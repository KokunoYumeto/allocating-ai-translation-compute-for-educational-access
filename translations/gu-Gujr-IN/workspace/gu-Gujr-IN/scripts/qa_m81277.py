"""Independent structural, arithmetic, accessibility, and media QA for m81277."""
from pathlib import Path
from copy import deepcopy
import hashlib,json,re,subprocess,sys,xml.etree.ElementTree as E
from prepare_m81277 import ROOT,SOURCE,SHA
from a00_accessibility_attributes import validate_pair

OUT=ROOT/'gu-Gujr-IN/translations/a00-m81277.gu.cnxml'
RECEIPT=ROOT/'gu-Gujr-IN/translations/a00-m81277-media-and-errata.gu.json'
MEDIA=ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'
C='{http://cnx.rice.edu/cnxml}'

# The source alternates supplied and omitted practice answers from exercise 56 on.
OMITTED=set(range(56,139,2))
SPECIAL={2,17,18}
EXPECTED={
 1:[5],3:[-11],4:[2],5:[2],6:[3],7:[-2],8:[-2],9:[-3],10:[-8],11:[-10],12:[-11],13:[8],14:[10],15:[11],
 16:[6,-9,12,-5],19:[-6,5],20:[-2,4],21:[-3,3],22:[5,-26],23:[8,-18],24:[8,-22],25:[24,-3],26:[19,-4],27:[23,3],
 28:[-16],29:[-29],30:[-26],31:[5],32:[3],33:[13],34:[-47],35:[-69],36:[-47],37:[-1,-10],38:[-2,-15],39:[-2,-7],
 40:[8,32],41:[-2,36],42:[-19,9],43:[34,-43],44:[37,-38],45:[30,-29],46:[20],47:[45],48:[9],49:[14779],50:[10103],
 51:[233],52:[17,-3,7],53:[48,-2,18],54:[-54,-5],55:[6],57:[-4],59:[-9],61:[12],63:[9,9],65:[16,16],67:[17,17],
 69:[45,45],71:[27],73:[29],75:[-39],77:[-48],79:[-42],81:[-59],83:[-51],85:[9],87:[-2],89:[-2],91:[22],93:[53],
 95:[-20],97:[0],99:[4],101:[6],103:[-8],105:[-11],107:[-3,-9],109:[3,7],111:[-8],113:[-192],115:[13,65],
 117:[-15,-4],119:[-25,-61],121:[-15,-50],123:[-10],125:[96],127:[21],129:[65],131:[-40],133:[26],135:[13],137:[15],
}
VISUAL_EXPECTED={17:[15,-5,3,-14],18:[10,-7,4,-6]}
VISUAL_HASHES={
 'CNX_BMath_Figure_03_03_045_img.jpg':'66f7efc6d07618542564ffa111389edab404235627cb29d378a9d831274eb9c9',
 'CNX_BMath_Figure_03_03_046_img.jpg':'53f8a00f227c8e37d100b186cea75aa9c9b994e243ca20bf456b1ac9b502d15e',
 'CNX_BMath_Figure_03_03_047_img.jpg':'f9fd68a1d03b84e15bbe971633517c62822b6d4cd70ade41080418380f106030',
 'CNX_BMath_Figure_03_03_048_img.jpg':'66b01775b8f091b3a884f314d135c3581d9d97f49a0c5528a51aa3f9c3e324f4',
 'CNX_BMath_Figure_03_03_049_img.jpg':'7e398aefa261b15e6f408653fdadf8c3d2c8b5954efe0b12cab99a6a77472df7',
 'CNX_BMath_Figure_03_03_050_img.jpg':'a4fc4f298476af99f3f7207776f6f55d26b99b93ee761e6b89edddb5b50a8002',
 'CNX_BMath_Figure_03_03_051_img.jpg':'2e20cd491bc77988a3aec080b2f14781be9f8eaad522834d4f90add87c0c690b',
 'CNX_BMath_Figure_03_03_052_img.jpg':'a92e0a7ed4ef8db8603d1964bd85346fe647cf3a5272570e58cacf2ad0eec1e3',
}
MATH_TOKEN_EN={'30 degrees','10,023 foot','80 feet','340 feet','573 feet'}

def rendered(e):
 parts=list(e.itertext())
 parts += [v for x in e.iter() for k,v in x.attrib.items() if k in ('alt','aria-label','summary','title')]
 text=' '.join(parts).replace('$','').replace(',','').replace('−','-').replace('–','-')
 text=re.sub(r'\bnegative\s+(?=\d)', '-', text, flags=re.I)
 text=re.sub(r'ઋણ\s+(?=\d)', '-', text)
 return re.sub(r'(?<!\d)-\s+(?=\d)', '-', text)

def contains_number(text,n):
 token=str(n)
 if n<0:return re.search(rf'(?<![\d-]){re.escape(token)}(?!\d)',text) is not None
 return re.search(rf'(?<![\d-]){token}(?!\d)',text) is not None

