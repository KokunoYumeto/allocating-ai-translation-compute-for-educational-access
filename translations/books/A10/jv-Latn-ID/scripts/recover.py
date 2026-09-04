"""Build the bounded A10 reader from hash-verified recovered component inputs.

Usage: python scripts/recover.py PATH_TO_TRANSLATIONS_EXPORT
Only this package directory is written. No TeX, Git, or remote writes.
"""
from pathlib import Path
from copy import deepcopy
from collections import Counter
import hashlib, json, sys, re, urllib.request, shutil, html
from lxml import etree as E
from lxml import html as H
from asset_labels import adaptation_caption

OUT = Path(__file__).resolve().parents[1]
EXPORT = Path(sys.argv[1]).resolve()
PREFIX = 'jv-Latn-ID/workspace/languages/jv-Latn-ID/'
PIN = '38cae454e644abf9f0a623e876994553881597c9'
MANIFEST_SHA = '772c054d8b6f9337f62a89df2fc2c726ed2d97c9077cb07f07dd0150e5ffe5a1'
SOURCE_SHA = 'a8fdd235aa254c5a0a1248fa858e9b3579d9b40982bbc514cbe6a18c3e6fcbed'
CN = 'http://cnx.rice.edu/cnxml'
M = 'http://www.w3.org/1998/Math/MathML'
NS = {'c': CN, 'm': M}
TRACKS = {'jv-academic': ('jv-Latn-ID', 'Basa Jawa akademik'),
          'jv-conversation': ('jv-Latn-ID', 'Basa Jawa padinan · ngoko'),
          'id-academic': ('id-ID', 'Jembatan Bahasa Indonesia')}
FIRST = ['variable-bridge', 'operation-symbols', 'equality-symbols', 'grouping-symbols', 'expressions-equations', 'exponents']
REST = ['order-operations', 'evaluate-expressions', 'combine-like-terms']
UNITS = ['a10-' + k for k in FIRST + REST]
RECEIPT = []
def sha(b): return hashlib.sha256(b).hexdigest()
def write(rel, content):
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, str): content = content.encode('utf-8')
    p.write_bytes(content)
    return sha(content)
def jwrite(rel, obj): return write(rel, json.dumps(obj, indent=2, ensure_ascii=False) + '\n')
manifest_bytes = (EXPORT / 'EXPORT_MANIFEST.json').read_bytes()
assert sha(manifest_bytes) == MANIFEST_SHA
manifest = json.loads(manifest_bytes)
entries = {f['path']: f for f in manifest['files']}
def recover(rel, dest=None):
    entry = entries[PREFIX + rel]
    data = (EXPORT / entry['path']).read_bytes()
    assert sha(data) == entry['export_sha256'], rel
    dest = dest or rel
    write(dest, data)
    RECEIPT.append({'export_path': entry['path'], 'path': dest, 'bytes': len(data), 'sha256': sha(data)})
    return data

# Exact export inputs only: no operational QA logs, transcripts, or A00 payload.
for unit in UNITS:
    recover(f'provenance/{unit}.en.cnxml', f'source/components/{unit}.en.cnxml')
    for track in TRACKS:
        recover(f'translation/{unit}.{track}.cnxml', f'source/components/{unit}.{track}.cnxml')
        for ext in ('md', 'ssml'):
            recover(f'review/audio/{unit}.{track}.{ext}', f'narration/{unit}.{track}.{ext}')
    for ext in ('assets.json', 'edits.json'):
        rel = f'translation/{unit}.{ext}'
        if PREFIX + rel in entries: recover(rel, f'provenance/component-inputs/{unit}.{ext}')
    rel = f'audio/{unit}.rules.json'
    if PREFIX + rel in entries: recover(rel, f'provenance/component-inputs/{unit}.rules.json')
for entry in entries.values():
    rel = entry['path'].removeprefix(PREFIX)
    if entry['path'].startswith(PREFIX) and any(rel.startswith(f'translation/assets/{u}/') for u in UNITS):
        recover(rel, rel.replace('translation/', '', 1))
for rel, dest in [('canon/README.md','provenance/shared-canon-README.md'),
                  ('canon/sources.lock.json','provenance/shared-canon-sources.lock.json'),
                  ('terminology.csv','provenance/shared-terminology.csv'),
                  ('provenance/A10-LICENSE.txt','LICENSE.txt'),
                  ('provenance/A10-NOTICE.txt','provenance/inherited-indonesian-NOTICE.txt'),
                  ('provenance/A10-SOURCE_AUTHORITY.md','provenance/inherited-source-authority.md')]:
    recover(rel, dest)
