"""Build the dedicated three-track reader and finite narration products."""
from __future__ import annotations

import argparse
import base64
import html
import json
import re
import xml.etree.ElementTree as ET
import zipfile

from build import STYLE, render
from config import DOWNLOADS, LANG, TRACKS, UPSTREAM_COMMIT
from draft_evaluation import products as draft_products
from evaluation_checks import (ASSETS_SHA256, CANON_LOCK_SHA256, RULES_SHA256,
                               SECTION, TRACKS as EVALUATION_TRACKS, UNIT,
                               blocks, load_rules, load_variants, sha,
                               validate_assets)
from prepare_evaluation_assets import products as asset_products
from qa import Reader
from safe_io import write_bytes

BUILD_RECEIPT = f'qa/{UNIT}.production-build.in-progress.json'
HTML_PATH = f'review/units/{UNIT}.html'
LOCALES = {'jv-academic': 'jv-Latn-ID', 'jv-conversation': 'jv-Latn-ID',
           'id-academic': 'id-ID'}
LABELS = {'jv-academic': 'Jawa · ragam akademik',
          'jv-conversation': 'Jawa · ragam pacelathon',
          'id-academic': 'Indonesia · ragam akademik'}


def _saved_equal(generated: dict[str, bytes]) -> None:
    for path, raw in generated.items():
        assert (LANG / path).read_bytes() == raw, ('stale_required_product', path)


def _transcript(track: str, readout: list[tuple[str, str]]) -> bytes:
    lines = [f'# {UNIT} · {track}', '',
             'Finite source-bound transcript; no synthesized audio is included.', '']
    for anchor, text in readout:
        lines.extend([f'## {anchor}', '', text, ''])
    return ('\n'.join(lines).rstrip() + '\n').encode()


def _ssml(track: str, readout: list[tuple[str, str]]) -> bytes:
    # No voice/provider element and no locale substitution are authorized.
    paragraphs = []
    for anchor, text in readout:
        spoken = html.escape(text).replace('\n', '<break strength="medium"/>')
        paragraphs.append(
            f'<p><mark name="m82453--{html.escape(anchor, quote=True)}"/>{spoken}</p>')
    body = ''.join(paragraphs)
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<speak version="1.1" xml:lang="{LOCALES[track]}">{body}</speak>\n').encode()


def _page(variants: dict[str, ET.Element], media: dict[str, dict],
          readouts: dict[str, list[tuple[str, str]]]) -> bytes:
    title = html.escape(variants['jv-academic'].findtext('{*}title') or '')
    pieces = [
        '<!doctype html><html lang="jv-Latn-ID"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        f'<title>{html.escape(UNIT)}</title><style>{STYLE}</style></head><body><main>',
        f'<header id="{UNIT}"><div class="eyebrow">A10 · m82453</div>',
        f'<h1>{title}</h1>',
        '<p class="status">Pratinjau telung ragam sing kaiket ing sumber. '
        'Ora ana audio sintesis utawa klaim panutur asli. '
        'Lima gambar ing kolom Indonesia njaga label piksel Inggris saka sumber '
        'pinned; alt Indonesia lan transkrip menehi katrangan basa Indonesia.</p>',
        f'<p class="source">Bagean sumber lengkap: {SECTION}; 13 anak langsung; '
        'bagean istilah sejenis sabanjure ora kalebu.</p></header>',
        # Stable incoming target requested by the independently built like-terms unit.
        '<span id="fs-id1170655171250" data-cross-unit-alias="true"></span>',
    ]
    for track in EVALUATION_TRACKS:
        pieces.append(
            f'<span id="{UNIT}--{track}--{SECTION}" data-source-id="{SECTION}"></span>')
    for index in range(13):
        pieces.append('<div class="parallel">')
        for track in EVALUATION_TRACKS:
            prefix = f'{UNIT}--{track}--'
            pieces.append(
                f'<article class="track" lang="{LOCALES[track]}" data-register="{track}">'
                f'<div class="register">{html.escape(LABELS[track])}</div>'
                + render(variants[track][index], prefix, media[track]) + '</article>')
        pieces.append('</div>')
    pieces.extend([
        '<footer><p>Transkrip lan SSML iku teks offline sing kaiket ing sumber. '
        'Panyemak basa, pocapan, ngrungokake, browser, lan screen reader durung '
        'menehi persetujuan.</p></footer></main></body></html>\n'])
    page = ''.join(pieces).encode()
    # The readout argument is intentional authority: page and audio cover the same 13 blocks.
    assert all(len(readouts[track]) == 13 for track in EVALUATION_TRACKS)
    return page


