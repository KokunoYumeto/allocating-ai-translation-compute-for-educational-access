"""Prepare the complete pinned m81245 subtraction media layer.

All 55 effective Indonesian media are checked against the exact canonical
English archive bytes.  Fifty-three nonlinguistic figures remain byte-identical
for every track.  Two English-labelled JPEGs are retained for the Indonesian
track and receive four finite native-Javanese SVG derivatives.
"""
import argparse
import html
import json
from pathlib import PurePosixPath
import struct
import xml.etree.ElementTree as ET
import zipfile

from config import DOWNLOADS, LANG, TRACKS, UPSTREAM_COMMIT
from prepare_name_whole_assets import A00_COMMIT, blob_sha1, git, sha256
from safe_io import write_bytes


UNIT = 'a00-subtract-whole'
MODULE = 'm81245'
OUT = f'translation/assets/{UNIT}/'
MANIFEST = f'translation/{UNIT}.assets.json'
RULES = f'audio/{UNIT}.rules.json'
RULES_SHA256 = 'fe5e22786f6e367c73236289f7782953fc964c9ca3b25148362e8be2872dbd8e'
SOURCE_MODULE_SHA256 = 'd6829f9326dfcb9d30e589b2917bbc18ab2c871b0f44b939b1ceeb477ec8fe3f'
ENGLISH_MODULE_SHA256 = '02df262b21ee15472223ae863bc5f3bcb3714389a8ef46e66c8b4469c6972841'
SOURCE_MODULE_BLOB = 'e5e9e2861e49c0271203107ee90487ff342bc539'
ENGLISH_MODULE_BLOB = 'a58aee1910796b767da79e76d0bc26d7fb5dc6b7'
CANON_LOCK_SHA256 = '396bc9db6ce9f8ab06e0366cf8f525f68e403afa567a7235bea1ea611c006c76'
ARCHIVE_PREFIX = f'osbooks-prealgebra-bundle-{UPSTREAM_COMMIT}/'
SVG = '{http://www.w3.org/2000/svg}'
XML_LANG = '{http://www.w3.org/XML/1998/namespace}lang'
LINGUISTIC_IDS = ('fs-id1376326', 'eip-id1164272051986')

SOURCE_LABELS = {
    'fs-id1376326': ['4 tens', '3 ones', '3 tens', '13 ones'],
    'eip-id1164272051986': [
        'I can...', 'Confidently', 'With some help', 'No-I don’t get it!',
        'use subtraction notation.', 'model subtraction of whole numbers.',
        'subtract whole numbers.', 'translate word phrases to math notation.',
        'subtract whole numbers in applications.',
    ],
}
TARGET_LABELS = {
    'fs-id1376326': {
        'jv-academic': ['4 puluhan', '3 satuan', '3 puluhan', '13 satuan'],
        'jv-conversation': ['4 puluhan', '3 satuan', '3 puluhan', '13 satuan'],
    },
    'eip-id1164272051986': {
        'jv-academic': [
            'Aku bisa...', 'Yakin', 'Kanthi pitulungan sethithik',
            'Ora—aku durung mangerteni', 'nggunakake notasi pangurangan.',
            'nggambarake pangurangan wilangan cacah nganggo model.',
            'ngurangi wilangan cacah.',
            'ngowahi frasa tembung dadi notasi matematika.',
            'ngurangi wilangan cacah ing penerapan.',
        ],
        'jv-conversation': [
            'Aku bisa...', 'Yakin', 'Kanthi pitulungan sethithik',
            'Ora—aku durung ngerti', 'nggunakake notasi pangurangan.',
            'nggambarake pangurangan wilangan cacah nganggo model.',
            'ngurangi wilangan cacah.',
            'ngowahi frasa tembung dadi notasi matematika.',
            'ngurangi wilangan cacah ing penerapan.',
        ],
    },
}

