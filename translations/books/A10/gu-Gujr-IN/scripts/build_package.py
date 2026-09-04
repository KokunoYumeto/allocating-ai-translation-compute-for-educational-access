"""Bounded A10 recovery build. No legacy builders, TeX, or shared writes.

Usage: python -X utf8 scripts/build_package.py /path/to/read-only/translations
Requires BeautifulSoup4 and SymPy. Network is used only to acquire SHA-pinned
OpenStax source XML; a verified existing local copy avoids any fresh request.
"""
import ast
from collections import Counter
import csv
import hashlib
from html import escape
import json
from pathlib import Path
import re
import shutil
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import sympy as S

ROOT = Path(__file__).resolve().parents[1]
EXPORT = Path(sys.argv[1]).resolve()
PREFIX = 'gu-Gujr-IN/workspace/gu-Gujr-IN/'
INPUT = EXPORT / PREFIX
MANIFEST_PIN = '772c054d8b6f9337f62a89df2fc2c726ed2d97c9077cb07f07dd0150e5ffe5a1'
COMMIT = '38cae454e644abf9f0a623e876994553881597c9'
MODULES = ['m82630'] + [f'm{x}' for x in range(82451,82463)]
NS = {'c':'http://cnx.rice.edu/cnxml', 'm':'http://www.w3.org/1998/Math/MathML'}
inventory = []

def sha(b): return hashlib.sha256(b).hexdigest()
def write(path, text):
    p = ROOT/path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8', newline='\n')
def jsonwrite(path, obj): write(path, json.dumps(obj, ensure_ascii=False, indent=2)+'\n')

manifest_bytes = (EXPORT/'EXPORT_MANIFEST.json').read_bytes()
assert sha(manifest_bytes) == MANIFEST_PIN
manifest = json.loads(manifest_bytes)
files = {x['path']:x for x in manifest['files']}
def read_verified(relative):
    key = PREFIX+relative
    item = files[key]
    b = (INPUT/relative).read_bytes()
    assert len(b)==item['bytes'] and sha(b)==item['export_sha256'],key
    return b
def copy_verified(relative, target=None):
    target = target or relative
    b = read_verified(relative)
    p = ROOT/target
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b)
    entry = {'export_path':PREFIX+relative,'path':target,'bytes':len(b),'sha256':sha(b),'mode':'exact copy'}
    if entry not in inventory: inventory.append(entry)
    return b

recipes = json.loads(read_verified('library-recipes.json'))
authority = list(csv.DictReader(read_verified('provenance/A10-canonical-manifest.csv').decode('utf-8-sig').splitlines()))
authority_by_path = {x['relative_path']:x for x in authority}
for relative in ['assets/OFL.txt','canon/README.md','canon/examples.csv','canon/targeted-examples.md','canon/reference-lock.json','terminology.csv','sources.lock.json','provenance/A10-canonical-manifest.csv','notices/A10-LICENSE.txt','notices/A10-NOTICE.txt','notices/OpenStax-LICENSE.txt']:
    copy_verified(relative)
copy_verified('notices/A10-LICENSE.txt','LICENSE.txt')
copy_verified('output/assets/style.css','assets/style.css')
copy_verified('output/assets/NotoSansGujarati.ttf','assets/NotoSansGujarati.ttf')
copy_verified('output/library/library.css','reader/library.css')
for relative in ['GOAL.md','canon/README.md','canon/examples.csv','canon/targeted-examples.md','canon/reference-lock.json','assets/style.css','library-recipes.json']:
    b=read_verified(relative)
    inventory.append({'export_path':PREFIX+relative,'bytes':len(b),'sha256':sha(b),'mode':'provenance pin; source unchanged'})

def semantic_math(root):
    return [(e.tag.rsplit('}',1)[-1],(e.text or '').strip()) for e in root.iter()
            if e.tag.startswith('{'+NS['m']+'}') and e.tag.rsplit('}',1)[-1] in {'mn','mi','mo'}]
def ids(root,tag): return [e.get('id') for e in root.findall('.//c:'+tag,NS)]
def math_signature(soup):
    return [str(x) for x in soup.find_all('math')]
def assets_for(soup):
    for e in soup.find_all(['img','image','source']):
        u=e.get('src') or e.get('href') or e.get('xlink:href')
        if not u or u.startswith('data:') or u.startswith('#'): continue
        parsed=urllib.parse.urlsplit(u)
        assert not parsed.scheme, ('remote runtime',u)
        path=urllib.parse.unquote(parsed.path)
        assert path.startswith('media/'),path
        copy_verified('output/library/'+path,'reader/'+path)

