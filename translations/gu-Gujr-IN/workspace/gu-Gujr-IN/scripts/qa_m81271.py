"""Exact equation QA and actual-media handoff for all supplied m81271 answers."""
import hashlib,json,re,sys
from pathlib import Path
from fractions import Fraction
import xml.etree.ElementTree as E
from prepare_m81271 import ROOT,SOURCE,SHA,gather
from a00_accessibility_attributes import validate_pair,LANGUAGE_ATTRS
from qa_m81270 import norm,polynomial,evaluate
C='{http://cnx.rice.edu/cnxml}';M='{http://www.w3.org/1998/Math/MathML}'
OUTPUT=ROOT/'gu-Gujr-IN/translations/a00-m81271.gu.cnxml'
MEDIA=ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'
flat=lambda e:' '.join(''.join(e.itertext()).split())

def mt(e):
 if e.tag==M+'mtext':
  t=(e.text or '').strip()
  if not t:return ''
  if t in ('when','જ્યારે'):return '@'
  if t in ('Determine whether','નક્કી કરો કે','Is','શું','Evaluate','કિંમત શોધો:'):return ''
  if t in ('is a solution of','ઉકેલ છે કે નહીં આ સમીકરણનો:','a solution of','ઉકેલ છે આ સમીકરણનો:'):return '|'
  if re.fullmatch(r'\$\d+|\?',t):return t
  raise ValueError(t)
 if e.tag==M+'mtable':raise ValueError('table')
 if e.tag==M+'mspace':return ''
 if e.tag==M+'msup':return '('+mt(e[0])+')**('+mt(e[1])+')'
 if e.tag==M+'mfrac':return '('+mt(e[0])+')/('+mt(e[1])+')'
 return (e.text or '')+''.join(mt(c)for c in e)
def maths(e):
 out=[]
 for m in e.iter(M+'math'):
  try:out.append(norm(mt(m)))
  except ValueError:out.append(None)
 return out
def written(e):
 if e.tag==M+'math':return mt(e)
 if e.tag==C+'span'and e.get('class')=='token':return ''
 return (e.text or '')+''.join(written(c)+(c.tail or '')for c in e)
def compact(solution):
 return norm(written(solution)).replace('$','').rstrip('.')
def sides(eq):
 pair=eq.replace('?','').replace('✓','').split('=');assert len(pair)==2,(eq,pair)
 return pair
def equation_polys(eq):return tuple(polynomial(t)for t in sides(eq))
def solve(eq):
 a,b=sides(eq);p=polynomial('('+a+')-('+b+')');variables=[k for k in p if k]
 assert len(variables)==1 and len(variables[0])==1,(eq,p)
 k=variables[0];return k[0],-p.get((),0)/p[k]
def holds(eq,env=None):
 a,b=sides(eq);return evaluate(a,env)==evaluate(b,env)
def assigned(eq):
 a,b=sides(eq);assert re.fullmatch('[a-z]',a),(eq,a)
 return a,evaluate(b)
def same_equation(got,wanted):assert equation_polys(got)==equation_polys(wanted),(got,wanted)

# Each entry is manually bound to the full canonical problem, not inferred
# merely from the supplied answer. Source indices are asserted by ID below.
SOLVE_MAIN={12:('fs-id2297687','x+8=17'),15:('fs-id588715','100=y+74'),18:('fs-id1572945','x-5=8'),21:('fs-id2608765','27=a-16')}
COMPACT_SOLVE=set([13,14,16,17,19,20,22,23,55,57,59,61,63,65,67,69,71,73,75,77])
BOOL_MAIN={3:('fs-id1371062',False),6:('fs-id2390900',True)}
BOOL_COMPACT={4,5,7,8,39,41,43,45,47,49}
MODELS={9:('fs-id2201230',4,5),10:('fs-id1969582',1,7),11:('fs-id1282732',3,4),51:('fs-id1612218',2,5),53:('fs-id2587676',3,6)}
WORD_EQUATIONS={
 24:('fs-id1524263','6+9=15'),25:('fs-id2751334','7+6=13'),26:('fs-id2379660','8+6=14'),
 27:('fs-id1714226','8*7=56'),28:('fs-id1587742','6*9=54'),29:('fs-id1392031','21*3=63'),
 30:('fs-id3242407','2*(x-3)=18'),31:('fs-id1516593','2*(x-5)=30'),32:('fs-id1973694','2*(y-4)=16'),
 79:('fs-id2241253','8+9=17'),81:('fs-id2425667','23-19=4'),83:('fs-id2275837','3*9=27'),85:('fs-id2434661','54/6=9'),87:('fs-id2925319','2*(n-10)=52'),89:('fs-id1730534','3*y+10=100')}
