"""Source-bound independent QA for59 missing answers, all displayed math and models."""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from worked_answer_figures import equal_groups_model

ROOT=Path(__file__).resolve().parents[2]
LANG=ROOT/'gu-Gujr-IN'
SOURCE=ROOT/'downloads/gu-Gujr-IN/a00-id/provenance/logbook/authority/prealgebra2e/m81255.source.cnxml'
MEDIA=ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'
C='{http://cnx.rice.edu/cnxml}'
M='{http://www.w3.org/1998/Math/MathML}'
source=ET.parse(SOURCE).getroot()
parents={c:p for p in source.iter() for c in p}
exercises={e.get('id'):e for e in source.iter(C+'exercise')}
missing={i for i,e in exercises.items() if e.find(C+'solution') is None}
path=LANG/'translations/a00-m81255-added-solutions.gu.json'
data=json.loads(path.read_text(encoding='utf-8'))
assert len(missing)==len(data['items'])==59
assert {i['source_exercise'] for i in data['items']}==missing
assert data['source_sha256']==hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='1717786daf25223f0712f505768442007c15cf449e382d5596414460d26bd4ba'


def numbers(text):return [int(s.replace(',','')) for s in re.findall(r'\d[\d,]*',text)]


def numeric_math(problem):
    return [n for e in problem.iter() if e.tag in (M+'mn',M+'mtext') for n in numbers(''.join(e.itertext()))]


def calc(node):
    if isinstance(node,ast.Constant) and isinstance(node.value,int):return node.value
    if isinstance(node,ast.BinOp):
        a,b=calc(node.left),calc(node.right)
        if isinstance(node.op,ast.Add):return a+b
        if isinstance(node.op,ast.Sub):return a-b
        if isinstance(node.op,ast.Mult):return a*b
    raise AssertionError(ast.dump(node))


def equations(text):
    # Check all links in full numeric equality chains, not just the last result.
    expr=r'\d[\d,]*(?:\s*[+−×]\s*\d[\d,]*)*'
    count=0
    for match in re.finditer(r'(?<![\d,])'+expr+r'(?:\s*=\s*'+expr+r')+',text):
        parts=match[0].split('=')
        values=[calc(ast.parse(p.strip().replace(',','').replace('−','-').replace('×','*'),mode='eval').body) for p in parts]
        assert len(set(values))==1,match[0]
        count+=len(values)-1
    return count


def instruction(exercise):
    siblings=list(parents[exercise]);before=siblings[:siblings.index(exercise)]
    return ''.join(next(p for p in reversed(before) if p.tag==C+'para').itertext())


# Independent transcription of image headings and blank positions, after actual
# original-image review. No generator or translation metadata is imported here.
GRIDS={'fs-id3323581':(list(range(10)),list(range(10)),'207'),
       'fs-id2160228':(list(range(3,10)),list(range(4,10)),'211'),
       'fs-id2909043':(list(range(3,10)),list(range(6,10)),'215'),
       'fs-id2650134':(list(range(6,10)),list(range(6,10)),'219')}
PARTIAL_BLANK_COLS=[[5,7],[3,6,8],[1,3,6,9],[0,2,4,5,7,9],[4,5,8],[2,5,9],[0,1,4,5,8],[2,4,6,7],[3,5,7],[0,1,5,6,8,9]]
WORDS={'આઠ':8,'છ':6,'ત્રણ':3,'નવ':9,'વીસ':20,'પંદર':15,'ઓગણચાલીસ':39,'ચોસઠ':64}
counts=Counter();eq_count=0;grid_cells=0;new_cells=0;partial_cells=0;model_squares=0;image_hashes={}

