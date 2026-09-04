"""Read-only regressions for the complete A00 whole-number naming subsection.

Pinned source and finite-fixture checks do not require generated products.
Narration checks require a working baseline before testing mutations. Only asset
and saved-output checks wait for the asset manifest; once present, missing/stale
products are failures. The word/value probe is a bounded test oracle, never a
production parser, pronunciation judgment, or native-language certification.
"""
import copy
from functools import lru_cache
import hashlib
import json
import re
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import build
import build_units
import draft_units
from build import CN, MATH, XML_LANG
from config import LANG, TRACKS
from qa import Reader


UNIT = 'a00-name-whole'
SECTION = 'fs-id1321580'
DESCRIPTOR = {'section': SECTION, 'slice': None}
EXPECTED_IDS = '''fs-id1321580 fs-id2566318 eip-id1168289680652 fs-id1227744
fs-id2220075 fs-id3400199 fs-id1364640 eip-375 fs-id2326974 fs-id1545709
fs-id882630 fs-id1880734 fs-id2196744 fs-id1171100715908 eip-id1168287499693
fs-id1209906 fs-id1851678 fs-id2774887 fs-id2601285 fs-id2353164 fs-id2269538
fs-id1312880 fs-id1469854 fs-id2136533 fs-id1773572 fs-id2926171 fs-id2555667
fs-id1683677 fs-id1278691 fs-id1825910 fs-id1314136 fs-id4315464 fs-id2627959
fs-id2425040 fs-id1526255 fs-id2670483 fs-id2263806 fs-id1738516 fs-id1409152
fs-id1344528 fs-id1394436 fs-id1628781 fs-id2472209 fs-id2223828 fs-id1919954
fs-id1393924 fs-id2243722 fs-id1808812 fs-id2060477 fs-id2172100 fs-id1250766
fs-id1360632 fs-id1269733'''.split()
DIRECT_IDS = '''fs-id2566318 eip-id1168289680652 fs-id2220075 fs-id3400199
fs-id1364640 fs-id2326974 fs-id2774887 fs-id2136533 fs-id1825910
fs-id1628781 fs-id1808812'''.split()
MATH_KEYS = (
    ('fs-id2220075', 1), ('fs-id2326974', 1), ('fs-id2326974', 2),
    ('fs-id2774887', 1), ('fs-id2136533', 1), ('fs-id1825910', 1),
    ('fs-id1825910', 2), ('fs-id1628781', 1), ('fs-id1808812', 1),
)
TOKENS = ('37,519,248', '8,165,432,098,710', '8,165,432,098,710',
          '9,258,137,904,061', '17,864,325,619,004', '2014',
          '327,577,529', '316,128,839', '31,536,000')
VALUES = {
    '37,519,248': 37_519_248,
    '8,165,432,098,710': 8_165_432_098_710,
    '9,258,137,904,061': 9_258_137_904_061,
    '17,864,325,619,004': 17_864_325_619_004,
    '2014': 2014,
    '327,577,529': 327_577_529,
    '316,128,839': 316_128_839,
    '31,536,000': 31_536_000,
}
REFS = (
    ('fs-id1227744', '../../media/CNX_BMath_Figure_01_01_013_img.jpg.id-ID.svg'),
    ('fs-id1209906', '../../media/CNX_BMath_Figure_01_01_014_img.jpg.id-ID.svg'),
    ('fs-id2670483', '../../media/CNX_BMath_Figure_01_01_015_img.jpg.id-ID.svg'),
)
CHARTS = (
    ('eip-id1168289680652', '37,519,248', 3),
    ('fs-id2326974', '8,165,432,098,710', 5),
    ('fs-id1825910', '327,577,529', 0),
)
IMAGE_HASHES = (
    'dc7daac5f2b4dfd2ac4caa2e0a4932a5c69b56243653a861c6899f95f3ba8410',
    'f7fffee2f8cdbb4eec2e547860a9df7f028e25c193ee44cf05db21b5c73ab64e',
    '5dc38a4522845a6b875b72a1076ffa36870cd8e313124f08a0d157bde09671df',
)
ANSWERS = (
    ('fs-id2774887', 'fs-id1312880', 'fs-id1469854', '9,258,137,904,061'),
    ('fs-id2136533', 'fs-id1683677', 'fs-id1278691', '17,864,325,619,004'),
    ('fs-id1628781', 'fs-id1393924', 'fs-id2243722', '316,128,839'),
    ('fs-id1808812', 'fs-id1360632', 'fs-id1269733', '31,536,000'),
)
JV_DIGITS = 'nol siji loro telu papat lima enem pitu wolu sanga'.split()
ID_DIGITS = 'nol satu dua tiga empat lima enam tujuh delapan sembilan'.split()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load_json(relative):
    return json.loads((LANG / relative).read_text(encoding='utf-8'))


