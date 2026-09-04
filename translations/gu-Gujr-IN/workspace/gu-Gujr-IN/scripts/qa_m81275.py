"""Exact signed/absolute-value answer QA and actual-image handoff, all m81275."""
import ast,hashlib,json,re,sys
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import xml.etree.ElementTree as E
from prepare_m81275 import ROOT,SOURCE,SHA,gather,ATTRIBUTES
from a00_accessibility_attributes import validate_pair,LANGUAGE_ATTRS
from qa_m81273 import written,maths
from qa_m81270 import norm
C='{http://cnx.rice.edu/cnxml}';M='{http://www.w3.org/1998/Math/MathML}'
OUTPUT=ROOT/'gu-Gujr-IN/translations/a00-m81275.gu.cnxml'
MEDIA=ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'
flat=lambda e:' '.join(''.join(e.itertext()).split())
def clean(e):return norm(re.sub('[ⓐⓑⓒⓓ]','',written(e))).strip()
def ev(s,env=None):
 s=re.sub(r'\|([^|]*)\|',lambda m:'A('+m[1]+')',s)
 assert '|'not in s,s
 s=norm(s);s=re.sub(r'(?<=[\da-z)])(?=A)','*',s);env=env or {}
 def walk(n):
  if isinstance(n,ast.Expression):return walk(n.body)
  if isinstance(n,ast.Constant)and type(n.value)is int:return Fraction(n.value)
  if isinstance(n,ast.Name):return Fraction(env[n.id])
  if isinstance(n,ast.UnaryOp):return -walk(n.operand)if isinstance(n.op,ast.USub)else walk(n.operand)
  if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='A'and len(n.args)==1:return abs(walk(n.args[0]))
  if isinstance(n,ast.BinOp):
   a,b=walk(n.left),walk(n.right)
   if isinstance(n.op,ast.Add):return a+b
   if isinstance(n.op,ast.Sub):return a-b
   if isinstance(n.op,ast.Mult):return a*b
   if isinstance(n.op,ast.Div):return a/b
   if isinstance(n.op,ast.Pow)and b.denominator==1:return a**int(b)
  raise AssertionError(s)
 return walk(ast.parse(s,mode='eval'))
def answer_parts(e):
 items=list(e.iter(C+'item'))
 return [clean(a)for a in items]if items else[clean(e)]
def relation(a,b):return '<'if a<b else'>'if a>b else'='
def pair(s):
 parts=re.split('_+|[<>=]',s);assert len(parts)==2,(s,parts)
 return tuple(ev(p)for p in parts)
def rhs(table):
 out=[]
 for row in table.iter(C+'row'):
  cells=row.findall(C+'entry');s=clean(cells[-1])
  if s:out.append(s)
 return out
def sign_amount(s):
 raw=re.sub(r'(?<=\d),(?=\d{3}(?:\D|$))','',s).replace('−','-')
 found=re.findall(r'[+-]?\$?\d+',raw);assert len(found)==1,(s,found)
 return int(found[0].replace('$',''))

