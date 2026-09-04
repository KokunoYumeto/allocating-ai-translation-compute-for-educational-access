"""Prepare only the three pinned m81243/fs-id1321580 naming diagrams.

products() is read-only and returns relative output paths mapped to bytes.
Only explicitly registered text and root xml:lang change in Javanese SVGs.
--check compares deterministic products without writing or accessing a network.
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
SECTION = 'fs-id1321580'
OUT = 'translation/assets/a00-name-whole/'
MANIFEST = 'translation/a00-name-whole.assets.json'
EDITS = 'translation/a00-name-whole.edits.json'
XML_LANG = '{http://www.w3.org/XML/1998/namespace}lang'
SVG = '{http://www.w3.org/2000/svg}'
CNXML = '{http://cnx.rice.edu/cnxml}'
MATHML = '{http://www.w3.org/1998/Math/MathML}'
TRACKS = ('id-academic', 'jv-academic', 'jv-conversation')
CHILD_IDS = [None, 'fs-id2566318', 'eip-id1168289680652', 'fs-id2220075',
             'fs-id3400199', 'fs-id1364640', 'fs-id2326974', 'fs-id2774887',
             'fs-id2136533', 'fs-id1825910', 'fs-id1628781', 'fs-id1808812']

# Source, academic Javanese, conversational Javanese. Short mathematical labels
# deliberately agree across registers; prose descriptions distinguish register.
PERIOD_LABELS = [
    ('jutaan', 'yutanan', 'yutanan'),
    ('ribuan', 'éwuan', 'éwuan'),
    ('satuan', 'satuan', 'satuan'),
]
SOURCES = [
    {
        'key': '013_img', 'media_id': 'fs-id1227744',
        'figure_id': 'eip-id1168289680652', 'parent_id': 'eip-id1168289680652',
        'top_level_anchor': 'eip-id1168289680652',
        'pivot_blob': '083883764e68f940fcba2bd75528d0ee3bd28851',
        'original_blob': 'cd49e88636f04298fbd9ff39d13a55b8febf1c5a',
        'example': '37,519,248', 'groups': ['37', '519', '248'],
        'word_labels': ['Tiga puluh tujuh juta', 'Lima ratus sembilan belas ribu',
                        'Dua ratus empat puluh delapan'],
        'word_label_commas': 0,
        'labels': [
            ('Nama bilangan 37,519,248', 'Jeneng wilangan 37,519,248', 'Jeneng wilangan 37,519,248'),
            ('Bilangan dibagi menjadi kelompok jutaan, ribuan, dan satuan, lalu setiap kelompok ditulis dengan kata-kata Indonesia.',
             'Wilangan dipisah dadi klompok yutanan, éwuan, lan satuan, banjur saben klompok ditulis nganggo tembung basa Jawa.',
             'Wilangan iki dipisah dadi klompok yutanan, éwuan, lan satuan, banjur saben klompoke ditulis nganggo tembung basa Jawa.'),
            *PERIOD_LABELS,
            ('kelompok tiga digit', 'klompok telung digit', 'klompok telung digit'),
            ('Tiga puluh tujuh juta', 'Telung puluh pitu yuta', 'Telung puluh pitu yuta'),
            ('Lima ratus sembilan belas ribu', 'Limang atus sangalas éwu', 'Limang atus sangalas éwu'),
            ('Dua ratus empat puluh delapan', 'Rong atus patang puluh wolu', 'Rong atus patang puluh wolu'),
        ],
    },
    {
        'key': '014_img', 'media_id': 'fs-id1209906', 'figure_id': None,
        'parent_id': 'eip-id1168287499693', 'top_level_anchor': 'fs-id2326974',
        'pivot_blob': 'b28077f32a345ded1f00e57dde73f635eb916241',
        'original_blob': 'df6eea606623d2fc13fe52895a91bc40adc860d1',
        'example': '8,165,432,098,710', 'groups': ['8', '165', '432', '098', '710'],
        'word_labels': ['Delapan triliun,', 'Seratus enam puluh lima miliar,',
                        'Empat ratus tiga puluh dua juta,', 'Sembilan puluh delapan ribu,',
                        'Tujuh ratus sepuluh'],
        'word_label_commas': 4,
        'labels': [
            ('Nama bilangan 8,165,432,098,710', 'Jeneng wilangan 8,165,432,098,710', 'Jeneng wilangan 8,165,432,098,710'),
            ('Bilangan dibagi menjadi kelompok triliun, miliar, jutaan, ribuan, dan satuan, lalu ditulis dengan kata-kata Indonesia.',
             'Wilangan dipisah dadi klompok trilyun, milyar, yutanan, éwuan, lan satuan, banjur ditulis nganggo tembung basa Jawa.',
             'Wilangan iki dipisah dadi klompok trilyun, milyar, yutanan, éwuan, lan satuan, banjur ditulis nganggo tembung basa Jawa.'),
            ('triliun', 'trilyun', 'trilyun'),
            ('miliar', 'milyar', 'milyar'),
            *PERIOD_LABELS,
            ('Delapan triliun,', 'Wolung trilyun,', 'Wolung trilyun,'),
            ('Seratus enam puluh lima miliar,', 'Satus sewidak lima milyar,', 'Satus sewidak lima milyar,'),
            ('Empat ratus tiga puluh dua juta,', 'Patang atus telung puluh loro yuta,', 'Patang atus telung puluh loro yuta,'),
            ('Sembilan puluh delapan ribu,', 'Sangang puluh wolu éwu,', 'Sangang puluh wolu éwu,'),
            ('Tujuh ratus sepuluh', 'Pitung atus sepuluh', 'Pitung atus sepuluh'),
        ],
    },
    {
        'key': '015_img', 'media_id': 'fs-id2670483', 'figure_id': None,
        'parent_id': 'fs-id1526255', 'top_level_anchor': 'fs-id1825910',
        'pivot_blob': 'ea18f8da00fced1e8ff733ae8d0f3018714be0dc',
        'original_blob': '9ad67dbd14591be6b1f5863b0673ed0ec5656b1b',
        'example': '327,577,529', 'groups': ['327', '577', '529'],
        'word_labels': [], 'word_label_commas': 0,
        'labels': [
            ('Kelompok bilangan 327,577,529', 'Klompok wilangan 327,577,529', 'Klompok wilangan 327,577,529'),
            ('Tiga kelompok digit berturut-turut berlabel jutaan, ribuan, dan satuan.',
             'Telung klompok digit kanthi urut diwenehi label yutanan, éwuan, lan satuan.',
             'Ana telung klompok digit sing urut, tulisane yutanan, éwuan, lan satuan.'),
            *PERIOD_LABELS,
        ],
    },
]
CONSULTATIONS = [
    ('C01', 'wilangan.txt', 'Count/number sense supports wilangan; complete pedagogical labels are not dictionary quotations.'),
    ('C05', 'telu.txt', 'Telu means three; telung in composed labels remains a productive choice, not a quotation of the complete compound.'),
    ('C07', 'lima.txt', 'Read lima and limang atus; component evidence does not certify sangalas or every cardinal compound.'),
    ('C19', 'atus.txt', 'Read atus, satus, rong atus, and pitung counting-stem examples.'),
    ('C24', 'ewu.txt', 'Dedicated entry gives éwu and éwuan; both spelling and accents are retained in every target label.'),
    ('C25', 'yuta.txt', 'Use the million sense of 1yuta, not the unrelated archaic homograph. Yutanan remains provisional.'),
    ('C26', 'wolu.txt', 'Wolu means eight; wolung in the trilyun compound remains a productive count form.'),
    ('C27', 'sanga.txt', 'Sangang puluh directly supports the ninety component of the 098 group name.'),
    ('C28', 'sewidak.txt', 'The sixty sense supports sewidak in 165; do not substitute a different variant silently.'),
]
RENDER_WITNESS = [
    {'key': '013_img', 'dimensions': [900, 210],
     'jv-academic': '81145e95a64620568f35319646dad83b780e03d6eb421c56ba6dd184f9d48d63',
     'jv-conversation': 'edefe849fe071f7af7ccde870af71aa2f638ab3f1e733a371ba8c07802b00e10',
     'rgba_pixel_sha256': '02638b4eccd11d76a1e5b2c07567be080f52e293fa423443b1dfb6401b1bc8db'},
    {'key': '014_img', 'dimensions': [1000, 280],
     'jv-academic': '1ab63d03edf6136a8e71abb7587732621a010325bbca95db9b34830ce784bc90',
     'jv-conversation': '5142917041ddc7c3b992a6a7672b37efdee559a5588c6c6ac1d53c7212dd5952',
     'rgba_pixel_sha256': '2681da3c4c33513bedb773d3ce445b7f45375baa4977a5d729cd830d56f7de26'},
    {'key': '015_img', 'dimensions': [350, 90],
     'jv-academic': 'c20768534e38dee8378ba0b3a68a00d451a0649ca142814f5eda8e70cd87c13a',
     'jv-conversation': '620b95264f5b29de11531c74d658fcdccfd12e7923635521d77c54dd8bfb091d',
     'rgba_pixel_sha256': '154a47f5e70efefa56265eacf6f2bc9d500c63b80db84c2a77fd85cc5d32d4aa'},
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
    if root.tag != SVG + 'svg':
        raise ValueError('Unexpected SVG root namespace')
    allowed = {SVG + 'text', SVG + 'title', SVG + 'desc'}
    for node in root.iter():
        if node.text and node.text.strip() and node.tag not in allowed:
            raise ValueError('Unregistered SVG text-bearing node: ' + node.tag)
        if node.tail and node.tail.strip():
            raise ValueError('Unregistered SVG tail text')
        if node.tag in allowed and len(node):
            raise ValueError('Nested SVG text is not registered')
    return [node for node in root.iter() if node.tag in allowed]


def geometry_signature(raw):
    root = ET.fromstring(raw)
    return [(node.tag, sorted((key, value) for key, value in node.attrib.items()
                             if not (node is root and key == XML_LANG)), len(node))
            for node in root.iter()]


def numeric_cells(raw):
    return [{'text': node.text, 'x': node.get('x'), 'y': node.get('y')}
            for node in text_nodes(raw)
            if node.tag == SVG + 'text' and re.fullmatch(r'[0-9]+', node.text or '')]


def punctuation_signature(raw):
    return [(node.get('x'), node.get('y'), re.findall(r'[,.;:!?]', node.text or ''))
            for node in text_nodes(raw) if node.tag == SVG + 'text']


def validate_source_svg(raw, source):
    if blob_sha1(raw) != source['pivot_blob']:
        raise ValueError('Source SVG differs from the reviewed exact blob')
    root = ET.fromstring(raw)
    if root.get(XML_LANG) != 'id-ID':
        raise ValueError('Unexpected source SVG locale')
    values = [node.text or '' for node in text_nodes(raw)]
    labels = [row[0] for row in source['labels']]
    if len(labels) != len(set(labels)) or any(values.count(label) != 1 for label in labels):
        raise ValueError('Missing, repeated, or duplicate reviewed source label')
    for value in values:
        if value not in labels and not re.fullmatch(r'[0-9]+|,', value):
            raise ValueError('Unregistered SVG text: ' + value)
    wanted = source['groups'] * (2 if source['word_labels'] else 1)
    if [cell['text'] for cell in numeric_cells(raw)] != wanted:
        raise ValueError('Digit group order or literal leading zeros changed')
    if ','.join(source['groups']) != source['example'] or values.count(',') != len(source['groups']) - 1:
        raise ValueError('Example grouping or comma separators changed')
    if sum(label.endswith(',') for label in source['word_labels']) != source['word_label_commas']:
        raise ValueError('Word-label comma convention changed')
    if source['key'] == '015_img' and any(node.tag in {SVG + 'line', SVG + 'polygon'} for node in root.iter()):
        raise ValueError('Phone-example diagram must not acquire arrow rows')


def localize(raw, track, source):
    if track not in ('jv-academic', 'jv-conversation'):
        raise ValueError('Explicit Javanese register required')
    validate_source_svg(raw, source)
    mapping = {row[0]: row[1 if track == 'jv-academic' else 2] for row in source['labels']}
    before = [node.text or '' for node in text_nodes(raw)]
    text = raw.decode('utf-8')
    if text.count('xml:lang="id-ID"') != 1:
        raise ValueError('Unexpected serialized source SVG locale')
    text = text.replace('xml:lang="id-ID"', 'xml:lang="jv-Latn-ID"')
    for old, new in mapping.items():
        token = '>' + html.escape(old, quote=False) + '<'
        if text.count(token) != 1:
            raise ValueError('Nonunique serialized SVG label: ' + old)
        text = text.replace(token, '>' + html.escape(new, quote=False) + '<')
    output = text.encode('utf-8')
    after = [node.text or '' for node in text_nodes(output)]
    if after != [mapping.get(value, value) for value in before]:
        raise ValueError('Unexpected SVG text substitution')
    if geometry_signature(raw) != geometry_signature(output):
        raise ValueError('SVG geometry, hierarchy, IDs, or non-language attributes changed')
    if numeric_cells(raw) != numeric_cells(output) or punctuation_signature(raw) != punctuation_signature(output):
        raise ValueError('SVG digit cells or visible punctuation changed')
    if re.findall(r'[0-9]+|[$×+=−÷]', '\n'.join(before)) != re.findall(r'[0-9]+|[$×+=−÷]', '\n'.join(after)):
        raise ValueError('Numeric or operator text changed, including the title')
    return output


def source_scope():
    result = {}
    for repo, commit, expected in [
        ('a00-id', A00_COMMIT, '90def09ee1dbfdc66aa8bc910938ad7684668e97'),
        ('openstax-prealgebra-bundle', UPSTREAM_COMMIT, '612244f80ecb6bce0f811c9d99204ae2f9f7a4f5'),
    ]:
        raw = pinned_blob(repo, commit, 'modules/m81243/index.cnxml', expected)
        root = ET.fromstring(raw)
        parents = {child: parent for parent in root.iter() for child in parent}
        section = root.find('.//*[@id="' + SECTION + '"]')
        if section is None or [node.get('id') for node in section] != CHILD_IDS:
            raise ValueError('Whole-number naming section boundary changed')
        siblings = list(parents[section])
        position = siblings.index(section)
        if [siblings[position - 1].get('id'), siblings[position + 1].get('id')] != ['fs-id1883656', 'fs-id1339359']:
            raise ValueError('Adjacent source section boundary changed')
        ids = [node.get('id') for node in section.iter() if node.get('id')]
        if len(ids) != 53 or len(set(ids)) != 53 or len(list(section.iter(MATHML + 'math'))) != 9:
            raise ValueError('Section ID or MathML count changed')
        media = list(section.iter(CNXML + 'media'))
        if [node.get('id') for node in media] != [source['media_id'] for source in SOURCES]:
            raise ValueError('Source media scope or order changed')
        media_witness = []
        for node, source in zip(media, SOURCES):
            images = list(node)
            suffix = '.jpg.id-ID.svg' if repo == 'a00-id' else '.jpg'
            wanted_src = '../../media/CNX_BMath_Figure_01_01_' + source['key'] + suffix
            if len(images) != 1 or images[0].tag != CNXML + 'image' or images[0].get('src') != wanted_src:
                raise ValueError('Source image reference changed')
            anchor = node
            while parents[anchor] is not section:
                anchor = parents[anchor]
            if parents[node].get('id') != source['parent_id'] or anchor.get('id') != source['top_level_anchor']:
                raise ValueError('Media parent or top-level anchor changed')
            media_witness.append({'media_id': node.get('id'), 'parent_id': parents[node].get('id'),
                                  'top_level_anchor': anchor.get('id'), 'src': wanted_src, 'alt': node.get('alt')})
        canonical = ET.canonicalize(ET.tostring(section, encoding='unicode'), strip_text=True, rewrite_prefixes=True)
        result[repo] = {'commit': commit, 'module_path': 'modules/m81243/index.cnxml',
                        'git_blob_sha1': expected, 'module_sha256': sha256(raw),
                        'section_canonical_sha256': sha256(canonical.encode('utf-8')),
                        'section_child_count': len(section), 'section_unique_id_count': len(ids),
                        'mathml_count': 9, 'media': media_witness}
    return result


def translation_witness(scope):
    raw = (LANG / EDITS).read_bytes()
    ledger = json.loads(raw)
    if ledger['source_module'] != 'm81243' or ledger['source_section'] != SECTION or ledger['tracks'] != list(TRACKS[1:]):
        raise ValueError('Translation ledger scope/register mismatch')
    phrases = {row[0]: row[1:] for row in ledger['phrases']}
    if len(phrases) != len(ledger['phrases']):
        raise ValueError('Duplicate source phrase in translation ledger')
    for source, media in zip(SOURCES, scope['a00-id']['media']):
        targets = phrases[media['alt']]
        source_quotes = re.findall('[“](.*?)[”]', media['alt'])
        for column, track in enumerate(TRACKS[1:]):
            mapping = {row[0]: row[column + 1] for row in source['labels']}
            target_quotes = re.findall('[“](.*?)[”]', targets[column])
            if len(target_quotes) != len(source_quotes):
                raise ValueError('Quoted diagram-label count changed in translated alt')
            for before, after in zip(source_quotes, target_quotes):
                if re.fullmatch(r'[0-9]+', before) and before != after:
                    raise ValueError('Quoted numeric group or leading zero changed in translated alt')
            # Alts quote the actual period/word labels. The inherited 014 alt
            # omits the word-row commas and lowercases its final word label.
            periods = [row[0] for row in source['labels']
                       if row[0] in {'triliun', 'miliar', 'jutaan', 'ribuan', 'satuan'}]
            for label in periods + source['word_labels']:
                wanted = mapping[label].rstrip(',').casefold()
                positions = [index for index, value in enumerate(source_quotes)
                             if value.casefold() == label.rstrip(',').casefold()]
                if len(positions) != 1 or target_quotes[positions[0]].casefold() != wanted:
                    raise ValueError('SVG label disagrees with translated source alt: ' + track + '/' + label)
    return {'path': EDITS, 'sha256': sha256(raw), 'bytes': len(raw),
            'check': 'Every shared period and word-row label agrees with the corresponding translated alt; source SVG punctuation is retained.'}


def products():
    scope = source_scope()
    manifest = {
        'schema': 'jv-name-whole-assets-v1', 'program': 'A00', 'module': 'm81243', 'section_id': SECTION,
        'scope': 'All three naming-diagram references in the complete section; no other section assets. This does not complete the section workflow, module, book, or assignment.',
        'previous_section': 'fs-id1883656', 'next_section': 'fs-id1339359',
        'sources': scope, 'source_hash_basis': 'Exact pinned Git blob bytes, not Windows-normalized checkout bytes.',
        'translation_witness': translation_witness(scope),
        'credit': 'Copyright Rice University, OpenStax, under CC BY-NC-SA 4.0 license. Indonesian SVG adaptations: KokunoYumeto; Javanese text-label adaptation: this unofficial AI-assisted draft. Full inherited component notices remain controlling; no endorsement implied.',
        'consultations': [{'id': key, 'path': 'downloads/jv-Latn-ID/canon/' + name,
                           'readable_sha256': sha256((DOWNLOADS / 'canon' / name).read_bytes()),
                           'stages': ['asset label drafting', 'source-to-label comparison', 'final label QA'],
                           'decision': decision} for key, name, decision in CONSULTATIONS],
        'register_decisions': {
            'shared_labels': 'Both Javanese registers intentionally share exact cardinal/period labels; only prose descriptions differ in register.',
            'unstandardized': ['yutanan', 'klompok telung digit', 'sangalas and composed cardinal phrases'],
            'technical_loans': ['satuan', 'digit', 'label', 'milyar', 'trilyun'],
            'language_metadata': 'Javanese root xml:lang is explicit; source descriptions mentioning Indonesian words are explicitly localized to basa Jawa.',
            'leading_zeros': 'Both literal 098 groups remain visible. The matching cardinal word label names ninety-eight thousand, not a leading zero digit.',
            'ones_period': 'Satuan remains a period label; it is not appended to the complete cardinal word form.',
            'geometry_basis': 'Inherited Indonesian SVG geometry, not pixel identity with canonical English JPEGs. The 013 red annotation arrow already points right in the SVG and left in the JPEG; the inherited SVG geometry is retained without a silent repair.',
        },
        'qa': {
            'checkpoint': '2026-08-31',
            'source_review': 'Read both complete source subsections and every SVG title/description/text node. Inspected all three local canonical JPEGs; local bytes matched pinned Git bytes and canonical tree identities.',
            'preserved': ['all non-language attributes', 'hierarchy and IDs', 'styles/paths/coordinates', 'all numeric groups and leading zeros', 'visible comma punctuation', 'source media order and parents'],
            'canonical_jpeg_visual_inspection': True, 'visual_review_of_derivatives': False,
            'static_render_review': {
                'date': '2026-08-31',
                'renderer': 'ImageMagick 7.1.2-26 Q16-HDRI x64 38ba210:20260621; explicit RSVG/librsvg 2.40.20',
                'arguments': ['-background', 'white', '-density', '96', 'RSVG:<absolute SVG path>', 'png:-'],
                'method': 'All six Javanese SVGs rendered in memory. Pillow RGBA byte comparison established equal academic/conversation pixels for each diagram. All three distinct rendered images were inspected; no clipped or overlapping labels observed. No PNGs written.',
                'scope': 'Static standalone SVG clipping/overlap check only; not canonical JPEG pixel equivalence, integrated-reader layout, browser compatibility, native language certification, or listening.',
                'witnesses': RENDER_WITNESS,
                'matches_current_javanese_svg_bytes': False,
            },
            'integrated_reader_layout_review': False, 'screen_reader_review': False,
            'human_language_review': False, 'listening_review': False, 'audio_synthesis_count': 0,
            'full_assignment_complete': False,
            'output_policy': 'Pure products(); two equal in-memory passes before per-file atomic writes. --check only compares bytes; not an all-files transaction.',
        },
        'assets': [],
    }
    generated = {}
    for source in SOURCES:
        original_name = 'CNX_BMath_Figure_01_01_' + source['key'] + '.jpg'
        name = original_name + '.id-ID.svg'
        raw = pinned_blob('a00-id', A00_COMMIT, 'media/' + name, source['pivot_blob'])
        validate_source_svg(raw, source)
        original = pinned_blob('a00-id', A00_COMMIT, 'media/' + original_name, source['original_blob'])
        canonical_oid = git('openstax-prealgebra-bundle', 'rev-parse', UPSTREAM_COMMIT + ':media/' + original_name).decode('ascii').strip()
        if canonical_oid != source['original_blob']:
            raise ValueError('Canonical JPEG identity mismatch')
        entry = {key: source[key] for key in ('media_id', 'figure_id', 'parent_id', 'top_level_anchor', 'example')}
        entry.update({
            'source_src': '../../media/' + name, 'mime_type': 'image/svg+xml',
            'indonesian_source': {'path': 'media/' + name, 'git_blob_sha1': source['pivot_blob'], 'sha256': sha256(raw), 'bytes': len(raw), 'locale': 'id-ID'},
            'canonical_original': {'path': 'media/' + original_name, 'git_blob_sha1': source['original_blob'], 'sha256': sha256(original), 'bytes': len(original), 'contains_linguistic_text': True},
            'top_groups': source['groups'], 'numeric_group_cells': numeric_cells(raw),
            'standalone_comma_count': len(source['groups']) - 1,
            'word_label_comma_count': source['word_label_commas'],
            'word_arrow_row_count': len(source['word_labels']),
            'word_arrow_rows': [{'group': group, 'source_label': label} for group, label in zip(source['groups'], source['word_labels'])],
            'leading_zero_cells': [cell for cell in numeric_cells(raw) if len(cell['text']) > 1 and cell['text'].startswith('0')],
            'geometry_signature_sha256': sha256(json.dumps(geometry_signature(raw), ensure_ascii=False).encode('utf-8')),
            'outputs': {},
        })
        for track in TRACKS:
            output = raw if track == 'id-academic' else localize(raw, track, source)
            path = OUT + (name if track == 'id-academic' else original_name + '.' + track + '.svg')
            generated[path] = output
            value = {'path': path, 'sha256': sha256(output), 'bytes': len(output),
                     'locale': 'id-ID' if track == 'id-academic' else 'jv-Latn-ID',
                     'contains_linguistic_text': True, 'contains_untranslated_linguistic_text': False,
                     'derivative_type': 'source-byte-retention' if track == 'id-academic' else 'registered-svg-text-substitution'}
            if track != 'id-academic':
                index = 1 if track == 'jv-academic' else 2
                value['substitutions'] = [{'source': row[0], 'target': row[index],
                                          'status': 'explicit-technical-loan' if row[0] == row[index] else 'translated-draft'}
                                         for row in source['labels']]
            entry['outputs'][track] = value
        manifest['assets'].append(entry)
    manifest['qa']['asset_file_count'] = len(generated)
    manifest['qa']['asset_bytes'] = sum(map(len, generated.values()))
    rendered_current = all(sha256(generated[OUT + 'CNX_BMath_Figure_01_01_' + witness['key']
                                           + '.jpg.' + track + '.svg']) == witness[track]
                           for witness in RENDER_WITNESS for track in TRACKS[1:])
    manifest['qa']['static_render_review']['matches_current_javanese_svg_bytes'] = rendered_current
    manifest['qa']['visual_review_of_derivatives'] = rendered_current
    generated[MANIFEST] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    if len(generated) != 10 or sum(map(len, generated.values())) > 250_000:
        raise ValueError('Unexpected output scope or size')
    return generated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Compare all product bytes without writing')
    args = parser.parse_args()
    generated = products()
    if generated != products():
        raise ValueError('Nondeterministic whole-number naming asset products')
    for relative, raw in generated.items():
        path = LANG / relative
        if args.check:
            if path.read_bytes() != raw:
                raise ValueError('Stale or changed asset: ' + relative)
        else:
            write_bytes(path, raw)
    print(('Checked' if args.check else 'Prepared') + ' 3 source diagrams, 9 SVGs and 1 manifest; geometry/groups/commas invariant; static render evidence is hash-bound; human and integrated-reader review pending.')


if __name__ == '__main__':
    main()
