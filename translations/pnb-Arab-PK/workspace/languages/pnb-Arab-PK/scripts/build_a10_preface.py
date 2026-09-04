"""Deterministic, full-hierarchy m82630 reader; existing shared builders are read-only."""
import html
import json
import re
import xml.etree.ElementTree as ET

from prepare_a10_preface import (BASE, MANIFEST, TRANSLATION, EXCERPT, NOTICES, N, MD,
    DEFAULT_CREDIT, load_inputs, notice_record, file_hash, require)

OUTPUT = BASE/'reader/a10-preface.html'
LOCAL_CSS = '''
.a10-preface .source-label, .a10-preface footer, .a10-preface bdi { overflow-wrap:anywhere; }
.a10-preface h4 { font-size:1.1rem; color:var(--accent); margin-block:1rem .4rem; }
.a10-preface .source-list-no-bullets { list-style:none; padding-inline-start:0; }
.a10-preface .source-mixed-para { display:block; }
.a10-preface .inline-source-media { display:inline; white-space:normal; }
.a10-preface .inline-source-media img { display:inline-block; width:var(--icon-width); height:var(--icon-height); max-width:100%; min-width:0; padding:0; border:0; vertical-align:middle; }
.a10-preface .alt-advisory { font-size:.8rem; margin-inline:.25rem; }
.a10-preface .source-media { max-width:100%; margin-block:1rem; }
.a10-preface .source-media img { display:block; width:791px; min-width:791px; max-width:none; height:auto; }
.a10-preface .figure-scroll { direction:ltr; border:1px solid #cad7d1; background:white; }
.a10-preface .bridge dl { display:grid; grid-template-columns:minmax(6rem,.65fr) minmax(0,1fr); gap:.4rem 1rem; }
.a10-preface .bridge dt { font-weight:600; }
.a10-preface .bridge dd { margin:0; overflow-wrap:anywhere; }
@media (max-width:600px) { .a10-preface .bridge dl { display:block; } .a10-preface .bridge dd { margin-block-end:.7rem; } }
@media print { .a10-preface .source-media img { width:100%; min-width:0; max-width:791px; } }
'''


def esc(value):
    return html.escape(str(value), quote=True)


def fragment(value):
    return ET.fromstring('<fragment>'+re.sub(r'<br\s*>', '<br/>', value)+'</fragment>')


