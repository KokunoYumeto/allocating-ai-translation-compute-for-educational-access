"""Independent source-bound QA for complete m49304 / PNB012."""
from pathlib import Path
import argparse
from collections import Counter
import copy
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET

from qa_notation import jpeg_dimensions, unique_object

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
MATH = 'http://www.w3.org/1998/Math/MathML'
CANONICAL = ROOT / 'downloads/upstream/osbooks-college-algebra-bundle/modules/m49304/index.cnxml'


def tag(node):
    return node.tag.rsplit('}', 1)[-1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def signature(node):
    return node.tag, dict(node.attrib), node.text, tuple((signature(c), c.tail) for c in node)


def parse_html(data):
    text = data.decode('utf-8')
    assert text.startswith('<!doctype html>\n')
    return ET.fromstring(text.split('\n', 1)[1])


class Expected:
    """Derive source paths, keys and slots directly from CNXML."""
    def __init__(self, source):
        self.source = source
        self.parent = {c: n for n in source.iter() for c in n}
        self.paths = {source: 'root'}
        for node in source.iter():
            for index, child in enumerate(node):
                self.paths[child] = self.paths[node] + '/' + str(index)
        self.blocks = []
        for node in source.iter():
            name, owner, key = tag(node), self.parent.get(node), None
            if name == 'media':
                key = node.get('id') + '/alt'
            elif name == 'table':
                key = node.get('id') + '/summary'
            elif name == 'title':
                key = ('m49304/title' if owner is source else 'm49304/metadata/title'
                       if tag(owner) == 'metadata' else owner.get('id') + '/title')
            elif name in ('para', 'footnote', 'meaning'):
                key = node.get('id')
            elif name == 'term':
                key = node.get('id') or owner.get('id') + '/term'
            elif name == 'label' and ''.join(node.itertext()).strip():
                key = owner.get('id') + '/label'
            elif name == 'item':
                key = owner.get('id') + '/item/' + str(list(owner).index(node) + 1)
            elif name == 'caption':
                key = owner.get('id') + '/caption'
            elif name == 'entry':
                table = owner
                while tag(table) != 'table':
                    table = self.parent[table]
                rows = [n for n in table.iter() if tag(n) == 'row']
                key = table.get('id') + '/row/' + str(rows.index(owner) + 1) + '/entry/' + str(list(owner).index(node) + 1)
            if key:
                self.blocks.append((key, node))
        assert len(self.blocks) == len(set(k for k, _ in self.blocks)) == 376
        self.keys = {node: key for key, node in self.blocks}

    def groups(self, node):
        def descendants(current, wanted):
            for child in current:
                name = tag(child)
                if name == wanted:
                    yield child
                elif name not in ('list', 'table', 'media', 'figure', 'footnote', 'para', 'term'):
                    yield from descendants(child, wanted)
        return {
            'math': list(descendants(node, 'math')),
            'term': list(descendants(node, 'term')),
            'link': list(descendants(node, 'link')),
            'child': [c for c in node if (c in self.keys and tag(c) != 'term') or tag(c) in ('list', 'table', 'media', 'figure')],
        }

    def math_owners(self):
        result = []
        for math in self.source.iter('{' + MATH + '}math'):
            owner = self.parent[math]
            while owner is not self.source and owner not in self.keys and tag(owner) != 'equation':
                owner = self.parent[owner]
            if owner in self.keys:
                key = self.keys[owner]
                slot = self.groups(owner)['math'].index(math)
            else:
                key = owner.get('id')
                slot = [n for n in owner if tag(n) == 'math'].index(math)
            result.append((key, slot, math))
        assert len(result) == 258
        return result


class QA:
    def __init__(self, check_only=False):
        self.check_only, self.checks, self.mutations = check_only, 0, 0
        self.mutation_labels = []
        self.paths = {
            'excerpt': BASE / 'source-excerpts/unit-012.cnxml',
            'manifest': BASE / 'source-excerpts/manifest-012.json',
            'translation': BASE / 'translations/unit-012.json',
            'notes': BASE / 'qa/unit-012-language-notes.md',
            'notice': BASE / 'provenance/unit-012-component-notices.json',
            'prepare': BASE / 'scripts/prepare_domain_range.py',
            'build': BASE / 'scripts/build_domain_range.py',
            'qa': BASE / 'scripts/qa_domain_range.py',
            'reader': BASE / 'reader/unit-012.html',
            'style': BASE / 'styles/reader.css',
            'terms': BASE / 'terminology.tsv',
            'canon_study': BASE / 'canon/receipts/PNB-012-study-next-unit-20260831T151047014721Z.json',
            'canon_draft': BASE / 'canon/receipts/PNB-012-draft-20260831T154217182067Z.json',
            'canon_revision': BASE / 'canon/receipts/PNB-012-revision-20260831T170750618482Z.json',
            'canon_qa': BASE / 'canon/receipts/PNB-012-qa-20260901T130609961914Z.json',
        }
        self.raw = {key: path.read_bytes() for key, path in self.paths.items()}
        self.manifest = json.loads(self.raw['manifest'], object_pairs_hook=unique_object)
        self.translation = json.loads(self.raw['translation'], object_pairs_hook=unique_object)
        self.source = ET.fromstring(self.raw['excerpt'])
        self.expected = Expected(self.source)
        self.document = parse_html(self.raw['reader'])

    def check(self, condition, label):
        assert condition, label
        self.checks += 1

    def ids(self, root):
        return {n.get('id'): n for n in root.iter() if n.get('id')}

    def validate_source(self):
        canonical = CANONICAL.read_bytes()
        lf = canonical.replace(b'\r\n', b'\n')
        excerpt_lf = self.raw['excerpt'].replace(b'\r\n', b'\n')
        self.check(digest(canonical) == '0e230c4c96d46e7962dcb3afa1f1630718f7e1cdfae9e665d640690ab6ace19c', 'canonical_raw_hash')
        self.check(digest(lf) == self.manifest['full_module_sha256'] == 'b884c16482dc3cc3bc6f96ebc342ae934863f7aacd5eb39ec73c7a5f6a49f92c', 'canonical_lf_hash')
        self.check(excerpt_lf == lf + (b'' if lf.endswith(b'\n') else b'\n'), 'whole_module_excerpt')
        self.check(signature(self.source) == signature(ET.fromstring(canonical)), 'xml_exact_except_eol')
        counts = {name: sum(tag(n) == name for n in self.source.iter()) for name in ('math', 'media', 'figure', 'table', 'link', 'footnote', 'exercise', 'solution')}
        self.check(counts == {'math': 258, 'media': 44, 'figure': 26, 'table': 1, 'link': 35, 'footnote': 2, 'exercise': 82, 'solution': 51}, 'source_counts')
        self.check(len(list(self.source.iter())) - 1 == 4275, 'source_elements')
        source_ids = [n.get('id') for n in self.source.iter() if n.get('id')]
        self.check(len(source_ids) == len(set(source_ids)) == 577 == self.manifest['source_statistics']['identified_nodes'], 'source_ids')
        self.check(self.manifest['source_block_keys'] == [k for k, _ in self.expected.blocks], 'manifest_key_order')
        self.check(self.manifest['source_ids'] == source_ids, 'manifest_id_order')
        media_nodes = [n for n in self.source.iter() if tag(n) == 'media']
        self.check([row['media_id'] for row in self.manifest['images']] == [n.get('id') for n in media_nodes], 'manifest_media_order')
        source_parent = {c: n for n in self.source.iter() for c in n}
        for media, row in zip(media_nodes, self.manifest['images']):
            image = next(n for n in media if tag(n) == 'image')
            ancestor = source_parent.get(media)
            while ancestor is not None and tag(ancestor) != 'figure':
                ancestor = source_parent.get(ancestor)
            figure_id = ancestor.get('id') if ancestor is not None else None
            self.check(row['source_path'] == image.get('src').removeprefix('../../'), 'manifest_source_image:' + media.get('id'))
            self.check(row['source_mime_type'] == image.get('mime-type') and row.get('figure_id') == figure_id, 'manifest_source_media_context:' + media.get('id'))
            self.check(row['path'] == 'assets/unit-012-' + media.get('id') + '.jpg' and row['publication_status'] == 'admitted-unchanged', 'manifest_publication_binding:' + media.get('id'))
        derived_links = []
        for owner_key, owner in self.expected.blocks:
            for index, link in enumerate(self.expected.groups(owner)['link']):
                derived_links.append({'key': owner_key + '/link/' + str(index), 'attributes': dict(link.attrib),
                                      'text': ''.join(link.itertext()), 'path': self.expected.paths[link]})
        self.check(self.manifest['source_links'] == derived_links, 'manifest_source_links_exact')
        section = next(n for n in self.source.iter() if n.get('id') == 'fs-id1165135176628')
        exercises = [n for n in section.iter() if tag(n) == 'exercise']
        solutions = [n for n in section.iter() if tag(n) == 'solution']
        supplied_exercises = [n.get('id') for n in exercises if any(tag(c) == 'solution' for c in n)]
        missing_exercises = [n.get('id') for n in exercises if not any(tag(c) == 'solution' for c in n)]
        self.check(self.manifest['section_exercise_ids'] == [n.get('id') for n in exercises], 'section_exercise_ids')
        self.check(self.manifest['section_solution_ids'] == [n.get('id') for n in solutions], 'section_solution_ids')
        self.check(self.manifest['section_exercises_without_solutions'] == missing_exercises and len(supplied_exercises) == 30, 'section_solution_partition')
        self.check(set(self.manifest['section_solution_ids']).isdisjoint(missing_exercises), 'solution_absence_distinct')
        expected_canon = {
            'canon_study': ('next-unit', ['C01', 'C02', 'C03', 'C04', 'C06', 'C09', 'C10', 'C11']),
            'canon_draft': ('draft', ['C01', 'C02', 'C03', 'C04', 'C05', 'C06', 'C09', 'C10', 'C11']),
            'canon_revision': ('revision', ['C01', 'C02', 'C04', 'C05', 'C09', 'C10', 'C11']),
            'canon_qa': ('qa', ['C01', 'C02', 'C04', 'C05', 'C09', 'C10', 'C11']),
        }
        for key, (stage, ids) in expected_canon.items():
            receipt = json.loads(self.raw[key], object_pairs_hook=unique_object)
            expected_unit = 'PNB-012-study' if key == 'canon_study' else 'PNB-012'
            self.check(receipt['unit'] == expected_unit and receipt['stage'] == stage, 'canon_stage:' + key)
            self.check([row['id'] for row in receipt['examples']] == ids, 'canon_ids:' + key)
            self.check(receipt['claim'] == 'Passages displayed for agent reading; receipt alone is not evidence of linguistic correctness.', 'canon_limitation:' + key)

    def validate_translation(self):
        blocks = self.translation['source_blocks']
        self.check(list(blocks) == [k for k, _ in self.expected.blocks], 'translation_key_order')
        for key, node in self.expected.blocks:
            value = blocks[key]
            self.check(value == unicodedata.normalize('NFC', value), 'nfc:' + key)
            self.check(not any(unicodedata.category(c) == 'Cf' for c in value), 'no_format_controls:' + key)
            if tag(node) not in ('table', 'media'):
                for kind, nodes in self.expected.groups(node).items():
                    self.check(re.findall(r'\{\{' + kind + r':(\d+)\}\}', value) == [str(i) for i in range(len(nodes))], 'placeholders:' + key + ':' + kind)
            if not key.endswith('/alt'):
                ET.fromstring('<fragment>' + value + '</fragment>')
            # Compare every source-owned digit token independently of the
            # renderer. Math is checked tree-for-tree later, so its digits and
            # all other structural placeholders are excluded here.
            def source_owned_text(current):
                if tag(current) == 'table':
                    return current.get('summary', '')
                if tag(current) == 'media':
                    return current.get('alt', '')
                text = current.text or ''
                for child in current:
                    if tag(child) not in ('math', 'list', 'table', 'media', 'figure', 'footnote', 'para', 'term', 'link'):
                        text += source_owned_text(child)
                    text += child.tail or ''
                return text
            target_without_slots = re.sub(r'\{\{(?:math|term|link|child):\d+\}\}', '', value)
            if key.endswith('/alt'):
                target_fragment = ET.Element('fragment')
                target_fragment.text = target_without_slots
            else:
                target_fragment = ET.fromstring('<fragment>' + target_without_slots + '</fragment>')
            target_text = ''.join(target_fragment.itertext())
            source_text = source_owned_text(node)
            self.check(Counter(re.findall(r'\d+(?:[.,]\d+)*', source_text)) ==
                       Counter(re.findall(r'\d+(?:[.,]\d+)*', target_text)), 'prose_numeric_tokens:' + key)
            owned_emphasis = []
            def source_emphases(current):
                for child in current:
                    if tag(child) == 'emphasis':
                        owned_emphasis.append('em' if child.get('effect') == 'italics' else 'strong')
                        source_emphases(child)
                    elif tag(child) not in ('list', 'table', 'media', 'figure', 'footnote', 'para', 'term'):
                        source_emphases(child)
            if tag(node) not in ('table', 'media'):
                source_emphases(node)
            source_emphasis = Counter(owned_emphasis)
            target_emphasis = Counter(tag(n) for n in target_fragment.iter() if tag(n) in ('em', 'strong'))
            self.check(source_emphasis == target_emphasis, 'emphasis_fidelity:' + key)
            normalized_source_parts = source_text.replace('ⓐ', '(a)').replace('ⓑ', '(b)').replace('ⓒ', '(c)')
            self.check(re.findall(r'\([abc]\)', target_text) == re.findall(r'\([abc]\)', normalized_source_parts), 'part_tokens:' + key)
        self.check(len(self.translation['image_alt_overrides']) == len(self.translation['image_alt_note_ids']) == 44, 'all_image_descriptions')
        self.check(set(self.translation['image_alt_overrides']) == {x['media_id'] for x in self.manifest['images']}, 'image_description_ids')
        self.check(set(self.translation['image_alt_note_ids'].values()) == {'domain-alt-corrections', 'domain-alt-descriptions'}, 'image_note_classes')
        self.check(self.translation['translated_table_data_cells'] == ['fs-id1165137447518/row/1/entry/2', 'fs-id1165137447518/row/2/entry/2', 'fs-id1165137447518/row/3/entry/2'], 'table_data_keys')
        for needle in ('2000–2003', 'x≤−2', 'f(x)=x³', '(−∞,1]', '2002', '31'):
            self.check(needle in self.translation['bridge_after_html'] or needle in self.translation['bridge_before_html'], 'original_note:' + needle)
        self.check('−1/√x' not in self.translation['bridge_after_html'], 'no_false_negative_reciprocal_correction')
        self.check('1/√(x−2)' in self.translation['bridge_after_html'] and 'x&gt;2' in self.translation['bridge_after_html'], 'denominator_root_precision')

    def validate_assets(self, document):
        images = list(document.iter('img'))
        self.check(len(images) == 44, 'reader_images')
        by_id = self.ids(document)
        for spec in self.manifest['images']:
            source = ROOT / 'downloads/complete-upstream/osbooks-college-algebra-bundle' / spec['source_path']
            asset = BASE / spec['path']
            data = source.read_bytes()
            self.check(data == asset.read_bytes(), 'asset_unchanged:' + spec['media_id'])
            self.check(digest(data) == spec['sha256'] and len(data) == spec['bytes'], 'asset_hash:' + spec['media_id'])
            self.check(jpeg_dimensions(data) == (spec['width'], spec['height']), 'asset_dimensions:' + spec['media_id'])
            image = by_id[spec['media_id']]
            self.check(image.get('src') == '../' + spec['path'], 'asset_src:' + spec['media_id'])
            self.check(image.get('width') == str(spec['width']) and image.get('height') == str(spec['height']), 'asset_html_dimensions:' + spec['media_id'])
            key = spec['media_id'] + '/alt'
            self.check(image.get('data-source-alt') == self.translation['source_blocks'][key], 'source_alt:' + spec['media_id'])
            self.check(image.get('alt') == self.translation['image_alt_overrides'][spec['media_id']], 'accessible_alt:' + spec['media_id'])
            self.check(image.get('aria-describedby') == self.translation['image_alt_note_ids'][spec['media_id']], 'alt_note:' + spec['media_id'])
        notices = json.loads(self.raw['notice'], object_pairs_hook=unique_object)
        self.check(len(notices) == 44 and sum(x['classification'] == 'VERIFIED_EIA_PD' for x in notices) == 1, 'notice_partition')
        self.check(next(x for x in notices if x['classification'] == 'VERIFIED_EIA_PD')['asset_path'].endswith('009-e7be.jpg'), 'eia_notice_binding')
        for spec, notice in zip(self.manifest['images'], notices):
            self.check(notice['rights_component_id'] == spec['component_rights_id'], 'notice_component:' + spec['media_id'])
            self.check(notice['asset_path'] == spec['source_path'] and notice['sha256'] == spec['sha256'] and int(notice['bytes']) == spec['bytes'], 'notice_asset:' + spec['media_id'])
            self.check(notice['source_modules'] == 'm49304' and notice['admission'] == 'admitted', 'notice_scope:' + spec['media_id'])

    def validate_math(self, document):
        wrappers = [n for n in document.iter('span') if n.get('data-source-owner')]
        owners = self.expected.math_owners()
        self.check(len(wrappers) == len(owners) == 258, 'math_count')
        for wrapper, (key, slot, original) in zip(wrappers, owners):
            self.check((wrapper.get('data-source-owner'), wrapper.get('data-source-slot')) == (key, str(slot)), 'math_owner:' + key + ':' + str(slot))
            rendered = next(n for n in wrapper if tag(n) == 'math')
            clone = copy.deepcopy(rendered)
            clone.attrib.pop('dir', None)
            edits = json.loads(clone.attrib.pop('data-source-text-edits', '[]'))
            for edit in reversed(edits):
                leaf = clone
                for index in edit['path']:
                    leaf = leaf[index]
                # ElementTree parses a serialized empty leaf as ``None`` even
                # though the renderer records the replacement as ``""``.
                self.check((leaf.text or '') == edit['new'], 'math_edit_new:' + key)
                leaf.text = edit['old']
            expected = copy.deepcopy(original)
            expected.tail = None
            self.check(signature(clone) == signature(expected), 'math_reversible:' + key + ':' + str(slot))
            leaves = [n for n in original.iter() if not len(n) and (n.text or '').strip()]
            last = leaves[-1]
            should_edit = (tag(last) == 'mo' and last.text in ('.', ',')) or (tag(last) == 'mn' and re.fullmatch(r'−?\d+\.', last.text or '') is not None)
            self.check(bool(edits) == should_edit, 'math_edge_ledger:' + key + ':' + str(slot))

    @staticmethod
    def content_signature(node):
        return node.text, tuple((signature(child), child.tail) for child in node)

    @staticmethod
    def replace_node(root, target, replacement):
        parents = {child: node for node in root.iter() for child in node}
        parent = parents[target]
        replacement.tail = target.tail
        parent[list(parent).index(target)] = replacement

    def validate_blocks(self, document):
        """Reverse rendered placeholders and bind every translated source block."""
        keyed = [node for node in document.iter() if node.get('data-source-key')]
        keyed_by_key = {}
        for node in keyed:
            keyed_by_key.setdefault(node.get('data-source-key'), []).append(node)
        footnotes = [node for _, node in self.expected.blocks if tag(node) == 'footnote']
        special = {'table', 'media', 'footnote'}
        for key, original in self.expected.blocks:
            if tag(original) in special:
                continue
            self.check(len(keyed_by_key.get(key, [])) == 1, 'block_owner:' + key)
            clone = copy.deepcopy(keyed_by_key[key][0])
            groups = self.expected.groups(original)
            # Structural children are replaced first; by source contract the
            # other placeholder groups never descend into such children.
            for index, child in enumerate(groups['child']):
                sid = child.get('id')
                self.check(bool(sid), 'identified_child:' + key + ':' + str(index))
                target = next((n for n in clone.iter() if n.get('id') == sid), None)
                self.check(target is not None, 'rendered_child:' + key + ':' + str(index))
                if tag(child) in ('table', 'media'):
                    parents = {c: n for n in clone.iter() for c in n}
                    while target.get('data-source-child') != sid:
                        target = parents[target]
                self.replace_node(clone, target, ET.Element('ph', {'kind': 'child', 'index': str(index)}))
            for index, _ in enumerate(groups['math']):
                targets = [n for n in clone.iter('span') if n.get('data-source-owner') == key and n.get('data-source-slot') == str(index)]
                self.check(len(targets) == 1, 'block_math:' + key + ':' + str(index))
                self.replace_node(clone, targets[0], ET.Element('ph', {'kind': 'math', 'index': str(index)}))
            for index, term_node in enumerate(groups['term']):
                term_key = self.expected.keys[term_node]
                targets = [n for n in clone.iter() if n.get('data-source-key') == term_key]
                self.check(len(targets) == 1, 'block_term:' + key + ':' + str(index))
                self.replace_node(clone, targets[0], ET.Element('ph', {'kind': 'term', 'index': str(index)}))
            for index, _ in enumerate(groups['link']):
                link_key = key + '/link/' + str(index)
                targets = [n for n in clone.iter('a') if n.get('data-source-link') == link_key]
                self.check(len(targets) == 1, 'block_link:' + link_key)
                self.replace_node(clone, targets[0], ET.Element('ph', {'kind': 'link', 'index': str(index)}))
            value = re.sub(r'\{\{(math|term|link|child):(\d+)\}\}', r'<ph kind="\1" index="\2"/>', self.translation['source_blocks'][key])
            expected_fragment = ET.fromstring('<fragment>' + value + '</fragment>')
            self.check(self.content_signature(clone) == self.content_signature(expected_fragment), 'block_content:' + key)

        by_id = self.ids(document)
        for index, original in enumerate(footnotes, 1):
            sid, key = original.get('id'), self.expected.keys[original]
            body = copy.deepcopy(by_id[sid + '-text'])
            backlink = body[-1]
            self.check(tag(backlink) == 'a' and backlink.get('href') == '#' + sid and (backlink.tail or '') == '', 'footnote_backlink:' + sid)
            if len(body) > 1:
                self.check((body[-2].tail or '').endswith(' '), 'footnote_separator:' + sid)
                body[-2].tail = (body[-2].tail or '')[:-1] or None
            else:
                self.check((body.text or '').endswith(' '), 'footnote_separator:' + sid)
                body.text = (body.text or '')[:-1] or None
            body.remove(backlink)
            expected_fragment = ET.fromstring('<fragment>' + self.translation['source_blocks'][key] + '</fragment>')
            self.check(self.content_signature(body) == self.content_signature(expected_fragment), 'footnote_content:' + sid)

        for field in ('content-id', 'uuid'):
            source_value = next((node.text or '') for node in self.source.iter() if tag(node) == field)
            rendered = next(node for node in document.iter('p') if node.get('data-source-field') == field)
            self.check(''.join(rendered.itertext()) == source_value, 'metadata_value:' + field)

    def validate_document(self, document):
        self.check(tag(document) == 'html' and document.attrib == {'lang': 'pnb-Arab-PK', 'dir': 'rtl'}, 'html_frame')
        self.check([tag(c) for c in document] == ['head', 'body'], 'html_children')
        head, body = document
        self.check([tag(c) for c in body] == ['header', 'main', 'footer'], 'body_children')
        self.check(not any(tag(n) in ('script', 'iframe', 'object', 'embed') for n in document.iter()), 'no_active_content')
        by_id = self.ids(document)
        self.check(len(by_id) == len([n for n in document.iter() if n.get('id')]), 'unique_html_ids')
        source_ids = [n.get('id') for n in self.source.iter() if n.get('id')]
        rendered_source_ids = [n.get('id') for n in document.iter() if n.get('id') in set(source_ids)]
        self.check(rendered_source_ids == source_ids, 'source_id_order')
        self.check(all(key in by_id for key in ('domain-source-context', 'source-translation', 'domain-bridge', 'domain-restrictions', 'domain-piecewise', 'domain-historical', 'domain-alt-corrections', 'domain-alt-descriptions', 'domain-order', 'domain-table-summary')), 'original_note_ids')
        self.check(len(list(document.iter('article'))) == 82 and sum('source-solution' in n.get('class', '') for n in document.iter('section')) == 51, 'exercise_solution_counts')
        self.check(len([n for n in document.iter('a') if n.get('data-source-link')]) == 35, 'source_links')
        for row in self.manifest['source_links']:
            key = row['key']
            link = next(n for n in document.iter('a') if n.get('data-source-link') == key)
            attrs = row['attributes']
            expected = attrs.get('url') or ('unit-009.html' if attrs.get('document') else '#' + attrs['target-id'])
            self.check(link.get('href') == expected, 'link_target:' + key)
            label = self.translation['source_link_labels'].get(key)
            if label is None:
                target_node = next(n for n in self.source.iter() if n.get('id') == attrs['target-id'])
                label = {'figure': 'متعلقہ شکل', 'example': 'متعلقہ مثال', 'table': 'متعلقہ جدول'}.get(tag(target_node), 'متعلقہ حصہ')
            self.check(''.join(link.itertext()) == ''.join(ET.fromstring('<fragment>' + label + '</fragment>').itertext()), 'link_label:' + key)
        table = by_id['fs-id1165137447518']
        self.check(table.get('data-source-summary') == '..' and table.get('aria-label') == self.translation['table_summary_overrides']['fs-id1165137447518'], 'table_summary_binding')
        rows = list(table.iter('tr'))
        self.check(len(rows) == 3 and all([tag(c) for c in row] == ['th', 'td'] for row in rows), 'table_shape_semantics')
        self.check(all(row[0].get('scope') == 'row' and row[0].get('dir') == 'rtl' and row[1].get('dir') == 'rtl' for row in rows), 'table_directions')
        self.check([cell.get('data-source-key') for row in rows for cell in row] ==
                   ['fs-id1165137447518/row/' + str(row) + '/entry/' + str(entry)
                    for row in range(1, 4) for entry in range(1, 3)], 'table_cell_order')
        self.validate_assets(document)
        self.validate_math(document)
        self.validate_blocks(document)
        source_section = by_id['source-translation']
        allowed = {'h1', 'h2', 'h3', 'h4', 'h5', 'p', 'div', 'section', 'article', 'aside', 'figure', 'figcaption', 'ol', 'ul', 'li', 'span', 'sup', 'a', 'bdi', 'em', 'strong', 'dt', 'dd', 'dl', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'colgroup', 'col', 'img'}
        self.check(all(tag(n) in allowed or n.tag.startswith('{' + MATH + '}') for n in source_section.iter()), 'source_container_node_kinds')
        self.check(source_section.attrib == {'id': 'source-translation'} and (source_section.text or '') == '' and (source_section.tail or '') == '', 'source_section_frame')
        html_counts = Counter(tag(n) for n in source_section.iter() if not n.tag.startswith('{' + MATH + '}'))
        expected_counts = Counter({'span': 286, 'p': 275, 'div': 196, 'bdi': 170, 'a': 126,
            'article': 82, 'h4': 82, 'section': 80, 'li': 52, 'h5': 51, 'img': 44,
            'h3': 38, 'figure': 26, 'aside': 25, 'strong': 24, 'h2': 16, 'em': 15,
            'figcaption': 12, 'ol': 11, 'ul': 4, 'tr': 3, 'th': 3, 'td': 3, 'dt': 3,
            'dd': 3, 'sup': 2, 'col': 2, 'h1': 1, 'table': 1, 'colgroup': 1,
            'tbody': 1, 'dl': 1})
        self.check(html_counts == expected_counts and len(list(source_section.iter())) == 5050, 'complete_source_element_inventory')
        self.check(not any(n.get('hidden') is not None or n.get('aria-hidden') == 'true' or 'display:none' in n.get('style', '').replace(' ', '') for n in source_section.iter()), 'source_content_visible')

        source_set = set(source_ids)
        source_parent = {c: n for n in self.source.iter() for c in n}
        html_parent = {c: n for n in source_section.iter() for c in n}
        for sid in source_ids:
            source_node = next(n for n in self.source.iter() if n.get('id') == sid)
            ancestor = source_parent.get(source_node)
            while ancestor is not None and ancestor.get('id') not in source_set:
                ancestor = source_parent.get(ancestor)
            expected_parent = ancestor.get('id') if ancestor is not None else None
            rendered = by_id[sid]
            actual_ancestor = html_parent.get(rendered)
            while actual_ancestor is not None and actual_ancestor.get('id') not in source_set:
                actual_ancestor = html_parent.get(actual_ancestor)
            actual_parent = actual_ancestor.get('id') if actual_ancestor is not None else None
            self.check(actual_parent == expected_parent, 'source_id_ancestor:' + sid)
            source_name = tag(source_node)
            expected_tag = {
                'para': 'div' if any(tag(c) == 'list' for c in source_node) else 'p',
                'exercise': 'article', 'problem': 'div', 'solution': 'section', 'media': 'img',
                'figure': 'figure', 'note': 'aside', 'equation': 'div',
                'list': 'ol' if source_node.get('list-type') == 'enumerated' else 'ul',
                'term': 'span', 'section': 'section', 'example': 'section', 'commentary': 'aside',
                'definition': 'div', 'meaning': 'dd', 'footnote': 'sup', 'table': 'table',
            }[source_name]
            self.check(tag(rendered) == expected_tag, 'source_wrapper:' + sid)
            omitted = {'alt'} if source_name == 'media' else {'summary'} if source_name == 'table' else set()
            for name, value in source_node.attrib.items():
                if name != 'id' and name not in omitted:
                    self.check(rendered.get('data-source-' + name) == value, 'source_attribute:' + sid + ':' + name)
            for name in ('class', 'list-type', 'number-style', 'display', 'align', 'colname', 'colnum'):
                self.check(rendered.get('data-source-' + name) == source_node.get(name), 'source_attribute_complete:' + sid + ':' + name)
            if rendered.get('data-source-key') is None:
                self.check((rendered.text or '').strip() == '', 'structural_own_text:' + sid)
            if tag(source_node) not in ('term', 'footnote'):
                self.check((rendered.tail or '').strip() == '', 'structural_tail:' + sid)

    def mutation(self, label, change):
        clone = copy.deepcopy(self.document)
        change(clone)
        try:
            self.validate_document(clone)
        except AssertionError:
            self.mutations += 1
            self.mutation_labels.append(label)
            return
        raise AssertionError('Mutation escaped: ' + label)

    def input_mutation(self, label, change, validate):
        manifest, translation, raw = copy.deepcopy(self.manifest), copy.deepcopy(self.translation), dict(self.raw)
        change()
        try:
            validate()
        except AssertionError:
            self.mutations += 1
            self.mutation_labels.append(label)
            return
        finally:
            self.manifest, self.translation, self.raw = manifest, translation, raw
        raise AssertionError('Input mutation escaped: ' + label)

    def validate_mutations(self):
        def by_id(root, sid):
            return next(n for n in root.iter() if n.get('id') == sid)
        def first_keyed(root, key):
            return next(n for n in root.iter() if n.get('data-source-key') == key)
        def change_prose(root):
            node = first_keyed(root, 'fs-id1165137404978')
            node.text = 'CONTRADICTORY 999'
        def change_emphasis(root):
            next(root.iter('strong')).tag = 'em'
        def change_link_label(root):
            link = next(n for n in root.iter('a') if n.get('data-source-link'))
            link.text = 'غلط حوالہ'
            for child in list(link):
                link.remove(child)
        def change_ledger(root):
            math = next(n for n in root.iter('{' + MATH + '}math') if n.get('data-source-text-edits'))
            math.set('data-source-text-edits', '[]')
        def swap_table_rows(root):
            table = by_id(root, 'fs-id1165137447518')
            tbody = next(table.iter('tbody'))
            tbody[0], tbody[1] = tbody[1], tbody[0]
        def change_footnote_tail(root):
            body = by_id(root, 'fs-id1165137758551-text')
            body[-1].tail = ' CONTRADICTORY 999'
        def move_solution(root):
            solution = by_id(root, 'fs-id1165135329797')
            parents = {c: n for n in root.iter() for c in n}
            parents[solution].remove(solution)
            by_id(root, 'source-translation').append(solution)
        def swap_wrapper_tags(root):
            by_id(root, 'fs-id1165137772018').tag = 'section'
            by_id(root, 'fs-id1165135329797').tag = 'div'
        self.mutation('changed_math_number', lambda d: setattr(next(n for n in d.iter('{' + MATH + '}mn')), 'text', '999'))
        self.mutation('removed_math_text_edit_ledger', change_ledger)
        self.mutation('changed_asset_src', lambda d: by_id(d, 'fs-id1165135435537').set('src', '../assets/fake.jpg'))
        self.mutation('changed_source_alt', lambda d: by_id(d, 'fs-id1165137424715').set('data-source-alt', 'x>=999'))
        self.mutation('changed_accessible_alt', lambda d: by_id(d, 'fs-id1165137447903').set('alt', 'wrong endpoint'))
        self.mutation('hidden_source_image', lambda d: by_id(d, 'fs-id1165135435537').set('hidden', 'hidden'))
        self.mutation('removed_source_id', lambda d: by_id(d, 'fs-id1165135193832').attrib.pop('id'))
        self.mutation('changed_external_link', lambda d: next(n for n in d.iter('a') if n.get('data-source-link') == 'fs-id1165135189954/item/1/link/0').set('href', 'https://example.invalid'))
        self.mutation('changed_source_link_label', change_link_label)
        self.mutation('changed_translated_prose_and_number', change_prose)
        self.mutation('changed_source_emphasis_effect', change_emphasis)
        self.mutation('removed_precision_note', lambda d: by_id(d, 'domain-restrictions').attrib.pop('id'))
        self.mutation('table_header_demoted', lambda d: setattr(next(by_id(d, 'fs-id1165137447518').iter('th')), 'tag', 'td'))
        self.mutation('table_rows_swapped', swap_table_rows)
        self.mutation('footnote_backlink_tail_injection', change_footnote_tail)
        self.mutation('source_solution_reparented', move_solution)
        self.mutation('source_wrapper_types_swapped', swap_wrapper_tags)
        self.mutation('source_list_type_changed', lambda d: by_id(d, 'list-00001').set('data-source-list-type', 'bulleted'))
        self.mutation('source_structural_tail_injection', lambda d: setattr(by_id(d, 'fs-id1165135193832'), 'tail', ' CONTRADICTORY 999'))
        self.mutation('extra_source_paragraph', lambda d: by_id(d, 'source-translation').append(ET.Element('p', {'dir': 'ltr'})))
        self.mutation('hidden_source_section', lambda d: by_id(d, 'source-translation').set('hidden', 'hidden'))
        self.input_mutation('manifest_source_image_path_changed',
                            lambda: self.manifest['images'][0].__setitem__('source_path', 'media/fake.jpg'), self.validate_source)
        self.input_mutation('manifest_source_links_reordered',
                            lambda: self.manifest['source_links'].__setitem__(slice(0, 2), list(reversed(self.manifest['source_links'][:2]))), self.validate_source)
        self.input_mutation('manifest_missing_solution_claim_changed',
                            lambda: self.manifest['section_exercises_without_solutions'].__setitem__(0, self.manifest['section_exercise_ids'][0]), self.validate_source)
        self.input_mutation('translation_table_semantics_reversed',
                            lambda: self.translation.__setitem__('translated_table_data_cells', ['fs-id1165137447518/row/1/entry/1']), self.validate_translation)
        self.input_mutation('translated_prose_number_changed',
                            lambda: self.translation['source_blocks'].__setitem__('fs-id1165137404978', self.translation['source_blocks']['fs-id1165137404978'].replace('2000', '2003', 1)), self.validate_translation)
        def change_notice():
            notices = json.loads(self.raw['notice'], object_pairs_hook=unique_object)
            notices[0]['sha256'] = '0' * 64
            self.raw['notice'] = json.dumps(notices, ensure_ascii=False).encode('utf-8')
        self.input_mutation('component_notice_hash_changed', change_notice, lambda: self.validate_assets(self.document))
        def change_canon_stage():
            receipt = json.loads(self.raw['canon_qa'], object_pairs_hook=unique_object)
            receipt['stage'] = 'unread'
            self.raw['canon_qa'] = json.dumps(receipt, ensure_ascii=False).encode('utf-8')
        self.input_mutation('canon_qa_stage_changed', change_canon_stage, self.validate_source)

    def run(self):
        self.validate_source()
        self.validate_translation()
        self.validate_document(self.document)
        self.validate_mutations()
        if not self.check_only:
            before = self.paths['reader'].read_bytes()
            subprocess.run([sys.executable, '-B', str(BASE / 'scripts/build_domain_range.py'), '--unit', '012'], cwd=ROOT, check=True, capture_output=True)
            first = self.paths['reader'].read_bytes()
            subprocess.run([sys.executable, '-B', str(BASE / 'scripts/build_domain_range.py'), '--unit', '012'], cwd=ROOT, check=True, capture_output=True)
            second = self.paths['reader'].read_bytes()
            self.check(before == first == second, 'deterministic_build')
            self.raw['reader'] = second
        receipt = {
            'unit': 'PNB-012', 'status': 'source-structure-math-and-assets-passed; native-visual-educator-review-pending',
            'checks_passed': self.checks, 'detached_mutations_rejected': self.mutations,
            'mutations': self.mutation_labels,
            'reader_sha256': digest(self.paths['reader'].read_bytes()),
            'source_statistics': self.manifest['source_statistics'],
            'scope': 'Complete canonical m49304 source/key/ID/ancestry/block/number/emphasis/part-token/MathML/table/link/footnote/image and supplied-solution binding; independent source expectations; no renderer expected-DOM import.',
            'limitations': ['Native Punjabi specialist and mathematics-educator review pending',
                            'Browser review is separate from source-bound automated checks',
                            'Finite image descriptions and source examples are not universal mathematical, historical, market, legal or pricing verification',
                            'Canon passages are prose usage evidence, not mathematical terminology authority or native certification',
                            'The complete five-work assignment remains active'],
            'inputs': {key: {'path': path.relative_to(BASE).as_posix(), 'sha256': digest(path.read_bytes())}
                       for key, path in self.paths.items() if key != 'reader'},
        }
        if not self.check_only:
            out = BASE / 'qa/structural-012.json'
            out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
        return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    print(json.dumps(QA(args.check_only).run(), ensure_ascii=False, sort_keys=True))
