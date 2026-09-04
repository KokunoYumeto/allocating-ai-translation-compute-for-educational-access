"""Standalone PNB010/011 readers; exact source-node markers and no quarantined image output."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
import argparse
import csv
import hashlib
import html
import json
import re
import xml.etree.ElementTree as ET

from qa_notation import unique_object
from prepare_frontmatter import prepare

BASE = Path(__file__).resolve().parents[1]
UNIT_CSS = '''
bdi:not([lang="en"]) { white-space:nowrap; }
.source-document { margin-block:1.4rem; }
.source-metadata { border-inline-start:3px solid #cad7d1; padding-inline-start:1rem; }
.metadata-value { font-size:.8rem; overflow-wrap:anywhere; }
.source-para { margin-block:.8rem; }
.source-media { max-width:100%; margin-block:1rem; }
.source-media img { display:block; width:var(--source-width); min-width:var(--source-width); max-width:none; height:auto; padding:0; border:0; }
.figure-scroll { max-width:100%; direction:ltr; }
.component-unavailable { border:2px dashed #b98238; background:#fff6e7; }
.component-reference { font-size:.8rem; overflow-wrap:anywhere; }
.source-alt-text { font-size:1rem; }
.source-empty-label { display:none; }
h4 { color:var(--accent); font-size:1.08rem; }
.original { border-block-start:1px solid #cad7d1; }
'''


def tag(node):
    return node.tag.rsplit('}', 1)[-1]


def attrs(values):
    return ''.join(' ' + k + '="' + html.escape(str(v), quote=True) + '"' for k, v in values.items())


def inner(node):
    return html.escape(node.text or '') + ''.join(ET.tostring(c, encoding='unicode') for c in node)


class Renderer:
    def __init__(self, unit, source, manifest, translation):
        self.unit, self.source, self.manifest, self.translation = unit, source, manifest, translation
        self.blocks = translation['source_blocks']
        self.parent = {c: n for n in source.iter() for c in n}
        self.paths = {}
        self.used = []

        def walk(node, path):
            self.paths[node] = path
            for i, child in enumerate(node):
                walk(child, str(i) if path == 'root' else path + '/' + str(i))
        walk(source, 'root')

    def source_attrs(self, node):
        out = {'data-source-node': self.paths[node], 'data-source-tag': tag(node),
               'data-source-namespace': node.tag[1:].split('}', 1)[0]}
        if node.get('id'):
            out['id'] = node.get('id')
        out.update({'data-source-' + k: v for k, v in node.attrib.items() if k != 'id'})
        return out

    def key(self, node):
        name, owner = tag(node), self.parent.get(node)
        module = self.manifest['module']
        if name == 'title':
            return module + '/title' if owner is self.source else module + '/metadata/title' if tag(owner) == 'metadata' else owner.get('id') + '/title'
        if name == 'abstract':
            return module + '/metadata/abstract'
        if name == 'media':
            return node.get('id') + '/alt'
        if name == 'caption':
            return owner.get('id') + '/caption'
        if name == 'item':
            return owner.get('id') + '/item/' + str(list(owner).index(node) + 1)
        assert name == 'para'
        return node.get('id')

    def own_inline(self, node):
        for child in node:
            if tag(child) == 'list':
                continue
            yield child
            yield from self.own_inline(child)

    def translated(self, node):
        key = self.key(node)
        assert key not in self.used
        self.used.append(key)
        value = self.blocks[key]
        assert '__DRAFT_REQUIRED__' not in value
        if tag(node) == 'media':
            assert not any(c in value for c in '<>{}')
            return value
        groups = {'child': [c for c in node if tag(c) == 'list'],
                  'link': [c for c in self.own_inline(node) if tag(c) == 'link']}
        for kind, members in groups.items():
            assert re.findall(r'\{\{' + kind + r':(\d+)\}\}', value) == [str(i) for i in range(len(members))], key + ':' + kind

        def substitute(match):
            kind, index = match[1], int(match[2])
            original = groups[kind][index]
            if kind == 'child':
                return self.render(original)
            link_key = key + '/link/' + str(index)
            assert set(original.attrib) == {'target-id'}
            link_attrs = {**self.source_attrs(original), 'href': '#' + original.get('target-id'),
                          'data-source-link': link_key}
            return '<a' + attrs(link_attrs) + '>' + self.translation['source_link_labels'][link_key] + '</a>'

        expanded = re.sub(r'\{\{(child|link):(\d+)\}\}', substitute, value)
        assert '{{' not in expanded and '}}' not in expanded
        fragment = ET.fromstring('<fragment>' + expanded + '</fragment>')
        originals = [n for n in self.own_inline(node) if tag(n) in ('emphasis', 'newline')]
        slots = [n for n in fragment.iter() if n.tag in ('em', 'strong', 'br') and n.get('data-source-node') is None]
        assert len(originals) == len(slots), key + ':format count'
        for original, slot in zip(originals, slots):
            expected = 'br' if tag(original) == 'newline' else 'em' if original.get('effect') == 'italics' else 'strong'
            assert slot.tag == expected and not slot.attrib, key + ':source formatting'
            slot.attrib.update(self.source_attrs(original))
        return inner(fragment)

    def media(self, node):
        spec = self.manifest['images'][0]
        assert node.get('id') == spec['media_id']
        image = node[0]
        source_alt = self.translated(node)
        base = {**self.source_attrs(node), 'class': 'source-media', 'data-source-alt': source_alt,
                'data-component-status': spec['publication_status']}
        if self.unit == '010':
            assert hashlib.sha256((BASE / spec['path']).read_bytes()).hexdigest() == spec['sha256']
            image_attrs = {**self.source_attrs(image), 'src': '../' + spec['path'], 'alt': source_alt,
                           'data-source-key': self.key(node), 'width': spec['width'], 'height': spec['height'],
                           'style': f'--source-width:{spec["width"]}px',
                           'aria-describedby': 'preface-diagram-description preface-reflection-correction'}
            output = '<div class="figure-scroll" dir="ltr" tabindex="0" role="region" aria-label="اصل تصویر؛ تِن حصے ویکھن لئی پاسے سرکاؤ"><img' + attrs(image_attrs) + ' /></div>'
            output += '<p class="scroll-hint">پوری اصل تصویر دے تِن حصے ویکھن لئی پاسے سرکاؤ، یا <a href="../' + spec['path'] + '">اصل تصویر وکھری کھولو</a>۔</p>'
            output += '<p class="scroll-hint source-alt-advisory"><a href="#preface-diagram-description">ساڈی اصل تصویری وضاحت</a> تے <a href="#preface-reflection-correction">غلط چھپے نشان دی وکھری درستی</a> ویکھو۔</p>'
        else:
            assert spec['publication_status'] == 'quarantined-not-copied' and not (BASE / spec['path']).exists()
            image_attrs = {**self.source_attrs(image), 'class': 'source-image-unavailable',
                           'data-source-sha256': spec['sha256'], 'data-source-width': spec['width'],
                           'data-source-height': spec['height'], 'data-asset-coverage': 'incomplete'}
            output = '<div' + attrs(image_attrs) + '>' + self.translation['asset_unavailable_html']
            output += '<p class="component-reference" dir="ltr" lang="en">Source reference only: <bdi dir="ltr">' + html.escape(spec['source_path']) + '</bdi>; SHA-256 <bdi dir="ltr">' + spec['sha256'] + '</bdi>; <bdi dir="ltr">' + str(spec['width']) + '×' + str(spec['height']) + '</bdi>. Not included.</p></div>'
            output += '<p class="source-alt-text" data-source-key="' + self.key(node) + '">' + html.escape(source_alt) + '</p>'
        return '<div' + attrs(base) + '>' + output + '</div>'

    def render(self, node):
        name, a = tag(node), self.source_attrs(node)
        if name in ('document', 'metadata', 'content', 'section', 'list', 'figure'):
            out = {'document': 'div', 'metadata': 'div', 'content': 'div', 'section': 'section',
                   'list': 'ul', 'figure': 'figure'}[name]
            a['class'] = 'source-' + name
            if name == 'document':
                a['id'] = 'source-document'
            if name == 'list' and node.get('list-type') == 'enumerated':
                out = 'ol'
            return '<' + out + attrs(a) + '>' + ''.join(self.render(c) for c in node) + '</' + out + '>'
        if name in ('content-id', 'uuid'):
            assert not len(node)
            return '<p' + attrs({**a, 'class': 'metadata-value', 'dir': 'ltr'}) + '><bdi dir="ltr" lang="en">' + html.escape(node.text or '') + '</bdi></p>'
        if name == 'label' or (name == 'abstract' and not len(node) and not (node.text or '').strip()):
            assert not len(node) and not (node.text or '').strip()
            return '<span' + attrs({**a, 'class': 'source-empty-label' if name == 'label' else 'source-empty-abstract', 'data-source-empty': 'true'}) + '></span>'
        if name == 'media':
            return self.media(node)
        if name in ('title', 'para', 'item', 'caption', 'abstract'):
            a['data-source-key'] = self.key(node)
            if name == 'title':
                owner, depth = self.parent[node], 0
                cursor = owner
                while cursor is not self.source:
                    depth += tag(cursor) == 'section'
                    cursor = self.parent[cursor]
                out = 'h2' if owner is self.source else 'h' + str(min(6, max(3, depth + 1)))
            else:
                out = {'para': 'p', 'item': 'li', 'caption': 'figcaption', 'abstract': 'p'}[name]
            if name == 'para' and any(tag(c) == 'list' for c in node):
                out, a['class'] = 'div', 'source-para'
            return '<' + out + attrs(a) + '>' + self.translated(node) + '</' + out + '>'
        raise ValueError('Unsupported source element: ' + name)


def terminology_html():
    with (BASE / 'terminology.tsv').open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream, delimiter='\t'))
    output = '<section id="terminology"><h2>تِن زباناں دی سانجھی اصطلاحی کُنجی</h2><div class="table-scroll"><table><thead><tr><th scope="col">شاہ مکھی پنجابی</th><th scope="col" lang="ur-Arab-PK">اردو</th><th scope="col" lang="en" dir="ltr">English</th></tr></thead><tbody>'
    output += ''.join('<tr><td>' + html.escape(r['pnb-Arab-PK']) + '</td><td lang="ur-Arab-PK">' + html.escape(r['ur-Arab-PK']) + '</td><td lang="en" dir="ltr">' + html.escape(r['en']) + '</td></tr>' for r in rows)
    return output + '</tbody></table></div></section>'


def build(unit):
    prepare(unit, check_only=True)
    manifest = json.loads((BASE / f'source-excerpts/manifest-{unit}.json').read_text(encoding='utf-8'), object_pairs_hook=unique_object)
    translation = json.loads((BASE / f'translations/unit-{unit}.json').read_text(encoding='utf-8'), object_pairs_hook=unique_object)
    source = ET.parse(BASE / f'source-excerpts/unit-{unit}.cnxml').getroot()
    renderer = Renderer(unit, source, manifest, translation)
    body = renderer.render(source)
    assert set(renderer.used) == set(translation['source_blocks']) == set(manifest['source_block_keys'])
    assert len(renderer.used) == len(set(renderer.used)) == (98 if unit == '010' else 6)
    title, subtitle = html.escape(translation['title']), html.escape(translation['subtitle'])
    module = manifest['module']
    css = (BASE / 'styles/reader.css').read_text(encoding='utf-8') + UNIT_CSS
    source_url = manifest['upstream_url'] + '/blob/' + manifest['commit'] + '/' + manifest['path']
    result = '<!doctype html>\n<html lang="pnb-Arab-PK" dir="rtl"><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" /><title>' + title + ' — PNB-' + unit + '</title><style>' + css + '</style></head><body>'
    result += '<header><p class="eyebrow"><bdi dir="ltr">PNB-' + unit + ' · A30 / ' + module + '</bdi></p><h1>' + title + '</h1><p>' + subtitle + '</p><p class="status">ابتدائی ترجمہ · پنجابی دے ماہر دی لسانی جانچ ہن تک نہیں ہوئی</p><nav aria-label="سبق دے حصے"><a href="unit-009.html">مشقاں والا پچھلا ریڈر</a> · <a href="#source-document">پورا ماخذی متن</a> · <a href="#' + ('preface' if unit == '010' else 'introduction') + '-bridge">ساڈی اصل رہنمائی</a> · <a href="#credits">ماخذ تے سہرے</a></nav></header>'
    result += '<main>' + translation['bridge_before_html'] + '<p class="source-label">ماخذ دا ترجمہ: <bdi dir="ltr" lang="en">OpenStax Precalculus 2e — ' + ('Preface' if unit == '010' else 'Introduction to Functions') + '</bdi>۔</p>' + body + translation['bridge_after_html'] + terminology_html() + '</main>'
    result += '<footer id="credits" lang="en" dir="ltr"><h2>Sources, credits and changes</h2><p>Text adapted from <a href="' + source_url + '">OpenStax Precalculus 2e, module ' + module + '</a>, Jay Abramson et al., OpenStax / Rice University; foundational chapters credit David Lippman and Melonie Rasmussen. Text adaptation: <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a>. Contributor records remain in <a href="../provenance/ATTRIBUTION.md">the shared provenance record</a>; this unit retains its <a href="../provenance/unit-' + unit + '-component-notices.json">exact existing component notice</a>. OpenStax and Rice University do not endorse this adaptation.</p>'
    if unit == '010':
        result += '<p>Changes: complete 98-block Shahmukhi translation of the preface, including original metadata/abstract, all lists and post-list prose, nine contributing-author lines and 46 reviewer lines. All 55 source line breaks and 28 emphasis elements remain. The admitted 975×473 JPEG is unchanged: Copyright Rice University, OpenStax, under CC BY-NC-SA 4.0. The printed diagonal label x=1 is retained in the pixels and explicitly corrected to y=x only in a separately labeled original explanation. Original bilingual/accessibility support is not source prose.</p>'
    else:
        result += '<p>Changes: complete six-block Shahmukhi text/alt/caption translation, with original metadata, empty abstract and empty unnumbered-figure label preserved. The source JPEG is quarantined in the existing component record and is NOT copied, rendered, linked as an asset or exported. Its source node/reference/hash and named caption credits remain; a clearly original unavailable-component notice takes its place. Source credit \"bull\": modification of work by Prayitno Hadinata; source credit \"graph\": modification of work by MeasuringWorth. Image coverage remains incomplete pending coordinated permission or replacement. The text license is not asserted as permission for that excluded JPEG.</p>'
    result += '<p>Source order and all identifiers are retained; no MathML exists in this module. Plain source URLs remain plain text. Historical prices, biography, publication plans and resource claims are translated source statements, not current verification. Indonesian comparison: KokunoYumeto/openstax-precalculus-2e-id, alpha.58-reader.1; canonical commit ' + manifest['commit'] + '. No native-speaker, educator or assistive-technology certification is claimed. The full five-work assignment remains active; this reader is not a complete book or final release.</p></footer></body></html>\n'
    parsed = ET.fromstring(result[result.index('<html'):])
    identifiers = [n.get('id') for n in parsed.iter() if n.get('id')]
    assert len(identifiers) == len(set(identifiers))
    source_ids = [n.get('id') for n in source.iter() if n.get('id')]
    assert [sid for sid in identifiers if sid in source_ids] == source_ids
    assert [n.get('data-source-node') for n in parsed.iter() if n.get('data-source-node') is not None] == list(renderer.paths.values())
    reader = BASE / f'reader/unit-{unit}.html'
    for n in parsed.iter():
        for attribute in ('href', 'src'):
            if not n.get(attribute):
                continue
            address = urlsplit(n.get(attribute))
            if address.scheme or address.netloc:
                continue
            if address.path:
                path = (reader.parent / unquote(address.path)).resolve()
                assert path.is_relative_to(BASE.resolve()) and path.is_file()
            elif address.fragment:
                assert address.fragment in identifiers
    assert len(list(parsed.iter('img'))) == (1 if unit == '010' else 0)
    reader.write_text(result, encoding='utf-8', newline='\n')
    print(f'Built PNB-{unit}: {len(renderer.used)} blocks; image inclusion {"complete (1 unchanged)" if unit == "010" else "INCOMPLETE (quarantined; no image output)"}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unit', choices=['010', '011'], required=True)
    build(parser.parse_args().unit)
