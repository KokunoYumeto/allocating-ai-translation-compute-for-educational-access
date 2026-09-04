"""Prepare only A10-007's 23 manifest-declared source images and retained notice evidence."""
import copy
import csv
import hashlib
import json
from pathlib import PurePosixPath
import xml.etree.ElementTree as ET

from prepare_a10 import BASE, ROOT, CANONICAL, CNXML, MATH, digest, file_hash, jpeg_dimensions, require, tag, tree

MANIFEST = BASE / 'source-excerpts/manifest-a10-007.json'
EXCERPT = BASE / 'source-excerpts/a10-unit-007.cnxml'
TRANSLATION = BASE / 'translations/a10-unit-007.json'
PLAN = BASE / 'plans/A10-007-scope.json'
LANGUAGE_NOTES = BASE / 'qa/a10-unit-007-language-notes.md'
NOTICES = BASE / 'provenance/a10-unit-007-component-notices.json'
MEDIA_MANIFEST = ROOT / 'downloads/extracted/A10/authority/MEDIA_AUTHORITY_MANIFEST.csv'


def logical_lf_hash(path):
    return digest(path.read_bytes().replace(b'\r\n', b'\n'))


def source_alt(media):
    require(media.get('alt') is not None, 'Expected source media alt attribute')
    return media.get('alt')


