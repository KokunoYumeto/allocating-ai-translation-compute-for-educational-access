"""Deterministic complete-m81357 Shahmukhi reader; shared builders stay read-only."""
import html
import json
import re
import xml.etree.ElementTree as ET

from prepare_a20_preface import (
    BASE, MANIFEST, TRANSLATION, EXCERPT, NOTICES, N, DEFAULT_CREDIT,
    load_inputs, notice_record, fh, require,
)

OUTPUT = BASE / 'reader/a20-preface.html'
LOCAL_CSS = '''
.a20-preface .source-label, .a20-preface footer, .a20-preface bdi { overflow-wrap:anywhere; }
.a20-preface h4 { font-size:1.1rem; color:var(--accent); margin-block:1rem .4rem; }
.a20-preface .source-list-no-bullets { list-style:none; padding-inline-start:0; }
.a20-preface .source-mixed-para { display:block; }
.a20-preface .inline-source-media { display:inline; white-space:normal; }
.a20-preface .inline-source-media img { display:inline-block; width:var(--icon-width); height:var(--icon-height); max-width:100%; min-width:0; padding:0; border:0; vertical-align:middle; transform:none; }
.a20-preface .alt-advisory { font-size:.8rem; margin-inline:.25rem; }
.a20-preface .source-media { max-width:100%; margin-block:1rem; }
.a20-preface .source-media img { display:block; width:791px; min-width:791px; max-width:none; height:auto; transform:none; }
.a20-preface .figure-scroll { direction:ltr; border:1px solid #cad7d1; background:white; }
.a20-preface .figure-accessible-label { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }
.a20-preface .bridge dl { display:grid; grid-template-columns:minmax(6rem,.65fr) minmax(0,1fr); gap:.4rem 1rem; }
.a20-preface .bridge dt { font-weight:600; }
.a20-preface .bridge dd { margin:0; overflow-wrap:anywhere; }
@media (max-width:600px) { .a20-preface .bridge dl { display:block; } .a20-preface .bridge dd { margin-block-end:.7rem; } }
@media print { .a20-preface .source-media img { width:100%; min-width:0; max-width:791px; } }
'''


def esc(value):
    return html.escape(str(value), quote=True)


def fragment(value):
    return ET.fromstring('<fragment>' + re.sub(r'<br\s*>', '<br/>', value) + '</fragment>')


