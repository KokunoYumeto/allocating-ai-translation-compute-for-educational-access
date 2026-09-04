"""Build the complete, source-bound m81245 translation trees.

The existing edit and AX-2 ledgers are immutable inputs.  Two independently
verified target-only media-alt repairs are applied here through exact media
ID, source path, old alt, source ref, and image-hash bindings.
"""
import argparse
import copy
import hashlib
import json
import xml.etree.ElementTree as ET

from build import CN, MATH, translated
from build_units import tree_key
from config import LANG
from draft_units import merged_edits, pinned_blob
from safe_io import write_bytes


UNIT = 'a00-subtract-whole'
TRACKS = ('id-academic', 'jv-academic', 'jv-conversation')
CORRECTION_IDS = ('fs-id2425624', 'fs-id2643011')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def at(root, path):
    node = root
    for index in path:
        node = node[index]
    return node


def canonical_sha(node):
    return sha(tree_key(node).encode())


def source_blobs():
    lock = json.loads((LANG / 'sources.lock.json').read_text(encoding='utf-8'))
    repos = {row['name']: row for row in lock['repositories']}
    path = 'modules/m81245/index.cnxml'
    return (
        pinned_blob(repos['a00-id'], path),
        pinned_blob(repos['openstax-prealgebra-bundle'], path),
    )


def correction_contract(rules, assets):
    charts = {row['media_id']: row for row in rules['chart_fixtures']}
    asset_rows = {row['media_id']: row for row in assets['assets']}
    result = []
    for media_id in CORRECTION_IDS:
        chart = charts[media_id]
        asset = asset_rows[media_id]
        assert chart['source_path'] == asset['source_path']
        assert chart['source_ref'] == asset['source_src']
        assert chart['sha256'] == asset['source_sha256']
        assert chart['source_alt'] == asset['source_alt']
        assert chart['source_alt_discrepancy']['state'].endswith(
            'narrow alt edit pending root integration')
        result.append({
            'media_id': media_id,
            'source_path': chart['source_path'],
            'source_ref': chart['source_ref'],
            'image_sha256': chart['sha256'],
            'old_source_alt': chart['source_alt'],
            'old_target_alt': {
                track: chart['target_alt'][track]
                for track in TRACKS if track.startswith('jv')
            },
            'corrected_target_alt': {
                track: chart['independent_expected_reading'][track]
                for track in TRACKS if track.startswith('jv')
            },
            'id_academic_policy': 'exact_pivot_alt_retained; corrected independent narration supplies the accessibility warning',
        })
    return result


def apply_corrections(source, target, track, contract, asset_manifest):
    if track == 'id-academic':
        return
    asset_rows = {row['media_id']: row for row in asset_manifest['assets']}
    for row in contract:
        source_node = at(source, row['source_path'])
        target_node = at(target, row['source_path'])
        assert source_node.get('id') == target_node.get('id') == row['media_id']
        assert source_node.get('alt') == row['old_source_alt']
        assert target_node.get('alt') == row['old_target_alt'][track]
        source_image = source_node.find('{*}image')
        target_image = target_node.find('{*}image')
        assert source_image is not None and target_image is not None
        assert source_image.get('src') == target_image.get('src') == row['source_ref']
        output = asset_rows[row['media_id']]['outputs'][track]
        raw = (LANG / output['path']).read_bytes()
        assert sha(raw) == output['sha256'] == row['image_sha256']
        target_node.set('alt', row['corrected_target_alt'][track])


def validate_counts(source, rules):
    scope = rules['scope']
    ids = [node.get('id') for node in source.iter() if node.get('id')]
    assert len(ids) == len(set(ids)) == scope['source_id_count'] == 716
    assert len(list(source.iter('{' + MATH + '}math'))) == scope['source_mathml_count'] == 262
    assert len(list(source.iter('{' + CN + '}media'))) == scope['source_media'] == 55
    assert len(list(source.iter('{' + CN + '}table'))) == scope['source_tables'] == 17
    exercises = list(source.iter('{' + CN + '}exercise'))
    solutions = list(source.iter('{' + CN + '}solution'))
    assert len(exercises) == scope['source_exercises'] == 125
    assert len(solutions) == scope['source_solutions'] == 83
    assert len(exercises) - len(solutions) == scope['source_missing_answers'] == 42
    assert len(list(source.iter('{' + CN + '}link'))) == scope['source_links'] == 6
    return ids


