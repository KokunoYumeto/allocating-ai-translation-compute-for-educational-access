"""Deterministic offline CNXML -> register-aligned HTML and narration/SSML.

No inference, network calls, speech service, or hidden language fallback.
Every linguistic source string requires an explicit phrase edit.
"""
import base64
import copy
import html
import json
import re
import xml.etree.ElementTree as ET
from config import LANG, TRACKS, UNITS
from safe_io import write_text as write

CN = 'http://cnx.rice.edu/cnxml'
MATH = 'http://www.w3.org/1998/Math/MathML'
XML_LANG = '{http://www.w3.org/XML/1998/namespace}lang'
ET.register_namespace('', CN)
ET.register_namespace('m', MATH)


def local(el):
    return el.tag.rsplit('}', 1)[-1]


def phrase(text, index, mapping, unchanged):
    if not text or not text.strip():
        return text
    key = text.strip()
    if key in unchanged or not re.search('[A-Za-z]', key):
        return text
    if key not in mapping:
        raise ValueError(f'Untranslated source text: {key!r}')
    return text[:len(text)-len(text.lstrip())] + mapping[key][index] + text[len(text.rstrip()):]


def translated(root, track, edits):
    root = copy.deepcopy(root)
    index = edits['tracks'].index(track)
    mapping = {row[0]: row[1:] for row in edits['phrases']}
    assert len(mapping) == len(edits['phrases']), 'Duplicate translation keys'
    for el in root.iter():
        el.text = phrase(el.text, index, mapping, edits['unchanged_identifiers'])
        el.tail = phrase(el.tail, index, mapping, edits['unchanged_identifiers'])
        for attr in ('alt', 'aria-label', 'summary'):
            if attr in el.attrib:
                el.set(attr, phrase(el.get(attr), index, mapping, []))
    root.set(XML_LANG, 'jv-Latn-ID')
    return root


