"""Resolve selected A30 media against exact upstream Git blob IDs."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from acquire_releases import download,sha

ROOT=Path(__file__).resolve().parents[3]
base=ROOT/'downloads/canonical-precalculus'
repo=ROOT/'downloads/osbooks-college-algebra-bundle'
pin='789b54099106b071d1d32bfcee454fed72eb4768'
names=set()
for mid in ['m49301','m49324']:
    doc=ET.parse(base/'modules'/mid/'index.cnxml')
    names.update(Path(e.get('src')).name for e in doc.iter() if e.get('src') and '/media/' in e.get('src'))
def acquire(name):
    url=f'https://raw.githubusercontent.com/openstax/osbooks-college-algebra-bundle/{pin}/media/{name}'
    dest=base/'media'/name
    expected=subprocess.check_output(['git','-C',str(repo),'rev-parse',f'{pin}:media/{name}']).decode().strip()
    if not dest.exists(): download(url,dest)
    raw=dest.read_bytes()
    actual=hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
    assert actual==expected,(name,actual,expected)
    return {'name':name,'url':url,'git_blob':expected,'sha256':sha(dest),'bytes':len(raw)}
with ThreadPoolExecutor(max_workers=4) as pool:
    assets=list(pool.map(acquire,sorted(names)))
out=ROOT/'languages/bn-Beng-IN/provenance/A30/selected-media.lock.json'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps({'modules':['m49301','m49324'],'assets':assets},indent=2)+'\n')
print('A30 selected media verified:',len(assets))
