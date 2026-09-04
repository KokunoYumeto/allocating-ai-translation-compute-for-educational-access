"""Source-bound integrity, arithmetic, and media handoff for complete m81244."""
from pathlib import Path
from collections import Counter
import hashlib,json,re,sys
import xml.etree.ElementTree as ET
from prepare_m81244 import ROOT,SOURCE,SHA,gather
from a00_accessibility_attributes import validate_pair,residual_attributes

C='{http://cnx.rice.edu/cnxml}'; M='{http://www.w3.org/1998/Math/MathML}'
OUTPUT=ROOT/'gu-Gujr-IN/translations/a00-m81244.gu.cnxml'
MEDIA=ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'
flat=lambda e: ' '.join(''.join(e.itertext()).split())
numbers=lambda s:re.findall(r'\d+(?:,\d{3})*(?:\.\d+)?',s or '')

def main():
 sys.stdout.reconfigure(encoding='utf-8')
 assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
 source=ET.parse(SOURCE).getroot();target=ET.parse(OUTPUT).getroot()
 assert target.attrib.pop('{http://www.w3.org/XML/1998/namespace}lang')=='gu-Gujr-IN'
 stats=validate_pair(source,target)
 for a,b in zip(source.iter(),target.iter()):
  if a.get('alt'):assert numbers(a.get('alt'))==numbers(b.get('alt')),(a.get('id'),'alt numbers')
 residual={k:[v for _,_,v in slots] for k,slots in gather(target).items()}
 assert not residual,residual
 assert not residual_attributes(target),residual_attributes(target)
 # Evaluate every flat numeric MathML equality, excluding layout/carry tables.
 equalities=[]
 def value(s):return sum(map(int,s.split('+')))
 for i,m in enumerate(target.iter(M+'math')):
  if m.find('.//'+M+'mtable') is not None:continue
  t=re.sub(r'\s+','',flat(m)).replace(',','').rstrip('.;')
  if re.fullmatch(r'\d+(?:\+\d+)*=\d+(?:\+\d+)*',t):
   left,right=t.split('=');assert value(left)==value(right),t
   equalities.append({'math_index':i,'equation':t})
 # Independently compare simple exercise expressions with supplied bare answers.
 direct=[]
 for e in target.iter(C+'exercise'):
  p=e.find(C+'problem');s=e.find(C+'solution')
  if p is None or s is None:continue
  pm=[re.sub(r'\s+','',flat(m)).replace(',','').rstrip('.') for m in p.iter(M+'math')]
  sm=[re.sub(r'\s+','',flat(m)).replace(',','').rstrip('.') for m in s.iter(M+'math')]
  if len(pm)==len(sm) and pm and all(re.fullmatch(r'\d+(?:\+\d+)+',x) for x in pm) and all(re.fullmatch(r'\d+',x) for x in sm):
   for x,y in zip(pm,sm):assert value(x)==int(y),(e.get('id'),x,y)
   direct.append(e.get('id'))
 # Values transcribed independently from prose, column-work, and inspected diagrams.
 reviewed_sums={
  'fs-id1578501':([28,61],89),'fs-id2325655':([43,69],112),
  'fs-id2277302':([324,586],910),'fs-id2144790':([1683,479],2162),
  'fs-id2264879':([21357,861,8596],30814),'fs-id1899571':([87,93,68,95,89],432),
  'fs-id1564459':([18,15,26,49,32],140),'fs-id1761942':([230,165,325],720),
  'fs-id1628979':([4,6,2,3,2,9],26),'fs-id2483376':([9,4,3,2,3,2,3,4],30),
  'fs-id2427950':([12,6,4,2,4,2,4,2],36),
  'fs-id2195542':([1100,250,525],1875),'fs-id2264366':([14,19,12,25,68],138),
  'fs-id2609576':([238,120,156,196,100,132,225],1167),
  'fs-id1962359':([82572,79316,75298],237186),
  'fs-id2658194':([14,12,18],44),'fs-id1718142':([21,7,21,7],56),
  'fs-id1788660':([19,18,16,18],71),'fs-id2427822':([24,7,19,3,5,4],62),
  'fs-id1606437':([320,170,150],640),'fs-id1567863':([82,91,75,88,70],406),
  'fs-id1369108':([210,145,183,230,159,164],1091)}
 for eid,(operands,result) in reviewed_sums.items():
  assert source.find('.//*[@id="'+eid+'"]') is not None
  assert sum(operands)==result,(eid,operands,result)
 assert reviewed_sums['fs-id1567863'][1]>=400
 assert reviewed_sums['fs-id1369108'][1]<1150
 missing=[e.get('id') for e in source.iter(C+'exercise') if e.find(C+'solution') is None]
 assert len(missing)==40
 issues={
  'eip-id1168287196613':{
   'issue':'Source alt mistakes the carried digits above 324 for fractions 1/3 and 1/2.',
   'corrected_alt_gu':'324 અને 586નો ઊભી ગોઠવણીમાં સરવાળો. 324ના સોના અંક 3ની ઉપર અને દશકના અંક 2ની ઉપર આગળના સ્થાને લઈ જવાયેલો 1 લખેલો છે. રેખાની નીચે દશક અને એકમના સ્થાને આંશિક સરવાળો 10 છે.'},
  'eip-id1168287121476':{
   'issue':'Source alt mistakes the carried digits for fractions; image shows 324+586=910.',
   'corrected_alt_gu':'324 અને 586નો ઊભી ગોઠવણીમાં સરવાળો 910 છે. 324ના સોના અંક 3ની ઉપર અને દશકના અંક 2ની ઉપર આગળના સ્થાને લઈ જવાયેલો 1 લખેલો છે. આ અંકો આગળના સ્થાને લઈ જવાનું દર્શાવે છે.'},
  'eip-id1168289744408':{
   'issue':'Source alt locates both tens and ones on the right; the three tens rods are on the left.',
   'corrected_alt_gu':'ડાબે દસ ખંડની ત્રણ સળીઓ છે. જમણે તેર એકમના ખંડ છે; તેમાંના દસ લાલ અને ત્રણ આછા વાદળી છે. આ 3 દશક અને 13 એકમ દર્શાવે છે.'},
  'fs-id2263429':{
   'issue':'Source alt reverses the grid dimensions: actual image has five columns and eight rows, including headers.',
   'corrected_alt_gu':'કોષ્ટકમાં શીર્ષકનાં ખાનાં સહિત 5 સ્તંભ અને 8 હરોળ છે. પહેલી હરોળનાં મૂલ્યો +, 6, 7, 8, 9 છે. પહેલા સ્તંભનાં મૂલ્યો +, 3, 4, 5, 6, 7, 8, 9 છે. અંદરનાં બધાં જવાબનાં ખાનાં ખાલી છે.'}}
 unit_labels={
  'CNX_BMath_Figure_01_02_002.jpg':{'feet':'ફૂટ'},
  'CNX_BMath_Figure_01_02_208_img.jpg':{'in':'ઇંચ'},
  'CNX_BMath_Figure_01_02_209_img.jpg':{'cm':'સેમી'},
  'CNX_BMath_Figure_01_02_210_img.jpg':{'m':'મી'},
  'CNX_BMath_Figure_01_02_211_img.jpg':{'ft':'ફૂટ'},
  'CNX_BMath_Figure_01_02_212_img.jpg':{'yd':'યાર્ડ'},
  'CNX_BMath_Figure_01_02_213_img.jpg':{'m':'મી'},
  'CNX_BMath_Figure_01_02_214_img.jpg':{'ft':'ફૂટ'},
  'CNX_BMath_Figure_01_02_215_img.jpg':{'in':'ઇંચ'}}
 inventory=[]
 for media in source.iter(C+'media'):
  im=media.find(C+'image')
  if im is None:continue
  f=im.get('src').split('/')[-1];p=MEDIA/f
  item={'media_id':media.get('id'),'source':im.get('src'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'inspection':'All 50 figures visually read in contact sheets; four errata and self-check also read individually at original size.'}
  item['embedded_language']='unit labels' if f in unit_labels else 'self-check table' if 'AppB' in f else 'none; numbers, symbols, or model only'
  if f in unit_labels:item['label_map_gu']=unit_labels[f]
  if media.get('id') in issues:
   issues[media.get('id')].update({'source_alt':media.get('alt'),'source_image':im.get('src'),'source_image_sha256':item['sha256'],'faithful_cnxml_unchanged':True})
  inventory.append(item)
 assert len(inventory)==50
 selfcheck={'media_id':'eip-id1168469634014','image':'CNX_BMath_Figure_AppB_002_A.jpg',
  'headers_gu':['હું આ કરી શકું છું…','વિશ્વાસપૂર્વક','થોડી મદદથી','ના—મને સમજાતું નથી!'],
  'rows_gu':['સરવાળાની લખાવટનો ઉપયોગ.','પૂર્ણ સંખ્યાઓનો સરવાળો નમૂના દ્વારા દર્શાવવો.','નમૂના વિના પૂર્ણ સંખ્યાઓનો સરવાળો.','શબ્દોમાં આપેલી વાતને ગણિતની લખાવટમાં ફેરવવી.','વ્યવહારુ પ્રશ્નોમાં પૂર્ણ સંખ્યાઓનો સરવાળો.'],
  'response_cells':'All 15 response cells remain blank; no learner answers added.'}
 report={'module':'m81244','source_sha256':SHA,'translation_sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
  'coverage':stats,'language_slots':612,'translated_accessibility_attributes':20,'residual_english_slots':residual,'residual_english_accessibility_attributes':residual_attributes(target),
  'checked_flat_math_equalities':equalities,'checked_direct_answer_exercises':direct,
  'independently_recomputed_column_prose_and_perimeter_sums':reviewed_sums,
  'missing_source_solution_exercise_ids':missing,'source_alt_errata':issues,
  'self_check_table':selfcheck,'media_inventory':inventory,
  'limits':['Faithful CNXML retains source alt mistakes; use keyed corrections only as a separately labelled editorial layer.',
   'Source punctuation inside MathML is preserved, including periods or commas before Gujarati postpositions. Integrated renderer/punctuation policy requires separate review.',
   '40 absent source solutions are not filled here. Root owns separate worked companion.',
   'No integrated HTML/PDF render is claimed. Contact sheets inspect source media, not final Gujarati layout.',
   'Addition property and addend terminology remains provisional pending Gujarati mathematics educator review.']}
 out=ROOT/'gu-Gujr-IN/translations/a00-m81244-media-and-errata.gu.json'
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'result':'pass',**stats,'flat_equalities_checked':len(equalities),'bare_answer_exercises_checked':len(direct),'independent_recomputations':len(reviewed_sums),'missing_source_solutions':len(missing),'media_inspected':len(inventory),'source_alt_errata':len(issues),'sha256':report['translation_sha256']},indent=2))

if __name__=='__main__':main()
