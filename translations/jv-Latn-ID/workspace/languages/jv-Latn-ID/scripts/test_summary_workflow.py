"""Production checks for the four-component m81243 reader and narration."""
import copy
import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from build import XML_LANG
import build_summary
from config import LANG, TRACKS
import draft_summary
from qa import Reader
import summary_checks as checks


class SummaryWorkflow(unittest.TestCase):
    def test_complete_bound_context_and_all_narration_blocks(self):
        for track in TRACKS:
            roots, blocks, media, rules = checks.bind(track)
            self.assertEqual(list(roots), ['title', 'metadata', 'recap', 'glossary'])
            self.assertEqual([mark for mark, _ in blocks],
                             rules['reader_and_ssml_contract']['block_marks'])
            self.assertEqual(len(blocks), 14)
            self.assertEqual(len(rules['prose_fixtures']), 35)
            self.assertEqual(len(rules['nonspoken_fixtures']), 3)
            self.assertEqual(len(rules['structural_cues']), 9)
            self.assertEqual(len(media), 1)
            joined = '\n'.join(body for _, body in blocks)
            self.assertNotIn('7cbc90c7-60c8-4211-bffe-b77aadc95509', joined)
            self.assertNotIn('m81243', joined)

    def test_chart_procedures_and_glossary_facts_independently_recomputed(self):
        source = draft_summary.sources()['a00-id']
        recap = source['recap']
        self.assertEqual([len(node) for node in recap.findall('{*}list/{*}item/{*}list')], [2, 3, 4])
        rules = checks.checked_rules()
        chart = rules['chart_fixtures'][0]
        digits = chart['digit_cells']
        self.assertEqual(digits[:8], [None] * 8)
        self.assertEqual(sum((digit or 0) * place for digit, place in
                             zip(digits, chart['column_place_values'])), 5278194)
        meanings = {node.get('id'): (node.text or '') for node in source['glossary'].findall('.//{*}meaning')}
        self.assertRegex(meanings['fs-id2567732'], r'1, 2, 3,\s*…')
        self.assertRegex(meanings['fs-id1934263'], r'0, 1, 2, 3,\s*…')
        self.assertIn('0', meanings['fs-id2284600'])
        rounding = rules['semantic_invariants']['rounding']
        self.assertEqual((rounding['threshold'], rounding['increment'],
                          rounding['carry_from_digit'], rounding['replacement_digit']), (5, 1, 9, 0))

    def test_changed_rules_source_target_and_asset_fail_closed(self):
        rules = copy.deepcopy(checks.checked_rules())
        rules['block_fixtures'][0]['expected']['id-academic'] = 'changed'
        with self.assertRaises(AssertionError):
            checks.bind('id-academic', rules)

        original_blob = draft_summary.pinned_blob
        def changed_blob(repo, path):
            raw = original_blob(repo, path)
            return raw + b'changed' if path.endswith('m81243/index.cnxml') else raw
        with patch.object(draft_summary, 'pinned_blob', changed_blob), self.assertRaises(AssertionError):
            checks.bind('jv-academic')

        original_parse = checks.ET.parse
        target = LANG / f'translation/{checks.UNIT}.recap.jv-conversation.cnxml'
        def changed_parse(path, *args, **kwargs):
            tree = original_parse(path, *args, **kwargs)
            if Path(path) == target:
                tree.getroot()[0].text = 'changed'
            return tree
        with patch.object(checks.ET, 'parse', changed_parse), self.assertRaises(AssertionError):
            checks.bind('jv-conversation')

        output = json.loads((LANG / f'translation/{checks.UNIT}.assets.json').read_bytes())['assets'][0]['outputs']['jv-academic']['path']
        original_read = Path.read_bytes
        def changed_asset(path):
            raw = original_read(path)
            return raw + b'changed' if path == LANG / output else raw
        with patch.object(Path, 'read_bytes', changed_asset), self.assertRaises(AssertionError):
            checks.bind('jv-academic')

    def test_saved_reader_transcripts_and_ssml_are_deterministic(self):
        generated = build_summary.products()
        self.assertEqual(generated, build_summary.products())
        for name, raw in generated.items():
            self.assertEqual((LANG / name).read_bytes(), raw, name)
        page = generated[f'review/units/{checks.UNIT}.html'].decode()
        reader = Reader()
        reader.feed(page)
        self.assertEqual(len(reader.ids), 69)
        self.assertEqual(len(reader.tracks), 12)
        self.assertEqual(len(reader.images), 3)
        self.assertEqual(reader.maths, 0)
        self.assertNotIn('7cbc90c7-60c8-4211-bffe-b77aadc95509', page)
        rules = checks.checked_rules()
        for track, (locale, _) in TRACKS.items():
            document = ET.fromstring(generated[f'review/audio/{checks.UNIT}.{track}.ssml'])
            self.assertEqual(document.get(XML_LANG), locale)
            self.assertEqual([node.get('name') for node in document.findall('{*}mark')],
                             rules['reader_and_ssml_contract']['block_marks'])

    def test_coverage_records_separate_integrated_component_build(self):
        from coverage import component_coverage
        rows = component_coverage()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['offline_reader'], 'standalone_draft_built')
        self.assertEqual(rows[0]['narration_ssml'], 'three_track_drafts_built')
        self.assertIsNotNone(rows[0]['verified_build'])
        self.assertFalse(rows[0]['full_module_complete'])


if __name__ == '__main__':
    unittest.main()
