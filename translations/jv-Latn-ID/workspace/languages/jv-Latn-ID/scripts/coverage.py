"""Emit a deterministic, source-ordered full-assignment coverage ledger.

Run without options to emit JSON; --check compares it with coverage.json.
--write atomically replaces only coverage.json after all evidence checks pass.
No fetch, extraction, translation build, or audit is performed.
Baseline module counts come from source-locked, actually present pilot artifacts.
Additional unit drafts and verified standalone builds are listed separately.
A module is never complete merely because its Indonesian input was acquired.
"""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

LANG = Path(__file__).resolve().parents[1]
ROOT = LANG.parents[1]
NS = {'c': 'http://cnx.rice.edu/collxml', 'md': 'http://cnx.rice.edu/mdml',
      'x': 'http://cnx.rice.edu/cnxml', 'm': 'http://www.w3.org/1998/Math/MathML'}
TRACKS = ('jv-conversation', 'jv-academic', 'id-academic')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git_blobs(repository, paths):
    """Read already-local pinned blobs in one process, with lazy fetch disabled."""
    env = dict(os.environ, GIT_NO_LAZY_FETCH='1', GIT_OPTIONAL_LOCKS='0')
    queries = ''.join(f"{repository['commit']}:{path}\n" for path in paths)
    raw = subprocess.check_output(
        ['git', '--no-optional-locks', '-C', str(ROOT / repository['local_path']),
         'cat-file', '--batch'], input=queries.encode(), env=env)
    stream = io.BytesIO(raw)
    result = {}
    for path in paths:
        header = stream.readline().split()
        require(len(header) == 3 and header[1] == b'blob', f'Missing local blob: {path}')
        result[path] = stream.read(int(header[2]))
        require(stream.read(1) == b'\n', f'Invalid blob framing: {path}')
    require(not stream.read(), 'Unexpected trailing Git blob output')
    return result


def read_witness(lock, name):
    record = next(item for item in lock['files'] if item['retained_at'] == name)
    raw = (LANG / name).read_bytes()
    require(sha(raw) == record['sha256'], f'Changed retained witness: {name}')
    return raw


def collection_rows(raw):
    root = ET.fromstring(raw)
    rows = []

    def visit(content, chapters):
        for child in content:
            if child.tag == '{' + NS['c'] + '}module':
                rows.append({'module': child.attrib['document'], 'chapter_source': chapters})
            elif child.tag == '{' + NS['c'] + '}subcollection':
                title = child.find('md:title', NS)
                visit(child.find('c:content', NS), chapters + [''.join(title.itertext())])
            else:
                raise ValueError(f'Uninventoried collection node: {child.tag}')

    visit(root.find('c:content', NS), [])
    require(len({row['module'] for row in rows}) == len(rows), 'Duplicate module reference')
    return ''.join(root.find('c:metadata/md:title', NS).itertext()), rows


def pilot_coverage(unit, source, receipt):
    """Check present boundaries, not just a status label from a prior summary."""
    section = next(node for node in source.iter() if node.get('id') == unit['section'])
    children = list(section)
    count = unit['children']
    selected = children if count is None else children[:count]
    if count is not None:
        require(children[count].get('id') == unit['next_anchor'], 'A10 next anchor changed')
    else:
        source_nodes = list(source.iter())
        end = source_nodes.index(list(section.iter())[-1])
        next_id = next(node.get('id') for node in source_nodes[end + 1:] if node.get('id'))
        require(next_id == unit['next_anchor'], 'A00 next anchor changed')
    excerpt = ET.fromstring((LANG / unit['excerpt_path']).read_bytes())
    require(sha((LANG / unit['excerpt_path']).read_bytes()) == unit['indonesian_excerpt_sha256'],
            'Changed locked Indonesian excerpt')
    expected_ids = [unit['section']] + [node.get('id') for child in selected
                                      for node in child.iter() if node.get('id')]
    actual_ids = [node.get('id') for node in excerpt.iter() if node.get('id')]
    require(actual_ids == expected_ids, 'Pilot source-boundary IDs differ')
    files = [f"translation/{unit['key']}.{track}.cnxml" for track in TRACKS]
    files += [f"review/audio/{unit['key']}.{track}.{suffix}"
              for track in TRACKS for suffix in ('md', 'ssml')]
    for path in files:
        require(sha((LANG / path).read_bytes()) == receipt['output_sha256'][path],
                f'Pilot artifact no longer matches QA receipt: {path}')
    return {
        'unit': unit['key'], 'source_section': unit['section'],
        'selection': 'entire_section' if count is None else f'first_{count}_child_nodes_including_title',
        'direct_child_anchors': [child.get('id') for child in selected if child.get('id')],
        'covered_source_ids': expected_ids, 'next_excluded_anchor': unit['next_anchor'],
        'scope': unit['scope'], 'artifacts': files,
        'narration': 'draft_TTS_text_and_SSML_present_for_excerpt_only',
        'diagram_table_descriptions': 'draft_present_for_excerpt_only',
        'offline_build': 'excerpt_in_review/pilot.html',
        'automated_qa': 'pilot_receipt_structural_pass_only',
        'native_language_review': 'pending', 'visual_screen_reader_review': 'pending',
        'audio_synthesis': 'not_done_not_required_if_TTS_text_selected',
        'pronunciation_listening_review': 'pending',
    }