# Actual plot coordinates, independently read from the images, including the
# erroneous source-alt b=5 for the final plot whose actual b is8.
PLOTS={0:[0,1,3],2:[3,-3,-2],3:[1,-1,-4],4:[-4,4,-1],41:[2,-2,-5],43:[-8,8,-6]}
LABELS={
 'CNX_BMath_Figure_03_01_003.jpg':{'labels':['ભૂમધ્ય સમુદ્ર (0 ફૂટ)','ઇઝરાયલ','મૃત સમુદ્ર (−1302 ફૂટ)','જોર્ડન'],'scope':'મૂળની ઊંચાઈઓ અને સમુદ્રની સપાટીઓ જાળવો; આ માપ પ્રમાણે દોરેલો ભૌગોલિક નકશો નથી.'},
 'CNX_BMath_Figure_03_01_004.jpg':{'labels':['0 ફૂટ','−500 ફૂટ'],'scope':'પાણીની સપાટીએ શૂન્ય; ઊભી માપરેખા પર પાંચસો ફૂટ નીચે સબમરીન. મૂળ મધ્યનાં અંક વગરનાં સમાન અંતરનાં ચિહ્નો જાળવો.'},
 'CNX_BMath_Figure_03_01_006.jpg':{'labels':['ઋણ સંખ્યાઓ','ધન સંખ્યાઓ','શૂન્ય'],'range':[-4,4],'scope':'શૂન્યની ડાબે ઋણ, જમણે ધન; શૂન્યને બંને કૌંસની બહાર રાખો. શૂન્યનો ઊભો તીર જાળવો.'},
 'CNX_BMath_Figure_03_01_012.jpg':{'labels':['વધતું','ઘટતું'],'range':[-4,4],'scope':'ઉપરનો આછો વાદળી-લીલો તીર જમણે, નીચેનો લાલ તીર ડાબે. દિશાઓ બદલશો નહીં.'},
 'CNX_BMath_Figure_03_01_016.jpg':{'panels':[{'id':'a','opposites':[-2,2],'distance':2,'text_gu':'સંખ્યાઓ −2 અને 2 એકબીજાની વિરોધી સંખ્યાઓ છે.'},{'id':'b','opposites':[-3,3],'distance':3,'text_gu':'સંખ્યાઓ −3 અને 3 એકબીજાની વિરોધી સંખ્યાઓ છે.'}],'range':[-4,4],'scope':'મૂળ બંને પેનલ, બિંદુઓ, શૂન્યની બંને બાજુના સમાન અંતરનાં કૌંસ અને (a)/(b) ઓળખ જાળવો.'},
 'CNX_BMath_Figure_03_01_019.jpg':{'labels':['−5 શૂન્યથી 5 એકમ દૂર છે, તેથી |−5| = 5.','5 શૂન્યથી 5 એકમ દૂર છે, તેથી |5| = 5.','5 એકમ','5 એકમ'],'points':[-5,0,5],'scope':'બંને પૂર્ણ સમજૂતી, બંને નિરપેક્ષ મૂલ્યનાં સમીકરણ, બંને પાંચ-એકમનાં નામ, વાદળી-લીલા તીર અને સમાન અંતરનાં કૌંસ જાળવો.'},
}
SUBSTITUTIONS=[('020',8,'x','-(8)',-8),('021',-8,'x','-(-8)',8),('022',-35,'x','|-35|',35),('023',-20,'y','|-(-20)|',20),('024',12,'u','-|12|',-12),('025',-14,'p','-|-14|',-14)]
for code,n,v,expr,value in SUBSTITUTIONS:
 LABELS[f'CNX_BMath_Figure_03_01_{code}_img-01.png']={'text_gu':f'{v}ની જગ્યાએ {str(n).replace("-","−")} મૂકો.','value':n,'variable':v,'highlight':'સંપૂર્ણ મૂકેલી સંખ્યા લાલ રાખો, તેની ઋણ નિશાની સહિત; ચલ કાળો/ઘેરો અને ત્રાંસો.','following_original_math':expr,'result':value}
