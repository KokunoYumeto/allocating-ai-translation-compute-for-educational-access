"""Incremental whole-source module pipeline; partial drafts never count as complete.

Translator mappings are exact, hash-locked source slots, not training data. A content
prefix includes all metadata and all selected original nodes, not cherry-picked prose.
"""
import argparse, copy, html, json, re, shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from build import C, M, L, STYLE, attrs, local, sha, write
from build_frontmatter import slots as standard_slots, XML_LANG, MD
from acquire_canon import Readable
from number_names import parse_name


def slots(root):
    yield from standard_slots(root)
    for i, node in enumerate(root.iter()):
        if node.get('summary'):
            yield i, node, 'summary', node.get('summary')


class Renderer:
    def __init__(self, module, spec):
        self.module, self.spec = module, spec
        self.target_types = {}

    def media_grid(self, e):
        img = e.find('{'+C+'}image')
        return self.spec.get('_image_tables', {}).get(Path(img.get('src')).name) if img is not None else None

    def inner(self, e, level):
        return html.escape(e.text or '') + ''.join(self.render(n, level)+html.escape(n.tail or '') for n in e)

    def render(self, e, level=2):
        tag, a = local(e), attrs(e)
        inner = lambda: self.inner(e, level)
        if e.tag.startswith('{'+M+'}'):
            m = copy.deepcopy(e)
            m.tail = None
            for n in m.iter(): n.tag = local(n)
            m.set('xmlns', M)
            return ET.tostring(m, encoding='unicode', short_empty_elements=False)
        if tag in ('section', 'note', 'example'):
            t = {'section':'section', 'note':'aside', 'example':'div'}[tag]
            children = html.escape(e.text or '')
            has_title = any(local(child) == 'title' for child in e)
            for child in e:
                depth = level if local(child) == 'title' else min(level+int(has_title), 6)
                children += self.render(child, depth)+html.escape(child.tail or '')
            return f'<{t}{a}>'+children+f'</{t}>'
        if tag == 'title': return f'<h{level}{a}>'+inner()+f'</h{level}>'
        if tag == 'emphasis':
            t = 'strong' if e.get('effect') == 'bold' else 'em'
            return f'<{t}{a}>'+inner()+f'</{t}>'
        if tag == 'link':
            if e.get('url'):
                href, label = e.get('url'), inner()
                assert href.startswith(('https://', 'http://'))
            else:
                document = e.get('document', self.module)
                target = e.get('target-id')
                assert target
                href = ('../'+document+'/index.html' if document != self.module else '')+'#'+target
                if document not in self.target_types:
                    reference = ET.parse(L.parent/'downloads/bn-Beng-BD/openstax-canonical/modules'/document/'index.cnxml')
                    self.target_types[document] = {n.get('id'):local(n) for n in reference.iter() if n.get('id')}
                kind = self.target_types[document][target]
                name = {'table':'ছক','figure':'চিত্র','exercise':'কাজ','example':'উদাহরণ'}.get(kind,'অংশ')
                label = inner() or '<span data-editorial="true">উৎসের '+name+' ('+target+')</span>'
            return f'<a{a} href="{html.escape(href, quote=True)}">'+label+'</a>'
        if tag == 'media':
            description = 'চিত্রের বর্ণনা: '+html.escape(e.get('alt', ''))
            grid = self.media_grid(e)
            if not grid: return f'<span{a} class="media-description">'+description+'</span>'
            table = '<div data-editorial="true" class="table-scroll" tabindex="0" role="region" aria-label="'+html.escape(grid['caption_bn'])+'"><table><caption>'+html.escape(grid['caption_bn'])+'</caption><thead><tr><th scope="col">+</th>'
            table += ''.join('<th scope="col">'+str(x)+'</th>' for x in grid['column_labels'])+'</tr></thead><tbody>'
            for label,row in zip(grid['row_labels'],grid['cells']):
                table += '<tr><th scope="row">'+str(label)+'</th>'+''.join('<td>'+('ফাঁকা' if n is None else str(n))+'</td>' for n in row)+'</tr>'
            table += '</tbody></table></div>'
            return f'<div{a} class="media-description"><p>'+description+'</p>'+table+'</div>'
        if tag == 'table':
            table = self.spec['tables'][e.get('id')]
            result = f'<table{a}><caption data-editorial="true">'+html.escape(table['caption_bn'])+'</caption>'
            group = e.find('{'+C+'}tgroup')
            if group.find('{'+C+'}thead') is None:
                result += '<thead data-editorial="true"><tr>'+''.join('<th scope="col">'+html.escape(s)+'</th>' for s in table['headers_bn'])+'</tr></thead>'
            for block in group:
                t = local(block)
                if t not in ('thead', 'tbody'): continue
                result += '<'+t+'>'
                for row in block:
                    assert len(row) == table['actual_columns']
                    result += '<tr>'
                    for index, cell in enumerate(row):
                        row_header = t == 'tbody' and index == 0 and table.get('row_headers')
                        ct = 'th' if t == 'thead' or row_header else 'td'
                        scope = (' scope="row"' if row_header else ' scope="col"') if ct == 'th' else ''
                        result += f'<{ct}{attrs(cell)}{scope}>'+self.inner(cell, level)+f'</{ct}>'
                    result += '</tr>'
                result += '</'+t+'>'
            result += '</table>'
            if table['actual_columns'] > 6:
                result = '<div class="table-scroll" tabindex="0" role="region" aria-label="'+html.escape(table['caption_bn'],quote=True)+'">'+result+'</div>'
            return result
        if tag in ('label', 'image'): return f'<span{a}></span>' if e.get('id') else ''
        if tag == 'newline': return '<br/>'
        if tag == 'list': t = 'ol' if e.get('list-type') == 'enumerated' else 'ul'
        elif tag == 'para' and any(local(n) in ('list','table','figure','note','section') or (local(n)=='media' and self.media_grid(n)) for n in e): t = 'div'
        else: t = {'para':'p','exercise':'div','problem':'div','solution':'div','equation':'div','term':'dfn','figure':'figure','caption':'figcaption','span':'span','item':'li','definition':'div','meaning':'p','glossary':'section'}.get(tag)
        if t is None: raise ValueError('Unmapped module node: '+tag)
        label = '<p class="source-label" data-editorial="true">উৎসের কাজ: '+e.get('id')+'</p>' if tag == 'exercise' else ''
        return f'<{t}{a}>'+label+inner()+f'</{t}>'