def unit_build_coverage(key, draft_sha, receipt, selected):
    """A separate build receipt may establish reader/SSML draft integration."""
    path = LANG / f'qa/{key}.build-receipt.json'
    if not path.exists():
        return None
    raw = path.read_bytes()
    build = json.loads(raw)
    require(build['schema'] == 'jv-unit-build-v1' and build['unit'] == key and
            build['status'] == 'structural_pass_human_review_pending', f'Unknown unit build state: {key}')
    require(build['source_draft_receipt_sha256'] == draft_sha, f'Build bound to stale draft receipt: {key}')
    require(build['whole_module_complete'] is False and build['synthesized_audio_files'] == 0 and
            all(build[field] is False for field in ('human_language_review', 'visual_review', 'listening_review')),
            f'Unit build review/completion state needs explicit reconciliation: {key}')
    math_count = sum(1 for child in selected for node in child.iter() if node.tag == '{' + NS['m'] + '}math')
    image_count = sum(1 for child in selected for node in child.iter() if node.tag == '{' + NS['x'] + '}image')
    require(build['source_ids'] == len(receipt['source_ids']) and build['source_math_expressions'] == math_count and
            build['source_media_references'] == image_count, f'Unit build source counts differ: {key}')
    require(build['register_tracks'] == 3 and build['ssml_files'] == 3, f'Incomplete unit build tracks: {key}')
    expected_files = {f'review/units/{key}.html'}
    expected_files.update(f'review/audio/{key}.{track}.{suffix}' for track in TRACKS for suffix in ('md', 'ssml'))
    require(set(build['output_sha256']) == expected_files, f'Unit build must witness all seven outputs: {key}')
    dependencies = {}
    rules = None
    rules_sha = build.get('rules_sha256')
    if rules_sha is not None:
        name = f'audio/{key}.rules.json'
        rules_raw = (LANG / name).read_bytes()
        require(sha(rules_raw) == rules_sha, f'Changed unit narration rules: {key}')
        rules = json.loads(rules_raw)
        require(len(rules['math_fixtures']) == build['source_bound_math_fixtures'],
                f'Unit narration fixture count differs: {key}')
        dependencies[name] = rules_sha
    else:
        require(build['source_bound_math_fixtures'] == 0, f'Unit narration fixtures lack a rules witness: {key}')
    nonspoken = {'a10-equality-symbols': ['fs-id1171789687379'],
                'a10-grouping-symbols': ['fs-id1166424830424']}.get(key, [])
    require(build.get('nonspoken_source_blocks', []) == nonspoken,
            f'Unexpected nonspoken source block declaration: {key}')
    for anchor in nonspoken:
        node = next(child for child in selected if child.get('id') == anchor)
        require(not ''.join(node.itertext()).strip() and
                all(child.tag.rsplit('}', 1)[-1] in ('para', 'newline') for child in node.iter()),
                f'Nonspoken block is not layout-only: {key}/{anchor}')
    expected_marks = [receipt['module'] + '--' + child.get('id', 'title') for child in selected
                      if child.get('id') not in nonspoken]
    if key == 'a00-rounding':
        require(selected[0].tag.endswith('}title') and selected[0].get('id') is None,
                'Rounding title is no longer anonymous')
        require(receipt['section'] == 'fs-id2472737', 'Rounding section identity changed')
        expected_marks[0] = receipt['module'] + '--' + receipt['section'] + '--title'
    elif key == 'a00-section-exercises':
        require(rules is not None and len(rules.get('block_fixtures', [])) == 80,
                'Section-exercise mark contract is incomplete')
        expected_marks = [fixture['generated_mark'] for fixture in rules['block_fixtures']]
        require(len(expected_marks) == len(set(expected_marks)) and
                all(mark.startswith(receipt['module'] + '--') for mark in expected_marks),
                'Section-exercise mark contract is invalid')
    for name, expected_sha in sorted(build['output_sha256'].items()):
        output = (LANG / name).read_bytes()
        require(sha(output) == expected_sha, f'Changed unit build output: {name}')
        if name.endswith('.ssml'):
            document = ET.fromstring(output)
            locale = 'jv-Latn-ID' if '.jv-' in name else 'id-ID'
            require(document.tag == '{http://www.w3.org/2001/10/synthesis}speak' and
                    document.get('{http://www.w3.org/XML/1998/namespace}lang') == locale,
                    f'Unit SSML locale differs: {name}')
            require([node.get('name') for node in document.findall('{*}mark')] == expected_marks,
                    f'Unit SSML source marks differ: {name}')
    assets_sha = build.get('asset_manifest_sha256')
    assets = []
    asset_outputs = {}
    if assets_sha is not None:
        name = f'translation/{key}.assets.json'
        assets_raw = (LANG / name).read_bytes()
        require(sha(assets_raw) == assets_sha, f'Changed unit asset manifest: {key}')
        dependencies[name] = assets_sha
        assets = json.loads(assets_raw)['assets']
        for asset in assets:
            require(set(asset['outputs']) == set(TRACKS), f'Incomplete unit asset tracks: {key}')
            for output in asset['outputs'].values():
                target = (LANG / output['path']).resolve()
                require(target.is_relative_to(LANG.resolve()), f'Out-of-scope unit asset: {output["path"]}')
                require(sha(target.read_bytes()) == output['sha256'], f'Changed unit asset: {output["path"]}')
                asset_outputs[output['path']] = output['sha256']
    require(len(assets) == image_count, f'Unit media dependencies incomplete: {key}')
    return {
        'status': 'standalone_reader_and_three_track_SSML_drafts_integrated',
        'receipt': {'path': path.relative_to(LANG).as_posix(), 'sha256': sha(raw)},
        'verified_output_sha256': dict(sorted(build['output_sha256'].items())),
        'verified_dependency_sha256': dict(sorted(dependencies.items())),
        'verified_asset_output_sha256': dict(sorted(asset_outputs.items())),
        'source_ids': build['source_ids'], 'source_math_expressions': math_count,
        'source_media_references': image_count, 'register_tracks': 3, 'ssml_files': 3,
        'reported_build_checks': build['checks'],
        'inventory_checks': ['draft_receipt_binding', 'source_counts', 'seven_output_hashes',
                             'SSML_locales_and_source_marks', 'rules_and_asset_dependency_hashes'],
        'human_language_review': 'pending', 'visual_screen_reader_review': 'pending',
        'listening_review': 'pending', 'synthesized_audio_files': 0, 'whole_module_complete': False,
        'scope_limit': 'These standalone excerpt builds do not establish whole-module/book completion or human approval.',
    }


