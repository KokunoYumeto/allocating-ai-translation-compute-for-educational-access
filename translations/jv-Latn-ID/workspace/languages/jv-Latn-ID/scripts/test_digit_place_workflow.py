"""Read-only A00 digit-place regression suite with explicit integration gates.

Source/asset tests and the narrow integer oracle run without a unit descriptor.
Draft replay activates when the descriptor is registered. Production narration
tests wait ONLY for the descriptor and the source-bound rules file. Once both
exist, missing/stale products and unsupported narration are failures, not skips.
The numeric oracle is a test fixture, not a production parser or evidence that
narration/large-number language is approved.
"""
import copy
import hashlib
import json
import re
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import build
import build_units
import draft_units
import prepare_digit_place_assets as asset_builder
from build import MATH, XML_LANG
from config import LANG, TRACKS
from qa import Reader


UNIT = 'a00-digit-place'
SECTION = 'fs-id1883656'
DESCRIPTOR = {'section': SECTION, 'slice': None}
EXPECTED_IDS = '''fs-id1883656 fs-id1795155 term-00009 fs-id2825467
fs-id1408851 CNX_BMath_Figure_01_01_011 fs-id1339846 fs-id930962
fs-id1891091 fs-id1256900 fs-id1581177 fs-id1738612 fs-id2218367
fs-id2851093 fs-id2281077 fs-id2297687 eip-id1168898159450 fs-id2310429
fs-id1573052 fs-id1607674 fs-id1816164 fs-id1386307 fs-id2903653
fs-id1811287 fs-id1282619 fs-id1518735 fs-id3013699 fs-id1778628
fs-id1508784 fs-id2619544 fs-id1807276'''.split()
GROUPED_FACTS = (
    ('5,278,194', 5_278_194), ('5,000,000', 5_000_000),
    ('200,000', 200_000), ('70,000', 70_000), ('8,000', 8_000),
    ('63,407,218', 63_407_218), ('27,493,615', 27_493_615),
    ('519,711,641,328', 519_711_641_328),
)
INVALID_GROUPING = (
    '', '00', '01', '0,001', '1000', '5,27,8194', '5,,278,194',
    '519,711,641,328,', ',519,711,641,328', '519,711,641,328.0',
    '-519,711,641,328', '−1', '+1', '1e3', 'NaN', '1.000',
    '519，711，641，328', '５１９,７１１', '1,000,000,000,000',
)
EXPECTED_REFS = (
    ('fs-id1339846', '../../media/CNX_BMath_Figure_01_01_011.jpg.id-ID.svg'),
    ('fs-id2297687', '../../media/CNX_BMath_Figure_01_01_012_img.jpg.id-ID.svg'),
)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def integer_fixture(token):
    """Narrow ASCII grouped-integer oracle for this section's <=12 digits.

    Commas separate groups of three, never decimals; leading zeros, signs,
    exponents, non-ASCII substitutes, and out-of-scope magnitude fail closed.
    This local oracle is deliberately NOT substituted into production code.
    """
    if not isinstance(token, str) or not re.fullmatch(r'0|[1-9][0-9]{0,2}(?:,[0-9]{3})*', token):
        raise ValueError('invalid_source_integer_fixture')
    digits = token.replace(',', '')
    if len(digits) > 12:
        raise ValueError('out_of_scope_source_integer_fixture')
    return int(digits)


def source_root():
    raw = asset_builder.pinned_blob('a00-id', asset_builder.A00_COMMIT,
                                    'modules/m81243/index.cnxml',
                                    '90def09ee1dbfdc66aa8bc910938ad7684668e97')
    return draft_units.select(raw, DESCRIPTOR)


