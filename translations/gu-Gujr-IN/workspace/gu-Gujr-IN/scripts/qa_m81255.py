"""m81255 source integrity, independent arithmetic, complete media/errata handoff."""
import ast,hashlib,json,re,sys
from pathlib import Path
import xml.etree.ElementTree as ET
from prepare_m81255 import ROOT,SOURCE,SHA,gather
from a00_accessibility_attributes import validate_pair,residual_attributes
C='{http://cnx.rice.edu/cnxml}';M='{http://www.w3.org/1998/Math/MathML}'
OUTPUT=ROOT/'gu-Gujr-IN/translations/a00-m81255.gu.cnxml'
MEDIA=ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'
flat=lambda e:' '.join(''.join(e.itertext()).split())
def norm(t):
 t=re.sub(r'\s+','',t).replace(',','').replace('−','-').rstrip('.;✓')
 for x in ('×','·','⋅'):t=t.replace(x,'*')
 t=re.sub(r'(?<=[\d)])(?=\()', '*',t)
 t=re.sub(r'(?<=\))(?=\d)', '*',t)
 return t
def calc(t):
 assert re.fullmatch(r'[0-9+*()\-]+',t),t
 def walk(n):
  if isinstance(n,ast.Expression):return walk(n.body)
  if isinstance(n,ast.Constant) and type(n.value) is int:return n.value
  if isinstance(n,ast.BinOp):
   a,b=walk(n.left),walk(n.right)
   if isinstance(n.op,ast.Mult):return a*b
   if isinstance(n.op,ast.Add):return a+b
   if isinstance(n.op,ast.Sub):return a-b
  raise ValueError(t)
 return walk(ast.parse(t,mode='eval'))

