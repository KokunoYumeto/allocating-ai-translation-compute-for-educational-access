"""Refresh only reviewed target-alt/asset bindings; never authorize new speech.

The original finite narration draft remains the speech authority. Compare every
old/new target tree allowing only the three reviewed number-line alt slots.
Source hashes, mathematics, speech and ordered sequences may not change here.
"""
import argparse
import copy
import json
import xml.etree.ElementTree as ET

from build import CN, MATH
from build_units import sha, tree_key
from config import LANG, TRACKS
from draft_units import products as draft_products
from safe_io import write_bytes

UNIT = 'a00-rounding'
ALT_IDS = {'fs-id3447999', 'fs-id2907091', 'fs-id2471614'}
SOURCE = '19fe0a6c486c4c0c1898735c0e4a6a07380bb19d87d21c7b5f440c31a308e6bd'


def parse(text):
    return ET.fromstring(f'<wrapper xmlns="{CN}" xmlns:m="{MATH}">{text}</wrapper>')[0]


def at(root, path):
    for index in path:
        root = root[index]
    return root


def xml(node):
    node = copy.deepcopy(node)
    node.tail = None
    return ET.tostring(node, encoding='unicode')


def compatible(old, new, track):
    old = copy.deepcopy(old)
    new_nodes = {n.get('id'): n for n in new.iter() if n.get('id')}
    if track.startswith('jv'):
        for node in old.iter():
            if node.get('id') in ALT_IDS:
                node.set('alt', new_nodes[node.get('id')].get('alt'))
    assert tree_key(old) == tree_key(new), 'Unreviewed change outside three target alt slots'


def products():
    generated = draft_products(UNIT)
    roots = {t: ET.fromstring(generated[f'translation/{UNIT}.{t}.cnxml']) for t in TRACKS}
    source = roots['id-academic']
    assert sha(tree_key(source).encode()) == SOURCE
    rules_path = LANG / f'audio/{UNIT}.rules.json'
    rules = json.loads(rules_path.read_text(encoding='utf-8'))
    assert rules['scope']['section_sha256']['id-academic'] == SOURCE
    for group, path_key, variant_key in [('block_fixtures', 'path', 'variants'),
                                         ('chart_fixtures', 'source_path', 'variant_cnxml'),
                                         ('table_fixtures', 'source_path', 'variant_cnxml')]:
        for fixture in rules[group]:
            path = fixture[path_key]
            assert tree_key(parse(fixture['source_cnxml'])) == tree_key(at(source, path))
            for track, root in roots.items():
                node = at(root, path)
                compatible(parse(fixture[variant_key][track]), node, track)
                fixture[variant_key][track] = xml(node)
                fixture['variant_tree_sha256'][track] = sha(tree_key(node).encode())
                if group == 'chart_fixtures':
                    fixture['alt'][track] = node.get('alt')
    assets_raw = (LANG / f'translation/{UNIT}.assets.json').read_bytes()
    assets = json.loads(assets_raw)['assets']
    for fixture, asset in zip(rules['chart_fixtures'], assets):
        node = at(source, fixture['source_path'])
        assert fixture['media_id'] == asset['media_id'] == node.get('id')
        assert fixture['asset']['sha256'] == asset['source_sha256']
        fixture['source_alt'] = node.get('alt')
        fixture['source_image'] = node.find('{*}image').get('src')
        fixture['outputs'] = asset['outputs']
    rules['scope']['section_sha256'].update({t: sha(tree_key(r).encode()) for t, r in roots.items()})
    rules['scope']['edits_sha256'] = sha((LANG / f'translation/{UNIT}.edits.json').read_bytes())
    rules['scope']['asset_manifest_sha256'] = sha(assets_raw)
    rules['target_binding_revision'] = {
        'date': '2026-08-31', 'allowed_alt_media_ids': sorted(ALT_IDS),
        'reason': 'Actual retained number-line points are teal, not source-alt orange. Only JV alts become location-focused; source, values, math and finite speech are unchanged.',
        'asset_review': 'qa/a00-rounding.ASSETS.md',
        'standalone_visual_review_only': True,
    }
    generated[f'audio/{UNIT}.rules.json'] = (json.dumps(rules, ensure_ascii=False, indent=2) + '\n').encode()
    return generated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for path, raw in products().items():
        if args.check:
            assert (LANG / path).read_bytes() == raw, f'Stale reviewed binding: {path}'
        else:
            write_bytes(LANG / path, raw)
    print('Complete rounding drafts and reviewed target/asset bindings verified; no new speech generated.')


if __name__ == '__main__':
    main()
