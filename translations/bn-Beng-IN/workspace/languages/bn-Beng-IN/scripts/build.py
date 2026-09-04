"""Deterministic, dependency-free offline pilot builder and structural gate."""
from pathlib import Path
import copy
import hashlib
import html
import json
import re
import shutil
import xml.etree.ElementTree as ET

LANG=Path(__file__).resolve().parents[1]
C='http://cnx.rice.edu/cnxml'
M='http://www.w3.org/1998/Math/MathML'
D='http://cnx.rice.edu/mdml'
ET.register_namespace('',C)
ET.register_namespace('m',M)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def local(e): return e.tag.rsplit('}',1)[-1]
def math_signature(root):
    def sig(e): return (e.tag,sorted(e.attrib.items()),e.text or '',[(sig(c),c.tail or '') for c in e])
    return [sig(e) for e in root.iter(f'{{{M}}}math')]

def module_source(module):
    for p in [LANG/f'provenance/pilot/{module}.source.cnxml',LANG/f'provenance/modules/{module}.source.cnxml']:
        if p.is_file():return p
    raise FileNotFoundError(f'Freeze canonical module witness before building: {module}')

def translated(overlay_path=None):
    overlay=json.loads((overlay_path or LANG/'translations/m81285-fs-id1726667.bn-Beng-IN.json').read_text(encoding='utf-8'))
    assert overlay['locale']=='bn-Beng-IN'
    document=ET.parse(module_source(overlay['module']))
    if overlay.get('source_xpath'):
        assert overlay['section'].startswith('__'),'XPath blocks must have explicit synthetic coverage IDs'
        matches=document.findall(overlay['source_xpath'],{'c':C,'m':M,'md':D})
        assert len(matches)==1,(overlay['source_xpath'],len(matches))
        source=matches[0]
    else:source=document.find(f'.//*[@id="{overlay["section"]}"]')
    assert source is not None,overlay['section']
    target=copy.deepcopy(source)
    def slots(e,values):
        assert not e.tag.startswith(f'{{{M}}}'),'Use explicit math_text for linguistic mtext only'
        assert len(values)==len(e)+1,(e.get('id'),len(values),len(e))
        e.text=values[0]
        for child,tail in zip(e,values[1:]):child.tail=tail
    def unique(root,xpath):
        matches=root.findall(xpath,{'c':C,'m':M,'md':D})
        assert len(matches)==1,(xpath,len(matches))
        return matches[0]
    path_alts={id(unique(target,xpath)):value for xpath,value in overlay.get('alt_paths',{}).items()}
    for e in target.iter():
        eid=e.get('id')
        if eid in overlay['paragraphs']:
            slots(e,overlay['paragraphs'][eid])
        if local(e)=='title' and (e.text or '').strip():
            e.text=overlay['titles'][e.text]
        if eid in overlay['terms']: e.text=overlay['terms'][eid]
        if 'alt' in e.attrib: e.set('alt',overlay['alt'][eid] if eid in overlay['alt'] else path_alts[id(e)])
        if eid in overlay.get('aria_labels',{}):
            assert 'aria-label' in e.attrib
            e.set('aria-label',overlay['aria_labels'][eid])
        if eid in overlay.get('summaries',{}):
            assert 'summary' in e.attrib
            e.set('summary',overlay['summaries'][eid])
    for xpath,values in overlay.get('nodes',{}).items():slots(unique(target,xpath),values)
    for xpath,value in overlay.get('math_text',{}).items():
        e=unique(target,xpath)
        assert e.tag==f'{{{M}}}mtext' and len(e)==0 and e.text==value['source'],xpath
        assert re.search('[A-Za-z]{2,}',value['source']), 'Only linguistic mtext may be localized'
        assert re.findall('[0-9]+',value['source'])==re.findall('[0-9]+',value['target']), 'Numeric mtext changed'
        e.text=value['target']
    assert [e.tag for e in source.iter()]==[e.tag for e in target.iter()]
    assert [e.get('id') for e in source.iter()]==[e.get('id') for e in target.iter()]
    for a,b in zip(source.iter(),target.iter()):
        assert {k:v for k,v in a.attrib.items() if k not in ('alt','aria-label','summary')}=={k:v for k,v in b.attrib.items() if k not in ('alt','aria-label','summary')}
    reversed_math=copy.deepcopy(target)
    for xpath,value in overlay.get('math_text',{}).items():unique(reversed_math,xpath).text=value['source']
    assert math_signature(source)==math_signature(reversed_math)
    retained_credits={}
    for item in overlay.get('retained_credit_names',[]):
        a,b=unique(source,item['xpath']),unique(target,item['xpath'])
        value=item['source']
        assert a.tag==b.tag==f'{{{C}}}caption' and len(a)==len(b)==0, 'Credit-name exceptions are limited to leaf captions'
        assert value and (a.text or '').count(value)==(b.text or '').count(value)==1, 'Retained credit must occur exactly once in source and target'
        retained_credits.setdefault(id(b),[]).append(value)
    for e in target.iter():
        texts=[e.tail or '']
        if not e.tag.startswith(f'{{{M}}}'):
            text=e.text or ''
            for value in retained_credits.get(id(e),[]):text=text.replace(value,'',1)
            texts += [text,e.get('alt',''),e.get('aria-label',''),e.get('summary','')]
        assert not any(re.search('[A-Za-z]{3,}',t) for t in texts),(e.get('id'),texts)
    return source,target

