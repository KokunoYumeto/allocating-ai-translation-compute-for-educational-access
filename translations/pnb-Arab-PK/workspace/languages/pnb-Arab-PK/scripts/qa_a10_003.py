"""Independent CNXML-derived QA for A10-003; mutations are detached/in-memory."""
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
MANIFEST = BASE / 'source-excerpts/manifest-a10-003.json'
TRANSLATION = BASE / 'translations/a10-unit-003.json'
READER = BASE / 'reader/a10-unit-003.html'
NOTICES = BASE / 'provenance/a10-unit-003-component-notices.json'
RECEIPT = BASE / 'qa/structural-a10-003.json'
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
        elif name == 'note' and not len(n) and (n.text or '').strip():
            key = n.get('id')
        elif name == 'item':
            key = p[n].get('id') + '/item/' + str(list(p[n]).index(n) + 1)
        elif name == 'entry':
            table = p[n]
            while local(table) != 'table':
                table = p[table]
            rows = [c for c in table.iter() if local(c) == 'row']
            key = table.get('id') + '/row/' + str(rows.index(p[n]) + 1) + '/entry/' + str(list(p[n]).index(n) + 1)
        else:
            continue
        check('unique_source_key:' + key, key not in specs)
        specs[key] = n
    return specs


def target_block(doc, key):
    found = [n for n in doc.iter() if n.get('data-source-key') == key]
    check('unique_target_block:' + key, len(found) == 1)
    return found[0]


def source_prose(node):
    result = node.text or ''
    for child in node:
        if local(child) not in {'math', 'link'}:
            result += source_prose(child)
        result += child.tail or ''
    return result


def replace_child(parent, child, replacement):
    index = list(parent).index(child)
    value = replacement + (child.tail or '')
    if index:
        parent[index - 1].tail = (parent[index - 1].tail or '') + value
    else:
        parent.text = (parent.text or '') + value
    parent.remove(child)


def inner(node):
    return node.text, tuple((signature(c), c.tail) for c in node)


def blank_frame(node):
    return not (node.text or '').strip() and all(not (c.tail or '').strip() for c in node)


def validate_source(source, manifest, report=check):
    path = ROOT / manifest['canonical_local_path']
    data = path.read_bytes()
    report('canonical_hash_bytes', sha(path) == manifest['full_module_sha256'] and len(data) == manifest['full_module_bytes'])
    report('canonical_blob', hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == manifest['canonical_git_blob_sha1'])
    full = E.fromstring(data)
    content = next(n for n in full if local(n) == 'content')
    report('immediate_two_node_scope', [n.get('id') for n in list(content)[3:5]] == ['newelem_para01', 'fs-id1170655199097']
           and len(source) == 2 and len(source[1]) == 17)
    report('exact_canonical_selected_subtrees', [signature(n) for n in list(content)[3:5]] == [signature(n) for n in source])
    report('stop_before_next_section', list(content)[5].get('id') == manifest['next_source_id'] == 'fs-id1170655247410')
    report('complete_last_tryit', source[1][-1].get('id') == manifest['scope_through_inclusive'] == 'fs-id1170655200179'
           and list(source[1][-1].iter())[-1].get('id') == 'fs-id1170655247402')
    report('frozen_witness_hash', sha(BASE / 'source-excerpts/a10-unit-003.cnxml') == manifest['excerpt_sha256'])
    ids = [n.get('id') for n in source.iter() if n is not source and n.get('id')]
    report('40sourceIDs', ids == manifest['source_ids_in_document_order'] and len(ids) == 40)
    specs = source_specs(source)
    report('178source_keys', list(specs) == manifest['source_block_keys_in_document_order'] and len(specs) == 178)
    lock = json.loads((BASE / 'sources.lock.json').read_text(encoding='utf-8'))
    pin = next(n for n in lock['repositories'] if n['role'] == 'A10+A20 upstream')
    report('existing_lock_commit_tree', (pin['commit'], pin['tree']) == (manifest['commit'], manifest['tree']))
    comparison_path = ROOT / manifest['indonesian_comparison_path']
    report('indonesian_comparison_hash', sha(comparison_path) == manifest['indonesian_comparison_sha256'])
    other = E.parse(comparison_path).getroot()
    for selected in source:
        comparison = identified(other, selected.get('id'))
        sig = lambda node: [(n.tag, n.get('id'), n.get('src'), n.get('target-id')) for n in node.iter()]
        report('comparison_structure:' + selected.get('id'), sig(selected) == sig(comparison))
    return specs