coverage = json.loads((EXPORT / PREFIX / 'coverage.json').read_bytes())
coverage_entry = entries[PREFIX + 'coverage.json']
assert sha((EXPORT / PREFIX / 'coverage.json').read_bytes()) == coverage_entry['export_sha256']

source_path = OUT / 'source/m82453.en.cnxml'
source_url = f'https://raw.githubusercontent.com/openstax/osbooks-prealgebra-bundle/{PIN}/modules/m82453/index.cnxml'
if source_path.exists():
    source = source_path.read_bytes()
else:
    with urllib.request.urlopen(source_url, timeout=45) as r: source = r.read()
assert sha(source) == SOURCE_SHA, 'Pinned source mismatch'
write('source/m82453.en.cnxml', source)
canonical = E.fromstring(source)
sections = canonical.findall('c:content/c:section', NS)
def tag(el): return E.QName(el).localname
def normalized(el, formula=False):
    # CNXML pretty-print whitespace is immaterial; MathML mathematical tokens are not.
    if formula and tag(el) == 'mtext': return (el.tag, 'LINGUISTIC_TEXT')
    attrs = tuple(sorted((k,v) for k,v in el.attrib.items() if k != '{http://www.w3.org/XML/1998/namespace}lang'))
    return (el.tag, attrs, (el.text or '').strip(), tuple((normalized(c, formula),(c.tail or '').strip()) for c in el))
def shape(el):
    return (el.tag, el.get('id'), tuple(shape(c) for c in el))
def ids(el): return [x.get('id') for x in el.iter() if x.get('id')]
def maths(el): return [normalized(x, True) for x in el.iter('{'+M+'}math')]
def mathematical_reference(section):
    node = deepcopy(section)
    # Two English grammatical ordinals are encoded as n^(th), not powers.
    # The pinned Indonesian pivot already uses n in both reading instructions.
    for anchor in ('fs-id1170655228836','fs-id1170654937018'):
        matches = node.xpath('//*[@id=$anchor]', anchor=anchor)
        if not matches: continue
        para = matches[0]
        ordinal = para.findall('m:math',NS)[1]
        assert ''.join(ordinal.itertext()) == 'nth'
        ordinal.clear()
        row = E.SubElement(ordinal, '{'+M+'}mrow')
        E.SubElement(row, '{'+M+'}mi').text = 'n'
    # Inherited pivot correction: the list continues the immediately preceding
    # displayed n² and 9n² pair. Original English x²/9x² bytes stay in source/.
    for listing in node.xpath('//*[@id="fs-id1166422559187"]'):
        for token in listing.findall('c:item',NS)[2].iter('{'+M+'}mi'):
            assert token.text == 'x'
            token.text = 'n'
    return node
def subtree(unit, track): return E.parse(str(OUT / f'source/components/{unit}.{track}.cnxml')).getroot()
assembled = {}
source_first = deepcopy(subtree('a10-variable-bridge', 'en'))
for short in FIRST[1:]:
    node = subtree('a10-'+short, 'en')
    for c in list(node)[1:]: source_first.append(deepcopy(c))
assert normalized(source_first) == normalized(sections[0]), 'Opening component union is not complete first section'
for n, short in enumerate(REST, 1):
    assert normalized(subtree('a10-'+short, 'en')) == normalized(sections[n]), short

asset_lookup = {}
for unit in UNITS:
    p = OUT / f'provenance/component-inputs/{unit}.assets.json'
    if not p.exists(): continue
    for a in json.loads(p.read_text(encoding='utf-8'))['assets']:
        mid = a.get('source_media_id') or a.get('media_id') or a.get('source_binding',{}).get('media_id')
        for track, output in a['outputs'].items():
            rel = output['path'].replace('translation/', '', 1)
            assert sha((OUT/rel).read_bytes()) == output['sha256']
            asset_lookup[(mid, track)] = rel

