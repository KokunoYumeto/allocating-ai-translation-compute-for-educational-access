"""Prepare only the fifteen manifest-declared A10-004 original JPEGs."""
from pathlib import PurePosixPath
import csv
import hashlib
import json
import xml.etree.ElementTree as ET
from prepare_a10 import BASE, ROOT, CANONICAL, CNXML, MATH, digest, file_hash, jpeg_dimensions, require, tag, tree

MANIFEST = BASE / 'source-excerpts/manifest-a10-004.json'
NOTICES = BASE / 'provenance/a10-unit-004-component-notices.json'
MEDIA_MANIFEST = ROOT / 'downloads/extracted/A10/authority/MEDIA_AUTHORITY_MANIFEST.csv'


def load_inputs():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    require((manifest['unit'], manifest['assignment'], manifest['collection'], manifest['module'])
            == ('A10-004', 'A10', 'col31130', 'm82452'), 'Unexpected A10-004 scope')
    lock = json.loads((BASE / 'sources.lock.json').read_text(encoding='utf-8'))
    pin = next(row for row in lock['repositories'] if row['role'] == 'A10+A20 upstream')
    require((manifest['commit'], manifest['tree']) == (pin['commit'], pin['tree']), 'Source lock mismatch')
    canonical = CANONICAL / 'modules/m82452/index.cnxml'
    require((ROOT / manifest['canonical_local_path']).resolve() == canonical.resolve(), 'Canonical path changed')
    require(file_hash(canonical) == manifest['full_module_sha256'], 'Canonical hash mismatch')
    require(canonical.stat().st_size == manifest['full_module_bytes'], 'Canonical size mismatch')
    source_bytes = canonical.read_bytes()
    source_blob = hashlib.sha1(b'blob ' + str(len(source_bytes)).encode('ascii') + b'\0' + source_bytes).hexdigest()
    require(source_blob == manifest['canonical_git_blob_sha1'], 'Canonical Git blob mismatch')
    excerpt_path = BASE / 'source-excerpts/a10-unit-004.cnxml'
    require(manifest['source_excerpt'] == excerpt_path.name, 'Excerpt path mismatch')
    require(file_hash(excerpt_path) == manifest['excerpt_sha256']
            and excerpt_path.stat().st_size == manifest['excerpt_bytes'], 'Frozen witness mismatch')
    source, excerpt = ET.parse(canonical).getroot(), ET.parse(excerpt_path).getroot()
    content = source.find('{' + CNXML + '}content')
    require(content is not None, 'Missing source content')
    require(manifest['top_level_content_child_start_zero_based'] == 5
            and manifest['top_level_content_children_included'] == 2, 'Changed top-level scope')
    selected = list(content)[5:7]
    require([node.get('id') for node in selected] == manifest['selection_ids']
            == ['fs-id1170655247410', 'fs-id1170655222085'], 'Skipped instructional or review section')
    section, review = selected
    require(section.get('id') == manifest['section_start'] == manifest['scope_from']
            and len(section) == manifest['section_direct_children_included'] == 46,
            'Changed complete instructional-section extent')
    require(review.get('id') == manifest['review_section_id'] == manifest['scope_through_inclusive']
            and len(review) == manifest['review_direct_children_included'] == 2,
            'Changed complete Key Concepts extent')
    require(section[-1].get('id') == manifest['last_instructional_child_id'] == 'fs-id1170655222063',
            'Changed last instructional child')
    require(list(content)[7].get('id') == manifest['next_source_id'] == 'fs-id1170655190123'
            and list(content)[7].get('class') == manifest['next_source_class'] == 'section-exercises',
            'Changed required next exercise section')
    require(len(excerpt) == 2 and excerpt.get('id') == manifest['excerpt_root_id'] == 'a10-unit-004-excerpt'
            and [tree(node) for node in selected] == [tree(node) for node in excerpt],
            'Frozen whole instructional/review subtrees differ from canonical source')
    for node, field in [(section, 'selected_section_child_ids'), (review, 'selected_review_child_ids')]:
        child_keys = [child.get('id') or node.get('id') + '/title' for child in node]
        require(child_keys == manifest[field], 'Changed selected child sequence')
    ids = [node.get('id') for node in excerpt.iter() if node is not excerpt and node.get('id')]
    require(ids == manifest['source_ids_in_document_order'] and len(ids) == 168,
            'Changed source ID sequence')
    require(ids[-1] == manifest['last_descendant_id'] == 'fs-id1166421706953',
            'Changed final source descendant')
    parents = {child: node for node in excerpt.iter() for child in node}
    images = [node for node in excerpt.iter() if tag(node) == 'image']
    require(len(images) == len(manifest['images']) == 15, 'Only fifteen selected images are allowed')
    require((ROOT / manifest['media_authority_manifest_path']).resolve() == MEDIA_MANIFEST.resolve(),
            'Media authority path changed')
    require(file_hash(MEDIA_MANIFEST) == manifest['media_authority_manifest_sha256'], 'Media authority hash mismatch')
    with MEDIA_MANIFEST.open(encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.DictReader(handle))
    prepared = []
    for node, spec in zip(images, manifest['images']):
        filename = PurePosixPath(node.get('src')).name
        src = '../../media/' + filename
        require(node.get('src') == spec['source_src'] == src
                and spec['source_path'] == 'media/' + filename, 'Image source path changed')
        original = CANONICAL / 'media' / filename
        require((canonical.parent / src).resolve() == original.resolve()
                and (ROOT / spec['canonical_local_path']).resolve() == original.resolve(), 'Unsafe original image path')
        target = BASE / 'assets/a10' / filename
        require(spec['path'] == 'assets/a10/' + filename
                and target.resolve().parent == (BASE / 'assets/a10').resolve(), 'Unsafe target image path')
        require(parents[node].get('id') == spec['media_id'], 'Image-media association changed')
        require(node.get('mime-type') == spec['declared_mime']
                and spec['actual_image_format'] == 'Jpeg', 'Source MIME ledger changed')
        data = original.read_bytes()
        require(len(data) == spec['bytes'] and digest(data) == spec['sha256'], 'Original image hash/size mismatch')
        require(jpeg_dimensions(data) == (spec['width'], spec['height']), 'Original JPEG dimensions mismatch')
        matches = [row for row in rows if row['relative_path'] == spec['source_path']]
        require(len(matches) == 1, 'Missing or duplicate media authority row')
        row = matches[0]
        require(row['sha256'] == spec['sha256'] and int(row['bytes']) == len(data), 'Media authority values mismatch')
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()
        require(blob == row['git_blob_sha1'] == spec['git_blob_sha1'], 'Original image Git blob mismatch')
        prepared.append((spec, original, target, data, row, parents[node].get('alt')))
    require(sum(len(item[3]) for item in prepared) == manifest['total_declared_image_bytes'] == 1015473,
            'Image byte total changed')
    allowed_notices = {
        'languages/pnb-Arab-PK/provenance/A10-release/NOTICE.txt',
        'languages/pnb-Arab-PK/provenance/upstream--osbooks-prealgebra-bundle/LICENSE'
    }
    require({entry['path'] for entry in manifest['existing_notice_inputs']} == allowed_notices,
            'Unexpected existing notice inputs')
    notices = []
    for entry in manifest['existing_notice_inputs']:
        data = (ROOT / entry['path']).read_bytes().replace(b'\r\n', b'\n')
        require(digest(data) == entry['sha256'], 'Existing notice logical-LF hash mismatch')
        notices.append(dict(entry))
    return manifest, excerpt, prepared, notices


