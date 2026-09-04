"""Source-derived PNB012 inventory and validated unchanged-asset preparation.

The inventory reads pinned canonical CNXML, never a translation or renderer.
No acquisitions, source edits, rights reassessment or differing-file overwrites.
"""
from pathlib import Path, PurePosixPath
import argparse
import collections
import csv
import hashlib
import io
import json
import re
import xml.etree.ElementTree as ET

from qa_notation import jpeg_dimensions, unique_object

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
CANONICAL = ROOT / 'downloads/upstream/osbooks-college-algebra-bundle/modules/m49304/index.cnxml'
COMPARISON = ROOT / 'downloads/extracted/A30/repo/source/modules/m49304/index.cnxml'
SOURCE_ROOT = ROOT / 'downloads/complete-upstream/osbooks-college-algebra-bundle'
RIGHTS = ROOT / 'downloads/extracted/A30/00_control/COMPONENT_RIGHTS.csv'
RAW_SHA = '0e230c4c96d46e7962dcb3afa1f1630718f7e1cdfae9e665d640690ab6ace19c'
LF_SHA = 'b884c16482dc3cc3bc6f96ebc342ae934863f7aacd5eb39ec73c7a5f6a49f92c'
COMPARISON_SHA = 'a341bb8c05830b95c865b18d64b186fc9a88a08640bbb12f030879faa90b7539'
FIELDS = ['rights_component_id', 'asset_path', 'bytes', 'sha256', 'source_modules',
          'classification', 'admission', 'license_id', 'attribution', 'required_action']


def digest(data):
    return hashlib.sha256(data).hexdigest()


def tag(node):
    return node.tag.rsplit('}', 1)[-1]


def signature(node):
    return node.tag, dict(node.attrib), node.text, tuple((signature(c), c.tail) for c in node)


def safe_path(value):
    p = PurePosixPath(value)
    assert not p.is_absolute() and '..' not in p.parts and '\\' not in value and ':' not in value
    assert p.as_posix() == value
    return p


