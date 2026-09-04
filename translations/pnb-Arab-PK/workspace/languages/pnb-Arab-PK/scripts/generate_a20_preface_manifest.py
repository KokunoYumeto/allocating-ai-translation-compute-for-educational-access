"""Generate the frozen complete-m81357 manifest from pinned, already-acquired inputs."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import struct
import xml.etree.ElementTree as ET

from PIL import Image
from prepare_a10 import jpeg_dimensions

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
CANONICAL = ROOT / 'downloads/complete-upstream/osbooks-prealgebra-bundle'
SOURCE = CANONICAL / 'modules/m81357/index.cnxml'
COMPARISON = ROOT / 'downloads/extracted/A20/source/modules/m81357/index.cnxml'
EXCERPT = BASE / 'source-excerpts/a20-preface.cnxml'
TRANSLATION = BASE / 'translations/a20-preface.json'
A10_SOURCE = CANONICAL / 'modules/m82630/index.cnxml'
A10_TRANSLATION = BASE / 'translations/a10-preface.json'
OUTPUT = BASE / 'source-excerpts/manifest-a20-preface.json'
N = '{http://cnx.rice.edu/cnxml}'
MD = '{http://cnx.rice.edu/mdml}'
COMMIT = '38cae454e644abf9f0a623e876994553881597c9'
TREE = '7907e4c81d43de1c3b6da173f0eb273c01dc5b55'
SOURCE_SHA = 'f4d01bced59370e726f637a3d5b846ad77aa3536dba5a838cb00ceeadebd3033'
COMPARISON_SHA = 'b8892a3bd4dff624639d7b798499bc4c0f887db6e4d289ddd051f4d41067706c'
DEFAULT_CREDIT = 'Copyright Rice University, OpenStax, under CC BY-NC-SA 4.0 license.'
HASH_POLICY = 'SHA-256 after CRLF-to-LF normalization in memory; files are not rewritten. Source/image/Git-blob hashes are raw-byte identities.'
FILES = ['tryit.png', 'howtoicon.png', 'media.png', 'CNX_ElemAlg_Figure_05_01_015_img.jpg']


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fh(path):
    return sha(path.read_bytes())


def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def local(tag):
    return tag.rsplit('}', 1)[-1]


def dimensions(data):
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        require(data[12:16] == b'IHDR', 'PNG header missing')
        return struct.unpack('>II', data[16:24])
    return jpeg_dimensions(data)


def inventory(source, module):
    parents = {child: parent for parent in source.iter() for child in parent}
    keys, blocks, roles, ancestors = [], {}, {}, {}
    for node in source.iter():
        tag = local(node.tag)
        ident = node.get('id')
        if ident:
            chain, parent = [], parents.get(node)
            while parent is not None:
                if parent.get('id'):
                    chain.insert(0, parent.get('id'))
                parent = parents.get(parent)
            ancestors[ident] = chain
        key = None
        if node.tag == N + 'title':
            key = (parents[node].get('id') or module) + '/title'
        elif node.tag == N + 'para':
            key = ident
        elif node.tag == N + 'item':
            key = parents[node].get('id') + '/item/' + str(list(parents[node]).index(node) + 1)
        elif node.tag == N + 'media':
            key = ident + '/alt'
        if key:
            keys.append(key)
            blocks[key] = node
            roles[key] = {'tag': tag, 'newlines': len(node.findall('.//' + N + 'newline'))}
    return keys, blocks, roles, ancestors, parents


def inner(node):
    parts = [node.text or '']
    media_index = 0
    for child in node:
        tag = local(child.tag)
        if tag == 'emphasis':
            parts.append('<emphasis effect="' + child.get('effect') + '">' + inner(child) + '</emphasis>')
        elif tag == 'newline':
            parts.append('<newline/>')
        elif tag == 'media':
            parts.append('{{child:' + str(media_index) + '}}')
            media_index += 1
        else:
            raise ValueError('Unexpected owner child ' + tag)
        parts.append(child.tail or '')
    return ''.join(parts)


def owner_source(node):
    return node.get('alt') if node.tag == N + 'media' else inner(node)


def image_mode(path):
    with Image.open(path) as image:
        return image.mode


def build():
    raw = SOURCE.read_bytes()
    comp_raw = COMPARISON.read_bytes()
    require(len(raw) == 23553 and sha(raw) == SOURCE_SHA and raw == EXCERPT.read_bytes(), 'Canonical/excerpt changed')
    require(len(comp_raw) == 24171 and sha(comp_raw) == COMPARISON_SHA, 'Comparison changed')
    source, comparison = ET.fromstring(raw), ET.fromstring(comp_raw)
    require(source.attrib == comparison.attrib == {'class': 'preface'}, 'Document class changed')
    require([local(x.tag) for x in source.iter()] == [local(x.tag) for x in comparison.iter()], 'Comparison structure changed')
    require([x.get('id') for x in source.iter() if x.get('id')] == [x.get('id') for x in comparison.iter() if x.get('id')], 'Comparison IDs changed')
    keys, blocks, roles, ancestors, parents = inventory(source, 'm81357')
    a10 = ET.parse(A10_SOURCE).getroot()
    a10_keys, a10_blocks, _, _, _ = inventory(a10, 'm82630')
    translation = json.loads(TRANSLATION.read_text(encoding='utf-8'))
    a10_translation = json.loads(A10_TRANSLATION.read_text(encoding='utf-8'))
    require(keys == list(translation['source_blocks']) and len(keys) == 89, '89-owner order changed')
    reuse = translation['reuse_from_a10_preface']
    require(len(reuse) == 55 and set(reuse).issubset(keys) and set(reuse.values()).issubset(a10_keys), '55-owner reuse map changed')
    candidate = {key: (reuse[key] if key in reuse else 'eip-673/item/1') for key in keys
                 if key in reuse or key == 'eip-629/item/1'}
    require(len(candidate) == 56 and candidate['eip-629/item/1'] == 'eip-673/item/1', '56 source-candidate map changed')
    for key, a10_key in candidate.items():
        require(owner_source(blocks[key]) == owner_source(a10_blocks[a10_key]).replace('Elementary Algebra 2e', 'Intermediate Algebra 2e'), 'Source candidate mismatch: ' + key)
    for key, a10_key in reuse.items():
        require(translation['source_blocks'][key] == a10_translation['source_blocks'][a10_key].replace('Elementary Algebra 2e', 'Intermediate Algebra 2e'), 'Target reuse mismatch: ' + key)
    fresh = [key for key in keys if key not in reuse]
    require(len(fresh) == 34, '34 fresh/revised owners changed')
    counts = Counter(local(x.tag) for x in source.iter())
    expected = {'document': 1, 'title': 28, 'metadata': 1, 'content-id': 1, 'abstract': 1, 'uuid': 1, 'content': 1,
                'para': 33, 'section': 26, 'emphasis': 38, 'list': 3, 'item': 25, 'newline': 27, 'media': 4, 'image': 4}
    require(counts == expected and sum(counts.values()) == 194, '194-element source inventory changed')
    images = []
    for node, filename in zip(source.findall('.//' + N + 'media'), FILES):
        image_node = node.find(N + 'image')
        canonical = CANONICAL / 'media' / filename
        compared = ROOT / 'downloads/extracted/A20/source/media' / filename
        cdata, idata = canonical.read_bytes(), compared.read_bytes()
        parent = parents[node]
        record = {
            'figure_id': None,
            'media_id': node.get('id'),
            'parent_id': parent.get('id'),
            'parent_tag': local(parent.tag),
            'source_src': image_node.get('src'),
            'source_path': 'media/' + filename,
            'canonical_local_path': canonical.relative_to(ROOT).as_posix(),
            'comparison_local_path': compared.relative_to(ROOT).as_posix(),
            'path': 'assets/a20/' + filename,
            'mime_type': image_node.get('mime-type'),
            'bytes': len(cdata),
            'sha256': sha(cdata),
            'width': dimensions(cdata)[0],
            'height': dimensions(cdata)[1],
            'mode': image_mode(canonical),
            'git_blob_sha1': blob(cdata),
            'source_alt': node.get('alt'),
            'comparison_bytes': len(idata),
            'comparison_sha256': sha(idata),
            'comparison_width': dimensions(idata)[0],
            'comparison_height': dimensions(idata)[1],
            'comparison_mode': image_mode(compared),
            'comparison_byte_identical': cdata == idata,
        }
        images.append(record)
    require([x['comparison_byte_identical'] for x in images] == [True, True, True, False], 'Comparison asset identities changed')
    notice_paths = [
        'languages/pnb-Arab-PK/provenance/A20-release/LICENSE.txt',
        'languages/pnb-Arab-PK/provenance/A20-release/README.md',
        'languages/pnb-Arab-PK/provenance/A20-release/manifests/source-checkpoint-0030.json',
        'languages/pnb-Arab-PK/provenance/upstream--osbooks-prealgebra-bundle/LICENSE',
    ]
    notice_inputs = [{'path': path, 'sha256': sha((ROOT / path).read_bytes().replace(b'\r\n', b'\n'))} for path in notice_paths]
    manifest = {
        'schema': 'pnb-bounded-cnxml-manifest-v1', 'unit': 'A20-preface', 'assignment': 'A20', 'locale': 'pnb-Arab-PK',
        'collection': 'col31234', 'collection_title': 'Intermediate Algebra 2e', 'module': 'm81357', 'module_title': 'Preface',
        'module_title_pnb': translation['title'], 'module_collection_order': 1, 'document_class': 'preface', 'content_class': 'preface',
        'module_uuid': source.find(N + 'metadata/' + MD + 'uuid').text, 'commit': COMMIT, 'tree': TREE,
        'upstream_url': 'https://github.com/openstax/osbooks-prealgebra-bundle', 'path': 'modules/m81357/index.cnxml',
        'canonical_local_path': SOURCE.relative_to(ROOT).as_posix(), 'full_module_bytes': len(raw), 'full_module_sha256': SOURCE_SHA,
        'canonical_git_blob_sha1': blob(raw), 'indonesian_comparison_path': COMPARISON.relative_to(ROOT).as_posix(),
        'indonesian_comparison_sha256': COMPARISON_SHA, 'source_excerpt': EXCERPT.name, 'excerpt_root_id': None,
        'excerpt_bytes': len(raw), 'excerpt_sha256': SOURCE_SHA,
        'canonical_hash_note': 'Canonical and full witness are byte-identical LF files including their terminal LF; the Indonesian comparison is a separate complete-language witness.',
        'purpose': 'Complete source-bound preface translation; not training or fine-tuning',
        'selection_kind': 'Entire m81357 document, original metadata, display title and every content descendant',
        'scope_from': 'document/title', 'scope_through_inclusive': 'fs-id1165926697399',
        'scope_boundary': 'Entire final reviewer paragraph, all 16 reviewer lines and closing module structure',
        'next_collection_module': 'm81358', 'next_collection_module_title': 'Introduction',
        'content_direct_children_in_source_order': [x.get('id') for x in source.find(N + 'content')],
        'source_ids_in_document_order': list(ancestors), 'source_ancestor_ids': ancestors,
        'source_text_keys_in_order': keys, 'source_block_roles': roles,
        'source_counts': {'all_elements_including_document': 194, 'retained_source_ids_excluding_excerpt_root': 66,
            'translated_text_blocks': 89, 'xml_title_elements': 28, 'display_title_owners': 27, 'metadata_title_mirrors': 1,
            'paragraphs': 33, 'list_items': 25, 'emphasis_nodes': 38, 'sections': 26, 'lists': 3, 'newlines': 27,
            'images': 4, 'media': 4, 'figures': 0, 'captions': 0, 'mathml_trees': 0, 'mathml_tables': 0,
            'cnxml_tables': 0, 'source_links': 0, 'terms': 0, 'notes': 0, 'footnotes': 0, 'exercises': 0, 'solutions': 0},
        'owner_reuse': {'candidate_source_matches_after_book_title_substitution': candidate, 'candidate_source_match_count': 56,
            'exact_target_reuse_after_book_title_substitution': reuse, 'target_reused_count': 55,
            'fresh_or_fidelity_revised_keys': fresh, 'fresh_or_fidelity_revised_count': 34,
            'reclassified_candidate': {'source_key': 'eip-629/item/1', 'a10_key': 'eip-673/item/1',
                'reason': 'A20 fidelity revision uses ہر اصطلاح for source term; frozen A10 uses ہر لفظ, so the source candidate is not claimed as byte-equal target reuse.'},
            'policy': translation['reuse_policy']},
        'source_links': [], 'references': [], 'images': images,
        'reader_asset_state': 'Four canonical originals inspected at original detail; preparation copies exact bytes to assignment-local paths.',
        'existing_notice_inputs': notice_inputs, 'existing_notice_input_hash_policy': HASH_POLICY,
        'retained_attribution': {'original_senior_contributing_authors': ['Lynn Marecek', 'Andrea Honeycutt Mathis'],
            'source_default_art_credit': DEFAULT_CREDIT, 'source_default_art_credit_paragraph': 'eip-787',
            'existing_license_statement': 'Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International, subject to component-specific credits and restrictions.',
            'non_endorsement': 'OpenStax and Rice University do not endorse this translation; names, logos, and marks are not licensed.',
            'rights_limit': 'Retained source claims and existing audited restrictions, not new image-specific clearance or a new supply/license audit.'},
        'renderer_contract': {'source_title_once': 'm81357/title is the translated visible document title; metadata title is retained separately, not displayed twice.',
            'source_full_structure': 'All 26 sections and every paragraph/list/item descendant; no skipped unsupported nodes or inferred figure numbers.',
            'mixed_paragraphs': [{'id': 'eip-761', 'child_media_id': 'eip-id11722388'}, {'id': 'eip-326', 'child_media_id': 'fs-id1166400341244'}, {'id': 'eip-873', 'child_media_id': 'eip-id1176044388'}],
            'mixed_content_policy': 'Each mixed paragraph has exactly one {{child:0}} slot; the graph is standalone section-level media.',
            'image_accessibility': 'Keep faithful source alts traceable; separately label pixel-faithful overrides and advisory destinations.',
            'newlines': 'Preserve all 27: twelve chapter title/body breaks and fifteen breaks between sixteen reviewer lines.',
            'lists': 'Preserve fs-id1165926710568 bulleted/none, fs-id1165926805076 bulleted/bullet and eip-629 unspecified attributes.',
            'proper_names': 'Preserve all 16 reviewer lines, two senior-author lines, URLs, identifiers and English image labels in LTR isolation.',
            'original_content': 'Opening context and closing discrepancy/term notes are original siblings outside the source article.',
            'source_claims': 'Institutional, access, resource and licensing statements are pinned-source claims, not refreshed offers.',
            'no_mathml': 'No source MathML, table, link, footnote, exercise or solution exists in this module.'},
        'source_discrepancies': [
            {'id': 'A20-PREFACE-ALT-001', 'source_key': 'fs-id1165926920334/alt', 'finding': 'Canonical alt claims complete explanatory sentences are visible below the graphs; pixels show only Intersecting, Parallel and Coincident.', 'treatment': 'Faithful translated source alt stays traceable; a separate accessible override and note describe the pixels.'},
            {'id': 'A20-PREFACE-ASSET-001', 'source_key': 'fs-id1165926920334/alt', 'finding': 'Indonesian comparison is a 1600x620 RGB redraw with Indonesian labels, not the 791x257 CMYK canonical JPEG.', 'treatment': 'Serve only the exact canonical JPEG; retain the redraw as comparison evidence.'},
            {'id': 'A20-PREFACE-TEXT-001', 'source_key': 'fs-id1165926710568/item/8', 'finding': 'Outline says Roots and Radical while the collection chapter title says Roots and Radicals.', 'treatment': 'Retain the singular source wording; explain the discrepancy in a separate original note.'},
            {'id': 'A20-PREFACE-TIME-001', 'source_key': 'fs-id1165926605740', 'finding': 'Web/PDF/print/accounts/partners/video/resource statements are dated source voice.', 'treatment': 'Translate the claims and separately state that current availability was not rechecked.'},
            {'id': 'A20-PREFACE-ICON-001', 'source_key': 'fs-id1166400341244/alt', 'finding': 'Source says three ellipses while the inspected icon visibly contains three dots; icons are static in this reader.', 'treatment': 'Retain faithful alts; separate accessible overrides describe visible pixels and do not promise controls.'},
            {'id': 'A20-PREFACE-COMP-001', 'source_key': 'fs-id1165926910741', 'finding': 'Indonesian comparison adds that it is a Bahasa Indonesia translation; canonical English does not.', 'treatment': 'Do not import the comparison-only phrase; identify the Punjabi adaptation only in a separate original bridge.'},
            {'id': 'A20-PREFACE-ANSWER-001', 'source_key': 'para-00001', 'finding': 'Canonical literally says odd-numbered questions are provided to students in the Answer Key, although the paragraph otherwise discusses answers.', 'treatment': 'Keep the faithful source wording and explain the likely question/answer wording tension in a separate original note.'},
            {'id': 'A20-PREFACE-SOLVE-001', 'source_key': 'fs-id1165926710568/item/10', 'finding': 'Canonical says students solve exponential and logarithmic functions, rather than equations or problems.', 'treatment': 'Retain the source wording in Punjabi and explain the unusual object of solve in a separate original note.'}],
        'whole_assignment_complete': False,
        'translation_workflow_status': 'Complete 89-owner source draft, canon-based revision and QA reading, isolated preparation/build, and failure-driven structural QA complete; independent browser, native-language, educator, and assistive-technology review remain.'}
    require(manifest['content_direct_children_in_source_order'] == ['fs-id1165926910741','fs-id1165926784292','fs-id1165926866457','fs-id1165926700317','fs-id1165926682605','fs-id1165924264981'], 'Content boundary changed')
    OUTPUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('Generated A20-preface manifest: 89 owners / 66 IDs / 194 elements / 4 media.')


if __name__ == '__main__':
    build()
