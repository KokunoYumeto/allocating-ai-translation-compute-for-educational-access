"""Exact front/content/back source selection and fail-closed consumer checks."""
import copy
import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch
from build import XML_LANG
from config import LANG, TRACKS
import draft_summary as summary


class SummaryComponents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = summary.sources()['a00-id']
        cls.tracks = summary.variants(cls.source)

    def test_complete_four_scopes_and_saved_determinism(self):
        products = summary.products()
        self.assertEqual(products, summary.products())
        self.assertEqual(len(products), 17)
        for name, raw in products.items():
            self.assertEqual((LANG / name).read_bytes(), raw)
        receipt = json.loads(products[f'qa/{summary.UNIT}.components-receipt.json'])
        self.assertEqual([c['original_document_path'] for c in receipt['components']], [[0], [1], [2, 6], [3]])
        self.assertEqual(len(receipt['excluded_content_sections']), 7)
        self.assertIn('fs-id2279009', receipt['excluded_content_sections'])
        self.assertFalse(receipt['full_module_complete'])
        self.assertEqual(receipt['source_objectives'], 6)
        self.assertEqual(receipt['source_glossary_definitions'], 7)
        self.assertEqual(len(receipt['source_ids']), 23)

    def test_locales_identifiers_and_unchanged_id_components(self):
        for track, roots in self.tracks.items():
            for key, root in roots.items():
                self.assertEqual(root.get(XML_LANG), None if track == 'id-academic' else 'jv-Latn-ID')
                if track == 'id-academic':
                    self.assertEqual(summary.tree_key(root), summary.tree_key(self.source[key]))
            self.assertEqual(roots['metadata'].findtext('{*}content-id'), 'm81243')
            self.assertEqual(roots['metadata'].findtext('{*}uuid'), '7cbc90c7-60c8-4211-bffe-b77aadc95509')

    def test_glossary_sequences_and_ordered_steps_preserved(self):
        for roots in self.tracks.values():
            meanings = roots['glossary'].findall('{*}definition/{*}meaning')
            self.assertIn('1, 2, 3,…', meanings[1].text)
            self.assertIn('0, 1, 2, 3, …', meanings[6].text)
            self.assertIn(' 0 ', meanings[3].text)
            self.assertEqual([len(n) for n in roots['recap'].findall('{*}list/{*}item/{*}list')], [2, 3, 4])

    def test_missing_moved_reordered_or_changed_scopes_rejected(self):
        for track in TRACKS:
            mutations = [
                lambda roots: roots.pop('metadata'),
                lambda roots: roots.update(glossary=roots['recap']),
                lambda roots: roots['glossary'].remove(roots['glossary'][0]),
                lambda roots: roots['metadata'].find('{*}uuid').__setattr__('text', 'different-id'),
                lambda roots: roots['metadata'].find('{*}abstract/{*}list').remove(roots['metadata'].find('{*}abstract/{*}list')[0]),
                lambda roots: roots['recap'].find('{*}list').__setitem__(slice(None), list(reversed(roots['recap'].find('{*}list')))),
                lambda roots: roots['glossary'][1].find('{*}meaning').__setattr__('text', '1, 2, 3.'),
                lambda roots: roots['glossary'][3].find('{*}meaning').__setattr__('text', 'Origin is 1.'),
                lambda roots: roots['recap'].find('{*}figure/{*}media').set('alt', 'No blank cells.'),
                lambda roots: roots['recap'].set('new-attribute', 'unreviewed'),
            ]
            for index, mutate in enumerate(mutations):
                changed = copy.deepcopy(self.tracks[track])
                mutate(changed)
                with self.subTest(track=track, mutation=index), self.assertRaises(AssertionError):
                    summary.validate_components(self.source, changed, track)

    def test_changed_source_and_incomplete_phrase_map_rejected(self):
        changed = copy.deepcopy(self.source)
        changed['glossary'][0].set('id', 'wrong')
        with self.assertRaises(AssertionError):
            summary.variants(changed)
        edits = summary.merged_edits(summary.UNIT)
        edits['phrases'] = [row for row in edits['phrases'] if row[0] != 'Konsep Utama']
        with self.assertRaises(ValueError):
            summary.variants(self.source, edits)
        original = summary.pinned_blob
        def modified(repo, path):
            return original(repo, path) + b'changed'
        with patch.object(summary, 'pinned_blob', modified), self.assertRaises(AssertionError):
            summary.sources()

    def test_coverage_records_components_without_whole_module_claim(self):
        from coverage import component_coverage
        rows = component_coverage()
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(rows[0]['components']), 4)
        self.assertFalse(rows[0]['full_module_complete'])
        self.assertEqual(rows[0]['narration_ssml'], 'three_track_drafts_built')
        self.assertIsNotNone(rows[0]['verified_build'])

    def test_coverage_rejects_changed_component_bytes(self):
        from coverage import component_coverage
        original = Path.read_bytes
        target = LANG / f'translation/{summary.UNIT}.glossary.jv-academic.cnxml'
        def changed(path):
            raw = original(path)
            return raw + b'changed' if path == target else raw
        with patch.object(Path, 'read_bytes', changed), self.assertRaises(ValueError):
            component_coverage()


if __name__ == '__main__':
    unittest.main()