RENDER_REVIEW = {
    'status': 'completed',
    'renderer': 'ImageMagick 7.1.2-26 Q16-HDRI x64 38ba210:20260621; explicit RSVG/librsvg 2.40.20',
    'arguments': ['-background', 'white', '-density', '96', 'RSVG:<absolute SVG path>',
                  '-alpha', 'remove', '-alpha', 'off', '<temporary PNG path>'],
    'outputs': [
        {
            'path': OUT + 'CNX_BMath_Figure_01_03_014_img.jv-academic.svg',
            'svg_sha256': 'f444c89797e4706da5f5cbba7e9ebea054d474250cf4b41f4d60802c46df961e',
            'rendered_geometry': '626x117',
            'temporary_png_sha256': '10bae0a158738d7b95358f840433efc74c6bc4e266a629c5baafef183697e8bc',
            'inspected': True,
        },
        {
            'path': OUT + 'CNX_BMath_Figure_01_03_014_img.jv-conversation.svg',
            'svg_sha256': '4c0b64d69092e1942c60116ea3cd70d5696b1d7bffee23028d0fc17c58bfacee',
            'rendered_geometry': '626x117',
            'temporary_png_sha256': '10bae0a158738d7b95358f840433efc74c6bc4e266a629c5baafef183697e8bc',
            'inspected': True,
        },
        {
            'path': OUT + 'CNX_BMath_Figure_AppB_004.jv-academic.svg',
            'svg_sha256': 'c023fee09344e9e01e347089def6bb77bb63d6c7768ba768eefff5915f85172a',
            'rendered_geometry': '649x180',
            'temporary_png_sha256': '2d154a979b74dc35ed7e7faac2a47b4a294398caa094817b8e8aac0edb2eb37e',
            'inspected': True,
        },
        {
            'path': OUT + 'CNX_BMath_Figure_AppB_004.jv-conversation.svg',
            'svg_sha256': 'f549e1c1d9cdbb952a15d99cb777274567902f29f74d3d5a8b652c5a2cfba8dd',
            'rendered_geometry': '649x180',
            'temporary_png_sha256': 'ce701c7a2723b0ed52d996228e22563227bebe90da4e48e4625e10e238e256ad',
            'inspected': True,
        },
    ],
    'observation': (
        'All four final SVGs were rendered and opened at native output size. '
        'Every label, grid line, block cell and right-pointing regrouping arrow '
        'was visible; no clipping or overlap was observed. The two regrouping '
        'tracks are intentionally pixel-identical because their visible labels '
        'are identical while their nonvisual descriptions remain register-specific.'
    ),
    'scope': (
        'Static standalone SVG clipping, overlap and diagram-structure review '
        'only; not integrated-reader, browser, screen-reader, native-language, '
        'pronunciation or listening approval.'
    ),
}


def source_bytes(path):
    """Read one already-materialized ID-release medium without network access."""
    return (DOWNLOADS / 'a00-id' / path).read_bytes()


def canonical_bytes(archive, path):
    """Read one exact canonical archive member without extracting the archive."""
    return archive.read(ARCHIVE_PREFIX + path)


def tree_blobs(repo, commit):
    """Return the pinned media tree in one read-only Git metadata query."""
    rows = git(repo, 'ls-tree', '-r', commit, '--', 'media').decode('utf-8').splitlines()
    result = {}
    for row in rows:
        metadata, path = row.split('\t', 1)
        mode, kind, oid = metadata.split()
        assert mode == '100644' and kind == 'blob'
        result[path] = oid
    return result


def image_info(raw):
    """Return actual MIME and dimensions using only format headers."""
    if raw.startswith(b'\x89PNG\r\n\x1a\n'):
        assert raw[12:16] == b'IHDR'
        width, height = struct.unpack('>II', raw[16:24])
        return 'image/png', 'PNG', width, height
    if raw.startswith(b'\xff\xd8'):
        pos = 2
        sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
               0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
        while pos < len(raw):
            while pos < len(raw) and raw[pos] != 0xFF:
                pos += 1
            while pos < len(raw) and raw[pos] == 0xFF:
                pos += 1
            assert pos < len(raw), 'Truncated JPEG marker'
            marker = raw[pos]
            pos += 1
            if marker in (0x01, *range(0xD0, 0xD9)):
                continue
            assert pos + 2 <= len(raw), 'Truncated JPEG segment'
            length = int.from_bytes(raw[pos:pos + 2], 'big')
            assert length >= 2 and pos + length <= len(raw), 'Invalid JPEG segment'
            if marker in sof:
                assert length >= 7
                height = int.from_bytes(raw[pos + 3:pos + 5], 'big')
                width = int.from_bytes(raw[pos + 5:pos + 7], 'big')
                return 'image/jpeg', 'JPEG', width, height
            pos += length
        raise AssertionError('JPEG has no supported SOF marker')
    raise AssertionError('Unregistered media format')


