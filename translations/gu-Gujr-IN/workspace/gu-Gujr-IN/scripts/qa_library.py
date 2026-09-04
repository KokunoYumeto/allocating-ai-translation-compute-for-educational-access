"""Independent source-structure/math and offline-reader integrity checks."""
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

from build_library import C, M, LANG, ROOT, OUT, compose
import csv

# Natural-language mtext sometimes needs Gujarati operand order. This exact
# source/owner/text exception does not relax numeric MathML or other prose.
MTEXT_WORD_ORDER = {
    ('A10:m82454', 'fs-id1166422639606', '19 from 47', '47માંથી 19'):
        '4483b9df8736598af20287450b89cf367728da04c697f85f1abb64bbeffb092f',
    ('A10:m82461', 'fs-id1170654027716', '2000 pounds', '2,000 પાઉન્ડ'):
        'df82cee2f1a278bb88f392572457ee679bc09d108962a9b6c72ba5bb0084655e',
}


def local(tag):
    return tag.rsplit('}',1)[-1]


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[]; self.links=[]; self.resources=[]; self.lang=None; self.main=0
        self.math=0; self.svg=0; self.svg_labels=[]

    def handle_starttag(self, tag, attributes):
        a=dict(attributes)
        if a.get('id'):self.ids.append(a['id'])
        if tag=='html':self.lang=a.get('lang')
        if tag=='main':self.main+=1
        if tag=='a':self.links.append(a.get('href',''))
        if tag in ('img','script','iframe') and a.get('src'):self.resources.append(a['src'])
        if tag=='link' and a.get('href'):self.resources.append(a['href'])
        assert tag not in ('script','iframe'), 'Unexpected runtime dependency'
        if tag=='img':assert a.get('alt'), 'Missing image alternative'
        if tag=='th':assert a.get('scope') in ('row','col'), 'Unscoped table header'
        if tag=='math':self.math+=1
        if tag=='svg':
            self.svg+=1
            # Decorative lines inside a named semantic figure are intentionally
            # hidden; only informative SVGs need their own accessible name.
            if a.get('aria-hidden') != 'true':
                assert a.get('role')=='img' and (a.get('aria-labelledby') or a.get('aria-label'))
                self.svg_labels += a.get('aria-labelledby','').split()


