"""Deterministic, packet-local reader build. No network, TeX or predecessor writes."""
from pathlib import Path
from lxml import etree as E
from html import escape as h
import copy, hashlib, json, re
from content import ALT, ARIA, SOLVES, CHECKS, OPEN, ADAPT

ROOT=Path(__file__).resolve().parents[1]
C='{http://cnx.rice.edu/cnxml}'; M='{http://www.w3.org/1998/Math/MathML}'
def write(p,s):
 p=ROOT/p; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s,encoding='utf-8',newline='\n')
def js(p,o): write(p,json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def sha(p): return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def local(e): return E.QName(e).localname
def math(s):
 # Keep the authored order, signs and grouping, while making fractions semantic.
 tokens=re.findall(r'\d+(?:\.\d+)?/\d+|\d+(?:\.\d+)?|[A-Za-z]|\?=|[^\s]',s)
 out=''
 for t in tokens:
  if re.fullmatch(r'\d+(?:\.\d+)?/\d+',t):
   a,b=t.split('/'); out+=f'<mfrac><mn>{a}</mn><mn>{b}</mn></mfrac>'
  elif re.fullmatch(r'\d+(?:\.\d+)?',t): out+=f'<mn>{t}</mn>'
  elif t.isalpha(): out+=f'<mi>{t}</mi>'
  elif t=='?=': out+='<mover><mo>=</mo><mo>?</mo></mover>'
  else: out+=f'<mo>{h(t.replace("-","−"))}</mo>'
 return '<span class="math-scroll"><math xmlns="http://www.w3.org/1998/Math/MathML"><mrow>'+out+'</mrow></math></span>'
def native(e):
 tag=local(e); attrs=''.join(f' {h(k)}="{h(v)}"' for k,v in e.attrib.items() if not k.startswith('{'))
 if tag=='math': attrs+=' xmlns="http://www.w3.org/1998/Math/MathML"'
 return f'<{tag}{attrs}>'+h(e.text or '')+''.join(native(c)+h(c.tail or '') for c in e)+f'</{tag}>'

source=E.parse(str(ROOT/'source/en.cnxml'))
draft=E.parse(str(ROOT/'source/recovered.gu.cnxml'))
target=copy.deepcopy(draft)
changes=[]
def change(e,slot,new,reason):
 old=e.get(slot[1:]) if slot.startswith('@') else getattr(e,slot)
 if old==new: return
 anchor=next((a.get('id') for a in [e,*e.iterancestors()] if a.get('id')),None)
 changes.append({'anchor':anchor,'element_index':list(target.iter()).index(e),'slot':slot,'old':old,'new':new,'reason':reason})
 if slot.startswith('@'): e.set(slot[1:],new)
 else: setattr(e,slot,new)
for key,value in ALT.items(): change(next(e for e in target.iter() if e.get('id')==key),'@alt',value,'Source-image inspection and source-equation reconciliation; exact original media retained.')
for key,value in ARIA.items(): change(next(e for e in target.iter() if e.get('id')==key),'@aria-label',value,'Repair inherited mathematical/table description against source equation and actual image.')
for se,ge in zip(source.iter(),target.iter()):
 if (se.text or '').startswith('The solution to '):
  maths=list(ge.iter(M+'math'))
  if len(maths)==2 and (maths[-1].tail or '').strip()=='છે.':
   change(maths[0],'tail','નો ઉકેલ છે ','Gujarati sentence order; retained source MathML terminal period.')
   change(maths[1],'tail','','Gujarati sentence order; retained source MathML terminal period.')
 if (ge.text or '').startswith('કારની સૂચિત કિંમત દર્શાવવા'):
  change(ge,'text','ધારો કે ','Repair variable definition around retained s = MathML.')
  change(ge[0],'tail',' કારની સૂચિત કિંમત.','Repair variable definition around retained s = MathML.')
 # Keep the source emphasis boundaries and all child nodes; improve imperative order.
 if local(ge)=='emphasis' and re.match(r'પગલું [1-7]\. ',ge.text or ''):
  n=int(ge.text[6]); replacements={1:('પગલું 1.',' પ્રશ્ન વાંચો.'),2:('પગલું 2.',' શું શોધવાનું છે તે ઓળખો.'),3:('પગલું 3.',' શોધવાની રાશિને નામ આપો.'),4:('પગલું 4.',' સમીકરણ બનાવો. પ્રશ્નને એક વાક્યમાં ફરી કહો.'),5:('પગલું 5.',' સમીકરણ ઉકેલો.'),6:('પગલું 6.',' જવાબ ચકાસો.'),7:('પગલું 7.',' પ્રશ્નનો સંપૂર્ણ વાક્યમાં જવાબ આપો.')}
  if ':' in ge.text and ge.getparent().getparent().tag==C+'row':
   a,b=replacements[n]; change(ge,'text',a,'Natural Gujarati imperative order.'); change(ge,'tail',b,'Natural Gujarati imperative order; following source newline retained.')
target.write(str(ROOT/'source/m82463.gu.cnxml'),encoding='utf-8',xml_declaration=True,pretty_print=False)
js('REVISION.json',{'module':'m82463','source_sha256':sha('source/en.cnxml'),'recovered_sha256':sha('source/recovered.gu.cnxml'),'revised_sha256':sha('source/m82463.gu.cnxml'),'changes':changes,'source_media_erratum':{'id':'eip-id1169750892315','file':'CNX_ElemAlg_Figure_02_01_011a_img_new.jpg','issue':'Extra z after -8 in substitution row. Source equation and all subsequent rows require -8. Original retained unchanged; corrected semantic presentation is clearly marked.'}})
exercises=list(target.iter(C+'exercise')); src_ex=list(source.iter(C+'exercise'))
ordinals={e.get('id'):i+1 for i,e in enumerate(exercises)}
answers=[]
for n,eq,value,steps,explanation in SOLVES+[OPEN]:
 answers.append({'source_order':n,'source_exercise':exercises[n-1].get('id'),'kind':'open_first_step' if n==116 else 'solve','source_equation':eq,'answer':value,'steps':steps,'explanation_gu':explanation,'provenance':'new authored support; not an OpenStax supplied solution'})
for n,eq,var,value,result,lhs,rhs,explanation in CHECKS:
 answers.append({'source_order':n,'source_exercise':exercises[n-1].get('id'),'kind':'check','source_equation':eq,'variable':var,'candidate':value,'answer':result,'lhs':lhs,'rhs':rhs,'explanation_gu':explanation,'provenance':'new authored support; not an OpenStax supplied solution'})
answers.sort(key=lambda a:a['source_order']); js('support/NEW_ANSWERS.json',answers)

media=json.loads((ROOT/'provenance/MEDIA_SOURCE.json').read_text(encoding='utf-8-sig'))
byname={a['name']:a for a in media}
def suffix(name): return re.search(r'_02_01_(\w+)_img',name).group(1)
def adapted(name,alt,identifier=True):
 a=ADAPT[suffix(name)]; rec=byname[name]; ident=f' id="{h(rec["id"])}"' if identifier else ''
 out=f'<div{ident} class="adapted" data-source-media="{name}"><div class="badge">ગુજરાતી રજૂઆત · મૂળ આકૃતિ {suffix(name)}</div>'
 if a.get('kind')=='instruction': out+='<p>xની જગ્યાએ <span class="accent">'+math('3/2')+'</span> મૂકો.</p>'
 elif a.get('kind')=='selfcheck':
  out+='<div class="table-scroll"><table class="selfcheck"><thead><tr>'+''.join('<th scope="col">'+h(c)+'</th>' for c in a['headers'])+'</tr></thead><tbody>'
  for skill in a['skills']: out+='<tr><th scope="row">'+h(skill)+'</th>'+''.join('<td class="blank" aria-label="ખાલી પ્રતિભાવ કોષ"></td>' for _ in range(3))+'</tr>'
  out+='</tbody></table></div>'
 elif a.get('kind')=='phrase':
  out+='<div class="table-scroll"><table class="phrase"><tbody><tr>'+''.join('<td>'+h(c)+'</td>' for c in a['cells'])+'</tr><tr>'+''.join('<td>'+math(c)+'</td>' for c in a['math'])+'</tr></tbody></table></div>'
 else:
  out+='<div class="table-scroll"><table class="steps"><tbody><tr>'
  for i,c in enumerate(a['cells']):
   tag='th' if i==0 else 'td'; out+=f'<{tag}'+(' scope="row"' if i==0 else '')+'>'+h(c)
   if i==2:
    out+=''.join('<div class="mathline">'+math(m)+'</div>' for m in a['math'])
    if a.get('accent'): out+='<p class="accent">બંને બાજુની સમાન ક્રિયા: '+math(a['accent'])+'</p>'
    if a.get('after'): out+='<p>'+h(a['after'])+'</p>'
   out+=f'</{tag}>'
  out+='</tr></tbody></table></div>'
 out+=f'<details class="original"><summary>મૂળ ચિત્ર અને વર્ણન</summary><p>{h(alt)}</p><img src="media/{name}" alt="{h(alt)}"><p><a href="media/{name}">મૂળ ફાઇલ · {h(name)}</a></p></details></div>'
 return out
def attrs(e,cls=''):
 a=f' id="{h(e.get("id"))}"' if e.get('id') else ''
 if cls: a+=f' class="{h(cls)}"'
 return a
def contents(e): return h(e.text or '')+''.join(render(c)+h(c.tail or '') for c in e)
def render(e):
 tag=local(e)
 if e.tag.startswith(M): return '<span class="math-scroll">'+native(e)+'</span>' if tag=='math' else native(e)
 if tag=='media':
  im=e.find(C+'image'); name=Path(im.get('src')).name; alt=e.get('alt','')
  if suffix(name) in ADAPT: return adapted(name,alt)
  result=f'<span{attrs(e,"source-media")}><img src="media/{name}" alt="{h(alt)}" loading="lazy"></span>'
  if suffix(name)=='011a': result+=f'<aside class="correction"><strong>મૂળ ચિત્રની છાપભૂલ:</strong> બીજી લીટીમાં −8 પછીનો z વધારાનો છે. યોગ્ય ચકાસણી: {math("5(12-4)-4(12)=-8")}; {math("40-48=-8")}. મૂળ ચિત્ર ઉપર યથાવત્ રાખ્યું છે.</aside>'
  return result
 if tag=='image': return ''
 if tag=='table':
  desc=e.get('aria-label') or e.get('summary') or ''
  return '<div class="table-scroll"><table'+attrs(e)+'>'+contents(e)+'</table></div>'+(f'<details class="description"><summary>કોષ્ટકનું વર્ણન</summary><p>{h(desc)}</p></details>' if desc else '')
 if tag=='tgroup': return contents(e)
 if tag=='colspec': return ''
 if tag=='entry':
  a=attrs(e)
  if e.get('namest'): a+=f' colspan="{int(e.get("nameend")[1:])-int(e.get("namest")[1:])+1}"'
  if e.get('morerows'): a+=f' rowspan="{int(e.get("morerows"))+1}"'
  return '<td'+a+'>'+contents(e)+'</td>'
 if tag=='row': return '<tr'+attrs(e)+'>'+contents(e)+'</tr>'
 if tag=='exercise':
  n=ordinals[e.get('id')]; c=contents(e)
  if e.find(C+'solution') is None: c+=f'<p class="support-link"><a href="answers.html#answer-{e.get("id")}">નવો સમજાવેલો જવાબ જુઓ</a> · મૂળ સ્ત્રોતમાં જવાબ આપેલો નથી.</p>'
  return '<article'+attrs(e,'exercise')+f'><header class="exercise-label">પ્રશ્ન · સ્ત્રોતક્રમ {n} <small>{e.get("id")}</small></header>'+c+'</article>'
 if tag=='solution': return '<details'+attrs(e,'source-solution')+'><summary>મૂળ સ્ત્રોતમાં આપેલો જવાબ</summary>'+contents(e)+'</details>'
 if tag=='list':
  t='ol' if e.get('list-type')=='enumerated' else 'ul'
  return f'<{t}'+attrs(e)+'>'+contents(e)+f'</{t}>'
 if tag=='link':
  tid=e.get('target-id',''); doc=e.get('document',''); label=contents(e) or (doc+' · '+tid if doc else 'સંદર્ભ '+tid)
  if doc: return f'<span class="external-ref" data-document="{doc}" data-target-id="{tid}">{label} (આ અગાઉના એકમનો સંદર્ભ છે; આ પેકેટમાં નથી.)</span>'
  url=e.get('url') or '#'+tid
  return f'<a{attrs(e)} href="{h(url)}">{label}</a>'
 if tag=='title':
  depth=len(list(e.iterancestors(C+'section'))); t='h'+str(min(5,2+depth))
  return f'<{t}'+attrs(e)+'>'+contents(e)+f'</{t}>'
 if tag=='newline': return '<br'+attrs(e)+'>'
 mapping={'content':'div','section':'section','para':'div','problem':'div','example':'section','note':'aside','figure':'figure','caption':'figcaption','item':'li','emphasis':'strong','term':'dfn','definition':'section','meaning':'div','glossary':'section','equation':'div','span':'span','label':'span','thead':'thead','tbody':'tbody'}
 t=mapping.get(tag,'div'); cls={'para':'para','note':'note','example':'example','equation':'equation','section':'source-section'}.get(tag,tag)
 return f'<{t}'+attrs(e,cls)+'>'+contents(e)+f'</{t}>'

TITLE='સમાનતાના બાદબાકી અને સરવાળાના ગુણધર્મોથી સમીકરણો ઉકેલો'
def page(title,body):
 return '<!doctype html>\n<html lang="gu-IN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+h(title)+' · A10 m82463</title><link rel="stylesheet" href="assets/reader.css"></head><body><a class="skip" href="#main">મુખ્ય લખાણ પર જાઓ</a><header class="masthead"><div class="eyebrow">ELEMENTARY ALGEBRA 2e · ગુજરાતી · A10 / m82463</div><nav aria-label="મુખ્ય માર્ગદર્શન"><a href="index.html">પાઠ</a><a href="answers.html">38 નવા જવાબ</a><a href="support.html">મદદ અને ફરી ચકાસણી</a><a href="figures.html">આકૃતિઓ</a><a href="about.html">સ્ત્રોત અને વ્યાપ</a></nav></header><main id="main"><h1>'+h(title)+'</h1>'+body+'</main><footer>OpenStax આધારિત ગુજરાતી રૂપાંતર · એક સંપૂર્ણ એકમ, આખું પુસ્તક નહીં. <a href="about.html">શ્રેય અને મર્યાદા</a></footer></body></html>\n'
sections=list(target.getroot().find(C+'content').findall(C+'section'))
nav='<nav class="contents" aria-label="આ પાઠના વિભાગો"><h2>આ પાઠમાં</h2><ol>'+''.join(f'<li><a href="#{e.get("id")}">{h("".join(e.find(C+"title").itertext()))}</a></li>' for e in sections if e.find(C+'title') is not None)+'</ol></nav>'
body='<p class="lead">પહેલાં સમાનતા સમજો, પછી બંને બાજુ એકસરખી ક્રિયા કરો, અને અંતે મૂળ સમીકરણમાં જવાબ મૂકી ચકાસો.</p><div class="scope">આ પેકેટમાં m82463નો સંપૂર્ણ અનુવાદ છે: 116 પ્રશ્નો, મૂળના 78 જવાબ અને અલગથી ઉમેરેલા 38 સમજાવેલા જવાબ. 15 લખાણવાળી આકૃતિઓની ગુજરાતી રજૂઆત સાથે તમામ 68 મૂળ ચિત્રો જાળવ્યાં છે.</div>'+nav+render(target.getroot().find(C+'content'))
gloss=target.getroot().find(C+'glossary')
if gloss is not None: body+=render(gloss)
# Any non-content source ID remains an explicit provenance anchor, never silently discarded.
rendered=set(re.findall(r'\bid="([^"]+)"',body)); missing=[e.get('id') for e in target.iter() if e.get('id') and e.get('id') not in rendered]
body+=''.join(f'<span id="{h(i)}" class="provenance-anchor"></span>' for i in missing)
write('index.html',page(TITLE,body))
body='<p class="lead">આ જવાબો આ આવૃત્તિ માટે નવા લખાયા છે. તે OpenStaxમાં આપેલા જવાબ નથી. પહેલાં મૂળ પ્રશ્ન અજમાવો, પછી સમજ અને ચકાસણી વાંચો.</p><p>નીચેનો “સ્ત્રોતક્રમ” XMLમાં પ્રશ્નનો ક્રમ છે; પુસ્તકની છાપેલી કસરત સંખ્યા તરીકે તેને ન લો.</p>'
for a in answers:
 body+=f'<article class="answer" id="answer-{a["source_exercise"]}"><h2>સ્ત્રોતક્રમ {a["source_order"]}</h2><p><a href="index.html#{a["source_exercise"]}">મૂળ પ્રશ્ન પર જાઓ</a> · <code>{a["source_exercise"]}</code></p><p class="badge">નવો પૂરક જવાબ</p>'+math(a['source_equation'])+'<p>'+h(a['explanation_gu'])+'</p>'
 if a['kind']=='check': body+='<p>ડાબી બાજુ: '+math(a['lhs'])+' · જમણી બાજુ: '+math(a['rhs'])+'</p>'
 else:
  body+='<ol class="work">'+''.join('<li>'+math(s)+'</li>' for s in a['steps'])+'</ol>'
  var=re.search('[A-Za-z]',a['source_equation']).group()
  body+=f'<p>ચકાસણી: મૂળ સમીકરણમાં {math(var+"="+a["answer"])} મૂકો. બંને બાજુ સમાન મળે છે. ચોક્કસ મૂલ્યો <a href="QA.json">ગણિત-ચકાસણી નોંધમાં</a> છે.</p>'
 body+='</article>'
write('answers.html',page('મૂળમાં ન આપેલા 38 જવાબો',body))
gallery='<p>ગુજરાતી લખાણ અર્થ અને કોષ્ટકના સંબંધો જાળવે છે; મૂળ ફાઇલ અલગ ખોલી શકાય છે. ખાલી પ્રતિભાવ કોષોમાં કોઈ જવાબ ભર્યો નથી.</p>'
for rec in media:
 if suffix(rec['name']) in ADAPT:
  e=next(e for e in target.iter(C+'media') if e.get('id')==rec['id']); gallery+=adapted(rec['name'],e.get('alt'))
gallery+='<section id="source-erratum"><h2>આકૃતિ 011a: મૂળ છાપભૂલની નોંધ</h2>'+render(next(e for e in target.iter(C+'media') if e.get('id')=='eip-id1169750892315'))+'</section>'
write('figures.html',page('ગુજરાતી આકૃતિ-રજૂઆત અને મૂળ ચિત્રો',gallery))
js('support/FIGURE_ADAPTATIONS.json',[{'source_id':rec['id'],'source_file':'media/'+rec['name'],'source_sha256':rec['sha256'],'presentation':ADAPT[suffix(rec['name'])],'type':'new semantic Gujarati adaptation; exact original retained'} for rec in media if suffix(rec['name']) in ADAPT])
body='''<p class="lead">મૂળ પાઠથી અલગ, આ એકમ માટે નવી શીખવાની મદદ. આખી AX-1/AX-3 યોજના કે ધોરણ 2–6નો સંપૂર્ણ અભ્યાસમાર્ગ અહીં પૂરો થતો નથી.</p>
<h2>સરખી ક્રિયા શા માટે?</h2><p>સમાનતાચિહ્ન બંને બાજુની કિંમત સમાન છે એમ કહે છે. બંને બાજુથી એક જ સંખ્યા બાદ કરીએ અથવા બંને બાજુએ એક જ સંખ્યા ઉમેરીએ તો સમાનતા જળવાય છે. “બાજુ બદલવાથી ચિહ્ન બદલાય” યાદ રાખવાને બદલે બંને બાજુની ક્રિયા લખો.</p><div class="mathline">'''+math('x+3=8')+'''</div><div class="mathline">'''+math('x+3-3=8-3')+'''</div><div class="mathline">'''+math('x=5')+'''</div>
<h2>જ્યાં અટકો ત્યાંથી ફરી શરૂ કરો</h2><p>નીચેનો માર્ગ પોતાની ભૂલ પ્રમાણે પસંદ કરો. ધોરણ કે ઉંમર પરથી ક્ષમતાનું અનુમાન કરાતું નથી.</p>
<section id="route-substitution"><h3>1 · ઉકેલ ચકાસતાં અટકો</h3><p>ચાલની દરેક જગ્યાએ સૂચવેલી સંખ્યા કૌંસમાં મૂકો. બે બાજુ અલગ ગણીને સરખાવો.</p>'''+math('3x+1=10')+'''<p>x = 3 અજમાવો.</p><details><summary>પ્રતિસાદ</summary>ડાબે 3 × 3 + 1 = 10; જમણે 10. તેથી 3 ઉકેલ છે.</details><p>ફરી ચકાસો: x = 2 હોય તો શું થાય?</p><details><summary>ફરી ચકાસણીનો જવાબ</summary>ડાબે 7 અને જમણે 10. 2 ઉકેલ નથી.</details><a href="index.html#'''+exercises[4].get('id')+'''">મૂળ ઉદાહરણ જુઓ</a></section>
<section id="route-balance"><h3>2 · કઈ ક્રિયા કરવી તે નક્કી ન થાય</h3><p>ચલ સાથે ઉમેરેલી સંખ્યાને દૂર કરવા બંને બાજુથી તે બાદ કરો. ચલમાંથી બાદ થયેલી સંખ્યાને દૂર કરવા બંને બાજુએ તે ઉમેરો.</p>'''+math('x-6=11')+'''<details><summary>ઉકેલ</summary>બંને બાજુએ 6 ઉમેરો: x − 6 + 6 = 11 + 6; x = 17. ચકાસણી: 17 − 6 = 11.</details><p>ફરી ચકાસો: y + 8 = 3.</p><details><summary>ફરી ચકાસણીનો જવાબ</summary>બંને બાજુથી 8 બાદ કરો: y = −5. ચકાસણી: −5 + 8 = 3.</details></section>
<section id="route-sign"><h3>3 · કૌંસ ખોલતાં ચિહ્નની ભૂલ થાય</h3><p>કૌંસ બહારની સંખ્યાથી અંદરના દરેક પદને ગુણો. ઋણ સંખ્યાનો ઋણ સાથે ગુણાકાર ધન છે.</p>'''+math('-2(x-3)=-2x+6')+'''<p>ફરી ચકાસો: −3(y + 4) + 4y = 5.</p><details><summary>ફરી ચકાસણીનો જવાબ</summary>−3y − 12 + 4y = 5; y − 12 = 5; y = 17. ચકાસણી: −3(21) + 68 = 5.</details></section>
<section id="route-fraction"><h3>4 · અપૂર્ણાંક કે દશાંશમાં અટકો</h3><p>સમીકરણ ઉકેલવાની રીત બદલાતી નથી. અપૂર્ણાંકોનો સરવાળો કરતાં સમાન છેદ લો; દશાંશમાં સ્થાનકિંમત જાળવો.</p>'''+math('x-1/4=1/2')+'''<details><summary>ઉકેલ</summary>બંને બાજુએ 1/4 ઉમેરો: x = 2/4 + 1/4 = 3/4.</details><p>ફરી ચકાસો: y + 0.7 = 1.2.</p><details><summary>ફરી ચકાસણીનો જવાબ</summary>બંને બાજુથી 0.7 બાદ કરો: y = 0.5. ચકાસણી: 0.5 + 0.7 = 1.2.</details></section>
<section id="route-words"><h3>5 · શબ્દપ્રશ્નને સમીકરણમાં ફેરવતાં અટકો</h3><p>અજ્ઞાત રાશિને એકમ સાથે નામ આપો. “કરતાં ઓછું”માં કોણ ઓછું છે તે પહેલાં નક્કી કરો.</p><p>ઉદાહરણ: એક પુસ્તકની કિંમત બીજી કિંમત કરતાં 8 ડૉલર ઓછી છે અને તે 24 ડૉલર છે. બીજી કિંમત p ડૉલર લો: p − 8 = 24; p = 32. ચકાસણી: 32 − 8 = 24.</p><p>ફરી ચકાસો: કુલ 19 પાનાંમાંથી 7 પાનાં વાંચ્યાં. બાકી b પાનાં માટે સમીકરણ બનાવો.</p><details><summary>ફરી ચકાસણીનો જવાબ</summary>b + 7 = 19; b = 12 પાનાં. ચકાસણી: 12 + 7 = 19.</details></section>
<h2>આગળ વધવાની પોતાની ચકાસણી</h2><p>દરેક પ્રકારનો પ્રશ્ન મદદ જોયા વિના ઉકેલો, પછી મૂળ સમીકરણમાં અવેજી કરીને ચકાસો. ભૂલ હોય તો સંબંધિત માર્ગ વાંચો અને ફરી ચકાસણી કરો. અહીંના પ્રતિસાદ માટે બીજા વ્યક્તિની હાજરી જરૂરી નથી.</p>'''
write('support.html',page('સમાનતા સમજવા અને ભૂલ સુધારવા મદદ',body))
body='''<p>આ m82463નો પૂર્ણ ગુજરાતી એકમ છે, 82 એકમના A10 પુસ્તકની પૂર્ણ આવૃત્તિ નહીં. અગાઉનું 13-એકમ પેકેટ અપરિવર્તિત છે. આ એકમ જોડવાથી મૉડ્યુલ-અનુવાદ પ્રગતિ 14/82 થશે; આખા પુસ્તકની સામગ્રી-બંધતા, સંપૂર્ણ AX-1/AX-3 અને અલગ ધોરણ 2–6 માર્ગ હજુ બાકી છે.</p>
<h2>સ્ત્રોત અને શ્રેય</h2><p>OpenStax, <cite>Elementary Algebra 2e</cite>. Senior contributing authors: Lynn Marecek, MaryAnne Anthony-Smith, Andrea Honeycutt Mathis. Canonical collection col31130; module m82463. <a href="https://github.com/openstax/osbooks-prealgebra-bundle/tree/38cae454e644abf9f0a623e876994553881597c9/modules/m82463">ચોક્કસ સત્તાવાર સ્ત્રોત</a>.</p>
<p>પુનઃપ્રાપ્ત ગુજરાતી મસોદો સુધારીને વપરાયો છે. નવી આવૃત્તિમાં લખાણ/વર્ણનોના નોંધાયેલા સુધારા, 15 ગુજરાતી આકૃતિ-રૂપાંતરો, 38 અલગ નવા જવાબો અને આ એકમની નવી સહાય છે. OpenAI Codex દ્વારા તૈયાર કરેલું યાંત્રિક અનુવાદ-સંપાદન અને સહાયક લખાણ; માનવીય પ્રમાણિત અનુવાદ તરીકે રજૂ કરાતું નથી. OpenStax અથવા Rice University આ અનુવાદને સમર્થન આપતાં નથી.</p>
<p>સત્તાવાર pinned repository અને આ રૂપાંતર: <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a>, component-specific notices સહિત. <a href="notices/A10-LICENSE.txt">પ્રાપ્ત લાઇસન્સની પૂર્ણ નકલ</a>. Noto Sans Gujarati: <a href="assets/OFL.txt">SIL Open Font License</a>. ચિહ્નો/ટ્રેડમાર્ક માટે વધારાના હક્ક અપાતા નથી.</p>
<p>પુનઃપ્રાપ્ત <a href="notices/A10-NOTICE.txt">જૂની Indonesian preservation notice</a> માત્ર પૂર્વરૂપનો ઐતિહાસિક શ્રેય છે; તેમાંની 82/82 અથવા PDF-પાનાંની સંખ્યા આ ગુજરાતી પેકેટનો દાવો નથી. અહીં કોઈ Indonesian અથવા A00નો પૂર્ણ પાઠ સમાવાયો નથી.</p>
<h2>ચકાસી શકાય તેવી ફાઇલો</h2><ul><li><a href="source/en.cnxml">અચળ અંગ્રેજી સ્ત્રોત</a></li><li><a href="source/recovered.gu.cnxml">અચળ પુનઃપ્રાપ્ત ગુજરાતી મસોદો</a></li><li><a href="source/m82463.gu.cnxml">સુધારેલ ગુજરાતી CNXML</a></li><li><a href="REVISION.json">દરેક સંપાદન અને મૂળ છાપભૂલની નોંધ</a></li><li><a href="support/NEW_ANSWERS.json">38 નવા જવાબોના સ્થિર ID</a></li><li><a href="CANON_REVIEW.md">ગુજરાતી ગણિતીય વપરાશના નિર્ણયો અને સંદર્ભો</a></li><li><a href="EXPERT_REVIEW_LOG.json">શબ્દાવલી અને મુશ્કેલ પસંદગીઓનું પૂર્ણ એકમ-લેજર</a></li><li><a href="PACKAGE.json">ચોક્કસ વ્યાપ અને આગળનો એકમ</a></li><li><a href="QA.json">ચકાસણી</a></li><li><a href="BROWSER_QA.json">ડેસ્કટૉપ અને સાંકડા પડદાની તપાસ</a></li><li><a href="MANIFEST.json">ફાઇલ હૅશ</a></li></ul>
<p>વાચકમાં કોઈ બાહ્ય સ્ક્રિપ્ટ, ઑનલાઇન ફૉન્ટ અથવા CDN જરૂરી નથી. અગાઉના એકમના ચાર સંદર્ભો તેમના મૂળ document/target ID સાથે ચિહ્નિત છે; તે એકમો અહીં ઉમેરાયેલા નથી. વાસ્તવિક ઑડિયો, SSML અને સંપૂર્ણ ધોરણવાર અભ્યાસમાર્ગ આ પેકેટમાં નથી.</p>'''
write('about.html',page('વ્યાપ, સ્ત્રોત અને શ્રેય',body))
print(json.dumps({'source_exercises':len(exercises),'source_solutions':sum(e.find(C+'solution') is not None for e in exercises),'new_answers':len(answers),'revisions':len(changes),'adaptations':len(ADAPT),'reader_pages':5}))
