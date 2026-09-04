"""Exact arithmetic, all supplied answers and actual-image inventory for m81272."""
import ast,hashlib,json,re,sys
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import xml.etree.ElementTree as E
from prepare_m81272 import ROOT,SOURCE,SHA,gather,ATTRIBUTES,VARIABLE_OWNERS
from a00_accessibility_attributes import validate_pair,LANGUAGE_ATTRS
C='{http://cnx.rice.edu/cnxml}';M='{http://www.w3.org/1998/Math/MathML}'
OUTPUT=ROOT/'gu-Gujr-IN/translations/a00-m81272.gu.cnxml'
MEDIA=ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'
flat=lambda e:' '.join(''.join(e.itertext()).split())
def ev(s,env=None):
 s=re.sub(r'(?<=\d),(?=\d{3}(?:\D|$))','',s).replace('−','-').replace('÷','/').replace('⋅','*').replace('·','*')
 s=re.sub(r'(?<=\d)(?=[a-z])','*',s);env=env or {}
 def go(n):
  if isinstance(n,ast.Expression):return go(n.body)
  if isinstance(n,ast.Constant)and type(n.value)in(int,float):return Fraction(str(n.value))
  if isinstance(n,ast.Name):return Fraction(env[n.id])
  if isinstance(n,ast.BinOp):
   a,b=go(n.left),go(n.right)
   if isinstance(n.op,ast.Add):return a+b
   if isinstance(n.op,ast.Sub):return a-b
   if isinstance(n.op,ast.Mult):return a*b
   if isinstance(n.op,ast.Div):return a/b
  raise ValueError(s)
 return go(ast.parse(s.strip(),mode='eval'))
def equals(s):
 a,b=s.rstrip('.,').split('=');assert ev(a)==ev(b),s