coverage=[]
sources={}
rendered={}
reconciliation=[]
for module in MODULES:
    rawpath=f'modules/{module}/index.cnxml'
    pin=authority_by_path[rawpath]
    target=ROOT/f'source/en/{module}.cnxml'
    if target.exists():
        b=target.read_bytes()
    else:
        url=f'https://raw.githubusercontent.com/openstax/osbooks-prealgebra-bundle/{COMMIT}/{rawpath}'
        request=urllib.request.Request(url, headers={'User-Agent':'A10-bounded-recovery/1.0'})
        with urllib.request.urlopen(request,timeout=45) as response: b=response.read()
    assert sha(b)==pin['sha256'] and len(b)==int(pin['bytes']), (module,'canonical pin mismatch',sha(b),pin['sha256'])
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(b)
    canonical=ET.fromstring(b)
    sources[module]=canonical
    inventory.append({'path':f'source/en/{module}.cnxml','bytes':len(b),'sha256':sha(b),'git_blob_sha1':pin['git_blob_sha1'],'source_url':f'https://raw.githubusercontent.com/openstax/osbooks-prealgebra-bundle/{COMMIT}/{rawpath}','mode':'verified canonical source'})
    translated=copy_verified(f'translations/a10-{module}.gu.cnxml',f'source/gu/a10-{module}.gu.cnxml')
    gu=ET.fromstring(translated)
    assert ids(canonical,'exercise')==ids(gu,'exercise'),(module,'exercise IDs')
    assert ids(canonical,'solution')==ids(gu,'solution'),(module,'supplied solution IDs')
    assert ids(canonical,'figure')==ids(gu,'figure'),(module,'figure IDs')
    assert semantic_math(canonical)==semantic_math(gu),(module,'source mathematical tokens')
    recipe=recipes['A10:'+module]
    for key in ['errata_file','media_review','worked_companion']:
        if recipe.get(key): copy_verified(recipe[key],'support/recovered/'+Path(recipe[key]).name)
    old=read_verified(f'output/library/a10-{module}.html')
    soup=BeautifulSoup(old.decode('utf8'),'html.parser')
    before=math_signature(soup)
    soup.select_one('.eyebrow').string='ગુજરાતી · A10 · 13 પાઠનું આંશિક પેકેજ'
    for a in soup.select('nav a'):
        if a.get('href')=='index.html': a['href']='../index.html'
        elif a.get('href')=='../index.html': a['href']='../support/fractions.html';a.string='અપૂર્ણાંક સમજ અને ઉકેલો'
    for link in soup.select('a[href="../notices.html"]'): link['href']='../attribution.html'
    if module=='m82456':
        link=soup.new_tag('a',href='../support/fractions.html');link.string='41 વધારાના ઉકેલો';soup.nav.append(link)
    assert before==math_signature(soup),(module,'reader math changed')
    assert all(soup.find(id=i) for i in ids(gu,'exercise')),(module,'reader exercise missing')
    assert all(soup.find(id=i) for i in ids(gu,'solution')),(module,'reader supplied solution missing')
    assets_for(soup)
    write(f'reader/a10-{module}.html',str(soup))
    rendered[module]=soup
    inventory.append({'path':f'reader/a10-{module}.html','export_path':PREFIX+f'output/library/a10-{module}.html','input_sha256':sha(old),'mode':'current reader; navigation/banner-only changes; exact MathML retained'})
    exercises=canonical.findall('.//c:exercise',NS)
    omitted=[e.get('id') for e in exercises if not e.findall('.//c:solution',NS)]
    added=[]
    if recipe.get('worked_companion'):
        companion=json.loads(read_verified(recipe['worked_companion']))
        added=[x['source_exercise'] for x in companion['items']]
        assert len(added)==len(set(added)) and set(added)==set(omitted),(module,'recovered answer coverage')
        htmlrel=f'output/library/a10-{module}-answers.html'
        olda=read_verified(htmlrel)
        sa=BeautifulSoup(olda.decode('utf8'),'html.parser')
        sig=math_signature(sa)
        sa.select_one('.eyebrow').string='ગુજરાતી · A10 · મૂળ જવાબોથી અલગ પૂરક'
        for a in sa.select('a[href]'):
            if a['href']=='index.html':a['href']='../index.html'
            elif a['href']=='../index.html':a['href']='../support/fractions.html';a.string='અપૂર્ણાંક સમજ અને ઉકેલો'
            elif a['href']=='../notices.html':a['href']='../attribution.html'
        assets_for(sa)
        assert sig==math_signature(sa)
        write(f'reader/a10-{module}-answers.html',str(sa))
        inventory.append({'path':f'reader/a10-{module}-answers.html','export_path':PREFIX+htmlrel,'input_sha256':sha(olda),'mode':'current recovered answer reader; navigation/banner-only changes'})
    entry={'module':module,'title_gu':recipe['title'],'source_exercises':len(exercises),'supplied_solutions':len(ids(canonical,'solution')),'source_omitted_answers':len(omitted),'recovered_added_answers':len(added),'new_added_answers':41 if module=='m82456' else 0,'figures':len(ids(canonical,'figure')),'media_occurrences':len(ids(canonical,'media')),'reader':f'reader/a10-{module}.html','draft_status':'full recovered source draft; not linguistic certification'}
    coverage.append(entry)
    reconciliation.append({'module':module,'source_exercise_ids':[e.get('id')for e in exercises],'supplied_solution_ids':ids(canonical,'solution'),'source_omitted_exercise_ids':omitted,'recovered_added_answer_exercise_ids':added,'source_figure_ids':ids(canonical,'figure'),'source_media':[{'id':m.get('id'),'sources':[e.get('src')for e in m.iter()if e.get('src')]}for m in canonical.findall('.//c:media',NS)]})

