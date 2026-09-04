"""Prepare the complete pinned m81268 media layer without network access.

The Indonesian and canonical English modules contain 44 corresponding media
elements.  Thirty-nine media objects are byte-identical and are retained for
all tracks.  Five inherited Indonesian localizations stay exact for the
Indonesian track and receive ten narrowly registered Javanese SVG derivatives.
Seven accessibility repairs are bound to the exact source element, old surface,
module digest and either source-asset or source-tree digest.
"""
import argparse
import base64
import copy
import hashlib
import html
import json
from pathlib import PurePosixPath
import re
import struct
import xml.etree.ElementTree as ET

from config import LANG, TRACKS, UPSTREAM_COMMIT
from prepare_name_whole_assets import A00_COMMIT, blob_sha1, git, sha256
from safe_io import write_bytes


UNIT = 'a00-use-algebra'
MODULE = 'm81268'
OUT = f'translation/assets/{UNIT}/'
MANIFEST = f'translation/{UNIT}.assets.json'
EDITS = f'translation/{UNIT}.edits.json'
SOURCE_MODULE_PATH = f'modules/{MODULE}/index.cnxml'
SOURCE_MODULE_BLOB = '90f2418a98a724e513acb8da81199bba2dc71dd6'
SOURCE_MODULE_SHA256 = '6fc5288d96f74128429a8bdcacb4cd94bb1a07182729dc23c30af37204a76222'
ENGLISH_MODULE_BLOB = '5aee0d8b5b9500d04c72947abddf4bcc349d12e4'
ENGLISH_MODULE_SHA256 = '7a46eec9084976ca082e71f10f4cad97f2ba231d7b390e27753a21efb530bf87'
EDITS_SHA256 = '99a688f1eb0f696637ec91149ab25da06f6cbc0937addc0864092984f26e2121'
CANON_LOCK_SHA256 = '396bc9db6ce9f8ab06e0366cf8f525f68e403afa567a7235bea1ea611c006c76'
PRIOR_NINE_FIELD_MEDIA_DIGEST = 'ce8c8939a515ba1288609b2c589506fb1dfbb31bfc61d84b5f2ad9a5b6f747ae'
SVG_NS = 'http://www.w3.org/2000/svg'
SVG = '{' + SVG_NS + '}'
XML_LANG = '{http://www.w3.org/XML/1998/namespace}lang'
ET.register_namespace('', SVG_NS)

LOCALIZED_IDS = (
    'fs-id1495317',
    'fs-id2149605',
    'fs-id2284773',
    'eip-id1168266330736',
    'eip-id1164269481313',
)

EXPECTED_LOCALIZED = {
    'fs-id1495317': {
        'source_ref': '../../media/CNX_BMath_Figure_02_01_003_id.png',
        'canonical_ref': '../../media/CNX_BMath_Figure_02_01_003.jpg',
        'source_sha256': '9ef4f4d9a5543683108dccb81f0a7a87838d9d5e1d8ecabf82d3ec271e6a17f2',
        'canonical_sha256': '81f7103397afbc78b766dd95d227010a6d3df89fe874d81fd9366d1fe68ce0b3',
        'kind': 'embedded-exact-png-with-registered-cell-overlays',
    },
    'fs-id2149605': {
        'source_ref': '../../media/CNX_BMath_Figure_02_01_003_img_id.svg',
        'canonical_ref': '../../media/CNX_BMath_Figure_02_01_003_img.jpg',
        'source_sha256': 'e9ad9856de9aefee930f2c7979afece0e578352f369b2cdd507cb3d069920623',
        'canonical_sha256': '7dc7475e67b77961ee18a9cf83d43f90a89c337d4ab95d6da8a5fccc6dc51597',
        'kind': 'registered-text-only-svg-localization',
    },
    'fs-id2284773': {
        'source_ref': '../../media/CNX_BMath_Figure_02_01_010_img_id.svg',
        'canonical_ref': '../../media/CNX_BMath_Figure_02_01_010_img.jpg',
        'source_sha256': '7d40e31c0228732b63b25d9cc25d4a2581ce5837d296df71ec51d2e9f31f0213',
        'canonical_sha256': '7ab18908c96626a006646dcd12a2c9f865bd7786814b099f8db6946801d61fc1',
        'kind': 'registered-text-only-svg-localization',
    },
    'eip-id1168266330736': {
        'source_ref': '../../media/CNX_BMath_Figure_02_01_020_img_id.svg',
        'canonical_ref': '../../media/CNX_BMath_Figure_02_01_020_img.jpg',
        'source_sha256': 'd5df434a4087f50e3ec688cf57280eb3af1ed5f478f229824720cb3825c8da5a',
        'canonical_sha256': '91aae6f52410caa82159fc77778d5919a94b95e28ea2563189929272f0cd2827',
        'kind': 'registered-text-only-svg-localization',
    },
    'eip-id1164269481313': {
        'source_ref': '../../media/CNX_BMath_Figure_AppB_007_id.svg',
        'canonical_ref': '../../media/CNX_BMath_Figure_AppB_007.jpg',
        'source_sha256': '376222e2eb1ab72329364ff837172108c9f4b9ba29105e76a6a59b400953a81a',
        'canonical_sha256': '05fb64db457a3e1820214999e50771c3dd89d7847eafc661cc7c6aed4b2dc5c9',
        'kind': 'registered-text-only-svg-localization',
    },
}

