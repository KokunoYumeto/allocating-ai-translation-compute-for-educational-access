"""Independent exact QA for all supplied answers, chapter review and test included."""
import ast,hashlib,json,math,re,sys
from collections import Counter
from copy import deepcopy
import xml.etree.ElementTree as E
from prepare_m81273 import ROOT,SOURCE,SHA,gather,ATTRIBUTES
from a00_accessibility_attributes import validate_pair,LANGUAGE_ATTRS
from qa_m81270 import norm,evaluate,polynomial
from qa_m81271 import solve,holds,same_equation
C='{http://cnx.rice.edu/cnxml}';M='{http://www.w3.org/1998/Math/MathML}'
OUTPUT=ROOT/'gu-Gujr-IN/translations/a00-m81273.gu.cnxml'
MEDIA=ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'
flat=lambda e:' '.join(''.join(e.itertext()).split())

def written(e):
 if e.tag==C+'span'and e.get('class')=='token':return ''
 if e.tag==M+'msup':return '('+written(e[0])+')**('+written(e[1])+')'
 if e.tag==C+'sup':return '**('+''.join(e.itertext())+')'
 if e.tag==M+'mfrac':return '('+written(e[0])+')/('+written(e[1])+')'
 if e.tag==M+'mtext':
  s=(e.text or '').strip()
  if s in ('when','જ્યારે'):return '@'
  if s in ('and','અને'):return ','
  return s
 return (e.text or '')+''.join(written(c)+(c.tail or '')for c in e)
def maths(e):return [norm(written(m))for m in e.iter(M+'math')if m.find('.//'+M+'mtable')is None]
def compact(e):return norm(written(e))
def numbers(e):return [int(x)for x in re.findall(r'\d+',flat(e))]
def prime(n):return n>1 and all(n%d for d in range(2,math.isqrt(n)+1))
def factors(n):return [d for d in range(1,n+1)if n%d==0]
def prime_product(s,n):
 assert evaluate(s)==n,(s,n)
 def walk(a):
  if isinstance(a,ast.Expression):return walk(a.body)
  if isinstance(a,ast.Constant):assert type(a.value)is int and prime(a.value),(s,a.value);return [a.value]
  if isinstance(a,ast.BinOp)and isinstance(a.op,ast.Mult):return walk(a.left)+walk(a.right)
  if isinstance(a,ast.BinOp)and isinstance(a.op,ast.Pow):
   assert isinstance(a.right,ast.Constant)and type(a.right.value)is int and a.right.value>0
   return walk(a.left)*a.right.value
  raise AssertionError(s)
 return walk(ast.parse(s,mode='eval'))

# Each numeric input is transcribed from the full source problem and asserted
# against that problem. This avoids checking an answer against itself.
FACTORS={3:48,4:80,5:60,6:84,7:126,8:294,9:120,10:80,11:60,12:48,13:126,14:294,
24:86,26:132,28:693,30:115,32:2475,34:56,36:168,38:391,40:432,42:2160,44:150,46:525,48:36,50:350,182:84,184:350,218:1080}
LCMS={15:(15,20),16:(9,12),17:(18,24),18:(15,18),19:(15,20),20:(15,35),21:(50,100),22:(55,88),23:(60,72),52:(8,12),54:(6,15),56:(30,40),58:(60,75),60:(8,12),62:(24,30),64:(70,84),66:(6,21),68:(24,30),186:(9,15),188:(25,35)}
EVALUATE={94:('3**4',{}),96:('2**7',{}),98:('10+2*5',{}),100:('(30+6)/2',{}),102:('7**2+5**2',{}),104:('4+3*(10-1)',{}),106:('9*x-5',{'x':7}),108:('3*a-4*b',{'a':10,'b':1}),198:('(8+1)*4',{}),200:('(8+4)/3+1',{}),202:('5*(2+7*(9-8))',{}),204:('y**3',{'y':5}),206:('h*w',{'h':12,'w':3})}
SOLVES={140:'c+8=14',142:'23=x+12',144:'y-7=16',146:'19=p-15',158:'h-15=27',160:'z+52=85',162:'27=q+19',164:'31=v-25',212:'n-6=25'}
WORD_SOLVES={154:'x+8=35',156:'q-18=57',214:'y-15=32'}
WORD_EXPRESSIONS={124:'x-6',126:'3*n*9',128:'5*(y+1)',130:'c+3',208:'x+5',210:'3*(a-b)'}

