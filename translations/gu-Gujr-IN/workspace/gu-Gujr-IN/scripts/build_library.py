"""Build an honest, incrementally translated A00/A10 offline source library."""
from collections import Counter
import copy
import csv
import hashlib
from html import escape as esc
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

from localized_figures import localized_svg
from worked_answer_figures import answer_table, base10_model, equal_groups_model, hundreds_model
from library_review_metadata import media_metadata

ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT/'gu-Gujr-IN'
OUT = LANG/'output/library'
C = 'http://cnx.rice.edu/cnxml'
M = 'http://www.w3.org/1998/Math/MathML'
ET.register_namespace('', C)
ET.register_namespace('m', M)
CANONICAL = ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9'


def tag(element):
    return element.tag.rsplit('}', 1)[-1]


def math_html(element, token_replacements=None):
    name = tag(element)
    attributes = ''.join(f' {esc(k)}="{esc(v)}"' for k,v in element.attrib.items())
    if name == 'math':
        attributes += f' xmlns="{M}"'
    if name == 'menclose' and element.get('notation')=='longdiv':
        # The local browser did not draw menclose(longdiv). Preserve the source
        # element/tokens and explicitly draw the missing enclosure.
        attributes += ' style="border-top:1px solid currentColor;border-left:1px solid currentColor;padding:.08em .16em 0 .18em;margin-left:.18em;border-top-left-radius:.28em"'
    text = element.text or ''
    if name == 'mn' and token_replacements and text in token_replacements:
        text = token_replacements[text]
    return f'<{name}{attributes}>'+esc(text)+''.join(math_html(c,token_replacements)+esc(c.tail or '') for c in element)+f'</{name}>'


def wrap(title, content, nav='', supplement=False):
    description = 'મૂળ પાઠથી અલગ સમજ અને ઉકેલનું પૂરક.' if supplement else 'સ્રોતને અનુસરતો અનુવાદ.'
    return f'''<!doctype html>
<html lang="gu-Gujr-IN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | ગુજરાતી ગણિત</title><link rel="stylesheet" href="../assets/style.css"><link rel="stylesheet" href="library.css"></head><body><a class="skip" href="#main">મુખ્ય પાઠ પર જાઓ</a><header><p class="eyebrow">ગુજરાતી · A00 / A10 · સમગ્ર અનુવાદ ચાલુ છે</p><h1>{esc(title)}</h1><p>{description} ગુજરાતી શિક્ષકની સમીક્ષા બાકી છે.</p></header><nav aria-label="વાંચનનાં પાનાં"><a href="index.html">પુસ્તકની સૂચિ</a><a href="../index.html">સરળ અભ્યાસ અને તપાસ</a><a href="../notices.html">સ્રોત અને શ્રેય</a>{nav}</nav><main id="main" class="source">{content}</main><footer>OpenStax / Rice University; Indonesian adaptation: KokunoYumeto. Gujarati translation: Language Allocation / OpenAI Codex. CC BY-NC-SA 4.0, component notices apply. No endorsement or native-review claim. <a href="../notices.html">પૂર્ણ શ્રેય અને શરતો</a>.</footer></body></html>'''