@lru_cache(maxsize=None)
def pinned(repo_name, path='modules/m81243/index.cnxml'):
    repositories = load_json('sources.lock.json')['repositories']
    repo = next(row for row in repositories if row['name'] == repo_name)
    return draft_units.pinned_blob(repo, path)


def source_root():
    return draft_units.select(pinned('a00-id'), DESCRIPTOR)


def variants():
    source = source_root()
    edits = load_json(f'translation/{UNIT}.edits.json')
    shared = load_json('translation/phrases.json')
    rows = {row[0]: row for row in shared['phrases']}
    for row in edits['phrases']:
        if row[0] in rows and rows[row[0]] != row:
            raise AssertionError('Shared phrase conflict: ' + row[0])
        rows[row[0]] = row
    merged = {**edits, 'phrases': list(rows.values()),
              'unchanged_identifiers': shared['unchanged_identifiers'] + edits['unchanged_identifiers']}
    return {'id-academic': source, **{
        track: build.translated(source, track, merged) for track in edits['tracks']}}


def find_id(root, anchor):
    return next(node for node in root.iter() if node.get('id') == anchor)


def cnxml_fixture(text):
    return ET.fromstring(f'<wrapper xmlns="{CN}">{text}</wrapper>')[0]


def integer_fixture(token):
    """Only the eight source integers; 2014 is the sole ungrouped year."""
    if not isinstance(token, str) or token not in VALUES:
        raise ValueError('unregistered_integer_fixture')
    if token != '2014' and not re.fullmatch(r'[1-9][0-9]{0,2}(?:,[0-9]{3})+', token):
        raise ValueError('invalid_grouping')
    return int(token.replace(',', ''))


def reading_value(text, track):
    """Arithmetic oracle over the finite numeral vocabulary used here.

    This checks value and descending scales, not naturalness or pronunciation.
    It never reads files or changes the production narration implementation.
    """
    jv = dict(zip(JV_DIGITS, range(10))) | {
        'rong': 2, 'telung': 3, 'patang': 4, 'limang': 5, 'nem': 6,
        'pitung': 7, 'wolung': 8, 'sangang': 9, 'sepuluh': 10,
        'patbelas': 14, 'nembelas': 16, 'pitulas': 17, 'sangalas': 19,
        'salawé': 25, 'pitulikur': 27, 'wolulikur': 28, 'sangalikur': 29,
        'sèket': 50, 'sewidak': 60, 'satus': 100,
    }
    indonesian = dict(zip(ID_DIGITS, range(10))) | {'sepuluh': 10, 'seratus': 100}
    scales = ({'trilyun': 10**12, 'milyar': 10**9, 'yuta': 10**6, 'éwu': 1000}
              if track.startswith('jv') else
              {'triliun': 10**12, 'miliar': 10**9, 'juta': 10**6, 'ribu': 1000})
    lexicon = jv if track.startswith('jv') else indonesian
    pieces, total, previous_scale = [], 0, 10**15
    tokens = re.sub(r'[,.]', '', text).split()
    if not tokens:
        raise ValueError('empty_number_name')
    for token in tokens:
        if token in scales:
            scale = scales[token]
            if not pieces or scale >= previous_scale:
                raise ValueError('invalid_period_order')
            total += sum(pieces) * scale
            previous_scale, pieces = scale, []
        elif token in ('atus', 'ratus', 'puluh'):
            if not pieces:
                raise ValueError('missing_cardinal_stem')
            pieces[-1] *= {'atus': 100, 'ratus': 100, 'puluh': 10}[token]
        elif token == 'belas' and not track.startswith('jv'):
            if not pieces:
                raise ValueError('missing_teen_stem')
            pieces[-1] += 10
        elif token in lexicon:
            pieces.append(lexicon[token])
        else:
            raise ValueError('unregistered_number_word: ' + token)
    return total + sum(pieces)


def svg_geometry(raw):
    root = ET.fromstring(raw)
    root.attrib.pop(XML_LANG, None)
    for node in root.iter():
        if node.text and re.search(r'[^\W\d_]', node.text, re.UNICODE):
            node.text = '__linguistic_text__'
    return build_units.tree_key(root)