def number(value, is_jv):
    if not re.fullmatch(r'[0-9]+(?:\.[0-9]+)?', value):
        raise ValueError(f'Unreviewed number narration syntax: {value}')
    if '.' in value:
        left, right = value.split('.')
        return number(left, is_jv) + ' koma ' + ' '.join(number(c, is_jv) for c in right)
    n = int(value)
    small = ['nol', 'siji', 'loro', 'telu', 'papat', 'lima', 'enem', 'pitu', 'wolu', 'sanga'] if is_jv else ['nol', 'satu', 'dua', 'tiga', 'empat', 'lima', 'enam', 'tujuh', 'delapan', 'sembilan']
    if n < 10:
        return small[n]
    if n == 10:
        return 'sepuluh'
    if n == 11:
        return 'sewelas' if is_jv else 'sebelas'
    if n < 20:
        return {12:'rolas', 13:'telulas', 14:'patbelas', 15:'limalas', 16:'nembelas', 17:'pitulas', 18:'wolulas', 19:'sangalas'}[n] if is_jv else small[n-10] + ' belas'
    if n < 100:
        stem = {2:'rong', 3:'telung', 4:'patang', 5:'seket', 6:'sewidak', 7:'pitung', 8:'wolung', 9:'sangang'}
        tens = (stem[n//10] + (' puluh' if n//10 not in (5, 6) else '')) if is_jv else small[n//10] + ' puluh'
        # Javanese 21–29 have the conventional likur construction.
        if is_jv and 21 <= n <= 29:
            return {21:'selikur', 22:'rolikur', 23:'telulikur', 24:'patlikur', 25:'selawe', 26:'nemlikur', 27:'pitulikur', 28:'wolulikur', 29:'sangalikur'}[n]
        return tens + ((' ' + small[n%10]) if n%10 else '')
    if n < 1000:
        stems = {2:'rong', 3:'telung', 4:'patang', 5:'limang', 6:'nem', 7:'pitung', 8:'wolung', 9:'sangang'}
        hundred = ('satus' if n//100 == 1 else stems[n//100] + ' atus') if is_jv else ('seratus' if n//100 == 1 else small[n//100] + ' ratus')
        return hundred + ((' ' + number(str(n%100), is_jv)) if n%100 else '')
    raise ValueError(f'Unreviewed number narration outside pilot range: {value}')


def spoken_text(text, is_jv):
    text = text or ''
    # The conversational source phrase already names the glyph as a tandha.
    # Avoid producing "Tandha tandha telung titik" when expanding its name.
    if is_jv:
        text = text.replace('Tandha “…”', '“tandha telung titik”')
    text = text.replace('“…”', '“tandha telung titik”' if is_jv else '“tanda tiga titik”')
    text = re.sub(r'\d+(?:\.\d+)?', lambda m: number(m[0], is_jv), text)
    labels = ({'ⓐ':'bagean a: ', 'ⓑ':'bagean be: ', 'ⓒ':'bagean ce: ', 'ⓓ':'bagean de: ', 'ⓔ':'bagean e: '}
              if is_jv else
              {'ⓐ':'bagian a: ', 'ⓑ':'bagian be: ', 'ⓒ':'bagian ce: ', 'ⓓ':'bagian de: ', 'ⓔ':'bagian e: '})
    for marker, label in labels.items():
        text = text.replace(marker, label)
    return text.replace('…', ' lan sateruse ' if is_jv else ' dan seterusnya ')


def speak_math(el, is_jv):
    tag = local(el)
    if tag not in ('math', 'mrow', 'mn', 'mi', 'mtext', 'mo', 'mfrac', 'mspace'):
        raise ValueError(f'Unreviewed MathML narration element: {tag}')
    if tag == 'mn':
        return number(el.text, is_jv)
    if tag in ('mi', 'mtext'):
        if el.text in ('g', 'x', 'y', 'a', 'b', 'c'):
            letter = {'g':'ge', 'x':'eks', 'y':'ye', 'a':'a', 'b':'be', 'c':'ce'}[el.text]
            return ('aksara ' if is_jv else 'huruf ') + letter
        return spoken_text(el.text, is_jv)
    if tag == 'mo':
        operators = {'+':'ditambah', ',':',', '.':'.', '…':'lan sateruse' if is_jv else 'dan seterusnya'}
        if el.text not in operators:
            raise ValueError(f'Unreviewed MathML narration operator: {el.text!r}')
        return operators[el.text]
    if tag == 'mfrac':
        if len(el) != 2:
            raise ValueError('MathML fraction must have one numerator and one denominator')
        return 'pecahan: ' + speak_math(el[0], is_jv) + ' per ' + speak_math(el[1], is_jv) + (', pungkasan pecahan' if is_jv else ', akhir pecahan')
    if tag == 'mspace':
        return ''
    return ' '.join(speak_math(c, is_jv) for c in el)


def speak(el, is_jv):
    tag = local(el)
    if el.tag.startswith('{' + MATH + '}'):
        return speak_math(el, is_jv)
    if tag == 'media':
        return spoken_text(el.get('alt', ''), is_jv)
    if tag == 'link':
        return 'gambar garis wilangan' if el.get('target-id', '').startswith('CNX_') and is_jv else 'gambar garis bilangan' if el.get('target-id', '').startswith('CNX_') else 'tabel umur Greg lan Alex' if is_jv else 'tabel usia Greg dan Alex'
    if tag == 'table':
        headers = el.findall('.//{*}thead/{*}row/{*}entry')
        lines = []
        for row in el.findall('.//{*}tbody/{*}row'):
            lines.append('; '.join(speak(h, is_jv) + ': ' + speak(c, is_jv) for h, c in zip(headers, row)))
        return 'Tabel. ' + '. '.join(lines) + '.'
    if tag == 'emphasis' and (el.text or '').strip() in ('g', 'x', 'y', 'a', 'b', 'c'):
        return ('aksara ' if is_jv else 'huruf ') + {'g':'ge', 'x':'eks', 'y':'ye', 'a':'a', 'b':'be', 'c':'ce'}[el.text.strip()]
    result = spoken_text(el.text, is_jv)
    if tag == 'solution' and el.find('{*}title') is None:
        result = ('Wangsulan.\n' if is_jv else 'Jawaban.\n') + result
    for child in el:
        result += speak(child, is_jv) + spoken_text(child.tail, is_jv)
        if local(child) in ('para', 'title', 'equation', 'item', 'solution', 'problem'):
            result += '\n'
    return result


def math_html(el):
    tag = local(el)
    attrs = ''.join(' ' + html.escape(k) + '="' + html.escape(v, quote=True) + '"' for k, v in el.attrib.items())
    if tag == 'math':
        attrs += ' xmlns="' + MATH + '"'
    content = html.escape(el.text or '') + ''.join(math_html(c) + html.escape(c.tail or '') for c in el)
    return f'<{tag}{attrs}>{content}</{tag}>'


def render(el, prefix, svg, parent=''):
    tag = local(el)
    if tag == 'newline':
        return '<br>'
    if el.tag.startswith('{' + MATH + '}'):
        return math_html(el)
    attrs = ''
    if el.get('id'):
        attrs += f' id="{prefix}{html.escape(el.get("id"))}" data-source-id="{html.escape(el.get("id"))}"'
    content = html.escape(el.text or '') + ''.join(render(c, prefix, svg, tag) + html.escape(c.tail or '') for c in el)
    if tag == 'link':
        target = el.get('target-id')
        if target is None:
            url = el.get('url')
            if (not prefix.startswith(('a00-rounding--', 'a00-m81243-complete--')) or url not in (
                    'https://www.openstax.org/l/24detplaceval',
                    'https://www.openstax.org/l/24numdigword') or not content.strip()):
                raise ValueError('Unregistered external learning-resource link')
            return f'<a{attrs} href="{html.escape(url, quote=True)}" rel="noreferrer">{content}</a>'
        label = 'Gambar' if target.startswith('CNX_') else 'Tabel'
        return f'<a{attrs} href="#{prefix}{target}">{label}</a>'
    if tag == 'image':
        return ''
    if tag == 'media':
        image = el.find('{*}image')
        if image is None:
            raise ValueError('Unregistered media: missing image')
        if isinstance(svg, dict):
            if image.get('src') not in svg:
                raise ValueError('Unregistered media: add an explicit source-bound asset mapping')
            asset = svg[image.get('src')]
            encoded = base64.b64encode(asset['bytes']).decode()
            mime = asset['mime_type']
        elif image.get('src') == '../../media/CNX_BMath_Figure_01_01_001.jpg.id-ID.svg':
            encoded = base64.b64encode(svg.encode()).decode()
            mime = 'image/svg+xml'
        else:
            raise ValueError('Unregistered media: add an explicit source-bound asset mapping')
        return f'<span{attrs}><img src="data:{mime};base64,{encoded}" alt="{html.escape(el.get("alt", ""), quote=True)}"></span>'
    if tag in ('tgroup', 'colspec', 'label'):
        return content
    tags = {'section':'section', 'glossary':'section', 'definition':'div',
            'title':'h3', 'para':'p', 'term':'strong', 'meaning':'p',
            'note':'aside', 'equation':'div', 'figure':'figure',
            'caption':'figcaption', 'example':'div', 'exercise':'div',
            'problem':'div', 'solution':'div', 'list':'ul', 'item':'li',
            'span':'span', 'emphasis':'em', 'table':'table', 'thead':'thead',
            'tbody':'tbody', 'row':'tr', 'entry':'td'}
    out = tags.get(tag)
    if not out:
        raise ValueError(f'Unmapped CNXML element {tag}')
    if tag == 'list':
        kind = el.get('list-type', 'bulleted')
        attrs += f' data-source-list-type="{html.escape(kind, quote=True)}"'
        if kind == 'enumerated':
            styles = {'arabic': '1', 'lower-alpha': 'a', 'upper-alpha': 'A',
                      'lower-roman': 'i', 'upper-roman': 'I'}
            style = el.get('number-style', 'arabic')
            if style not in styles:
                raise ValueError(f'Unregistered enumerated-list style: {style}')
            out = 'ol'
            attrs += f' type="{styles[style]}"'
            items = el.findall('{*}item')
            explicit_parts = items and all(
                len(item) and local(item[0]) == 'span'
                and item[0].get('class') == 'token'
                and re.fullmatch('[ⓐ-ⓩ]', (item[0].text or '').strip())
                for item in items)
            if explicit_parts:
                # Keep ordered-list semantics, but do not duplicate source ⓐ.
                attrs += ' class="source-labeled-list"'
        elif kind == 'labeled-item':
            # Source items already contain their explicit part labels.
            attrs += ' class="source-labeled-list"'
        elif kind != 'bulleted':
            raise ValueError(f'Unregistered CNXML list type: {kind}')
    if tag == 'table':
        # Keep a source summary accessible without inventing a visible header.
        label = el.get('aria-label') or el.get('summary')
        if label:
            attrs += f' aria-label="{html.escape(label, quote=True)}"'
        content = re.sub(r'<thead>(.*?)</thead>', lambda m: '<thead>' + m[1].replace('<td>', '<th scope="col">').replace('</td>', '</th>') + '</thead>', content, flags=re.S)
    if tag == 'solution':
        attrs += ' class="solution"'
        if el.find('{*}title') is None:
            content = '<h4><span lang="jv-Latn-ID">Wangsulan</span> / <span lang="id-ID">Jawaban</span></h4>' + content
    if tag in ('note', 'example'):
        attrs += f' class="{tag} {html.escape(el.get("class", ""))}"'
    return f'<{out}{attrs}>{content}</{out}>'


STYLE = '''
:root{color-scheme:light;--ink:#173431;--accent:#24675d;--line:#c9d8d2}*{box-sizing:border-box}
body{margin:0;background:#f3f6f3;color:var(--ink);font:17px/1.65 Georgia,"Times New Roman",serif}
main{max-width:1440px;margin:auto;padding:36px}header{max-width:1000px;margin:0 auto 36px}h1{font-size:2.5rem;line-height:1.15;margin:.4em 0}h2{font-size:1.65rem}h3{font-size:1.16rem}h4{font-size:1rem}
.eyebrow,.register,.source,.status,nav{font:13px/1.5 system-ui,sans-serif}.eyebrow{letter-spacing:.12em;text-transform:uppercase;color:var(--accent)}
.status{background:#fff4d7;padding:16px;border-left:4px solid #986d18}.source{overflow-wrap:anywhere;color:#425853}
.parallel{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;margin:18px 0}.track{background:#fff;padding:20px;border:1px solid var(--line);min-width:0}
.register{font-weight:700;letter-spacing:.03em;color:var(--accent);border-bottom:2px solid var(--line);padding-bottom:10px;margin-bottom:16px}
.section-title{padding-top:30px;border-top:2px solid var(--accent)}p{margin:.7em 0}figure{margin:16px 0}img{max-width:100%;height:auto}figcaption{font-size:.9em}
aside,.example{padding:12px;border-left:3px solid var(--line);background:#fafcf9}.solution{margin-top:16px;border-top:1px dashed var(--line);padding-top:8px}
table{width:100%;border-collapse:collapse}td,th{border:1px solid var(--line);padding:6px;text-align:center}th{background:#edf4ef}math{font-size:1.1em}a{color:#185e54}ul,ol{padding-left:1.2em}.source-labeled-list{list-style:none}
footer{margin-top:40px;border-top:2px solid var(--accent);padding-top:20px;font:14px/1.6 system-ui,sans-serif}.note-box{max-width:1000px;margin:20px auto;padding:20px;background:#fff}
@media(max-width:1050px){main{padding:18px}.parallel{grid-template-columns:1fr}.track{padding:18px}h1{font-size:2rem}}
@media print{body{background:#fff}main{padding:0}.parallel{display:block}.track{break-inside:avoid}.status{background:#fff}nav{display:none}}
'''


def main():
    edits = json.loads((LANG / 'translation/phrases.json').read_text(encoding='utf-8'))
    id_svg = (LANG / 'translation/number-line.id-ID.svg').read_text(encoding='utf-8')
    jv_svg = id_svg.replace('xml:lang="id-ID"', 'xml:lang="jv-Latn-ID"').replace('Garis bilangan: lebih besar dan lebih kecil', 'Garis wilangan: luwih gedhé lan luwih cilik').replace('Garis bilangan dari 0 sampai 6. Panah ke kanan berlabel lebih besar dan panah ke kiri berlabel lebih kecil.', 'Garis wilangan saka 0 nganti 6. Panah nengen diwenehi label luwih gedhé lan panah ngiwa diwenehi label luwih cilik.').replace('lebih besar', 'luwih gedhé').replace('lebih kecil', 'luwih cilik')
    write(LANG / 'translation/number-line.jv-Latn-ID.svg', jv_svg)
    pieces = []
    for unit in UNITS:
        source = ET.parse(LANG / f'translation/{unit["key"]}.id-academic.cnxml').getroot()
        variants = {'id-academic': source}
        for track in ('jv-academic', 'jv-conversation'):
            variants[track] = translated(source, track, edits)
            write(LANG / f'translation/{unit["key"]}.{track}.cnxml', ET.tostring(variants[track], encoding='unicode', xml_declaration=True) + '\n')
        pieces.append(f'<section class="section-title" id="{unit["key"]}"><h2 lang="jv-Latn-ID">{unit["program"]} · {html.escape(variants["jv-academic"].findtext("{*}title"))}</h2><p class="source" lang="en">{unit["module"]} / {unit["section"]} · {html.escape(unit["scope"])}</p>')
        for track in TRACKS:
            pieces.append(f'<span id="{unit["module"]}--{track}--{unit["section"]}" data-source-id="{unit["section"]}"></span>')
        for index in range(1, len(source)):
            pieces.append('<div class="parallel">')
            for track, (locale, label) in TRACKS.items():
                prefix = unit['module'] + '--' + track + '--'
                markup = render(variants[track][index], prefix, jv_svg if track.startswith('jv') else id_svg)
                pieces.append(f'<article class="track" lang="{locale}" data-register="{track}"><div class="register">{label}</div>{markup}</article>')
            pieces.append('</div>')
        pieces.append('</section>')
        for track, (locale, label) in TRACKS.items():
            is_jv = track.startswith('jv')
            blocks = []
            for el in variants[track]:
                body = re.sub(r'[ \t]+', ' ', speak(el, is_jv)).strip()
                body = body.replace('lan sateruse lan sateruse', 'lan sateruse').replace('dan seterusnya dan seterusnya', 'dan seterusnya')
                body = re.sub(r'\n{3,}', '\n\n', body)
                blocks.append((f'{unit["module"]}--{el.get("id", "title")}', body))
            transcript = f'# {label}\n\nStatus: narration draft; not synthesized or listening-reviewed.\n\n'
            transcript += '\n\n'.join(f'## {mark}\n\n{body}' for mark, body in blocks) + '\n'
            write(LANG / f'review/audio/{unit["key"]}.{track}.md', transcript)
            ssml = f'<?xml version="1.0" encoding="UTF-8"?>\n<speak xmlns="http://www.w3.org/2001/10/synthesis" version="1.1" xml:lang="{locale}">\n'
            ssml += f'<p>{html.escape(label)}</p>\n'
            ssml += ''.join(f'<mark name="{mark}"/><p>{html.escape(body)}</p><break time="600ms"/>\n' for mark, body in blocks)
            ssml += '</speak>\n'
            write(LANG / f'review/audio/{unit["key"]}.{track}.ssml', ssml)
    header = '''<!DOCTYPE html>
<html lang="id-ID"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Wilangan lan aljabar · Javanese–Indonesian pilot</title><style>''' + STYLE + '''</style></head><body><main>
<header><div class="eyebrow"><span lang="en">Javanese · jv-Latn-ID</span> / Bahasa Indonesia</div><h1><span lang="jv-Latn-ID">Wilangan lan aljabar</span><br><span lang="id-ID">Dari bilangan menuju aljabar</span></h1><p>Unit percontohan dwibahasa dengan tiga register yang diberi label secara terbuka.</p>
<div class="status">Draf untuk penelaahan, bukan edisi siap terbit. Bahasa Jawa akademik di sini adalah rancangan pedagogis. Belum ditelaah penutur/pendidik Jawa; audio belum disintesis atau diuji dengar.</div>
<nav><a href="#a00-number-sense">A00 · Bilangan</a> · <a href="#a10-variable-bridge">A10 · Variabel</a> · <a href="#audio">Naskah audio</a> · <a href="#credits">Kredit</a></nav></header>
<div class="note-box"><h2>Tujuan / <span lang="jv-Latn-ID">Ancas</span></h2><p lang="jv-Latn-ID">Ngenali wilangan asli lan wilangan cacah; maca garis wilangan; mbedakake variabel lan konstanta.</p><p lang="id-ID">Mengenali bilangan asli dan cacah; membaca garis bilangan; membedakan variabel dan konstanta.</p><p lang="id-ID">Konvensi sumber: bilangan asli dimulai dari 1; bilangan cacah mencakup 0. Titik desimal dalam formula (misalnya 5.2) dipertahankan dari sumber dan dibaca “koma”. Ngoko bukan krama; pemakaiannya perlu disesuaikan dengan hubungan sosial.</p></div>
'''
    audio_links = '<section id="audio" class="note-box"><h2>Audio / naskah narasi</h2><p>Naskah lengkap tiap unit tersedia per register. Berkas SSML tidak membuktikan tersedianya suara Javanese pada penyedia TTS.</p><ul>'
    for unit in UNITS:
        for track, (_, label) in TRACKS.items():
            stem = f'audio/{unit["key"]}.{track}'
            audio_links += f'<li>{unit["program"]} · <span lang="{TRACKS[track][0]}">{label}</span>: <a href="{stem}.md">Naskah</a> / <a href="{stem}.ssml">SSML</a></li>'
    audio_links += '</ul></section>'
    footer = '''<footer id="credits" lang="en"><h2>Attribution / <span lang="id-ID">Kredit</span></h2><p>Unofficial selected adaptation of OpenStax <em>Prealgebra 2e</em> and <em>Elementary Algebra 2e</em>, through the Indonesian editions by KokunoYumeto. Original senior contributing authors: Lynn Marecek, MaryAnne Anthony-Smith, Andrea Honeycutt Mathis. Copyright Rice University, OpenStax, under CC BY-NC-SA 4.0 license. The number-line figure retains the original ID and geometry; Javanese labels are adapted.</p><p>Source commit: 38cae454e644abf9f0a623e876994553881597c9. Indonesian A10 release: v1.0.2. Translation and narration: AI-assisted Codex draft, 2026-08-30. Original author and component notices remain in <a href="../ATTRIBUTION.md">ATTRIBUTION.md</a> and <a href="../provenance/A00-LICENSE.txt">the retained license</a>.</p><p>OpenStax and Rice University do not endorse this adaptation; names, logos, and marks are not licensed. Material is CC BY-NC-SA 4.0, subject to component-specific restrictions. AX-2 planning references retain their own CC BY 4.0 attribution. No training/fine-tuning dataset is created.</p><p><a href="../canon/README.md">Javanese reference shelf</a> · <a href="../terminology.csv">Terminology</a> · <a href="../NEXT_UNIT.md">Next source unit</a></p></footer></main></body></html>
'''
    write(LANG / 'review/pilot.html', header + '\n'.join(pieces) + audio_links + footer)
    print('Built four Javanese CNXML excerpts, one localized SVG, one offline reader, six narration transcripts and six SSML files.')


if __name__ == '__main__':
    main()
