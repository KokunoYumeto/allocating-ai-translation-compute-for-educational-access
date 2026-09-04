import copy
import json
import unittest
import xml.etree.ElementTree as ET

from build import MATH, XML_LANG
from config import LANG, TRACKS
from qa import Reader
import addition_production_checks as checks
import build_addition_production as production
import draft_addition_production as draft


class AdditionProductionWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source, cls.variants, cls.rules, cls.edits = checks.load_saved()
        cls.generated = production.products()

    def test_complete_cnxml_census_and_exact_track_hashes(self):
        for track in TRACKS:
            root = self.variants[track]
            ids = [node.get('id') for node in root.iter() if node.get('id')]
            self.assertEqual(ids, self.rules['ordered_source_ids'])
            self.assertEqual((len(ids), len(set(ids))), (756, 756))
            self.assertEqual(len(list(root.iter('{' + MATH + '}math'))), 401)
            self.assertEqual((len(root.findall('.//{*}media')),
                              len(root.findall('.//{*}table'))), (50, 21))
            self.assertEqual((len(root.findall('.//{*}exercise')),
                              len(root.findall('.//{*}solution'))), (129, 89))
            self.assertEqual(checks.tree_sha(root),
                             self.rules['scope']['target_module_tree_sha256'][track])
            if track.startswith('jv'):
                self.assertEqual(root.get(XML_LANG), 'jv-Latn-ID')

    def test_finite_blocks_and_answer_boundaries(self):
        for track in TRACKS:
            blocks = checks.narration_blocks(
                self.source, self.variants[track], self.rules, track, self.edits)
            self.assertEqual(len(blocks), 189)
            self.assertEqual([mark for mark, _ in blocks],
                             [row['mark'] for row in self.rules['block_fixtures']])
            self.assertEqual([body for _, body in blocks],
                             [row['expected'][track] for row in self.rules['block_fixtures']])
        answers = self.rules['answer_policy']
        self.assertEqual((answers['supplied'], answers['absent'],
                          answers['untitled_cue_count'], answers['existing_solution_titles']),
                         (89, 40, 74, 15))
        self.assertFalse(answers['synthesis_of_missing_answer'])
        self.assertEqual(sum(not row['source_answer_available']
                             for row in self.rules['exercise_inventory']), 40)
        self.assertTrue(all(row['expected_solution']['jv-academic'] is None
                            for row in self.rules['exercise_inventory']
                            if not row['source_answer_available']))

    def test_detached_mutated_wrong_track_and_rule_payload_fail_closed(self):
        target = self.variants['jv-academic']
        bound = checks.bind(self.source, target, self.rules, 'jv-academic', self.edits)
        fixture = self.rules['math_fixtures'][0]
        node = checks.node_at(target, fixture['source_path'])
        self.assertEqual(checks.registered_math_readout(
            node, self.source, target, self.rules, 'jv-academic', bound),
            fixture['expected']['jv-academic'])
        with self.assertRaisesRegex(ValueError, 'unsupported_source_bound_narration'):
            checks.registered_math_readout(
                copy.deepcopy(node), self.source, target, self.rules, 'jv-academic', bound)
        with self.assertRaisesRegex(ValueError, 'unsupported_source_bound_narration'):
            checks.registered_math_readout(
                node, self.source, target, self.rules, 'jv-conversation', bound)
        changed_rules = copy.deepcopy(self.rules)
        changed_rules['block_fixtures'][0]['expected']['jv-academic'] += ' owah'
        with self.assertRaisesRegex(ValueError, 'unsupported_source_bound_narration'):
            checks.registered_math_readout(
                node, self.source, target, changed_rules, 'jv-academic', bound)
        original = node.find('.//*').text
        node.find('.//*').text = (original or '') + ' owah'
        try:
            with self.assertRaisesRegex(ValueError, 'unsupported_source_bound_narration'):
                checks.registered_math_readout(
                    node, self.source, target, self.rules, 'jv-academic', bound)
        finally:
            node.find('.//*').text = original
        with self.assertRaisesRegex(ValueError, 'unsupported_source_bound_narration'):
            checks.registered_math_readout(
                node, self.source, target, self.rules, 'jv-academic', {})

    def test_reader_and_ssml_exact_census(self):
        production.verify_saved(self.generated)
        page = self.generated[f'review/units/{draft.UNIT}.html'].decode('utf-8')
        reader = Reader(); reader.feed(page)
        self.assertEqual((reader.maths, len(reader.images), len(reader.tracks)),
                         (1203, 150, 36))
        self.assertEqual(page.count('data-editorial-solution-cue="true"'), 222)
        self.assertEqual(len(reader.ids), len(set(reader.ids)))
        for track, (locale, _label) in TRACKS.items():
            root = ET.fromstring(self.generated[f'review/audio/{draft.UNIT}.{track}.ssml'])
            self.assertEqual(root.get(XML_LANG), locale)
            self.assertEqual(len(root.findall('{*}mark')), 189)
            self.assertEqual(len(root.findall('{*}p')), 189)
            self.assertNotIn('<voice', ET.tostring(root, encoding='unicode'))
            self.assertNotIn('<audio', ET.tostring(root, encoding='unicode'))

    def test_production_receipt_is_truthful_and_noncoverage_discoverable(self):
        receipt = json.loads(self.generated[production.RECEIPT])
        self.assertEqual(receipt['status'], 'structural_pass_human_review_pending')
        self.assertTrue(receipt['complete_source_scope'])
        self.assertFalse(receipt['whole_module_complete'])
        self.assertEqual(receipt['synthesized_audio_files'], 0)
        self.assertFalse(receipt['review_limits']['native_language_review'])
        self.assertNotIn(f'qa/{draft.UNIT}.draft-receipt.json', self.generated)
        self.assertTrue((LANG / f'qa/{draft.UNIT}.in-progress.json').is_file())


if __name__ == '__main__':
    unittest.main()
