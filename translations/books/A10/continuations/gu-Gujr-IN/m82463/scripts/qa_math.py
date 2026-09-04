"""Bind exact arithmetic to actual source questions and displayed answer nodes."""
from pathlib import Path
from lxml import etree as E
import hashlib,json,re
import sympy as S
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, rationalize
from content import SOLVES,CHECKS,OPEN,ADAPT
R=Path(__file__).resolve().parents[1]; C='{http://cnx.rice.edu/cnxml}'; M='{http://www.w3.org/1998/Math/MathML}'
src=E.parse(str(R/'source/en.cnxml')); gu=E.parse(str(R/'source/m82463.gu.cnxml'))
se=list(src.iter(C+'exercise')); ge=list(gu.iter(C+'exercise'))
TRANS=standard_transformations+(implicit_multiplication_application,rationalize)
def parse(s):
 s=s.replace('−','-').replace(',','').replace('✓','').replace('?','').strip().rstrip('.')
 assert re.fullmatch(r'[A-Za-z0-9\s+\-*/().]*',s),s
 return parse_expr(s,transformations=TRANS,local_dict={x:S.Symbol(x) for x in 'abcdefghijklmnopqrstuvwxyz'},evaluate=True)
def raw(e):
 tag=E.QName(e).localname
 if tag=='mfrac': return '(('+raw(e[0])+')/('+raw(e[1])+'))'
 if tag=='mtext': return '-' if (e.text or '').strip()=='−' else ''
 if tag in ['mi','mn','mo']: return e.text or ''
 return ' '.join(raw(c) for c in e)
def formulas(e): return [raw(m).strip().rstrip('.') for m in e.iter(M+'math')]
def sides(s):
 a,b=s.split('='); return parse(a),parse(b)
def residual(s):
 a,b=sides(s); return S.expand(a-b)
def solution(s):
 r=residual(s); sy=sorted(r.free_symbols,key=str); assert len(sy)==1,(s,sy)
 vals=S.solve(r,sy[0]); assert len(vals)==1,(s,vals)
 return sy[0],vals[0]
def sha(e): return hashlib.sha256(E.tostring(e,method='c14n')).hexdigest()
def same_sides(a,b):
 x,y=sides(a); u,v=sides(b); return S.simplify(x-u)==0 and S.simplify(y-v)==0
def displayed_value(sol,var=None):
    """Actual final symbolic/number answer, not presence of expected number tokens."""
    candidates=[]
    for f in formulas(sol):
        try:
            pieces=[piece.strip() for piece in f.split(';')]
            for trailing in pieces[1:]:
                if trailing:
                    value=parse(trailing)
                    if not value.free_symbols:
                        candidates.append(value)
            equation=pieces[0]
            if '=' in equation:
                # Supplied solutions frequently use equivalent chains such as
                # ``p = 9/6 = 3/2``. Parse every member and bind each constant
                # member to the variable member.
                members=[parse(part) for part in equation.split('=')]
                if var is not None and any(member==var for member in members):
                    candidates.extend(member for member in members if not member.free_symbols)
            else:
                candidates.append(parse(equation))
        except (AssertionError,S.SympifyError,ValueError,SyntaxError,TypeError):
            pass
    return candidates
def evidence_numbers(elem):
    """Numerical values visibly present in solution prose or descriptions."""
    fields=[' '.join(elem.itertext())]
    fields.extend(value for child in elem.iter() for value in child.attrib.values())
    normalized=' '.join(fields).replace('−','-').replace(',','')
    return [S.Rational(token) for token in re.findall(r'(?<![A-Za-z])[-]?\d+(?:\.\d+)?',normalized)]