class Reader:
    def __init__(self, m, t):
        self.m, self.t = m, t
        self.used = []
        self.images = {x['media_id']: x for x in m['images']}

    def block(self, key):
        require(key not in self.used, 'Duplicate source translation key '+key)
        self.used.append(key)
        value = self.t['source_blocks'][key]
        require(not re.search(r'[\u0a00-\u0a7f\ufffd\u061c\u200b\u200e\u200f\u202a-\u202e\u2066-\u2069]', value), 'Invalid source script')
        parsed = fragment(value)
        for node in parsed.iter():
            require(node.tag in ('fragment','em','strong','bdi','br'), 'Unexpected translation tag '+node.tag)
            require(node.attrib in ({}, {'dir':'ltr'}, {'dir':'ltr','lang':'en'}), 'Unexpected translation attributes')
        return value

    def media(self, node):
        ident = node.get('id')
        spec = self.images[ident]
        alt = self.block(ident+'/alt')
        require(not list(fragment(alt)), 'Faithful source alt must be plain text')
        override = self.t['image_alt_overrides'][ident]
        require(not list(fragment(override)), 'Corrected alt must be plain text')
        note = self.t['image_alt_note_ids'][ident]
        require(fragment(self.t['bridge_after_html']).find('.//*[@id="'+note+'"]') is not None, 'Original alt note missing')
        url = '../'+spec['path']
        image = (f'<img id="{ident}" data-source-tag="media" data-source-key="{ident}/alt" '
                 f'src="{esc(url)}" alt="{esc(override)}" data-source-alt="{esc(alt)}" '
                 f'aria-describedby="{esc(note)}" width="{spec["width"]}" height="{spec["height"]}">')
        advisory = f'<span class="alt-advisory" data-origin="renderer-ui"><a href="#{esc(note)}">تصویری وضاحت دا نوٹ</a></span>'
        if spec['parent_tag'] == 'para':
            return (f'<span class="inline-source-media" data-source-child="{ident}" '
                    f'style="--icon-width:{spec["width"]}px;--icon-height:{spec["height"]}px">{image}{advisory}</span>')
        return (f'<div class="source-media" data-source-child="{ident}"><div class="figure-scroll" dir="ltr" '
                f'tabindex="0" role="region" aria-label="تِن محوری گراف">{image}</div>'
                f'<p class="scroll-hint" data-origin="renderer-ui">تنگ سکرین اُتے تصویر نوں پاسے ول سرکا کے ویکھو؛ '
                f'<a href="{esc(url)}">اصل تصویر وکھری کھولو</a>۔{advisory}</p></div>')

    def node(self, source, depth=0, parent=None):
        tag = source.tag.removeprefix(N)
        ident = source.get('id')
        attrs = f' data-source-tag="{tag}"'
        if ident:
            attrs += f' id="{esc(ident)}"'
        if source.get('class'):
            attrs += f' data-source-class="{esc(source.get("class"))}"'
        if tag == 'media':
            return self.media(source)
        if tag == 'title':
            key = (parent.get('id') or 'm82630')+'/title'
            return f'<h{depth+1}{attrs} data-source-key="{key}">{self.block(key)}</h{depth+1}>'
        if tag in ('para', 'item'):
            key = ident if tag == 'para' else parent.get('id')+'/item/'+str(list(parent).index(source)+1)
            value = self.block(key)
            children = source.findall(N+'media')
            for index, child in enumerate(children):
                token = '{{child:'+str(index)+'}}'
                require(value.count(token) == 1, 'Mixed source child placeholder mismatch')
                value = value.replace(token, self.media(child))
            require('{{' not in value, 'Unresolved source placeholder')
            htmltag = 'p' if tag == 'para' else 'li'
            extra = ' class="source-mixed-para"' if children else ''
            return f'<{htmltag}{attrs} data-source-key="{key}"{extra}>{value}</{htmltag}>'
        if tag in ('content', 'section', 'list'):
            if tag == 'list':
                htmltag = 'ul'
                attrs += ' data-source-list-type="'+esc(source.get('list-type','unspecified'))+'"'
                attrs += ' data-source-bullet-style="'+esc(source.get('bullet-style','unspecified'))+'"'
                attrs += ' class="'+('source-list-no-bullets' if source.get('bullet-style') == 'none' else 'source-list')+'"'
            else:
                htmltag = 'section'
            inner = ''.join(self.node(child, depth+(tag == 'section'), source) for child in source)
            return f'<{htmltag}{attrs}>{inner}</{htmltag}>'
        raise ValueError('Unsupported source node: '+tag)


