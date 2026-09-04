"""Deterministic B10-only frontmatter reader; no shared renderer edits or upstream execution."""
import html
import json
import re
from lxml import etree as E
from prepare_b10_frontmatter import (BASE, MANIFEST, TRANSLATION, EXCERPT, NOTICES,
    XID, XI, SLOT_TAGS, load_inputs, notice_record, source_path, file_hash, require)

OUTPUT = BASE/'reader/b10-frontmatter.html'
LOCAL_CSS = '''
.b10-frontmatter .source-label, .b10-frontmatter footer, .b10-frontmatter bdi { overflow-wrap:anywhere; }
.b10-frontmatter .source-docinfo { border-block:1px solid #cad7d1; padding-block:.5rem 1rem; }
.b10-frontmatter .source-brandlogo img { display:block; width:100px; max-width:100%; height:auto; padding:0; border:0; }
.b10-frontmatter .source-image img { display:block; width:200px; max-width:100%; height:auto; padding:0; border:0; }
.b10-frontmatter .source-sidebyside { max-width:100%; border-inline-start:3px solid #cad7d1; padding-inline-start:1rem; }
.b10-frontmatter .source-shortdescription, .b10-frontmatter .source-attribute, .b10-frontmatter .source-raw-setting { font-size:1rem; }
.b10-frontmatter details { max-width:100%; margin-block:1rem; }
.b10-frontmatter summary { cursor:pointer; font-size:1rem; }
.b10-frontmatter pre { direction:ltr; text-align:left; font:14px/1.6 Consolas,monospace; overflow:auto; max-width:100%; padding:.7rem; background:#f0f5f1; }
.b10-frontmatter .source-mixed-para { margin-block:.8rem; }
.b10-frontmatter .source-attribution { border-inline-start:3px solid #cad7d1; padding-inline-start:1rem; }
.b10-frontmatter .bridge dl { display:grid; grid-template-columns:minmax(6rem,.65fr) minmax(0,1fr); gap:.4rem 1rem; }
.b10-frontmatter .bridge dt { font-weight:600; }
.b10-frontmatter .bridge dd { margin:0; overflow-wrap:anywhere; }
@media (max-width:600px) { .b10-frontmatter .bridge dl { display:block; } .b10-frontmatter .bridge dd { margin-block-end:.7rem; } }
'''
AUTO_HEADINGS = {
    'docinfo':'کتاب بارے اصل معلومات',
    'titlepage':'سرورق دی لکھت',
    'colophon':'اشاعت تے لائسنس',
    'dedication':'نذر',
    'acknowledgement':'شکریہ',
}
SOURCE_LABEL = 'ایتھے اصل کتاب دی مُڈھلی معلومات تے دو پورے دیباچے نیں؛ ایہہ پوری کتاب یا باب صفر دا ترجمہ نہیں۔'
STATUS = 'ابتدائی ترجمہ · پنجابی دے ماہر تے ریاضی دے استاد دی جانچ ہن تک نہیں ہوئی۔'
PENDING = 'باب صفر تے باقی پنجاں کتاباں دا پورا کم ہن وی جاری اے۔'
COPY_HINT = 'اصل تصویر وکھری کھولو'
QR_HINT = 'تصویری وضاحت دا وکھرا نوٹ'
META_LABELS = {'macros':'اصل ریاضی دے ماکروز — صرف متن، بغیر چلائے',
               'latex-image-preamble':'اصل تصویری تیاری دا متن — بغیر چلائے'}


def esc(value):
    return html.escape(str(value), quote=True)


def frag(value):
    return E.fromstring(('<fragment>'+value+'</fragment>').encode())


def inner(node):
    return (html.escape(node.text,quote=False) if node.text else '')+''.join(E.tostring(c,encoding='unicode',method='html') for c in node)


