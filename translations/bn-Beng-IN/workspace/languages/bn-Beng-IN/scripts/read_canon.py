"""Render and OCR explicitly selected reference pages. Outputs are ignored inputs."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('pdf',type=Path)
    parser.add_argument('pages',help='one-based comma-separated PDF page numbers')
    args=parser.parse_args()
    pages=[int(x) for x in args.pages.split(',')]
    out=args.pdf.parent/args.pdf.stem
    out.mkdir(exist_ok=True)
    for p in pages:
        subprocess.run(['pdftoppm','-f',str(p),'-l',str(p),'-r','180',
                        '-singlefile','-png',str(args.pdf),str(out/f'p{p:03}')],
                       check=True,capture_output=True)
    def ocr(p):
        dest=out/f'p{p:03}'
        subprocess.run(['tesseract',str(dest.with_suffix('.png')),str(dest),
                        '--tessdata-dir','downloads/tessdata','-l','ben','--psm','3'],check=True,capture_output=True)
        text=dest.with_suffix('.txt').read_text(encoding='utf-8')
        return {'pdf_page':p,'renderer':'Poppler pdftoppm / 180dpi','png':str(dest.with_suffix('.png')),'ocr_text':str(dest.with_suffix('.txt')),
                'bengali_characters':sum('\u0980'<=c<='\u09ff' for c in text),
                'ocr_sha256':hashlib.sha256(text.encode()).hexdigest()}
    with ThreadPoolExecutor(max_workers=3) as pool:
        result=list(pool.map(ocr,pages))
    receipt=out/'ocr-receipt.json'
    previous=json.loads(receipt.read_text(encoding='utf-8')) if receipt.is_file() else []
    merged={r['pdf_page']:r for r in previous}
    merged.update({r['pdf_page']:r for r in result})
    receipt.write_text(json.dumps([merged[p] for p in sorted(merged)],indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
