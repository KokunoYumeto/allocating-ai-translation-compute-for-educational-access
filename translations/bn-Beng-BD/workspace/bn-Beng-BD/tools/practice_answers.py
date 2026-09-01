"""Render and independently verify the separately authored full practice key.

The editable cases are translator inputs. No source solution is inserted/replaced.
"""
from fractions import Fraction
from pathlib import Path
import html, json, re
import xml.etree.ElementTree as ET
from build import C, M, L, local, write
from number_names import parse_name

PLACES=['একক','দশক','শতক','হাজার','দশ হাজার','একশত হাজার','মিলিয়ন','দশ মিলিয়ন','একশত মিলিয়ন','বিলিয়ন','দশ বিলিয়ন','একশত বিলিয়ন','ট্রিলিয়ন','দশ ট্রিলিয়ন','একশত ট্রিলিয়ন']
SCALES={0:'এককের দল',3:'হাজারের দল',6:'মিলিয়নের দল',9:'বিলিয়নের দল',12:'ট্রিলিয়নের দল'}
bn=lambda s:str(s).translate(str.maketrans('0123456789','০১২৩৪৫৬৭৮৯'))
esc=html.escape
def numeric_values(e):
    if local(e)=='mfrac':
        return [numeric_values(e[0])[0]/numeric_values(e[1])[0]]
    if local(e) in ('mn','mtext'):
        value=(e.text or '').replace(',','').replace('$','').strip()
        return [Fraction(value)] if re.fullmatch(r'\d+(?:\.\d+)?',value) else []
    return [x for child in e for x in numeric_values(child)]
def printed_integers(e):
    return [int(x.replace(',','')) for x in re.findall(r'\d+(?:,\d+)*',''.join(e.itertext()))]
