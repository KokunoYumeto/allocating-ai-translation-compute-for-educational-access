from pathlib import Path
import xml.etree.ElementTree as E,json,hashlib,re
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82460/index.cnxml'
GU=Path(__file__).with_name('a10-m82460.gu.cnxml')
MEDIA=ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'
OUT=ROOT/'gu-Gujr-IN/reviews/a10-m82460-media-inventory.json'
C='{http://cnx.rice.edu/cnxml}'
lang={'fs-id1170654036108','fs-id1170653797753','fs-id1170653797768','fs-id1170654084441'}
def main():
 s=E.parse(SRC).getroot();g=E.parse(GU).getroot();gs={x.get('id'):x for x in g.iter()if x.get('id')};rows=[]
 for n,e in enumerate(s.iter(C+'media')):
  src=e.find(C+'image').get('src');f=MEDIA/Path(src).name;assert f.exists()
  i=e.get('id');islang=i in lang
  rows.append({'index':n,'source_media':i,'source_asset':src,'original_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'source_alt':e.get('alt'),'alt_gu':gs[i].get('alt'),'image_review':'actual unchanged original individually viewed; expressions, arrows, highlights, signs, fractions and embedded English compared with source alternative','localization':'Gujarati redraw needed' if islang else 'Retain mathematical-only original','embedded_english':'question/statement English' if i in lang-{'fs-id1170654084441'} else 'self-check table English' if i=='fs-id1170654084441' else '','keyed_erratum':False})
 assert len(rows)==17 and sum(bool(x['embedded_english'])for x in rows)==4
 d={'module':'m82460','translation_sha256':hashlib.sha256(GU.read_bytes()).hexdigest(),'actual_images_reviewed':17,'language_bearing':4,'mathematical_only':13,'media':rows}
 OUT.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('Inventory',len(rows),'language',4,'math',13)
if __name__=='__main__':main()