def render_cnxml(root,module='m81285',media_prefix='media/',study_labels=False):
    ids={e.get('id') for e in root.iter() if e.get('id')}
    target_labels={e.get('id'):{'example':'উদাহরণ','figure':'চিত্র','section':'উপবিভাগ','exercise':'অনুশীলনী','note':'টীকা','table':'সারণি'}.get(local(e),'উৎসের অংশ') for e in root.iter() if e.get('id')}
    def render(e):
        tag=local(e)
        eid=f' id="{html.escape(e.get("id"),quote=True)}"' if e.get('id') else ''
        if e.tag==f'{{{M}}}math':
            m=copy.deepcopy(e);m.tail=None
            raw=ET.tostring(m,encoding='unicode')
            raw=raw.replace('m:','').replace('xmlns:m=', 'xmlns=')
            if sum(len(x.text or '') for x in e.iter(f'{{{M}}}mtext'))>24:
                return '<span class="math-scroll" tabindex="0" role="region" aria-label="দীর্ঘ গাণিতিক রাশি; প্রয়োজনে ডানে-বাঁয়ে সরিয়ে দেখো">'+raw+'</span>'
            return raw
        if tag=='image': return ''
        if tag=='media':
            image=e.find(f'{{{C}}}image')
            name=Path(image.get('src')).name
            return f'<div{eid} class="media"><img src="{media_prefix}{name}" alt="{html.escape(e.get("alt",""),quote=True)}"/><p class="description">{html.escape(e.get("alt",""))}</p></div>'
        if tag=='link':
            tid=e.get('target-id')
            doc=e.get('document',module)
            href='#'+tid if tid in ids else f'https://github.com/openstax/osbooks-prealgebra-bundle/blob/38cae454e644abf9f0a623e876994553881597c9/modules/{doc}/index.cnxml'
            if e.get('url'):href=e.get('url')
            label=html.escape(e.text or '')+''.join(render(c)+html.escape(c.tail or '') for c in e)
            if not label.strip():label=(target_labels[tid] if tid in ids else 'পূর্ববর্তী উৎস-উদাহরণ')+' ['+(tid or doc)+']'
            return f'<a href="{href}">{label}</a>'
        if tag=='newline':return '<br/>'
        body=html.escape(e.text or '')+''.join(render(c)+html.escape(c.tail or '') for c in e)
        if study_labels and tag=='exercise':
            jump=f' · <a href="#{html.escape(e.get("id"),quote=True)}">এই প্রশ্নের লিঙ্ক</a>' if e.get('id') else ''
            body='<p class="exercise-label">অনুশীলন'+jump+'</p>'+body
        if study_labels and tag=='solution' and e.find(f'{{{C}}}title') is None:
            body='<p class="solution-label">উৎসে প্রদত্ত উত্তর</p>'+body
        if tag in ('tgroup','colspec'):return body
        if tag=='list':
            t='ol' if e.get('list-type')=='enumerated' else 'ul'
            # One source list has a stray apostrophe before circled; keep CNXML
            # exact while suppressing duplicate browser numbers in its reader.
            cl=' class="circled"' if e.get('class','').lstrip("'")=='circled' else ''
            return f'<{t}{eid}{cl}>{body}</{t}>'
        if tag=='emphasis':return '<strong>'+body+'</strong>'
        tags={'section':'section','title':'h2','para':'p','figure':'figure','example':'section','exercise':'div','problem':'div','solution':'section','term':'strong','note':'aside','equation':'div','label':'span','span':'span','table':'table','thead':'thead','tbody':'tbody','row':'tr','entry':'td','item':'li','caption':'caption','glossary':'section','definition':'div','meaning':'p','abstract':'section'}
        if tag=='para' and any(local(c) in ('list','table') for c in e):tags['para']='div'
        assert tag in tags,tag
        clas=f' class="{tag}"'
        aria_text=e.get('aria-label') or e.get('summary')
        aria=f' aria-label="{html.escape(aria_text,quote=True)}"' if aria_text else ''
        return f'<{tags[tag]}{eid}{clas}{aria}>{body}</{tags[tag]}>'
    return render(root)