# Equations translated from the literal source prose; this is a separately
# reviewed semantic step, not claimed to be automatic natural-language proof.
WORDS={29:'x+11=54',30:'x+10=41',31:'x-12=51',32:'12t-11t=-14',33:'4x-3x=14',34:'7a-6a=-8',35:'w+28=57',36:'a+16=23',37:'h+26=68',38:'s-875=28675',39:'s-1025=19875',40:'n-3.25=7.75',91:'x+9=52',93:'m-10=-14',95:'y-30=40',97:'9x-8x=107',99:'n-1/6=1/2',101:'-4n+5n=-82',103:'m+7=18',105:'s+15=22',107:'t-5=16',109:'t+0.7=101.2',111:'p-17.43=103.76',113:'d+1/12=5/8'}
checks={5:True,6:False,7:True,41:True,43:False,115:False}
receipts=[]
for n,(s,g) in enumerate(zip(se,ge),1):
 ss=s.find(C+'solution'); gs=g.find(C+'solution')
 if ss is None: continue
 prob=s.find(C+'problem'); ff=formulas(prob); result={'source_order':n,'source_exercise':s.get('id'),'kind':'source-supplied','source_problem_sha256':sha(prob),'source_solution_sha256':sha(ss),'gujarati_solution_sha256':sha(gs)}
 if n in checks:
  if n==115:
   # English prose supplies the -8 candidate; math order contains the equation.
   eq=next(f for f in ff if '=' in f and len(residual(f).free_symbols)==1); var=S.Symbol('x'); candidate=S.Rational(-8)
  else:
   var,candidate=solution(ff[0]); eq=ff[1]
  lhs,rhs=sides(eq); lv=S.simplify(lhs.subs(var,candidate)); rv=S.simplify(rhs.subs(var,candidate)); actual=lv==rv
  assert actual==checks[n]
  txt=' '.join(gs.itertext())
  if n==5: assert any(S.simplify(v-candidate)==0 for v in displayed_value(gs,var))
  else: assert ('હા' if actual else 'ના') in txt,(n,txt)
  result.update(equation=eq,candidate=str(candidate),left=str(lv),right=str(rv),answer=actual,display_binding='actual Gujarati affirmative/negative text and source MathML')
 elif n in (1,2):
  var,val=solution(ff[1]); ans=S.simplify(parse(ff[0]).subs(var,val)); ds=displayed_value(gs)
  assert any(S.simplify(v-ans)==0 for v in ds),(n,ans,ds)
  result.update(expression=ff[0],substitution=str(val),answer=str(ans),displayed_candidates=list(map(str,ds)))
 elif n in (3,4):
  expr=ff[0] if n==3 else 'x-5'; ans=S.expand(parse(expr)); ds=displayed_value(gs)
  assert any(S.simplify(v-ans)==0 for v in ds),(n,ans,ds)
  result.update(expression=expr,answer=str(ans),displayed_candidates=list(map(str,ds)))
 else:
  eq=WORDS[n] if n in WORDS else ''.join(ff)
  var,ans=solution(eq); ds=displayed_value(gs,var)
  math_match=any(S.simplify(v-ans)==0 for v in ds)
  prose_values=evidence_numbers(gs)
  prose_match=any(S.simplify(v-ans)==0 for v in prose_values)
  assert math_match or prose_match,(n,eq,ans,ds,prose_values)
  if math_match:
   result['display_binding']={'kind':'actual solution MathML expression equality','candidates':list(map(str,ds))}
  else:
   result['display_binding']={'kind':'actual Gujarati solution prose/description numeric value','candidates':list(map(str,prose_values))}
  image_answers={20:('010c',S.Integer(18)),29:('013c',S.Integer(43)),32:('014b',S.Integer(-14)),35:('015g',S.Integer(29))}
  if n in image_answers:
   img,visual=image_answers[n]; name=f'CNX_ElemAlg_Figure_02_01_{img}_img_new.jpg'
   assert ans==visual
   result['display_binding'].update(image=name,sha256=hashlib.sha256((R/'media'/name).read_bytes()).hexdigest(),visually_transcribed_source_answer=str(visual))
  lhs,rhs=sides(eq); assert S.simplify((lhs-rhs).subs(var,ans))==0
  result.update(equation=eq,answer=str(ans),left=str(S.simplify(lhs.subs(var,ans))),right=str(S.simplify(rhs.subs(var,ans))),question_binding='source-prose semantic mapping' if n in WORDS else 'actual source question MathML')
 receipts.append(result)
