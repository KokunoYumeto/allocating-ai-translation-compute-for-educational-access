"""Source identity, geometry, logical-label and blank-matrix asset checks."""
import json
import unittest
from unittest.mock import patch
from pathlib import Path
from config import LANG
from prepare_digit_place_assets import geometry_signature, sha256, text_nodes
import prepare_section_exercise_assets as assets


class SectionExerciseAssets(unittest.TestCase):
    def test_saved_products_and_all_source_bindings(self):
        generated = assets.products()
        self.assertEqual(generated, assets.products())
        self.assertEqual(len(generated), 8)
        for name, raw in generated.items():
            self.assertEqual((LANG / name).read_bytes(), raw, name)
        manifest = json.loads(generated[f'translation/{assets.UNIT}.assets.json'])
        self.assertEqual(len(manifest['assets']), 5)
        self.assertEqual([row['block_counts'] for row in manifest['assets'][:4]], [
            {'hundreds':5,'tens':6,'ones':1}, {'hundreds':3,'tens':8,'ones':4},
            {'hundreds':4,'tens':0,'ones':7}, {'hundreds':6,'tens':2,'ones':0}])
        self.assertTrue(all(len(set(o['sha256'] for o in row['outputs'].values())) == 1
                            for row in manifest['assets'][:4]))

    def test_self_check_geometry_labels_and_empty_matrix(self):
        manifest = json.loads((LANG/f'translation/{assets.UNIT}.assets.json').read_bytes())
        row = manifest['assets'][-1]
        source = (LANG/row['outputs']['id-academic']['path']).read_bytes()
        rules = json.loads((LANG/f'audio/{assets.UNIT}.rules.json').read_bytes())
        chart = rules['chart_fixtures'][-1]
        for track in ('jv-academic','jv-conversation'):
            target = (LANG/row['outputs'][track]['path']).read_bytes()
            self.assertEqual(geometry_signature(source), geometry_signature(target))
            values = [n.text for n in text_nodes(target)]
            self.assertEqual(values, assets.SVG_TEXT[track])
            self.assertEqual(values[3], chart['choice_labels'][track][0])
            self.assertEqual(' '.join(values[4:6]), chart['choice_labels'][track][1])
            self.assertEqual(' '.join((values[6],values[7],values[8])), chart['choice_labels'][track][2])
        self.assertEqual(row['logical_shape']['empty_choice_cells'], 18)
        self.assertEqual(row['logical_shape']['preselected_choices'], 0)

    def test_changed_source_or_saved_payload_fails(self):
        original = assets.pinned_blob
        def changed(repo,commit,path,oid):
            raw = original(repo,commit,path,oid)
            return raw+b'changed' if path.endswith(assets.SVG_NAME) else raw
        with patch.object(assets,'pinned_blob',changed),self.assertRaises(AssertionError):
            assets.products()
        original_read = Path.read_bytes
        target = LANG/assets.OUT/assets.SVG_NAME.replace('.id-ID.svg','.jv-academic.svg')
        def altered(path):
            raw=original_read(path)
            return raw+b'changed' if path==target else raw
        generated=assets.products()
        with patch.object(Path,'read_bytes',altered),self.assertRaises(AssertionError):
            assets.verify_saved(generated)


if __name__ == '__main__':
    unittest.main()
