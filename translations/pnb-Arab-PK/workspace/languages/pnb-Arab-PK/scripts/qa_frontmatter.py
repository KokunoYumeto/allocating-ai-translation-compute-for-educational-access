"""Independent source-derived PNB010/011 QA, including detached mutation regressions.

No renderer import or expected-DOM reuse. Canonical CNXML determines all node
positions, attributes, ancestry, keys, inline boundaries and numeric witnesses.
The renderer's CSS literal is read as a hashed static input, never executed.
"""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from collections import Counter
import argparse
import ast
import copy
import csv
import hashlib
import io
import json
import re
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET

from qa_notation import jpeg_dimensions, unique_object

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
CN = 'http://cnx.rice.edu/cnxml'
MD = 'http://cnx.rice.edu/mdml'
SOURCE = {
    '010': {
        'module': 'm50919', 'raw': '1483e6509bb6339890bae39b53c5bdb4b010a144558d95ae20b213ab1a06c176',
        'lf': 'f6cfb6514c8b3e8cbeff7e1e81bc3ef2db53750bc91305f167af43fb70805a69',
        'comparison': 'c27732bd5c9002733638ac561caaff778ed63de04cbdd63f10d9b0724a18c972',
        'uuid': 'b3f4423d-9598-4fec-8822-df3767e33a9a', 'nodes': 224, 'ids': 73, 'keys': 98,
        'last': 'eip-958', 'media': 'preface01', 'filename': 'CNX_Precalc_Figure_Preface_01.jpg',
        'image_sha': '66e71b8e2eab72b69cdb3a89691726f322f35202e3390dc0c94fa40cc6379494',
        'dimensions': (975, 473), 'image_bytes': 245379,
    },
    '011': {
        'module': 'm49299', 'raw': '0b05ac175b00d400bc502d4eee3d6e338da3c70ca1e031b9bdd91a51608d3687',
        'lf': '9539d32c4a802797ad1b350c8823bf105ece72bbffd64d8d006b3b3ef034e906',
        'comparison': '298829ef88555d695b1dfec2ebac14ce787a2546ce964c04c16ca5ab79a76b7b',
        'uuid': 'bc43a726-bcbf-4db7-89a0-50d97ab46818', 'nodes': 15, 'ids': 4, 'keys': 6,
        'last': 'fs-id1165137911603', 'media': 'fs-id1165137810701', 'filename': 'CNX_Precalc_Figure_01_00_001n.jpg',
        'image_sha': 'ca0b74aac78b0d531539da17c762954d38cd084c7770297216ef9b651bcc3363',
        'dimensions': (1401, 637), 'image_bytes': 268874,
    },
}
RECEIPTS = ['PNB-010-011-study-next-unit-20260831T134937995168Z.json',
            'PNB-010-011-revision-20260831T142528785915Z.json',
            'PNB-010-011-qa-20260831T142953465529Z.json']
FORBIDDEN = set('\u061c\u200e\u200f\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069\ufffd')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def tag(node):
    return node.tag.rsplit('}', 1)[-1]


def signature(node):
    return node.tag, dict(node.attrib), node.text, tuple((signature(c), c.tail) for c in node)


def html_signature(node):
    return node.tag, dict(sorted(node.attrib.items())), node.text or '', tuple((html_signature(c), c.tail or '') for c in node)


def source_positions(root):
    result = {'root': root}
    def visit(node, prefix):
        for i, child in enumerate(node):
            path = f'{prefix}/{i}' if prefix else str(i)
            result[path] = child
            visit(child, path)
    visit(root, '')
    return result


def by_id(document, sid):
    found = [n for n in document.iter() if n.get('id') == sid]
    assert len(found) == 1, 'id must occur exactly once: ' + sid
    return found[0]


def source_dom(document):
    nodes = [n for n in document.iter() if n.get('data-source-node') is not None]
    assert len(nodes) == len({n.get('data-source-node') for n in nodes}), 'duplicate source path'
    return {n.get('data-source-node'): n for n in nodes}


def fragment(value):
    return ET.fromstring('<fragment>' + value + '</fragment>')


def own_text(node):
    output = node.text or ''
    for child in node:
        if tag(child) != 'list' and child.get('data-source-tag') != 'list':
            output += own_text(child)
        output += child.tail or ''
    return output


def nearest(node, parents, predicate):
    while node in parents:
        node = parents[node]
        if predicate(node):
            return node
    return None


