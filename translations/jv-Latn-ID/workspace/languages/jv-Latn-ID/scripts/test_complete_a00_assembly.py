"""Structural tests for the complete-source-scope m81243 assembly."""
import copy
import json
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

from build import MATH, XML_LANG
from build_units import tree_key
from config import LANG, TRACKS
import draft_complete_a00_module as complete


class CompleteA00Assembly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.id_raw, cls.en_raw = complete.source_modules()
        cls.source = ET.fromstring(cls.id_raw)

    def test_complete_exact_scope_counts_and_order(self):
        self.assertEqual([node.get('id') for node in self.source[2]],
                         [anchor for anchor, _ in complete.SECTION_UNITS])
        self.assertEqual(len([node for node in self.source.iter() if node.get('id')]), 628)
        self.assertEqual(len(list(self.source.iter('{' + MATH + '}math'))), 249)
        self.assertEqual(len(list(self.source.iter('{http://cnx.rice.edu/cnxml}media'))), 47)
        self.assertEqual(len(list(self.source.iter('{http://cnx.rice.edu/cnxml}exercise'))), 88)
        self.assertEqual(len(list(self.source.iter('{http://cnx.rice.edu/cnxml}solution'))), 59)
        self.assertEqual(len(list(self.source.iter('{http://cnx.rice.edu/cnxml}definition'))), 7)

    def test_all_tracks_are_exact_component_assemblies(self):
        for track in TRACKS:
            target = complete.assemble(self.source, track)
            self.assertEqual(complete.validate(self.source, target, track),
                             [node.get('id') for node in self.source.iter() if node.get('id')])
            if track == 'id-academic':
                self.assertEqual(tree_key(target), tree_key(self.source))
            else:
                self.assertEqual(target.get(XML_LANG), 'jv-Latn-ID')

    def test_saved_products_and_receipt_are_deterministic(self):
        generated = complete.products()
        self.assertEqual(generated, complete.products())
        for name, raw in generated.items():
            self.assertEqual((LANG / name).read_bytes(), raw, name)
        receipt = json.loads(generated[f'qa/{complete.UNIT}.assembly-receipt.json'])
        self.assertTrue(receipt['complete_source_scope'])
        self.assertFalse(receipt['whole_module_complete'])
        self.assertEqual(receipt['source_id_count'], 628)
        self.assertEqual(len(receipt['verified_dependency_sha256']), 33)

    def test_changed_source_or_component_fails_closed(self):
        original = complete.draft_summary.pinned_blob
        def changed(repo, path):
            raw = original(repo, path)
            return raw + b'changed' if path.endswith('m81243/index.cnxml') else raw
        with patch.object(complete.draft_summary, 'pinned_blob', changed), self.assertRaises(AssertionError):
            complete.products()
        target = complete.assemble(self.source, 'jv-academic')
        target[2][3][0].text = 'changed'
        with self.assertRaises(AssertionError):
            complete.validate(self.source, target, 'jv-academic')


if __name__ == '__main__':
    unittest.main()
