"""Finite production binding for complete A00 m81245 subtraction.

There is deliberately no generic mathematical, table, diagram, or number
reader.  Every spoken component comes from the exact 1,419,111-byte rules
contract after the complete source and target trees have been rebound.
"""
import copy
import hashlib
import json
import re
import xml.etree.ElementTree as ET

from build import CN, MATH, XML_LANG, local
from build_units import tree_key
from config import LANG, TRACKS
from draft_subtract_whole import CORRECTION_IDS, UNIT, products as draft_products


RULES_SHA256 = 'fe5e22786f6e367c73236289f7782953fc964c9ca3b25148362e8be2872dbd8e'
ASSETS_SHA256 = '8e843e32fc5bdea7e428417b55603ef19a7ef82f668492ae446d4db46fe65ef5'
EDITS_SHA256 = 'f14ba0b15bfd343d9b4337d708b01a05b7734695c240531d0d53918ab72ec581'
SHARED_EDITS_SHA256 = 'adc145f5957bf18281cd737b9e1079af4d24f6d5505c9485138de3018b2ab5b8'
SOURCE_LOCK_SHA256 = '27259f1bdafac170ec4476192d142a1a7dfbc6da7b238099338f329e955432eb'
CANON_LOCK_SHA256 = '396bc9db6ce9f8ab06e0366cf8f525f68e403afa567a7235bea1ea611c006c76'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical_sha(node):
    return sha(tree_key(node).encode())


def at(root, path):
    node = root
    for index in path:
        node = node[index]
    return node


def path_index(root):
    result = {}

    def visit(node, path):
        result[id(node)] = tuple(path)
        for index, child in enumerate(node):
            visit(child, path + (index,))

    visit(root, ())
    return result


def slot(node, name):
    if name == 'text':
        return node.text or ''
    if name == 'tail':
        return node.tail or ''
    return node.get(name, '')


def correction_rows(rules, receipt):
    charts = {row['media_id']: row for row in rules['chart_fixtures']}
    rows = {row['media_id']: row for row in receipt['accessibility_corrections']}
    assert set(rows) == set(CORRECTION_IDS)
    for media_id, row in rows.items():
        chart = charts[media_id]
        assert row['source_path'] == chart['source_path']
        assert row['source_ref'] == chart['source_ref']
        assert row['image_sha256'] == chart['sha256']
        assert row['old_source_alt'] == chart['source_alt']
        assert row['old_target_alt'] == {
            track: chart['target_alt'][track] for track in TRACKS if track.startswith('jv')}
        assert row['corrected_target_alt'] == {
            track: chart['independent_expected_reading'][track]
            for track in TRACKS if track.startswith('jv')}
    return rows


class BoundModule:
    pass


