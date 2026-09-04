"""Read-only source-bound equality regression tests; never a completion claim.

The span has 35 new IDs plus its shared section wrapper: 36 total, not 35.
All mutations are in memory. Product writers are disabled and no acquisition,
build CLI, image rewrite, voice service, or shared-file edit is performed.

QA consultation on 2026-08-31 reread actual C09 kiwa, C10 tengen, C11 luwih,
C12 gedhe, C13 cilik, C17 rolas, C18 likur, and C22 para readable KBJI entries.
These support components/directions, not standardized full mathematical phrases
or every composed numeral. Native, visual, screen-reader and listening review,
and the full A00/A10/AX-2 assignment, remain unfinished.
"""
import base64
import copy
import hashlib
import json
from pathlib import Path
import re
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import build_units
import draft_units
import prepare_equality_assets as asset_builder
from build import CN, MATH, XML_LANG
from config import LANG, TRACKS
from qa import Reader


UNIT = 'a10-equality-symbols'
MODULE = 'm82453'
SECTION = 'fs-id1170655150800'
SPACE = 'fs-id1171789687379'
EQUALITY = 'fs-id1170655025665'
DIAGRAMS = 'fs-id1170655207857'
REVERSALS = 'fs-id1170655155145'
TABLE = 'fs-id1170655178120'
EXAMPLE = 'fs-id1170655113222'
PRACTICES = ('fs-id1170654935250', 'fs-id1170655124058')
EXPECTED_IDS = '''fs-id1170655150800 fs-id1171789687379 fs-id1170655208137
term-00010 fs-id1170655025665 fs-id1170654990403 fs-id1170655126926
fs-id1170655108736 fs-id1170655207857 fs-id1167270244162 fs-id1170652623871
fs-id1167269909313 fs-id1167269961954 fs-id1170655155145 fs-id1170655178120
fs-id1170655113222 fs-id1170654999980 fs-id1170655020482 fs-id1170654984453
fs-id1170654989586 fs-id1170655105413 fs-id1166424795899 fs-id1170654935250
fs-id1170655166352 fs-id1170654985390 fs-id1170654943066 fs-id1170655190264
fs-id1170654943209 fs-id1170655353526 fs-id1170655124058 fs-id1170655205783
fs-id1170655166119 fs-id1170655203511 fs-id1170655174550 fs-id1170655192260
fs-id1170655222902'''.split()
IMAGES = (
    ('fs-id1170652623871', 'CNX_ElemAlg_Figure_01_02_001_img_new.jpg', 14959,
     '5bd5be8d8057f98b4b6acf06f64445d6806ef7265117cd1f5106d1140bbe25da'),
    ('fs-id1167269961954', 'CNX_ElemAlg_Figure_01_02_002_img_new.jpg', 15798,
     '0e2f32f4998d214b4dc06b124d9830ed9fe624be30a94e2c29259ac70fb8fb9f'),
)
# Independent finite test oracle, not an expression parser or evaluator.
# The three special fixtures are checked separately below.
FORMULAS = ('a = b', None, None, None, 'a ≠ b', 'a ≤ b', 'a ≥ b',
            '17 ≤ 26', '8 ≠ 17 − 3', '12 > 27 ÷ 3', 'y + 7 < 19',
            '17 ≤ 26', '8 ≠ 17 − 3', '12 > 27 ÷ 3', 'y + 7 < 19',
            '14 ≤ 27', '19 − 2 ≠ 8', '12 > 4 ÷ 2', 'x − 7 < 1',
            '19 ≥ 15', '7 = 12 − 5', '15 ÷ 3 < 8', 'y + 3 > 6')
WORDS_JV = dict(zip('1 2 3 4 5 6 7 8 11 12 14 15 17 19 26 27'.split(),
                    ('siji', 'loro', 'telu', 'papat', 'lima', 'enem', 'pitu', 'wolu',
                     'sewelas', 'rolas', 'patbelas', 'limalas', 'pitulas', 'sangalas', 'nemlikur', 'pitulikur')))
WORDS_ID = dict(zip('1 2 3 4 5 6 7 8 11 12 14 15 17 19 26 27'.split(),
                    ('satu', 'dua', 'tiga', 'empat', 'lima', 'enam', 'tujuh', 'delapan',
                     'sebelas', 'dua belas', 'empat belas', 'lima belas', 'tujuh belas',
                     'sembilan belas', 'dua puluh enam', 'dua puluh tujuh')))
