"""Freeze acquired translation inputs, not a training dataset. Python 3.10+."""
from pathlib import Path
import copy
import hashlib
import json
import subprocess
import zipfile
import xml.etree.ElementTree as ET

LANG = Path(__file__).resolve().parents[1]
ROOT = LANG.parent
BASE = ROOT / 'downloads/mr-Deva-IN'
PROV = LANG / 'provenance'

REPOS = {
    'catalog': ('program-catalog', '2f0e52280791854f904475e5f92392f52745ea24'),
    'A20-id': ('indonesian/A20', 'b293e167477c8fe2e8885c6f6d79d12cbb2e0e89'),
    'A30-id': ('indonesian/A30', '3209a5a2dea18c2fc527c5ea41b7dd2195076e40'),
    'B10-id': ('indonesian/B10', 'e94905932301e699b7c4d44e88ec54e972b886b6'),
    'B20-id': ('indonesian/B20', '59aaa2a6145eecd67680752c28ad4be7e43eff5e'),
    'B40-id': ('indonesian/B40', 'e84ce2956a7304830c42eba70106f940fefee7c4'),
    'B10-en': ('upstream/B10', '82336dc87d77c3f18d2cdbc8ec1e74eb3ba38799'),
    'B20-en': ('upstream/B20', '9f0295936d395bec68dab7915057135a2c7f0414'),
    'B40-en': ('upstream/B40', 'df2262e089a02651c127f1dd12649c4622ee1383'),
}
ARCHIVES = [
    ('A20-id-old', 'A20-source.zip', 'https://github.com/KokunoYumeto/openstax-intermediate-algebra-2e-id/releases/download/v0.1.3-wip/openstax-intermediate-algebra-2e-id-ID-0.1.3-wip-source.zip', '993925e704368e1817d85b7f46d151b538285a2baeb466b459be0eda95e4fff5'),
    ('A20-id', 'A20-v0.3.0-source.zip', 'https://github.com/KokunoYumeto/openstax-intermediate-algebra-2e-id/releases/download/v0.3.0-wip/openstax-intermediate-algebra-2e-id-ID-0.3.0-wip-editable-source.zip', 'a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7'),
    ('A30-id', 'A30-source.zip', 'https://github.com/KokunoYumeto/openstax-precalculus-2e-id/releases/download/v0.1.0-alpha.58-reader.1/precalculus-2e-id-ID-0.1.0-alpha.58-reader.1-source-core.zip', '9f8ba5e44bd4d4794c559de85a5449f3b4bd279d153801b94f3d39a471f5a0ca'),
    ('A20-en', 'A20-canonical.zip', 'https://codeload.github.com/openstax/osbooks-prealgebra-bundle/zip/38cae454e644abf9f0a623e876994553881597c9', None),
    ('A30-en', 'A30-canonical.zip', 'https://codeload.github.com/openstax/osbooks-college-algebra-bundle/zip/789b54099106b071d1d32bfcee454fed72eb4768', '2fdf5495f5f11dbe3c8f6d4705a257a2ed7f13db1968cc6b2be409e0202a94f9'),
]

def digest(data):
    return hashlib.sha256(data).hexdigest()

def file_digest(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()

def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], text=True).strip()

def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')

def witness(relative, data, source):
    destination = PROV / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    return {'path': destination.relative_to(LANG).as_posix(), 'sha256': digest(data), 'bytes': len(data), 'source': source}

