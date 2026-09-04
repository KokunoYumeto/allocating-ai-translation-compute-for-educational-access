"""Reproduce the all-original m82461 media inventory after visual review."""
from pathlib import Path
import xml.etree.ElementTree as E,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82461/index.cnxml'
GU=Path(__file__).with_name('a10-m82461.gu.cnxml')
MEDIA=ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'
OUT=ROOT/'gu-Gujr-IN/reviews/a10-m82461-media-inventory.json'
C='{http://cnx.rice.edu/cnxml}'
LANG_INDEX=set(range(18))|{19,25,26,28,30,35,39}
def main():
 s=E.parse(SRC).getroot();g=E.parse(GU).getroot();gs={x.get('id'):x for x in g.iter()if x.get('id')}
 errata=json.loads(GU.with_name('a10-m82461-errata.gu.json').read_text(encoding='utf8'))['entries'];rows=[]
 for n,e in enumerate(s.iter(C+'media')):
  src=e.find(C+'image').get('src');f=MEDIA/Path(src).name;assert f.exists()
  i=e.get('id');islang=n in LANG_INDEX
  if n<=17:embedded='English unit words and/or worked-step prose'
  elif n==19:embedded='English decimal-shift instruction'
  elif n==25:embedded='English “inch” scale label'
  elif n==26:embedded='English CUPS label and unit abbreviations'
  elif n==28:embedded='English thermometer headings and state labels'
  elif n in {30,35}:embedded='English substitution instruction'
  elif n==39:embedded='English self-check table'
  else:embedded=''
  rows.append({'index':n,'source_media':i,'source_asset':src,'original_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'source_alt':e.get('alt'),'alt_gu':gs[i].get('alt'),'image_review':'actual unchanged original individually opened at original detail; all visible values, units, arrows, cancellations, scale labels and color emphasis compared with source and Gujarati alternatives','localization':'Gujarati redraw needed'if islang else'Retain mathematical-only original','embedded_english':embedded,'keyed_erratum':i in errata})
 assert len(rows)==44 and sum(bool(x['embedded_english'])for x in rows)==25
 d={'module':'m82461','translation_sha256':hashlib.sha256(GU.read_bytes()).hexdigest(),'actual_images_reviewed':44,'language_bearing':25,'mathematical_only':19,'media':rows}
 OUT.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
 print('Inventory',len(rows),'language',25,'math',19)
if __name__=='__main__':main()
