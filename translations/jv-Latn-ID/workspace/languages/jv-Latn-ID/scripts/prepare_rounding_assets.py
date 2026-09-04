"""Source-bound rounding SVG labels and explicitly enumerated semantic repairs.

The Indonesian redraws remain byte-identical. Javanese derivatives repair only
the declared arrows/marks seen against the canonical figures, never silently
claiming that inherited redraw geometry was correct.
"""
import argparse
import html
import json
import math
import re
import xml.etree.ElementTree as ET
import zipfile

from config import DOWNLOADS, LANG, TRACKS, UPSTREAM_COMMIT
from prepare_name_whole_assets import A00_COMMIT, blob_sha1, geometry_signature, git, sha256, text_nodes
from safe_io import write_bytes

UNIT = 'a00-rounding'
SECTION = 'fs-id2472737'
PREFIX = 'CNX_BMath_Figure_01_01_'
SOURCE_SVGS = {
    '022.jpg': '561131e8e413cb52636e5b3e482217432258814aae3c4eb98899ef043012b124',
    '031_img.jpg': '4aa1f144691f1fb8897b0fd424b2f6a99ff0ca7005928ac62190d76499abf540',
    '032_img.jpg': '527943359fc7bd94782609fc2d8952f2208fb2cfe9d91b6208c3f7061bd0b28d',
    '033_img.jpg': 'd40e1da0a24abf725b57f5b2cfd734293337498bbf1aaa97f2fd250ae466e35f',
    '034_img-01.png': '0c6003deeb8ec9383e35a10df8097ead55355d7348c80042e8bd60209de38b8d',
    '035_img-01.png': '654e100587fa28498f0320fe39ba925984364eb02cb5509152db217366e8316d',
    '035_img-02.png': '323944b83b62b03092fa8c1f36526597b803409b33a1290d2c7d8796ba6cd803',
    '036_img-01.png': '0f588ad8af33e29fa2b4782bcf360cb4ce4f318b72a1edb32be0bab74347bc2c',
    '036_img-02.png': 'bbfaf72703afee57ad050df97675cf05722de2e4b2d6a56002a6f5c8b91c3052',
    '037_img-01.png': '4a248d9a1afd5dd8b2f06fdf67db44fc05c3212ab439bcd8273b11e2f85cc581',
    '038_img-01.png': '3c60edfa23ee2f564460d62f7098559e197b9246e403c5d3f6d8d92f2e78ffff',
    '038_img-03.png': '40052ab7a27c594704229f41d6cd9dad99109565fc21fd5306022e602b295df1',
}
LABELS = {
    'tempat puluhan': 'panggonan puluhan',
    'tempat ratusan': 'panggonan atusan',
    'tempat ribuan': 'panggonan éwuan',
    'lebih besar dari 5': 'luwih gedhé tinimbang 5',
    'kurang dari 5': 'luwih cilik tinimbang 5',
    'tambahkan 1': 'tambahake 1',
    'ganti dengan 0': 'ganti nganggo 0',
    'jangan tambahkan 1': 'aja ditambahi 1',
    'tambahkan 1 (9 + 1 = 10)': 'tambahake 1 (9 + 1 = 10)',
    'Tulis 0 di tempat ratusan.': 'Tulisen 0 ing panggonan atusan.',
    'Tulis 0 di tempat ribuan.': 'Tulisen 0 ing panggonan éwuan.',
    'Tambahkan 1 ke tempat ribuan.': 'Tambahake 1 ing panggonan éwuan.',
    'Tambahkan 1 ke tempat puluh ribuan.': 'Tambahake 1 ing panggonan puluhan éwu.',
    'Digit pembanding lebih besar dari lima': 'Digit pambandhing luwih gedhé tinimbang lima',
    'Digit pembanding kurang dari lima': 'Digit pambandhing luwih cilik tinimbang lima',
    'Pada bilangan 76, digit 7 berada di tempat puluhan dan digit 6 lebih besar dari 5.': 'Ing wilangan 76, digit 7 ana ing panggonan puluhan lan digit 6 luwih gedhé tinimbang 5.',
    'Pada bilangan 72, digit 7 berada di tempat puluhan dan digit 2 kurang dari 5.': 'Ing wilangan 72, digit 7 ana ing panggonan puluhan lan digit 2 luwih cilik tinimbang 5.',
    'Digit puluhan ditambah satu dan digit satuan diganti nol, sehingga 76 dibulatkan menjadi 80.': 'Digit puluhan ditambahi siji lan digit satuan diganti nol, mula 76 dibunderake dadi 80.',
    'Digit puluhan tidak ditambah dan digit satuan diganti nol, sehingga 72 dibulatkan menjadi 70.': 'Digit puluhan ora ditambahi lan digit satuan diganti nol, mula 72 dibunderake dadi 70.',
    '76 dibulatkan ke puluhan terdekat menjadi 80.': '76 dibunderake menyang puluhan paling cedhak dadi 80.',
    'Digit ratusan ditambah satu dan digit di kanannya diganti nol, sehingga hasil pembulatan adalah 23,700.': 'Digit atusan ditambahi siji lan digit ing sisih tengene diganti nol, mula asil pambunderane yaiku 23,700.',
    'Satu ditambahkan pada digit 9; nol ditulis di tempat ratusan; satu ditambahkan ke tempat ribuan; digit sisanya diganti nol.': 'Siji ditambahake ing digit 9; nol ditulis ing panggonan atusan; siji ditambahake ing panggonan éwuan; digit liyane diganti nol.',
    'Satu ditambahkan pada digit 9; nol ditulis di tempat ribuan; satu ditambahkan ke tempat puluh ribuan; tiga digit terakhir diganti nol.': 'Siji ditambahake ing digit 9; nol ditulis ing panggonan éwuan; siji ditambahake ing panggonan puluhan éwu; telung digit pungkasan diganti nol.',
}
for old, new in [('76', '80'), ('72', '70'), ('23,658', '23,700'), ('3,978', '4,000'), ('29,504', '30,000')]:
    LABELS[f'Membulatkan {old} menjadi {new}'] = f'Mbunderake {old} dadi {new}'
