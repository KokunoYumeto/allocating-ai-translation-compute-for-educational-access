"""Finite native-vector draft checks; not an integrated visual approval."""
import copy
import json
import unittest
import xml.etree.ElementTree as ET

import prepare_exponent_assets as assets
from config import LANG


class ExponentAssets(unittest.TestCase):
    def test_exact_saved_products_and_per_track_media_types(self):
        generated = assets.products()
        self.assertEqual(generated, assets.products())
        self.assertEqual(len(generated), 7)
        for path, raw in generated.items():
            self.assertEqual((LANG / path).read_bytes(), raw, path)
        manifest = json.loads(generated['translation/a10-exponents.assets.json'])
        for row in manifest['assets']:
            self.assertEqual(row['outputs']['id-academic']['mime_type'], 'image/jpeg')
            for track in ('jv-academic', 'jv-conversation'):
                self.assertEqual(row['outputs'][track]['mime_type'], 'image/svg+xml')
        self.assertEqual([row['source_git_blob'] for row in manifest['assets']],
                         ['ed2cb8bf92e9a4ec9def4c206f288c874a00f12f', 'a2b54ff7ab676ad2a2f99cf93fecc035d8ae4037'])

    def test_actual_formula_geometry_and_mutations(self):
        for key in ('003', '004'):
            raw = assets.vector(key, 'jv-academic', 'Test alt')
            root = ET.fromstring(raw)
            nodes = {node.get('id'): node for node in root.iter() if node.get('id')}
            self.assertEqual(nodes['arrow'].get('orient'), 'auto')
            self.assertLess(float(nodes['power-exponent'].get('y')), float(nodes['power-base'].get('y')))
            self.assertGreater(float(nodes['power-exponent'].get('x')), float(nodes['power-base'].get('x')))
            if key == '004':
                self.assertEqual([x.text for x in nodes['factor-pattern']], ['a', '·', 'a', '·', 'a', '·', '…', '·', 'a'])
            for anchor, attribute, value in [('arrow', 'orient', 'auto-start-reverse'),
                                              ('base-arrow', 'd', 'M214 28 H178'),
                                              ('power-exponent', 'y', '50')]:
                changed = copy.deepcopy(root)
                next(node for node in changed.iter() if node.get('id') == anchor).set(attribute, value)
                with self.assertRaises(AssertionError):
                    assets.verify_vector(ET.tostring(changed), key, 'jv-academic', 'Test alt')

    def test_unknown_case_rejected(self):
        for key, track in [('005', 'jv-academic'), ('003', 'id-academic'), ('004', 'unknown')]:
            with self.assertRaises(AssertionError):
                assets.vector(key, track, 'Test alt')


if __name__ == '__main__':
    unittest.main()
