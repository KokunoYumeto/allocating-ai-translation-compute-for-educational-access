"""Dependency-free, deterministic RTL reader from a frozen CNXML excerpt."""
from pathlib import Path
import copy
import csv
import html
import json
import re
import xml.etree.ElementTree as ET
import argparse
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

BASE = Path(__file__).resolve().parents[1]
MATH = "http://www.w3.org/1998/Math/MathML"
ET.register_namespace("", MATH)
parser = argparse.ArgumentParser()
parser.add_argument('--unit', choices=['001','002','003','004','005','006','007','008'], default='001')
args = parser.parse_args()
unit = args.unit
manifest = json.loads((BASE/'source-excerpts'/('manifest.json' if unit == '001' else f'manifest-{unit}.json')).read_text(encoding='utf-8'))
doc = ET.parse(BASE / 'source-excerpts' / manifest.get('source_excerpt','m49301-opening.cnxml')).getroot()
translation = json.loads((BASE / f'translations/unit-{unit}.json').read_text(encoding='utf-8'))
blocks = translation["source_blocks"]
used = set()
footnotes = []
used_link_labels = set()
figure_labels = {'Figure_01_01_001':'1.1.1'} if unit == '001' else {e['figure_id']:e['local_label'] for e in manifest.get('images',[]) if 'figure_id' in e}
reference_labels = {**figure_labels, **{e['id']:e['local_label'] for e in manifest.get('references',[])}}
reference_specs = {e['id']:e for e in manifest.get('references',[])}
image_specs = {'CNX_Precalc_Figure_01_01_001.jpg':{'path':'assets/Figure_01_01_001.jpg','width':943,'height':284}} if unit == '001' else {e['source_path'].split('/')[-1]:e for e in manifest.get('images',[])}
BLOCKS = {'figure','para','note','list','exercise','problem','solution','section','equation','example','table','footnote'}
if unit == '008':
    BLOCKS.add('media')

def tag(node):
    return node.tag.rsplit("}", 1)[-1]

def math_html(node, owner_key=None, math_index=None):
    clone = copy.deepcopy(node)
    clone.tail = None
    clone.set("dir", "ltr")
    # Source embeds English sentence punctuation in MathML. Keep the source
    # witness intact, but relocate only terminal sentence dots/commas into the
    # translated prose. Mathematical commas inside sets/pairs are untouched.
    if unit in ('004', '005', '006', '007', '008'):
        leaves = []
        def visit(element,path):
            if not len(element):
                leaves.append((element,path))
            for i,child in enumerate(element):
                visit(child,path+[i])
        visit(clone,[])
        edits = []
        def edit(element,path,new):
            edits.append({'path':path,'old':element.text,'new':new})
            element.text = new
        if unit != '008' and leaves and tag(leaves[0][0]) in ('mo','mtext') and leaves[0][0].text in ('“','”'):
            edit(*leaves[0],'')
        for element,path in reversed(leaves):
            element_tag = tag(element)
            if element_tag in ('mo','mtext') and element.text in ('.',',','“','”') and (unit != '008' or element_tag == 'mo' and element.text in ('.', ',')):
                edit(element,path,'')
            elif unit != '008' and element_tag == 'mo' and element.text == '),':
                edit(element,path,')')
                break
            elif unit == '006' and element_tag == 'mn' and re.fullmatch(r'\d+\.', element.text or ''):
                edit(element,path,element.text[:-1])
                break
            elif unit == '007' and element_tag in ('mn', 'mtext') and re.fullmatch(r'\d+[.,:]', element.text or ''):
                edit(element,path,element.text[:-1])
                break
            elif unit == '008' and (owner_key, math_index, element_tag, element.text) == ('fs-id1165137637786', 9, 'mn', '1.'):
                edit(element,path,'1')
                break
            elif unit == '008' and (owner_key, math_index, element_tag, element.text) == ('fs-id1165137761111', 0, 'mo', '?'):
                edit(element,path,'')
                break
            else:
                break
        if edits:
            clone.set('data-source-text-edits',json.dumps(edits,ensure_ascii=False,separators=(',',':')))
    last = clone
    while len(last):
        last = last[-1]
    if unit not in ('004', '005', '006', '007', '008') and tag(last) == 'mo' and last.text in ('.', ','):
        parents = {c:p for p in clone.iter() for c in p}
        clone.set('data-source-punctuation', last.text)
        parents[last].remove(last)
    focus = ' tabindex="0" role="region" aria-label="ریاضی دا فارمولا؛ لوڑ پئے تے پاسے سرکاؤ"' if node.get('display') == 'block' else ''
    return '<span class="math-isolate" dir="ltr"' + focus + '>' + ET.tostring(clone, encoding="unicode") + '</span>'

