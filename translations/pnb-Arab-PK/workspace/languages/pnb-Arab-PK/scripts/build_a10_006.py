"""Deterministic, source-bound A10-006 first-section reader."""
import copy
import html
import json
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

from build_a10 import OutputIDs, attr
from prepare_a10_006 import BASE, ROOT, MATH, NOTICES, TRANSLATION, file_hash, load_inputs, notice_record, require, tag

ET.register_namespace('', MATH)
OUTPUT = BASE / 'reader/a10-unit-006.html'
MATH_TAG = '{' + MATH + '}math'
PARTS = {'ⓐ': 'a', 'ⓑ': 'b', 'ⓒ': 'c', 'ⓓ': 'd', 'ⓔ': 'e'}
LONG_PARTS = {'fs-id1166424795899', 'fs-id1170655353526', 'fs-id1170655222902'}
LOCAL_CSS = r'''
.a10-006-reader .source-document,.a10-006-reader .source-metadata,.a10-006-reader .source-abstract,
.a10-006-reader .source-content,.a10-006-reader .source-section,.a10-006-reader .source-note,
.a10-006-reader .source-example,.a10-006-reader .source-exercise,.a10-006-reader .source-problem,
.a10-006-reader .source-solution,.a10-006-reader .source-block-container { min-width:0; max-width:100%; }
.a10-006-reader .source-metadata { font-size:.87em; background:#f0f5f1; padding:.6rem 1rem; margin-block:1rem; overflow-wrap:anywhere; }
.a10-006-reader .source-retained-metadata { margin-block:.4rem; overflow-wrap:anywhere; }
.a10-006-reader .source-section { border-block-start:1px solid #cad7d1; margin-block-start:1.2rem; }
.a10-006-reader .source-example { margin-block:1.5rem; border-block-start:2px solid #8cb4a3; padding-block-start:.4rem; }
.a10-006-reader .source-exercise { margin-block:.8rem; }
.a10-006-reader .source-solution { padding-block-start:.35rem; }
.a10-006-reader .example-label,.a10-006-reader .solution-label { color:#1b6159; }
.a10-006-reader .source-inline-part { display:inline-block; white-space:nowrap; max-width:100%; vertical-align:baseline; margin-inline-end:.25rem; }
.a10-006-reader .source-para[data-long-source-part=true] { white-space:normal; }
.a10-006-reader .source-original-advisory { font-size:.9rem; border-inline-start:3px solid #b98238; padding-inline-start:.7rem; }
.a10-006-reader .source-english-echo { border:1px solid #c6d5cc; border-radius:4px; background:#f8f3e8; padding:.35rem .65rem; margin-block:.45rem; white-space:normal; overflow-wrap:anywhere; }
.a10-006-reader .source-english-label { font-size:.78em; margin:0; color:#5c4b2c; }
.a10-006-reader .source-english-words { font-size:.88em; line-height:1.6; margin:.1rem 0; text-align:left; }
.a10-006-reader .source-equation { direction:ltr; text-align:center; overflow-x:auto; background:#f0f5f1; padding:1rem .5rem; margin-block:1.3rem; border-radius:4px; line-height:1.7; }
.a10-006-reader .source-equation .math-isolate { display:block; max-width:none; width:max-content; min-width:100%; }
.a10-006-reader .source-empty-label { display:none; }
.a10-006-reader .source-media { min-width:0; max-width:100%; margin-block:1rem; }
.a10-006-reader .source-media .figure-scroll { width:100%; max-width:100%; direction:ltr; overflow-x:auto; }
.a10-006-reader .source-media img { display:block; width:var(--source-width); min-width:var(--source-width); max-width:none; height:auto; padding:0; border:0; margin-inline:auto; background:white; }
.a10-006-reader .source-media .scroll-hint,.a10-006-reader .source-table-container > .scroll-hint { direction:rtl; white-space:normal; text-align:start; }
.a10-006-reader .source-table-container { min-width:0; max-width:100%; margin-block:1.2rem; }
.a10-006-reader .source-table-scroll { width:100%; max-width:100%; overflow-x:auto; direction:ltr; }
.a10-006-reader .source-table { width:var(--source-table-width); min-width:var(--source-table-width); max-width:none; table-layout:fixed; direction:ltr; }
.a10-006-reader .source-table th,.a10-006-reader .source-table td { min-width:0; width:330px; white-space:normal; overflow-wrap:anywhere; font-family:inherit; }
.a10-006-reader .source-table td[dir=ltr],.a10-006-reader .source-table th[dir=ltr] { font-family:"Cambria Math",Cambria,"Segoe UI",serif; }
.a10-006-reader .source-table .math-isolate { max-width:100%; }
.a10-006-reader .source-table-label { font-size:.9em; margin:.25rem 0; color:#1b6159; }
.a10-006-reader .source-column-binding { display:none; }
.a10-006-reader .source-term.no-emphasis { font-style:normal; }
.a10-006-reader .original-bridge { border-block-start:2px solid #b98238; margin-block-start:1.8rem; padding-block-start:.5rem; }
@media (max-width:600px) {
  .a10-006-reader .source-table { --source-table-width:calc(var(--source-columns) * 330px); }
}
'''