def drafts():
    source = source_root()
    edits = json.loads((LANG / f'translation/{UNIT}.edits.json').read_text(encoding='utf-8'))
    shared = json.loads((LANG / 'translation/phrases.json').read_text(encoding='utf-8'))
    rows = {row[0]: row for row in shared['phrases']}
    for row in edits['phrases']:
        if row[0] in rows and rows[row[0]] != row:
            raise AssertionError('Conflicting shared phrase: ' + row[0])
        rows[row[0]] = row
    edits['phrases'] = list(rows.values())
    result = {'id-academic': source}
    for track in ('jv-academic', 'jv-conversation'):
        result[track] = build.translated(source, track, edits)
        draft_units.validate(source, result[track])
    return result


def media_refs(root):
    return tuple((node.get('id'), image.get('src')) for node in root.iter()
                 if node.tag.endswith('}media') for image in node if image.tag.endswith('}image'))


def digit_cells(raw):
    return [(node.text, node.get('x'), node.get('y'))
            for node in asset_builder.text_nodes(raw) if re.fullmatch(r'[0-9]+', node.text or '')]


def ssml_blocks(raw):
    result, current = {}, None
    for child in ET.fromstring(raw):
        if child.tag.endswith('}mark'):
            current = child.get('name')
        elif child.tag.endswith('}p') and current is not None:
            result[current] = ''.join(child.itertext())
    return result


class SourceAndIntegerFixtureTests(unittest.TestCase):
    def test_exact_31_source_ids_and_40_mathml_expressions(self):
        for track, root in drafts().items():
            with self.subTest(track=track):
                self.assertEqual([node.get('id') for node in root.iter() if node.get('id')], EXPECTED_IDS)
                self.assertEqual(len(set(EXPECTED_IDS)), 31)
                self.assertEqual(len(list(root.iter('{' + MATH + '}math'))), 40)
                self.assertEqual(media_refs(root), EXPECTED_REFS)

    def test_comma_grouped_source_tokens_are_exact_in_all_tracks(self):
        for track, root in drafts().items():
            tokens = [node.text for node in root.iter('{' + MATH + '}mn')]
            self.assertEqual([token for token in tokens if ',' in token], [token for token, _ in GROUPED_FACTS])
            with self.subTest(track=track):
                self.assertEqual(max(map(integer_fixture, tokens)), 519_711_641_328)

    def test_narrow_grouped_integer_fixture_is_deterministic_and_exact(self):
        for token, value in GROUPED_FACTS:
            with self.subTest(token=token):
                self.assertEqual(integer_fixture(token), value)
                self.assertEqual(integer_fixture(token), integer_fixture(token))
                groups = [int(group) for group in token.split(',')]
                recomposed = sum(group * 1000 ** power for power, group in enumerate(reversed(groups)))
                self.assertEqual(recomposed, value)
        self.assertEqual(integer_fixture('0'), 0)
        self.assertEqual(integer_fixture('999'), 999)

    def test_narrow_grouping_fixture_rejects_ambiguous_or_unreviewed_syntax(self):
        for token in INVALID_GROUPING:
            with self.subTest(token=token), self.assertRaises(ValueError):
                integer_fixture(token)

    def test_chart_value_and_all_fifteen_exercise_place_facts(self):
        self.assertEqual(5 * 10**6 + 2 * 10**5 + 7 * 10**4 + 8 * 10**3 + 1 * 10**2 + 9 * 10 + 4,
                         integer_fixture('5,278,194'))
        probes = (
            ('63,407,218', [(7, 3), (0, 4), (1, 1), (6, 7), (3, 6)]),
            ('27,493,615', [(2, 7), (1, 1), (4, 5), (7, 6), (5, 0)]),
            ('519,711,641,328', [(9, 9), (4, 4), (2, 1), (6, 5), (7, 8)]),
        )
        for token, answers in probes:
            digits = str(integer_fixture(token))
            for digit, power in answers:
                with self.subTest(token=token, digit=digit):
                    self.assertEqual(digits.count(str(digit)), 1, 'These source question digits are unambiguous')
                    self.assertEqual(len(digits) - 1 - digits.index(str(digit)), power)

    def test_math_punctuation_is_preserved_and_continuation_is_literal_prose(self):
        source = source_root()
        operators = [node.text for node in source.iter('{' + MATH + '}mo')]
        self.assertEqual(operators, ['.'] * 7 + [';'])
        self.assertNotIn('…', ''.join(source.itertext()), 'This section has continuation words, not an ellipsis glyph')
        for track, root in drafts().items():
            self.assertEqual([node.text for node in root.iter('{' + MATH + '}mo')], operators)
            paragraph = next(node for node in root if node.get('id') == 'fs-id1795155')
            self.assertIn('lan sateruse' if track.startswith('jv') else 'dan seterusnya', ''.join(paragraph.itertext()))

    def test_pilot_sequence_and_a10_heading_ellipsis_remain_distinct(self):
        for track in TRACKS:
            sequence = build.spoken_text('…', track.startswith('jv'))
            self.assertIn('sateruse' if track.startswith('jv') else 'seterusnya', sequence)
            heading = {'jv-academic': 'Asile yaiku…', 'jv-conversation': 'Asile…', 'id-academic': 'Hasilnya adalah…'}[track]
            spoken = build_units.speech_text(heading, track, 'a10-operation-symbols')
            self.assertTrue(spoken.endswith(':'))
            self.assertNotIn('sateruse', spoken)
            self.assertNotIn('seterusnya', spoken)

    def test_changed_grouping_id_or_punctuation_fails_draft_validation(self):
        variants = drafts()
        for mutation in ('number-grouping', 'source-id', 'punctuation'):
            target = copy.deepcopy(variants['jv-academic'])
            if mutation == 'number-grouping':
                next(node for node in target.iter('{' + MATH + '}mn') if node.text == '5,278,194').text = '5278,194'
            elif mutation == 'source-id':
                target.set('id', 'wrong-section')
            else:
                next(node for node in target.iter('{' + MATH + '}mo') if node.text == ';').text = '+'
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                draft_units.validate(variants['id-academic'], target)


