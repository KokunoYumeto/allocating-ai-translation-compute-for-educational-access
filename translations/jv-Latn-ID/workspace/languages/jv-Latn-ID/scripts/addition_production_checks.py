"""Fail-closed complete-module checks and finite narration for m81244."""
import copy
import hashlib
import json
import xml.etree.ElementTree as ET

from build_units import tree_key
from config import LANG, TRACKS
import draft_addition_production as draft


NON_BLOCK_SOURCE_IDS = [
    'fs-id2601285', 'fs-id2145437', 'fs-id1385496', 'fs-id2691382',
    'fs-id2197427', 'fs-id1611455', 'fs-id2263283', 'fs-id2150139',
    'fs-id2280700', 'fs-id1405751', 'eip-985',
]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def rules_digest(rules):
    return sha(json.dumps(rules, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':')).encode('utf-8'))


def node_at(root, path):
    node = root
    for index in path:
        node = node[index]
    return node


def tree_sha(node):
    return sha(tree_key(node).encode('utf-8'))


def expected_top_level_anchor(source, path):
    if not path or path[0] in (0, 1):
        return draft.MODULE + '::front'
    if path[0] == 2 and len(path) > 1:
        return source[2][path[1]].get('id')
    if path[0] == 3:
        return draft.MODULE + '::glossary'
    raise ValueError('Fixture path has no registered top-level anchor')


def ancestor_ids(source, path):
    node, result = source, []
    for index in path[:-1]:
        node = node[index]
        if node.get('id'):
            result.append(node.get('id'))
    return result


def validate_fixture_group(source, target, rules, track, key):
    fixtures = rules[key]
    ids = []
    for fixture in fixtures:
        if fixture['module'] != draft.MODULE:
            raise ValueError('Fixture escaped complete addition module')
        source_node = node_at(source, fixture['source_path'])
        target_node = node_at(target, fixture['source_path'])
        if fixture['top_level_anchor'] != expected_top_level_anchor(source, fixture['source_path']):
            raise ValueError(f'Changed {key} top-level anchor: {fixture["id"]}')
        if fixture.get('ancestor_ids') is not None and fixture['ancestor_ids'] != ancestor_ids(
                source, fixture['source_path']):
            raise ValueError(f'Changed {key} ancestor chain: {fixture["id"]}')
        if source_node is target_node and track != 'id-academic':
            raise ValueError('Javanese fixture shares source object')
        if tree_sha(source_node) != fixture['source_tree_sha256']:
            raise ValueError(f'Changed {key} source fixture: {fixture["id"]}')
        if tree_sha(target_node) != fixture['variant_tree_sha256'][track]:
            raise ValueError(f'Changed {key} target fixture: {fixture["id"]}')
        if fixture.get('element_id') != source_node.get('id'):
            raise ValueError(f'Changed {key} element ID: {fixture["id"]}')
        ids.append(fixture['id'])
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate fixture IDs in ' + key)
    return ids


