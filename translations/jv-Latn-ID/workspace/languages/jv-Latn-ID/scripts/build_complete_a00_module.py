"""Build the complete-source-scope m81243 review reader and aggregate SSML."""
import argparse
import html
import json
import xml.etree.ElementTree as ET

from build import STYLE, render
from build_units import sha
from complete_a00_checks import (ASSEMBLY_RECEIPT_SHA256, asset_map,
                                 checked_assembly, full_blocks,
                                 rounding_editorial_material)
from config import LANG, TRACKS
import draft_complete_a00_module as complete
from qa import Reader
from safe_io import write_bytes

LABELS = {
    'title': 'Outer module title · original path [0]',
    'metadata': 'Learning objectives · metadata path [1]',
    'glossary': 'Outer glossary · original path [3]',
}


def render_parallel(pieces, label, nodes, media):
    pieces.append('<section class="complete-component"><h2 data-editorial-ui="true">' + html.escape(label) + '</h2><div class="parallel">')
    for track, (locale, register) in TRACKS.items():
        node = nodes[track]
        if label.startswith('Learning objectives'):
            abstract = node.find('{*}abstract')
            assert abstract is not None
            markup = ''.join(render(child, f'{complete.UNIT}--{track}--', media[track])
                             for child in abstract)
        else:
            markup = render(node, f'{complete.UNIT}--{track}--', media[track])
        pieces.append(f'<article class="track" lang="{locale}" data-register="{track}"><div class="register">{html.escape(register)}</div>{markup}</article>')
    pieces.append('</div></section>')