class Renderer:
    def __init__(self, module_id, root, metadata=None, module_pages=None):
        self.module_id = module_id
        self.lookup = {e.get('id'): e for e in root.iter() if e.get('id')}
        self.media = []
        self.counter = 0
        self.metadata = metadata or {}
        self.module_pages = module_pages or {}
        self.parents = {child: parent for parent in root.iter() for child in parent}
        self.text_replacement_rules = self.metadata.get('text_replacements', [])
        self.text_rule_seen = Counter()
        self.text_rule_applied = Counter()
        self.math_replacement_hits = Counter()

    def owner_id(self, element):
        current = element
        while current is not None:
            if current.get('id'):
                return current.get('id')
            current = self.parents.get(current)
        return None

    def replacement_text(self, element):
        owner = self.owner_id(element)
        for index, rule in enumerate(self.text_replacement_rules):
            if owner != rule['owner_id'] or tag(element) != rule['tag']:
                continue
            if rule.get('class') is not None and element.get('class') != rule['class']:
                continue
            if (element.text or '') != rule['source_text']:
                continue
            self.text_rule_seen[index] += 1
            if self.text_rule_seen[index] == rule['occurrence']:
                self.text_rule_applied[index] += 1
                return rule['replacement_text']
        return None

    def assert_overrides_applied(self):
        for index, rule in enumerate(self.text_replacement_rules):
            assert self.text_rule_applied[index] == 1, ('Text replacement not applied exactly once', rule, self.text_rule_applied[index])
        for owner, replacements in self.metadata.get('math_token_replacements', {}).items():
            for source in replacements:
                assert self.math_replacement_hits[(owner, source)] > 0, ('Math-token replacement not applied', owner, source)

    def inner(self, element, level=2, in_header=False):
        return esc(element.text or '')+''.join(self.render(c, level, in_header)+esc(c.tail or '') for c in element)

    def render(self, element, level=2, in_header=False):
        rendered = self.render_element(element,level,in_header)
        correction = self.metadata.get('errata',{}).get(element.get('id'))
        if correction:
            rendered += '<aside class="note source-correction" aria-label="મૂળ સ્રોતની ભૂલ અંગે નોંધ"><strong>મૂળ સ્રોતની ભૂલ અંગે નોંધ:</strong> '+esc(correction['correction_gu'])+'</aside>'
        bridge=self.metadata.get('reader_bridges',{}).get(element.get('id'))
        if bridge:
            rendered += '<aside class="note reader-bridge" aria-label="વાંચવામાં મદદરૂપ નોંધ"><strong>વાંચવામાં મદદરૂપ નોંધ:</strong> '+esc(bridge['reader_note_gu'])+'</aside>'
        return rendered

    def render_element(self, element, level=2, in_header=False):
        name = tag(element)
        if element.tag.startswith('{'+M+'}'):
            owner = self.owner_id(element)
            replacements = self.metadata.get('math_token_replacements', {}).get(owner, {})
            for token in element.iter('{'+M+'}mn'):
                if (token.text or '') in replacements:
                    self.math_replacement_hits[(owner, token.text or '')] += 1
            rendered = math_html(element,replacements)
            # MathML mtext does not line-wrap like HTML prose. Keep the complete
            # formula accessible in a named local scroller instead of widening
            # the phone document for long prose or several grouped expressions.
            long_prose=any(len(e.text or '')>=30 for e in element.iter('{'+M+'}mtext'))
            token_length=sum(len((e.text or '').strip()) for e in element.iter())
            additive_operators=sum(e.tag=='{'+M+'}mo' and (e.text or '').strip() in ('+','−') for e in element.iter())
            long_formula=token_length>=24 or (token_length>=20 and additive_operators>=5)
            if name=='math' and (element.find('.//{'+M+'}mtable') is not None or long_prose or long_formula):
                return '<div class="math-scroll" role="region" aria-label="ગણિતની ગોઠવણી; જરૂર પડે તો આડું ખસેડીને વાંચો" tabindex="0" style="max-width:100%;overflow-x:auto;margin:.6rem 0">'+rendered+'</div>'
            return rendered
        identifier = element.get('id')
        attrs = f' id="{esc(identifier)}"' if identifier else ''
        if name == 'section':
            body = esc(element.text or '')+''.join(self.render(c, level if tag(c)=='title' else level+1)+esc(c.tail or '') for c in element)
            return f'<section{attrs}>{body}</section>'
        if name == 'title':
            return f'<h{min(level,6)}{attrs}>{self.inner(element,level)}</h{min(level,6)}>'
        if name == 'link':
            target = element.get('target-id')
            document = element.get('document')
            content = self.inner(element,level)
            if target:
                destination = self.lookup.get(target)
                if not content.strip():
                    kind = tag(destination) if destination is not None else 'reference'
                    content = {'figure':'આકૃતિ','example':'ઉદાહરણ','table':'કોષ્ટક','exercise':'અભ્યાસ'}.get(kind,'સંદર્ભ')
                    content += ' '+esc(target.rsplit('_',1)[-1] if target.startswith('CNX_') else target)
                if document and document != self.module_id:
                    if document not in self.module_pages:
                        return f'<span{attrs} class="pending-reference">{content} (સંબંધિત પાઠનો અનુવાદ બાકી)</span>'
                    return f'<a{attrs} href="{esc(self.module_pages[document])}#{esc(target)}">{content}</a>'
                return f'<a{attrs} href="#{esc(target)}">{content}</a>'
            url = element.get('url') or element.get('document')
            if not url:
                raise ValueError(('Unsupported source link', element.attrib))
            if url in self.module_pages:
                return f'<a{attrs} href="{esc(self.module_pages[url])}">{content or esc(url)}</a>'
            if not url.startswith(('https://','http://')):
                return f'<span{attrs} class="pending-reference">{content or esc(url)} (સંબંધિત અનુવાદ બાકી)</span>'
            return f'<a{attrs} href="{esc(url)}">{content or "વધારાનો મૂળ સ્રોત (ઇન્ટરનેટ જરૂરી)"}</a>'
        if name == 'media':
            self.counter += 1
            unique = identifier or f'{self.module_id}-media-{self.counter}'
            alt = element.get('alt') or element.get('aria-label') or ''
            alt = self.metadata.get('corrected_alternatives',{}).get(identifier,alt)
            images = list(element.iter('{'+C+'}image'))
            body = ''
            for image in images:
                filename = Path(image.get('src','')).name
                localized = localized_svg(filename,alt,unique+'-redraw')
                self_check = self.metadata.get('self_check_table')
                if self_check and filename == Path(self_check['source_image']).name:
                    source = CANONICAL/'media'/filename
                    assert hashlib.sha256(source.read_bytes()).hexdigest() == self_check['source_image_sha256']
                    localized = '<div class="table-scroll" role="region" aria-label="પોતાની સમજની તપાસ" tabindex="0"><table><thead><tr>'+''.join('<th scope="col">'+esc(h)+'</th>' for h in self_check['headers'])+'</tr></thead><tbody>'+''.join('<tr><th scope="row">'+esc(r)+'</th><td></td><td></td><td></td></tr>' for r in self_check['rows'])+'</tbody></table></div>'
                chart = self.metadata.get('accessible_charts', {}).get(filename)
                if chart:
                    source = CANONICAL/'media'/filename
                    assert hashlib.sha256(source.read_bytes()).hexdigest() == chart['source_image_sha256']
                    operation=chart.get('operation','×')
                    caption={'+':'સરવાળાનું કોષ્ટક','−':'બાદબાકીનું કોષ્ટક','×':'ગુણાકારનું કોષ્ટક','÷':'ભાગાકારનું કોષ્ટક'}[operation]
                    localized = answer_table({'caption_gu': caption, 'corner_gu': operation,
                                              'row_headers': chart['row_headers'], 'column_headers': chart['column_headers'],
                                              'cells': chart['visible_cells']})
                if filename == 'number-line.svg':
                    localized = (LANG/'assets/number-line.svg').read_text(encoding='utf-8').replace('line-title',unique+'-title').replace('line-description',unique+'-description')
                if localized:
                    body += localized
                    mode = 'localized_svg' if '<svg' in localized else 'localized_semantic_diagram'
                else:
                    source = CANONICAL/'media'/filename
                    if not source.is_file():
                        raise FileNotFoundError(source)
                    destination = OUT/'media'/filename
                    if not destination.is_file() or hashlib.sha256(destination.read_bytes()).digest()!=hashlib.sha256(source.read_bytes()).digest():
                        shutil.copyfile(source,destination)
                    body += f'<img loading="lazy" src="media/{esc(filename)}" alt="{esc(alt)}">'
                    mode = 'original_image_with_gujarati_alternative'
                self.media.append({'source':image.get('src'), 'media_id':unique, 'mode':mode,'alt':alt})
            return f'<div{attrs} class="source-media">{body}<p class="figure-description">{esc(alt)}</p></div>'
        if name == 'image':
            raise ValueError('Image outside a media wrapper')
        if name == 'table':
            label = self.metadata.get('corrected_table_names',{}).get(identifier) or element.get('aria-label') or element.get('summary') or 'કોષ્ટક'
            return f'<div class="table-scroll" role="region" aria-label="કોષ્ટક; જરૂર પડે તો આડું ખસેડીને વાંચો" tabindex="0"><table{attrs} aria-label="{esc(label)}">{self.inner(element,level)}</table></div>'
        if name == 'tgroup':
            return self.inner(element,level)
        if name == 'colspec':
            return ''
        if name in ('thead','tbody'):
            return f'<{name}{attrs}>'+self.inner(element,level,name=='thead')+f'</{name}>'
        if name == 'row':
            return f'<tr{attrs}>'+self.inner(element,level,in_header)+'</tr>'
        if name == 'entry':
            cell = 'th' if in_header else 'td'
            if in_header:
                attrs += ' scope="col"'
            if element.get('morecols'):
                attrs += f' colspan="{int(element.get("morecols"))+1}"'
            if element.get('morerows'):
                attrs += f' rowspan="{int(element.get("morerows"))+1}"'
            return f'<{cell}{attrs}>'+self.inner(element,level,in_header)+f'</{cell}>'
        if name in ('newline','space'):
            return '<br>' if name=='newline' else ' '
        if name == 'label':
            return f'<span{attrs} class="source-label">{self.inner(element,level)}</span>'
        if name == 'list':
            listtag = 'ol' if element.get('list-type')=='enumerated' else 'ul'
            return f'<{listtag}{attrs}>'+self.inner(element,level)+f'</{listtag}>'
        if name == 'para':
            # CNXML permits tables/media inside paragraphs; a div avoids invalid
            # nested HTML paragraphs without dropping source IDs or reading order.
            return f'<div{attrs} class="source-paragraph">{self.inner(element,level)}</div>'
        if name == 'glossary':
            return f'<section{attrs}><h2>શબ્દાર્થ</h2>{self.inner(element,3)}</section>'
        if name == 'definition':
            return f'<div{attrs} class="definition">{self.inner(element,level)}</div>'
        mapped = {'term':'strong','emphasis':'em','span':'span','item':'li','figure':'figure','caption':'figcaption','meaning':'div'}
        htmltag = mapped.get(name,'div')
        replacement = self.replacement_text(element)
        content = esc(replacement) if replacement is not None else self.inner(element,level)
        return f'<{htmltag}{attrs} class="{esc(name)}">{content}</{htmltag}>'


