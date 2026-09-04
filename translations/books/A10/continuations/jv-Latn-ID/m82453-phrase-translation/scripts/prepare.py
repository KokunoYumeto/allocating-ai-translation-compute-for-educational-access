from pathlib import Path
from lxml import etree as E
import json,hashlib,sys,urllib.request
ROOT=Path(__file__).resolve().parents[1]
source=Path(sys.argv[1]).read_bytes()
assert hashlib.sha256(source).hexdigest()=='a8fdd235aa254c5a0a1248fa858e9b3579d9b40982bbc514cbe6a18c3e6fcbed'
full=E.fromstring(source); section=full.xpath('//*[@id="fs-id1170654942537"]')[0]
(ROOT/'source').mkdir(parents=True,exist_ok=True)
raw=E.tostring(section,encoding='utf-8',xml_declaration=True,with_tail=False)
(ROOT/'source/en.cnxml').write_bytes(raw)
slots=[]
for i,e in enumerate(section.iter()):
 for field in ['text','tail']:
  s=getattr(e,field)
  if s and s.strip() and any(c.isalpha() for c in s) and not (field=='text' and e.tag.startswith('{http://www.w3.org/1998/Math/MathML}') and E.QName(e).localname not in ['mtext']):
   slots.append({'node':i,'tag':E.QName(e).localname,'id':e.get('id'),'field':field,'source':s.strip()})
 for field in ['alt','aria-label','summary']:
  if e.get(field): slots.append({'node':i,'tag':E.QName(e).localname,'id':e.get('id'),'field':'@'+field,'source':e.get(field)})
(ROOT/'source/text-slots.json').write_text(json.dumps(slots,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ns={'c':'http://cnx.rice.edu/cnxml','m':'http://www.w3.org/1998/Math/MathML'}
media=[]
for e in section.findall('.//c:media',ns):
 name=Path(e[0].get('src')).name
 p=ROOT/'assets/canonical'/name;p.parent.mkdir(parents=True,exist_ok=True)
 url='https://raw.githubusercontent.com/openstax/osbooks-prealgebra-bundle/38cae454e644abf9f0a623e876994553881597c9/media/'+name
 if not p.exists():
  with urllib.request.urlopen(url,timeout=30) as r:p.write_bytes(r.read())
 b=p.read_bytes();media.append({'id':e.get('id'),'file':p.relative_to(ROOT).as_posix(),'url':url,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'git_blob_sha1':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()})
meta={'source_section_sha256':hashlib.sha256(raw).hexdigest(),'source_module_sha256':hashlib.sha256(source).hexdigest(),'section':'fs-id1170654942537','direct_children':len(section),'ids':len(section.xpath('.//@id')),'mathml':len(section.findall('.//m:math',ns)),'exercises':len(section.findall('.//c:exercise',ns)),'solutions':len(section.findall('.//c:solution',ns)),'media':media,'next_anchor':section.getnext().get('id')}
(ROOT/'source/BOUNDARY.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for i,s in enumerate(slots):print(f'{i} | {s["node"]}:{s["field"]} | {s["source"]}')
print(json.dumps(meta,indent=2))
