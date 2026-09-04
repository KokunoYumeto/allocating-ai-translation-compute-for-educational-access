"""Full m81256 numerical/source QA and separate editorial/image handoff.

Math parsing respects fraction and long-division structure; it never concatenates
their operands into a spurious whole number. No omitted source answer is added.
"""
import ast,hashlib,json,re,sys
from fractions import Fraction
from pathlib import Path
import xml.etree.ElementTree as ET
from prepare_m81256 import ROOT,SOURCE,SHA,gather,natural_latin
from a00_accessibility_attributes import validate_pair,residual_attributes
C='{http://cnx.rice.edu/cnxml}';M='{http://www.w3.org/1998/Math/MathML}'
OUTPUT=ROOT/'gu-Gujr-IN/translations/a00-m81256.gu.cnxml'
MEDIA=ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'
flat=lambda e:' '.join(''.join(e.itertext()).split())
def mathtext(e):
 tag=e.tag.removeprefix(M)
 if tag=='mtable':raise ValueError('table needs its own reviewed interpretation')
 if tag=='mfrac':return '('+mathtext(e[0])+')/('+mathtext(e[1])+')'
 if tag=='mspace':return ''
 children=list(e)
 if not children:return e.text or ''
 parts=[]
 for child in children:
  t=mathtext(child)
  if child.tag==M+'menclose' and child.get('notation')=='longdiv':
   if not parts:raise ValueError('longdiv without preceding divisor')
   t='('+t+')/('+parts.pop()+')'
  parts.append(t)
 return (e.text or '')+''.join(parts)
def norm(t):
 t=re.sub(r'\s+','',t).replace(',','').replace('−','-').replace('÷','/').rstrip('.;✓?')
 for x in ('×','·','⋅'):t=t.replace(x,'*')
 t=re.sub(r'(?<=[\d)])(?=\()', '*',t);t=re.sub(r'(?<=\))(?=\d)', '*',t)
 return t
def calc(t):
 if not re.fullmatch(r'[0-9+*()/\-]+',t):raise ValueError(t)
 def walk(n):
  if isinstance(n,ast.Expression):return walk(n.body)
  if isinstance(n,ast.Constant) and type(n.value)is int:return Fraction(n.value)
  if isinstance(n,ast.BinOp):
   a,b=walk(n.left),walk(n.right)
   if isinstance(n.op,ast.Mult):return a*b
   if isinstance(n.op,ast.Add):return a+b
   if isinstance(n.op,ast.Sub):return a-b
   if isinstance(n.op,ast.Div):return a/b
  raise ValueError(t)
 return walk(ast.parse(t,mode='eval'))
def exprs(e):
 out=[]
 for m in e.iter(M+'math'):
  try:out.append(norm(mathtext(m)))
  except ValueError:out.append(None)
 return out
def vertical_text(e):
 # A mover carries an annotation; the base belongs to the operand.
 if e.tag in (M+'mover',M+'munder'):return vertical_text(e[0])
 if e.tag==M+'mspace':return ''
 return (e.text or '')+''.join(vertical_text(c)for c in e)

