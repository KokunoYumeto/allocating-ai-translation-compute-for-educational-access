"""Independent source/MathML/answer/encoding/offline verification; no network or TeX."""
from pathlib import Path
import collections,copy,hashlib,json,re,subprocess,sys
from urllib.parse import urlsplit,unquote
from lxml import etree as E,html as H
from PIL import Image
from jsonschema import validate as validate_json_schema
from sympy import Symbol,expand,simplify,Poly
from sympy.parsing.sympy_parser import parse_expr,standard_transformations,implicit_multiplication_application
B=Path(__file__).resolve().parent
M='http://www.w3.org/1998/Math/MathML';C='http://cnx.rice.edu/cnxml'
tests=[]
def ck(v,label):
 if not v:raise AssertionError(label)
 tests.append(label)
def sha(v):return hashlib.sha256(v).hexdigest()
def tag(n):return E.QName(n).localname
def fp(n,math=False):
 attrs=dict(n.attrib)
 if math and tag(n)=='math':attrs.pop('dir',None);attrs.pop('xmlns',None)
 return tag(n),attrs,n.text or '',tuple((fp(c,math),c.tail or '') for c in n)
def paths(root):
 out={}
 def walk(n,p):
  out[p]=n
  for i,c in enumerate(n):walk(c,p+'/'+str(i))
 walk(root,'document');return out
plan=json.loads((B/'source/SELECTION.json').read_bytes());tr=json.loads((B/'translation.json').read_bytes())
pkg=json.loads((B/'PACKAGE.json').read_bytes());raw=(B/'source/m82453.en.cnxml').read_bytes()
ck(sha(raw)==plan['source_sha256']==pkg['source']['module_sha256'],'canonical module hash')
ck(len(raw)==184248,'canonical module bytes')
section_raw=raw[89018:108818]
ck(sha(section_raw)==plan['byte_range']['sha256']==pkg['source']['raw_section_sha256'],'exact raw section boundary/hash')
whole=E.fromstring(raw);doc=E.parse(str(B/'source/a10-unit-009.cnxml')).getroot()
section=whole.xpath('//*[@id="fs-id1170655163482"]')[0]
ck(fp(section)==fp(doc[0]),'complete canonical subtree content/attributes/order')
ck(section.getnext().get('id')=='fs-id1170654942537','next source sibling')
ck(tag(doc[0][-1][-1][-1])=='item' and len(doc[0][-1][-1])==3,'coverage includes last anonymous how-to item')
ck(sha((B/'source/a10-unit-009.cnxml').read_bytes())==plan['excerpt_sha256'],'exact wrapped source pin')
collection=(B/'source/collection.xml').read_bytes()
ck(sha(collection)==pkg['source']['collection_sha256'],'collection pin')
modules=E.fromstring(collection).xpath('//*[local-name()="module"]/@document')
ck(len(modules)==82 and modules.count('m82453')==1,'82 source collection entries; selected module membership')
source=paths(doc)
expected={p:n for p,n in source.items() if E.QName(n).namespace!=M or tag(n)=='math'}
english_blocks=json.loads((B/'source/ENGLISH_BLOCKS.json').read_bytes())
ck(list(english_blocks)==list(plan['source_keys_to_paths']),'English source-block keys exact order')
def source_template(node):
 out=node.text or '';math_index=child_index=link_index=0
 for child in node:
  name=tag(child)
  if child.tag=='{'+M+'}math':out+='{{math:'+str(math_index)+'}}';math_index+=1
  elif name=='link':out+='{{link:'+str(link_index)+'}}';link_index+=1
  elif name in {'table','list','media','para','note','figure'}:out+='{{child:'+str(child_index)+'}}';child_index+=1
  elif name=='emphasis':
   html_tag='strong' if child.get('effect')=='bold' else 'em';out+='<'+html_tag+'>'+source_template(child)+'</'+html_tag+'>'
  elif name=='term':out+="<span id='"+child.get('id')+"' class='source-term'>"+source_template(child)+'</span>'
  elif name=='newline':out+='<br />'
  elif name=='span':out+="<bdi dir='ltr'>("+'abcde'['ⓐⓑⓒⓓⓔ'.index(child.text)]+')</bdi>'
  else:raise AssertionError('unsupported source template child '+name)
  out+=child.tail or ''
 return out
