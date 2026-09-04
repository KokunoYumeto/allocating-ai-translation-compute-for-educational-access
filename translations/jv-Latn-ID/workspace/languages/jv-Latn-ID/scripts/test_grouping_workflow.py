"""Read-only grouping tests with an explicit, temporary integration boundary.

Source/fixture tests select the pinned [23:28] span directly and do not require
a production descriptor or generated grouping files. ProductionIntegrationTests
skip only while the descriptor is absent, with a visible reason for every test.
Once registered, missing/stale artifacts or unsupported spacing are failures.
These temporary skips are unintegrated work, never completion of A00/A10/AX-2.

All mutations are in-memory copies. Writers are disabled; no build CLI, source
acquisition, image work, synthesis, or shared-file edit is invoked. The finite
speech oracle checks the reviewed fixture convention, not a generic parser or
native-language/visual/screen-reader/listening approval. The rules retain the
actual local and online canon consultation evidence and its limitations.
"""
import copy
import hashlib
import json
from pathlib import Path
import re
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import zipfile

import build
import build_units
import draft_units
from build import CN, MATH, XML_LANG
from config import DOWNLOADS, LANG, TRACKS
from qa import Reader


UNIT = 'a10-grouping-symbols'
MODULE = 'm82453'
SECTION = 'fs-id1170655150800'
INTRO = 'fs-id1170654957487'
TAXONOMY = 'fs-id1170655219760'
EXAMPLES = 'fs-id1170654936322'
SPACE = 'fs-id1166424830424'
NEXT = 'fs-id1170654957085'
DESCRIPTOR = {'section': SECTION, 'slice': [23, 28]}
EXPECTED_IDS = [SECTION, INTRO, TAXONOMY, 'fs-id1167269979347',
                'fs-id1170654880176', 'term-00011', EXAMPLES, SPACE]