def build(module):
    specpath = L/'modules'/(module+'.json')
    spec = json.loads(specpath.read_text(encoding='utf-8'))
    sourcepath = L.parent/'downloads/bn-Beng-BD/openstax-canonical/modules'/module/'index.cnxml'
    assert sha(sourcepath.read_bytes()) == spec['source_sha256']
    indonesian = L.parent/'downloads/bn-Beng-BD/a00-id/modules'/module/'index.cnxml'
    assert sha(indonesian.read_bytes()) == spec['indonesian_sha256']
    whole = ET.parse(sourcepath).getroot()
    image_tables_sha = None
    if spec.get('image_tables_path'):
        tablepath = L/spec['image_tables_path']
        image_tables_sha = sha(tablepath.read_bytes())
        grids = json.loads(tablepath.read_text(encoding='utf-8'))
        original_alts = {Path(e.find('{'+C+'}image').get('src')).name:e.get('alt','') for e in whole.iter('{'+C+'}media')}
        for name,g in grids.items():
            assert name in original_alts
            if 'fill' in g:
                assert g['fill'] in ('blank','sum')
                g['cells'] = [[i+j if g['fill']=='sum' else None for j in g['column_labels']] for i in g['row_labels']]
            assert len(g['cells']) == len(g['row_labels'])
            for i,row in zip(g['row_labels'],g['cells']):
                assert len(row) == len(g['column_labels'])
                assert all(n is None or n == i+j for j,n in zip(g['column_labels'],row))
            if g.get('source_alt_column_check'):
                columns = [x.split(';') for x in re.findall('“([^”]+)”',original_alts[name])]
                assert [x.strip() for x in columns[0]] == ['+']+list(map(str,g['row_labels']))
                for j,column in enumerate(columns[1:]):
                    assert int(column[0]) == g['column_labels'][j]
                    values = [None if x.strip()=='null' else int(x) for x in column[1:]]
                    assert values == [row[j] for row in g['cells']], (name,j,values)
        spec['_image_tables'] = grids
    source = copy.deepcopy(whole)
    content = source.find('{'+C+'}content')
    prefix = spec.get('content_prefix_count', len(content))
    complete = prefix == len(content)
    assert 0 < prefix <= len(content)
    if not complete:
        content[:] = list(content)[:prefix]
        glossary = source.find('{'+C+'}glossary')
        if glossary is not None: source.remove(glossary)
    target = copy.deepcopy(source)
    stringpath = L/spec['strings']
    mapping = json.loads(stringpath.read_text(encoding='utf-8'))
    used, count = set(), 0
    for i, e, prop, v in slots(target):
        if local(e) in ('mi','mn','mo'): continue
        key = v.strip()
        assert key in mapping, ('Untranslated', i, e.get('id', local(e)), prop, key)
        new = v[:len(v)-len(v.lstrip())]+mapping[key]+v[len(v.rstrip()):]
        assert re.search('[\u0980-\u09ff]', mapping[key]), key
        if prop in ('alt','aria-label','summary'): e.set(prop,new)
        else: setattr(e,prop,new)
        used.add(key); count += 1
    # Later source slots may already be drafted, but unknown/orphan keys are forbidden.
    all_keys = {v.strip() for _, e, _, v in slots(whole) if local(e) not in ('mi','mn','mo')}
    assert set(mapping) <= all_keys, ('Orphan keys', set(mapping)-all_keys)
    if complete: assert used == set(mapping)
    for override in spec.get('slot_overrides', []):
        e = list(target.iter())[override['node_index']]
        assert local(e) == override['tag']
        assert getattr(e, override['property']) == override['expected']
        setattr(e, override['property'], override['translation'])
    target.set(XML_LANG, 'bn-Beng-BD')
    for a, b in zip(source.iter(), target.iter()):
        assert a.tag == b.tag
        omit = {'alt','aria-label','summary',XML_LANG}
        assert {k:v for k,v in a.attrib.items() if k not in omit} == {k:v for k,v in b.attrib.items() if k not in omit}
        if local(a) in ('mn','mo','mi','mspace','content-id','uuid'): assert a.text == b.text
        if local(a) == 'mtext' and not re.search('[A-Za-z]', a.text or ''): assert a.text == b.text
        if local(a) == 'mtext' and (a.text or '').strip() != 'base-10':
            assert re.findall(r'\d+',a.text or '') == re.findall(r'\d+',b.text or '')
    assert len(list(source.iter())) == len(list(target.iter()))
    ids = {e.get('id') for e in source.iter() if e.get('id')}
    assert ids == {e.get('id') for e in target.iter() if e.get('id')}
    exercises = {e.get('id'):e for e in target.iter('{'+C+'}exercise')}
    assert set(exercises) == {c['exercise'] for c in spec['answer_cases']}
    for case in spec['answer_cases']:
        solution = exercises[case['exercise']].find('{'+C+'}solution')
        absent = solution is None
        assert absent == case.get('source_solution_absent',False), case['exercise']
        text = '' if absent else ''.join(solution.itertext())+' '.join(e.get('alt','') for e in solution.iter('{'+C+'}media'))
        for fragment in case['required_solution_text']: assert fragment in text, (case, fragment)
        for name, value in case.get('number_names', {}).items():
            assert parse_name(name) == value and name in text
        problem = exercises[case['exercise']].find('{'+C+'}problem')
        if 'operand_pairs' in case:
            numeric = [n for n in problem.iter() if local(n)=='mn' or (case.get('include_currency') and local(n)=='mtext' and (n.text or '').startswith('$'))]
            assert [int(n.text.replace(',','').replace('$','')) for n in numeric] == case.get('question_numbers',[n for pair in case['operand_pairs'] for n in pair])
        if 'question_number_name' in case:
            assert case['question_number_name'] in ''.join(problem.itertext())
            assert parse_name(case['question_number_name']) == int(re.sub(r'\D', '', text))
        if 'model_groups' in case:
            assert sum(count*value for count, value in case['model_groups']) == int(text.strip())
        results = case.get('addition_results', [case['addition_result']] if 'addition_result' in case else [])
        if results:
            assert len(results) == len(case['operand_pairs'])
            for index, (operands, answer) in enumerate(zip(case['operand_pairs'], results)):
                assert sum(operands) == answer
                # Independent base-ten column calculation, including carrying.
                remaining, carry, place, accumulated = list(operands), 0, 1, 0
                while any(remaining) or carry:
                    subtotal = carry+sum(n%10 for n in remaining)
                    carry, digit = divmod(subtotal,10)
                    accumulated += digit*place
                    place *= 10
                    remaining = [n//10 for n in remaining]
                assert accumulated == answer
                if absent: continue
                if case.get('result_table_ids'):
                    table = next(n for n in solution.iter('{'+C+'}table') if n.get('id') == case['result_table_ids'][index])
                    final = list(table.iter('{'+M+'}mn'))[-1].text
                    assert int(final.replace(',','').strip().rstrip('.')) == answer
                elif case.get('result_only'):
                    found = re.findall(r'\d[\d,]*', text)
                    assert found and int(found[-1].replace(',','')) == answer, (case['exercise'], found)
                else:
                    expected = '+'.join(map(str,operands))+'='+str(answer)
                    assert expected in re.sub(r'[\s,]+', '', text), (case['exercise'], expected)
            if case.get('result_items') and not absent:
                assert [int(n.replace(',','')) for n in re.findall(r'\d[\d,]*',text)] == results
        if 'comparison' in case:
            answer = results[0]
            boundary = case['comparison']['boundary']
            relation = case['comparison']['relation']
            assert (answer >= boundary if relation=='at_least' else answer < boundary)
            assert boundary in case['question_numbers'] and 'হ্যাঁ' in text
        if 'image_table_pair' in case:
            names = [Path(n.get('src')).name for n in exercises[case['exercise']].iter('{'+C+'}image')]
            assert names == case['image_table_pair']
            first = spec['_image_tables'][names[0]]
            if not absent:
                second = spec['_image_tables'][names[1]]
                assert first['row_labels'] == second['row_labels'] and first['column_labels'] == second['column_labels']
                assert all(n is not None for row in second['cells'] for n in row)
        if 'perimeter_sides' in case:
            image = problem.find('.//{'+C+'}image')
            assert image is not None and Path(image.get('src')).name == case['problem_image']
            sides = case['perimeter_sides']
            assert all(n > 0 for n in sides) and sum(sides) == case['perimeter']
            if not absent: assert str(case['perimeter']) in text and case['unit_bn'] in text
            # Bind hand-inspected labels to the translated textual alternative.
            alt = problem.find('.//{'+C+'}media').get('alt')
            labels = [int(n) for n in re.findall(r'\d+',alt)]
            assert sorted(labels) == sorted(case.get('visible_side_labels',sides)), (case['exercise'],labels,sides)
            if 'inferred_side' in case:
                outer,inner,length = case['inferred_side']
                assert outer-inner == length and length in sides
    equalities = 0
    for math in target.iter('{'+M+'}math'):
        if math.find('.//{'+M+'}mtable') is not None: continue
        for equation in ''.join(math.itertext()).split(';'):
            equation = re.sub(r'[\s,]+','',equation).rstrip('.')
            if re.fullmatch(r'\d+(?:\+\d+)*=\d+(?:\+\d+)*',equation):
                left,right = equation.split('=')
                assert sum(map(int,left.split('+'))) == sum(map(int,right.split('+'))), equation
                equalities += 1
    matrix_cells = 0
    if spec.get('addition_matrix'):
        table = next(n for n in target.iter('{'+C+'}table') if n.get('id') == spec['addition_matrix'])
        group = table.find('{'+C+'}tgroup')
        assert [e.text for e in group.find('{'+C+'}thead')[0]] == ['+']+list(map(str,range(10)))
        for i,row in enumerate(group.find('{'+C+'}tbody')):
            assert int(row[0].text) == i
            assert [int(e.text) for e in row[1:]] == [i+j for j in range(10)]
            matrix_cells += len(row)-1
        assert matrix_cells == 100
    media = []
    for e in source.iter('{'+C+'}image'):
        name = Path(e.get('src')).name
        assert name in spec['visually_inspected_media']
        src = sourcepath.parents[2]/'media'/name
        dst = L/'translations/media'/name
        if not dst.exists(): shutil.copyfile(src, dst)
        assert src.read_bytes() == dst.read_bytes()
        media.append({'path':dst.relative_to(L).as_posix(),'sha256':sha(dst.read_bytes())})
    assert {Path(x['path']).name for x in media} == set(spec['visually_inspected_media'])
    canon = {x['id']:x for x in json.loads((L/'canon/download-receipt.json').read_text(encoding='utf-8'))}
    for ref in spec['canon_witnesses_consulted']:
        stem = L.parent/'downloads/bn-Beng-BD/canon'/ref
        raw, text = stem.with_suffix('.html').read_bytes(), stem.with_suffix('.txt').read_text(encoding='utf-8')
        assert sha(raw) == canon[ref]['sha256'] and sha(text.encode()) == canon[ref]['text_sha256']
        parser = Readable(); parser.feed(raw.decode('utf-8'))
        assert text == '\n'.join(' '.join(s.split()) for s in ''.join(parser.parts).splitlines() if s.strip())
    renderer = Renderer(module, spec)
    tcontent = target.find('{'+C+'}content')
    abstract = target.find('{'+C+'}metadata').find('{'+MD+'}abstract')
    title = target.findtext('{'+C+'}title')
    source_html = ''.join(renderer.render(e) for e in tcontent)
    glossary = target.find('{'+C+'}glossary')
    if glossary is not None:
        source_html += '<section id="bd-glossary"><h2 data-editorial="true">শব্দকোষ</h2>'+renderer.render(glossary)+'</section>'
    objective_html = ''.join(renderer.render(e) for e in abstract)
    status_bn = 'পূর্ণ উৎস-খসড়া' if complete else 'উৎসের ধারাবাহিক আংশিক খসড়া'
    footer = '<footer id="bd-attribution" lang="en"><h2>Attribution / উৎস ও পরিবর্তন</h2><p>OpenStax, Prealgebra 2e; Copyright Rice University; original author/reviewer credits retained in <a href="../m81241/index.html">the preface</a>. Frozen canonical bundle 38cae454e644abf9f0a623e876994553881597c9; Indonesian edition by KokunoYumeto. Bangladesh Bangla translation: Language Allocation, AI-assisted draft, 2026-08-31.</p><p><a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a>, subject to component notices. <a href="../../provenance/notices/canonical-LICENSE">License</a>. OpenStax and Rice University do not endorse this translation. No native-teacher, browser, PDF or screen-reader approval is claimed for this new draft.</p></footer>'
    style = STYLE.replace('../assets/', '../../assets/').replace('NumeracyBangla.ttf','NumeracyBanglaMath.ttf')+'\n.circled{list-style:none;padding-left:0}td{overflow-wrap:anywhere}.table-scroll{overflow-x:auto}.table-scroll table{min-width:540px}.table-scroll:focus{outline:3px solid #bc6900}'
    body = '<header><p>bn-Beng-BD · '+module+' · '+status_bn+'</p><h1>'+html.escape(title)+'</h1></header><aside><p>'+html.escape(spec['editorial_note_bn'])+'</p></aside><section id="bd-objectives"><h2>শেখার লক্ষ্য</h2>'+objective_html+'</section><article id="bd-source">'+source_html+'</article>'+footer
    page = '<!DOCTYPE html>\n<html lang="bn-Beng-BD"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><title>'+html.escape(title)+'</title><style>'+style+'</style></head><body><a class="skip" href="#bd-source">পাঠে যাই</a><main>'+body+'</main></body></html>\n'
    document = ET.fromstring(page.split('\n',1)[1])
    htmlids = [e.get('id') for e in document.iter() if e.get('id')]
    assert len(htmlids) == len(set(htmlids)) and ids <= set(htmlids)
    for p in document.iter('p'): assert not any(local(n) in ('p','div','ul','ol','table','figure','section') for n in list(p.iter())[1:])
    assert not list(document.iter('script')) and not re.search(r'TODO|TBD|\ufffd',page)
    assert all(e.get('scope') in ('row','col') for e in document.iter('th'))
    assert (L/'assets/NumeracyBanglaMath.ttf').is_file()
    headings = [int(e.tag[1]) for e in document.iter() if re.fullmatch('h[1-6]',e.tag)]
    assert headings[0] == 1 and all(b <= a+1 for a,b in zip(headings,headings[1:])), headings
    def source_text(e):
        s = e.text or ''
        if local(e) == 'media': s += 'চিত্রের বর্ণনা: '+e.get('alt','')
        for child in e: s += source_text(child)+(child.tail or '')
        return s
    def visible_text(e):
        if e.get('data-editorial') == 'true': return ''
        return (e.text or '')+''.join(visible_text(n)+(n.tail or '') for n in e)
    normalize = lambda s: re.sub(r'\s+', '', s)
    article = next(e for e in document.iter('article') if e.get('id') == 'bd-source')
    expected_source = source_text(tcontent)+(source_text(glossary) if glossary is not None else '')
    assert normalize(expected_source) == normalize(visible_text(article)), 'Lost/extra source text in HTML'
    objective_section = next(e for e in document.iter('section') if e.get('id') == 'bd-objectives')
    objective_section.remove(objective_section[0])
    assert normalize(source_text(abstract)) == normalize(visible_text(objective_section))
    links = 0
    out = L/'output'/module/'index.html'
    for a in document.iter('a'):
        href = a.get('href')
        if href.startswith(('http://','https://')): continue
        path, _, fragment = href.partition('#')
        otherids = htmlids
        if path:
            other = (out.parent/path).resolve()
            assert other.is_file(), href
            if fragment:
                otherdoc = ET.fromstring(other.read_text(encoding='utf-8').split('\n',1)[1])
                otherids = [n.get('id') for n in otherdoc.iter()]
        if fragment: assert fragment in otherids, href
        links += 1
    tr = ET.tostring(target, encoding='utf-8', xml_declaration=True)
    folder = 'complete_modules' if complete else 'draft_modules'
    trpath = L/'translations'/folder/module/'index.cnxml'
    trpath.parent.mkdir(parents=True,exist_ok=True); trpath.write_bytes(tr)
    write(out,page)
    receipt = {'module':module, 'status':('complete' if complete else 'partial')+'_source_translation_structural_math_pass',
               'entire_assignment_complete':False, 'whole_document_elements':len(list(whole.iter())),
               'selected_elements':len(list(source.iter())), 'selected_source_ids':len(ids),
               'content_prefix_count':prefix, 'total_content_children':len(whole.find('{'+C+'}content')),
               'selected_content_ids':[e.get('id') for e in content], 'translated_slots':count,
               'unique_used_strings':len(used), 'unique_drafted_strings':len(mapping),
               'source_exercises':len(exercises), 'source_supplied_solutions':len(list(target.iter('{'+C+'}solution'))),
               'answer_cases_verified':len(spec['answer_cases']), 'local_links_verified':links,
               'literal_addition_equalities_verified':equalities, 'addition_matrix_cells_verified':matrix_cells,
               'image_tables_verified':len(spec.get('_image_tables',{})), 'image_tables_sha256':image_tables_sha,
               'source_text_render_coverage_pass':True, 'indonesian_sha256':sha(indonesian.read_bytes()),
               'heading_hierarchy_pass':True,
               'source_sha256':sha(sourcepath.read_bytes()), 'translation_sha256':sha(tr),
               'translation_path':trpath.relative_to(L).as_posix(), 'html_sha256':sha(page.encode()),
               'strings_sha256':sha(stringpath.read_bytes()),'spec_sha256':sha(specpath.read_bytes()),
               'media':media, 'canon_witnesses_verified':spec['canon_witnesses_consulted'],
               'limits':['Partial source coverage is not a full module' if not complete else 'Source draft, not complete workflow',
                         'Separate expanded/child answers and PDF/human/accessibility checks remain queued']}
    write(out.parent/'qa-receipt.json',json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('module'); parser.add_argument('--inventory', action='store_true')
    parser.add_argument('--section'); args = parser.parse_args()
    if args.inventory:
        whole = ET.parse(L.parent/'downloads/bn-Beng-BD/openstax-canonical/modules'/args.module/'index.cnxml').getroot()
        nodes = set(whole.iter())
        if args.section:
            nodes = set(next(n for n in whole.iter() if n.get('id') == args.section).iter())
        seen = set()
        for i, e, prop, value in slots(whole):
            if e not in nodes or local(e) in ('mi','mn','mo') or value.strip() in seen: continue
            seen.add(value.strip())
            print(json.dumps([i,e.get('id',local(e)),prop,value.strip()],ensure_ascii=False))
    else:
        first = build(args.module); assert build(args.module) == first
        print(json.dumps(first,ensure_ascii=False,indent=2))