def build():
    m, t, source, prepared, credit_text = load_inputs()
    for spec, target, data in prepared:
        require(target.is_file() and file_hash(target) == spec['sha256'], 'Run prepare_a10_preface.py first')
    require(json.loads(NOTICES.read_text(encoding='utf-8')) == notice_record(m, prepared, credit_text), 'Component notice stale')
    for field, ident in [('bridge_before_html','a10-preface-source-context'),('bridge_after_html','a10-preface-bridge')]:
        root = fragment(t[field])[0]
        require(root.get('id') == ident and root.get('data-origin') == 'original-bridge', 'Original bridge separation missing')
    renderer = Reader(m, t)
    source_html = renderer.node(source.find(N+'title'), parent=source)+renderer.node(source.find(N+'content'))
    require(renderer.used == m['source_text_keys_in_order'], '87 source keys were not used in exact order')
    meta = source.find(N+'metadata')
    metadata = ''.join(f'<meta name="source-{name}" content="{esc(meta.find(MD+name).text or "")}">'
                       for name in ('content-id','title','abstract','uuid'))
    css = (BASE/'styles/reader.css').read_text(encoding='utf-8')+LOCAL_CSS
    url = m['upstream_url']+'/blob/'+m['commit']+'/'+m['path']
    result = f'''<!doctype html>
<html lang="pnb-Arab-PK" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="Complete m82630 preface in Shahmukhi Punjabi; not a complete textbook"><meta name="source-document-class" content="preface">{metadata}<title>{esc(t['title'])} — A10 preface</title><style>{css}</style></head>
<body class="a10-reader a10-preface"><header><p class="eyebrow"><bdi dir="ltr">A10 / col31130 / m82630</bdi></p><p>{esc(t['subtitle'])}</p><p class="status">ابتدائی ترجمہ · پنجابی دے ماہر تے ریاضی دے استاد دی جانچ ہن تک نہیں ہوئی۔</p><nav aria-label="حصے"><a href="#a10-preface-source">ماخذ دا ترجمہ</a> · <a href="#a10-preface-bridge">ساڈے نوٹ تے لفظاں دی کُنجی</a> · <a href="#credits">ماخذ تے انتساب</a> · <a href="a10-introduction.html">باب دی جان پہچان</a></nav></header>
<main><p class="source-label" data-origin="renderer-ui">ماخذ: <bdi dir="ltr" lang="en">OpenStax Elementary Algebra 2e</bdi>۔ ایتھے پورا دیباچہ <bdi dir="ltr">m82630</bdi> ترجمہ کیتا گیا اے؛ ایہہ پوری کتاب نہیں۔</p>{t['bridge_before_html']}<article id="a10-preface-source" data-source-tag="document" data-source-class="preface" data-source-module="m82630">{source_html}</article>{t['bridge_after_html']}<p class="status" data-origin="renderer-ui">پنجاں مقررہ کتاباں دا پورا کم ہن وی جاری اے۔</p></main>
<footer id="credits" lang="en" dir="ltr"><h2>Sources, credits and changes — A10 preface</h2>
<p>Adapted from <a href="{esc(url)}">OpenStax Elementary Algebra 2e, module m82630: Preface</a>, collection col31130. Original senior contributing authors: Lynn Marecek; MaryAnne Anthony-Smith; Andrea Honeycutt Mathis. Source publisher: OpenStax / Rice University. All 21 reviewer credits and three named author affiliations are retained in source order, including the canonical spelling Saint Louis Iniversity.</p>
<p>The existing A10 notice states <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International</a>, subject to component-specific credits and restrictions. This adaptation retains that license framework and those restrictions. See the retained <a href="../provenance/A10-release/NOTICE.txt">A10 release notice</a>, <a href="../provenance/upstream--osbooks-prealgebra-bundle/LICENSE">canonical license text</a>, and <a href="../provenance/a10-preface-component-notices.json">selected component evidence</a>. No new clearance is asserted.</p>
<p id="a10-preface-art-credit">Raw-source default art credit: <span data-origin="retained-source-credit">{DEFAULT_CREDIT}</span> The pinned source paragraph <a href="#eip-787">eip-787</a> provides this default for art without attribution in the text and retains component-specific permission limits. Named book authors are not relabeled as image creators. This source claim and the media identity records are retained, not independently verified as image-specific clearance.</p>
<p>OpenStax and Rice University do not endorse this translation. Their names, logos and marks are not licensed by the source notice. All four original images are unchanged and unmirrored. The three inline icons are static illustrations, not functional controls. The graph remains unnumbered section-level media; no figure or caption is invented.</p>
<p>Changes: complete translation of 87 source blocks, with all 66 source IDs, 25 sections, 23 list items and 31 explicit newlines retained. Original metadata, including the original title, is retained separately; the translated visible document title appears once. RTL prose uses LTR isolation for source numbers, names and English. Three source lists preserve their declared attributes; the third has unspecified source list type, and its visible bullets are presentation only.</p>
<p>Faithful translated source alts are retained in data-source-alt. Separately labeled accessible overrides describe the visible originals, with visible correction links and aria-describedby pointing to the original explanations. The missing graph sentences, the icon description differences, Prealgebra 2e and Saint Louis Iniversity remain traceable. Opening context and closing correction/word-key material are original additions outside the source article.</p>
<p>Indonesian comparison: <a href="https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id/releases/tag/v1.0.2">Elementary Algebra 2e Indonesian preservation release v1.0.2</a>. Its complete-book publication claim and process provenance describe that source release, not this local Punjabi reader. This Punjabi adaptation was produced with OpenAI Codex assistance at the user's direction; original human-contributor credits remain intact. Source institutional, resource, access and licensing statements are pinned-source claims, not newly verified current offers.</p>
<p>Coverage: complete m82630 preface only, not the whole textbook. The complete A10, A20, A30, B10 and B40 workflow remains unfinished. This is not a training or fine-tuning dataset. Native-language, educator, assistive-technology and browser review remain separate. <a href="../source-excerpts/a10-preface.cnxml">Frozen source witness</a> · <a href="../source-excerpts/manifest-a10-preface.json">Source manifest</a> · <a href="../qa/a10-preface-language-notes.md">Language and source notes</a>.</p></footer></body></html>
'''
    ET.fromstring(re.sub(r'<(meta|img|br)(\s[^<>]*?)?\s*/?>', lambda match: match.group(0).rstrip('/>')+'/>', result.replace('<!doctype html>','')))
    OUTPUT.write_text(result, encoding='utf-8', newline='\n')
    print('Built complete A10 preface: 87 keys / 66 IDs / 25 sections / 4 originals.')


if __name__ == '__main__':
    build()
