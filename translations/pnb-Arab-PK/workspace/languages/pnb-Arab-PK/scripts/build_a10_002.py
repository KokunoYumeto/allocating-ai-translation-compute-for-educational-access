"""Deterministic source-bound A10-002 reader; existing builders and CSS are read-only."""
import html
import json
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from build_a10 import Reader as BaseReader, OutputIDs, LOCAL_CSS as BASE_LOCAL_CSS, attr
from prepare_a10_002 import BASE, ROOT, NOTICES, MATH, load_inputs, notice_record, file_hash, require, tag

ET.register_namespace('', MATH)
TRANSLATION = BASE / 'translations/a10-unit-002.json'
OUTPUT = BASE / 'reader/a10-unit-002.html'
BLOCKS = {'figure', 'para', 'note', 'list', 'exercise', 'problem', 'solution', 'section', 'example', 'media', 'table'}
LOCAL_CSS = BASE_LOCAL_CSS + '''
.a10-002-reader .source-table-container { max-width:100%; margin-block:1rem; }
.a10-002-reader .source-table-scroll { max-width:100%; overflow-x:auto; direction:ltr; }
.a10-002-reader .source-table { width:100%; min-width:660px; direction:ltr; table-layout:fixed; }
.a10-002-reader .source-table td { width:50%; white-space:normal; font-family:inherit; direction:rtl; text-align:start; }
.a10-002-reader .source-table .source-media { margin-block:.2rem; }
.a10-002-reader .source-table .source-media img { margin-inline:auto; }
.a10-002-reader .source-stepwise { list-style:decimal; }
.a10-002-reader .source-bulleted { list-style:disc; padding-inline-start:1.7rem; }
.a10-002-reader .figure-label { font-size:1rem; }
'''


