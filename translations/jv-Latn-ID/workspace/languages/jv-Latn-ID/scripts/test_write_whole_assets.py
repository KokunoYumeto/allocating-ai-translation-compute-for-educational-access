"""Writing-unit SVG-only checks; not full unit or integrated visual approval."""
import json
import unittest
from config import LANG
import prepare_write_whole_assets as assets


class WritingAssets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.products = assets.products()
        cls.manifest = json.loads(cls.products['translation/a00-write-whole.assets.json'])

    def test_saved_products_and_determinism(self):
        self.assertEqual(self.products, assets.products())
        self.assertEqual(len(self.products), 10)
        for path, raw in self.products.items():
            self.assertEqual((LANG / path).read_bytes(), raw, path)

    def test_groups_geometry_and_register_labels(self):
        for row, expected in zip(self.manifest['assets'], [['53', '401', '742'], ['9', '246', '073', '189'], ['77', '000', '000', '000']]):
            variants = {track: self.products[output['path']] for track, output in row['outputs'].items()}
            self.assertEqual(variants['jv-academic'], variants['jv-conversation'])
            for raw in variants.values():
                self.assertEqual(assets.svg_digits(raw), expected)
                self.assertEqual(assets.geometry_signature(raw), assets.geometry_signature(variants['id-academic']))

    def test_unregistered_label_and_numeric_rewrite_fail(self):
        row = self.manifest['assets'][0]
        raw = self.products[row['outputs']['id-academic']['path']]
        changed = dict(row['translation_labels'])
        changed.pop('lima puluh tiga juta')
        with self.assertRaises(AssertionError):
            assets.localize(raw, changed)
        changed = dict(row['translation_labels'])
        changed['Kata-kata menjadi 53,401,742'] = 'Tembung dadi 53,401,743'
        with self.assertRaises(AssertionError):
            assets.localize(raw, changed)


if __name__ == '__main__':
    unittest.main()
