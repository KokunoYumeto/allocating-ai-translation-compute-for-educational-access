"""Complete, finite rounding dispatch. No generic math/number speech fallback."""
import copy
import json
import re
import xml.etree.ElementTree as ET

from build import MATH, local, translated
from config import LANG, TRACKS
from draft_units import merged_edits
from prepare_rounding_bindings import at, parse, SOURCE

UNIT = 'a00-rounding'
# This is a reviewed fixture-contract digest, not a source or correctness claim.
# Arithmetic, exact source/target slots, table composition and assets are checked
# independently below. New registered speech requires a deliberate review edit.
RULES_DIGEST = '59219f112077ad4eacd7d1b0ebde35e2d01d3173c2ea7514e95903153219b500'
ID_NOTE = ('Catatan aksesibilitas editorial: beberapa panah, garis bawah, warna, '
           'dan tanda coret pada gambar Indonesia tidak tepat atau tidak lengkap. '
           'Uraian diagram berikut mengikuti maksud matematika dan gambar kanonik '
           'OpenStax; gambar Indonesia tetap dipertahankan tanpa perubahan. '
           'Gambar Jawa memuat koreksi yang dicatat terpisah.')


def digest(value):
    from build_units import sha
    return sha(json.dumps(value, sort_keys=True, ensure_ascii=False).encode())


def tree_hash(node):
    from build_units import sha, tree_key
    return sha(tree_key(node).encode())


def clean(text):
    text = re.sub(r'[ \t]+', ' ', text)
    text = '\n'.join(line.strip() for line in text.splitlines())
    return re.sub(r'\n{3,}', '\n\n', text).strip()


def literal(text, track, lexicon):
    """Independent verifier over a finite token lexicon, never dispatch."""
    pattern = r'\d+(?:,\d{3})*'
    text = re.sub(pattern, lambda m: lexicon[m[0]][track], text)
    return text.replace('ⓐ', 'bagean a' if track.startswith('jv') else 'bagian a').replace(
        'ⓑ', 'bagean be' if track.startswith('jv') else 'bagian be')


def sequence(items, source, root, rules, track, fixtures):
    parts = []
    for item in items:
        kind = item['kind']
        if kind == 'boundary':
            assert item['text'] in ('\n', '\n\n', ' ')
            parts.append(item['text'])
        elif kind == 'replayed_literal':
            assert getattr(at(source, item['path']), item['slot']) == item['source_text']
            target = getattr(at(root, item['path']), item['slot'])
            assert target == item['expected'][track], 'Changed literal speech slot'
            assert not re.search(r'\d|[ⓐⓑ]', target)
            parts.append(target)
        elif kind == 'answer_cue':
            node = next(n for n in source.iter() if n.get('id') == item['solution_id'])
            assert local(node) == 'solution' and node.find('{*}title') is None
            parts.append(rules['answer_policy']['cue'][track] + '\n')
        elif kind in ('math_fixture', 'prose_fixture', 'table_fixture', 'chart_fixture', 'structural_cue'):
            fixture = fixtures[item['ref']]
            if 'path' in item:
                assert item['path'] == fixture['source_path'], 'Moved finite fixture'
            if 'slot' in item:
                assert item['slot'] == fixture['slot']
            parts.append(fixture['expected'][track])
        else:
            raise ValueError('unsupported_rounding_sequence')
    return clean(''.join(parts))


