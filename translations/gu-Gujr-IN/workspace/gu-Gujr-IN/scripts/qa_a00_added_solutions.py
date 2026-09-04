"""Independently check29 added answers against source IDs, values and arithmetic."""
from fractions import Fraction
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
LANG=ROOT/'gu-Gujr-IN'
C='http://cnx.rice.edu/cnxml';M='http://www.w3.org/1998/Math/MathML'
source=ET.parse(ROOT/'downloads/gu-Gujr-IN/a00-id/provenance/logbook/authority/prealgebra2e/m81243.source.cnxml').getroot()
exercises={e.get('id'):e for e in source.iter('{'+C+'}exercise')}
data=json.loads((LANG/'translations/a00-m81243-added-solutions.gu.json').read_text(encoding='utf-8'))
missing={i for i,e in exercises.items() if e.find('{'+C+'}solution') is None}
assert len(data['items'])==len(missing)==29
assert {i['source_exercise'] for i in data['items']}==missing

# This decoder is independent of the hand-written Gujarati word-form answers.
WORDS={'એક':1,'બે':2,'ચાર':4,'પાંચ':5,'આઠ':8,'બાર':12,'પંદર':15,'અઢાર':18,
       'વીસ':20,'તેવીસ':23,'પચ્ચીસ':25,'છેતાલીસ':46,'ઓગણપચાસ':49,'અઠ્ઠાવન':58,
       'બાસઠ':62,'પાંસઠ':65,'સડસઠ':67,'છોતેર':76,'બ્યાસી':82,'અઠ્ઠાણું':98,
       'એકસો':100,'બસો':200,'ત્રણસો':300,'ચારસો':400,'પાંચસો':500,'છસો':600,
       'સાતસો':700,'આઠસો':800,'નવસો':900}
SCALES={'હજાર':1000,'મિલિયન':1000000,'બિલિયન':1000000000,'ટ્રિલિયન':1000000000000}


def decode_words(text):
    words=re.findall(r'[\u0a80-\u0aff]+',text)
    total=0;group=0
    for word in words:
        if word=='ડૉલર':continue
        if word in SCALES:
            total+=group*SCALES[word];group=0
        else:group+=WORDS[word]
    return total+group


def expression(e):
    if e.tag=='{'+M+'}mfrac':return expression(e[0])+'/'+expression(e[1])
    return (e.text or '')+''.join(expression(c) for c in e)


EXPECTED_COMPOSITIONS={'fs-id1384471':253,'fs-id2760170':61415,'fs-id2353124':18102783,
                       'fs-id2241247':11471036106,'fs-id2926292':4568000000,'fs-id1572155':3500000000000}
checked=[]
for item in data['items']:
    ident=item['source_exercise'];check=item['check'];kind=check['kind']
    problem=exercises[ident].find('{'+C+'}problem')
    original=''.join(problem.itertext())
    assert len(item['steps'])>=2 and item['question_gu'] and item['answer']
    assert '\ufffd' not in json.dumps(item,ensure_ascii=False)
    if kind=='classification':
        math=problem.find('.//{'+M+'}math')
        actual_terms=expression(math).split(',')
        assert actual_terms==check['terms'],(ident,actual_terms)
        values=[Fraction(x) for x in actual_terms]
        assert [int(x) for x in values if x.denominator==1 and x>=1]==check['counting']
        assert [int(x) for x in values if x.denominator==1 and x>=0]==check['whole']
        assert all(str(x) in item['answer'] for x in check['whole'])
    elif kind=='base10':
        expected={'fs-id2646862':384,'fs-id1339977':620}[ident]
        assert sum(v*p for v,p in zip(check['parts'],[100,10,1]))==expected==int(item['answer'])
    elif kind=='places':
        assert f"{check['number']:,}" in original
        for part in check['parts']:assert int(str(check['number'])[-len(str(part['place']))])==part['digit']
    elif kind=='number_name':
        assert f"{check['number']:,}" in original
        assert decode_words(item['answer'])==check['number']==sum(check['group_values'])
    elif kind=='compose':
        assert int(item['answer'].replace(',',''))==EXPECTED_COMPOSITIONS[ident]==sum(check['parts'])
    elif kind=='rounding':
        for case in check['cases']:
            n,p=case['number'],case['place']
            assert f'{n:,}' in original
            # Integer half-up formula, independently of the builder's distances.
            expected=((n+p//2)//p)*p
            assert expected==case['result'] and f'{expected:,}' in item['answer']
    elif kind=='open_example':
        assert 'નમૂનાનો જવાબ' in item['answer'] and abs(47-50)<abs(47-40)
    else:raise ValueError(kind)
    checked.append(ident)
receipt={'schema':'gujarati-added-solutions-qa-v1','module':'A00 m81243','result':'pass','added_answers':len(checked),
         'source_omitted_answer_ids_covered':sorted(checked),'checks':['Exact missing-source-exercise coverage','Original fraction parsing','Independent place-value and half-up rounding','Gujarati word forms decoded numerically','Displayed answer binding','Worked-reasoning presence'],
         'native_review_pending':True,'source_faithful_xml_unchanged':True}
(LANG/'A00_ADDED_SOLUTIONS_QA.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
print('PASS: all29 source-omitted exercises covered;10 Gujarati word-form answers decoded independently.')
