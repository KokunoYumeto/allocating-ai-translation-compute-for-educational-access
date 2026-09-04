"""Independent CNXML-derived A10-005 QA. Never imports renderer expected DOM."""
import ast
import copy
import csv
import hashlib
import json
import math
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
C = 'http://cnx.rice.edu/cnxml'
M = 'http://www.w3.org/1998/Math/MathML'
READER = BASE / 'reader/a10-unit-005.html'
RECEIPT = BASE / 'qa/structural-a10-005.json'
BAD = re.compile('[\u0a00-\u0a7f\u061c\u200e\u200f\u202a-\u202e\u2066-\u2069\ufffd]')
NUM = re.compile(r'\d+(?:,\d{3})*(?:\.\d+)?')
MAPPED = {'document', 'title', 'metadata', 'content-id', 'abstract', 'para', 'list', 'item', 'uuid',
          'content', 'section', 'exercise', 'problem', 'solution', 'media', 'image', 'glossary',
          'definition', 'term', 'meaning'}
CONTAINERS = {'document', 'metadata', 'abstract', 'content', 'section', 'exercise', 'problem',
              'solution', 'glossary', 'definition', 'list', 'media'}
LONG = {'fs-id1170655207108', 'fs-id1170655207128'}


def tag(node):
    return node.tag.rsplit('}', 1)[-1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    return digest(Path(path).read_bytes())


def shape(node):
    return (node.tag, tuple(sorted(node.attrib.items())), node.text,
            tuple((shape(child), child.tail) for child in node))


def inner(node):
    return node.text, tuple((shape(child), child.tail) for child in node)


def text(node):
    return ''.join(node.itertext())


def flat(value):
    return re.sub(r'\s+', ' ', value).strip()


def parsed(value):
    return ET.fromstring('<fragment>' + value + '</fragment>')


def numerals(value):
    return NUM.findall(value)


def numbers(value):
    return [int(n.replace(',', '')) for n in numerals(value)]


def element(tag_name, attrs=None, value=None):
    e = ET.Element(tag_name, attrs or {})
    e.text = value
    return e


def parents(root):
    return {child: parent for parent in root.iter() for child in parent}


def unwrap(parent, child):
    position = list(parent).index(child)
    before = parent.text if position == 0 else parent[position - 1].tail
    if child.text:
        if position == 0:
            parent.text = (before or '') + child.text
        else:
            parent[position - 1].tail = (before or '') + child.text
    additions = list(child)
    parent.remove(child)
    for offset, addition in enumerate(additions):
        parent.insert(position + offset, addition)
    if additions:
        additions[-1].tail = (additions[-1].tail or '') + (child.tail or '') or None
    elif position:
        parent[position - 1].tail = (parent[position - 1].tail or '') + (child.tail or '') or None
    else:
        parent.text = (parent.text or '') + (child.tail or '') or None


def delete_preserving_tail(parent, child):
    index = list(parent).index(child)
    if child.tail:
        if index:
            parent[index - 1].tail = (parent[index - 1].tail or '') + child.tail
        else:
            parent.text = (parent.text or '') + child.tail
    parent.remove(child)


def nonmath_text(node):
    clone = copy.deepcopy(node)
    for owner in clone.iter():
        for child in list(owner):
            if child.tag == '{' + M + '}math':
                child[:] = []
                child.text = None
    return text(clone)


def css_literal(path, combined=False):
    module = ast.parse(path.read_text(encoding='utf-8'))
    assign = next(n for n in module.body if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == 'LOCAL_CSS' for t in n.targets))
    return ast.literal_eval(assign.value.right if combined else assign.value)


class Failure(AssertionError):
    pass


class Context:
    def __init__(self):
        self.manifest_path = BASE / 'source-excerpts/manifest-a10-005.json'
        self.manifest = json.loads(self.manifest_path.read_text(encoding='utf-8'))
        self.translation_path = BASE / 'translations/a10-unit-005.json'
        self.translation = json.loads(self.translation_path.read_text(encoding='utf-8'))
        self.canonical_path = ROOT / self.manifest['canonical_local_path']
        self.canonical = ET.parse(self.canonical_path).getroot()
        self.source = copy.deepcopy(self.canonical)
        content = self.source.find('{' + C + '}content')
        if len(content) != 8 or content[7].get('id') != 'fs-id1170655190123':
            raise Failure('canonical_contiguous_final_scope')
        for node in list(content)[:7]:
            content.remove(node)
        self.source.set('id', 'a10-unit-005-excerpt')
        self.excerpt_path = BASE / 'source-excerpts/a10-unit-005.cnxml'
        self.excerpt = ET.parse(self.excerpt_path).getroot()
        self.parent = parents(self.source)
        self.paths = {}
        def walk(node, path):
            self.paths[path] = node
            for index, child in enumerate(node):
                walk(child, path + '/' + str(index))
        walk(self.source, 'document')
        self.node_paths = {node: path for path, node in self.paths.items()}
        self.mapped = {path: node for path, node in self.paths.items() if tag(node) in MAPPED}
        self.blocks = {}
        for node in self.source.iter():
            name = tag(node)
            parent = self.parent.get(node)
            if name == 'title':
                key = 'm82452/title' if parent is self.source else 'm82452/metadata/title' if tag(parent) == 'metadata' else parent.get('id') + '/title'
            elif name in {'para', 'meaning'}:
                key = node.get('id')
            elif name == 'item':
                key = parent.get('id') + '/item/' + str(list(parent).index(node) + 1)
            elif name == 'term':
                key = parent.get('id') + '/term'
            elif name == 'media':
                key = node.get('id') + '/alt'
            else:
                continue
            self.blocks[key] = node
        self.keys = {node: key for key, node in self.blocks.items()}
        self.ids = [n.get('id') for n in self.source.iter() if n is not self.source and n.get('id')]
        self.exercises = [n for n in self.source.iter() if tag(n) == 'exercise']
        self.labels = {n.get('id'): str(i) for i, n in enumerate(self.exercises, 1)}
        self.advisories = {}
        for row in self.translation['source_corrections']:
            for key in row['source_keys']:
                self.advisories.setdefault(key, []).append(row['note_id'])
        self.notices_path = BASE / 'provenance/a10-unit-005-component-notices.json'
        self.css = ((BASE / 'styles/reader.css').read_text(encoding='utf-8')
                    + css_literal(BASE / 'scripts/build_a10.py')
                    + css_literal(BASE / 'scripts/build_a10_005.py', True))
        self.input_paths = {
            self.canonical_path, self.excerpt_path, self.manifest_path, self.translation_path,
            BASE / 'sources.lock.json', BASE / 'styles/reader.css', BASE / 'scripts/build_a10.py',
            BASE / 'scripts/prepare_a10.py', BASE / 'scripts/build_a10_005.py',
            BASE / 'scripts/prepare_a10_005.py', Path(__file__).resolve(),
            BASE / 'qa/a10-unit-005-language-notes.md', BASE / 'plans/A10-005-scope.json',
            ROOT / self.manifest['indonesian_comparison_path'], ROOT / self.manifest['media_authority_manifest_path']
        }
        self.input_paths.update(ROOT / n['path'] for n in self.manifest['existing_notice_inputs'])
        self.input_paths.update(ROOT / n['canonical_local_path'] for n in self.manifest['images'])
        self.input_paths.update(BASE / n['path'] for n in self.manifest['canon_consultations'])
        self.input_paths.update(ROOT / n['path'] for n in self.manifest['canon_source_files'])
        self.input_paths.add(BASE / self.manifest['supplemental_number_word_reading']['path'])


