"""Retain and localize the nine A00 m81243/fs-id2340048 assets, offline.

Only SVG text-node content and xml:lang are changed. Numeric-only JPEGs and
Indonesian SVGs are retained as their exact pinned Git blob bytes. The output
manifest records each source reference and derivative, including shared draft
technical terms. This does not render the new SVGs or certify their language.
"""
import hashlib
import html
import json
import os
import re
import subprocess
import xml.etree.ElementTree as ET

from config import DOWNLOADS, LANG, UPSTREAM_COMMIT
from safe_io import write_bytes, write_text


A00_COMMIT = '3de9207f56f8b5c57c017abf973fb04e00d740f1'
SECTION = 'fs-id2340048'
SVG_NS = '{http://www.w3.org/2000/svg}'
XML_LANG = '{http://www.w3.org/XML/1998/namespace}lang'
OUT = LANG / 'translation' / 'assets' / 'a00-place-value'
MANIFEST = LANG / 'translation' / 'a00-place-value.assets.json'
TRACKS = ('id-academic', 'jv-academic', 'jv-conversation')
ASSETS = [
    ('002', 'fs-id1302206', 'CNX_BMath_Figure_01_01_002', '9ab68936ec41534e35c9f1a085643ea9edc6fd6e', '6f49f8ad5f272db6df92734a7762034b327c4e14'),
    ('003_img', 'fs-id2438560', None, '449c3d28af60a1043596a3bdb79ab25c7ba5a3c9', '449c3d28af60a1043596a3bdb79ab25c7ba5a3c9'),
    ('004', 'fs-id2294051', 'CNX_BMath_Figure_01_01_004', 'ed17253f44cd2afec046b052c018c631fb1641ed', '0f9875886cb6cdf2b75222052b5683c285eece81'),
    ('005', 'fs-id1823977', 'CNX_BMath_Figure_01_01_005', '580f6c4fca11b1c5bb60facf88f3655ad2c4aca5', '1f5c82729f0d3fc5afafefb49b426f3589e29b96'),
    ('006_img', 'fs-id2387933', None, 'e2d18f74c96196042cef2519a0d5672ee22beee8', 'e2d18f74c96196042cef2519a0d5672ee22beee8'),
    ('007_img', 'fs-id2482064', None, 'e576d1c2b928355b6a473644e507cc0e4075b233', 'e576d1c2b928355b6a473644e507cc0e4075b233'),
    ('008_img', 'fs-id2164193', None, '9816fcd002799e96419b2c70c09a43193ad7e07e', '9816fcd002799e96419b2c70c09a43193ad7e07e'),
    ('009_img', 'fs-id4224006', None, '4c6168770250e23ad95dff1e8f37c233b74b5991', '4c6168770250e23ad95dff1e8f37c233b74b5991'),
    ('010_img', 'fs-id1841537', None, '5541acef5ca7f7bf733d1218d467119f6b15012f', '5541acef5ca7f7bf733d1218d467119f6b15012f'),
]

