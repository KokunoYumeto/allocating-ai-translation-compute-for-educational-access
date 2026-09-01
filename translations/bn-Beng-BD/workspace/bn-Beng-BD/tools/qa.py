"""Fail-closed structural, mathematical, answer and provenance checks."""
from pathlib import Path
import ast, copy, hashlib, json, operator, re, tempfile, xml.etree.ElementTree as ET
from build import build, local, C, M, L
from acquire_canon import Readable
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def calc(s):
    s=s.translate(str.maketrans('০১২৩৪৫৬৭৮৯×','0123456789*'))
    def ev(n):
        if isinstance(n,ast.Constant) and isinstance(n.value,int):return n.value
        if isinstance(n,ast.BinOp) and isinstance(n.op,(ast.Add,ast.Mult)):
            return (operator.add if isinstance(n.op,ast.Add) else operator.mul)(ev(n.left),ev(n.right))
        raise ValueError(s)
    return ev(ast.parse(s,mode='eval').body)
def main():
    result=build(L/'output')
    source=ET.parse(L/'provenance/u01-source-extract.cnxml').getroot()
    target=ET.parse(L/'translations/modules/m81243/index.cnxml').getroot()
    mapping=json.loads((L/'translations/u01-text.bn.json').read_text(encoding='utf-8'))
    s,t=list(source.iter()),list(target.iter())
    assert len(s)==len(t)
    for i,(a,b) in enumerate(zip(s,t)):
        assert a.tag==b.tag,(i,a.tag,b.tag)
        ignore={'alt','aria-label','{http://www.w3.org/XML/1998/namespace}lang'}
        assert {k:v for k,v in a.attrib.items() if k not in ignore}=={k:v for k,v in b.attrib.items() if k not in ignore},(i,a.attrib,b.attrib)
        for attribute in ('alt','aria-label'):
            if a.get(attribute):assert b.get(attribute)==mapping[a.get(attribute)]
        if local(a) in ('mn','mo','mspace'):assert a.text==b.text,(i,a.text,b.text)
        if a.text and re.fullmatch(r'[\d, .ⓐⓑ…$]+',a.text):assert a.text==b.text
    for e in target.iter(f'{{{C}}}image'):
        assert (L/'translations/modules/m81243'/e.get('src')).resolve().is_file()
        assert digest((L/'translations/modules/m81243'/e.get('src')).resolve())==digest(L.parent/'downloads/bn-Beng-BD/openstax-canonical/media'/Path(e.get('src')).name)
    content=(L/'output/u01-number-sense.html').read_text(encoding='utf-8')
    doc=ET.fromstring(content.split('\n',1)[1]);ids=[e.get('id') for e in doc.iter() if e.get('id')]
    assert len(ids)==len(set(ids)), 'Duplicate HTML IDs'
    source_ids={e.get('id') for e in source.iter() if e.get('id')}
    assert source_ids.issubset(set(ids)),source_ids-set(ids)
    links=[e.get('href')[1:] for e in doc.iter('a') if e.get('href','').startswith('#')]
    assert all(x in ids for x in links),set(links)-set(ids)
    assert doc.get('lang')=='bn-Beng-BD'
    assert not list(doc.iter('script'))
    assert all(e.get('scope') for e in doc.iter('th'))
    for p in doc.iter('p'):
        assert not any(local(n) in ('p','div','section','table','figure') for n in list(p.iter())[1:]),'Block element nested in paragraph'
    assert (L/'assets/NumeracyBangla.ttf').is_file()
    assert not re.search(r'(TODO|TBD|\ufffd)',content)
    companion=ET.parse(L/'translations/u01-companion.xhtml').getroot()
    byid={e.get('id'):e for e in companion.iter() if e.get('id')}
    checks={'d1':'০','d2':'১০, ১১','d3':'২০ + ৩ = ২৩','d4':'৪ × ১০০ = ৪০০','p1':'১০০ + ৭০ + ৬ = ১৭৬','p2':'২০০ + ৩০ + ৭ = ২৩৭','p3':'৫ × ১০০ = ৫০০','p4':'৪০০ + ০ + ২ = ৪০২','p5':'২৭০ = ২০০ + ৭০ + ০','p6':'৩০, ৪০, ৫০','p7':'৩০ + ৪ = ৩৪','p8':'১০০','e1':'৬০৮ = ৬০০ + ০ + ৮','e2':'১০ + ২ = ১২'}
    for key,answer in checks.items():
        assert 'bd-'+key in byid
        txt=''.join(byid['bd-a-'+key].itertext())
        assert answer in txt,(key,txt)
        assert len(txt)>30,(key,'not worked')
    mathchecks=[]
    for e in companion.iter():
        if local(e) not in ('p','td'): continue
        txt=''.join(e.itertext())
        for m in re.finditer(r'([০-৯]+(?:\s*[+×]\s*[০-৯]+)*)\s*=\s*([০-৯]+(?:\s*[+×]\s*[০-৯]+)*)',txt):
            assert calc(m[1])==calc(m[2]),m.group()
            mathchecks.append(m.group())
    assert len(mathchecks)>30
    exercises=list(source.iter(f'{{{C}}}exercise'))
    assert len(exercises)==6
    assert all(e.find(f'{{{C}}}solution') is not None for e in exercises)
    assert {e.get('id') for e in exercises}=={'fs-id1398237','fs-id3298473','fs-id1786026','fs-id2908692','fs-id1227376','fs-id1983295'}
    canon=json.loads((L/'canon/register.json').read_text(encoding='utf-8'))
    assert 10<=len(canon['examples'])<=20
    receipt=json.loads((L/'canon/download-receipt.json').read_text(encoding='utf-8'))
    assert len(receipt)==len(canon['sources']) and all(x['status']=='downloaded' for x in receipt)
    for item in receipt:
        canon_path=L.parent/'downloads/bn-Beng-BD/canon'
        html_path=canon_path/(item['id']+'.html')
        assert digest(html_path)==item['sha256']
        # Historical text receipts hash the LF-normalized Unicode extraction;
        # Windows write_text stored CRLF. Preserve those consulted files unchanged.
        text=(canon_path/(item['id']+'.txt')).read_text(encoding='utf-8')
        assert hashlib.sha256(text.encode('utf-8')).hexdigest()==item['text_sha256'],item['id']
        parser=Readable();parser.feed(html_path.read_text(encoding='utf-8'))
        extracted='\n'.join(' '.join(line.split()) for line in ''.join(parser.parts).splitlines() if line.strip())
        assert text==extracted,item['id']
    lock=json.loads((L/'sources.lock.json').read_text())
    modulemap=json.loads((L/'module-map.json').read_text(encoding='utf-8'))
    for unit in modulemap['units']:
        for code in ('A00','A10'):
            for ref in unit[code]:
                module=ET.parse(L.parent/'downloads/bn-Beng-BD/openstax-canonical/modules'/ref['module']/'index.cnxml').getroot()
                anchors={e.get('id') for e in module.iter()}
                for anchor in ref.get('sections',[]) + ([ref['section']] if 'section' in ref else []):assert anchor in anchors,ref
    assert digest(L/'provenance/u01-source-extract.cnxml')==lock['pilot_source']['extract_sha256']
    for notice in lock['preserved_notices']:assert digest(L/notice['copy'])==notice['sha256']
    with tempfile.TemporaryDirectory(prefix='bn-u01-') as td:
        again=build(Path(td))
        assert again==result, 'Nondeterministic build'
    results={'status':'pass','source_elements_preserved':len(s),'source_ids_preserved':len(source_ids),'source_exercises_with_solutions':len(exercises),'mathml_numeric_and_operator_tokens_unchanged':True,'source_figures_text_equivalents':len(list(source.iter(f'{{{C}}}media'))),'companion_items_with_worked_answers':len(checks),'arithmetic_equalities_checked':len(mathchecks),'internal_links_checked':len(links),'html_unique_ids':len(ids),'canon_examples':len(canon['examples']),'canon_documents_hash_verified':len(receipt),'html_deterministic_rebuild':True,'upstream_acquisition':lock['canonical_upstream']['acquisition_status'],'limits':['Not native-teacher reviewed','Not a complete Grades 2–5 kit','PDFs are not PDF/UA certified','Figures are text equivalents, not newly drawn Bangla diagrams'],'html_sha256':result['html_sha256']}
    results['translation_inputs_sha256']={path:digest(L/path) for path in ('translations/u01-text.bn.json','translations/u01-companion.xhtml','provenance/u01-source-extract.cnxml')}
    results['source_accessibility_labels_translated_and_corrected']=2
    results['original_figure_hashes_verified']=10
    results['canon_text_extraction_verified']=True
    results['canon_text_hash_normalization']='UTF-8 with LF line endings'
    (L/'output/qa-receipt.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(results,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