def validate_dom(doc, source, manifest, translation, report=check):
    specs, sp, dp = source_specs(source), parents(source), parents(doc)
    source_ids = [n.get('id') for n in source.iter() if n is not source and n.get('id')]
    output_ids = [n.get('id') for n in doc.iter() if n.get('id')]
    report('localeRTL', doc.tag == 'html' and doc.get('lang') == 'pnb-Arab-PK' and doc.get('dir') == 'rtl')
    report('source_key_order', list(specs) == list(translation['source_blocks']))
    report('unique_output_IDs', len(output_ids) == len(set(output_ids)))
    report('source_ID_document_order', [sid for sid in output_ids if sid in set(source_ids)] == source_ids)
    report('no_unresolved_tokens_or_badscript', not re.search(r'\{\{[^}]*\}\}', E.tostring(doc, encoding='unicode'))
           and not FORBIDDEN.search(E.tostring(doc, encoding='unicode')))
    for node in doc.iter():
        report('no_event_script:' + node.tag, node.tag not in {'script', 'iframe'} and not any(k.lower().startswith('on') for k in node.attrib))
    for original in source.iter():
        if original is source or not original.get('id'):
            continue
        actual = identified(doc, original.get('id'))
        sparent = sp.get(original)
        while sparent is not None and (sparent is source or not sparent.get('id')):
            sparent = sp.get(sparent)
        aparent = dp.get(actual)
        while aparent is not None and aparent.get('id') not in source_ids:
            aparent = dp.get(aparent)
        report('source_ancestry:' + original.get('id'), (sparent.get('id') if sparent is not None else None)
               == (aparent.get('id') if aparent is not None else None))
    math_count = link_count = newline_count = 0
    for key, original in specs.items():
        name = local(original)
        value = translation['source_blocks'][key]
        if name in {'media', 'table'}:
            actual = identified(doc, original.get('id'))
            source_string = original.get('alt') if name == 'media' else original.get('aria-label', original.get('summary'))
            report('accessible_source_numerals:' + key, NUMS.findall(source_string) == NUMS.findall(value))
            accessible, trace = ('alt', 'data-source-alt') if name == 'media' else ('aria-label', 'data-source-summary')
            report('faithful_accessible_and_trace:' + key, actual.get(accessible) == actual.get(trace) == value)
            report('description_origin:' + key, actual.get('data-description-origin') == 'source-translation'
                   and not actual.get('aria-describedby'))
            continue
        actual = target_block(doc, key)
        expected_tag = ('h2' if local(sp[original]) == 'section' else 'h3') if name == 'title' else \
            'li' if name == 'item' else 'p' if name in {'para', 'note'} else actual.tag
        report('source_block_tag:' + key, actual.tag == expected_tag)
        if name != 'entry':
            report('source_proseRTL:' + key, actual.get('dir') in {None, 'rtl'})
        if name == 'note':
            report('direct_note_exact_owner', dp[actual] is identified(doc, original.get('id')) and actual.get('class') == 'source-note-text')
        clone = copy.deepcopy(actual)
        source_math = [n for n in original if local(n) == 'math']
        output_math = [n for n in clone.iter() if local(n) == 'math']
        report('math_owner_count:' + key, len(source_math) == len(output_math))
        cp = parents(clone)
        for index, (source_tree, target_tree) in enumerate(zip(source_math, output_math)):
            wrapper = cp[target_tree]
            report('math_owner_wrapper:' + key, cp.get(wrapper) is clone and wrapper.tag == 'span'
                   and wrapper.attrib == {'class': 'math-isolate', 'dir': 'ltr'} and len(wrapper) == 1
                   and not wrapper.text and not target_tree.tail)
            copied = copy.deepcopy(target_tree)
            report('mathLTR:' + key, copied.attrib.pop('dir', None) == 'ltr')
            report('math_exact_tree:' + key, signature(copied) == signature(source_tree))
            replace_child(clone, wrapper, '{{math:' + str(index) + '}}')
            math_count += 1
        original_links = [n for n in original if local(n) == 'link']
        target_links = [n for n in clone if n.tag == 'a']
        report('source_link_owner_count:' + key, len(original_links) == len(target_links))
        for index, (source_link, target_link) in enumerate(zip(original_links, target_links)):
            target = source_link.get('target-id')
            report('exact_source_link:' + key, target_link.get('data-source-target') == target
                   and target_link.get('href') == '#' + target)
            label = fragment('جدول <bdi dir="ltr">' + manifest['renderer_contract']['source_link_labels'][target] + '</bdi>')
            report('source_table_link_label:' + key, inner(target_link) == inner(label))
            replace_child(clone, target_link, '{{link:' + str(index) + '}}')
            link_count += 1
        expected = fragment(value)
        report('exact_source_target_fragment:' + key, inner(clone) == inner(expected))
        clean_value = re.sub(r'\{\{[^}]*\}\}', '', value)
        report('source_prose_numerals:' + key, NUMS.findall(source_prose(original)) == NUMS.findall(text(fragment(clean_value))))
        source_newline = sum(local(n) == 'newline' for n in original)
        report('source_newline:' + key, len(list(actual.iter('br'))) == source_newline)
        newline_count += source_newline
        for isolated in actual.iter('bdi'):
            report('bdiLTR:' + key, isolated.get('dir') == 'ltr')
    report('3math3links1newline', (math_count, link_count, newline_count) == (3, 3, 1))
    source_symbols = [text(n) for n in source.iter() if local(n) == 'emphasis' and n.get('effect') == 'italics']
    actual_symbols = [text(n.find('bdi')) for n in doc.iter('em') if n.find('bdi') is not None]
    report('13italicLatin_occurrences_7prelude', source_symbols == actual_symbols and len(source_symbols) == 13
           and source_symbols[:7] == ['a', 'b', 'c', 'm', 'n', 'x', 'y'])
    tables = [n for n in source.iter() if local(n) == 'table']
    report('exact_two_tables', len(list(doc.iter('table'))) == len(tables) == 2)
    for original in tables:
        sid = original.get('id')
        actual = identified(doc, sid)
        source_group = next(n for n in original if local(n) == 'tgroup')
        cols = int(source_group.get('cols'))
        report('table_direction_and_metadata:' + sid, actual.tag == 'table' and actual.get('dir') == 'ltr'
               and actual.get('data-source-tgroup-cols') == str(cols) and actual.get('data-source-class') == original.get('class', '')
               and actual.get('data-source-summary-attribute') == ('aria-label' if 'aria-label' in original.attrib else 'summary'))
        groups = [n for n in source_group if local(n) in {'thead', 'tbody'}]
        actual_groups = [n for n in actual if n.tag in {'thead', 'tbody'}]
        report('table_source_rowgroups:' + sid, [local(n) for n in groups] == [n.tag for n in actual_groups])
        colspecs = [n for n in source_group if local(n) == 'colspec']
        actual_cols = list(actual.iter('col'))
        report('source_colspec_count:' + sid, len(colspecs) == len(actual_cols))
        for original_col, actual_col in zip(colspecs, actual_cols):
            report('source_colspec:' + sid, actual_col.get('data-source-colnum') == original_col.get('colnum')
                   and actual_col.get('data-source-colname') == original_col.get('colname'))
        expected_children = ([actual.find('colgroup')] if colspecs else []) + actual_groups
        report('table_no_anonymous_children:' + sid, list(actual) == expected_children and blank_frame(actual))
        row_number = 0
        for original_group, actual_group in zip(groups, actual_groups):
            report('rowgroup_size_frame:' + sid, len(original_group) == len(actual_group) and blank_frame(actual_group))
            for original_row, actual_row in zip(original_group, actual_group):
                row_number += 1
                report('row_geometry:' + sid + ':' + str(row_number), actual_row.tag == 'tr'
                       and actual_row.get('data-source-row') == str(row_number) and len(actual_row) == len(original_row) == cols
                       and blank_frame(actual_row))
                for column, (original_cell, cell) in enumerate(zip(original_row, actual_row), 1):
                    key = f'{sid}/row/{row_number}/entry/{column}'
                    head = local(original_group) == 'thead'
                    row_head = cols == 13 and not head and column == 1 and re.fullmatch(r'Multiples of \d+', text(original_cell))
                    expected = 'th' if head or row_head else 'td'
                    report('cell_key_and_role:' + key, cell.tag == expected and cell.get('data-source-key') == key
                           and cell.get('scope') == ('col' if head else 'row' if row_head else None))
                    numeric = not len(original_cell) and re.fullmatch(r'\d+', text(original_cell))
                    report('cell_direction:' + key, cell.get('dir') == ('ltr' if numeric else 'rtl'))
                    report('cell_alignment_trace:' + key, all(cell.get('data-source-' + k) == original_cell.get(k) for k in ['align', 'valign']))
                    if not len(original_cell) and not text(original_cell).strip():
                        report('source_empty_cell:' + key, not len(cell) and not text(cell).strip())
        container = dp[dp[actual]]
        report('table_local_wrapper:' + sid, container.tag == 'div' and container.get('class') == 'source-table-container'
               and container.get('data-source-child') == sid and blank_frame(container)
               and dp[actual].get('class') == 'table-scroll source-table-scroll' and dp[actual].get('dir') == 'ltr'
               and dp[actual].get('tabindex') == '0' and dp[actual].get('role') == 'region'
               and list(dp[actual]) == [actual] and blank_frame(dp[actual]))
        numbered = sid in manifest['renderer_contract']['source_link_labels']
        report('table_wrapper_closed_children:' + sid, len(container) == (3 if numbered else 2)
               and list(container)[-2] is dp[actual] and container[-1].attrib == {'class': 'scroll-hint', 'data-origin': 'renderer-ui'}
               and text(container[-1]) == 'سارے کالم ویکھن لئی لوڑ پئے تے جدول نوں پاسے سرکاؤ۔')
        if numbered:
            report('local_table_caption:' + sid, container[0].attrib == {'class': 'source-table-label', 'data-origin': 'renderer-ui'}
                   and inner(container[0]) == inner(fragment('جدول <bdi dir="ltr">' + manifest['renderer_contract']['source_link_labels'][sid] + '</bdi>')))
    def rendered_anchor(original):
        if local(original) in {'media', 'table'}:
            found = [n for n in doc.iter('div') if n.get('data-source-child') == original.get('id')]
            check('unique_structural_wrapper', len(found) == 1)
            return found[0]
        if original.get('id'):
            return identified(doc, original.get('id'))
        return target_block(doc, next(k for k, v in specs.items() if v is original))
    containers = {'section', 'example', 'exercise', 'problem', 'solution', 'note', 'list'}
    full = E.parse(ROOT / manifest['canonical_local_path']).getroot()
    all_examples = [n for n in full.iter() if local(n) == 'example']
    for original in source.iter():
        if local(original) not in containers:
            continue
        actual = identified(doc, original.get('id'))
        report('source_containerRTL:' + original.get('id'), actual.get('dir') in {None, 'rtl'})
        if local(original) == 'note' and not len(original):
            expected = [target_block(doc, original.get('id'))]
        else:
            expected = [rendered_anchor(n) for n in original]
        if local(original) == 'example':
            heading = actual.find('h2')
            label = str([n.get('id') for n in all_examples].index(original.get('id')) + 1)
            report('source_example_number', heading is not None and heading.attrib == {'class': 'example-label', 'data-origin': 'renderer-ui'}
                   and inner(heading) == inner(fragment('حل کیتی مثال <bdi dir="ltr">' + label + '</bdi>')))
            expected = [heading] + expected
        report('source_container_closed_children:' + original.get('id'), list(actual) == expected and blank_frame(actual))
        if local(original) == 'list':
            report('source_bullet_list', actual.tag == 'ul' and actual.get('data-source-list-type') == original.get('list-type')
                   and actual.get('data-source-bullet-style') == original.get('bullet-style'))
    bridge = identified(doc, 'a10-003-original-bridge')
    original_bridge = E.fromstring(translation['bridge_after_html'])
    stripped = copy.deepcopy(bridge)
    report('bridge_origin_marker', stripped.attrib.pop('data-origin', None) == 'original-bridge')
    report('original_bridge_exact', signature(stripped) == signature(original_bridge))
    report('exact_ID_set', set(output_ids) == set(source_ids) | {n.get('id') for n in original_bridge.iter() if n.get('id')} | {'credits'})
    for correction in translation['source_corrections']:
        report('original_note_destination:' + correction['id'], correction['bridge_id'] in {n.get('id') for n in bridge.iter()})
    body, main = doc.find('body'), doc.find('.//main')
    report('body_closed_frame', body is not None and [n.tag for n in body] == ['header', 'main', 'footer'] and blank_frame(body))
    report('main_closed_frame', list(main) == [main[0], rendered_anchor(source[0]), rendered_anchor(source[1]), bridge, main[-1]]
           and len(main) == 5 and blank_frame(main))
    label = fragment('ماخذ: <bdi dir="ltr" lang="en">OpenStax Elementary Algebra 2e</bdi>، باب <bdi dir="ltr" lang="en">Foundations</bdi>، سبق «'
                     + manifest['module_title_pnb'] + '»۔ ایتھے مضاعف تے پورا ونڈے جان والا پورا سیکشن تے اوہدے نالوں پہلاں والا پیرا ترجمہ کیتے گئے نیں؛ پورا سبق یا پوری کتاب نہیں۔')
    report('main_source_label_no_injection', main[0].tag == 'p' and main[0].attrib == {'class': 'source-label', 'data-origin': 'renderer-ui'}
           and inner(main[0]) == inner(label))
    report('main_status_no_injection', main[-1].tag == 'p' and main[-1].attrib == {'class': 'status', 'data-origin': 'renderer-ui'}
           and not len(main[-1]) and main[-1].text == 'ایس سبق دا اگلا ماخذی سیکشن ایس حصے وچ شامل نہیں۔ پنجاں مقررہ کتاباں دا پورا کم ہن وی جاری اے۔')
    report('header_target_title', text(body.find('header/h1')) == translation['title'])
    report('english_footerLTR', body.find('footer').get('lang') == 'en' and body.find('footer').get('dir') == 'ltr')
    counts = dict(Counter(local(n) for n in source.iter() if n is not source))
    counts['source_ids'] = len(source_ids)
    counts['source_text_blocks'] = len(specs)
    counts['empty_table_cells'] = sum(local(n) == 'entry' and not len(n) and not text(n).strip()
                                     for n in source.iter())
    return counts


