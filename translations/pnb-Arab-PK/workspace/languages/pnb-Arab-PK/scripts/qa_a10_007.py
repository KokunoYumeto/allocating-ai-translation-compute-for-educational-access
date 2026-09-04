"""Independent CNXML-derived structural QA for A10-007; does not import renderer expectations."""
import ast
import copy
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
C = 'http://cnx.rice.edu/cnxml'
M = 'http://www.w3.org/1998/Math/MathML'
MURL = '{' + M + '}'
READER = BASE / 'reader/a10-unit-007.html'
RECEIPT = BASE / 'qa/structural-a10-007.json'
MANIFEST = BASE / 'source-excerpts/manifest-a10-007.json'
TRANSLATION = BASE / 'translations/a10-unit-007.json'
EXCERPT = BASE / 'source-excerpts/a10-unit-007.cnxml'
NOTICE = BASE / 'provenance/a10-unit-007-component-notices.json'
PREPARE = BASE / 'scripts/prepare_a10_007.py'
BUILD = BASE / 'scripts/build_a10_007.py'
CANONICAL = ROOT / 'downloads/complete-upstream/osbooks-prealgebra-bundle/modules/m82453/index.cnxml'
COMPARISON = ROOT / 'downloads/extracted/A10/translated/modules/m82453/index.cnxml'
AUTHORITY = ROOT / 'downloads/extracted/A10/authority/MEDIA_AUTHORITY_MANIFEST.csv'
BAD = re.compile('[\u0a00-\u0a7f\u061c\u200b-\u200f\u202a-\u202e\u2060-\u206f\ufffd]')
NUM = re.compile(r'\d+(?:,\d{3})*(?:\.\d+)?')
TARGET_NUMERAL_WORDS = {'تیجی': '3'}
PARTS = {'ⓐ': 'a', 'ⓑ': 'b', 'ⓒ': 'c', 'ⓓ': 'd', 'ⓔ': 'e'}
STRUCTURAL = {'list', 'table', 'media', 'para', 'note', 'figure'}


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


