"""Build the Gujarati offline reader with Python's standard library only."""
import html
import json
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET

LANG = Path(__file__).resolve().parents[1]
OUT = LANG / "output"
UNIT = json.loads((LANG / "translations/unit01.gu.json").read_text(encoding="utf-8"))
esc = html.escape
C = "http://cnx.rice.edu/cnxml"
M = "http://www.w3.org/1998/Math/MathML"


def p(text): return f"<p>{esc(text)}</p>"
def paragraphs(texts): return "".join(map(p, texts))
def steps(texts): return "<ol>" + "".join(f"<li>{esc(t)}</li>" for t in texts) + "</ol>"


def page(title, content, extra=""):
    return f'''<!doctype html>
<html lang="gu-Gujr-IN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | GU-NUM-01</title><link rel="stylesheet" href="assets/style.css"></head>
<body><a class="skip" href="#main">મુખ્ય પાઠ પર જાઓ</a>
<header><p class="eyebrow">GU-NUM-01 · ગુજરાતી · gu-Gujr-IN</p><h1>{esc(title)}</h1>
<p>{esc(UNIT['subtitle'])}</p><p class="muted">પ્રારંભિક આવૃત્તિ · ગુજરાતી શિક્ષકની સમીક્ષા બાકી છે</p></header>
<nav aria-label="પાઠનાં પાનાં"><a href="index.html">વિદ્યાર્થી પાનું</a><a href="solutions.html">ઉકેલ અને પ્રતિસાદ</a><a href="source.html">મૂળને અનુસરતો અનુવાદ</a><a href="library/index.html">સંપૂર્ણ સોંપણીની પ્રગતિ</a><a href="notices.html">સ્રોત અને શ્રેય</a></nav>
<main id="main" {extra}>{content}</main>
<footer><p>OpenStax, Rice University; મૂળ લેખકો Lynn Marecek, MaryAnne Anthony-Smith અને Andrea Honeycutt Mathis.
Indonesian adaptation: KokunoYumeto repositories, produced with OpenAI Codex gpt-5.6-sol, Ultra. Gujarati translation/adaptation: Language Allocation, OpenAI Codex, 2026-08-30.</p>
<p>CC BY-NC-SA 4.0; તૃતીય પક્ષના ઘટકોની અલગ શરતો યથાવત્ છે. આ અનધિકૃત અનુવાદને OpenStax અથવા Rice University નું સમર્થન નથી. નામો, ચિહ્નો અને લોગોના હકો મળતા નથી. સામગ્રી જેવી છે તેવી આપવામાં આવે છે; કોઈ બાંયધરી નથી. <a href="notices.html">પૂર્ણ શ્રેય અને શરતો</a>.</p></footer></body></html>'''


def item_question(item):
    result = f'<article class="item" id="{item["id"]}"><h3><span class="id">{item["id"]}</span> {esc(item["prompt"])}</h3>'
    if "options" in item:
        result += '<ol class="options">' + ''.join(f'<li>{esc(o)}</li>' for o in item['options']) + '</ol>'
    result += '<p class="muted">તમારો જવાબ અને વિચાર કાગળ પર લખો અથવા બોલીને સમજાવો.</p><div class="answer-space" aria-hidden="true"></div></article>'
    return result


def math_html(element):
    name = element.tag.split('}')[-1]
    attrs = ''.join(f' {esc(k)}="{esc(v)}"' for k, v in element.attrib.items())
    if name == 'math': attrs += f' xmlns="{M}"'
    return f'<{name}{attrs}>' + esc(element.text or '') + ''.join(math_html(c)+esc(c.tail or '') for c in element) + f'</{name}>'


def cnxml(element, level=2):
    name = element.tag.split('}')[-1]
    if element.tag.startswith('{'+M+'}'): return math_html(element)
    attrs = f' id="{esc(element.attrib["id"])}"' if 'id' in element.attrib else ''
    inner = esc(element.text or '') + ''.join(cnxml(c, level + (name == 'section' and c.tag != f'{{{C}}}title')) + esc(c.tail or '') for c in element)
    if name == 'title': return f'<h{min(level,4)}{attrs}>{inner}</h{min(level,4)}>'
    if name == 'link': return f'<a href="#{esc(element.attrib["target-id"])}">આકૃતિ 1</a>'
    if name == 'media':
        return f'<div{attrs}>' + inner + f'<p class="muted">{esc(element.get("alt", ""))}</p></div>'
    if name == 'image': return number_line()
    if name == 'label': return ''
    tags = {'section':'section','para':'p','term':'strong','figure':'figure','caption':'figcaption','list':'ul','item':'li','span':'span'}
    tag = tags.get(name, 'div')
    return f'<{tag}{attrs} class="{esc(name)}">{inner}</{tag}>'


