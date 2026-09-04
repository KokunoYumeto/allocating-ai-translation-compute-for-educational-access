"""Offline Punjabi reader: complete Chapter1 opening/Section1.1, not all Chapter1."""
import html
import json
import re
from lxml import etree as E
from prepare_b10_002 import *
from b10_002_tex import convert

TOKEN=re.compile(r'{{(tex|footnote|xref|index|child|symbol):(\d+)}}')
LOCAL_CSS="""
.b10-002 main,.b10-002 article,.b10-002 section,.b10-002 .source-p{min-width:0}
.b10-002 .source-p{margin-block:.85rem}
.b10-002 .source-exercise,.b10-002 .source-example,.b10-002 .source-definition,.b10-002 .source-assemblage,.b10-002 .source-investigation{border-inline-start:3px solid #cad7d1;padding:.4rem 1rem;margin-block:1.2rem}
.b10-002 .source-math{direction:ltr;unicode-bidi:isolate;display:inline-block;max-width:100%;vertical-align:middle;overflow-x:auto;overflow-y:hidden;padding:.12rem}
.b10-002 .source-display-math{display:block;text-align:center;margin-block:.6rem}
.b10-002 math{direction:ltr;font-size:1.06em}.b10-002 mtext{white-space:pre}
.b10-002 .tex-link{display:inline-block;font:10px/1.4 Consolas,monospace;vertical-align:super;margin-inline-start:.2rem;color:#466358}
.b10-002 .source-table-scroll{overflow-x:auto;max-width:100%;margin-block:1rem}
.b10-002 table{direction:ltr;width:auto;min-width:12rem;margin-inline:auto;border-collapse:collapse}
.b10-002 td,.b10-002 th{text-align:center;padding:.4rem .65rem;vertical-align:top}
.b10-002 .source-tabular.prose-table{min-width:30rem}.b10-002 .prose-table td{min-width:12rem}
.b10-002 tr[data-source-bottom="minor"]>*{border-bottom:1px solid #637b6c}
.b10-002 col[data-source-right="minor"]{border-right:1px solid #637b6c}.b10-002 col[data-source-right="medium"]{border-right:2px solid #637b6c}
.b10-002 .source-sidebyside{display:flex;flex-wrap:wrap;gap:.8rem;align-items:flex-start;justify-content:center;direction:ltr}
.b10-002 .source-sidebyside>.source-table-scroll{flex:0 1 auto}
.b10-002 .source-index{position:relative;display:inline;font-size:.72rem;line-height:1.5}
.b10-002 .index-marker{cursor:help;background:#edf3ee;border-radius:.3rem;padding:0 .2rem}
.b10-002 .index-content{display:none;position:absolute;z-index:2;inset-inline-start:0;top:1.2rem;min-width:9rem;max-width:16rem;background:white;border:1px solid #9cb4a4;padding:.4rem}
.b10-002 .source-index:hover>.index-content,.b10-002 .source-index:focus-within>.index-content{display:block}
.b10-002 .source-index-h,.b10-002 .source-index-see{display:block}
.b10-002 .source-fn{font-size:.86em;color:#365449}.b10-002 .source-notation{display:inline-block;border:1px solid #d7e2da;padding:.2rem}
.b10-002 .source-solution,.b10-002 .source-answer,.b10-002 .source-feedback,.b10-002 .source-hint{margin-block:.6rem;padding:.45rem;border:1px solid #cad7d1;border-radius:.3rem}
.b10-002 summary{cursor:pointer}.b10-002 .source-choice,.b10-002 .source-match{margin-block:.5rem;padding:.4rem;border-bottom:1px solid #dae4dd}
.b10-002 .source-match{display:grid;grid-template-columns:1fr 1fr;gap:.8rem}
.b10-002 .source-choices,.b10-002 .source-matches{padding:.3rem}
.b10-002 ol[type="a"],.b10-002 ol[type="a"]>li{list-style-type:lower-alpha}
.b10-002 .source-warning,.b10-002 .cache-warning{font-size:.9rem;color:#6c401f;background:#fff3df;padding:.3rem .5rem}
.b10-002 .source-warning{display:block;margin-block:.3rem}
.b10-002 .snapshot-label,.b10-002 .static-policy{background:#edf3ee;padding:.6rem}
.b10-002 .pending-reference{text-decoration:underline dotted}.b10-002 .pending-marker{font-size:.8em}
.b10-002 .source-empty-response textarea{display:block;box-sizing:border-box;width:100%;min-height:5rem;font:inherit;direction:rtl}
.b10-002 pre{direction:ltr;text-align:left;white-space:pre;overflow:auto;max-width:100%;font:14px/1.6 Consolas,monospace;padding:.6rem;background:#f0f5f1}
.b10-002 .tex-owner{direction:ltr;text-align:left;overflow-wrap:anywhere;font:11px/1.5 Consolas,monospace}
.b10-002 .raw-tex-fallback{border-bottom:1px solid #dce4df;padding:.5rem}.b10-002 :target{outline:2px solid #8dab98}
.b10-002 .source-label,.b10-002 footer,.b10-002 bdi{overflow-wrap:anywhere}
.b10-002 q{quotes:"«" "»" "‹" "›"}
@media(max-width:600px){.b10-002 .source-exercise,.b10-002 .source-example,.b10-002 .source-definition{padding-inline:.6rem}.b10-002 .source-match{display:block}.b10-002 .source-sidebyside{display:block}}
"""
HEADINGS={'objectives':'سکھن دے مقصد','investigation':'کھوج لاؤ!','definition':'تعریف','example':'مثال','aside':'نالے ایہہ وی…','remark':'اک ہور گل','worksheet':'مل کے مشق','reading-questions':'پڑھن بارے سوال','exercise':'مشق','assemblage':'خلاصہ'}
DISCLOSURES={'solution':'ماخذ دا حل — کھولو','answer':'ماخذ دا جواب — کھولو','feedback':'ماخذ دی رہنمائی — کھولو','hint':'ماخذ دا اشارہ — کھولو'}
PENDING={'sec_logic-implications':'استلزام','sec_logic-rules':'منطق دے اصول','sec_logic-proofs':'ثبوت','sec_logic-structures':'ڈسکریٹ بناوٹاں بارے ثبوت'}

