"""Independent source-MathML arithmetic plus source-bound phrase checks."""
import re
from qa_a10_m82454_math import tokens,expression,calc,NS

def run(source,gu):
    ex=source.findall('.//c:exercise',NS);gx=gu.findall('.//c:exercise',NS);checks=[]
    expected={1:[-27,10,-32,42],2:[-48,28,-63,60],3:[-56,54,-28,39],4:[-7,11],5:[-9,17],6:[-8,16],7:[-9,25],8:[-7,39],9:[-9,23],10:[-48],11:[-63],12:[-84],13:[16,-16],14:[81,-81],15:[49,-49],16:[21],17:[29],18:[52],19:[9],20:[4],21:[9],22:[6],23:[21],24:[6],25:[-4,6],26:[-6,10],27:[-1,17],28:[36],29:[196],30:[8],31:[8,32],32:[-2,36],33:[-19,9],34:[52],35:[39],36:[13],55:[-32],57:[-63],59:[-6],61:[14],63:[-4],65:[13],67:[-12],69:[-47],71:[64],73:[-16],75:[90],77:[9],79:[41],81:[-9],83:[-29],85:[5],87:[-47,16],89:[-4,10],91:[-8],93:[-16],95:[121],97:[1,33],99:[-5,25],101:[21],103:[-56]}
    envs={25:[{'n':-5}],26:[{'n':-8}],27:[{'y':-9}],28:[{'x':-18,'y':24}],29:[{'x':-15,'y':29}],30:[{'x':-8,'y':10}],31:[{'z':12},{'z':-12}],32:[{'k':19},{'k':-19}],33:[{'b':14},{'b':-14}],34:[{'x':4}],35:[{'x':-3}],36:[{'x':-2}],87:[{'y':-33},{'y':30}],89:[{'a':-7}],91:[{'m':-15,'n':7}],93:[{'r':-9,'s':-7}],95:[{'x':-3,'y':14}],97:[{'x':8},{'x':-8}],99:[{'m':5},{'m':-5}],101:[{'w':-2}],103:[{'a':-6,'b':-3}]}
    def ev(e):
        sol=e.find('c:solution',NS);assert sol is not None
        return (' '.join(sol.itertext())+' '+' '.join(v for x in sol.iter()for k,v in x.attrib.items()if k in{'alt','aria-label'})).replace('−','-').replace('–','-')
    def bind(n,answers,magnitude=False):
        for name,e in [('source',ex[n-1]),('Gujarati',gx[n-1])]:
            evidence=ev(e).replace('$','').replace(',','');evidence=re.sub(r'negative (\d+)',r'-\1',evidence);evidence=re.sub(r'-\s+(?=\d)','-',evidence)
            for answer in answers:
                value=abs(answer)if magnitude else answer
                assert re.search(r'(?<![\d-])'+re.escape(str(value))+r'(?!\d)',evidence),(n,name,value,'answer binding')
    def question(n):return ex[n-1].find('c:problem',NS)
    for n,answers in expected.items():
        formulas=[]
        for m in question(n).findall('.//m:math',NS):
            ts=tokens(m)
            if 'when'in ts:ts=ts[:ts.index('when')]
            if '='in ts:continue
            if not ts:continue
            formulas.append(expression(ts))
        values=envs.get(n,[{}]);raw=''.join(question(n).itertext()).replace('−','-')
        for env in values:
            for name,value in env.items():assert re.search(name+r'=\s*'+str(value)+r'(?!\d)',raw),(n,name,value,raw)
        if len(formulas)==1 and len(values)>1:forms=[(formulas[0],env)for env in values]
        elif len(values)==1:forms=[(f,values[0])for f in formulas]
        else:assert len(formulas)==len(values);forms=list(zip(formulas,values))
        assert len(forms)==len(answers),(n,forms,answers)
        actual=[calc(f,env)for f,env in forms];assert actual==answers,(n,actual,answers)
        bind(n,answers);checks.append({'ordinal':n,'source_exercise':ex[n-1].get('id'),'type':'source_mathml_arithmetic','expressions':[{'formula':f,'substitutions':v}for f,v in forms],'answers':answers})
    phrases={37:[('8+(-12)+3',-1)],38:[('9+(-16)+4',-3)],39:[('-8+(-12)+7',-13)],40:[('13-(-21)',34),('-19-24',-43)],41:[('14-(-23)',37),('-17-21',-38)],42:[('11-(-19)',30),('-11-18',-29)],43:[('(-2)*14',-28)],44:[('(-5)*12',-60)],45:[('8*(-13)',-104)],46:[('(-56)/(-7)',8)],47:[('(-63)/(-9)',7)],48:[('(-72)/(-9)',8)],105:[('3+(-15)+7',-5)],107:[('10-(-18)',28)],109:[('(-5)-(-30)',25)],111:[('(-3)*15',-45)],113:[('(-60)/(-20)',3)]}
    for n,rows in phrases.items():
        raw=''.join(question(n).itertext()).replace('−','-');answers=[]
        for f,answer in rows:
            for num in re.findall(r'\d+',f):assert num in raw,(n,num,raw)
            assert calc(f)==answer,(n,f,answer);answers.append(answer)
        bind(n,answers);checks.append({'ordinal':n,'source_exercise':ex[n-1].get('id'),'type':'source_phrase_semantics','source_phrase':raw,'expressions':[f for f,a in rows],'answers':answers})
    apps={49:('11-(-9)',20,False),50:('15-(-30)',45,False),51:('(-6)-(-15)',9,False),52:('3*(-15)',-45,True),53:('7*(-15)',-105,True),54:('8*(-2)',-16,True),119:('84-(-12)',96,False),121:('25-6+10-8',21,False),123:('124-152',-28,False),125:('-38+225',187,False),127:('300*(-12)',-3600,False)}
    words={'three':'3','fifteen':'15','seven':'7','eight':'8'}
    for n,(f,answer,magnitude)in apps.items():
        raw=''.join(question(n).itertext()).replace('−','-')
        for a,b in words.items():raw=re.sub(r'\b'+a+r'\b',b,raw)
        for num in re.findall(r'\d+',f):assert num in raw,(n,num,raw)
        assert calc(f)==answer;bind(n,[answer],magnitude)
        checks.append({'ordinal':n,'source_exercise':ex[n-1].get('id'),'type':'application','expression':f,'signed_result':answer,'display_as_loss_magnitude':magnitude})
    for n,answer,points in [(115,'-6/(a+b)',[{'a':1,'b':2},{'a':-3,'b':5},{'a':4,'b':7}]),(117,'-10*(p-q)',[{'p':1,'q':3},{'p':-2,'q':4},{'p':0,'q':-1}])]:
        sol=ex[n-1].find('c:solution',NS);math=sol.find('.//m:math',NS);formula=expression(tokens(math))
        for env in points:assert calc(formula,env)==calc(answer,env)
        # Exact AST expressions retain source numerator/denominator grouping.
        if n==115:assert math.find('.//m:mfrac',NS)is not None
        checks.append({'ordinal':n,'source_exercise':ex[n-1].get('id'),'type':'symbolic_phrase','source_solution_expression':formula,'expected_expression':answer,'exact_test_points':points})
    assert len(checks)==91,(len(checks),[n+1 for n,e in enumerate(ex)if e.find('c:solution',NS)is not None and n+1 not in{c['ordinal']for c in checks}])
    assert -(2**4)!=(-2)**4
    return {'source_solutions':93,'independently_checked_exercises':91,'open_response_source_answers_reviewed':[ex[128].get('id'),ex[130].get('id')],'checks':checks}
