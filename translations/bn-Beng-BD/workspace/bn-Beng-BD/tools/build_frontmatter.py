"""Source-preserving front-matter translation and offline semantic HTML.

Exact frozen source and explicit retained-name lists; no downloads or training export.
"""
import argparse, copy, html, json, re, shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from build import C, L, M, STYLE, attrs, local, sha, write
from acquire_canon import Readable

MD = 'http://cnx.rice.edu/mdml'
XML_LANG = '{http://www.w3.org/XML/1998/namespace}lang'


def source_path(module):
    return L.parent/'downloads/bn-Beng-BD/openstax-canonical/modules'/module/'index.cnxml'


def slots(root):
    for i, node in enumerate(root.iter()):
        for prop in ('text', 'tail', 'alt', 'aria-label'):
            value = node.get(prop) if prop in ('alt', 'aria-label') else getattr(node, prop)
            if value and re.search('[A-Za-z]', value) and local(node) not in ('content-id', 'uuid'):
                yield i, node, prop, value


def render_front(e, level=2):
    tag, a = local(e), attrs(e)
    def inside():
        return html.escape(e.text or '') + ''.join(render_front(n, level) + html.escape(n.tail or '') for n in e)
    if tag == 'section':
        parts = [html.escape(e.text or '')]
        for child in e:
            depth = level if local(child) == 'title' else level+1
            parts.append(render_front(child, depth) + html.escape(child.tail or ''))
        return f'<section{a}>'+''.join(parts)+'</section>'
    if tag == 'title':
        assert 2 <= level <= 6
        return f'<h{level}{a}>'+inside()+f'</h{level}>'
    if tag == 'emphasis':
        t = 'strong' if e.get('effect') == 'bold' else 'em'
        return f'<{t}{a}>'+inside()+f'</{t}>'
    if tag == 'media':
        return f'<span{a} class="media-description">চিত্রের বর্ণনা: '+html.escape(e.get('alt', ''))+'</span>'
    if tag == 'image':
        return ''
    if tag == 'newline':
        return '<br/>'
    if tag == 'list':
        t = 'ol' if e.get('list-type') == 'enumerated' else 'ul'
    elif tag == 'para' and any(local(n) in ('list', 'table', 'figure', 'section') for n in e):
        t = 'div'
    else:
        t = {'para':'p', 'item':'li', 'figure':'figure', 'caption':'figcaption'}.get(tag)
    if not t:
        raise ValueError('Unsupported front-matter node: '+tag)
    return f'<{t}{a}>'+inside()+f'</{t}>'