WORDS_JV.update({'a':'aksara a', 'b':'aksara be', 'x':'aksara eks', 'y':'aksara ye',
                 '=':'padha karo', '≠':'ora padha karo', '<':'luwih cilik tinimbang',
                 '>':'luwih gedhé tinimbang', '≤':'luwih cilik utawa padha karo',
                 '≥':'luwih gedhé utawa padha karo', '−':'dikurangi', '÷':'dipara', '+':'ditambah'})
WORDS_ID.update({'a':'huruf a', 'b':'huruf be', 'x':'huruf eks', 'y':'huruf ye',
                 '=':'sama dengan', '≠':'tidak sama dengan', '<':'kurang dari', '>':'lebih dari',
                 '≤':'kurang dari atau sama dengan', '≥':'lebih dari atau sama dengan',
                 '−':'dikurangi', '÷':'dibagi', '+':'ditambah'})


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def variant(track):
    return ET.parse(LANG / f'translation/{UNIT}.{track}.cnxml').getroot()


def rules():
    return json.loads((LANG / f'audio/{UNIT}.rules.json').read_bytes())


def anchor(root, source_id):
    return next(node for node in root.iter() if node.get('id') == source_id)


def math_at(root, source_id=DIAGRAMS, ordinal=1):
    return list(anchor(root, source_id).iter('{' + MATH + '}math'))[ordinal - 1]


def reading(formula, track):
    words = WORDS_JV if track.startswith('jv') else WORDS_ID
    return ' '.join(words[token] for token in formula.split())


def normalized(text):
    return re.sub(r'\s+', ' ', text).strip()


def transcript_blocks(raw):
    return {name: body.strip() for name, body in re.findall(
        r'^## (\S+)\n\n(.*?)(?=^## |\Z)', raw.decode(), re.M | re.S)}


def ssml_blocks(raw):
    result, current = {}, None
    for node in ET.fromstring(raw):
        if node.tag.endswith('}mark'):
            current = node.get('name')
            if current in result:
                raise AssertionError('Duplicate source speech mark')
        elif node.tag.endswith('}p') and current is not None:
            result[current] = ''.join(node.itertext())
            current = None
    return result