def _svg_document(width, height, title, desc, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xml:lang="jv-Latn-ID" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        'role="img" aria-labelledby="title desc">\n'
        f'<title id="title">{html.escape(title)}</title>\n'
        f'<desc id="desc">{html.escape(desc)}</desc>\n'
        '<rect id="background" width="100%" height="100%" fill="#ffffff"/>\n'
        f'{body}</svg>\n'
    ).encode('utf-8')


def _cells(group_id, positions, fill, stroke):
    rows = [f'<g id="{group_id}" fill="{fill}" stroke="{stroke}" stroke-width="1.2">']
    for ordinal, (x, y, width, height) in enumerate(positions, 1):
        rows.append(
            f'<rect id="{group_id}-{ordinal:02d}" x="{x:g}" y="{y:g}" '
            f'width="{width:g}" height="{height:g}"/>'
        )
    rows.append('</g>')
    return '\n'.join(rows)


def regrouping_svg(track, alt):
    labels = TARGET_LABELS['fs-id1376326'][track]
    title = (
        'Panglompokan manèh patang puluhan lan telung satuan'
        if track == 'jv-academic'
        else 'Nglompokaké manèh patang puluhan lan telung satuan'
    )
    left_tens = [(17.5 * x, y, 17.5, 17) for y in (29, 51, 73, 95) for x in range(10)]
    left_ones = [(187 + 24 * x, 29, 17, 17) for x in range(3)]
    right_tens = [(328 + 17.5 * x, y, 17.5, 17) for y in (40, 62, 84) for x in range(10)]
    right_blue = [(514 + 24 * x, 40, 17, 17) for x in range(3)]
    right_red = [(514 + 23 * x, y, 17, 17) for y in (62, 84) for x in range(5)]
    label_rows = '\n'.join(
        f'<text id="label-{ordinal}" x="{x}" y="17" text-anchor="middle">{html.escape(value)}</text>'
        for ordinal, (x, value) in enumerate(zip((88, 219, 416, 570), labels), 1)
    )
    body = f'''<defs><marker id="arrowhead" viewBox="0 0 10 8" refX="9" refY="4" markerWidth="8" markerHeight="6" orient="auto"><path d="M0 0 L10 4 L0 8 Z" fill="#43d8c9"/></marker></defs>
<g id="labels" font-family="Arial, sans-serif" font-size="16" fill="#111111">
{label_rows}
</g>
{_cells('left-tens', left_tens, '#e8f7f4', '#006f80')}
{_cells('left-ones', left_ones, '#e8f7f4', '#006f80')}
{_cells('right-tens', right_tens, '#e8f7f4', '#006f80')}
{_cells('right-ones-blue', right_blue, '#e8f7f4', '#006f80')}
{_cells('right-ones-red', right_red, '#ffdada', '#e52f38')}
<path id="regroup-arrow" d="M260 72 H317" fill="none" stroke="#43d8c9" stroke-width="2" marker-end="url(#arrowhead)"/>
'''
    raw = _svg_document(626, 117, title, alt, body)
    verify_vector(raw, 'fs-id1376326', track, alt)
    return raw


def _multiline(node_id, x, lines, y_values, size=13, anchor='middle', weight='normal'):
    assert len(lines) == len(y_values)
    spans = ''.join(
        f'<tspan x="{x}" y="{y}">{html.escape(line)}</tspan>'
        for line, y in zip(lines, y_values)
    )
    return (
        f'<text id="{node_id}" x="{x}" text-anchor="{anchor}" '
        f'font-size="{size}" font-weight="{weight}">{spans}</text>'
    )