SVG_SUBSTITUTIONS = {
    'fs-id2149605': {
        'jv-academic': {
            'Basis dan eksponen': 'Basis lan eksponen',
            'Pada bentuk dua pangkat tiga, dua adalah basis dan tiga adalah eksponen.':
                'Ing wujud loro pangkat telu, loro yaiku basis lan telu yaiku eksponen.',
            'basis': 'basis', 'eksponen': 'eksponen',
        },
        'jv-conversation': {
            'Basis dan eksponen': 'Basis lan eksponen',
            'Pada bentuk dua pangkat tiga, dua adalah basis dan tiga adalah eksponen.':
                'Ing wujud loro pangkat telu, loro kuwi basis lan telu kuwi eksponen.',
            'basis': 'basis', 'eksponen': 'eksponen',
        },
    },
    'fs-id2284773': {
        'jv-academic': {
            'Notasi eksponen': 'Notasi eksponen',
            'Pada a pangkat n, a adalah basis dan n adalah eksponen. Bentuk itu sama dengan hasil kali n faktor a.':
                'Ing a pangkat n, a yaiku basis lan n yaiku eksponen. Wujud iku padha karo asil ping-pingan n faktor a.',
            'basis': 'basis', 'eksponen': 'eksponen', 'n faktor': 'n faktor',
        },
        'jv-conversation': {
            'Notasi eksponen': 'Notasi eksponen',
            'Pada a pangkat n, a adalah basis dan n adalah eksponen. Bentuk itu sama dengan hasil kali n faktor a.':
                'Ing a pangkat n, a kuwi basis lan n kuwi eksponen. Wujud kuwi padha karo asil ping-pingan n faktor a.',
            'basis': 'basis', 'eksponen': 'eksponen', 'n faktor': 'n faktor',
        },
    },
    'eip-id1168266330736': {
        'jv-academic': {
            'Ringkasan notasi eksponen': 'Ringkesan notasi eksponen',
            'Pada a pangkat n, a adalah basis dan n adalah eksponen. Bentuk itu sama dengan hasil kali n faktor a.':
                'Ing a pangkat n, a yaiku basis lan n yaiku eksponen. Wujud iku padha karo asil ping-pingan n faktor a.',
            'basis': 'basis', 'eksponen': 'eksponen', 'n faktor': 'n faktor',
        },
        'jv-conversation': {
            'Ringkasan notasi eksponen': 'Ringkesan notasi eksponen',
            'Pada a pangkat n, a adalah basis dan n adalah eksponen. Bentuk itu sama dengan hasil kali n faktor a.':
                'Ing a pangkat n, a kuwi basis lan n kuwi eksponen. Wujud kuwi padha karo asil ping-pingan n faktor a.',
            'basis': 'basis', 'eksponen': 'eksponen', 'n faktor': 'n faktor',
        },
    },
    'eip-id1164269481313': {
        'jv-academic': {
            'Daftar periksa penilaian mandiri': 'Dhaptar pamriksaan mandhiri',
            'Empat tujuan pembelajaran dapat dinilai dengan pilihan dengan yakin, dengan sedikit bantuan, atau belum mengerti.':
                'Patang ancas piwulang bisa dibiji nganggo pilihan kanthi yakin, kanthi pitulungan sithik, utawa durung mangerteni.',
            'Saya dapat…': 'Aku bisa…', 'Dengan yakin': 'Kanthi yakin',
            'Dengan sedikit': 'Kanthi pitulungan', 'bantuan': 'sithik',
            'Tidak—saya tidak': 'Ora—aku ora', 'mengerti': 'mangerteni',
            'menggunakan variabel dan simbol aljabar.': 'nggunakake variabel lan simbol aljabar.',
            'mengidentifikasi ekspresi dan persamaan.': 'ngenali ekspresi lan persamaan.',
            'menyederhanakan ekspresi dengan eksponen.': 'nggawe ekspresi mawa eksponen luwih prasaja.',
            'menyederhanakan ekspresi': 'nggawe ekspresi luwih prasaja',
            'menggunakan urutan operasi.': 'nganggo urutan operasi.',
        },
        'jv-conversation': {
            'Daftar periksa penilaian mandiri': 'Dhaptar kanggo mriksa awake dhewe',
            'Empat tujuan pembelajaran dapat dinilai dengan pilihan dengan yakin, dengan sedikit bantuan, atau belum mengerti.':
                'Patang ancas sinau bisa dipriksa nganggo pilihan yakin, nganggo pitulungan sithik, utawa durung ngerti.',
            'Saya dapat…': 'Aku bisa…', 'Dengan yakin': 'Yakin',
            'Dengan sedikit': 'Nganggo pitulungan', 'bantuan': 'sithik',
            'Tidak—saya tidak': 'Ora—aku ora', 'mengerti': 'ngerti',
            'menggunakan variabel dan simbol aljabar.': 'nganggo variabel lan tandha aljabar.',
            'mengidentifikasi ekspresi dan persamaan.': 'ngenali wujud aljabar lan persamaan.',
            'menyederhanakan ekspresi dengan eksponen.': 'nggawe wujud mawa eksponen luwih prasaja.',
            'menyederhanakan ekspresi': 'nggawe wujud luwih prasaja',
            'menggunakan urutan operasi.': 'nganggo urutan ngetung.',
        },
    },
}

INVARIANT_SVG_TEXT = {
    'fs-id2149605': ['2', '3'],
    'fs-id2284773': ['a', 'n', 'a', 'n', ' = a · a · a · … · a'],
    'eip-id1168266330736': ['a', 'n', 'a', 'n', ' = a · a · a · … · a'],
    'eip-id1164269481313': [],
}

FUEL_LABELS = {
    'jv-academic': ['Mobil', 'Efisiensi bahan', 'bakar (mpg)'],
    'jv-conversation': ['Montor', 'Irite bahan', 'bakar (mpg)'],
}