SELF_CHECK={'source_file':'CNX_BMath_Figure_AppB_012.jpg','headers':['હું કરી શકું છું…','આત્મવિશ્વાસથી','થોડી મદદથી','ના—મને સમજાતું નથી!'],'skills':['સંયુક્ત સંખ્યાનું અવિભાજ્ય અવયવીકરણ શોધવું.','બે સંખ્યાઓનો લઘુત્તમ સામાન્ય અવયવી (LCM) શોધવો.'],'blank_response_cells':6,'answer_policy':'બધાં છ જવાબનાં ખાના ખાલી રાખો.'}
FIGURES={
 'CNX_BMath_Figure_02_05_006_img.jpg':{'labels':{'LCM':'લઘુત્તમ સામાન્ય અવયવી (LCM)'},'numbers':[12,18],'aligned_factors':[[2,2,3,None],[2,None,3,3]],'merged':[2,2,3,3],'final_value':36,'accessible_gu':'બારના અવયવ બે, બે, ત્રણ અને અઢારના અવયવ બે, ત્રણ, ત્રણ છે. ચાર સ્તંભમાં ગોઠવણી: બંનેનો પહેલો બે; માત્ર બારનો બીજો બે; બંનેનો પહેલો ત્રણ; માત્ર અઢારનો બીજો ત્રણ. દરેક સ્તંભથી એક અવયવ નીચે ઉતારતાં લઘુત્તમ સામાન્ય અવયવી બે ગુણ્યા બે ગુણ્યા ત્રણ ગુણ્યા ત્રણ બરાબર છત્રીસ. મૂળમાં અંતિમ છત્રીસની અલગ લીટી પણ છે.'},
 'CNX_BMath_Figure_02_05_026_img-03.png':{'labels':{'LCM':'લઘુત્તમ સામાન્ય અવયવી (LCM)'},'numbers':[15,18],'aligned_factors':[[None,3,None,5],[2,3,3,None]],'merged':[2,3,3,5],'final_value':90,'accessible_gu':'પંદરના અવયવ ત્રણ અને પાંચ; અઢારના અવયવ બે, ત્રણ અને ત્રણ. ચાર સ્તંભ: માત્ર અઢારનો બે, બંનેનો પહેલો ત્રણ, માત્ર અઢારનો બીજો ત્રણ, માત્ર પંદરનો પાંચ. દરેક સ્તંભથી એક અવયવ લેતાં લઘુત્તમ સામાન્ય અવયવી બે ગુણ્યા ત્રણ ગુણ્યા ત્રણ ગુણ્યા પાંચ બરાબર નેવું.'},
 'CNX_BMath_Figure_02_05_027_img-03.png':{'labels':{'LCM':'લઘુત્તમ સામાન્ય અવયવી (LCM)'},'numbers':[50,100],'aligned_factors':[[None,2,5,5],[2,2,5,5]],'merged':[2,2,5,5],'final_value':100,'accessible_gu':'પચાસના અવયવ બે, પાંચ અને પાંચ; સોના અવયવ બે, બે, પાંચ અને પાંચ. ચાર સ્તંભ: માત્ર સોનો પહેલો બે, બંનેનો ગોઠવેલો બે, બંનેનો પહેલો પાંચ, બંનેનો બીજો પાંચ. દરેક સ્તંભથી એક અવયવ લેતાં લઘુત્તમ સામાન્ય અવયવી બે ગુણ્યા બે ગુણ્યા પાંચ ગુણ્યા પાંચ બરાબર સો.'},
}
ERRATA=[]
def err(key,ids,issue,gu,**kw):ERRATA.append({'key':key,'source_ids':ids,'issue':issue,'corrected_reader_text_gu':gu,**kw})
err('first-tree-circle',['fs-id2777835'],'018 first tree alt claims circle around3, absent in actual image. Right edge of3 is clipped. The following paragraph introduces the circle.','છત્રીસમાંથી ડાબે બાર અને જમણે ત્રણની શાખા છે. આ પહેલા ચિત્રમાં ત્રણની આસપાસ વર્તુળ નથી; જમણી ધાર થોડે કપાયેલી દેખાય છે.',corrected_alt_gu='છત્રીસમાંથી ડાબે બાર અને જમણે ત્રણની શાખા. આ પહેલા તબક્કામાં ત્રણની આસપાસ વર્તુળ નથી.')
err('48-ladder-aria',['eip-id1168469467686'],'Copied30 in six-above-thirty phrase; actual025 stage has6 above12. All actual divisions correct.','બારને બે વડે ભાગતાં ભાગફળ છ મળે છે; છ બારની ઉપર ભાગાકારના કૌંસની બહાર છે.',corrected_aria_label_gu='અડતાલીસની નિસરણી: અડતાલીસ ભાગ્યા બે બરાબર ચોવીસ; ચોવીસ ભાગ્યા બે બરાબર બાર; બાર ભાગ્યા બે બરાબર છ; છ ભાગ્યા બે બરાબર ત્રણ. દરેક ભાગફળ અગાઉના ભાજ્યની ઉપર લખેલું છે. બાજુના ચાર બે અને ટોચનો ત્રણ ગુણતાં અડતાલીસ મળે છે.')
err('48-quotient-position',['eip-id1168466807907'],'Source025-01alt says quotient above divisor; image is above bar/dividend.','અડતાલીસ ભાગ્યા બે બરાબર ચોવીસ. ભાજક બે ડાબે કૌંસની બહાર છે; ભાગફળ ચોવીસ ભાજ્ય અડતાલીસની ઉપર આડી રેખાની બહાર છે.',corrected_alt_gu='અડતાલીસ ભાગ્યા બે બરાબર ચોવીસ. ભાગફળ ચોવીસ ભાજ્યની ઉપર આડી રેખાની બહાર છે, ભાજકની ઉપર નહીં.')
for ident,left,right in [('fs-id2704082',3,5),('fs-id2758794',4,9)]:
 gu=f'ડાબે વાદળી પરબીડિયું અને {left} ગોળી; જમણે {right} ગોળી. ગોળીઓ આછા પીળા રંગની અને આછા લીલા કિનારાવાળી છે.'
 err('model-color-'+ident,[ident],'Source alt calls counters blue; actual counters pale yellow with lime outlines, envelope cyan.',gu,corrected_alt_gu=gu)