def number_line():
    ticks=''.join(f'<path d="M {70+i*85} 75 v 16"/><text x="{70+i*85}" y="117">{i}</text>' for i in range(7))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" class="number-line gu-number-line" width="680" height="160" viewBox="0 0 680 160" role="img" aria-labelledby="line-title line-description"><title id="line-title">સંખ્યારેખા</title><desc id="line-description">0 થી 6 સમાન અંતરે. ડાબે નાની અને જમણે મોટી સંખ્યાઓ.</desc><style>.gu-number-line text{{font-family:Gujarati,'Noto Sans Gujarati','Nirmala UI',sans-serif;font-size:21px;text-anchor:middle;fill:#182c35;stroke:none}}.gu-number-line path{{stroke:#182c35;stroke-width:2;fill:none}}</style><path d="M 35 83 H 630 l -12 -8 m 12 8 l -12 8"/>{ticks}<path d="M 410 27 H 585 l -10 -6 m 10 6 l -10 6 M 250 27 H 75 l 10 -6 m -10 6 l 10 6"/><text x="160" y="58">નાની</text><text x="500" y="58">મોટી</text></svg>'''


def build():
    OUT.mkdir(exist_ok=True)
    (LANG / 'assets/number-line.svg').write_text(number_line(), encoding='utf-8')
    shutil.copytree(LANG / 'assets', OUT / 'assets', dirs_exist_ok=True)
    shutil.copytree(LANG / 'notices', OUT / 'notices', dirs_exist_ok=True)
    student = '<section aria-labelledby="start"><h2 id="start">શરૂ કરતાં પહેલાં</h2>' + paragraphs(UNIT['intro']) + '</section>'
    student += '<section><h2>પહેલી તપાસ</h2>' + ''.join(item_question(i) for i in UNIT['items'] if i['phase']=='placement') + '</section>'
    student += '<section class="note"><h2>ક્યાંથી શરૂ કરવું?</h2>' + paragraphs(UNIT['routing']) + '<p>સાચા જવાબો અને દરેક વિકલ્પ માટેનો પ્રતિસાદ <a href="solutions.html">ઉકેલના પાનામાં</a> છે.</p></section>'
    for route in UNIT['routes']:
        w=route['worked']
        student += f'<section class="route" id="{route["id"]}"><h2>{route["id"]} · {esc(route["title"])}</h2>' + p(route['trigger']) + paragraphs(route['paragraphs'])
        student += '<div class="worked"><h3>સાથે ઉકેલીએ</h3>' + p(w['prompt']) + steps(w['steps']) + f'<p class="math">{esc(w["math"])}</p></div>'
        student += '<p>હવે અભ્યાસ: ' + ', '.join(f'<a href="#{x}">{x}</a>' for x in route['practice']) + '</p></section>'
    student += '<table><caption>305 માટે સ્થાનકિંમત</caption><thead><tr><th scope="col">સ્થાન</th><th scope="col">સો</th><th scope="col">દશક</th><th scope="col">એકમ</th></tr></thead><tbody><tr><th scope="row">અંક</th><td>3</td><td>0</td><td>5</td></tr><tr><th scope="row">કિંમત</th><td>300</td><td>0</td><td>5</td></tr></tbody></table>'
    for phase,title in [('practice','અભ્યાસ'),('exit','છેલ્લી તપાસ')]:
        student += '<section><h2>'+title+'</h2>' + ''.join(item_question(i) for i in UNIT['items'] if i['phase']==phase) + '</section>'
    student += '<p>વધુ પડકાર માટે <a href="source.html#fs-id1170655190140">A10 નું સ્થાનકિંમતનું ઉદાહરણ</a> જુઓ. ભિન્ન અને દશાંશ સંખ્યાઓ હજી શીખ્યા ન હોય તો મૂળ અનુવાદનાં તે ઉદાહરણો પછી કરો.</p>'
    (OUT/'index.html').write_text(page(UNIT['title'],student),encoding='utf-8')
    answers='<p class="note">પહેલાં બાળકને પોતે વિચારવા દો. આ પાનું મોટા માણસ અથવા સ્વતપાસ માટે છે. જવાબ સાથે કારણ પણ સાંભળો.</p>'
    for item in UNIT['items']:
        answers += f'<article class="item" id="answer-{item["id"]}"><h2>{item["id"]} · સંપૂર્ણ ઉકેલ</h2>'+p(item['prompt'])+'<p><strong>જવાબ: '+esc(item['answer'])+'</strong></p>'+steps(item['steps'])
        if 'feedback' in item:
            answers += '<h3>વિકલ્પ મુજબ પ્રતિસાદ</h3>' + ''.join(f'<p class="feedback"><strong>{esc(o)}</strong>: {esc(f)}</p>' for o,f in item['feedback'].items())
        answers += f'<p>વધુ મદદ: <a href="index.html#{item["route"]}">{item["route"]}</a>. <a href="index.html#{item["id"]}">પ્રશ્ન પર પાછા જાઓ</a>.</p></article>'
    answers += '<h2>મૂળ ઉદાહરણો માટે અલગ સરળ સમજ</h2>'
    for w in UNIT['source_worked_companion']:
        answers += f'<article class="item" id="{w["id"]}"><h3>{esc(w["title"])}</h3><p><a href="source.html#{w["source_exercise"]}">મૂળ પ્રશ્ન</a></p>'+steps(w['steps'])+p(w['answer'])+'</article>'
    (OUT/'solutions.html').write_text(page('ઉકેલ અને ભૂલ સમજવા માટેનો પ્રતિસાદ',answers),encoding='utf-8')
    source='<div class="note"><h2>આ અનુવાદનો વિસ્તાર</h2><p>A00 m81243 નો પ્રથમ સંપૂર્ણ ઉપવિભાગ fs-id1830385. મૂળ ક્રમ, સંખ્યાઓ અને ઓળખચિહ્નો જાળવ્યાં છે. સંખ્યારેખા ગુજરાતી લેબલ સાથે ફરી દોરી છે. આ આખા પ્રકરણનો અનુવાદ નથી.</p><p>આગળ A10 m82452 નો એક પસંદ કરેલો અભ્યાસ છે. સરળ સમજ અને નવા નિદાન પ્રશ્નો અલગ <a href="solutions.html">સહાયક પાનામાં</a> છે.</p></div>'
    for file in ['a00-m81243-part01.gu.cnxml','a10-m82452-excerpt.gu.cnxml']:
        root=ET.parse(LANG/'translations'/file).getroot()
        source+=cnxml(root.find(f'{{{C}}}content'))
    (OUT/'source.html').write_text(page('મૂળને અનુસરતો ગુજરાતી અનુવાદ',source,'class="source"'),encoding='utf-8')
    notices='''<h2>સ્રોત, ફેરફારો અને શરતો</h2><p>OpenStax Prealgebra 2e અને Elementary Algebra 2e; canonical source commit <code>38cae454e644abf9f0a623e876994553881597c9</code>.</p>
<p><a href="https://github.com/openstax/osbooks-prealgebra-bundle/tree/38cae454e644abf9f0a623e876994553881597c9">OpenStax source</a>; <a href="https://github.com/KokunoYumeto/openstax-prealgebra-2e-id-ID">Indonesian A00 v0.2.7</a>; <a href="https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id/releases/tag/v1.0.2">Indonesian A10 v1.0.2</a>.</p>
<p>Gujarati changes: translated module drafts and figure labels, localized mathematical diagrams, a separate diagnostic/remediation companion and added worked explanations. Original numerical examples and identifiers retained. Source errors and localized alternatives are recorded explicitly. The source library retains credited source photographs and front-matter illustrations where applicable. Prior Indonesian adaptations and model provenance are retained in the notices below.</p>
<p>Content and Gujarati adaptations: <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a>, subject to component-specific credits/restrictions. No endorsement by OpenStax or Rice University. Names, logos and trademarks are not licensed. Content is provided as-is, without warranty. Gujarati educational and language review is pending.</p>
<ul><li><a href="notices/OpenStax-LICENSE.txt">Unmodified OpenStax license</a></li><li><a href="notices/OpenStax-README.md">Original upstream notice</a></li><li><a href="notices/A00-README.md">Indonesian A00 attribution and provenance</a></li><li><a href="notices/A10-NOTICE.txt">Indonesian A10 attribution and provenance</a></li><li><a href="notices/A00-LICENSE.txt">A00 license</a></li><li><a href="notices/A10-LICENSE.txt">A10 license</a></li><li><a href="assets/OFL.txt">Noto Sans Gujarati font license</a></li></ul>
<h2>ઑફલાઇન ઉપયોગ</h2><p>આ ફોલ્ડર સાથે રાખો અને index.html ખોલો. ઇન્ટરનેટ કે ખાતાની જરૂર નથી. કોઈ માહિતી મોકલાતી કે સાચવાતી નથી. છાપવા માટે બ્રાઉઝરની Print સુવિધા વાપરો. સ્રોતની બાહ્ય કડીઓ ખોલવા જ ઇન્ટરનેટ જોઈએ.</p>
<h2>સુલભતા અંગે મર્યાદા</h2><p>HTML માં ગુજરાતી ભાષાની ઓળખ, શીર્ષકો, કોષ્ટકનાં મથાળાં, MathML અને ચિત્રનું લખાણરૂપ વર્ણન છે. PDF છાપવા માટે છે. માનવી દ્વારા સ્ક્રીન-રીડર પરીક્ષણ અને PDF/UA પ્રમાણન થયું નથી.</p>'''
    (OUT/'notices.html').write_text(page('સ્રોત અને શ્રેય',notices),encoding='utf-8')
    print('Built index.html, solutions.html, source.html and notices.html with local font, figure and licenses.')


if __name__ == '__main__': build()
