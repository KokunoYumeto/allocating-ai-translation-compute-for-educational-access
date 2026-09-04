"""Independent checks against pinned source, not against the answer generator."""
import ast
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from lxml import html
from worked_answer_figures import base10_model, equal_groups_model, hundreds_model

ROOT=Path(__file__).resolve().parents[2];LANG=ROOT/'gu-Gujr-IN'
SOURCE=ROOT/'downloads/gu-Gujr-IN/a00-id/provenance/logbook/authority/prealgebra2e/m81256.source.cnxml'
MEDIA=ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'
C='{http://cnx.rice.edu/cnxml}';M='{http://www.w3.org/1998/Math/MathML}';S='{http://www.w3.org/2000/svg}'
source=ET.parse(SOURCE).getroot();parents={c:p for p in source.iter() for c in p}
exercises={e.get('id'):e for e in source.iter(C+'exercise')}
missing=[i for i,e in exercises.items() if e.find(C+'solution') is None]
path=LANG/'translations/a00-m81256-added-solutions.gu.json';data=json.loads(path.read_text(encoding='utf-8'))
assert data['source_sha256']==hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='73e8bf102d72a8c3891b1f9823c015f288ffcd2315cc452e68e4028429e93b40'
assert len(data['items'])==len(missing)==135
assert [x['source_exercise'] for x in data['items']]==missing


def numbers(text):return [int(n.replace(',','')) for n in re.findall(r'\d[\d,]*',text)]


def operands(problem):
    # Separate XML leaves so adjacent MathML numbers cannot silently concatenate.
    found=numbers(' '.join(problem.itertext()))
    if problem.find('.//'+M+'menclose') is not None:
        assert len(found)==2
        found.reverse()
    return found


def instruction(ex):
    before=list(parents[ex])[:list(parents[ex]).index(ex)]
    paras=[p for p in before if p.tag==C+'para']
    return ' '.join(paras[-1].itertext()) if paras else ''


def calc(node):
    if isinstance(node,ast.Constant) and isinstance(node.value,int):return Fraction(node.value)
    if isinstance(node,ast.BinOp):
        a,b=calc(node.left),calc(node.right)
        if isinstance(node.op,ast.Add):return a+b
        if isinstance(node.op,ast.Sub):return a-b
        if isinstance(node.op,ast.Mult):return a*b
        if isinstance(node.op,ast.Div):return a/b
    raise AssertionError(ast.dump(node))


def equalities(text):
    expr=r'\d[\d,]*(?:\s*[+−×÷]\s*\d[\d,]*)*';count=0
    for match in re.finditer(r'(?<![\d,])'+expr+r'(?:\s*=\s*'+expr+r')+',text):
        parts=[p.strip().replace(',','').replace('−','-').replace('×','*').replace('÷','/') for p in match[0].split('=')]
        values=[calc(ast.parse(p,mode='eval').body) for p in parts]
        assert len(set(values))==1,match[0]
        count+=len(values)-1
    return count


