"""Two source-bound A10 exponent diagrams: exact JPEGs plus native JV SVGs.

Vector derivatives reflow longer labels; they are not pixel-identical image edits.
No network or archive-wide extraction/validation is performed.
"""
import argparse
import hashlib
import html
import json
import xml.etree.ElementTree as ET
import zipfile

from build import translated
from config import DOWNLOADS, LANG, UPSTREAM_COMMIT
from safe_io import write_bytes

UNIT = 'a10-exponents'
OUT = 'translation/assets/a10-exponents/'
SVG = '{http://www.w3.org/2000/svg}'
SOURCES = [
    ('003', 'fs-id1170655219218', 'ed2cb8bf92e9a4ec9def4c206f288c874a00f12f',
     '5be6626600b25727b5a93b37e1c4cb45a82a3fe9cc1e91b4fc0888b804370ec7', 33650),
    ('004', 'fs-id1170655111941', 'a2b54ff7ab676ad2a2f99cf93fecc035d8ae4037',
     'fe978ddd3f9f8cb93b2402be5268888aa0f668ae5c2dd12032c7f16208ec2bbe', 38920),
]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def vector(key, track, alt):
    assert key in ('003', '004') and track in ('jv-academic', 'jv-conversation')
    academic = track == 'jv-academic'
    base_label = 'wilangan pokok' if academic else 'wilangan dhasar'
    numeric = key == '003'
    width, height = (940, 100) if numeric else (480, 155)
    base, exponent = ('2', '3') if numeric else ('a', 'n')
    math_style = 'normal' if numeric else 'italic'
    opening = f'''<svg xmlns="http://www.w3.org/2000/svg" xml:lang="jv-Latn-ID" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{html.escape(base_label)} lan eksponen</title>
<desc id="desc">{html.escape(alt)}</desc>
<defs><marker id="arrow" viewBox="0 0 10 8" refX="9" refY="4" markerWidth="8" markerHeight="6" orient="auto"><path d="M0 0 L10 4 L0 8 Z" fill="#111"/></marker></defs>
<rect width="100%" height="100%" fill="white"/>
<g font-family="Arial, sans-serif" font-size="20" fill="#111">
<text id="base-label" x="15" y="34" fill="#c21823">{base_label}</text>
<path id="base-arrow" d="M178 28 H214" stroke="#111" stroke-width="2" marker-end="url(#arrow)"/>
<text id="power-base" x="225" y="40" font-family="Georgia, serif" font-style="{math_style}" font-size="30">{base}</text>
<text id="power-exponent" x="246" y="22" font-family="Georgia, serif" font-style="{math_style}" font-size="19">{exponent}</text>
<path id="exponent-arrow" d="M295 18 H263" stroke="#111" stroke-width="2" marker-end="url(#arrow)"/>
<text id="exponent-label" x="309" y="26" fill="#006f80">eksponen</text>
'''
    if numeric:
        wording = ('tegese ping-pingan telung faktor sing padha karo 2,' if academic else
                   'tegese ana telung faktor 2 sing dipingake,')
        body = f'''<text id="explanation" x="450" y="32">{wording}</text>
<text x="450" y="70">yaiku</text>
<text id="expanded-product" x="505" y="70" font-family="Georgia, serif" font-size="25">2 · 2 · 2.</text>
'''
    else:
        body = '''<text id="equation-base" x="20" y="88" font-family="Georgia, serif" font-style="italic" font-size="28">a</text>
<text id="equation-exponent" x="36" y="72" font-family="Georgia, serif" font-style="italic" font-size="18">n</text>
<text id="equals" x="62" y="88" font-size="28">=</text>
<g id="factor-pattern" font-family="Georgia, serif" font-size="28">
<text x="100" y="88" font-style="italic">a</text><text x="130" y="88">·</text>
<text x="160" y="88" font-style="italic">a</text><text x="190" y="88">·</text>
<text x="220" y="88" font-style="italic">a</text><text x="250" y="88">·</text>
<text x="275" y="88">…</text><text x="314" y="88">·</text><text x="344" y="88" font-style="italic">a</text>
</g>
<path id="factor-brace" d="M98 97 Q98 108 110 108 H211 Q229 108 229 118 Q229 108 247 108 H348 Q360 108 360 97" fill="none" stroke="#006f80" stroke-width="2"/>
<text id="factor-count" x="229" y="143" text-anchor="middle" fill="#006f80">n faktor</text>
'''
    result = (opening + body + '</g>\n</svg>\n').encode()
    verify_vector(result, key, track, alt)
    return result


