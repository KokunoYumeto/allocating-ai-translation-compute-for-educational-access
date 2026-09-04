"""Finite expression/equation workflow checks; no production algebra parser."""
import copy
import html.parser
import json
import re
import unittest
import xml.etree.ElementTree as ET
from build import CN, MATH, XML_LANG, local, number, translated
import build_units as build
from config import LANG, TRACKS
from draft_units import UNITS, merged_edits, products as draft_products

UNIT = 'a10-expressions-equations'


def normalized(text):
    return re.sub(r'\s+', ' ', text.replace(',', ' ')).strip().lower()


def finite_read(expression, jv):
    """Independent test-only token walk, restricted to this exact notation set."""
    tag = local(expression)
    if tag == 'mn':
        value = number(expression.text, jv)
        return value.replace('seket', 'sèket').replace('selawe', 'salawé') if jv else value
    if tag == 'mi':
        return ('aksara ' if jv else 'huruf ') + {'n': 'en', 'x': 'eks', 'y': 'ye'}[expression.text]
    if tag == 'mo':
        return {'+': 'ditambah', '−': 'dikurangi', '·': 'ping' if jv else 'kali',
                '÷': 'dipara' if jv else 'dibagi', '=': 'padha karo' if jv else 'sama dengan',
                '(': 'bukak kurung biasa' if jv else 'buka kurung biasa', ')': 'tutup kurung biasa'}[expression.text]
    if tag == 'mfrac':
        assert len(expression) == 2
        return 'pecahan: ' + finite_read(expression[0], jv) + ' per ' + finite_read(expression[1], jv) + (' pungkasan pecahan' if jv else ' akhir pecahan')
    if tag == 'msup':
        assert len(expression) == 2
        assert [node.text for node in expression] == ['y', '3']
        return finite_read(expression[0], jv) + ' pangkat ' + finite_read(expression[1], jv) + (' pungkasan pangkat' if jv else ' akhir pangkat')
    assert tag in ('math', 'mrow')
    result = []
    for index, child in enumerate(expression):
        if index and local(expression[index - 1]) == 'mn' and (local(child) == 'mi' or local(child) == 'mo' and child.text == '('):
            result.append('ping' if jv else 'kali')
        result.append(finite_read(child, jv))
    return ' '.join(result)


