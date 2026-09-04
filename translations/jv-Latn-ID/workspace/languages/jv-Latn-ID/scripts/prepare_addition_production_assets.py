"""Prepare the exact m81244 media layer and registered Javanese SVGs offline."""
import argparse
import copy
import hashlib
import json
from pathlib import PurePosixPath
import re
import xml.etree.ElementTree as ET

from build import XML_LANG
from build_units import tree_key
from config import LANG, TRACKS
import draft_addition_production as draft
from safe_io import write_bytes


UNIT = draft.UNIT
OUT = f'translation/assets/{UNIT}/'
MANIFEST = f'translation/{UNIT}.assets.json'
SVG_NS = 'http://www.w3.org/2000/svg'
SVG = '{' + SVG_NS + '}'
# Keep CNXML's process-global default namespace registration intact when this
# module is imported by the combined producer.
ET.register_namespace('svg', SVG_NS)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def blob_sha1(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def mime_and_format(raw):
    if raw.startswith(b'\xff\xd8\xff'):
        return 'image/jpeg', 'JPEG'
    if raw.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'image/png', 'PNG'
    root = ET.fromstring(raw)
    if root.tag == SVG + 'svg':
        return 'image/svg+xml', 'SVG'
    raise ValueError('Unsupported addition media bytes')


def text_nodes(raw_or_root):
    root = (ET.fromstring(raw_or_root)
            if isinstance(raw_or_root, (bytes, str)) else raw_or_root)
    allowed = {SVG + 'text', SVG + 'title', SVG + 'desc'}
    for node in root.iter():
        if node.text and node.text.strip() and node.tag not in allowed:
            raise ValueError('Unregistered SVG text-bearing node: ' + node.tag)
    return [node for node in root.iter() if node.tag in allowed and (node.text or '').strip()]


def geometry_signature(raw):
    root = ET.fromstring(raw)
    return [(node.tag,
             sorted((key, value) for key, value in node.attrib.items()
                    if not (node is root and key == XML_LANG)),
             len(node)) for node in root.iter()]


def localize_svg(raw, track, proposal):
    if track not in ('jv-academic', 'jv-conversation'):
        raise ValueError('Explicit Javanese SVG register required')
    index = 1 if track == 'jv-academic' else 2
    root = ET.fromstring(raw)
    nodes = text_nodes(root)
    substitutions = proposal['substitutions']
    if len(nodes) != len(substitutions):
        raise ValueError(f'SVG occurrence inventory changed for {proposal["media_id"]}')
    before = []
    for node, row in zip(nodes, substitutions):
        if node.text != row[0]:
            raise ValueError(f'SVG source occurrence changed for {proposal["media_id"]}')
        before.append(node.text)
        node.text = row[index]
    root.set(XML_LANG, 'jv-Latn-ID')
    output = ET.tostring(root, encoding='utf-8', xml_declaration=True) + b'\n'
    if geometry_signature(raw) != geometry_signature(output):
        raise ValueError('SVG geometry/hierarchy/nonlanguage attributes changed')
    after = [node.text for node in text_nodes(output)]
    if after != [row[index] for row in substitutions]:
        raise ValueError('SVG registered text substitution changed')
    token_pattern = r'\d+|[$×+=−÷]'
    if re.findall(token_pattern, '\n'.join(before)) != re.findall(token_pattern, '\n'.join(after)):
        raise ValueError('SVG numeric/operator tokens changed')
    return output


def add_product(generated, path, raw):
    if path in generated and generated[path] != raw:
        raise ValueError('Addition asset output collision: ' + path)
    generated[path] = raw


def products():
    rules_raw, edits_raw = draft.RULES_PATH.read_bytes(), draft.EDITS_PATH.read_bytes()
    if sha(rules_raw) != draft.RULES_SHA256 or sha(edits_raw) != draft.EDITS_SHA256:
        raise ValueError('Addition handoff changed before asset generation')
    rules, edits = json.loads(rules_raw), json.loads(edits_raw)
    id_raw = draft.ID_PATH.read_bytes()
    if sha(id_raw) != draft.ID_SHA256:
        raise ValueError('Pinned Indonesian source changed')
    source_root = ET.fromstring(id_raw)
    variants = {'id-academic': source_root}
    from build import translated
    for track in ('jv-academic', 'jv-conversation'):
        variants[track] = translated(source_root, track, edits)
    source_media = source_root.findall('.//{*}media')
    fixtures = rules['chart_fixtures']
    if len(source_media) != 50 or len(fixtures) != 50:
        raise ValueError('Addition media census changed')
    proposals = {row['media_id']: row for row in edits['media_linguistic_proposals']}
    if len(proposals) != 7:
        raise ValueError('Expected seven registered source SVG proposals')
    generated, records, localized = {}, [], []
    formats = {'JPEG': 0, 'PNG': 0, 'SVG': 0}
    for ordinal, (media, fixture) in enumerate(zip(source_media, fixtures), 1):
        media_id = media.get('id')
        if media_id != fixture['media_id'] or sha(tree_key(media).encode()) != fixture['source_tree_sha256']:
            raise ValueError('Media fixture order/tree changed: ' + str(media_id))
        image = media.find('{*}image')
        source_ref = image.get('src')
        asset = fixture['asset']
        if source_ref != asset['source_ref'] or image.get('mime-type') != asset['source_declared_mime']:
            raise ValueError('Media source reference/MIME changed: ' + media_id)
        source_path = LANG.parent.parent / asset['existing_path']
        raw = source_path.read_bytes()
        actual_mime, actual_format = mime_and_format(raw)
        if (sha(raw), len(raw), actual_format) != (asset['sha256'], asset['bytes'], asset['actual_format']):
            raise ValueError('Bound source asset changed: ' + media_id)
        formats[actual_format] += 1
        witness_path = LANG.parent.parent / asset['semantic_witness_path']
        if sha(witness_path.read_bytes()) != asset['semantic_witness_sha256']:
            raise ValueError('Semantic witness bytes changed: ' + media_id)
        source_name = PurePosixPath(source_ref).name
        stored = OUT + source_name
        add_product(generated, stored, raw)
        outputs = {'id-academic': {
            'path': stored, 'sha256': sha(raw), 'bytes': len(raw),
            'mime_type': actual_mime, 'derivative_type': 'exact-indonesian-source-bytes'}}
        substitutions = []
        proposal = proposals.get(media_id)
        if actual_format == 'SVG':
            if proposal is None or (proposal['source_sha256'], proposal['source_git_blob']) != (
                    sha(raw), blob_sha1(raw)):
                raise ValueError('SVG proposal/source binding changed: ' + media_id)
            if proposal['source_path'] != source_ref.removeprefix('../../'):
                raise ValueError('SVG proposal path changed: ' + media_id)
            localized.append(media_id)
            for track in ('jv-academic', 'jv-conversation'):
                derivative = localize_svg(raw, track, proposal)
                output_path = OUT + PurePosixPath(source_name).stem + f'.{track}.svg'
                add_product(generated, output_path, derivative)
                outputs[track] = {
                    'path': output_path, 'sha256': sha(derivative), 'bytes': len(derivative),
                    'mime_type': 'image/svg+xml',
                    'derivative_type': 'registered-text-only-svg-localization'}
                substitutions.append({
                    'track': track,
                    'occurrences': [{'source': row[0], 'target': row[1 if track == 'jv-academic' else 2]}
                                    for row in proposal['substitutions']]})
        else:
            if proposal is not None:
                raise ValueError('Raster unexpectedly has an SVG linguistic proposal')
            for track in ('jv-academic', 'jv-conversation'):
                outputs[track] = dict(outputs['id-academic'])
        target_alt = {}
        for track in TRACKS:
            target_node = variants[track].find(f'.//*[@id="{media_id}"]')
            if target_node is None or target_node.get('alt') != fixture['alt'][track]:
                raise ValueError('Target media alt differs from bound fixture: ' + media_id)
            target_alt[track] = target_node.get('alt')
        records.append({
            'ordinal': ordinal, 'media_id': media_id, 'source_src': source_ref,
            'source_media_tree_sha256': fixture['source_tree_sha256'],
            'source_alt': media.get('alt'), 'target_alt': target_alt,
            'source': {'path': asset['existing_path'], 'sha256': sha(raw), 'bytes': len(raw),
                       'declared_mime_type': image.get('mime-type'),
                       'actual_mime_type': actual_mime, 'format': actual_format,
                       'git_blob_sha1': blob_sha1(raw)},
            'semantic_witness': {'path': asset['semantic_witness_path'],
                                 'sha256': asset['semantic_witness_sha256'],
                                 'prior_actual_view_record': asset['semantic_witness']},
            'registered_substitutions': substitutions,
            'outputs': outputs,
        })
    if set(localized) != set(proposals) or len(localized) != 7:
        raise ValueError('Registered localized SVG set changed')
    if formats != {'JPEG': 26, 'PNG': 17, 'SVG': 7}:
        raise ValueError('Addition media format census changed')
    if len(generated) != 64:
        raise ValueError('Expected 50 retained assets plus 14 localized SVGs')
    exception = edits['source_bound_attribute_exceptions'][0]
    corrected = next(row for row in records if row['media_id'] == draft.CORRECTED_MEDIA_ID)
    if (corrected['source']['sha256'], corrected['source_alt']) != (
            draft.CORRECTED_ASSET_SHA256, exception['source_phrase']):
        raise ValueError('Scoped 222 correction lost source asset/old-alt binding')
    manifest = {
        'schema': 'jv-addition-production-assets-v1',
        'status': 'complete_source_bound_assets_reader_integration_pending',
        'unit': UNIT, 'program': 'A00', 'module': draft.MODULE,
        'source_module_sha256': draft.ID_SHA256,
        'handoff_sha256': {'rules': draft.RULES_SHA256, 'edits': draft.EDITS_SHA256},
        'scope': {'source_media': 50, 'retained_source_assets': 50,
                  'source_formats': formats, 'localized_svg_sources': 7,
                  'javanese_svg_derivatives': 14, 'stored_asset_files_total': 64},
        'numeric_alt_exception': {
            'element_id': draft.CORRECTED_MEDIA_ID, 'attribute': 'alt',
            'exact_old_source_surface': exception['source_phrase'],
            'source_asset_sha256': draft.CORRECTED_ASSET_SHA256,
            'target_numbers': exception['target_numbers'], 'generic_bypass': False,
        },
        'policy': (
            'All 50 Indonesian source media files are retained byte-exact. The 43 raster assets are '
            'shared unchanged by all tracks. Seven inherited Indonesian SVGs remain exact for the '
            'Indonesian track and receive fourteen derivatives changing only registered text '
            'occurrences and root language; geometry, hierarchy, IDs, numbers and operators are fixed.'),
        'review_limits': {
            'prior_source_and_semantic_witness_view_records_retained': True,
            'derivative_geometry_and_text_structure_checked': True,
            'integrated_reader_visual_review': False, 'screen_reader_review': False,
            'native_language_review': False, 'synthesized_audio_files': 0,
            'whole_assignment_complete': False,
        },
        'assets': records,
    }
    generated[MANIFEST] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    return generated


def verify_saved(generated=None):
    generated = products() if generated is None else generated
    for path, raw in generated.items():
        if (LANG / path).read_bytes() != raw:
            raise ValueError('Stale addition asset product: ' + path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    generated = products()
    if generated != products():
        raise ValueError('Nondeterministic addition asset generation')
    if args.check:
        verify_saved(generated)
    else:
        for path, raw in generated.items():
            write_bytes(LANG / path, raw)
    print(('Checked' if args.check else 'Prepared') +
          ' 50 exact addition assets and 14 registered Javanese SVG derivatives.')


if __name__ == '__main__':
    main()