def translated(key, node):
    used.add(key)
    value = blocks[key]
    def own_maths(element):
        for child in element:
            if tag(child) == 'math':
                yield child
            elif tag(child) not in BLOCKS:
                yield from own_maths(child)
    maths = list(own_maths(node))
    indexes = [int(i) for i in re.findall(r"\{\{math:(\d+)\}\}", value)]
    if indexes != list(range(len(maths))):
        raise ValueError(f"Changed math count/order in {key}: {indexes}")
    value = re.sub(r"\{\{math:(\d+)\}\}", lambda m: math_html(maths[int(m[1])], key, int(m[1])), value)
    children = [c for c in node if tag(c) in BLOCKS]
    positions = [int(i) for i in re.findall(r'\{\{child:(\d+)\}\}',value)]
    if positions != list(range(len(children))):
        raise ValueError(f'Changed block-child count/order in {key}: {positions}')
    value = re.sub(r'\{\{child:(\d+)\}\}',lambda m: render(children[int(m[1])],node),value)
    links = [c for c in node if tag(c) == 'link']
    positions = [int(i) for i in re.findall(r'\{\{link:(\d+)\}\}',value)]
    if unit != '001' and positions != list(range(len(links))):
        raise ValueError(f'Changed link count/order in {key}: {positions}')
    def source_link(match):
        link_index = int(match[1])
        link = links[link_index]
        target = link.get('target-id')
        if unit == '008':
            link_key = f'{key}/link/{link_index}'
            marker = f' data-source-link="{html.escape(link_key, quote=True)}"'
            if link.get('url'):
                label = translation['source_link_labels'][link_key]
                used_link_labels.add(link_key)
                return f'<a{marker} href="{html.escape(link.get("url"), quote=True)}">{html.escape(label)}</a>'
            spec = reference_specs[target]
            noun = {'table':'جدول', 'figure':'شکل', 'example':'مثال'}[spec['kind']]
            return f'<a{marker} href="{html.escape(spec["href"], quote=True)}">{noun} <bdi dir="ltr">{html.escape(spec["local_label"])}</bdi></a>'
        label = reference_labels[target]
        noun = 'جدول' if target.startswith('Table_') else 'شکل'
        return f'<a href="#{target}">{noun} <bdi dir="ltr">{label}</bdi></a>'
    return re.sub(r'\{\{link:(\d+)\}\}',source_link,value)

