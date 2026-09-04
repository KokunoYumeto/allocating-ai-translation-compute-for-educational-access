"""Fail-closed source, derivative and accessibility tests for m81268 assets."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from config import LANG, TRACKS
import prepare_use_algebra_assets as assets


class UseAlgebraAssets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generated = assets.products()
        cls.manifest = json.loads(cls.generated[assets.MANIFEST])
        cls.by_id = {row['media_id']: row for row in cls.manifest['assets']}
        source_raw, _ = assets.pinned_repo_blob(
            'a00-id', assets.A00_COMMIT, assets.SOURCE_MODULE_PATH)
        english_raw, _ = assets.pinned_repo_blob(
            'openstax-prealgebra-bundle', assets.UPSTREAM_COMMIT,
            assets.SOURCE_MODULE_PATH)
        cls.source_root = ET.fromstring(source_raw)
        cls.english_root = ET.fromstring(english_raw)

    def test_complete_deterministic_saved_scope(self):
        self.assertEqual(self.generated, assets.products())
        self.assertEqual(len(self.generated), 55)
        self.assertEqual(len(self.manifest['assets']), 44)
        self.assertEqual(self.manifest['scope'], {
            'source_media_occurrences': 44, 'canonical_media_occurrences': 44,
            'source_unique_ids': 44, 'source_unique_refs': 44,
            'exact_id_en_byte_matches': 39, 'inherited_id_localizations': 5,
            'retained_source_assets': 44, 'javanese_svg_derivatives': 10,
            'stored_asset_files_total': 54, 'scoped_accessibility_corrections': 7,
            'source_formats': {'JPEG': 4, 'PNG': 36, 'SVG': 4},
            'canonical_formats': {'JPEG': 9, 'PNG': 35, 'SVG': 0},
        })
        self.assertEqual(
            [row['ordinal'] for row in self.manifest['assets']], list(range(1, 45)))
        self.assertEqual(len(self.by_id), 44)
        self.assertEqual(
            len({row['source']['ref'] for row in self.manifest['assets']}), 44)
        self.assertEqual(
            len({row['outputs'][track]['path']
                 for row in self.manifest['assets'] for track in TRACKS}), 54)
        self.assertLess(sum(map(len, self.generated.values())), 2_000_000)
        for path, raw in self.generated.items():
            self.assertEqual((LANG / path).read_bytes(), raw, path)

    def test_all_source_and_canonical_bytes_and_effective_xml_are_bound(self):
        source_media = assets.media_nodes(self.source_root)
        english_media = assets.media_nodes(self.english_root)
        self.assertEqual(
            [node.get('id') for node in source_media],
            [node.get('id') for node in english_media])
        identical = 0
        for record, source_node, english_node in zip(
                self.manifest['assets'], source_media, english_media):
            with self.subTest(media=record['media_id']):
                self.assertEqual(record['media_id'], source_node.get('id'))
                self.assertEqual(record['source_effective_xml'], assets.c14n(source_node))
                self.assertEqual(record['canonical_effective_xml'], assets.c14n(english_node))
                self.assertEqual(
                    record['source_effective_xml_c14n_sha256'],
                    assets.utf8_sha(record['source_effective_xml']))
                self.assertEqual(
                    record['canonical_effective_xml_c14n_sha256'],
                    assets.utf8_sha(record['canonical_effective_xml']))
                source_raw, source_oid = assets.pinned_repo_blob(
                    'a00-id', assets.A00_COMMIT, record['source']['path'])
                english_raw, english_oid = assets.pinned_repo_blob(
                    'openstax-prealgebra-bundle', assets.UPSTREAM_COMMIT,
                    record['canonical_english']['path'])
                self.assertEqual(source_oid, record['source']['git_blob_sha1'])
                self.assertEqual(english_oid, record['canonical_english']['git_blob_sha1'])
                self.assertEqual(
                    (assets.sha256(source_raw), len(source_raw), assets.image_info(source_raw)[0]),
                    (record['source']['sha256'], record['source']['bytes'],
                     record['source']['actual_mime_type']))
                self.assertEqual(
                    (assets.sha256(english_raw), len(english_raw), assets.image_info(english_raw)[0]),
                    (record['canonical_english']['sha256'],
                     record['canonical_english']['bytes'],
                     record['canonical_english']['actual_mime_type']))
                equal = source_raw == english_raw
                self.assertEqual(equal, record['id_source_equals_canonical_english_bytes'])
                identical += equal
        self.assertEqual(identical, 39)
        self.assertEqual(
            self.manifest['prior_handoff_nine_field_media_digest_sha256'],
            assets.PRIOR_NINE_FIELD_MEDIA_DIGEST)

    def test_only_five_sources_receive_ten_registered_derivatives(self):
        localized = [row for row in self.manifest['assets']
                     if row['contains_linguistic_pixels']]
        self.assertEqual([row['media_id'] for row in localized], list(assets.LOCALIZED_IDS))
        self.assertEqual(len(localized) * 2, 10)
        for record in self.manifest['assets']:
            paths = {track: record['outputs'][track]['path'] for track in TRACKS}
            hashes = {track: record['outputs'][track]['sha256'] for track in TRACKS}
            source_raw = self.generated[paths['id-academic']]
            self.assertEqual(assets.sha256(source_raw), record['source']['sha256'])
            if record['media_id'] in assets.LOCALIZED_IDS:
                self.assertEqual(len(record['registered_substitutions']), 2)
                self.assertFalse(record['id_source_equals_canonical_english_bytes'])
                self.assertFalse(
                    record['untranslated_visible_source_language_after_target_derivative'])
                for track in ('jv-academic', 'jv-conversation'):
                    self.assertNotEqual(paths[track], paths['id-academic'])
                    self.assertEqual(record['outputs'][track]['mime_type'], 'image/svg+xml')
                    raw = self.generated[paths[track]]
                    self.assertEqual(assets.sha256(raw), hashes[track])
                    if record['media_id'] == 'fs-id1495317':
                        assets.verify_fuel_wrapper(
                            raw, source_raw, track, record['target_alt'][track])
                    else:
                        assets.verify_localized_svg(
                            raw, source_raw, record['media_id'], track)
            else:
                self.assertEqual(len(set(paths.values())), 1)
                self.assertEqual(len(set(hashes.values())), 1)
                self.assertEqual(record['registered_substitutions'], [])
                self.assertIsNone(
                    record['untranslated_visible_source_language_after_target_derivative'])

    def test_svg_geometry_math_ids_and_fuel_pixels_are_preserved(self):
        fuel = self.by_id['fs-id1495317']
        fuel_source = self.generated[fuel['outputs']['id-academic']['path']]
        for track in ('jv-academic', 'jv-conversation'):
            raw = self.generated[fuel['outputs'][track]['path']]
            root = ET.fromstring(raw)
            by_id = {node.get('id'): node for node in root.iter() if node.get('id')}
            href = by_id['source-raster'].get('href')
            encoded = href.removeprefix('data:image/png;base64,')
            import base64
            self.assertEqual(base64.b64decode(encoded), fuel_source)
            self.assertEqual(
                [(by_id[name].get('x'), by_id[name].get('width'))
                 for name in ('top-label-cover', 'bottom-label-cover')],
                [('1', '107'), ('1', '107')])
            self.assertEqual(
                [by_id['top-label'].text, by_id['bottom-label-1'].text,
                 by_id['bottom-label-2'].text], assets.FUEL_LABELS[track])
        for media_id in assets.LOCALIZED_IDS[1:]:
            record = self.by_id[media_id]
            source_raw = self.generated[record['outputs']['id-academic']['path']]
            source_root = ET.fromstring(source_raw)
            source_ids = [node.get('id') for node in source_root.iter()]
            source_invariants = [row for row in assets.svg_text_entries(source_root)
                                 if row[2] in assets.INVARIANT_SVG_TEXT[media_id]]
            for track in ('jv-academic', 'jv-conversation'):
                target_root = ET.fromstring(
                    self.generated[record['outputs'][track]['path']])
                self.assertEqual(assets.geometry_signature(source_root),
                                 assets.geometry_signature(target_root))
                self.assertEqual(source_ids, [node.get('id') for node in target_root.iter()])
                self.assertEqual(target_root.get(assets.XML_LANG), 'jv-Latn-ID')
                target_invariants = [row for row in assets.svg_text_entries(target_root)
                                     if row[2] in assets.INVARIANT_SVG_TEXT[media_id]]
                self.assertEqual(source_invariants, target_invariants)

    def test_seven_repairs_are_exactly_scoped_and_restore_only_declared_facts(self):
        corrections = self.manifest['scoped_accessibility_corrections']
        expected = [(row[1], row[3]) for row in assets.CORRECTION_SPECS]
        self.assertEqual([(row['element_id'], row['slot']) for row in corrections], expected)
        self.assertEqual(len(corrections), 7)
        edit_data = json.loads((LANG / assets.EDITS).read_bytes())
        for correction in corrections:
            with self.subTest(element=correction['element_id']):
                node = assets.find_id(
                    self.source_root, correction['element_id'], correction['element'])
                self.assertEqual(node.get(correction['slot']),
                                 correction['old_source_surface'])
                self.assertEqual(assets.c14n(node), correction['source_element_c14n'])
                self.assertEqual(
                    correction['source_element_c14n_sha256'],
                    assets.utf8_sha(correction['source_element_c14n']))
                self.assertEqual(correction['source_module_sha256'],
                                 assets.SOURCE_MODULE_SHA256)
                if correction['scope_hash_kind'] == 'asset-sha256':
                    self.assertEqual(correction['scope_hash'],
                                     self.by_id[correction['element_id']]['source']['sha256'])
                    self.assertEqual(correction['asset_sha256'], correction['scope_hash'])
                else:
                    self.assertEqual(correction['scope_hash'],
                                     correction['source_element_c14n_sha256'])
                    self.assertIsNone(correction['asset_sha256'])
                self.assertEqual(
                    correction['old_source_surface'],
                    edit_data['phrases'][correction['phrase_index_zero_based']][0])
        exponent = next(row for row in corrections
                        if row['element_id'] == 'eip-id1164754514704')
        self.assertNotIn('Eksponen? Tidak.', exponent['old_source_surface'])
        self.assertTrue(all('Apa ana eksponen? ora.' in value
                            for value in exponent['target_surfaces'].values()))
        fuel = next(row for row in corrections if row['element_id'] == 'fs-id1495317')
        self.assertTrue(all('ora ana aksara variabel' in value
                            for value in fuel['target_surfaces'].values()))
        mountain = next(row for row in corrections if row['element_id'] == 'fs-id2935762')
        self.assertTrue(all('Mt. Massive' in value and '14,269 foot' in value
                            for value in mountain['target_surfaces'].values()))

    def test_mutated_source_text_geometry_math_and_bindings_fail_closed(self):
        media_id = 'fs-id2149605'
        record = self.by_id[media_id]
        source_raw = self.generated[record['outputs']['id-academic']['path']]
        changed_text = source_raw.replace(b'>basis<', b'>basisX<', 1)
        with self.assertRaises(ValueError):
            assets.localize_source_svg(changed_text, media_id, 'jv-academic')

        target_raw = self.generated[record['outputs']['jv-academic']['path']]
        changed_geometry = target_raw.replace(b'x1="46"', b'x1="47"', 1)
        with self.assertRaises(ValueError):
            assets.verify_localized_svg(
                changed_geometry, source_raw, media_id, 'jv-academic')
        changed_math = target_raw.replace(b'>2<', b'>4<', 1)
        with self.assertRaises(ValueError):
            assets.verify_localized_svg(changed_math, source_raw, media_id, 'jv-academic')

        fuel = self.by_id['fs-id1495317']
        fuel_source = self.generated[fuel['outputs']['id-academic']['path']]
        with self.assertRaises(ValueError):
            assets.fuel_wrapper(fuel_source + b'changed', 'jv-academic', 'alt')

        changed_root = copy.deepcopy(self.source_root)
        node = assets.find_id(changed_root, 'fs-id2757058', 'table')
        node.set('aria-label', node.get('aria-label') + ' changed')
        edits = json.loads((LANG / assets.EDITS).read_bytes())
        with self.assertRaises(ValueError):
            assets.validate_correction_bindings(
                changed_root, edits, self.manifest['assets'])

        original_git = assets.git
        source_path = record['source']['path']

        def changed_git(repo, *args):
            raw = original_git(repo, *args)
            if repo == 'a00-id' and args == (
                    'show', f'{assets.A00_COMMIT}:{source_path}'):
                return raw + b'changed'
            return raw

        with patch.object(assets, 'git', changed_git), self.assertRaises(ValueError):
            assets.pinned_repo_blob('a00-id', assets.A00_COMMIT, source_path)

    def test_saved_mutation_is_rejected(self):
        first_path = next(iter(self.generated))
        target = LANG / first_path
        original_read = Path.read_bytes

        def changed_read(path):
            raw = original_read(path)
            return raw + b'changed' if path == target else raw

        with patch.object(Path, 'read_bytes', changed_read), self.assertRaises(ValueError):
            assets.verify_saved(self.generated)

    def test_render_receipts_credit_methodology_and_completion_limits(self):
        review = self.manifest['render_review']
        self.assertEqual(review['status'], 'completed')
        self.assertEqual(len(review['outputs']), 10)
        self.assertTrue(all(row['inspected'] for row in review['outputs']))
        self.assertEqual(
            {row['rendered_geometry'] for row in review['outputs']},
            {'632x117', '220x26', '224x104', '221x100', '632x172'})
        for row in review['outputs']:
            self.assertEqual(assets.sha256(self.generated[row['path']]),
                             row['svg_sha256'])
        credit = self.manifest['credits']['openstax-prealgebra-2e-cc-by-nc-sa-4.0']
        license_raw, license_oid = assets.pinned_repo_blob(
            'a00-id', assets.A00_COMMIT, 'LICENSE')
        self.assertEqual(credit['license_sha256'], assets.sha256(license_raw))
        self.assertEqual(credit['license_git_blob_sha1'], license_oid)
        self.assertEqual(credit['license'], 'CC BY-NC-SA 4.0')
        limits = self.manifest['methodology_limits']
        self.assertIn('withdrawn', limits['withdrawn_global_ranking'])
        self.assertIn('candidate integration only', limits['candidate_backend'])
        self.assertFalse(limits['source_replacement_performed'])
        review_limits = self.manifest['review_limits']
        self.assertTrue(review_limits['standalone_derivative_render_review'])
        self.assertFalse(review_limits['integrated_reader_visual_review'])
        self.assertFalse(review_limits['native_language_review'])
        self.assertFalse(review_limits['full_assignment_complete'])


if __name__ == '__main__':
    unittest.main()
