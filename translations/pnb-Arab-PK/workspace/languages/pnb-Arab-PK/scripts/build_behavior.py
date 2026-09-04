"""Build the standalone deterministic PNB-013 complete-m49306 reader."""
from pathlib import Path
import argparse
import copy
import csv
import hashlib
import html
import json
import re
import xml.etree.ElementTree as ET

import build_domain_range as shared
from build_domain_range import attributes, source_attrs, tag
from prepare_behavior import prepare, source_blocks
from qa_notation import unique_object


BASE = Path(__file__).resolve().parents[1]


def math_html(original, owner, slot):
    """Preserve every canonical token; bidi isolation is outside the MathML tree."""
    clone = copy.deepcopy(original)
    clone.tail = None
    clone.set('dir', 'ltr')
    attrs = {'class': 'math-isolate', 'dir': 'ltr', 'data-source-owner': owner,
             'data-source-slot': slot}
    if any(tag(node) == 'mtable' for node in original.iter()) or len(list(original.iter())) > 70:
        attrs.update({'tabindex': '0', 'role': 'region',
                      'aria-label': 'ریاضی دا فارمولا؛ لوڑ پئے تے پاسے سرکاؤ'})
    return '<span' + attributes(attrs) + '>' + ET.tostring(clone, encoding='unicode') + '</span>'


class BehaviorRenderer(shared.DomainRenderer):
    """Render canonical m49306 structures without importing expected DOM."""
    def __init__(self, source, manifest, translation):
        self.source, self.manifest, self.translation = source, manifest, translation
        self.blocks, self.used = translation['source_blocks'], set()
        self.parent = {child: node for node in source.iter() for child in node}
        self.keys = {node: key for key, node in source_blocks(source)}
        self.images = {row['media_id']: row for row in manifest['images']}
        self.links = {row['path']: row for row in manifest['source_links']}
        self.paths = {source: 'root'}
        for node in source.iter():
            for index, child in enumerate(node):
                self.paths[child] = self.paths[node] + '/' + str(index)
        self.exercises = [node.get('id') for node in source.iter() if tag(node) == 'exercise']
        self.footnotes = []

    def translated(self, node):
        key = self.keys[node]
        assert key not in self.used
        self.used.add(key)
        value = self.blocks[key]
        if tag(node) in ('media', 'table'):
            assert '{{' not in value
            return value

        def descendants(current, wanted):
            for child in current:
                name = tag(child)
                if name == wanted:
                    yield child
                elif name not in ('list', 'table', 'media', 'figure', 'footnote', 'para', 'term'):
                    yield from descendants(child, wanted)

        groups = {
            'math': list(descendants(node, 'math')),
            'term': list(descendants(node, 'term')),
            'link': list(descendants(node, 'link')),
            'break': list(descendants(node, 'newline')),
            'child': [child for child in node
                      if (child in self.keys and tag(child) != 'term')
                      or tag(child) in ('list', 'table', 'media', 'figure')],
        }
        for kind, nodes in groups.items():
            found = re.findall(r'\{\{' + kind + r':(\d+)\}\}', value)
            assert found == [str(index) for index in range(len(nodes))], key + ':' + kind

        def substitute(match):
            kind, index = match[1], int(match[2])
            original = groups[kind][index]
            if kind == 'math':
                return math_html(original, key, index)
            if kind == 'term':
                term_key = self.keys[original]
                assert term_key not in self.used
                self.used.add(term_key)
                return '<span' + attributes({'id': original.get('id'), 'class': 'source-term',
                                              'data-source-key': term_key,
                                              **source_attrs(original)}) + '>' + self.blocks[term_key] + '</span>'
            if kind == 'child':
                return self.render(original)
            if kind == 'break':
                return '<br data-source-break="' + self.paths[original] + '" />'
            link_key = key + '/link/' + str(index)
            spec = self.links[self.paths[original]]
            label = self.translation['source_link_labels'].get(link_key)
            if original.get('url'):
                href = original.get('url')
                assert spec['attributes']['url'] == href and label
            else:
                target = original.get('target-id')
                assert target and any(item.get('id') == target for item in self.source.iter())
                href = '#' + target
                if label is None:
                    target_node = next(item for item in self.source.iter() if item.get('id') == target)
                    label = {'figure': 'متعلقہ شکل', 'example': 'متعلقہ مثال',
                             'table': 'متعلقہ جدول'}.get(tag(target_node), 'متعلقہ حصہ')
            return '<a' + attributes({'href': href, 'data-source-link': link_key}) + '>' + label + '</a>'

        return re.sub(r'\{\{(math|term|link|child|break):(\d+)\}\}', substitute, value)

    def table(self, node):
        sid = node.get('id')
        original_summary = self.translated(node)
        group = next(child for child in node if tag(child) == 'tgroup')
        body = '<colgroup>' + ''.join('<col' + attributes(source_attrs(column)) + ' />'
                                     for column in group if tag(column) == 'colspec') + '</colgroup>'
        row_index = 0
        for subgroup in (child for child in group if tag(child) in ('thead', 'tbody')):
            body += '<' + tag(subgroup) + attributes(source_attrs(subgroup)) + '>'
            for row in subgroup:
                row_index += 1
                body += '<tr' + attributes(source_attrs(row)) + '>'
                for column_index, entry in enumerate(row, 1):
                    key = f'{sid}/row/{row_index}/entry/{column_index}'
                    assert self.keys[entry] == key
                    is_header = key in self.translation['table_header_cells']
                    attrs = {'dir': 'rtl', 'data-source-key': key, **source_attrs(entry)}
                    if entry.get('align') == 'center':
                        attrs['style'] = 'text-align:center'
                    if is_header:
                        attrs['scope'] = self.translation['table_header_scopes'][key]
                    body += '<' + ('th' if is_header else 'td') + attributes(attrs) + '>'
                    body += self.translated(entry)
                    body += '</' + ('th' if is_header else 'td') + '>'
                body += '</tr>'
            body += '</' + tag(subgroup) + '>'
        attrs = {'id': sid, 'class': 'source-table', 'dir': 'ltr',
                 'data-source-summary': original_summary,
                 'aria-label': self.translation['table_summary_overrides'][sid],
                 'aria-describedby': 'behavior-table-correction' if sid == 'Table_01_03_03'
                 else 'behavior-table-summary',
                 'data-description-origin': 'original-correction',
                 **source_attrs(node, ('summary',))}
        note = 'behavior-table-correction' if sid == 'Table_01_03_03' else 'behavior-table-summary'
        advisory = '<p class="scroll-hint source-summary-advisory">ماخذ دے خلاصے بارے <a href="#' + note + '">ساڈی اصل وضاحت ویکھو</a>۔</p>'
        return '<div class="source-table-container" data-source-child="' + sid + '"><div class="table-scroll source-table-scroll" dir="ltr" tabindex="0" role="region" aria-label="جدول؛ لوڑ پئے تے پاسے سرکاؤ"><table' + attributes(attrs) + '>' + body + '</table></div>' + advisory + '</div>'


