"""Verify the complete exact-commit archive as a Git tree; freeze acquisition receipt."""
from pathlib import Path, PurePosixPath
import hashlib, json, shutil, tarfile
L=Path(__file__).resolve().parents[1]; D=L.parent/'downloads/bn-Beng-BD'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def blob(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).digest()
def tree(nodes):
    def key(item): return (item[0]+('/' if isinstance(item[1],dict) else '')).encode()
    payload=b''
    for name,value in sorted(nodes.items(),key=key):
        mode,h=('40000',tree(value)) if isinstance(value,dict) else value
        payload+=mode.encode()+b' '+name.encode()+b'\0'+h
    return hashlib.sha1(b'tree '+str(len(payload)).encode()+b'\0'+payload).digest()
def main():
    archive=D/'openstax-bundle-38cae454.tar.gz'; root={}; files=[]; size=0
    with tarfile.open(archive,'r:gz') as t:
        for m in t:
            if m.isdir(): continue
            parts=PurePosixPath(m.name).parts[1:]
            if not parts: continue
            assert '..' not in parts
            if m.issym(): data=m.linkname.encode(); mode='120000'
            else:
                assert m.isfile(), m.name
                data=t.extractfile(m).read();mode='100755' if m.mode&0o111 else '100644'
                p=D/'openstax-canonical'/Path(*parts)
                assert p.read_bytes()==data, str(p)
            node=root
            for part in parts[:-1]: node=node.setdefault(part,{})
            node[parts[-1]]=(mode,blob(data)); size+=len(data)
            files.append({'path':'/'.join(parts),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'mode':mode})
    witnessed=tree(root).hex()
    expected='7907e4c81d43de1c3b6da173f0eb273c01dc5b55'
    assert witnessed==expected, (witnessed,expected)
    assert sha(D/'pilot-source/m81243.cnxml')==sha(D/'openstax-canonical/modules/m81243/index.cnxml')
    lock=json.loads((L/'sources.lock.json').read_text())
    lock['canonical_upstream'].update({'acquisition_status':'complete_verified','method':'Exact-commit codeload tar.gz; complete archive reconstructed to publisher Git tree SHA-1','archive_url':'https://codeload.github.com/openstax/osbooks-prealgebra-bundle/tar.gz/38cae454e644abf9f0a623e876994553881597c9','archive_path':'downloads/bn-Beng-BD/openstax-bundle-38cae454.tar.gz','archive_sha256':sha(archive),'archive_bytes':archive.stat().st_size,'extracted_path':'downloads/bn-Beng-BD/openstax-canonical','file_count':len(files),'uncompressed_file_bytes':size,'reconstructed_git_tree':witnessed})
    for name in ('LICENSE','README.md'):
        p=D/'openstax-canonical'/name
        if p.exists():
            target=L/'provenance/notices'/('canonical-'+name.replace('.md','.md'))
            shutil.copyfile(p,target)
            lock['preserved_notices'].append({'source':'openstax-canonical/'+name,'copy':str(target.relative_to(L)).replace('\\','/'),'sha256':sha(target)})
    for mod in ('m81241','m82630'):
        source=D/'openstax-canonical/modules'/mod/'index.cnxml'
        target=L/'provenance/notices'/('canonical-'+mod+'-preface.cnxml')
        shutil.copyfile(source,target)
        lock['preserved_notices'].append({'source':'openstax-canonical/modules/'+mod+'/index.cnxml','copy':str(target.relative_to(L)).replace('\\','/'),'sha256':sha(target)})
    (L/'sources.lock.json').write_text(json.dumps(lock,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # Per-file witness stays small enough to review (~1 MB), full media stays ignored.
    (L/'provenance/canonical-files.json').write_text(json.dumps(files,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(lock['canonical_upstream'],indent=2))
if __name__=='__main__': main()
