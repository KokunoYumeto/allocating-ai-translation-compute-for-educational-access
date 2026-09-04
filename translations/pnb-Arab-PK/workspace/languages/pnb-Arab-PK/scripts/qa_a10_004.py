"""Independent CNXML-derived A10-004 QA; no renderer/expected-DOM imports."""
from pathlib import Path
from collections import Counter
from urllib.parse import urlsplit, unquote
import copy
import csv
import hashlib
import html
import io
import json
import math
import re
import subprocess
import sys
import xml.etree.ElementTree as E
from PIL import Image

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
MANIFEST = BASE / 'source-excerpts/manifest-a10-004.json'
TRANSLATION = BASE / 'translations/a10-unit-004.json'
READER = BASE / 'reader/a10-unit-004.html'
NOTICES = BASE / 'provenance/a10-unit-004-component-notices.json'
RECEIPT = BASE / 'qa/structural-a10-004.json'
CNXML = 'http://cnx.rice.edu/cnxml'
MATH = 'http://www.w3.org/1998/Math/MathML'
BLOCKS = {'figure', 'para', 'note', 'list', 'exercise', 'problem', 'solution', 'section', 'example', 'media', 'table'}
FORBIDDEN = re.compile('[\u0a00-\u0a7f\ufffd\u061c\u200b\u200e\u200f\u202a-\u202e\u2066-\u2069]')


def check(name, condition):
    if not condition:
        raise AssertionError(name)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local(n):
    return n.tag.rsplit('}', 1)[-1]


def text(n):
    return ''.join(n.itertext())


def parents(root):
    return {child: n for n in root.iter() for child in n}


def signature(n):
    return n.tag, tuple(sorted(n.attrib.items())), n.text, tuple((signature(c), c.tail) for c in n)


def inner(n):
    return n.text, tuple((signature(c), c.tail) for c in n)


def fragment(value):
    return E.fromstring('<fragment>' + re.sub(r'<br\s*>', '<br/>', value) + '</fragment>')


def parse_reader(value):
    value = value[value.index('<html'):]
    value = re.sub(r'<(meta|img|br|col)\b([^<>]*?)(?<!/)>', r'<\1\2/>', value)
    return E.fromstring(value)


def only(nodes, message):
    check(message, len(nodes) == 1)
    return nodes[0]


def identified(root, sid):
    return only([n for n in root.iter() if n.get('id') == sid], 'unique_id:' + sid)


def block(root, key):
    return only([n for n in root.iter() if n.get('data-source-key') == key], 'unique_key:' + key)


def blank_frame(n):
    return not (n.text or '').strip() and all(not (c.tail or '').strip() for c in n)


def replace_child(parent, child, replacement):
    index = list(parent).index(child)
    value = replacement + (child.tail or '')
    if index:
        parent[index - 1].tail = (parent[index - 1].tail or '') + value
    else:
        parent.text = (parent.text or '') + value
    parent.remove(child)


def source_specs(source):
    p, specs = parents(source), {}
    for n in source.iter():
        name = local(n)
        if name == 'para':
            key = n.get('id')
        elif name == 'title':
            key = p[n].get('id') + '/title'
        elif name in {'media', 'table'}:
            key = n.get('id') + ('/alt' if name == 'media' else '/summary')
        elif name == 'note' and not len(n) and (n.text or '').strip():
            key = n.get('id')
        elif name == 'item':
            key = p[n].get('id') + '/item/' + str(list(p[n]).index(n) + 1)
        elif name == 'entry':
            table = p[n]
            while local(table) != 'table':
                table = p[table]
            rows = [x for x in table.iter() if local(x) == 'row']
            key = table.get('id') + '/row/' + str(rows.index(p[n]) + 1) + '/entry/' + str(list(p[n]).index(n) + 1)
        else:
            continue
        check('unique_source_key:' + str(key), key is not None and key not in specs)
        specs[key] = n
    return specs


def source_prose(n):
    if local(n) == 'media':
        return n.get('alt', '')
    if local(n) == 'table':
        return n.get('aria-label', n.get('summary', ''))
    value = n.text or ''
    for c in n:
        if local(c) not in BLOCKS | {'math', 'link'}:
            value += source_prose(c)
        value += c.tail or ''
    return value


def validate_source(source, manifest, translation, report=check):
    canonical_path = ROOT / manifest['canonical_local_path']
    data = canonical_path.read_bytes()
    report('canonical_hash_size', sha(canonical_path) == manifest['full_module_sha256'] and len(data) == manifest['full_module_bytes'])
    report('canonical_git_blob', hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == manifest['canonical_git_blob_sha1'])
    lock = json.loads((BASE / 'sources.lock.json').read_text(encoding='utf-8'))
    pin = next(x for x in lock['repositories'] if x['role'] == 'A10+A20 upstream')
    report('locked_upstream_identity', (pin['commit'], pin['tree']) == (manifest['commit'], manifest['tree']))
    canonical = E.fromstring(data)
    content = canonical.find('{' + CNXML + '}content')
    selected = list(content)[5:7]
    report('whole_instruction_and_review_boundary', [x.get('id') for x in selected] == manifest['selection_ids'] == ['fs-id1170655247410', 'fs-id1170655222085'])
    report('section_and_review_extent', [len(x) for x in selected] == [46, 2] and manifest['section_direct_children_included'] == 46 and manifest['review_direct_children_included'] == 2)
    report('required_next_exercises', content[7].get('id') == manifest['next_source_id'] == 'fs-id1170655190123' and content[7].get('class') == 'section-exercises')
    report('excerpt_exact_canonical_trees', [signature(n) for n in selected] == [signature(n) for n in source])
    excerpt_path = BASE / 'source-excerpts/a10-unit-004.cnxml'
    report('excerpt_frozen_hash_size', sha(excerpt_path) == manifest['excerpt_sha256'] and excerpt_path.stat().st_size == manifest['excerpt_bytes'])
    report('scope_not_complete_book', manifest['whole_assignment_complete'] is False and source.get('id') == manifest['excerpt_root_id'] == 'a10-unit-004-excerpt')
    comparison = ROOT / manifest['indonesian_comparison_path']
    report('comparison_hash', sha(comparison) == manifest['indonesian_comparison_sha256'])
    comparison_root = E.parse(comparison).getroot()
    comparison_selected = [n for n in comparison_root.iter() if n.get('id') in manifest['selection_ids']]
    shape = lambda roots: [(n.tag, n.get('id'), n.get('src'), n.get('target-id'), n.get('url')) for r in roots for n in r.iter()]
    report('comparison_same_structure_and_refs', shape(selected) == shape(comparison_selected))
    specs = source_specs(source)
    ids = [n.get('id') for n in source.iter() if n is not source and n.get('id')]
    report('source_ids_168_order', ids == manifest['source_ids_in_document_order'] and len(ids) == 168 and len(set(ids)) == 168)
    report('source_keys_150_order', list(specs) == manifest['source_block_keys_in_document_order'] == list(translation['source_blocks']) and len(specs) == 150)
    counts = Counter(local(n) for n in source.iter())
    expected = {'section':2, 'title':16, 'para':52, 'media':15, 'image':15, 'math':15, 'figure':1, 'table':3, 'entry':14, 'note':20, 'example':5, 'exercise':15, 'solution':15, 'list':13, 'item':48, 'newline':6, 'term':12}
    for name, count in expected.items():
        report('source_count:' + name, counts[name] == count)
    report('no_source_mathml_table_or_part_token', counts['mtable'] == 0 and not any(local(n) == 'span' and n.get('class') == 'token' for n in source.iter()))
    numerals, reordered, placeholders = 0, [], Counter()
    for key, n in specs.items():
        raw = translation['source_blocks'][key]
        value = re.sub(r'\{\{[^}]+\}\}', '', raw)
        target = fragment(value)
        source_digits, target_digits = re.findall(r'\d+', source_prose(n)), re.findall(r'\d+', text(target))
        report('source_prose_numerals:' + key, Counter(source_digits) == Counter(target_digits))
        numerals += len(source_digits)
        if source_digits != target_digits:
            reordered.append(key)
        if local(n) not in {'media', 'table'}:
            for kind, chosen in [('math', [c for c in n if local(c) == 'math']), ('child', [c for c in n if local(c) in BLOCKS]), ('link', [c for c in n if local(c) == 'link'])]:
                positions = [int(i) for i in re.findall(r'\{\{' + kind + r':(\d+)\}\}', raw)]
                report('placeholder_ownership:' + key + ':' + kind, positions == list(range(len(chosen))))
                placeholders[kind] += len(chosen)
            report('source_explicit_newlines:' + key, len(list(target.iter('br'))) == sum(local(c) == 'newline' for c in n))
    report('488_numerals_genitive_exceptions_only', numerals == 488 and reordered == manifest['renderer_contract']['genitive_numeric_order_exceptions'])
    report('all_placeholder_totals', placeholders == {'math':15, 'child':12, 'link':3})
    report('target_locale_unicode', translation['locale'] == 'pnb-Arab-PK' and not FORBIDDEN.search(TRANSLATION.read_text(encoding='utf-8')))
    report('correction_contract_matches', translation['source_corrections'] == manifest['source_discrepancies'])
    return {'source_ids':len(ids), 'source_keys':len(specs), 'mathml':counts['math'], 'images':counts['image'], 'tables':counts['table'], 'cells':counts['entry'], 'prose_numerals':numerals, 'newlines':counts['newline'], 'lists':counts['list'], 'list_items':counts['item']}


def correction_map(translation):
    result = {}
    for record in translation['source_corrections']:
        for key in record['source_keys']:
            result.setdefault(key, []).append(record)
    return result


