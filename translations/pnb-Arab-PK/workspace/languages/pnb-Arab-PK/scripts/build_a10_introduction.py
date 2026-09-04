"""Deterministic complete m82451 reader, isolated from the A10 lesson builder."""
import html
import json
import re
import xml.etree.ElementTree as ET

from prepare_a10_introduction import (BASE, MANIFEST, TRANSLATION, EXCERPT, NOTICES,
    N, MD, SOURCE_KEYS, DEFAULT_CREDIT, load_inputs, notice_record, file_hash, require)

OUTPUT = BASE / 'reader/a10-introduction.html'
LOCAL_CSS = '''
.a10-introduction .source-label, .a10-introduction footer { overflow-wrap:anywhere; }
.a10-introduction .source-media { min-width:0; max-width:100%; }
.a10-introduction .source-media img { display:block; width:100%; max-width:975px; min-width:0; height:auto; padding:0; border:0; margin-inline:auto; }
.a10-introduction .bridge dl { display:grid; grid-template-columns:minmax(6rem,.65fr) minmax(0,1fr); gap:.4rem 1rem; }
.a10-introduction .bridge dt { font-weight:600; }
.a10-introduction .bridge dd { margin:0; overflow-wrap:anywhere; }
@media (max-width:600px) { .a10-introduction .bridge dl { display:block; } .a10-introduction .bridge dd { margin-block-end:.7rem; } }
'''


def esc(value):
    return html.escape(str(value), quote=True)


