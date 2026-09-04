"""Assemble all reviewed m81243 roots at their exact original document paths."""
import argparse
import copy
import json
import xml.etree.ElementTree as ET

from build import MATH, XML_LANG
from build_units import sha, tree_key
from config import LANG, TRACKS
import draft_summary
from safe_io import write_bytes

UNIT = 'a00-m81243-complete'
MODULE = 'm81243'
SECTION_UNITS = [
    ('fs-id1830385', 'a00-number-sense'),
    ('fs-id2340048', 'a00-place-value'),
    ('fs-id1883656', 'a00-digit-place'),
    ('fs-id1321580', 'a00-name-whole'),
    ('fs-id1339359', 'a00-write-whole'),
    ('fs-id2472737', 'a00-rounding'),
    ('fs-id2296006', 'a00-whole-summary.recap'),
    ('fs-id2279009', 'a00-section-exercises'),
]
ID_SHA256 = '7153ce88bcd4aea07fab4075bdb025884e07d534aafb6d06ff1bfbedbc46f251'
EN_SHA256 = '396b0029798e054e5db6d7acde738cec9f9d8b86bc81da8cc3690d01ec07cf2b'


def source_modules():
    lock = json.loads((LANG / 'sources.lock.json').read_bytes())
    repositories = {row['name']: row for row in lock['repositories']}
    id_raw = draft_summary.pinned_blob(repositories['a00-id'], f'modules/{MODULE}/index.cnxml')
    en_raw = draft_summary.pinned_blob(repositories['openstax-prealgebra-bundle'],
                                       f'modules/{MODULE}/index.cnxml')
    assert sha(id_raw) == ID_SHA256 and sha(en_raw) == EN_SHA256
    return id_raw, en_raw


def target_path(unit, track):
    return LANG / f'translation/{unit}.{track}.cnxml'


def assemble(source, track):
    assert track in TRACKS
    roots = {
        'title': ET.parse(target_path('a00-whole-summary.title', track)).getroot(),
        'metadata': ET.parse(target_path('a00-whole-summary.metadata', track)).getroot(),
        'glossary': ET.parse(target_path('a00-whole-summary.glossary', track)).getroot(),
    }
    sections = [(anchor, ET.parse(target_path(unit, track)).getroot())
                for anchor, unit in SECTION_UNITS]
    assert [node.get('id') for _, node in sections] == [anchor for anchor, _ in SECTION_UNITS]
    target = copy.deepcopy(source)
    target[0] = copy.deepcopy(roots['title'])
    target[1] = copy.deepcopy(roots['metadata'])
    target[2][:] = [copy.deepcopy(node) for _, node in sections]
    target[3] = copy.deepcopy(roots['glossary'])
    if track.startswith('jv'):
        target.set(XML_LANG, 'jv-Latn-ID')
    assert [node.get('id') for node in target[2]] == [anchor for anchor, _ in SECTION_UNITS]
    return target


def validate(source, target, track):
    assert source.tag == target.tag and len(source) == len(target) == 4
    assert [node.tag for node in source] == [node.tag for node in target]
    assert [node.get('id') for node in source[2]] == [node.get('id') for node in target[2]]
    source_ids = [node.get('id') for node in source.iter() if node.get('id')]
    target_ids = [node.get('id') for node in target.iter() if node.get('id')]
    assert source_ids == target_ids and len(source_ids) == len(set(source_ids)) == 628
    assert len(list(source.iter('{' + MATH + '}math'))) == len(list(target.iter('{' + MATH + '}math'))) == 249
    for (anchor, unit), source_section, target_section in zip(SECTION_UNITS, source[2], target[2]):
        assert source_section.get('id') == target_section.get('id') == anchor
        saved = ET.parse(target_path(unit, track)).getroot()
        assert tree_key(target_section) == tree_key(saved)
    for component, index in (('title', 0), ('metadata', 1), ('glossary', 3)):
        saved = ET.parse(target_path(f'a00-whole-summary.{component}', track)).getroot()
        assert tree_key(target[index]) == tree_key(saved)
    if track == 'id-academic':
        assert tree_key(target) == tree_key(source)
        assert target.get(XML_LANG) is None
    else:
        assert target.get(XML_LANG) == 'jv-Latn-ID'
    return source_ids


def products():
    id_raw, en_raw = source_modules()
    source = ET.fromstring(id_raw)
    assert [node.tag.rsplit('}', 1)[-1] for node in source] == ['title', 'metadata', 'content', 'glossary']
    assert [node.get('id') for node in source[2]] == [anchor for anchor, _ in SECTION_UNITS]
    generated, dependencies = {}, {}
    ids = None
    for track in TRACKS:
        target = assemble(source, track)
        current_ids = validate(source, target, track)
        ids = current_ids if ids is None else ids
        assert current_ids == ids
        name = f'translation/{UNIT}.{track}.cnxml'
        generated[name] = ET.tostring(target, encoding='utf-8', xml_declaration=True) + b'\n'
    generated[f'provenance/{UNIT}.en.cnxml'] = en_raw
    for track in TRACKS:
        for component in ('title', 'metadata', 'glossary'):
            path = target_path(f'a00-whole-summary.{component}', track)
            dependencies[path.relative_to(LANG).as_posix()] = sha(path.read_bytes())
        for _, unit in SECTION_UNITS:
            path = target_path(unit, track)
            dependencies[path.relative_to(LANG).as_posix()] = sha(path.read_bytes())
    receipt = {
        'schema': 'source-bound-complete-module-assembly-v1',
        'status': 'complete_source_scope_assembled_cross_component_review_pending',
        'unit': UNIT, 'program': 'A00', 'module': MODULE,
        'source_module_sha256': {'indonesian': ID_SHA256, 'english': EN_SHA256},
        'source_document_paths': {'title':[0], 'metadata':[1], 'content':[2], 'glossary':[3]},
        'source_content_section_ids': [anchor for anchor, _ in SECTION_UNITS],
        'component_unit_map': {anchor: unit for anchor, unit in SECTION_UNITS},
        'source_ids': ids, 'source_id_count': 628,
        'source_math_expressions': 249, 'source_media_references': 47,
        'source_exercises': 88, 'source_solutions_present': 59,
        'source_tables': 8, 'source_glossary_definitions': 7,
        'register_tracks': 3,
        'complete_source_scope': True,
        'offline_reader': 'pending_complete_module_build',
        'narration_ssml': 'pending_complete_module_build',
        'independent_cross_component_review': 'pending',
        'human_language_review': 'pending',
        'whole_module_complete': False,
        'files': {name: sha(raw) for name, raw in sorted(generated.items())},
        'verified_dependency_sha256': dict(sorted(dependencies.items())),
        'checks': ['exact_full_ID_and_EN_source_pins', 'original_four_root_positions',
                   'all_eight_content_sections_in_source_order', 'all_628_IDs_once',
                   'all_249_MathML_roots', 'exact_saved_component_tree_reuse',
                   'exact_ID_full_tree_replay', 'three_track_root_locale_contract'],
    }
    generated[f'qa/{UNIT}.assembly-receipt.json'] = (json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode()
    return generated


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    generated = products()
    assert generated == products()
    for name, raw in generated.items():
        if args.check:
            assert (LANG / name).read_bytes() == raw, name
        else:
            write_bytes(LANG / name, raw)
    print('Complete m81243 source scope assembled in three tracks; cross-component review and full reader/audio remain pending.')


if __name__ == '__main__':
    main()
