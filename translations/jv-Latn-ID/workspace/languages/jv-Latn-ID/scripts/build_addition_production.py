"""Build the complete three-track m81244 reader and finite SSML drafts."""
import argparse
import base64
import hashlib
import html
import json
import re
import xml.etree.ElementTree as ET

from build import MATH, STYLE, local, math_html
from config import LANG, TRACKS
from qa import Reader
from safe_io import write_bytes
import addition_production_checks as checks
import draft_addition_production as draft
import prepare_addition_production_assets as asset_producer


UNIT = draft.UNIT
RECEIPT = f'qa/{UNIT}.production-receipt.json'
ALLOWED_EXTERNAL = {
    'https://www.openstax.org/l/24add2blocks',
    'https://www.openstax.org/l/24add3blocks',
    'https://www.openstax.org/l/24addwhlnumb',
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def link_cues(rules, track):
    cues = {}
    for row in rules['structural_cues']:
        if row['source_tree'].lstrip().startswith('<n1:link'):
            key = row['variant_tree_sha256'][track]
            if key in cues:
                raise ValueError('Duplicate registered link tree')
            cues[key] = row
    if len(cues) != 8:
        raise ValueError('Expected eight registered source links')
    return cues


def render(element, prefix, media, track, cues, parent=''):
    tag = local(element)
    if tag == 'newline':
        return '<br>'
    if element.tag.startswith('{' + MATH + '}'):
        return math_html(element)
    attrs = ''
    if element.get('id'):
        source_id = html.escape(element.get('id'), quote=True)
        attrs += f' id="{prefix}{source_id}" data-source-id="{source_id}"'
    content = html.escape(element.text or '') + ''.join(
        render(child, prefix, media, track, cues, tag) + html.escape(child.tail or '')
        for child in element)
    if tag == 'link':
        fixture = cues.get(checks.tree_sha(element))
        if fixture is None:
            raise ValueError('Unregistered addition reader link')
        label = content.strip() or html.escape(fixture['expected'][track])
        target, url, document = (element.get('target-id'), element.get('url'),
                                 element.get('document'))
        if dict(element.attrib) != fixture['source_attributes']:
            raise ValueError('Registered source link attributes changed')
        if url is not None:
            if url not in ALLOWED_EXTERNAL or target is not None or document is not None:
                raise ValueError('Unregistered external source link')
            return (f'<a{attrs} href="{html.escape(url, quote=True)}" rel="noreferrer" '
                    f'data-source-url="{html.escape(url, quote=True)}">{label}</a>')
        if target is None:
            raise ValueError('Source link has neither registered target nor URL')
        if document is None:
            href = '#' + prefix + target
        elif document == 'm81243':
            href = (f'{document.replace("m81243", "a00-m81243-complete")}.html#'
                    f'a00-m81243-complete--{track}--{target}')
        else:
            raise ValueError('Unregistered cross-module link')
        document_attr = (f' data-source-document="{html.escape(document, quote=True)}"'
                         if document else '')
        return (f'<a{attrs} href="{html.escape(href, quote=True)}" '
                f'data-source-target-id="{html.escape(target, quote=True)}"{document_attr}>{label}</a>')
    if tag == 'image':
        return ''
    if tag == 'media':
        image = element.find('{*}image')
        if image is None or image.get('src') not in media:
            raise ValueError('Unregistered addition media output')
        asset = media[image.get('src')]
        encoded = base64.b64encode(asset['bytes']).decode('ascii')
        return (f'<span{attrs}><img src="data:{asset["mime_type"]};base64,{encoded}" '
                f'alt="{html.escape(element.get("alt", ""), quote=True)}" '
                f'data-source-src="{html.escape(image.get("src"), quote=True)}"></span>')
    if tag in ('tgroup', 'colspec', 'label'):
        return content
    tags = {
        'abstract': 'section', 'section': 'section', 'glossary': 'section',
        'definition': 'div', 'title': 'h4' if parent == 'solution' else 'h3',
        'para': 'p', 'term': 'strong', 'meaning': 'p', 'note': 'aside',
        'equation': 'div', 'figure': 'figure', 'caption': 'figcaption',
        'example': 'div', 'exercise': 'div', 'problem': 'div', 'solution': 'div',
        'list': 'ul', 'item': 'li', 'span': 'span', 'emphasis': 'em',
        'table': 'table', 'thead': 'thead', 'tbody': 'tbody', 'row': 'tr',
        'entry': 'td',
    }
    output_tag = tags.get(tag)
    if output_tag is None:
        raise ValueError('Unmapped addition CNXML element: ' + tag)
    if tag == 'list':
        kind = element.get('list-type', 'bulleted')
        attrs += f' data-source-list-type="{html.escape(kind, quote=True)}"'
        if kind == 'enumerated':
            styles = {'arabic': '1', 'lower-alpha': 'a', 'upper-alpha': 'A',
                      'lower-roman': 'i', 'upper-roman': 'I'}
            style = element.get('number-style', 'arabic')
            if style not in styles:
                raise ValueError('Unregistered enumerated-list style')
            output_tag = 'ol'
            attrs += f' type="{styles[style]}"'
        elif kind == 'labeled-item':
            attrs += ' class="source-labeled-list"'
        elif kind != 'bulleted':
            raise ValueError('Unregistered source list type')
    if tag == 'table':
        label = element.get('aria-label') or element.get('summary')
        if label:
            attrs += f' aria-label="{html.escape(label, quote=True)}"'
        content = re.sub(
            r'<thead>(.*?)</thead>',
            lambda match: '<thead>' + match.group(1).replace(
                '<td>', '<th scope="col">').replace('</td>', '</th>') + '</thead>',
            content, flags=re.S)
    if tag == 'solution':
        attrs += ' class="solution"'
        if element.find('{*}title') is None:
            cue = 'Wangsulan' if track.startswith('jv') else 'Jawaban'
            content = (f'<h4 data-editorial-solution-cue="true">{cue}</h4>' + content)
    if tag in ('note', 'example'):
        source_class = element.get('class', '')
        attrs += f' class="{tag} {html.escape(source_class, quote=True)}"'
    return f'<{output_tag}{attrs}>{content}</{output_tag}>'


def media_maps(manifest):
    result = {track: {} for track in TRACKS}
    for asset in manifest['assets']:
        for track in TRACKS:
            output = asset['outputs'][track]
            raw = (LANG / output['path']).read_bytes()
            if sha(raw) != output['sha256'] or len(raw) != output['bytes']:
                raise ValueError('Changed addition asset output')
            result[track][asset['source_src']] = {
                'bytes': raw, 'mime_type': output['mime_type']}
    if any(len(rows) != 50 for rows in result.values()):
        raise ValueError('Incomplete addition reader media map')
    return result


def page_and_audio(source, variants, rules, edits, media):
    block_sets = {}
    for track in TRACKS:
        block_sets[track] = checks.narration_blocks(
            source, variants[track], rules, track, edits)
    groups = [('title', [0]), ('objectives', [1, 2])]
    groups += [(f'content-{index + 1:02d}', [2, index]) for index in range(9)]
    groups.append(('glossary', [3]))
    pieces = [
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        '<title>m81244 · Addition / Nambah Wilangan Cacah</title><style>', STYLE,
        '.production-note{border-left:4px solid #986d18;background:#fff4d7;padding:16px}'
        '.module-group{border-top:2px solid var(--accent);padding-top:24px;margin-top:30px}'
        '</style></head><body><main>',
        '<header><div class="eyebrow">A00 · m81244 · complete pinned source scope</div>',
        '<h1><span lang="jv-Latn-ID">Nambah Wilangan Cacah</span> / '
        '<span lang="id-ID">Menjumlahkan Bilangan Cacah</span></h1>',
        '<p class="production-note">Draf produksi struktural telung trek. '
        'Durung ana telaah basa manungsa, telaah screen reader, sintesis swara, utawa uji rungon.</p>',
        '<p><a href="../../ATTRIBUTION.md">Attribution and inherited notices</a></p></header>',
    ]
    for group_index, (group_name, path) in enumerate(groups, 1):
        pieces.append(f'<section class="module-group" id="{UNIT}--group-{group_index:02d}" '
                      f'data-editorial-group="{group_name}">')
        pieces.append(f'<h2 data-editorial-ui="true">Source group {group_index:02d} · {group_name}</h2>')
        pieces.append('<div class="parallel">')
        for track, (locale, label) in TRACKS.items():
            node = checks.node_at(variants[track], path)
            prefix = f'{UNIT}--{track}--'
            markup = render(node, prefix, media[track], track,
                            link_cues(rules, track))
            pieces.append(f'<article class="track" lang="{locale}" data-register="{track}">'
                          f'<div class="register">{html.escape(label)}</div>{markup}</article>')
        pieces.append('</div></section>')
    pieces.append(
        '<footer lang="en"><p>Unofficial AI-assisted adaptation of OpenStax through the '
        'Indonesian edition by KokunoYumeto. Rice University/OpenStax, CC BY-NC-SA 4.0, '
        'subject to inherited component notices. No endorsement is implied.</p>'
        '<p>Identity metadata remain in the CNXML/provenance artifacts and are intentionally not '
        'voiced. Empty source links receive only their registered accessibility names.</p>'
        '</footer></main></body></html>')
    page = ''.join(pieces).encode('utf-8')
    generated = {f'review/units/{UNIT}.html': page}
    for track, (locale, label) in TRACKS.items():
        blocks = block_sets[track]
        transcript = (
            f'# {label} · m81244\n\n'
            'Status: finite source-bound narration draft; not synthesized, listening-reviewed, '
            'screen-reader-reviewed, or human-language-reviewed.\n\n')
        transcript += '\n\n'.join(f'## {mark}\n\n{body}' for mark, body in blocks) + '\n'
        generated[f'review/audio/{UNIT}.{track}.md'] = transcript.encode('utf-8')
        ssml = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<speak xmlns="http://www.w3.org/2001/10/synthesis" version="1.1" '
                f'xml:lang="{locale}">\n')
        ssml += ''.join(
            f'<mark name="{html.escape(mark, quote=True)}"/><p>{html.escape(body)}</p>'
            '<break time="600ms"/>\n' for mark, body in blocks)
        ssml += '</speak>\n'
        generated[f'review/audio/{UNIT}.{track}.ssml'] = ssml.encode('utf-8')
    return generated, block_sets