def toolkit_table(node):
    """PNB008 CALS tables: preserve real groups/spans and direct media cells."""
    sid = node.get('id')
    summary_key = sid + '/summary'
    used.add(summary_key)
    original_summary = blocks[summary_key]
    summary = translation.get('table_summary_overrides', {}).get(sid, original_summary)
    attributes = f' id="{sid}" dir="ltr" class="source-table" aria-label="{html.escape(summary, quote=True)}" data-source-summary="{html.escape(original_summary, quote=True)}"'
    advisory = ''
    if sid in translation.get('table_summary_overrides', {}):
        attributes += ' aria-describedby="toolkit-table-summary" data-description-origin="original-correction"'
        advisory = '<p class="scroll-hint source-summary-advisory">ایس جدول دے ماخذی خلاصے بارے <a href="#toolkit-table-summary">ساڈی وکھری درستی تے وضاحت وی ویکھو</a>۔</p>'
    if any(tag(c) == 'label' for c in node):
        assert all(not len(c) and not (c.text or '').strip() for c in node if tag(c) == 'label')
        attributes += ' data-source-empty-label="true"'
    if node.get('class'):
        attributes += f' data-source-class="{html.escape(node.get("class"), quote=True)}"'
    group = next(c for c in node if tag(c) == 'tgroup')
    columns = [c for c in group if tag(c) == 'colspec']
    column_names = {c.get('colname'):i for i,c in enumerate(columns)}
    width = int(group.get('cols'))
    assert len(columns) == width
    attributes += f' data-source-tgroup-cols="{width}"'
    colgroup = '<colgroup>' + ''.join('<col' + ''.join(f' data-source-{k}="{html.escape(v, quote=True)}"' for k,v in c.attrib.items()) + ' />' for c in columns) + '</colgroup>'
    content = ''
    row_index = 0
    for section in [c for c in group if tag(c) in ('thead','tbody')]:
        section_name = tag(section)
        content += f'<{section_name}>'
        for row in section:
            row_index += 1
            cells, occupied = '', 0
            for column_index, entry in enumerate(row, 1):
                key = f'{sid}/row/{row_index}/entry/{column_index}'
                span = 1
                if entry.get('namest') or entry.get('nameend'):
                    assert entry.get('namest') in column_names and entry.get('nameend') in column_names
                    assert column_names[entry.get('namest')] == occupied
                    span = column_names[entry.get('nameend')] - occupied + 1
                    assert span > 0
                occupied += span
                keyed = key in blocks
                is_header = section_name == 'thead' or keyed and key not in translation.get('translated_table_data_cells', [])
                out_tag = 'th' if is_header else 'td'
                attrs = f' data-source-key="{key}"' if keyed else ''
                if is_header:
                    scope = ('colgroup' if span > 1 else 'col') if section_name == 'thead' else 'row'
                    attrs += f' scope="{scope}"'
                if span > 1:
                    attrs += f' colspan="{span}"'
                for attribute in ('namest','nameend','align'):
                    if entry.get(attribute):
                        attrs += f' data-source-{attribute}="{html.escape(entry.get(attribute), quote=True)}"'
                if entry.get('align') == 'center':
                    attrs += ' style="text-align:center"'
                if keyed:
                    attrs += ' dir="rtl"'
                    value = translated(key,entry)
                elif len(entry):
                    assert all(tag(c) == 'media' and not (c.tail or '').strip() for c in entry) and not (entry.text or '').strip()
                    attrs += ' dir="ltr"'
                    value = ''.join(render(c,entry,i) for i,c in enumerate(entry))
                else:
                    raw = (entry.text or '').strip()
                    attrs += ' dir="ltr"' + (' lang="en"' if re.search('[A-Za-z]',raw) else '')
                    value = html.escape(raw)
                cells += f'<{out_tag}{attrs}>{value}</{out_tag}>'
            assert occupied == width, f'Invalid CALS row width: {sid}/{row_index}'
            row_attrs = f' data-source-valign="{row.get("valign")}"' if row.get('valign') else ''
            content += f'<tr{row_attrs}>' + cells + '</tr>'
        content += f'</{section_name}>'
    return f'<div class="source-table-container" data-source-child="{sid}"><div class="table-scroll source-table-scroll" dir="ltr" tabindex="0" role="region" aria-label="جدول؛ لوڑ پئے تے پاسے سرکاؤ"><table{attributes}>{colgroup}{content}</table></div>{advisory}</div>'