for track in TRACKS:
    opening = deepcopy(subtree('a10-variable-bridge', track))
    for short in FIRST[1:]:
        for c in list(subtree('a10-'+short, track))[1:]: opening.append(deepcopy(c))
    assembled[track] = [opening] + [subtree('a10-'+k, track) for k in REST]
    for n, section in enumerate(assembled[track]):
        assert ids(section) == ids(sections[n]), (track, n, 'IDs/order')
        reference = mathematical_reference(sections[n])
        assert shape(section) == shape(reference), (track, n, 'hierarchy')
        for ordinal,(got,expected) in enumerate(zip(maths(section),maths(reference))):
            assert got == expected, (track, n, 'formula', ordinal, got, expected)
        write(f'source/assembled/{n+1:02}-{track}.cnxml', E.tostring(section, encoding='utf-8', xml_declaration=True))

SELECTED_IDS = {i for s in sections[:4] for i in ids(s)}
ALL_IDS = {i for i in ids(canonical)}
external_links = []
def esc(s): return html.escape(s or '', quote=True)
def render(el, track, parent=None):
    name = tag(el)
    ident = el.get('id')
    attrs = f' id="{esc(ident)}" data-source-id="{esc(ident)}"' if ident else ''
    for key in ('aria-label', 'summary'):
        if el.get(key): attrs += f' {key}="{esc(el.get(key))}"'
    def inner(): return esc(el.text) + ''.join(render(c,track,name)+esc(c.tail) for c in el)
    if el.tag.startswith('{'+M+'}'):
        node = deepcopy(el)
        for descendant in node.iter():
            descendant.tag = tag(descendant)
            if descendant.get('id'): descendant.set('data-source-id', descendant.get('id'))
        E.cleanup_namespaces(node)
        node.set('xmlns', M)
        return E.tostring(node, encoding='unicode', with_tail=False)
    if name == 'section': return f'<section{attrs}>{inner()}</section>'
    if name == 'title':
        level = 2 if parent == 'section' else 3
        return f'<h{level}{attrs}>{inner()}</h{level}>'
    if name in ('para', 'definition'): return f'<div class="{name}"{attrs}>{inner()}</div>'
    if name == 'emphasis': return f'<{ "strong" if el.get("effect")=="bold" else "em"}{attrs}>{inner()}</{ "strong" if el.get("effect")=="bold" else "em"}>'
    if name == 'term': return f'<dfn{attrs}>{inner()}</dfn>'
    if name == 'link':
        target = el.get('target-id')
        if target:
            if target in SELECTED_IDS: href = '#'+target
            else:
                assert target in ALL_IDS, ('unknown link target', target)
                href = f'source/m82453.en.cnxml#{target}'
                external_links.append(target)
            label = inner() or ('Pranala sumber' if track.startswith('jv') else 'Rujukan sumber')
            if target not in SELECTED_IDS: label += ' (English; outside this reader)'
            return f'<a{attrs} href="{esc(href)}">{label}</a>'
        href = el.get('url') or el.get('href')
        if href: return f'<a{attrs} href="{esc(href)}">{inner() or esc(href)}</a>'
        return f'<span{attrs}>{inner()}</span>'
    if name == 'table': return f'<div class="table-scroll"><table{attrs}>{inner()}</table></div>'
    if name in ('tgroup','colspec'): return inner()
    if name in ('thead','tbody','tfoot'): return f'<{name}{attrs}>{inner()}</{name}>'
    if name == 'row': return f'<tr{attrs}>{inner()}</tr>'
    if name == 'entry':
        in_head = any(tag(p)=='thead' for p in el.iterancestors())
        t = 'th' if in_head else 'td'
        if in_head: attrs += ' scope="col"'
        return f'<{t}{attrs}>{inner()}</{t}>'
    if name == 'list':
        t = 'ol' if el.get('list-type') in ('enumerated','ordered') else 'ul'
        return f'<{t}{attrs}>{inner()}</{t}>'
    if name == 'item': return f'<li{attrs}>{inner()}</li>'
    if name == 'example': return f'<section class="example"{attrs}><p class="source-label">'+('Tuladha saka sumber' if track.startswith('jv') else 'Contoh dari sumber')+f'</p>{inner()}</section>'
    if name == 'note': return f'<aside class="note"{attrs}>{inner()}</aside>'
    if name == 'exercise': return f'<div class="exercise"{attrs}>{inner()}</div>'
    if name == 'problem': return f'<div class="problem"{attrs}>{inner()}</div>'
    if name == 'solution':
        label = 'Wangsulan saka sumber' if track.startswith('jv') else 'Jawaban yang disediakan sumber'
        return f'<details class="solution"{attrs}><summary>{label}</summary>{inner()}</details>'
    if name == 'equation': return f'<div class="equation"{attrs}>{inner()}</div>'
    if name == 'media':
        path = asset_lookup[(ident,track)]
        alt = el.get('alt') or el.get('aria-label') or ''
        assert alt, ('un-described media', ident)
        # Image child IDs remain addressable although the rendered resource is bound by its media parent.
        child_ids = ''.join(f'<span id="{esc(c.get("id"))}" data-source-id="{esc(c.get("id"))}"></span>' for c in el.iterdescendants() if c.get('id'))
        return f'<figure{attrs}>{child_ids}<img src="{esc(path)}" alt="{esc(alt)}" loading="lazy"><details class="description"><summary>'+('Katrangan gambar' if track.startswith('jv') else 'Deskripsi gambar')+f'</summary><p>{esc(alt)}</p></details>'+adaptation_caption(ident,track)+'</figure>'
    if name == 'image': return ''
    if name == 'label': return f'<span class="label"{attrs}>{inner()}</span>'
    return f'<div class="cnxml-{name}"{attrs}>{inner()}</div>'

