"""Check companion answers against pinned problems, independently of author data."""
import ast
from collections import Counter, defaultdict
import copy
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
LANG=ROOT/'gu-Gujr-IN'
sys.path.insert(0,str(LANG/'translations'))
from qa_a10_m82453_math import expression, calc

C='{http://cnx.rice.edu/cnxml}'
M='{http://www.w3.org/1998/Math/MathML}'
SOURCE=ROOT/'downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82453/index.cnxml'
source=ET.parse(SOURCE).getroot()
parents={c:p for p in source.iter() for c in p}
exercises={e.get('id'):e for e in source.iter(C+'exercise')}
path=LANG/'translations/a10-m82453-added-solutions.gu.json'
data=json.loads(path.read_text(encoding='utf-8'))
missing={key for key,e in exercises.items() if e.find(C+'solution') is None}
assert len(missing)==len(data['items'])==51
assert {i['source_exercise'] for i in data['items']}==missing
assert data['source_sha256']==hashlib.sha256(SOURCE.read_bytes()).hexdigest()

def normalize(s):
    s=s.strip().replace(',','').translate(str.maketrans({'−':'-','·':'*','×':'*','÷':'/','[':'(',']':')'}))
    s=re.sub('[²³⁵]',lambda m:'**'+{'²':'2','³':'3','⁵':'5'}[m[0]],s)
    s=re.sub(r'(?<=[0-9)])(?=[a-z(])','*',s)
    s=re.sub(r'(?<=[a-z])(?=\()','*',s)
    return s

def polynomial(s):
    """Exact coefficient dictionary; unlike sampling, proves these identities."""
    def clean(d):return {k:v for k,v in d.items() if v}
    def add(a,b):
        out=dict(a)
        for k,v in b.items():out[k]=out.get(k,0)+v
        return clean(out)
    def mul(a,b):
        out={}
        for ka,va in a.items():
            for kb,vb in b.items():
                powers=Counter(dict(ka));powers.update(dict(kb));k=tuple(sorted(powers.items()))
                out[k]=out.get(k,0)+va*vb
        return clean(out)
    def walk(n):
        if isinstance(n,ast.Expression):return walk(n.body)
        if isinstance(n,ast.Constant) and isinstance(n.value,int):return {():n.value} if n.value else {}
        if isinstance(n,ast.Name):return {((n.id,1),):1}
        if isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.USub):return {k:-v for k,v in walk(n.operand).items()}
        if isinstance(n,ast.BinOp):
            a=walk(n.left)
            if isinstance(n.op,ast.Pow):
                assert isinstance(n.right,ast.Constant) and 0<=n.right.value<=5
                out={():1}
                for _ in range(n.right.value):out=mul(out,a)
                return out
            b=walk(n.right)
            if isinstance(n.op,ast.Add):return add(a,b)
            if isinstance(n.op,ast.Sub):return add(a,{k:-v for k,v in b.items()})
            if isinstance(n.op,ast.Mult):return mul(a,b)
        raise ValueError(ast.dump(n))
    return walk(ast.parse(s,mode='eval'))

def comma_expressions(math):
    row=math[0];result=[];part=ET.Element(M+'mrow')
    for child in row:
        if child.tag==M+'mo' and child.text==',':
            result.append(expression(part));part=ET.Element(M+'mrow')
        else:part.append(copy.deepcopy(child))
    result.append(expression(part))
    return result

def additive_terms(formula):
    def split(n):
        if isinstance(n,ast.BinOp) and isinstance(n.op,ast.Add):return split(n.left)+split(n.right)
        return [polynomial(ast.unparse(n))]
    return split(ast.parse(formula,mode='eval').body)

def displayed_equations(text):
    count=0
    # Gujarati sentences delimit these Latin-variable/numeric math runs.
    for run in re.findall(r'[a-z0-9²³⁵+−·×÷*/=(),\[\] \t]+',text):
        if '=' not in run:continue
        if run.strip()=='=':continue  # Description of the equality symbol.
        if re.fullmatch(r'\s*[a-z]\s*=\s*\d+(?:\s*,\s*[a-z]\s*=\s*\d+)*\s*',run):continue
        parts=[normalize(p.strip()) for p in run.strip().split('=')]
        # Standalone x = 7 etc are assignments, not asserted identities.
        if len(parts)==2 and re.fullmatch('[a-z]',parts[0]):continue
        try:
            if any(re.search('[a-z]',p) for p in parts):
                values=[polynomial(p) for p in parts]
            else:values=[calc(p,{}) for p in parts]
        except (SyntaxError,ValueError,KeyError):
            raise AssertionError(('Unparsed displayed equation',run))
        assert all(v==values[0] for v in values),run
        count+=len(values)-1
    return count

