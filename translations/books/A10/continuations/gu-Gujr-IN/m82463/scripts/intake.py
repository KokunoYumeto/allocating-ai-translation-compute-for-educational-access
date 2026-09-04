"""Acquire only the assigned module and its exact media; shared inputs read-only."""
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPORT=Path(sys.argv[1])
PREFIX='gu-Gujr-IN/workspace/gu-Gujr-IN/'
COMMIT='38cae454e644abf9f0a623e876994553881597c9'
def sha(b):return hashlib.sha256(b).hexdigest()
mb=(EXPORT/'EXPORT_MANIFEST.json').read_bytes()
assert sha(mb)=='772c054d8b6f9337f62a89df2fc2c726ed2d97c9077cb07f07dd0150e5ffe5a1'
manifest={r['path']:r for r in json.loads(mb)['files']}
pins=[]
def copy(rel,target):
    b=(EXPORT/(PREFIX+rel)).read_bytes();r=manifest[PREFIX+rel]
    assert sha(b)==r['export_sha256'] and len(b)==r['bytes']
    p=ROOT/target;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    pins.append({'path':target,'export_path':PREFIX+rel,'sha256':sha(b),'bytes':len(b)})
    return b
draft=copy('translations/a10-m82463.gu.cnxml','source/recovered.gu.cnxml')
copy('translations/qa_a10_m82463_math.py','scripts/recovered_math_qa.py')
for rel in ['canon/README.md','canon/examples.csv','canon/targeted-examples.md','canon/reference-lock.json','terminology.csv','notices/A10-LICENSE.txt','notices/A10-NOTICE.txt','assets/OFL.txt','assets/NotoSansGujarati.ttf','assets/style.css']:
    copy(rel,rel)
copy('provenance/A10-canonical-manifest.csv','provenance/A10-canonical-manifest.csv')
audit=json.loads((EXPORT/(PREFIX+'reviews/a10-m82463-media-source-audit.json')).read_text(encoding='utf8'))
assert sha((EXPORT/(PREFIX+'reviews/a10-m82463-media-source-audit.json')).read_bytes())==manifest[PREFIX+'reviews/a10-m82463-media-source-audit.json']['export_sha256']
def acquire(args):
    rel,target,expected=args;p=ROOT/target
    if p.exists():b=p.read_bytes()
    else:
        req=urllib.request.Request(f'https://raw.githubusercontent.com/openstax/osbooks-prealgebra-bundle/{COMMIT}/{rel}',headers={'User-Agent':'A10-m82463-recovery/1.0'})
        with urllib.request.urlopen(req,timeout=45)as response:b=response.read()
    assert sha(b)==expected,(target,sha(b),expected)
    p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    return {'path':target,'source_path':rel,'sha256':sha(b),'bytes':len(b),'canonical_commit':COMMIT}
tasks=[('modules/m82463/index.cnxml','source/en.cnxml','b6345a5a6a99108f9d32d6518445a4ae70a6b0c54a258021dffc6f2b77b8278a')]
for x in audit:tasks.append(('media/'+x['name'],'media/'+x['name'],x['sha256']))
with ThreadPoolExecutor(max_workers=4)as pool:pins.extend(pool.map(acquire,tasks))
(ROOT/'provenance/INPUT_PINS.json').write_text(json.dumps(pins,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(ROOT/'provenance/MEDIA_SOURCE.json').write_text(json.dumps([{k:v for k,v in x.items()if k!='path'}for x in audit],ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'source_recovered':True,'draft_sha256':sha(draft),'media':len(audit),'pinned_inputs':len(pins)}))