class EqualitySourceTests(unittest.TestCase):
    def test_exact_36_total_ids_35_new_ids_and_23_mathml(self):
        self.assertEqual(len(set(EXPECTED_IDS)), 36)
        previous = ET.parse(LANG / 'translation/a10-operation-symbols.id-academic.cnxml').getroot()
        previous_ids = {node.get('id') for node in previous.iter() if node.get('id')}
        self.assertEqual(set(EXPECTED_IDS) & previous_ids, {SECTION})
        self.assertEqual(len(set(EXPECTED_IDS) - previous_ids), 35)
        descriptor = draft_units.UNITS[UNIT]
        self.assertEqual((descriptor['module'], descriptor['section'], descriptor['slice']),
                         (MODULE, SECTION, [13, 23]))
        for track in TRACKS:
            root = variant(track)
            self.assertEqual([node.get('id') for node in root.iter() if node.get('id')], EXPECTED_IDS)
            self.assertEqual(len(list(root.iter('{' + MATH + '}math'))), 23)
            self.assertEqual([node.get('id') for node in root if node.get('id')],
                             [SPACE, 'fs-id1170655208137', EQUALITY, 'fs-id1170655108736',
                              DIAGRAMS, REVERSALS, TABLE, EXAMPLE, *PRACTICES])

    def test_all_exact_fixtures_dispatch_once_and_preserve_semantics(self):
        specification, source = rules(), variant('id-academic')
        fixtures = specification['math_fixtures']
        self.assertEqual(len(fixtures), 23)
        self.assertEqual([row['id'] for row in fixtures], [f'A10-EQ-M{i:02}' for i in range(1, 24)])
        self.assertEqual(len({(row['anchor'], row['math_ordinal']) for row in fixtures}), 23)
        for track in TRACKS:
            root = variant(track)
            dispatched = build_units.source_bound_math(root, specification, track, source)
            self.assertEqual(len(dispatched), 23)
            for row, formula in zip(fixtures, FORMULAS):
                expression = math_at(root, row['anchor'], row['math_ordinal'])
                self.assertEqual(dispatched[id(expression)], row['expected'][track])
                if formula is not None:
                    tokens = [node.text for node in expression.iter()
                              if node.tag in {'{' + MATH + '}' + tag for tag in ('mi', 'mn', 'mo')}]
                    self.assertEqual(tokens, formula.split())
                    self.assertEqual(dispatched[id(expression)], reading(formula, track))
            glyph = math_at(root, EQUALITY, 2)
            self.assertEqual(dispatched[id(glyph)], 'tandha padha karo' if track.startswith('jv') else 'tanda sama dengan')
            for ordinal, symbol, direction in ((1, '<', 'kiwa'), (2, '>', 'tengen')):
                relation = reading('a ' + symbol + ' b', track)
                if track == 'jv-academic':
                    expected = relation.capitalize() + '. Diwaca: ' + relation + '. Aksara a mapan ing sisih ' + direction + ' aksara be ing garis wilangan.'
                elif track == 'jv-conversation':
                    expected = relation.capitalize() + '. Wacane: ' + relation + '. Aksara a ana ing ' + direction + ' aksara be ing garis wilangan.'
                else:
                    direction_id = 'kiri' if ordinal == 1 else 'kanan'
                    expected = relation.capitalize() + '. Dibaca: ' + relation + '. Huruf a berada di sebelah ' + direction_id + ' huruf be pada garis bilangan.'
                self.assertEqual(dispatched[id(math_at(root, ordinal=ordinal))], expected)

    def test_two_layout_trees_keep_empty_rows_and_cell_attributes(self):
        for track in TRACKS:
            layouts = [math_at(variant(track), ordinal=i).find('.//{' + MATH + '}mtable') for i in (1, 2)]
            self.assertEqual([[len(row) for row in table] for table in layouts], [[0, 0, 1, 1], [1, 1]])
            for table in layouts:
                self.assertEqual(table.attrib, {})
                self.assertTrue(all(row.tag == '{' + MATH + '}mtr' and row.attrib == {} for row in table))
                self.assertTrue(all(cell.attrib == {'columnalign':'left'} for cell in table.iter('{' + MATH + '}mtd')))
                self.assertTrue(all(space.attrib == {'width':'0.2em'} for space in table.iter('{' + MATH + '}mspace')))

    def test_source_tree_mutations_fail_closed(self):
        for kind in ('anchor', 'operand', 'operator', 'mtext', 'empty-row', 'row-order',
                     'mtable-attribute', 'mtr-attribute', 'mtd-attribute', 'space-width', 'wrapper'):
            changed = variant('id-academic')
            expression = math_at(changed)
            table = expression.find('.//{' + MATH + '}mtable')
            if kind == 'anchor':
                anchor(changed, DIAGRAMS).set('id', 'unregistered-anchor')
            elif kind in ('operand', 'operator', 'mtext'):
                tag, value = {'operand':('mi', 'b'), 'operator':('mo', '>'), 'mtext':('mtext', 'unregistered')}[kind]
                expression.find('.//{' + MATH + '}' + tag).text = value
            elif kind == 'empty-row':
                table.remove(table[0])
            elif kind == 'row-order':
                table[2], table[3] = table[3], table[2]
            elif kind == 'mtable-attribute':
                table.set('columnspacing', '1em')
            elif kind == 'mtr-attribute':
                table[0].set('rowalign', 'top')
            elif kind == 'mtd-attribute':
                table.find('.//{' + MATH + '}mtd').set('columnalign', 'right')
            elif kind == 'space-width':
                expression.find('.//{' + MATH + '}mspace').set('width', '0.3em')
            else:
                wrapper = ET.Element('{' + MATH + '}mrow')
                wrapper[:] = list(expression)
                expression[:] = [wrapper]
            for track in TRACKS:
                with self.subTest(kind=kind, track=track), self.assertRaisesRegex(ValueError, 'unsupported_source_bound_narration'):
                    build_units.source_bound_math(changed, rules(), track)

    def test_translated_operator_attribute_and_ordinal_mutations_fail_closed(self):
        source = variant('id-academic')
        for kind in ('operator', 'attribute', 'ordinal'):
            target = variant('jv-academic')
            if kind == 'operator':
                math_at(target).find('.//{' + MATH + '}mo').text = '>'
            elif kind == 'attribute':
                math_at(target).find('.//{' + MATH + '}mtd').set('columnalign', 'right')
            else:
                first, second = math_at(target, TABLE, 1), math_at(target, TABLE, 2)
                first[:], second[:] = list(second), list(first)
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, 'unsupported_translated_math_narration'):
                build_units.source_bound_math(target, rules(), 'jv-academic', source)

    def test_duplicate_and_unused_fixture_mutations_are_rejected(self):
        for kind in ('duplicate', 'unused'):
            changed = rules()
            addition = copy.deepcopy(changed['math_fixtures'][0])
            if kind == 'unused':
                addition['anchor'] = 'not-in-this-unit'
            changed['math_fixtures'].append(addition)
            with self.subTest(kind=kind), self.assertRaises(AssertionError):
                build_units.source_bound_math(variant('id-academic'), changed, 'id-academic')


