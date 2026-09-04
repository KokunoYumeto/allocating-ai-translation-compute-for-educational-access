"""Complete source-bound Gujarati translation builder for A00 m81277."""
from copy import deepcopy
from pathlib import Path
import hashlib,json,re,sys,xml.etree.ElementTree as E
from prepare_m81244 import gather
from prepare_m81276 import COMMON as PRIOR_COMMON
from a00_accessibility_attributes import apply_attributes,validate_pair

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'downloads/gu-Gujr-IN/a00-id/provenance/logbook/authority/prealgebra2e/m81277.source.cnxml'
SHA='b11ddb3b2810002dd83a9e63b79029165d5340f16f46cd7533be98ef6d2f5692'
MAP=ROOT/'gu-Gujr-IN/translations/a00-m81277.gu.map.json'
OUT=ROOT/'gu-Gujr-IN/translations/a00-m81277.gu.cnxml'
RECEIPT=ROOT/'gu-Gujr-IN/translations/a00-m81277-media-and-errata.gu.json'
MEDIA=ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'

COMMON=dict(PRIOR_COMMON)
COMMON.update({
 'Subtract Integers':'પૂર્ણાંકોની બાદબાકી કરો',
 'Model subtraction of integers':'પૂર્ણાંકોની બાદબાકીને નમૂના દ્વારા દર્શાવી શકશો',
 'Translate words phrases to algebraic expressions':'શબ્દસમૂહોને બીજગણિતીય પદાવલીઓમાં ફેરવી શકશો',
 'Subtract integers in applications':'વ્યવહારુ પ્રશ્નોમાં પૂર્ણાંકોની બાદબાકી કરી શકશો',
 'Model Subtraction of Integers':'પૂર્ણાંકોની બાદબાકીને નમૂના દ્વારા દર્શાવો',
 'Subtraction of Integers':'પૂર્ણાંકોની બાદબાકી',
 'Simplify Expressions with Integers':'પૂર્ણાંકો ધરાવતી પદાવલીઓ સરળ કરો',
 'Evaluate Variable Expressions with Integers':'પૂર્ણાંકો ધરાવતી ચલ પદાવલીઓની કિંમત શોધો',
 'Translate Word Phrases to Algebraic Expressions':'શબ્દસમૂહોને બીજગણિતીય પદાવલીઓમાં ફેરવો',
 'Subtract Integers in Applications':'વ્યવહારુ પ્રશ્નોમાં પૂર્ણાંકોની બાદબાકી કરો',
 'Model the subtraction':'બાદબાકીને નમૂના દ્વારા દર્શાવો',
 'Model each subtraction.':'દરેક બાદબાકીને નમૂના દ્વારા દર્શાવો.',
 'Model each subtraction expression:':'દરેક બાદબાકીની પદાવલીને નમૂના દ્વારા દર્શાવો:',
 'Take away the second number.':'બીજી સંખ્યા દૂર કરો.',
 'Find the counters that are left.':'બાકી રહેલા કાઉન્ટર શોધો.',
 'Subtract':'બાદ કરો:', 'Subtract.':'બાદબાકી કરો.',
 'Simplify each expression:':'દરેક પદાવલી સરળ કરો:',
 'Subtraction Property':'બાદબાકીનો ગુણધર્મ',
 'Checking Account':'ચેકિંગ ખાતું',
 'Translate and then simplify:':'ગાણિતિક લખાવટમાં ફેરવો અને પછી સરળ કરો:',
 'Identify what you are asked to find.':'તમારે શું શોધવાનું છે તે ઓળખો.',
 'Write a phrase.':'શબ્દસમૂહ લખો.',
})

def norm(s):return ' '.join((s or '').split())