def draft_coverage(books, a00_blobs, release_root):
    """Verify additional draft witnesses and any source-bound build receipts."""
    modules = {(book['program'], row['module']): row
               for book in books for row in book['modules']}
    drafts = []
    for path in sorted((LANG / 'qa').glob('*.draft-receipt.json')):
        receipt_raw = path.read_bytes()
        receipt = json.loads(receipt_raw)
        key = receipt['unit']
        require(path.name == f'{key}.draft-receipt.json', f'Draft receipt filename differs: {path.name}')
        require(receipt['schema'] == 'source-bound-unit-draft-v1' and
                receipt['status'] == 'translation_draft_only', f'Unknown draft state: {key}')
        require(receipt['full_module_complete'] is False and
                receipt['offline_reader'] == 'pending_integration' and
                receipt['narration_ssml'] == 'pending_integration', f'Draft integration state changed: {key}')
        module = modules[(receipt['program'], receipt['module'])]
        require(receipt['indonesian_module_sha256'] == module['indonesian_sha256'] and
                receipt['english_module_sha256'] == module['canonical_sha256'], f'Draft source pin differs: {key}')
        source_path = f"modules/{receipt['module']}/index.cnxml"
        source_raw = (a00_blobs[source_path] if receipt['program'] == 'A00' else
                      (release_root / 'translated' / source_path).read_bytes())
        require(sha(source_raw) == receipt['indonesian_module_sha256'], f'Draft module changed: {key}')
        source = ET.fromstring(source_raw)
        section = next(node for node in source.iter() if node.get('id') == receipt['section'])
        selection = receipt['slice']
        if selection is None:
            selected = list(section)
        else:
            require(len(selection) == 2 and all(type(value) is int for value in selection), f'Invalid slice: {key}')
            start, end = selection
            require(0 < start < end <= len(section) and section[0].tag == '{' + NS['x'] + '}title',
                    f'Invalid title-context slice: {key}')
            selected = [section[0]] + list(section)[start:end]
        ids = [receipt['section']] + [node.get('id') for child in selected
                                      for node in child.iter() if node.get('id')]
        direct_ids = [child.get('id') for child in selected if child.get('id')]
        require(ids == receipt['source_ids'] and direct_ids == receipt['included_direct_child_ids'],
                f'Draft source selection differs: {key}')
        expected_files = {f'translation/{key}.{track}.cnxml' for track in TRACKS}
        expected_files.add(f'provenance/{key}.en.cnxml')
        require(set(receipt['files']) == expected_files, f'Draft must witness all four CNXML files: {key}')
        for name, expected_sha in sorted(receipt['files'].items()):
            target = (LANG / name).resolve()
            require(target.is_relative_to(LANG.resolve()), f'Out-of-scope draft path: {name}')
            raw = target.read_bytes()
            require(sha(raw) == expected_sha, f'Changed draft artifact: {name}')
            document = ET.fromstring(raw)
            require([node.get('id') for node in document.iter() if node.get('id')] == ids,
                    f'Draft artifact source IDs differ: {name}')
            if '.jv-' in name:
                require(document.get('{http://www.w3.org/XML/1998/namespace}lang') == 'jv-Latn-ID',
                        f'Draft target locale differs: {name}')
        edits_path = f'translation/{key}.edits.json'
        require(sha((LANG / edits_path).read_bytes()) == receipt['edits_sha256'], f'Changed draft edits: {key}')
        shared_sha = receipt.get('shared_edits_sha256')
        if shared_sha is not None:
            require(sha((LANG / 'translation/phrases.json').read_bytes()) == shared_sha,
                    f'Changed shared draft edits: {key}')
        integrated_ids = {anchor for excerpt in module['covered_excerpts'] for anchor in excerpt['covered_source_ids']}
        build = unit_build_coverage(key, sha(receipt_raw), receipt, selected)
        drafts.append({
            'unit': key, 'program': receipt['program'], 'module': receipt['module'],
            'module_ordinal': module['ordinal'], 'source_section': receipt['section'],
            'source_child_slice': selection, 'scope': receipt['scope'],
            'direct_child_anchors': direct_ids, 'verified_source_ids': ids,
            'additional_source_ids_beyond_pilot': [anchor for anchor in ids if anchor not in integrated_ids],
            'source_ids_already_in_pilot': [anchor for anchor in ids if anchor in integrated_ids],
            'receipt': {'path': path.relative_to(LANG).as_posix(), 'sha256': sha(receipt_raw)},
            'verified_file_sha256': dict(sorted(receipt['files'].items())),
            'verified_edits': {'path': edits_path, 'sha256': receipt['edits_sha256']},
            'shared_edits': ({'path': 'translation/phrases.json', 'verified_sha256': shared_sha}
                             if shared_sha is not None else 'not_recorded_in_legacy_receipt'),
            'reported_translation_checks': receipt['checks'],
            'inventory_checks': ['source_pin', 'source_slice_and_ID_order', 'four_artifact_hashes_and_ID_order',
                                 'target_locale', 'edits_hash', 'shared_edits_hash_when_recorded'],
            'translation': 'verified_unit_draft_not_language_approval',
            'integration_state': 'standalone_reader_and_SSML_drafts_integrated' if build else 'unintegrated_translation_draft',
            'offline_reader': 'standalone_draft_built' if build else 'pending_integration',
            'narration_ssml': 'three_track_drafts_built' if build else 'pending_integration',
            'verified_build': build,
            'human_review': receipt['human_review'], 'full_module_complete': False,
            'effect_on_baseline_module_counts': 'none',
        })
    expected_build_names = {f"{row['unit']}.build-receipt.json" for row in drafts}
    expected_build_names.add('a00-m81243-complete.build-receipt.json')
    require(all(path.name in expected_build_names for path in (LANG / 'qa').glob('*.build-receipt.json')),
            'A unit build receipt has no inventoried draft receipt')
    return sorted(drafts, key=lambda row: (row['program'], row['module_ordinal'], row['unit']))


