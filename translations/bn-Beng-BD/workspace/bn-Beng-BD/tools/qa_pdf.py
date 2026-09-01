"""Check PDFs for missing content/overflow and record limits; visual inspection is separate."""
from pathlib import Path
import hashlib,json
import fitz
L=Path(__file__).resolve().parents[1]
def main():
    receipts=[]
    for kind in ('print','screen'):
        p=L/'output/pdf'/('u01-'+kind+'.pdf')
        doc=fitz.open(p)
        text='\n'.join(page.get_text() for page in doc)
        assert '\ufffd' not in text
        for marker in ['D1.','D2.','D3.','D4.','P1.','P2.','P3.','P4.','P5.','P6.','P7.','P8.','E1.','E2.','fs-id1398237','fs-id3298473','fs-id1786026','fs-id2908692','fs-id1227376','fs-id1983295','OpenStax','Rice University']:
            assert marker in text,(kind,marker)
        overflow=[]
        for i,page in enumerate(doc):
            assert len(page.get_text())>80
            for block in page.get_text('dict')['blocks']:
                for line in block.get('lines',[]):
                    box=fitz.Rect(line['bbox'])
                    if box.x0 < 43 or box.y0<25 or box.x1>page.rect.width-43 or box.y1>page.rect.height-18: overflow.append({'page':i+1,'box':list(box),'text':''.join(x['text'] for x in line['spans'])})
        assert not overflow,overflow
        receipts.append({'file':str(p.relative_to(L)).replace('\\','/'),'pages':len(doc),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'checked_all_pages_for_text_overflow':True,'assessment_and_source_ids_found':True,'replacement_characters':0,'text_extraction_chars':len(text),'tagged':False,'screen_reader_primary':'output/u01-number-sense.html','visual_status':'requires human/model PNG inspection; not established by this script'})
    (L/'output/pdf/qa-receipt.json').write_text(json.dumps(receipts,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipts,indent=2))
if __name__=='__main__':main()
