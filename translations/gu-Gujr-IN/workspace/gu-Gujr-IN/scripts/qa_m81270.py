"""Independent exact arithmetic/polynomial QA for the full m81270 translation."""
import ast,hashlib,json,re,sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
import xml.etree.ElementTree as E
from prepare_m81270 import ROOT,SOURCE,SHA,gather,ATTRIBUTES
from a00_accessibility_attributes import validate_pair,LANGUAGE_ATTRS
C='{http://cnx.rice.edu/cnxml}';M='{http://www.w3.org/1998/Math/MathML}'
OUTPUT=ROOT/'gu-Gujr-IN/translations/a00-m81270.gu.cnxml'
MEDIA=ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'
flat=lambda e:' '.join(''.join(e.itertext()).split())
def mathtext(e):
 tag=e.tag.removeprefix(M)
 if tag=='mtext':
  t=(e.text or '').strip()
  if t in ('when','જ્યારે'):return '@'
  if t in ('and','અને'):return ','
  if t in ('Evaluate','કિંમત શોધો:'):return ''
  raise ValueError(t)
 if tag=='mtable':raise ValueError('table is checked cell by cell')
 if tag=='msup':return '('+mathtext(e[0])+')**('+mathtext(e[1])+')'
 if tag=='mfrac':return '('+mathtext(e[0])+')/('+mathtext(e[1])+')'
 if tag=='mspace':return ''
 pieces=[]
 for c in e:
  t=mathtext(c)
  if c.tag==M+'menclose' and c.get('notation')=='longdiv':t='('+t+')/('+pieces.pop()+')'
  pieces.append(t)
 return (e.text or '')+''.join(pieces)
def norm(t):
 t=re.sub(r'(?<=\d),(?=\d{3}(?:\D|$))','',t)
 t=re.sub(r'\s+','',t).replace('−','-').replace('–','-').replace('÷','/').rstrip('.;')
 for c in '·⋅×':t=t.replace(c,'*')
 t=t.replace('[','(').replace(']',')')
 t=re.sub(r'(?<=[\da-z)])(?=[a-z(])','*',t)
 t=re.sub(r'(?<=[a-z)])(?=\d)','*',t)
 return t
def evaluate(t,env=None):
 env=env or {}
 if not re.fullmatch(r'[a-z0-9+*()/\-]+',t):raise ValueError(t)
 def walk(n):
  if isinstance(n,ast.Expression):return walk(n.body)
  if isinstance(n,ast.Constant) and type(n.value)is int:return Fraction(n.value)
  if isinstance(n,ast.Name) and n.id in env:return Fraction(env[n.id])
  if isinstance(n,ast.UnaryOp)and isinstance(n.op,ast.USub):return -walk(n.operand)
  if isinstance(n,ast.BinOp):
   a,b=walk(n.left),walk(n.right)
   if isinstance(n.op,ast.Add):return a+b
   if isinstance(n.op,ast.Sub):return a-b
   if isinstance(n.op,ast.Mult):return a*b
   if isinstance(n.op,ast.Div):return a/b
   if isinstance(n.op,ast.Pow)and b.denominator==1:return a**int(b)
  raise ValueError(t)
 return walk(ast.parse(t,mode='eval'))
