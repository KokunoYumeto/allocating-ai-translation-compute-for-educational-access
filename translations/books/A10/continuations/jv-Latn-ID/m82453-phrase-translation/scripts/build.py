from pathlib import Path
from copy import deepcopy
from lxml import etree as E
import json,html,re
ROOT=Path(__file__).resolve().parents[1]
CN='http://cnx.rice.edu/cnxml';M='http://www.w3.org/1998/Math/MathML';NS={'c':CN,'m':M}
boundary=json.loads((ROOT/'source/BOUNDARY.json').read_text(encoding='utf-8'))
ASSETS={a['id']:a['file'] for a in boundary['media']}
TRACKS={'jv-academic':('jv-Latn-ID','Basa Jawa akademik'),'jv-conversation':('jv-Latn-ID','Basa Jawa padinan · ngoko'),'id-academic':('id-ID','Jembatan Bahasa Indonesia'),'en':('en','Canonical English comparison')}
AUDIO_META=json.loads((ROOT/'audio/AUDIO.json').read_text(encoding='utf-8')) if (ROOT/'audio/AUDIO.json').exists() else {'tracks':{}}
def tag(e):return E.QName(e).localname
def esc(t):return html.escape(t or '',quote=True)
def write(path,text):
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
def render(e,t,parent=None):
 n=tag(e);id=e.get('id');a=f' id="{id}" data-source-id="{id}"' if id else ''
 for attr in ['aria-label','summary']:
  if e.get(attr):a+=f' {attr}="{esc(e.get(attr))}"'
 def inner():return esc(e.text)+''.join(render(c,t,n)+esc(c.tail) for c in e)
 if e.tag.startswith('{'+M+'}'):
  node=deepcopy(e)
  for c in node.iter():c.tag=tag(c)
  E.cleanup_namespaces(node);node.set('xmlns',M)
  return '<span class="math-scroll">'+E.tostring(node,encoding='unicode',with_tail=False)+'</span>'
 if n=='section':return f'<section{a}>{inner()}</section>'
 if n=='title':
  level=2 if parent=='section' else 3
  return f'<h{level}{a}>{inner()}</h{level}>'
 if n=='para':return f'<div class="para"{a}>{inner()}</div>'
 if n=='newline':return '<br>'
 if n=='span':return f'<span class="{esc(e.get("class"))}"{a}>{inner()}</span>'
 if n=='emphasis':
  kind='strong' if e.get('effect')=='bold' else 'em'
  return f'<{kind}{a}>{inner()}</{kind}>'
 if n=='link':return f'<a href="#{e.get("target-id")}">'+('Table' if t=='en' else 'Tabel')+'</a>'
 if n=='table':return f'<div class="table-scroll"><table{a}>{inner()}</table></div>'
 if n in ['tgroup','colspec']:return inner()
 if n in ['thead','tbody']:return f'<{n}{a}>{inner()}</{n}>'
 if n=='row':return f'<tr{a}>{inner()}</tr>'
 if n=='entry':
  head=any(tag(x)=='thead' for x in e.iterancestors());kind='th' if head else 'td'
  return f'<{kind}{a}{" scope=col" if head else ""}>{inner()}</{kind}>'
 if n=='media':
  caption='Gambar sumber basa Inggris; katrangan ing ngisor iki nganggo basa Jawa.' if t.startswith('jv') else ('Gambar sumber berbahasa Inggris; deskripsi di bawah ini dalam bahasa Indonesia.' if t=='id-academic' else 'Unchanged canonical source image.')
  summary='Katrangan gambar' if t.startswith('jv') else ('Deskripsi gambar' if t=='id-academic' else 'Image description')
  return f'<figure{a}><img src="{ASSETS[id]}" alt="{esc(e.get("alt"))}"><figcaption>{caption}</figcaption><details><summary>{summary}</summary><p>{esc(e.get("alt"))}</p></details></figure>'
 if n=='list':
  kind='ol' if e.get('list-type')=='enumerated' else 'ul'
  return f'<{kind}{a}>{inner()}</{kind}>'
 if n=='item':return f'<li{a}>{inner()}</li>'
 if n=='example':
  label='Tuladha saka sumber' if t.startswith('jv') else ('Contoh dari sumber' if t=='id-academic' else 'Source example')
  return f'<section class="example"{a}><p class="eyebrow">{label}</p>{inner()}</section>'
 if n=='note':return f'<aside class="note"{a}>{inner()}</aside>'
 if n=='solution':return f'<details class="solution"{a}><summary>'+('Wangsulan saka sumber' if t.startswith('jv') else ('Jawaban dari sumber' if t=='id-academic' else 'Source-supplied answer'))+f'</summary>{inner()}</details>'
 if n=='problem':
  compare='' if t=='en' else f'<p class="source-link"><a href="en.html#{id}" lang="en">Exact English source wording</a></p>'
  return f'<div class="problem"{a}>{inner()}{compare}</div>'
 if n=='equation':return f'<div class="equation"{a}>{inner()}</div>'
 return f'<div class="{n}"{a}>{inner()}</div>'