def tokens(e):
    tag=e.tag.rsplit('}',1)[-1]
    if tag=='msup': return ['(']+tokens(e[0])+[')','**','(']+tokens(e[1])+[')']
    if tag=='mfrac':return ['(','(']+tokens(e[0])+[')','/','(']+tokens(e[1])+[')',')']
    if tag in {'math','mrow'}:return [t for x in e for t in tokens(x)]
    if tag=='mspace':return []
    raw=(e.text or '').strip().replace('−','-')
    if tag=='mn' and raw.startswith('-'):return ['(','-',raw[1:],')']
    if tag in {'mn','mi','mo'}:return [{'·':'*','⋅':'*','×':'*','÷':'/'}.get(raw,raw)]
    raise ValueError((tag,raw))
def formula(e):
    out=[]
    def val(t):return t==')' or bool(re.fullmatch(r'\d+|[A-Za-z]',t))
    for t in tokens(e):
        if out and val(out[-1]) and (t=='(' or re.fullmatch(r'\d+|[A-Za-z]',t)):out.append('*')
        out.append(t)
    f=''.join(out);ast.parse(f,mode='eval');return f
def exact(f):return S.sympify(f,locals={c:S.Symbol(c)for c in 'abmnqrsxyAB'},rational=True)
def equal(a,b):return S.cancel(exact(a)-exact(b))==0
def mathml(f):
    def visit(n):
        if isinstance(n,ast.Constant):return f'<mn>{n.value}</mn>'
        if isinstance(n,ast.Name):return f'<mi>{n.id}</mi>'
        if isinstance(n,ast.UnaryOp):return '<mrow><mo>−</mo>'+visit(n.operand)+'</mrow>'
        if isinstance(n,ast.BinOp):
            a,b=visit(n.left),visit(n.right)
            if isinstance(n.op,ast.Div):return f'<mfrac>{a}{b}</mfrac>'
            if isinstance(n.op,ast.Pow):return f'<msup>{a}{b}</msup>'
            op={ast.Mult:'·',ast.Add:'+',ast.Sub:'−'}[type(n.op)]
            return f'<mrow>{a}<mo>{op}</mo>{b}</mrow>'
        raise ValueError(n)
    return '<math xmlns="http://www.w3.org/1998/Math/MathML">'+visit(ast.parse(f,mode='eval').body)+'</math>'

def svg_bars(name,rows,description):
    # Equal unit widths encode amount; every subdivision is countable.
    w=660;h=65+len(rows)*76
    result=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="{name}-title {name}-desc"><title id="{name}-title">{escape(description)}</title><desc id="{name}-desc">દરેક હરોળમાં સમાન પહોળાઈ એક આખું એકમ દર્શાવે છે. રંગીન સરખા ભાગો ગણો.</desc>'
    for row,(parts,filled,label,unit_count) in enumerate(rows):
        x,y=20,40+row*76
        result+=f'<text x="20" y="{y-9}" font-size="34">{escape(label)}</text>'
        for i in range(parts*unit_count):
            width=600/(parts*unit_count)
            result+=f'<rect data-part="{i+1}" data-filled="{str(i<filled).lower()}" x="{x+i*width}" y="{y}" width="{width}" height="30" fill="'+('#16828a' if i<filled else '#fff')+'" stroke="#223f49" stroke-width="1.2"/>'
    return result+'</svg>'
