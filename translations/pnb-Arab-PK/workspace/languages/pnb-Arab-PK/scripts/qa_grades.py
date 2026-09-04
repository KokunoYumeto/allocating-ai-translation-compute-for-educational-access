"""Source-bound PNB-003 checks; mutations use detached DOMs, never source files.

The grade computation is explicitly conditional on this example's implicit
whole-percent domain. It does not certify a universal GPA or ranking policy.
"""
from pathlib import Path
from decimal import Decimal
from urllib.parse import unquote, urlsplit
import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET


BASE = Path(__file__).resolve().parents[1]
READER = BASE / 'reader/unit-003.html'
MANIFEST = BASE / 'source-excerpts/manifest-003.json'
TRANSLATION = BASE / 'translations/unit-003.json'
GRADE_TABLE = 'Table_01_01_01'
BASEBALL_TABLE = 'Table_01_01_02'
FORBIDDEN = re.compile(r'[\u0a00-\u0a7f\ufffd\u061c\u200e\u200f\u202a-\u202e\u2066-\u2069]')


def tag(node):
    return node.tag.rsplit('}', 1)[-1]


def text(node):
    return ''.join(node.itertext()).strip()


def require(name, condition):
    if not condition:
        raise AssertionError(name)


def element(document, identifier):
    found = [node for node in document.iter() if node.get('id') == identifier]
    require(f'exactly_one_element:{identifier}', len(found) == 1)
    return found[0]


def sha256(path):
    data = path.read_bytes()
    if path.suffix.lower() == ".cnxml":
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def parse_reader(data):
    return ET.fromstring(data[data.index('<html'):])


def parent_map(document):
    return {child: parent for parent in document.iter() for child in parent}


def rows(table):
    return [node for node in table.iter() if tag(node) in ('row', 'tr')]


def source_block_specs(source):
    """Derive keys from actual text-bearing nodes, not from the JSON key list."""
    parents = parent_map(source)
    specs = {}
    for node in source.iter():
        name = tag(node)
        if name in ('title', 'label', 'para', 'footnote', 'item'):
            if name == 'item':
                items = [child for child in parents[node] if tag(child) == 'item']
                key = f"{parents[node].get('id')}/item/{items.index(node) + 1}"
            else:
                key = node.get('id') or f"{parents[node].get('id')}/{name}"
            specs[key] = (name, node, None)
        if name != 'table':
            continue
        table_id = node.get('id')
        specs[table_id + '/summary'] = ('summary', node, None)
        for row_index, row in enumerate(rows(node), 1):
            for entry_index, entry in enumerate(row, 1):
                is_header = tag(parents[row]) == 'thead' or any(tag(child) == 'emphasis' for child in entry)
                if is_header:
                    key = f'{table_id}/row/{row_index}/entry/{entry_index}'
                    specs[key] = ('entry', entry, (table_id, row_index, entry_index))
    return specs


def target_for_block(document, source, spec):
    name, node, location = spec
    if name == 'footnote':
        return element(document, node.get('id') + '-text')
    if name == 'entry':
        table_id, row_index, entry_index = location
        return rows(element(document, table_id))[row_index - 1][entry_index - 1]
    if node.get('id'):
        return element(document, node.get('id'))
    parent = parent_map(source)[node]
    if name == 'item':
        items = [child for child in parent if tag(child) == 'item']
        return element(document, parent.get('id')).findall('li')[items.index(node)]
    headings = [child for child in element(document, parent.get('id')) if child.tag in ('h2', 'h3')]
    require(f'one_translated_heading:{parent.get("id")}/{name}', len(headings) == 1)
    return headings[0]


def text_without_ids(node, excluded, excluded_hrefs=()):
    value = node.text or ''
    for child in node:
        if child.get('id') not in excluded and child.get('href') not in excluded_hrefs:
            value += text_without_ids(child, excluded, excluded_hrefs)
        value += child.tail or ''
    return value