def component_coverage():
    """Separate front/content/back components cannot masquerade as a section."""
    from draft_summary import UNIT, products
    receipt_name = f'qa/{UNIT}.components-receipt.json'
    receipts = {path.relative_to(LANG).as_posix() for path in (LANG / 'qa').glob('*.components-receipt.json')}
    require(receipts <= {receipt_name}, 'Unregistered multi-scope component receipt')
    if not receipts:
        return []
    generated = products()
    for name, raw in generated.items():
        require((LANG / name).read_bytes() == raw, f'Stale source-positioned component: {name}')
    receipt = json.loads(generated[receipt_name])
    build_name = f'qa/{UNIT}.components-build-receipt.json'
    build_receipts = {path.relative_to(LANG).as_posix()
                      for path in (LANG / 'qa').glob('*.components-build-receipt.json')}
    require(build_receipts <= {build_name}, 'Unregistered source-positioned component build receipt')
    verified_build = None
    if build_name in build_receipts:
        from build_summary import products as build_products
        built = build_products()
        for name, raw in built.items():
            require((LANG / name).read_bytes() == raw, f'Stale source-positioned component build: {name}')
        build = json.loads(built[build_name])
        require(build['schema'] == 'source-positioned-components-build-v1' and
                build['status'] == 'structural_pass_human_review_pending' and
                build['unit'] == UNIT and build['module'] == receipt['module'],
                'Unknown source-positioned component build state')
        require(build['source_component_receipt_sha256'] == sha(generated[receipt_name]),
                'Component build is bound to a stale source receipt')
        require(build['source_ids'] == len(receipt['source_ids']) and
                build['source_math_expressions'] == receipt['source_mathml'] and
                build['source_media_references'] == receipt['source_media'],
                'Component build source counts differ')
        require(build['whole_module_complete'] is False and build['synthesized_audio_files'] == 0 and
                all(build[field] is False for field in
                    ('human_language_review', 'visual_review', 'integrated_browser_review',
                     'screen_reader_review', 'listening_review')),
                'Component build review/completion state needs reconciliation')
        verified_build = {
            'status': 'standalone_reader_and_three_track_SSML_drafts_integrated',
            'receipt': {'path': build_name, 'sha256': sha(built[build_name])},
            'verified_output_sha256': build['output_sha256'],
            'source_ids': build['source_ids'],
            'source_math_expressions': build['source_math_expressions'],
            'source_media_references': build['source_media_references'],
            'source_marked_narration_blocks': build['source_marked_narration_blocks'],
            'register_tracks': build['register_tracks'], 'ssml_files': build['ssml_files'],
            'rules_sha256': build['rules_sha256'],
            'asset_manifest_sha256': build['asset_manifest_sha256'],
            'reported_build_checks': build['checks'],
            'whole_module_complete': False,
        }
    return [{
        'unit': UNIT, 'program': receipt['program'], 'module': receipt['module'],
        'state': ('verified_source_positioned_components_with_standalone_reader_and_SSML'
                  if verified_build else 'verified_source_positioned_translation_components_not_reader_or_audio'),
        'components': receipt['components'],
        'excluded_content_sections': receipt['excluded_content_sections'],
        'source_ids': receipt['source_ids'],
        'receipt': {'path': receipt_name, 'sha256': sha(generated[receipt_name])},
        'verified_file_sha256': receipt['files'],
        'verification': 'Fresh complete pinned source, exact phrase replay and all sixteen component artifact bytes verified without writing outputs.',
        'offline_reader': 'standalone_draft_built' if verified_build else receipt['offline_reader'],
        'narration_ssml': 'three_track_drafts_built' if verified_build else receipt['narration_ssml'],
        'verified_build': verified_build,
        'human_review': receipt['human_review'], 'full_module_complete': False,
        'effect_on_baseline_module_counts': 'none',
    }]