def load_inputs():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    require((manifest['unit'], manifest['assignment'], manifest['collection'], manifest['module'])
            == ('A10-007', 'A10', 'col31130', 'm82453'), 'Unexpected A10-007 scope')
    lock = json.loads((BASE / 'sources.lock.json').read_text(encoding='utf-8'))
    pin = next(row for row in lock['repositories'] if row['role'] == 'A10+A20 upstream')
    require((manifest['commit'], manifest['tree']) == (pin['commit'], pin['tree']),
            'Manifest does not match the frozen A10 source lock')

    canonical = CANONICAL / 'modules/m82453/index.cnxml'
    require((ROOT / manifest['canonical_local_path']).resolve() == canonical.resolve(),
            'Canonical path changed')
    raw = canonical.read_bytes()
    require((len(raw), digest(raw)) == (manifest['full_module_bytes'], manifest['full_module_sha256']),
            'Canonical hash/size changed')
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()
    require(blob == manifest['canonical_git_blob_sha1'], 'Canonical Git blob changed')
    for witness in manifest['source_byte_witnesses']:
        part = raw[witness['start_byte']:witness['end_byte_exclusive']]
        require((len(part), digest(part)) == (witness['bytes'], witness['sha256']),
                'Canonical section byte witness changed')

    comparison = ROOT / manifest['indonesian_comparison_path']
    require((comparison.stat().st_size, file_hash(comparison))
            == (manifest['indonesian_comparison_bytes'], manifest['indonesian_comparison_sha256']),
            'Pinned Indonesian comparison changed')
    require((EXCERPT.stat().st_size, file_hash(EXCERPT))
            == (manifest['excerpt_bytes'], manifest['excerpt_sha256']), 'Frozen excerpt changed')
    require((TRANSLATION.stat().st_size, file_hash(TRANSLATION))
            == (manifest['translation_bytes'], manifest['translation_sha256']), 'Frozen translation changed')
    require((PLAN.stat().st_size, file_hash(PLAN))
            == (manifest['scope_plan_bytes'], manifest['scope_plan_sha256']), 'Frozen scope plan changed')
    require((LANGUAGE_NOTES.stat().st_size, file_hash(LANGUAGE_NOTES))
            == (manifest['language_notes_bytes'], manifest['language_notes_sha256']), 'Frozen language notes changed')

    source = ET.parse(canonical).getroot()
    excerpt = ET.parse(EXCERPT).getroot()
    content = source.find('{' + CNXML + '}content')
    require(content is not None and len(content) == 8, 'Canonical content extent changed')
    require(content[2].get('id') == manifest['section_start'] == 'fs-id1170654953465'
            and content[3].get('id') == manifest['next_source_id'] == 'fs-id1170654889475',
            'Section boundary changed')
    section = content[2]
    require(len(section) == manifest['section_direct_children_included'] == 31
            and section[-1].get('id') == manifest['scope_through_inclusive'] == 'fs-id1170654936028',
            'Complete section child boundary changed')
    require(len(excerpt) == 1 and excerpt.get('id') == manifest['excerpt_root_id']
            and tree(section) == tree(excerpt[0]), 'Excerpt section differs from canonical source')
    ids = [node.get('id') for node in excerpt.iter() if node is not excerpt and node.get('id')]
    require(ids == manifest['source_ids_in_document_order'] and len(ids) == len(set(ids)) == 111,
            'Source ID sequence changed')
    require(len(list(section.iter())) == 682 and ids[-1] == manifest['last_descendant_id'],
            'Selected source element extent changed')
    counts = {name: sum(tag(node) == name for node in section.iter())
              for name in ('exercise', 'solution', 'math', 'newline', 'image', 'media',
                           'table', 'entry', 'row', 'term', 'span', 'emphasis')}
    require(counts == dict(exercise=9, solution=9, math=21, newline=3, image=23, media=23,
                           table=4, entry=70, row=35, term=3, span=12, emphasis=18),
            'Selected source counts changed')

    require((ROOT / manifest['media_authority_manifest_path']).resolve() == MEDIA_MANIFEST.resolve()
            and file_hash(MEDIA_MANIFEST) == manifest['media_authority_manifest_sha256']
            and MEDIA_MANIFEST.stat().st_size == manifest['media_authority_manifest_bytes'],
            'Media authority manifest changed')
    with MEDIA_MANIFEST.open(encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.DictReader(handle))
    parents = {child: node for node in excerpt.iter() for child in node}
    image_nodes = [node for node in excerpt.iter() if tag(node) == 'image']
    require(len(image_nodes) == len(manifest['images']) == 23, 'Exactly 23 declared images required')
    prepared = []
    for node, spec in zip(image_nodes, manifest['images']):
        media = parents[node]
        require(tag(media) == 'media' and media.get('id') == spec['media_id']
                and spec['figure_id'] is None and spec['local_label'] is None,
                'Unnumbered media ownership changed')
        filename = PurePosixPath(node.get('src')).name
        require(node.get('src') == spec['source_cnxml_src'] == '../../media/' + filename
                and spec['source_path'] == 'media/' + filename, 'Source image path changed')
        original = CANONICAL / 'media' / filename
        require((canonical.parent / node.get('src')).resolve() == original.resolve()
                and (ROOT / spec['canonical_local_path']).resolve() == original.resolve(),
                'Source image escaped its declared canonical path')
        target = BASE / 'assets/a10' / filename
        require(spec['path'] == 'assets/a10/' + filename
                and target.resolve().parent == (BASE / 'assets/a10').resolve(), 'Unsafe asset target')
        require(node.get('mime-type') == spec['source_declared_mime'] == 'image/png'
                and spec['actual_mime'] == 'image/jpeg'
                and spec['actual_image_format'] == 'JPEG', 'Declared/actual MIME contract changed')
        data = original.read_bytes()
        require((len(data), digest(data)) == (spec['bytes'], spec['sha256']), 'Source image bytes changed')
        require(jpeg_dimensions(data) == (spec['width'], spec['height']), 'Source image dimensions changed')
        matches = [(idx, row) for idx, row in enumerate(rows, 2)
                   if row['relative_path'] == spec['source_path']]
        require(len(matches) == 1, 'Missing or duplicate authority row')
        row_index, row = matches[0]
        require(row_index == spec['existing_media_authority_row_number_including_header']
                and row == spec['existing_media_authority_row']
                and row['sha256'] == spec['sha256'] and int(row['bytes']) == len(data),
                'Media authority row changed')
        git_blob = hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()
        require(git_blob == row['git_blob_sha1'] == spec['git_blob_sha1'], 'Image Git blob changed')
        faithful_alt = source_alt(media)
        require(faithful_alt == spec['source_english_alt'], 'Source alt changed')
        prepared.append((spec, original, target, data, row, faithful_alt))
    require(sum(len(data) for _, _, _, data, _, _ in prepared)
            == manifest['total_declared_image_bytes'] == 1603339, 'Image payload total changed')

    expected_notices = {
        'languages/pnb-Arab-PK/provenance/A10-release/NOTICE.txt',
        'languages/pnb-Arab-PK/provenance/upstream--osbooks-prealgebra-bundle/LICENSE'
    }
    require({entry['path'] for entry in manifest['existing_notice_inputs']} == expected_notices,
            'Unexpected notice input')
    notices = []
    for entry in manifest['existing_notice_inputs']:
        path = ROOT / entry['path']
        normalized = path.read_bytes().replace(b'\r\n', b'\n')
        require((len(normalized), digest(normalized))
                == (entry['logical_lf_bytes'], entry['logical_lf_sha256']),
                'Existing notice logical-LF pin changed')
        notices.append(dict(entry))
    return manifest, prepared, notices


