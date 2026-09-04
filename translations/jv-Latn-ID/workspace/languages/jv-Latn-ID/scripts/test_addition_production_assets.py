import copy
import json
import unittest
import xml.etree.ElementTree as ET

from build import XML_LANG
from config import LANG, TRACKS
import draft_addition_production as draft
import prepare_addition_production_assets as assets


class AdditionProductionAssets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generated = assets.products()
        cls.manifest = json.loads(cls.generated[assets.MANIFEST])

    def test_products_are_saved_and_deterministic(self):
        assets.verify_saved(self.generated)
        self.assertEqual(self.generated, assets.products())
        self.assertEqual(len(self.generated), 65)

    def test_exact_asset_and_format_census(self):
        scope = self.manifest['scope']
        self.assertEqual(scope['source_formats'], {'JPEG': 26, 'PNG': 17, 'SVG': 7})
        self.assertEqual((scope['source_media'], scope['retained_source_assets'],
                          scope['javanese_svg_derivatives'], scope['stored_asset_files_total']),
                         (50, 50, 14, 64))
        self.assertEqual(len(self.manifest['assets']), 50)
        outputs = {row['outputs']['id-academic']['path'] for row in self.manifest['assets']}
        self.assertEqual(len(outputs), 50)
        for row in self.manifest['assets']:
            source_raw = (LANG / row['outputs']['id-academic']['path']).read_bytes()
            self.assertEqual(assets.sha(source_raw), row['source']['sha256'])
            for track in TRACKS:
                output = row['outputs'][track]
                raw = (LANG / output['path']).read_bytes()
                self.assertEqual((assets.sha(raw), len(raw)),
                                 (output['sha256'], output['bytes']))

    def test_svg_derivatives_change_only_registered_text_and_locale(self):
        rows = [row for row in self.manifest['assets'] if row['source']['format'] == 'SVG']
        self.assertEqual(len(rows), 7)
        for row in rows:
            source_raw = (LANG / row['outputs']['id-academic']['path']).read_bytes()
            before = assets.geometry_signature(source_raw)
            for track in ('jv-academic', 'jv-conversation'):
                raw = (LANG / row['outputs'][track]['path']).read_bytes()
                self.assertEqual(before, assets.geometry_signature(raw))
                self.assertEqual(ET.fromstring(raw).get(XML_LANG), 'jv-Latn-ID')
                occurrences = row['registered_substitutions'][
                    0 if track == 'jv-academic' else 1]['occurrences']
                self.assertEqual([node.text for node in assets.text_nodes(raw)],
                                 [item['target'] for item in occurrences])

    def test_only_scoped_222_alt_fact_is_corrected(self):
        exception = self.manifest['numeric_alt_exception']
        self.assertEqual(exception['element_id'], 'fs-id2263429')
        self.assertEqual(exception['attribute'], 'alt')
        self.assertEqual(exception['source_asset_sha256'], draft.CORRECTED_ASSET_SHA256)
        self.assertFalse(exception['generic_bypass'])
        corrected = next(row for row in self.manifest['assets']
                         if row['media_id'] == 'fs-id2263429')
        self.assertEqual(corrected['source_alt'], exception['exact_old_source_surface'])
        self.assertIn('5 kolom lan 8 baris', corrected['target_alt']['jv-academic'])
        self.assertEqual(corrected['outputs']['id-academic']['sha256'],
                         draft.CORRECTED_ASSET_SHA256)


if __name__ == '__main__':
    unittest.main()