# Independently transcribed nonnumeric phrase meanings and story operand order.
PHRASES={90:([100,65],'−','subtract sixty-five from one hundred'),91:([41,23],'−','twenty-three less than forty-one'),104:([94,33],'×','ninety-four times thirty-three'),105:([10,264],'×','ten times two hundred sixty-four')}
WORDS={'છપ્પન':56,'સાત':7,'બેતાલીસ':42,'છ':6,'ત્રેસઠ':63,'નવ':9,'બોતેર':72,'આઠ':8,'અડતાળીસ':48,'પચ્ચીસ':25,'અઢાર':18,'દસ હજાર પંચ્યાસી':10085,'ત્રણ હજાર ચારસો બાણું':3492,'ચાલીસ':40,'પંદર':15,'પાંચ હજાર સાતસો ચોવીસ':5724,'બે હજાર નવસો અઢાર':2918,'ચૌદ':14,'ચોપન':54}
counts=Counter();equations=0;long_rows=0;model_units=0;chart_cells=0;source_images={};problem_hashes={}
for index,item in enumerate(data['items'],1):
    ex=exercises[item['source_exercise']];problem=ex.find(C+'problem');text=' '.join(problem.itertext());given=operands(problem);check=item['check'];kind=check['kind'];counts[kind]+=1
    problem_hashes[item['source_exercise']]=hashlib.sha256(ET.tostring(problem,encoding='utf-8')).hexdigest()
    assert len(item['steps'])>=2 and item['question_gu'] and item['answer']
    shown=' '.join([item['question_gu'],item['answer']]+item['steps']);assert '\ufffd' not in shown
    equations+=equalities(shown)
    if kind in ('division','division_model','undefined_division'):
        assert given==check['operands'],(index,given,check['operands'])
        n,d=given
        if kind=='undefined_division':
            assert d==0 and n!=0 and item['answer']=='વ્યાખ્યાયિત નથી.'
            assert '0 વડે ભાગાકાર' in shown
            continue
        q,r=divmod(n,d);assert (q,r)==(check['quotient'],check['remainder'])
        assert d*q+r==n and 0<=r<d
        assert f'{d:,} × {q:,} + {r} = {n:,}' in shown
        assert f'0 ≤ {r} < {d:,}' in shown
        if check['trace']:
            trace=check['trace'];digits=str(n);start=trace[0]['position'];prior=0;quotient_digits=[]
            for j,row in enumerate(trace):
                pos=start+j;assert row['position']==pos
                partial=int(digits[:pos+1]) if j==0 else prior*10+int(digits[pos])
                dq,dr=divmod(partial,d)
                assert row==dict(position=pos,partial=partial,digit=dq,product=d*dq,remainder=dr)
                quotient_digits.append(str(dq));prior=dr;long_rows+=1
            assert int(''.join(quotient_digits))==q and prior==r and trace[-1]['position']==len(digits)-1
        if kind=='division_model':
            assert 'model' in instruction(ex).lower()
            assert item['equal_groups_model']==dict(groups=d,each=q)
    elif kind=='word_form':
        assert item['source_notation_mathml']==ET.tostring(problem.find('.//'+M+'math'),encoding='unicode')
        assert given==check['operands']==[WORDS[w] for w in check['word_forms']]
        assert 'words' in instruction(ex)
        assert all(w in item['answer'] for w in check['word_forms'])
        op=check['operator'];tokens=''.join(problem.itertext())
        if op=='+':assert '+' in tokens
        if op=='−':assert '−' in tokens
        if op=='÷':assert '/' in tokens or '÷' in tokens or problem.find('.//'+M+'mfrac') is not None or problem.find('.//'+M+'menclose') is not None
    elif kind=='arithmetic':
        values=check['operands'];op=check['operator']
        if index in PHRASES:
            expected,expected_op,phrase=PHRASES[index];assert phrase in text
            assert (values,op)==(expected,expected_op)
        elif index==106:
            assert given==[4] and 'twice' in text and values==[2,4] and op=='×'
        elif index==80:
            assert 'CNX_BMath_Figure_01_05_214_img.jpg' in problem.find('.//'+C+'image').get('src')
            assert values==[5,12,13] and op=='+' and check['unit_gu']=='સે.મી.'
        elif index==50:assert given==[53,71] and values==[71,53] and op=='−' and 'farther' in text
        elif index==133:assert given==[29,32] and values==[32,29] and op=='+' and 'more than' in text
        else:assert given==values,(index,given,values)
        result=sum(values) if op=='+' else values[0]-values[1] if op=='−' else values[0]*values[1]
        assert result==check['result']
        if 'check by adding' in instruction(ex):assert f'{result:,} + {values[1]:,} = {values[0]:,}' in shown
        # Check the requested operation, not merely the operand values.
        math_tokens=''.join(problem.itertext())
        if problem.find('.//'+M+'math') is not None:
            if '+' in math_tokens:assert op=='+'
            elif '−' in math_tokens:assert op=='−'
            elif any(len(numbers(' '.join(m.itertext())))>1 for m in problem.iter(M+'math')):assert op=='×',(index,op)
    elif kind=='ceiling_story':
        assert given==[25,365] and check['operands']==[365,25]
        n,d=check['operands'];assert check['result']==-(-n//d)==15
        assert d*(check['result']-1)<n<=d*check['result'] and 'આખી' in item['answer']
    elif kind=='check_remainder':
        assert given==[300,8,37,4] and 8*37+4==300 and 0<=4<8
    elif kind=='classification':
        assert given==check['values'];assert check['counting']==[x for x in given if x>0];assert check['whole']==[x for x in given if x>=0]
    elif kind=='hundreds_model':
        assert given==[104] and check['value']==104
        assert item['hundreds_model']==dict(hundreds=1,tens=0,ones=4)
    elif kind=='place_values':
        assert given==[check['number']]+check['digits']
        n=check['number']
        assert all(n//10**p%10==d and v==d*10**p for d,p,v in zip(check['digits'],check['powers'],check['values']))
        assert len(check['values'])==(5 if index==59 else 4)
    elif kind=='number_words':
        expected={60:(204614,[204000,614],'બસો ચાર હજાર છસો ચૌદ'),61:(31640976,[31000000,640000,976],'એકત્રીસ મિલિયન છસો ચાલીસ હજાર નવસો છોતેર')}[index]
        assert given==[expected[0]] and check['groups']==expected[1] and check['word_answer']==expected[2]
        assert sum(check['groups'])==check['value'] and expected[2] in item['answer']
    elif kind=='number_digits':
        phrase,value,parts={62:('six hundred two',602,[600,2]),63:('two billion, four hundred ninety-two million, seven hundred eleven thousand, two',2492711002,[2000000000,492000000,711000,2])}[index]
        assert phrase in text and check['value']==value and check['groups']==parts and sum(parts)==value
    elif kind=='round':
        n,p=check['value'],check['place'];assert given==[n]
        assert check['result']==((n+p//2)//p)*p
        assert check['lower']==n//p*p and check['upper']==check['lower']+p
        context=text+' '+instruction(ex);assert ('hundred' if p==100 else 'ten') in context
    elif kind in ('addition_model','subtraction_model','multiplication_model'):
        assert given==check['operands'] and 'model' in instruction(ex).lower()
        a,b=given;expected=a+b if kind=='addition_model' else a-b if kind=='subtraction_model' else a*b
        assert check['result']==expected
        if 'base10_model' in item:
            values=[10*s['tens']+s['ones'] for s in item['base10_model']['stages']]
            assert values==([a,b,a+b,a+b] if kind=='addition_model' else [a,a,b,a-b])
        else:assert item['equal_groups_model']==dict(groups=a,each=b)
    elif kind=='chart':
        assert 'fill in the missing values' in instruction(ex)
        filename=Path(problem.find('.//'+C+'image').get('src')).name;assert filename==check['source_image']
        assert filename==f'CNX_BMath_Figure_01_05_{224 if index==71 else 228}_img.jpg'
        table=item['answer_table'];op='+' if index==71 else '×'
        assert table['corner_gu']==check['operator']==op and check['blank_count']==28
        assert table['row_headers']==list(range(6,10)) and table['column_headers']==list(range(3,10))
        assert table['cells']==[[(r+c if op=='+' else r*c) for c in range(3,10)] for r in range(6,10)]
        chart_cells+=28
    elif kind=='addition_pair':
        assert given==[n for pair in check['operands'] for n in pair]
        assert check['results']==[sum(pair) for pair in check['operands']]
    else:raise AssertionError((index,kind))
    # Inspect actual rendered models, including per-unit geometry and no overlap.
    for key,render in [('base10_model',base10_model),('equal_groups_model',equal_groups_model),('hundreds_model',hundreds_model)]:
        if key not in item:continue
        element=ET.fromstring(render(item[key]));rects=element.findall('.//'+S+'rect');model_units+=len(rects)
        for svg in element.iter(S+'svg'):
            assert svg.get('role')=='img' and svg.get('aria-label')
            coords=[(int(e.get('x')),int(e.get('y')),int(e.get('width')),int(e.get('height'))) for e in svg.findall(S+'rect')]
            assert len(coords)==len(set(coords))
            for a,(x,y,w,h) in enumerate(coords):
                assert w==h
                for xx,yy,ww,hh in coords[a+1:]:assert x+w<=xx or xx+ww<=x or y+h<=yy or yy+hh<=y
        expected=sum(10*s['tens']+s['ones'] for s in item[key]['stages']) if key=='base10_model' else item[key]['groups']*item[key]['each'] if key=='equal_groups_model' else 104
        assert len(rects)==expected

for filename in ('CNX_BMath_Figure_01_05_224_img.jpg','CNX_BMath_Figure_01_05_228_img.jpg','CNX_BMath_Figure_01_05_214_img.jpg'):
    source_images[filename]=hashlib.sha256((MEDIA/filename).read_bytes()).hexdigest()
assert counts['undefined_division']==3 and chart_cells==56
reader_path=LANG/'output/library/a00-m81256-answers.html'
reader=html.fromstring(reader_path.read_text(encoding='utf-8'))
sections=reader.xpath('//section[@class="worked-answer"]')
assert len(sections)==135
for section,item in zip(sections,data['items']):
    assert section.get('id')=='answer-'+item['source_exercise']
    assert section.xpath('./p/a/@href')==['a00-m81256.html#'+item['source_exercise']]
    assert section.xpath('./p')[1].text_content()==item['question_gu']
    assert [li.text_content() for li in section.xpath('./ol/li')]==item['steps']
    answer=section.xpath('./p[strong]')[0].text_content()
    assert answer=='જવાબ: '+item['answer']
    if 'source_notation_mathml' in item:
        actual=section.xpath('./div[@class="answer-source-notation"]/*')[0]
        expected=ET.fromstring(item['source_notation_mathml'])
        actual_nodes=list(actual.iter());expected_nodes=list(expected.iter());assert len(actual_nodes)==len(expected_nodes)
        for original,rendered in zip(expected_nodes,actual_nodes):
            name=original.tag.rsplit('}',1)[-1]
            attrs={k:v for k,v in rendered.attrib.items()if k!='xmlns'}
            if name=='menclose' and original.get('notation')=='longdiv':
                assert attrs.pop('style')=='border-top:1px solid currentColor;border-left:1px solid currentColor;padding:.08em .16em 0 .18em;margin-left:.18em;border-top-left-radius:.28em'
            assert (name,original.text,dict(original.attrib))==(rendered.tag.rsplit('}',1)[-1],rendered.text,attrs)
    if 'answer_table' in item:
        expected=item['answer_table'];table=section.xpath('.//table')[0]
        assert table.xpath('./caption')[0].text_content()==expected['caption_gu']
        assert [e.text_content() for e in table.xpath('./thead/tr/th')]==[expected['corner_gu']]+list(map(str,expected['column_headers']))
        assert [[int(e.text_content()) for e in row.xpath('./td')] for row in table.xpath('./tbody/tr')]==expected['cells']
    if 'hundreds_model' in item:assert len(section.xpath('.//*[local-name()="rect"]'))==104
    if 'equal_groups_model' in item:assert len(section.xpath('.//*[local-name()="rect"]'))==item['equal_groups_model']['groups']*item['equal_groups_model']['each']
    if 'base10_model' in item:assert len(section.xpath('.//*[local-name()="rect"]'))==sum(10*s['tens']+s['ones'] for s in item['base10_model']['stages'])
receipt=dict(result='pass',source_exercises=313,source_supplied_solutions=178,all_source_omitted_answers=135,
             rendered_answers_questions_all_steps_and_links_checked=135,rendered_html_sha256=hashlib.sha256(reader_path.read_bytes()).hexdigest(),
             companion_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),source_problem_xml_sha256=problem_hashes,
             categories=dict(counts),displayed_numeric_equality_links=equations,long_division_rows=long_rows,
             rendered_countable_model_units=model_units,completed_chart_cells=chart_cells,actual_source_images=source_images,
             limits=['Source problems and shared instructions read in full; all135 source IDs/order pinned.','Source input and reader translation unchanged.','Independent peer and actual-browser reviews are recorded separately.','Native educator, child and assistive-technology reviews pending.'])
(LANG/'A00_DIVISION_ANSWERS_QA.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ('source_problem_xml_sha256','actual_source_images')},ensure_ascii=False))
