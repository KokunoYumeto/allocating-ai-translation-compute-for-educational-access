"""Separate AX-3 addition lesson and all-source worked answers, never source inserts."""
import copy, html, json, re
import xml.etree.ElementTree as ET
from pathlib import Path
import build_module as b
from number_names import WORDS, parse_name
from acquire_canon import Readable

DIGITS = str.maketrans('0123456789','০১২৩৪৫৬৭৮৯')
ASCII = str.maketrans('০১২৩৪৫৬৭৮৯','0123456789')
PLACES = ['একক','দশক','শতক','হাজার','দশ হাজার','লক্ষ','দশ লক্ষ','কোটি']


def bn(n): return format(n,',').translate(DIGITS)
def esc(s): return html.escape(str(s))
def p(s): return '<p>'+esc(s)+'</p>'
def equation(nums, result): return ' + '.join(bn(n) for n in nums)+' = '+bn(result)


def number_name(n):
    assert 0 <= n < 1000
    if n < 100: result = WORDS[n]
    else: result = WORDS[n//100]+'শত'+(' '+WORDS[n%100] if n%100 else '')
    assert parse_name(result) == n
    return result


def carry_rows(nums):
    assert nums and all(isinstance(n,int) and n >= 0 for n in nums)
    remaining, carry, place, rows = list(nums), 0, 1, []
    while any(remaining) or carry or not rows:
        digits = [n%10 for n in remaining]
        total = sum(digits)+carry
        next_carry, digit = divmod(total,10)
        rows.append({'place':place,'digits':digits,'incoming':carry,'total':total,'digit':digit,'outgoing':next_carry})
        remaining = [n//10 for n in remaining]
        carry, place = next_carry, place*10
    assert sum(row['place']*row['digit'] for row in rows) == sum(nums)
    return rows


def addition_work(nums):
    result, rows = sum(nums), carry_rows(nums)
    out = p(equation(nums,result))
    if max(nums) < 10:
        out += p('দলগুলো একসঙ্গে গুনলে মোট '+bn(result)+'।')
        if result >= 10:
            out += p(bn(result)+' একক = '+bn(result//10)+' দশক ও '+bn(result%10)+' একক। দশটি একক নতুন একটি দশক হয়।')
    out += '<table><caption>একই ঘর মিলিয়ে ডান থেকে বামে যোগ</caption><thead><tr><th scope="col">ঘর</th><th scope="col">এই ঘরের হিসাব</th><th scope="col">যে অঙ্ক লিখি</th><th scope="col">পরের ঘরে হাতে রাখি</th></tr></thead><tbody>'
    for index,row in enumerate(rows):
        pieces = ([row['incoming']] if row['incoming'] else [])+row['digits']
        note = equation(pieces,row['total'])
        if row['incoming']: note += ' (প্রথম সংখ্যাটি আগের ঘর থেকে হাতে রাখা)'
        carried = 'নেই' if not row['outgoing'] else bn(row['outgoing'])+' '+PLACES[index+1]+'; মান '+bn(row['outgoing']*row['place']*10)
        out += '<tr><th scope="row">'+PLACES[index]+'</th><td>'+esc(note)+'</td><td>'+bn(row['digit'])+'</td><td>'+esc(carried)+'</td></tr>'
    out += '</tbody></table>'
    if any(n == 0 for n in nums): out += p('শূন্য যোগ করায় মোট মান বাড়ে না; অন্য সংখ্যাগুলোর মান একই থাকে।')
    return out, rows


def model_work(nums):
    assert all(0 <= n < 100 for n in nums)
    out = p('ব্লক দিয়ে মডেল করি। দশকের প্রতিটি দণ্ডের মান ১০, এককের প্রতিটি টুকরোর মান ১।')
    for index,n in enumerate(nums,1):
        tens,ones=divmod(n,10)
        groups=([bn(tens)+'টি দশকের দণ্ড'] if tens else [])+([bn(ones)+'টি এককের টুকরো'] if ones else [])
        out += p('দল '+bn(index)+': '+' ও '.join(groups)+' নিই; মান '+bn(n)+'।')
    ones=sum(n%10 for n in nums); carried,remaining=divmod(ones,10)
    tens=sum(n//10 for n in nums)+carried
    out += p('এককের টুকরোগুলো একসঙ্গে করলে '+bn(ones)+'টি হয়।')
    if carried:
        out += p('দশটি করে একক বদলে '+bn(carried)+'টি নতুন দশকের দণ্ড নিই; বাকি '+bn(remaining)+'টি একক।')
    else: out += p('দশটি একক হয়নি, তাই নতুন দশকের দল বানাতে হবে না।')
    out += p('সব মিলিয়ে '+bn(tens)+' দশক ও '+bn(remaining)+' একক; মোট '+bn(sum(nums))+'।')
    assert tens*10+remaining==sum(nums)
    return out


def answer_grid(g):
    out = p('বামের সারির সংখ্যার সঙ্গে ওপরের কলামের সংখ্যা যোগ করে ঘরটি পূরণ করি। একই নিয়ম প্রতিটি ঘরে প্রযোজ্য।')
    out += p('যেমন, প্রথম ঘর: '+equation([g['row_labels'][0],g['column_labels'][0]],g['row_labels'][0]+g['column_labels'][0])+'।')
    out += '<div class="table-scroll" tabindex="0" role="region" aria-label="সম্পূর্ণ যোগের ছক"><table><caption>সব ঘরের উত্তর</caption><thead><tr><th scope="col">+</th>'
    out += ''.join('<th scope="col">'+bn(x)+'</th>' for x in g['column_labels'])+'</tr></thead><tbody>'
    cells=[]
    for i in g['row_labels']:
        row=[i+j for j in g['column_labels']]; cells.append(row)
        out += '<tr><th scope="row">'+bn(i)+'</th>'+''.join('<td>'+bn(x)+'</td>' for x in row)+'</tr>'
    return out+'</tbody></table></div>',cells


def worked(case, unit, grids):
    proof={'exercise':case['exercise'],'source_solution_absent':case.get('source_solution_absent',False)}
    if 'model_groups' in case:
        products=[count*value for count,value in case['model_groups']]
        out=''.join(p(bn(count)+' × '+bn(value)+' = '+bn(count*value)) for count,value in case['model_groups'])
        return out+p('সব দলের মোট মান: '+equation(products,sum(products))+'।'),dict(proof,kind='read_blocks',answer=sum(products))
    if 'question_number_name' in case:
        value=parse_name(case['question_number_name'])
        assert value == 342006
        out=p('তিনশত বিয়াল্লিশ হাজার মানে ৩৪২ × ১,০০০ = ৩৪২,০০০। এর সঙ্গে ছয় যোগ করি: ৩৪২,০০০ + ৬ = ৩৪২,০০৬।')
        return out,dict(proof,kind='read_number_name',answer=value)
    if 'image_table_pair' in case:
        g=grids[case['image_table_pair'][0]]
        out,cells=answer_grid(g)
        return out,dict(proof,kind='addition_chart',rows=g['row_labels'],columns=g['column_labels'],cells=cells)
    if 'perimeter_sides' in case:
        out=p('পরিসীমা পেতে সীমানা বরাবর প্রতিটি বাহু একবার করে ধরি এবং দৈর্ঘ্যগুলো যোগ করি।')
        if 'inferred_side' in case:
            outer,inner,length=case['inferred_side']
            assert outer-inner == length
            out += p('ছোট বাঁ উল্লম্ব বাহুর দৈর্ঘ্য ছবিতে লেখা নেই। পুরো উচ্চতা '+bn(outer)+' ইঞ্চি; ভেতরের উল্লম্ব অংশ '+bn(inner)+' ইঞ্চি। তাই বাকি অংশ '+bn(outer)+' − '+bn(inner)+' = '+bn(length)+' ইঞ্চি।')
        calc,rows=addition_work(case['perimeter_sides']); out += calc
        out += p('পরিসীমা '+bn(case['perimeter'])+' '+case['unit_bn']+'। এটি দৈর্ঘ্যের একক; ক্ষেত্রফলের একক নয়।')
        return out,dict(proof,kind='perimeter',answer=case['perimeter'],unit=case['unit_bn'],columns=rows)
    if 'operand_pairs' in case:
        results=case.get('addition_results',[case['addition_result']] if 'addition_result' in case else [])
        if not results:
            out=''
            for pair in case['operand_pairs']:
                names=[number_name(n) for n in pair]
                out += p(' + '.join(bn(n) for n in pair)+' পড়ি: '+' যোগ '.join(names)+'। অর্থ: '+' ও '.join(bn(n) for n in pair)+'-এর যোগফল।')
            out += p('এখানে প্রতীককে কথায় লিখতে বলা হয়েছে; যোগফল গণনা করা এই প্রশ্নের আবশ্যিক অংশ নয়।')
            return out,dict(proof,kind='notation',operand_pairs=case['operand_pairs'])
        out=''; columns=[]
        for index,(nums,result) in enumerate(zip(case['operand_pairs'],results)):
            assert sum(nums) == result
            if len(results)>1: out += p('উপাংশ '+bn(index+1)+'।')
            operands=list(nums)
            if case.get('model_requested'): out += model_work(nums)
            phrase=case.get('word_phrase')
            if phrase in ('the sum of','the total of'):
                out += p('সংখ্যা দুটির যোগফল বা মোট পরিমাণ চাওয়া হয়েছে; তাই সংখ্যা দুটি যোগ করি।')
            elif phrase=='increased by':
                out += p('প্রথম সংখ্যাকে দ্বিতীয় সংখ্যার পরিমাণ বাড়াতে বলা হয়েছে। তাই প্রথম সংখ্যার সঙ্গে দ্বিতীয়টি যোগ করি।')
            elif phrase=='more than':
                operands=list(reversed(nums))
                out += p('প্রথম সংখ্যাটি বলে কত বেশি; দ্বিতীয় সংখ্যাটি মূল সংখ্যা। তাই মূল সংখ্যার সঙ্গে বাড়তি পরিমাণ যোগ করি।')
            elif phrase=='added to':
                operands=list(reversed(nums))
                out += p('প্রথম সংখ্যাটি দ্বিতীয় সংখ্যার সঙ্গে যোগ করতে বলা হয়েছে। মূল সংখ্যাটি আগে লিখে তার সঙ্গে দেওয়া পরিমাণ যোগ করি।')
            calc,rows=addition_work(operands); out += calc; columns.append(rows)
            if unit: out += p('উত্তর: '+bn(result)+' '+unit+'। সংখ্যার সঙ্গে এককও লিখি।')
        if 'comparison' in case:
            boundary=case['comparison']['boundary']; result=results[0]
            if case['comparison']['relation']=='at_least':
                assert result >= boundary
                out += p(bn(result)+' ≥ '+bn(boundary)+'। প্রয়োজনীয় নম্বরের চেয়ে কম নয়; তাই শিক্ষার্থী পাস করেছে।')
            else:
                assert result < boundary
                out += p(bn(result)+' < '+bn(boundary)+'। মোট ওজন সর্বোচ্চ ধারণক্ষমতার নিচে আছে; তাই প্রশ্নের উত্তর হ্যাঁ।')
        return out,dict(proof,kind='addition',answers=results,operand_pairs=case['operand_pairs'],columns=columns,unit=unit,model_requested=case.get('model_requested',False),word_phrase=case.get('word_phrase'))
    if case['exercise']=='fs-id1408863':
        return p('একটি সম্ভাব্য উত্তর: এক অঙ্কের সব যোগফলে এখনো পুরো নিশ্চিত নই। প্রতিদিন কয়েকটি দল বস্তু দিয়ে গুনব, দশের দল বানাব এবং উত্তর মিলিয়ে ভুলের কারণ বলব। যে যোগফলগুলো বুঝি না, সেগুলোতে শিক্ষকের সাহায্য নেব। নিজের অভিজ্ঞতা অনুযায়ী অন্য উত্তরও গ্রহণযোগ্য।'),dict(proof,kind='reflection')
    assert case['exercise']=='fs-id1827602',case
    return p('একটি সম্ভাব্য উত্তর: ৮ + ৪ বোঝাতে বারোটি একক নিয়েছি। দশটি একক একত্রে একটি দশকের দণ্ড হয়েছে, বাকি দুটি একক। তাই ১ দশক ও ২ একক মিলে ১২। মডেলটি হাতে রাখার কারণ বুঝতে সাহায্য করেছে। শিশু নিজের ব্যবহৃত অন্য সঠিক মডেলের কথা বলতে পারে।'),dict(proof,kind='reflection')


def check_html(page, outpath):
    root=ET.fromstring(page.split('\n',1)[1]); ids=[n.get('id') for n in root.iter() if n.get('id')]
    assert len(ids)==len(set(ids))
    assert not list(root.iter('script'))
    assert all(n.get('scope') in ('row','col') for n in root.iter('th'))
    assert not re.search(r'TODO|TBD|\ufffd',page)
    levels=[int(n.tag[1:]) for n in root.iter() if re.fullmatch('h[1-6]',n.tag)]
    assert levels[0]==1 and all(y<=x+1 for x,y in zip(levels,levels[1:]))
    for node in root.iter('p'): assert not any(n.tag in ('p','div','table','ol','ul','section') for n in list(node.iter())[1:])
    links=0
    for node in root.iter('a'):
        href=node.get('href','')
        if href.startswith(('https://','http://')): continue
        path,_,anchor=href.partition('#')
        if path:
            dest=(outpath.parent/path).resolve()
            assert dest.is_file(),href
            if anchor: assert 'id="'+anchor+'"' in dest.read_text(encoding='utf-8'),href
        elif anchor: assert anchor in ids,href
        links += 1
    return links


def check_text_equalities(root):
    count=0
    for node in root.iter():
        if node.tag not in ('p','li','td'): continue
        text=' '.join(node.itertext()).translate(ASCII)
        for left,right in re.findall(r'(?<![\d,])([\d,]+(?:\s*\+\s*[\d,]+)+)\s*=\s*([\d,]+)',text):
            assert sum(int(n.strip().replace(',','')) for n in left.split('+'))==int(right.replace(',','')),(left,right)
            count += 1
    return count


def build():
    source_receipt=b.build('m81244')
    assert source_receipt['status']=='complete_source_translation_structural_math_pass'
    specpath=b.L/'companions/U03A.json'; spec=json.loads(specpath.read_text(encoding='utf-8'))
    module=json.loads((b.L/'modules/m81244.json').read_text(encoding='utf-8'))
    grids=json.loads((b.L/module['image_tables_path']).read_text(encoding='utf-8'))
    for g in grids.values():
        if 'fill' in g: g['cells']=[[i+j if g['fill']=='sum' else None for j in g['column_labels']] for i in g['row_labels']]
    module['_image_tables']=grids
    canon={x['id']:x for x in json.loads((b.L/'canon/download-receipt.json').read_text(encoding='utf-8'))}
    for ref in spec['canon_witnesses']:
        stem=b.L.parent/'downloads/bn-Beng-BD/canon'/ref
        raw=stem.with_suffix('.html').read_bytes(); text=stem.with_suffix('.txt').read_text(encoding='utf-8')
        assert b.sha(raw)==canon[ref]['sha256'] and b.sha(text.encode())==canon[ref]['text_sha256']
        parser=Readable(); parser.feed(raw.decode())
        assert text=='\n'.join(' '.join(s.split()) for s in ''.join(parser.parts).splitlines() if s.strip())
    lessonpath=b.L/spec['lesson']; lesson=ET.parse(lessonpath).getroot()
    lesson_ids={n.get('id') for n in lesson.iter() if n.get('id')}
    answers=[n for n in lesson.iter() if n.get('data-task')]
    assert {n.get('data-task') for n in answers}==set(spec['assessment_ids'])<=lesson_ids
    assert len(answers)==len(spec['assessment_ids'])==14
    for node in lesson.iter():
        if node.get('data-operands'):
            nums=list(map(int,node.get('data-operands').split(','))); result=int(node.get('data-sum'))
            assert sum(nums)==result and str(result) in ''.join(node.itertext()).translate(ASCII).replace(',','')
    equalities=check_text_equalities(lesson)
    assert equalities>=35,equalities
    # Independent validation of the displayed place-column algorithm.
    for a in range(100):
        for z in range(100): assert sum(row['digit']*row['place'] for row in carry_rows([a,z]))==a+z
    full=ET.parse(b.L/source_receipt['translation_path']).getroot()
    exercises={n.get('id'):n for n in full.iter('{'+b.C+'}exercise')}
    cases={c['exercise']:c for c in module['answer_cases']}
    assert set(cases)==set(exercises) and len(cases)==129
    model_section=next(n for n in full.iter() if n.get('id')=='fs-id2145437')
    model_ids={n.get('id') for n in model_section.iter('{'+b.C+'}exercise')}
    model_ids.update(['fs-id2431569','fs-id2210891','fs-id1583137','fs-id1389381','fs-id1932178','fs-id1509761','fs-id2495783','fs-id1209935'])
    word_section=next(n for n in full.iter() if n.get('id')=='fs-id2691382')
    word_ids={n.get('id') for n in word_section.iter('{'+b.C+'}exercise')}
    word_ids.update(['fs-id2387977','fs-id1233172','fs-id1916031','fs-id1834317','fs-id2223707','fs-id1529453','fs-id1760728','fs-id2671623','fs-id1606377','fs-id1614332','fs-id2281219','fs-id1159676'])
    assert len(word_ids)==18
    canonical=ET.parse(b.L.parent/'downloads/bn-Beng-BD/openstax-canonical/modules/m81244/index.cnxml').getroot()
    for ex in canonical.iter('{'+b.C+'}exercise'):
        identifier=ex.get('id'); text=''.join(ex.find('{'+b.C+'}problem').itertext())
        if identifier in model_ids: cases[identifier]['model_requested']=True
        if identifier not in word_ids: continue
        phrases=[phrase for phrase in ('the sum of','the total of','increased by','more than','added to') if phrase in text]
        assert len(phrases)==1 and len(cases[identifier]['operand_pairs'][0])==2
        if phrases:
            cases[identifier]['word_phrase']=phrases[0]
            if phrases[0] in ('more than','added to'):
                sol=ex.find('{'+b.C+'}solution')
                if sol is not None:
                    values=[int(n.text.replace(',','')) for n in sol.iter('{'+b.M+'}mn')]
                    assert values[:2]==list(reversed(cases[identifier]['operand_pairs'][0]))
    renderer=b.Renderer('m81244',module); records=[]
    key='<article id="bd-u03a-source-answers"><h1>যোগ: উৎসের সব কাজের আলাদা ব্যাখ্যাসহ উত্তর</h1>'+p('এটি নতুন করে লেখা উত্তর-সহায়িকা, উৎসের সমাধানের হুবহু অনুবাদ নয়। ১২৯টি উৎস-কাজের সবগুলোর ব্যাখ্যা আছে; উৎসে উত্তরহীন ৪০টি কাজের উত্তরও এখানে যোগ করা হয়েছে। বিশ্বস্ত উৎস-অনুবাদে কোনো নতুন উত্তর ঢোকানো হয়নি।')
    key += p('শিক্ষক উপযুক্ত কাজ বেছে দেবেন। বড় সংখ্যা, ডলার, পাউন্ড, আউন্স ও প্রাপ্তবয়স্ক জীবনের প্রসঙ্গ দ্বিতীয় শ্রেণির আবশ্যিক মূল্যায়ন নয়। উৎসের প্রশ্নের অঙ্ক অপরিবর্তিত; নতুন ব্যাখ্যার অঙ্ক বাংলায়। উৎসের সঙ্গে মিলিয়ে দেখার জন্য বড় সংখ্যায় আন্তর্জাতিক তিন-অঙ্কের কমা রাখা হয়েছে। কোনো মুদ্রা বা একক রূপান্তর হয়নি। প্রশ্নের ক্যালরি/পরিসংখ্যান শুধু উৎসের অনুশীলনের তথ্য।')
    key += '<nav aria-label="উত্তর-সহায়িকার লিংক"><p><a href="index.html">শিশুর সহজ পাঠ</a> · <a href="../m81244/index.html">পূর্ণ উৎস-অনুবাদ</a></p></nav><section><h2>মূল ক্রমে সব উৎস-কাজ</h2>'
    for index,(identifier,ex) in enumerate(exercises.items(),1):
        case=cases[identifier]; problem=ex.find('{'+b.C+'}problem')
        answer,proof=worked(case,spec['answer_units'].get(identifier,''),grids); records.append(proof)
        key += '<section id="bd-u03a-answer-'+identifier+'"><h3>উৎস-কাজ '+bn(index)+'</h3><p><a href="../m81244/index.html#'+identifier+'">'+identifier+'</a> · '+('উৎসে সমাধান নেই; নিচের উত্তর নতুন' if proof['source_solution_absent'] else 'উৎসে সমাধান আছে; নিচে আলাদা বিস্তৃত ব্যাখ্যা')+'</p>'
        key += renderer.render(problem,4)+'<div class="worked-answer"><p><strong>ব্যাখ্যাসহ উত্তর</strong></p>'+answer+'</div></section>'
    key += '</section></article>'
    assert sum(x['source_solution_absent'] for x in records)==40
    keytree=ET.fromstring(key)
    keynodes={n.get('id'):n for n in keytree.iter() if n.get('id')}
    def source_text(node):
        value=node.text or ''
        if b.local(node)=='media': value += 'চিত্রের বর্ণনা: '+node.get('alt','')
        return value+''.join(source_text(n)+(n.tail or '') for n in node)
    def rendered_text(node):
        if node.get('data-editorial')=='true': return ''
        return (node.text or '')+''.join(rendered_text(n)+(n.tail or '') for n in node)
    for ex in exercises.values():
        problem=ex.find('{'+b.C+'}problem')
        rendered=keynodes[problem.get('id')]
        assert re.sub(r'\s+','',source_text(problem))==re.sub(r'\s+','',rendered_text(rendered)),problem.get('id')
    answer_equalities=check_text_equalities(keytree)
    assert answer_equalities>350,answer_equalities
    style=b.STYLE.replace('../assets/','../../assets/').replace('NumeracyBangla.ttf','NumeracyBanglaMath.ttf')+'\n.table-scroll{overflow-x:auto}.table-scroll:focus{outline:3px solid #bc6900}.table-scroll table{min-width:540px}.worked-answer{border-left:3px solid #35877b;padding-left:1rem}td{overflow-wrap:anywhere}'
    footer='<footer><h2>উৎস ও সীমা</h2>'+p('ভিত্তি: OpenStax Prealgebra 2e, m81244; মূল স্বত্ব Rice University। ইন্দোনেশীয় সংস্করণ: KokunoYumeto। বাংলাদেশ বাংলা অনুবাদ ও আলাদা সহায়িকা: Language Allocation, AI-সহায়তায় তৈরি খসড়া। বাংলাদেশি শিক্ষক, নতুন PDF, ব্রাউজার, স্ক্রিনরিডার ও বাস্তব মুদ্রণ-পরীক্ষা বাকি।')+'<p><a href="../../provenance/notices/canonical-LICENSE">CC BY-NC-SA 4.0 ও প্রযোজ্য নোটিশ</a> · <a href="../m81241/index.html">মূল লেখক ও পর্যালোচকদের পরিচয়</a>। OpenStax বা Rice University এই অনুবাদের অনুমোদন দেয়নি।</p></footer>'
    def page(title,body): return '<!DOCTYPE html>\n<html lang="bn-Beng-BD"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><title>'+title+'</title><style>'+style+'</style></head><body><main>'+body+footer+'</main></body></html>\n'
    lessonbody=ET.tostring(lesson,encoding='unicode')+'<nav aria-label="সম্পূর্ণ উত্তর"><p><a href="answers.html">সব উৎস-কাজের আলাদা ব্যাখ্যাসহ উত্তর</a> · <a href="../m81244/index.html">পূর্ণ উৎস-অনুবাদ</a></p></nav>'
    pages={'index.html':page('যোগের সহজ পাঠ',lessonbody),'answers.html':page('যোগ: সব উৎস-কাজের ব্যাখ্যাসহ উত্তর',key)}
    out=b.L/'output/U03A'
    # Both local pages must exist before link closure can be checked.
    for name,body in pages.items(): b.write(out/name,body)
    links=sum(check_html(body,out/name) for name,body in pages.items())
    keypath=b.L/'translations/u03a-worked-answers.xhtml'; b.write(keypath,key+'\n')
    recordpath=b.L/'translations/u03a-answers.json'; b.write(recordpath,json.dumps(records,ensure_ascii=False,indent=2)+'\n')
    receipt={'unit':'U03A','status':'companion_structural_math_pass','entire_assignment_complete':False,'source_module':'m81244','source_translation_sha256':source_receipt['translation_sha256'],'source_spec_sha256':source_receipt['spec_sha256'],'companion_spec_sha256':b.sha(specpath.read_bytes()),'lesson_sha256':b.sha(lessonpath.read_bytes()),'child_tasks':14,'child_addition_equalities_checked':equalities,'source_worked_answer_cases':129,'new_answers_absent_from_source':40,'explicit_block_model_cases':len(model_ids),'word_phrase_cases':sum(bool(r.get('word_phrase')) for r in records),'answer_chart_cells':sum(len(r['rows'])*len(r['columns']) for r in records if r['kind']=='addition_chart'),'independent_small_addition_cases':10000,'local_links_verified':links,'canon_witnesses_verified':spec['canon_witnesses'],'html_sha256':{name:b.sha(body.encode()) for name,body in pages.items()},'answer_records_sha256':b.sha(recordpath.read_bytes()),'answer_xhtml_sha256':b.sha(keypath.read_bytes()),'limits':spec['review_limits']}
    receipt['answer_text_equalities_checked']=answer_equalities
    receipt['all_129_quoted_questions_text_coverage_pass']=True
    b.write(out/'qa-receipt.json',json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    return receipt


if __name__=='__main__':
    first=build(); assert build()==first
    print(json.dumps(first,ensure_ascii=False,indent=2))