def nums(e):return [int((m.text or '').replace(',',''))for m in e.iter(M+'mn')if re.fullmatch(r'[\d,]+',m.text or '')]
def small_nums(e):return list(map(int,re.findall(r'\d+',flat(e))))
def factors(n):return [d for d in range(1,n+1)if n%d==0]
def prime(n):return n>1 and len(factors(n))==2
def rows(e):return [r.findall(C+'entry')for r in e.iter(C+'row')]
FIGURE_LABELS={
 'CNX_BMath_Figure_02_04_008_img.jpg':{'factors':'અવયવ','product':'ગુણનફળ','math':'8 · 9 = 72','scope':'આઠ અને નવની નીચેનો કૌંસ અવયવને દર્શાવે છે; બોતેરની નીચેનો કૌંસ ગુણનફળને દર્શાવે છે. મૂળ ગાણિતિક લખાણ કાળું અને નામ તથા કૌંસ તેજ આછા વાદળી છે.'},
 'CNX_BMath_Figure_02_04_009.jpg':{'headers':['ભાજ્ય','ભાજક','ભાગફળ','અવયવ'],'rows':[[72,1,72,'1, 72'],[72,2,36,'2, 36'],[72,3,24,'3, 24'],[72,4,18,'4, 18'],[72,5,'14.4','–'],[72,6,12,'6, 12'],[72,7,'~10.29','–'],[72,8,9,'8, 9']],'scope':'મૂળમાં નવ હરોળ, શીર્ષક સહિત; ભાજક નવની હરોળ નથી. અપૂર્ણ ભાગફળવાળી હરોળના અવયવના ખાનામાં આડી રેખા છે.'},
 'CNX_BMath_Figure_02_04_014_Errata.jpg':{'headers_left':['સંખ્યા','અવયવ','અવિભાજ્ય કે સંયુક્ત?'],'headers_right':['સંખ્યા','અવયવ','અવિભાજ્ય કે સંયુક્ત?'],'left_rows':[[n,', '.join(map(str,factors(n))),'અવિભાજ્ય'if prime(n)else'સંયુક્ત']for n in range(2,12)],'right_rows':[[n,', '.join(map(str,factors(n))),'અવિભાજ્ય'if prime(n)else'સંયુક્ત']for n in range(12,21)]+[['','','']],'highlighted_numbers':[2,3,5,7,11,13,17,19],'scope':'ત્રણ-ત્રણ સ્તંભનાં બે પેનલ, વચ્ચે પાતળી ખાલી પટ્ટી. શીર્ષક સાથે અગિયાર હરોળ. માત્ર અવિભાજ્ય સંખ્યાના નંબરવાળા ખાનામાં આછો રાખોડી-વાદળી રંગ છે; સંયુક્તના ખાના સફેદ. લાલ લખાણ નથી. પંદરના અવયવમાં બે નથી.'},
 'CNX_BMath_Figure_02_05_203_img.jpg':{'headers':['ભણતર પૂરું થયા પછીનાં અઠવાડિયાં','ફ્રૅન્કે ખાતામાં મૂકેલા કુલ ડૉલર','સરળ કરેલો સરવાળો'],'rows':[[0,'100','100'],[1,'100 + 15','115'],[2,'100 + 15 · 2','130'],[3,'100 + 15 · 3','145'],[4,'100 + 15 · 4','160'],[5,'100 + 15 · 5','175'],[6,'100 + 15 · 6','190'],[20,'100 + 15 · 20','400'],['x','100 + 15 · x','100 + 15x']],'scope':'ફ્રૅન્કનો સંપૂર્ણ ઉકેલ; શીર્ષક સહિત દસ હરોળ અને ત્રણ સ્તંભ. ખાલી ઉત્તરો નથી.'},
}
SELF_CHECK={'source_file':'CNX_BMath_Figure_AppB_011.jpg','headers':['હું કરી શકું છું…','આત્મવિશ્વાસથી','થોડી મદદથી','ના—મને સમજાતું નથી!'],'skills':['સંખ્યાઓના અવયવી ઓળખવા.','વિભાજ્યતાની સામાન્ય ચાવીઓ વાપરવી.','સંખ્યાના બધા અવયવ શોધવા.','અવિભાજ્ય અને સંયુક્ત સંખ્યાઓ ઓળખવી.'],'blank_response_cells':12,'answer_policy':'બધાં બાર જવાબનાં ખાના ખાલી રાખો.'}
ERRATA=[]
def err(key,ids,issue,correction,**kw):ERRATA.append({'key':key,'source_ids':ids,'issue':issue,'corrected_reader_text_gu':correction,**kw})
for ident,n in [('fs-id1949566',2),('fs-id1379128',5),('fs-id2320043',10),('fs-id1242400',3)]:
 correction=f'એકથી પચાસ સુધીની સંખ્યાઓનું પાંચ હરોળ અને દસ સ્તંભનું કોષ્ટક. સંખ્યા {n}ના અવયવી રંગથી દર્શાવેલા છે.'
 err('grid-'+ident,[ident],'English source alt calls highlighted multiples factors.',correction,corrected_alt_gu=correction)