def polynomial(t):
 # Sparse exact polynomials: tuple of sorted variable names -> coefficient.
 def add(a,b,sign=1):
  o=defaultdict(Fraction,a)
  for k,v in b.items():o[k]+=sign*v
  return {k:v for k,v in o.items()if v}
 def mul(a,b):
  o=defaultdict(Fraction)
  for ka,va in a.items():
   for kb,vb in b.items():o[tuple(sorted(ka+kb))]+=va*vb
  return {k:v for k,v in o.items()if v}
 def walk(n):
  if isinstance(n,ast.Expression):return walk(n.body)
  if isinstance(n,ast.Constant)and type(n.value)is int:return {():Fraction(n.value)}if n.value else{}
  if isinstance(n,ast.Name)and re.fullmatch('[a-z]',n.id):return {(n.id,):Fraction(1)}
  if isinstance(n,ast.UnaryOp)and isinstance(n.op,ast.USub):return {k:-v for k,v in walk(n.operand).items()}
  if isinstance(n,ast.BinOp):
   a,b=walk(n.left),walk(n.right)
   if isinstance(n.op,ast.Add):return add(a,b)
   if isinstance(n.op,ast.Sub):return add(a,b,-1)
   if isinstance(n.op,ast.Mult):return mul(a,b)
   if isinstance(n.op,ast.Div)and set(b)=={()}:return {k:v/b[()]for k,v in a.items()}
   if isinstance(n.op,ast.Pow)and set(b)=={()}and b[()].denominator==1 and 0<=b[()]<=12:
    result={():Fraction(1)}
    for _ in range(int(b[()])):result=mul(result,a)
    return result
  raise ValueError(t)
 if not re.fullmatch(r'[a-z0-9+*()/\-]+',t):raise ValueError(t)
 return walk(ast.parse(t,mode='eval'))
def exprs(e):
 out=[]
 for m in e.iter(M+'math'):
  try:out.append(norm(mathtext(m)))
  except ValueError:out.append(None)
 return out
def written(e):
 if e.tag==M+'math':return mathtext(e)
 if e.tag==C+'span'and e.get('class')=='token':return ''
 result=e.text or ''
 for c in e:result+=('**('+flat(c)+')'if c.tag==C+'sup'else written(c))+(c.tail or '')
 return result
def answer_forms(solution):
 lst=solution.find('.//'+C+'list')
 pieces=list(lst)if lst is not None else [solution]
 try:forms=[norm(written(x))for x in pieces]
 except ValueError:return None
 return forms if all(re.fullmatch(r'[a-z0-9+*()/\-]+',f)for f in forms)else None
def numerical_inputs(problem):
 pp=exprs(problem)
 if not pp or any(p is None for p in pp):return None
 # First expression may include when and all assignments or have later math
 # nodes/list items containing the assignments. Every assignment is source-bound.
 first=pp[0].split('@');formula=first[0].rstrip(',');extra=first[1:]+pp[1:]
 if not extra:return None
 assignments=[]
 for fragment in extra:
  assignments+=re.findall(r'([a-z])=(\d+)',fragment)
 if not assignments:return None
 if len({k for k,v in assignments})==1 and len(assignments)>1:return formula,[{k:int(v)}for k,v in assignments]
 return formula,[{k:int(v)for k,v in assignments}]

LABELS={f'CNX_BMath_Figure_02_02_{n}_img-01.png':[[old,new]]for n,old,new in [
 ('016','Substitute 5 for x.','xની જગ્યાએ 5 મૂકો.'),('017','Substitute 1 for x.','xની જગ્યાએ 1 મૂકો.'),('018','Substitute 10 for x.','xની જગ્યાએ 10 મૂકો.'),('019','Substitute 5 for x.','xની જગ્યાએ 5 મૂકો.'),('020','Substitute 10 for x and 2 for y.','xની જગ્યાએ 10 અને yની જગ્યાએ 2 મૂકો.'),('021','Substitute 4 for each x.','દરેક xની જગ્યાએ 4 મૂકો.') ]}