def _validate_reader(page: bytes, variants: dict[str, ET.Element],
                     media_manifest: dict, media: dict[str, dict]) -> dict:
    text = page.decode()
    reader = Reader()
    reader.feed(text)
    assert len(reader.ids) == len(set(reader.ids)) == 251
    assert reader.maths == 38 * 3 == 114
    assert len(reader.images) == 16 * 3 == 48
    assert len(re.findall(r'<table\b', text)) == 5 * 3 == 15
    assert reader.links == []
    assert reader.tracks.count(('jv-academic', 'jv-Latn-ID')) == 13
    assert reader.tracks.count(('jv-conversation', 'jv-Latn-ID')) == 13
    assert reader.tracks.count(('id-academic', 'id-ID')) == 13
    assert 'fs-id1170655171250' in reader.ids
    for track in EVALUATION_TRACKS:
        prefix = f'{UNIT}--{track}--'
        for node in variants[track].iter():
            if node.get('id'):
                assert prefix + node.get('id') in reader.ids
    assert all(row.get('alt') for row in reader.images)
    assert all(re.fullmatch(r'data:image/(?:jpeg|svg\+xml);base64,[A-Za-z0-9+/=]+',
                            row.get('src', '')) for row in reader.images)
    assets = {row['fixture_id']: row for row in media_manifest['assets']}
    for fixture_id in ('A10-EVAL-D14', 'A10-EVAL-D16'):
        source_src = assets[fixture_id]['source_src']
        effective = base64.b64encode(media['id-academic'][source_src]['bytes']).decode()
        assert text.count('data:image/jpeg;base64,' + effective) == 3
        canonical_member = assets[fixture_id]['canonical_authority']['archive_member']
        with zipfile.ZipFile(DOWNLOADS / 'openstax-full-pinned.zip') as archive:
            canonical = archive.read(canonical_member)
        assert base64.b64encode(canonical).decode() not in text
        assert sha(canonical) == assets[fixture_id]['canonical_authority']['sha256']
    return {'html_ids': 251, 'source_bound_track_ids': 249, 'mathml': 114,
            'images': 48, 'tables': 15, 'track_articles': 39,
            'links': 0, 'incoming_cross_unit_aliases': 1}


