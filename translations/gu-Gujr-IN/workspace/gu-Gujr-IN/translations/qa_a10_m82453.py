from pathlib import Path
import xml.etree.ElementTree as E
import hashlib,re,json
from qa_a10_m82453_math import run as run_math_checks
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82453/index.cnxml'
GU=Path(__file__).with_name('a10-m82453.gu.cnxml')
NS={'c':'http://cnx.rice.edu/cnxml','m':'http://www.w3.org/1998/Math/MathML'}
def main():
 s=E.parse(SRC).getroot();g=E.parse(GU).getroot();a=list(s.iter());b=list(g.iter())
 assert[e.tag for e in a]==[e.tag for e in b];assert[e.get('id')for e in a]==[e.get('id')for e in b]
 for x,y in zip(a,b):
  for k,v in x.attrib.items():
   if k not in {'alt','aria-label','summary','title'}:assert y.get(k)==v,(x.get('id'),k)
   elif re.search('[A-Za-z]',v):assert re.search('[\u0a80-\u0aff]',y.get(k,'')),(x.get('id'),k,'not localized')
  if x.tag.startswith('{'+NS['m']+'}')and not x.tag.endswith('mtext'):assert x.text==y.text
  if x.tag.endswith('mtext') and re.fullmatch('[A-Za-z]',(x.text or '').strip()):assert x.text==y.text,('MathML letter',x.text,y.text)
 ids=[e.get('id')for e in b if e.get('id')];assert len(ids)==len(set(ids))
 ex=g.findall('.//c:exercise',NS);sol=g.findall('.//c:solution',NS);media=[e for e in b if e.tag.endswith('media')]
 assert len(ex)==156 and len(sol)==105 and len(media)==50
 # Purely numerical or mathematical figures do not need invented prose. Every
 # language-bearing alternative must, however, be localized.
 assert all(re.search('[\u0a80-\u0aff]',e.get('alt',''))or not re.search('[A-Za-z]',e.get('alt',''))for e in media)
 numerical=run_math_checks(s)
 for check in numerical['checks']:
  if check['kind']=='numeric_or_monomial_coefficient':
   exercise=next(e for e in ex if e.get('id')==check['source_exercise'])
   solution=exercise.find('c:solution',NS)
   evidence=' '.join(solution.itertext())+' '+' '.join(e.get('alt','')for e in solution.iter())
   assert re.search(r'(?<!\d)'+str(check['answer'])+r'(?!\d)',evidence),(check['source_exercise'],'Gujarati answer binding')
 errata=json.loads(GU.with_name('a10-m82453-errata.gu.json').read_text(encoding='utf8'))
 for i,entry in errata['entries'].items():
  assert any(e.get('id')==i for e in a)
  if entry.get('alt_gu'):assert next(e for e in b if e.get('id')==i).get('alt')==entry['alt_gu']
  if entry.get('summary_gu'):assert next(e for e in b if e.get('id')==i).get('summary')==entry['summary_gu']
 report={'result':'pass','module':'m82453','elements':len(b),'source_ids':len(ids),'mathml':len(g.findall('.//m:math',NS)),'exercises':len(ex),'source_solutions':len(sol),'source_omitted_solutions':len(ex)-len(sol),'media_alternatives_checked':len(media),'translated_media_alt':sum(bool(re.search('[\u0a80-\u0aff]',e.get('alt','')))for e in media),'nonlinguistic_media_alternative':1,'translated_aria_labels':sum(bool(e.get('aria-label'))for e in b),'translated_summaries':sum(bool(e.get('summary'))for e in b),'source_title_attributes':sum('title'in e.attrib for e in a),'errata_entries':len(errata['entries']),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'translation_sha256':hashlib.sha256(GU.read_bytes()).hexdigest(),'numerical':numerical}
 (ROOT/'gu-Gujr-IN/reviews/a10-m82453-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 compact={k:v for k,v in report.items() if k!='numerical'};compact.update({k:v for k,v in numerical.items() if k!='checks'})
 print(json.dumps(compact,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
