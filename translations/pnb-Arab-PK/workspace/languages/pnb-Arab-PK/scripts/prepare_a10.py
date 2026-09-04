"""Prepare only A10-001's declared images and retained-rights evidence."""
from pathlib import Path, PurePosixPath
import copy
import csv
import hashlib
import json
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
MANIFEST = BASE / 'source-excerpts/manifest-a10-001.json'
NOTICES = BASE / 'provenance/a10-unit-001-component-notices.json'
CANONICAL = ROOT / 'downloads/complete-upstream/osbooks-prealgebra-bundle'
MEDIA_MANIFEST = ROOT / 'downloads/extracted/A10/authority/MEDIA_AUTHORITY_MANIFEST.csv'
CNXML = 'http://cnx.rice.edu/cnxml'
MATH = 'http://www.w3.org/1998/Math/MathML'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    return digest(path.read_bytes())


def tag(node):
    return node.tag.rsplit('}', 1)[-1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def tree(node):
    """Expanded names, attributes and exact mixed text; exclude outer tail only."""
    return (node.tag, tuple(sorted(node.attrib.items())), node.text,
            tuple((tree(child), child.tail) for child in node))


def jpeg_dimensions(data):
    require(data[:2] == b'\xff\xd8', 'Expected an original JPEG')
    offset = 2
    while offset < len(data):
        require(data[offset] == 255, 'Malformed JPEG marker')
        while offset < len(data) and data[offset] == 255:
            offset += 1
        require(offset < len(data), 'Truncated JPEG marker')
        marker = data[offset]
        offset += 1
        if marker in {1, 0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
            continue
        require(offset + 2 <= len(data), 'Truncated JPEG segment')
        length = int.from_bytes(data[offset:offset + 2], 'big')
        require(length >= 2 and offset + length <= len(data), 'Invalid JPEG length')
        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                      0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
            require(length >= 8, 'Truncated JPEG frame')
            return (int.from_bytes(data[offset + 5:offset + 7], 'big'),
                    int.from_bytes(data[offset + 3:offset + 5], 'big'))
        require(marker != 0xDA, 'JPEG dimensions missing before scan')
        offset += length
    raise ValueError('JPEG dimensions not found')


def load_inputs():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    require((manifest['unit'], manifest['assignment'], manifest['collection'], manifest['module'])
            == ('A10-001', 'A10', 'col31130', 'm82452'), 'Unexpected A10 scope')
    lock = json.loads((BASE / 'sources.lock.json').read_text(encoding='utf-8'))
    pinned = next(row for row in lock['repositories'] if row['role'] == 'A10+A20 upstream')
    require(manifest['commit'] == pinned['commit'] and manifest['tree'] == pinned['tree'],
            'Manifest does not match the existing source lock')
    canonical_file = CANONICAL / 'modules/m82452/index.cnxml'
    require((ROOT / manifest['canonical_local_path']).resolve() == canonical_file.resolve(),
            'Unexpected canonical module path')
    require(file_hash(canonical_file) == manifest['full_module_sha256'], 'Canonical hash mismatch')
    excerpt_file = BASE / 'source-excerpts/a10-unit-001.cnxml'
    require(manifest['source_excerpt'] == excerpt_file.name, 'Unexpected excerpt path')
    require(file_hash(excerpt_file) == manifest['excerpt_sha256'], 'Excerpt hash mismatch')
    source = ET.parse(canonical_file).getroot()
    excerpt = ET.parse(excerpt_file).getroot()
    content = source.find('{' + CNXML + '}content')
    require(content is not None, 'Missing canonical content')
    require([node.get('id') for node in list(content)[:2]] == manifest['prelude_ids'],
            'Changed canonical prelude')
    section = copy.deepcopy(next(node for node in content if node.get('id') == manifest['section_start']))
    require(manifest['section_direct_children_included'] == 13, 'Unexpected section extent')
    require(section[12].get('id') == manifest['scope_through_inclusive']
            and section[13].get('id') == manifest['next_source_id'], 'Changed source boundary')
    for child in list(section)[13:]:
        section.remove(child)
    selected = list(content)[:2] + [section]
    require(len(excerpt) == 3 and [tree(node) for node in selected] == [tree(node) for node in excerpt],
            'Frozen selection differs from canonical source')
    source_ids = [node.get('id') for node in excerpt.iter() if node is not excerpt and node.get('id')]
    require(source_ids == manifest['source_ids_in_document_order'] and len(source_ids) == 43,
            'Changed source ID sequence')
    image_nodes = [node for node in excerpt.iter() if tag(node) == 'image']
    require(len(image_nodes) == len(manifest['images']) == 3, 'Only the three selected images are allowed')
    with MEDIA_MANIFEST.open(encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.DictReader(handle))
    prepared = []
    for node, spec in zip(image_nodes, manifest['images']):
        src = node.get('src')
        filename = PurePosixPath(src).name
        require(src == '../../media/' + filename and spec['source_src'] == src,
                'Image source path changed')
        require(spec['source_path'] == 'media/' + filename, 'Image manifest path changed')
        original = CANONICAL / 'media' / filename
        require((canonical_file.parent / src).resolve() == original.resolve()
                and (ROOT / spec['canonical_local_path']).resolve() == original.resolve(),
                'Image escaped its declared canonical location')
        target = BASE / 'assets/a10' / filename
        require(spec['path'] == 'assets/a10/' + filename
                and target.resolve().parent == (BASE / 'assets/a10').resolve(), 'Unsafe reader image path')
        data = original.read_bytes()
        require(len(data) == spec['bytes'] and digest(data) == spec['sha256'], 'Original image hash/size mismatch')
        require(jpeg_dimensions(data) == (spec['width'], spec['height']), 'Original image dimensions mismatch')
        matched = [row for row in rows if row['relative_path'] == spec['source_path']]
        require(len(matched) == 1, 'Missing/duplicate A10 media authority row')
        row = matched[0]
        require(row['sha256'] == spec['sha256'] and int(row['bytes']) == len(data), 'A10 media row mismatch')
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()
        require(blob == row['git_blob_sha1'], 'Selected original image blob mismatch')
        prepared.append((spec, original, target, data, row))
    notice_inputs = []
    for entry in manifest['existing_notice_inputs']:
        path = ROOT / entry['path']
        require(digest(path.read_bytes().replace(b'\r\n', b'\n')) == entry['sha256'], 'Existing notice input logical-LF hash mismatch')
        notice_inputs.append({'path': entry['path'], 'sha256': entry['sha256']})
    return manifest, excerpt, prepared, notice_inputs


def notice_record(manifest, prepared, notice_inputs):
    release_notice = BASE / 'provenance/A10-release/NOTICE.txt'
    return {
        'schema': 'a10-retained-component-evidence-v1',
        'unit': 'A10-001', 'work': 'OpenStax Elementary Algebra 2e',
        'module': 'm82452', 'collection': 'col31130', 'commit': manifest['commit'],
        'manifest_sha256': file_hash(MANIFEST), 'excerpt_sha256': manifest['excerpt_sha256'],
        'scope': 'Three unchanged source images only; no new license or supply audit.',
        'existing_notice_inputs': notice_inputs,
        'release_notice_verbatim': release_notice.read_text(encoding='utf-8'),
        'existing_license_statement': 'Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International, subject to component-specific credits and restrictions.',
        'rights_status': 'Existing audited A10 policy is retained. This preparation step makes no new component-specific clearance determination.',
        'credit_limit': 'The selected media authority rows identify bytes and Git blobs, not rights holders or permissions. Absence of an image-specific credit in these rows or selected captions is not clearance.',
        'media_authority_manifest': {'path': MEDIA_MANIFEST.relative_to(ROOT).as_posix(),
                                     'sha256': file_hash(MEDIA_MANIFEST)},
        'images': [dict(figure_id=spec['figure_id'], media_id=spec['media_id'],
                        source_path=spec['source_path'], path=spec['path'], sha256=spec['sha256'],
                        bytes=spec['bytes'], width=spec['width'], height=spec['height'],
                        existing_media_authority_row=row,
                        treatment='Original bytes retained, no mirroring or image editing; Punjabi alt and labeled original explanatory key.',
                        component_clearance='Not newly assessed; subject to retained component-specific credits and restrictions.')
                   for spec, original, target, data, row in prepared],
        'whole_book_translation_complete': False,
        'earlier_collection_items_pending': manifest['earlier_collection_items_still_pending']
    }


def prepare():
    manifest, excerpt, prepared, notices = load_inputs()
    for spec, original, target, data, row in prepared:
        require(not target.exists() or file_hash(target) == spec['sha256'],
                'Refusing to overwrite a different existing reader asset: ' + str(target))
    # All source, destination and existing-file checks complete before any writes.
    for spec, original, target, data, row in prepared:
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_bytes(data)
        require(file_hash(target) == spec['sha256'], 'Copied image hash mismatch')
    record = notice_record(manifest, prepared, notices)
    NOTICES.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('Prepared A10-001: 3 exact original images; existing rights status retained, no new clearance asserted.')


if __name__ == '__main__':
    prepare()