class ChartAssetTests(unittest.TestCase):
    def test_all_source_reference_hashes_and_six_output_geometries(self):
        manifest = json.loads((LANG / asset_builder.MANIFEST).read_text(encoding='utf-8'))
        self.assertEqual(tuple((row['media_id'], row['source_src']) for row in manifest['assets']), EXPECTED_REFS)
        self.assertEqual(len(manifest['assets']), 2)
        for asset in manifest['assets']:
            inherited = (LANG / asset['outputs']['id-academic']['path']).read_bytes()
            self.assertEqual(sha(inherited), asset['indonesian_source']['sha256'])
            self.assertEqual(asset_builder.blob_sha1(inherited), asset['indonesian_source']['git_blob_sha1'])
            self.assertEqual(''.join(value for value, _, _ in digit_cells(inherited)), asset['example'].replace(',', ''))
            self.assertEqual(asset['leading_empty_digit_cells'], 15 - len(digit_cells(inherited)))
            for track, record in asset['outputs'].items():
                with self.subTest(example=asset['example'], track=track):
                    actual = (LANG / record['path']).read_bytes()
                    self.assertEqual(sha(actual), record['sha256'])
                    self.assertEqual(asset_builder.geometry_signature(inherited), asset_builder.geometry_signature(actual))
                    self.assertEqual(digit_cells(inherited), digit_cells(actual))
                    self.assertEqual(ET.fromstring(actual).get(XML_LANG), 'id-ID' if track == 'id-academic' else 'jv-Latn-ID')

    def test_asset_generation_is_deterministic_and_read_only(self):
        with patch.object(asset_builder, 'write_bytes', side_effect=AssertionError('Forbidden asset write')) as writer:
            first = asset_builder.products()
            self.assertEqual(first, asset_builder.products())
            self.assertEqual(len(first), 7)
            for path, raw in first.items():
                self.assertEqual((LANG / path).read_bytes(), raw, path)
            writer.assert_not_called()

    def test_coordinate_and_digit_mutations_are_detectable(self):
        manifest = json.loads((LANG / asset_builder.MANIFEST).read_text(encoding='utf-8'))
        inherited = (LANG / manifest['assets'][0]['outputs']['id-academic']['path']).read_bytes()
        for mutation in ('coordinate', 'digit'):
            changed = ET.fromstring(inherited)
            digit = next(node for node in changed.iter() if node.tag.endswith('}text') and node.text == '5')
            if mutation == 'coordinate':
                digit.set('x', '475')
            else:
                digit.text = '6'
            raw = ET.tostring(changed)
            with self.subTest(mutation=mutation):
                self.assertNotEqual(sha(raw), sha(inherited))
                if mutation == 'coordinate':
                    self.assertNotEqual(asset_builder.geometry_signature(raw), asset_builder.geometry_signature(inherited))
                self.assertNotEqual(digit_cells(raw), digit_cells(inherited))

    def test_unknown_asset_label_or_locale_fails_closed(self):
        manifest = json.loads((LANG / asset_builder.MANIFEST).read_text(encoding='utf-8'))
        raw = (LANG / manifest['assets'][0]['outputs']['id-academic']['path']).read_bytes()
        mutations = (raw.replace(b'Bagan Nilai Tempat', b'Unknown title'), raw.replace(b'xml:lang="id-ID"', b'xml:lang="en"'))
        for changed in mutations:
            with self.assertRaises(ValueError):
                asset_builder.localize(changed, 'jv-academic')


