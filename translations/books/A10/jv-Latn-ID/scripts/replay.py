"""Rebuild and hash-compare reader outputs without modifying recovered inputs."""
from pathlib import Path
import hashlib,json,subprocess,sys
root=Path(__file__).resolve().parents[1]
names=['jv-academic.html','jv-conversation.html','id-academic.html','PACKAGE.json','provenance/RECOVERY-INPUTS.json','provenance/SOURCE-BOUNDARY.json']
names += [p.relative_to(root).as_posix() for p in (root/'source/assembled').glob('*.cnxml')]
def hashes(): return {n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in names}
before=hashes()
subprocess.run([sys.executable,str(root/'scripts/recover.py'),sys.argv[1]],check=True)
after=hashes()
assert before==after,'Non-deterministic build output'
(root/'provenance/BUILD-REPLAY.json').write_text(json.dumps({'passed':True,'outputs_compared':len(names),'sha256':after,'method':'Fresh source component reads and independent rerender; SHA-256 byte comparison; output path argument excluded from payload.'},indent=2)+'\n',encoding='utf-8')
print('Deterministic byte replay passed:',len(names),'outputs')