SOURCE_HASHES = {
    'id': '2c0b688d569044b128d589579e9ba7d871a0fb9ac7a670ac6f22d0ef2b66e635',
    'en': 'a8fdd235aa254c5a0a1248fa858e9b3579d9b40982bbc514cbe6a18c3e6fcbed',
}
EXPRESSIONS = ['8(14−8)', '21−3[2+4(9−8)]', '24÷{13−2[1(6−5)+4]}']
DELIMITERS = [['(', ')'], ['[', '(', ')', ']'], ['{', '[', '(', ')', ']', '}']]
IMPLIED_SITES = ['8(14−8)', '3[2+4(9−8)]', '4(9−8)', '2[1(6−5)+4]', '1(6−5)']
# Independent, finite oracle: only numbers actually present in this source span.
# C18 supports selikur/patlikur; other component evidence/limits are in the rules.
NUMBERS = {
    '1': ('siji', 'satu'), '2': ('loro', 'dua'), '3': ('telu', 'tiga'),
    '4': ('papat', 'empat'), '5': ('lima', 'lima'), '6': ('enem', 'enam'),
    '8': ('wolu', 'delapan'), '9': ('sanga', 'sembilan'),
    '13': ('telulas', 'tiga belas'), '14': ('patbelas', 'empat belas'),
    '21': ('selikur', 'dua puluh satu'), '24': ('patlikur', 'dua puluh empat'),
}
OPS = {
    '(': ('bukak kurung biasa', 'buka kurung biasa'),
    ')': ('tutup kurung biasa', 'tutup kurung biasa'),
    '[': ('bukak kurung siku', 'buka kurung siku'),
    ']': ('tutup kurung siku', 'tutup kurung siku'),
    '{': ('bukak kurung kurawal', 'buka kurung kurawal'),
    '}': ('tutup kurung kurawal', 'tutup kurung kurawal'),
    '−': ('dikurangi', 'dikurangi'), '+': ('ditambah', 'ditambah'),
    '÷': ('dipara', 'dibagi'),
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def source_documents():
    """Read two small members, not the full canonical archive or network."""
    with zipfile.ZipFile(DOWNLOADS / 'a10-source.zip') as archive:
        raw_id = archive.read(f'translated/modules/{MODULE}/index.cnxml')
        raw_en = archive.read(f'authority/source/modules/{MODULE}/index.cnxml')
    lock = json.loads((LANG / 'sources.lock.json').read_bytes())
    witness = next(row for row in lock['units'] if row['program'] == 'A10' and row['module'] == MODULE)
    assert sha(raw_id) == SOURCE_HASHES['id'] == witness['indonesian_module_sha256']
    assert sha(raw_en) == SOURCE_HASHES['en'] == witness['upstream_module_sha256']
    return raw_id, raw_en


def source_roots():
    return tuple(draft_units.select(raw, DESCRIPTOR) for raw in source_documents())


def rules():
    return json.loads((LANG / f'audio/{UNIT}.rules.json').read_bytes())


def drafts():
    source, _ = source_roots()
    edits = json.loads((LANG / f'translation/{UNIT}.edits.json').read_bytes())
    shared = json.loads((LANG / 'translation/phrases.json').read_bytes())
    rows = {row[0]: row for row in shared['phrases']}
    for row in edits['phrases']:
        assert row[0] not in rows or rows[row[0]] == row, 'Conflicting shared phrase'
        rows[row[0]] = row
    merged = {**edits, 'phrases': list(rows.values()),
              'unchanged_identifiers': sorted(set(shared['unchanged_identifiers'] + edits['unchanged_identifiers']))}
    result = {'id-academic': source}
    for track in ('jv-academic', 'jv-conversation'):
        result[track] = build.translated(source, track, merged)
        draft_units.validate(source, result[track])
    return result


def anchor(root, source_id):
    return next(node for node in root.iter() if node.get('id') == source_id)


def maths(root):
    return list(root.iter('{' + MATH + '}math'))


def occupied_cells(root):
    return [cell for cell in maths(root)[1].find('.//{' + MATH + '}mtr')
            if ''.join(cell.itertext()).strip()]


def fixture_scope(specification):
    """Suite gate for metadata; does not claim dispatch checks it implicitly."""
    scope = specification['scope']
    assert (scope['unit'], scope['module'], scope['section']) == (UNIT, MODULE, SECTION)
    assert scope['direct_child_slice_zero_based'] == [23, 28]
    assert (scope['first_anchor'], scope['last_included_anchor'], scope['next_anchor']) == (INTRO, SPACE, NEXT)
    assert scope['indonesian_sha256'] == SOURCE_HASHES['id'] and scope['english_sha256'] == SOURCE_HASHES['en']
    assert scope['source_ids_total'] == 8 and scope['new_source_ids_excluding_shared_section'] == 7
    assert scope['source_mathml_expression_count'] == 2
    assert specification['nonspoken_source_blocks'] == [SPACE]
    fixtures = specification['math_fixtures']
    assert [(row['module'], row['section'], row['anchor'], row['math_ordinal']) for row in fixtures] == [
        (MODULE, SECTION, TAXONOMY, 1), (MODULE, SECTION, EXAMPLES, 1)]
    assert not specification['matching_contract']['broad_parser_authorized']
    assert not specification['matching_contract']['generic_matrix_reading_authorized']
    assert not specification['matching_contract']['expression_evaluation_authorized']


def cell_reading(cell, track):
    """Test-only oracle for these three exact expressions; never evaluates."""
    if ''.join(cell.itertext()) not in EXPRESSIONS:
        raise ValueError('Unregistered grouping test expression')
    words, stack, previous, implied = [], [], None, 0
    index = 0 if track.startswith('jv') else 1
    for node in cell:
        tag, token = node.tag.rsplit('}', 1)[-1], node.text
        assert node.tag in ('{' + MATH + '}mn', '{' + MATH + '}mo')
        if token in ('(', '[', '{'):
            stack.append(token)
            if previous == 'mn':
                words.append('ping' if index == 0 else 'kali')
                implied += 1
        elif token in (')', ']', '}'):
            assert stack.pop() == {')': '(', ']': '[', '}': '{'}[token]
        words.append((NUMBERS if tag == 'mn' else OPS)[token][index])
        previous = tag
    assert not stack
    return ' '.join(words), implied


def fixture_readings(specification, source):
    """Semantic regression gate for edited expected readings, not production NLP."""
    fixture_scope(specification)
    first, second = specification['math_fixtures']
    assert second['source_expressions'] == EXPRESSIONS
    assert second['delimiter_sequences_per_expression'] == DELIMITERS
    implied = specification['implicit_multiplication_convention']
    assert implied['source_sites'] == IMPLIED_SITES and implied['site_count'] == 5
    for track in TRACKS:
        index = 0 if track.startswith('jv') else 1
        heading = {'jv-academic': 'Tandha ', 'jv-conversation': '', 'id-academic': 'Tanda '}[track]
        labels = [heading + ('Kurung ' if not heading else 'kurung ') + shape for shape in ('biasa', 'siku', 'kurawal')]
        assert first['translated_mtext'][track] == labels
        expected = ' '.join(label + ': ' + OPS[left][index] + ', ' + OPS[right][index] + '.'
                            for label, (left, right) in zip(labels, [('(', ')'), ('[', ']'), ('{', '}')]))
        assert first['expected'][track] == expected, 'Changed bracket taxonomy reading'
        parts = second['expected'][track].rstrip('.').split('. ')
        headers = {'jv-academic': ['Ekspresi kapisan', 'Ekspresi kapindho', 'Ekspresi katelu'],
                   'jv-conversation': ['Wujud siji', 'Wujud loro', 'Wujud telu'],
                   'id-academic': ['Ekspresi pertama', 'Ekspresi kedua', 'Ekspresi ketiga']}[track]
        assert len(parts) == 3
        total = 0
        for part, header, cell in zip(parts, headers, occupied_cells(source)):
            actual_header, body = part.split(': ', 1)
            assert actual_header == header
            expected, count = cell_reading(cell, track)
            assert body.replace(',', '') == expected, 'Changed operand/operator/nesting reading'
            total += count
        assert total == 5
        for fixture, expression in zip((first, second), maths(source)):
            actual = re.findall(r'(?:bukak|buka|tutup) kurung (?:biasa|siku|kurawal)', fixture['expected'][track])
            tokens = [node.text for node in expression.iter('{' + MATH + '}mo') if node.text in '()[]{}']
            assert actual == [OPS[token][index] for token in tokens], 'Changed bracket type/order'


def ssml_blocks(raw):
    result, current = {}, None
    for child in ET.fromstring(raw):
        if child.tag.endswith('}mark'):
            current = child.get('name')
            assert current not in result, 'Duplicate source speech mark'
        elif child.tag.endswith('}p') and current is not None:
            result[current] = ''.join(child.itertext())
            current = None
    return result


class GroupingSourceTests(unittest.TestCase):
    def test_exact_contiguous_slice_and_next_boundary_without_descriptor(self):
        for raw in source_documents():
            full = ET.fromstring(raw)
            section = anchor(full, SECTION)
            selected = draft_units.select(raw, DESCRIPTOR)
            self.assertEqual(section[23].get('id'), INTRO)
            self.assertEqual(section[27].get('id'), SPACE)
            self.assertEqual(section[28].get('id'), NEXT)
            self.assertEqual([ET.tostring(node) for node in selected],
                             [ET.tostring(section[0])] + [ET.tostring(node) for node in list(section)[23:28]])

    def test_eight_ids_seven_new_and_two_mathml_in_every_register(self):
        raw_id, _ = source_documents()
        earlier = draft_units.select(raw_id, {'section': SECTION, 'slice': [1, 23]})
        earlier_ids = {node.get('id') for node in earlier.iter() if node.get('id')}
        for track, root in drafts().items():
            with self.subTest(track=track):
                ids = [node.get('id') for node in root.iter() if node.get('id')]
                self.assertEqual(ids, EXPECTED_IDS)
                self.assertEqual(set(ids) & earlier_ids, {SECTION})
                self.assertEqual(len(set(ids) - earlier_ids), 7)
                self.assertEqual(len(maths(root)), 2)
                for tag in ('table', 'media', 'link', 'exercise', 'solution'):
                    self.assertFalse(root.findall('.//{' + CN + '}' + tag), tag)

    def test_exact_new_source_keys_and_shared_title_resolve(self):
        source, _ = source_roots()
        edits = json.loads((LANG / f'translation/{UNIT}.edits.json').read_bytes())
        keys = {text.strip() for node in source.iter() for text in (node.text, node.tail)
                if text and re.search('[A-Za-z]', text)}
        self.assertEqual(len(edits['phrases']), 8)
        self.assertEqual({row[0] for row in edits['phrases']}, keys - {'Gunakan Variabel dan Simbol Aljabar'})
        for root in drafts().values():
            self.assertTrue(root.find('{*}title').text)

    def test_source_english_and_indonesian_math_differ_only_in_labels(self):
        source, english = source_roots()
        for left, right in zip(maths(source), maths(english)):
            self.assertEqual(build_units.narration_tree_key(left), build_units.narration_tree_key(right))
        self.assertEqual([node.text for node in source.iter('{' + MATH + '}mtext')],
                         ['Tanda kurung biasa', 'Tanda kurung siku', 'Tanda kurung kurawal'])
        self.assertEqual([node.text for node in english.iter('{' + MATH + '}mtext')], ['Parentheses', 'Brackets', 'Braces'])

    def test_empty_layout_cells_groups_and_attributes_are_preserved(self):
        for root in drafts().values():
            tables = [math.find('.//{' + MATH + '}mtable') for math in maths(root)]
            self.assertEqual([[len(row) for row in table] for table in tables], [[4, 4, 4], [7]])
            self.assertEqual([sum(not len(cell) for row in table for cell in row) for table in tables], [6, 4])
            self.assertEqual(len([node for node in tables[0].iter('{' + MATH + '}mrow') if not len(node)]), 3)
            self.assertTrue(all(table.attrib == {} and all(row.attrib == {} for row in table) for table in tables))
            self.assertTrue(all(cell.get('columnalign') == 'left' for row in tables[0] for cell in row if len(cell)))
            self.assertTrue(all(cell.get('columnalign') == 'center' for cell in occupied_cells(root)))
            self.assertEqual([node.attrib for node in tables[0].iter('{' + MATH + '}mspace')], [{'width': '0.15em'}] * 2)

    def test_exact_three_expressions_nested_brackets_and_five_implied_products(self):
        for track, root in drafts().items():
            cells = occupied_cells(root)
            self.assertEqual([''.join(cell.itertext()) for cell in cells], EXPRESSIONS)
            self.assertEqual([[node.text for node in cell if node.text in '()[]{}'] for cell in cells], DELIMITERS)
            self.assertEqual([cell_reading(cell, track)[1] for cell in cells], [1, 2, 2])
            self.assertEqual(sum(cell_reading(cell, track)[1] for cell in cells), 5)

    def test_spacing_only_source_is_preserved_and_intrinsically_silent(self):
        for track, root in drafts().items():
            space = anchor(root, SPACE)
            self.assertEqual([child.tag for child in space], ['{' + CN + '}newline'])
            self.assertFalse(''.join(space.itertext()).strip())
            self.assertFalse(build_units.narrate(space, track, UNIT, {}, rules()).strip())
        self.assertEqual(rules()['nonspoken_source_blocks'], [SPACE])


class GroupingFixtureTests(unittest.TestCase):
    def test_exact_scope_and_source_tree_dispatch_in_all_three_tracks(self):
        specification = rules()
        fixture_scope(specification)
        variants = drafts()
        for track, root in variants.items():
            bound = build_units.source_bound_math(root, specification, track, variants['id-academic'])
            self.assertEqual(len(bound), 2)
            self.assertEqual([bound[id(math)] for math in maths(root)], [row['expected'][track] for row in specification['math_fixtures']])
            self.assertEqual([node.text for node in root.iter('{' + MATH + '}mtext')], specification['math_fixtures'][0]['translated_mtext'][track])

    def test_finite_oracle_verifies_every_reading_operand_operator_and_delimiter(self):
        fixture_readings(rules(), source_roots()[0])

    def test_changed_source_trees_fail_closed(self):
        for kind in ('anchor', 'extra-ordinal', 'mtable', 'mtr', 'mtd', 'stretchy',
                     'empty-cell', 'empty-group', 'delimiter', 'closing-brace', 'operand', 'cell-order'):
            root = source_roots()[0]
            first, second = maths(root)
            table = first.find('.//{' + MATH + '}mtable')
            row = second.find('.//{' + MATH + '}mtr')
            if kind == 'anchor':
                anchor(root, TAXONOMY).set('id', 'unregistered')
            elif kind == 'extra-ordinal':
                anchor(root, TAXONOMY).append(copy.deepcopy(first))
            elif kind in ('mtable', 'mtr', 'mtd'):
                target = {'mtable': table, 'mtr': table[0], 'mtd': table[0][0]}[kind]
                target.set('columnalign', 'right')
            elif kind == 'stretchy':
                second.find('.//{' + MATH + '}mo').set('stretchy', 'true')
            elif kind == 'empty-cell':
                table[0].remove(table[0][1])
            elif kind == 'empty-group':
                table[0][3][-1].remove(table[0][3][-1][1])
            elif kind == 'delimiter':
                second.find('.//{' + MATH + '}mo').text = '['
            elif kind == 'closing-brace':
                row[-1].remove(row[-1][-1])
            elif kind == 'operand':
                second.find('.//{' + MATH + '}mn').text = '9'
            else:
                row[0], row[3] = row[3], row[0]
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, 'unsupported_source_bound_narration'):
                build_units.source_bound_math(root, rules(), 'id-academic')

    def test_changed_source_fixture_anchor_ordinal_and_math_are_rejected(self):
        for kind in ('anchor', 'ordinal', 'alignment', 'delimiter', 'source-label'):
            specification = rules()
            row = specification['math_fixtures'][0]
            if kind == 'anchor':
                row['anchor'] = 'not-in-source'
            elif kind == 'ordinal':
                row['math_ordinal'] = 2
            elif kind == 'alignment':
                row['source_mathml'] = row['source_mathml'].replace('columnalign="left"', 'columnalign="right"', 1)
            elif kind == 'delimiter':
                row['source_mathml'] = row['source_mathml'].replace('<m:mo>(</m:mo>', '<m:mo>[</m:mo>', 1)
            else:
                row['source_mathml'] = row['source_mathml'].replace('Tanda kurung biasa', 'Unknown bracket')
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, 'unsupported_source_bound_narration'):
                build_units.source_bound_math(source_roots()[0], specification, 'id-academic')

    def test_duplicate_and_unused_fixture_failures(self):
        for kind in ('duplicate', 'unused'):
            specification = rules()
            extra = copy.deepcopy(specification['math_fixtures'][0])
            if kind == 'unused':
                extra['anchor'] = 'not-in-this-span'
            specification['math_fixtures'].append(extra)
            with self.subTest(kind=kind), self.assertRaises(AssertionError):
                build_units.source_bound_math(source_roots()[0], specification, 'id-academic')

    def test_altered_fixture_scope_fails_explicit_suite_gate(self):
        for kind in ('module', 'slice', 'hash', 'spacing'):
            specification = rules()
            if kind == 'module':
                specification['math_fixtures'][0]['module'] = 'wrong-module'
            elif kind == 'slice':
                specification['scope']['direct_child_slice_zero_based'] = [23, 27]
            elif kind == 'hash':
                specification['scope']['indonesian_sha256'] = '0' * 64
            else:
                specification['nonspoken_source_blocks'] = []
            with self.subTest(kind=kind), self.assertRaises(AssertionError):
                fixture_scope(specification)

    def test_altered_expected_speech_fails_semantic_regression_gate(self):
        for kind in ('operand', 'multiplication', 'bracket-type', 'closing-order', 'missing-expression', 'taxonomy'):
            specification = rules()
            row = specification['math_fixtures'][1]
            value = row['expected']['jv-academic']
            if kind == 'operand':
                row['expected']['jv-academic'] = value.replace('wolu ping', 'sanga ping', 1)
            elif kind == 'multiplication':
                row['expected']['jv-academic'] = value.replace('wolu ping', 'wolu', 1)
            elif kind == 'bracket-type':
                row['expected']['jv-academic'] = value.replace('bukak kurung siku', 'bukak kurung biasa', 1)
            elif kind == 'closing-order':
                row['expected']['jv-academic'] = value.replace('tutup kurung biasa, tutup kurung siku', 'tutup kurung siku, tutup kurung biasa', 1)
            elif kind == 'missing-expression':
                row['expected']['jv-academic'] = value.split(' Ekspresi katelu:')[0]
            else:
                specification['math_fixtures'][0]['expected']['jv-academic'] = 'Kurung.'
            with self.subTest(kind=kind), self.assertRaises(AssertionError):
                fixture_readings(specification, source_roots()[0])

    def test_changed_translation_structure_and_tokens_fail_validation(self):
        variants = drafts()
        for kind in ('source-id', 'numeric-token', 'delimiter', 'attribute'):
            changed = copy.deepcopy(variants['jv-academic'])
            if kind == 'source-id':
                changed.set('id', 'wrong-section')
            elif kind == 'numeric-token':
                next(changed.iter('{' + MATH + '}mn')).text = '9'
            elif kind == 'delimiter':
                next(changed.iter('{' + MATH + '}mo')).text = '['
            else:
                next(changed.iter('{' + MATH + '}mtd')).set('columnalign', 'right')
            with self.subTest(kind=kind), self.assertRaises(AssertionError):
                draft_units.validate(variants['id-academic'], changed)