def validate_reader(page, source, rules):
    text = page.decode('utf-8')
    reader = Reader()
    reader.feed(text)
    if len(reader.ids) != len(set(reader.ids)):
        raise ValueError('Duplicate addition reader HTML ID')
    source_ids = rules['ordered_source_ids']
    expected_reader_ids = {f'{UNIT}--group-{index:02d}' for index in range(1, 13)}
    for track in TRACKS:
        expected = {f'{UNIT}--{track}--{source_id}' for source_id in source_ids}
        if not expected.issubset(reader.ids):
            raise ValueError('Reader omitted source IDs for ' + track)
        expected_reader_ids.update(expected)
        rendered_order = re.findall(
            rf'id="{re.escape(UNIT)}--{re.escape(track)}--([^"]+)" data-source-id=', text)
        if rendered_order != source_ids:
            raise ValueError('Reader source ID order changed for ' + track)
    if set(reader.ids) != expected_reader_ids or len(reader.ids) != 2280:
        raise ValueError('Reader contains missing or unregistered HTML IDs')
    if reader.maths != 401 * 3 or len(reader.images) != 50 * 3:
        raise ValueError('Reader MathML/media census changed')
    if len(reader.tracks) != 12 * 3:
        raise ValueError('Reader parallel-track group census changed')
    if len(re.findall(r'<table(?:\s|>)', text)) != 21 * 3:
        raise ValueError('Reader CNXML table census changed')
    if text.count('data-editorial-solution-cue="true"') != 74 * 3:
        raise ValueError('Reader untitled-answer cue census changed')
    if any(not image.get('alt') or not image.get('src', '').startswith('data:image/')
           for image in reader.images):
        raise ValueError('Reader image missing exact data asset or target alt')
    if set(link for link in reader.links if link.startswith('https://')) != ALLOWED_EXTERNAL:
        raise ValueError('Reader external link set changed')
    for link in reader.links:
        if link.startswith('#') and link[1:] not in reader.ids:
            raise ValueError('Unresolved same-module reader link: ' + link)
        if (not link.startswith(('#', 'https://'))
                and not link.startswith('a00-m81243-complete.html#')
                and link != '../../ATTRIBUTION.md'):
            raise ValueError('Unregistered reader link target: ' + link)
    if '<script' in text.lower():
        raise ValueError('Addition reader unexpectedly contains script')
    return reader


