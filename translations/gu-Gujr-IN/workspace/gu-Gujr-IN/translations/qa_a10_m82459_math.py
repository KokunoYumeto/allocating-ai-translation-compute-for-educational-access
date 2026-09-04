"""Independent exact rational, square-root, classification and order audit.

No binary decimal arithmetic. Irrational roots are certified by integer-square
bounds. Ellipsis-only inputs are explicitly conditional, never certified from
a finite prefix. Image point lists were independently read from all originals.
"""
from fractions import Fraction as F
from math import isqrt
import re
from inspect_a10_m82459 import C,M,flat
def clean(t):
 t=re.sub(r'\s+','',t).replace('−','-')
 if t.endswith('.')and not t.endswith('...'):t=t[:-1]
 return t.rstrip(',;')
def number(t):
 t=clean(t)
 if '…'in t or t.endswith('...'):return ('assumed_irrational',t.replace('...','…'))
 z=re.fullmatch(r'(-?)sqrt\((-?\d+)\)',t)
 if z:
  sign,n=z.groups();n=int(n);sgn=-1 if sign else 1
  if n<0:return ('nonreal',(sgn,n))
  k=isqrt(n)
  if k*k==n:return ('rational',F(sgn*k))
  assert k*k<n<(k+1)*(k+1)
  return ('irrational',(sgn,n))
 z=re.fullmatch(r'(-?)(\d+)\.(\d*)overbar\((\d+)\)',t)
 if z:
  sign,n,prefix,cycle=z.groups();k=len(prefix)
  v=F(n)+F(int(prefix or '0'),10**k)+F(int(cycle),10**k*(10**len(cycle)-1))
  return ('rational',-v if sign else v)
 z=re.fullmatch(r'(-?)(\d+)\(\((\d+)\)/\((\d+)\)\)',t)
 if z:
  sign,n,a,b=z.groups();v=F(n)+F(int(a),int(b));return ('rational',-v if sign else v)
 z=re.fullmatch(r'(-?)\(\((-?\d+)\)/\((\d+)\)\)',t)
 if z:
  sign,a,b=z.groups();return ('rational',(-1 if sign else 1)*F(int(a),int(b)))
 return ('rational',F(t))
def values(t):
 return[number(x)for x in re.split(r',|and|અને',t)if clean(x)]
def maths(e):return list(e.iter(M+'math'))
def qvalues(e):
 out=[]
 for x in maths(e):
  t=flat(x)
  if clean(t)not in {'<','>'}:out.extend(values(t))
 if not out:out=[number(x)for x in re.findall(r'[-−]?\d+(?:\.\d+)?',flat(e))]
 return out
def same(a,b):assert a==b,(a,b)
def parts(t):return re.split('[ⓐⓑⓒⓓⓔ]',t)[1:]
def compare(t):
 if '_'in t and ':'in t:t=t.rsplit(':',1)[-1]
 a,b=re.split(r'_+|<|>',t);x=number(a);y=number(b)
 assert x[0]==y[0]=='rational'
 return '>'if x[1]>y[1]else'<'if x[1]<y[1]else'='
def classify(xs,kind):
 if kind=='whole':return[x for x in xs if x[0]=='rational'and x[1].denominator==1 and x[1]>=0]
 if kind=='integer':return[x for x in xs if x[0]=='rational'and x[1].denominator==1]
 if kind=='rational':return[x for x in xs if x[0]=='rational']
 if kind=='irrational':return[x for x in xs if x[0]in {'irrational','assumed_irrational'}]
 if kind=='real':return[x for x in xs if x[0]!='nonreal']
