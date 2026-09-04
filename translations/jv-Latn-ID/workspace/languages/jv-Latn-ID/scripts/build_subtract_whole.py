"""Build the complete m81245 offline reader and finite narration tracks."""
import argparse
import hashlib
import html
import json
import re
import xml.etree.ElementTree as ET

import build as shared_build
from build import MATH, STYLE, XML_LANG, local
from config import LANG, TRACKS
from draft_subtract_whole import CORRECTION_IDS, products as draft_products
from qa import Reader
from safe_io import write_bytes
from subtract_whole_checks import UNIT, bind, blocks


BASE_RENDER = shared_build.render


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def track_from_prefix(prefix):
    for track in TRACKS:
        if prefix == f'{UNIT}--{track}--':
            return track
    raise ValueError('Unregistered subtraction render prefix')


def render(node, prefix, media, parent=''):
    """Extend the shared renderer only for this module's six exact links."""
    if local(node) != 'link':
        return BASE_RENDER(node, prefix, media, parent)
    track = track_from_prefix(prefix)
    content = html.escape(node.text or '') + ''.join(
        render(child, prefix, media, 'link') + html.escape(child.tail or '')
        for child in node)
    target = node.get('target-id')
    document = node.get('document')
    url = node.get('url')
    if document is not None:
        allowed = {
            ('m81244', 'fs-id1239606'),
            ('m81244', 'fs-id1988116'),
        }
        if (document, target) not in allowed or url is not None:
            raise ValueError('Unregistered cross-module subtraction reference')
        label = content.strip() or f'{document} · {target}'
        href = f'a00-add-whole.html#a00-add-whole--{track}--{target}'
        return (f'<a href="{html.escape(href, quote=True)}" '
                f'data-source-document="{document}" data-source-target-id="{target}">{label}</a>')
    if target is not None:
        if target != 'fs-id1549826' or url is not None:
            raise ValueError('Unregistered in-module subtraction reference')
        label = content.strip() or ('Tabel' if track == 'id-academic' else 'Tabel')
        return f'<a href="#{prefix}{target}">{label}</a>'
    allowed_urls = {
        'https://www.openstax.org/l/24sub2dignum',
        'https://www.openstax.org/l/24sub3dignum',
        'https://www.openstax.org/l/24subwholenum',
    }
    if url not in allowed_urls or not content.strip():
        raise ValueError('Unregistered external subtraction reference')
    return f'<a href="{html.escape(url, quote=True)}" rel="noreferrer">{content}</a>'


def render_bound(node, prefix, media, parent=''):
    """Install the six-link wrapper only for one source-bound render call."""
    previous = shared_build.render
    shared_build.render = render
    try:
        return render(node, prefix, media, parent)
    finally:
        shared_build.render = previous


def metadata_markup(root, prefix, media):
    metadata = root.find('{*}metadata')
    abstract = metadata.find('{*}abstract')
    assert abstract is not None and len(abstract) == 2
    return '<section class="note-box">' + ''.join(
        render_bound(child, prefix, media) for child in abstract) + '</section>'


def verify_cross_module_routes(links):
    target_page = LANG / 'review/units/a00-add-whole.html'
    raw = target_page.read_text(encoding='utf-8')
    routes = []
    expected_links = []
    for target in ('fs-id1239606', 'fs-id1988116'):
        fragments = {}
        for track in TRACKS:
            fragment = f'a00-add-whole--{track}--{target}'
            href = 'a00-add-whole.html#' + fragment
            assert raw.count(f'id="{fragment}"') == 1
            expected_links.append(href)
            fragments[track] = fragment
        routes.append({
            'document': 'm81244',
            'target_id': target,
            'reader_dependency': 'a00-add-whole.html',
            'track_fragments': fragments,
            'resolved_in_offline_reader': True,
        })
    actual = [link for link in links
              if link.startswith('a00-add-whole.html#a00-add-whole--')]
    assert sorted(actual) == sorted(expected_links)
    return routes


