"""Independent, failure-driven structural QA for the complete m81357 preface."""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

from prepare_a20_preface import (
    BASE, ROOT, MANIFEST, TRANSLATION, EXCERPT, NOTICES, N, SOURCE, COMPARISON,
    SOURCE_SHA, COMPARISON_SHA, DEFAULT_CREDIT, HASH_POLICY, FILES,
    load_inputs, notice_record, inventory, owner_source, sha, fh, blob, dimensions, image_mode,
    A10_SOURCE, A10_TRANSLATION,
)

OUTPUT = BASE / 'reader/a20-preface.html'
RECEIPT = BASE / 'qa/structural-a20-preface.json'
MD = '{http://cnx.rice.edu/mdml}'
EXPECTED_LOCAL_CSS = '''
.a20-preface .source-label, .a20-preface footer, .a20-preface bdi { overflow-wrap:anywhere; }
.a20-preface h4 { font-size:1.1rem; color:var(--accent); margin-block:1rem .4rem; }
.a20-preface .source-list-no-bullets { list-style:none; padding-inline-start:0; }
.a20-preface .source-mixed-para { display:block; }
.a20-preface .inline-source-media { display:inline; white-space:normal; }
.a20-preface .inline-source-media img { display:inline-block; width:var(--icon-width); height:var(--icon-height); max-width:100%; min-width:0; padding:0; border:0; vertical-align:middle; transform:none; }
.a20-preface .alt-advisory { font-size:.8rem; margin-inline:.25rem; }
.a20-preface .source-media { max-width:100%; margin-block:1rem; }
.a20-preface .source-media img { display:block; width:791px; min-width:791px; max-width:none; height:auto; transform:none; }
.a20-preface .figure-scroll { direction:ltr; border:1px solid #cad7d1; background:white; }
.a20-preface .figure-accessible-label { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }
.a20-preface .bridge dl { display:grid; grid-template-columns:minmax(6rem,.65fr) minmax(0,1fr); gap:.4rem 1rem; }
.a20-preface .bridge dt { font-weight:600; }
.a20-preface .bridge dd { margin:0; overflow-wrap:anywhere; }
@media (max-width:600px) { .a20-preface .bridge dl { display:block; } .a20-preface .bridge dd { margin-block-end:.7rem; } }
@media print { .a20-preface .source-media img { width:100%; min-width:0; max-width:791px; } }
'''


class Checks:
    def __init__(self):
        self.names = []

    def check(self, condition, name):
        if not condition:
            raise AssertionError(name)
        self.names.append(name)


def parse(value):
    value = value.replace('<!doctype html>', '')
    value = re.sub(r'<(meta|img|br)(\s[^<>]*?)?\s*/?>', lambda m: m.group(0).rstrip('/>') + '/>', value)
    return ET.fromstring(value)


def frag(value):
    return parse('<fragment>' + value + '</fragment>')


def text(node):
    return ''.join(node.itertext())


def byid(root, ident):
    return next(x for x in root.iter() if x.get('id') == ident)


def local(tag):
    return tag.rsplit('}', 1)[-1]


def check_tree(actual, expected, checks, path):
    checks.check(actual.tag == expected.tag, path + ':tag')
    checks.check(actual.attrib == expected.attrib, path + ':attributes')
    checks.check((actual.text or '') == (expected.text or ''), path + ':text')
    checks.check(len(actual) == len(expected), path + ':child_count')
    for index, (a_child, e_child) in enumerate(zip(actual, expected)):
        check_tree(a_child, e_child, checks, path + '/' + str(index))
        checks.check((a_child.tail or '') == (e_child.tail or ''), path + '/' + str(index) + ':tail')


def isolated(node, ltr=False):
    here = ltr or node.get('dir') == 'ltr'
    own = re.sub(r'\{\{child:\d+\}\}', '', node.text or '')
    if re.search(r'[A-Za-z0-9]', own) and not here:
        return False
    for child in node:
        if not isolated(child, here) or (re.search(r'[A-Za-z0-9]', child.tail or '') and not here):
            return False
    return True


