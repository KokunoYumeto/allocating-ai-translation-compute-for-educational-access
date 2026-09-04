"""Bounded recovery builder. Writes only alongside this script; inputs are read-only.

Usage: python build_package.py EXPORT_LANGUAGE_DIR EXPORT_MANIFEST JVSOURCE JV_ASSETS
The reusable Reader class is mechanically extracted from the inspected recovered
A10-007 renderer, with no old entry point, path imports or preparer executed.
"""
import ast, collections, copy, hashlib, html, json, re, sys, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit
from lxml import html as LH

BASE = Path(__file__).resolve().parent
MATH = 'http://www.w3.org/1998/Math/MathML'
MATH_TAG = '{'+MATH+'}math'
ET.register_namespace('', MATH)
PARTS = {'ⓐ':'a','ⓑ':'b','ⓒ':'c','ⓓ':'d','ⓔ':'e'}
LONG_PARTS = set()
STRUCTURAL_CHILDREN = {'list','table','media','para','note','figure'}
def tag(n): return n.tag.split('}')[-1]
def attr(v): return html.escape(str(v),quote=True)
def require(v,m):
    if not v: raise ValueError(m)
def digest(b): return hashlib.sha256(b).hexdigest()
def write(p,b):
    p=BASE/p; require(p.resolve().is_relative_to(BASE),'write boundary'); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes(b if isinstance(b,bytes) else b.encode('utf-8'))
