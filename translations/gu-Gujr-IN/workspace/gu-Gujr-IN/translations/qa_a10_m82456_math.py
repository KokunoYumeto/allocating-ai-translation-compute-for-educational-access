"""Independent exact fraction/polynomial checks using source MathML.
No numerical result is taken from the Gujarati mapping. Source questions are
computed independently, then bound to source and Gujarati displayed answers.
"""
import ast,re
from fractions import Fraction
from qa_a10_m82454_math import tokens as old_tokens,expression,calc,NS

def tokens(e):
    tag=e.tag.rsplit('}',1)[-1]
    if tag=='msup':return ['(']+tokens(e[0])+[')','**','(']+tokens(e[1])+[')']
    if tag=='mfrac':return ['(','(']+tokens(e[0])+[')','/','(']+tokens(e[1])+[')',')']
    if tag in {'math','mrow'}:
        # A whole numeral immediately followed by a simple numeric fraction is
        # the source's mixed-number notation, not implicit multiplication.
        if len(e)==2 and e[0].tag.endswith('mn')and e[1].tag.endswith('mfrac'):
            return ['(']+tokens(e[0])+['+']+tokens(e[1])+[')']
        return [t for x in e for t in tokens(x)]
    return old_tokens(e)

def polyadd(a,b):
    out=a.copy()
    for k,v in b.items():out[k]=out.get(k,Fraction())+v
    return {k:v for k,v in out.items()if v}
def polymul(a,b):
    out={}
    for k,v in a.items():
        for l,w in b.items():
            key=''.join(sorted(k+l));out[key]=out.get(key,Fraction())+v*w
    return {k:v for k,v in out.items()if v}
def negate(a):return {k:-v for k,v in a.items()}
def rational(formula):
    one={'':Fraction(1)}
    def visit(n):
        if isinstance(n,ast.Expression):return visit(n.body)
        if isinstance(n,ast.Constant)and isinstance(n.value,int):return ({'':Fraction(n.value)}if n.value else{},one)
        if isinstance(n,ast.Name):assert len(n.id)==1;return {n.id:Fraction(1)},one
        if isinstance(n,ast.UnaryOp):
            a,b=visit(n.operand);assert isinstance(n.op,(ast.UAdd,ast.USub));return (negate(a)if isinstance(n.op,ast.USub)else a),b
        assert isinstance(n,ast.BinOp)
        a,b=visit(n.left);c,d=visit(n.right)
        if isinstance(n.op,ast.Add):return polyadd(polymul(a,d),polymul(c,b)),polymul(b,d)
        if isinstance(n.op,ast.Sub):return polyadd(polymul(a,d),negate(polymul(c,b))),polymul(b,d)
        if isinstance(n.op,ast.Mult):return polymul(a,c),polymul(b,d)
        if isinstance(n.op,ast.Div):assert c;return polymul(a,d),polymul(b,c)
        if isinstance(n.op,ast.Pow):
            assert d==one and set(c)<= {''};power=c.get('',0);assert power.denominator==1 and 0<=power<=10
            num,den=one,one
            for _ in range(int(power)):num,den=polymul(num,a),polymul(den,b)
            return num,den
        raise ValueError(ast.dump(n))
    return visit(ast.parse(formula,mode='eval'))
def equal(a,b):
    an,ad=rational(a);bn,bd=rational(b)
    return not polyadd(polymul(an,bd),negate(polymul(bn,ad)))
def formula(m):return expression(tokens(m))