def render(node, parent=None, index=0):
    name = tag(node)
    sid = node.get("id")
    ident = f' id="{sid}"' if sid else ""
    if name == "document":
        return ''.join(render(c, node, i) for i, c in enumerate(node))
    if name == "section":
        return f'<section{ident} class="translated">' + ''.join(render(c, node, i) for i, c in enumerate(node)) + '</section>'
    if name in ('example','exercise','problem','solution','commentary'):
        out_tag = 'section' if name in ('example','solution') else 'div'
        number = int(sid.rsplit('_',1)[-1]) if name == 'example' else None
        heading = f'<h2>حل کیتی مثال <bdi dir="ltr">{number}</bdi></h2>' if name == 'example' else '<h3>حل</h3>' if name == 'solution' else ''
        return f'<{out_tag}{ident} class="source-{name}">' + heading + ''.join(render(c,node,i) for i,c in enumerate(node)) + f'</{out_tag}>'
    if name in ("para", "title", "label", "caption", "item"):
        if name == "item":
            key = f'{parent.get("id")}/item/{index + 1}'
        else:
            key = sid or f'{parent.get("id")}/{name}'
        out_tag = {"para": "p", "title": "h2" if tag(parent) == "section" else "h3", "label": "h3", "caption": "figcaption", "item": "li"}[name]
        return f'<{out_tag}{ident}>' + translated(key, node) + f'</{out_tag}>'
    if name == "equation":
        return f'<div{ident} class="equation" dir="ltr">' + ''.join(math_html(c) for c in node if tag(c) == "math") + '</div>'
    if name == 'footnote':
        footnotes.append((sid,translated(sid,node)))
        return f'<sup{ident} class="source-footnote"><a href="#{sid}-text" aria-label="ماخذ دا حوالہ {len(footnotes)}"><bdi dir="ltr">{len(footnotes)}</bdi></a></sup>'
    if name == 'table':
        if unit == '008':
            return toolkit_table(node)
        summary_key = sid+'/summary'
        used.add(summary_key)
        original_summary = blocks[summary_key]
        summary = translation.get('table_summary_overrides',{}).get(sid,original_summary)
        attributes = f' aria-label="{html.escape(summary,quote=True)}" data-source-summary="{html.escape(original_summary,quote=True)}"'
        rows = [e for e in node.iter() if tag(e) == 'row']
        group = next(e for e in node if tag(e) == 'tgroup')
        row_parents = {c:p for p in node.iter() for c in p}
        content = ''
        for row_index,row in enumerate(rows,1):
            cells = ''
            for column_index,entry in enumerate(row,1):
                key = f'{sid}/row/{row_index}/entry/{column_index}'
                is_translated = key in blocks
                is_header = is_translated and key not in translation.get('translated_table_data_cells', [])
                out_tag = 'th' if is_header else 'td'
                scope = ('col' if tag(row_parents[row]) == 'thead' else 'row') if is_header else ''
                if is_translated:
                    value = translated(key,entry)
                    attrs = f' dir="rtl" scope="{scope}"' if is_header else ' dir="rtl"'
                else:
                    raw = ''.join(entry.itertext()).strip()
                    value = html.escape(raw)
                    attrs = ' dir="ltr" lang="en"' if re.search('[A-Za-z]',raw) else ' dir="ltr"'
                if entry.get('align') == 'center':
                    attrs += ' style="text-align:center"'
                cells += f'<{out_tag}{attrs}>{value}</{out_tag}>'
            content += '<tr>'+cells+'</tr>'
        assert all(len(row) == int(group.get('cols')) for row in rows), f'Unsupported spanned CALS table: {sid}'
        return f'<div class="table-scroll source-table-scroll" dir="ltr" tabindex="0" role="region" aria-label="جدول؛ لوڑ پئے تے پاسے سرکاؤ"><table{ident}{attributes} dir="ltr" class="source-table"><tbody>{content}</tbody></table></div>'
    if name == "figure":
        return f'<figure{ident}>' + ''.join(render(c, node, i) for i, c in enumerate(node)) + '</figure>'
    if name == "media":
        altkey = sid + "/alt"
        used.add(altkey)
        image_node = next(c for c in node if tag(c) == 'image')
        spec = image_specs[image_node.get('src').split('/')[-1]]
        src = '../'+spec['path']
        alt = blocks[altkey]
        alt_attrs = ''
        advisory = ''
        if sid in translation.get('image_alt_overrides', {}):
            alt = translation['image_alt_overrides'][sid]
            note_id = translation['image_alt_note_ids'][sid]
            alt_attrs = f' data-source-alt="{html.escape(blocks[altkey], quote=True)}" aria-describedby="{html.escape(note_id, quote=True)}"'
            if unit == '008':
                alt_attrs += ' data-description-origin="original-accessibility-addition"'
            advisory = f'<p class="scroll-hint source-alt-advisory">ایس شکل دے ماخذ والے متبادل متن بارے <a href="#{html.escape(note_id, quote=True)}">ساڈی وکھری درستی تے وضاحت وی ویکھو</a>۔</p>'
        media_html = '<div class="figure-scroll" dir="ltr" tabindex="0" role="region" aria-label="اصل شکل؛ لوڑ پئے تے پاسے سرکاؤ">' + f'<img{ident} src="{src}" alt="{html.escape(alt, quote=True)}"{alt_attrs} width="{spec["width"]}" height="{spec["height"]}" style="--source-width:{spec["width"]}px" />' + f'</div><p class="scroll-hint">چھوٹی سکرین اُتے پوری شکل ویکھن لئی پاسے سرکاؤ، یا <a href="{src}">اصل شکل وکھری کھولو</a>۔</p>' + advisory
        return f'<div class="source-media" data-source-child="{sid}">{media_html}</div>' if unit == '008' else media_html
    if name in ("note", "list"):
        out_tag = "aside" if name == "note" else "ol"
        if unit == '008' and name == 'list' and node.get('list-type') != 'enumerated':
            out_tag = 'ul'
        attrs = ' class="source-parts" role="list"' if name == 'list' and any(tag(c) == 'span' and c.get('class') == 'token' for item in node for c in item) else ''
        return f'<{out_tag}{ident}{attrs}>' + ''.join(render(c, node, i) for i, c in enumerate(node)) + f'</{out_tag}>'
    raise ValueError(f"Unsupported CNXML element: {name}")

