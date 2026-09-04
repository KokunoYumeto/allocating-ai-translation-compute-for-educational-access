"""Exact-source text-only SVG localization for the entire writing subsection."""
import argparse
import html
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from config import DOWNLOADS, LANG, UPSTREAM_COMMIT
from safe_io import write_bytes
from prepare_name_whole_assets import (A00_COMMIT, XML_LANG, SVG, blob_sha1,
                                      geometry_signature, git, sha256, text_nodes)

UNIT = 'a00-write-whole'
SECTION = 'fs-id1339359'
LABELS = {'jutaan': 'yutanan', 'ribuan': 'éwuan', 'satuan': 'satuan',
          'miliar': 'milyar', 'miliaran': 'milyaran'}
FIGURES = [
    ('016_img', 'fs-id2668978', ['53', '401', '742'], {
        'Kata-kata menjadi 53,401,742': 'Tembung dadi 53,401,742',
        'Lima puluh tiga juta, empat ratus satu ribu, dan tujuh ratus empat puluh dua dipetakan ke kelompok digit 53, 401, dan 742.': 'Sèket telu yuta, patang atus siji éwu, lan pitung atus patang puluh loro dipetakake menyang klompok digit 53, 401, lan 742.',
        'lima puluh tiga juta': 'sèket telu yuta',
        'empat ratus satu ribu': 'patang atus siji éwu',
        'tujuh ratus empat puluh dua': 'pitung atus patang puluh loro',
    }),
    ('017_img', 'fs-id2903601', ['9', '246', '073', '189'], {
        'Kata-kata menjadi 9,246,073,189': 'Tembung dadi 9,246,073,189',
        'Empat kelompok kata-kata Indonesia dipetakan ke kelompok digit 9, 246, 073, dan 189.': 'Patang klompok tembung basa Jawa dipetakake menyang klompok digit 9, 246, 073, lan 189.',
        'sembilan miliar': 'sangang milyar',
        'dua ratus empat puluh enam juta': 'rong atus patang puluh enem yuta',
        'tujuh puluh tiga ribu': 'pitung puluh telu éwu',
        'seratus delapan puluh sembilan': 'satus wolung puluh sanga',
    }),
    ('018_img', 'fs-id1345376', ['77', '000', '000', '000'], {
        'Tujuh puluh tujuh miliar': 'Pitung puluh pitu milyar',
        'Kelompok 77 miliar diikuti tiga kelompok nol: 77,000,000,000.': 'Klompok 77 milyar diterusake telung klompok nol: 77,000,000,000.',
        '77 miliar': '77 milyar',
    }),
]


def svg_digits(raw):
    return [(node.text or '').replace(' ', '') for node in text_nodes(raw)
            if node.tag == SVG + 'text' and node.get('y') == '175']


def localize(raw, mapping):
    source = ET.fromstring(raw)
    assert source.get(XML_LANG) == 'id-ID'
    text = raw.decode('utf-8').replace('xml:lang="id-ID"', 'xml:lang="jv-Latn-ID"')
    for node in text_nodes(raw):
        value = node.text or ''
        if re.search('[A-Za-z]', value):
            assert value in mapping, f'Unregistered SVG label: {value}'
            text = text.replace('>' + html.escape(value, quote=False) + '<',
                                '>' + html.escape(mapping[value], quote=False) + '<')
    result = text.encode('utf-8')
    assert geometry_signature(raw) == geometry_signature(result)
    assert svg_digits(raw) == svg_digits(result)
    for old, new in zip(text_nodes(raw), text_nodes(result)):
        assert new.text == mapping.get(old.text, old.text)
        assert re.findall(r'\d+', old.text or '') == re.findall(r'\d+', new.text or '')
    return result