err('multiples-table-aria',['fs-id1946698'],'Source aria column1 includes header1 as extra data; column3 includes header3 and omits21. Actual table is correct.','નવ હરોળ અને તેર સ્તંભનું કોષ્ટક. પહેલી હરોળમાં ગણતરીની સંખ્યાઓ એકથી બાર. પછીની આઠ હરોળમાં અનુક્રમે બે, ત્રણ, ચાર, પાંચ, છ, સાત, આઠ અને નવના પહેલા બાર અવયવી. દરેક ખાનું હરોળની સંખ્યા અને સ્તંભની ગણતરીની સંખ્યાનું ગુણનફળ છે.',corrected_aria_label_gu='ગણતરીની સંખ્યાઓ એકથી બાર સાથે બે થી નવના અવયવી દર્શાવતું કોષ્ટક. દરેક હરોળના બાર ગુણનફળ સાચા છે.',actual_rows=[[d]+[d*k for k in range(1,13)]for d in range(2,10)])
err('divisibility-table-aria',['fs-id2134771'],'Source aria says five rows and omits the6 divisibility test. Actual table has7rows including title/header.','શીર્ષક અને મથાળાની હરોળ સહિત સાત હરોળ. ચાવીઓ: બે માટે છેલ્લો અંક શૂન્ય, બે, ચાર, છ કે આઠ; ત્રણ માટે અંકોનો સરવાળો ત્રણ વડે વિભાજ્ય; પાંચ માટે છેલ્લો અંક પાંચ કે શૂન્ય; છ માટે બે અને ત્રણ બંને વડે વિભાજ્ય; દસ માટે છેલ્લો અંક શૂન્ય.',corrected_aria_label_gu='સાત હરોળનું વિભાજ્યતાની ચાવીઓનું કોષ્ટક; બે, ત્રણ, પાંચ, છ અને દસના નિયમો, શીર્ષક અને મથાળા સાથે.')
err('copied-division',['eip-id1168466267838','fs-id1596736','fs-id1862568'],'10,519 example contains copied645÷3. Indonesian witness corrects the expression; adjacent long-division3506R1 is correct.','આ ઉદાહરણમાં ભાગાકાર 10,519 ÷ 3 છે. ભાગફળ 3,506 અને શેષ 1. મૂળમાં અહીં અગાઉના ઉદાહરણનું 645 ÷ 3 રહી ગયું છે.',source_expression='645 ÷ 3',corrected_expression='10,519 ÷ 3')
err('factor72-image-alt',['fs-id3369689'],'Source alt claims10rows/divisor9; actual9rows inclheader/divisors1..8. Dashes are not empty cells.','ચિત્રમાં શીર્ષક સહિત નવ હરોળ અને ચાર સ્તંભ છે: ભાજ્ય, ભાજક, ભાગફળ અને અવયવ. ભાજ્ય બોતેર છે. ભાજક એકથી આઠ સુધી છે. ભાગફળ ગણતરીની સંખ્યા ન હોય ત્યારે અવયવના ખાનામાં આડી રેખા છે. નવના ભાજકવાળી હરોળ ચિત્રમાં નથી.',corrected_alt_gu='બોતેરના અવયવ શોધતું નવ હરોળનું કોષ્ટક, શીર્ષક સહિત; ભાજક એકથી આઠ સુધી. ભાજક નવની હરોળ ચિત્રમાં નથી.',actual_rows=FIGURE_LABELS['CNX_BMath_Figure_02_04_009.jpg']['rows'])
err('prime-image-alt',['fs-id1480189'],'Source alt claims20rows/3cols and red primes and adds factor2 for15. Actual two3colpanels,11rowsinclheader; prime number cells gray-teal, all math correct. Caption/prose correctly say primes highlighted.','ચિત્રમાં ત્રણ-ત્રણ સ્તંભનાં બે પેનલ છે. શીર્ષક સહિત અગિયાર હરોળ છે. બે થી અગિયાર ડાબે અને બારથી વીસ જમણે છે. માત્ર અવિભાજ્ય સંખ્યાના નંબરવાળા ખાના આછા રાખોડી-વાદળી છે; લાલ લખાણ નથી. પંદરના અવયવ એક, ત્રણ, પાંચ અને પંદર છે.',corrected_alt_gu='બે થી વીસની સંખ્યાઓ, તેમના અવયવ અને અવિભાજ્ય કે સંયુક્ત વર્ગ દર્શાવતું બે પેનલનું કોષ્ટક. અવિભાજ્ય સંખ્યાના નંબરવાળા ખાના આછા રાખોડી-વાદળી છે. પંદરના અવયવમાં બે નથી.')
err('composite-definition',['fs-id1824744','fs-id1227093'],'Definition omits greaterthan1, wrongly admitting1. Earlier paragraph correctly excludes1; Indonesian definition includes>1.','સંયુક્ત સંખ્યા એ એક કરતાં મોટી એવી ગણતરીની સંખ્યા છે જે અવિભાજ્ય ન હોય. તેના બે કરતાં વધુ ધન અવયવ હોય છે. એક અવિભાજ્ય પણ નથી અને સંયુક્ત પણ નથી.')
err('prime-procedure',['eip-id1168468773932','eip-id1170196371762'],'Unqualified primefactor=>composite ignores self-factor. Domain>1 and properfactor<n needed; test factor before stop for perfect squares.','એક કરતાં મોટી આપેલી સંખ્યા માટે, તેનાથી નાનો અવિભાજ્ય અવયવ મળે તો સંખ્યા સંયુક્ત છે. નાના અવિભાજ્ય ભાજકો ક્રમશઃ તપાસો. ભાજકનો વર્ગ સંખ્યા કરતાં મોટો થાય ત્યાં સુધી કોઈ એવો અવયવ ન મળે તો સંખ્યા અવિભાજ્ય છે. વર્ગ સમાન થાય ત્યારે તે ભાજકની તપાસ છોડશો નહીં.')
err('77-table-aria',['fs-id2371111'],'Source aria finalrow says77÷11=7 although actual prime-divisor7 test is77÷7=11.','છેલ્લી હરોળમાં ભાજક સાત છે: સિત્યોતેર ભાગ્યા સાત બરાબર અગિયાર. તેથી સાત અવયવ છે.',corrected_aria_label_gu='સિત્યોતેર માટે અવિભાજ્ય ભાજકો બે, ત્રણ, પાંચ અને સાતની ચકાસણી. પ્રથમ ત્રણ અવયવ નથી; સાત અવયવ છે, કારણ કે સિત્યોતેર ભાગ્યા સાત બરાબર અગિયાર.')
for ident in ('fs-id1783686','fs-id4201920'):
 err('bank-row-count-'+ident,[ident],'Source aria says9rows; actual10includingheader. Preserve exercise blanks.','કોષ્ટકમાં શીર્ષક સહિત દસ હરોળ અને ત્રણ સ્તંભ છે. મૂળ પ્રશ્નની ખાલી જગ્યાઓ ખાલી જ રાખો.')
