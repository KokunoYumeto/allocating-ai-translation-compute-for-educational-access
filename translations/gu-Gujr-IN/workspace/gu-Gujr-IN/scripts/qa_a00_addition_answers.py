"""Independently bind all40 added answers to the original questions and images."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT/'gu-Gujr-IN'
SOURCE = ROOT/'downloads/gu-Gujr-IN/a00-id/provenance/logbook/authority/prealgebra2e/m81244.source.cnxml'
MEDIA = ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'
C = '{http://cnx.rice.edu/cnxml}'
M = '{http://www.w3.org/1998/Math/MathML}'
data = json.loads((LANG/'translations/a00-m81244-added-solutions.gu.json').read_text(encoding='utf-8'))
source = ET.parse(SOURCE).getroot()
exercises = {e.get('id'): e for e in source.iter(C+'exercise')}
parents = {c: p for p in source.iter() for c in p}
missing = {i for i, e in exercises.items() if e.find(C+'solution') is None}
assert len(data['items']) == len(missing) == 40
assert {i['source_exercise'] for i in data['items']} == missing
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == data['source_sha256']


def numbers_in(s):
    return [int(n.replace(',', '')) for n in re.findall(r'\d[\d,]*', s)]


def original_numbers(problem):
    return [n for e in problem.iter() if e.tag in (M+'mn', M+'mtext')
            for n in numbers_in(''.join(e.itertext()))]


def equations(text):
    # Parse only complete chains of nonnegative integer addition/subtraction.
    # This checks what the pupil actually reads, not merely stored check fields.
    count = 0
    for match in re.finditer(r'(?<!\d)(\d[\d,]*(?:\s*[+−]\s*\d[\d,]*)+)\s*=\s*(\d[\d,]*)', text):
        operands = numbers_in(match[1])
        operators = re.findall(r'[+−]', match[1])
        value = operands[0]
        for op, operand in zip(operators, operands[1:]):
            value = value+operand if op == '+' else value-operand
        assert value == int(match[2].replace(',', '')), match[0]
        count += 1
    return count


# These values and dimensions were transcribed independently from the actual
# source images, not copied from the generator's computed answer tables.
GRIDS = {'fs-id1485179': (tuple(range(10)), tuple(range(10)), '218.jpg'),
         'fs-id1516426': (tuple(range(3, 10)), tuple(range(6, 10)), '222.jpg'),
         'fs-id2220307': (tuple(range(6, 10)), tuple(range(6, 10)), '226.jpg')}
SIDES = {'fs-id2130628': ([12, 5, 13], '209_img.jpg', 'સેમી'),
         'fs-id2173206': ([19, 14, 19, 14], '211_img.jpg', 'ફૂટ'),
         'fs-id1321391': ([24, 17, 29, 17], '213_img.jpg', 'મીટર'),
         'fs-id1960065': ([25, 10, 14, 7, 11, 10-7], '215_img.jpg', 'ઇંચ')}
WORDS = {'છ': 6, 'ત્રણ': 3, 'પંદર': 15, 'સોળ': 16,
         'ચારસો': 400, 'આડત્રીસ': 38, 'એકસો': 100, 'તેર': 13}
counts = Counter()
eq_count = 0
grid_cells = 0
model_stages = 0
for item in data['items']:
    ident = item['source_exercise']
    exercise = exercises[ident]
    problem = exercise.find(C+'problem')
    check = item['check']
    kind = check['kind']
    counts[kind] += 1
    assert len(item['steps']) >= 2 and item['question_gu'] and item['answer']
    assert '\ufffd' not in json.dumps(item, ensure_ascii=False)
    eq_count += equations(' '.join([item['answer']]+item['steps']))
    if kind == 'words':
        assert original_numbers(problem) == check['addends']
        decoded = [sum(WORDS[w] for w in form.split()) for form in check['word_forms']]
        assert decoded == check['addends']
        assert all(word in item['answer'] for word in check['word_forms'])
        preceding = list(parents[exercise])[:list(parents[exercise]).index(exercise)]
        instruction = next(p for p in reversed(preceding) if p.tag == C+'para')
        assert 'expressions to words' in ''.join(instruction.itertext())
        assert '=' not in item['answer']
    elif kind in ('sum', 'model', 'phrase_sum', 'story_sum'):
        original = original_numbers(problem)
        if ident == 'fs-id1215287':
            # Two occurrences of12 are the shake volume, not calories.
            assert original == [12, 420, 230, 12, 580]
            original = [n for n in original if n != 12]
            assert '12 ઔંસ' in item['steps'][0]
        assert Counter(original) == Counter(check['addends']), (ident, original)
        expected = sum(original)
        assert expected == check['result']
        assert expected in numbers_in(item['answer'])
        if kind == 'story_sum':
            assert item['answer'] == f'{expected:,} '+check['unit_gu']+'.'
        else:
            displayed = item['answer'].split('=')
            assert len(displayed) == 2
            assert Counter(numbers_in(displayed[0])) == Counter(original)
            assert numbers_in(displayed[1]) == [expected]
        if kind == 'model':
            stages = item['base10_model']['stages']
            values = [s['tens']*10+s['ones'] for s in stages]
            assert values[:2] == original and all(v == expected for v in values[2:])
            assert stages[-1]['ones'] < 10
            assert all(s['label_gu'] and s['tens'] >= 0 and s['ones'] >= 0 for s in stages)
            model_stages += len(stages)
    elif kind == 'two_sums':
        math = list(problem.iter(M+'math'))
        actual = [original_numbers(e) for e in math]
        assert actual == check['addends']
        assert [sum(n) for n in actual] == check['results'] == numbers_in(item['answer'])
    elif kind == 'grid':
        table = item['answer_table']; rows, cols, suffix = GRIDS[ident]
        assert tuple(table['row_headers']) == rows and tuple(table['column_headers']) == cols
        assert check['source_image'].endswith(suffix)
        assert len(table['cells']) == len(rows)
        for r, cells in zip(rows, table['cells']):
            assert len(cells) == len(cols)
            for c, value in zip(cols, cells):
                assert value == r+c
                grid_cells += 1
    elif kind == 'perimeter':
        sides, suffix, unit = SIDES[ident]
        assert check['source_image'].endswith(suffix)
        assert check['sides'] == sides and check['result'] == sum(sides)
        assert item['answer'] == str(sum(sides))+' '+unit+'.'
        if ident == 'fs-id1960065':
            assert sides[1] == sides[3]+sides[5] and sides[0] == sides[2]+sides[4]
            assert '10 − 7 = 3' in ' '.join(item['steps'])
            assert 'મૂળ ચિત્રમાં લખેલું માપ નથી' in ' '.join(item['steps'])
    elif kind == 'open_example':
        assert 'નમૂનાનો જવાબ' in item['answer'] and 'જુદા જવાબો પણ માન્ય' in item['steps'][-1]
        assert sum(check['addends']) == check['result']
    else:
        raise ValueError(kind)
    if 'source_image' in check:
        image = problem.find('.//'+C+'image')
        assert Path(image.get('src')).name == check['source_image']
        assert hashlib.sha256((MEDIA/check['source_image']).read_bytes()).hexdigest() == check['source_image_sha256']

receipt = {'schema': 'gujarati-added-solutions-qa-v1', 'module': 'A00 m81244',
           'result': 'pass', 'added_answers': 40, 'kinds': dict(counts),
           'displayed_equations_checked': eq_count, 'completed_grid_cells_checked': grid_cells,
           'base10_model_stages_checked': model_stages,
           'source_sha256': data['source_sha256'],
           'target_sha256': hashlib.sha256((LANG/'translations/a00-m81244-added-solutions.gu.json').read_bytes()).hexdigest(),
           'source_omitted_answer_ids_covered': sorted(missing),
           'checks': ['Exact missing-source-exercise coverage', 'Source instructional context for words/models',
                      'Independent Gujarati number-word decoding', 'Independent arithmetic from source problem tokens',
                      'Actual image headers and boundary lengths', 'Every displayed arithmetic equation',
                      'Base10 conservation before/after regrouping', 'Currency/unit retention and12oz distractor',
                      'Missing side derived explicitly; reflection identified as an example'],
           'native_review_pending': True, 'source_faithful_xml_unchanged': True}
(LANG/'A00_ADDITION_ANSWERS_QA.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
print(f'PASS:40 answers;{eq_count} displayed equations;{grid_cells} grid cells;{model_stages} model stages.')
