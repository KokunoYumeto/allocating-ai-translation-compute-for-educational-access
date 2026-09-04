"""Reacquire exactly the locked translation inputs; never advance branch tips."""
from pathlib import Path
import hashlib
import json
import subprocess
import urllib.request

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
lock = json.loads((BASE/'sources.lock.json').read_text(encoding='utf-8'))

def run(*args):
    subprocess.run(args, check=True)

def git(path,*args):
    return subprocess.check_output(['git','-C',str(path),*args],text=True).strip()

for entry in lock['repositories']:
    path=ROOT/entry['local_path']
    if not path.exists():
        path.parent.mkdir(parents=True,exist_ok=True)
        run('git','clone','--depth','1','--filter=blob:none','--no-checkout',entry['url'],str(path))
        run('git','-C',str(path),'fetch','--depth','1','origin',entry['commit'])
        if entry['sparse_paths']:
            run('git','-C',str(path),'sparse-checkout','set',*entry['sparse_paths'])
        run('git','-C',str(path),'checkout','--detach',entry['commit'])
    else:
        assert git(path,'rev-parse','HEAD') == entry['commit'], f'Refusing to replace existing checkout: {path}'
    assert git(path,'rev-parse','HEAD^{tree}') == entry['tree']

def download(url,path,sha):
    if path.exists():
        assert hashlib.sha256(path.read_bytes()).hexdigest()==sha, f'Existing file differs: {path}'
        return
    path.parent.mkdir(parents=True,exist_ok=True)
    partial=path.with_suffix(path.suffix+'.part')
    request=urllib.request.Request(url,headers={'User-Agent':'Translation-source-acquisition/1.0'})
    with urllib.request.urlopen(request,timeout=60) as response, partial.open('wb') as output:
        while chunk:=response.read(1024*1024): output.write(chunk)
    assert hashlib.sha256(partial.read_bytes()).hexdigest()==sha, f'Download checksum mismatch: {url}'
    partial.rename(path)

for entry in lock['archives']:
    download(entry['url'],ROOT/entry['local_path'],entry['sha256'])
for entry in lock['complete_upstream_archives']:
    download(entry['url'],ROOT/entry['local_path'],entry['sha256'])

pilot=json.loads((BASE/'source-excerpts/manifest.json').read_text(encoding='utf-8'))
content=subprocess.check_output(['git','-C',str(ROOT/'downloads/upstream/osbooks-college-algebra-bundle'),'show',pilot['commit']+':'+pilot['path']])
assert hashlib.sha256(content).hexdigest()==pilot['full_module_sha256']
(ROOT/'downloads/m49301.cnxml').write_bytes(content)
download('https://raw.githubusercontent.com/openstax/osbooks-college-algebra-bundle/'+pilot['commit']+'/'+pilot['image']['path'],ROOT/'downloads/Figure_01_01_001.jpg',pilot['image']['sha256'])
print('Locked repositories, archives and pilot image are present. Run complete_upstreams.py, then lock_sources.py to verify/extract.')