def validate_images(doc, source, manifest, report=check, digests=None):
    media = [n for n in source.iter() if local(n) == 'media']
    images = list(doc.iter('img'))
    report('2images_no_figures', len(media) == len(images) == len(manifest['images']) == 2 and len(list(doc.iter('figure'))) == 0)
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
        wrapper = p[scroll]
        report('media_wrapper_closed:' + sid, wrapper.attrib == {'class': 'source-media', 'data-source-child': sid}
               and len(wrapper) == 2 and list(scroll) == [actual] and blank_frame(wrapper) and blank_frame(scroll))
        hint = wrapper[-1]
        expected_hint = fragment('چھوٹی سکرین اُتے پوری شکل ویکھن لئی پاسے سرکاؤ، یا <a href="'
                                 + actual.get('src') + '">اصل شکل وکھری کھولو</a>۔')
        report('image_hint_no_injection:' + sid, hint.attrib == {'class': 'scroll-hint', 'data-origin': 'renderer-ui'}
               and inner(hint) == inner(expected_hint))
        records.append({'media_id': sid, 'path': spec['path'], 'sha256': spec['sha256'], 'bytes': len(data),
                        'width': dims[0], 'height': dims[1], 'source_mime': src.get('mime-type'), 'actual_mime': 'image/jpeg'})
    return records


