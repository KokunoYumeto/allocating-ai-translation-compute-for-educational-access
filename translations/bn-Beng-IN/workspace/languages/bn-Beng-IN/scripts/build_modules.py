"""Assemble fully translated source modules and the offline navigation index."""
import copy,html,json,sys,xml.etree.ElementTree as ET
import build,build_sections,progress
from qa import Page

L=build.LANG

def catalog():
    rows=[]
    for q in sorted((L/'qa/sections').glob('*.json')):
        r=json.loads(q.read_text(encoding='utf-8'))
        p=L/'translations'/f'{r["module"]}-{r["section"]}.bn-Beng-IN.json'
        if r['result']!='pass' or not p.is_file() or build.sha(p)!=r['translation_sha256']:continue
        overlay=json.loads(p.read_text(encoding='utf-8'))
        _,target=build.translated(p)
        title=target.findtext(f'{{{build.C}}}title') or overlay.get('display_title') or r['section']
        rows.append((r['module'],title,r['reader'].removeprefix('reader/')))
    body='<h1>গণিতের বাংলা পাঠসূচি</h1><p class="notice">ভারতীয় বাংলা · অনুবাদ চলছে। এই সূচির পাঠগুলি সম্পূর্ণ বরাদ্দের একটি অংশ। মূল সূত্র, পরিচয়চিহ্ন ও ছবি সংরক্ষিত; মূল ছবির ইংরেজি লেখার অর্থ বাংলা বিবরণে দেওয়া আছে। স্বাধীন ভাষা/শিক্ষক, শিক্ষার্থী ও সহায়ক-প্রযুক্তি পর্যালোচনা বাকি।</p><h2>সহজ ভাষার সহায়িকা</h2><ul><li><a href="U01-companion.html">U01 · ভগ্নাংশ থেকে সমীকরণ</a> — মূল পাঠ থেকে পৃথক, নতুন/অভিযোজিত সহায়িকা</li></ul><h2>সম্পূর্ণ অনূদিত মডিউল</h2><ul>'
    for p in sorted((L/'qa/modules').glob('*.json')):
        r=json.loads(p.read_text(encoding='utf-8'))
        if r['result']=='pass':body+=f'<li><a href="{r["reader"].removeprefix("reader/")}">{html.escape(r["title"])}</a> · {r["module"]} — উৎসের সব পাঠ্যাংশ অন্তর্ভুক্ত; পর্যালোচনার সীমা পাঠে দেওয়া আছে।</li>'
    body+='</ul>'
    if (L/'reader/U02-companion.html').is_file():body+='<p><a href="U02-companion.html">U02 · লঘিষ্ঠ আকার, গুণ ও ভাগ — পৃথক সহায়িকা</a></p>'
    if (L/'reader/U03-companion.html').is_file():body+='<p><a href="U03-companion.html">U03 · মিশ্র ভগ্নাংশ ও ভগ্নাংশ-রেখা — পৃথক সহায়িকা</a></p>'
    if (L/'reader/U04-companion.html').is_file():body+='<p><a href="U04-companion.html">U04 · ভগ্নাংশের যোগ ও বিয়োগ — পৃথক সহায়িকা</a></p>'
    if (L/'reader/U05-companion.html').is_file():body+='<p><a href="U05-companion.html">U05 · মিশ্র ভগ্নাংশের যোগ ও বিয়োগ — পৃথক সহায়িকা</a></p>'
    if (L/'reader/U06-companion.html').is_file():body+='<p><a href="U06-companion.html">U06 · দশমিক, ভগ্নাংশ ও সমীকরণ — পৃথক সহায়িকা</a></p>'
    body+='<h2>পৃথক অনূদিত অংশ</h2><ul>'
    for module,title,reader in rows:body+=f'<li><a href="{reader}">{html.escape(title)}</a> · {module}</li>'
    body+='</ul>'
    (L/'reader/index.html').write_text(build.page('গণিতের বাংলা পাঠসূচি',body),encoding='utf-8')

