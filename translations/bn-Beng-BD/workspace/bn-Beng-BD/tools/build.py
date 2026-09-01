"""Deterministic offline translation-document builder; standard library only.

The keyed strings are translator inputs, not a training/fine-tuning export.
Unknown translatable slots are fatal. Numeric MathML and CNXML IDs never change.
"""
from pathlib import Path
import argparse, copy, hashlib, html, json, re, shutil, xml.etree.ElementTree as ET, zipfile

L = Path(__file__).resolve().parents[1]
C = 'http://cnx.rice.edu/cnxml'
M = 'http://www.w3.org/1998/Math/MathML'
ET.register_namespace('', C)
ET.register_namespace('m', M)
def sha(data): return hashlib.sha256(data).hexdigest()
def local(e): return e.tag.rsplit('}',1)[-1]
def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')
def inner(e):
    return html.escape(e.text or '') + ''.join(render(n) + html.escape(n.tail or '') for n in e)
def attrs(e):
    return ''.join(f' {k}="{html.escape(v,quote=True)}"' for k,v in e.attrib.items() if k in ('id','class'))
def render(e, header=False):
    tag = local(e)
    a = attrs(e)
    if e.tag.startswith('{'+M+'}'):
        c = copy.deepcopy(e)
        c.tail = None
        for n in c.iter(): n.tag = local(n)
        c.set('xmlns',M)
        return ET.tostring(c, encoding='unicode', short_empty_elements=False)
    if tag == 'document': return inner(e)
    if tag == 'para' and any(local(child) in ('list','table','figure','note','section') for child in e):
        chunks=[f'<div{a}>']
        if (e.text or '').strip():chunks.append('<p>'+html.escape(e.text)+'</p>')
        for child in e:
            chunks.append(render(child))
            if (child.tail or '').strip():chunks.append('<p>'+html.escape(child.tail)+'</p>')
        return ''.join(chunks)+'</div>'
    if tag == 'link':
        if e.get('url'):
            url=e.get('url')
            if not url.startswith(('http://','https://')):raise ValueError('Unsupported external link: '+url)
            return f'<a{a} href="{html.escape(url,quote=True)}">{inner(e)}</a>'
        target = e.get('target-id')
        return f'<a{a} href="#{target}">চিত্র {target.rsplit("_",1)[-1]}</a>'
    if tag == 'media':
        # Explicit text-equivalent rendition. No image-only formulas or unlocalized labels.
        return f'<span{a} class="media-description">চিত্রের বর্ণনা: {html.escape(e.get("alt", ""))}</span>'
    if tag == 'table':
        group = e.find(f'{{{C}}}tgroup')
        rounding_tables={'eip-659':'843: দশকের স্থানে আসন্ন মান','eip-493':'23,658: শতকের স্থানে আসন্ন মান','eip-379':'3,978: শতকের স্থানে আসন্ন মান','eip-695':'147,032: হাজারের স্থানে আসন্ন মান','eip-596':'29,504: হাজারের স্থানে আসন্ন মান'}
        caption = rounding_tables.get(e.get('id')) or ('সংখ্যার নাম লেখার ধাপ' if e.get('id') == 'fs-id1171100715908' else 'স্থানীয় মানের ছক')
        chunks = [f'<table{a}><caption>{caption}</caption>']
        if e.get('id') == 'fs-id1171100715908':
            chunks.append('<thead><tr><th scope="col">বিবরণ</th><th scope="col">কথায়</th></tr></thead>')
        elif e.get('id') in rounding_tables:
            chunks.append('<thead><tr><th scope="col">ধাপ</th><th scope="col">সংখ্যায় কী হচ্ছে</th></tr></thead>')
        for block in group:
            btag = local(block)
            if btag not in ('thead','tbody'): continue
            chunks.append(f'<{btag}>')
            for row in block:
                chunks.append('<tr>')
                for cell in row:
                    ctag = 'th' if btag == 'thead' else 'td'
                    scope = ' scope="col"' if ctag == 'th' else ''
                    chunks.append(f'<{ctag}{attrs(cell)}{scope}>{inner(cell)}</{ctag}>')
                chunks.append('</tr>')
            chunks.append(f'</{btag}>')
        return ''.join(chunks)+'</table>'
    if tag == 'list':
        t = 'ol' if e.get('list-type') == 'enumerated' else 'ul'
        return f'<{t}{a}>'+inner(e)+f'</{t}>'
    if tag in ('label','image'): return f'<span{a}></span>' if e.get('id') else ''
    if tag == 'newline': return '<br/>'
    mapped = {'section':'section','title':'h3','para':'p','note':'aside','example':'div','exercise':'div','problem':'div','solution':'div','equation':'div','term':'dfn','figure':'figure','caption':'figcaption','span':'span','item':'li','emphasis':'em'}.get(tag)
    if not mapped: raise ValueError('Unmapped CNXML node: '+tag)
    content = inner(e)
    if tag == 'exercise': content = f'<p class="source-label">উৎসের কাজ: {e.get("id")}</p>'+content
    return f'<{mapped}{a}>{content}</{mapped}>'

