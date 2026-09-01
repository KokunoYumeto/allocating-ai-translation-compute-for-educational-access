"""Freeze small reviewable source witnesses; corpora remain ignored translation inputs."""
from pathlib import Path
import copy, hashlib, json, shutil, subprocess, xml.etree.ElementTree as ET

L = Path(__file__).resolve().parents[1]
R = L.parent
D = R / 'downloads/bn-Beng-BD'
NS = 'http://cnx.rice.edu/cnxml'
ET.register_namespace('', NS)
ET.register_namespace('m', 'http://www.w3.org/1998/Math/MathML')
ET.register_namespace('md', 'http://cnx.rice.edu/mdml')
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], text=True, encoding='utf-8').strip()

def main():
    lock_path = L / 'sources.lock.json'
    previous = json.loads(lock_path.read_text(encoding='utf-8')) if lock_path.exists() else {}
    source = D / 'pilot-source/m81243.cnxml'
    root = ET.parse(source).getroot()
    content = root.find(f'{{{NS}}}content')
    subset = ET.Element(f'{{{NS}}}document', {'data-source-module': 'm81243'})
    for section in list(content)[:2]: subset.append(copy.deepcopy(section))
    witness = L / 'provenance/u01-source-extract.cnxml'
    witness.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(subset).write(witness, encoding='utf-8', xml_declaration=True)
    # Exact notices copied without editing. Their individual identities are locked.
    notices = [
        ('a00-id/LICENSE', 'a00-LICENSE.txt'),
        ('a00-id/README.md', 'a00-README.md'),
        ('a00-id/modules/m81241/index.cnxml', 'a00-preface.id.cnxml'),
        ('a10-source/NOTICE.txt', 'a10-NOTICE.txt'),
        ('a10-source/LICENSE.txt', 'a10-LICENSE.txt'),
        ('a10-id/SOURCE_AUTHORITY.md', 'a10-SOURCE_AUTHORITY.md'),
        ('a10-id/MODEL_PROVENANCE.md', 'a10-MODEL_PROVENANCE.md'),
        ('a10-release/release-manifest.json', 'a10-release-manifest.json'),
        ('a10-release/SHA256SUMS.txt', 'a10-SHA256SUMS.txt'),
        ('program/LICENSE', 'program-LICENSE.txt')]
    notice_locks = []
    for relative, name in notices:
        target = L / 'provenance/notices' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(D / relative, target)
        notice_locks.append({'source': relative, 'copy': str(target.relative_to(L)).replace('\\','/'), 'sha256': digest(target)})
    authority_path = D / 'program/backend/v2.1/planning/educational-access/authority_snapshot.json'
    authority = json.loads(authority_path.read_text(encoding='utf-8'))
    def walk(x):
        if isinstance(x, dict):
            yield x
            for v in x.values(): yield from walk(v)
        elif isinstance(x, list):
            for v in x: yield from walk(v)
    ax = [x for x in walk(authority) if x.get('portfolio_id') in ('AX-1','AX-3')]
    save(L / 'provenance/AX-specifications.json', {'source_file': str(authority_path.relative_to(R)).replace('\\','/'), 'source_sha256': digest(authority_path), 'specifications': ax})
    repos = []
    for folder, code in [('program','catalog/AX-1/AX-3'),('a00-id','A00'),('a10-id','A10-wrapper')]:
        p = D / folder
        files = git(p, 'ls-files').splitlines()
        repos.append({'assignment':code, 'path':str(p.relative_to(R)).replace('\\','/'), 'url':git(p,'remote','get-url','origin'), 'commit':git(p,'rev-parse','HEAD'), 'tree':git(p,'rev-parse','HEAD^{tree}'), 'tracked_files':len(files), 'working_bytes':sum((p/f).stat().st_size for f in files), 'shallow':git(p,'rev-parse','--is-shallow-repository') == 'true'})
    release = json.loads((D / 'a10-release/release-manifest.json').read_text())
    expected = next(x for x in release['artifacts'] if x['filename'].endswith('-source.zip'))
    assert digest(D/'a10-release/source.zip') == expected['sha256']
    module_checks = []
    for module in release['module_identities']:
        p = D / 'a10-source/translated/modules' / module['module_id'] / 'index.cnxml'
        assert digest(p) == module['sha256'], p
        module_checks.append(module['module_id'])
    lock = {'schema':'bn-Beng-BD.sources.v1', 'acquired_date':'2026-08-30', 'purpose':'Translation inputs only; no training/fine-tuning dataset.', 'repositories':repos,
        'a10_source_release':{'tag':'v1.0.2','url':'https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id/releases/download/v1.0.2/'+expected['filename'], 'path':'downloads/bn-Beng-BD/a10-release/source.zip', 'sha256':expected['sha256'], 'bytes':expected['bytes'], 'translated_modules_verified':len(module_checks), 'manifest_sha256':digest(D/'a10-release/release-manifest.json')},
        'canonical_upstream':{'url':'https://github.com/openstax/osbooks-prealgebra-bundle','commit':release['source_authority']['commit'],'tree':release['source_authority']['tree'],'acquisition_status':'pending_archive_completion'},
        'pilot_source':{'module':'m81243', 'url':'https://raw.githubusercontent.com/openstax/osbooks-prealgebra-bundle/'+release['source_authority']['commit']+'/modules/m81243/index.cnxml','complete_module_sha256':digest(source),'selected_sections':['fs-id1830385','fs-id2340048'],'extract_sha256':digest(witness),'extract_path':'provenance/u01-source-extract.cnxml'}, 'preserved_notices':notice_locks}
    # Re-freezing small witnesses must not erase a completed upstream verification.
    old_canonical = previous.get('canonical_upstream', {})
    if old_canonical.get('acquisition_status') == 'complete_verified':
        assert all(old_canonical[key] == lock['canonical_upstream'][key] for key in ('url','commit','tree'))
        lock['canonical_upstream'] = old_canonical
    existing_copies = {item['copy'] for item in notice_locks}
    for item in previous.get('preserved_notices', []):
        if item['copy'] not in existing_copies:
            assert digest(L / item['copy']) == item['sha256'], item['copy']
            notice_locks.append(item)
    save(lock_path, lock)
    print(json.dumps({'repos':repos,'a10_modules_verified':len(module_checks),'source_extract':str(witness)},indent=2))

if __name__ == '__main__': main()
