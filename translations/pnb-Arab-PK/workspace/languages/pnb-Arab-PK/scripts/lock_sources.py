"""Verify acquired source packages and pin repositories; no audits or publishing."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import zipfile

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
DL = ROOT / 'downloads'
P = BASE / 'provenance'
P.mkdir(exist_ok=True)

def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], text=True).strip()

specs = [
 ('catalog', 'program-matematika-indonesia', None, None),
 ('A10', 'openstax-elementary-algebra-2e-id', None, None),
 ('A20', 'openstax-intermediate-algebra-2e-id', None, None),
 ('A30', 'openstax-precalculus-2e-id', None, None),
 ('B10', 'discrete-mathematics-open-introduction-id', None, None),
 ('B40', 'hefferon-linear-algebra-id', None, None),
 ('A10+A20 upstream', 'upstream/osbooks-prealgebra-bundle', '38cae454e644abf9f0a623e876994553881597c9', ['collections', 'modules']),
 ('A30 upstream', 'upstream/osbooks-college-algebra-bundle', '789b54099106b071d1d32bfcee454fed72eb4768', ['collections', 'modules']),
 ('B10 upstream', 'upstream/discrete-book', '82336dc87d77c3f18d2cdbc8ec1e74eb3ba38799', None),
 ('B40 upstream', 'upstream/hefferon-linear-algebra', 'df2262e089a02651c127f1dd12649c4622ee1383', None),
 ('auxiliary, unused', 'OpenLogic-id', None, None),
 ('auxiliary upstream, unused', 'upstream/OpenLogic', '9620cc73f9c8e0ad003c514a5d3748f29611c4c0', None),
]
repos = []
for role, relative, expected, sparse in specs:
    path = DL / relative
    commit = git(path, 'rev-parse', 'HEAD')
    assert expected is None or expected == commit, relative
    files = git(path, 'ls-files').splitlines()
    record = dict(role=role, local_path='downloads/' + relative, url=git(path,'remote','get-url','origin'), commit=commit, tree=git(path,'rev-parse','HEAD^{tree}'), shallow=git(path,'rev-parse','--is-shallow-repository')=='true', sparse_paths=sparse, tracked_files=len(files), present_tracked_files=sum((path / f).is_file() for f in files))
    if sparse:
        record['scope_note'] = 'Convenient sparse text checkout; complete source and media are separately materialized and blob-verified in complete_upstream_archives.'
    records = []
    for name in ['README.md','SOURCE_AUTHORITY.md','PUBLICATION.json','RELEASE_MANIFEST.json','SHA256SUMS.txt','LICENSE','LICENSE.txt','NOTICE.id-ID.md','THIRD_PARTY_NOTICES.md']:
        if (path / name).is_file():
            target = P / relative.replace('/', '--') / name
            target.parent.mkdir(exist_ok=True)
            # Retain upstream Git blob bytes, not Windows line-ending conversion.
            content = subprocess.check_output(['git','-C',str(path),'show',f'{commit}:{name}'])
            target.write_bytes(content)
            records.append({'path':str(target.relative_to(BASE)).replace('\\','/'),'sha256':hashlib.sha256(content).hexdigest()})
    record['evidence'] = records
    repos.append(record)

packages = [
 ('A10', 'A10-source.zip','v1.0.2','elementary-algebra-2e-id-ID-1.0.2-source.zip','6f04e88387e8d4e6e710dddcebb8d41e952a315231d7e203d62170c6ad9f3456', 'openstax-elementary-algebra-2e-id',82,82),
 ('A20', 'A20-v0.3.0-editable-source.zip','v0.3.0-wip','openstax-intermediate-algebra-2e-id-ID-0.3.0-wip-editable-source.zip','a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7','openstax-intermediate-algebra-2e-id',48,83),
 ('A30', 'A30-source.zip','v0.1.0-alpha.58-reader.1','precalculus-2e-id-ID-0.1.0-alpha.58-reader.1-source-core.zip','9f8ba5e44bd4d4794c559de85a5449f3b4bd279d153801b94f3d39a471f5a0ca','openstax-precalculus-2e-id',58,87),
]
archives = []
for role, local, version, filename, expected, repo, translated, total in packages:
    path = DL / 'releases' / local
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    assert actual == expected, f'Checksum mismatch: {path}: {actual}'
    dest = DL / 'extracted' / role
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        for name in z.namelist():
            target = (dest / name).resolve()
            assert target.is_relative_to(dest.resolve()), f'Unsafe archive member: {name}'
        z.extractall(dest)
        count = len(z.namelist())
    records = []
    for name in ['LICENSE.txt','NOTICE.txt','README.md','README.txt','MANIFEST.json','manifests/source-checkpoint-0030.json','00_control/AUTHORITY_RECEIPT.json','00_control/WORK_RIGHTS.json']:
        if (dest / name).is_file():
            target = P / f'{role}-release' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(dest / name, target)
            records.append({'path':str(target.relative_to(BASE)).replace('\\','/'),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    archives.append(dict(role=role,version=version,url=f'https://github.com/KokunoYumeto/{repo}/releases/download/{version}/{filename}',local_path='downloads/releases/'+local,sha256=actual,bytes=path.stat().st_size,zip_members=count,crc='pass',extracted_to='downloads/extracted/'+role,indonesian_coverage=dict(translated=translated,total=total),evidence=records))

# Only copy the pilot's component row, not perform a new rights audit.
import csv
with (DL / 'extracted/A30/00_control/COMPONENT_RIGHTS.csv').open(encoding='utf-8-sig',newline='') as f:
    component_rows = [r for r in csv.DictReader(f) if 'CNX_Precalc_Figure_01_01_001.jpg' in str(r)]
(P / 'pilot-component-notice.json').write_text(json.dumps(component_rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert component_rows, 'Missing existing figure notice'
lock = dict(schema='translation-sources-lock-v1',locale='pnb-Arab-PK',purpose='translation inputs only; no training/fine-tuning dataset',observed_date='2026-08-30',repositories=repos,archives=archives,notes=['B10 is DMOI, not Open Logic. Auxiliary OpenLogic clones are retained unused.', 'A20 repository README/manifest are older than v0.3.0-wip release; use the 48-module editable-source package.', 'Failed/interrupted A20-source.zip download is superseded and not admitted or extracted.', 'Frozen upstream formulas are authoritative; Indonesian editions are comparison witnesses.'])
complete = json.loads((P / 'complete-upstreams.json').read_text(encoding='utf-8'))
assert complete['status'] == 'pass'
lock['complete_upstream_archives'] = complete['archives']
(BASE / 'sources.lock.json').write_text(json.dumps(lock,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Pinned {len(repos)} repositories and verified/extracted {len(archives)} source archives')
