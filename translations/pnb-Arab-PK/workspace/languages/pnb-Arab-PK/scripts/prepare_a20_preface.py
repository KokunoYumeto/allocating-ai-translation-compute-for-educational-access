"""Prepare exact m81357 assets and retained A20 component evidence."""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET

from generate_a20_preface_manifest import (
    BASE, ROOT, CANONICAL, SOURCE, COMPARISON, EXCERPT, TRANSLATION, OUTPUT as MANIFEST,
    N, COMMIT, TREE, SOURCE_SHA, COMPARISON_SHA, DEFAULT_CREDIT, HASH_POLICY,
    FILES, sha, fh, blob, dimensions, image_mode, inventory, owner_source, require,
    A10_SOURCE, A10_TRANSLATION,
)

NOTICES = BASE / 'provenance/a20-preface-component-notices.json'
ASSET_DIR = BASE / 'assets/a20'


def load_inputs():
    m = json.loads(MANIFEST.read_text(encoding='utf-8'))
    t = json.loads(TRANSLATION.read_text(encoding='utf-8'))
    require((m['unit'], m['assignment'], m['module'], m['collection'], m['locale']) ==
            ('A20-preface', 'A20', 'm81357', 'col31234', 'pnb-Arab-PK'), 'Manifest scope changed')
    require((t['unit'], t['assignment'], t['module'], t['locale']) ==
            ('A20-preface', 'A20', 'm81357', 'pnb-Arab-PK'), 'Translation scope changed')
    lock = json.loads((BASE / 'sources.lock.json').read_text(encoding='utf-8'))
    pinned = next(x for x in lock['repositories'] if x['role'] == 'A10+A20 upstream')
    comparison_repo = next(x for x in lock['repositories'] if x['role'] == 'A20')
    release = next(x for x in lock['archives'] if x['role'] == 'A20')
    require((m['commit'], m['tree']) == (pinned['commit'], pinned['tree']) == (COMMIT, TREE), 'Canonical pin changed')
    require((comparison_repo['commit'], comparison_repo['tree']) ==
            ('b293e167477c8fe2e8885c6f6d79d12cbb2e0e89', '9ee25a0fa6eb336cbd40f3aa61587797b2bf4f27'), 'Comparison repository pin changed')
    require((release['version'], release['sha256'], release['indonesian_coverage']) ==
            ('v0.3.0-wip', 'a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7', {'translated': 48, 'total': 83}), 'Comparison release changed')
    raw, comp_raw = SOURCE.read_bytes(), COMPARISON.read_bytes()
    require(raw == EXCERPT.read_bytes() and len(raw) == m['full_module_bytes'] == m['excerpt_bytes'] == 23553 and
            sha(raw) == m['full_module_sha256'] == m['excerpt_sha256'] == SOURCE_SHA, 'Canonical/witness identity changed')
    require(blob(raw) == m['canonical_git_blob_sha1'], 'Canonical Git blob changed')
    require(len(comp_raw) == 24171 and sha(comp_raw) == m['indonesian_comparison_sha256'] == COMPARISON_SHA, 'Comparison identity changed')
    source = ET.fromstring(raw)
    keys, blocks, roles, ancestors, parents = inventory(source, 'm81357')
    require(keys == m['source_text_keys_in_order'] == list(t['source_blocks']) and len(keys) == 89, '89-owner order changed')
    require(roles == m['source_block_roles'] and ancestors == m['source_ancestor_ids'] and len(ancestors) == 66, 'Roles/ancestry changed')
    require(t['title'] == t['source_blocks']['m81357/title'] == m['module_title_pnb'], 'Translated title mismatch')
    a10 = ET.parse(A10_SOURCE).getroot()
    _, a10_blocks, _, _, _ = inventory(a10, 'm82630')
    a10_t = json.loads(A10_TRANSLATION.read_text(encoding='utf-8'))
    reuse = m['owner_reuse']['exact_target_reuse_after_book_title_substitution']
    candidate = m['owner_reuse']['candidate_source_matches_after_book_title_substitution']
    require(reuse == t['reuse_from_a10_preface'] and len(reuse) == 55 and len(m['owner_reuse']['fresh_or_fidelity_revised_keys']) == 34, 'Reuse ledger changed')
    require(len(candidate) == 56 and candidate['eip-629/item/1'] == 'eip-673/item/1' and
            m['owner_reuse']['candidate_source_match_count'] == 56 and m['owner_reuse']['target_reused_count'] == 55 and
            m['owner_reuse']['fresh_or_fidelity_revised_count'] == 34, 'Source-candidate/target-reuse counts changed')
    for key, a10_key in candidate.items():
        require(owner_source(blocks[key]) == owner_source(a10_blocks[a10_key]).replace('Elementary Algebra 2e', 'Intermediate Algebra 2e'), 'Source candidate changed: ' + key)
    for key, a10_key in reuse.items():
        require(t['source_blocks'][key] == a10_t['source_blocks'][a10_key].replace('Elementary Algebra 2e', 'Intermediate Algebra 2e'), 'Target reuse changed: ' + key)
    prepared = []
    for spec, node, filename in zip(m['images'], source.findall('.//' + N + 'media'), FILES):
        original = ROOT / spec['canonical_local_path']
        compared = ROOT / spec['comparison_local_path']
        target = BASE / spec['path']
        require(original == CANONICAL / 'media' / filename and target == ASSET_DIR / filename and target.resolve().parent == ASSET_DIR.resolve(), 'Asset path changed')
        require(spec['media_id'] == node.get('id') and spec['source_alt'] == node.get('alt'), 'Media alt identity changed')
        require(node.find(N + 'image').attrib == {'mime-type': spec['mime_type'], 'src': spec['source_src']}, 'Source image attributes changed')
        cdata, idata = original.read_bytes(), compared.read_bytes()
        require((len(cdata), sha(cdata), dimensions(cdata), image_mode(original), blob(cdata)) ==
                (spec['bytes'], spec['sha256'], (spec['width'], spec['height']), spec['mode'], spec['git_blob_sha1']), 'Canonical asset changed')
        require((len(idata), sha(idata), dimensions(idata), image_mode(compared), cdata == idata) ==
                (spec['comparison_bytes'], spec['comparison_sha256'], (spec['comparison_width'], spec['comparison_height']), spec['comparison_mode'], spec['comparison_byte_identical']), 'Comparison asset changed')
        require(not target.exists() or fh(target) == spec['sha256'], 'Refusing to overwrite different asset')
        prepared.append((spec, target, cdata))
    require([x[0]['comparison_byte_identical'] for x in prepared] == [True, True, True, False], 'Expected graph-only redraw difference changed')
    require(m['existing_notice_input_hash_policy'] == HASH_POLICY, 'Notice hash policy changed')
    for item in m['existing_notice_inputs']:
        require(sha((ROOT / item['path']).read_bytes().replace(b'\r\n', b'\n')) == item['sha256'], 'Existing notice input changed: ' + item['path'])
    credit_text = ''.join(source.find('.//*[@id="eip-787"]').itertext())
    require(credit_text.endswith(DEFAULT_CREDIT) and 'limitations provided in the credit' in credit_text, 'Source art credit changed')
    require([(x['id'], x['source_key']) for x in t['source_corrections']] ==
            [(x['id'], x['source_key']) for x in m['source_discrepancies']], 'Discrepancy ledger changed')
    return m, t, source, prepared, credit_text


