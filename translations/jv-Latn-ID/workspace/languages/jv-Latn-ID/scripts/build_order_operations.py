"""Deterministic production artifacts for the complete A10 order-of-operations unit."""
from __future__ import annotations

import argparse
import collections
import html
import json
import re
import xml.etree.ElementTree as ET

from build import MATH, STYLE, XML_LANG, render
from config import LANG, TRACKS as TRACK_CONFIG
from order_operations_checks import (
    EDITS_PATH, EDITS_SHA256, EN_MODULE_SHA256, ID_MODULE_SHA256, LOCALES, MODULE,
    NEXT_FIRST_PARAGRAPH, NEXT_SECTION, RULES_PATH, RULES_SHA256, SECTION,
    SHARED_EDITS_PATH, SHARED_EDITS_SHA256, SOURCE_LOCK_SHA256, TRACKS, UNIT,
    blocks, load_rules, question_readouts, sha, source_sections, validate_scope, variants,
)
from prepare_order_operations_assets import asset_products
from qa import Reader
from safe_io import write_bytes

SOURCE_RECEIPT = f'qa/{UNIT}.source-receipt.json'
PRODUCTION_RECEIPT = f'qa/{UNIT}.production-receipt.json'
DISPLAY_TRACKS = tuple(TRACK_CONFIG)


def xml_bytes(root: ET.Element) -> bytes:
    return ET.tostring(root, encoding='utf-8', xml_declaration=True) + b'\n'