def build_one(module):
    source=ET.parse(build.module_source(module)).getroot()
    target=copy.deepcopy(source)
    inputs={};errata=[];blocks=[]
    parents={id(c):e for e in target.iter() for c in e}
    for ident,kind,old in progress.required_blocks(target):
        path=L/'translations'/f'{module}-{ident}.bn-Beng-IN.json'
        assert path.is_file(),f'Module incomplete: {module}/{ident}'
        receipt=build_sections.build_one(path.name)
        canon=L/'canon/sections'/f'{module}-{ident}.json'
        if ident=='fs-id1726667':canon=L/'canon/consultations.json'
        assert canon.is_file(),f'Missing actual canon consultation record: {ident}'
        original,replacement=build.translated(path)
        assert ET.tostring(old)==ET.tostring(original),(module,ident,'source block mismatch')
        parent=parents[id(old)];position=list(parent).index(old)
        parent.remove(old);parent.insert(position,replacement)
        inputs[path.relative_to(L).as_posix()]=build.sha(path)
        inputs[canon.relative_to(L).as_posix()]=build.sha(canon)
        blocks.append(ident);errata+=receipt['source_errata']
    title=target.findtext(f'{{{build.C}}}title')
    target.set('{http://www.w3.org/XML/1998/namespace}lang','bn-Beng-IN')
    meta_title=target.find(f'{{{build.C}}}metadata/{{{build.D}}}title')
    if meta_title is not None:meta_title.text=title
    assert [e.tag for e in source.iter()]==[e.tag for e in target.iter()]
    assert [e.get('id') for e in source.iter()]==[e.get('id') for e in target.iter()]
    assert len(build.math_signature(source))==len(build.math_signature(target))
    rendered=ET.Element(f'{{{build.C}}}section')
    abstract=target.find(f'{{{build.C}}}metadata/{{{build.D}}}abstract')
    if abstract is not None:rendered.append(copy.deepcopy(abstract))
    for e in target.find(f'{{{build.C}}}content'):rendered.append(copy.deepcopy(e))
    glossary=target.find(f'{{{build.C}}}glossary')
    if glossary is not None:
        g=copy.deepcopy(glossary);heading=ET.Element(f'{{{build.C}}}title');heading.text='শব্দার্থ'
        g.insert(0,heading);rendered.append(g)
    intro=f'<h1>{html.escape(title)}</h1><p class="notice">উৎস-অনুগত সম্পূর্ণ মডিউল · A00 / {module}। সম্পূর্ণ বইয়ের অনুবাদ এখনও চলছে। গণিত, প্রশ্ন, উপস্থিত সমাধান, মূল পরিচয়চিহ্ন ও ছবি সংরক্ষিত। সূত্রের শব্দলেবেল ও ছবি-বিবরণ বাংলায় অনূদিত। যেসব প্রশ্নের উত্তর মূল উৎসে নেই, এখানে সেগুলিতে নতুন উত্তর যোগ করা হয়নি। মূল ছবিতে থাকা ভুল/ইংরেজি লেবেলের ক্ষেত্রে বাংলা বিবরণ ও সম্পাদকীয় সতর্কতা পড়ো। স্বাধীন বাংলা ভাষা/শিক্ষক, শিক্ষার্থী ও সহায়ক-প্রযুক্তি পর্যালোচনা বাকি। বাইরের উৎস-লিঙ্কে ইন্টারনেট প্রয়োজন।</p>'
    footer='<footer>OpenStax, Rice University · Prealgebra 2e · Lynn Marecek, MaryAnne Anthony-Smith, Andrea Honeycutt Mathis। <a href="../../provenance/pilot/m81241.source.cnxml">পূর্ণ উৎস-স্বীকৃতি</a> · <a href="../../provenance/A00/repository/LICENSE">CC BY-NC-SA 4.0 ও উপাদানভিত্তিক শর্ত</a>। অনানুষ্ঠানিক অনুবাদ; মূল প্রকাশকের অনুমোদন দাবি করা হচ্ছে না।</footer>'
    result=build_sections.reader_page(title,intro+build.render_cnxml(rendered,module,'../../provenance/pilot/media/',study_labels=True)+footer)
    reader=L/'reader/modules'/f'{module}.html';reader.parent.mkdir(parents=True,exist_ok=True)
    reader.write_text(result,encoding='utf-8')
    output=L/'translations'/f'{module}.bn-Beng-IN.cnxml';output.write_bytes(ET.tostring(target,encoding='utf-8',xml_declaration=True))
    page=Page();page.feed(result)
    assert page.lang=='bn-Beng-IN' and not page.scripts and len(page.ids)==len(set(page.ids))
    for href in page.links:
        if href.startswith('#'):assert href[1:] in page.ids,href
        elif not href.startswith('https:'):assert (reader.parent/href).is_file(),href
    assert all(i.get('alt') and (reader.parent/i['src']).is_file() for i in page.images)
    receipt={'result':'pass','module':module,'title':title,'coverage':'all learner-facing source blocks including title, objectives, content and glossary',
             'source_sha256':build.sha(build.module_source(module)),'blocks':blocks,'inputs':inputs,
             'builders':{f'scripts/{n}':build.sha(L/'scripts'/n) for n in ['build.py','build_sections.py','build_modules.py','progress.py']},
             'reader':reader.relative_to(L).as_posix(),'reader_sha256':build.sha(reader),'cnxml_sha256':build.sha(output),
             'nodes':sum(1 for e in source.iter()),'ids':sum(bool(e.get('id')) for e in source.iter()),'mathml':len(build.math_signature(source)),
             'images':len(page.images),'source_errata':errata,'visual_review':'pending','independent_human_review':'pending'}
    q=L/'qa/modules';q.mkdir(parents=True,exist_ok=True)
    (q/f'{module}.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return receipt

if __name__=='__main__':
    catalog()
    for module in sys.argv[1:]:
        r=build_one(module)
        print(json.dumps({k:r[k] for k in ['module','result','nodes','ids','mathml','images']},ensure_ascii=False))
    catalog()