for item in data['items']:
    ident=item['source_exercise'];exercise=exercises[ident];problem=exercise.find(C+'problem')
    prose=''.join(problem.itertext()).strip();check=item['check'];kind=check['kind'];counts[kind]+=1
    assert len(item['steps'])>=2 and item['question_gu'] and item['answer']
    assert '\ufffd' not in json.dumps(item,ensure_ascii=False)
    visible=' '.join([item['question_gu'],item['answer']]+item['steps'])
    eq_count+=equations(visible)
    if kind=='word_form':
        original=numeric_math(problem)
        assert original==check['operands']==[WORDS[w] for w in check['word_forms']]
        assert 'notation to words' in instruction(exercise) and '=' not in item['answer']
        assert all(w in item['answer'] for w in check['word_forms'])
    elif kind=='chart':
        rows,cols,suffix=GRIDS[ident];table=item['answer_table']
        assert table['row_headers']==rows and table['column_headers']==cols
        filename=Path(problem.find('.//'+C+'image').get('src')).name
        assert filename==check['source_image']==f'CNX_BMath_Figure_01_04_{suffix}.jpg'
        image_hashes[filename]=hashlib.sha256((MEDIA/filename).read_bytes()).hexdigest()
        assert len(table['cells'])==len(rows)
        for ri,(r,row) in enumerate(zip(rows,table['cells'])):
            assert len(row)==len(cols)
            for ci,(c,value) in enumerate(zip(cols,row)):
                assert value==sum(r for _ in range(c))
                expected_blank=suffix!='207' or ci in PARTIAL_BLANK_COLS[ri]
                assert check['source_visible_cells'][ri][ci]==(None if expected_blank else value)
                new_cells+=expected_blank;grid_cells+=1
        assert check['filled_blank_count']==sum(v is None for row in check['source_visible_cells'] for v in row)
        assert 'missing values' in instruction(exercise)
    elif kind=='commuted_pair':
        original=[numeric_math(m) for m in problem.iter(M+'math')]
        assert original==check['operands']==[[8,9],[9,8]]
        assert check['results']==[a*b for a,b in original]==[72,72]
        assert item['answer']=='(a) 72 (b) 72.'
    elif kind=='mixed_arithmetic':
        original=numbers(prose)
        reverse=any(s in prose for s in ['more than','less than','subtract'])
        expected=original[::-1] if reverse else original
        assert check['operands']==expected
        op='−' if any(s in prose for s in ['−','difference','subtract','less than']) else '+'
        assert op==check['operator']
        a,b=expected;result=a-b if op=='−' else a+b
        assert result==check['result'] and item['answer']==f'{a:,} {op} {b:,} = {result:,}'
    elif kind in ('multiply','phrase_multiply','story_multiply','equal_groups'):
        if kind in ('multiply','equal_groups'):expected=numeric_math(problem)
        elif prose=='forty-eight times seventy-one':expected=[48,71]
        elif prose=='ten times two hundred fifty-five':expected=[10,255]
        else:
            expected=numbers(re.sub(r'\bfour\b','4',prose))
            if 'twice' in prose:expected=[2]+expected
        assert check['operands']==expected,(ident,expected,check['operands'])
        a,b=expected;result=a*b
        assert result==check['result']
        if kind=='equal_groups':
            assert 'model the multiplication' in instruction(exercise)
            model=item['equal_groups_model'];assert [model['groups'],model['each']]==expected
            svg=ET.fromstring(equal_groups_model(model));rects=list(svg.iter('{http://www.w3.org/2000/svg}rect'))
            assert len(rects)==result
            assert sorted(Counter(r.get('y') for r in rects).values())==[b]*a
            assert len({(r.get('x'),r.get('y')) for r in rects})==result
            model_squares+=len(rects)
        else:
            assert item['answer'].startswith(f'{a:,} × {b:,} = {result:,}')
        if 'answer_table' in item:
            t=item['answer_table'];rows,cols=t['row_headers'],t['column_headers']
            assert sum(rows)==b and sum(cols)==a
            assert all(len(str(v).rstrip('0'))==1 for v in rows+cols)
            assert len(t['cells'])==len(rows)
            for r,row in zip(rows,t['cells']):
                assert len(row)==len(cols)
                for c,value in zip(cols,row):assert value==r*c;partial_cells+=1
            assert sum(map(sum,t['cells']))==result
        if kind=='story_multiply':
            if 'area' in prose:assert check['unit_gu']=='ચોરસ ફૂટ' and 'ચોરસ ફૂટ' in item['answer']
            if 'Salary' in prose:assert check['unit_gu']=='ડૉલર પ્રતિ વર્ષ' and 'માત્ર વાર્ષિક વધારો' in visible
            if 'NCAA' in prose:assert 'આજના નિયમોની પુષ્ટિ' in visible
    elif kind=='open_example':
        assert 'models' in prose and 'multiplication facts' in prose
        assert check['groups']*check['each']==check['result']
        assert 'નમૂનાનો જવાબ' in item['answer'] and 'જુદા જવાબો પણ માન્ય' in visible
    else:raise AssertionError(kind)

receipt=dict(schema='gujarati-added-solutions-qa-v1',module='A00 m81255',result='pass',added_answers=59,kinds=dict(counts),
             displayed_equality_links_checked=eq_count,completed_chart_cells=grid_cells,filled_source_blanks=new_cells,
             partial_product_cells=partial_cells,model_unit_squares=model_squares,source_image_sha256=image_hashes,
             source_sha256=data['source_sha256'],target_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
             source_omitted_answer_ids_covered=sorted(missing),native_review_pending=True,source_faithful_xml_unchanged=True,
             checks=['Exact source missing-answer coverage','Original group instructions for words/models/charts','Source operands including English four and twice',
                     'All displayed numeric equality chains','Independent actual-image chart dimensions and blank mask','Partial-product value conservation',
                     'Rendered countable model squares','Mixed addition/subtraction direction','Area square units; annual increase rather than total salary'])
(LANG/'A00_MULTIPLICATION_ANSWERS_QA.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(f'PASS:59answers;{eq_count}equality links;{grid_cells}chartcells;{new_cells}filledblanks;{partial_cells}partialproductcells;{model_squares}modelsquares.')