def source_products() -> tuple[dict[str, bytes], ET.Element, dict[str, ET.Element], dict]:
    rules = load_rules()
    source, english = source_sections()
    roots = variants(source)
    generated = {f'translation/{UNIT}.{track}.cnxml': xml_bytes(roots[track]) for track in TRACKS}
    generated[f'provenance/{UNIT}.en.cnxml'] = xml_bytes(english)
    direct_ids = [node.get('id') for node in source if node.get('id')]
    receipt = {
        'schema': 'jv-order-operations-source-receipt-v1', 'unit': UNIT,
        'status': 'source_bound_structural_pass_human_review_pending',
        'program': 'A10', 'module': MODULE, 'section': SECTION, 'complete_section': True,
        'scope': rules['scope']['completion_claim'], 'included_direct_child_ids': direct_ids,
        'source_ids': [node.get('id') for node in source.iter() if node.get('id')],
        'counts': {
            'direct_children': 31, 'ids': 111, 'mathml': 21, 'msup': 3, 'mfrac': 0,
            'tables': 4, 'physical_table_rows': 35, 'media': 23, 'exercises': 9,
            'solutions': 9, 'question_parts': 12, 'supplied_answers': 12,
            'absent_answers': 0, 'prose_fixtures': 11,
        },
        'pins': {
            'indonesian_module_sha256': ID_MODULE_SHA256,
            'english_module_sha256': EN_MODULE_SHA256,
            'edits_sha256': EDITS_SHA256, 'shared_edits_sha256': SHARED_EDITS_SHA256,
            'rules_sha256': RULES_SHA256, 'source_lock_sha256': SOURCE_LOCK_SHA256,
        },
        'accessibility_corrections': {
            'target_only_exact_bindings': 6,
            'numeric_sequence_exceptions': [
                {'phrase_index_zero_based': 72, 'element_id': 'fs-id1167836329648', 'attribute': 'alt'},
                {'phrase_index_zero_based': 75, 'element_id': 'fs-id1167836375645', 'attribute': 'aria-label'},
                {'phrase_index_zero_based': 89, 'element_id': 'fs-id1167829840981', 'attribute': 'aria-label'},
            ],
            'global_numeric_relaxation': False, 'source_pivot_changed': False,
        },
        'next_source_cursor': {'section': NEXT_SECTION, 'first_paragraph': NEXT_FIRST_PARAGRAPH},
        'files': {path: sha(raw) for path, raw in generated.items()},
        'checks': [
            'exact_pinned_id_and_en_modules', 'complete_31_child_boundary_and_next_sibling',
            '111_unique_ids_and_exact_order', 'exact_phrase_replay_all_three_tracks',
            '21_anchor_ordinal_tree_bound_mathml', 'four_headerless_tables_35_physical_rows',
            '23_source_media_trees', 'eleven_whole_prose_fixtures',
            'twelve_questions_twelve_supplied_answers',
            'six_exact_target_attribute_corrections_only_three_numeric_sequence_exceptions',
        ],
        'human_language_review': False, 'human_visual_review': False,
        'screen_reader_review': False, 'assistive_technology_review': False,
        'listening_review': False, 'synthesized_audio_files': 0,
        'whole_module_complete': False, 'full_ax2_complete': False,
    }
    generated[SOURCE_RECEIPT] = (json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode()
    return generated, source, roots, rules


def _media_maps(asset_generated: dict[str, bytes], manifest: dict) -> dict[str, dict]:
    result = {track: {} for track in TRACKS}
    assert len(manifest['assets']) == 23
    for asset in manifest['assets']:
        for track in TRACKS:
            output = asset['outputs'][track]
            raw = asset_generated[output['path']]
            assert sha(raw) == output['sha256'] == asset['source_sha256']
            assert output['mime_type'] == 'image/jpeg'
            result[track][asset['source_src']] = {'bytes': raw, 'mime_type': 'image/jpeg'}
    assert all(len(result[track]) == 23 for track in TRACKS)
    return result


def _audio_products(source: ET.Element, roots: dict[str, ET.Element], rules: dict) -> tuple[dict[str, bytes], dict[str, list]]:
    generated, all_blocks = {}, {}
    fixtures = {row['id']: row for row in rules['math_fixtures']}
    for track in DISPLAY_TRACKS:
        locale, label = TRACK_CONFIG[track]
        assert locale == LOCALES[track]
        narration = blocks(roots[track], track, rules, source)
        all_blocks[track] = narration
        questions = question_readouts(roots[track], track, rules, source)
        assert questions == [fixtures[key]['expected'][track] for key in rules['answer_policy']['question_fixtures']]
        transcript = (
            '# ' + label + '\n\n'
            'Status: source-bound narration draft; not synthesized, listening-reviewed, or human-approved.\n\n' +
            '\n\n'.join(f'## {MODULE}--{anchor}\n\n{body}' for anchor, body in narration) + '\n'
        )
        stem = f'review/audio/{UNIT}.{track}'
        generated[stem + '.md'] = transcript.encode()
        ssml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<speak xmlns="http://www.w3.org/2001/10/synthesis" version="1.1" xml:lang="{locale}">'
            f'<p>{html.escape(label)}</p>\n' +
            ''.join(f'<mark name="{MODULE}--{anchor}"/><p>{html.escape(body)}</p><break time="600ms"/>\n'
                    for anchor, body in narration) +
            '</speak>\n'
        )
        parsed = ET.fromstring(ssml)
        assert parsed.get(XML_LANG) == locale
        assert [node.get('name') for node in parsed.findall('{*}mark')] == [MODULE + '--' + anchor for anchor, _ in narration]
        assert [node.text for node in parsed.findall('{*}p')][1:] == [body for _, body in narration]
        assert not parsed.findall('.//{*}voice') and not parsed.findall('.//{*}lang')
        assert len(parsed.findall('{*}p')) == 32 and all(normalized_text(''.join(node.itertext())) for node in parsed.findall('{*}p'))
        generated[stem + '.ssml'] = ssml.encode()
    return generated, all_blocks