def products() -> dict[str, bytes]:
    # Re-run both upstream dedicated producers in memory; never trust stale files.
    _saved_equal(draft_products())
    _saved_equal(asset_products())
    rules, rules_raw = load_rules()
    variants = load_variants()
    asset_manifest, media = validate_assets(rules)
    readouts, bindings = {}, {}
    for track in EVALUATION_TRACKS:
        readouts[track], bindings[track] = blocks(
            variants['id-academic'], variants[track], track, rules, rules_raw)
    generated = {}
    for track in EVALUATION_TRACKS:
        generated[f'review/audio/{UNIT}.{track}.md'] = _transcript(track, readouts[track])
        generated[f'review/audio/{UNIT}.{track}.ssml'] = _ssml(track, readouts[track])
        ssml = ET.fromstring(generated[f'review/audio/{UNIT}.{track}.ssml'])
        assert ssml.tag == 'speak' and not list(ssml.iter('voice'))
        assert ssml.get('{http://www.w3.org/XML/1998/namespace}lang') == LOCALES[track]
        assert len(list(ssml.iter('mark'))) == 13
    page = _page(variants, media, readouts)
    generated[HTML_PATH] = page
    reader_counts = _validate_reader(page, variants, asset_manifest, media)
    assert all(b.canon['lock_sha256'] == CANON_LOCK_SHA256 for b in bindings.values())
    transcript_counts = {
        track: {'blocks': len(readouts[track]),
                'sha256': sha(generated[f'review/audio/{UNIT}.{track}.md']),
                'ssml_sha256': sha(generated[f'review/audio/{UNIT}.{track}.ssml'])}
        for track in EVALUATION_TRACKS
    }
    draft_receipt_path = LANG / f'qa/{UNIT}.production-draft.in-progress.json'
    receipt = {
        'schema': 'source-bound-unit-production-build-v1',
        'status': 'dedicated_complete_section_production_pass_global_inventory_integration_pending',
        'unit': UNIT, 'program': 'A10', 'module': 'm82453', 'section': SECTION,
        'source_ids': 83, 'source_direct_children': 13, 'source_mathml': 38,
        'source_msup': 12, 'source_tables': 5, 'source_table_rows': 21,
        'source_media': 16, 'source_exercises': 9, 'source_solutions': 9,
        'question_parts': 15, 'part_markers': 24, 'source_links': 0,
        'math_fixtures': 38, 'prose_fixtures': 18, 'table_fixtures': 5,
        'chart_fixtures': 16, 'reference_fixtures': 0,
        'prose_only_math_per_track': 28, 'standalone_math_per_track': 10,
        'untitled_solution_cues_per_track': 6, 'worked_solution_titles_per_track': 3,
        'register_tracks': 3, 'transcript_files': 3, 'ssml_files': 3,
        'source_draft_receipt_sha256': sha(draft_receipt_path.read_bytes()),
        'rules_sha256': RULES_SHA256, 'asset_manifest_sha256': ASSETS_SHA256,
        'canon': bindings['jv-academic'].canon,
        'assets': {
            'effective_jpegs': 16, 'javanese_label_derivatives': 10,
            'canonical_retained_as_effective': 14, 'indonesian_release_overrides': 2,
            'indonesian_english_pixel_label_disclosures': 5,
            'override_012b_sha256': 'fc469cf6cd1dfac09c4010af7d7606f1309033663fc0ddbf891813f1b5208b67',
            'override_013b_sha256': '31e05fe68d3807d96bca8c3c747a82bc0ccf1b08d2dbfdb70fc1dea36a025a1e',
            'canonical_012b_sha256_not_used': '8ec3ccd4ccb9745db4f7a2a14740c03abd00f61330ab6c0f3a6292a26a864b76',
            'canonical_013b_sha256_not_used': 'efa3a502dd3a5cceadc846d48d1aa6fe5fe3f48b9671183a7ab43143df6d19fb',
        },
        'reader': reader_counts, 'narration': transcript_counts,
        'answer_checks': 15, 'worked_table_rows_checked': 21,
        'negative_policy': {
            'generic_fallback': False, 'answer_invention': False,
            'broad_exceptions': False, 'provider_voice_fallback': False,
            'locale_fallback': False,
        },
        'installed_regression_tests': [
            f'scripts/test_evaluation_assets.py', f'scripts/test_evaluation_workflow.py'],
        'source_reference_policy': 'zero source links; no fabricated reference',
        'incoming_cross_unit_target': f'{UNIT}.html#fs-id1170655171250',
        'human_language_review': False, 'native_educator_review': False,
        'browser_visual_review': False, 'screen_reader_review': False,
        'pronunciation_review': False, 'synthesis': False, 'listening_review': False,
        'synthesized_audio_files': 0, 'whole_module_complete': False,
        'next_excluded_section': 'fs-id1170655163482',
        'next_excluded_first_paragraph': 'fs-id1170655355506',
        'next_cursor': 'independent production review, then coordinator-owned global inventory integration',
        'output_sha256': {path: sha(raw) for path, raw in sorted(generated.items())},
    }
    generated[BUILD_RECEIPT] = (json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode()
    return generated


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    generated = products()
    assert generated == products(), 'nondeterministic_evaluation_build'
    for path, raw in generated.items():
        if args.check:
            assert (LANG / path).read_bytes() == raw, ('stale_evaluation_build', path)
        else:
            write_bytes(LANG / path, raw)
    print('Evaluation reader, 3 finite transcripts and 3 provider-free SSML files verified.')


if __name__ == '__main__':
    main()