for key,path in plan['source_keys_to_paths'].items():
 node=source[path]
 expected_english=node.get('alt') if tag(node)=='media' else source_template(node)
 ck(english_blocks[key]==expected_english,'English source block exact at '+path)
def verify_html(data):
 h=H.fromstring(data);bound=h.xpath('//*[@data-source-path]')
 ck(len(bound)==253==len(expected),'all source node bindings, no extras')
 bm={n.get('data-source-path'):n for n in bound}
 ck(len(bm)==len(bound) and set(bm)==set(expected),'unique exact source paths')
 for p,n in expected.items():
  o=bm[p]
  ck(o.get('data-source-qname')==n.tag and o.get('data-source-tag')==tag(n) and json.loads(o.get('data-source-attributes'))==dict(n.attrib),'binding attributes '+p)
  ck(o.get('id')==n.get('id'),'binding ID '+p)
  if p!='document':
   ancestor=next((x for x in o.iterancestors() if x.get('data-source-path')),None)
   ck(ancestor is not None and ancestor.get('data-source-path')==p.rsplit('/',1)[0],'source hierarchy '+p)
  if tag(n)=='math':
   ck(len(o)==1 and tag(o[0])=='math' and fp(n,True)==fp(o[0],True),'exact MathML tree '+p)
   ck(o.get('dir')==o[0].get('dir')=='ltr','isolated source MathML '+p)
  if tag(n)=='emphasis':
   ck(tag(o)==('strong' if n.get('effect')=='bold' else 'em'),'source emphasis semantics '+p)
   if n.get('effect')=='italics':ck(''.join(o.itertext())==''.join(n.itertext()),'exact italic variable '+p)
  if tag(n)=='span':
   ck(''.join(o.itertext())=='('+'abcde'['ⓐⓑⓒⓓⓔ'.index(n.text)]+')' and o.get('dir')=='ltr','part token order/letter '+p)
  if tag(n)=='newline':ck(tag(o)=='br','source line break '+p)
  if tag(n) in {'section','note','example','exercise','problem','solution','list'}:
   children=[x.get('data-source-path') for x in o.xpath('.//*[@data-source-path]') if next((a for a in x.iterancestors() if a.get('data-source-path')),None) is o]
   ck(children==[p+'/'+str(i) for i,c in enumerate(n)],'structural child order '+p)
 ids=h.xpath('//*[@id]/@id')
 ck(len(ids)==len(set(ids)),'all output IDs unique')
 ck([n.get('id') for n in bound if n.get('id') and n.get('id')!='a10-unit-009-excerpt']==plan['source_ids'],'all 108 section source IDs in order')
 ck(h.xpath('//*[@data-source-key]/@data-source-key')==list(tr['source_blocks'])==list(plan['source_keys_to_paths']),'66 translated block keys exact order')
 ck(h.get('lang')=='pnb-Arab-PK' and h.get('dir')=='rtl','Punjabi Shahmukhi language/direction')
 ck(not h.xpath('//script|//iframe|//object|//embed|//link'),'no remote or executable reader dependencies')
 ck(not re.search(r'\{\{[^}]+\}\}',data.decode()),'no unresolved placeholders')
 for attr in ('href','src'):
  for v in h.xpath('//@'+attr):
   u=urlsplit(v)
   if u.scheme in ('https','http'):ck(attr=='href','external URL is optional citation only');continue
   ck(not u.scheme and not u.netloc,'no unexpected URL scheme')
   target=(B/unquote(u.path)).resolve() if u.path else B/'index.html'
   generated_here=target==B/'QA.json'
   ck(target.is_relative_to(B) and (target.is_file() or generated_here),'offline link exists '+v)
   if u.fragment and target==B/'index.html':ck(unquote(u.fragment) in ids,'offline fragment exists '+v)
 for v in h.xpath('//@aria-describedby'):
  ck(all(x in ids for x in v.split()),'accessible description targets '+v)
 for ex in plan['exercises']:
  node=h.get_element_by_id(ex['id']);sol=node.xpath('.//*[@id="'+ex['solution_id']+'"]')
  ck(len(sol)==1 and sol[0].get('data-source-tag')=='solution','supplied solution association '+ex['id'])
 for spec in plan['images']:
  o=h.get_element_by_id(spec['media_id']).xpath('.//img')[0];key=spec['media_id']+'/alt'
  ck(o.get('src')==spec['path'] and int(o.get('width'))==spec['width'] and int(o.get('height'))==spec['height'],'source image association/geometry '+key)
  ck(o.get('data-source-alt')==tr['source_blocks'][key],'faithful source alt retained '+key)
  alt=tr['image_alt_overrides'].get(key,{}).get('alt',tr['source_blocks'][key])
  ck(o.get('alt')==alt and o.get('data-description-origin')==('original-correction' if key in tr['image_alt_overrides'] else 'source-translation'),'explicit description origin '+key)
 ck(h.get_element_by_id('learning-key').get('data-origin')=='original-translator-guidance','guidance distinctly credited')
 ck(h.get_element_by_id('fs-id1170655171250').get('data-origin')=='original-cross-reference-context','prior cross-reference contextual bridge distinct from source')
 return h