def render_markdown(text):
    # Deliberately narrow syntax; unknown raw markup is escaped, never executed.
    def inline(s): return re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',html.escape(s))
    output=[]
    for block in text.strip().split('\n\n'):
        if block.startswith('# '): output.append('<h1>'+inline(block[2:])+'</h1>')
        elif block.startswith('## '):
            title=block[3:]; key=title.split(' — ')[0]
            anchor=key if re.fullmatch('[A-Z][0-9]?',key) else 'section-'+str(len(output))
            output.append(f'<h2 id="{anchor}">'+inline(title)+'</h2>')
        elif re.match(r'1\. ',block):
            lines=block.splitlines()
            assert all(re.match(r'\d+\. ',x) for x in lines)
            output.append('<ol>'+''.join('<li>'+inline(re.sub(r'^\d+\. ','',x))+'</li>' for x in lines)+'</ol>')
        else: output.append('<p>'+inline(block.replace('\n',' '))+'</p>')
    return '\n'.join(output)

CSS='''body{font-family:"Nirmala UI","Noto Sans Bengali",sans-serif;color:#182d39;background:#f7f5ef;margin:0;font-size:19px;line-height:1.85}main{max-width:900px;margin:auto;padding:32px 24px;background:white}nav{padding:14px 0;border-bottom:2px solid #14685e}a{color:#075b6b}h1,h2{line-height:1.5;color:#104d48}h1{font-size:2rem}h2{font-size:1.3rem;margin-top:1.7em}p,li{overflow-wrap:anywhere}li{padding:6px 0}aside,.example{border-left:4px solid #157468;padding:8px 20px;margin:24px 0;background:#eff8f4}.solution{padding:8px 14px;background:#f7f7f3}.media{text-align:center;margin:20px 0}img{max-width:100%;height:auto;max-height:280px}math{font-size:1.1em;direction:ltr}.description,.notice{font-size:0.85em;color:#43535a}.notice{border:1px solid #9bafa9;padding:16px}footer{border-top:1px solid #9bafa9;margin-top:36px;padding:16px 0}@media(max-width:480px){main{padding:18px 14px}body{font-size:18px}aside,.example{padding:6px 10px}}@media print{body{background:white;font-size:12pt}main{padding:0}nav{display:none}h2{break-after:avoid}img{max-height:50mm}.example,li{break-inside:avoid}}'''

