"""Deterministic real-Chromium layout checks and representative screenshots.

The reader is served only on loopback. This script launches one captured headless
Chrome process, inspects computed layout through the DevTools protocol, records
desktop and narrow evidence, and shuts down its own process tree.
"""
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


B = Path(__file__).resolve().parent
V = B / "visual"
CHROME_CANDIDATES = (
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(B), **kwargs)

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
        message_id = self.next_id
        self.next_id += 1
        await self.ws.send_json({"id": message_id, "method": method, "params": params or {}})
        while True:
            message = await self.ws.receive(timeout=15)
            if message.type != aiohttp.WSMsgType.TEXT:
                raise RuntimeError(f"Unexpected CDP websocket message: {message.type}")
            data = json.loads(message.data)
            if data.get("id") != message_id:
                continue
            if "error" in data:
                raise RuntimeError(f"CDP {method} failed: {data['error']}")
            return data.get("result", {})


METRICS_JS = r"""
(() => {
  const q = (selector) => Array.from(document.querySelectorAll(selector));
  const root = document.documentElement;
  const bodyStyle = getComputedStyle(document.body);
  const mainStyle = getComputedStyle(document.querySelector('main'));
  const math = q('math');
  const wrappers = q('.math-isolate');
  const figures = q('.source-media');
  const images = q('.source-media img').map((img) => {
    const style = getComputedStyle(img);
    const scroller = img.closest('.figure-scroll');
    const rect = img.getBoundingClientRect();
    return {
      src: new URL(img.getAttribute('src'), document.baseURI).pathname.split('/').pop(),
      complete: img.complete,
      naturalWidth: img.naturalWidth,
      naturalHeight: img.naturalHeight,
      renderedWidth: Math.round(img.getBoundingClientRect().width * 100) / 100,
      renderedHeight: Math.round(img.getBoundingClientRect().height * 100) / 100,
      transform: style.transform,
      display: style.display,
      direction: style.direction,
      left: Math.round(rect.left * 100) / 100,
      right: Math.round(rect.right * 100) / 100,
      fullyWithinViewport: rect.left >= -0.5 && rect.right <= window.innerWidth + 0.5,
      scrollerClientWidth: scroller ? scroller.clientWidth : null,
      scrollerScrollWidth: scroller ? scroller.scrollWidth : null,
      locallyScrollable: scroller ? scroller.scrollWidth > scroller.clientWidth + 1 : false
    };
  });
  const reflows = q('.figure-reflow').map((node) => {
    const style = getComputedStyle(node);
    return {
      display: style.display,
      clientWidth: node.clientWidth,
      scrollWidth: node.scrollWidth,
      horizontalOverflow: node.scrollWidth > node.clientWidth + 1,
      expressionCount: node.querySelectorAll('.responsive-expression').length,
      textLength: node.textContent.trim().length
    };
  });
  const mainRect = document.querySelector('main').getBoundingClientRect();
  const localLinks = q('a[href]').filter((a) => {
    const u = new URL(a.href, document.baseURI);
    return u.origin === location.origin;
  });
  return {
    viewport: {
      innerWidth: window.innerWidth,
      innerHeight: window.innerHeight,
      devicePixelRatio: window.devicePixelRatio
    },
    document: {
      lang: root.lang,
      dir: root.dir,
      computedBodyDirection: bodyStyle.direction,
      computedMainDirection: mainStyle.direction,
      clientWidth: root.clientWidth,
      scrollWidth: root.scrollWidth,
      scrollHeight: root.scrollHeight,
      horizontalOverflow: root.scrollWidth > root.clientWidth + 1
    },
    counts: {
      sourceBindings: q('[data-source-path]').length,
      sourceKeys: q('[data-source-key]').length,
      math: math.length,
      mathWrappers: wrappers.length,
      sourceExercises: q('[data-source-tag="exercise"]').length,
      sourceSolutions: q('[data-source-tag="solution"]').length,
      figures: figures.length,
      responsiveFigureReflows: reflows.length,
      urduBridges: q('[lang="ur-Arab-PK"]').length,
      englishRuns: q('[lang="en"]').length,
      scripts: q('script').length,
      iframes: q('iframe').length,
      externalStylesheets: q('link[rel="stylesheet"]').length
    },
    directionality: {
      allMathLTR: math.every((node) => getComputedStyle(node).direction === 'ltr'),
      allMathWrappersLTR: wrappers.every((node) => getComputedStyle(node).direction === 'ltr'),
      hiddenBidiControlsAbsent: !/[\u202a-\u202e\u2066-\u2069]/.test(document.documentElement.textContent),
      bodyFontSize: bodyStyle.fontSize
    },
    images,
    reflows,
    fullWidthLayout: {
      mainWidth: Math.round(mainRect.width * 100) / 100,
      mainLeft: Math.round(mainRect.left * 100) / 100,
      mainRight: Math.round(mainRect.right * 100) / 100
    },
    navigation: {
      localLinks: localLinks.length,
      missingSameDocumentFragments: localLinks.filter((a) => {
        const u = new URL(a.href, document.baseURI);
        return u.pathname === location.pathname && u.hash && !document.getElementById(decodeURIComponent(u.hash.slice(1)));
      }).map((a) => a.getAttribute('href'))
    },
    keyContent: {
      titleVisible: document.querySelector('h1').getBoundingClientRect().height > 0,
      learningKeyPresent: Boolean(document.getElementById('learning-key')),
      wordKeyPresent: Boolean(document.getElementById('word-key')),
      creditsPresent: Boolean(document.getElementById('credits')),
      lastSourceItemPresent: Boolean(document.querySelector('[data-source-key="fs-id1166425014151/item/3"]'))
    }
  };
})()
"""