htmlraw=(B/'index.html').read_bytes();h=verify_html(htmlraw)
for spec in plan['images']:
 f=B/spec['path'];b=f.read_bytes()
 ck(sha(b)==spec['sha256'] and len(b)==spec['bytes'],'canonical media bytes '+f.name)
 with Image.open(f) as im:ck(im.size==(spec['width'],spec['height']) and im.format=='JPEG','decoded source image geometry '+f.name)
for f in [B/'index.html',B/'translation.json',B/'guidance.html',B/'LANGUAGE_NOTES.md']:
 s=f.read_bytes().decode('utf-8','strict')
 ck(not re.search('[\u0a00-\u0a7f\ufffd\u202a-\u202e\u2066-\u2069]',s),'UTF-8/no Gurmukhi/replacement/hidden bidi '+f.name)
ck(len(h.xpath('//*[@lang="ur-Arab-PK"]'))==3,'three explicitly tagged Urdu bridges')
punjabi=' '.join(tr['source_blocks'].values())+' '+(B/'guidance.html').read_text(encoding='utf-8')
for marker in ['نیں','تے','اوہناں','کیوں جے','چیتے رکھو','ضریباں نوں','اک عبارت بن دی اے']:
 ck(marker in punjabi,'native Shahmukhi Punjabi marker '+marker)
