"""Pin readable local canon witnesses without redistributing textbook pages."""
from pathlib import Path
import hashlib
import json
import subprocess

LANG = Path(__file__).resolve().parents[1]
ROOT = LANG.parent
BASE = ROOT/'downloads/mr-Deva-IN/canon'
paths = ['balbharati-8-mr.pdf','tessdata/mar.traineddata','tessdata/eng.traineddata']
for page in (12,13,34,39,85,86):
    paths.extend([f'pages/balbharati8-{page}.png',f'ocr/balbharati8-{page}.txt'])
files = []
for relative in paths:
    path = BASE/relative
    raw = path.read_bytes()
    assert raw, relative
    files.append({'path':path.relative_to(ROOT).as_posix(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
receipt = {
    'schema':1,'date':'2026-08-30','locale':'mr-Deva-IN','reference_examples':16,
    'downloaded_pdf_url':'https://books.ebalbharati.in/pdfs/801020004.pdf',
    'marathi_ocr_model_url':'https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/mar.traineddata',
    'ocr_engine':subprocess.check_output(['tesseract','--version'],text=True).splitlines()[0],
    'method':'Poppler 160 dpi, Tesseract mar+eng psm 3; OCR read; six relevant pages visually inspected',
    'physical_pdf_pages_used':[12,13,34,39,85,86],
    'ocr_limits':'Prose readable; formula tokens unreliable. Rendered pages govern formulas. Legacy-font renderer warnings inspected, not ignored.',
    'web_only_reference':{'url':'https://marathivishwakosh.org/21979/','title':'फलन (Function)','author':'गणेश कडू','published':'2019-08-31','read':'web reader prose','local_download':'failed connection; not counted as acquired HTML','excluded':'image-only formula tokens not read'},
    'files':files,
}
(LANG/'canon/witnesses.lock.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Pinned {len(files)} local canon artifacts and 16 reference locators.')