class ProductionIntegrationTests(unittest.TestCase):
    def setUp(self):
        if UNIT not in draft_units.UNITS:
            self.skipTest('TEMPORARILY UNINTEGRATED: a10-grouping-symbols production descriptor absent; source/fixture passes are not reader/audio completion')
        descriptor = draft_units.UNITS[UNIT]
        self.assertEqual((descriptor['program'], descriptor['module'], descriptor['section'], descriptor['slice']),
                         ('A10', MODULE, SECTION, [23, 28]))
        for module in (build_units, draft_units):
            guard = patch.object(module, 'write_bytes', side_effect=AssertionError('Forbidden integration-test write'))
            guard.start()
            self.addCleanup(guard.stop)

    def test_registered_drafts_and_products_are_current_deterministic_read_only(self):
        for first, second in ((draft_units.products(UNIT), draft_units.products(UNIT)),
                              (build_units.products(UNIT), build_units.products(UNIT))):
            self.assertEqual(first, second)
            for path, raw in first.items():
                self.assertEqual((LANG / path).read_bytes(), raw, path)

    def test_reader_preserves_every_source_id_and_empty_spacing_node(self):
        products = build_units.products(UNIT)
        reader = Reader()
        page = products[f'review/units/{UNIT}.html'].decode()
        reader.feed(page)
        self.assertEqual(reader.maths, 6)
        self.assertEqual(reader.images, [])
        self.assertEqual(len(reader.ids), len(set(reader.ids)))
        for track in TRACKS:
            for source_id in EXPECTED_IDS:
                self.assertIn(UNIT + '--' + track + '--' + source_id, reader.ids)
            self.assertRegex(page, re.escape('id="' + UNIT + '--' + track + '--' + SPACE + '"') + r'[^>]*>\s*<br\s*/?>')

    def test_transcripts_and_ssml_preserve_readings_but_omit_empty_spacing_speech(self):
        products, variants, specification = build_units.products(UNIT), drafts(), rules()
        for track, (locale, _) in TRACKS.items():
            raw = products[f'review/audio/{UNIT}.{track}.ssml']
            document = ET.fromstring(raw)
            self.assertEqual(document.get(XML_LANG), locale)
            self.assertTrue(all(''.join(node.itertext()).strip() for node in document.findall('{*}p')))
            expected = {MODULE + '--' + source_id: body for source_id, body in build_units.blocks(
                variants[track], track, UNIT, specification, variants['id-academic'])}
            self.assertEqual(list(expected), [MODULE + '--' + source_id for source_id in ('title', INTRO, TAXONOMY, 'fs-id1170654880176', EXAMPLES)])
            self.assertNotIn(MODULE + '--' + SPACE, ssml_blocks(raw))
            self.assertEqual(ssml_blocks(raw), expected)
            transcript = products[f'review/audio/{UNIT}.{track}.md'].decode()
            markdown = {name: body.strip() for name, body in re.findall(r'^## (\S+)\n\n(.*?)(?=^## |\Z)', transcript, re.M | re.S)}
            self.assertEqual(markdown, expected)
            for row in specification['math_fixtures']:
                self.assertIn(row['expected'][track], expected[MODULE + '--' + row['anchor']])
            self.assertNotIn('Wangsulan.', transcript)
            self.assertNotIn('Jawaban.', transcript)

    def test_receipt_records_spacing_exception_hashes_and_unfinished_review(self):
        products = build_units.products(UNIT)
        receipt = json.loads(products[f'qa/{UNIT}.build-receipt.json'])
        self.assertEqual((receipt['source_ids'], receipt['source_math_expressions'], receipt['source_media_references']), (8, 2, 0))
        self.assertEqual(receipt['source_bound_math_fixtures'], 2)
        self.assertEqual(receipt['nonspoken_source_blocks'], [SPACE])
        self.assertEqual(receipt['rules_sha256'], sha((LANG / f'audio/{UNIT}.rules.json').read_bytes()))
        self.assertEqual(receipt['source_draft_receipt_sha256'], sha((LANG / f'qa/{UNIT}.draft-receipt.json').read_bytes()))
        self.assertEqual(receipt['output_sha256'], {path: sha(raw) for path, raw in products.items() if path.startswith('review/')})
        for field in ('human_language_review', 'visual_review', 'listening_review', 'whole_module_complete'):
            self.assertFalse(receipt[field])
        self.assertEqual(receipt['synthesized_audio_files'], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