def validate_advisory(n, key, corrections, report=check):
    records = corrections.get(key, [])
    report('advisory_attributes:' + key, n.tag == 'p' and n.attrib == {'class':'source-original-advisory', 'data-origin':'renderer-ui', 'data-source-advisory-for':key})
    report('advisory_bound_records:' + key, bool(records) and len(n) == len(records) and n.text == 'ایس ماخذی گل نال ')
    for i, (a, record) in enumerate(zip(n, records)):
        report('advisory_target:' + key + ':' + str(i), a.tag == 'a' and a.attrib == {'href':'#'+record['bridge_id'], 'data-correction-id':record['id']} and not len(a) and a.text == 'ساڈی وکھری درستی تے وضاحت')
        report('advisory_tail:' + key + ':' + str(i), a.tail == ('؛ ' if i < len(records)-1 else ' وی پڑھو۔'))


def validate_dom(doc, source, manifest, translation, report=check):
    specs, corrections = source_specs(source), correction_map(translation)
    sp, dp = parents(source), parents(doc)
    source_ids = [n.get('id') for n in source.iter() if n is not source and n.get('id')]
    html_ids = [n.get('id') for n in doc.iter() if n.get('id')]
    report('html_locale_RTL', doc.tag == 'html' and doc.attrib == {'lang':'pnb-Arab-PK','dir':'rtl'})
    report('unique_output_ids', len(html_ids) == len(set(html_ids)))
    report('rendered_source_ids_order', [i for i in html_ids if i in set(source_ids)] == source_ids)
    for n in source.iter():
        if n is source or not n.get('id'):
            continue
        target = identified(doc, n.get('id'))
        a, expected_parent = sp[n], None
        while a is not source:
            if a.get('id'):
                expected_parent = a.get('id')
                break
            a = sp[a]
        b, actual_parent = dp.get(target), None
        while b is not None:
            if b.get('id') in source_ids:
                actual_parent = b.get('id')
                break
            b = dp.get(b)
        report('source_id_ancestry:' + n.get('id'), expected_parent == actual_parent)
    keyed = [n.get('data-source-key') for n in doc.iter() if n.get('data-source-key')]
    expected_keyed = [key for key, n in specs.items() if local(n) not in {'media','table'}]
    report('exact_rendered_key_inventory', keyed == expected_keyed)
    advisory_nodes = [n for n in doc.iter() if n.get('data-source-advisory-for')]
    report('one_advisory_per_corrected_source_key', Counter(n.get('data-source-advisory-for') for n in advisory_nodes) == Counter({k:1 for k in corrections}))
    for n in advisory_nodes:
        validate_advisory(n, n.get('data-source-advisory-for'), corrections, report)

    def described(key):
        return ' '.join(dict.fromkeys(r['bridge_id'] for r in corrections.get(key, []))) or None

    def source_anchor(n):
        name = local(n)
        if name in {'media','table'}:
            return only([x for x in doc.iter() if x.get('data-source-child') == n.get('id')], 'source_wrapper:' + n.get('id'))
        if name in {'title','item','entry'}:
            return block(doc, next(k for k, v in specs.items() if v is n))
        if name == 'para' and n.get('id') in corrections:
            return only([x for x in doc.iter() if x.get('data-source-block-owner') == n.get('id')], 'paragraph_wrapper:' + n.get('id'))
        return identified(doc, n.get('id'))

    math_count = 0
    for key, n in specs.items():
        if local(n) in {'media','table'}:
            continue
        rendered = block(doc, key)
        expected_tag = 'p' if local(n) in {'para','note'} else 'li' if local(n) == 'item' else 'td' if local(n) == 'entry' else 'h2' if local(sp[n]) == 'section' else 'h3'
        report('block_tag:' + key, rendered.tag == expected_tag)
        if local(n) != 'note':
            report('block_source_tag:' + key, rendered.get('data-source-tag') == local(n))
        report('block_describedby:' + key, rendered.get('aria-describedby') == described(key))
        if local(n) != 'entry':
            expected_attrs = {'data-source-key':key}
            if local(n) == 'note':
                expected_attrs['class'] = 'source-note-text'
            else:
                expected_attrs['data-source-tag'] = local(n)
                if n.get('id'):
                    expected_attrs['id'] = n.get('id')
                if local(n) == 'para':
                    expected_attrs['class'] = 'source-para'
                if described(key):
                    expected_attrs['aria-describedby'] = described(key)
            report('block_exact_attributes:' + key, rendered.attrib == expected_attrs)
        clone = copy.deepcopy(rendered)
        direct_children = [c for c in n if local(c) in BLOCKS]
        for i, child in enumerate(direct_children):
            candidates = [x for x in clone.iter() if x.get('data-source-child') == child.get('id')] if local(child) in {'media','table'} else [x for x in clone.iter() if x.get('id') == child.get('id')]
            current = only(candidates, 'owned_nested_child:' + key + ':' + str(i))
            replace_child(parents(clone)[current], current, '{{child:' + str(i) + '}}')
        maths = [c for c in n if local(c) == 'math']
        output_maths = list(clone.iter('{' + MATH + '}math'))
        report('math_owner_count:' + key, len(output_maths) == len(maths))
        for i, (original, target) in enumerate(zip(maths, output_maths)):
            math_count += 1
            mp = parents(clone)
            wrapper = mp[target]
            report('math_isolation:' + key + ':' + str(i), wrapper.tag == 'span' and wrapper.attrib == {'class':'math-isolate','dir':'ltr'} and len(wrapper) == 1 and not wrapper.text and not target.tail and target.get('dir') == 'ltr')
            restored = copy.deepcopy(target)
            restored.attrib.pop('dir', None)
            report('exact_source_math_tree:' + key + ':' + str(i), signature(restored) == signature(original))
            replace_child(mp[wrapper], wrapper, '{{math:' + str(i) + '}}')
        source_links = [c for c in n if local(c) == 'link']
        actual_links = [x for x in clone.iter('a') if x.get('data-source-link-owner')]
        report('link_owner_count:' + key, len(actual_links) == len(source_links))
        for i, (link, actual) in enumerate(zip(source_links, actual_links)):
            spec = only([r for r in manifest['references'] if r['source_key'] == key and r['link_index'] == i], 'bound_reference:' + key)
            identity = link.get('target-id') or link.get('url')
            attrs = {'href':spec['href'],'data-source-link-owner':key,'data-source-link-index':str(i), 'data-source-url' if link.get('url') else 'data-source-target':identity}
            report('exact_source_reference:' + key, actual.attrib == attrs and identity == spec['id'])
            report('source_link_display:' + key, inner(actual) == inner(fragment(translation['source_link_labels'][key+'/link/'+str(i)])))
            if link.get('url'):
                report('external_url_unchanged:' + key, spec['href'] == link.get('url') and spec['kind'] == 'external')
            replace_child(parents(clone)[actual], actual, '{{link:' + str(i) + '}}')
        for ui in list(clone.iter()):
            if ui.get('data-source-advisory-for'):
                validate_advisory(ui, key, corrections, report)
                replace_child(parents(clone)[ui], ui, '')
        report('exact_source_translation_content:' + key, inner(clone) == inner(fragment(translation['source_blocks'][key])))
        if local(n) in {'para','note'}:
            original_vars = [x for x in n.iter() if local(x) == 'emphasis' and x.get('effect') == 'italics' and re.fullmatch('[a-z]', text(x))]
            target_vars = [x for x in rendered.iter('em') if re.fullmatch('[a-z]', text(x))]
            report('all_inline_variables:' + key, [text(x) for x in original_vars] == [text(x) for x in target_vars])
            for orig_em, target_em in zip(original_vars,target_vars):
                report('latin_variable_isolated:' + key + ':' + text(orig_em), text(orig_em) == text(target_em) and len(target_em) == 1 and target_em[0].tag == 'bdi' and target_em[0].attrib == {'dir':'ltr','lang':'en'})
    report('all15math_exact_no_ledgers', math_count == len(list(doc.iter('{' + MATH + '}math'))) == 15 and not any('data-source-text-edits' in n.attrib or 'data-source-punctuation' in n.attrib for n in doc.iter()))
    report('no_inline_part_groups', not any('source-inline-part' in n.get('class','').split() for n in doc.iter()))

    # Structural containers must contain exactly their source children and only
    # declared UI; unkeyed paragraphs and anonymous text are not ignored.
    for n in source.iter():
        name = local(n)
        if name not in {'section','example','exercise','problem','solution','figure','note','list'}:
            continue
        target = identified(doc, n.get('id'))
        expected_container_tag = {'section':'section','example':'section','exercise':'div','problem':'div','solution':'section','figure':'figure','note':'aside','list':'ol' if n.get('list-type') == 'enumerated' else 'ul'}[name]
        report('container_element_type:' + n.get('id'), target.tag == expected_container_tag)
        container_attrs = {'id':n.get('id'),'data-source-tag':name}
        if name == 'section':
            container_attrs.update({'class':'translated','data-source-class':n.get('class','')})
        elif name in {'example','exercise','problem','solution'}:
            container_attrs['class'] = 'source-'+name
            if name == 'solution' and not any(local(c) == 'title' for c in n):
                container_attrs['aria-label'] = 'حل'
        elif name == 'note':
            container_attrs.update({'class':'source-note source-'+n.get('class',''),'data-source-class':n.get('class','')})
            if n.get('class') == 'try':
                container_attrs['aria-label'] = 'آپ کر کے ویکھو'
        elif name == 'list':
            for field in ('list-type','number-style','bullet-style','display','class'):
                container_attrs['data-source-'+field] = n.get(field,'')
            kind, bullet = n.get('list-type'), n.get('bullet-style')
            container_attrs['role'] = 'list'
            container_attrs['class'] = ('source-enumerated' if kind == 'enumerated' else 'source-bulleted'+(' source-open-circle' if bullet == 'open-circle' else '') if kind == 'bulleted' else 'source-resource-list')
        report('container_exact_attributes:' + n.get('id'), target.attrib == container_attrs)
        if name == 'note' and not len(n) and (n.text or '').strip():
            report('direct_text_note_frame:' + n.get('id'), len(target) == 1 and target[0] is block(doc, n.get('id')) and blank_frame(target))
            continue
        expected = [source_anchor(c) for c in n]
        ui = []
        if name == 'example':
            label = target[0]
            value = manifest['renderer_contract']['example_labels'][n.get('id')]
            report('one_example_label:' + n.get('id'), label.tag == 'h2' and label.attrib == {'class':'example-label','data-origin':'renderer-ui'} and inner(label) == inner(fragment('حل کیتی مثال <bdi dir="ltr">'+value+'</bdi>')))
            ui = [label]
        if name == 'figure':
            label = target[-1]
            value = next(x['local_label'] for x in manifest['images'] if x['figure_id'] == n.get('id'))
            report('one_figure_label:' + n.get('id'), label.tag == 'figcaption' and label.attrib == {'class':'source-figure-label','data-origin':'renderer-ui'} and inner(label) == inner(fragment('شکل <bdi dir="ltr">'+value+'</bdi>')))
            ui = [label]
        report('container_exact_source_children:' + n.get('id'), [c for c in target if c not in ui] == expected)
        report('container_no_anonymous_text:' + n.get('id'), blank_frame(target) and not (n.text or '').strip() and all(not (c.tail or '').strip() for c in n))
        source_text = target.text or ''
        if name == 'example':
            source_text += ui[0].tail or ''
        report('container_source_text_and_tails:' + n.get('id'), source_text == (n.text or '') and all((c.tail or '') == (original.tail or '') for c, original in zip(expected, n)))
        report('container_source_tag:' + n.get('id'), target.get('data-source-tag') == name)
        if name == 'list':
            kind = n.get('list-type','')
            report('list_tag_type:' + n.get('id'), target.tag == ('ol' if kind == 'enumerated' else 'ul') and target.get('role') == 'list')
            for field in ('list-type','number-style','bullet-style','display','class'):
                report('list_metadata:' + n.get('id') + ':' + field, target.get('data-source-'+field) == n.get(field,''))
        if name == 'solution':
            explicit = [c for c in n if local(c) == 'title']
            report('solution_title_once:' + n.get('id'), len(target.findall('h3')) == len(explicit) and not target.findall('h2'))
    for key in corrections:
        if local(specs[key]) == 'para':
            wrap = source_anchor(specs[key])
            report('paragraph_wrapper_closed:' + key, wrap.tag == 'div' and wrap.attrib == {'class':'source-block-container','data-source-block-owner':key} and len(wrap) == 2 and wrap[0] is block(doc,key) and wrap[1].get('data-source-advisory-for') == key and blank_frame(wrap))
    validate_tables(doc, source, manifest, translation, report)
    validate_frames(doc, source, manifest, translation, source_anchor, report)
    for n in doc.iter():
        if any(k.startswith('on') for k in n.attrib):
            report('no_event_handler', False)
        report('no_embedded_execution:' + local(n), local(n) not in {'script','iframe','object','embed','applet'})
        if n.tag in {'head','style','title'} or any(a.tag == 'head' for a in ancestry(n, dp)):
            continue
        if n.text and re.search('[A-Za-z0-9]', n.text):
            report('visible_Latin_numeric_LTR:' + local(n), any(a.get('dir') == 'ltr' for a in [n]+list(ancestry(n,dp))))
        if n.tail and re.search('[A-Za-z0-9]', n.tail):
            report('visible_tail_LTR:' + local(n), any(a.get('dir') == 'ltr' for a in ancestry(n,dp)))