def notice_record(manifest, prepared, notices):
    return {
        'schema': 'a10-retained-component-evidence-v1',
        'unit': 'A10-004', 'work': 'OpenStax Elementary Algebra 2e',
        'module': 'm82452', 'collection': 'col31130', 'commit': manifest['commit'],
        'manifest_sha256': file_hash(MANIFEST), 'excerpt_sha256': manifest['excerpt_sha256'],
        'scope': 'Fifteen unchanged declared source images only; no new supply or license audit.',
        'existing_notice_inputs': notices,
        'existing_notice_hash_policy': manifest['existing_notice_hash_policy'],
        'release_notice_verbatim': (BASE / 'provenance/A10-release/NOTICE.txt').read_text(encoding='utf-8'),
        'existing_license_statement': 'Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International, subject to component-specific credits and restrictions.',
        'rights_status': 'Existing audited A10 policy is retained. No new component-specific clearance determination is made.',
        'credit_limit': 'Media authority rows identify bytes and Git blobs, not rights holders or permissions. Absence of an image-specific credit is not clearance.',
        'media_authority_manifest': {'path': MEDIA_MANIFEST.relative_to(ROOT).as_posix(),
                                     'sha256': file_hash(MEDIA_MANIFEST)},
        'images': [
            dict(figure_id=spec['figure_id'], media_id=spec['media_id'],
                 source_path=spec['source_path'], path=spec['path'], sha256=spec['sha256'],
                 bytes=spec['bytes'], width=spec['width'], height=spec['height'],
                 source_declared_mime=spec['declared_mime'], actual_mime='image/jpeg',
                 source_english_alt=source_alt, existing_media_authority_row=row,
                 treatment='Original JPEG bytes unchanged and unmirrored; faithful source-alt trace with separately declared original accessible corrections and bilingual key. Source MIME retained even where PNG was declared.',
                 component_clearance='Not newly assessed; subject to retained component-specific credits and restrictions.')
            for spec, original, target, data, row, source_alt in prepared
        ],
        'whole_book_translation_complete': False,
        'earlier_collection_items_not_covered_by_this_unit': manifest['earlier_collection_items_not_covered_by_this_unit']
    }


def prepare():
    manifest, excerpt, prepared, notices = load_inputs()
    for spec, original, target, data, row, source_alt in prepared:
        require(not target.exists() or file_hash(target) == spec['sha256'],
                'Refusing to overwrite different existing reader asset: ' + str(target))
    # Validate every input and resolved target before any asset write.
    for spec, original, target, data, row, source_alt in prepared:
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_bytes(data)
        require(file_hash(target) == spec['sha256'], 'Copied image hash mismatch')
    NOTICES.write_text(json.dumps(notice_record(manifest, prepared, notices), ensure_ascii=False, indent=2) + '\n',
                       encoding='utf-8', newline='\n')
    print('Prepared A10-004: 15 original JPEGs, 1,015,473 bytes; existing rights status retained, no new clearance.')


if __name__ == '__main__':
    prepare()


