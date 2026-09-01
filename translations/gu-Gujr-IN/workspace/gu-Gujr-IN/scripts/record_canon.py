"""Pin acquired Gujarati linguistic references and local OCR witnesses."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]
LANG=ROOT/'gu-Gujr-IN';DL=ROOT/'downloads/gu-Gujr-IN/gujarati-canon'
URLS={
    'std3-week2.pdf':'https://ssagujarat.org/StudyFromHome/STD%203-Week2.pdf',
    'std5-week1.pdf':'https://ssagujarat.org/StudyFromHome/Std%205-Week1.pdf',
    'std6-week1.pdf':'https://ssagujarat.org/StudyFromHome/Std%206-Week1.pdf',
    'std6-week2.pdf':'https://www.ssagujarat.org/StudyFromHome/STD%206-Week2.pdf',
    'guj.traineddata':'https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/guj.traineddata',
}
PAGES={'std5-week1':[13],'std6-week1':[12,14,15,16]}


def record(p,url=None):
    row={'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    if url:row['url']=url
    return row


def main():
    acquired=[record(DL/name,url) for name,url in URLS.items()]
    witnesses=[record(DL/f'{name}-p{page:02d}{ext}') for name,pages in PAGES.items() for page in pages for ext in ('.txt','.png')]
    d={'schema':'gujarati-usage-canon-v1','date':'2026-08-30','reference_use':'Linguistic consultation only; not a training dataset',
       'files':acquired,'admitted_example_count':13,'ocr':'Tesseract with guj tessdata_fast; 160 dpi; psm 3',
       'readable_witnesses':witnesses,'review':'Selected OCR read; page images checked to resolve OCR number/operator errors',
       'font':record(LANG/'assets/NotoSansGujarati.ttf','https://raw.githubusercontent.com/google/fonts/main/ofl/notosansgujarati/NotoSansGujarati%5Bwdth,wght%5D.ttf')}
    (LANG/'canon/reference-lock.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