def validate_blocks(document, source, translation, manifest, check=require):
    specs = source_block_specs(source)
    blocks = translation['source_blocks']
    check('all_17_source_block_keys_exact', len(specs) == len(blocks) == 17 and set(specs) == set(blocks))
    reference_labels = {entry['id']: entry['local_label'] for entry in manifest['references']}
    for key, spec in specs.items():
        name, original, _ = spec
        rendered = target_for_block(document, source, spec)
        if name == 'summary':
            check(f'source_summary_translation_used:{key}', rendered.get('data-source-summary') == blocks[key])
            continue
        value = blocks[key]
        links = [node for node in original if tag(node) == 'link']
        children = [node for node in original if tag(node) == 'footnote']
        link_positions = [int(index) for index in re.findall(r'\{\{link:(\d+)\}\}', value)]
        child_positions = [int(index) for index in re.findall(r'\{\{child:(\d+)\}\}', value)]
        require(f'block_link_placeholder_order:{key}', link_positions == list(range(len(links))))
        require(f'block_child_placeholder_order:{key}', child_positions == list(range(len(children))))
        value = re.sub(r'\{\{link:(\d+)\}\}', lambda match:
                       'جدول ' + reference_labels[links[int(match[1])].get('target-id')], value)
        value = re.sub(r'\{\{child:(\d+)\}\}', '', value)
        expected_text = text(ET.fromstring('<root>' + value + '</root>'))
        backlinks = {'#' + original.get('id')} if name == 'footnote' else set()
        actual_text = text_without_ids(rendered, {node.get('id') for node in children}, backlinks).strip()
        check(f'source_block_translation_used:{key}', actual_text == expected_text)
    return list(specs)


def validate_structure(document, source, check=require):
    target_ids = [node.get('id') for node in document.iter() if node.get('id')]
    source_nodes = [node for node in source.iter() if node is not source and node.get('id')]
    source_ids = [node.get('id') for node in source_nodes]
    source_id_set = set(source_ids)
    check('unique_html_ids', len(target_ids) == len(set(target_ids)))
    check('all_source_ids_retained_in_document_order',
          [identifier for identifier in target_ids if identifier in source_id_set] == source_ids)
    check('excerpt_wrapper_not_rendered', source.get('id') not in target_ids)
    source_parents, target_parents = parent_map(source), parent_map(document)

    def identified_ancestors(node, parents):
        ancestors = []
        while node in parents:
            node = parents[node]
            if node.get('id') in source_id_set:
                ancestors.append(node.get('id'))
        return ancestors

    check('all_source_id_ancestor_chains_preserved', all(
        identified_ancestors(node, source_parents) ==
        identified_ancestors(element(document, node.get('id')), target_parents)
        for node in source_nodes
    ))
    parts = []
    for source_list in (node for node in source.iter() if tag(node) == 'list'):
        identifier = source_list.get('id')
        rendered = element(document, identifier)
        original_items = [node for node in source_list if tag(node) == 'item']
        target_items = rendered.findall('li')
        check(f'source_part_count_and_list_semantics:{identifier}',
              len(original_items) == len(target_items) == 2 and rendered.tag == 'ol' and rendered.get('role') == 'list')
        for index, (original, target) in enumerate(zip(original_items, target_items), 1):
            token = next(node for node in original if tag(node) == 'span' and node.get('class') == 'token')
            label = '(' + unicodedata.normalize('NFKC', text(token)) + ')'
            key = f'{identifier}/item/{index}'
            check(f'source_part_label_first_ltr:{key}', len(target) > 0 and target[0].tag == 'bdi'
                  and target[0].get('dir') == 'ltr' and text(target[0]) == label and not (target.text or '').strip())
            parts.append({'source_key': key, 'label': label})
    return source_ids, parts