def ancestry(n, p):
    while n in p:
        n = p[n]
        yield n


def validate_tables(doc, source, manifest, translation, report=check):
    corrections = correction_map(translation)
    total, blanks = 0, 0
    for source_table in [n for n in source.iter() if local(n) == 'table']:
        sid, key = source_table.get('id'), source_table.get('id') + '/summary'
        target = identified(doc, sid)
        source_rows = [n for n in source_table.iter() if local(n) == 'row']
        group = only([n for n in source_table if local(n) == 'tgroup'], 'one_source_tgroup:' + sid)
        spec = only([s for s in manifest['tables'] if s['id'] == sid], 'one_table_spec:' + sid)
        described = ' '.join(dict.fromkeys(r['bridge_id'] for r in corrections.get(key, []))) or None
        override = translation['table_summary_overrides'].get(sid)
        report('table_source_geometry:' + sid, group.get('cols') == '2' and [local(n) for n in group] == ['tbody'] and spec['rows'] == len(source_rows) and spec['columns'] == 2)
        report('table_two_column_LTR:' + sid, target.tag == 'table' and target.get('dir') == 'ltr' and target.get('data-source-tgroup-cols') == '2')
        report('table_exact_metadata:' + sid, target.get('data-source-tag') == 'table' and target.get('data-source-class') == source_table.get('class') and target.get('data-source-summary-attribute') == 'aria-label' and target.get('data-source-label-empty') == 'true')
        table_fields = {'id','data-source-tag','data-source-summary-attribute','aria-label','data-source-summary','data-description-origin','data-source-tgroup-cols','data-source-label-empty','data-source-class','dir','class'}
        report('table_no_hidden_extra_attributes:' + sid, set(target.attrib) == table_fields | ({'aria-describedby'} if described else set()))
        report('table_preserved_source_summary:' + sid, target.get('data-source-summary') == translation['source_blocks'][key])
        report('table_accessible_original_first:' + sid, target.get('aria-label') == (override or translation['source_blocks'][key]) and target.get('data-description-origin') == ('original-correction' if override else 'source-translation') and target.get('aria-describedby') == described)
        report('table_no_invented_headers:' + sid, [n.tag for n in target] == ['tbody'] and not list(target.iter('th')) and target.get('class') == 'source-table source-worked-table')
        body = target[0]
        report('tbody_closed_frame:' + sid, body.attrib == {'data-source-tag':'tbody'} and len(body) == len(source_rows) and blank_frame(body) and blank_frame(target))
        report('tbody_source_whitespace:' + sid, (body.text or '') == (group[0].text or '') and all((r.tail or '') == (s.tail or '') for r, s in zip(body, source_rows)))
        empty = []
        cell_keys = []
        for ri, (sr, tr) in enumerate(zip(source_rows, body), 1):
            report('row_shape:' + sid + ':' + str(ri), tr.tag == 'tr' and tr.attrib == {'data-source-tag':'row','data-source-row':str(ri)} and len(tr) == len(sr) == 2 and blank_frame(tr))
            report('row_source_text_and_cell_tails:' + sid + ':' + str(ri), (tr.text or '') == (sr.text or '') and all((c.tail or '') == (s.tail or '') for c, s in zip(tr, sr)))
            for ci, (sc, tc) in enumerate(zip(sr, tr), 1):
                total += 1
                cell_key = f'{sid}/row/{ri}/entry/{ci}'
                cell_keys.append(cell_key)
                desc = ' '.join(dict.fromkeys(r['bridge_id'] for r in corrections.get(cell_key, []))) or None
                pure_graphic = len(sc) > 0 and not (sc.text or '').strip() and all(local(c) in {'media','math'} and not (c.tail or '').strip() for c in sc)
                expected_attrs = {'data-source-tag':'entry','data-source-key':cell_key,'dir':'ltr' if pure_graphic else 'rtl'}
                if desc:
                    expected_attrs['aria-describedby'] = desc
                report('cell_owner_geometry:' + cell_key, tc.tag == 'td' and tc.attrib == expected_attrs)
                if not len(sc) and not (sc.text or '').strip():
                    blanks += 1
                    empty.append({'row':ri,'entry':ci})
                    report('source_blank_cell_retained:' + cell_key, not len(tc) and not (tc.text or '').strip())
        report('table_cell_count_and_blank_manifest:' + sid, spec['cells'] == len(source_rows)*2 and spec['empty_cells'] == empty)
        wrapper = only([n for n in doc.iter() if n.get('data-source-child') == sid], 'table_wrapper:' + sid)
        expected_ui_keys = ([key] if key in corrections else []) + [k for k in cell_keys if k in corrections]
        report('table_wrapper_closed:' + sid, wrapper.tag == 'div' and wrapper.attrib == {'class':'source-table-container','data-source-child':sid} and len(wrapper) == 2 + len(expected_ui_keys) and blank_frame(wrapper))
        scroll, hint = wrapper[0], wrapper[1]
        report('table_scroll_region:' + sid, scroll.tag == 'div' and scroll.attrib == {'class':'table-scroll source-table-scroll','dir':'ltr','tabindex':'0','role':'region','aria-label':'جدول؛ لوڑ پئے تے پاسے سرکاؤ'} and list(scroll) == [target] and blank_frame(scroll))
        report('table_hint_exact:' + sid, hint.tag == 'p' and hint.attrib == {'class':'scroll-hint','data-origin':'renderer-ui'} and not len(hint) and hint.text == 'سارے کالم ویکھن لئی لوڑ پئے تے جدول نوں پاسے سرکاؤ۔')
        report('table_advisory_positions:' + sid, [n.get('data-source-advisory-for') for n in list(wrapper)[2:]] == expected_ui_keys)
    report('all14_data_cells_one_blank', total == len(list(doc.iter('td'))) == 14 and blanks == 1)


