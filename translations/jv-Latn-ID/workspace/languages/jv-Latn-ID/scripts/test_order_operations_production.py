"""Focused fail-closed production tests for all of m82453/fs-id1170654953465."""
from __future__ import annotations

import base64
import collections
import copy
import html.parser
import json
import re
import unittest
import xml.etree.ElementTree as ET

import build_order_operations as production
from build import MATH, XML_LANG, local
from config import LANG
import order_operations_checks as checks
import prepare_order_operations_assets as assets


class OfflineReader(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.images, self.tables, self.rows, self.tracks = [], [], [], [], []
        self.math = 0
        self._table_rows = None

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        if attrs.get('data-register'):
            self.tracks.append((attrs['data-register'], attrs.get('lang')))
        if tag == 'img':
            self.images.append(attrs)
        elif tag == 'table':
            self.tables.append(attrs)
            self._table_rows = 0
        elif tag == 'tr' and self._table_rows is not None:
            self._table_rows += 1
        elif tag == 'math':
            self.math += 1

    def handle_endtag(self, tag):
        if tag == 'table':
            self.rows.append(self._table_rows)
            self._table_rows = None


class OrderOperationsProduction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = checks.load_rules()
        cls.source, cls.english = checks.source_sections()
        cls.roots = checks.variants(cls.source)
        cls.asset_products = assets.asset_products()
        cls.products = production.products()

    def test_exact_complete_boundary_ids_order_and_counts(self):
        self.assertEqual(len(self.source), 31)
        self.assertEqual(self.source[0].tag.rsplit('}', 1)[-1], 'title')
        self.assertEqual(self.source[1].get('id'), 'fs-id1170655225397')
        self.assertEqual(self.source[-1].get('id'), 'fs-id1170654936028')
        ids = [node.get('id') for node in self.source.iter() if node.get('id')]
        self.assertEqual((len(ids), len(set(ids)), ids[-1]), (111, 111, 'fs-id1170654940244'))
        self.assertNotIn(checks.NEXT_SECTION, ids)
        self.assertEqual(len(list(self.source.iter('{' + MATH + '}math'))), 21)
        self.assertEqual(len(list(self.source.iter('{' + MATH + '}msup'))), 3)
        self.assertEqual(len(list(self.source.iter('{' + MATH + '}mfrac'))), 0)
        self.assertEqual((len(self.source.findall('.//{*}table')), len(self.source.findall('.//{*}media'))), (4, 23))
        self.assertEqual((len(self.source.findall('.//{*}exercise')), len(self.source.findall('.//{*}solution'))), (9, 9))
        self.assertEqual(len(self.source.findall('.//{*}link')), 0)
        for track, root in self.roots.items():
            checks.validate_scope(self.source, root, self.rules, track)
            self.assertEqual([node.get('id') for node in root.iter() if node.get('id')], ids)

    def test_six_corrections_and_only_three_numeric_sequence_exceptions(self):
        corrections = self.rules['accessible_description_policy']['target_attribute_exceptions']
        self.assertEqual([(row['phrase_index_zero_based'], row['element_id'], row['attribute']) for row in corrections], [
            (68, 'fs-id1167829713618', 'aria-label'),
            (70, 'fs-id1167824617198', 'alt'),
            (72, 'fs-id1167836329648', 'alt'),
            (75, 'fs-id1167836375645', 'aria-label'),
            (80, 'fs-id1171791418206', 'alt'),
            (89, 'fs-id1167829840981', 'aria-label'),
        ])
        for track in ('jv-academic', 'jv-conversation'):
            numeric = [row['phrase_index_zero_based'] for row in corrections
                       if row['source_digit_sequence'] != row['target_digit_sequences'][track]]
            self.assertEqual(numeric, [72, 75, 89])
            nodes = {node.get('id'): node for node in self.roots[track].iter() if node.get('id')}
            for row in corrections:
                self.assertEqual(nodes[row['element_id']].get(row['attribute']), row['expected_target_values'][track])

        mutations = []
        wrong = copy.deepcopy(self.roots['jv-academic'])
        next(node for node in wrong.iter() if node.get('id') == 'fs-id1167836329648').set('alt', 'Ekspresi (7)7 lan 8')
        mutations.append(wrong)
        wrong = copy.deepcopy(self.roots['jv-academic'])
        next(node for node in wrong.iter('{' + MATH + '}mn')).text = '99'
        mutations.append(wrong)
        wrong = copy.deepcopy(self.roots['jv-academic'])
        next(node for node in wrong.iter() if node.get('id') == 'fs-id1171791418206').set('alt', 'changed')
        mutations.append(wrong)
        wrong = copy.deepcopy(self.roots['jv-academic'])
        wrong.remove(wrong[2])
        mutations.append(wrong)
        for root in mutations:
            with self.assertRaises((AssertionError, ValueError)):
                checks.validate_scope(self.source, root, self.rules, 'jv-academic')

    def test_all_21_math_occurrences_are_live_tree_bound_without_fallback(self):
        fixtures = {(row['anchor'], row['math_ordinal']): row for row in self.rules['math_fixtures']}
        self.assertEqual(len(fixtures), 21)
        for track, root in self.roots.items():
            bound = checks.bind(root, self.source, self.rules, track)
            self.assertEqual(len(bound.math), 21)
            for block in root:
                for ordinal, node in enumerate(block.iter('{' + MATH + '}math'), 1):
                    fixture = fixtures[(block.get('id'), ordinal)]
                    if fixture['id'] in ('A10-ORD-M01', 'A10-ORD-M02', 'A10-ORD-M16'):
                        with self.assertRaises(ValueError):
                            checks.narrate(node, track, bound, self.rules)
                    else:
                        self.assertEqual(checks.narrate(node, track, bound, self.rules), fixture['expected'][track])
                    with self.assertRaises(ValueError):
                        checks.narrate(copy.deepcopy(node), track, bound, self.rules)
            first = next(root.iter('{' + MATH + '}math'))
            original = first[0][0].text if len(first[0]) else first[0].text
            leaf = next(node for node in first.iter() if not len(node) and (node.text or '').strip())
            prior = leaf.text
            leaf.text = '99'
            with self.assertRaises(ValueError):
                checks.narrate(first, track, bound, self.rules)
            leaf.text = prior
            with self.assertRaises(AssertionError):
                checks.narrate(first, next(name for name in checks.TRACKS if name != track), bound, self.rules)
        unknown = ET.fromstring('<math xmlns="' + MATH + '"><mn>2</mn></math>')
        bound = checks.bind(self.roots['id-academic'], self.source, self.rules, 'id-academic')
        with self.assertRaises(ValueError):
            checks.narrate(unknown, 'id-academic', bound, self.rules)
        changed_rules = copy.deepcopy(self.rules)
        changed_rules['math_fixtures'][0]['expected']['id-academic'] += ' changed'
        with self.assertRaises(AssertionError):
            checks.narrate(self.roots['id-academic'][1], 'id-academic', bound, changed_rules)

    def test_four_headerless_tables_have_35_rows_and_one_finite_readout_each(self):
        chart_by_id = {row['media_id']: row for row in self.rules['chart_fixtures']}
        for track, root in self.roots.items():
            blocks = dict(checks.blocks(root, track, self.rules, self.source))
            nodes = {node.get('id'): node for node in root.iter() if node.get('id')}
            row_counts = []
            for fixture in self.rules['table_fixtures']:
                table = nodes[fixture['table_id']]
                rows = table.findall('.//{*}tbody/{*}row')
                row_counts.append(len(rows))
                self.assertIsNone(table.find('.//{*}thead'))
                self.assertTrue(all(len(row) == 2 for row in rows))
                self.assertEqual(blocks[fixture['anchor']].count(fixture['expected'][track]), 1)
                contained = [chart_by_id[node.get('id')]['expected'][track]
                             for node in table.iter() if node.get('id') in chart_by_id]
                # Some rows intentionally repeat the same expression in source
                # MathML and in an image.  The whole-table fixture, not a count
                # heuristic on that repeated substring, is the speech authority.
                self.assertTrue(all(reading in fixture['expected'][track] for reading in contained))
                for row in fixture['row_fixtures']:
                    self.assertEqual(fixture['expected'][track].count(row['expected'][track]), 1)
            self.assertEqual(row_counts, [7, 6, 8, 14])
            self.assertEqual(sum(row_counts), 35)

    def test_23_exact_jpegs_manifest_and_reader_payloads(self):
        manifest = json.loads(self.asset_products[f'translation/{checks.UNIT}.assets.json'])
        self.assertEqual(len(manifest['assets']), 23)
        self.assertEqual(sum(row['source_bytes'] for row in manifest['assets']), 1603339)
        for row in manifest['assets']:
            outputs = row['outputs']
            self.assertEqual(len({outputs[track]['path'] for track in checks.TRACKS}), 1)
            raw = self.asset_products[outputs['id-academic']['path']]
            self.assertTrue(raw.startswith(b'\xff\xd8\xff'))
            self.assertEqual((len(raw), checks.sha(raw), assets.git_blob(raw)),
                             (row['source_bytes'], row['source_sha256'], row['source_git_blob_sha1']))
            self.assertEqual(list(assets.jpeg_dimensions(raw)), row['dimensions'])
            self.assertTrue(all(outputs[track]['mime_type'] == 'image/jpeg' for track in checks.TRACKS))
        reader = OfflineReader()
        reader.feed(self.products[f'review/units/{checks.UNIT}.html'].decode())
        self.assertEqual((reader.math, len(reader.images), len(reader.tables)), (63, 69, 12))
        self.assertEqual(sorted(reader.rows), sorted([7, 6, 8, 14] * 3))
        self.assertEqual(len(reader.ids), len(set(reader.ids)))
        self.assertEqual(collections.Counter(track for track, _ in reader.tracks), {track: 31 for track in production.DISPLAY_TRACKS})
        for row in manifest['assets']:
            raw = self.asset_products[row['outputs']['id-academic']['path']]
            matches = [image for image in reader.images
                       if base64.b64decode(image['src'].split(',', 1)[1]) == raw]
            self.assertEqual(len(matches), 3)
            self.assertTrue(all(image['src'].startswith('data:image/jpeg;base64,') and image.get('alt') for image in matches))

    def test_questions_answers_outer_cues_and_no_answer_fixture_leak(self):
        checks.validate_answers(self.source, self.rules)
        fixtures = {row['id']: row for row in self.rules['math_fixtures']}
        for track, root in self.roots.items():
            narration = checks.blocks(root, track, self.rules, self.source)
            by_anchor = dict(narration)
            cue = 'Wangsulan.' if track.startswith('jv') else 'Jawaban.'
            self.assertEqual(sum(body.count(cue) for _, body in narration), 6)
            self.assertEqual(checks.question_readouts(root, track, self.rules, self.source),
                             [fixtures[key]['expected'][track] for key in self.rules['answer_policy']['question_fixtures']])
            for fixture in self.rules['prose_fixtures'][5:]:
                question, answer = by_anchor[fixture['anchor']].split(cue, 1)
                self.assertNotIn(fixture['expected'][track], question)
                self.assertIn(fixture['expected'][track], answer)
            for fixture in self.rules['table_fixtures']:
                block = by_anchor[fixture['anchor']]
                solution_title = {'id-academic': 'Penyelesaian', 'jv-academic': 'Panyelesaian',
                                  'jv-conversation': 'Cara Ngrampungake'}[track]
                self.assertIn(solution_title, block)
                self.assertGreater(block.index(fixture['expected'][track]), block.index(solution_title))

    def test_ssml_transcripts_marks_locales_and_no_hidden_voice_or_lang(self):
        for track, root in self.roots.items():
            expected = checks.blocks(root, track, self.rules, self.source)
            ssml = ET.fromstring(self.products[f'review/audio/{checks.UNIT}.{track}.ssml'])
            transcript = self.products[f'review/audio/{checks.UNIT}.{track}.md'].decode()
            self.assertEqual(ssml.get(XML_LANG), checks.LOCALES[track])
            self.assertEqual([node.get('name') for node in ssml.findall('{*}mark')],
                             [checks.MODULE + '--' + anchor for anchor, _ in expected])
            self.assertEqual([node.text for node in ssml.findall('{*}p')][1:], [body for _, body in expected])
            self.assertEqual(len(ssml.findall('{*}p')), 32)
            self.assertFalse(ssml.findall('.//{*}voice'))
            self.assertFalse(ssml.findall('.//{*}lang'))
            self.assertTrue(all(''.join(node.itertext()).strip() for node in ssml.findall('{*}p')))
            for _, body in expected:
                self.assertIn(body, transcript)
            self.assertNotRegex('\n'.join(node.text or '' for node in ssml.findall('{*}p')[1:]),
                                r'\d|[+−÷·^=\[\]]')

    def test_asset_and_rule_mutations_fail_closed(self):
        manifest = json.loads(self.asset_products[f'translation/{checks.UNIT}.assets.json'])
        corrupted = dict(self.asset_products)
        path = manifest['assets'][0]['outputs']['id-academic']['path']
        corrupted[path] = corrupted[path][:-1] + bytes([corrupted[path][-1] ^ 1])
        with self.assertRaises(AssertionError):
            production._media_maps(corrupted, manifest)
        changed = copy.deepcopy(manifest)
        changed['assets'][0]['outputs']['jv-academic']['mime_type'] = 'image/png'
        with self.assertRaises(AssertionError):
            production._media_maps(self.asset_products, changed)
        changed_rules = copy.deepcopy(self.rules)
        changed_rules['table_fixtures'][0]['expected']['id-academic'] += ' altered'
        with self.assertRaises(AssertionError):
            checks.bind(self.roots['id-academic'], self.source, changed_rules, 'id-academic')

    def test_saved_products_match_a_second_deterministic_build(self):
        again = production.products()
        self.assertEqual(self.products, again)
        self.assertEqual(len(self.products), 37)
        for path, raw in self.products.items():
            self.assertEqual((LANG / path).read_bytes(), raw, path)
        receipt = json.loads(self.products[production.PRODUCTION_RECEIPT])
        self.assertEqual(receipt['counts']['source_physical_table_rows'], 35)
        self.assertEqual(receipt['counts']['absent_answers'], 0)
        self.assertEqual(receipt['counts']['numeric_sequence_exceptions'], 3)
        self.assertFalse(receipt['generic_numeric_exception'])
        self.assertFalse(receipt['hidden_language_fallback'])
        self.assertEqual(receipt['next_source_cursor'], {
            'section': checks.NEXT_SECTION, 'first_paragraph': checks.NEXT_FIRST_PARAGRAPH})
        for path, digest in receipt['output_sha256'].items():
            self.assertEqual(checks.sha(self.products[path]), digest)


if __name__ == '__main__':
    unittest.main()