for place, target_place, value, digit in [('puluhan', 'puluhan', '843', '4'), ('ratusan', 'atusan', '23,658', '6'),
                                         ('ratusan', 'atusan', '3,978', '9'), ('ribuan', 'éwuan', '147,032', '7'),
                                         ('ribuan', 'éwuan', '29,504', '9')]:
    LABELS[f'Tempat {place} pada {value}'] = f'Panggonan {target_place} ing {value}'
    LABELS[f'Panah menunjuk digit {digit} sebagai digit pada tempat {place}.'] = f'Panah nuding digit {digit} minangka digit ing panggonan {target_place}.'


def attribute(text, name, value):
    result, count = re.subn(r'\b' + re.escape(name) + r'="[^"]*"', name + '="' + str(value) + '"', text)
    assert count == 1, ('Unexpected SVG attribute', name)
    return result


def repair_geometry(text, key):
    """Finite changes with a complete reversible before/after ledger."""
    changes = []

    def patch(before, after, reason):
        nonlocal text
        assert text.count(before) == 1
        text = text.replace(before, after)
        changes.append({'before': before, 'after': after, 'reason': reason})

    def arrow(index, x, y, reason, color=None):
        old_line = re.findall(r'<line\b[^>]*/>', text)[index]
        old_head = re.findall(r'<polygon\b[^>]*/>', text)[index]
        data = ET.fromstring(old_line)
        start_x, start_y = float(data.get('x1')), float(data.get('y1'))
        dx, dy = x - start_x, y - start_y
        length = math.hypot(dx, dy)
        ux, uy = dx / length, dy / length
        points = [(x, y), (x - 8 * ux - 4.5 * uy, y - 8 * uy + 4.5 * ux),
                  (x - 8 * ux + 4.5 * uy, y - 8 * uy - 4.5 * ux)]
        line = attribute(attribute(old_line, 'x2', x), 'y2', y)
        head = attribute(old_head, 'points', ' '.join(f'{a:g},{b:g}' for a, b in points))
        if color:
            line, head = attribute(line, 'stroke', color), attribute(head, 'fill', color)
        patch(old_line, line, reason)
        patch(old_head, head, reason + '; arrowhead follows the corrected line')

    def extra(node, reason):
        patch('</svg>', node + '\n</svg>', reason)

    # Explicit numeric font fixes the measured digit destinations across the
    # standalone renderer and normal serif browser fallback. No numeric text,
    # baseline, size, centre or source reading is changed.
    for match in list(re.finditer(r'<text\b[^>]*>[0-9,]+</text>', text)):
        old = match.group()
        patch(old, old.replace('<text ', '<text font-family="Times New Roman, serif" ', 1),
              'Explicit serif numeric font for reviewed glyph/arrow alignment')
    if key in ('022.jpg', '032_img.jpg'):
        arrow(1, 185, 140, 'Canonical red comparison arrow points to the units digit', '#e52f38')
        extra('<line x1="172" y1="133" x2="188" y2="133" stroke="#111111" stroke-width="2"/>',
              'Restore canonical underline under the comparison digit, omitted by ID redraw')
    elif key in ('031_img.jpg', '033_img.jpg'):
        arrow(0, 252, 44, 'Addition/no-addition instruction addresses the tens digit', '#e52f38')
        arrow(1, 269, 44, 'Replacement instruction addresses only the units digit')
        extra('<line x1="263" y1="36" x2="274" y2="11" stroke="#111111" stroke-width="2"/>',
              'Restore the canonical units-digit cross-out omitted by ID redraw')
    elif key == '035_img-01.png':
        arrow(0, 176, 78, 'Centre place-label arrow on hundreds digit 6, not its left edge')
    elif key in ('037_img-01.png', '038_img-01.png'):
        center = 160 if key.startswith('037') else 194
        arrow(0, center, 78, 'Point to the intended thousands digit, not the number centre')
        old = re.findall(r'<line\b[^>]*/>', text)[1]
        patch(old, attribute(attribute(old, 'x1', center - 6), 'x2', center + 6),
              'Move inherited underline from the preceding digit to the intended thousands digit')
    elif key in ('035_img-02.png', '036_img-02.png', '038_img-03.png'):
        first, left, right, center = {
            '035_img-02.png': (252, 260, 287, 274),
            '036_img-02.png': (452, 459, 486, 473),
            '038_img-03.png': (487, 501, 543, 522),
        }[key]
        arrow(0, first, 42, 'Add-one instruction points to the actual target-place digit')
        arrow(1, center, 50, 'Replace-zero instruction points to the complete following-digit group')
        extra(f'<path d="M {left},38 V 43 H {right} V 38" fill="none" stroke="#42b9d7" stroke-width="2"/>',
              'Restore canonical grouping mark over all digits replaced by zeros')
    return text, changes


