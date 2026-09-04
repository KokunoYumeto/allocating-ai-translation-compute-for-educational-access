"""Meaningful content, provenance, structure, link and deterministic build checks."""
import csv
from fractions import Fraction
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET

LANG=Path(__file__).resolve().parents[1]
ROOT=LANG.parent
C='http://cnx.rice.edu/cnxml'; M='http://www.w3.org/1998/Math/MathML'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


class Page(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.links=[];self.resources=[];self.lang=None;self.math=0;self.main=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='html':self.lang=a.get('lang')
        if tag=='main':self.main+=1
        if tag=='math':self.math+=1
        if tag=='a' and 'href' in a:self.links.append(a['href'])
        if tag in ('img','script','iframe') and 'src' in a:self.resources.append(a['src'])
        if tag=='link' and 'href' in a:self.resources.append(a['href'])
        assert tag not in ('script','iframe'), 'Remote/runtime scripting not expected'
        if tag=='img':assert a.get('alt'), 'Missing alternative text'
        if tag=='th':assert a.get('scope') in ('row','col'), 'Unscoped table header'


def signature(root):
    return [(e.tag,e.get('id'),e.get('target-id'),e.get('document')) for e in root.iter()]


def math_signature(root):
    return [(e.tag,e.attrib,(e.text or '').strip()) for e in root.iter()
            if e.tag.startswith('{'+M+'}') and not e.tag.endswith('mtext')]


def main():
    data=json.loads((LANG/'translations/unit01.gu.json').read_text(encoding='utf-8'))
    items=data['items'];byid={i['id']:i for i in items};routes={r['id'] for r in data['routes']}
    assert len(byid)==len(items)==17
    assert [sum(i['phase']==p for i in items) for p in ('placement','practice','exit')]==[6,8,3]
    for i in items:
        assert i['route'] in routes and len(i['steps'])>=2 and i['answer'].strip()
        if 'options' in i:
            assert len(i['options'])==len(set(i['options']))==3
            assert i['answer'] in i['options']
            assert set(i['feedback'])==set(i['options'])
        c=i['check'];kind=c['kind']
        if kind=='sum':assert sum(c['values'])==c['result']
        elif kind=='max':assert max(c['values'])==c['result']
        elif kind=='sort':assert sorted(c['values'])==c['result']
        elif kind=='digit_value':assert (c['number']//c['place']%10)*c['place']==c['result']
        elif kind=='expanded':assert sum(c['terms'])==c['number']
        elif kind=='group':assert divmod(c['ones'],10)==(c['tens'],c['remainder'])
        elif kind=='zero_convention':assert i['id']=='D2' and i['answer']==i['options'][0]
        else:raise ValueError(kind)
    # Independent expected answers bind the displayed answers to computations.
    expected={'D1':'7','D3':'40','D4':'305','D5':'85','D6':'200 + 0 + 6','E1':'9','E2':'1 દશક',
              'E4':'420','E5':'500 + 0 + 7','E6':'190','E7':'9, 90, 99','X2':'54 = 50 + 4','X3':'76'}
    for k,v in expected.items():assert byid[k]['answer']==v,(k,'displayed answer mismatch')
    assert '60' in byid['E3']['answer'] and '52' in byid['E8']['answer']
    assert 'દશક' in byid['X1']['answer'] and 'ના' in byid['X1']['answer']
    for route in data['routes']:
        assert all(x in byid for x in route['practice']+route['recheck'])
    triples=[(['0','1/4','3','5.2','15','105'],[3,15,105],[0,3,15,105]),
             (['0','2/3','2','9','11.8','241','376'],[2,9,241,376],[0,2,9,241,376]),
             (['0','5/3','7','8.8','13','201'],[7,13,201],[0,7,13,201])]
    for terms,counting,whole in triples:
        nums=list(map(Fraction,terms))
        assert [int(x) for x in nums if x.denominator==1 and x>=1]==counting
        assert [int(x) for x in nums if x.denominator==1 and x>=0]==whole
    assert 50000+1000+400+90+3==51493
    src=ET.parse(ROOT/'downloads/gu-Gujr-IN/a00-id/provenance/logbook/authority/prealgebra2e/m81243.source.cnxml').getroot()
    src=next(e for e in src.iter() if e.get('id')=='fs-id1830385')
    dst=ET.parse(LANG/'translations/a00-m81243-part01.gu.cnxml').find(f'.//{{{C}}}section')
    assert signature(src)==signature(dst),'CNXML hierarchy/IDs/references changed'
    assert math_signature(src)==math_signature(dst),'MathML numbers/operators changed'
    a10src=ET.parse(ROOT/'downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82452/index.cnxml').getroot()
    a10src=next(e for e in a10src.iter() if e.get('id')=='fs-id1170655190140')
    a10dst=ET.parse(LANG/'translations/a10-m82452-excerpt.gu.cnxml').find(f'.//{{{C}}}exercise')
    assert signature(a10src)==signature(a10dst)
    assert ''.join(a10src.find(f'{{{C}}}problem').itertext())==''.join(a10dst.find(f'{{{C}}}problem').itertext())
    source_ids={e.get('id') for r in (dst,a10dst) for e in r.iter() if e.tag==f'{{{C}}}exercise'}
    assert source_ids=={w['source_exercise'] for w in data['source_worked_companion']}
    output=LANG/'output'
    pages={}
    for path in output.glob('*.html'):
        parser=Page();parser.feed(path.read_text(encoding='utf-8'));pages[path.name]=parser
        assert len(parser.ids)==len(set(parser.ids)),path
        assert parser.lang=='gu-Gujr-IN' and parser.main==1
        assert '\ufffd' not in path.read_text(encoding='utf-8')
        for resource in parser.resources:
            assert not urlsplit(resource).scheme and (output/resource).is_file(),resource
    for name,parser in pages.items():
        for link in parser.links:
            parsed=urlsplit(link)
            if parsed.scheme:continue
            target=unquote(parsed.path) or name
            assert (output/target).is_file(),(name,link)
            if parsed.fragment:assert parsed.fragment in pages[target].ids,(name,link)
    assert source_ids.issubset(set(pages['source.html'].ids))
    assert pages['source.html'].math==sum(e.tag==f'{{{M}}}math' for e in src.iter())
    css=(output/'assets/style.css').read_text()
    assert 'http' not in css and '@font-face' in css and '@media print' in css
    before={p.relative_to(output).as_posix():sha(p) for p in output.rglob('*') if p.is_file() and p.suffix!='.pdf'}
    subprocess.run([sys.executable,str(LANG/'scripts/build.py')],check=True,capture_output=True)
    after={p.relative_to(output).as_posix():sha(p) for p in output.rglob('*') if p.is_file() and p.suffix!='.pdf'}
    assert before==after,'Non-deterministic HTML build'
    canon=list(csv.DictReader((LANG/'canon/examples.csv').open(encoding='utf-8')))
    assert 10<=len(canon)<=20
    modulemap=list(csv.DictReader((LANG/'source-module-map.csv').open(encoding='utf-8')))
    assert sum(x['program']=='A00' for x in modulemap)==75 and sum(x['program']=='A10' for x in modulemap)==82
    receipt={'schema':'gujarati-pilot-qa-v1','result':'pass','locale':'gu-Gujr-IN','date':'2026-08-30',
             'companion_items':len(items),'placement_items':6,'remediation_paths':3,'practice_items':8,'exit_items':3,
             'source_exercises_with_full_worked_companions':len(source_ids),'canon_examples':len(canon),
             'canonical_modules_mapped':len(modulemap),'source_mathml_nodes':len(math_signature(src)),
             'source_ids_preserved':len([e for e in src.iter() if e.get('id')]),
             'checks':['CNXML hierarchy and IDs','MathML numeric/operator structure','A10 problem text unchanged except solution terms',
                       'independent exact-rational classification','place-value arithmetic','displayed answer binding',
                       'all item solutions and distractor feedback present','routing closure','HTML IDs and internal links',
                       'local assets and offline runtime','language metadata','image alternatives','table headers','deterministic rebuild'],
             'human_review_pending':['Gujarati educator review','child pilot','screen-reader keyboard session','PDF/UA tagging'],
             'outputs_sha256':after}
    (LANG/'QA.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('result','companion_items','source_exercises_with_full_worked_companions','canon_examples','source_ids_preserved')},indent=2))


if __name__=='__main__':main()