def complete_module_candidate_coverage():
    """Record a full-source candidate and its separately bound external review."""
    from draft_complete_a00_module import UNIT, products as assembly_products
    from build_complete_a00_module import products as build_products
    assembly_name = f'qa/{UNIT}.assembly-receipt.json'
    build_name = f'qa/{UNIT}.build-receipt.json'
    review_name = 'qa/A00_M81243_COMPLETE_REREVIEW.md'
    review_sha256 = 'adfe7d63fe3325906f6dc7c7d259c9b5f92a297b702b12c72467cae5f5977218'
    reviewed_build_receipt_sha256 = '94f1f1f13f255a060ebdd4e1153f509f058a7be85a656f898f8bc153a4ee1099'
    assembly_receipts = {path.relative_to(LANG).as_posix()
                         for path in (LANG / 'qa').glob('*.assembly-receipt.json')}
    require(assembly_receipts <= {assembly_name}, 'Unregistered complete-module assembly receipt')
    if assembly_name not in assembly_receipts:
        return []
    assembled = assembly_products()
    built = build_products()
    for name, raw in {**assembled, **built}.items():
        require((LANG / name).read_bytes() == raw, f'Stale complete-module candidate: {name}')
    assembly = json.loads(assembled[assembly_name])
    build = json.loads(built[build_name])
    review_raw = (LANG / review_name).read_bytes()
    require(sha(review_raw) == review_sha256 and
            b'The automated independent cross-component review closes on this exact' in review_raw and
            reviewed_build_receipt_sha256.encode() in review_raw,
            'Complete-module independent rereview evidence changed')
    require(sha(built[build_name]) == reviewed_build_receipt_sha256,
            'Complete-module build receipt differs from independently reviewed bytes')
    require(assembly['schema'] == 'source-bound-complete-module-assembly-v1' and
            assembly['complete_source_scope'] is True and assembly['whole_module_complete'] is False,
            'Unknown complete-module assembly state')
    require(build['schema'] == 'complete-source-scope-module-build-v1' and
            build['status'] == 'structural_pass_independent_cross_component_review_pending' and
            build['complete_source_scope'] is True and build['whole_module_complete'] is False,
            'Unknown complete-module candidate build state')
    require(build['source_assembly_receipt_sha256'] == sha(assembled[assembly_name]),
            'Complete-module build is bound to a stale assembly')
    require(build['unmarked_editorial_notices'] == {
                'complete_id_reader': 2, 'complete_id_transcript': 1,
                'complete_id_ssml': 1, 'javanese_transcripts_and_ssml': 0,
            } and
            'reviewed_unmarked_rounding_notices_carried_without_new_marks' in build['checks'],
            'Complete-module unmarked editorial dependency contract changed')
    require((build['source_ids'], build['source_math_expressions'],
             build['source_media_references'], build['source_exercises'],
             build['source_solutions_present']) ==
            (assembly['source_id_count'], assembly['source_math_expressions'],
             assembly['source_media_references'], assembly['source_exercises'],
             assembly['source_solutions_present']),
            'Complete-module candidate source counts differ')
    return [{
        'unit': UNIT, 'program': assembly['program'], 'module': assembly['module'],
        'state': 'complete_source_scope_assembled_built_and_automated_cross_component_review_passed_human_review_pending',
        'complete_source_scope': True,
        'source_content_section_ids': assembly['source_content_section_ids'],
        'source_ids': build['source_ids'], 'source_math_expressions': build['source_math_expressions'],
        'source_media_references': build['source_media_references'],
        'source_exercises': build['source_exercises'],
        'source_solutions_present': build['source_solutions_present'],
        'source_marked_narration_blocks': build['source_marked_narration_blocks'],
        'unmarked_editorial_notices': build['unmarked_editorial_notices'],
        'assembly_receipt': {'path': assembly_name, 'sha256': sha(assembled[assembly_name])},
        'build_receipt': {'path': build_name, 'sha256': sha(built[build_name])},
        'verified_translation_sha256': assembly['files'],
        'verified_output_sha256': build['output_sha256'],
        'producer_pre_review_state': build['independent_cross_component_review'],
        'independent_cross_component_review': {
            'status': 'passed', 'path': review_name, 'sha256': review_sha256,
            'scope': 'automated_exact_source_tree_asset_reader_notice_narration_dependency_and_mutation_review',
        },
        'human_language_review': 'pending', 'whole_module_complete': False,
        'effect_on_baseline_module_counts': 'none_pending_human_and_integrated_accessibility_review',
    }]


