"""Source-bound independent checks for39 signed-product/division answers."""
import ast
from fractions import Fraction
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
from qa_a10_m82454_math import calc, expression, tokens

C = '{http://cnx.rice.edu/cnxml}'
M = '{http://www.w3.org/1998/Math/MathML}'
SOURCE = ROOT / 'downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82455/index.cnxml'
PATH = LANG / 'translations/a10-m82455-added-solutions.gu.json'
data = json.loads(PATH.read_text(encoding='utf-8'))
source = ET.parse(SOURCE).getroot()
missing = [e for e in source.iter(C + 'exercise') if e.find(C + 'solution') is None]
assert data['source_sha256'] == hashlib.sha256(SOURCE.read_bytes()).hexdigest() == '794635f93249017847f2646910d007e9de53b00ee6037133aa5c3edb7c2b88ec'
assert len(missing) == len(data['items']) == 39
assert [e.get('id') for e in missing] == [item['source_exercise'] for item in data['items']]


def compact(s):
    return re.sub(r'\s+', '', s).replace('⋅', '·').replace('-', '−')


def written_math(e):
    if e.tag == M + 'msup':
        exponent = ''.join(e[1].itertext())
        return written_math(e[0]) + {'2': '²', '3': '³', '5': '⁵'}[exponent]
    return (e.text or '') + ''.join(written_math(c) + (c.tail or '') for c in e)


def numbers(s):
    return [int(n) for n in re.findall(r'[+-]?\d+', s.replace('$', '').replace(',', '').replace('−', '-'))]


def normalize(s):
    s = re.sub(r'\s+', '', s).replace(',', '').translate(str.maketrans({'−': '-', '×': '*', '·': '*', '÷': '/', '[': '(', ']': ')'}))
    for superscript, value in [('²', '2'), ('³', '3'), ('⁵', '5')]:
        s = s.replace(superscript, '**' + value)
    s = re.sub(r'(?<=[0-9)])(?=[a-z(])', '*', s)
    s = re.sub(r'(?<=[a-z])(?=\()', '*', s)
    ast.parse(s, mode='eval')
    return s


