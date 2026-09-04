"""Retain the two source-bound A10 equality/inequality number-line JPEGs.

No network calls, image redraws, source-archive writes, or shared-file edits.
--check reconstructs the small products in memory and compares existing bytes.
The full archive is consumed read-only; only its two selected entries are read.
"""
import argparse
import csv
import hashlib
import io
import json
import os
import subprocess
import xml.etree.ElementTree as ET
import zipfile

from config import DOWNLOADS, LANG, UPSTREAM_COMMIT, A10_ZIP_SHA
from safe_io import write_bytes

UNIT = 'a10-equality-symbols'
MODULE = 'm82453'
SECTION = 'fs-id1170655150800'
NOTE = 'fs-id1170655207857'
OUT = f'translation/assets/{UNIT}/'
MANIFEST = f'translation/{UNIT}.assets.json'
TRACKS = ('id-academic', 'jv-academic', 'jv-conversation')
SOURCES = [
    {'filename': 'CNX_ElemAlg_Figure_01_02_001_img_new.jpg', 'media_id': 'fs-id1170652623871',
     'bytes': 14959, 'sha256': '5bd5be8d8057f98b4b6acf06f64445d6806ef7265117cd1f5106d1140bbe25da',
     'git_blob_sha1': '62201bcb6f45e97930f3093ee90ac0f0f3d7bd15'},
    {'filename': 'CNX_ElemAlg_Figure_01_02_002_img_new.jpg', 'media_id': 'fs-id1167269961954',
     'bytes': 15798, 'sha256': '0e2f32f4998d214b4dc06b124d9830ed9fe624be30a94e2c29259ac70fb8fb9f',
     'git_blob_sha1': 'd0dd558a8770e9c5142e04a0312f39bfc7b05c6d'},
]
# Directly inspected on 2026-08-31; exact hashes above bind these observations.
INSPECTIONS = {
    'CNX_ElemAlg_Figure_01_02_001_img_new.jpg': 'A horizontal black number line with arrowheads at both ends and two vertical ticks. Italic a is below the left tick and italic b below the right tick. No prose, numeric labels, or printed inequality operator occurs; a and b are mathematical identifiers.',
    'CNX_ElemAlg_Figure_01_02_002_img_new.jpg': 'A horizontal black number line with arrowheads at both ends and two vertical ticks. Italic b is below the left tick and italic a below the right tick. No prose, numeric labels, or printed inequality operator occurs; a and b are mathematical identifiers.',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def blob_sha(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def pinned_oid(path):
    env = dict(os.environ, GIT_NO_LAZY_FETCH='1', GIT_TERMINAL_PROMPT='0', GIT_OPTIONAL_LOCKS='0')
    return subprocess.check_output(
        ['git', '--no-optional-locks', '-C', str(DOWNLOADS / 'openstax-prealgebra-bundle'),
         'rev-parse', UPSTREAM_COMMIT + ':' + path], env=env).decode('ascii').strip()


def dimensions(raw):
    """Read JPEG SOF dimensions without decoding or rewriting the bitmap."""
    require(raw[:2] == b'\xff\xd8', 'Expected an original JPEG')
    position = 2
    frames = {0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf}
    while position < len(raw):
        require(raw[position] == 0xff, 'Unexpected JPEG header')
        while raw[position] == 0xff:
            position += 1
        marker = raw[position]
        position += 1
        require(marker not in (0xda, 0xd9), 'JPEG frame header missing')
        if marker == 0x01 or 0xd0 <= marker <= 0xd8:
            continue
        length = int.from_bytes(raw[position:position + 2], 'big')
        require(length >= 2 and position + length <= len(raw), 'Invalid JPEG segment length')
        if marker in frames:
            require(length >= 8, 'Invalid JPEG frame header')
            return {'width': int.from_bytes(raw[position + 5:position + 7], 'big'),
                    'height': int.from_bytes(raw[position + 3:position + 5], 'big')}
        position += length
    raise ValueError('JPEG frame dimensions unavailable')


def media_references(raw):
    document = ET.fromstring(raw)
    section = next(node for node in document.iter() if node.get('id') == SECTION)
    note = next(node for node in section.iter() if node.get('id') == NOTE)
    return [(node.get('id'), child.get('src'), child.get('mime-type'))
            for node in note.iter() if node.tag.endswith('}media')
            for child in node if child.tag.endswith('}image')]


def products():
    require(set(INSPECTIONS) == {record['filename'] for record in SOURCES},
            'Both source images require a recorded direct inspection')
    lock = json.loads((LANG / 'sources.lock.json').read_bytes())
    source_archive = DOWNLOADS / 'a10-source.zip'
    with source_archive.open('rb') as stream:
        require(hashlib.file_digest(stream, 'sha256').hexdigest() == A10_ZIP_SHA,
                'A10 release source archive checksum differs')
    full_record = next(record for record in lock['assets'] if record.get('local_path', '').endswith('/openstax-full-pinned.zip'))
    full_path = DOWNLOADS / 'openstax-full-pinned.zip'
    require(full_path.stat().st_size == full_record['bytes'], 'Pinned canonical archive size differs')
    witness = next(unit for unit in lock['units'] if unit['program'] == 'A10' and unit['module'] == MODULE)
    with zipfile.ZipFile(source_archive) as release:
        release_manifest = json.loads(release.read('MANIFEST.json'))
        release_entries = {entry['path']: entry for entry in release_manifest['entries']}

        def release_file(path):
            raw = release.read(path)
            expected = release_entries[path]
            require(sha(raw) == expected['sha256'] and len(raw) == expected['bytes'],
                    'Changed A10 release member: ' + path)
            return raw

        media_manifest = release_file('authority/MEDIA_AUTHORITY_MANIFEST.csv')
        rows = {row['relative_path']: row for row in csv.DictReader(io.StringIO(media_manifest.decode('utf-8-sig')))}
        indonesian = release_file(f'translated/modules/{MODULE}/index.cnxml')
        english = release_file(f'authority/source/modules/{MODULE}/index.cnxml')
        require(sha(indonesian) == witness['indonesian_module_sha256'], 'Indonesian module pin differs')
        require(sha(english) == witness['upstream_module_sha256'], 'Canonical module pin differs')
        require(blob_sha(english) == pinned_oid(f'modules/{MODULE}/index.cnxml'), 'Canonical module Git witness differs')
        expected_refs = [(record['media_id'], '../../media/' + record['filename'], 'image/jpeg') for record in SOURCES]
        require(media_references(indonesian) == expected_refs and media_references(english) == expected_refs,
                'Inequality-note media scope or source order differs')
        require(all('media/' + record['filename'] not in release.namelist() for record in SOURCES),
                'A10 source-package media availability changed; reconcile acquisition metadata')

    report = {
        'schema': 'jv-equality-assets-1', 'program': 'A10', 'module': MODULE, 'section_id': SECTION,
        'source_note_id': NOTE,
        'scope': 'Both number-line media references in the selected equality/inequality note only; not the complete module or book.',
        'source_hash_basis': 'Exact release witness and canonical ZIP member bytes, checked against pinned Git blob identities.',
        'indonesian_repository': 'https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id',
        'indonesian_release': 'v1.0.2', 'indonesian_release_sha256': A10_ZIP_SHA,
        'indonesian_module_sha256': sha(indonesian), 'indonesian_module_blob_sha1': blob_sha(indonesian),
        'canonical_repository': 'https://github.com/openstax/osbooks-prealgebra-bundle',
        'canonical_commit': UPSTREAM_COMMIT, 'canonical_module_sha256': sha(english),
        'canonical_module_blob_sha1': blob_sha(english),
        'media_authority_manifest_sha256': sha(media_manifest),
        'canonical_archive': {'path': full_record['local_path'], 'acquisition_sha256': full_record['sha256'],
                              'verification_this_run': 'Archive size plus the two selected member CRCs, byte counts, SHA-256 and pinned Git blob identities; full archive hash is inherited acquisition evidence, not recomputed here.'},
        'credit': 'Rice University/OpenStax, CC BY-NC-SA 4.0, subject to retained source and component notices. These are exact source JPEGs, not new illustrations or a claim of endorsement. Full original notices remain controlling.',
        'consultations': [
            {'source': 'downloads/jv-Latn-ID/canon/kiwa.txt', 'stage': 'asset source-reading and left/right review',
             'decision': 'Read actual C09 entry: use the left-direction sense. Preserve the source point order; image labels themselves are mathematical identifiers, not words to translate.'},
            {'source': 'downloads/jv-Latn-ID/canon/tengen.txt', 'stage': 'asset source-reading and left/right review',
             'decision': 'Read actual C10 entry: tengen is right; distinguish the sleep-related tengèn homograph. Per-register descriptions stay in the translated CNXML, not embedded into these source bitmaps.'},
        ],
        'register_decisions': {
            'shared_label_policy': 'Retain mathematical a/b identifiers and the exact line, ticks, arrows, spacing and colours. The same non-linguistic bytes serve all three tracks; no synthetic language-specific image is introduced.',
            'alt_text_policy': 'Each CNXML track supplies its own translated alt description. This asset manifest does not replace the source-bound narration or claim native-language approval.',
        },
        'qa': {'source_images_inspected': '2026-08-31: both exact source JPEGs inspected using local image viewing; recorded observations are source-hash-bound.',
               'preservation': 'All output image bytes are identical to the pinned canonical source; geometry and mathematical labels therefore remain unchanged.',
               'reader_integration': 'pending_separate_unit_build', 'native_language_review': 'pending',
               'screen_reader_and_listening_review': 'pending'},
        'assets': [],
    }
    generated = {}
    prefix = f'osbooks-prealgebra-bundle-{UPSTREAM_COMMIT}/'
    with zipfile.ZipFile(full_path) as archive:
        for record in SOURCES:
            name = record['filename']
            path = 'media/' + name
            row = rows[path]
            require(int(row['bytes']) == record['bytes'] and row['sha256'] == record['sha256'] and
                    row['git_blob_sha1'] == record['git_blob_sha1'], 'A10 media authority differs: ' + name)
            require(pinned_oid(path) == record['git_blob_sha1'], 'Canonical image Git identity differs: ' + name)
            require(sum(info.filename == prefix + path for info in archive.infolist()) == 1,
                    'Canonical image archive entry is missing or duplicated: ' + name)
            raw = archive.read(prefix + path)  # ZIP CRC is checked by the standard library.
            require(len(raw) == record['bytes'] and sha(raw) == record['sha256'] and
                    blob_sha(raw) == record['git_blob_sha1'], 'Canonical image bytes differ: ' + name)
            output = OUT + name
            generated[output] = raw
            common = {'path': path, 'sha256': sha(raw), 'bytes': len(raw),
                      'git_blob_sha1': blob_sha(raw), 'locale': 'zxx'}
            entry = {
                'source_src': '../../' + path, 'media_id': record['media_id'], 'figure_id': None,
                'mime_type': 'image/jpeg', 'dimensions_pixels': dimensions(raw),
                'indonesian_source': {**common, 'availability': 'A10 release media-authority reference; JPEG not packaged in that source ZIP'},
                'canonical_original': {**common, 'archive_member': prefix + path,
                                       'contains_linguistic_text': False},
                'visual_inspection': INSPECTIONS[name],
                'outputs': {},
            }
            for track in TRACKS:
                entry['outputs'][track] = {'path': output, 'sha256': sha(raw), 'bytes': len(raw),
                                          'locale': 'zxx', 'contains_linguistic_text': False,
                                          'contains_untranslated_linguistic_text': False,
                                          'derivative_type': 'source-byte-retention'}
            report['assets'].append(entry)
    report['qa']['unique_output_files'] = len(generated)
    report['qa']['unique_output_bytes'] = sum(len(raw) for raw in generated.values())
    generated[MANIFEST] = (json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode()
    require(sum(map(len, generated.values())) < 100_000, 'Asset output exceeded bounded allowance')
    return generated


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    generated = products()
    require(generated == products(), 'Equality asset generation is not deterministic')
    for path, raw in generated.items():
        if args.check:
            require((LANG / path).read_bytes() == raw, 'Stale equality asset: ' + path)
        else:
            write_bytes(LANG / path, raw)
    print('Equality assets: 2 source references, 2 exact JPEG files, 3 track mappings; byte/geometry preservation verified.')


if __name__ == '__main__':
    main()
