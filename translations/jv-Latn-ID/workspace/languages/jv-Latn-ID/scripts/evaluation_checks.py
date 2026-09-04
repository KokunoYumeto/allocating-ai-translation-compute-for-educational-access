"""Fail-closed checks for the complete A10 evaluate-expressions section.

This module is deliberately unit-local.  It does not register a generic
MathML, table, image, or prose speech path.  A readout exists only while the
complete pinned source and translated section, immutable rule bytes, live XML
node, and finite fixture all still agree.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import xml.etree.ElementTree as ET

from build import MATH, local
from config import DOWNLOADS, LANG, ROOT

UNIT = 'a10-evaluate-expressions'
SECTION = 'fs-id1170654889475'
RULES_SHA256 = '9b629c2df98b99cca29740fdbcace2c7e9b301bc45f9e88f407a71be44557ab5'
ASSETS_SHA256 = '92d7567c03373e025ea30c2fa3f30370046ae660b6bc6bbb9048ce1b17932e9a'
CANON_LOCK_SHA256 = '396bc9db6ce9f8ab06e0366cf8f525f68e403afa567a7235bea1ea611c006c76'
TRACKS = ('jv-academic', 'jv-conversation', 'id-academic')
TREE_SHA256 = {
    'id-academic': '0d76d191791c6df1efc290e27434429fa289ca829c536ee2007c3573c984f779',
    'jv-academic': 'e85314cf23e35c44def3df1e807d54c83c8e4ed5615e436957aec85b5cbf0c48',
    'jv-conversation': '4249059f26841227ff36325361701ced9a492adeeeadab82206bd1f927740de1',
}
CANON_IDS = ('C01', 'C07', 'C09', 'C10', 'C14', 'C15', 'C17', 'C19',
             'C21', 'C26', 'C28', 'C29', 'C30', 'C34', 'C43')
OVERRIDES = {
    'A10-EVAL-D14': {
        'effective': 'fc469cf6cd1dfac09c4010af7d7606f1309033663fc0ddbf891813f1b5208b67',
        'canonical': '8ec3ccd4ccb9745db4f7a2a14740c03abd00f61330ab6c0f3a6292a26a864b76',
        'bytes': 439, 'dimensions': [14, 12],
    },
    'A10-EVAL-D16': {
        'effective': '31e05fe68d3807d96bca8c3c747a82bc0ccf1b08d2dbfdb70fc1dea36a025a1e',
        'canonical': 'efa3a502dd3a5cceadc846d48d1aa6fe5fe3f48b9671183a7ab43143df6d19fb',
        'bytes': 1079, 'dimensions': [117, 14],
    },
}

NUMBERS = {
    '1': ('siji', 'satu'), '2': ('loro', 'dua'), '3': ('telu', 'tiga'),
    '4': ('papat', 'empat'), '5': ('lima', 'lima'), '6': ('enem', 'enam'),
    '7': ('pitu', 'tujuh'), '8': ('wolu', 'delapan'), '9': ('sanga', 'sembilan'),
    '12': ('rolas', 'dua belas'), '13': ('telulas', 'tiga belas'),
    '16': ('nembelas', 'enam belas'), '31': ('telung puluh siji', 'tiga puluh satu'),
    '32': ('telung puluh loro', 'tiga puluh dua'),
    '35': ('telung puluh lima', 'tiga puluh lima'),
    '40': ('patang puluh', 'empat puluh'), '52': ('sèket loro', 'lima puluh dua'),
    '64': ('sewidak papat', 'enam puluh empat'),
    '81': ('wolung puluh siji', 'delapan puluh satu'),
    '216': ('rong atus nembelas', 'dua ratus enam belas'),
}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def tree_key(element: ET.Element) -> str:
    node = copy.deepcopy(element)
    node.tail = None
    return ET.canonicalize(ET.tostring(node, encoding='unicode'),
                           strip_text=True, rewrite_prefixes=True)


def fixture_element(text: str) -> ET.Element:
    return ET.fromstring(f'<wrapper xmlns:m="{MATH}">{text}</wrapper>')[0]


def normalized(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def load_rules() -> tuple[dict, bytes]:
    raw = (LANG / f'audio/{UNIT}.rules.json').read_bytes()
    assert sha(raw) == RULES_SHA256, 'changed_evaluation_rules'
    return json.loads(raw), raw


def load_variants() -> dict[str, ET.Element]:
    return {track: ET.parse(LANG / f'translation/{UNIT}.{track}.cnxml').getroot()
            for track in TRACKS}


def validate_canon(rules: dict) -> dict:
    """Reopen the current lock and every actually consulted readable extract."""
    lock_path = LANG / 'canon/sources.lock.json'
    raw = lock_path.read_bytes()
    assert sha(raw) == CANON_LOCK_SHA256, 'changed_current_canon_lock'
    lock = json.loads(raw)
    assert len(lock['records']) == 50
    current = {row['id']: row for row in lock['records']}
    consulted = rules['canon_checkpoint']['current_narration_stage_full_reads']
    assert [row['id'] for row in consulted] == list(CANON_IDS)
    for saved in consulted:
        row = current[saved['id']]
        for key in ('headword', 'url', 'readable_path', 'readable_sha256'):
            assert row[key] == saved[key], ('changed_consulted_canon', saved['id'], key)
        readable = ROOT / row['readable_path']
        assert readable.is_file() and sha(readable.read_bytes()) == row['readable_sha256']
    return {'records': 50, 'lock_sha256': CANON_LOCK_SHA256,
            'consulted_ids': list(CANON_IDS), 'readable_files_reopened': len(CANON_IDS)}


def validate_assets(rules: dict) -> tuple[dict, dict[str, dict[str, dict]]]:
    path = LANG / f'translation/{UNIT}.assets.json'
    raw = path.read_bytes()
    assert sha(raw) == ASSETS_SHA256, 'changed_evaluation_asset_manifest'
    manifest = json.loads(raw)
    assert manifest['rules_sha256'] == RULES_SHA256
    assert len(manifest['assets']) == len(rules['chart_fixtures']) == 16
    charts = {row['id']: row for row in rules['chart_fixtures']}
    assets = {row['fixture_id']: row for row in manifest['assets']}
    assert set(assets) == set(charts)
    mappings = {track: {} for track in TRACKS}
    derivatives = 0
    for fixture_id, asset in assets.items():
        chart = charts[fixture_id]
        assert asset['source_media_id'] == chart['media_id']
        assert asset['source_src'] == chart['source_image']
        assert asset['effective_source']['sha256'] == chart['primary_asset']['sha256']
        for track in TRACKS:
            output = asset['outputs'][track]
            output_raw = (LANG / output['path']).read_bytes()
            assert sha(output_raw) == output['sha256']
            assert output['mime_type'] in ('image/jpeg', 'image/svg+xml')
            if output['mime_type'] == 'image/jpeg':
                assert output_raw.startswith(b'\xff\xd8\xff')
            else:
                svg = ET.fromstring(output_raw)
                assert svg.tag.endswith('}svg')
                labels = [''.join(node.itertext()) for node in svg.iter()
                          if local(node) == 'text']
                assert chart['derivative_required'] is True and track.startswith('jv')
                assert chart['expected_jv_visible_labels'][track] in labels
                derivatives += 1
            mappings[track][asset['source_src']] = {
                'bytes': output_raw, 'mime_type': output['mime_type'],
                'sha256': output['sha256'], 'path': output['path'],
            }
    assert derivatives == 10
    assert sum(row['source_declared_mime'] == 'image/png'
               for row in assets.values()) == 14
    assert sum(row['source_declared_mime'] == 'image/jpeg'
               for row in assets.values()) == 2
    assert sum(row['derivative_required'] for row in assets.values()) == 5
    for asset in assets.values():
        assert asset['outputs']['id-academic']['mime_type'] == 'image/jpeg'
        if not asset['derivative_required']:
            assert len({asset['outputs'][track]['sha256'] for track in TRACKS}) == 1
    for fixture_id, expected in OVERRIDES.items():
        asset = assets[fixture_id]
        assert asset['indonesian_release_override']['present'] is True
        assert asset['indonesian_release_override']['sha256'] == expected['effective']
        assert asset['effective_source']['sha256'] == expected['effective']
        assert asset['effective_source']['bytes'] == expected['bytes']
        assert asset['effective_source']['dimensions'] == expected['dimensions']
        assert asset['canonical_authority']['sha256'] == expected['canonical']
        assert asset['canonical_authority']['retained_as_effective_source'] is False
        assert expected['effective'] != expected['canonical']
        assert all(asset['outputs'][track]['sha256'] == expected['effective'] for track in TRACKS)
    return manifest, mappings


def _number(value: str, track: str) -> str:
    if value not in NUMBERS:
        raise ValueError('unregistered_evaluation_integer')
    return NUMBERS[value][0 if track.startswith('jv') else 1]


def finite_math_witness(node: ET.Element, track: str) -> str:
    """Independent verifier for only the token set in the 38 pinned trees."""
    jv = track.startswith('jv')

    def walk(current: ET.Element) -> str:
        tag = local(current)
        if current.attrib:
            # The selected fixture trees have no semantic attributes.
            raise ValueError('unregistered_evaluation_math_attribute')
        if tag == 'mn':
            return _number((current.text or '').strip(), track)
        if tag in ('mi', 'mtext'):
            value = (current.text or '').strip()
            if value not in ('x', 'y'):
                raise ValueError('unregistered_evaluation_identifier')
            return ('aksara ' if jv else 'huruf ') + {'x': 'eks', 'y': 'ye'}[value]
        if tag == 'mo':
            value = current.text or ''
            operators = {
                '−': ' dikurangi ', '+': ' ditambah ',
                '=': ' padha karo ' if jv else ' sama dengan ',
                '·': ' ping ' if jv else ' kali ',
                '(': 'bukak kurung biasa ' if jv else 'buka kurung biasa ',
                ')': ' tutup kurung biasa', ',': ',', '.': '.',
            }
            if value not in operators:
                raise ValueError('unregistered_evaluation_operator')
            return operators[value]
        if tag == 'msup':
            if len(current) != 2:
                raise ValueError('unregistered_evaluation_power_shape')
            return (walk(current[0]) + ' pangkat ' + walk(current[1])
                    + (', pungkasan pangkat' if jv else ', akhir pangkat'))
        if tag not in ('math', 'mrow'):
            raise ValueError('unregistered_evaluation_math_tag')
        parts = []
        previous = None
        for child in current:
            child_tag = local(child)
            if previous is not None:
                previous_tag = local(previous)
                implicit = (previous_tag in ('mn', 'mi', 'mtext', 'msup')
                            and (child_tag in ('mi', 'mtext', 'msup')
                                 or child_tag == 'mo' and (child.text or '') == '('))
                if implicit:
                    parts.append(' ping ' if jv else ' kali ')
            parts.append(walk(child))
            previous = child
        return ''.join(parts)

    return normalized(walk(node)).replace(' ,', ',').replace(' .', '.')


class Binding:
    """Authority retained for one exact target tree and its actual live nodes."""
    def __init__(self, source: ET.Element, target: ET.Element, track: str,
                 rules: dict, rules_raw: bytes):
        self.source = source
        self.target = target
        self.track = track
        self.rules = copy.deepcopy(rules)
        self.rules_snapshot = json.dumps(self.rules, ensure_ascii=False, sort_keys=True)
        self.rules_raw_sha256 = sha(rules_raw)
        self.source_snapshot = tree_key(source)
        self.target_snapshot = tree_key(target)
        self.nodes = {id(node): (node, tree_key(node)) for node in target.iter()}
        self.math = {}
        self.prose = {}
        self.tables = {}
        self.charts = {}
        self.prose_only = set()
        self.canon = validate_canon(rules)
        self.asset_manifest, self.media = validate_assets(rules)

    def guard(self, element: ET.Element) -> None:
        if self.rules_raw_sha256 != RULES_SHA256:
            raise ValueError('unsupported_source_bound_narration')
        if json.dumps(self.rules, ensure_ascii=False, sort_keys=True) != self.rules_snapshot:
            raise ValueError('unsupported_source_bound_narration')
        if tree_key(self.source) != self.source_snapshot or tree_key(self.target) != self.target_snapshot:
            raise ValueError('unsupported_source_bound_narration')
        registered = self.nodes.get(id(element))
        if registered is None or registered[0] is not element or registered[1] != tree_key(element):
            raise ValueError('unsupported_source_bound_narration')


def bind(source: ET.Element, target: ET.Element, track: str,
         rules: dict | None = None, rules_raw: bytes | None = None) -> Binding:
    if track not in TRACKS:
        raise ValueError('unsupported_evaluation_track')
    if rules is None or rules_raw is None:
        rules, rules_raw = load_rules()
    if sha(rules_raw) != RULES_SHA256:
        raise ValueError('unsupported_source_bound_narration')
    if rules != json.loads(rules_raw):
        raise ValueError('unsupported_source_bound_narration')
    scope = rules['scope']
    assert scope['unit'] == UNIT and scope['section'] == SECTION
    assert [node.get('id') for node in source.iter() if node.get('id')] == scope['source_section_ids']
    assert len(source) == scope['source_direct_children'] == 13
    assert sha(tree_key(source).encode()) == TREE_SHA256['id-academic']
    assert sha(tree_key(target).encode()) == TREE_SHA256[track]
    assert len(list(source.iter('{' + MATH + '}math'))) == 38
    assert len(source.findall('.//{*}table')) == 5
    assert len(source.findall('.//{*}media')) == 16
    assert len(source.findall('.//{*}exercise')) == len(source.findall('.//{*}solution')) == 9
    assert not source.findall('.//{*}link') and rules['reference_fixtures'] == []
    bound = Binding(source, target, track, rules, rules_raw)
    # Bind only the private immutable snapshot, never caller-owned mappings.
    rules = bound.rules
    source_ids = {node.get('id'): node for node in source.iter() if node.get('id')}
    target_ids = {node.get('id'): node for node in target.iter() if node.get('id')}
    for group, target_map, id_key in (
            ('prose_fixtures', bound.prose, 'element_id'),
            ('table_fixtures', bound.tables, 'table_id'),
            ('chart_fixtures', bound.charts, 'media_id')):
        for fixture in rules[group]:
            source_node = source_ids[fixture[id_key]]
            target_node = target_ids[fixture[id_key]]
            fixture_tree = fixture_element(fixture['source_cnxml'])
            assert tree_key(fixture_tree) == tree_key(source_node)
            assert sha(tree_key(source_node).encode()) == fixture['source_tree_sha256']
            assert sha(tree_key(target_node).encode()) == fixture['expected_target_tree_sha256'][track]
            assert fixture['expected'][track].strip()
            target_map[id(target_node)] = fixture
    indexed = {(row['anchor'], row['math_ordinal']): row for row in rules['math_fixtures']}
    assert len(indexed) == 38
    used = set()
    for source_block, target_block in zip(source, target):
        anchor = source_block.get('id')
        for ordinal, (source_math, target_math) in enumerate(zip(
                source_block.iter('{' + MATH + '}math'),
                target_block.iter('{' + MATH + '}math')), 1):
            fixture = indexed.get((anchor, ordinal))
            if fixture is None:
                raise ValueError(f'unsupported_source_bound_narration: {(anchor, ordinal)}')
            expected_tree = fixture_element(fixture['source_mathml'])
            assert tree_key(source_math) == tree_key(expected_tree)
            assert sha(tree_key(source_math).encode()) == fixture['source_tree_sha256']
            assert sha(tree_key(target_math).encode()) == fixture['expected_target_tree_sha256'][track]
            assert finite_math_witness(source_math, track) == fixture['expected'][track]
            bound.math[id(target_math)] = fixture
            if fixture.get('standalone_readout_authorized') is False:
                required = target_ids[fixture['requires_prose_element']]
                assert target_math in list(required.iter())
                assert id(required) in bound.prose
                bound.prose_only.add(id(target_math))
            used.add((anchor, ordinal))
    assert used == set(indexed)
    _validate_answers(rules)
    return bound


def _safe_fragment(text: str | None, track: str) -> str:
    text = text or ''
    if re.search(r'[0-9$^=·+−]|\b[xy]\b', text):
        raise ValueError('unsupported_unregistered_evaluation_text')
    return text


def _narrate(element: ET.Element, bound: Binding) -> str:
    fixture = bound.prose.get(id(element))
    if fixture is not None:
        return fixture['expected'][bound.track]
    fixture = bound.tables.get(id(element))
    if fixture is not None:
        return fixture['expected'][bound.track] + '\n'
    fixture = bound.charts.get(id(element))
    if fixture is not None:
        return fixture['expected'][bound.track]
    if element.tag == '{' + MATH + '}math':
        fixture = bound.math.get(id(element))
        if fixture is None or id(element) in bound.prose_only:
            raise ValueError('unsupported_source_bound_narration')
        return fixture['expected'][bound.track]
    tag = local(element)
    jv = bound.track.startswith('jv')
    if tag == 'image':
        return ''
    if tag == 'newline':
        return '\n'
    if tag == 'span' and element.get('class') == 'token':
        value = (element.text or '').strip()
        if value not in ('ⓐ', 'ⓑ') or len(element):
            raise ValueError('unsupported_evaluation_part_marker')
        return ('Bagean ' if jv else 'Bagian ') + ('a' if value == 'ⓐ' else 'be') + '.'
    if tag == 'emphasis' and not len(element) and (element.text or '').strip() in ('x', 'y'):
        value = (element.text or '').strip()
        return ('aksara ' if jv else 'huruf ') + {'x': 'eks', 'y': 'ye'}[value]
    if tag == 'link':
        raise ValueError('unsupported_source_reference')
    allowed = {'section', 'title', 'para', 'note', 'example', 'exercise', 'problem',
               'solution', 'list', 'item', 'figure', 'caption', 'equation', 'emphasis',
               'term', 'definition', 'meaning', 'label', 'tgroup', 'tbody', 'row',
               'entry', 'colspec'}
    if tag not in allowed:
        raise ValueError('unsupported_evaluation_element')
    result = _safe_fragment(element.text, bound.track)
    if tag == 'solution' and element.find('{*}title') is None:
        result = ('Wangsulan.\n' if jv else 'Jawaban.\n') + result
    for child in element:
        result += _narrate(child, bound) + _safe_fragment(child.tail, bound.track)
        if local(child) in ('title', 'para', 'problem', 'solution', 'item', 'table', 'figure'):
            result += '\n'
    return result


def narrate(element: ET.Element, bound: Binding) -> str:
    bound.guard(element)
    return _narrate(element, bound)


def _clean_block(text: str) -> str:
    return '\n'.join(normalized(line) for line in text.splitlines() if normalized(line))


def blocks(source: ET.Element, target: ET.Element, track: str,
           rules: dict | None = None, rules_raw: bytes | None = None) -> tuple[list[tuple[str, str]], Binding]:
    bound = bind(source, target, track, rules, rules_raw)
    result = []
    for index, node in enumerate(target):
        anchor = f'{SECTION}--title' if index == 0 else node.get('id')
        result.append((anchor, _clean_block(narrate(node, bound))))
    validate_readout(result, bound)
    return result, bound


def validate_readout(readout: list[tuple[str, str]], bound: Binding) -> None:
    rules, track = bound.rules, bound.track
    assert len(readout) == len(dict(readout)) == 13
    by_anchor = dict(readout)
    combined = '\n'.join(text for _, text in readout)
    for group in ('math_fixtures', 'prose_fixtures', 'table_fixtures', 'chart_fixtures'):
        for fixture in rules[group]:
            assert fixture['expected'][track] in by_anchor[fixture['anchor']], ('missing_fixture', fixture['id'])
    cue = 'Wangsulan.' if track.startswith('jv') else 'Jawaban.'
    assert combined.count(cue) == len(rules['answer_policy']['untitled_solution_cues']) == 6
    worked_title = rules['answer_policy']['worked_title_expected'][track]
    assert combined.count(worked_title) == len(rules['answer_policy']['worked_solution_ids']) == 3
    assert not re.search(r'[0-9$^=·]|(?<!aksara )(?<!huruf )\b[xy]\b', combined)
    assert rules['reference_fixtures'] == [] and not bound.target.findall('.//{*}link')
    question_fixtures = {row['id']: row for row in rules['prose_fixtures']}
    answer_fixtures = {row['id']: row for row in rules['prose_fixtures']}
    untitled = {row['solution_id']: row for row in rules['answer_policy']['untitled_solution_cues']}
    source_nodes = {node.get('id'): node for node in bound.source.iter() if node.get('id')}
    top_by_id = {}
    for top in bound.source:
        for node in top.iter():
            if node.get('id'):
                top_by_id[node.get('id')] = top.get('id')
    for exercise in rules['answer_policy']['exercise_checks']:
        anchor = top_by_id[exercise['exercise_id']]
        body = by_anchor[anchor]
        question = next(row for row in rules['prose_fixtures']
                        if row['element_id'] == exercise['question_paragraph'])
        solution_id = exercise['solution_id']
        boundary = cue if solution_id in untitled else worked_title
        assert body.index(question['expected'][track]) < body.index(boundary)
        if solution_id in untitled:
            answer = answer_fixtures[untitled[solution_id]['prose_fixture']]
            assert body.index(boundary) < body.index(answer['expected'][track])
        else:
            solution = source_nodes[solution_id]
            tables = [row for row in rules['table_fixtures']
                      if source_nodes[row['table_id']] in list(solution.iter())]
            assert tables and all(body.index(boundary) < body.index(row['expected'][track]) for row in tables)


def _validate_answers(rules: dict) -> None:
    """Finite arithmetic witnesses; never exposed as question narration."""
    expected = [
        [('7x−4', 5, 31), ('7x−4', 1, 3)],
        [('8x−3', 2, 13), ('8x−3', 1, 5)],
        [('4y−4', 3, 8), ('4y−4', 5, 16)],
        [('x^2', 4, 16), ('3^x', 4, 81)],
        [('x^2', 3, 9), ('4^x', 3, 64)],
        [('x^3', 6, 216), ('2^x', 6, 64)],
        [('2x^2+3x+8', 4, 52)], [('3x^2+4x+1', 3, 40)],
        [('6x^2−4x−7', 2, 9)],
    ]
    actual = [[(part['expression'], part['given_value'], part['source_answer'])
               for part in row['parts']] for row in rules['answer_policy']['exercise_checks']]
    assert actual == expected
    calculators = {
        '7x−4': lambda x: 7*x-4, '8x−3': lambda x: 8*x-3,
        '4y−4': lambda y: 4*y-4, 'x^2': lambda x: x**2,
        '3^x': lambda x: 3**x, '4^x': lambda x: 4**x,
        'x^3': lambda x: x**3, '2^x': lambda x: 2**x,
        '2x^2+3x+8': lambda x: 2*x**2+3*x+8,
        '3x^2+4x+1': lambda x: 3*x**2+4*x+1,
        '6x^2−4x−7': lambda x: 6*x**2-4*x-7,
    }
    assert all(calculators[expression](value) == answer
               for rows in actual for expression, value, answer in rows)
    assert [row['source_expression_rows'] for row in rules['answer_policy']['worked_steps']] == [
        ['7x−4', '7(5)−4', '35−4', '31'],
        ['7x−4', '7(1)−4', '7−4', '3'],
        ['x^2', '4^2', '4·4', '16'],
        ['3^x', '3^4', '3·3·3·3', '81'],
        ['2x^2+3x+8', '2(4)^2+3(4)+8', '2(16)+3(4)+8', '32+12+8', '52'],
    ]
