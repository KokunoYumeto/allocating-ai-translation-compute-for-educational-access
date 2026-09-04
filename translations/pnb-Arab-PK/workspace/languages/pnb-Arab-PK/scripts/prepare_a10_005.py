"""Prepare only the declared A10-005 checklist image and retained notices."""
import copy
import csv
import hashlib
import json
from pathlib import PurePosixPath
import xml.etree.ElementTree as ET
from prepare_a10 import BASE, ROOT, CANONICAL, CNXML, MATH, digest, file_hash, jpeg_dimensions, require, tag, tree

MANIFEST = BASE / 'source-excerpts/manifest-a10-005.json'
NOTICES = BASE / 'provenance/a10-unit-005-component-notices.json'
MEDIA_MANIFEST = ROOT / 'downloads/extracted/A10/authority/MEDIA_AUTHORITY_MANIFEST.csv'


def load_inputs():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    require((manifest['unit'], manifest['assignment'], manifest['collection'], manifest['module'])
            == ('A10-005', 'A10', 'col31130', 'm82452'), 'Unexpected A10-005 scope')
    lock = json.loads((BASE / 'sources.lock.json').read_text(encoding='utf-8'))
    pin = next(row for row in lock['repositories'] if row['role'] == 'A10+A20 upstream')
    require((manifest['commit'], manifest['tree']) == (pin['commit'], pin['tree']), 'Source lock mismatch')
    canonical = CANONICAL / 'modules/m82452/index.cnxml'
    require((ROOT / manifest['canonical_local_path']).resolve() == canonical.resolve(), 'Canonical path changed')
    data = canonical.read_bytes()
    require(digest(data) == manifest['full_module_sha256'] and len(data) == manifest['full_module_bytes'],
            'Canonical hash/size mismatch')
    blob = hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()
    require(blob == manifest['canonical_git_blob_sha1'], 'Canonical Git blob changed')
    for witness in manifest['source_byte_witnesses']:
        part = data[witness['start_byte']:witness['end_byte_exclusive']]
        require(len(part) == witness['bytes'] and digest(part) == witness['sha256'], 'Source byte witness changed')
    comparison = ROOT / manifest['indonesian_comparison_path']
    require(file_hash(comparison) == manifest['indonesian_comparison_sha256'], 'Pinned comparison changed')
    excerpt_path = BASE / 'source-excerpts/a10-unit-005.cnxml'
    require(manifest['source_excerpt'] == excerpt_path.name and file_hash(excerpt_path) == manifest['excerpt_sha256']
            and excerpt_path.stat().st_size == manifest['excerpt_bytes'], 'Frozen excerpt changed')
    source, excerpt = ET.parse(canonical).getroot(), ET.parse(excerpt_path).getroot()
    expected = copy.deepcopy(source)
    content = expected.find('{' + CNXML + '}content')
    require(content is not None and len(content) == 8, 'Canonical content extent changed')
    require(content[7].get('id') == manifest['scope_from'] == 'fs-id1170655190123'
            and content[7].get('class') == 'section-exercises', 'Changed final exercise scope')
    for child in list(content)[:7]:
        content.remove(child)
    require(source.attrib == manifest['source_root_attributes'] == {}, 'Canonical root attributes changed')
    expected.set('id', 'a10-unit-005-excerpt')
    require(excerpt.get('id') == manifest['excerpt_root_id'] and tree(expected) == tree(excerpt),
            'Complete selected hierarchy differs from canonical source')
    require([tag(node) for node in excerpt] == ['title', 'metadata', 'content', 'glossary'],
            'Root title, metadata or glossary omitted')
    meta = excerpt.find('{' + CNXML + '}metadata')
    require([tag(node) for node in meta] == manifest['module_context_backfill']['source_order'],
            'Metadata child order changed')
    fields = {tag(node): node.text for node in meta}
    require(fields['content-id'] == manifest['module_context_backfill']['content_id'] == 'm82452'
            and fields['uuid'] == manifest['module_context_backfill']['uuid']
            == '16b0b665-bb17-4b27-886f-08a966ee6c79', 'Complete metadata values changed')
    ids = [node.get('id') for node in excerpt.iter() if node is not excerpt and node.get('id')]
    require(ids == manifest['source_ids_in_document_order'] and len(ids) == len(set(ids)) == 383,
            'Changed source ID sequence')
    require(len(list(excerpt.iter())) == 624 and ids[-1] == manifest['last_descendant_id'],
            'Changed selected element extent')
    counts = {name: sum(tag(node) == name for node in excerpt.iter())
              for name in ('exercise', 'solution', 'definition', 'math', 'newline', 'image', 'table', 'link')}
    require(counts == dict(exercise=82, solution=41, definition=11, math=12, newline=5, image=1, table=0, link=0),
            'Changed bounded content counts')
    require((ROOT / manifest['media_authority_manifest_path']).resolve() == MEDIA_MANIFEST.resolve()
            and file_hash(MEDIA_MANIFEST) == manifest['media_authority_manifest_sha256'], 'Media authority changed')
    with MEDIA_MANIFEST.open(encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.DictReader(handle))
    parents = {child: node for node in excerpt.iter() for child in node}
    images = [node for node in excerpt.iter() if tag(node) == 'image']
    require(len(images) == len(manifest['images']) == 1, 'Only one declared image is allowed')
    prepared = []
    for node, spec in zip(images, manifest['images']):
        filename = PurePosixPath(node.get('src')).name
        require(filename == 'CNX_ElemAlg_Figure_01_01_201_img_new.jpg', 'Unexpected admitted image')
        require(node.get('src') == spec['source_src'] == '../../media/' + filename
                and spec['source_path'] == 'media/' + filename, 'Source image path changed')
        original = CANONICAL / 'media' / filename
        require((canonical.parent / node.get('src')).resolve() == original.resolve()
                and (ROOT / spec['canonical_local_path']).resolve() == original.resolve(), 'Unsafe source image path')
        target = BASE / 'assets/a10' / filename
        require(spec['path'] == 'assets/a10/' + filename
                and target.resolve().parent == (BASE / 'assets/a10').resolve(), 'Unsafe target image path')
        require(parents[node].get('id') == spec['media_id'] == 'fs-id1170655207116'
                and spec['figure_id'] is None, 'Unnumbered image ownership changed')
        require(node.get('mime-type') == spec['declared_mime'] == 'image/jpeg'
                and spec['actual_image_format'] == 'Jpeg', 'Source/actual MIME changed')
        image_data = original.read_bytes()
        require(len(image_data) == spec['bytes'] == manifest['total_declared_image_bytes'] == 75105
                and digest(image_data) == spec['sha256'], 'Original image bytes changed')
        require(jpeg_dimensions(image_data) == (spec['width'], spec['height']) == (632, 166),
                'Original image dimensions changed')
        matches = [row for row in rows if row['relative_path'] == spec['source_path']]
        require(len(matches) == 1, 'Missing/duplicate media authority row')
        row = matches[0]
        require(row == spec['existing_media_authority_row'] and row['sha256'] == spec['sha256']
                and int(row['bytes']) == len(image_data), 'Existing image identity row changed')
        blob = hashlib.sha1(b'blob ' + str(len(image_data)).encode('ascii') + b'\0' + image_data).hexdigest()
        require(blob == row['git_blob_sha1'] == spec['git_blob_sha1'], 'Image Git blob changed')
        prepared.append((spec, original, target, image_data, row, parents[node].get('alt')))
    allowed = {'languages/pnb-Arab-PK/provenance/A10-release/NOTICE.txt',
               'languages/pnb-Arab-PK/provenance/upstream--osbooks-prealgebra-bundle/LICENSE'}
    require({row['path'] for row in manifest['existing_notice_inputs']} == allowed, 'Unexpected notice input')
    notices = []
    for row in manifest['existing_notice_inputs']:
        require(digest((ROOT / row['path']).read_bytes().replace(b'\r\n', b'\n')) == row['sha256'],
                'Existing notice logical-LF hash changed')
        notices.append(dict(row))
    return manifest, excerpt, prepared, notices