def localize(raw, key, track):
    assert sha256(raw) == SOURCE_SVGS[key], 'Unreviewed rounding SVG source'
    assert track in ('jv-academic', 'jv-conversation')
    mapping = dict(LABELS)
    if track == 'jv-conversation':
        for key_label, value in mapping.items():
            if value.startswith(('tambahake', 'Tambahake', 'aja nambahake')):
                mapping[key_label] = value.replace('tambahake', 'tambahna').replace('Tambahake', 'Tambahna').replace('aja nambahake', 'aja nambahi')
    text = raw.decode('utf-8').replace('xml:lang="id-ID"', 'xml:lang="jv-Latn-ID"')
    used = {}
    for node in text_nodes(raw):
        value = node.text or ''
        if re.search('[A-Za-z]', value):
            assert value in mapping, 'Unregistered SVG label: ' + value
            text = text.replace('>' + html.escape(value, quote=False) + '<', '>' + html.escape(mapping[value], quote=False) + '<')
            used[value] = mapping[value]
    text_only = text.encode('utf-8')
    assert geometry_signature(raw) == geometry_signature(text_only)
    result, changes = repair_geometry(text, key)
    final = result.encode('utf-8')
    assert [n.text for n in text_nodes(final)] == [used.get(n.text, n.text) for n in text_nodes(raw)]
    for old, new in zip(text_nodes(raw), text_nodes(final)):
        assert re.findall(r'\d+', old.text or '') == re.findall(r'\d+', new.text or '')
    reversed_text = result
    for change in reversed(changes):
        assert reversed_text.count(change['after']) == 1
        reversed_text = reversed_text.replace(change['after'], change['before'])
    assert reversed_text.encode() == text_only, 'Unlisted SVG geometry change'
    return final, used, changes