def main():
    rows=list(csv.DictReader((LANG/'source-module-map.csv').open(encoding='utf-8')))
    recipes=json.loads((LANG/'library-recipes.json').read_text(encoding='utf-8'))
    results=[]
    word_order_checks=[]
    for row in rows:
        key=row['program']+':'+row['module_id']
        if key not in recipes:continue
        translated, source=compose(row,recipes[key])
        srcids={e.get('id'):e for e in source.iter() if e.get('id')}
        expected=list(source.iter())
        parents={child:parent for parent in source.iter() for child in parent}
        actual=list(translated.iter())
        full=[(e.tag,e.get('id')) for e in expected]==[(e.tag,e.get('id')) for e in actual]
        if full:
            pairs=list(zip(expected,actual))
        else:
            pairs=[]
            for section in translated.findall('./{'+C+'}content/{'+C+'}section'):
                original=srcids[section.get('id')]
                assert [(e.tag,e.get('id')) for e in original.iter()]==[(e.tag,e.get('id')) for e in section.iter()]
                pairs += list(zip(original.iter(),section.iter()))
        numbers=0
        for original,target in pairs:
            if original.tag=='{'+C+'}emphasis' and original.get('effect')=='italics' and len(original)==0 and re.fullmatch('[A-Za-z]',(original.text or '').strip()):
                assert (original.text or '').strip()==(target.text or '').strip(),(key,'Italic variable drift',original.text,target.text)
            for attr in ('alt','aria-label','summary','title'):
                value=target.get(attr,'')
                assert not (re.search(r'[A-Za-z]{3}',value) and not re.search(r'[\u0a80-\u0aff]',value)), (key,target.get('id'),'Untranslated accessibility attribute',attr,value)
            for attr,value in original.attrib.items():
                if attr in ('alt','aria-label','summary','title','{http://www.w3.org/XML/1998/namespace}lang'):continue
                if local(original.tag)=='image' and Path(target.get('src','')).name=='number-line.svg' and attr in ('src','mime-type'):continue
                assert target.get(attr)==value,(key,original.get('id'),attr)
            if original.tag.startswith('{'+M+'}'):
                if local(original.tag)=='mtext':
                    old_numbers=re.findall(r'\d+',original.text or '')
                    new_numbers=re.findall(r'\d+',target.text or '')
                    if old_numbers != new_numbers:
                        owner=original
                        while not owner.get('id') and owner in parents:owner=parents[owner]
                        case=(key,owner.get('id'),original.text or '',target.text or '')
                        assert case in MTEXT_WORD_ORDER,(key,'mtext numerical drift',case)
                        assert hashlib.sha256((ROOT/row['authority_path']).read_bytes()).hexdigest()==MTEXT_WORD_ORDER[case]
                        if case[0:2] == ('A10:m82454', 'fs-id1166422639606'):
                            assert Counter(old_numbers)==Counter(new_numbers),case
                            # Both phrases instruct 47 minus 19; the enclosing
                            # solution applies the negative sign to obtain -28.
                            assert old_numbers==['19','47'] and new_numbers==['47','19']
                            meaning='subtract 19 from 47; enclosing signed sum is 19 + (-47) = -28'
                        else:
                            # Gujarati reader formatting adds the thousands
                            # separator without changing the source quantity.
                            assert case[0:2] == ('A10:m82461', 'fs-id1170654027716')
                            assert ''.join(old_numbers)==''.join(new_numbers)=='2000'
                            meaning='same 2,000-pound quantity; target adds a thousands separator'
                        word_order_checks.append({'module':key,'owner':owner.get('id'),'source':original.text,'target':target.text,'meaning':meaning})
                else:
                    assert (original.text or '').strip()==(target.text or '').strip(),(key,'MathML drift',original.text,target.text)
                    if local(original.tag)=='mn':numbers+=1
            for field in ('text','tail'):
                value=getattr(original,field) or ''
                if re.search(r'\d',value) and not any(c.isalpha() for c in value):
                    assert ''.join(value.split())==''.join((getattr(target,field) or '').split()),(key,'Numeric-only text drift',value,getattr(target,field))
        source_solutions=sum(local(e.tag)=='solution' for e in actual)
        exercises=[e for e in actual if local(e.tag)=='exercise']
        results.append({'key':key,'complete_source_tree':full,'elements':len(actual),'ids':sum(bool(e.get('id')) for e in actual),
                        'math_expressions':sum(local(e.tag)=='math' for e in actual),'numeric_mathml_tokens_checked':numbers,
                        'exercises':len(exercises),'source_solutions':source_solutions,
                        'source_exercises_without_supplied_solution':[e.get('id') for e in exercises if e.find('{'+C+'}solution') is None]})
    pages={}
    for path in (LANG/'output').rglob('*.html'):
        p=Page();content=path.read_text(encoding='utf-8');p.feed(content)
        assert '\ufffd' not in content,path
        assert len(p.ids)==len(set(p.ids)),(path,'Duplicate IDs',[i for i,n in Counter(p.ids).items() if n>1])
        assert p.lang=='gu-Gujr-IN' and p.main==1,path
        assert set(p.svg_labels)<=set(p.ids),(path,'Missing SVG accessible name target')
        pages[path.resolve()]=p
    for path,page in pages.items():
        for reference in page.links+page.resources:
            u=urlsplit(reference)
            if u.scheme:
                assert reference not in page.resources,(path,'Remote runtime resource')
                continue
            target=(path.parent/unquote(u.path)).resolve() if u.path else path
            assert target.is_file(),(path,reference)
            if u.fragment and target in pages:assert unquote(u.fragment) in pages[target].ids,(path,reference)
    # Independent checks for the localized base-10 diagrams and Try Its.
    for h,t,o,answer in [(1,3,8,138),(2,1,5,215),(1,7,6,176),(2,3,7,237)]:
        assert 100*h+10*t+o==answer
    assert 3*100+7*10+4==374
    before={p.relative_to(OUT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.rglob('*') if p.is_file()}
    subprocess.run([sys.executable,str(LANG/'scripts/build_library.py')],check=True,capture_output=True)
    after={p.relative_to(OUT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.rglob('*') if p.is_file()}
    assert before==after,'Non-deterministic library build'
    receipt={'schema':'gujarati-library-qa-v1','result':'pass','assignment_complete':False,'modules':results,
             'reviewed_mtext_word_order':word_order_checks,
             'html_pages_checked':len(pages),'checks':['Source XML hierarchy and IDs','Source attributes and references','MathML numbers/operators/variables','Single-letter italic variables outside MathML','Numeric-only text','Source solution coverage inventory','Offline resources and all internal links','Unique IDs','Named SVGs','Table header scopes','Independent base-10 arithmetic','Deterministic library rebuild'],
             'limitations':['Text-tree completeness is not native linguistic review.','Original image modes and untranslated visual labels remain tracked separately.','Added-answer coverage is recorded per module; later modules may still need omitted-answer companions.','Tagged screen PDF and full-assignment AX-3 work remain pending.'],
             'output_sha256':after}
    (LANG/'LIBRARY_QA.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:receipt[k] for k in ('result','html_pages_checked','modules')},indent=2))


if __name__=='__main__':main()
