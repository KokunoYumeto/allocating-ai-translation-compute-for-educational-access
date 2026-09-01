"""OCR selected canon pages before reading; inputs/outputs remain ignored.
Usage: python ta-Taml-IN/scripts/ocr_canon.py --pages 1 2 3 4 5 6 7 8 20 21 22
No network, no training-corpus export. Tesseract model is an OCR dependency only.
"""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = Path(os.environ.get("LOCALAPPDATA", ""))
DEFAULT_POPPLER = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", nargs="+", type=int, required=True)
    parser.add_argument("--poppler", default=shutil.which("pdftoppm") or str(DEFAULT_POPPLER))
    parser.add_argument("--pdf", default="downloads/tamil-canon/tn-scert-6-term1-maths-2018.pdf")
    args = parser.parse_args()
    out = ROOT / "downloads/tamil-canon/ocr"
    out.mkdir(parents=True, exist_ok=True)
    def page(n):
        stem = out / f"page-{n:03d}"
        subprocess.run([args.poppler, "-f", str(n), "-l", str(n), "-r", "180", "-singlefile", "-png", str(ROOT / args.pdf), str(stem)], check=True)
        subprocess.run(["tesseract", str(stem) + ".png", str(stem), "--tessdata-dir", str(ROOT / "downloads/tessdata"), "-l", "tam", "--psm", "3"], check=True, capture_output=True)
        print(f"OCR page {n}: {stem.name}.txt", flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(page, args.pages))

if __name__ == "__main__":
    main()
