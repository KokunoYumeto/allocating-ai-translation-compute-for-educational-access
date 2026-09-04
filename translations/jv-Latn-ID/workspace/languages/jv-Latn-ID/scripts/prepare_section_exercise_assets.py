"""Prepare all five exact end-exercise media from pinned sources.

Four numeric model JPEGs are retained byte-for-byte. The self-check SVG changes
only its registered title/description/text nodes and root language; geometry and
all eighteen blank response cells remain unchanged. No learner choice is added.
"""
import argparse
import json
import xml.etree.ElementTree as ET

from config import LANG, UPSTREAM_COMMIT
from prepare_digit_place_assets import A00_COMMIT, XML_LANG, geometry_signature, git, pinned_blob, sha256, text_nodes
from safe_io import write_bytes

UNIT = 'a00-section-exercises'
OUT = f'translation/assets/{UNIT}/'
RULES_SHA = '3515f1383f855c7174d1d1ea52e732e8bea1767908e688d2c42f3589b1d9750c'
RASTERS = [
    ('fs-id1393361', 'CNX_BMath_Figure_01_01_201_img.jpg', '157ec2d1aea653a81b9d308e7dacd34b42a03891'),
    ('fs-id1284927', 'CNX_BMath_Figure_01_01_202_img.jpg', '317eed443d55a93272fa54b143e762cae19988cc'),
    ('fs-id2675330', 'CNX_BMath_Figure_01_01_203_img.jpg', '326c0fda6527b6d573a76bb72e5dbdc0197c1af8'),
    ('fs-id2716627', 'CNX_BMath_Figure_01_01_204_img.jpg', '7f325be62a618e385f3caa0fb021a033eb188af1'),
]
SVG_NAME = 'CNX_BMath_Figure_AppB_001.jpg.id-ID.svg'
SVG_BLOB = '001819d8d3a35cc7bdbe8f45bc46b9daae97872a'
SVG_TEXT = {
    'jv-academic': [
        'Pambiji dhiri babagan wilangan cacah lan nilai panggonan',
        'Dhaptar enem katrampilan kanthi pilihan Yakin, Kanthi pitulungan, utawa Ora, aku durung mangerteni.',
        'Aku bisa…', 'Yakin', 'Kanthi', 'pitulungan', 'Ora, aku', 'durung', 'mangerteni',
        'ngenali wilangan asli lan wilangan cacah.', 'nggawe model wilangan cacah.',
        'ngenali nilai panggonan sawijining digit.',
        'nggunakake nilai panggonan kanggo nyebutake wilangan cacah.',
        'nggunakake nilai panggonan kanggo nulis wilangan cacah.', 'mbunderake wilangan cacah.',
    ],
    'jv-conversation': [
        'Mbiji pangertenmu babagan wilangan cacah lan nilai panggonan',
        'Dhaptar enem katrampilan kanthi pilihan Yakin, Nganggo pitulungan, utawa Ora, aku durung ngerti.',
        'Aku bisa…', 'Yakin', 'Nganggo', 'pitulungan', 'Ora, aku', 'durung', 'ngerti',
        'ngenali wilangan asli lan wilangan cacah.', 'nggawe model wilangan cacah.',
        'ngenali nilai panggonane saben digit.',
        'nganggo nilai panggonan kanggo nyebut wilangan cacah.',
        'nganggo nilai panggonan kanggo nulis wilangan cacah.', 'mbunderake wilangan cacah.',
    ],
}


def localized_svg(source, track):
    nodes = text_nodes(source)
    assert [node.text for node in nodes] == [
        'Penilaian diri bilangan cacah dan nilai tempat',
        'Daftar enam keterampilan dengan pilihan Yakin, Dengan bantuan, atau Tidak—saya belum memahaminya.',
        'Saya dapat…', 'Yakin', 'Dengan', 'bantuan', 'Tidak—saya', 'belum', 'memahaminya!',
        'mengidentifikasi bilangan asli dan bilangan cacah.', 'memodelkan bilangan cacah.',
        'mengidentifikasi nilai tempat suatu digit.',
        'menggunakan nilai tempat untuk menamai bilangan cacah.',
        'menggunakan nilai tempat untuk menuliskan bilangan cacah.', 'membulatkan bilangan cacah.',
    ]
    assert len(nodes) == len(SVG_TEXT[track]) == 15
    root = ET.fromstring(source)
    root.set(XML_LANG, 'jv-Latn-ID')
    for node, value in zip([n for n in root.iter() if n.tag.rsplit('}', 1)[-1] in ('title', 'desc', 'text')], SVG_TEXT[track]):
        node.text = value
    raw = ET.tostring(root, encoding='utf-8', xml_declaration=True) + b'\n'
    assert geometry_signature(source) == geometry_signature(raw)
    return raw