err('LCM36-final-line',['fs-id1733229'],'Source alt omits final separate LCM=36 line, visible in image.',FIGURES['CNX_BMath_Figure_02_05_006_img.jpg']['accessible_gu'],corrected_alt_gu=FIGURES['CNX_BMath_Figure_02_05_006_img.jpg']['accessible_gu'])
err('ladder-prime-factor',['eip-id1168468309839','eip-id1170195278197'],'Procedure says smallest prime rather than smallest prime factor. It fails odd composites if interpreted as always divide by2. Explanatory fs-id1040789 does say prime factor.','હાલની સંખ્યા કે ભાગફળના સૌથી નાના અવિભાજ્ય અવયવ વડે ભાગો. જે અવિભાજ્ય સંખ્યા વડે નિઃશેષ ન ભાગી શકાય તેને છોડીને આગળ વધો. ભાગફળ અવિભાજ્ય થાય ત્યાં સુધી ચાલુ રાખો.')
err('practice-expression-label',['fs-id1762517'],'Practice test calls6·4 and15−x equations though they are expressions.','નીચેના અભ્યાસમાં દરેક બીજગણિતીય પદાવલીને શબ્દોમાં લખો.')
BRIDGES=[
 {'source_ids':['fs-id2168577','fs-id1215798','eip-id1168469875559','eip-id1170195278180'],'note_gu':'અવયવવૃક્ષ માટે એક કરતાં મોટા બે ધન અવયવ પસંદ કરો. એક ગુણ્યા એ જ સંખ્યાની જોડી લેવાથી પ્રક્રિયા આગળ વધતી નથી અને એક અવિભાજ્ય પણ નથી.'},
 {'source_ids':['fs-id1223478','fs-id4120770'],'note_gu':'આ વિભાગની ગણતરીની સંખ્યાઓ એકથી શરૂ થાય છે; તેથી લઘુત્તમ સામાન્ય અવયવી અહીં સૌથી નાનો ધન સામાન્ય અવયવી છે. શૂન્યને આ યાદીઓમાં ઉમેરશો નહીં.'},
 {'source_ids':['fs-id2692103'],'note_gu':'અવિભાજ્ય અવયવીકરણમાં ગુણાકારના અવયવોનો ક્રમ બદલાય તો પણ એ જ અવયવીકરણ ગણાય છે. વારંવાર આવતો અવયવ જેટલી વાર આવે તેટલી વાર જાળવો.'},
 {'source_ids':['fs-id1733229','eip-id1168467200222','eip-id1168466277374'],'note_gu':'સમાન અવિભાજ્ય અવયવને એક વાર લેવાનો અર્થ દરેક મેળ ખાતા સ્તંભમાંથી એક વાર છે. જુદા સ્તંભમાં ફરી આવતો બે, ત્રણ કે પાંચ કાઢી નાખવો નહીં.'},
 {'source_ids':['fs-id2202169'],'note_gu':'જવાબ ચાળીસ હૉટ ડૉગ અને ચાળીસ બન છે: બંને વસ્તુની સંખ્યા સરખી રાખવાની છે. કુલ મળીને ચાળીસ વસ્તુ નથી.'},
]