def validate_inputs(manifest, translation, source, comparison, checks):
    raw, comp_raw = SOURCE.read_bytes(), COMPARISON.read_bytes()
    checks.check(raw == EXCERPT.read_bytes(), 'complete_raw_boundary')
    checks.check(len(raw) == manifest['full_module_bytes'] == manifest['excerpt_bytes'] == 23553, 'canonical_size')
    checks.check(sha(raw) == manifest['full_module_sha256'] == manifest['excerpt_sha256'] == SOURCE_SHA, 'canonical_hash')
    checks.check(blob(raw) == manifest['canonical_git_blob_sha1'], 'canonical_git_blob')
    checks.check(len(comp_raw) == 24171 and sha(comp_raw) == manifest['indonesian_comparison_sha256'] == COMPARISON_SHA, 'comparison_hash')
    lock = json.loads((BASE / 'sources.lock.json').read_text(encoding='utf-8'))
    pinned = next(x for x in lock['repositories'] if x['role'] == 'A10+A20 upstream')
    comparison_repo = next(x for x in lock['repositories'] if x['role'] == 'A20')
    release = next(x for x in lock['archives'] if x['role'] == 'A20')
    checks.check((manifest['commit'], manifest['tree']) == (pinned['commit'], pinned['tree']) ==
                 ('38cae454e644abf9f0a623e876994553881597c9', '7907e4c81d43de1c3b6da173f0eb273c01dc5b55'), 'canonical_pin')
    checks.check((comparison_repo['commit'], comparison_repo['tree']) ==
                 ('b293e167477c8fe2e8885c6f6d79d12cbb2e0e89', '9ee25a0fa6eb336cbd40f3aa61587797b2bf4f27'), 'comparison_pin')
    checks.check((release['version'], release['sha256'], release['indonesian_coverage']) ==
                 ('v0.3.0-wip', 'a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7', {'translated': 48, 'total': 83}), 'comparison_release_48_of_83')
    checks.check((manifest['unit'], manifest['assignment'], manifest['module'], manifest['collection'], manifest['locale']) ==
                 ('A20-preface', 'A20', 'm81357', 'col31234', 'pnb-Arab-PK'), 'manifest_scope')
    checks.check((translation['unit'], translation['assignment'], translation['module'], translation['locale']) ==
                 ('A20-preface', 'A20', 'm81357', 'pnb-Arab-PK'), 'translation_scope')
    checks.check(source.tag == N + 'document' and source.attrib == {'class': 'preface'} and
                 [x.tag for x in source] == [N + 'title', N + 'metadata', N + 'content'], 'whole_document_shape')
    checks.check(source.find(N + 'content').attrib == {'class': 'preface'}, 'content_class')
    source_nodes, comparison_nodes = list(source.iter()), list(comparison.iter())
    checks.check(len(source_nodes) == len(comparison_nodes) == 194, 'exact_194_elements')
    for index, (canonical, compared) in enumerate(zip(source_nodes, comparison_nodes)):
        checks.check(local(canonical.tag) == local(compared.tag), 'comparison_element_tag:' + str(index))
        canonical_attrs = {k: v for k, v in canonical.attrib.items() if k != 'alt'}
        comparison_attrs = {k: v for k, v in compared.attrib.items() if k != 'alt'}
        checks.check(canonical_attrs == comparison_attrs, 'comparison_non_alt_attributes:' + str(index))
        checks.check(canonical.get('id') == compared.get('id'), 'comparison_id:' + str(index))
    counts = Counter(local(x.tag) for x in source_nodes)
    expected_raw = {'document': 1, 'title': 28, 'metadata': 1, 'content-id': 1, 'abstract': 1, 'uuid': 1, 'content': 1,
                    'para': 33, 'section': 26, 'emphasis': 38, 'list': 3, 'item': 25, 'newline': 27, 'media': 4, 'image': 4}
    checks.check(counts == expected_raw, 'exact_element_inventory')
    expected_counts = {'all_elements_including_document': 194, 'retained_source_ids_excluding_excerpt_root': 66,
        'translated_text_blocks': 89, 'xml_title_elements': 28, 'display_title_owners': 27, 'metadata_title_mirrors': 1,
        'paragraphs': 33, 'list_items': 25, 'emphasis_nodes': 38, 'sections': 26, 'lists': 3, 'newlines': 27,
        'images': 4, 'media': 4, 'figures': 0, 'captions': 0, 'mathml_trees': 0, 'mathml_tables': 0,
        'cnxml_tables': 0, 'source_links': 0, 'terms': 0, 'notes': 0, 'footnotes': 0, 'exercises': 0, 'solutions': 0}
    checks.check(manifest['source_counts'] == expected_counts, 'manifest_count_contract')
    keys, blocks, roles, ancestors, parents = inventory(source, 'm81357')
    checks.check(keys == manifest['source_text_keys_in_order'] == list(translation['source_blocks']) and len(keys) == 89, 'exact_89_owner_order')
    checks.check(roles == manifest['source_block_roles'], 'exact_owner_roles')
    checks.check(ancestors == manifest['source_ancestor_ids'] and list(ancestors) == manifest['source_ids_in_document_order'] and len(ancestors) == 66, 'exact_66_ids_ancestry')
    for index, ident in enumerate(ancestors):
        checks.check(list(source.iter()).index(byid(source, ident)) >= 0, 'source_id_present:' + str(index) + ':' + ident)
        checks.check(sum(x.get('id') == ident for x in source.iter()) == 1, 'source_id_unique:' + str(index) + ':' + ident)
    checks.check([x.get('id') for x in source.find(N + 'content')] == manifest['content_direct_children_in_source_order'] ==
                 ['fs-id1165926910741', 'fs-id1165926784292', 'fs-id1165926866457', 'fs-id1165926700317', 'fs-id1165926682605', 'fs-id1165924264981'], 'full_content_order')
    checks.check(translation['title'] == translation['source_blocks']['m81357/title'] == manifest['module_title_pnb'] == 'دیباچہ', 'one_translated_title')
    for key, node in blocks.items():
        value = translation['source_blocks'][key]
        parsed = frag(value)
        checks.check(not re.search(r'[\u0a00-\u0a7f\ufffd\u061c\u200b\u200e\u200f\u202a-\u202e\u2066-\u2069]', value), 'clean_unicode:' + key)
        checks.check(all(x.tag in ('fragment', 'em', 'strong', 'bdi', 'br') for x in parsed.iter()), 'fragment_tag_allowlist:' + key)
        checks.check(all(x.attrib in ({}, {'dir': 'ltr'}, {'dir': 'ltr', 'lang': 'en'}) for x in parsed.iter()), 'fragment_attribute_allowlist:' + key)
        checks.check(len(parsed.findall('.//br')) == roles[key]['newlines'], 'newline_count:' + key)
        source_text = node.get('alt') if node.tag == N + 'media' else text(node)
        target_text = re.sub(r'\{\{child:\d+\}\}', '', text(parsed))
        checks.check(re.findall(r'\d+(?:\.\d+)*', source_text) == re.findall(r'\d+(?:\.\d+)*', target_text), 'source_numerals:' + key)
        checks.check(len(node.findall('.//' + N + 'emphasis[@effect="bold"]')) == len(parsed.findall('.//strong')), 'bold_count:' + key)
        checks.check(len(node.findall('.//' + N + 'emphasis[@effect="italics"]')) == len(parsed.findall('.//em')), 'italics_count:' + key)
        checks.check(re.findall(r'\{\{child:\d+\}\}', value) == ['{{child:' + str(i) + '}}' for i in range(len(node.findall(N + 'media')))], 'child_slots:' + key)
        if not key.endswith('/alt'):
            checks.check(isolated(parsed), 'ltr_isolation:' + key)
    checks.check(sum(len(frag(x).findall('.//strong')) for x in translation['source_blocks'].values()) == 25, 'target_25_strong')
    checks.check(sum(len(frag(x).findall('.//em')) for x in translation['source_blocks'].values()) == 13, 'target_13_em')
    checks.check(sum(len(frag(x).findall('.//br')) for x in translation['source_blocks'].values()) == 27, 'target_27_breaks')
    checks.check(sum(x.count('{{child:0}}') for x in translation['source_blocks'].values()) == 3, 'three_inline_media_slots')
    reviewer = blocks['fs-id1165926697399']
    source_lines = [(reviewer.text or '').strip()] + [(x.tail or '').strip() for x in reviewer]
    target_reviewer = frag(translation['source_blocks']['fs-id1165926697399'])
    checks.check(len(source_lines) == 16 and [text(x) for x in target_reviewer.findall('bdi')] == source_lines, 'exact_16_reviewer_lines')
    checks.check([x.tag for x in target_reviewer] == ['bdi', 'br'] * 15 + ['bdi'], 'exact_15_reviewer_breaks')
    for ident in ('fs-id1165926653414', 'eip-863'):
        checks.check(text(frag(translation['source_blocks'][ident])) == text(blocks[ident]), 'exact_author_credit:' + ident)
    checks.check('OpenStax Partners' not in translation['source_blocks']['fs-id1165926914580'] and
                 '<bdi dir="ltr" lang="en">OpenStax</bdi> دے ساتھی' in translation['source_blocks']['fs-id1165926914580'], 'partners_common_noun_not_invented_label')
    checks.check('ہر اصطلاح' in translation['source_blocks']['eip-629/item/1'] and 'ہر لفظ' not in translation['source_blocks']['eip-629/item/1'], 'key_terms_term_not_word')
    candidate = manifest['owner_reuse']['candidate_source_matches_after_book_title_substitution']
    reuse = manifest['owner_reuse']['exact_target_reuse_after_book_title_substitution']
    fresh = manifest['owner_reuse']['fresh_or_fidelity_revised_keys']
    checks.check(len(candidate) == manifest['owner_reuse']['candidate_source_match_count'] == 56 and
                 candidate['eip-629/item/1'] == 'eip-673/item/1', '56_source_candidate_matches')
    checks.check(reuse == translation['reuse_from_a10_preface'] and len(reuse) == manifest['owner_reuse']['target_reused_count'] == 55 and
                 len(fresh) == manifest['owner_reuse']['fresh_or_fidelity_revised_count'] == 34 and set(reuse).isdisjoint(fresh) and
                 set(reuse) | set(fresh) == set(keys), '55_reused_34_fresh_partition')
    a10_source = ET.parse(A10_SOURCE).getroot()
    _, a10_blocks, _, _, _ = inventory(a10_source, 'm82630')
    a10_translation = json.loads(A10_TRANSLATION.read_text(encoding='utf-8'))
    for key, a10_key in candidate.items():
        checks.check(owner_source(blocks[key]) == owner_source(a10_blocks[a10_key]).replace('Elementary Algebra 2e', 'Intermediate Algebra 2e'), 'reuse_source_fragment:' + key)
    for key, a10_key in reuse.items():
        checks.check(translation['source_blocks'][key] == a10_translation['source_blocks'][a10_key].replace('Elementary Algebra 2e', 'Intermediate Algebra 2e'), 'reuse_target_fragment:' + key)
    checks.check(translation['source_blocks']['eip-629/item/1'] != a10_translation['source_blocks']['eip-673/item/1'] and
                 manifest['owner_reuse']['reclassified_candidate']['source_key'] == 'eip-629/item/1', 'one_candidate_reclassified_without_a10_change')
    checks.check('terjemahan Bahasa Indonesia' in text(comparison) and 'terjemahan Bahasa Indonesia' not in json.dumps(translation, ensure_ascii=False), 'indonesian_only_opening_not_imported')
    checks.check('جڑاں تے جذر' in translation['source_blocks']['fs-id1165926710568/item/8'] and 'Roots and Radicals' in translation['bridge_after_html'], 'chapter_8_discrepancy_separate')
    checks.check('ایس نظام دا اک حل اے' in translation['source_blocks']['fs-id1165926920334/alt'] and
                 'Intersecting' in translation['image_alt_overrides']['fs-id1165926920334'] and
                 'پوری وضاحتی سطراں' in translation['image_alt_overrides']['fs-id1165926920334'], 'graph_alt_pixel_discrepancy_separate')
    checks.check('تِن حذف دے نشان' in translation['source_blocks']['fs-id1166400341244/alt'] and 'تِن نقطے' in translation['image_alt_overrides']['fs-id1166400341244'], 'ellipsis_dots_separate')
    checks.check([(x['id'], x['source_key']) for x in translation['source_corrections']] ==
                 [(x['id'], x['source_key']) for x in manifest['source_discrepancies']] and len(translation['source_corrections']) == 8, 'eight_discrepancies_bound')
    checks.check(not translation['source_blocks']['fs-id1165926710568/item/8'].endswith('۔') and
                 not translation['source_blocks']['eip-761'].endswith('۔') and
                 not owner_source(blocks['fs-id1165926710568/item/8']).rstrip().endswith(('.', '!', '?')) and
                 not owner_source(blocks['eip-761']).rstrip().endswith(('.', '!', '?')), 'two_source_terminal_omissions_preserved')
    checks.check('اوہناں نوں حل کردے نیں' in translation['source_blocks']['fs-id1165926710568/item/10'] and
                 'a20-preface-solve-functions-note' in translation['bridge_after_html'], 'solve_functions_wording_disclosed')
    checks.check('سوال سکھن والیاں نوں جواباں دی کُنجی' in translation['source_blocks']['para-00001'] and
                 'a20-preface-answer-key-note' in translation['bridge_after_html'], 'answer_key_question_wording_disclosed')
    media_ids = [x['media_id'] for x in manifest['images']]
    checks.check(list(translation['image_alt_overrides']) == list(translation['image_alt_note_ids']) == media_ids, 'four_alt_bindings')
    for ident in media_ids:
        checks.check(not list(frag(translation['image_alt_overrides'][ident])), 'plain_alt_override:' + ident)
        checks.check(frag(translation['bridge_after_html']).find('.//*[@id="' + translation['image_alt_note_ids'][ident] + '"]') is not None, 'alt_note_exists:' + ident)
    for field, ident in [('bridge_before_html', 'a20-preface-source-context'), ('bridge_after_html', 'a20-preface-bridge')]:
        bridge = frag(translation[field])
        checks.check(len(bridge) == 1 and bridge[0].get('id') == ident and bridge[0].get('data-origin') == 'original-bridge', 'original_bridge_input:' + field)