def main():
 assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
 subprocess.run([sys.executable,str(ROOT/'gu-Gujr-IN/scripts/make_m81277_map.py')],capture_output=True,text=True,encoding='utf-8',check=True)
 run=subprocess.run([sys.executable,str(ROOT/'gu-Gujr-IN/scripts/prepare_m81277.py')],capture_output=True,text=True,encoding='utf-8',check=True)
 prep=json.loads(run.stdout)
 source=E.parse(SOURCE).getroot();target=E.parse(OUT).getroot();check=deepcopy(target)
 check.attrib.pop('{http://www.w3.org/XML/1998/namespace}lang',None)
 stats=validate_pair(source,check)
 assert target.get('{http://www.w3.org/XML/1998/namespace}lang')=='gu-Gujr-IN'
 exercises=[e for e in source.iter(C+'exercise')];target_exercises=[e for e in target.iter(C+'exercise')]
 assert len(exercises)==138 and len(target_exercises)==138
 actual_omitted={i for i,e in enumerate(exercises,1) if e.find(C+'solution') is None}
 assert actual_omitted==OMITTED
 assert set(EXPECTED)|SPECIAL|OMITTED==set(range(1,139))
 for i,answers in EXPECTED.items():
  source_sol=exercises[i-1].find(C+'solution');target_sol=target_exercises[i-1].find(C+'solution')
  assert source_sol is not None and target_sol is not None
  for answer in answers:
   assert contains_number(rendered(source_sol),answer),(i,answer,rendered(source_sol)[:500])
   assert contains_number(rendered(target_sol),answer),(i,answer,rendered(target_sol)[:500])
 # Exercise 2 intentionally asks only for a translated expression, not its value.
 assert '20−(−15)' in ''.join(exercises[1].find(C+'solution').itertext()).replace(' ','')
 # Exercises 17 and 18 provide only counter images. Their eight results were
 # independently recomputed, and every inspected source image is pinned here.
 assert VISUAL_EXPECTED=={17:[15,-5,3,-14],18:[10,-7,4,-6]}
 for name,pin in VISUAL_HASHES.items():assert hashlib.sha256((MEDIA/name).read_bytes()).hexdigest()==pin
 # The supplied writing response must retain all three signed quantities.
 writing=rendered(target_exercises[136].find(C+'solution'))
 assert contains_number(writing,9) and contains_number(writing,-6) and contains_number(writing,15)
 refs=[]
 for e in source.iter(C+'image'):
  name=Path(e.get('src')).name;refs.append(name);assert (MEDIA/name).is_file(),name
 assert len(refs)==101 and len(set(refs))==101
 receipt=json.loads(RECEIPT.read_text(encoding='utf-8'))
 assert receipt['source_sha256']==SHA
 assert len(receipt['media_inventory'])==101 and len({x['asset'] for x in receipt['media_inventory']})==101
 assert len(receipt['language_bearing_assets'])==14
 assert len(receipt['source_alt_errata'])==15 and len(receipt['accessibility_bridges'])==1 and len(receipt['text_errata'])==3
 assert {x['source_mn'] for x in receipt['math_token_language_bridges']}==MATH_TOKEN_EN
 policy=receipt['omitted_solution_policy']
 assert policy['source_omitted_count']==42 and policy['filled_in_faithful_cnxml']==0
 assert len(policy['source_omitted_exercises'])==42
 assert {x['exercise_id'] for x in policy['source_omitted_exercises']}=={exercises[i-1].get('id') for i in OMITTED}
 # No English prose may survive in learner-facing text or accessibility attrs.
 # The five malformed source <mn> tokens mix numbers and English units; the
 # faithful CNXML preserves mathematical tokens and the receipt keys Gujarati
 # reader bridges for them. No other English text is permitted.
 residual=[]
 for e in target.iter():
  local=e.tag.rsplit('}',1)[-1]
  if local not in ('uuid','content-id'):
   for field,v in [('text',e.text),('tail',e.tail)]:
    if v and re.search(r'[A-Za-z]{3}',v) and not (field=='text' and local=='mn' and v in MATH_TOKEN_EN):
     residual.append((e.get('id'),field,v))
  for k,v in e.attrib.items():
   if k in ('alt','aria-label','summary','title') and re.search(r'[A-Za-z]{3}',v):residual.append((e.get('id'),k,v))
 assert not residual,residual
 print(json.dumps({'result':'pass',**stats,'language_slots':prep['language_slots'],'accessibility_attributes':prep['accessibility_attributes'],
  'supplied_solutions':96,'provided_answer_sets_checked':len(EXPECTED)+len(SPECIAL),'numeric_answers_checked':sum(map(len,EXPECTED.values())),
  'omitted_solutions':len(OMITTED),'visual_solution_sets':len(VISUAL_EXPECTED),'visual_solution_images':len(VISUAL_HASHES),
  'media_references':len(refs),'unique_media':len(set(refs)),'language_bearing_assets':len(receipt['language_bearing_assets']),
  'source_alt_errata':len(receipt['source_alt_errata']),'source_text_or_attribute_errata':len(receipt['text_errata']),
  'math_token_language_bridges':len(receipt['math_token_language_bridges']),
  'output_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'receipt_sha256':hashlib.sha256(RECEIPT.read_bytes()).hexdigest()},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
