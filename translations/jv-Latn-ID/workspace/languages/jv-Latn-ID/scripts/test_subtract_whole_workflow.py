"""Focused fail-closed production tests for complete m81245 subtraction."""
import base64
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import build as shared_build
from build import MATH, XML_LANG, translated
from draft_units import merged_edits
from config import LANG, TRACKS
import build_subtract_whole as builder
import draft_subtract_whole as draft
from qa import Reader
import subtract_whole_checks as checks


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def by_id(root, node_id):
    return next(node for node in root.iter() if node.get('id') == node_id)


def transcript_blocks(raw):
    result = []
    for chunk in raw.decode().split('\n## ')[1:]:
        key, body = chunk.split('\n\n', 1)
        key = key.removeprefix('m81245--')
        result.append((key, body.rstrip('\n')))
    return result


class SubtractWholeWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.draft_products = draft.products()
        cls.bound = checks.bind()
        cls.build_products = builder.products()
        cls.rules = cls.bound.rules
        cls.assets = cls.bound.assets
        cls.build_receipt = json.loads(
            cls.build_products[f'qa/{draft.UNIT}.in-progress.json'])

    def test_complete_pinned_source_provenance_and_finite_inventory(self):
        id_raw, en_raw = draft.source_blobs()
        self.assertEqual(sha(id_raw),
                         'd6829f9326dfcb9d30e589b2917bbc18ab2c871b0f44b939b1ceeb477ec8fe3f')
        self.assertEqual(sha(en_raw),
                         '02df262b21ee15472223ae863bc5f3bcb3714389a8ef46e66c8b4469c6972841')
        serialized_id = (ET.tostring(ET.fromstring(id_raw), encoding='utf-8',
                                     xml_declaration=True) + b'\n')
        serialized_en = (ET.tostring(ET.fromstring(en_raw), encoding='utf-8',
                                     xml_declaration=True) + b'\n')
        self.assertEqual(
            self.draft_products['translation/a00-subtract-whole.id-academic.cnxml'],
            serialized_id)
        self.assertEqual(
            self.draft_products['provenance/a00-subtract-whole.en.cnxml'],
            serialized_en)

        source = self.bound.source
        source_ids = [node.get('id') for node in source.iter() if node.get('id')]
        self.assertEqual(len(source_ids), len(set(source_ids)))
        self.assertEqual(source_ids,
                         [row['id'] for row in self.rules['source_id_identity']])
        self.assertEqual(
            [node.get('id') for node in self.bound.english.iter() if node.get('id')],
            source_ids)
        for root in self.bound.variants.values():
            self.assertEqual(
                [node.get('id') for node in root.iter() if node.get('id')],
                source_ids)
        self.assertEqual(
            (len(source_ids), len(list(source.iter('{' + MATH + '}math'))),
             len(source.findall('.//{*}media')), len(source.findall('.//{*}table')),
             len(source.findall('.//{*}exercise')),
             len(source.findall('.//{*}solution')), len(source.findall('.//{*}link'))),
            (716, 262, 55, 17, 125, 83, 6))
        self.assertEqual(len(self.bound.phrases), 503)
        self.assertEqual(len(self.rules['phrase_fixtures']), 336)
        self.assertEqual(len(self.bound.math), 262)
        self.assertEqual(len(self.bound.tables), 17)
        self.assertEqual(len(self.bound.charts), 55)
        self.assertEqual(len(self.bound.references), 6)
        self.assertEqual(len(self.bound.utterances), 263)
        self.assertEqual(len(self.bound.exercises), 125)
        linguistic_differences = []
        for row in self.rules['math_fixtures']:
            source_math = checks.at(source, row['source_path'])
            english_math = checks.at(self.bound.english, row['source_path'])
            source_tokens = [node.text or '' for node in source_math.iter()
                             if node.tag == '{' + MATH + '}mtext']
            english_tokens = [node.text or '' for node in english_math.iter()
                              if node.tag == '{' + MATH + '}mtext']
            for left, right in zip(source_tokens, english_tokens):
                if left != right:
                    linguistic_differences.append((row['ordinal'], left, right))
        self.assertEqual(linguistic_differences, [
            (18, 'basis-10', 'base-10'),
            (52, 'karena', 'because'),
            (52, 'karena', 'because'),
            (52, 'karena', 'because'),
            (133, 'Juni', 'June'),
            (133, '', 'st'),
            (262, 'dan', 'and'),
        ])

    def test_narrow_alt_repairs_change_only_two_javanese_attributes(self):
        contract = draft.correction_contract(self.rules, self.assets)
        self.assertEqual([row['media_id'] for row in contract],
                         ['fs-id2425624', 'fs-id2643011'])
        expected_hashes = {
            'fs-id2425624':
                '5946124a1470c7aa9c4f6edda62c2e0ae0d83e2aeecaab6f65a1ef81054de628',
            'fs-id2643011':
                'ddd74c6d17086f66c2fb9d2f508bdb230e476557fa5b3a082ede509ea5d94871',
        }
        expected_refs = {
            'fs-id2425624': '../../media/CNX_BMath_Figure_01_03_016_img.jpg',
            'fs-id2643011': '../../media/CNX_BMath_Figure_01_03_017_img.jpg',
        }
        self.assertEqual({row['media_id']: row['image_sha256'] for row in contract},
                         expected_hashes)
        self.assertEqual({row['media_id']: row['source_ref'] for row in contract},
                         expected_refs)

        source = self.bound.source
        edits = merged_edits(draft.UNIT)
        for track in ('jv-academic', 'jv-conversation'):
            base = translated(source, track, edits)
            actual = self.bound.variants[track]
            differences = []
            for before, after in zip(base.iter(), actual.iter()):
                self.assertEqual((before.tag, before.text, before.tail),
                                 (after.tag, after.text, after.tail))
                for name in sorted(set(before.attrib) | set(after.attrib)):
                    if before.get(name) != after.get(name):
                        differences.append((before.get('id'), name,
                                            before.get(name), after.get(name)))
            self.assertEqual(
                [(row[0], row[1]) for row in differences],
                [('fs-id2425624', 'alt'), ('fs-id2643011', 'alt')])
            for row in contract:
                node = by_id(actual, row['media_id'])
                self.assertEqual(node.get('alt'), row['corrected_target_alt'][track])
                self.assertEqual(by_id(base, row['media_id']).get('alt'),
                                 row['old_target_alt'][track])
                self.assertEqual(
                    self.bound.charts[tuple(row['source_path'])]
                    ['independent_expected_reading'][track],
                    row['corrected_target_alt'][track])
        for row in contract:
            self.assertEqual(by_id(source, row['media_id']).get('alt'),
                             row['old_source_alt'])
            asset = next(item for item in self.assets['assets']
                         if item['media_id'] == row['media_id'])
            self.assertEqual(
                {asset['outputs'][track]['sha256'] for track in TRACKS},
                {row['image_sha256']})

    def test_correction_contract_rejects_wrong_alt_id_ref_and_bytes(self):
        source = copy.deepcopy(self.bound.source)
        contract = draft.correction_contract(self.rules, self.assets)
        track = 'jv-academic'
        target = translated(source, track, merged_edits(draft.UNIT))

        wrong_alt = copy.deepcopy(target)
        by_id(wrong_alt, contract[0]['media_id']).set('alt', 'owah')
        with self.assertRaises(AssertionError):
            draft.apply_corrections(source, wrong_alt, track, contract, self.assets)

        wrong_id = copy.deepcopy(source)
        checks.at(wrong_id, contract[0]['source_path']).set('id', 'wrong-id')
        with self.assertRaises(AssertionError):
            draft.apply_corrections(wrong_id, copy.deepcopy(target), track,
                                    contract, self.assets)

        wrong_ref = copy.deepcopy(source)
        checks.at(wrong_ref, contract[0]['source_path']).find('{*}image').set(
            'src', '../../media/wrong.jpg')
        with self.assertRaises(AssertionError):
            draft.apply_corrections(wrong_ref, copy.deepcopy(target), track,
                                    contract, self.assets)

        asset = next(row for row in self.assets['assets']
                     if row['media_id'] == contract[0]['media_id'])
        changed_path = LANG / asset['outputs'][track]['path']
        original_read = Path.read_bytes

        def changed_saved(path):
            raw = original_read(path)
            return raw + b'changed' if path == changed_path else raw

        with patch.object(Path, 'read_bytes', changed_saved), \
                self.assertRaises(AssertionError):
            draft.apply_corrections(source, copy.deepcopy(target), track,
                                    contract, self.assets)

    def test_questions_answers_and_finite_chart_narration(self):
        missing = set(self.rules['answer_policy']['missing_solution_ids'])
        for track in TRACKS:
            narration = checks.blocks(track, self.bound)
            keys = [key for key, _ in narration]
            self.assertEqual(len(keys), len(set(keys)))
            self.assertEqual(len(narration), 263)
            self.assertEqual(sum(key.endswith('--question') for key in keys), 125)
            self.assertEqual(sum(key.endswith('--answer') for key in keys), 83)
            self.assertFalse(any(exercise + '--answer' in keys for exercise in missing))
            cue = self.rules['answer_policy']['answer_cues'][track]
            self.assertEqual(sum(body.count(cue) for _, body in narration), 83)
            for media_id in draft.CORRECTION_IDS:
                fixture = next(row for row in self.rules['chart_fixtures']
                               if row['media_id'] == media_id)
                node = checks.at(self.bound.variants[track], fixture['source_path'])
                self.assertEqual(checks.narrate(node, track, self.bound),
                                 fixture['independent_expected_reading'][track])
                if track == 'id-academic':
                    self.assertTrue(checks.narrate(node, track, self.bound).startswith(
                        'Catatan aksesibilitas:'))

    def test_reader_assets_ids_math_and_real_reference_routes(self):
        page = self.build_products['review/units/a00-subtract-whole.html'].decode()
        reader = Reader()
        reader.feed(page)
        self.assertEqual(len(reader.ids), len(set(reader.ids)))
        self.assertEqual((len(reader.ids), reader.maths, len(reader.images)),
                         (2148, 786, 165))
        self.assertEqual(reader.tracks,
                         [(track, locale) for _ in range(11)
                          for track, (locale, _) in TRACKS.items()])
        self.assertEqual(page.count('<table'), 51)

        expected_assets = Counter()
        for row in self.assets['assets']:
            for track in TRACKS:
                output = row['outputs'][track]
                expected_assets[(output['mime_type'], output['sha256'])] += 1
        actual_assets = Counter()
        for image in reader.images:
            header, encoded = image['src'].split(',', 1)
            self.assertTrue(header.startswith('data:image/'))
            actual_assets[(header[5:].removesuffix(';base64'),
                           sha(base64.b64decode(encoded)))] += 1
            self.assertTrue(image.get('alt'))
        self.assertEqual(actual_assets, expected_assets)

        expected_cross = {
            f'a00-add-whole.html#a00-add-whole--{track}--{target}'
            for track in TRACKS
            for target in ('fs-id1239606', 'fs-id1988116')
        }
        self.assertEqual(
            {link for link in reader.links if link.startswith('a00-add-whole.html#')},
            expected_cross)
        addition = (LANG / 'review/units/a00-add-whole.html').read_text(encoding='utf-8')
        for link in expected_cross:
            fragment = link.split('#', 1)[1]
            self.assertEqual(addition.count(f'id="{fragment}"'), 1)
        self.assertEqual(
            {link for link in reader.links if link.startswith('https://www.openstax.org/l/24sub')},
            {'https://www.openstax.org/l/24sub2dignum',
             'https://www.openstax.org/l/24sub3dignum',
             'https://www.openstax.org/l/24subwholenum'})
        self.assertEqual(sum(link.startswith('#a00-subtract-whole--')
                             for link in reader.links), 3)

    def test_transcript_ssml_marks_bodies_locales_and_boundaries(self):
        for track, (locale, _) in TRACKS.items():
            expected = checks.blocks(track, self.bound)
            stem = f'review/audio/a00-subtract-whole.{track}'
            transcript = transcript_blocks(self.build_products[stem + '.md'])
            self.assertEqual(transcript, expected)
            ssml_raw = self.build_products[stem + '.ssml']
            root = ET.fromstring(ssml_raw)
            self.assertEqual(root.get(XML_LANG), locale)
            self.assertEqual([node.get('name') for node in root.findall('{*}mark')],
                             ['m81245--' + key for key, _ in expected])
            paragraphs = root.findall('{*}p')
            self.assertEqual([''.join(node.itertext()) for node in paragraphs[1:]],
                             [body for _, body in expected])
            self.assertNotIn(b'<voice', ssml_raw)
            self.assertNotIn(b'<audio', ssml_raw)
        self.assertFalse(any((LANG / 'review/audio').glob(
            'a00-subtract-whole*.mp3')))

    def test_unknown_or_changed_dispatch_fails_closed(self):
        track = 'jv-academic'
        fixture = next(row for row in self.rules['chart_fixtures']
                       if row['media_id'] == draft.CORRECTION_IDS[0])
        node = checks.at(self.bound.variants[track], fixture['source_path'])
        with self.assertRaises(ValueError):
            checks.narrate(copy.deepcopy(node), track, self.bound)
        with self.assertRaises(ValueError):
            checks.narrate(node, 'unknown', self.bound)

        original_alt = node.get('alt')
        try:
            node.set('alt', original_alt + ' owah')
            with self.assertRaises(ValueError):
                checks.narrate(node, track, self.bound)
        finally:
            node.set('alt', original_alt)

        rules_path = LANG / 'audio/a00-subtract-whole.rules.json'
        original_read = Path.read_bytes

        def changed_rules(path):
            raw = original_read(path)
            return raw + b'changed' if path == rules_path else raw

        with patch.object(Path, 'read_bytes', changed_rules), \
                self.assertRaises(ValueError):
            checks.narrate(node, track, self.bound)

        unknown_link = ET.fromstring(
            '<link xmlns="http://cnx.rice.edu/cnxml" url="https://example.com">x</link>')
        with self.assertRaises(ValueError):
            builder.render(unknown_link, 'a00-subtract-whole--jv-academic--', {})
        with self.assertRaises(ValueError):
            builder.render(unknown_link, 'wrong-prefix', {})
        with self.assertRaises(AssertionError):
            builder.verify_cross_module_routes([])

        contract = self.rules['matching_contract']
        self.assertEqual(contract['unknown_case'], 'error')
        self.assertFalse(contract['broad_parser_authorized'])
        self.assertFalse(contract['generic_mathml_parser_authorized'])
        self.assertFalse(contract['generic_number_parser_authorized'])
        self.assertFalse(contract['generic_table_parser_authorized'])
        self.assertFalse(contract['generic_diagram_parser_authorized'])
        self.assertFalse(contract['provider_calls_authorized'])

    def test_receipt_claims_hashes_and_single_safe_state_name(self):
        receipt = self.build_receipt
        draft_receipt_raw = self.draft_products[
            'qa/a00-subtract-whole.in-progress.json']
        self.assertEqual(receipt['schema'], 'jv-complete-module-build-v1')
        self.assertEqual(receipt['source_draft_receipt_sha256'],
                         sha(draft_receipt_raw))
        self.assertTrue(receipt['complete_module_source'])
        self.assertFalse(receipt['whole_module_complete'])
        self.assertFalse(receipt['full_assignment_complete'])
        for key in ('native_language_review', 'educator_review',
                    'integrated_visual_review', 'assistive_technology_review',
                    'pronunciation_review', 'listening_review'):
            self.assertFalse(receipt[key])
        self.assertEqual(receipt['provider_calls'], 0)
        self.assertEqual(receipt['synthesized_audio_files'], 0)
        self.assertEqual(set(receipt['accessibility_rebinding']['corrected_media_ids']),
                         set(draft.CORRECTION_IDS))
        self.assertEqual(len(receipt['cross_module_routes']), 2)
        self.assertTrue(all(row['resolved_in_offline_reader']
                            for row in receipt['cross_module_routes']))
        for path, digest in receipt['output_sha256'].items():
            self.assertEqual(sha(self.build_products[path]), digest)
        self.assertFalse((LANG / 'qa/a00-subtract-whole.draft-receipt.json').exists())
        self.assertFalse((LANG / 'qa/a00-subtract-whole.build-receipt.json').exists())

    def test_z_deterministic_and_saved_outputs(self):
        self.assertEqual(self.draft_products, draft.products())
        self.assertEqual(self.build_products, builder.products())
        for path, raw in self.draft_products.items():
            if path != 'qa/a00-subtract-whole.in-progress.json':
                self.assertEqual((LANG / path).read_bytes(), raw, path)
        for path, raw in self.build_products.items():
            self.assertEqual((LANG / path).read_bytes(), raw, path)
        self.assertIs(shared_build.render, builder.BASE_RENDER)


if __name__ == '__main__':
    unittest.main()
