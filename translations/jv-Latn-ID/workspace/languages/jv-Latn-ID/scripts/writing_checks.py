"""Finite validation for the exact writing lesson, never a speech fallback."""
import re
import xml.etree.ElementTree as ET

from build import MATH, number
from config import TRACKS


VALUES = ('53,401,742', '9,246,073,189', '53,809,051', '2,022,714,466',
          '77,000,000,000', '34,000,000', '204,000,000')
PROSE_IDS = ('fs-id4163187', 'fs-id1885399', 'fs-id2590590',
             'fs-id865214', 'fs-id1395137', 'fs-id1586764')


def literal_witness(token, track, unit=None):
    assert token in VALUES, 'Unregistered printed integer'
    jv = track.startswith('jv')
    prefix = 'digit saka kiwa menyang tengen: ' if jv else 'digit dari kiri ke kanan: '
    separator = '; tandha koma; ' if jv else '; tanda koma; '
    value = separator.join(', '.join(number(digit, jv) for digit in group)
                           for group in token.split(','))
    return prefix + value + ('; ' + unit if unit else '') + '.'


def validate_values(source, variants, rules):
    witnesses = {row['source']: row for row in rules['number_decomposition_witnesses']}
    assert tuple(witnesses) == VALUES and len(rules['number_decomposition_witnesses']) == 7
    math = {row['id']: row for row in rules['math_fixtures']}
    prose = {row['id']: row for row in rules['prose_fixtures']}
    assert len(math) == 6 and len(prose) == 6
    assert [row['element_id'] for row in prose.values()] == list(PROSE_IDS)
    nodes = {node.get('id'): node for node in source.iter() if node.get('id')}
    expected_math = ('53,401,742', '9,246,073,189', '$77', '$77,000,000,000.', '34', '204')
    for index, (fixture, token) in enumerate(zip(math.values(), expected_math), 1):
        assert fixture['id'] == f'A00-WRITE-M{index:02}' and fixture['source_value'] == token
        tree = ET.fromstring(f'<root xmlns:m="{MATH}">{fixture["source_mathml"]}</root>')[0]
        leaves = [node.text for node in tree.iter() if node.tag in ('{' + MATH + '}mn', '{' + MATH + '}mtext')]
        assert leaves == [token]
        if index in (1, 2, 4):
            value = token.strip('$.')
            unit = 'dolar Amerika Serikat' if index == 4 else None
            assert fixture['reading_policy'] == 'literal_digits_not_cardinal_answer'
            for track in TRACKS:
                assert fixture['expected'][track] == literal_witness(value, track, unit)
                assert fixture['expected_cardinal'][track] == witnesses[value]['expected_cardinal'][track]
    for fixture_id, readings in {
        'A00-WRITE-M03': ('pitung puluh pitu', 'tujuh puluh tujuh'),
        'A00-WRITE-M05': ('telung puluh papat', 'tiga puluh empat'),
        'A00-WRITE-M06': ('rong atus papat', 'dua ratus empat'),
    }.items():
        for track in TRACKS:
            assert math[fixture_id]['expected'][track] == readings[0 if track.startswith('jv') else 1]
    for mid, pid in [('A00-WRITE-M03', 'A00-WRITE-P03'), ('A00-WRITE-M06', 'A00-WRITE-P06')]:
        assert math[mid]['requires_prose_fixture'] == pid
        assert math[mid]['requires_prose_element'] == prose[pid]['element_id']
        assert math[mid]['standalone_readout_authorized'] is False
        assert prose[pid]['math_fixtures'] == [mid]
        assert prose[pid]['override_before_child_narration'] is True
    invariants = rules['answer_value_invariants']
    assert len(invariants) == 4
    assert [row['number'] for row in invariants] == [VALUES[2], VALUES[3], VALUES[5], VALUES[6]]
    for invariant in invariants:
        answer = nodes[invariant['answer_paragraph']]
        assert ''.join(answer.itertext()).strip() == invariant['source_answer']
        assert answer in list(nodes[invariant['solution_id']].iter())
        assert nodes[invariant['solution_id']].find('{*}title') is None
        assert nodes[invariant['problem_paragraph']] in list(nodes[invariant['anchor']].find('.//{*}problem').iter())
        fixture = prose[invariant['answer_prose_fixture']]
        assert fixture['element_id'] == invariant['answer_paragraph'] and fixture['requires_solution_cue'] is True
        unit = {'mile': 'mil', 'pound': 'pound', None: None}[invariant['unit']]
        for track, root in variants.items():
            target = next(node for node in root.iter() if node.get('id') == invariant['answer_paragraph'])
            assert ''.join(target.itertext()).strip() == invariant['expected_visible_answer'][track]
            assert fixture['expected'][track] == literal_witness(invariant['number'], track, unit)
            assert invariant['expected_cardinal'][track] == witnesses[invariant['number']]['expected_cardinal'][track]
    quantities = rules['quantity_invariants']
    assert len(quantities) == 3
    assert [(row['coefficient'], row['scale'], row['spoken_unit']) for row in quantities] == [
        ('77', '1000000000', 'dolar Amerika Serikat'), ('34', '1000000', 'mil'), ('204', '1000000', 'pound')]
    for quantity in quantities:
        assert int(quantity['coefficient']) * int(quantity['scale']) == int(quantity['whole_number'].replace(',', ''))
        assert math[quantity['prompt_math_fixture']]['source_value'].lstrip('$') == quantity['coefficient']
        answer = math[quantity['answer_math_fixture']] if 'answer_math_fixture' in quantity else prose[quantity['answer_prose_fixture']]
        for track in TRACKS:
            assert answer['expected'][track] == literal_witness(quantity['whole_number'], track, quantity['spoken_unit'])
            if 'full_prompt_fixture' in quantity:
                prompt = prose[quantity['full_prompt_fixture']]['expected'][track]
                assert prompt.count(quantity['spoken_unit']) == 1
                assert (witnesses[quantity['whole_number']]['expected_cardinal'][track] + ' ' + quantity['spoken_unit']) in prompt
                assert 'digit saka kiwa' not in prompt and 'digit dari kiri' not in prompt and not re.search(r'\d', prompt)
    assert [row['whole_number'] for row in rules['chart_fixtures']] == [VALUES[0], VALUES[1], VALUES[4]]
    for chart in rules['chart_fixtures']:
        assert chart['arrow_direction'] == 'word_block_to_digit_group'
        assert chart['groups_from_left'] == chart['whole_number'].split(',')
        assert sum(int(group) * int(scale) for group, scale in zip(chart['groups_from_left'], chart['group_scales'])) == int(chart['whole_number'].replace(',', ''))
        empty = [2, 3, 4] if chart['id'] == 'A00-WRITE-C03' else []
        assert chart['empty_word_block_indices_from_left'] == empty
        assert len(chart['arrow_mappings']) == len(chart['groups_from_left']) == len(chart['word_block_readings'])
        for i, (mapping, group, words) in enumerate(zip(chart['arrow_mappings'], chart['groups_from_left'], chart['word_block_readings']), 1):
            assert mapping['group_index_from_left'] == i and mapping['source_group'] == group
            assert mapping['word_block_empty'] == (i in empty) == (words is None)
            assert mapping['expected_word_label'] == words
        for track in TRACKS:
            expected_digits = [', '.join(number(digit, track.startswith('jv')) for digit in group) for group in chart['groups_from_left']]
            assert chart['printed_digit_readings'][track] == expected_digits
            assert len(chart['period_labels'][track]) == len(expected_digits)
            for digits in set(expected_digits):
                assert chart['expected'][track].count(digits) >= expected_digits.count(digits)
            for label, words in zip(chart['period_labels'][track], chart['word_block_readings']):
                assert label in chart['expected'][track]
                if words is not None:
                    assert words[track] in chart['expected'][track]


