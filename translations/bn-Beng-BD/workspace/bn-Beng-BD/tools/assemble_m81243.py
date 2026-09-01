"""Assemble the complete first instructional module, including all ancillary text."""
from pathlib import Path
import copy, hashlib, html, json, re
import xml.etree.ElementTree as ET
from build import C,M,L,STYLE,NOTICE,attrs,inner,local,render,write
from build_unit import build
MD='http://cnx.rice.edu/mdml'
sha=lambda b:hashlib.sha256(b).hexdigest()

def assemble():
    canonical=L.parent/'downloads/bn-Beng-BD/openstax-canonical/modules/m81243/index.cnxml'
    assert sha(canonical.read_bytes())=='396b0029798e054e5db6d7acde738cec9f9d8b86bc81da8cc3690d01ec07cf2b'
    source=ET.parse(canonical).getroot();target=copy.deepcopy(source)
    # Refresh the section receipts instead of trusting stale files after compaction.
    receipts={u:build(u) for u in ('U02A','U02B','U02C','U02D','U02E')}
    from build import build as build_u01
    receipt_u01=build_u01(L/'output')
    files=['translations/modules/m81243/index.cnxml']+['translations/modules/m81243/'+u.lower()+'.cnxml' for u in receipts]
    sections={};input_hashes={}
    for name in files:
        path=L/name;input_hashes[name]=sha(path.read_bytes())
        for e in ET.parse(path).getroot():
            assert local(e)=='section' and e.get('id') not in sections
            sections[e.get('id')]=e
    content=target.find('{'+C+'}content');old_content=source.find('{'+C+'}content')
    assert [e.get('id') for e in old_content]==list(sections),'Missing, reordered or extra content section'
    for i,old in enumerate(list(content)):content[i]=copy.deepcopy(sections[old.get('id')])
    mapping=json.loads((L/'translations/m81243-extras.bn.json').read_text(encoding='utf-8'))
    used=set();slots=0
    excluded=set(content.iter())
    for e in target.iter():
        if e in excluded:continue
        for prop in ('text','tail','alt','aria-label'):
            attr=prop in ('alt','aria-label');v=e.get(prop) if attr else getattr(e,prop)
            if v in mapping:
                if attr:e.set(prop,mapping[v])
                else:setattr(e,prop,mapping[v])
                used.add(v);slots+=1
            elif v and re.search('[A-Za-z]',v):
                assert local(e) in ('content-id','uuid'),(e.tag,v)
    assert used==set(mapping)
    target.set('{http://www.w3.org/XML/1998/namespace}lang','bn-Beng-BD')
    assert len(list(source.iter()))==len(list(target.iter()))
    for a,b in zip(source.iter(),target.iter()):
        assert a.tag==b.tag
        omissions={'alt','aria-label','{http://www.w3.org/XML/1998/namespace}lang'}
        assert {k:v for k,v in a.attrib.items() if k not in omissions}=={k:v for k,v in b.attrib.items() if k not in omissions}
        if local(a) in ('mn','mo','mspace') or (local(a)=='mtext' and re.fullmatch(r'[$0-9, .;]+',a.text or '')):assert a.text==b.text
        if a not in set(old_content.iter()) and local(a) in ('content-id','uuid'):assert a.text==b.text
    source_ids={e.get('id') for e in source.iter() if e.get('id')}
    assert source_ids=={e.get('id') for e in target.iter() if e.get('id')}
    output=L/'translations/complete_modules/m81243/index.cnxml';output.parent.mkdir(parents=True,exist_ok=True)
    data=ET.tostring(target,encoding='utf-8',xml_declaration=True);output.write_bytes(data)
    title=target.findtext('{'+C+'}title')
    abstract=target.find('{'+C+'}metadata').find('{'+MD+'}abstract')
    glossary=target.find('{'+C+'}glossary')
    glossary_html='<section id="bd-m81243-glossary"><h2>শব্দার্থ</h2><dl>'
    for definition in glossary:
        term=definition.find('{'+C+'}term');meaning=definition.find('{'+C+'}meaning')
        glossary_html+=f'<div{attrs(definition)}><dt{attrs(term)}>{inner(term)}</dt><dd{attrs(meaning)}>{inner(meaning)}</dd></div>'
    glossary_html+='</dl></section>'
    notice=NOTICE.replace('module m81243, sections fs-id1830385 and fs-id2340048','complete module m81243, including title, objectives, all eight content sections and glossary').replace('Faithful extract retains','Faithful module retains').replace('2026-08-30.','2026-08-30–31.')
    navigation='<nav aria-label="অনুবাদ ও সহায়িকা"><a href="#bd-m81243-objectives">শেখার লক্ষ্য</a> · <a href="#bd-m81243-glossary">শব্দার্থ</a> · <a href="../U02E/index.html#bd-u02e-answers">অনুশীলনের সব পূর্ণ উত্তর</a></nav>'
    introduction='<aside><p>এটি সম্পূর্ণ উৎস-মডিউলের বিশ্বস্ত অনুবাদের খসড়া, শিশুবান্ধব সংক্ষিপ্ত পাঠ নয়। উৎসের সংখ্যা, একক, গঠন, সব অনুশীলন এবং দেওয়া সমাধান রাখা হয়েছে। সব 58টি শেষের অনুশীলনের অতিরিক্ত পূর্ণ উত্তর আলাদা সহায়িকায় আছে। পুরোনো জনসংখ্যা ও আপেক্ষিক সময় উৎসের প্রেক্ষাপট; বর্তমান তথ্য নয়।</p><p>পাঠের সহজ রূপ ও নির্দেশনামূলক উদাহরণের বাড়তি ব্যাখ্যা: <a href="../u01-number-sense.html">U01</a>, <a href="../U02A/index.html">U02A</a>, <a href="../U02B/index.html">U02B</a>, <a href="../U02C/index.html">U02C</a>, <a href="../U02D/index.html">U02D</a>। বাংলাদেশের শিক্ষকের পর্যালোচনা এবং এই পূর্ণ মডিউলের চাক্ষুষ/PDF যাচাই এখনও বাকি।</p></aside>'
    body='<header><p>bn-Beng-BD · A00 · m81243 · পূর্ণ খসড়া</p><h1>'+html.escape(title)+'</h1>'+navigation+'</header>'+introduction+'<section id="bd-m81243-objectives"><h2>শেখার লক্ষ্য</h2>'+inner(abstract)+'</section>'+''.join(render(e) for e in content)+glossary_html+notice
    page='<!DOCTYPE html>\n<html lang="bn-Beng-BD"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><title>'+html.escape(title)+'</title><style>'+STYLE.replace('../assets/','../../assets/')+'\n.circled{list-style:none}dd{margin-bottom:1rem}</style></head><body><main>'+body+'</main></body></html>\n'
    doc=ET.fromstring(page.split('\n',1)[1]);ids=[e.get('id') for e in doc.iter() if e.get('id')]
    assert len(ids)==len(set(ids)) and source_ids<=set(ids)
    for p in doc.iter('p'):assert not any(local(e) in ('div','table','p','ul','ol','section','figure') for e in list(p.iter())[1:])
    for a in doc.iter('a'):
        href=a.get('href','')
        if href.startswith('#'):assert href[1:] in ids
        elif href and not href.startswith(('https://','http://')):
            path,_,fragment=href.partition('#');other=L/'output/m81243'/path
            assert other.is_file()
            if fragment:assert 'id="'+fragment+'"' in other.read_text(encoding='utf-8')
    for image in target.iter('{'+C+'}image'):
        dest=(output.parent/image.get('src')).resolve()
        expected=L.parent/'downloads/bn-Beng-BD/openstax-canonical/media'/dest.name
        assert dest.read_bytes()==expected.read_bytes()
    write(L/'output/m81243/index.html',page)
    receipt={'module':'m81243','status':'complete_source_translation_structural_math_pass','entire_assignment_complete':False,
             'source_sha256':sha(canonical.read_bytes()),'whole_document_elements':len(list(source.iter())),
             'all_source_ids':len(source_ids),'content_sections':len(sections),'glossary_definitions':len(glossary),
             'extra_translation_slots':slots,'extra_unique_strings':len(mapping),
             'source_exercises':len(list(source.iter('{'+C+'}exercise'))),'source_supplied_solutions':len(list(source.iter('{'+C+'}solution'))),
             'all_58_practice_exercises_have_separate_worked_answers':True,
             'translation_sha256':sha(data),'html_sha256':sha(page.encode('utf-8')),
             'section_input_sha256':input_hashes,'extra_input_sha256':sha((L/'translations/m81243-extras.bn.json').read_bytes()),
             'original_media_references_verified':len(list(target.iter('{'+C+'}image'))),
             'limits':['AI-assisted source translation draft; native Bangladesh teacher fluency review pending','Complete module HTML is structurally checked, not browser-visual checked','U02 PDF/print/screen workflow remains pending','74 other A00 modules plus selected A10 and other companion domains remain']}
    write(L/'output/m81243/qa-receipt.json',json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    return receipt
if __name__=='__main__':
    a=assemble();assert assemble()==a
    print(json.dumps(a,ensure_ascii=False,indent=2))