def expected_media(node, spec, translation):
    ident = node.get('id')
    image_attributes = {'id': ident, 'data-source-tag': 'media', 'data-source-key': ident + '/alt',
        'src': '../' + spec['path'], 'alt': translation['image_alt_overrides'][ident],
        'data-source-alt': translation['source_blocks'][ident + '/alt'],
        'aria-describedby': translation['image_alt_note_ids'][ident], 'width': str(spec['width']), 'height': str(spec['height'])}
    if spec['parent_tag'] != 'para':
        image_attributes.update({'dir': 'rtl', 'lang': 'pnb-Arab-PK'})
    image = ET.Element('img', image_attributes)
    advisory = ET.Element('span', {'class': 'alt-advisory', 'data-origin': 'renderer-ui'})
    ET.SubElement(advisory, 'a', {'href': '#' + translation['image_alt_note_ids'][ident]}).text = 'تصویری وضاحت دا نوٹ'
    if spec['parent_tag'] == 'para':
        wrapper = ET.Element('span', {'class': 'inline-source-media', 'data-source-child': ident,
            'style': f'--icon-width:{spec["width"]}px;--icon-height:{spec["height"]}px'})
        wrapper.extend([image, advisory])
        return wrapper
    wrapper = ET.Element('div', {'class': 'source-media', 'data-source-child': ident})
    label = ET.SubElement(wrapper, 'span', {'id': 'a20-preface-graph-label', 'class': 'figure-accessible-label',
        'data-origin': 'renderer-ui', 'dir': 'rtl', 'lang': 'pnb-Arab-PK'})
    label.text = 'تِن محوری گراف'
    scroll = ET.SubElement(wrapper, 'div', {'class': 'figure-scroll', 'dir': 'ltr', 'tabindex': '0', 'role': 'region',
        'aria-labelledby': 'a20-preface-graph-label'})
    scroll.append(image)
    hint = ET.SubElement(wrapper, 'p', {'class': 'scroll-hint', 'data-origin': 'renderer-ui'})
    hint.text = 'تنگ سکرین اُتے تصویر نوں پاسے ول سرکا کے ویکھو؛ '
    link = ET.SubElement(hint, 'a', {'href': '../' + spec['path']})
    link.text, link.tail = 'اصل تصویر وکھری کھولو', '۔'
    hint.append(advisory)
    return wrapper


