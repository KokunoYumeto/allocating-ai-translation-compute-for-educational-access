"""Prepare only the four pinned A10-006 images; preserve existing notice policy."""
import copy
import csv
import hashlib
import json
from pathlib import PurePosixPath
import xml.etree.ElementTree as ET
from prepare_a10 import BASE, ROOT, CANONICAL, CNXML, MATH, digest, file_hash, jpeg_dimensions, require, tag, tree

MANIFEST = BASE / 'source-excerpts/manifest-a10-006.json'
NOTICES = BASE / 'provenance/a10-unit-006-component-notices.json'
MEDIA_MANIFEST = ROOT / 'downloads/extracted/A10/authority/MEDIA_AUTHORITY_MANIFEST.csv'
TRANSLATION = BASE / 'translations/a10-unit-006.json'


def load_inputs():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    require((manifest['unit'], manifest['assignment'], manifest['collection'], manifest['module'])
            == ('A10-006', 'A10', 'col31130', 'm82453'), 'Unexpected A10-006 scope')
    lock = json.loads((BASE / 'sources.lock.json').read_text(encoding='utf-8'))
    pin = next(row for row in lock['repositories'] if row['role'] == 'A10+A20 upstream')
    require((manifest['commit'], manifest['tree']) == (pin['commit'], pin['tree']), 'Source lock mismatch')
    canonical = CANONICAL / 'modules/m82453/index.cnxml'
    require((ROOT / manifest['canonical_local_path']).resolve() == canonical.resolve(), 'Canonical path changed')
    data = canonical.read_bytes()
    require(digest(data) == manifest['full_module_sha256'] and len(data) == manifest['full_module_bytes'],
            'Canonical hash/size changed')
    blob = hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()
    require(blob == manifest['canonical_git_blob_sha1'], 'Canonical Git blob changed')
    require(manifest['source_prefix_start_byte'] == 0 and manifest['source_prefix_end_byte_exclusive'] == 42893,
            'Canonical prefix boundary changed')
    prefix = data[:manifest['source_prefix_end_byte_exclusive']]
    require(digest(prefix) == manifest['source_prefix_sha256'], 'Canonical prefix changed')
    for witness in manifest['source_byte_witnesses']:
        part = data[witness['start_byte']:witness['end_byte_exclusive']]
        require(len(part) == witness['bytes'] and digest(part) == witness['sha256'], 'Source byte witness changed')
    comparison = ROOT / manifest['indonesian_comparison_path']
    require(file_hash(comparison) == manifest['indonesian_comparison_sha256']
            and comparison.stat().st_size == manifest['indonesian_comparison_bytes'], 'Pinned comparison changed')
    excerpt_path = BASE / 'source-excerpts/a10-unit-006.cnxml'
    require(manifest['source_excerpt'] == excerpt_path.name and file_hash(excerpt_path) == manifest['excerpt_sha256']
            and excerpt_path.stat().st_size == manifest['excerpt_bytes'], 'Frozen excerpt changed')
    require(manifest['translation_path'] == TRANSLATION.relative_to(BASE).as_posix()
            and file_hash(TRANSLATION) == manifest['translation_sha256']
            and TRANSLATION.stat().st_size == manifest['translation_bytes'], 'Frozen translation changed')
    source, excerpt = ET.parse(canonical).getroot(), ET.parse(excerpt_path).getroot()
    expected = copy.deepcopy(source)
    content = expected.find('{' + CNXML + '}content')
    require(content is not None and len(content) == 8, 'Canonical content extent changed')
    require([node.get('id') for node in list(content)[:2]] == manifest['selection_ids']
            == ['fs-id1170654939047', 'fs-id1170655150800'], 'Opening selection changed')
    require(content[2].get('id') == manifest['next_source_id'] == 'fs-id1170654953465',
            'Next required section changed')
    require(len(content[1]) == manifest['section_direct_children_included'] == 53
            and content[1][-1].get('id') == manifest['scope_through_inclusive'] == 'fs-id1170655102894',
            'Complete first section boundary changed')
    for child in list(content)[2:]:
        content.remove(child)
    for child in list(expected):
        if tag(child) == 'glossary':
            expected.remove(child)
    require(source.attrib == manifest['source_root_attributes'] == {}, 'Canonical root attributes changed')
    expected.set('id', 'a10-unit-006-excerpt')
    require(excerpt.get('id') == manifest['excerpt_root_id'] and tree(expected) == tree(excerpt),
            'Complete selected tree differs from canonical source')
    require([tag(node) for node in excerpt] == ['title', 'metadata', 'content'], 'Root metadata/order omitted')
    meta = excerpt.find('{' + CNXML + '}metadata')
    require([tag(node) for node in meta] == manifest['module_metadata']['source_order'], 'Metadata order changed')
    values = {tag(node): node.text for node in meta}
    require(values['content-id'] == manifest['module_metadata']['content_id'] == 'm82453'
            and values['uuid'] == manifest['module_metadata']['uuid'] == '7c6afafa-02d2-4a6b-8aa7-26905730d112',
            'Metadata values changed')
    ids = [node.get('id') for node in excerpt.iter() if node is not excerpt and node.get('id')]
    require(ids == manifest['source_ids_in_document_order'] and len(ids) == len(set(ids)) == 134,
            'Source ID sequence changed')
    require(len(list(excerpt.iter())) == 1243 and ids[-1] == manifest['last_descendant_id'],
            'Selected element extent changed')
    counts = {name: sum(tag(node) == name for node in excerpt.iter())
              for name in ('exercise', 'solution', 'math', 'newline', 'image', 'table', 'link', 'term', 'span')}
    require(counts == dict(exercise=9, solution=9, math=98, newline=12, image=4, table=8, link=3, term=14, span=48),
            'Selected content counts changed')
    require((ROOT / manifest['media_authority_manifest_path']).resolve() == MEDIA_MANIFEST.resolve()
            and file_hash(MEDIA_MANIFEST) == manifest['media_authority_manifest_sha256'], 'Media authority changed')
    with MEDIA_MANIFEST.open(encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.DictReader(handle))
    parents = {child: node for node in excerpt.iter() for child in node}
    images = [node for node in excerpt.iter() if tag(node) == 'image']
    require(len(images) == len(manifest['images']) == 4, 'Only four declared images are allowed')
    prepared = []
    for index, (node, spec) in enumerate(zip(images, manifest['images']), 1):
        filename = PurePosixPath(node.get('src')).name
        require(filename == f'CNX_ElemAlg_Figure_01_02_{index:03}_img_new.jpg', 'Unexpected selected image')
        require(node.get('src') == spec['source_src'] == spec['source_cnxml_src'] == '../../media/' + filename
                and spec['source_path'] == 'media/' + filename, 'Image source path changed')
        original = CANONICAL / 'media' / filename
        require((canonical.parent / node.get('src')).resolve() == original.resolve()
                and (ROOT / spec['canonical_local_path']).resolve() == original.resolve(), 'Unsafe source image path')
        target = BASE / 'assets/a10' / filename
        require(spec['path'] == 'assets/a10/' + filename
                and target.resolve().parent == (BASE / 'assets/a10').resolve(), 'Unsafe target image path')
        require(parents[node].get('id') == spec['media_id'] and spec['figure_id'] is None
                and spec['local_label'] is None, 'Unnumbered image ownership changed')
        require(node.get('mime-type') == spec['declared_mime'] == spec['source_declared_mime'] == 'image/jpeg'
                and spec['actual_mime'] == 'image/jpeg' and spec['actual_image_format'] == 'Jpeg', 'MIME changed')
        image_data = original.read_bytes()
        require(len(image_data) == spec['bytes'] and digest(image_data) == spec['sha256'], 'Image bytes changed')
        require(jpeg_dimensions(image_data) == (spec['width'], spec['height']), 'Original image dimensions changed')
        matches = [(row_index, row) for row_index, row in enumerate(rows, 2)
                   if row['relative_path'] == spec['source_path']]
        require(len(matches) == 1, 'Missing/duplicate image identity row')
        row_index, row = matches[0]
        require(row == spec['existing_media_authority_row']
                and row_index == spec['existing_media_authority_row_number_including_header']
                and row['sha256'] == spec['sha256'] and int(row['bytes']) == len(image_data), 'Media row changed')
        blob = hashlib.sha1(b'blob ' + str(len(image_data)).encode('ascii') + b'\0' + image_data).hexdigest()
        require(blob == row['git_blob_sha1'] == spec['git_blob_sha1'], 'Image Git blob changed')
        require(parents[node].get('alt') == spec['source_english_alt'], 'Source alt identity changed')
        prepared.append((spec, original, target, image_data, row, parents[node].get('alt')))
    require(sum(len(data) for _, _, _, data, _, _ in prepared) == manifest['total_declared_image_bytes'] == 103327,
            'Declared image payload changed')
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
        'schema': 'a10-retained-component-evidence-v1', 'unit': 'A10-006',
        'work': 'OpenStax Elementary Algebra 2e', 'module': 'm82453', 'collection': 'col31130',
        'commit': manifest['commit'], 'manifest_sha256': file_hash(MANIFEST),
        'excerpt_sha256': manifest['excerpt_sha256'],
        'scope': 'Four unchanged declared original JPEGs only; no new supply or license audit.',
        'existing_notice_inputs': notices, 'existing_notice_hash_policy': manifest['existing_notice_hash_policy'],
        'release_notice_verbatim': (BASE / 'provenance/A10-release/NOTICE.txt').read_text(encoding='utf-8'),
        'existing_license_statement': 'Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International, subject to component-specific credits and restrictions.',
        'rights_status': 'Existing audited A10 policy is retained. No new component-specific clearance determination is made.',
        'credit_limit': 'Media authority rows identify bytes and Git blobs, not rights holders or permissions. Absence of an image-specific credit is not clearance.',
        'media_authority_manifest': {'path': MEDIA_MANIFEST.relative_to(ROOT).as_posix(), 'sha256': file_hash(MEDIA_MANIFEST)},
        'images': [
            dict(figure_id=None, media_id=spec['media_id'], source_path=spec['source_path'], path=spec['path'],
                 sha256=spec['sha256'], bytes=spec['bytes'], git_blob_sha1=spec['git_blob_sha1'],
                 width=spec['width'], height=spec['height'], source_declared_mime=spec['declared_mime'],
                 actual_mime='image/jpeg', source_english_alt=source_alt, existing_media_authority_row=row,
                 treatment='Original JPEG bytes unchanged and unmirrored; faithful Punjabi source-alt trace and separate bilingual key. Only declared image003 uses an explicitly original disambiguated accessible alt.',
                 original_bilingual_key_id=spec['original_bilingual_key_id'],
                 original_accessible_override=spec['source_alt_override'],
                 component_clearance='Not newly assessed; subject to retained component-specific credits and restrictions.')
            for spec, original, target, data, row, source_alt in prepared
        ],
        'whole_module_translation_complete': False, 'whole_book_translation_complete': False,
        'whole_assignment_complete': False,
        'scope_boundary': {'from': manifest['scope_from'], 'section': manifest['section_start'],
                           'through': manifest['scope_through_inclusive'], 'next_required': manifest['next_source_id']}
    }


def prepare():
    manifest, document, prepared, notices = load_inputs()
    for spec, original, target, data, row, source_alt in prepared:
        require(not target.exists() or file_hash(target) == spec['sha256'],
                'Refusing to overwrite a different existing image: ' + str(target))
    # Validate every source, destination and retained notice before any write.
    for spec, original, target, data, row, source_alt in prepared:
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_bytes(data)
        require(file_hash(target) == spec['sha256'], 'Copied asset hash mismatch')
    NOTICES.write_text(json.dumps(notice_record(manifest, prepared, notices), ensure_ascii=False, indent=2) + '\n',
                       encoding='utf-8', newline='\n')
    print('Prepared A10-006:4originalJPEGs,103327bytes; retained component restrictions, no new clearance.')


if __name__ == '__main__':
    prepare()