STYLE = '''
@font-face{font-family:"Noto Sans Bengali";src:url("../assets/NumeracyBangla.ttf") format("truetype");font-display:swap}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f6f5f0;color:#172e35;font:20px/1.8 "Noto Sans Bengali","Nirmala UI",sans-serif}
main{max-width:960px;margin:auto;background:white;padding:2rem 3rem}header{border-bottom:4px solid #226e65;padding-bottom:1rem}h1{font-size:2rem;line-height:1.5}h2{font-size:1.5rem;border-top:2px solid #b4cfc9;padding-top:1rem;margin-top:2rem}h3{font-size:1.15rem;color:#215b53;margin:1.4rem 0 .7rem}p{margin:.65rem 0}li{margin:.8rem 0}a{color:#125448;text-underline-offset:.2em}a:focus{outline:3px solid #bc6900}table{border-collapse:collapse;width:100%;margin:1rem 0}th,td{border:1px solid #698481;padding:.5rem;text-align:left}th{background:#edf5f2}caption{text-align:left;font-weight:bold}.notice,aside{background:#f0f5f3;border-left:4px solid #426d64;padding:.8rem 1rem;margin:1.2rem 0}.kicker,.source-label{font-size:.85rem;color:#405655}.media-description{display:block;border:1px dashed #698481;padding:.6rem;margin:1rem 0}.numberline{word-spacing:.35em;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}math{font-size:1em}figure{margin:1rem 0}dfn{font-style:normal;font-weight:bold}.skip{display:block;padding:.5rem}footer{border-top:2px solid #698481;margin-top:3rem;padding-top:1rem;font-size:.85rem;overflow-wrap:anywhere}nav ul{padding-left:1.5rem}nav li{margin:.2rem 0}
@media(max-width:600px){body{font-size:18px}main{padding:1rem}th,td{padding:.3rem}h1{font-size:1.65rem}}
@media print{@page{size:A4;margin:18mm}body{background:white;font-size:12pt;color:black}main{padding:0;max-width:none}.skip{display:none}h1,h2,h3{break-after:avoid}tr,figure{break-inside:avoid}a{color:black}section{orphans:3;widows:3}}
'''
NOTICE = '''<footer id="attribution" lang="en"><h2>Attribution / উৎস ও পরিবর্তন</h2>
<p>Based on OpenStax, <em>Prealgebra 2e</em>, Lynn Marecek and MaryAnne Anthony-Smith; Copyright Rice University. Canonical source: <a href="https://github.com/openstax/osbooks-prealgebra-bundle/tree/38cae454e644abf9f0a623e876994553881597c9">frozen OpenStax bundle</a>, module m81243, sections fs-id1830385 and fs-id2340048. Indonesian edition by the KokunoYumeto project; its stated model provenance is “OpenAI Codex gpt-5.6-sol, Ultra.” Original human credits and notices are retained in provenance/notices.</p>
<p>Bangladesh Bangla translation, text-equivalent figure renditions, plain-language companion and expanded answers: Language Allocation project, AI-assisted draft, 2026-08-30. Not reviewed by a Bangladesh teacher. Faithful extract retains original digits, dollars, hierarchy, IDs and MathML values; the companion uses Bangla digits and separately authored classroom contexts. The external manipulative activity mentioned by the source is not bundled or counted as translated.</p>
<p>Source and derivative: <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0</a>, subject to component-specific notices. Supplied as-is without warranties; see the retained license. OpenStax and Rice University do not endorse this translation. Their names, logos and marks are not licensed. Bangladesh canon references are consulted for usage only, not relicensed or reproduced as a textbook.</p>
<p>License URI: https://creativecommons.org/licenses/by-nc-sa/4.0/</p>
<p>Original book: https://openstax.org/details/books/prealgebra-2e</p></footer>'''

