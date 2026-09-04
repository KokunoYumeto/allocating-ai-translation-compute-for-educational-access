"""Read-only verification of existing source identity and selected text closure."""
from pathlib import Path
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[1]
lock=json.loads((BASE/'sources.lock.json').read_text(encoding='utf-8'))
def git(path,*args):
    return subprocess.check_output(['git','-C',str(path),*args])

for r in lock['repositories']:
    path=ROOT/r['local_path']
    assert git(path,'rev-parse','HEAD').decode().strip()==r['commit'], r['role']
    assert git(path,'rev-parse','HEAD^{tree}').decode().strip()==r['tree'], r['role']
    for item in r['evidence']:
        assert hashlib.sha256((BASE/item['path']).read_bytes()).hexdigest()==item['sha256'], item['path']
for a in lock['archives']:
    assert hashlib.sha256((ROOT/a['local_path']).read_bytes()).hexdigest()==a['sha256'],a['role']
    for item in a['evidence']:
        assert hashlib.sha256((BASE/item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
for a in lock['complete_upstream_archives']:
    assert hashlib.sha256((ROOT/a['local_path']).read_bytes()).hexdigest()==a['sha256'],a['repository']
    assert (ROOT/a['full_extract']).is_dir(),a['repository']

counts={}
for role,repo,collection in [('A10','osbooks-prealgebra-bundle','elementary-algebra-2e'),('A20','osbooks-prealgebra-bundle','intermediate-algebra-2e'),('A30','osbooks-college-algebra-bundle','precalculus-2e')]:
    path=ROOT/'downloads/upstream'/repo
    doc=ET.parse(path/'collections'/f'{collection}.collection.xml')
    modules=[e.get('document') for e in doc.iter() if e.tag.endswith('}module')]
    for module in modules:
        relative=f'modules/{module}/index.cnxml'
        # EOL conversion is irrelevant to XML, but every local parsed tree must
        # equal its exact pinned Git blob after newline normalization.
        raw=git(path,'show',f'HEAD:{relative}')
        actual=(path/relative).read_bytes()
        assert raw.replace(b'\r\n',b'\n')==actual.replace(b'\r\n',b'\n'), relative
    counts[role]=len(modules)
assert counts=={'A10':82,'A20':83,'A30':87},counts
pilot=json.loads((BASE/'source-excerpts/manifest.json').read_text(encoding='utf-8'))
raw=git(ROOT/'downloads/upstream/osbooks-college-algebra-bundle','show',pilot['commit']+':'+pilot['path'])
assert hashlib.sha256(raw).hexdigest()==pilot['full_module_sha256']
assert hashlib.sha256((BASE/'assets/Figure_01_01_001.jpg').read_bytes()).hexdigest()==pilot['image']['sha256']
receipt={'status':'pass','repository_count':len(lock['repositories']),'release_archives_checked':len(lock['archives']),'complete_upstream_archives_checked':len(lock['complete_upstream_archives']),'canonical_openstax_module_closure':counts,'pilot_source_blob_sha256':pilot['full_module_sha256'],'scope':'All assigned text modules, release archives and metadata; full OpenStax source/media archive identities rechecked. Every upstream archive blob verified by complete_upstreams.py; see provenance/complete-upstreams.json.', 'sources_lock_sha256':hashlib.sha256((BASE/'sources.lock.json').read_bytes()).hexdigest()}
(BASE/'qa/acquisition.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(receipt)