def expected_article(source, manifest, translation):
    keys, blocks, _, _, parents = inventory(source, 'm81357')
    inverse = {node: key for key, node in blocks.items()}
    images = {x['media_id']: x for x in manifest['images']}

    def convert(node, depth=0):
        tag = local(node.tag)
        if tag == 'media':
            return expected_media(node, images[node.get('id')], translation)
        attrs = {'data-source-tag': tag}
        if node.get('id'):
            attrs['id'] = node.get('id')
        if node.get('class'):
            attrs['data-source-class'] = node.get('class')
        if tag in ('title', 'para', 'item'):
            key = inverse[node]
            attrs['data-source-key'] = key
            html_tag = {'title': 'h' + str(depth + 1), 'para': 'p', 'item': 'li'}[tag]
            if node.findall(N + 'media'):
                attrs['class'] = 'source-mixed-para'
            result = ET.Element(html_tag, attrs)
            value = translation['source_blocks'][key]
            for index, child in enumerate(node.findall(N + 'media')):
                value = value.replace('{{child:' + str(index) + '}}', ET.tostring(convert(child), encoding='unicode'))
            parsed = frag(value)
            result.text = parsed.text
            result.extend(list(parsed))
            return result
        if tag == 'list':
            attrs.update({'data-source-list-type': node.get('list-type', 'unspecified'),
                'data-source-bullet-style': node.get('bullet-style', 'unspecified'),
                'class': 'source-list-no-bullets' if node.get('bullet-style') == 'none' else 'source-list'})
            result = ET.Element('ul', attrs)
        elif tag in ('content', 'section'):
            result = ET.Element('section', attrs)
        else:
            raise AssertionError('unsupported_expected_node:' + tag)
        result.extend(convert(child, depth + (tag == 'section')) for child in node)
        return result

    article = ET.Element('article', {'id': 'a20-preface-source', 'data-source-tag': 'document',
        'data-source-class': 'preface', 'data-source-module': 'm81357'})
    article.extend([convert(source.find(N + 'title')), convert(source.find(N + 'content'))])
    return article


FOOTER_TEXT = [
    'Adapted from OpenStax Intermediate Algebra 2e, module m81357: Preface, collection col31234. Original senior contributing authors retained in source order: Lynn Marecek; Andrea Honeycutt Mathis. Source publisher: OpenStax / Rice University. All 16 reviewer lines and both named author affiliations remain in the source article.',
    'The existing A20 notice states Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International, subject to component-specific credits and restrictions. This adaptation retains that framework and those restrictions. See the retained A20 release license notice, canonical license text, and selected component evidence. No new clearance is asserted.',
    'Raw-source default art credit: ' + DEFAULT_CREDIT + ' The pinned source paragraph eip-787 supplies this default for art lacking an in-text attribution and retains component-specific permission limits. Media identity records are not image-specific clearance.',
    'OpenStax and Rice University do not endorse this translation. Their names, logos and marks are not licensed. All four canonical images are unchanged and unmirrored. The three inline icons are static illustrations, not controls. The graph is unnumbered section-level media; no figure identity or caption is invented.',
    'Changes: complete translation of 89 source owners, retaining all 194 source elements, 66 source IDs, 26 sections, 27 visible title owners plus the metadata title mirror, 33 paragraphs, 25 list items, 38 emphasis nodes and 27 explicit newlines. Original metadata stays separate and the translated visible title appears once. After the explicit book-title substitution, 56 canonical-English owners are A10 source candidates; after one A20 fidelity revision, 55 remain exact target reuses and 34 owners are independently translated or fidelity-revised, without changing frozen A10.',
    'Faithful source alts remain in data-source-alt. Separately labeled accessible overrides describe the inspected pixels and point to visible original notes. The missing graph sentences, Indonesian RGB redraw, Chapter 8 singular/plural discrepancy, Answer Key question/answer wording, solve-functions wording, static-icon qualification and dated service claims remain traceable. Original opening context and closing discrepancy/term notes are outside the source article.',
    "Indonesian comparison: Intermediate Algebra 2e Indonesian editable checkpoint v0.3.0-wip, an admitted partial 48/83-module comparison. It is not canonical and not a complete book. This Punjabi adaptation was produced with OpenAI Codex assistance at the user's direction; original human-contributor credits remain intact.",
    'Coverage: complete m81357 preface only, not the textbook. The complete A10, A20, A30, B10 and B40 workflow remains unfinished. This is not a training or fine-tuning dataset. Native-language, educator, assistive-technology and independent browser review remain separate. Frozen source witness · Source manifest · Language and source notes.'
]


