"""Generate the complete A10 evaluation-section translation products.

This dedicated producer avoids changing the shared unit registry while the
section is still an in-progress integration candidate.  It preserves the exact
13-child source boundary, every ID and mathematical tree, and writes a receipt
whose basename cannot be mistaken for an inventoried global build receipt.
"""
import argparse
import copy
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import zipfile

from build import MATH, XML_LANG, translated
from config import DOWNLOADS, LANG, UPSTREAM_COMMIT
from qa import identity
from safe_io import write_bytes

UNIT = 'a10-evaluate-expressions'
MODULE = 'm82453'
SECTION = 'fs-id1170654889475'
PREVIOUS = 'fs-id1170654953465'
NEXT = 'fs-id1170655163482'
NEXT_FIRST = 'fs-id1170655355506'
ID_SHA256 = '2c0b688d569044b128d589579e9ba7d871a0fb9ac7a670ac6f22d0ef2b66e635'
EN_SHA256 = 'a8fdd235aa254c5a0a1248fa858e9b3579d9b40982bbc514cbe6a18c3e6fcbed'
EDITS_SHA256 = '5b6f3dee1956637649814b1b5eb111aaef708b0a9e54fd62100dd1e7b048d874'
SHARED_SHA256 = 'adc145f5957bf18281cd737b9e1079af4d24f6d5505c9485138de3018b2ab5b8'
SOURCE_LOCK_SHA256 = '27259f1bdafac170ec4476192d142a1a7dfbc6da7b238099338f329e955432eb'
RULES_SHA256 = '9b629c2df98b99cca29740fdbcace2c7e9b301bc45f9e88f407a71be44557ab5'
TARGET_TREE_SHA256 = {
    'id-academic': '0d76d191791c6df1efc290e27434429fa289ca829c536ee2007c3573c984f779',
    'jv-academic': 'e85314cf23e35c44def3df1e807d54c83c8e4ed5615e436957aec85b5cbf0c48',
    'jv-conversation': '4249059f26841227ff36325361701ced9a492adeeeadab82206bd1f927740de1',
}
EN_TREE_SHA256 = '4d1eda548937163e0422d09c41a7dc58d449b998d9600016ca3c4e8a86764545'
ASSET_MANIFEST = LANG / f'translation/{UNIT}.assets.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def tree_key(element):
    node = copy.deepcopy(element)
    node.tail = None
    return ET.canonicalize(ET.tostring(node, encoding='unicode'), strip_text=True, rewrite_prefixes=True)


def select(document_raw):
    document = ET.fromstring(document_raw)
    parents = {id(child): parent for parent in document.iter() for child in parent}
    section = next(node for node in document.iter() if node.get('id') == SECTION)
    parent = parents[id(section)]
    index = list(parent).index(section)
    assert parent[index - 1].get('id') == PREVIOUS
    assert parent[index + 1].get('id') == NEXT
    assert next(node for node in parent[index + 1].iter() if node.get('id')).get('id') == NEXT
    assert parent[index + 1][1].get('id') == NEXT_FIRST
    result = copy.deepcopy(section)
    result.tail = None
    return result


def merged_edits():
    unit = json.loads((LANG / f'translation/{UNIT}.edits.json').read_text(encoding='utf-8'))
    shared = json.loads((LANG / 'translation/phrases.json').read_text(encoding='utf-8'))
    rows = {row[0]: row for row in shared['phrases']}
    for row in unit['phrases']:
        assert row[0] not in rows or rows[row[0]] == row, 'Conflicting shared phrase'
        rows[row[0]] = row
    unit['phrases'] = list(rows.values())
    unit['unchanged_identifiers'] = sorted(set(unit['unchanged_identifiers'] + shared['unchanged_identifiers']))
    return unit


def count_parts(root):
    return sum((node.text or '').count('ⓐ') + (node.text or '').count('ⓑ')
               for node in root.iter())


def validate_source(source, english, rules):
    ids = [node.get('id') for node in source.iter() if node.get('id')]
    assert ids == rules['scope']['source_section_ids'] and len(ids) == len(set(ids)) == 83
    assert len(source) == 13 and source[0].tag.endswith('}title')
    assert source[1].get('id') == 'fs-id1170654968998'
    assert source[-1].get('id') == 'fs-id1170655197213'
    assert ids[-1] == 'fs-id1170655106384'
    assert [node.get('id') for node in english.iter() if node.get('id')] == ids
    assert sha(tree_key(source).encode()) == TARGET_TREE_SHA256['id-academic']
    assert sha(tree_key(english).encode()) == EN_TREE_SHA256
    assert len(list(source.iter('{' + MATH + '}math'))) == 38
    assert len(list(source.iter('{' + MATH + '}msup'))) == 12
    assert sum(node.tag.endswith('}mtext') and node.text == 'x' for node in source.iter()) == 1
    tables = source.findall('.//{*}table')
    assert len(tables) == 5
    assert sum(len(table.findall('.//{*}tbody/{*}row')) for table in tables) == 21
    assert all(table.find('.//{*}thead') is None for table in tables)
    assert [len(table.findall('.//{*}tbody/{*}row')) for table in tables] == [4, 4, 4, 4, 5]
    assert len(source.findall('.//{*}media')) == 16
    assert len(source.findall('.//{*}exercise')) == 9
    assert len(source.findall('.//{*}solution')) == 9
    assert count_parts(source) == 24
    assert not source.findall('.//{*}link')
    for left, right in zip(source.iter('{' + MATH + '}math'), english.iter('{' + MATH + '}math')):
        assert tree_key(left) == tree_key(right), 'ID/EN MathML differs'