class Reader(BaseReader):
    def __init__(self, manifest, document, translation):
        super().__init__(manifest, document, translation)
        self.correction_ids = {}
        for record in translation['source_corrections']:
            for key in record['source_keys']:
                if key.endswith(('/alt', '/summary')):
                    sid = key.split('/')[0]
                    targets = self.correction_ids.setdefault(sid, [])
                    if record['bridge_id'] not in targets:
                        targets.append(record['bridge_id'])
        self.parents = {child: node for node in document.iter() for child in node}

    def translated(self, key, node):
        require(key not in self.used, 'Repeated translation key: ' + key)
        self.used.append(key)
        value = self.blocks[key]
        sources = {
            'math': [child for child in node if tag(child) == 'math'],
            'child': [child for child in node if tag(child) in BLOCKS],
            'link': [child for child in node if tag(child) == 'link']
        }
        for kind, nodes in sources.items():
            positions = [int(index) for index in re.findall(r'\{\{' + kind + r':(\d+)\}\}', value)]
            require(positions == list(range(len(nodes))), 'Changed ' + kind + ' placeholders: ' + key)
        require(value.count('<br>') == sum(tag(child) == 'newline' for child in node), 'Changed newlines: ' + key)
        tokens = [child for child in node if tag(child) == 'span' and child.get('class') == 'token']
        expected_parts = [chr(ord('a') + ord((child.text or '').strip()) - 0x24D0) for child in tokens]
        require(re.findall(r'<bdi\b[^>]*>\(([a-c])\)', value) == expected_parts, 'Changed source parts: ' + key)
        value = re.sub(r'\{\{math:(\d+)\}\}', lambda match: self.math_html(sources['math'][int(match[1])]), value)
        value = re.sub(r'\{\{child:(\d+)\}\}', lambda match: self.render(sources['child'][int(match[1])], node), value)

        def link(match):
            target = sources['link'][int(match[1])].get('target-id')
            require(target in self.figure_labels, 'Unknown source figure target')
            return ('<a href="#' + attr(target) + '" data-source-target="' + attr(target)
                    + '">شکل <bdi dir="ltr">' + attr(self.figure_labels[target]) + '</bdi></a>')
        return re.sub(r'\{\{link:(\d+)\}\}', link, value)

    def advisory(self, sid, overridden=False):
        targets = self.correction_ids.get(sid, [])
        if not targets:
            return ''
        intro = ('پڑھ کے سناؤن والی وضاحت ساڈی ولوں درست کیتی گئی اے؛ ماخذ دا وفادار ترجمہ وکھرا محفوظ اے۔ '
                 if overridden else 'ایس ماخذی بیان دی شرط یا فرق بارے ')
        links = ' · '.join('<a href="#' + attr(target) + '">ساڈی اصل وضاحت ویکھو</a>' for target in targets)
        return '<p class="source-alt-advisory" data-origin="renderer-ui">' + intro + links + '۔</p>'

    def render(self, node, parent=None, index=0):
        name, sid = tag(node), node.get('id')
        ident = ' id="' + attr(sid) + '"' if sid else ''
        marker = ' data-source-tag="' + name + '"'
        if name == 'para':
            mixed = any(tag(child) in BLOCKS for child in node)
            out_tag = 'div' if mixed else 'p'
            value = self.translated(sid, node)
            if not mixed:
                value = self.group_inline_parts(value, node)
            classes = ' class="source-para source-mixed-para"' if mixed else ' class="source-para"'
            return '<' + out_tag + ident + marker + classes + '>' + value + '</' + out_tag + '>'
        if name == 'note':
            note_class = node.get('class', '')
            label = ' aria-label="آپ کر کے ویکھو"' if note_class == 'try' else ''
            content = ''.join(self.render(child, node, i) for i, child in enumerate(node))
            return '<aside' + ident + marker + ' class="source-note source-' + attr(note_class) + '"' + label + '>' + content + '</aside>'
        if name == 'list':
            if node.get('list-type') == 'bulleted':
                out_tag, cls = 'ul', 'source-bulleted'
            else:
                require(node.get('list-type') == 'enumerated', 'Unsupported selected list type')
                out_tag = 'ol'
                cls = 'source-parts' if node.get('class') == 'circled' else 'source-stepwise'
            child_marker = ' data-source-child="' + attr(sid) + '"' if parent is not None and tag(parent) == 'item' else ''
            attrs = (' data-source-list-type="' + attr(node.get('list-type'))
                     + '" data-source-number-style="' + attr(node.get('number-style', '')) + '"')
            return ('<' + out_tag + ident + marker + attrs + child_marker + ' class="' + cls + '" role="list">'
                    + ''.join(self.render(child, node, i) for i, child in enumerate(node)) + '</' + out_tag + '>')
        if name == 'figure':
            label = self.figure_labels[sid]
            heading = '<p class="figure-label" data-origin="renderer-ui">شکل <bdi dir="ltr">' + attr(label) + '</bdi></p>'
            return '<figure' + ident + marker + '>' + heading + ''.join(self.render(child, node, i) for i, child in enumerate(node)) + '</figure>'
        if name == 'media':
            key = sid + '/alt'
            require(key not in self.used, 'Repeated media key')
            self.used.append(key)
            image = next(child for child in node if tag(child) == 'image')
            spec = self.images[image.get('src')]
            require(sid == spec['media_id'] and image.get('mime-type') == spec['declared_mime'], 'Media association/MIME changed')
            overrides = self.translation.get('image_alt_overrides', {})
            alt = overrides.get(sid, self.blocks[key])
            targets = self.correction_ids.get(sid, [])
            require(sid not in overrides or targets, 'Accessible correction lacks original note')
            described = ' aria-describedby="' + attr(' '.join(targets)) + '"' if targets else ''
            trace = (' data-source-alt="' + attr(self.blocks[key]) + '" data-source-image-mime="' + attr(spec['declared_mime'])
                     + '" data-rendered-image-mime="image/jpeg" data-description-origin="'
                     + ('original-correction' if sid in overrides else 'source-translation') + '"')
            src = '../' + spec['path']
            return ('<div class="source-media" data-source-child="' + attr(sid) + '"><div class="figure-scroll" dir="ltr"'
                    + ' tabindex="0" role="region" aria-label="اصل شکل؛ لوڑ پئے تے پاسے سرکاؤ">'
                    + '<img' + ident + marker + ' src="' + attr(src) + '" alt="' + attr(alt) + '" width="' + str(spec['width'])
                    + '" height="' + str(spec['height']) + '" style="--source-width:' + str(spec['width']) + 'px"'
                    + trace + described + '></div><p class="scroll-hint" data-origin="renderer-ui">'
                    + 'چھوٹی سکرین اُتے پوری شکل ویکھن لئی پاسے سرکاؤ، یا <a href="' + attr(src) + '">اصل شکل وکھری کھولو</a>۔</p>'
                    + self.advisory(sid, sid in overrides) + '</div>')
        if name == 'table':
            key = sid + '/summary'
            require(key not in self.used, 'Repeated table summary')
            self.used.append(key)
            group = next(child for child in node if tag(child) == 'tgroup')
            body = next(child for child in group if tag(child) == 'tbody')
            require(not any(tag(child) == 'thead' for child in group), 'Unexpected table header')
            rows = list(body)
            cols = int(group.get('cols'))
            declared = next(spec for spec in self.manifest['renderer_contract']['tables'] if spec['id'] == sid)
            require(len(rows) == declared['rows'] and cols == declared['columns'] == 2, 'Changed table geometry')
            require(all(len(row) == cols and all(tag(cell) == 'entry' for cell in row) for row in rows),
                    'Spanned or malformed cells not supported')
            overrides = self.translation.get('table_summary_overrides', {})
            summary = overrides.get(sid, self.blocks[key])
            targets = self.correction_ids.get(sid, [])
            require(sid not in overrides or targets, 'Table correction lacks original note')
            attributes = (' aria-label="' + attr(summary) + '" data-source-summary="' + attr(self.blocks[key])
                          + '" data-description-origin="' + ('original-correction' if sid in overrides else 'source-translation')
                          + '" data-source-tgroup-cols="' + str(cols) + '" data-source-class="' + attr(node.get('class', '')) + '"')
            if targets:
                attributes += ' aria-describedby="' + attr(' '.join(targets)) + '"'
            labels = [child for child in node if tag(child) == 'label']
            require(all(not list(label) and not (label.text or '').strip() for label in labels), 'Unexpected nonempty table label')
            if labels:
                attributes += ' data-source-empty-label="true"'
            colspecs = [child for child in group if tag(child) == 'colspec']
            column_html = ''
            if colspecs:
                column_html = '<colgroup>' + ''.join(
                    '<col data-source-tag="colspec" data-source-colnum="' + attr(col.get('colnum'))
                    + '" data-source-colname="' + attr(col.get('colname')) + '">' for col in colspecs) + '</colgroup>'
            contents, blank_cells = '', []
            for row_index, row in enumerate(rows, 1):
                cells = ''
                for cell_index, cell in enumerate(row, 1):
                    cell_key = f'{sid}/row/{row_index}/entry/{cell_index}'
                    if not list(cell) and not (cell.text or '').strip():
                        blank_cells.append(f'{row_index}/{cell_index}')
                    cell_value = self.translated(cell_key, cell)
                    cells += ('<td data-source-tag="entry" data-source-key="' + cell_key
                              + '" dir="rtl">' + cell_value + '</td>')
                contents += '<tr data-source-tag="row" data-source-row="' + str(row_index) + '">' + cells + '</tr>'
            require(blank_cells == declared['empty_cells'], 'Changed empty table cells')
            return ('<div class="source-table-container" data-source-child="' + attr(sid) + '">'
                    + self.advisory(sid, sid in overrides)
                    + '<div class="table-scroll source-table-scroll" dir="ltr" tabindex="0" role="region" aria-label="جدول؛ لوڑ پئے تے پاسے سرکاؤ">'
                    + '<table' + ident + marker + attributes + ' dir="ltr" class="source-table">' + column_html
                    + '<tbody data-source-tag="tbody">' + contents + '</tbody></table></div></div>')
        return super().render(node, parent, index)

    def bridge(self):
        fragment = ET.fromstring(self.translation['bridge_after_html'])
        require(fragment.get('data-origin') == 'original-bridge', 'Original bridge label missing')
        ids = {node.get('id') for node in fragment.iter() if node.get('id')}
        for targets in self.correction_ids.values():
            require(set(targets) <= ids, 'Missing original correction destination')
        return self.translation['bridge_after_html']


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []

    def handle_starttag(self, name, attrs):
        for key, value in attrs:
            if key in {'href', 'src'}:
                self.targets.append(value)