def assert_metrics(label: str, width: int, data: dict) -> None:
    assert data["viewport"]["innerWidth"] == width, (label, data["viewport"])
    assert data["document"]["lang"] == "pnb-Arab-PK"
    assert data["document"]["dir"] == "rtl"
    assert data["document"]["computedBodyDirection"] == "rtl"
    assert data["document"]["computedMainDirection"] == "rtl"
    assert not data["document"]["horizontalOverflow"], (label, data["document"])
    assert data["counts"]["sourceBindings"] == 253
    assert data["counts"]["sourceKeys"] == 66
    assert data["counts"]["math"] == data["counts"]["mathWrappers"] == 62
    assert data["counts"]["sourceExercises"] == 12
    assert data["counts"]["sourceSolutions"] == 12
    assert data["counts"]["figures"] == len(data["images"]) == 3
    assert data["counts"]["responsiveFigureReflows"] == len(data["reflows"]) == 3
    assert data["counts"]["urduBridges"] == 3
    assert data["counts"]["scripts"] == 0
    assert data["counts"]["iframes"] == 0
    assert data["counts"]["externalStylesheets"] == 0
    assert data["directionality"]["allMathLTR"]
    assert data["directionality"]["allMathWrappersLTR"]
    assert data["directionality"]["hiddenBidiControlsAbsent"]
    assert data["navigation"]["missingSameDocumentFragments"] == []
    assert all(data["keyContent"].values())
    expected = [(594, 84), (594, 70), (594, 51)]
    assert [(i["naturalWidth"], i["naturalHeight"]) for i in data["images"]] == expected
    assert all(i["complete"] and i["transform"] == "none" for i in data["images"])
    assert all(not i["locallyScrollable"] for i in data["images"])
    assert all(i["fullyWithinViewport"] for i in data["images"])
    assert data["fullWidthLayout"]["mainLeft"] == 0
    assert data["fullWidthLayout"]["mainRight"] == width
    assert data["fullWidthLayout"]["mainWidth"] == width
    if width == 390:
        assert data["directionality"]["bodyFontSize"] == "19px"
        assert all(i["renderedWidth"] <= i["scrollerClientWidth"] + 0.5 for i in data["images"])
        assert all(i["scrollerScrollWidth"] == i["scrollerClientWidth"] for i in data["images"])
        assert all(r["display"] == "block" and not r["horizontalOverflow"] and r["expressionCount"] == 1 and r["textLength"] > 20 for r in data["reflows"])
    else:
        assert data["directionality"]["bodyFontSize"] == "21px"
        assert all(abs(i["renderedWidth"] - 594) < 0.5 for i in data["images"])
        assert all(r["display"] == "none" for r in data["reflows"])


async def wait_ready(cdp: CDP) -> None:
    for _ in range(80):
        result = await cdp.send(
            "Runtime.evaluate",
            {
                "expression": "document.readyState === 'complete' && document.fonts.status === 'loaded' && [...document.images].every(i => i.complete)",
                "returnByValue": True,
            },
        )
        if result["result"].get("value") is True:
            return
        await asyncio.sleep(0.1)
    raise TimeoutError("reader did not reach complete font/image state")


