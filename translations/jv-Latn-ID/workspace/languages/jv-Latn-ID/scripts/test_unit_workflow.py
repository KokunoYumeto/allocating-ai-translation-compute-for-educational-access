"""Read-only adversarial regression tests for the next A00/A10 unit pipeline.

All mutations are in-memory XML/JSON copies. Product functions are exercised
with their write helpers disabled; no build CLI or acquisition is invoked.
These tests check source fidelity and explicit readings, not language quality,
voice availability, listening, or rendered visual accessibility.
"""
import copy
import hashlib
import json
import re
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import build_units
import draft_units
from build import CN, MATH, XML_LANG, number
from config import LANG, TRACKS


A00 = 'a00-place-value'
A10 = 'a10-operation-symbols'
CROSS_ANCHOR = 'fs-id1170655004454'
TABLE_ANCHOR = 'fs-id1170655178881'


def variant(unit, track):
    return ET.parse(LANG / f'translation/{unit}.{track}.cnxml').getroot()


def rules():
    return json.loads((LANG / 'audio/a10-operation-symbols.rules.json').read_text(encoding='utf-8'))


def find_anchor(root, anchor):
    return next(node for node in root.iter() if node.get('id') == anchor)


def math_at(root, anchor=TABLE_ANCHOR, ordinal=1):
    return list(find_anchor(root, anchor).iter('{' + MATH + '}math'))[ordinal - 1]


class SourceBoundUnitTests(unittest.TestCase):
    def setUp(self):
        self.root = variant(A10, 'id-academic')
        self.rules = rules()

    def assert_math_rejected(self, changed):
        for track in TRACKS:
            with self.subTest(track=track), self.assertRaisesRegex(ValueError, 'unsupported_source_bound_narration'):
                build_units.source_bound_math(changed, self.rules, track)

    def test_all_eleven_source_fixtures_match_once_in_each_track(self):
        self.assertEqual(len(self.rules['math_fixtures']), 11)
        self.assertEqual(len({(row['anchor'], row['math_ordinal']) for row in self.rules['math_fixtures']}), 11)
        for track in TRACKS:
            root = variant(A10, track)
            actual = build_units.source_bound_math(root, self.rules, track)
            self.assertEqual(len(actual), 11)
            for row in self.rules['math_fixtures']:
                expression = math_at(root, row['anchor'], row['math_ordinal'])
                self.assertEqual(actual[id(expression)], row['expected'][track])

    def test_changed_source_anchor_is_rejected(self):
        find_anchor(self.root, TABLE_ANCHOR).set('id', 'unregistered-table-anchor')
        self.assert_math_rejected(self.root)

    def test_reordered_math_ordinals_are_rejected(self):
        first, second = math_at(self.root), math_at(self.root, ordinal=2)
        first[:], second[:] = list(second), list(first)
        self.assert_math_rejected(self.root)

    def test_equivalent_flattening_does_not_authorize_new_tree(self):
        expression = math_at(self.root)
        wrapper = ET.Element('{' + MATH + '}mrow')
        wrapper[:] = list(expression)
        expression[:] = [wrapper]
        self.assert_math_rejected(self.root)

    def test_changed_operator_is_rejected(self):
        math_at(self.root).find('.//{' + MATH + '}mo').text = '−'
        self.assert_math_rejected(self.root)

    def test_added_math_attribute_is_rejected(self):
        math_at(self.root).set('intent', 'unreviewed-intent')
        self.assert_math_rejected(self.root)

    def test_long_division_operand_and_enclosure_mutations_are_rejected(self):
        for mutation in ('swap-operands', 'missing-outside-operand', 'extra-inside-operand', 'changed-notation'):
            changed = copy.deepcopy(self.root)
            expression = math_at(changed, ordinal=5)
            enclosure = expression.find('.//{' + MATH + '}menclose')
            parent = next(node for node in expression.iter() if enclosure in list(node))
            outside = parent[list(parent).index(enclosure) - 1]
            self.assertEqual(outside.text, 'b')
            self.assertEqual(enclosure[0].text, 'a')
            if mutation == 'swap-operands':
                outside.text, enclosure[0].text = 'a', 'b'
            elif mutation == 'missing-outside-operand':
                parent.remove(outside)
            elif mutation == 'extra-inside-operand':
                extra = ET.SubElement(enclosure, '{' + MATH + '}mi')
                extra.text = 'c'
            else:
                enclosure.set('notation', 'longdiv radical')
            with self.subTest(mutation=mutation):
                self.assert_math_rejected(changed)

    def test_duplicate_or_unused_fixture_is_rejected(self):
        duplicate = copy.deepcopy(self.rules)
        duplicate['math_fixtures'].append(copy.deepcopy(duplicate['math_fixtures'][0]))
        with self.assertRaises(AssertionError):
            build_units.source_bound_math(self.root, duplicate, 'jv-academic')
        unused = copy.deepcopy(self.rules)
        addition = copy.deepcopy(unused['math_fixtures'][0])
        addition['anchor'] = 'not-present-in-this-unit'
        unused['math_fixtures'].append(addition)
        with self.assertRaisesRegex(AssertionError, 'Unused source math fixture'):
            build_units.source_bound_math(self.root, unused, 'jv-academic')

    def test_draft_validation_rejects_id_operator_and_numeric_mutations(self):
        for unit in (A00, A10):
            source = variant(unit, 'id-academic')
            target = variant(unit, 'jv-academic')
            draft_units.validate(source, target)
            for mutation in ('id', 'operator', 'number'):
                changed = copy.deepcopy(target)
                if mutation == 'id':
                    changed.set('id', 'wrong-source-id')
                elif mutation == 'operator':
                    next(changed.iter('{' + MATH + '}mo')).text = '×'
                else:
                    next(changed.iter('{' + MATH + '}mn')).text = '999'
                with self.subTest(unit=unit, mutation=mutation), self.assertRaises(AssertionError):
                    draft_units.validate(source, changed)


