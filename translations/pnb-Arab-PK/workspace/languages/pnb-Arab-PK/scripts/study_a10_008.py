"""Freeze the exact canonical source study for A10-008 before drafting."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path, PurePosixPath
import xml.etree.ElementTree as ET

from prepare_a10 import BASE, ROOT, CNXML, MATH, digest, file_hash, jpeg_dimensions, require, tag, tree

UNIT = 'A10-008'
CANONICAL = ROOT / 'downloads/complete-upstream/osbooks-prealgebra-bundle/modules/m82453/index.cnxml'
COMPARISON = ROOT / 'downloads/extracted/A10/translated/modules/m82453/index.cnxml'
COLLECTION = ROOT / 'downloads/complete-upstream/osbooks-prealgebra-bundle/collections/elementary-algebra-2e.collection.xml'
AUTHORITY = ROOT / 'downloads/extracted/A10/authority/MEDIA_AUTHORITY_MANIFEST.csv'
EXCERPT = BASE / 'source-excerpts/a10-unit-008.cnxml'
PLAN = BASE / 'plans/A10-008-scope.json'
NEXT_RECEIPT = BASE / 'canon/receipts/A10-008-next-unit-20260901T190136843513Z.json'
C = '{' + CNXML + '}'
MM = '{' + MATH + '}'


def paths(root):
    result = {}
    def walk(node, path):
        result[node] = path
        for index, child in enumerate(node):
            walk(child, path + '/' + str(index))
    walk(root, 'document')
    return result


def parents(root):
    return {child: node for node in root.iter() for child in node}


def derive_key(node, parent, root):
    name = tag(node)
    if name == 'title':
        return parent.get('id') + '/title'
    if name == 'para':
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


def math_record(index, node, parent_map):
    owner = parent_map[node]
    while tag(owner) not in {'para', 'entry'}:
        owner = parent_map[owner]
    raw = ET.tostring(node, encoding='utf-8', short_empty_elements=True)
    return {
        'index': index,
        'owner_tag': tag(owner),
        'owner_id': owner.get('id'),
        'sha256': digest(raw),
        'bytes': len(raw),
        'text': ''.join(node.itertext())
    }


def table_record(node):
    group = next(child for child in node if tag(child) == 'tgroup')
    sections = [child for child in group if tag(child) in {'thead', 'tbody'}]
    rows = [row for section in sections for row in section if tag(row) == 'row']
    entries = [entry for row in rows for entry in row if tag(entry) == 'entry']
    return {
        'id': node.get('id'),
        'attributes': dict(node.attrib),
        'summary_attribute': 'aria-label',
        'tgroup_attributes': dict(group.attrib),
        'columns': int(group.get('cols')),
        'rows': len(rows),
        'cells': len(entries),
        'empty_cells': sum(not len(entry) and not (entry.text or '').strip() for entry in entries),
        'cells_with_media': sum(any(tag(child) == 'media' for child in entry) for entry in entries),
        'source_thead_cells': sum(len(row) for section in sections if tag(section) == 'thead' for row in section),
        'rendering': 'Preserve the exact two-column LTR source geometry, row/cell order, empty cells, source alignment and nested media/MathML; no source header cells are inferred. Use a local horizontal scroller on narrow screens.'
    }


def image_table_id(media, parent_map):
    owner = parent_map[media]
    while owner is not None and tag(owner) != 'table':
        owner = parent_map.get(owner)
    return owner.get('id') if owner is not None else None


def write_frozen(path, data):
    if path.exists():
        require(path.read_bytes() == data, 'Refusing to change frozen source-study output: ' + str(path))
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def main():
    raw = CANONICAL.read_bytes()
    require((len(raw), digest(raw)) == (184248, 'a8fdd235aa254c5a0a1248fa858e9b3579d9b40982bbc514cbe6a18c3e6fcbed'),
            'Canonical module pin changed')
    require((COMPARISON.stat().st_size, file_hash(COMPARISON))
            == (186219, '2c0b688d569044b128d589579e9ba7d871a0fb9ac7a670ac6f22d0ef2b66e635'),
            'Pinned Indonesian comparison changed')
    require((COLLECTION.stat().st_size, file_hash(COLLECTION))
            == (5256, '5fdc03ab9e6ee7327be72f7e0a17c4d884e65f4a8081a0b2a06dbdb1392bda72'),
            'Canonical collection changed')
    require(NEXT_RECEIPT.is_file(), 'Required next-unit canon reading receipt absent')

    source = ET.parse(CANONICAL).getroot()
    content = source.find(C + 'content')
    require(content is not None and len(content) == 8, 'Canonical content extent changed')
    require((content[2].get('id'), content[3].get('id'), content[4].get('id'))
            == ('fs-id1170654953465', 'fs-id1170654889475', 'fs-id1170655163482'),
            'A10-008 contiguous sibling boundary changed')
    section = content[3]
    require(len(section) == 13 and tag(section[0]) == 'title'
            and ''.join(section[0].itertext()).strip() == 'Evaluate an Expression'
            and section[-1].get('id') == 'fs-id1170655197213',
            'A10-008 complete section extent changed')

    start_pos = raw.index(b'fs-id1170654889475')
    start = raw.rfind(b'<section', 0, start_pos)
    next_pos = raw.index(b'fs-id1170655163482', start_pos)
    end = raw.rfind(b'<section', 0, next_pos)
    selected = raw[start:end]
    require((start, end, len(selected), digest(selected))
            == (72059, 89018, 16959, '72b8090bf339fd3efd3d44f016567ca66be1026a4434794369c6df2041aa6150'),
            'Canonical section byte range changed')
    excerpt_data = (b"<?xml version='1.0' encoding='utf-8'?>\n"
                    b'<document xmlns="http://cnx.rice.edu/cnxml" '
                    b'xmlns:m="http://www.w3.org/1998/Math/MathML" '
                    b'id="a10-unit-008-excerpt">' + selected + b'</document>\n')
    write_frozen(EXCERPT, excerpt_data)
    excerpt = ET.fromstring(excerpt_data)
    require(len(excerpt) == 1 and tree(excerpt[0]) == tree(section), 'Generated excerpt tree changed')

    path_map = paths(excerpt)
    parent_map = parents(excerpt)
    keys = []
    key_paths = {}
    for node in excerpt.iter():
        key = derive_key(node, parent_map.get(node), excerpt)
        if key:
            require(key not in key_paths, 'Duplicate source key: ' + key)
            keys.append(key)
            key_paths[key] = path_map[node]

    ids = [node.get('id') for node in excerpt.iter() if node is not excerpt and node.get('id')]
    counts = Counter(tag(node) for node in section.iter())
    maths = [node for node in section.iter() if node.tag == MM + 'math']
    table_nodes = [node for node in section.iter() if tag(node) == 'table']
    tables = [table_record(node) for node in table_nodes]
    token_owners = []
    for node in section.iter():
        tokens = [child for child in node if tag(child) == 'span' and child.get('class') == 'token']
        if tokens:
            owner_key = derive_key(node, parents(section).get(node), section)
            structural = any(tag(child) in {'list', 'table', 'media', 'para', 'note', 'figure'} for child in node)
            token_owners.append({
                'key': owner_key,
                'owner_tag': tag(node),
                'owner_id': node.get('id'),
                'tokens': [(child.text or '').strip() for child in tokens],
                'display_labels': ['(' + chr(ord('a') + 'ⓐⓑⓒⓓⓔ'.index((child.text or '').strip())) + ')' for child in tokens],
                'group_short_parts': not structural
            })

    with AUTHORITY.open(encoding='utf-8-sig', newline='') as handle:
        authority_rows = list(csv.DictReader(handle))
    images = []
    for image in [node for node in section.iter() if tag(node) == 'image']:
        media = parents(section)[image]
        filename = PurePosixPath(image.get('src')).name
        source_path = 'media/' + filename
        original = CANONICAL.parents[2] / source_path
        data = original.read_bytes()
        matches = [(index, row) for index, row in enumerate(authority_rows, 2)
                   if row['relative_path'] == source_path]
        require(len(matches) == 1, 'Missing/duplicate image authority row: ' + source_path)
        row_number, authority_row = matches[0]
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + bytes([0]) + data).hexdigest()
        require(authority_row['sha256'] == digest(data)
                and int(authority_row['bytes']) == len(data)
                and authority_row['git_blob_sha1'] == blob,
                'Image authority row differs: ' + source_path)
        comparison_image = ROOT / 'downloads/extracted/A10/translated/media' / filename
        images.append({
            'media_id': media.get('id'),
            'table_id': image_table_id(media, parents(section)),
            'source_cnxml_src': image.get('src'),
            'source_path': source_path,
            'canonical_local_path': original.relative_to(ROOT).as_posix(),
            'future_reader_path': 'assets/a10/' + filename,
            'bytes': len(data),
            'sha256': digest(data),
            'git_blob_sha1': blob,
            'width': jpeg_dimensions(data)[0],
            'height': jpeg_dimensions(data)[1],
            'source_declared_mime': image.get('mime-type'),
            'actual_mime': 'image/jpeg',
            'actual_format': 'JPEG',
            'authority_row_number_including_header': row_number,
            'authority_row': authority_row,
            'source_english_alt': media.get('alt'),
            'comparison_redraw': ({
                'path': comparison_image.relative_to(ROOT).as_posix(),
                'bytes': comparison_image.stat().st_size,
                'sha256': file_hash(comparison_image),
                'byte_identical_to_canonical': file_hash(comparison_image) == digest(data)
            } if comparison_image.is_file() else None),
            'copy_status': 'Not copied at source-study freeze; the isolated preparer must verify path/hash/blob/dimensions before copying only these 16 files.'
        })

    comparison_section = next(node for node in ET.parse(COMPARISON).getroot().iter()
                              if node.get('id') == 'fs-id1170654889475')
    canonical_nodes = list(section.iter())
    comparison_nodes = list(comparison_section.iter())
    require(len(canonical_nodes) == len(comparison_nodes) == 445, 'Comparison subtree extent changed')
    require([tag(node) for node in canonical_nodes] == [tag(node) for node in comparison_nodes]
            and [node.get('id') for node in canonical_nodes] == [node.get('id') for node in comparison_nodes],
            'Comparison structure/ID order differs')
    attribute_differences = [index for index, (left, right) in enumerate(zip(canonical_nodes, comparison_nodes))
                             if left.attrib != right.attrib]
    text_tail_differences = [index for index, (left, right) in enumerate(zip(canonical_nodes, comparison_nodes))
                             if left.text != right.text or left.tail != right.tail]

    exercise_nodes = [node for node in section.iter() if tag(node) == 'exercise']
    exercises = []
    for index, exercise in enumerate(exercise_nodes, 1):
        problem = next(node for node in exercise if tag(node) == 'problem')
        solution = next((node for node in exercise if tag(node) == 'solution'), None)
        exercises.append({
            'index': index,
            'exercise_id': exercise.get('id'),
            'problem_id': problem.get('id'),
            'solution_id': solution.get('id') if solution is not None else None,
            'source_supplied_solution': solution is not None,
            'worked_example': tag(parents(section)[exercise]) == 'example'
        })

    plan = {
        'schema': 'pnb-contiguous-source-scope-v1',
        'unit': UNIT,
        'assignment': 'A10',
        'locale': 'pnb-Arab-PK',
        'plan_stage': 'Source study complete and exact input boundary frozen before drafting. No translated reader or coverage is claimed by this plan.',
        'canonical_module': 'm82453',
        'canonical_path': CANONICAL.relative_to(ROOT).as_posix(),
        'canonical_bytes': len(raw),
        'canonical_sha256': digest(raw),
        'canonical_git_blob_sha1': hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + bytes([0]) + raw).hexdigest(),
        'canonical_commit': '38cae454e644abf9f0a623e876994553881597c9',
        'canonical_tree': '7907e4c81d43de1c3b6da173f0eb273c01dc5b55',
        'comparison_path': COMPARISON.relative_to(ROOT).as_posix(),
        'comparison_bytes': COMPARISON.stat().st_size,
        'comparison_sha256': file_hash(COMPARISON),
        'comparison_version': 'v1.0.2',
        'collection': {
            'id': 'col31130', 'path': COLLECTION.relative_to(ROOT).as_posix(),
            'bytes': COLLECTION.stat().st_size, 'sha256': file_hash(COLLECTION),
            'module_count': 82, 'module_order_one_based': 4,
            'previous_module': 'm82452', 'next_module': 'm82454'
        },
        'scope': {
            'content_child_index_zero_based': 3,
            'section_id': 'fs-id1170654889475',
            'section_title': 'Evaluate an Expression',
            'section_direct_children': len(section),
            'first_direct_child': 'fs-id1170654889475/title',
            'last_direct_child_id': section[-1].get('id'),
            'last_descendant_id': ids[-1],
            'stop_before_id': 'fs-id1170655163482',
            'stop_before_title': 'Identify and Combine Like Terms',
            'no_intermediate_nodes_skipped': True,
            'selected_wrapper_id': excerpt.get('id'),
            'source_byte_range': {'start': start, 'end_exclusive': end, 'bytes': len(selected), 'sha256': digest(selected)},
            'excerpt': {
                'path': EXCERPT.relative_to(ROOT).as_posix(), 'bytes': len(excerpt_data),
                'sha256': digest(excerpt_data), 'root_id': excerpt.get('id'),
                'construction': 'Generated CNXML document wrapper around one exact canonical section byte subtree; only wrapper ID/namespaces/XML declaration/closing tags are generated. Selected source attributes,text,tails,IDs,MathML and order are unchanged.'
            }
        },
        'exact_counts': {
            'source_blocks': len(keys), 'source_ids': len(ids), 'source_elements': sum(counts.values()),
            'mathml_trees': len(maths), 'mathml_nodes': sum(sum(1 for _ in node.iter()) for node in maths),
            'direct_math_placeholders': len(maths), 'standalone_equation_math_owners': counts['equation'],
            'titles': counts['title'], 'paragraphs': counts['para'], 'terms': counts['term'],
            'bold_emphases': sum(tag(node) == 'emphasis' and node.get('effect') == 'bold' for node in section.iter()),
            'examples': counts['example'], 'exercises': counts['exercise'], 'solutions': counts['solution'],
            'explicit_solution_titles': sum(tag(node) == 'solution' and any(tag(child) == 'title' for child in node)
                                            for node in section.iter()),
            'circled_part_tokens': counts['span'], 'explicit_newlines': counts['newline'],
            'cnxml_tables': counts['table'], 'table_rows': counts['row'], 'table_cells': counts['entry'],
            'empty_table_cells': sum(item['empty_cells'] for item in tables),
            'source_thead_cells': sum(item['source_thead_cells'] for item in tables),
            'media': counts['media'], 'images': counts['image'], 'source_links': counts['link']
        },
        'source_tag_counts': dict(sorted(counts.items())),
        'source_ids_in_order': ids,
        'section_direct_children': [
            {'index': index, 'tag': tag(node), 'id': node.get('id'),
             'title': (''.join(next(child for child in node if tag(child) == 'title').itertext()).strip()
                       if any(tag(child) == 'title' for child in node) else None)}
            for index, node in enumerate(section)
        ],
        'source_block_formula': '23paragraphs+5titles+5table summaries+42cells(including7empty)+16image alts=91.',
        'source_block_keys_in_order': keys,
        'source_keys_to_paths': key_paths,
        'tables': tables,
        'token_owners': token_owners,
        'exercises': exercises,
        'source_mathml': {
            'total': len(maths), 'direct_placeholders': len(maths), 'standalone_equations': 0,
            'records': [math_record(index, node, parents(section)) for index, node in enumerate(maths)],
            'comparison_differences': 0
        },
        'images': images,
        'total_declared_image_bytes': sum(item['bytes'] for item in images),
        'comparison_structure': {
            'element_count_each': len(canonical_nodes), 'tag_sequence_equal': True,
            'id_sequence_equal': True, 'attribute_difference_node_indexes': attribute_differences,
            'text_or_tail_difference_node_indexes': text_tail_differences,
            'canonical_is_authoritative': True
        },
        'image_visual_study': [
            {'file': '010d', 'canonical_pixels': '7−4', 'source_alt_issue': 'Calls it numbers suggesting a score/date/general notation rather than the subtraction expression; requires a separately declared accessible correction.'},
            {'file': '012b', 'canonical_pixels': '3^x', 'canonical_row_one_mathml': '3^x', 'canonical_table_summary': '3^4 after substitution', 'indonesian_redraw': '3^4', 'decision': 'Keep canonical 3^x bytes/alt and disclose the canonical summary/cells mismatch. Indonesian redraw reflects the worked substitution but is comparison evidence only.'},
            {'file': '013b', 'canonical_pixels': '2x^2+3x+8', 'indonesian_redraw': '2(4)^2+3(4)+8', 'decision': 'Keep canonical bytes/alt. Disclose that the canonical table summary claims a substituted row although the pixels repeat the original expression.'}
        ],
        'discrepancy_decisions': [
            {'id': 'a10-008-source-table-right-typo', 'source': 'Both first table summaries say “To the write” where spatial context requires “right”.', 'treatment': 'Translate the intended spatial description and disclose the English source typo; do not change the frozen CNXML.'},
            {'id': 'a10-008-010d-alt', 'source': '010d pixels show 7−4 while the English alt speculates about score/date/notation.', 'treatment': 'Retain a faithful Punjabi alt trace and provide a separate pixel-based accessible description.'},
            {'id': 'a10-008-reversed-try-wording', 'source': 'Two Try It prompts read “Evaluate x=…, when [expressions]”, reversing the stated given and requested quantities; the preceding worked prompt also has an illogical “when” before its part list.', 'treatment': 'Use natural Punjabi matching the supplied-answer intent while preserving all MathML order and explicitly disclose the source wording repair for these three prompts.'},
            {'id': 'a10-008-012b-summary-pixels', 'source': 'The exponent table summary says the substituted row is 3^4, but canonical row-one MathML and row-two 012b pixels/alt both show 3^x. Indonesian redraw changes row two to 3^4.', 'treatment': 'Keep canonical bytes/MathML/alt and faithful summary trace; add a separately original corrected accessible table summary.'},
            {'id': 'a10-008-013b-summary-pixels', 'source': 'The final table summary describes 2(4)^2+3(4)+8, but canonical 013b pixels/alt repeat 2x^2+3x+8. Indonesian redraw changes the pixels to the substituted expression.', 'treatment': 'Keep canonical pixels/alt authoritative; faithful summary remains traceable and a separately original corrected accessible summary describes the actual canonical row.'},
            {'id': 'a10-008-indonesian-redraws', 'source': 'Indonesian comparison supplies only two redraws in this section, 012b and 013b, both differing from canonical bytes.', 'treatment': 'Do not substitute either redraw; use them only to understand the comparison edition’s intended worked steps.'}
        ],
        'renderer_risks': [
            'Keep all MathML and numeric/image table cells LTR-isolated inside RTL prose.',
            'Four solution paragraphs contain a part token/newline immediately followed by a wide table; never wrap the table inside the short part-label no-break span.',
            'All five tables have two source columns and no source headers; retain td semantics and local horizontal scrolling.',
            'Canonical images are tiny equation/text rasters; preserve natural source widths rather than upscaling or mirroring.',
            'Preserve the base/exponent distinction in x² versus 3ˣ and verify part order/answers from exact source math.'
        ],
        'canon_consultations': {
            'next_unit': NEXT_RECEIPT.relative_to(ROOT).as_posix(),
            'read_loci': ['C01', 'C02', 'C03', 'C04', 'C06', 'C09', 'C10', 'C11', 'C12'],
            'draft_revision_qa_required': True
        },
        'canon_limit': 'One-author general-prose canon supports grammar/register only, not specialized algebra terminology or native certification.',
        'cursor': {'previous_verified_unit': 'A10-007', 'current': 'A10-008',
                   'next_required': 'fs-id1170655163482', 'next_title': 'Identify and Combine Like Terms'},
        'whole_module_complete': False, 'whole_book_complete': False, 'whole_assignment_complete': False,
        'native_review': 'pending', 'educator_review': 'pending', 'assistive_technology_review': 'pending'
    }
    plan_data = (json.dumps(plan, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    write_frozen(PLAN, plan_data)
    print('Studied A10-008:91blocks,83IDs,38MathML/232nodes,5tables/42cells,16JPEGs,9exercises/9solutions.')


if __name__ == '__main__':
    main()
