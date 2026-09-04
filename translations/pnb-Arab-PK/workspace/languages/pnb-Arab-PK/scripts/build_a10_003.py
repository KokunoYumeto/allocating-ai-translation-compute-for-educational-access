"""Deterministic A10-003 reader; frozen inputs and earlier builders remain read-only."""
import json
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from build_a10 import Reader as BaseReader, OutputIDs, LOCAL_CSS as BASE_LOCAL_CSS, attr
from prepare_a10_003 import BASE, ROOT, NOTICES, MATH, load_inputs, notice_record, file_hash, require, tag

ET.register_namespace('', MATH)
TRANSLATION = BASE / 'translations/a10-unit-003.json'
OUTPUT = BASE / 'reader/a10-unit-003.html'
BLOCKS = {'figure', 'para', 'note', 'list', 'exercise', 'problem', 'solution', 'section', 'example', 'media', 'table'}
LOCAL_CSS = BASE_LOCAL_CSS + '''
.a10-003-reader .source-table-container { max-width:100%; margin-block:1rem; }
.a10-003-reader .source-table-scroll { max-width:100%; overflow-x:auto; direction:ltr; }
.a10-003-reader .source-table { direction:ltr; table-layout:fixed; }
.a10-003-reader .source-table th, .a10-003-reader .source-table td { min-width:0; font-family:inherit; white-space:normal; }
.a10-003-reader .source-grid { width:100%; min-width:820px; }
.a10-003-reader .source-grid col:first-child { width:170px; }
.a10-003-reader .source-grid td, .a10-003-reader .source-grid th[scope="col"]:not(:first-child) { text-align:left; }
.a10-003-reader .source-grid th, .a10-003-reader .source-grid td { vertical-align:middle; }
.a10-003-reader .source-grid th:first-child { text-align:start; }
.a10-003-reader .source-worked-table { width:100%; min-width:660px; }
.a10-003-reader .source-worked-table td { width:50%; direction:rtl; text-align:start; }
.a10-003-reader .source-bulleted { list-style:disc; padding-inline-start:1.7rem; }
.a10-003-reader .source-table-label { font-size:1rem; margin-block:.25rem; }
.a10-003-reader .original-bridge { border-block-start:2px solid #cad7d1; margin-block-start:2rem; padding-block-start:.5rem; }
'''


