"""Freeze existing readable canon files; never downloads or OCRs again."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import shutil
from build import atomic_write

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parent


def record(path):
    with path.open("rb") as stream:
        digest=hashlib.file_digest(stream,"sha256").hexdigest()
    return {"path":path.relative_to(ROOT).as_posix(),"bytes":path.stat().st_size,"sha256":digest}


def seal():
    assert shutil.disk_usage(BASE).free>=32*1024*1024,"Insufficient free space"
    from pypdf import PdfReader
    books=[]
    for ident,local,remote,expected in [("TS-MATH2-2018","TS-2TM-MAT.pdf","2TM_MAT.pdf",138),("TS6-2018","ap/TS-6TM-MAT.pdf","6TM_MAT.pdf",226)]:
        path=ROOT/"downloads/canon"/local
        pages=len(PdfReader(path).pages)
        assert pages==expected
        books.append({"id":ident,"region":"Telangana","url":"https://scert.telangana.gov.in/PDF/publication/ebooks/"+remote,"pdf_pages":pages,**record(path)})
    assert books[1]["sha256"]=="3faa1f0551382ea25853d62604c63aa27034c6c07f7d56ce016c83d36b6f90ee"
    ocr=[]
    for book,folder,prefix,pages in [("TS-MATH2-2018","ocr","TS-p",[7,14,20,21,25,26,31,32,33,34,38,40,42,44]),("TS6-2018","ap","TS6-sets-",[26,27,85]),("TS6-2018","ap","TS6-naming-",[13,14,15,16,17,18])]:
        for page in pages:
            for suffix in ["txt","png"]:
                path=ROOT/"downloads/canon"/folder/f"{prefix}{page:03d}.{suffix}"
                ocr.append({"book":book,"pdf_page":page,"kind":suffix,**record(path)})
    models=[{"language":lang,**record(ROOT/"downloads/canon/tessdata"/(lang+".traineddata"))} for lang in ["tel","eng"]]
    version=subprocess.check_output([r"C:\Program Files\Tesseract-OCR\tesseract.exe","--version"],text=True).splitlines()[0]
    data={"schema":"telugu-readable-canon-lock-v1","purpose":"Reference only; not training or fine-tuning data; complete PDFs and OCR stay ignored","books":books,"ocr_engine":version,"model_files":models,"page_files":ocr,"selection":"16 starter examples plus4 topic-specific place/naming anchors; selected-page OCR only, not whole-PDF OCR","AP_status":"Not acquired; see ap-witness.md","actual_use_log":"CONSULTATIONS.md; hashes do not prove reading"}
    atomic_write(BASE/"canon/lock.json",(json.dumps(data,ensure_ascii=False,indent=2)+"\n").encode("utf-8"))
    print(json.dumps({"books":books,"page_records":len(ocr),"ocr_engine":version}))


def verify():
    data=json.loads((BASE/"canon/lock.json").read_text(encoding="utf-8"))
    records=data["books"]+data["model_files"]+data["page_files"]
    for item in records:
        assert record(ROOT/item["path"])=={key:item[key] for key in ["path","bytes","sha256"]},item["path"]
    print(f"PASS: {len(records)} canon PDF/model/OCR/page records")


if __name__=="__main__":
    verify() if "--verify" in sys.argv else seal()
