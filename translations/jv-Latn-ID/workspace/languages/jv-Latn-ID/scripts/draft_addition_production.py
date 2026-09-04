"""Generate the complete, source-bound three-track m81244 addition CNXML.

This producer is deliberately specific to the pinned complete module.  It
performs exact phrase-ledger replay and accepts only the registered
fs-id2263429 alt correction after also checking the bound image bytes.
"""
import argparse
import copy
import hashlib
import json
import re
import xml.etree.ElementTree as ET

from build import MATH, XML_LANG, translated
from build_units import tree_key
from config import LANG, TRACKS
from safe_io import write_bytes


UNIT = 'a00-add-whole'
MODULE = 'm81244'
RULES_PATH = LANG / f'audio/{UNIT}.rules.json'
EDITS_PATH = LANG / f'translation/{UNIT}.edits.json'
ID_PATH = LANG.parent.parent / 'downloads/jv-Latn-ID/a00-id/modules/m81244/index.cnxml'
EN_PATH = (LANG.parent.parent /
           'downloads/jv-Latn-ID/a00-id/provenance/logbook/authority/prealgebra2e/m81244.source.cnxml')
ID_SHA256 = 'd23343f302c34436169e88ffdbc4eab37baabf0a3d1134755b2f5676c75e1cc6'
EN_SHA256 = 'b32058ce714e5fd43b010ccc81b2ae00a11567b229e9f96dda7b85b3cd82ba6b'
RULES_SHA256 = 'a3146c9e6142adfaf146a96ae1ef21e5599092ec23c25b45b8a6a37bdbebe98f'
EDITS_SHA256 = 'd5c0c31ca0967cab5c48277a4662d6b28cafff663d6ef6ddee9d7fe4e9c73442'
CORRECTED_MEDIA_ID = 'fs-id2263429'
CORRECTED_ASSET_SHA256 = '86eabdbd452417939156e6a0c3cd2207f502b331eb02c521a7b0ecc8a9a54690'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def node_at(root, path):
    node = root
    for index in path:
        node = node[index]
    return node


def numeric_surfaces(root):
    """Return path/slot/digits for linguistic surfaces, not MathML tokens."""
    result = {}

    def walk(node, path):
        if not node.tag.startswith('{' + MATH + '}'):
            for slot, value in [('text', node.text), ('tail', node.tail)]:
                if value and re.search(r'\d', value):
                    result[(tuple(path), slot)] = (node, value, re.findall(r'\d+', value))
            for slot in ('alt', 'aria-label', 'summary'):
                value = node.get(slot)
                if value and re.search(r'\d', value):
                    result[(tuple(path), slot)] = (node, value, re.findall(r'\d+', value))
        for index, child in enumerate(node):
            walk(child, path + [index])

    walk(root, [])
    return result


def validate_numeric_exception(source, target, track, edits, rules):
    source_values, target_values = numeric_surfaces(source), numeric_surfaces(target)
    if set(source_values) != set(target_values):
        raise ValueError('Numeric linguistic surface paths changed')
    changes = []
    for key in source_values:
        source_node, old, old_digits = source_values[key]
        target_node, new, new_digits = target_values[key]
        if old_digits != new_digits:
            changes.append((key, source_node, target_node, old, new, old_digits, new_digits))
    if len(changes) != 1:
        raise ValueError(f'Expected one scoped numeric surface change for {track}, got {len(changes)}')
    (path_slot, source_node, target_node, old, _new, old_digits, new_digits), = changes
    path, slot = path_slot
    exception = edits['source_bound_attribute_exceptions'][0]
    rule_exception = rules['matching_contract']['numeric_exception'][0]
    if exception != rule_exception:
        raise ValueError('Edit/rule numeric exception registration differs')
    if (source_node is not node_at(source, path) or target_node is not node_at(target, path)
            or source_node.get('id') != CORRECTED_MEDIA_ID
            or target_node.get('id') != CORRECTED_MEDIA_ID
            or slot != exception['attribute'] or old != exception['source_phrase']
            or old_digits != exception['source_numbers'] or new_digits != exception['target_numbers']):
        raise ValueError('Numeric exception escaped its exact source ID/attribute/old phrase')
    image = source_node.find('{*}image')
    if image is None or image.get('src') != '../../media/CNX_BMath_Figure_01_02_222.jpg':
        raise ValueError('Numeric exception image reference changed')
    asset = LANG.parent.parent / 'downloads/jv-Latn-ID/a00-id/media/CNX_BMath_Figure_01_02_222.jpg'
    if sha(asset.read_bytes()) != CORRECTED_ASSET_SHA256:
        raise ValueError('Numeric exception image bytes changed')


