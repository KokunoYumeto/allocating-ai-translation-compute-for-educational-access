"""Bind new answers to original questions; check signs, steps and emitted HTML."""
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

from lxml import html

ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT / 'gu-Gujr-IN'
sys.path.insert(0, str(LANG / 'translations'))
# The existing source-solution audit parser is independent of the new authoring
# script. It retains signed tokens, absolute-value bars, powers and substitutions.
from qa_a10_m82454_math import calc, expression, problem_expressions, tokens

C = '{http://cnx.rice.edu/cnxml}'
M = '{http://www.w3.org/1998/Math/MathML}'
SOURCE = ROOT / 'downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82454/index.cnxml'
PATH = LANG / 'translations/a10-m82454-added-solutions.gu.json'
source = ET.parse(SOURCE).getroot()
missing = [e for e in source.iter(C + 'exercise') if e.find(C + 'solution') is None]
data = json.loads(PATH.read_text(encoding='utf-8'))
assert data['source_sha256'] == hashlib.sha256(SOURCE.read_bytes()).hexdigest() == '4483b9df8736598af20287450b89cf367728da04c697f85f1abb64bbeffb092f'
assert len(missing) == len(data['items']) == 40
assert [e.get('id') for e in missing] == [i['source_exercise'] for i in data['items']]


def compact(s):
    return re.sub(r'\s+', '', s).replace('⋅', '·').replace('-', '−')


def written_math(e):
    if e.tag == M + 'msup':
        assert ''.join(e[1].itertext()) == '2'
        return written_math(e[0]) + '²'
    return (e.text or '') + ''.join(written_math(c) + (c.tail or '') for c in e)


def numbers(s):
    return [int(n) for n in re.findall(r'[+−-]?\d+', s.replace(',', '').replace('−', '-'))]


def text_expression(s):
    s = re.sub(r'\s+', '', s).replace(',', '').translate(str.maketrans({'−': '-', '×': '*', '·': '*', '÷': '/', '[': '(', ']': ')'})).replace('²', '**2')
    ts = re.findall(r'\*\*|\d+|[a-z]|[()|+*/-]', s)
    assert ''.join(ts) == s, ('Unparsed mathematics', s)
    return expression(ts)


def equations(s):
    count = 0
    env = {}
    runs = re.findall(r'[a-z0-9²+−·×÷*/=(),\[\]| \t]+', s)
    for run in [part for whole in runs for part in re.split(r',\s+', whole)]:
        run = re.sub(r'^\s*\([a-d]\)\s*', '', run)
        if '=' not in run:
            continue
        parts = [p.strip() for p in run.strip().split('=')]
        if len(parts) == 2 and re.fullmatch('[a-z]', parts[0]):
            env[parts[0]] = int(calc(text_expression(parts[1]), env))
            continue
        values = [calc(text_expression(part), env) for part in parts]
        assert all(value == values[0] for value in values), ('False displayed equality', run)
        count += len(values) - 1
    return count