SELF_CHECK={'source_file':'CNX_BMath_Figure_AppB_013.jpg','headers':['હું કરી શકું છું…','આત્મવિશ્વાસથી','થોડી મદદથી','ના—મને સમજાતું નથી!'],'skills':['સંખ્યારેખા પર ધન અને ઋણ સંખ્યાઓનાં સ્થાન દર્શાવવાં.','ધન અને ઋણ સંખ્યાઓનો ક્રમ નક્કી કરવો.','વિરોધી સંખ્યાઓ શોધવી.','નિરપેક્ષ મૂલ્ય ધરાવતી પદાવલીઓ સરળ કરવી.','શબ્દસમૂહોને પૂર્ણાંક ધરાવતી પદાવલીઓમાં ફેરવવા.'],'blank_response_cells':15,'answer_policy':'પંદરેય પ્રતિભાવનાં ખાના ખાલી રાખો.'}
ERRATA=[]
def err(key,ids,issue,gu,**kw):ERRATA.append({'key':key,'source_ids':ids,'issue':issue,'corrected_reader_text_gu':gu,**kw})
err('thermometer-sign',['fs-id1724574'],'Source alt says20degrees; actual thermometer and source prose show−20°F.','થર્મોમીટર ઋણ વીસ ડિગ્રી ફેરનહાઇટ દર્શાવે છે.',corrected_alt_gu='ડિગ્રી ફેરનહાઇટનું થર્મોમીટર; વાંચન ઋણ વીસ ડિગ્રી છે, શૂન્યથી વીસ ડિગ્રી નીચે.')
err('extra-negative-alt',['eip-id1168469566638'],'Source alt has|-(-(-20))|; actual023-02has|-(-20)|. Same absolute result does not make its structure equivalent.','ચિત્રમાં |−(−20)| છે. અંદરની ઋણ વીસ લાલ છે; બહારની ઋણ નિશાની અને કૌંસ કાળાં છે.',corrected_alt_gu='નિરપેક્ષ મૂલ્યની અંદર ઋણ નિશાની અને પછી કૌંસમાં ઋણ વીસ: |−(−20)|. કૌંસમાંની ઋણ વીસ લાલ છે.')
err('missing-opposite-aria',['eip-id1168469585161'],'Source aria firstrow saysabsolutevalueofy; actual firstrow isabsolutevalueof−y.','પહેલી હરોળમાં |−y| છે. yની જગ્યાએ ઋણ વીસ મૂકી |−(−20)| મળે છે, જે |20| પછી વીસ થાય છે.',corrected_aria_label_gu='ચાર હરોળ: |−y|; yની જગ્યાએ ઋણ વીસ મૂકો; અંદરની વિરોધી સંખ્યા સરળ કરતાં |20|; નિરપેક્ષ મૂલ્ય લેતાં વીસ.')
err('plot203-b',['fs-id1054913'],'Source alt saysb=5; actual203andproblem43sayb=8.','સંખ્યારેખા પર a ઋણ આઠના સ્થાને, b આઠના સ્થાને અને c ઋણ છના સ્થાને છે.',corrected_alt_gu='સંખ્યારેખા પર a = −8, b = 8 અને c = −6. મૂળ ચિત્રનું b આઠે છે, પાંચે નહીં.')
err('circled-choice-summary',['eip-id1171842583307'],'Source summary confusescircledchoiceⓒ withcopyrightsymbol.','અહીં ⓒ પ્રશ્નના ત્રીજા ભાગની ઓળખ છે. |0| = 0, કારણ કે શૂન્ય શૂન્યથી શૂન્ય એકમ દૂર છે.',corrected_summary_gu='પ્રશ્નનો ત્રીજો ભાગ: શૂન્યનું નિરપેક્ષ મૂલ્ય શૂન્ય છે; ⓒ ભાગની ઓળખ છે.')
err('absolute-image-completeness',['fs-id1595569'],'Source alt omits the actual full text and two absolute-value equalities on019.','ઋણ પાંચ અને પાંચ બંને શૂન્યથી પાંચ એકમ દૂર છે. તેથી |−5| = 5 અને |5| = 5. બંને બાજુ સમાન અંતર દર્શાવતા કૌંસ છે.',corrected_alt_gu='સંખ્યારેખા પર ઋણ પાંચ, શૂન્ય અને પાંચ. બંને બાજુ પાંચ એકમનું અંતર. લખાણ સ્પષ્ટ કરે છે: |−5| = 5 અને |5| = 5.')
err('unsigned-zero',['fs-id1103886'],'Unqualifiedunsignedmeanspositiverule wrongly includeszero. Source006caption correctly excludeszero; Indo drops the final overgeneralization.','ધન સંખ્યાની આગળની વત્તાની નિશાની સામાન્ય રીતે છોડીએ છીએ. પરંતુ શૂન્ય ધન પણ નથી અને ઋણ પણ નથી.')
for ident,n in [('eip-id1166567530079',12),('eip-id1166568936114',1302),('eip-id1166566291529',40)]:
 err('context-sign-'+ident,[ident],f'Source says unsigned{n}isnegative; context requires representing quantity as−{n}, not reclassifying positive numeral.',f'આ સંદર્ભમાં સંખ્યા {n}ની આગળ ઋણ નિશાની મૂકીને દર્શાવવાની છે. નિશાની વગરની સંખ્યા {n} પોતે ધન છે.')