def validate(source, target, track, edits, rules):
    if track not in TRACKS:
        raise ValueError('Unknown addition track')
    if len(source) != len(target) or [x.tag for x in source.iter()] != [x.tag for x in target.iter()]:
        raise ValueError('Complete module hierarchy changed')
    source_ids = [node.get('id') for node in source.iter() if node.get('id')]
    target_ids = [node.get('id') for node in target.iter() if node.get('id')]
    if source_ids != target_ids or source_ids != rules['ordered_source_ids']:
        raise ValueError('Source ID order changed')
    if len(source_ids) != 756 or len(set(source_ids)) != 756:
        raise ValueError('Source ID census changed')
    manifest = rules['structural_manifest']
    if [(row['id'], row['tag'], row['source_path']) for row in manifest] != [
            (node.get('id'), node.tag, list(path))
            for path, node in id_paths(source)]:
        raise ValueError('Structural manifest no longer matches pinned source')
    for source_node, target_node in zip(source.iter(), target.iter()):
        for key, value in source_node.attrib.items():
            if key not in ('alt', 'aria-label', 'summary', XML_LANG) and target_node.get(key) != value:
                raise ValueError(f'Nonlinguistic attribute changed: {key}')
    if len(list(source.iter('{' + MATH + '}math'))) != 401:
        raise ValueError('MathML census changed')
    if len(source.findall('.//{*}media')) != 50 or len(source.findall('.//{*}table')) != 21:
        raise ValueError('Media/table census changed')
    if len(source.findall('.//{*}exercise')) != 129 or len(source.findall('.//{*}solution')) != 89:
        raise ValueError('Exercise/solution census changed')
    if sum(node.find('{*}title') is None for node in source.findall('.//{*}solution')) != 74:
        raise ValueError('Untitled solution census changed')
    if len(list(source.iter('{' + MATH + '}mover'))) != 25 or len(list(source.iter('{' + MATH + '}munder'))) != 17:
        raise ValueError('Carry/underline MathML census changed')
    if track == 'id-academic':
        if tree_key(source) != tree_key(target):
            raise ValueError('Indonesian track is not an exact tree replay')
    else:
        if target.get(XML_LANG) != 'jv-Latn-ID':
            raise ValueError('Javanese root locale missing')
        replay = translated(source, track, edits)
        if tree_key(target) != tree_key(replay):
            raise ValueError('Target differs from exact phrase-ledger replay')
        validate_numeric_exception(source, target, track, edits, rules)
    expected_hash = rules['scope']['target_module_tree_sha256'][track]
    if sha(tree_key(target).encode()) != expected_hash:
        raise ValueError('Target canonical tree hash changed')
    return source_ids


def id_paths(root):
    result = []

    def walk(node, path):
        if node.get('id'):
            result.append((tuple(path), node))
        for index, child in enumerate(node):
            walk(child, path + (index,))

    walk(root, ())
    return result


