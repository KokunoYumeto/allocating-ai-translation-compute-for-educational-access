"""Hash the bounded publishable payload, excluding the checksum itself and local log."""
from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parent
excluded={'SHA256SUMS','CHECKSUMS.sha256','MANIFEST.json','BUILD_LOG.md'}
files=sorted(p for p in B.rglob('*') if p.is_file() and p.relative_to(B).as_posix() not in excluded and '__pycache__' not in p.parts)
manifest={'schema':'bounded-reader-file-inventory-v1','locale':'pnb-Arab-PK','excludes':['MANIFEST.json','SHA256SUMS','CHECKSUMS.sha256','BUILD_LOG.md'],'files':[{'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
(B/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files.append(B/'MANIFEST.json'); files.sort()
lines=[hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(B).as_posix() for p in files]
(B/'SHA256SUMS').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(B/'CHECKSUMS.sha256').write_bytes((B/'SHA256SUMS').read_bytes())
for line in lines:
    sha,rel=line.split('  ',1)
    assert hashlib.sha256((B/rel).read_bytes()).hexdigest()==sha
print(json.dumps({'payload_files':len(files),'payload_bytes_excluding_checksum':sum(p.stat().st_size for p in files),'checksum_sha256':hashlib.sha256((B/'SHA256SUMS').read_bytes()).hexdigest(),'index_sha256':hashlib.sha256((B/'index.html').read_bytes()).hexdigest()}))