def notice_record(m, prepared, credit_text):
    return {
        'schema': 'a20-retained-component-evidence-v1',
        'unit': 'A20-preface', 'work': 'OpenStax Intermediate Algebra 2e', 'module': 'm81357', 'collection': 'col31234',
        'commit': m['commit'], 'manifest_sha256': fh(MANIFEST), 'excerpt_sha256': m['excerpt_sha256'],
        'scope': 'Complete m81357 preface and four unchanged canonical originals; no new supply/license audit.',
        'comparison_scope': 'Indonesian v0.3.0-wip comparison is an admitted partial 48/83 checkpoint; it is not canonical and not a complete book.',
        'owner_reuse': {'candidate_source_matches': 56, 'exact_target_reuses': 55, 'fresh_or_fidelity_revised': 34,
            'reclassified_source_key': 'eip-629/item/1', 'frozen_a10_unchanged': True},
        'existing_notice_inputs': m['existing_notice_inputs'], 'existing_notice_input_hash_policy': HASH_POLICY,
        'release_license_verbatim': (BASE / 'provenance/A20-release/LICENSE.txt').read_text(encoding='utf-8'),
        'original_senior_contributing_authors': m['retained_attribution']['original_senior_contributing_authors'],
        'existing_license_statement': m['retained_attribution']['existing_license_statement'],
        'non_endorsement': m['retained_attribution']['non_endorsement'],
        'rights_status': 'Existing audited A20 policy retained; no new component-specific clearance determination.',
        'credit_limit': 'Canonical Git identity and byte hashes establish which files are served, not image-specific rights holders or new permissions. The raw-source default art credit and component-specific limits remain visible.',
        'source_default_art_credit': DEFAULT_CREDIT, 'source_default_art_credit_paragraph': 'eip-787',
        'raw_source_art_attribution_paragraph_verbatim': credit_text,
        'images': [{**spec,
            'treatment': ('Exact canonical bytes, unchanged and unmirrored. Faithful source alt stays traceable beside a labeled pixel-faithful accessible override. ' +
                          ('The differing Indonesian RGB redraw is comparison-only and is not served.' if not spec['comparison_byte_identical'] else 'The admitted Indonesian file is byte-identical.')),
            'component_clearance': 'Not newly assessed; subject to retained component-specific credits and restrictions.'}
            for spec, _, _ in prepared],
        'source_discrepancies': m['source_discrepancies'], 'whole_book_translation_complete': False,
        'publication_claim_limit': 'The retained A20 release describes a partial Indonesian checkpoint, not this Punjabi preface or a complete Punjabi book.'
    }


def prepare():
    m, t, source, prepared, credit_text = load_inputs()
    for spec, target, data in prepared:
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_bytes(data)
        require(fh(target) == spec['sha256'], 'Prepared asset differs')
    NOTICES.write_text(json.dumps(notice_record(m, prepared, credit_text), ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('Prepared A20-preface: four exact canonical originals and retained component evidence.')


if __name__ == '__main__':
    prepare()
