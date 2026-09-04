"""Prove full OpenStax archives match every pinned Git blob; extract locally."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[1]
records=[]
for name,filename,commit in [
    ('osbooks-prealgebra-bundle','upstream-prealgebra-pinned.zip','38cae454e644abf9f0a623e876994553881597c9'),
    ('osbooks-college-algebra-bundle','upstream-college-algebra-pinned.zip','789b54099106b071d1d32bfcee454fed72eb4768')
]:
    archive=ROOT/'downloads/releases'/filename
    repo=ROOT/'downloads/upstream'/name
    raw=subprocess.check_output(['git','-C',str(repo),'ls-tree','-r','-z',commit])
    expected={}
    for line in raw.split(b'\0'):
        if not line: continue
        identity,path=line.split(b'\t',1)
        mode,kind,oid=identity.split()
        if kind==b'blob': expected[path.decode('utf-8')]=oid.decode()
    prefix=name+'-'+commit+'/'
    target=ROOT/'downloads/complete-upstream'/name
    target.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        present={n[len(prefix):] for n in z.namelist() if n.startswith(prefix) and not n.endswith('/')}
        assert present==set(expected), f'Archive tree differs: {name}; missing {set(expected)-present}, extra {present-set(expected)}'
        for path,oid in expected.items():
            data=z.read(prefix+path)
            assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==oid, path
            output=(target/path).resolve()
            assert output.is_relative_to(target.resolve())
            output.parent.mkdir(parents=True,exist_ok=True)
            output.write_bytes(data)
    records.append({'repository':name,'commit':commit,'url':f'https://codeload.github.com/openstax/{name}/zip/{commit}','local_path':str(archive.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'bytes':archive.stat().st_size,'all_git_blobs_verified':len(expected),'crc':'pass','full_extract':str(target.relative_to(ROOT)).replace('\\','/'),'symlink_policy':'Git blobs are materialized as ordinary files, including link payloads if present; source text/asset bytes verified.'})
receipt={'status':'pass','archives':records,'method':'SHA-256 archive identity plus every Git blob SHA-1 compared to pinned tree; not inferred from clean sparse checkout','acquisition_note':'Prealgebra archive copied read-only from sibling task e4ec; college-algebra archive downloaded directly. No sibling files changed.'}
(BASE/'provenance/complete-upstreams.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,indent=2))
