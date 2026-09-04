"""Source, math, fixed-context and saved-output regressions for all exponents."""
import base64
import copy
import html.parser
import json
import math
import unittest
import xml.etree.ElementTree as ET

from build import MATH, XML_LANG
import build_units as build
from config import LANG, TRACKS
from draft_units import UNITS, products as draft_products
import exponent_checks as checks

UNIT = 'a10-exponents'


class Reader(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.images, self.tables, self.links, self.ids = [], [], [], []
        self.maths = 0
        self.headers = 0

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        if tag == 'img':
            self.images.append(attrs)
        if tag == 'table':
            self.tables.append(attrs)
        if tag == 'a':
            self.links.append(attrs.get('href'))
        self.maths += tag == 'math'
        self.headers += tag == 'th'


class ExponentWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = json.loads((LANG / f'audio/{UNIT}.rules.json').read_text(encoding='utf-8'))
        cls.roots = {track: ET.parse(LANG / f'translation/{UNIT}.{track}.cnxml').getroot() for track in TRACKS}
        cls.source = cls.roots['id-academic']

    def test_whole_source_boundary_and_deterministic_phrase_replay(self):
        self.assertEqual(UNITS[UNIT]['slice'], [40, 53])
        self.assertEqual(len(self.source), 14)
        self.assertEqual(sum(bool(n.get('id')) for n in self.source.iter()), 32)
        self.assertEqual(len(self.source.findall('.//{' + MATH + '}math')), 32)
        self.assertEqual(len(self.source.findall('.//{*}exercise')), 3)
        self.assertEqual(len(self.source.findall('.//{*}solution')), 3)
        english = ET.parse(LANG / f'provenance/{UNIT}.en.cnxml').getroot()
        differences = [i for i, (a, b) in enumerate(zip(self.source.iter('{' + MATH + '}math'), english.iter('{' + MATH + '}math')), 1)
                       if build.tree_key(a) != build.tree_key(b)]
        self.assertEqual(differences, [12, 14])
        self.assertEqual(len(english.findall('.//{' + MATH + '}msup')), 24)
        for path, raw in draft_products(UNIT).items():
            self.assertEqual((LANG / path).read_bytes(), raw, path)

    def test_all_96_math_readings_and_independent_literal_operand_inventory(self):
        # Independent finite formula inventory: literal factors/exponents, not flattened text.
        powers = [(2,3), (2,9), (2,3), (2,3), (2,3), ('a','n'), ('a','n'),
                  ('a','n'), ('a',2), ('a',3), ('a',2), ('a',3), (7,2), (5,3),
                  (9,4), (12,5), (3,4), (3,4), (5,3), (1,7), (7,2), (0,5)]
        actual = []
        for node in self.source.iter('{' + MATH + '}msup'):
            pair = [''.join(child.itertext()) for child in node]
            actual.append(tuple(int(v) if v.isdigit() else v for v in pair))
        self.assertEqual(actual, powers)
        for fixture in self.rules['math_fixtures']:
            tree = build.fixture_element(fixture['source_mathml'])
            for track in TRACKS:
                self.assertEqual(checks.math_witness(tree, track), fixture['expected'][track])
        for track, root in self.roots.items():
            bound = build.source_bound_math(root, self.rules, track, self.source)
            checks.validate_semantics(self.source, root, self.rules, track, bound)

    def test_changed_power_factor_namespace_and_source_identity_reject(self):
        for change in ('base', 'exponent', 'flat', 'dot', 'missing_factor', 'namespace', 'attribute', 'anchor'):
            root = copy.deepcopy(self.source)
            power = root.find('.//{' + MATH + '}msup')
            if change == 'base':
                power[0].text = '3'
            elif change == 'exponent':
                power[1].text = '2'
            elif change == 'flat':
                power.tag = '{' + MATH + '}mrow'
            elif change == 'dot':
                root.find('.//{' + MATH + '}mo').text = '+'
            elif change == 'missing_factor':
                row = root.find('.//{' + MATH + '}mrow')
                row.remove(row[0])
            elif change == 'namespace':
                power[0].tag = '{wrong}mn'
            elif change == 'attribute':
                power.set('mathvariant', 'bold')
            else:
                root[1].set('id', 'invented')
            with self.subTest(change=change), self.assertRaises((ValueError, AssertionError)):
                build.blocks(root, 'id-academic', UNIT, self.rules, root)

    def test_all_seven_context_only_occurrences_reject_detached_maps(self):
        for track, root in self.roots.items():
            bound = build.source_bound_math(root, self.rules, track, self.source)
            self.assertEqual(len(bound.prose_only), 7)
            for node in root.iter('{' + MATH + '}math'):
                if id(node) in bound.prose_only:
                    for mapping in (bound, {}, dict(bound)):
                        with self.subTest(track=track), self.assertRaises(ValueError):
                            build.narrate(node, track, UNIT, mapping, self.rules)
            unknown = ET.fromstring('<math xmlns="' + MATH + '"><mn>2</mn></math>')
            with self.assertRaises(ValueError):
                build.narrate(unknown, track, UNIT, bound, self.rules)
            self.assertEqual(len(build.blocks(root, track, UNIT, self.rules, self.source)), 14)

    def test_direct_helpers_reject_detached_mutated_or_unvalidated_context(self):
        for track, original in self.roots.items():
            root = copy.deepcopy(original)
            bound = build.source_bound_math(root, self.rules, track, self.source)
            ids = {node.get('id'): node for node in root.iter() if node.get('id')}
            nodes = [ids[checks.PROSE_IDS[0]], ids[checks.CHART_IDS[1]],
                     ids['eip-958'], ids['fs-id1170655112606'][0]]
            for node in nodes:
                expected = build.narrate(node, track, UNIT, bound, self.rules)
                self.assertTrue(expected)
                for mapping in (bound, {}, dict(bound)):
                    with self.subTest(track=track, tag=node.tag), self.assertRaises(ValueError):
                        build.narrate(copy.deepcopy(node), track, UNIT, mapping, self.rules)
                changed_rules = copy.deepcopy(self.rules)
                changed_rules['prose_fixtures'][0]['expected'][track] += ' changed'
                with self.assertRaises(ValueError):
                    build.narrate(node, track, UNIT, bound, changed_rules)
                with self.assertRaises(ValueError):
                    build.narrate(node, next(t for t in TRACKS if t != track), UNIT, bound, self.rules)
                node.set('unregistered-context', 'changed after binding')
                with self.assertRaises(ValueError):
                    build.narrate(node, track, UNIT, bound, self.rules)
                node.attrib.pop('unregistered-context')
            # Rebinding an altered tree is not an escape from the full gate.
            ids[checks.PROSE_IDS[0]][-1].tail = ', changed positive domain to negative.'
            with self.assertRaises(AssertionError):
                build.source_bound_math(root, self.rules, track, self.source)

    def test_entire_target_prose_tables_charts_and_reference_are_bound(self):
        for track, original in self.roots.items():
            for change in ('domain', 'bare_n', 'answer', 'zero', 'summary', 'aria', 'blank', 'row', 'alt', 'path', 'reference', 'prose'):
                root = copy.deepcopy(original)
                nodes = {n.get('id'): n for n in root.iter() if n.get('id')}
                if change in ('domain', 'bare_n'):
                    nodes[checks.PROSE_IDS[0]][-1].tail = ', altered domain.'
                elif change in ('answer', 'zero'):
                    nodes[checks.PROSE_IDS[4 if change == 'answer' else 5]][-1].tail = '99'
                elif change in ('summary', 'aria'):
                    nodes[checks.TABLE_IDS[1 if change == 'summary' else 0]].set('summary' if change == 'summary' else 'aria-label', 'wrong')
                elif change in ('blank', 'row'):
                    tbody = nodes['eip-958'].find('.//{*}tbody')
                    if change == 'blank':
                        tbody[0][0].text = '0'
                    else:
                        tbody.remove(tbody[0])
                elif change == 'alt':
                    nodes[checks.CHART_IDS[1]].set('alt', 'wrong factors')
                elif change == 'path':
                    nodes[checks.CHART_IDS[0]][0].set('src', 'wrong.jpg')
                elif change == 'reference':
                    nodes['fs-id1170655112606'][0].set('target-id', 'unknown-table')
                else:
                    nodes['fs-id1170654982105'].text = 'Unregistered source wording'
                with self.subTest(track=track, change=change), self.assertRaises((ValueError, AssertionError)):
                    build.blocks(root, track, UNIT, self.rules, self.source)

    def test_finite_reading_rule_mutations_reject(self):
        for group in ('math_fixtures', 'table_fixtures', 'prose_fixtures', 'chart_fixtures', 'reference_fixtures'):
            for track, root in self.roots.items():
                rules = copy.deepcopy(self.rules)
                rules[group][0]['expected'][track] += ' incorrect extra answer'
                with self.subTest(group=group, track=track), self.assertRaises(AssertionError):
                    build.blocks(root, track, UNIT, rules, self.source)
        for field in ('explicit_factors_before_ellipsis', 'explicit_factors_after_ellipsis', 'total_factor_count_symbol'):
            rules = copy.deepcopy(self.rules)
            rules['notation_conventions']['finite_diagram_factor_pattern'][field] = 99
            with self.assertRaises(AssertionError):
                build.blocks(self.source, 'id-academic', UNIT, rules, self.source)
        rules = copy.deepcopy(self.rules)
        rules['math_fixtures'][9].pop('standalone_readout_authorized')
        with self.assertRaises(AssertionError):
            build.blocks(self.source, 'id-academic', UNIT, rules, self.source)

    def test_five_source_results_and_complete_worked_steps(self):
        table = next(n for n in self.source.iter() if n.get('id') == 'eip-958')
        rows = table.findall('.//{*}tbody/{*}row')
        self.assertEqual(len(rows), 5)
        self.assertFalse(''.join(rows[0][0].itertext()).strip())
        for row in rows[1:4]:
            factors = [int(n.text) for n in row[1].iter('{' + MATH + '}mn')]
            self.assertEqual(math.prod(factors), 81)
        self.assertEqual(rows[4][1].text, '81')
        self.assertEqual([5**3, 1**7, 7**2, 0**5], [125, 1, 49, 0])
        for track, root in self.roots.items():
            blocks = build.blocks(root, track, UNIT, self.rules, self.source)
            checks.validate_readout(blocks, self.rules, track)

    def test_mixed_mime_embedded_assets_and_real_reader_link(self):
        page = Reader()
        page.feed((LANG / f'review/units/{UNIT}.html').read_text(encoding='utf-8'))
        self.assertEqual((page.maths, len(page.tables), len(page.images), page.headers), (96, 6, 6, 6))
        self.assertEqual(len(page.ids), len(set(page.ids)))
        manifest = json.loads((LANG / f'translation/{UNIT}.assets.json').read_text(encoding='utf-8'))
        for track, root in self.roots.items():
            self.assertIn(f'#{UNIT}--{track}--fs-id1170654954100', page.links)
            for asset in manifest['assets']:
                output = asset['outputs'][track]
                payload = (LANG / output['path']).read_bytes()
                matches = [img for img in page.images if base64.b64decode(img['src'].split(',', 1)[1]) == payload]
                self.assertEqual(len(matches), 1)
                self.assertTrue(matches[0]['src'].startswith('data:' + output['mime_type'] + ';base64,'))
            table = next(n for n in root.iter() if n.get('id') == 'eip-958')
            rendered = next(t for t in page.tables if t['id'] == f'{UNIT}--{track}--eip-958')
            self.assertEqual(rendered['aria-label'], table.get('summary'))

    def test_saved_ssml_and_transcripts_have_exact_marks_and_cues(self):
        for track, root in self.roots.items():
            blocks = build.blocks(root, track, UNIT, self.rules, self.source)
            ssml = ET.parse(LANG / f'review/audio/{UNIT}.{track}.ssml').getroot()
            transcript = (LANG / f'review/audio/{UNIT}.{track}.md').read_text(encoding='utf-8')
            self.assertEqual(ssml.get(XML_LANG), TRACKS[track][0])
            self.assertEqual([n.get('name') for n in ssml.findall('{*}mark')], ['m82453--' + a for a, _ in blocks])
            self.assertEqual([n.text for n in ssml.findall('{*}p')][1:], [s for _, s in blocks])
            for _, text in blocks:
                self.assertIn(text, transcript)
            for group in ('table_fixtures', 'prose_fixtures', 'chart_fixtures'):
                for fixture in self.rules[group]:
                    self.assertEqual(transcript.count(fixture['expected'][track]), 1)

    def test_saved_products_deterministic_and_all_prior_units_unchanged(self):
        generated = build.products(UNIT)
        self.assertEqual(generated, build.products(UNIT))
        for path, raw in generated.items():
            self.assertEqual((LANG / path).read_bytes(), raw, path)
        for unit in UNITS:
            if unit != UNIT:
                for path, raw in build.products(unit).items():
                    self.assertEqual((LANG / path).read_bytes(), raw, path)


if __name__ == '__main__':
    unittest.main()