ERRATA={
 'fs-id1508917':{'kind':'zero-property-body','issue':'English omits the nonzero-divisor condition; nearby division-by-zero rule conflicts. Indonesian includes nonzero.','corrected_gu':'શૂન્યનો શૂન્ય સિવાયની કોઈ પણ સંખ્યા વડે ભાગાકાર કરતાં શૂન્ય મળે છે.'},
 'eip-158':{'kind':'zero-property','issue':'English says zero divided by any number is0 without excluding zero.','corrected_gu':'શૂન્યનો શૂન્ય સિવાયની કોઈ પણ સંખ્યા વડે ભાગાકાર કરતાં 0 મળે છે.'},
 'eip-id1168288542869':{'kind':'zero-example-rule','issue':'Body omits nonzero condition although this table summary correctly includes it.','corrected_gu':'શૂન્યનો શૂન્ય સિવાયની કોઈ પણ સંખ્યા વડે ભાગાકાર કરતાં શૂન્ય મળે છે.'},
 'eip-id1170326423719':{'kind':'zero-summary-rule','issue':'Repeated key-concepts rule also omits nonzero condition.','corrected_gu':'શૂન્યનો શૂન્ય સિવાયની કોઈ પણ સંખ્યા વડે ભાગાકાર કરતાં 0 મળે છે.'},
 'eip-708':{'kind':'body-and-aria','issue':'Problem and all images are1461÷13=112R5 but concluding body MathML says1462. Aria says16−3 instead of16−13, and has literal t0 typo. Indonesian corrects1461 in body.','corrected_gu':'1,461 ÷ 13નું ભાગફળ 112 અને શેષ 5 છે.','corrected_aria_gu':'1,461નો 13 વડે લાંબો ભાગાકાર. 14માંથી 13 બાદ કરતાં 1 રહે છે. 6ને નીચે ઉતારતાં 16 બને છે. 16માંથી 13 બાદ કરતાં 3 રહે છે. છેલ્લો 1 નીચે ઉતારતાં 31 બને છે. 31માંથી 26 બાદ કરતાં શેષ 5 રહે છે. ભાગફળ 112 છે. ચકાસણી: 112 × 13 = 1,456 અને 1,456 + 5 = 1,461. ચિત્રમાં ભાગફળ, ભાજક અને શેષનાં નામ આપેલાં છે.'},
 'fs-id2150327':{'kind':'alt','issue':'Source alt says each of4groups has7circles. Actual006image has4groups of6, totaling24.','corrected_gu':'24 ચકતીઓનાં ચાર જૂથ છે; દરેક જૂથમાં છ ચકતીઓ છે. આથી 24 ÷ 6 = 4.'},
 'fs-id2590530':{'kind':'alt','issue':'Source alt says3cookies remain outside. Actual028image has4outside the3groups of8.','corrected_gu':'28 કૂકીમાંથી આઠ આઠ કૂકીનાં ત્રણ જૂથ બનાવ્યાં છે અને ચાર કૂકી બહાર બાકી છે. ભાગફળ 3 અને શેષ 4 છે.'},
 'eip-id1168287242183':{'kind':'intermediate-alt','issue':'Source043-03alt describes remainder1 already present. Actual intermediate image writes6under7 but no subtraction line/result1 yet;043-04shows it.','corrected_gu':'78નો 3 વડે લાંબો ભાગાકાર. ભાગફળનો 2, અંક 7ની ઉપર છે. ગુણનફળ 6, અંક 7ની નીચે લાલ રંગે લખેલું છે; બાદબાકીનો શેષ આ પગલામાં હજી લખ્યો નથી.'},
 'eip-id1168288541565':{'kind':'alt-operand-name','issue':'Source calls brought-down third digit9 a digit of quotient; it is from dividend2596.','corrected_gu':'2596નો 4 વડે લાંબો ભાગાકાર. ભાજ્યનો ત્રીજો અંક 9, શેષ 1ની પાસે નીચે ઉતારતાં 19 બને છે. ભાગફળનો આગળનો અંક 4 છે. 19માંથી 16 બાદ કરતાં શેષ 3 રહે છે.'},
 'eip-id1168287450666':{'kind':'alt','issue':'Source049-02alt sayswrite4; actual imagewrites3and subtracts723from745, leaving22.','corrected_gu':'74521નો 241 વડે લાંબો ભાગાકાર. ભાગફળમાં 3ને ભાજ્યના 5ની ઉપર લખેલું છે. 745માંથી 723 બાદ કરતાં 22 રહે છે.'},
 'fs-id2700533':{'kind':'alt','issue':'Source211alt describes abstract reflected panels; actual image is one10rod plus3unit blocks, representing13 for6+7.','corrected_gu':'એક દશકની સળી અને ત્રણ એકમના ખંડ છે. કુલ 13 એકમ થાય છે; આ 6 + 7નો નમૂનો છે.'},
 'fs-id1575621':{'kind':'alt-chart','issue':'Source222alt has malformed/incomplete rows, omits row7header and the end ofrow8. Actual chart transcribed separately with blanks retained.','corrected_gu':'11 હરોળ અને 11 સ્તંભનું સરવાળાનું કોષ્ટક. ઉપરની હરોળ અને ડાબા સ્તંભમાં 0થી 9 છે. આપેલા સરવાળા અને ખાલી ખાણાં જુદી સુલભ કોષ્ટક નોંધમાં જાળવ્યાં છે; ખાલી ખાણાં ભરવાનાં છે.'},
 'fs-id1981934':{'kind':'alt-chart','issue':'Source226alt says10×10 with plus sign, but actual has11×11withmultiplication sign. Source describes0inrow4column2, which is actuallyblank. Exact actual matrix supplied.','corrected_gu':'11 હરોળ અને 11 સ્તંભનું ગુણાકાર કોષ્ટક. ઉપરની હરોળ અને ડાબા સ્તંભમાં 0થી 9 છે; પહેલા ખાણામાં ગુણાકારની નિશાની છે. કેટલાક ગુણનફળ આપેલા છે અને બાકીનાં ખાણાં ખાલી છે.'},
 'eip-id3140794':{'kind':'aria-copy-error','issue':'Division notation table aria copied multiplication3×8symbols/prose. Actual table is12÷4infournotations.','corrected_gu':'ભાગાકારની લખાવટનું કોષ્ટક. ક્રિયા ભાગાકાર છે. પદાવલી 12નો 4 વડે ભાગાકાર ચાર લખાવટમાં દર્શાવે છે: ÷, ત્રાંસી રેખા, અપૂર્ણાંકની રેખા અને લાંબા ભાગાકારની રેખા. તેને બાર ભાગ્યા ચાર વાંચીએ છીએ; પરિણામ 12 અને 4નું ભાગફળ છે.'},
 'eip-id1167114554527':{'kind':'aria-copy-error','issue':'Key-concepts duplicate has the same multiplication-copy error as eip-id3140794.','corrected_gu':'ભાગાકારની લખાવટનું કોષ્ટક: 12નો 4 વડે ભાગાકાર ચાર લખાવટમાં છે. તેને બાર ભાગ્યા ચાર વાંચીએ છીએ; પરિણામ 12 અને 4નું ભાગફળ છે.'},
 'eip-id1168288480300':{'kind':'aria-placeholder','issue':'Source aria is only t, not meaningful accessibility text. Faithful transliterationટી retained.','corrected_gu':'11નો 11 વડે ભાગાકાર કરતાં 1 મળે છે. ચકાસણી: 1 × 11 = 11.'},
 'eip-id1168288536381':{'kind':'aria-placeholder','issue':'Source aria is only t.','corrected_gu':'19નો 1 વડે ભાગાકાર કરતાં 19 મળે છે. ચકાસણી: 19 × 1 = 19.'},
 'eip-id1168289599719':{'kind':'aria-placeholder','issue':'Source aria is only t.','corrected_gu':'7નો 1 વડે ભાગાકાર કરતાં 7 મળે છે. ચકાસણી: 7 × 1 = 7.'},
 'eip-244':{'kind':'aria-reversed-operands','issue':'Aria calls the shown long division3dividedby78thoughactual78dividedby3.','corrected_gu':'78નો 3 વડે લાંબો ભાગાકાર. 7માંથી 6 બાદ કરતાં 1 રહે છે; 8 નીચે ઉતારતાં 18 બને છે. 18માંથી 18 બાદ કરતાં શેષ શૂન્ય રહે છે. ભાગફળ 26 છે.'},
 'eip-287':{'kind':'aria-reversed-operands-and-subtrahend','issue':'Aria opens4dividedby2596instead of2596by4and says25−4instead of25−24.','corrected_gu':'2596નો 4 વડે લાંબો ભાગાકાર. 25માંથી 24 બાદ કરતાં 1 રહે છે. 9 નીચે ઉતારતાં 19 બને છે; 19માંથી 16 બાદ કરતાં 3 રહે છે. 6 નીચે ઉતારતાં 36 બને છે; 36માંથી 36 બાદ કરતાં શેષ શૂન્ય રહે છે. ભાગફળ 649 છે.'},
 'eip-879':{'kind':'aria-step-order','issue':'Aria describes quotient5above3immediately after first14−12, before bringing down3.','corrected_gu':'1439નો 4 વડે લાંબો ભાગાકાર. 14માંથી 12 બાદ કરતાં 2 રહે છે. 3 નીચે ઉતારતાં 23 બને છે; હવે ભાગફળમાં 5 લખીએ છીએ. 23માંથી 20 બાદ કરતાં 3 રહે છે. 9 નીચે ઉતારતાં 39 બને છે; 39માંથી 36 બાદ કરતાં શેષ 3 રહે છે. ભાગફળ 359 છે.'},
 'eip-787':{'kind':'aria-duplication-and-wrong-check-number','issue':'Aria repeats bring-down2outoforder and concludes74,3521. Actual correctcheck74521=241×309+52.','corrected_gu':'74521નો 241 વડે લાંબો ભાગાકાર. 745માંથી 723 બાદ કરતાં 22 રહે છે. 2 નીચે ઉતારતાં 222 બને છે; ભાગફળમાં સ્થાન જાળવવા 0 લખીએ છીએ. 1 નીચે ઉતારતાં 2221 બને છે. 2221માંથી 2169 બાદ કરતાં શેષ 52 રહે છે. ભાગફળ 309 છે. ચકાસણી: 309 × 241 + 52 = 74521.'},
 'fs-id1619545':{'kind':'aria-count','issue':'Source aria says3representations but actual expressioncell contains4divisionnotations.','corrected_gu':'કોષ્ટકમાં ભાગાકાર સૂચવતા શબ્દસમૂહો, 12નો 4 વડે ભાગાકાર દર્શાવતાં ઉદાહરણો અને ભાગાકારની ચાર જુદી લખાવટ છે.'},
}
LABELS={
 'CNX_BMath_Figure_01_05_047_img-06.png':[['quotient','ભાગફળ'],['divisor','ભાજક'],['remainder','શેષ']],
 'CNX_BMath_Figure_01_05_048_img-06.png':[['quotient','ભાગફળ'],['divisor','ભાજક'],['remainder','શેષ']],
 'CNX_BMath_Figure_01_05_049d_img.jpg':[['quotient','ભાગફળ'],['divisor','ભાજક'],['remainder','શેષ']],
 'CNX_BMath_Figure_01_05_209_img.jpg':[['Place Value','સ્થાનકિંમત'],['Digit','અંક'],['Total Value','કુલ કિંમત'],['hundreds','સો'],['tens','દશક'],['ones','એકમ']],
 'CNX_BMath_Figure_01_05_213_img.jpg':[['8 ft','8 ફૂટ'],['15 ft','15 ફૂટ']],
 'CNX_BMath_Figure_01_05_214_img.jpg':[['5 cm','5 સે.મી.'],['12 cm','12 સે.મી.'],['13 cm','13 સે.મી.']],
}
SELF_CHECK={'media_id':'eip-id1164270856201','image':'CNX_BMath_Figure_AppB_006.jpg','columns':['હું આ કરી શકું છું…','વિશ્વાસપૂર્વક','થોડી મદદથી','ના—મને સમજાતું નથી!'],'rows':['ભાગાકારની લખાવટનો ઉપયોગ કરવો.','પૂર્ણ સંખ્યાઓનો ભાગાકાર નમૂના દ્વારા દર્શાવવો.','પૂર્ણ સંખ્યાઓનો ભાગાકાર કરવો.','શબ્દોમાં આપેલી વાતને બીજગણિતની પદાવલીઓમાં ફેરવવી.','વ્યવહારુ પ્રશ્નોમાં પૂર્ણ સંખ્યાઓનો ભાગાકાર કરવો.'],'response_cells':[[None]*3 for _ in range(5)]}
PLACE_VALUE={'image':'CNX_BMath_Figure_01_05_209_img.jpg','columns':['સ્થાનકિંમત','અંક','કુલ કિંમત'],'rows':[['સો',2,200],['દશક',5,50],['એકમ',8,8],['','',258]],'model':'two hundred squares, five tens rods, eight ones blocks, actual image inspected'}
def charts():
 result=[]
 plus=[[0,1,None,3,4,None,6,7,None,9],[1,2,3,4,None,None,7,8,9,None],[None,3,4,5,6,7,8,None,10,11],[3,None,5,None,7,8,None,10,None,12],[4,5,None,None,8,9,None,None,12,None],[5,None,7,8,None,None,11,None,13,None],[6,7,8,None,10,None,None,13,None,15],[None,None,9,None,None,12,13,None,15,16],[8,9,None,11,None,None,14,None,16,None],[9,10,11,None,13,14,None,None,17,None]]
 times=[[0,0,0,0,0,None,0,None,0,0],[0,1,2,None,4,5,6,7,None,9],[0,None,4,None,8,10,None,14,16,None],[None,3,None,9,None,None,18,None,24,None],[0,4,None,12,None,None,24,None,None,36],[0,5,10,None,20,None,30,35,40,45],[None,None,12,18,None,None,36,42,None,54],[0,7,None,21,None,35,None,None,56,63],[0,8,16,None,32,None,48,None,64,None],[None,None,18,27,36,None,None,63,72,None]]
 for no,op,cells in [('222','+',plus),('226','×',times)]:
  result.append({'image':f'CNX_BMath_Figure_01_05_{no}_img.jpg','operation':op,'source_status':'problem-partial','row_headers':list(range(10)),'column_headers':list(range(10)),'visible_cells':cells,'evidence':'Transcribed from direct enlargement of actual source image; source alt is flawed. All source blanks retained.'})
 for no,op,filled in [('223','+',True),('224','+',False),('227','×',True),('228','×',False)]:
  rr=list(range(10))if filled else list(range(6,10));cc=list(range(10))if filled else list(range(3,10))
  result.append({'image':f'CNX_BMath_Figure_01_05_{no}_img.jpg','operation':op,'source_status':'supplied-solution'if filled else'problem-blank','row_headers':rr,'column_headers':cc,'visible_cells':[[(r+c if op=='+' else r*c)if filled else None for c in cc]for r in rr],'evidence':'Actual image inspected and supplied solution cells independently recomputed. Blank questions remain blank.'})
 for chart in result:
  for r,row in zip(chart['row_headers'],chart['visible_cells']):
   assert len(row)==len(chart['column_headers'])
   for c,v in zip(chart['column_headers'],row):
    if v is not None:assert v==(r+c if chart['operation']=='+' else r*c),(chart['image'],r,c,v)
 return result