def main():
    lock = {'schema': 1, 'locale': 'mr-Deva-IN', 'acquired_date': '2026-08-30', 'purpose': 'translation inputs only; not training/fine-tuning data', 'repositories': [], 'archives': [], 'witnesses': [], 'source_selections': []}
    for key, (relative, pin) in REPOS.items():
        path = BASE / relative
        head = git(path, 'rev-parse', 'HEAD')
        assert head == pin, (key, head, pin)
        tracked = git(path, 'ls-files').splitlines()
        materialized = [p for p in tracked if (path / p).is_file()]
        entry = {'id': key, 'path': path.relative_to(ROOT).as_posix(), 'url': git(path, 'remote', 'get-url', 'origin'), 'commit': head, 'tree': git(path, 'rev-parse', 'HEAD^{tree}'), 'shallow': git(path, 'rev-parse', '--is-shallow-repository') == 'true', 'tracked_files': len(tracked), 'materialized_files': len(materialized)}
        if key == 'B40-id':
            entry['scope'] = 'filtered sparse checkout: root notices plus source, 00_control, publication, qa, tools, backend; generated docs/ excluded'
        else:
            assert len(tracked) == len(materialized), key
            entry['scope'] = 'full shallow checkout'
        lock['repositories'].append(entry)
        notices = [p for p in materialized if '/' not in p and (p.upper().startswith(('LICENSE', 'NOTICE', 'THIRD_PARTY', 'ATTRIBUTION', 'ACKNOWLEDG')))]
        for name in ['README.md', *notices]:
            if (path / name).is_file():
                # git blob bytes preserve originals rather than checkout newline conversion.
                data = subprocess.check_output(['git', '-C', str(path), 'show', f'HEAD:{name}'])
                lock['witnesses'].append(witness(f'notices/{key}/{name}', data, f'{key}@{pin}:{name}'))
    for key, filename, url, expected in ARCHIVES:
        path = BASE / 'releases' / filename
        actual = file_digest(path)
        if expected:
            assert actual == expected, (filename, actual, expected)
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None, filename
            names = archive.namelist()
            info = {'id': key, 'path': path.relative_to(ROOT).as_posix(), 'url': url, 'bytes': path.stat().st_size, 'sha256': actual, 'published_sha256': expected, 'verification': 'sha256_and_full_zip_crc_pass' if expected else 'observed_sha256_and_full_zip_crc_pass', 'entries': len(names), 'uncompressed_bytes': sum(i.file_size for i in archive.infolist())}
            if key.endswith('-en'):
                info['commit'] = url.rsplit('/', 1)[-1]
                prefix = names[0].split('/')[0] + '/'
                for name in names:
                    local = name[len(prefix):]
                    if local in ('LICENSE', 'README.md') or local.startswith('collections/') and local.endswith('.xml') and ('intermediate-algebra-2e' in local or 'precalculus-2e' in local):
                        lock['witnesses'].append(witness(f'notices/{key}/{local}', archive.read(name), f'{key}:{name}'))
            if key == 'A20-id':
                for name in ['LICENSE.txt', 'README.md', 'manifests/source-checkpoint-0030.json']:
                    lock['witnesses'].append(witness(f'A20-v0.3.0/{name}', archive.read(name), f'{filename}:{name}'))
            lock['archives'].append(info)
    # Preserve catalogs/release notices without reevaluating their binding audits.
    copies = [(BASE/'program-catalog/backend/authority/curriculum-authority-v1.json', 'catalog-authority.json')]
    for course in ('A20', 'A30'):
        for name in ('RELEASE_MANIFEST.json', 'SHA256SUMS.txt'):
            copies.append((BASE/f'indonesian/{course}/{name}', f'{course}-index-{name}'))
    for version in ('0.2.0', '0.3.0'):
        for suffix in ('manifest.json', 'SHA256SUMS.txt'):
            copies.append((BASE/f'releases/A20-v{version}-{suffix}', f'A20-v{version}-{suffix}'))
    for source, dest in copies:
        lock['witnesses'].append(witness(dest, source.read_bytes(), source.relative_to(ROOT).as_posix()))
    # Freeze the exact canonical and Indonesian blocks referenced by this pilot.
    pilot = ET.parse(LANG/'translations/MR-BRIDGE-001.xml').getroot()
    selections = ET.Element('translation-source-selections', {'purpose': 'human-reviewable translation provenance, not a training dataset'})
    for block in pilot.iter():
        locator = block.get('data-source')
        if not locator:
            continue
        course, rest = locator.split(':')
        module, source_id = rest.split('#')
        selected = ET.SubElement(selections, 'selection', {'locator': locator})
        record = {'locator': locator, 'target_id': block.get('id'), 'sources': []}
        for locale in ('en', 'id'):
            filename = f'{course}-canonical.zip' if locale == 'en' else ('A20-v0.3.0-source.zip' if course == 'A20' else 'A30-source.zip')
            with zipfile.ZipFile(BASE/'releases'/filename) as archive:
                candidates = [n for n in archive.namelist() if n.endswith(f'/modules/{module}/index.cnxml')]
                if locale == 'id' and course == 'A30':
                    candidates = [n for n in candidates if n.startswith('repo/source/')]
                assert len(candidates) == 1, (filename, candidates)
                raw = archive.read(candidates[0])
                tree = ET.fromstring(raw)
                found = [e for e in tree.iter() if e.get('id') == source_id]
                assert len(found) == 1, (locator, locale)
                fragment = ET.tostring(found[0], encoding='utf-8')
                branch = ET.SubElement(selected, 'source', {'locale': locale, 'module-sha256': digest(raw), 'fragment-sha256': digest(fragment)})
                branch.append(copy.deepcopy(found[0]))
                math_nodes = [e for e in found[0].iter() if e.tag == '{http://www.w3.org/1998/Math/MathML}math']
                record['sources'].append({'locale': locale, 'archive': filename, 'member': candidates[0], 'module_sha256': digest(raw), 'fragment_sha256': digest(fragment), 'math_count': len(math_nodes), 'math_sha256': [digest(ET.tostring(e, encoding='utf-8')) for e in math_nodes]})
        lock['source_selections'].append(record)
    ET.indent(selections)
    fragment_bytes = ET.tostring(selections, encoding='utf-8', xml_declaration=True)
    lock['witnesses'].append(witness('selected-source-blocks.xml', fragment_bytes, 'exact source-ID selection from pinned canonical and Indonesian archives'))
    lock['failures_and_resolution'] = [
        'A20/A30 full Git fetch interrupted; complete exact-commit ZIPs acquired instead.',
        'B40 Indonesian full shallow clone interrupted; pinned filtered/sparse source checkout acquired.',
        'A20 v0.2.0 ZIP transfer failed; metadata retained; superseded by verified v0.3.0 ZIP. Failed/empty v0.2.0 is not counted as acquired.',
        'GitHub anonymous REST rate limit encountered; exact-tag release download URLs used.'
    ]
    save_json(LANG/'sources.lock.json', lock)
    print(json.dumps({'repositories': len(lock['repositories']), 'verified_archives': len(lock['archives']), 'selected_blocks': len(lock['source_selections']), 'archive_bytes': sum(a['bytes'] for a in lock['archives'])}, indent=2))

if __name__ == '__main__':
    main()
