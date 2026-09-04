"""Hash the actually downloaded/OCR-read target-language references."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
LANG=ROOT/'languages/bn-Beng-IN'
folder=ROOT/'downloads/bn-Beng-IN-canon'
sources=[('WB-Class7-Learning-Bridge','https://banglarshiksha.wb.gov.in/Frontend/download_ott_pdf?upload_code_pk=c113bdb407089ca002da5ba8b0e3ccff65b7933d12e3dbd626a9cb3385de23c742e8eb03634f425fb759cf85119d882e088d590be00aa02eddaa1fe8745a04c3KKUngupyuletaIii9ScK8uA0xTaKJd5810VMGu84Ppg%3D','West Bengal, primary locale witness'),('SCERT-Tripura-VI','https://www.scerttripura.org/pdf/class6/VIMathBengaliversion.pdf','Tripura, supplementary Indian Bengali witness')]
def record(p): return {'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
result=[]
for name,url,scope in sources:
    r=record(folder/(name+'.pdf'));r.update({'id':name,'url':url,'scope':scope,'native_text_readability':'legacy font encoding; use OCR plus visual checks','ocr_engine':'Tesseract 5 / ben tessdata_fast','read_pages':[]})
    receipt=json.loads((folder/name/'ocr-receipt.json').read_text())
    for item in receipt:
        r['read_pages'].append({'pdf_page':item['pdf_page'],'ocr':record(ROOT/item['ocr_text']),'render':record(ROOT/item['png'])})
    result.append(r)
out={'locale':'bn-Beng-IN','purpose':'reference only; not redistributed as learner content','sources':result,
     'ocr_model':record(ROOT/'downloads/tessdata/ben.traineddata'),'ocr_model_url':'https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/ben.traineddata'}
(LANG/'canon/references.lock.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Reference PDFs and OCR hashes locked; see canon/examples.tsv for the current exemplar count.')
