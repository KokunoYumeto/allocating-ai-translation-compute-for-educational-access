"""Deterministic isolated B40-opening reader. No upstream engine or shared edits."""
import html
import json
import re
from pathlib import Path
from lxml import etree as E
from prepare_b40_opening import BASE,ROOT,MANIFEST,TRANSLATION,WITNESS,NOTICES,ASSETS,load,require,file_hash
from b40_opening_tex import convert

OUTPUT=BASE/"reader/b40-opening.html"
TOKEN=re.compile(r"\{\{(tex|url|include|mark):(\d+)\}\}")
LOCAL_CSS=r"""
.b40-opening{--b40-line:#cad7d1;--b40-soft:#f0f5f1}
.b40-opening .source-label,.b40-opening footer,.b40-opening bdi{overflow-wrap:anywhere}
.b40-opening .b40-cover{border-block:1px solid var(--b40-line);padding:1rem;text-align:center}
.b40-opening .b40-cover-components{direction:ltr;display:flex;gap:1.25rem;align-items:flex-end;justify-content:center;flex-wrap:wrap}
.b40-opening .source-cover-component{margin:0;min-width:0;max-width:14rem}
.b40-opening .source-cover-component img{display:block;width:auto;height:15rem;max-width:100%;object-fit:contain;margin:auto;padding:0;border:0}
.b40-opening .source-cover-component:first-child img{height:10rem}
.b40-opening .source-cover-component figcaption{direction:rtl;text-align:center;font-size:.9rem}
.b40-opening .source-table-scroll{direction:ltr;overflow:auto;max-width:100%;border:1px solid var(--b40-line);margin-block:1rem}
.b40-opening table{border-collapse:collapse;min-width:max-content;width:100%;margin:0}
.b40-opening th,.b40-opening td{border:1px solid var(--b40-line);padding:.45rem .65rem;vertical-align:top}
.b40-opening .source-notation td:nth-child(odd),.b40-opening .source-greek td:nth-child(odd){direction:ltr;text-align:center}
.b40-opening .source-notation td:nth-child(even),.b40-opening .source-greek td:nth-child(even){direction:rtl;text-align:right}
.b40-opening .source-schedule th,.b40-opening .source-schedule td:first-child{direction:rtl;text-align:center}
.b40-opening .source-schedule td:last-child{direction:rtl;text-align:right}
.b40-opening .source-math{direction:ltr;unicode-bidi:isolate;display:inline-flex;align-items:baseline;gap:.2rem;max-width:100%}
.b40-opening math{direction:ltr}.b40-opening mspace{display:inline-block}
.b40-opening .tex-link{font:10px/1.2 system-ui,sans-serif;vertical-align:super}
.b40-opening .source-quote{margin-block:1.2rem;border-inline-start:3px solid var(--b40-line);padding-inline-start:1rem}
.b40-opening .source-quote p{margin:.15rem 0}
.b40-opening .source-credit{font-style:normal;border-inline-start:3px solid var(--b40-line);padding-inline-start:1rem}
.b40-opening .source-credit p{margin:.15rem 0}
.b40-opening .source-mark{direction:ltr;unicode-bidi:isolate;font-weight:700}
.b40-opening details{max-width:100%;margin-block:.6rem}.b40-opening summary{cursor:pointer}
.b40-opening pre{direction:ltr;text-align:left;font:13px/1.5 Consolas,monospace;white-space:pre;overflow:auto;max-width:100%;padding:.6rem;background:var(--b40-soft)}
.b40-opening .tex-owner{direction:ltr;text-align:left;overflow-wrap:anywhere;font:11px/1.4 Consolas,monospace}
.b40-opening .original-note{border-inline-start:3px solid #95aa9e;padding-inline-start:1rem;margin-block:1rem}
.b40-opening .term-grid{display:grid;grid-template-columns:minmax(7rem,.55fr) minmax(0,1fr);gap:.35rem 1rem}
.b40-opening .term-grid dt{font-weight:600}.b40-opening .term-grid dd{margin:0}
.b40-opening .component-limit{font-size:.9rem}
@media(max-width:600px){
 .b40-opening .b40-cover-components{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));align-items:end}
 .b40-opening .source-cover-component{min-width:0;max-width:100%}
 .b40-opening .source-cover-component img,.b40-opening .source-cover-component:first-child img{min-width:0;width:auto;max-width:100%;height:auto;max-height:15rem}
 .b40-opening th,.b40-opening td{padding:.35rem .5rem}
 .b40-opening .term-grid{display:block}.b40-opening .term-grid dd{margin-block-end:.65rem}
}
"""
UI={
"source":"ایہہ اصل پیش فرض سرورق، علامتاں، یونانی حرف تے پوری مُڈھلی گل اے۔ فہرستِ مضامین اگلا لازمی حصہ اے۔",
"raw":"اصل فارمولے — TeX متن","open":"اصل فارمولا ویکھو","component":"اصل PDF وکھری کھولو",
"preview":"شفاف تصویری روپ: اصل PDF توں، بغیر TeX یا Asymptote چلائے۔ ایہہ اصل سرورق دی ٹھیک جگہ بندی دا دعویٰ نہیں۔"}

