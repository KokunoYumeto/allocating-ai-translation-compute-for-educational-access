"""Fail-closed bindings for the four source-positioned m81243 components."""
import json
import xml.etree.ElementTree as ET

from build_units import sha, tree_key
from config import LANG, TRACKS
import draft_summary

UNIT = draft_summary.UNIT
RULES_SHA256 = '410bccaa107cc17042f807fb37eab4101b1578be9adaa1ee81aaa4cd3adeb8f3'
COMPONENTS = tuple(draft_summary.SCOPE_PATHS)


def at(root, path):
    for index in path:
        root = root[index]
    return root


def same_tree(actual, serialized):
    return tree_key(actual) == tree_key(ET.fromstring(serialized))


def checked_rules(override=None):
    raw = (LANG / f'audio/{UNIT}.rules.json').read_bytes()
    assert sha(raw) == RULES_SHA256, 'Changed complete summary narration rules'
    rules = json.loads(raw)
    if override is not None:
        assert override == rules, 'Changed summary narration rule object'
    assert rules['scope']['unit'] == UNIT and rules['scope']['module'] == draft_summary.MODULE
    assert rules['scope']['component_order'] == list(COMPONENTS)
    assert rules['scope']['source_component_paths'] == draft_summary.SCOPE_PATHS
    assert rules['scope']['complete_module'] is False
    assert rules['qa_checkpoint']['fixture_payload_sha256'] == 'e846b8d3b1141cff48d47765c35203da3aded3b0cea004c67a455dc50a79190c'
    return rules


def _validate_node_fixture(fixture, source, target, track):
    component = fixture['component']
    assert component in COMPONENTS
    assert fixture['source_component_document_path'] == draft_summary.SCOPE_PATHS[component]
    assert fixture['original_document_path'] == draft_summary.SCOPE_PATHS[component] + fixture['source_path']
    source_node = at(source[component], fixture['source_path'])
    target_node = at(target[component], fixture['source_path'])
    assert source_node.tag == fixture['source_tag'] and source_node.get('id') == fixture['source_id']
    assert same_tree(source_node, fixture['source_cnxml'])
    assert sha(tree_key(source_node).encode()) == fixture['source_tree_sha256']
    assert sha(tree_key(target_node).encode()) == fixture['target_tree_sha256'][track]
    return source_node, target_node


def _validate_components(source, english, target, rules, track):
    draft_summary.validate_components(source, target, track)
    assert len(rules['component_fixtures']) == len(COMPONENTS)
    for fixture, component in zip(rules['component_fixtures'], COMPONENTS):
        assert fixture['component'] == component
        assert fixture['original_document_path'] == draft_summary.SCOPE_PATHS[component]
        assert same_tree(source[component], fixture['source_cnxml'])
        assert same_tree(english[component], fixture['english_cnxml'])
        assert same_tree(target[component], fixture['target_cnxml'][track])
        assert sha(tree_key(source[component]).encode()) == fixture['source_tree_sha256']
        assert sha(tree_key(english[component]).encode()) == fixture['english_tree_sha256']
        assert sha(tree_key(target[component]).encode()) == fixture['target_tree_sha256'][track]
        assert [n.get('id') for n in source[component].iter() if n.get('id')] == fixture['source_ids']
    manifest = rules['source_id_manifest']
    assert len(manifest) == len({row['id'] for row in manifest}) == 23
    for row in manifest:
        node = at(source[row['component']], row['source_path'])
        assert node.get('id') == row['id'] and node.tag == row['tag']
        assert row['original_document_path'] == draft_summary.SCOPE_PATHS[row['component']] + row['source_path']


