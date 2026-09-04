"""Record only explicitly inspected PNG pages; never automatic visual approval."""
import argparse,json
from pathlib import Path
from build import L,write,sha

def digest(path):return sha(path.read_bytes())

def main():
    p=argparse.ArgumentParser();p.add_argument('job');p.add_argument('kind',choices=['print','screen'])
    p.add_argument('--version',default='reading-v1');p.add_argument('--pages',default='');p.add_argument('--transfer-from')
    args=p.parse_args()
    receipt=json.loads((L/'output/pdf'/(args.job+'-build-receipt.json')).read_text(encoding='utf-8'))
    relative='output/pdf/'+args.job+'-'+args.kind+'.pdf'
    info=next(x for x in receipt if x['file']==relative)
    assert digest(L/relative)==info['sha256']
    out=L/'output/pdf'/(args.version+'-'+args.job+'-'+args.kind+'-visual.json')
    record=json.loads(out.read_text(encoding='utf-8')) if out.exists() else {'pdf':relative,'pdf_sha256':info['sha256'],'total_pages':info['pages'],'renderer':'Bundled Poppler pdftoppm, PNG, 120 dpi','inspected_png_sha256':{},'review_method':{}}
    assert record['pdf_sha256']==info['sha256']
    width=len(str(info['pages']))
    folder=L.parent/'tmp/pdfs/bn-Beng-BD'/args.version/(args.job+'-'+args.kind)
    def png(n):return folder/('page-'+str(n).zfill(width)+'.png')
    if args.transfer_from:
        prior=json.loads(Path(args.transfer_from).read_text(encoding='utf-8'))
        for page,dig in prior['inspected_png_sha256'].items():
            if png(int(page)).exists() and digest(png(int(page)))==dig:
                record['inspected_png_sha256'][page]=dig
                record['review_method'][page]='Exact PNG hash match to '+Path(args.transfer_from).name
    for part in filter(None,args.pages.split(',')):
        limits=part.split('-');first,last=int(limits[0]),int(limits[-1])
        assert 1<=first<=last<=info['pages']
        for page in range(first,last+1):
            record['inspected_png_sha256'][str(page)]=digest(png(page))
            record['review_method'][str(page)]='Direct page-image inspection'
    record['all_pages_inspected']=set(record['inspected_png_sha256'])=={str(n) for n in range(1,info['pages']+1)}
    record['scope']='Visual shaping/layout/page-boundary review only. No native-teacher, browser, screen-reader or physical-print approval; PDFs remain untagged and Bengali copy/search unreliable.'
    write(out,json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'job':args.job,'kind':args.kind,'seen':len(record['inspected_png_sha256']),'pages':info['pages']}))

if __name__=='__main__':main()
