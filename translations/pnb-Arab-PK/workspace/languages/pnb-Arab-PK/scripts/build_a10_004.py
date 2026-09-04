"""Source-bound A10-004 reader; earlier builders, CSS and inputs are read-only."""
import json
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from build_a10 import Reader as BaseReader, OutputIDs, LOCAL_CSS as BASE_LOCAL_CSS, attr
from prepare_a10_004 import BASE, ROOT, NOTICES, MATH, load_inputs, notice_record, file_hash, require, tag

ET.register_namespace('', MATH)
TRANSLATION = BASE / 'translations/a10-unit-004.json'
OUTPUT = BASE / 'reader/a10-unit-004.html'
BLOCKS = {'figure', 'para', 'note', 'list', 'exercise', 'problem', 'solution', 'section', 'example', 'media', 'table'}
LOCAL_CSS = BASE_LOCAL_CSS + '''
.a10-004-reader .source-table-container { min-width:0; max-width:100%; margin-block:1rem; }
.a10-004-reader .source-table-scroll { direction:ltr; overflow-x:auto; max-width:100%; }
.a10-004-reader .source-table { width:660px; min-width:660px; table-layout:fixed; border-collapse:collapse; }
.a10-004-reader .source-table td { width:50%; padding:.5rem; vertical-align:top; text-align:start; overflow-wrap:anywhere; }
.a10-004-reader .source-table td[dir=ltr] { text-align:left; }
.a10-004-reader .source-table .source-media { margin-block:.25rem; }
.a10-004-reader .source-media .scroll-hint { direction:rtl; white-space:normal; text-align:start; }
.a10-004-reader .source-enumerated { list-style-type:decimal; padding-inline-start:2rem; }
.a10-004-reader .source-bulleted { list-style-type:disc; padding-inline-start:1.7rem; }
.a10-004-reader .source-open-circle { list-style-type:circle; }
.a10-004-reader .source-resource-list { list-style:none; padding-inline-start:0; }
.a10-004-reader li { margin-block:.3rem; }
.a10-004-reader .source-original-advisory { font-size:.9rem; border-inline-start:3px solid #b98238; padding-inline-start:.7rem; }
.a10-004-reader .source-block-container { min-width:0; max-width:100%; }
.a10-004-reader .source-figure-label { text-align:center; font-size:.9rem; }
'''