class NarrationRegressionTests(unittest.TestCase):
    def test_result_heading_ellipsis_is_a_pause_not_a_sequence(self):
        specification = next(row for row in rules()['prose_symbol_fixtures'] if row['id'] == 'A10-OPS-P01')
        for track in TRACKS:
            root = variant(A10, track)
            heading = find_anchor(root, TABLE_ANCHOR).findall('.//{*}thead/{*}row/{*}entry')[3]
            self.assertEqual(heading.text, specification['translated_visible_text'][track])
            spoken = build_units.speech_text(heading.text, track, A10)
            self.assertEqual(spoken, specification['expected'][track])
            self.assertNotIn('sateruse', spoken)
            self.assertNotIn('seterusnya', spoken)
            with self.assertRaisesRegex(ValueError, 'unsupported_ellipsis_context'):
                build_units.speech_text('Unregistered heading…', track, A10)
            self.assertIn('…', heading.text, 'Spoken substitution must not mutate visible text')

    def test_literal_three_xy_and_cross_prefix_are_not_conflated(self):
        specification = rules()
        literal = next(row for row in specification['prose_symbol_fixtures'] if row['id'] == 'A10-OPS-P02')
        prefix = next(row for row in specification['prose_symbol_fixtures'] if row['id'] == 'A10-OPS-P03')
        alternative = next(row for row in specification['math_fixtures'] if row['id'] == 'A10-OPS-M09')
        for track in TRACKS:
            root = variant(A10, track)
            paragraph = find_anchor(root, CROSS_ANCHOR)
            xy = next(node for node in paragraph if node.tag == '{' + CN + '}emphasis' and node.text == 'xy')
            previous = paragraph[list(paragraph).index(xy) - 1]
            self.assertRegex(previous.tail, r'3\s*$')
            self.assertEqual(xy.text, 'xy', 'The source letters are identifiers, not translatable prose')
            original = ET.tostring(paragraph)
            body = dict(build_units.blocks(root, track, A10, specification))[CROSS_ANCHOR]
            self.assertEqual(body.count(literal['expected'][track]), 1)
            self.assertLess(body.index(literal['expected'][track]), body.index(alternative['expected'][track]))
            self.assertTrue(body.startswith(prefix['expected_combined_prefix_and_glyph'][track]))
            self.assertEqual(body.count(prefix['expected_combined_prefix_and_glyph'][track]), 1)
            repeated = 'tandha silang tandha ping' if track.startswith('jv') else 'tanda silang tanda kali'
            self.assertNotIn(repeated, body)
            self.assertEqual(ET.tostring(paragraph), original, 'Narration must not rewrite source XML')

    def test_changed_three_xy_prefix_is_rejected(self):
        for track in TRACKS:
            root = variant(A10, track)
            paragraph = find_anchor(root, CROSS_ANCHOR)
            xy = next(node for node in paragraph if node.tag == '{' + CN + '}emphasis' and node.text == 'xy')
            previous = paragraph[list(paragraph).index(xy) - 1]
            previous.tail, count = re.subn(r'3\s*$', '4', previous.tail)
            self.assertEqual(count, 1)
            with self.subTest(track=track), self.assertRaisesRegex(AssertionError, 'Unregistered prose juxtaposition'):
                build_units.blocks(root, track, A10, rules())

    def test_currency_is_spoken_once_without_raw_dollar_symbol(self):
        for track in TRACKS:
            root = variant(A00, track)
            before = ET.tostring(root)
            opening = find_anchor(root, 'fs-id1461000')
            body = build_units.narrate(opening, track, A00, {})
            prefix = 'satus' if track.startswith('jv') else 'seratus'
            self.assertIn(prefix + ' dolar Amerika Serikat', body)
            self.assertEqual(body.count('dolar Amerika Serikat'), 3)
            self.assertNotIn('$', body)
            self.assertNotIn('dolar Amerika Serikat dolar', body)
            all_blocks = build_units.blocks(root, track, A00, None)
            self.assertTrue(all('$' not in text for _, text in all_blocks))
            self.assertEqual(ET.tostring(root), before)

    def test_money_figure_link_is_not_the_previous_number_line(self):
        root = variant(A00, 'id-academic')
        link = find_anchor(root, 'fs-id1461000').find('{*}link')
        self.assertEqual(link.get('target-id'), 'CNX_BMath_Figure_01_01_002')
        for track in TRACKS:
            spoken = build_units.narrate(link, track, A00, {})
            self.assertEqual(spoken, 'gambar dhuwit kertas' if track.startswith('jv') else 'gambar uang kertas')
            self.assertNotIn('garis', spoken)
        link.set('target-id', 'CNX_BMath_Figure_01_01_unregistered')
        with self.assertRaisesRegex(ValueError, 'Unregistered spoken source reference'):
            build_units.narrate(link, 'jv-academic', A00, {})

    def test_total_rows_skip_empty_cells_and_read_equals(self):
        expected = {
            'jv-academic': 'Nilai total: Gunggung padha karo satus telung puluh wolu',
            'jv-conversation': 'Nilai kabeh: Kabeh padha karo satus telung puluh wolu',
            'id-academic': 'Nilai total: Jumlah sama dengan seratus tiga puluh delapan',
        }
        for track in TRACKS:
            root = variant(A00, track)
            table = find_anchor(root, 'fs-id1714120')
            final_row = table.findall('.//{*}tbody/{*}row')[-1]
            self.assertEqual(len(final_row), 5)
            self.assertTrue(all(not ''.join(cell.itertext()).strip() for cell in final_row[:4]))
            # blocks() is the production boundary that normalizes whitespace
            # introduced when mtext equality is expanded before MathML speech.
            body = dict(build_units.blocks(root, track, A00, None))['fs-id1714120']
            self.assertEqual(body.strip().splitlines()[-1], expected[track])
            self.assertEqual(body.strip().splitlines()[-1].count(':'), 1)
            self.assertNotIn('=', body)
            worked = find_anchor(root, 'fs-id1785447')
            worked_final = re.sub(r'[ \t]+', ' ', build_units.narrate(worked, track, A00, {})).strip().splitlines()[-1]
            self.assertEqual(worked_final, ('Nilai kabeh' if track == 'jv-conversation' else 'Nilai total') + ': ' + number('215', track.startswith('jv')))

    def test_complete_transcripts_keep_heading_and_answer_conventions(self):
        for track in TRACKS:
            a10 = (LANG / f'review/audio/{A10}.{track}.md').read_text(encoding='utf-8')
            self.assertNotIn('sateruse', a10)
            self.assertNotIn('seterusnya', a10)
            a00 = (LANG / f'review/audio/{A00}.{track}.md').read_text(encoding='utf-8')
            self.assertNotIn('$', a00)
            self.assertNotIn('=', a00)
            self.assertEqual(a00.count('Wangsulan.' if track.startswith('jv') else 'Jawaban.'), 2)
            self.assertIn(number('176', track.startswith('jv')), a00)
            self.assertIn(number('237', track.startswith('jv')), a00)