def dump(p,v): write(p,json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def tree(n): return (n.tag,tuple(sorted(n.attrib.items())),(n.text or '').strip(),tuple((tree(c),(c.tail or '').strip()) for c in n))

def main():
    src,export_path,jvsource,jvassets=map(Path,sys.argv[1:5])
    raw=export_path.read_bytes(); require(digest(raw)=='772c054d8b6f9337f62a89df2fc2c726ed2d97c9077cb07f07dd0150e5ffe5a1','export pin')
    export=json.loads(raw); records={r['source_path']:r for r in export['files'] if r.get('lane')=='pnb-Arab-PK' and r.get('source_path')}
    selected=[]
    def select(rel,target=None):
        b=(src/rel).read_bytes(); r=records[rel]
        require(digest(b)==r['export_sha256'] and len(b)==r['bytes'],'export changed: '+rel)
        target=target or rel; write(target,b)
        selected.append({'export_path':r['path'],'path':target,'bytes':len(b),'sha256':digest(b)})
        return b
    units=['a10-preface','a10-introduction']+['a10-unit-%03d'%i for i in range(1,9)]
    for u in units:
        select('source-excerpts/'+u+'.cnxml'); select('translations/'+u+'.json')
        if u!='a10-unit-008':
            suf=u.replace('a10-unit-','a10-')
            select('source-excerpts/manifest-'+suf+'.json')
            select('reader/'+u+'.html')
            select('provenance/'+u+'-component-notices.json')
    select('plans/A10-008-scope.json','source-excerpts/selection-a10-008.json')
    select('styles/reader.css')
    select('provenance/A10-release/NOTICE.txt')
    select('provenance/upstream--osbooks-prealgebra-bundle/LICENSE')
    write('LICENSE.txt',(BASE/'provenance/upstream--osbooks-prealgebra-bundle/LICENSE').read_bytes())
    pins=[]
    for rel in ['canon/examples.json','canon/supplemental-number-wording.json','styles/reader.css']:
        b=(src/rel).read_bytes(); require(digest(b)==records[rel]['export_sha256'],'canon/style pin')
        pins.append({'export_path':records[rel]['path'],'sha256':digest(b),'bytes':len(b),'treatment':'read-only shared pin; not a mathematical certification'})
    dump('provenance/SHARED_CANON_PINS.json',{'pins':pins,'scope':'Three essays support grammar/register only; no shared canon edited.'})
    # Copy only image files actually referenced by selected readers.
    assets=set()
    for u in units[:-1]:
        doc=LH.fromstring((BASE/'reader'/f'{u}.html').read_text(encoding='utf-8'))
        for im in doc.xpath('//img[@src]'):
            path=unquote(urlsplit(im.get('src')).path)
            if path.startswith('../assets/a10/'): assets.add(path[3:])
    for rel in sorted(assets): select(rel)
    plan=json.loads((BASE/'source-excerpts/selection-a10-008.json').read_bytes())
    canonical=jvsource.read_bytes(); require(digest(canonical)==plan['canonical_sha256'],'canonical m82453 pin')
    write('source/m82453.en.cnxml',canonical)
    root=ET.fromstring(canonical); content=root.find('{http://cnx.rice.edu/cnxml}content')
    excerpt=ET.parse(BASE/'source-excerpts/a10-unit-008.cnxml').getroot()
    require(tree(excerpt[0])==tree(content[3]),'entire section identity')
    require(content[4].get('id')=='fs-id1170655163482','next sibling')
    for rec in plan['images']:
        target=BASE/rec['future_reader_path']
        b=target.read_bytes() if target.exists() else (jvassets/Path(rec['source_path']).name).read_bytes()
        if digest(b)!=rec['sha256']:
            url='https://raw.githubusercontent.com/openstax/osbooks-prealgebra-bundle/'+plan['canonical_commit']+'/'+rec['source_path']
            b=urllib.request.urlopen(url,timeout=45).read()
        require(digest(b)==rec['sha256'] and len(b)==rec['bytes'],'A10-008 image pin')
        write(rec['future_reader_path'],b)
    # Official collection and complete source witnesses, bounded to four modules.
    upstream='https://raw.githubusercontent.com/openstax/osbooks-prealgebra-bundle/'+plan['canonical_commit']+'/'
    specs=[('collections/elementary-algebra-2e.collection.xml','source/collection.xml',plan['collection']['sha256'])]
    for u in ['a10-preface','a10-introduction','a10-001']:
        man=json.loads((BASE/'source-excerpts'/('manifest-'+u+'.json')).read_bytes())
        module=man['module']; target='source/'+module+'.en.cnxml'
        if module == 'm82630':
            data=(BASE/'source-excerpts'/('a10-preface.cnxml' if module=='m82630' else 'a10-introduction.cnxml')).read_bytes()
            require(digest(data)==man['full_module_sha256'],'complete witness pin'); write(target,data)
        else: specs.append(('modules/'+module+'/index.cnxml',target,man['full_module_sha256']))
    for remote,target,sha in specs:
        p=BASE/target
        data=p.read_bytes() if p.exists() else urllib.request.urlopen(upstream+remote,timeout=45).read()
        require(digest(data)==sha,'official source pin '+remote); write(target,data)
    coll=ET.parse(BASE/'source/collection.xml').getroot()
    modules=[n.get('document') for n in coll.iter() if tag(n)=='module']
    require(modules[:4]==['m82630','m82451','m82452','m82453'] and len(modules)==82,'collection membership')
    # Extract inspected reusable class without executing recovered script entry point/imports.
    raw_renderer=select('scripts/build_a10_007.py','source/recovered-renderer.py')
    syntax=ast.parse(raw_renderer.decode('utf-8'))
    chosen=[n for n in syntax.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in {'Reader','compact','inner_xml','fragment_text'}]
    chosen += [n for n in syntax.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='LOCAL_CSS' for t in n.targets)]
    exec(compile(ast.Module(body=chosen,type_ignores=[]),'source/recovered-renderer.py','exec'),globals())
    tr=json.loads((BASE/'translations/a10-unit-008.json').read_bytes())
    tr['status']='Complete recovered section, revised and source-bound built; deterministic and actual visual results in QA.json. Terminology is provisional, not linguistically certified.'
    # Correct literal backslash-n draft artifacts, not source text or formulas.
    for k,v in tr['source_blocks'].items(): tr['source_blocks'][k]=v.replace('\\n','\n')
    dump('translations/a10-unit-008.json',tr)
    man=copy.deepcopy(plan)
    man['example_labels']=[{'id':n.get('id'),'local_label':'E'+str(i)} for i,n in enumerate([n for n in excerpt.iter() if tag(n)=='example'],1)]
    man['table_summary_overrides']=tr['table_summary_overrides']
    for im in man['images']:
        key=im['media_id']+'/alt'; im['path']=im['future_reader_path']; im['original_bilingual_key_id']=tr['retained_image_keys'][key]; im['source_alt_override']=tr['image_alt_overrides'].get(key)
    reader=Reader(man,excerpt,tr)
    body=reader.render(excerpt)
    require(reader.used==list(tr['source_blocks']) and len(reader.used)==91,'008 block coverage')
    mapped={n for n in excerpt.iter() if not n.tag.startswith('{'+MATH+'}') or n.tag==MATH_TAG}
    require(reader.bound==mapped,'008 source binding coverage')
    before,after,last=reader.bridges()
    css=(BASE/'styles/reader.css').read_text(encoding='utf-8')+LOCAL_CSS
    # The Reader's leaf wrapper is repaired structurally using source keys before parsing.
    for key in ['fs-id1166424830192','fs-id1167829683833','fs-id1166424780807','fs-id1167836730046','fs-id1169149281503']:
        start=body.index('<p ',body.index('id="'+key+'"')-3); end=body.index('</p>',start)
        # First closing p belongs to nested UI: find wrapper boundary by balanced p tokens.
        depth=0
        for mt in re.finditer(r'<p\b[^>]*>|</p>',body[start:]):
            depth += -1 if mt[0]=='</p>' else 1
            if depth==0: end=start+mt.start(); break
        body=body[:end]+'</div>'+body[end+4:]; body=body[:start]+'<div'+body[start+2:]
    footer='''<footer id="credits" lang="en" dir="ltr"><h2>Source and changes</h2><p>OpenStax Elementary Algebra 2e, module m82453, source commit 38cae454e644abf9f0a623e876994553881597c9. Original senior contributing authors: Lynn Marecek, MaryAnne Anthony-Smith, Andrea Honeycutt Mathis; OpenStax/Rice University. Shahmukhi Punjabi adaptation with OpenAI Codex assistance. No endorsement is implied.</p><p><a href="../LICENSE.txt">CC BY-NC-SA 4.0</a>, subject to inherited component notices. <a href="../provenance/A10-release/NOTICE.txt">Inherited A10 release notice</a>. All 16 source JPEGs and 38 MathML trees are preserved. Nine exercises and nine supplied solutions are source content. Separately labeled original notes explain source wording/pixel discrepancies; no new source answer is invented.</p><p>Complete section fs-id1170654889475 through final descendant fs-id1170655106384. Next: fs-id1170655163482, Identify and Combine Like Terms. This is not the whole module or book. <a href="../source-excerpts/a10-unit-008.cnxml">Exact source witness</a> · <a href="../LANGUAGE_NOTES.md">Language evidence and limits</a>.</p></footer>'''
    result='<!doctype html>\n<html lang="pnb-Arab-PK" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+tr['title']+'</title><style>'+css+'</style></head><body class="a10-reader a10-007-reader"><header><h1>'+tr['title']+'</h1></header><main>'+before+body+after+last+'</main>'+footer+'</body></html>'
    write('reader/a10-unit-008.html',result)
    dump('provenance/a10-unit-008-component-notices.json',{'source_commit':plan['canonical_commit'],'inherited_notice':'A10-release/NOTICE.txt','images':[{k:r[k] for k in ['media_id','source_path','sha256','bytes','width','height','git_blob_sha1','source_declared_mime']} for r in plan['images']],'scope':'Byte identity is not a new image-specific license clearance; inherited component restrictions retained.'})
    # Add book-level navigation without changing recovered source-bound content.
    reader_changes=[]
    for i,u in enumerate(units):
        p=BASE/'reader'/f'{u}.html'; text=p.read_text(encoding='utf-8'); old=digest(p.read_bytes())
        links='<a href="../index.html">کتاب دی فہرست</a>'
        if i: links+=' · <a href="'+units[i-1]+'.html">پچھلا سبق</a>'
        if i+1<len(units): links+=' · <a href="'+units[i+1]+'.html">اگلا سبق</a>'
        nav='<nav class="package-navigation" aria-label="کتاب دی رہنمائی">'+links+'</nav>'
        text=text.replace('<main>',nav+'<main>',1)
        text=re.sub(r'\.\./qa/a10-[a-z0-9-]+-language-notes\.md','../LANGUAGE_NOTES.md',text)
        # Local reader-first navigation; historical within-unit notes remain source provenance, not a live cursor.
        extra='\n.package-navigation{max-width:1000px;margin:auto;padding:1rem 2rem;background:#dae9e2;font-size:1rem}.source-para{min-width:0}.package-navigation a{white-space:nowrap}@media(max-width:600px){header,main,footer{padding:1rem 1.1rem}body{font-size:19px}h1{font-size:1.9rem}}\n'
        text=text.replace('</style>',extra+'</style>',1)
        write('reader/'+u+'.html',text)
        reader_changes.append({'reader':'reader/'+u+'.html','before_sha256':old,'after_sha256':digest(text.encode()),'changes':'Added package previous/next/index navigation, mobile padding, local language-note target; A10-008 newly built.'})
    dump('provenance/RECOVERY_SELECTION.json',{'manifest_sha256':digest(raw),'selected_export_files':selected,'reader_changes':reader_changes,'method':'Each selected exported file rehashed before copying. No entire language lane copied. A10-008 source and assets separately verified against canonical pins.'})
    titles=[json.loads((BASE/'translations'/f'{u}.json').read_bytes()).get('title',u) for u in units]
    items=''.join('<li><a href="reader/'+u+'.html">'+attr(t)+'</a><span lang="en" dir="ltr"> — '+u+'</span></li>' for u,t in zip(units,titles))
    index='''<!doctype html><html lang="pnb-Arab-PK" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ابتدائی الجبرا — پنجابی شاہ مکھی</title><style>body{margin:0;background:#edf1ee;color:#173434;font:21px/2.3 "Urdu Typesetting","Noto Naskh Arabic","Segoe UI",serif}main{max-width:850px;margin:auto;padding:2rem;background:#fffdf8}h1{line-height:1.8}h2{color:#1b6159}a{color:#175b94}li{margin:.6rem 0}bdi,[dir=ltr]{unicode-bidi:isolate}[lang=en]{font:16px/1.6 "Segoe UI",sans-serif}aside{border-right:4px solid #b98238;padding:.7rem 1rem;background:#f8f3e8} @media(max-width:600px){main{padding:1.2rem}body{font-size:19px}h1{font-size:1.8rem}}</style></head><body><main><p>پنجابی · شاہ مکھی · پاکستان</p><h1>ابتدائی الجبرا</h1><p><bdi lang="en">OpenStax Elementary Algebra 2e</bdi> دا ماخذ نال جڑیا پنجابی ترجمہ</p><aside>ایہہ پوری کتاب نہیں۔ دیباچہ، باب دا تعارف تے «پورے عدد» دا پورا سبق شامل نیں۔ «الجبرے دی زبان» دے پہلے تِن سیکشن، جبری عبارت دی قدر کڈھن تک، شامل نیں۔</aside><h2>پڑھنا شروع کرو</h2><ol>'''+items+'''</ol><h2>پڑھت بارے</h2><p>ایہہ پیکج انٹرنیٹ توں بناں وی کھلدا اے۔ پنجابی نثر سجّے توں کھبّے اے؛ فارمولا تے حسابی جدول کھبّے توں سجّے نیں۔ چھوٹی سکرین اُتے وڈے جدول نوں پاسے سرکاؤ۔ ماخذ دے سوال تے دِتّے حل اصل مواد نیں؛ مترجم دیاں وضاحتاں وکھریاں نشان لائیاں نیں۔ اردو تے انگریزی صرف لفظ سمجھاؤن دے پُل نیں، پنجابی متن دی تھاں نہیں۔</p><p>اگلا سیکشن: ہم جنس اجزا پہچانو تے اکٹھے کرو — <bdi lang="en">fs-id1170655163482</bdi>۔ باقی کتاب اِس پیکج وچ نہیں۔</p><section lang="en" dir="ltr"><h2>About this bounded edition</h2><p>Three complete source modules out of 82: Preface (m82630), Introduction (m82451), Whole Numbers (m82452). Partial m82453 includes its opening plus three complete instructional sections, ending Evaluate an Expression. Ten reading pages. This preserves and extends recovered drafts; it is not a complete new book or linguistic certification.</p><p>Original authors: Lynn Marecek; MaryAnne Anthony-Smith; Andrea Honeycutt Mathis. OpenStax/Rice University. Punjabi adaptation with OpenAI Codex assistance. No endorsement implied. <a href="LICENSE.txt">CC BY-NC-SA 4.0</a>, subject to inherited component restrictions. <a href="provenance/A10-release/NOTICE.txt">Source notice</a>.</p><p><a href="LANGUAGE_NOTES.md">Language evidence and limits</a> · <a href="PACKAGE.json">Exact coverage and pins</a> · <a href="QA.json">Verification results</a> · <a href="SHA256SUMS">Checksums</a></p></section></main></body></html>'''
    write('index.html',index)
    print('Built 10 reading pages, selected',len(selected),'exported files. Next: QA and visual inspection.')

if __name__=='__main__': main()