def build():
    manifest, document, prepared, notices = load_inputs()
    for spec, original, target, data, row, source_alt in prepared:
        require(target.is_file() and file_hash(target) == spec['sha256'], 'Run prepare_a10_002.py: missing/changed reader image')
    require(NOTICES.is_file() and json.loads(NOTICES.read_text(encoding='utf-8')) == notice_record(manifest, prepared, notices),
            'Run prepare_a10_002.py: component evidence missing/changed')
    target_text = TRANSLATION.read_text(encoding='utf-8')
    translation = json.loads(target_text)
    require((translation['locale'], translation['unit'], translation['module']) == ('pnb-Arab-PK', 'A10-002', 'm82452'),
            'Changed translation scope')
    require(not re.search('[\u0a00-\u0a7f\u202a-\u202e\u2066-\u2069\u200e\u200f\u061c]', target_text),
            'Disallowed script/direction controls')
    require(list(translation['source_blocks']) == manifest['source_block_keys_in_document_order'], 'Changed translation key sequence')
    expected_overrides = manifest['renderer_contract']['accessible_overrides']
    require(list(translation['image_alt_overrides']) == expected_overrides['image_ids']
            and list(translation['table_summary_overrides']) == expected_overrides['table_ids'], 'Changed accessible override scope')
    reader = Reader(manifest, document, translation)
    body, bridge = reader.render(document), reader.bridge()
    require(reader.used == list(translation['source_blocks']) and len(reader.used) == 92, 'Changed source block coverage/order')
    require(not re.search(r'\{\{[^}]*\}\}', body + bridge), 'Unresolved placeholders')
    css = (BASE / 'styles/reader.css').read_text(encoding='utf-8') + LOCAL_CSS
    source_url = manifest['upstream_url'] + '/blob/' + manifest['commit'] + '/' + manifest['path']
    result = f'''<!doctype html>
<html lang="pnb-Arab-PK" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Shahmukhi Punjabi Elementary Algebra 2e; A10-002 bounded translation, not a complete book">
<title>{attr(translation['title'])} — A10-002</title><style>{css}</style></head>
<body class="a10-reader a10-002-reader"><header><p class="eyebrow"><bdi dir="ltr">A10-002 · A10 / col31130 / m82452</bdi></p>
<h1>{attr(translation['title'])}</h1><p>{attr(translation['subtitle'])}</p>
<p class="status">ابتدائی ترجمہ · پنجابی دے ماہر تے ریاضی دے استاد دی جانچ ہن تک نہیں ہوئی۔</p>
<nav aria-label="سبق دے حصے"><a href="a10-unit-001.html">پچھلا حصہ: جگہ دی قدر</a> · <a href="#{manifest['scope_from']}">ماخذ دا ترجمہ</a> · <a href="#a10-002-original-bridge">لفظاں دی کُنجی تے درستیاں</a> · <a href="#credits">ماخذ تے انتساب</a></nav></header>
<main><p class="source-label">ماخذ: <bdi dir="ltr" lang="en">OpenStax Elementary Algebra 2e</bdi>، باب <bdi dir="ltr" lang="en">Foundations</bdi>، سبق «{attr(manifest['module_title_pnb'])}»۔ ایتھے پہلے سیکشن دا باقی حصہ ترجمہ کیتا گیا اے؛ پورا سبق یا پوری کتاب نہیں۔</p>
{body}{bridge}
<p class="status">ایس سبق دا اگلا ماخذی پیراگراف متغیرات بارے اے؛ اوہ ایس حصے وچ شامل نہیں۔ پنجاں مقررہ کتاباں دا پورا کم ہن وی جاری اے۔</p></main>
<footer id="credits" lang="en" dir="ltr"><h2>Sources, credits and changes — A10-002</h2>
<p>Adapted from <a href="{attr(source_url)}">OpenStax Elementary Algebra 2e, module m82452: Introduction to Whole Numbers</a>, collection col31130, Foundations. Original senior contributing authors: Lynn Marecek; MaryAnne Anthony-Smith; Andrea Honeycutt Mathis. Source publisher: OpenStax / Rice University.</p>
<p>The existing A10 notice states <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International</a>, subject to component-specific credits and restrictions. This adaptation retains that license framework and those restrictions. See the retained <a href="../provenance/A10-release/NOTICE.txt">A10 release notice</a>, <a href="../provenance/upstream--osbooks-prealgebra-bundle/LICENSE">canonical license text</a>, and <a href="../provenance/a10-unit-002-component-notices.json">selected component evidence</a>. Media authority rows establish source identity, not new image-specific clearance. No new clearance is asserted.</p>
<p>OpenStax and Rice University do not endorse this translation. Their names, logos and marks are not licensed by the source notice. No cover or added logo is reproduced. All fourteen original English JPEG images are unchanged and unmirrored. Figure label A10-002.1 is local reader numbering, not canonical book numbering; thirteen other media elements remain unnumbered. Four incorrect source PNG MIME declarations remain in the witness and metadata while original JPEG files are served.</p>
<p>Changes: Shahmukhi Punjabi translation of 92 declared source blocks/scaffolds; RTL prose with LTR mathematics, numbers, English and original diagram/table geometry; seven newlines, eighteen ordered (a)–(c) source part labels, three tables including their blank cells, and fourteen exact source MathML trees retained. Six explicitly original image-alt corrections and three table-summary corrections are announced accessibly; their faithful source translations remain in data-source-alt/data-source-summary attributes. Visible advisories and aria-describedby link to original correction notes. Source-bound wording is not silently repaired. Original bilingual keys and explanations are labeled separately. No additional practice was added.</p>
<p>Indonesian comparison: <a href="https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id/releases/tag/v1.0.2">Elementary Algebra 2e Indonesian preservation release v1.0.2</a>. Its 82-module release and OpenAI Codex process provenance do not imply equivalent Punjabi coverage. This Punjabi adaptation was produced with OpenAI Codex assistance at the user's direction; original human-contributor credits remain intact.</p>
<p>Coverage: section fs-id1170655083568 children 13–32 (zero-based, counting the original title), from fs-id1170655113270 through fs-id1170655197222; stop before standalone paragraph newelem_para01. This unit does not cover earlier collection items m82630 and m82451. This is not a complete module, complete textbook, or completed five-work assignment, and is not a training or fine-tuning dataset. Native-language, educator and assistive-technology review remain pending. <a href="../source-excerpts/a10-unit-002.cnxml">Frozen source witness</a> · <a href="../source-excerpts/manifest-a10-002.json">Exact source selection</a>.</p>
</footer></body></html>
'''
    ids = OutputIDs()
    ids.feed(result)
    require(len(ids.ids) == len(set(ids.ids)), 'Duplicate reader IDs')
    expected = manifest['source_ids_in_document_order']
    require([sid for sid in ids.ids if sid in set(expected)] == expected, 'Changed rendered source ID order')
    links = Links()
    links.feed(result)
    for target in links.targets:
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc:
            continue
        if parsed.path:
            path = (OUTPUT.parent / unquote(parsed.path)).resolve()
            require(path.is_relative_to(BASE.resolve()) and path.is_file(), 'Missing or unsafe local target: ' + target)
        else:
            require(parsed.fragment in ids.ids, 'Missing local fragment: ' + target)
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(result, encoding='utf-8', newline='\n')
    print('Built A10-002: 92 source blocks, 108 IDs, 14 exact MathML trees, 3 tables, 14 original JPEGs; full assignment incomplete.')


if __name__ == '__main__':
    build()