def verify_vector(raw, key, track, alt):
    root = ET.fromstring(raw)
    nodes = {node.get('id'): node for node in root.iter() if node.get('id')}
    assert root.get('{http://www.w3.org/XML/1998/namespace}lang') == 'jv-Latn-ID'
    assert nodes['desc'].text == alt
    assert nodes['base-label'].text == ('wilangan pokok' if track == 'jv-academic' else 'wilangan dhasar')
    assert nodes['exponent-label'].text == 'eksponen'
    assert nodes['arrow'].get('orient') == 'auto'
    assert nodes['base-arrow'].get('d') == 'M178 28 H214'
    assert nodes['exponent-arrow'].get('d') == 'M295 18 H263'
    assert float(nodes['power-exponent'].get('x')) > float(nodes['power-base'].get('x'))
    assert float(nodes['power-exponent'].get('y')) < float(nodes['power-base'].get('y'))
    assert (nodes['power-base'].text, nodes['power-exponent'].text) == (('2', '3') if key == '003' else ('a', 'n'))
    if key == '003':
        assert nodes['expanded-product'].text == '2 · 2 · 2.'
    else:
        assert nodes['equation-base'].text == 'a' and nodes['equation-exponent'].text == 'n'
        assert nodes['equals'].text == '=' and nodes['factor-count'].text == 'n faktor'
        assert [node.text for node in nodes['factor-pattern']] == ['a', '·', 'a', '·', 'a', '·', '…', '·', 'a']
        assert nodes['factor-brace'].get('d') == 'M98 97 Q98 108 110 108 H211 Q229 108 229 118 Q229 108 247 108 H348 Q360 108 360 97'
    assert all(node.tag.startswith(SVG) for node in root.iter())


def products():
    edits_path = LANG / f'translation/{UNIT}.edits.json'
    edits = json.loads(edits_path.read_text(encoding='utf-8'))
    with zipfile.ZipFile(DOWNLOADS / 'a10-source.zip') as archive:
        source_raw = archive.read('translated/modules/m82453/index.cnxml')
    assert sha(source_raw) == '2c0b688d569044b128d589579e9ba7d871a0fb9ac7a670ac6f22d0ef2b66e635'
    source = ET.fromstring(source_raw)
    generated, records = {}, []
    with zipfile.ZipFile(DOWNLOADS / 'openstax-full-pinned.zip') as archive:
        for key, media_id, blob, digest, size in SOURCES:
            name = f'CNX_ElemAlg_Figure_01_02_{key}_img_new.jpg'
            media = next(node for node in source.iter() if node.get('id') == media_id)
            assert media.find('{*}image').get('src') == '../../media/' + name
            raw = archive.read(f'osbooks-prealgebra-bundle-{UPSTREAM_COMMIT}/media/{name}')
            assert len(raw) == size and sha(raw) == digest
            assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == blob
            original_path = OUT + name
            generated[original_path] = raw
            outputs = {'id-academic': {'path': original_path, 'sha256': digest, 'mime_type': 'image/jpeg'}}
            for track in ('jv-academic', 'jv-conversation'):
                alt = translated(media, track, edits).get('alt')
                path = OUT + name.removesuffix('.jpg') + '.' + track + '.svg'
                rendered = vector(key, track, alt)
                generated[path] = rendered
                outputs[track] = {'path': path, 'sha256': sha(rendered), 'mime_type': 'image/svg+xml'}
            records.append({'source_media_id': media_id, 'source_src': '../../media/' + name,
                            'source_git_blob': blob, 'source_sha256': digest, 'mime_type': 'image/jpeg',
                            'outputs': outputs})
    manifest = {'schema': 'jv-unit-assets-v1', 'unit': UNIT,
                'status': 'vector_draft_preparation_not_reader_integrated_not_visually_approved',
                'source_commit': UPSTREAM_COMMIT, 'edits_sha256': sha(edits_path.read_bytes()), 'assets': records,
                'decisions': [
                    'Exact English source JPEG retained for unchanged Indonesian source-track media; the two Javanese registers get native vector derivatives.',
                    'Longer Javanese base labels are reflowed; arrow direction, base/exponent position, factor order and whole-product brace remain. Not pixel-identical geometry or original typography.',
                    'Red/teal label roles retained with darker colors; no claim of browser readability or human visual approval.',
                    '003 explains three equal factors, consistent with corrected Indonesian source, not three additional binary multiplications.',
                    '004 retains all four explicitly printed a factors with a finite n-factor ellipsis; Javanese alt corrects the inherited omitted pre-ellipsis factor.',
                    'Per-output MIME types differ. Future reader integration must use each output mime_type, not the source JPEG MIME for all tracks.',
                    'C21 ping and C34 rambang were fully reread while checking source, labels and factor meaning. Basis/eksponen/pangkat and complete wording remain provisional.'
                ], 'synthesized_audio_files': 0, 'whole_module_complete': False}
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
    print('Two exact exponent JPEGs and four source-bound Javanese SVG drafts checked; reader integration and visual review pending.')


if __name__ == '__main__':
    main()
