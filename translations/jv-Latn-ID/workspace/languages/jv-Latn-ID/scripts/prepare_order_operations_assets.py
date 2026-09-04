"""Materialize the 23 exact, numeric-only order-of-operations JPEG assets."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import struct
import zipfile

from config import LANG, ROOT
from order_operations_checks import TRACKS, UNIT, load_rules, sha, source_sections
from safe_io import write_bytes

OUT = f'translation/assets/{UNIT}/'
PINNED_ARCHIVE = ROOT / 'downloads/jv-Latn-ID/openstax-full-pinned.zip'
A10_ARCHIVE = ROOT / 'downloads/jv-Latn-ID/a10-source.zip'
PINNED_COMMIT = '38cae454e644abf9f0a623e876994553881597c9'
MEDIA_MANIFEST_SHA256 = '3b8478b77c8860363b7000cbffa68782320e73458289bdcda957acf1b971210f'


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def jpeg_dimensions(raw: bytes) -> tuple[int, int]:
    """Read SOF geometry without decoding or altering source pixels."""
    if not raw.startswith(b'\xff\xd8'):
        raise ValueError('Asset is not a JPEG')
    offset = 2
    sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    while offset < len(raw):
        while offset < len(raw) and raw[offset] == 0xFF:
            offset += 1
        if offset >= len(raw):
            break
        marker = raw[offset]
        offset += 1
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            continue
        if offset + 2 > len(raw):
            break
        length = struct.unpack('>H', raw[offset:offset + 2])[0]
        if length < 2 or offset + length > len(raw):
            raise ValueError('Malformed JPEG segment')
        if marker in sof:
            if length < 7:
                raise ValueError('Malformed JPEG SOF segment')
            height, width = struct.unpack('>HH', raw[offset + 3:offset + 7])
            return width, height
        offset += length
    raise ValueError('JPEG has no supported SOF geometry')


def asset_products() -> dict[str, bytes]:
    rules = load_rules()
    source, _ = source_sections()
    nodes = {node.get('id'): node for node in source.iter() if node.get('id')}
    with zipfile.ZipFile(A10_ARCHIVE) as archive:
        authority_raw = archive.read('authority/MEDIA_AUTHORITY_MANIFEST.csv')
    assert sha(authority_raw) == MEDIA_MANIFEST_SHA256 == rules['asset_binding']['source_media_manifest_sha256']
    authority = {row['relative_path']: row for row in csv.DictReader(io.StringIO(authority_raw.decode('utf-8')))}

    generated: dict[str, bytes] = {}
    records = []
    prefix = f'osbooks-prealgebra-bundle-{PINNED_COMMIT}/media/'
    with zipfile.ZipFile(PINNED_ARCHIVE) as archive:
        for chart in rules['chart_fixtures']:
            primary = chart['primary_asset']
            filename = primary['filename']
            media = nodes[chart['media_id']]
            image = media.find('{*}image')
            assert image.get('src') == chart['source_image'] == '../../media/' + filename
            assert image.get('mime-type') == 'image/png'
            authority_row = authority['media/' + filename]
            assert (int(authority_row['bytes']), authority_row['sha256'], authority_row['git_blob_sha1']) == (
                primary['bytes'], primary['sha256'], primary['git_blob_sha1'])
            raw = archive.read(prefix + filename)
            assert len(raw) == primary['bytes'] and sha(raw) == primary['sha256']
            assert git_blob(raw) == primary['git_blob_sha1']
            assert list(jpeg_dimensions(raw)) == primary['dimensions']
            path = OUT + filename
            generated[path] = raw
            outputs = {track: {'path': path, 'sha256': primary['sha256'], 'mime_type': 'image/jpeg'}
                       for track in TRACKS}
            records.append({
                'fixture_id': chart['id'], 'source_media_id': chart['media_id'],
                'source_src': chart['source_image'], 'source_declared_mime': 'image/png',
                'source_actual_mime': 'image/jpeg', 'source_bytes': primary['bytes'],
                'source_sha256': primary['sha256'], 'source_git_blob_sha1': primary['git_blob_sha1'],
                'dimensions': primary['dimensions'], 'linguistic_labels_present': False,
                'derivative_required': False, 'outputs': outputs,
            })
    assert len(generated) == len(records) == 23 and len({row['source_media_id'] for row in records}) == 23
    manifest = {
        'schema': 'jv-order-operations-assets-v1', 'unit': UNIT,
        'status': 'byte_exact_source_assets_materialized_native_visual_review_pending',
        'source_commit': PINNED_COMMIT, 'source_archive': rules['asset_binding']['source_archive_path'],
        'source_media_manifest_sha256': MEDIA_MANIFEST_SHA256, 'assets': records,
        'decisions': [
            'All 23 source images contain numeric notation only; there are no linguistic image labels and no derivative is authorized or needed.',
            'The source CNXML image/png declarations remain unchanged; delivery uses image/jpeg because every byte-pinned file is JPEG.',
            'The same byte-exact JPEG is used in all three tracks; no pixels, geometry, operators, brackets, colors, or order are changed.',
            'Six Javanese alt/aria corrections remain textual CNXML changes bound separately to exact elements, attributes, source keys, target values, and these image hashes.',
            'Materialization and hash checks do not claim human visual, screen-reader, classroom, or assistive-technology approval.',
        ],
        'provider_calls': 0, 'generated_derivatives': 0, 'synthesized_audio_files': 0,
        'human_visual_review': False, 'assistive_technology_review': False,
    }
    generated[f'translation/{UNIT}.assets.json'] = (
        json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode()
    return generated


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    arguments = parser.parse_args()
    generated = asset_products()
    assert generated == asset_products(), 'Nondeterministic order-of-operations asset materialization'
    for path, raw in generated.items():
        if arguments.check:
            assert (LANG / path).read_bytes() == raw, f'Stale order-of-operations asset: {path}'
        else:
            write_bytes(LANG / path, raw)
    print('23 byte-exact order-of-operations JPEGs and their finite manifest verified; human visual review pending.')


if __name__ == '__main__':
    main()