class ReadOnlyProductTests(unittest.TestCase):
    def test_products_are_deterministic_current_and_do_not_write(self):
        # Both functions return bytes. Disable write helpers defensively so this
        # test can never accidentally become a CLI-like rewrite of artifacts.
        with (patch.object(build_units, 'write_bytes', side_effect=AssertionError('Forbidden unit write')),
              patch.object(draft_units, 'write_bytes', side_effect=AssertionError('Forbidden draft write'))):
            for unit in (A00, A10):
                with self.subTest(unit=unit):
                    draft_first = draft_units.products(unit)
                    self.assertEqual(draft_first, draft_units.products(unit))
                    first = build_units.products(unit)
                    snapshot = {path: hashlib.sha256((LANG / path).read_bytes()).hexdigest() for path in first}
                    second = build_units.products(unit)
                    self.assertEqual(first, second)
                    self.assertEqual(len(first), 8, 'One reader, three transcripts, three SSML files, one receipt')
                    for path, raw in first.items():
                        self.assertEqual((LANG / path).read_bytes(), raw, path)
                        self.assertEqual(hashlib.sha256((LANG / path).read_bytes()).hexdigest(), snapshot[path], path)
                    for path, raw in draft_first.items():
                        self.assertEqual((LANG / path).read_bytes(), raw, path)
                    for track in TRACKS:
                        speech = ET.fromstring(first[f'review/audio/{unit}.{track}.ssml'])
                        self.assertEqual(speech.get(XML_LANG), TRACKS[track][0])
                        self.assertTrue(speech.findall('{*}mark'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