# Each tuple is (exact Indonesian text, academic Javanese, conversational
# Javanese). Identical technical terms are an explicit provisional choice,
# not an unnoticed translation fallback. Numerals and operators stay intact.
LABELS = {
    '002': [
        ('Nilai tiga kelompok uang kertas', 'Nilai telung klompok dhuwit kertas', 'Nilai dhuwit kertas ing telung klompok'),
        ('Tiga lembar uang seratus dolar bernilai tiga ratus dolar; tujuh lembar uang sepuluh dolar bernilai tujuh puluh dolar; empat lembar uang satu dolar bernilai empat dolar.',
         'Telung lembar dhuwit satus dolar regane telung atus dolar; pitung lembar dhuwit sepuluh dolar regane pitung puluh dolar; patang lembar dhuwit sadolar regane patang dolar.',
         'Dhuwit satus dolar telung lembar regane telung atus dolar; dhuwit sepuluh dolar pitung lembar regane pitung puluh dolar; dhuwit sadolar patang lembar regane patang dolar.'),
        ('Tiga lembar uang $100', 'Telung lembar dhuwit $100', 'Dhuwit $100 telung lembar'),
        ('Tujuh lembar uang $10', 'Pitung lembar dhuwit $10', 'Dhuwit $10 pitung lembar'),
        ('Empat lembar uang $1', 'Patang lembar dhuwit $1', 'Dhuwit $1 patang lembar'),
    ],
    '004': [
        ('Blok basis sepuluh', 'Blok basis sepuluh', 'Blok basis sepuluh'),
        ('Satu blok mewakili satu, satu batang sepuluh blok mewakili sepuluh, dan satu persegi seratus blok mewakili seratus.',
         'Siji blok makili siji, siji batang isi sepuluh blok makili sepuluh, lan siji persegi isi satus blok makili satus.',
         'Blok siji makili siji, batang siji isi sepuluh blok makili sepuluh, lan persegi siji isi satus blok makili satus.'),
        ('Satu blok', 'Siji blok', 'Blok siji'),
        ('mewakili 1:', 'makili 1:', 'makili 1:'),
        ('Satu batang', 'Siji batang', 'Batang siji'),
        ('mewakili 10:', 'makili 10:', 'makili 10:'),
        ('Satu persegi', 'Siji persegi', 'Persegi siji'),
        ('mewakili 100:', 'makili 100:', 'makili 100:'),
    ],
    '005': [
        ('Blok basis sepuluh untuk 138', 'Blok basis sepuluh kanggo 138', 'Blok basis sepuluh kanggo 138'),
        ('Satu persegi ratusan, tiga batang puluhan, dan delapan blok satuan menyatakan bilangan 138.',
         'Siji persegi atusan, telung batang puluhan, lan wolung blok satuan makili wilangan 138.',
         'Persegi atusan siji, batang puluhan telu, lan blok satuan wolu nggambarake wilangan 138.'),
        ('1 ratusan', '1 atusan', '1 atusan'),
        ('3 puluhan', '3 puluhan', '3 puluhan'),
        ('8 satuan', '8 satuan', '8 satuan'),
    ],
}