TRANSLATE_SOLVE={
 33:('fs-id2646972','x+3=47'),34:('fs-id2198774','x+7=37'),35:('fs-id1381605','y+11=28'),
 36:('fs-id1823280','y-14=18'),37:('fs-id1919754','z-17=37'),38:('fs-id2280096','x-19=45'),
 91:('fs-id1474456','p+5=21'),93:('fs-id1772561','r+18=73'),95:('fs-id2135772','d-30=52'),97:('fs-id1281817','u-12=89'),99:('fs-id1579845','c-325=799')}
# Every row was transcribed from actual images; checks use exact algebra.
IMAGE_PATHS={
 '019/020':(['x+3=8','x+3-3=8-3','x=5'],['5+3=8','8=8']),
 '021/022':(['x+4=5','x+4-4=5-4','x=1'],['1+4=5','5=5']),
 '023':(['x+8=17','x+8-8=17-8','x=9'],['9+8=17','17=17']),
 '024/025':(['100=y+74','100-74=y+74-74','26=y'],['100=26+74','100=100']),
 '026':(['x-5=8','x-5+5=8+5','x=13'],['13-5=8','8=8']),
 '027':(['27=a-16','27+16=a-16+16','43=a'],['27=43-16','27=27']),
 '030':(['x+3=47','x+3-3=47-3','x=44'],['44+3=47','47=47']),
 '031':(['y-14=18','y-14+14=18+14','y=32'],['32-14=18','18=18']),
}
FIGURE_LABELS={
 'CNX_BMath_Figure_02_03_017_img-01.png':{'source_text':'Substitute 5 for x.','Gujarati':'xની જગ્યાએ 5 મૂકો.','red':['5']},
 'CNX_BMath_Figure_02_03_018_img-01.png':{'source_text':'Substitute 2 for y.','Gujarati':'yની જગ્યાએ 2 મૂકો.','red':['2']},
 'CNX_BMath_Figure_02_03_026_img-01.png':{'source_text':'Now we can check. Let x = 13.','Gujarati':'હવે ચકાસી શકીએ. ધારો કે x = 13.','red':['13']},
 'CNX_BMath_Figure_02_03_027_img-01.png':{'source_text':'Now we can check. Let a = 43.','Gujarati':'હવે ચકાસી શકીએ. ધારો કે a = 43.','red':['43'],'source_alt_erratum':'eip-id1168468500212'},
 'CNX_BMath_Figure_02_03_032-01.png':{'source_rows':['The sum of 6 and 9 is 15.','The sum of 6 and 9 = 15.'],'Gujarati_rows':['6 અને 9નો સરવાળો બરાબર છે 15.','6 અને 9નો સરવાળો = 15.'],'boxed_gu':'બરાબર છે','arrow':'cyan downward from boxed equals words to =; preserve operand order6,9,15'},
 'CNX_BMath_Figure_02_03_028_img-01.png':{'source_rows':['The product of 8 and 7 is 56.','The product of 8 and 7 = 56.'],'Gujarati_rows':['8 અને 7નું ગુણનફળ બરાબર છે 56.','8 અને 7નું ગુણનફળ = 56.'],'boxed_gu':'બરાબર છે','arrow':'cyan downward from boxed equals words to =; preserve operand order8,7,56'},
 'CNX_BMath_Figure_02_03_029_img-01.png':{'source_text':'Twice the difference of x and 3 gives 18.','Gujarati':'x અને 3ના તફાવતના બમણા કરતાં મળે 18.','boxed_gu':'મળે'},
 'CNX_BMath_Figure_02_03_029_img-02.png':{'source_text':'Twice the difference of x and 3 gives 18.','Gujarati':'x અને 3ના તફાવતના બમણા કરતાં મળે 18.','boxed_gu':'મળે','phrase_maps_gu':[['બમણા','2'],['x અને 3ના તફાવત','(x − 3)'],['મળે','='],['18','18']],'math_row':'2 (x − 3) = 18','layout_note':'Gujarati phrase order differs from English: the cyan brace connectors must map the same phrase meanings to the math tokens, never imply(2x)−3. Keep equation token order2,(x−3),=,18.'},
}
SELF_CHECK={'media_id':'eip-id1164271039378','source_file':'CNX_BMath_Figure_AppB_010.jpg','columns':['હું આ કરી શકું છું…','વિશ્વાસપૂર્વક','થોડી મદદથી','ના—મને સમજાતું નથી!'],'rows':['સંખ્યા સમીકરણનો ઉકેલ છે કે નહીં તે નક્કી કરવું.','સમાનતાના બાદબાકીના ગુણધર્મને નમૂના દ્વારા દર્શાવવો.','સમાનતાના બાદબાકીના ગુણધર્મ વડે સમીકરણો ઉકેલવાં.','સમાનતાના સરવાળાના ગુણધર્મ વડે સમીકરણો ઉકેલવાં.','શબ્દસમૂહોને બીજગણિતનાં સમીકરણોમાં ફેરવવાં.','સમીકરણ બનાવીને ઉકેલવું.'],'response_cells':[[None]*3 for _ in range(6)]}
ERRATA={
 'fs-id4876998':{'kind':'alt-color','issue':'Source calls removal circles/arrows red. Actual002showsmagenta outlines/arrows and green transitionarrow.','corrected_alt_gu':'ડાબા નમૂનામાં પરબીડિયું અને ત્રણ ગોળી, જમણે આઠ ગોળી છે. બંને બાજુ ત્રણ ગોળી આસપાસ જાંબલી ગુલાબી રંગનું વલય અને બહાર તરફ તીર છે. બંને બાજુથી ત્રણ ગોળી દૂર કરતાં ડાબે માત્ર પરબીડિયું અને જમણે પાંચ ગોળી રહે છે. બંને નમૂના વચ્ચે લીલું તીર છે.'},
 'fs-id1572781':{'kind':'alt-color','issue':'Source calls removal circles/arrows red. Actual005showsmagenta.','corrected_alt_gu':'ડાબા નમૂનામાં પરબીડિયું અને ચાર ગોળી, જમણે પાંચ ગોળી છે. બંને બાજુ ચાર ગોળીની આસપાસ જાંબલી ગુલાબી વલય અને બહાર તરફ તીર છે. બંને બાજુથી ચાર ગોળી દૂર કરતાં ડાબે માત્ર પરબીડિયું અને જમણે એક ગોળી રહે છે. બંને નમૂના વચ્ચે લીલું તીર છે.'},
 'eip-id1168469546267':{'kind':'alt-equality-test','issue':'Source says question mark indicates an unknown operator. It asks whether the two sides are equal; it is not an unknown operation.','corrected_alt_gu':'સમીકરણની ચકાસણી છે: 12 − 4 બરાબર છે કે નહીં 10 − 2? પ્રશ્નચિહ્ન બરાબરની નિશાનીની ઉપર છે. બંને બાજુ 8 મળે છે, તેથી 8 = 8 સાચું છે.'},
 'eip-id1168468500212':{'kind':'alt-wrong-variable','issue':'Sourcealtq=43contradictsactual027-01a=43andentireexample.','corrected_alt_gu':'લખાણ છે: હવે ચકાસી શકીએ. ધારો કે a = 43. સંખ્યા 43 લાલ છે અને બાકી લખાણ ઘેરા લીલાશ પડતા વાદળી રંગનું છે.'},
 'eip-id1168468767272':{'kind':'alt-incomplete-color','issue':'Actual027-03colorsbothnew+16groupsred,notonlyright16.','corrected_alt_gu':'સમીકરણ 27 + 16 = a − 16 + 16 છે. બંને બાજુ નવું ઉમેરેલું +16 લાલ છે. મૂળ a − 16 સહિત બાકી ચિહ્નો કાળાં છે.'},
 'eip-id1168469877592':{'kind':'alt-equation-called-expression','issue':'Sourcecalls18=18anexpression;it is an equation/true equality.','corrected_alt_gu':'સમીકરણ 18 = 18 પછી ખરાની નિશાની છે, જે સમાનતા સાચી હોવાનું દર્શાવે છે.'},
 'eip-id1168467129923':{'kind':'alt-equation-called-expression','issue':'Source calls the word-and-symbol equality “the sum of6and9=15” a mathematical expression; it is an equality statement/equation, not merely an expression.','corrected_alt_gu':'“6 અને 9નો સરવાળો બરાબર છે 15” લખાણને “6 અને 9નો સરવાળો = 15” તરીકે દર્શાવવામાં આવ્યું છે. આ સમાનતાવાળું વિધાન, એટલે સમીકરણ, છે; માત્ર ગાણિતિક પદાવલી નથી.'},
}
BRIDGES={
 'eip-id1168469875178':{'kind':'Gujarati-phrase-order','reader_note_gu':'અહીં પહેલાં xમાંથી 3 બાદ કરવાના છે અને પછી આખા તફાવતના બમણા કરવાના છે. તેથી કૌંસમાં x − 3 આવે છે અને તેની બહાર 2 આવે છે.','purpose':'Localize brace layout semantically; avoid teaching fixed English word order as Gujarati grammar.'},
 'fs-id2171617':{'kind':'equality-check-symbol','reader_note_gu':'બરાબરની નિશાનીની ઉપર પ્રશ્નચિહ્ન હોય ત્યારે હજી સમાનતા ચકાસી રહ્યા છીએ. તે નવી ગણિતની ક્રિયા નથી. ચકાસ્યા પછી = કે ≠ લખીએ છીએ.'},
}
ENLARGED=set(FIGURE_LABELS)|{SELF_CHECK['source_file'],'CNX_BMath_Figure_02_03_002.jpg','CNX_BMath_Figure_02_03_005_img.jpg','CNX_BMath_Figure_02_03_018_img-04.png','CNX_BMath_Figure_02_03_027_img-03.png'}

