"""Independent source context, operand direction, arithmetic and exchange checks."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT/'gu-Gujr-IN'
SOURCE = ROOT/'downloads/gu-Gujr-IN/a00-id/provenance/logbook/authority/prealgebra2e/m81245.source.cnxml'
C = '{http://cnx.rice.edu/cnxml}'
M = '{http://www.w3.org/1998/Math/MathML}'
source = ET.parse(SOURCE).getroot()
parents = {c: p for p in source.iter() for c in p}
exercises = {e.get('id'): e for e in source.iter(C+'exercise')}
missing = {key for key, e in exercises.items() if e.find(C+'solution') is None}
path = LANG/'translations/a00-m81245-added-solutions.gu.json'
data = json.loads(path.read_text(encoding='utf-8'))
assert len(missing) == len(data['items']) == 42
assert {i['source_exercise'] for i in data['items']} == missing
assert data['source_sha256'] == hashlib.sha256(SOURCE.read_bytes()).hexdigest()


def numbers(text):
    return [int(n.replace(',', '')) for n in re.findall(r'\d[\d,]*', text)]


def source_numbers(problem):
    return [n for e in problem.iter() if e.tag in (M+'mn', M+'mtext') for n in numbers(''.join(e.itertext()))]


def check_equations(text):
    count = 0
    for match in re.finditer(r'(?<!\d)(\d[\d,]*(?:\s*[+−]\s*\d[\d,]*)+)\s*=\s*(\d[\d,]*)', text):
        terms = numbers(match[1]); ops = re.findall('[+−]', match[1]); value = terms[0]
        for op, term in zip(ops, terms[1:]):
            value += term if op == '+' else -term
        assert value == numbers(match[2])[0], match[0]
        count += 1
    return count


def check_transfers(records, initial):
    previous = list(map(int, reversed(str(initial))))
    for record in records:
        before, after = record['before'], record['after']
        assert before == previous
        assert sum(d*10**i for i, d in enumerate(before)) == initial
        assert sum(d*10**i for i, d in enumerate(after)) == initial
        k = len(str(record['from_place']))-1
        assert record['from_place'] == 10**k and k > 0 and before[k] > 0
        expected = before[:]; expected[k] -= 1; expected[k-1] += 10
        assert expected == after and all(d >= 0 for d in after)
        previous = after
    return len(records)


WORD_VALUES = {'અઢાર': 18, 'સોળ': 16, 'ત્ર્યાસી': 83, 'ચોસઠ': 64,
               'સાતસો': 700, 'નેવું': 90, 'પાંચસો': 500, 'પચ્ચીસ': 25}
counts = Counter(); equations = 0; exchanges = 0; stages_checked = 0
for item in data['items']:
    ident = item['source_exercise']; check = item['check']; kind = check['kind']
    problem = exercises[ident].find(C+'problem')
    original = source_numbers(problem); prose = ''.join(problem.itertext())
    counts[kind] += 1
    assert len(item['steps']) >= 2 and item['question_gu'] and item['answer']
    assert '\ufffd' not in json.dumps(item, ensure_ascii=False)
    text = ' '.join([item['answer']]+item['steps'])
    equations += check_equations(text)
    if kind == 'words':
        assert check['operands'] == original
        assert [sum(WORD_VALUES[w] for w in form.split()) for form in check['word_forms']] == original
        assert all(w in item['answer'] for w in check['word_forms'])
        assert '=' not in item['answer']
        siblings = list(parents[exercises[ident]])
        instruction = next(p for p in reversed(siblings[:siblings.index(exercises[ident])]) if p.tag == C+'para')
        assert 'notation to words' in ''.join(instruction.itertext())
    elif kind in ('model', 'subtract_check', 'subtract', 'phrase_subtract', 'story_subtract'):
        if kind == 'phrase_subtract':
            expected = list(reversed(original)) if ('Subtract' in prose or 'less than' in prose) else original
        elif ident == 'fs-id1057274':
            assert original == [1, 97, 73]
            expected = original[1:]
        elif ident == 'fs-id2661110':
            assert original == [755, 1600]
            expected = list(reversed(original))
        else:
            expected = original
        assert check['operands'] == expected and len(expected) == 2, (ident, expected)
        a, b = expected; result = a-b
        assert result == check['result'] and result >= 0
        if kind == 'story_subtract':
            assert item['answer'] == f'{result:,} '+check['unit_gu']+'.'
        else:
            lhs, rhs = item['answer'].split('=')
            assert numbers(lhs) == [a, b] and '−' in lhs and numbers(rhs) == [result]
        if kind == 'subtract_check':
            assert f'{result:,} + {b:,} = {a:,}' in text
        exchanges += check_transfers(check.get('transfers', []), a)
        if kind == 'model':
            stages = item['base10_model']['stages']
            assert stages[0]['role'] == 'initial' and stages[-2]['role'] == 'removed' and stages[-1]['role'] == 'remaining'
            for s in stages:
                target = {'initial': a, 'regrouped': a, 'removed': b, 'remaining': result}[s['role']]
                assert s['tens']*10+s['ones'] == target
                stages_checked += 1
            before = stages[-3]; removed = stages[-2]; remaining = stages[-1]
            assert before['tens']-removed['tens'] == remaining['tens']
            assert before['ones']-removed['ones'] == remaining['ones']
    elif kind == 'mixed_addition':
        assert original == check['operands'] == [647, 528]
        assert '+' in ''.join(problem.find('.//'+M+'math').itertext())
        assert sum(original) == check['result'] == numbers(item['answer'].split('=')[1])[0]
    elif kind == 'word_addition':
        assert prose.strip() == 'Sixty more than ninety-three'
        assert check['operands'] == [93, 60] and check['result'] == 153
        assert item['answer'] == '93 + 60 = 153'
    elif kind == 'two_step_story':
        # Adjacent source mn nodes35 and0 form350. Do not misread them as
        # separate scores, and do not silently alter the source tree.
        assert original == [35, 0, 75, 50, 70, 80]
        first_math = problem.find('.//'+M+'math')
        assert int(''.join(first_math.itertext())) == check['target'] == 350
        assert original[2:] == check['scores']
        assert check['target']-sum(check['scores']) == check['result'] == 75
        assert item['answer'] == '75 ગુણ.'
        exchanges += check_transfers(check['transfers'], 350)
    elif kind == 'open_example':
        assert 'addition facts help' in prose
        assert check['part_a']+check['part_b'] == check['total']
        assert 'નમૂનાનો જવાબ' in item['answer'] and 'જુદા જવાબો પણ માન્ય' in text
    else:
        raise ValueError(kind)

receipt = {'schema': 'gujarati-added-solutions-qa-v1', 'module': 'A00 m81245', 'result': 'pass',
           'added_answers': 42, 'kinds': dict(counts), 'displayed_equations_checked': equations,
           'regrouping_value_conservation_transfers': exchanges, 'base10_model_stages_checked': stages_checked,
           'source_sha256': data['source_sha256'], 'target_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
           'source_omitted_answer_ids_covered': sorted(missing),
           'checks': ['Exact missing-source coverage', 'Word-form instructional context and Gujarati decoding',
                      'Source operand order including from/less-than reversal', 'Independent subtraction and inverse addition',
                      'Mixed addition preserved in subtraction section', 'Every displayed numeric equation',
                      'Regrouping through zero conserves whole value', 'Model removal and remaining blocks',
                      'Date excluded; currency retained; adjacent35/0 parsed as350', 'Two-step score problem and open reflection'],
           'native_review_pending': True, 'source_faithful_xml_unchanged': True}
(LANG/'A00_SUBTRACTION_ANSWERS_QA.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
print(f'PASS:42 answers;{equations} displayed equations;{exchanges} regrouping transfers;{stages_checked} model stages.')
