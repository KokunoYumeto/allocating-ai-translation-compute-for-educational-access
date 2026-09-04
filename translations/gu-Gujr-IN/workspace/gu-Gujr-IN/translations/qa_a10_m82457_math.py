"""Exact independent checks of every determinate supplied m82457 answer.
Two confirmed source mathematical errors remain unchanged in faithful XML and
are bound to explicit source-ID keyed errata with recomputed correction values.
"""
import re,json
from pathlib import Path
from fractions import Fraction
from qa_a10_m82456_math import equal,calc,expression,NS
from qa_a10_m82454_math import tokens as leaf_tokens

def tokens(e):
    tag=e.tag.rsplit('}',1)[-1]
    if tag=='msup':return ['(']+tokens(e[0])+[')','**','(']+tokens(e[1])+[')']
    if tag=='mfrac':return ['(','(']+tokens(e[0])+[')','/','(']+tokens(e[1])+[')',')']
    if tag in {'math','mrow','mtd','menclose'}:
        if len(e)==2 and e[0].tag.endswith('mn')and e[1].tag.endswith('mfrac'):return ['(']+tokens(e[0])+['+']+tokens(e[1])+[')']
        return[t for x in e for t in tokens(x)]
    if tag=='mn'and(e.text or '').strip()in{'−','-'}:return ['-']
    return leaf_tokens(e)
def formula(e):return expression(tokens(e))
def sub(f,env):
    for name,value in env.items():f=re.sub(r'\b'+name+r'\b','('+str(value)+')',f)
    return f

