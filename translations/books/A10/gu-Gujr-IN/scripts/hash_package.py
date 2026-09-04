"""Create a sorted SHA-256 manifest for the completed bounded package."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
qa=json.loads((ROOT/'QA.json').read_text(encoding='utf8'))
browser=json.loads((ROOT/'BROWSER_QA.json').read_text(encoding='utf8'))
assert qa['deterministic_status']=='pass' and qa['visual_qa'].startswith('pass:')
assert browser['status']=='pass' and len(browser['pages'])==40
lines=[];total=0
for p in sorted(ROOT.rglob('*')):
    if p.is_file() and p.name!='CHECKSUMS.sha256':
        b=p.read_bytes();total+=len(b)
        lines.append(hashlib.sha256(b).hexdigest()+'  '+p.relative_to(ROOT).as_posix())
manifest='\n'.join(lines)+'\n'
(ROOT/'CHECKSUMS.sha256').write_text(manifest,encoding='utf8',newline='\n')
print(json.dumps({'files_hashed':len(lines),'bytes_hashed':total,'checksums_sha256':hashlib.sha256(manifest.encode()).hexdigest(),'package_json_sha256':hashlib.sha256((ROOT/'PACKAGE.json').read_bytes()).hexdigest(),'qa_json_sha256':hashlib.sha256((ROOT/'QA.json').read_bytes()).hexdigest(),'index_sha256':hashlib.sha256((ROOT/'index.html').read_bytes()).hexdigest(),'fraction_answers_sha256':hashlib.sha256((ROOT/'support/fraction-answers.json').read_bytes()).hexdigest()}))