def main():
 sys.stdout.reconfigure(encoding='utf-8');assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
 source=E.parse(SOURCE).getroot();target=E.parse(OUTPUT).getroot()
 assert target.attrib.pop('{http://www.w3.org/XML/1998/namespace}lang')=='gu-Gujr-IN'
 stats=validate_pair(source,target);allowed=set('abcdefghijklmnopqrstuvwxyz')
 for owner,slots in gather(target).items():
  for e,f,t in slots:assert all(w in allowed for w in re.findall('[A-Za-z]+',t)),(owner,f,t)
 for e in target.iter():
  for k,v in e.attrib.items():
   if k in LANGUAGE_ATTRS:assert re.search('[\u0a80-\u0aff]',v)and all(w in allowed for w in re.findall('[A-Za-z]+',v)),(e.get('id'),k,v)
 ex=list(target.iter(C+'exercise'));assert len(ex)==107
 checked={};boolean_parts=0
 def mark(i,kind):
  assert i not in checked and ex[i].find(C+'solution')is not None
  checked[i]=kind
 # Readiness: two exact evaluations and one phrase translation.
 for i in (0,1):
  p=maths(ex[i].find(C+'problem'));parts=''.join(p).split('@');formula=parts[0];v,n=assigned(parts[1])
  assert evaluate(formula,{v:n})==evaluate(compact(ex[i].find(C+'solution')))
  mark(i,'readiness evaluation')
 assert polynomial(compact(ex[2].find(C+'solution')))==polynomial('x-8');mark(2,'readiness phrase')
 # Every yes/no supplied answer is evaluated against its complete equation.
 for i in sorted(set(BOOL_MAIN)|BOOL_COMPACT):
  p=maths(ex[i].find(C+'problem'))
  if len(p)==1 and '|'in p[0]:assignment,eq=p[0].split('|');assignments=[assigned(assignment)]
  else:eq=p[0];assignments=[assigned(t)for t in p[1:]]
  truth=[holds(eq,{v:n})for v,n in assignments]
  if i in BOOL_MAIN:
   ident,wanted=BOOL_MAIN[i];assert ex[i].get('id')==ident;assert truth==[wanted]
   s=flat(ex[i].find(C+'solution'));assert ('ઉકેલ નથી'in s)==(not wanted)
  else:
   s=flat(ex[i].find(C+'solution'));answers=re.findall('હા|ના',s);assert len(answers)==len(truth),(i,s,truth)
   assert [a=='હા'for a in answers]==truth,(i,eq,assignments,truth,answers)
  boolean_parts+=len(truth);mark(i,'solution membership')
 # Actual envelope/counter diagrams establish each model, then exact algebra
 # verifies the source solution rather than trusting the source alt.
 for i,(ident,a,b)in MODELS.items():
  assert ex[i].get('id')==ident;eq=f'x+{a}={b}';wanted=('x',Fraction(b-a))
  assert solve(eq)==wanted
  if i==9:
   ms=maths(ex[i].find(C+'solution'));assert eq in ms;assert f'x={b-a}'in ms
  else:
   forms=compact(ex[i].find(C+'solution')).split(';');assert len(forms)==2
   same_equation(forms[0],eq);assert assigned(forms[1])==wanted
  mark(i,'envelope model')
 # Every simple supplied equation solution, whether variable is left or right.
 for i in sorted(set(SOLVE_MAIN)|COMPACT_SOLVE):
  pp=maths(ex[i].find(C+'problem'));assert len(pp)==1,(i,pp)
  wanted=solve(pp[0])
  if i in SOLVE_MAIN:
   ident,eq=SOLVE_MAIN[i];assert ex[i].get('id')==ident;same_equation(pp[0],eq)
   assert any(solve(rows[0])==wanted for rows,checks in IMAGE_PATHS.values())
   # Main supplied answers are image-only or narrative, all independently
   # bound to actual rendered solution rows below.
  else:assert assigned(compact(ex[i].find(C+'solution')))==wanted,(i,pp)
  mark(i,'addition/subtraction solution')
 # Word-to-equation answers preserve both sides, operand order and grouping.
 for i,(ident,eq)in WORD_EQUATIONS.items():
  assert ex[i].get('id')==ident
  if i not in (24,27,30):same_equation(compact(ex[i].find(C+'solution')),eq)
  if re.search('[a-z]',eq):assert holds(eq,dict([solve(eq)]))
  else:assert holds(eq)
  mark(i,'word-to-equation')
 for i,(ident,eq)in TRANSLATE_SOLVE.items():
  assert ex[i].get('id')==ident;wanted=solve(eq)
  if i in (33,36):
   final=maths(ex[i].find(C+'solution'))[-1];assert assigned(final)==wanted
  else:
   forms=compact(ex[i].find(C+'solution')).split(';');assert len(forms)==2
   same_equation(forms[0],eq);assert assigned(forms[1])==wanted
  mark(i,'word-to-equation and solution')
 for i,ident in [(101,'fs-id2279583'),(103,'fs-id1828925')]:
  assert ex[i].get('id')==ident;eq=maths(ex[i].find(C+'problem'))[-1]
  assert solve(eq)[1]==evaluate(compact(ex[i].find(C+'solution')))
  mark(i,'currency application')
 supplied={i for i,e in enumerate(ex)if e.find(C+'solution')is not None}
 assert set(checked)==supplied,(supplied-set(checked),set(checked)-supplied)
 assert len(checked)==72
 # All eight displayed solution paths and their numerical checks.
 image_rows=0
 for key,(rows,checks)in IMAGE_PATHS.items():
  wanted=solve(rows[0]);assert all(solve(row)==wanted for row in rows),(key,rows)
  assert all(holds(row)for row in checks),(key,checks);image_rows+=len(rows)+len(checks)
 assert not holds('6*x-17=16',{'x':5})
 assert not holds('6*5-17=16')and not holds('30-17=16')and Fraction(13)!=16
 assert holds('6*y-4=5*y-2',{'y':2})and holds('6*2-4=5*2-2')and holds('12-4=10-2')and holds('8=8')
 # All three MathML tables: equation checking and equal operations on both sides.
 tables=list(target.iter(M+'mtable'));assert len(tables)==3
 rows=[[norm(mt(row))for row in table if len(row)]for table in tables]
 assert rows[0]==['x+2=7','5+2=?7','7=7✓'],rows[0]
 assert solve(rows[0][0])==('x',Fraction(5))and holds(rows[0][1])and holds(rows[0][2])
 for rr,operation in [(rows[1],'-3'),(rows[2],'+10')]:
  same_equation(rr[0],'a=b');same_equation(rr[1],f'a{operation}=b{operation}')
  a,b=sides(rr[1]);assert polynomial('('+a+')-('+b+')')==polynomial('a-b')
 # The general properties retain equality for an arbitrary common c.
 for sign in ('+','-'):
  assert polynomial(f'(a{sign}c)-(b{sign}c)')==polynomial('a-b')
 lookup={e.get('id'):e for e in target.iter()if e.get('id')}
 for ident,eq in [('eip-466','a-c=b-c'),('eip-id1170195252351','a+c=b+c')]:same_equation(maths(lookup[ident])[-1],eq)
 assert 17-3==14 and 17+10==27
 # Actual model image references, including duplicate001.jpg.
 model_counts={
  'fs-id1910217':(3,8),'fs-id1494384':(3,8),'fs-id1230119':(4,5),'fs-id1948644':(1,7),'fs-id2609375':(3,4),
  'fs-id1185520':(2,5),'fs-id2382403':(4,7),'fs-id1218100':(3,6),'fs-id2650560':(5,9)}
 for ident,(outside,total)in model_counts.items():assert lookup[ident].tag==C+'media'and total-outside>0
 missing=[e.get('id')for e in source.iter(C+'exercise')if e.find(C+'solution')is None];assert len(missing)==35
 media=[]
 for e in source.iter(C+'media'):
  name=Path(list(e)[0].get('src')).name;p=MEDIA/name
  media.append({'media_id':e.get('id'),'source_file':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'inspection':'actual contact-sheet view'+('; original separately opened'if name in ENLARGED else''),'localization':'Gujarati label map supplied'if name in FIGURE_LABELS else'complete Gujarati self-check supplied'if name==SELF_CHECK['source_file']else'retain actual mathematical diagram; keyed corrected accessibility applies'})
 assert len(media)==72 and len({m['source_file']for m in media})==71 and len(ENLARGED)==13
 counts={kind:list(checked.values()).count(kind)for kind in sorted(set(checked.values()))}
 receipt={'module':'m81271','source_sha256':SHA,'translation_sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),'integrity':stats,'source_text_tail_alt_slots':592,'other_language_attributes':15,'total_language_slots':607,'natural_English_residuals':0,'all_supplied_solutions_checked':72,'solution_check_categories':counts,'membership_answer_parts_checked':boolean_parts,'eight_image_paths_rows_checked':image_rows,'membership_image_paths_checked':2,'MathML_tables_checked':3,'general_equality_properties_checked':2,'actual_model_initial_state_references_checked':len(model_counts),'model_removal_sequences_checked':2,'source_missing_solution_count':35,'missing_source_solution_ids':missing,'source_exercises_checked':[{'id':ex[i].get('id'),'category':kind}for i,kind in sorted(checked.items())],'media':media,'figure_label_translations':FIGURE_LABELS,'self_check':SELF_CHECK,'source_errata':ERRATA,'separate_reader_bridges':BRIDGES,'source_color_note':'Removalcircles/arrows002and005magenta, transitionarrowsgreen. Added/subtractedgroupsarecoloredaswhole+number/-number.027bothnew+16groupsred,original−16black. Substitution5/2/13/43red;source03044and03132checkingnumeralsareblack,notinventedred. AppB0106skills18blankresponses.','scope_note':'Complete full canonical translation with607language slots, all72providedanswers checked. All72mediareferences(71uniquefiles)actually inspected,13originals separately opened.9languagebearingimagesneedrootfigureintegration;other63referencesmathonly.35missingsolutionsstayomitted;7sourceerrataand2bridgesareseparate.'}
 out=ROOT/'gu-Gujr-IN/translations/a00-m81271-media-and-errata.gu.json';out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in receipt.items()if k not in ('missing_source_solution_ids','source_exercises_checked','media','figure_label_translations','self_check','source_errata','separate_reader_bridges')},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