def products():
    id_raw, en_raw = ID_PATH.read_bytes(), EN_PATH.read_bytes()
    rules_raw, edits_raw = RULES_PATH.read_bytes(), EDITS_PATH.read_bytes()
    if (len(id_raw), sha(id_raw), len(en_raw), sha(en_raw)) != (
            123306, ID_SHA256, 119141, EN_SHA256):
        raise ValueError('Pinned addition source bytes changed')
    if sha(rules_raw) != RULES_SHA256 or sha(edits_raw) != EDITS_SHA256:
        raise ValueError('Addition AX-2 handoff changed')
    rules, edits = json.loads(rules_raw), json.loads(edits_raw)
    if (rules['scope']['module'], edits['source_module'], edits['tracks']) != (
            MODULE, MODULE, ['jv-academic', 'jv-conversation']):
        raise ValueError('Unexpected addition handoff scope')
    source, english = ET.fromstring(id_raw), ET.fromstring(en_raw)
    if [node.tag.rsplit('}', 1)[-1] for node in source] != ['title', 'metadata', 'content', 'glossary']:
        raise ValueError('Complete module root structure changed')
    if sha(tree_key(source).encode()) != rules['scope']['source_module_tree_sha256']:
        raise ValueError('Indonesian canonical source tree changed')
    if sha(tree_key(english).encode()) != rules['scope']['english_module_tree_sha256']:
        raise ValueError('English canonical source tree changed')
    variants = {'id-academic': copy.deepcopy(source)}
    for track in ('jv-academic', 'jv-conversation'):
        variants[track] = translated(source, track, edits)
    source_ids = None
    generated = {}
    for track in TRACKS:
        ids = validate(source, variants[track], track, edits, rules)
        source_ids = ids if source_ids is None else source_ids
        if ids != source_ids:
            raise ValueError('Track ID order mismatch')
        raw = (id_raw if track == 'id-academic' else
               ET.tostring(variants[track], encoding='utf-8', xml_declaration=True) + b'\n')
        generated[f'translation/{UNIT}.{track}.cnxml'] = raw
    generated[f'provenance/{UNIT}.en.cnxml'] = en_raw
    receipt = {
        'schema': 'jv-addition-source-bound-cnxml-v1',
        'status': 'complete_source_scope_generated_production_review_pending',
        'unit': UNIT, 'program': 'A00', 'module': MODULE,
        'source_pins': {
            'indonesian': {'commit': rules['scope']['indonesian_commit'],
                           'blob': rules['scope']['indonesian_blob'], 'sha256': ID_SHA256,
                           'bytes': len(id_raw)},
            'english': {'commit': rules['scope']['english_commit'],
                        'blob': rules['scope']['english_blob'], 'sha256': EN_SHA256,
                        'bytes': len(en_raw)},
        },
        'handoff_sha256': {'rules': RULES_SHA256, 'edits': EDITS_SHA256},
        'counts': dict(rules['scope']['counts']),
        'target_canonical_tree_sha256': dict(rules['scope']['target_module_tree_sha256']),
        'numeric_exception': {
            'count': 1, 'element_id': CORRECTED_MEDIA_ID, 'attribute': 'alt',
            'source_asset_sha256': CORRECTED_ASSET_SHA256,
            'generic_numeric_bypass': False,
        },
        'complete_source_scope': True,
        'whole_assignment_complete': False,
        'human_language_review': 'pending',
        'screen_reader_review': 'pending',
        'synthesized_audio_files': 0,
        'content_files': {path: sha(raw) for path, raw in sorted(generated.items())},
        'checks': [
            'exact_ID_and_EN_source_bytes_and_tree_pins',
            'exact_phrase_ledger_replay_for_both_Javanese_tracks',
            'all_756_unique_IDs_in_source_order', 'all_401_MathML_roots',
            '50_media_21_tables_129_exercises_89_supplied_40_absent_solutions',
            '74_untitled_solution_boundaries', '25_mover_and_17_munder_nodes',
            'single_exact_ID_attribute_old_phrase_and_asset_hash_numeric_exception',
        ],
    }
    generated[f'qa/{UNIT}.in-progress.json'] = (
        json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    return generated


def verify_saved(generated=None):
    generated = products() if generated is None else generated
    for path, raw in generated.items():
        if (LANG / path).read_bytes() != raw:
            raise ValueError('Stale addition draft product: ' + path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    generated = products()
    if generated != products():
        raise ValueError('Nondeterministic addition CNXML generation')
    if args.check:
        verify_saved(generated)
    else:
        for path, raw in generated.items():
            write_bytes(LANG / path, raw)
    print(('Checked' if args.check else 'Generated') +
          ' complete m81244 CNXML in three tracks plus exact English provenance.')


if __name__ == '__main__':
    main()