def validate_reader(root, source, manifest, translation, checks):
    checks.check(root.tag == 'html' and root.attrib == {'lang': 'pnb-Arab-PK', 'dir': 'rtl'} and [x.tag for x in root] == ['head', 'body'], 'reader_root')
    checks.check(not (root.text or '').strip() and all(not (x.tail or '').strip() for x in root), 'reader_root_slots')
    head, body = root
    checks.check(body.attrib == {'class': 'a20-reader a20-preface'} and [x.tag for x in body] == ['header', 'main', 'footer'], 'body_shape')
    checks.check(not (body.text or '').strip() and all(not (x.tail or '').strip() for x in body), 'body_slots')
    metadata = {local(x.tag): x.text or '' for x in source.find(N + 'metadata')}
    expected_meta = [{'charset': 'utf-8'}, {'name': 'viewport', 'content': 'width=device-width, initial-scale=1'},
        {'name': 'description', 'content': 'Complete m81357 preface in Shahmukhi Punjabi; not a complete textbook'},
        {'name': 'source-document-class', 'content': 'preface'}] + [{'name': 'source-' + name, 'content': value} for name, value in metadata.items()]
    metas = head.findall('meta')
    checks.check([x.attrib for x in metas] == expected_meta and all(not list(x) and not (x.text or '') for x in metas), 'exact_source_metadata')
    checks.check([x.tag for x in head] == ['meta'] * 8 + ['title', 'style'], 'head_shape')
    checks.check(head.find('title').text == translation['title'] + ' — A20 preface', 'html_title')
    shared_css = (BASE / 'styles/reader.css').read_text(encoding='utf-8')
    checks.check(head.find('style').text == shared_css + EXPECTED_LOCAL_CSS, 'reviewed_unit_css')
    checks.check('transform:none' in EXPECTED_LOCAL_CSS and 'scaleX(-1)' not in head.find('style').text, 'images_not_mirrored')
    header, main, footer = body
    checks.check([x.tag for x in header] == ['p', 'p', 'p', 'nav'] and header[0].attrib == {'class': 'eyebrow'} and header[2].attrib == {'class': 'status'}, 'header_shape')
    checks.check(text(header[0]) == 'A20 / col31234 / m81357' and text(header[1]) == translation['subtitle'], 'header_identity')
    checks.check('جانچ ہن تک نہیں ہوئی' in text(header[2]), 'human_review_pending')
    checks.check([x.get('href') for x in header.find('nav').findall('a')] == ['#a20-preface-source', '#a20-preface-bridge', '#credits'], 'header_nav')
    checks.check([x.tag for x in main] == ['p', 'aside', 'article', 'section', 'p'], 'main_shape')
    checks.check(not (main.text or '').strip() and all(not (x.tail or '').strip() for x in main), 'main_exact_slots')
    checks.check(main[0].attrib == {'class': 'source-label', 'data-origin': 'renderer-ui'} and 'پورا دیباچہ' in text(main[0]) and 'پوری کتاب نہیں' in text(main[0]), 'bounded_source_label')
    check_tree(main[1], frag(translation['bridge_before_html'])[0], checks, 'bridge_before')
    check_tree(main[3], frag(translation['bridge_after_html'])[0], checks, 'bridge_after')
    checks.check(main[4].attrib == {'class': 'status', 'data-origin': 'renderer-ui'} and text(main[4]) == 'پنجاں مقررہ کتاباں دا پورا کم ہن وی جاری اے۔', 'whole_assignment_active')
    article = main[2]
    graph_precheck = byid(article, 'fs-id1165926920334')
    graph_region_precheck = next(x for x in article.iter('div') if x.get('class') == 'figure-scroll')
    checks.check(graph_precheck.get('dir') == 'rtl' and graph_precheck.get('lang') == 'pnb-Arab-PK', 'graph_punjabi_alt_direction')
    checks.check(graph_region_precheck.get('dir') == 'ltr' and graph_region_precheck.get('aria-labelledby') == 'a20-preface-graph-label' and graph_region_precheck.get('aria-label') is None, 'graph_ltr_geometry_rtl_name')
    check_tree(article, expected_article(source, manifest, translation), checks, 'exact_complete_source_article')
    source_keys = [x.get('data-source-key') for x in article.iter() if x.get('data-source-key')]
    checks.check(source_keys == manifest['source_text_keys_in_order'] and len(source_keys) == 89, 'rendered_89_owner_order')
    checks.check(sum(x.tag == 'br' for x in article.iter()) == 27, 'rendered_27_breaks')
    checks.check(sum(x.tag == 'strong' for x in article.iter()) == 25 and sum(x.tag == 'em' for x in article.iter()) == 13, 'rendered_38_emphasis')
    all_ids = [x.get('id') for x in root.iter() if x.get('id')]
    checks.check(len(all_ids) == len(set(all_ids)), 'reader_ids_unique')
    for ident in manifest['source_ids_in_document_order']:
        checks.check(all_ids.count(ident) == 1, 'rendered_source_id:' + ident)
    images = list(article.iter('img'))
    checks.check([x.get('id') for x in images] == [x['media_id'] for x in manifest['images']] and len(images) == 4, 'four_images_source_order')
    for image, spec in zip(images, manifest['images']):
        checks.check(image.get('src') == '../' + spec['path'], 'image_src:' + spec['media_id'])
        checks.check(image.get('data-source-alt') == translation['source_blocks'][spec['media_id'] + '/alt'], 'faithful_alt:' + spec['media_id'])
        checks.check(image.get('alt') == translation['image_alt_overrides'][spec['media_id']], 'accessible_alt:' + spec['media_id'])
        checks.check(image.get('aria-describedby') == translation['image_alt_note_ids'][spec['media_id']], 'alt_note_binding:' + spec['media_id'])
        checks.check((image.get('width'), image.get('height')) == (str(spec['width']), str(spec['height'])), 'image_dimensions:' + spec['media_id'])
    graph = byid(root, 'fs-id1165926920334')
    checks.check(graph.get('src').endswith('/CNX_ElemAlg_Figure_05_01_015_img.jpg') and graph.get('width') == '791' and graph.get('height') == '257', 'canonical_graph_served')
    checks.check(graph.get('dir') == 'rtl' and graph.get('lang') == 'pnb-Arab-PK', 'graph_punjabi_alt_direction')
    graph_label = byid(root, 'a20-preface-graph-label')
    graph_region = next(x for x in article.iter('div') if x.get('class') == 'figure-scroll')
    checks.check(graph_label.attrib == {'id': 'a20-preface-graph-label', 'class': 'figure-accessible-label', 'data-origin': 'renderer-ui', 'dir': 'rtl', 'lang': 'pnb-Arab-PK'} and text(graph_label) == 'تِن محوری گراف', 'graph_punjabi_accessible_label')
    checks.check(graph_region.get('dir') == 'ltr' and graph_region.get('aria-labelledby') == 'a20-preface-graph-label' and graph_region.get('aria-label') is None, 'graph_ltr_geometry_rtl_name')
    checks.check(graph.get('src') != manifest['images'][3]['comparison_local_path'], 'comparison_redraw_not_served')
    checks.check(footer.attrib == {'id': 'credits', 'lang': 'en', 'dir': 'ltr'} and [x.tag for x in footer] == ['h2'] + ['p'] * 8, 'footer_shape')
    checks.check(footer.find('h2').text == 'Sources, credits and changes — A20 preface', 'footer_heading')
    for index, (paragraph, expected) in enumerate(zip(footer.findall('p'), FOOTER_TEXT)):
        checks.check(text(paragraph) == expected, 'exact_credit_and_limits:' + str(index))
        checks.check(paragraph.attrib == ({'id': 'a20-preface-art-credit'} if index == 2 else {}), 'footer_paragraph_attributes:' + str(index))
    span = footer.find('.//span')
    checks.check(span.attrib == {'data-origin': 'retained-source-credit'} and span.text == DEFAULT_CREDIT, 'raw_source_art_credit')
    expected_links = [manifest['upstream_url'] + '/blob/' + manifest['commit'] + '/' + manifest['path'],
        'https://creativecommons.org/licenses/by-nc-sa/4.0/', '../provenance/A20-release/LICENSE.txt',
        '../provenance/upstream--osbooks-prealgebra-bundle/LICENSE', '../provenance/a20-preface-component-notices.json',
        '#eip-787', 'https://github.com/KokunoYumeto/openstax-intermediate-algebra-2e-id/releases/tag/v0.3.0-wip',
        '../source-excerpts/a20-preface.cnxml', '../source-excerpts/manifest-a20-preface.json', '../qa/a20-preface-language-notes.md']
    checks.check([x.get('href') for x in footer.iter('a')] == expected_links, 'exact_provenance_links')
    ids = set(all_ids)
    for index, anchor in enumerate(root.iter('a')):
        href = anchor.get('href', '')
        if href.startswith('#'):
            checks.check(href[1:] in ids, 'internal_link:' + str(index) + ':' + href)
        elif not href.startswith('https://'):
            path = (OUTPUT.parent / href).resolve()
            checks.check(path.is_relative_to(BASE.resolve()) and path.is_file(), 'local_link:' + str(index) + ':' + href)