class EqualityNarrationTests(unittest.TestCase):
    def bodies(self, track):
        return dict(build_units.blocks(variant(track), track, UNIT, rules(), variant('id-academic')))

    def test_plain_reversals_keep_both_operands_relation_and_equivalence(self):
        relations = [('a < b', 'b > a'), ('7 < 11', '11 > 7'),
                     ('a > b', 'b < a'), ('17 > 4', '4 < 17')]
        for track in TRACKS:
            root = variant(track)
            visible = normalized(''.join(anchor(root, REVERSALS).itertext()))
            for left, right in relations:
                self.assertIn(left, visible)
                self.assertIn(right, visible)
            equivalence = {'jv-academic':'padha tegese karo', 'jv-conversation':'tegese padha karo',
                           'id-academic':'setara dengan'}[track]
            body, cursor = self.bodies(track)[REVERSALS], 0
            for left, right in relations:
                expected = reading(left, track) + ' ' + equivalence + ' ' + reading(right, track)
                self.assertEqual(body.count(expected), 1)
                cursor = body.index(expected, cursor) + len(expected)
            self.assertNotRegex(body, r'[<>=]|\bb\b|(?:aksara|huruf) (?:aksara|huruf)')

    def test_table_plain_a_greater_b_is_read_with_headers_and_named_letters(self):
        for track in TRACKS:
            root, body = variant(track), self.bodies(track)[TABLE]
            rows = anchor(root, TABLE).findall('.//{*}tbody/{*}row')
            self.assertEqual(len(rows), 5)
            self.assertEqual(rows[3][0][0].text, 'a > b')
            lines = body.splitlines()
            self.assertEqual(len(lines), 6)
            self.assertEqual(lines[0], 'Tabel.')
            for line, symbol in zip(lines[1:], ('≠', '<', '≤', '>', '≥')):
                expected = reading('a ' + symbol + ' b', track)
                self.assertEqual(line.count(expected), 2)
                self.assertEqual(line.count(': '), 2)
            self.assertNotRegex(body, r'[<>=≠≤≥]|\bb\b|(?:aksara|huruf) (?:aksara|huruf)')

    def test_equality_glyph_name_is_not_doubled_and_xml_is_unchanged(self):
        for track in TRACKS:
            root = variant(track)
            before = ET.tostring(root)
            body = dict(build_units.blocks(root, track, UNIT, rules(), variant('id-academic')))[EQUALITY]
            self.assertNotRegex(body.lower(), r'tandha tandha|simbol tanda|simbol tandha')
            self.assertEqual(body.count(reading('a = b', track)), 2)
            prefix = 'Tandha padha karo jenenge' if track == 'jv-conversation' else (
                'Simbol padha karo diarani' if track == 'jv-academic' else 'Simbol sama dengan disebut')
            self.assertIn(prefix, body)
            self.assertEqual(ET.tostring(root), before)

    def test_diagram_point_order_and_mathematical_relation_agree(self):
        specification = rules()
        fixtures = [row for row in specification['diagram_rules'] if row.get('source_media')]
        self.assertEqual([row['source_media'] for row in fixtures], [row[0] for row in IMAGES])
        for track in TRACKS:
            root = variant(track)
            body = self.bodies(track)[DIAGRAMS]
            for index, row in enumerate(fixtures):
                media = anchor(root, row['source_media'])
                expected = row['expected'][track]
                self.assertEqual(build_units.narrate(media, track, UNIT, {}, specification), expected)
                self.assertEqual(body.count(expected), 1)
                left, right = ('a', 'b') if index == 0 else ('b', 'a')
                # Visible alt keeps source mathematical identifiers, not phonetic rewrites.
                self.assertLess(media.get('alt').index('titik ' + left), media.get('alt').index('titik ' + right))
                left_spoken, right_spoken = ('titik ' + reading(token, track) for token in (left, right))
                self.assertLess(expected.index(left_spoken), expected.index(right_spoken))
                self.assertNotRegex(expected, r'\bb\b|titik [ab]\b')
                self.assertIn('kiwa' if track.startswith('jv') else 'kiri', expected)
                self.assertIn(reading('a < b' if index == 0 else 'a > b', track), expected)
            self.assertLess(body.index(fixtures[0]['expected'][track]), body.index(fixtures[1]['expected'][track]))

    def test_unregistered_diagram_and_unexpected_empty_block_are_rejected(self):
        for kind in ('diagram', 'empty-block'):
            root = variant('jv-academic')
            if kind == 'diagram':
                anchor(root, IMAGES[0][0]).set('id', 'unregistered-media')
            else:
                anchor(root, 'fs-id1170655208137').clear()
            with self.subTest(kind=kind), self.assertRaises((ValueError, AssertionError)):
                build_units.blocks(root, 'jv-academic', UNIT, rules(), variant('id-academic'))

    def test_part_a_through_d_labels_and_two_answer_cues(self):
        for track in TRACKS:
            bodies = self.bodies(track)
            label = 'bagean ' if track.startswith('jv') else 'bagian '
            cue = 'Wangsulan.' if track.startswith('jv') else 'Jawaban.'
            for source_id in (EXAMPLE, *PRACTICES):
                body = bodies[source_id]
                labels = re.findall(re.escape(label) + r'(a|be|ce|de):', body)
                self.assertEqual(labels, ['a', 'be', 'ce', 'de'] * 2)
                self.assertNotRegex(body, r'[ⓐⓑⓒⓓ]|\b(?:bagean|bagian) [bcd]:')
                self.assertEqual(body.count(cue), 0 if source_id == EXAMPLE else 1)
                if source_id in PRACTICES:
                    question, answer = body.split(cue)
                    self.assertEqual(question.count(label + 'ce:'), 1)
                    self.assertEqual(answer.count(label + 'de:'), 1)
            self.assertEqual(sum(body.count(cue) for body in bodies.values()), 2)


class EqualityProductsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Guard every relevant writer for the whole class, including failed tests.
        cls.writer_patches = [patch.object(module, 'write_bytes', side_effect=AssertionError('Forbidden test write'))
                              for module in (build_units, draft_units, asset_builder)]
        for guard in cls.writer_patches:
            guard.start()
            cls.addClassCleanup(guard.stop)
        cls.draft = draft_units.products(UNIT)
        cls.generated = build_units.products(UNIT)
        cls.assets = asset_builder.products()

    def test_draft_asset_and_build_products_are_current_and_deterministic(self):
        for first, second in ((self.draft, draft_units.products(UNIT)),
                              (self.assets, asset_builder.products()),
                              (self.generated, build_units.products(UNIT))):
            self.assertEqual(first, second)
            for path, raw in first.items():
                self.assertEqual((LANG / path).read_bytes(), raw, path)
        self.assertEqual(len(self.generated), 8)
        self.assertEqual(len(self.assets), 3, 'Exactly two JPEGs and one manifest; no track-specific duplicates')

    def test_two_source_images_and_six_embedded_images_keep_exact_bytes(self):
        manifest = json.loads(self.assets[f'translation/{UNIT}.assets.json'])
        self.assertEqual(len(manifest['assets']), 2)
        reader = Reader()
        reader.feed(self.generated[f'review/units/{UNIT}.html'].decode())
        self.assertEqual(len(reader.images), 6)
        embedded = [base64.b64decode(row['src'].split(',', 1)[1], validate=True) for row in reader.images]
        for record, (media_id, name, size, digest) in zip(manifest['assets'], IMAGES):
            self.assertEqual(record['media_id'], media_id)
            self.assertEqual(record['source_src'], '../../media/' + name)
            raw = self.assets[f'translation/assets/{UNIT}/{name}']
            self.assertEqual((len(raw), sha(raw)), (size, digest))
            self.assertEqual(asset_builder.dimensions(raw), {'width':192, 'height':37})
            self.assertEqual(embedded.count(raw), 3)
            for track in TRACKS:
                self.assertEqual(record['outputs'][track]['sha256'], digest)
                self.assertEqual(record['outputs'][track]['derivative_type'], 'source-byte-retention')
                self.assertEqual(record['outputs'][track]['locale'], 'zxx')

    def test_reader_preserves_spacing_anchor_but_ssml_has_no_empty_paragraph(self):
        reader = Reader()
        reader.feed(self.generated[f'review/units/{UNIT}.html'].decode())
        self.assertEqual(reader.maths, 69)
        self.assertEqual(len(reader.ids), len(set(reader.ids)))
        self.assertEqual(len(reader.heads), 6)
        self.assertTrue(all(header.get('scope') == 'col' for header in reader.heads))
        for track, (locale, _) in TRACKS.items():
            self.assertIn(UNIT + '--' + track + '--' + SPACE, reader.ids)
            self.assertTrue(all(UNIT + '--' + track + '--' + source_id in reader.ids for source_id in EXPECTED_IDS))
            raw = self.generated[f'review/audio/{UNIT}.{track}.ssml']
            document = ET.fromstring(raw)
            self.assertEqual(document.get(XML_LANG), locale)
            self.assertTrue(all(''.join(node.itertext()).strip() for node in document.findall('{*}p')))
            self.assertNotIn(MODULE + '--' + SPACE, ssml_blocks(raw))
            expected = {MODULE + '--' + key: text for key, text in build_units.blocks(
                variant(track), track, UNIT, rules(), variant('id-academic'))}
            self.assertEqual(len(expected), 10, 'Title plus nine nonempty instructional blocks')
            self.assertEqual(ssml_blocks(raw), expected)
            self.assertEqual(transcript_blocks(self.generated[f'review/audio/{UNIT}.{track}.md']), expected)

    def test_stale_plain_relation_and_media_reference_mutations_fail_draft_gate(self):
        target = LANG / f'translation/{UNIT}.jv-academic.cnxml'
        original_read = Path.read_bytes
        for kind in ('plain-relation', 'media-reference', 'point-order-alt', 'part-label'):
            changed = variant('jv-academic')
            if kind == 'plain-relation':
                node = anchor(changed, TABLE).findall('.//{*}tbody/{*}row')[3][0][0]
                node.text = 'a < b'
            elif kind == 'media-reference':
                anchor(changed, IMAGES[0][0])[0].set('src', '../../media/' + IMAGES[1][1])
            elif kind == 'point-order-alt':
                anchor(changed, IMAGES[0][0]).set('alt', anchor(changed, IMAGES[1][0]).get('alt'))
            else:
                marker = next(node for node in changed.iter('{' + CN + '}span') if node.text == 'ⓒ')
                marker.text = 'ⓓ'
            changed_bytes = ET.tostring(changed, encoding='utf-8', xml_declaration=True) + b'\n'
            def mutated_read(path, raw=changed_bytes):
                return raw if path == target else original_read(path)
            with self.subTest(kind=kind), patch.object(Path, 'read_bytes', mutated_read), self.assertRaisesRegex(AssertionError, 'Stale source-bound draft'):
                build_units.products(UNIT)

    def test_corrupt_asset_bytes_are_rejected_without_writing(self):
        target = LANG / f'translation/assets/{UNIT}/{IMAGES[0][1]}'
        original_read = Path.read_bytes
        corrupted = bytearray(target.read_bytes())
        corrupted[-10] ^= 1
        def mutated_read(path):
            return bytes(corrupted) if path == target else original_read(path)
        with patch.object(Path, 'read_bytes', mutated_read), self.assertRaises(AssertionError):
            build_units.products(UNIT)

    def test_receipt_hashes_and_human_review_limits_are_honest(self):
        receipt = json.loads(self.generated[f'qa/{UNIT}.build-receipt.json'])
        self.assertEqual((receipt['source_ids'], receipt['source_math_expressions'], receipt['source_media_references']), (36, 23, 2))
        self.assertEqual(receipt['nonspoken_source_blocks'], [SPACE])
        self.assertEqual(receipt['source_draft_receipt_sha256'], sha(self.draft[f'qa/{UNIT}.draft-receipt.json']))
        self.assertEqual(receipt['rules_sha256'], sha((LANG / f'audio/{UNIT}.rules.json').read_bytes()))
        self.assertEqual(receipt['asset_manifest_sha256'], sha(self.assets[f'translation/{UNIT}.assets.json']))
        self.assertEqual(receipt['output_sha256'], {path:sha(raw) for path, raw in self.generated.items() if path.startswith('review/')})
        self.assertTrue({'exact_source_tree_math_fixtures', 'translated_linguistic_mtext_only',
                         'relation_diagram_and_plain_notation_readings', 'spacing_source_node_preserved'} <= set(receipt['checks']))
        self.assertTrue({'long_division_operand_order', 'cross_variable_and_ellipsis_contexts'}.isdisjoint(receipt['checks']))
        for field in ('human_language_review', 'visual_review', 'listening_review', 'whole_module_complete'):
            self.assertFalse(receipt[field])
        self.assertEqual(receipt['synthesized_audio_files'], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