def esc(v,quote=True):return html.escape(str(v),quote=quote)
def frag(v):return E.fromstring(("<fragment>"+v+"</fragment>").encode())
def attrs(block):
    return (' data-source-key="'+esc(block["key"])+'" data-source-kind="'+esc(block["kind"])+'"'
            ' data-source-file="'+esc(block["source_file"])+'" data-source-start="'+str(block["source_start"])+'"'
            ' data-source-end="'+str(block["source_end"])+'" data-source-raw-sha256="'+block["source_raw_sha256"]+'"')

class Reader:
    def __init__(self,m,t,notice):
        self.m=m;self.t=t;self.notice=notice;self.blocks={b["key"]:b for b in m["source_blocks"]}
        self.used=[];self.math_seen=[];self.math_number={}
        n=0
        for b in m["source_blocks"]:
            for s in b["slots"]:
                if s["kind"]=="tex":n+=1;self.math_number[(b["key"],s["token"])]=n
        require(n==76,"Math inventory differs")
    def slot(self,block,slot):
        kind=slot["kind"];token=slot["token"]
        if kind=="tex":
            number=self.math_number[(block["key"],token)]
            math,record=convert(slot["value"]);self.math_seen.append((block["key"],token))
            return ('<span class="source-math" dir="ltr" data-source-slot-token="'+esc(token)+'"'
                    ' data-source-slot-kind="tex" data-source-tex="'+esc(slot["value"])+'"'
                    ' data-source-tex-raw="'+esc(slot["raw"])+'" data-source-tex-sha256="'+record["source_tex_sha256"]+'">'
                    +math+'<a class="tex-link" data-origin="renderer-ui" href="#source-tex-'+str(number).zfill(3)+'"'
                    ' aria-label="'+UI["open"]+'" dir="ltr" lang="en">TeX</a></span>')
        if kind=="url":
            value=slot["value"];href=value if re.match(r"https?://",value) else "https://"+value
            return ('<a class="source-url" data-source-slot-token="'+esc(token)+'" data-source-slot-kind="url"'
                    ' data-source-url="'+esc(value)+'" data-renderer-url-normalization="'+("none" if href==value else "https-scheme-added")+'"'
                    ' href="'+esc(href)+'"><bdi dir="ltr" lang="en">'+esc(value)+'</bdi></a>')
        if kind=="mark":
            glyph="?" if slot["value"]=="puzzlemark" else "✓"
            return ('<span class="source-mark" data-source-slot-token="'+esc(token)+'" data-source-slot-kind="mark"'
                    ' data-source-mark="'+esc(slot["value"])+'" dir="ltr">'+glyph+'</span>')
        if kind=="include":
            require(slot["value"]=="publicationdate","Unsupported include")
            date=self.blocks["src/publicationdate.tex#date"]
            content=self.block(date["key"],tag="span",extra=' class="source-included-date"')
            return ('<span class="source-include" data-source-slot-token="'+esc(token)+'" data-source-slot-kind="include"'
                    ' data-source-include="publicationdate">'+content+'</span>')
        raise ValueError("Unknown slot")
    def expand_text(self,text,block,slotmap):
        text=text or "";out=[];pos=0
        for hit in TOKEN.finditer(text):
            out.append(esc(text[pos:hit.start()],False));tok=hit.group()
            require(tok in slotmap,"Unknown target placeholder "+tok);out.append(self.slot(block,slotmap[tok]));pos=hit.end()
        out.append(esc(text[pos:],False));return "".join(out)
    def inline(self,node,block,slotmap):
        if node.tag=="fragment":
            return self.expand_text(node.text,block,slotmap)+"".join(self.inline(c,block,slotmap)+self.expand_text(c.tail,block,slotmap) for c in node)
        require(node.tag in {"bdi","em","span"},"Unexpected target tag "+node.tag)
        require(node.tag!="span" or node.get("class")=="source-pronunciation","Unexpected target span")
        a="".join(" "+k+'="'+esc(v)+'"' for k,v in node.attrib.items())
        return "<"+node.tag+a+">"+self.expand_text(node.text,block,slotmap)+"".join(self.inline(c,block,slotmap)+self.expand_text(c.tail,block,slotmap) for c in node)+"</"+node.tag+">"
    def block(self,key,tag="div",extra=""):
        require(key not in self.used,"Duplicate source block "+key);self.used.append(key)
        b=self.blocks[key];slots={s["token"]:s for s in b["slots"]}
        body=self.inline(frag(self.t["source_blocks"][key]),b,slots)
        return "<"+tag+attrs(b)+extra+'><span class="source-content">'+body+"</span></"+tag+">"
    def table(self,file,number):
        cells=[b for b in self.m["source_blocks"] if b["source_file"]==file and b.get("table")==number]
        rows={}
        for b in cells:rows.setdefault(b["row"],[]).append(b)
        if file.endswith("symlist.tex") and number==1:cls,label,head="source-notation","علامتاں دی اصل جدول",False
        elif file.endswith("symlist.tex"):cls,label,head="source-greek","یونانی حرف تے اصل انگریزی اُچار",True
        else:cls,label,head="source-schedule","چوداں ہفتیاں دا ماخذ اوقات نامہ",True
        content=""
        for rn in sorted(rows):
            values=[]
            for b in sorted(rows[rn],key=lambda x:x["column"]):
                celltag="th" if head and rn==1 else "td"
                values.append(self.block(b["key"],celltag,' scope="col"' if celltag=="th" else ""))
            content+="<tr data-source-row=\""+str(rn)+"\">"+"".join(values)+"</tr>"
        groups=("<thead>"+content.split("</tr>",1)[0]+"</tr></thead><tbody>"+content.split("</tr>",1)[1]+"</tbody>") if head else "<tbody>"+content+"</tbody>"
        return '<div class="source-table-scroll" data-origin="renderer-ui-wrapper" tabindex="0"><table class="'+cls+'" dir="ltr" data-source-file="'+file+'" data-source-table="'+str(number)+'" aria-label="'+label+'">'+groups+"</table></div>"
    def line_group(self,number):
        cells=[b for b in self.m["source_blocks"] if b["source_file"]=="src/pref/pref.tex" and b.get("table")==number]
        if number in {2,3}:
            return '<blockquote class="source-quote" data-source-file="src/pref/pref.tex" data-source-table="'+str(number)+'">'+"".join(self.block(b["key"],"p",' data-source-row="'+str(b["row"])+'"') for b in cells)+"</blockquote>"
        return '<address class="source-credit" data-source-file="src/pref/pref.tex" data-source-table="4">'+"".join(self.block(b["key"],"p",' data-source-row="'+str(b["row"])+'"') for b in cells)+"</address>"
    def cover(self):
        title=self.block("src/cover/covernew.tex#metadata/title","h1")
        author=self.block("src/cover/covernew.tex#metadata/author","p")
        graphic=[self.block("src/sty/covergraphic.sty#visible/"+x,"p") for x in ["title","author","edition","webaddress"]]
        figs=[]
        alt={x["repository_path"]:x for x in self.t["original_accessibility_alts"]}
        for comp in self.notice["components"]:
            a=alt[comp["source_path"]];ident=comp["id"];desc="b40-component-"+ident+"-desc"
            figs.append('<figure class="source-cover-component" data-source-component="'+ident+'" data-source-layer-order="'+str(len(figs)+1)+'">'
              '<img src="../'+esc(comp["preview"]["path"])+'" width="'+str(comp["preview"]["width"])+'" height="'+str(comp["preview"]["height"])+'"'
              ' alt="'+esc(a["alt_pnb"])+'" data-alt-origin="'+esc(a["origin"])+'" data-source-alt-present="false"'
              ' data-source-pdf-sha256="'+comp["source_sha256"]+'" aria-describedby="'+desc+'">'
              '<figcaption id="'+desc+'"><span data-origin="renderer-ui">'+UI["preview"]+'</span> '
              '<a href="../'+esc(comp["prepared_path"])+'" dir="ltr" lang="en">'+UI["component"]+"</a></figcaption></figure>")
        return '<section class="b40-cover" data-source-section="default-cover">'+title+author+graphic[0]+'<div class="b40-cover-components">'+"".join(figs)+"</div>"+"".join(graphic[1:])+"</section>"
    def symlist(self):
        return '<section data-source-section="notation-greek">'+self.block("src/cover/symlist.tex#heading/1","h2")+self.table("src/cover/symlist.tex",1)+self.block("src/cover/symlist.tex#heading/2","h2")+self.table("src/cover/symlist.tex",2)+self.block("src/cover/symlist.tex#capitals-note","p")+"</section>"
    def preface(self):
        blocks=sorted([b for b in self.m["source_blocks"] if b["source_file"]=="src/pref/pref.tex"],key=lambda b:b["source_start"])
        seen=set();out=[]
        for b in blocks:
            if b.get("table"):
                n=b["table"]
                if n not in seen:out.append(self.table("src/pref/pref.tex",1) if n==1 else self.line_group(n));seen.add(n)
                continue
            if b["kind"]=="heading":
                level="h2" if b["key"].endswith("heading/1") else "h3";out.append(self.block(b["key"],level))
            else:out.append(self.block(b["key"],"p"))
        return '<section data-source-section="complete-preface">'+"".join(out)+"</section>"
    def originals(self):
        out='<section id="b40-opening-original-notes" class="bridge" data-origin="original-bridge"><h2>وکھرے سیاقی نوٹ</h2>'
        for note in self.t["original_notes"]:
            out+='<aside id="'+esc(note["id"])+'" class="original-note" data-origin="'+esc(note["kind"])+'" data-source-key-targets="'+esc(json.dumps(note["source_keys"],ensure_ascii=False,separators=(",",":")))+'"><h3>'+esc(note["title"])+"</h3>"+note["html"]+"</aside>"
        out+='<h3>شروع دے عارضی اصطلاحی چُون</h3><dl class="term-grid">'
        for row in self.t["provisional_terms"]:
            out+="<dt>"+esc(row["english"])+"</dt><dd>"+esc(row["punjabi"])+" <span class=\"component-limit\">("+esc(row["status"])+")</span></dd>"
        return out+"</dl></section>"
    def fallback(self):
        out='<section id="b40-opening-source-math" data-origin="renderer-ui"><h2>'+UI["raw"]+'</h2><p>ہر روپ دے نال اصل ماخذ دا جیویں دا تیویں متن، حدبند پارسر دا درخت تے واپس جوڑن جوگ ٹوکن حساب محفوظ اے۔ ایہہ پورا TeX نہیں۔</p>'
        for record in self.notice["math_records"]:
            i=record["number"];out+='<details id="source-tex-'+str(i).zfill(3)+'" class="raw-tex-fallback" data-tex-owner="'+esc(record["owner"])+'" data-source-slot-token="'+esc(record["slot_token"])+'"><summary>فارمولا <bdi dir="ltr">'+str(i)+'</bdi> — اصل متن</summary><p class="tex-owner" dir="ltr" lang="en">'+esc(record["owner"])+'</p><pre dir="ltr"><code data-source-tex-fallback="true">'+esc(record["source_raw"],False)+"</code></pre></details>"
        return out+"</section>"