def svg_numeric_text(raw):
    return [(node.tag, node.get('x'), node.get('y'), re.findall(r'[0-9]+(?:,[0-9]+)*', node.text or ''))
            for node in ET.fromstring(raw).iter()
            if re.search(r'[0-9]', node.text or '')]


def ssml_blocks(raw):
    result, current = {}, None
    for child in ET.fromstring(raw):
        if child.tag.endswith('}mark'):
            current = child.get('name')
            if current in result:
                raise AssertionError('Duplicate SSML source mark')
        elif child.tag.endswith('}p') and current is not None:
            result[current] = ''.join(child.itertext())
    return result


class SourceAndFiniteFixtureTests(unittest.TestCase):
    def setUp(self):
        self.rules = load_json(f'audio/{UNIT}.rules.json')
        self.variants = variants()
        self.source = self.variants['id-academic']

    def test_pinned_module_hashes_and_complete_section_boundary(self):
        self.assertEqual(sha(pinned('a00-id')), '7153ce88bcd4aea07fab4075bdb025884e07d534aafb6d06ff1bfbedbc46f251')
        self.assertEqual(sha(pinned('openstax-prealgebra-bundle')), '396b0029798e054e5db6d7acde738cec9f9d8b86bc81da8cc3690d01ec07cf2b')
        self.assertEqual(len(self.source), 12)
        self.assertEqual([node.get('id') for node in self.source[1:]], DIRECT_IDS)
        self.assertEqual(self.rules['scope']['next_section'], 'fs-id1339359')
        self.assertEqual(self.rules['scope']['last_descendant_id'], 'fs-id1269733')
        self.assertNotIn('fs-id1339359', EXPECTED_IDS)

    def test_47_exact_phrase_keys_and_both_registers_preserve_53_ids(self):
        edits = load_json(f'translation/{UNIT}.edits.json')
        phrases = {value.strip() for node in self.source.iter()
                   for value in (node.text, node.tail, node.get('alt'), node.get('aria-label'))
                   if value and re.search('[A-Za-z]', value)}
        self.assertEqual(len(phrases), 47)
        self.assertEqual(len(edits['phrases']), 47)
        self.assertEqual({row[0] for row in edits['phrases']}, phrases)
        self.assertTrue(any(row[1] != row[2] for row in edits['phrases']))
        for track, target in self.variants.items():
            with self.subTest(track=track):
                self.assertEqual([node.get('id') for node in target.iter() if node.get('id')], EXPECTED_IDS)
                self.assertEqual(len(set(EXPECTED_IDS)), 53)
                if track.startswith('jv'):
                    draft_units.validate(self.source, target)

    def test_all_nine_source_tokens_styles_periods_and_year_are_exact(self):
        for track, root in self.variants.items():
            with self.subTest(track=track):
                self.assertEqual(tuple(node.text for node in root.iter('{' + MATH + '}mn')), TOKENS)
                self.assertEqual(len(list(root.iter('{' + MATH + '}math'))), 9)
                self.assertEqual([node.text for node in root.iter('{' + MATH + '}mo')], ['.', '.'])
                self.assertEqual([node.attrib for node in root.iter('{' + MATH + '}mstyle')], [{'fontweight': 'bold'}])
                self.assertEqual(len(list(root.iter('{' + CN + '}newline'))), 1)
                self.assertNotIn('…', ''.join(root.itertext()))
        year = self.rules['year_witness']
        self.assertEqual((year['source'], year['anchor'], year['math_ordinal']), ('2014', 'fs-id1825910', 1))

    def test_finite_integer_fixture_preserves_values_and_rejects_unregistered_forms(self):
        for token, value in VALUES.items():
            self.assertEqual(integer_fixture(token), value)
            self.assertEqual(integer_fixture(token), integer_fixture(token))
        invalid = ('', None, '2,014', '02014', '2014.0', '37519248',
                   '8,165,432,98,710', '9,258,137,904,61', '17,864,325,619,4',
                   '31,536', '31,536,000,', '31,,536,000', '０３１,５３６,０００',
                   '31，536，000', '-31,536,000', '+2014', '1e3', '1,000',
                   '100,000,000,000,000')
        for token in invalid:
            with self.subTest(token=token), self.assertRaises(ValueError):
                integer_fixture(token)

    def test_all_27_contextual_readouts_and_cardinal_witnesses_preserve_the_number(self):
        fixtures = self.rules['math_fixtures']
        self.assertEqual(len(fixtures), 9)
        for fixture, token in zip(fixtures, TOKENS):
            self.assertEqual(fixture['source_value'], token)
            self.assertEqual(set(fixture['expected']), set(TRACKS))
            cardinals = fixture['expected'] if token == '2014' else fixture['expected_cardinal']
            self.assertEqual(set(cardinals), set(TRACKS))
            for track, spoken in fixture['expected'].items():
                with self.subTest(fixture=fixture['id'], track=track):
                    cardinal = cardinals[track]
                    self.assertEqual(reading_value(cardinal, track), VALUES[token])
                    self.assertNotRegex(cardinal, r'[0-9]|\b(?:koma|nol|satuan)\b')
                    self.assertEqual(spoken.endswith('.'), token in ('327,577,529', '316,128,839'))
                    if token == '2014':
                        self.assertEqual(spoken, self.rules['year_witness']['expected'][track])
                    else:
                        # Naming exercises must expose the printed digits, not
                        # supply the word-form answer in the question itself.
                        digits = JV_DIGITS if track.startswith('jv') else ID_DIGITS
                        separator = '; tandha koma; ' if track.startswith('jv') else '; tanda koma; '
                        prefix = 'digit saka kiwa menyang tengen: ' if track.startswith('jv') else 'digit dari kiri ke kanan: '
                        groups = [', '.join(digits[int(digit)] for digit in group) for group in token.split(',')]
                        punctuation = '.' if token in ('327,577,529', '316,128,839') else ''
                        self.assertEqual(spoken, prefix + separator.join(groups) + punctuation)
                        self.assertEqual(spoken.count(separator), token.count(','))
                        self.assertNotIn(cardinal, spoken)
        for text in ('', '31,536,000', 'siji koma loro', 'puluh', 'siji éwu siji yuta'):
            with self.assertRaises(ValueError):
                reading_value(text, 'jv-academic')

    def test_seven_decompositions_keep_leading_and_all_zero_groups(self):
        witnesses = self.rules['number_decomposition_witnesses']
        self.assertEqual([row['source'] for row in witnesses], [token for token in VALUES if token != '2014'])
        self.assertEqual(len(witnesses), 7)
        for row in witnesses:
            groups = row['source'].split(',')
            scales = [str(1000**power) for power in reversed(range(len(groups)))]
            self.assertEqual(row['groups_from_left'], groups)
            self.assertEqual(row['group_scales'], scales)
            self.assertEqual(sum(int(g) * int(s) for g, s in zip(groups, scales)), integer_fixture(row['source']))
            self.assertEqual(int(row['fixed_value']), integer_fixture(row['source']))
        zeros = [row['group'] for witness in witnesses for row in witness['leading_zero_groups']]
        self.assertEqual(zeros, ['098', '061', '004', '000'])

    def test_source_bound_matcher_covers_every_anchor_ordinal_and_exact_tree(self):
        self.assertEqual(tuple((row['anchor'], row['math_ordinal']) for row in self.rules['math_fixtures']), MATH_KEYS)
        for row in self.rules['math_fixtures']:
            self.assertIn(row['source_mathml'], pinned('a00-id').decode())
        for track, root in self.variants.items():
            bound = build_units.source_bound_math(root, self.rules, track, self.source)
            self.assertEqual(len(bound), 9)
            for block in root:
                for ordinal, expression in enumerate(block.iter('{' + MATH + '}math'), 1):
                    fixture = next(row for row in self.rules['math_fixtures']
                                   if (row['anchor'], row['math_ordinal']) == (block.get('id'), ordinal))
                    self.assertEqual(build_units.narrate(expression, track, UNIT, bound, self.rules), fixture['expected'][track])

    def test_math_mutations_reject_grouping_zeroes_style_operator_and_anchor(self):
        for mutation in ('grouping', 'leading-zero', 'all-zero-period', 'year', 'style', 'operator', 'anchor'):
            changed = copy.deepcopy(self.source)
            if mutation == 'grouping':
                next(node for node in changed.iter('{' + MATH + '}mn') if node.text == TOKENS[0]).text = '37519,248'
            elif mutation == 'leading-zero':
                next(node for node in changed.iter('{' + MATH + '}mn') if node.text == TOKENS[1]).text = '8,165,432,98,710'
            elif mutation == 'all-zero-period':
                next(node for node in changed.iter('{' + MATH + '}mn') if node.text == TOKENS[-1]).text = '31,536'
            elif mutation == 'year':
                next(node for node in changed.iter('{' + MATH + '}mn') if node.text == '2014').text = '2,014'
            elif mutation == 'style':
                next(changed.iter('{' + MATH + '}mstyle')).set('fontweight', 'normal')
            elif mutation == 'operator':
                next(changed.iter('{' + MATH + '}mo')).text = ';'
            else:
                find_id(changed, 'fs-id2326974').set('id', 'wrong-example')
            with self.subTest(mutation=mutation), self.assertRaises((ValueError, AssertionError)):
                build_units.source_bound_math(changed, self.rules, 'id-academic')

    def test_changed_fixture_ordinal_duplicate_and_unknown_tree_fail(self):
        for mutation in ('ordinal', 'duplicate', 'tree'):
            rules = copy.deepcopy(self.rules)
            if mutation == 'ordinal':
                rules['math_fixtures'][0]['math_ordinal'] = 2
            elif mutation == 'duplicate':
                rules['math_fixtures'].append(copy.deepcopy(rules['math_fixtures'][0]))
            else:
                rules['math_fixtures'][0]['source_mathml'] = rules['math_fixtures'][0]['source_mathml'].replace('m:mn', 'm:mi')
            with self.subTest(mutation=mutation), self.assertRaises((ValueError, AssertionError)):
                build_units.source_bound_math(self.source, rules, 'id-academic')

    def test_three_charts_bind_exact_media_groups_and_arrow_cardinals(self):
        fixtures = self.rules['chart_fixtures']
        self.assertEqual(tuple((row['media_id'], row['source_image']) for row in fixtures), REFS)
        self.assertEqual(len(fixtures), 3)
        for row, (anchor, token, arrows) in zip(fixtures, CHARTS):
            self.assertEqual((row['anchor'], row['whole_number']), (anchor, token))
            self.assertEqual(row['groups_from_left'], token.split(','))
            self.assertEqual(row['source_alt'], find_id(self.source, row['media_id']).get('alt'))
            self.assertEqual(len(row['arrow_mappings']), arrows)
            for track in TRACKS:
                digits = JV_DIGITS if track.startswith('jv') else ID_DIGITS
                expected = [', '.join(digits[int(digit)] for digit in group) for group in token.split(',')]
                self.assertEqual(row['printed_digit_readings'][track], expected)
                position = 0
                for phrase in expected:
                    position = row['expected'][track].index(phrase, position) + len(phrase)
                for arrow in row['arrow_mappings']:
                    index = arrow['group_index_from_left'] - 1
                    self.assertEqual(arrow['source_group'], token.split(',')[index])
                    self.assertIn(arrow['expected_word_label'][track], row['expected'][track])
                    self.assertEqual(reading_value(arrow['expected_word_label'][track], track),
                                     int(arrow['source_group']) * int(row['group_scales'][index]))

    def test_chart_zero_is_explicit_and_third_chart_has_no_invented_arrows(self):
        chart = self.rules['chart_fixtures'][1]
        self.assertEqual(chart['groups_from_left'][3], '098')
        for track in TRACKS:
            text = chart['expected'][track]
            self.assertIn('nol, sanga, wolu' if track.startswith('jv') else 'nol, sembilan, delapan', text)
            self.assertRegex(text, r'(?:dudu (?:panggonan|papan)|bukan tempat) kosong')
            self.assertIn('sangang puluh wolu éwu' if track.startswith('jv') else 'sembilan puluh delapan ribu', text)
            self.assertNotIn('panah', self.rules['chart_fixtures'][2]['expected'][track].lower())

    def test_table_retains_three_declared_columns_but_five_two_entry_rows(self):
        self.assertEqual(len(self.rules['table_fixtures']), 1)
        row = self.rules['table_fixtures'][0]
        table = find_id(self.source, 'fs-id1171100715908')
        self.assertEqual(build_units.tree_key(table), build_units.tree_key(cnxml_fixture(row['source_cnxml'])))
        self.assertIn(row['source_cnxml'], pinned('a00-id').decode())
        self.assertEqual(table.get('aria-label'), row['source_aria_label'])
        self.assertEqual(table.find('{*}tgroup').get('cols'), '3')
        self.assertEqual(table.findall('.//{*}thead'), [])
        self.assertEqual([len(node) for node in table.findall('.//{*}row')], [2] * 5)
        self.assertEqual([[cell.text for cell in node] for node in table.findall('.//{*}row')], row['source_rows'])
        self.assertEqual(list(map(int, row['row_values'])), [8 * 10**12, 165 * 10**9, 432 * 10**6, 98_000, 710])
        self.assertEqual(sum(map(int, row['row_values'])), VALUES['8,165,432,098,710'])
        for track, text in row['expected'].items():
            self.assertEqual(len(text.splitlines()), 5)
            for line, value in zip(text.splitlines(), row['row_values']):
                self.assertEqual(reading_value(line.rsplit(': ', 1)[1], track), int(value))

    def test_quoted_lan_preserves_source_emphasis_and_scoped_instruction(self):
        self.assertEqual(len(self.rules['prose_fixtures']), 1)
        row = self.rules['prose_fixtures'][0]
        self.assertEqual(row['anchor'], 'fs-id3400199')
        self.assertEqual(build_units.tree_key(find_id(self.source, row['anchor'])),
                         build_units.tree_key(cnxml_fixture(row['source_cnxml'])))
        for track, root in self.variants.items():
            word = 'lan' if track.startswith('jv') else 'dan'
            emphasis = find_id(root, row['anchor']).find('{*}emphasis')
            self.assertEqual((emphasis.text, emphasis.get('effect')), (word, 'italics'))
            self.assertEqual(row['expected'][track].count('“' + word + '”'), 1)
            self.assertEqual(len(re.findall(r'\b' + word + r'\b', row['expected'][track])), 1)

    def test_four_answers_and_title_cue_metadata_match_actual_solutions(self):
        rows = self.rules['answer_value_invariants']
        self.assertEqual(len(rows), 4)
        for row, (anchor, solution, paragraph, token) in zip(rows, ANSWERS):
            self.assertEqual((row['anchor'], row['solution_id'], row['answer_paragraph'], row['number']),
                             (anchor, solution, paragraph, token))
            self.assertIsNone(find_id(self.source, solution).find('{*}title'))
            self.assertEqual(find_id(self.source, paragraph).text, row['source_answer'])
            for track, root in self.variants.items():
                text = ''.join(find_id(root, paragraph).itertext())
                self.assertEqual(text, row['expected_visible_answer'][track])
                self.assertEqual(reading_value(text, track), VALUES[token])
        titled = self.rules['solution_cues'][0]
        self.assertEqual(titled['solution_ids'], ['fs-id2196744', 'fs-id2425040'])
        for solution in titled['solution_ids']:
            self.assertEqual(find_id(self.source, solution).findtext('{*}title'), 'Penyelesaian')
        self.assertEqual(self.rules['solution_cues'][1]['solution_ids'], [row[1] for row in ANSWERS])

    def test_canon_spellings_and_no_generic_parser_or_human_claim(self):
        readings = {row['source_value']: (row['expected'] if row['source_value'] == '2014'
                                         else row['expected_cardinal'])['jv-academic']
                    for row in self.rules['math_fixtures']}
        self.assertIn('sèket', readings['9,258,137,904,061'])
        self.assertIn('salawé', readings['17,864,325,619,004'])
        for text in readings.values():
            self.assertNotRegex(text, r'\b(?:ewu|ewonan|seket|selawe)\b')
        self.assertFalse(self.rules['matching_contract']['generic_number_parser_authorized'])
        self.assertFalse(self.rules['matching_contract']['strip_commas_then_parse_at_runtime'])
        for field in ('human_language_review', 'visual_review', 'listening_review', 'provider_compatibility_tested'):
            self.assertFalse(self.rules['qa_receipt'][field])
        self.assertEqual(self.rules['qa_receipt']['synthesized_audio_files'], 0)


class NarrationIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.assertIn(UNIT, draft_units.UNITS, 'The registered descriptor must not disappear')
        self.rules = load_json(f'audio/{UNIT}.rules.json')
        self.variants = variants()
        self.source = self.variants['id-academic']

    def blocks(self, track, target=None, source=None, rules=None):
        return dict(build_units.blocks(target if target is not None else self.variants[track],
                                       track, UNIT, rules if rules is not None else self.rules,
                                       source if source is not None else self.source))

    def test_complete_baseline_routes_each_fixed_readout_to_its_source_block(self):
        for track in TRACKS:
            blocks = self.blocks(track)
            self.assertEqual(list(blocks), ['title'] + DIRECT_IDS)
            for fixture in self.rules['chart_fixtures'] + self.rules['table_fixtures'] + self.rules['prose_fixtures']:
                expected = fixture['expected'][track]
                self.assertEqual([anchor for anchor, body in blocks.items() if expected in body], [fixture['anchor']])
                self.assertEqual(blocks[fixture['anchor']].count(expected), 1)
            self.assertEqual(blocks['fs-id3400199'], self.rules['prose_fixtures'][0]['expected'][track])

    def test_baseline_has_four_untitled_answer_cues_without_worked_duplicates(self):
        for track in TRACKS:
            blocks = self.blocks(track)
            cue = 'Wangsulan.' if track.startswith('jv') else 'Jawaban.'
            self.assertEqual(sum(body.count(cue) for body in blocks.values()), 4)
            for anchor, _, _, _ in ANSWERS:
                self.assertEqual(blocks[anchor].count(cue), 1)
            for anchor in ('fs-id2326974', 'fs-id1825910'):
                self.assertNotIn(cue, blocks[anchor])

    def test_practice_prompts_do_not_speak_the_word_form_answer_before_the_cue(self):
        for track in TRACKS:
            blocks = self.blocks(track)
            cue = 'Wangsulan.' if track.startswith('jv') else 'Jawaban.'
            for anchor, _, _, token in ANSWERS:
                fixture = next(row for row in self.rules['math_fixtures'] if row['anchor'] == anchor)
                prompt, answer = blocks[anchor].split(cue)
                with self.subTest(track=track, number=token):
                    self.assertIn(fixture['expected'][track], prompt)
                    self.assertNotIn(fixture['expected_cardinal'][track], prompt)
                    self.assertNotIn('digit saka kiwa menyang tengen:', answer)
                    self.assertNotIn('digit dari kiri ke kanan:', answer)
                    invariant = next(row for row in self.rules['answer_value_invariants'] if row['anchor'] == anchor)
                    self.assertIn(invariant['expected_visible_answer'][track], answer)

    def test_source_table_chart_and_quoted_prose_mutations_fail_after_valid_baseline(self):
        self.blocks('id-academic')  # A missing handler is not a successful negative test.
        for mutation in ('table-cols', 'table-cell', 'table-aria', 'chart-alt', 'chart-path', 'quoted-word'):
            changed = copy.deepcopy(self.source)
            if mutation == 'table-cols':
                find_id(changed, 'fs-id1171100715908').find('{*}tgroup').set('cols', '2')
            elif mutation == 'table-cell':
                row = find_id(changed, 'fs-id1171100715908').find('.//{*}row')
                row.remove(row[-1])
            elif mutation == 'table-aria':
                find_id(changed, 'fs-id1171100715908').set('aria-label', 'Altered source description')
            elif mutation == 'chart-alt':
                find_id(changed, 'fs-id1209906').set('alt', 'Changed chart')
            elif mutation == 'chart-path':
                find_id(changed, 'fs-id1209906').find('{*}image').set('src', REFS[0][1])
            else:
                find_id(changed, 'fs-id3400199').find('{*}emphasis').text = 'atau'
            with self.subTest(mutation=mutation), self.assertRaises((ValueError, AssertionError)):
                self.blocks('id-academic', changed, changed)

    def test_target_table_chart_and_quoted_word_mutations_fail_after_valid_baseline(self):
        for track in ('jv-academic', 'jv-conversation'):
            self.blocks(track)
            for mutation in ('table-word', 'chart-alt', 'quoted-word'):
                changed = copy.deepcopy(self.variants[track])
                if mutation == 'table-word':
                    find_id(changed, 'fs-id1171100715908').find('.//{*}row')[1].text = 'sangang trilyun'
                elif mutation == 'chart-alt':
                    find_id(changed, 'fs-id1209906').set('alt', 'Unexpected translated diagram')
                else:
                    find_id(changed, 'fs-id3400199').find('{*}emphasis').text = 'utawa'
                with self.subTest(track=track, mutation=mutation), self.assertRaises((ValueError, AssertionError)):
                    self.blocks(track, target=changed)

    def test_nonmath_fixture_mutations_do_not_bypass_source_registration(self):
        self.blocks('id-academic')
        for mutation in ('table-source', 'chart-source', 'prose-source'):
            rules = copy.deepcopy(self.rules)
            if mutation == 'table-source':
                rules['table_fixtures'][0]['source_cnxml'] = rules['table_fixtures'][0]['source_cnxml'].replace('cols="3"', 'cols="2"')
            elif mutation == 'chart-source':
                rules['chart_fixtures'][0]['source_alt'] = 'Unregistered chart alt'
            else:
                rules['prose_fixtures'][0]['source_cnxml'] = rules['prose_fixtures'][0]['source_cnxml'].replace('>dan<', '>atau<')
            with self.subTest(mutation=mutation), self.assertRaises((ValueError, AssertionError)):
                self.blocks('id-academic', rules=rules)