def validate_notice(notice, manifest, source, checks):
    expected_fields = {'schema', 'unit', 'work', 'module', 'collection', 'commit', 'manifest_sha256', 'excerpt_sha256', 'scope',
        'comparison_scope', 'owner_reuse', 'existing_notice_inputs', 'existing_notice_input_hash_policy', 'release_license_verbatim',
        'original_senior_contributing_authors', 'existing_license_statement', 'non_endorsement', 'rights_status', 'credit_limit',
        'source_default_art_credit', 'source_default_art_credit_paragraph', 'raw_source_art_attribution_paragraph_verbatim',
        'images', 'source_discrepancies', 'whole_book_translation_complete', 'publication_claim_limit'}
    checks.check(set(notice) == expected_fields, 'notice_exact_fields')
    checks.check(notice['schema'] == 'a20-retained-component-evidence-v1' and
                 (notice['unit'], notice['module'], notice['collection']) == ('A20-preface', 'm81357', 'col31234'), 'notice_scope')
    checks.check(notice['work'] == 'OpenStax Intermediate Algebra 2e' and notice['commit'] == manifest['commit'] and
                 notice['manifest_sha256'] == fh(MANIFEST) and notice['excerpt_sha256'] == SOURCE_SHA, 'notice_source_bindings')
    checks.check(notice['scope'] == 'Complete m81357 preface and four unchanged canonical originals; no new supply/license audit.', 'notice_bounded_scope')
    checks.check(notice['comparison_scope'] == 'Indonesian v0.3.0-wip comparison is an admitted partial 48/83 checkpoint; it is not canonical and not a complete book.', 'notice_comparison_limit')
    checks.check(notice['owner_reuse'] == {'candidate_source_matches': 56, 'exact_target_reuses': 55,
                 'fresh_or_fidelity_revised': 34, 'reclassified_source_key': 'eip-629/item/1',
                 'frozen_a10_unchanged': True}, 'notice_owner_reuse_counts')
    checks.check(notice['existing_notice_inputs'] == manifest['existing_notice_inputs'] and notice['existing_notice_input_hash_policy'] == HASH_POLICY, 'notice_hash_policy')
    for item in notice['existing_notice_inputs']:
        checks.check(sha((ROOT / item['path']).read_bytes().replace(b'\r\n', b'\n')) == item['sha256'], 'notice_input:' + item['path'])
    checks.check(notice['release_license_verbatim'] == (BASE / 'provenance/A20-release/LICENSE.txt').read_text(encoding='utf-8'), 'verbatim_release_license')
    checks.check(notice['original_senior_contributing_authors'] == ['Lynn Marecek', 'Andrea Honeycutt Mathis'], 'notice_authors')
    checks.check(notice['existing_license_statement'] == manifest['retained_attribution']['existing_license_statement'], 'notice_license')
    checks.check(notice['non_endorsement'] == manifest['retained_attribution']['non_endorsement'], 'notice_nonendorsement')
    checks.check(notice['rights_status'] == 'Existing audited A20 policy retained; no new component-specific clearance determination.' and
                 'not image-specific rights holders or new permissions' in notice['credit_limit'], 'notice_no_new_clearance')
    raw_credit = text(byid(source, 'eip-787'))
    checks.check(notice['source_default_art_credit'] == DEFAULT_CREDIT and notice['source_default_art_credit_paragraph'] == 'eip-787' and
                 notice['raw_source_art_attribution_paragraph_verbatim'] == raw_credit, 'notice_raw_credit')
    checks.check(notice['source_discrepancies'] == manifest['source_discrepancies'], 'notice_discrepancies')
    checks.check(notice['whole_book_translation_complete'] is False and notice['publication_claim_limit'] ==
                 'The retained A20 release describes a partial Indonesian checkpoint, not this Punjabi preface or a complete Punjabi book.', 'notice_publication_limit')
    checks.check(len(notice['images']) == len(manifest['images']) == 4, 'notice_four_images')
    for record, spec in zip(notice['images'], manifest['images']):
        checks.check(set(record) == set(spec) | {'treatment', 'component_clearance'}, 'notice_image_fields:' + spec['media_id'])
        for key, value in spec.items():
            checks.check(record[key] == value, 'notice_image_binding:' + spec['media_id'] + ':' + key)
        checks.check(record['component_clearance'] == 'Not newly assessed; subject to retained component-specific credits and restrictions.', 'notice_image_clearance:' + spec['media_id'])
        checks.check('Exact canonical bytes, unchanged and unmirrored.' in record['treatment'], 'notice_image_treatment:' + spec['media_id'])
        original, compared, prepared = ROOT / spec['canonical_local_path'], ROOT / spec['comparison_local_path'], BASE / spec['path']
        cdata, idata, pdata = original.read_bytes(), compared.read_bytes(), prepared.read_bytes()
        checks.check(cdata == pdata and sha(cdata) == spec['sha256'] and len(cdata) == spec['bytes'], 'prepared_asset_identity:' + spec['media_id'])
        checks.check(dimensions(cdata) == (spec['width'], spec['height']) and image_mode(original) == spec['mode'], 'canonical_asset_geometry:' + spec['media_id'])
        checks.check((sha(idata), len(idata), dimensions(idata), image_mode(compared), cdata == idata) ==
                     (spec['comparison_sha256'], spec['comparison_bytes'], (spec['comparison_width'], spec['comparison_height']), spec['comparison_mode'], spec['comparison_byte_identical']), 'comparison_asset_identity:' + spec['media_id'])
    checks.check([x['comparison_byte_identical'] for x in manifest['images']] == [True, True, True, False], 'only_graph_is_redraw')
    checks.check((manifest['images'][3]['mode'], manifest['images'][3]['width'], manifest['images'][3]['height']) == ('CMYK', 791, 257) and
                 (manifest['images'][3]['comparison_mode'], manifest['images'][3]['comparison_width'], manifest['images'][3]['comparison_height']) == ('RGB', 1600, 620), 'canonical_cmyk_comparison_rgb')