CORRECTION_SPECS = [
    (174, 'fs-id1495317', 'media', 'alt', 'asset-sha256'),
    (394, 'eip-id1164752720032', 'media', 'alt', 'asset-sha256'),
    (398, 'eip-id1164752720113', 'media', 'alt', 'asset-sha256'),
    (380, 'eip-id1164754514704', 'table', 'aria-label', 'element-c14n-sha256'),
    (490, 'fs-id2757058', 'table', 'aria-label', 'element-c14n-sha256'),
    (514, 'fs-id2935762', 'table', 'aria-label', 'element-c14n-sha256'),
    (536, 'eip-id1164269481313', 'media', 'alt', 'asset-sha256'),
]

EXPONENT_ROW_TARGETS = {
    'jv-academic': (
        'Tabel iki nuduhake ekspresi papat ditambah telu ing njero tandha kurung, banjur dipingake pitu. '
        'Apa ana tandha kurung? ya; gawea luwih prasaja isi tandha kurung kanthi nggunggung papat lan telu '
        'mula dipikolehi pitu. Ekspresi saiki dadi pitu ping pitu. Apa ana eksponen? ora. Apa ana '
        'ping-pingan utawa paran? ya; pingna pitu kanthi pitu kanggo entuk patang puluh sanga.'
    ),
    'jv-conversation': (
        'Tabel iki nuduhake wujud aljabar papat ditambah telu ing njero tandha kurung, banjur dipingake pitu. '
        'Apa ana tandha kurung? ya; gawea luwih prasaja isi tandha kurung nganggo nggunggung papat lan telu '
        'mula dipikolehi pitu. Wujud aljabar saiki dadi pitu ping pitu. Apa ana eksponen? ora. Apa ana '
        'ping-pingan utawa paran? ya; pingna pitu nganggo pitu kanggo entuk patang puluh sanga.'
    ),
}

RENDER_REVIEW = {
    'status': 'completed',
    'renderer': 'ImageMagick 7.1.2-26 Q16-HDRI x64 38ba210:20260621; explicit RSVG/librsvg 2.40.20',
    'arguments': ['-background', 'white', '-density', '96', 'RSVG:<absolute SVG path>',
                  '-alpha', 'remove', '-alpha', 'off', '<temporary PNG path>'],
    'outputs': [
        {'path': OUT + 'CNX_BMath_Figure_02_01_003_id.jv-academic.svg',
         'svg_sha256': '394aa27a9726b379359fc0c974e129c947d41b7c646584a9a8130507b20f298b',
         'rendered_geometry': '632x117',
         'temporary_png_sha256': '901feac6e343b5ddcf75f81fe0c7e250828922618f97b5f901c6ba0d7cd3f32b',
         'inspected': True},
        {'path': OUT + 'CNX_BMath_Figure_02_01_003_id.jv-conversation.svg',
         'svg_sha256': 'b4d562cd8babfdcb4291739d4a178a5ae5517576c9fc013da6f02568f6966c8f',
         'rendered_geometry': '632x117',
         'temporary_png_sha256': '7040ee982947e6efbb3b8ede39a391965a672d00359baf24824616ad492dc505',
         'inspected': True},
        {'path': OUT + 'CNX_BMath_Figure_02_01_003_img_id.jv-academic.svg',
         'svg_sha256': '145546859f8201b712bd80db040964b2ad7a8a579d24709e56780dab2747f7bb',
         'rendered_geometry': '220x26',
         'temporary_png_sha256': 'd7790894620c2f63c8858832159f5bd30c5dfabbd63fe9864d263464fc773b48',
         'inspected': True},
        {'path': OUT + 'CNX_BMath_Figure_02_01_003_img_id.jv-conversation.svg',
         'svg_sha256': 'bf058c75862dcdb86af0d5add1bb2137265aa7ac008b893f4af7f48931fd8a7f',
         'rendered_geometry': '220x26',
         'temporary_png_sha256': 'd7790894620c2f63c8858832159f5bd30c5dfabbd63fe9864d263464fc773b48',
         'inspected': True},
        {'path': OUT + 'CNX_BMath_Figure_02_01_010_img_id.jv-academic.svg',
         'svg_sha256': '38a81375d7e465ea02060c6554e1941576a3256674bb4c1a9d3b42dec34d8e59',
         'rendered_geometry': '224x104',
         'temporary_png_sha256': 'bfad66d7a31ce2a2dd603fc415cbf5c4b3f483dcef76700831162931075a323a',
         'inspected': True},
        {'path': OUT + 'CNX_BMath_Figure_02_01_010_img_id.jv-conversation.svg',
         'svg_sha256': 'f6cf564060ca82cd1355797c2573a22875f54d0df2f3978a9d98ee97a36ca404',
         'rendered_geometry': '224x104',
         'temporary_png_sha256': '4da7229bb4ef7121b253c9a8bafbac843bc191e427ff203a1315d28ea7ac2da9',
         'inspected': True},
        {'path': OUT + 'CNX_BMath_Figure_02_01_020_img_id.jv-academic.svg',
         'svg_sha256': '15302d3879803381f4d986dff80c84e755f6f04ab82a4846d109ef6b4c83c5f3',
         'rendered_geometry': '221x100',
         'temporary_png_sha256': 'd065d0ec39f282eb3902de0ad293ddcc4352ba3ecc032458827b6e89bee2df62',
         'inspected': True},
        {'path': OUT + 'CNX_BMath_Figure_02_01_020_img_id.jv-conversation.svg',
         'svg_sha256': '3a4189344daa006967e31f5c76534ffca97c2aa8a1f873d25f76ec641c3b61bd',
         'rendered_geometry': '221x100',
         'temporary_png_sha256': 'd065d0ec39f282eb3902de0ad293ddcc4352ba3ecc032458827b6e89bee2df62',
         'inspected': True},
        {'path': OUT + 'CNX_BMath_Figure_AppB_007_id.jv-academic.svg',
         'svg_sha256': '886fa8021ccf172dd6399ea7fa6dfe706ccdf6161aa70f962a41d358d3fc2d27',
         'rendered_geometry': '632x172',
         'temporary_png_sha256': 'a9df0fd86da20f12d47d4599ac11a41150cc4e1558cc5f4ce6bedf81f73a1c14',
         'inspected': True},
        {'path': OUT + 'CNX_BMath_Figure_AppB_007_id.jv-conversation.svg',
         'svg_sha256': 'a6bff9dfbdfe1d57b212c3025b3a035513c8e33e0009b60baa4ede6acc50de74',
         'rendered_geometry': '632x172',
         'temporary_png_sha256': '41fa404d6627623bd3adc5cd5bb59b7f99049fc2b1dca8d10a23c6d1e5feec95',
         'inspected': True},
    ],
    'observation': (
        'All ten final derivatives were rendered and opened at native output size. The fuel-table '
        'cars, values and grid remain visible beyond the two covered label cells; exponent arrows, '
        'formulae and braces remain intact; all self-check headings, objectives and blank response '
        'cells remain legible. No clipping, overlap, missing embedded raster or geometry drift was observed. '
        'Pixel-identical renders are expected where register differences occur only in nonvisual SVG descriptions.'
    ),
    'scope': (
        'Static standalone SVG clipping, overlap, embedded-raster and diagram-structure review only; '
        'not integrated-reader, browser, screen-reader, native-language, pronunciation or listening approval.'
    ),
}