SELF_CHECK={'media_id':'eip-id1165721410747','image':'CNX_BMath_Figure_AppB_008.jpg','columns':['હું આ કરી શકું છું…','વિશ્વાસપૂર્વક','થોડી મદદથી','ના—મને સમજાતું નથી!'],'rows':['બીજગણિતની પદાવલીઓની કિંમત શોધવી.','પદ, સહગુણક અને સજાતીય પદો ઓળખવાં.','સજાતીય પદો ભેગાં કરીને પદાવલીઓ સરળ કરવી.','શબ્દસમૂહોને બીજગણિતની પદાવલીઓમાં ફેરવવાં.'],'response_cells':[[None]*3 for _ in range(4)]}
ERRATA={
 'eip-id1166566546426':{'kind':'aria-wrong-substituted-expression','issue':'Source says3+x=10. Actual image and body use3+7=10.','corrected_aria_gu':'પદાવલી x + 7માં xની જગ્યાએ 3 મૂકો. 3 + 7 = 10.'},
 'eip-id1166566410105':{'kind':'aria-wrong-substituted-expression','issue':'Source says12+x=19. Actual image and body use12+7=19.','corrected_aria_gu':'પદાવલી x + 7માં xની જગ્યાએ 12 મૂકો. 12 + 7 = 19.'},
 'eip-id1168469463011':{'kind':'alt-decimal-confusion','issue':'Source quotes9.5−2and9.5but actual image is9·5−2.','corrected_alt_gu':'પદાવલી 9 · 5 − 2 છે. માત્ર 5 લાલ છે; બાકી સંખ્યાઓ, ગુણાકારનું ટપકું અને ઓછાની નિશાની કાળાં છે.'},
 'eip-id1168469574762':{'kind':'alt-exponent-position','issue':'Source says2x, but actual019-02hasxasexponent,2^x.','corrected_alt_gu':'પદાવલી 2ની xમી ઘાત છે; x, આધાર 2ની જમણે ઉપર ઘાતાંક તરીકે છે.'},
 'eip-id1168469574804':{'kind':'alt-factor-count-ambiguity','issue':'Source says multiplied by itself five times, while the actual019-04image and formula have five factors2 and four multiplication signs. State factors explicitly.','corrected_alt_gu':'સંખ્યા 2 પાંચ અવયવ તરીકે આવે છે: 2 · 2 · 2 · 2 · 2. વચ્ચે ગુણાકારની ચાર નિશાની છે. ગુણનફળ 32 છે, એટલે 2ની 5મી ઘાત.'},
 'eip-id1166566546467':{'kind':'alt-expression-called-equation','issue':'Source calls3+7anequation despite noequalsign.','corrected_alt_gu':'પદાવલી 3 + 7 છે. 3 લાલ છે અને વત્તાની નિશાની તથા 7 કાળાં છે.'},
 'eip-id1168466011092':{'kind':'alt-expression-called-equation','issue':'Source calls2x²+3x+8aquadraticequation; it is anexpression/polynomial.','corrected_alt_gu':'દ્વિઘાત પદાવલી 2x² + 3x + 8 છે. પહેલું પદ 2 ગુણ્યા xનો વર્ગ છે.'},
 'fs-id2266631':{'kind':'aria-row-count','issue':'Source says5rows; actual table has4includingheader.','corrected_aria_gu':'ચાર હરોળ અને બે સ્તંભનું કોષ્ટક. સ્તંભનાં નામ પદ અને સહગુણક છે. પદ 9aનો સહગુણક 9, પદ yનો સહગુણક 1 અને પદ 5x²નો સહગુણક 5 છે.'},
 'fs-id1605094':{'kind':'alt-wrong-sign','issue':'Source alt says+2x; actual015diagram has−2xbefore and after moving it.','corrected_alt_gu':'પહેલી પદાવલી 3x + 4y − 2x + 6y છે. વચ્ચેનાં +4y અને −2x પદોની જગ્યા બદલતાં 3x − 2x + 4y + 6y મળે છે. ઓછાની નિશાની 2x સાથે જ રહે છે. બંને પદાવલી સરળ કરતાં x + 10y મળે છે.'},
 'eip-id1168467195542':{'kind':'aria-wrong-signs-and-result','issue':'Source aria is copied from anallplus exampleand gives8x²+12x. Actual023sequence and lesson use subtraction giving6x²+4x.','corrected_aria_gu':'પદાવલી 7x² + 8x − x² − 4x છે. સજાતીય પદો એકસાથે ગોઠવતાં 7x² − x² + 8x − 4x મળે છે. ઘાતાંક અને ચલ એ જ રાખીને સહગુણકોનો તફાવત લો: 7 − 1 = 6 અને 8 − 4 = 4. પરિણામ 6x² + 4x છે. બંને પદ સજાતીય નથી, તેથી વધુ ભેગાં કરી શકાતાં નથી.'},
 'fs-id1362744':{'kind':'solution-choice-label','issue':'The second supplied answer repeatsⓐ; it corresponds toⓑ. Canonicaltokenpreserved;Indonesianusesⓑ.','corrected_gu':'ⓐ 4(p + q); ⓑ 4p + q'},
 'fs-id3447413':{'kind':'source-phrase-ambiguity','issue':'Nine times five less than twice x has unclear English grouping. Indonesianinterprets9(2x−5). Gujarati makes that intendedinstructionexplicit; no suppliedansweradded.','intended_expression':'9*(2*x-5)','reader_note_gu':'મૂળ અંગ્રેજી શબ્દસમૂહમાં જૂથ સ્પષ્ટ નથી. અહીં અર્થ છે: xને બમણો કરો, તેમાંથી પાંચ બાદ કરો અને મળેલા પરિણામના નવ ગણા કરો.'},
}
BRIDGES={
 'fs-id2208916':{'kind':'English-and-encoded-as-identifiers','issue':'The source EnglishandisencodedasthreeMathMLmi tokens a,n,d. All three remain unchanged because non-mtextmath tokens are preserved.','reader_note_gu':'આ પંક્તિમાં અંગ્રેજી andનો અર્થ અને છે. અહીં તફાવત લેવાની સંખ્યાઓ 20 અને 4 છે; પદાવલી 20 − 4 બને છે.'},
 'fs-id3011311':{'kind':'signed-terms-domain-note','reader_note_gu':'મૂળ પાઠ અહીં ઉમેરેલાં પદોની વાત કરે છે અને આગળ ઋણ સહગુણકો પણ લે છે. પદ સાથે તેની નિશાની રાખવી: −2xને ખસેડો ત્યારે ઓછાની નિશાની પણ સાથે ખસે છે.'},
}
ENLARGED={f'CNX_BMath_Figure_02_02_{n}_img-01.png'for n in ('016','017','018','019','020','021')}|{'CNX_BMath_Figure_AppB_008.jpg','CNX_BMath_Figure_02_02_015_img.jpg','CNX_BMath_Figure_02_02_016_img-03.png','CNX_BMath_Figure_02_02_019_img-02.png',*(f'CNX_BMath_Figure_02_02_023_img-0{n}.png'for n in (2,3,4))}
SIMPLIFY_IDS=set('fs-id1198821 fs-id1369298 fs-id1531346 fs-id1361054 fs-id2265620 fs-id1951243 fs-id2777870 fs-id2207889 fs-id1787268 fs-id2214125 fs-id2662762 fs-id2443073'.split())
WORD_FORMS={
 'fs-id1373796':['47-41','5*x/2'],'fs-id1881870':['17+19','7*x'],
 'fs-id1269389':['x+11','11*a-14'],'fs-id2257971':['j+19','2*x-21'],
 'fs-id1362744':['4*(p+q)','4*p+q'],'fs-id1909857':['2*x-8','2*(x-8)'],
 'fs-id2161945':['w-5'],'fs-id2211820':['l+2'],'fs-id2199400':['6*q-7'],'fs-id1816678':['4*n+8'],
 'fs-id1376085':['8+12'],'fs-id1935473':['14-9'],'fs-id2777756':['9*7'],'fs-id1966910':['36/9'],
 'fs-id1408808':['x-4'],'fs-id1605936':['6*y'],'fs-id1407244':['8*x+3*x'],'fs-id2202614':['y/3'],
 'fs-id2643011':['8*(y-9)'],'fs-id2370308':['5*(x+y)'],'fs-id2391056':['b+15'],'fs-id2287979':['b-4'],'fs-id3292991':['2*n-7'],
}
EVAL_SEQUENCES={
 'fs-id1177441':[['3+7','10'],['12+7','19']],
 'fs-id2219842':[['9*5-2','45-2','43'],['9*(1)-2','9-2','7']],
 'fs-id1610002':[['10**2','10*10','100']],
 'fs-id1567145':[['2**5','2*2*2*2*2','32']],
 'fs-id1408555':[['3*10+4*2-6','30+8-6','32']],
 'fs-id1788450':[['2*4**2+3*4+8','2*16+3*4+8','32+12+8','52']],
}
POLY_SEQUENCES={
 'fs-id2261867':['3*x+6*x','x+x+x+x+x+x+x+x+x','9*x'],
 'fs-id1605094':['3*x+4*y-2*x+6*y','3*x-2*x+4*y+6*y','x+10*y'],
 'fs-id1558860':['3*x+7+4*x+5','3*x+4*x+7+5','7*x+12'],
 'fs-id1336931':['7*x**2+8*x-x**2-4*x','7*x**2-x**2+8*x-4*x','6*x**2+4*x'],
}
def single_term(t):
 p=polynomial(t);assert len(p)==1,(t,p)
 return next(iter(p.items()))
