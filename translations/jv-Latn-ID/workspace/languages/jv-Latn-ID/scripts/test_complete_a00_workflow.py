"""Production checks for the complete-source-scope m81243 reader and SSML."""
import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from build import XML_LANG
from build_units import sha
import build_complete_a00_module as build
from complete_a00_checks import (asset_map, checked_assembly, full_blocks,
                                 rounding_editorial_material)
from config import LANG, TRACKS
import draft_complete_a00_module as complete
from qa import Reader


class CompleteA00Workflow(unittest.TestCase):
    def test_all_assets_and_narration_blocks_are_bound_in_source_order(self):
        roots, receipt = checked_assembly()
        self.assertEqual(receipt['source_id_count'], 628)
        for track in TRACKS:
            media, _ = asset_map(track, roots[track])
            self.assertEqual(len(media), 47)
            blocks, _ = full_blocks(track)
            marks = [mark for mark, _ in blocks]
            self.assertEqual(len(marks), len(set(marks)))
            self.assertEqual(len(marks), 183)
            self.assertEqual(marks[0:2], ['m81243--outer-title', 'm81243--para-00001--objectives'])
            self.assertLess(marks.index('m81243--fs-id2472737--title'),
                            marks.index('m81243--fs-id2296006--title'))
            self.assertLess(marks.index('m81243--fs-id2296006--title'),
                            marks.index('m81243--fs-id2318815--title'))
            self.assertEqual(marks[-1], 'm81243--fs-id4338000')

    def test_saved_reader_transcripts_ssml_and_receipt_are_deterministic(self):
        generated = build.products()
        self.assertEqual(generated, build.products())
        for name, raw in generated.items():
            self.assertEqual((LANG / name).read_bytes(), raw, name)
        page = generated[f'review/units/{complete.UNIT}.html'].decode()
        reader = Reader()
        reader.feed(page)
        self.assertEqual(len(reader.ids), 1884)
        self.assertEqual(len(reader.tracks), 33)
        self.assertEqual(reader.maths, 747)
        self.assertEqual(len(reader.images), 141)
        self.assertNotIn('7cbc90c7-60c8-4211-bffe-b77aadc95509', page)
        for track, (locale, _) in TRACKS.items():
            root = ET.fromstring(generated[f'review/audio/{complete.UNIT}.{track}.ssml'])
            self.assertEqual(root.get(XML_LANG), locale)
            marks = [node.get('name') for node in root.findall('{*}mark')]
            self.assertEqual(marks, [mark for mark, _ in full_blocks(track)[0]])
        receipt = json.loads(generated[f'qa/{complete.UNIT}.build-receipt.json'])
        self.assertTrue(receipt['complete_source_scope'])
        self.assertFalse(receipt['whole_module_complete'])
        self.assertEqual(receipt['source_marked_narration_blocks'], 183)
        self.assertEqual(receipt['unmarked_editorial_notices'], {
            'complete_id_reader': 2, 'complete_id_transcript': 1,
            'complete_id_ssml': 1, 'javanese_transcripts_and_ssml': 0,
        })

    def test_reviewed_unmarked_rounding_notices_are_carried_id_only(self):
        notices, dependencies = rounding_editorial_material()
        self.assertEqual(set(dependencies), {
            'qa/a00-rounding.build-receipt.json',
            'review/units/a00-rounding.html',
            'review/audio/a00-rounding.id-academic.md',
            'review/audio/a00-rounding.id-academic.ssml',
        })
        generated = build.products()
        page = generated[f'review/units/{complete.UNIT}.html'].decode()
        self.assertEqual(page.count(notices['indonesian_accessibility_notice']), 1)
        self.assertEqual(page.count(notices['offline_link_notice']), 1)
        for track in TRACKS:
            expected = 1 if track == 'id-academic' else 0
            transcript = generated[f'review/audio/{complete.UNIT}.{track}.md'].decode()
            self.assertEqual(transcript.count(notices['indonesian_accessibility_notice']), expected)
            root = ET.fromstring(generated[f'review/audio/{complete.UNIT}.{track}.ssml'])
            self.assertEqual(sum(''.join(node.itertext()) == notices['indonesian_accessibility_notice']
                                 for node in root.findall('{*}p')), expected)
            self.assertEqual(len(root.findall('{*}mark')), 183)

    def test_changed_audio_asset_or_assembly_dependency_fails_closed(self):
        original = Path.read_bytes
        audio = LANG / 'review/audio/a00-rounding.jv-academic.md'
        def changed_audio(path):
            raw = original(path)
            return raw + b'changed' if path == audio else raw
        with patch.object(Path, 'read_bytes', changed_audio), self.assertRaises(AssertionError):
            full_blocks('jv-academic')

        manifest = json.loads((LANG / 'translation/a00-rounding.assets.json').read_bytes())
        asset = LANG / manifest['assets'][0]['outputs']['id-academic']['path']
        def changed_asset(path):
            raw = original(path)
            return raw + b'changed' if path == asset else raw
        roots, _ = checked_assembly()
        with patch.object(Path, 'read_bytes', changed_asset), self.assertRaises(AssertionError):
            asset_map('id-academic', roots['id-academic'])

        manifest_path = LANG / 'translation/a00-rounding.assets.json'
        def changed_manifest(path):
            raw = original(path)
            return raw + b' ' if path == manifest_path else raw
        with patch.object(Path, 'read_bytes', changed_manifest), self.assertRaises(AssertionError):
            asset_map('id-academic', roots['id-academic'])

        assembly = LANG / f'qa/{complete.UNIT}.assembly-receipt.json'
        def changed_assembly(path):
            raw = original(path)
            return raw + b'changed' if path == assembly else raw
        with patch.object(Path, 'read_bytes', changed_assembly), self.assertRaises(AssertionError):
            checked_assembly()

        bounded_reader = LANG / 'review/units/a00-rounding.html'
        def changed_editorial_reader(path):
            raw = original(path)
            return raw.replace(b'Pranala luar asli', b'Pranala njaba asli', 1) if path == bounded_reader else raw
        with patch.object(Path, 'read_bytes', changed_editorial_reader), self.assertRaises(AssertionError):
            rounding_editorial_material()

        receipt_path = LANG / 'qa/a00-rounding.build-receipt.json'
        receipt = json.loads(original(receipt_path))
        changed_reader_raw = original(bounded_reader) + b'<!-- coherently receipted mutation -->'
        receipt['output_sha256']['review/units/a00-rounding.html'] = sha(changed_reader_raw)
        changed_receipt_raw = (json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode()
        def coherent_receipt_and_reader(path):
            if path == receipt_path:
                return changed_receipt_raw
            if path == bounded_reader:
                return changed_reader_raw
            return original(path)
        with patch.object(Path, 'read_bytes', coherent_receipt_and_reader), self.assertRaises(AssertionError):
            rounding_editorial_material()

    def test_coverage_records_candidate_without_advancing_module_count(self):
        from coverage import complete_module_candidate_coverage
        rows = complete_module_candidate_coverage()
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]['complete_source_scope'])
        self.assertFalse(rows[0]['whole_module_complete'])
        self.assertEqual(rows[0]['unmarked_editorial_notices']['complete_id_ssml'], 1)
        self.assertEqual(rows[0]['unmarked_editorial_notices']['javanese_transcripts_and_ssml'], 0)
        self.assertEqual(rows[0]['producer_pre_review_state'], 'pending')
        self.assertEqual(rows[0]['independent_cross_component_review']['status'], 'passed')
        self.assertEqual(rows[0]['effect_on_baseline_module_counts'],
                         'none_pending_human_and_integrated_accessibility_review')

    def test_coverage_rejects_coherent_unreviewed_build_receipt_mutation(self):
        from coverage import complete_module_candidate_coverage
        original = Path.read_bytes
        receipt_name = f'qa/{complete.UNIT}.build-receipt.json'
        receipt_path = LANG / receipt_name
        generated = build.products()
        receipt = json.loads(generated[receipt_name])
        receipt['coherent_unreviewed_mutation_probe'] = True
        changed_receipt = (json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode()
        changed_products = dict(generated)
        changed_products[receipt_name] = changed_receipt

        def changed_saved_receipt(path):
            return changed_receipt if path == receipt_path else original(path)

        with patch.object(build, 'products', return_value=changed_products), \
                patch.object(Path, 'read_bytes', changed_saved_receipt), \
                self.assertRaisesRegex(ValueError, 'independently reviewed bytes'):
            complete_module_candidate_coverage()


if __name__ == '__main__':
    unittest.main()