err('do-not-simplify-alternatives',['eip-788','eip-id1168469720526','eip-id1168467354570'],'Instruction saysdonotsimplify; suppliedbanswers also include simplified alternatives6and5. Preserve both source answers.','સૂચના પ્રમાણે પહેલાં વિરોધી સંખ્યાની પદાવલી લખો: −(−6) અથવા −(−5). મૂળ જવાબમાં તેના સરળ કરેલા મૂલ્ય છ અને પાંચ પણ વિકલ્પ તરીકે આપ્યા છે.')
BRIDGES=[
 {'source_ids':['fs-id2307168','fs-id2680246'],'note_gu':'શૂન્ય સિવાયની સંખ્યાની વિરોધી સંખ્યા શૂન્યની બીજી બાજુ સમાન અંતરે હોય છે. શૂન્યની વિરોધી સંખ્યા શૂન્ય જ છે.'},
 {'source_ids':['fs-id1768644'],'note_gu':'મૂળ અંગ્રેજી પ્રશ્નમાં માઉન્ટ મૅકકિન્લીની ઊંચાઈ 20,320 ફૂટ છે; ઇન્ડોનેશિયન સાક્ષીમાં 20,310 છે. અહીં પિન કરેલા અંગ્રેજી પ્રશ્નનો આંકડો અને આપેલો જવાબ જાળવ્યાં છે. હાલના ભૌગોલિક આંકડા તરીકે મૌન રીતે અપડેટ કર્યા નથી.'},
 {'source_ids':['fs-id1673833','fs-id1299001','fs-id2539952','fs-id1374603'],'note_gu':'આ પ્રશ્નોમાં મૂળના માપ, એકમો, સમયસંદર્ભ અને ઐતિહાસિક માહિતી જાળવેલાં છે. તેમને તાજા રેકોર્ડ કે આજના અંદાજપત્રની માહિતી ન ગણશો. સેલ્સિયસના મહત્તમ અને લઘુત્તમના મૂળ આંકડાઓને અહીં ચોક્કસ નવા વૈજ્ઞાનિક રેકોર્ડ તરીકે ચકાસ્યાનો દાવો નથી.'},
 {'source_ids':['fs-id1367615','fs-id1552620','fs-id4297808','fs-id1937480'],'note_gu':'યાર્ડમાં આગળ કે પાછળ જવાનું અહીં અમેરિકન ફૂટબૉલનો સંદર્ભ છે. ગૉલ્ફમાં પાર એટલે નક્કી કરેલી પ્રમાણભૂત સ્ટ્રોક સંખ્યા; તેની ઉપર ધન અને નીચે ઋણ સ્કોર લખીએ છીએ.'},
]