def page(title, lang, body):
    return f'<!doctype html>\n<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><link rel="stylesheet" href="reader.css"></head><body><a class="skip" href="#main">Skip to content</a><main id="main">{body}</main></body></html>\n'
def footer():
    return '<footer lang="en"><p>Adapted from OpenStax <cite>Elementary Algebra 2e</cite>, senior contributing authors Lynn Marecek, MaryAnne Anthony-Smith, and Andrea Honeycutt Mathis. Source and derivative: <a href="LICENSE.txt">CC BY-NC-SA 4.0</a>, subject to component-specific credits. OpenStax/Rice University does not endorse this translation.</p><p>Javanese wording and book-local supplements are AI-assisted provisional editorial work, not a linguistic certification. <a href="NOTICE.md">Credits and scope</a> · <a href="provenance/USAGE-WITNESSES.md">Terminology evidence</a> · <a href="PACKAGE.json">Exact coverage</a> · <a href="QA.json">QA</a>.</p></footer>'

titles = [s.find('c:title',NS).text for s in assembled['jv-academic']]
for track,(lang,label) in TRACKS.items():
    toc = '<ol>'+''.join(f'<li><a href="#{s.get("id")}">{esc(s.find("c:title",NS).text)}</a></li>' for s in assembled[track])+'</ol>'
    nav = '<nav aria-label="Register"><a href="index.html">Pambuka / Awal</a> · '+ ' · '.join(f'<a href="{t}.html" lang="{l}">{esc(n)}</a>' for t,(l,n) in TRACKS.items())+'</nav>'
    scope = '<p class="scope" lang="en">Four complete instructional source sections of module m82453. This is a partial book and partial module, not an entire chapter. Source exercises and supplied answers retain their IDs; open each answer only when ready.</p>'
    body = nav+f'<header><p class="eyebrow">A10 · Elementary Algebra 2e · 1.2</p><h1>{esc(label)}<br><span class="subtitle">Basa Aljabar</span></h1>{scope}</header><nav aria-label="Isi">{toc}</nav>'
    if track == 'id-academic': body += '<aside lang="id-ID">Jalur Bahasa Indonesia ini adalah jembatan terpisah. Jalur ini bukan bukti pemakaian istilah matematika dalam bahasa Jawa.</aside>'
    for n,s in enumerate(assembled[track]): body += render(s,track)
    body += '<section id="narration"><h2>Naskah wacan / Naskah narasi</h2><p lang="en">Written narration and SSML only. No recorded or synthesized audio is supplied. Components follow the reader order.</p><ol>'
    for u in UNITS:
        body += f'<li>{esc(u)}: <a href="narration/{u}.{track}.md">written narration</a> · <a href="narration/{u}.{track}.ssml">SSML</a></li>'
    body += '</ol></section>'+footer()
    write(f'{track}.html',page(label,lang,body))

section_counts = []
for s in sections[:4]:
    section_counts.append({'source_id':s.get('id'),'source_title':s.find('c:title',NS).text,
        'direct_children':len(s),'ids':len(ids(s)),
        'mathml':len(list(s.iter('{'+M+'}math'))),'media':len(s.findall('.//c:media',NS)),
        'exercises':len(s.findall('.//c:exercise',NS)),'source_solutions':len(s.findall('.//c:solution',NS))})