diagrams={
 'eighths':svg_bars('eighths',[(8,5,'5/8',1),(16,10,'10/16 = 5/8',1)],'એકસરખા આખામાં 5/8 અને 10/16ની સમાન રંગીન લંબાઈ.'),
 'ribbon':svg_bars('ribbon',[(8,6,'6 × 1/8 = 6/8 = 3/4',1)],'એક યાર્ડના આઠ સરખા ભાગ; છ રંગીન ભાગો. દરેક રંગીન ભાગ 1/8 યાર્ડની એક રિબન.'),
 'half':svg_bars('half',[(6,4,'2/3 = 4/6',1),(6,2,'1/2 × 2/3 = 2/6 = 1/3',1)],'એકસરખા આખાના છ ભાગમાંથી ચાર રંગીન; બીજી હરોળમાં તેમાંથી અડધા એટલે બે રંગીન ભાગ.'),
}
# Cooking diagrams use lengths proportional to cup volume and outlines for fills.
cups='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 660 265" role="img" aria-labelledby="cups-title"><title id="cups-title">8/3 કપ માપવાની બે રીત: બે 1 કપ અને બે 1/3 કપના માપ; અથવા આઠ 1/3 કપના માપ.</title>'
for row,amounts in enumerate([[S.Rational(1),S.Rational(1),S.Rational(1,3),S.Rational(1,3)],[S.Rational(1,3)]*8]):
    x=20;y=45+row*130
    cups+=f'<text x="20" y="{y-15}" font-size="32">રીત {row+1}</text>'
    for i,amount in enumerate(amounts):
        width=float(amount)*180
        cups+=f'<rect data-volume="{amount}" x="{x}" y="{y}" width="{width}" height="34" fill="#16828a" stroke="#223f49"/>'
        cups+=f'<text x="{x+width/2}" y="{y+67}" text-anchor="middle" font-size="34">{amount}</text>'
        x+=width+10
    assert sum(amounts)==S.Rational(8,3)
diagrams['cups']=cups+'</svg>'

data=json.loads((ROOT/'support/fraction-answers.json').read_text(encoding='utf8'))
ex={e.get('id'):e for e in sources['m82456'].findall('.//c:exercise',NS)}
omitted={i for i,e in ex.items() if not e.findall('.//c:solution',NS)}
assert {x['id']for x in data['items']}==omitted and len(data['items'])==41
newchecks=[]
cards=[]
for ordinal,item in enumerate(data['items'],1):
    i=item['id'];e=ex[i];problem=e.find('c:problem',NS);kind=item.get('kind','calculate')
    if kind=='calculate':
        maths=problem.findall('.//m:math',NS);assert len(maths)==1
        f=formula(maths[0]);assert equal(f,item['answer']),(i,f,item['answer'])
        newchecks.append({'id':i,'method':'exact source-MathML rational/symbolic identity','source_formula':f,'answer':item['answer'],'domain':item.get('domain')})
    elif kind=='equivalent':
        f=formula(problem.find('.//m:math',NS))
        assert len(set(item['answers']))==3 and all(equal(f,a)for a in item['answers'])
        newchecks.append({'id':i,'method':'three distinct source-bound equivalent fractions','source_formula':f,'answers':item['answers']})
    elif kind=='phrase':
        text=' '.join(problem.itertext())
        if i=='fs-id1170654293085':assert 'difference' in text and '3' in text and 'B' in text and item['answer']=='A/(3-B)'
        else:assert 'sum' in text and '4' in text and item['answer']=='(m+n)/(4*q)'
        newchecks.append({'id':i,'method':'source English phrase and grouping read; symbolic domain explicitly retained','answer':item['answer'],'domain':item['domain']})
    elif kind=='application':
        source_text=' '.join(problem.itertext())
        if i=='fs-id1170654189085':
            assert '4' in source_text and 'fudge' in source_text and 'cups' in source_text
            assert formula(problem.find('.//m:math',NS)).replace('(','').replace(')','')=='2/3'
            assert equal('4*(2/3)',item['answer']) and equal('1+1+1/3+1/3',item['answer']) and equal('8*(1/3)',item['answer'])
        else:
            maths=problem.findall('.//m:math',NS)
            assert 'ribbon' in source_text and 'yard' in source_text
            assert equal(formula(maths[0]),'3/4') and equal(formula(maths[1]),'6')
            assert equal('(3/4)/6',item['answer']) and equal('6*(1/8)','3/4')
        newchecks.append({'id':i,'method':'source-bound exact application quantity, unit and diagram counts','answer':item['answer'],'unit_gu':item['unit_gu']})
    else:
        if i=='fs-id1170652648184':assert equal('(1/2)*(2/3)','1/3') and equal('2/6','1/3')
        else:assert equal('(-a/b)*(-b/a)','1') and equal('(-2/3)*(-3/2)','1')
        newchecks.append({'id':i,'method':'authored open-response example; exact identity and domain verified','answer':item['answer']})
    original=rendered['m82456'].find(id=i).select_one('.problem')
    question=BeautifulSoup(str(original),'html.parser')
    for tag in question.find_all(attrs={'id':True}):del tag['id']
    instruction=('ત્રણ સમ અપૂર્ણાંકો શોધો.' if kind=='equivalent' else
                 'અપૂર્ણાંકને સાદું રૂપ આપો.' if 3<=ordinal<=7 else
                 'ગુણાકાર કરો.' if 8<=ordinal<=15 else
                 'ભાગાકાર કરો.' if 16<=ordinal<=22 else
                 'પદાવલીને સાદું રૂપ આપો.' if 23<=ordinal<=35 else
                 'શબ્દોમાંથી પદાવલી લખો.' if kind=='phrase' else 'મૂળ પ્રશ્ન')
    answer=' = '.join(mathml(a)for a in item['answers']) if kind=='equivalent' else (mathml(item['answer'])if item['answer']!='negative reciprocal' else 'નીચેનું સમજૂતીવાળું ઉદાહરણ જુઓ.')
    steps=''.join('<li>'+escape(s)+'</li>'for s in item['steps'])
    diagram=''
    if item.get('diagram'):
        name=item['diagram'];diagram='<figure>'+diagrams[name]+'<figcaption>અલગ રચેલું સહાયક ચિત્ર; મૂળ સ્રોતની આકૃતિનું સ્થાન લેતું નથી.</figcaption></figure>'
    domain='<p>શરત: '+escape(item['domain'])+'</p>'if item.get('domain') else ''
    cards.append(f'<section class="worked" id="answer-{i}"><h2>{ordinal}. {instruction}</h2>{question}<p><a href="../reader/a10-m82456.html#{i}">મૂળ અભ્યાસ</a> · <span class="id">{i}</span></p><details><summary>અલગ રચેલો ઉકેલ જુઓ</summary><p>જવાબ: {answer} {escape(item.get("unit_gu",""))}</p>{domain}<ol>{steps}</ol>{diagram}</details></section>')