class Reader(BaseReader):
    def __init__(self, manifest, document, translation):
        super().__init__(manifest, document, translation)
        self.correction_ids = {}
        self.table_labels = manifest['renderer_contract']['source_link_labels']

    def translated(self, key, node):
        require(key not in self.used, 'Repeated translation key: ' + key)
        require(key in self.blocks, 'Missing translation key: ' + key)
        self.used.append(key)
        value = self.blocks[key]
        sources = {
            'math': [child for child in node if tag(child) == 'math'],
            'child': [child for child in node if tag(child) in BLOCKS],
            'link': [child for child in node if tag(child) == 'link']
        }
        for kind, children in sources.items():
            indices = [int(index) for index in re.findall(r'\{\{' + kind + r':(\d+)\}\}', value)]
            require(indices == list(range(len(children))), 'Changed ' + kind + ' placeholders: ' + key)
        require(not sources['child'], 'Unexpected mixed structural child in A10-003')
        require(value.count('<br>') == sum(tag(child) == 'newline' for child in node), 'Changed newline: ' + key)
        require(not any(tag(child) == 'span' and child.get('class') == 'token' for child in node),
                'Unexpected circled part token')
        value = re.sub(r'\{\{math:(\d+)\}\}', lambda match: self.math_html(sources['math'][int(match[1])]), value)

        def link(match):
            target = sources['link'][int(match[1])].get('target-id')
            require(target in self.table_labels, 'Unknown source table link')
            return ('<a href="#' + attr(target) + '" data-source-target="' + attr(target)
                    + '">جدول <bdi dir="ltr">' + attr(self.table_labels[target]) + '</bdi></a>')
        return re.sub(r'\{\{link:(\d+)\}\}', link, value)

    def render(self, node, parent=None, index=0):
        name, sid = tag(node), node.get('id')
        ident = ' id="' + attr(sid) + '"' if sid else ''
        marker = ' data-source-tag="' + name + '"'
        if name in {'para', 'title', 'item'}:
            key = (parent.get('id') + '/item/' + str(index + 1) if name == 'item'
                   else sid or parent.get('id') + '/' + name)
            out_tag = {'para': 'p', 'title': 'h2' if tag(parent) == 'section' else 'h3', 'item': 'li'}[name]
            classes = ' class="source-para"' if name == 'para' else ''
            return ('<' + out_tag + ident + marker + ' data-source-key="' + attr(key) + '"' + classes
                    + '>' + self.translated(key, node) + '</' + out_tag + '>')
        if name == 'note':
            note_class = node.get('class', '')
            if sid in self.manifest['renderer_contract']['direct_text_note_keys']:
                require(not len(node), 'Direct-text activity acquired children')
                content = ('<p class="source-note-text" data-source-key="' + attr(sid) + '">'
                           + self.translated(sid, node) + '</p>')
            else:
                require(not (node.text or '').strip(), 'Untranslated direct note text')
                content = ''.join(self.render(child, node, i) for i, child in enumerate(node))
            label = ' aria-label="آپ کر کے ویکھو"' if note_class == 'try' else ''
            return '<aside' + ident + marker + ' class="source-note source-' + attr(note_class) + '"' + label + '>' + content + '</aside>'
        if name == 'list':
            require(node.get('list-type') == 'bulleted' and node.get('bullet-style') == 'bullet',
                    'Unexpected source list type')
            return ('<ul' + ident + marker + ' data-source-list-type="bulleted" data-source-bullet-style="bullet"'
                    + ' class="source-bulleted" role="list">'
                    + ''.join(self.render(child, node, i) for i, child in enumerate(node)) + '</ul>')
        if name == 'media':
            key = sid + '/alt'
            require(key not in self.used, 'Repeated image alt')
            self.used.append(key)
            require(len(node) == 1 and tag(node[0]) == 'image', 'Unexpected source media contents')
            source_image = node[0]
            spec = self.images[source_image.get('src')]
            require(sid == spec['media_id'] and source_image.get('mime-type') == spec['declared_mime']
                    == 'image/jpeg', 'Image association/MIME mismatch')
            src = '../' + spec['path']
            return ('<div class="source-media" data-source-child="' + attr(sid) + '">'
                    + '<div class="figure-scroll" dir="ltr" tabindex="0" role="region" aria-label="اصل شکل؛ لوڑ پئے تے پاسے سرکاؤ">'
                    + '<img' + ident + marker + ' src="' + attr(src) + '" alt="' + attr(self.blocks[key])
                    + '" data-source-alt="' + attr(self.blocks[key]) + '" data-description-origin="source-translation"'
                    + ' data-source-image-mime="image/jpeg" data-rendered-image-mime="image/jpeg" width="' + str(spec['width'])
                    + '" height="' + str(spec['height']) + '" style="--source-width:' + str(spec['width']) + 'px">'
                    + '</div><p class="scroll-hint" data-origin="renderer-ui">چھوٹی سکرین اُتے پوری شکل ویکھن لئی پاسے سرکاؤ، یا '
                    + '<a href="' + attr(src) + '">اصل شکل وکھری کھولو</a>۔</p></div>')
        if name == 'table':
            return self.table(node)
        return super().render(node, parent, index)

    def table(self, node):
        sid = node.get('id')
        key = sid + '/summary'
        require(key not in self.used, 'Repeated source table summary')
        self.used.append(key)
        spec = next(table for table in self.manifest['tables'] if table['id'] == sid)
        summary_attribute = spec['summary_source_attribute']
        require(summary_attribute in node.attrib, 'Changed source summary attribute')
        require(len(node) == 1 and tag(node[0]) == 'tgroup', 'Unexpected source table children')
        group = node[0]
        cols = int(group.get('cols'))
        require(cols == spec['columns'], 'Changed source column count')
        colspecs = [child for child in group if tag(child) == 'colspec']
        row_groups = [child for child in group if tag(child) in {'thead', 'tbody'}]
        require(len(colspecs) + len(row_groups) == len(group), 'Unknown tgroup structure')
        require([tag(child) for child in row_groups] == (['thead', 'tbody'] if spec['source_thead_rows'] else ['tbody']),
                'Changed source row groups')
        header_grid = bool(spec['source_thead_rows'])
        require(len(colspecs) == (cols if header_grid else 0), 'Changed source colspecs')
        col_html = ''
        if colspecs:
            col_html = '<colgroup>' + ''.join('<col data-source-tag="colspec" data-source-colnum="' + attr(col.get('colnum'))
                + '" data-source-colname="' + attr(col.get('colname')) + '">' for col in colspecs) + '</colgroup>'
        row_index, blank_cells, groups_html = 0, [], ''
        for row_group in row_groups:
            rows_html = ''
            for row in row_group:
                row_index += 1
                require(tag(row) == 'row' and len(row) == cols, 'Changed source row geometry')
                cells_html = ''
                for cell_index, cell in enumerate(row, 1):
                    require(tag(cell) == 'entry' and set(cell.attrib) <= {'align', 'valign'},
                            'Unexpected source cell/span attributes')
                    require(cell.attrib == ({'align': 'left', 'valign': 'middle'} if header_grid else {}),
                            'Changed source cell alignment attributes')
                    cell_key = f'{sid}/row/{row_index}/entry/{cell_index}'
                    if not len(cell) and not (cell.text or '').strip():
                        blank_cells.append({'row': row_index, 'entry': cell_index})
                    heading = tag(row_group) == 'thead'
                    # Source labels explicitly name the multiplier for the whole body row.
                    row_heading = header_grid and not heading and cell_index == 1
                    if row_heading:
                        require(re.fullmatch(r'Multiples of \d+', (cell.text or '').strip()), 'Unknown row header meaning')
                    cell_tag = 'th' if heading or row_heading else 'td'
                    scope = ' scope="' + ('col' if heading else 'row') + '"' if heading or row_heading else ''
                    numeric = not len(cell) and bool(re.fullmatch(r'\d+', (cell.text or '').strip()))
                    direction = 'ltr' if numeric else 'rtl'
                    source_alignment = ''.join(' data-source-' + key + '="' + attr(cell.get(key)) + '"'
                                               for key in ('align', 'valign') if key in cell.attrib)
                    cells_html += ('<' + cell_tag + ' data-source-tag="entry" data-source-key="' + attr(cell_key)
                                   + '" dir="' + direction + '"' + scope + source_alignment + '>' + self.translated(cell_key, cell)
                                   + '</' + cell_tag + '>')
                rows_html += '<tr data-source-tag="row" data-source-row="' + str(row_index) + '">' + cells_html + '</tr>'
            group_tag = tag(row_group)
            groups_html += '<' + group_tag + ' data-source-tag="' + group_tag + '">' + rows_html + '</' + group_tag + '>'
        require(row_index == spec['rows'] and blank_cells == spec['empty_cells'], 'Changed row count or empty cells')
        require(row_index * cols == spec['cells'], 'Changed source cell total')
        label = ''
        if sid in self.table_labels:
            label = ('<p class="source-table-label" data-origin="renderer-ui">جدول <bdi dir="ltr">'
                     + attr(self.table_labels[sid]) + '</bdi></p>')
        css_class = 'source-table source-grid' if header_grid else 'source-table source-worked-table'
        summary = self.blocks[key]
        attributes = (' id="' + attr(sid) + '" data-source-tag="table" data-source-summary-attribute="' + summary_attribute
                      + '" aria-label="' + attr(summary) + '" data-source-summary="' + attr(summary)
                      + '" data-description-origin="source-translation" data-source-tgroup-cols="' + str(cols)
                      + '" data-source-class="' + attr(node.get('class', '')) + '"')
        return ('<div class="source-table-container" data-source-child="' + attr(sid) + '">' + label
                + '<div class="table-scroll source-table-scroll" dir="ltr" tabindex="0" role="region" aria-label="جدول؛ لوڑ پئے تے پاسے سرکاؤ">'
                + '<table' + attributes + ' dir="ltr" class="' + css_class + '">' + col_html + groups_html
                + '</table></div><p class="scroll-hint" data-origin="renderer-ui">سارے کالم ویکھن لئی لوڑ پئے تے جدول نوں پاسے سرکاؤ۔</p></div>')

    def bridge(self):
        raw = self.translation['bridge_after_html']
        fragment = ET.fromstring(raw)
        require(fragment.tag == 'section' and fragment.get('id') == 'a10-003-original-bridge'
                and fragment.get('class') == 'original-bridge', 'Original bridge label missing')
        ids = {node.get('id') for node in fragment.iter() if node.get('id')}
        require(all(record['bridge_id'] in ids for record in self.translation['source_corrections']),
                'Missing original clarification destination')
        # Add a presentation provenance marker only; source/translation inputs stay frozen.
        require(raw.startswith('<section '), 'Unexpected bridge root syntax')
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
        require(target.is_file() and file_hash(target) == spec['sha256'], 'Run prepare_a10_003.py: image missing/changed')
    require(NOTICES.is_file() and json.loads(NOTICES.read_text(encoding='utf-8')) == notice_record(manifest, prepared, notices),
            'Run prepare_a10_003.py: retained component evidence missing/changed')
    target_text = TRANSLATION.read_text(encoding='utf-8')
    translation = json.loads(target_text)
    require((translation['locale'], translation['unit'], translation['module']) == ('pnb-Arab-PK', 'A10-003', 'm82452'),
            'Unexpected translation scope')
    require(not re.search('[\u0a00-\u0a7f\u202a-\u202e\u2066-\u2069\u200e\u200f\u061c\ufffd]', target_text),
            'Disallowed script/direction controls')
    require(list(translation['source_blocks']) == manifest['source_block_keys_in_document_order'], 'Changed source key order')
    require(translation['image_alt_overrides'] == translation['table_summary_overrides'] == {},
            'No accessible override is declared for A10-003')
    reader = Reader(manifest, document, translation)
    body, bridge = reader.render(document), reader.bridge()
    require(reader.used == list(translation['source_blocks']) and len(reader.used) == 178, 'Changed source coverage/order')
    require(not re.search(r'\{\{[^}]*\}\}', body + bridge), 'Unresolved placeholder')
    css = (BASE / 'styles/reader.css').read_text(encoding='utf-8') + LOCAL_CSS
    source_url = manifest['upstream_url'] + '/blob/' + manifest['commit'] + '/' + manifest['path']
    result = f'''<!doctype html>
<html lang="pnb-Arab-PK" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Shahmukhi Punjabi Elementary Algebra 2e; A10-003 bounded translation, not a complete book">
<title>{attr(translation['title'])} — A10-003</title><style>{css}</style></head>
<body class="a10-reader a10-003-reader"><header><p class="eyebrow"><bdi dir="ltr">A10-003 · A10 / col31130 / m82452</bdi></p>
<h1>{attr(translation['title'])}</h1><p>{attr(translation['subtitle'])}</p>
<p class="status">ابتدائی ترجمہ · پنجابی دے ماہر تے ریاضی دے استاد دی جانچ ہن تک نہیں ہوئی۔</p>
<nav aria-label="سبق دے حصے"><a href="a10-unit-002.html">پچھلا حصہ: عدد لفظاں وچ لکھنا تے گول کرنا</a> · <a href="#{manifest['scope_from']}">ماخذ دا ترجمہ</a> · <a href="#a10-003-original-bridge">لفظاں دی کُنجی تے وضاحت</a> · <a href="#credits">ماخذ تے انتساب</a></nav></header>
<main><p class="source-label" data-origin="renderer-ui">ماخذ: <bdi dir="ltr" lang="en">OpenStax Elementary Algebra 2e</bdi>، باب <bdi dir="ltr" lang="en">Foundations</bdi>، سبق «{attr(manifest['module_title_pnb'])}»۔ ایتھے مضاعف تے پورا ونڈے جان والا پورا سیکشن تے اوہدے نالوں پہلاں والا پیرا ترجمہ کیتے گئے نیں؛ پورا سبق یا پوری کتاب نہیں۔</p>
{body}{bridge}
<p class="status" data-origin="renderer-ui">ایس سبق دا اگلا ماخذی سیکشن ایس حصے وچ شامل نہیں۔ پنجاں مقررہ کتاباں دا پورا کم ہن وی جاری اے۔</p></main>
<footer id="credits" lang="en" dir="ltr"><h2>Sources, credits and changes — A10-003</h2>
<p>Adapted from <a href="{attr(source_url)}">OpenStax Elementary Algebra 2e, module m82452: Introduction to Whole Numbers</a>, collection col31130, Foundations. Original senior contributing authors: Lynn Marecek; MaryAnne Anthony-Smith; Andrea Honeycutt Mathis. Source publisher: OpenStax / Rice University.</p>
<p>The existing A10 notice states <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International</a>, subject to component-specific credits and restrictions. This adaptation retains that license framework and those restrictions. See the retained <a href="../provenance/A10-release/NOTICE.txt">A10 release notice</a>, <a href="../provenance/upstream--osbooks-prealgebra-bundle/LICENSE">canonical license text</a>, and <a href="../provenance/a10-unit-003-component-notices.json">selected component evidence</a>. Media authority rows establish source identity, not new image-specific clearance. No new clearance is asserted.</p>
<p>OpenStax and Rice University do not endorse this translation. Their names, logos and marks are not licensed by the source notice. No cover or added logo is reproduced. Both original JPEG diagrams are unchanged and unmirrored and remain unnumbered. Table label A10-003.1 is local reader numbering, not canonical book numbering; source table eip-272 remains unnumbered.</p>
<p>Changes: Shahmukhi Punjabi translation of 178 source text/cell scaffolds; RTL prose with LTR mathematics, numbers, English and original diagram/table geometry. All 40 source IDs, three exact MathML trees, the source newline, both tables with 148 cells including 4 empty cells, and both original JPEGs are retained. The thirteen-column grid retains its source thead as thirteen column headers; the nine source Multiples-of body labels gain row-header semantics without cell movement or text changes. Source grid alignment attributes remain in metadata; numeric cells keep left/middle alignment while Punjabi labels follow RTL text alignment. The worked table has 18 data cells and no invented headers. The legacy summary versus aria-label source distinction is recorded. Three source links point to the actual multiples table. Original bilingual keys and source-range/domain qualifications are labeled separately; no source alt/summary correction or extra practice is added.</p>
<p>Indonesian comparison: <a href="https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id/releases/tag/v1.0.2">Elementary Algebra 2e Indonesian preservation release v1.0.2</a>. Its 82-module release and OpenAI Codex process provenance do not imply equivalent Punjabi coverage. This Punjabi adaptation was produced with OpenAI Codex assistance at the user's direction; original human-contributor credits remain intact.</p>
<p>Coverage: standalone paragraph newelem_para01 followed by all of section fs-id1170655199097, through its last direct child fs-id1170655200179 and answer fs-id1170655247402; stop before fs-id1170655247410. Earlier collection items m82630 and m82451 are outside this unit and have separate checkpoints. This is not a complete module, complete textbook, or completed five-work assignment, and is not a training or fine-tuning dataset. Native-language, educator and assistive-technology review remain pending. <a href="../source-excerpts/a10-unit-003.cnxml">Frozen source witness</a> · <a href="../source-excerpts/manifest-a10-003.json">Exact source selection</a>.</p>
</footer></body></html>
'''
    ids = OutputIDs()
    ids.feed(result)
    require(len(ids.ids) == len(set(ids.ids)), 'Duplicate reader IDs')
    expected = manifest['source_ids_in_document_order']
    require([sid for sid in ids.ids if sid in set(expected)] == expected, 'Changed rendered source ID order')
    links = LocalLinks()
    links.feed(result)
    for target in links.targets:
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc:
            continue
        if parsed.path:
            path = (OUTPUT.parent / unquote(parsed.path)).resolve()
            require(path.is_relative_to(BASE.resolve()) and path.is_file(), 'Missing/unsafe local target: ' + target)
        else:
            require(parsed.fragment in ids.ids, 'Missing local fragment: ' + target)
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(result, encoding='utf-8', newline='\n')
    print('Built A10-003:178source blocks,40IDs,3exactMathML,2tables/148cells,2originalJPEGs; full assignment incomplete.')


if __name__ == '__main__':
    build()