ck('عبارت بندی اے' not in punjabi,'rejected fused predicate absent')
ck('جِنہاں وچ اوہی متغیر اوہناں ای طاقتاں اُتے ہون' in tr['source_blocks']['fs-id1170654936541'],'plural same-variable/same-power definition')
review_schema=json.loads((B/'provenance/EXPERT_REVIEW_LOG_SCHEMA.json').read_bytes())
review=json.loads((B/'EXPERT_REVIEW_LOG.json').read_bytes())
validate_json_schema(review,review_schema)
ck(review['locale']=='pnb-Arab-PK' and review['coverage_status']=='complete','complete locale expert-review ledger')
ck(len(review['entries'])==14 and len({e['decision_id'] for e in review['entries']})==14,'fourteen unique substantive review decisions')
timings={e['decision_id']:e['rationale_timing'] for e in review['entries']}
ck(timings['pnb-a10-009-responsive-figure-reflow']=='contemporaneous' and sum(v=='retrospective_reconstruction' for v in timings.values())==13,'retrospective backfills and contemporaneous reflow decision labeled honestly')
ck(all(e['authorities_checked'] and e['source_location'] and e['target_location'] and e['review_question'] for e in review['entries']),'review entries have precise loci, authorities and questions')
ck(any(e['provisional'] for e in review['entries']) and any(not e['provisional'] for e in review['entries']),'provisional terminology distinguished from settled structural decisions')
ck(sha((B/'provenance/EXPERT_REVIEW_LOG_SCHEMA.json').read_bytes())=='4269beadddf14ad56382b90045c0914be785013d898408e53275cc4856a83568','expert-review schema exact authority copy')
# These responsive panels are explicitly original layout/accessibility
# adaptations, not source bindings. Check their full mathematical meaning so a
# visually present but numerically wrong reconstruction cannot pass.
reflows=h.xpath('//*[@data-origin="original-responsive-reconstruction"]')
ck(len(reflows)==3,'three explicitly original responsive figure reconstructions')
reflow_by_media={next(x for x in n.iterancestors() if x.get('data-source-tag')=='media').get('id'):n for n in reflows}
ck(set(reflow_by_media)=={'fs-id1170655224688','fs-id1170653192952','fs-id1170655041754'},'responsive reconstructions bound to exact source media')
expected_reflow_expressions={
 'fs-id1170655224688':'2x² + 3x + 7 + x² + 4x + 5',
 'fs-id1170653192952':'2x² + x² + 3x + 4x + 7 + 5',
 'fs-id1170655041754':'3x² + 7x + 12',
}
for media_id,expected_expression in expected_reflow_expressions.items():
 node=reflow_by_media[media_id]
 expressions=node.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," responsive-expression ")]')
 ck(len(expressions)==1 and ' '.join(''.join(expressions[0].itertext()).split())==expected_expression,'exact responsive expression '+media_id)
 ck(expressions[0].get('dir')=='ltr','responsive expression LTR '+media_id)
ck([' '.join(''.join(n.itertext()).split()) for n in reflow_by_media['fs-id1170655224688'].xpath('.//bdi')]==['2x², x²','3x, 4x','7, 5'],'responsive like-term groups exact and ordered')
ck(any(e['decision_id']=='pnb-a10-009-responsive-figure-reflow' for e in review['entries']),'responsive figure decision in expert-review ledger')
# Symbolic checks use actual rendered source MathML where present, with exact
# source plain-text witnesses checked independently above and below.
def mt(n):
 t=tag(n)
 if t=='msup':return '('+mt(n[0])+')**('+mt(n[1])+')'
 if t in {'mi','mn','mo'}:return n.text or ''
 if t=='mspace':return ' '
 return ''.join(mt(c) for c in n)
def math_strings(sid):return [mt(n).strip('.,; ') for n in h.get_element_by_id(sid).xpath('.//math')]
def parse(s):return parse_expr(s.replace('·','*'),transformations=standard_transformations+(implicit_multiplication_application,),evaluate=False)
def eq(a,b,label):ck(simplify(parse(a)-parse(b))==0,label)
coefficient_cases=[('fs-id1170655199112',['14*y','15*x**2','a'],[14,15,1]),('fs-id1170654942256',['17*x','41*b**2','z'],[17,41,1]),('fs-id1170654941720',['9*p','13*a**3','y**3'],[9,13,1])]
for sid,terms,answers in coefficient_cases:
 for term,answer in zip(terms,answers):ck(parse(term).as_coeff_Mul()[0]==answer,'coefficient '+sid+' '+term)
 for actual in math_strings(sid):ck(any(simplify(parse(actual)-parse(t))==0 for t in terms),'actual problem MathML coefficient witness '+sid)
for sid,expected_numbers in [('fs-id1170654943072',['17','41','1']),('fs-id1170654941895',['9','13','1'])]:
 ck(re.findall(r'\d+',''.join(h.get_element_by_id(sid).itertext()))==expected_numbers,'actual source plain-text coefficient answers '+sid)
