"""Independent CNXML-derived QA for A10-006. Does not import renderer expected DOM."""
import ast
import copy
import csv
import hashlib
import json
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
CURL = '{' + C + '}'
MURL = '{' + M + '}'
READER = BASE / 'reader/a10-unit-006.html'
RECEIPT = BASE / 'qa/structural-a10-006.json'
BAD = re.compile('[\u0a00-\u0a7f\u061c\u200e\u200f\u202a-\u202e\u2066-\u2069\ufffd]')
NUM = re.compile(r'\d+(?:,\d{3})*(?:\.\d+)?')
PLACEHOLDER = re.compile(r'\{\{[^}]+\}\}')
PARTS = {'ⓐ': 'a', 'ⓑ': 'b', 'ⓒ': 'c', 'ⓓ': 'd', 'ⓔ': 'e'}
LONG_PARTS = {'fs-id1166424795899', 'fs-id1170655353526', 'fs-id1170655222902'}
ENGLISH_ORIGIN = 'retained-canonical-English-words'


class Failure(AssertionError):
    pass


class Checker:
    def __init__(self):
        self.names = []

    def ok(self, condition, name):
        if not condition:
            raise Failure(name)
        self.names.append(name)


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
    return (node.text, tuple((shape(child), child.tail) for child in node))


def flat(value):
    return re.sub(r'\s+', ' ', value).strip()


def text(node):
    return ''.join(node.itertext())


def parents(root):
    return {child: parent for parent in root.iter() for child in parent}


def parse_reader(raw):
    return ET.fromstring(re.sub(r'<!doctype[^>]*>', '', raw, count=1, flags=re.I))


def parsed_fragment(value):
    return ET.fromstring('<fragment>' + value + '</fragment>')


def remove_preserving_tail(parent, child, replacement=''):
    index = list(parent).index(child)
    before = parent.text if index == 0 else parent[index - 1].tail
    combined = (before or '') + replacement + (child.tail or '')
    if index == 0:
        parent.text = combined or None
    else:
        parent[index - 1].tail = combined or None
    parent.remove(child)


def unwrap(parent, child):
    index = list(parent).index(child)
    before = parent.text if index == 0 else parent[index - 1].tail
    if child.text:
        if index == 0:
            parent.text = (before or '') + child.text
        else:
            parent[index - 1].tail = (before or '') + child.text
    additions = list(child)
    tail = child.tail
    parent.remove(child)
    for offset, addition in enumerate(additions):
        parent.insert(index + offset, addition)
    if additions:
        additions[-1].tail = (additions[-1].tail or '') + (tail or '') or None
    elif index:
        parent[index - 1].tail = (parent[index - 1].tail or '') + (tail or '') or None
    else:
        parent.text = (parent.text or '') + (tail or '') or None


