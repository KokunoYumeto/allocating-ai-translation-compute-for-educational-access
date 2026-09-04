"""Fail-closed contracts for the complete A10 order-of-operations section.

This module deliberately has no generic mathematical, table, image, language,
or voice fallback.  Every non-prose readout is bound to the exact source tree
and fixed handoff fixture that authorized it.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from build import CN, MATH, XML_LANG, local, translated
from build_units import fixture_element, tree_key
from config import LANG, ROOT
from draft_units import merged_edits
from qa import identity

UNIT = 'a10-order-operations'
MODULE = 'm82453'
SECTION = 'fs-id1170654953465'
NEXT_SECTION = 'fs-id1170654889475'
NEXT_FIRST_PARAGRAPH = 'fs-id1170654968998'
TRACKS = ('jv-academic', 'jv-conversation', 'id-academic')
LOCALES = {'jv-academic': 'jv-Latn-ID', 'jv-conversation': 'jv-Latn-ID', 'id-academic': 'id-ID'}
ID_SOURCE = ROOT / 'downloads/jv-Latn-ID/a10-source/translated/modules/m82453/index.cnxml'
EN_SOURCE = ROOT / 'downloads/jv-Latn-ID/a10-source/authority/source/modules/m82453/index.cnxml'
RULES_PATH = LANG / f'audio/{UNIT}.rules.json'
EDITS_PATH = LANG / f'translation/{UNIT}.edits.json'
SHARED_EDITS_PATH = LANG / 'translation/phrases.json'

ID_MODULE_SHA256 = '2c0b688d569044b128d589579e9ba7d871a0fb9ac7a670ac6f22d0ef2b66e635'
EN_MODULE_SHA256 = 'a8fdd235aa254c5a0a1248fa858e9b3579d9b40982bbc514cbe6a18c3e6fcbed'
RULES_SHA256 = '84b0a2f114bad14228ae9af8583c8654b5c6cd8052d7c5d41725f0041fd35e86'
EDITS_SHA256 = 'ad35129451826eab5a414a6b4c436ad4a4fd675356f6497f32d468bcd5cb8aa5'
SHARED_EDITS_SHA256 = 'adc145f5957bf18281cd737b9e1079af4d24f6d5505c9485138de3018b2ab5b8'
SOURCE_TREE_SHA256 = 'd0b2d0a31eb3971ba2ed241ce241072db123220b31a4d7813469ac96a941dcd1'
TARGET_TREE_SHA256 = {
    'id-academic': SOURCE_TREE_SHA256,
    'jv-academic': '096051037734d427e7e1d346bb4168f59d341c56e51bf71613001ad4397058de',
    'jv-conversation': '1f131d873e2763eccc27033138cf997bba56b4d50293b253ff4842eb073a2768',
}
SOURCE_LOCK_SHA256 = '27259f1bdafac170ec4476192d142a1a7dfbc6da7b238099338f329e955432eb'


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def tree_sha(node: ET.Element) -> str:
    return sha(tree_key(node).encode())


def normalized(text: str | None) -> str:
    return re.sub(r'\s+', ' ', text or '').strip()


def exact_json_digest(value) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    return sha(raw)


def load_rules() -> dict:
    raw = RULES_PATH.read_bytes()
    assert sha(raw) == RULES_SHA256, 'Changed order-of-operations narration handoff'
    rules = json.loads(raw)
    assert rules['scope']['unit'] == UNIT and rules['scope']['module'] == MODULE
    assert rules['scope']['section'] == SECTION and rules['tracks'] == list(TRACKS)
    assert rules['locales'] == LOCALES
    return rules


def load_edits() -> dict:
    assert sha(EDITS_PATH.read_bytes()) == EDITS_SHA256, 'Changed order-of-operations edit handoff'
    assert sha(SHARED_EDITS_PATH.read_bytes()) == SHARED_EDITS_SHA256, 'Changed shared phrase pivot'
    edits = json.loads(EDITS_PATH.read_text(encoding='utf-8'))
    assert edits['unit'] == UNIT and edits['source_module'] == MODULE and edits['source_section'] == SECTION
    assert edits['direct_child_slice_zero_based'] is None
    return edits


def _section(document: ET.Element, section_id: str) -> ET.Element:
    matches = [node for node in document.iter() if node.get('id') == section_id]
    assert len(matches) == 1, f'Expected one source section {section_id}'
    result = copy.deepcopy(matches[0])
    result.tail = None
    return result


def source_sections() -> tuple[ET.Element, ET.Element]:
    id_raw, en_raw = ID_SOURCE.read_bytes(), EN_SOURCE.read_bytes()
    assert sha(id_raw) == ID_MODULE_SHA256 and sha(en_raw) == EN_MODULE_SHA256
    id_document, en_document = ET.fromstring(id_raw), ET.fromstring(en_raw)
    source, english = _section(id_document, SECTION), _section(en_document, SECTION)
    assert tree_sha(source) == SOURCE_TREE_SHA256
    # Prove the excluded cursor is the immediate next sibling in both pinned modules.
    for document in (id_document, en_document):
        parent = next(node for node in document.iter() if any(child.get('id') == SECTION for child in node))
        index = next(i for i, child in enumerate(parent) if child.get('id') == SECTION)
        assert parent[index + 1].get('id') == NEXT_SECTION
        assert next(node.get('id') for node in parent[index + 1] if node.get('id')) == NEXT_FIRST_PARAGRAPH
    return source, english


def variants(source: ET.Element | None = None) -> dict[str, ET.Element]:
    source = source if source is not None else source_sections()[0]
    load_edits()
    edits = merged_edits(UNIT)
    result = {
        'id-academic': copy.deepcopy(source),
        'jv-academic': translated(source, 'jv-academic', edits),
        'jv-conversation': translated(source, 'jv-conversation', edits),
    }
    rules = load_rules()
    for track in TRACKS:
        validate_scope(source, result[track], rules, track)
    return result


def _source_fixture(text: str) -> ET.Element:
    return ET.fromstring(text)


def _nodes(root: ET.Element) -> dict[str, ET.Element]:
    nodes = [node for node in root.iter() if node.get('id')]
    assert len(nodes) == len({node.get('id') for node in nodes}), 'Duplicate source ID'
    return {node.get('id'): node for node in nodes}


def visible_math(node: ET.Element) -> str:
    tag = local(node)
    if tag == 'msup':
        assert len(node) == 2
        return visible_math(node[0]) + '^' + visible_math(node[1])
    if tag == 'mspace':
        return ''
    if not len(node):
        return node.text or ''
    return (node.text or '') + ''.join(visible_math(child) + (child.tail or '') for child in node)


def _validate_corrections(source: ET.Element, target: ET.Element, rules: dict, track: str) -> None:
    edits = load_edits()
    edit_rows = edits['target_only_accessibility_corrections']
    rule_rows = rules['accessible_description_policy']['target_attribute_exceptions']
    assert len(edit_rows) == len(rule_rows) == 6
    assert [(row['phrase_index_zero_based'], row['element_id'], row['attribute']) for row in edit_rows] == [
        (68, 'fs-id1167829713618', 'aria-label'),
        (70, 'fs-id1167824617198', 'alt'),
        (72, 'fs-id1167836329648', 'alt'),
        (75, 'fs-id1167836375645', 'aria-label'),
        (80, 'fs-id1171791418206', 'alt'),
        (89, 'fs-id1167829840981', 'aria-label'),
    ]
    source_nodes, target_nodes = _nodes(source), _nodes(target)
    charts = {row['primary_asset']['filename']: row for row in rules['chart_fixtures']}
    numeric_exception_keys = set()
    for edit_row, rule_row in zip(edit_rows, rule_rows):
        for field in ('phrase_index_zero_based', 'element_id', 'attribute', 'source_digit_sequence',
                      'target_digit_sequences', 'primary_media', 'previous_targets'):
            assert edit_row[field] == rule_row[field], f'Correction handoffs disagree: {field}'
        index, element_id, attribute = (edit_row[key] for key in ('phrase_index_zero_based', 'element_id', 'attribute'))
        phrase_row = edits['phrases'][index]
        assert source_nodes[element_id].get(attribute) == phrase_row[0]
        expected = phrase_row[edits['tracks'].index(track) + 1] if track != 'id-academic' else phrase_row[0]
        assert target_nodes[element_id].get(attribute) == expected
        if track != 'id-academic':
            assert rule_row['expected_target_values'][track] == expected
            assert rule_row['validation_exception_scope'].endswith('no global numeric relaxation.')
        for media in edit_row['primary_media']:
            chart = charts[media['filename']]
            assert media['sha256'] == chart['primary_asset']['sha256']
            assert media['git_blob_sha1'] == chart['primary_asset']['git_blob_sha1']
        target_digits = (edit_row['source_digit_sequence'] if track == 'id-academic'
                         else edit_row['target_digit_sequences'][track])
        if edit_row['source_digit_sequence'] != target_digits:
            numeric_exception_keys.add((element_id, attribute))
    expected_numeric = set() if track == 'id-academic' else {
        ('fs-id1167836329648', 'alt'),
        ('fs-id1167836375645', 'aria-label'),
        ('fs-id1167829840981', 'aria-label'),
    }
    assert numeric_exception_keys == expected_numeric

    differences = set()
    for left, right in zip(source.iter(), target.iter()):
        assert left.tag == right.tag
        for slot, left_value, right_value in [
            ('text', left.text or '', right.text or ''), ('tail', left.tail or '', right.tail or ''),
            *[(attribute, left.get(attribute, ''), right.get(attribute, ''))
              for attribute in ('alt', 'aria-label', 'summary')],
        ]:
            left_digits = re.findall(r'\d+(?:\.\d+)?', left_value)
            right_digits = re.findall(r'\d+(?:\.\d+)?', right_value)
            if left_digits == right_digits:
                continue
            key = (left.get('id'), slot)
            assert key in expected_numeric, f'Unregistered numeric-sequence change: {key}'
            correction = next(row for row in edit_rows if (row['element_id'], row['attribute']) == key)
            assert left_digits == correction['source_digit_sequence']
            assert right_digits == correction['target_digit_sequences'][track]
            differences.add(key)
    assert differences == expected_numeric, 'Numeric exceptions were broadened or not exercised'


def _validate_fixtures(source: ET.Element, target: ET.Element, rules: dict, track: str) -> None:
    source_nodes, target_nodes = _nodes(source), _nodes(target)
    source_blocks = {node.get('id'): node for node in source if node.get('id')}
    target_blocks = {node.get('id'): node for node in target if node.get('id')}

    indexed = {(row['anchor'], row['math_ordinal']): row for row in rules['math_fixtures']}
    assert len(indexed) == len(rules['math_fixtures']) == 21
    seen = set()
    for anchor, block in source_blocks.items():
        target_block = target_blocks[anchor]
        source_math = list(block.iter('{' + MATH + '}math'))
        target_math = list(target_block.iter('{' + MATH + '}math'))
        assert len(source_math) == len(target_math)
        for ordinal, (left, right) in enumerate(zip(source_math, target_math), 1):
            key = (anchor, ordinal)
            assert key in indexed, f'Unregistered MathML occurrence: {key}'
            fixture = indexed[key]
            expected_source = fixture_element(fixture['source_mathml'])
            assert tree_key(left) == tree_key(expected_source)
            assert tree_sha(left) == fixture['source_tree_sha256']
            assert tree_sha(right) == fixture['expected_target_tree_sha256'][track]
            assert fixture['expected'][track] == '' if fixture['id'] == 'A10-ORD-M16' else bool(fixture['expected'][track])
            seen.add(key)
    assert seen == set(indexed)

    for group, id_field in (('prose_fixtures', 'element_id'), ('table_fixtures', 'table_id'),
                            ('chart_fixtures', 'media_id')):
        fixtures = rules[group]
        assert len(fixtures) == len({row[id_field] for row in fixtures})
        for fixture in fixtures:
            element_id = fixture[id_field]
            expected_source = _source_fixture(fixture['source_cnxml'])
            assert tree_key(source_nodes[element_id]) == tree_key(expected_source)
            assert tree_sha(source_nodes[element_id]) == fixture['source_tree_sha256']
            assert tree_sha(target_nodes[element_id]) == fixture['expected_target_tree_sha256'][track]
            for attribute, value in fixture.get('target_linguistic_attributes', {}).get(track, {}).items():
                assert target_nodes[element_id].get(attribute) == value

    assert len(rules['prose_fixtures']) == 11
    assert all(row['override_before_child_narration'] is True for row in rules['prose_fixtures'])
    tables = rules['table_fixtures']
    assert len(tables) == 4 and [len(row['source_rows']) for row in tables] == [7, 6, 8, 14]
    assert sum(len(row['source_rows']) for row in tables) == 35
    for fixture in tables:
        table = source_nodes[fixture['table_id']]
        tgroup, rows = table.find('{*}tgroup'), table.findall('.//{*}tbody/{*}row')
        shape = fixture['source_shape']
        assert tgroup.get('cols') == str(shape['declared_columns']) == '2'
        assert table.find('.//{*}thead') is None and len(rows) == shape['body_rows']
        assert [len(row) for row in rows] == shape['actual_entries_per_row']
        assert table.get('class') == shape['class'] and table.get('aria-label') == fixture['source_aria_label']
        assert fixture['source_summary'] is None and len(fixture['row_fixtures']) == len(rows)
    assert {node.get('id') for node in source.iter('{' + CN + '}table')} == {row['table_id'] for row in tables}

    charts = rules['chart_fixtures']
    assert len(charts) == 23
    assert {node.get('id') for node in source.iter('{' + CN + '}media')} == {row['media_id'] for row in charts}
    for fixture in charts:
        media = source_nodes[fixture['media_id']]
        image = media.find('{*}image')
        assert media.get('alt') == fixture['source_alt']
        assert image.get('src') == fixture['source_image']
        assert image.get('mime-type') == 'image/png'
        assert Path(image.get('src')).name == fixture['primary_asset']['filename']
        assert fixture['primary_asset']['actual_mime'] == 'image/jpeg'
        assert fixture['retain_source_bytes'] is True and fixture['derivative_required'] is False
        assert fixture['linguistic_labels_present'] is False and fixture['color_independent_readout'] is True
    nonspoken = rules['nonspoken_source_math']
    assert len(nonspoken) == 1 and nonspoken[0]['fixture_id'] == 'A10-ORD-M16'
    assert nonspoken[0]['expected'] == {track_name: '' for track_name in TRACKS}
    assert rules['nonspoken_source_blocks'] == [] and rules['reference_fixtures'] == []


def validate_answers(source: ET.Element, rules: dict) -> None:
    expected_checks = [
        ('fs-id1170654954598', ['4+3·7', '(4+3)·7'], ['25', '49']),
        ('fs-id1170654936731', ['12−5·2', '(12−5)·2'], ['2', '14']),
        ('fs-id1170655164725', ['8+3·9', '(8+3)·9'], ['35', '99']),
        ('fs-id1170654942988', ['18÷6+4(5−2)'], ['15']),
        ('fs-id1170655117790', ['30÷5+10(3−2)'], ['16']),
        ('fs-id1170654928204', ['70÷10+4(6−2)'], ['23']),
        ('fs-id1170655174686', ['5+2^3+3[6−3(4−2)]'], ['13']),
        ('fs-id1170655222647', ['9+5^3−[4(9+3)]'], ['86']),
        ('fs-id1170654942628', ['7^2−2[4(5+1)]'], ['1']),
    ]
    checks = rules['answer_policy']['exercise_checks']
    assert [(row['exercise_id'], row['source_questions'], row['source_answers']) for row in checks] == expected_checks
    exercises = source.findall('.//{*}exercise')
    assert len(exercises) == 9 and [node.get('id') for node in exercises] == [row[0] for row in expected_checks]
    assert sum(len(row[1]) for row in expected_checks) == sum(len(row[2]) for row in expected_checks) == 12
    for exercise, (_, questions, _) in zip(exercises, expected_checks):
        problem = exercise.find('{*}problem')
        actual = [visible_math(node).rstrip('.') for node in problem.iter('{' + MATH + '}math')]
        assert actual == questions
        assert exercise.find('{*}solution') is not None
    computed = [4 + 3*7, (4+3)*7, 12-5*2, (12-5)*2, 8+3*9, (8+3)*9,
                18//6+4*(5-2), 30//5+10*(3-2), 70//10+4*(6-2),
                5+2**3+3*(6-3*(4-2)), 9+5**3-4*(9+3), 7**2-2*4*(5+1)]
    assert [str(value) for value in computed] == [answer for _, _, answers in expected_checks for answer in answers]
    assert rules['answer_policy']['question_fixtures'] == [f'A10-ORD-M{i:02}' for i in range(8, 15)] + [f'A10-ORD-M{i:02}' for i in range(17, 22)]
    assert len(rules['answer_policy']['untitled_solution_cues']) == 6
    nodes = _nodes(source)
    for row in rules['answer_policy']['untitled_solution_cues']:
        solution = nodes[row['solution_id']]
        assert local(solution) == 'solution' and solution.find('{*}title') is None
        assert nodes[row['answer_paragraph']] in list(solution.iter())
    for solution_id in rules['answer_policy']['worked_solution_ids']:
        assert nodes[solution_id].find('{*}title') is not None
    assert rules['answer_policy']['worked_steps'] == [
        ['4+3·7', '4+3·7', '4+21', '25'],
        ['(4+3)·7', '(4+3)·7', '(7)7', '49'],
        ['18÷6+4(5−2)', '18÷6+4(3)', '18÷6+4(3)', '3+4(3)', '3+12', '15'],
        ['5+2^3+3[6−3(4−2)]', '5+2^3+3[6−3(4−2)]', '5+2^3+3[6−3(2)]',
         '5+2^3+3[6−6]', '5+2^3+3[0]', '5+2^3+3[0]', '5+8+3[0]', '5+8+0', '13+0', '13'],
    ]
    # The six untitled answer paragraphs are the only prose answer fixtures.
    assert [normalized(''.join(nodes[row['answer_paragraph']].itertext())) for row in rules['answer_policy']['untitled_solution_cues']] == [
        'ⓐ 2 ⓑ 14', 'ⓐ 35 ⓑ 99', '16', '23', '86', '1']
    chart_values = {row['id']: row['source_visible_expression'] for row in rules['chart_fixtures']}
    assert [chart_values[key] for key in ('A10-ORD-D04', 'A10-ORD-D08', 'A10-ORD-D13', 'A10-ORD-D23')] == ['25', '49', '15', '13']


def validate_scope(source: ET.Element, target: ET.Element, rules: dict, track: str) -> None:
    assert track in TRACKS, 'No language/register fallback'
    assert rules == load_rules(), 'Mutated narration rules are not authoritative'
    scope = rules['scope']
    assert scope['complete_section'] is True and scope['direct_child_slice_zero_based'] is None
    assert (scope['source_direct_children'], scope['source_ids_total'], scope['source_mathml_expression_count'],
            scope['source_msup_count'], scope['source_cnxml_tables'], scope['source_media'],
            scope['source_exercises'], scope['source_solutions'], scope['question_parts'], scope['source_links']) == (
                31, 111, 21, 3, 4, 23, 9, 9, 12, 0)
    assert len(source) == 31 and source[0].tag == '{' + CN + '}title'
    assert tree_sha(source) == scope['indonesian_section_canonical_sha256'] == SOURCE_TREE_SHA256
    assert tree_sha(target) == scope['target_section_canonical_sha256'][track] == TARGET_TREE_SHA256[track]
    assert sha(EDITS_PATH.read_bytes()) == scope['edits_sha256'] == EDITS_SHA256
    assert sha(SHARED_EDITS_PATH.read_bytes()) == scope['shared_edits_sha256'] == SHARED_EDITS_SHA256
    assert sha((LANG / 'sources.lock.json').read_bytes()) == scope['source_lock_sha256'] == SOURCE_LOCK_SHA256
    assert source.get('id') == target.get('id') == SECTION and NEXT_SECTION not in _nodes(source)
    ids = [node.get('id') for node in source.iter() if node.get('id')]
    assert len(ids) == 111 and len(ids) == len(set(ids)) and ids[-1] == scope['last_descendant_id']
    assert source[1].get('id') == scope['first_top_level_anchor'] and source[-1].get('id') == scope['last_top_level_anchor']
    assert all(node.get('target-id') in ids for node in source.iter() if node.get('target-id'))
    assert identity(source) == identity(target)
    replay = copy.deepcopy(source) if track == 'id-academic' else translated(source, track, merged_edits(UNIT))
    assert tree_key(target) == tree_key(replay), 'Target is not the exact declared phrase replay'
    assert (target.get(XML_LANG) == 'jv-Latn-ID') == track.startswith('jv')
    assert len(list(source.iter('{' + MATH + '}math'))) == 21
    assert len(list(source.iter('{' + MATH + '}msup'))) == 3
    assert len(list(source.iter('{' + MATH + '}mfrac'))) == 0
    assert len(source.findall('.//{*}table')) == 4 and len(source.findall('.//{*}media')) == 23
    assert len(source.findall('.//{*}exercise')) == len(source.findall('.//{*}solution')) == 9
    assert len(source.findall('.//{*}link')) == 0
    _validate_corrections(source, target, rules, track)
    _validate_fixtures(source, target, rules, track)
    validate_answers(source, rules)


class BoundContext:
    """Live-node authority: copied IDs and post-binding mutations do not inherit speech."""
    def __init__(self, root: ET.Element, source: ET.Element, rules: dict, track: str):
        self.root = root
        self.source = source
        self.track = track
        self.rules_digest = exact_json_digest(rules)
        self.nodes = {id(node): (node, tree_key(node)) for node in root.iter()}
        self.math: dict[int, str] = {}
        self.context_only: set[int] = set()
        self.prose = {row['element_id']: row['expected'][track] for row in rules['prose_fixtures']}
        self.tables = {row['table_id']: row['expected'][track] for row in rules['table_fixtures']}
        self.media = {row['media_id']: row['expected'][track] for row in rules['chart_fixtures']}


def bind(root: ET.Element, source: ET.Element, rules: dict, track: str) -> BoundContext:
    validate_scope(source, root, rules, track)
    bound = BoundContext(root, source, rules, track)
    indexed = {(row['anchor'], row['math_ordinal']): row for row in rules['math_fixtures']}
    used = set()
    for block in root:
        for ordinal, expression in enumerate(block.iter('{' + MATH + '}math'), 1):
            key = (block.get('id'), ordinal)
            assert key in indexed
            fixture = indexed[key]
            bound.math[id(expression)] = fixture['expected'][track]
            if fixture.get('standalone_readout_authorized') is False or not fixture['expected'][track]:
                bound.context_only.add(id(expression))
            used.add(key)
    assert used == set(indexed) and len(bound.math) == 21
    return bound


def _require_bound(element: ET.Element, track: str, bound: BoundContext, rules: dict) -> None:
    assert isinstance(bound, BoundContext) and bound.track == track and track in TRACKS, 'No track fallback'
    assert exact_json_digest(rules) == bound.rules_digest, 'Changed narration rules after binding'
    registered = bound.nodes.get(id(element))
    if registered is None or registered[0] is not element or registered[1] != tree_key(element):
        raise ValueError('unsupported_source_bound_order_operations_context')


def plain_text(text: str | None, track: str) -> str:
    """Plain linguistic text only; notation and numerals must use fixed fixtures."""
    assert track in TRACKS, 'No language fallback'
    text = text or ''
    if re.search(r'\d|[+−÷·^=\[\]]|…', text):
        raise ValueError(f'unsupported_unregistered_notation_or_number: {text!r}')
    labels = ({'ⓐ': 'bagean a: ', 'ⓑ': 'bagean be: '} if track.startswith('jv')
              else {'ⓐ': 'bagian a: ', 'ⓑ': 'bagian be: '})
    for glyph, reading in labels.items():
        text = text.replace(glyph, reading)
    return text


def narrate(element: ET.Element, track: str, bound: BoundContext, rules: dict) -> str:
    _require_bound(element, track, bound, rules)
    element_id, tag = element.get('id'), local(element)
    if element_id in bound.prose:
        return bound.prose[element_id]
    if element.tag == '{' + MATH + '}math':
        if id(element) not in bound.math:
            raise ValueError('unsupported_source_bound_order_operations_math')
        if id(element) in bound.context_only:
            raise ValueError('context_only_or_nonspoken_order_operations_math')
        return bound.math[id(element)]
    if tag == 'table':
        if element_id not in bound.tables:
            raise ValueError('unsupported_order_operations_table')
        return bound.tables[element_id] + '\n'
    if tag == 'media':
        if element_id not in bound.media:
            raise ValueError('unsupported_order_operations_image')
        return bound.media[element_id]
    if tag == 'image':
        return ''
    if tag == 'newline':
        return '\n'
    if tag == 'link':
        raise ValueError('No links are registered in the selected section')
    result = plain_text(element.text, track)
    if tag == 'solution' and element.find('{*}title') is None:
        result = ('Wangsulan.\n' if track.startswith('jv') else 'Jawaban.\n') + result
    for child in element:
        result += narrate(child, track, bound, rules) + plain_text(child.tail, track)
        if local(child) in ('para', 'title', 'equation', 'item', 'solution', 'problem'):
            result += '\n'
    return result


def blocks(root: ET.Element, track: str, rules: dict, source: ET.Element) -> list[tuple[str, str]]:
    bound = bind(root, source, rules, track)
    result = []
    for index, element in enumerate(root):
        body = narrate(element, track, bound, rules)
        body = re.sub(r'[ \t]+', ' ', body)
        body = re.sub(r' *\n *', '\n', body)
        body = re.sub(r'\n{3,}', '\n\n', body).strip()
        assert body, 'No source block may silently disappear'
        anchor = SECTION + '--title' if index == 0 else element.get('id')
        assert anchor
        result.append((anchor, body))
    validate_readout(result, rules, track)
    return result


def validate_readout(block_rows: list[tuple[str, str]], rules: dict, track: str) -> None:
    assert track in TRACKS and len(block_rows) == len(dict(block_rows)) == 31
    combined = '\n'.join(body for _, body in block_rows)
    cue = 'Wangsulan.' if track.startswith('jv') else 'Jawaban.'
    assert combined.count(cue) == 6
    assert not re.search(r'\d|[+−÷·^=\[\]]', combined), 'Raw notation escaped finite speech fixtures'
    by_anchor = dict(block_rows)
    for fixture in rules['table_fixtures']:
        assert by_anchor[fixture['anchor']].count(fixture['expected'][track]) == 1
    for fixture in rules['prose_fixtures']:
        assert fixture['expected'][track] in by_anchor[fixture['anchor']]
    for fixture in rules['prose_fixtures'][5:]:
        question, answer = by_anchor[fixture['anchor']].split(cue, 1)
        assert fixture['expected'][track] not in question and fixture['expected'][track] in answer
    assert all(term not in '\n'.join(row['expected'][track].lower() for row in rules['table_fixtures'])
               for term in ('warna abang', 'wernane abang', 'berwarna merah', 'warna ireng', 'warna hitam'))


def question_readouts(root: ET.Element, track: str, rules: dict, source: ET.Element) -> list[str]:
    bound = bind(root, source, rules, track)
    result = []
    for exercise in root.findall('.//{*}exercise'):
        problem = exercise.find('{*}problem')
        body = narrate(problem, track, bound, rules)
        assert 'Wangsulan.' not in body and 'Jawaban.' not in body
        result.extend(bound.math[id(node)] for node in problem.iter('{' + MATH + '}math'))
    return result