err('Frank-solution-alt',['fs-id19495660'],'Source solution alt copied Gina75+20 and blanktable. Actual image is completed Frank100+15x.','આ ફ્રૅન્કનો પૂર્ણ કોષ્ટક છે: અઠવાડિયાં શૂન્ય, એક, બે, ત્રણ, ચાર, પાંચ, છ, વીસ અને x; કુલ ડૉલર અનુક્રમે સો, એકસો પંદર, એકસો ત્રીસ, એકસો પિસ્તાલીસ, એકસો સાઠ, એકસો પંચોતેર, એકસો નેવું, ચારસો અને 100 + 15x.',corrected_alt_gu='ફ્રૅન્કના ખાતામાં શરૂઆતમાં સો ડૉલર અને દર અઠવાડિયે પંદર ડૉલર ઉમેરાય છે. શીર્ષક સહિત દસ હરોળનું સંપૂર્ણ જવાબનું કોષ્ટક; x અઠવાડિયે કુલ 100 + 15x ડૉલર.',actual_rows=FIGURE_LABELS['CNX_BMath_Figure_02_05_203_img.jpg']['rows'])
err('multiples-list-punctuation',['fs-id2648898','fs-id1463032'],'Source answer lacks comma between10and12; numeric-only text preserved faithfully.','બેના અવયવીની યાદીમાં દસ અને બાર વચ્ચે અલ્પવિરામ હોવો જોઈએ.',source_text='10 12',corrected_text='10, 12')
BRIDGES=[{'source_id':'fs-id1393991','note_gu':'સામાન્ય બીજગણિતની વ્યાખ્યામાં પૂર્ણાંક અવયવ ઋણ પણ હોઈ શકે; આ વિભાગના અવયવની યાદીવાળા અભ્યાસમાં ધન અવયવ શોધવાના છે.'},{'source_id':'fs-id1932440','note_gu':'આ વિભાગમાં ગણતરીની સંખ્યા એકથી શરૂ થાય છે; તેથી અહીં આપેલી અવયવીની યાદીઓ ધન અવયવીની છે. પૂર્ણ સંખ્યાના ગુણાકારની વ્યાપક વ્યાખ્યામાં શૂન્ય અવયવી ગણાય છે, પણ મૂળ યાદીઓમાં તેને મૌન રીતે ઉમેર્યું નથી.'},{'source_id':'eip-id1168466680369','note_gu':'પુસ્તકનાં નામ મૂળની ઓળખ જાળવતા લિપ્યંતરિત છે: One Hundred Hungry Ants; Spunky Monkeys on Parade; A Remainder of One. મૂળ કડીઓ યથાવત્ છે.'}]

