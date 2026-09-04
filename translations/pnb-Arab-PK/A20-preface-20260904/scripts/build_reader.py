"""Build only recovered OpenStax col31234/m81357, independent of other books."""
from pathlib import Path
import hashlib
import html
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
N = '{http://cnx.rice.edu/cnxml}'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write_json(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def main():
    manifest = json.loads((ROOT / 'source/recovered-manifest.json').read_text(encoding='utf-8'))
    original = ROOT / 'source/recovered-translation.json'
    target = json.loads(original.read_text(encoding='utf-8'))
    correction = json.loads((ROOT / 'source/corrections.json').read_text(encoding='utf-8'))
    for item in correction['corrections']:
        field = item['field']
        assert target[field].count(item['before']) == 1
        target[field] = target[field].replace(item['before'], item['after'])
    write_json(ROOT / 'source/a20-preface.translation.json', target)
    source_path = ROOT / 'source/a20-preface.cnxml'
    assert sha(source_path) == 'f4d01bced59370e726f637a3d5b846ad77aa3536dba5a838cb00ceeadebd3033'
    source = ET.parse(source_path).getroot()
    images = {i['media_id']: i for i in manifest['images']}
    used = []

    def block(key):
        assert key not in used
        used.append(key)
        return target['source_blocks'][key]

    def render(node, depth=0, parent=None):
        tag = node.tag.removeprefix(N)
        ident = node.get('id')
        attrs = f' data-source-tag="{tag}"'
        if ident:
            attrs += f' id="{ident}"'
        if node.get('class'):
            attrs += f' data-source-class="{node.get("class")}"'
        if tag == 'title':
            key = (parent.get('id') or 'm81357') + '/title'
            return f'<h{depth+1}{attrs} data-source-key="{key}">{block(key)}</h{depth+1}>'
        if tag == 'media':
            im = images[ident]
            asset = ROOT / im['path']
            assert asset.stat().st_size == im['bytes'] and sha(asset) == im['sha256']
            alt = block(ident + '/alt')
            note = target['image_alt_note_ids'][ident]
            image = (f'<img{attrs} data-source-key="{ident}/alt" src="{im["path"]}" '
                     f'width="{im["width"]}" height="{im["height"]}" lang="pnb-Arab-PK" dir="rtl" '
                     f'alt="{html.escape(target["image_alt_overrides"][ident], quote=True)}" '
                     f'data-source-alt="{html.escape(alt, quote=True)}" aria-describedby="{note}">')
            advisory = f'<a class="alt-advisory" href="#{note}" data-origin="renderer-ui">تصویری وضاحت دا نوٹ</a>'
            if im['parent_tag'] == 'para':
                return f'<span class="inline-source-media">{image}{advisory}</span>'
            return ('<div class="source-media"><div class="figure-scroll" dir="ltr" '
                    'role="region" aria-label="تِن محوری گراف" tabindex="0">' + image +
                    f'</div><p class="scroll-hint">{advisory} · <a href="{im["path"]}">اصل تصویر</a></p></div>')
        if tag in ('para', 'item'):
            key = ident if tag == 'para' else parent.get('id') + '/item/' + str(list(parent).index(node) + 1)
            value = block(key)
            for index, child in enumerate(node.findall(N + 'media')):
                token = '{{child:' + str(index) + '}}'
                assert value.count(token) == 1
                value = value.replace(token, render(child))
            assert '{{child:' not in value
            out_tag = 'p' if tag == 'para' else 'li'
            return f'<{out_tag}{attrs} data-source-key="{key}">{value}</{out_tag}>'
        if tag in ('content', 'section', 'list'):
            out_tag = 'ul' if tag == 'list' else 'section'
            if tag == 'list':
                attrs += f' data-source-list-type="{node.get("list-type", "unspecified")}" data-source-bullet-style="{node.get("bullet-style", "unspecified")}"'
                if node.get('bullet-style') == 'none':
                    attrs += ' class="source-list-no-bullets"'
            return f'<{out_tag}{attrs}>' + ''.join(render(c, depth+(tag == 'section'), node) for c in node) + f'</{out_tag}>'
        raise ValueError(tag)

    source_html = render(source.find(N+'title'), parent=source) + render(source.find(N+'content'))
    assert used == manifest['source_text_keys_in_order']
    before = target['bridge_before_html'].replace(' — ', ' - ')
    after = target['bridge_after_html'].replace(' — ', ' - ')
    toc = '<nav aria-label="حصے"><a href="#a20-preface-source">ماخذ دا ترجمہ</a> · <a href="#a20-preface-bridge">لفظاں دی کُنجی</a> · <a href="#credits">انتساب</a></nav>'
    out = f'''<!doctype html>
<html lang="pnb-Arab-PK" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Recovered complete preface only: OpenStax Intermediate Algebra 2e in Shahmukhi Punjabi, module m81357."><meta name="source-module" content="m81357"><meta name="source-uuid" content="8299e5c9-9342-4802-96c4-5c9cc0b69482"><meta name="generator" content="OpenAI Codex gpt-5.6-sol, Ultra"><title>دیباچہ | Intermediate Algebra 2e | Shahmukhi Punjabi</title><link rel="stylesheet" href="styles/reader.css"></head>
<body><header><p class="eyebrow"><bdi dir="ltr" lang="en">OpenStax Intermediate Algebra 2e</bdi></p><p class="book-title">درمیانے درجے دا الجبرا: دیباچہ</p><p>{target['subtitle']}</p><p class="status">صرف پورا دیباچہ <bdi dir="ltr">m81357</bdi>۔ ایہہ باباں یا پوری کتاب دا ترجمہ نہیں۔</p><p class="formats"><a href="output/pdf/a20-preface-shahmukhi.pdf"><bdi dir="ltr" lang="en">PDF</bdi> کھولو</a></p>{toc}</header>
<main>{before}<article id="a20-preface-source" data-source-tag="document" data-source-module="m81357" data-source-class="preface">{source_html}</article>{after}
<aside class="bridge" data-origin="original-recovery-note"><h2>ایس پیکیج دی حد</h2><p>دیباچے وچ باباں، مشقاں تے جواباں دا ذکر اصل پوری کتاب بارے اے۔ اوہ باب، سوال تے جواب ایس پیکیج وچ شامل نہیں۔ اگلا ماخذ حصہ <bdi dir="ltr">m81358</bdi> دا تعارف اے؛ اوہدا ترجمہ ایتھے شامل نہیں۔</p><p>ایہہ کم شاہ مکھی پنجابی وچ پڑھائی نوں ثانوی درجے توں یونیورسٹی دے ابتدائی درجے تک اردو تے انگریزی نال جوڑن لئی اے۔ اردو تے انگریزی صرف وکھرے دِتے لفظی پُل نیں؛ اوہ پنجابی دی جگہ نہیں لیندیاں۔</p><p>ماخذ نال میل، تصویر، حروف تے صفحہ بندی دی جانچ کیتی گئی اے۔ ایہہ پنجابی دے ہر ماہر یا ریاضی دے ہر استاد دی مشترک اصطلاحی منظوری دا دعویٰ نہیں۔</p></aside></main>
<footer id="credits" lang="en" dir="ltr"><h2>Sources, credits, scope and changes</h2><p>Complete preface only: OpenStax <em>Intermediate Algebra 2e</em>, collection col31234, module m81357, source UUID 8299e5c9-9342-4802-96c4-5c9cc0b69482. This is a bounded recovered edition, not a complete textbook or chapter.</p><p>Senior contributing authors: Lynn Marecek and Andrea Honeycutt Mathis. All source affiliations and 16 reviewer lines are retained above. Source publisher: OpenStax / Rice University. OpenStax and Rice University do not endorse this translation.</p><p>Source: <a href="https://github.com/openstax/osbooks-prealgebra-bundle/blob/38cae454e644abf9f0a623e876994553881597c9/modules/m81357/index.cnxml">official CNXML at commit 38cae454e644abf9f0a623e876994553881597c9</a>. Recovered translation and style derive from <a href="https://github.com/KokunoYumeto/allocating-ai-translation-compute-for-educational-access/tree/ed6f2e2020118723c2a12fe3377d2273c3d8ec50/translations/pnb-Arab-PK">immutable public recovery intake</a>. The historical Indonesian checkpoint remains a comparison witness only; no change to the completed Indonesian edition is implied.</p><p>License: <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a>, subject to component-specific notices. Default source art credit: Copyright Rice University, OpenStax, under CC BY-NC-SA 4.0 license. All four source images are unchanged and unmirrored. Fonts retain their separate <a href="assets/fonts/OFL.txt">SIL Open Font License 1.1</a>. Names and marks are not licensed. See <a href="LICENSE.txt">LICENSE.txt</a>.</p><p>Recovered source translation: 89 text owners, 66 source IDs, 26 sections, 33 paragraphs, 25 list items, 27 explicit line breaks and four image alternatives. There are no source equations, exercises or solutions in this preface. The source outline describes later chapters; it does not establish that those chapters have been translated.</p><p>Recovery changes: reader-first cover and honest scope; standalone offline font-backed HTML; tagged browser-generated PDF; deterministic source/asset/DOM checks; and one separately recorded Urdu-bridge correction from the two-digit wording to the two-term wording for binomial theorem. The 89 faithful source blocks remain byte-identical. Source discrepancies and original bridges remain visibly separate.</p><p>Produced with OpenAI Codex assistance at the user's direction. Recovery model identification: OpenAI Codex gpt-5.6-sol, Ultra. Preserved human author/contributor credits are not replaced by model credit. Language canon: 12 short prose loci from three essays by Jamil Ahmad Pal, preserved as narrow register evidence, not mathematical terminology certification.</p><p>Next source anchor: m81358 (Introduction); not translated in this package. The wider A10/A20/A30/discrete/linear-algebra programme remains future scope governed by its book owners. No acquired source or another locale receives translation credit here. HTML is the primary semantic reader; PDF tagging and extraction checks are not a claim of PDF/UA certification or tested screen-reader pronunciation.</p></footer></body></html>'''
    (ROOT / 'index.html').write_text(out, encoding='utf-8', newline='\n')
    print(json.dumps({'html':'index.html','source_owners':len(used),'source_sha256':sha(source_path),'html_sha256':sha(ROOT/'index.html')}))


if __name__ == '__main__':
    main()