class Reader:
    def __init__(self, manifest, translation):
        self.m = manifest
        self.t = translation
        self.used = []
        self.images = {x['media_id']: x for x in manifest['images']}

    def block(self, key):
        require(key not in self.used, 'Duplicate source translation key ' + key)
        self.used.append(key)
        value = self.t['source_blocks'][key]
        require(not re.search(r'[\u0a00-\u0a7f\ufffd\u061c\u200b\u200e\u200f\u202a-\u202e\u2066-\u2069]', value), 'Invalid source script')
        parsed = fragment(value)
        for node in parsed.iter():
            require(node.tag in ('fragment', 'em', 'strong', 'bdi', 'br'), 'Unexpected translation tag ' + node.tag)
            require(node.attrib in ({}, {'dir': 'ltr'}, {'dir': 'ltr', 'lang': 'en'}), 'Unexpected translation attributes')
        return value

    def media(self, node):
        ident = node.get('id')
        spec = self.images[ident]
        faithful = self.block(ident + '/alt')
        override = self.t['image_alt_overrides'][ident]
        require(not list(fragment(faithful)) and not list(fragment(override)), 'Image alts must be plain text')
        note = self.t['image_alt_note_ids'][ident]
        require(fragment(self.t['bridge_after_html']).find('.//*[@id="' + note + '"]') is not None, 'Alt note missing')
        url = '../' + spec['path']
        language = ' dir="rtl" lang="pnb-Arab-PK"' if spec['parent_tag'] != 'para' else ''
        image = (f'<img id="{ident}" data-source-tag="media" data-source-key="{ident}/alt" src="{esc(url)}" '
                 f'alt="{esc(override)}" data-source-alt="{esc(faithful)}" aria-describedby="{esc(note)}" '
                 f'width="{spec["width"]}" height="{spec["height"]}"{language}>')
        advisory = f'<span class="alt-advisory" data-origin="renderer-ui"><a href="#{esc(note)}">تصویری وضاحت دا نوٹ</a></span>'
        if spec['parent_tag'] == 'para':
            return (f'<span class="inline-source-media" data-source-child="{ident}" '
                    f'style="--icon-width:{spec["width"]}px;--icon-height:{spec["height"]}px">{image}{advisory}</span>')
        return (f'<div class="source-media" data-source-child="{ident}"><span id="a20-preface-graph-label" '
                f'class="figure-accessible-label" data-origin="renderer-ui" dir="rtl" lang="pnb-Arab-PK">تِن محوری گراف</span>'
                f'<div class="figure-scroll" dir="ltr" tabindex="0" role="region" aria-labelledby="a20-preface-graph-label">{image}</div>'
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
            key = (parent.get('id') or 'm81357') + '/title'
            return f'<h{depth + 1}{attrs} data-source-key="{key}">{self.block(key)}</h{depth + 1}>'
        if tag in ('para', 'item'):
            key = ident if tag == 'para' else parent.get('id') + '/item/' + str(list(parent).index(source) + 1)
            value = self.block(key)
            children = source.findall(N + 'media')
            for index, child in enumerate(children):
                token = '{{child:' + str(index) + '}}'
                require(value.count(token) == 1, 'Mixed child placeholder mismatch')
                value = value.replace(token, self.media(child))
            require('{{' not in value, 'Unresolved source placeholder')
            html_tag = 'p' if tag == 'para' else 'li'
            extra = ' class="source-mixed-para"' if children else ''
            return f'<{html_tag}{attrs} data-source-key="{key}"{extra}>{value}</{html_tag}>'
        if tag in ('content', 'section', 'list'):
            if tag == 'list':
                html_tag = 'ul'
                attrs += ' data-source-list-type="' + esc(source.get('list-type', 'unspecified')) + '"'
                attrs += ' data-source-bullet-style="' + esc(source.get('bullet-style', 'unspecified')) + '"'
                attrs += ' class="' + ('source-list-no-bullets' if source.get('bullet-style') == 'none' else 'source-list') + '"'
            else:
                html_tag = 'section'
            inner = ''.join(self.node(child, depth + (tag == 'section'), source) for child in source)
            return f'<{html_tag}{attrs}>{inner}</{html_tag}>'
        raise ValueError('Unsupported source node ' + tag)


def build():
    m, t, source, prepared, credit_text = load_inputs()
    for spec, target, _ in prepared:
        require(target.is_file() and fh(target) == spec['sha256'], 'Run prepare_a20_preface.py first')
    require(json.loads(NOTICES.read_text(encoding='utf-8')) == notice_record(m, prepared, credit_text), 'Component notice stale')
    for field, ident in [('bridge_before_html', 'a20-preface-source-context'), ('bridge_after_html', 'a20-preface-bridge')]:
        root = fragment(t[field])[0]
        require(root.get('id') == ident and root.get('data-origin') == 'original-bridge', 'Original bridge separation missing')
    renderer = Reader(m, t)
    source_html = renderer.node(source.find(N + 'title'), parent=source) + renderer.node(source.find(N + 'content'))
    require(renderer.used == m['source_text_keys_in_order'], '89 source keys not used in exact order')
    metadata = source.find(N + 'metadata')
    md_uri = '{http://cnx.rice.edu/mdml}'
    meta_html = ''.join(f'<meta name="source-{name}" content="{esc(metadata.find(md_uri + name).text or "")}">'
                        for name in ('content-id', 'title', 'abstract', 'uuid'))
    css = (BASE / 'styles/reader.css').read_text(encoding='utf-8') + LOCAL_CSS
    url = m['upstream_url'] + '/blob/' + m['commit'] + '/' + m['path']
    result = f'''<!doctype html>
<html lang="pnb-Arab-PK" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="Complete m81357 preface in Shahmukhi Punjabi; not a complete textbook"><meta name="source-document-class" content="preface">{meta_html}<title>{esc(t['title'])} — A20 preface</title><style>{css}</style></head>
<body class="a20-reader a20-preface"><header><p class="eyebrow"><bdi dir="ltr">A20 / col31234 / m81357</bdi></p><p>{esc(t['subtitle'])}</p><p class="status">ابتدائی ترجمہ · پنجابی دے ماہر تے ریاضی دے استاد دی جانچ ہن تک نہیں ہوئی۔</p><nav aria-label="حصے"><a href="#a20-preface-source">ماخذ دا ترجمہ</a> · <a href="#a20-preface-bridge">ساڈے نوٹ تے لفظاں دی کُنجی</a> · <a href="#credits">ماخذ تے انتساب</a></nav></header>
<main><p class="source-label" data-origin="renderer-ui">ماخذ: <bdi dir="ltr" lang="en">OpenStax Intermediate Algebra 2e</bdi>۔ ایتھے پورا دیباچہ <bdi dir="ltr">m81357</bdi> ترجمہ کیتا گیا اے؛ ایہہ پوری کتاب نہیں۔</p>{t['bridge_before_html']}<article id="a20-preface-source" data-source-tag="document" data-source-class="preface" data-source-module="m81357">{source_html}</article>{t['bridge_after_html']}<p class="status" data-origin="renderer-ui">پنجاں مقررہ کتاباں دا پورا کم ہن وی جاری اے۔</p></main>
<footer id="credits" lang="en" dir="ltr"><h2>Sources, credits and changes — A20 preface</h2>
<p>Adapted from <a href="{esc(url)}">OpenStax Intermediate Algebra 2e, module m81357: Preface</a>, collection col31234. Original senior contributing authors retained in source order: Lynn Marecek; Andrea Honeycutt Mathis. Source publisher: OpenStax / Rice University. All 16 reviewer lines and both named author affiliations remain in the source article.</p>
<p>The existing A20 notice states <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International</a>, subject to component-specific credits and restrictions. This adaptation retains that framework and those restrictions. See the retained <a href="../provenance/A20-release/LICENSE.txt">A20 release license notice</a>, <a href="../provenance/upstream--osbooks-prealgebra-bundle/LICENSE">canonical license text</a>, and <a href="../provenance/a20-preface-component-notices.json">selected component evidence</a>. No new clearance is asserted.</p>
<p id="a20-preface-art-credit">Raw-source default art credit: <span data-origin="retained-source-credit">{DEFAULT_CREDIT}</span> The pinned source paragraph <a href="#eip-787">eip-787</a> supplies this default for art lacking an in-text attribution and retains component-specific permission limits. Media identity records are not image-specific clearance.</p>
<p>OpenStax and Rice University do not endorse this translation. Their names, logos and marks are not licensed. All four canonical images are unchanged and unmirrored. The three inline icons are static illustrations, not controls. The graph is unnumbered section-level media; no figure identity or caption is invented.</p>
<p>Changes: complete translation of 89 source owners, retaining all 194 source elements, 66 source IDs, 26 sections, 27 visible title owners plus the metadata title mirror, 33 paragraphs, 25 list items, 38 emphasis nodes and 27 explicit newlines. Original metadata stays separate and the translated visible title appears once. After the explicit book-title substitution, 56 canonical-English owners are A10 source candidates; after one A20 fidelity revision, 55 remain exact target reuses and 34 owners are independently translated or fidelity-revised, without changing frozen A10.</p>
<p>Faithful source alts remain in data-source-alt. Separately labeled accessible overrides describe the inspected pixels and point to visible original notes. The missing graph sentences, Indonesian RGB redraw, Chapter 8 singular/plural discrepancy, Answer Key question/answer wording, solve-functions wording, static-icon qualification and dated service claims remain traceable. Original opening context and closing discrepancy/term notes are outside the source article.</p>
<p>Indonesian comparison: <a href="https://github.com/KokunoYumeto/openstax-intermediate-algebra-2e-id/releases/tag/v0.3.0-wip">Intermediate Algebra 2e Indonesian editable checkpoint v0.3.0-wip</a>, an admitted partial 48/83-module comparison. It is not canonical and not a complete book. This Punjabi adaptation was produced with OpenAI Codex assistance at the user's direction; original human-contributor credits remain intact.</p>
<p>Coverage: complete m81357 preface only, not the textbook. The complete A10, A20, A30, B10 and B40 workflow remains unfinished. This is not a training or fine-tuning dataset. Native-language, educator, assistive-technology and independent browser review remain separate. <a href="../source-excerpts/a20-preface.cnxml">Frozen source witness</a> · <a href="../source-excerpts/manifest-a20-preface.json">Source manifest</a> · <a href="../qa/a20-preface-language-notes.md">Language and source notes</a>.</p></footer></body></html>
'''
    ET.fromstring(re.sub(r'<(meta|img|br)(\s[^<>]*?)?\s*/?>', lambda match: match.group(0).rstrip('/>') + '/>', result.replace('<!doctype html>', '')))
    OUTPUT.write_text(result, encoding='utf-8', newline='\n')
    print('Built A20-preface: 89 owners / 66 IDs / 194 source elements / 4 originals.')


if __name__ == '__main__':
    build()
