"""Actual-source and independent finite readout checks for whole-number writing."""
import copy
import json
import re
import unittest
import xml.etree.ElementTree as ET

import build_units
import draft_units
from build import MATH, XML_LANG, translated
from config import LANG, TRACKS
from qa import Reader
from writing_checks import validate_values

UNIT = 'a00-write-whole'
SECTION = 'fs-id1339359'
DIRECT = ['fs-id2607182', 'fs-id2398163', 'fs-id2376697', 'fs-id1542693',
          'fs-id2437124', 'fs-id3202693', 'fs-id1805534', 'fs-id1397780']
PRINTED = ['53,401,742', '9,246,073,189', '77,000,000,000',
           '53,809,051', '2,022,714,466', '34,000,000', '204,000,000']


def node(root, anchor):
    return next(element for element in root.iter() if element.get('id') == anchor)


def decode_literal(text, track):
    """Test-only digit/mark decoder; deliberately does not use number()."""
    jv = track.startswith('jv')
    digits = ('nol siji loro telu papat lima enem pitu wolu sanga' if jv else
              'nol satu dua tiga empat lima enam tujuh delapan sembilan').split()
    names = {word: str(value) for value, word in enumerate(digits)}
    prefix = 'digit saka kiwa menyang tengen: ' if jv else 'digit dari kiri ke kanan: '
    if not text.startswith(prefix) or not text.endswith('.'):
        raise ValueError('Not literal digits')
    text = text[len(prefix):-1]
    units = [unit for unit in ('dolar Amerika Serikat', 'mil', 'pound') if text.endswith('; ' + unit)]
    unit = units[0] if units else None
    if unit:
        text = text[:-len('; ' + unit)]
    separator = '; tandha koma; ' if jv else '; tanda koma; '
    groups = [group.split(', ') for group in text.split(separator)]
    try:
        return ','.join(''.join(names[word] for word in group) for group in groups), unit
    except KeyError as error:
        raise ValueError('Unknown digit name') from error


class WritingWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        lock = json.loads((LANG / 'sources.lock.json').read_text(encoding='utf-8'))
        repo = next(row for row in lock['repositories'] if row['name'] == 'a00-id')
        cls.raw = draft_units.pinned_blob(repo, 'modules/m81243/index.cnxml')
        cls.source = draft_units.select(cls.raw, {'section': SECTION, 'slice': None})
        cls.rules = json.loads((LANG / f'audio/{UNIT}.rules.json').read_text(encoding='utf-8'))
        cls.variants = {'id-academic': cls.source, **{
            track: translated(cls.source, track, draft_units.merged_edits(UNIT))
            for track in ('jv-academic', 'jv-conversation')}}

    def test_entire_exact_source_boundary(self):
        self.assertEqual(build_units.sha(self.raw), '7153ce88bcd4aea07fab4075bdb025884e07d534aafb6d06ff1bfbedbc46f251')
        self.assertEqual([child.get('id') for child in self.source][1:], DIRECT)
        ids = [item.get('id') for item in self.source.iter() if item.get('id')]
        self.assertEqual(len(ids), 57)
        self.assertEqual(len(set(ids)), 57)
        self.assertEqual(ids[-1], 'fs-id1395137')
        self.assertNotIn('fs-id2472737', ids)
        self.assertEqual(len(self.source.findall('.//{*}exercise')), 6)
        self.assertEqual(len(self.source.findall('.//{*}solution')), 6)
        self.assertEqual(len(self.source.findall('.//{*}media')), 3)
        self.assertEqual(self.source.findall('.//{*}table'), [])
        tokens = [x.text for x in self.source.iter() if x.tag in ('{' + MATH + '}mn', '{' + MATH + '}mtext', '{' + MATH + '}mo')]
        self.assertEqual(tokens, ['53,401,742', '.', '9,246,073,189', '.', '$77', '$77,000,000,000.', '34', '204'])

    def test_all_twenty_one_literal_answers_independent(self):
        fixtures = [row for row in self.rules['math_fixtures'] if row['reading_policy'] == 'literal_digits_not_cardinal_answer']
        fixtures += [row for row in self.rules['prose_fixtures'] if row.get('requires_solution_cue')]
        self.assertEqual(len(fixtures), 7)
        for track in TRACKS:
            decoded = [decode_literal(row['expected'][track], track) for row in fixtures]
            self.assertEqual([value for value, _ in decoded], PRINTED)
            self.assertEqual([unit for _, unit in decoded], [None, None, 'dolar Amerika Serikat', None, None, 'mil', 'pound'])
        self.assertEqual([int(value.replace(',', '')) for value in PRINTED],
                         [53*10**6+401*1000+742, 9*10**9+246*10**6+73*1000+189,
                          77*10**9, 53*10**6+809*1000+51, 2*10**9+22*10**6+714*1000+466,
                          34*10**6, 204*10**6])
        with self.assertRaises(ValueError):
            decode_literal('sèket telu yuta', 'jv-academic')

    def test_exact_values_and_metadata_mutations(self):
        validate_values(self.source, self.variants, self.rules)
        mutations = [
            lambda r: r['math_fixtures'][0]['expected'].__setitem__('jv-academic', 'sèket telu yuta'),
            lambda r: r['math_fixtures'][2].__setitem__('standalone_readout_authorized', True),
            lambda r: r['quantity_invariants'][0].__setitem__('scale', '1000000'),
            lambda r: r['quantity_invariants'][2].__setitem__('spoken_unit', 'kilogram'),
            lambda r: r['chart_fixtures'][1].__setitem__('groups_from_left', ['9', '246', '73', '189']),
            lambda r: r['chart_fixtures'][2].__setitem__('empty_word_block_indices_from_left', []),
            lambda r: r['chart_fixtures'][0].__setitem__('arrow_direction', 'digit_group_to_word_block'),
        ]
        for mutate in mutations:
            altered = copy.deepcopy(self.rules)
            mutate(altered)
            with self.assertRaises(AssertionError):
                validate_values(self.source, self.variants, altered)

    def test_all_tracks_complete_and_no_answer_leakage(self):
        for track, root in self.variants.items():
            narration = build_units.blocks(root, track, UNIT, self.rules, self.source)
            self.assertEqual([anchor for anchor, _ in narration], ['title'] + DIRECT)
            full = '\n'.join(body for _, body in narration)
            cue = 'Wangsulan.' if track.startswith('jv') else 'Jawaban.'
            self.assertEqual(full.count(cue), 4)
            self.assertNotIn('bagean bagean', full)
            self.assertNotIn('bagian bagian', full)
            self.assertNotIn('be: ,', full)
            self.assertNotRegex(full, r'\bpon\b')
            for invariant in self.rules['answer_value_invariants']:
                question, answer = dict(narration)[invariant['anchor']].split(cue)
                self.assertNotIn('digit saka kiwa', question)
                self.assertNotIn('digit dari kiri', question)
                self.assertIn(decode_literal(answer.strip(), track)[0], PRINTED)
            for fixture in self.rules['chart_fixtures'] + self.rules['prose_fixtures']:
                self.assertEqual(full.count(fixture['expected'][track]), 1)

    def test_required_full_prose_context_cannot_fall_back(self):
        for track, root in self.variants.items():
            bound = build_units.source_bound_math(root, self.rules, track, self.source)
            self.assertEqual(len(bound), 6)
            self.assertEqual(len(bound.prose_only), 2)
            for anchor in ('fs-id2590590', 'fs-id1586764'):
                parent = node(root, anchor)
                expression = parent.find('.//{' + MATH + '}math')
                for mapping in (bound, {}, dict(bound)):
                    with self.assertRaises(ValueError):
                        build_units.narrate(expression, track, UNIT, mapping, self.rules)
                self.assertIn('pound' if anchor == 'fs-id1586764' else 'milyar' if track.startswith('jv') else 'miliar',
                              build_units.narrate(parent, track, UNIT, bound, self.rules))
            altered = copy.deepcopy(self.rules)
            altered['prose_fixtures'] = [row for row in altered['prose_fixtures'] if row['id'] != 'A00-WRITE-P03']
            with self.assertRaises(AssertionError):
                build_units.blocks(root, track, UNIT, altered, self.source)

    def test_source_and_target_mutations_rejected(self):
        mutations = [
            lambda r: node(r, 'fs-id4163187').__setattr__('text', '53,809,51'),
            lambda r: node(r, 'fs-id2668978').set('alt', 'Wrong words 53 401 742'),
            lambda r: node(r, 'fs-id2903601').find('{*}image').set('src', 'unknown.svg'),
            lambda r: node(r, 'fs-id2590590').find('.//{' + MATH + '}mtext').__setattr__('text', '€77'),
            lambda r: node(r, 'fs-id1395137').__setattr__('text', '204,000,000 kilogram'),
            lambda r: node(r, 'fs-id2880619').find('{*}span').__setattr__('text', 'ⓒ'),
        ]
        for track, root in self.variants.items():
            for mutate in mutations:
                changed = copy.deepcopy(root)
                mutate(changed)
                with self.assertRaises((AssertionError, ValueError)):
                    build_units.blocks(changed, track, UNIT, self.rules, self.source)
        source = copy.deepcopy(self.source)
        node(source, 'fs-id2607182').text = 'Other source introduction.'
        with self.assertRaises(AssertionError):
            build_units.blocks(source, 'id-academic', UNIT, self.rules, source)

    def test_saved_reader_and_ssml_contract(self):
        page = (LANG / f'review/units/{UNIT}.html').read_text(encoding='utf-8')
        reader = Reader()
        reader.feed(page)
        self.assertEqual(reader.maths, 18)
        self.assertEqual(len(reader.images), 9)
        self.assertEqual(reader.heads, [])
        for track, (locale, _) in TRACKS.items():
            self.assertIn(f'<ol id="{UNIT}--{track}--eip-100"', page)
            ssml = ET.parse(LANG / f'review/audio/{UNIT}.{track}.ssml').getroot()
            self.assertEqual(ssml.get(XML_LANG), locale)
            narration = build_units.blocks(self.variants[track], track, UNIT, self.rules, self.source)
            self.assertEqual([mark.get('name') for mark in ssml.findall('{*}mark')], ['m81243--' + anchor for anchor, _ in narration])
            self.assertEqual([p.text for p in ssml.findall('{*}p')][1:], [body for _, body in narration])
            self.assertTrue(all(image['src'].startswith('data:image/svg+xml;base64,') for image in reader.images))

    def test_deterministic_saved_products(self):
        for producer in (draft_units.products, build_units.products):
            generated = producer(UNIT)
            self.assertEqual(generated, producer(UNIT))
            for path, raw in generated.items():
                self.assertEqual((LANG / path).read_bytes(), raw, path)


if __name__ == '__main__':
    unittest.main()
