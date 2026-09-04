"""Full B10 Chapter0 static reader, with limited derived MathML and raw TeX fallback."""
import html
import json
import re
from lxml import etree as E
from prepare_b10_001 import (BASE, MANIFEST, TRANSLATION, EXCERPT, NOTICES, OUTPUT,
    XID, key, load_inputs, notice_record, file_hash, require)
from b10_001_tex import convert

LOCAL_CSS='''
.b10-001 main,.b10-001 article,.b10-001 section,.b10-001 .source-p { min-width:0; }
.b10-001 .source-p,.b10-001 .source-mixed-para { margin-block:.85rem; }
.b10-001 .source-investigation,.b10-001 .source-example,.b10-001 .source-aside,.b10-001 .source-exercise { border-inline-start:3px solid #cad7d1; padding:.4rem 1rem; margin-block:1.2rem; }
.b10-001 .source-sidebyside { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:1rem; }
.b10-001 .source-image { margin-block:1.2rem; }
.b10-001 .source-image img { display:block; width:152px; max-width:100%; height:auto; margin-inline:auto; padding:0; border:0; }
.b10-001 .source-shortdescription,.b10-001 .source-description,.b10-001 .original-image-description { font-size:1rem; }
.b10-001 .source-math { direction:ltr; unicode-bidi:isolate; display:inline-block; max-width:100%; vertical-align:middle; overflow-x:auto; overflow-y:hidden; padding:.15rem .12rem; }
.b10-001 .source-math.source-display-math { display:block; text-align:center; margin-block:.6rem; }
.b10-001 math { direction:ltr; font-size:1.08em; }
.b10-001 mtext { white-space:pre; }
.b10-001 .tex-link { display:inline-block; font:10px/1.4 Consolas,monospace; vertical-align:super; margin-inline-start:.25rem; color:#466358; }
.b10-001 .source-index { display:inline-block; font-size:.75rem; line-height:1.5; vertical-align:middle; margin-inline:.1rem; max-width:100%; }
.b10-001 .source-index summary { cursor:pointer; background:#edf3ee; border-radius:.3rem; padding:.1rem .25rem; }
.b10-001 .source-index[open] { display:block; border:1px solid #cad7d1; padding:.4rem; }
.b10-001 .source-index-h,.b10-001 .source-index-see { display:block; padding-inline-start:.5rem; }
.b10-001 .source-footnote { font-size:.86em; padding-inline:.25rem; color:#365449; }
.b10-001 .source-footnote-mark { font-family:serif; }
.b10-001 .source-table-scroll { overflow-x:auto; max-width:100%; }
.b10-001 table { width:auto; min-width:18rem; margin-inline:auto; direction:ltr; }
.b10-001 td { text-align:center; padding:.4rem .8rem; }
.b10-001 tr[data-source-bottom="minor"] td { border-bottom:1px solid #65796e; }
.b10-001 td:first-child { border-right:1px solid #65796e; }
.b10-001 .source-var-input { width:4ch; max-width:6rem; text-align:center; direction:ltr; font:inherit; border:1px solid #81988b; border-radius:.25rem; }
.b10-001 .source-math-answer-row { direction:ltr; unicode-bidi:isolate; text-align:left; }
.b10-001 textarea { display:block; width:100%; box-sizing:border-box; min-height:5rem; font:inherit; direction:rtl; border:1px solid #81988b; border-radius:.3rem; }
.b10-001 .source-setup { font-size:1rem; margin-block:.75rem; border:1px solid #cad7d1; padding:.5rem; }
.b10-001 .source-condition { padding-inline-start:1rem; border-inline-start:2px solid #dae4dd; }
.b10-001 .source-latex-image { font-size:.8rem; margin-block:.3rem; }
.b10-001 .raw-tex-fallback { border-block-end:1px solid #dce4df; padding:.5rem; margin-block:.2rem; }
.b10-001 .raw-tex-fallback:target { outline:2px solid #8dab98; }
.b10-001 summary { cursor:pointer; }
.b10-001 pre { direction:ltr; text-align:left; font:14px/1.6 Consolas,monospace; white-space:pre; overflow:auto; max-width:100%; padding:.6rem; background:#f0f5f1; }
.b10-001 .tex-owner { direction:ltr; text-align:left; overflow-wrap:anywhere; font:11px/1.5 Consolas,monospace; }
.b10-001 .pending-reference { text-decoration:underline dotted; }
.b10-001 .pending-marker { font-size:.8em; }
.b10-001 .source-label,.b10-001 footer,.b10-001 bdi { overflow-wrap:anywhere; }
@media(max-width:600px) { .b10-001 .source-sidebyside { display:block; } .b10-001 td { padding:.3rem .5rem; } .b10-001 .source-investigation,.b10-001 .source-example,.b10-001 .source-aside,.b10-001 .source-exercise { padding-inline:.65rem; } }
'''
TOKEN=re.compile(r'{{(tex|footnote|xref|index|child|symbol|answer):(\d+)}}')
MATH_ANSWER_ROW='sec_intro-structures.ptx#/section/reading-questions[1]/exercise[2]/statement[1]/p[2]'