def main():
 sys.stdout.reconfigure(encoding='utf-8');assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
 source=E.parse(SOURCE).getroot();target=E.parse(OUTPUT).getroot();check=deepcopy(target)
 lang='{http://www.w3.org/XML/1998/namespace}lang'
 if source.get(lang)is None:check.attrib.pop(lang,None)
 else:check.set(lang,source.get(lang))
 stats=validate_pair(source,check)
 assert target.get('{http://www.w3.org/XML/1998/namespace}lang')=='gu-Gujr-IN'
 lookup={e.get('id'):e for e in target.iter()if e.get('id')};src={e.get('id'):e for e in source.iter()if e.get('id')}
 residual=[]
 for owner,slots in gather(target).items():
  for e,f,text in slots:
   for token in re.findall(r'[A-Za-z]+',text):
    if token not in ('a','b','m','n','x'):residual.append((owner,f,token))
 assert not residual,residual
 for e in target.iter():
  for a in LANGUAGE_ATTRS:
   assert not re.search(r'[A-Za-z]{2,}',e.get(a,'')),(e.get('id'),a)
 ex=list(source.iter(C+'exercise'));gu=list(target.iter(C+'exercise'));checked={}
 def mark(i,kind):assert ex[i].find(C+'solution')is not None;checked[i]=kind
 # Readiness questions, then all twelve pairs of divisibility answers.
 assert nums(ex[0].find(C+'problem'))==[0,4,215]
 assert nums(ex[0].find(C+'solution'))==[n for n in [0,4,215]if n>=1];mark(0,'readiness')
 assert nums(ex[1].find(C+'solution'))==[sum(nums(ex[1].find(C+'problem')))];mark(1,'readiness')
 boolean_parts=0
 for i in range(2,14):
  p=nums(ex[i].find(C+'problem'));assert len(p)==3,(i,p)
  d,a,b=p;expected=[a%d==0,b%d==0]
  got=[s.lower()=='yes'for s in re.findall(r'\b(?:yes|no)\b',flat(ex[i].find(C+'solution')),re.I)]
  got_gu=[s=='હા'for s in re.findall(r'(?<![\u0a80-\u0aff])(?:હા|ના)(?![\u0a80-\u0aff])',flat(gu[i].find(C+'solution')))]
  assert got==got_gu==expected,(i,got,got_gu,expected);boolean_parts+=2;mark(i,'multiple membership')
 # Given divisibility lists, including negative lists and displayed checks.
 for i,n in [(14,1290),(15,6240),(16,7248),(17,5625),(18,4962),(19,3765)]:
  assert n in nums(ex[i].find(C+'problem'))
  sol=ex[i].find(C+'solution');expected=[d for d in [2,3,5,10]if n%d==0]
  if i in (14,17):
   sol=list(sol.iter(C+'para'))[-1];parts=re.split(r'but not',flat(sol));s=re.sub(r'(?<=\d),(?=\d{3}(?:\D|$))','',parts[0]);actual=list(map(int,re.findall(r'\d+',s)))[1:]
  else:actual=list(map(int,re.findall(r'\d+',flat(sol).split(', not')[0])))
  assert actual==expected,(i,actual,expected);mark(i,'divisibility list')
 for i in range(36,54,2):
  n=nums(ex[i].find(C+'problem'))[0];expected=[d for d in [2,3,4,5,6,10]if n%d==0]
  assert small_nums(ex[i].find(C+'solution'))==expected;mark(i,'divisibility list')
 for i in [20,21,22,54,56,58,60]:
  n=nums(ex[i].find(C+'problem'))[0];sol=ex[i].find(C+'solution')
  if i==20:sol=list(sol.iter(C+'para'))[-1]
  assert small_nums(sol)==factors(n),(i,small_nums(sol),factors(n));mark(i,'complete factor list')
 for i in range(26,36,2):
  n=nums(ex[i].find(C+'problem'))[0]
  assert small_nums(ex[i].find(C+'solution'))==list(range(n,50,n));mark(i,'multiples below50')
 for i in [24,25,62,64,66,68,70,72]:
  n=nums(ex[i].find(C+'problem'))[0]
  assert flat(ex[i].find(C+'solution'))==('prime'if prime(n)else'composite')
  assert flat(gu[i].find(C+'solution'))==('અવિભાજ્ય'if prime(n)else'સંયુક્ત');mark(i,'prime or composite')
 assert nums(ex[23].find(C+'problem'))==[83,77]and prime(83)and not prime(77)
 assert '83 is prime' in flat(ex[23].find(C+'solution'))and 'It is composite' in flat(ex[23].find(C+'solution'));mark(23,'prime or composite')
 # Actual Frank answer image is independently transcribed above, not copied alt.
 assert small_nums(ex[74].find(C+'problem').find(C+'para'))==[100,15]
 for week,formula,total in FIGURE_LABELS['CNX_BMath_Figure_02_05_203_img.jpg']['rows']:
  for x in ([week]if type(week)is int else [0,1,7,21]):
   assert ev(formula,{'x':x})==ev(total,{'x':x})==100+15*x
 mark(74,'completed image bank table')
 supplied={i for i,e in enumerate(ex)if e.find(C+'solution')is not None};assert set(checked)==supplied and len(checked)==51
 # Ninety-six actual multiplication-table entries and eight dance arrangements.
 rr=rows(src['fs-id1946698']);assert len(rr)==9
 for d,row in enumerate(rr[1:],2):assert [int(flat(c))for c in row[1:]]==[d*k for k in range(1,13)]
 for row in rows(src['fs-id1406287'])[1:]:
  a,b=map(lambda c:int(flat(c)),row[:2]);assert a*b==24;equals(flat(row[2]))
 # All displayed divisibility checks, including exact finite decimals.
 for ident,n in [('fs-id1405269',1290),('fs-id1970659',5625)]:
  for row in rows(src[ident])[1:]:
   d=int(flat(row[0]));assert (flat(row[2])=='yes')==(n%d==0);equals(flat(row[3]))
 for ident,n in [('fs-id3335859',83),('fs-id2371111',77)]:
  for row in rows(src[ident])[1:]:
   d=int(flat(row[0]));assert (flat(row[2]).lower()=='yes.')==(n%d==0)
 assert Fraction(11857,1000)<Fraction(83,7)<Fraction(11858,1000)
 assert Fraction(7545,1000)<Fraction(83,11)<Fraction(7546,1000)
 # All8 MathML tables:12 product equations,5 digit-sum transformations,1division.
 tables=list(source.iter(M+'mtable'));assert len(tables)==8
 for t in tables[:2]:
  for row in t:equals(flat(row))
 for t in tables[2:7]:assert ev(flat(t[0]))==ev(flat(t[1]))
 assert nums(tables[7])==[3506,1,3,10519]and divmod(10519,3)==(3506,1)
 assert flat(tables[7].find('.//'+M+'mtext'))=='R'
 assert flat(list(target.iter(M+'mtable'))[7].find('.//'+M+'mtext'))=='શેષ'
 # Digit sums, source720factorimage, both bankproblem partialtables.
 for n,total in [(645,15),(10519,16),(1290,12),(5625,18),(83,11),(77,14)]:assert sum(map(int,str(n)))==total
 for n,d,q,fs in FIGURE_LABELS['CNX_BMath_Figure_02_04_009.jpg']['rows']:
  if str(q).startswith('~'):assert round(n/d,2)==float(str(q)[1:])
  else:assert Fraction(str(q))==Fraction(n,d)
  assert (fs!='–')==(n%d==0)
 for ident,start,amount in [('fs-id1783686',100,15),('fs-id4201920',75,20)]:
  rr=rows(src[ident]);assert len(rr)==10
  assert [flat(row[0])for row in rr[1:]]==['0','1','2','3','4','5','6','20','x']
  for week,row in enumerate(rr[1:5]):
   assert ev(flat(row[1]))==start+amount*week
   if week<3:assert ev(flat(row[2]))==start+amount*week
  assert sum(not flat(c)for row in rr[1:]for c in row)==9
  assert sum(flat(c).count('[]')for row in rr[1:]for c in row)==2
 # Source and translated rule tables retain6; keyconcepttable also retains4.
 for ident,wanted in [('fs-id2134771',[2,3,5,6,10]),('eip-839',[2,3,4,5,6,10])]:
  assert [int(flat(row[0]))for row in rows(src[ident])[2:]]==wanted
  assert [int(flat(row[0]))for row in rows(lookup[ident])[2:]]==wanted
 missing=[e.get('id')for e in ex if e.find(C+'solution')is None];assert len(missing)==27
 media=[]
 for e in source.iter(C+'media'):
  name=Path(list(e)[0].get('src')).name;p=MEDIA/name
  media.append({'media_id':e.get('id'),'source_file':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'inspection':'actual original image directly viewed during source preparation; five language images reopened during revision','localization':'Gujarati label/table map supplied'if name in FIGURE_LABELS else'complete Gujarati self-check supplied'if name==SELF_CHECK['source_file']else'retain math-only multiple grid; corrected alt supplied'})
 assert len(media)==9
 receipt={'module':'m81272','source_sha256':SHA,'translation_sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),'integrity':stats,'source_text_tail_alt_slots':575,'other_language_attributes':18,'total_language_slots':593,'natural_English_residuals':0,'all_supplied_solutions_checked':51,'solution_check_categories':{k:list(checked.values()).count(k)for k in sorted(set(checked.values()))},'multiple_membership_parts_checked':boolean_parts,'multiplication_table_products_checked':96,'dance_factor_arrangements_checked':8,'divisibility_quotient_rows_checked':8,'prime_divisor_rows_checked':9,'MathML_tables_checked':8,'source_missing_solution_count':27,'missing_source_solution_ids':missing,'source_exercises_checked':[{'id':ex[i].get('id'),'category':k}for i,k in sorted(checked.items())],'media':media,'figure_label_translations':FIGURE_LABELS,'self_check':SELF_CHECK,'source_errata':ERRATA,'separate_reader_bridges':BRIDGES,'scope_note':'Complete canonical full translation, all593language slots and51providedanswers checked. All9originalimagesread;5languagebearingfigure maps supplied;4mathgridsretained.27sourceomittedsolutionsstayomitted. Prime-image caption/prose are correct: primes are palegray-teal highlighted, not all numbers. Source errors stay in faithful CNXML and are keyed separately.'}
 out=ROOT/'gu-Gujr-IN/translations/a00-m81272-media-and-errata.gu.json';out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in receipt.items()if k not in ('media','source_errata','separate_reader_bridges','figure_label_translations','self_check','missing_source_solution_ids','source_exercises_checked')},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