def fragment(name):
    return (BASE / "translations" / name).read_text(encoding="utf-8")

body = render(doc)
assert used == set(blocks), f"Unused translations: {set(blocks) - used}"
if unit == '008':
    assert used_link_labels == set(translation['source_link_labels']), 'Unused external link labels'
endnotes = '<section class="source-endnotes"><h2>ماخذ دے حوالے</h2><ol>' + ''.join(f'<li id="{sid}-text">{value} <a href="#{sid}">متن ول واپس</a></li>' for sid,value in footnotes) + '</ol></section>' if footnotes else ''
with (BASE / "terminology.tsv").open(encoding="utf-8", newline="") as f:
    terms = list(csv.DictReader(f, delimiter="\t"))
ledger = '<section id="terminology"><h2>تِن زباناں دی اصطلاحی کُنجی</h2><div class="table-scroll"><table><thead><tr><th scope="col">شاہ مکھی پنجابی</th><th scope="col" lang="ur-Arab-PK">اردو</th><th scope="col" lang="en" dir="ltr">English</th></tr></thead><tbody>'
for row in terms:
    ledger += '<tr><td>' + html.escape(row["pnb-Arab-PK"]) + '</td><td lang="ur-Arab-PK">' + html.escape(row["ur-Arab-PK"]) + '</td><td lang="en" dir="ltr">' + html.escape(row["en"]) + '</td></tr>'
ledger += '</tbody></table></div></section>'
css = (BASE / "styles/reader.css").read_text(encoding="utf-8")
if unit == '008':
    css += '''
.source-media { max-width:100%; }
.source-media img { display:block; width:var(--source-width); min-width:var(--source-width); max-width:none; height:auto; padding:0; border:0; }
.source-table td[dir="rtl"] { white-space:normal; font-family:inherit; }
#Table_01_01_14 { width:890px; min-width:890px; table-layout:fixed; }
#Table_01_01_14 col:nth-child(1) { width:170px; }
#Table_01_01_14 col:nth-child(2) { width:170px; }
#Table_01_01_14 col:nth-child(3) { width:550px; }
#Table_01_01_14 th[colspan] { text-align:left; }
#Table_01_01_14 .source-media { width:100%; }
#Table_01_01_14 .scroll-hint { white-space:normal; font-family:inherit; direction:rtl; }
#toolkit-pixel-values td { white-space:nowrap; }
.source-summary-advisory { direction:rtl; }
'''
before = fragment('bridge-before.html') if unit == '001' else translation.get('bridge_before_html','')
after = fragment('bridge-after.html') if unit == '001' else translation.get('bridge_after_html','')
first_id = next(c.get('id') for c in doc if c.get('id'))
nav = '<a href="#bridge-start">ابتدائی پُل</a> · <a href="#fs-id1165133394710">ماخذ دا ترجمہ</a> · <a href="#bridge-practice">مشق</a>' if unit == '001' else f'<a href="unit-{int(unit)-1:03}.html">پچھلا سبق</a> · <a href="#{first_id}">ماخذ دا ترجمہ</a>'
if unit in ('001', '002', '003'):
    nav += f' · <a href="unit-{int(unit)+1:03}.html">اگلا سبق</a>'