def mutations(root, source, comparison, manifest, translation, notice):
    results = []
    mismatches = []

    def swap(parent, a, b):
        children = list(parent)
        children[a], children[b] = children[b], children[a]
        parent[:] = children

    def rejects(name, kind, change, expected_failure):
        rr, mm, tt, nn = deepcopy(root), deepcopy(manifest), deepcopy(translation), deepcopy(notice)
        change(rr, mm, tt, nn)
        try:
            if kind == 'reader':
                validate_reader(rr, source, mm, tt, Checks())
            elif kind == 'input':
                validate_inputs(mm, tt, source, comparison, Checks())
            else:
                validate_notice(nn, mm, source, Checks())
        except AssertionError as error:
            if str(error) != expected_failure:
                mismatches.append({'name': name, 'expected': expected_failure, 'actual': str(error)})
            else:
                results.append({'name': name, 'rejected_by': str(error), 'detached': True})
        else:
            raise AssertionError('mutation_not_rejected:' + name)

    article_guard = 'exact_complete_source_article/1:child_count'
    rejects('drop_opening_paragraph', 'reader', lambda r, m, t, n: byid(r, 'a20-preface-source')[1].remove(byid(r, 'fs-id1165926910741')), article_guard)
    rejects('swap_top_sections', 'reader', lambda r, m, t, n: swap(byid(r, 'a20-preface-source')[1], 1, 5), 'exact_complete_source_article/1/1:attributes')
    rejects('inject_unkeyed_paragraph', 'reader', lambda r, m, t, n: ET.SubElement(byid(r, 'fs-id1165926784292'), 'p').__setattr__('text', 'Complete book.'), 'exact_complete_source_article/1/1:child_count')
    rejects('inject_container_text', 'reader', lambda r, m, t, n: byid(r, 'fs-id1165926866457').__setattr__('text', '999'), 'exact_complete_source_article/1/2:text')
    rejects('wrong_heading_level', 'reader', lambda r, m, t, n: byid(r, 'eip-291')[0].__setattr__('tag', 'h2'), 'exact_complete_source_article/1/3/4/4/0:tag')
    rejects('invent_numbered_chapter_list', 'reader', lambda r, m, t, n: byid(r, 'fs-id1165926710568').__setattr__('tag', 'ol'), 'exact_complete_source_article/1/3/2/3:tag')
    rejects('swap_chapter_items', 'reader', lambda r, m, t, n: swap(byid(r, 'fs-id1165926710568'), 0, 1), 'exact_complete_source_article/1/3/2/3/0:attributes')
    rejects('change_chapter_digit', 'reader', lambda r, m, t, n: byid(r, 'fs-id1165926710568')[0].find('.//bdi').__setattr__('text', '11'), 'exact_complete_source_article/1/3/2/3/0/0/0:text')
    rejects('drop_reviewer_break', 'reader', lambda r, m, t, n: byid(r, 'fs-id1165926697399').remove(byid(r, 'fs-id1165926697399')[1]), 'exact_complete_source_article/1/5/2/1:child_count')
    rejects('change_reviewer_name', 'reader', lambda r, m, t, n: byid(r, 'fs-id1165926697399')[0].__setattr__('text', 'Changed Person'), 'exact_complete_source_article/1/5/2/1/0:text')
    rejects('move_inline_icon_after_text', 'reader', lambda r, m, t, n: byid(r, 'eip-761').__setattr__('text', 'آپ کر کے ویکھو'), 'exact_complete_source_article/1/3/4/3/1:text')
    rejects('wrong_icon_src', 'reader', lambda r, m, t, n: byid(r, 'eip-id11722388').set('src', '../assets/a20/media.png'), 'exact_complete_source_article/1/3/4/3/1/0/0:attributes')
    rejects('erase_faithful_alt', 'reader', lambda r, m, t, n: byid(r, 'fs-id1165926920334').attrib.pop('data-source-alt'), 'exact_complete_source_article/1/3/5/2/1/0:attributes')
    rejects('wrong_accessible_alt', 'reader', lambda r, m, t, n: byid(r, 'fs-id1166400341244').set('alt', 'three ellipses'), 'exact_complete_source_article/1/3/4/4/1/0/0:attributes')
    rejects('wrong_alt_note', 'reader', lambda r, m, t, n: byid(r, 'eip-id1176044388').set('aria-describedby', 'credits'), 'exact_complete_source_article/1/3/4/5/1/0/0:attributes')
    rejects('graph_alt_inherits_ltr', 'reader', lambda r, m, t, n: byid(r, 'fs-id1165926920334').attrib.pop('dir'), 'graph_punjabi_alt_direction')
    rejects('graph_punjabi_name_replaced_by_ltr_aria_label', 'reader', lambda r, m, t, n: next(x for x in r.iter('div') if x.get('class') == 'figure-scroll').attrib.update({'aria-label': 'تِن محوری گراف', 'aria-labelledby': ''}), 'graph_ltr_geometry_rtl_name')
    rejects('invent_graph_figure', 'reader', lambda r, m, t, n: byid(r, 'fs-id1165926734826')[-1].__setattr__('tag', 'figure'), 'exact_complete_source_article/1/3/5/2:tag')
    rejects('metadata_uuid', 'reader', lambda r, m, t, n: r.find('head/meta[@name="source-uuid"]').set('content', 'changed'), 'exact_source_metadata')
    rejects('duplicate_visible_metadata_title', 'reader', lambda r, m, t, n: byid(r, 'a20-preface-source').insert(0, ET.Element('h1')), 'exact_complete_source_article:child_count')
    rejects('relabel_original_bridge', 'reader', lambda r, m, t, n: byid(r, 'a20-preface-bridge').set('data-origin', 'source'), 'bridge_after:attributes')
    rejects('main_completion_claim', 'reader', lambda r, m, t, n: r.find('body/main').__setattr__('text', 'Whole book complete.'), 'main_exact_slots')
    rejects('footer_extra_claim', 'reader', lambda r, m, t, n: ET.SubElement(byid(r, 'credits'), 'p').__setattr__('text', 'Published complete book.'), 'footer_shape')
    rejects('footer_new_clearance', 'reader', lambda r, m, t, n: byid(r, 'a20-preface-art-credit').find('span').__setattr__('text', 'All images cleared.'), 'exact_credit_and_limits:2')
    rejects('css_mirror', 'reader', lambda r, m, t, n: r.find('head/style').__setattr__('text', r.find('head/style').text + 'img{transform:scaleX(-1)}'), 'reviewed_unit_css')
    rejects('translation_numeral', 'input', lambda r, m, t, n: t['source_blocks'].__setitem__('fs-id1165926605740', t['source_blocks']['fs-id1165926605740'] + ' 2027'), 'source_numerals:fs-id1165926605740')
    rejects('translation_gurmukhi', 'input', lambda r, m, t, n: t['source_blocks'].__setitem__('fs-id1165926605740', t['source_blocks']['fs-id1165926605740'] + ' ਪੰਜਾਬੀ'), 'clean_unicode:fs-id1165926605740')
    rejects('translation_drop_reviewer_break', 'input', lambda r, m, t, n: t['source_blocks'].__setitem__('fs-id1165926697399', t['source_blocks']['fs-id1165926697399'].replace('<br>', '', 1)), 'newline_count:fs-id1165926697399')
    rejects('translation_drop_icon_slot', 'input', lambda r, m, t, n: t['source_blocks'].__setitem__('eip-761', t['source_blocks']['eip-761'].replace('{{child:0}}', '')), 'child_slots:eip-761')
    rejects('translation_invent_partners_label', 'input', lambda r, m, t, n: t['source_blocks'].__setitem__('fs-id1165926914580', t['source_blocks']['fs-id1165926914580'].replace('OpenStax</bdi> دے ساتھی', 'OpenStax Partners</bdi>')), 'partners_common_noun_not_invented_label')
    rejects('translation_term_to_word', 'input', lambda r, m, t, n: t['source_blocks'].__setitem__('eip-629/item/1', t['source_blocks']['eip-629/item/1'].replace('ہر اصطلاح', 'ہر لفظ')), 'key_terms_term_not_word')
    rejects('reuse_map_extra', 'input', lambda r, m, t, n: t['reuse_from_a10_preface'].__setitem__('fs-id1165926910741', 'eip-192'), '55_reused_34_fresh_partition')
    rejects('manifest_owner_order', 'input', lambda r, m, t, n: m['source_text_keys_in_order'].reverse(), 'exact_89_owner_order')
    rejects('notice_image_hash', 'notice', lambda r, m, t, n: n['images'][0].__setitem__('sha256', '0' * 64), 'notice_image_binding:eip-id11722388:sha256')
    rejects('notice_graph_comparison_hash', 'notice', lambda r, m, t, n: n['images'][3].__setitem__('comparison_sha256', '0' * 64), 'notice_image_binding:fs-id1165926920334:comparison_sha256')
    rejects('notice_new_clearance', 'notice', lambda r, m, t, n: n.__setitem__('rights_status', 'All images cleared.'), 'notice_no_new_clearance')
    rejects('notice_injected_field', 'notice', lambda r, m, t, n: n.__setitem__('new_permission', True), 'notice_exact_fields')
    rejects('notice_complete_book', 'notice', lambda r, m, t, n: n.__setitem__('whole_book_translation_complete', True), 'notice_publication_limit')
    rejects('notice_complete_comparison', 'notice', lambda r, m, t, n: n.__setitem__('comparison_scope', 'Complete 83/83 book.'), 'notice_comparison_limit')
    rejects('notice_reuse_overclaim', 'notice', lambda r, m, t, n: n['owner_reuse'].__setitem__('exact_target_reuses', 56), 'notice_owner_reuse_counts')
    if mismatches:
        raise AssertionError('mutation_guard_mismatches:' + json.dumps(mismatches, ensure_ascii=False))
    return results


