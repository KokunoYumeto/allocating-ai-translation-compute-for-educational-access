"""Reacquire exact locked corpora; no audits, training exports, or publication."""
from pathlib import Path
import hashlib,json,subprocess,tarfile,urllib.request,zipfile
L=Path(__file__).resolve().parents[1]; R=L.parent
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def run(*a):return subprocess.check_output(a,text=True,encoding='utf-8').strip()
def download(url,p,expected):
    p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():
        if sha(p)==expected:return
        raise RuntimeError('Existing file differs; inspect before replacing: '+str(p))
    partial=p.with_suffix(p.suffix+'.partial')
    if partial.exists():raise RuntimeError('Inspect earlier partial download: '+str(partial))
    with urllib.request.urlopen(url,timeout=120) as response, partial.open('wb') as f:
        while block:=response.read(1024*1024):f.write(block)
    assert sha(partial)==expected,'Downloaded hash mismatch: '+url
    partial.rename(p)
def main():
    lock=json.loads((L/'sources.lock.json').read_text())
    for repo in lock['repositories']:
        p=R/repo['path']
        if not p.exists():
            p.mkdir(parents=True)
            run('git','init',str(p));run('git','-C',str(p),'config','core.autocrlf','false')
            run('git','-C',str(p),'remote','add','origin',repo['url'])
            run('git','-C',str(p),'fetch','--depth','1','origin',repo['commit'])
            run('git','-C',str(p),'checkout','--detach','FETCH_HEAD')
        assert run('git','-C',str(p),'rev-parse','HEAD')==repo['commit']
        assert run('git','-C',str(p),'rev-parse','HEAD^{tree}')==repo['tree']
        files=run('git','-C',str(p),'ls-files','-z').split('\0')
        assert all((p/f).exists() for f in files if f),'Sparse/missing checkout'
        print(repo['assignment'],'complete',flush=True)
    a=lock['canonical_upstream'];p=R/a['archive_path']
    download(a['archive_url'],p,a['archive_sha256'])
    dest=R/a['extracted_path']
    if not dest.exists():
        dest.mkdir(parents=True)
        with tarfile.open(p,'r:gz') as t:
            for m in t:
                parts=Path(m.name).parts[1:]
                if not parts:continue
                m.name='/'.join(parts)
                target=(dest/m.name).resolve()
                assert target.is_relative_to(dest.resolve())
                t.extract(m,dest,filter='data')
    a=lock['a10_source_release'];p=R/a['path'];download(a['url'],p,a['sha256'])
    dest=R/'downloads/bn-Beng-BD/a10-source'
    if not dest.exists():
        with zipfile.ZipFile(p) as z:
            for name in z.namelist():assert (dest/name).resolve().is_relative_to(dest.resolve())
            z.extractall(dest)
    print('Exact source archives available. Run verify_sources.py to reconstruct the canonical Git tree.')
if __name__=='__main__':main()