def validate_arithmetic(doc, source, report=check):
    results = {}
    grid = next(n for n in source.iter() if local(n) == 'table' and any(local(c) == 'thead' for c in n.iter()))
    sid = grid.get('id')
    source_rows = [n for n in grid.iter() if local(n) == 'row']
    actual_rows = list(identified(doc, sid).iter('tr'))
    counting = [int(text(n)) for n in source_rows[0][1:]]
    report('grid_counting_columns', counting == list(range(1, 13)))
    products = 0
    for original, actual in zip(source_rows[1:], actual_rows[1:]):
        multiplier = int(NUMS.search(text(original[0]))[0])
        values = [int(text(n)) for n in actual[1:]]
        source_values = [int(text(n)) for n in original[1:]]
        report('grid_products:' + str(multiplier), values == source_values == [multiplier * n for n in counting])
        products += len(values)
    report('108source_products', products == 108)
    results['grid_products'] = products
    results['try_it'] = []
    for note in source.iter():
        if local(note) != 'note' or note.get('class') != 'try':
            continue
        problem = next(n for n in note.iter() if local(n) == 'problem')
        solution = next(n for n in note.iter() if local(n) == 'solution')
        values = [int(n.replace(',', '')) for n in NUMS.findall(text(problem))]
        number, divisors = values[0], values[1:]
        answer = [int(n) for n in NUMS.findall(text(identified(doc, solution.get('id'))))]
        expected = [d for d in divisors if number % d == 0]
        report('tryit_source_and_arithmetic:' + note.get('id'), answer == [int(n) for n in NUMS.findall(text(solution))] == expected)
        results['try_it'].append({'number': number, 'tested_divisors': divisors, 'divisible_by': expected})
    exercise = next(n for n in source.iter() if local(n) == 'example')
    problem = next(n for n in exercise.iter() if local(n) == 'problem')
    values = [int(n.replace(',', '')) for n in NUMS.findall(text(problem))]
    number, divisors = values[0], values[1:]
    worked = next(n for n in exercise.iter() if local(n) == 'table')
    worked_math = next(n for n in worked.iter() if local(n) == 'math')
    mn = [int(text(n)) for n in worked_math.iter() if local(n) == 'mn']
    report('source_worked_digit_sum', mn[:-1] == list(map(int, str(number))) and mn[-1] == sum(mn[:-1]))
    source_statements = []
    for key, original in source_specs(source).items():
        if not key.startswith(worked.get('id') + '/row/'):
            continue
        source_text = text(original)
        target_text = text(target_block(doc, key))
        if source_text.startswith('Yes.'):
            report('worked_yes_marker:' + key, target_text.startswith('ہاں۔'))
        if source_text.startswith('No'):
            report('worked_no_marker:' + key, target_text.startswith('نہیں'))
        for value, negation, divisor in re.findall(r'(\d[\d,]*) is (not )?divis(?:i)?ble by (\d+)', source_text):
            dividend, by = int(value.replace(',', '')), int(divisor)
            report('source_worked_statement_arithmetic:' + key, (dividend % by == 0) == (not bool(negation)))
            source_statements.append({'number': dividend, 'divisor': by, 'divisible': not bool(negation)})
        if 'but not by' in source_text:
            dividend = int(NUMS.search(source_text)[0].replace(',', ''))
            by = int(re.search(r'but not by (\d+)', source_text)[1])
            report('source_worked_but_not_arithmetic:' + key, dividend % by != 0)
    results['worked'] = {'number': number, 'tested_divisors': divisors, 'divisible_by': [d for d in divisors if number % d == 0],
                         'digit_sum': mn[-1], 'source_statements_checked': source_statements}
    return results