def compact(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def inner_xml(fragment):
    out = html.escape(fragment.text or '', quote=False)
    for child in fragment:
        out += ET.tostring(child, encoding='unicode', short_empty_elements=True)
    return out


class Reader:
    def __init__(self, manifest, document, translation):
        self.manifest = manifest
        self.document = document
        self.translation = translation
        self.blocks = translation['source_blocks']
        self.used = []
        self.bound = set()
        self.paths = {}
        self.nodes = {}
        def walk(node, path):
            self.paths[node] = path
            self.nodes[path] = node
            for index, child in enumerate(node):
                walk(child, path + '/' + str(index))
        walk(document, 'document')
        self.key_nodes = {key: self.nodes[path] for key, path in manifest['source_keys_to_paths'].items()}
        require(list(self.key_nodes) == list(self.blocks), 'Manifest/source key sequence differs from translation')
        self.images = {entry['source_src']: entry for entry in manifest['images']}
        self.tables = {entry['id']: entry for entry in manifest['tables']}
        self.link_labels = translation['source_link_labels']
        self.echo_keys = set(translation['source_english_echo_keys'])
        self.echo_omit_math = set(translation['source_english_echo_policy']['omit_mathml_owners'])
        self.advisories = {}
        for record in translation['source_corrections']:
            for key in record['source_keys']:
                require(key in self.blocks, 'Unknown correction source key: ' + key)
                self.advisories.setdefault(key, []).append(record['note_id'])
        self.example_labels = {row['id']: row['local_label'] for row in manifest['example_labels']}
        self.numbered_tables = {row['id']: row['local_label'] for row in manifest['references']
                                if row['kind'] == 'table' and row['unit'] == 'A10-006'}
        self.short_groups = {row['key'] for row in manifest['token_owners'] if row['group_short_parts']}
        require(self.short_groups.isdisjoint(LONG_PARTS), 'Long source paragraph cannot be atomic parts')

    def binding(self, node, include_id=True):
        require(node in self.paths and node not in self.bound, 'Repeated/unknown source binding')
        self.bound.add(node)
        values = []
        if include_id and node.get('id'):
            values.append(('id', node.get('id')))
        values.extend([
            ('data-source-tag', tag(node)), ('data-source-path', self.paths[node]),
            ('data-source-qname', node.tag), ('data-source-attributes', compact(node.attrib))
        ])
        return ''.join(' ' + name + '="' + attr(value) + '"' for name, value in values)

    def math_html(self, node):
        require(node.tag == MATH_TAG and node.get('dir') in {None, 'ltr'}, 'Unexpected MathML root direction')
        clone = copy.deepcopy(node)
        clone.tail = None
        clone.set('dir', 'ltr')
        return ('<span class="math-isolate" dir="ltr"' + self.binding(node)
                + '>' + ET.tostring(clone, encoding='unicode', short_empty_elements=True) + '</span>')

    def bind_inline(self, source_node, fragment):
        mappings = [
            ([child for child in source_node if tag(child) == 'term'], list(fragment.iter('span')), 'term'),
            ([child for child in source_node if tag(child) == 'emphasis' and child.get('effect') == 'bold'],
             list(fragment.iter('strong')), 'bold emphasis'),
            ([child for child in source_node if tag(child) == 'emphasis' and child.get('effect') == 'italics'],
             list(fragment.iter('em')), 'italic emphasis'),
            ([child for child in source_node if tag(child) == 'newline'], list(fragment.iter('br')), 'newline')
        ]
        for sources, raw_targets, label in mappings:
            if label == 'term':
                targets = [node for node in raw_targets if 'source-term' in node.get('class', '').split()]
            else:
                targets = raw_targets
            require(len(sources) == len(targets), 'Changed ' + label + ' count in ' + self.paths[source_node])
            for source, target in zip(sources, targets):
                if source.get('id'):
                    require(target.get('id') == source.get('id'), 'Changed term ID')
                for name, value in self.binding_dict(source, include_id=False).items():
                    target.set(name, value)
        tokens = [child for child in source_node if tag(child) == 'span' and child.get('class') == 'token']
        labels = [node for node in fragment.iter('bdi') if re.fullmatch(r'\(([a-e])\)', ''.join(node.itertext()).strip())]
        require(len(tokens) == len(labels), 'Changed source part-label count: ' + self.paths[source_node])
        require([PARTS[(node.text or '').strip()] for node in tokens]
                == [re.fullmatch(r'\(([a-e])\)', ''.join(node.itertext()).strip())[1] for node in labels],
                'Changed source part-label order')
        for source, target in zip(tokens, labels):
            for name, value in self.binding_dict(source, include_id=False).items():
                target.set(name, value)

    def binding_dict(self, node, include_id=True):
        require(node in self.paths and node not in self.bound, 'Repeated/unknown source binding')
        self.bound.add(node)
        values = {}
        if include_id and node.get('id'):
            values['id'] = node.get('id')
        values.update({'data-source-tag': tag(node), 'data-source-path': self.paths[node],
                       'data-source-qname': node.tag, 'data-source-attributes': compact(node.attrib)})
        return values

    def translated(self, key, node):
        require(self.key_nodes.get(key) is node and key not in self.used, 'Missing/repeated source key: ' + key)
        self.used.append(key)
        value = self.blocks[key]
        maths = [child for child in node if child.tag == MATH_TAG]
        links = [child for child in node if tag(child) == 'link']
        require([int(i) for i in re.findall(r'\{\{math:(\d+)\}\}', value)] == list(range(len(maths))),
                'Changed math placeholders: ' + key)
        require([int(i) for i in re.findall(r'\{\{link:(\d+)\}\}', value)] == list(range(len(links))),
                'Changed link placeholders: ' + key)
        require(not re.search(r'\{\{child:', value), 'Unexpected child placeholder: ' + key)
        require(len(re.findall(r'<br\s*/?>', value)) == sum(tag(child) == 'newline' for child in node),
                'Changed newline count: ' + key)
        fragment = ET.fromstring('<fragment>' + value + '</fragment>')
        self.bind_inline(node, fragment)
        value = inner_xml(fragment)
        value = re.sub(r'\{\{math:(\d+)\}\}', lambda match: self.math_html(maths[int(match[1])]), value)
        def link(match):
            index = int(match[1])
            source = links[index]
            label_key = key + '/link/' + str(index)
            require(label_key in self.link_labels, 'Missing source-link label')
            label = self.link_labels[label_key]
            return ('<a href="#' + attr(source.get('target-id')) + '" data-source-target="'
                    + attr(source.get('target-id')) + '"' + self.binding(source)
                    + '>' + label + '</a>')
        return re.sub(r'\{\{link:(\d+)\}\}', link, value)

    def group_parts(self, value, node, key):
        tokens = [child for child in node if tag(child) == 'span' and child.get('class') == 'token']
        if not tokens:
            return value
        expected = [PARTS[(child.text or '').strip()] for child in tokens]
        labels = list(re.finditer(r'<bdi\b[^>]*>\(([a-e])\)</bdi>', value))
        require([match[1] for match in labels] == expected, 'Changed rendered part order')
        require(key in self.short_groups, 'Undeclared inline part grouping: ' + key)
        result = value[:labels[0].start()]
        for index, label in enumerate(labels):
            end = labels[index + 1].start() if index + 1 < len(labels) else len(value)
            part = value[label.start():end]
            suffix = re.search(r'((?:\s|<br\s*/?>)*)\Z', part)
            result += ('<span class="source-inline-part" data-source-part="' + label[1]
                       + '">' + part[:suffix.start()] + '</span>' + suffix[0])
        return result

    def english_lexical(self, node, omit_math):
        def lexical(owner):
            result = html.escape(owner.text or '', quote=False)
            for child in owner:
                name = tag(child)
                if child.tag == MATH_TAG:
                    require(omit_math, 'Unexpected MathML in retained English lexical owner')
                elif name == 'emphasis':
                    html_tag = 'strong' if child.get('effect') == 'bold' else 'em'
                    result += '<' + html_tag + '>' + lexical(child) + '</' + html_tag + '>'
                elif name == 'term':
                    result += '<span>' + lexical(child) + '</span>'
                elif name == 'span' and child.get('class') == 'token':
                    label = PARTS[(child.text or '').strip()]
                    result += '<bdi dir="ltr" data-english-source-part="' + label + '">(' + label + ')</bdi>'
                elif name == 'newline':
                    result += '<br />'
                else:
                    raise ValueError('Unsupported retained English inline child: ' + name)
                result += html.escape(child.tail or '', quote=False)
            return result
        return lexical(node)

    def english_echo(self, key, node):
        if key not in self.echo_keys:
            return ''
        has_math = any(child.tag == MATH_TAG for child in node)
        require(has_math == (key in self.echo_omit_math), 'Unexpected English-echo MathML policy: ' + key)
        lexical = self.english_lexical(node, has_math)
        require('<math' not in lexical and ' id=' not in lexical, 'English echo duplicated source node identity')
        return ('<div class="source-english-echo" data-origin="retained-canonical-English-words"'
                + ' data-source-english-for="' + attr(key) + '" aria-describedby="a10-006-english-context">'
                + '<p class="source-english-label" dir="rtl">اصل ماخذ دے انگریزی لفظ</p>'
                + '<p class="source-english-words" lang="en" dir="ltr">' + lexical + '</p></div>')

    def described(self, key, additional=()):
        values = list(self.advisories.get(key, [])) + list(additional)
        values = list(dict.fromkeys(values))
        return ' aria-describedby="' + attr(' '.join(values)) + '"' if values else ''

    def advisory(self, key):
        targets = self.advisories.get(key, [])
        if not targets:
            return ''
        links = '؛ '.join('<a href="#' + attr(target) + '">مترجم دی وکھری وضاحت</a>' for target in targets)
        return ('<p class="source-original-advisory" data-origin="renderer-ui" data-source-advisory-for="'
                + attr(key) + '">ایس ماخذی گل نال ' + links + ' وی پڑھو۔</p>')

    def children(self, node):
        require(not (node.text or '').strip(), 'Untranslated source container text: ' + self.paths[node])
        result = node.text or ''
        for index, child in enumerate(node):
            result += self.render(child, node, index)
            require(not (child.tail or '').strip(), 'Untranslated source container tail: ' + self.paths[child])
            result += child.tail or ''
        return result

    def leaf(self, node, parent, index):
        name = tag(node)
        key = next((key for key, source in self.key_nodes.items() if source is node), None)
        require(key is not None, 'Missing leaf key: ' + self.paths[node])
        value = self.translated(key, node)
        if name == 'para' and key in self.short_groups:
            value = self.group_parts(value, node, key)
        attrs = self.binding(node) + ' data-source-key="' + attr(key) + '"'
        described = self.described(key)
        if name == 'title':
            out = 'h1' if tag(parent) == 'document' else 'h2' if tag(parent) == 'section' else 'h3'
        elif name == 'item':
            out = 'li'
        else:
            out = 'p'
        classes = []
        if name == 'para':
            classes.append('source-para')
        if name == 'item':
            classes.append('source-item')
        class_attr = ' class="' + ' '.join(classes) + '"' if classes else ''
        long = ' data-long-source-part="true"' if key in LONG_PARTS else ''
        result = '<' + out + attrs + class_attr + long + described + '>' + value
        if name == 'item':
            result += self.advisory(key)
        result += '</' + out + '>'
        extras = self.english_echo(key, node)
        if name != 'item':
            extras += self.advisory(key)
        if extras:
            return ('<div class="source-block-container" data-source-block-owner="' + attr(key)
                    + '">' + result + extras + '</div>')
        return result

    def render(self, node, parent=None, index=0):
        name, sid = tag(node), node.get('id')
        if name in {'para', 'title', 'item'}:
            return self.leaf(node, parent, index)
        if name == 'math':
            return self.math_html(node)
        if name == 'document':
            return '<div' + self.binding(node) + ' class="source-document">' + self.children(node) + '</div>'
        if name in {'metadata', 'abstract', 'content', 'section', 'note', 'example', 'exercise', 'problem', 'solution'}:
            out = 'section' if name in {'metadata', 'section', 'note', 'example', 'solution'} else 'div'
            ui = ''
            extra = ''
            if name == 'metadata':
                ui = '<h2 class="metadata-label" data-origin="renderer-ui">ماخذ دی پہچان تے سِکھن دے مقصد</h2>'
            elif name == 'example':
                label = self.example_labels[sid]
                ui = ('<h2 class="example-label" data-origin="renderer-ui">حل کیتی مثال <bdi dir="ltr">'
                      + attr(label) + '</bdi></h2>')
            elif name == 'solution' and not any(tag(child) == 'title' for child in node):
                ui = '<h3 class="solution-label" data-origin="renderer-ui">حل</h3>'
                extra = ' aria-label="حل"'
            elif name == 'note' and node.get('class') == 'try':
                extra = ' aria-label="آپ کر کے ویکھو"'
            return ('<' + out + self.binding(node) + ' class="source-' + name + '"' + extra + '>'
                    + ui + self.children(node) + '</' + out + '>')
        if name in {'content-id', 'uuid'}:
            require(not len(node), 'Unexpected metadata identity children')
            label = 'ماخذ دے ماڈیول دی پہچان' if name == 'content-id' else 'ماخذ دی مستقل پہچان'
            return ('<p' + self.binding(node) + ' class="source-retained-metadata" aria-label="' + label
                    + '"><bdi dir="ltr" lang="en">' + attr(node.text or '') + '</bdi></p>')
        if name == 'list':
            kind = node.get('list-type')
            if sid == 'list-00001':
                require(kind is None and set(node.attrib) == {'id'}, 'Objective-list structure changed')
                out, classes = 'ul', 'source-objectives'
            else:
                require(kind == 'bulleted' and node.get('bullet-style') == 'bullet', 'Source list style changed')
                out, classes = 'ul', 'source-bulleted'
            return ('<' + out + self.binding(node) + ' class="' + classes + '" role="list">'
                    + self.children(node) + '</' + out + '>')
        if name == 'equation':
            require(len(node) == 2 and tag(node[0]) == 'label' and tag(node[1]) == 'math'
                    and not (node[0].text or '').strip() and not len(node[0]), 'Equation structure changed')
            return ('<div' + self.binding(node) + ' class="source-equation">'
                    + self.render(node[0], node, 0) + (node[0].tail or '')
                    + self.render(node[1], node, 1) + (node[1].tail or '') + '</div>')
        if name == 'label':
            require(not len(node) and not (node.text or '').strip(), 'Source label is not empty')
            return '<span' + self.binding(node) + ' class="source-empty-label" aria-hidden="true"></span>'
        if name == 'media':
            return self.media(node)
        if name == 'table':
            return self.table(node)
        if name in {'tgroup', 'colspec', 'thead', 'tbody', 'row', 'entry', 'image', 'term', 'emphasis', 'span', 'link', 'newline'}:
            raise ValueError('Inline/table source node escaped its owner: ' + self.paths[node])
        raise ValueError('Unsupported selected source element: ' + name)

    def media(self, node):
        sid = node.get('id')
        key = sid + '/alt'
        require(self.key_nodes.get(key) is node and key not in self.used and len(node) == 1
                and tag(node[0]) == 'image', 'Changed media/key structure')
        self.used.append(key)
        image = node[0]
        spec = self.images.get(image.get('src'))
        require(spec and spec['media_id'] == sid and image.get('mime-type') == spec['declared_mime'],
                'Changed image association or MIME')
        faithful = self.blocks[key]
        require('<' not in faithful and '>' not in faithful, 'Media alt must be plain text')
        override_record = self.translation['image_alt_overrides'].get(key)
        if override_record:
            require(override_record == spec['source_alt_override'], 'Image override differs from frozen declaration')
        effective = override_record['alt'] if override_record else faithful
        origin = 'original-correction' if override_record else 'source-translation'
        extra_ids = [spec['original_bilingual_key_id']]
        described = self.described(key, extra_ids)
        src = '../' + spec['path']
        image_html = ('<img' + self.binding(image) + ' src="' + attr(src)
                      + '" alt="' + attr(effective) + '" data-source-alt="' + attr(faithful)
                      + '" data-description-origin="' + origin + '" data-source-image-mime="'
                      + attr(image.get('mime-type')) + '" data-rendered-image-mime="image/jpeg" width="'
                      + str(spec['width']) + '" height="' + str(spec['height']) + '" style="--source-width:'
                      + str(spec['width']) + 'px"' + described + ' />')
        return ('<div' + self.binding(node) + ' data-source-key="' + attr(key) + '" class="source-media">'
                + (node.text or '') + '<div class="figure-scroll" dir="ltr" tabindex="0" role="region"'
                + ' aria-label="اصل تصویر؛ لوڑ پئے تے پاسے سرکاؤ">' + image_html + '</div>' + (image.tail or '')
                + '<p class="scroll-hint" data-origin="renderer-ui" dir="rtl">چھوٹی سکرین اُتے پوری تصویر ویکھن لئی پاسے سرکاؤ، یا '
                + '<a href="' + attr(src) + '">اصل تصویر وکھری کھولو</a>۔ '
                + '<a href="#' + attr(spec['original_bilingual_key_id']) + '">دو زبانی کنجی یا وضاحت</a> وی ویکھو۔</p>'
                + self.advisory(key) + '</div>')

    def table(self, node):
        sid = node.get('id')
        key = sid + '/summary'
        require(self.key_nodes.get(key) is node and key not in self.used, 'Changed/repeated table summary')
        self.used.append(key)
        spec = self.tables[sid]
        label_nodes = [child for child in node if tag(child) == 'label']
        groups = [child for child in node if tag(child) == 'tgroup']
        require(len(label_nodes) <= 1 and len(groups) == 1
                and all(tag(child) in {'label', 'tgroup'} for child in node), 'Changed table root children')
        label_html = ''
        if label_nodes:
            require(not len(label_nodes[0]) and not (label_nodes[0].text or '').strip(), 'Nonempty source table label')
            label_html = self.render(label_nodes[0], node, list(node).index(label_nodes[0])) + (label_nodes[0].tail or '')
        group = groups[0]
        require(int(group.get('cols')) == spec['columns'], 'Changed tgroup column count')
        columns = [child for child in group if tag(child) == 'colspec']
        require(len(columns) in {0, spec['columns']}, 'Changed colspec count')
        position = 0
        column_html = ''
        if columns:
            require(list(group)[:len(columns)] == columns, 'Colspecs changed position')
            cols = []
            for column in columns:
                cols.append('<col' + self.binding(column) + ' />' + (column.tail or ''))
            column_html = '<colgroup class="source-column-group">' + ''.join(cols) + '</colgroup>'
            position = len(columns)
        section_html = []
        row_index = 0
        header_cells = 0
        cell_count = 0
        empty_count = 0
        for section in list(group)[position:]:
            section_name = tag(section)
            require(section_name in {'thead', 'tbody'}, 'Unexpected tgroup child')
            rows = []
            for row in section:
                require(tag(row) == 'row', 'Non-row in table section')
                row_index += 1
                cells = []
                for entry_index, entry in enumerate(row, 1):
                    require(tag(entry) == 'entry', 'Non-entry in source row')
                    cell_count += 1
                    if not len(entry) and not (entry.text or '').strip():
                        empty_count += 1
                    cell_key = f'{sid}/row/{row_index}/entry/{entry_index}'
                    require(self.key_nodes.get(cell_key) is entry, 'Changed table-cell key path')
                    value = self.translated(cell_key, entry)
                    require(not [child for child in entry if tag(child) == 'span' and child.get('class') == 'token']
                            or not re.search(r'source-inline-part', value), 'Table part group must not be generated')
                    is_header = section_name == 'thead'
                    if is_header:
                        header_cells += 1
                    out = 'th' if is_header else 'td'
                    direction = 'ltr' if not re.search(r'[\u0600-\u06ff]', ''.join(ET.fromstring('<f>' + value + '</f>').itertext())) else 'rtl'
                    source_align = entry.get('align', 'left')
                    source_vertical = entry.get('valign', row.get('valign', 'top'))
                    cell = ('<' + out + self.binding(entry) + ' data-source-key="' + attr(cell_key)
                            + '" dir="' + direction + '" style="text-align:' + attr(source_align)
                            + ';vertical-align:' + attr(source_vertical) + '"' + self.described(cell_key)
                            + '>' + value + self.english_echo(cell_key, entry) + self.advisory(cell_key)
                            + '</' + out + '>' + (entry.tail or ''))
                    cells.append(cell)
                rows.append('<tr' + self.binding(row) + '>' + (row.text or '') + ''.join(cells)
                            + '</tr>' + (row.tail or ''))
            section_html.append('<' + section_name + self.binding(section) + '>' + (section.text or '')
                                + ''.join(rows) + '</' + section_name + '>' + (section.tail or ''))
        require((row_index, cell_count, empty_count, header_cells)
                == (spec['rows'], spec['cells'], spec['empty_cells'], spec['source_thead_cells']),
                'Changed source table geometry')
        faithful = self.blocks[key]
        require('<' not in faithful and '>' not in faithful, 'Table summary must be plain text')
        override = self.translation['table_summary_overrides'].get(key)
        if override:
            require(override == self.manifest['table_summary_overrides'][key], 'Table summary override differs')
        effective = override['summary'] if override else faithful
        origin = 'original-correction' if override else 'source-translation'
        source_summary_attr = spec['summary_source_attribute']
        require(node.get(source_summary_attr) == spec['attributes'][source_summary_attr], 'Source summary attribute changed')
        table_html = ('<table' + self.binding(group) + ' class="source-table" dir="ltr"'
                      + ' style="--source-columns:' + str(spec['columns']) + ';--source-table-width:'
                      + str(spec['columns'] * 330) + 'px" aria-label="' + attr(effective)
                      + '" data-source-summary="' + attr(faithful) + '" data-description-origin="' + origin
                      + '" data-source-summary-attribute="' + attr(source_summary_attr) + '"'
                      + ' data-source-tgroup-cols="' + str(spec['columns']) + '"' + self.described(key)
                      + '>' + (group.text or '') + column_html + ''.join(section_html) + '</table>')
        local_label = self.numbered_tables.get(sid)
        label_ui = ('<p class="source-table-label" data-origin="renderer-ui">جدول <bdi dir="ltr">'
                    + attr(local_label) + '</bdi></p>') if local_label else ''
        return ('<div' + self.binding(node) + ' class="source-table-container" data-source-key="' + attr(key)
                + '">' + (node.text or '') + label_html
                + '<div class="table-scroll source-table-scroll" dir="ltr" tabindex="0" role="region"'
                + ' aria-label="جدول؛ لوڑ پئے تے پاسے سرکاؤ">' + table_html + '</div>'
                + (group.tail or '') + label_ui
                + '<p class="scroll-hint" data-origin="renderer-ui" dir="rtl">سارے کالم ویکھن لئی لوڑ پئے تے جدول نوں پاسے سرکاؤ۔</p>'
                + self.advisory(key) + '</div>')

    def bridges(self):
        values = []
        ids = []
        for field in ('bridge_before_html', 'bridge_after_html'):
            raw = self.translation[field]
            root = ET.fromstring(raw)
            require(root.tag == 'section' and root.get('id') and root.get('class') in {'original-bridge', 'bridge'},
                    'Unlabeled original bridge')
            current_ids = [node.get('id') for node in root.iter() if node.get('id')]
            require(len(current_ids) == len(set(current_ids)), 'Duplicate original bridge ID')
            ids.extend(current_ids)
            if 'data-origin=' not in raw:
                raw = raw.replace('<section ', '<section data-origin="original-bridge" ', 1)
            values.append(raw)
        require(len(ids) == len(set(ids)), 'Duplicate original bridge ID')
        required = {record['note_id'] for record in self.translation['source_corrections']}
        required.update(self.translation['retained_image_keys'].values())
        require(required <= set(ids), 'Missing original correction or image-key target')
        return values

    def coverage(self):
        mapped = {node for node in self.document.iter() if not node.tag.startswith('{' + MATH + '}') or node.tag == MATH_TAG}
        require(self.bound == mapped, 'Missing/extra rendered source-node bindings')
        require(self.used == list(self.blocks) and len(self.used) == 187, 'Changed source-block coverage/order')
        require(len([node for node in self.bound if node.tag == MATH_TAG]) == 98, 'Changed MathML binding count')


class LocalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []
    def handle_starttag(self, name, attrs):
        self.targets.extend(value for key, value in attrs if key in {'href', 'src'})


def check_links(result):
    ids = OutputIDs()
    ids.feed(result)
    require(len(ids.ids) == len(set(ids.ids)), 'Duplicate output ID')
    links = LocalLinks()
    links.feed(result)
    for target in links.targets:
        url = urlsplit(target)
        if url.scheme or url.netloc:
            require(url.scheme in {'http', 'https'}, 'Unsafe external link')
            continue
        if url.path:
            path = (OUTPUT.parent / unquote(url.path)).resolve()
            require(path.is_relative_to(BASE.resolve()) and path.is_file(), 'Missing/unsafe local path: ' + target)
            if url.fragment:
                page_ids = OutputIDs()
                page_ids.feed(path.read_text(encoding='utf-8'))
                require(unquote(url.fragment) in page_ids.ids, 'Missing cross-unit fragment: ' + target)
        else:
            require(unquote(url.fragment) in ids.ids, 'Missing local fragment: ' + target)


def build():
    manifest, document, prepared, notices = load_inputs()
    for spec, original, target, data, row, source_alt in prepared:
        require(target.is_file() and file_hash(target) == spec['sha256'], 'Run prepare_a10_006.py: asset absent/changed')
    require(NOTICES.is_file() and json.loads(NOTICES.read_text(encoding='utf-8'))
            == notice_record(manifest, prepared, notices), 'Run prepare_a10_006.py: component evidence absent/changed')
    raw = TRANSLATION.read_text(encoding='utf-8')
    translation = json.loads(raw)
    require((translation['unit'], translation['locale'], translation['canonical_module'])
            == ('A10-006', 'pnb-Arab-PK', 'm82453'), 'Translation scope changed')
    require(file_hash(TRANSLATION) == manifest['translation_sha256']
            and TRANSLATION.stat().st_size == manifest['translation_bytes'], 'Frozen translation changed')
    require(list(translation['source_blocks']) == manifest['source_block_keys_in_document_order'],
            'Changed source-block order')
    require(translation['source_english_echo_keys'] == manifest['source_english_echo_keys'],
            'Changed retained-English echo contract')
    require(translation['image_alt_overrides'] == manifest['image_alt_overrides']
            and translation['table_summary_overrides'] == manifest['table_summary_overrides'],
            'Changed accessible override contract')
    require(not re.search('[\u0a00-\u0a7f\u061c\u200e\u200f\u202a-\u202e\u2066-\u2069\ufffd]', raw),
            'Disallowed script or bidi controls')
    reader = Reader(manifest, document, translation)
    source_body = reader.render(document)
    reader.coverage()
    before, after = reader.bridges()
    require(not re.search(r'\{\{[^}]+\}\}', before + source_body + after), 'Unresolved placeholder')
    css = (BASE / 'styles/reader.css').read_text(encoding='utf-8') + LOCAL_CSS
    source_url = manifest['upstream_url'] + '/blob/' + manifest['commit'] + '/' + manifest['path']
    result = f'''<!doctype html>
<html lang="pnb-Arab-PK" dir="rtl"><head><meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="description" content="Shahmukhi Punjabi Elementary Algebra 2e; A10-006 first complete section with metadata, not a complete module or book" />
<title>{attr(translation['title'])} — A10-006</title><style>{css}</style></head>
<body class="a10-reader a10-006-reader"><header><p class="eyebrow"><bdi dir="ltr">A10-006 · A10 / col31130 / m82453</bdi></p>
<h1>{attr(translation['title'])}</h1>
<p class="status">ابتدائی ترجمہ · پنجابی دے ماہر تے ریاضی دے استاد دی جانچ ہن تک نہیں ہوئی۔</p>
<nav aria-label="سبق دے حصے"><a href="a10-unit-005.html">پچھلا حصہ: صحیح عدداں دیاں مشقاں</a> · <a href="#{manifest['section_start']}">متغیر تے الجبرے دیاں علامتاں</a> · <a href="#a10-006-original-bridge">لفظاں دی کُنجی تے وضاحت</a> · <a href="#credits">ماخذ تے انتساب</a></nav></header>
<main><p class="source-label" data-origin="renderer-ui">ماخذ: <bdi dir="ltr" lang="en">OpenStax Elementary Algebra 2e</bdi>، باب <bdi dir="ltr" lang="en">Foundations</bdi>، سبق «{attr(manifest['module_title_pnb'])}»۔ ایس قسط وچ ماڈیول دی پہچان، پنج مقصد، شروع دا نوٹ تے پہلا پورا تدریسی سیکشن نیں؛ مقصد باقی ماڈیول نوں وی آکھدے نیں، پر اوہ متن ایتھے ہجے شامل نہیں۔</p>
{before}{source_body}{after}
<p class="status" data-origin="renderer-ui">اگلا ضروری سیکشن <bdi dir="ltr" lang="en">Simplify Expressions Using the Order of Operations</bdi>، پہچان <bdi dir="ltr">fs-id1170654953465</bdi> اے۔ پورا ماڈیول، پوری کتاب تے پنجاں مقررہ کتاباں دا کم ہجے جاری اے۔</p></main>
<footer id="credits" lang="en" dir="ltr"><h2>Sources, credits and changes — A10-006</h2>
<p>Adapted from <a href="{attr(source_url)}">OpenStax Elementary Algebra 2e, module m82453: Use the Language of Algebra</a>, collection col31130, Foundations. Original senior contributing authors: Lynn Marecek; MaryAnne Anthony-Smith; Andrea Honeycutt Mathis. Source publisher: OpenStax / Rice University.</p>
<p>The existing A10 notice states <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International</a>, subject to component-specific credits and restrictions. This adaptation retains that framework and those restrictions. See the retained <a href="../provenance/A10-release/NOTICE.txt">A10 release notice</a>, <a href="../provenance/upstream--osbooks-prealgebra-bundle/LICENSE">canonical license text</a>, and <a href="../provenance/a10-unit-006-component-notices.json">selected component evidence</a>. Media authority rows establish source identity, not image-specific permission. No new clearance is asserted.</p>
<p>OpenStax and Rice University do not endorse this translation. Their names, logos and marks are not licensed by the source notice. No cover or added logo is reproduced. Four original JPEGs are byte-identical, unedited and unmirrored. The source MIME declarations remain image/jpeg, matching the admitted bytes. All four media objects are unnumbered; no source figure label was invented.</p>
<p>Changes: Shahmukhi Punjabi translation of 187 source-bound blocks across the complete original title/metadata, opening note and complete first section. All 134 original IDs, 98 exact MathML trees (737 MathML nodes), eight source tables with 41 rows/97 cells/15 actual header cells, 14 term IDs, five bold and 89 italic emphases, 48 source part labels, 12 explicit newlines, three internal table references, three worked examples and six Try It problem/solution pairs are retained. Thirty-two short parts are grouped for line wrapping; three long answer paragraphs and four table labels are not grouped. Three explicit source Solution titles render once; six untitled Try It solutions receive clearly generated UI labels.</p>
<p>The source explicitly teaches translation to and from English. Thirty-six source-key-bound panels retain the exact relevant canonical English lexical wording; they are not new exercises or answers. The one worked-answer echo omits four repeated formula trees because those exact source formulas already appear immediately in its source-bound translation. The original English variable+s suffix and the English mtext/ordinal lettering inside canonical MathML remain traceable.</p>
<p>The source operations summary, exponent factor wording and other scoped ambiguities are preserved in faithful translations. Separately labeled original explanations disclose them. One evidence-resolved image description and one table summary use separately declared accessible corrections while faithful source translations remain in data-source-alt/data-source-summary. Mathematics, source cells and image pixels are not silently repaired. Local table labels 1.2.1–1.2.3 are disclosed navigation labels, not canonical book numbering. No extra practice was added.</p>
<p>Indonesian comparison: <a href="https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id/releases/tag/v1.0.2">Elementary Algebra 2e Indonesian preservation release v1.0.2</a>. Its 82-module release and OpenAI Codex process provenance do not imply equivalent Punjabi coverage. This adaptation was produced with OpenAI Codex assistance at the user's direction; original human-contributor credits remain intact.</p>
<p>Coverage: module m82453 title/metadata, note fs-id1170654939047 and complete section fs-id1170655150800 through Try It fs-id1170655102894, last descendant fs-id1170655114560. Stop before fs-id1170654953465. This is not a complete module, textbook or five-work assignment and is not training or fine-tuning data. Native-language, educator and assistive-technology review remain pending. <a href="../source-excerpts/a10-unit-006.cnxml">Frozen source witness</a> · <a href="../source-excerpts/manifest-a10-006.json">Exact source selection</a>.</p>
</footer></body></html>
'''
    ids = OutputIDs()
    ids.feed(result)
    expected = manifest['source_ids_in_document_order']
    require([source_id for source_id in ids.ids if source_id in set(expected)] == expected,
            'Rendered source ID order changed')
    check_links(result)
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(result, encoding='utf-8', newline='\n')
    print('Built A10-006:187blocks,134IDs,98exactMathML,8tables/97cells,4originalJPEGs,36Englishlexicalechoes.')


if __name__ == '__main__':
    build()