def normalized_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def _reader_page(source: ET.Element, roots: dict[str, ET.Element], rules: dict,
                 media: dict[str, dict], audio: dict[str, bytes]) -> bytes:
    title = roots['jv-academic'].findtext('{*}title')
    pieces = [
        '<!DOCTYPE html><html lang="id-ID"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        '<title>' + html.escape(UNIT) + '</title><style>' + STYLE + '</style></head><body><main>',
        '<header><div class="eyebrow">A10 · jv-Latn-ID / id-ID</div>',
        '<h1 lang="jv-Latn-ID">' + html.escape(title) + '</h1>',
        '<p class="source" lang="en">Complete pinned section m82453/fs-id1170654953465; next section excluded.</p>',
        '<p class="status">Draf telung register. Durung ditelaah penutur utawa pendhidhik Jawa, durung diuji nganggo teknologi bantu, lan durung diuji rungokake; dudu edisi siap terbit.</p>',
        '</header>',
    ]
    for track in DISPLAY_TRACKS:
        pieces.append(f'<span id="{UNIT}--{track}--{SECTION}" data-source-id="{SECTION}"></span>')
    for index in range(len(source)):
        pieces.append('<div class="parallel">')
        for track in DISPLAY_TRACKS:
            locale, label = TRACK_CONFIG[track]
            pieces.append(
                f'<article class="track" lang="{locale}" data-register="{track}">'
                f'<div class="register">{html.escape(label)}</div>' +
                render(roots[track][index], UNIT + '--' + track + '--', media[track]) + '</article>')
        pieces.append('</div>')
    pieces.append('<section class="note-box"><h2>Naskah audio</h2><ul>')
    for track in DISPLAY_TRACKS:
        locale, label = TRACK_CONFIG[track]
        stem = f'../audio/{UNIT}.{track}'
        assert f'review/audio/{UNIT}.{track}.md' in audio and f'review/audio/{UNIT}.{track}.ssml' in audio
        pieces.append(f'<li><span lang="{locale}">{html.escape(label)}</span>: '
                      f'<a href="{stem}.md">Naskah</a> / <a href="{stem}.ssml">SSML</a></li>')
    pieces.extend([
        '</ul></section>',
        '<footer lang="en"><p>Unofficial AI-assisted adaptation of OpenStax through the Indonesian edition by KokunoYumeto. Inherited licensing and component notices apply; no endorsement. <a href="../../ATTRIBUTION.md">Full attribution and notices</a>.</p>',
        '<p>Source IDs, order, mathematical notation, quantities, and image bytes are preserved. Native-language, visual, screen-reader, assistive-technology, classroom, and listening review remain pending.</p></footer>',
        '</main></body></html>',
    ])
    page = '\n'.join(pieces)
    assert '<script' not in page.lower() and '<audio' not in page.lower()
    assert not re.search(r'(?:src|href)="https?://', page)
    inspection = Reader()
    inspection.feed(page)
    assert len(inspection.ids) == len(set(inspection.ids))
    assert inspection.maths == 3 * 21 and len(inspection.images) == 3 * 23
    assert all(image.get('alt') and image.get('src', '').startswith('data:image/jpeg;base64,') for image in inspection.images)
    assert inspection.heads == []
    assert collections.Counter(track for track, _ in inspection.tracks) == {track: 31 for track in DISPLAY_TRACKS}
    assert all(LOCALES[track] == locale for track, locale in inspection.tracks)
    source_ids = [node.get('id') for node in source.iter() if node.get('id')]
    for track in DISPLAY_TRACKS:
        assert all(f'{UNIT}--{track}--{element_id}' in inspection.ids for element_id in source_ids)
    for link in inspection.links:
        assert not link.startswith('#'), 'Selected source has no internal references'
        resolved = (LANG / 'review/units' / link).resolve()
        assert resolved.is_file() or resolved.relative_to(LANG).as_posix() in audio
    return page.encode()


