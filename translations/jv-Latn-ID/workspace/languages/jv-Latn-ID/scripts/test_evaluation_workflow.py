"""Regression tests for finite evaluation-section production integration."""
import copy
import json
import re
import unittest
import xml.etree.ElementTree as ET

from build_evaluation import BUILD_RECEIPT, HTML_PATH, products
from config import LANG
from draft_evaluation import products as draft_products
from evaluation_checks import (SECTION, TRACKS, bind, blocks, load_rules,
                               load_variants, narrate, sha)
from qa import Reader


class EvaluationWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules, cls.rules_raw = load_rules()
        cls.variants = load_variants()

    def test_draft_and_build_are_deterministic_and_saved(self):
        draft = draft_products()
        self.assertEqual(draft, draft_products())
        built = products()
        self.assertEqual(built, products())
        for generated in (draft, built):
            for path, raw in generated.items():
                self.assertEqual((LANG / path).read_bytes(), raw, path)

    def test_exact_three_track_readout_contract(self):
        for track in TRACKS:
            readout, bound = blocks(self.variants['id-academic'], self.variants[track],
                                    track, self.rules, self.rules_raw)
            self.assertEqual(len(readout), 13)
            self.assertEqual(len(bound.math), 38)
            self.assertEqual(len(bound.prose_only), 28)
            self.assertEqual(len(bound.prose), 18)
            self.assertEqual(len(bound.tables), 5)
            self.assertEqual(len(bound.charts), 16)
            combined = '\n'.join(text for _, text in readout)
            self.assertIsNone(re.search(r'[0-9$^=·]|(?<!aksara )(?<!huruf )\b[xy]\b', combined))
            cue = 'Wangsulan.' if track.startswith('jv') else 'Jawaban.'
            self.assertEqual(combined.count(cue), 6)
            title = self.rules['answer_policy']['worked_title_expected'][track]
            self.assertEqual(combined.count(title), 3)

    def test_context_only_and_live_node_guards_fail_closed(self):
        source = copy.deepcopy(self.variants['id-academic'])
        target = copy.deepcopy(self.variants['jv-academic'])
        bound = bind(source, target, 'jv-academic', self.rules, self.rules_raw)
        context_only = next(node for node in target.iter()
                            if node.tag.endswith('}math') and id(node) in bound.prose_only)
        with self.assertRaisesRegex(ValueError, 'unsupported_source_bound_narration'):
            narrate(context_only, bound)
        standalone = next(node for node in target.iter()
                          if node.tag.endswith('}math') and id(node) not in bound.prose_only)
        self.assertTrue(narrate(standalone, bound))
        with self.assertRaisesRegex(ValueError, 'unsupported_source_bound_narration'):
            narrate(copy.deepcopy(standalone), bound)
        standalone[0][0].text = '999'
        with self.assertRaisesRegex(ValueError, 'unsupported_source_bound_narration'):
            narrate(standalone, bound)

    def test_source_target_and_rules_mutations_are_rejected(self):
        source = copy.deepcopy(self.variants['id-academic'])
        target = copy.deepcopy(self.variants['jv-conversation'])
        changed_rules = copy.deepcopy(self.rules)
        changed_rules['math_fixtures'][0]['expected']['jv-conversation'] += ' palsu'
        with self.assertRaisesRegex(ValueError, 'unsupported_source_bound_narration'):
            bind(source, target, 'jv-conversation', changed_rules, self.rules_raw)
        source_math = next(source.iter('{http://www.w3.org/1998/Math/MathML}mn'))
        source_math.text = '99'
        with self.assertRaises((AssertionError, ValueError)):
            bind(source, target, 'jv-conversation', self.rules, self.rules_raw)

    def test_unknown_tree_has_no_generic_fallback(self):
        source = copy.deepcopy(self.variants['id-academic'])
        target = copy.deepcopy(self.variants['id-academic'])
        bound = bind(source, target, 'id-academic', self.rules, self.rules_raw)
        fake = ET.Element('{http://cnx.rice.edu/cnxml}para')
        fake.text = 'Teks aman nanging ora kaiket.'
        with self.assertRaisesRegex(ValueError, 'unsupported_source_bound_narration'):
            narrate(fake, bound)

    def test_reader_and_provider_free_ssml(self):
        page = (LANG / HTML_PATH).read_text(encoding='utf-8')
        reader = Reader()
        reader.feed(page)
        self.assertEqual(len(reader.ids), len(set(reader.ids)))
        self.assertEqual(len(reader.ids), 251)
        self.assertIn('fs-id1170655171250', reader.ids)
        self.assertEqual(reader.maths, 114)
        self.assertEqual(len(reader.images), 48)
        self.assertEqual(len(re.findall(r'<table\b', page)), 15)
        self.assertEqual(reader.links, [])
        for track in TRACKS:
            root = ET.parse(LANG / f'review/audio/a10-evaluate-expressions.{track}.ssml').getroot()
            self.assertEqual(root.tag, 'speak')
            self.assertEqual(len(list(root.iter('mark'))), 13)
            self.assertEqual(list(root.iter('voice')), [])
            spoken = ''.join(root.itertext())
            self.assertIsNone(re.search(r'[0-9$^=·]|(?<!aksara )(?<!huruf )\b[xy]\b', spoken))

    def test_receipt_records_exclusions_and_no_approval_claims(self):
        receipt = json.loads((LANG / BUILD_RECEIPT).read_text(encoding='utf-8'))
        self.assertEqual(receipt['source_ids'], 83)
        self.assertEqual(receipt['question_parts'], 15)
        self.assertEqual(receipt['reader']['source_bound_track_ids'], 249)
        self.assertEqual(receipt['next_excluded_section'], 'fs-id1170655163482')
        self.assertEqual(receipt['assets']['indonesian_release_overrides'], 2)
        for field in ('human_language_review', 'native_educator_review',
                      'browser_visual_review', 'screen_reader_review',
                      'pronunciation_review', 'synthesis', 'listening_review'):
            self.assertIs(receipt[field], False)
        self.assertEqual(receipt['synthesized_audio_files'], 0)
        self.assertIn('global inventory integration', receipt['next_cursor'])


if __name__ == '__main__':
    unittest.main()
