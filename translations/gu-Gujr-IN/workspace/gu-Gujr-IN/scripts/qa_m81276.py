"""Independent structural, arithmetic, accessibility, and media QA for m81276."""
from pathlib import Path
from copy import deepcopy
import hashlib,json,re,subprocess,sys,xml.etree.ElementTree as E
from prepare_m81276 import ROOT,SOURCE,SHA
from a00_accessibility_attributes import validate_pair

OUT=ROOT/'gu-Gujr-IN/translations/a00-m81276.gu.cnxml'
RECEIPT=ROOT/'gu-Gujr-IN/translations/a00-m81276-media-and-errata.gu.json'
MEDIA=ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'
C='{http://cnx.rice.edu/cnxml}'

OMITTED={53,55,57,59,61,63,65,67,69,71,73,75,77,79,81,83,85,87,89,91,93,95,97,99,101,103,105,107,109,111,113,115}
SPECIAL={3,17,18,114}
EXPECTED={
 1:[14],2:[20],4:[8],5:[6],6:[7],7:[-8],8:[-6],9:[-7],10:[-2],11:[-2],12:[-3],13:[2],14:[2],15:[3],16:[6,3,-1,-5],
 19:[-28,8],20:[-17,57],21:[-46,26],22:[-50],23:[-50],24:[-70],25:[10],26:[13],27:[0],28:[5,-4],29:[2,-12],30:[2,-1],
 31:[-4,6],32:[-6,10],33:[-1,17],34:[6],35:[9],36:[13],37:[36],38:[196],39:[8],40:[-4],41:[-3],42:[-14],43:[-1],44:[-3],45:[-13],
 46:[5],47:[4],48:[-33],49:[32],50:[14],51:[37],52:[11],54:[-9],56:[-2],58:[1],60:[-80],62:[32],64:[-135],66:[0],68:[-22],
 70:[108],72:[-4],74:[29],76:[-18,-87],78:[-47,16],80:[-4,10],82:[-13,5],84:[-8],86:[10],88:[64],90:[121],92:[-9],94:[6],
 96:[-25],98:[-7],100:[-5],102:[7],104:[-118],106:[-8],108:[25],110:[20],112:[-32],
}
VISUAL_EXPECTED={17:[7,3,-2,-4],18:[6,4,-6,-7]}
VISUAL_HASHES={
 'CNX_BMath_Figure_03_02_039_img.jpg':'261198b6b9ead4f8154bace63d050893d2e1b14791ef922fcde60bd18e39f02e',
 'CNX_BMath_Figure_03_02_040_img.jpg':'ca2987de95c27d027a7b654538f77a25046209306022d4b859da767b5c9d45f0',
 'CNX_BMath_Figure_03_02_041_img.jpg':'1e9c778d480158ddc04663d4b6d962d3ef3cdccc7dbccb8bf2f5a5021bb74741',
 'CNX_BMath_Figure_03_02_042_img.jpg':'c8a66663f947b0b20732816d9742c06da40c6349c1f2bad681cb4766d95610da',
 'CNX_BMath_Figure_03_02_043_img.jpg':'772c5b595d464d8d9f0f5ddb5fd6be39c95630c4c7c95dceae673753176ff4c8',
 'CNX_BMath_Figure_03_02_044_img.jpg':'3d24f74272188570167638a44d87f33a2cfd7bfbf9ffc0c7bf3e86532bbe0166',
 'CNX_BMath_Figure_03_02_045_img.jpg':'ad54f4d336fac0304f751550e7a4fa62e33f81f92aca421074c96dc8787c6cc9',
 'CNX_BMath_Figure_03_02_046_img.jpg':'20af4e898d8bd10413a02590642bb76e7ac854f559804b761650811eff987b00',
}

def rendered(e):
 parts=list(e.itertext())
 parts += [v for x in e.iter() for k,v in x.attrib.items() if k in ('alt','aria-label','summary','title')]
 return ' '.join(parts).replace('$','').replace('−','-')

def contains_number(text,n):
 token=str(n)
 if n<0:return re.search(rf'(?<![\d-]){re.escape(token)}(?!\d)',text) is not None
 return re.search(rf'(?<![\d-]){token}(?!\d)',text) is not None