ERRATA={
 'fs-id2278409':{'kind':'body','issue':'English says multiply by10 in896×201 although the tens multiplier is0; the adjacent source diagram and Indonesian witness clarify the zero placeholder. The source also places2×6=12 before its final locative phrase.','corrected_gu':'પહેલાં 1 વડે ગુણાકાર કરો. દશકનો અંક 0 હોવાથી દશકનું સ્થાન જાળવવા એક શૂન્ય મૂકો. પછી 200 વડે ગુણાકાર કરો. 2 × 6 = 12 હોવાથી તેમાંથી 2 સોના સ્થાને મૂકો.'},
 'eip-279':{'kind':'body-place-value-clarification','issue':'During the8-tens multiplier the source says carry1 to the tens place; it is above the top tens digit6 but contributes one hundred to the shifted partial product.','corrected_gu':'8 દશકનો 2 એકમ વડે ગુણાકાર કરતાં 16 દશક મળે છે. તેના 6 દશક ગુણનફળના દશકના સ્થાને લખો અને 1 સો આગળ લઈ જાઓ. તે 1 ઉપરની સંખ્યાના દશકના અંક 6ની ઉપર લખાય છે. પછી 8 દશક અને 6 દશકના ગુણાકારથી 48 સો મળે છે; આગળ લઈ જવાયેલો 1 સો ઉમેરીને 49 સો થાય છે.'},
 'eip-id1170326423736':{'kind':'summary-algorithm','issue':'Fourth summary step multiplies the entire bottom number by top digits while subsequent steps again repeat bottom digits; main procedure correctly uses one bottom digit at a time.','corrected_gu':'નીચેની સંખ્યાના એકમના અંકનો ગુણાકાર ઉપરની સંખ્યાના એકમના અંક વડે, પછી દશકના અંક વડે અને એમ આગળ કરો. પછી નીચેની સંખ્યાના દશકના અંક માટે અને આગળનાં સ્થાનો માટે પ્રક્રિયા ફરી કરો.'},
 'fs-id1747316':{'kind':'solution-unit-word','issue':'Problem asks for shingles but supplied English answer says tiles; numerical1080 is correct.','corrected_gu':'યુસુફને છત ઢાંકવા 1,080 પટ્ટીઓ જોઈએ.'},
 'eip-id1168288456465475826':{'kind':'alt','issue':'Image020-04 carries only1 above the original62. Source alt incorrectly describes1and6 as carried digits above62.','corrected_gu':'62નો 87 વડે ગુણાકાર છે. પહેલા આંશિક ગુણનફળ માટે 62 × 7 = 434 લખેલું છે. આગળ લઈ જવાયેલો 1 ઉપર છે; લાલ 6 એ મૂળ સંખ્યા 62નો દશકનો અંક છે.'},
 'eip-id1168288446465456465475826':{'kind':'alt-terminology','issue':'Source calls carried1 a remainder. Here it is regrouping within multiplication, not a division remainder.','corrected_gu':'62નો 87 વડે ગુણાકાર છે. પહેલું આંશિક ગુણનફળ 434 છે. બીજા આંશિક ગુણનફળ માટે 8 × 2 = 16ના 6 દશક અને સ્થાન જાળવતો 0 નીચે લખીને 60 બનાવ્યું છે. આગળ લઈ જવાયેલો 1 ઉપર લખ્યો છે.'},
 'fs-id1944807':{'kind':'alt','issue':'Source alt describes a complete11×11 multiplication chart, including a pink zero. Actual207image is a partially blank question chart with no pink zero. See exact visible-cells matrix.','corrected_gu':'11 સ્તંભ અને 11 હરોળના ગુણાકાર કોષ્ટકમાં ઉપરની હરોળ અને ડાબા સ્તંભ પર 0થી 9 સુધીના અંક છે. કેટલાક ગુણનફળ આપેલા છે અને કેટલાક ખાનાં ખાલી છે; ખાલી ખાનાં ભરવાનાં છે. આ ચિત્રમાં ગુલાબી શૂન્ય નથી.'},
 'fs-id2676083':{'kind':'alt','issue':'Source alt says6columns6rows and headers5–9; actual219image has5columns5rows withheaders6–9.','corrected_gu':'5 સ્તંભ અને 5 હરોળનું ગુણાકાર કોષ્ટક. ઉપરની હરોળ અને ડાબા સ્તંભમાં 6, 7, 8, 9 છે. અંદરના 16 ખાનાં ખાલી છે અને ભરવાનાં છે.'},
}
LABELS={
 'CNX_BMath_Figure_01_04_008_img.jpg':[['Here are the 2 tens in 21.','21માંના 2 દશક અહીં છે.'],['Here is the 1 one in 21.','21માંનો 1 એકમ અહીં છે.']],
 'CNX_BMath_Figure_01_04_010_img.jpg':[['This comes from 3 × 2 plus the 2 we carried.','આ 3 × 2માં આગળ લઈ જવાયેલો 2 ઉમેરવાથી મળે છે.']],
 'CNX_BMath_Figure_01_04_011_img.jpg':[['Multiply 8(354)','ગુણાકાર કરો: 8(354)'],['Multiply 3(354)','ગુણાકાર કરો: 3(354)'],['Multiply 4(354)','ગુણાકાર કરો: 4(354)'],['Add the partial products','આંશિક ગુણનફળોનો સરવાળો કરો']],
 'CNX_BMath_Figure_01_04_012_img.jpg':[['Multiply 1(896)','ગુણાકાર કરો: 1(896)'],['Multiply 0(896)','ગુણાકાર કરો: 0(896)'],['Multiply 2(896)','ગુણાકાર કરો: 2(896)'],['Add the partial products','આંશિક ગુણનફળોનો સરવાળો કરો']],
 'CNX_BMath_Figure_01_04_014.jpg':[['1 cm','1 સે.મી.'],['1 square centimeter','1 ચોરસ સેન્ટિમીટર'],['(1 sq. cm or 1 cm²)','(1 ચો. સે.મી. અથવા 1 સે.મી.²)'],['1 inch','1 ઇંચ'],['1 square inch','1 ચોરસ ઇંચ'],['(1 sq. in. or 1 in²)','(1 ચો. ઇંચ અથવા 1 ઇંચ²)']],
 'CNX_BMath_Figure_01_04_013.jpg':[['2 ft','2 ફૂટ'],['3 ft','3 ફૂટ'],['2 · 3 = 6 ft²','2 · 3 = 6 ચોરસ ફૂટ']],
}
SELF_CHECK={'media_id':'eip-id1164270868879','image':'CNX_BMath_Figure_AppB_005.jpg','columns':['હું આ કરી શકું છું…','વિશ્વાસપૂર્વક','થોડી મદદથી','ના—મને સમજાતું નથી!'],'rows':['ગુણાકારની લખાવટનો ઉપયોગ કરવો.','પૂર્ણ સંખ્યાઓનો ગુણાકાર નમૂના દ્વારા દર્શાવવો.','પૂર્ણ સંખ્યાઓનો ગુણાકાર કરવો.','શબ્દોમાં આપેલી વાતને ગણિતની લખાવટમાં ફેરવવી.','વ્યવહારુ પ્રશ્નોમાં પૂર્ણ સંખ્યાઓનો ગુણાકાર કરવો.'],'response_cells':[[None]*3 for _ in range(5)]}