def jpeg_dimensions(data):
    if data[:2] != b'\xff\xd8':
        raise Failure('asset_jpeg_signature')
    offset = 2
    while offset < len(data):
        if data[offset] != 255:
            raise Failure('asset_jpeg_marker')
        while offset < len(data) and data[offset] == 255:
            offset += 1
        marker = data[offset]
        offset += 1
        if marker in {1, 0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
            continue
        length = int.from_bytes(data[offset:offset + 2], 'big')
        if length < 2 or offset + length > len(data):
            raise Failure('asset_jpeg_length')
        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                      0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
            return (int.from_bytes(data[offset + 5:offset + 7], 'big'),
                    int.from_bytes(data[offset + 3:offset + 5], 'big'))
        if marker == 0xDA:
            raise Failure('asset_jpeg_frame_missing')
        offset += length
    raise Failure('asset_jpeg_truncated')


def logical_lf_hash(path):
    return digest(Path(path).read_bytes().replace(b'\r\n', b'\n'))


def math_fingerprint(node):
    payload = json.dumps(shape(node), ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    return digest(payload)


def nonmath_text(node):
    clone = copy.deepcopy(node)
    for owner in clone.iter():
        for child in list(owner):
            if child.tag == MURL + 'math':
                child[:] = []
                child.text = None
    return text(clone)


def source_lexical_fragment(node, omit_math):
    root = ET.Element('fragment')
    root.text = node.text
    def append(owner, target):
        for child in owner:
            name = tag(child)
            rendered = None
            if child.tag == MURL + 'math':
                if not omit_math:
                    raise Failure('english_echo_unexpected_math')
            elif name == 'emphasis':
                rendered = ET.Element('strong' if child.get('effect') == 'bold' else 'em')
                rendered.text = child.text
                append(child, rendered)
            elif name == 'term':
                rendered = ET.Element('span')
                rendered.text = child.text
                append(child, rendered)
            elif name == 'span' and child.get('class') == 'token':
                rendered = ET.Element('bdi', {'dir': 'ltr', 'data-english-source-part': PARTS[(child.text or '').strip()]})
                rendered.text = '(' + PARTS[(child.text or '').strip()] + ')'
            elif name == 'newline':
                rendered = ET.Element('br')
            else:
                raise Failure('english_echo_unsupported_source_inline_' + name)
            if rendered is not None:
                rendered.tail = child.tail
                target.append(rendered)
            elif child.tail:
                if len(target):
                    target[-1].tail = (target[-1].tail or '') + child.tail
                else:
                    target.text = (target.text or '') + child.tail
    append(node, root)
    return root


def derive_source_key(node, parent, module):
    name = tag(node)
    if name == 'title':
        if tag(parent) == 'document':
            return module + '/title'
        if tag(parent) == 'metadata':
            return module + '/metadata/title'
        return parent.get('id') + '/title'
    if name == 'para':
        return node.get('id')
    if name == 'item':
        return parent.get('id') + '/item/' + str(list(parent).index(node) + 1)
    if name == 'media':
        return node.get('id') + '/alt'
    return None


def stable_files():
    return [
        BASE / 'plans/A10-006-scope.json',
        BASE / 'source-excerpts/a10-unit-006.cnxml',
        BASE / 'source-excerpts/manifest-a10-006.json',
        BASE / 'translations/a10-unit-006.json',
        BASE / 'qa/a10-unit-006-language-notes.md',
        BASE / 'canon/examples.json',
        ROOT / 'downloads/canon/pnb-Arab-PK/R1.txt',
        ROOT / 'downloads/canon/pnb-Arab-PK/R2.txt',
        ROOT / 'downloads/canon/pnb-Arab-PK/R3.txt',
        BASE / 'canon/receipts/A10-006-next-unit-20260831T153830867915Z.json',
        BASE / 'canon/receipts/A10-006-draft-20260831T160340088615Z.json',
        BASE / 'canon/receipts/A10-006-revision-20260831T162228757267Z.json',
        BASE / 'canon/receipts/A10-006-qa-20260831T163307978573Z.json',
        BASE / 'canon/receipts/a10-unit-006-terminology-search.json',
        BASE / 'scripts/read_canon.py',
        BASE / 'scripts/prepare_a10.py',
        BASE / 'scripts/build_a10.py',
        BASE / 'scripts/prepare_a10_006.py',
        BASE / 'scripts/build_a10_006.py',
        BASE / 'scripts/qa_a10_006.py',
        BASE / 'styles/reader.css',
        BASE / 'sources.lock.json',
        ROOT / 'downloads/complete-upstream/osbooks-prealgebra-bundle/collections/elementary-algebra-2e.collection.xml',
        ROOT / 'downloads/complete-upstream/osbooks-prealgebra-bundle/modules/m82453/index.cnxml',
        ROOT / 'downloads/extracted/A10/translated/modules/m82453/index.cnxml',
        ROOT / 'downloads/extracted/A10/authority/MEDIA_AUTHORITY_MANIFEST.csv',
        BASE / 'provenance/A10-release/NOTICE.txt',
        BASE / 'provenance/upstream--osbooks-prealgebra-bundle/LICENSE',
        BASE / 'reader/a10-unit-005.html'
    ]


class Context:
    def __init__(self):
        self.manifest_path = BASE / 'source-excerpts/manifest-a10-006.json'
        self.manifest = json.loads(self.manifest_path.read_text(encoding='utf-8'))
        self.translation_path = BASE / 'translations/a10-unit-006.json'
        self.translation = json.loads(self.translation_path.read_text(encoding='utf-8'))
        self.excerpt_path = BASE / 'source-excerpts/a10-unit-006.cnxml'
        self.excerpt = ET.parse(self.excerpt_path).getroot()
        self.canonical_path = ROOT / self.manifest['canonical_local_path']
        self.canonical = ET.parse(self.canonical_path).getroot()
        self.source = copy.deepcopy(self.canonical)
        content = self.source.find(CURL + 'content')
        if len(content) != 8 or content[0].get('id') != 'fs-id1170654939047' or content[1].get('id') != 'fs-id1170655150800':
            raise Failure('canonical_opening_scope')
        if content[2].get('id') != 'fs-id1170654953465':
            raise Failure('canonical_next_boundary')
        for child in list(content)[2:]:
            content.remove(child)
        for child in list(self.source):
            if tag(child) == 'glossary':
                self.source.remove(child)
        self.source.set('id', 'a10-unit-006-excerpt')
        self.parent = parents(self.source)
        self.paths = {}
        self.path_nodes = {}
        def walk(node, path):
            self.paths[node] = path
            self.path_nodes[path] = node
            for index, child in enumerate(node):
                walk(child, path + '/' + str(index))
        walk(self.source, 'document')
        self.mapped = [node for node in self.source.iter()
                       if not node.tag.startswith(MURL) or node.tag == MURL + 'math']
        self.mapped_paths = [self.paths[node] for node in self.mapped]
        self.mapped_set = set(self.mapped)
        self.ids = [node.get('id') for node in self.source.iter()
                    if node is not self.source and node.get('id')]
        self.blocks = {}
        self.keys = {}
        module = next(node.text for node in self.source.iter() if tag(node) == 'content-id')
        tables = []
        for node in self.source.iter():
            parent = self.parent.get(node)
            key = derive_source_key(node, parent, module)
            if tag(node) == 'table':
                key = node.get('id') + '/summary'
                tables.append(node)
            if tag(node) == 'entry':
                table = next(owner for owner in self.source.iter() if tag(owner) == 'table' and node in set(owner.iter()))
                sections = [section for group in table if tag(group) == 'tgroup'
                            for section in group if tag(section) in {'thead', 'tbody'}]
                rows = [row for section in sections for row in section if tag(row) == 'row']
                row = self.parent[node]
                key = table.get('id') + '/row/' + str(rows.index(row) + 1) + '/entry/' + str(list(row).index(node) + 1)
            if key:
                self.blocks[key] = node
                self.keys[node] = key
        self.tables = tables
        self.maths = [node for node in self.source.iter() if node.tag == MURL + 'math']
        self.notice_path = BASE / 'provenance/a10-unit-006-component-notices.json'
        self.notice = json.loads(self.notice_path.read_text(encoding='utf-8'))
        self.reader_raw = READER.read_text(encoding='utf-8')
        self.reader = parse_reader(self.reader_raw)
        self.local_css = self.read_local_css()
        self.authority_path = ROOT / self.manifest['media_authority_manifest_path']
        with self.authority_path.open(encoding='utf-8-sig', newline='') as handle:
            self.authority_rows = list(csv.DictReader(handle))
        self.assets = {row['path']: (BASE / row['path']).read_bytes() for row in self.manifest['images']}

    def read_local_css(self):
        module = ast.parse((BASE / 'scripts/build_a10_006.py').read_text(encoding='utf-8'))
        assignment = next(node for node in module.body if isinstance(node, ast.Assign)
                          and any(isinstance(target, ast.Name) and target.id == 'LOCAL_CSS' for target in node.targets))
        return ast.literal_eval(assignment.value)


def validate_inputs(ctx, checker):
    m, tr = ctx.manifest, ctx.translation
    checker.ok((m['unit'], m['assignment'], m['collection'], m['module'])
               == ('A10-006', 'A10', 'col31130', 'm82453'), 'input_scope')
    checker.ok((tr['unit'], tr['locale'], tr['canonical_module']) == ('A10-006', 'pnb-Arab-PK', 'm82453'),
               'translation_scope')
    canonical_bytes = ctx.canonical_path.read_bytes()
    checker.ok((len(canonical_bytes), digest(canonical_bytes))
               == (m['full_module_bytes'], m['full_module_sha256']), 'canonical_size_hash')
    blob = hashlib.sha1(b'blob ' + str(len(canonical_bytes)).encode('ascii') + b'\0' + canonical_bytes).hexdigest()
    checker.ok(blob == m['canonical_git_blob_sha1'], 'canonical_git_blob')
    checker.ok(m['source_prefix_start_byte'] == 0 and m['source_prefix_end_byte_exclusive'] == 42893,
               'source_prefix_extent')
    checker.ok(digest(canonical_bytes[:42893]) == m['source_prefix_sha256'], 'source_prefix_hash')
    for index, witness in enumerate(m['source_byte_witnesses']):
        part = canonical_bytes[witness['start_byte']:witness['end_byte_exclusive']]
        checker.ok((len(part), digest(part)) == (witness['bytes'], witness['sha256']),
                   'source_witness_' + str(index))
    checker.ok(shape(ctx.source) == shape(ctx.excerpt), 'exact_selected_tree')
    checker.ok((ctx.excerpt_path.stat().st_size, file_hash(ctx.excerpt_path))
               == (m['excerpt_bytes'], m['excerpt_sha256']), 'excerpt_size_hash')
    checker.ok((ctx.translation_path.stat().st_size, file_hash(ctx.translation_path))
               == (m['translation_bytes'], m['translation_sha256']), 'translation_size_hash')
    checker.ok(ctx.ids == m['source_ids_in_document_order'] and len(ctx.ids) == len(set(ctx.ids)) == 134,
               'source_id_sequence')
    checker.ok(len(list(ctx.source.iter())) == 1243 and len(ctx.mapped_paths) == 604, 'source_element_extent')
    checker.ok(list(ctx.blocks) == m['source_block_keys_in_document_order']
               == list(tr['source_blocks']) and len(ctx.blocks) == 187, 'source_key_sequence')
    checker.ok({key: ctx.paths[node] for key, node in ctx.blocks.items()} == m['source_keys_to_paths'],
               'source_key_paths')
    counts = Counter(tag(node) for node in ctx.source.iter())
    for key, value in m['source_tag_counts'].items():
        checker.ok(counts[key] == value, 'source_tag_count_' + key)
    checker.ok(len(ctx.maths) == m['source_counts']['mathml_trees'] == 98, 'source_math_count')
    checker.ok(sum(1 for node in ctx.source.iter() if node.tag.startswith(MURL)) == 737,
               'source_math_node_count')
    math_records = []
    for owner in ctx.source.iter():
        key = ctx.keys.get(owner)
        direct = [child for child in owner if child.tag == MURL + 'math']
        for index, math_node in enumerate(direct):
            owner_key = owner.get('id') if tag(owner) == 'equation' else key
            math_records.append((owner_key, ctx.paths[owner], index, ctx.paths[math_node],
                                 math_fingerprint(math_node), text(math_node), tag(owner) == 'equation'))
    declared = [(row['owner_source_key'], row['owner_source_path'], row['placeholder_index'],
                 row['source_path'], row['tree_sha256'], row['text'], row['automatic_equation_owner'])
                for row in m['source_mathml']]
    checker.ok(math_records == declared, 'source_math_fingerprints')
    checker.ok(not m['mathml_changes'], 'zero_math_change_ledger')
    checker.ok(len(ctx.tables) == 8 and sum(tag(n) == 'entry' for n in ctx.source.iter()) == 97,
               'source_table_count_cells')
    checker.ok(sum(tag(n) == 'entry' for section in ctx.source.iter() if tag(section) == 'thead'
                   for row in section for n in row) == 15, 'source_actual_header_cells')
    checker.ok(sum(tag(n) == 'span' and n.get('class') == 'token' for n in ctx.source.iter()) == 48,
               'source_part_count')
    checker.ok(sum(tag(n) == 'newline' for n in ctx.source.iter()) == 12, 'source_newline_count')
    checker.ok(sum(tag(n) == 'emphasis' and n.get('effect') == 'bold' for n in ctx.source.iter()) == 5,
               'source_bold_count')
    checker.ok(sum(tag(n) == 'emphasis' and n.get('effect') == 'italics' for n in ctx.source.iter()) == 89,
               'source_italic_count')
    checker.ok(sum(tag(n) == 'term' for n in ctx.source.iter()) == 14, 'source_term_count')
    checker.ok(sum(tag(n) == 'link' for n in ctx.source.iter()) == 3, 'source_link_count')
    checker.ok(sum(tag(n) == 'exercise' for n in ctx.source.iter()) == 9
               and sum(tag(n) == 'solution' for n in ctx.source.iter()) == 9, 'source_exercise_solution_count')
    checker.ok(sum(tag(n) == 'title' for solution in ctx.source.iter() if tag(solution) == 'solution'
                   for n in list(solution)[:1]) == 3, 'source_explicit_solution_titles')
    checker.ok(not BAD.search(ctx.translation_path.read_text(encoding='utf-8')), 'translation_script_controls')
    checker.ok(not any(PLACEHOLDER.search(value) and not re.fullmatch(
        r'(?:[^{}]|\{\{(?:math|link):\d+\}\})*', value, flags=re.S)
        for value in tr['source_blocks'].values()), 'translation_placeholder_kinds')
    for key, source_node in ctx.blocks.items():
        value = tr['source_blocks'][key]
        fragment = parsed_fragment(value)
        maths = [child for child in source_node if child.tag == MURL + 'math']
        links = [child for child in source_node if tag(child) == 'link']
        checker.ok([int(x) for x in re.findall(r'\{\{math:(\d+)\}\}', value)] == list(range(len(maths))),
                   'translation_math_slots_' + key)
        checker.ok([int(x) for x in re.findall(r'\{\{link:(\d+)\}\}', value)] == list(range(len(links))),
                   'translation_link_slots_' + key)
        checker.ok(not re.search(r'\{\{child:', value), 'translation_no_child_slot_' + key)
        checker.ok(len(list(fragment.iter('br'))) == sum(tag(c) == 'newline' for c in source_node),
                   'translation_newline_' + key)
        checker.ok(len(list(fragment.iter('strong'))) ==
                   sum(tag(c) == 'emphasis' and c.get('effect') == 'bold' for c in source_node),
                   'translation_bold_' + key)
        checker.ok(len(list(fragment.iter('em'))) ==
                   sum(tag(c) == 'emphasis' and c.get('effect') == 'italics' for c in source_node),
                   'translation_italic_' + key)
        source_terms = [c for c in source_node if tag(c) == 'term']
        target_terms = [n for n in fragment.iter('span') if 'source-term' in n.get('class', '').split()]
        checker.ok([n.get('id') for n in target_terms] == [n.get('id') for n in source_terms],
                   'translation_term_ids_' + key)
        source_parts = [PARTS[(c.text or '').strip()] for c in source_node
                        if tag(c) == 'span' and c.get('class') == 'token']
        target_parts = [match[1] for match in re.finditer(r'<bdi\b[^>]*>\(([a-e])\)</bdi>', value)]
        checker.ok(target_parts == source_parts, 'translation_parts_' + key)
    source_numerals = 0
    for key, source_node in ctx.blocks.items():
        if key.endswith('/summary'):
            source_value = source_node.get('aria-label') or source_node.get('summary') or ''
        elif key.endswith('/alt'):
            source_value = source_node.get('alt') or ''
        else:
            source_value = nonmath_text(source_node)
        target_value = text(parsed_fragment(re.sub(r'\{\{(?:math|link):\d+\}\}', '', tr['source_blocks'][key])))
        left, right = NUM.findall(source_value), NUM.findall(target_value)
        source_numerals += len(left)
        checker.ok(left == right, 'source_prose_numerals_' + key)
    checker.ok(source_numerals == 128, 'source_prose_numeral_total')
    checker.ok(tr['source_english_echo_keys'] == m['source_english_echo_keys']
               and len(set(tr['source_english_echo_keys'])) == 36, 'english_echo_input_contract')
    checker.ok(tr['image_alt_overrides'] == m['image_alt_overrides']
               and tr['table_summary_overrides'] == m['table_summary_overrides'], 'accessible_override_contract')
    bridge_ids = []
    for field in ('bridge_before_html', 'bridge_after_html'):
        bridge = ET.fromstring(tr[field])
        checker.ok(bridge.tag == 'section' and bridge.get('id') and bridge.get('class') in {'bridge', 'original-bridge'},
                   'original_bridge_label_' + field)
        bridge_ids.extend(node.get('id') for node in bridge.iter() if node.get('id'))
    checker.ok(len(bridge_ids) == len(set(bridge_ids)), 'original_bridge_unique_ids')
    expected_notes = {row['note_id'] for row in tr['source_corrections']}
    expected_notes.update(tr['retained_image_keys'].values())
    checker.ok(expected_notes <= set(bridge_ids), 'original_correction_targets')
    checker.ok(all(key in tr['source_blocks'] for row in tr['source_corrections'] for key in row['source_keys']),
               'correction_source_owners')
    checker.ok(not tr['whole_module_complete'] and not tr['whole_book_complete']
               and not tr['whole_assignment_complete'], 'translation_incomplete_claims')
    comparison = ROOT / m['indonesian_comparison_path']
    checker.ok((comparison.stat().st_size, file_hash(comparison))
               == (m['indonesian_comparison_bytes'], m['indonesian_comparison_sha256']), 'comparison_pin')
    collection = ROOT / 'downloads/complete-upstream/osbooks-prealgebra-bundle/collections/elementary-algebra-2e.collection.xml'
    checker.ok((collection.stat().st_size, file_hash(collection))
               == (5256, '5fdc03ab9e6ee7327be72f7e0a17c4d884e65f4a8081a0b2a06dbdb1392bda72'),
               'collection_pin')
    lock = json.loads((BASE / 'sources.lock.json').read_text(encoding='utf-8'))
    pin = next(row for row in lock['repositories'] if row['role'] == 'A10+A20 upstream')
    checker.ok((m['commit'], m['tree']) == (pin['commit'], pin['tree']), 'source_lock_pin')
    checker.ok(file_hash(ctx.authority_path) == m['media_authority_manifest_sha256'], 'media_authority_pin')


def normalize_target_block(target, source_node):
    clone = copy.deepcopy(target)
    while True:
        parent_map = parents(clone)
        removable = [node for node in clone.iter()
                     if node is not clone and ('source-original-advisory' in node.get('class', '').split()
                                              or 'source-english-echo' in node.get('class', '').split())]
        if not removable:
            break
        remove_preserving_tail(parent_map[removable[0]], removable[0])
    while True:
        parent_map = parents(clone)
        wrappers = [node for node in clone.iter()
                    if node is not clone and 'source-inline-part' in node.get('class', '').split()]
        if not wrappers:
            break
        unwrap(parent_map[wrappers[0]], wrappers[0])
    direct_math = [child for child in source_node if child.tag == MURL + 'math']
    direct_links = [child for child in source_node if tag(child) == 'link']
    replacements = {}
    for index, child in enumerate(direct_math):
        replacements[child.get('data-source-path') if False else None] = None
        replacements[index] = child
    for index, child in enumerate(direct_math):
        path = None
        # Path is recoverable from the target's binding metadata by matching the source child tree.
        for node in clone.iter():
            if node.get('data-source-tag') == 'math' and text(node).replace(' ', '') == text(child).replace(' ', ''):
                if node.get('data-source-path') not in {value for value in replacements.values() if isinstance(value, str)}:
                    path = node.get('data-source-path')
                    replacements[index] = path
                    break
        if path is None:
            raise Failure('rendered_block_missing_math_placeholder')
    parent_map = parents(clone)
    for index in range(len(direct_math)):
        node = next(n for n in clone.iter() if n.get('data-source-path') == replacements[index])
        remove_preserving_tail(parent_map[node], node, '{{math:' + str(index) + '}}')
        parent_map = parents(clone)
    link_nodes = [node for node in clone.iter() if node.get('data-source-tag') == 'link']
    if len(link_nodes) != len(direct_links):
        raise Failure('rendered_block_link_count')
    for index, node in enumerate(link_nodes):
        parent_map = parents(clone)
        remove_preserving_tail(parent_map[node], node, '{{link:' + str(index) + '}}')
    for node in clone.iter():
        for name in list(node.attrib):
            if name.startswith('data-source-'):
                del node.attrib[name]
    return clone


def validate_reader(ctx, checker, root=None, translation=None, notice=None, assets=None, local_css=None):
    root = copy.deepcopy(root if root is not None else ctx.reader)
    tr = translation if translation is not None else ctx.translation
    component = notice if notice is not None else ctx.notice
    asset_map = assets if assets is not None else ctx.assets
    css = local_css if local_css is not None else ctx.local_css
    raw = ET.tostring(root, encoding='unicode')
    checker.ok(root.tag == 'html' and root.get('lang') == 'pnb-Arab-PK' and root.get('dir') == 'rtl',
               'reader_locale_rtl')
    checker.ok(not BAD.search(raw), 'reader_script_controls')
    checker.ok(not PLACEHOLDER.search(raw), 'reader_no_unresolved_placeholders')
    heads = root.findall('head')
    bodies = root.findall('body')
    checker.ok(len(heads) == len(bodies) == 1 and bodies[0].get('class') == 'a10-reader a10-006-reader',
               'reader_frame')
    main = bodies[0].find('main')
    checker.ok(main is not None and [child.get('id') or child.get('class') for child in main]
               == ['source-label', 'a10-006-before', 'a10-unit-006-excerpt',
                   'a10-006-original-bridge', 'status'], 'main_exact_children')
    checker.ok(main[0].get('data-origin') == main[-1].get('data-origin') == 'renderer-ui'
               and main[1].get('data-origin') == main[3].get('data-origin') == 'original-bridge',
               'main_origin_labels')
    output_ids = [node.get('id') for node in root.iter() if node.get('id')]
    checker.ok(len(output_ids) == len(set(output_ids)), 'reader_unique_ids')
    checker.ok([sid for sid in output_ids if sid in set(ctx.ids)] == ctx.ids, 'reader_source_id_order')
    mapped_targets = [node for node in root.iter() if node.get('data-source-path')]
    target_paths = [node.get('data-source-path') for node in mapped_targets]
    checker.ok(target_paths == ctx.mapped_paths and len(target_paths) == len(set(target_paths)) == 604,
               'reader_all_source_bindings_order')
    target_by_path = dict(zip(target_paths, mapped_targets))
    for path, target in target_by_path.items():
        source = ctx.path_nodes[path]
        checker.ok(target.get('data-source-tag') == tag(source), 'binding_tag_' + path)
        checker.ok(target.get('data-source-qname') == source.tag, 'binding_qname_' + path)
        checker.ok(json.loads(target.get('data-source-attributes')) == source.attrib, 'binding_attributes_' + path)
        source_parent = ctx.parent.get(source)
        while source_parent is not None and source_parent not in ctx.mapped_set:
            source_parent = ctx.parent.get(source_parent)
        expected_parent = ctx.paths[source_parent] if source_parent is not None else None
        target_parent = parents(root).get(target)
        while target_parent is not None and not target_parent.get('data-source-path'):
            target_parent = parents(root).get(target_parent)
        actual_parent = target_parent.get('data-source-path') if target_parent is not None else None
        checker.ok(actual_parent == expected_parent, 'binding_ancestry_' + path)
    key_targets = [node for node in root.iter() if node.get('data-source-key')]
    checker.ok([node.get('data-source-key') for node in key_targets] == list(tr['source_blocks']),
               'rendered_key_sequence')
    checker.ok(len(key_targets) == len({node.get('data-source-key') for node in key_targets}) == 187,
               'rendered_key_uniqueness')
    key_target_map = {node.get('data-source-key'): node for node in key_targets}
    for key, source_node in ctx.blocks.items():
        target = key_target_map[key]
        checker.ok(target.get('data-source-path') == ctx.paths[source_node], 'key_source_owner_' + key)
        if key.endswith('/summary'):
            faithful = target.find('.//*[@data-source-summary]')
            checker.ok(faithful is not None and faithful.get('data-source-summary') == tr['source_blocks'][key],
                       'rendered_table_faithful_summary_' + key)
            record = tr['table_summary_overrides'].get(key)
            expected = record['summary'] if record else tr['source_blocks'][key]
            checker.ok(faithful.get('aria-label') == expected
                       and faithful.get('data-description-origin') ==
                       ('original-correction' if record else 'source-translation'),
                       'rendered_table_effective_summary_' + key)
        elif key.endswith('/alt'):
            image = target.find('.//img')
            checker.ok(image is not None and image.get('data-source-alt') == tr['source_blocks'][key],
                       'rendered_image_faithful_alt_' + key)
            record = tr['image_alt_overrides'].get(key)
            expected = record['alt'] if record else tr['source_blocks'][key]
            checker.ok(image.get('alt') == expected and image.get('data-description-origin') ==
                       ('original-correction' if record else 'source-translation'),
                       'rendered_image_effective_alt_' + key)
        else:
            actual = normalize_target_block(target, source_node)
            expected = parsed_fragment(tr['source_blocks'][key])
            checker.ok(inner(actual) == inner(expected), 'rendered_source_block_' + key)
    math_targets = [node for node in mapped_targets if node.get('data-source-tag') == 'math']
    checker.ok(len(math_targets) == len(ctx.maths) == 98, 'rendered_math_count')
    for index, (source, wrapper) in enumerate(zip(ctx.maths, math_targets)):
        checker.ok(wrapper.get('dir') == 'ltr' and 'math-isolate' in wrapper.get('class', '').split(),
                   'math_outer_ltr_' + str(index))
        maths = [node for node in wrapper if node.tag == MURL + 'math']
        checker.ok(len(maths) == 1 and maths[0].get('dir') == 'ltr', 'math_root_ltr_' + str(index))
        clone = copy.deepcopy(maths[0])
        if source.get('dir') is None:
            del clone.attrib['dir']
        checker.ok(shape(clone) == shape(source), 'math_exact_tree_' + str(index))
    english_mtext = [node for node in ctx.maths if any(tag(x) == 'mtext' and re.search('[A-Za-z]{2}', x.text or '')
                                                      for x in node.iter())]
    checker.ok(len(english_mtext) == 3, 'canonical_english_mtext_owners')
    ordinals = [node for node in ctx.maths if any(tag(x) == 'msup'
                and len(x) == 2 and text(x[0]) == 'n' and text(x[1]) == 'th' for x in node.iter())]
    checker.ok(len(ordinals) == 2, 'canonical_english_ordinal_math')
    echoes = [node for node in root.iter() if 'source-english-echo' in node.get('class', '').split()]
    checker.ok([node.get('data-source-english-for') for node in echoes] == tr['source_english_echo_keys']
               and len(echoes) == 36, 'rendered_english_echo_sequence')
    for echo in echoes:
        key = echo.get('data-source-english-for')
        checker.ok(echo.get('data-origin') == ENGLISH_ORIGIN
                   and echo.get('aria-describedby') == 'a10-006-english-context', 'english_echo_origin_' + key)
        words = next((node for node in echo if 'source-english-words' in node.get('class', '').split()), None)
        checker.ok(words is not None and words.get('lang') == 'en' and words.get('dir') == 'ltr',
                   'english_echo_language_' + key)
        checker.ok(not any(node.get('id') for node in words.iter())
                   and not any(node.tag == MURL + 'math' for node in words.iter()), 'english_echo_no_ids_math_' + key)
        expected = source_lexical_fragment(ctx.blocks[key], key in set(tr['source_english_echo_policy']['omit_mathml_owners']))
        checker.ok(inner(words) == inner(expected), 'english_echo_exact_source_' + key)
    checker.ok(sum(1 for echo in echoes if echo.get('data-source-english-for') == 'fs-id1166424795899') == 1,
               'english_echo_one_math_omission_owner')
    short = {row['key']: row for row in ctx.manifest['token_owners'] if row['group_short_parts']}
    wrappers = [node for node in root.iter() if 'source-inline-part' in node.get('class', '').split()]
    checker.ok(len(wrappers) == 32 and len(short) == 12, 'short_part_wrapper_total')
    for key, record in short.items():
        owner = key_target_map[key]
        owned = [node for node in owner.iter() if 'source-inline-part' in node.get('class', '').split()]
        checker.ok([node.get('data-source-part') for node in owned]
                   == [value.strip('()') for value in record['display_labels']], 'short_part_markers_' + key)
        for index, wrapper in enumerate(owned):
            bound = [node for node in wrapper.iter() if node.get('data-source-tag') == 'span']
            checker.ok(len(bound) == 1 and flat(text(wrapper)).startswith('(' + wrapper.get('data-source-part') + ')')
                       and flat(text(wrapper)) != '(' + wrapper.get('data-source-part') + ')',
                       'short_part_complete_' + key + '_' + str(index))
            checker.ok(not (wrapper.tail or '').strip(), 'short_part_tail_' + key + '_' + str(index))
    checker.ok(not any('source-inline-part' in node.get('class', '').split()
                       for key in LONG_PARTS for node in key_target_map[key].iter()), 'long_parts_wrap_normally')
    checker.ok(not any('source-inline-part' in node.get('class', '').split()
                       for table in root.iter() if table.get('data-source-tag') == 'tgroup' for node in table.iter()),
               'table_parts_not_grouped')
    table_targets = [target_by_path[ctx.paths[node]] for node in ctx.tables]
    checker.ok(len(table_targets) == 8, 'rendered_table_count')
    for source_table, wrapper in zip(ctx.tables, table_targets):
        sid = source_table.get('id')
        group = next(node for node in source_table if tag(node) == 'tgroup')
        target_table = target_by_path[ctx.paths[group]]
        columns = int(group.get('cols'))
        rows = [row for section in group if tag(section) in {'thead', 'tbody'} for row in section]
        entries = [entry for row in rows for entry in row]
        target_entries = [target_by_path[ctx.paths[entry]] for entry in entries]
        header_entries = [entry for section in group if tag(section) == 'thead'
                          for row in section for entry in row]
        checker.ok(target_table.tag == 'table' and target_table.get('dir') == 'ltr'
                   and target_table.get('data-source-tgroup-cols') == str(columns), 'table_ltr_geometry_' + sid)
        checker.ok(target_table.get('style') ==
                   '--source-columns:' + str(columns) + ';--source-table-width:' + str(columns * 330) + 'px',
                   'table_source_driven_width_' + sid)
        checker.ok(len(rows) == next(row['rows'] for row in ctx.manifest['tables'] if row['id'] == sid)
                   and len(entries) == next(row['cells'] for row in ctx.manifest['tables'] if row['id'] == sid),
                   'table_rows_cells_' + sid)
        checker.ok(sum(target.tag == 'th' for target in target_entries) == len(header_entries)
                   and all(target.tag == ('th' if source in header_entries else 'td')
                           for source, target in zip(entries, target_entries)), 'table_header_semantics_' + sid)
        for source, target in zip(entries, target_entries):
            value = text(parsed_fragment(tr['source_blocks'][ctx.keys[source]]))
            expected_dir = 'rtl' if re.search('[\u0600-\u06ff]', value) else 'ltr'
            checker.ok(target.get('dir') == expected_dir, 'table_cell_direction_' + ctx.paths[source])
            expected_style = ('text-align:' + source.get('align', 'left') + ';vertical-align:'
                              + source.get('valign', ctx.parent[source].get('valign', 'top')))
            checker.ok(target.get('style') == expected_style, 'table_cell_alignment_' + ctx.paths[source])
    checker.ok(sum(node.tag == 'th' for node in root.iter() if node.get('data-source-tag') == 'entry') == 15,
               'rendered_exact_header_total')
    checker.ok(sum(node.get('data-source-tag') == 'entry' and not flat(text(node))
                   for node in root.iter()) == 1, 'rendered_one_empty_cell')
    references = []
    for source_link in [node for node in ctx.source.iter() if tag(node) == 'link']:
        target = target_by_path[ctx.paths[source_link]]
        references.append((target.get('href'), target.get('data-source-target'), inner(target)))
    declared_refs = []
    for row in ctx.manifest['references']:
        key = row['source_key'] + '/link/' + str(row['link_index'])
        declared_refs.append((row['href'], row['id'], inner(parsed_fragment(tr['source_link_labels'][key]))))
    checker.ok(references == declared_refs, 'rendered_exact_link_targets_labels')
    media_nodes = [node for node in ctx.source.iter() if tag(node) == 'media']
    checker.ok(len(media_nodes) == 4 and len(ctx.manifest['images']) == 4, 'rendered_image_count')
    for media, spec in zip(media_nodes, ctx.manifest['images']):
        wrapper = target_by_path[ctx.paths[media]]
        image = next(node for node in media if tag(node) == 'image')
        target = target_by_path[ctx.paths[image]]
        asset = asset_map[spec['path']]
        checker.ok((len(asset), digest(asset), jpeg_dimensions(asset))
                   == (spec['bytes'], spec['sha256'], (spec['width'], spec['height'])),
                   'asset_bytes_dimensions_' + spec['media_id'])
        checker.ok(target.tag == 'img' and target.get('src') == '../' + spec['path']
                   and target.get('width') == str(spec['width']) and target.get('height') == str(spec['height'])
                   and target.get('style') == '--source-width:' + str(spec['width']) + 'px',
                   'rendered_image_geometry_' + spec['media_id'])
        checker.ok(target.get('data-source-image-mime') == image.get('mime-type') == 'image/jpeg'
                   and target.get('data-rendered-image-mime') == 'image/jpeg', 'rendered_image_mime_' + spec['media_id'])
        described = set((target.get('aria-describedby') or '').split())
        checker.ok(spec['original_bilingual_key_id'] in described
                   and set(ctx.translation['retained_image_keys'].values()) <= set(output_ids),
                   'image_key_description_' + spec['media_id'])
        fallback = [node for node in wrapper.iter('a') if node.get('href') == '../' + spec['path']]
        checker.ok(len(fallback) == 1, 'image_fallback_' + spec['media_id'])
    authority = {row['relative_path']: row for row in ctx.authority_rows}
    for spec in ctx.manifest['images']:
        checker.ok(authority.get(spec['source_path']) == spec['existing_media_authority_row'],
                   'image_authority_row_' + spec['media_id'])
    table_rule = re.search(r'\.a10-006-reader \.source-table th[^\{]*\{([^}]+)\}', css)
    hint_rule = re.search(r'\.a10-006-reader \.source-media \.scroll-hint[^\{]*\{([^}]+)\}', css)
    part_rule = re.search(r'\.a10-006-reader \.source-inline-part\s*\{([^}]+)\}', css)
    checker.ok(css.count('.a10-006-reader .source-table') >= 3 and 'overflow-x:auto' in css
               and table_rule and 'width:330px' in table_rule[1] and 'white-space:normal' in table_rule[1]
               and hint_rule and 'direction:rtl' in hint_rule[1] and 'white-space:normal' in hint_rule[1]
               and part_rule and 'white-space:nowrap' in part_rule[1], 'unit_css_layout_contract')
    checker.ok('transform:' not in css and 'scaleX' not in css, 'unit_css_no_image_mirroring')
    shared_css = (BASE / 'styles/reader.css').read_text(encoding='utf-8')
    checker.ok('overflow-x:auto' in shared_css and '.math-isolate' in shared_css, 'common_css_scroll_math')
    all_local_ids = set(output_ids)
    for node in root.iter():
        for attribute in ('href', 'src'):
            target = node.get(attribute)
            if not target:
                continue
            url = urlsplit(target)
            if url.scheme or url.netloc:
                checker.ok(url.scheme in {'http', 'https'}, 'external_link_scheme_' + target)
                continue
            if url.path:
                path = (READER.parent / unquote(url.path)).resolve()
                checker.ok(path.is_relative_to(BASE.resolve()) and path.is_file(), 'local_path_' + target)
                if url.fragment:
                    other = parse_reader(path.read_text(encoding='utf-8'))
                    checker.ok(unquote(url.fragment) in {x.get('id') for x in other.iter() if x.get('id')},
                               'cross_fragment_' + target)
            else:
                checker.ok(unquote(url.fragment) in all_local_ids, 'local_fragment_' + target)
    generated_solutions = [node for node in root.iter() if 'solution-label' in node.get('class', '').split()]
    checker.ok(len(generated_solutions) == 6 and all(node.get('data-origin') == 'renderer-ui'
               for node in generated_solutions), 'generated_tryit_solution_labels')
    explicit = [node for node in ctx.source.iter() if tag(node) == 'title' and tag(ctx.parent[node]) == 'solution']
    checker.ok(len(explicit) == 3 and all(len([target_by_path[ctx.paths[node]]]) == 1 for node in explicit),
               'explicit_solution_titles_once')
    example_labels = [node for node in root.iter() if 'example-label' in node.get('class', '').split()]
    checker.ok(len(example_labels) == 3 and [flat(text(node)) for node in example_labels]
               == ['حل کیتی مثال 1', 'حل کیتی مثال 2', 'حل کیتی مثال 3'], 'example_labels_1_to_3')
    unowned = []
    parent_map = parents(root)
    source_document = target_by_path['document']
    for owner in source_document.iter():
        if owner.text and owner.text.strip():
            ancestor = owner
            allowed = False
            while ancestor is not None:
                if (ancestor.get('data-source-key') or ancestor.get('data-origin') or ancestor.tag.startswith(MURL)
                        or ancestor.get('data-source-tag') in {'content-id', 'uuid'}):
                    allowed = True
                    break
                ancestor = parent_map.get(ancestor)
            if not allowed:
                unowned.append(flat(owner.text))
        for child in owner:
            if child.tail and child.tail.strip():
                ancestor = owner
                allowed = False
                while ancestor is not None:
                    if (ancestor.get('data-source-key') or ancestor.get('data-origin') or ancestor.tag.startswith(MURL)
                            or ancestor.get('data-source-tag') in {'content-id', 'uuid'}):
                        allowed = True
                        break
                    ancestor = parent_map.get(ancestor)
                if not allowed:
                    unowned.append(flat(child.tail))
    checker.ok(not unowned, 'no_anonymous_source_or_frame_prose_' + '|'.join(unowned[:5]))
    footer = next((node for node in root.iter('footer') if node.get('id') == 'credits'), None)
    footer_text = flat(text(footer)) if footer is not None else ''
    checker.ok(footer is not None and footer.get('lang') == 'en' and footer.get('dir') == 'ltr',
               'footer_language_direction')
    for required in ('Lynn Marecek', 'MaryAnne Anthony-Smith', 'Andrea Honeycutt Mathis',
                     'Attribution-NonCommercial-ShareAlike 4.0', 'do not endorse',
                     'not image-specific permission', 'not a complete module',
                     'not training or fine-tuning data', 'assistive-technology review remain pending'):
        checker.ok(required in footer_text, 'footer_' + re.sub('[^A-Za-z0-9]+', '_', required))
    checker.ok('Abramson' not in footer_text and 'Lippman' not in footer_text and 'Rasmussen' not in footer_text,
               'footer_no_a30_authors')
    checker.ok(not ctx.translation['whole_module_complete'] and 'Stop before fs-id1170654953465' in footer_text,
               'footer_exact_incomplete_boundary')
    validate_notice(ctx, checker, component)


def validate_notice(ctx, checker, component):
    m = ctx.manifest
    checker.ok((component['schema'], component['unit'], component['work'], component['module'], component['collection'])
               == ('a10-retained-component-evidence-v1', 'A10-006', 'OpenStax Elementary Algebra 2e',
                   'm82453', 'col31130'), 'notice_identity')
    checker.ok(component['manifest_sha256'] == file_hash(ctx.manifest_path)
               and component['excerpt_sha256'] == m['excerpt_sha256'], 'notice_input_hashes')
    checker.ok(component['existing_notice_inputs'] == m['existing_notice_inputs']
               and component['existing_notice_hash_policy'] == m['existing_notice_hash_policy'],
               'notice_retained_inputs')
    for entry in m['existing_notice_inputs']:
        checker.ok(logical_lf_hash(ROOT / entry['path']) == entry['sha256'],
                   'notice_logical_lf_' + Path(entry['path']).name)
    checker.ok(component['release_notice_verbatim']
               == (BASE / 'provenance/A10-release/NOTICE.txt').read_text(encoding='utf-8'),
               'notice_release_verbatim')
    checker.ok('No new component-specific clearance' in component['rights_status']
               and 'not rights holders or permissions' in component['credit_limit']
               and component['media_authority_manifest']['sha256'] == m['media_authority_manifest_sha256'],
               'notice_no_invented_clearance')
    checker.ok(len(component['images']) == 4, 'notice_image_count')
    for source, record in zip(m['images'], component['images']):
        for field in ('media_id', 'source_path', 'path', 'sha256', 'bytes', 'git_blob_sha1', 'width', 'height'):
            checker.ok(record[field] == source[field], 'notice_image_' + source['media_id'] + '_' + field)
        checker.ok(record['existing_media_authority_row'] == source['existing_media_authority_row']
                   and record['source_english_alt'] == source['source_english_alt']
                   and record['original_accessible_override'] == source['source_alt_override'],
                   'notice_image_trace_' + source['media_id'])
        checker.ok('Not newly assessed' in record['component_clearance'], 'notice_image_restriction_' + source['media_id'])
    checker.ok(component['scope_boundary']['next_required'] == m['next_source_id']
               and not component['whole_module_translation_complete']
               and not component['whole_book_translation_complete']
               and not component['whole_assignment_complete'], 'notice_incomplete_scope')


def derive_arithmetic_checks(ctx, checker):
    power_cases = []
    for exercise in [node for node in ctx.source.iter() if tag(node) == 'exercise']:
        problem = next((node for node in exercise if tag(node) == 'problem'), None)
        solution = next((node for node in exercise if tag(node) == 'solution'), None)
        if problem is None or solution is None:
            continue
        powers = []
        for sup in problem.iter(MURL + 'msup'):
            if len(sup) == 2 and text(sup[0]).isdigit() and text(sup[1]).isdigit():
                powers.append((int(text(sup[0])), int(text(sup[1]))))
        if powers:
            answer_numbers = [int(value) for value in NUM.findall(nonmath_text(solution))]
            computed = [base ** exponent for base, exponent in powers]
            if all(value in answer_numbers for value in computed):
                power_cases.append((exercise.get('id'), powers, computed))
    checker.ok(len(power_cases) >= 2, 'derived_power_answer_cases')
    for exercise_id, powers, computed in power_cases:
        checker.ok(all(base ** exponent == value for (base, exponent), value in zip(powers, computed)),
                   'derived_power_arithmetic_' + exercise_id)
    worked = []
    for table in ctx.tables:
        answers = ([int(text(node)) for node in table.iter(MURL + 'mn') if text(node).isdigit()]
                   + [int(value) for value in NUM.findall(nonmath_text(table))])
        for sup in table.iter(MURL + 'msup'):
            if len(sup) == 2 and text(sup[0]).isdigit() and text(sup[1]).isdigit():
                base, exponent = int(text(sup[0])), int(text(sup[1]))
                result = base ** exponent
                if result in answers:
                    worked.append((table.get('id'), base, exponent, result))
    declared_worked = ctx.manifest['worked_exponent_check']
    checker.ok((declared_worked['source_table_id'], declared_worked['base'], declared_worked['exponent'],
                declared_worked['result']) in worked, 'derived_worked_power_result')
    age_table = ctx.tables[0]
    rows = [row for row in age_table.iter() if tag(row) == 'row'][1:4]
    pairs = []
    for row in rows:
        values = [int(text(node)) for node in row.iter(MURL + 'mn')]
        if len(values) == 2:
            pairs.append(tuple(values))
    checker.ok(len(pairs) == 3 and len({right - left for left, right in pairs}) == 1,
               'derived_age_constant_difference')


def mutation_rejections(ctx):
    outcomes = []

    def reject(name, mutate=None, translation=None, notice=None, assets=None, css=None):
        root = copy.deepcopy(ctx.reader)
        if mutate:
            mutate(root)
        check = Checker()
        try:
            validate_reader(ctx, check, root=root,
                            translation=translation if translation is not None else ctx.translation,
                            notice=notice if notice is not None else ctx.notice,
                            assets=assets if assets is not None else ctx.assets,
                            local_css=css if css is not None else ctx.local_css)
        except (Failure, KeyError, ValueError, IndexError, TypeError, json.JSONDecodeError) as error:
            outcomes.append({'name': name, 'rejected': True, 'reason': str(error)[:240]})
            return
        raise Failure('mutation_not_rejected_' + name)

    def by_attr(root, name, value):
        return next(node for node in root.iter() if node.get(name) == value)

    def change_source_number(root):
        owner = by_attr(root, 'data-source-key', 'fs-id1170655151082')
        target = next(node for node in owner.iter() if '20' in (node.text or ''))
        target.text = target.text.replace('20', '21', 1)
    reject('changed_source_prose_number', change_source_number)
    reject('changed_math_number',
           lambda root: setattr(next(node for node in root.iter(MURL + 'mn')), 'text', '999'))
    reject('math_root_rtl',
           lambda root: next(node for node in root.iter(MURL + 'math')).set('dir', 'rtl'))
    reject('deleted_empty_math_node',
           lambda root: next(node for node in root.iter(MURL + 'mtable')).remove(
               next(node for node in next(node for node in root.iter(MURL + 'mtable')) if tag(node) == 'mtr')))
    reject('switched_source_image',
           lambda root: by_attr(root, 'data-source-path', 'document/2/1/17/2/0').set(
               'src', '../assets/a10/CNX_ElemAlg_Figure_01_02_002_img_new.jpg'))
    reject('changed_effective_image_alt',
           lambda root: by_attr(root, 'data-source-path', 'document/2/1/41/0').set('alt', 'غلط'))
    reject('changed_faithful_image_alt',
           lambda root: by_attr(root, 'data-source-path', 'document/2/1/41/0').set('data-source-alt', 'غلط'))
    reject('changed_table_effective_summary',
           lambda root: next(node for node in root.iter('table')
                             if node.get('data-description-origin') == 'original-correction').set('aria-label', 'غلط'))
    reject('changed_table_faithful_summary',
           lambda root: next(node for node in root.iter('table')
                             if node.get('data-description-origin') == 'original-correction').set('data-source-summary', 'غلط'))
    reject('header_changed_to_data_cell',
           lambda root: setattr(next(node for node in root.iter('th')), 'tag', 'td'))
    def swap_entries(root):
        row = next(node for node in root.iter('tr') if len([x for x in node if x.tag in {'td', 'th'}]) >= 2)
        a, b = list(row)[:2]
        row.remove(a)
        row.remove(b)
        row.insert(0, b)
        row.insert(1, a)
    reject('switched_table_entries', swap_entries)
    reject('bad_table_width',
           lambda root: next(node for node in root.iter('table') if node.get('data-source-tag') == 'tgroup').set(
               'style', '--source-columns:2;--source-table-width:700px'))
    reject('missing_english_echo',
           lambda root: parents(root)[next(node for node in root.iter()
                                          if 'source-english-echo' in node.get('class', '').split())].remove(
               next(node for node in root.iter() if 'source-english-echo' in node.get('class', '').split())))
    reject('changed_english_echo_word',
           lambda root: setattr(next(node for node in root.iter()
                                     if 'source-english-words' in node.get('class', '').split()), 'text', 'wrong'))
    reject('english_echo_gets_source_id',
           lambda root: next(node for node in root.iter()
                             if 'source-english-words' in node.get('class', '').split()).set('id', 'invented-source-id'))
    reject('wrong_english_echo_owner',
           lambda root: next(node for node in root.iter()
                             if 'source-english-echo' in node.get('class', '').split()).set(
                                 'data-source-english-for', 'fs-id1170655151082'))
    reject('changed_source_link_target',
           lambda root: next(node for node in root.iter('a') if node.get('data-source-target')).set(
               'href', '#fs-id1170655178120'))
    reject('changed_source_binding_path',
           lambda root: next(node for node in root.iter() if node.get('data-source-path')).set(
               'data-source-path', 'document/999'))
    reject('changed_source_attribute_ledger',
           lambda root: next(node for node in root.iter() if node.get('data-source-attributes')).set(
               'data-source-attributes', '{}'))
    reject('duplicate_source_id',
           lambda root: next(node for node in root.iter() if node.get('id') == 'term-00002').set('id', 'term-00001'))
    reject('short_answer_split_outside_group',
           lambda root: setattr(next(node for node in root.iter()
                                     if 'source-inline-part' in node.get('class', '').split()), 'tail', 'غلط '))
    reject('short_part_wrong_marker',
           lambda root: next(node for node in root.iter()
                             if 'source-inline-part' in node.get('class', '').split()).set('data-source-part', 'e'))
    def inject_main(root):
        main = root.find('./body/main')
        node = ET.Element('p', {'dir': 'ltr'})
        node.text = 'injected'
        main.insert(2, node)
    reject('main_level_prose_injection', inject_main)
    def inject_source(root):
        document = by_attr(root, 'data-source-path', 'document')
        node = ET.Element('p')
        node.text = 'anonymous source prose'
        document.insert(0, node)
    reject('anonymous_source_prose_injection', inject_source)
    reject('unresolved_placeholder',
           lambda root: setattr(root.find('./body/main'), 'text', '{{math:0}}'))
    reject('removed_original_correction_description',
           lambda root: next(node for node in root.iter('img')
                             if node.get('data-description-origin') == 'original-correction').set(
                                 'aria-describedby', 'a10-006-word-key'))
    reject('generated_solution_label_reclassified_source',
           lambda root: next(node for node in root.iter()
                             if 'solution-label' in node.get('class', '').split()).set('data-origin', 'source'))
    reject('removed_explicit_solution_title',
           lambda root: parents(root)[by_attr(root, 'data-source-path', 'document/2/1/20/0/1/0')].remove(
               by_attr(root, 'data-source-path', 'document/2/1/20/0/1/0')))
    reject('source_image_mime_changed',
           lambda root: by_attr(root, 'data-source-path', 'document/2/1/17/2/0').set(
               'data-source-image-mime', 'image/png'))
    bad_translation = copy.deepcopy(ctx.translation)
    first_key = next(iter(bad_translation['source_blocks']))
    bad_translation['source_blocks'][first_key] += ' غلط'
    reject('translation_block_tampered_in_memory', translation=bad_translation)
    bad_notice = copy.deepcopy(ctx.notice)
    bad_notice['rights_status'] = 'All images cleared.'
    reject('invented_component_clearance', notice=bad_notice)
    bad_assets = dict(ctx.assets)
    first_asset = next(iter(bad_assets))
    data = bytearray(bad_assets[first_asset])
    data[-1] ^= 1
    bad_assets[first_asset] = bytes(data)
    reject('asset_digest_mutated_in_memory', assets=bad_assets)
    reject('css_table_wrap_removed', css=ctx.local_css.replace(
        'width:330px; white-space:normal', 'width:330px; white-space:nowrap', 1))
    reject('css_image_mirroring_added', css=ctx.local_css + '\nimg{transform:scaleX(-1)}')
    return outcomes


def subprocess_cycle():
    commands = [
        [sys.executable, str(BASE / 'scripts/prepare_a10_006.py')],
        [sys.executable, str(BASE / 'scripts/build_a10_006.py')]
    ]
    outputs = []
    for command in commands:
        completed = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True, encoding='utf-8')
        if completed.returncode:
            raise Failure('subprocess_failed_' + Path(command[-1]).name + '_' + completed.stderr[-500:])
        outputs.append(completed.stdout.strip())
    return {'reader_sha256': file_hash(READER), 'notice_sha256': file_hash(BASE / 'provenance/a10-unit-006-component-notices.json'),
            'reader_bytes': READER.stat().st_size,
            'notice_bytes': (BASE / 'provenance/a10-unit-006-component-notices.json').stat().st_size,
            'stdout': outputs}


def run():
    files_before = {path.resolve(): file_hash(path) for path in stable_files()}
    first_cycle = subprocess_cycle()
    second_cycle = subprocess_cycle()
    if first_cycle != second_cycle:
        raise Failure('two_build_cycles_not_deterministic')
    files_after = {path.resolve(): file_hash(path) for path in stable_files()}
    if files_before != files_after:
        changed = [str(path) for path in files_before if files_before[path] != files_after[path]]
        raise Failure('stable_input_hashes_changed_' + ','.join(changed))
    ctx = Context()
    checks = Checker()
    validate_inputs(ctx, checks)
    validate_reader(ctx, checks)
    derive_arithmetic_checks(ctx, checks)
    mutations = mutation_rejections(ctx)
    artifacts = []
    artifact_paths = stable_files() + [
        *(BASE / row['path'] for row in ctx.manifest['images']),
        BASE / 'provenance/a10-unit-006-component-notices.json',
        READER
    ]
    seen = set()
    for path in artifact_paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        artifacts.append({'path': path.relative_to(ROOT).as_posix(), 'bytes': path.stat().st_size,
                          'sha256': file_hash(path)})
    receipt = {
        'schema': 'independent-source-bound-structural-qa-v1',
        'unit': 'A10-006', 'locale': 'pnb-Arab-PK',
        'source': {'module': 'm82453', 'selection': 'title+complete metadata+opening note+complete first section',
                   'scope_from': ctx.manifest['scope_from'], 'section_start': ctx.manifest['section_start'],
                   'through': ctx.manifest['scope_through_inclusive'],
                   'last_descendant': ctx.manifest['last_descendant_id'],
                   'next_required': ctx.manifest['next_source_id']},
        'counts': {'checks_passed': len(checks.names), 'detached_mutations_rejected': len(mutations),
                   'source_blocks': 187, 'source_ids': 134, 'source_bindings': 604,
                   'mathml_trees': 98, 'mathml_nodes': 737, 'tables': 8, 'table_cells': 97,
                   'actual_header_cells': 15, 'images': 4, 'english_lexical_echoes': 36,
                   'circled_parts': 48, 'short_part_wrappers': 32, 'explicit_newlines': 12},
        'determinism': {'cycles': 2, 'identical': True, **first_cycle},
        'detached_mutations': mutations,
        'verified': checks.names,
        'artifacts': artifacts,
        'limitations': {
            'native_language_review': 'Pending; no native-speaker certification is claimed.',
            'educator_review': 'Pending; source-bound arithmetic checks do not certify pedagogy or all domain conventions.',
            'assistive_technology_review': 'Pending; static DOM/ARIA checks are not a live screen-reader test.',
            'visual_review': 'Independent browser review is owned by the parent. Binary image dimensions/hashes and DOM/CSS overflow contracts are verified here; this receipt is not a visual certification.',
            'source_scope': 'Only the selected opening and complete first section of m82453. The next section, rest of the module, A10 and all five assigned works remain incomplete.',
            'canon': 'Four actual C01–C12 stage receipts guide prose grammar; the one-author prose canon is not specialist mathematical-term authority.',
            'rights': 'Existing audited A10 notice policy retained; media authority rows prove identity, not new clearance.'
        },
        'whole_module_complete': False, 'whole_book_complete': False, 'whole_assignment_complete': False
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('A10-006 QA: ' + str(len(checks.names)) + ' checks, ' + str(len(mutations))
          + ' detached mutations rejected; 2 deterministic prepare/build cycles.')


if __name__ == '__main__':
    run()