def notice_record(manifest, prepared, notices):
    return {
        'schema': 'a10-retained-component-evidence-v1',
        'unit': 'A10-007',
        'work': 'OpenStax Elementary Algebra 2e',
        'module': 'm82453',
        'collection': 'col31130',
        'commit': manifest['commit'],
        'manifest_sha256': file_hash(MANIFEST),
        'excerpt_sha256': manifest['excerpt_sha256'],
        'scope': 'Twenty-three unchanged manifest-declared original JPEGs only; no new supply or license audit.',
        'existing_notice_inputs': notices,
        'existing_notice_hash_policy': manifest['existing_notice_hash_policy'],
        'release_notice_verbatim': (BASE / 'provenance/A10-release/NOTICE.txt').read_text(encoding='utf-8'),
        'existing_license_statement': 'Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International, subject to component-specific credits and restrictions.',
        'rights_status': 'Existing audited A10 policy is retained. No new component-specific clearance determination is made.',
        'credit_limit': 'Authority rows identify exact bytes and Git blobs, not rights holders or permissions. Absence of an image-specific credit is not clearance.',
        'media_authority_manifest': {
            'path': MEDIA_MANIFEST.relative_to(ROOT).as_posix(),
            'sha256': file_hash(MEDIA_MANIFEST)
        },
        'images': [
            {
                'figure_id': None,
                'media_id': spec['media_id'],
                'source_path': spec['source_path'],
                'path': spec['path'],
                'sha256': spec['sha256'],
                'bytes': spec['bytes'],
                'git_blob_sha1': spec['git_blob_sha1'],
                'width': spec['width'],
                'height': spec['height'],
                'source_declared_mime': spec['source_declared_mime'],
                'actual_mime': 'image/jpeg',
                'source_english_alt': faithful_alt,
                'existing_media_authority_row': row,
                'treatment': 'Original JPEG bytes retained unchanged and unmirrored; faithful Punjabi alt trace plus separately declared original accessible overrides only where manifest records a correction.',
                'original_bilingual_key_id': spec['original_bilingual_key_id'],
                'original_accessible_override': spec['source_alt_override'],
                'component_clearance': 'Not newly assessed; subject to retained component-specific credits and restrictions.'
            }
            for spec, original, target, data, row, faithful_alt in prepared
        ],
        'whole_module_translation_complete': False,
        'whole_book_translation_complete': False,
        'whole_assignment_complete': False,
        'scope_boundary': {
            'from': manifest['scope_from'],
            'through': manifest['scope_through_inclusive'],
            'next_required': manifest['next_source_id']
        }
    }


def prepare():
    manifest, prepared, notices = load_inputs()
    for spec, original, target, data, row, faithful_alt in prepared:
        require(not target.exists() or file_hash(target) == spec['sha256'],
                'Refusing to overwrite a different existing image: ' + str(target))
    # Validate every source, destination and retained notice before any output write.
    for spec, original, target, data, row, faithful_alt in prepared:
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_bytes(data)
        require(file_hash(target) == spec['sha256'], 'Copied asset hash mismatch')
    record = notice_record(manifest, prepared, notices)
    NOTICES.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n',
                       encoding='utf-8', newline='\n')
    print('Prepared A10-007:23originalJPEGs,1603339bytes; retained restrictions,no new clearance.')


if __name__ == '__main__':
    prepare()