def page(title,body,depth=0):
    p='../' if depth else ''
    return f'<!doctype html><html lang="gu-Gujr-IN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)}</title><link rel="stylesheet" href="{p}assets/style.css"><link rel="stylesheet" href="{p}assets/package.css"></head><body><a class="skip" href="#main">મુખ્ય ભાગ પર જાઓ</a><header><p class="eyebrow">ગુજરાતી · OpenStax Elementary Algebra 2e · A10</p><h1>{escape(title)}</h1></header><nav><a href="{p}index.html">પેકેજની સૂચિ</a><a href="{p}support/fractions.html">અપૂર્ણાંક સમજ અને ઉકેલો</a><a href="{p}attribution.html">શ્રેય અને શરતો</a></nav><main id="main">{body}</main><footer>CC BY-NC-SA 4.0 · OpenStax/Rice University · Gujarati adaptation: Language Allocation / OpenAI Codex. No endorsement or linguistic certification.</footer></body></html>'

intro='''<p class="note">આ પૂરકમાં m82456ના મૂળ સ્રોતે જવાબ ન આપેલા તમામ 41 અભ્યાસોના અલગ રચેલા ઉકેલો છે. મૂળ 80 આપેલા ઉકેલો મૂળ પાઠમાં જ છે. પહેલા પ્રશ્ન જાતે કરો; પછી “ઉકેલ જુઓ” ખોલો. આ 13 પાઠનું આંશિક A10 પેકેજ છે, આખું પુસ્તક નથી.</p>
<section id="learning-route"><h2>સમજ માટે ટૂંકો માર્ગ</h2><p>અપૂર્ણાંકનો અંશ પસંદ કરેલા ભાગ બતાવે છે; છેદ આખી વસ્તુના કેટલા સરખા ભાગ કર્યા છે તે બતાવે છે. સરખામણીમાં આખી વસ્તુનું માપ એકસરખું રાખો.</p>
<ol><li>સમાન ભાગ અને સમ અપૂર્ણાંક: ઉકેલ 1–2; રંગીન લંબાઈ બદલાય છે કે માત્ર ભાગોની સંખ્યા?</li><li>સામાન્ય અવયવ અને ચિહ્ન: ઉકેલ 3–15. અંશ અને છેદ બંનેને એક જ શૂન્ય સિવાયના અવયવ વડે ભાગો.</li><li>ભાગાકાર: ઉકેલ 16–25. માત્ર ભાજકનો વ્યસ્ત લો; ભાજક શૂન્ય ન હોય.</li><li>અપૂર્ણાંક રેખા: ઉકેલ 26–35. આખા અંશ અને આખા છેદની ગણતરી અલગ કરો.</li><li>શબ્દો અને એકમો: ઉકેલ 36–41. કુલ માત્રા, દરેક ભાગ અને ભાગોની સંખ્યા અલગ ઓળખો.</li></ol>
<p>આ માર્ગ કૌશલ્ય પ્રમાણે પસંદ કરવા માટે છે; કોઈ ચોક્કસ ધોરણની સમકક્ષતા જાહેર કરતો નથી. ધોરણ 2–6ની મદદ માટે પહેલો અને છેલ્લો ભાગ પસંદ કરી શકાય; ચલવાળા અને આગળના મૂળ પ્રશ્નો કાઢવામાં આવ્યા નથી.</p></section>
<section><h2>ત્રણ ઝડપી તપાસ</h2><ol><li>5/8ને 10/8 બનાવવું સમ અપૂર્ણાંક આપે છે? <details><summary>પ્રતિસાદ</summary><p>ના. માત્ર અંશ બમણો થયો છે; કિંમત બમણી થાય છે. સમ અપૂર્ણાંક 10/16 છે, કારણ કે બંને બમણા કર્યા છે.</p></details></li><li>(4/5) ÷ (3/4)માં કયા અપૂર્ણાંકનો વ્યસ્ત લેવાય? <details><summary>પ્રતિસાદ</summary><p>ભાજક 3/4નો. એટલે (4/5) × (4/3), બંનેનો વ્યસ્ત નહીં.</p></details></li><li>y = 0 હોય તો (2/5) ÷ (y/9) ગણાય? <details><summary>પ્રતિસાદ</summary><p>ના. ભાજક શૂન્ય થાય છે; તેથી y ≠ 0 જરૂરી છે.</p></details></li></ol><p>આ ત્રણ નવા સમજ-તપાસ પ્રશ્નો મૂળ 41 અભ્યાસોની ગણતરીમાં સામેલ નથી.</p></section>'''
write('support/fractions.html',page('અપૂર્ણાંક: સમજ, ચિત્રો અને 41 વધારાના ઉકેલો',intro+''.join(cards),1))
write('assets/package.css','details{margin:.7rem 0}summary{cursor:pointer;font-weight:700}svg{display:block;width:100%;height:auto;max-width:660px;background:white;font-family:Gujarati,sans-serif}svg text{fill:#182c35}ol{padding-left:1.7rem}.worked h2{font-size:1.22rem;margin-top:.2rem}.id{overflow-wrap:anywhere}th,td{overflow-wrap:anywhere}.table-scroll{overflow-x:auto}main{overflow-wrap:break-word}math{vertical-align:middle}details[open]{border-left:3px solid #16828a;padding-left:.8rem}@media(max-width:540px){.table-scroll table{font-size:15px}.table-scroll th,.table-scroll td{padding:.3rem}}@media print{details{display:block}details>*{display:block}}\n')
rows=''
for entry in coverage:
    m=entry['module']
    supplement=(f'<a href="reader/a10-{m}-answers.html">{entry["recovered_added_answers"]} વધારાના ઉકેલો</a>'if entry['recovered_added_answers'] else '<a href="support/fractions.html">41 નવા વધારાના ઉકેલો</a>'if m=='m82456' else 'અલગ પૂરક હજી નથી')
    rows+=f'<tr><td><a href="{entry["reader"]}">{entry["title_gu"]}</a><br><small>{m}</small></td><td>{entry["source_exercises"]}</td><td>{entry["supplied_solutions"]}</td><td>{supplement}</td></tr>'
