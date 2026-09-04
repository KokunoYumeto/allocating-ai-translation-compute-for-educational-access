"""Prepare the complete pinned m49306 witness and its admitted unchanged assets."""
from pathlib import Path, PurePosixPath
import argparse
import collections
import csv
import hashlib
import json
import xml.etree.ElementTree as ET

from qa_notation import jpeg_dimensions, unique_object


BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
CANONICAL = ROOT / 'downloads/upstream/osbooks-college-algebra-bundle/modules/m49306/index.cnxml'
COMPARISON = ROOT / 'downloads/extracted/A30/repo/source/modules/m49306/index.cnxml'
COMPONENTS = ROOT / 'downloads/complete-upstream/osbooks-college-algebra-bundle'
RIGHTS = ROOT / 'downloads/extracted/A30/00_control/COMPONENT_RIGHTS.csv'
RAW_SHA = '043afbc674a470470bf2288160f0136e32fe72740f76a73c2d52ba4a95b29370'
LF_SHA = '87e3bea0a14b4f487e0a5428b8138a644b0630b692d02c5a0e348e26ae3e6806'
COMPARISON_SHA = 'd14cddfd180339f2958f47d66e30c90709c2119c3f2074165d3bf5c4dfef6c9e'


def tag(node):
    return node.tag.rsplit('}', 1)[-1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_relative(value):
    path = PurePosixPath(value)
    assert not path.is_absolute() and '..' not in path.parts and path.as_posix() == value
    return path


def source_blocks(source):
    parent = {child: node for node in source.iter() for child in node}
    result = []
    for node in source.iter():
        name, owner, key = tag(node), parent.get(node), None
        if name == 'media':
            key = node.get('id') + '/alt'
        elif name == 'table':
            key = node.get('id') + '/summary'
        elif name == 'title':
            key = ('m49306/title' if owner is source else 'm49306/metadata/title'
                   if tag(owner) == 'metadata' else owner.get('id') + '/title')
        elif name in ('para', 'footnote', 'meaning'):
            key = node.get('id')
        elif name == 'term':
            key = node.get('id') or owner.get('id') + '/term'
        elif name == 'label' and ''.join(node.itertext()).strip():
            key = owner.get('id') + '/label'
        elif name == 'item':
            key = owner.get('id') + '/item/' + str(list(owner).index(node) + 1)
        elif name == 'caption':
            key = owner.get('id') + '/caption'
        elif name == 'entry':
            table = owner
            while tag(table) != 'table':
                table = parent[table]
            rows = [candidate for candidate in table.iter() if tag(candidate) == 'row']
            key = (table.get('id') + '/row/' + str(rows.index(owner) + 1)
                   + '/entry/' + str(list(owner).index(node) + 1))
        if key:
            result.append((key, node))
    assert len(result) == len(set(key for key, _ in result)) == 353
    return result


def inventory():
    raw, comparison_raw = CANONICAL.read_bytes(), COMPARISON.read_bytes()
    assert digest(raw) == RAW_SHA and digest(raw.replace(b'\r\n', b'\n')) == LF_SHA
    assert digest(comparison_raw) == COMPARISON_SHA
    source, comparison = ET.fromstring(raw), ET.fromstring(comparison_raw)
    parent = {child: node for node in source.iter() for child in node}
    paths = {source: 'root'}
    for node in source.iter():
        for index, child in enumerate(node):
            paths[child] = paths[node] + '/' + str(index)
    blocks = source_blocks(source)
    keyed = {node: key for key, node in blocks}
    templates, slots, links, labels = {}, {}, [], {}
    for key, node in blocks:
        if tag(node) == 'media':
            templates[key] = node.get('alt', '')
            slots[key] = {}
            continue
        if tag(node) == 'table':
            templates[key] = node.get('summary', '')
            slots[key] = {}
            continue
        counts, groups = collections.Counter(), collections.defaultdict(list)
        def inline(current):
            value = current.text or ''
            for child in current:
                name = tag(child)
                kind = ('math' if name == 'math' else 'link' if name == 'link'
                        else 'term' if name == 'term' else 'break' if name == 'newline' else 'child'
                        if child in keyed or name in ('list', 'table', 'media', 'figure') else None)
                if kind:
                    index = counts[kind]
                    counts[kind] += 1
                    groups[kind].append(paths[child])
                    value += '{{' + kind + ':' + str(index) + '}}'
                    if kind == 'link':
                        link_key = key + '/link/' + str(index)
                        row = {'key': link_key, 'attributes': dict(child.attrib),
                               'text': ''.join(child.itertext()), 'path': paths[child]}
                        links.append(row)
                        if row['text']:
                            labels[link_key] = row['text']
                else:
                    value += inline(child)
                value += child.tail or ''
            return value
        templates[key] = inline(node)
        slots[key] = dict(groups)
    assert len(links) == 37

    comparison_media = {node.get('id'): node for node in comparison.iter() if tag(node) == 'media'}
    rights_rows = {}
    with RIGHTS.open(encoding='utf-8-sig', newline='') as stream:
        for row in csv.DictReader(stream):
            rights_rows[row['asset_path']] = row
    images, notices = [], []
    for media in (node for node in source.iter() if tag(node) == 'media'):
        assert len(media) == 1 and tag(media[0]) == 'image'
        source_path = media[0].get('src').removeprefix('../../')
        safe_relative(source_path)
        data = (COMPONENTS / source_path).read_bytes()
        width, height = jpeg_dimensions(data)
        compare_image = comparison_media[media.get('id')][0]
        compare_path = (PurePosixPath('downloads/extracted/A30/repo/source/modules/m49306') /
                        PurePosixPath(compare_image.get('src')))
        compare_path = PurePosixPath(*[part for part in compare_path.parts if part != '..'])
        # Resolve through pathlib for the stored repository-relative witness.
        compare_file = (COMPARISON.parent / compare_image.get('src')).resolve()
        compare_repo = compare_file.relative_to(ROOT.resolve()).as_posix()
        compare_data = compare_file.read_bytes()
        ancestor = parent[media]
        while ancestor is not source and tag(ancestor) != 'figure':
            ancestor = parent[ancestor]
        figure_id = ancestor.get('id') if tag(ancestor) == 'figure' else None
        rights = rights_rows[source_path]
        assert rights['source_modules'] == 'm49306' and rights['admission'] == 'admitted'
        assert rights['sha256'] == digest(data) and int(rights['bytes']) == len(data)
        row = {
            'media_id': media.get('id'), 'source_path': source_path,
            'path': 'assets/unit-013-' + media.get('id') + '.jpg',
            'sha256': digest(data), 'bytes': len(data), 'width': width, 'height': height,
            'source_mime_type': media[0].get('mime-type'), 'publication_status': 'admitted-unchanged',
            'component_rights_id': rights['rights_component_id'],
            'comparison_asset': {
                'path': compare_repo, 'sha256': digest(compare_data),
                'treatment': ('byte-identical comparison JPEG' if data == compare_data
                              else 'different Indonesian SVG redraw; comparison only, not canonical pixels'),
            },
        }
        if figure_id:
            row['figure_id'] = figure_id
        images.append(row)
        notices.append({key: rights[key] for key in ('rights_component_id', 'asset_path', 'bytes', 'sha256',
            'source_modules', 'classification', 'admission', 'license_id', 'attribution', 'required_action')})
    assert len(images) == len(notices) == 24
    section = next(node for node in source.iter() if node.get('id') == 'fs-id1165135457748')
    section_exercises = [node for node in section.iter() if tag(node) == 'exercise']
    section_solutions = [node for node in section.iter() if tag(node) == 'solution']
    absent = [node.get('id') for node in section_exercises if not any(tag(child) == 'solution' for child in node)]
    counts = collections.Counter(tag(node) for node in source.iter())
    manifest = {
        'commit': '789b54099106b071d1d32bfcee454fed72eb4768', 'module': 'm49306',
        'path': 'modules/m49306/index.cnxml',
        'upstream_url': 'https://github.com/openstax/osbooks-college-algebra-bundle',
        'full_module_sha256': LF_SHA, 'unit': 'PNB-013',
        'purpose': 'complete canonical module witness for translation; not training or fine-tuning',
        'source_excerpt': 'unit-013.cnxml',
        'selection_ids': [node.get('id') for node in next(node for node in source if tag(node) == 'content') if node.get('id')],
        'next_source_id': None, 'next_module': 'm49308', 'excerpt_sha256': LF_SHA,
        'source_byte_witnesses': {
            'canonical_checkout_path': CANONICAL.relative_to(ROOT).as_posix(),
            'canonical_checkout_sha256': RAW_SHA,
            'newline_equivalence': 'Complete canonical bytes with CRLF converted to LF. All XML text, tails, attributes, metadata and source order retained; no synthetic excerpt wrapper.',
            'comparison_path': COMPARISON.relative_to(ROOT).as_posix(),
            'comparison_sha256': COMPARISON_SHA,
        },
        'selection_boundary': {
            'method': 'whole module: title, complete metadata with four objectives, all content children including all Section Exercises, then entire nine-definition glossary',
            'root_order': [tag(node) for node in source],
            'last_source_id': [node.get('id') for node in source.iter() if node.get('id')][-1],
            'following_module': 'm49308',
            'note': 'No answers are invented for the 23 Section Exercises without source solutions.',
        },
        'module_metadata': {
            'root_attributes': dict(source.attrib),
            'content_id': next(node.text for node in source.iter() if tag(node) == 'content-id'),
            'uuid': next(node.text for node in source.iter() if tag(node) == 'uuid'),
            'source_order': [tag(node) for node in next(node for node in source if tag(node) == 'metadata')],
        },
        'source_statistics': {
            'translation_blocks': len(blocks), 'non_document_elements': len(list(source.iter())) - 1,
            'identified_nodes': sum(bool(node.get('id')) for node in source.iter()),
            'mathml_trees': counts['math'], 'images': counts['media'], 'figure_wrappers': counts['figure'],
            'tables': counts['table'], 'links': counts['link'], 'footnotes': counts['footnote'],
            'inline_terms': sum(tag(node) == 'term' and bool(node.get('id')) for node in source.iter()),
            'emphasis': counts['emphasis'], 'part_tokens': sum(tag(node) == 'span' and node.get('class') == 'token' for node in source.iter()),
            'all_exercises': counts['exercise'], 'all_supplied_solutions': counts['solution'],
            'section_exercises': len(section_exercises), 'section_supplied_solutions': len(section_solutions),
            'section_missing_solutions': len(absent), 'glossary_definitions': counts['definition'],
        },
        'source_block_keys': [key for key, _ in blocks], 'source_block_templates': templates,
        'source_block_slots': slots,
        'source_ids': [node.get('id') for node in source.iter() if node.get('id')],
        'section_exercise_ids': [node.get('id') for node in section_exercises],
        'section_solution_ids': [node.get('id') for node in section_solutions],
        'section_exercises_without_solutions': absent,
        'images': images, 'source_links': links, 'source_link_labels': labels,
    }
    return raw.replace(b'\r\n', b'\n'), manifest, notices


def prepare(check_only=False):
    excerpt, manifest, notices = inventory()
    outputs = {
        BASE / 'source-excerpts/unit-013.cnxml': excerpt,
        BASE / 'source-excerpts/manifest-013.json': (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode(),
        BASE / 'provenance/unit-013-component-notices.json': (json.dumps(notices, ensure_ascii=False, indent=2) + '\n').encode(),
    }
    for target, data in outputs.items():
        if check_only:
            if target.exists():
                assert target.read_bytes() == data
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                assert target.read_bytes() == data
            else:
                target.write_bytes(data)
    for row in manifest['images']:
        source = COMPONENTS / row['source_path']
        target = BASE / row['path']
        data = source.read_bytes()
        assert digest(data) == row['sha256'] and jpeg_dimensions(data) == (row['width'], row['height'])
        if check_only:
            if target.exists():
                assert target.read_bytes() == data
        else:
            if target.exists():
                assert target.read_bytes() == data
            else:
                target.write_bytes(data)
    print(json.dumps({'unit': 'PNB-013', 'blocks': 353, 'ids': 438, 'math': 254,
                      'images': 24, 'check_only': check_only}, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true')
    prepare(parser.parse_args().check_only)