excluded = [{'id':s.get('id'),'title':s.findtext('c:title',default='Untitled source section',namespaces=NS)} for s in sections[4:]]
source_modules = [x['module'] for p in coverage['programs'] if p['program']=='A10' for x in p['modules']]
package = {'schema':'A10-recovered-reader-v1','locale':'jv-Latn-ID','date':'2026-09-04',
    'title':'Basa Aljabar — patang perangan saka Elementary Algebra 2e',
    'status':'complete_bounded_four_section_reader; partial_module_and_book',
    'completed_books':0,'complete_source_modules':0,'partial_source_modules':1,
    'a10_collection_modules':len(source_modules),'complete_instructional_sections':4,
    'covered_module':'m82453','register_tracks':list(TRACKS),'source_components':UNITS,
    'section_counts':section_counts,
    'totals':{key:sum(s[key] for s in section_counts) for key in ('direct_children','ids','mathml','media','exercises','source_solutions')},
    'completion_this_recovery':'Six later component fragments assembled and proved to be the complete first instructional section; this section and three later complete sections newly integrated into single-register offline readers with connected source links, narration inventories and deterministic gates.',
    'excluded':{'within_module_sections':excluded,'module_metadata_and_glossary':'not translated into this reader','other_a10_modules':[m for m in source_modules if m!='m82453'],'A00':'entirely outside this package'},
    'next_source': {'module':'m82453','section':sections[4].get('id'),'title':sections[4].find('c:title',NS).text,'first_child_id':next(c.get('id') for c in sections[4] if c.get('id'))},
    'pins':{'export_manifest_sha256':MANIFEST_SHA,'upstream_commit':PIN,'canonical_m82453_sha256':SOURCE_SHA,
       'recovered_coverage_sha256':coverage_entry['export_sha256'],'indonesian_pivot_release':'v1.0.2',
       'indonesian_pivot_m82453_sha256':'2c0b688d569044b128d589579e9ba7d871a0fb9ac7a670ac6f22d0ef2b66e635',
       'canon_lock_sha256':sha((OUT/'provenance/shared-canon-sources.lock.json').read_bytes()),
       'shared_terminology_sha256':sha((OUT/'provenance/shared-terminology.csv').read_bytes())},
    'source_url':source_url,'inputs_manifest':'provenance/RECOVERY-INPUTS.json',
    'source_answers':'Retained inside source-solution details; no generated answer is substituted.',
    'inherited_asset_adaptations':{'record':'provenance/ASSET-OVERRIDES.json','media_ids':['fs-id1167836692989','fs-id1169149089480'],'role':'Indonesian v1.0.2 substitution redraws, not unchanged canonical pixels; comparison originals separately retained.'},
    'math_language_exceptions':[{'ids':['fs-id1170655228836','fs-id1170654937018'],'change':'English n-th grammatical ordinal MathML becomes n in the already-pinned Indonesian/Javanese reading phrase pangkat n; expressions a^n are unaltered.'},
        {'ids':['fs-id1166422559187'],'change':'Inherited Indonesian pivot uses n² and 9n² in the third list item where canonical English prints x² and 9x². This matches the immediately preceding n² pair. Both are valid like-term examples; canonical bytes preserved unchanged.'}],
    'new_supplements':'index.html: one explicitly labeled, independently checked worked example; source files untouched.',
    'narration':{'written_files':27,'ssml_files':27,'recorded_audio':0,'synthesized_audio':0},
    'linguistic_status':'Evidence-based provisional; no claim of human approval, dialect-wide standardization or validated TTS pronunciation.',
    'license':'CC BY-NC-SA 4.0; inherited component credits apply'}
jwrite('PACKAGE.json',package)
jwrite('provenance/RECOVERY-INPUTS.json',{'schema':'hash-verified-narrow-export-selection-v1','export_manifest_sha256':MANIFEST_SHA,'files':RECEIPT})
jwrite('provenance/SOURCE-BOUNDARY.json',{'source_sha256':SOURCE_SHA,'four_sections':section_counts,'opening_complete_union':FIRST,'excluded_sections':excluded,'next_source':package['next_source']})
print(json.dumps({'built_tracks':list(TRACKS),'totals':package['totals'],'next_source':package['next_source'],'copied_inputs':len(RECEIPT)},indent=2))