def read():return json.loads((L/'translations/u02e-answers.json').read_text(encoding='utf-8'))['cases']
def groups(n):
    top=((len(str(n))-1)//3)*3
    return [(power,(n//10**power)%1000) for power in range(top,-1,-3)]
def body(case):
    kind=case['kind'];unit=' '+case['unit'] if case.get('unit') else ''
    if kind=='classify':
        inputs='; '.join(bn(x) for x in case['inputs'])
        selected=lambda k:', '.join(bn(x) for x in case[k])
        excluded='; '.join(bn(x) for x in case['inputs'] if Fraction(x).denominator!=1)
        return f'<p>দেওয়া সংখ্যা: {inputs}। a: স্বাভাবিক সংখ্যা {selected("counting")}। b: শূন্যসহ স্বাভাবিক সংখ্যা {selected("whole")}।</p><p>স্বাভাবিক সংখ্যা গণনায় ১ থেকে শুরু হয়। শূন্যসহ সমষ্টিতে ০-ও থাকে। এখানে {excluded} সম্পূর্ণ গণনাসংখ্যা নয়, তাই কোনো তালিকাতেই নেই।</p>'
    if kind=='blocks':
        h,t,o=case['groups'];n=case['answer']
        return f'<p>ছবিতে {bn(h)}টি শতকের বর্গ, {bn(t)}টি দশকের দণ্ড এবং {bn(o)}টি আলাদা একক। তাই {bn(h)} × ১০০ + {bn(t)} × ১০ + {bn(o)} = {bn(n)}। কোনো দলে কিছু না থাকলে সেই ঘরে ০ লিখি; ঘরটি বাদ দিই না।</p>'
    if kind=='places':
        result=f'<p>সংখ্যা {bn(format(case["number"],","))}। স্থান হলো ঘরের নাম; স্থানীয় মান হলো অঙ্কটির সংখ্যাগত অবদান। নিচের ক্রম উৎসের a–e-এর ক্রম।</p><table><caption>প্রতিটি অঙ্কের স্থান ও স্থানীয় মান</caption><thead><tr><th scope="col">অঙ্ক</th><th scope="col">স্থান</th><th scope="col">স্থানীয় মান</th></tr></thead><tbody>'
        for d,p in zip(case['digits'],case['powers']):
            result+=f'<tr><td>{bn(d)}</td><td>{PLACES[p]}</td><td>{bn(d)} × {bn(10**p)} = {bn(d*10**p)}</td></tr>'
        return result+'</tbody></table>'
    if kind in ('name','write'):
        n=case['number'];g=groups(n)
        details='; '.join(f'{SCALES[p]} {bn(v):s}' for p,v in g)
        parts=[v*10**p for p,v in g if v]
        equation=' + '.join(bn(v) for v in parts)+' = '+bn(n)
        if len(parts)==1:
            if n<1000:
                equation=' + '.join(f'{bn(n//10**p%10)} × {bn(10**p)}' for p in range(len(str(n))-1,-1,-1))+' = '+bn(n)
            else:
                power,value=next((p,v) for p,v in g if v)
                equation=f'{bn(value)} × {bn(10**power)} = {bn(n)}'
        action='কথায়' if kind=='name' else 'অঙ্কে'
        answer=case['name'] if kind=='name' else bn(format(n,','))
        return f'<p>{action}: {esc(answer+unit)}। উৎসের তিন-অঙ্কের দল: {details}।</p><p>{equation}। {"প্রতি দলের সংখ্যা পড়ে তার দলের নাম বলি; এককের দলের নাম বলি না।" if kind=="name" else "মাঝের ও শেষের প্রতিটি দল তিন ঘরে লিখি; প্রয়োজনমতো শুরুর শূন্য রাখি। একেবারে বাঁয়ের দলে অপ্রয়োজনীয় শুরুর শূন্য লিখি না।"}</p>'
    if kind=='round':
        result=''
        for i,(n,s,a) in enumerate(zip(case['numbers'],case['steps'],case['answers'])):
            power=len(str(s))-1;digit=(n//(s//10))%10;lo=(n//s)*s;hi=lo+s
            decision='নিচের গুণিতকটি নিই' if digit<5 else 'ওপরের গুণিতকটি নিই'
            result+=f'<p data-round-number="{n}" data-round-step="{s}" data-round-result="{a}">{chr(97+i)}। {bn(format(n,","))}{unit}: {PLACES[power]} স্থানে আসন্ন মান {bn(format(a,","))}{unit}। ঠিক ডানের অঙ্ক {bn(digit)}, তাই {decision}। দুই পাশের গুণিতক {bn(format(lo,","))} ও {bn(format(hi,","))}; দূরত্ব যথাক্রমে {bn(n-lo)} ও {bn(hi-n)}। দূরত্ব সমান হলে এই পাঠে বড় মানটি নিই।</p>'
        return result
    if kind=='explain':return '<p>'+esc(case['answer'])+'</p>'
    raise ValueError(kind)

INTRO='''<article id="bd-u02e-companion"><h1>মূল ধারণা ও অনুশীলন: সম্পূর্ণ উত্তর-সহায়িকা</h1>
<p>এই সহায়িকা উৎসের সব ৫৮টি অনুশীলনের আলাদা করে লেখা পূর্ণ উত্তর। উৎসে ২৯টির সমাধান আছে; মূল অনুবাদে সেগুলোই রাখা হয়েছে। অন্যগুলোর উত্তর এখানে নতুন করে যোগ করা হয়েছে, মূল লেখকের উত্তর বলে চালানো হয়নি।</p>
<p>এটি শিশুদের জন্য একসঙ্গে করানোর প্রশ্নপত্র নয়। <a href="../u01-number-sense.html">সংখ্যার শুরু</a>, <a href="../U02A/index.html">স্থানীয় মান</a>, <a href="../U02B/index.html">কথায় লেখা</a>, <a href="../U02C/index.html">অঙ্কে লেখা</a> ও <a href="../U02D/index.html">আসন্ন মান</a> শেখার পরে শিক্ষক প্রয়োজনমতো কাজ বাছতে পারেন। ভগ্নাংশ, দশমিক ও বড় আন্তর্জাতিক সংখ্যাগুলো ছোট শিশুদের জন্য বাধ্যতামূলক প্রবেশ-শর্ত নয়।</p>
<aside><p>এই সহায়িকায় বাংলা অঙ্কে উৎসের আন্তর্জাতিক তিন-অঙ্কের কমার দল রাখা হয়েছে, যাতে উৎসের সঙ্গে সরাসরি মেলানো যায়; এটি দেশীয় লক্ষ-কোটির কমার নিয়ম নয়। ফুট, গ্যালন, ডলার ইত্যাদি একক বদলানো হয়নি। উৎসের জনসংখ্যা, পূর্বাভাস, “পাঁচ বছর পর” ও “বারো বছর আগে” উৎসের পুরোনো প্রেক্ষাপটের কথা; আজকের তথ্য নয়।</p>
<p>বছর থেকে সময়ের দুটি উদাহরণে প্রতি বছর ৩৬৫ দিন ধরা হয়েছে: ৭০ × ৩৬৫ × ২৪ = ৬১৩২০০ ঘণ্টা এবং ৩৬৫ × ২৪ × ৬০ = ৫২৫৬০০ মিনিট। অধিবর্ষ ধরলে ফল আলাদা হবে।</p></aside>
<section id="bd-u02e-answers"><h2>প্রতিটি উৎস-অনুশীলনের উত্তর</h2>'''
END='''</section><section id="bd-u02e-self-check"><h2>কোথায় সাহায্য লাগবে?</h2>
<p>প্রতি সারিতে নিজের অবস্থা চিহ্নিত করো। “এখনও শিখছি” মানে সাহায্য নিয়ে আবার চেষ্টা করার জায়গা; এটি লজ্জা বা নম্বর দেওয়ার ছক নয়।</p>
<table><caption>নিজের শেখা নিয়ে কথা বলি</caption><thead><tr><th scope="col">আমি যে কাজটি করি</th><th scope="col">নিজে পারি</th><th scope="col">কিছু সাহায্যে পারি</th><th scope="col">এখনও শিখছি</th></tr></thead><tbody>
<tr><th scope="row">স্বাভাবিক ও শূন্যসহ স্বাভাবিক সংখ্যা চিনি</th><td>□</td><td>□</td><td>□</td></tr>
<tr><th scope="row">দলের মডেল থেকে সংখ্যা বলি</th><td>□</td><td>□</td><td>□</td></tr>
<tr><th scope="row">অঙ্কের স্থান ও স্থানীয় মান বলি</th><td>□</td><td>□</td><td>□</td></tr>
<tr><th scope="row">সংখ্যা কথায় লিখি</th><td>□</td><td>□</td><td>□</td></tr>
<tr><th scope="row">কথা থেকে অঙ্কে লিখি</th><td>□</td><td>□</td><td>□</td></tr>
<tr><th scope="row">নির্দিষ্ট স্থানে আসন্ন মান নির্ণয় করি</th><td>□</td><td>□</td><td>□</td></tr>
</tbody></table><p>একটি কঠিন কাজ বেছে শিক্ষক বা সহপাঠীকে দেখাও। কোন ধাপে আটকে গেছ বলো, সেই ধাপটি একসঙ্গে করো, তারপর একই ধরনের আরেকটি কাজ নিজে চেষ্টা করো। নিজে পারলে কোন কৌশল কাজে লেগেছে সেটিও বলো।</p></section></article>'''
def generate():
    chunks=[INTRO]
    for index,case in enumerate(read(),1):
        chunks.append(f'<section id="bd-u02e-answer-{case["id"]}" data-practice-exercise="{case["id"]}"><h3>{bn(index)}। <a href="#{case["id"]}">{case["id"]}</a></h3>'+body(case)+'</section>')
    output='\n'.join(chunks)+END+'\n'
    ET.fromstring(output)
    write(L/'translations/u02e-companion.xhtml',output)
    return output

def verify(original,translated,companion):
    cases=read();source={e.get('id'):e for e in original.iter('{'+C+'}exercise')};target={e.get('id'):e for e in translated.iter('{'+C+'}exercise')}
    assert len(cases)==len({c['id'] for c in cases})==len(source)
    checked=set();counts={};source_solutions=0
    step_words={'ten':10,'hundred':100,'thousand':1000,'ten-thousand':10000,'billion':10**9,'hundred-million':10**8,'ten-million':10**7,'million':10**6}
    for c in cases:
        key=c['id'];kind=c['kind'];old=source[key];new=target[key]
        problem=new.find('{'+C+'}problem');solution=new.find('{'+C+'}solution')
        numeric=numeric_values(problem)
        section=next(e for e in companion.iter('section') if e.get('data-practice-exercise')==key)
        assert len(''.join(section.itertext()))>80
        # Generated answer text must remain exactly the translator's case/templates.
        expected=ET.fromstring('<section>'+body(c)+'</section>')
        assert ''.join(section.itertext()).endswith(''.join(expected.itertext()))
        if kind=='classify':
            inputs=list(map(Fraction,c['inputs']));assert inputs==numeric
            assert c['counting']==[int(n) for n in inputs if n.denominator==1 and n>0]
            assert c['whole']==[int(n) for n in inputs if n.denominator==1 and n>=0]
            if solution is not None:
                lists=solution.find('{'+C+'}list');assert len(lists)==2
                assert printed_integers(lists[0])==c['counting'] and printed_integers(lists[1])==c['whole']
        elif kind=='blocks':
            assert sum(g*s for g,s in zip(c['groups'],(100,10,1)))==c['answer']
            assert Path(next(old.iter('{'+C+'}image')).get('src')).name==c['figure']
            if solution is not None:assert printed_integers(solution)==[c['answer']]
        elif kind=='places':
            assert numeric==[c['number']]
            source_digits=[printed_integers(e)[0] for e in problem.find('{'+C+'}list')]
            assert source_digits==c['digits']
            for d,p in zip(c['digits'],c['powers']):assert c['number']//10**p%10==d
            if solution is not None:
                labels=[''.join(e.itertext())[1:].strip() for e in solution.find('{'+C+'}list')]
                assert labels==[PLACES[p] for p in c['powers']],labels
        elif kind in ('name','write'):
            assert parse_name(c['name'])==c['number'],c
            assert sum(v*10**p for p,v in groups(c['number']))==c['number']
            if kind=='name':
                assert c['number'] in numeric
                if solution is not None:assert c['name'] in ''.join(solution.itertext())
            else:
                assert c['name'] in ''.join(problem.itertext())
                if solution is not None:assert printed_integers(solution)==[c['number']]
        elif kind=='round':
            assert set(c['numbers'])<=set(numeric)
            old_problem=old.find('{'+C+'}problem');old_text=''.join(old_problem.itertext())
            nearest=re.search(r'Round to the nearest (ten|hundred|thousand):',old_text)
            if nearest:assert c['steps']==[step_words[nearest[1]]]*len(c['numbers'])
            else:
                labels=[''.join(e.itertext())[1:].strip().split()[0] for e in old_problem.find('{'+C+'}list')]
                assert c['steps']==[step_words[x] for x in labels]
            for n,s,a in zip(c['numbers'],c['steps'],c['answers']):
                lo=n//s*s;hi=lo+s
                assert a==min((lo,hi),key=lambda v:(abs(v-n),-v))
            if solution is not None:assert printed_integers(solution)==c['answers']
        elif kind=='explain':
            assert all(word in c['answer'] for word in c['required'])
            if c.get('round_example'):
                n,s,a=c['round_example'];assert ((n+s//2)//s)*s==a
        else:raise ValueError(kind)
        checked.add(key);counts[kind]=counts.get(kind,0)+1;source_solutions+=solution is not None
    assert checked==set(source)
    return checked,{'all_practice_exercises_with_separate_worked_answers':len(checked),'source_solutions_retained':source_solutions,'new_answers_for_source_without_solution':len(checked)-source_solutions,'case_types':counts,'answer_inputs':'translations/u02e-answers.json'}

if __name__=='__main__':
    print(json.dumps({'generated_characters':len(generate()),'cases':len(read())}))