def numeric_checks(source, root, rules, track):
    lexicon = rules['finite_cardinal_lexicon']
    expressions = list(source.iter('{' + MATH + '}math'))
    assert len(expressions) == len(rules['math_fixtures']) == 69
    for i, (node, f) in enumerate(zip(expressions, rules['math_fixtures']), 1):
        assert f['id'] == f'M{i:02}' and node is at(source, f['source_path'])
        assert tree_hash(node) == f['source_tree_sha256'] == tree_hash(parse(f['source_mathml']))
        assert tree_hash(at(root, f['source_path'])) == tree_hash(node)
        assert [n.text for n in node.iter('{' + MATH + '}mn')] == [f['number']]
        assert [n.text for n in node.iter('{' + MATH + '}mo')] == f['punctuation']
        assert f['expected'][track] == lexicon[f['number']][track] + ''.join(f['punctuation'])
        assert f['value_invariant'] == int(f['number'].replace(',', ''))
        assert f['group_widths'] == list(map(len, f['number'].split(',')))
        assert (at(root, f['source_path']).tail or '') == f['following_prose_tail'][track]
        block = source[f['top_level_index']]
        assert block.get('id') == f['top_level_anchor']
        assert list(block.iter('{' + MATH + '}math'))[f['ordinal'] - 1] is node
        context = 'top_level_anchor' if 3 <= i <= 5 else 'P-GROUP' if 60 <= i <= 67 else None
        assert f['required_complete_context'] == context
    cases = rules['numeric_and_answer_checks']['rounding_cases']
    finite = [(19651127,1000000,20000000),(19651127,100000,19700000),
              (19651127,10000,19650000),(76,10,80),(72,10,70),(75,10,80),
              (843,10,840),(23658,100,23700),(3978,100,4000),
              (147032,1000,147000),(29504,1000,30000),(157,10,160),
              (884,10,880),(17852,100,17900),(4951,100,5000),
              (63921,1000,64000),(156437,1000,156000)]
    assert len(cases) == 17
    for case, (value, unit, result) in zip(cases, finite):
        assert (case['input_value'], case['requested_unit'], case['result_value']) == (value, unit, result)
        assert int(case['source_input'].replace(',', '')) == value
        assert int(case['source_result'].replace(',', '')) == result
        assert (value + unit // 2) // unit * unit == result
        position = len(str(unit))
        target, decision = value // unit % 10, value // (unit // 10) % 10
        assert (case['target_digit_position_from_right'], case['target_digit']) == (position, target)
        assert (case['decision_digit_position_from_right'], case['decision_digit']) == (position-1, decision)
        assert case['decision_rule'] == ('>=5 add one to target' if decision >= 5 else '<5 keep target')
        assert case['nearest_lower'] == value // unit * unit
        assert case['nearest_upper'] == (value // unit + 1) * unit
        assert case['is_exact_midpoint'] == (value % unit == unit // 2)
        assert case['target_carry_required'] == (target == 9 and decision >= 5)
        assert case['replacement_positions_from_right'] == list(range(1, position))
        assert case['result_groups'] == case['source_result'].split(',')
        assert case['result_zero_positions_from_right'] == [len(str(result))-i for i,d in enumerate(str(result)) if d == '0']
        expected = lexicon['20'][track] + (' yuta' if track.startswith('jv') else ' juta') if unit == 1000000 else lexicon[case['source_result']][track]
        assert case['expected_result'][track] == expected
    group = rules['numeric_and_answer_checks']['regrouping']
    assert group['anchor'] == 'fs-id1751923'
    assert group['groups'] == [{'count':1,'unit':1000},{'count':9,'unit':1000},
        {'count':10,'unit':1000},{'count':1,'unit':10000},{'count':0,'unit':1000},
        {'count':1,'unit':10000},{'count':2,'unit':10000},{'digit':0,'place':1000}]
    assert 1000+9000 == 10000 == 1*10000+0*1000 and (1+2)*10000 == 30000


def validate(source, root, rules, track):
    from build_units import sha, tree_key
    assert track in TRACKS and digest(rules) == RULES_DIGEST, 'Unregistered rounding fixture contract'
    scope = rules['scope']
    assert scope['unit'] == UNIT and scope['complete_section'] is True
    assert source.get('id') == scope['section'] == 'fs-id2472737' and len(source) == 30
    assert tree_hash(source) == scope['section_sha256']['id-academic'] == SOURCE
    assert [n.get('id') for n in source.iter() if n.get('id')] == scope['source_ids']
    assert len(scope['source_ids']) == len(set(scope['source_ids'])) == 104
    replay = source if track == 'id-academic' else translated(source, track, merged_edits(UNIT))
    assert tree_key(root) == tree_key(replay) and tree_hash(root) == scope['section_sha256'][track]
    assert sha((LANG / f'translation/{UNIT}.edits.json').read_bytes()) == scope['edits_sha256']
    assert sha((LANG / 'translation/phrases.json').read_bytes()) == scope['shared_edits_sha256']
    assets_raw = (LANG / f'translation/{UNIT}.assets.json').read_bytes()
    assert sha(assets_raw) == scope['asset_manifest_sha256']
    assets = json.loads(assets_raw)['assets']
    fixtures = {}
    for group in ('math_fixtures','prose_fixtures','chart_fixtures','table_fixtures','structural_cues'):
        for f in rules[group]:
            assert f['id'] not in fixtures
            fixtures[f['id']] = f
    numeric_checks(source, root, rules, track)
    for f in rules['prose_fixtures']:
        a, b = at(source, f['source_path']), at(root, f['source_path'])
        if f['id'] == 'P-GROUP':
            assert tree_hash(a) == f['source_tree_sha256'] == tree_hash(parse(f['source_cnxml']))
            assert tree_hash(b) == f['target_tree_sha256'][track] == tree_hash(parse(f['target_cnxml'][track]))
            assert f['math_refs'] == [f'M{i}' for i in range(60,68)]
        else:
            assert tree_hash(a) == f['containing_source_tree_sha256']
            assert tree_hash(b) == f['containing_target_tree_sha256'][track]
            assert getattr(a, f['slot']) == f['source_text']
            assert getattr(b, f['slot']) == f['target_text'][track]
            assert literal(f['target_text'][track], track, rules['finite_cardinal_lexicon']) == f['expected'][track]
    assert len(rules['chart_fixtures']) == len(assets) == 23
    for chart, asset in zip(rules['chart_fixtures'], assets):
        node = at(source, chart['source_path'])
        target = at(root, chart['source_path'])
        assert chart['media_id'] == asset['media_id'] == node.get('id')
        assert tree_hash(node) == chart['source_tree_sha256'] == tree_hash(parse(chart['source_cnxml']))
        assert tree_hash(target) == chart['variant_tree_sha256'][track] == tree_hash(parse(chart['variant_cnxml'][track]))
        assert chart['alt'][track] == target.get('alt') and chart['outputs'] == asset['outputs']
        assert node.find('{*}image').get('src') == asset['source_src']
        output = asset['outputs'][track]
        raw = (LANG / output['path']).read_bytes()
        assert sha(raw) == output['sha256']
        mime = 'image/png' if raw.startswith(b'\x89PNG') else 'image/jpeg' if raw.startswith(b'\xff\xd8\xff') else 'image/svg+xml'
        assert output['mime_type'] == mime
        if mime == 'image/svg+xml':
            assert local(ET.fromstring(raw)) == 'svg'
    for cue in rules['structural_cues']:
        node = at(source, cue['source_path'])
        assert tree_hash(node) == cue['source_tree_sha256']
        if cue['id'].startswith('LINK-'):
            assert node.get('target-id') == cue['source_target_id'] and not ''.join(node.itertext()).strip()
        else:
            assert node is source[19][1][cue['ordinal']-1] and local(node) == 'item'
    assert len(rules['table_fixtures']) == 5
    for index, f in enumerate(rules['table_fixtures']):
        table = at(root, f['source_path'])
        assert tree_hash(at(source, f['source_path'])) == f['source_tree_sha256']
        assert tree_hash(table) == f['variant_tree_sha256'][track]
        rows = table.findall('.//{*}tbody/{*}row')
        assert table.find('{*}tgroup').get('cols') == '3' and table.find('.//{*}thead') is None
        assert len(rows) == [5,4,4,4,4][index] and all(len(row) == 2 for row in rows)
        assert len(f['row_fixtures']) == len(rows)
        speech, blanks = [], []
        for ri, (row, row_fixtures) in enumerate(zip(rows, f['row_fixtures']), 1):
            assert len(row_fixtures) == 2
            cells = []
            for ci, (cell, cf) in enumerate(zip(row, row_fixtures), 1):
                assert at(root, cf['source_path']) is cell and (cf['row'],cf['column']) == (ri,ci)
                assert tree_hash(at(source, cf['source_path'])) == cf['source_tree_sha256']
                assert tree_hash(cell) == cf['target_tree_sha256'][track]
                assert cf['is_blank'] == (not len(cell) and not (cell.text or '').strip())
                if cf['is_blank']:
                    blanks.append([ri,ci])
                text = sequence(cf['content_sequence'], source, root, rules, track, fixtures)
                assert text == cf['expected'][track]
                if text:
                    cells.append(text)
            speech.append(' '.join(cells))
        assert blanks == f['blank_cells'] and clean('\n'.join(speech)) == f['expected'][track]
    assert len(rules['block_fixtures']) == 30
    result = []
    for index, f in enumerate(rules['block_fixtures']):
        assert f['index'] == index and f['path'] == [index]
        assert tree_hash(source[index]) == f['source_tree_sha256']
        assert tree_hash(root[index]) == f['variant_tree_sha256'][track]
        speech = sequence(f['content_sequence'], source, root, rules, track, fixtures)
        assert speech == f['expected'][track], 'Changed full block composition: ' + f['id']
        mark = 'fs-id2472737--title' if index == 0 else source[index].get('id')
        assert f['generated_mark'] == 'm81243--' + mark
        result.append((mark,speech))
    validate_readout(result, rules, track, source, root)
    return result


def validate_readout(blocks, rules, track, source=None, root=None):
    assert len(blocks) == len(dict(blocks)) == 30
    text = '\n'.join(t for _,t in blocks)
    assert not re.search(r'[0-9ⓐⓑ^=$]|\\n', text)
    assert text.count(rules['answer_policy']['cue'][track]) == 6
    for e in rules['exercise_inventory']:
        speech = dict(blocks)[e['top_level_anchor']]
        question, solution = e['expected_question'][track], e['expected_solution'][track]
        assert clean(question + '\n\n' + solution) == speech
        if source is not None:
            sn = {n.get('id'):n for n in source.iter() if n.get('id')}
            tn = {n.get('id'):n for n in root.iter() if n.get('id')}
            for kind in ('problem','solution'):
                assert tree_hash(sn[e[kind+'_id']]) == e['source_'+kind+'_tree_sha256']
                assert tree_hash(tn[e[kind+'_id']]) == e['target_'+kind+'_tree_sha256'][track]
            assert [n.text for n in sn[e['problem_id']].iter('{' + MATH + '}mn')] == e['source_prompt_values']
    for case in rules['numeric_and_answer_checks']['rounding_cases']:
        if case['exercise_id']:
            e = next(e for e in rules['exercise_inventory'] if e['exercise_id'] == case['exercise_id'])
            result = case['expected_result'][track]
            assert result in e['expected_solution'][track]
            # A correct rounded cardinal can prefix the unrounded question
            # (147,000 within the spoken 147,032). Substring absence is not an
            # answer-leak test. Exact bound question slots/composition above are.


def registered_speech(root, rules, track):
    """Reconstruct from the immutable reviewed contract, never caller cache."""
    speech = {id(root[i]):f['expected'][track] for i,f in enumerate(rules['block_fixtures'])}
    for f in rules['math_fixtures']:
        node = at(root, f['source_path'])
        if not f['required_complete_context']:
            speech[id(node)] = f['expected'][track]
    for group in ('table_fixtures','chart_fixtures'):
        for f in rules[group]:
            speech[id(at(root,f['source_path']))] = f['expected'][track]
    f = rules['prose_fixtures'][0]
    speech[id(at(root,f['source_path']))] = f['expected'][track]
    nodes = {n.get('id'):n for n in root.iter() if n.get('id')}
    for e in rules['exercise_inventory']:
        for kind, key in [('problem','expected_question'),('solution','expected_solution')]:
            speech[id(nodes[e[kind+'_id']])] = e[key][track]
    return speech


def bind(root, rules, track, source):
    from build_units import BoundMath, tree_key
    validate(source, root, rules, track)
    bound = BoundMath()
    bound.rounding_source, bound.rounding_root = source, root
    bound.rounding_snapshots = (tree_key(source), tree_key(root))
    bound.rounding_track, bound.rounding_rules = track, digest(rules)
    bound.rounding_nodes = {id(n):n for n in root.iter()}
    bound.rounding_speech = registered_speech(root,rules,track)
    for f in rules['math_fixtures']:
        node = at(root,f['source_path'])
        bound[id(node)] = f['expected'][track]
        if f['required_complete_context']:
            bound.prose_only.add(id(node))
    return bound


def narrate(node, track, bound, rules):
    from build_units import BoundMath, tree_key, sha
    if (not isinstance(bound,BoundMath) or getattr(bound,'rounding_track',None) != track
            or digest(rules) != RULES_DIGEST or getattr(bound,'rounding_rules',None) != RULES_DIGEST
            or getattr(bound,'rounding_nodes',{}).get(id(node)) is not node
            or id(node) not in getattr(bound,'rounding_speech',{})):
        raise ValueError('unsupported_source_bound_rounding_context')
    current_trees = (tree_key(bound.rounding_source),tree_key(bound.rounding_root))
    if (bound.rounding_snapshots != current_trees or sha(current_trees[0].encode()) != SOURCE
            or sha(current_trees[1].encode()) != rules['scope']['section_sha256'][track]):
        raise ValueError('changed_source_bound_rounding_context')
    expected = registered_speech(bound.rounding_root,rules,track)
    expected_math = {id(at(bound.rounding_root,f['source_path'])):f['expected'][track] for f in rules['math_fixtures']}
    expected_context = {id(at(bound.rounding_root,f['source_path'])) for f in rules['math_fixtures'] if f['required_complete_context']}
    if bound.rounding_speech != expected or dict(bound) != expected_math or bound.prose_only != expected_context:
        raise ValueError('changed_source_bound_rounding_readout_cache')
    return expected[id(node)]