def run(s,g):
 se=list(s.iter(C+'exercise'));ge=list(g.iter(C+'exercise'));checked=[];conditional=[];open_ex=[]
 image_points={
 21:('003_img_new', ['-3','-((5)/(2))','-((1)/(4))','((3)/(4))','((6)/(5))','((7)/(3))','4']),
 22:('004_img_new',['-((8)/(3))','-((7)/(4))','-1','((1)/(3))','((6)/(5))','((9)/(2))','5']),
 23:('005_img_new',['-((7)/(3))','-2','-((7)/(4))','((2)/(3))','((7)/(5))','3','((7)/(2))']),
 27:('007_new',['0.4']),28:('008_img_new',['0.6']),29:('009_img_new',['0.9']),
 30:('010_new',['-0.74']),31:('011_img_new',['-0.6']),32:('012_img_new',['-0.7']),
 74:('202_img_new',['((3)/(4))','((8)/(5))','((10)/(3))']),76:('203_img_new',['((3)/(10))','((11)/(6))','((7)/(2))','4']),
 78:('205_img_new',['-((2)/(5))','((2)/(5))']),80:('207_img_new',['-((5)/(2))','-1((2)/(3))','-((3)/(4))','((3)/(4))','1((2)/(3))','((5)/(2))']),
 90:('209_img_new',['0.8']),92:('211_img_new',['-1.6'])}
 simplify={0,1,2,3,4,5,42,44,46,48,50,52};ratios={6,7,8,54,56}
 pairkind={12,13,14,62,64};realpair={15,16,17,66,68};cat={9,10,11,18,19,20,58,60,70,72}
 order={24,25,26,33,34,35,36,37,38,39,40,41,82,84,86,88,94,96,98,100}
 for j,(a,b)in enumerate(zip(se,ge)):
  sol=a.find(C+'solution');gs=b.find(C+'solution');p=a.find(C+'problem');gp=b.find(C+'problem')
  if sol is None:same(gs,None);continue
  if j==104:
   assert 'Answers may vary'in flat(sol)and'જવાબો જુદા હોઈ શકે છે'in flat(gs);open_ex.append(a.get('id'));continue
  record={'index':j,'exercise':a.get('id')};binding=''
  if j in simplify|ratios:
   qp=parts(flat(p));expected=[number(x)for x in qp]if qp else qvalues(p)
   if j in {0,3,6}:
    def output_rows(e):return[number(flat(t[-1]))for t in e.iter(M+'mtable')]
    actual=output_rows(sol);gactual=output_rows(gs)
   else:
    actual=qvalues(sol);gactual=qvalues(gs)
   same(expected,actual);same(expected,gactual);binding='exact rational result from source input, final MathML rows or supplied numbers'
  elif j in pairkind|realpair:
   xs=qvalues(p);enparts=parts(flat(sol));gparts=parts(flat(gs));assert len(xs)==len(enparts)==len(gparts)==2
   for x,ep,gpart in zip(xs,enparts,gparts):
    if j in pairkind:
     en=re.findall(r'\birrational\b|\brational\b',ep)[-1];gu=re.findall(r'અસંમેય|(?<!અ)સંમેય',gpart)[-1]
     same(en,x[0]);same(gu,'સંમેય'if x[0]=='rational'else'અસંમેય')
    else:
     en=re.findall(r'not a real number|real number',ep)[-1];gu=re.findall(r'વાસ્તવિક સંખ્યા નથી|વાસ્તવિક સંખ્યા છે|વાસ્તવિક સંખ્યા',gpart)[-1]
     same(en,'not a real number'if x[0]=='nonreal'else'real number');same(gu.endswith('નથી'),x[0]=='nonreal')
   binding='integer-square bounds and negative-radicand domain, final English/Gu classification labels'
  elif j in cat:
   xs=qvalues(p);kinds=['whole','integer','rational','irrational','real']if j in {18,19,20,70,72}else['rational','irrational']
   expected=[classify(xs,k)for k in kinds]
   if j==18:
    for ss in [sol,gs]:
     mm=maths(ss);actual=[[number('8')],values(flat(mm[2])),values(flat(mm[5])),values(flat(mm[6])),xs]
     same(actual,expected)
    assert '8 is the only whole number'in flat(sol)and'માત્ર 8 જ પૂર્ણ સંખ્યા'in flat(gs)
    assert 'All the numbers listed are real numbers'in flat(sol)and'બધી સંખ્યાઓ વાસ્તવિક સંખ્યાઓ છે'in flat(gs)
   elif j==9:
    same(expected,[[number('0.58overbar(3)'),number('0.47')],[number('3.605551275…')]])
    assert '0.47 are rational'in flat(sol)and'0.47 સંમેય છે'in flat(gs)
    for ss in [sol,gs]:same([number(flat(maths(ss)[k]))for k in [1,3]],[expected[0][0],expected[1][0]])
   else:
    for ss in [sol,gs]:
     ps=parts(flat(ss));actual=[]
     for pp in ps:actual.append([]if pp.strip()in {'none','કોઈ નહીં'}else values(pp))
     same(actual,expected)
   if any(x[0]=='assumed_irrational'for x in xs):conditional.append(a.get('id'));record['condition']='ellipsis-only continuation assumed nonterminating/nonrepeating; explicit source erratum'
   binding='complete category membership including zero, exact fractions, recurring identities and integer-square bounds'
  elif j in image_points:
   suffix,points=image_points[j];expected=[number(x)for x in points];same(sorted(qvalues(p),key=lambda x:x[1]),expected)
   for ss in [sol,gs]:
    im=next(e for e in ss.iter(C+'media')if e.find(C+'image').get('src').endswith(suffix+'.jpg'))
    alt=im.get('alt');assert alt
   # Gujarati labels bind each original point; mixed-number labels remain explicit.
   for point in points:
    token=point.replace('-','−')
    token=re.sub(r'\(\((\d+)\)/\((\d+)\)\)',r'\1/\2',token)
    token=token.replace('−12/3','−1 પૂર્ણ 2/3').replace('12/3','1 પૂર્ણ 2/3')
    assert token in alt,(j,token,alt)
   record['original_image']=suffix+'.jpg';record['verified_points']=[str(x[1])for x in expected]
   binding='all original points independently viewed; exact sorted source inputs and current Gujarati alternative'
  elif j in order:
   qs=[flat(x)for x in maths(p)if '_'in flat(x)]
   if not qs:qs=[flat(p)]
   expected=[compare(x)for x in qs]
   for ss in [sol,gs]:
    if j==24:answers=[flat(t[-1])for t in ss.iter(M+'mtable')]
    elif j in {33,36,39}:answers=[flat(maths(ss)[-1])]
    else:answers=re.findall('[<>]',flat(ss))
    actual=[]
    for answer in answers:
     sign=re.findall('[<>]',answer)[0]
     if len(answer.strip())>1:same(compare(answer),sign)
     actual.append(sign)
    same(actual,expected)
   binding='exact signed-fraction/decimal ordering; displayed final inequality and operand order'
  elif j==102:
   assert '147'in flat(p)and'44'in flat(p);buses=(147+44-1)//44;same(buses,4);assert 3*44<147<=4*44
   assert '4 busses'in flat(sol)and'4 બસ'in flat(gs);assert flat(gs).count('જવાબો જુદા હોઈ શકે છે')==2
   binding='capacity ceiling4, not ordinary rounding; two source-open explanation parts preserved'
  else:raise AssertionError(('unreviewed supplied solution',j))
  record['binding']=binding;checked.append(record)
 assert len(checked)==73 and len(conditional)==7 and len(open_ex)==1
 return {'independently_checked_exercises':73,'determinate_mathematical_exercises':66,'conditional_ellipsis_exercises':conditional,'source_open_exercises':open_ex,'partially_open_exercise':se[102].get('id'),'image_answer_exercises':15,'checks':checked}
