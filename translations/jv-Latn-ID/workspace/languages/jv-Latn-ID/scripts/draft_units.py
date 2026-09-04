"""Produce source-bound next-unit CNXML drafts without rerunning acquisition.

These drafts are not yet offline-reader or narration completion. Every text edit
is explicit; source IDs, numeric facts and mathematical tokens are invariant.
"""
import argparse
import copy
import hashlib
import json
import os
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from build import MATH, XML_LANG, translated
from config import LANG, DOWNLOADS
from qa import identity
from safe_io import write_bytes

UNITS = {
    'a00-rounding': {
        'program': 'A00', 'module': 'm81243', 'section': 'fs-id2472737',
        'slice': None,
        'scope': 'Entire rounding section: all nine exercises/solutions, five tables, 23 figures and original external learning-resource links; later exercises, summary and glossary remain outside this unit.',
    },
    'a00-section-exercises': {
        'program': 'A00', 'module': 'm81243', 'section': 'fs-id2279009',
        'slice': None,
        'scope': 'Entire final section: all four nested subsections, 58 exercises, 29 supplied and 29 absent solutions, four model images, and the complete six-row self-check. The section has no direct title; no wrapper title or answer is invented.',
    },
    'a00-place-value': {
        'program': 'A00', 'module': 'm81243', 'section': 'fs-id2340048',
        'slice': None, 'scope': 'Entire place-value modeling section; no remainder of m81243 implied.',
    },
    'a00-digit-place': {
        'program': 'A00', 'module': 'm81243', 'section': 'fs-id1883656',
        'slice': None,
        'scope': 'Entire identifying-digit-place-value section; no later section or remainder of m81243 implied.',
    },
    'a00-name-whole': {
        'program': 'A00', 'module': 'm81243', 'section': 'fs-id1321580',
        'slice': None,
        'scope': 'Entire using-place-value-to-name-whole-numbers section, including both worked examples and four practices; no remainder of m81243 implied.',
    },
    'a00-write-whole': {
        'program': 'A00', 'module': 'm81243', 'section': 'fs-id1339359',
        'slice': None,
        'scope': 'Entire using-place-value-to-write-whole-numbers section, all three charts, two worked examples and four practices; no rounding or remainder of m81243 implied.',
    },
    'a10-operation-symbols': {
        'program': 'A10', 'module': 'm82453', 'section': 'fs-id1170655150800',
        'slice': [7, 13],
        'scope': 'Original section title as context plus source children [7:13]; operation introduction, table, examples, and multiplication-cross warning only.',
    },
    'a10-equality-symbols': {
        'program': 'A10', 'module': 'm82453', 'section': 'fs-id1170655150800',
        'slice': [13, 23],
        'scope': 'Original section title as context plus source children [13:23]; spacing node, equality/inequality definitions, number-line relations, notation, and examples only.',
    },
    'a10-grouping-symbols': {
        'program': 'A10', 'module': 'm82453', 'section': 'fs-id1170655150800',
        'slice': [23, 28],
        'scope': 'Original section title as context plus source children [23:28]; all three grouping-symbol types and nested examples, including trailing layout space; no later expression/equation lesson implied.',
    },
    'a10-expressions-equations': {
        'program': 'A10', 'module': 'm82453', 'section': 'fs-id1170655150800',
        'slice': [28, 40],
        'scope': 'Original section title as context plus complete expression/equation children [28:40], three tables and all eight classifications; stops before the formal exponent introduction.',
    },
    'a10-exponents': {
        'program': 'A10', 'module': 'm82453', 'section': 'fs-id1170655150800',
        'slice': [40, 53],
        'scope': 'Original section title plus the entire remaining exponent lesson [40:53], two diagrams, both tables, worked example and four practice answers; no order-of-operations or whole-module completion implied.',
    },
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pinned_blob(repo, path):
    environment = dict(os.environ, GIT_NO_LAZY_FETCH='1', GIT_OPTIONAL_LOCKS='0')
    return subprocess.check_output(['git', '-C', str(DOWNLOADS / repo['name']),
                                    'show', f"{repo['commit']}:{path}"], env=environment)


def select(raw, descriptor):
    document = ET.fromstring(raw)
    section = next(node for node in document.iter() if node.get('id') == descriptor['section'])
    selected = copy.deepcopy(section)
    if descriptor['slice'] is not None:
        start, end = descriptor['slice']
        assert section[0].tag.endswith('}title') and start > 0 and end <= len(section)
        selected[:] = [copy.deepcopy(section[0])] + [copy.deepcopy(node) for node in section[start:end]]
    selected.tail = None
    return selected


def validate(source, target):
    assert identity(source) == identity(target), 'Source structure or IDs changed'
    ids = [node.get('id') for node in source.iter() if node.get('id')]
    assert len(ids) == len(set(ids)), 'Duplicate source ID'
    assert all(node.get('target-id') in ids for node in source.iter() if node.get('target-id')), 'Unresolved in-unit reference'
    for left, right in zip(source.iter(), target.iter()):
        if left.tag.startswith('{' + MATH + '}'):
            assert left.attrib == right.attrib, 'MathML attributes changed'
            if not left.tag.endswith('}mtext'):
                assert left.text == right.text, 'Non-prose mathematical token changed'
            elif not re.search('[A-Za-z]', left.text or ''):
                assert left.text == right.text, 'Nonlinguistic mtext token changed'
        for value_left, value_right in [(left.text or '', right.text or ''),
                                        (left.tail or '', right.tail or '')] + [
                (left.get(attr, ''), right.get(attr, '')) for attr in ('alt', 'aria-label', 'summary')]:
            assert re.findall(r'\d+(?:\.\d+)?', value_left) == re.findall(r'\d+(?:\.\d+)?', value_right), 'Numeric fact changed'
    assert target.get(XML_LANG) == 'jv-Latn-ID'


def merged_edits(key):
    edits = json.loads((LANG / f'translation/{key}.edits.json').read_text(encoding='utf-8'))
    shared = json.loads((LANG / 'translation/phrases.json').read_text(encoding='utf-8'))
    shared_rows = {row[0]: row for row in shared['phrases']}
    for row in edits['phrases']:
        assert row[0] not in shared_rows or shared_rows[row[0]] == row, f'Undeclared shared-phrase conflict: {row[0]}'
        shared_rows[row[0]] = row
    edits['phrases'] = list(shared_rows.values())
    edits['unchanged_identifiers'] = sorted(set(shared['unchanged_identifiers'] + edits['unchanged_identifiers']))
    return edits


def products(key):
    descriptor = UNITS[key]
    lock = json.loads((LANG / 'sources.lock.json').read_text(encoding='utf-8'))
    repositories = {repo['name']: repo for repo in lock['repositories']}
    path = f"modules/{descriptor['module']}/index.cnxml"
    english = pinned_blob(repositories['openstax-prealgebra-bundle'], path)
    if descriptor['program'] == 'A00':
        indonesian = pinned_blob(repositories['a00-id'], path)
    else:
        with zipfile.ZipFile(DOWNLOADS / 'a10-source.zip') as archive:
            indonesian = archive.read('translated/' + path)
    witness = next(unit for unit in lock['units'] if unit['module'] == descriptor['module'])
    assert sha(english) == witness['upstream_module_sha256']
    assert sha(indonesian) == witness['indonesian_module_sha256']
    source = select(indonesian, descriptor)
    edits_path = LANG / f'translation/{key}.edits.json'
    shared_path = LANG / 'translation/phrases.json'
    edits = merged_edits(key)
    generated = {}
    for track in ('id-academic', 'jv-academic', 'jv-conversation'):
        variant = source if track == 'id-academic' else translated(source, track, edits)
        if track != 'id-academic':
            validate(source, variant)
        generated[f'translation/{key}.{track}.cnxml'] = ET.tostring(variant, encoding='utf-8', xml_declaration=True) + b'\n'
    generated[f'provenance/{key}.en.cnxml'] = ET.tostring(select(english, descriptor), encoding='utf-8', xml_declaration=True) + b'\n'
    next_ids = [node.get('id') for node in source if node.get('id')]
    receipt = {
        'schema': 'source-bound-unit-draft-v1', 'status': 'translation_draft_only',
        'unit': key, **descriptor, 'included_direct_child_ids': next_ids,
        'source_ids': [node.get('id') for node in source.iter() if node.get('id')],
        'indonesian_module_sha256': sha(indonesian), 'english_module_sha256': sha(english),
        'edits_sha256': sha(edits_path.read_bytes()),
        'shared_edits_sha256': sha(shared_path.read_bytes()),
        'files': {path: sha(raw) for path, raw in generated.items()},
        'checks': ['source_module_hashes', 'exact_phrase_coverage', 'source_structure_and_ids',
                   'in_unit_cross_references', 'mathematical_tokens_and_attributes', 'numeric_text_and_alt_facts'],
        'offline_reader': 'pending_integration', 'narration_ssml': 'pending_integration',
        'human_review': 'pending', 'full_module_complete': False,
    }
    generated[f'qa/{key}.draft-receipt.json'] = (json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode()
    return generated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--unit', required=True, choices=UNITS)
    parser.add_argument('--check', action='store_true')
    arguments = parser.parse_args()
    generated = products(arguments.unit)
    for path, raw in generated.items():
        if arguments.check:
            assert (LANG / path).read_bytes() == raw, f'Stale unit draft: {path}'
        else:
            write_bytes(LANG / path, raw)
    print(f'{arguments.unit}: source-bound three-track draft validated; reader/narration integration pending.')


if __name__ == '__main__':
    main()