def local_name(node):
    return node.tag.rsplit('}', 1)[-1]


def c14n(node):
    raw = ET.tostring(node, encoding='unicode')
    return ET.canonicalize(raw, strip_text=False, rewrite_prefixes=True)


def utf8_sha(value):
    return sha256(value.encode('utf-8'))


def pinned_repo_blob(repo, commit, path):
    oid = git(repo, 'rev-parse', f'{commit}:{path}').decode('ascii').strip()
    raw = git(repo, 'show', f'{commit}:{path}')
    if blob_sha1(raw) != oid:
        raise ValueError('Pinned Git object mismatch: ' + repo + ':' + path)
    return raw, oid


def image_info(raw):
    if raw.startswith(b'\x89PNG\r\n\x1a\n'):
        if raw[12:16] != b'IHDR':
            raise ValueError('PNG missing IHDR')
        width, height = struct.unpack('>II', raw[16:24])
        return 'image/png', 'PNG', width, height
    if raw.startswith(b'\xff\xd8'):
        position = 2
        sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
               0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
        while position < len(raw):
            while position < len(raw) and raw[position] != 0xFF:
                position += 1
            while position < len(raw) and raw[position] == 0xFF:
                position += 1
            if position >= len(raw):
                break
            marker = raw[position]
            position += 1
            if marker in (0x01, *range(0xD0, 0xD9)):
                continue
            if position + 2 > len(raw):
                raise ValueError('Truncated JPEG segment')
            length = int.from_bytes(raw[position:position + 2], 'big')
            if length < 2 or position + length > len(raw):
                raise ValueError('Invalid JPEG segment')
            if marker in sof:
                height = int.from_bytes(raw[position + 3:position + 5], 'big')
                width = int.from_bytes(raw[position + 5:position + 7], 'big')
                return 'image/jpeg', 'JPEG', width, height
            position += length
        raise ValueError('JPEG has no supported SOF marker')
    root = ET.fromstring(raw)
    if root.tag != SVG + 'svg':
        raise ValueError('Unregistered image type')
    width = int(float(re.sub(r'[^0-9.]', '', root.get('width'))))
    height = int(float(re.sub(r'[^0-9.]', '', root.get('height'))))
    return 'image/svg+xml', 'SVG', width, height


def media_nodes(root):
    return [node for node in root.iter() if local_name(node) == 'media']


def media_image(node):
    images = [child for child in node if local_name(child) == 'image']
    if len(images) != 1:
        raise ValueError('Media must have exactly one direct image child')
    return images[0]


def find_id(root, element_id, expected_tag=None):
    matches = [node for node in root.iter() if node.get('id') == element_id]
    if len(matches) != 1:
        raise ValueError('Expected one source element: ' + element_id)
    node = matches[0]
    if expected_tag and local_name(node) != expected_tag:
        raise ValueError('Unexpected source element type: ' + element_id)
    return node


def geometry_signature(root):
    rows = []
    for node in root.iter():
        attrs = tuple(sorted((key, value) for key, value in node.attrib.items()
                             if key != XML_LANG))
        rows.append((local_name(node), attrs, len(node)))
    return rows


def svg_text_entries(root):
    entries = []
    for ordinal, node in enumerate(root.iter()):
        if local_name(node) in ('title', 'desc', 'text', 'tspan') and node.text and node.text.strip():
            entries.append((ordinal, local_name(node), node.text))
    return entries