source_label = 'دا ابتدائی حصہ؛ پورے حصے دا ترجمہ نہیں۔' if unit == '001' else 'دی پہلی حل کیتی مثال؛ پورے حصے دا ترجمہ نہیں۔' if unit == '002' else 'دا چُنیا ہویا حصہ؛ پورے حصے دا ترجمہ نہیں۔'
figure_note = 'Figure label 1.1.1 is local chapter.section.figure numbering; the canonical ID is Figure_01_01_001.' if unit == '001' else 'Figure labels 1.1.2–1.1.4 are local chapter.section.figure numbering, not published sequential figure numbers; canonical IDs Figure_01_01_004, Figure_01_01_027 and Figure_01_01_028 remain intact.'
change_notice = 'Shahmukhi Punjabi translation; labeled original algebra refresher, practice and answers; Urdu/English terminology; RTL HTML layout. Source MathML and the figure are retained in the source witness. In the reader only terminal English sentence punctuation is relocated from MathML into Punjabi prose; mathematical commas and parentheses are unchanged. Diagram English labels and odd/even formula text are intentionally preserved with Punjabi explanations.' if unit == '001' else 'Shahmukhi Punjabi translation of Example_01_01_01 including both worked solutions; three unchanged English diagrams; labeled original bilingual legend and direction-of-association clarification; Urdu/English terminology and RTL HTML layout. Source circled-letter part labels are rendered as isolated (a)/(b), preserving their correspondence. An accidental extra English article in the final source sentence is not reproduced. No additional practice or source MathML occurs in this unit; the frozen source witness is retained.'
if unit in ('003','004','005','006','007','008'):
    figure_note = 'Figure label 1.1.5 is local chapter.section.figure numbering; canonical ID Image_01_01_005 remains intact. The original English image is unchanged.' if unit == '004' else 'Figure label 1.1.6 is local chapter.section.figure numbering; canonical ID Figure_01_01_006 remains intact. The original English image is unchanged.' if unit == '006' else 'Table references use local chapter.section.table numbering; source table IDs and cell order remain intact. This unit contains no source images.'
    if unit == '007':
        figure_note = 'Figure labels 1.1.7–1.1.9 and table references are local reader labels. Canonical IDs and original English images are unchanged; source Table_01_01_12 remains unnumbered. Faithfully translated image alt is retained in data-source-alt, while corrected accessible descriptions link to explicit original notes. Exact component notices are retained in unit-007-component-notices.json.'
    if unit == '008':
        figure_note = 'Six genuine source figures use local reader labels; nine unnumbered toolkit media stay within their table cells. All fifteen original JPEGs are unchanged. Faithful source alts remain in data-source-alt; original expanded accessible descriptions link to visible notes. Exact existing component records are retained in unit-008-component-notices.json. The toolkit title spans its three original columns, and the equation table remains unnumbered. Earlier-unit references preserve their destination IDs; six historical external URLs are retained without a current-availability claim.'
    change_notice = 'Shahmukhi Punjabi translation of the declared source selection, with original explanatory additions labeled separately. Source identifiers, table data, proper names and mathematical content are retained. Where present, source circled-letter parts are displayed as isolated Latin-letter labels with the same correspondence. Unit-specific source ambiguities and accessibility-summary corrections are disclosed in the original bridge notes and provenance record. No native-speaker approval is claimed.'
    if unit in ('004', '005', '006', '007'):
        change_notice += ' Source MathML nodes remain in order; English quotation marks and terminal sentence punctuation are moved into Punjabi prose by reversible text edits recorded in data-source-text-edits. Internal mathematical punctuation and closing parentheses remain. The frozen source is unchanged.'
    if unit == '008':
        change_notice += ' All 49 source MathML trees retain their node order. Standalone terminal periods/commas and exactly one owner-bound numeric 1. and one question-mark token are relocated into Punjabi prose by reversible data-source-text-edits; internal mathematical punctuation, roots, fractions and scripts remain. Source emphasis without an explicit effect is displayed as strong, not silently italicized. The frozen source is unchanged.'
