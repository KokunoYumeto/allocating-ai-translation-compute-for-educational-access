"""Build one review reader and three SSML drafts from four exact source roots."""
import argparse
import html
import json
import xml.etree.ElementTree as ET

from build import STYLE, render
from build_units import sha
from config import LANG, TRACKS
from qa import Reader
from safe_io import write_bytes
from summary_checks import COMPONENTS, RULES_SHA256, UNIT, bind

MODULE = 'm81243'
LABELS = {
    'title': 'Outer module title · original path [0]',
    'metadata': 'Learning objectives · metadata path [1]',
    'recap': 'Key concepts · content path [2,6]',
    'glossary': 'Glossary · original path [3]',
}


def component_html(component, roots, track, media):
    prefix = f'{UNIT}--{track}--'
    root = roots[component]
    if component == 'metadata':
        abstract = root.find('{*}abstract')
        assert abstract is not None
        return ''.join(render(child, prefix, media) for child in abstract)
    return render(root, prefix, media)


def products():
    contexts = {track: bind(track) for track in TRACKS}
    generated = {}
    pieces = [
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
        '<title>m81243 source-positioned components</title><style>' + STYLE + '</style></head><body><main>',
        '<header><div class="eyebrow">A00 · jv-Latn-ID / id-ID</div>',
        '<h1>m81243 source-positioned front, recap and back matter</h1>',
        '<p class="source">Exact original paths [0], [1], [2,6] and [3]; this is not a contiguous or complete module.</p>',
        '<p class="status">Three-register AI-assisted draft. Native-language, educator, integrated-browser, screen-reader and listening review remain pending; no audio was synthesized.</p>',
        '<p><a href="../pilot.html">Initial reader</a> · <a href="../../NEXT_UNIT.md">Continuation</a></p></header>',
    ]
    for component in COMPONENTS:
        pieces.append('<section class="component" data-original-path="' +
                      html.escape(json.dumps({'title':[0], 'metadata':[1], 'recap':[2,6], 'glossary':[3]}[component])) + '">')
        pieces.append('<h2 data-editorial-ui="true">' + html.escape(LABELS[component]) + '</h2>')
        pieces.append('<div class="parallel">')
        for track, (locale, label) in TRACKS.items():
            roots, _, media, _ = contexts[track]
            pieces.append(f'<article class="track" lang="{locale}" data-register="{track}"><div class="register">{html.escape(label)}</div>')
            pieces.append(component_html(component, roots, track, media))
            pieces.append('</article>')
        pieces.append('</div></section>')
    pieces.append('<section class="note-box"><h2>Narration drafts</h2><ul>')
    for track, (locale, label) in TRACKS.items():
        _, blocks, _, rules = contexts[track]
        transcript = '# ' + label + '\n\nStatus: narration draft; not synthesized or listening-reviewed.\n\n'
        transcript += '\n\n'.join(f'## {mark}\n\n{body}' for mark, body in blocks) + '\n'
        stem = f'review/audio/{UNIT}.{track}'
        generated[stem + '.md'] = transcript.encode()
        ssml = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<speak xmlns="http://www.w3.org/2001/10/synthesis" version="1.1" xml:lang="{locale}">'
                f'<p>{html.escape(label)}</p>\n')
        ssml += ''.join(f'<mark name="{html.escape(mark, quote=True)}"/><p>{html.escape(body)}</p><break time="600ms"/>\n'
                        for mark, body in blocks)
        ssml += '</speak>\n'
        document = ET.fromstring(ssml)
        assert [node.get('name') for node in document.findall('{*}mark')] == rules['reader_and_ssml_contract']['block_marks']
        generated[stem + '.ssml'] = ssml.encode()
        pieces.append(f'<li><span lang="{locale}">{html.escape(label)}</span>: <a href="../audio/{UNIT}.{track}.md">Transcript</a> / <a href="../audio/{UNIT}.{track}.ssml">SSML</a></li>')
    pieces.append('</ul></section>')
    pieces.append('<footer><p>Unofficial AI-assisted adaptation of OpenStax through the Indonesian editions by KokunoYumeto. Rice University/OpenStax, CC BY-NC-SA 4.0, subject to inherited component notices. No endorsement. <a href="../../ATTRIBUTION.md">Full attribution and original notices</a>.</p></footer></main></body></html>')
    page = '\n'.join(pieces)
    inspection = Reader()
    inspection.feed(page)
    assert len(inspection.ids) == len(set(inspection.ids)) == 69
    assert len(inspection.tracks) == 12 and inspection.maths == 0
    assert len(inspection.images) == 3 and all(image.get('alt') and
                                                image['src'].startswith('data:image/svg+xml;base64,')
                                                for image in inspection.images)
    assert '7cbc90c7-60c8-4211-bffe-b77aadc95509' not in page
    for track in TRACKS:
        roots = contexts[track][0]
        assert all(f'{UNIT}--{track}--{node.get("id")}' in inspection.ids
                   for component in COMPONENTS for node in roots[component].iter() if node.get('id'))
    generated[f'review/units/{UNIT}.html'] = page.encode()
    component_receipt = LANG / f'qa/{UNIT}.components-receipt.json'
    asset_manifest = LANG / f'translation/{UNIT}.assets.json'
    receipt = {
        'schema': 'source-positioned-components-build-v1',
        'status': 'structural_pass_human_review_pending',
        'unit': UNIT, 'program': 'A00', 'module': MODULE,
        'source_component_receipt_sha256': sha(component_receipt.read_bytes()),
        'source_component_paths': {'title':[0], 'metadata':[1], 'recap':[2,6], 'glossary':[3]},
        'source_ids': 23, 'source_math_expressions': 0, 'source_media_references': 1,
        'source_objectives': 6, 'source_glossary_definitions': 7,
        'source_bound_spoken_text_fixtures': 35, 'explicit_nonspoken_text_fixtures': 3,
        'source_marked_narration_blocks': 14,
        'register_tracks': 3, 'ssml_files': 3,
        'rules_sha256': RULES_SHA256,
        'asset_manifest_sha256': sha(asset_manifest.read_bytes()),
        'human_language_review': False, 'visual_review': False,
        'integrated_browser_review': False, 'screen_reader_review': False,
        'listening_review': False, 'synthesized_audio_files': 0,
        'whole_module_complete': False,
        'checks': ['four_exact_original_paths', 'complete_source_and_target_tree_replay',
                   'all_35_spoken_and_3_nonspoken_text_slots', 'one_exact_bound_chart',
                   'nine_source_step_cues', 'fourteen_source_positioned_marks',
                   'offline_reader_ids_locales_and_embedded_asset', 'deterministic_outputs'],
        'output_sha256': {name: sha(raw) for name, raw in sorted(generated.items())},
    }
    generated[f'qa/{UNIT}.components-build-receipt.json'] = (json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode()
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
    print('Four exact source-positioned components built as one reader plus three transcript/SSML drafts; no complete-module claim.')


if __name__ == '__main__':
    main()
