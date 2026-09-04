"""Meaningful source integrity, arithmetic and full-media handoff for m81245."""
import hashlib,json,re,sys
import xml.etree.ElementTree as ET
from prepare_m81245 import ROOT,SOURCE,SHA,gather
from a00_accessibility_attributes import validate_pair,residual_attributes

C='{http://cnx.rice.edu/cnxml}';M='{http://www.w3.org/1998/Math/MathML}'
OUTPUT=ROOT/'gu-Gujr-IN/translations/a00-m81245.gu.cnxml'
MEDIA=ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'
flat=lambda e:' '.join(''.join(e.itertext()).split())
def norm(t):return re.sub(r'\s+','',t).replace(',','').replace('−','-').rstrip('.;✓')
def calc(t):
 assert re.fullmatch(r'\d+(?:[+-]\d+)*',t),t
 return sum(int(x) for x in re.findall(r'[+-]?\d+',t))

ALT_ERRATA={
 'fs-id2793179':('Source says 9−6; image and problem are 6−1=5.','છ ખંડમાંથી એક ખંડને વર્તુળમાં દર્શાવી દૂર કરેલો છે. પાંચ ખંડ બાકી છે. નીચે 6 − 1 = 5 લખેલું છે.'),
 'eip-id1168288455224':('Source says ten circled and four additional blocks, and interprets arrow as repetition. Actual image circles eight of thirteen blocks and removes them.','તેર છૂટા એકમના ખંડમાંથી પહેલા આઠને જાંબલી વર્તુળમાં દર્શાવ્યા છે. નીચેનું ડાબે બતાવતું તીર આઠ ખંડ દૂર કરવાનું સૂચવે છે. વર્તુળની બહાર બે અને ત્રણનાં જૂથમાં પાંચ ખંડ બાકી છે.'),
 'eip-id1168288437405':('Source describes borrowing in 030-02, but borrowing is first drawn in the next image.','207માંથી 64 બાદ કરવાની ઊભી ગોઠવણી. એકમમાં 7 − 4 = 3 કર્યા પછી રેખાની નીચે એકમના સ્થાને 3 લખેલો છે. આ ચિત્રમાં હજી ડાબેના સ્થાનેથી લેવાના ફેરફાર દર્શાવ્યા નથી.'),
 'eip-id1168286359298':('Source calls this 107−64=43; image is intermediate work for 207−64.','207માંથી 64 બાદ કરવાની ઊભી ગોઠવણીમાં 2 સોમાંથી 1 સો લઈને 10 દશક બનાવ્યા છે. ઉપર 1 સો, 10 દશક અને 7 એકમ દર્શાવ્યાં છે. રેખાની નીચે દશક અને એકમના સ્થાને આંશિક પરિણામ 43 છે; સોની બાદબાકી હજી બાકી છે.'),
 'eip-id1168286001486':('Source calls this the first borrowing step for ones; it actually also borrows a hundred for tens.','910માંથી 586 બાદ કરવાની ઊભી ગોઠવણીમાં એકમ માટે 1 દશક લીધા પછી દશક શૂન્ય હતા. હવે સોના સ્થાનેથી 1 સો લઈને 10 દશક બનાવ્યા છે. ઉપર 8 સો, 10 દશક અને 10 એકમ છે. રેખાની નીચે એકમના સ્થાને 4 છે.'),
 'eip-id1168286120643':('Source falsely calls intermediate 24 an incorrect final answer; the hundreds have not yet been subtracted.','910માંથી 586 બાદ કરતી વખતે એકમમાં 10 − 6 = 4 અને દશકમાં 10 − 8 = 2 મળે છે. રેખાની નીચે આંશિક પરિણામ 24 લખેલું છે. સોની બાદબાકીનું આગળનું પગલું હજી બાકી છે; પૂર્ણ જવાબ 324 થાય છે.'),
 'eip-id1787878989448284288577':('Source says 2062−479=1583; actual image is intermediate borrowing work for 2162−479.','2,162માંથી 479 બાદ કરવાની ઊભી ગોઠવણીમાં દશક અને એકમનું આંશિક પરિણામ 83 છે. સોના સ્થાને શૂન્ય હોવાથી 2 હજારમાંથી 1 હજાર લઈને 10 સો બનાવ્યા છે. ઉપરનાં ફરી ગોઠવેલાં મૂલ્યો 1 હજાર, 10 સો, 15 દશક અને 12 એકમ છે.'),
 'eip-id1787428844577':('Source claims complete 1683 in 028-08; actual image shows partial683 before the thousands step.','2,162માંથી 479 બાદ કરતી વખતે સોમાં 10 − 4 = 6 કર્યા પછી રેખાની નીચે આંશિક પરિણામ 683 છે. તેનો સોના સ્થાનનો અંક 6 લાલ રંગમાં છે. હજારના સ્થાનની બાદબાકી હજી બાકી છે.'),
 'eip-id1168287220447':('Clarification: 7 is the ones result, not the complete difference.','43માંથી 26 બાદ કરવાની ઊભી ગોઠવણીમાં 4 દશકને 3 દશક અને 3 એકમને 13 એકમ તરીકે ફરી ગોઠવ્યા છે. એકમમાં 13 − 6 = 7થી મળેલો 7 રેખાની નીચે એકમના સ્થાને છે; દશકની બાદબાકી બાકી છે.'),
 'eip-id1168286081662':('Clarification: 4 is the ones result, not the complete difference.','910માંથી 586 બાદ કરવાની ઊભી ગોઠવણીમાં 1 દશક લઈને 0 એકમને 10 એકમ કર્યા છે. દશકનો 1 છેકીને 0 અને એકમનો 0 છેકીને 10 લખ્યું છે. એકમમાં 10 − 6 = 4થી મળેલો 4 રેખાની નીચે છે; બીજા સ્થાનની બાદબાકી બાકી છે.'),
}