def self_check_svg(track, alt):
    labels = TARGET_LABELS['eip-id1164272051986'][track]
    title = (
        'Pambiji mandiri katrampilan pangurangan'
        if track == 'jv-academic'
        else 'Mbiji dhewe katrampilan ngurangi'
    )
    final_header = ['Ora—aku durung', 'mangerteni' if track == 'jv-academic' else 'ngerti']
    row_top = (52, 77, 103, 128, 154)
    row_bottom = (77, 103, 128, 154, 180)
    fills = ''.join(
        f'<rect id="row-fill-{index}" x="0" y="{top}" width="649" '
        f'height="{bottom - top}" fill="{fill}"/>\n'
        for index, (top, bottom, fill) in enumerate(
            zip(row_top, row_bottom, ('#ffffff', '#eef8f8', '#ffffff', '#eef8f8', '#ffffff')), 1
        )
    )
    blank_cells = ''.join(
        f'<rect id="choice-{row}-{column}" x="{left}" y="{top}" '
        f'width="{right-left}" height="{bottom-top}" fill="none" stroke="none"/>\n'
        for row, (top, bottom) in enumerate(zip(row_top, row_bottom), 1)
        for column, (left, right) in enumerate(zip((297, 414, 531), (414, 531, 649)), 1)
    )
    body_labels = '\n'.join(
        f'<text id="skill-{index}" x="5" y="{y}" font-size="12">{html.escape(value)}</text>'
        for index, (value, y) in enumerate(zip(labels[4:], (69, 95, 120, 146, 172)), 1)
    )
    verticals = '\n'.join(
        f'<line id="v-{index}" x1="{x}" y1="0" x2="{x}" y2="180"/>'
        for index, x in enumerate((297, 414, 531), 1)
    )
    horizontals = '\n'.join(
        f'<line id="h-{index}" x1="0" y1="{y}" x2="649" y2="{y}"/>'
        for index, y in enumerate((52, 77, 103, 128, 154), 1)
    )
    body = f'''<rect id="header-fill" x="0" y="0" width="649" height="52" fill="#add8d8"/>
{fills}<g id="blank-choice-cells">{blank_cells}</g>
<g id="grid" fill="none" stroke="#3e9fa3" stroke-width="1">
<rect id="outer-border" x="0.5" y="0.5" width="648" height="179"/>
{verticals}
{horizontals}
</g>
<g id="table-text" font-family="Arial, sans-serif" fill="#111111">
<text id="header-1" x="5" y="31" font-size="14">{html.escape(labels[0])}</text>
<text id="header-2" x="355.5" y="31" text-anchor="middle" font-size="13" font-weight="bold">{html.escape(labels[1])}</text>
{_multiline('header-3', 472.5, ['Kanthi', 'pitulungan', 'sethithik'], (13, 29, 45), 13, weight='bold')}
{_multiline('header-4', 590, final_header, (20, 38), 13, weight='bold')}
{body_labels}
</g>
'''
    raw = _svg_document(649, 180, title, alt, body)
    verify_vector(raw, 'eip-id1164272051986', track, alt)
    return raw


def vector(media_id, track, alt):
    assert media_id in LINGUISTIC_IDS, 'Unknown subtraction linguistic asset'
    assert track in ('jv-academic', 'jv-conversation'), 'Unknown target track'
    if media_id == 'fs-id1376326':
        return regrouping_svg(track, alt)
    return self_check_svg(track, alt)


def _id_map(root):
    result = {}
    for node in root.iter():
        if node.get('id'):
            assert node.get('id') not in result
            result[node.get('id')] = node
    return result


def verify_vector(raw, media_id, track, alt):
    assert media_id in LINGUISTIC_IDS
    assert track in ('jv-academic', 'jv-conversation')
    root = ET.fromstring(raw)
    assert root.tag == SVG + 'svg' and root.get(XML_LANG) == 'jv-Latn-ID'
    assert all(node.tag.startswith(SVG) for node in root.iter())
    nodes = _id_map(root)
    assert nodes['desc'].text == alt
    visible = [nodes[f'label-{n}'].text for n in range(1, 5)] if media_id == 'fs-id1376326' else [
        nodes['header-1'].text, nodes['header-2'].text,
        ' '.join(child.text for child in nodes['header-3']),
        ' '.join(child.text for child in nodes['header-4']),
        *[nodes[f'skill-{n}'].text for n in range(1, 6)],
    ]
    assert visible == TARGET_LABELS[media_id][track]
    assert not any(source in visible for source in SOURCE_LABELS[media_id])
    if media_id == 'fs-id1376326':
        assert (root.get('width'), root.get('height'), root.get('viewBox')) == ('626', '117', '0 0 626 117')
        assert [len(nodes[group]) for group in
                ('left-tens', 'left-ones', 'right-tens', 'right-ones-blue', 'right-ones-red')] == [40, 3, 30, 3, 10]
        assert nodes['regroup-arrow'].get('d') == 'M260 72 H317'
        assert nodes['arrowhead'].get('orient') == 'auto'
        assert [nodes[f'label-{n}'].get('x') for n in range(1, 5)] == ['88', '219', '416', '570']
    else:
        assert (root.get('width'), root.get('height'), root.get('viewBox')) == ('649', '180', '0 0 649 180')
        assert len(nodes['blank-choice-cells']) == 15
        assert all(not ''.join(node.itertext()).strip() for node in nodes['blank-choice-cells'])
        assert [nodes[f'v-{n}'].get('x1') for n in range(1, 4)] == ['297', '414', '531']
        assert [nodes[f'h-{n}'].get('y1') for n in range(1, 6)] == ['52', '77', '103', '128', '154']
        assert nodes['outer-border'].get('width') == '648' and nodes['outer-border'].get('height') == '179'