totals={k:sum(x[k]for x in coverage)for k in ['source_exercises','supplied_solutions','source_omitted_answers','recovered_added_answers','new_added_answers','figures','media_occurrences']}
body=f'''<p class="note">આ OpenStax Elementary Algebra 2eના 82માંથી 13 મોડ્યુલનો પુનઃપ્રાપ્ત ગુજરાતી પ્રારૂપ છે: પ્રસ્તાવના, પ્રકરણ 1ના પાઠ અને પ્રકરણ 2નો પરિચય. <strong>આ આખું ગુજરાતી પુસ્તક નથી.</strong> મૂળ અંકો, ચલ, અભ્યાસ અને આપેલા ઉકેલોની ઓળખ જાળવેલી છે.</p>
<p><a href="support/fractions.html">નવું: અપૂર્ણાંક માટે 41 પગથિયાવાર ઉકેલો, ચાર ચિત્રો અને ત્રણ સમજ-તપાસ પ્રશ્નો</a>.</p>
<p>આ પેકેજમાં {totals['source_exercises']} મૂળ અભ્યાસ, {totals['supplied_solutions']} મૂળ આપેલા ઉકેલ અને {totals['recovered_added_answers']} પુનઃપ્રાપ્ત અલગ જવાબો છે; હવે 41 નવા અલગ જવાબ ઉમેર્યા છે. આખું ફોલ્ડર સાથે રાખીને index.html ખોલો. પાઠ, ચિત્રો, અક્ષરફોન્ટ અને ગણિત ઓફલાઇન છે; બહારના સ્રોત માટે જ ઇન્ટરનેટ જોઈએ.</p>
<div class="table-scroll"><table><thead><tr><th>પાઠ</th><th>અભ્યાસ</th><th>મૂળ ઉકેલ</th><th>અલગ સહાય</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>મર્યાદા અને આગળનું કામ</h2><p>બાકી 69 A10 મોડ્યુલ આ પેકેજમાં નથી. આગળનો સ્રોત m82463 છે (સમીકરણો: સરવાળો અને બાદબાકી). m82457–m82461ના બાકી જવાબો, આગળના પાઠોની ચિત્ર-સહાય અને લાંબા ગાળાનું સંપૂર્ણ પુસ્તક કાર્ય બાકી છે. A00ના 16 પુનઃપ્રાપ્ત પાઠ અહીં સામેલ નથી.</p><p>ધોરણ 2–6 માટેનો મદદનો માર્ગ અલગ છે; તે અદ્યતન સ્રોતને બદલે કે દૂર કરતો નથી. ભાષાકીય અને સુલભતા મર્યાદાઓ સ્પષ્ટ છે; મૂળ ગુજરાતી વક્તા, બાળક અથવા સહાયક ટેકનોલોજીની પ્રમાણિત તપાસનો દાવો નથી.</p>
<p><a href="PACKAGE.json">કવરેજ અને પિન</a> · <a href="QA.json">યાંત્રિક તપાસ</a> · <a href="ANSWER_RECONCILIATION.json">અભ્યાસ/ઉકેલ ઓળખ</a> · <a href="SOURCE_INVENTORY.json">સ્રોત અને આકૃતિ બાઇટ પિન</a></p>'''
write('index.html',page('પ્રારંભિક બીજગણિત: ગુજરાતી વાચન પેકેજ',body))
attribution='''<h2>Attribution and license</h2><p>Original: OpenStax / Rice University, <em>Elementary Algebra 2e</em>, senior contributing authors Lynn Marecek, MaryAnne Anthony-Smith and Andrea Honeycutt Mathis. Canonical collection col31130, commit <code>38cae454e644abf9f0a623e876994553881597c9</code>.</p><p>Indonesian translation input: KokunoYumeto, complete preservation release v1.0.2. Its <a href="notices/A10-NOTICE.txt">inherited notice</a> describes the Indonesian predecessor, not this partial Gujarati package.</p><p>Recovered Gujarati translation/adaptation: Language Allocation / OpenAI Codex, 2026. New fraction answer companion and four diagrams: Language Allocation / OpenAI Codex, 2026-09-04. New answers are not source-supplied answers. New diagrams do not replace original source figures.</p><p>Content/adaptation: <a href="LICENSE.txt">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International</a>, subject to inherited component credits and restrictions. OpenStax and Rice University do not endorse this translation; no trademark rights or warranty are implied. The <a href="assets/OFL.txt">Noto Sans Gujarati font uses SIL OFL 1.1</a>.</p><p>The original notices and source pins are retained. Gujarati canon observations inform language; reference PDFs are not redistributed. This is a reading/translation artifact, not a training or fine-tuning dataset.</p><p>Optional online primary source: <a href="https://github.com/openstax/osbooks-prealgebra-bundle/tree/38cae454e644abf9f0a623e876994553881597c9/modules/m82456">pinned OpenStax m82456 source</a>. All necessary lesson dependencies are local.</p>'''
write('attribution.html',page('સ્રોત, શ્રેય અને ઉપયોગની શરતો',attribution))
for r in reconciliation:
    r['new_added_answer_exercise_ids']=[i['id']for i in data['items']]if r['module']=='m82456'else[]
    answered=set(r['recovered_added_answer_exercise_ids']+r['new_added_answer_exercise_ids'])
    r['remaining_omitted_exercise_ids']=[i for i in r['source_omitted_exercise_ids']if i not in answered]