ck(re.findall(r'\d+',re.sub(r'\{\{math:\d+\}\}','',tr['source_blocks']['fs-id1166425225066']))==['14','14','15','1'],'worked coefficient plain-text answers')
for sid,groups,unpaired in [('fs-id1170654936786',[['y**3','4*y**3'],['7*x**2','5*x**2'],['14','23']],['9*x']),('fs-id1170655163428',[['9','15'],['y**2','11*y**2'],['2*x**3','8*x**3']],['9*y']),('fs-id1170654942824',[['19','24'],['8*x**2','3*x**2'],['4*x**3','6*x**3']],[])]:
 signatures=[]
 for group in groups:
  sig=[parse(x).as_coeff_Mul()[1] for x in group]
  ck(len(set(sig))==1,'like-group variables/exponents '+sid+' '+str(group));signatures.append(sig[0])
 ck(len(set(signatures))==len(groups) and all(parse(x).as_coeff_Mul()[1] not in signatures for x in unpaired),'distinct groups/unpaired '+sid)
 terms=sum(groups,[])+unpaired
 for actual in math_strings(sid):ck(any(simplify(parse(actual)-parse(t))==0 for t in terms),'actual source grouping problem witness '+sid)
for sid,expected_answers in [('fs-id1170654936607',['y**2','11*y**2','2*x**3','8*x**3']),('fs-id1170654936398',['8*x**2','3*x**2','4*x**3','6*x**3'])]:
 actual=math_strings(sid);ck(len(actual)==4,'four MathML like-term answers '+sid)
 for a,b in zip(actual,expected_answers):eq(a,b,'actual source grouped answer '+sid)
for problem,solution,expected in [('fs-id1170654944220','fs-id1170654942642',['4*x**2','5*x','17']),('fs-id1170654943822','fs-id1170654940734',['5*x','2*y'])]:
 eq(math_strings(problem)[0],'+'.join(expected),'identified terms reconstruct source expression '+problem)
 actual=math_strings(solution)
 if actual:
  terms=actual[0].split(',');ck(len(terms)==len(expected),'answer term count '+solution)
  for a,b in zip(terms,expected):eq(a,b,'answer term '+solution)
 else:ck(''.join(h.get_element_by_id(solution).itertext()).strip()=='5x, 2y','plain-text term answer')
for sid,expected in [('fs-id1166422654836',['9*x**2+7*x+12','8*x+3*y']),('fs-id1166422254836',['9*x**2+7*x+12','9*x**2','8*x+3*y'])]:
 actual=math_strings(sid);ck(len(actual)==len(expected),'worked term source MathML count '+sid)
 for a,b in zip(actual,expected):eq(a,b,'worked term MathML '+sid)
for problem,answer,expected in [('fs-id1170655165463','fs-id1170654944753','10*x**2+16*x+17'),('fs-id1170655206783','fs-id1170654936363','12*y**2+9*y+7')]:
 eq(math_strings(problem)[0],math_strings(answer)[0],'supplied simplified answer '+answer)
 eq(math_strings(answer)[0],expected,'answer expected coefficient signature '+answer)
