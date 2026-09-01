"""Record explicitly inspected page ranges; transfer only exact PNG matches.

This does not inspect images or grant approval automatically. --pages must list
only pages the reviewer has actually seen. --transfer-from uses recorded hashes.
"""
import argparse, hashlib, json
from pathlib import Path
from build import L, write

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--version',required=True)
    p.add_argument('--kind',choices=('print','screen'),required=True)
    p.add_argument('--pages',default='')
    p.add_argument('--transfer-from')
    args=p.parse_args()
    pdf=L/'output/pdf'/f'u02-complete-{args.kind}.pdf'
    build=json.loads((L/'output/pdf/u02-build-receipt.json').read_text(encoding='utf-8'))
    info=next(x for x in build if x['file']==pdf.relative_to(L).as_posix())
    assert digest(pdf)==info['sha256']
    folder=L.parent/'tmp/pdfs/bn-Beng-BD/U02'
    output=L/'output/pdf'/f'u02-visual-{args.version}-{args.kind}.json'
    result=json.loads(output.read_text(encoding='utf-8')) if output.exists() else {
        'pdf_sha256':info['sha256'],'total_pages':info['pages'],
        'renderer':'Bundled Poppler, PNG, 95 dpi',
        'inspected_png_sha256':{},'review_method':{}}
    assert result['pdf_sha256']==info['sha256']
    def png(page):return folder/f'{args.kind}-{args.version}-{page:02d}.png'
    if args.transfer_from:
        prior=json.loads(Path(args.transfer_from).read_text(encoding='utf-8'))
        for key,value in prior.get('inspected_png_sha256',prior.get('print_png_sha256',{})).items():
            if png(int(key)).is_file() and digest(png(int(key)))==value:
                result['inspected_png_sha256'][key]=value
                result['review_method'][key]='Exact PNG hash match to '+Path(args.transfer_from).name
    for part in filter(None,args.pages.split(',')):
        bounds=part.split('-');start=int(bounds[0]);end=int(bounds[-1])
        assert 1<=start<=end<=info['pages']
        for page in range(start,end+1):
            result['inspected_png_sha256'][str(page)]=digest(png(page))
            result['review_method'][str(page)]='Direct page-image inspection'
    result['all_pages_inspected']=set(result['inspected_png_sha256'])=={str(n) for n in range(1,info['pages']+1)}
    result['scope']='Visual page record only; separate defect/reproducibility gates remain. No teacher, screen-reader, browser or physical-print validation.'
    write(output,json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'file':str(output),'reviewed':len(result['inspected_png_sha256']),'total':info['pages']}))
if __name__=='__main__':main()