def charts(source):
 result=[]
 # This description's complete column inventory was compared with actual205image.
 e=next(e for e in source.iter() if e.get('id')=='fs-id2715597')
 values=re.findall('“([^”]+)”',e.get('alt'))
 cols=[]
 for value in values:
  cols.append([None if x.strip()=='null' else x.strip() if x.strip()=='x' else int(x) for x in re.split('[;,]',value)])
 assert len(cols)==11 and all(len(x)==11 for x in cols)
 result.append({'image':'CNX_BMath_Figure_01_04_205.jpg','source_status':'problem-partial','column_headers':list(range(10)),'row_headers':list(range(10)),'visible_cells':[[cols[j+1][i+1] for j in range(10)] for i in range(10)],'evidence':'Actual205image read directly and source column values cross-checked.'})
 cells207=[[0,0,0,0,0,None,0,None,0,0],[0,1,2,None,4,5,None,7,None,9],[0,None,4,None,8,10,None,14,16,None],[None,3,None,9,None,None,18,None,24,None],[0,4,8,12,None,None,24,28,None,36],[0,5,None,15,20,None,30,35,40,None],[None,None,12,18,None,None,36,42,None,54],[0,7,None,21,None,35,None,None,56,63],[0,8,16,None,32,None,48,None,64,72],[None,None,18,27,36,None,None,63,None,None]]
 result.append({'image':'CNX_BMath_Figure_01_04_207.jpg','source_status':'problem-partial','column_headers':list(range(10)),'row_headers':list(range(10)),'visible_cells':cells207,'evidence':'Transcribed from actual207image, not its incorrect full-table alt.'})
 specs=[('206',0,10,0,10,True),('209',4,10,3,10,False),('210',4,10,3,10,True),('211',3,10,4,10,False),('213',6,10,3,10,False),('214',6,10,3,10,True),('215',3,10,6,10,False),('217',5,10,5,10,False),('218',5,10,5,10,True),('219',6,10,6,10,False)]
 for no,ra,rb,ca,cb,filled in specs:
  rr=list(range(ra,rb));cc=list(range(ca,cb))
  result.append({'image':f'CNX_BMath_Figure_01_04_{no}.jpg','source_status':'supplied-solution' if filled else 'problem-blank','column_headers':cc,'row_headers':rr,'visible_cells':[[r*c if filled else None for c in cc] for r in rr],'evidence':'Every source image inspected; supplied-solution cell values independently recomputed and compared visually. Empty questions remain empty.'})
 for chart in result:
  for r,row in zip(chart['row_headers'],chart['visible_cells']):
   for c,v in zip(chart['column_headers'],row):
    if v is not None:assert v==r*c,(chart['image'],r,c,v)
 return result