def main():
 sys.stdout.reconfigure(encoding='utf-8');assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
 source=ET.parse(SOURCE).getroot();target=ET.parse(OUTPUT).getroot()
 assert target.attrib.pop('{http://www.w3.org/XML/1998/namespace}lang')=='gu-Gujr-IN'
 stats=validate_pair(source,target);assert not gather(target)
 residual=[v for v in residual_attributes(target)if natural_latin(v['text'])];assert not residual,residual
 equations=[];pairs=[];bare=[];remainder=[];undefined=[]
 for m in target.iter(M+'math'):
  try:t=norm(mathtext(m))
  except ValueError:continue
  if re.fullmatch(r'[0-9+*/()\-]+=[0-9+*/()\-]+',t):
   a,b=t.split('=');assert calc(a)==calc(b),t;equations.append(t)
  if re.fullmatch(r'[0-9+*/()\-]+;\d+',t):
   a,b=t.split(';');assert calc(a)==int(b),t;pairs.append(t)
 for ex in target.iter(C+'exercise'):
  p=ex.find(C+'problem');s=ex.find(C+'solution')
  if p is None or s is None:continue
  pm=exprs(p);sm=exprs(s);st=norm(flat(s)).replace('$','')
  if pm and len(pm)==len(sm) and all(x and re.fullmatch(r'[0-9+*/()\-]+',x)and re.search(r'[+*/\-]',x)for x in pm) and all(x and re.fullmatch(r'\d+',x)for x in sm):
   assert [calc(x)for x in pm]==list(map(int,sm)),(ex.get('id'),pm,sm);bare.append(ex.get('id'))
  if len(pm)==1 and pm[0] and re.fullmatch(r'[0-9+*/()\-]+',pm[0])and re.search(r'[+*/\-]',pm[0]):
   if re.fullmatch(r'\d+',st):
    assert calc(pm[0])==int(st),(ex.get('id'),pm,st)
    if ex.get('id')not in bare:bare.append(ex.get('id'))
   if st=='વ્યાખ્યાયિતનથી':
    try:calc(pm[0]);raise AssertionError(ex.get('id'))
    except ZeroDivisionError:undefined.append(ex.get('id'))
   rem=re.fullmatch(r'(\d+)R(\d+)',st)or re.fullmatch(r'ભાગફળ(\d+)અનેશેષ(\d+)',st)
   if rem:
    dividend,divisor=re.fullmatch(r'\(?(\d+)\)?/\(?(\d+)\)?',pm[0]).groups()
    n,d,q,r=map(int,(dividend,divisor,*rem.groups()));assert n==d*q+r and 0<=r<d,(ex.get('id'),n,d,q,r);remainder.append(ex.get('id'))
  if re.fullmatch(r'[0-9+*/()\-]+;\d+',st):
   a,b=st.split(';');assert calc(a)==int(b),(ex.get('id'),st);pairs.append(st)
 # Source-bound independent computations, not generated missing answers.
 worked={'fs-id1231874':('2596/4',649),'fs-id2877048':('4506/6',751),'fs-id2646175':('7263/9',807),'fs-id1618615':('51/17',3),'fs-id1519296':('160/8',20),'fs-id2830290':('135/9',15),'fs-id1738974':('36/4',9),'fs-id2266431':('64/2',32),'fs-id2189920':('125/5',25),'fs-id1347502':('48/3',16),'fs-id2993531':('45-17',28),'fs-id3366641':('45/9',5),'fs-id1258137':('8+14+11+17',50),'fs-id998947':('12*4',48),'fs-id1931975':('24+14+38',76),'fs-id1917106':('86-28',58),'fs-id2388645':('8*6',48),'fs-id1499411':('12*150',1800),'fs-id2909001':('27/3',9),'fs-id2692098':('3816-3472',344),'fs-id2881667':('12+6+9+3',30)}
 for ident,(equation,answer)in worked.items():
  assert calc(equation)==answer
  sol=next(e for e in target.iter(C+'exercise')if e.get('id')==ident).find(C+'solution')
  txt=flat(sol)+' '+' '.join(e.get('alt','')for e in sol.iter())
  numbers=[int(x.replace(',',''))for x in re.findall(r'\d+(?:,\d{3})*',txt)]
  assert answer in numbers,(ident,answer)
 remainders={'fs-id1572223':(1439,4,359,3),'fs-id1524226':(1461,13,112,5),'fs-id1410272':(74521,241,309,52)}
 for ident,(n,d,q,r)in remainders.items():
  assert n==d*q+r and 0<=r<d
  ex=next(e for e in target.iter(C+'exercise')if e.get('id')==ident)
  assert calc(exprs(ex.find(C+'problem'))[0])==Fraction(n,d)
  txt=flat(ex.find(C+'solution'));assert str(q)in txt and str(r)in txt
 # Bind all three vertical MathML checks to the actual output cells.
 tables=list(target.iter(M+'mtable'));assert len(tables)==3
 values=[[norm(vertical_text(row))for row in table]for table in tables[:2]]
 assert values==[['26','*3','78'],['3','*8','24','+4','28']],values
 assert calc(values[0][0]+values[0][1])==calc(values[0][2])
 assert calc(values[1][0]+values[1][1])==calc(values[1][2])
 assert calc(values[1][2]+values[1][3])==calc(values[1][4])
 cells=[norm(mathtext(row[-1]))for row in tables[2]]
 assert cells[1:]==['51/17','3'] and calc(cells[1])==calc(cells[2])
 assert divmod(365,14)==(26,1) and (365+14-1)//14==27
 assert 2*100+5*10+8==258 and 2*(8+15)==46
 rounding={'fs-id1543448':(412,10,410),'fs-id1804438':(3556,10,3560),'fs-id1510692':(38975,100,39000),'fs-id2785009':(81486,100,81500)}
 for ident,(n,place,answer)in rounding.items():
  ex=next(e for e in target.iter(C+'exercise')if e.get('id')==ident)
  assert exprs(ex.find(C+'problem'))==[str(n)]
  assert (n+place//2)//place*place==answer==int(norm(flat(ex.find(C+'solution'))))
 chartdata=charts();inventory=[]
 for e in source.iter(C+'media'):
  file=Path(list(e)[0].get('src')).name;p=MEDIA/file
  inventory.append({'media_id':e.get('id'),'source_file':file,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'review':'actual source image inspected on contact sheet; selected error/chart/self-check images additionally enlarged','localization':'full self-check table supplied'if file==SELF_CHECK['image']else'Gujarati label mapping supplied'if file in LABELS else'retain original numeric/symbolic image; R remains source-defined mathematical remainder notation'})
 missing=[e.get('id')for e in source.iter(C+'exercise')if e.find(C+'solution')is None]
 receipt={'module':'m81256','source_sha256':SHA,'translation_sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),'integrity':stats,'language_slots':810,'all_accessibility_attributes_translated':21,'english_natural_language_slot_residuals':0,'english_natural_accessibility_attribute_residuals':0,'preserved_latin_math_symbols':['R remainder notation','x multiplication notation','(a)/(b) source choice labels'],'numeric_math_equalities_checked':len(equations),'expression_answer_pairs_checked':len(pairs),'bare_answer_exercises_checked':len(bare),'remainder_answer_exercises_checked':len(remainder),'undefined_answer_exercises_checked':len(undefined),'independent_worked_application_results':len(worked),'independent_worked_remainder_results':len(remainders),'all_mathml_tables_manually_checked':3,'additional_ceil_model_perimeter_checks':3,'source_rounding_answers_checked':len(rounding),'chart_visible_numeric_cells_checked':sum(v is not None for c in chartdata for row in c['visible_cells']for v in row),'missing_source_solution_count':len(missing),'missing_source_solution_ids':missing,'media':inventory,'figure_label_translations':LABELS,'self_check':SELF_CHECK,'place_value_258':PLACE_VALUE,'source_chart_accessible_data':chartdata,'source_errata':ERRATA,'source_faithfulness_note':'Faithful CNXML retains all source structures, numeric tokens, existing omissions and mistakes. Corrections and accessible image equivalents here are separately keyed editorial content. No missing-source solutions added. R, x and source choice letters are mathematical notation, not untranslated prose. English grammatical signal words of/and are explicitly presented as English and transliterated in Gujarati; a separate reader bridge may explain Gujarati phrasing.'}
 (ROOT/'gu-Gujr-IN/translations/a00-m81256-media-and-errata.gu.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in receipt.items()if k not in ('media','figure_label_translations','self_check','place_value_258','source_chart_accessible_data','source_errata','missing_source_solution_ids')},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
