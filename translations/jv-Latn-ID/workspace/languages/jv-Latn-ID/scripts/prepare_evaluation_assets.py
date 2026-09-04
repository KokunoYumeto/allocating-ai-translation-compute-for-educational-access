"""Prepare the finite effective-media set for A10 expression evaluation.

The Indonesian v1.0.2 release overrides 012b and 013b.  Every other source
image falls back to the pinned canonical archive.  The five English instruction
labels receive small native SVG derivatives for the two Javanese tracks; all
numeric images retain their effective JPEG bytes.  This is deterministic asset
preparation, not image synthesis or human visual approval.
"""
import argparse
import csv
import hashlib
import html
import io
import json
import re
import xml.etree.ElementTree as ET
import zipfile

from config import DOWNLOADS, LANG, UPSTREAM_COMMIT
from safe_io import write_bytes

UNIT = 'a10-evaluate-expressions'
RULES_PATH = LANG / f'audio/{UNIT}.rules.json'
OUT = f'translation/assets/{UNIT}/'
RULES_SHA256 = '9b629c2df98b99cca29740fdbcace2c7e9b301bc45f9e88f407a71be44557ab5'
ID_MANIFEST_SHA256 = '5499e09e64347de101f410848a951d7ab25f44b57cf61cdcf0cbd8b1dc71ce9f'
AUTHORITY_SHA256 = '3b8478b77c8860363b7000cbffa68782320e73458289bdcda957acf1b971210f'
ID_OVERRIDES = {
    'CNX_ElemAlg_Figure_01_02_012b_img_new.jpg':
        'fc469cf6cd1dfac09c4010af7d7606f1309033663fc0ddbf891813f1b5208b67',
    'CNX_ElemAlg_Figure_01_02_013b_img_new.jpg':
        '31e05fe68d3807d96bca8c3c747a82bc0ccf1b08d2dbfdb70fc1dea36a025a1e',
}
SVG = '{http://www.w3.org/2000/svg}'
XML_LANG = '{http://www.w3.org/XML/1998/namespace}lang'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git_blob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def jpeg_dimensions(raw):
    """Return dimensions from an exact JPEG without decoding or transcoding it."""
    assert raw.startswith(b'\xff\xd8\xff'), 'Effective evaluation media is not JPEG'
    index = 2
    while index + 4 <= len(raw):
        while index < len(raw) and raw[index] != 0xFF:
            index += 1
        while index < len(raw) and raw[index] == 0xFF:
            index += 1
        assert index < len(raw), 'Truncated JPEG marker'
        marker = raw[index]
        index += 1
        if marker in (0x01, 0xD8, 0xD9):
            continue
        assert index + 2 <= len(raw), 'Truncated JPEG segment'
        length = int.from_bytes(raw[index:index + 2], 'big')
        assert length >= 2 and index + length <= len(raw), 'Invalid JPEG segment'
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                      0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            height = int.from_bytes(raw[index + 3:index + 5], 'big')
            width = int.from_bytes(raw[index + 5:index + 7], 'big')
            return width, height
        index += length
    raise AssertionError('JPEG dimensions not found')


def records(value):
    """Yield manifest records without assuming the producer's outer key name."""
    if isinstance(value, dict):
        if {'path', 'bytes', 'sha256'} <= set(value):
            yield value
        for child in value.values():
            yield from records(child)
    elif isinstance(value, list):
        for child in value:
            yield from records(child)


def vector(track, visible_label, alt):
    assert track in ('jv-academic', 'jv-conversation')
    assert re.fullmatch(r"(?:nalika x = [15]|Ganti(?:a)? x nganggo 4\.|Gunakna x = 4\.)", visible_label)
    match = re.search(r'([145])(?=\.?$)', visible_label)
    assert match is not None
    before, number, after = visible_label[:match.start()], match.group(1), visible_label[match.end():]
    width = max(260, 46 + 17 * len(visible_label))
    raw = f'''<svg xmlns="http://www.w3.org/2000/svg" xml:lang="jv-Latn-ID" width="{width}" height="72" viewBox="0 0 {width} 72" role="img" aria-labelledby="title desc">
<title id="title">{html.escape(visible_label)}</title>
<desc id="desc">{html.escape(alt)}</desc>
<rect id="background" width="100%" height="100%" fill="#ffffff"/>
<text id="label" x="18" y="45" font-family="Arial, sans-serif" font-size="28" fill="#343434"><tspan>{html.escape(before)}</tspan><tspan id="highlight" fill="#c21823">{number}</tspan><tspan>{html.escape(after)}</tspan></text>
</svg>
'''.encode()
    verify_vector(raw, track, visible_label, alt)
    return raw