def build():
    m, t, source, prepared, credit_text = load_inputs()
    spec, original, target, data, row = prepared
    require(target.is_file() and file_hash(target) == spec['sha256'], 'Run prepare_a10_introduction.py first')
    require(NOTICES.is_file() and json.loads(NOTICES.read_text(encoding='utf-8')) == notice_record(m, prepared, credit_text),
            'Retained component notice missing or stale')
    blocks = t['source_blocks']
    require(list(blocks) == SOURCE_KEYS, 'Four translation keys must remain in source order')
    for key, value in blocks.items():
        require(not list(ET.fromstring('<fragment>'+value+'</fragment>')), 'Introduction source block gained unexpected markup: '+key)
        require(not re.search(r'[\u0a00-\u0a7f\ufffd\u061c\u200b\u200e\u200f\u202a-\u202e\u2066-\u2069]|\{\{', value), 'Invalid source script or placeholder')
    bridge = ET.fromstring(t['bridge_after_html'])
    require(bridge.get('id') == 'a10-introduction-bridge' and bridge.get('data-origin') == 'original-bridge', 'Original key must be separately labeled')
    css = (BASE/'styles/reader.css').read_text(encoding='utf-8') + LOCAL_CSS
    metadata = source.find(N+'metadata')
    meta_html = ''.join('<meta name="source-'+name+'" content="'+esc(metadata.find(MD+name).text or '')+'">'
                        for name in ('content-id','title','abstract','uuid'))
    source_url = m['upstream_url']+'/blob/'+m['commit']+'/'+m['path']
    preface_url = m['upstream_url']+'/blob/'+m['commit']+'/modules/m82630/index.cnxml'
    image_url = '../'+spec['path']
    result = f'''<!doctype html>
<html lang="pnb-Arab-PK" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Complete m82451 chapter introduction in Shahmukhi Punjabi; not a complete textbook">
<meta name="source-document-class" content="introduction">{meta_html}
<title>{esc(t['title'])} — A10 introduction</title><style>{css}</style></head>
<body class="a10-reader a10-introduction"><header><p class="eyebrow"><bdi dir="ltr">A10 / col31130 / m82451</bdi></p>
<p>{esc(t['subtitle'])}</p><p class="status">ابتدائی ترجمہ · پنجابی دے ماہر تے ریاضی دے استاد دی جانچ ہن تک نہیں ہوئی۔</p>
<nav aria-label="حصے"><a href="#a10-introduction-source">ماخذ دا ترجمہ</a> · <a href="#a10-introduction-bridge">لفظاں دی کُنجی</a> · <a href="#credits">ماخذ تے انتساب</a> · <a href="a10-unit-001.html">اگلے سبق دا شروع</a></nav></header>
<main><p class="source-label" data-origin="renderer-ui">ماخذ: <bdi dir="ltr" lang="en">OpenStax Elementary Algebra 2e</bdi>، باب <bdi dir="ltr" lang="en">Foundations</bdi>۔ ایتھے باب دی جان پہچان دا پورا ماڈیول <bdi dir="ltr">m82451</bdi> ترجمہ کیتا گیا اے؛ ایہہ پوری کتاب نہیں۔</p>
<article id="a10-introduction-source" data-source-tag="document" data-source-class="introduction" data-source-module="m82451"><h1 data-source-tag="title" data-source-key="m82451/title">{esc(blocks['m82451/title'])}</h1><section data-source-tag="content"><figure id="{spec['figure_id']}" class="splash" data-source-tag="figure"><div class="source-media"><div class="figure-scroll" dir="ltr"><img id="{spec['media_id']}" data-source-tag="media" data-source-key="{spec['media_id']}/alt" src="{esc(image_url)}" alt="{esc(blocks[spec['media_id']+'/alt'])}" width="975" height="450"></div><p class="scroll-hint" data-origin="renderer-ui">تصویر دے اصل سائز لئی <a href="{esc(image_url)}">اصل تصویر وکھری کھولو</a>۔</p></div><figcaption data-source-tag="caption" data-source-key="{spec['figure_id']}/caption">{esc(blocks[spec['figure_id']+'/caption'])}</figcaption></figure><p id="fs-id1170653837691" data-source-tag="para" data-source-key="fs-id1170653837691">{esc(blocks['fs-id1170653837691'])}</p></section></article>
{t['bridge_after_html']}
<p class="status" data-origin="renderer-ui">ایس کتاب دا دیباچہ <bdi dir="ltr">m82630</bdi> ہن تک ترجمہ نہیں ہویا۔ پنجاں مقررہ کتاباں دا پورا کم ہن وی جاری اے۔</p></main>
<footer id="credits" lang="en" dir="ltr"><h2>Sources, credits and changes — A10 introduction</h2>
<p>Adapted from <a href="{esc(source_url)}">OpenStax Elementary Algebra 2e, module m82451: Introduction</a>, collection col31130, Foundations. Original senior contributing authors: Lynn Marecek; MaryAnne Anthony-Smith; Andrea Honeycutt Mathis. Source publisher: OpenStax / Rice University.</p>
<p>The existing A10 notice states <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International</a>, subject to component-specific credits and restrictions. This adaptation retains that license framework and those restrictions. See the retained <a href="../provenance/A10-release/NOTICE.txt">A10 release notice</a>, <a href="../provenance/upstream--osbooks-prealgebra-bundle/LICENSE">canonical license text</a>, and <a href="../provenance/a10-introduction-component-notices.json">selected component evidence</a>. No new clearance is asserted.</p>
<p id="a10-introduction-art-credit">Raw-source default art credit: <span data-origin="retained-source-credit">{DEFAULT_CREDIT}</span> The <a href="{esc(preface_url)}">pinned raw preface, paragraph eip-787</a> supplies this wording for art without attribution in the text. No photographer is named in m82451. Book authors are not credited as photographers. The source statement and media identity evidence are retained, not independently verified as image-specific clearance; component-specific permissions and restrictions remain binding.</p>
<p>OpenStax and Rice University do not endorse this translation. Their names, logos and marks are not licensed by the source notice. The original splash photograph is unchanged and unmirrored, responsively displayed without cropping. No numbered figure label is invented. The caption and image description remain source-bound Punjabi translations.</p>
<p>Changes: complete translation of the four m82451 text blocks; RTL prose with an original, separately labeled Punjabi/Urdu/English word key. All three source IDs and full content order are preserved. Canonical metadata is retained as source metadata, including the original title; the translated visible title appears once. The frozen witness preserves the 1,066-byte canonical module plus one terminal LF, recorded separately in the manifest. No formula, exercise or source correction is added.</p>
<p>Indonesian comparison: <a href="https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id/releases/tag/v1.0.2">Elementary Algebra 2e Indonesian preservation release v1.0.2</a>. Its complete-book publication claim and process provenance describe that source release, not this local Punjabi reader. This Punjabi adaptation was produced with OpenAI Codex assistance at the user's direction; original human-contributor credits remain intact.</p>
<p>Coverage: complete m82451 title and content, not m82452 or the whole textbook. Preface m82630 remains untranslated. The complete A10, A20, A30, B10 and B40 workflow remains unfinished. This is not a training or fine-tuning dataset. Native-language, educator, assistive-technology and visual review remain separate. <a href="../source-excerpts/a10-introduction.cnxml">Frozen source witness</a> · <a href="../source-excerpts/manifest-a10-introduction.json">Exact source scope</a>.</p>
</footer></body></html>
'''
    # Parse an inspection copy without repairing hierarchy before writing HTML.
    inspection = re.sub(r'<(meta|img)\b([^<>]*?)(?<!/)>', lambda x: '<'+x[1]+x[2]+' />', result[result.index('<html'):])
    parsed = ET.fromstring(inspection)
    ids = [n.get('id') for n in parsed.iter() if n.get('id')]
    require(len(ids) == len(set(ids)), 'Duplicate reader ID')
    require([x for x in ids if x in m['source_ids_in_document_order']] == m['source_ids_in_document_order'], 'Source ID sequence changed')
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(result, encoding='utf-8', newline='\n')
    print('Built complete A10 introduction: 4 source blocks, 3 source IDs, 1 original splash photograph; whole assignment incomplete.')


if __name__ == '__main__':
    build()