class Validator:
    def __init__(self, context):
        self.c = context
        self.checks = Counter()

    def check(self, condition, name):
        self.checks[name] += 1
        if not condition:
            raise Failure(name)

    def validate_inputs(self):
        c, m, t = self.c, self.c.manifest, self.c.translation
        self.check((m['unit'], m['module'], m['collection'], t['locale']) == ('A10-005', 'm82452', 'col31130', 'pnb-Arab-PK'), 'scope_identity')
        lock = json.loads((BASE / 'sources.lock.json').read_text(encoding='utf-8'))
        pin = next(r for r in lock['repositories'] if r['role'] == 'A10+A20 upstream')
        self.check((pin['commit'], pin['tree']) == (m['commit'], m['tree']), 'unchanged_locked_commit')
        raw = c.canonical_path.read_bytes()
        self.check(len(raw) == m['full_module_bytes'] and digest(raw) == m['full_module_sha256'], 'canonical_bytes')
        self.check(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == m['canonical_git_blob_sha1'], 'canonical_git_blob')
        self.check(shape(c.source) == shape(c.excerpt), 'exact_full_selected_source_tree')
        self.check(file_hash(c.excerpt_path) == m['excerpt_sha256'] and c.excerpt_path.stat().st_size == m['excerpt_bytes'], 'frozen_excerpt_bytes')
        self.check(file_hash(c.translation_path) == m['translation_sha256'] and c.translation_path.stat().st_size == m['translation_bytes'], 'frozen_translation_bytes')
        for witness in m['source_byte_witnesses']:
            data = raw[witness['start_byte']:witness['end_byte_exclusive']]
            self.check(len(data) == witness['bytes'] and digest(data) == witness['sha256'], 'original_byte_range')
        self.check(c.ids == m['source_ids_in_document_order'] and len(c.ids) == len(set(c.ids)) == 383, 'all_source_ids')
        self.check(list(c.blocks) == list(t['source_blocks']) == m['source_block_keys_in_document_order'] and len(c.blocks) == 181, 'all_source_keys')
        self.check(len(list(c.source.iter())) == 624, 'all_selected_elements')
        self.check([tag(n) for n in c.source] == ['title', 'metadata', 'content', 'glossary'], 'complete_root_context')
        self.check(len(c.exercises) == 82 and sum(tag(n) == 'solution' for n in c.source.iter()) == 41, 'source_questions_and_optional_answers')
        self.check(sum(tag(n) == 'definition' for n in c.source.iter()) == 11, 'source_glossary_extent')
        self.check(sum(n.tag == '{' + M + '}math' for n in c.source.iter()) == 12, 'source_math_extent')
        self.check(sum(tag(n) == 'newline' for n in c.source.iter()) == 5, 'source_newline_extent')
        self.check(sum(tag(n) == 'span' and n.get('class') == 'token' for n in c.source.iter()) == 116, 'source_part_extent')
        self.check(not any(tag(n) in {'table', 'figure', 'link'} for n in c.source.iter()), 'source_has_no_table_figure_link')
        self.check(t['source_corrections'] == m['source_discrepancies'] and not t['image_alt_overrides'] and not t['table_summary_overrides'], 'original_qualifications_not_silent_overrides')
        self.check(not BAD.search(c.translation_path.read_text(encoding='utf-8')), 'target_script_controls')
        self.check(not any(t[k] for k in ('whole_module_complete', 'whole_book_complete', 'whole_assignment_complete')), 'coverage_claims_bounded')
        comparison = ROOT / m['indonesian_comparison_path']
        self.check(file_hash(comparison) == m['indonesian_comparison_sha256'], 'pinned_indonesian_comparison')
        for row in m['canon_consultations']:
            path = BASE / row['path']
            rec = json.loads(path.read_text(encoding='utf-8'))
            self.check(file_hash(path) == row['sha256'] and rec['stage'] == row['stage']
                       and [r['id'] for r in rec['examples']] == row['ids'], 'actual_canon_receipt')
        self.check({r['stage'] for r in m['canon_consultations']} == {'next-unit', 'draft', 'revision', 'qa'}, 'all_canon_stages')
        for row in m['canon_source_files']:
            self.check(file_hash(ROOT / row['path']) == row['sha256'], 'canon_file_identity')
        row = m['supplemental_number_word_reading']
        self.check(file_hash(BASE / row['path']) == row['sha256'], 'supplement_observation_identity')

    def basic_attrs(self, source):
        result = {'data-source-tag': tag(source), 'data-source-path': self.c.node_paths[source],
                  'data-source-qname': source.tag,
                  'data-source-attributes': json.dumps(source.attrib, ensure_ascii=False, sort_keys=True, separators=(',', ':'))}
        if source.get('id'):
            result['id'] = source.get('id')
        return result

    def check_ui(self, dom, owner, label=None):
        name = tag(owner)
        if name == 'exercise':
            expected = parsed('<h3 class="exercise-label" data-origin="renderer-ui" data-exercise-label="' + label
                              + '">مشق <bdi dir="ltr">' + label + '</bdi></h3>')[0]
        elif name == 'solution':
            expected = parsed('<p class="solution-label" data-origin="renderer-ui">حل</p>')[0]
        elif name == 'metadata':
            expected = parsed('<h3 class="metadata-label" data-origin="renderer-ui">ماخذ دی پہچان تے سِکھن دے مقصد</h3>')[0]
        elif name == 'glossary':
            expected = parsed('<h2 class="glossary-label" data-origin="renderer-ui">اصطلاحاں دے مطلب</h2>')[0]
        else:
            raise Failure('unexpected_source_ui_owner')
        self.check(shape(dom) == shape(expected) and not (dom.tail or '').strip(), 'source_ui_exact_and_owner_bound')

    def expected_advisory(self, key):
        links = '؛ '.join('<a href="#' + i + '">مترجم دی وکھری وضاحت</a>' for i in self.c.advisories[key])
        return parsed('<p class="source-original-advisory" data-origin="renderer-ui" data-source-advisory-for="'
                      + key + '">ایس ماخذی گل نال ' + links + ' وی پڑھو۔</p>')[0]

    def expected_part_groups(self, fragment, source):
        children = list(fragment)
        labels = [i for i, n in enumerate(children) if n.tag == 'bdi' and re.fullmatch(r'\([a-e]\)', n.text or '')]
        tokens = [n.text for n in source if tag(n) == 'span' and n.get('class') == 'token']
        self.check([children[i].text for i in labels] == ['(' + chr(ord('a') + ord(s) - ord('ⓐ')) + ')' for s in tokens], 'translation_part_correspondence')
        groups = []
        for number, start in enumerate(labels):
            stop = labels[number + 1] if number + 1 < len(labels) else len(children)
            while stop > start and children[stop - 1].tag == 'br':
                stop -= 1
            group = element('span', {'class': 'source-inline-part', 'data-source-part': children[start].text[1]})
            for child in children[start:stop]:
                group.append(copy.deepcopy(child))
            group[-1].tail = (group[-1].tail or '').rstrip() or None
            groups.append(group)
        return groups

    def validate_leaf(self, source, dom):
        c = self.c
        key = c.keys[source]
        expected = parsed(re.sub(r'\{\{math:(\d+)\}\}', r'<source-math-slot data-index="\1" />', c.translation['source_blocks'][key]))
        actual = copy.deepcopy(dom)
        maths = [n for n in source if n.tag == '{' + M + '}math']
        math_spans = [n for n in actual.iter('span') if n.get('class') == 'math-isolate']
        self.check(len(math_spans) == len(maths), 'math_owner_and_count')
        amap = parents(actual)
        for index, (span, original) in enumerate(zip(math_spans, maths)):
            self.check(span.attrib == {'class': 'math-isolate', 'dir': 'ltr'} and len(span) == 1
                       and span.text is None and span[0].tail is None, 'math_isolate_structure')
            copied = copy.deepcopy(span[0])
            self.check(copied.tag == original.tag and copied.get('dir') == 'ltr', 'math_ltr')
            self.check(set(copied.attrib) == set(original.attrib) | {'dir'}, 'math_no_edit_ledger_or_extra_attrs')
            copied.attrib.pop('dir')
            self.check(shape(copied) == shape(original), 'exact_math_tree_and_text')
            slot = element('source-math-slot', {'data-index': str(index)})
            slot.tail = span.tail
            parent = amap[span]
            parent[list(parent).index(span)] = slot
        groups = [n for n in actual.iter('span') if n.get('class') == 'source-inline-part']
        expected_groups = self.expected_part_groups(expected, source) if key not in LONG else []
        self.check(len(groups) == len(expected_groups), 'short_parts_only_not_long_selfcheck')
        for group, original in zip(groups, expected_groups):
            self.check(group in list(actual), 'part_group_direct_paragraph_child')
            self.check(shape(group) == shape(original), 'complete_part_bounds_and_marker')
            self.check(not list(group.iter('br')), 'newlines_outside_part_groups')
            unwrap(actual, group)
        self.check(inner(actual) == inner(expected), 'exact_translated_leaf_text_children_tails')
        source_numbers = numerals(nonmath_text(source))
        target_numbers = numerals(re.sub(r'\{\{math:\d+\}\}', '', text(parsed(c.translation['source_blocks'][key]))))
        self.check(Counter(source_numbers) == Counter(target_numbers), 'source_prose_numeric_multiset')
        if key == 'fs-id1170655194334':
            self.check(source_numbers == ['1,339,724,852', '1', '2010']
                       and target_numbers == ['1', '2010', '1,339,724,852'], 'declared_date_fronting_only')
        else:
            self.check(source_numbers == target_numbers, 'source_numeric_order')
        self.check(sum(tag(n) == 'newline' for n in source) == len(list(actual.iter('br'))), 'source_break_count')
        for effect, html_tag in [('bold', 'strong'), ('italics', 'em')]:
            self.check(sum(tag(n) == 'emphasis' and n.get('effect') == effect for n in source)
                       == len(list(actual.iter(html_tag))), 'source_emphasis_count')
        amap = parents(actual)
        for n in actual.iter():
            for value, parent in ((n.text, n), (n.tail, amap.get(n))):
                if not value or not re.search(r'[A-Za-z0-9$]', value):
                    continue
                isolated = False
                while parent is not None:
                    if parent.tag == 'bdi' and parent.get('dir') == 'ltr':
                        isolated = True
                        break
                    parent = amap.get(parent)
                self.check(isolated, 'source_english_numbers_dollars_isolated')

    def validate_dom(self, dom):
        c, m, t = self.c, self.c.manifest, self.c.translation
        self.check(dom.tag == 'html' and dom.attrib == {'lang': 'pnb-Arab-PK', 'dir': 'rtl'}, 'locale_rtl_root')
        self.check([n.tag for n in dom] == ['head', 'body'], 'exact_root_frame')
        self.check(not (dom.text or '').strip() and all(not (n.tail or '').strip() for n in dom), 'root_no_anonymous_text')
        head, body = list(dom)
        self.check([n.tag for n in head] == ['meta', 'meta', 'meta', 'title', 'style'], 'head_no_extra_nodes')
        self.check(not head.attrib and not (head.text or '').strip() and all(not (n.tail or '').strip() for n in head), 'head_no_anonymous_text')
        self.check(all(not len(n) for n in head) and not head[3].attrib and not head[4].attrib, 'head_leaf_attributes')
        self.check(head[0].attrib == {'charset': 'utf-8'} and head[1].attrib == {'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}, 'encoding_mobile_viewport')
        self.check(head[3].text == t['title'] + ' — A10-005', 'page_title')
        self.check(head[4].text == c.css and not len(head[4]), 'exact_stylesheet_inputs')
        self.check('.a10-005-reader .source-media .scroll-hint { direction:rtl; white-space:normal;' in c.css
                   and '.a10-005-reader .source-inline-part { white-space:nowrap;' in c.css
                   and '[data-long-source-part=true] { white-space:normal;' in c.css, 'unit_wrapping_direction_guards')
        self.check(body.attrib == {'class': 'a10-reader a10-005-reader'} and [n.tag for n in body] == ['header', 'main', 'footer'], 'body_exact_frame')
        self.check(not (body.text or '').strip() and all(not (n.tail or '').strip() for n in body), 'body_no_anonymous_text')
        header, main, footer = list(body)
        self.check([n.tag for n in header] == ['p', 'h1', 'p', 'p', 'nav'] and not header.attrib, 'header_exact_frame')
        self.check([n.attrib for n in header] == [{'class': 'eyebrow'}, {}, {}, {'class': 'status'}, {'aria-label': 'سبق دے حصے'}], 'header_exact_attributes')
        self.check(not (header.text or '').strip() and all(not (n.tail or '').strip() for n in header), 'header_no_anonymous_text')
        self.check(header[1].text == t['title'] and not len(header[1]) and header[2].text == t['subtitle'], 'header_translation_metadata')
        self.check(text(header[0]) == 'A10-005 · A10 / col31130 / m82452'
                   and header[0][0].attrib == {'dir': 'ltr'}, 'header_source_identity')
        self.check(text(header[3]) == 'ابتدائی ترجمہ · پنجابی دے ماہر تے ریاضی دے استاد دی جانچ ہن تک نہیں ہوئی۔', 'header_native_review_pending')
        nav_hrefs = [n.get('href') for n in header[4]]
        self.check(nav_hrefs == ['a10-unit-004.html', '#fs-id1170655190123', '#fs-id1166426314283', '#a10-005-original-bridge', '#credits'], 'previous_and_internal_navigation')
        self.check(len(main) == 5 and not main.attrib and not (main.text or '').strip()
                   and all(not (n.tail or '').strip() for n in main), 'main_exact_frame_no_anonymous_text')
        expected_label = parsed('<p class="source-label" data-origin="renderer-ui">ماخذ: <bdi dir="ltr" lang="en">OpenStax Elementary Algebra 2e</bdi>، باب <bdi dir="ltr" lang="en">Foundations</bdi>، سبق «'
                                + m['module_title_pnb'] + '»۔ ایس قسط وچ سبق دیاں ساریاں مشقاں، کتاب وچ دِتے حل، اپنی پرکھ، اصطلاحاں تے ماڈیول دے مقصد تے پہچان نیں؛ پچھلا تدریسی متن الگ قسطاں وچ اے۔</p>')[0]
        expected_status = parsed('<p class="status" data-origin="renderer-ui">اگلا ماڈیول <bdi dir="ltr" lang="en">m82453</bdi> اے۔ پنجاں مقررہ کتاباں دا پورا کم ہن وی جاری اے؛ ایہہ پوری کتاب دے مکمل ترجمے دا دعویٰ نہیں۔</p>')[0]
        self.check(shape(main[0]) == shape(expected_label) and shape(main[4]) == shape(expected_status), 'main_original_ui_exact')
        self.check(shape(main[1]) == shape(ET.fromstring(t['bridge_before_html']))
                   and shape(main[3]) == shape(ET.fromstring(t['bridge_after_html'])), 'original_bridges_exact_and_separate')
        frame = main[2]
        self.check(frame.get('data-source-path') == 'document', 'source_document_frame')
        mapped_nodes = [n for n in dom.iter() if n.get('data-source-path') is not None]
        paths = [n.get('data-source-path') for n in mapped_nodes]
        self.check(paths == list(c.mapped) and len(paths) == len(set(paths)), 'all_source_paths_in_order')
        by_path = dict(zip(paths, mapped_nodes))
        self.by_key = {n.get('data-source-key'): n for n in dom.iter() if n.get('data-source-key')}
        key_list = [n.get('data-source-key') for n in dom.iter() if n.get('data-source-key')]
        self.check(key_list == list(c.blocks) and len(self.by_key) == len(c.blocks), 'all181source_blocks_once_in_order')
        all_ids = [n.get('id') for n in dom.iter() if n.get('id')]
        self.check(len(all_ids) == len(set(all_ids)) and [i for i in all_ids if i in set(c.ids)] == c.ids, 'all383rendered_source_ids_in_order')
        parent_map = parents(dom)
        for path, source in c.mapped.items():
            node = by_path[path]
            name = tag(source)
            attrs = self.basic_attrs(source)
            if name in CONTAINERS:
                attrs['class'] = 'source-' + name
                html_tag = 'section' if name in {'metadata', 'section', 'exercise', 'solution', 'glossary', 'definition'} else 'div'
                if name == 'list':
                    attrs.update({'class': 'source-objectives', 'role': 'list'})
                    html_tag = 'ul'
                if name == 'media':
                    attrs['data-source-child'] = source.get('id')
            elif name in {'content-id', 'uuid'}:
                attrs.update({'class': 'source-retained-metadata', 'aria-label': 'ماخذ دے ماڈیول دی پہچان' if name == 'content-id' else 'ماخذ دی مستقل پہچان'})
                html_tag = 'p'
                expected = parsed('<bdi dir="ltr" lang="en">' + (source.text or '') + '</bdi>')
                self.check(inner(node) == inner(expected), 'exact_retained_metadata_value')
            elif name == 'image':
                spec = m['images'][0]
                media = c.parent[source]
                key = media.get('id') + '/alt'
                faithful = t['source_blocks'][key]
                attrs.update({'data-source-key': key, 'src': '../' + spec['path'], 'alt': faithful,
                              'data-source-alt': faithful, 'data-description-origin': 'source-translation',
                              'data-source-image-mime': source.get('mime-type'), 'data-rendered-image-mime': 'image/jpeg',
                              'width': str(spec['width']), 'height': str(spec['height']),
                              'style': '--source-width:' + str(spec['width']) + 'px',
                              'aria-describedby': t['retained_image_keys'][key]})
                html_tag = 'img'
                self.check(not len(node) and node.text is None, 'unchanged_void_source_image')
            else:
                key = c.keys[source]
                attrs['data-source-key'] = key
                if name == 'para':
                    attrs['class'] = 'source-para'
                if key in LONG:
                    attrs['data-long-source-part'] = 'true'
                if key in c.advisories:
                    attrs['aria-describedby'] = ' '.join(c.advisories[key])
                parent_name = tag(c.parent[source])
                html_tag = 'h2' if name == 'title' and parent_name in {'document', 'section'} else 'h3' if name in {'title', 'term'} else 'li' if name == 'item' else 'p'
                self.validate_leaf(source, node)
            self.check(node.tag == html_tag and node.attrib == attrs, 'source_node_exact_tag_attributes')
            if source is not c.source:
                ancestor = parent_map.get(node)
                while ancestor is not None and ancestor.get('data-source-path') is None:
                    ancestor = parent_map.get(ancestor)
                self.check(ancestor is by_path[c.node_paths[c.parent[source]]], 'source_parent_ancestry')
            if name not in CONTAINERS:
                continue
            projected = copy.deepcopy(node)
            if name in {'exercise', 'solution', 'metadata', 'glossary'}:
                self.check(len(projected) > 0, 'required_source_ui_present')
                self.check_ui(projected[0], source, c.labels.get(source.get('id')))
                delete_preserving_tail(projected, projected[0])
            for wrapper in list(projected):
                if wrapper.get('class') != 'source-block-container':
                    continue
                key = wrapper.get('data-source-block-owner')
                self.check(key in c.advisories and wrapper.attrib == {'class': 'source-block-container', 'data-source-block-owner': key}
                           and wrapper.text is None and len(wrapper) == 2, 'advisory_wrapper_bound')
                self.check(wrapper[0].get('data-source-key') == key and wrapper[0].tail is None
                           and shape(wrapper[1]) == shape(self.expected_advisory(key)) and wrapper[1].tail is None, 'visible_original_advisory_exact')
                wrapper.remove(wrapper[1])
                unwrap(projected, wrapper)
            if name == 'media':
                spec = m['images'][0]
                key = source.get('id') + '/alt'
                target = t['retained_image_keys'][key]
                self.check(len(projected) == 2 and projected[0].attrib == {
                    'class': 'figure-scroll', 'dir': 'ltr', 'tabindex': '0', 'role': 'region',
                    'aria-label': 'اصل پرکھ فہرست؛ لوڑ پئے تے پاسے سرکاؤ'}, 'image_local_scroller_structure')
                expected_hint = parsed('<p class="scroll-hint" data-origin="renderer-ui" dir="rtl">چھوٹی سکرین اُتے پوری تصویر ویکھن لئی پاسے سرکاؤ، یا <a href="../'
                                       + spec['path'] + '">اصل تصویر وکھری کھولو</a>۔ <a href="#' + target
                                       + '">مترجم دی دو زبانی کنجی</a> وی ویکھو۔</p>')[0]
                self.check(shape(projected[1]) == shape(expected_hint) and projected[1].tail is None, 'image_hint_fallback_and_bilingual_key')
                projected.remove(projected[1])
                unwrap(projected, projected[0])
            self.check(projected.text == source.text, 'source_container_exact_text')
            self.check([n.get('data-source-path') for n in projected] == [c.node_paths[n] for n in source], 'source_container_exact_child_order_no_injection')
            self.check([n.tail for n in projected] == [n.tail for n in source], 'source_container_exact_tails')
        self.check(len(list(dom.iter('img'))) == 1 and not list(dom.iter('table')) and not list(dom.iter('figure')), 'only_original_image_no_invented_table_figure')
        self.check(not any(n.tag in {'script', 'iframe', 'object', 'embed', 'form', 'input', 'button'} for n in dom.iter()), 'no_runtime_or_invented_form')
        self.check(sum(n.tag == '{' + M + '}math' for n in dom.iter()) == 12, 'all_and_only12math_roots')
        self.check(len([n for n in frame.iter() if n.get('class') == 'source-inline-part']) == 114
                   and len([n for n in frame.iter() if n.get('data-long-source-part')]) == 2, '114short_two_long_groups')
        self.check(not BAD.search(ET.tostring(dom, encoding='unicode')) and '{{' not in ET.tostring(dom, encoding='unicode'), 'no_bad_script_controls_placeholders')
        self.validate_footer(footer)
        self.validate_links(dom)
        self.validate_answers()

    def validate_footer(self, footer):
        self.check(footer.attrib == {'id': 'credits', 'lang': 'en', 'dir': 'ltr'}
                   and [n.tag for n in footer] == ['h2'] + ['p'] * 7
                   and footer[0].text == 'Sources, credits and changes — A10-005', 'footer_frame_and_language')
        value = text(footer)
        required = ['Lynn Marecek', 'MaryAnne Anthony-Smith', 'Andrea Honeycutt Mathis',
                    'Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International',
                    'subject to component-specific credits and restrictions', 'No new clearance is asserted.',
                    'OpenStax and Rice University do not endorse', 'names, logos and marks are not licensed',
                    'not a standalone full-module translation', 'not training or fine-tuning data',
                    'Native-language, educator and assistive-technology review remain pending',
                    '41 supplied solutions', 'complete original title/metadata including content-id and UUID',
                    'eleven bold/two italic', 'twelve exact MathML', '116 source part labels', 'five explicit',
                    'No new practice or unsupplied source answer', 'OpenAI Codex assistance']
        for phrase in required:
            self.check(phrase in value, 'required_attribution_changes_limits')
        m = self.c.manifest
        expected_hrefs = [
            m['upstream_url'] + '/blob/' + m['commit'] + '/' + m['path'],
            'https://creativecommons.org/licenses/by-nc-sa/4.0/',
            '../provenance/A10-release/NOTICE.txt', '../provenance/upstream--osbooks-prealgebra-bundle/LICENSE',
            '../provenance/a10-unit-005-component-notices.json',
            'https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id/releases/tag/v1.0.2',
            '../source-excerpts/a10-unit-005.cnxml', '../source-excerpts/manifest-a10-005.json',
            '../qa/a10-unit-005-language-notes.md']
        self.check([n.get('href') for n in footer.iter('a')] == expected_hrefs, 'exact_attribution_destinations')
        self.check(all(n.tag in {'footer', 'h2', 'p', 'a'} for n in footer.iter()), 'footer_no_extra_structures')

    def validate_links(self, dom):
        ids = {n.get('id') for n in dom.iter() if n.get('id')}
        self.local_paths = set()
        for n in dom.iter():
            if n.get('aria-describedby'):
                self.check(set(n.get('aria-describedby').split()) <= ids, 'aria_description_targets')
            for key in ('href', 'src'):
                if key not in n.attrib:
                    continue
                value = n.get(key)
                url = urlsplit(value)
                if url.scheme or url.netloc:
                    self.check(url.scheme in {'http', 'https'}, 'safe_reference_scheme')
                    continue
                if url.path:
                    path = (READER.parent / unquote(url.path)).resolve()
                    self.check(path.is_relative_to(BASE.resolve()) and path.is_file(), 'local_reference_exists')
                    self.local_paths.add(path)
                    if url.fragment:
                        other = path.read_text(encoding='utf-8')
                        self.check(re.search(r'\bid=["\']' + re.escape(unquote(url.fragment)) + r'["\']', other) is not None, 'cross_reader_fragment_exists')
                else:
                    self.check(unquote(url.fragment) in ids, 'local_fragment_exists')

    def validate_answers(self):
        c = self.c
        section = next(n for n in c.source.iter() if n.get('id') == 'fs-id1170655190123')
        self.answer_rows, self.written_values = [], []
        families = Counter()
        for subsection in section:
            instruction = ''
            for exercise in subsection:
                if tag(exercise) == 'para' and 'In the following' in text(exercise):
                    instruction = flat(text(exercise))
                if tag(exercise) != 'exercise':
                    continue
                problem = exercise.find('{' + C + '}problem')
                solution = exercise.find('{' + C + '}solution')
                prows = list(problem.iter('{' + C + '}para'))
                q = flat(text(problem))
                family = ''
                for phrase, kind in [
                    ('find the place value', 'place-value'), ('name each number using words', 'number-to-words'),
                    ('write each number as a whole number using digits', 'words-to-number'),
                    ('round', 'rounding'), ('divisibility tests', 'divisibility'),
                    ('prime factorization', 'prime-factorization'),
                    ('least common multiple', 'lcm-prime-factors' if 'prime factors method' in instruction else 'lcm-listing-multiples')
                ]:
                    if phrase in instruction:
                        family = kind
                        break
                if subsection.get('class') in {'everyday', 'writing'}:
                    family = subsection.get('class')
                self.check(bool(family), 'source_exercise_family_derived')
                families[family] += 1
                if family == 'words-to-number':
                    value = word_value(q)
                    actual_value = word_value(text(self.by_key[prows[0].get('id')]), True)
                    self.check(actual_value == value, 'written_number_question_value')
                    self.written_values.append({'source_key': prows[0].get('id'), 'role': 'question', 'value': value})
                if solution is None:
                    continue
                source_answer = next(solution.iter('{' + C + '}para'))
                actual_answer = self.by_key[source_answer.get('id')]
                source_value = flat(text(source_answer))
                displayed = flat(text(actual_answer))
                values = None
                if family == 'place-value':
                    number = numbers(prows[0].text)[0]
                    digits = [numbers(n.tail)[0] for n in prows[0] if tag(n) == 'span']
                    powers = []
                    for digit in digits:
                        self.check(str(number).count(str(digit)) == 1, 'source_selected_digit_unambiguous')
                        powers.append(len(str(number)) - 1 - str(number).index(str(digit)))
                    english = ['ones', 'tens', 'hundreds', 'thousands', 'ten thousands', 'hundred thousands',
                               'millions', 'ten millions', 'hundred millions', 'billions', 'ten billions', 'hundred billions', 'trillions']
                    punjabi = ['اکائیاں', 'دہائیاں', 'سینکڑے', 'ہزاراں', 'دس ہزار', 'سو ہزار',
                               'ملیناں', 'دس ملین', 'سو ملین', 'بلیناں', 'دس بلین', 'سو بلین', 'ٹریلیناں']
                    source_parts = [flat(n.tail or '').rstrip('.,;') for n in source_answer if tag(n) == 'span']
                    target_parts = [re.sub(r'^\([a-e]\)\s*', '', flat(text(n))) for n in actual_answer
                                    if n.get('class') == 'source-inline-part']
                    self.check(source_parts == [english[i] for i in powers], 'source_place_values_recalculated')
                    self.check(target_parts == [punjabi[i] for i in powers], 'rendered_place_values_recalculated')
                    values = [10 ** i for i in powers]
                elif family == 'number-to-words':
                    value = numbers(q)[0]
                    self.check(word_value(source_value) == word_value(displayed, True) == value, 'number_to_words_value')
                    self.written_values.append({'source_key': source_answer.get('id'), 'role': 'solution', 'value': value})
                    values = [value]
                elif family == 'words-to-number':
                    values = [value]
                    self.check(numbers(source_value) == numbers(displayed) == values, 'words_to_number_answer')
                elif family == 'rounding':
                    if 'hundred, ⓑ thousand' in instruction:
                        places, ns = [100, 1000, 10000], numbers(q) * 3
                    else:
                        places, ns = [100 if 'nearest hundred' in q else 10] * 2, numbers(q)
                    values = [((n + p // 2) // p) * p for n, p in zip(ns, places)]
                    self.check(numbers(source_value) == numbers(displayed) == values, 'rounding_recalculated')
                elif family == 'divisibility':
                    number = numbers(q)[0]
                    values = [v for v in numbers(instruction) if number % v == 0]
                    self.check(numbers(source_value) == numbers(displayed) == values, 'divisibility_recalculated')
                elif family == 'prime-factorization':
                    original = [int(n.text) for n in solution.iter('{' + M + '}mn')]
                    values = [int(n.text) for n in actual_answer.iter('{' + M + '}mn')]
                    self.check(values == original and math.prod(values) == numbers(q)[0], 'prime_product_recalculated')
                    self.check(all(n > 1 and all(n % d for d in range(2, math.isqrt(n) + 1)) for n in values), 'every_factor_prime')
                elif family.startswith('lcm-'):
                    values = [math.lcm(*numbers(q))]
                    self.check(numbers(source_value) == numbers(displayed) == values, 'lcm_recalculated')
                elif family == 'everyday':
                    if q.startswith('Writing a Check'):
                        value = numbers(q)[0]
                        self.check(word_value(source_value) == word_value(displayed, True) == value, 'check_price_words_value')
                        self.written_values.append({'source_key': source_answer.get('id'), 'role': 'solution', 'value': value})
                        values = [value]
                    elif q.startswith('Buying a Car'):
                        number = numbers(q)[0]
                        values = [((number + p // 2) // p) * p for p in (10, 100, 1000, 10000)]
                        self.check(numbers(source_value) == numbers(displayed) == values, 'price_rounding_recalculated')
                    elif q.startswith('Population'):
                        number = numbers(q)[0]
                        values = [((number + p // 2) // p) * p for p in (1000000000, 100000000, 1000000)]
                        self.check(numbers(source_value) == numbers(displayed) == values, 'population_rounding_recalculated')
                    elif q.startswith('Grocery Shopping'):
                        sizes = [numbers(q)[0], word_value(re.search(r'packs of ([A-Za-z-]+)', q)[1])]
                        values = [math.lcm(*sizes)]
                        self.check(numbers(source_value) == numbers(displayed) == values, 'equal_item_count_recalculated')
                    else:
                        raise Failure('unexpected_everyday_supplied_solution')
                elif family == 'writing':
                    self.check(source_value == 'Answers may vary.' and displayed == 'جواب وکھو وکھ ہو سکدے نیں۔', 'open_writing_answers_retained')
                self.answer_rows.append({'exercise_id': exercise.get('id'), 'solution_id': solution.get('id'),
                                         'source_key': source_answer.get('id'), 'family': family, 'values': values})
        self.check(len(self.answer_rows) == 41 and len(self.written_values) == 13, 'all41answers_and13word_values_checked')
        self.check(dict(families) == c.manifest['exercise_families'], 'source_family_totals')
        self.check(self.written_values == c.manifest['written_number_semantics'], 'word_value_manifest_matches_source')

    def validate_image_data(self, data, spec):
        self.check(digest(data) == spec['sha256'] and len(data) == spec['bytes'], 'image_exact_byte_digest')
        self.check(jpeg_dimensions(data) == (spec['width'], spec['height']) == (632, 166), 'original_jpeg_dimensions')
        self.check(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == spec['git_blob_sha1'], 'original_image_git_blob')

    def validate_notice(self, record):
        c, m = self.c, self.c.manifest
        expected_fields = {'schema', 'unit', 'work', 'module', 'collection', 'commit', 'manifest_sha256', 'excerpt_sha256',
                           'scope', 'existing_notice_inputs', 'existing_notice_hash_policy', 'release_notice_verbatim',
                           'existing_license_statement', 'rights_status', 'credit_limit', 'media_authority_manifest',
                           'images', 'whole_book_translation_complete', 'earlier_collection_items_not_covered_by_this_unit'}
        self.check(set(record) == expected_fields, 'notice_no_extra_unbound_fields')
        self.check(record['earlier_collection_items_not_covered_by_this_unit'] == m['earlier_collection_items_not_covered_by_this_unit'], 'notice_earlier_coverage_exact')
        self.check(record['schema'] == 'a10-retained-component-evidence-v1'
                   and (record['unit'], record['module'], record['collection'], record['commit'])
                   == ('A10-005', 'm82452', 'col31130', m['commit']), 'notice_scope_identity')
        self.check(record['work'] == 'OpenStax Elementary Algebra 2e'
                   and record['manifest_sha256'] == file_hash(c.manifest_path)
                   and record['excerpt_sha256'] == m['excerpt_sha256'], 'notice_source_binding')
        self.check(record['scope'] == 'One unchanged declared checklist image only; no new supply or license audit.'
                   and record['whole_book_translation_complete'] is False, 'notice_bounded_coverage')
        self.check(record['existing_notice_inputs'] == m['existing_notice_inputs']
                   and record['existing_notice_hash_policy'] == m['existing_notice_hash_policy'], 'notice_inputs_policy')
        for row in m['existing_notice_inputs']:
            self.check(digest((ROOT / row['path']).read_bytes().replace(b'\r\n', b'\n')) == row['sha256'], 'retained_notice_logical_lf')
        self.check(record['release_notice_verbatim'] == (BASE / 'provenance/A10-release/NOTICE.txt').read_text(encoding='utf-8'), 'release_notice_verbatim')
        self.check(record['existing_license_statement'] == 'Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International, subject to component-specific credits and restrictions.', 'notice_license_restrictions')
        self.check(record['rights_status'] == 'Existing audited A10 policy is retained. No new component-specific clearance determination is made.'
                   and record['credit_limit'] == 'Media authority rows identify bytes and Git blobs, not rights holders or permissions. Absence of an image-specific credit is not clearance.', 'notice_no_invented_clearance')
        authority_path = ROOT / m['media_authority_manifest_path']
        self.check(file_hash(authority_path) == m['media_authority_manifest_sha256']
                   and record['media_authority_manifest'] == {'path': m['media_authority_manifest_path'], 'sha256': m['media_authority_manifest_sha256']}, 'notice_authority_binding')
        with authority_path.open(encoding='utf-8-sig', newline='') as handle:
            rows = list(csv.DictReader(handle))
        image = next(n for n in c.source.iter() if tag(n) == 'image')
        media = c.parent[image]
        spec = m['images'][0]
        self.check(len(record['images']) == 1 and media.get('id') == spec['media_id']
                   and image.get('src') == spec['source_src'] and image.get('mime-type') == spec['declared_mime'] == 'image/jpeg', 'source_image_association_and_mime')
        source = (c.canonical_path.parent / image.get('src')).resolve()
        target = (BASE / spec['path']).resolve()
        self.check(source == (ROOT / spec['canonical_local_path']).resolve()
                   and source.parent == (ROOT / 'downloads/complete-upstream/osbooks-prealgebra-bundle/media').resolve()
                   and target.parent == (BASE / 'assets/a10').resolve(), 'resolved_image_paths_scoped')
        self.validate_image_data(source.read_bytes(), spec)
        self.validate_image_data(target.read_bytes(), spec)
        matches = [r for r in rows if r['relative_path'] == spec['source_path']]
        self.check(len(matches) == 1 and matches[0] == spec['existing_media_authority_row'], 'existing_media_authority_row')
        row = record['images'][0]
        self.check(set(row) == {'figure_id', 'media_id', 'source_path', 'path', 'sha256', 'bytes', 'git_blob_sha1',
                               'width', 'height', 'source_declared_mime', 'actual_mime', 'source_english_alt',
                               'existing_media_authority_row', 'treatment', 'component_clearance'}, 'notice_image_no_extra_fields')
        for key in ('figure_id', 'media_id', 'source_path', 'path', 'sha256', 'bytes', 'git_blob_sha1', 'width', 'height'):
            self.check(row[key] == spec[key], 'notice_exact_image_field')
        self.check(row['source_english_alt'] == media.get('alt')
                   and row['source_declared_mime'] == image.get('mime-type') and row['actual_mime'] == 'image/jpeg'
                   and row['existing_media_authority_row'] == matches[0], 'notice_source_alt_mime_identity')
        self.check(row['component_clearance'] == 'Not newly assessed; subject to retained component-specific credits and restrictions.'
                   and row['treatment'] == 'Original JPEG bytes unchanged and unmirrored; faithful Punjabi alt and explicitly original bilingual checklist key. No accessible source-error override is declared.', 'notice_component_limit_and_treatment')


def word_value(value, punjabi=False):
    if punjabi:
        value = re.sub(r'[\u064b-\u065f\u0670]', '', value)
        units = {'اک': 1, 'دو': 2, 'تن': 3, 'چار': 4, 'پنج': 5, 'چھے': 6, 'ست': 7, 'اٹھ': 8, 'نو': 9,
                 'دس': 10, 'گیاراں': 11, 'باراں': 12, 'پندراں': 15, 'ستاراں': 17, 'اٹھاراں': 18,
                 'چووی': 24, 'چھبی': 26, 'پینتی': 35, 'چھتی': 36, 'سینتیہہ': 37, 'چوتالی': 44,
                 'چھیالی': 46, 'ترونجا': 53, 'اکاہٹھ': 61, 'چونہٹھ': 64, 'ستاہٹھ': 67, 'اکہتر': 71,
                 'پچھتر': 75, 'اٹھہتر': 78, 'تراسی': 83, 'انانویں': 89, 'تریانویں': 93}
        scales = {'ہزار': 1000, 'ملین': 1000000, 'بلین': 1000000000, 'ٹریلین': 1000000000000}
        hundred = 'سو'
    else:
        value = value.lower()
        units = dict(zip('zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split(), range(20)))
        units.update(dict(zip('twenty thirty forty fifty sixty seventy eighty ninety'.split(), range(20, 100, 10))))
        scales = {'thousand': 1000, 'million': 1000000, 'billion': 1000000000, 'trillion': 1000000000000}
        hundred = 'hundred'
    total = group = 0
    for word in re.split(r'[\s,،.\-]+', value.strip()):
        if not word or word in {'dollars', 'and', 'ڈالر'}:
            continue
        if word in units:
            group += units[word]
        elif word == hundred:
            group *= 100
        elif word in scales:
            total += group * scales[word]
            group = 0
        else:
            raise Failure('unrecognized_written_number_token')
    return total + group


def jpeg_dimensions(data):
    if data[:2] != b'\xff\xd8':
        raise Failure('not_original_jpeg')
    i = 2
    while i < len(data):
        if data[i] != 255:
            raise Failure('jpeg_marker')
        while data[i] == 255:
            i += 1
        marker = data[i]
        i += 1
        if marker in {1, 0xd8, 0xd9} or 0xd0 <= marker <= 0xd7:
            continue
        length = int.from_bytes(data[i:i + 2], 'big')
        if length < 2 or i + length > len(data):
            raise Failure('jpeg_segment_length')
        if marker in {0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf}:
            return int.from_bytes(data[i + 5:i + 7], 'big'), int.from_bytes(data[i + 3:i + 5], 'big')
        i += length
    raise Failure('missing_jpeg_dimensions')


def by_key(dom, key):
    return next(n for n in dom.iter() if n.get('data-source-key') == key)


def by_id(dom, sid):
    return next(n for n in dom.iter() if n.get('id') == sid)


def detached_mutations(context, baseline):
    results = []

    def reject(name, mutate, target='dom'):
        validator = Validator(context)
        specimen = copy.deepcopy(baseline) if target == 'dom' else json.loads(context.notices_path.read_text(encoding='utf-8'))
        before = ET.tostring(specimen) if target == 'dom' else json.dumps(specimen, sort_keys=True)
        mutate(specimen)
        after = ET.tostring(specimen) if target == 'dom' else json.dumps(specimen, sort_keys=True)
        if before == after:
            raise Failure('mutation_was_noop:' + name)
        try:
            if target == 'dom':
                validator.validate_dom(specimen)
            else:
                validator.validate_notice(specimen)
        except Failure as error:
            results.append({'mutation': name, 'rejected_by': str(error), 'detached': True})
        else:
            raise Failure('mutation_not_rejected:' + name)

    reject('changed_prime_factor_number', lambda d: setattr(next(d.iter('{' + M + '}mn')), 'text', '3'))
    reject('changed_glossary_math_variable', lambda d: setattr(next(d.iter('{' + M + '}mi')), 'text', 'z'))
    reject('changed_English_math_and', lambda d: setattr(next(d.iter('{' + M + '}mtext')), 'text', 'or'))
    reject('math_RTL', lambda d: next(d.iter('{' + M + '}math')).set('dir', 'rtl'))
    reject('invented_punctuation_edit_ledger', lambda d: next(d.iter('{' + M + '}math')).set('data-source-text-edits', '[]'))
    reject('deleted_math_factor_node', lambda d: next(d.iter('{' + M + '}mrow')).remove(next(d.iter('{' + M + '}mrow'))[0]))
    reject('changed_UUID_value', lambda d: setattr(next(n for n in d.iter() if n.get('data-source-tag') == 'uuid')[0], 'text', '00000000-bb17-4b27-886f-08a966ee6c79'))
    reject('changed_module_content_id', lambda d: setattr(next(n for n in d.iter() if n.get('data-source-tag') == 'content-id')[0], 'text', 'm82453'))

    def drop_uuid(d):
        n = next(n for n in d.iter() if n.get('data-source-tag') == 'uuid')
        parents(d)[n].remove(n)
    reject('omitted_full_metadata_UUID', drop_uuid)

    def swap_metadata(d):
        node = next(n for n in d.iter() if n.get('data-source-tag') == 'metadata')
        node[1], node[2] = node[2], node[1]
    reject('reordered_metadata_children', swap_metadata)

    def drop_definition(d):
        n = next(n for n in d.iter() if n.get('data-source-tag') == 'definition')
        parents(d)[n].remove(n)
    reject('dropped_glossary_definition', drop_definition)
    reject('wrong_definition_term_pair', lambda d: setattr(by_key(d, 'fs-id1166421632702/term'), 'text', 'مرکب عدد'))
    reject('changed_rounding_answer', lambda d: setattr(next(n for n in by_key(d, 'fs-id1170655194779').iter('bdi') if n.text == '390'), 'text', '391'))
    reject('changed_population_number', lambda d: setattr(next(n for n in by_key(d, 'fs-id1170655194334').iter('bdi') if n.text == '1,339,724,852'), 'text', '1,339,724,853'))
    reject('wrong_written_number_word', lambda d: setattr(by_key(d, 'fs-id1170655227550'), 'text', 'اک ہزار، اُناسی'))

    def switch_solution(d):
        source_exercises = [n for n in d.iter() if n.get('data-source-tag') == 'exercise']
        solved = next(n for n in source_exercises if any(c.get('data-source-tag') == 'solution' for c in n))
        unsolved = next(n for n in source_exercises if not any(c.get('data-source-tag') == 'solution' for c in n))
        solution = next(n for n in solved if n.get('data-source-tag') == 'solution')
        solved.remove(solution)
        unsolved.append(solution)
    reject('supplied_solution_moved_to_unsolved_question', switch_solution)

    def invent_solution(d):
        unsolved = next(n for n in d.iter() if n.get('data-source-tag') == 'exercise'
                        and not any(c.get('data-source-tag') == 'solution' for c in n))
        unsolved.append(parsed('<section class="source-solution"><p><bdi dir="ltr">42</bdi></p></section>')[0])
    reject('invented_absent_source_answer', invent_solution)
    reject('removed_source_key_binding', lambda d: by_key(d, 'fs-id1170655227544').attrib.pop('data-source-key'))
    reject('wrong_source_part_label', lambda d: setattr(next(n for n in by_key(d, 'fs-id1170655205416').iter('bdi') if n.text == '(a)'), 'text', '(b)'))
    reject('wrong_short_part_marker', lambda d: next(n for n in by_key(d, 'fs-id1170655205416').iter('span') if n.get('data-source-part') == 'a').set('data-source-part', 'b'))

    def split_answer(d):
        n = next(n for n in by_key(d, 'fs-id1170655205482').iter('span') if n.get('data-source-part') == 'c')
        label = n[0]
        if label.tail != ' سو ہزار':
            raise Failure('split_mutation_precondition')
        label.tail = ' سو'
        n.tail = ' ہزار' + (n.tail or '')
    reject('split_hazaar_outside_answer_group_same_total_text', split_answer)

    def group_long(d):
        n = by_key(d, 'fs-id1170655207108')
        group = element('span', {'class': 'source-inline-part', 'data-source-part': 'a'})
        group.text = n.text
        n.text = None
        for child in list(n):
            n.remove(child)
            group.append(child)
        n.append(group)
    reject('nowrap_long_selfcheck_paragraph', group_long)

    def delete_break(d):
        n = by_key(d, 'fs-id1170655227507')
        br = next(n.iter('br'))
        delete_preserving_tail(parents(n)[br], br)
    reject('deleted_explicit_newline', delete_break)
    reject('invented_explicit_newline', lambda d: by_key(d, 'fs-id1170655227507').append(element('br')))

    def unwrap_bold(d):
        n = by_key(d, 'fs-id1170655190132')
        unwrap(n, n[0])
    reject('removed_source_bold', unwrap_bold)
    reject('changed_italic_n', lambda d: setattr(next(by_key(d, 'fs-id1166421632833').iter('bdi')), 'text', 'm'))
    reject('source_image_switched_to_other_asset', lambda d: next(d.iter('img')).set('src', '../assets/a10/CNX_ElemAlg_Figure_01_01_001_new.jpg'))
    reject('changed_image_dimensions', lambda d: next(d.iter('img')).set('width', '633'))
    reject('mirrored_image_style', lambda d: next(d.iter('img')).set('style', '--source-width:632px;transform:scaleX(-1)'))
    reject('changed_checklist_alt', lambda d: next(d.iter('img')).set('alt', 'تِن کالم'))
    reject('checklist_key_wrong_destination', lambda d: next(d.iter('img')).set('aria-describedby', 'a10-005-composite-scope'))

    def remove_advisory(d):
        n = next(n for n in d.iter() if n.get('data-source-advisory-for') == 'fs-id1166426314289')
        parents(d)[n].remove(n)
    reject('removed_visible_definition_qualification', remove_advisory)
    reject('silently_repaired_source_definition', lambda d: setattr(by_key(d, 'fs-id1166426314289'), 'text', 'مرکب عدد اک توں وڈا اے۔'))
    reject('source_container_anonymous_text', lambda d: setattr(by_id(d, 'fs-id1170655190127'), 'text', 'غیر ماخذی اضافہ'))

    def tail_injection(d):
        n = by_id(d, 'fs-id1170655190132')
        n.tail = (n.tail or '') + 'غیر ماخذی اضافہ'
    reject('source_container_anonymous_tail', tail_injection)
    reject('source_anonymous_isolated_paragraph', lambda d: by_id(d, 'fs-id1170655190127').append(parsed('<p><bdi dir="ltr">42</bdi></p>')[0]))
    reject('main_anonymous_isolated_paragraph', lambda d: d.find('body/main').append(parsed('<p><bdi dir="ltr">42</bdi></p>')[0]))
    reject('body_anonymous_isolated_paragraph', lambda d: d.find('body').append(parsed('<p><bdi dir="ltr">42</bdi></p>')[0]))
    reject('root_extra_head', lambda d: d.append(element('head')))
    reject('invented_CNXML_table_in_reader', lambda d: by_id(d, 'fs-id1170655190127').append(parsed('<table><tr><td>42</td></tr></table>')[0]))
    reject('wrong_generated_exercise_number', lambda d: setattr(next(n for n in d.iter() if n.get('class') == 'exercise-label')[0], 'text', '2'))
    reject('changed_original_bridge_note', lambda d: setattr(by_id(d, 'a10-005-composite-scope')[1], 'text', 'غیر ماخذی دعویٰ'))
    reject('RTL_hint_nowrap_CSS_regression', lambda d: setattr(d.find('head/style'), 'text', d.find('head/style').text.replace('direction:rtl; white-space:normal;', 'direction:ltr; white-space:nowrap;')))
    reject('notice_new_clearance_claim', lambda n: n.__setitem__('rights_status', 'All images newly cleared.'), 'notice')
    reject('notice_dropped_component_restrictions', lambda n: n.__setitem__('existing_license_statement', 'Unrestricted reuse.'), 'notice')
    reject('notice_wrong_source_alt', lambda n: n['images'][0].__setitem__('source_english_alt', 'Different source.'), 'notice')
    reject('notice_extra_clearance_field', lambda n: n.__setitem__('all_rights_cleared', True), 'notice')
    reject('hidden_native_review_warning', lambda d: d.find('body/header')[3].set('style', 'display:none'))
    image_data = bytearray((BASE / context.manifest['images'][0]['path']).read_bytes())
    image_data[-5] ^= 1
    try:
        Validator(context).validate_image_data(bytes(image_data), context.manifest['images'][0])
    except Failure as error:
        results.append({'mutation': 'changed_image_byte_in_memory', 'rejected_by': str(error), 'detached': True})
    else:
        raise Failure('image_byte_mutation_not_rejected')
    return results


def snapshot(paths):
    return {str(p.resolve()): file_hash(p) for p in sorted(paths, key=lambda n: str(n).lower())}


def artifact_record(path):
    record = {'path': path.relative_to(ROOT).as_posix(), 'bytes': path.stat().st_size, 'sha256': file_hash(path)}
    if path.suffix.lower() not in {'.jpg', '.jpeg', '.png'}:
        record['logical_lf_sha256'] = digest(path.read_bytes().replace(b'\r\n', b'\n'))
    return record


def main():
    context = Context()
    validator = Validator(context)
    input_before = snapshot(context.input_paths)
    validator.validate_inputs()
    cycles = []
    linked_inputs_before = None
    for cycle in (1, 2):
        for script in ('prepare_a10_005.py', 'build_a10_005.py'):
            result = subprocess.run([sys.executable, '-X', 'utf8', str(BASE / 'scripts' / script)],
                                    cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
            validator.check(result.returncode == 0, 'prepare_build_subprocess_success')
            if result.returncode:
                raise Failure(result.stdout + result.stderr)
        dom = ET.parse(READER).getroot()
        validator.validate_dom(dom)
        validator.validate_notice(json.loads(context.notices_path.read_text(encoding='utf-8')))
        linked_inputs = validator.local_paths - {READER, context.notices_path, BASE / context.manifest['images'][0]['path']}
        if linked_inputs_before is None:
            linked_inputs_before = snapshot(linked_inputs)
        validator.check(snapshot(linked_inputs) == linked_inputs_before, 'stable_linked_local_inputs')
        cycles.append({'cycle': cycle, 'reader_sha256': file_hash(READER), 'component_notices_sha256': file_hash(context.notices_path),
                       'image_sha256': file_hash(BASE / context.manifest['images'][0]['path'])})
    validator.check({r['reader_sha256'] for r in cycles} == {cycles[0]['reader_sha256']}
                    and len({r['component_notices_sha256'] for r in cycles}) == 1
                    and len({r['image_sha256'] for r in cycles}) == 1, 'two_build_cycles_deterministic')
    mutations = detached_mutations(context, dom)
    validator.check(snapshot(context.input_paths) == input_before, 'stable_input_hashes')
    artifact_paths = context.input_paths | {READER, context.notices_path, BASE / context.manifest['images'][0]['path']} | validator.local_paths
    mapped_count = len(context.mapped)
    math_nodes = sum(1 for n in context.source.iter() if n.tag.startswith('{' + M + '}'))
    record = {
        'schema': 'pnb-source-bound-structural-qa-v1', 'unit': 'A10-005', 'status': 'passed',
        'method': 'Canonical CNXML re-selection and independent source-path/parent/child/text/tail mapping; no renderer expected DOM import.',
        'counts': {
            'checks': sum(validator.checks.values()), 'source_blocks': len(context.blocks), 'source_ids': len(context.ids),
            'source_elements': len(list(context.source.iter())), 'mapped_structural_elements': mapped_count,
            'exact_mathml_elements': math_nodes, 'mathml_roots': 12, 'source_token_spans': 116,
            'source_emphases': 13, 'source_newlines': 5, 'short_part_groups': 114, 'long_selfcheck_parts': 2,
            'exercises': len(context.exercises), 'supplied_solutions': len(validator.answer_rows), 'unsupplied_solutions_not_invented': 41,
            'glossary_definitions': 11, 'original_images': 1, 'cnxml_tables': 0, 'numbered_figures': 0,
            'written_number_values': len(validator.written_values), 'detached_mutations': len(mutations)
        },
        'source_element_accounting': {'structural': mapped_count, 'MathML': math_nodes, 'circled_tokens': 116, 'emphases': 13, 'newlines': 5},
        'checks_by_name': dict(sorted(validator.checks.items())), 'build_cycles': cycles,
        'source_answer_checks': validator.answer_rows, 'written_number_values': validator.written_values,
        'detached_mutations': mutations,
        'artifacts': [artifact_record(p) for p in sorted(artifact_paths, key=lambda n: n.relative_to(ROOT).as_posix())],
        'artifact_hash_policy': 'sha256 is exact current bytes. logical_lf_sha256 is separately supplied for text; only existing notice pin comparison uses CRLF-to-LF normalization.',
        'limitations': [
            'Native-speaking Western Punjabi,mathematics-educator and assistive-technology review remain pending.',
            'Written-number checks validate the declared provisional lexical values,not native-language standardization.',
            'Root visual/browser review is separate; this receipt does not claim screenshot or human visual certification.',
            'Original checklist pixels were inspected during source/draft/revision/input QA; structural tests prove retained bytes and geometry metadata,not independent OCR.',
            'The checklist is a static image; no source HTML table or interactive form exists.',
            'Historical population/date and average distance are source exercise givens,not updated factual assertions.',
            'Source glossary domain shorthand remains faithful with separate original qualifications; no universal convention is asserted.',
            'Footer verifies required attribution/license/limits and link structure,not linguistic certification of every original editorial sentence.',
            'Complete-module source-union review across checkpoints and the full five-work workflow remain separate; no complete book claim.'
        ],
        'whole_book_translation_complete': False, 'whole_assignment_complete': False
    }
    validator.check(sum(record['source_element_accounting'].values()) == record['counts']['source_elements'], 'all624source_elements_accounted')
    record['checks_by_name'] = dict(sorted(validator.checks.items()))
    record['counts']['checks'] = sum(validator.checks.values())
    RECEIPT.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f"A10-005 QA passed: {record['counts']['checks']}checks,{len(mutations)}detached mutations,two deterministic build cycles.")
    print('Reader SHA256 ' + file_hash(READER))
    print('Receipt SHA256 ' + file_hash(RECEIPT))


if __name__ == '__main__':
    main()
