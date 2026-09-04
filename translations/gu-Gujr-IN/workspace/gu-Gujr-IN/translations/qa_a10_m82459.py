from pathlib import Path
import xml.etree.ElementTree as E
import hashlib,re,json
from qa_a10_m82459_math import run as run_math_checks
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82459/index.cnxml'
GU=Path(__file__).with_name('a10-m82459.gu.cnxml')
NS={'c':'http://cnx.rice.edu/cnxml','m':'http://www.w3.org/1998/Math/MathML'}
def main():
 s=E.parse(SRC).getroot();g=E.parse(GU).getroot();a=list(s.iter());b=list(g.iter())
 assert[e.tag for e in a]==[e.tag for e in b];assert[e.get('id')for e in a]==[e.get('id')for e in b]
 for x,y in zip(a,b):
  for k,v in x.attrib.items():
   if k not in {'alt','aria-label','summary','title'}:assert y.get(k)==v,(x.get('id'),k)
   elif re.search('[A-Za-z]',v):assert re.search('[\u0a80-\u0aff]',y.get(k,'')),(x.get('id'),k,'not localized')
  if x.tag.startswith('{'+NS['m']+'}')and not x.tag.endswith('mtext'):assert x.text==y.text
  if x.tag.endswith('mtext')and re.fullmatch('[A-Za-z]',(x.text or '').strip()):assert x.text==y.text,('MathML letter',x.text,y.text)
  if x.tag.endswith('emphasis')and x.get('effect')=='italics'and re.fullmatch('[A-Za-z]',(x.text or '').strip()):assert x.text==y.text,('inline variable',x.text,y.text)
 ids=[e.get('id')for e in b if e.get('id')];assert len(ids)==len(set(ids))
 ex=g.findall('.//c:exercise',NS);sol=g.findall('.//c:solution',NS);media=g.findall('.//c:media',NS)
 assert len(ex)==106 and len(sol)==74 and len(media)==26
 assert all(re.search('[\u0a80-\u0aff]',e.get('alt',''))or not re.search('[A-Za-z]',e.get('alt',''))for e in media)
 numerical=run_math_checks(s,g)
 errata=json.loads(GU.with_name('a10-m82459-errata.gu.json').read_text(encoding='utf8'))
 for i,entry in errata['entries'].items():
  assert any(e.get('id')==i for e in a)
  for attr in ['alt','summary','aria-label','title']:
   if entry.get(attr+'_gu'):assert next(e for e in b if e.get('id')==i).get(attr)==entry[attr+'_gu']
 report={'result':'pass','module':'m82459','elements':len(b),'source_ids':len(ids),'mathml':len(g.findall('.//m:math',NS)),'exercises':len(ex),'source_solutions':len(sol),'source_omitted_solutions':len(ex)-len(sol),'media_alternatives_checked':len(media),'translated_media_alt':sum(bool(re.search('[\u0a80-\u0aff]',e.get('alt','')))for e in media),'translated_aria_labels':sum(bool(e.get('aria-label'))for e in b),'translated_summaries':sum(bool(e.get('summary'))for e in b),'source_title_attributes':sum('title'in e.attrib for e in a),'errata_entries':len(errata['entries']),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'translation_sha256':hashlib.sha256(GU.read_bytes()).hexdigest(),'numerical':numerical}
 (ROOT/'gu-Gujr-IN/reviews/a10-m82459-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({k:v for k,v in report.items()if k!='numerical'},ensure_ascii=False,indent=2));print('Numerical exercises checked:',numerical['independently_checked_exercises'])
if __name__=='__main__':main()