def notice_record(manifest, prepared, notices):
    return {
        'schema': 'a10-retained-component-evidence-v1', 'unit': 'A10-005',
        'work': 'OpenStax Elementary Algebra 2e', 'module': 'm82452', 'collection': 'col31130',
        'commit': manifest['commit'], 'manifest_sha256': file_hash(MANIFEST),
        'excerpt_sha256': manifest['excerpt_sha256'],
        'scope': 'One unchanged declared checklist image only; no new supply or license audit.',
        'existing_notice_inputs': notices, 'existing_notice_hash_policy': manifest['existing_notice_hash_policy'],
        'release_notice_verbatim': (BASE / 'provenance/A10-release/NOTICE.txt').read_text(encoding='utf-8'),
        'existing_license_statement': 'Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International, subject to component-specific credits and restrictions.',
        'rights_status': 'Existing audited A10 policy is retained. No new component-specific clearance determination is made.',
        'credit_limit': 'Media authority rows identify bytes and Git blobs, not rights holders or permissions. Absence of an image-specific credit is not clearance.',
        'media_authority_manifest': {'path': MEDIA_MANIFEST.relative_to(ROOT).as_posix(), 'sha256': file_hash(MEDIA_MANIFEST)},
        'images': [dict(figure_id=spec['figure_id'], media_id=spec['media_id'],
                       source_path=spec['source_path'], path=spec['path'], sha256=spec['sha256'],
                       bytes=spec['bytes'], git_blob_sha1=spec['git_blob_sha1'], width=spec['width'], height=spec['height'],
                       source_declared_mime=spec['declared_mime'], actual_mime='image/jpeg', source_english_alt=source_alt,
                       existing_media_authority_row=row,
                       treatment='Original JPEG bytes unchanged and unmirrored; faithful Punjabi alt and explicitly original bilingual checklist key. No accessible source-error override is declared.',
                       component_clearance='Not newly assessed; subject to retained component-specific credits and restrictions.')
                   for spec, original, target, data, row, source_alt in prepared],
        'whole_book_translation_complete': False,
        'earlier_collection_items_not_covered_by_this_unit': manifest['earlier_collection_items_not_covered_by_this_unit']
    }


def prepare():
    manifest, document, prepared, notices = load_inputs()
    for spec, original, target, data, row, source_alt in prepared:
        require(not target.exists() or file_hash(target) == spec['sha256'],
                'Refusing to overwrite a different existing image: ' + str(target))
    # Every input and resolved target is checked before any material write.
    for spec, original, target, data, row, source_alt in prepared:
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_bytes(data)
        require(file_hash(target) == spec['sha256'], 'Copied asset hash mismatch')
    NOTICES.write_text(json.dumps(notice_record(manifest, prepared, notices), ensure_ascii=False, indent=2) + '\n',
                       encoding='utf-8', newline='\n')
    print('Prepared A10-005: one original JPEG,75,105bytes; existing component restrictions retained.')


if __name__ == '__main__':
    prepare()
