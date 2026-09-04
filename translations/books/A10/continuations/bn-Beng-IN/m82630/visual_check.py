"""Run bounded real-Chrome layout QA and save reproducible visual evidence."""
from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import urlopen

import aiohttp


ROOT = Path(__file__).resolve().parent
VISUAL = ROOT / "visual"
CHROME_CANDIDATES = (
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, _format: str, *args: object) -> None:
        return


class QuietServer(ThreadingHTTPServer):
    def handle_error(self, request: object, client_address: object) -> None:
        return


class CDP:
    def __init__(self, ws: aiohttp.ClientWebSocketResponse):
        self.ws = ws
        self.next_id = 1

    async def send(self, method: str, params: dict | None = None) -> dict:
        request_id = self.next_id
        self.next_id += 1
        await self.ws.send_json({"id": request_id, "method": method, "params": params or {}})
        while True:
            message = await self.ws.receive(timeout=15)
            if message.type != aiohttp.WSMsgType.TEXT:
                raise RuntimeError(f"Unexpected CDP message: {message.type}")
            data = json.loads(message.data)
            if data.get("id") != request_id:
                continue
            if "error" in data:
                raise RuntimeError(f"CDP {method} failed: {data['error']}")
            return data.get("result", {})


METRICS_JS = r"""
(() => {
  const q = (selector) => Array.from(document.querySelectorAll(selector));
  const root = document.documentElement;
  const main = document.querySelector('main');
  const header = document.querySelector('header');
  const rect = (node) => {
    const r = node.getBoundingClientRect();
    return {left:r.left, right:r.right, width:r.width, height:r.height};
  };
  const images = q('img').map((img) => {
    const r = img.getBoundingClientRect();
    const parent = img.parentElement.getBoundingClientRect();
    return {
      src: new URL(img.getAttribute('src'), document.baseURI).pathname.split('/').pop(),
      complete: img.complete,
      naturalWidth: img.naturalWidth,
      naturalHeight: img.naturalHeight,
      renderedWidth: r.width,
      renderedHeight: r.height,
      parentWidth: parent.width,
      overflowsParent: r.width > parent.width + 1
    };
  });
  return {
    viewport:{width:window.innerWidth,height:window.innerHeight,devicePixelRatio:window.devicePixelRatio},
    document:{lang:root.lang,clientWidth:root.clientWidth,scrollWidth:root.scrollWidth,scrollHeight:root.scrollHeight,horizontalOverflow:root.scrollWidth > root.clientWidth + 1},
    bodyFontSize:getComputedStyle(document.body).fontSize,
    main:rect(main),
    header:rect(header),
    images,
    counts:{images:images.length,figures:q('figure').length,scripts:q('script').length,iframes:q('iframe').length,stylesheets:q('link[rel="stylesheet"]').length,ids:q('[id]').length},
    keyContent:{title:Boolean(document.querySelector('h1')),graph:Boolean(document.getElementById('fs-id1171782146065')),editorial:Boolean(document.getElementById('editorial-notes')),footer:Boolean(document.querySelector('footer'))}
  };
})()
"""


async def ready(cdp: CDP) -> None:
    for _ in range(100):
        result = await cdp.send(
            "Runtime.evaluate",
            {
                "expression": "(() => { [...document.images].forEach(i => i.loading = 'eager'); return document.readyState === 'complete' && document.fonts.status === 'loaded' && [...document.images].every(i => i.complete); })()",
                "returnByValue": True,
            },
        )
        if result["result"].get("value") is True:
            return
        await asyncio.sleep(0.1)
    raise TimeoutError("Reader did not reach its complete image/font state")


def validate(label: str, width: int, metrics: dict) -> None:
    assert metrics["viewport"]["width"] == width
    assert metrics["document"]["lang"] == "bn-IN"
    assert not metrics["document"]["horizontalOverflow"]
    assert metrics["counts"] == {"images": 4, "figures": 1, "scripts": 0, "iframes": 0, "stylesheets": 1, "ids": 68}
    assert all(metrics["keyContent"].values())
    assert all(image["complete"] and not image["overflowsParent"] for image in metrics["images"])
    graph = next(image for image in metrics["images"] if image["src"] == "CNX_ElemAlg_Figure_05_01_015_img.jpg")
    assert (graph["naturalWidth"], graph["naturalHeight"]) == (791, 257)
    assert graph["renderedWidth"] <= metrics["main"]["width"]
    for surface in (metrics["main"], metrics["header"]):
        assert abs(surface["left"] - (width - surface["right"])) <= 1.1
    if label == "desktop":
        assert metrics["bodyFontSize"] == "20px"
        assert metrics["main"]["width"] / width >= 0.96
    else:
        assert metrics["bodyFontSize"] == "18px"
        assert metrics["main"]["width"] / width >= 0.95
        assert graph["renderedWidth"] <= width - 25