def validate_exercises(source, target, rules, track):
    rows = rules['exercise_inventory']
    if len(rows) != 129 or [row['ordinal'] for row in rows] != list(range(1, 130)):
        raise ValueError('Exercise inventory order/census changed')
    supplied = absent = titled = cues = 0
    source_problem_ids = []
    for row in rows:
        exercise_source = node_at(source, row['source_path'])
        exercise_target = node_at(target, row['source_path'])
        if exercise_source.get('id') != row['exercise_id'] or exercise_target.get('id') != row['exercise_id']:
            raise ValueError('Exercise source path/ID changed')
        problem_source = exercise_source.find('{*}problem')
        problem_target = exercise_target.find('{*}problem')
        if (problem_source is None or problem_target is None
                or problem_source.get('id') != row['problem_id']
                or tree_sha(problem_source) != row['source_problem_tree_sha256']
                or tree_sha(problem_target) != row['target_problem_tree_sha256'][track]):
            raise ValueError('Exercise problem binding changed: ' + row['exercise_id'])
        source_problem_ids.append(row['problem_id'])
        solution_source = exercise_source.find('{*}solution')
        solution_target = exercise_target.find('{*}solution')
        if row['source_answer_available']:
            supplied += 1
            if (solution_source is None or solution_target is None
                    or solution_source.get('id') != row['source_solution_id']
                    or solution_target.get('id') != row['source_solution_id']
                    or tree_sha(solution_source) != row['source_solution_tree_sha256']
                    or tree_sha(solution_target) != row['target_solution_tree_sha256'][track]
                    or row['expected_solution'][track] is None):
                raise ValueError('Supplied solution binding changed: ' + row['exercise_id'])
            has_title = solution_source.find('{*}title') is not None
            if has_title != row['existing_source_solution_title']:
                raise ValueError('Solution title boundary changed: ' + row['exercise_id'])
            titled += int(has_title)
            cues += int(not has_title)
        else:
            absent += 1
            if (solution_source is not None or solution_target is not None
                    or row['source_solution_id'] is not None
                    or row['source_solution_tree_sha256'] is not None
                    or row['target_solution_tree_sha256'][track] is not None
                    or row['expected_solution'][track] is not None
                    or row['answer_validation'].get('computed_answer') is not None):
                raise ValueError('Absent source answer was synthesized: ' + row['exercise_id'])
        if not row['expected_question'][track]:
            raise ValueError('Empty finite question readout')
    if (supplied, absent, titled, cues) != (89, 40, 15, 74):
        raise ValueError('Exercise answer/cue census changed')
    policy = rules['answer_policy']
    if (policy['supplied'], policy['absent'], policy['untitled_cue_count'],
            policy['existing_solution_titles'], policy['synthesis_of_missing_answer']) != (
            89, 40, 74, 15, False):
        raise ValueError('Answer policy changed')
    if policy['missing_source_answer_ids'] != [
            row['exercise_id'] for row in rows if not row['source_answer_available']]:
        raise ValueError('Missing-answer ID order changed')
    return source_problem_ids


def validate_scope(source, target, rules, track, edits):
    if track not in TRACKS:
        raise ValueError('unsupported_source_bound_narration: unknown track')
    if sha(draft.RULES_PATH.read_bytes()) != draft.RULES_SHA256:
        raise ValueError('unsupported_source_bound_narration: changed rules file')
    if sha(draft.EDITS_PATH.read_bytes()) != draft.EDITS_SHA256:
        raise ValueError('unsupported_source_bound_narration: changed edits file')
    if rules['scope']['complete_module'] is not True or rules['scope']['module'] != draft.MODULE:
        raise ValueError('unsupported_source_bound_narration: incomplete scope')
    draft.validate(source, target, track, edits, rules)
    expected_counts = {
        'math_fixtures': 401, 'prose_fixtures': 240, 'chart_fixtures': 50,
        'table_fixtures': 21, 'block_fixtures': 189,
        'exercise_inventory': 129, 'structural_cues': 52,
    }
    fixture_ids = {}
    for key, count in expected_counts.items():
        if len(rules[key]) != count:
            raise ValueError('Changed fixture census: ' + key)
        if key not in ('exercise_inventory',):
            fixture_ids[key] = validate_fixture_group(source, target, rules, track, key)
    if fixture_ids['math_fixtures'] != [f'M{ordinal:03d}' for ordinal in range(1, 402)]:
        raise ValueError('Math fixture global order changed')
    if [row['global_ordinal'] for row in rules['math_fixtures']] != list(range(1, 402)):
        raise ValueError('Math fixture global ordinals changed')
    per_anchor = {}
    for row in rules['math_fixtures']:
        per_anchor[row['top_level_anchor']] = per_anchor.get(row['top_level_anchor'], 0) + 1
        if row['ordinal'] != per_anchor[row['top_level_anchor']]:
            raise ValueError('Math fixture per-anchor ordinal changed')
    if fixture_ids['prose_fixtures'] != [f'P{ordinal:03d}' for ordinal in range(1, 241)]:
        raise ValueError('Prose fixture order changed')
    if fixture_ids['chart_fixtures'] != [f'C{ordinal:02d}' for ordinal in range(1, 51)]:
        raise ValueError('Media fixture order changed')
    if fixture_ids['table_fixtures'] != [f'T{ordinal:02d}' for ordinal in range(1, 22)]:
        raise ValueError('Table fixture order changed')
    if fixture_ids['block_fixtures'] != [f'B{ordinal:03d}' for ordinal in range(1, 190)]:
        raise ValueError('Narration block fixture order changed')
    validate_exercises(source, target, rules, track)
    blocks = rules['block_fixtures']
    if [row['mark'] for row in blocks] != [row['mark'] for row in rules['block_fixtures']]:
        raise ValueError('Block mark order changed')
    if len({row['mark'] for row in blocks}) != 189 or not all(
            row['mark'].startswith(draft.MODULE + '--path-') for row in blocks):
        raise ValueError('Block marks are not unique path-derived module marks')
    flat_ids = [source_id for row in blocks for source_id in row['source_ids']]
    missing = [source_id for source_id in rules['ordered_source_ids'] if source_id not in flat_ids]
    if (missing != NON_BLOCK_SOURCE_IDS or len(flat_ids) != 745
            or len(flat_ids) != len(set(flat_ids))
            or flat_ids != [source_id for source_id in rules['ordered_source_ids']
                            if source_id not in NON_BLOCK_SOURCE_IDS]):
        raise ValueError('Narration block source-ID partition changed')
    references = {
        'math_refs': set(fixture_ids['math_fixtures']),
        'media_refs': set(fixture_ids['chart_fixtures']),
        'table_refs': set(fixture_ids['table_fixtures']),
        'prose_refs': set(fixture_ids['prose_fixtures']),
    }
    for ref_key, expected in references.items():
        actual = {ref for row in blocks for ref in row[ref_key]}
        if actual != expected:
            raise ValueError('Block fixture coverage changed: ' + ref_key)
    if any(not row['expected'][track].strip() for row in blocks):
        raise ValueError('Empty registered narration block')
    return fixture_ids


