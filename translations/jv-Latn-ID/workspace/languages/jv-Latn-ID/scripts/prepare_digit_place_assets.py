"""Prepare the two m81243/fs-id1883656 charts from pinned local Git blobs.

Only registered SVG text and root xml:lang are changed. Geometry, styles, IDs,
numeric cells, and operator text are invariant. No network or shared writes.
--check reconstructs all products in memory and compares existing bytes.
"""
import argparse
import hashlib
import html
import json
import os
import re
import subprocess
import xml.etree.ElementTree as ET

from config import DOWNLOADS, LANG, UPSTREAM_COMMIT
from safe_io import write_bytes


A00_COMMIT = '3de9207f56f8b5c57c017abf973fb04e00d740f1'
SECTION = 'fs-id1883656'
OUT = 'translation/assets/a00-digit-place/'
MANIFEST = 'translation/a00-digit-place.assets.json'
XML_LANG = '{http://www.w3.org/XML/1998/namespace}lang'
SVG = '{http://www.w3.org/2000/svg}'
TRACKS = ('id-academic', 'jv-academic', 'jv-conversation')
SOURCES = [
    {'key': '011', 'media_id': 'fs-id1339846', 'figure_id': 'CNX_BMath_Figure_01_01_011',
     'pivot_blob': 'c7fd63689cb359befc7169687a4c205d116f6c86',
     'original_blob': '6c112f73c84b2b70e17b537d87086bba8f729e82', 'example': '5,278,194'},
    {'key': '012_img', 'media_id': 'fs-id2297687', 'figure_id': None,
     'pivot_blob': '023b6451c55ca24039a23c9fb26e4a8ba1fd5a76',
     'original_blob': 'b0367727073e7bb77665d0b2f88d304fd6af867c', 'example': '63,407,218'},
]

