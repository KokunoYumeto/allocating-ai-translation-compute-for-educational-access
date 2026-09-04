"""Source-positioned recap/front/back components; not a partial fake module.

Four separate XML roots retain their original namespace and ordered-tree path.
No wrapper source IDs, moved glossary, or translated whole module are invented.
This is translation input preparation; audio and an assembled reader are separate.
"""
import argparse
import copy
import json
import xml.etree.ElementTree as ET

from build import MATH, translated
from build_units import sha, tree_key
from config import LANG, TRACKS
from draft_units import merged_edits, pinned_blob, validate
from safe_io import write_bytes

UNIT = 'a00-whole-summary'
MODULE = 'm81243'
SCOPE_PATHS = {'title': [0], 'metadata': [1], 'recap': [2, 6], 'glossary': [3]}
SOURCE_HASHES = {
    'a00-id': '7153ce88bcd4aea07fab4075bdb025884e07d534aafb6d06ff1bfbedbc46f251',
    'openstax-prealgebra-bundle': '396b0029798e054e5db6d7acde738cec9f9d8b86bc81da8cc3690d01ec07cf2b',
}
SCOPE_HASHES = {
    'title': '3b8234f2c1c4558c7aa2153e4debf367560462693fb82357f525603919b5c273',
    'metadata': '419cec0dfb0c8a0b0bdb8996e48369479bff176798bf2703a1d805ed682c7bab',
    'recap': '098df4a46ab1146a26b9d36e79ccab231324d5437bcb1f837e56d8b83b77e5d0',
    'glossary': 'fbbdcdc3812322372bd6d484e76d6830ff44f45bbbe8d739648a069e26c3321c',
}
CONTENT_ORDER = ['fs-id1830385', 'fs-id2340048', 'fs-id1883656', 'fs-id1321580',
                 'fs-id1339359', 'fs-id2472737', 'fs-id2296006', 'fs-id2279009']


def at(root, path):
    for index in path:
        root = root[index]
    return root


def selected(document):
    assert [n.tag.rsplit('}', 1)[-1] for n in document] == ['title', 'metadata', 'content', 'glossary']
    assert [n.get('id') for n in document[2]] == CONTENT_ORDER
    result = {}
    for key, path in SCOPE_PATHS.items():
        result[key] = copy.deepcopy(at(document, path))
        result[key].tail = None
    return result


def sources():
    lock = json.loads((LANG / 'sources.lock.json').read_bytes())
    repositories = {row['name']: row for row in lock['repositories']}
    result = {}
    for name, expected in SOURCE_HASHES.items():
        raw = pinned_blob(repositories[name], f'modules/{MODULE}/index.cnxml')
        assert sha(raw) == expected, 'Changed complete source: ' + name
        result[name] = selected(ET.fromstring(raw))
    for key, root in result['a00-id'].items():
        assert sha(tree_key(root).encode()) == SCOPE_HASHES[key], 'Changed component source: ' + key
    return result


def variants(source, edits=None):
    assert list(source) == list(SCOPE_PATHS), 'Changed component order'
    for key, root in source.items():
        assert sha(tree_key(root).encode()) == SCOPE_HASHES[key], 'Changed source component'
    edits = merged_edits(UNIT) if edits is None else edits
    result = {}
    for track in TRACKS:
        result[track] = {}
        for key, root in source.items():
            target = copy.deepcopy(root) if track == 'id-academic' else translated(root, track, edits)
            if track != 'id-academic':
                validate(root, target)
            result[track][key] = target
    return result


def validate_components(source, target, track):
    """Validate public consumers against fresh exact source and phrase replay."""
    assert track in TRACKS
    expected = variants(source)[track]
    assert list(target) == list(SCOPE_PATHS), 'Missing or reordered component'
    for key in SCOPE_PATHS:
        assert tree_key(target[key]) == tree_key(expected[key]), 'Changed component replay: ' + key


def facts(roots):
    ids = [n.get('id') for root in roots.values() for n in root.iter() if n.get('id')]
    assert len(ids) == len(set(ids)) == 23
    assert not any(list(root.iter('{' + MATH + '}math')) for root in roots.values())
    assert not any(root.findall('.//{*}exercise') for root in roots.values())
    assert roots['metadata'].findtext('{*}content-id') == MODULE
    assert roots['metadata'].findtext('{*}uuid') == '7cbc90c7-60c8-4211-bffe-b77aadc95509'
    assert roots['title'].text == roots['metadata'].findtext('{*}title')
    assert len(roots['metadata'].findall('{*}abstract/{*}list/{*}item')) == 6
    assert len(roots['glossary']) == 7
    assert [len(n) for n in roots['recap'].findall('{*}list/{*}item/{*}list')] == [2, 3, 4]
    assert len(roots['recap'].findall('.//{*}media')) == 1
    return ids


def products():
    pinned = sources()
    source = pinned['a00-id']
    tracks = variants(source)
    ids = facts(source)
    for track, roots in tracks.items():
        validate_components(source, roots, track)
        assert facts(roots) == ids
    generated, components = {}, []
    for key, path in SCOPE_PATHS.items():
        names = {}
        for track, roots in tracks.items():
            name = f'translation/{UNIT}.{key}.{track}.cnxml'
            names[track] = name
            generated[name] = ET.tostring(roots[key], encoding='utf-8', xml_declaration=True) + b'\n'
        name = f'provenance/{UNIT}.{key}.en.cnxml'
        names['en-source'] = name
        generated[name] = ET.tostring(pinned['openstax-prealgebra-bundle'][key], encoding='utf-8', xml_declaration=True) + b'\n'
        components.append({
            'component': key, 'original_document_path': path,
            'source_root_tag': source[key].tag,
            'source_ids': [n.get('id') for n in source[key].iter() if n.get('id')],
            'tree_sha256': {track: sha(tree_key(roots[key]).encode()) for track, roots in tracks.items()},
            'canonical_tree_sha256': sha(tree_key(pinned['openstax-prealgebra-bundle'][key]).encode()),
            'files': names,
        })
    receipt = {
        'schema': 'source-positioned-module-components-v1', 'unit': UNIT,
        'status': 'translation_components_draft_only', 'program': 'A00', 'module': MODULE,
        'source_module_sha256': SOURCE_HASHES, 'components': components,
        'source_document_child_order': ['title', 'metadata', 'content', 'glossary'],
        'source_content_child_ids': CONTENT_ORDER,
        'excluded_content_sections': [anchor for anchor in CONTENT_ORDER if anchor != 'fs-id2296006'],
        'assembly_rule': 'Replace only the four exact original paths during a future complete-module assembly; these separate roots are not a complete or contiguous document.',
        'source_ids': ids, 'source_mathml': 0, 'source_exercises': 0,
        'source_objectives': 6, 'source_glossary_definitions': 7, 'source_media': 1,
        'edits_sha256': sha((LANG / f'translation/{UNIT}.edits.json').read_bytes()),
        'shared_edits_sha256': sha((LANG / 'translation/phrases.json').read_bytes()),
        'files': {name: sha(raw) for name, raw in generated.items()},
        'offline_reader': 'pending_integration', 'narration_ssml': 'pending_integration',
        'full_module_complete': False, 'human_review': 'pending',
    }
    generated[f'qa/{UNIT}.components-receipt.json'] = (json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode()
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
    print('Four source-positioned components: 12 track roots + 4 English witnesses; no full-module or audio completion.')


if __name__ == '__main__':
    main()
