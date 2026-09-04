"""Deterministic A10-005 exercises/metadata/glossary reader; shared inputs read-only."""
import json
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from build_a10 import Reader as BaseReader, OutputIDs, LOCAL_CSS as BASE_LOCAL_CSS, attr
from prepare_a10_005 import BASE, ROOT, NOTICES, MATH, load_inputs, notice_record, file_hash, require, tag

ET.register_namespace('', MATH)
TRANSLATION = BASE / 'translations/a10-unit-005.json'
OUTPUT = BASE / 'reader/a10-unit-005.html'
LONG_PARTS = {'fs-id1170655207108', 'fs-id1170655207128'}
LOCAL_CSS = BASE_LOCAL_CSS + '''
.a10-005-reader .source-document, .a10-005-reader .source-content,
.a10-005-reader .source-block-container { min-width:0; max-width:100%; }
.a10-005-reader .source-exercise { margin-block:1.3rem; padding-block:0 .6rem; border-block-end:1px solid #cad7d1; }
.a10-005-reader .exercise-label { font-size:1.1rem; margin-block:1rem .2rem; }
.a10-005-reader .solution-label { font-size:.95rem; color:#1b6159; margin-block:.3rem; }
.a10-005-reader .source-inline-part { white-space:nowrap; margin-inline-end:.25rem; }
.a10-005-reader .source-para[data-long-source-part=true] { white-space:normal; }
.a10-005-reader .source-metadata { font-size:.87em; background:#f0f5f1; padding:.6rem 1rem; margin-block:1rem; overflow-wrap:anywhere; }
.a10-005-reader .source-retained-metadata { margin-block:.4rem; overflow-wrap:anywhere; }
.a10-005-reader .source-definition { margin-block:1.2rem; border-block-end:1px solid #cad7d1; }
.a10-005-reader .source-definition h3 { margin-block:.7rem .2rem; }
.a10-005-reader .source-original-advisory { font-size:.9rem; border-inline-start:3px solid #b98238; padding-inline-start:.7rem; }
.a10-005-reader .source-media .scroll-hint { direction:rtl; white-space:normal; text-align:start; }
'''