def esc(v):return html.escape(str(v),quote=True)
def exact(v):return esc(v).replace('\n','&#10;').replace('\r','&#13;').replace('\t','&#9;')
def frag(v):return E.fromstring(('<fragment>'+v+'</fragment>').encode())
def plain(v):return ''.join(frag(v).itertext())
def attrs_json(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))

class Reader:
    def __init__(self,m,t,roots,cache,nodes,keys,raws):
        self.m,self.t,self.roots,self.cache,self.nodes,self.keys,self.raws=m,t,roots,cache,nodes,keys,raws
        self.blocks={b['key']:b for b in m['source_blocks']};self.used=[];self.math_seen=[]
        self.math={s['source_path']:(i,s) for i,s in enumerate(m['tex_slots'],1)}
        self.bindings={b['owner']:(i,b) for i,b in enumerate(m['cached_static_bindings'],1)}
        self.warnings={}
        for n in t['original_notes']:
            if n['kind']!='original-clarification':
                for k in n['source_keys']:self.warnings.setdefault(k,[]).append(n['id'])
    def attrs(self,e):
        k=self.keys[e];s=' data-source-node="'+esc(k)+'" data-source-tag="'+esc(e.tag)+'" data-source-attributes="'+esc(attrs_json(dict(e.attrib)))+'"'
        if e.get(XID):s+=' id="'+esc(e.get(XID))+'"'
        elif e.get('label') and e.tag=='exercise':s+=' id="'+esc(e.get('label'))+'" data-anchor-origin="source-label"'
        if k in self.blocks:s+=' data-source-key="'+esc(k)+'"'
        if k in self.warnings:s+=' aria-describedby="'+esc(' '.join(self.warnings[k]))+'"'
        return s
    def warning(self,k):
        if k not in self.warnings:return ''
        return '<span class="source-warning" data-origin="original-note-link">ماخذ دے ایس متن بارے وکھری درستی: '+''.join('<a href="#'+ident+'" data-correction-for="'+esc(k)+'">نوٹ کھولو</a>' for ident in self.warnings[k])+'</span>'
    def block(self,e):
        k=self.keys[e];require(k not in self.used,'Duplicate source key');self.used.append(k)
        b=self.blocks[k];slots={s['token']:s for s in b['slots']};markup=iter(b['inline_markup'])
        def text(v):
            v=v or '';parts=[];start=0
            for match in TOKEN.finditer(v):
                parts.append(html.escape(v[start:match.start()],quote=False));parts.append(self.node(self.nodes[slots[match.group()]['source_path']]));start=match.end()
            parts.append(html.escape(v[start:],quote=False));return ''.join(parts)
        def visit(n):
            if n.tag=='fragment':return text(n.text)+''.join(visit(c)+text(c.tail) for c in n)
            require(n.tag in {'bdi','em','q','span','strong'},'Unknown target markup')
            a=''.join(' '+name+'="'+esc(v)+'"' for name,v in n.attrib.items() if name!='data-source-tag')
            if n.tag!='bdi':
                sm=next(markup);s=self.nodes[sm['path']]
                require(n.tag=={'term':'span','alert':'strong','foreign':'span'}.get(s.tag,s.tag),'Inline source binding differs');a+=self.attrs(s)
            return '<'+n.tag+a+'>'+text(n.text)+''.join(visit(c)+text(c.tail) for c in n)+'</'+n.tag+'>'
        rendered=visit(frag(self.t['source_blocks'][k]));require(next(markup,None) is None,'Unbound inline markup')
        return rendered+self.warning(k)
    def children(self,e):
        return html.escape(e.text or '',quote=False)+''.join(self.node(c)+html.escape(c.tail or '',quote=False) for c in e)
    def node(self,e):
        k,tag=self.keys[e],e.tag;a=self.attrs(e)
        if tag in {'m','me'}:
            num,s=self.math[k];require(e.text==s['raw_tex'] and k not in self.math_seen,'Math identity');self.math_seen.append(k)
            derived,r=convert(e.text,tag=='me')
            return '<span'+a+' class="source-math'+(' source-display-math' if tag=='me' else '')+'" dir="ltr" data-source-tex="'+exact(e.text)+'" data-source-tex-sha256="'+r['source_tex_sha256']+'" data-math-status="'+r['status']+'">'+derived+'<a class="tex-link" data-origin="renderer-ui" href="#source-tex-'+str(num).zfill(3)+'" aria-label="اصل فارمولا ویکھو" lang="en" dir="ltr">TeX</a></span>'
        if tag=='xref':
            ref=e.get('ref')
            if ref in PENDING:return '<span'+a+' class="pending-reference" data-reference-status="pending">'+PENDING[ref]+' <span class="pending-marker" data-origin="renderer-ui">(اگلا حصہ؛ پنجابی متن ہن موجود نہیں)</span></span>'
            target=next(n for n in self.nodes.values() if n.get(XID)==ref);label=plain(self.t['source_blocks'][self.keys[target.find('title')]])
            return '<a'+a+' href="#'+esc(ref)+'" data-reference-status="available">'+esc(label)+'</a>'
        if tag in {'ellipsis','lq','rq'}:return '<span'+a+' class="source-symbol">'+{'ellipsis':'…','lq':'“','rq':'”'}[tag]+'</span>'
        if tag==XI:
            if e.get('parse')=='text':
                f='source/practice/'+e.get('href')
                return '<details'+a+' class="source-inert-pg"><summary data-origin="renderer-ui">اصل مقامی سوال دا کوڈ — صرف متن، نہیں چلایا گیا</summary><pre dir="ltr"><code data-source-inert-pg="'+esc(f)+'">'+html.escape(self.raws[f].decode(),quote=False)+'</code></pre></details>'
            f='source/'+e.get('href')
            return '<div'+a+' class="source-expanded-include" data-expanded-source="'+esc(f)+'">'+self.node(self.roots[f])+'</div>'
        if tag=='webwork':
            i,b=self.bindings[k]
            return '<div'+a+' id="webwork-owner-'+str(i)+'" class="source-webwork"><p data-origin="renderer-ui" class="snapshot-label">ایس مشق دی اک مقرر محفوظ صورت: <a data-cache-owner="'+esc(k)+'" href="#'+b['cache_xml_id']+'"><bdi dir="ltr" lang="en">'+b['cache_ww_id']+'</bdi> — بیج <bdi dir="ltr">'+b['seed']+'</bdi> کھولو</a>۔ سوال خودکار طور اُتے نواں نہیں بنے گا؛ نمبر نہیں لگن گے۔</p>'+self.children(e)+'</div>'
        if k in self.blocks:
            ht={'title':'h1' if e.getparent().tag=='chapter' else 'h2' if e.getparent().tag=='section' else 'h3','cell':'th' if e.getparent().get('header')=='yes' else 'td','li':'li','caption':'figcaption','h':'span','see':'span','fn':'span'}.get(tag,'div')
            cls='source-'+tag
            if tag in {'h','see'}:cls='source-index-'+tag
            extra=''
            if tag=='cell':
                extra+=' dir="'+('rtl' if re.search('[\u0600-\u06ff]',self.t['source_blocks'][k]) else 'ltr')+'"'
                if ht=='th':extra+=' scope="col"'
            return '<'+ht+a+' class="'+cls+'"'+extra+'>'+self.block(e)+'</'+ht+'>'
        if tag=='idx':
            return '<span'+a+' class="source-index"><span class="index-marker" tabindex="0" data-origin="renderer-ui" aria-label="ماخذ دا فہرستی لفظ">فہرست</span><span class="index-content" data-origin="renderer-ui-wrapper">'+self.children(e)+'</span></span>'
        if tag=='tabular':
            cols=''.join(self.node(c) for c in e if c.tag=='col');rows=''.join(self.node(c) for c in e if c.tag=='row')
            require(all(c.tag in {'col','row'} for c in e),'Unknown table child')
            prose=' prose-table' if '/example[1]/statement[1]/tabular[' in k else ''
            return '<div class="source-table-scroll" data-origin="renderer-ui-wrapper"><table'+a+' class="source-tabular'+prose+'" dir="ltr"><colgroup data-origin="renderer-ui-wrapper">'+cols+'</colgroup><tbody data-origin="renderer-ui-wrapper">'+rows+'</tbody></table></div>'
        if tag=='col':return '<col'+a+' data-source-right="'+esc(e.get('right',''))+'"/>'
        if tag=='row':return '<tr'+a+' data-source-bottom="'+esc(e.get('bottom',''))+'">'+self.children(e)+'</tr>'
        if tag in DISCLOSURES:return '<details'+a+' class="source-'+tag+'"><summary data-origin="renderer-ui">'+DISCLOSURES[tag]+'</summary>'+self.children(e)+'</details>'
        if tag=='response':
            require(not len(e) and not (e.text or '').strip(),'Unreviewed response shape')
            return '<div'+a+' class="source-empty-response"><label data-origin="renderer-ui">آپ جواب لکھ کے آزما لو — ایہہ خانہ محفوظ نہیں ہُندا<textarea aria-label="اپنا عارضی جواب" data-origin="renderer-ui" rows="3"></textarea></label></div>'
        if tag=='choice':
            flag=e.get('correct','unspecified')
            info='<details data-origin="renderer-ui" class="source-choice-flag"><summary>ماخذ دے اختیار دا نشان</summary><p>اصل نشان: <bdi dir="ltr" lang="en">'+flag+'</bdi>۔ ایہہ خودکار جانچ نہیں؛ درستی دے وکھرے نوٹ وی ویکھو۔</p></details>'
            return '<div'+a+' class="source-choice">'+self.children(e)+info+'</div>'
        allowed={'chapter','section','subsection','introduction','objectives','ol','ul','li','investigation','blockquote','exercise','statement','definition','aside','example','notation','remark','worksheet','choices','figure','sidebyside','assemblage','paragraphs','reading-questions','matches','match','exercises','task','static'}
        require(tag in allowed,'Unsupported source tag '+tag)
        ht={'chapter':'article','blockquote':'blockquote','ol':'ol','ul':'ul','li':'li','figure':'figure'}.get(tag,'section' if tag in {'section','subsection','exercise','definition','example','exercises','static'} else 'div')
        extra=' type="a"' if tag=='ol' and e.get('label')=='a.' else ''
        heading='<h4 data-origin="renderer-ui">'+HEADINGS[tag]+'</h4>' if tag in HEADINGS and e.find('title') is None else ''
        body=self.children(e)
        if tag=='chapter':body+='<div data-origin="expanded-section" data-expanded-source="'+SECTION+'">'+self.node(self.roots[SECTION])+'</div>'
        return '<'+ht+a+' class="source-'+tag+'"'+extra+'>'+heading+body+'</'+ht+'>'
    def snapshots(self):
        out='<section id="b10-002-fixed-snapshots" data-origin="source-cache-collection"><h2>محفوظ سوالاں دیاں مقرر صورتاں</h2><p class="static-policy">ایہہ ماخذ دے محفوظ سوال نیں، زندہ سوال بنانے والی مشین نہیں۔ اصل مشقاں نال اوہناں دے رشتے، بیج تے اصل کوڈ محفوظ نیں۔ <a href="#b10-002-fixed-cache">مقرر تے بدل سکدیاں صورتاں دا فرق</a>۔</p>'
        for i,(c,b) in enumerate(zip(self.cache,self.m['cached_static_bindings']),1):
            meta={n.tag:tree(n) for n in c if n.tag!='static'}
            out+='<section id="'+b['cache_xml_id']+'" class="source-cache-record" data-cache-record="'+str(i)+'" data-cache-owner="'+esc(b['owner'])+'" data-cache-attributes="'+esc(attrs_json(dict(c.attrib)))+'" data-cache-tree-sha256="'+self.m['cache_record_tree_sha256'][i-1]+'">'
            out+='<h3 class="snapshot-label" data-origin="renderer-ui"><bdi dir="ltr" lang="en">'+b['cache_ww_id']+'</bdi> — بیج <bdi dir="ltr">'+b['seed']+'</bdi> · <a data-cache-return="'+esc(b['owner'])+'" href="#webwork-owner-'+str(i)+'">اصل مشق ول مُڑو</a></h3>'
            if i==4:out+='<p class="cache-warning" data-origin="original-note-link"><a href="#b10-002-cache-parity">خبردار: ایس محفوظ صورت دے اصل حل وچ عددی غلطی اے؛ وکھری درستی پڑھو۔</a></p>'
            out+=self.node(c.find('static'))
            out+='<details class="cache-inert-metadata" data-origin="cache-provenance"><summary>اصل محفوظ سوال دی شناخت تے کوڈ — صرف متن</summary><pre dir="ltr"><code data-cache-metadata="'+str(i)+'">'+html.escape(json.dumps(meta,ensure_ascii=False,indent=2),quote=False)+'</code></pre></details></section>'
        return out+'</section>'
    def notes(self):
        out='<section id="b10-002-original-notes" data-origin="original"><h2>مترجم دے وکھرے نوٹ — ماخذ دا حصہ نہیں</h2>'
        for n in self.t['original_notes']:
            out+='<section id="'+n['id']+'" data-origin="original" data-note-kind="'+n['kind']+'"><h3>'+esc(n['title'])+'</h3><div class="original-note-content">'+n['html']+'</div></section>'
        return out+'</section>'
    def fallback(self):
        out='<section id="b10-002-source-math" data-origin="renderer-ui"><h2>اصل فارمولے تے ماکروز — صرف متن</h2><p>سارے اصل فارمولے جیویں دے تیویں محفوظ نیں۔ محدود، مقامی نقشے نال بنے ریاضی روپ وکھرے نیں؛ اک غیرپرکھیا باریک فاصلے والا روپ اصل متن وچ ای دکھایا اے۔</p>'
        for i,s in enumerate(self.m['tex_slots'],1):
            out+='<details id="source-tex-'+str(i).zfill(3)+'" class="raw-tex-fallback" data-tex-owner="'+esc(s['source_path'])+'"><summary>فارمولا <bdi dir="ltr">'+str(i)+'</bdi> — اصل متن</summary><p class="tex-owner" dir="ltr" lang="en">'+esc(s['source_path'])+'</p><pre dir="ltr"><code data-source-tex-fallback="true">'+html.escape(s['raw_tex'],quote=False)+'</code></pre></details>'
        return out+'<details id="b10-002-source-macros"><summary>اصل ماکروز — نہیں چلائے گئے</summary><pre dir="ltr"><code data-source-macros="true">'+html.escape(self.m['source_macros'],quote=False)+'</code></pre></details></section>'