def build(module):
    specpath = L/'modules'/(module+'.json')
    spec = json.loads(specpath.read_text(encoding='utf-8'))
    original = source_path(module)
    assert sha(original.read_bytes()) == spec['source_sha256']
    indonesian = L.parent/'downloads/bn-Beng-BD/a00-id/modules'/module/'index.cnxml'
    assert sha(indonesian.read_bytes()) == spec['indonesian_sha256']
    source = ET.parse(original).getroot()
    target = copy.deepcopy(source)
    stringpath = L/spec['strings']
    mapping = json.loads(stringpath.read_text(encoding='utf-8'))
    retained = set(spec['retained_exact_strings'])
    assert not retained.intersection(mapping)
    used, kept, translated_slots = set(), set(), 0
    for i, node, prop, value in slots(target):
        key = value.strip()
        if key in retained:
            kept.add(key)
            continue
        assert key in mapping, ('Untranslated', i, node.get('id'), prop, key)
        replacement = mapping[key]
        assert re.search('[\u0980-\u09ff]', replacement), ('Not Bangla', key)
        new = value[:len(value)-len(value.lstrip())] + replacement + value[len(value.rstrip()):]
        if prop in ('alt', 'aria-label'):
            node.set(prop, new)
        else:
            setattr(node, prop, new)
        used.add(key)
        translated_slots += 1
    assert used == set(mapping), ('Unused strings', set(mapping)-used)
    assert kept == retained, ('Unused name exemptions', retained-kept)
    for override in spec.get('slot_overrides', []):
        node = list(target.iter())[override['node_index']]
        assert local(node) == override['tag'] and override['property'] in ('text', 'tail')
        assert getattr(node, override['property']) == override['expected']
        setattr(node, override['property'], override['translation'])
    target.set(XML_LANG, 'bn-Beng-BD')
    assert len(list(source.iter())) == len(list(target.iter()))
    for a, b in zip(source.iter(), target.iter()):
        assert a.tag == b.tag
        omissions = {'alt', 'aria-label', XML_LANG}
        assert {k:v for k,v in a.attrib.items() if k not in omissions} == {k:v for k,v in b.attrib.items() if k not in omissions}
        if local(a) in ('content-id', 'uuid', 'mn', 'mo', 'mspace'):
            assert a.text == b.text
    source_ids = [e.get('id') for e in source.iter() if e.get('id')]
    assert source_ids == [e.get('id') for e in target.iter() if e.get('id')]
    assert not list(source.iter('{'+C+'}exercise')), 'Front matter must not hide unanswered assessments'
    media = []
    for node in source.iter('{'+C+'}image'):
        name = Path(node.get('src')).name
        assert name in spec['visually_inspected_media']
        upstream = original.parents[2]/'media'/name
        destination = L/'translations/media'/name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            shutil.copyfile(upstream, destination)
        assert destination.read_bytes() == upstream.read_bytes()
        assert (L/'translations/complete_modules'/module/node.get('src')).resolve() == destination.resolve()
        media.append({'path':destination.relative_to(L).as_posix(), 'sha256':sha(destination.read_bytes())})
    assert set(spec['visually_inspected_media']) == {Path(x['path']).name for x in media}
    canon_receipts = {x['id']:x for x in json.loads((L/'canon/download-receipt.json').read_text(encoding='utf-8'))}
    for ref in spec['canon_witnesses_consulted']:
        record = canon_receipts[ref]
        stem = L.parent/'downloads/bn-Beng-BD/canon'/ref
        raw = stem.with_suffix('.html').read_bytes()
        text = stem.with_suffix('.txt').read_text(encoding='utf-8')
        assert sha(raw) == record['sha256'] and sha(text.encode()) == record['text_sha256']
        parser = Readable()
        parser.feed(raw.decode('utf-8'))
        assert text == '\n'.join(' '.join(line.split()) for line in ''.join(parser.parts).splitlines() if line.strip())
    tr = ET.tostring(target, encoding='utf-8', xml_declaration=True)
    trpath = L/'translations/complete_modules'/module/'index.cnxml'
    trpath.parent.mkdir(parents=True, exist_ok=True)
    content = target.find('{'+C+'}content')
    title = target.findtext('{'+C+'}title')
    navigation = '<nav aria-label="সংলগ্ন পাঠ"><a href="../m81241/index.html">প্রাক্‌কথন</a> · <a href="../m81242/index.html">অধ্যায়ের ভূমিকা</a> · <a href="../m81243/index.html">সংখ্যার প্রথম পাঠ</a></nav>'
    notice = '<footer id="bd-attribution" lang="en"><h2>Attribution / উৎস ও পরিবর্তন</h2><p>OpenStax, Prealgebra 2e; Copyright Rice University. Original author and reviewer credits are preserved in m81241. Canonical bundle 38cae454e644abf9f0a623e876994553881597c9, complete module '+module+'. Indonesian edition: KokunoYumeto project, pinned A00 commit 3de9207f56f8b5c57c017abf973fb04e00d740f1. Bangladesh Bangla translation and text-equivalent figures: Language Allocation project, AI-assisted draft, 2026-08-31.</p><p>Licensed under <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a>, subject to retained component notices. OpenStax and Rice University do not endorse this translation; their marks are not licensed. Original notices: <a href="../../provenance/notices/canonical-LICENSE">canonical license</a> and <a href="../../provenance/notices/a00-README.md">Indonesian edition README</a>. External services are not bundled, verified as currently available, or counted as translated.</p></footer>'
    body = '<header><p>bn-Beng-BD · A00 · '+module+' · পূর্ণ উৎস-খসড়া</p><h1>'+html.escape(title)+'</h1>'+navigation+'</header><aside><p>'+html.escape(spec['editorial_note_bn'])+'</p><p>এটি উৎসের বিশ্বস্ত অনুবাদ, শিশুর সংক্ষিপ্ত সহায়িকা নয়। উৎসের প্রথম পুরুষে বলা কথাগুলো মূল প্রকাশকের; অনুবাদ প্রকল্পের দাবি নয়। বাংলাদেশের শিক্ষক, ভাষা-সম্পাদক ও স্ক্রিন-রিডার ব্যবহারকারীর পর্যালোচনা এখনও বাকি।</p></aside><article id="bd-source">'+''.join(render_front(e) for e in content)+'</article>'+notice
    style = STYLE.replace('../assets/', '../../assets/').replace('NumeracyBangla.ttf', 'NumeracyBanglaMath.ttf')
    page = '<!DOCTYPE html>\n<html lang="bn-Beng-BD"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><title>'+html.escape(title)+'</title><style>'+style+'</style></head><body><a class="skip" href="#bd-source">উৎসের অনুবাদে যাই</a><main>'+body+'</main></body></html>\n'
    doc = ET.fromstring(page.split('\n', 1)[1])
    ids = [e.get('id') for e in doc.iter() if e.get('id')]
    assert len(ids) == len(set(ids)) and set(source_ids) <= set(ids)
    for p in doc.iter('p'):
        assert not any(local(n) in ('p', 'ul', 'ol', 'section', 'figure', 'div', 'table') for n in list(p.iter())[1:])
    # Compare rendered source text to the translated tree independently of markup.
    def texts(e):
        s = e.text or ''
        if local(e) == 'media':
            s += 'চিত্রের বর্ণনা: '+e.get('alt', '')
        for child in e:
            s += texts(child) + (child.tail or '')
        return s
    normalize = lambda s: re.sub(r'\s+', '', s)
    article = next(e for e in doc.iter('article') if e.get('id') == 'bd-source')
    assert normalize(texts(content)) == normalize(''.join(article.itertext()))
    headings = [int(e.tag[1]) for e in doc.iter() if re.fullmatch('h[1-6]', e.tag)]
    assert headings[0] == 1 and all(b <= a+1 for a, b in zip(headings, headings[1:]))
    out = L/'output'/module/'index.html'
    assert not list(doc.iter('script')) and not re.search(r'TODO|TBD|\ufffd', page)
    local_references = 0
    for element in doc.iter('a'):
        href = element.get('href', '')
        if href.startswith(('https://', 'http://')):
            continue
        path, _, fragment = href.partition('#')
        if path:
            destination = (out.parent/path).resolve()
            assert destination.is_file(), ('Missing local link', href)
            if fragment:
                other = ET.fromstring(destination.read_text(encoding='utf-8').split('\n', 1)[1])
                assert fragment in {n.get('id') for n in other.iter()}
        else:
            assert fragment in ids
        local_references += 1
    fonts = re.findall(r'url\("([^"]+)"\)', style)
    assert len(fonts) == 1
    assert (out.parent/fonts[0]).resolve().is_file()
    trpath.write_bytes(tr)
    write(out, page)
    receipt = {'module':module, 'status':'complete_source_translation_structural_math_pass',
               'entire_assignment_complete':False, 'source_sha256':sha(original.read_bytes()),
               'indonesian_sha256':sha(indonesian.read_bytes()), 'whole_document_elements':len(list(source.iter())),
               'all_source_ids':len(source_ids), 'source_exercises':0, 'source_supplied_solutions':0,
               'translated_slots':translated_slots, 'unique_translated_strings':len(used),
               'exact_retained_name_strings':len(kept), 'translation_sha256':sha(tr), 'html_sha256':sha(page.encode()),
               'guarded_grammar_overrides':spec.get('slot_overrides', []),
               'strings_sha256':sha(stringpath.read_bytes()), 'spec_sha256':sha(specpath.read_bytes()),
               'local_links_verified':local_references, 'local_fonts_verified':len(fonts),
               'canon_witnesses_verified':spec['canon_witnesses_consulted'],
               'source_text_render_coverage_pass':True, 'heading_hierarchy_pass':True,
               'original_media_references_verified':len(media), 'media':media,
               'limits':['AI-assisted draft; native Bangladesh teacher/editorial review pending',
                         'HTML structural/text checks, not browser or screen-reader testing',
                         'This new front matter has no PDF edition yet',
                         'Historical publisher statements and external services are not current claims']}
    write(out.parent/'qa-receipt.json', json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('modules', nargs='+')
    parser.add_argument('--inventory', action='store_true')
    args = parser.parse_args()
    for module in args.modules:
        if args.inventory:
            seen = set()
            for i, node, prop, value in slots(ET.parse(source_path(module)).getroot()):
                key = value.strip()
                if key not in seen:
                    print(json.dumps([i, node.get('id', local(node)), prop, key], ensure_ascii=False))
                    seen.add(key)
        else:
            first = build(module)
            assert build(module) == first
            print(json.dumps(first, ensure_ascii=False, indent=2))