class Reader(BaseReader):
    def __init__(self, manifest, document, translation):
        super().__init__(manifest, document, translation)
        self.paths = {}
        def walk(node, path):
            self.paths[node] = path
            for index, child in enumerate(node):
                walk(child, path + '/' + str(index))
        walk(document, 'document')
        self.advisories = {}
        for record in translation['source_corrections']:
            for key in record['source_keys']:
                require(key in self.blocks, 'Unknown original advisory key')
                self.advisories.setdefault(key, []).append(record['note_id'])
        self.labels = {node.get('id'): str(index) for index, node in
                       enumerate((n for n in document.iter() if tag(n) == 'exercise'), 1)}

    def attrs(self, node):
        ident = ' id="' + attr(node.get('id')) + '"' if node.get('id') else ''
        return (ident + ' data-source-tag="' + tag(node) + '" data-source-path="' + self.paths[node]
                + '" data-source-qname="' + attr(node.tag) + '" data-source-attributes="'
                + attr(json.dumps(node.attrib, ensure_ascii=False, sort_keys=True, separators=(',', ':'))) + '"')

    def described(self, key):
        ids = self.advisories.get(key, [])
        return ' aria-describedby="' + attr(' '.join(ids)) + '"' if ids else ''

    def advisory(self, key):
        ids = self.advisories.get(key, [])
        if not ids:
            return ''
        links = '؛ '.join('<a href="#' + attr(i) + '">مترجم دی وکھری وضاحت</a>' for i in ids)
        return ('<p class="source-original-advisory" data-origin="renderer-ui" data-source-advisory-for="'
                + attr(key) + '">ایس ماخذی گل نال ' + links + ' وی پڑھو۔</p>')

    def translated(self, key, node):
        require(key in self.blocks and key not in self.used, 'Missing/repeated source key: ' + key)
        self.used.append(key)
        value = self.blocks[key]
        maths = [child for child in node if tag(child) == 'math']
        require([int(i) for i in re.findall(r'\{\{math:(\d+)\}\}', value)] == list(range(len(maths))),
                'Changed source mathematics placeholders: ' + key)
        require(not re.search(r'\{\{(?:link|child):', value), 'Unexpected block/link placeholder')
        require(len(re.findall(r'<br\s*/?>', value)) == sum(tag(c) == 'newline' for c in node),
                'Changed source newline count: ' + key)
        fragment = ET.fromstring('<fragment>' + value + '</fragment>')
        for effect, html_tag in [('bold', 'strong'), ('italics', 'em')]:
            require(sum(tag(c) == 'emphasis' and c.get('effect') == effect for c in node)
                    == len(list(fragment.iter(html_tag))), 'Changed emphasis: ' + key)
        tokens = [c for c in node if tag(c) == 'span' and c.get('class') == 'token']
        expected = [chr(ord('a') + ord(c.text) - ord('ⓐ')) for c in tokens]
        actual = [m[1] for m in re.finditer(r'<bdi\b[^>]*>\(([a-e])\)</bdi>', value)]
        require(actual == expected, 'Changed source part order: ' + key)
        value = re.sub(r'\{\{math:(\d+)\}\}', lambda m: self.math_html(maths[int(m[1])]), value)
        if tag(node) == 'para' and key not in LONG_PARTS:
            value = self.group_inline_parts(value, node)
        return value

    def children(self, node):
        require(not (node.text or '').strip(), 'Untranslated source container text')
        result = node.text or ''
        for index, child in enumerate(node):
            result += self.render(child, node, index)
            require(not (child.tail or '').strip(), 'Untranslated source container tail')
            result += child.tail or ''
        return result

    def render(self, node, parent=None, index=0):
        name, sid = tag(node), node.get('id')
        attrs = self.attrs(node)
        if name in {'document', 'metadata', 'abstract', 'content', 'section', 'exercise',
                    'problem', 'solution', 'glossary', 'definition'}:
            out_tag = 'section' if name in {'metadata', 'section', 'exercise', 'solution', 'glossary', 'definition'} else 'div'
            ui = ''
            if name == 'exercise':
                ui = ('<h3 class="exercise-label" data-origin="renderer-ui" data-exercise-label="'
                      + self.labels[sid] + '">مشق <bdi dir="ltr">' + self.labels[sid] + '</bdi></h3>')
            elif name == 'solution':
                ui = '<p class="solution-label" data-origin="renderer-ui">حل</p>'
            elif name == 'metadata':
                ui = '<h3 class="metadata-label" data-origin="renderer-ui">ماخذ دی پہچان تے سِکھن دے مقصد</h3>'
            elif name == 'glossary':
                ui = '<h2 class="glossary-label" data-origin="renderer-ui">اصطلاحاں دے مطلب</h2>'
            return ('<' + out_tag + attrs + ' class="source-' + name + '">' + ui
                    + self.children(node) + '</' + out_tag + '>')
        if name in {'content-id', 'uuid'}:
            require(not len(node), 'Unexpected metadata value children')
            label = 'ماخذ دے ماڈیول دی پہچان' if name == 'content-id' else 'ماخذ دی مستقل پہچان'
            return ('<p' + attrs + ' class="source-retained-metadata" aria-label="' + label
                    + '"><bdi dir="ltr" lang="en">' + attr(node.text or '') + '</bdi></p>')
        if name in {'para', 'title', 'item', 'term', 'meaning'}:
            if name == 'title':
                key = 'm82452/title' if tag(parent) == 'document' else 'm82452/metadata/title' if tag(parent) == 'metadata' else parent.get('id') + '/title'
            elif name == 'item':
                key = parent.get('id') + '/item/' + str(index + 1)
            elif name == 'term':
                key = parent.get('id') + '/term'
            else:
                key = sid
            out_tag = 'h2' if name == 'title' and tag(parent) in {'document', 'section'} else 'h3' if name in {'title', 'term'} else 'li' if name == 'item' else 'p'
            classes = ' class="source-para"' if name == 'para' else ''
            long = ' data-long-source-part="true"' if key in LONG_PARTS else ''
            html = ('<' + out_tag + attrs + ' data-source-key="' + attr(key) + '"' + classes + long
                    + self.described(key) + '>' + self.translated(key, node) + '</' + out_tag + '>')
            if key in self.advisories:
                html = ('<div class="source-block-container" data-source-block-owner="' + attr(key) + '">'
                        + html + self.advisory(key) + '</div>')
            return html
        if name == 'list':
            require(sid == 'list-00001' and len(node) == 3 and set(node.attrib) == {'id'},
                    'Unexpected objective-list structure')
            return '<ul' + attrs + ' class="source-objectives" role="list">' + self.children(node) + '</ul>'
        if name == 'media':
            key = sid + '/alt'
            require(key not in self.used and len(node) == 1 and tag(node[0]) == 'image', 'Changed media structure')
            self.used.append(key)
            child = node[0]
            spec = self.images[child.get('src')]
            require(sid == spec['media_id'] and not spec['figure_id'], 'Changed checklist ownership')
            source = '../' + spec['path']
            target = self.translation['retained_image_keys'][key]
            faithful = self.blocks[key]
            image = ('<img' + self.attrs(child) + ' data-source-key="' + attr(key) + '" src="' + attr(source)
                     + '" alt="' + attr(faithful) + '" data-source-alt="' + attr(faithful)
                     + '" data-description-origin="source-translation" data-source-image-mime="'
                     + attr(child.get('mime-type')) + '" data-rendered-image-mime="image/jpeg" width="'
                     + str(spec['width']) + '" height="' + str(spec['height']) + '" style="--source-width:'
                     + str(spec['width']) + 'px" aria-describedby="' + attr(target) + '" />')
            return ('<div' + attrs + ' class="source-media" data-source-child="' + sid + '">'
                    + (node.text or '') + '<div class="figure-scroll" dir="ltr" tabindex="0" role="region"'
                    + ' aria-label="اصل پرکھ فہرست؛ لوڑ پئے تے پاسے سرکاؤ">' + image + '</div>' + (child.tail or '')
                    + '<p class="scroll-hint" data-origin="renderer-ui" dir="rtl">چھوٹی سکرین اُتے پوری تصویر ویکھن لئی پاسے سرکاؤ، یا '
                    + '<a href="' + attr(source) + '">اصل تصویر وکھری کھولو</a>۔ '
                    + '<a href="#' + attr(target) + '">مترجم دی دو زبانی کنجی</a> وی ویکھو۔</p></div>')
        raise ValueError('Unsupported selected source element: ' + name)

    def bridges(self):
        results = []
        ids = []
        for field in ('bridge_before_html', 'bridge_after_html'):
            raw = self.translation[field]
            root = ET.fromstring(raw)
            require(root.tag == 'section' and root.get('data-origin') == 'original-bridge'
                    and root.get('class') == 'bridge', 'Unlabeled original bridge')
            ids.extend(n.get('id') for n in root.iter() if n.get('id'))
            results.append(raw)
        require(len(ids) == len(set(ids)), 'Duplicate original bridge ID')
        require(all(r['note_id'] in ids for r in self.translation['source_corrections']), 'Missing correction target')
        require(all(t in ids for t in self.translation['retained_image_keys'].values()), 'Missing imagekey target')
        return results


class LocalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []

    def handle_starttag(self, name, attrs):
        self.targets.extend(value for key, value in attrs if key in {'href', 'src'})


def build():
    manifest, document, prepared, notices = load_inputs()
    for spec, original, target, data, row, source_alt in prepared:
        require(target.is_file() and file_hash(target) == spec['sha256'], 'Run prepare_a10_005.py: image absent/changed')
    require(NOTICES.is_file() and json.loads(NOTICES.read_text(encoding='utf-8')) == notice_record(manifest, prepared, notices),
            'Run prepare_a10_005.py: component record absent/changed')
    require(file_hash(TRANSLATION) == manifest['translation_sha256']
            and TRANSLATION.stat().st_size == manifest['translation_bytes'], 'Frozen translation changed')
    raw = TRANSLATION.read_text(encoding='utf-8')
    translation = json.loads(raw)
    require((translation['unit'], translation['locale'], translation['module']) == ('A10-005', 'pnb-Arab-PK', 'm82452'),
            'Translation scope changed')
    require(list(translation['source_blocks']) == manifest['source_block_keys_in_document_order'], 'Source key order changed')
    require(translation['source_corrections'] == manifest['source_discrepancies']
            and not translation['image_alt_overrides'] and not translation['table_summary_overrides']
            and not translation['source_link_labels'], 'Original correction/override contract changed')
    require(not re.search('[\u0a00-\u0a7f\u202a-\u202e\u2066-\u2069\u200e\u200f\u061c\ufffd]', raw),
            'Disallowed script or bidi controls')
    reader = Reader(manifest, document, translation)
    source_body = reader.render(document)
    before, after = reader.bridges()
    require(reader.used == list(translation['source_blocks']) and len(reader.used) == 181, 'Changed rendered coverage')
    require(not re.search(r'\{\{[^}]+\}\}', source_body + before + after), 'Unresolved placeholder')
    css = (BASE / 'styles/reader.css').read_text(encoding='utf-8') + LOCAL_CSS
    source_url = manifest['upstream_url'] + '/blob/' + manifest['commit'] + '/' + manifest['path']
    result = f'''<!DOCTYPE html>
<html lang="pnb-Arab-PK" dir="rtl"><head><meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="description" content="Shahmukhi Punjabi Elementary Algebra 2e; A10-005 exercises,metadata and glossary; not a complete book" />
<title>{attr(translation['title'])} — A10-005</title><style>{css}</style></head>
<body class="a10-reader a10-005-reader"><header><p class="eyebrow"><bdi dir="ltr">A10-005 · A10 / col31130 / m82452</bdi></p>
<h1>{attr(translation['title'])}</h1><p>{attr(translation['subtitle'])}</p>
<p class="status">ابتدائی ترجمہ · پنجابی دے ماہر تے ریاضی دے استاد دی جانچ ہن تک نہیں ہوئی۔</p>
<nav aria-label="سبق دے حصے"><a href="a10-unit-004.html">پچھلا حصہ: اوّلی اجزا تے سانجھے مضاعف</a> · <a href="#fs-id1170655190123">مشقاں</a> · <a href="#fs-id1166426314283">اصطلاحاں</a> · <a href="#a10-005-original-bridge">مترجم دی وضاحت</a> · <a href="#credits">ماخذ تے انتساب</a></nav></header>
<main><p class="source-label" data-origin="renderer-ui">ماخذ: <bdi dir="ltr" lang="en">OpenStax Elementary Algebra 2e</bdi>، باب <bdi dir="ltr" lang="en">Foundations</bdi>، سبق «{attr(manifest['module_title_pnb'])}»۔ ایس قسط وچ سبق دیاں ساریاں مشقاں، کتاب وچ دِتے حل، اپنی پرکھ، اصطلاحاں تے ماڈیول دے مقصد تے پہچان نیں؛ پچھلا تدریسی متن الگ قسطاں وچ اے۔</p>
{before}{source_body}{after}
<p class="status" data-origin="renderer-ui">اگلا ماڈیول <bdi dir="ltr" lang="en">m82453</bdi> اے۔ پنجاں مقررہ کتاباں دا پورا کم ہن وی جاری اے؛ ایہہ پوری کتاب دے مکمل ترجمے دا دعویٰ نہیں۔</p></main>
<footer id="credits" lang="en" dir="ltr"><h2>Sources, credits and changes — A10-005</h2>
<p>Adapted from <a href="{attr(source_url)}">OpenStax Elementary Algebra 2e, module m82452: Introduction to Whole Numbers</a>, collection col31130, Foundations. Original senior contributing authors: Lynn Marecek; MaryAnne Anthony-Smith; Andrea Honeycutt Mathis. Source publisher: OpenStax / Rice University.</p>
<p>The existing A10 notice states <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International</a>, subject to component-specific credits and restrictions. This adaptation retains that license framework and those restrictions. See the retained <a href="../provenance/A10-release/NOTICE.txt">A10 release notice</a>, <a href="../provenance/upstream--osbooks-prealgebra-bundle/LICENSE">canonical license text</a>, and <a href="../provenance/a10-unit-005-component-notices.json">selected component evidence</a>. Media authority rows establish identity, not new image-specific clearance. No new clearance is asserted.</p>
<p>OpenStax and Rice University do not endorse this translation. Their names, logos and marks are not licensed by the source notice. No cover or added logo is reproduced. The original English checklist JPEG is unchanged and unmirrored; its declared image/jpeg type agrees with its original bytes. The image remains unnumbered. Its four-column layout and nine blank assessment cells are retained; this static image is not a working web form.</p>
<p>Changes: Shahmukhi Punjabi translation of 181 source text blocks; RTL prose with LTR mathematics, numbers, English and original geometry. All 383 original IDs, 82 exercises, 41 supplied solutions, 11 glossary definitions, the complete original title/metadata including content-id and UUID, twelve exact MathML trees, eleven bold/two italic emphases, 116 source part labels and five explicit source newlines are retained. Short parts are grouped for readability; two long self-check parts wrap normally. Source solutions are neither invented nor removed. Both supplied Answers may vary replies remain open-ended. Local exercise numbers 1–82 and solution/metadata/glossary labels are original reader UI, not additional source titles.</p>
<p>Original keys, scope qualifications and contextual notes are visibly labeled and bound to their source owners. Source glossary shorthand remains faithful: the original composite-number omission and other domain conventions are explained separately, not silently repaired. Source MathML retains English and; the separate key explains it. Dated population/average-distance values are exercise givens, not updated factual claims. USD currency and source three-digit grouping remain unchanged; the population date moves within the Punjabi sentence without changing its value. No new practice or unsupplied source answer is added.</p>
<p>Indonesian comparison: <a href="https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id/releases/tag/v1.0.2">Elementary Algebra 2e Indonesian preservation release v1.0.2</a>. Its 82-module release and OpenAI Codex process provenance do not imply equivalent Punjabi coverage. This adaptation was produced with OpenAI Codex assistance at the user's direction; original human-contributor credits remain intact.</p>
<p>Coverage: complete final content section fs-id1170655190123, through self-check paragraph fs-id1170655207150; full trailing glossary through fs-id1166424132616; original root title and complete metadata. Earlier A10-001–004 readers supply previous instructional source. This file is not a standalone full-module translation, a complete textbook or a completed five-work assignment, and is not training or fine-tuning data. Complete-module source-union/workflow review is separate. Native-language, educator and assistive-technology review remain pending. <a href="../source-excerpts/a10-unit-005.cnxml">Frozen source witness</a> · <a href="../source-excerpts/manifest-a10-005.json">Exact source selection</a> · <a href="../qa/a10-unit-005-language-notes.md">Source and language notes</a>.</p>
</footer></body></html>
'''
    # Well-formed source fragments also produce a directly inspectable full document.
    ET.fromstring(result)
    ids = OutputIDs()
    ids.feed(result)
    require(len(ids.ids) == len(set(ids.ids)), 'Duplicate rendered ID')
    expected = manifest['source_ids_in_document_order']
    require([i for i in ids.ids if i in set(expected)] == expected, 'Rendered source ID order changed')
    links = LocalLinks()
    links.feed(result)
    for target in links.targets:
        url = urlsplit(target)
        if url.scheme or url.netloc:
            require(url.scheme in {'http', 'https'}, 'Non-web external reference')
            continue
        if url.path:
            path = (OUTPUT.parent / unquote(url.path)).resolve()
            require(path.is_relative_to(BASE.resolve()) and path.is_file(), 'Missing/unsafe local file: ' + target)
            if url.fragment:
                other = OutputIDs()
                other.feed(path.read_text(encoding='utf-8'))
                require(unquote(url.fragment) in other.ids, 'Missing cross-unit fragment')
        else:
            require(unquote(url.fragment) in ids.ids, 'Missing local fragment')
    OUTPUT.write_text(result, encoding='utf-8', newline='\n')
    print('Built A10-005:181blocks,383IDs,82exercises/41solutions,11definitions,12MathML,116parts,5breaks,1originalJPEG.')


if __name__ == '__main__':
    build()