def footer(m):
    a=m['authority'];url=a['canonical']['repository'].removesuffix('.git')+'/blob/'+a['canonical']['commit']+'/source/sec_logic-statements.ptx';idurl=a['comparison']['repository'].removesuffix('.git')+'/tree/'+a['comparison']['commit']
    witnesses=component_witnesses(m)
    component_links=' · '.join('<a data-component-witness="'+esc(row['repository_path'])+'" href="../'+esc(row['local_path'])+'">'+esc(Path(row['repository_path']).name)+'</a>' for row in witnesses['files'])
    return f"""<footer id="credits" dir="ltr" lang="en"><h2>Sources, credits and changes — B10 Section 1.1</h2>
<p>Adapted from <a href="{url}">Oscar Levin, Discrete Mathematics: An Open Introduction, Fourth Edition</a>. Original author: Oscar Levin, University of Northern Colorado. Source edition date: Fall 2024. Copyright 2013–2025 Oscar Levin. This reader retains the complete Chapter1 opening, Section1.1 and both active exercise includes. Earlier complete metadata and both prefaces are in the <a href="b10-frontmatter.html">frontmatter reader</a>; complete Chapter0 is in <a href="b10-unit-001.html">the previous reader</a>.</p>
<p>The retained active fourth-edition notice states <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International</a>. The adaptation retains that work-level framework and more specific component restrictions. The <a href="../provenance/discrete-mathematics-open-introduction-id/LICENSE">retained edition license</a> records the existing discrepancy with the <a href="../provenance/upstream--discrete-book/LICENSE">stale root BY-SA 4.0 text</a>. See <a href="../provenance/discrete-mathematics-open-introduction-id/THIRD_PARTY_NOTICES.md">retained component notices</a> and <a href="../provenance/b10-unit-002-component-notices.json">selected component and reversible math evidence</a>. No new rights audit or clearance is asserted. No endorsement by Oscar Levin or University of Northern Colorado is implied.</p>
<p id="b10-002-component-witnesses">Selected WeBWorK evidence: {component_links}. The four original English OPL problem files and the two original local DMOI PG files retain their Oscar Levin / University of Northern Colorado attribution headers. The verbatim OPL notice states the default CC BY-NC-SA 3.0 Unported terms unless otherwise indicated, with alternative-license provisions; it is not replaced by the book-level license. The <a data-component-acquisition="true" href="../{witnesses['acquisition_path']}">scoped acquisition receipt</a> records exact pinned paths, blob identities and hashes. These seven retained files are only this unit's witnesses, not the whole public provenance package. All PG remains inert; no live variants were generated and no new clearance is claimed.</p>
<p>Changes: 559 source-bound Punjabi blocks; RTL prose and LTR mathematics, English and numerals; all source hierarchy, IDs, terms, references, eight tables/104 cells and 23 authored exercise nodes retained. All 337 exact source TeX owners (123 raw forms) remain inspectable. The finite nonexecuting mapper derives 336 MathML forms; the single unreviewed negative-thin-space form remains exact visible TeX. Raw macros, token/spacing/operator ledgers and inert local PG are preserved. This is not universal LaTeX support.</p>
<p>Six pinned source-cache snapshots are separately labeled with seeds and exact authored-owner links. They are fixed generated evidence, not newly executed or exhaustive variants. Source choices, flags, answers and erroneous parity solution remain source-attributed; separate original correction notes are visibly linked. No answer is invented where the cache supplies none. No upstream code, TeX, Perl/PG, external script, PreTeXt/Runestone engine, analytics, randomization or grading service runs. Two response boxes are unsaved scratch space.</p>
<p><a href="{idurl}">Pinned Indonesian comparison</a> informed comparison only; its corrections, substitutions and source omissions are not silently imported as canonical content. The adaptation was produced with OpenAI Codex assistance at the user's direction. Full Chapter1, the B10 book and the five-work assignment remain incomplete. Native Punjabi, educator and assistive-technology reviews remain separate. No training or fine-tuning dataset is created.</p>
<p><a href="../source-excerpts/b10-unit-002.ptx">Frozen authored witness</a> · <a href="../source-excerpts/b10-unit-002-webwork.xml">Frozen cache witness</a> · <a href="../source-excerpts/manifest-b10-unit-002.json">Source manifest</a> · <a href="../qa/b10-unit-002-language-notes.md">Language/source notes</a>.</p></footer>"""