def bind():
    expected = draft_products()
    for path, raw in expected.items():
        if path == f'qa/{UNIT}.in-progress.json':
            continue  # the production stage replaces this one state receipt
        assert (LANG / path).read_bytes() == raw, f'Stale complete subtraction draft: {path}'
    rules_path = LANG / f'audio/{UNIT}.rules.json'
    assets_path = LANG / f'translation/{UNIT}.assets.json'
    assert sha(rules_path.read_bytes()) == RULES_SHA256
    assert sha(assets_path.read_bytes()) == ASSETS_SHA256
    assert sha((LANG / f'translation/{UNIT}.edits.json').read_bytes()) == EDITS_SHA256
    assert sha((LANG / 'translation/phrases.json').read_bytes()) == SHARED_EDITS_SHA256
    assert sha((LANG / 'sources.lock.json').read_bytes()) == SOURCE_LOCK_SHA256
    assert sha((LANG / 'canon/sources.lock.json').read_bytes()) == CANON_LOCK_SHA256
    rules = json.loads(rules_path.read_text(encoding='utf-8'))
    assets = json.loads(assets_path.read_text(encoding='utf-8'))
    receipt = json.loads(expected[f'qa/{UNIT}.in-progress.json'].decode())
    variants = {track: ET.parse(LANG / f'translation/{UNIT}.{track}.cnxml').getroot()
                for track in TRACKS}
    english = ET.parse(LANG / f'provenance/{UNIT}.en.cnxml').getroot()
    source = variants['id-academic']
    corrections = correction_rows(rules, receipt)
    assert rules['scope']['complete_module_source'] is True
    assert rules['scope']['full_assignment_complete'] is False
    assert rules['matching_contract']['unknown_case'] == 'error'
    assert rules['matching_contract']['generic_mathml_parser_authorized'] is False
    assert rules['matching_contract']['generic_number_parser_authorized'] is False
    assert rules['matching_contract']['provider_calls_authorized'] is False
    assert assets['status'] == 'complete_source_bound_asset_draft_not_reader_integrated'
    assert assets['rules_sha256'] == RULES_SHA256
    assert canonical_sha(source) == rules['scope']['indonesian_module_canonical_sha256']
    assert canonical_sha(english) == rules['scope']['english_module_canonical_sha256']
    for track, root in variants.items():
        assert canonical_sha(root) == receipt['corrected_target_canonical_sha256'][track]
        if track.startswith('jv'):
            assert root.get(XML_LANG) == 'jv-Latn-ID'

    source_ids = [node.get('id') for node in source.iter() if node.get('id')]
    assert source_ids == [row['id'] for row in rules['source_id_identity']]
    assert len(source_ids) == len(set(source_ids)) == 716
    assert [node.get('id') for node in english.iter() if node.get('id')] == source_ids
    for root in variants.values():
        assert [node.get('id') for node in root.iter() if node.get('id')] == source_ids
    for row in rules['source_id_identity']:
        node = at(source, row['source_path'])
        assert node.get('id') == row['id']
        assert node.tag == row['qname'] and node.attrib == row['attributes']
        assert canonical_sha(node) == row['source_canonical_sha256']

    phrase_occurrences = {}
    for fixture in rules['phrase_fixtures']:
        assert sha(fixture['source'].encode()) == fixture['source_sha256']
        for occurrence in fixture['occurrences']:
            key = (tuple(occurrence['path']), occurrence['slot'])
            assert key not in phrase_occurrences
            phrase_occurrences[key] = fixture
            source_node = at(source, occurrence['path'])
            assert slot(source_node, occurrence['slot']).strip() == fixture['source']
            for track, root in variants.items():
                actual = slot(at(root, occurrence['path']), occurrence['slot']).strip()
                if (occurrence['slot'] == 'alt'
                        and at(source, occurrence['path']).get('id') in corrections
                        and track.startswith('jv')):
                    expected_value = corrections[at(source, occurrence['path']).get('id')][
                        'corrected_target_alt'][track]
                else:
                    expected_value = fixture['targets'][track]
                assert actual == expected_value
    assert len(rules['phrase_fixtures']) == 336

    math_by_path = {}
    for fixture in rules['math_fixtures']:
        path = tuple(fixture['source_path'])
        assert path not in math_by_path
        math_by_path[path] = fixture
        source_node = at(source, path)
        assert source_node.tag == '{' + MATH + '}math'
        assert canonical_sha(source_node) == fixture['source_canonical_sha256']
        assert canonical_sha(at(english, path)) == fixture['english_canonical_sha256']
        for track, root in variants.items():
            assert canonical_sha(at(root, path)) == fixture['target_canonical_sha256'][track]
    assert len(math_by_path) == 262

    tables_by_path = {}
    for fixture in rules['table_fixtures']:
        path = tuple(fixture['source_path'])
        assert path not in tables_by_path
        tables_by_path[path] = fixture
        node = at(source, path)
        assert node.get('id') == fixture['table_id']
        assert canonical_sha(node) == fixture['source_canonical_sha256']
        assert len(fixture['rows']) == fixture['row_count']
        for track, root in variants.items():
            assert canonical_sha(at(root, path)) == fixture['target_canonical_sha256'][track]
    assert len(tables_by_path) == 17

    charts_by_path = {}
    asset_by_id = {row['media_id']: row for row in assets['assets']}
    assert len(asset_by_id) == 55
    media_maps = {track: {} for track in TRACKS}
    for fixture in rules['chart_fixtures']:
        path = tuple(fixture['source_path'])
        assert path not in charts_by_path
        charts_by_path[path] = fixture
        node = at(source, path)
        assert node.get('id') == fixture['media_id']
        assert node.get('alt') == fixture['source_alt']
        assert node.find('{*}image').get('src') == fixture['source_ref']
        asset = asset_by_id[fixture['media_id']]
        assert asset['source_path'] == fixture['source_path']
        assert asset['source_src'] == fixture['source_ref']
        assert asset['source_sha256'] == fixture['sha256']
        for track, root in variants.items():
            target = at(root, path)
            expected_alt = (corrections[fixture['media_id']]['corrected_target_alt'][track]
                            if fixture['media_id'] in corrections and track.startswith('jv')
                            else fixture['target_alt'][track])
            assert target.get('alt') == expected_alt
            assert target.find('{*}image').get('src') == fixture['source_ref']
            output = asset['outputs'][track]
            raw = (LANG / output['path']).read_bytes()
            assert sha(raw) == output['sha256']
            assert len(raw) == output['bytes']
            media_maps[track][fixture['source_ref']] = {
                'bytes': raw, 'mime_type': output['mime_type']}
    assert len(charts_by_path) == 55

    references_by_path = {}
    for fixture in rules['reference_fixtures']:
        path = tuple(fixture['source_path'])
        assert path not in references_by_path
        references_by_path[path] = fixture
        node = at(source, path)
        assert node.attrib == fixture['attributes']
        assert canonical_sha(node) == fixture['source_canonical_sha256']
        for root in variants.values():
            assert at(root, path).attrib == fixture['attributes']
    assert len(references_by_path) == 6
    assert [row['attributes'].get('document') for row in rules['reference_fixtures'][:2]] == ['m81244', 'm81244']

    utterances_by_path = {}
    corrected_paths = [tuple(row['source_path']) for row in corrections.values()]
    for fixture in rules['utterance_fixtures']:
        path = tuple(fixture['source_path'])
        assert path not in utterances_by_path
        utterances_by_path[path] = fixture
        assert canonical_sha(at(source, path)) == fixture['source_canonical_sha256']
        for track, root in variants.items():
            if not (track.startswith('jv') and any(path == changed[:len(path)] for changed in corrected_paths)):
                assert canonical_sha(at(root, path)) == fixture['target_canonical_sha256'][track]
    assert len(utterances_by_path) == 263

    exercises_by_path = {}
    solutions = 0
    for fixture in rules['exercise_fixtures']:
        path = tuple(fixture['source_path'])
        assert path not in exercises_by_path
        exercises_by_path[path] = fixture
        exercise = at(source, path)
        assert exercise.get('id') == fixture['exercise_id']
        assert canonical_sha(exercise) == fixture['source_canonical_sha256']
        problem = exercise.find('{*}problem')
        assert problem is not None and problem.get('id') == fixture['problem_id']
        assert canonical_sha(problem) == fixture['problem_canonical_sha256']
        solution = exercise.find('{*}solution')
        if fixture['answer_state'] == 'source-provided':
            assert solution is not None and solution.get('id') == fixture['solution_id']
            assert canonical_sha(solution) == fixture['solution_canonical_sha256']
            solutions += 1
        else:
            assert fixture['answer_state'] == 'source-absent'
            assert solution is None and fixture['solution_id'] is None
            assert fixture['solution_component_sequence'] is None
    assert len(exercises_by_path) == 125 and solutions == 83
    assert len(exercises_by_path) - solutions == 42
    assert rules['answer_policy']['provided_solution_count'] == solutions
    assert set(rules['answer_policy']['missing_solution_ids']) == {
        row['exercise_id'] for row in rules['exercise_fixtures']
        if row['answer_state'] == 'source-absent'}

    for row in rules['nonspoken_source_elements']:
        node = at(source, row['source_path'])
        assert node.tag == row['qname'] and node.attrib == row['attributes']
    assert len(rules['nonspoken_source_elements']) == 35
    assert len(rules['fail_closed_cases']) == 35

    bound = BoundModule()
    bound.source = source
    bound.english = english
    bound.variants = variants
    bound.rules = rules
    bound.assets = assets
    bound.receipt = receipt
    bound.corrections = corrections
    bound.phrases = phrase_occurrences
    bound.math = math_by_path
    bound.tables = tables_by_path
    bound.charts = charts_by_path
    bound.references = references_by_path
    bound.utterances = utterances_by_path
    bound.exercises = exercises_by_path
    bound.media = media_maps
    bound.paths = {track: path_index(root) for track, root in variants.items()}
    bound.snapshots = {track: canonical_sha(root) for track, root in variants.items()}
    bound.nodes = {track: {id(node): node for node in root.iter()} for track, root in variants.items()}
    return bound