def main():
 assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
 run=subprocess.run([sys.executable,str(ROOT/'gu-Gujr-IN/scripts/prepare_m81276.py')],capture_output=True,text=True,encoding='utf-8',check=True)
 prep=json.loads(run.stdout)
 source=E.parse(SOURCE).getroot();target=E.parse(OUT).getroot();check=deepcopy(target)
 check.attrib.pop('{http://www.w3.org/XML/1998/namespace}lang',None)
 stats=validate_pair(source,check)
 assert target.get('{http://www.w3.org/XML/1998/namespace}lang')=='gu-Gujr-IN'
 exercises=[e for e in source.iter(C+'exercise')];target_exercises=[e for e in target.iter(C+'exercise')]
 assert len(exercises)==115
 actual_omitted={i for i,e in enumerate(exercises,1) if e.find(C+'solution') is None}
 assert actual_omitted==OMITTED
 assert set(EXPECTED)|SPECIAL|OMITTED==set(range(1,116))
 for i,answers in EXPECTED.items():
  sol=exercises[i-1].find(C+'solution');assert sol is not None
  text=rendered(sol)
  for answer in answers:assert contains_number(text,answer),(i,answer,text[:500])
 # Exercise 3 intentionally returns an unsimplified algebraic expression.
 assert '3+(−7)' in ''.join(exercises[2].find(C+'solution').itertext()).replace(' ','')
 # Exercises 17/18 provide only counter pictures. Their eight results were
 # recomputed and the exact inspected source images are pinned here.
 assert VISUAL_EXPECTED=={17:[7,3,-2,-4],18:[6,4,-6,-7]}
 for name,pin in VISUAL_HASHES.items():assert hashlib.sha256((MEDIA/name).read_bytes()).hexdigest()==pin
 # The supplied writing solution is open-ended but must retain both sign cases.
 writing=' '.join(target_exercises[113].find(C+'solution').itertext())
 assert 'ઋણ સંખ્યાઓ વધુ' in writing and 'ધન સંખ્યાઓ વધુ' in writing
 refs=[]
 for e in source.iter(C+'image'):
  name=Path(e.get('src')).name;refs.append(name);assert (MEDIA/name).is_file(),name
 assert len(refs)==72 and len(set(refs))==71
 receipt=json.loads(RECEIPT.read_text(encoding='utf-8'))
 assert receipt['source_sha256']==SHA
 assert len(receipt['media_inventory'])==72 and len({x['asset'] for x in receipt['media_inventory']})==71
 assert len(receipt['language_bearing_assets'])==12
 assert len(receipt['source_alt_errata'])==10 and len(receipt['accessibility_bridges'])==1 and len(receipt['text_errata'])==1
 assert receipt['omitted_solution_policy']['source_omitted_count']==32 and receipt['omitted_solution_policy']['filled_in_faithful_cnxml']==0
 # No English prose may survive in learner-facing text or accessibility attrs;
 # isolated algebra variables and UUID/content identifiers are allowed.
 residual=[]
 for e in target.iter():
  local=e.tag.rsplit('}',1)[-1]
  if local not in ('uuid','content-id') and not (e.tag.startswith('{http://www.w3.org/1998/Math/MathML}') and local!='mtext'):
   for field,v in [('text',e.text),('tail',e.tail)]:
    if v and re.search(r'[A-Za-z]{3}',v):residual.append((e.get('id'),field,v))
  for k,v in e.attrib.items():
   if k in ('alt','aria-label','summary','title') and re.search(r'[A-Za-z]{3}',v):residual.append((e.get('id'),k,v))
 assert not residual,residual
 print(json.dumps({'result':'pass',**stats,'language_slots':prep['language_slots'],'accessibility_attributes':prep['accessibility_attributes'],
  'supplied_solutions':83,'omitted_solutions':len(OMITTED),'numeric_solution_checks':sum(map(len,EXPECTED.values())),
  'visual_solution_sets':len(VISUAL_EXPECTED),'media_references':len(refs),'unique_media':len(set(refs)),
  'source_alt_errata':len(receipt['source_alt_errata']),'language_bearing_assets':len(receipt['language_bearing_assets']),
  'output_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'receipt_sha256':hashlib.sha256(RECEIPT.read_bytes()).hexdigest()},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