async def inspect(cdp: CDP, url: str, label: str, width: int, height: int, mobile: bool) -> tuple[dict, list[dict]]:
    await cdp.send(
        "Emulation.setDeviceMetricsOverride",
        {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": mobile, "screenWidth": width, "screenHeight": height},
    )
    await cdp.send("Page.navigate", {"url": url})
    await ready(cdp)
    result = await cdp.send("Runtime.evaluate", {"expression": METRICS_JS, "returnByValue": True})
    metrics = result["result"]["value"]
    validate(label, width, metrics)
    shots = []
    for suffix, position, action in (
        ("top", "page top", "window.scrollTo(0,0); true"),
        ("graph", "graph and its Bengali description", "document.getElementById('fs-id1171782146065').scrollIntoView({block:'center'}); true"),
    ):
        await cdp.send("Runtime.evaluate", {"expression": action, "returnByValue": True})
        capture = await cdp.send("Page.captureScreenshot", {"format": "png", "fromSurface": True, "captureBeyondViewport": False})
        data = base64.b64decode(capture["data"])
        path = VISUAL / f"{label}-{suffix}.png"
        path.write_bytes(data)
        shots.append({"path": path.relative_to(ROOT).as_posix(), "bytes": len(data), "sha256": sha(data), "position": position})
    return metrics, shots


async def browser_run(ws_url: str, url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(ws_url, max_msg_size=32 * 1024 * 1024) as ws:
            cdp = CDP(ws)
            await cdp.send("Page.enable")
            await cdp.send("Runtime.enable")
            version = await cdp.send("Browser.getVersion")
            desktop, desktop_shots = await inspect(cdp, url, "desktop", 1440, 1000, False)
            narrow, narrow_shots = await inspect(cdp, url, "narrow", 390, 844, True)
            return {
                "schema": "a10.bn-Beng-IN.browser-visual.v1",
                "status": "pass",
                "date": "2026-09-04",
                "browser": {"product": version["product"], "revision": version["revision"], "protocol_version": version["protocolVersion"], "user_agent": version["userAgent"], "javascript_version": version["jsVersion"]},
                "transport": "one captured headless Chrome process over loopback HTTP and DevTools",
                "viewports": {"desktop": desktop, "narrow": narrow},
                "screenshots": desktop_shots + narrow_shots,
                "checks": [
                    "main and header are centered and fill at least 96% of the desktop viewport",
                    "390px reader fills at least 95% of the viewport",
                    "no document-level horizontal overflow",
                    "all four exact images load and stay within their containers",
                    "the 791px graph reflows below the narrow viewport width with no hidden content",
                    "title, graph, editorial notes, and footer remain present",
                ],
            }


def fetch_json(url: str) -> object:
    with urlopen(url, timeout=5) as response:
        return json.loads(response.read())


def main() -> None:
    VISUAL.mkdir(exist_ok=True)
    chrome = next((path for path in CHROME_CANDIDATES if path.is_file()), None)
    if chrome is None:
        raise FileNotFoundError("Installed Google Chrome is required for visual QA")
    server = QuietServer(("127.0.0.1", 0), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}/index.html"
    proc: subprocess.Popen | None = None
    try:
        with tempfile.TemporaryDirectory(prefix="a10-bn-in-chrome-", ignore_cleanup_errors=True) as profile:
            flags = [
                str(chrome), "--headless=new", "--disable-background-networking", "--disable-breakpad",
                "--disable-component-update", "--disable-default-apps", "--disable-extensions",
                "--disable-features=OptimizationHints,MediaRouter", "--disable-gpu", "--disable-sync",
                "--force-device-scale-factor=1", "--hide-scrollbars", "--metrics-recording-only",
                "--no-first-run", "--no-pings", "--no-proxy-server", "--remote-allow-origins=*",
                "--remote-debugging-port=0", f"--user-data-dir={profile}", "about:blank",
            ]
            startupinfo = None
            creationflags = 0
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                creationflags = subprocess.CREATE_NO_WINDOW
            proc = subprocess.Popen(flags, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, startupinfo=startupinfo, creationflags=creationflags)
            port_file = Path(profile) / "DevToolsActivePort"
            deadline = time.monotonic() + 15
            while not port_file.is_file():
                if proc.poll() is not None:
                    raise RuntimeError(f"Chrome exited before DevTools startup: {proc.returncode}")
                if time.monotonic() > deadline:
                    raise TimeoutError("Chrome DevTools port did not become ready")
                time.sleep(0.05)
            port = int(port_file.read_text(encoding="utf-8").splitlines()[0])
            pages = [target for target in fetch_json(f"http://127.0.0.1:{port}/json/list") if target.get("type") == "page"]
            if len(pages) != 1:
                raise RuntimeError(f"Expected one captured page, found {len(pages)}")
            result = asyncio.run(browser_run(pages[0]["webSocketDebuggerUrl"], url))
            payload = (json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
            (VISUAL / "RESULTS.json").write_bytes(payload)
    finally:
        if proc is not None and proc.poll() is None:
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    check=False,
                )
            else:
                proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
        server.shutdown()
        server.server_close()
    data = (VISUAL / "RESULTS.json").read_bytes()
    print(json.dumps({"status": "pass", "bytes": len(data), "sha256": sha(data)}, sort_keys=True))


if __name__ == "__main__":
    main()