result = f'''<!doctype html>
<html lang="pnb-Arab-PK" dir="rtl"><head><meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="description" content="Shahmukhi Punjabi algebra-to-functions bridge; incremental translation unit" />
<title>{translation['title']} — PNB-{unit}</title><style>{css}</style></head><body>
<header><p class="eyebrow"><bdi dir="ltr">PNB-{unit} · A30 / m49301</bdi></p><h1>{translation['title']}</h1><p>{translation['subtitle']}</p>
<p class="status">ابتدائی ترجمہ · پنجابی دے ماہر دی لسانی جانچ ہن تک نہیں ہوئی</p>
<nav aria-label="سبق دے حصے">{nav} · <a href="#terminology">اصطلاحاں</a></nav></header>
<main>{before}
<p class="source-label">ماخذ دا ترجمہ: <bdi dir="ltr" lang="en">OpenStax Precalculus 2e, §1.1</bdi> {source_label}</p>
{body}{endnotes}{after}{ledger}</main>
<footer id="credits" lang="en" dir="ltr">
<h2>Sources, credits and changes</h2>
<p>Adapted from <a href="https://github.com/openstax/osbooks-college-algebra-bundle/blob/789b54099106b071d1d32bfcee454fed72eb4768/modules/m49301/index.cnxml">OpenStax Precalculus 2e, module m49301</a>, Jay Abramson et al., OpenStax / Rice University; foundational chapters credit David Lippman and Melonie Rasmussen. Figure copyright Rice University, OpenStax, under CC BY-NC-SA 4.0. Full contributor notices remain in <a href="../provenance/ATTRIBUTION.md">the provenance record</a>. Licensed under <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a>, subject to retained component notices. OpenStax and Rice University do not endorse this adaptation; no cover or trademarks are reproduced. {figure_note}</p>
<p>Changes: {change_notice}</p>
<p>Indonesian comparison edition: KokunoYumeto/openstax-precalculus-2e-id, alpha.58-reader.1. Its stated process provenance is OpenAI Codex gpt-5.6-sol, Ultra. This pilot was produced with OpenAI Codex assistance at the user's direction; source and human-contributor credits are not replaced. This is a local translation pilot, not a complete textbook or a model-training corpus.</p>
</footer></body></html>'''
if unit == '008':
    class ReaderTargets(HTMLParser):
        def __init__(self):
            super().__init__()
            self.ids, self.targets = [], []
        def handle_starttag(self, name, attrs):
            for key,value in attrs:
                if key == 'id':
                    self.ids.append(value)
                if key in ('href','src'):
                    self.targets.append(value)
    parsed = ReaderTargets()
    parsed.feed(result)
    assert len(parsed.ids) == len(set(parsed.ids)), 'Duplicate reader IDs'
    source_ids = [n.get('id') for n in doc.iter() if n is not doc and n.get('id')]
    assert [i for i in parsed.ids if i in set(source_ids)] == source_ids, 'Source ID order changed'
    for target in parsed.targets:
        address = urlsplit(target)
        if address.scheme or address.netloc:
            continue
        if address.path:
            path = (BASE/'reader'/unquote(address.path)).resolve()
            assert path.is_relative_to(BASE.resolve()) and path.is_file(), f'Missing/unsafe local target: {target}'
            if address.fragment:
                destination = ReaderTargets()
                destination.feed(path.read_text(encoding='utf-8'))
                assert address.fragment in destination.ids, f'Missing cross-unit ID: {target}'
        else:
            assert address.fragment in parsed.ids, f'Missing fragment: {target}'
(BASE / "reader").mkdir(exist_ok=True)
(BASE / f'reader/unit-{unit}.html').write_text(result, encoding="utf-8", newline="\n")
print(f'Built unit-{unit}.html: {len(used)} translated blocks; {len(terms)} terminology entries')