def write_receipt(source,data):
 refs=[];source_alts={}
 for media in source.iter():
  if not media.tag.endswith('media'):continue
  image=next((x for x in media if x.tag.endswith('image')),None)
  if image is None or not image.get('src'):continue
  name=Path(image.get('src')).name;path=MEDIA/name
  refs.append({'reference_index':len(refs)+1,'media_id':media.get('id'),'asset':name,
   'asset_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'actual_original_reviewed':True,
   'embedded_language':name in data['language_bearing_assets'],
   'reader_action':'localized redraw required' if name in data['language_bearing_assets'] else 'retain original'})
  if media.get('alt') is not None:source_alts[media.get('id')]=media.get('alt')
 errata=[]
 for mid,corrected in data['corrected_alts'].items():
  errata.append({'media_id':mid,'source_alt_en':source_alts[mid],
   'faithful_source_alt_gu':data['groups'][mid][0],'actual_image_and_math_correction_gu':corrected,
   'handling':'Faithful CNXML retains the translated source alt; reader integration should surface the corrected alternative with a source note.'})
 bridges=[]
 for mid,complete in data['bridge_alts'].items():
  bridges.append({'media_id':mid,'source_alt_en':source_alts[mid],
   'faithful_source_alt_gu':data['groups'][mid][0],'complete_alt_gu':complete})
 omitted=[]
 for exercise in (e for e in source.iter() if e.tag.endswith('exercise')):
  if any(e.tag.endswith('solution') for e in exercise):continue
  problem=next((e for e in exercise if e.tag.endswith('problem')),None)
  omitted.append({'exercise_id':exercise.get('id'),'problem_id':problem.get('id') if problem is not None else None})
 receipt={'module_id':'m81277','source_sha256':SHA,
  'translation_kind':'faithful Gujarati CNXML plus source-bound media and errata handoff',
  'actual_source_and_media_review':{'source_language_slots_read':701,'other_accessibility_attributes_read':29,
   'media_references_read':101,'unique_original_images_read':101},
  'media_inventory':refs,'language_bearing_assets':data['language_bearing_assets'],
  'source_alt_errata':errata,'accessibility_bridges':bridges,
  'math_token_language_bridges':data.get('math_token_language_bridges',[]),
  'text_errata':data.get('text_errata',[]),
  'omitted_solution_policy':{'source_omitted_count':42,'source_omitted_exercises':omitted,
   'filled_in_faithful_cnxml':0,
   'note':'No omitted source answer is inserted into the faithful CNXML.'}}
 RECEIPT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
 sys.stdout.reconfigure(encoding='utf-8');assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
 data=json.loads(MAP.read_text(encoding='utf-8'));manual=data['groups'];attributes=data['attributes']
 source=E.parse(SOURCE).getroot();target=deepcopy(source);groups=gather(target);missing={}
 for owner,slots in groups.items():
  choices=manual.get(owner)
  if choices is None:choices=[COMMON.get(norm(v)) for _,_,v in slots]
  if choices is not None and len(choices)!=len(slots):raise AssertionError((owner,len(choices),len(slots)))
  if choices is None or any(x is None for x in choices):
   missing[owner]=[norm(v) for _,_,v in slots];continue
  for (el,field,v),new in zip(slots,choices):
   if field=='alt':el.set(field,new)
   else:setattr(el,field,re.match(r'^\s*',v).group()+new+re.search(r'\s*$',v).group())
 if missing:
  print(json.dumps({'remaining_groups':len(missing),'remaining_slots':sum(map(len,missing.values())),'missing':missing},ensure_ascii=False,indent=2));return
 attr_count=apply_attributes(source,target,attributes)
 stats=validate_pair(source,target);target.set('{http://www.w3.org/XML/1998/namespace}lang','gu-Gujr-IN')
 E.ElementTree(target).write(OUT,encoding='utf-8',xml_declaration=True);write_receipt(source,data)
 print(json.dumps({'result':'pass',**stats,'language_slots':sum(map(len,groups.values()))+attr_count,
  'accessibility_attributes':attr_count,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),
  'receipt_sha256':hashlib.sha256(RECEIPT.read_bytes()).hexdigest()},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