def localize_source_svg(raw, media_id, track):
    if media_id not in SVG_SUBSTITUTIONS or track not in ('jv-academic', 'jv-conversation'):
        raise ValueError('Unregistered SVG localization request')
    source = ET.fromstring(raw)
    if source.tag != SVG + 'svg' or source.get(XML_LANG) is not None:
        raise ValueError('Unexpected inherited SVG root')
    substitutions = SVG_SUBSTITUTIONS[media_id][track]
    encountered, invariant = [], []
    target = copy.deepcopy(source)
    for node in target.iter():
        if local_name(node) not in ('title', 'desc', 'text', 'tspan') or not node.text or not node.text.strip():
            continue
        if node.text in substitutions:
            encountered.append(node.text)
            node.text = substitutions[node.text]
        elif node.text in INVARIANT_SVG_TEXT[media_id]:
            invariant.append(node.text)
        else:
            raise ValueError('Unregistered SVG text: ' + repr(node.text))
    if set(encountered) != set(substitutions) or invariant != INVARIANT_SVG_TEXT[media_id]:
        raise ValueError('Incomplete or reordered SVG text registration')
    target.set(XML_LANG, 'jv-Latn-ID')
    if geometry_signature(source) != geometry_signature(target):
        raise ValueError('SVG geometry or attribute mutation')
    source_math = [row for row in svg_text_entries(source) if row[2] in INVARIANT_SVG_TEXT[media_id]]
    target_math = [row for row in svg_text_entries(target) if row[2] in INVARIANT_SVG_TEXT[media_id]]
    if source_math != target_math:
        raise ValueError('SVG math mutation')
    value = ET.tostring(target, encoding='utf-8', xml_declaration=True)
    verify_localized_svg(value, raw, media_id, track)
    return value


def fuel_wrapper(raw, track, media_alt):
    if track not in FUEL_LABELS or sha256(raw) != EXPECTED_LOCALIZED['fs-id1495317']['source_sha256']:
        raise ValueError('Unregistered or mutated fuel source')
    if image_info(raw) != ('image/png', 'PNG', 632, 117):
        raise ValueError('Unexpected fuel raster geometry')
    labels = FUEL_LABELS[track]
    title = 'Tabel efisiensi bahan bakar mobil' if track == 'jv-academic' else 'Tabel irite bahan bakar montor'
    encoded = base64.b64encode(raw).decode('ascii')
    value = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        'xml:lang="jv-Latn-ID" width="632" height="117" '
        'viewBox="0 0 632 117" role="img" aria-labelledby="title desc">\n'
        f'<title id="title">{html.escape(title)}</title>\n'
        f'<desc id="desc">{html.escape(media_alt)}</desc>\n'
        f'<image id="source-raster" x="0" y="0" width="632" height="117" '
        f'href="data:image/png;base64,{encoded}" xlink:href="data:image/png;base64,{encoded}"/>\n'
        '<g id="registered-label-overlays" font-family="Arial, Helvetica, sans-serif" text-anchor="middle" fill="#111">\n'
        '<rect id="top-label-cover" x="1" y="1" width="107" height="79" fill="#a4d3d5"/>\n'
        '<rect id="bottom-label-cover" x="1" y="82" width="107" height="34" fill="#90d4d6"/>\n'
        f'<text id="top-label" x="54" y="36" font-size="13" font-weight="700">{html.escape(labels[0])}</text>\n'
        f'<text id="bottom-label-1" x="54" y="96" font-size="9.5">{html.escape(labels[1])}</text>\n'
        f'<text id="bottom-label-2" x="54" y="108" font-size="9.5">{html.escape(labels[2])}</text>\n'
        '</g>\n</svg>\n'
    ).encode('utf-8')
    verify_fuel_wrapper(value, raw, track, media_alt)
    return value


def verify_localized_svg(value, source_raw, media_id, track):
    source, target = ET.fromstring(source_raw), ET.fromstring(value)
    if target.get(XML_LANG) != 'jv-Latn-ID' or geometry_signature(source) != geometry_signature(target):
        raise ValueError('Localized SVG geometry/language mismatch')
    substitutions = SVG_SUBSTITUTIONS[media_id][track]
    source_entries, target_entries = svg_text_entries(source), svg_text_entries(target)
    if len(source_entries) != len(target_entries):
        raise ValueError('Localized SVG text-node count mismatch')
    for source_row, target_row in zip(source_entries, target_entries):
        expected = substitutions.get(source_row[2], source_row[2])
        if source_row[:2] != target_row[:2] or target_row[2] != expected:
            raise ValueError('Unregistered SVG text mutation')


def verify_fuel_wrapper(value, source_raw, track, media_alt):
    root = ET.fromstring(value)
    if (root.tag, root.get(XML_LANG), root.get('viewBox')) != (SVG + 'svg', 'jv-Latn-ID', '0 0 632 117'):
        raise ValueError('Fuel wrapper geometry/language mismatch')
    by_id = {node.get('id'): node for node in root.iter() if node.get('id')}
    embedded = by_id['source-raster'].get('href')
    prefix = 'data:image/png;base64,'
    if not embedded.startswith(prefix) or base64.b64decode(embedded[len(prefix):]) != source_raw:
        raise ValueError('Fuel wrapper does not embed exact source bytes')
    if by_id['desc'].text != media_alt:
        raise ValueError('Fuel wrapper accessibility surface mismatch')
    labels = [by_id['top-label'].text, by_id['bottom-label-1'].text, by_id['bottom-label-2'].text]
    if labels != FUEL_LABELS[track]:
        raise ValueError('Fuel wrapper label mismatch')
    if [(by_id[name].get('x'), by_id[name].get('y'), by_id[name].get('width'), by_id[name].get('height'))
            for name in ('top-label-cover', 'bottom-label-cover')] != [
                ('1', '1', '107', '79'), ('1', '82', '107', '34')]:
        raise ValueError('Fuel cover escaped registered label cells')


def derive(raw, media_id, track, target_alt):
    if media_id == 'fs-id1495317':
        return fuel_wrapper(raw, track, target_alt)
    return localize_source_svg(raw, media_id, track)


def asset_output(generated, path, raw):
    if path in generated and generated[path] != raw:
        raise ValueError('Output path collision: ' + path)
    generated[path] = raw


def translated_alt(edits, media_id):
    bindings = [row for row in edits['source_key_bindings']
                if row['element_id'] == media_id and row['element'] == 'media' and row['slot'] == 'alt']
    if len(bindings) != 1:
        raise ValueError('Expected one translated media alt: ' + media_id)
    phrase = edits['phrases'][bindings[0]['phrase_index_zero_based']]
    return {'id-academic': phrase[0], 'jv-academic': phrase[1], 'jv-conversation': phrase[2]}