def products():
    source_raw = git('a00-id', 'show', A00_COMMIT + ':modules/m81243/index.cnxml')
    section = next(node for node in ET.fromstring(source_raw).iter() if node.get('id') == SECTION)
    source_media = section.findall('.//{*}media')
    assert [node.get('id') for node in source_media] == [row[1] for row in FIGURES]
    english_raw = git('openstax-prealgebra-bundle', 'show', UPSTREAM_COMMIT + ':modules/m81243/index.cnxml')
    english = next(node for node in ET.fromstring(english_raw).iter() if node.get('id') == SECTION)
    english_media = {node.get('id'): node for node in english.findall('.//{*}media')}
    generated, assets = {}, []
    with zipfile.ZipFile(DOWNLOADS / 'openstax-full-pinned.zip') as archive:
        prefix = 'osbooks-prealgebra-bundle-' + UPSTREAM_COMMIT + '/'
        for (key, media_id, groups, labels), media in zip(FIGURES, source_media):
            filename = 'CNX_BMath_Figure_01_01_' + key + '.jpg'
            pivot_path = 'media/' + filename + '.id-ID.svg'
            assert media.find('{*}image').get('src') == '../../' + pivot_path
            raw = git('a00-id', 'show', A00_COMMIT + ':' + pivot_path)
            assert blob_sha1(raw) == git('a00-id', 'rev-parse', A00_COMMIT + ':' + pivot_path).decode().strip()
            assert svg_digits(raw) == groups
            original_path = 'media/' + filename
            assert english_media[media_id].find('{*}image').get('src') == '../../' + original_path
            original = archive.read(prefix + original_path)
            assert blob_sha1(original) == git('openstax-prealgebra-bundle', 'rev-parse', UPSTREAM_COMMIT + ':' + original_path).decode().strip()
            target = localize(raw, {**LABELS, **labels})
            outputs = {}
            for track in ('id-academic', 'jv-academic', 'jv-conversation'):
                suffix = 'id-ID' if track == 'id-academic' else track
                path = f'translation/assets/{UNIT}/{filename}.{suffix}.svg'
                value = raw if track == 'id-academic' else target
                generated[path] = value
                outputs[track] = {'path': path, 'sha256': sha256(value), 'bytes': len(value)}
            assets.append({'media_id': media_id, 'source_src': '../../' + pivot_path,
                           'mime_type': 'image/svg+xml', 'source_svg_sha256': sha256(raw),
                           'source_svg_blob_sha1': blob_sha1(raw),
                           'canonical_path': original_path, 'canonical_sha256': sha256(original),
                           'canonical_blob_sha1': blob_sha1(original),
                           'digit_groups': groups, 'translation_labels': {**LABELS, **labels},
                           'outputs': outputs})
    manifest = {'unit': UNIT, 'section': SECTION, 'module': 'm81243',
                'a00_commit': A00_COMMIT, 'upstream_commit': UPSTREAM_COMMIT,
                'source_module_sha256': sha256(source_raw), 'english_module_sha256': sha256(english_raw),
                'status': 'deterministic_text_only_SVG_draft_visual_review_pending',
                'register_note': 'Diagram labels deliberately match across the two provisional Javanese registers; surrounding prose remains separate.',
                'canon': ['C07', 'C19', 'C24', 'C25', 'C27'],
                'source_discrepancy': 'English 017 alt points seventy-three thousand to 742; retain ID correction 073 and unchanged ID SVG geometry. Canonical raster and ID redraw are separate witnesses, not pixel-identical claims.',
                'checks': ['exact_pinned_member_blobs', 'complete_three_media_scope',
                           'complete_registered_linguistic_text', 'unchanged_geometry_and_nonlanguage_attributes',
                           'unchanged_printed_digits_including_zeroes'],
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
            assert (LANG / path).read_bytes() == raw, f'Stale asset: {path}'
        else:
            write_bytes(LANG / path, raw)
    print('Writing-number figures: three source SVGs and six target SVGs validated; visual review pending.')


if __name__ == '__main__':
    main()
