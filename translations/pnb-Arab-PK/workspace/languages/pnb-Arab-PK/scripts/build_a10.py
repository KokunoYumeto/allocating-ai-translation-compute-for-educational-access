"""Deterministic, bounded A10-001 reader; shared renderer/style inputs are read-only."""
from pathlib import Path
from html.parser import HTMLParser
import copy
import html
import json
import re
import xml.etree.ElementTree as ET
from prepare_a10 import BASE, ROOT, MATH, NOTICES, load_inputs, notice_record, file_hash, require, tag

ET.register_namespace('', MATH)
BLOCKS = {'figure', 'para', 'note', 'list', 'exercise', 'problem', 'solution', 'section', 'example', 'media'}
TRANSLATION = BASE / 'translations/a10-unit-001.json'
OUTPUT = BASE / 'reader/a10-unit-001.html'
LOCAL_CSS = '''
.a10-reader .source-mixed-para { margin-block:.8rem; }
.a10-reader .source-media { min-width:0; max-width:100%; margin-block:1rem; }
.a10-reader .source-media .figure-scroll { width:100%; max-width:100%; direction:ltr; overflow-x:auto; }
.a10-reader .source-media img { display:block; width:var(--source-width); min-width:var(--source-width); max-width:none; height:auto; padding:0; border:0; margin-inline:auto; background:white; }
.a10-reader .source-alt-advisory { font-size:.9rem; border-inline-start:3px solid #b98238; padding-inline-start:.7rem; }
.a10-reader .source-label, .a10-reader footer { overflow-wrap:anywhere; }
.a10-reader .source-solution { margin-block:1rem; padding-block-start:.4rem; }
.a10-reader .source-note-text { margin:0; }
.a10-reader .source-inline-part { display:inline-block; max-width:100%; vertical-align:baseline; }
'''


def attr(value):
    return html.escape(str(value), quote=True)