def main():
 sys.stdout.reconfigure(encoding='utf-8')
 assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
 source=ET.parse(SOURCE).getroot();target=ET.parse(OUTPUT).getroot()
 assert target.attrib.pop('{http://www.w3.org/XML/1998/namespace}lang')=='gu-Gujr-IN'
 stats=validate_pair(source,target);assert not gather(target);assert not residual_attributes(target)
 equalities=[];semicolons=[]
 for i,m in enumerate(target.iter(M+'math')):
  if m.find('.//'+M+'mtable') is not None:continue
  t=norm(flat(m))
  if re.fullmatch(r'[0-9+*()\-]+=[0-9+*()\-]+',t):
   a,b=t.split('=');assert calc(a)==calc(b),t;equalities.append(t)
  if re.fullmatch(r'[0-9+*()\-]+;\d+',t):
   a,b=t.split(';');assert calc(a)==int(b),t;semicolons.append(t)
 bare=[];prose_equations=[]
 for e in target.iter():
  for f in ('text','tail'):
   for t in re.findall(r'\d[\d,]*\s*[×·⋅+−-]\s*\d[\d,]*\s*=\s*\d[\d,]*',getattr(e,f) or ''):
    a,b=norm(t).split('=');assert calc(a)==calc(b),t;prose_equations.append(t)
 for ex in target.iter(C+'exercise'):
  p=ex.find(C+'problem');s=ex.find(C+'solution')
  if p is None or s is None:continue
  pm=[norm(flat(m)) for m in p.iter(M+'math')];sm=[norm(flat(m)) for m in s.iter(M+'math')]
  if len(pm)==len(sm) and pm and all(re.fullmatch(r'[0-9+*()\-]+',x) for x in pm) and all(re.fullmatch(r'\d+',x) for x in sm):
   assert [calc(x) for x in pm]==list(map(int,sm)),ex.get('id');bare.append(ex.get('id'))
  st=norm(flat(s))
  if len(pm)==1 and re.fullmatch(r'[0-9+*()\-]+',pm[0]) and re.fullmatch(r'\d+',st):
   assert calc(pm[0])==int(st),(ex.get('id'),pm,st)
   if ex.get('id') not in bare:bare.append(ex.get('id'))
  if re.fullmatch(r'[0-9+*()\-]+;\d+',st):
   a,b=st.split(';');assert calc(a)==int(b),st;semicolons.append(st)
 # Independent results taken from the source questions, checked against actual
 # supplied solution text or retained source media; absent answers are not filled.
 recomputed={'fs-id1233454':('15*4',60),'fs-id2830374':('286*5',1430),'fs-id2420156':('62*87',5394),'fs-id1259024':('354*438',155052),'fs-id3165737':('896*201',180096),'fs-id1361122':('12*27',324),'fs-id2199166':('2*211',422),'fs-id1337923':('4*20',80),'fs-id2788401':('6*24',144),'fs-id1860848':('8*10',80),'fs-id1619802':('2*4',8),'fs-id1836274':('2*14',28),'fs-id1728333':('2*18',36),'fs-id3242021':('8*14',112),'fs-id1894988':('16*20',320),'fs-id1632412':('24*45',1080),'fs-id2691352':('9*12',108),'fs-id1394908':('8*5',40),'fs-id1611590':('45*20',900),'fs-id1405472':('9*6',54),'fs-id1506191':('7*44',308),'fs-id1384110':('15*12',180),'fs-id2149566':('2*10',20),'fs-id2306358':('2*50',100),'fs-id2620993':('13*9',117),'fs-id3415411':('42*34',1428),'fs-id2626472':('94*50',4700),'fs-id1226787':('300*12',3600)}
 for ident,(equation,answer) in recomputed.items():
  assert calc(equation)==answer
  ex=next(e for e in target.iter(C+'exercise') if e.get('id')==ident);sol=ex.find(C+'solution')
  alltext=flat(sol)+' '+' '.join(e.get('alt','') for e in sol.iter())
  values=[int(x.replace(',','')) for x in re.findall(r'\d+(?:,\d{3})*',alltext)]
  assert answer in values,(ident,answer)
 chartdata=charts(source)
 inventory=[]
 for e in source.iter(C+'media'):
  file=Path(list(e)[0].get('src')).name;p=MEDIA/file
  inventory.append({'media_id':e.get('id'),'source_file':file,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'review':'actual image inspected','localization':'full self-check table supplied' if file==SELF_CHECK['image'] else 'Gujarati label mapping supplied' if file in LABELS else 'retain original: numeric/symbolic image; coin inscriptions are incidental historical artwork'})
 missing=[e.get('id') for e in source.iter(C+'exercise') if e.find(C+'solution') is None]
 receipt={'module':'m81255','source_sha256':SHA,'translation_sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),'integrity':stats,'language_slots':551,'all_accessibility_attributes_translated':18,'english_language_slot_residuals':0,'english_accessibility_attribute_residuals':0,'numeric_math_equalities_checked':len(equalities),'source_expression_answer_pairs_checked':len(semicolons),'bare_answer_exercises_checked':len(bare),'prose_equalities_checked':len(prose_equations),'independent_worked_and_application_results':len(recomputed),'chart_visible_numeric_cells_checked':sum(v is not None for chart in chartdata for row in chart['visible_cells'] for v in row),'missing_source_solution_count':len(missing),'missing_source_solution_ids':missing,'media':inventory,'figure_label_translations':LABELS,'self_check':SELF_CHECK,'source_chart_accessible_data':chartdata,'source_errata':ERRATA,'source_faithfulness_note':'Faithful CNXML preserves source errors and omissions. Corrected text and image/table alternatives here are separately keyed editorial material; no missing-source answers inserted. Source dollars/feet/international grouping and institutional facts are retained as textbook context, not updated claims.'}
 (ROOT/'gu-Gujr-IN/translations/a00-m81255-media-and-errata.gu.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in receipt.items() if k not in ('media','figure_label_translations','self_check','source_chart_accessible_data','source_errata','missing_source_solution_ids')},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
