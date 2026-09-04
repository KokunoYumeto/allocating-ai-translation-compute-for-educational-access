"""Hash-bound PDF rebuild/visual status; never infer unseen page approval."""
import argparse,json,subprocess,sys
from build_new_reading_editions import L,JOBS,sha,write

def digest(path):return sha(path.read_bytes())

def main():
    p=argparse.ArgumentParser();p.add_argument('--rebuild-cycles',type=int,default=0);p.add_argument('--require-all-visual',action='store_true');args=p.parse_args()
    assert 0<=args.rebuild_cycles<=2
    output=L/'output/pdf/new-reading-status.json'
    prior=json.loads(output.read_text(encoding='utf-8')) if output.exists() else {}
    infos=[r for job in JOBS for r in json.loads((L/'output/pdf'/(job+'-build-receipt.json')).read_text(encoding='utf-8'))]
    assert len(infos)==10
    snapshot={r['file']:r['sha256'] for r in infos}
    snapshot.update({r['input_html']:r['input_html_sha256'] for r in infos})
    snapshot['assets/NumeracyBanglaMath.ttf']=infos[0]['font_sha256']
    unchanged=json.loads((L/'output/U02/reproducibility.json').read_text(encoding='utf-8'))['sha256']
    def check_bytes():
        for name,expected in {**snapshot,**unchanged}.items():
            assert digest(L/name)==expected,('Changed bytes',name)
    check_bytes()
    for cycle in range(args.rebuild_cycles):
        for job in JOBS:
            subprocess.run([sys.executable,'-B',str(L/'tools/build_new_reading_editions.py'),job],check=True,stdout=subprocess.DEVNULL)
        check_bytes();print(json.dumps({'fresh_cycle':cycle+1,'hashes_unchanged':len(set(snapshot)|set(unchanged))}),flush=True)
    infos=[r for job in JOBS for r in json.loads((L/'output/pdf'/(job+'-build-receipt.json')).read_text(encoding='utf-8'))]
    results=[]
    for r in infos:
        assert r['semantic_flowable_input_coverage_pass'] and r['all_pages_bounds_checked']
        stem=(L/r['file']).stem
        candidates=[]
        for path in (L/'output/pdf').glob('reading-*-'+stem+'-visual.json'):
            record=json.loads(path.read_text(encoding='utf-8'))
            if record['pdf_sha256']!=r['sha256']:continue
            assert record['total_pages']==r['pages']
            version=path.name.removesuffix('-'+stem+'-visual.json')
            folder=L.parent/'tmp/pdfs/bn-Beng-BD'/version/stem
            for page,expected in record['inspected_png_sha256'].items():
                assert 1<=int(page)<=r['pages']
                assert digest(folder/('page-'+page.zfill(len(str(r['pages'])))+'.png'))==expected
            candidates.append((len(record['inspected_png_sha256']),path,record))
        best=max(candidates,key=lambda c:c[0]) if candidates else None
        seen=best[0] if best else 0
        complete=seen==r['pages']
        assert not complete or best[2]['all_pages_inspected']
        results.append({'file':r['file'],'sha256':r['sha256'],'pages':r['pages'],'visually_inspected_pages':seen,'all_pages_visually_inspected':complete,'visual_receipt':best[1].relative_to(L).as_posix() if best else None})
    cycles=args.rebuild_cycles
    if prior.get('sha256')==snapshot and prior.get('builder_sha256')==digest(L/'tools/build_new_reading_editions.py'):cycles=max(cycles,prior.get('fresh_build_cycles',0))
    status={'schema':'bn-Beng-BD.new-reading-status.v1','pdfs':results,'pages':sum(r['pages'] for r in results),'visually_inspected_pages':sum(r['visually_inspected_pages'] for r in results),'all_visual_reviews_complete':all(r['all_pages_visually_inspected'] for r in results),'fresh_build_cycles':cycles,'sha256':snapshot,'unchanged_prior_U01_U02_hashes_verified':len(unchanged),'builder_sha256':digest(L/'tools/build_new_reading_editions.py'),'scope':'Draft reading copies only; HTML is the semantic edition. No native-teacher/browser/screen-reader/physical-print approval. PDFs untagged; Bengali copy/search unreliable.'}
    write(output,json.dumps(status,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:status[k] for k in ('pages','visually_inspected_pages','all_visual_reviews_complete','fresh_build_cycles','unchanged_prior_U01_U02_hashes_verified')}))
    if args.require_all_visual:assert status['all_visual_reviews_complete'],'Uninspected pages remain'

if __name__=='__main__':main()