jsonwrite('ANSWER_RECONCILIATION.json',reconciliation)
jsonwrite('SOURCE_INVENTORY.json',inventory)
jsonwrite('PACKAGE.json',{'schema':'recovered-a10-reader-package-v1','locale':'gu-Gujr-IN','date':'2026-09-04','book':'OpenStax Elementary Algebra 2e','scope':'13 of 82 A10 modules; partial recovered source drafts, not a complete Gujarati book','module_ids':MODULES,'coverage':coverage,'totals':totals,'new_support':{'module':'m82456','source_omitted_answers_completed':41,'new_diagrams':4,'new_diagnostic_questions':3,'original_source_xml_unchanged':True},'pins':{'export_manifest_sha256':MANIFEST_PIN,'canonical_commit':COMMIT,'canon_and_style':'unchanged; exact hashes in SOURCE_INVENTORY.json'},'excluded':'All A00 readers/full content; stale offline ZIP; private operational records; all A10 units outside the selected 13','remaining_scope':'69 A10 modules; further answer/figure/learning-route support; no native-review or accessibility certification claimed','next_source_anchor':f'https://github.com/openstax/osbooks-prealgebra-bundle/blob/{COMMIT}/modules/m82463/index.cnxml','next_support_anchor':'m82457: source-omitted fraction addition/subtraction answers','entrypoint':'index.html','offline':True,'license':'CC BY-NC-SA 4.0 with inherited component notices; font OFL 1.1'})