eq(math_strings('fs-id1170654941823')[0],'3*x**2+7*x+12','source JPEG solution algebra')
eq('2*x**2+x**2+3*x+4*x+7+5','3*x**2+7*x+12','source diagram reordered/result identity')
eq(math_strings('fs-id1170654943110')[0],'12*x','combine introductory expression')
eq(math_strings('fs-id1170654940628')[0],'12*x','combine repeated introductory expression')
ck(all(simplify(parse(mt(n).strip('.,; ')) - parse('12*x'))==0 for n in h.get_element_by_id('fs-id1170654940806').xpath('.//mtd')),'all three wide expansion rows equal 12x')
eq('2*x**2+x**2','3*x**2','separate original guidance identity')
ck(parse('2*x**2+3*x+8').subs(Symbol('x'),4)==52,'separate prior-context calculation')
# Mutation controls test the actual verifier without touching any live file.
base_count=len(tests);mutations={}
for name,mut in [('coefficient',lambda d:d.replace(b'<mn>17</mn>',b'<mn>18</mn>',1)),('exponent',lambda d:d.replace(b'<mn>2</mn>',b'<mn>3</mn>',1)),('source-id',lambda d:d.replace(b'id="fs-id1170654958637"',b'id="changed-source-id"',1)),('image-path',lambda d:d.replace(b'src="assets/CNX_ElemAlg_Figure_01_02_014a_new.jpg"',b'src="assets/changed.jpg"',1))]:
 damaged=mut(htmlraw);ck(damaged!=htmlraw,'mutation changes witness '+name)
 try:verify_html(damaged)
 except AssertionError:mutations[name]='rejected'
 else:raise AssertionError('mutation accepted '+name)
tests=tests[:base_count]
for n in mutations:ck(mutations[n]=='rejected','negative control '+n)
before=sha(htmlraw)
for run in range(2):
 result=subprocess.run([sys.executable,str(B/'build.py')],capture_output=True,text=True,encoding='utf-8',check=True)
 ck(sha((B/'index.html').read_bytes())==before,'byte-identical rebuild '+str(run+1))
visual_path=B/'visual/RESULTS.json';inspection_path=B/'visual/INSPECTION.json'
visual=json.loads(visual_path.read_bytes()) if visual_path.exists() else None
inspection=json.loads(inspection_path.read_bytes()) if inspection_path.exists() else None
ck(visual is not None and visual['status']=='passed','actual offline browser checks passed')
ck(inspection is not None and inspection['status']=='passed','actual representative screenshot inspection passed')
for item in visual['inputs']:
 ck((B/item['path']).stat().st_size==item['bytes'] and sha((B/item['path']).read_bytes())==item['sha256'],'visual evidence binds final input '+item['path'])
ck(inspection['visual_results_sha256']==sha(visual_path.read_bytes()),'visual inspection binds final browser results')
expected_visual_images={item['path']:(item['bytes'],item['sha256']) for viewport in visual['viewports'].values() for item in viewport['screenshots']}
inspected_visual_images={item['path']:(item['bytes'],item['sha256']) for item in inspection['images']}
ck(inspected_visual_images==expected_visual_images,'inspection covers every saved browser screenshot exactly')
for item in inspection['images']:
 ck((B/item['path']).stat().st_size==item['bytes'] and sha((B/item['path']).read_bytes())==item['sha256'],'inspected screenshot bytes/hash '+item['path'])
ck(len(inspection.get('observations',[]))==10 and all(x.get('status')=='passed' and x.get('image') in expected_visual_images and x.get('observation') for x in inspection['observations']),'ten final-code screenshot observations passed')
qa={'schema':'a10-section-qa-v1','status':'passed','date':'2026-09-04','unit':'A10-009','section':plan['section_id'],'checks_passed':len(tests),'checks':tests,'negative_controls':mutations,'coverage':pkg['coverage'],'reader_sha256':before,'visual_results':'visual/RESULTS.json','visual_inspection':'visual/INSPECTION.json','expert_review_log':'EXPERT_REVIEW_LOG.json','expert_review_entries':len(review['entries']),'evidence_limits':['Institutional paired-script dictionary observations are not Pakistani classroom attestation.','Native Shahmukhi prose loci support grammar, not mathematical compounds.','Book-local compounds remain provisional, with distinct Urdu/English bridges.','No human-review release hold; deterministic operational checks passed.','No actual audio or human recording produced.'],'whole_book_complete':False,'next_anchor':plan['next_anchor']}
(B/'QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ck((B/'QA.json').is_file(),'generated QA local link exists')
print(json.dumps({'checks':len(tests),'reader_sha256':before,'qa_sha256':sha((B/'QA.json').read_bytes())}))