class QA:
    def __init__(self, unit):
        self.unit, self.spec = unit, SOURCE[unit]
        self.module = self.spec['module']
        self.checks, self.mutations = [], []
        self.manifest_path = BASE / f'source-excerpts/manifest-{unit}.json'
        self.excerpt = BASE / f'source-excerpts/unit-{unit}.cnxml'
        self.translation_path = BASE / f'translations/unit-{unit}.json'
        self.notice_path = BASE / f'provenance/unit-{unit}-component-notices.json'
        self.reader_path = BASE / f'reader/unit-{unit}.html'
        self.canonical = ROOT / f'downloads/upstream/osbooks-college-algebra-bundle/modules/{self.module}/index.cnxml'
        self.comparison = ROOT / f'downloads/extracted/A30/repo/source/modules/{self.module}/index.cnxml'
        self.rights_path = ROOT / 'downloads/extracted/A30/00_control/COMPONENT_RIGHTS.csv'
        self.original_image = ROOT / 'downloads/complete-upstream/osbooks-college-algebra-bundle/media' / self.spec['filename']
        self.manifest = json.loads(self.manifest_path.read_text(encoding='utf-8'), object_pairs_hook=unique_object)
        self.translation = json.loads(self.translation_path.read_text(encoding='utf-8'), object_pairs_hook=unique_object)
        self.notice = json.loads(self.notice_path.read_text(encoding='utf-8'), object_pairs_hook=unique_object)
        self.full = ET.parse(self.canonical).getroot()
        self.source = ET.parse(self.excerpt).getroot()
        self.positions = source_positions(self.full)
        self.paths = {n: p for p, n in self.positions.items()}
        self.parents = {c: n for n in self.full.iter() for c in n}
        self.key_nodes = {}
        for node in self.full.iter():
            name = tag(node)
            if name in ('title', 'para', 'item', 'caption', 'media') or (name == 'abstract' and (node.text or '').strip()):
                self.key_nodes[self.key(node)] = node
        self.source_ids = [n.get('id') for n in self.full.iter() if n.get('id')]
        self.image_spec = self.manifest['images'][0]
        self.asset = BASE / self.image_spec['path']
        self.rows = list(csv.DictReader(self.rights_path.open(encoding='utf-8-sig', newline='')))
        self.row = next(r for r in self.rows if r['asset_path'] == 'media/' + self.spec['filename'])
        self.receipt_paths = [BASE / 'canon/receipts' / n for n in RECEIPTS]
        self.receipt_paths += [BASE / 'canon/receipts' / ('PNB-010-draft-20260831T140647843606Z.json' if unit == '010' else 'PNB-011-draft-20260831T142335459763Z.json')]
        self.input_paths = [self.manifest_path, self.excerpt, self.translation_path, self.notice_path,
                            BASE / f'qa/unit-{unit}-language-notes.md', self.canonical, self.comparison,
                            self.rights_path, self.original_image, BASE / 'styles/reader.css', BASE / 'terminology.tsv',
                            BASE / 'provenance/ATTRIBUTION.md', BASE / 'reader/unit-009.html',
                            BASE / 'scripts/prepare_frontmatter.py', BASE / 'scripts/build_frontmatter.py',
                            Path(__file__).resolve(), BASE / 'scripts/qa_notation.py',
                            BASE / 'canon/examples.json', *self.receipt_paths]
        if unit == '010':
            self.input_paths += [self.asset, ROOT / 'downloads/extracted/A30/repo/source/media/id-ID/CNX_Precalc_Figure_Preface_01-id.svg']

    def check(self, condition, label):
        assert condition, label
        self.checks.append(label)

    def key(self, node):
        parent, name = self.parents.get(node), tag(node)
        if name == 'title' and parent is self.full:
            return self.module + '/title'
        if name == 'title' and tag(parent) == 'metadata':
            return self.module + '/metadata/title'
        if name == 'abstract':
            return self.module + '/metadata/abstract'
        if name == 'title':
            return parent.get('id') + '/title'
        if name == 'media':
            return node.get('id') + '/alt'
        if name == 'caption':
            return parent.get('id') + '/caption'
        if name == 'item':
            return parent.get('id') + '/item/' + str(list(parent).index(node) + 1)
        return node.get('id')

    def validate_inputs(self):
        full = self.canonical.read_bytes()
        self.check(sha(full) == self.spec['raw'], 'pinned canonical raw bytes')
        full_lf = full.replace(b'\r\n', b'\n')
        self.check(sha(full_lf) == self.spec['lf'] == self.manifest['full_module_sha256'], 'pinned canonical LF bytes')
        excerpt = self.excerpt.read_bytes().replace(b'\r\n', b'\n')
        self.check(not full_lf.endswith(b'\n') and excerpt == full_lf + b'\n', 'only documented terminal LF outside XML')
        self.check(sha(excerpt) == self.manifest['excerpt_sha256'], 'excerpt digest')
        self.check(signature(self.source) == signature(self.full), 'complete exact XML including internal tails')
        self.check(sha(self.comparison.read_bytes()) == self.spec['comparison'], 'pinned Indonesian text comparison')
        m = self.manifest
        self.check(m['commit'] == '789b54099106b071d1d32bfcee454fed72eb4768', 'canonical pin unchanged')
        self.check(m['unit'] == self.translation['unit'] == 'PNB-' + self.unit and m['module'] == self.module, 'unit/module binding')
        self.check(self.translation['locale'] == 'pnb-Arab-PK', 'translation locale')
        self.check(m['path'] == f'modules/{self.module}/index.cnxml', 'canonical path')
        self.check(m['source_byte_witnesses']['canonical_checkout_path'] == self.canonical.relative_to(ROOT).as_posix(), 'canonical witness path')
        self.check(m['source_byte_witnesses']['canonical_checkout_sha256'] == self.spec['raw'], 'canonical witness digest field')
        self.check(m['source_byte_witnesses']['comparison_path'] == self.comparison.relative_to(ROOT).as_posix(), 'comparison witness path')
        self.check(m['source_byte_witnesses']['comparison_sha256'] == self.spec['comparison'], 'comparison witness digest field')
        self.check([tag(n) for n in self.full] == ['title', 'metadata', 'content'], 'complete root order')
        self.check(len(self.positions) == self.spec['nodes'], 'complete source element count')
        self.check(len(self.source_ids) == self.spec['ids'] and self.source_ids[-1] == self.spec['last'], 'complete source ID inventory/boundary')
        self.check(m['source_ids'] == self.source_ids, 'manifest ordered IDs')
        self.check(list(self.key_nodes) == m['source_block_keys'] == list(self.translation['source_blocks']), 'exact ordered source-derived key set')
        self.check(len(self.key_nodes) == self.spec['keys'], 'complete translation count')
        self.check(m['selection_ids'] == [n.get('id') for n in self.full.find('{' + CN + '}content')], 'all content children included')
        self.check(m['next_source_id'] is None and m['next_module'] == ('m49299' if self.unit == '010' else 'm49301'), 'whole-module end cursor')
        self.check(self.full.attrib == {'class': 'preface' if self.unit == '010' else 'introduction'}, 'source document class')
        self.check(m['module_metadata']['root_attributes'] == self.full.attrib, 'metadata root attributes')
        self.check(m['module_metadata']['content_id'] == self.module and m['module_metadata']['uuid'] == self.spec['uuid'], 'metadata identity')
        source_counts = Counter(tag(n) for n in self.full.iter())
        expected_counts = {'translation_blocks': len(self.key_nodes), 'non_document_elements': len(self.positions) - 1,
                           'identified_nodes': len(self.source_ids), 'sections': source_counts['section'], 'paragraphs': source_counts['para'],
                           'lists': source_counts['list'], 'list_items': source_counts['item'],
                           'child_placeholders': sum(tag(n) == 'para' and any(tag(c) == 'list' for c in n) for n in self.full.iter()),
                           'newlines': source_counts['newline'], 'emphasis': source_counts['emphasis'], 'mathml_trees': source_counts['math'],
                           'tables': source_counts['table'], 'links': source_counts['link'], 'images': source_counts['image'],
                           'figure_wrappers': source_counts['figure'], 'footnotes': source_counts['footnote']}
        self.check(m['source_statistics'] == expected_counts, 'all source statistics independently counted')
        self.check(not any(source_counts[n] for n in ('math', 'table', 'footnote', 'exercise', 'solution')), 'no invented source math/table/exercises')
        for p in self.receipt_paths:
            receipt = json.loads(p.read_text(encoding='utf-8'), object_pairs_hook=unique_object)
            self.check(bool(receipt), 'actual-read receipt exists:' + p.name)
        self.validate_component()

    def validate_component(self):
        s, row, data = self.image_spec, self.row, self.original_image.read_bytes()
        media = next(n for n in self.full.iter() if tag(n) == 'media')
        self.check(len(self.manifest['images']) == 1 and len(media) == 1 and tag(media[0]) == 'image', 'single actual source image')
        self.check(s['media_id'] == media.get('id') == self.spec['media'], 'source media identity')
        self.check(s['source_path'] == 'media/' + self.spec['filename'] and media[0].get('src') == '../../' + s['source_path'], 'source image path binding')
        self.check(s['path'] == f'assets/unit-{self.unit}-{self.spec["media"]}.jpg', 'exact own safe destination')
        self.check(s['sha256'] == sha(data) == self.spec['image_sha'], 'canonical JPEG bytes')
        self.check((s['width'], s['height']) == jpeg_dimensions(data) == self.spec['dimensions'], 'JPEG actual dimensions')
        self.check(type(s['width']) is type(s['height']) is type(s['bytes']) is int, 'image dimensions/bytes integer types')
        self.check(s['bytes'] == len(data) == self.spec['image_bytes'] == int(row['bytes']), 'JPEG byte count')
        self.check(s['source_mime_type'] == media[0].get('mime-type'), 'original MIME retained')
        self.check(row['sha256'] == s['sha256'] and row['source_modules'] == self.module, 'existing component image/module binding')
        self.check(self.notice == [row], 'whole exact existing component record retained')
        self.check(s['component_rights_id'] == row['rights_component_id'], 'component record identity')
        expected = ('admitted-unchanged', 'admitted', 'CC-BY-NC-SA-4.0', 'WORK_DEFAULT_UNCREDITED_ART') if self.unit == '010' else ('quarantined-not-copied', 'quarantined', 'NOASSERTION', 'STRICT_RISK_UNKNOWN')
        self.check((s['publication_status'], row['admission'], row['license_id'], row['classification']) == expected, 'independent admission gate')
        if self.unit == '010':
            self.check('figure_id' not in s and tag(self.parents[media]) == 'section', 'direct source media has no invented figure')
            self.check(self.asset.is_file() and self.asset.read_bytes() == data, 'admitted local JPEG unchanged')
            self.check(row['attribution'] == 'Copyright Rice University, OpenStax, under CC BY-NC-SA 4.0.', 'exact admitted default art credit')
            svg = ROOT / s['comparison_asset']['path']
            self.check(sha(svg.read_bytes()) == s['comparison_asset']['sha256'] == '06d10b7af41416d83e87fc7614508c2bd088e33addd699fc58ad703fcf111693', 'different Indonesian SVG witness')
        else:
            self.check(s['figure_id'] == self.parents[media].get('id') == 'Figure_01_00_001', 'original unnumbered figure ID')
            self.check(not self.asset.exists(), 'quarantined JPEG absent from own publishable assets')
            self.check(row['attribution'] == 'credit "bull": modification of work by Prayitno Hadinata; credit "graph": modification of work by MeasuringWorth', 'named quarantined component credits unchanged')
            self.check(not (ROOT / s['comparison_asset']['path']).exists(), 'comparison JPEG explicitly unavailable, not compared')

    def expected_tag(self, node):
        name = tag(node)
        if name == 'emphasis':
            return 'em' if node.get('effect') == 'italics' else 'strong'
        if name == 'image':
            return 'img' if self.unit == '010' else 'div'
        if name == 'abstract':
            return 'p' if (node.text or '').strip() else 'span'
        if name == 'title':
            if self.parents[node] is self.full:
                return 'h2'
            ancestors, cursor = [], self.parents[node]
            while cursor is not self.full:
                ancestors.append(cursor)
                cursor = self.parents[cursor]
            return 'h' + str(min(6, max(3, 1 + sum(tag(n) == 'section' for n in ancestors))))
        if name == 'para':
            return 'div' if any(tag(c) == 'list' for c in node) else 'p'
        return {'document': 'div', 'metadata': 'div', 'content': 'div', 'section': 'section',
                'list': 'ol' if node.get('list-type') == 'enumerated' else 'ul', 'figure': 'figure',
                'media': 'div', 'item': 'li', 'caption': 'figcaption', 'content-id': 'p',
                'uuid': 'p', 'newline': 'br', 'label': 'span', 'link': 'a'}[name]

    def validate_structure(self, document):
        mapped = source_dom(document)
        self.check(list(mapped) == list(self.positions), 'every source node once in complete source order')
        ids = [n.get('id') for n in document.iter() if n.get('id')]
        self.check(len(ids) == len(set(ids)), 'all DOM IDs unique')
        self.check([s for s in ids if s in self.source_ids] == self.source_ids, 'source ID order')
        parents = {c: n for n in document.iter() for c in n}
        for path, source in self.positions.items():
            actual, name = mapped[path], tag(source)
            self.check(actual.tag == self.expected_tag(source), 'source semantic wrapper:' + path)
            exact_attrs = {'data-source-node': path, 'data-source-tag': name,
                           'data-source-namespace': source.tag[1:].split('}', 1)[0]}
            exact_attrs.update({'data-source-' + k: self.translation['source_blocks'][self.key(source)] if k == 'alt' else v
                                for k,v in source.attrib.items() if k != 'id'})
            if source.get('id'):
                exact_attrs['id'] = source.get('id')
            if name in ('document', 'metadata', 'content', 'section', 'list', 'figure', 'media'):
                exact_attrs['class'] = 'source-' + name
            if name == 'document':
                exact_attrs['id'] = 'source-document'
            if name in ('title', 'para', 'item', 'caption') or (name == 'abstract' and (source.text or '').strip()):
                exact_attrs['data-source-key'] = self.key(source)
            if name == 'para' and any(tag(c) == 'list' for c in source):
                exact_attrs['class'] = 'source-para'
            if name in ('content-id', 'uuid'):
                exact_attrs.update({'class': 'metadata-value', 'dir': 'ltr'})
            if name == 'label' or (name == 'abstract' and not (source.text or '').strip()):
                exact_attrs.update({'class': 'source-empty-label' if name == 'label' else 'source-empty-abstract', 'data-source-empty': 'true'})
            if name == 'link':
                exact_attrs.update({'href': '#' + source.get('target-id'), 'data-source-link': self.key(self.parents[source]) + '/link/0'})
            if name == 'media':
                exact_attrs['data-component-status'] = self.image_spec['publication_status']
            if name == 'image':
                if self.unit == '010':
                    exact_attrs.update({'src': '../' + self.image_spec['path'],
                                        'alt': self.translation['source_blocks'][self.key(self.parents[source])],
                                        'data-source-key': self.key(self.parents[source]), 'width': '975', 'height': '473',
                                        'style': '--source-width:975px',
                                        'aria-describedby': 'preface-diagram-description preface-reflection-correction'})
                else:
                    exact_attrs.update({'class': 'source-image-unavailable', 'data-source-sha256': self.spec['image_sha'],
                                        'data-source-width': '1401', 'data-source-height': '637', 'data-asset-coverage': 'incomplete'})
            self.check(actual.attrib == exact_attrs, 'exact source wrapper attributes/no hidden style:' + path)
            self.check(actual.get('data-source-tag') == name and actual.get('data-source-namespace') == source.tag[1:].split('}', 1)[0], 'source tag/namespace:' + path)
            expected_id = source.get('id') if source is not self.full else 'source-document'
            self.check(actual.get('id') == expected_id, 'source ID position:' + path)
            for key, value in source.attrib.items():
                if key == 'id':
                    continue
                expected = self.translation['source_blocks'][self.key(source)] if key == 'alt' else value
                self.check(actual.get('data-source-' + key) == expected, 'source attribute:' + path + ':' + key)
            ancestor = nearest(actual, parents, lambda n: n.get('data-source-node') is not None)
            expected_parent = self.paths.get(self.parents.get(source))
            self.check((ancestor.get('data-source-node') if ancestor is not None else None) == expected_parent, 'source ancestry:' + path)
            if name in ('document', 'metadata', 'content', 'section', 'list', 'figure'):
                self.check(list(actual) == [mapped[self.paths[c]] for c in source], 'complete structural children:' + path)
                self.check(not (actual.text or '').strip() and all(not (c.tail or '').strip() for c in actual), 'no structural prose/tail injection:' + path)
            if name in ('content-id', 'uuid'):
                self.check(len(actual) == 1 and actual[0].tag == 'bdi' and actual[0].attrib == {'dir': 'ltr', 'lang': 'en'}, 'metadata field shape:' + path)
                self.check(not actual.text and not actual[0].tail and actual[0].text == source.text and not len(actual[0]), 'exact metadata value:' + path)
                self.check(actual.get('dir') == 'ltr', 'metadata LTR:' + path)
            if name == 'newline' or name == 'label' or (name == 'abstract' and not (source.text or '').strip()):
                self.check(not len(actual) and not actual.text, 'empty source element remains empty:' + path)
        self.check(not any(tag(n) == 'math' for n in document.iter()), 'no invented MathML')
        self.validate_blocks(document)

    def validate_blocks(self, document):
        mapped = source_dom(document)
        keyed = [n for n in document.iter() if n.get('data-source-key') is not None]
        self.check([n.get('data-source-key') for n in keyed] == list(self.key_nodes), 'source prose/alt keys exactly once in order')
        for actual in keyed:
            key = actual.get('data-source-key')
            source = self.key_nodes[key]
            value = self.translation['source_blocks'][key]
            if tag(source) == 'media':
                expected_owner = mapped[self.paths[source[0]]] if self.unit == '010' else mapped[self.paths[source]][-1]
                self.check(actual is expected_owner, 'source alt ownership:' + key)
                self.check(actual.get('alt') == value if self.unit == '010' else own_text(actual) == value, 'faithful source alt:' + key)
                continue
            self.check(actual is mapped[self.paths[source]], 'source block exact owner:' + key)
            clone = copy.deepcopy(actual)
            clone.tag, clone.attrib, clone.tail = 'fragment', {}, None
            children = [c for c in source if tag(c) == 'list']
            links = [c for c in source.iter() if tag(c) == 'link']
            for kind, originals in [('child', children), ('link', links)]:
                tokens = re.findall(r'\{\{' + kind + r':(\d+)\}\}', value)
                self.check(tokens == [str(i) for i in range(len(originals))], 'source placeholders:' + key + ':' + kind)
                for index, original in enumerate(originals):
                    matches = [n for n in clone.iter() if n.get('data-source-node') == self.paths[original]]
                    self.check(len(matches) == 1, 'rendered child/link slot:' + key + ':' + kind + ':' + str(index))
                    slot = matches[0]
                    tail = slot.tail
                    slot.clear()
                    slot.tag, slot.attrib, slot.tail = 'slot', {'kind': kind, 'index': str(index)}, tail
            for n in clone.iter():
                for attribute in list(n.attrib):
                    if attribute.startswith('data-source-'):
                        del n.attrib[attribute]
            expected = re.sub(r'\{\{(child|link):(\d+)\}\}', lambda m: '<slot kind="' + m[1] + '" index="' + m[2] + '" />', value)
            self.check(html_signature(clone) == html_signature(fragment(expected)), 'exact translated inline text/tails/markup:' + key)
            allowed = {'fragment', 'bdi', 'em', 'strong', 'br', 'slot'}
            self.check(all(n.tag in allowed for n in fragment(expected).iter()), 'restricted translation inline vocabulary:' + key)
            for n in fragment(expected).iter('bdi'):
                self.check(n.get('dir') == 'ltr' and set(n.attrib) <= {'dir', 'lang'}, 'isolated numeric/proper-name literal:' + key)

    def validate_values(self, document):
        mapped = source_dom(document)
        number = r'\d+(?:[.,-]\d+)*(?:st|nd|rd|th)?'
        for key, source in self.key_nodes.items():
            if tag(source) == 'media':
                continue
            original, actual = own_text(source), own_text(mapped[self.paths[source]])
            old, new = re.findall(number, original), re.findall(number, actual)
            if key == 'para-00004':
                self.check(old == ['2nd'] and not new and 'دوجے ایڈیشن' in actual, 'explicit second-edition ordinal localization')
            else:
                self.check(Counter(old) == Counter(new), 'source numeric tokens/decimal/range punctuation:' + key)
        if self.unit == '010':
            for sid, expected_lines in [('eip-777', 9), ('eip-958', 46)]:
                source = next(n for n in self.full.iter() if n.get('id') == sid)
                original = [(source.text or '').strip()] + [(c.tail or '').strip() for c in source]
                actual = by_id(document, sid)
                names = [n.text for n in actual.iter('bdi')]
                self.check(names == [n for n in original if n] and len(names) == expected_lines, 'every exact name/affiliation in order:' + sid)
                self.check(len(list(actual.iter('br'))) == len(source), 'all actual credit breaks including terminal:' + sid)
                self.check(all(n.get('dir') == 'ltr' and n.get('lang') == 'en' for n in actual.iter('bdi')), 'credit names English LTR:' + sid)
            self.check(len(list(by_id(document, 'eip-958'))[-1]) == 0 and list(by_id(document, 'eip-958'))[-1].tag == 'br', 'reviewer terminal break retained')
            source_strong = next(n for n in self.full.iter() if tag(n) == 'emphasis' and n.text == 'Jay Abramson, Arizona State University')
            actual = mapped[self.paths[source_strong]]
            self.check(actual.tag == 'strong' and own_text(actual) == source_strong.text, 'exact senior-author credit and source bold')
            self.check('Copyright Rice University, OpenStax, under CC BY-NC-SA 4.0 license.' in own_text(by_id(document, 'para-00001')), 'verbatim source fallback credit')
            self.check(sum(n.tag == 'br' for n in mapped.values()) == 55, '55 source newlines')
            self.check(sum(n.tag == 'em' for n in mapped.values()) == 11 and sum(n.tag == 'strong' for n in mapped.values()) == 17, 'all italic/default-bold/explicit-bold source styles')
        else:
            text = own_text(by_id(document, 'fs-id1165137768418'))
            self.check(re.findall(r'\$[\d,]+', text) == ['$100', '$500', '$1,100'], 'source dollars and thousands separator')
            self.check(re.findall(r'\b(?:1995|2000)\b', text) == ['1995', '2000', '2000'], 'historical dates source order')
            self.check(2000 - 1995 == 5 and 'پنج سال' in text, 'source five-year interval, not a new forecast')
            caption = next(n for n in document.iter() if n.get('data-source-key') == 'Figure_01_00_001/caption')
            self.check([n.text for n in caption.iter('bdi')] == ['Standard and Poor’s', '"bull"', 'Prayitno Hadinata', '"graph"', 'MeasuringWorth'], 'all caption credit names/roles exact')

    def validate_links(self, document):
        mapped = source_dom(document)
        actual_source_links = [n for n in document.iter() if n.get('data-source-link') is not None]
        source_links = [n for n in self.full.iter() if tag(n) == 'link']
        self.check(len(actual_source_links) == len(source_links) == (1 if self.unit == '010' else 0), 'exact actual source link count')
        expected_label_keys = []
        for original, actual in zip(source_links, actual_source_links):
            owner = self.parents[original]
            key = self.key(owner) + '/link/0'
            expected_label_keys.append(key)
            self.check(actual is mapped[self.paths[original]], 'source link exact owner/order')
            self.check(actual.get('href') == '#' + original.get('target-id') and actual.get('data-source-link') == key, 'source link target and keyed label')
            self.check(not len(actual) and actual.text == self.translation['source_link_labels'][key], 'source link translated label without extra content')
        self.check(list(self.translation['source_link_labels']) == expected_label_keys, 'no unused/invented source link labels')
        if self.unit == '010':
            self.check(self.manifest['references'] == [{'id': 'fs-id1166812582991', 'kind': 'section', 'href': '#fs-id1166812582991', 'unit': 'PNB-010', 'label_key': 'eip-id1170058262242/link/0'}], 'manifest source reference exact')
        else:
            self.check(self.manifest['references'] == [], 'no invented source references')
        ids = {n.get('id') for n in document.iter() if n.get('id')}
        for node in document.iter():
            for attribute in ('href', 'src'):
                value = node.get(attribute)
                if value is None:
                    continue
                address = urlsplit(value)
                self.check(not address.netloc or address.scheme == 'https', 'safe URL scheme:' + value)
                if address.scheme:
                    self.check(address.scheme == 'https', 'HTTPS external URL:' + value)
                    continue
                if address.path:
                    path = (self.reader_path.parent / unquote(address.path)).resolve()
                    self.check(path.is_relative_to(BASE.resolve()) and path.is_file(), 'local reference exists within language tree:' + value)
                    if address.fragment:
                        target = ET.fromstring('<html' + path.read_text(encoding='utf-8').split('<html', 1)[1])
                        self.check(address.fragment in {n.get('id') for n in target.iter()}, 'cross-reader target:' + value)
                else:
                    self.check(address.fragment in ids, 'local fragment target:' + value)

    def validate_media(self, document):
        mapped = source_dom(document)
        original = next(n for n in self.full.iter() if tag(n) == 'media')
        media, picture = mapped[self.paths[original]], mapped[self.paths[original[0]]]
        alt = self.translation['source_blocks'][self.key(original)]
        self.check(media.get('data-source-alt') == alt and media.get('data-component-status') == self.image_spec['publication_status'], 'media faithful alt and publication status')
        if self.unit == '010':
            self.check([n.tag for n in media] == ['div', 'p', 'p'] and not media.text and all(not n.tail for n in media), 'exact admitted media topology/tails')
            scroll = media[0]
            self.check(scroll.attrib == {'class': 'figure-scroll', 'dir': 'ltr', 'tabindex': '0', 'role': 'region', 'aria-label': 'اصل تصویر؛ تِن حصے ویکھن لئی پاسے سرکاؤ'}, 'focusable LTR image scroll wrapper')
            self.check(list(scroll) == [picture] and not scroll.text and not picture.tail, 'image-only scroll child')
            self.check(picture.get('src') == '../' + self.image_spec['path'] and picture.get('alt') == alt, 'unaltered image path and faithful alt')
            self.check((picture.get('width'), picture.get('height')) == tuple(map(str, self.spec['dimensions'])), 'display source natural dimensions')
            self.check(picture.get('style') == '--source-width:975px', 'natural width retained for scrolling')
            self.check(picture.get('aria-describedby') == 'preface-diagram-description preface-reflection-correction', 'accessible original description/correction targets')
            expected_hint = fragment('<p class="scroll-hint">پوری اصل تصویر دے تِن حصے ویکھن لئی پاسے سرکاؤ، یا <a href="../' + self.image_spec['path'] + '">اصل تصویر وکھری کھولو</a>۔</p>')[0]
            expected_advice = fragment('<p class="scroll-hint source-alt-advisory"><a href="#preface-diagram-description">ساڈی اصل تصویری وضاحت</a> تے <a href="#preface-reflection-correction">غلط چھپے نشان دی وکھری درستی</a> ویکھو۔</p>')[0]
            self.check(html_signature(media[1]) == html_signature(expected_hint), 'exact image scroll hint')
            self.check(html_signature(media[2]) == html_signature(expected_advice), 'visible image original-note links')
            self.check(len(list(document.iter('img'))) == 1, 'one admitted image only')
        else:
            self.check([n.tag for n in media] == ['div', 'p'] and not media.text and all(not n.tail for n in media), 'exact unavailable media topology/tails')
            self.check(media[0] is picture and [n.tag for n in picture] == ['aside', 'p'] and not picture.text and all(not n.tail for n in picture), 'quarantine source-image slot shape')
            self.check(picture.get('data-asset-coverage') == 'incomplete' and picture.get('data-source-sha256') == self.spec['image_sha'], 'quarantine hash/coverage displayed metadata')
            self.check((picture.get('data-source-width'), picture.get('data-source-height')) == ('1401', '637'), 'quarantine dimensions reference only')
            expected = fragment(self.translation['asset_unavailable_html'])[0]
            self.check(html_signature(picture[0]) == html_signature(expected), 'explicit exact original unavailable notice')
            self.check(picture[0].get('data-origin') == 'original-rights-notice', 'rights placeholder not mislabeled source prose')
            reference = 'Source reference only: ' + self.image_spec['source_path'] + '; SHA-256 ' + self.spec['image_sha'] + '; 1401×637. Not included.'
            self.check(own_text(picture[1]) == reference and picture[1].attrib == {'class': 'component-reference', 'dir': 'ltr', 'lang': 'en'}, 'exact non-loading source image reference')
            self.check(media[1].attrib == {'class': 'source-alt-text', 'data-source-key': self.key(original)} and media[1].text == alt and not len(media[1]), 'quarantine faithful alt remains readable')
            self.check(not list(document.iter('img')) and not self.asset.exists(), 'quarantined image neither rendered nor copied')
            for n in document.iter():
                self.check(not any(n.get(k) and (self.spec['filename'] in n.get(k) or self.spec['image_sha'] in n.get(k) or 'unit-011-fs-id1165137810701.jpg' in n.get(k)) for k in ('href', 'src', 'srcset', 'poster', 'data', 'style')), 'no hidden quarantine asset request')

    def validate_original(self, document):
        prefix = 'preface' if self.unit == '010' else 'introduction'
        for field, sid in [('bridge_before_html', prefix + '-source-context'), ('bridge_after_html', prefix + '-bridge')]:
            self.check(html_signature(by_id(document, sid)) == html_signature(fragment(self.translation[field])[0]), 'exact separated original content:' + field)
        self.validate_graph_bindings(document)

    def validate_graph_bindings(self, document):
        """Bindings to actually inspected, independently hash-pinned source pixels.

        These assertions do not compare with translation JSON, and finite numeric
        substitutions are explicitly not a proof of a universal function/domain.
        """
        if self.unit == '010':
            description = by_id(document, 'preface-diagram-description')
            literals = [n.text for n in description.iter('bdi')]
            self.check(literals == ['y=x²+4x+3', '(−3,0)', '(−1,0)', '(−2,−1)', '(h,k)', '(h,k+a)', '(h,k−a)', '(h−b,k)', '(h+b,k)', '(h,k+c)', '(h,k−c)', 'f(x)=5x³+1', '(0,1)', '(1,6)', 'f⁻¹(x)=∛((x−1)/5)', '(1,0)', '(6,1)'], 'independently observed source-image formula/coordinate labels')
            for x, y in [(-3, 0), (-1, 0), (-2, -1)]:
                self.check(x*x + 4*x + 3 == y, 'parabola labeled point:' + str(x))
            self.check((-3 + -1) / 2 == -2, 'parabola symmetry axis from source roots')
            for x, y in [(0, 1), (1, 6)]:
                self.check(5*x**3 + 1 == y and (y-1)/5 == x**3, 'source cubic/inverse paired point:' + str(x))
            correction = by_id(document, 'preface-reflection-correction')
            self.check([n.text for n in correction.iter('bdi')] == ['x=1', 'y=x'], 'source erroneous printed label separated from correct reflection line')
            self.check('اصل تصویر' in own_text(correction) and 'نہیں بدلیا' in own_text(correction), 'explicit unchanged-source correction disclosure')
            self.check(nearest(correction, {c:n for n in document.iter() for c in n}, lambda n:n.get('data-source-node') is not None) is None, 'correction not inserted into translated source')
        else:
            note = by_id(document, 'introduction-years-values')
            self.check([n.text for n in note.iter('bdi')] == ['y', 'P', 'x'], 'source graph axes preserved in original note, not default relabeling')
            self.check('فارمولا' in own_text(note) and 'نہیں گھڑیا' in own_text(note), 'no invented source table/formula claim')
            self.check('گراف موجود نہیں' in own_text(by_id(document, 'introduction-source-context')), 'source above-graph reference explicitly unavailable')

    def validate_frame(self, document, raw):
        self.check(raw.startswith('<!doctype html>\n<html ') and raw.endswith('</html>\n') and raw.count('<!doctype') == 1, 'strict raw HTML envelope')
        self.check(raw[:raw.index('<html')] == '<!doctype html>\n', 'no hidden HTML prelude')
        self.check(document.tag == 'html' and document.attrib == {'lang': 'pnb-Arab-PK', 'dir': 'rtl'}, 'Shahmukhi document RTL')
        self.check([n.tag for n in document] == ['head', 'body'] and not document.text and all(not n.tail for n in document), 'complete HTML root topology')
        head, body = document
        self.check(not head.attrib and not body.attrib, 'exact head/body attributes; no hidden reader')
        self.check([n.tag for n in head] == ['meta', 'meta', 'title', 'style'] and not head.text and all(not n.tail for n in head), 'head contains no hidden resources')
        self.check(head[0].attrib == {'charset': 'utf-8'} and head[1].attrib == {'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}, 'encoding and responsive viewport')
        self.check(not head[2].attrib and not head[3].attrib and all(not len(n) for n in head) and not head[0].text and not head[1].text, 'exact inert head leaf attributes/content')
        self.check(head[2].text == self.translation['title'] + ' — PNB-' + self.unit, 'reader title')
        parsed_code = ast.parse((BASE / 'scripts/build_frontmatter.py').read_text(encoding='utf-8'))
        styles = [ast.literal_eval(n.value) for n in parsed_code.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'UNIT_CSS' for t in n.targets)]
        self.check(len(styles) == 1 and head[3].text == (BASE / 'styles/reader.css').read_text(encoding='utf-8') + styles[0], 'hashed static CSS exactly included')
        self.check(all(s in styles[0] for s in ('width:var(--source-width)', 'max-width:none', 'direction:ltr', 'overflow-wrap:anywhere', '.component-unavailable')), 'independent essential layout constraints')
        self.check('bdi:not([lang="en"]) { white-space:nowrap; }' in head[3].text, 'numeric/formula literals do not break; English names/URLs may wrap')
        self.check([n.tag for n in body] == ['header', 'main', 'footer'] and not body.text and all(not n.tail for n in body), 'complete body topology/tails')
        header, main, footer = body
        self.check(not header.attrib and not main.attrib, 'exact header/main attributes; no hidden source')
        self.check([n.tag for n in header] == ['p', 'h1', 'p', 'p', 'nav'] and not header.text and all(not n.tail for n in header), 'exact header shape/tails')
        self.check(own_text(header[0]) == 'PNB-' + self.unit + ' · A30 / ' + self.module and header[1].text == self.translation['title'] and header[2].text == self.translation['subtitle'], 'header identity/title/subtitle')
        self.check(header[3].text == 'ابتدائی ترجمہ · پنجابی دے ماہر دی لسانی جانچ ہن تک نہیں ہوئی', 'native-review limitation visible')
        prefix = 'preface' if self.unit == '010' else 'introduction'
        expected_header = fragment('<header><p class="eyebrow"><bdi dir="ltr">PNB-' + self.unit + ' · A30 / ' + self.module + '</bdi></p><h1></h1><p></p><p class="status">ابتدائی ترجمہ · پنجابی دے ماہر دی لسانی جانچ ہن تک نہیں ہوئی</p><nav aria-label="سبق دے حصے"><a href="unit-009.html">مشقاں والا پچھلا ریڈر</a> · <a href="#source-document">پورا ماخذی متن</a> · <a href="#' + prefix + '-bridge">ساڈی اصل رہنمائی</a> · <a href="#credits">ماخذ تے سہرے</a></nav></header>')[0]
        expected_header[1].text, expected_header[2].text = self.translation['title'], self.translation['subtitle']
        self.check(html_signature(header) == html_signature(expected_header), 'exact complete header text/attributes/tails')
        self.check([n.get('href') for n in header[4]] == ['unit-009.html', '#source-document', '#' + prefix + '-bridge', '#credits'], 'navigation targets exact')
        self.check(len(main) == 5 and [n.get('id') for n in main] == [prefix + '-source-context', None, 'source-document', prefix + '-bridge', 'terminology'], 'complete main source/original/ledger order')
        self.check(not main.text and all(not n.tail for n in main), 'no main text/tail injection')
        self.check(main[1].attrib == {'class': 'source-label'} and own_text(main[1]) == 'ماخذ دا ترجمہ: OpenStax Precalculus 2e — ' + ('Preface' if self.unit == '010' else 'Introduction to Functions') + '۔', 'exact translated-source label')
        with (BASE / 'terminology.tsv').open(encoding='utf-8', newline='') as stream:
            terms = list(csv.DictReader(stream, delimiter='\t'))
        ledger = main[4]
        self.check([n.tag for n in ledger] == ['h2', 'div'] and not ledger.text and all(not n.tail for n in ledger), 'term ledger topology')
        self.check(len(ledger[1]) == 1 and ledger[1][0].tag == 'table' and [n.tag for n in ledger[1][0]] == ['thead', 'tbody'], 'term ledger table shape')
        rows = ledger[1][0][1]
        self.check(len(rows) == len(terms), 'complete shared terminology rows')
        for index, (row, term) in enumerate(zip(rows, terms)):
            self.check([n.tag for n in row] == ['td', 'td', 'td'] and [own_text(n) for n in row] == [term['pnb-Arab-PK'], term['ur-Arab-PK'], term['en']], 'terminology row:' + str(index))
            self.check(row[1].get('lang') == 'ur-Arab-PK' and row[2].get('lang') == 'en' and row[2].get('dir') == 'ltr', 'terminology language/isolation:' + str(index))
            self.check(not row.text and all(not n.tail for n in row), 'no terminology row-tail injection:' + str(index))
        expected_ledger = fragment('<section id="terminology"><h2>تِن زباناں دی سانجھی اصطلاحی کُنجی</h2><div class="table-scroll"><table><thead><tr><th scope="col">شاہ مکھی پنجابی</th><th scope="col" lang="ur-Arab-PK">اردو</th><th scope="col" lang="en" dir="ltr">English</th></tr></thead><tbody /></table></div></section>')[0]
        for term in terms:
            row = ET.SubElement(expected_ledger[1][0][1], 'tr')
            for language, a in [('pnb-Arab-PK', {}), ('ur-Arab-PK', {'lang':'ur-Arab-PK'}), ('en', {'lang':'en', 'dir':'ltr'})]:
                ET.SubElement(row, 'td', a).text = term[language]
        self.check(html_signature(ledger) == html_signature(expected_ledger), 'exact ledger topology/all own text/tails/attributes')
        self.check(footer.attrib == {'id': 'credits', 'lang': 'en', 'dir': 'ltr'} and [n.tag for n in footer] == ['h2', 'p', 'p', 'p'], 'footer topology')
        self.check(not footer.text and all(not n.tail for n in footer), 'no footer tail injection')
        links = [n.get('href') for n in footer.iter('a')]
        self.check(links == ['https://github.com/openstax/osbooks-college-algebra-bundle/blob/789b54099106b071d1d32bfcee454fed72eb4768/modules/' + self.module + '/index.cnxml', 'https://creativecommons.org/licenses/by-nc-sa/4.0/', '../provenance/ATTRIBUTION.md', f'../provenance/unit-{self.unit}-component-notices.json'], 'exact provenance and license destinations')
        text = own_text(footer)
        self.check('OpenStax and Rice University do not endorse this adaptation.' in text and 'No native-speaker, educator or assistive-technology certification is claimed.' in text, 'nonendorsement and certification limits')
        if self.unit == '010':
            self.check(self.row['attribution'] in text and '55 source line breaks' in text and '28 emphasis' in text, 'preface footer source credit/counts')
        else:
            self.check('Image coverage remains incomplete' in text and 'NOT copied, rendered, linked as an asset or exported' in text and 'Prayitno Hadinata' in text and 'MeasuringWorth' in text, 'quarantine exclusion and named credits visible')
        expected_footer = fragment('<footer id="credits" lang="en" dir="ltr"><h2>Sources, credits and changes</h2><p>Text adapted from <a href="' + links[0] + '">OpenStax Precalculus 2e, module ' + self.module + '</a>, Jay Abramson et al., OpenStax / Rice University; foundational chapters credit David Lippman and Melonie Rasmussen. Text adaptation: <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a>. Contributor records remain in <a href="../provenance/ATTRIBUTION.md">the shared provenance record</a>; this unit retains its <a href="../provenance/unit-' + self.unit + '-component-notices.json">exact existing component notice</a>. OpenStax and Rice University do not endorse this adaptation.</p><p /><p /></footer>')[0]
        if self.unit == '010':
            expected_footer[2].text = 'Changes: complete 98-block Shahmukhi translation of the preface, including original metadata/abstract, all lists and post-list prose, nine contributing-author lines and 46 reviewer lines. All 55 source line breaks and 28 emphasis elements remain. The admitted 975×473 JPEG is unchanged: Copyright Rice University, OpenStax, under CC BY-NC-SA 4.0. The printed diagonal label x=1 is retained in the pixels and explicitly corrected to y=x only in a separately labeled original explanation. Original bilingual/accessibility support is not source prose.'
        else:
            expected_footer[2].text = 'Changes: complete six-block Shahmukhi text/alt/caption translation, with original metadata, empty abstract and empty unnumbered-figure label preserved. The source JPEG is quarantined in the existing component record and is NOT copied, rendered, linked as an asset or exported. Its source node/reference/hash and named caption credits remain; a clearly original unavailable-component notice takes its place. Source credit "bull": modification of work by Prayitno Hadinata; source credit "graph": modification of work by MeasuringWorth. Image coverage remains incomplete pending coordinated permission or replacement. The text license is not asserted as permission for that excluded JPEG.'
        expected_footer[3].text = 'Source order and all identifiers are retained; no MathML exists in this module. Plain source URLs remain plain text. Historical prices, biography, publication plans and resource claims are translated source statements, not current verification. Indonesian comparison: KokunoYumeto/openstax-precalculus-2e-id, alpha.58-reader.1; canonical commit 789b54099106b071d1d32bfcee454fed72eb4768. No native-speaker, educator or assistive-technology certification is claimed. The full five-work assignment remains active; this reader is not a complete book or final release.'
        self.check(html_signature(footer) == html_signature(expected_footer), 'complete footer content and credit text/markup/tails exact')
        for node in document.iter():
            self.check(node.tag not in {'script', 'iframe', 'object', 'embed', 'canvas', 'svg', 'video', 'audio', 'picture', 'source'}, 'no active/hidden content elements')
            for k, v in node.attrib.items():
                self.check(not k.lower().startswith('on') and k not in ('srcdoc', 'srcset') and not re.search(r'url\s*\(|javascript:|data:', v, flags=re.I), 'no executable/resource injection attribute')
            if node.tag == 'bdi':
                self.check(node.get('dir') == 'ltr', 'all literal islands LTR')
        self.check(not re.search(r'url\s*\(|@import', head[3].text, flags=re.I), 'no remote CSS resources')
        self.check(not any(c in raw for c in FORBIDDEN), 'no bidi controls/replacement glyph')
        self.check(unicodedata.normalize('NFC', raw) == raw, 'reader NFC Unicode')
        self.check('{{' not in raw and '__DRAFT_REQUIRED__' not in raw, 'no unfinished placeholders')

    def validate_document(self, document, raw=None):
        if raw is None:
            raw = '<!doctype html>\n' + ET.tostring(document, encoding='unicode') + '\n'
        self.validate_structure(document)
        self.validate_values(document)
        self.validate_links(document)
        self.validate_media(document)
        self.validate_original(document)
        self.validate_frame(document, raw)

    def mutation(self, label, document, change, validator=None):
        altered = copy.deepcopy(document)
        change(altered)
        before = len(self.checks)
        try:
            (validator or self.validate_document)(altered)
        except (AssertionError, KeyError, ValueError, IndexError, StopIteration, ET.ParseError):
            del self.checks[before:]
            self.mutations.append(label)
            self.check(True, 'detached mutation rejected:' + label)
        else:
            del self.checks[before:]
            raise AssertionError('Mutation escaped: ' + label)

    def mutations_run(self, document):
        def keyed(d, k):
            return next(n for n in d.iter() if n.get('data-source-key') == k)
        def remove(d, node):
            parent = next(n for n in d.iter() if node in list(n))
            parent.remove(node)
        first_para = next(n.get('id') for n in self.full.iter() if tag(n) == 'para')
        self.mutation('source paragraph omitted', document, lambda d: remove(d, by_id(d, first_para)))
        self.mutation('unkeyed contradictory source paragraph', document, lambda d: by_id(d, 'source-document').append(ET.fromstring('<p>Contradictory answer 999.</p>')))
        self.mutation('source structural own text injected', document, lambda d: setattr(by_id(d, 'source-document'), 'text', 'extra source claim'))
        self.mutation('source structural child tail injected', document, lambda d: setattr(by_id(d, 'source-document')[0], 'tail', 'extra tail claim'))
        self.mutation('source paragraph tail injected', document, lambda d: setattr(by_id(d, first_para), 'tail', 'uncredited addition'))
        self.mutation('source paragraph wrapper changed', document, lambda d: setattr(by_id(d, first_para), 'tag', 'aside'))
        self.mutation('source node path duplicated', document, lambda d: by_id(d, first_para).set('data-source-node', 'root'))
        self.mutation('source ID altered', document, lambda d: by_id(d, first_para).set('id', 'altered-source-id'))
        self.mutation('source namespace changed', document, lambda d: by_id(d, first_para).set('data-source-namespace', 'urn:wrong'))
        self.mutation('source module class changed', document, lambda d: by_id(d, 'source-document').set('data-source-class', 'wrong'))
        self.mutation('source root children swapped', document, lambda d: self.swap(by_id(d, 'source-document'), 0, 1))
        self.mutation('source paragraph hidden by added style', document, lambda d: by_id(d, first_para).set('style', 'display:none'))
        self.mutation('source paragraph hidden by aria-hidden', document, lambda d: by_id(d, first_para).set('aria-hidden', 'true'))
        self.mutation('metadata UUID changed', document, lambda d: setattr(next(n for n in d.iter() if n.get('data-source-tag') == 'uuid')[0], 'text', 'invented-uuid'))
        self.mutation('metadata UUID child-tail injection', document, lambda d: setattr(next(n for n in d.iter() if n.get('data-source-tag') == 'uuid')[0], 'tail', 'secret claim'))
        self.mutation('translated title changed', document, lambda d: setattr(keyed(d, self.module + '/title'), 'text', 'wrong title'))
        self.mutation('extra main content appended', document, lambda d: d.find('body/main').append(ET.Element('p')))
        self.mutation('hidden prelude script', document, lambda d: None, lambda d:self.validate_frame(d, '<script>bad()</script><!doctype html>\n' + ET.tostring(d, encoding='unicode') + '\n'))
        self.mutation('post-document content', document, lambda d: None, lambda d:self.validate_frame(d, '<!doctype html>\n' + ET.tostring(d, encoding='unicode') + '<p>extra</p>\n'))
        self.mutation('wrong document direction', document, lambda d: d.set('dir', 'ltr'))
        self.mutation('whole reader hidden by body style', document, lambda d: d.find('body').set('style', 'display:none'))
        self.mutation('whole reader hidden from accessibility', document, lambda d: d.find('body').set('aria-hidden', 'true'))
        self.mutation('main hidden attribute injected', document, lambda d: d.find('body/main').set('hidden', 'hidden'))
        self.mutation('main source hidden by style', document, lambda d: d.find('body/main').set('style', 'display:none'))
        self.mutation('head hidden attribute injected', document, lambda d: d.find('head').set('aria-hidden', 'true'))
        self.mutation('CSS disabled outside print', document, lambda d: d.find('head/style').set('media', 'print'))
        self.mutation('numeric range nowrap CSS removed', document, lambda d: setattr(d.find('head/style'), 'text', d.find('head/style').text.replace('bdi:not([lang="en"]) { white-space:nowrap; }', 'bdi { white-space:normal; }')))
        self.mutation('literal direction changed', document, lambda d: next(d.iter('bdi')).set('dir', 'rtl'))
        self.mutation('footer source URL changed', document, lambda d: next(by_id(d, 'credits').iter('a')).set('href', 'https://example.invalid/'))
        self.mutation('footer contradictory claim appended', document, lambda d: setattr(by_id(d, 'credits')[2], 'text', by_id(d, 'credits')[2].text + ' Source image coverage is complete in all cases.'))
        self.mutation('header navigation wording changed', document, lambda d: setattr(d.find('body/header/nav')[0], 'text', 'wrong navigation label'))
        self.mutation('term ledger tbody text injected', document, lambda d: setattr(by_id(d, 'terminology')[1][0][1], 'text', 'wrong term'))
        self.mutation('script inserted in original bridge', document, lambda d: by_id(d, 'preface-bridge' if self.unit == '010' else 'introduction-bridge').append(ET.Element('script')))
        self.mutation('CSS remote resource injected', document, lambda d: setattr(d.find('head/style'), 'text', d.find('head/style').text + 'body{background:url(https://example.invalid/a)}'))
        self.mutation('Unicode bidi override injected', document, lambda d: setattr(by_id(d, first_para), 'text', '\u202e' + (by_id(d, first_para).text or '')))
        self.mutation('invented MathML', document, lambda d: by_id(d, 'source-document').append(ET.Element('{http://www.w3.org/1998/Math/MathML}math')))
        if self.unit == '010':
            self.mutation('source abstract omitted', document, lambda d: remove(d, keyed(d, self.module + '/metadata/abstract')))
            self.mutation('child list reordered', document, lambda d: self.swap(by_id(d, 'eip-id1168983371474'), 0, 1))
            self.mutation('mixed post-list tail removed', document, lambda d: setattr(by_id(d, 'eip-id1166690773820'), 'tail', ''))
            self.mutation('chapter range changed', document, lambda d: setattr(next(by_id(d, 'eip-id1164239746735').iter('bdi')), 'text', '1-5'))
            self.mutation('650 example count changed', document, lambda d: setattr(next(by_id(d, 'eip-321').iter('bdi')), 'text', '651'))
            self.mutation('biography years changed', document, lambda d: setattr(next(n for n in by_id(d, 'eip-704').iter('bdi') if n.text == '35'), 'text', '36'))
            self.mutation('author spelling changed', document, lambda d: setattr(next(by_id(d, 'eip-777').iter('bdi')), 'text', 'Unknown Author'))
            self.mutation('reviewer terminal newline removed', document, lambda d: by_id(d, 'eip-958').remove(by_id(d, 'eip-958')[-1]))
            self.mutation('reviewer newline tail injected', document, lambda d: setattr(by_id(d, 'eip-958')[-1], 'tail', 'another invented reviewer'))
            self.mutation('source italic changed to bold', document, lambda d: setattr(next(n for n in d.iter('em') if n.get('data-source-node')), 'tag', 'strong'))
            self.mutation('source author link target changed', document, lambda d: next(n for n in d.iter('a') if n.get('data-source-link')).set('href', '#eip-29'))
            self.mutation('source author link tail injected', document, lambda d: setattr(next(n for n in d.iter('a') if n.get('data-source-link')), 'tail', 'new contradictory claim'))
            self.mutation('admitted image URL changed', document, lambda d: next(d.iter('img')).set('src', 'unit-009.html'))
            self.mutation('admitted image dimension changed', document, lambda d: next(d.iter('img')).set('width', '974'))
            self.mutation('admitted source alt changed', document, lambda d: next(d.iter('img')).set('alt', 'wrong graph'))
            self.mutation('image scroll direction changed', document, lambda d: next(n for n in d.iter() if n.get('class') == 'figure-scroll').set('dir', 'rtl'))
            self.mutation('image wrapper extra text', document, lambda d: setattr(next(n for n in d.iter() if n.get('class') == 'figure-scroll'), 'text', 'uncredited image claim'))
            self.mutation('correction detached from accessibility', document, lambda d: next(d.iter('img')).set('aria-describedby', 'preface-diagram-description'))
            self.mutation('incorrect original cubic coefficient', document, lambda d: setattr(next(n for n in by_id(d, 'preface-diagram-description').iter('bdi') if n.text == 'f(x)=5x³+1'), 'text', 'f(x)=6x³+1'))
            self.mutation('wrong reflected ordered pair', document, lambda d: setattr(next(n for n in by_id(d, 'preface-diagram-description').iter('bdi') if n.text == '(6,1)'), 'text', '(1,6)'))
            self.mutation('incorrect correction line', document, lambda d: setattr(list(by_id(d, 'preface-reflection-correction').iter('bdi'))[1], 'text', 'y=1'))
            self.mutation('independent source numeral detector', document, lambda d: setattr(next(by_id(d, 'eip-321').iter('bdi')), 'text', '651'), self.validate_values)
            self.mutation('independent source-image cubic detector', document, lambda d: setattr(next(n for n in by_id(d, 'preface-diagram-description').iter('bdi') if n.text == 'f(x)=5x³+1'), 'text', 'f(x)=6x³+1'), self.validate_graph_bindings)
            self.mutation('independent source-image inverse-pair detector', document, lambda d: setattr(next(n for n in by_id(d, 'preface-diagram-description').iter('bdi') if n.text == '(6,1)'), 'text', '(1,6)'), self.validate_graph_bindings)
        else:
            self.mutation('source empty abstract given invented prose', document, lambda d: setattr(next(n for n in d.iter() if n.get('data-source-tag') == 'abstract'), 'text', 'invented objective'))
            self.mutation('source empty figure label numbered', document, lambda d: setattr(next(n for n in d.iter() if n.get('data-source-tag') == 'label'), 'text', 'Figure 1'))
            self.mutation('source caption named credit removed', document, lambda d: setattr(next(n for n in keyed(d, 'Figure_01_00_001/caption').iter('bdi') if n.text == 'MeasuringWorth'), 'text', 'OpenStax'))
            self.mutation('source dollar thousands decimal changed', document, lambda d: setattr(next(n for n in by_id(d, 'fs-id1165137768418').iter('bdi') if n.text == '$1,100'), 'text', '$1.100'))
            self.mutation('source historical date changed', document, lambda d: setattr(next(n for n in by_id(d, 'fs-id1165137768418').iter('bdi') if n.text == '1995'), 'text', '1996'))
            self.mutation('source y year relabeled x', document, lambda d: setattr(next(by_id(d, 'introduction-years-values').iter('bdi')), 'text', 'x'))
            self.mutation('quarantined JPEG published in img', document, lambda d: by_id(d, 'fs-id1165137810701').append(ET.Element('img', {'src':'../' + self.image_spec['path']})))
            self.mutation('quarantined source image slot changed to img', document, lambda d: setattr(next(n for n in d.iter() if n.get('data-source-tag') == 'image'), 'tag', 'img'))
            self.mutation('quarantined image hidden in CSS', document, lambda d: by_id(d, 'introduction-image-unavailable').set('style', 'background-image:url(../' + self.image_spec['path'] + ')'))
            self.mutation('quarantine source hash reference changed', document, lambda d: next(n for n in d.iter() if n.get('data-source-tag') == 'image').set('data-source-sha256', '0'*64))
            self.mutation('quarantine falsely marked complete', document, lambda d: next(n for n in d.iter() if n.get('data-source-tag') == 'image').set('data-asset-coverage', 'complete'))
            self.mutation('quarantine source-reference tail injected', document, lambda d: setattr(next(n for n in d.iter() if n.get('class') == 'component-reference'), 'tail', 'uncredited addition'))
            self.mutation('original rights notice mislabeled source', document, lambda d: by_id(d, 'introduction-image-unavailable').set('data-origin', 'translated-source'))
            self.mutation('independent source-dollar punctuation detector', document, lambda d: setattr(next(n for n in by_id(d, 'fs-id1165137768418').iter('bdi') if n.text == '$1,100'), 'text', '$1.100'), self.validate_values)
            self.mutation('independent source-year detector', document, lambda d: setattr(next(n for n in by_id(d, 'fs-id1165137768418').iter('bdi') if n.text == '1995'), 'text', '1996'), self.validate_values)
            self.mutation('independent source-axis detector', document, lambda d: setattr(next(by_id(d, 'introduction-years-values').iter('bdi')), 'text', 'x'), self.validate_graph_bindings)

    @staticmethod
    def swap(parent, a, b):
        children = list(parent)
        children[a], children[b] = children[b], children[a]
        parent[:] = children

    def preparation_mutations(self):
        from prepare_frontmatter import validate_component
        data = self.original_image.read_bytes()
        cases = [
            ('manifest asset path traversal', lambda s,r,n:s.__setitem__('path', '../escape.jpg')),
            ('manifest image hash altered', lambda s,r,n:s.__setitem__('sha256', '0'*64)),
            ('manifest media ID altered', lambda s,r,n:s.__setitem__('media_id', 'invented')),
            ('manifest image dimension altered', lambda s,r,n:s.__setitem__('width', s['width']+1)),
            ('manifest source module notice altered', lambda s,r,n:r.__setitem__('source_modules', 'm49301')),
            ('exact notice credit dropped', lambda s,r,n:n[0].__setitem__('attribution', '')),
            ('component admission reversed', lambda s,r,n:r.__setitem__('admission', 'quarantined' if self.unit == '010' else 'admitted')),
            ('publication status bypassed', lambda s,r,n:s.__setitem__('publication_status', 'admitted-unchanged' if self.unit == '011' else 'quarantined-not-copied')),
        ]
        for label, change in cases:
            s,r,n = copy.deepcopy(self.image_spec), copy.deepcopy(self.row), copy.deepcopy(self.notice)
            change(s,r,n)
            try:
                validate_component(self.unit, self.full, s,r,data,n)
            except (AssertionError, KeyError, ValueError):
                self.mutations.append(label)
                self.check(True, 'detached preparation mutation rejected:' + label)
            else:
                raise AssertionError('Preparation mutation escaped: ' + label)


def run(unit, check_only):
    def command(script, *args):
        result = subprocess.run([sys.executable, '-B', str(BASE / 'scripts' / script), *args], check=True, capture_output=True, text=True, encoding='utf-8')
        return result.stdout.strip()
    before = None
    if not check_only:
        command('prepare_frontmatter.py', '--unit', unit, '--check-only')
        command('build_frontmatter.py', '--unit', unit)
        before = (BASE / f'reader/unit-{unit}.html').read_bytes()
        command('build_frontmatter.py', '--unit', unit)
        assert before == (BASE / f'reader/unit-{unit}.html').read_bytes(), 'build not deterministic'
    qa = QA(unit)
    inputs_before = {p: p.read_bytes() for p in qa.input_paths}
    qa.validate_inputs()
    data = qa.reader_path.read_bytes()
    raw = data.decode('utf-8')
    assert raw.startswith('<!doctype html>\n')
    document = ET.fromstring(raw[len('<!doctype html>\n'):])
    qa.validate_document(document, raw)
    qa.mutations_run(document)
    qa.preparation_mutations()
    qa.check(all(p.read_bytes() == b for p,b in inputs_before.items()), 'all scoped inputs unchanged during QA')
    qa.check(qa.reader_path.read_bytes() == data, 'detached mutations never alter reader')
    if before is not None:
        qa.check(before == data, 'two deterministic builds')
    receipt = {
        'unit': 'PNB-' + unit, 'status': 'passed' if unit == '010' else 'text-and-quarantine-placeholder-passed; source-image-coverage-incomplete',
        'source_module': qa.module, 'source_elements_including_document': qa.spec['nodes'], 'source_ids': qa.spec['ids'],
        'translated_source_blocks': qa.spec['keys'], 'source_mathml': 0, 'source_images': 1,
        'published_images': 1 if unit == '010' else 0, 'quarantined_images': 0 if unit == '010' else 1,
        'source_image_coverage_complete': unit == '010', 'checks_passed': len(qa.checks),
        'detached_mutations_rejected': len(qa.mutations), 'mutations': qa.mutations,
        'scope': 'Whole canonical source-derived node/ID/ancestry/text-key/inline/number/metadata/credit coverage; independent image witness/admission validation; original notes separated. No renderer expected-DOM import.',
        'limitations': ['Native Punjabi specialist review pending', 'Browser/assistive-technology certification is a separate gate', 'Source historical/legal/resource statements are not current verification', 'Finite graphic checks are not a proof of universal mathematical/market claims', 'The full five-work assignment remains active'] + ([] if unit == '010' else ['Source JPEG remains quarantined, absent and unexported; image coverage is incomplete']),
        'reader_sha256': sha(data),
        'inputs': [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(b)} for p,b in inputs_before.items()],
        'checks': qa.checks,
    }
    if not check_only:
        (BASE / f'qa/structural-{unit}.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({k:receipt[k] for k in ['unit','status','checks_passed','detached_mutations_rejected','reader_sha256','source_image_coverage_complete']}, sort_keys=True))
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unit', choices=['010','011'], required=True)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    run(args.unit, args.check_only)