class PageTables(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = []
        self.math_count = 0
        self.images = 0
        self.headers = 0
        self.ids = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if attributes.get('id'):
            self.ids.append(attributes['id'])
        if tag == 'table':
            self.tables.append(attributes)
        self.math_count += tag == 'math'
        self.images += tag == 'img'
        self.headers += tag == 'th'


class ExpressionsWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = json.loads((LANG / f'audio/{UNIT}.rules.json').read_text(encoding='utf-8'))
        cls.roots = {track: ET.parse(LANG / f'translation/{UNIT}.{track}.cnxml').getroot() for track in TRACKS}
        cls.source = cls.roots['id-academic']

    def test_source_boundary_and_exact_draft_replay(self):
        self.assertEqual(UNITS[UNIT]['slice'], [28, 40])
        self.assertEqual(self.source[1].get('id'), 'fs-id1170654957085')
        self.assertEqual(self.source[-1].get('id'), 'fs-id1170655205588')
        self.assertEqual(sum(bool(node.get('id')) for node in self.source.iter()), 34)
        self.assertFalse(any(node.get('id') == 'fs-id1170654982105' for node in self.source.iter()))
        self.assertEqual(len(self.source.findall('.//{' + MATH + '}math')), 21)
        self.assertEqual(len(self.source.findall('.//{*}exercise')), 3)
        for path, raw in draft_products(UNIT).items():
            self.assertEqual((LANG / path).read_bytes(), raw, path)

    def test_63_independent_finite_math_readings(self):
        for fixture in self.rules['math_fixtures']:
            tree = build.fixture_element(fixture['source_mathml'])
            self.assertEqual(build.sha(build.tree_key(tree).encode()), fixture['source_tree_sha256'])
            for track, reading in fixture['expected'].items():
                with self.subTest(fixture=fixture['id'], track=track):
                    self.assertEqual(normalized(reading), normalized(finite_read(tree, track.startswith('jv'))))
        for track, root in self.roots.items():
            self.assertEqual(len(build.source_bound_math(root, self.rules, track, self.source)), 21)

    def test_fraction_and_power_cannot_flatten_or_swap(self):
        for kind in ('swap_fraction', 'flatten_fraction', 'flatten_power', 'exponent', 'power_scope'):
            changed = copy.deepcopy(self.source)
            fraction = changed.find('.//{' + MATH + '}mfrac')
            power = changed.find('.//{' + MATH + '}msup')
            if kind == 'swap_fraction':
                fraction[:] = list(reversed(fraction))
            elif kind == 'flatten_fraction':
                fraction.tag = '{' + MATH + '}mrow'
            elif kind == 'flatten_power':
                power.tag = '{' + MATH + '}mrow'
            elif kind == 'exponent':
                power[1].text = '4'
            else:
                wrapper = ET.Element('{' + MATH + '}mrow')
                wrapper.append(copy.deepcopy(power[1]))
                ET.SubElement(wrapper, '{' + MATH + '}mo').text = '÷'
                ET.SubElement(wrapper, '{' + MATH + '}mn').text = '14'
                power[1] = wrapper
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                build.source_bound_math(changed, self.rules, 'id-academic')

    def test_changed_operators_attributes_anchors_and_ordinals_rejected(self):
        for kind in ('number', 'operator', 'letter', 'attribute', 'namespace', 'anchor'):
            changed = copy.deepcopy(self.source)
            if kind in ('number', 'operator', 'letter'):
                tag, value = {'number': ('mn', '999'), 'operator': ('mo', '−'), 'letter': ('mi', 'z')}[kind]
                changed.find('.//{' + MATH + '}' + tag).text = value
            elif kind == 'attribute':
                changed.find('.//{' + MATH + '}mo').set('stretchy', 'true')
            elif kind == 'namespace':
                changed.find('.//{' + MATH + '}mn').tag = '{wrong}mn'
            else:
                changed[4].set('id', 'wrong-anchor')
            with self.subTest(kind=kind), self.assertRaises((ValueError, AssertionError)):
                build.source_bound_math(changed, self.rules, 'id-academic')
        rules = copy.deepcopy(self.rules)
        rules['math_fixtures'][0]['math_ordinal'] = 99
        with self.assertRaises(ValueError):
            build.source_bound_math(self.source, rules, 'id-academic')

    def test_complete_table_binding_and_unknown_text_rejected(self):
        for track, root in self.roots.items():
            build.validate_nonmath_fixtures(root, self.source, UNIT, self.rules, track)
        for anchor, kind in [('eip-10', 'summary'), ('fs-id1170655221887', 'aria-label'), ('eip-10', 'row'), ('eip-10', 'classification')]:
            changed = copy.deepcopy(self.roots['jv-academic'])
            table = next(node for node in changed.iter() if node.get('id') == anchor)
            if kind in ('summary', 'aria-label'):
                table.set(kind, 'unregistered target wording')
            elif kind == 'row':
                body = table.find('.//{*}tbody')
                body.remove(body[0])
            else:
                table.find('.//{*}emphasis').text = 'ekspresi'
            with self.subTest(kind=kind), self.assertRaises(AssertionError):
                build.validate_nonmath_fixtures(changed, self.source, UNIT, self.rules, 'jv-academic')

    def test_summary_survives_cnxml_and_becomes_reader_label(self):
        page = PageTables()
        page.feed((LANG / f'review/units/{UNIT}.html').read_text(encoding='utf-8'))
        self.assertEqual((len(page.tables), page.math_count, page.images, page.headers), (9, 63, 0, 15))
        self.assertEqual(len(page.ids), len(set(page.ids)))
        for track, root in self.roots.items():
            node = next(node for node in root.iter() if node.get('id') == 'eip-10')
            table = next(attrs for attrs in page.tables if attrs['id'] == f'{UNIT}--{track}--eip-10')
            self.assertEqual(table['aria-label'], node.get('summary'))
            self.assertTrue(table['aria-label'])
            self.assertIsNone(node.find('.//{*}thead'))

    def test_all_eight_classifications_and_no_math_answer_leak(self):
        build.validate_expression_answers(self.source, self.roots, self.rules)
        for kind in ('classification', 'spoken_leak'):
            rules = copy.deepcopy(self.rules)
            if kind == 'classification':
                rules['classification_checks'][0]['expected_classification'] = 'expression'
            else:
                rules['math_fixtures'][9]['expected']['jv-academic'] += ' persamaan'
            with self.assertRaises(AssertionError):
                build.validate_expression_answers(self.source, self.roots, rules)
        for track, root in self.roots.items():
            bound = build.source_bound_math(root, self.rules, track, self.source)
            labels = self.rules['answer_policy']['expected_answer_labels'][track]
            for fixture in self.rules['table_fixtures']:
                readout = fixture['expected'][track]
                table = next(node for node in root.iter() if node.get('id') == fixture['table_id'])
                for row in table.findall('.//{*}tbody/{*}row'):
                    formula = row.find('.//{' + MATH + '}math')
                    self.assertIn(normalized(bound[id(formula)]), normalized(readout))
                if fixture['table_id'] == 'eip-10':
                    lines = readout.splitlines()[1:]
                    self.assertEqual(len(lines), 4)
                    for line, check in zip(lines, self.rules['classification_checks'][:4]):
                        self.assertIn(labels[check['expected_classification']], line)

    def test_transcript_ssml_marks_answer_cues_and_table_once(self):
        ss = '{http://www.w3.org/2001/10/synthesis}'
        for track, root in self.roots.items():
            blocks = build.blocks(root, track, UNIT, self.rules, self.source)
            self.assertEqual(len(blocks), 13)
            transcript = (LANG / f'review/audio/{UNIT}.{track}.md').read_text(encoding='utf-8')
            ssml = ET.parse(LANG / f'review/audio/{UNIT}.{track}.ssml').getroot()
            self.assertEqual(ssml.get(XML_LANG), TRACKS[track][0])
            self.assertEqual([node.get('name') for node in ssml.findall(ss + 'mark')], ['m82453--' + anchor for anchor, _ in blocks])
            self.assertEqual([node.text for node in ssml.findall(ss + 'p')][1:], [body for _, body in blocks])
            cue = 'Wangsulan.' if track.startswith('jv') else 'Jawaban.'
            self.assertEqual(transcript.count(cue), 2)
            for fixture in self.rules['table_fixtures']:
                self.assertEqual(transcript.count(fixture['expected'][track]), 1)
            for anchor in ('fs-id1170655166808', 'fs-id1170655205588'):
                body = dict(blocks)[anchor]
                problem, answer = body.split(cue)
                self.assertNotIn('bagean a: persamaan', problem)
                self.assertNotIn('bagian a: persamaan', problem)
                self.assertTrue(answer.strip())

    def test_saved_products_and_determinism(self):
        generated = build.products(UNIT)
        self.assertEqual(generated, build.products(UNIT))
        for path, raw in generated.items():
            self.assertEqual((LANG / path).read_bytes(), raw, path)


if __name__ == '__main__':
    unittest.main()