def like_groups(formula):
 terms=formula.split(',')if ','in formula else formula.split('+')
 groups=defaultdict(list)
 for term in terms:
  key,coefficient=single_term(term);groups[key].append(polynomial(term))
 return list(g for g in groups.values()if len(g)>1)
def group_signature(groups):
 return sorted(tuple(sorted(str(sorted(p.items()))for p in group))for group in groups)
def main():
 sys.stdout.reconfigure(encoding='utf-8');assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
 source=E.parse(SOURCE).getroot();target=E.parse(OUTPUT).getroot()
 assert target.attrib.pop('{http://www.w3.org/XML/1998/namespace}lang')=='gu-Gujr-IN'
 stats=validate_pair(source,target);allowed=set('abcdefghijklmnopqrstuvwxyz')|{'ab'}
 for owner,slots in gather(target).items():
  for e,f,t in slots:assert all(w in allowed for w in re.findall('[A-Za-z]+',t)),(owner,f,t)
 for e in target.iter():
  for k,v in e.attrib.items():
   if k in LANGUAGE_ATTRS:assert re.search('[\u0a80-\u0aff]',v)and all(w in allowed for w in re.findall('[A-Za-z]+',v)),(e.get('id'),k,v)
 exs={e.get('id'):e for e in target.iter(C+'exercise')};evaluated=[];identities=[];numeric=[]
 for ident,ex in exs.items():
  p=ex.find(C+'problem');s=ex.find(C+'solution')
  if s is None:continue
  forms=answer_forms(s)
  if forms is None:continue
  inputs=numerical_inputs(p)
  if inputs:
   formula,envs=inputs
   assert len(forms)==len(envs),(ident,forms,envs)
   assert [evaluate(formula,v)for v in envs]==[evaluate(f)for f in forms],(ident,formula,envs,forms)
   evaluated.append((ident,len(envs)));continue
  pp=exprs(p)
  if ident in SIMPLIFY_IDS|{'fs-idm216816528','fs-idm216233584'}:
   assert len(pp)==len(forms)and all(q and re.fullmatch(r'[a-z0-9+*()/\-]+',q)for q in pp),(ident,pp,forms)
   # Coefficient questions are not polynomial simplification.
   if ident in ('fs-id1459626','fs-id2924560'):continue
   assert [polynomial(q)for q in pp]==[polynomial(f)for f in forms],(ident,pp,forms)
   (identities if any(re.search('[a-z]',q)for q in pp)else numeric).append(ident)
 assert set(identities)==SIMPLIFY_IDS
 # All remaining bare word-to-algebra answers, with grouping/operand order.
 word_parts=0
 for ident,wanted in WORD_FORMS.items():
  got=answer_forms(exs[ident].find(C+'solution'));assert got is not None and len(got)==len(wanted),(ident,got)
  assert [polynomial(t)for t in got]==[polynomial(t)for t in wanted],(ident,got,wanted)
  word_parts+=len(wanted)
 # Each numerical worked image path is bound to its actual source variables.
 image_steps=0
 for ident,paths in EVAL_SEQUENCES.items():
  formula,envs=numerical_inputs(exs[ident].find(C+'problem'));assert len(envs)==len(paths)
  for env,path in zip(envs,paths):
   wanted=evaluate(formula,env)
   assert all(evaluate(row)==wanted for row in path),(ident,env,path)
   image_steps+=len(path)
 for ident,rows in POLY_SEQUENCES.items():
  assert all(polynomial(row)==polynomial(rows[0])for row in rows),(ident,rows)
  if ident in exs:assert polynomial(exprs(exs[ident].find(C+'problem'))[0])==polynomial(rows[0])
 assert polynomial('2*x**2')!=polynomial('(2*x)**2')
 assert evaluate('2*x**2',{'x':4})==32 and evaluate('(2*x)**2',{'x':4})==64
 # Four compact supplied like-term answers: preserve the complete groups.
 likes=0
 for ident in ('fs-id2466455','fs-id2284527','fs-id1693521','fs-id2269831'):
  ex=exs[ident];expected=like_groups(exprs(ex.find(C+'problem'))[0]);text=written(ex.find(C+'solution'))
  got=[[polynomial(norm(t))for t in group.split('અને')]for group in text.split(';')]
  assert group_signature(expected)==group_signature(got),(ident,expected,got)
  likes+=len(got)
 # Worked like-term example: every repeated monomial class, constants included.
 mainlike=exprs(exs['fs-id1308316'].find(C+'problem'))
 assert [len(g)for g in like_groups(mainlike[0])]==[2,2,2]
 assert [len(g)for g in like_groups(mainlike[1])]==[2,3]
 # Explicit term/coefficient tables and compact exercise answers.
 lookup={e.get('id'):e for e in target.iter()if e.get('id')}
 coefrows=list(lookup['fs-id2266631'].iter(C+'row'))[1:];assert len(coefrows)==3
 for row in coefrows:
  term=exprs(row[0])[0];coefficient=exprs(row[1])[0]
  assert single_term(term)[1]==evaluate(coefficient)
 for ident in ('fs-id1459626','fs-id2924560'):
  ex=exs[ident];assert single_term(exprs(ex.find(C+'problem'))[0])[1]==evaluate(answer_forms(ex.find(C+'solution'))[0])
 for ident,expected in [('fs-id1791962',[4,3,2]),('fs-id1790324',[9,13,1])]:
  text=flat(exs[ident].find(C+'solution')).split('સહગુણકો',1)[1]
  assert [int(x)for x in re.findall(r'\d+',text)]==expected
 for ident,expected in [('fs-id1405969',9),('fs-id2593979',15),('fs-id1944608',1),('fs-id2265026',6)]:
  assert evaluate(exprs(lookup[ident])[-1])==expected
 # Terms lists are kept as the source's four/five cell rows, not prematurely
 # combined; a constant and the implicit unit coefficient are included.
 termsrows=list(lookup['fs-id1596496'].iter(C+'row'))[1:];assert len(termsrows)==5
 for row in termsrows:
  expression=exprs(row[0])[0];term_list=exprs(row[1])[0]
  assert polynomial(expression)==polynomial('+'.join(term_list.split(',')))
 for ident in ('fs-id1471893','fs-id1722869'):
  ex=exs[ident];answer=norm(written(ex.find(C+'solution')))
  assert polynomial(exprs(ex.find(C+'problem'))[0])==polynomial('+'.join(answer.split(',')))
 # Seven actual MathML tables, including the Englishandmi encoding and
 # exact fraction/notation equivalence in the quotient explanation.
 tables=list(target.iter(M+'mtable'));assert len(tables)==7
 for ident,wanted in [('fs-id2208916','20-4'),('fs-id14671710','10*x/3'),('fs-id2284969','y+8'),('fs-id2190936','9*z-7'),('fs-id2299604','5*(m+n)'),('fs-id1823388','5*m+n')]:
  table=lookup[ident].find('.//'+M+'mtable');last=norm(mathtext(table[-1][-1]));assert polynomial(last)==polynomial(wanted),(ident,last)
 quotient=lookup['fs-id1171105493688'];fraction=next(quotient.iter(M+'mfrac'))
 assert polynomial(norm(mathtext(fraction)))==polynomial('10*x/3')
 assert [e.text for e in lookup['fs-id2208916'].iter(M+'mi')]==['a','n','d']
 # Applications with worked source answers; verify preserved currency values.
 assert 2100-750==1350
 assert re.findall(r'\$\d+',flat(exs['fs-id2758209'].find(C+'solution')))==['$750','$1350']
 missing=[e.get('id')for e in source.iter(C+'exercise')if e.find(C+'solution')is None];assert len(missing)==39
 media=[]
 for e in source.iter(C+'media'):
  name=Path(list(e)[0].get('src')).name;file=MEDIA/name
  media.append({'media_id':e.get('id'),'source_file':name,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'inspection':'actual contact-sheet image'+('; original separately enlarged'if name in ENLARGED else''),'localization':'Gujarati text map supplied'if name in LABELS else'full self-check table supplied'if name==SELF_CHECK['image']else'retain source mathematical diagram; corrected alt and color notes apply where keyed'})
 receipt={'module':'m81270','source_sha256':SHA,'translation_sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),'integrity':stats,'source_text_tail_alt_slots':736,'other_language_attributes':14,'all_source_slots_accounted':750,'natural_English_residuals':0,'source_non_mtext_English_retained':'fs-id2208916containsEnglishandastheMathMLmi tokens a,n,d; readerbridge supplied; allsourcelettersunchanged','numeric_evaluation_exercises_checked':len(evaluated),'numeric_evaluation_parts_checked':sum(n for _,n in evaluated),'numeric_readiness_answers_checked':len(numeric),'polynomial_simplification_answers_checked':len(identities),'word_translation_answers_checked':word_parts,'numeric_image_paths_checked':sum(map(len,EVAL_SEQUENCES.values())),'numeric_image_steps_checked':image_steps,'symbolic_image_sequences_checked':len(POLY_SEQUENCES),'compact_like_term_groups_checked':likes,'worked_like_term_groups_checked':5,'coefficient_values_checked':15,'term_table_rows_checked':5,'terms_list_answers_checked':2,'MathML_tables_reviewed':7,'source_missing_solution_count':len(missing),'missing_source_solution_ids':missing,'media':media,'figure_label_translations':LABELS,'self_check':SELF_CHECK,'source_errata':ERRATA,'separate_reader_bridges':BRIDGES,'colored_figures_note':'Substitution valuesred5/1/10/5/10/4;020yvalue2cyan. Keepbase2blackandvariableexponentredafter substitution. In023redx²termsandcyanxterms, all joining operatorsincludingminusblack; onlytermscolored. Diagram015minusbelongswith2x. AppB008has4skillsand12blankresponses.','scope_note':'Complete canonical text/metadata/exercises/solutions/glossary/accessibility translation. All49actualimagesinspected,13enlarged. Sevenlanguage-bearingfiguresawaitrootintegration;42symbolic originalsretained. All39omitted-sourceanswersremainomittedinfaithfulXML. Editorialerrataandreaderbridgesareseparate.'}
 destination=ROOT/'gu-Gujr-IN/translations/a00-m81270-media-and-errata.gu.json';destination.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in receipt.items()if k not in ('missing_source_solution_ids','media','figure_label_translations','self_check','source_errata','separate_reader_bridges')},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
