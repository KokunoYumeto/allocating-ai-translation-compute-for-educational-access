"""Independent arithmetic checks against source-bound A10 m82453 answers.

No translations are used as calculators. Problem MathML is parsed into a small
AST evaluator using exact rational arithmetic; stated source answers are then
checked and located within their own source solution (including figure alts).
"""
import ast,re
from fractions import Fraction
NS={'c':'http://cnx.rice.edu/cnxml','m':'http://www.w3.org/1998/Math/MathML'}
def tokens(e):
    tag=e.tag.rsplit('}',1)[-1]
    if tag=='msup':return ['(']+tokens(e[0])+[')','**','(']+tokens(e[1])+[')']
    if tag=='mfrac':return ['(']+tokens(e[0])+[')','/','(']+tokens(e[1])+[')']
    if tag in {'math','mrow'}:return [t for c in e for t in tokens(c)]
    if tag=='mspace':return []
    if tag in {'mn','mi','mo','mtext'}:
        raw=(e.text or '').strip()
        if tag=='mo' or (tag=='mtext' and raw=='/'):return [{'−':'-','·':'*','×':'*','÷':'/','[':'(',']':')','{':'(','}':')'}.get(raw,raw)]
        if not re.fullmatch(r'(?:\d+(?:\.\d+)?|[A-Za-z])',raw):raise ValueError(raw)
        return [raw]
    raise ValueError(tag)
def expression(e):
    ts=tokens(e)
    while ts and ts[-1] in {'.',','}:ts.pop()
    if any(t in {',','=','≠','<','>','≤','≥'} for t in ts):raise ValueError('not an arithmetic expression')
    out=[]
    for t in ts:
        if out and (out[-1]==')' or re.fullmatch(r'[A-Za-z]|\d+(?:\.\d+)?',out[-1])) and (t=='(' or re.fullmatch(r'[A-Za-z]|\d+(?:\.\d+)?',t)):out.append('*')
        out.append(t)
    result=''.join(out);ast.parse(result,mode='eval');return result
def calc(text,env):
    def visit(n):
        if isinstance(n,ast.Expression):return visit(n.body)
        if isinstance(n,ast.Constant) and isinstance(n.value,(int,float)):return Fraction(str(n.value))
        if isinstance(n,ast.Name):return Fraction(env[n.id])
        if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.UAdd,ast.USub)):return visit(n.operand)*(1 if isinstance(n.op,ast.UAdd) else -1)
        if isinstance(n,ast.BinOp):
            a,b=visit(n.left),visit(n.right)
            if isinstance(n.op,ast.Add):return a+b
            if isinstance(n.op,ast.Sub):return a-b
            if isinstance(n.op,ast.Mult):return a*b
            if isinstance(n.op,ast.Div):return a/b
            if isinstance(n.op,ast.Pow):
                assert b.denominator==1 and abs(b)<=20
                return a**int(b)
        raise ValueError(ast.dump(n))
    return visit(ast.parse(text,mode='eval'))