def esc(value):
    return html.escape(str(value),quote=True)


def exact_attr(value):
    return esc(value).replace('\t','&#9;').replace('\n','&#10;').replace('\r','&#13;')


def frag(value):
    return E.fromstring(('<fragment>'+value+'</fragment>').encode())


def plain(value):
    return ''.join(frag(value).itertext())


class Reader:
    def __init__(self,m,t,source):
        self.m,self.t,self.source=m,t,source
        self.nodes={key(n):n for n in source.iter()}
        self.blocks={b['key']:b for b in m['source_blocks']}
        self.used=[]
        self.math={s['source_path']:(i,s) for i,s in enumerate(m['tex_slots'],1)}
        self.footnotes={key(e):i for i,e in enumerate(source.iter('fn'),1)}
        self.assets={x['id']:x for x in m['declared_assets']}
        self.math_seen=[]

    def attrs(self,e):
        text=' data-source-node="'+esc(key(e))+'" data-source-tag="'+esc(e.tag)+'" data-source-attributes="'+esc(json.dumps(dict(e.attrib),ensure_ascii=False,sort_keys=True,separators=(',',':')))+'"'
        if e.get(XID):text+=' id="'+esc(e.get(XID))+'"'
        elif e.get('label'):text+=' id="'+esc(e.get('label'))+'" data-anchor-origin="source-label"'
        return text

    def block(self,e):
        k=key(e);require(k not in self.used,'Duplicate source key '+k);self.used.append(k)
        spec=self.blocks[k];slots={s['token']:s for s in spec['slots']};markup=iter(spec['inline_markup'])
        target=frag(self.t['source_blocks'][k])
        def text(value):
            value=value or '';parts=[];start=0
            for match in TOKEN.finditer(value):
                parts.append(html.escape(value[start:match.start()],quote=False))
                slot=slots[match.group()];parts.append(self.node(self.nodes[slot['source_path']]))
                start=match.end()
            parts.append(html.escape(value[start:],quote=False));return ''.join(parts)
        def visit(n):
            if n.tag=='fragment':return text(n.text)+''.join(visit(c)+text(c.tail) for c in n)
            require(n.tag in ['bdi','em','q','span','strong'],'Unexpected target inline tag')
            attributes=''.join(' '+a+'="'+esc(v)+'"' for a,v in n.attrib.items() if a!='data-source-tag')
            if n.tag!='bdi':
                sm=next(markup);source=self.nodes[sm['path']]
                expected={'term':'span','alert':'strong'}.get(source.tag,source.tag)
                require(n.tag==expected,'Source inline binding mismatch')
                attributes+=self.attrs(source)
            return '<'+n.tag+attributes+'>'+text(n.text)+''.join(visit(c)+text(c.tail) for c in n)+'</'+n.tag+'>'
        rendered=visit(target)
        require(next(markup,None) is None,'Unused source inline markup')
        return rendered

    def formula(self,e):
        k=key(e);number,spec=self.math[k]
        require(k not in self.math_seen and e.text==spec['raw_tex'],'Math source owner differs');self.math_seen.append(k)
        math,record=convert(e.text,e.tag=='me')
        cls='source-math'+(' source-display-math' if e.tag=='me' else '')
        return '<span'+self.attrs(e)+' class="'+cls+'" dir="ltr" data-source-tex="'+exact_attr(e.text)+'" data-source-tex-sha256="'+record['source_tex_sha256']+'" data-derived-mathml="true">'+math+'<a class="tex-link" data-origin="renderer-ui" href="#source-tex-'+str(number).zfill(3)+'" aria-label="اصل فارمولا ویکھو" lang="en" dir="ltr">TeX</a></span>'

    def image(self,e):
        ident=e.get(XID) or e.find('latex-image').get('label');spec=self.assets[ident]
        raw=e.findtext('shortdescription');translated=plain(self.t['source_blocks'][key(e.find('shortdescription'))])
        original=self.t['original_image_descriptions'][ident]['html'];descid='original-image-description-'+ident
        rendered='<img data-rendered-source-image="'+ident+'" src="../'+esc(spec['planned_reader_path'])+'" width="'+spec['width']+'" height="'+spec['height']+'" alt="'+esc(translated)+'" data-source-alt="'+esc(raw)+'" data-alt-origin="translated-source-shortdescription" aria-describedby="'+descid+'">'
        children=''.join(self.node(c) for c in e)
        extra='<p id="'+descid+'" data-origin="original-accessibility-description" class="original-image-description"><span data-origin="renderer-ui">مترجم دی اپنی تصویری وضاحت: </span>'+original+'</p>'
        extra+='<p data-origin="renderer-ui" class="scroll-hint"><a href="../'+esc(spec['planned_reader_path'])+'">اصل تصویر وکھری کھولو</a> · <a href="#original-b10-001-graphs">گراف بارے وکھرا نوٹ</a></p>'
        return '<div'+self.attrs(e)+' class="source-image">'+rendered+children+extra+'</div>'

    def node(self,e):
        tag,k,attrs=e.tag,key(e),self.attrs(e)
        if tag in ['m','me']:return self.formula(e)
        if tag=='image':return self.image(e)
        if tag=='latex-image':return '<details'+attrs+' class="source-latex-image"><summary data-origin="renderer-ui">اصل تصویری <bdi dir="ltr" lang="en">TeX</bdi> — بغیر چلائے</summary><pre dir="ltr" data-source-opaque-text="true"><code>'+html.escape(e.text or '',quote=False)+'</code></pre></details>'
        if tag in ['midpoint','ellipsis']:
            return '<span'+attrs+' dir="ltr">'+('·' if tag=='midpoint' else '…')+'</span>'
        if tag=='xref':
            spec=next(x for x in self.t['reference_labels'].values() if x['source_ref']==e.get('ref'))
            if spec['resolution']=='local':return '<a'+attrs+' href="#'+esc(spec['target_id'])+'">'+spec['html']+'</a>'
            return '<span'+attrs+' class="pending-reference" data-reference-status="pending-untranslated">'+spec['html']+' <span class="pending-marker" data-origin="renderer-ui">('+esc(spec['pending_notice'])+')</span></span>'
        if tag=='fn':
            value=self.block(e)
            return '<span'+attrs+' class="source-footnote" role="note" data-source-key="'+esc(k)+'"><sup data-origin="renderer-ui" class="source-footnote-mark" dir="ltr">['+str(self.footnotes[k])+']</sup> '+value+'</span>'
        if tag=='idx':
            return '<details'+attrs+' class="source-index"><summary data-origin="renderer-ui">اشاریہ</summary>'+''.join(self.node(c) for c in e)+'</details>'
        if tag=='var' and e.getparent().tag=='p':
            slot=next(x for x in self.m['answer_slots'] if x['source_path']==k)
            return '<span'+attrs+' class="source-answer-slot"><input class="source-var-input" data-origin="renderer-ui" type="text" inputmode="numeric" dir="ltr" size="1" aria-label="خالی تھاں '+str(slot['index']+1)+'" data-source-answer-index="'+str(slot['index'])+'"></span>'
        if tag=='response':
            return '<div'+attrs+' class="source-response"><label data-origin="renderer-ui">اپنا جواب<textarea aria-label="اپنا جواب" data-origin="renderer-ui"></textarea></label><p data-origin="renderer-ui" class="scroll-hint">ایہہ جواب ایتھے محفوظ یا خودکار جانچ نہیں ہُندا۔</p></div>'
        if k in self.t['source_blocks']:
            value=self.block(e)
            if tag=='title':
                depth=1 if e.getparent().tag=='chapter' else 2 if e.getparent().tag=='section' else 3
                ht='h'+str(depth)
            elif tag=='cell':ht='td'
            elif tag in ['h','see']:ht='span'
            else:ht='div'
            cls='source-index-'+tag if tag in ['h','see'] else 'source-'+tag
            if k==MATH_ANSWER_ROW:
                require(tag=='p' and (e.text or '').strip()=='1, 3,' and len(e)==3 and all(c.tag=='var' and dict(c.attrib)=={'width':'1'} and not len(c) and not c.text for c in e) and [(c.tail or '').strip() for c in e]==[',',',',', ...'],'Exact pure mathematical answer row required')
                cls+=' source-math-answer-row';attrs+=' dir="ltr"'
            return '<'+ht+attrs+' class="'+cls+'" data-source-key="'+esc(k)+'">'+value+'</'+ht+'>'
        if tag=='tabular':
            cols=''.join(self.node(c) for c in e if c.tag=='col');rows=''.join(self.node(c) for c in e if c.tag=='row')
            return '<div class="source-table-scroll" data-origin="renderer-ui-wrapper" tabindex="0"><table'+attrs+' dir="ltr" aria-label="ترتیب وار سلسلے دی جدول"><colgroup data-origin="renderer-ui-wrapper">'+cols+'</colgroup><tbody data-origin="renderer-ui-wrapper">'+rows+'</tbody></table></div>'
        if tag=='col':return '<col'+attrs+'>'
        if tag=='row':return '<tr'+attrs+' data-source-bottom="'+esc(e.get('bottom',''))+'">'+''.join(self.node(c) for c in e)+'</tr>'
        if tag=='setup':return '<details'+attrs+' class="source-setup"><summary data-origin="renderer-ui">ماخذ دے جواب تے رہنمائی — کھولھن توں پہلاں آپ آزما لو</summary><p data-origin="renderer-ui">ایہہ ماخذ دیاں شرطاں تے جواب نیں؛ ایتھے خودکار نمبر نہیں لگدے۔</p>'+''.join(self.node(c) for c in e)+'</details>'
        if tag=='condition':
            label=('ایس عدد لئی: <bdi dir="ltr" lang="en">'+esc(e.get('number'))+'</bdi>') if e.get('number') else 'ہور جواب لئی'
            return '<div'+attrs+' class="source-condition"><p data-origin="renderer-ui">'+label+'</p>'+''.join(self.node(c) for c in e)+'</div>'
        allowed={'chapter','section','subsection','introduction','blockquote','investigation','ol','li','sidebyside','reading-questions','exercise','statement','aside','example','description','var'}
        require(tag in allowed,'Unsupported source structure '+tag)
        ht={'chapter':'article','blockquote':'blockquote','ol':'ol','li':'li'}.get(tag,'section' if tag in ['section','subsection','investigation','exercise','aside','example','reading-questions'] else 'div')
        headings={'investigation':'کھوج لاؤ!','aside':'نالے ایہہ وی…','example':'مثال','reading-questions':'پڑھن بارے سوال'}
        heading='<h4 data-origin="renderer-ui">'+headings[tag]+'</h4>' if tag in headings else ''
        return '<'+ht+attrs+' class="source-'+tag+'">'+heading+''.join(self.node(c) for c in e)+'</'+ht+'>'

    def fallback(self):
        out='<section id="b10-001-source-math" data-origin="renderer-ui"><h2>اصل فارمولے — <bdi dir="ltr" lang="en">TeX</bdi> متن</h2><p>ایہہ اصل متن جیویں دا تیویں اے۔ اُتّے دکھائے فارمولے ایس دے محدود، بغیر <bdi dir="ltr" lang="en">TeX</bdi> چلائے بنائے گئے <bdi dir="ltr" lang="en">MathML</bdi> روپ نیں۔</p>'
        for i,s in enumerate(self.m['tex_slots'],1):
            out+='<details id="source-tex-'+str(i).zfill(3)+'" class="raw-tex-fallback" data-tex-owner="'+esc(s['source_path'])+'"><summary>فارمولا <bdi dir="ltr" lang="en">'+str(i)+'</bdi> — اصل متن کھولو</summary><p class="tex-owner" dir="ltr" lang="en">'+esc(s['source_path'])+'</p><pre dir="ltr"><code data-source-tex-fallback="true">'+html.escape(s['raw_tex'],quote=False)+'</code></pre></details>'
        out+='<details id="b10-001-source-macros"><summary>اصل ماکروز — صرف متن، بغیر چلائے</summary><pre dir="ltr"><code data-source-macros="true">'+html.escape(self.m['source_macros'],quote=False)+'</code></pre></details></section>'
        return out


