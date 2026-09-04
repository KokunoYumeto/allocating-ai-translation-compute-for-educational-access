"""Regression tests for the evaluation unit's exact media provenance."""
import base64
import json
import unittest
import xml.etree.ElementTree as ET

from config import LANG
from evaluation_checks import ASSETS_SHA256, OVERRIDES, TRACKS, load_rules, sha, validate_assets
from prepare_evaluation_assets import products


class EvaluationAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules, _ = load_rules()
        cls.manifest, cls.media = validate_assets(cls.rules)
        cls.assets = {row['fixture_id']: row for row in cls.manifest['assets']}

    def test_products_are_deterministic_and_saved(self):
        first = products()
        self.assertEqual(first, products())
        for path, raw in first.items():
            self.assertEqual((LANG / path).read_bytes(), raw, path)
        self.assertEqual(sha((LANG / 'translation/a10-evaluate-expressions.assets.json').read_bytes()),
                         ASSETS_SHA256)
        self.assertEqual(len(first), 27)  # 16 JPEGs + 10 SVGs + manifest.

    def test_truthful_mime_and_exact_labels(self):
        svg_count = 0
        for asset in self.assets.values():
            for track in TRACKS:
                output = asset['outputs'][track]
                raw = self.media[track][asset['source_src']]['bytes']
                if output['mime_type'] == 'image/jpeg':
                    self.assertTrue(raw.startswith(b'\xff\xd8\xff'))
                else:
                    svg_count += 1
                    root = ET.fromstring(raw)
                    labels = [''.join(node.itertext()) for node in root.iter()
                              if node.tag.endswith('}text')]
                    chart = next(row for row in self.rules['chart_fixtures']
                                 if row['id'] == asset['fixture_id'])
                    self.assertIn(chart['expected_jv_visible_labels'][track], labels)
        self.assertEqual(svg_count, 10)

    def test_indonesian_overrides_are_not_canonical_regressions(self):
        for fixture_id, expected in OVERRIDES.items():
            asset = self.assets[fixture_id]
            self.assertEqual(asset['effective_source']['sha256'], expected['effective'])
            self.assertEqual(asset['canonical_authority']['sha256'], expected['canonical'])
            self.assertNotEqual(expected['effective'], expected['canonical'])
            self.assertTrue(asset['indonesian_release_override']['present'])
            for track in TRACKS:
                raw = self.media[track][asset['source_src']]['bytes']
                self.assertEqual(sha(raw), expected['effective'])
                self.assertNotEqual(sha(raw), expected['canonical'])

    def test_outputs_are_not_data_url_placeholders(self):
        for asset in self.assets.values():
            for track in TRACKS:
                raw = self.media[track][asset['source_src']]['bytes']
                self.assertGreater(len(base64.b64encode(raw)), 20)
                self.assertNotIn(b'data:image/', raw[:64])


if __name__ == '__main__':
    unittest.main()
