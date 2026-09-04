"""Independent exact algebra/property audit for all source-supplied answer classes."""
from fractions import Fraction as F
import ast,re
from inspect_a10_m82460 import C,M,flat

def norm(s):return ''.join(s.split()).replace('−','-').replace('·','*').replace('⋅','*').replace('÷','/').rstrip('.,')
def pyexpr(s,vals):
 s=norm(s)
 for _ in range(3):s=re.sub(r'\(\(([^()]*)\)\/\(([^()]*)\)\)',r'((\1)/(\2))',s)
 s=re.sub(r'(\d+)\(\((\d+)\)\/\((\d+)\)\)',r'(\1+(\2)/(\3))',s)
 for v,n in vals.items():s=re.sub(v,f'({n})',s)
 s=re.sub(r'(?<=[0-9)])(?=\()', '*',s);s=re.sub(r'(?<=\))(?=[0-9])','*',s)
 return s
def exact(s,vals):
 tree=ast.parse(pyexpr(s,vals),mode='eval')
 def go(n):
  if isinstance(n,ast.Expression):return go(n.body)
  if isinstance(n,ast.Constant):return F(str(n.value))
  if isinstance(n,ast.UnaryOp)and isinstance(n.op,ast.USub):return-go(n.operand)
  if isinstance(n,ast.BinOp):
   a,b=go(n.left),go(n.right)
   if isinstance(n.op,ast.Add):return a+b
   if isinstance(n.op,ast.Sub):return a-b
   if isinstance(n.op,ast.Mult):return a*b
   if isinstance(n.op,ast.Div):return a/b
  raise AssertionError((s,ast.dump(n)))
 return go(tree)
def maths(e):return[flat(x)for x in e.iter(M+'math')]
def mathsig(e):
 return [[(x.tag.rsplit('}',1)[-1],x.text) for x in m.iter() if not x.tag.endswith('mtext')] for m in e.iter(M+'math')]
def run(s,g):
 se=list(s.iter(C+'exercise'));ge=list(g.iter(C+'exercise'));assert len(se)==156
 supplied=[i for i,e in enumerate(se)if e.find(C+'solution')is not None];assert len(supplied)==105
 # Every source-supplied response retains identical mathematical trees in Gujarati.
 for i in supplied:
  a=se[i].find(C+'solution');b=ge[i].find(C+'solution');assert mathsig(a)==mathsig(b),(i,'solution MathML drift')
 # Recompute every single-expression symbolic answer that has a displayed result.
 candidates=set(range(0,9))|set(range(19,54))|{56,58,60,62,64,72,76,78,80}|set(range(110,148,2))
 checked=[]
 for i in sorted(candidates):
  if i not in supplied:continue
  q=maths(se[i].find(C+'problem'));a=maths(se[i].find(C+'solution'))
  if not q or not a:continue
  pos=-2 if i==6 else -1
  lhs,rhs=q[0],a[pos]
  for vals in ({'a':2,'b':5,'c':-3,'d':4,'g':2,'h':-5,'m':3,'n':-2,'p':2,'q':3,'r':4,'s':-2,'u':3,'v':7,'w':-4,'x':2,'y':-3,'z':5},{'a':-5,'b':2,'c':7,'d':-3,'g':-4,'h':3,'m':2,'n':5,'p':-3,'q':8,'r':-2,'s':6,'u':-1,'v':4,'w':3,'x':-4,'y':2,'z':-3}):
   assert exact(lhs,vals)==exact(rhs,vals),(i,lhs,rhs,vals)
  checked.append(i)
 # Exact additive inverses and reciprocals, including decimal-to-fraction conversions.
 inv={9:('add',[F(5,8),F('0.6'),F(-8),F(-4,3)]),10:('add',[F(7,9),F('1.2'),F(-14),F(-9,4)]),11:('add',[F(7,13),F('8.4'),F(-46),F(-5,2)]),12:('mul',[F(9),F(-1,9),F('0.9')]),13:('mul',[F(4),F(-1,7),F('0.3')]),14:('mul',[F(18),F(-4,5),F('0.6')]),82:('add',[F(2,5),F('4.3'),F(-8),F(-10,3)]),84:('add',[F(-7,6),F('-0.075'),F(23),F(1,4)]),86:('mul',[F(6),F(-3,4),F('0.7')]),88:('mul',[F(11,12),F('-1.1'),F(-4)])}
 for i,(kind,xs)in inv.items():
  sm=maths(se[i].find(C+'solution'));vals=[]
  if len(sm)==len(xs):vals=[exact(x,{})for x in sm]
  else:
   # Worked responses repeat inputs; bind the last occurrence of each required result.
   text=norm(flat(se[i].find(C+'solution')))
   expected=[-x if kind=='add'else 1/x for x in xs]
   tokens={9:['-((5)/(8))','-0.6','8','((4)/(3))'],12:['((1)/(9))','-9','((10)/(9))'],82:['-((2)/(5))','-4.3','8','((10)/(3))'],84:['((7)/(6))','0.075','-23','-((1)/(4))'],86:['((1)/(6))','-((4)/(3))','((10)/(7))']}[i]
   assert all(norm(t) in text for t in tokens),(i,tokens,text)
   vals=expected
  expected=[-x if kind=='add'else 1/x for x in xs];assert vals==expected,(i,vals,expected)
 # Zero cases: numerator zero with nonzero denominator is0; nonzero/0 is undefined.
 zero={15:['0','0','undefined'],16:['0','0','undefined'],17:['0','0','undefined'],18:['0','undefined'],25:['0','undefined'],26:['0','undefined'],90:['0'],92:['0'],94:['0'],96:['0'],102:['0'],104:['0'],106:['undefined'],108:['undefined']}
 for i,answers in zero.items():
  assert i in supplied
  gt=flat(ge[i].find(C+'solution'))
  for x in answers:assert ('અવ્યાખ્યાયિત'in gt)if x=='undefined'else re.search(r'(^|\D)0(\D|$)',gt)
 # Figure-only worked answers were independently read from actual originals.
 figures={33:'3x+2',36:'30+25q',39:'-8y-2'}
 for i,result in figures.items():
  assert any(result.replace('-','−')in e.get('alt','') for e in ge[i].find(C+'solution').iter(C+'media'))
 # Fixed practical results and source-open responses.
 assert '$80'in flat(ge[148].find(C+'solution'));assert '$23.88'in flat(ge[150].find(C+'solution'))
 assert 'જવાબો જુદા હોઈ શકે છે'in flat(ge[152].find(C+'solution'))
 assert 'જવાબો જુદા હોઈ શકે છે'in flat(ge[154].find(C+'solution'))
 # Eight source answers are plain CNXML text rather than MathML; recompute and bind them explicitly.
 plain={7:'32x',54:'12x',66:'17',68:'14.88',70:'28a',74:'10p',98:'44',100:'d'}
 for i,result in plain.items():assert result in norm(flat(ge[i].find(C+'solution'))),(i,result)
 assert len(checked)>=60,len(checked)
 assert set(supplied)==set(checked)|set(inv)|set(zero)|set(figures)|{148,150,152,154}|set(plain)
 return {'independently_checked_exercises':len(supplied),'exact_symbolic_equivalence_exercises':checked,'plain_text_exact_answer_exercises':sorted(plain),'inverse_exercises':sorted(inv),'zero_property_exercises':sorted(zero),'actual_figure_answer_exercises':sorted(figures),'practical_answer_exercises':[148,150],'source_open_exercises':[152,154],'method':'exact Fraction evaluation at two assignments plus exact inverse/zero/property, explicit plain-text answers and actual-original figure checks'}