def footer(m):
    c=m["canonical"];base=c["repository"].removesuffix(".git")+"/-/blob/"+c["commit"]
    return f'''<footer id="credits" dir="ltr" lang="en"><h2>Sources, credits and changes — B40 opening</h2>
<p>Adapted from <a href="{base}/src/book.tex">Jim Hefferon, Linear Algebra, Fourth edition, second printing</a>. The exact source author, Saint Michael's College affiliation, location, publication date and edition/printing lines are retained. This reader stops before the generated table of contents and starred-subsection explanation; it is not complete front matter or a complete book.</p>
<p>The selected existing work option is <a href="https://creativecommons.org/licenses/by-sa/2.5/">Creative Commons Attribution-ShareAlike 2.5</a>, retained from the original GFDL / CC BY-SA 2.5 options. See the <a href="../provenance/upstream--hefferon-linear-algebra/LICENSE">pinned source license</a>, <a href="../provenance/hefferon-linear-algebra-id/NOTICE.id-ID.md">retained Indonesian-edition notice</a>, and <a href="../provenance/b40-opening-component-notices.json">opening component and reversible-math evidence</a>. This is not a new rights/supply audit or blanket component clearance. No endorsement by Jim Hefferon or Saint Michael's College is implied.</p>
<p>Both one-page PDF components are byte-exact pinned originals and are linked from their figures. Their transparent PNG previews were rasterized with Poppler at 144 dpi without running TeX or Asymptote. They are displayed separately in source layer order and explicitly do not claim exact upstream cover placement; no mirror, crop or recolor was applied. The source provides no alt, so Punjabi descriptions are visibly identified as original accessibility additions.</p>
<p>Changes: 174 source-bound Punjabi slots; six source tabular environments represented as two semantic data tables, one 14-week schedule, two lineated quotations and one address/credit block; RTL prose with LTR-isolated math, dates, names and section identifiers. A strictly limited nonexecuting parser derives 76 MathML owners from exact raw TeX and source-bound Hefferon macros. Raw TeX, delimiters, application/x-tex annotations, reversible token ledgers and spacing normalization records are retained. This is not universal LaTeX support.</p>
<p>The <a href="{m["comparison"]["repository"].removesuffix(".git")}/tree/{m["comparison"]["commit"]}">pinned Indonesian comparison</a> informed comparison only. Source historical availability, price, latest-version, contact and software claims remain Jim Hefferon's dated source voice, not current verification. Separate original notes qualify them without replacing source blocks. Produced with OpenAI Codex assistance at the user's direction.</p>
<p>Coverage: default opening only. Generated contents and the starred-subsection explanation remain required before Chapter One. The entire B40 book and five-work A10/A20/A30/B10/B40 assignment remain incomplete. Technical terms remain provisional; native-language, educator, browser and assistive-technology review are separate. No training or fine-tuning dataset is created. <a href="../source-excerpts/b40-opening.json">Frozen raw witness</a> · <a href="../source-excerpts/manifest-b40-opening.json">Source manifest</a> · <a href="../qa/b40-opening-language-notes.md">Language/source notes</a>.</p></footer>'''