class Reader:
    def __init__(self, manifest, document, translation):
        self.manifest = manifest
        self.document = document
        self.translation = translation
        self.blocks = translation['source_blocks']
        self.used = []
        self.images = {entry['source_src']: entry for entry in manifest['images']}
        self.figure_labels = {entry['figure_id']: entry['local_label'] for entry in manifest['images'] if entry['figure_id']}
        self.correction_ids = {
            'fs-id1170655200451': 'a10-alt-correction-1',
            'fs-id1170655112880': 'a10-alt-correction-2'
        }

    def math_html(self, node):
        clone = copy.deepcopy(node)
        clone.tail = None
        clone.set('dir', 'ltr')
        return '<span class="math-isolate" dir="ltr">' + ET.tostring(clone, encoding='unicode') + '</span>'

    def group_inline_parts(self, value, node):
        tokens = [child for child in node if tag(child) == 'span' and child.get('class') == 'token']
        if not tokens:
            return value
        expected = [chr(ord('a') + ord((child.text or '').strip()) - 0x24D0) for child in tokens]
        labels = list(re.finditer(r'<bdi\b[^>]*>\(([a-e])\)', value))
        require([match[1] for match in labels] == expected, 'Changed inline source-part order')
        require(not any(tag(child) in BLOCKS for child in node), 'Block child cannot be grouped inside an inline part')
        result = value[:labels[0].start()]
        for index, label in enumerate(labels):
            end = labels[index + 1].start() if index + 1 < len(labels) else len(value)
            part = value[label.start():end]
            # Keep the original separators outside the atomic wrapping unit.
            # In particular, a source newline must still break the paragraph.
            suffix = re.search(r'((?:\s|<br\s*/?>)*)\Z', part)
            result += ('<span class="source-inline-part" data-source-part="' + label[1] + '">'
                       + part[:suffix.start()] + '</span>' + suffix[0])
        return result

    def translated(self, key, node):
        require(key not in self.used, 'Repeated translation key: ' + key)
        self.used.append(key)
        value = self.blocks[key]
        maths = [child for child in node if tag(child) == 'math']
        children = [child for child in node if tag(child) in BLOCKS]
        links = [child for child in node if tag(child) == 'link']
        for kind, sources in [('math', maths), ('child', children), ('link', links)]:
            positions = [int(value) for value in re.findall(r'\{\{' + kind + r':(\d+)\}\}', value)]
            require(positions == list(range(len(sources))), 'Changed ' + kind + ' placeholder order: ' + key)
        require(value.count('<br>') == sum(tag(child) == 'newline' for child in node), 'Changed newline count: ' + key)
        value = re.sub(r'\{\{math:(\d+)\}\}', lambda match: self.math_html(maths[int(match[1])]), value)
        value = re.sub(r'\{\{child:(\d+)\}\}', lambda match: self.render(children[int(match[1])], node), value)
        def link(match):
            target = links[int(match[1])].get('target-id')
            require(target in self.figure_labels, 'Unknown selected source link target')
            return '<a href="#' + attr(target) + '" data-source-target="' + attr(target) + '">شکل <bdi dir="ltr">' + attr(self.figure_labels[target]) + '</bdi></a>'
        return re.sub(r'\{\{link:(\d+)\}\}', link, value)

    def render(self, node, parent=None, index=0):
        name, sid = tag(node), node.get('id')
        ident = ' id="' + attr(sid) + '"' if sid else ''
        marker = ' data-source-tag="' + name + '"'
        if name == 'document':
            return ''.join(self.render(child, node, i) for i, child in enumerate(node))
        if name == 'section':
            return '<section' + ident + marker + ' class="translated">' + ''.join(self.render(child, node, i) for i, child in enumerate(node)) + '</section>'
        if name in {'example', 'exercise', 'problem', 'solution'}:
            out_tag = 'section' if name in {'example', 'solution'} else 'div'
            heading = ''
            if name == 'example':
                label = self.manifest['renderer_contract']['example_labels'][sid]
                heading = '<h2 class="example-label" data-origin="renderer-ui">حل کیتی مثال <bdi dir="ltr">' + attr(label) + '</bdi></h2>'
            # A source Solution title is rendered below once; no automatic duplicate.
            accessibility = ' aria-label="حل"' if name == 'solution' and not any(tag(child) == 'title' for child in node) else ''
            return '<' + out_tag + ident + marker + ' class="source-' + name + '"' + accessibility + '>' + heading + ''.join(self.render(child, node, i) for i, child in enumerate(node)) + '</' + out_tag + '>'
        if name in {'para', 'title', 'caption', 'item'}:
            key = parent.get('id') + '/item/' + str(index + 1) if name == 'item' else sid or parent.get('id') + '/' + name
            mixed = name == 'para' and any(tag(child) in BLOCKS for child in node)
            out_tag = 'div' if mixed else {'para': 'p', 'title': 'h2' if tag(parent) == 'section' else 'h3', 'caption': 'figcaption', 'item': 'li'}[name]
            classes = ' class="source-para source-mixed-para"' if mixed else ''
            value = self.translated(key, node)
            if name == 'para':
                value = self.group_inline_parts(value, node)
            return '<' + out_tag + ident + marker + classes + '>' + value + '</' + out_tag + '>'
        if name == 'figure':
            return '<figure' + ident + marker + '>' + ''.join(self.render(child, node, i) for i, child in enumerate(node)) + '</figure>'
        if name == 'media':
            key = sid + '/alt'
            require(key not in self.used, 'Repeated media alt')
            self.used.append(key)
            image = next(child for child in node if tag(child) == 'image')
            spec = self.images[image.get('src')]
            require(sid == spec['media_id'], 'Media image association changed')
            src = '../' + spec['path']
            child_marker = ' data-source-child="' + attr(sid) + '"' if parent is not None and tag(parent) == 'para' else ''
            warning = ''
            described = ''
            if sid in self.correction_ids:
                advisory_id = self.correction_ids[sid] + '-advisory'
                described = ' aria-describedby="' + advisory_id + '"'
                warning = '<p id="' + advisory_id + '" class="source-alt-advisory" data-origin="renderer-ui">ایس شکل دے ماخذ والے متبادل متن بارے <a href="#' + self.correction_ids[sid] + '">ساڈی وکھری درستی تے وضاحت وی ویکھو</a>۔</p>'
            return ('<div class="source-media"' + child_marker + '><div class="figure-scroll" dir="ltr" tabindex="0" role="region" aria-label="اصل شکل؛ لوڑ پئے تے پاسے سرکاؤ">'
                    + '<img' + ident + marker + ' src="' + attr(src) + '" alt="' + attr(self.blocks[key]) + '" width="' + str(spec['width']) + '" height="' + str(spec['height']) + '" style="--source-width:' + str(spec['width']) + 'px"' + described + '>'
                    + '</div><p class="scroll-hint" data-origin="renderer-ui">چھوٹی سکرین اُتے پوری شکل ویکھن لئی پاسے سرکاؤ، یا <a href="' + attr(src) + '">اصل شکل وکھری کھولو</a>۔</p>' + warning + '</div>')
        if name == 'note':
            note_class = node.get('class', '')
            if sid in self.manifest['renderer_contract']['direct_text_note_keys']:
                content = '<p class="source-note-text">' + self.translated(sid, node) + '</p>'
            else:
                content = ''.join(self.render(child, node, i) for i, child in enumerate(node))
            label = ' aria-label="آپ کر کے ویکھو"' if note_class == 'try' else ''
            return '<aside' + ident + marker + ' class="source-note source-' + attr(note_class) + '"' + label + '>' + content + '</aside>'
        if name == 'list':
            return '<ol' + ident + marker + ' class="source-parts" role="list">' + ''.join(self.render(child, node, i) for i, child in enumerate(node)) + '</ol>'
        raise ValueError('Unsupported selected CNXML element: ' + name)

    def bridge(self):
        fragment = ET.fromstring(self.translation['bridge_after_html'])
        require(fragment.get('data-origin') == 'original-bridge', 'Original bridge label missing')
        for media_id, target_id in self.correction_ids.items():
            source_alt = next(node.get('alt') for node in self.document.iter() if node.get('id') == media_id)
            number = re.search(r'\d[\d,]*', source_alt)[0]
            candidates = [node for node in fragment.iter('p') if number in ''.join(node.itertext()) and 'انڈونیشی' in ''.join(node.itertext())]
            require(len(candidates) == 1, 'Original correction paragraph is not uniquely discoverable')
            candidates[0].set('id', target_id)
        # Only presentation anchors are added; the translation file remains unchanged.
        return ET.tostring(fragment, encoding='unicode')