class Reader:
    def __init__(self,m,t,roots):
        self.m,self.t,self.roots = m,t,roots
        self.used = []
        self.images = {x['id']:x for x in m['images']}
        self.url_ids = {x['source_key']:x['source_url_id'] for x in m['original_urls']}

    def key(self,e,file):
        return file+'#'+source_path(e)

    def attrs(self,e,file):
        tag = 'include' if e.tag == XI else e.tag
        value = ' data-source-node="'+esc(self.key(e,file))+'" data-source-tag="'+esc(tag)+'"'
        value += ' data-source-attributes="'+esc(json.dumps(dict(e.attrib),ensure_ascii=False,sort_keys=True,separators=(',',':')))+'"'
        if e.get(XID):
            value += ' id="'+esc(e.get(XID))+'"'
        return value

    def block(self,key,e=None):
        require(key not in self.used,'Duplicate source key '+key)
        self.used.append(key)
        value = self.t['source_blocks'][key]
        require(not re.search(r'[\u0a00-\u0a7f\ufffd\u061c\u200b\u200e\u200f\u202a-\u202e\u2066-\u2069]',value),'Invalid source script/control')
        f = frag(value)
        for n in f.iter():
            require(n.tag in ('fragment','bdi','em','q','a','span'),'Unsupported translated markup')
            require(not n.get('id') and not n.get('data-origin'),'Source block injection')
        if e is not None:
            def owned_inline(n):
                parent = n.getparent()
                while parent is not None and parent is not e:
                    if parent.tag == 'ul':
                        return False
                    parent = parent.getparent()
                return n is not e and parent is e
            for stag,ttag in [('q','q'),('em','em'),('url','a'),('ndash','span'),('pretext','bdi')]:
                source_nodes = [n for n in e.iter(stag) if owned_inline(n)]
                targets = list(f.iter(ttag))
                if stag in ('ndash','pretext'):
                    targets = [n for n in targets if n.get('data-source-tag') == stag]
                require(len(source_nodes)==len(targets),'Inline source count differs: '+key+'/'+stag)
                file = key.split('#')[0]
                for sn,tn in zip(source_nodes,targets):
                    tn.set('data-source-node',self.key(sn,file))
                    tn.set('data-source-tag',stag)
                    tn.set('data-source-attributes',json.dumps(dict(sn.attrib),ensure_ascii=False,sort_keys=True,separators=(',',':')))
                    if stag == 'url':
                        require(tn.get('href')==sn.get('href') and tn.get('data-source-url')==self.url_ids[self.key(sn,file)],'URL source binding differs')
        return inner(f)

    def image(self,e,file,ident):
        spec = self.images[ident]
        url = '../'+spec['planned_reader_path']
        alt = self.t['original_image_alt_overrides'][ident]
        require('<' not in alt and '>' not in alt,'Alt override must be plain')
        extra = ' data-alt-origin="original-accessibility-description"'
        if ident == 'qrcode':
            rawalt = spec['source_alt']
            key = self.m['source_keys'][-1]
            translated = ''.join(frag(self.t['source_blocks'][key]).itertext())
            note = self.t['image_alt_note_ids'][ident]
            extra += ' data-source-alt="'+esc(rawalt)+'" data-translated-source-alt="'+esc(translated)+'" data-source-alt-owner="sidebyside" aria-describedby="'+esc(note)+'"'
        else:
            extra += ' data-source-alt-present="false"'
        image = '<img src="'+esc(url)+'" alt="'+esc(alt)+'" width="'+str(spec['width'])+'" height="'+str(spec['height'])+'"'+extra+'>'
        if ident == 'cover4':
            image = '<a data-source-brandlogo-url="true" href="'+esc(e.get('url'))+'">'+image+'</a>'
        hint = '<p class="scroll-hint" data-origin="renderer-ui"><a href="'+esc(url)+'">'+COPY_HINT+'</a>'
        if ident == 'qrcode':
            hint += ' · <a href="#'+esc(note)+'">'+QR_HINT+'</a>'
        return '<div'+self.attrs(e,file)+' class="'+('source-brandlogo' if ident=='cover4' else 'source-image')+'">'+image+hint+'</p></div>'

    def node(self,e,file,depth=2):
        tag,key,attrs = e.tag,self.key(e,file),self.attrs(e,file)
        if tag == 'brandlogo':
            return self.image(e,file,'cover4')
        if tag == 'image':
            return self.image(e,file,'qrcode')
        if tag == 'blurb':
            shelfkey = key+'/@shelf'
            return ('<section'+attrs+' class="source-blurb"><p class="source-attribute" data-source-key="'+esc(shelfkey)+'" data-source-attribute="shelf">'+self.block(shelfkey)+'</p>'
                    '<p data-source-key="'+esc(key)+'">'+self.block(key,e)+'</p></section>')
        if tag in ('macros','latex-image-preamble'):
            body = '<pre dir="ltr" data-source-text-slot="own">'+esc(e.text or '')+'</pre>'
            for c in e:
                require(c.tag == XI,'Unexpected opaque metadata child')
                body += '<p'+self.attrs(c,file)+' class="source-raw-setting"><bdi dir="ltr" lang="en" data-origin="renderer-ui">'+esc(c.get('href'))+' (parse='+esc(c.get('parse'))+')</bdi></p>'
                body += '<pre dir="ltr" data-source-text-slot="tail">'+esc(c.tail or '')+'</pre>'
            return '<details'+attrs+'><summary data-origin="renderer-ui">'+META_LABELS[tag]+'</summary>'+body+'</details>'
        if tag == 'document-id':
            return '<p'+attrs+' class="source-raw-setting" dir="ltr" lang="en">'+esc(e.text or '')+'</p>'
        if tag == 'cross-references':
            return '<p'+attrs+' class="source-raw-setting"><bdi dir="ltr" lang="en" data-origin="renderer-ui">cross-references: '+esc(e.get('text'))+'</bdi></p>'
        if tag == 'url':
            require(not list(e) and not (e.text or '').strip(),'Only standalone source URL expected')
            return '<a'+attrs+' data-source-url="'+self.url_ids[key]+'" href="'+esc(e.get('href'))+'"><bdi dir="ltr" lang="en">'+esc(e.get('visual'))+'</bdi></a>'
        if key in self.t['source_blocks']:
            value = self.block(key,e)
            if list(e.findall('ul')):
                require(value.count('{{child:0}}') == 1,'List placeholder required')
                value = value.replace('{{child:0}}',self.node(e.find('ul'),file,depth))
                htmltag,css = 'div',' class="source-mixed-para"'
            else:
                require('{{child:' not in value,'Unresolved source placeholder')
                htmltag = ('h1' if file=='dmoi.ptx' and tag=='title' else 'h'+str(depth) if tag=='title' else 'p')
                css = ' class="source-'+tag+'"'
            return '<'+htmltag+attrs+' data-source-key="'+esc(key)+'"'+css+'>'+value+'</'+htmltag+'>'
        htmltag = 'ul' if tag=='ul' else 'li' if tag=='li' else 'section' if tag in ('docinfo','frontmatter','titlepage','colophon','dedication','acknowledgement','preface','paragraphs') else 'div'
        require(tag in ('docinfo','frontmatter','titlepage','author','colophon','website','copyright','dedication','acknowledgement','preface','paragraphs','ul','li','attribution','sidebyside'),'Unsupported structural source '+tag)
        label = AUTO_HEADINGS.get(tag)
        if tag=='preface' and e.find('title') is None:
            label = 'دیباچہ'
        heading = '<h2 data-origin="renderer-ui">'+label+'</h2>' if label else ''
        children = ''.join(self.node(c,file,3 if tag=='paragraphs' else depth) for c in e)
        return '<'+htmltag+attrs+' class="source-'+tag+'">'+heading+children+'</'+htmltag+'>'

    def source_html(self):
        dmoi = self.roots['dmoi.ptx']
        book = dmoi.find('book')
        return ('<article id="b10-frontmatter-source"'+self.attrs(dmoi,'dmoi.ptx')+'>'
                +self.node(self.roots['bookinfo.ptx'],'bookinfo.ptx')
                +'<section'+self.attrs(book,'dmoi.ptx')+' class="source-book">'
                +self.node(book.find('title'),'dmoi.ptx')+self.node(book.find('subtitle'),'dmoi.ptx')
                +self.node(self.roots['frontmatter.ptx'],'frontmatter.ptx')+'</section></article>')


