"""Build and check the next source-faithful section and its separate companion.

This incremental renderer does not replace the frozen U01 edition. No downloads.
"""
from pathlib import Path
import argparse, ast, copy, hashlib, html, json, operator, re, shutil
import xml.etree.ElementTree as ET
from build import C, M, L, STYLE, NOTICE, local, render, write
from acquire_canon import Readable
from number_names import parse_name

def digest(data): return hashlib.sha256(data).hexdigest()
def number(text): return int(text.translate(str.maketrans('০১২৩৪৫৬৭৮৯','0123456789')).replace(',',''))
def round_half_up(n,step):
    assert n>=0 and step in (10,100,1000,10000,100000,1000000,10000000,100000000,1000000000)
    result=((n+step//2)//step)*step
    lower=(n//step)*step;upper=lower+step
    # Independently choose the closest bound, taking the larger one in a tie.
    assert result==min((lower,upper),key=lambda candidate:(abs(candidate-n),-candidate))
    return result
def calc(text):
    text=text.translate(str.maketrans('০১২৩৪৫৬৭৮৯×','0123456789*')).replace(',','')
    def visit(n):
        if isinstance(n,ast.Constant) and type(n.value) is int:return n.value
        if isinstance(n,ast.BinOp) and isinstance(n.op,(ast.Add,ast.Mult)):
            return (operator.add if isinstance(n.op,ast.Add) else operator.mul)(visit(n.left),visit(n.right))
        raise ValueError(text)
    return visit(ast.parse(text,mode='eval').body)

def build(unit):
    spec=json.loads((L/'units'/(unit+'.json')).read_text(encoding='utf-8'))
    original=L.parent/'downloads/bn-Beng-BD/openstax-canonical/modules'/spec['module']/'index.cnxml'
    assert digest(original.read_bytes())==spec['canonical_module_sha256']
    whole=ET.parse(original).getroot()
    source=ET.Element('{'+C+'}document',{'data-source-module':spec['module']})
    for anchor in spec['sections']:
        found=[e for e in whole.iter() if e.get('id')==anchor]
        assert len(found)==1 and local(found[0])=='section',anchor
        source.append(copy.deepcopy(found[0]))
    witness=ET.tostring(source,encoding='utf-8',xml_declaration=True)
    (L/spec['witness']).write_bytes(witness)
    translated=copy.deepcopy(source)
    mapping=json.loads((L/spec['strings']).read_text(encoding='utf-8'))
    used=set();slots=0
    for e in translated.iter():
        for prop in ('text','tail','alt','aria-label'):
            attr=prop in ('alt','aria-label')
            value=e.get(prop) if attr else getattr(e,prop)
            if value in mapping:
                if attr:e.set(prop,mapping[value])
                else:setattr(e,prop,mapping[value])
                used.add(value);slots+=1
            elif value and re.search('[A-Za-z]',value):raise ValueError('Untranslated: '+repr(value))
    assert used==set(mapping),'Unused strings: '+repr(set(mapping)-used)
    for override in spec.get('text_overrides',[]):
        nodes=[e for e in translated.iter() if e.get('id')==override['id']]
        assert len(nodes)==1 and local(nodes[0]) not in ('mn','mo','mtext','math','mrow','mspace')
        assert nodes[0].text==override['expected']
        nodes[0].text=override['text']
    translated.set('{http://www.w3.org/XML/1998/namespace}lang',spec['locale'])
    for a,b in zip(source.iter(),translated.iter()):
        assert a.tag==b.tag
        omitted={'alt','aria-label','{http://www.w3.org/XML/1998/namespace}lang'}
        assert {k:v for k,v in a.attrib.items() if k not in omitted}=={k:v for k,v in b.attrib.items() if k not in omitted}
        if local(a) in ('mn','mo','mspace') or (local(a)=='mtext' and re.fullmatch(r'[$0-9, .;]+',a.text or '')):assert a.text==b.text
    tr=ET.tostring(translated,encoding='utf-8',xml_declaration=True)
    (L/spec['translation']).parent.mkdir(parents=True,exist_ok=True)
    (L/spec['translation']).write_bytes(tr)
    media=[]
    for e in source.iter('{'+C+'}image'):
        name=Path(e.get('src')).name
        upstream=L.parent/'downloads/bn-Beng-BD/openstax-canonical/media'/name
        dest=L/'translations/media'/name
        if not dest.exists():shutil.copyfile(upstream,dest)
        assert dest.read_bytes()==upstream.read_bytes()
        assert (L/spec['translation']).parent.joinpath(e.get('src')).resolve()==dest.resolve()
        media.append({'path':dest.relative_to(L).as_posix(),'sha256':digest(dest.read_bytes())})
    if spec.get('practice_answers'):
        from practice_answers import generate,verify
        generate()
    companion_text=(L/spec['companion']).read_text(encoding='utf-8')
    companion=ET.fromstring(companion_text)
    byid={e.get('id'):e for e in companion.iter() if e.get('id')}
    prefix='bd-'+unit.lower()
    for key in spec['assessment_ids']:
        assert prefix+'-'+key in byid,key
        answer=''.join(byid[prefix+'-a-'+key].itertext())
        assert len(answer)>30,(key,'Missing worked answer')
        if key in spec.get('answer_name_contracts',{}):
            assert spec['answer_name_contracts'][key] in answer,(key,'Number name differs')
            assert parse_name(spec['answer_name_contracts'][key])==spec['answer_number_contracts'][key],key
    for case in spec.get('write_answer_contracts',[]):
        question=''.join(byid[prefix+'-'+case['id']].itertext())
        answer=byid[prefix+'-a-'+case['id']]
        assert case['name'] in question
        assert parse_name(case['name'])==case['number']
        assert int(answer.get('data-answer-number'))==case['number']
        tokens=re.findall(r'[০-৯0-9]+(?:,[০-৯0-9]+)*',''.join(answer.itertext()))
        assert case['number'] in [number(x) for x in tokens]
    pattern=r'([০-৯0-9][০-৯0-9,]*(?:\s*[+×]\s*[০-৯0-9][০-৯0-9,]*)*)\s*=\s*([০-৯0-9][০-৯0-9,]*(?:\s*[+×]\s*[০-৯0-9][০-৯0-9,]*)*)'
    equations=[];regrouped=0
    for e in companion.iter():
        if local(e) in ('p','td'):
            text=''.join(e.itertext())
            for match in re.finditer(pattern,text):
                assert calc(match[1])==calc(match[2]),match.group()
                equations.append(match.group())
        if e.get('data-same-integer'):
            tokens=re.findall(r'[০-৯0-9]+(?:,[০-৯0-9]+)+',''.join(e.itertext()))
            assert tokens
            for token in tokens:assert number(token)==int(e.get('data-same-integer')),token
            regrouped+=len(tokens)
    assert len(equations)>=spec.get('minimum_equations',30)
    exercises={e.get('id'):e for e in source.iter('{'+C+'}exercise')}
    checked_cases=0
    for case in spec['source_place_cases']:
        exercise=exercises[case['exercise']]
        assert exercise.find('{'+C+'}solution') is not None
        source_number=next(exercise.iter('{'+M+'}mn')).text
        assert number(source_number)==case['number']
        tables=[e for e in companion.iter('table') if e.get('data-exercise')==case['exercise']]
        assert len(tables)==1
        rows=list(tables[0].find('tbody'))
        assert len(rows)==len(case['digits'])
        for row,digit,power in zip(rows,case['digits'],case['powers']):
            assert (case['number']//10**power)%10==digit
            assert int(row.get('data-digit'))==digit and int(row.get('data-power'))==power
            assert int(row.get('data-value'))==digit*10**power
            assert number(''.join(row[0].itertext()))==digit
            assert number(''.join(row[2].itertext()).split('=')[-1].strip())==digit*10**power
            checked_cases+=1
    naming_cases=0
    translated_exercises={e.get('id'):e for e in translated.iter('{'+C+'}exercise')}
    for case in spec.get('source_name_cases',[]):
        exercise=exercises[case['exercise']]
        assert case['number'] in [number(e.text) for e in exercise.iter('{'+M+'}mn')]
        assert sum(value*10**power for value,power in case['groups'])==case['number']
        assert parse_name(case['name'])==case['number'],case
        answer=translated_exercises[case['exercise']].find('{'+C+'}solution')
        assert answer is not None and case['name'] in ''.join(answer.itertext())
        supplements=[e for e in companion.iter('section') if e.get('data-name-exercise')==case['exercise']]
        assert len(supplements)==1 and int(supplements[0].get('data-number'))==case['number']
        assert case['name'] in ''.join(supplements[0].itertext())
        naming_cases+=1
    writing_cases=0
    for case in spec.get('source_write_cases',[]):
        exercise=translated_exercises[case['exercise']]
        problem=''.join(exercise.find('{'+C+'}problem').itertext())
        answer=''.join(exercise.find('{'+C+'}solution').itertext())
        if 'name' in case:
            assert case['name'] in problem and parse_name(case['name'])==case['number']
        else:
            assert case['given']*10**case['power']==case['number']
            assert case['scale_word'] in problem
            assert case['given'] in [number(x) for x in re.findall(r'[0-9]+(?:,[0-9]+)*',problem)]
            assert case['unit'] in answer
        assert case['number'] in [number(x) for x in re.findall(r'[0-9]+(?:,[0-9]+)*',answer)]
        supplements=[e for e in companion.iter('p') if e.get('data-write-exercise')==case['exercise'] and e.get('data-number')==str(case['number'])]
        assert len(supplements)==1 and len(''.join(supplements[0].itertext()))>40
        writing_cases+=1
    rounding_cases=0
    for case in spec.get('source_round_cases',[]):
        exercise=translated_exercises[case['exercise']]
        problem=''.join(exercise.find('{'+C+'}problem').itertext())
        answer=''.join(exercise.find('{'+C+'}solution').itertext())
        assert case['number'] in [number(x) for x in re.findall(r'[0-9]+(?:,[0-9]+)*',problem)]
        assert case['place_word'] in problem
        assert round_half_up(case['number'],case['step'])==case['answer']
        assert case['answer'] in [number(x) for x in re.findall(r'[0-9]+(?:,[0-9]+)*',answer)]
        supplements=[e for e in companion.iter('p') if e.get('data-round-exercise')==case['exercise'] and e.get('data-round-number')==str(case['number'])]
        assert len(supplements)==1 and len(''.join(supplements[0].itertext()))>40
        assert supplements[0].get('data-round-step')==str(case['step'])
        assert supplements[0].get('data-round-result')==str(case['answer'])
        rounding_cases+=1
    companion_rounds=0
    for e in companion.iter():
        if e.get('data-round-number') is not None:
            n,step,result=[int(e.get('data-round-'+key)) for key in ('number','step','result')]
            assert round_half_up(n,step)==result
            tokens=[number(x) for x in re.findall(r'[০-৯0-9]+(?:,[০-৯0-9]+)*',''.join(e.itertext()))]
            assert n in tokens and result in tokens
            companion_rounds+=1
    for case in spec.get('round_answer_contracts',[]):
        answer=byid[prefix+'-a-'+case['id']]
        question=''.join(byid[prefix+'-'+case['id']].itertext())
        assert case['number'] in [number(x) for x in re.findall(r'[০-৯0-9]+(?:,[০-৯0-9]+)*',question)]
        assert case['place_word'] in question
        assert answer.get('data-round-number')==str(case['number'])
        assert answer.get('data-round-step')==str(case['step'])
        assert answer.get('data-round-result')==str(case['answer'])
    checked_exercises={case['exercise'] for field in ('source_place_cases','source_name_cases','source_write_cases','source_round_cases') for case in spec.get(field,[])}
    practice_receipt={}
    if spec.get('practice_answers'):
        practice_checked,practice_receipt=verify(source,translated,companion)
        checked_exercises.update(practice_checked)
    assert checked_exercises==set(exercises),'Unverified source exercise'
    for erratum in spec.get('alt_errata',[]):
        media_node=next(e for e in translated.iter() if e.get('id')==erratum['id'])
        assert erratum['required'] in media_node.get('alt','') and erratum['forbidden'] not in media_node.get('alt','')
    canon=json.loads((L/'canon/register.json').read_text(encoding='utf-8'))
    examples={x['id']:x for x in canon['examples']}
    receipts={x['id']:x for x in json.loads((L/'canon/download-receipt.json').read_text(encoding='utf-8'))}
    for ref in spec['canon_consulted']:
        item=receipts[examples[ref]['source']]
        path=L.parent/'downloads/bn-Beng-BD/canon'/item['id']
        raw=path.with_suffix('.html').read_bytes()
        assert digest(raw)==item['sha256']
        text=path.with_suffix('.txt').read_text(encoding='utf-8')
        assert digest(text.encode('utf-8'))==item['text_sha256']
        parser=Readable();parser.feed(raw.decode('utf-8'))
        assert text=='\n'.join(' '.join(line.split()) for line in ''.join(parser.parts).splitlines() if line.strip())
    style=STYLE.replace('../assets/','../../assets/')+'\n.circled{list-style:none;padding-left:0}td{overflow-wrap:anywhere}\n'
    if spec.get('edition_font'):
        assert (L/'assets'/spec['edition_font']).is_file()
        style=style.replace('NumeracyBangla.ttf',spec['edition_font'])
    attribution=NOTICE.replace('module m81243, sections fs-id1830385 and fs-id2340048','module '+spec['module']+', section '+', '.join(spec['sections']))
    notice=spec.get('faithful_notice','এই অংশে উৎসের আন্তর্জাতিক তিন-অঙ্কের কমার দল, 0–9 অঙ্ক ও বড় সংখ্যাগুলো রাখা হয়েছে। এগুলো দেশীয় লক্ষ-কোটির ঘর হিসেবে পুনর্নামকরণ করা হয়নি। চিত্রগুলো বাংলা পাঠ্য বর্ণনা হিসেবে দেওয়া হয়েছে। এটি U02-এর প্রথম অংশ; পুরো ইউনিট নয়।')
    faithful='<article id="faithful"><h2>উৎসের গঠন অক্ষুণ্ণ রেখে অনুবাদ</h2><p class="notice">'+html.escape(notice)+'</p>'+render(translated)+'</article>'
    page='<!DOCTYPE html>\n<html lang="bn-Beng-BD"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><title>'+html.escape(spec['title'])+'</title><style>'+style+'</style></head><body><a class="skip" href="#'+prefix+'-companion">মূল পাঠে যাই</a><main><header><p class="kicker">BANGLADESH BANGLA · '+unit+' · DRAFT</p><nav aria-label="পাঠের অংশ"><a href="#'+prefix+'-answers">সব উত্তর</a> · <a href="#faithful">উৎসের অনুবাদ</a> · <a href="#attribution">উৎস</a></nav></header>'+companion_text+faithful+attribution+'</main></body></html>\n'
    doc=ET.fromstring(page.split('\n',1)[1])
    ids=[e.get('id') for e in doc.iter() if e.get('id')]
    assert len(ids)==len(set(ids))
    source_ids={e.get('id') for e in source.iter() if e.get('id')}
    assert source_ids<=set(ids)
    links=[e.get('href')[1:] for e in doc.iter('a') if e.get('href','').startswith('#')]
    assert set(links)<=set(ids)
    assert all(e.get('scope') for e in doc.iter('th'))
    assert not list(doc.iter('script'))
    assert not re.search(r'TODO|TBD|\ufffd',page)
    for p in doc.iter('p'):assert not any(local(e) in ('div','table','section','p','ul','ol','figure') for e in list(p.iter())[1:])
    out=L/'output'/unit
    for anchor in doc.iter('a'):
        href=anchor.get('href','')
        if href and not href.startswith(('#','http://','https://')):assert (out/href).resolve().is_file(),href
    write(out/'index.html',page)
    receipt={'unit':unit,'status':'structural_math_pass','source_module':spec['module'],'source_sections':spec['sections'],
             'source_elements_including_container':len(list(source.iter())),'source_ids_preserved':len(source_ids),
             'translation_slots':slots,'unique_translation_strings':len(used),'source_exercises':len(exercises),
             'all_source_solutions_retained':True,'source_mathml_unchanged':True,'media':media,
             'companion_items_with_worked_answers':len(spec['assessment_ids']),'arithmetic_equalities_checked':len(equations),
             'regrouped_number_forms_checked':regrouped,'source_digit_place_contributions_checked':checked_cases,
             'source_number_names_independently_parsed':naming_cases,'companion_number_names_parsed':len(spec.get('answer_name_contracts',{})),
             'source_written_number_cases_checked':writing_cases,'companion_written_numbers_checked':len(spec.get('write_answer_contracts',[])),
             'source_rounding_cases_checked':rounding_cases,'companion_rounding_results_checked':companion_rounds,
             'practice_answers':practice_receipt,'unit_specification_sha256':digest((L/'units'/(unit+'.json')).read_bytes()),
             'internal_links_checked':len(links),'canon_examples_checked':spec['canon_consulted'],
             'witness_sha256':digest(witness),'translation_sha256':digest(tr),'html_sha256':digest(page.encode('utf-8')),
             'input_sha256':{name:digest((L/spec[name]).read_bytes()) for name in ('strings','companion')},
             'limits':spec['limits']+['No visual browser or native-teacher validation claimed']}
    if spec.get('practice_answers'):receipt['practice_answer_input_sha256']=digest((L/spec['practice_answers']).read_bytes())
    write(out/'qa-receipt.json',json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    return receipt

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('unit');args=parser.parse_args()
    first=build(args.unit)
    assert build(args.unit)==first,'Nondeterministic section build'
    print(json.dumps(first,ensure_ascii=False,indent=2))