def build():
    m,t,repo=load();require(NOTICES.exists(),"Run preparation first")
    notice=json.loads(NOTICES.read_text(encoding="utf-8"))
    require(notice["manifest_sha256"]==file_hash(MANIFEST) and notice["translation_sha256"]==file_hash(TRANSLATION) and notice["witness_sha256"]==file_hash(WITNESS),"Stale component notice")
    for comp in notice["components"]:
        require(file_hash(BASE/comp["prepared_path"])==comp["source_sha256"],"Prepared PDF differs")
        require(file_hash(BASE/comp["preview"]["path"])==comp["preview"]["sha256"],"Preview differs")
    r=Reader(m,t,notice);source=r.cover()+r.symlist()+r.preface()
    require(set(r.used)==set(m["expected_source_keys"]) and len(r.used)==len(m["expected_source_keys"])==174,"All 174 source keys exactly once")
    require(r.math_seen==[(x["owner"],x["slot_token"]) for x in notice["math_records"]],"All math owners/order differ")
    css=(BASE/"styles/reader.css").read_text(encoding="utf-8")+LOCAL_CSS
    result=f'''<!doctype html>
<html lang="pnb-Arab-PK" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="source-author" content="Jim Hefferon"><meta name="source-edition" content="Fourth edition, second printing"><meta name="source-publication-date" content="2021-Oct-12"><title>خطی الجبرا — B40 مُڈھلا حصہ</title><style>{css}</style></head>
<body class="b40-opening"><header><p class="eyebrow"><bdi dir="ltr" lang="en">B40 / Linear Algebra / opening</bdi></p><p class="status">ابتدائی ترجمہ · پنجابی دے ماہر تے ریاضی دے استاد دی جانچ ہن تک نہیں ہوئی۔</p><nav aria-label="حصے"><a href="#b40-opening-source">ماخذ دا ترجمہ</a> · <a href="#b40-opening-original-notes">وکھرے نوٹ</a> · <a href="#b40-opening-source-math">اصل فارمولے</a> · <a href="#credits">ماخذ تے انتساب</a></nav></header>
<main><p class="source-label" data-origin="renderer-ui">{UI["source"]}</p><article id="b40-opening-source">{source}</article>{r.originals()}{r.fallback()}<p class="status" data-origin="renderer-ui">فہرستِ مضامین تے ستارے والی وضاحت اگلا لازمی ماخذ حصہ نیں؛ باب ہن شامل نہیں۔</p></main>{footer(m)}</body></html>
'''
    check=re.sub(r"<(meta|img|mspace)\b([^<>]*?)(?<!/)>",r"<\1\2/>",result.replace("<!doctype html>",""))
    root=E.fromstring(check.encode());ids=root.xpath("//@id")
    require(len(ids)==len(set(ids)),"Duplicate IDs")
    require(not root.xpath("//script|//iframe|//object|//embed"),"Unexpected executable/embed")
    require(not any(TOKEN.search(x) for x in root.xpath("//text()")),"Unresolved text placeholder")
    OUTPUT.parent.mkdir(exist_ok=True);OUTPUT.write_text(result,encoding="utf-8",newline="\n")
    print("Built B40-opening: 174 keys, 76 MathML owners, 6 source table layouts, 2 exact PDFs/previews; stops before TOC.")

if __name__=="__main__":build()