# Exact Indonesian source, academic Javanese, conversational Javanese.
# Concise chart labels intentionally match across Javanese registers. Only the
# description differs in register; no implicit untranslated-language fallback.
LABELS = [
    ('Bagan Nilai Tempat', 'Bagan Nilai Panggonan', 'Bagan Nilai Panggonan'),
    ('Bagan lima belas kolom untuk triliun, miliar, juta, ribuan, dan satuan beserta digit contoh.',
     'Bagan limalas kolom kanggo trilyun, milyar, yuta, éwuan, lan satuan, karo digit conto.',
     'Bagan iki ana limalas kolom kanggo trilyun, milyar, yuta, éwuan, lan satuan, karo conto digit.'),
    ('Nilai Tempat', 'Nilai Panggonan', 'Nilai Panggonan'),
    ('Triliun', 'Trilyun', 'Trilyun'),
    ('Miliar', 'Milyar', 'Milyar'),
    ('Juta', 'Yuta', 'Yuta'),
    ('Ribuan', 'Éwuan', 'Éwuan'),
    ('Satuan', 'Satuan', 'Satuan'),
    ('Ratusan triliun', 'Atusan trilyun', 'Atusan trilyun'),
    ('Sepuluh triliun', 'Sepuluh trilyun', 'Sepuluh trilyun'),
    ('triliun', 'trilyun', 'trilyun'),
    ('Ratusan miliar', 'Atusan milyar', 'Atusan milyar'),
    ('Sepuluh miliar', 'Sepuluh milyar', 'Sepuluh milyar'),
    ('miliar', 'milyar', 'milyar'),
    ('Seratus juta', 'Satus yuta', 'Satus yuta'),
    ('Sepuluh juta', 'Sepuluh yuta', 'Sepuluh yuta'),
    ('jutaan', 'yutanan', 'yutanan'),
    ('Seratus ribu', 'Satus éwu', 'Satus éwu'),
    ('Sepuluh ribu', 'Sepuluh éwu', 'Sepuluh éwu'),
    ('ribuan', 'éwuan', 'éwuan'),
    ('ratusan', 'atusan', 'atusan'),
    ('puluhan', 'puluhan', 'puluhan'),
    ('satuan', 'satuan', 'satuan'),
]


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def blob_sha1(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def git(repo, *args):
    env = dict(os.environ, GIT_NO_LAZY_FETCH='1', GIT_OPTIONAL_LOCKS='0', GIT_TERMINAL_PROMPT='0')
    return subprocess.check_output(['git', '-C', str(DOWNLOADS / repo), *args], env=env)


def pinned_blob(repo, commit, path, expected):
    raw = git(repo, 'show', commit + ':' + path)
    if blob_sha1(raw) != expected:
        raise ValueError('Unexpected pinned source blob: ' + path)
    return raw


def text_nodes(raw):
    root = ET.fromstring(raw)
    allowed = {SVG + 'text', SVG + 'title', SVG + 'desc'}
    for node in root.iter():
        if node.text and node.text.strip() and node.tag not in allowed:
            raise ValueError('Unregistered SVG text-bearing node: ' + node.tag)
    return [node for node in root.iter() if node.tag in allowed]


def geometry_signature(raw):
    root = ET.fromstring(raw)
    return [(node.tag, sorted((key, value) for key, value in node.attrib.items()
                             if not (node is root and key == XML_LANG)), len(node))
            for node in root.iter()]


def localize(raw, track):
    if track not in ('jv-academic', 'jv-conversation'):
        raise ValueError('Explicit Javanese register required')
    mapping = {row[0]: row[1 if track == 'jv-academic' else 2] for row in LABELS}
    if len(mapping) != len(LABELS):
        raise ValueError('Duplicate registered label')
    values = [node.text or '' for node in text_nodes(raw)]
    if set(mapping) - set(values):
        raise ValueError('A reviewed source label is missing')
    for value in values:
        if value not in mapping and not re.fullmatch(r'[0-9]+', value):
            raise ValueError('Unregistered linguistic SVG label: ' + value)
    text = raw.decode('utf-8')
    if text.count('xml:lang="id-ID"') != 1:
        raise ValueError('Unexpected source SVG locale')
    text = text.replace('xml:lang="id-ID"', 'xml:lang="jv-Latn-ID"')
    for old, new in mapping.items():
        source = '>' + html.escape(old, quote=False) + '<'
        if text.count(source) != 1:
            raise ValueError('Nonunique SVG label: ' + old)
        text = text.replace(source, '>' + html.escape(new, quote=False) + '<')
    output = text.encode('utf-8')
    if geometry_signature(raw) != geometry_signature(output):
        raise ValueError('SVG geometry, hierarchy, IDs, or non-language attributes changed')
    after = [node.text or '' for node in text_nodes(output)]
    if after != [mapping.get(value, value) for value in values]:
        raise ValueError('Unexpected text substitution')
    if re.findall(r'\d+|[$×+=−÷]', '\n'.join(values)) != re.findall(r'\d+|[$×+=−÷]', '\n'.join(after)):
        raise ValueError('SVG numeric/operator text changed')
    return output


def source_scope():
    paths = [
        ('a00-id', A00_COMMIT, '90def09ee1dbfdc66aa8bc910938ad7684668e97'),
        ('openstax-prealgebra-bundle', UPSTREAM_COMMIT, '612244f80ecb6bce0f811c9d99204ae2f9f7a4f5'),
    ]
    result = {}
    for repo, commit, expected in paths:
        raw = pinned_blob(repo, commit, 'modules/m81243/index.cnxml', expected)
        section = ET.fromstring(raw).find('.//*[@id="' + SECTION + '"]')
        if section is None:
            raise ValueError('Source section absent')
        actual = [(media.get('id'), image.get('src')) for media in section.iter()
                  if media.tag.endswith('}media') for image in media if image.tag.endswith('}image')]
        wanted = [(source['media_id'], '../../media/CNX_BMath_Figure_01_01_' + source['key'] + '.jpg'
                   + ('.id-ID.svg' if repo == 'a00-id' else '')) for source in SOURCES]
        if actual != wanted:
            raise ValueError('Source media scope or order changed')
        result[repo] = {'commit': commit, 'module_path': 'modules/m81243/index.cnxml',
                        'git_blob_sha1': expected, 'module_sha256': sha256(raw)}
    return result


def products():
    scope = source_scope()
    manifest = {
        'schema': 'jv-digit-place-assets-v1', 'program': 'A00', 'module': 'm81243', 'section_id': SECTION,
        'scope': 'Both chart references in the complete digit-place section. Asset preparation does not complete the section, book, or full assignment.',
        'sources': scope,
        'source_hash_basis': 'Exact pinned Git blob bytes; no Windows checkout normalization.',
        'credit': 'Copyright Rice University, OpenStax, under CC BY-NC-SA 4.0 license. Indonesian SVG adaptations: KokunoYumeto; Javanese text-label adaptation: this unofficial AI-assisted draft. Full inherited component notices remain controlling; no endorsement implied.',
        'consultations': [
            {'id': 'C19', 'path': 'downloads/jv-Latn-ID/canon/atus.txt',
             'stages': ['label drafting', 'source-to-label comparison', 'final label QA'],
             'decision': 'Read atusan, satus, and rong atus in the actual entry. These support the hundreds vocabulary, not every compound chart label. The incidental karobelah/éwu usage is not treated as full orthographic authority for the large-number register.'},
            {'id': 'C20', 'path': 'downloads/jv-Latn-ID/canon/enggon.txt',
             'stages': ['label drafting', 'final label QA'],
             'decision': 'Read enggon/panggonan place/location senses. Nilai panggonan remains an explicitly provisional mathematical compound.'},
            {'id': 'C01', 'path': 'downloads/jv-Latn-ID/canon/wilangan.txt',
             'stages': ['source-to-label comparison'],
             'decision': 'Read count/number senses; do not conflate example digits with names of place-value periods.'},
            {'id': 'C24', 'path': 'downloads/jv-Latn-ID/canon/ewu.txt',
             'stages': ['topic-driven spelling revision', 'label QA'],
             'decision': 'The dedicated entry supports éwu/éwuan; revise only Javanese labels, preserving inherited geometry and Indonesian source bytes.'},
            {'id': 'C25', 'path': 'downloads/jv-Latn-ID/canon/yuta.txt',
             'stages': ['topic-driven spelling revision', 'label QA'],
             'decision': 'Yuta is directly supported as million; yutanan and composed place labels remain provisional.'},
        ],
        'register_decisions': {
            'same_short_labels': 'Concise place-value labels intentionally match in both Javanese registers; descriptions differ. Both outputs declare jv-Latn-ID explicitly.',
            'unstandardized': ['nilai panggonan', 'yutanan', 'milyar', 'trilyun', 'satuan', 'puluhan'],
            'spelling': 'Matches the current section draft, including dedicated C24 éwu/éwuan spelling. Mathematical compounds and register remain subject to native review.',
            'geometry_basis': 'Inherited Indonesian SVG geometry, not pixel identity with the canonical English JPEG. The Indonesian edition already redrew both charts.',
        },
        'qa': {
            'source_review': '2026-08-30: original JPEGs inspected, every Indonesian SVG title/description/text node read, all source references compared in both full section trees.',
            'preserved': ['hierarchy', 'all IDs', 'all non-language attributes', 'coordinate/path/rotation/style attributes', 'numeric/operator tokens', 'digit cell positions', 'source media order'],
            'visual_review_of_derivatives': False, 'human_language_review': False,
            'listening_review': False, 'full_assignment_complete': False,
            'output_policy': 'Per-file atomic writes only after every product validates; --check never writes. Both product passes must match byte-for-byte.',
        },
        'assets': [],
    }
    generated = {}
    for source in SOURCES:
        original_name = 'CNX_BMath_Figure_01_01_' + source['key'] + '.jpg'
        name = original_name + '.id-ID.svg'
        raw = pinned_blob('a00-id', A00_COMMIT, 'media/' + name, source['pivot_blob'])
        original = pinned_blob('a00-id', A00_COMMIT, 'media/' + original_name, source['original_blob'])
        canonical_oid = git('openstax-prealgebra-bundle', 'rev-parse', UPSTREAM_COMMIT + ':media/' + original_name).decode('ascii').strip()
        if canonical_oid != source['original_blob']:
            raise ValueError('Canonical JPEG identity mismatch')
        digits = [node for node in text_nodes(raw) if re.fullmatch(r'[0-9]+', node.text or '')]
        if ''.join(node.text for node in digits) != source['example'].replace(',', ''):
            raise ValueError('Source chart example digit order mismatch')
        entry = {
            'source_src': '../../media/' + name, 'media_id': source['media_id'], 'figure_id': source['figure_id'],
            'mime_type': 'image/svg+xml',
            'indonesian_source': {'path': 'media/' + name, 'git_blob_sha1': source['pivot_blob'], 'sha256': sha256(raw), 'bytes': len(raw), 'locale': 'id-ID'},
            'canonical_original': {'path': 'media/' + original_name, 'git_blob_sha1': source['original_blob'], 'sha256': sha256(original), 'bytes': len(original), 'contains_linguistic_text': True},
            'example': source['example'], 'column_count': 15, 'leading_empty_digit_cells': 15 - len(digits),
            'digit_cells': [{'text': node.text, 'x': node.get('x'), 'y': node.get('y')} for node in digits],
            'outputs': {},
        }
        for track in TRACKS:
            output = raw if track == 'id-academic' else localize(raw, track)
            path = OUT + (name if track == 'id-academic' else original_name + '.' + track + '.svg')
            generated[path] = output
            value = {'path': path, 'sha256': sha256(output), 'bytes': len(output),
                     'locale': 'id-ID' if track == 'id-academic' else 'jv-Latn-ID',
                     'contains_linguistic_text': True, 'contains_untranslated_linguistic_text': False,
                     'derivative_type': 'source-byte-retention' if track == 'id-academic' else 'registered-svg-text-substitution'}
            if track != 'id-academic':
                index = 1 if track == 'jv-academic' else 2
                value['substitutions'] = [{'source': row[0], 'target': row[index],
                                          'status': 'explicit-shared-technical-wording' if row[0] == row[index] else 'translated-draft'} for row in LABELS]
            entry['outputs'][track] = value
        manifest['assets'].append(entry)
    manifest['qa']['asset_file_count'] = len(generated)
    manifest['qa']['asset_bytes'] = sum(map(len, generated.values()))
    generated[MANIFEST] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    if len(generated) != 7 or sum(map(len, generated.values())) > 250_000:
        raise ValueError('Unexpected output scope or size')
    return generated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Validate exact current output bytes without writing')
    args = parser.parse_args()
    generated = products()
    if generated != products():
        raise ValueError('Nondeterministic digit-place asset products')
    for relative, raw in generated.items():
        path = LANG / relative
        if args.check:
            if path.read_bytes() != raw:
                raise ValueError('Stale or changed asset: ' + relative)
        else:
            write_bytes(path, raw)
    print(('Checked' if args.check else 'Prepared') + ' 2 source charts, 6 SVGs and 1 manifest; geometry/numbers invariant; human and rendered review pending.')


if __name__ == '__main__':
    main()