async def inspect_viewport(cdp: CDP, url: str, name: str, width: int, height: int, mobile: bool) -> dict:
    await cdp.send(
        "Emulation.setDeviceMetricsOverride",
        {
            "width": width,
            "height": height,
            "deviceScaleFactor": 1,
            "mobile": mobile,
            "screenWidth": width,
            "screenHeight": height,
        },
    )
    await cdp.send("Page.navigate", {"url": url})
    await wait_ready(cdp)
    measured = await cdp.send(
        "Runtime.evaluate",
        {"expression": METRICS_JS, "returnByValue": True, "awaitPromise": True},
    )
    metrics = measured["result"]["value"]
    assert_metrics(name, width, metrics)

    top = await cdp.send("Page.captureScreenshot", {"format": "png", "fromSurface": True, "captureBeyondViewport": False})
    top_bytes = base64.b64decode(top["data"])
    top_path = V / f"{name}.png"
    top_path.write_bytes(top_bytes)

    layout = await cdp.send("Page.getLayoutMetrics")
    content = layout.get("cssContentSize") or layout["contentSize"]
    full = await cdp.send(
        "Page.captureScreenshot",
        {
            "format": "png",
            "fromSurface": True,
            "captureBeyondViewport": True,
            "clip": {"x": 0, "y": 0, "width": content["width"], "height": content["height"], "scale": 1},
        },
    )
    full_bytes = base64.b64decode(full["data"])
    full_path = V / f"{name}-full.png"
    full_path.write_bytes(full_bytes)

    cluster_result = await cdp.send(
        "Runtime.evaluate",
        {
            "expression": "(() => { const r=document.getElementById('fs-id1170654941968').getBoundingClientRect(); return {x:0,y:r.top+window.scrollY,width:document.documentElement.clientWidth,height:r.height}; })()",
            "returnByValue": True,
        },
    )
    cluster_rect = cluster_result["result"]["value"]
    cluster = await cdp.send(
        "Page.captureScreenshot",
        {
            "format": "png",
            "fromSurface": True,
            "captureBeyondViewport": True,
            "clip": {**cluster_rect, "scale": 1},
        },
    )
    cluster_bytes = base64.b64decode(cluster["data"])
    cluster_path = V / f"{name}-figure-cluster.png"
    cluster_path.write_bytes(cluster_bytes)

    await cdp.send(
        "Runtime.evaluate",
        {
            "expression": "document.getElementById('fs-id1170655224688').scrollIntoView({block:'start'}); true",
            "returnByValue": True,
        },
    )
    lower = await cdp.send("Page.captureScreenshot", {"format": "png", "fromSurface": True, "captureBeyondViewport": False})
    lower_bytes = base64.b64decode(lower["data"])
    lower_path = V / f"{name}-figures.png"
    lower_path.write_bytes(lower_bytes)

    await cdp.send(
        "Runtime.evaluate",
        {
            "expression": "window.scrollTo(0, document.documentElement.scrollHeight); true",
            "returnByValue": True,
        },
    )
    bottom = await cdp.send("Page.captureScreenshot", {"format": "png", "fromSurface": True, "captureBeyondViewport": False})
    bottom_bytes = base64.b64decode(bottom["data"])
    bottom_path = V / f"{name}-bottom.png"
    bottom_path.write_bytes(bottom_bytes)

    metrics["screenshots"] = [
        {"path": f"visual/{top_path.name}", "bytes": len(top_bytes), "sha256": sha(top_bytes), "position": "page top"},
        {"path": f"visual/{full_path.name}", "bytes": len(full_bytes), "sha256": sha(full_bytes), "position": "complete full page"},
        {"path": f"visual/{cluster_path.name}", "bytes": len(cluster_bytes), "sha256": sha(cluster_bytes), "position": "complete three-figure worked-solution cluster"},
        {"path": f"visual/{lower_path.name}", "bytes": len(lower_bytes), "sha256": sha(lower_bytes), "position": "worked-example/figure region"},
        {"path": f"visual/{bottom_path.name}", "bytes": len(bottom_bytes), "sha256": sha(bottom_bytes), "position": "page bottom and credits"},
    ]
    return metrics