def validate_frames(doc, source, manifest, translation, source_anchor, report=check):
    report('html_closed_frame', [n.tag for n in doc] == ['head','body'] and blank_frame(doc))
    head, body = doc.find('head'), doc.find('body')
    report('head_closed_frame', [n.tag for n in head] == ['meta','meta','meta','title','style'] and blank_frame(head))
    report('viewport_utf8', head[0].attrib == {'charset':'utf-8'} and head[1].attrib == {'name':'viewport','content':'width=device-width, initial-scale=1'})
    report('head_title_from_target', head.find('title').text == translation['title'] + ' — A10-004')
    report('body_closed_frame', body.attrib == {'class':'a10-reader a10-004-reader'} and [n.tag for n in body] == ['header','main','footer'] and blank_frame(body))
    header, main, footer = list(body)
    report('header_closed_frame', [n.tag for n in header] == ['p','h1','p','p','nav'] and blank_frame(header))
    report('header_identification', inner(header[0]) == inner(fragment('<bdi dir="ltr">A10-004 · A10 / col31130 / m82452</bdi>')) and header[0].attrib == {'class':'eyebrow'})
    report('header_title_subtitle_exact', not len(header[1]) and header[1].text == translation['title'] and not len(header[2]) and header[2].text == translation['subtitle'])
    report('header_review_status_exact', not len(header[3]) and header[3].attrib == {'class':'status'} and header[3].text == 'ابتدائی ترجمہ · پنجابی دے ماہر تے ریاضی دے استاد دی جانچ ہن تک نہیں ہوئی۔')
    nav = header[4]
    nav_hrefs = ['a10-unit-003.html','#'+manifest['scope_from'],'#a10-004-original-bridge','#credits']
    nav_text = ['پچھلا حصہ: مضاعف تے پورا ونڈے جان دی پرکھ','ماخذ دا ترجمہ','لفظاں دی کُنجی تے وضاحت','ماخذ تے انتساب']
    report('navigation_closed_destinations', nav.attrib == {'aria-label':'سبق دے حصے'} and len(nav) == 4 and not nav.text)
    for i, (a, href, label) in enumerate(zip(nav, nav_hrefs, nav_text)):
        report('navigation_exact:' + str(i), a.tag == 'a' and a.attrib == {'href':href} and not len(a) and a.text == label and a.tail == (' · ' if i < 3 else None))
    bridge = identified(doc, 'a10-004-original-bridge')
    expected_bridge = E.fromstring(translation['bridge_after_html'])
    expected_bridge.set('data-origin','original-bridge')
    report('original_bridge_exact_and_labeled', signature(bridge) == signature(expected_bridge))
    report('main_closed_frame', len(main) == 5 and list(main) == [main[0],source_anchor(source[0]),source_anchor(source[1]),bridge,main[-1]] and blank_frame(main))
    source_label = ('ماخذ: <bdi dir="ltr" lang="en">OpenStax Elementary Algebra 2e</bdi>، باب <bdi dir="ltr" lang="en">Foundations</bdi>، سبق «'
                    + manifest['module_title_pnb'] + '»۔ ایتھے اوّلی اجزا تے سانجھے مضاعفاں والا پورا سیکشن تے اوہدے نال اہم خیالاں دی دہرائی ترجمہ کیتی گئی اے؛ پورا سبق یا پوری کتاب نہیں۔')
    report('main_source_label_exact', main[0].tag == 'p' and main[0].attrib == {'class':'source-label','data-origin':'renderer-ui'} and inner(main[0]) == inner(fragment(source_label)))
    report('main_required_next_status_exact', main[-1].tag == 'p' and main[-1].attrib == {'class':'status','data-origin':'renderer-ui'} and not len(main[-1]) and main[-1].text == 'اگلا ضروری کم ایس سبق دیاں مشقاں دا ماخذی حصہ اے؛ اوہ ایتھے شامل نہیں۔ پنجاں مقررہ کتاباں دا پورا کم ہن وی جاری اے۔')
    report('footer_closed_English_frame', footer.attrib == {'id':'credits','lang':'en','dir':'ltr'} and [n.tag for n in footer] == ['h2']+['p']*7 and blank_frame(footer))
    report('footer_unit_title', not len(footer[0]) and footer[0].text == 'Sources, credits and changes — A10-004')
    bridge_ids = {n.get('id') for n in bridge.iter() if n.get('id')}
    report('all_correction_destinations_in_original_bridge', all(r['bridge_id'] in bridge_ids for r in translation['source_corrections']))
    report('exact_override_counts', len(translation['image_alt_overrides']) == 4 and len(translation['table_summary_overrides']) == 2)
    style = head.find('style').text
    report('natural_unmirrored_image_css', 'width:var(--source-width)' in style and 'min-width:var(--source-width)' in style and 'max-width:none' in style and not re.search(r'transform\s*:',style))
    report('unit_table_local_scroll_size', '.a10-004-reader .source-table { width:660px; min-width:660px; table-layout:fixed;' in style and '.a10-004-reader .source-table-scroll { direction:ltr; overflow-x:auto;' in style)
    hint_rules = re.findall(r'\.a10-004-reader\s+\.source-media\s+\.scroll-hint\s*\{([^{}]*)\}', style)
    report('media_hint_unit_scoped_wrap_rule_once', len(hint_rules) == 1)
    hint_properties = dict(re.findall(r'([\w-]+)\s*:\s*([^;]+)\s*;', hint_rules[0]))
    report('media_hint_RTL_normal_wrap_not_numeric_cell_nowrap', hint_properties == {'direction':'rtl','white-space':'normal','text-align':'start'})


def validate_images(doc, source, manifest, translation, report=check, digests=None):
    digests = digests or {}
    source_media = [n for n in source.iter() if local(n) == 'media']
    images = list(doc.iter('img'))
    report('exact15images_source_order', len(images) == len(source_media) == len(manifest['images']) == 15 and [n.get('id') for n in images] == [n.get('id') for n in source_media])
    corrections = correction_map(translation)
    for sm, img, spec in zip(source_media, images, manifest['images']):
        si = only([n for n in sm if local(n) == 'image'], 'one_source_image:' + sm.get('id'))
        sid, key = sm.get('id'), sm.get('id')+'/alt'
        filename = Path(si.get('src')).name
        original = ROOT / manifest['canonical_local_path']
        original = (original.parent / si.get('src')).resolve()
        target = (BASE / spec['path']).resolve()
        report('image_declared_exact_paths:' + sid, spec['source_src'] == si.get('src') == '../../media/'+filename and spec['source_path'] == 'media/'+filename and target == (BASE/'assets/a10'/filename).resolve() and original == (ROOT/spec['canonical_local_path']).resolve())
        actual_digest = digests.get(spec['path'], sha(target))
        data = original.read_bytes()
        report('image_source_target_bytes_hash:' + sid, hashlib.sha256(data).hexdigest() == actual_digest == spec['sha256'] and len(data) == target.stat().st_size == spec['bytes'])
        with Image.open(io.BytesIO(data)) as decoded:
            report('image_original_decodes_JPEG_dimensions:' + sid, decoded.format == 'JPEG' and decoded.size == (spec['width'],spec['height']))
            decoded.verify()
        with Image.open(target) as decoded:
            report('image_copied_decodes_JPEG_dimensions:' + sid, decoded.format == 'JPEG' and decoded.size == (spec['width'],spec['height']))
            decoded.verify()
        report('image_canonical_git_blob:' + sid, hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == spec['git_blob_sha1'])
        report('image_source_MIME_trace:' + sid, spec['declared_mime'] == si.get('mime-type') == img.get('data-source-image-mime') and img.get('data-rendered-image-mime') == 'image/jpeg' and spec['actual_image_format'] == 'Jpeg')
        override = translation['image_alt_overrides'].get(sid)
        described = ' '.join(dict.fromkeys(r['bridge_id'] for r in corrections.get(key,[]))) or None
        report('image_alt_source_and_original_override:' + sid, img.get('data-source-alt') == translation['source_blocks'][key] and img.get('alt') == (override or translation['source_blocks'][key]) and img.get('data-description-origin') == ('original-correction' if override else 'source-translation') and img.get('aria-describedby') == described)
        src = '../'+spec['path']
        report('image_dimensions_src:' + sid, img.get('src') == src and img.get('width') == str(spec['width']) and img.get('height') == str(spec['height']) and img.get('style') == '--source-width:'+str(spec['width'])+'px' and img.get('data-source-tag') == 'media')
        image_fields = {'id','data-source-tag','src','alt','data-source-alt','data-description-origin','data-source-image-mime','data-rendered-image-mime','width','height','style'}
        report('image_no_hidden_extra_attributes:' + sid, set(img.attrib) == image_fields | ({'aria-describedby'} if described else set()))
        wrapper = only([n for n in doc.iter() if n.get('data-source-child') == sid], 'image_wrapper:' + sid)
        report('image_wrapper_closed:' + sid, wrapper.tag == 'div' and wrapper.attrib == {'class':'source-media','data-source-child':sid} and len(wrapper) == (3 if key in corrections else 2) and blank_frame(wrapper))
        scroll, hint = wrapper[0], wrapper[1]
        report('image_scroll_region:' + sid, scroll.tag == 'div' and scroll.attrib == {'class':'figure-scroll','dir':'ltr','tabindex':'0','role':'region','aria-label':'اصل شکل؛ لوڑ پئے تے پاسے سرکاؤ'} and list(scroll) == [img] and blank_frame(scroll))
        report('image_hint_exact:' + sid, hint.tag == 'p' and hint.attrib == {'class':'scroll-hint','data-origin':'renderer-ui','dir':'rtl'} and len(hint) == 1 and hint.text == 'چھوٹی سکرین اُتے پوری شکل ویکھن لئی پاسے سرکاؤ، یا ')
        a = hint[0]
        report('image_fallback_link_exact:' + sid, a.tag == 'a' and a.attrib == {'href':src} and not len(a) and a.text == 'اصل شکل وکھری کھولو' and a.tail == '۔')
        if key in corrections:
            report('image_advisory_owner_position:' + sid, wrapper[2].get('data-source-advisory-for') == key)
    report('four_retained_PNG_declarations', sum(n.get('data-source-image-mime') == 'image/png' for n in images) == 4)
    report('image_total_bytes', sum(x['bytes'] for x in manifest['images']) == manifest['total_declared_image_bytes'] == 1015473)