def build():
    args=load_inputs();m,t=args[:2]
    require(NOTICES.exists() and json_read(NOTICES)==notice_record(m),'Run preparation first; notice differs')
    r=Reader(*args);source=r.node(r.roots[CHAPTER]);snapshots=r.snapshots()
    require(r.used==m['expected_source_keys'],'559 source key/order mismatch')
    source_math_order=[r.keys[n] for f,root in list(r.roots.items())+[(CACHEFILE,c.find('static')) for c in r.cache] for n in root.iter() if n.tag in {'m','me'}]
    require(r.math_seen==source_math_order,'337 source math DOM owner/order mismatch')
    css=(BASE/'styles/reader.css').read_text(encoding='utf-8')+LOCAL_CSS
    title=plain(t['source_blocks'][SECTION+'#/section/title[1]'])
    result=f"""<!doctype html>
<html lang="pnb-Arab-PK" dir="rtl"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><meta name="source-author" content="Oscar Levin"/><meta name="source-edition" content="Fourth Edition"/><meta name="source-book-id" content="dmoi4"/><meta name="source-document-id" content="dmoi-4"/><meta name="source-copyright" content="2013–2025 Oscar Levin"/><title>{esc(title)} — B10 1.1</title><style>{css}</style></head>
<body class="b10-002"><header><p class="eyebrow"><bdi dir="ltr" lang="en">B10 / dmoi4 / 1.1</bdi></p><p class="status">ابتدائی ترجمہ؛ ماہر پنجابی تے ریاضی دے استاد دی جانچ ہن باقی اے۔</p><nav aria-label="حصے"><a href="#ch_logic">باب دی مُڈھلی گل بات</a> · <a href="#sec_logic-statements">ریاضی دے بیان</a> · <a href="#b10-002-fixed-snapshots">محفوظ سوال</a> · <a href="#b10-002-original-notes">وکھرے نوٹ</a> · <a href="#b10-002-source-math">اصل فارمولے</a> · <a href="#credits">انتساب</a></nav></header>
<main><p class="source-label" data-origin="renderer-ui">ایتھے باب <bdi dir="ltr">1</bdi> دی مُڈھلی گل بات تے پورا حصہ <bdi dir="ltr">1.1</bdi> اوہدیاں مشقاں سمیت اے؛ پورا باب تے پوری کتاب ہن شامل نہیں۔</p>{source}{snapshots}{r.notes()}{r.fallback()}</main>{footer(m)}</body></html>
"""
    root=E.fromstring(result.replace('<!doctype html>','').encode());ids=root.xpath('//@id')
    require(len(ids)==len(set(ids)),'Duplicate HTML IDs')
    require(not root.xpath('//script|//iframe|//object|//embed|//img'),'No runtime/images allowed')
    require(not TOKEN.search(result),'Unresolved placeholder')
    require(len(root.xpath('//*[@data-source-node]'))==1602,'Exact1602 source nodes required')
    OUTPUT.write_text(result,encoding='utf-8',newline='\n')
    print('Built B10-002:559 keys;337 math owners;8 tables/104 cells;23 authored exercises;6 fixed snapshots. Chapter1/book incomplete.')

if __name__=='__main__':build()
