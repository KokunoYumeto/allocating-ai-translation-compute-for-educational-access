"""Independent source-bound QA for complete canonical m49306 / PNB-013."""
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
CANONICAL = ROOT / 'downloads/upstream/osbooks-college-algebra-bundle/modules/m49306/index.cnxml'


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
                key = ('m49306/title' if owner is source else 'm49306/metadata/title'
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
        assert len(self.blocks) == len(set(k for k, _ in self.blocks)) == 353
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
            'break': list(descendants(node, 'newline')),
            'child': [c for c in node if (c in self.keys and tag(c) != 'term') or tag(c) in ('list', 'table', 'media', 'figure')],
        }

    def template(self, node):
        if tag(node) == 'table':
            return node.get('summary', '')
        if tag(node) == 'media':
            return node.get('alt', '')
        groups = self.groups(node)
        lookup = {child: (kind, index) for kind, nodes in groups.items()
                  for index, child in enumerate(nodes)}
        def inline(current):
            value = current.text or ''
            for child in current:
                if child in lookup:
                    kind, index = lookup[child]
                    value += '{{' + kind + ':' + str(index) + '}}'
                else:
                    value += inline(child)
                value += child.tail or ''
            return value
        return inline(node)

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
        assert len(result) == 254
        return result


class QA:
    def __init__(self, check_only=False):
        self.check_only, self.checks, self.mutations = check_only, 0, 0
        self.mutation_labels = []
        self.paths = {
            'excerpt': BASE / 'source-excerpts/unit-013.cnxml',
            'manifest': BASE / 'source-excerpts/manifest-013.json',
            'translation': BASE / 'translations/unit-013.json',
            'translation_part_a': BASE / 'translations/unit-013-part-a.json',
            'translation_part_b': BASE / 'translations/unit-013-part-b.json',
            'translation_shell': BASE / 'translations/unit-013-shell.json',
            'notes': BASE / 'qa/unit-013-language-notes.md',
            'notice': BASE / 'provenance/unit-013-component-notices.json',
            'canon_study': BASE / 'canon/receipts/PNB-013-study-next-unit-20260901T142834088775Z.json',
            'canon_draft': BASE / 'canon/receipts/PNB-013-part-b-draft-20260901T155502197593Z.json',
            'canon_revision': BASE / 'canon/receipts/PNB-013-part-b-revision-20260901T161106552203Z.json',
            'canon_qa': BASE / 'canon/receipts/PNB-013-qa-20260901T185936943200Z.json',
            'prepare': BASE / 'scripts/prepare_behavior.py',
            'assemble': BASE / 'scripts/assemble_behavior_translation.py',
            'build': BASE / 'scripts/build_behavior.py',
            'qa': BASE / 'scripts/qa_behavior.py',
            'reader': BASE / 'reader/unit-013.html',
            'style': BASE / 'styles/reader.css',
            'terms': BASE / 'terminology.tsv',
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
        self.check(digest(canonical) == '043afbc674a470470bf2288160f0136e32fe72740f76a73c2d52ba4a95b29370', 'canonical_raw_hash')
        self.check(digest(lf) == self.manifest['full_module_sha256'] == '87e3bea0a14b4f487e0a5428b8138a644b0630b692d02c5a0e348e26ae3e6806', 'canonical_lf_hash')
        self.check(excerpt_lf == lf + (b'' if lf.endswith(b'\n') else b'\n'), 'whole_module_excerpt')
        self.check(signature(self.source) == signature(ET.fromstring(canonical)), 'xml_exact_except_eol')
        counts = {name: sum(tag(n) == name for n in self.source.iter()) for name in ('math', 'media', 'figure', 'table', 'link', 'footnote', 'exercise', 'solution')}
        self.check(counts == {'math': 254, 'media': 24, 'figure': 19, 'table': 5, 'link': 37, 'footnote': 1, 'exercise': 61, 'solution': 38}, 'source_counts')
        self.check(len(list(self.source.iter())) - 1 == 3436, 'source_elements')
        source_ids = [n.get('id') for n in self.source.iter() if n.get('id')]
        self.check(len(source_ids) == len(set(source_ids)) == 438 == self.manifest['source_statistics']['identified_nodes'], 'source_ids')
        self.check(self.manifest['source_block_keys'] == [k for k, _ in self.expected.blocks], 'manifest_key_order')
        self.check(self.manifest['source_block_templates'] == {k: self.expected.template(n) for k, n in self.expected.blocks}, 'manifest_templates_exact')
        expected_slots = {k: ({} if tag(node) in ('table', 'media') else
                              {kind: [self.expected.paths[item] for item in nodes]
                               for kind, nodes in self.expected.groups(node).items() if nodes})
                          for k, node in self.expected.blocks}
        self.check(self.manifest['source_block_slots'] == expected_slots, 'manifest_slots_exact')
        self.check(self.manifest['source_ids'] == source_ids, 'manifest_id_order')
        self.check(self.manifest['module_metadata'] == {'content_id': 'm49306',
                   'uuid': '3b988a5f-9566-4f24-8c2b-7ae001b71d2c',
                   'root_attributes': {}, 'source_order': ['content-id', 'title', 'abstract', 'uuid']}, 'metadata_exact')
        self.check(self.manifest['next_module'] == 'm49308' and self.manifest['next_source_id'] is None, 'whole_module_boundary')
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
            self.check(row['path'] == 'assets/unit-013-' + media.get('id') + '.jpg' and row['publication_status'] == 'admitted-unchanged', 'manifest_publication_binding:' + media.get('id'))
        derived_links = []
        for owner_key, owner in self.expected.blocks:
            for index, link in enumerate(self.expected.groups(owner)['link']):
                derived_links.append({'key': owner_key + '/link/' + str(index), 'attributes': dict(link.attrib),
                                      'text': ''.join(link.itertext()), 'path': self.expected.paths[link]})
        self.check(self.manifest['source_links'] == derived_links, 'manifest_source_links_exact')
        self.check(self.manifest['source_link_labels'] == {'fs-id1165135708041/item/1/link/0': 'Average Rate of Change'}, 'source_link_labels_exact')
        section = next(n for n in self.source.iter() if n.get('id') == 'fs-id1165135457748')
        exercises = [n for n in section.iter() if tag(n) == 'exercise']
        solutions = [n for n in section.iter() if tag(n) == 'solution']
        supplied_exercises = [n.get('id') for n in exercises if any(tag(c) == 'solution' for c in n)]
        missing_exercises = [n.get('id') for n in exercises if not any(tag(c) == 'solution' for c in n)]
        self.check(self.manifest['section_exercise_ids'] == [n.get('id') for n in exercises], 'section_exercise_ids')
        self.check(self.manifest['section_solution_ids'] == [n.get('id') for n in solutions], 'section_solution_ids')
        self.check(self.manifest['section_exercises_without_solutions'] == missing_exercises and len(supplied_exercises) == 24 and len(missing_exercises) == 23, 'section_solution_partition')
        self.check(set(self.manifest['section_solution_ids']).isdisjoint(missing_exercises), 'solution_absence_distinct')
        footnote = next(n for n in self.source.iter() if tag(n) == 'footnote')
        footnote_text = ''.join(footnote.itertext())
        self.check('3/5/2014' in footnote_text and 'http://www.eia.gov/totalenergy/data/annual/showtext.cfm?t=ptb0524' in footnote_text, 'dated_footnote_witness')
        table = next(n for n in self.source.iter() if n.get('id') == 'Table_01_03_03')
        rows = [[(''.join(entry.itertext())).strip() for entry in row]
                for row in table.iter() if tag(row) == 'row']
        self.check('(2004, 243)' in table.get('summary') and rows[7] == ['2004', '249'], 'table_243_249_discrepancy')

    def validate_translation(self):
        blocks = self.translation['source_blocks']
        self.check(list(blocks) == [k for k, _ in self.expected.blocks], 'translation_key_order')
        part_a = json.loads(self.raw['translation_part_a'], object_pairs_hook=unique_object)
        part_b = json.loads(self.raw['translation_part_b'], object_pairs_hook=unique_object)
        shell = json.loads(self.raw['translation_shell'], object_pairs_hook=unique_object)
        self.check(list(part_a) == list(part_b) == ['source_blocks'], 'translation_part_frames')
        self.check(list(part_a['source_blocks']) == self.manifest['source_block_keys'][:157] and
                   list(part_b['source_blocks']) == self.manifest['source_block_keys'][157:],
                   'translation_part_boundary')
        combined = {**part_a['source_blocks'], **part_b['source_blocks']}
        self.check(combined == blocks, 'translation_parts_assemble_exactly')
        for key, node in self.expected.blocks:
            value = blocks[key]
            self.check(value == unicodedata.normalize('NFC', value), 'nfc:' + key)
            self.check(not any(unicodedata.category(c) == 'Cf' for c in value), 'no_format_controls:' + key)
            if tag(node) not in ('table', 'media'):
                for kind, nodes in self.expected.groups(node).items():
                    self.check(re.findall(r'\{\{' + kind + r':(\d+)\}\}', value) == [str(i) for i in range(len(nodes))], 'placeholders:' + key + ':' + kind)
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
            target_without_slots = re.sub(r'\{\{(?:math|term|link|child|break):\d+\}\}', '', value)
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
            normalized_source_parts = source_text.replace('ⓐ', '(a)').replace('ⓑ', '(b)').replace('ⓒ', '(c)').replace('ⓓ', '(d)')
            self.check(re.findall(r'\([abcd]\)', target_text) == re.findall(r'\([abcd]\)', normalized_source_parts), 'part_tokens:' + key)
        self.check(len(self.translation['image_alt_overrides']) == len(self.translation['image_alt_note_ids']) == 24, 'all_image_descriptions')
        self.check(set(self.translation['image_alt_overrides']) == {x['media_id'] for x in self.manifest['images']}, 'image_description_ids')
        self.check(set(self.translation['image_alt_note_ids'].values()) == {'behavior-alt-corrections', 'behavior-alt-descriptions'}, 'image_note_classes')
        alt_text = '\n'.join(self.translation['image_alt_overrides'].values())
        self.check(not re.search(r'(?i)\b(?:reciprocal|minimum|maximum|toolkit|alt|milligrams|exponential|mg)\b', alt_text)
                   and not any(value.startswith('A مقدار') for value in self.translation['image_alt_overrides'].values())
                   and 'V شکل' not in alt_text and 'عند' not in alt_text,
                   'accessible_alts_punjabi_register')
        self.check(all('بنیادی اوزاراں دی جدول' in self.translation['image_alt_overrides'][sid]
                       for sid in ('fs-id1165135186344', 'fs-id1165137834947', 'fs-id1165137834962')),
                   'toolkit_alts_localized')
        self.check('اُلٹ قدر' in self.translation['image_alt_overrides']['fs-id1165137888935'] and
                   'اُلٹ قدر' in self.translation['image_alt_overrides']['fs-id1165134080979'],
                   'reciprocal_alts_localized')
        self.check('سبھ توں چھوٹی قدر' in self.translation['image_alt_overrides']['fs-id1165134377142'] and
                   'سبھ توں وڈی قدر' in self.translation['image_alt_overrides']['fs-id1165134377142'] and
                   'وڈی قدر' in self.translation['image_alt_overrides']['fs-id1165134298977'],
                   'extrema_alts_localized')
        self.check('ملی گرام' in self.translation['image_alt_overrides']['fs-id1165135517159'] and
                   'قوت نمائی' in self.translation['image_alt_overrides']['fs-id1165135517159'],
                   'radioactive_graph_alt_localized')
        entry_keys = [key for key, node in self.expected.blocks if tag(node) == 'entry']
        headers = self.translation['table_header_cells']
        self.check(len(entry_keys) == 78 and len(headers) == 9 and self.translation['translated_table_data_cells'] == [key for key in entry_keys if key not in headers], 'table_data_keys')
        self.check(set(self.translation['table_header_scopes']) == set(headers) and Counter(self.translation['table_header_scopes'].values()) == Counter({'row': 5, 'col': 4}), 'table_header_scopes')
        assembled = dict(shell)
        assembled['translated_table_data_cells'] = [key for key in entry_keys if key not in headers]
        assembled['source_blocks'] = combined
        self.check(assembled == self.translation, 'translation_shell_assembly_exact')
        self.check(self.translation['title'] == blocks['m49306/title'] ==
                   'بدلاوے دیاں شرحاں تے گرافاں دا ورتارا', 'page_title_target_terminology')
        self.check(self.translation['subtitle'].startswith('بدلاوے دی اوسط شرح') and
                   'تبدیلی' not in self.translation['subtitle'] and 'رویہ' not in self.translation['subtitle'],
                   'page_subtitle_target_terminology')
        self.check(self.translation['source_link_labels'] ==
                   {'fs-id1165135708041/item/1/link/0': 'بدلاوے دی اوسط شرح'},
                   'external_link_target_terminology')
        self.check(set(self.translation['table_summary_overrides']) == {'Table_01_03_01', 'Table_01_03_02', 'eip-id1165135358784', 'Table_01_03_03', 'Table_01_03_04'}, 'table_summary_ids')
        for needle in ('2004→243', '>249</bdi>', 'x₂≠x₁', 'a≠0', 'a≠5', 'fs-id1165135536272', 'f(b)', 'Figure015/014', '3/5/2014'):
            self.check(needle in self.translation['bridge_after_html'] or needle in self.translation['bridge_before_html'], 'original_note:' + needle)
        self.check('24' in self.translation['bridge_before_html'] and '23' in self.translation['bridge_before_html'], 'solution_partition_note')
        self.check('{{break:0}}' in blocks['fs-id1165137418913'], 'source_newline_placeholder')
        self.check('فنکشن کیویں بدلدے نیں' in blocks['fs-id1165137784644'] and
                   'فنکشن کیویں بدل دے نیں' not in blocks['fs-id1165137784644'],
                   'attached_plural_verb')
        self.check('ایس طرح' in blocks['fs-id1165137784644'] and
                   'ایسے طرح' not in blocks['fs-id1165137784644'],
                   'punjabi_comparison_connector')
        self.check('ایسیاں قدراں' in blocks['fs-id1165134272749'] and
                   'ایسی قدراں' not in blocks['fs-id1165134272749'] and
                   'ایسے طرح' not in blocks['fs-id1165134272749'],
                   'punjabi_plural_modifier_and_connector')
        self.check(all('ایہو جیہا عدد' in blocks[key] and 'ایسا عدد' not in blocks[key]
                       for key in ('fs-id1165134378691', 'fs-id1165134299106')),
                   'punjabi_indefinite_number_phrase')
        self.check('اوہنے <bdi dir="ltr">10.7</bdi> گیلن پیٹرول بھریا سی' in
                   blocks['fs-id1165135387238'], 'fuel_pumping_action')
        self.check(blocks['fs-id1165135481945/title'] == 'اہم خیالاں',
                   'key_concepts_plural')
        self.check('اوسط رخ والی رفتار' in blocks['fs-id1165135387257'] and
                   'average speed' in self.translation['bridge_after_html'] and
                   'average velocity' in self.translation['bridge_after_html'] and
                   'اوسط سمتی رفتار' in self.translation['bridge_after_html'],
                   'speed_velocity_distinction')
        bridge = ET.fromstring(self.translation['bridge_after_html'])
        visible_ascii = []
        for node in bridge.iter():
            if node.text and re.search(r'[A-Za-z]', node.text):
                visible_ascii.append((node, node.text))
            for child in node:
                if child.tail and re.search(r'[A-Za-z]', child.tail):
                    visible_ascii.append((node, child.tail))
        self.check(all(tag(carrier) == 'bdi' and carrier.get('dir') == 'ltr'
                       for carrier, _ in visible_ascii), 'bridge_visible_ascii_ltr_isolated')
        english_runs = ('rational', 'average speed', 'average velocity', 'canonical', 'summary',
                        'metadata', 'Toolkit', 'alt', 'reciprocal', 'exact', 'Figure015/014',
                        'source ID', 'file-name', 'mapping', 'JPEG', 'SVG', 'redraw',
                        'rate of change', 'average rate of change', 'increasing/decreasing',
                        'local extrema', 'absolute maximum/minimum', 'assignment')
        english_bdis = [node for node in bridge.iter('bdi')
                        if node.get('dir') == 'ltr' and node.get('lang') == 'en']
        for run in english_runs:
            self.check(any(run in ''.join(node.itertext()) for node in english_bdis),
                       'bridge_english_run_tagged:' + run)
        notes = self.raw['notes'].decode('utf-8')
        self.check('No contemporaneous Part A or whole-unit draft/revision canon receipt exists' in notes and
                   'No receipt was fabricated, backdated or retroactively claimed' in notes,
                   'truthful_canon_receipt_gap')
        canon_qa = json.loads(self.raw['canon_qa'], object_pairs_hook=unique_object)
        canon_examples = {row['id']: row for row in canon_qa['examples']}
        self.check(canon_qa['stage'] == 'qa' and canon_qa['unit'] == 'PNB-013' and
                   set(canon_examples) == {'C01', 'C02', 'C04', 'C05', 'C06', 'C09', 'C10', 'C11'},
                   'whole_unit_qa_canon_scope')
        self.check(canon_examples['C04']['quote'] == 'صفحے گھٹ ودھ وی ہوندے رہے' and
                   canon_examples['C04']['paragraph_sha256'] == '2b8bfffa5cc63fcf6c267d51dbed8c23de3ec997bc4c0a6bf6299ef78d209e49',
                   'whole_unit_qa_c04_hash')

    def validate_assets(self, document):
        images = list(document.iter('img'))
        self.check(len(images) == 24, 'reader_images')
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
        self.check(len(notices) == 24 and all(x['classification'] == 'WORK_DEFAULT_UNCREDITED_ART' for x in notices), 'notice_partition')
        for spec, notice in zip(self.manifest['images'], notices):
            self.check(notice['rights_component_id'] == spec['component_rights_id'], 'notice_component:' + spec['media_id'])
            self.check(notice['asset_path'] == spec['source_path'] and notice['sha256'] == spec['sha256'] and int(notice['bytes']) == spec['bytes'], 'notice_asset:' + spec['media_id'])
            self.check(notice['source_modules'] == 'm49306' and notice['admission'] == 'admitted' and notice['license_id'] == 'CC-BY-NC-SA-4.0', 'notice_scope:' + spec['media_id'])

    def validate_math(self, document):
        wrappers = [n for n in document.iter('span') if n.get('data-source-owner')]
        owners = self.expected.math_owners()
        self.check(len(wrappers) == len(owners) == 254, 'math_count')
        for wrapper, (key, slot, original) in zip(wrappers, owners):
            self.check((wrapper.get('data-source-owner'), wrapper.get('data-source-slot')) == (key, str(slot)), 'math_owner:' + key + ':' + str(slot))
            rendered = next(n for n in wrapper if tag(n) == 'math')
            clone = copy.deepcopy(rendered)
            clone.attrib.pop('dir', None)
            edits = clone.attrib.pop('data-source-text-edits', None)
            self.check(edits is None, 'math_has_no_text_edit_ledger:' + key + ':' + str(slot))
            expected = copy.deepcopy(original)
            expected.tail = None
            self.check(signature(clone) == signature(expected), 'math_exact:' + key + ':' + str(slot))

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
            for index, original_break in enumerate(groups['break']):
                targets = [n for n in clone.iter('br') if n.get('data-source-break') == self.expected.paths[original_break]]
                self.check(len(targets) == 1, 'block_break:' + key + ':' + str(index))
                self.replace_node(clone, targets[0], ET.Element('ph', {'kind': 'break', 'index': str(index)}))
            value = re.sub(r'\{\{(math|term|link|child|break):(\d+)\}\}', r'<ph kind="\1" index="\2"/>', self.translation['source_blocks'][key])
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
        note_ids = ('behavior-source-context', 'source-translation', 'behavior-bridge', 'behavior-rate-domain',
                    'behavior-velocity-bridge',
                    'behavior-extrema-precision', 'behavior-underdetermined', 'behavior-table-correction',
                    'behavior-alt-corrections', 'behavior-alt-descriptions', 'behavior-historical',
                    'behavior-table-summary')
        self.check(all(key in by_id for key in note_ids), 'original_note_ids')
        bridge = by_id['behavior-bridge']
        visible_ascii = []
        for node in bridge.iter():
            if node.text and re.search(r'[A-Za-z]', node.text):
                visible_ascii.append((node, node.text))
            for child in node:
                if child.tail and re.search(r'[A-Za-z]', child.tail):
                    visible_ascii.append((node, child.tail))
        self.check(all(tag(carrier) == 'bdi' and carrier.get('dir') == 'ltr'
                       for carrier, _ in visible_ascii), 'reader_bridge_visible_ascii_ltr_isolated')
        english_words = ('rational', 'canonical', 'summary', 'metadata', 'Toolkit', 'alt',
                         'reciprocal', 'exact', 'Figure015/014', 'source ID', 'file-name',
                         'mapping', 'JPEG', 'SVG', 'redraw', 'assignment')
        self.check(all(any(word in ''.join(node.itertext())
                           for node in bridge.iter('bdi')
                           if node.get('dir') == 'ltr' and node.get('lang') == 'en')
                       for word in english_words), 'reader_bridge_english_lang_tags')
        table_summary_note = by_id['behavior-table-summary']
        self.check([(node.text, node.attrib) for node in table_summary_note.iter('bdi')] == [
            ('summary', {'dir': 'ltr', 'lang': 'en'}),
            ('data-source-summary', {'dir': 'ltr', 'lang': 'en'}),
            ('aria-label', {'dir': 'ltr', 'lang': 'en'})], 'table_summary_bidi_isolates')
        self.check(len(list(document.iter('article'))) == 61 and sum('source-solution' in n.get('class', '') for n in document.iter('section')) == 38, 'exercise_solution_counts')
        self.check(len([n for n in document.iter('a') if n.get('data-source-link')]) == 37, 'source_links')
        for row in self.manifest['source_links']:
            key = row['key']
            link = next(n for n in document.iter('a') if n.get('data-source-link') == key)
            attrs = row['attributes']
            expected = attrs.get('url') or '#' + attrs['target-id']
            self.check(link.get('href') == expected, 'link_target:' + key)
            label = self.translation['source_link_labels'].get(key)
            if label is None:
                target_node = next(n for n in self.source.iter() if n.get('id') == attrs['target-id'])
                label = {'figure': 'متعلقہ شکل', 'example': 'متعلقہ مثال', 'table': 'متعلقہ جدول'}.get(tag(target_node), 'متعلقہ حصہ')
            self.check(''.join(link.itertext()) == ''.join(ET.fromstring('<fragment>' + label + '</fragment>').itertext()), 'link_label:' + key)
        for source_table in (node for node in self.source.iter() if tag(node) == 'table'):
            sid, table = source_table.get('id'), by_id[source_table.get('id')]
            key = sid + '/summary'
            self.check(table.get('data-source-summary') == self.translation['source_blocks'][key], 'table_source_summary:' + sid)
            self.check(table.get('aria-label') == self.translation['table_summary_overrides'][sid], 'table_aria_summary:' + sid)
            self.check(table.get('dir') == 'ltr' and table.get('data-description-origin') == 'original-correction', 'table_direction_origin:' + sid)
            source_rows = [node for node in source_table.iter() if tag(node) == 'row']
            html_rows = list(table.iter('tr'))
            self.check(len(html_rows) == len(source_rows), 'table_rows:' + sid)
            cell_keys = []
            for row_index, (source_row, html_row) in enumerate(zip(source_rows, html_rows), 1):
                self.check(len(source_row) == len(html_row), 'table_columns:' + sid + ':' + str(row_index))
                for column_index, (source_entry, cell) in enumerate(zip(source_row, html_row), 1):
                    cell_key = f'{sid}/row/{row_index}/entry/{column_index}'
                    cell_keys.append(cell_key)
                    self.check(cell.get('data-source-key') == cell_key and cell.get('dir') == 'rtl', 'table_cell_binding:' + cell_key)
                    header = cell_key in self.translation['table_header_cells']
                    self.check(tag(cell) == ('th' if header else 'td'), 'table_cell_semantics:' + cell_key)
                    self.check(cell.get('scope') == (self.translation['table_header_scopes'][cell_key] if header else None), 'table_cell_scope:' + cell_key)
                    cell_clone = copy.deepcopy(cell)
                    groups = self.expected.groups(source_entry)
                    for slot, _ in enumerate(groups['math']):
                        targets = [n for n in cell_clone.iter('span')
                                   if n.get('data-source-owner') == cell_key and
                                   n.get('data-source-slot') == str(slot)]
                        self.check(len(targets) == 1, 'table_cell_math:' + cell_key + ':' + str(slot))
                        self.replace_node(cell_clone, targets[0],
                                          ET.Element('ph', {'kind': 'math', 'index': str(slot)}))
                    expected_value = re.sub(r'\{\{math:(\d+)\}\}',
                                            r'<ph kind="math" index="\1"/>',
                                            self.translation['source_blocks'][cell_key])
                    expected_fragment = ET.fromstring('<fragment>' + expected_value + '</fragment>')
                    self.check(self.content_signature(cell_clone) ==
                               self.content_signature(expected_fragment),
                               'table_cell_content:' + cell_key)
                    for name, value in source_entry.attrib.items():
                        self.check(cell.get('data-source-' + name) == value, 'table_entry_attribute:' + cell_key + ':' + name)
            self.check(cell_keys == [self.expected.keys[node] for node in source_table.iter() if tag(node) == 'entry'], 'table_cell_order:' + sid)
            parents = {child: node for node in document.iter() for child in node}
            wrapper = parents[parents[table]]
            self.check(wrapper.get('data-source-child') == sid and parents[table].get('dir') == 'ltr', 'table_scroll_wrapper:' + sid)
        sales = by_id['Table_01_03_03']
        sales_rows = list(sales.iter('tr'))
        self.check('2004→243' in self.translation['bridge_after_html'] and ''.join(sales_rows[7][1].itertext()) == '249', 'table_false_summary_actual_cell')
        self.validate_assets(document)
        self.validate_math(document)
        self.validate_blocks(document)
        source_section = by_id['source-translation']
        allowed = {'h1', 'h2', 'h3', 'h4', 'h5', 'p', 'div', 'section', 'article', 'aside', 'figure', 'figcaption', 'ol', 'ul', 'li', 'span', 'sup', 'a', 'bdi', 'em', 'strong', 'dt', 'dd', 'dl', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'colgroup', 'col', 'img', 'br'}
        self.check(all(tag(n) in allowed or n.tag.startswith('{' + MATH + '}') for n in source_section.iter()), 'source_container_node_kinds')
        self.check(source_section.attrib == {'id': 'source-translation'} and (source_section.text or '') == '' and (source_section.tail or '') == '', 'source_section_frame')
        html_counts = Counter(tag(n) for n in source_section.iter() if not n.tag.startswith('{' + MATH + '}'))
        expected_counts = Counter({'section': 64, 'h1': 1, 'div': 141, 'p': 200, 'bdi': 144,
            'h2': 16, 'ul': 4, 'li': 28, 'a': 91, 'sup': 1, 'table': 5,
            'colgroup': 5, 'col': 20, 'tbody': 5, 'tr': 25, 'th': 9, 'strong': 11,
            'span': 270, 'td': 69, 'em': 13, 'aside': 14, 'h3': 24, 'ol': 2,
            'article': 61, 'h4': 61, 'h5': 38, 'figure': 19, 'figcaption': 2,
            'dt': 9, 'dd': 9, 'dl': 1, 'img': 24, 'br': 1})
        self.check(html_counts == expected_counts and len(list(source_section.iter())) == 4066, 'complete_source_element_inventory')
        self.check(not any(n.get('hidden') is not None or n.get('aria-hidden') == 'true' or 'display:none' in n.get('style', '').replace(' ', '') for n in source_section.iter()), 'source_content_visible')

        source_text = ''.join(source_section.itertext())
        self.check(all(token not in source_text for token in ('x₂≠x₁', 'a≠0', 'a≠5', '2004→243')), 'original_notes_outside_source')
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
            node = first_keyed(root, 'fs-id1165135194500')
            node.text = 'CONTRADICTORY 999'
        def change_emphasis(root):
            next(root.iter('strong')).tag = 'em'
        def change_link_label(root):
            link = next(n for n in root.iter('a') if n.get('data-source-link'))
            link.text = 'غلط حوالہ'
            for child in list(link):
                link.remove(child)
        def swap_table_rows(root):
            table = by_id(root, 'Table_01_03_03')
            tbody = next(table.iter('tbody'))
            tbody[0], tbody[1] = tbody[1], tbody[0]
        def change_footnote_tail(root):
            body = by_id(root, 'fs-id1165137642606-text')
            body[-1].tail = ' CONTRADICTORY 999'
        def move_solution(root):
            solution = by_id(root, 'fs-id1165137593409')
            parents = {c: n for n in root.iter() for c in n}
            parents[solution].remove(solution)
            by_id(root, 'source-translation').append(solution)
        def swap_wrapper_tags(root):
            by_id(root, 'fs-id1165135485962').tag = 'section'
            by_id(root, 'fs-id1165137593409').tag = 'div'
        def mutate_part_a_phrase(key, old, new):
            part_a = json.loads(self.raw['translation_part_a'], object_pairs_hook=unique_object)
            part_a['source_blocks'][key] = part_a['source_blocks'][key].replace(old, new)
            self.raw['translation_part_a'] = json.dumps(part_a, ensure_ascii=False).encode('utf-8')
            self.translation['source_blocks'][key] = self.translation['source_blocks'][key].replace(old, new)
        def change_page_terminology():
            shell = json.loads(self.raw['translation_shell'], object_pairs_hook=unique_object)
            shell['title'] = self.translation['title'] = 'تبدیلی دیاں شرحاں تے گرافاں دا رویہ'
            shell['subtitle'] = self.translation['subtitle'] = 'اوسط تبدیلی، ودھدے گھٹدے وقفے تے مقامی/مطلق انتہائیں'
            self.raw['translation_shell'] = json.dumps(shell, ensure_ascii=False).encode('utf-8')
        def change_external_label_terminology():
            key = 'fs-id1165135708041/item/1/link/0'
            shell = json.loads(self.raw['translation_shell'], object_pairs_hook=unique_object)
            shell['source_link_labels'][key] = self.translation['source_link_labels'][key] = 'اوسط تبدیلی دی شرح'
            self.raw['translation_shell'] = json.dumps(shell, ensure_ascii=False).encode('utf-8')
        def restore_raw_english_alt():
            sid = 'fs-id1165137888935'
            shell = json.loads(self.raw['translation_shell'], object_pairs_hook=unique_object)
            changed = shell['image_alt_overrides'][sid].replace('اُلٹ قدر', 'reciprocal')
            shell['image_alt_overrides'][sid] = self.translation['image_alt_overrides'][sid] = changed
            self.raw['translation_shell'] = json.dumps(shell, ensure_ascii=False).encode('utf-8')
        def unwrap_bridge_rational():
            shell = json.loads(self.raw['translation_shell'], object_pairs_hook=unique_object)
            old = '<bdi dir="ltr" lang="en">rational</bdi>'
            shell['bridge_after_html'] = shell['bridge_after_html'].replace(old, 'rational')
            self.translation['bridge_after_html'] = self.translation['bridge_after_html'].replace(old, 'rational')
            self.raw['translation_shell'] = json.dumps(shell, ensure_ascii=False).encode('utf-8')
        self.mutation('changed_math_number', lambda d: setattr(next(n for n in d.iter('{' + MATH + '}mn')), 'text', '999'))
        self.mutation('math_text_edit_ledger_injected', lambda d: next(n for n in d.iter('{' + MATH + '}math')).set('data-source-text-edits', '[]'))
        self.mutation('changed_asset_src', lambda d: by_id(d, 'fs-id1165137838377').set('src', '../assets/fake.jpg'))
        self.mutation('changed_source_alt', lambda d: by_id(d, 'fs-id1165137459600').set('data-source-alt', 'x>=999'))
        self.mutation('changed_accessible_alt', lambda d: by_id(d, 'fs-id1165134080979').set('alt', 'wrong reciprocal claim'))
        self.mutation('hidden_source_image', lambda d: by_id(d, 'fs-id1165137838377').set('hidden', 'hidden'))
        self.mutation('removed_source_id', lambda d: by_id(d, 'fs-id1165137645483').attrib.pop('id'))
        self.mutation('changed_external_link', lambda d: next(n for n in d.iter('a') if n.get('data-source-link') == 'fs-id1165135708041/item/1/link/0').set('href', 'https://example.invalid'))
        self.mutation('changed_source_link_label', change_link_label)
        self.mutation('changed_translated_prose_and_number', change_prose)
        self.mutation('changed_source_emphasis_effect', change_emphasis)
        self.mutation('removed_precision_note', lambda d: by_id(d, 'behavior-rate-domain').attrib.pop('id'))
        self.mutation('bridge_english_lang_removed', lambda d: next(
            n for n in by_id(d, 'behavior-bridge').iter('bdi')
            if ''.join(n.itertext()) == 'rational').attrib.pop('lang'))
        self.mutation('table_summary_bdi_replaced', lambda d: setattr(
            next(by_id(d, 'behavior-table-summary').iter('bdi')), 'tag', 'span'))
        self.mutation('table_header_demoted', lambda d: setattr(next(by_id(d, 'Table_01_03_03').iter('th')), 'tag', 'td'))
        self.mutation('table_rows_swapped', swap_table_rows)
        self.mutation('table_actual_249_changed', lambda d: setattr(list(by_id(d, 'Table_01_03_03').iter('tr'))[7][1], 'text', '243'))
        self.mutation('table_false_summary_corrected_silently', lambda d: by_id(d, 'Table_01_03_03').set('data-source-summary', '2004=249'))
        self.mutation('footnote_backlink_tail_injection', change_footnote_tail)
        self.mutation('source_solution_reparented', move_solution)
        self.mutation('source_wrapper_types_swapped', swap_wrapper_tags)
        self.mutation('source_list_type_changed', lambda d: by_id(d, 'list-00001').set('data-source-list-type', 'bulleted'))
        self.mutation('source_structural_tail_injection', lambda d: setattr(by_id(d, 'fs-id1165137645483'), 'tail', ' CONTRADICTORY 999'))
        self.mutation('extra_source_paragraph', lambda d: by_id(d, 'source-translation').append(ET.Element('p', {'dir': 'ltr'})))
        self.mutation('hidden_source_section', lambda d: by_id(d, 'source-translation').set('hidden', 'hidden'))
        self.mutation('source_newline_removed', lambda d: setattr(next(d.iter('br')), 'tag', 'span'))
        self.mutation('glossary_location_changed_to_value', lambda d: setattr(first_keyed(d, 'fs-id1165135412035'), 'text', 'CONTRADICTORY function value'))
        self.input_mutation('manifest_source_image_path_changed',
                            lambda: self.manifest['images'][0].__setitem__('source_path', 'media/fake.jpg'), self.validate_source)
        self.input_mutation('manifest_source_links_reordered',
                            lambda: self.manifest['source_links'].__setitem__(slice(0, 2), list(reversed(self.manifest['source_links'][:2]))), self.validate_source)
        self.input_mutation('manifest_missing_solution_claim_changed',
                            lambda: self.manifest['section_exercises_without_solutions'].__setitem__(0, self.manifest['section_exercise_ids'][0]), self.validate_source)
        self.input_mutation('translation_table_semantics_reversed',
                            lambda: self.translation['table_header_scopes'].__setitem__('Table_01_03_03/row/1/entry/1', 'row'), self.validate_translation)
        self.input_mutation('translated_prose_number_changed',
                            lambda: self.translation['source_blocks'].__setitem__('Table_01_03_03/row/8/entry/2', '243'), self.validate_translation)
        self.input_mutation('source_summary_silently_corrected',
                            lambda: self.translation['source_blocks'].__setitem__('Table_01_03_03/summary', self.translation['source_blocks']['Table_01_03_03/summary'].replace('2004, 243', '2004, 249')), self.validate_translation)
        self.input_mutation('newline_placeholder_removed',
                            lambda: self.translation['source_blocks'].__setitem__('fs-id1165137418913', self.translation['source_blocks']['fs-id1165137418913'].replace('{{break:0}}', '')), self.validate_translation)
        self.input_mutation('plural_verb_split',
                            lambda: self.translation['source_blocks'].__setitem__('fs-id1165137784644', self.translation['source_blocks']['fs-id1165137784644'].replace('فنکشن کیویں بدلدے نیں', 'فنکشن کیویں بدل دے نیں')), self.validate_translation)
        self.input_mutation('punjabi_connector_replaced_by_urdu_form',
                            lambda: mutate_part_a_phrase('fs-id1165137784644', 'ایس طرح', 'ایسے طرح'),
                            self.validate_translation)
        self.input_mutation('punjabi_plural_modifier_replaced_by_singular',
                            lambda: mutate_part_a_phrase('fs-id1165134272749', 'ایسیاں قدراں', 'ایسی قدراں'),
                            self.validate_translation)
        self.input_mutation('punjabi_indefinite_replaced_by_aisa',
                            lambda: self.translation['source_blocks'].__setitem__('fs-id1165134378691', self.translation['source_blocks']['fs-id1165134378691'].replace('ایہو جیہا عدد', 'ایسا عدد')), self.validate_translation)
        self.input_mutation('fuel_action_collapsed_to_piya',
                            lambda: self.translation['source_blocks'].__setitem__('fs-id1165135387238', self.translation['source_blocks']['fs-id1165135387238'].replace('اوہنے <bdi dir="ltr">10.7</bdi> گیلن پیٹرول بھریا سی', '<bdi dir="ltr">10.7</bdi> گیلن پیٹرول پیا اے')), self.validate_translation)
        self.input_mutation('key_concepts_singular',
                            lambda: self.translation['source_blocks'].__setitem__('fs-id1165135481945/title', 'اہم خیال'), self.validate_translation)
        self.input_mutation('velocity_collapsed_to_speed',
                            lambda: self.translation['source_blocks'].__setitem__('fs-id1165135387257', self.translation['source_blocks']['fs-id1165135387257'].replace('اوسط رخ والی رفتار', 'اوسط رفتار')), self.validate_translation)
        self.input_mutation('page_terminology_reverted_to_urdu_register', change_page_terminology,
                            self.validate_translation)
        self.input_mutation('external_label_terminology_reverted', change_external_label_terminology,
                            self.validate_translation)
        self.input_mutation('accessible_alt_raw_english_restored', restore_raw_english_alt,
                            self.validate_translation)
        self.input_mutation('bridge_raw_english_unwrapped', unwrap_bridge_rational,
                            self.validate_translation)
        self.input_mutation('canon_receipt_gap_claim_erased',
                            lambda: self.raw.__setitem__('notes', self.raw['notes'].replace(
                                b'No contemporaneous Part A or whole-unit draft/revision canon receipt exists',
                                b'Contemporaneous receipts exist for every stage')),
                            self.validate_translation)
        def change_canon_c04_hash():
            receipt = json.loads(self.raw['canon_qa'], object_pairs_hook=unique_object)
            next(row for row in receipt['examples'] if row['id'] == 'C04')['paragraph_sha256'] = '2b8bfffa5cc5076691266281325fbff7cb2025060317571257e5a74520787bb'
            self.raw['canon_qa'] = json.dumps(receipt, ensure_ascii=False).encode('utf-8')
        self.input_mutation('qa_canon_c04_hash_regressed', change_canon_c04_hash,
                            self.validate_translation)
        def change_notice():
            notices = json.loads(self.raw['notice'], object_pairs_hook=unique_object)
            notices[0]['sha256'] = '0' * 64
            self.raw['notice'] = json.dumps(notices, ensure_ascii=False).encode('utf-8')
        self.input_mutation('component_notice_hash_changed', change_notice, lambda: self.validate_assets(self.document))

    def run(self):
        self.validate_source()
        self.validate_translation()
        self.validate_document(self.document)
        self.validate_mutations()
        if not self.check_only:
            before = self.paths['reader'].read_bytes()
            subprocess.run([sys.executable, '-B', str(BASE / 'scripts/build_behavior.py'), '--unit', '013'], cwd=ROOT, check=True, capture_output=True)
            first = self.paths['reader'].read_bytes()
            subprocess.run([sys.executable, '-B', str(BASE / 'scripts/build_behavior.py'), '--unit', '013'], cwd=ROOT, check=True, capture_output=True)
            second = self.paths['reader'].read_bytes()
            self.check(before == first == second, 'deterministic_build')
            self.raw['reader'] = second
        receipt = {
            'unit': 'PNB-013', 'status': 'source-structure-math-and-assets-passed; native-visual-educator-review-pending',
            'checks_passed': self.checks, 'detached_mutations_rejected': self.mutations,
            'mutations': self.mutation_labels,
            'reader_sha256': digest(self.paths['reader'].read_bytes()),
            'source_statistics': self.manifest['source_statistics'],
            'scope': 'Complete canonical m49306 source/key/ID/ancestry/block/number/emphasis/part-token/newline/MathML/table/link/footnote/image and supplied-solution binding; independent source expectations; no renderer expected-DOM import.',
            'limitations': ['Native Punjabi specialist and mathematics-educator review pending',
                            'Browser review is separate from source-bound automated checks',
                            'No contemporaneous Part A or whole-unit draft/revision canon receipt exists; no retroactive receipt was created',
                            'Finite image descriptions and source examples are not universal mathematical, historical, market, legal or pricing verification',
                            'Canon passages are prose usage evidence, not mathematical terminology authority or native certification',
                            'The complete five-work assignment remains active'],
            'inputs': {key: {'path': path.relative_to(BASE).as_posix(), 'sha256': digest(path.read_bytes())}
                       for key, path in self.paths.items() if key != 'reader'},
        }
        if not self.check_only:
            out = BASE / 'qa/structural-013.json'
            out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
        return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    print(json.dumps(QA(args.check_only).run(), ensure_ascii=False, sort_keys=True))