def validate_notices(doc, source, manifest, report=check, record=None):
    record = record if record is not None else json.loads(NOTICES.read_text(encoding='utf-8'))
    report('notice_schema_identity', record['schema'] == 'a10-retained-component-evidence-v1' and (record['unit'],record['work'],record['module'],record['collection'],record['commit']) == ('A10-004','OpenStax Elementary Algebra 2e','m82452','col31130',manifest['commit']))
    report('notice_manifest_witness_pins', record['manifest_sha256'] == sha(MANIFEST) and record['excerpt_sha256'] == manifest['excerpt_sha256'])
    report('notice_no_new_clearance', record['rights_status'] == 'Existing audited A10 policy is retained. No new component-specific clearance determination is made.' and record['credit_limit'] == 'Media authority rows identify bytes and Git blobs, not rights holders or permissions. Absence of an image-specific credit is not clearance.')
    report('notice_license_restrictions', record['existing_license_statement'] == 'Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International, subject to component-specific credits and restrictions.')
    report('notice_existing_texts', record['existing_notice_inputs'] == manifest['existing_notice_inputs'] and record['existing_notice_hash_policy'] == manifest['existing_notice_hash_policy'])
    for entry in manifest['existing_notice_inputs']:
        report('notice_logical_LF_hash:' + entry['path'], hashlib.sha256((ROOT/entry['path']).read_bytes().replace(b'\r\n',b'\n')).hexdigest() == entry['sha256'])
    report('notice_release_verbatim', record['release_notice_verbatim'] == (BASE/'provenance/A10-release/NOTICE.txt').read_text(encoding='utf-8'))
    authority = ROOT / manifest['media_authority_manifest_path']
    report('authority_manifest_pin', sha(authority) == manifest['media_authority_manifest_sha256'] and record['media_authority_manifest'] == {'path':manifest['media_authority_manifest_path'],'sha256':sha(authority)})
    with authority.open(encoding='utf-8-sig',newline='') as handle:
        rows = list(csv.DictReader(handle))
    source_media = [n for n in source.iter() if local(n) == 'media']
    report('notice_all15_components', len(record['images']) == len(source_media) == 15)
    for item, sm, spec in zip(record['images'],source_media,manifest['images']):
        row = only([r for r in rows if r['relative_path'] == spec['source_path']], 'one_authority_row:' + spec['source_path'])
        for field in ('figure_id','media_id','source_path','path','sha256','bytes','width','height'):
            report('component_field:' + sm.get('id') + ':' + field, item[field] == spec[field])
        report('component_exact_source_description:' + sm.get('id'), item['source_english_alt'] == sm.get('alt'))
        report('component_retained_MIME:' + sm.get('id'), item['source_declared_mime'] == spec['declared_mime'] and item['actual_mime'] == 'image/jpeg')
        report('component_authority_row:' + sm.get('id'), item['existing_media_authority_row'] == row and row['sha256'] == spec['sha256'] and int(row['bytes']) == spec['bytes'] and row['git_blob_sha1'] == spec['git_blob_sha1'])
        report('component_no_clearance_claim:' + sm.get('id'), item['component_clearance'] == 'Not newly assessed; subject to retained component-specific credits and restrictions.')
    report('notice_book_incomplete', record['whole_book_translation_complete'] is False)
    footer = text(identified(doc,'credits'))
    for required in ['Lynn Marecek','MaryAnne Anthony-Smith','Andrea Honeycutt Mathis','subject to component-specific credits and restrictions','No new clearance is asserted','do not endorse this translation','names, logos and marks are not licensed','fifteen exact MathML trees','fourteen data cells including one empty cell','Section Exercises, which is required next','not a complete module','Native-language, educator and assistive-technology review remain pending']:
        report('footer_required:' + required, required in footer)
    report('no_A30_author_substitution', not any(x in footer for x in ['Jay Abramson','David Lippman','Melonie Rasmussen']))


def validate_links(doc, report=check):
    all_ids = {n.get('id') for n in doc.iter() if n.get('id')}
    references = []
    for n in doc.iter():
        for field in ('href','src'):
            if field not in n.attrib:
                continue
            value = n.get(field)
            references.append({'attribute':field,'value':value})
            parsed = urlsplit(value)
            if parsed.scheme or parsed.netloc:
                report('external_web_scheme:' + value, parsed.scheme in {'http','https'})
                continue
            if parsed.path:
                path = (READER.parent/unquote(parsed.path)).resolve()
                report('local_path_exists_scoped:' + value, path.is_relative_to(BASE.resolve()) and path.is_file())
                if parsed.fragment:
                    linked = parse_reader(path.read_text(encoding='utf-8'))
                    report('cross_reader_fragment:' + value, unquote(parsed.fragment) in {x.get('id') for x in linked.iter() if x.get('id')})
            else:
                report('local_fragment:' + value, unquote(parsed.fragment) in all_ids)
        for sid in (n.get('aria-describedby') or '').split():
            report('accessible_description_target:' + sid, sid in all_ids)
    return references


def prime(n):
    return n > 1 and all(n % d for d in range(2, math.isqrt(n)+1))


def factorization(n):
    result, d = [], 2
    while d*d <= n:
        while n % d == 0:
            result.append(d)
            n //= d
        d += 1
    return result + ([n] if n > 1 else [])


def math_factors(n):
    leaves = [(local(x),x.text or '') for x in n.iter() if local(x) in {'mn','mo'}]
    if ('mo','=') in leaves:
        leaves = leaves[leaves.index(('mo','='))+1:]
    check('product_only_prime_expression', all(k == 'mn' or v == '·' for k,v in leaves))
    return [int(v) for k,v in leaves if k == 'mn']


def rendered_prose(n):
    clone = copy.deepcopy(n)
    for m in list(clone.iter('{' + MATH + '}math')):
        p = parents(clone)
        wrapper = p[m]
        replace_child(p[wrapper],wrapper,' ')
    for ui in list(clone.iter()):
        if ui.get('data-source-advisory-for'):
            replace_child(parents(clone)[ui],ui,' ')
    return text(clone)