async def run_cdp(ws_url: str, url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(ws_url, max_msg_size=32 * 1024 * 1024) as ws:
            cdp = CDP(ws)
            await cdp.send("Page.enable")
            await cdp.send("Runtime.enable")
            version = await cdp.send("Browser.getVersion")
            desktop = await inspect_viewport(cdp, url, "desktop", 1440, 1000, False)
            narrow = await inspect_viewport(cdp, url, "narrow", 390, 844, True)
            return {
                "schema": "a10-browser-visual-results-v1",
                "status": "passed",
                "date": "2026-09-04",
                "inputs": [
                    {"path": path, "bytes": (B / path).stat().st_size, "sha256": sha((B / path).read_bytes())}
                    for path in (
                        "index.html",
                        "reader.css",
                        "build.py",
                        "renderer_base.py",
                        "visual_check.py",
                        "translation.json",
                        "guidance.html",
                        "EXPERT_REVIEW_LOG.json",
                    )
                ],
                "browser": {
                    "product": version["product"],
                    "revision": version["revision"],
                    "protocol_version": version["protocolVersion"],
                    "user_agent": version["userAgent"],
                    "javascript_version": version["jsVersion"],
                },
                "transport": "single captured headless Chrome process via loopback HTTP and DevTools protocol",
                "viewports": {"desktop": desktop, "narrow": narrow},
                "checks": [
                    "actual browser loaded all local images and fonts",
                    "desktop 1440x1000 and narrow 390x844 computed layouts",
                    "no document-level horizontal overflow",
                    "all three source figures fit wholly inside desktop and 390px viewports without local or document-level horizontal scrolling",
                    "three semantic figure reconstructions are visible at 390px and remain overflow-free",
                    "RTL Punjabi document and LTR MathML wrappers",
                    "253 source bindings, 66 source keys, 62 MathML trees",
                    "12 exercises retain 12 supplied solutions",
                    "three Urdu bridges remain explicitly tagged",
                    "no scripts, iframes, or external stylesheets in the reader",
                    "same-document navigation fragments resolve",
                    "three unmirrored canonical JPEGs decoded at exact dimensions and retain natural desktop width",
                    "saved page-top, complete full-page, complete three-figure cluster, figure-region and bottom/credits screenshots for both viewports",
                ],
            }


def fetch_json(url: str) -> object:
    with urlopen(url, timeout=5) as response:
        return json.loads(response.read())


def main() -> None:
    V.mkdir(exist_ok=True)
    chrome = next((path for path in CHROME_CANDIDATES if path.is_file()), None)
    if chrome is None:
        raise FileNotFoundError("Pinned QA requires installed Google Chrome")

    server = QuietServer(("127.0.0.1", 0), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}/index.html"

    proc: subprocess.Popen | None = None
    try:
        with tempfile.TemporaryDirectory(prefix="a10-009-chrome-") as profile:
            flags = [
                str(chrome),
                "--headless=new",
                "--disable-background-networking",
                "--disable-breakpad",
                "--disable-component-update",
                "--disable-default-apps",
                "--disable-extensions",
                "--disable-features=OptimizationHints,MediaRouter",
                "--disable-gpu",
                "--disable-sync",
                "--force-device-scale-factor=1",
                "--hide-scrollbars",
                "--metrics-recording-only",
                "--no-first-run",
                "--no-pings",
                "--no-proxy-server",
                "--remote-allow-origins=*",
                "--remote-debugging-port=0",
                f"--user-data-dir={profile}",
                "about:blank",
            ]
            startupinfo = None
            creationflags = 0
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                creationflags = subprocess.CREATE_NO_WINDOW
            proc = subprocess.Popen(
                flags,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                startupinfo=startupinfo,
                creationflags=creationflags,
            )
            try:
                port_file = Path(profile) / "DevToolsActivePort"
                deadline = time.monotonic() + 15
                port = None
                while port is None:
                    if proc.poll() is not None:
                        raise RuntimeError(f"Chrome exited before DevTools startup: {proc.returncode}")
                    if time.monotonic() > deadline:
                        raise TimeoutError("Chrome DevTools port did not become ready")
                    if port_file.is_file():
                        try:
                            lines = port_file.read_text(encoding="utf-8").splitlines()
                            if lines:
                                port = int(lines[0])
                                break
                        except (OSError, ValueError):
                            pass
                    time.sleep(0.05)
                targets = fetch_json(f"http://127.0.0.1:{port}/json/list")
                pages = [target for target in targets if target.get("type") == "page"]
                if len(pages) != 1:
                    raise RuntimeError(f"Expected one captured page, found {len(pages)}")
                results = asyncio.run(run_cdp(pages[0]["webSocketDebuggerUrl"], url))
                payload = json.dumps(results, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
                (V / "RESULTS.json").write_text(payload, encoding="utf-8", newline="\n")
            finally:
                if proc.poll() is None:
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait(timeout=5)
    finally:
        server.shutdown()
        server.server_close()
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)

    result_bytes = (V / "RESULTS.json").read_bytes()
    print(json.dumps({"status": "passed", "results_sha256": sha(result_bytes)}, sort_keys=True))


if __name__ == "__main__":
    main()