def _media_nodes(root):
    return [node for node in root.iter() if node.tag.rsplit('}', 1)[-1] == 'media']


def _image(node):
    children = [child for child in node if child.tag.rsplit('}', 1)[-1] == 'image']
    assert len(children) == 1
    return children[0]


def _output(generated, path, raw):
    if path in generated:
        assert generated[path] == raw
    else:
        generated[path] = raw


def products():
    rules_raw = (LANG / RULES).read_bytes()
    assert sha256(rules_raw) == RULES_SHA256
    rules = json.loads(rules_raw)
    charts = rules['chart_fixtures']
    assert len(charts) == 55
    assert [row['ordinal'] for row in charts] == list(range(1, 56))
    assert len({row['media_id'] for row in charts}) == len({row['source_ref'] for row in charts}) == 55
    assert [row['media_id'] for row in charts if row['visible_linguistic_pixels']] == list(LINGUISTIC_IDS)

    source_raw = git('a00-id', 'show', f'{A00_COMMIT}:modules/{MODULE}/index.cnxml')
    english_raw = git('openstax-prealgebra-bundle', 'show',
                      f'{UPSTREAM_COMMIT}:modules/{MODULE}/index.cnxml')
    assert sha256(source_raw) == SOURCE_MODULE_SHA256
    assert sha256(english_raw) == ENGLISH_MODULE_SHA256
    assert blob_sha1(source_raw) == SOURCE_MODULE_BLOB
    assert blob_sha1(english_raw) == ENGLISH_MODULE_BLOB
    source_media = _media_nodes(ET.fromstring(source_raw))
    english_media = _media_nodes(ET.fromstring(english_raw))
    assert [node.get('id') for node in source_media] == [row['media_id'] for row in charts]
    assert [node.get('id') for node in english_media] == [row['media_id'] for row in charts]
    source_tree = tree_blobs('a00-id', A00_COMMIT)
    canonical_tree = tree_blobs('openstax-prealgebra-bundle', UPSTREAM_COMMIT)

    canon_raw = (LANG / 'canon/sources.lock.json').read_bytes()
    assert sha256(canon_raw) == CANON_LOCK_SHA256
    canon = json.loads(canon_raw)
    assert len(canon['records']) == 50
    canon_ids = {row['id'] for row in canon['records']}
    consulted = ['C01', 'C02', 'C03', 'C05', 'C06', 'C37', 'C38', 'C39', 'C48', 'C49', 'C50']
    assert set(consulted) <= canon_ids

    id_license = git('a00-id', 'show', f'{A00_COMMIT}:LICENSE')
    upstream_license = git('openstax-prealgebra-bundle', 'show', f'{UPSTREAM_COMMIT}:LICENSE')
    assert id_license == upstream_license

    generated, records = {}, []
    with zipfile.ZipFile(DOWNLOADS / 'openstax-full-pinned.zip') as archive:
        for chart, source_node, english_node in zip(charts, source_media, english_media):
            source_image, english_image = _image(source_node), _image(english_node)
            assert source_image.get('src') == english_image.get('src') == chart['source_ref']
            relative = chart['source_ref'].removeprefix('../../')
            assert chart['source_ref'].startswith('../../media/')
            assert relative == 'media/' + PurePosixPath(relative).name
            raw = source_bytes(relative)
            canonical = canonical_bytes(archive, relative)
            assert raw == canonical, 'ID release differs from canonical media: ' + chart['media_id']
            assert sha256(raw) == chart['sha256'] and len(raw) == chart['bytes']
            assert blob_sha1(raw) == chart['git_blob'] == source_tree[relative] == canonical_tree[relative]
            actual_mime, actual_format, width, height = image_info(raw)
            assert (actual_format, width, height) == (chart['format'], chart['width'], chart['height'])
            assert chart['id_release_equals_canonical_pin'] is True

            source_path = OUT + PurePosixPath(relative).name
            _output(generated, source_path, raw)
            outputs = {
                'id-academic': {
                    'path': source_path, 'sha256': sha256(raw), 'bytes': len(raw),
                    'mime_type': actual_mime, 'derivative_type': 'exact-source-byte-retention',
                }
            }
            substitutions = []
            for track in ('jv-academic', 'jv-conversation'):
                if chart['media_id'] in LINGUISTIC_IDS:
                    expected = [
                        {'source': row['english'], 'target': row[track]}
                        for row in chart['visible_linguistic_pixels']
                    ]
                    assert [row['source'] for row in expected] == SOURCE_LABELS[chart['media_id']]
                    assert [row['target'] for row in expected] == TARGET_LABELS[chart['media_id']][track]
                    substitutions.append({'track': track, 'labels': expected})
                    value = vector(chart['media_id'], track, chart['target_alt'][track])
                    path = OUT + PurePosixPath(relative).stem + f'.{track}.svg'
                    mime_type = 'image/svg+xml'
                    derivative_type = 'native-svg-registered-text-and-source-layout-reconstruction'
                else:
                    assert chart['visible_linguistic_pixels'] == []
                    value, path, mime_type = raw, source_path, actual_mime
                    derivative_type = 'exact-source-byte-retention'
                _output(generated, path, value)
                outputs[track] = {
                    'path': path, 'sha256': sha256(value), 'bytes': len(value),
                    'mime_type': mime_type, 'derivative_type': derivative_type,
                }
            records.append({
                'ordinal': chart['ordinal'], 'media_id': chart['media_id'],
                'source_path': chart['source_path'], 'scope': chart['scope'],
                'source_src': chart['source_ref'],
                'source_declared_mime': source_image.get('mime-type'),
                'actual_mime_type': actual_mime, 'format': actual_format,
                'source_bytes': len(raw), 'source_sha256': sha256(raw),
                'source_git_blob_sha1': blob_sha1(raw),
                'geometry': {'width': width, 'height': height},
                'canonical_path': relative, 'canonical_bytes': len(canonical),
                'canonical_sha256': sha256(canonical),
                'canonical_git_blob_sha1': blob_sha1(canonical),
                'id_release_equals_canonical_pin': True,
                'contains_linguistic_pixels': chart['media_id'] in LINGUISTIC_IDS,
                'source_alt': chart['source_alt'],
                'target_alt': chart['target_alt'],
                'registered_text_substitutions': substitutions,
                'credit_id': 'openstax-prealgebra-2e-cc-by-nc-sa-4.0',
                'outputs': outputs,
            })

    assert len(records) == 55
    assert len(generated) == 59
    assert sum(row['actual_mime_type'] == 'image/jpeg' for row in records) == 17
    assert sum(row['actual_mime_type'] == 'image/png' for row in records) == 38
    assert sum(row['contains_linguistic_pixels'] for row in records) == 2
    assert sum(output['mime_type'] == 'image/svg+xml'
               for row in records for output in row['outputs'].values()) == 4
    manifest = {
        'schema': 'jv-subtract-whole-assets-v1',
        'unit': UNIT, 'module': MODULE,
        'status': 'complete_source_bound_asset_draft_not_reader_integrated',
        'rules_sha256': RULES_SHA256,
        'source': {
            'a00_commit': A00_COMMIT, 'module_path': f'modules/{MODULE}/index.cnxml',
            'module_git_blob_sha1': SOURCE_MODULE_BLOB,
            'module_sha256': SOURCE_MODULE_SHA256,
        },
        'canonical_english': {
            'upstream_commit': UPSTREAM_COMMIT,
            'module_path': f'modules/{MODULE}/index.cnxml',
            'module_git_blob_sha1': ENGLISH_MODULE_BLOB,
            'module_sha256': ENGLISH_MODULE_SHA256,
            'archive_access': 'read individual pinned members in memory; no extraction',
        },
        'scope': {
            'source_media_occurrences': 55, 'unique_source_refs': 55,
            'unique_source_sha256': 55, 'exact_id_en_byte_matches': 55,
            'retained_nonspeaking_media': 53, 'linguistic_source_rasters': 2,
            'javanese_svg_derivatives': 4, 'stored_source_assets': 55,
            'stored_asset_files_total': 59,
            'actual_source_formats': {'JPEG': 17, 'PNG': 38},
        },
        'policy': (
            'Every exact Indonesian source medium is retained. The 53 media with '
            'no visible linguistic pixels are shared byte-for-byte by all three '
            'tracks. The two English-labelled source JPEGs stay unchanged for '
            'id-academic and receive only the four registered Javanese SVGs.'
        ),
        'credits': {
            'openstax-prealgebra-2e-cc-by-nc-sa-4.0': {
                'source': 'OpenStax, Rice University, Prealgebra 2e',
                'source_url': 'https://openstax.org/details/books/prealgebra-2e',
                'license': 'CC BY-NC-SA 4.0',
                'license_path': 'downloads/jv-Latn-ID/a00-id/LICENSE',
                'license_sha256': sha256(id_license),
                'indonesian_adaptation': 'KokunoYumeto, unofficial AI-assisted Indonesian adaptation',
                'javanese_derivatives': 'Unofficial AI-assisted Javanese draft; text/layout changes are declared per asset',
                'notice': 'Full inherited component rights and notices remain controlling; no endorsement is implied.',
            }
        },
        'canon_checkpoint': {
            'lock_sha256': CANON_LOCK_SHA256, 'actual_record_count': 50,
            'fully_read_for_asset_stage': consulted,
            'decision': (
                'Wilangan/cacah, numeral, subtraction, word/phrase and help senses '
                'were checked against the actual readable entries. Lexical evidence '
                'does not independently certify the provisional school compounds.'
            ),
        },
        'allocation_methodology_note': (
            'The former allocation ranking is withdrawn and is not evidence for '
            'this asset scope; work continues under the standing commissioned '
            'all-A00, all-A10 and AX-2 assignment.'
        ),
        'known_non_asset_alt_issues': [
            {
                'media_id': 'fs-id2425624',
                'source_sha256': '5946124a1470c7aa9c4f6edda62c2e0ae0d83e2aeecaab6f65a1ef81054de628',
                'status': 'Exact source bytes retained; narrow target-alt correction and rules rebinding are owned by root.',
            },
            {
                'media_id': 'fs-id2643011',
                'source_sha256': 'ddd74c6d17086f66c2fb9d2f508bdb230e476557fa5b3a082ede509ea5d94871',
                'status': 'Exact source bytes retained; narrow target-alt correction and rules rebinding are owned by root.',
            },
        ],
        'render_review': RENDER_REVIEW,
        'review_limits': {
            'source_byte_and_header_review': True,
            'standalone_derivative_render_review': RENDER_REVIEW['status'] == 'completed',
            'integrated_reader_visual_review': False,
            'browser_review': False, 'screen_reader_review': False,
            'native_language_review': False, 'listening_review': False,
            'synthesized_audio_files': 0, 'whole_module_complete': False,
            'full_assignment_complete': False,
        },
        'assets': records,
    }
    generated[MANIFEST] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    assert len(generated) == 60
    return generated


def verify_saved(generated=None):
    generated = products() if generated is None else generated
    for path, raw in generated.items():
        assert (LANG / path).read_bytes() == raw, 'Stale subtraction asset: ' + path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    generated = products()
    assert generated == products()
    if args.check:
        verify_saved(generated)
    else:
        for path, raw in generated.items():
            write_bytes(LANG / path, raw)
    print(
        ('Checked' if args.check else 'Prepared')
        + ' 55 exact source media, 4 Javanese SVG derivatives and 1 manifest; '
        'reader/native/listening review remains pending.'
    )


if __name__ == '__main__':
    main()