def merge_reader_metadata(metadata, addition):
    allowed = {'errata', 'corrected_alternatives', 'corrected_table_names',
               'reader_bridges', 'math_token_replacements', 'text_replacements',
               'self_check_table'}
    unexpected = set(addition) - allowed
    assert not unexpected, ('Unexpected reader metadata fields', sorted(unexpected))
    for field, value in addition.items():
        if field == 'self_check_table':
            metadata[field] = value
        elif field == 'text_replacements':
            metadata.setdefault(field, []).extend(value)
        else:
            metadata.setdefault(field, {}).update(value)


def compose(row, recipe):
    source = ET.parse(ROOT/row['canonical_path']).getroot()
    if recipe.get('complete_module_file'):
        result = ET.parse(LANG/recipe['complete_module_file']).getroot()
        assert result.findtext('{'+C+'}title')==recipe['title'], 'Reader title must match translated source title'
        return result, source
    result = ET.Element(source.tag, dict(source.attrib))
    result.set('{http://www.w3.org/XML/1998/namespace}lang','gu-Gujr-IN')
    ET.SubElement(result,'{'+C+'}title').text = recipe['title']
    metadata = json.loads((LANG/recipe['metadata_file']).read_text(encoding='utf-8')) if recipe.get('metadata_file') else {}
    if metadata.get('metadata_cnxml'):
        result.append(ET.fromstring(metadata['metadata_cnxml']))
    content = ET.SubElement(result,'{'+C+'}content')
    translated = {}
    for name in recipe['section_files']:
        for section in ET.parse(LANG/name).getroot().find('{'+C+'}content'):
            assert section.get('id') not in translated, 'Overlapping source sections'
            translated[section.get('id')] = section
    for section in source.find('{'+C+'}content'):
        if section.get('id') in translated:
            content.append(copy.deepcopy(translated[section.get('id')]))
    assert len(content)==len(translated), 'Unknown section in recipe'
    if metadata.get('glossary_cnxml'):
        result.append(ET.fromstring(metadata['glossary_cnxml']))
    return result, source


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'media').mkdir(exist_ok=True)
    rows = list(csv.DictReader((LANG/'source-module-map.csv').open(encoding='utf-8')))
    recipes = json.loads((LANG/'library-recipes.json').read_text(encoding='utf-8'))
    module_pages = {key.split(':')[1]:key.lower().replace(':','-')+'.html' for key in recipes}
    coverage = []
    for row in rows:
        key = row['program']+':'+row['module_id']
        record = {'program':row['program'],'module_id':row['module_id'],'source_title':row['source_title'],
                  'source_translation':'not_started','workflow':'not_started','path':None}
        if key in recipes:
            recipe = recipes[key]
            root,source = compose(row,recipe)
            sections = [e.get('id') for e in source.findall('./{'+C+'}content/{'+C+'}section')]
            present = [e.get('id') for e in root.findall('./{'+C+'}content/{'+C+'}section')]
            metadata = json.loads((LANG/recipe['metadata_file']).read_text(encoding='utf-8')) if recipe.get('metadata_file') else {}
            if recipe.get('errata_file'):
                metadata['errata'] = json.loads((LANG/recipe['errata_file']).read_text(encoding='utf-8'))['entries']
                metadata['corrected_alternatives'] = {identifier:item['corrected_alt_gu'] for identifier,item in metadata['errata'].items() if item.get('corrected_alt_gu')}
            if recipe.get('media_review'):
                review = json.loads((LANG/recipe['media_review']).read_text(encoding='utf-8'))
                normalized = media_metadata(review)
                merge_reader_metadata(metadata,normalized)
            if recipe.get('reader_overlay'):
                overlay_path = LANG/recipe['reader_overlay']
                overlay = json.loads(overlay_path.read_text(encoding='utf-8'))
                assert overlay['module_id'] == row['module_id']
                assert hashlib.sha256((ROOT/row['authority_path']).read_bytes()).hexdigest() == overlay['source_sha256']
                assert hashlib.sha256((LANG/recipe['complete_module_file']).read_bytes()).hexdigest() == overlay['translation_sha256']
                assert hashlib.sha256((LANG/recipe['media_review']).read_bytes()).hexdigest() == overlay['media_review_sha256']
                merge_reader_metadata(metadata,overlay['metadata'])
            renderer = Renderer(row['module_id'],root,metadata,module_pages)
            draft_complete = bool(recipe.get('complete_module_file')) or (present==sections and bool(recipe.get('metadata_file')))
            scope = 'આખા પાઠનો અનુવાદિત પ્રારૂપ અહીં છે.' if draft_complete else f'અહીં {len(present)} / {len(sections)} મુખ્ય વિભાગો છે.'
            body = f'<p class="note">{scope} ચિત્રો, ઉકેલો અને સુલભતાની સમીક્ષા અલગથી ચાલુ છે. આખી સોંપણી હજુ પૂરી નથી.</p>'
            body += '<ul class="module-contents">'+''.join(f'<li><a href="#{e.get("id")}">{esc("".join(e.find("{"+C+"}title").itertext()) if e.find("{"+C+"}title") is not None else "અભ્યાસ")}</a></li>' for e in root.findall('./{'+C+'}content/{'+C+'}section'))+'</ul>'
            for content in root:
                if tag(content) in ('content','glossary'):
                    body += renderer.render(content)
                elif tag(content)=='metadata':
                    abstract = next((e for e in content.iter() if tag(e)=='abstract'),None)
                    if abstract is not None:
                        body += '<section><h2>શીખવાના હેતુઓ</h2>'+renderer.inner(abstract)+'</section>'
            renderer.assert_overrides_applied()
            name=row['program'].lower()+'-'+row['module_id']+'.html'
            extra_nav = ''
            if recipe.get('worked_companion'):
                supplement = json.loads((LANG/recipe['worked_companion']).read_text(encoding='utf-8'))
                assert supplement['book']==row['program'] and supplement['module']==row['module_id']
                missing = {e.get('id') for e in root.iter('{'+C+'}exercise') if e.find('{'+C+'}solution') is None}
                supplied = [item['source_exercise'] for item in supplement['items']]
                assert len(supplied)==len(set(supplied)) and set(supplied)==missing, (key,'Incomplete added answers')
                answers_name = name.replace('.html','-answers.html')
                extra_nav = f'<a href="{answers_name}">ઉમેરેલા પગથિયાવાર ઉકેલો</a>'
                answers_body = '<p class="note">આ અલગ પૂરકમાં મૂળ સ્રોતે જવાબ ન આપેલા અભ્યાસોના પગથિયાવાર ઉકેલો ઉમેર્યા છે. મૂળ પાઠમાં આપેલા ઉકેલો ત્યાં જ રાખ્યા છે. આ પૂરક મૂળ સ્રોતનો ભાગ નથી.</p>'
                if supplement.get('note_gu'):
                    answers_body += '<p>'+esc(supplement['note_gu'])+'</p>'
                answers_body += '<ol class="answer-index">'
                for number,item in enumerate(supplement['items'],1):
                    answers_body += f'<li><a href="#answer-{esc(item["source_exercise"])}">અભ્યાસ {number}</a></li>'
                answers_body += '</ol>'
                for number,item in enumerate(supplement['items'],1):
                    sid = esc(item['source_exercise'])
                    answers_body += f'<section id="answer-{sid}" class="worked-answer"><h2>અભ્યાસ {number}</h2><p><a href="{name}#{sid}">મૂળ પાઠમાં આ પ્રશ્ન જુઓ</a></p><p>{esc(item["question_gu"])}</p>'
                    if item.get('source_notation_mathml'):
                        notation=ET.fromstring(item['source_notation_mathml'])
                        assert notation.tag=='{'+M+'}math'
                        answers_body += '<div class="answer-source-notation">'+math_html(notation)+'</div>'
                    answers_body += '<ol>'+''.join('<li>'+esc(step)+'</li>' for step in item['steps'])+'</ol><p><strong>જવાબ:</strong> '+esc(item['answer'])+'</p>'
                    if item.get('english_answer'):
                        answers_body += '<p>મૂળ પ્રશ્ન મુજબ અંગ્રેજી શબ્દરૂપ: <span lang="en">'+esc(item['english_answer'])+'</span></p>'
                    if item.get('answer_table'):
                        answers_body += answer_table(item['answer_table'])
                    if item.get('base10_model'):
                        answers_body += base10_model(item['base10_model'])
                    if item.get('equal_groups_model'):
                        answers_body += equal_groups_model(item['equal_groups_model'])
                    if item.get('hundreds_model'):
                        answers_body += hundreds_model(item['hundreds_model'])
                    answers_body += '</section>'
                (OUT/answers_name).write_text(wrap(recipe['title']+' — ઉમેરેલા ઉકેલો',answers_body,f'<a href="{name}">મૂળ પાઠ</a>',supplement=True),encoding='utf-8',newline='\n')
                record['added_worked_answers'] = {'count':len(supplied),'path':'library/'+answers_name,'role':supplement['role'],'coverage':'all_source_omitted_answers','source_solutions_expansion_complete':False}
            (OUT/name).write_text(wrap(recipe['title'],body,extra_nav),encoding='utf-8',newline='\n')
            record.update({'path':'library/'+name, 'source_translation':'partial', 'workflow':'in_progress',
                           'sections_present':present,'sections_expected':sections,'review_state':recipe['review_state'],
                           'media':renderer.media,'math_expressions':sum(tag(e)=='math' for e in root.iter())})
            if draft_complete:
                record['source_translation'] = 'draft_complete_pending_review'
            record['target_title'] = recipe['title']
            ET.ElementTree(root).write(LANG/'translations'/f'{row["program"].lower()}-{row["module_id"]}-assembled.gu.cnxml',encoding='utf-8',xml_declaration=True)
        coverage.append(record)
    index = '<p>આ આખી સોંપણીની સૂચિ છે. પૂર્ણતાનો દાવો માત્ર આખા પાઠ અને તેની સમીક્ષા પૂરી થયા પછી જ કરવામાં આવશે.</p>'
    draft_pdf=LANG/'output/tagged-screen-pdf/a00-m81243.pdf'
    if draft_pdf.is_file():
        pdf_check=json.loads((LANG/'reviews/a00-m81243-tagged-pdf-qa.json').read_text(encoding='utf-8'))
        pdf_input=json.loads((LANG/'reviews/a00-m81243-tagged-pdf-manifest.json').read_text(encoding='utf-8'))
        assert hashlib.sha256(draft_pdf.read_bytes()).hexdigest()==pdf_check['pdf_sha256']
        assert not pdf_check['errors']
        assert hashlib.sha256((OUT/'a00-m81243.html').read_bytes()).hexdigest()==pdf_input['source_sha256'], 'Tagged PDF source changed; review and regenerate the derivative before linking it.'
        index += '<aside class="note"><p><a href="../tagged-screen-pdf/a00-m81243.pdf">પૂર્ણ સંખ્યાઓનો પરિચય — 41 પાનાંની પ્રયોગાત્મક ટૅગવાળી PDF</a></p><p>આ તકનીકી પ્રારૂપ છે. PDF.jsની તપાસમાં કેટલાક ગુજરાતી અક્ષરો ગુમાય છે. સ્ક્રીન વાંચન માટે અર્થપૂર્ણ HTML પાઠને પ્રાથમિકતા આપો. PDF/UA પ્રમાણિત નથી; સહાયક ટેકનોલોજીની સમીક્ષા બાકી છે.</p></aside>'
    for book in ('A00','A10'):
        index += f'<section><h2>{book}</h2><ol>'
        for row in [r for r in coverage if r['program']==book]:
            text=esc(row['module_id']+' · '+row.get('target_title',row['source_title']))
            state = 'પૂર્ણ પાઠનો પ્રારૂપ; કાર્યપ્રવાહની સમીક્ષા બાકી' if row['source_translation']=='draft_complete_pending_review' else 'આંશિક અનુવાદ'
            index += f'<li><a href="{Path(row["path"]).name}">{text}</a> — {state}</li>' if row['path'] else f'<li><span lang="en">{text}</span> — અનુવાદ બાકી</li>'
        index += '</ol></section>'
    (OUT/'index.html').write_text(wrap('પુસ્તકો અને અનુવાદની પ્રગતિ',index),encoding='utf-8',newline='\n')
    (OUT/'library.css').write_text('''img,.localized-figure{display:block;max-width:100%;height:auto;margin:1rem auto}.source-media{margin:1rem 0}.figure-description{font-size:.85rem;color:#33484d}.table-scroll{overflow-x:auto;max-width:100%;margin:1rem 0}.table-scroll table{min-width:420px}.source-paragraph{margin:.8rem 0}.module-contents{list-style:disc!important}.source .definition{border-left:3px solid #08656b;padding:.6rem 1rem;margin:.8rem 0}.source li{margin:.4rem 0}.source .list{padding-left:1.2rem}.source span[effect="underline"]{text-decoration:underline}.source .example{margin:1rem 0}.source .solution{overflow-wrap:anywhere}math{overflow:visible} @media print{.table-scroll{overflow:visible}.table-scroll table{min-width:0}.localized-figure{max-height:60mm}.source-media{break-inside:avoid}}''',encoding='utf-8',newline='\n')
    receipt={'schema':'gujarati-full-assignment-coverage-v1','assignment_complete':False,'modules_expected':len(rows),
             'modules':coverage,'pending_workflow':['Complete source translation','Complete worked answers including source-omitted solutions','Figure localization review','AX-3 companion across assignment','Tagged screen PDFs','Print outputs','Offline package and accessibility QA']}
    (LANG/'COVERAGE.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f'Built {len(recipes)} draft module pages; {len(rows)} assigned modules retained in coverage.')


if __name__ == '__main__':
    main()
