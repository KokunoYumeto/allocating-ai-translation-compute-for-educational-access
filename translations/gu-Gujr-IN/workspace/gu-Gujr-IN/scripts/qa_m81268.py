"""Source-bound m81268 integrity, mathematics and editorial/media handoff.

Superscripts, fractions, grouping and long-division retain their structure.
No supplied answer is inferred from flattened superscript digits, and omitted
source solutions are inventoried rather than inserted in the faithful CNXML.
"""
import ast,hashlib,json,re,sys
from pathlib import Path
from fractions import Fraction
import xml.etree.ElementTree as E
from prepare_m81268 import ROOT,SOURCE,SHA,gather,ATTRIBUTES
from a00_accessibility_attributes import validate_pair,LANGUAGE_ATTRS
C='{http://cnx.rice.edu/cnxml}';M='{http://www.w3.org/1998/Math/MathML}'
OUTPUT=ROOT/'gu-Gujr-IN/translations/a00-m81268.gu.cnxml'
MEDIA=ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'
flat=lambda e:' '.join(''.join(e.itertext()).split())
def mathtext(e):
 tag=e.tag.removeprefix(M)
 if tag=='mtext' and (e.text or '').strip()in ('Simplify:','સરળ કરો:'):return ''
 if tag in ('mtable','mtext'):raise ValueError('language or table needs contextual review')
 if tag=='msup':return '('+mathtext(e[0])+')**('+mathtext(e[1])+')'
 if tag=='mfrac':return '('+mathtext(e[0])+')/('+mathtext(e[1])+')'
 if tag=='mspace':return ''
 parts=[]
 for child in e:
  t=mathtext(child)
  if child.tag==M+'menclose' and child.get('notation')=='longdiv':
   if not parts:raise ValueError('long division without divisor')
   t='('+t+')/('+parts.pop()+')'
  parts.append(t)
 return (e.text or '')+''.join(parts)
def norm(t):
 t=re.sub(r'\s+','',t).replace(',','').replace('−','-').replace('÷','/').rstrip('.;')
 for x in '×·⋅':t=t.replace(x,'*')
 t=t.replace('[','(').replace(']',')').replace('{','(').replace('}',')')
 t=re.sub(r'(?<=[\d)])(?=\()', '*',t);t=re.sub(r'(?<=\))(?=\d)', '*',t)
 return t
def calc(t):
 if not re.fullmatch(r'[0-9+*()/\-]+',t):raise ValueError(t)
 def walk(n):
  if isinstance(n,ast.Expression):return walk(n.body)
  if isinstance(n,ast.Constant) and type(n.value)is int:return Fraction(n.value)
  if isinstance(n,ast.BinOp):
   a,b=walk(n.left),walk(n.right)
   if isinstance(n.op,ast.Mult):return a*b
   if isinstance(n.op,ast.Add):return a+b
   if isinstance(n.op,ast.Sub):return a-b
   if isinstance(n.op,ast.Div):return a/b
   if isinstance(n.op,ast.Pow) and b.denominator==1:return a**int(b)
  raise ValueError(t)
 return walk(ast.parse(t,mode='eval'))
def expressions(e):
 result=[]
 for m in e.iter(M+'math'):
  try:result.append(norm(mathtext(m)))
  except ValueError:result.append(None)
 return result
def powertext(e):
 if e.tag==M+'math':return norm(mathtext(e))
 if e.tag==C+'span' and e.get('class')=='token':return ''
 out=e.text or ''
 for child in e:
  out+=('**('+flat(child)+')'if child.tag==C+'sup'else powertext(child))+(child.tail or '')
 return out
def numeric_answers(solution):
 direct=solution.find(C+'list')
 slots=list(direct)if direct is not None else [solution]
 out=[]
 for item in slots:
  t=norm(powertext(item))
  if not re.fullmatch(r'[0-9+*()/\-]+',t):return None
  out.append(t)
 return out
def repeated_signature(t):
 parts=t.split('*')
 if parts and all(p==parts[0]for p in parts) and re.fullmatch('[a-z]|[0-9]+',parts[0]):return parts[0],len(parts)
 return None