def validate_readout(narration, rules, track):
    blocks = dict(narration)
    assert list(blocks) == ['title'] + rules['scope']['direct_child_ids_after_title']
    full = '\n'.join(blocks.values())
    for fixture in rules['prose_fixtures'] + rules['chart_fixtures']:
        assert full.count(fixture['expected'][track]) == 1, 'Absent/duplicated full writing fixture'
    cue = 'Wangsulan.' if track.startswith('jv') else 'Jawaban.'
    for invariant in rules['answer_value_invariants']:
        question, answer = blocks[invariant['anchor']].split(cue)
        expected = next(row for row in rules['prose_fixtures'] if row['id'] == invariant['answer_prose_fixture'])['expected'][track]
        assert expected not in question and expected in answer
        assert 'digit saka kiwa' not in question and 'digit dari kiri' not in question
    for anchor in ('fs-id2376697', 'fs-id3202693'):
        title = {'jv-academic': 'Panyelesaian', 'jv-conversation': 'Cara Ngrampungake', 'id-academic': 'Penyelesaian'}[track]
        question, answer = blocks[anchor].split(title)
        assert 'digit saka kiwa' not in question and 'digit dari kiri' not in question
        assert cue not in blocks[anchor] and 'digit ' in answer
    assert not re.search(r'\bpon\b', full) and 'pound' in full