def validate_correction_bindings(source_root, edits, asset_records):
    by_media = {row['media_id']: row for row in asset_records}
    registered = {(row['element_id'], row['slot']) for row in edits['scoped_accessibility_corrections']}
    expected = {(row[1], row[3]) for row in CORRECTION_SPECS}
    if registered != expected or len(registered) != 7:
        raise ValueError('Accessibility correction registration mismatch')
    results = []
    for phrase_index, element_id, tag, slot, scope_kind in CORRECTION_SPECS:
        binding = edits['source_key_bindings'][phrase_index]
        if binding != {
                'phrase_index_zero_based': phrase_index, 'element_id': element_id,
                'element': tag, 'slot': slot}:
            raise ValueError('Accessibility correction binding mismatch')
        phrase = edits['phrases'][phrase_index]
        node = find_id(source_root, element_id, tag)
        if node.get(slot) != phrase[0]:
            raise ValueError('Accessibility old surface no longer matches source')
        element_c14n = c14n(node)
        if scope_kind == 'asset-sha256':
            if element_id not in by_media:
                raise ValueError('Correction has no bound source asset')
            scope_hash = by_media[element_id]['source']['sha256']
            asset_sha = scope_hash
            outputs = {
                track: by_media[element_id]['outputs'][track]['sha256']
                for track in ('jv-academic', 'jv-conversation')
            }
        else:
            scope_hash = utf8_sha(element_c14n)
            asset_sha, outputs = None, None
        targets = {'jv-academic': phrase[1], 'jv-conversation': phrase[2]}
        integration_note = None
        if element_id == 'eip-id1164754514704':
            targets = dict(EXPONENT_ROW_TARGETS)
            if any('Apa ana eksponen? ora.' not in value for value in targets.values()):
                raise ValueError('Missing restored exponent/no row')
            integration_note = (
                'The immutable edit phrase predates the final row-restoration wording. '
                'Root must rebind this exact target-only override; the edit file is intentionally unchanged here.'
            )
        results.append({
            'phrase_index_zero_based': phrase_index,
            'element_id': element_id, 'element': tag, 'slot': slot,
            'old_source_surface': phrase[0],
            'old_source_surface_sha256': utf8_sha(phrase[0]),
            'source_element_c14n': element_c14n,
            'source_element_c14n_sha256': utf8_sha(element_c14n),
            'source_module_sha256': SOURCE_MODULE_SHA256,
            'scope_hash_kind': scope_kind, 'scope_hash': scope_hash,
            'asset_sha256': asset_sha, 'bound_target_output_sha256': outputs,
            'target_surfaces': targets,
            'integration_note': integration_note,
            'fail_closed_scope': [
                'module_sha256', 'element_id', 'element', 'slot',
                'old_source_surface_sha256', scope_kind,
            ],
        })
    return results


