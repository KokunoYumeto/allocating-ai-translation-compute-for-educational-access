"""Source-bound complete chapter introduction, including attribution and alt."""
from copy import deepcopy
import hashlib,json,re,sys,xml.etree.ElementTree as E
from pathlib import Path
from prepare_m81244 import gather
from a00_accessibility_attributes import validate_pair,LANGUAGE_ATTRS
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'downloads/gu-Gujr-IN/a00-id/provenance/logbook/authority/prealgebra2e/m81274.source.cnxml'
SHA='098c31928c9718bd11e923247cbb305e02338e1a3772968c7c8524af8faabae4'
GROUPS={
 'document':['પૂર્ણાંકોનો પરિચય','પૂર્ણાંકોનો પરિચય'],
 'fs-idm221482352':['તસવીરમાં બરફથી ઢંકાયેલી પર્વતમાળા દેખાય છે.'],
 'CNX_BMath_Figure_03_00_001':['માઉન્ટ એવરેસ્ટનું શિખર. (શ્રેય: Gunther Hagleitner, Flickr)'],
 'fs-id2348704':['29,000 ફૂટ કરતાં વધુ ઊંચાઈએ આવેલો માઉન્ટ એવરેસ્ટ જમીન પરનું સૌથી ઊંચું શિખર છે. નેપાળ અને ચીનની સરહદે આવેલો માઉન્ટ એવરેસ્ટ તેની અત્યંત કઠોર આબોહવા માટે પણ જાણીતો છે. શિખરની નજીક તાપમાન થીજવાના તાપમાનથી ઉપર કદી જતું નથી. દર વર્ષે વિશ્વભરના પર્વતારોહકો આ પ્રચંડ ઊંચાઈ સર કરવાના પ્રયાસમાં અત્યંત કઠિન પરિસ્થિતિઓનો સામનો કરે છે. તેમાંથી માત્ર કેટલાક જ સફળ થાય છે. પર્વતારોહકો અનુભવતા ઊંચાઈના મોટા ફેરફારો અને તાપમાનના ફેરફારો વર્ણવવા માટે શૂન્યથી ઉપર અને નીચે બંને તરફ વિસ્તરતી સંખ્યાઓ વાપરવી જરૂરી છે. આ પ્રકરણમાં આપણે આ પ્રકારની સંખ્યાઓ અને તેમની સાથે કરવામાં આવતી ક્રિયાઓ વર્ણવીશું.'],
}
def main():
 sys.stdout.reconfigure(encoding='utf-8');assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
 source=E.parse(SOURCE).getroot();target=deepcopy(source);slots=gather(target)
 assert set(slots)==set(GROUPS)
 for key,group in slots.items():
  assert len(group)==len(GROUPS[key])
  for (e,field,old),new in zip(group,GROUPS[key]):
   if field=='alt':e.set(field,new)
   else:setattr(e,field,new)
 stats=validate_pair(source,target);target.set('{http://www.w3.org/XML/1998/namespace}lang','gu-Gujr-IN')
 out=ROOT/'gu-Gujr-IN/translations/a00-m81274.gu.cnxml';E.ElementTree(target).write(out,encoding='utf-8',xml_declaration=True)
 check=E.parse(out).getroot();check.attrib.pop('{http://www.w3.org/XML/1998/namespace}lang');assert validate_pair(source,check)==stats
 for key,group in gather(check).items():
  for e,f,t in group:
   tokens=re.findall('[A-Za-z]+',t)
   assert tokens==(['Gunther','Hagleitner','Flickr']if key=='CNX_BMath_Figure_03_00_001'else[]),(key,tokens)
 for e in check.iter():
  for a in LANGUAGE_ATTRS:assert not re.search('[A-Za-z]',e.get(a,''))
 image=ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media/CNX_BMath_Figure_03_00_001.jpg'
 print(json.dumps({'result':'pass',**stats,'language_slots':sum(map(len,slots.values())),'translation_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'photo_sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'figure_policy':'Retain original viewed photograph; no embedded language. Credit names unchanged.'},indent=2))
if __name__=='__main__':main()