class Reader(BaseReader):
    def __init__(self, manifest, document, translation):
        super().__init__(manifest, document, translation)
        self.references = {(r['source_key'], r['link_index']): r for r in manifest['references']}
        self.advisories = {}
        for record in translation['source_corrections']:
            for key in record['source_keys']:
                require(key in self.blocks, 'Unknown correction source key: ' + key)
                self.advisories.setdefault(key, []).append(record)
        self.direct_notes = set(manifest['renderer_contract']['direct_text_note_keys'])

    def described(self, key):
        targets = list(dict.fromkeys(r['bridge_id'] for r in self.advisories.get(key, [])))
        return ' aria-describedby="' + attr(' '.join(targets)) + '"' if targets else ''

    def advisory(self, key):
        records = self.advisories.get(key, [])
        if not records:
            return ''
        links = '؛ '.join('<a href="#' + attr(r['bridge_id']) + '" data-correction-id="' + attr(r['id'])
                         + '">ساڈی وکھری درستی تے وضاحت</a>' for r in records)
        return ('<p class="source-original-advisory" data-origin="renderer-ui" data-source-advisory-for="'
                + attr(key) + '">ایس ماخذی گل نال ' + links + ' وی پڑھو۔</p>')

    def translated(self, key, node):
        require(key not in self.used, 'Repeated translation key: ' + key)
        self.used.append(key)
        value = self.blocks[key]
        sources = {
            'math': [c for c in node if tag(c) == 'math'],
            'child': [c for c in node if tag(c) in BLOCKS],
            'link': [c for c in node if tag(c) == 'link']
        }
        for kind, children in sources.items():
            indices = [int(i) for i in re.findall(r'\{\{' + kind + r':(\d+)\}\}', value)]
            require(indices == list(range(len(children))), 'Changed ' + kind + ' placeholders: ' + key)
        require(len(re.findall(r'<br\s*/?>', value)) == sum(tag(c) == 'newline' for c in node),
                'Changed source newline count: ' + key)
        require(not any(tag(c) == 'span' and c.get('class') == 'token' for c in node),
                'Unexpected circled source part')
        value = re.sub(r'\{\{math:(\d+)\}\}', lambda m: self.math_html(sources['math'][int(m[1])]), value)
        value = re.sub(r'\{\{child:(\d+)\}\}', lambda m: self.render(sources['child'][int(m[1])], node), value)

        def link(match):
            index = int(match[1])
            node = sources['link'][index]
            spec = self.references[(key, index)]
            source_value = node.get('target-id') or node.get('url')
            require(source_value == spec['id'], 'Changed source reference association')
            label = self.translation['source_link_labels'][key + '/link/' + str(index)]
            metadata = (' data-source-url="' + attr(source_value) + '"' if node.get('url')
                        else ' data-source-target="' + attr(source_value) + '"')
            if node.get('url'):
                require(spec['kind'] == 'external' and spec['href'] == source_value, 'Changed historical URL')
            return ('<a href="' + attr(spec['href']) + '" data-source-link-owner="' + attr(key)
                    + '" data-source-link-index="' + str(index) + '"' + metadata + '>' + label + '</a>')
        return re.sub(r'\{\{link:(\d+)\}\}', link, value)

    def children(self, node):
        require(not (node.text or '').strip(), 'Untranslated direct container text: ' + str(node.get('id')))
        result = node.text or ''
        for index, child in enumerate(node):
            result += self.render(child, node, index)
            require(not (child.tail or '').strip(), 'Untranslated container tail: ' + str(child.get('id')))
            result += child.tail or ''
        return result

    def render(self, node, parent=None, index=0):
        name, sid = tag(node), node.get('id')
        ident = ' id="' + attr(sid) + '"' if sid else ''
        marker = ' data-source-tag="' + name + '"'
        if name == 'document':
            return self.children(node)
        if name == 'section':
            return ('<section' + ident + marker + ' class="translated" data-source-class="'
                    + attr(node.get('class', '')) + '">' + self.children(node) + '</section>')
        if name in {'example', 'exercise', 'problem', 'solution'}:
            out_tag = 'section' if name in {'example', 'solution'} else 'div'
            heading = ''
            if name == 'example':
                label = self.manifest['renderer_contract']['example_labels'][sid]
                heading = ('<h2 class="example-label" data-origin="renderer-ui">حل کیتی مثال <bdi dir="ltr">'
                           + attr(label) + '</bdi></h2>')
            # Explicit source Solution titles are not duplicated by a generated heading.
            label = ' aria-label="حل"' if name == 'solution' and not any(tag(c) == 'title' for c in node) else ''
            return ('<' + out_tag + ident + marker + ' class="source-' + name + '"' + label + '>'
                    + heading + self.children(node) + '</' + out_tag + '>')
        if name in {'para', 'title', 'item'}:
            key = (parent.get('id') + '/item/' + str(index + 1) if name == 'item'
                   else sid or parent.get('id') + '/' + name)
            mixed = name == 'para' and any(tag(c) in BLOCKS for c in node)
            out_tag = 'div' if mixed else {'para': 'p', 'title': 'h2' if tag(parent) == 'section' else 'h3', 'item': 'li'}[name]
            classes = ' class="source-para source-mixed-para"' if mixed else ' class="source-para"' if name == 'para' else ''
            value = self.translated(key, node)
            # A list item can contain a marked advisory paragraph after its source content.
            inside_advisory = self.advisory(key) if name == 'item' else ''
            result = ('<' + out_tag + ident + marker + ' data-source-key="' + attr(key) + '"'
                      + classes + self.described(key) + '>' + value + inside_advisory + '</' + out_tag + '>')
            if name != 'item' and key in self.advisories:
                return ('<div class="source-block-container" data-source-block-owner="' + attr(key) + '">'
                        + result + self.advisory(key) + '</div>')
            return result
        if name == 'note':
            note_class = node.get('class', '')
            if sid in self.direct_notes:
                require(not len(node), 'Direct-text note acquired children')
                content = ('<p class="source-note-text" data-source-key="' + attr(sid) + '">'
                           + self.translated(sid, node) + '</p>')
            else:
                content = self.children(node)
            label = ' aria-label="آپ کر کے ویکھو"' if note_class == 'try' else ''
            return ('<aside' + ident + marker + ' class="source-note source-' + attr(note_class)
                    + '" data-source-class="' + attr(note_class) + '"' + label + '>' + content + '</aside>')
        if name == 'list':
            kind, bullet = node.get('list-type', ''), node.get('bullet-style', '')
            require(kind in {'enumerated', 'bulleted', ''}, 'Unsupported source list type')
            require(set(node.attrib) <= {'id', 'list-type', 'number-style', 'bullet-style', 'display', 'class'},
                    'Unexpected list attributes')
            if kind == 'enumerated':
                require(node.get('number-style') == 'arabic', 'Unsupported list number style')
                out_tag, classes = 'ol', 'source-enumerated'
            elif kind == 'bulleted':
                require(bullet in {'bullet', 'open-circle'}, 'Unsupported source bullet')
                out_tag = 'ul'
                classes = 'source-bulleted' + (' source-open-circle' if bullet == 'open-circle' else '')
            else:
                require(node.get('display') == 'block' and sid == 'fs-id1170655222071', 'Unknown default list')
                out_tag, classes = 'ul', 'source-resource-list'
            metadata = ''.join(' data-source-' + k + '="' + attr(node.get(k, '')) + '"'
                               for k in ('list-type', 'number-style', 'bullet-style', 'display', 'class'))
            return ('<' + out_tag + ident + marker + metadata + ' class="' + classes + '" role="list">'
                    + self.children(node) + '</' + out_tag + '>')
        if name == 'figure':
            label = self.figure_labels[sid]
            return ('<figure' + ident + marker + '>' + self.children(node)
                    + '<figcaption class="source-figure-label" data-origin="renderer-ui">شکل <bdi dir="ltr">'
                    + attr(label) + '</bdi></figcaption></figure>')
        if name == 'media':
            key = sid + '/alt'
            require(key not in self.used, 'Repeated image alt')
            self.used.append(key)
            require(len(node) == 1 and tag(node[0]) == 'image', 'Unexpected source media structure')
            image = node[0]
            spec = self.images[image.get('src')]
            require(sid == spec['media_id'] and image.get('mime-type') == spec['declared_mime'],
                    'Image association or source MIME changed')
            faithful = self.blocks[key]
            override = self.translation['image_alt_overrides'].get(sid)
            require(not override or key in self.advisories, 'Override lacks visible correction')
            origin = 'original-correction' if override else 'source-translation'
            src = '../' + spec['path']
            return ('<div class="source-media" data-source-child="' + attr(sid) + '">'
                    + '<div class="figure-scroll" dir="ltr" tabindex="0" role="region" aria-label="اصل شکل؛ لوڑ پئے تے پاسے سرکاؤ">'
                    + '<img' + ident + marker + ' src="' + attr(src) + '" alt="' + attr(override or faithful)
                    + '" data-source-alt="' + attr(faithful) + '" data-description-origin="' + origin
                    + '" data-source-image-mime="' + attr(spec['declared_mime'])
                    + '" data-rendered-image-mime="image/jpeg" width="' + str(spec['width']) + '" height="'
                    + str(spec['height']) + '" style="--source-width:' + str(spec['width']) + 'px"' + self.described(key) + '>'
                    + '</div><p class="scroll-hint" data-origin="renderer-ui" dir="rtl">چھوٹی سکرین اُتے پوری شکل ویکھن لئی پاسے سرکاؤ، یا '
                    + '<a href="' + attr(src) + '">اصل شکل وکھری کھولو</a>۔</p>' + self.advisory(key) + '</div>')
        if name == 'table':
            return self.table(node)
        raise ValueError('Unsupported selected source element: ' + name)

    def table(self, node):
        sid = node.get('id')
        key = sid + '/summary'
        require(key not in self.used, 'Repeated table summary')
        self.used.append(key)
        spec = next(x for x in self.manifest['tables'] if x['id'] == sid)
        require([tag(c) for c in node] == ['label', 'tgroup'] and not len(node[0])
                and not (node[0].text or '').strip(), 'Changed empty source table label')
        group = node[1]
        require(group.attrib == {'cols': '2'} and len(group) == 1 and tag(group[0]) == 'tbody',
                'Changed two-column source table structure')
        rows, empty_cells, cell_advisories = [], [], []
        for ri, row in enumerate(group[0], 1):
            require(tag(row) == 'row' and not row.attrib and len(row) == 2, 'Changed source row')
            cells = []
            for ci, cell in enumerate(row, 1):
                require(tag(cell) == 'entry' and not cell.attrib, 'Unexpected source cell attributes')
                cell_key = f'{sid}/row/{ri}/entry/{ci}'
                if not len(cell) and not (cell.text or '').strip():
                    empty_cells.append({'row': ri, 'entry': ci})
                image_or_math_only = (len(cell) and not (cell.text or '').strip()
                                      and all(tag(c) in {'media', 'math'} and not (c.tail or '').strip() for c in cell))
                direction = 'ltr' if image_or_math_only else 'rtl'
                cells.append('<td data-source-tag="entry" data-source-key="' + attr(cell_key)
                             + '" dir="' + direction + '"' + self.described(cell_key) + '>'
                             + self.translated(cell_key, cell) + '</td>')
                if cell_key in self.advisories:
                    cell_advisories.append(self.advisory(cell_key))
            # Source structural whitespace is retained, not treated as new prose.
            rows.append('<tr data-source-tag="row" data-source-row="' + str(ri) + '">'
                        + (row.text or '') + ''.join(cell_html + (cell.tail or '') for cell_html, cell in zip(cells, row)) + '</tr>')
        require(len(rows) == spec['rows'] and len(rows) * 2 == spec['cells']
                and empty_cells == spec['empty_cells'], 'Changed table geometry or blank cell')
        body = '<tbody data-source-tag="tbody">' + (group[0].text or '')
        body += ''.join(html + (row.tail or '') for html, row in zip(rows, group[0])) + '</tbody>'
        faithful = self.blocks[key]
        override = self.translation['table_summary_overrides'].get(sid)
        require(not override or key in self.advisories, 'Table override lacks correction')
        origin = 'original-correction' if override else 'source-translation'
        attrs = (' id="' + attr(sid) + '" data-source-tag="table" data-source-summary-attribute="aria-label"'
                 + ' aria-label="' + attr(override or faithful) + '" data-source-summary="' + attr(faithful)
                 + '" data-description-origin="' + origin + '" data-source-tgroup-cols="2" data-source-label-empty="true"'
                 + ' data-source-class="' + attr(node.get('class', '')) + '"' + self.described(key))
        return ('<div class="source-table-container" data-source-child="' + attr(sid) + '">'
                + '<div class="table-scroll source-table-scroll" dir="ltr" tabindex="0" role="region" aria-label="جدول؛ لوڑ پئے تے پاسے سرکاؤ">'
                + '<table' + attrs + ' dir="ltr" class="source-table source-worked-table">' + body + '</table></div>'
                + '<p class="scroll-hint" data-origin="renderer-ui">سارے کالم ویکھن لئی لوڑ پئے تے جدول نوں پاسے سرکاؤ۔</p>'
                + self.advisory(key) + ''.join(cell_advisories) + '</div>')

    def bridge(self):
        raw = self.translation['bridge_after_html']
        fragment = ET.fromstring(raw)
        require(fragment.tag == 'section' and fragment.get('id') == 'a10-004-original-bridge'
                and fragment.get('class') == 'original-bridge', 'Unlabeled original bridge')
        ids = [n.get('id') for n in fragment.iter() if n.get('id')]
        require(len(ids) == len(set(ids)) and all(r['bridge_id'] in ids for r in self.translation['source_corrections']),
                'Missing or duplicate original correction targets')
        require(raw.startswith('<section '), 'Unexpected bridge syntax')
        return raw.replace('<section ', '<section data-origin="original-bridge" ', 1)


class LocalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []

    def handle_starttag(self, name, attrs):
        self.targets.extend(value for key, value in attrs if key in {'href', 'src'})


def build():
    manifest, document, prepared, notices = load_inputs()
    for spec, original, target, data, row, source_alt in prepared:
        require(target.is_file() and file_hash(target) == spec['sha256'], 'Run prepare_a10_004.py: asset missing/changed')
    require(NOTICES.is_file() and json.loads(NOTICES.read_text(encoding='utf-8')) == notice_record(manifest, prepared, notices),
            'Run prepare_a10_004.py: retained component evidence missing/changed')
    raw = TRANSLATION.read_text(encoding='utf-8')
    translation = json.loads(raw)
    require((translation['locale'], translation['unit'], translation['module']) == ('pnb-Arab-PK', 'A10-004', 'm82452'),
            'Unexpected translation scope')
    require(not re.search('[\u0a00-\u0a7f\u202a-\u202e\u2066-\u2069\u200e\u200f\u061c\ufffd]', raw),
            'Disallowed script or bidi controls')
    require(list(translation['source_blocks']) == manifest['source_block_keys_in_document_order'], 'Changed key order')
    require(translation['source_corrections'] == manifest['source_discrepancies'], 'Changed correction contract')
    require(translation['source_link_labels'] == manifest['renderer_contract']['source_link_labels'], 'Changed link labels')
    for field, spec in [('image_alt_overrides', 'image_ids'), ('table_summary_overrides', 'table_ids')]:
        require(list(translation[field]) == manifest['renderer_contract']['accessible_overrides'][spec], 'Changed overrides')
    reader = Reader(manifest, document, translation)
    source_body, bridge = reader.render(document), reader.bridge()
    require(reader.used == list(translation['source_blocks']) and len(reader.used) == 150, 'Changed source coverage/order')
    require(not re.search(r'\{\{[^}]+\}\}', source_body + bridge), 'Unresolved placeholder')
    css = (BASE / 'styles/reader.css').read_text(encoding='utf-8') + LOCAL_CSS
    source_url = manifest['upstream_url'] + '/blob/' + manifest['commit'] + '/' + manifest['path']
    result = f'''<!doctype html>
<html lang="pnb-Arab-PK" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Shahmukhi Punjabi Elementary Algebra 2e; A10-004 instruction and review, exercises required next; not a complete book">
<title>{attr(translation['title'])} — A10-004</title><style>{css}</style></head>
<body class="a10-reader a10-004-reader"><header><p class="eyebrow"><bdi dir="ltr">A10-004 · A10 / col31130 / m82452</bdi></p>
<h1>{attr(translation['title'])}</h1><p>{attr(translation['subtitle'])}</p>
<p class="status">ابتدائی ترجمہ · پنجابی دے ماہر تے ریاضی دے استاد دی جانچ ہن تک نہیں ہوئی۔</p>
<nav aria-label="سبق دے حصے"><a href="a10-unit-003.html">پچھلا حصہ: مضاعف تے پورا ونڈے جان دی پرکھ</a> · <a href="#{manifest['scope_from']}">ماخذ دا ترجمہ</a> · <a href="#a10-004-original-bridge">لفظاں دی کُنجی تے وضاحت</a> · <a href="#credits">ماخذ تے انتساب</a></nav></header>
<main><p class="source-label" data-origin="renderer-ui">ماخذ: <bdi dir="ltr" lang="en">OpenStax Elementary Algebra 2e</bdi>، باب <bdi dir="ltr" lang="en">Foundations</bdi>، سبق «{attr(manifest['module_title_pnb'])}»۔ ایتھے اوّلی اجزا تے سانجھے مضاعفاں والا پورا سیکشن تے اوہدے نال اہم خیالاں دی دہرائی ترجمہ کیتی گئی اے؛ پورا سبق یا پوری کتاب نہیں۔</p>
{source_body}{bridge}
<p class="status" data-origin="renderer-ui">اگلا ضروری کم ایس سبق دیاں مشقاں دا ماخذی حصہ اے؛ اوہ ایتھے شامل نہیں۔ پنجاں مقررہ کتاباں دا پورا کم ہن وی جاری اے۔</p></main>
<footer id="credits" lang="en" dir="ltr"><h2>Sources, credits and changes — A10-004</h2>
<p>Adapted from <a href="{attr(source_url)}">OpenStax Elementary Algebra 2e, module m82452: Introduction to Whole Numbers</a>, collection col31130, Foundations. Original senior contributing authors: Lynn Marecek; MaryAnne Anthony-Smith; Andrea Honeycutt Mathis. Source publisher: OpenStax / Rice University.</p>
<p>The existing A10 notice states <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International</a>, subject to component-specific credits and restrictions. This adaptation retains that license framework and those restrictions. See the retained <a href="../provenance/A10-release/NOTICE.txt">A10 release notice</a>, <a href="../provenance/upstream--osbooks-prealgebra-bundle/LICENSE">canonical license text</a>, and <a href="../provenance/a10-unit-004-component-notices.json">selected component evidence</a>. Media authority rows establish identity, not new image-specific clearance. No new clearance is asserted.</p>
<p>OpenStax and Rice University do not endorse this translation. Their names, logos and marks are not licensed by the source notice. No cover or added logo is reproduced. All fifteen original JPEGs are unchanged and unmirrored; four source PNG MIME declarations are retained as metadata despite actual JPEG bytes. Figure A10-004.1 is a local reader label, not canonical book numbering; other media and all three source tables remain unnumbered. The source place-value reference reaches the earlier reader figure A10-001.2.</p>
<p>Changes: Shahmukhi Punjabi translation of 150 source text/cell scaffolds; RTL prose with LTR mathematics, numbers, English and original geometry. All 168 source IDs, fifteen exact MathML trees including source punctuation and English and, six explicit source newlines, twelve term IDs, thirteen lists with forty-eight items, three tables with fourteen data cells including one empty cell, and all fifteen source images are retained. Five explicit Solution titles appear once. Nested lists/media remain in their source owners. The original English plural suffix s is expressed by Punjabi morphology; the prime-number plural term is bolded as a whole. Four evidence-resolved image descriptions and two table summaries use separately labeled original accessible overrides, with faithful translated source descriptions preserved in data attributes. Visible source-key-bound advisories lead to original corrections and scope qualifications. No source formula, cell data or image was silently repaired, and no extra practice was added.</p>
<p>The original Java-enablement instruction is retained as historical source wording with an adjacent original warning, not an instruction from this adaptation to enable or install obsolete plugins or run an external application. The original source URL is retained; its current functionality was not established. No external Java/runtime was executed. The original bridge separately cites Oracle's browser-specific Java help.</p>
<p>Indonesian comparison: <a href="https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id/releases/tag/v1.0.2">Elementary Algebra 2e Indonesian preservation release v1.0.2</a>. Its 82-module release and OpenAI Codex process provenance do not imply equivalent Punjabi coverage. This adaptation was produced with OpenAI Codex assistance at the user's direction; original human-contributor credits remain intact.</p>
<p>Coverage: complete section fs-id1170655247410 followed by complete Key Concepts section fs-id1170655222085, ending with list fs-id1166421706953. Stop before fs-id1170655190123, Section Exercises, which is required next and not translated here. Earlier collection modules m82630 and m82451 have separate checkpoints. This is not a complete module, complete textbook or completed five-work assignment, and is not training or fine-tuning data. Native-language, educator and assistive-technology review remain pending. <a href="../source-excerpts/a10-unit-004.cnxml">Frozen source witness</a> · <a href="../source-excerpts/manifest-a10-004.json">Exact source selection</a>.</p>
</footer></body></html>
'''
    ids = OutputIDs()
    ids.feed(result)
    require(len(ids.ids) == len(set(ids.ids)), 'Duplicate output ID')
    expected = manifest['source_ids_in_document_order']
    require([sid for sid in ids.ids if sid in set(expected)] == expected, 'Changed rendered source ID order')
    links = LocalLinks()
    links.feed(result)
    for target in links.targets:
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc:
            require(parsed.scheme in {'http', 'https'}, 'Non-web external link')
            continue
        if parsed.path:
            path = (OUTPUT.parent / unquote(parsed.path)).resolve()
            require(path.is_relative_to(BASE.resolve()) and path.is_file(), 'Missing/unsafe local path: ' + target)
            if parsed.fragment:
                page_ids = OutputIDs()
                page_ids.feed(path.read_text(encoding='utf-8'))
                require(unquote(parsed.fragment) in page_ids.ids, 'Missing cross-unit fragment: ' + target)
        else:
            require(unquote(parsed.fragment) in ids.ids, 'Missing local fragment: ' + target)
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(result, encoding='utf-8', newline='\n')
    print('Built A10-004:150source blocks,168IDs,15exactMathML,3tables/14cells,15originalJPEGs; exercises required next.')


if __name__ == '__main__':
    build()