def run(source,gu):
    ex=source.findall('.//c:exercise',NS);gx=gu.findall('.//c:exercise',NS);checks=[]
    # Zero-based source ordinals; answers independently transcribed/reviewed.
    numeric={3:'-4/7',4:'-7/9',5:'-5/9',6:'-6/11',7:'-23/40',8:'-5/8',12:'-55/84',13:'-4/21',14:'-3/16',21:'3/4',22:'4/15',23:'2/3',24:'6/5',25:'4/5',26:'11/14',30:'-1/3',31:'-3/4',32:'-5/3',33:'3',34:'4',35:'2',43:'-5/11',45:'-12/7',47:'10/21',53:'27/40',55:'1/4',57:'-1/6',59:'-21/50',61:'11/30',63:'20/11',67:'-34',69:'9/8',71:'4/9',75:'-4/9',79:'-10',81:'-1/16',83:'-10/9',85:'-2/5',89:'5/2',91:'16/3',93:'0',95:'1/3',97:'3/5',99:'42/17',101:'9/7',103:'-8',105:'11/6',107:'5/2'}
    symbolic={9:'x/y',10:'x/y',11:'a/b',15:'48*x',16:'-33*a',17:'-26*b',18:'-10/(3*n)',19:'-21/(5*p)',20:'-15/(8*q)',27:'3/y',28:'3/(4*b)',29:'4/q',49:'-x/(4*y)',51:'2*x**2/(3*y)',65:'9*n',73:'33/(4*x)',77:'10*u/(9*v)',87:'2*m/(3*n)'}
    for n,answer in (numeric|symbolic).items():
        question=ex[n].find('c:problem',NS);math=question.findall('.//m:math',NS);assert len(math)==1,(n,len(math));f=formula(math[0]);assert equal(f,answer),(n,f,answer)
        if n in numeric:assert calc(f)==calc(answer)
        if n==6:
            # The final answer is image-only in the authority source. Its actual
            # original008c was viewed, independently giving minus6/11.
            sol=ex[n].find('c:solution',NS);assert any(x.get('src','').endswith('008c_new.jpg')for x in sol.iter())
            assert 'negative six elevenths' in ' '.join(x.get('alt','')for x in sol.iter())
            assert '-6/11' in ' '.join(x.get('alt','')for x in gx[n].iter()).replace('−','-')
            binding='actual unchanged008c figure plus source/Gu alternatives'
        else:
            for label,e in [('source',ex[n]),('Gujarati',gx[n])]:
                mats=e.find('c:solution',NS).findall('.//m:math',NS)
                if mats:result=formula(mats[-1]);assert equal(result,answer),(n,label,result,answer)
                else:
                    result=''.join(e.find('c:solution',NS).itertext()).strip().replace('−','-');assert re.fullmatch(r'-?\d+[a-z]?',result),(n,label,result);result=re.sub(r'(\d)([a-z])',r'\1*\2',result);assert equal(result,answer),(n,label,result,answer)
            binding='source and Gujarati final MathML expressions'
        checks.append({'ordinal':n+1,'source_exercise':ex[n].get('id'),'type':'exact_rational_polynomial_identity'if n in symbolic else'exact_fraction_arithmetic','question':f,'answer':answer,'binding':binding})
    equivalences={0:['4/10','6/15','10/25'],1:['6/10','9/15','12/20'],2:['8/10','12/15','16/20'],39:['6/16','9/24','12/32'],41:['10/18','15/27','20/36']}
    for n,answers in equivalences.items():
        f=formula(ex[n].find('c:problem',NS).find('.//m:math',NS));assert len(set(answers))==3
        for a in answers:assert calc(f)==calc(a)
        for e in [ex[n],gx[n]]:
            fractions=[formula(m)for m in e.find('c:solution',NS).findall('.//m:mfrac',NS)]
            for a in answers:assert any(x.replace('(','').replace(')','')==a for x in fractions),(n,a,fractions)
        checks.append({'ordinal':n+1,'source_exercise':ex[n].get('id'),'type':'three_equivalent_fractions','question':f,'answers':answers})
    phrases={36:'(m-n)/p',37:'(a-b)/(c*d)',38:'(p+q)/r',109:'r/(s+10)',111:'(x-y)/(-3)'}
    for n,answer in phrases.items():
        for e in [ex[n],gx[n]]:
            math=e.find('c:solution',NS).findall('.//m:math',NS)[-1];assert equal(formula(math),answer),(n,formula(math),answer)
        checks.append({'ordinal':n+1,'source_exercise':ex[n].get('id'),'type':'source_phrase_scope_exact_algebra','answer':answer})
    # Applications: source proportions/units read separately from result strings.
    n=113;q=ex[n].find('c:problem',NS);assert formula(q.find('.//m:math',NS)).replace('(','').replace(')','')=='3/4';assert 'double'in ''.join(q.itertext());answer=calc('2*(3/4)');assert answer==Fraction(3,2)
    for e in [ex[n],gx[n]]:assert any(equal(formula(m),'3/2')for m in e.find('c:solution',NS).findall('.//m:mfrac',NS))
    checks.append({'ordinal':n+1,'source_exercise':ex[n].get('id'),'type':'recipe_proportion','formula':'2*(3/4)','answer':'3/2 cups','part_b':'open diagram answer reviewed; valid alternatives include1+1/2or three1/2cups'})
    n=115;q=ex[n].find('c:problem',NS);fs=[formula(m)for m in q.findall('.//m:math',NS)];assert len(fs)==2 and calc(fs[0])==5 and calc(fs[1])==Fraction(1,4);assert calc('('+fs[0]+')/('+fs[1]+')')==20
    for e in [ex[n],gx[n]]:assert re.search(r'\b20\b',''.join(e.find('c:solution',NS).itertext()))
    checks.append({'ordinal':n+1,'source_exercise':ex[n].get('id'),'type':'equal_portions','formula':'5/(1/4)','answer':'20 bags'})
    supplied={i+1 for i,e in enumerate(ex)if e.find('c:solution',NS)is not None};covered={x['ordinal']for x in checks};assert supplied-covered=={118,120},(len(checks),supplied-covered)
    assert len(checks)==78 and len(covered)==78
    assert Fraction(3,6)==Fraction(4,8)==Fraction(1,2)
    return {'source_solutions':80,'independently_checked_exercises':78,'open_response_source_answers_reviewed':[ex[117].get('id'),ex[119].get('id')],'checks':checks,'symbolic_method':'exact cross-multiplied polynomial coefficient comparison; domain restrictions retained or explicitly noted in errata'}