def products():
    rules_path = LANG / f'audio/{UNIT}.rules.json'
    assets_path = LANG / f'translation/{UNIT}.assets.json'
    edits_path = LANG / f'translation/{UNIT}.edits.json'
    shared_path = LANG / 'translation/phrases.json'
    source_lock_path = LANG / 'sources.lock.json'
    rules = json.loads(rules_path.read_text(encoding='utf-8'))
    assets = json.loads(assets_path.read_text(encoding='utf-8'))
    scope = rules['scope']
    assert scope['unit'] == UNIT and scope['module'] == 'm81245'
    assert scope['complete_module_source'] is True
    assert sha(rules_path.read_bytes()) == assets['rules_sha256']
    assert sha(edits_path.read_bytes()) == scope['edits_sha256']
    assert sha(shared_path.read_bytes()) == scope['shared_edits_sha256']
    assert sha(source_lock_path.read_bytes()) == scope['source_lock_sha256']

    indonesian_raw, english_raw = source_blobs()
    assert sha(indonesian_raw) == scope['indonesian_sha256']
    assert sha(english_raw) == scope['english_sha256']
    source = ET.fromstring(indonesian_raw)
    english = ET.fromstring(english_raw)
    assert canonical_sha(source) == scope['indonesian_module_canonical_sha256']
    assert canonical_sha(english) == scope['english_module_canonical_sha256']
    source_ids = validate_counts(source, rules)
    assert [node.get('id') for node in english.iter() if node.get('id')] == source_ids

    edits = merged_edits(UNIT)
    contract = correction_contract(rules, assets)
    variants = {'id-academic': copy.deepcopy(source)}
    for track in TRACKS[1:]:
        base = translated(source, track, edits)
        assert canonical_sha(base) == scope['target_module_canonical_sha256'][track]
        variants[track] = base
        apply_corrections(source, variants[track], track, contract, assets)

    generated = {}
    for track, root in variants.items():
        raw = ET.tostring(root, encoding='utf-8', xml_declaration=True) + b'\n'
        generated[f'translation/{UNIT}.{track}.cnxml'] = raw
    generated[f'provenance/{UNIT}.en.cnxml'] = (
        ET.tostring(english, encoding='utf-8', xml_declaration=True) + b'\n')

    receipt = {
        'schema': 'source-bound-complete-module-draft-v1',
        'status': 'complete_source_translation_structural_pass_production_build_pending',
        'unit': UNIT,
        'module': 'm81245',
        'complete_module_source': True,
        'full_assignment_complete': False,
        'source_pins': {
            'indonesian_sha256': sha(indonesian_raw),
            'english_sha256': sha(english_raw),
            'indonesian_git_blob': scope['indonesian_git_blob'],
            'english_git_blob': scope['english_git_blob'],
        },
        'counts': {
            'ids': 716, 'mathml': 262, 'media': 55, 'tables': 17,
            'exercises': 125, 'supplied_solutions': 83,
            'absent_solutions': 42, 'references': 6,
        },
        'base_target_canonical_sha256': scope['target_module_canonical_sha256'],
        'corrected_target_canonical_sha256': {
            track: canonical_sha(root) for track, root in variants.items()
        },
        'accessibility_corrections': contract,
        'correction_count': 2,
        'input_sha256': {
            'edits': sha(edits_path.read_bytes()),
            'shared_edits': sha(shared_path.read_bytes()),
            'rules': sha(rules_path.read_bytes()),
            'assets': sha(assets_path.read_bytes()),
            'source_lock': sha(source_lock_path.read_bytes()),
        },
        'output_sha256': {path: sha(raw) for path, raw in generated.items()},
        'checks': [
            'exact_pinned_git_blobs', 'complete_source_tree_and_order',
            '716_unique_ordered_ids', '262_mathml_roots',
            '55_media_17_tables_125_exercises',
            '83_supplied_and_42_absent_solutions', 'six_exact_references',
            'two_fail_closed_javanese_alt_repairs',
            'indonesian_pivot_and_source_media_unchanged',
        ],
        'native_language_review': False,
        'educator_review': False,
        'assistive_technology_review': False,
        'listening_review': False,
        'synthesized_audio_files': 0,
        'whole_module_complete': False,
    }
    receipt_raw = (json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode()
    generated[f'qa/{UNIT}.in-progress.json'] = receipt_raw
    return generated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    generated = products()
    assert generated == products(), 'Nondeterministic subtraction draft generation'
    for path, raw in generated.items():
        if args.check:
            actual = (LANG / path).read_bytes()
            if path == f'qa/{UNIT}.in-progress.json' and actual != raw:
                later = json.loads(actual)
                assert later['schema'] == 'jv-complete-module-build-v1'
                assert later['source_draft_receipt_sha256'] == sha(raw)
            else:
                assert actual == raw, f'Stale subtraction draft: {path}'
        else:
            write_bytes(LANG / path, raw)
    print('a00-subtract-whole: complete three-track source draft validated; production build pending.')


if __name__ == '__main__':
    main()