def compact(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def target_number_tokens(value):
    """Return digits plus explicitly audited Shahmukhi number-word equivalents in order."""
    tokens = [(match.start(), match.group()) for match in NUM.finditer(value)]
    for word, number in TARGET_NUMERAL_WORDS.items():
        pattern = r'(?<![\u0600-\u06ff])' + re.escape(word) + r'(?![\u0600-\u06ff])'
        tokens.extend((match.start(), number) for match in re.finditer(pattern, value))
    return [number for _, number in sorted(tokens)]


def shape(node):
    return (node.tag, tuple(sorted(node.attrib.items())), node.text,
            tuple((shape(child), child.tail) for child in node))


def inner(node):
    return (node.text, tuple((shape(child), child.tail) for child in node))


def tree_hash(node):
    return digest(json.dumps(shape(node), ensure_ascii=False, separators=(',', ':')).encode('utf-8'))


def text(node):
    return ''.join(node.itertext())


def fragment(value):
    return ET.fromstring('<fragment>' + value + '</fragment>')


def fragment_text(value):
    return text(fragment(value))


def parents(root):
    return {child: parent for parent in root.iter() for child in parent}


def paths(root):
    result = {}
    def walk(node, path):
        result[node] = path
        for index, child in enumerate(node):
            walk(child, path + '/' + str(index))
    walk(root, 'document')
    return result


def parse_reader(raw):
    return ET.fromstring(re.sub(r'<!doctype[^>]*>', '', raw, count=1, flags=re.I))


def replace_preserving_tail(root, target, replacement):
    parent_map = parents(root)
    parent = parent_map[target]
    index = list(parent).index(target)
    before = parent.text if index == 0 else parent[index - 1].tail
    combined = (before or '') + replacement + (target.tail or '')
    if index == 0:
        parent.text = combined or None
    else:
        parent[index - 1].tail = combined or None
    parent.remove(target)


def unwrap(root, target):
    parent_map = parents(root)
    parent = parent_map[target]
    index = list(parent).index(target)
    before = parent.text if index == 0 else parent[index - 1].tail
    if target.text:
        if index == 0:
            parent.text = (before or '') + target.text
        else:
            parent[index - 1].tail = (before or '') + target.text
    additions = list(target)
    tail = target.tail
    parent.remove(target)
    for offset, child in enumerate(additions):
        parent.insert(index + offset, child)
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


def derive_key(node, parent, root):
    name = tag(node)
    if name == 'title':
        return parent.get('id') + '/title'
    if name == 'para':
        return node.get('id')
    if name == 'item':
        return parent.get('id') + '/item/' + str(list(parent).index(node) + 1)
    if name == 'note' and (node.text or '').strip():
        return node.get('id')
    if name == 'table':
        return node.get('id') + '/summary'
    if name == 'entry':
        owner = parent
        parent_map = parents(root)
        while tag(owner) != 'table':
            owner = parent_map[owner]
        sections = [section for group in owner if tag(group) == 'tgroup'
                    for section in group if tag(section) in {'thead', 'tbody'}]
        rows = [row for section in sections for row in section if tag(row) == 'row']
        return (owner.get('id') + '/row/' + str(rows.index(parent) + 1)
                + '/entry/' + str(list(parent).index(node) + 1))
    if name == 'media':
        return node.get('id') + '/alt'
    return None


def source_inline_text(node):
    out = node.text or ''
    for child in node:
        if child.tag == MURL + 'math' or tag(child) in STRUCTURAL:
            out += child.tail or ''
        else:
            out += source_inline_text(child) + (child.tail or '')
    return out


def safe_math_value(math):
    def render(node):
        name = tag(node)
        if name == 'math':
            return ''.join(render(child) for child in node)
        if name == 'mrow':
            return ''.join(render(child) for child in node)
        if name in {'mn', 'mo'}:
            return node.text or ''
        if name == 'msup':
            children = list(node)
            if len(children) != 2:
                raise Failure('arithmetic_msup_shape')
            return '(' + render(children[0]) + '**' + render(children[1]) + ')'
        raise Failure('arithmetic_unsupported_' + name)
    value = render(math).rstrip('.,')
    value = value.replace('−', '-').replace('·', '*').replace('÷', '/').replace('[', '(').replace(']', ')')
    value = re.sub(r'(?<=\d)\(', '*(', value)
    value = re.sub(r'\)(?=\d)', ')*', value)
    value = re.sub(r'\)(?=\()', ')*', value)
    parsed = ast.parse(value, mode='eval')
    allowed = (ast.Expression, ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div,
               ast.Pow, ast.USub, ast.UnaryOp, ast.Constant)
    if any(not isinstance(node, allowed) for node in ast.walk(parsed)):
        raise Failure('arithmetic_ast')
    return eval(compile(parsed, '<source-math>', 'eval'), {'__builtins__': {}}, {})


class Context:
    def __init__(self):
        self.manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
        self.translation = json.loads(TRANSLATION.read_text(encoding='utf-8'))
        self.excerpt = ET.parse(EXCERPT).getroot()
        self.section = self.excerpt[0]
        self.parent = parents(self.excerpt)
        self.paths = paths(self.excerpt)
        self.blocks = {}
        self.key_nodes = {}
        for node in self.excerpt.iter():
            key = derive_key(node, self.parent.get(node), self.excerpt)
            if key:
                self.blocks[key] = node
                self.key_nodes[node] = key
        self.reader_raw = READER.read_text(encoding='utf-8')
        self.reader = parse_reader(self.reader_raw)
        self.reader_parent = parents(self.reader)
        self.targets = {node.get('data-source-key'): node for node in self.reader.iter()
                        if node.get('data-source-key')}
        self.notice = json.loads(NOTICE.read_text(encoding='utf-8'))


def stable_files():
    files = [
        BASE / 'plans/A10-007-scope.json', EXCERPT, MANIFEST, TRANSLATION,
        BASE / 'qa/a10-unit-007-language-notes.md',
        BASE / 'canon/examples.json',
        BASE / 'canon/receipts/A10-007-next-unit-20260901T113658158000Z.json',
        BASE / 'canon/receipts/A10-007-draft-20260901T131653162304Z.json',
        BASE / 'canon/receipts/A10-007-revision-20260901T133224609108Z.json',
        BASE / 'canon/receipts/A10-007-qa-20260901T143427234503Z.json',
        ROOT / 'downloads/canon/pnb-Arab-PK/R1.txt',
        ROOT / 'downloads/canon/pnb-Arab-PK/R2.txt',
        ROOT / 'downloads/canon/pnb-Arab-PK/R3.txt',
        BASE / 'scripts/read_canon.py',
        BASE / 'scripts/prepare_a10.py',
        BASE / 'scripts/build_a10.py',
        PREPARE, BUILD, Path(__file__),
        BASE / 'styles/reader.css', BASE / 'sources.lock.json',
        ROOT / 'downloads/complete-upstream/osbooks-prealgebra-bundle/collections/elementary-algebra-2e.collection.xml',
        CANONICAL, COMPARISON, AUTHORITY,
        BASE / 'provenance/A10-release/NOTICE.txt',
        BASE / 'provenance/upstream--osbooks-prealgebra-bundle/LICENSE',
        BASE / 'reader/a10-unit-006.html'
    ]
    return files


def validate_inputs(ctx, checker):
    m, tr = ctx.manifest, ctx.translation
    checker.ok((m['unit'], m['assignment'], m['collection'], m['module'])
               == ('A10-007', 'A10', 'col31130', 'm82453'), 'input_scope')
    checker.ok((tr['unit'], tr['locale'], tr['direction'], tr['canonical_module'])
               == ('A10-007', 'pnb-Arab-PK', 'rtl', 'm82453'), 'translation_scope')
    raw = CANONICAL.read_bytes()
    checker.ok((len(raw), digest(raw)) == (m['full_module_bytes'], m['full_module_sha256']),
               'canonical_size_hash')
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()
    checker.ok(blob == m['canonical_git_blob_sha1'], 'canonical_git_blob')
    witness = m['source_byte_witnesses'][0]
    part = raw[witness['start_byte']:witness['end_byte_exclusive']]
    checker.ok((len(part), digest(part)) == (witness['bytes'], witness['sha256'])
               == (29166, '3dc49717e5bbe76d0c8c1003e1bad065bdc079a9f274d4b55a33eb333cc55770'),
               'section_byte_witness')
    canonical = ET.parse(CANONICAL).getroot()
    content = next(node for node in canonical if tag(node) == 'content')
    checker.ok(len(content) == 8 and content[2].get('id') == m['section_start']
               and content[3].get('id') == m['next_source_id'], 'canonical_section_boundary')
    checker.ok(shape(content[2]) == shape(ctx.section), 'exact_selected_section_tree')
    checker.ok((EXCERPT.stat().st_size, file_hash(EXCERPT)) == (m['excerpt_bytes'], m['excerpt_sha256']),
               'excerpt_size_hash')
    checker.ok((TRANSLATION.stat().st_size, file_hash(TRANSLATION))
               == (m['translation_bytes'], m['translation_sha256']), 'translation_size_hash')
    checker.ok((BASE / m['scope_plan_path']).stat().st_size == m['scope_plan_bytes']
               and file_hash(BASE / m['scope_plan_path']) == m['scope_plan_sha256'], 'plan_size_hash')
    checker.ok((BASE / m['language_notes_path']).stat().st_size == m['language_notes_bytes']
               and file_hash(BASE / m['language_notes_path']) == m['language_notes_sha256'], 'notes_size_hash')
    checker.ok((COMPARISON.stat().st_size, file_hash(COMPARISON))
               == (m['indonesian_comparison_bytes'], m['indonesian_comparison_sha256']), 'comparison_pin')
    checker.ok(file_hash(AUTHORITY) == m['media_authority_manifest_sha256']
               and AUTHORITY.stat().st_size == m['media_authority_manifest_bytes'], 'authority_pin')
    lock = json.loads((BASE / 'sources.lock.json').read_text(encoding='utf-8'))
    pin = next(row for row in lock['repositories'] if row['role'] == 'A10+A20 upstream')
    checker.ok((m['commit'], m['tree']) == (pin['commit'], pin['tree']), 'source_lock_pin')

    ids = [node.get('id') for node in ctx.excerpt.iter() if node is not ctx.excerpt and node.get('id')]
    checker.ok(ids == m['source_ids_in_document_order'] and len(ids) == len(set(ids)) == 111,
               'source_id_sequence')
    checker.ok(len(list(ctx.section.iter())) == 682 and ids[-1] == m['last_descendant_id'],
               'source_element_extent')
    checker.ok(list(ctx.blocks) == m['source_block_keys_in_document_order']
               == list(tr['source_blocks']) and len(ctx.blocks) == 143, 'source_key_sequence')
    checker.ok({key: ctx.paths[node] for key, node in ctx.blocks.items()} == m['source_keys_to_paths'],
               'source_key_paths')
    counts = {}
    for node in ctx.section.iter():
        counts[tag(node)] = counts.get(tag(node), 0) + 1
    checker.ok(counts == m['source_tag_counts'], 'source_tag_counts')
    checker.ok((counts['math'], counts['table'], counts['row'], counts['entry'], counts['media'])
               == (21, 4, 35, 70, 23), 'core_source_counts')
    checker.ok(sum(1 for node in ctx.section.iter() if tag(node) == 'entry'
                   and not len(node) and not (node.text or '').strip()) == 16, 'source_empty_cells')
    checker.ok(sum(1 for node in ctx.section.iter() if tag(node) == 'thead') == 0, 'source_zero_headers')
    checker.ok(sum(1 for node in ctx.section.iter() if tag(node) == 'note' and (node.text or '').strip()) == 1,
               'source_direct_note_count')

    math_records = []
    for owner in ctx.excerpt.iter():
        direct = [child for child in owner if child.tag == MURL + 'math']
        for index, math in enumerate(direct):
            automatic = tag(owner) == 'equation'
            math_records.append({
                'owner_source_key': owner.get('id') if automatic else ctx.key_nodes.get(owner),
                'owner_source_path': ctx.paths[owner],
                'placeholder_index': index,
                'source_path': ctx.paths[math],
                'tree_sha256': tree_hash(math),
                'text': text(math),
                'automatic_equation_owner': automatic
            })
    checker.ok(math_records == m['source_mathml'] and len(math_records) == 21, 'source_math_manifest')
    checker.ok(not m['mathml_changes'], 'zero_math_edits')
    checker.ok(m['source_mathml_comparison']['unequal_source_order_indexes_zero_based'] == [4, 5, 6],
               'comparison_math_differences')
    checker.ok(text([node for node in ctx.section.iter()
                     if tag(node) == 'equation' and node.get('id') == 'fs-id1170654007218'][0])
               == 'ParenthesesPleaseExponentsExcuseMultiplicationDivisionMyDearAdditionSubtractionAuntSally',
               'canonical_mnemonic_math')

    checker.ok(not BAD.search(TRANSLATION.read_text(encoding='utf-8')), 'target_script_controls')
    for key, source in ctx.blocks.items():
        value = tr['source_blocks'][key]
        maths = [child for child in source if child.tag == MURL + 'math']
        children = [child for child in source if tag(child) in STRUCTURAL]
        links = [child for child in source if tag(child) == 'link']
        checker.ok([int(x) for x in re.findall(r'\{\{math:(\d+)\}\}', value)]
                   == list(range(len(maths))), 'translation_math_slots_' + key)
        checker.ok([int(x) for x in re.findall(r'\{\{child:(\d+)\}\}', value)]
                   == list(range(len(children))), 'translation_child_slots_' + key)
        checker.ok([int(x) for x in re.findall(r'\{\{link:(\d+)\}\}', value)]
                   == list(range(len(links))), 'translation_link_slots_' + key)
        parsed = fragment(value)
        checker.ok(len(list(parsed.iter('br')))
                   == sum(tag(child) == 'newline' for child in source), 'translation_newlines_' + key)
        checker.ok(len(list(parsed.iter('strong')))
                   == sum(tag(child) == 'emphasis' and child.get('effect') == 'bold'
                          for child in source), 'translation_bold_' + key)
        source_terms = [child for child in source if tag(child) == 'term']
        target_terms = [node for node in parsed.iter('span')
                        if 'source-term' in node.get('class', '').split()]
        checker.ok([node.get('id') for node in target_terms] == [node.get('id') for node in source_terms],
                   'translation_terms_' + key)
        source_parts = [PARTS[(child.text or '').strip()] for child in source
                        if tag(child) == 'span' and child.get('class') == 'token']
        target_parts = [match[1] for match in re.finditer(r'<bdi\b[^>]*>\(([a-e])\)</bdi>', value)]
        checker.ok(target_parts == source_parts, 'translation_parts_' + key)
        if key.endswith('/summary'):
            source_value = source.get('aria-label') or source.get('summary') or ''
        elif key.endswith('/alt'):
            source_value = source.get('alt') or ''
        else:
            source_value = source_inline_text(source)
        target_value = fragment_text(re.sub(r'\{\{(?:math|child|link):\d+\}\}', '', value))
        source_numbers = NUM.findall(source_value)
        target_number_list = target_number_tokens(target_value)
        if key.endswith('/summary'):
            # Image/table summaries may translate an explicit repeated expression as
            # "the same expression".  Preserve every distinct source numeral while
            # permitting that non-lossy compression and spelled-number digitization.
            numerals_retained = set(source_numbers) <= set(target_number_list)
        else:
            target_numbers = iter(target_number_list)
            numerals_retained = all(any(candidate == number for candidate in target_numbers)
                                    for number in source_numbers)
        checker.ok(numerals_retained, 'translation_numerals_' + key)
    checker.ok(sum(value.count('<strong>') for value in tr['source_blocks'].values()) == 18,
               'target_total_bold')
    checker.ok(tr['source_blocks']['fs-id1167836700561/alt'].find("(4 + 3) ', 7") >= 0,
               'malformed_alt_faithful')
    checker.ok(tr['source_blocks']['fs-id1167836329648/alt'].find('نقط') < 0,
               '006c_no_imported_dot')
    checker.ok('Please Excuse My Dear Aunt Sally.' in tr['source_blocks']['fs-id1170654938531'],
               'english_mnemonic_faithful')
    checker.ok(len(tr['image_alt_overrides']) == 4
               and set(tr['image_alt_overrides']) == set(m['image_alt_overrides']), 'four_alt_overrides')
    checker.ok(not tr['whole_module_complete'] and not tr['whole_book_complete']
               and not tr['whole_assignment_complete'], 'incomplete_claims')


def normalized_block(target, source, ctx):
    clone = copy.deepcopy(target)
    source_path = ctx.paths[source]
    direct_math = [child for child in source if child.tag == MURL + 'math']
    direct_links = [child for child in source if tag(child) == 'link']
    direct_structural = [child for child in source if tag(child) in STRUCTURAL]

    for index, child in enumerate(direct_math):
        matches = [node for node in clone.iter()
                   if node.get('data-source-path') == ctx.paths[child]
                   and node.get('data-source-tag') == 'math']
        if len(matches) != 1:
            raise Failure('rendered_math_placeholder_' + source_path)
        replace_preserving_tail(clone, matches[0], '{{math:' + str(index) + '}}')
    for index, child in enumerate(direct_links):
        matches = [node for node in clone.iter()
                   if node.get('data-source-path') == ctx.paths[child]]
        if len(matches) != 1:
            raise Failure('rendered_link_placeholder_' + source_path)
        replace_preserving_tail(clone, matches[0], '{{link:' + str(index) + '}}')
    for index, child in enumerate(direct_structural):
        matches = [node for node in clone.iter()
                   if node.get('data-source-path') == ctx.paths[child]]
        if len(matches) != 1:
            raise Failure('rendered_child_placeholder_' + source_path)
        replace_preserving_tail(clone, matches[0], '{{child:' + str(index) + '}}')

    while True:
        removable = [node for node in clone.iter() if node is not clone
                     and (node.get('data-origin') == 'renderer-ui'
                          or 'source-original-advisory' in node.get('class', '').split())]
        if not removable:
            break
        replace_preserving_tail(clone, removable[0], '')
    while True:
        wrappers = [node for node in clone.iter() if node is not clone
                    and 'source-inline-part' in node.get('class', '').split()]
        if not wrappers:
            break
        unwrap(clone, wrappers[0])
    for node in clone.iter():
        for name in list(node.attrib):
            if name.startswith('data-source-'):
                del node.attrib[name]
    return inner(clone)


def find_parent_with(node, parent_map, predicate):
    current = node
    while current in parent_map:
        current = parent_map[current]
        if predicate(current):
            return current
    return None


def validate_dom(ctx, checker, root=None):
    if root is None:
        root = ctx.reader
    m, tr = ctx.manifest, ctx.translation
    parent_map = parents(root)
    checker.ok(root.get('lang') == 'pnb-Arab-PK' and root.get('dir') == 'rtl', 'reader_locale_direction')
    body = root.find('body')
    checker.ok(body is not None and [tag(child) for child in body] == ['header', 'main', 'footer'],
               'body_frame')
    main = body.find('main')
    checker.ok(main is not None and len(main) == 6, 'main_exact_child_count')
    checker.ok(main[0].get('data-origin') == 'renderer-ui'
                and main[1].get('id') == 'a10-007-before'
                and 'source-document' in main[2].get('class', '').split()
               and main[3].get('id') == 'a10-007-original-bridge'
               and any(node.get('id') == 'a10-007-image-terms' for node in main[4].iter())
                and main[5].get('data-origin') == 'renderer-ui', 'main_exact_shape')
    source_document = main[2]
    checker.ok(len(source_document) == 1
               and source_document[0].get('data-source-path') == ctx.paths[ctx.section]
               and not (source_document.text or '').strip()
               and all(not (child.tail or '').strip() for child in source_document),
               'source_document_exact_boundary')
    checker.ok(not BAD.search(ET.tostring(root, encoding='unicode')), 'reader_script_controls')

    source_targets = [node for node in root.iter() if node.get('data-source-path') is not None]
    expected_nodes = [node for node in ctx.excerpt.iter()
                      if not node.tag.startswith(MURL) or node.tag == MURL + 'math']
    checker.ok([node.get('data-source-path') for node in source_targets]
               == [ctx.paths[node] for node in expected_nodes], 'all_source_paths_order')
    checker.ok(len(source_targets) == len(expected_nodes)
               and len({node.get('data-source-path') for node in source_targets}) == len(expected_nodes),
               'source_binding_bijection')
    for source, target in zip(expected_nodes, source_targets):
        checker.ok(target.get('data-source-tag') == tag(source)
                   and target.get('data-source-qname') == source.tag
                   and target.get('data-source-attributes') == compact(source.attrib),
                   'source_binding_' + ctx.paths[source])

    source_ids = m['source_ids_in_document_order']
    output_ids = [node.get('id') for node in root.iter() if node.get('id')]
    checker.ok([value for value in output_ids if value in set(source_ids)] == source_ids,
               'rendered_source_id_order')
    checker.ok(len(output_ids) == len(set(output_ids)), 'unique_output_ids')

    targets = [node for node in root.iter() if node.get('data-source-key')]
    checker.ok([node.get('data-source-key') for node in targets] == list(tr['source_blocks'])
               and len(targets) == 143, 'rendered_key_order')
    target_map = {node.get('data-source-key'): node for node in targets}
    for key, source in ctx.blocks.items():
        target = target_map[key]
        if key.endswith('/alt'):
            image = next((node for node in target.iter() if tag(node) == 'img'), None)
            checker.ok(image is not None and image.get('data-source-alt') == tr['source_blocks'][key],
                       'rendered_faithful_alt_' + key)
        elif key.endswith('/summary'):
            table = next((node for node in target.iter() if tag(node) == 'table'), None)
            checker.ok(table is not None and table.get('data-source-summary') == tr['source_blocks'][key],
                       'rendered_faithful_summary_' + key)
        else:
            checker.ok(normalized_block(target, source, ctx) == inner(fragment(tr['source_blocks'][key])),
                       'rendered_block_' + key)

    source_maths = [node for node in ctx.excerpt.iter() if node.tag == MURL + 'math']
    math_spans = [node for node in root.iter()
                  if node.get('data-source-tag') == 'math' and 'math-isolate' in node.get('class', '').split()]
    checker.ok(len(math_spans) == len(source_maths) == 21, 'rendered_math_count')
    for index, (source, span) in enumerate(zip(source_maths, math_spans)):
        children = list(span)
        checker.ok(span.get('dir') == 'ltr' and len(children) == 1 and children[0].tag == MURL + 'math',
                   'math_wrapper_' + str(index))
        clone = copy.deepcopy(children[0])
        checker.ok(clone.get('dir') == 'ltr' and clone.get('data-source-text-edits') is None,
                   'math_root_presentation_' + str(index))
        del clone.attrib['dir']
        checker.ok(shape(clone) == shape(source), 'math_exact_tree_' + str(index))
    checker.ok('ParenthesesPleaseExponentsExcuseMultiplicationDivisionMyDearAdditionSubtractionAuntSally'
               in text(math_spans[6]), 'rendered_mnemonic_math')
    mnemonic = target_map['fs-id1170654938531']
    checker.ok('Please Excuse My Dear Aunt Sally.' in text(mnemonic), 'rendered_mnemonic_prose')

    table_wrappers = [target_map[row['id'] + '/summary'] for row in m['tables']]
    checker.ok(len(table_wrappers) == 4, 'rendered_table_count')
    total_rows = total_cells = total_empty = total_headers = 0
    for spec, wrapper in zip(m['tables'], table_wrappers):
        table = next(node for node in wrapper.iter() if tag(node) == 'table')
        scroll = find_parent_with(table, parent_map,
                                  lambda node: 'source-table-scroll' in node.get('class', '').split())
        checker.ok(table.get('dir') == 'ltr' and table.get('data-source-tgroup-cols') == '2'
                   and '--source-table-width:660px' in table.get('style', ''), 'table_ltr_width_' + spec['id'])
        checker.ok(scroll is not None and scroll.get('dir') == 'ltr' and scroll.get('tabindex') == '0',
                   'table_local_scroll_' + spec['id'])
        rows = [node for node in table.iter() if tag(node) == 'tr']
        cells = [node for node in table.iter() if tag(node) in {'td', 'th'}]
        headers = [node for node in cells if tag(node) == 'th']
        source_empty_keys = [key for key in tr['source_blocks']
                             if key.startswith(spec['id'] + '/row/') and tr['source_blocks'][key] == '']
        total_rows += len(rows)
        total_cells += len(cells)
        total_headers += len(headers)
        total_empty += len(source_empty_keys)
        checker.ok((len(rows), len(cells), len(source_empty_keys), len(headers))
                   == (spec['rows'], spec['cells'], spec['empty_cells'], 0),
                   'table_geometry_' + spec['id'])
    checker.ok((total_rows, total_cells, total_empty, total_headers) == (35, 70, 16, 0),
               'all_table_geometry')

    with AUTHORITY.open(encoding='utf-8-sig', newline='') as handle:
        authority = {row['relative_path']: row for row in csv.DictReader(handle)}
    image_targets = [target_map[row['media_id'] + '/alt'] for row in m['images']]
    checker.ok(len(image_targets) == 23, 'rendered_image_count')
    for spec, wrapper in zip(m['images'], image_targets):
        image = next(node for node in wrapper.iter() if tag(node) == 'img')
        key = spec['media_id'] + '/alt'
        override = tr['image_alt_overrides'].get(key)
        expected_alt = fragment_text(override['alt']) if override else fragment_text(tr['source_blocks'][key])
        checker.ok(image.get('src') == '../' + spec['path']
                   and image.get('alt') == expected_alt
                   and image.get('data-source-alt') == tr['source_blocks'][key], 'image_alt_src_' + key)
        checker.ok(image.get('data-source-image-mime') == 'image/png'
                   and image.get('data-rendered-image-mime') == 'image/jpeg'
                   and image.get('width') == str(spec['width'])
                   and image.get('height') == str(spec['height']), 'image_mime_dims_' + key)
        described = set((image.get('aria-describedby') or '').split())
        expected_notes = {spec['original_bilingual_key_id']}
        expected_notes.update(row['note_id'] for row in tr['source_corrections'] if key in row['source_keys'])
        checker.ok(expected_notes <= described
                   and all(any(node.get('id') == note for node in root.iter()) for note in expected_notes),
                   'image_description_targets_' + key)
        scroll = find_parent_with(image, parent_map,
                                  lambda node: 'figure-scroll' in node.get('class', '').split())
        checker.ok(scroll is not None and scroll.get('dir') == 'ltr' and scroll.get('tabindex') == '0',
                   'image_local_scroll_' + key)
        media_source = ctx.blocks[key]
        entry_source = find_parent_with(media_source, ctx.parent, lambda node: tag(node) == 'entry')
        target_cell = find_parent_with(wrapper, parent_map, lambda node: tag(node) in {'td', 'th'})
        checker.ok(entry_source is not None and target_cell is not None
                   and target_cell.get('data-source-path') == ctx.paths[entry_source],
                   'image_source_cell_ancestry_' + key)
        data = (BASE / spec['path']).read_bytes()
        checker.ok((len(data), digest(data), jpeg_dimensions(data))
                   == (spec['bytes'], spec['sha256'], (spec['width'], spec['height'])),
                   'image_bytes_' + key)
        checker.ok(authority[spec['source_path']] == spec['existing_media_authority_row'],
                   'image_authority_' + key)

    grouped = [node for node in root.iter() if 'source-inline-part' in node.get('class', '').split()]
    expected_grouped = [row for row in m['token_owners'] if row['group_short_parts']]
    checker.ok(len(grouped) == 10 and len(expected_grouped) == 5, 'part_group_count')
    for record in expected_grouped:
        owner = target_map[record['key']]
        wrappers = [node for node in owner.iter()
                    if 'source-inline-part' in node.get('class', '').split()]
        checker.ok([node.get('data-source-part') for node in wrappers]
                   == [label.strip('()') for label in record['display_labels']], 'part_markers_' + record['key'])
        for wrapper, label in zip(wrappers, record['display_labels']):
            checker.ok(label in text(wrapper) and not any(tag(node) in {'table', 'br'} for node in wrapper.iter()),
                       'part_content_' + record['key'] + '_' + label)
    for key in ('fs-id1167836283034', 'fs-id1167836522115'):
        owner = target_map[key]
        checker.ok(not any('source-inline-part' in node.get('class', '').split() for node in owner.iter())
                   and any(tag(node) == 'table' for node in owner.iter())
                   and any(tag(node) == 'br' for node in owner.iter()), 'table_part_not_grouped_' + key)

    direct = target_map['fs-id1166425080552']
    checker.ok(tag(direct) == 'aside' and 'source-direct-note' in direct.get('class', '').split(),
               'direct_note_semantics')
    checker.ok('Game of 24' in text(direct) and not any(tag(node) == 'a' for node in direct.iter()),
               'game24_no_invented_link')
    checker.ok(sum(1 for node in root.iter() if tag(node) == 'strong'
                   and node.get('data-source-tag') == 'emphasis') == 18, 'rendered_bold_bindings')
    checker.ok(len([node for node in root.iter() if 'example-label' in node.get('class', '').split()]) == 3,
               'generated_example_labels')
    checker.ok(len([node for node in root.iter() if 'solution-label' in node.get('class', '').split()]) == 6,
               'generated_tryit_solution_labels')
    checker.ok(len([node for node in root.iter() if node.get('data-source-key', '').endswith('/title')
                    and node.get('data-source-key') in {'fs-id1170654939340/title',
                                                       'fs-id1170655114295/title',
                                                       'fs-id1170654914329/title'}]) == 3,
               'explicit_solution_titles')

    footer = body.find('footer')
    footer_text = text(footer)
    checker.ok(footer.get('id') == 'credits' and footer.get('dir') == 'ltr'
               and all(name in footer_text for name in ('Lynn Marecek', 'MaryAnne Anthony-Smith',
                                                        'Andrea Honeycutt Mathis')), 'footer_authors')
    checker.ok('Attribution-NonCommercial-ShareAlike 4.0' in footer_text
               and 'No new clearance is asserted' in footer_text
               and 'do not endorse' in footer_text, 'footer_rights_nonendorsement')
    checker.ok('not a complete module' in footer_text and 'not training or fine-tuning data' in footer_text,
               'footer_incomplete_nontraining')
    checker.ok('Twenty-three original JPEGs' in footer_text and 'image/png' in footer_text,
               'footer_image_mime_disclosure')

    ids = {node.get('id') for node in root.iter() if node.get('id')}
    for node in root.iter():
        for name in ('href', 'src'):
            target = node.get(name)
            if not target:
                continue
            url = urlsplit(target)
            if url.scheme or url.netloc:
                checker.ok(url.scheme in {'http', 'https'}, 'external_link_scheme')
                continue
            if url.path:
                path = (READER.parent / unquote(url.path)).resolve()
                checker.ok(path.is_relative_to(BASE.resolve()) and path.is_file(), 'local_path_' + target)
                if url.fragment:
                    other = parse_reader(path.read_text(encoding='utf-8'))
                    checker.ok(any(item.get('id') == unquote(url.fragment) for item in other.iter()),
                               'cross_fragment_' + target)
            else:
                checker.ok(unquote(url.fragment) in ids, 'local_fragment_' + target)


def validate_arithmetic(ctx, checker):
    exercises = [node for node in ctx.section.iter() if tag(node) == 'exercise']
    checker.ok(len(exercises) == 9, 'arithmetic_exercise_count')
    for index, exercise in enumerate(exercises):
        problem = next(node for node in exercise if tag(node) == 'problem')
        solution = next(node for node in exercise if tag(node) == 'solution')
        questions = [node for node in problem.iter() if node.tag == MURL + 'math']
        answers = []
        tables = [node for node in solution.iter() if tag(node) == 'table']
        if tables:
            for table in tables:
                media = [node for node in table.iter() if tag(node) == 'media']
                values = NUM.findall(media[-1].get('alt') or '')
                answers.append(int(values[-1]))
        else:
            for para in [node for node in solution.iter() if tag(node) == 'para']:
                direct = ''.join(part for part in source_inline_text(para))
                answers.extend(int(value) for value in NUM.findall(direct))
        values = [safe_math_value(node) for node in questions]
        checker.ok(values == answers, 'source_arithmetic_' + str(index))
    checker.ok([row['answer'] for row in ctx.manifest['source_answer_arithmetic']]
               == [25,49,2,14,35,99,15,16,23,13,86,1], 'manifest_arithmetic_order')


def validate_notice(ctx, checker, notice=None):
    notice = notice or ctx.notice
    m = ctx.manifest
    checker.ok((notice['schema'], notice['unit'], notice['module'], notice['collection'])
               == ('a10-retained-component-evidence-v1', 'A10-007', 'm82453', 'col31130'),
               'notice_scope')
    checker.ok(notice['manifest_sha256'] == file_hash(MANIFEST)
               and notice['excerpt_sha256'] == m['excerpt_sha256'], 'notice_input_hashes')
    checker.ok(len(notice['images']) == 23, 'notice_image_count')
    for row, spec in zip(notice['images'], m['images']):
        checker.ok((row['media_id'], row['source_path'], row['path'], row['sha256'], row['bytes'])
                   == (spec['media_id'], spec['source_path'], spec['path'], spec['sha256'], spec['bytes']),
                   'notice_image_' + spec['media_id'])
        checker.ok(row['source_declared_mime'] == 'image/png'
                   and row['actual_mime'] == 'image/jpeg'
                   and 'Not newly assessed' in row['component_clearance'], 'notice_image_rights_' + spec['media_id'])
    checker.ok('No new component-specific clearance' in notice['rights_status']
               and 'not clearance' in notice['credit_limit']
               and 'component-specific credits and restrictions' in notice['existing_license_statement'],
               'notice_rights_limits')
    checker.ok(not notice['whole_module_translation_complete']
               and not notice['whole_book_translation_complete']
               and not notice['whole_assignment_complete'], 'notice_incomplete')
    checker.ok(notice['release_notice_verbatim']
               == (BASE / 'provenance/A10-release/NOTICE.txt').read_text(encoding='utf-8'),
               'notice_release_verbatim')


def run_cycle():
    for script in (PREPARE, BUILD):
        result = subprocess.run([sys.executable, str(script)], cwd=ROOT, capture_output=True, text=True)
        if result.returncode:
            raise Failure('subprocess_' + script.stem + ':' + result.stdout + result.stderr)
    return {
        'reader': file_hash(READER),
        'notice': file_hash(NOTICE),
        'assets': [file_hash(BASE / row['path'])
                   for row in json.loads(MANIFEST.read_text(encoding='utf-8'))['images']]
    }


def expect_failure(name, action, mutations):
    try:
        action()
    except (Failure, AssertionError, ValueError, KeyError, IndexError, SyntaxError):
        mutations.append(name)
        return
    raise Failure('mutation_survived_' + name)


def detached_mutations(ctx):
    mutations = []
    def dom_case(name, mutate):
        altered = copy.deepcopy(ctx.reader)
        mutate(altered)
        expect_failure(name, lambda: validate_dom(ctx, Checker(), altered), mutations)

    def target(root, key):
        return next(node for node in root.iter() if node.get('data-source-key') == key)

    dom_case('changed_answer', lambda root: setattr(target(root, 'fs-id1170654936134'), 'text', '17'))
    def change_math(root):
        node = next(node for node in root.iter() if tag(node) == 'mn' and (node.text or '') == '4')
        node.text = '5'
    dom_case('changed_math_number', change_math)
    dom_case('math_direction_removed', lambda root: next(node for node in root.iter()
             if node.tag == MURL + 'math').attrib.pop('dir'))
    def swap_media(root):
        a = target(root, 'fs-id1167836282522/alt')
        b = target(root, 'fs-id1167836477496/alt')
        pa, pb = parents(root)[a], parents(root)[b]
        ia, ib = list(pa).index(a), list(pb).index(b)
        pa.remove(a); pb.remove(b); pa.insert(ia, b); pb.insert(ib, a)
    dom_case('switched_media_cells', swap_media)
    dom_case('changed_image_src', lambda root: next(node for node in target(
             root, 'fs-id1167836700561/alt').iter() if tag(node) == 'img').set(
             'src', '../assets/a10/CNX_ElemAlg_Figure_01_02_006b_img_new.jpg'))
    dom_case('changed_faithful_alt', lambda root: next(node for node in target(
             root, 'fs-id1167836700561/alt').iter() if tag(node) == 'img').set('data-source-alt', 'بدلیا'))
    dom_case('missing_override_description', lambda root: next(node for node in target(
             root, 'fs-id1167836700561/alt').iter() if tag(node) == 'img').set('aria-describedby', 'a10-007-image-trace'))
    def make_header(root):
        cell = next(node for node in root.iter() if tag(node) == 'td')
        cell.tag = 'th'
    dom_case('invented_table_header', make_header)
    def delete_empty(root):
        cell = target(root, 'fs-id1167833022118/row/1/entry/1')
        parents(root)[cell].remove(cell)
    dom_case('deleted_empty_cell', delete_empty)
    def split_part(root):
        owner = target(root, 'fs-id1170654942951')
        wrapper = next(node for node in owner.iter() if node.get('data-source-part') == 'a')
        wrapper.tail = (wrapper.tail or '') + '2'
        for node in wrapper.iter():
            if node.text == '2':
                node.text = ''
                break
    dom_case('answer_outside_part_group', split_part)
    def group_table_owner(root):
        table = next(node for node in target(root, 'fs-id1167836283034').iter() if tag(node) == 'table')
        table.set('class', (table.get('class', '') + ' source-inline-part').strip())
        table.set('data-source-part', 'a')
    dom_case('table_inside_part_group', group_table_owner)
    dom_case('wrong_part_marker', lambda root: next(node for node in root.iter()
             if 'source-inline-part' in node.get('class', '').split()).set('data-source-part', 'e'))
    dom_case('changed_direct_note', lambda root: setattr(target(root, 'fs-id1166425080552'), 'text', 'بدلیا'))
    def link_game(root):
        note = target(root, 'fs-id1166425080552')
        ET.SubElement(note, 'a', {'href': 'https://example.invalid'}).text = 'کھیل'
    dom_case('invented_game_link', link_game)
    dom_case('duplicate_source_id', lambda root: target(root, 'fs-id1170654905788').set('id', 'fs-id1170655225397'))
    def inject_source(root):
        document = next(node for node in root.iter() if 'source-document' in node.get('class', '').split())
        ET.SubElement(document, 'p').text = 'گھڑی ہوئی ماخذی لکھت'
    dom_case('source_document_injection', inject_source)
    def inject_main(root):
        main = root.find('body').find('main')
        main.insert(1, ET.Element('p', {'dir': 'ltr'}))
        main[1].text = 'injected'
    dom_case('main_frame_injection', inject_main)
    def mnemonic(root):
        node = target(root, 'fs-id1170654938531')
        for item in node.iter():
            if item.text and 'Please Excuse' in item.text:
                item.text = item.text.replace('Please', 'Kindly')
                return
        raise Failure('mutation_setup_mnemonic')
    dom_case('changed_mnemonic', mnemonic)
    def emphasis(root):
        node = next(node for node in root.iter()
                    if tag(node) == 'strong' and node.get('data-source-tag') == 'emphasis')
        node.tag = 'b'
    dom_case('changed_source_emphasis', emphasis)
    dom_case('changed_source_mime_trace', lambda root: next(node for node in target(
             root, 'fs-id1167836282522/alt').iter() if tag(node) == 'img').set('data-source-image-mime', 'image/jpeg'))
    dom_case('table_direction_rtl', lambda root: next(node for node in root.iter()
             if tag(node) == 'table').set('dir', 'rtl'))

    bad_notice = copy.deepcopy(ctx.notice)
    bad_notice['rights_status'] = 'cleared'
    expect_failure('notice_clearance_mutation', lambda: validate_notice(ctx, Checker(), bad_notice), mutations)
    spec = ctx.manifest['images'][0]
    data = (BASE / spec['path']).read_bytes() + b'x'
    expect_failure('asset_digest_mutation',
                   lambda: (_ for _ in ()).throw(Failure('asset_digest'))
                   if digest(data) != spec['sha256'] else None, mutations)
    return mutations


def artifact_hashes(ctx):
    files = stable_files() + [NOTICE, READER] + [BASE / row['path'] for row in ctx.manifest['images']]
    return {path.relative_to(ROOT).as_posix(): file_hash(path) for path in files}


def main():
    stable_before = {path.relative_to(ROOT).as_posix(): file_hash(path) for path in stable_files()}
    first = run_cycle()
    second = run_cycle()
    if first != second:
        raise Failure('deterministic_two_cycle_output')
    stable_after = {path.relative_to(ROOT).as_posix(): file_hash(path) for path in stable_files()}
    if stable_before != stable_after:
        raise Failure('stable_input_hashes')

    ctx = Context()
    checker = Checker()
    validate_inputs(ctx, checker)
    validate_dom(ctx, checker)
    validate_arithmetic(ctx, checker)
    validate_notice(ctx, checker)
    mutations = detached_mutations(ctx)

    receipt = {
        'schema': 'pnb-structural-qa-v1',
        'unit': 'A10-007',
        'scope': {
            'section': ctx.manifest['section_start'],
            'through': ctx.manifest['scope_through_inclusive'],
            'next_required': ctx.manifest['next_source_id']
        },
        'checks_passed': len(checker.names),
        'detached_mutations_rejected': len(mutations),
        'mutation_names': mutations,
        'cycles': 2,
        'deterministic_outputs': first,
        'source_counts': {
            'source_blocks': 143, 'source_ids': 111, 'source_elements': 682,
            'mathml_trees': 21, 'tables': 4, 'rows': 35, 'cells': 70,
            'empty_cells': 16, 'header_cells': 0, 'images': 23,
            'part_labels': 12, 'newlines': 3, 'direct_text_notes': 1
        },
        'artifact_hashes': artifact_hashes(ctx),
        'limitations': {
            'native_speaker_review': 'pending',
            'mathematics_educator_review': 'pending',
            'assistive_technology_review': 'pending',
            'visual_review': 'pending independent browser review; exact pixels/dimensions were inspected at source-study stage',
            'historical_activity_context': 'No universal historical date or current Game of24 availability is certified.',
            'coverage': 'Complete one section only; m82453,A10,the five works and whole assignment remain incomplete.'
        }
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n',
                       encoding='utf-8', newline='\n')
    print('QA A10-007:' + str(len(checker.names)) + 'checks/'
          + str(len(mutations)) + 'mutations/2cycles; reader=' + first['reader'])


if __name__ == '__main__':
    main()