def footer(m):
    canonical = m['authority']['canonical']['repository'].removesuffix('.git')+'/blob/'+m['authority']['canonical']['commit']+'/source/frontmatter.ptx'
    comparison = m['authority']['comparison']['repository'].removesuffix('.git')+'/tree/'+m['authority']['comparison']['commit']
    return f'''<footer id="credits" dir="ltr" lang="en"><h2>Sources, credits and changes — B10 front matter</h2>
<p>Adapted from <a href="{canonical}">Oscar Levin, Discrete Mathematics: An Open Introduction, Fourth Edition</a>. Original author: Oscar Levin, University of Northern Colorado. Source titlepage: Fall 2024. Copyright 2013–2025 Oscar Levin. Both source prefaces, dedication, acknowledgements, author attribution lines and earlier title/docinfo wording are retained.</p>
<p>The existing active fourth-edition notice states <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International</a>. This adaptation retains that work-level framework and component-specific restrictions. The archived <a href="../provenance/discrete-mathematics-open-introduction-id/LICENSE">existing edition license</a> records the discrepancy with the <a href="../provenance/upstream--discrete-book/LICENSE">stale upstream root BY-SA 4.0 text</a>; neither source notice was rewritten. See <a href="../provenance/discrete-mathematics-open-introduction-id/THIRD_PARTY_NOTICES.md">retained component notices</a> and <a href="../provenance/b10-frontmatter-component-notices.json">selected component evidence</a>. This is not a new rights audit or image-clearance claim.</p>
<p>No endorsement by Oscar Levin or University of Northern Colorado is implied. The original 100×142 cover/logo and 200×200 QR are unchanged, unmirrored and uncropped. Source QR description is retained verbatim in data-source-alt and faithfully translated in its original sidebyside slot; a separate original accessible description and visible correction note do not certify its undecoded payload. The cover's alt description is an original accessibility addition because the source has none.</p>
<p>Changes: 50 complete source-bound Punjabi slots; RTL prose with LTR-isolated English and numerals; four original IDs and complete source hierarchy/order; original opening context and closing correction/term key outside source translation. All source macros/preamble/include metadata are inert escaped text. No TeX, external runtime, analytics or online grading is executed or copied. Source interactive/resource/legal statements describe the pinned author's text, not current verification or local implemented features.</p>
<p><a href="{comparison}">Pinned Indonesian comparison</a> was read for comparison only. Its added colophon, DOI, initialism, final website and replacement QR are not canonical English source content. Original English author/edition/component credits are retained. This Punjabi adaptation was produced with OpenAI Codex assistance at the user's direction.</p>
<p>Coverage: complete earlier metadata/title/front matter only. Chapter 0 and the rest of B10 remain untranslated here; A10, A20, A30, B10 and B40 remain an unfinished full-work assignment. No training or fine-tuning dataset is created. Native-language, educator, assistive-technology and browser review remain separate. <a href="../source-excerpts/b10-frontmatter.ptx">Frozen witness</a> · <a href="../source-excerpts/manifest-b10-frontmatter.json">Exact source manifest</a> · <a href="../qa/b10-frontmatter-language-notes.md">Language and source notes</a>.</p></footer>'''