class BoundAddition:
    """Authority token tied to actual validated whole-tree objects and snapshots."""
    def __init__(self, source, target, track, rules, fixture_ids):
        self.source = source
        self.target = target
        self.track = track
        self.rule_digest = rules_digest(rules)
        self.source_snapshot = tree_sha(source)
        self.target_snapshot = tree_sha(target)
        self.fixture_ids = fixture_ids
        self.block_nodes = {
            id(node_at(target, row['source_path'])): (node_at(target, row['source_path']), row)
            for row in rules['block_fixtures']}
        self.math_nodes = {
            id(node_at(target, row['source_path'])): (node_at(target, row['source_path']), row)
            for row in rules['math_fixtures']}


def bind(source, target, rules, track, edits):
    fixture_ids = validate_scope(source, target, rules, track, edits)
    return BoundAddition(source, target, track, rules, fixture_ids)


def validate_bound(source, target, rules, track, bound):
    if (not isinstance(bound, BoundAddition) or bound.source is not source
            or bound.target is not target or bound.track != track
            or bound.rule_digest != rules_digest(rules)
            or bound.source_snapshot != tree_sha(source)
            or bound.target_snapshot != tree_sha(target)):
        raise ValueError('unsupported_source_bound_narration')


def registered_math_readout(element, source, target, rules, track, bound):
    validate_bound(source, target, rules, track, bound)
    registered = bound.math_nodes.get(id(element))
    if registered is None or registered[0] is not element or tree_sha(element) != registered[1]['variant_tree_sha256'][track]:
        raise ValueError('unsupported_source_bound_narration')
    return registered[1]['expected'][track]


def registered_block_readout(element, source, target, rules, track, bound):
    validate_bound(source, target, rules, track, bound)
    registered = bound.block_nodes.get(id(element))
    if registered is None or registered[0] is not element or tree_sha(element) != registered[1]['variant_tree_sha256'][track]:
        raise ValueError('unsupported_source_bound_narration')
    return registered[1]['mark'], registered[1]['expected'][track]


def narration_blocks(source, target, rules, track, edits, bound=None):
    bound = bind(source, target, rules, track, edits) if bound is None else bound
    validate_bound(source, target, rules, track, bound)
    result = []
    for row in rules['block_fixtures']:
        element = node_at(target, row['source_path'])
        registered = bound.block_nodes.get(id(element))
        if (registered is None or registered[0] is not element
                or tree_sha(element) != row['variant_tree_sha256'][track]):
            raise ValueError('unsupported_source_bound_narration')
        result.append((row['mark'], row['expected'][track]))
    if len(result) != 189 or [mark for mark, _ in result] != [row['mark'] for row in rules['block_fixtures']]:
        raise ValueError('Narration block order changed')
    return result


def load_saved():
    rules = json.loads(draft.RULES_PATH.read_bytes())
    edits = json.loads(draft.EDITS_PATH.read_bytes())
    source = ET.parse(LANG / f'translation/{draft.UNIT}.id-academic.cnxml').getroot()
    variants = {track: ET.parse(LANG / f'translation/{draft.UNIT}.{track}.cnxml').getroot()
                for track in TRACKS}
    return source, variants, rules, edits