def products():
    roots, assembly = checked_assembly()
    media, asset_dependencies = {}, {}
    for track in TRACKS:
        media[track], bound = asset_map(track, roots[track])
        asset_dependencies.update(bound)
    blocks, audio_dependencies = {}, {}
    for track in TRACKS:
        blocks[track], bound = full_blocks(track)
        audio_dependencies.update(bound)
    notices, notice_dependencies = rounding_editorial_material()
    audio_dependencies.update(notice_dependencies)

    pieces = [
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
        '<title>Complete m81243 review draft</title><style>' + STYLE + '</style></head><body><main>',
        '<header><div class="eyebrow">A00 · m81243 · jv-Latn-ID / id-ID</div>',
        '<h1>Complete source-scope review draft</h1>',
        '<p class="source">All original document roots and all eight content sections, in exact source order.</p>',
        '<p class="status">Cross-component automated review draft. Native-language, educator, integrated-browser, screen-reader and listening review remain pending; no audio was synthesized.</p>',
        '<p><a href="../pilot.html">Initial reader</a> · <a href="../../NEXT_UNIT.md">Continuation</a></p></header>',
        '<aside class="note-box" lang="id-ID"><p>' + html.escape(notices['indonesian_accessibility_notice']) + '</p><p>' + html.escape(notices['offline_link_notice']) + '</p></aside>',
    ]
    render_parallel(pieces, LABELS['title'], {track: root[0] for track, root in roots.items()}, media)
    render_parallel(pieces, LABELS['metadata'], {track: root[1] for track, root in roots.items()}, media)
    for index, (anchor, _) in enumerate(complete.SECTION_UNITS):
        render_parallel(pieces, f'Content section {index + 1} of 8 · {anchor}',
                        {track: root[2][index] for track, root in roots.items()}, media)
    render_parallel(pieces, LABELS['glossary'], {track: root[3] for track, root in roots.items()}, media)
    pieces.append('<section class="note-box"><h2>Complete-module narration drafts</h2><ul>')
    generated = {}
    for track, (locale, label) in TRACKS.items():
        transcript = '# ' + label + '\n\nStatus: complete-source-scope narration draft; not synthesized or listening-reviewed.\n\n'
        if track == 'id-academic':
            transcript += notices['indonesian_accessibility_notice'] + '\n\n'
        transcript += '\n\n'.join(f'## {mark}\n\n{body}' for mark, body in blocks[track]) + '\n'
        stem = f'review/audio/{complete.UNIT}.{track}'
        generated[stem + '.md'] = transcript.encode()
        ssml = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<speak xmlns="http://www.w3.org/2001/10/synthesis" version="1.1" xml:lang="{locale}">'
                f'<p>{html.escape(label)}</p>\n')
        if track == 'id-academic':
            ssml += '<p>' + html.escape(notices['indonesian_accessibility_notice']) + '</p>\n'
        ssml += ''.join(f'<mark name="{html.escape(mark, quote=True)}"/><p>{html.escape(body)}</p><break time="600ms"/>\n'
                        for mark, body in blocks[track])
        ssml += '</speak>\n'
        document = ET.fromstring(ssml)
        assert [node.get('name') for node in document.findall('{*}mark')] == [mark for mark, _ in blocks[track]]
        expected_notice_count = 1 if track == 'id-academic' else 0
        assert sum(''.join(node.itertext()) == notices['indonesian_accessibility_notice']
                   for node in document.findall('{*}p')) == expected_notice_count
        assert transcript.count(notices['indonesian_accessibility_notice']) == expected_notice_count
        generated[stem + '.ssml'] = ssml.encode()
        pieces.append(f'<li><span lang="{locale}">{html.escape(label)}</span>: <a href="../audio/{complete.UNIT}.{track}.md">Transcript</a> / <a href="../audio/{complete.UNIT}.{track}.ssml">SSML</a></li>')
    pieces.append('</ul></section><footer><p>Unofficial AI-assisted adaptation of OpenStax through the Indonesian editions by KokunoYumeto. Rice University/OpenStax, CC BY-NC-SA 4.0, subject to inherited component notices. No endorsement. <a href="../../ATTRIBUTION.md">Full attribution and original notices</a>.</p></footer></main></body></html>')
    page = '\n'.join(pieces)
    reader = Reader()
    reader.feed(page)
    assert len(reader.ids) == len(set(reader.ids)) == 1884
    assert len(reader.tracks) == 33
    assert reader.maths == 747
    assert len(reader.images) == 141 and all(image.get('alt') and image['src'].startswith('data:image/')
                                             for image in reader.images)
    assert '7cbc90c7-60c8-4211-bffe-b77aadc95509' not in page
    assert page.count(notices['indonesian_accessibility_notice']) == 1
    assert page.count(notices['offline_link_notice']) == 1
    for track, root in roots.items():
        assert all(f'{complete.UNIT}--{track}--{node.get("id")}' in reader.ids
                   for node in root.iter() if node.get('id'))
    for link in reader.links:
        if link.startswith('#'):
            assert link[1:] in reader.ids
        elif link.startswith('http'):
            assert link in ('https://www.openstax.org/l/24detplaceval',
                            'https://www.openstax.org/l/24numdigword')
        else:
            resolved = (LANG / 'review/units' / link).resolve()
            relative = resolved.relative_to(LANG.resolve()).as_posix()
            assert resolved.is_file() or relative in generated
    generated[f'review/units/{complete.UNIT}.html'] = page.encode()
    dependencies = {f'qa/{complete.UNIT}.assembly-receipt.json': ASSEMBLY_RECEIPT_SHA256}
    dependencies.update(asset_dependencies)
    dependencies.update(audio_dependencies)
    receipt = {
        'schema': 'complete-source-scope-module-build-v1',
        'status': 'structural_pass_independent_cross_component_review_pending',
        'unit': complete.UNIT, 'program': 'A00', 'module': complete.MODULE,
        'source_assembly_receipt_sha256': ASSEMBLY_RECEIPT_SHA256,
        'source_ids': 628, 'source_math_expressions': 249,
        'source_media_references': 47, 'source_exercises': 88,
        'source_solutions_present': 59, 'source_tables': 8,
        'source_glossary_definitions': 7, 'source_marked_narration_blocks': 183,
        'unmarked_editorial_notices': {
            'complete_id_reader': 2, 'complete_id_transcript': 1,
            'complete_id_ssml': 1, 'javanese_transcripts_and_ssml': 0,
        },
        'register_tracks': 3, 'ssml_files': 3,
        'complete_source_scope': True,
        'independent_cross_component_review': 'pending',
        'human_language_review': False, 'visual_review': False,
        'integrated_browser_review': False, 'screen_reader_review': False,
        'listening_review': False, 'synthesized_audio_files': 0,
        'whole_module_complete': False,
        'checks': ['exact_complete_module_assembly_receipt', 'all_628_source_IDs_rendered_per_track',
                   'all_249_MathML_rendered_per_track', 'all_47_media_manifest_bound_per_track',
                   'all_183_existing_narration_blocks_reordered_without_body_changes',
                   'reviewed_unmarked_rounding_notices_carried_without_new_marks',
                   'derived_unique_section_title_marks', 'complete_source_order',
                   'offline_links_and_attribution', 'deterministic_outputs'],
        'verified_dependency_sha256': dict(sorted(dependencies.items())),
        'output_sha256': {name: sha(raw) for name, raw in sorted(generated.items())},
    }
    generated[f'qa/{complete.UNIT}.build-receipt.json'] = (json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode()
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
    print('Complete-source-scope m81243 reader and three aggregate SSML drafts built; independent review pending.')


if __name__ == '__main__':
    main()
