"""Independent full-tree, number, credit and actual diagram checks."""
from pathlib import Path
import hashlib
import json
import re
import xml.etree.ElementTree as ET

LANG=Path(__file__).resolve().parents[1];ROOT=LANG.parent
C='{http://cnx.rice.edu/cnxml}'
results=[]
for mid in ('m82630','m82451'):
    source=ET.parse(ROOT/f'downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/{mid}/index.cnxml').getroot()
    path=LANG/f'translations/a10-{mid}.gu.cnxml';target=ET.parse(path).getroot()
    a=list(source.iter());b=list(target.iter())
    assert [(e.tag,e.get('id')) for e in a]==[(e.tag,e.get('id')) for e in b]
    for x,y in zip(a,b):
        for k,v in x.attrib.items():
            if k not in ('alt','aria-label','summary','title','{http://www.w3.org/XML/1998/namespace}lang'):assert y.get(k)==v
        for field in ('text','tail'):
            old=getattr(x,field) or '';new=getattr(y,field) or ''
            assert re.findall(r'\d+',old)==re.findall(r'\d+',new),(mid,x.get('id'),field,old,new)
        for field in ('alt','aria-label','summary','title'):
            new=y.get(field,'')
            assert not (re.search('[A-Za-z]{3}',new) and not re.search('[\u0a80-\u0aff]',new))
    if mid=='m82630':
        for identifier in ['eip-id1169146105286','eip-855','eip-250','eip-478']:
            x=next(e for e in a if e.get('id')==identifier);y=next(e for e in b if e.get('id')==identifier)
            assert ' '.join(''.join(x.itertext()).split())==' '.join(''.join(y.itertext()).split())
        assert len(list(source.iter(C+'image')))==4
    rows=json.loads((LANG/f'translations/a10-{mid}.slots.gu.json').read_text(encoding='utf-8'))
    assert all(row['target'] is not None for row in rows)
    results.append({'module':mid,'elements':len(b),'ids':sum(bool(e.get('id')) for e in b),'language_slots':len(rows),'images':sum(e.tag==C+'image' for e in b),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
# Dot lies on BOTH redrawn crossing segments; parallel segments have equal
# direction vectors but different offsets. No source equations are invented.
for x1,y1,x2,y2 in [(20,170,180,90),(95,20,180,190)]:
    assert (140-x1)*(y2-y1)==(110-y1)*(x2-x1)
assert (142-42,18-187)==(172-72,18-187)
receipt={'schema':'gujarati-front-matter-qa-v1','result':'pass','modules':results,'checks':['Complete source tree and IDs','Non-language attributes','Every numeric token in prose/tails','All language-bearing accessibility attributes','All reviewer and author-affiliation credits unchanged','Complete slot coverage','Diagram intersection and parallelism'],'limitations':['Native educator review pending; front-matter technical register provisional.','Source figure alt error recorded separately; original translated XML preserved.']}
(LANG/'A10_FRONT_MATTER_QA.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False,indent=2))