def _validate_fixtures(source, target, rules, track):
    prose = {row['id']: row for row in rules['prose_fixtures']}
    nonspoken = {row['id']: row for row in rules['nonspoken_fixtures']}
    cues = {row['id']: row for row in rules['structural_cues']}
    charts = {row['id']: row for row in rules['chart_fixtures']}
    assert len(prose) == 35 and len(nonspoken) == 3 and len(cues) == 9 and len(charts) == 1
    occupied = set()
    for fixture in prose.values():
        source_node, target_node = _validate_node_fixture(fixture, source, target, track)
        assert fixture['slot'] == 'text'
        assert source_node.text == fixture['source_text']
        assert target_node.text == fixture['target_text'][track]
        assert fixture['expected'][track]
        occupied.add((fixture['component'], tuple(fixture['source_path']), fixture['slot']))
    for fixture in nonspoken.values():
        source_node, target_node = _validate_node_fixture(fixture, source, target, track)
        assert fixture['slot'] == 'text'
        assert source_node.text == fixture['source_text']
        assert target_node.text == fixture['target_text'][track]
        assert fixture['expected'][track] is None
        occupied.add((fixture['component'], tuple(fixture['source_path']), fixture['slot']))
    assert len(occupied) == 38
    for fixture in cues.values():
        _validate_node_fixture(fixture, source, target, track)
        assert fixture['step_ordinal'] > 0 and fixture['expected'][track]
    chart = charts['C01']
    source_media, target_media = _validate_node_fixture(chart, source, target, track)
    assert source_media.get('alt') == chart['source_alt']
    assert target_media.get('alt') == chart['target_alt'][track]
    assert chart['columns'] == 15 and chart['groups'] == 5
    assert chart['digit_cells'][:8] == [None] * 8
    assert chart['digit_cells'][8:] == [5, 2, 7, 8, 1, 9, 4]
    assert sum((digit or 0) * place for digit, place in
               zip(chart['digit_cells'], chart['column_place_values'])) == chart['expected_value'] == 5278194
    return prose, cues, charts


def bind(track, rules_override=None):
    """Load fresh exact roots and return validated roots, speech and media."""
    assert track in TRACKS
    rules = checked_rules(rules_override)
    pinned = draft_summary.sources()
    source, english = pinned['a00-id'], pinned['openstax-prealgebra-bundle']
    target = {component: ET.parse(
        LANG / f'translation/{UNIT}.{component}.{track}.cnxml').getroot()
              for component in COMPONENTS}
    _validate_components(source, english, target, rules, track)
    prose, cues, charts = _validate_fixtures(source, target, rules, track)

    receipt_raw = (LANG / f'qa/{UNIT}.components-receipt.json').read_bytes()
    assert sha(receipt_raw) == rules['scope']['components_receipt_sha256']
    receipt = json.loads(receipt_raw)
    assert receipt['source_ids'] == [row['id'] for row in rules['source_id_manifest']]
    assert receipt['components'][0]['original_document_path'] == [0]
    assert [row['original_document_path'] for row in receipt['components']] == [[0], [1], [2, 6], [3]]

    chart = charts['C01']
    manifest_path = LANG / chart['asset_manifest']
    manifest_raw = manifest_path.read_bytes()
    assert sha(manifest_raw) == chart['asset_manifest_sha256']
    manifest = json.loads(manifest_raw)
    assert manifest['assets'] == [chart['asset']]
    media = {}
    for asset in manifest['assets']:
        output = asset['outputs'][track]
        raw = (LANG / output['path']).read_bytes()
        assert sha(raw) == output['sha256']
        media[asset['source_src']] = {'bytes': raw,
                                      'mime_type': output.get('mime_type', asset['mime_type'])}

    blocks = []
    for index, block in enumerate(rules['block_fixtures']):
        assert block['index'] == index and block['module'] == draft_summary.MODULE
        _validate_node_fixture(block, source, target, track)
        parts = []
        for row in block['content_sequence']:
            kind = row['kind']
            if kind == 'text_fixture':
                parts.append(prose[row['ref']]['expected'][track])
            elif kind == 'structural_cue':
                parts.append(cues[row['ref']]['expected'][track])
            elif kind == 'chart_fixture':
                parts.append(charts[row['ref']]['expected'][track])
            elif kind == 'boundary':
                parts.append(row['text'])
            else:
                raise AssertionError('Unknown summary narration content kind: ' + kind)
        body = ''.join(parts)
        assert body == block['expected'][track] and body
        blocks.append((block['generated_mark'], body))
    expected_marks = rules['reader_and_ssml_contract']['block_marks']
    assert [mark for mark, _ in blocks] == expected_marks
    assert len(blocks) == len(set(mark for mark, _ in blocks)) == 14
    return target, blocks, media, rules