def products():
    rules_raw = (LANG / f'audio/{UNIT}.rules.json').read_bytes()
    assert sha256(rules_raw) == RULES_SHA
    rules = json.loads(rules_raw)
    charts = {row['media_id']: row for row in rules['chart_fixtures']}
    assert len(charts) == 5
    files, assets = {}, []
    for media_id, name, oid in RASTERS:
        source = pinned_blob('a00-id', A00_COMMIT, 'media/' + name, oid)
        chart = charts[media_id]
        assert sha256(source) == chart['source_asset_sha256'] and len(source) == chart['source_asset_bytes']
        assert source.startswith(b'\xff\xd8')
        assert git('openstax-prealgebra-bundle', 'rev-parse', UPSTREAM_COMMIT + ':media/' + name).decode().strip() == oid
        path = OUT + name
        files[path] = source
        outputs = {track: {'path': path, 'sha256': sha256(source), 'mime_type': 'image/jpeg'}
                   for track in ('id-academic', 'jv-academic', 'jv-conversation')}
        assets.append({'media_id': media_id, 'source_src': chart['source_src'],
                       'source_sha256': sha256(source), 'source_git_blob_sha1': oid,
                       'mime_type': 'image/jpeg', 'role': chart['role'],
                       'block_counts': chart['block_counts'], 'outputs': outputs})
    source = pinned_blob('a00-id', A00_COMMIT, 'media/' + SVG_NAME, SVG_BLOB)
    chart = charts['eip-id1165721974707']
    assert sha256(source) == chart['source_asset_sha256'] and len(source) == chart['source_asset_bytes']
    id_path = OUT + SVG_NAME
    files[id_path] = source
    outputs = {'id-academic': {'path': id_path, 'sha256': sha256(source), 'mime_type': 'image/svg+xml'}}
    for track in ('jv-academic', 'jv-conversation'):
        raw = localized_svg(source, track)
        path = OUT + SVG_NAME.replace('.id-ID.svg', f'.{track}.svg')
        files[path] = raw
        outputs[track] = {'path': path, 'sha256': sha256(raw), 'mime_type': 'image/svg+xml'}
    canonical_name = SVG_NAME.removesuffix('.id-ID.svg')
    canonical_oid = 'e07f7f9383088a27bd7a867aa47cec7855a27d2d'
    canonical = pinned_blob('a00-id', A00_COMMIT, 'media/' + canonical_name, canonical_oid)
    assert git('openstax-prealgebra-bundle', 'rev-parse', UPSTREAM_COMMIT + ':media/' + canonical_name).decode().strip() == canonical_oid
    assets.append({'media_id': chart['media_id'], 'source_src': chart['source_src'],
                   'source_sha256': sha256(source), 'source_git_blob_sha1': SVG_BLOB,
                   'canonical_original': {'path': 'media/' + canonical_name, 'git_blob_sha1': canonical_oid,
                                          'sha256': sha256(canonical), 'mime_type': 'image/jpeg'},
                   'mime_type': 'image/svg+xml', 'role': chart['role'],
                   'logical_shape': chart['logical_shape'], 'outputs': outputs})
    manifest = {
        'schema': 'jv-section-exercise-assets-v1', 'unit': UNIT, 'module': 'm81243',
        'section': 'fs-id2279009', 'rules_sha256': RULES_SHA,
        'scope': 'All five section media: four unchanged numeric JPEGs and one text-only localized self-check SVG.',
        'source_review': 'Root viewed all four exact model JPEGs and the separate canonical English self-check raster; read the complete actual ID SVG XML.',
        'visual_derivative_review': 'Root rendered and inspected both localized self-check SVG variants at 96 density on white. All six rows, three headers, eighteen empty cells and labels are visible without observed clipping. Standalone evidence only; no integrated-browser claim.',
        'human_review': False, 'assets': assets,
    }
    files[f'translation/{UNIT}.assets.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode()
    return files


def verify_saved(generated=None):
    generated = products() if generated is None else generated
    for name, raw in generated.items():
        assert (LANG / name).read_bytes() == raw, name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    generated = products()
    assert generated == products()
    if args.check:
        verify_saved(generated)
    else:
        for name, raw in generated.items():
            write_bytes(LANG / name, raw)
    print('Prepared four retained JPEGs and three self-check SVGs; standalone target render review recorded.')


if __name__ == '__main__':
    main()