checks = []
eq_count = 0
formula_count = 0
for ordinal, (original, item) in enumerate(zip(missing, data['items']), 1):
    problem = original.find(C + 'problem')
    prose = ''.join(problem.itertext())
    kind = item['check']['kind']
    record = {'ordinal': ordinal, 'source_exercise': original.get('id'), 'kind': kind}
    # Readable question notation is bound to the actual source tokens, including
    # outside minus signs and parentheses, not merely a numerically equal answer.
    if ordinal <= 35:
        math_parts = []
        for m in problem.iter(M + 'math'):
            for part in re.split('when|and', written_math(m)):
                part = compact(part)
                if part:
                    assert part in compact(item['question_gu']), (ordinal, 'question notation', part)
                    math_parts.append(part)
        formula_count += len(math_parts)
        record['original_question_notation'] = math_parts
    if kind == 'comparison':
        pairs = []
        for m in problem.iter(M + 'math'):
            ts = tokens(m)
            split = ts.index('___')
            pairs.append((calc(expression(ts[:split])), calc(expression(ts[split + 1:]))))
        triplets = []
        for part in re.split(r'\([a-d]\)', item['answer']):
            part = part.strip().rstrip('; .')
            if not part:
                continue
            a, sign, b = re.split('([<>=])', part)
            triplets.append((calc(text_expression(a)), sign, calc(text_expression(b))))
        assert len(pairs) == len(triplets)
        for (a, b), (ga, sign, gb) in zip(pairs, triplets):
            assert (a, b) == (ga, gb)
            assert sign == ('<' if a < b else '>' if a > b else '=')
        record['pairs'] = [[int(a), int(b)] for a, b in pairs]
        record['operators'] = [t[1] for t in triplets]
    elif kind == 'opposite':
        inputs = numbers(prose)
        assert inputs == [9, -4] and inputs == numbers(item['question_gu'])
        assert numbers(item['answer']) == [-n for n in inputs]
        record['inputs'] = inputs
        record['answers'] = numbers(item['answer'])
    elif kind == 'numeric':
        expressions = problem_expressions(problem)
        expected = [calc(formula, env) for formula, env in expressions]
        assert expected and all(v.denominator == 1 for v in expected)
        assert numbers(item['answer']) == expected, (ordinal, expected, item['answer'])
        record['source_expressions'] = [{'expression': f, 'substitutions': env} for f, env in expressions]
        record['answers'] = [int(v) for v in expected]
    elif kind == 'temperature':
        assert numbers(prose) == [57, 90, 0]
        assert numbers(item['question_gu']) == [57, 0, 90]
        assert 'below' in prose and numbers(item['answer']) == [57, -90]
        assert item['answer'].count('°C') == 2
        assert 'આજના વિશ્વવિક્રમોની ચકાસણી નથી' in ' '.join(item['steps'])
        record['answers_celsius'] = [57, -90]
    elif kind == 'enrollment':
        assert numbers(prose) == [1400000, 2007, 2010, 110171, 2009, 2010, 2007, 2010, 2009, 2010]
        assert numbers(item['question_gu']) == [2007, 2010, 1400000, 2009, 2010, 110171]
        assert 'grew' in prose and 'declined' in prose
        assert numbers(item['answer']) == [1400000, -110171]
        record['answers_students'] = [1400000, -110171]
        record['periods'] = [[2007, 2010], [2009, 2010]]
    elif kind == 'weekly_change':
        amounts = [int(calc(expression(tokens(m)))) for m in problem.iter(M + 'math')]
        assert amounts == [-201, -16, -23, 172, -34]
        assert 'June 22, 2009' in prose
        assert numbers(item['question_gu']) == [22, 2009] + amounts
        assert numbers(item['answer']) == [sum(amounts)] and sum(amounts) < 0
        assert 'ઋણ' in item['answer'] and 'ઐતિહાસિક' in ' '.join(item['steps'])
        record['changes'] = amounts
        record['overall_change'] = sum(amounts)
    elif kind == 'open_signs':
        assert 'three uses' in prose and 'નમૂનાનો જવાબ' in item['answer']
        assert all(term in item['answer'] for term in ['બાદબાકી', 'ઋણ સંખ્યા', 'વિરોધી સંખ્યા'])
        record['semantic_review'] = 'Three contextual uses; negative number and unary opposite are related, not disjoint operations.'
    elif kind == 'open_example':
        assert 'life experience' in prose and 'two negative numbers' in prose
        assert 'નમૂનો' in item['answer'] and 'દાવો નથી' in ' '.join(item['steps'])
        assert '-20+(-30)=-50' in compact(item['answer']).replace('−', '-')
        record['semantic_review'] = 'Invented debt sample, explicit negative convention, two negative addends; pupil may supply another valid experience.'
    else:
        raise AssertionError(kind)
    eq_count += equations(item['answer'])
    for step in item['steps']:
        eq_count += equations(step)
    checks.append(record)

page_path = LANG / 'output/library/a10-m82454-answers.html'
rendered = None
if '--rendered' in sys.argv:
    page = html.fromstring(page_path.read_bytes())
    sections = page.xpath('//section[contains(concat(" ",normalize-space(@class)," ")," worked-answer ")]')
    assert len(sections) == len(data['items'])
    for section, item in zip(sections, data['items']):
        sid = item['source_exercise']
        assert section.get('id') == 'answer-' + sid
        ps = section.xpath('./p')
        assert ps[0].xpath('./a/@href') == ['a10-m82454.html#' + sid]
        assert ps[1].text_content() == item['question_gu']
        assert section.xpath('./ol/li/text()') == item['steps']
        assert ps[-1].text_content() == 'જવાબ: ' + item['answer']
    rendered = {'sha256': hashlib.sha256(page_path.read_bytes()).hexdigest(), 'questions_answers_and_all_steps_bound': len(sections)}

receipt = {'schema': 'gujarati-integer-added-answers-qa-v1', 'result': 'pass', 'module': 'A10:m82454',
           'source_sha256': data['source_sha256'], 'answer_file_sha256': hashlib.sha256(PATH.read_bytes()).hexdigest(),
           'added_answers': len(checks), 'original_question_math_parts_bound': formula_count,
           'displayed_equality_links_checked': eq_count, 'rendered': rendered, 'checks': checks,
           'limits': ['Separate added solutions, not source-supplied answers.', 'Human semantic review complements these exact arithmetic checks.', 'Native educator, pupil and actual assistive-technology acceptance remain pending.']}
(LANG / 'A10_INTEGER_ANSWERS_QA.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps({k: receipt[k] for k in ['result', 'added_answers', 'original_question_math_parts_bound', 'displayed_equality_links_checked', 'rendered']}, ensure_ascii=False))