def scoped_inputs(manifest):
    paths = [MANIFEST, TRANSLATION, EXCERPT, BASE / 'sources.lock.json', BASE / 'styles/reader.css',
        BASE / 'qa/a20-preface-language-notes.md', BASE / 'scripts/generate_a20_preface_manifest.py',
        BASE / 'scripts/prepare_a20_preface.py', BASE / 'scripts/build_a20_preface.py', Path(__file__),
        SOURCE, COMPARISON, A10_SOURCE, A10_TRANSLATION]
    paths += [ROOT / x['path'] for x in manifest['existing_notice_inputs']]
    paths += [ROOT / x['canonical_local_path'] for x in manifest['images']]
    paths += [ROOT / x['comparison_local_path'] for x in manifest['images']]
    receipt_dir = BASE / 'canon/receipts'
    paths += sorted(receipt_dir.glob('A20-preface-*.json'))
    return {x.relative_to(ROOT).as_posix(): fh(x) for x in paths}


def run():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    translation = json.loads(TRANSLATION.read_text(encoding='utf-8'))
    source = ET.parse(EXCERPT).getroot()
    comparison = ET.parse(COMPARISON).getroot()
    before = scoped_inputs(manifest)
    checks = Checks()
    validate_inputs(manifest, translation, source, comparison, checks)
    products = []
    for _ in range(2):
        for script in ('prepare_a20_preface.py', 'build_a20_preface.py'):
            subprocess.run([sys.executable, '-B', str(BASE / 'scripts' / script)], check=True, capture_output=True, text=True, encoding='utf-8')
        products.append({'reader': fh(OUTPUT), 'notices': fh(NOTICES), 'manifest': fh(MANIFEST),
            'images': {x['path']: fh(BASE / x['path']) for x in manifest['images']}})
    checks.check(products[0] == products[1], 'two_preparations_two_builds_identical')
    root = parse(OUTPUT.read_text(encoding='utf-8'))
    notice = json.loads(NOTICES.read_text(encoding='utf-8'))
    validate_reader(root, source, manifest, translation, checks)
    validate_notice(notice, manifest, source, checks)
    negative = mutations(root, source, comparison, manifest, translation, notice)
    checks.check(before == scoped_inputs(manifest), 'all_scoped_inputs_unchanged')
    checks.check(products[-1] == {'reader': fh(OUTPUT), 'notices': fh(NOTICES), 'manifest': fh(MANIFEST),
        'images': {x['path']: fh(BASE / x['path']) for x in manifest['images']}}, 'mutations_did_not_change_products')
    receipt = {'schema': 'pnb-source-bound-structural-qa-v1', 'unit': 'A20-preface', 'module': 'm81357', 'status': 'pass',
        'scope': 'Entire pinned m81357 Preface; module checkpoint only, whole A20 book and five-work assignment remain active.',
        'source_counts': manifest['source_counts'], 'owner_reuse': {'candidate_source_matches': 56,
            'exact_target_reuses': 55, 'fresh_or_fidelity_revised': 34,
            'reclassified_source_key': 'eip-629/item/1', 'frozen_a10_unchanged': True},
        'checks_passed': len(checks.names), 'check_names': checks.names,
        'detached_mutations_rejected': len(negative), 'mutation_results': negative,
        'deterministic_preparations': 2, 'deterministic_builds': 2, 'outputs': products[-1],
        'source_input_raw_sha256': before, 'existing_notice_input_hash_policy': HASH_POLICY,
        'limits': ['Repeated per-element and per-owner assertions are not independent linguistic judgments.',
            'Actual target-language draft/revision/QA reading is evidenced separately; automated receipt creation never substitutes for reading.',
            'Independent browser, native-language, educator and assistive-technology review remain separate from structural QA.',
            'The canonical graph and all icons were visually inspected, but byte/DOM checks are not a fresh image-understanding proof.',
            'External services, accounts and dated resource claims were not rechecked; source voice and original qualifications remain separate.',
            'Existing audited rights policy is retained without a new supply/license or image-clearance audit.',
            'The metadata title is retained as metadata rather than duplicated as a second visible source title.',
            'The Indonesian comparison is a partial 48/83 checkpoint and its RGB redraw is not served.',
            'No complete-book or whole-assignment completion is asserted.']}
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f'A20-preface QA passed: {len(checks.names)} checks; {len(negative)} detached mutations; two builds and preparations identical.')
    print('reader SHA-256 ' + fh(OUTPUT))
    print('notice SHA-256 ' + fh(NOTICES))
    print('receipt SHA-256 ' + fh(RECEIPT))


if __name__ == '__main__':
    run()