def validate_notices(doc, manifest, report=check, record=None):
    notices = record if record is not None else json.loads(NOTICES.read_text(encoding='utf-8'))
    report('notice_scope_hashes', notices['unit'] == 'A10-003' and notices['manifest_sha256'] == sha(MANIFEST)
           and notices['excerpt_sha256'] == manifest['excerpt_sha256'] and notices['whole_book_translation_complete'] is False)
    report('notice2images', len(notices['images']) == 2)
    for entry in manifest['existing_notice_inputs']:
        report('logical_notice_hash:' + entry['path'],
               hashlib.sha256((ROOT / entry['path']).read_bytes().replace(b'\r\n', b'\n')).hexdigest() == entry['sha256'])
    report('notice_inputs_preserved', notices['existing_notice_inputs'] == manifest['existing_notice_inputs'])
    report('notice_verbatim_preserved', notices['release_notice_verbatim'] == (BASE / 'provenance/A10-release/NOTICE.txt').read_text(encoding='utf-8'))
    source = E.parse(BASE / 'source-excerpts/a10-unit-003.cnxml').getroot()
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
    report('previous_unit_navigation', 'a10-unit-002.html' in links)
    return links


def mutations(doc, source, manifest, translation):
    names = []
    def reject(name, mutate, validator=None):
        changed = copy.deepcopy(doc)
        mutate(changed)
        try:
            (validator or (lambda d: validate_dom(d, source, manifest, translation)))(changed)
        except (AssertionError, IndexError, KeyError, ValueError):
            names.append(name)
        else:
            raise AssertionError('mutation_not_rejected:' + name)

    grid_id = next(n.get('id') for n in source.iter() if local(n) == 'table' and any(local(c) == 'thead' for c in n.iter()))
    worked_id = next(n.get('id') for n in source.iter() if local(n) == 'table' and 'summary' in n.attrib)
    first_media = manifest['images'][0]['media_id']
    second_media = manifest['images'][1]['media_id']
    reject('grid_product_changed', lambda d: setattr(identified(d, grid_id).find('tbody')[0][1].find('bdi'), 'text', '999'))
    def swap_grid(d):
        row = identified(d, grid_id).find('tbody')[0]
        row[1], row[2] = row[2], row[1]
    reject('grid_cells_swapped', swap_grid)
    reject('tenth_source_row_removed', lambda d: identified(d, grid_id).find('tbody').remove(identified(d, grid_id).find('tbody')[-1]))
    reject('source_column_header_changed_to_data', lambda d: setattr(identified(d, grid_id).find('thead')[0][0], 'tag', 'td'))
    reject('source_header_scope_changed', lambda d: identified(d, grid_id).find('thead')[0][1].set('scope', 'row'))
    reject('row_header_scope_changed', lambda d: identified(d, grid_id).find('tbody')[0][0].set('scope', 'col'))
    reject('thead_changed_to_tbody', lambda d: setattr(identified(d, grid_id).find('thead'), 'tag', 'tbody'))
    reject('source_colspec_changed', lambda d: identified(d, grid_id).find('colgroup')[0].set('data-source-colname', 'wrong'))
    reject('source_alignment_trace_changed', lambda d: identified(d, grid_id).find('tbody')[0][0].set('data-source-align', 'right'))
    reject('table_geometry_RTL', lambda d: identified(d, grid_id).set('dir', 'rtl'))
    reject('legacy_summary_origin_lost', lambda d: identified(d, worked_id).set('data-source-summary-attribute', 'aria-label'))
    reject('blank_cell_filled', lambda d: setattr(identified(d, worked_id).find('tbody')[0][1], 'text', '1'))
    reject('blank_cell_removed', lambda d: identified(d, worked_id).find('tbody')[0].remove(identified(d, worked_id).find('tbody')[0][1]))
    reject('worked_header_invented', lambda d: setattr(identified(d, worked_id).find('tbody')[0][0], 'tag', 'th'))
    reject('math_operand_changed', lambda d: setattr(next(n for n in d.iter() if local(n) == 'mn'), 'text', '16'))
    def remove_period(d):
        period = next(n for n in d.iter() if local(n) == 'mo' and n.text == '.')
        parents(d)[period].remove(period)
    reject('math_terminal_period_removed', remove_period)
    reject('math_direction_changed', lambda d: next(n for n in d.iter() if local(n) == 'math').set('dir', 'rtl'))
    reject('italic_variable_changed', lambda d: setattr(identified(d, 'newelem_para01').find('em/bdi'), 'text', 'z'))
    reject('source_term_id_removed', lambda d: identified(d, 'term-00007').attrib.pop('id'))
    reject('source_prose_numeral_changed', lambda d: setattr(identified(d, 'fs-id1170655126540').find('bdi'), 'text', '9'))
    reject('source_prose_tail_injected', lambda d: setattr(identified(d, 'fs-id1170655126540').find('bdi'), 'tail', ' غلط'))
    reject('source_link_retargeted', lambda d: identified(d, 'fs-id1170654984223').find('a').set('href', '#term-00007'))
    reject('source_newline_removed', lambda d: target_block(d, worked_id + '/row/2/entry/2').remove(target_block(d, worked_id + '/row/2/entry/2').find('br')))
    reject('worked_yes_no_reversed', lambda d: setattr(target_block(d, worked_id + '/row/5/entry/2'), 'text', 'نہیں۔ '))
    reject('tryit_answer_changed', lambda d: setattr(identified(d, 'fs-id1170655200173').find('bdi'), 'text', '5'),
           lambda d: validate_arithmetic(d, source))
    reject('direct_activity_text_missing', lambda d: setattr(target_block(d, 'fs-id1166426279739').find('bdi'), 'tail', None))
    reject('source_solution_title_duplicate', lambda d: identified(d, 'fs-id1170655229161').insert(0, copy.deepcopy(identified(d, 'fs-id1170655229161').find('h3'))))
    reject('source_container_anonymous_text', lambda d: setattr(identified(d, 'fs-id1170655199097'), 'text', 'غلط'))
    reject('source_container_anonymous_child', lambda d: E.SubElement(identified(d, 'fs-id1170655199097'), 'p', {'dir': 'ltr'}))
    reject('source_container_changed_direction', lambda d: identified(d, 'fs-id1170655199097').set('dir', 'ltr'))
    reject('source_table_wrapper_anonymous_text', lambda d: setattr(parents(d)[parents(d)[identified(d, grid_id)]], 'text', 'غلط'))
    reject('source_table_wrapper_extra_UI_paragraph', lambda d: E.SubElement(parents(d)[parents(d)[identified(d, grid_id)]], 'p', {'data-origin': 'renderer-ui'}))
    reject('source_image_wrapper_extra_UI', lambda d: E.SubElement(parents(d)[parents(d)[identified(d, first_media)]], 'p', {'data-origin': 'renderer-ui'}),
           lambda d: validate_images(d, source, manifest))
    reject('image_asset_swapped', lambda d: identified(d, first_media).set('src', identified(d, second_media).get('src')),
           lambda d: validate_images(d, source, manifest))
    reject('image_dimensions_changed', lambda d: identified(d, first_media).set('width', '394'),
           lambda d: validate_images(d, source, manifest))
    reject('source_image_mime_changed', lambda d: identified(d, first_media).set('data-source-image-mime', 'image/png'),
           lambda d: validate_images(d, source, manifest))
    reject('faithful_alt_trace_changed', lambda d: identified(d, first_media).set('data-source-alt', 'غلط'))
    reject('accessible_alt_changed', lambda d: identified(d, first_media).set('alt', 'غلط'))
    reject('faithful_summary_trace_changed', lambda d: identified(d, grid_id).set('data-source-summary', 'غلط'))
    reject('accessible_summary_changed', lambda d: identified(d, grid_id).set('aria-label', 'غلط'))
    def main_injection(d):
        p = E.SubElement(d.find('.//main'), 'p')
        isolated = E.SubElement(p, 'bdi', {'dir': 'ltr'})
        isolated.text = '4962 = 999'
    reject('correctly_isolated_main_paragraph_injection', main_injection)
    reject('body_paragraph_injection', lambda d: E.SubElement(d.find('body'), 'p', {'dir': 'ltr'}))
    reject('main_anonymous_tail', lambda d: setattr(d.find('.//main')[1], 'tail', ' غلط'))
    reject('main_label_prose_injection', lambda d: setattr(d.find('.//main')[0], 'text', 'غلط'))
    reject('main_status_prose_injection', lambda d: setattr(d.find('.//main')[-1], 'text', 'غلط'))
    reject('unlabeled_original_bridge', lambda d: identified(d, 'a10-003-original-bridge').attrib.pop('data-origin'))
    reject('original_correction_text_changed', lambda d: setattr(identified(d, 'a10-003-table-range'), 'text', 'غلط'))
    reject('bad_direction_control', lambda d: setattr(identified(d, 'newelem_para01'), 'text', '\u202e'))
    try:
        validate_images(doc, source, manifest, digests={first_media: '0' * 64})
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
        raise AssertionError('notice_mutation_not_rejected')
    return names


