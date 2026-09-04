"""Fail-closed complete-media and finite-vector tests for m81245."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from config import LANG, TRACKS
import prepare_subtract_assets as assets


class SubtractAssets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generated = assets.products()
        cls.manifest = json.loads(cls.generated[assets.MANIFEST])

    def test_complete_exact_source_scope_and_saved_products(self):
        self.assertEqual(len(self.manifest['assets']), 55)
        self.assertEqual(len(self.generated), 60)
        self.assertEqual(self.generated, assets.products())
        self.assertEqual(self.manifest['scope'], {
            'source_media_occurrences': 55, 'unique_source_refs': 55,
            'unique_source_sha256': 55, 'exact_id_en_byte_matches': 55,
            'retained_nonspeaking_media': 53, 'linguistic_source_rasters': 2,
            'javanese_svg_derivatives': 4, 'stored_source_assets': 55,
            'stored_asset_files_total': 59,
            'actual_source_formats': {'JPEG': 17, 'PNG': 38},
        })
        for path, raw in self.generated.items():
            self.assertEqual((LANG / path).read_bytes(), raw, path)
        self.assertEqual(
            [row['ordinal'] for row in self.manifest['assets']], list(range(1, 56))
        )
        self.assertEqual(
            len({row['media_id'] for row in self.manifest['assets']}), 55
        )
        for row in self.manifest['assets']:
            self.assertTrue(row['id_release_equals_canonical_pin'])
            self.assertEqual(row['source_sha256'], row['canonical_sha256'])
            self.assertEqual(row['source_git_blob_sha1'], row['canonical_git_blob_sha1'])
            self.assertEqual(row['source_bytes'], row['canonical_bytes'])
            source = (LANG / row['outputs']['id-academic']['path']).read_bytes()
            self.assertEqual(assets.sha256(source), row['source_sha256'])
            self.assertEqual(assets.image_info(source)[0], row['actual_mime_type'])
            for track in TRACKS:
                output = row['outputs'][track]
                raw = (LANG / output['path']).read_bytes()
                self.assertEqual((assets.sha256(raw), len(raw)),
                                 (output['sha256'], output['bytes']))

    def test_only_four_registered_svg_derivatives(self):
        rows = self.manifest['assets']
        linguistic = [row for row in rows if row['contains_linguistic_pixels']]
        self.assertEqual([row['media_id'] for row in linguistic], list(assets.LINGUISTIC_IDS))
        for row in rows:
            paths = {track: row['outputs'][track]['path'] for track in TRACKS}
            if row in linguistic:
                self.assertEqual(row['outputs']['id-academic']['mime_type'], 'image/jpeg')
                for track in ('jv-academic', 'jv-conversation'):
                    self.assertEqual(row['outputs'][track]['mime_type'], 'image/svg+xml')
                    self.assertNotEqual(paths[track], paths['id-academic'])
                self.assertEqual(len(row['registered_text_substitutions']), 2)
            else:
                self.assertEqual(len(set(paths.values())), 1)
                self.assertEqual(row['registered_text_substitutions'], [])
                self.assertEqual(len({row['outputs'][track]['sha256'] for track in TRACKS}), 1)

    def test_regrouping_geometry_counts_labels_and_arrow(self):
        row = next(row for row in self.manifest['assets']
                   if row['media_id'] == 'fs-id1376326')
        for track in ('jv-academic', 'jv-conversation'):
            raw = (LANG / row['outputs'][track]['path']).read_bytes()
            assets.verify_vector(raw, row['media_id'], track, row['target_alt'][track])
            root = ET.fromstring(raw)
            nodes = assets._id_map(root)
            self.assertEqual(
                [len(nodes[group]) for group in
                 ('left-tens', 'left-ones', 'right-tens',
                  'right-ones-blue', 'right-ones-red')],
                [40, 3, 30, 3, 10],
            )
            self.assertEqual(
                [nodes[f'label-{n}'].text for n in range(1, 5)],
                ['4 puluhan', '3 satuan', '3 puluhan', '13 satuan'],
            )
            self.assertEqual(nodes['regroup-arrow'].get('d'), 'M260 72 H317')

    def test_self_check_geometry_five_rows_and_fifteen_blanks(self):
        row = next(row for row in self.manifest['assets']
                   if row['media_id'] == 'eip-id1164272051986')
        for track in ('jv-academic', 'jv-conversation'):
            raw = (LANG / row['outputs'][track]['path']).read_bytes()
            assets.verify_vector(raw, row['media_id'], track, row['target_alt'][track])
            root = ET.fromstring(raw)
            nodes = assets._id_map(root)
            self.assertEqual(len(nodes['blank-choice-cells']), 15)
            self.assertEqual(
                [nodes[f'skill-{n}'].text for n in range(1, 6)],
                assets.TARGET_LABELS[row['media_id']][track][4:],
            )
            self.assertEqual(
                [nodes[f'v-{n}'].get('x1') for n in range(1, 4)],
                ['297', '414', '531'],
            )
            self.assertEqual(
                [nodes[f'h-{n}'].get('y1') for n in range(1, 6)],
                ['52', '77', '103', '128', '154'],
            )

    def test_source_vector_and_saved_mutations_fail_closed(self):
        first = self.manifest['assets'][0]
        original_source = assets.source_bytes

        def changed_source(path):
            raw = original_source(path)
            if path == first['canonical_path']:
                return raw + b'changed'
            return raw

        with patch.object(assets, 'source_bytes', changed_source), self.assertRaises(AssertionError):
            assets.products()

        original_canonical = assets.canonical_bytes

        def changed_canonical(archive, path):
            raw = original_canonical(archive, path)
            if path == first['canonical_path']:
                return raw + b'changed'
            return raw

        with patch.object(assets, 'canonical_bytes', changed_canonical), self.assertRaises(AssertionError):
            assets.products()

        vector_row = next(row for row in self.manifest['assets']
                          if row['media_id'] == 'fs-id1376326')
        original = ET.fromstring(
            (LANG / vector_row['outputs']['jv-academic']['path']).read_bytes()
        )
        for node_id, attribute, value in [
            ('label-1', None, '5 puluhan'),
            ('regroup-arrow', 'd', 'M317 72 H260'),
            ('arrowhead', 'orient', 'auto-start-reverse'),
        ]:
            changed = copy.deepcopy(original)
            node = next(node for node in changed.iter() if node.get('id') == node_id)
            if attribute:
                node.set(attribute, value)
            else:
                node.text = value
            with self.subTest(node=node_id), self.assertRaises(AssertionError):
                assets.verify_vector(
                    ET.tostring(changed), vector_row['media_id'], 'jv-academic',
                    vector_row['target_alt']['jv-academic'],
                )

        original_read = Path.read_bytes
        changed_path = LANG / first['outputs']['id-academic']['path']

        def changed_saved(path):
            raw = original_read(path)
            return raw + b'changed' if path == changed_path else raw

        with patch.object(Path, 'read_bytes', changed_saved), self.assertRaises(AssertionError):
            assets.verify_saved(self.generated)

    def test_unknown_derivatives_and_completion_claims_rejected(self):
        for media_id, track in [
            ('unknown', 'jv-academic'),
            ('fs-id1376326', 'id-academic'),
            ('eip-id1164272051986', 'unknown'),
        ]:
            with self.subTest(media=media_id, track=track), self.assertRaises(AssertionError):
                assets.vector(media_id, track, 'alt')
        limits = self.manifest['review_limits']
        self.assertFalse(limits['whole_module_complete'])
        self.assertFalse(limits['full_assignment_complete'])
        self.assertFalse(limits['native_language_review'])
        self.assertFalse(limits['listening_review'])
        self.assertIn('withdrawn', self.manifest['allocation_methodology_note'])

    def test_render_receipts_credits_canon_and_declared_mime(self):
        review = self.manifest['render_review']
        self.assertEqual(review['status'], 'completed')
        self.assertEqual(len(review['outputs']), 4)
        self.assertTrue(all(row['inspected'] for row in review['outputs']))
        self.assertEqual(
            {row['rendered_geometry'] for row in review['outputs']},
            {'626x117', '649x180'},
        )
        self.assertEqual(
            len({row['temporary_png_sha256'] for row in review['outputs']}), 3
        )
        for row in review['outputs']:
            self.assertEqual(assets.sha256(self.generated[row['path']]), row['svg_sha256'])
        credit = self.manifest['credits']['openstax-prealgebra-2e-cc-by-nc-sa-4.0']
        license_raw = assets.git('a00-id', 'show', f'{assets.A00_COMMIT}:LICENSE')
        self.assertEqual(credit['license_sha256'], assets.sha256(license_raw))
        self.assertEqual(credit['license'], 'CC BY-NC-SA 4.0')
        self.assertEqual(self.manifest['canon_checkpoint']['actual_record_count'], 50)
        self.assertEqual(
            self.manifest['canon_checkpoint']['fully_read_for_asset_stage'],
            ['C01', 'C02', 'C03', 'C05', 'C06', 'C37', 'C38', 'C39', 'C48', 'C49', 'C50'],
        )
        jpg_declared = next(row for row in self.manifest['assets']
                            if row['media_id'] == 'eip-id1164272051986')
        self.assertEqual(jpg_declared['source_declared_mime'], 'image/jpg')
        self.assertEqual(jpg_declared['actual_mime_type'], 'image/jpeg')
        self.assertEqual(
            [row['media_id'] for row in self.manifest['known_non_asset_alt_issues']],
            ['fs-id2425624', 'fs-id2643011'],
        )
        self.assertTrue(self.manifest['review_limits']['standalone_derivative_render_review'])
        self.assertFalse(self.manifest['review_limits']['integrated_reader_visual_review'])


if __name__ == '__main__':
    unittest.main()