def products():
    source_raw, source_module_oid = pinned_repo_blob('a00-id', A00_COMMIT, SOURCE_MODULE_PATH)
    english_raw, english_module_oid = pinned_repo_blob(
        'openstax-prealgebra-bundle', UPSTREAM_COMMIT, SOURCE_MODULE_PATH)
    if (source_module_oid, sha256(source_raw), len(source_raw)) != (
            SOURCE_MODULE_BLOB, SOURCE_MODULE_SHA256, 153454):
        raise ValueError('Indonesian module pin mismatch')
    if (english_module_oid, sha256(english_raw), len(english_raw)) != (
            ENGLISH_MODULE_BLOB, ENGLISH_MODULE_SHA256, 152620):
        raise ValueError('English module pin mismatch')
    source_root, english_root = ET.fromstring(source_raw), ET.fromstring(english_raw)
    source_media, english_media = media_nodes(source_root), media_nodes(english_root)
    if len(source_media) != 44 or [row.get('id') for row in source_media] != [row.get('id') for row in english_media]:
        raise ValueError('Pinned media occurrence/order mismatch')

    edits_raw = (LANG / EDITS).read_bytes()
    if sha256(edits_raw) != EDITS_SHA256:
        raise ValueError('Translation handoff changed before asset binding')
    edits = json.loads(edits_raw)
    if edits['unit'] != UNIT or len(edits['phrases']) != 543:
        raise ValueError('Unexpected translation handoff shape')
    canon_raw = (LANG / 'canon/sources.lock.json').read_bytes()
    if sha256(canon_raw) != CANON_LOCK_SHA256 or len(json.loads(canon_raw)['records']) != 50:
        raise ValueError('Canon checkpoint changed')

    generated, records = {}, []
    localized_seen = []
    source_formats = {'JPEG': 0, 'PNG': 0, 'SVG': 0}
    canonical_formats = {'JPEG': 0, 'PNG': 0, 'SVG': 0}
    for ordinal, (source_node, english_node) in enumerate(zip(source_media, english_media), 1):
        media_id = source_node.get('id')
        source_image, english_image = media_image(source_node), media_image(english_node)
        source_ref, canonical_ref = source_image.get('src'), english_image.get('src')
        if not source_ref.startswith('../../media/') or not canonical_ref.startswith('../../media/'):
            raise ValueError('Media reference escapes pinned media tree')
        source_path = source_ref.removeprefix('../../')
        canonical_path = canonical_ref.removeprefix('../../')
        source_asset, source_oid = pinned_repo_blob('a00-id', A00_COMMIT, source_path)
        canonical_asset, canonical_oid = pinned_repo_blob(
            'openstax-prealgebra-bundle', UPSTREAM_COMMIT, canonical_path)
        source_mime, source_format, width, height = image_info(source_asset)
        canonical_mime, canonical_format, canonical_width, canonical_height = image_info(canonical_asset)
        source_formats[source_format] += 1
        canonical_formats[canonical_format] += 1
        is_localized = media_id in LOCALIZED_IDS
        if is_localized:
            localized_seen.append(media_id)
            expected = EXPECTED_LOCALIZED[media_id]
            if (source_ref, canonical_ref, sha256(source_asset), sha256(canonical_asset)) != (
                    expected['source_ref'], expected['canonical_ref'],
                    expected['source_sha256'], expected['canonical_sha256']):
                raise ValueError('Localized source/canonical binding mismatch: ' + media_id)
            if source_asset == canonical_asset:
                raise ValueError('Localized source unexpectedly canonical-identical')
        elif source_ref != canonical_ref or source_asset != canonical_asset or source_oid != canonical_oid:
            raise ValueError('Unregistered Indonesian media localization: ' + media_id)

        alt = translated_alt(edits, media_id)
        stored_source_path = OUT + PurePosixPath(source_path).name
        asset_output(generated, stored_source_path, source_asset)
        outputs = {
            'id-academic': {
                'path': stored_source_path, 'sha256': sha256(source_asset),
                'bytes': len(source_asset), 'mime_type': source_mime,
                'derivative_type': 'exact-indonesian-source-byte-retention',
            }
        }
        substitutions = []
        for track in ('jv-academic', 'jv-conversation'):
            if is_localized:
                value = derive(source_asset, media_id, track, alt[track])
                path = OUT + PurePosixPath(source_path).stem + f'.{track}.svg'
                asset_output(generated, path, value)
                outputs[track] = {
                    'path': path, 'sha256': sha256(value), 'bytes': len(value),
                    'mime_type': 'image/svg+xml',
                    'derivative_type': EXPECTED_LOCALIZED[media_id]['kind'],
                }
                if media_id == 'fs-id1495317':
                    labels = [{'source': source, 'target': target}
                              for source, target in zip(
                                  ['Mobil', 'Efisiensi bahan bakar', '(mpg)'], FUEL_LABELS[track])]
                else:
                    labels = [{'source': source, 'target': target}
                              for source, target in SVG_SUBSTITUTIONS[media_id][track].items()]
                substitutions.append({'track': track, 'registered_text': labels})
            else:
                outputs[track] = {
                    'path': stored_source_path, 'sha256': sha256(source_asset),
                    'bytes': len(source_asset), 'mime_type': source_mime,
                    'derivative_type': 'exact-indonesian-source-byte-retention',
                }

        source_surface = c14n(source_node)
        canonical_surface = c14n(english_node)
        records.append({
            'ordinal': ordinal, 'media_id': media_id,
            'source_effective_xml': source_surface,
            'source_effective_xml_c14n_sha256': utf8_sha(source_surface),
            'canonical_effective_xml': canonical_surface,
            'canonical_effective_xml_c14n_sha256': utf8_sha(canonical_surface),
            'source_alt': source_node.get('alt'), 'target_alt': alt,
            'source': {
                'repository': 'a00-id', 'commit': A00_COMMIT,
                'ref': source_ref, 'path': source_path,
                'declared_mime_type': source_image.get('mime-type'),
                'actual_mime_type': source_mime, 'format': source_format,
                'bytes': len(source_asset), 'sha256': sha256(source_asset),
                'git_blob_sha1': source_oid,
                'geometry': {'width': width, 'height': height},
            },
            'canonical_english': {
                'repository': 'openstax-prealgebra-bundle', 'commit': UPSTREAM_COMMIT,
                'ref': canonical_ref, 'path': canonical_path,
                'declared_mime_type': english_image.get('mime-type'),
                'actual_mime_type': canonical_mime, 'format': canonical_format,
                'bytes': len(canonical_asset), 'sha256': sha256(canonical_asset),
                'git_blob_sha1': canonical_oid,
                'geometry': {'width': canonical_width, 'height': canonical_height},
            },
            'id_source_equals_canonical_english_bytes': not is_localized,
            'contains_linguistic_pixels': is_localized,
            'registered_substitutions': substitutions,
            'untranslated_visible_source_language_after_target_derivative': False if is_localized else None,
            'technical_source_identical_labels': (
                ['basis', 'eksponen', 'n faktor', 'mpg'] if is_localized else []),
            'credit_id': 'openstax-prealgebra-2e-cc-by-nc-sa-4.0',
            'outputs': outputs,
        })

    if localized_seen != list(LOCALIZED_IDS):
        raise ValueError('Localized media order mismatch')
    if source_formats != {'JPEG': 4, 'PNG': 36, 'SVG': 4}:
        raise ValueError('Unexpected Indonesian media formats')
    if canonical_formats != {'JPEG': 9, 'PNG': 35, 'SVG': 0}:
        raise ValueError('Unexpected canonical media formats')
    if sum(row['id_source_equals_canonical_english_bytes'] for row in records) != 39:
        raise ValueError('Expected 39 canonical-identical media')
    if len(generated) != 54:
        raise ValueError('Expected 44 retained source assets plus ten derivatives')

    corrections = validate_correction_bindings(source_root, edits, records)
    license_raw, license_oid = pinned_repo_blob('a00-id', A00_COMMIT, 'LICENSE')
    canonical_license, canonical_license_oid = pinned_repo_blob(
        'openstax-prealgebra-bundle', UPSTREAM_COMMIT, 'LICENSE')
    if license_raw != canonical_license or license_oid != canonical_license_oid:
        raise ValueError('Inherited license mismatch')
    ordered_binding_digest = sha256(('\n'.join(
        json.dumps({
            'ordinal': row['ordinal'], 'media_id': row['media_id'],
            'source_ref': row['source']['ref'], 'source_blob': row['source']['git_blob_sha1'],
            'source_sha256': row['source']['sha256'],
            'canonical_ref': row['canonical_english']['ref'],
            'canonical_blob': row['canonical_english']['git_blob_sha1'],
            'canonical_sha256': row['canonical_english']['sha256'],
            'source_xml_sha256': row['source_effective_xml_c14n_sha256'],
        }, ensure_ascii=False, sort_keys=True) for row in records) + '\n').encode('utf-8'))
    manifest = {
        'schema': 'jv-use-algebra-assets-v1', 'unit': UNIT, 'module': MODULE,
        'status': 'complete_source_bound_asset_draft_not_reader_integrated',
        'source': {
            'repository': 'a00-id', 'commit': A00_COMMIT, 'path': SOURCE_MODULE_PATH,
            'git_blob_sha1': SOURCE_MODULE_BLOB, 'sha256': SOURCE_MODULE_SHA256,
            'bytes': len(source_raw),
        },
        'canonical_english': {
            'repository': 'openstax-prealgebra-bundle', 'commit': UPSTREAM_COMMIT,
            'path': SOURCE_MODULE_PATH, 'git_blob_sha1': ENGLISH_MODULE_BLOB,
            'sha256': ENGLISH_MODULE_SHA256, 'bytes': len(english_raw),
        },
        'translation_handoff': {'path': EDITS, 'sha256': EDITS_SHA256, 'modified': False},
        'scope': {
            'source_media_occurrences': 44, 'canonical_media_occurrences': 44,
            'source_unique_ids': 44, 'source_unique_refs': 44,
            'exact_id_en_byte_matches': 39, 'inherited_id_localizations': 5,
            'retained_source_assets': 44, 'javanese_svg_derivatives': 10,
            'stored_asset_files_total': 54, 'scoped_accessibility_corrections': 7,
            'source_formats': source_formats, 'canonical_formats': canonical_formats,
        },
        'ordered_binding_digest_sha256': ordered_binding_digest,
        'prior_handoff_nine_field_media_digest_sha256': PRIOR_NINE_FIELD_MEDIA_DIGEST,
        'policy': (
            'All 44 effective Indonesian source objects are retained exactly. The 39 nonlinguistic '
            'objects that equal canonical English bytes are shared by every track. Only the five '
            'registered inherited Indonesian localizations receive two Javanese SVG derivatives each. '
            'The fuel-table SVG embeds the exact source PNG and covers only the two linguistic label '
            'cell interiors; the four inherited SVG families change only registered text plus root language.'
        ),
        'credits': {
            'openstax-prealgebra-2e-cc-by-nc-sa-4.0': {
                'source': 'OpenStax, Rice University, Prealgebra 2e',
                'source_url': 'https://openstax.org/details/books/prealgebra-2e',
                'license': 'CC BY-NC-SA 4.0', 'license_path': 'downloads/jv-Latn-ID/a00-id/LICENSE',
                'license_sha256': sha256(license_raw), 'license_git_blob_sha1': license_oid,
                'indonesian_adaptation': 'KokunoYumeto, unofficial AI-assisted Indonesian adaptation',
                'javanese_derivatives': 'Unofficial AI-assisted Javanese draft; registered text changes are declared per output.',
                'notice': 'Inherited component rights and notices remain controlling; no endorsement is implied.',
            }
        },
        'canon_checkpoint': {
            'lock_sha256': CANON_LOCK_SHA256, 'record_count': 50,
            'actual_readable_entries_rechecked_for_asset_wording': ['C48 basa', 'C49 tembung'],
            'decision': (
                'Basa and tembung support language/word framing but do not certify technical algebra '
                'loans or school compounds. Basis, eksponen, faktor, mpg and algebra labels remain '
                'declared technical/source loans or provisional compounds.'
            ),
        },
        'methodology_limits': {
            'withdrawn_global_ranking': (
                'The earlier Top-10/rank-9 allocation is withdrawn and is not evidence for this scope.'
            ),
            'candidate_backend': (
                'Indonesian catalog aedb245/v0.62.14 backend-v2/capsule is candidate integration only '
                'and did not replace either pinned source in this asset layer.'
            ),
            'source_replacement_performed': False,
        },
        'scoped_accessibility_corrections': corrections,
        'render_review': RENDER_REVIEW,
        'review_limits': {
            'all_source_media_personally_viewed_in_prior_translation_stage': True,
            'source_byte_xml_and_geometry_review': True,
            'standalone_derivative_render_review': RENDER_REVIEW['status'] == 'completed',
            'integrated_reader_visual_review': False, 'screen_reader_review': False,
            'native_language_review': False, 'listening_review': False,
            'synthesized_audio_files': 0, 'whole_module_production_complete': False,
            'full_assignment_complete': False,
        },
        'assets': records,
    }
    generated[MANIFEST] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    if len(generated) != 55 or sum(map(len, generated.values())) > 2_000_000:
        raise ValueError('Unexpected product count or output-size cap exceeded')
    return generated


def verify_saved(generated=None):
    generated = products() if generated is None else generated
    for path, raw in generated.items():
        if (LANG / path).read_bytes() != raw:
            raise ValueError('Stale use-algebra asset: ' + path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    generated = products()
    if generated != products():
        raise ValueError('Nondeterministic asset generation')
    if args.check:
        verify_saved(generated)
    else:
        for path, raw in generated.items():
            write_bytes(LANG / path, raw)
    print(
        ('Checked' if args.check else 'Prepared')
        + ' 44 exact source assets, 10 Javanese SVG derivatives, 7 scoped repairs and 1 manifest.'
    )


if __name__ == '__main__':
    main()