class OutputIDs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []

    def handle_starttag(self, name, attrs):
        for key, value in attrs:
            if key == 'id':
                self.ids.append(value)


def build():
    manifest, document, prepared, notices = load_inputs()
    for spec, original, target, data, row in prepared:
        require(target.is_file() and file_hash(target) == spec['sha256'], 'Run prepare_a10.py: reader image missing/changed')
    require(NOTICES.is_file(), 'Run prepare_a10.py: component evidence missing')
    require(json.loads(NOTICES.read_text(encoding='utf-8')) == notice_record(manifest, prepared, notices), 'Retained component record changed')
    translation = json.loads(TRANSLATION.read_text(encoding='utf-8'))
    require((translation['locale'], translation['unit'], translation['module']) == ('pnb-Arab-PK', 'A10-001', 'm82452'), 'Translation locale/scope mismatch')
    target_text = TRANSLATION.read_text(encoding='utf-8')
    require(not re.search('[\u0a00-\u0a7f\u202a-\u202e\u2066-\u2069\u200e\u200f\u061c]', target_text), 'Disallowed script/direction controls')
    reader = Reader(manifest, document, translation)
    body = reader.render(document)
    require(reader.used == list(translation['source_blocks']) and len(reader.used) == 30, 'Changed source-block order/coverage')
    bridge = reader.bridge()
    require(not re.search(r'\{\{[^}]*\}\}', body + bridge), 'Unresolved translation placeholder')
    css = (BASE / 'styles/reader.css').read_text(encoding='utf-8') + LOCAL_CSS
    source_url = manifest['upstream_url'] + '/blob/' + manifest['commit'] + '/' + manifest['path']
    result = f'''<!doctype html>
<html lang="pnb-Arab-PK" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Shahmukhi Punjabi Elementary Algebra 2e; A10-001 bounded translation, not a complete book">
<title>{attr(translation['title'])} — A10-001</title><style>{css}</style></head>
<body class="a10-reader"><header><p class="eyebrow"><bdi dir="ltr">A10-001 · A10 / col31130 / m82452</bdi></p>
<h1>{attr(translation['title'])}</h1><p>{attr(translation['subtitle'])}</p>
<p class="status">ابتدائی ترجمہ · پنجابی دے ماہر تے ریاضی دے استاد دی جانچ ہن تک نہیں ہوئی۔</p>
<nav aria-label="سبق دے حصے"><a href="#{manifest['scope_from']}">ماخذ دا ترجمہ</a> · <a href="#a10-place-value-bridge">لفظاں دی کُنجی تے وضاحت</a> · <a href="#credits">ماخذ تے انتساب</a></nav></header>
<main><p class="source-label">ماخذ: <bdi dir="ltr" lang="en">OpenStax Elementary Algebra 2e</bdi>، باب <bdi dir="ltr" lang="en">Foundations</bdi>، سبق «{attr(manifest['module_title_pnb'])}»۔ ایتھے سبق دا شروع تے پہلے حصے دا چُنیا ہویا ٹکڑا ترجمہ کیتا گیا اے؛ پورا سبق یا پوری کتاب نہیں۔</p>
{body}{bridge}
<p class="status">ایس کتاب دا دیباچہ <bdi dir="ltr">m82630</bdi> تے باب دی جان پہچان <bdi dir="ltr">m82451</bdi> ہن تک ایس ترجمے وچ شامل نہیں۔ پنجاں مقررہ کتاباں دا پورا کم ہن وی جاری اے۔</p></main>
<footer id="credits" lang="en" dir="ltr"><h2>Sources, credits and changes — A10-001</h2>
<p>Adapted from <a href="{attr(source_url)}">OpenStax Elementary Algebra 2e, module m82452: Introduction to Whole Numbers</a>, collection col31130, Foundations. Original senior contributing authors: Lynn Marecek; MaryAnne Anthony-Smith; Andrea Honeycutt Mathis. Source publisher: OpenStax / Rice University.</p>
<p>The existing A10 notice states <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International</a>, subject to component-specific credits and restrictions. This adaptation retains that license framework and those restrictions. See the retained <a href="../provenance/A10-release/NOTICE.txt">A10 release notice</a>, <a href="../provenance/upstream--osbooks-prealgebra-bundle/LICENSE">canonical license text</a>, and <a href="../provenance/a10-unit-001-component-notices.json">selected component evidence</a>. The image authority rows establish source identity, not new image-specific clearance. No new clearance is asserted.</p>
<p>OpenStax and Rice University do not endorse this translation. Their names, logos and marks are not licensed by the source notice. No cover or added logo is reproduced. Original English diagrams are unchanged and unmirrored. Figure labels A10-001.1 and A10-001.2 are local reader labels, not canonical book numbering; the nested solution image is unnumbered.</p>
<p>Changes: Shahmukhi Punjabi translation of the declared 30 text blocks; RTL reader with LTR mathematics, numbers and English; original bilingual keys and explanations labeled separately; source circled parts rendered as (a)–(e), in order. Source IDs, the two spacing-only MathML trees and the three original JPEGs are retained. A paragraph-equivalent container keeps nested solution media in source order. Both source-alt discrepancies are preserved in the source-bound alt translations and disclosed through links to labeled original corrections. No additional practice was added.</p>
<p>Indonesian comparison: <a href="https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id/releases/tag/v1.0.2">Elementary Algebra 2e Indonesian preservation release v1.0.2</a>. Its retained notice describes an 82-module Indonesian release and states its own OpenAI Codex process provenance; that is not a claim that this Punjabi reader covers 82 modules. This Punjabi adaptation was produced with OpenAI Codex assistance at the user's direction; original human-contributor credits remain intact.</p>
<p>Coverage: only m82452's two prelude nodes and the first 13 children of section fs-id1170655083568, through fs-id1170654885628, stopping before fs-id1170655113270. Earlier collection items m82630 and m82451 remain pending. This is not a complete module, complete textbook, or completed five-work assignment, and is not a training or fine-tuning dataset. Native-language, educator and assistive-technology review remain pending. <a href="../source-excerpts/a10-unit-001.cnxml">Frozen source witness</a> · <a href="../source-excerpts/manifest-a10-001.json">Exact source selection</a>.</p>
</footer></body></html>
'''
    parsed = OutputIDs()
    parsed.feed(result)
    require(len(parsed.ids) == len(set(parsed.ids)), 'Duplicate reader ID')
    expected = manifest['source_ids_in_document_order']
    require([sid for sid in parsed.ids if sid in set(expected)] == expected, 'Rendered source ID order changed')
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(result, encoding='utf-8', newline='\n')
    print('Built A10-001: 30 source blocks, 43 source IDs, 2 exact MathML trees, 3 original images; full assignment incomplete.')


if __name__ == '__main__':
    build()