class SavedProductTests(unittest.TestCase):
    def setUp(self):
        if not (LANG / f'translation/{UNIT}.assets.json').is_file():
            self.skipTest('Asset manifest pending: only asset/saved-output checks wait; source and narration tests stay active')

    def products(self):
        with (patch.object(build_units, 'write_bytes', side_effect=AssertionError('Forbidden build write')),
              patch.object(draft_units, 'write_bytes', side_effect=AssertionError('Forbidden draft write'))):
            return build_units.products(UNIT)

    def test_three_source_asset_hashes_and_all_nine_locales_geometries_and_digits(self):
        manifest = load_json(f'translation/{UNIT}.assets.json')
        self.assertEqual(tuple((row['media_id'], row['source_src']) for row in manifest['assets']), REFS)
        self.assertEqual(len(manifest['assets']), 3)
        for row, (_, source_ref), expected_hash in zip(manifest['assets'], REFS, IMAGE_HASHES):
            source = pinned('a00-id', source_ref.removeprefix('../../'))
            self.assertEqual(sha(source), expected_hash)
            self.assertEqual(set(row['outputs']), set(TRACKS))
            for track, output in row['outputs'].items():
                with self.subTest(media=row['media_id'], track=track):
                    raw = (LANG / output['path']).read_bytes()
                    self.assertEqual(sha(raw), output['sha256'])
                    self.assertEqual(svg_geometry(raw), svg_geometry(source))
                    self.assertEqual(svg_numeric_text(raw), svg_numeric_text(source))
                    self.assertEqual(ET.fromstring(raw).get(XML_LANG), TRACKS[track][0])
                    if track == 'id-academic':
                        self.assertEqual(raw, source)

    def test_registered_draft_products_are_current_deterministic_and_read_only(self):
        with patch.object(draft_units, 'write_bytes', side_effect=AssertionError('Forbidden draft write')) as writer:
            first = draft_units.products(UNIT)
            self.assertEqual(first, draft_units.products(UNIT))
            for path, raw in first.items():
                self.assertEqual((LANG / path).read_bytes(), raw, path)
            writer.assert_not_called()

    def test_saved_build_products_are_current_deterministic_and_honest(self):
        first = self.products()
        self.assertEqual(first, self.products())
        self.assertEqual(len(first), 8)
        for path, raw in first.items():
            self.assertEqual((LANG / path).read_bytes(), raw, path)
        receipt = json.loads(first[f'qa/{UNIT}.build-receipt.json'])
        self.assertEqual((receipt['source_ids'], receipt['source_math_expressions'], receipt['source_media_references']), (53, 9, 3))
        self.assertEqual(receipt['source_bound_math_fixtures'], 9)
        for field in ('human_language_review', 'visual_review', 'listening_review', 'whole_module_complete'):
            self.assertFalse(receipt[field])
        self.assertEqual(receipt['synthesized_audio_files'], 0)

    def test_reader_and_ssml_keep_all_ids_nine_images_and_four_answer_cues(self):
        products = self.products()
        reader = Reader()
        reader.feed(products[f'review/units/{UNIT}.html'].decode('utf-8'))
        self.assertEqual(reader.maths, 27)
        self.assertEqual(len(reader.images), 9)
        self.assertEqual(len(reader.heads), 0, 'The source table has no column-header row')
        self.assertEqual(len(reader.ids), len(set(reader.ids)))
        rules = load_json(f'audio/{UNIT}.rules.json')
        for track in TRACKS:
            self.assertTrue(all(UNIT + '--' + track + '--' + anchor in reader.ids for anchor in EXPECTED_IDS))
            raw = products[f'review/audio/{UNIT}.{track}.ssml']
            self.assertEqual(ET.fromstring(raw).get(XML_LANG), TRACKS[track][0])
            blocks = ssml_blocks(raw)
            self.assertEqual(list(blocks), ['m81243--' + anchor for anchor in ['title'] + DIRECT_IDS])
            cue = 'Wangsulan.' if track.startswith('jv') else 'Jawaban.'
            self.assertEqual(sum(body.count(cue) for body in blocks.values()), 4)
            for fixture in rules['chart_fixtures'] + rules['table_fixtures'] + rules['prose_fixtures']:
                expected = fixture['expected'][track]
                self.assertEqual([anchor for anchor, body in blocks.items() if expected in body], ['m81243--' + fixture['anchor']])


if __name__ == '__main__':
    unittest.main(verbosity=2)