def run(source):
    exercises=source.findall('.//c:exercise',NS)
    # (source ordinal, arithmetic-expression index excluding assignments,
    # substitutions, independently recorded source answer).
    numeric=[
      (7,0,{},81),(8,0,{},125),(8,1,{},1),(9,0,{},49),(9,1,{},0),
      (10,0,{},25),(10,1,{},49),(11,0,{},2),(11,1,{},14),(12,0,{},35),(12,1,{},99),
      (13,0,{},15),(14,0,{},16),(15,0,{},23),(16,0,{},13),(17,0,{},86),(18,0,{},1),
      (19,0,{'x':5},31),(19,0,{'x':1},3),(20,0,{'x':2},13),(20,0,{'x':1},5),(21,0,{'y':3},8),(21,0,{'y':5},16),
      (22,0,{'x':4},16),(22,1,{'x':4},81),(23,0,{'x':3},9),(23,1,{'x':3},64),(24,0,{'x':6},216),(24,1,{'x':6},64),
      (25,0,{'x':4},52),(26,0,{'x':3},40),(27,0,{'x':2},9),
      (28,0,{'y':1},14),(28,1,{'x':1},15),(28,2,{'a':1},1),
      (29,0,{'x':1},17),(29,1,{'b':1},41),(29,2,{'z':1},1),
      (30,0,{'p':1},9),(30,1,{'a':1},13),(30,2,{'y':1},1),
      (75,0,{},125),(77,0,{},256),(79,0,{},43),(79,1,{},55),(81,0,{},5),(83,0,{},34),(85,0,{},58),(87,0,{},6),(89,0,{},4),(91,0,{},35),(93,0,{},58),(95,0,{},149),(97,0,{},50),
      (99,0,{'x':2},22),(101,0,{'x':12},144),(103,0,{'x':2},32),(105,0,{'x':4},21),(107,0,{'x':10,'y':7},9),(109,0,{'a':3,'b':8},73),(111,0,{'l':15,'w':12},54),
      (113,0,{'a':1},8),(115,0,{'r':1},5)]
    result=[]
    def source_problem(n):
        ex=exercises[n-1];problem=ex.find('c:problem',NS);sol=ex.find('c:solution',NS);assert sol is not None
        parsed=[]
        for m in problem.findall('.//m:math',NS):
            try:parsed.append(expression(m))
            except (ValueError,SyntaxError):pass
        if n in {28,29,30}:
            def linear(e):
                if e.tag==f"{{{NS['m']}}}math":return expression(e)
                return (e.text or '')+''.join(linear(c)+(c.tail or '') for c in e)
            pieces=re.split('[ⓐⓑⓒ]',linear(problem))[1:]
            parsed=[re.sub(r'(?<=\d)(?=[A-Za-z])','*',p.strip().rstrip('.')) for p in pieces]
        # Some source coefficients are prose with an italic variable.
        if not parsed:
            text=''.join(problem.itertext()).strip()
            if re.fullmatch(r'\d+[a-z]',text):parsed=[text[:-1]+'*'+text[-1]]
        answer_evidence=' '.join(sol.itertext())+' '+' '.join(e.get('alt','') for e in sol.iter())
        return ex,parsed,answer_evidence
    for n,i,env,expected in numeric:
        ex,parsed,evidence=source_problem(n);assert len(parsed)>i,(n,parsed,i)
        formula=parsed[i]
        assert set(re.findall(r'[A-Za-z]',formula))<=set(env),(n,parsed,env)
        actual=calc(formula,env)
        assert actual==expected,(n,formula,env,actual,expected)
        assert re.search(r'(?<!\d)'+str(expected)+r'(?!\d)',evidence),(n,'answer not bound to source solution',expected)
        result.append({'source_exercise':ex.get('id'),'kind':'numeric_or_monomial_coefficient','problem_expression':formula,'substitutions':env,'answer':expected})
    # These are polynomial identities, checked at five exact integer points;
    # every source polynomial here has degree <=2, so five points exceed the
    # degree bound. The last source solution MathML is independently checked
    # too, except the fully visual worked example37 (reviewed in the figures).
    polynomial={37:'3*x**2+7*x+12',38:'10*x**2+16*x+17',39:'12*y**2+9*y+7',125:'13*x',127:'7*c',129:'10*u+3',131:'22*a+1',133:'17*x**2+20*x+16'}
    for n,answer in polynomial.items():
        ex,parsed,evidence=source_problem(n);formula=parsed[0]
        names=set(re.findall(r'[A-Za-z]',formula+answer))
        for v in range(5):
            env={name:v for name in names};assert calc(formula,env)==calc(answer,env),(n,v)
        sol=ex.find('c:solution',NS);solmath=[]
        for m in sol.findall('.//m:math',NS):
            try:solmath.append(expression(m))
            except (ValueError,SyntaxError):pass
        if n!=37:
            # Some simple answers use italic prose instead of MathML.
            candidate=solmath[-1] if solmath else ''.join(sol.itertext()).strip()
            candidate=re.sub(r'(?<=\d)(?=[a-z])','*',candidate)
            for v in range(5):assert calc(candidate,{name:v for name in names})==calc(answer,{name:v for name in names}),(n,candidate)
        result.append({'source_exercise':ex.get('id'),'kind':'polynomial_identity','problem_expression':formula,'answer':answer,'exact_test_points':[0,1,2,3,4]})
    ex=exercises[150];assert ex.get('id')=='fs-id1170655222137';assert 2100-750==1350
    evidence=''.join(ex.find('c:solution',NS).itertext());assert '750' in evidence and '1,350' in evidence
    result.append({'source_exercise':ex.get('id'),'kind':'deductible_word_problem','claim':2100,'deductible':750,'insurer_payment':1350})
    return {'independent_checks':len(result),'covered_exercises':len({c['source_exercise']for c in result}),'checks':result}