def build():
    prepare(check_only=True)
    manifest = json.loads((BASE / 'source-excerpts/manifest-013.json').read_text(encoding='utf-8'), object_pairs_hook=unique_object)
    translation = json.loads((BASE / 'translations/unit-013.json').read_text(encoding='utf-8'), object_pairs_hook=unique_object)
    source = ET.parse(BASE / 'source-excerpts/unit-013.cnxml').getroot()
    shared.math_html = math_html
    renderer = BehaviorRenderer(source, manifest, translation)
    body = renderer.render(source)
    assert renderer.used == set(translation['source_blocks'])
    assert len(renderer.exercises) == 61 and len(renderer.footnotes) == 1
    assert all(('data-source-link="' + row['key'] + '"') in body for row in manifest['source_links'])
    endnotes = '<section class="source-endnotes"><h2>ماخذ دے حوالے</h2><ol>' + ''.join(
        '<li id="' + sid + '-text">' + value + ' <a href="#' + sid + '">متن ول واپس</a></li>'
        for sid, value in renderer.footnotes) + '</ol></section>'
    with (BASE / 'terminology.tsv').open(encoding='utf-8', newline='') as stream:
        terms = list(csv.DictReader(stream, delimiter='\t'))
    ledger = '<section id="terminology"><h2>تِن زباناں دی اصطلاحی کُنجی</h2><div class="table-scroll"><table><thead><tr><th scope="col">شاہ مکھی پنجابی</th><th scope="col" lang="ur-Arab-PK">اردو</th><th scope="col" lang="en" dir="ltr">English</th></tr></thead><tbody>'
    for row in terms:
        ledger += '<tr><td>' + html.escape(row['pnb-Arab-PK']) + '</td><td lang="ur-Arab-PK">' + html.escape(row['ur-Arab-PK']) + '</td><td lang="en" dir="ltr">' + html.escape(row['en']) + '</td></tr>'
    ledger += '</tbody></table></div></section>'
    css = (BASE / 'styles/reader.css').read_text(encoding='utf-8') + '''
.source-media { max-width:100%; }
.source-media img { display:block; width:var(--source-width); min-width:var(--source-width); max-width:none; height:auto; padding:0; border:0; }
.source-table td[dir="rtl"], .source-table th[dir="rtl"] { white-space:normal; font-family:inherit; }
.source-para { margin-block:.8rem; }
.source-glossary dt { font-weight:bold; color:var(--accent); }
.source-glossary dd { margin-inline-start:1rem; margin-block-end:1rem; }
.source-exercise { margin-block:1.5rem; border-block-start:1px solid #cad7d1; padding-block-start:.4rem; }
.source-term { font-weight:inherit; }
'''
    title = html.escape(translation['title'])
    source_url = manifest['upstream_url'] + '/blob/' + manifest['commit'] + '/' + manifest['path']
    result = '<!doctype html>\n<html lang="pnb-Arab-PK" dir="rtl"><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" /><title>' + title + ' — PNB-013</title><style>' + css + '</style></head><body>'
    result += '<header><p class="eyebrow"><bdi dir="ltr">PNB-013 · A30 / m49306</bdi></p><h1>' + title + '</h1><p>' + html.escape(translation['subtitle']) + '</p><p class="status">نظرثانی ہُندا مسودہ · ماخذ-بند خودکار جانچ پاس؛ براؤزر، پنجابی تے ریاضی ماہر دی جانچ باقی اے</p><nav aria-label="سبق دے حصے"><a href="unit-012.html">پچھلا سبق</a> · <a href="#fs-id1165137645483">بدلاوے دی اوسط شرح</a> · <a href="#fs-id1165135440486">گراف دا ورتارا</a> · <a href="#fs-id1165135457748">مشقاں</a> · <a href="#source-glossary-title">اصطلاحاں</a> · <a href="#behavior-bridge">ساڈیاں اصل وضاحتاں</a></nav></header>'
    result += '<main>' + translation['bridge_before_html'] + '<section id="source-translation">' + body + '</section>' + endnotes + translation['bridge_after_html'] + '<p id="behavior-table-summary" class="original">ہر جدول دا ماخذی <bdi dir="ltr" lang="en">summary</bdi> وکھرے <bdi dir="ltr" lang="en">data-source-summary</bdi> وچ محفوظ اے؛ <bdi dir="ltr" lang="en">aria-label</bdi> اصل دکھائی بنتر تے خانے پڑھ کے دِتا گیا اے۔</p>' + ledger + '</main>'
    result += '<footer id="credits" lang="en" dir="ltr"><h2>Sources, credits and changes</h2><p>Adapted from <a href="' + source_url + '">OpenStax Precalculus 2e, complete module m49306</a>, Jay Abramson et al., OpenStax / Rice University. Exact existing component records for all 24 admitted work-default JPEGs are retained in <a href="../provenance/unit-013-component-notices.json">unit-013-component-notices.json</a>. OpenStax and Rice University do not endorse this adaptation.</p><p>Changes: Shahmukhi Punjabi draft of all 353 source text blocks, all 61 exercises and all 38 source-supplied solutions; the 23 Section Exercises without source solutions remain unanswered. All 254 canonical MathML trees and 438 source IDs remain source-derived. All 24 canonical JPEGs are unchanged; translated source alt strings stay in data-source-alt and separately marked original descriptions disclose visible details and source discrepancies. The false Table_01_03_03 source summary remains in data-source-summary while its visible 2004 cell remains 249 and the aria label states the actual table. Original precision notes and bilingual support are separate from source translation.</p><p>Indonesian comparison edition: KokunoYumeto/openstax-precalculus-2e-id, pinned local comparison. No native-speaker, educator, visual, mathematical-pedagogy or assistive-technology certification is claimed. This is one complete source module, not a complete textbook, final publication or model-training corpus. The full five-work assignment remains active.</p></footer></body></html>'
    assert '<script' not in result.lower() and '<iframe' not in result.lower() and '<object' not in result.lower()
    reader = BASE / 'reader/unit-013.html'
    reader.parent.mkdir(parents=True, exist_ok=True)
    reader.write_text(result, encoding='utf-8', newline='\n')
    built = reader.read_bytes()
    assert hashlib.sha256(built).hexdigest() == hashlib.sha256(result.encode('utf-8')).hexdigest()
    print('Built PNB-013: 353 source blocks, 61 exercises, 38 supplied solutions, 24 unchanged images')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unit', choices=['013'], default='013')
    parser.parse_args()
    build()