def mime(raw):
    if raw.startswith(b'\xff\xd8\xff'):
        return 'image/jpeg'
    if raw.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'image/png'
    assert ET.fromstring(raw).tag == '{http://www.w3.org/2000/svg}svg'
    return 'image/svg+xml'


def products():
    source = git('a00-id', 'show', A00_COMMIT + ':modules/m81243/index.cnxml')
    section = next(n for n in ET.fromstring(source).iter() if n.get('id') == SECTION)
    english = git('openstax-prealgebra-bundle', 'show', UPSTREAM_COMMIT + ':modules/m81243/index.cnxml')
    en_section = next(n for n in ET.fromstring(english).iter() if n.get('id') == SECTION)
    en_media = {n.get('id'): n for n in en_section.findall('.//{*}media')}
    media = section.findall('.//{*}media')
    assert len(media) == len(en_media) == 23
    generated, assets, found_svg = {}, [], []
    with zipfile.ZipFile(DOWNLOADS / 'openstax-full-pinned.zip') as archive:
        prefix = 'osbooks-prealgebra-bundle-' + UPSTREAM_COMMIT + '/'
        for node in media:
            pivot_path = node[0].get('src')[6:]
            raw = git('a00-id', 'show', A00_COMMIT + ':' + pivot_path)
            canonical_path = en_media[node.get('id')][0].get('src')[6:]
            canonical = archive.read(prefix + canonical_path)
            assert blob_sha1(canonical) == git('openstax-prealgebra-bundle', 'rev-parse', UPSTREAM_COMMIT + ':' + canonical_path).decode().strip()
            key = canonical_path.removeprefix('media/' + PREFIX)
            is_svg = pivot_path.endswith('.svg')
            assert is_svg == (key in SOURCE_SVGS)
            if not is_svg:
                assert raw == canonical, 'ID rounding raster differs from canonical witness'
            else:
                found_svg.append(key)
            outputs = {}
            labels, repairs = {}, {}
            for track in TRACKS:
                value = raw
                if is_svg and track.startswith('jv'):
                    value, labels[track], repairs[track] = localize(raw, key, track)
                suffix = ('.id-ID.svg' if track == 'id-academic' else '.' + track + '.svg') if is_svg else ''
                path = f'translation/assets/{UNIT}/{PREFIX}{key}{suffix}'
                generated[path] = value
                outputs[track] = {'path': path, 'sha256': sha256(value), 'bytes': len(value), 'mime_type': mime(value)}
            assets.append({'media_id': node.get('id'), 'source_src': node[0].get('src'),
                           'source_declared_mime': node[0].get('mime-type'), 'mime_type': mime(raw),
                           'source_sha256': sha256(raw), 'source_blob_sha1': blob_sha1(raw),
                           'canonical_path': canonical_path, 'canonical_sha256': sha256(canonical),
                           'canonical_blob_sha1': blob_sha1(canonical), 'translation_labels': labels,
                           'target_only_geometry_repairs': repairs, 'outputs': outputs})
    assert set(found_svg) == set(SOURCE_SVGS) and len(found_svg) == 12
    manifest = {'unit': UNIT, 'module': 'm81243', 'section': SECTION,
                'a00_commit': A00_COMMIT, 'upstream_commit': UPSTREAM_COMMIT,
                'source_module_sha256': sha256(source), 'english_module_sha256': sha256(english),
                'status': 'source_bound_SVG_translation_and_declared_repairs_visual_review_pending',
                'policy': 'All 12 ID SVGs and 11 rasters retained exactly; only Javanese SVG labels and individually recorded geometry repairs change. Canonical rasters and ID redraws are distinct witnesses.',
                'canon': ['C19', 'C24', 'C31', 'C32', 'C33', 'C35', 'C43'],
                'visual_review': False, 'assets': assets}
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
            assert (LANG / path).read_bytes() == raw, 'Stale rounding asset: ' + path
        else:
            write_bytes(LANG / path, raw)
    print('23 rounding images bound; 24 Javanese SVG derivatives generated with declared repairs. Visual review pending.')


if __name__ == '__main__':
    main()
