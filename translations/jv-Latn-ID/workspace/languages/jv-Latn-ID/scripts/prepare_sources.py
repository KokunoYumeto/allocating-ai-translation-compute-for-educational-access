"""Acquire/replay frozen translation inputs; never upload or construct training data.

Generated files are source witnesses, XML excerpts, notices, and provenance only.
Run --acquire on a fresh checkout; existing corpora must match the frozen pins.
"""
import argparse
import csv
import hashlib
import io
import json
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from config import LANG, ROOT, DOWNLOADS, REPOSITORIES, A10_ZIP_URL, A10_ZIP_SHA, UNITS
from safe_io import write_bytes


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(DOWNLOADS / repo), *args])


def blob(repo, path):
    return git(repo, 'show', f'HEAD:{path}')


def write(path, data):
    write_bytes(path, data)


def full_archive_origin(downloaded_now, previous_assets, local_path, digest):
    """Describe this run without mistaking a prior PC's hard link for this file."""
    if downloaded_now:
        return {'acquisition': 'Downloaded from the pinned canonical URL during this acquisition; no shared-origin or hard-link claim.'}
    record = {'acquisition': 'Reused an existing repo-relative archive and verified its bytes during this run; current storage topology is not inferred.'}
    prior = [asset for asset in previous_assets
             if asset.get('local_path') == local_path and asset.get('sha256') == digest]
    if len(prior) > 1:
        raise ValueError('Ambiguous previous archive acquisition evidence')
    if prior:
        historical = prior[0].get('historical_acquisition')
        if historical is None and prior[0].get('shared_origin_at_acquisition'):
            historical = {key: prior[0][key] for key in ('acquisition', 'shared_origin_at_acquisition')}
        if historical:
            record['historical_acquisition'] = dict(historical)
            record['historical_acquisition_note'] = 'Retained prior lock evidence only; not a path dependency or a claim about the current PC.'
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--acquire', action='store_true')
    args = parser.parse_args()
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    previous_lock = LANG / 'sources.lock.json'
    previous_assets = json.loads(previous_lock.read_text(encoding='utf-8')).get('assets', []) if previous_lock.exists() else []
    lock = {'schema': 'jv-translation-input-lock-v1', 'purpose': 'translation_inputs_only_not_training_or_fine_tuning', 'acquired_date': '2026-08-30', 'repositories': [], 'assets': [], 'files': [], 'units': UNITS}
    for name, url, commit, role in REPOSITORIES:
        dest = DOWNLOADS / name
        if args.acquire and not dest.exists():
            subprocess.run(['git', 'init', str(dest)], check=True)
            subprocess.run(['git', '-C', str(dest), 'remote', 'add', 'origin', url], check=True)
            fetch = ['git', '-C', str(dest), 'fetch', '--depth', '1']
            if name == 'openstax-prealgebra-bundle':
                subprocess.run(['git', '-C', str(dest), 'config', 'remote.origin.promisor', 'true'], check=True)
                subprocess.run(['git', '-C', str(dest), 'config', 'remote.origin.partialclonefilter', 'blob:none'], check=True)
                fetch += ['--filter=blob:none']
                subprocess.run(['git', '-C', str(dest), 'sparse-checkout', 'init', '--cone'], check=True)
                subprocess.run(['git', '-C', str(dest), 'sparse-checkout', 'set', 'modules', 'collections'], check=True)
            subprocess.run(fetch + ['origin', commit], check=True)
            subprocess.run(['git', '-C', str(dest), 'checkout', '--detach', 'FETCH_HEAD'], check=True)
        actual = git(name, 'rev-parse', 'HEAD').decode().strip()
        if actual != commit:
            raise ValueError(f'{name}: expected frozen {commit}; got {actual}; refusing overwrite')
        lock['repositories'].append({'name': name, 'url': url, 'commit': actual, 'tree': git(name, 'rev-parse', 'HEAD^{tree}').decode().strip(), 'role': role, 'local_path': dest.relative_to(ROOT).as_posix(), 'shallow': git(name, 'rev-parse', '--is-shallow-repository').decode().strip() == 'true', 'tracked_file_count': len(git(name, 'ls-tree', '-r', '--name-only', 'HEAD').splitlines()), 'checkout_scope': 'modules, collections and root notices; unrelated media not materialized' if name == 'openstax-prealgebra-bundle' else 'complete shallow repository checkout'})

    archive = DOWNLOADS / 'a10-source.zip'
    if args.acquire and not archive.exists():
        urllib.request.urlretrieve(A10_ZIP_URL, archive)
    data = archive.read_bytes()
    assert len(data) == 6397865 and sha(data) == A10_ZIP_SHA, 'A10 source archive checksum mismatch'
    lock['assets'].append({'url': A10_ZIP_URL, 'release': 'v1.0.2', 'bytes': len(data), 'sha256': sha(data), 'local_path': archive.relative_to(ROOT).as_posix(), 'checksum_authority': 'GitHub release asset digest SHA-256 (also bound by the release SHA256SUMS file)'})
    z = zipfile.ZipFile(io.BytesIO(data))
    manifest = json.loads(z.read('MANIFEST.json'))
    for entry in manifest['entries']:
        raw = z.read(entry['path'])
        assert len(raw) == entry['bytes'] and sha(raw) == entry['sha256'], entry['path']
    lock['a10_release_manifest_entries_verified'] = len(manifest['entries'])
    # Safely materialize the entire assigned A10 source package for continued work.
    extracted = DOWNLOADS / 'a10-source'
    for entry in z.infolist():
        target = (extracted / entry.filename).resolve()
        if not target.is_relative_to(extracted.resolve()):
            raise ValueError(f'unsafe archive member {entry.filename}')
        if not entry.is_dir():
            write(target, z.read(entry))

    def preserve(repo, path, output):
        raw = blob(repo, path)
        write(LANG / output, raw)
        lock['files'].append({'repository': repo, 'path': path, 'retained_at': output, 'sha256': sha(raw), 'bytes': len(raw), 'hash_basis': 'git blob; independent of checkout CRLF conversion'})

    for repo, path, output in [
        ('a00-id', 'LICENSE', 'provenance/A00-LICENSE.txt'),
        ('a00-id', 'README.md', 'provenance/A00-README.md'),
        ('a00-id', 'provenance/UPSTREAM_README.md', 'provenance/UPSTREAM_README.md'),
        ('a00-id', 'modules/m81241/index.cnxml', 'provenance/A00-preface-credits.id.cnxml'),
        ('a00-id', 'provenance/logbook/authority/prealgebra2e/prealgebra2e-source-manifest.tsv', 'provenance/A00-source-manifest.tsv'),
        ('a10-id', 'SOURCE_AUTHORITY.md', 'provenance/A10-SOURCE_AUTHORITY.md'),
        ('a10-id', 'MODEL_PROVENANCE.md', 'provenance/A10-MODEL_PROVENANCE.md'),
        ('a10-id', 'PUBLICATION.json', 'provenance/A10-PUBLICATION.json'),
        ('openstax-prealgebra-bundle', 'LICENSE', 'provenance/UPSTREAM-LICENSE.txt'),
        ('access-dossier', 'LICENSE', 'provenance/AX2-LICENSE.txt'),
        ('access-dossier', 'THIRD_PARTY_NOTICES.md', 'provenance/AX2-THIRD_PARTY_NOTICES.md'),
        ('catalog', 'backend/v2.1/planning/educational-access/authority_snapshot.json', 'provenance/AX2-authority-snapshot.json'),
    ]:
        preserve(repo, path, output)
    for path in ['NOTICE.txt', 'LICENSE.txt', 'authority/SOURCE_AUTHORITY_MANIFEST.csv', 'translated/modules/m82630/index.cnxml']:
        raw = z.read(path)
        dest = 'provenance/A10-preface-credits.id.cnxml' if path.endswith('m82630/index.cnxml') else 'provenance/A10-' + path.split('/')[-1]
        write(LANG / dest, raw)
        lock['files'].append({'archive': 'a10-source.zip', 'path': path, 'retained_at': dest, 'sha256': sha(raw), 'bytes': len(raw)})

    snapshot = json.loads(blob('catalog', 'backend/v2.1/planning/educational-access/authority_snapshot.json'))
    # Only assigned AX-2 specifications, not a fresh examination of the audit.
    for path in ['curriculum_portfolios.csv', 'accessibility_derivatives.csv']:
        raw = blob('access-dossier', path)
        expected = next(x for x in snapshot['source_file_facts'] if x['name'] == path)
        assert sha(raw) == expected['sha256'] and len(raw) == expected['bytes'], path
        preserve('access-dossier', path, f'provenance/AX2-{path}')
    lock['ax2_resolution'] = {'owner': 'access-dossier', 'portfolio_id': 'AX-2', 'derivative_id': 'AX-AUDIO', 'catalog_hashes_match_dossier': True, 'independent_repository': False, 'note': 'AX-2 is a cross-project specification in the catalog/dossier, not a separate book repository; no unrelated B10/OpenLogic corpus is assigned.'}

    # Verify every A00 canonical source module against the inherited frozen manifest.
    rows = list(csv.DictReader(io.StringIO(blob('a00-id', 'provenance/logbook/authority/prealgebra2e/prealgebra2e-source-manifest.tsv').decode()), delimiter='\t'))
    for row in rows:
        raw = blob('openstax-prealgebra-bundle', f"modules/{row['module']}/index.cnxml")
        assert sha(raw) == row['sha256'] and len(raw) == int(row['bytes']), row['module']
    lock['a00_canonical_modules_verified'] = len(rows)
    a10_paths = [p for p in z.namelist() if p.startswith('authority/source/modules/') and p.endswith('/index.cnxml')]
    for path in a10_paths:
        raw = blob('openstax-prealgebra-bundle', path.removeprefix('authority/source/'))
        assert raw == z.read(path), path
    lock['a10_canonical_modules_verified'] = len(a10_paths)

    ET.register_namespace('', 'http://cnx.rice.edu/cnxml')
    ET.register_namespace('m', 'http://www.w3.org/1998/Math/MathML')
    for unit in UNITS:
        raw = blob('a00-id', unit['source']) if unit['program'] == 'A00' else z.read(unit['source'])
        upstream = blob('openstax-prealgebra-bundle', f"modules/{unit['module']}/index.cnxml")
        unit['indonesian_module_sha256'] = sha(raw)
        unit['upstream_module_sha256'] = sha(upstream)
        doc = ET.fromstring(raw)
        section = next(x for x in doc.iter() if x.get('id') == unit['section'])
        if unit['children'] is not None:
            section[:] = list(section)[:unit['children']]
        section.tail = None
        out = ET.tostring(section, encoding='utf-8', xml_declaration=True)
        path = f"translation/{unit['key']}.id-academic.cnxml"
        write(LANG / path, out)
        unit['indonesian_excerpt_sha256'] = sha(out)
        unit['excerpt_path'] = path
        # Preserve a matching English source excerpt for source-vs-pivot QA.
        doc = ET.fromstring(upstream)
        section = next(x for x in doc.iter() if x.get('id') == unit['section'])
        if unit['children'] is not None:
            section[:] = list(section)[:unit['children']]
        section.tail = None
        write(LANG / f"provenance/{unit['key']}.en.cnxml", ET.tostring(section, encoding='utf-8', xml_declaration=True))
    preserve('a00-id', 'media/CNX_BMath_Figure_01_01_001.jpg.id-ID.svg', 'translation/number-line.id-ID.svg')
    image_path = 'media/CNX_BMath_Figure_01_01_001.jpg'
    image = blob('openstax-prealgebra-bundle', image_path)
    write(DOWNLOADS / 'canonical-pilot-media' / 'CNX_BMath_Figure_01_01_001.jpg', image)
    lock['assets'].append({'repository': 'openstax-prealgebra-bundle', 'path': image_path, 'sha256': sha(image), 'bytes': len(image), 'local_path': 'downloads/jv-Latn-ID/canonical-pilot-media/CNX_BMath_Figure_01_01_001.jpg', 'role': 'Canonical original number-line image; reader uses the Indonesian edition SVG with translated labels.'})
    checksum_url = A10_ZIP_URL.rsplit('/', 1)[0] + '/SHA256SUMS.txt'
    checksum_path = DOWNLOADS / 'A10-release-SHA256SUMS.txt'
    if not checksum_path.exists():
        urllib.request.urlretrieve(checksum_url, checksum_path)
    checksums = checksum_path.read_bytes()
    assert sha(checksums) == '5f4abce9a019ea01dd5fb5fa0f4aa61e478cc1699c166fa28dd1596bbe510d8d'
    assert A10_ZIP_SHA in checksums.decode() and A10_ZIP_URL.rsplit('/', 1)[-1] in checksums.decode()
    write(LANG / 'provenance/A10-release-SHA256SUMS.txt', checksums)
    lock['assets'].append({'url': checksum_url, 'sha256': sha(checksums), 'bytes': len(checksums), 'retained_at': 'provenance/A10-release-SHA256SUMS.txt'})
    full_archive = DOWNLOADS / 'openstax-full-pinned.zip'
    full_url = 'https://codeload.github.com/openstax/osbooks-prealgebra-bundle/zip/38cae454e644abf9f0a623e876994553881597c9'
    downloaded_full_archive = False
    if args.acquire and not full_archive.exists():
        urllib.request.urlretrieve(full_url, full_archive)
        downloaded_full_archive = True
    # The existing NTFS hard link is consumed read-only. Never overwrite it.
    assert full_archive.stat().st_size == 537455794
    with full_archive.open('rb') as stream:
        full_sha = hashlib.file_digest(stream, 'sha256').hexdigest()
    assert full_sha == 'effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917'
    with zipfile.ZipFile(full_archive) as full:
        assert full.testzip() is None, 'Full canonical archive CRC failure'
        prefix = 'osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/'
        assert all(p.startswith(prefix) for p in full.namelist())
        for row in rows:
            assert sha(full.read(prefix + f"modules/{row['module']}/index.cnxml")) == row['sha256']
        for path in a10_paths:
            assert full.read(prefix + path.removeprefix('authority/source/')) == z.read(path)
        full_count = len(full.infolist())
    full_local_path = full_archive.relative_to(ROOT).as_posix()
    lock['assets'].append({'url': full_url, 'sha256': full_sha, 'bytes': 537455794, 'archive_entries': full_count, 'crc_all_entries': 'pass', 'local_path': full_local_path, 'coverage': 'Complete pinned upstream archive including media; separate from sparse Git checkout', **full_archive_origin(downloaded_full_archive, previous_assets, full_local_path, full_sha)})
    write(LANG / 'sources.lock.json', (json.dumps(lock, ensure_ascii=False, indent=2) + '\n').encode())
    print(f"Pinned {len(REPOSITORIES)} repositories; verified {len(rows)} A00 / {len(a10_paths)} A10 canonical modules and {len(manifest['entries'])} release entries.")


if __name__ == '__main__':
    main()