def validate_audio(generated, block_sets):
    for track, (locale, _label) in TRACKS.items():
        raw = generated[f'review/audio/{UNIT}.{track}.ssml']
        root = ET.fromstring(raw)
        if root.get('{http://www.w3.org/XML/1998/namespace}lang') != locale:
            raise ValueError('SSML locale changed')
        marks = [node.get('name') for node in root.findall('{*}mark')]
        paragraphs = root.findall('{*}p')
        if marks != [mark for mark, _ in block_sets[track]] or len(set(marks)) != 189:
            raise ValueError('SSML source-path marks changed')
        if len(paragraphs) != 189:
            raise ValueError('SSML block count changed')
        for paragraph, (_mark, expected) in zip(paragraphs, block_sets[track]):
            if ''.join(paragraph.itertext()) != expected:
                raise ValueError('SSML emitted nonregistered narration')
        ssml_text = raw.decode('utf-8')
        if '<voice' in ssml_text or '<audio' in ssml_text:
            raise ValueError('Hidden provider voice/audio fallback is forbidden')


def products():
    draft_generated = draft.products()
    draft.verify_saved(draft_generated)
    asset_generated = asset_producer.products()
    asset_producer.verify_saved(asset_generated)
    source, variants, rules, edits = checks.load_saved()
    manifest_raw = (LANG / asset_producer.MANIFEST).read_bytes()
    manifest = json.loads(manifest_raw)
    media = media_maps(manifest)
    generated, block_sets = page_and_audio(source, variants, rules, edits, media)
    reader = validate_reader(generated[f'review/units/{UNIT}.html'], source, rules)
    validate_audio(generated, block_sets)
    dependencies = {
        f'audio/{UNIT}.rules.json': draft.RULES_SHA256,
        f'translation/{UNIT}.edits.json': draft.EDITS_SHA256,
        f'translation/{UNIT}.assets.json': sha(manifest_raw),
        f'qa/{UNIT}.in-progress.json': sha(draft_generated[f'qa/{UNIT}.in-progress.json']),
    }
    for script in (
            'build.py', 'build_units.py', 'config.py', 'qa.py', 'safe_io.py',
            'draft_addition_production.py', 'prepare_addition_production_assets.py',
            'addition_production_checks.py', 'build_addition_production.py'):
        dependencies[f'scripts/{script}'] = sha((LANG / f'scripts/{script}').read_bytes())
    for track in TRACKS:
        path = f'translation/{UNIT}.{track}.cnxml'
        dependencies[path] = sha((LANG / path).read_bytes())
    receipt = {
        'schema': 'jv-addition-production-integration-v1',
        'status': 'structural_pass_human_review_pending',
        'unit': UNIT, 'program': 'A00', 'module': draft.MODULE,
        'complete_source_scope': True, 'whole_module_complete': False,
        'source_ids': 756, 'source_math_expressions': 401,
        'source_media_references': 50, 'source_tables': 21,
        'source_exercises': 129, 'source_solutions_present': 89,
        'source_solutions_absent': 40, 'untitled_solution_cues': 74,
        'narration_blocks_per_track': 189, 'register_tracks': 3,
        'reader_track_articles': len(reader.tracks), 'reader_embedded_images': len(reader.images),
        'ssml_files': 3, 'transcript_files': 3, 'synthesized_audio_files': 0,
        'numeric_alt_exception': {
            'count': 1, 'element_id': draft.CORRECTED_MEDIA_ID, 'attribute': 'alt',
            'exact_old_surface_and_asset_hash_required': True,
            'source_asset_sha256': draft.CORRECTED_ASSET_SHA256,
            'generic_numeric_bypass': False,
        },
        'output_sha256': {path: sha(raw) for path, raw in sorted(generated.items())},
        'verified_dependency_sha256': dict(sorted(dependencies.items())),
        'checks': [
            'complete_pinned_ID_EN_and_target_tree_replay',
            '756_IDs_per_track_and_exact_source_order', '401_MathML_per_track',
            '50_exact_media_per_track_and_21_tables_per_track',
            '129_exercises_89_supplied_40_absent_without_invention',
            '74_single_untitled_solution_cues_and_15_existing_titles',
            '189_finite_source_path_blocks_per_track',
            'provider_neutral_SSML_without_voice_or_audio_fallback',
            'all_same_module_links_resolved_and_three_external_URLs_exact',
            'deterministic_source_bound_assets_and_text_only_SVG_derivatives',
        ],
        'review_limits': {
            'integrated_browser_visual_review': False, 'screen_reader_review': False,
            'native_language_review': False, 'listening_review': False,
            'provider_synthesis': False, 'full_A00_A10_AX2_assignment_complete': False,
            'cross_module_m81243_link_file': 'separate coordinator-owned production dependency',
        },
    }
    generated[RECEIPT] = (json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    return generated


def verify_saved(generated=None):
    generated = products() if generated is None else generated
    for path, raw in generated.items():
        if (LANG / path).read_bytes() != raw:
            raise ValueError('Stale addition production output: ' + path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    generated = products()
    if generated != products():
        raise ValueError('Nondeterministic addition production build')
    if args.check:
        verify_saved(generated)
    else:
        for path, raw in generated.items():
            write_bytes(LANG / path, raw)
    print(('Checked' if args.check else 'Built') +
          ' complete m81244 three-track reader and 3 transcripts/SSML drafts.')


if __name__ == '__main__':
    main()