# Every local HTML resource and fragment is resolved; remote hyperlinks are
# allowed, remote runtime resources are not. No A00 content is admitted.
jsonwrite('QA.json',{'schema':'recovered-a10-qa-v1','deterministic_status':'running'})
link_errors=[];remote_runtime=[];duplicate_ids=[]
htmls={p:BeautifulSoup(p.read_text(encoding='utf8'),'html.parser')for p in ROOT.rglob('*.html')}
for p,soup in htmls.items():
    counts=Counter(e['id']for e in soup.find_all(attrs={'id':True}))
    duplicate_ids.extend({'path':str(p.relative_to(ROOT)),'id':i}for i,n in counts.items()if n>1)
    for e in soup.find_all(True):
        for attr in ['href','src','xlink:href']:
            u=e.get(attr)
            if not u or u.startswith('data:'):continue
            parsed=urllib.parse.urlsplit(u)
            if parsed.scheme:
                if e.name not in {'a'}:remote_runtime.append(u)
                continue
            dest=(p.parent/urllib.parse.unquote(parsed.path)).resolve()if parsed.path else p
            if not dest.is_relative_to(ROOT) or not dest.exists():link_errors.append([str(p.relative_to(ROOT)),u,'missing target']);continue
            if parsed.fragment and dest.suffix=='.html' and not htmls[dest].find(id=urllib.parse.unquote(parsed.fragment)):
                link_errors.append([str(p.relative_to(ROOT)),u,'missing fragment'])
    assert not soup.find('script'),p
assert not link_errors,link_errors[:12]
assert not remote_runtime,remote_runtime
assert not duplicate_ids,duplicate_ids[:12]
assert not any('a00-'in p.name.lower()for p in ROOT.rglob('*')if p.is_file())
qa={'schema':'recovered-a10-qa-v1','deterministic_status':'pass','module_source_pin_checks':13,'source_exercise_solution_figure_id_checks':'pass for all 13 modules','source_numeric_variable_operator_token_checks':'pass for all 13 modules','current_reader_mathml_preservation':'exact HTML MathML serialization retained before/after navigation-only rewrite','existing_supplement_reconciliation':'all four companions exactly equal respective source-omitted ID sets; numerical content inherited, not freshly re-proved in full','new_fraction_checks':newchecks,'new_fraction_answer_count':41,'new_answer_source_omission_set_equality':True,'diagram_checks':{'count':4,'equal_part_counts':'5/8 = 10/16; 6/8 = 3/4; 4/6 halved gives 2/6; two measured routes sum to 8/3 cups','source_figures_unchanged':True},'html_count':len(htmls),'local_link_errors':link_errors,'remote_runtime_dependencies':remote_runtime,'duplicate_html_ids':duplicate_ids,'utf8':'all authored and imported text decoded strictly; no U+FFFD permitted','visual_qa':'pending bounded browser inspection; not an accessibility certification','remaining_limits':['Recovered source-language translations are not re-certified by this build.','Existing source errata remain explicit and source XML stays unchanged.','Native speaker, child and assistive-technology evidence is not claimed.']}
for p in ROOT.rglob('*'):
    if p.is_file()and p.suffix in {'.html','.json','.md','.css','.cnxml','.csv','.txt','.py'}:
        assert '\ufffd'not in p.read_text(encoding='utf-8-sig'),p
jsonwrite('QA.json',qa)
print(json.dumps({'modules':len(coverage),'totals':totals,'files':sum(p.is_file()for p in ROOT.rglob('*')),'qa':'pass; visual pending'},ensure_ascii=False))