VISUAL_FACTS = {
    '003_img': 'Only $300 + $70 + $4 and $374, with red place-value digits and arrows. No linguistic text.',
    '006_img': 'Only 100 + 30 + 8 and 138, with red place-value digits and arrows. No linguistic text.',
    '007_img': 'Two 10-by-10 squares, one 10-block rod, five unit blocks: 215. No text.',
    '008_img': 'Only 200 + 10 + 5 and 215, with red place-value digits and arrows. No linguistic text.',
    '009_img': 'One 10-by-10 square, seven 10-block rods, six unit blocks: 176. No text.',
    '010_img': 'Two 10-by-10 squares, three 10-block rods, seven unit blocks: 237. No text.',
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def git(repo, *args):
    # A missing partial-clone blob is an error, never permission to fetch.
    env = dict(os.environ, GIT_NO_LAZY_FETCH='1', GIT_TERMINAL_PROMPT='0')
    return subprocess.check_output(['git', '-C', str(DOWNLOADS / repo), *args], env=env)


def blob(repo, commit, path, expected=None):
    data = git(repo, 'show', commit + ':' + path)
    if expected is not None and git_blob_sha1(data) != expected:
        raise ValueError('Unexpected pinned blob: ' + path)
    return data


def svg_signature(data):
    root = ET.fromstring(data)
    return [(el.tag, sorted((key, val) for key, val in el.attrib.items() if key != XML_LANG), len(el))
            for el in root.iter()]


def text_values(data):
    root = ET.fromstring(data)
    allowed = {SVG_NS + 'title', SVG_NS + 'desc', SVG_NS + 'text'}
    return [el.text or '' for el in root.iter() if el.tag in allowed]


def localize_svg(data, key, track):
    source_text = data.decode('utf-8')
    values = text_values(data)
    mapping = {entry[0]: entry[1 if track == 'jv-academic' else 2] for entry in LABELS[key]}
    if len(mapping) != len(LABELS[key]):
        raise ValueError('Duplicate label mapping')
    for value in values:
        if value not in mapping and not re.fullmatch(r'[\d$×+ =.,:\-]+', value):
            raise ValueError('Unregistered linguistic SVG text: ' + value)
    if set(mapping) - set(values):
        raise ValueError('A registered source label is absent')
    output = source_text
    if output.count('xml:lang="id-ID"') != 1:
        raise ValueError('Unexpected source SVG language declaration')
    output = output.replace('xml:lang="id-ID"', 'xml:lang="jv-Latn-ID"')
    for old, new in mapping.items():
        before = '>' + html.escape(old, quote=False) + '<'
        after = '>' + html.escape(new, quote=False) + '<'
        if output.count(before) != 1:
            raise ValueError('Label replacement is not unique: ' + old)
        output = output.replace(before, after)
    result = output.encode('utf-8')
    if svg_signature(data) != svg_signature(result):
        raise ValueError('SVG hierarchy, geometry, style, or IDs changed')
    if re.findall(r'\d+|[$×+=]', '\n'.join(values)) != re.findall(r'\d+|[$×+=]', '\n'.join(text_values(result))):
        raise ValueError('SVG numeric/operator text changed')
    if text_values(result) != [mapping.get(value, value) for value in values]:
        raise ValueError('SVG text substitution mismatch')
    return result


def prepare():
    module = blob('a00-id', A00_COMMIT, 'modules/m81243/index.cnxml')
    upstream_module = blob('openstax-prealgebra-bundle', UPSTREAM_COMMIT, 'modules/m81243/index.cnxml')
    section = ET.fromstring(module).find('.//*[@id="' + SECTION + '"]')
    upstream_section = ET.fromstring(upstream_module).find('.//*[@id="' + SECTION + '"]')
    if section is None or upstream_section is None:
        raise ValueError('Pinned place-value section missing')
    actual_refs = [(media.get('id'), image.get('src'), image.get('mime-type'))
                   for media in section.iter() if media.tag.endswith('}media')
                   for image in media if image.tag.endswith('}image')]
    expected_refs = [(media_id, '../../media/CNX_BMath_Figure_01_01_' + key + '.jpg' + ('.id-ID.svg' if key in LABELS else ''),
                      'image/svg+xml' if key in LABELS else 'image/jpeg')
                     for key, media_id, _, _, _ in ASSETS]
    if actual_refs != expected_refs:
        raise ValueError('Section media scope/order differs from reviewed nine references')
    upstream_refs = [(media.get('id'), image.get('src'))
                     for media in upstream_section.iter() if media.tag.endswith('}media')
                     for image in media if image.tag.endswith('}image')]
    if upstream_refs != [(mid, '../../media/CNX_BMath_Figure_01_01_' + key + '.jpg') for key, mid, _, _, _ in ASSETS]:
        raise ValueError('Canonical media anchors do not match the reviewed source')
    report = {
        'schema': 'jv-place-value-assets-1', 'program': 'A00', 'module': 'm81243', 'section_id': SECTION,
        'scope': 'All nine media references in the complete place-value modeling section; not the full module/book.',
        'source_hash_basis': 'Exact Git blob bytes, not Windows checkout newline transformations.',
        'indonesian_repository': 'https://github.com/KokunoYumeto/openstax-prealgebra-2e-id-ID',
        'indonesian_commit': A00_COMMIT,
        'canonical_repository': 'https://github.com/openstax/osbooks-prealgebra-bundle',
        'canonical_commit': UPSTREAM_COMMIT,
        'indonesian_module_blob_sha1': git_blob_sha1(module),
        'canonical_module_blob_sha1': git_blob_sha1(upstream_module),
        'credit': 'Copyright Rice University, OpenStax, under CC BY-NC-SA 4.0 license. Indonesian SVG adaptations: KokunoYumeto; Javanese text-label adaptation: this unofficial AI-assisted draft. No separate figure credit appears in this selected source section. Full retained notices remain controlling; no endorsement implied.',
        'consultations': [
            {'source': 'downloads/jv-Latn-ID/canon/atus.txt', 'stage': 'source reading, label drafting, label QA',
             'decision': 'Read actual KBJI text: atusan is attested for hundreds; satus for one hundred. Using atusan as a mathematical place-value label remains a provisional pedagogical extension.'},
            {'source': 'downloads/jv-Latn-ID/canon/cacah.txt', 'stage': 'source reading and label drafting',
             'decision': 'Use the count/quantity sense, not chopping. Counts in all nine figures remain unchanged.'},
            {'source': 'downloads/jv-Latn-ID/canon/tengen.txt', 'stage': 'source-to-diagram comparison',
             'decision': 'The relevant direction is tengen, not the sleep-related tengèn homograph. Source left-to-right grouping remains unchanged.'},
        ],
        'register_decisions': {
            'academic': 'Provisional ngoko-based instructional register; compact numeral-before-object SVG labels.',
            'conversation': 'Ngoko object-before-count labels where appropriate; same mathematical content.',
            'unstandardized_terms': ['basis', 'blok', 'batang', 'persegi', 'puluhan', 'satuan', 'dolar'],
            'shared_label_policy': 'Shared technical loans are explicitly mapped even when spelling equals Indonesian. They are not claimed to be KBJI-attested or a standardized academic register.',
            'currency_policy': 'Preserve original dollar denominations, symbols, and multiplications; no rupiah conversion or changed scenario.',
        },
        'qa': {
            'source_images_inspected': '2026-08-30: all nine original JPEGs inspected using local-image viewing; all six unchanged JPEGs contain no linguistic text.',
            'source_svg_review': 'Parsed every title, description, and text node in the three inherited Indonesian SVGs.',
            'geometry_basis': 'The three inherited Indonesian SVGs, not pixel identity to the original English JPEGs. Figure 002 was already redrawn in the Indonesian edition.',
            'preservation': 'All SVG element names, hierarchy, IDs, non-language attributes, numeric/operator text, and order compared exactly. Only registered text and root xml:lang may differ.',
            'new_svg_visual_review': 'Pending: no rendered review or clipping certification is claimed.',
            'native_language_review': 'Pending; all new Javanese labels and narration descriptions are draft.',
            'narration': 'The manifest descriptions do not replace translated source alt text or per-register narration; builder integration remains separate.',
        },
        'assets': [],
    }
    pending = {}
    for key, media_id, figure_id, expected_pivot, expected_original in ASSETS:
        original_name = 'CNX_BMath_Figure_01_01_' + key + '.jpg'
        source_name = original_name + ('.id-ID.svg' if key in LABELS else '')
        source_path = 'media/' + source_name
        data = blob('a00-id', A00_COMMIT, source_path, expected_pivot)
        # The complete Indonesian clone retains all original JPEG bytes. Verify
        # against the canonical tree without materializing its sparse media.
        original = blob('a00-id', A00_COMMIT, 'media/' + original_name, expected_original)
        canonical_oid = git('openstax-prealgebra-bundle', 'rev-parse', UPSTREAM_COMMIT + ':media/' + original_name).decode('ascii').strip()
        if canonical_oid != expected_original:
            raise ValueError('Canonical original image witness mismatch')
        entry = {
            'source_src': '../../' + source_path, 'media_id': media_id, 'figure_id': figure_id,
            'mime_type': 'image/svg+xml' if key in LABELS else 'image/jpeg',
            'indonesian_source': {'path': source_path, 'git_blob_sha1': expected_pivot, 'sha256': sha256(data), 'bytes': len(data), 'locale': 'id-ID' if key in LABELS else 'zxx'},
            'canonical_original': {'path': 'media/' + original_name, 'git_blob_sha1': expected_original, 'sha256': sha256(original), 'bytes': len(original), 'contains_linguistic_text': key in LABELS},
            'outputs': {},
        }
        for track in TRACKS:
            if key not in LABELS:
                output_name, output = original_name, data
            elif track == 'id-academic':
                output_name, output = source_name, data
            else:
                output_name = original_name + '.' + track + '.svg'
                output = localize_svg(data, key, track)
            path = OUT / output_name
            if path in pending and pending[path] != output:
                raise ValueError('Output path collision')
            pending[path] = output
            derivative = {
                'path': path.relative_to(LANG).as_posix(), 'sha256': sha256(output), 'bytes': len(output),
                'locale': ('id-ID' if track == 'id-academic' else 'jv-Latn-ID') if key in LABELS else 'zxx',
                'contains_linguistic_text': key in LABELS,
                'contains_untranslated_linguistic_text': False,
                'derivative_type': ('source-byte-retention' if track == 'id-academic' else 'registered-svg-text-substitution') if key in LABELS else 'source-byte-retention',
            }
            if key in LABELS and track != 'id-academic':
                index = 1 if track == 'jv-academic' else 2
                derivative['substitutions'] = [{'source': label[0], 'target': label[index], 'status': 'provisional-shared-technical-wording' if label[0] == label[index] else 'translated-draft'} for label in LABELS[key]]
            entry['outputs'][track] = derivative
        if key not in LABELS:
            entry['visual_inspection'] = VISUAL_FACTS[key]
        report['assets'].append(entry)
    report['qa']['unique_output_files'] = len(pending)
    report['qa']['unique_output_bytes'] = sum(len(data) for data in pending.values())
    manifest_text = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if report['qa']['unique_output_bytes'] + len(manifest_text.encode('utf-8')) > 2_000_000:
        raise ValueError('Refusing outputs above the bounded two-megabyte allowance')
    # Validate everything before making any small, per-file atomic writes.
    for path, data in pending.items():
        write_bytes(path, data)
    write_text(MANIFEST, manifest_text)
    return report


if __name__ == '__main__':
    result = prepare()
    print('Prepared 9 source references,', result['qa']['unique_output_files'], 'unique assets,', result['qa']['unique_output_bytes'], 'asset bytes.')