def source_blocks(source):
    """Return all source-derived translatable owners in original preorder."""
    parent = {c: n for n in source.iter() for c in n}
    blocks = []
    for node in source.iter():
        name, owner, key = tag(node), parent.get(node), None
        if name == 'media':
            key = node.get('id') + '/alt'
        elif name == 'table':
            key = node.get('id') + '/summary'
        elif name == 'title':
            key = ('m49304/title' if owner is source else 'm49304/metadata/title'
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
            rows = [n for n in table.iter() if tag(n) == 'row']
            key = (table.get('id') + '/row/' + str(rows.index(owner) + 1)
                   + '/entry/' + str(list(owner).index(node) + 1))
        if key is not None:
            assert key
            blocks.append((key, node))
    assert len(blocks) == len(set(k for k, _ in blocks)) == 376
    return blocks


def inventory():
    raw, comparison_bytes = CANONICAL.read_bytes(), COMPARISON.read_bytes()
    assert digest(raw) == RAW_SHA and digest(comparison_bytes) == COMPARISON_SHA
    full_lf = raw.replace(b'\r\n', b'\n')
    assert digest(full_lf) == LF_SHA
    source, comparison = ET.fromstring(raw), ET.fromstring(comparison_bytes)
    parent = {c: n for n in source.iter() for c in n}
    paths = {source: 'root'}
    for node in source.iter():
        for index, child in enumerate(node):
            paths[child] = paths[node] + '/' + str(index)
    blocks = source_blocks(source)
    keyed = {n: k for k, n in blocks}
    templates, slots, links, labels = {}, {}, [], {}
    for key, node in blocks:
        counts, groups = collections.Counter(), collections.defaultdict(list)

        def inline(current):
            value = current.text or ''
            for child in current:
                name = tag(child)
                kind = ('math' if name == 'math' else 'link' if name == 'link'
                        else 'term' if name == 'term' else 'child'
                        if child in keyed or name in ('list', 'table', 'media', 'figure') else None)
                if kind:
                    index = counts[kind]
                    counts[kind] += 1
                    groups[kind].append(paths[child])
                    value += '{{' + kind + ':' + str(index) + '}}'
                    if kind == 'link':
                        label_key = key + '/link/' + str(index)
                        label = re.sub(r'\s+', ' ', ''.join(child.itertext())).strip()
                        links.append({'key': label_key, 'attributes': dict(child.attrib),
                                      'text': label, 'path': paths[child]})
                        if label:
                            labels[label_key] = label
                elif name == 'emphasis':
                    wrapper = ('em' if child.get('effect') == 'italics' else 'u'
                               if child.get('effect') == 'underline' else 'strong')
                    value += '<' + wrapper + '>' + inline(child) + '</' + wrapper + '>'
                elif name == 'span' and child.get('class') == 'token':
                    label = {'ⓐ': '(a)', 'ⓑ': '(b)', 'ⓒ': '(c)', 'ⓓ': '(d)'}[child.text]
                    value += '<span class="part" dir="ltr">' + label + '</span>'
                elif name == 'newline':
                    value += '<br />'
                else:
                    raise AssertionError((key, name))
                value += child.tail or ''
            return value

        templates[key] = (node.get('alt') if tag(node) == 'media' else node.get('summary')
                          if tag(node) == 'table' else re.sub(r'\s+', ' ', inline(node)).strip())
        slots[key] = dict(groups)
    assert len(links) == 35
    csv_reader = csv.DictReader(io.StringIO(RIGHTS.read_text(encoding='utf-8-sig')))
    rows = list(csv_reader)
    assert csv_reader.fieldnames == FIELDS
    comparison_media = {n.get('id'): n for n in comparison.iter() if tag(n) == 'media'}
    images, notices = [], []
    for node in source.iter():
        if tag(node) != 'media':
            continue
        assert len(node) == 1 and tag(node[0]) == 'image'
        src = node[0].get('src')
        assert src.startswith('../../media/')
        rel = src[6:]
        assert safe_path(rel).parts[0] == 'media'
        data = (SOURCE_ROOT / rel).read_bytes()
        width, height = jpeg_dimensions(data)
        matching = [row for row in rows if row['asset_path'] == rel]
        assert len(matching) == 1
        row = matching[0]
        assert row['sha256'] == digest(data) and int(row['bytes']) == len(data)
        assert row['admission'] == 'admitted' and row['source_modules'] == 'm49304'
        assert row['classification'] in ('WORK_DEFAULT_UNCREDITED_ART', 'VERIFIED_EIA_PD')
        assert (row['classification'] == 'VERIFIED_EIA_PD') == (node.get('id') == 'fs-id1165135186977')
        notices.append(row)
        compared = (COMPARISON.parent / comparison_media[node.get('id')][0].get('src')).resolve()
        assert compared.is_relative_to((ROOT / 'downloads/extracted/A30/repo/source/media').resolve())
        compared_bytes = compared.read_bytes()
        spec = {'media_id': node.get('id'), 'source_path': rel,
                'path': 'assets/unit-012-' + node.get('id') + '.jpg', 'sha256': digest(data),
                'bytes': len(data), 'width': width, 'height': height,
                'source_mime_type': node[0].get('mime-type'), 'publication_status': 'admitted-unchanged',
                'component_rights_id': row['rights_component_id'],
                'comparison_asset': {'path': compared.relative_to(ROOT).as_posix(),
                                     'sha256': digest(compared_bytes),
                                     'treatment': 'byte-identical original JPEG' if compared_bytes == data
                                     else 'different Indonesian SVG redraw; comparison only, not canonical pixels'}}
        if tag(parent[node]) == 'figure':
            spec['figure_id'] = parent[node].get('id')
        images.append(spec)
    counts = collections.Counter(tag(n) for n in source.iter())
    content = next(n for n in source if tag(n) == 'content')
    metadata = next(n for n in source if tag(n) == 'metadata')
    exercise_section = next(n for n in source.iter() if n.get('id') == 'fs-id1165135176628')
    exercises = [n for n in exercise_section.iter() if tag(n) == 'exercise']
    solutions = [n.get('id') for n in exercise_section.iter() if tag(n) == 'solution']
    absent = [n.get('id') for n in exercises if not any(tag(c) == 'solution' for c in n)]
    manifest = {
        'commit': '789b54099106b071d1d32bfcee454fed72eb4768', 'module': 'm49304',
        'path': 'modules/m49304/index.cnxml',
        'upstream_url': 'https://github.com/openstax/osbooks-college-algebra-bundle',
        'full_module_sha256': LF_SHA, 'unit': 'PNB-012',
        'purpose': 'complete canonical module witness for translation; not training or fine-tuning',
        'source_excerpt': 'unit-012.cnxml', 'selection_ids': [n.get('id') for n in content],
        'next_source_id': None, 'next_module': 'm49306',
        'excerpt_sha256': digest(full_lf if full_lf.endswith(b'\n') else full_lf + b'\n'),
        'source_byte_witnesses': {
            'canonical_checkout_path': CANONICAL.relative_to(ROOT).as_posix(),
            'canonical_checkout_sha256': RAW_SHA,
            'newline_equivalence': 'Complete canonical bytes with CRLF converted to LF'
            + ('' if full_lf.endswith(b'\n') else ' and one final LF appended after the closing document element')
            + '. All XML text, tails, attributes, metadata and source order retained; no synthetic excerpt wrapper.',
            'comparison_path': COMPARISON.relative_to(ROOT).as_posix(), 'comparison_sha256': COMPARISON_SHA},
        'selection_boundary': {
            'method': 'whole module: title, complete metadata with two objectives, nine complete content children including all Section Exercises, then entire three-definition glossary',
            'root_order': [tag(n) for n in source],
            'last_source_id': [n.get('id') for n in source.iter() if n.get('id')][-1],
            'following_module': 'm49306',
            'note': 'Source coverage is not native, educator, visual or whole-book completion. No answers invented for the 31 Section Exercises without source solutions.'},
        'module_metadata': {'root_attributes': dict(source.attrib), 'content_id': 'm49304',
                            'uuid': next(n.text for n in metadata if tag(n) == 'uuid'),
                            'source_order': [tag(n) for n in metadata]},
        'source_statistics': {
            'translation_blocks': 376, 'non_document_elements': len(list(source.iter())) - 1,
            'identified_nodes': sum(bool(n.get('id')) for n in source.iter()),
            'mathml_trees': counts['math'], 'images': counts['media'], 'figure_wrappers': counts['figure'],
            'tables': counts['table'], 'links': counts['link'], 'footnotes': counts['footnote'],
            'inline_terms': sum(tag(n) == 'term' and bool(n.get('id')) for n in source.iter()),
            'emphasis': counts['emphasis'], 'part_tokens': counts['span'],
            'all_exercises': counts['exercise'], 'all_supplied_solutions': counts['solution'],
            'section_exercises': len(exercises), 'section_supplied_solutions': len(solutions),
            'section_missing_solutions': len(absent), 'glossary_definitions': counts['definition']},
        'source_block_keys': [key for key, _ in blocks],
        'source_ids': [n.get('id') for n in source.iter() if n.get('id')],
        'section_exercise_ids': [n.get('id') for n in exercises], 'section_solution_ids': solutions,
        'section_exercises_without_solutions': absent, 'images': images, 'source_links': links,
        'source_notices': 'Exact existing component rows preserved separately; no rights status inferred or overridden by translation.'}
    return {'manifest': manifest, 'notices': notices, 'templates': templates,
            'source_link_labels': labels, 'slots': slots,
            'node_paths': {key: paths[n] for key, n in blocks}}


def prepare(check_only=False):
    facts = inventory()
    manifest_path = BASE / 'source-excerpts/manifest-012.json'
    notice_path = BASE / 'provenance/unit-012-component-notices.json'
    excerpt_path = BASE / 'source-excerpts/unit-012.cnxml'
    snapshots = {p: p.read_bytes() for p in (manifest_path, notice_path, excerpt_path)}
    manifest = json.loads(snapshots[manifest_path], object_pairs_hook=unique_object)
    notices = json.loads(snapshots[notice_path], object_pairs_hook=unique_object)
    assert manifest == facts['manifest'] and notices == facts['notices']
    canonical_lf = CANONICAL.read_bytes().replace(b'\r\n', b'\n')
    assert snapshots[excerpt_path].replace(b'\r\n', b'\n') == canonical_lf + (b'' if canonical_lf.endswith(b'\n') else b'\n')
    assert signature(ET.fromstring(snapshots[excerpt_path])) == signature(ET.fromstring(canonical_lf))
    pending = []
    for spec in manifest['images']:
        destination = (BASE / safe_path(spec['path'])).resolve()
        assert destination.parent == (BASE / 'assets').resolve()
        source = (SOURCE_ROOT / safe_path(spec['source_path'])).resolve()
        assert source.parent == (SOURCE_ROOT / 'media').resolve()
        data = source.read_bytes()
        assert digest(data) == spec['sha256']
        assert not destination.exists() or destination.read_bytes() == data, 'Different existing asset; refusing overwrite'
        pending.append((destination, data))
    assert all(p.read_bytes() == data for p, data in snapshots.items()), 'Inputs changed before copies'
    if not check_only:
        for destination, data in pending:
            destination.parent.mkdir(parents=True, exist_ok=True)
            try:
                with destination.open('xb') as stream:
                    stream.write(data)
            except FileExistsError:
                pass
            assert destination.read_bytes() == data
    return {'unit': 'PNB-012', 'source_images': len(pending), 'publishable_images': len(pending),
            'asset_bytes': sum(len(data) for _, data in pending), 'check_only': check_only}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    print(json.dumps(prepare(args.check_only), sort_keys=True))