def make_ledger():
    lock_raw = (LANG / 'sources.lock.json').read_bytes()
    lock = json.loads(lock_raw)
    repos = {item['name']: item for item in lock['repositories']}
    receipt_raw = (LANG / 'qa/receipt.json').read_bytes()
    receipt = json.loads(receipt_raw)
    canon_raw = (LANG / 'canon/sources.lock.json').read_bytes()
    canon_records = json.loads(canon_raw)['records']
    require(len({row['id'] for row in canon_records}) == len(canon_records), 'Duplicate canon reference ID')
    require(receipt['status'] == 'structural_pass_human_review_pending', 'Review receipt changed')
    for path in ('review/pilot.html', 'translation/number-line.id-ID.svg',
                 'translation/number-line.jv-Latn-ID.svg'):
        require(sha((LANG / path).read_bytes()) == receipt['output_sha256'][path],
                f'Changed checked artifact: {path}')

    a00_manifest = read_witness(lock, 'provenance/A00-source-manifest.tsv')
    a00_rows = list(csv.DictReader(io.StringIO(a00_manifest.decode()), delimiter='\t'))
    a10_manifest = read_witness(lock, 'provenance/A10-SOURCE_AUTHORITY_MANIFEST.csv')
    a10_all = list(csv.DictReader(io.StringIO(a10_manifest.decode())))
    a10_rows = sorted((row for row in a10_all if row['role'] == 'cnxml_module'),
                      key=lambda row: int(row['order']))
    require([int(row['ordinal']) for row in a00_rows] == list(range(1, 76)), 'A00 ordinal gap')
    require([int(row['order']) for row in a10_rows] == list(range(1, 83)), 'A10 ordinal gap')
    coll_paths = ['collections/prealgebra-2e.collection.xml',
                  'collections/elementary-algebra-2e.collection.xml']
    canonical = git_blobs(repos['openstax-prealgebra-bundle'], coll_paths)
    a00_paths = [coll_paths[0]] + [f"modules/{row['module']}/index.cnxml" for row in a00_rows]
    a00_blobs = git_blobs(repos['a00-id'], a00_paths)
    require(a00_blobs[coll_paths[0]].replace(b'\r\n', b'\n') == canonical[coll_paths[0]].replace(b'\r\n', b'\n'),
            'A00 collection differs beyond line endings')
    release_root = ROOT / 'downloads/jv-Latn-ID/a10-source'
    a10_coll = (release_root / 'authority/elementary-algebra-2e.collection.xml').read_bytes()
    collection_witness = next(row for row in a10_all if row['role'] == 'collection')
    require(sha(a10_coll) == collection_witness['sha256'], 'A10 collection witness differs')
    require(a10_coll.replace(b'\r\n', b'\n') == canonical[coll_paths[1]].replace(b'\r\n', b'\n'),
            'A10 collection differs beyond line endings')
    release_manifest_raw = (release_root / 'MANIFEST.json').read_bytes()
    release_entries = {row['path']: row for row in json.loads(release_manifest_raw)['entries']}
    require(len(release_entries) == lock['a10_release_manifest_entries_verified'], 'Release entry count changed')

    books = []
    for code, index, manifest_rows in [('A00', 0, a00_rows), ('A10', 1, a10_rows)]:
        title, ordered = collection_rows(canonical[coll_paths[index]])
        expected = ([row['module'] for row in manifest_rows] if code == 'A00' else
                    [row['relative_path'].split('/')[1] for row in manifest_rows])
        require([row['module'] for row in ordered] == expected, f'{code} collection/manifest order differs')
        modules = []
        for ordinal, (row, witness) in enumerate(zip(ordered, manifest_rows), 1):
            module = row['module']
            path = f'modules/{module}/index.cnxml'
            if code == 'A00':
                raw = a00_blobs[path]
                local_path = repos['a00-id']['local_path'] + '/' + path
                hash_basis = 'pinned_Git_blob'
            else:
                path = 'translated/' + path
                raw = (release_root / path).read_bytes()
                require(sha(raw) == release_entries[path]['sha256'] and
                        len(raw) == release_entries[path]['bytes'], f'Changed A10 release module: {module}')
                local_path = release_root.relative_to(ROOT).as_posix() + '/' + path
                hash_basis = 'release_file_bytes'
            source = ET.fromstring(raw)
            source_class = source.get('class', '')
            role = ('preface' if ordinal == 1 else 'appendix' if source_class == 'appendix'
                    else 'chapter_introduction' if source_class == 'introduction' else 'instructional_module')
            covered = [pilot_coverage(unit, source, receipt) for unit in lock['units']
                       if unit['program'] == code and unit['module'] == module]
            modules.append({
                'ordinal': ordinal, **row, 'role': role,
                'title_id_source': ''.join(source.find('x:title', NS).itertext()),
                'indonesian_source': local_path, 'indonesian_sha256': sha(raw),
                'indonesian_hash_basis': hash_basis, 'canonical_sha256': witness['sha256'],
                'source_acquisition': 'acquired_not_equivalent_to_translation',
                'translation': 'partial' if covered else 'untranslated',
                'jv_conversation': 'partial_draft' if covered else 'untranslated',
                'jv_academic': 'partial_draft' if covered else 'untranslated',
                'id_academic': 'source_acquired',
                'AX2_full_module': {'narration': 'pending', 'diagram_descriptions': 'pending',
                                    'offline_build': 'pending', 'review': 'pending'},
                'covered_excerpts': covered,
            })
        books.append({
            'program': code, 'title_source': title, 'module_count': len(modules),
            'ordering': 'depth_first_collection_order_exactly_matches_manifest_ordinals',
            'collection': {'path': coll_paths[index], 'sha256': sha(canonical[coll_paths[index]]),
                           'repository_commit': repos['openstax-prealgebra-bundle']['commit'],
                           'pivot_raw_sha256': sha(a00_blobs[coll_paths[0]] if code == 'A00' else a10_coll),
                           'pivot_comparison': 'identical_text_after_CRLF_to_LF_comparison_only; raw_files_not_modified'},
            'manifest': {'retained_path': f"provenance/{'A00-source-manifest.tsv' if code == 'A00' else 'A10-SOURCE_AUTHORITY_MANIFEST.csv'}",
                         'sha256': sha(a00_manifest if code == 'A00' else a10_manifest)},
            'within_module_count': {role: [row['module'] for row in modules if row['role'] == role]
                                    for role in ('preface', 'chapter_introduction', 'appendix')},
            'completed_modules': 0, 'partial_modules': sum(bool(row['covered_excerpts']) for row in modules),
            'untranslated_modules': sum(not row['covered_excerpts'] for row in modules),
            'modules': modules,
        })
    obligations = [
        {'surface': 'collection_metadata_and_navigation', 'state': 'untranslated',
         'scope': 'Both source collection titles, chapter titles, navigation labels, and localized publication metadata; module text alone is insufficient.'},
        {'surface': 'prefaces_credits_appendices', 'state': 'untranslated_but_explicitly_in_module_counts',
         'scope': 'A00 m81241 and m56252/m56244/m56248; A10 m82630. All chapter introductions also remain assigned.'},
        {'surface': 'inherited_licenses_notices_and_attribution', 'state': 'originals_retained_full_publication_integration_pending',
         'scope': 'Preserve original legal and attribution evidence; local-language explanatory credit text must not replace the original notices. No new licence/supply audit.'},
        {'surface': 'covers_title_pages_and_generated_backmatter', 'state': 'full_publication_integration_pending',
         'scope': 'Account for publication title/cover text and any generated glossary, index, consolidated answers, and reference targets; these are not extra completed CNXML modules.'},
        {'surface': 'AX2_full_assignment', 'state': 'full_assignment_pending_excerpt_builds_recorded_separately',
         'scope': 'Deterministic formula narration, diagram/table descriptions, and audio OR TTS-ready text for every assigned unit; three distinct language/register tracks and per-unit QA.'},
        {'surface': 'AX1_prerequisite_packaging', 'state': 'excerpt_HTML_only_full_assignment_pending',
         'scope': 'Source AX-2 names AX-1 as prerequisite: semantic HTML/MathML, screen/print profiles and offline package. This inventory does not claim those whole-book deliverables exist.'},
        {'surface': 'A00_external_instructor_supplementary_answers', 'state': 'outside_acquired_collection_not_claimed_complete',
         'source_anchor': 'm56252/fs-id1171104427807',
         'scope': 'Cumulative-review source note directs instructors to supplementary answers at OpenStax. Preserve and translate the note; external restricted supplements are not silently included in the 75-module count.'},
        {'surface': 'linguistic_visual_screen_reader_pronunciation_reviews', 'state': 'pending',
         'scope': 'Automated pilot structural QA does not certify native language, register, screen-reader use, or listening/pronunciation.'},
    ]
    return {
        'schema': 'jv-full-assignment-coverage-v1',
        'scope': 'Entire assigned A00 and A10 collections plus AX-2 and their complete translation workflow; not a pilot-completion goal.',
        'status': 'incomplete', 'completed_modules': 0,
        'partial_modules': sum(book['partial_modules'] for book in books),
        'untranslated_modules': sum(book['untranslated_modules'] for book in books),
        'generated_by': ('scripts/coverage.py; deterministic inventory; --check is read-only and '
                         '--write atomically replaces only coverage.json; no downloads or builds'),
        'evidence': {'source_lock_sha256': sha(lock_raw), 'pilot_qa_receipt_sha256': sha(receipt_raw),
                     'a10_extracted_release_manifest_sha256': sha(release_manifest_raw),
                     'canonical_pin': repos['openstax-prealgebra-bundle']['commit'],
                     'state_rule': 'Baseline module counts retain source-locked pilot coverage; additional_unit_drafts separately verifies draft and optional standalone-build evidence. Neither establishes whole-module completion.'},
        'canon': {'path': 'canon/README.md', 'entries': len(canon_records),
                  'source_lock': {'path': 'canon/sources.lock.json', 'sha256': sha(canon_raw)},
                  'role': 'Lexical/usage shelf; consult and log at every translation/narration/QA production stage.',
                  'this_operation': 'Source inventory only; no linguistic wording was drafted or approved.'},
        'programs': books, 'additional_unit_drafts': draft_coverage(books, a00_blobs, release_root),
        'additional_module_components': component_coverage(),
        'complete_module_candidates': complete_module_candidate_coverage(),
        'obligations_outside_module_completion_counts': obligations,
        'completion_rule': 'Zero modules complete at this checkpoint. Every source module and non-module obligation must be handled; acquired Indonesian inputs and passing pilot QA are not completed Javanese translation.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--check', action='store_true', help='Read-only exact comparison with coverage.json')
    modes.add_argument('--write', action='store_true', help='Atomically replace coverage.json after verification')
    args = parser.parse_args()
    ledger = make_ledger()
    rendered = json.dumps(ledger, ensure_ascii=False, indent=2) + '\n'
    if args.check:
        require((LANG / 'coverage.json').read_text(encoding='utf-8') == rendered, 'coverage.json is stale')
        print('Coverage matches: A00 75 + A10 82; 0 complete, 2 partial, 155 untranslated; all AX-2 module completions pending.')
    elif args.write:
        from safe_io import write_text
        write_text(LANG / 'coverage.json', rendered)
        built = sum(unit['verified_build'] is not None for unit in ledger['additional_unit_drafts'])
        print(f"Coverage written atomically: 0 complete modules, {built} additional built unit drafts, {ledger['canon']['entries']} canon entries.")
    else:
        sys.stdout.reconfigure(encoding='utf-8')
        print(rendered, end='')


if __name__ == '__main__':
    main()