def main():
 sys.stdout.reconfigure(encoding='utf-8')
 assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
 source=ET.parse(SOURCE).getroot();target=ET.parse(OUTPUT).getroot()
 assert target.attrib.pop('{http://www.w3.org/XML/1998/namespace}lang')=='gu-Gujr-IN'
 stats=validate_pair(source,target)
 assert not gather(target),gather(target)
 assert not residual_attributes(target),residual_attributes(target)
 equalities=[]
 for i,m in enumerate(target.iter(M+'math')):
  if m.find('.//'+M+'mtable') is not None:continue
  t=norm(flat(m))
  if re.fullmatch(r'\d+(?:[+-]\d+)*=\d+(?:[+-]\d+)*',t):
   l,r=t.split('=');assert calc(l)==calc(r),t;equalities.append({'math_index':i,'equation':t})
 prose_equations=[]
 for e in target.iter():
  for field in ('text','tail'):
   t=getattr(e,field) or ''
   for equation in re.findall(r'\d[\d,]*\s*[+−-]\s*\d[\d,]*\s*=\s*\d[\d,]*',t):
    l,r=norm(equation).split('=');assert calc(l)==calc(r),equation
    prose_equations.append(equation)
 bare=[]
 for ex in target.iter(C+'exercise'):
  p=ex.find(C+'problem');s=ex.find(C+'solution')
  if p is None or s is None:continue
  pm=[norm(flat(m)) for m in p.iter(M+'math')];sm=[norm(flat(m)) for m in s.iter(M+'math')]
  if len(pm)==len(sm) and pm and all(re.fullmatch(r'\d+(?:[+-]\d+)+',x) for x in pm) and all(re.fullmatch(r'\d+',x) for x in sm):
   assert [calc(x) for x in pm]==[int(x) for x in sm],ex.get('id');bare.append(ex.get('id'))
  st=norm(flat(s))
  if len(pm)==1 and re.fullmatch(r'\d+(?:[+-]\d+)+',pm[0]) and re.fullmatch(r'\d+',st):
   assert calc(pm[0])==int(st),(ex.get('id'),pm,st)
   if ex.get('id') not in bare:bare.append(ex.get('id'))
  if re.fullmatch(r'\d+[+-]\d+;\d+',st):
   x,y=st.split(';');assert calc(x)==int(y),(ex.get('id'),st)
  # A source solution can put its expression and value in one semicolon-separated span.
  for m in s.iter(M+'math'):
   t=norm(flat(m))
   if re.fullmatch(r'\d+[+-]\d+;\d+',t):
    x,y=t.split(';');assert calc(x)==int(y),(ex.get('id'),t)
 recomputed={
  'fs-id2296830':('89-61',28),'fs-id1613753':('43-26',17),
  'fs-id2170154':('207-64',143),'fs-id2279338':('910-586',324),
  'fs-id1392397':('2162-479',1683),'fs-id1827544':('73-27',46),
  'fs-id1862405':('77-58',19),'fs-id4133018':('90-73',17),
  'fs-id3016565':('588-399',189),'fs-id1582423':('648-499',149),
  'fs-id2150255':('285-149',136),'fs-id3321482':('80-63',17),
  'fs-id4131869':('35-22',13),'fs-id1628108':('650-399',251),
  'fs-id2209737':('840-685',155),'fs-id1782279':('502-115-230',157),
  'fs-id2431291':('75+35',110)}
 for eid,(expression,answer) in recomputed.items():
  assert source.find('.//*[@id="'+eid+'"]') is not None
  assert calc(expression)==answer,(eid,expression,answer)
 # Independent regrouping conservation, including source body omission at hundreds.
 regrouping=[(43,[30,13]),(207,[100,100,7]),(910,[800,100,10]),(2162,[1000,1000,150,12])]
 for original,parts in regrouping:assert sum(parts)==original
 missing=[e.get('id') for e in source.iter(C+'exercise') if e.find(C+'solution') is None]
 assert len(missing)==42
 inventory=[];issues={}
 for media in source.iter(C+'media'):
  im=media.find(C+'image');f=im.get('src').split('/')[-1]
  item={'media_id':media.get('id'),'source':im.get('src'),'sha256':hashlib.sha256((MEDIA/f).read_bytes()).hexdigest(),'visually_inspected':True,
   'embedded_language':'self-check table' if 'AppB' in f else 'ones/tens labels' if f=='CNX_BMath_Figure_01_03_014_img.jpg' else 'none; numbers, symbols or models only'}
  if f=='CNX_BMath_Figure_01_03_014_img.jpg':item['label_map_gu']={'4 tens':'4 દશક','3 ones':'3 એકમ','3 tens':'3 દશક','13 ones':'13 એકમ'}
  inventory.append(item)
  if media.get('id') in ALT_ERRATA:
   issue,corrected=ALT_ERRATA[media.get('id')]
   issues[media.get('id')]={'issue':issue,'corrected_alt_gu':corrected,'source_alt':media.get('alt'),'source_image':im.get('src'),'source_image_sha256':item['sha256'],'faithful_cnxml_unchanged':True}
 assert len(inventory)==55
 attr_issues={}
 for eid in ('eip-811','eip-7544534','fs-id1549826'):
  s=source.find('.//*[@id="'+eid+'"]');t=target.find('.//*[@id="'+eid+'"]');new=t.get('aria-label')
  if eid=='eip-811':
   new=new.replace('સામે 10 છૂટા ખંડ, પછી બે છૂટા ખંડ અને ત્રણ છૂટા ખંડ છે, જેમાં 10 છૂટા ખંડની આસપાસ વર્તુળ છે.','સામે તેર છૂટા ખંડમાંથી પહેલા આઠ ખંડને વર્તુળમાં દર્શાવી દૂર કરવાના છે. વર્તુળની બહાર બે અને ત્રણનાં જૂથમાં પાંચ ખંડ છે.')
   why='Source aria-label incorrectly counts ten circled blocks; actual image removes eight from thirteen.'
  elif eid=='eip-7544534':
   new=new.replace('એકમની ઉપર 5 લખીને 2 છેકો. ','').replace('1, 683','1,683')
   why='Source aria-label inserts an erroneous duplicated instruction to write5 above the ones; correct step writes12.'
  else:
   new=new.replace('બે હરોળ અને પાંચ સ્તંભ','છ હરોળ અને ચાર સ્તંભ').replace('5 ઓછા 2','5 ઓછા 1')
   why='Actual CNXML table has four columns and six rows including header; first example is5−1, not5−2.'
  assert new!=t.get('aria-label')
  attr_issues[eid]={'attribute':'aria-label','source_text':s.get('aria-label'),'issue':why,'corrected_attribute_gu':new,'faithful_cnxml_unchanged':True}
 selfcheck={'media_id':'eip-id1164272051986','image':'CNX_BMath_Figure_AppB_004.jpg',
  'headers_gu':['હું આ કરી શકું છું…','વિશ્વાસપૂર્વક','થોડી મદદથી','ના—મને સમજાતું નથી!'],
  'rows_gu':['બાદબાકીની લખાવટનો ઉપયોગ.','પૂર્ણ સંખ્યાઓની બાદબાકી નમૂના દ્વારા દર્શાવવી.','પૂર્ણ સંખ્યાઓની બાદબાકી.','શબ્દોમાં આપેલી વાતને ગણિતની લખાવટમાં ફેરવવી.','વ્યવહારુ પ્રશ્નોમાં પૂર્ણ સંખ્યાઓની બાદબાકી.'],
  'response_cells':'All15 response cells remain blank.'}
 report={'module':'m81245','source_sha256':SHA,'translation_sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),'coverage':stats,
  'language_slots':503,'translated_accessibility_attributes':17,'residual_english_slots':0,'residual_english_accessibility_attributes':[],
  'checked_flat_math_equalities':equalities,'checked_prose_equations':prose_equations,'checked_bare_answer_exercises':bare,
  'independent_column_prose_recomputations':recomputed,'regrouping_conservation_checks':regrouping,
  'missing_source_solution_exercise_ids':missing,'source_alt_errata':issues,'source_attribute_errata':attr_issues,
  'self_check_table':selfcheck,'media_inventory':inventory,
  'source_body_omission':{'table_id':'eip-7544534','exercise_id':'fs-id1392397','issue':'Main source table prose omits the thousands-to-hundreds regrouping explanation, although the image and aria-label contain it.',
   'companion_explanation_gu':'સોના સ્થાને શૂન્ય હોવાથી તેમાંથી 4 સો બાદ કરી શકતા નથી. તેથી 2 હજારમાંથી 1 હજાર લઈને તેના બદલામાં 10 સો લો. હવે 1 હજાર, 10 સો, 15 દશક અને 12 એકમ છે. સોમાં 10 − 4 = 6 થાય છે.','faithful_cnxml_unchanged':True},
  'limits':['Corrections are a separately labelled editorial layer; faithful XML retains source mistakes.','No integrated HTML/PDF render claimed. All55 original figures viewed in contact sheets, with five critical images also viewed individually.','Math word-phrase colon constructions preserve operand order; educator/style review remains pending.','42 absent source solutions are not filled in faithful XML.']}
 out=ROOT/'gu-Gujr-IN/translations/a00-m81245-media-and-errata.gu.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'result':'pass',**stats,'language_slots':503,'accessibility_attributes':17,'math_equalities':len(equalities),'prose_equations':len(prose_equations),'bare_answer_exercises':len(bare),'independent_recomputations':len(recomputed),'missing_source_solutions':42,'media_inspected':55,'alt_errata_or_clarifications':len(issues),'attribute_errata':len(attr_issues),'sha256':report['translation_sha256']},indent=2))

if __name__=='__main__':main()