def page(title,body):
    return '<!doctype html>\n<html lang="bn-Beng-IN"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><title>'+title+'</title><style>'+CSS+'</style></head><body><main><nav aria-label="পাঠ নির্বাচন"><a href="U01-companion.html">সহজ ভাষার সহায়িকা</a> · <a href="U01-source-faithful.html">উৎস-অনুগত নির্বাচিত পাঠ</a></nav>'+body+'</main></body></html>\n'

def build(out=None):
    out=out or LANG/'reader'
    out.mkdir(parents=True,exist_ok=True)
    source,target=translated()
    (out/'media').mkdir(exist_ok=True)
    media_names={Path(e.get('src')).name for e in target.iter(f'{{{C}}}image')}
    for name in sorted(media_names):shutil.copyfile(LANG/'provenance/pilot/media'/name,out/'media'/name)
    for e in target.iter(f'{{{C}}}image'):
        assert (out/'media'/Path(e.get('src')).name).is_file(), 'Missing source image'
    root=ET.Element(f'{{{C}}}document',{'{http://www.w3.org/XML/1998/namespace}lang':'bn-Beng-IN','id':'m81285-fs-id1726667.bn-Beng-IN'})
    title=ET.SubElement(root,f'{{{C}}}title'); title.text='সমতুল ভগ্নাংশ নির্ণয়'
    content=ET.SubElement(root,f'{{{C}}}content');content.append(target)
    (LANG/'translations/m81285-fs-id1726667.bn-Beng-IN.cnxml').write_bytes(ET.tostring(root,encoding='utf-8',xml_declaration=True))
    notice='<h1>সমতুল ভগ্নাংশ নির্ণয়</h1><p class="notice">উৎস-অনুগত নির্বাচিত উপবিভাগ · A00 / m81285 / fs-id1726667। এটি সম্পূর্ণ বই নয়। মূলের গণিত, ক্রম, পরিচয়চিহ্ন এবং চিত্র অক্ষুণ্ণ রাখা হয়েছে; গদ্য ও চিত্রবিবরণ বাংলায় অনূদিত। পূর্ববর্তী উদাহরণের লিঙ্ক ইংরেজি মূল উৎসে যায় এবং ইন্টারনেট প্রয়োজন।</p>'
    credits='<footer>OpenStax, Rice University · Prealgebra 2e · Lynn Marecek, MaryAnne Anthony-Smith, Andrea Honeycutt Mathis। মূল অবদানকারীদের পূর্ণ স্বীকৃতি <a href="../provenance/pilot/m81241.source.cnxml">উৎস-প্রাককথনে</a>। <a href="../provenance/A00/repository/LICENSE">CC BY-NC-SA 4.0 ও উপাদানভিত্তিক শর্ত</a>। অনানুষ্ঠানিক বাংলা অনুবাদ; OpenStax বা Rice University-এর অনুমোদন দাবি করা হচ্ছে না। স্বাধীন বাংলা ভাষা-পর্যালোচনা বাকি।</footer>'
    (out/'U01-source-faithful.html').write_text(page('U01 · সমতুল ভগ্নাংশ',notice+render_cnxml(target)+credits),encoding='utf-8')
    md=(LANG/'translations/U01-companion.md').read_text(encoding='utf-8')
    (out/'U01-companion.html').write_text(page('U01 · ভগ্নাংশ থেকে সমীকরণ',render_markdown(md)+credits),encoding='utf-8')
    return {'mathml_expressions':len(math_signature(source)),'cnxml_nodes':sum(1 for e in source.iter()),
            'preserved_ids':sum(bool(e.get('id')) for e in source.iter()),
            'source_examples':sum(local(e)=='example' for e in source.iter()),
            'source_exercises':sum(local(e)=='exercise' for e in source.iter()),
            'assets':len(media_names),
            'outputs':{name:sha(out/name) for name in ['U01-companion.html','U01-source-faithful.html']}}

if __name__=='__main__': print(json.dumps(build(),indent=2))