def verify_vector(raw, track, visible_label, alt):
    root = ET.fromstring(raw)
    nodes = {node.get('id'): node for node in root.iter() if node.get('id')}
    assert root.tag == SVG + 'svg' and root.get(XML_LANG) == 'jv-Latn-ID'
    assert root.get('role') == 'img' and root.get('aria-labelledby') == 'title desc'
    assert nodes['title'].text == visible_label and nodes['desc'].text == alt
    assert ''.join(nodes['label'].itertext()) == visible_label
    assert nodes['highlight'].text in ('1', '4', '5')
    assert nodes['highlight'].get('fill') == '#c21823'
    assert nodes['background'].get('fill') == '#ffffff'
    assert int(root.get('width')) >= 260 and root.get('height') == '72'
    assert track in ('jv-academic', 'jv-conversation')


def products():
    rules_raw = RULES_PATH.read_bytes()
    assert sha(rules_raw) == RULES_SHA256
    rules = json.loads(rules_raw)
    charts = rules['chart_fixtures']
    assert len(charts) == 16
    assert sum(row['derivative_required'] for row in charts) == 5
    assert [row['id'] for row in charts] == [f'A10-EVAL-D{i:02}' for i in range(1, 17)]

    generated, assets = {}, []
    id_zip_path = DOWNLOADS / 'a10-source.zip'
    canonical_zip_path = DOWNLOADS / 'openstax-full-pinned.zip'
    with zipfile.ZipFile(id_zip_path) as id_zip, zipfile.ZipFile(canonical_zip_path) as canonical_zip:
        id_manifest_raw = id_zip.read('MANIFEST.json')
        authority_raw = id_zip.read('authority/MEDIA_AUTHORITY_MANIFEST.csv')
        assert sha(id_manifest_raw) == ID_MANIFEST_SHA256
        assert sha(authority_raw) == AUTHORITY_SHA256
        id_manifest = {row['path']: row for row in records(json.loads(id_manifest_raw))}
        authority = {row['relative_path']: row for row in csv.DictReader(io.StringIO(authority_raw.decode('utf-8-sig')))}
        id_members = set(id_zip.namelist())
        for fixture in charts:
            primary = fixture['primary_asset']
            english = fixture['english_authority_asset']
            name = primary['filename']
            source_src = '../../media/' + name
            assert fixture['source_image'] == source_src
            canonical_member = f'osbooks-prealgebra-bundle-{UPSTREAM_COMMIT}/media/{name}'
            canonical_raw = canonical_zip.read(canonical_member)
            authority_row = authority['media/' + name]
            assert (len(canonical_raw), sha(canonical_raw), git_blob(canonical_raw)) == (
                int(authority_row['bytes']), authority_row['sha256'], authority_row['git_blob_sha1'])
            assert sha(canonical_raw) == english['sha256']
            assert len(canonical_raw) == english['bytes']
            assert git_blob(canonical_raw) == english['git_blob_sha1']
            assert list(jpeg_dimensions(canonical_raw)) == english['dimensions']

            override_member = 'translated/media/' + name
            is_override = name in ID_OVERRIDES
            assert (override_member in id_members) is is_override
            assert fixture['indonesian_override_lookup']['present_in_id_zip'] is is_override
            assert fixture['indonesian_override_lookup']['present_in_id_manifest'] is is_override
            if is_override:
                effective = id_zip.read(override_member)
                manifest_row = id_manifest[override_member]
                assert (len(effective), sha(effective)) == (manifest_row['bytes'], manifest_row['sha256'])
                assert sha(effective) == ID_OVERRIDES[name]
                assert primary['provenance'] == 'pinned_indonesian_release_override'
                assert english['retained_as_effective_source'] is False
            else:
                assert override_member not in id_manifest
                effective = canonical_raw
                assert primary['provenance'] == 'pinned_english_authority_retained_by_indonesian_release'
                assert english['retained_as_effective_source'] is True
            assert (len(effective), sha(effective), list(jpeg_dimensions(effective))) == (
                primary['bytes'], primary['sha256'], primary['dimensions'])

            effective_path = OUT + name
            generated[effective_path] = effective
            outputs = {
                'id-academic': {'path': effective_path, 'sha256': sha(effective), 'mime_type': 'image/jpeg'}
            }
            if fixture['derivative_required']:
                assert fixture['linguistic_labels_present'] is True
                assert fixture['required_derivative_tracks'] == ['jv-academic', 'jv-conversation']
                for track in ('jv-academic', 'jv-conversation'):
                    visible = fixture['expected_jv_visible_labels'][track]
                    alt = fixture['expected_target_alt'][track]
                    derivative = vector(track, visible, alt)
                    path = effective_path + '.' + track + '.svg'
                    generated[path] = derivative
                    outputs[track] = {'path': path, 'sha256': sha(derivative), 'mime_type': 'image/svg+xml'}
            else:
                assert fixture['required_derivative_tracks'] == []
                for track in ('jv-academic', 'jv-conversation'):
                    outputs[track] = dict(outputs['id-academic'])

            source_media = ET.fromstring(fixture['source_cnxml'])
            source_declared_mime = source_media.find('{*}image').get('mime-type')
            assets.append({
                'fixture_id': fixture['id'], 'source_media_id': fixture['media_id'],
                'source_src': source_src, 'source_declared_mime': source_declared_mime,
                'effective_source': {
                    'path': primary['archive_member'], 'provenance': primary['provenance'],
                    'bytes': len(effective), 'sha256': sha(effective),
                    'dimensions': list(jpeg_dimensions(effective)), 'actual_mime': 'image/jpeg',
                },
                'canonical_authority': {
                    'archive_member': canonical_member, 'bytes': len(canonical_raw),
                    'sha256': sha(canonical_raw), 'git_blob_sha1': git_blob(canonical_raw),
                    'dimensions': list(jpeg_dimensions(canonical_raw)),
                    'retained_as_effective_source': not is_override,
                },
                'indonesian_release_override': {
                    'archive_member': override_member, 'present': is_override,
                    'sha256': sha(effective) if is_override else None,
                },
                'derivative_required': fixture['derivative_required'], 'outputs': outputs,
            })

    assert {row['effective_source']['sha256'] for row in assets if row['indonesian_release_override']['present']} == set(ID_OVERRIDES.values())
    manifest = {
        'schema': 'jv-unit-assets-v1', 'unit': UNIT,
        'status': 'deterministic_asset_preparation_static_visual_review_pending',
        'source_commit': UPSTREAM_COMMIT, 'rules_sha256': RULES_SHA256,
        'indonesian_release_manifest_sha256': ID_MANIFEST_SHA256,
        'canonical_media_manifest_sha256': AUTHORITY_SHA256,
        'resolution_order': 'Pinned Indonesian translated/media override first; canonical authority only when absent.',
        'assets': assets,
        'decisions': [
            '012b and 013b use exact pinned Indonesian release bytes. Their different canonical English bytes remain separately recorded and are never substituted.',
            'Fourteen media retain canonical authority bytes because the Indonesian release contains no override for those exact names.',
            'All effective source bytes are JPEG. Reader delivery uses truthful per-output MIME while CNXML source declarations remain untouched.',
            'Only five retained-English instruction labels receive Javanese SVG derivatives. Literal x/equality/value order and the highlighted replacement number are preserved.',
            'The compact SVGs are language-aware semantic redraws, not pixel-identical edits or human visual approval.',
            'No image generation provider, speech provider, synthesis, network acquisition or broad archive extraction is used.',
        ],
        'synthesized_audio_files': 0, 'whole_module_complete': False,
    }
    generated[f'translation/{UNIT}.assets.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode()
    return generated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    generated = products()
    assert generated == products()
    for path, raw in generated.items():
        if args.check:
            assert (LANG / path).read_bytes() == raw, path
        else:
            write_bytes(LANG / path, raw)
    print('Evaluation assets verified: 16 effective JPEGs, 10 Javanese label SVGs; no synthesis or human visual approval.')


if __name__ == '__main__':
    main()