def validate_target(source, target, track):
    assert identity(source) == identity(target)
    assert target.get(XML_LANG) == 'jv-Latn-ID'
    assert sha(tree_key(target).encode()) == TARGET_TREE_SHA256[track]
    for left, right in zip(source.iter(), target.iter()):
        if left.tag.startswith('{' + MATH + '}'):
            assert left.tag == right.tag and left.attrib == right.attrib
            if not left.tag.endswith('}mtext'):
                assert left.text == right.text
            else:
                assert left.text == right.text == 'x'
        pairs = [(left.text or '', right.text or ''), (left.tail or '', right.tail or '')]
        pairs += [(left.get(name, ''), right.get(name, '')) for name in ('alt', 'aria-label', 'summary')]
        for original, translation in pairs:
            assert re.findall(r'\d+(?:\.\d+)?', original) == re.findall(r'\d+(?:\.\d+)?', translation)
    assert count_parts(target) == 24


def products():
    edits_path = LANG / f'translation/{UNIT}.edits.json'
    shared_path = LANG / 'translation/phrases.json'
    rules_path = LANG / f'audio/{UNIT}.rules.json'
    assert sha(edits_path.read_bytes()) == EDITS_SHA256
    assert sha(shared_path.read_bytes()) == SHARED_SHA256
    assert sha((LANG / 'sources.lock.json').read_bytes()) == SOURCE_LOCK_SHA256
    assert sha(rules_path.read_bytes()) == RULES_SHA256
    assert ASSET_MANIFEST.is_file()
    rules = json.loads(rules_path.read_text(encoding='utf-8'))
    with zipfile.ZipFile(DOWNLOADS / 'a10-source.zip') as archive:
        id_raw = archive.read(f'translated/modules/{MODULE}/index.cnxml')
    with zipfile.ZipFile(DOWNLOADS / 'openstax-full-pinned.zip') as archive:
        en_raw = archive.read(f'osbooks-prealgebra-bundle-{UPSTREAM_COMMIT}/modules/{MODULE}/index.cnxml')
    assert sha(id_raw) == ID_SHA256 and sha(en_raw) == EN_SHA256
    source, english = select(id_raw), select(en_raw)
    validate_source(source, english, rules)
    edits = merged_edits()
    generated, variants = {}, {}
    for track in ('id-academic', 'jv-academic', 'jv-conversation'):
        variant = copy.deepcopy(source) if track == 'id-academic' else translated(source, track, edits)
        if track.startswith('jv'):
            validate_target(source, variant, track)
        variants[track] = variant
        generated[f'translation/{UNIT}.{track}.cnxml'] = (
            ET.tostring(variant, encoding='utf-8', xml_declaration=True) + b'\n')
    generated[f'provenance/{UNIT}.en.cnxml'] = (
        ET.tostring(english, encoding='utf-8', xml_declaration=True) + b'\n')
    receipt = {
        'schema': 'source-bound-unit-production-draft-v1',
        'status': 'complete_section_translation_and_assets_reader_in_progress',
        'unit': UNIT, 'program': 'A10', 'module': MODULE, 'section': SECTION,
        'scope': 'Complete 13-child evaluation section only; next like-terms section excluded.',
        'source_ids': 83, 'source_mathml': 38, 'source_tables': 5,
        'source_table_rows': 21, 'source_media': 16, 'source_exercises': 9,
        'source_solutions': 9, 'question_parts': 15,
        'previous_section': PREVIOUS, 'next_excluded_section': NEXT,
        'indonesian_module_sha256': ID_SHA256, 'english_module_sha256': EN_SHA256,
        'indonesian_section_canonical_sha256': TARGET_TREE_SHA256['id-academic'],
        'english_section_canonical_sha256': EN_TREE_SHA256,
        'target_section_canonical_sha256': TARGET_TREE_SHA256,
        'edits_sha256': EDITS_SHA256, 'shared_edits_sha256': SHARED_SHA256,
        'rules_sha256': RULES_SHA256,
        'asset_manifest_sha256': sha(ASSET_MANIFEST.read_bytes()),
        'checks': [
            'exact_source_module_and_section_hashes', 'complete_ordered_83_ids',
            'exact_38_mathml_trees_and_mtext_x', 'five_headerless_tables_21_rows',
            'sixteen_media_references', 'nine_exercises_nine_solutions',
            'all_numeric_text_and_attributes_preserved', 'next_section_excluded',
        ],
        'files': {path: sha(raw) for path, raw in generated.items()},
        'reader': 'in_progress', 'narration_ssml': 'in_progress',
        'human_language_review': False, 'whole_module_complete': False,
    }
    generated[f'qa/{UNIT}.production-draft.in-progress.json'] = (
        json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode()
    return generated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    generated = products()
    assert generated == products()
    for path, raw in generated.items():
        if args.check:
            assert (LANG / path).read_bytes() == raw, path
        else:
            write_bytes(LANG / path, raw)
    print('Complete evaluation section drafted in three tracks; reader/narration integration remains in progress.')


if __name__ == '__main__':
    main()
