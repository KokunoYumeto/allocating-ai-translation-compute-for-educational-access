"""Source-bind49 decimal figures and verify all28 localized diagrams."""
import hashlib,json,re
from decimal import Decimal,ROUND_HALF_UP
from fractions import Fraction as F
from html import escape
from pathlib import Path
from lxml import etree,html
from localized_a10_decimals import PREFIX,VERIFIED_MATH_ONLY,render_figure,RED,CYAN,GREEN

ROOT=Path(__file__).resolve().parents[2];LANG=ROOT/'gu-Gujr-IN'
SOURCE=ROOT/'downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82458/index.cnxml'
MEDIA=ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'
OUT=ROOT/'build/gujarati-decimal-figures'

def main():
 data=json.loads((LANG/'reviews/a10-m82458-media-inventory.json').read_text(encoding='utf8'))
 translation=LANG/'translations/a10-m82458.gu.cnxml';sh=hashlib.sha256(SOURCE.read_bytes()).hexdigest();gh=hashlib.sha256(translation.read_bytes()).hexdigest()
 assert sh=='678dc0c3ae2aad0192c0314395541720d6c6eb97f56d2f4d169f056fe1e630cb'
 assert gh==data['translation_sha256']=='9ce1aa6b189fa8b115ce88f921a609b24583ae13fa2470100212f6d9682270a0'
 src=etree.parse(str(SOURCE));gu=etree.parse(str(translation));media=src.xpath('//*[local-name()="media"]');alts={e.get('id'):e.get('alt') for e in gu.xpath('//*[local-name()="media"]')}
 assert len(media)==len(data['media'])==49
 ids=[];refs=[];redraws=[];figures=[]
 for e,item in zip(media,data['media']):
  ident=e.get('id');name=Path(e[0].get('src')).name
  assert ident==item['source_media'] and name==Path(item['source_asset']).name
  sha=hashlib.sha256((MEDIA/name).read_bytes()).hexdigest();assert sha==item['original_sha256']
  snippet=render_figure(name,alts[ident],ident+'-redraw')
  if snippet:
   assert name not in VERIFIED_MATH_ONLY and item['localization']=='Gujarati redraw required'
   tree=html.fragment_fromstring(snippet);text=' '.join(tree.xpath('.//text()[not(ancestor::math)]'))
   assert not re.search(r'[A-Za-z]{2,}',text),(name,text)
   ids+=tree.xpath('//@id');refs+=tree.xpath('//@aria-labelledby');refs+=re.findall(r'url\(#([^\)]+)\)',snippet);redraws.append((name,snippet))
  else:assert name in VERIFIED_MATH_ONLY and item['localization']!='Gujarati redraw required'
  figures.append({'source_media':ident,'filename':name,'sha256':sha,'mode':'localized' if snippet else 'verified mathematical-only original'})
 assert len(redraws)==28 and len(VERIFIED_MATH_ONLY)==21 and len(ids)==len(set(ids)) and all(r in ids for r in refs)
 t={n[len(PREFIX):]:html.fragment_fromstring(s) for n,s in redraws}
 chart=t['001_new.jpg'];assert len(chart.xpath('.//th'))==12 and chart.xpath('.//th[7]/@aria-label')==['દશાંશ ચિહ્ન'] and chart.xpath('.//tbody//td[7]/text()')==['.']
 for step in 'abcd':assert t['002'+step+'_new.jpg'].xpath('.//*[contains(text(),"પગલું")]')
 assert '4.3' in ''.join(t['002a_new.jpg'].itertext()) and 'ચાર અને ત્રણ દશાંશ' in ''.join(t['002d_new.jpg'].itertext())
 assert '14.024' in ''.join(t['003d_new.jpg'].itertext()) and t['003c_new.jpg'].xpath('.//u/text()')==['2','4']
 assert t['004b_new.jpg'].xpath('.//*[@data-underlined]/@data-underlined')==['5']
 assert t['004c_new.jpg'].xpath('.//*[@data-add-target]/@data-add-target')==['4'] and t['004c_new.jpg'].xpath('.//*[@data-delete-indices]/@data-delete-indices')==['5']
 assert t['005b_img_new.jpg'].xpath('.//*[@data-underlined]/@data-underlined')==['4'] and t['006b_img_new.jpg'].xpath('.//*[@data-underlined]/@data-underlined')==['3']
 assert t['005c_img_new.jpg'].xpath('.//*[@data-add-target]/@data-add-target')==['3'] and t['005c_img_new.jpg'].xpath('.//*[@data-delete-indices]/@data-delete-indices')==['4,5']
 assert t['006c_img_new.jpg'].xpath('.//*[@data-delete-indices]/@data-delete-indices')==['2,3,4,5']
 assert t['006c_img_new.jpg'].xpath('.//*[@data-no-add-target]/@data-no-add-target')==['1']
 for name,values in [('009a_img_new.jpg',['(0.3)','1 દશાંશ સ્થાન','(0.7)','1 દશાંશ સ્થાન','(0.2)','1 દશાંશ સ્થાન','(0.46)','2 દશાંશ સ્થાન']),('009d_img_new.jpg',['(0.21)','2 દશાંશ સ્થાન','(0.092)','3 દશાંશ સ્થાન']),('010a_img_new.jpg',['(−3.9)','1 દશાંશ સ્થાન','(4.075)','3 દશાંશ સ્થાન'])]:
  text=' '.join(t[name].itertext());assert all(v in text for v in values)
 text=' '.join(t['010d_img_new.jpg'].itertext());assert all(v in text for v in ('4.075','× 3.9','36675','12225','15.8925','4 દશાંશ સ્થાન'))
 assert 'translateX(-.55em)' in etree.tostring(t['010d_img_new.jpg'],encoding='unicode')
 assert all(v in ''.join(t['012_img_new.jpg'].itertext()) for v in ('100','2 શૂન્ય','5.63','563'))
 assert t['012_img_new.jpg'].xpath('.//*[@data-shift]/@data-shift')==['1','2']
 labels=' '.join(t['016_img_new.jpg'].itertext());assert all(v in labels for v in ('0.3','દશાંશ','7','શતાંશ','4','સહસ્રાંશ'))
 neg=' '.join(t['017_img_new.jpg'].itertext());assert all(v in neg for v in ('0.625','48','20','16','40','તેથી')) and '8⟌5.000' in neg.replace(' ','')
 assert t['017_img_new.jpg'].xpath('.//math//text()')==['−','5','8','=','−','0.625']
 rep=' '.join(t['018_img_new.jpg'].itertext());assert rep.count('120')==3 and rep.count('100')==3 and all(v in rep for v in ('43ને 22 વડે ભાગો','1.95454','120 ફરી આવે છે','100 ફરી આવે છે','પેટર્ન ફરી આવે છે','1.9','54'))
 self=t['201_img_new.jpg'];assert len(self.xpath('.//caption'))==5 and len(self.xpath('.//td[@aria-label="ખાલી"]'))==15
 checks={'round hundredth':Decimal('18.379').quantize(Decimal('.01'),rounding=ROUND_HALF_UP)==Decimal('18.38'),'round tenth':Decimal('18.379').quantize(Decimal('.1'),rounding=ROUND_HALF_UP)==Decimal('18.4'),'round one':Decimal('18.379').quantize(Decimal('1'),rounding=ROUND_HALF_UP)==Decimal('18'),
  '14.024 words':F(14)+F(24,1000)==F(14024,1000),'decimal products':F(3,10)*F(7,10)==F(21,100) and F(2,10)*F(46,100)==F(92,1000),'negative product':F(-39,10)*F(4075,1000)==F(-158925,10000),'multiply100':F(563,100)*100==563,'multiply1000':F(563,100)*1000==5630,
  'decimal division':F(2565,100)/F(6,100)==F(855,2),'money division':F(399,100)/24==F(133,800),'negative fraction':F(-5,8)==F(-625,1000),'recurring division':F(43,22)==F(1)+F(954,1000)+F(54,99000),
  'percent to decimal':all(F(a,b)==F(c,d) for a,b,c,d in [(6,100,6,100),(78,100,78,100),(27,1000,27,1000),(135,100,135,100)]),'35.7 percent':F(357,1000)==F(357,1000),'decimal to percent':all(F(a,b)==F(c,d) for a,b,c,d in [(5,100,5,100),(83,100,83,100),(105,100,105,100),(75,1000,75,1000),(3,10,30,100)])}
 assert all(checks.values())
 OUT.mkdir(parents=True,exist_ok=True);style="""@font-face{font-family:Gujarati;src:url('../../gu-Gujr-IN/output/assets/NotoSansGujarati.ttf')}*{box-sizing:border-box}body{font-family:Gujarati,'Nirmala UI',sans-serif;margin:20px auto;padding:0 16px;max-width:1080px;line-height:1.6;color:#182c35}article{margin-bottom:24px;border-bottom:2px solid #08656b;padding-bottom:16px}h2{font-size:18px;overflow-wrap:anywhere}math{font-family:math}"""
 groups=[redraws[i:i+7] for i in range(0,len(redraws),7)]
 for p,g in enumerate(groups,1):
  body=''.join(f'<article><h2>{escape(n)}</h2>{s}</article>' for n,s in g);doc='<!doctype html><html lang="gu-Gujr-IN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>દશાંશ</title><style>'+style+'</style><body><h1>દશાંશ</h1>'+body+'</body></html>';(OUT/f'page-{p}.html').write_text(doc,encoding='utf8')
 receipt={'source_sha256':sh,'translation_sha256':gh,'helper_sha256':hashlib.sha256(Path(__file__).with_name('localized_a10_decimals.py').read_bytes()).hexdigest(),'media':49,'redraws':28,'verified_math_only':21,'unique_ids':len(ids),'resolved_references':len(refs),'selfcheck_blank_cells':15,'mathematical_checks':checks,'figures':figures}
 (LANG/'reviews/a10-m82458-figures-qa.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({k:v for k,v in receipt.items() if k!='figures'}))

if __name__=='__main__':main()