def validate_tables(document, source, translation, check=require):
    tables = [node for node in source.iter() if tag(node) == 'table']
    check('two_source_tables_in_order', [node.get('id') for node in tables] == [GRADE_TABLE, BASEBALL_TABLE])
    check('two_rendered_source_tables_in_order', [node.get('id') for node in document.iter('table')
          if 'source-table' in node.get('class', '').split()] == [GRADE_TABLE, BASEBALL_TABLE])
    source_parents, target_parents = parent_map(source), parent_map(document)
    specs = source_block_specs(source)
    observed = []
    for original in tables:
        identifier = original.get('id')
        target = element(document, identifier)
        original_rows, target_rows = rows(original), rows(target)
        expected_shape = (2, 9) if identifier == GRADE_TABLE else (6, 2)
        check(f'actual_source_table_shape:{identifier}',
              (len(original_rows), len(original_rows[0])) == expected_shape
              and all(len(row) == expected_shape[1] for row in original_rows))
        check(f'rendered_source_table_shape:{identifier}',
              len(target_rows) == expected_shape[0] and all(len(row) == expected_shape[1] for row in target_rows))
        check(f'table_orientation_ltr:{identifier}', target.tag == 'table' and target.get('dir') == 'ltr')
        wrapper = target_parents[target]
        check(f'table_scroll_wrapper_ltr_and_keyboard_accessible:{identifier}',
              'source-table-scroll' in wrapper.get('class', '').split() and wrapper.get('dir') == 'ltr'
              and wrapper.get('tabindex') == '0' and wrapper.get('role') == 'region')
        for row_index, (source_row, target_row) in enumerate(zip(original_rows, target_rows), 1):
            for entry_index, (source_entry, target_entry) in enumerate(zip(source_row, target_row), 1):
                key = f'{identifier}/row/{row_index}/entry/{entry_index}'
                if key in specs:
                    expected_text = text(ET.fromstring('<root>' + translation['source_blocks'][key] + '</root>'))
                    scope = 'col' if tag(source_parents[source_row]) == 'thead' else 'row'
                    check(f'table_header_translation:{key}', text(target_entry) == expected_text)
                    check(f'table_header_semantics:{key}', target_entry.tag == 'th'
                          and target_entry.get('scope') == scope and target_entry.get('dir') == 'rtl')
                    if any(tag(child) == 'emphasis' for child in source_entry):
                        check(f'table_header_emphasis_retained:{key}', len(target_entry.findall('em')) == 1)
                else:
                    raw = text(source_entry)
                    check(f'table_data_exact:{key}', target_entry.tag == 'td' and text(target_entry) == raw)
                    check(f'table_data_ltr:{key}', target_entry.get('dir') == 'ltr')
                    if re.search('[A-Za-z]', raw):
                        check(f'proper_name_english_label:{key}', target_entry.get('lang') == 'en')
        faithful = translation['source_blocks'][identifier + '/summary']
        check(f'faithful_source_summary_retained:{identifier}', target.get('data-source-summary') == faithful)
        summary = translation.get('table_summary_overrides', {}).get(identifier, faithful)
        check(f'accessible_summary_matches_declared_translation:{identifier}', target.get('aria-label') == summary)
        observed.append({'id': identifier, 'rows': expected_shape[0], 'columns': expected_shape[1],
                         'source_cells': [[text(entry) for entry in row] for row in original_rows]})
    grade = element(document, GRADE_TABLE)
    check('grade_summary_discrepancy_is_real_and_not_used_as_aria',
          'two columns and ten rows' in element(source, GRADE_TABLE).get('summary', '')
          and 'دو کالم تے دس قطاراں' in grade.get('data-source-summary', '')
          and 'دو قطاراں تے نو کالم' in grade.get('aria-label', '')
          and 'دو کالم تے دس قطاراں' not in grade.get('aria-label', '')
          and grade.get('aria-label') != grade.get('data-source-summary'))
    check('only_inaccurate_grade_summary_overridden', set(translation.get('table_summary_overrides', {})) == {GRADE_TABLE})
    return observed