def _assert_live(bound, track):
    if track not in TRACKS or not isinstance(bound, BoundModule):
        raise ValueError('unsupported_subtraction_binding')
    root = bound.variants[track]
    if canonical_sha(root) != bound.snapshots[track]:
        raise ValueError('changed_source_bound_subtraction_tree')
    if sha((LANG / f'audio/{UNIT}.rules.json').read_bytes()) != RULES_SHA256:
        raise ValueError('changed_subtraction_rules')


def _literal(value, track):
    value = re.sub(r'\s+', ' ', value or '').strip()
    labels = ({'ⓐ': 'bagean a:', 'ⓑ': 'bagean be:'} if track.startswith('jv')
              else {'ⓐ': 'bagian a:', 'ⓑ': 'bagian be:'})
    for glyph, reading in labels.items():
        value = value.replace(glyph, reading)
    return value


def _slot_reading(bound, path, name, value, track):
    if not (value or '').strip():
        return ''
    fixture = bound.phrases.get((tuple(path), name))
    if fixture is not None:
        return fixture['targets'][track]
    if re.search('[A-Za-zÀ-ž]', value):
        raise ValueError(f'unsupported_subtraction_text_slot:{path}:{name}')
    return _literal(value, track)


def _compose(node, track, bound):
    path = bound.paths[track].get(id(node))
    if path is None or bound.nodes[track].get(id(node)) is not node:
        raise ValueError('unsupported_source_bound_subtraction_node')
    if path in bound.utterances:
        return bound.utterances[path]['expected_reading'][track]
    if path in bound.tables:
        rows = bound.tables[path]['rows']
        return 'Tabel.\n' + '\n'.join(row['expected_reading'][track] for row in rows)
    if path in bound.charts:
        return bound.charts[path]['independent_expected_reading'][track]
    if path in bound.math:
        return bound.math[path]['expected_reading'][track]
    if path in bound.references:
        return bound.references[path]['expected_reading'][track]
    if local(node) == 'newline':
        return '\n'
    parts = [_slot_reading(bound, path, 'text', node.text, track)]
    for child in node:
        parts.append(_compose(child, track, bound))
        parts.append(_slot_reading(bound, bound.paths[track][id(child)], 'tail', child.tail, track))
        if local(child) in ('para', 'title', 'item', 'problem', 'solution', 'table'):
            parts.append('\n')
    return ' '.join(part for part in parts if part)