def build(out):
    root = ET.parse(L/'provenance/u01-source-extract.cnxml').getroot()
    translated = copy.deepcopy(root)
    mapping = json.loads((L/'translations/u01-text.bn.json').read_text(encoding='utf-8'))
    used, slots = set(), 0
    for e in translated.iter():
        for prop in ('text','tail','alt','aria-label'):
            is_attribute = prop in ('alt','aria-label')
            v = e.get(prop) if is_attribute else getattr(e,prop)
            if v in mapping:
                if is_attribute: e.set(prop,mapping[v])
                else: setattr(e,prop,mapping[v])
                used.add(v); slots += 1
            elif v and re.search('[A-Za-z]',v):
                raise ValueError(f'Untranslated {e.get("id",local(e))} {prop}: {v!r}')
    assert set(mapping) == used, 'Unused translation keys: '+repr(set(mapping)-used)
    translated.set('{http://www.w3.org/XML/1998/namespace}lang','bn-Beng-BD')
    tr_path = L/'translations/modules/m81243/index.cnxml'
    tr_path.parent.mkdir(parents=True,exist_ok=True)
    ET.ElementTree(translated).write(tr_path,encoding='utf-8',xml_declaration=True)
    media=[]
    for e in root.iter(f'{{{C}}}image'):
        filename=Path(e.get('src')).name
        source=L.parent/'downloads/bn-Beng-BD/openstax-canonical/media'/filename
        target=L/'translations/media'/filename
        target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists(): shutil.copyfile(source,target)
        media.append({'file':str(target.relative_to(L)).replace('\\','/'),'sha256':sha(target.read_bytes())})
    companion = (L/'translations/u01-companion.xhtml').read_text(encoding='utf-8')
    ET.fromstring(companion)
    faithful = '<article id="faithful"><h2>উৎসের গঠন অক্ষুণ্ণ রেখে অনুবাদ</h2><p class="notice">এই অংশে মূল উৎসের 0–9 অঙ্ক, $ চিহ্ন, ভগ্নাংশ ও দশমিক অপরিবর্তিত আছে। $ মানে মার্কিন ডলার; টাকা নয়। চিত্রগুলো একই ID-তে বাংলা পাঠ্য বর্ণনা হিসেবে দেওয়া হয়েছে। এটি m81243-এর প্রথম দুই অংশ, পুরো মডিউল নয়।</p>'+render(translated)+'</article>'
    page = '<!DOCTYPE html>\n<html lang="bn-Beng-BD"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><title>সংখ্যা চিনি, স্থানীয় মান বুঝি | bn-Beng-BD U01</title><style>'+STYLE+'</style></head><body><a class="skip" href="#bd-u01-companion">মূল পাঠে যাই</a><main><header><p class="kicker">LANGUAGE ALLOCATION · BANGLADESH BANGLA · PILOT U01</p><nav aria-label="পাঠের অংশ"><ul><li><a href="#bd-u01-companion">শিশুর সহজ পাঠ</a></li><li><a href="#bd-u01-answers">সব কাজের উত্তর</a></li><li><a href="#faithful">উৎসের অনুবাদ</a></li><li><a href="#attribution">উৎস ও স্বীকৃতি</a></li></ul></nav></header>'+companion+faithful+NOTICE+'</main></body></html>\n'
    write(out/'u01-number-sense.html',page)
    manifest = {'locale':'bn-Beng-BD','unit':'U01','translation_slots':slots,'unique_translation_strings':len(used),'source_sha256':sha((L/'provenance/u01-source-extract.cnxml').read_bytes()),'translation_path':str(tr_path.relative_to(L)).replace('\\','/'),'translation_sha256':sha(tr_path.read_bytes()),'html_sha256':sha(page.encode()),'external_runtime_resources':0,'built_with':'Python standard library; deterministic HTML and CNXML','figures':'All source media are rendered as translated text equivalents; original images and relative src attributes retained in CNXML.','preserved_image_files':media}
    write(out/'build-receipt.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    return manifest

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=L/'output');a=p.parse_args()
    print(json.dumps(build(a.out),ensure_ascii=False,indent=2))