def validate_links_and_footnote(document, source, manifest, check=require):
    labels = {entry['id']: entry['local_label'] for entry in manifest['references']}
    expected_all = []
    for original in source.iter():
        links = [node for node in original if tag(node) == 'link']
        if not links:
            continue
        target = element(document, original.get('id'))
        actual = target.findall('a')
        expected = ['#' + link.get('target-id') for link in links]
        check(f'direct_source_link_targets:{original.get("id")}', [link.get('href') for link in actual] == expected)
        for link in actual:
            target_id = link.get('href')[1:]
            label = link.findall('bdi')
            check(f'source_table_link_label:{target_id}', len(label) == 1 and label[0].get('dir') == 'ltr'
                  and text(label[0]) == labels[target_id])
        expected_all.extend(expected)
    footnote_hrefs = {'#' + node.get('id') + '-text' for node in source.iter() if tag(node) == 'footnote'}
    actual_all = [link.get('href') for root in source
                  for link in element(document, root.get('id')).iter('a')
                  if link.get('href', '').startswith('#') and link.get('href') not in footnote_hrefs]
    check('all_source_table_links_order_exact', actual_all == expected_all)
    original_notes = [node for node in source.iter() if tag(node) == 'footnote']
    require('one_source_footnote', len(original_notes) == 1)
    original = original_notes[0]
    parsed = re.fullmatch(r'(https?://\S+)\. Accessed (\d+/\d+/\d+)\.', text(original))
    require('source_footnote_url_and_access_date_recognized', parsed is not None)
    url, accessed = parsed.groups()
    target = element(document, original.get('id'))
    check('source_footnote_reference_is_inline_superscript', target.tag == 'sup' and 'source-footnote' in target.get('class', '').split())
    parent = parent_map(document)[target]
    check('source_footnote_stays_in_original_paragraph', parent.get('id') == parent_map(source)[original].get('id'))
    inline_order = [('link', node.get('href')) if node.tag == 'a' else ('footnote', node.get('id'))
                    for node in parent if node.tag == 'a' or node.get('id') == original.get('id')]
    check('table_link_then_nested_footnote_order', inline_order == [('link', '#' + BASEBALL_TABLE), ('footnote', original.get('id'))])
    reference_links = target.findall('a')
    body_id = original.get('id') + '-text'
    check('source_footnote_reference_targets_own_endnote', len(reference_links) == 1
          and reference_links[0].get('href') == '#' + body_id)
    reference_labels = reference_links[0].findall('bdi')
    check('source_footnote_reference_number_ltr', len(reference_labels) == 1 and reference_labels[0].get('dir') == 'ltr'
          and text(reference_labels[0]) == str(original_notes.index(original) + 1))
    body = element(document, body_id)
    body_parents = parent_map(document)
    ancestor = body
    endnote_section = None
    while ancestor in body_parents:
        ancestor = body_parents[ancestor]
        if 'source-endnotes' in ancestor.get('class', '').split():
            endnote_section = ancestor
            break
    check('source_footnote_body_is_separate_endnote', body.tag == 'li' and endnote_section is not None)
    links = [link for link in body.iter('a') if not link.get('href', '').startswith('#')]
    check('source_footnote_url_exact', len(links) == 1 and links[0].get('href') == url and text(links[0]) == url)
    backlinks = [link for link in body.iter('a') if link.get('href', '').startswith('#')]
    check('source_footnote_backlink_targets_original_id', len(backlinks) == 1 and backlinks[0].get('href') == '#' + original.get('id'))
    url_labels = links[0].findall('bdi')
    check('source_footnote_url_ltr_english', len(url_labels) == 1 and url_labels[0].get('dir') == 'ltr'
          and url_labels[0].get('lang') == 'en')
    dates = [node for node in body.iter('bdi') if text(node) == accessed]
    check('source_footnote_access_date_exact_and_ltr', len(dates) == 1 and dates[0].get('dir') == 'ltr')
    return expected_all, {'id': original.get('id'), 'endnote_id': body_id, 'url': url, 'source_access_date': accessed}