word_forms={
 '3·9':'Three times nine.',
 'x+11':'The sum of x and eleven.',
 '(4)(8)':'The product of four and eight.',
 '17<35':'Seventeen is less than thirty-five.',
 '6n=36':'Six times n equals thirty-six.',
 'y−4>8':'The difference of y and four is greater than eight.',
 'a≠1·12':'a is not equal to the product of one and twelve.',
}
counts=Counter();checks=[];equations=0
for item in data['items']:
    ident=item['source_exercise'];kind=item['check']['kind'];counts[kind]+=1
    ex=exercises[ident];problem=ex.find(C+'problem');math=problem.findall('.//'+M+'math')
    prose=' '.join(''.join(problem.itertext()).split())
    answer=item['answer'];assert answer and len(item['steps'])>=2
    assert '\ufffd' not in json.dumps(item,ensure_ascii=False)
    equations+=displayed_equations(' '.join(item['steps']))
    result={'source_exercise':ident,'kind':kind}
    if kind=='word_form':
        formula=''.join(math[0].itertext())
        assert item['english_answer']==word_forms[formula]
        siblings=list(parents[ex]);instruction=next(e for e in reversed(siblings[:siblings.index(ex)]) if e.tag==C+'para')
        assert 'English' in ''.join(instruction.itertext())
        result['source_formula']=formula
    elif kind=='classification':
        equality=any(e.tag==M+'mo' and e.text=='=' for e in math[0].iter())
        assert answer==('સમીકરણ' if equality else 'પદાવલી')
    elif kind in {'numeric','numeric_pair','substitution'}:
        env={}
        if kind=='substitution':
            env={name:int(value) for m in math[1:] for name,value in re.findall(r'([a-z])=(\d+)',''.join(m.itertext()))}
            assert env
        formulas=[expression(m) for m in (math[:1] if kind=='substitution' else math)]
        actual=[calc(f,env) for f in formulas]
        claimed=[int(v) for v in re.findall(r'\) (\d+)',answer)] if kind=='numeric_pair' else [int(answer.replace(',',''))]
        assert actual==claimed,(ident,formulas,env,actual,claimed)
        result.update(source_expressions=formulas,source_substitutions=env,answers=claimed)
    elif kind=='coefficient':
        formula=expression(math[0]) if math else normalize(prose)
        terms=polynomial(formula);assert len(terms)==1
        assert int(answer)==next(iter(terms.values()))
    elif kind=='like_terms':
        original=[polynomial(f) for f in comma_expressions(math[0])]
        groups=defaultdict(list)
        for term in original:
            assert len(term)==1
            groups[next(iter(term))].append(term)
        expected_groups=[g for g in groups.values() if len(g)>1]
        expected_unpaired=[g[0] for g in groups.values() if len(g)==1]
        claimed=[[polynomial(normalize(t)) for t in g] for g in item['groups']]
        claimed_unpaired=[polynomial(normalize(t)) for t in item['unpaired']]
        assert claimed==expected_groups and claimed_unpaired==expected_unpaired
        assert all(t in answer for group in item['groups'] for t in group)
    elif kind=='terms':
        assert [polynomial(normalize(t)) for t in item['terms']]==additive_terms(expression(math[0]))
        assert answer==', '.join(item['terms'])+'.'
    elif kind=='polynomial':
        assert polynomial(expression(math[0]))==polynomial(normalize(answer))
    elif kind=='phrase':
        # Parse the original word order. These bindings are source prose,
        # not the author's check metadata or numeric answer constants.
        match=re.fullmatch(r'the (difference|product|quotient|sum) of (.+) and (.+)',prose)
        if match:
            operation,a,b=match.groups();formula=normalize(a)+{'difference':'-','product':'*','quotient':'/','sum':'+'}[operation]+normalize(b)
        elif prose=='seven times the difference of y and one':formula='7*(y-1)'
        elif 'number of girls' in prose:
            assert '4 less than the number of boys' in prose and 'Let b represent' in prose;formula='b-4'
        elif 'Jeannette' in prose:
            assert '$5 and $10' in prose and 'three more than six times the number of tens' in prose and 'Let t represent' in prose;formula='6*t+3'
        else:raise AssertionError(prose)
        actual=normalize(answer)
        if '/' in formula:
            names=set(re.findall('[a-z]',formula));assert '/' in actual
            # Quotient numerator/denominator are compared structurally too.
            assert ast.dump(ast.parse(formula,mode='eval'))==ast.dump(ast.parse(actual,mode='eval'))
            for n in [0,1,7]:assert calc(formula,{v:n for v in names})==calc(actual,{v:n for v in names})
        else:assert polynomial(formula)==polynomial(actual)
        result['source_derived_expression']=formula
    elif kind=='insurance_story':
        amounts=[int(v.replace(',','')) for v in re.findall(r'\$(\d[\d,]*)',prose)]
        assert amounts==[2500,2500,2500,19400]
        assert [int(v.replace(',','')) for v in re.findall(r'\$(\d[\d,]*)',answer)]==[amounts[0],amounts[-1]-amounts[0]]
    elif kind=='open_order':
        assert 'order of operations' in prose
        assert calc('2+6*3',{})==20 and calc('(2+6)*3',{})==24
        assert 'નમૂનાનો જવાબ' in answer
    elif kind=='open_grouping':
        assert '4 times the sum of x and y' in prose and 'the sum of 4 times x and y' in prose
        assert '4(x + y)' in answer and '4x + y' in answer
        assert calc('4*(x+y)',{'x':2,'y':3})==20 and calc('4*x+y',{'x':2,'y':3})==11
        assert polynomial('4*(x+y)-(4*x+y)')=={(('y',1),):3}
    else:raise AssertionError(kind)
    checks.append(result)

receipt={'schema':'gujarati-algebra-added-answers-qa-v1','result':'pass','module':'A10:m82453',
         'source_exercises_without_answers':len(missing),'added_answers':len(checks),'types':dict(counts),
         'displayed_equations_checked':equations,'source_sha256':data['source_sha256'],
         'answer_file_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'checks':checks,
         'limitations':['Gujarati prose and English word-form equivalence require semantic review beyond symbolic checks.','These are separate added answers, not supplied source solutions.','Native educator and pupil review remain pending.']}
(LANG/'A10_ALGEBRA_ANSWERS_QA.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:receipt[k] for k in ['result','added_answers','displayed_equations_checked','types']},ensure_ascii=False))