def _clean(text):
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r' *\n *', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' +([.,;:])', r'\1', text)
    return text.strip()


def blocks(track, bound):
    _assert_live(bound, track)
    root = bound.variants[track]
    source = bound.source
    exercise_by_id = {row['exercise_id']: row for row in bound.rules['exercise_fixtures']}
    inherited_paths = {tuple(row['inherited_instruction']['source_path'])
                       for row in bound.rules['exercise_fixtures']
                       if row['inherited_instruction'] is not None}
    output = []

    def add(key, body):
        body = _clean(body)
        if not body:
            raise ValueError(f'empty_subtraction_narration:{key}')
        output.append((key.replace('/', '-'), body))

    def walk(node):
        path = bound.paths[track][id(node)]
        tag = local(node)
        if path in inherited_paths:
            return
        if tag == 'exercise':
            fixture = exercise_by_id[node.get('id')]
            source_exercise = at(source, fixture['source_path'])
            assert canonical_sha(source_exercise) == fixture['source_canonical_sha256']
            problem = node.find('{*}problem')
            question = ''
            inherited = fixture['inherited_instruction']
            if inherited is not None:
                source_instruction = at(source, inherited['source_path'])
                target_instruction = at(root, inherited['source_path'])
                assert canonical_sha(source_instruction) == inherited['source_canonical_sha256']
                question += _compose(target_instruction, track, bound) + '\n'
            question += _compose(problem, track, bound)
            add(fixture['exercise_id'] + '--question', question)
            solution = node.find('{*}solution')
            if fixture['answer_state'] == 'source-provided':
                cue = bound.rules['answer_policy']['answer_cues'][track]
                add(fixture['exercise_id'] + '--answer', cue + '\n' + _compose(solution, track, bound))
            else:
                assert solution is None
            return
        if path in bound.utterances:
            role = bound.utterances[path]['context_role']
            assert role not in ('question', 'supplied_answer'), 'Detached exercise narration owner'
            add(bound.utterances[path]['key'], _compose(node, track, bound))
            return
        if path in bound.tables:
            add(node.get('id'), _compose(node, track, bound))
            return
        if path in bound.charts:
            add(node.get('id'), _compose(node, track, bound))
            return
        if path in bound.math:
            add('math-' + str(bound.math[path]['ordinal']), _compose(node, track, bound))
            return
        if path in bound.references:
            add('reference-' + str(bound.references[path]['ordinal']), _compose(node, track, bound))
            return
        if tag == 'item':
            add(node.get('id') or 'path-' + '-'.join(map(str, path)), _compose(node, track, bound))
            return
        if tag in ('content-id', 'uuid'):
            return
        if tag == 'title' and path == (1, 1):
            return  # duplicate metadata title; root title is the spoken owner
        for child in node:
            walk(child)

    walk(root)
    assert len(output) == len({key for key, _ in output})
    assert sum(key.endswith('--question') for key, _ in output) == 125
    assert sum(key.endswith('--answer') for key, _ in output) == 83
    missing = set(bound.rules['answer_policy']['missing_solution_ids'])
    assert not any(key.removesuffix('--answer') in missing for key, _ in output)
    cue = bound.rules['answer_policy']['answer_cues'][track]
    assert sum(body.count(cue) for _, body in output) == 83
    return output


def narrate(node, track, bound):
    _assert_live(bound, track)
    return _clean(_compose(node, track, bound))