def main():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    translation = json.loads(TRANSLATION.read_text(encoding='utf-8'))
    source = E.parse(BASE / 'source-excerpts/a10-unit-003.cnxml').getroot()
    inputs = [MANIFEST, TRANSLATION, BASE / 'source-excerpts/a10-unit-003.cnxml',
              BASE / 'qa/a10-unit-003-language-notes.md', BASE / 'plans/A10-003-scope.json',
              BASE / 'scripts/prepare_a10_003.py', BASE / 'scripts/build_a10_003.py', Path(__file__),
              BASE / 'scripts/prepare_a10.py', BASE / 'scripts/build_a10.py', BASE / 'styles/reader.css',
              BASE / 'sources.lock.json', ROOT / manifest['canonical_local_path'],
              ROOT / manifest['indonesian_comparison_path'], ROOT / manifest['media_authority_manifest_path']]
    inputs += [ROOT / item['path'] for item in manifest['existing_notice_inputs']]
    inputs += [ROOT / item['canonical_local_path'] for item in manifest['images']]
    inputs += list(sorted((BASE / 'canon/receipts').glob('A10-003-*.json')))
    initial = {str(p): sha(p) for p in inputs}
    hashes = []
    for _ in range(2):
        subprocess.run([sys.executable, str(BASE / 'scripts/prepare_a10_003.py')], check=True, capture_output=True)
        subprocess.run([sys.executable, str(BASE / 'scripts/build_a10_003.py')], check=True, capture_output=True)
        hashes.append((sha(READER), sha(NOTICES)))
    check('two_prepare_build_runs_deterministic', hashes[0] == hashes[1])
    doc = parse_reader(READER.read_text(encoding='utf-8'))
    passed = []
    def report(name, condition):
        check(name, condition)
        passed.append(name)
    validate_source(source, manifest, report)
    structural = validate_dom(doc, source, manifest, translation, report)
    image_records = validate_images(doc, source, manifest, report)
    arithmetic = validate_arithmetic(doc, source, report)
    validate_notices(doc, manifest, report)
    links = validate_links(doc, report)
    negative = mutations(doc, source, manifest, translation)
    report('two_prepare_build_runs_deterministic', hashes[0] == hashes[1])
    report('stable_input_hashes', initial == {str(p): sha(p) for p in inputs})
    artifacts = list(dict.fromkeys(inputs + [READER, NOTICES] + [BASE / image['path'] for image in manifest['images']]))
    record = {
        'unit': 'A10-003', 'scope': 'm82452 standalone newelem_para01 plus complete fs-id1170655199097; stop before fs-id1170655247410',
        'status': 'passed', 'checks_passed': len(passed), 'checks': passed,
        'source_derived_counts': structural, 'detached_mutations_rejected': negative,
        'reader_sha256': sha(READER), 'component_notices_sha256': sha(NOTICES),
        'artifacts': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p), 'bytes': p.stat().st_size} for p in artifacts],
        'artifact_hash_policy': 'Exact current artifact bytes. Existing notice semantic pins separately normalize only CRLF to LF.',
        'original_images': image_records, 'arithmetic_checks': arithmetic, 'local_references': links,
        'limitations': [
            'Structural/source-derived arithmetic checks are not native-speaker or educator certification.',
            'Browser/mobile and assistive-technology review are separate; this script does not certify visual layout.',
            'Source2-through9 wording is retained although the sourcegrid includes10. Original range/domain notes remain labeled and separate.',
            'Counting-number convention and positive-whole-number/nonzero-divisor scope are not generalized into a universal definition claim.',
            'Three exact MathML trees, all108grid products and both source TryIt divisor sets are checked; no universal theorem prover is claimed.',
            'OriginalJPEG identity and retained notice policy are checked, not new image clearance or a repeated supply/license audit.',
            'Full A10 and five-work workflow remain incomplete.'
        ]
    }
    RECEIPT.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f'A10-003 QA passed: {len(passed)} checks, {len(negative)} detached mutations; reader {sha(READER)}')


if __name__ == '__main__':
    main()