LETTERS={'a':'a','b':'be','l':'el','m':'em','n':'en','p':'pe','q':'ki','w':'we','x':'eks','y':'ye','z':'zet'}
JV={0:'nol',1:'siji',2:'loro',3:'telu',4:'papat',5:'lima',6:'enem',7:'pitu',8:'wolu',9:'sanga',10:'sepuluh',11:'sewelas',12:'rolas',13:'telulas',14:'patbelas',15:'limalas',16:'nembelas',17:'pitulas',18:'wolulas',19:'sangalas'}
ID={0:'nol',1:'satu',2:'dua',3:'tiga',4:'empat',5:'lima',6:'enam',7:'tujuh',8:'delapan',9:'sembilan',10:'sepuluh',11:'sebelas',12:'dua belas',13:'tiga belas',14:'empat belas',15:'lima belas',16:'enam belas',17:'tujuh belas',18:'delapan belas',19:'sembilan belas'}
def num(s,t):
 n=int(s);d=JV if t.startswith('jv') else ID
 if n in d:return d[n]
 if n<100:return d[n//10]+' puluh'+(' '+d[n%10] if n%10 else '')
 raise ValueError(('unsupported narration number',s))
def variable(s,t):return ('aksara ' if t.startswith('jv') else 'huruf ')+LETTERS[s]
def plain(s,t):
 s=s or ''
 # A single substitution pass avoids recursively expanding the spoken letter a.
 def token(m):
  if m[1]:return num(m[1],t)+(' ping ' if t.startswith('jv') else ' kali ')+variable(m[2],t)
  return num(m[3],t) if m[3] else variable(m[4],t)
 s=re.sub(r'\b(?:(\d+)([abxlwymnpqz])|(\d+)|([abxlwymnpqz]))\b',token,s)
 s=s.replace('²',' pangkat loro ' if t.startswith('jv') else ' pangkat dua ')
 s=s.replace('−',' dikurangi ').replace('+',' ditambah ').replace('÷',' dipara ' if t.startswith('jv') else ' dibagi ').replace('=',' padha karo ' if t.startswith('jv') else ' sama dengan ')
 s=s.replace('ⓐ',' Bagean a. ' if t.startswith('jv') else ' Bagian a. ').replace('ⓑ',' Bagean be. ' if t.startswith('jv') else ' Bagian b. ')
 return s
def speak_math(e,t):
 n=tag(e);children=list(e)
 if n=='mi':return variable(e.text,t)
 if n=='mn':return num(e.text,t)
 if n=='mo':
  return {'+':'ditambah','−':'dikurangi','·':'ping' if t.startswith('jv') else 'kali','÷':'dipara' if t.startswith('jv') else 'dibagi','(':'bukak kurung' if t.startswith('jv') else 'buka kurung',')':'tutup kurung',',':' ; ','.':'.'}.get(e.text,e.text or '')
 if n=='mtext':return (('dipara, ditulis garis miring' if t.startswith('jv') else 'dibagi, ditulis garis miring') if e.text=='/' else plain(e.text,t))
 if n=='mspace':return ''
 if n=='msup':return speak_math(children[0],t)+' pangkat '+speak_math(children[1],t)+', pungkasan pangkat' if t.startswith('jv') else speak_math(children[0],t)+' pangkat '+speak_math(children[1],t)+', akhir pangkat'
 if n=='mfrac':return ('wiwitan pecahan; pembilang ' if t.startswith('jv') else 'awal pecahan; pembilang ')+speak_math(children[0],t)+'; penyebut '+speak_math(children[1],t)+('; pungkasan pecahan' if t.startswith('jv') else '; akhir pecahan')
 if n=='menclose':return ('ing njero para gapit: ' if t.startswith('jv') else 'di dalam tanda pembagian bersusun: ')+' '.join(speak_math(c,t) for c in e)
 if n=='mtable':
  rows=[r for r in children if len(r)]
  return ' '.join(('Larik ' if t.startswith('jv') else 'Baris ')+num(str(i+1),t)+': '+' ; '.join(speak_math(c,t) for c in row) for i,row in enumerate(rows))
 # MathML implies multiplication when operands are juxtaposed; say it explicitly.
 operand={'mi','mn','msup','mfrac','mrow'}
 words=[];i=0
 while i<len(children):
  c=children[i]
  if i+1<len(children) and tag(children[i+1])=='menclose' and children[i+1].get('notation')=='longdiv':
   words.append(('pembagi ing njaba para gapit: ' if t.startswith('jv') else 'pembagi di luar tanda pembagian bersusun: ')+speak_math(c,t)+'; '+speak_math(children[i+1],t));i+=2;continue
  if i and ((tag(children[i-1]) in operand or (tag(children[i-1])=='mo' and children[i-1].text==')')) and (tag(c) in operand or (tag(c)=='mo' and c.text=='('))):words.append('ping' if t.startswith('jv') else 'kali')
  words.append(speak_math(c,t));i+=1
 return ' '.join(words)
def speak(e,t):
 n=tag(e)
 if e.tag.startswith('{'+M+'}'):return speak_math(e,t)
 if n=='media':return plain(e.get('alt'),t)
 if n=='image':return ''
 if n=='table':
  rows=e.findall('.//c:row',NS)
  return ('Tabel. ' if t.startswith('jv') else 'Tabel. ')+ ' '.join(('Larik ' if t.startswith('jv') else 'Baris ')+num(str(i+1),t)+'. '+'; '.join(('Kolom ')+num(str(j+1),t)+': '+speak(c,t) for j,c in enumerate(row)) for i,row in enumerate(rows))
 if n=='solution':prefix='Wangsulan saka sumber. ' if t.startswith('jv') else 'Jawaban dari sumber. '
 elif n=='newline':return '. '
 else:prefix=''
 return prefix+plain(e.text,t)+' '+ ' '.join(speak(c,t)+' '+plain(c.tail,t) for c in e)

for track,(lang,label) in TRACKS.items():
 section=E.parse(str(ROOT/('source/en.cnxml' if track=='en' else f'translation/{track}.cnxml'))).getroot()
 nav='<nav><a href="index.html">Pambuka / Awal</a> · '+' · '.join(f'<a href="{k}.html" lang="{l}">{v}</a>' for k,(l,v) in TRACKS.items())+'</nav>'
 intro='<p class="scope" lang="en">One complete source section, not a completed module/book. Javanese instructional text supplies localized meanings of the English phrases; every problem links to its exact English wording. Indonesian is a distinct pinned comparison bridge, not native Javanese evidence.</p>'
 notice='<aside class="note" lang="en">Source figures retain their English wording and original pixels because English phrase structure is being taught. The local descriptions explain their meaning and the exact red highlights. “More than” / “less than” here describe addition/subtraction, not inequality claims.</aside>'
 body=nav+f'<header><p class="eyebrow">A10 · m82453 · continuation</p><h1>{label}</h1>{intro}</header>'+notice+render(section,track)
 if track!='en':
  blocks=[]
  for i,c in enumerate(section):
   anchor=c.get('id') or boundary['section']+'--title'
   words=re.sub(r'\s+',' ',speak(c,track)).strip();blocks.append((anchor,words))
  has_audio=track in AUDIO_META.get('tracks',{})
  if has_audio:
   audio_note='Synthetic Javanese audio is supplied as a separately labelled, source-bound derivative. It is not a human recording; pronunciation remains provisional.'
  elif track=='id-academic':
   audio_note='This Indonesian comparison bridge has source-positioned written narration and SSML only; it is not evidence of, or a substitute for, Javanese audio.'
  else:
   audio_note='No actual audio is present for this track.'
  md='# '+label+' — written narration\n\n'+audio_note+'\n\n'+'\n\n'.join('## '+a+'\n\n'+w for a,w in blocks)+'\n'
  write(f'narration/{track}.md',md)
  ssml=E.Element('speak',version='1.0',attrib={'{http://www.w3.org/XML/1998/namespace}lang':lang})
  for a,w in blocks:
   E.SubElement(ssml,'mark',name=a);E.SubElement(ssml,'p').text=w
  write(f'narration/{track}.ssml',E.tostring(ssml,encoding='unicode'))
  audio_html=''
  if has_audio:
   meta=AUDIO_META['tracks'][track];src=meta['file']
   audio_html=f'<audio controls preload="metadata" src="{src}">Download <a href="{src}">the synthetic Javanese MP3</a>.</audio><p lang="en">Synthetic Javanese voice: <code>{esc(meta["voice"])}</code>; {esc(str(meta["duration_seconds"]))} seconds. This is not a human recording, and pronunciation has not been human-certified.</p>'
  else:
   audio_html='<p lang="en">Written narration and SSML only for this bridge; it is not used as an audio fallback for Javanese.</p>' if track=='id-academic' else '<p lang="en">No actual audio is present for this track.</p>'
  body+=f'<section><h2>Naskah wacan / Naskah narasi</h2><p><a href="narration/{track}.md">Written narration</a> · <a href="narration/{track}.ssml">SSML</a></p>{audio_html}</section>'
 body+='<footer lang="en"><p>OpenStax Elementary Algebra 2e, authors Lynn Marecek, MaryAnne Anthony-Smith, Andrea Honeycutt Mathis. CC BY-NC-SA 4.0, subject to original credits. No OpenStax endorsement. <a href="NOTICE.md">Attribution and corrections</a> · <a href="provenance/CONSULTATIONS.md">Canon decisions</a> · <a href="provenance/MODEL.md">Model provenance</a> · <a href="PACKAGE.json">Scope</a> · <a href="QA.json">QA</a> · <a href="BROWSER_QA.json">Browser QA</a>.</p></footer>'
 write(track+'.html',f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{label} — frasa lan aljabar</title><link rel="stylesheet" href="reader.css"></head><body><main>{body}</main></body></html>\n')

audio_status='Rong trek audio sintetik basa Jawa wis ana, dicantumake swara lan suwene, lan dudu rekaman manungsa.' if all(k in AUDIO_META.get('tracks',{}) for k in ['jv-academic','jv-conversation']) else 'Audio basa Jawa durung ana; aja nganggo swara basa liya minangka gantine.'
index=f'''<!doctype html><html lang="jv-Latn-ID"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Frasa lan aljabar · Basa Jawa</title><link rel="stylesheet" href="reader.css"></head><body><main>
<header><p class="eyebrow">OpenStax Elementary Algebra 2e · A10 · m82453</p><h1>Saka frasa menyang aljabar</h1><p>Sinau nemtokake operasi, njaga urutan pangurangan lan paran, lan nggunakake tandha kurung nalika ngowahi frasa dadi ekspresi aljabar.</p><p class="scope">Paket iki ngrampungake siji perangan sumber: “Translate an English Phrase to an Algebraic Expression”. Iki dudu modul utawa buku sing wis rampung.</p></header>
<div class="cards"><section class="card"><h2><a href="jv-academic.html">Basa Jawa akademik</a></h2><p>Andharan runtut kanthi istilah aljabar lan wangsulan saka sumber.</p></section><section class="card"><h2><a href="jv-conversation.html">Basa Jawa padinan · ngoko</a></h2><p>Panjelasan kanthi basa padinan. Isi matematika lan soal padha.</p></section><section class="card" lang="id-ID"><h2><a href="id-academic.html">Jembatan Bahasa Indonesia</a></h2><p>Pembanding Indonesia dari versi sumber v1.0.2; bukan bukti pemakaian bahasa Jawa.</p></section><section class="card" lang="en"><h2><a href="en.html">Exact English comparison</a></h2><p>Original wording, formulas, supplied solutions and three unchanged source images.</p></section></div>
<section><h2>Cara nggunakake</h2><p>Piliha jalur basa. Coba soal sadurunge mbukak “Wangsulan saka sumber”. Yen perlu ndeleng frasa Inggris asline, gunakna pranala ing saben soal. Gambar Inggris tetep asli; saben gambar duwe katrangan teks lengkap.</p><aside class="note"><p>Ing perangan iki, “more than” lan “less than” nuduhake panambahan lan pangurangan. Padanan Jawa ditulis kanthi urutan operasi sing cetha, ora minangka pratelan tandha luwih gedhe utawa luwih cilik. Frasa “five times the sum” mbutuhake kurung kanggo kabeh gunggung.</p></aside></section>
<section><h2>Naskah wacan lan audio AX-2</h2><p>Ana naskah narasi lan SSML kanggo telung jalur basa. Pangkat, pecahan, kurung, ping-pingan sing ora ditulis tandhane, tabel, gambar, lan wangsulan diterangake nganggo tembung. {audio_status}</p></section>
<section lang="en"><h2>Exact coverage</h2><p>One complete source subtree <code>fs-id1170654942537</code>: 23 direct children, 106 source IDs, 63 MathML occurrences, 15 exercises with all 15 supplied solutions, and three canonical figures. Five worked examples and ten practice exercises are retained. No new scored assessment is introduced.</p><p>Excluded: the rest of m82453, other modules, and full-book reference/media closure. Next source anchor: <code>fs-id1170655188891</code> (Key Concepts). The full assignment remains all 82 A10 modules and the complete learning/accessibility workflow.</p></section>
<footer lang="en"><p><a href="NOTICE.md">Attribution, pins and corrections</a> · <a href="LICENSE.txt">License</a> · <a href="PACKAGE.json">Package scope</a> · <a href="QA.json">QA</a> · <a href="BROWSER_QA.json">Browser QA</a> · <a href="MANIFEST.json">File manifest</a> · <a href="provenance/CONSULTATIONS.md">Canon decisions</a> · <a href="provenance/MODEL.md">Model provenance</a> · <a href="EXPERT_REVIEW_LOG.json">Expert-review ledger</a></p><p>Adapted from OpenStax, by Lynn Marecek, MaryAnne Anthony-Smith and Andrea Honeycutt Mathis. CC BY-NC-SA 4.0, subject to original credits. No OpenStax endorsement. Provisional AI-authored Javanese adaptation; no human certification is claimed.</p></footer></main></body></html>\n'''
write('index.html',index)
print('Four offline readers, three source-positioned narration/SSML tracks, and the index were built.')