assert len(receipts)==78

authored=json.loads((R/'support/NEW_ANSWERS.json').read_text(encoding='utf-8'))
new=[]
for a in authored:
 n=a['source_order']; s=se[n-1]; assert s.get('id')==a['source_exercise'] and s.find(C+'solution') is None
 prob=s.find(C+'problem'); ff=formulas(prob); eq=a['source_equation']
 if n in (42,44):
  var,candidate=solution(ff[0]); assert str(var)==a['variable'] and candidate==parse(a['candidate'])
  assert same_sides(ff[1],eq)
  lhs,rhs=sides(eq); lv=S.simplify(lhs.subs(var,candidate)); rv=S.simplify(rhs.subs(var,candidate))
  assert (lv==rv)==a['answer'] and lv==parse(a['lhs']) and rv==parse(a['rhs'])
 else:
  if n<=90 or n==116: assert same_sides(''.join(ff),eq),(n,ff,eq)
  var,ans=solution(eq); assert ans==parse(a['answer']),(n,ans,a['answer'])
  for step in a['steps']:
   v,x=solution(step); assert v==var and x==ans,(n,step,ans)
  # Bind the actual final worked step, not an unrelated expected-token list.
  v,x=solution(a['steps'][-1]); assert x==parse(a['answer'])
  lhs,rhs=sides(eq); lv=S.simplify(lhs.subs(var,ans)); rv=S.simplify(rhs.subs(var,ans)); assert lv==rv
 new.append({'source_order':n,'source_exercise':s.get('id'),'source_problem_sha256':sha(prob),'equation':eq,'answer':a['answer'],'left':str(lv),'right':str(rv),'steps_checked':len(a.get('steps',[])),'binding':'actual source MathML' if n<=90 or n==116 else 'source-prose semantic mapping; each original prompt read and mapping reviewed'})
assert len(new)==38 and {a['source_order'] for a in new}==set(range(42,117,2))
# Every newly authored diagnostic/example/recheck in support.html.
support=[('x+3=8','5'),('3x+1=10','3'),('x-6=11','17'),('y+8=3','-5'),('-3(y+4)+4y=5','17'),('x-1/4=1/2','3/4'),('y+0.7=1.2','0.5'),('p-8=24','32'),('b+7=19','12')]
for eq,value in support: assert solution(eq)[1]==parse(value)
assert residual('3x+1=10').subs(S.Symbol('x'),2)!=0
assert S.simplify(residual('-2(x-3)=-2x+6'))==0
# Adaptation rows contain equivalent equations, pending comparisons, or source
# equations awaiting substitution. Check each nonconstant chain has same answer.
for key,a in ADAPT.items():
 equations=[s.replace('?=','=') for s in a.get('math',[]) if '=' in s and s!='=']
 if not equations: continue
 symbolic=[]
 for eq in equations:
  r=residual(eq)
  if r.free_symbols: symbolic.append(solution(eq))
  else: assert r==0,(key,eq)
 if symbolic: assert len(set(symbolic))==1,(key,symbolic)
assert residual('5(12-4)-4(12)=-8')==0
output={'status':'pass','source_supplied':receipts,'new_missing_answers':new,'authored_learning_checks':{'positive_equations':len(support),'negative_candidate_checks':1,'distribution_identity':1},'figure_math':'all authored full equations verified; phrase correspondences reviewed against original images','limitations':['Natural-language-to-equation mappings require semantic reading, recorded separately from symbolic checks.','Image-only supplied results bound to hash-pinned, visually inspected source figures. No OCR confidence is substituted for a symbolic proof.']}
(R/'qa').mkdir(exist_ok=True); (R/'qa/MATH.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: 78 source-supplied, 38 new answers, all authored steps and learning checks')