def run(source,gu):
    ex=source.findall('.//c:exercise',NS);gx=gu.findall('.//c:exercise',NS);checks=[]
    envs={30:[{'x':'-1/3'},{'x':'-3/4'}],31:[{'x':'-7/4'},{'x':'-5/4'}],32:[{'y':'2/3'},{'y':'-3/4'}],33:[{'y':'-2/3'}],34:[{'y':'-1/4'}],35:[{'y':'-5/2'}],36:[{'x':'1/4','y':'-2/3'}],37:[{'a':'-2/3','b':'-1/2'}],38:[{'c':'-1/2','d':'-4/3'}],39:[{'p':'-4','q':'-2','r':'8'}],40:[{'a':'-8','b':'-7','c':'6'}],41:[{'x':'9','y':'-18','z':'-6'}],134:[{'x':'1/3'},{'x':'-1/6'}],136:[{'x':'3/5'},{'x':'-3/5'}],138:[{'w':'1/2'},{'w':'-1/2'}],140:[{'x':'-2/3','y':'-1/2'}],142:[{'a':'-3','b':'8'}]}
    def assignments(q):
        found=[]
        for m in q.findall('.//m:math',NS):
            ts=tokens(m)
            if '='not in ts:continue
            while ts and ts[-1]in{'.',','}:ts.pop()
            start=0
            for j,t in enumerate(ts+['END']):
                if t in{',','and','END'}:
                    ch=ts[start:j];start=j+1
                    if ch:assert ch[1]=='=';found.append((ch[0],calc(expression(ch[2:]))))
        return found
    def final_answer(sol):
        maths=[]
        for m in sol.findall('.//m:math',NS):
            try:
                ts=tokens(m)
                if ts and '='not in ts:maths.append(formula(m))
            except ValueError:continue
        if maths:return maths[-1]
        raw=''.join(sol.itertext()).strip().replace('−','-');assert re.fullmatch(r'-?\d+',raw),raw;return raw
    def answers(n,count,e):
        sol=e.find('c:solution',NS)
        def image_binding(filename,marker):
            media=next(x for x in sol.findall('.//c:media',NS)if any(z.get('src','').endswith(filename)for z in x.iter()))
            assert marker in re.sub(r'\s+','',media.get('alt','')),(n,filename,marker,media.get('alt'))
        if n==12:
            image_binding('001b_new.jpg','31/36');return ['31/36']
        if n==18:
            image_binding('004e_img_new.jpg','(24+5x)/40');return ['(24+5*x)/40']
        if n==24:
            image_binding('010c_new.jpg','1/52');return ['1/52']
        if n==21:
            tables=sol.findall('.//m:mtable',NS);assert len(tables)==2
            return[formula(t.findall('m:mtr/m:mtd',NS)[-1])for t in tables]
        if n==30:
            items=sol.findall('c:list/c:item',NS);assert len(items)==2
            # First result is plain0in the final table cell; second is MathML.
            rows=items[0].findall('.//c:table/c:tgroup/c:tbody/c:row',NS);raw=''.join(list(rows[-1])[-1].itertext()).strip();assert raw=='0'
            return [raw,final_answer(items[1])]
        if n==98:
            maths=sol.findall('.//m:math',NS);assert len(maths)==1
            spans=sol.findall('.//c:span',NS);assert len(spans)==2;second=spans[-1].tail.strip();assert second=='4'
            return [formula(maths[0]),second]
        if count==1:return [final_answer(sol)]
        maths=sol.findall('.//m:math',NS);assert len(maths)==count,(n,count,len(maths));return[formula(m)for m in maths]
    errors={10:('-1','-13/9'),35:('-17/8','17/8')}
    errata=json.loads(Path(__file__).with_name('a10-m82457-errata.gu.json').read_text(encoding='utf8'))['entries']
    for n,e in enumerate(ex):
        sol=e.find('c:solution',NS)
        if sol is None or n==146:continue
        q=e.find('c:problem',NS)
        if n==144:
            mats=q.findall('.//m:math',NS);assert len(mats)==2;fs=[formula(m)for m in mats];assert calc(fs[0])==Fraction(1,2)and calc(fs[1])==Fraction(3,8);forms=['('+fs[0]+')+('+fs[1]+')'];env=[{}]
        else:
            forms=[formula(m)for m in q.findall('.//m:math',NS)if '='not in tokens(m)];env=envs.get(n,[{}])
        if n in envs:
            observed=assignments(q);wanted=[(k,calc(v))for en in env for k,v in en.items()];assert observed==wanted,(n,observed,wanted)
        pairs=[(f,en)for en in env for f in forms];computed=[sub(f,en)for f,en in pairs]
        source_answers=answers(n,len(computed),e);gu_answers=answers(n,len(computed),gx[n]);assert len(source_answers)==len(computed)
        for j,(f,a,b)in enumerate(zip(computed,source_answers,gu_answers)):
            assert equal(a,b),(n,'source/Gu answer drift',a,b)
            if n in errors:
                old,new=errors[n];assert equal(a,old)and equal(f,new)and not equal(f,a),(n,f,a,old,new)
                assert ex[n].get('id')in errata and errata[ex[n].get('id')]['correct_answer']==new
            else:assert equal(f,a),(n,ex[n].get('id'),f,a)
            if not re.search('[a-z]',f):calc(f) # exact numeric evaluator independent of coefficient identity
        checks.append({'ordinal':n+1,'source_exercise':e.get('id'),'type':'source_mathematical_erratum'if n in errors else'exact_fraction_or_polynomial_identity','source_questions':forms,'substitutions':env,'displayed_source_and_Gujarati_answers':source_answers,'correct_answers':[errors[n][1]]if n in errors else source_answers,'answer_binding':'individually viewed original figure and filename/alt'if n in {12,18,24}else'final source/Gu MathML or explicitly located plain result'})
    assert len(checks)==94 and len({x['source_exercise']for x in checks})==94,len(checks)
    assert Fraction(1,2)+Fraction(3,8)==Fraction(7,8)
    return {'source_solutions':95,'independently_checked_exercises':94,'correct_source_answer_exercises':92,'source_mathematical_error_exercises':[ex[i].get('id')for i in errors],'open_response_source_answers_reviewed':[ex[146].get('id')],'checks':checks}