class DraftRegistrationTests(unittest.TestCase):
    def setUp(self):
        if UNIT not in draft_units.UNITS:
            self.skipTest('Production integration pending: a00-digit-place descriptor is absent; fixture/asset passes are not narration completion')

    def test_registered_draft_replay_is_current_deterministic_and_read_only(self):
        with patch.object(draft_units, 'write_bytes', side_effect=AssertionError('Forbidden draft write')) as writer:
            first = draft_units.products(UNIT)
            self.assertEqual(first, draft_units.products(UNIT))
            for path, raw in first.items():
                self.assertEqual((LANG / path).read_bytes(), raw, path)
            writer.assert_not_called()
        for track in TRACKS:
            root = ET.fromstring(first[f'translation/{UNIT}.{track}.cnxml'])
            self.assertEqual([node.get('id') for node in root.iter() if node.get('id')], EXPECTED_IDS)
            self.assertEqual(len(list(root.iter('{' + MATH + '}math'))), 40)


class ProductionIntegrationTests(unittest.TestCase):
    def setUp(self):
        if UNIT not in draft_units.UNITS:
            self.skipTest('Production narration pending: digit-place descriptor is absent')
        path = LANG / f'audio/{UNIT}.rules.json'
        if not path.is_file():
            self.skipTest('Production narration pending: digit-place source-bound rules file is absent; draft and asset tests remain active')
        self.rules = json.loads(path.read_text(encoding='utf-8'))

    def products(self):
        with (patch.object(build_units, 'write_bytes', side_effect=AssertionError('Forbidden production write')),
              patch.object(draft_units, 'write_bytes', side_effect=AssertionError('Forbidden draft write'))):
            return build_units.products(UNIT)

    def test_production_registered_integer_reading_is_deterministic_not_decimal(self):
        for track in TRACKS:
            root = drafts()[track]
            bound = build_units.source_bound_math(root, self.rules, track)
            self.assertEqual(len(bound), 40)
            expressions = {node.find('.//{' + MATH + '}mn').text: node
                           for node in root.iter('{' + MATH + '}math')
                           if node.find('.//{' + MATH + '}mn') is not None}
            for token, _ in GROUPED_FACTS:
                expression = expressions[token]
                spoken = build_units.narrate(expression, track, UNIT, bound)
                with self.subTest(token=token, track=track):
                    self.assertTrue(spoken.strip())
                    self.assertEqual(spoken, build_units.narrate(expression, track, UNIT, bound))
                    self.assertNotRegex(spoken, r'[0-9]')
                    self.assertNotIn('koma', spoken.lower(), 'Thousands separators must not be read as decimal commas')
            # Each group of the largest source integer must still be represented
            # in order. Scale names require separate native/lexicographic review.
            largest = build_units.narrate(expressions['519,711,641,328'], track, UNIT, bound)
            for alternatives in (('milyar', 'miliar'), ('yuta', 'juta'), ('ewu', 'éwu', 'èwu', 'ribu')):
                self.assertTrue(any(re.search(r'\b' + word + r'\b', largest, re.I) for word in alternatives),
                                f'Missing magnitude label {alternatives}: {largest}')
            position = 0
            for group in ('519', '711', '641', '328'):
                phrase = build.number(group, track.startswith('jv'))
                found = largest.find(phrase, position)
                self.assertGreaterEqual(found, 0, f'Missing/out-of-order whole-number group {group}: {largest}')
                position = found + len(phrase)

    def test_production_registered_integer_trees_reject_malformed_tokens(self):
        # Deliberately malformed examples, not general promises about arbitrary
        # future numbers. The selected unit contains no signed/decimal integers.
        invalid = ('5,27,8194', '5,,278,194', '519,711,641,328,',
                   '519,711,641,328.0', '-519,711,641,328', '５１９,７１１')
        for track in TRACKS:
            for token in invalid:
                changed = drafts()[track]
                next(node for node in changed.iter('{' + MATH + '}mn') if node.text == '519,711,641,328').text = token
                with self.subTest(token=token, track=track), self.assertRaises((ValueError, AssertionError)):
                    build_units.source_bound_math(changed, self.rules, track)

    def test_production_chart_narration_keeps_columns_blanks_and_digit_order(self):
        generated = self.products()
        examples = (
            ('CNX_BMath_Figure_01_01_011', '5278194', 8, 4),
            ('fs-id1891091', '63407218', 7, 2),
        )
        fixtures = self.rules['chart_fixtures']
        self.assertEqual([fixture['anchor'] for fixture in fixtures], [row[0] for row in examples])
        self.assertEqual(tuple((fixture['media_id'], fixture['source_image']) for fixture in fixtures), EXPECTED_REFS)
        for track in TRACKS:
            blocks = ssml_blocks(generated[f'review/audio/{UNIT}.{track}.ssml'])
            javanese = track.startswith('jv')
            for fixture, (anchor, digits, blanks, rows) in zip(fixtures, examples):
                with self.subTest(track=track, anchor=anchor):
                    # Source facts stay exact even when attributive count words
                    # differ from the bare cardinal (wolu -> wolung, pitu -> pitung).
                    self.assertEqual(fixture['module'], 'm81243')
                    self.assertEqual(fixture['source_declared_rows'], rows)
                    self.assertEqual(fixture['blank_columns'], list(range(1, blanks + 1)))
                    self.assertEqual(fixture['digit_cells'], [
                        {'column': column, 'digit': digit}
                        for column, digit in enumerate(digits, blanks + 1)
                    ])
                    self.assertEqual(integer_fixture(fixture['whole_number']), int(digits))
                    self.assertEqual(fixture['blank_columns'] + [cell['column'] for cell in fixture['digit_cells']],
                                     list(range(1, 16)))

                    expected = fixture['expected'][track]
                    self.assertTrue(expected.strip())
                    block_name = 'm81243--' + anchor
                    self.assertEqual([name for name, body in blocks.items() if expected in body], [block_name],
                                     'Each exact chart fixture belongs only to its source SSML block')
                    self.assertEqual(blocks[block_name].count(expected), 1)
                    self.assertRegex(expected, re.compile(r'\b' + re.escape(build.number('15', javanese)) + r' kolom\b', re.I))
                    count = ({8: r'(?:wolu|wolung)', 7: r'(?:pitu|pitung)'}[blanks]
                             if javanese else re.escape(build.number(str(blanks), False)))
                    blank_clause = (r' kolom kapisan ing larik digit (?:isih )?kosong\b'
                                    if javanese else r' kolom pertama pada baris digit kosong\b')
                    self.assertRegex(expected, re.compile(r'\b' + count + blank_clause, re.I))

                    # Isolate the digit row: a whole-block subsequence could be
                    # satisfied by question numbers or by "not zero" explanations.
                    ordinal = ({8: 'sanga', 7: 'wolu'}[blanks] if javanese
                               else {8: 'kesembilan', 7: 'kedelapan'}[blanks])
                    start = (r'Wiwit kolom kaping ' + ordinal + r'(?::|, ana) '
                             if javanese else r'Mulai kolom ' + ordinal + r': ')
                    digit_row = re.search(start + r'([^\.]+)\.', expected, re.I)
                    self.assertIsNotNone(digit_row, 'Missing source-positioned digit-row narration')
                    cells = digit_row.group(1).split('; ')
                    self.assertEqual(len(cells), len(digits))
                    for cell, digit in zip(cells, digits):
                        self.assertRegex(cell, re.compile(
                            r'^(?:(?:lan|dan) )?' + re.escape(build.number(digit, javanese))
                            + (r' ing ' if javanese else r' pada ') + r'\S', re.I))
                    if blanks == 8:
                        self.assertRegex(expected, re.compile(
                            r'kosong, (?:dudu (?:digit )?nol|bukan digit nol)\.', re.I))
                    else:
                        self.assertEqual(fixture['digit_cells'][3], {'column': 11, 'digit': '0'})
                        self.assertRegex(cells[3], re.compile(
                            r'^nol (?:ing puluhan éwu|pada puluh ribuan)$', re.I))
                        self.assertRegex(expected, re.compile(
                            r'\bNol (?:ing (?:kolom )?puluhan éwu (?:iku digit sing katulis|kuwi digit sing ditulis), dudu'
                            r'|pada kolom puluh ribuan adalah digit tertulis, bukan) sel kosong\.', re.I))

    def test_production_punctuation_continuation_and_answers_are_contextual(self):
        generated = self.products()
        for track in TRACKS:
            blocks = ssml_blocks(generated[f'review/audio/{UNIT}.{track}.ssml'])
            opening = blocks['m81243--fs-id1795155']
            self.assertIn('lan sateruse' if track.startswith('jv') else 'dan seterusnya', opening)
            self.assertNotIn('titik koma', blocks['m81243--fs-id1891091'])
            for anchor in ('fs-id2310429', 'fs-id1282619'):
                self.assertIn('Wangsulan.' if track.startswith('jv') else 'Jawaban.', blocks['m81243--' + anchor])

    def test_production_products_are_complete_current_and_deterministic(self):
        first = self.products()
        self.assertEqual(first, self.products())
        self.assertEqual(len(first), 8)
        for path, raw in first.items():
            self.assertEqual((LANG / path).read_bytes(), raw, path)
        page = first[f'review/units/{UNIT}.html'].decode('utf-8')
        inspection = Reader()
        inspection.feed(page)
        self.assertEqual(inspection.maths, 120)
        self.assertEqual(len(inspection.images), 6)
        self.assertEqual(len(inspection.ids), len(set(inspection.ids)))
        for track in TRACKS:
            self.assertTrue(all(UNIT + '--' + track + '--' + source_id in inspection.ids for source_id in EXPECTED_IDS))
            speech = ET.fromstring(first[f'review/audio/{UNIT}.{track}.ssml'])
            self.assertEqual(speech.get(XML_LANG), TRACKS[track][0])
        receipt = json.loads(first[f'qa/{UNIT}.build-receipt.json'])
        self.assertEqual(receipt['source_ids'], 31)
        self.assertEqual(receipt['source_math_expressions'], 40)
        self.assertEqual(receipt['source_media_references'], 2)
        self.assertFalse(receipt['human_language_review'])
        self.assertFalse(receipt['listening_review'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