def main():
 sys.stdout.reconfigure(encoding='utf-8');assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
 source=E.parse(SOURCE).getroot();target=E.parse(OUTPUT).getroot();check=deepcopy(target);lang='{http://www.w3.org/XML/1998/namespace}lang'
 if source.get(lang)is None:check.attrib.pop(lang,None)
 else:check.set(lang,source.get(lang))
 stats=validate_pair(source,check);assert target.get(lang)=='gu-Gujr-IN'
 allowed={'F','a','b','c','m','n','p','q','u','x','y','z'};residual=[]
 for k,slots in gather(target).items():
  for _,field,t in slots:
   for w in re.findall('[A-Za-z]+',t):
    if w not in allowed:residual.append((k,field,w))
 for e in target.iter():
  for attr in LANGUAGE_ATTRS:
   for w in re.findall('[A-Za-z]+',e.get(attr,'')):
    if w not in allowed:residual.append((e.get('id'),attr,w))
 assert not residual,residual
 ex=list(source.iter(C+'exercise'));gu=list(target.iter(C+'exercise'));checked={};tables_checked=set();steps=0
 def p(i,t=ex):return t[i].find(C+'problem')
 def s(i,t=ex):return t[i].find(C+'solution')
 def mark(i,kind):assert i not in checked and s(i)is not None;checked[i]=kind
 def check_steps(table,value,env=None):
  nonlocal steps
  cells=rhs(table);assert cells,(table.get('id'),cells)
  for q in cells:assert ev(q,env)==value,(table.get('id'),q,value);steps+=1
  tables_checked.add(table.get('id'))
 for i,coords in PLOTS.items():
  got=list(map(int,re.findall(r'-?\d+',','.join(maths(p(i))))));assert got==coords,(i,got,coords)
  mark(i,'actual plotted coordinates')
 assert maths(s(1))==['<']and 2<4;mark(1,'readiness comparison')
 for i in (5,23):
  problems=[q for q in maths(p(i))if '_'in q];tt=list(s(i).iter(C+'table'));assert len(problems)==len(tt)
  for q,t in zip(problems,tt):
   a,b=pair(q)
   for j,row in enumerate(rhs(t)):
    assert pair(row)==(a,b),(i,row,q)
    if '_'not in row:assert re.findall('[<>=]',row)==[relation(a,b)]
   tables_checked.add(t.get('id'))
  mark(i,'worked comparisons with all intermediate values')
 for i in (6,7,24,25,45,47,69,71):
  want=[relation(*pair(q))for q in maths(p(i))if '_'in q]
  assert answer_parts(s(i))==answer_parts(s(i,gu))==want;mark(i,'complete comparison parts')
 assert maths(p(8))==['7','-10'];items=list(s(8).iter(C+'item'))
 for n,item in zip([7,-10],items):assert ev(maths(item)[-2])==-n
 mark(8,'worked opposites and equal-distance figures')
 for i in (9,10,49,51):
  want=[-ev(q)for q in maths(p(i))];assert [ev(q)for q in answer_parts(s(i))]==[ev(q)for q in answer_parts(s(i,gu))]==want;mark(i,'opposite values')
 for i in (11,17,26,29,32):
  exprs=maths(p(i));tt=list(s(i).iter(C+'table'));assert len(exprs)==len(tt)
  for expr,t in zip(exprs,tt):check_steps(t,ev(expr))
  mark(i,'all worked simplification steps')
 for i in (12,13,18,19,27,28,30,31,33,34,53,55,61,63,73,75,77,79,81):
  want=[ev(q)for q in maths(p(i))];assert [ev(q)for q in answer_parts(s(i))]==[ev(q)for q in answer_parts(s(i,gu))]==want,(i,want,answer_parts(s(i)))
  mark(i,'signed and absolute-value simplification')
 for i in (14,15,16,57,59):
  pp=maths(p(i));expr=pp[0].rstrip(':@');pairs=[q.lstrip('@').split('=')for q in pp[1:]];envs=[{k:int(v)}for k,v in pairs];want=[ev(expr,env)for env in envs]
  if i==14:
   for t,env,value in zip(s(i).iter(C+'table'),envs,want):check_steps(t,value,env)
  else:assert [ev(q)for q in answer_parts(s(i))]==[ev(q)for q in answer_parts(s(i,gu))]==want
  mark(i,'both signs substituted into opposite variable')
 for i in (20,21,22,65,67):
  exprs=[];envs=[]
  for q in maths(p(i)):
   expr,assignment=q.split('@');k,v=assignment.split('=');exprs.append(expr);envs.append({k:int(v)})
  want=[ev(expr,env)for expr,env in zip(exprs,envs)]
  if i==20:
   for t,env,value in zip(s(i).iter(C+'table'),envs,want):check_steps(t,value,env)
  else:assert [ev(q)for q in answer_parts(s(i))]==[ev(q)for q in answer_parts(s(i,gu))]==want
  mark(i,'absolute-value scope with substitutions')
 for i,want in [(35,[-14,11,-16,9]),(36,[-9,15,-20,15]),(37,[19,-22,-9,-3]),(83,[-8,6,-3,7]),(85,[-20,5,-12,25])]:
  for t in (ex,gu):
   parts=maths(s(i,t))if i==35 else answer_parts(s(i,t));assert len(parts)==len(want)
   for q,n in zip(parts,want):
    for form in re.split(r'=|,o\*r\*?|,અથવા',q):assert ev(form)==n,(i,q,n)
  mark(i,'independently read signed word phrase')
 for i,want in [(39,[5]),(40,[-30]),(87,[-6]),(89,[-40]),(91,[-12]),(93,[3]),(95,[1]),(97,[20320,-282]),(99,[540,-27])]:
  for t in (ex,gu):assert [sign_amount(q)for q in answer_parts(s(i,t))]==want,(i,answer_parts(s(i,t)),want)
  if i==99:
   assert 'million'in flat(s(i))and'billion'in flat(s(i));assert 'મિલિયન'in flat(s(i,gu))and'બિલિયન'in flat(s(i,gu))
  mark(i,'signed quantity with original units and scale')
 app_tables=list(s(38).iter(C+'table'));assert len(app_tables)==4
 for table,want in zip(app_tables,[-12,3,-1302,-40]):
  assert sign_amount(rhs(table)[-1])==want;tables_checked.add(table.get('id'))
 mark(38,'four application signs and units')
 assert 'Sample answer'in flat(s(101))and 'નમૂનાનો જવાબ' in flat(s(101,gu));mark(101,'open life example retained as sample')
 roles=next(e for e in source.iter(C+'table')if e.get('id')=='eip-id1168469523154')
 first=[clean(row.findall(C+'entry')[0])for row in roles.iter(C+'row')];assert first==['10-4','-8','-x','-(-2)'];assert [ev(first[0]),ev(first[1]),ev(first[3])]==[6,-8,2]
 assert ev(first[2],{'x':8})==-8 and ev(first[2],{'x':-8})==8;tables_checked.add(roles.get('id'))
 supplied={i for i,e in enumerate(ex)if e.find(C+'solution')is not None};assert set(checked)==supplied,(sorted(supplied-set(checked)),sorted(set(checked)-supplied));assert len(checked)==72
 assert tables_checked=={e.get('id')for e in source.iter(C+'table')},({e.get('id')for e in source.iter(C+'table')}-tables_checked)
 assert len(tables_checked)==27 and not list(source.iter(M+'mtable'))
 for code,n,v,expr,result in SUBSTITUTIONS:assert ev(expr)==result
 for part in LABELS['CNX_BMath_Figure_03_01_016.jpg']['panels']:
  a,b=part['opposites'];assert a==-b and abs(a)==part['distance']==abs(b)
 media=[]
 for e in source.iter(C+'media'):
  name=e.find(C+'image').get('src').rsplit('/',1)[-1];path=MEDIA/name;assert path.is_file()
  media.append({'source_id':e.get('id'),'file':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'visually_read':True,'language_bearing':name in LABELS or name==SELF_CHECK['source_file']})
 assert len(media)==36 and sum(m['language_bearing']for m in media)==13
 ids={e.get('id')for e in source.iter()if e.get('id')}
 for entry in ERRATA+BRIDGES:assert all(k in ids for k in entry['source_ids']),entry
 missing=[{'source_index':i,'exercise_id':e.get('id'),'problem_id':e.find(C+'problem').get('id')}for i,e in enumerate(ex)if e.find(C+'solution')is None];assert len(missing)==31
 receipt={'module':'m81275','source_sha256':SHA,'translation_sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),'integrity':stats,'language_slots':613+len(ATTRIBUTES),'other_language_attributes':len(ATTRIBUTES),'natural_language_English_residuals':residual,'allowed_Latin':'Original literal variables and Fahrenheit unit F; source paths/identifiers unchanged.','provided_answers_checked':len(checked),'answer_categories':dict(Counter(checked.values())),'checked_answers':[{'source_index':i,'exercise_id':ex[i].get('id'),'check':checked[i]}for i in sorted(checked)],'worked_tables_checked':len(tables_checked),'numeric_worked_steps':steps,'source_omitted_solutions':missing,'actual_plot_coordinates':PLOTS,'media':media,'localized_figure_content':LABELS,'substitution_math':SUBSTITUTIONS,'self_check':SELF_CHECK,'source_errata':ERRATA,'reader_bridges':BRIDGES,'status':'Complete translator source workflow; image localization/reader integration and educator review remain separate.'}
 out=ROOT/'gu-Gujr-IN/translations/a00-m81275-media-and-errata.gu.json';out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'result':'pass',**stats,'language_slots':receipt['language_slots'],'provided_answers_checked':len(checked),'worked_tables_checked':len(tables_checked),'numeric_steps':steps,'omitted_solutions':31,'media':36,'language_figures':13,'errata':len(ERRATA),'bridges':len(BRIDGES),'sha256':receipt['translation_sha256']},indent=2))
if __name__=='__main__':main()
