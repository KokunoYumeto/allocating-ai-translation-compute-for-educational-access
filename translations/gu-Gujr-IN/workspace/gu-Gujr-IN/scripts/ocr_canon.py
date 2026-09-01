"""OCR selected Gujarati reference pages before reading their language.

Original PDFs and OCR remain ignored; this is a linguistic reference workspace.
"""
import argparse
import concurrent.futures
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
CANON = ROOT / "downloads/gu-Gujr-IN/gujarati-canon"
PAGES = {"std5-week1": [13], "std6-week1": [12, 14, 15, 16]}


def run_page(item):
    name, page, poppler = item
    prefix = CANON / f"{name}-p{page:02d}"
    subprocess.run([poppler, "-f", str(page), "-l", str(page), "-r", "160", "-singlefile", "-png",
                    str(CANON / (name + ".pdf")), str(prefix)], check=True, capture_output=True)
    subprocess.run(["tesseract", str(prefix.with_suffix(".png")), str(prefix), "--tessdata-dir", str(CANON),
                    "-l", "guj", "--psm", "3"], check=True, capture_output=True)
    print(f"OCR ready: {prefix.name}.txt", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdftoppm", required=True)
    args = parser.parse_args()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(run_page, [(n, p, args.pdftoppm) for n, pages in PAGES.items() for p in pages]))
