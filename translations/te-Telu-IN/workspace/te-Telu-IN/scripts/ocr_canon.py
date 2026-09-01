"""OCR a bounded set of canon pages into ignored, readable working files."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess
import hashlib
import json

ROOT=Path(__file__).resolve().parents[2]
CANON=ROOT/"downloads/canon"
PAGES=[7,14,20,21,25,26,31,32,33,34,38,40,42,44]


def page(number):
    stem=CANON/"ocr"/f"TS-p{number:03d}"
    subprocess.run(["pdftoppm","-f",str(number),"-l",str(number),"-scale-to","2200","-png","-singlefile",str(CANON/"TS-2TM-MAT.pdf"),str(stem)],check=True,capture_output=True)
    subprocess.run([r"C:\Program Files\Tesseract-OCR\tesseract.exe",str(stem)+".png",str(stem),"--tessdata-dir",str(CANON/"tessdata"),"-l","tel+eng","--psm","3"],check=True,capture_output=True)
    path=stem.with_suffix(".txt")
    value=path.read_text(encoding="utf-8")
    assert any("\u0c00"<=c<="\u0c7f" for c in value)
    return {"pdf_page":number,"ocr_path":path.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"characters":len(value)}


if __name__=="__main__":
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(page,PAGES))
    (CANON/"ocr/receipt.json").write_text(json.dumps(results,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(results,indent=2))