def main():
 sys.stdout.reconfigure(encoding='utf-8');assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
 source=E.parse(SOURCE).getroot();target=E.parse(OUTPUT).getroot();check=deepcopy(target)
 lang='{http://www.w3.org/XML/1998/namespace}lang'
 if source.get(lang)is None:check.attrib.pop(lang,None)
 else:check.set(lang,source.get(lang))
 stats=validate_pair(source,check);assert target.get(lang)=='gu-Gujr-IN'
 residual=[]
 for owner,slots in gather(target).items():
  for e,f,t in slots:
   for token in re.findall('[A-Za-z]+',t):
    if token not in ('LCM','a','b','c','h','m','n','p','q','r','u','v','w','x','y','z'):residual.append((owner,f,token))
 for e in target.iter():
  for attr in LANGUAGE_ATTRS:
   for token in re.findall('[A-Za-z]{2,}',e.get(attr,'')):
    if token!='LCM':residual.append((e.get('id'),attr,token))
 assert not residual,residual
 ex=list(source.iter(C+'exercise'));gu=list(target.iter(C+'exercise'));checked={}
 def p(i,t=ex):return t[i].find(C+'problem')
 def s(i,t=ex):return t[i].find(C+'solution')
 def mark(i,kind):assert s(i)is not None and i not in checked;(checked.__setitem__(i,kind))
 assert numbers(p(0))[:1]==[810] and numbers(s(0))==[d for d in [2,3,5,6,10]if 810%d==0];mark(0,'readiness divisibility')
 for i,n in [(1,127),(178,19),(180,121)]:
  assert numbers(p(i))[0]==n
  assert flat(s(i))==('prime'if prime(n)else'composite')
  assert flat(s(i,gu))==('અવિભાજ્ય'if prime(n)else'સંયુક્ત');mark(i,'prime classification')
 for i in [2,86,88,90,92]:
  assert polynomial(maths(p(i))[0])==polynomial(compact(s(i)))==polynomial(compact(s(i,gu)));mark(i,'exponent product equivalence')
 factor_forms=0
 for i,n in FACTORS.items():
  assert n in numbers(p(i)),(i,n,numbers(p(i)))
  for t in (ex,gu):
   if i in (3,6,9,12):forms=[q for q in maths(s(i,t))if '*'in q]
   else:forms=[norm(q)for q in re.split(r',\s*(?:or|અથવા)\s*',written(s(i,t)).strip())]
   assert forms,(i,forms)
   for q in forms:prime_product(q,n)
   if t is ex:factor_forms+=len(forms)
  mark(i,'complete prime factorization')
 for i,(a,b)in LCMS.items():
  assert numbers(p(i))==[a,b],(i,numbers(p(i)),a,b)
  if i==15:
   assert '60 is the least common multiple of 15 and 20' in flat(s(i))
   assert '60' in flat(s(i,gu))
  elif i in (18,21):
   forms=[q for q in maths(s(i))if '='in q]
   assert evaluate(forms[-1].split('=')[1])==math.lcm(a,b)
   assert numbers(list(s(i).iter(C+'entry'))[-1])[-1]==math.lcm(a,b)
  else:assert numbers(s(i))==numbers(s(i,gu))==[math.lcm(a,b)]
  mark(i,'least positive common multiple')
 assert 'packages of ten' in flat(p(70))and 'packs of eight' in flat(p(70));assert numbers(s(70))==[math.lcm(10,8)];mark(70,'equal purchase quantities')
 for i,(expr,env)in EVALUATE.items():
  raw=maths(p(i))[0];parts=raw.split('@');assert polynomial(parts[0])==polynomial(expr),(i,raw,expr)
  if env:
   actual={k:int(v)for k,v in (pair.split('=')for pair in parts[1].split(','))};assert actual==env
  assert evaluate(compact(s(i)))==evaluate(expr,env)==evaluate(compact(s(i,gu)));mark(i,'exact expression evaluation')
 for i in [116,118,120,122]:
  assert polynomial(maths(p(i))[0])==polynomial(compact(s(i)))==polynomial(compact(s(i,gu)));mark(i,'collect like terms')
 for i,expr in WORD_EXPRESSIONS.items():
  assert polynomial(compact(s(i)))==polynomial(expr)==polynomial(compact(s(i,gu)));mark(i,'word phrase scope independently read')
 assert polynomial(maths(p(110))[0])==polynomial('+'.join(compact(s(110)).split(',')));assert compact(s(110))==compact(s(110,gu));mark(110,'term decomposition')
 assert polynomial(maths(p(112))[0])=={('y',):6}and numbers(s(112))==[6];mark(112,'coefficient')
 like=[polynomial(q)for q in maths(p(114))[0].split(',')];groups={}
 for j,poly in enumerate(like):
  assert len(poly)==1;groups.setdefault(next(iter(poly)),[]).append(j)
 assert [v for v in groups.values()if len(v)>1]==[[1,5],[3,4]]
 assert flat(s(114))=='3 and 4; 3x and x'and flat(s(114,gu))=='3 અને 4; 3x અને x';mark(114,'all like-term groups')
 for i,eq,candidates in [(132,'y+16=40',[24,56]),(134,'4*n+12=36',[6,12]),(136,'15*x-5=10*x+45',[2,10])]:
  same_equation(maths(p(i))[0],eq);variable=solve(eq)[0];want=[holds(eq,{variable:n})for n in candidates]
  assert [int(q)for q in maths(p(i))[1:]]==candidates
  assert [q=='yes'for q in re.findall(r'yes|no',flat(s(i)))]==want
  assert [q=='હા'for q in re.findall(r'હા|ના',flat(s(i,gu)))]==want;mark(i,'candidate substitution')
 for i,eq in SOLVES.items():
  same_equation(maths(p(i))[0],eq);answer=compact(s(i));variable,value=solve(eq)
  assert answer.split('=')[0]==variable and evaluate(answer.split('=')[1])==value and compact(s(i,gu))==answer;mark(i,'linear equation solution')
 for i,eq in WORD_SOLVES.items():
  a,b=compact(s(i)).split(';');same_equation(a,eq);variable,value=solve(eq)
  assert b.split('=')[0]==variable and evaluate(b.split('=')[1])==value and compact(s(i,gu))==compact(s(i));mark(i,'word equation and solution')
 for i,eq in [(148,'7+33=40'),(150,'4*8=32'),(152,'2*(n-3)=76')]:
  same_equation(compact(s(i)),eq);same_equation(compact(s(i,gu)),eq)
  if i!=152:assert holds(eq)
  mark(i,'word equation translation')
 same_equation(compact(s(138)).split(';')[0],'x+3=5');assert compact(s(138)).split(';')[1]=='x=2'and compact(s(138,gu))==compact(s(138));mark(138,'actual envelope model3to5')
 for i,n in [(166,3),(168,8),(216,4)]:
  assert numbers(p(i))[0]==n and numbers(s(i))==numbers(s(i,gu))==list(range(n,50,n));mark(i,'all positive multiples below50')
 for i,n in [(170,96),(172,420)]:
  assert numbers(p(i))==[n]and numbers(s(i))==[d for d in [2,3,5,6,10]if n%d==0];mark(i,'only requested divisibility tests')
 for i,n in [(174,30),(176,180)]:
  assert numbers(p(i))==[n]and numbers(s(i))==numbers(s(i,gu))==factors(n);mark(i,'all positive factors')
 for i in (82,84,194):
  iseq='='in maths(p(i))[0];assert flat(s(i))==('equation'if iseq else'expression')and flat(s(i,gu))==('સમીકરણ'if iseq else'પદાવલી');mark(i,'expression versus equation')
 for i,expr,words in [(74,'3*8',['ગુણનફળ']), (76,'24/6',['ભાગફળ']),(78,'50≥47',['મોટું','બરાબર']),(80,'n+4=13',['સરવાળો','બરાબર']),(192,'15-x',['તફાવત'])]:
  assert maths(p(i))[0]==expr and all(w in flat(s(i,gu))for w in words);mark(i,'source and Gujarati verbal reading')
 assert flat(s(190))=='Answers will vary'and flat(s(190,gu))=='જવાબો જુદા જુદા હોઈ શકે';mark(190,'open reflection no unique answer')
 parts=s(196).findall(C+'para');assert len(parts)==1
 sourceparts=[compact(e)for e in s(196).iter(C+'item')];guparts=[compact(e)for e in s(196,gu).iter(C+'item')]
 assert polynomial(sourceparts[0])==polynomial('n**6')==polynomial(guparts[0])
 a,b=sourceparts[1].split('=');assert evaluate(a)==evaluate(b)==3**5 and guparts[1]==sourceparts[1];mark(196,'two exponent and expansion parts')
 supplied={i for i,e in enumerate(ex)if e.find(C+'solution')is not None}
 assert set(checked)==supplied,(sorted(supplied-set(checked)),sorted(set(checked)-supplied));assert len(checked)==121
 tables=list(source.iter(M+'mtable'));assert len(tables)==5
 for t in tables[:2]:
  vals=[norm(written(c))for c in t.iter(M+'mtd')];assert vals[1]==''
  for v in (vals[0],vals[2]):prime_product(v,36)
 for ti,bases,lengths in [(2,[10,25],[11,5]),(3,[15,20],[8,8])]:
  for row,d,k in zip(tables[ti].findall(M+'mtr'),bases,lengths):
   nums=[int(x)for x in re.findall(r'\d+',written(row))];assert nums.pop(0)==d
   assert nums==[d*j for j in range(1,k+1)],(ti,d,nums)
 for row in tables[4].findall(M+'mtr'):
  a,b=norm(written(row)).split('=');prime_product(b,int(a))
 for branches in [[(36,12,3),(12,3,4),(4,2,2)],[(48,2,24),(24,4,6),(4,2,2),(6,2,3)],[(84,4,21),(4,2,2),(21,3,7)]]:
  for n,a,b in branches:assert a*b==n
 for n,divs in [(36,[2,2,3]),(120,[2,2,2,3]),(48,[2,2,2,2])]:
  original=n
  for d in divs:assert prime(d)and n%d==0;n//=d
  assert prime(n)and math.prod(divs+[n])==original
 for data in FIGURES.values():
  a,b=data['numbers'];r1,r2=data['aligned_factors'];merged=[]
  assert math.prod(x for x in r1 if x)==a and math.prod(x for x in r2 if x)==b
  for x,y in zip(r1,r2):assert x is None or y is None or x==y;merged.append(x or y)
  assert merged==data['merged']and math.prod(merged)==data['final_value']==math.lcm(a,b)
 med=[]
 for e in source.iter(C+'media'):
  name=e.find(C+'image').get('src').rsplit('/',1)[-1];path=MEDIA/name;assert path.is_file()
  med.append({'source_id':e.get('id'),'file':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'visually_read':True,'language_bearing':name in FIGURES or name==SELF_CHECK['source_file']})
 assert len(med)==26 and sum(x['language_bearing']for x in med)==4
 missing=[{'source_index':i,'exercise_id':e.get('id'),'problem_id':e.find(C+'problem').get('id')}for i,e in enumerate(ex)if e.find(C+'solution')is None]
 assert len(missing)==99
 ids={e.get('id')for e in source.iter()if e.get('id')}
 for entry in ERRATA+BRIDGES:assert all(i in ids for i in entry['source_ids']),entry
 receipt={'module':'m81273','source_sha256':SHA,'translation_sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),'integrity':stats,'language_slots':514+len(ATTRIBUTES),'natural_language_English_residuals':residual,'allowed_Latin':'Original mathematical variables and defined LCM abbreviation; identifiers/URLs unchanged.','provided_answers_checked':len(checked),'answer_categories':dict(Counter(checked.values())),'prime_factor_forms_checked':factor_forms,'math_tables_checked':5,'source_omitted_solutions':missing,'checked_answers':[{'source_index':i,'exercise_id':ex[i].get('id'),'check':checked[i]}for i in sorted(checked)],'media':med,'localized_figure_content':FIGURES,'self_check':SELF_CHECK,'source_errata':ERRATA,'reader_bridges':BRIDGES,'status':'Complete translator source workflow; reader figure localization and educator review are separate root integration work.'}
 out=ROOT/'gu-Gujr-IN/translations/a00-m81273-media-and-errata.gu.json';out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'result':'pass',**stats,'language_slots':receipt['language_slots'],'provided_answers_checked':len(checked),'prime_factor_forms':factor_forms,'omitted_solutions':len(missing),'media':len(med),'language_figures':4,'errata':len(ERRATA),'bridges':len(BRIDGES),'sha256':receipt['translation_sha256']},indent=2))
if __name__=='__main__':main()
