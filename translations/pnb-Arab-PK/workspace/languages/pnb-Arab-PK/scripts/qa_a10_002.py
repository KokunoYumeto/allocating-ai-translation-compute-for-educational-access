"""Independent CNXML-derived QA for A10-002; mutations are detached/in-memory."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from collections import Counter
import copy
import csv
import hashlib
import html
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as E

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
MANIFEST = BASE / 'source-excerpts/manifest-a10-002.json'
TRANSLATION = BASE / 'translations/a10-unit-002.json'
READER = BASE / 'reader/a10-unit-002.html'
NOTICES = BASE / 'provenance/a10-unit-002-component-notices.json'
RECEIPT = BASE / 'qa/structural-a10-002.json'
MATH = 'http://www.w3.org/1998/Math/MathML'
BLOCKS = {'media', 'table', 'list'}
FORBIDDEN = re.compile('[\u0a00-\u0a7f\ufffd\u061c\u200b\u200e\u200f\u202a-\u202e\u2066-\u2069]')
NUMS = re.compile(r'\d+(?:,\d{3})*')


def check(name, condition):
    if not condition:
        raise AssertionError(name)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local(node):
    return node.tag.rsplit('}', 1)[-1]


def text(node):
    return ''.join(node.itertext())


def parents(root):
    return {c: n for n in root.iter() for c in n}


def identified(root, sid):
    found = [n for n in root.iter() if n.get('id') == sid]
    check('unique_id:' + sid, len(found) == 1)
    return found[0]


def signature(node):
    return node.tag, tuple(sorted(node.attrib.items())), node.text, tuple((signature(c), c.tail) for c in node)


def fragment(value):
    return E.fromstring('<fragment>' + value.replace('<br>', '<br/>') + '</fragment>')


def parse_reader(value):
    value = value[value.index('<html'):]
    value = re.sub(r'<(meta|img|br|col)\b([^<>]*?)(?<!/)>', r'<\1\2/>', value)
    return E.fromstring(value)


def jpeg_dimensions(data):
    check('jpeg_signature', data[:2] == b'\xff\xd8')
    i = 2
    while i < len(data):
        check('jpeg_marker', data[i] == 255)
        while data[i] == 255:
            i += 1
        marker = data[i]
        i += 1
        if marker in {1, 0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
            continue
        size = int.from_bytes(data[i:i + 2], 'big')
        check('jpeg_segment', size >= 2 and i + size <= len(data))
        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
            return int.from_bytes(data[i + 5:i + 7], 'big'), int.from_bytes(data[i + 3:i + 5], 'big')
        check('jpeg_frame_before_scan', marker != 0xDA)
        i += size
    raise AssertionError('jpeg_missing_frame')


def source_specs(source):
    p = parents(source)
    specs = {}
    for n in source.iter():
        name = local(n)
        if name == 'para':
            key = n.get('id')
        elif name == 'title':
            key = p[n].get('id') + '/title'
        elif name == 'media':
            key = n.get('id') + '/alt'
        elif name == 'table':
            key = n.get('id') + '/summary'
        elif name == 'item':
            key = p[n].get('id') + '/item/' + str(list(p[n]).index(n) + 1)
        elif name == 'entry':
            row, body = p[n], p[p[n]]
            table = p[p[body]]
            key = table.get('id') + '/row/' + str(list(body).index(row) + 1) + '/entry/' + str(list(row).index(n) + 1)
        else:
            continue
        specs[key] = n
    return specs


def target_block(doc, source, key, original):
    if original.get('id'):
        return identified(doc, original.get('id'))
    p = parents(source)
    if local(original) == 'title':
        owner = identified(doc, p[original].get('id'))
        matches = [n for n in owner if n.get('data-source-tag') == 'title']
        check('one_source_title:' + key, len(matches) == 1)
        return matches[0]
    if local(original) == 'item':
        return identified(doc, p[original].get('id')).findall('li')[int(key.rsplit('/', 1)[-1]) - 1]
    matches = [n for n in doc.iter('td') if n.get('data-source-key') == key]
    check('one_source_cell:' + key, len(matches) == 1)
    return matches[0]


def source_prose(node):
    result = node.text or ''
    for c in node:
        if local(c) not in BLOCKS | {'math', 'link'} and not (local(c) == 'span' and c.get('class') == 'token'):
            result += source_prose(c)
        result += c.tail or ''
    return result


def replace_child(parent, child, replacement):
    index = list(parent).index(child)
    value = replacement + (child.tail or '')
    if index:
        parent[index - 1].tail = (parent[index - 1].tail or '') + value
    else:
        parent.text = (parent.text or '') + value
    parent.remove(child)


def unwrap(parent, wrapper):
    index = list(parent).index(wrapper)
    children = list(wrapper)
    check('group_starts_with_child', not wrapper.text)
    parent.remove(wrapper)
    for offset, child in enumerate(children):
        parent.insert(index + offset, child)
    if children:
        children[-1].tail = ((children[-1].tail or '') + (wrapper.tail or '')) or None


def expected_groups(expected):
    starts = [i for i, n in enumerate(expected) if n.tag == 'bdi' and re.fullmatch(r'\([a-c]\)', n.text or '')]
    groups = []
    for j, start in enumerate(starts):
        end = starts[j + 1] if j + 1 < len(starts) else len(expected)
        value = ''.join(text(n) + (n.tail or '') for n in list(expected)[start:end]).strip()
        groups.append((expected[start].text[1], value))
    return groups


def validate_source(source, manifest, report=check):
    canonical_path = ROOT / manifest['canonical_local_path']
    data = canonical_path.read_bytes()
    report('canonical_size_hash', len(data) == manifest['full_module_bytes'] and sha(canonical_path) == manifest['full_module_sha256'])
    blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    report('canonical_git_blob', blob == manifest['canonical_git_blob_sha1'])
    full = E.fromstring(data)
    section = identified(full, 'fs-id1170655083568')
    fullparents = parents(full)
    parent = fullparents[section]
    report('twenty_child_remainder', len(section) == 33 and len(source) == 1 and len(source[0]) == 20
           and [signature(n) for n in source[0]] == [signature(n) for n in list(section)[13:]])
    report('section_container_unchanged', source[0].tag == section.tag and source[0].attrib == section.attrib)
    report('exact_boundaries', source[0][0].get('id') == manifest['scope_from'] == 'fs-id1170655113270'
           and source[0][-1].get('id') == manifest['scope_through_inclusive'] == 'fs-id1170655197222'
           and list(parent)[list(parent).index(section) + 1].get('id') == manifest['next_source_id'] == 'newelem_para01')
    report('excerpt_hash', sha(BASE / 'source-excerpts/a10-unit-002.cnxml') == manifest['excerpt_sha256'])
    report('incomplete_assignment_explicit', manifest['whole_assignment_complete'] is False)
    kinds = Counter(local(n) for n in source.iter())
    count_fields = {'para': 'paragraphs', 'title': 'titles', 'item': 'list_items', 'media': 'media',
                    'math': 'mathml_trees', 'table': 'cnxml_tables', 'figure': 'figures', 'image': 'images',
                    'link': 'source_links', 'note': 'notes', 'example': 'examples', 'exercise': 'exercises',
                    'solution': 'solutions', 'term': 'terms', 'newline': 'newlines', 'entry': 'table_cells'}
    report('manifest_counts_source_derived', all(kinds[k] == manifest['source_counts'][v] for k, v in count_fields.items()))
    return source_specs(source)


def validate_dom(doc, source, manifest, translation, report=check):
    specs = source_specs(source)
    sourceids = [n.get('id') for n in source.iter() if n is not source and n.get('id')]
    ids = [n.get('id') for n in doc.iter() if n.get('id')]
    report('unique_ids', len(ids) == len(set(ids)))
    report('all108_source_ids_order', len(sourceids) == 108 and sourceids == manifest['source_ids_in_document_order']
           and [i for i in ids if i in sourceids] == sourceids)
    report('92_source_keys_order', len(specs) == 92 and list(specs) == list(translation['source_blocks'])
           == manifest['source_block_keys_in_document_order'])
    report('locale_and_rtl', doc.get('lang') == 'pnb-Arab-PK' and doc.get('dir') == 'rtl')
    # Bind the page frame too: otherwise a new, correctly LTR-isolated paragraph
    # outside the retained source section can evade every keyed-block check.
    bodies = doc.findall('body')
    report('one_body_with_exact_frame', len(bodies) == 1 and
           [n.tag for n in bodies[0]] == ['header', 'main', 'footer'])
    body = bodies[0]
    main = body.find('main')
    report('body_and_main_no_anonymous_text', not (body.text or '').strip()
           and all(not (n.tail or '').strip() for n in body)
           and not (main.text or '').strip()
           and all(not (n.tail or '').strip() for n in main))
    report('exact_main_children_order', [(n.tag, n.get('id'), n.get('class')) for n in main] == [
        ('p', None, 'source-label'), ('section', 'fs-id1170655083568', 'translated'),
        ('section', 'a10-002-original-bridge', 'bridge'), ('p', None, 'status')])
    expected_label = E.fromstring('<p class="source-label">ماخذ: <bdi dir="ltr" lang="en">OpenStax Elementary Algebra 2e</bdi>، باب <bdi dir="ltr" lang="en">Foundations</bdi>، سبق «'
        + html.escape(manifest['module_title_pnb'])
        + '»۔ ایتھے پہلے سیکشن دا باقی حصہ ترجمہ کیتا گیا اے؛ پورا سبق یا پوری کتاب نہیں۔</p>')
    expected_status = E.fromstring('<p class="status">ایس سبق دا اگلا ماخذی پیراگراف متغیرات بارے اے؛ اوہ ایس حصے وچ شامل نہیں۔ پنجاں مقررہ کتاباں دا پورا کم ہن وی جاری اے۔</p>')
    report('exact_source_label_and_continuation', signature(main[0]) == signature(expected_label)
           and signature(main[-1]) == signature(expected_status))
    sp, dp = parents(source), parents(doc)

    def ancestry(n, mapping):
        result = []
        while n in mapping:
            n = mapping[n]
            if n.get('id') in sourceids:
                result.append(n.get('id'))
        return result

    for n in source.iter():
        if n is not source and n.get('id'):
            report('source_ancestry:' + n.get('id'), ancestry(n, sp) == ancestry(identified(doc, n.get('id')), dp))
    report('no_invalid_block_in_p', all(not any(local(c) in {'div', 'p', 'section', 'aside', 'table', 'ol', 'ul', 'figure'}
           for c in n.iter() if c is not n) for n in doc.iter('p')))
    report('all_bdi_ltr', all(n.get('dir') == 'ltr' for n in doc.iter('bdi')))

    def direction(n):
        while n is not None:
            if n.get('dir'):
                return n.get('dir')
            n = dp.get(n)
        return None

    report('english_lanes_ltr', all(direction(n) == 'ltr' for n in doc.iter() if n.get('lang') == 'en'))
    for n in doc.find('body').iter():
        for value in [n.text or '', *[c.tail or '' for c in n]]:
            if re.search('[A-Za-z0-9]', value):
                check('visible_latin_number_direction', direction(n) == 'ltr')
    report('visible_latin_number_direction', True)
    report('unicode_no_hidden_controls', not FORBIDDEN.search(E.tostring(doc, encoding='unicode'))
           and not FORBIDDEN.search(json.dumps(translation, ensure_ascii=False)))
    counts = Counter()
    corrections = {}
    for record in translation['source_corrections']:
        for key in record['source_keys']:
            if key.endswith(('/alt', '/summary')):
                corrections.setdefault(key.split('/')[0], [])
                if record['bridge_id'] not in corrections[key.split('/')[0]]:
                    corrections[key.split('/')[0]].append(record['bridge_id'])
    for key, original in specs.items():
        target = target_block(doc, source, key, original)
        name = local(original)
        value = translation['source_blocks'][key]
        if name in {'media', 'table'}:
            traceattr, accessible = ('data-source-alt', 'alt') if name == 'media' else ('data-source-summary', 'aria-label')
            mapping = translation['image_alt_overrides'] if name == 'media' else translation['table_summary_overrides']
            sid = original.get('id')
            report('faithful_description_trace:' + key, target.get(traceattr) == value)
            report('accessible_description:' + key, target.get(accessible) == mapping.get(sid, value))
            origin = 'original-correction' if sid in mapping else 'source-translation'
            report('description_origin:' + key, target.get('data-description-origin') == origin)
            expected_targets = corrections.get(sid, [])
            report('description_targets:' + key, target.get('aria-describedby', '').split() == expected_targets)
            for destination in expected_targets:
                identified(doc, destination)
            # Original description numerals remain bound, including deliberately wrong source claims.
            source_value = original.get('alt') if name == 'media' else original.get('aria-label')
            report('description_source_numerals:' + key, Counter(NUMS.findall(source_value)) == Counter(NUMS.findall(value)))
            continue
        expected = fragment(value)
        actual = copy.deepcopy(target)
        actual.tag, actual.attrib, actual.tail = 'fragment', {}, None
        direct_blocks = [c for c in original if local(c) in BLOCKS]
        direct_math = [c for c in original if local(c) == 'math']
        direct_links = [c for c in original if local(c) == 'link']
        tokens = [chr(ord('a') + ord(c.text) - ord('ⓐ')) for c in original if local(c) == 'span' and c.get('class') == 'token']
        wrappers = [c for c in actual if c.get('class') == 'source-inline-part']
        expected_short = expected_groups(expected) if name == 'para' and not direct_blocks else []
        report('inline_group_count:' + key, len(wrappers) == len(expected_short))
        for wrap, (letter, contents) in zip(wrappers, expected_short):
            report('inline_group_identity:' + key + ':' + letter, wrap.tag == 'span'
                   and wrap.attrib == {'class': 'source-inline-part', 'data-source-part': letter})
            report('complete_inline_group:' + key + ':' + letter, text(wrap).strip() == contents
                   and not any(local(c) in {'table', 'div', 'br'} for c in wrap.iter()))
            unwrap(actual, wrap)
        source_label_values = [n.text[1] for n in expected.iter('bdi') if re.fullmatch(r'\([a-c]\)', n.text or '')]
        report('source_part_labels:' + key, source_label_values == tokens)
        counts['parts'] += len(tokens)
        math_index = child_index = link_index = 0
        for child in list(actual):
            if child.get('class') == 'math-isolate':
                report('math_wrapper:' + key, child.get('dir') == 'ltr' and len(child) == 1 and not child.text and not child[0].tail)
                math = child[0]
                report('math_owner_count:' + key, math_index < len(direct_math))
                original_math = direct_math[math_index]
                report('math_ltr:' + key, math.get('dir') == 'ltr')
                math.attrib.pop('dir')
                report('exact_math_tree:' + key, signature(math) == signature(original_math))
                replace_child(actual, child, '{{math:' + str(math_index) + '}}')
                math_index += 1
            elif child.get('data-source-child'):
                report('child_order:' + key, child_index < len(direct_blocks)
                       and child.get('data-source-child') == direct_blocks[child_index].get('id'))
                replace_child(actual, child, '{{child:' + str(child_index) + '}}')
                child_index += 1
            elif child.get('data-source-target'):
                report('link_order:' + key, link_index < len(direct_links))
                destination = direct_links[link_index].get('target-id')
                report('source_link_exact:' + key, child.get('href') == '#' + destination and child.get('data-source-target') == destination)
                replace_child(actual, child, '{{link:' + str(link_index) + '}}')
                link_index += 1
        report('direct_math_child_link_counts:' + key, (math_index, child_index, link_index) ==
               (len(direct_math), len(direct_blocks), len(direct_links)))
        report('source_fragment_exact_text_children_tails:' + key, signature(actual) == signature(expected))
        raw_target = re.sub(r'\{\{[^}]+\}\}', '', text(expected))
        report('source_prose_numerals:' + key, Counter(NUMS.findall(source_prose(original))) == Counter(NUMS.findall(raw_target)))
        report('source_newlines:' + key, len(list(expected.iter('br'))) == sum(local(c) == 'newline' for c in original))
        counts['math'] += math_index
        counts['child'] += child_index
        counts['links'] += link_index
        counts['newlines'] += len(list(expected.iter('br')))
        counts['inline_groups'] += len(wrappers)
    report('global_math_newline_part_totals', counts == Counter(math=14, child=13, links=1, newlines=7, parts=18, inline_groups=12))
    report('exact14_math_no_injected_trees', sum(local(n) == 'math' for n in doc.iter()) == 14)
    report('override_counts', len(translation['image_alt_overrides']) == 6 and len(translation['table_summary_overrides']) == 3)
    original_bridge = E.fromstring(translation['bridge_after_html'])
    report('original_bridge_exact_and_labeled', original_bridge.get('data-origin') == 'original-bridge'
           and signature(identified(doc, original_bridge.get('id'))) == signature(original_bridge))
    for original in source.iter():
        name = local(original)
        if name in {'section', 'example', 'exercise', 'problem', 'solution', 'note', 'list', 'figure'}:
            target = identified(doc, original.get('id'))
            report('container_text_tails:' + original.get('id'), not (target.text or '').strip()
                   and all(not (c.tail or '').strip() for c in target))
            for child in target:
                known = child.get('data-source-tag') or child.get('data-source-child') or child.get('data-origin') == 'renderer-ui'
                check('no_anonymous_container_child:' + original.get('id'), bool(known))
            actual_children = []
            ui = []
            for child in target:
                if child.get('data-origin') == 'renderer-ui':
                    ui.append(child)
                    continue
                child_id = child.get('id') or child.get('data-source-child')
                child_kind = child.get('data-source-tag')
                if child_kind is None and child_id:
                    child_kind = local(identified(source, child_id))
                actual_children.append((child_kind, child_id))
            report('source_direct_children_exact:' + original.get('id'), actual_children ==
                   [(local(child), child.get('id')) for child in original])
            report('only_expected_container_ui:' + original.get('id'), len(ui) == (1 if name in {'example', 'figure'} else 0)
                   and all(child.tag == ('h2' if name == 'example' else 'p') for child in ui))
        if name == 'list':
            target = identified(doc, original.get('id'))
            wanted = 'ul' if original.get('list-type') == 'bulleted' else 'ol'
            report('list_type_and_item_count:' + original.get('id'), target.tag == wanted
                   and len(target.findall('li')) == len(original)
                   and target.get('data-source-list-type') == original.get('list-type'))
        if name == 'solution' and any(local(c) == 'title' for c in original):
            target = identified(doc, original.get('id'))
            report('source_solution_title_once:' + original.get('id'),
                   [text(c) for c in target if c.tag in {'h2', 'h3'}] == ['حل'])
    report('four_explicit_solution_titles', sum(local(n) == 'solution' and any(local(c) == 'title' for c in n) for n in source.iter()) == 4)
    tables = [n for n in source.iter() if local(n) == 'table']
    total_cells = blanks = 0
    for original in tables:
        sid = original.get('id')
        target = identified(doc, sid)
        group = next(n for n in original if local(n) == 'tgroup')
        source_body = next(n for n in group if local(n) == 'tbody')
        actual_body = target.find('tbody')
        report('table_no_anonymous_text:' + sid, not (target.text or '').strip()
               and all(not (c.tail or '').strip() for c in target) and not (actual_body.text or '').strip())
        report('table_geometry:' + sid, len(actual_body) == len(source_body) and int(group.get('cols')) == 2
               and all(c.tag == 'tr' and len(c) == 2 and all(x.tag == 'td' for x in c) for c in actual_body))
        report('table_no_invented_headers:' + sid, not list(target.iter('th')) and target.find('thead') is None)
        report('table_ltr_cells_rtl:' + sid, target.get('dir') == 'ltr' and all(c.get('dir') == 'rtl' for c in target.iter('td')))
        report('table_empty_label_trace:' + sid, (target.get('data-source-empty-label') == 'true')
               == any(local(n) == 'label' for n in original))
        report('table_group_class_trace:' + sid, target.get('data-source-tgroup-cols') == group.get('cols')
               and target.get('data-source-class') == original.get('class'))
        source_columns = [n for n in group if local(n) == 'colspec']
        actual_columns = list(target.iter('col'))
        report('source_colspec_trace:' + sid, len(source_columns) == len(actual_columns)
               and all(a.get('data-source-colnum') == s.get('colnum')
                       and a.get('data-source-colname') == s.get('colname') for s, a in zip(source_columns, actual_columns)))
        for r, source_row in enumerate(source_body):
            actual_row = actual_body[r]
            report('row_no_anonymous_text:' + sid + ':' + str(r), not (actual_row.text or '').strip()
                   and all(not (c.tail or '').strip() for c in actual_row))
            for c, source_cell in enumerate(source_row):
                total_cells += 1
                if not len(source_cell) and not (source_cell.text or '').strip():
                    blanks += 1
                    report('empty_source_cell:' + sid + ':' + str(r), not len(actual_row[c]) and not (actual_row[c].text or '').strip())
        wrapper = dp[target]
        report('table_scroll_region:' + sid, wrapper.get('dir') == 'ltr' and wrapper.get('tabindex') == '0'
               and wrapper.get('role') == 'region' and 'source-table-scroll' in wrapper.get('class', '').split())
    report('20cells_3empty_0headers', (total_cells, blanks) == (20, 3))
    report('only_three_source_table_elements', sum('source-table' in n.get('class', '').split() for n in doc.iter('table')) == 3)
    # Genuine source media wrappers are validated before excluding them from prose.
    for media in [n for n in source.iter() if local(n) == 'media']:
        image = identified(doc, media.get('id'))
        scroll = dp[image]
        wrapper = dp[scroll]
        report('media_wrapper_no_anonymous_text:' + media.get('id'),
               wrapper.get('class') == 'source-media' and wrapper.get('data-source-child') == media.get('id')
               and not (wrapper.text or '').strip() and all(not (c.tail or '').strip() for c in wrapper)
               and len(scroll) == 1 and not (scroll.text or '').strip() and not (image.tail or '').strip())
        report('media_wrapper_children:' + media.get('id'), all(c is scroll or c.get('data-origin') == 'renderer-ui' for c in wrapper))
        expected_targets = corrections.get(media.get('id'), [])
        visible = [n.get('href') for n in wrapper.iter('a')]
        report('visible_media_corrections:' + media.get('id'), all('#' + target in visible for target in expected_targets))
    for table in tables:
        sid = table.get('id')
        wrapper = dp[dp[identified(doc, sid)]]
        scroll = dp[identified(doc, sid)]
        report('table_wrapper_no_anonymous_text:' + sid, not (wrapper.text or '').strip()
               and all(not (c.tail or '').strip() for c in wrapper)
               and all(c is scroll or c.get('data-origin') == 'renderer-ui' for c in wrapper)
               and not (scroll.text or '').strip() and len(scroll) == 1 and not (scroll[0].tail or '').strip())
        visible = [n.get('href') for n in wrapper.iter('a')]
        report('visible_table_corrections:' + sid, all('#' + target in visible for target in corrections[sid]))
    return dict(counts)


def validate_images(doc, source, manifest, report=check, digests=None):
    media = [n for n in source.iter() if local(n) == 'media']
    images = list(doc.iter('img'))
    report('14images_one_figure', len(media) == len(images) == len(manifest['images']) == 14 and len(list(doc.iter('figure'))) == 1)
    records = []
    with (ROOT / manifest['media_authority_manifest_path']).open(encoding='utf-8-sig', newline='') as handle:
        authority = list(csv.DictReader(handle))
    for original, actual, spec in zip(media, images, manifest['images']):
        sid = original.get('id')
        src = next(n for n in original if local(n) == 'image')
        original_path = (ROOT / manifest['canonical_local_path']).parent / src.get('src')
        reader_path = (READER.parent / actual.get('src')).resolve()
        report('image_paths:' + sid, original_path.resolve() == (ROOT / spec['canonical_local_path']).resolve()
               and reader_path == (BASE / spec['path']).resolve() and actual.get('id') == spec['media_id'] == sid)
        original_data, data = original_path.read_bytes(), reader_path.read_bytes()
        actual_digest = (digests or {}).get(sid, hashlib.sha256(data).hexdigest())
        report('image_digests:' + sid, actual_digest == hashlib.sha256(original_data).hexdigest() == spec['sha256'])
        report('image_size:' + sid, len(data) == len(original_data) == spec['bytes'])
        dims = jpeg_dimensions(data)
        report('image_dimensions:' + sid, dims == (spec['width'], spec['height']) == (int(actual.get('width')), int(actual.get('height'))))
        report('source_mime_retained_actual_jpeg:' + sid, src.get('mime-type') == spec['declared_mime'] == actual.get('data-source-image-mime')
               and spec['actual_image_format'] == 'Jpeg' and actual.get('data-rendered-image-mime') == 'image/jpeg')
        row = [r for r in authority if r['relative_path'] == spec['source_path']]
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        report('image_authority_blob:' + sid, len(row) == 1 and row[0]['sha256'] == spec['sha256']
               and int(row[0]['bytes']) == spec['bytes'] and row[0]['git_blob_sha1'] == blob == spec['git_blob_sha1'])
        p = parents(doc)
        scroll = p[actual]
        report('image_ltr_scroll:' + sid, scroll.get('dir') == 'ltr' and scroll.get('tabindex') == '0' and scroll.get('role') == 'region')
        report('no_image_transform:' + sid, 'transform' not in actual.get('style', '') and 'transform' not in scroll.get('style', ''))
        report('image_fallback_link:' + sid, any(n.get('href') == actual.get('src') for n in p[scroll].iter('a')))
        records.append({'media_id': sid, 'path': spec['path'], 'sha256': spec['sha256'], 'bytes': len(data),
                        'width': dims[0], 'height': dims[1], 'source_mime': src.get('mime-type'), 'actual_mime': 'image/jpeg'})
    report('four_wrong_source_png_declarations', sum(r['source_mime'] == 'image/png' for r in records) == 4)
    return records


def validate_rounding(doc, source, report=check):
    results = []
    for problem_id, answer_id in [('fs-id1170655154263', 'fs-id1170655074702'), ('fs-id1170655025825', 'fs-id1170655154551')]:
        problem = text(identified(source, problem_id))
        number = int(NUMS.search(problem)[0].replace(',', ''))
        values = [int(n.replace(',', '')) for n in NUMS.findall(text(identified(doc, answer_id)))]
        expected = [((number + power // 2) // power) * power for power in (100, 1000, 10000)]
        report('six_tryit_rounding:' + answer_id, values == expected)
        results.append({'source': number, 'hundred_thousand_ten_thousand': values})
    for problem_id, answer_id in [('fs-id1170655128617', 'fs-id1170655108383'), ('fs-id1170655166306', 'fs-id1170654863185')]:
        number = int(NUMS.search(text(identified(source, problem_id)))[0].replace(',', ''))
        answer = int(NUMS.search(text(identified(doc, answer_id)))[0].replace(',', ''))
        report('single_hundred_tryit:' + answer_id, answer == ((number + 50) // 100) * 100)
    number = int(NUMS.search(text(identified(source, 'fs-id1170655151020')))[0].replace(',', ''))
    for table_id, power in [('fs-id1167832055010', 100), ('fs-id1167834184013', 1000), ('fs-id1167832006514', 10000)]:
        table = identified(doc, table_id)
        sentence = text(table.find('tbody')[-1][-1])
        values = [int(n.replace(',', '')) for n in NUMS.findall(sentence)]
        report('worked_table_rounding:' + table_id, number in values and ((number + power // 2) // power) * power in values)
    q = int(NUMS.search(text(identified(source, 'fs-id1170655105094')))[0].replace(',', ''))
    final_alt = identified(doc, 'fs-id1170655130142').get('alt')
    report('worked_23658_to23700', str(((q + 50) // 100) * 100) in [n.replace(',', '') for n in NUMS.findall(final_alt)])
    return results


def validate_notices(doc, manifest, report=check, record=None):
    notices = record if record is not None else json.loads(NOTICES.read_text(encoding='utf-8'))
    report('notice_scope_hashes', notices['unit'] == 'A10-002' and notices['manifest_sha256'] == sha(MANIFEST)
           and notices['excerpt_sha256'] == manifest['excerpt_sha256'] and notices['whole_book_translation_complete'] is False)
    report('notice14images', len(notices['images']) == 14)
    for entry in manifest['existing_notice_inputs']:
        report('logical_notice_hash:' + entry['path'],
               hashlib.sha256((ROOT / entry['path']).read_bytes().replace(b'\r\n', b'\n')).hexdigest() == entry['sha256'])
    report('notice_inputs_preserved', notices['existing_notice_inputs'] == manifest['existing_notice_inputs'])
    report('notice_verbatim_preserved', notices['release_notice_verbatim'] == (BASE / 'provenance/A10-release/NOTICE.txt').read_text(encoding='utf-8'))
    source = E.parse(BASE / 'source-excerpts/a10-unit-002.cnxml').getroot()
    for spec, retained in zip(manifest['images'], notices['images']):
        sid = spec['media_id']
        report('notice_component_identity:' + sid, all(retained[k] == spec[k] for k in
               ['figure_id', 'media_id', 'source_path', 'path', 'sha256', 'bytes', 'width', 'height']))
        report('notice_component_source_alt_mime:' + sid,
               retained['source_english_alt'] == identified(source, sid).get('alt')
               and retained['source_declared_mime'] == spec['declared_mime'] and retained['actual_mime'] == 'image/jpeg')
        row = retained['existing_media_authority_row']
        report('notice_component_authority_row:' + sid, row['relative_path'] == spec['source_path']
               and row['sha256'] == spec['sha256'] and int(row['bytes']) == spec['bytes']
               and row['git_blob_sha1'] == spec['git_blob_sha1'])
        report('notice_component_rights_limit:' + sid, retained['component_clearance'].startswith('Not newly assessed;'))
    report('notice_media_authority_hash', notices['media_authority_manifest']['path'] == manifest['media_authority_manifest_path']
           and notices['media_authority_manifest']['sha256'] == sha(ROOT / manifest['media_authority_manifest_path'])
           == manifest['media_authority_manifest_sha256'])
    footer = text(identified(doc, 'credits'))
    for required in ['Lynn Marecek', 'MaryAnne Anthony-Smith', 'Andrea Honeycutt Mathis', 'Elementary Algebra 2e',
                     'm82452', 'col31130', 'Attribution-NonCommercial-ShareAlike 4.0', 'component-specific credits and restrictions',
                     'do not endorse', 'No new clearance', 'not a complete module', 'Native-language']:
        report('footer_required:' + required, required in footer)
    report('no_crosswork_author_credit', not any(n in footer for n in ['Jay Abramson', 'David Lippman', 'Melonie Rasmussen']))
    report('rights_limits', 'No new component-specific clearance' in notices['rights_status']
           and 'not clearance' in notices['credit_limit'])
    return notices


def validate_links(doc, report=check):
    links = []
    for n in doc.iter():
        for identifier in n.get('aria-describedby', '').split():
            identified(doc, identifier)
        for key in ('href', 'src'):
            value = n.get(key)
            if value is None:
                continue
            parsed = urlsplit(value)
            if parsed.scheme in ('https', 'http'):
                continue
            report('safe_local_scheme:' + value, not parsed.scheme and not parsed.netloc)
            path = (READER.parent / unquote(parsed.path)).resolve() if parsed.path else READER.resolve()
            report('local_file:' + value, path.is_relative_to(BASE.resolve()) and path.is_file())
            if parsed.fragment:
                target = doc if path == READER.resolve() else parse_reader(path.read_text(encoding='utf-8'))
                identified(target, unquote(parsed.fragment))
            links.append(value)
    report('previous_unit_navigation', 'a10-unit-001.html' in links)
    return links


def mutations(doc, source, manifest, translation):
    names = []
    def reject(name, mutate, validator=None):
        changed = copy.deepcopy(doc)
        mutate(changed)
        try:
            (validator or (lambda d: validate_dom(d, source, manifest, translation)))(changed)
        except (AssertionError, IndexError, KeyError):
            names.append(name)
        else:
            raise AssertionError('mutation_not_rejected:' + name)

    reject('math_digit', lambda d: setattr(next(n for n in identified(d, 'fs-id1170655164902').iter() if local(n) == 'mn'), 'text', '7'))
    def main_injection(d):
        node = E.SubElement(d.find('.//main'), 'p', {'dir': 'ltr'})
        node.text = 'CONTRADICTORY 103978 = 999'
    reject('ltr_main_paragraph_injection', main_injection)
    reject('body_paragraph_injection', lambda d: E.SubElement(d.find('body'), 'p', {'dir': 'ltr'}))
    reject('main_anonymous_tail', lambda d: setattr(d.find('.//main')[1], 'tail', ' غلط'))
    reject('source_label_injected_prose', lambda d: setattr(d.find('.//main')[0], 'text', 'غلط'))
    reject('continuation_status_injected_prose', lambda d: setattr(d.find('.//main')[-1], 'text', 'غلط'))
    reject('math_mspace_width_changed', lambda d: next(n for n in d.iter() if local(n) == 'mspace').set('width', '2em'))
    def delete_space(d):
        space = next(n for n in d.iter() if local(n) == 'mspace')
        parents(d)[space].remove(space)
    reject('math_mspace_node_deleted', delete_space)
    reject('source_ancestry', lambda d: identified(d, 'fs-id1167832055010').set('id', 'wrong-table-id'))
    reject('source_prose_number', lambda d: setattr(identified(d, 'fs-id1170655105094').find('bdi'), 'text', '23,659'))
    reject('anonymous_container_text', lambda d: setattr(identified(d, 'fs-id1170655106038'), 'text', 'injected prose'))
    reject('anonymous_container_child', lambda d: E.SubElement(identified(d, 'fs-id1170655106038'), 'p'))
    reject('unbound_marked_container_child', lambda d: E.SubElement(identified(d, 'fs-id1170655106038'), 'p', {'data-source-tag': 'para'}))
    reject('anonymous_table_wrapper_text', lambda d: setattr(parents(d)[parents(d)[identified(d, 'fs-id1167832055010')]], 'text', 'injected'))
    reject('source_prose_tail', lambda d: setattr(identified(d, 'fs-id1170655105094').find('bdi'), 'tail', ' غلط'))
    reject('empty_cell_filled', lambda d: setattr(identified(d, 'fs-id1167832055010').find('tbody')[-1][0], 'text', '7'))
    reject('table_column_reversed', lambda d: identified(d, 'fs-id1167834184013').set('dir', 'rtl'))
    reject('invented_table_header', lambda d: setattr(identified(d, 'fs-id1167834184013').find('tbody')[0][0], 'tag', 'th'))
    reject('nested_bullet_changed', lambda d: setattr(identified(d, 'fs-id1170654989989'), 'tag', 'ol'))
    reject('solution_title_duplicate', lambda d: identified(d, 'fs-id1170655134210').insert(0, copy.deepcopy(identified(d, 'fs-id1170655134210').find('h3'))))
    reject('newline_removed', lambda d: identified(d, 'fs-id1170655190501').remove(identified(d, 'fs-id1170655190501').find('br')))
    reject('inline_group_wrong_marker', lambda d: identified(d, 'fs-id1170655074702').find('span').set('data-source-part', 'c'))
    def split_group(d):
        group = identified(d, 'fs-id1170655154263').find('span')
        last = group[-1]
        group.tail = (last.tail or '') + (group.tail or '')
        last.tail = None
    reject('inline_answer_split_outside', split_group)
    reject('faithful_alt_trace_erased', lambda d: identified(d, 'fs-id1167831823617').set('data-source-alt', 'درست'))
    reject('accessible_alt_wrong_digit', lambda d: identified(d, 'fs-id1167835305151').set('alt', 'ہندسے 3 دے تھلے لکیر'))
    reject('faithful_summary_trace_erased', lambda d: identified(d, 'fs-id1167832006514').set('data-source-summary', 'درست'))
    reject('accessible_summary_wrong_digit', lambda d: identified(d, 'fs-id1167832006514').set('aria-label', '0 < 5'))
    reject('wrong_correction_destination', lambda d: identified(d, 'fs-id1167835305151').set('aria-describedby', 'a10-002-alt022-correction'))
    reject('source_mime_erased', lambda d: identified(d, 'fs-id1167835305151').set('data-source-image-mime', 'image/jpeg'),
           lambda d: validate_images(d, source, manifest))
    reject('image_path_swap', lambda d: identified(d, 'fs-id1167835305151').set('src', '../' + manifest['images'][0]['path']),
           lambda d: validate_images(d, source, manifest))
    reject('source_link_changed', lambda d: identified(d, 'fs-id1170655113270').find('a').set('href', '#term-00006'))
    reject('tryit_answer_digit', lambda d: setattr(identified(d, 'fs-id1170655074702').find('span').findall('bdi')[1], 'text', '208,000'),
           lambda d: validate_rounding(d, source))
    try:
        validate_images(doc, source, manifest, digests={manifest['images'][0]['media_id']: '0' * 64})
    except AssertionError:
        names.append('image_digest_detached_argument')
    else:
        raise AssertionError('image_digest_mutation_not_rejected')
    notice = json.loads(NOTICES.read_text(encoding='utf-8'))
    notice['images'][0]['sha256'] = '0' * 64
    try:
        validate_notices(doc, manifest, record=notice)
    except AssertionError:
        names.append('component_notice_digest_detached_record')
    else:
        raise AssertionError('component_notice_mutation_not_rejected')
    return names


def main():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    translation = json.loads(TRANSLATION.read_text(encoding='utf-8'))
    source = E.parse(BASE / 'source-excerpts/a10-unit-002.cnxml').getroot()
    inputs = [MANIFEST, TRANSLATION, BASE / 'source-excerpts/a10-unit-002.cnxml',
              BASE / 'qa/a10-unit-002-language-notes.md', BASE / 'scripts/prepare_a10_002.py',
              BASE / 'scripts/build_a10_002.py', Path(__file__), BASE / 'scripts/prepare_a10.py',
              BASE / 'scripts/build_a10.py', BASE / 'styles/reader.css', BASE / 'sources.lock.json',
              ROOT / manifest['canonical_local_path'], ROOT / manifest['indonesian_comparison_path'],
              ROOT / manifest['media_authority_manifest_path']]
    inputs += [ROOT / item['path'] for item in manifest['existing_notice_inputs']]
    inputs += [ROOT / item['canonical_local_path'] for item in manifest['images']]
    inputs += list(sorted((BASE / 'canon/receipts').glob('A10-002-*.json')))
    initial = {str(p): sha(p) for p in inputs}
    hashes = []
    for _ in range(2):
        subprocess.run([sys.executable, str(BASE / 'scripts/prepare_a10_002.py')], check=True, capture_output=True)
        subprocess.run([sys.executable, str(BASE / 'scripts/build_a10_002.py')], check=True, capture_output=True)
        hashes.append((sha(READER), sha(NOTICES)))
    check('two_prepare_build_runs_deterministic', hashes[0] == hashes[1])
    doc = parse_reader(READER.read_text(encoding='utf-8'))
    passed = []
    def report(name, condition):
        check(name, condition)
        passed.append(name)
    validate_source(source, manifest, report)
    structural = validate_dom(doc, source, manifest, translation, report)
    images = validate_images(doc, source, manifest, report)
    rounds = validate_rounding(doc, source, report)
    validate_notices(doc, manifest, report)
    links = validate_links(doc, report)
    negative = mutations(doc, source, manifest, translation)
    report('two_prepare_build_runs_deterministic', hashes[0] == hashes[1])
    report('stable_input_hashes', initial == {str(p): sha(p) for p in inputs})
    artifacts = inputs + [READER, NOTICES] + [BASE / image['path'] for image in manifest['images']]
    unique = list(dict.fromkeys(artifacts))
    record = {
        'unit': 'A10-002', 'scope': 'm82452 first-section remainder only; full assignment incomplete',
        'status': 'passed', 'checks_passed': len(passed), 'checks': passed,
        'source_derived_counts': structural, 'detached_mutations_rejected': negative,
        'reader_sha256': sha(READER), 'component_notices_sha256': sha(NOTICES),
        'artifacts': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p), 'bytes': p.stat().st_size} for p in unique],
        'artifact_hash_policy': 'Exact current artifact bytes. Existing notice semantic pin checks separately normalize only CRLF to LF.',
        'original_images': images, 'rounding_checks': rounds, 'local_references': links,
        'limitations': [
            'Structural and bounded mathematical checks are not native-speaker or educator certification.',
            'Parent desktop/mobile visual review is separate; this script does not certify visual or assistive-technology behavior.',
            'Known source errors remain traceable in source_blocks and data-source descriptions; original accessible corrections are separately labeled.',
            'No new image clearance or repeated supply/license audit is performed.',
            'Only14literal/operator/spacing MathML trees are checked exactly; no universal formula or population claim is made.',
            'Earlier collection items and remaining modules are not made complete by this receipt.'
        ]
    }
    RECEIPT.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f'A10-002 QA passed: {len(passed)} checks, {len(negative)} detached mutations; reader {sha(READER)}')


if __name__ == '__main__':
    main()