def validate_arithmetic(doc, source, manifest, translation, report=check):
    specs, sp = source_specs(source), parents(source)
    results = []
    ns = {'c':CNXML,'m':MATH}
    for exercise in [n for n in source.iter() if local(n) == 'exercise']:
        question = exercise.find('c:problem/c:para',ns)
        solution = exercise.find('c:solution',ns)
        qvalues = [int(x) for x in re.findall(r'\d+',source_prose(question))]
        target_question = block(doc,question.get('id'))
        report('question_source_numbers:' + question.get('id'), [int(x) for x in re.findall(r'\d+',rendered_prose(target_question))] == qvalues)
        is_try = any(local(a) == 'note' and a.get('class') == 'try' for a in ancestry(exercise,sp))
        qtext = source_prose(question).lower()
        kind = 'lcm' if 'common multiple' in qtext or 'lcm' in qtext else 'prime-factorization'
        if kind == 'prime-factorization':
            report('one_factor_question_operand:' + question.get('id'), len(qvalues) == 1)
            source_math = only(list(solution.iter('{'+MATH+'}math'))[:1], 'source_factor_result:' + question.get('id'))
            target_solution = identified(doc,solution.get('id'))
            target_math = only(list(target_solution.iter('{'+MATH+'}math'))[:1], 'target_factor_result:' + question.get('id'))
            factors = math_factors(target_math)
            report('prime_product_source_answer:' + question.get('id'), factors == math_factors(source_math) == factorization(qvalues[0]) and all(prime(x) for x in factors) and math.prod(factors) == qvalues[0])
            result = factors
        else:
            report('two_lcm_question_operands:' + question.get('id'), len(qvalues) == 2)
            calculated = math.lcm(*qvalues)
            if is_try:
                answer = solution.find('c:para',ns)
                report('try_lcm_source_answer:' + question.get('id'), text(answer).strip() == str(calculated) and text(block(doc,answer.get('id'))).strip() == str(calculated))
            else:
                found = []
                for node in solution.iter():
                    if local(node) not in {'para','entry'}:
                        continue
                    prose = source_prose(node)
                    match = re.search(r'(\d+) is the least common multiple',prose)
                    if not match:
                        match = re.search(r'The LCM of \d+ and \d+ is (\d+)',prose)
                    if match:
                        found.append((node,prose,match))
                for node, prose, match in found:
                    key = next(k for k,v in specs.items() if v is node)
                    capture_index = len(re.findall(r'\d+',prose[:match.start(1)]))
                    output_numbers = [int(x) for x in re.findall(r'\d+',rendered_prose(block(doc,key)))]
                    report('worked_lcm_source_and_target:' + key, int(match[1]) == calculated and output_numbers[capture_index] == calculated)
                if not found:
                    image_conclusions = []
                    for media in solution.iter():
                        if local(media) == 'media':
                            match = re.search(r'LCM equals (\d+)',media.get('alt',''))
                            if match:
                                image_conclusions.append((media,match))
                    media, match = only(image_conclusions,'source_image_lcm_conclusion:' + question.get('id'))
                    target_alt = identified(doc,media.get('id')).get('alt')
                    displayed = re.search(r'LCM برابر (\d+)',target_alt)
                    report('worked_image_lcm_source_and_target:' + media.get('id'), int(match[1]) == calculated and displayed is not None and int(displayed[1]) == calculated)
            result = calculated
        results.append({'question_id':question.get('id'),'exercise_id':exercise.get('id'),'try_it':is_try,'kind':kind,'source_operands':qvalues,'recomputed_result':result})
    report('all15exercise_answers_computed', len(results) == 15 and sum(r['try_it'] for r in results) == 10)

    # Derive the classification data from the actual source figure description,
    # then recompute divisors and primality; no separately invented answer fixture.
    figure = only([n for n in source.iter() if local(n) == 'figure'], 'one_classification_figure')
    media = only([n for n in figure.iter() if local(n) == 'media'], 'one_classification_media')
    source_rows = re.findall(r'“(\d+)”\s*,\s*“([\d,]+)”\s*,?\s*(?:and\s*)“(Prime|Composite)”',media.get('alt'))
    target_alt = identified(doc,media.get('id')).get('alt')
    target_rows = re.findall(r'«(\d+)»\s*،\s*«([\d،\s]+)»\s*تے\s*«(اوّلی|مرکب)»',target_alt)
    report('classification_rows_all18', len(source_rows) == len(target_rows) == 18)
    for (number,divisors,label),(tn,td,tl) in zip(source_rows,target_rows):
        n = int(number)
        expected_divisors = [d for d in range(1,n+1) if n % d == 0]
        report('classification_factor_list:' + number, int(tn) == n and list(map(int,divisors.split(','))) == expected_divisors == [int(x) for x in re.findall(r'\d+',td)])
        report('classification_prime_or_composite:' + number, label == ('Prime' if prime(n) else 'Composite') and tl == ('اوّلی' if prime(n) else 'مرکب'))
    report('classification_data_order', [int(r[0]) for r in source_rows] == list(range(2,20)))
    report('ten_rows_corrected_not_source_eleven', 'دس سطراں' in target_alt and 'گیارہ سطراں' in translation['source_blocks'][media.get('id')+'/alt'] and 'ساڈی درست کیتی وضاحت' in target_alt)

    paragraph = identified(source,'fs-id1170655223714')
    number = int(re.findall(r'\d+',source_prose(paragraph))[0])
    positive = [d for d in range(1,number+1) if number%d == 0]
    bridge = identified(doc,'a10-004-original-bridge')
    report('missing_factor24_original_correction', any([int(x) for x in re.findall(r'\d+',text(n))] == positive for n in bridge.iter('bdi')) and 24 not in [int(x) for x in re.findall(r'\d+',source_prose(paragraph))])
    report('one_neither_prime_nor_composite', not prime(1) and len(factorization(1)) == 0 and 'نہ اوّلی اے، نہ مرکب' in text(identified(doc,'a10-004-composite-one')))

    table = identified(source,'fs-id1167826967413')
    conclusion = [n for n in table.iter() if local(n) == 'entry'][-1]
    operands = [int(x) for x in re.findall(r'\d+',text(conclusion))][:2]
    counts = Counter(factorization(operands[0])) | Counter(factorization(operands[1]))
    factors = sorted(counts.elements())
    report('five_column_LCM_multiplicity', len(factors) == 5 and math.prod(factors) == math.lcm(*operands))
    target_summary = identified(doc,table.get('id')).get('aria-label')
    expected_third = f'تیجا تیر {operands[0]} دی صورت دے تیجے {factors[2]} توں شروع ہوندا اے تے {operands[1]} دی صورت وچلی خالی تھاں وچوں لنگھ کے LCM دے تیجے {factors[2]} اُتے مُکدا اے۔'
    report('corrected_third_arrow_binding', expected_third in target_summary and 'تیجا تیر 12 دی صورت' in translation['source_blocks'][table.get('id')+'/summary'])
    summary252 = identified(doc,'fs-id1167834252648').get('aria-label')
    report('corrected_prime_tree_stop_rule', 'آخر وچ بچے سارے ضربی اجزا اوّلی عدد' in summary252 and 'سارے اوّلی عدداں دے اجزا' in translation['source_blocks']['fs-id1167834252648/summary'])

    # The review correction links the previous canonical worked table. Recompute
    # that table's stated result from its own numeric conclusion.
    canonical = E.parse(ROOT/manifest['canonical_local_path']).getroot()
    prior = identified(canonical,'fs-id1167832055010')
    final = [n for n in prior.iter() if local(n) == 'entry'][-1]
    match = re.fullmatch(r'So, ([\d,]+) is ([\d,]+) rounded to the nearest hundred\.',text(final))
    report('source_review_carry_statement', match is not None)
    rounded, original = [int(x.replace(',','')) for x in match.groups()]
    first_cell = [n for n in prior.iter() if local(n) == 'entry'][0]
    report('source_review_carry_computation', int(re.search(r'\d+(?:,\d{3})*',text(first_cell))[0].replace(',','')) == original and ((original+50)//100)*100 == rounded)
    heading = identified(doc,'a10-004-review-carry')
    paragraph = bridge[list(bridge).index(heading)+1]
    displayed = [text(n) for n in paragraph.iter('bdi')]
    report('original_review_carry_display', format(original,',') in displayed and format(rounded,',') in displayed and str(original//1000%10) in displayed and str(rounded//1000%10) in displayed)
    return results


def validate_canon(manifest, report=check):
    """Verify existing receipt/locus identity; never manufacture reading evidence."""
    contract = manifest['canon_consultations']
    index_path, script_path = BASE/'canon/examples.json', BASE/'scripts/read_canon.py'
    for name, path in [('index',index_path),('script',script_path)]:
        report('canon_' + name + '_pin', sha(path) == contract[name]['sha256'] and path.stat().st_size == contract[name]['bytes'])
    index = json.loads(index_path.read_text(encoding='utf-8'))
    examples = {r['id']:r for r in index['examples']}
    sources = {r['id']:r for r in index['sources']}
    records = []
    for item in contract['receipts']:
        path = BASE/item['path']
        report('canon_stage_receipt_hash:' + item['stage'], sha(path) == item['sha256'])
        receipt = json.loads(path.read_text(encoding='utf-8'))
        report('canon_stage_receipt_identity:' + item['stage'], receipt['unit'] == 'A10-004' and receipt['stage'] == item['stage'] and [e['id'] for e in receipt['examples']] == contract['example_ids'])
        for locus in receipt['examples']:
            example = examples[locus['id']]
            source = sources[example['source']]
            html_path = ROOT/'downloads/canon/pnb-Arab-PK'/(source['id']+'.html')
            txt_path = html_path.with_suffix('.txt')
            candidates = [line for line in txt_path.read_text(encoding='utf-8').splitlines() if example['quote'] in line]
            report('canon_readable_locus:' + item['stage'] + ':' + locus['id'], bool(candidates) and bool(re.search('[\u0600-\u06ff]',candidates[0])))
            report('canon_actual_source_and_paragraph:' + item['stage'] + ':' + locus['id'], sha(html_path) == locus['source_sha256'] and hashlib.sha256(candidates[0].encode()).hexdigest() == locus['paragraph_sha256'] and source['url'] == locus['source_url'])
        records.append({'stage':item['stage'],'path':item['path'],'sha256':sha(path),'example_ids':[e['id'] for e in receipt['examples']]})
    report('canon_four_actual_stages', {r['stage'] for r in records} == {'next-unit','draft','revision','qa'})
    return records


def mutations(doc, source, manifest, translation):
    """Mutate detached trees/arguments only; a validator assertion must reject each."""
    rejected = []

    def full(d):
        validate_dom(d,source,manifest,translation)
        validate_images(d,source,manifest,translation)
        validate_arithmetic(d,source,manifest,translation)
        validate_links(d)

    def reject(name, mutate, validator=full):
        changed = copy.deepcopy(doc)
        mutate(changed)
        check('mutation_really_changes_tree:' + name, signature(changed) != signature(doc))
        try:
            validator(changed)
        except AssertionError as error:
            rejected.append({'name':name,'rejected_by':str(error),'mode':'detached DOM'})
        else:
            raise AssertionError('mutation_not_rejected:' + name)

    def remove(n, d):
        parents(d)[n].remove(n)

    def append_prose(n):
        p = E.SubElement(n,'p')
        bdi = E.SubElement(p,'bdi',{'dir':'ltr'})
        bdi.text = '72 = 999'

    specs, sp = source_specs(source), parents(source)
    section_id = source[0].get('id')
    first_para = next(n for n in source[0] if local(n) == 'para').get('id')
    first_term = next(n.get('id') for n in source.iter() if local(n) == 'term')
    variable_key = next(key for key,n in specs.items() if local(n) == 'para' and any(local(e) == 'emphasis' and e.get('effect') == 'italics' and re.fullmatch('[a-z]',text(e)) for e in n.iter()))
    nested_list = next(n for n in source.iter() if local(n) == 'list' and local(sp[n]) == 'item')
    enumerated = next(n.get('id') for n in source.iter() if local(n) == 'list' and n.get('list-type') == 'enumerated')
    circle = next(n.get('id') for n in source.iter() if local(n) == 'list' and n.get('bullet-style') == 'open-circle')
    resource_list = next(n.get('id') for n in source.iter() if local(n) == 'list' and not n.get('list-type'))
    blank_key = next(key for key,n in specs.items() if local(n) == 'entry' and not len(n) and not (n.text or '').strip())
    first_table = next(n.get('id') for n in source.iter() if local(n) == 'table')
    newline_key = next(key for key,n in specs.items() if any(local(c) == 'newline' for c in n))
    direct_note = next(key for key,n in specs.items() if local(n) == 'note')
    explicit_solution = next(n.get('id') for n in source.iter() if local(n) == 'solution' and any(local(c) == 'title' for c in n))
    images = [n.get('id') for n in source.iter() if local(n) == 'media']
    alt_override = next(iter(translation['image_alt_overrides']))
    summary_override = next(iter(translation['table_summary_overrides']))
    corrections = correction_map(translation)
    corrected_para = next(key for key in corrections if local(specs[key]) == 'para')
    source_ref = next(r for r in manifest['references'] if r['kind'] == 'external')
    cross_ref = next(r for r in manifest['references'] if r['href'].startswith('a10-unit-001'))

    reject('source_paragraph_deleted',lambda d: remove(identified(d,first_para),d))
    def swap_children(d):
        section = identified(d,section_id)
        section[1],section[2] = section[2],section[1]
    reject('source_sibling_order_swapped',swap_children)
    reject('source_container_anonymous_text',lambda d: setattr(identified(d,section_id),'text','غلط'))
    reject('source_container_whitespace_dropped',lambda d: setattr(identified(d,section_id),'text',None))
    reject('source_container_unkeyed_paragraph',lambda d: append_prose(identified(d,section_id)))
    reject('source_paragraph_hidden',lambda d: identified(d,first_para).set('style','display:none'))
    reject('source_paragraph_extra_tail',lambda d: setattr(identified(d,first_para)[0],'tail',' غلط'))
    reject('source_term_id_changed',lambda d: identified(d,first_term).set('id','wrong-term'))
    reject('italic_variable_changed',lambda d: setattr(block(d,variable_key).find('em/bdi'),'text','z'))
    reject('source_math_number_changed',lambda d: setattr(next(d.iter('{'+MATH+'}mn')),'text','999'))
    reject('source_math_variable_changed',lambda d: setattr(next(d.iter('{'+MATH+'}mi')),'text','z'))
    reject('source_math_English_and_changed',lambda d: setattr(next(n for n in d.iter('{'+MATH+'}mtext') if (n.text or '').strip() == 'and'),'text','dan'))
    reject('source_math_terminal_period_removed',lambda d: remove(next(n for n in d.iter('{'+MATH+'}mo') if n.text == '.'),d))
    reject('source_math_direction_RTL',lambda d: next(d.iter('{'+MATH+'}math')).set('dir','rtl'))
    reject('unapproved_source_math_edit_ledger',lambda d: next(d.iter('{'+MATH+'}math')).set('data-source-text-edits','[]'))

    def move_nested(d):
        nested = identified(d,nested_list.get('id'))
        remove(nested,d)
        identified(d,section_id).append(nested)
    reject('nested_list_moved_out_of_owning_item',move_nested)
    reject('enumerated_list_changed_to_bulleted',lambda d: setattr(identified(d,enumerated),'tag','ul'))
    reject('open_circle_bullet_trace_changed',lambda d: identified(d,circle).set('data-source-bullet-style','bullet'))
    reject('resource_list_display_changed',lambda d: identified(d,resource_list).set('data-source-display','inline'))
    reject('list_extra_item',lambda d: E.SubElement(identified(d,enumerated),'li'))
    reject('source_blank_cell_filled',lambda d: setattr(block(d,blank_key),'text','1'))
    reject('source_blank_cell_removed',lambda d: remove(block(d,blank_key),d))
    reject('source_data_cell_changed_to_header',lambda d: setattr(identified(d,first_table).find('tbody')[0][0],'tag','th'))
    reject('source_empty_table_label_metadata_removed',lambda d: identified(d,first_table).attrib.pop('data-source-label-empty'))
    reject('source_table_cell_tail_injected',lambda d: setattr(identified(d,first_table).find('tbody')[0][0],'tail',' غلط'))
    reject('source_newline_removed',lambda d: remove(block(d,newline_key).find('br'),d))
    reject('direct_text_note_missing',lambda d: setattr(block(d,direct_note),'text',None))
    reject('explicit_solution_title_duplicated',lambda d: identified(d,explicit_solution).insert(0,copy.deepcopy(identified(d,explicit_solution).find('h3'))))
    reject('image_asset_swapped',lambda d: identified(d,images[0]).set('src',identified(d,images[1]).get('src')))
    reject('image_width_changed',lambda d: identified(d,images[0]).set('width','999'))
    reject('image_source_MIME_trace_changed',lambda d: identified(d,images[0]).set('data-source-image-mime','image/png'))
    reject('image_source_alt_trace_changed',lambda d: identified(d,alt_override).set('data-source-alt','غلط'))
    reject('known_wrong_source_alt_announced_first',lambda d: identified(d,alt_override).set('alt',translation['source_blocks'][alt_override+'/alt']))
    reject('corrected_image_hidden_from_AT',lambda d: identified(d,alt_override).set('aria-hidden','true'))
    reject('source_summary_trace_changed',lambda d: identified(d,summary_override).set('data-source-summary','غلط'))
    reject('known_wrong_source_summary_announced_first',lambda d: identified(d,summary_override).set('aria-label',translation['source_blocks'][summary_override+'/summary']))
    reject('correction_accessible_target_removed',lambda d: identified(d,alt_override).attrib.pop('aria-describedby'))
    def advisory_retargeted(d):
        advice = next(n for n in d.iter() if n.get('data-source-advisory-for'))
        current = advice[0].get('href')
        other = next('#'+r['bridge_id'] for r in translation['source_corrections'] if '#'+r['bridge_id'] != current)
        advice[0].set('href',other)
    reject('advisory_valid_but_wrong_destination',advisory_retargeted)
    reject('source_external_reference_changed',lambda d: next(n for n in d.iter('a') if n.get('data-source-link-owner') == source_ref['source_key']).set('href','https://example.org/'))
    reject('source_cross_unit_reference_changed',lambda d: next(n for n in d.iter('a') if n.get('data-source-link-owner') == cross_ref['source_key']).set('href','#'+section_id))
    reject('correctly_LTR_isolated_main_prose_injected',lambda d: append_prose(d.find('body/main')))
    reject('body_unkeyed_paragraph_injected',lambda d: append_prose(d.find('body')))
    reject('main_anonymous_tail_injected',lambda d: setattr(d.find('body/main')[1],'tail',' غلط'))
    reject('source_paragraph_wrapper_UI_injected',lambda d: append_prose(next(n for n in d.iter() if n.get('data-source-block-owner') == corrected_para)))
    reject('source_table_wrapper_UI_injected',lambda d: append_prose(next(n for n in d.iter() if n.get('data-source-child') == first_table)))
    reject('source_media_wrapper_UI_injected',lambda d: append_prose(next(n for n in d.iter() if n.get('data-source-child') == images[0])))
    reject('original_bridge_anonymous_prose_injected',lambda d: append_prose(identified(d,'a10-004-original-bridge')))
    reject('prohibited_bidi_control_in_source_prose',lambda d: setattr(identified(d,first_para),'text','\u202e'))
    reject('Gurmukhi_substitution_in_source_prose',lambda d: setattr(identified(d,first_para),'text','\u0a2a'))

    def media_hint(d):
        return next(n for n in d.iter() if n.get('data-source-child') == images[-2])[1]
    reject('media_hint_explicit_RTL_removed',lambda d: media_hint(d).attrib.pop('dir'))
    reject('media_hint_direction_changed_to_LTR',lambda d: media_hint(d).set('dir','ltr'))
    def nowrap_hint(d):
        style = d.find('head/style')
        before = '.a10-004-reader .source-media .scroll-hint { direction:rtl; white-space:normal; text-align:start; }'
        check('mutation_hint_rule_present', before in style.text)
        style.text = style.text.replace(before,before.replace('white-space:normal','white-space:nowrap'))
    reject('media_hint_inherits_or_forces_nowrap_regression',nowrap_hint)
    reject('media_hint_anonymous_extra_word',lambda d: setattr(media_hint(d),'text',media_hint(d).text+'غلط '))

    # Arithmetic-specific tests bypass prose-byte equality: the validator must
    # independently derive the mathematical answer from the actual source.
    answers = validate_arithmetic(doc,source,manifest,translation)
    prime_try = next(a for a in answers if a['try_it'] and a['kind'] == 'prime-factorization')
    lcm_try = next(a for a in answers if a['try_it'] and a['kind'] == 'lcm')
    arithmetic = lambda d: validate_arithmetic(d,source,manifest,translation)
    reject('source_question_operand_arithmetic_binding',lambda d: setattr(block(d,prime_try['question_id']).find('bdi'),'text',str(prime_try['source_operands'][0]+1)),arithmetic)
    def bad_prime_factor(d):
        exercise = identified(d,prime_try['exercise_id'])
        mn = next(exercise.iter('{'+MATH+'}mn'))
        mn.text = str(int(mn.text)+1)
    reject('TryIt_prime_factor_product_recomputed',bad_prime_factor,arithmetic)
    def bad_lcm(d):
        ex = identified(source,lcm_try['exercise_id'])
        solution = next(n for n in ex if local(n) == 'solution')
        para = next(n for n in solution if local(n) == 'para')
        block(d,para.get('id')).find('bdi').text = str(lcm_try['recomputed_result']+1)
    reject('TryIt_LCM_answer_recomputed',bad_lcm,arithmetic)
    def bad_classification(d):
        target = identified(d,alt_override)
        target.set('alt',target.get('alt').replace('«اوّلی»','«مرکب»',1))
    reject('classification_prime_label_recomputed',bad_classification,arithmetic)
    def wrong_arrow(d):
        table = identified(d,'fs-id1167826967413')
        table.set('aria-label',table.get('aria-label').replace('تیجا تیر 24','تیجا تیر 12'))
    reject('LCM_third_arrow_actual_operands_binding',wrong_arrow,arithmetic)
    def missing_factor(d):
        bridge = identified(d,'a10-004-original-bridge')
        source_values = [int(v) for v in re.findall(r'\d+',source_prose(identified(source,'fs-id1170655223714')))]
        full = [v for v in range(1,source_values[0]+1) if source_values[0] % v == 0]
        omitted = only(sorted(set(full)-set(source_values)),'one_source_omitted_factor')
        n = next(n for n in bridge.iter('bdi') if [int(v) for v in re.findall(r'\d+',text(n))] == full)
        n.text = re.sub(r'(?<!\d)'+str(omitted)+r'(?!\d)',str(omitted+1),n.text,count=1)
    reject('original_missing24_factor_correction_recomputed',missing_factor,arithmetic)

    try:
        validate_images(doc,source,manifest,translation,digests={manifest['images'][0]['path']:'0'*64})
    except AssertionError as error:
        rejected.append({'name':'image_digest_argument_corrupted_no_asset_write','rejected_by':str(error),'mode':'detached digest argument'})
    else:
        raise AssertionError('image_digest_mutation_not_rejected')
    for name, mutate in [
        ('component_notice_hash_corrupted',lambda r: r['images'][0].update({'sha256':'0'*64})),
        ('component_notice_invents_clearance',lambda r: r.update({'rights_status':'All image rights cleared'}))
    ]:
        original = json.loads(NOTICES.read_text(encoding='utf-8'))
        changed = copy.deepcopy(original)
        mutate(changed)
        check('notice_mutation_really_changes_record:' + name, changed != original)
        try:
            validate_notices(doc,source,manifest,record=changed)
        except AssertionError as error:
            rejected.append({'name':name,'rejected_by':str(error),'mode':'detached notice record'})
        else:
            raise AssertionError('notice_mutation_not_rejected:' + name)
    return rejected


def main():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    translation = json.loads(TRANSLATION.read_text(encoding='utf-8'))
    excerpt = BASE/'source-excerpts/a10-unit-004.cnxml'
    source = E.parse(excerpt).getroot()
    inputs = [
        MANIFEST, TRANSLATION, excerpt, BASE/'plans/A10-004-scope.json',
        BASE/'qa/a10-unit-004-language-notes.md',
        BASE/'scripts/prepare_a10_004.py', BASE/'scripts/build_a10_004.py', Path(__file__),
        BASE/'scripts/prepare_a10.py', BASE/'scripts/build_a10.py', BASE/'styles/reader.css',
        BASE/'sources.lock.json', ROOT/manifest['canonical_local_path'],
        ROOT/manifest['indonesian_comparison_path'], ROOT/manifest['media_authority_manifest_path'],
        BASE/'canon/examples.json', BASE/'scripts/read_canon.py'
    ]
    inputs += [ROOT/entry['path'] for entry in manifest['existing_notice_inputs']]
    inputs += [ROOT/entry['canonical_local_path'] for entry in manifest['images']]
    inputs += sorted((BASE/'canon/receipts').glob('A10-004-*.json'))
    for rid in ('R1','R2','R3'):
        inputs += [ROOT/'downloads/canon/pnb-Arab-PK'/(rid+suffix) for suffix in ('.html','.txt')]
    # Only actual cross-unit/navigation dependencies are included, not every reader.
    inputs += [BASE/'reader'/name for name in ('a10-unit-001.html','a10-unit-002.html','a10-unit-003.html')]
    inputs = list(dict.fromkeys(inputs))
    initial = {p.relative_to(ROOT).as_posix():sha(p) for p in inputs}
    outputs = [READER,NOTICES]+[BASE/entry['path'] for entry in manifest['images']]
    cycles = []
    for _ in range(2):
        for script in ('prepare_a10_004.py','build_a10_004.py'):
            subprocess.run([sys.executable,'-X','utf8',str(BASE/'scripts'/script)],
                           cwd=ROOT,check=True,capture_output=True,encoding='utf-8')
        cycles.append({p.relative_to(ROOT).as_posix():sha(p) for p in outputs})
    check('two_prepare_build_cycles_deterministic',cycles[0] == cycles[1])
    raw = READER.read_text(encoding='utf-8')
    doc = parse_reader(raw)
    passed = []
    def report(name, condition):
        check(name,condition)
        passed.append(name)
    report('reader_no_unresolved_placeholders',not re.search(r'\{\{[^}]+\}\}',raw))
    report('reader_no_Gurmukhi_or_prohibited_controls',not FORBIDDEN.search(raw))
    counts = validate_source(source,manifest,translation,report)
    validate_dom(doc,source,manifest,translation,report)
    validate_images(doc,source,manifest,translation,report)
    validate_notices(doc,source,manifest,report)
    references = validate_links(doc,report)
    arithmetic = validate_arithmetic(doc,source,manifest,translation,report)
    canon = validate_canon(manifest,report)
    negative = mutations(doc,source,manifest,translation)
    report('all_detached_mutations_rejected',bool(negative) and len({r['name'] for r in negative}) == len(negative))
    report('two_prepare_build_cycles_deterministic',cycles[0] == cycles[1])
    report('detached_mutations_did_not_change_outputs',cycles[1] == {p.relative_to(ROOT).as_posix():sha(p) for p in outputs})
    report('stable_input_hashes',initial == {p.relative_to(ROOT).as_posix():sha(p) for p in inputs})
    artifacts = list(dict.fromkeys(inputs+outputs))
    record = {
        'schema':'source-bound-reader-qa-v1',
        'unit':'A10-004','locale':'pnb-Arab-PK','status':'passed',
        'scope':{
            'module':manifest['module'],'selection_ids':manifest['selection_ids'],
            'top_level_content_children_zero_based':[5,6],
            'last_descendant_id':manifest['last_descendant_id'],
            'next_required_section':manifest['next_source_id'],
            'next_required_section_title':manifest['next_source_title'],
            'whole_module_complete':False,'whole_book_complete':False,'whole_assignment_complete':False
        },
        'checks_passed':len(passed),'checks':passed,
        'source_derived_counts':counts,
        'source_ids_in_document_order':manifest['source_ids_in_document_order'],
        'detached_mutations_rejected':negative,
        'deterministic_prepare_build_cycles':cycles,
        'reader_sha256':sha(READER),'component_notices_sha256':sha(NOTICES),
        'artifacts':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in artifacts],
        'artifact_hash_policy':'Exact current file bytes. Only retained notice semantic pins normalize CRLF to LF; raw notice artifact hashes remain explicitly distinct.',
        'source_derived_arithmetic':arithmetic,
        'original_image_inventory':[{'media_id':r['media_id'],'path':r['path'],'sha256':r['sha256'],'bytes':r['bytes'],'width':r['width'],'height':r['height'],'declared_mime':r['declared_mime'],'actual_mime':'image/jpeg'} for r in manifest['images']],
        'source_references':manifest['references'],'rendered_references':references,
        'canon_stage_receipt_validation':canon,
        'mathml_policy':'All fifteen source trees compare exactly after removing the sole presentation root dir=ltr attribute. No punctuation, token, node or text edit ledger is allowed.',
        'layout_guard':'Source-media Punjabi UI hints require explicit dir=rtl plus unit-scoped direction:rtl and white-space:normal; source tables/numeric cells/images retain LTR geometry. Real mobile dimensions are checked separately by the parent browser review.',
        'limitations':[
            'This independently CNXML-derived verifier imports neither the renderer nor its expected DOM. Passed repeated assertions are not a linguistic quality score.',
            'Shahmukhi source translation and new factor/prime/composite vocabulary remain provisional: native-speaker, educator and assistive-technology review are pending.',
            'The actual readable English/Indonesian and canon consultations are documented in language notes; receipt hashes validate identity, not the act or quality of human reading.',
            'Original image pixels were manually inspected during source/draft/revision/QA work; this script validates bytes, decoded format/dimensions and source relationships, not OCR or all visual text.',
            'Browser/mobile review is separate. The explicit hint wrapping/direction regression guard does not certify every viewport, font or assistive technology.',
            'The source missing24, composite>1 omission, factor-tree wording, method label, erroneous alts/summaries and review carry statement remain traceable; separately labeled original corrections and qualifications are not silent source repairs.',
            'LCM checks use the least positive common multiple of the positive source operands and retain prime multiplicities. No universal signed/zero convention or terminology certification is claimed.',
            'The historical source Java URL and wording remain preserved with an original warning; its present operation was not established and no external runtime was executed.',
            'Existing A10 notice/component restrictions are retained, not re-audited; absence of an image credit is not new rights clearance.',
            'The required Section Exercises begin next at fs-id1170655190123. This checkpoint does not complete m82452, A10 or the five-work assignment.'
        ]
    }
    RECEIPT.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f"A10-004 QA passed: {len(passed)} checks, {len(negative)} detached mutations; reader {sha(READER)}")


if __name__ == '__main__':
    main()