def products() -> dict[str, bytes]:
    generated, source, roots, rules = source_products()
    assets = asset_products()
    manifest = json.loads(assets[f'translation/{UNIT}.assets.json'])
    media = _media_maps(assets, manifest)
    audio, all_blocks = _audio_products(source, roots, rules)
    page = _reader_page(source, roots, rules, media, audio)
    generated.update(assets)
    generated.update(audio)
    generated[f'review/units/{UNIT}.html'] = page

    for track in TRACKS:
        validate_scope(source, roots[track], rules, track)
        assert len(all_blocks[track]) == 31
    source_receipt_raw = generated[SOURCE_RECEIPT]
    receipt_outputs = {path: sha(raw) for path, raw in generated.items() if path != SOURCE_RECEIPT}
    receipt = {
        'schema': 'jv-order-operations-production-receipt-v1', 'unit': UNIT,
        'status': 'deterministic_structural_pass_human_and_at_reviews_pending',
        'source_receipt_sha256': sha(source_receipt_raw),
        'rules_sha256': sha(RULES_PATH.read_bytes()), 'edits_sha256': sha(EDITS_PATH.read_bytes()),
        'shared_edits_sha256': sha(SHARED_EDITS_PATH.read_bytes()),
        'asset_manifest_sha256': sha(assets[f'translation/{UNIT}.assets.json']),
        'counts': {
            'register_tracks': 3, 'direct_children_per_track': 31, 'source_ids': 111,
            'source_mathml': 21, 'rendered_mathml': 63, 'source_msup': 3,
            'source_tables': 4, 'source_physical_table_rows': 35,
            'rendered_tables': 12, 'rendered_physical_table_rows': 105,
            'source_images': 23, 'embedded_images': 69, 'source_image_bytes': 1603339,
            'prose_fixtures': 11, 'question_parts': 12, 'supplied_answers': 12,
            'absent_answers': 0, 'target_accessibility_corrections': 6,
            'numeric_sequence_exceptions': 3, 'transcripts': 3, 'ssml_files': 3,
            'synthesized_audio_files': 0,
        },
        'next_source_cursor': {'section': NEXT_SECTION, 'first_paragraph': NEXT_FIRST_PARAGRAPH},
        'checks': [
            'byte_identical_source_and_target_replay', 'exact_fixture_tree_and_anchor_ordinal_dispatch',
            'generic_math_table_media_and_notation_fallback_rejected',
            'six_corrections_bound_to_source_id_attribute_old_value_target_value_and_asset_hash',
            'only_rows_72_75_89_have_numeric_sequence_exceptions',
            'all_23_authority_manifest_git_blob_sha256_size_geometry_and_jpeg_mime_checks',
            'all_12_questions_spoken_unevaluated_and_all_12_source_answers_preserved',
            'six_outer_untitled_solution_cues_and_no_answer_fixture_before_cue',
            'four_tables_read_once_with_35_physical_rows_and_no_aria_plus_row_duplication',
            '31_exact_source_marks_per_ssml_track_no_empty_spacing_paragraph',
            'explicit_root_locales_no_voice_or_language_fallback',
            'offline_embedded_reader_unique_ids_local_links_and_exact_jpeg_payloads',
        ],
        'exclusions': [
            NEXT_SECTION, NEXT_FIRST_PARAGRAPH, 'later_m82453_sections', 'whole_A10_completion',
            'whole_AX2_completion', 'generic_notation_speech', 'audio_synthesis',
            'native_educator_approval', 'human_visual_approval', 'screen_reader_approval',
            'assistive_technology_approval', 'classroom_approval', 'listening_approval',
        ],
        'source_pivot_changed': False, 'generic_numeric_exception': False,
        'hidden_language_fallback': False, 'hidden_voice_fallback': False,
        'human_language_review': False, 'human_visual_review': False,
        'screen_reader_review': False, 'assistive_technology_review': False,
        'classroom_review': False, 'listening_review': False,
        'whole_module_complete': False, 'full_ax2_complete': False,
        'output_sha256': receipt_outputs,
    }
    generated[PRODUCTION_RECEIPT] = (json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode()
    return generated


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    arguments = parser.parse_args()
    generated = products()
    assert generated == products(), 'Nondeterministic order-of-operations production build'
    for path, raw in generated.items():
        if arguments.check:
            assert (LANG / path).read_bytes() == raw, f'Stale order-of-operations output: {path}'
        else:
            write_bytes(LANG / path, raw)
    print('Complete order-of-operations section: three-track CNXML, offline reader, transcripts, SSML, assets, and receipts verified; human and AT reviews pending.')


if __name__ == '__main__':
    main()