def footer(m):
    a=m['authority'];url=a['canonical']['repository'].removesuffix('.git')+'/blob/'+a['canonical']['commit']+'/source/ch_intro.ptx'
    comparison=a['comparison']['repository'].removesuffix('.git')+'/tree/'+a['comparison']['commit']
    return f'''<footer id="credits" dir="ltr" lang="en"><h2>Sources, credits and changes — B10 Chapter 0</h2>
<p>Adapted from <a href="{url}">Oscar Levin, Discrete Mathematics: An Open Introduction, Fourth Edition</a>. Original author: Oscar Levin, University of Northern Colorado. Source edition date: Fall 2024. Copyright 2013–2025 Oscar Levin. Complete Chapter 0, both sections and all seven subsections/six exercises are retained. Earlier full metadata and both prefaces remain in the separate <a href="b10-frontmatter.html">frontmatter reader</a>.</p>
<p>The existing active fourth-edition notice states <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International</a>. This adaptation retains that work-level framework and more specific component restrictions. The archived <a href="../provenance/discrete-mathematics-open-introduction-id/LICENSE">edition license</a> retains the already recorded discrepancy with the <a href="../provenance/upstream--discrete-book/LICENSE">stale root BY-SA 4.0 text</a>. See <a href="../provenance/discrete-mathematics-open-introduction-id/THIRD_PARTY_NOTICES.md">retained component notices</a> and <a href="../provenance/b10-unit-001-component-notices.json">selected component and reversible math evidence</a>. No new rights audit or image-specific clearance is asserted. No endorsement by Oscar Levin or University of Northern Colorado is implied.</p>
<p>Two canonical 76×73 SVG graphs remain unchanged, unmirrored and uncropped. Source shortdescriptions and the first graph's full description are retained; additional detailed descriptions are visibly marked original accessibility notes. Source TikZ and macro definitions are escaped inert text, never executed.</p>
<p>Changes: 157 source-bound Punjabi slots; RTL prose with LTR mathematics/English/numerals; all source IDs, labels, hierarchy, index entries, footnotes, table and exercise data. A locally authored strictly limited parser derives 105 MathML formulas from 78 exact source TeX strings. The raw TeX, token/spacing/operator ledgers and source annotations remain inspectable. This is not universal LaTeX support. No upstream code, external scripts, TeX/TikZ, PreTeXt/Runestone runtime, analytics or grading service is executed. Local response boxes are unsaved scratch space; source answer/feedback conditions are static disclosures.</p>
<p><a href="{comparison}">Pinned Indonesian comparison</a> informed comparison only. Its extra second-graph description, changed formula text, story language and spelling edits are not silently imported as canonical content. Separate original notes qualify source wording without replacing it. The adaptation was produced with OpenAI Codex assistance at the user's direction.</p>
<p>Coverage: full Chapter 0 only; forward references to Chapters 4 and 2 are visibly pending Punjabi translation. The entire B10 book and the five-work A10/A20/A30/B10/B40 assignment remain incomplete. Native-language, educator, browser and assistive-technology review remain separate. No training or fine-tuning dataset is created. <a href="../source-excerpts/b10-unit-001.ptx">Frozen witness</a> · <a href="../source-excerpts/manifest-b10-unit-001.json">Source manifest</a> · <a href="../qa/b10-unit-001-language-notes.md">Language/source notes</a>.</p></footer>'''