def polynomial(s):
    """Exact monomial dictionary also checks all displayed numeric equalities."""
    def clean(v):
        return {k: n for k, n in v.items() if n}
    def add(a, b, sign=1):
        d = dict(a)
        for k, v in b.items():
            d[k] = d.get(k, 0) + sign * v
        return clean(d)
    def mul(a, b):
        d = {}
        for ka, va in a.items():
            for kb, vb in b.items():
                key = tuple(sorted(ka + kb))
                d[key] = d.get(key, 0) + va * vb
        return clean(d)
    def walk(n):
        if isinstance(n, ast.Expression):
            return walk(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return clean({(): Fraction(str(n.value))})
        if isinstance(n, ast.Name):
            return {(n.id,): Fraction(1)}
        if isinstance(n, ast.UnaryOp):
            assert isinstance(n.op, (ast.USub, ast.UAdd))
            return {k: v * (-1 if isinstance(n.op, ast.USub) else 1) for k, v in walk(n.operand).items()}
        if isinstance(n, ast.BinOp):
            a, b = walk(n.left), walk(n.right)
            if isinstance(n.op, ast.Add):
                return add(a, b)
            if isinstance(n.op, ast.Sub):
                return add(a, b, -1)
            if isinstance(n.op, ast.Mult):
                return mul(a, b)
            if isinstance(n.op, ast.Div):
                assert set(b) == {()} and b[()] != 0
                return {k: v / b[()] for k, v in a.items()}
            if isinstance(n.op, ast.Pow):
                assert set(b) <= {()}
                power = b.get((), 0)
                assert power.denominator == 1 and 0 <= power <= 6
                out = {(): Fraction(1)}
                for _ in range(int(power)):
                    out = mul(out, a)
                return out
        raise AssertionError(ast.dump(n))
    return walk(ast.parse(normalize(s), mode='eval'))


def equations(s):
    count = 0
    runs = re.findall(r'[a-z0-9²³⁵+−·×÷*/=(),.\[\] \t]+', s)
    for run in [p for whole in runs for p in re.split(r'\.(?=\s|$)|,\s+', whole)]:
        run = re.sub(r'^\s*\([a-d]\)\s*', '', run).strip().strip('.')
        if '=' not in run:
            continue
        parts = [p.strip() for p in run.split('=')]
        if len(parts) == 2 and re.fullmatch('[a-z]', parts[0]):
            continue  # Variable assignments in exposition are not identities.
        values = [polynomial(part) for part in parts]
        assert all(v == values[0] for v in values), ('False displayed equality', run)
        count += len(values) - 1
    return count


checks = []
equation_count = 0
question_parts = 0
for ordinal, (original, item) in enumerate(zip(missing, data['items']), 1):
    problem = original.find(C + 'problem')
    prose = ''.join(problem.itertext())
    kind = item['check']['kind']
    record = {'ordinal': ordinal, 'source_exercise': original.get('id'), 'kind': kind}
    if ordinal <= 25:
        parts = []
        for m in problem.iter(M + 'math'):
            for part in re.split(r'when|and|,\s*(?=[a-z])', written_math(m)):
                part = compact(part)
                if part:
                    assert part in compact(item['question_gu']), (ordinal, 'question notation', part)
                    parts.append(part)
        record['original_question_math_parts'] = parts
        question_parts += len(parts)
    if kind in ('numeric', 'substitution'):
        formulas = []
        for m in problem.iter(M + 'math'):
            ts = tokens(m)
            if 'when' in ts:
                ts = ts[:ts.index('when')]
            if ts and '=' not in ts:
                formulas.append(expression(ts))
        assignments = [(name, int(value)) for name, value in re.findall(r'([a-z])\s*=\s*([+-]?\d+)', prose.replace('−', '-'))]
        if not assignments:
            envs = [{}]
        elif len({name for name, value in assignments}) == 1:
            envs = [{name: value} for name, value in assignments]
        else:
            assert len({name for name, value in assignments}) == len(assignments)
            envs = [dict(assignments)]
        if len(formulas) == 1:
            pairs = [(formulas[0], env) for env in envs]
        elif len(envs) == 1:
            pairs = [(formula, envs[0]) for formula in formulas]
        else:
            assert len(envs) == len(formulas)
            pairs = list(zip(formulas, envs))
        expected = [calc(formula, env) for formula, env in pairs]
        assert expected and all(v.denominator == 1 for v in expected)
        assert numbers(item['answer']) == expected, (ordinal, expected, item['answer'])
        record['source_expressions'] = [{'expression': f, 'substitutions': env} for f, env in pairs]
        record['answers'] = [int(v) for v in expected]
    elif kind == 'numeric_phrase':
        values = numbers(prose)
        if 'increased by' in prose:
            assert 'sum of' in prose and len(values) == 3
            formula = f'({values[0]}+({values[1]}))+{values[2]}'
        elif prose.strip().startswith('subtract'):
            assert 'from' in prose and len(values) == 2
            formula = f'{values[1]}-({values[0]})'
        elif 'product of' in prose:
            assert len(values) == 2
            formula = f'({values[0]})*{values[1]}'
        else:
            assert 'quotient of' in prose and len(values) == 2
            formula = f'({values[0]})/({values[1]})'
        left, right = item['answer'].rstrip('.').split('=')
        assert ast.dump(ast.parse(normalize(left), mode='eval')) == ast.dump(ast.parse(formula, mode='eval'))
        answer = int(right.strip().replace('−', '-'))
        assert calc(formula) == answer
        record['source_phrase'] = prose.strip()
        record['expression'] = formula
        record['answer'] = answer
    elif kind == 'symbolic_quotient':
        assert 'quotient of' in prose and 'sum of' in prose and numbers(prose) == [-7]
        assert re.search(r'm\s*and\s*n', prose)
        answer = item['answer'].split(',')[0]
        assert ast.dump(ast.parse(normalize(answer), mode='eval')) == ast.dump(ast.parse('-7/(m+n)', mode='eval'))
        assert 'm + n ≠ 0' in item['answer']
        record['expression'] = '-7/(m+n)'
        record['domain'] = 'm+n != 0'
    elif kind == 'symbolic_product':
        assert 'product of' in prose and 'difference of' in prose and numbers(prose) == [-13]
        assert re.search(r'c\s*and\s*d', prose)
        assert item['answer'].startswith('−13(c − d);')
        assert polynomial('-13*(c-d)') == polynomial('-13*c+13*d') == {('c',): -13, ('d',): 13}
        record['expression'] = '-13*(c-d)'
        record['expanded_coefficients'] = {'c': -13, 'd': 13}
    elif kind == 'temperature_difference':
        assert numbers(prose) == [21, 89, -31]
        assert numbers(item['question_gu']) == [21, 89, -31]
        assert 'Celsius' not in prose and 'Fahrenheit' not in prose
        assert item['answer'] == str(89 - (-31)) + '°'
        record['source_quantities'] = [89, -31]
        record['answer_degrees_unspecified_scale'] = 120
    elif kind == 'football':
        assert numbers(prose) == [30, 9, 14, 2] and 'gained 9' in prose and 'lost 14' in prose and 'lost 2' in prose
        assert numbers(item['question_gu']) == [30, 9, 14, 2]
        assert numbers(item['answer']) == [30 + 9 - 14 - 2]
        record['start_and_changes_yards'] = [30, 9, -14, -2]
        record['final_yard_line'] = 23
    elif kind in ('account_withdrawal', 'account_deposit'):
        values = numbers(prose)
        expected = values[0] - values[1] if kind == 'account_withdrawal' else sum(values)
        assert values == numbers(item['question_gu'])
        assert numbers(item['answer']) == [expected]
        assert '$' in item['answer']
        record['source_dollars'] = values
        record['final_balance_dollars'] = expected
    elif kind == 'weight_change':
        assert 'eight women' in prose and 'average of 3 pounds' in prose and 'lost' in prose
        assert numbers(item['answer']) == [-8 * 3, 8 * 3]
        assert 'સરેરાશ' in item['question_gu'] and 'જરૂરી નથી' in ' '.join(item['steps'])
        record['people'] = 8
        record['average_change_pounds'] = -3
        record['total_change_pounds'] = -24
    elif kind == 'open_division_rules':
        assert 'rules for dividing integers' in prose and 'નમૂનાનો જવાબ' in item['answer']
        assert all(text in item['answer'] for text in ['શૂન્ય ન હોય', 'અશૂન્ય', 'ધન', 'ઋણ', 'વ્યાખ્યાયિત નથી'])
        record['semantic_scope'] = 'Equal/unlike nonzero signs; zero dividend allowed, zero divisor undefined, quotient not necessarily an integer.'
    elif kind == 'open_odd_power':
        ts = tokens(next(problem.iter(M + 'math')))
        assert ts[-1] == '?'
        ts = ts[:-1]  # Ignore only terminal question punctuation in calculation.
        at = ts.index('=')
        left, right = expression(ts[:at]), expression(ts[at + 1:])
        assert calc(left) == calc(right) == -64
        assert calc('-4**2') == -16 and calc('(-4)**2') == 16
        assert 'વિષમ' in item['answer']
        record['source_expressions'] = [left, right]
        record['common_value'] = -64
        record['even_exponent_counterexample'] = [-16, 16]
    else:
        raise AssertionError(kind)
    equation_count += equations(item['answer'])
    for step in item['steps']:
        equation_count += equations(step)
    checks.append(record)

rendered = None
if '--rendered' in sys.argv:
    path = LANG / 'output/library/a10-m82455-answers.html'
    page = html.fromstring(path.read_bytes())
    sections = page.xpath('//section[contains(concat(" ",normalize-space(@class)," ")," worked-answer ")]')
    assert len(sections) == len(data['items'])
    for section, item in zip(sections, data['items']):
        sid = item['source_exercise']
        assert section.get('id') == 'answer-' + sid
        ps = section.xpath('./p')
        assert ps[0].xpath('./a/@href') == ['a10-m82455.html#' + sid]
        assert ps[1].text_content() == item['question_gu']
        assert section.xpath('./ol/li/text()') == item['steps']
        assert ps[-1].text_content() == 'જવાબ: ' + item['answer']
    rendered = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'all_questions_answers_and_steps_bound': len(sections)}

receipt = {'schema': 'gujarati-integer-products-added-answers-qa-v1', 'result': 'pass', 'module': 'A10:m82455',
           'source_sha256': data['source_sha256'], 'answer_file_sha256': hashlib.sha256(PATH.read_bytes()).hexdigest(),
           'added_answers': len(checks), 'original_question_math_parts_bound': question_parts,
           'displayed_equality_links_checked': equation_count, 'rendered': rendered, 'checks': checks,
           'limits': ['Separate added answers, not source-supplied solutions.', 'Semantic peer review and actual output reading supplement arithmetic checks.', 'No educator, learner or actual assistive-technology acceptance claimed.']}
(LANG / 'A10_INTEGER_PRODUCTS_ANSWERS_QA.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps({k: receipt[k] for k in ['result', 'added_answers', 'original_question_math_parts_bound', 'displayed_equality_links_checked', 'rendered']}, ensure_ascii=False))
