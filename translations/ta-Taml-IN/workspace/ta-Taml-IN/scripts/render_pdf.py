"""Local Chromium document-print renderer; does not automate a user browser.
In-app Browser is used separately for visible HTML QA. No remote resource is loaded.
"""
import argparse
import os
from pathlib import Path
import subprocess
import shutil

ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT / "ta-Taml-IN"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chromium", default=os.environ.get("CHROMIUM_BIN", "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"))
    parser.add_argument("--profiles", nargs="+", choices=["print", "screen"], default=["print", "screen"])
    parser.add_argument("--unit", choices=["U001", "U002"], default="U001")
    args = parser.parse_args()
    reader = LANG / ("reader" if args.unit == "U001" else "reader-u002")
    out = LANG / "output/pdf"
    out.mkdir(parents=True, exist_ok=True)
    tmp = ROOT / "tmp/pdfs"
    tmp.mkdir(parents=True, exist_ok=True)
    for profile, source in [("print", "index.html"), ("screen", "screen.html")]:
        if profile not in args.profiles:
            continue
        if shutil.disk_usage(tmp).free < 128 * 1024 * 1024:
            raise RuntimeError("Insufficient free space for PDF export; no export attempted")
        # Reuse this task-owned document-print cache instead of accumulating
        # a fresh browser profile for every small editorial revision.
        cache = tmp / f"ta-document-print-{profile}"
        cache.mkdir(exist_ok=True)
        target = out / f"ta-Taml-IN-A00-{args.unit}-{profile}.pdf"
        assert (reader / source).is_file(), f"Missing {args.unit} reader: {source}"
        command = [args.chromium, "--headless", "--disable-gpu", "--disable-background-networking", "--disable-sync", "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--no-pdf-header-footer", "--export-tagged-pdf", "--virtual-time-budget=3000", f"--user-data-dir={cache}", f"--print-to-pdf={target}", (reader / source).as_uri()]
        subprocess.run(command, check=True, timeout=120, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert target.is_file() and target.stat().st_size > 10000
        print(f"{target.name}: {target.stat().st_size} bytes", flush=True)

if __name__ == "__main__":
    main()