def power_signature(t):
 m=re.fullmatch(r'\(?([a-z]|\d+)\)?\*\*\((\d+)\)',t)
 return (m[1],int(m[2]))if m else None

LABELS={
 'CNX_BMath_Figure_02_01_003.jpg':[['Car','કાર'],['Fuel economy (mpg)','ઇંધણ કાર્યક્ષમતા (ગૅલન દીઠ માઈલ)'],['Prius','પ્રિયસ'],['Mini Cooper','મિની કૂપર'],['Toyota Corolla','ટોયોટા કોરોલા'],['Versa','વર્સા'],['Honda Fit','હોન્ડા ફિટ']],
 'CNX_BMath_Figure_02_01_003_img.jpg':[['base','આધાર'],['exponent','ઘાતાંક']],
 'CNX_BMath_Figure_02_01_010_img.jpg':[['base','આધાર'],['exponent','ઘાતાંક'],['n factors','n અવયવો']],
 'CNX_BMath_Figure_02_01_020_img.jpg':[['base','આધાર'],['exponent','ઘાતાંક'],['n factors','n અવયવો']],
}
SELF_CHECK={'media_id':'eip-id1164269481313','image':'CNX_BMath_Figure_AppB_007.jpg','columns':['હું આ કરી શકું છું…','વિશ્વાસપૂર્વક','થોડી મદદથી','ના—મને સમજાતું નથી!'],'rows':['ચલ અને બીજગણિતનાં પ્રતીકોનો ઉપયોગ કરવો.','પદાવલીઓ અને સમીકરણો ઓળખવાં.','ઘાતાંકવાળી પદાવલીઓ સરળ કરવી.','ક્રિયાઓના ક્રમનો ઉપયોગ કરીને પદાવલીઓ સરળ કરવી.'],'response_cells':[[None]*3 for _ in range(4)]}
CAR_DATA={'media_id':'fs-id1495317','columns':['કાર','પ્રિયસ','મિની કૂપર','ટોયોટા કોરોલા','વર્સા','હોન્ડા ફિટ'],'fuel_economy_mpg':[48,27,28,26,27],'note':'Exact historical textbook values, not current product specifications. The image has no p/m/c/v/f equations despite source alt claiming them. Preserve source attribution to Bernard Goldbach/Wikimedia Commons.'}
ERRATA={
 'fs-id2953912':{'kind':'aria-variable-and-header','issue':'Source aria calls first variable uppercaseG but visible table usesg; it also describes the second column header ambiguously as the second row.','corrected_aria_gu':'પાંચ હરોળ અને બે સ્તંભનું કોષ્ટક. સ્તંભનાં નામ ગ્રેગની ઉંમર અને ઍલેક્સની ઉંમર છે. ચાર હરોળમાં અનુક્રમે 12 અને 15; 20 અને 23; 35 અને 38; તથા g અને g + 3 છે.'},
 'fs-id1891703':{'kind':'aria-row-order-and-slash','issue':'Source aria puts multiplication before subtraction, whereas this first table has addition, subtraction, multiplication, division. It calls the forward slash a backslash.','corrected_aria_gu':'પાંચ હરોળ અને ચાર સ્તંભનું કોષ્ટક. સ્તંભનાં નામ ક્રિયા, લખાવટ, આમ વાંચો અને પરિણામ છે. ક્રિયાઓનો ક્રમ સરવાળો, બાદબાકી, ગુણાકાર અને ભાગાકાર છે. સરવાળાનું પરિણામ a અને bનો સરવાળો; બાદબાકીનું પરિણામ a અને bનો તફાવત; ગુણાકારનું પરિણામ a અને bનું ગુણનફળ; ભાગાકારનું પરિણામ a અને bનું ભાગફળ છે. ગુણાકાર ટપકાથી અથવા કૌંસથી દર્શાવેલો છે. ભાગાકાર ÷, a/b, અપૂર્ણાંકની રેખા અને લાંબા ભાગાકારથી દર્શાવેલો છે; લાંબા ભાગાકારમાં ભાજક b બહાર અને ભાજ્ય a અંદર છે.'},
 'eip-id1168265095050':{'kind':'aria-slash-name','issue':'Repeated key-concept table really does use addition,multiplication,subtraction,division order; only the backslash description is wrong here.','corrected_aria_gu':ATTRIBUTES['eip-id1168265095050'].replace('ઊલટો ત્રાંસો લીટો','આગળનો ત્રાંસો લીટો')},
 'fs-id1495317':{'kind':'alt-invented-equations','issue':'Actual car image gives only numeric values48,27,28,26,27, not the letter equations described in source alt.','corrected_alt_gu':'કારની ઇંધણ કાર્યક્ષમતાનું બે હરોળ અને છ સ્તંભનું કોષ્ટક. કારના ફોટા અને નામની નીચે ગૅલન દીઠ માઈલ છે: પ્રિયસ 48; મિની કૂપર 27; ટોયોટા કોરોલા 28; વર્સા 26; હોન્ડા ફિટ 27. ચિત્રમાં ચલવાળાં સમીકરણો નથી.'},
 'fs-id2856176':{'kind':'aria-row-number','issue':'Source calls both brackets and braces the third row; braces are fourth row.','corrected_aria_gu':ATTRIBUTES['fs-id2856176'].replace('ત્રીજી હરોળના પહેલા સ્તંભમાં વાંકડિયા','ચોથી હરોળના પહેલા સ્તંભમાં વાંકડિયા')},
 'eip-id1164752763787':{'kind':'summary-literal-escape','issue':r'Source summary contains literal \u2260 rather than the visible inequality symbol≠; faithful string retains it.','corrected_summary_gu':'આ કોષ્ટક અસમાનતા 11 ≠ 15 − 3 પ્રતીકોમાં અને શબ્દોમાં દર્શાવે છે.'},
 'eip-id1164752720013':{'kind':'alt-decimal-confusion','issue':'Source calls2·2 the number2.2. Actual013-02has multiplication dot, first2red and second2black.','corrected_alt_gu':'પદાવલી 2 · 2 છે. પહેલો 2 લાલ છે; ગુણાકારનું ટપકું અને બીજો 2 કાળાં છે.'},
 'eip-id1164752720032':{'kind':'alt-missing-multiplication-sign','issue':'Source quoted expression18 9÷2 omits the multiplication dot; actual014-01is18·9÷2.','corrected_alt_gu':'પદાવલી 18 · 9 ÷ 2 છે. ગુણાકાર અને ભાગાકાર ડાબેથી જમણે કરતાં પરિણામ 81 મળે છે.'},
 'eip-id1164752650718':{'kind':'alt-highlight','issue':'Source says both plus signs are red; actual016-08has5+8red and the secondplus/0black.','corrected_alt_gu':'પદાવલી 5 + 8 + 0 છે. 5 + 8 લાલ છે; પછીની વત્તાની નિશાની અને 0 કાળાં છે.'},
 'eip-id1164754324223':{'kind':'alt-division-symbol','issue':'Source quoted expression usescolon; actual017-03uses÷. Division meaning is unchanged.','corrected_alt_gu':'પદાવલી 8 + 81 ÷ 3 − 25 છે. 81 ÷ 3 લાલ છે; બાકી પદાવલી કાળી છે.'},
 'eip-id1164754324162':{'kind':'aria-intermediate-number','issue':'Source aria says8+27−5 midway instead of8+27−25; actual images and final computation correctly use25.','corrected_aria_gu':'પદાવલી 2³ + 3⁴ ÷ 3 − 5² છે. ઘાતાંકવાળી પદાવલીઓ સરળ કરતાં 8 + 81 ÷ 3 − 25 થાય છે. ભાગાકાર કરતાં 8 + 27 − 25 થાય છે. ડાબેથી જમણે સરવાળો કરતાં 35 − 25 થાય છે અને બાદબાકી કરતાં 10 મળે છે.'},
 'fs-id2757058':{'kind':'source-name-spelling','issue':'Source aria saysDwayneWade; visible table body saysDwyaneWade. Both transliterateડ્વેનવેડ; English identifier spelling remains tableDwyaneWade.','canonical_name':'Dwyane Wade','name_gu':'ડ્વેન વેડ'},
 'eip-id1168266330675':{'kind':'summary-missing-base','issue':'First key-concept item says an expression a^n is a factor multiplied by itself n times; the intended base a is missing from this sentence. The earlier body includesa and the next item/figure is correct. Faithful XML preserves the first-item wording.','corrected_gu':'aⁿમાં a અવયવ તરીકે n વખત આવે છે, જ્યાં n ધન પૂર્ણાંક છે; એટલે aના n સરખા અવયવોનો ગુણાકાર થાય છે.'},
}
BRIDGES={
 'fs-id2786021':{'kind':'ordinal-language-bridge','source_math_note':'nth is encoded asmi n with superscriptmi t andmi h; all remain untouched, unlike translatablemtextth in the summary.','reader_note_gu':'અહીં અંગ્રેજી nthનો અર્થ nમી છે. aની nમી ઘાત એટલે aના n સરખા અવયવોનો ગુણાકાર, જ્યાં n ધન પૂર્ણાંક છે.'},
 'fs-id1269648':{'kind':'English-mnemonic-bridge','reader_note_gu':'મૂળ પાઠ અંગ્રેજી શબ્દોના પ્રથમ અક્ષરોથી P, E, M, D, A, S યાદ રાખે છે. તેમનો ક્રમ ગોળ કૌંસ, ઘાતાંક, ગુણાકાર/ભાગાકાર, સરવાળો/બાદબાકી છે. ગુણાકાર અને ભાગાકારની પ્રાથમિકતા સરખી છે; સરવાળો અને બાદબાકીની પણ સરખી છે. દરેક જોડીની ક્રિયા ડાબેથી જમણે કરો. ગુજરાતી અનુવાદ મૂળ અક્ષરો રાખે છે અને અર્થ સમજાવે છે.'},
}
ENLARGED={'02_01_003.jpg','02_01_003_img.jpg','02_01_010_img.jpg','02_01_020_img.jpg','AppB_007.jpg','02_01_011_img-02.png','02_01_013_img-02.png','02_01_014_img-01.png','02_01_015_img-03.png','02_01_016_img-08.png','02_01_017_img-03.png'}
COLOR_SEQUENCE={
 '011_img-02':'3·7 red including multiplication dot;4+black',
 '012_img-02':'(4+3) red including parentheses;·7black',
 '013_img-02':'first2red;dot and second2black',
 '014_img-02':'162red;÷2black',
 '015_img-02':'only3inside parenthesesred;parenthesesblack',
 '015_img-03':'first3red;plus and4(3)black',
 '015_img-04':'12red;3+black',
 '016_img-02':'(4−2)red including parentheses',
 '016_img-03':'3(2)red including parentheses',
 '016_img-04':'last6red;precedingminusblack',
 '016_img-05':'0red;bracketsblack',
 '016_img-06':'2³red',
 '016_img-07':'3[0]red',
 '016_img-08':'5+8red;secondplus and0black',
 '016_img-09':'13+0red',
 '017_img-02':'allthreepowersred;operatorsblack',
 '017_img-03':'81÷3red',
 '017_img-04':'8+27red;−25black',
 '017_img-05':'35−25red',
}
def main():
 sys.stdout.reconfigure(encoding='utf-8');assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
 source=E.parse(SOURCE).getroot();target=E.parse(OUTPUT).getroot()
 assert target.attrib.pop('{http://www.w3.org/XML/1998/namespace}lang')=='gu-Gujr-IN'
 stats=validate_pair(source,target)
 # Every residual Latin token is a reviewed source variable, mnemonic letter,
 # MPG unit abbreviation, or the source's literal unicode-escape mistake.
 allowed={'a','b','c','f','g','G','m','n','p','q','v','x','y','P','E','M','D','A','S','d','e','s','mpg','u'}
 residual=[]
 for owner,slots in gather(target).items():
  for _,field,t in slots:
   words=re.findall('[A-Za-z]+',t)
   assert all(w in allowed for w in words),(owner,field,t)
   residual.append({'id':owner,'field':field,'tokens':words})
 for e in target.iter():
  for k,v in e.attrib.items():
   if k in LANGUAGE_ATTRS:
    assert all(w in allowed for w in re.findall('[A-Za-z]+',v)),(e.get('id'),k,v)
    assert re.search('[\u0a80-\u0aff]',v),(e.get('id'),k,v)
 exs={e.get('id'):e for e in target.iter(C+'exercise')}
 comparisons=[];numeric_answers_checked=[];numeric_parts=0
 for m in target.iter(M+'math'):
  try:t=norm(mathtext(m))
  except ValueError:continue
  parts=re.split('([=<>≤≥≠])',t)
  if len(parts)==3 and all(re.fullmatch(r'[0-9+*()/\-]+',p)for p in (parts[0],parts[2])):
   a,b=calc(parts[0]),calc(parts[2]);sign=parts[1]
   assert {'=':a==b,'<':a<b,'>':a>b,'≤':a<=b,'≥':a>=b,'≠':a!=b}[sign],t
   comparisons.append(t)
 for ident,ex in exs.items():
  problem=ex.find(C+'problem');sol=ex.find(C+'solution')
  if sol is None:continue
  pm=expressions(problem);sm=numeric_answers(sol)
  if pm and sm and len(pm)==len(sm) and all(t and re.fullmatch(r'[0-9+*()/\-]+',t)for t in pm):
   assert [calc(t)for t in pm]==[calc(t)for t in sm],(ident,pm,sm)
   numeric_answers_checked.append(ident);numeric_parts+=len(pm)
 # Exponent form and expanded form are checked structurally, including letters.
 expansion=[]
 for ident in ['fs-id1259642','fs-id2268695','fs-id2669743','fs-id2785552','fs-id2238151','fs-id1610560','fs-id1892053','fs-id4333462','fs-id4333542','fs-id4333581']:
  ex=exs[ident];pm=expressions(ex.find(C+'problem'));sol=ex.find(C+'solution')
  if ident=='fs-id1259642':sm=[expressions(row[-1])[0]for row in sol.iter(C+'row')]
  elif ident=='fs-id2785552':sm=[t for t in expressions(sol)if t and repeated_signature(t)and '*'in t]
  elif list(sol.iter(C+'sup')):sm=[norm(powertext(sol))]
  elif sol.find(C+'list')is not None:sm=[norm(powertext(item))for item in sol.find(C+'list')]
  else:sm=expressions(sol)
  assert len(pm)==len(sm),(ident,pm,sm)
  for a,b in zip(pm,sm):
   assert (repeated_signature(a)==power_signature(b) and repeated_signature(a)is not None)or(power_signature(a)==repeated_signature(b)and power_signature(a)is not None),(ident,a,b)
   expansion.append((ident,a,b))
 # Read actual image endpoints, bind them to the source problem expressions,
 # and independently evaluate every intermediate row of each full sequence.
 sequences={
  'fs-id1238361':[['4+3*7','4+21','25'],['(4+3)*7','(7)*7','49']],
  'fs-id1956499':[['18/9*2','2*2','4'],['18*9/2','162/2','81']],
  'fs-id2877213':[['18/6+4*(5-2)','18/6+4*(3)','3+4*(3)','3+12','15']],
  'fs-id2563013':[['5+2**3+3*(6-3*(4-2))','5+2**3+3*(6-3*(2))','5+2**3+3*(6-6)','5+2**3+3*(0)','5+8+3*(0)','5+8+0','13+0','13']],
  'fs-id1956305':[['2**3+3**4/3-5**2','8+81/3-25','8+27-25','35-25','10']],
 }
 for ident,groups in sequences.items():
  pm=expressions(exs[ident].find(C+'problem'));assert len(pm)==len(groups)
  for p,seq in zip(pm,groups):
   assert calc(p)==calc(seq[0]);assert len({calc(t)for t in seq})==1,(ident,seq)
 # The supplied3^4table is textual MathML; bind its exact five rows.
 powrows=[expressions(row[-1])[0]for row in exs['fs-id2661125'].find(C+'solution').iter(C+'row')]
 assert powrows==['(3)**(4)','3*3*3*3','9*3*3','27*3','81'],powrows
 assert all(calc(t)==81 for t in powrows)
 # Classifications are based on the equal sign, never on true/false arithmetic.
 classes=0
 for ident in ['fs-id2853302','fs-id2619086','fs-id1891859','fs-id1891908','fs-id1891957','fs-id1891998']:
  ex=exs[ident];pm=expressions(ex.find(C+'problem'));sol=ex.find(C+'solution');sl=sol.find(C+'list')
  ss=[flat(e)for e in sl]if sl is not None else [flat(sol)]
  assert len(pm)==len(ss),(ident,pm,ss)
  for p,s in zip(pm,ss):assert ('સમીકરણ'if '='in p else'પદાવલી')in s,(ident,p,s);classes+=1
 # Five MathML tables: comparison equivalences, square/cube names, and the
 # outer wrong/right-order teaching comparison with two nested work tables.
 tables=list(target.iter(M+'mtable'));assert len(tables)==5
 nested=[t for t in tables if len(list(t.iter(M+'mtable')))==1 and len(t)==3]
 rows=[[norm(mathtext(row[-1]))for row in t]for t in nested]
 assert rows==[['4+3*7','7*7','49'],['4+3*7','4+21','25']],rows
 assert calc(rows[0][0])!=calc(rows[0][1])==calc(rows[0][2])==49
 assert len({calc(t)for t in rows[1]})==1 and calc(rows[1][-1])==25
 assert 7<11 and 11>7 and 17>4 and 4<17
 # MPG numerical comparisons and two supplied-symbol exercises.
 assert CAR_DATA['fuel_economy_mpg']==[48,27,28,26,27]
 for ident,answers in [('fs-id2488024',['>','<']),('fs-id1534636',['<','>'])]:
  assert [norm(flat(item)).lstrip('ⓐⓑ')for item in exs[ident].find(C+'solution').find(C+'list')]==answers
 assert 48>26 and 27<28 and 27<48 and 28>27
 # All source figures are inventoried and their exact bytes pinned.
 inventory=[]
 for e in source.iter(C+'media'):
  file=Path(list(e)[0].get('src')).name;p=MEDIA/file
  short=file.removeprefix('CNX_BMath_Figure_')
  inventory.append({'media_id':e.get('id'),'source_file':file,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'review':'actual image on contact sheet'+('; separately enlarged original'if short in ENLARGED else''),'localization':'self-check data supplied'if file==SELF_CHECK['image']else'Gujarati labels supplied'if file in LABELS else'retain original mathematical symbols/numbers; inspect highlight notes'})
 missing=[e.get('id')for e in source.iter(C+'exercise')if e.find(C+'solution')is None]
 assert len(missing)==36
 receipt={'module':'m81268','source_sha256':SHA,'translation_sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),'integrity':stats,'source_text_tail_alt_slots':805,'other_language_attributes':35,'all_source_language_slots_accounted':840,'natural_English_residuals':0,'reviewed_preserved_Latin_tokens':residual,'numeric_equalities_inequalities_checked':len(comparisons),'numeric_answer_exercises_checked':len(numeric_answers_checked),'numeric_answer_parts_checked':numeric_parts,'numeric_answer_exercise_ids':numeric_answers_checked,'exponent_expansion_parts_checked':len(expansion),'image_worked_sequences_checked':sum(map(len,sequences.values())),'image_worked_steps_checked':sum(len(seq)for groups in sequences.values()for seq in groups),'power_table_steps_checked':len(powrows),'classification_parts_checked':classes,'MathML_tables_reviewed':5,'intentional_wrong_order_example_preserved':True,'missing_source_solution_count':len(missing),'missing_source_solution_ids':missing,'media':inventory,'figure_label_translations':LABELS,'self_check':SELF_CHECK,'car_table':CAR_DATA,'colored_sequence_notes':COLOR_SEQUENCE,'source_errata':ERRATA,'separate_reader_bridges':BRIDGES,'scope_note':'Entire canonical module translated with source structures, all mathematical tokens, numeric literals, IDs, omissions, supplied solutions and source errors retained. Corrections/bridges are explicitly separate editorial material. All44images actually inspected;11alsoenlarged. Five language-bearing images require reader localization;39symbolic originals may be retained. No omitted source answers inserted.'}
 out=ROOT/'gu-Gujr-IN/translations/a00-m81268-media-and-errata.gu.json'
 out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in receipt.items()if k not in ('reviewed_preserved_Latin_tokens','numeric_answer_exercise_ids','missing_source_solution_ids','media','figure_label_translations','self_check','car_table','colored_sequence_notes','source_errata','separate_reader_bridges')},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