def products():
    bound = bind()
    source = bound.source
    source_ids = [node.get('id') for node in source.iter() if node.get('id')]
    content = source.find('{*}content')
    assert content is not None and len(content) == 9
    assert [node.get('id') for node in content] == [
        'fs-id2649398', 'fs-id1122445', 'fs-id1799687', 'fs-id1824154',
        'fs-id1185692', 'fs-id2567736', 'fs-id1828922', 'fs-id1379009',
        'fs-id2649429']

    pieces = [
        '<!DOCTYPE html><html lang="id-ID"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        '<title>a00-subtract-whole</title><style>' + STYLE + '</style></head><body><main>',
        '<header><div class="eyebrow">A00 · m81245 · jv-Latn-ID / id-ID</div>',
        '<h1 lang="jv-Latn-ID">Ngurangi Wilangan Cacah</h1>',
        '<p class="source" lang="en">Complete pinned m81245 source scope: metadata, five objectives, both readiness checks, five teaching sections, key concepts, all 84 end exercises, self-check, and outer glossary.</p>',
        '<p class="status">Draf produksi telung register. Rong katrangan gambar basa Jawa dibenerake kanthi wates ID, alt lawas, lan hash gambar. Pivot Indonesia lan gambar sumber tetep. Durung ana telaah penutur utawa pendidik Jawa, uji piranti bantu, utawa uji rungon.</p>',
        '<aside class="note-box" lang="id-ID"><p>Dua rujukan prasyarat mempertahankan rute sumber nyata ke m81244. Pembaca penjumlahan tujuannya masih menjadi dependensi keluaran terpisah; tidak dibuat stub dalam modul ini.</p><p>Tiga pranala sumber belajar daring dipertahankan, tetapi isinya tidak dibundel atau diambil oleh pembaca luring ini.</p></aside>',
        '</header>',
    ]

    # Metadata/objectives, each exact direct content child, and the outer
    # glossary remain source-positioned rather than being moved into a wrapper.
    pieces.append('<div class="parallel">')
    for track, (locale, label) in TRACKS.items():
        prefix = f'{UNIT}--{track}--'
        root = bound.variants[track]
        pieces.append(f'<article class="track" lang="{locale}" data-register="{track}">')
        pieces.append(f'<div class="register">{html.escape(label)}</div>')
        pieces.append('<h2>' + html.escape(root.findtext('{*}title')) + '</h2>')
        pieces.append(metadata_markup(root, prefix, bound.media[track]))
        pieces.append('</article>')
    pieces.append('</div>')

    for index in range(len(content)):
        pieces.append('<div class="parallel">')
        for track, (locale, label) in TRACKS.items():
            prefix = f'{UNIT}--{track}--'
            root_content = bound.variants[track].find('{*}content')
            pieces.append(f'<article class="track" lang="{locale}" data-register="{track}">')
            pieces.append(f'<div class="register">{html.escape(label)}</div>')
            pieces.append(render_bound(root_content[index], prefix, bound.media[track]))
            pieces.append('</article>')
        pieces.append('</div>')

    pieces.append('<div class="parallel">')
    for track, (locale, label) in TRACKS.items():
        prefix = f'{UNIT}--{track}--'
        glossary = bound.variants[track].find('{*}glossary')
        pieces.append(f'<article class="track" lang="{locale}" data-register="{track}">')
        pieces.append(f'<div class="register">{html.escape(label)}</div>')
        pieces.append(render_bound(glossary, prefix, bound.media[track]))
        pieces.append('</article>')
    pieces.append('</div>')

    generated = {}
    block_counts = {}
    pieces.append('<section class="note-box"><h2>Naskah audio</h2><ul>')
    for track, (locale, label) in TRACKS.items():
        narration = blocks(track, bound)
        block_counts[track] = len(narration)
        assert all(body for _, body in narration)
        transcript = ('# ' + label
                      + '\n\nStatus: narration draft; not synthesized or listening-reviewed. '
                        'Every block is rebound to the complete finite m81245 contract.\n\n')
        transcript += '\n\n'.join(
            f'## m81245--{key}\n\n{body}' for key, body in narration) + '\n'
        stem = f'review/audio/{UNIT}.{track}'
        generated[stem + '.md'] = transcript.encode()
        ssml = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<speak xmlns="http://www.w3.org/2001/10/synthesis" version="1.1" xml:lang="{locale}">'
                f'<p>{html.escape(label)}</p>\n')
        ssml += ''.join(
            f'<mark name="m81245--{html.escape(key, quote=True)}"/>'
            f'<p>{html.escape(body)}</p><break time="600ms"/>\n'
            for key, body in narration)
        ssml += '</speak>\n'
        parsed = ET.fromstring(ssml)
        assert parsed.get(XML_LANG) == locale
        assert [node.get('name') for node in parsed.findall('{*}mark')] == [
            'm81245--' + key for key, _ in narration]
        generated[stem + '.ssml'] = ssml.encode()
        pieces.append(
            f'<li><span lang="{locale}">{html.escape(label)}</span>: '
            f'<a href="../audio/{UNIT}.{track}.md">Naskah</a> / '
            f'<a href="../audio/{UNIT}.{track}.ssml">SSML</a></li>')
    pieces.append('</ul></section>')
    pieces.append('<footer lang="en"><p>Unofficial AI-assisted adaptation of OpenStax Prealgebra 2e through the Indonesian edition by KokunoYumeto. Rice University/OpenStax, CC BY-NC-SA 4.0, subject to inherited component notices. No endorsement. <a href="../../ATTRIBUTION.md">Full attribution and original notices</a>.</p><p>Source IDs, mathematics, order, 83 supplied answers, 42 absent answers, figures, references, and source units are retained. No native-language, educator, browser, screen-reader, pronunciation, or listening approval is claimed.</p></footer>')
    pieces.append('</main></body></html>')
    page = '\n'.join(pieces).encode()
    generated[f'review/units/{UNIT}.html'] = page

    inspection = Reader()
    inspection.feed(page.decode())
    assert len(inspection.ids) == len(set(inspection.ids)) == 3 * len(source_ids)
    assert inspection.maths == 3 * 262
    assert len(inspection.images) == 3 * 55
    assert all(image.get('alt') and image['src'].startswith('data:image/')
               for image in inspection.images)
    assert inspection.tracks == [
        (track, locale) for _ in range(11) for track, (locale, _) in TRACKS.items()]
    for track in TRACKS:
        prefix = f'{UNIT}--{track}--'
        assert all(prefix + source_id in inspection.ids for source_id in source_ids)
    assert sum(link.startswith('a00-add-whole.html#a00-add-whole--')
               for link in inspection.links) == 6
    assert sum(link.startswith('https://www.openstax.org/l/24sub') for link in inspection.links) == 9
    assert sum(link.startswith('#' + UNIT + '--') for link in inspection.links) == 3
    cross_module_routes = verify_cross_module_routes(inspection.links)

    draft_receipt_path = f'qa/{UNIT}.in-progress.json'
    draft_receipt_raw = draft_products()[draft_receipt_path]
    receipt = {
        'schema': 'jv-complete-module-build-v1',
        'unit': UNIT,
        'module': 'm81245',
        'status': 'complete_source_production_structural_pass_human_reviews_pending',
        'complete_module_source': True,
        'whole_module_complete': False,
        'full_assignment_complete': False,
        'source_draft_receipt_sha256': sha(draft_receipt_raw),
        'rules_sha256': sha((LANG / f'audio/{UNIT}.rules.json').read_bytes()),
        'asset_manifest_sha256': sha((LANG / f'translation/{UNIT}.assets.json').read_bytes()),
        'counts': {
            'source_ids': 716, 'source_mathml': 262, 'source_media': 55,
            'source_tables': 17, 'source_exercises': 125,
            'supplied_solutions': 83, 'absent_solutions': 42,
            'references': 6, 'reader_track_articles': 33,
            'reader_ids': len(inspection.ids), 'reader_mathml': inspection.maths,
            'reader_images': len(inspection.images),
            'narration_blocks': block_counts, 'transcripts': 3, 'ssml': 3,
        },
        'accessibility_rebinding': {
            'corrected_media_ids': list(CORRECTION_IDS),
            'policy': 'Javanese alt only; exact ID + old alt + source ref + image SHA-256; Indonesian pivot and all image bytes unchanged',
        },
        'cross_module_routes': cross_module_routes,
        'checks': [
            'complete_source_and_corrected_target_replay',
            '716_id_and_262_mathml_finite_binding',
            '55_asset_hashes_and_mime_types',
            '17_finite_table_readouts', '55_independent_diagram_readouts',
            '125_question_and_83_answer_playback_boundaries',
            '42_source_absent_answers_have_no_answer_blocks',
            'six_exact_reference_routes',
            'two_narrow_target_alt_repairs',
            'three_explicit_locale_and_register_tracks',
            'deterministic_reader_transcripts_and_ssml',
        ],
        'external_source_links_fetched': False,
        'provider_calls': 0,
        'synthesized_audio_files': 0,
        'native_language_review': False,
        'educator_review': False,
        'integrated_visual_review': False,
        'assistive_technology_review': False,
        'pronunciation_review': False,
        'listening_review': False,
        'output_sha256': {path: sha(raw) for path, raw in generated.items()},
    }
    generated[f'qa/{UNIT}.in-progress.json'] = (
        json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode()
    return generated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    generated = products()
    assert generated == products(), 'Nondeterministic complete subtraction build'
    for path, raw in generated.items():
        if args.check:
            assert (LANG / path).read_bytes() == raw, f'Stale subtraction output: {path}'
        else:
            write_bytes(LANG / path, raw)
    print('a00-subtract-whole: complete offline reader and three transcript/SSML tracks verified; human reviews pending.')


if __name__ == '__main__':
    main()