def validate_directions_and_local_refs(document, check=require):
    parents = parent_map(document)

    def direction(node):
        while node is not None:
            if node.get('dir'):
                return node.get('dir')
            node = parents.get(node)
        return None

    check('all_bdi_explicit_ltr', all(node.get('dir') == 'ltr' for node in document.iter('bdi')))
    check('english_language_lanes_ltr', all(direction(node) == 'ltr' for node in document.iter() if node.get('lang') == 'en'))
    for node in document.find('body').iter():
        fragments = [node.text or ''] + [child.tail or '' for child in node]
        for fragment in fragments:
            if re.search(r'[A-Za-z0-9]', fragment):
                require('visible_english_and_numbers_in_ltr_context', direction(node) == 'ltr')
    check('visible_english_and_numbers_in_ltr_context', True)
    references = []
    for node in document.iter():
        for attribute in ('href', 'src'):
            if attribute not in node.attrib:
                continue
            value = node.get(attribute)
            parsed = urlsplit(value)
            if parsed.scheme in ('http', 'https', 'mailto'):
                continue
            require(f'supported_local_reference:{value}', not parsed.scheme and not parsed.netloc)
            target = (READER.parent / unquote(parsed.path)).resolve() if parsed.path else READER.resolve()
            require(f'local_reference_exists:{value}', target.is_file())
            if parsed.fragment:
                target_doc = document if target == READER.resolve() else parse_reader(target.read_text(encoding='utf-8'))
                require(f'local_fragment_exists:{value}', any(node.get('id') == unquote(parsed.fragment) for node in target_doc.iter()))
            references.append(value)
    check('all_local_files_and_fragment_links_resolve', True)
    return references


def is_function(pairs):
    outputs = {}
    for input_value, output_value in pairs:
        outputs.setdefault(input_value, set()).add(output_value)
    return all(len(values) == 1 for values in outputs.values())