def build():
    m,t,source,roots,prepared = load_inputs()
    for spec,target,data in prepared:
        require(target.is_file() and file_hash(target)==spec['sha256'],'Run prepare_b10_frontmatter.py first')
    require(NOTICES.is_file() and json.loads(NOTICES.read_text(encoding='utf-8'))==notice_record(m,prepared),'Component notice stale')
    for field,ident in [('bridge_before_html','b10-frontmatter-source-context'),('bridge_after_html','b10-frontmatter-bridge')]:
        n=frag(t[field])[0]
        require(n.get('id')==ident and n.get('data-origin')=='original-bridge','Original bridge identity differs')
    renderer=Reader(m,t,roots)
    content=renderer.source_html()
    require(renderer.used==m['source_keys'],'All 50 translation keys must render exactly once in order')
    css=(BASE/'styles/reader.css').read_text(encoding='utf-8')+LOCAL_CSS
    result=f'''<!doctype html>
<html lang="pnb-Arab-PK" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="Complete canonical fourth-edition B10 frontmatter in Punjabi; not a complete textbook"><meta name="source-book-id" content="dmoi4"><meta name="source-document-id" content="dmoi-4"><meta name="source-author" content="Oscar Levin"><meta name="source-edition" content="Fourth Edition"><meta name="source-date" content="Fall 2024"><meta name="source-copyright" content="2013–2025 Oscar Levin"><title>{esc(t['title'])} — B10 front matter</title><style>{css}</style></head>
<body class="b10-frontmatter"><header><p class="eyebrow"><bdi dir="ltr">B10 / dmoi4 / frontmatter</bdi></p><p>{esc(t['subtitle'])}</p><p class="status">{STATUS}</p><nav aria-label="حصے"><a href="#b10-frontmatter-source">ماخذ دا ترجمہ</a> · <a href="#preface">پہلا دیباچہ</a> · <a href="#b10-frontmatter-bridge">ساڈے نوٹ تے لفظاں دی کُنجی</a> · <a href="#credits">ماخذ تے انتساب</a></nav></header>
<main><p class="source-label" data-origin="renderer-ui">{SOURCE_LABEL}</p>{t['bridge_before_html']}{content}{t['bridge_after_html']}<p class="status" data-origin="renderer-ui">{PENDING}</p></main>{footer(m)}</body></html>
'''
    inspection=re.sub(r'<(meta|img|br)\b([^<>]*?)(?<!/)>',r'<\1\2/>',result.replace('<!doctype html>',''))
    parsed=E.fromstring(inspection.encode())
    ids=[n.get('id') for n in parsed.iter() if n.get('id')]
    require(len(ids)==len(set(ids)),'Duplicate HTML IDs')
    require(not parsed.xpath('//script|//iframe|//object|//embed'),'Unexpected executable/external runtime')
    require('{{child:' not in result,'Unresolved source child slot')
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(result,encoding='utf-8',newline='\n')
    print('Built B10 frontmatter: 50 keys, 4 original IDs, both full prefaces, 2 unchanged PNGs; whole assignment incomplete.')


if __name__ == '__main__':
    build()