def build():
    m,t,source,prepared=load_inputs()
    for spec,target,raw in prepared:require(target.exists() and file_hash(target)==spec['sha256'],'Run preparation first')
    require(NOTICES.exists() and json.loads(NOTICES.read_text(encoding='utf-8'))==notice_record(m,prepared),'Component notice stale; run preparation')
    r=Reader(m,t,source);body=r.node(source)
    require(r.used==m['expected_source_keys'],'All157 source keys/order required')
    require(r.math_seen==[x['source_path'] for x in m['tex_slots']],'All105 math owners/order required')
    css=(BASE/'styles/reader.css').read_text(encoding='utf-8')+LOCAL_CSS
    result=f'''<!doctype html>
<html lang="pnb-Arab-PK" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="source-author" content="Oscar Levin"><meta name="source-edition" content="Fourth Edition"><meta name="source-book-id" content="dmoi4"><meta name="source-document-id" content="dmoi-4"><meta name="source-copyright" content="2013–2025 Oscar Levin"><title>{esc(t['title'])} — B10 Chapter 0</title><style>{css}</style></head>
<body class="b10-001"><header><p class="eyebrow"><bdi dir="ltr" lang="en">B10 / dmoi4 / Chapter 0</bdi></p><p>{esc(t['subtitle'])}</p><p class="status">ابتدائی ترجمہ · ماہر پنجابی تے ریاضی دے استاد دی جانچ ہن تک نہیں ہوئی۔</p><nav aria-label="حصے"><a href="#ch_intro">ماخذ دا ترجمہ</a> · <a href="#sec_intro-intro">ڈسکریٹ ریاضی کیہہ اے؟</a> · <a href="#sec_intro-structures">بناوٹاں</a> · <a href="#original-b10-001-notes">ساڈے وکھرے نوٹ</a> · <a href="#b10-001-source-math">اصل فارمولے</a> · <a href="#credits">ماخذ تے انتساب</a></nav></header>
<main><p class="source-label" data-origin="renderer-ui">ایتھے باب صفر دے دوویں حصے پورے نیں۔ اگلے باب تے پوری کتاب ہن وی کم وچ نیں۔</p>{t['bridge_before_html']}{body}{t['bridge_after_html']}{r.fallback()}</main>{footer(m)}</body></html>
'''
    normalized=re.sub(r'<(meta|img|col|input)\b([^<>]*?)(?<!/)>',r'<\1\2/>',result.replace('<!doctype html>',''))
    root=E.fromstring(normalized.encode());ids=root.xpath('//@id')
    require(len(ids)==len(set(ids)),'Duplicate reader IDs')
    require(not root.xpath('//script|//iframe|//object|//embed'),'Unexpected runtime')
    require(not TOKEN.search(result),'Unresolved source placeholder')
    OUTPUT.parent.mkdir(exist_ok=True);OUTPUT.write_text(result,encoding='utf-8',newline='\n')
    print('Built B10-001:157 keys,105 MathML owners,2 unchanged SVGs,full Chapter0; whole assignment incomplete.')


if __name__=='__main__':build()