def validate_example_mathematics(document, source, check=require):
    grade_rows = rows(element(source, GRADE_TABLE))
    bands = [text(cell) for cell in grade_rows[0]][1:]
    averages = [text(cell) for cell in grade_rows[1]][1:]
    expected_pairs = [f'({band}, {average})' for band, average in zip(bands, averages)]
    bridge = element(document, 'grades-ranks-bridge')
    check('support_bridge_explicitly_original', bridge.get('data-origin') == 'original-bridge')
    displayed = [node for node in bridge.iter('bdi') if 'formula' in node.get('class', '').split()]
    check('original_bridge_pairs_match_actual_table_columns', [text(node) for node in displayed] == expected_pairs)
    check('original_bridge_pairs_ltr', all(node.get('dir') == 'ltr' for node in displayed))
    structure = element(bridge, 'grade-table-structure')
    check('source_summary_mismatch_explained_in_original_bridge', 'دو قطاراں تے نو کالم' in text(structure)
          and 'دو کالم تے دس قطاراں' in text(structure) and 'درستی ساڈی ولوں' in text(structure))
    bridge_text = text(bridge)
    check('whole_percent_assumption_and_nonuniversal_scope_disclosed',
          'پورے فی صد عدداں والا ایہہ مفروضہ' in bridge_text and 'ماخذ ایہنوں وکھرے طور اُتے بیان نہیں کردا' in bridge_text
          and 'ہر سکول یا یونیورسٹی دا لازمی قاعدہ نہیں' in bridge_text)
    check('source_ranking_date_not_claimed_current', 'ایہہ ساڈی اج دی رسائی دی تاریخ نہیں' in bridge_text
          and 'ساڈی ولوں اج دے یا ہر ویلے لئی منّے ہوئے درجیاں دا دعویٰ نہیں' in bridge_text)
    pairs = []
    for band, average in zip(bands, averages):
        match = re.fullmatch(r'(\d+)–(\d+)', band)
        require(f'source_whole_percent_band_recognized:{band}', match is not None)
        low, high = map(int, match.groups())
        require(f'source_band_bounds_in_order:{band}', low <= high)
        require(f'source_gpa_decimal_point_retained:{average}', re.fullmatch(r'\d+\.\d', average) is not None)
        pairs.extend((value, Decimal(average)) for value in range(low, high + 1))
    inputs = [value for value, _ in pairs]
    check('source_whole_percent_bands_have_101_unique_inputs', len(inputs) == len(set(inputs)) == 101
          and sorted(inputs) == list(range(101)))
    check('source_percent_to_gpa_function_reverse_not_function', is_function(pairs) and not is_function([(y, x) for x, y in pairs]))
    original_solution = element(source, 'fs-id1165137807321')
    expected_numbers = re.findall(r'\d+\.\d+|\d+', text(original_solution))
    target_solution = element(document, original_solution.get('id'))
    check('grade_solution_numbers_source_exact_and_ltr',
          [text(node) for node in target_solution.iter('bdi')] == expected_numbers
          and all(node.get('dir') == 'ltr' for node in target_solution.iter('bdi')))
    expected_average, first_input, second_input = expected_numbers
    grade_map = dict(pairs)
    check('source_example_distinct_grades_share_gpa', int(first_input) != int(second_input)
          and grade_map[int(first_input)] == grade_map[int(second_input)] == Decimal(expected_average))
    baseball_rows = rows(element(source, BASEBALL_TABLE))[1:]
    baseball = [(text(row[0]), text(row[1])) for row in baseball_rows]
    check('source_five_player_rank_relation_is_bijection', len(baseball) == 5
          and is_function(baseball) and is_function([(rank, name) for name, rank in baseball]))
    source_answer = element(source, 'eip-idm243007968')
    rank_match = re.search(r'(\d+)(?:st|nd|rd|th) place', text(source_answer))
    require('source_hypothetical_tied_rank_recognized', rank_match is not None)
    tied_rank = rank_match[1]
    first_player = next(name for name, rank in baseball if rank == tied_rank)
    second_player = next(name for name, rank in reversed(baseball) if rank != tied_rank)
    tied = [(name, tied_rank if name == second_player else rank) for name, rank in baseball]
    check('source_players_tie_counterexample_breaks_rank_to_name_only', first_player != second_player
          and is_function(tied) and not is_function([(rank, name) for name, rank in tied]))
    return {'grade_bands': bands, 'gpas': averages, 'whole_percent_input_count': len(inputs),
            'domain_assumption': 'integers 0 through 100 only; source fractional-percent rounding is unspecified',
            'percent_to_gpa_is_function': True, 'gpa_to_percent_is_function': False,
            'baseball_pairs': baseball, 'hypothetical_tie': {'rank': tied_rank, 'distinct_players': [first_player, second_player]}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unit', choices=['003'], default='003')
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    translation = json.loads(TRANSLATION.read_text(encoding='utf-8'))
    excerpt = BASE / 'source-excerpts' / manifest['source_excerpt']
    source = ET.parse(excerpt).getroot()
    input_paths = [TRANSLATION, excerpt, MANIFEST, BASE / 'qa/unit-003-language-notes.md',
                   BASE / 'styles/reader.css', BASE / 'terminology.tsv', BASE / 'scripts/build.py',
                   Path(__file__).resolve(), BASE / 'provenance/ATTRIBUTION.md']
    start_hashes = {path.relative_to(BASE).as_posix(): sha256(path) for path in input_paths}
    command = [sys.executable, str(BASE / 'scripts/build.py'), '--unit', args.unit]
    subprocess.run(command, check=True)
    first = READER.read_bytes()
    subprocess.run(command, check=True)
    require('deterministic_reader_build', first == READER.read_bytes())
    reader_text = first.decode('utf-8')
    document = parse_reader(reader_text)
    checks = ['deterministic_reader_build']

    def check(name, condition):
        require(name, condition)
        checks.append(name)

    check('frozen_excerpt_hash_matches_manifest', sha256(excerpt) == manifest['excerpt_sha256'])
    check('exact_unit_selection_and_next_cursor', manifest['unit'] == translation['unit'] == 'PNB-003'
          and [node.get('id') for node in source] == manifest['selection_ids'] == ['Example_01_01_02', 'fs-id1165137588587']
          and manifest['next_source_id'] == 'fs-id1165134474160')
    check('exact_locale_and_rtl', document.get('lang') == translation['locale'] == 'pnb-Arab-PK' and document.get('dir') == 'rtl')
    for path in [*input_paths, READER]:
        check(f'unicode_clean:{path.relative_to(BASE).as_posix()}', not FORBIDDEN.search(path.read_text(encoding='utf-8')))
    check('no_unresolved_placeholders', not re.search(r'\{\{[^{}]*\}\}|\bTODO\b', reader_text))
    check('no_mathml_in_source_or_reader', not any(tag(node) == 'math' for node in source.iter())
          and not any(tag(node) == 'math' for node in document.iter()))
    check('no_source_images_or_unexpected_reader_images', not manifest['images'] and not list(document.iter('img')))
    check('partial_coverage_disclosed', 'پورے حصے دا ترجمہ نہیں' in reader_text)
    source_ids, parts = validate_structure(document, source, check)
    table_records = validate_tables(document, source, translation, check)
    block_keys = validate_blocks(document, source, translation, manifest, check)
    link_targets, footnote = validate_links_and_footnote(document, source, manifest, check)
    local_references = validate_directions_and_local_refs(document, check)
    mathematics = validate_example_mathematics(document, source, check)

    def mutation_check(name, mutate, validate, expected_error):
        mutant = copy.deepcopy(document)
        mutate(mutant)
        try:
            validate(mutant)
        except AssertionError as error:
            check(name, str(error) == expected_error)
        else:
            raise AssertionError(name + ':mutation_was_not_rejected')

    def alter_grade_cell(mutant):
        cell = rows(element(mutant, GRADE_TABLE))[1][1]
        cell.text = str(Decimal(text(cell)) + Decimal('0.1'))

    def swap_grade_rows(mutant):
        body = element(mutant, GRADE_TABLE).find('tbody')
        body[:] = list(reversed(list(body)))

    table_validator = lambda mutant: validate_tables(mutant, source, translation)
    mutation_check('mutation_changed_grade_cell_rejected', alter_grade_cell, table_validator,
                   f'table_data_exact:{GRADE_TABLE}/row/2/entry/2')
    mutation_check('mutation_swapped_grade_rows_rejected', swap_grade_rows, table_validator,
                   f'table_header_translation:{GRADE_TABLE}/row/1/entry/1')
    mutation_check('mutation_reversed_table_direction_rejected', lambda mutant: element(mutant, GRADE_TABLE).set('dir', 'rtl'),
                   table_validator, f'table_orientation_ltr:{GRADE_TABLE}')
    mutation_check('mutation_changed_nested_footnote_url_rejected',
                   lambda mutant: element(mutant, footnote['endnote_id']).find('a').set('href', footnote['url'] + '?changed=1'),
                   lambda mutant: validate_links_and_footnote(mutant, source, manifest), 'source_footnote_url_exact')
    check('mutations_do_not_change_reader', READER.read_bytes() == first)
    final_hashes = {path.relative_to(BASE).as_posix(): sha256(path) for path in input_paths}
    check('checked_inputs_unchanged_during_run', start_hashes == final_hashes)
    final_hashes[READER.relative_to(BASE).as_posix()] = sha256(READER)
    receipt = {
        'unit': 'PNB-003', 'status': 'structural_pass_linguistic_and_visual_review_separate',
        'translated_blocks': len(block_keys), 'source_block_keys': block_keys,
        'source_ids_preserved': len(source_ids), 'source_ids': source_ids, 'source_parts': parts,
        'source_math_count': 0, 'formula_validation': 'not_applicable_no_source_mathml',
        'tables': table_records, 'source_link_targets': link_targets, 'source_footnote': footnote,
        'example_mathematics': mathematics, 'local_reference_count': len(local_references),
        'checks': checks, 'hashes': final_hashes,
        'limitations': [
            'No native-speaker or educator certification; exact rendered translation matching does not prove linguistic fidelity.',
            'Only the manifest selection is covered, not all m49301 or the five-book assignment.',
            'Grade computation assumes integer percentage inputs 0–100 for this frozen example only; fractional handling is unspecified.',
            'No universal GPA policy or current/universal baseball ranking is asserted or verified.',
            'Source summary error is retained for traceability but replaced by the declared accurate accessibility summary.',
            'No source MathML occurs here; formula-tree certification is not applicable.',
            'Desktop/mobile visual layout, screen-reader behavior, glyph shaping and font portability require separate review.',
            'External URLs and the source access date are preserved, not network-tested or refreshed.',
        ],
    }
    (BASE / 'qa').mkdir(exist_ok=True)
    (BASE / 'qa/structural-003.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'PASS: {len(checks)} checks; {len(block_keys)} translated blocks; {len(source_ids)} retained IDs; 2 tables; no source MathML')


if __name__ == '__main__':
    main()
