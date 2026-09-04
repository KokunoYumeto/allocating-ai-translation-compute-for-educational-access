"""Build the complete like-terms section from frozen source and Punjabi blocks.
Only inspected reusable renderer definitions are executed; no prior build entrypoint.
"""
from pathlib import Path
import ast,copy,html,json,re,hashlib
import xml.etree.ElementTree as ET
B=Path(__file__).resolve().parent
MATH='http://www.w3.org/1998/Math/MathML';MATH_TAG='{'+MATH+'}math'
PARTS={'ⓐ':'a','ⓑ':'b','ⓒ':'c','ⓓ':'d','ⓔ':'e'};LONG_PARTS=set()
STRUCTURAL_CHILDREN={'list','table','media','para','note','figure'}
ET.register_namespace('',MATH)
def require(v,m):
 if not v:raise ValueError(m)
def tag(n):return n.tag.split('}')[-1]
def attr(v):return html.escape(str(v),quote=True)
raw=(B/'renderer_base.py').read_bytes()
require(hashlib.sha256(raw).hexdigest()=='c0413d3701b11c0c503be4ba78e580d93be8cdfd1460a9d180c0c9cb67e233c8','renderer pin')
syntax=ast.parse(raw.decode())
selected=[n for n in syntax.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in {'Reader','compact','inner_xml','fragment_text'}]
selected += [n for n in syntax.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='LOCAL_CSS' for t in n.targets)]
exec(compile(ast.Module(body=selected,type_ignores=[]),'renderer_base.py','exec'),globals())
class SectionReader(Reader):
 RESPONSIVE_FIGURES={
  'fs-id1170655224688':'''<div class="figure-reflow" data-origin="original-responsive-reconstruction" role="group" aria-label="قدم 1 دی پڑھ سکّن جوگی جوابی ترتیب"><p class="figure-step">قدم 1۔ ہم جنس اجزا پہچانو۔</p><p class="responsive-expression" dir="ltr"><span class="group-a">2x²</span> + <span class="group-b">3x</span> + <span class="group-c">7</span> + <span class="group-a">x²</span> + <span class="group-b">4x</span> + <span class="group-c">5</span></p><p class="figure-groups"><bdi class="group-a" dir="ltr">2x², x²</bdi> اک گروہ؛ <bdi class="group-b" dir="ltr">3x, 4x</bdi> دوجا؛ تے <bdi class="group-c" dir="ltr">7, 5</bdi> تِیجا گروہ اے۔</p></div>''',
  'fs-id1170653192952':'''<div class="figure-reflow" data-origin="original-responsive-reconstruction" role="group" aria-label="قدم 2 دی پڑھ سکّن جوگی ترتیب"><p class="figure-step">قدم 2۔ عبارت دی ترتیب بدلو، تاں جو ہم جنس اجزا اکٹھے ہو جان۔</p><p class="responsive-expression" dir="ltr"><span class="group-a">2x² + x²</span> + <span class="group-b">3x + 4x</span> + <span class="group-c">7 + 5</span></p></div>''',
  'fs-id1170655041754':'''<div class="figure-reflow" data-origin="original-responsive-reconstruction" role="group" aria-label="قدم 3 دا پڑھ سکّن جوگا حاصل"><p class="figure-step">قدم 3۔ ہم جنس اجزا اکٹھے کرو۔</p><p class="responsive-expression" dir="ltr"><span class="group-a">3x²</span> + <span class="group-b">7x</span> + <span class="group-c">12</span></p></div>'''
 }
 def render(self,node,parent=None,index=0):
  if tag(node)=='list' and node.get('class')=='circled':
   require(node.get('list-type')=='enumerated' and node.get('number-style')=='arabic','circled list semantics')
   return '<ol'+self.binding(node)+' class="source-circled-list" role="list">'+self.children(node)+'</ol>'
  return super().render(node,parent,index)
 def media(self,node):
  # Reader originally lives one directory down; this packet index is at root.
  rendered=super().media(node).replace('src="../assets/','src="assets/').replace('href="../assets/','href="assets/')
  rendered=rendered.replace('aria-label="اصل تصویر؛ لوڑ پئے تے پاسے سرکاؤ"','aria-label="اصل تصویر؛ پوری چوڑائی سکرین وچ فٹ اے"')
  rendered=rendered.replace('چھوٹی سکرین اُتے پوری تصویر ویکھن لئی پاسے سرکاؤ، یا ','اصل تصویر پوری سکرین وچ فٹ اے۔ نال دِتّی پڑھ سکّن جوگی ترتیب وی ویکھو، یا ')
  reflow=self.RESPONSIVE_FIGURES.get(node.get('id'))
  require(reflow is not None,'missing responsive figure reconstruction')
  return rendered.replace('<p class="scroll-hint"',reflow+'<p class="scroll-hint"',1)
plan=json.loads((B/'source/SELECTION.json').read_bytes());tr=json.loads((B/'translation.json').read_bytes())
source=ET.parse(B/'source/a10-unit-009.cnxml').getroot()
for im in plan['images']:im['source_alt_override']=tr['image_alt_overrides'].get(im['media_id']+'/alt')
r=SectionReader(plan,source,tr)
r.link_labels={'fs-id1170655174214/link/0':'پچھلی حل کیتی مثال'}
body=r.render(source)
require(r.used==list(tr['source_blocks']) and len(r.used)==66,'complete ordered source-block coverage')
mapped={n for n in source.iter() if not n.tag.startswith('{'+MATH+'}') or n.tag==MATH_TAG}
require(r.bound==mapped,'every source binding')
require(len([n for n in r.bound if n.tag==MATH_TAG])==62,'exact source math count')
require(not re.search(r'\{\{[^}]+\}\}',body),'unresolved placeholder')
guide=(B/'guidance.html').read_text(encoding='utf-8')
css=(B/'reader.css').read_text(encoding='utf-8')+LOCAL_CSS+'''
.source-circled-list{list-style:none;padding-inline-start:1rem}.source-process-list{padding-inline-start:1.8rem}
.source-equation{max-width:100%} .source-equation .math-isolate{overflow:visible}
.reader-note{border-inline-start:4px solid #b98238;padding:.7rem 1rem;background:#f8f3e8}
dt{font-weight:bold}dd{margin-inline-start:1rem}code{direction:ltr;unicode-bidi:isolate;font-size:.8em}
.a10-007-reader .source-media .figure-scroll{overflow-x:hidden}
.a10-007-reader .source-media img{width:min(100%,var(--source-width));min-width:0;max-width:var(--source-width)}
.figure-reflow{display:none;border:1px solid #8cb4a3;border-radius:6px;background:#f8fbf9;padding:.75rem 1rem;margin-block:.75rem}
.figure-reflow p{margin:.25rem 0}.figure-step{font-weight:700}.responsive-expression{direction:ltr;unicode-bidi:isolate;font-family:"Cambria Math",Cambria,"Segoe UI",serif;font-size:1.12em;line-height:1.7;overflow-wrap:anywhere;text-align:left}
.figure-groups{font-size:.92em}.group-a{color:#9b1c1c}.group-b{color:#006f78}.group-c{color:#4f7700}
@media(max-width:600px){body{font-size:19px}header,main,footer{padding:1rem 1.1rem}h1{font-size:1.8rem}.figure-reflow{display:block}.scroll-hint{font-size:.82rem}}
'''
page='''<!doctype html><html lang="pnb-Arab-PK" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ہم جنس اجزا پہچانو تے اکٹھے کرو</title><style>'''+css+'''</style></head><body class="a10-reader a10-007-reader"><header><p><bdi lang="en" dir="ltr">Elementary Algebra 2e · A10-009 · m82453</bdi></p><h1>ہم جنس اجزا پہچانو تے اکٹھے کرو</h1><p>پنجابی · شاہ مکھی</p><nav><a href="#fs-id1170655163482">اصل سبق دا ترجمہ</a> · <a href="#learning-key">ساڈی وکھری رہنمائی</a> · <a href="#word-key">لفظاں دا پُل</a> · <a href="#credits">ماخذ تے حق</a></nav><p class="reader-note">ایہہ ماخذ دا اک پورا سیکشن اے، پوری کتاب نہیں۔ سارے اصل سوال تے دِتّے حل شامل نیں۔ ساڈیاں وضاحتاں وکھریاں نشان لائیاں نیں۔</p></header><main>'''+body+guide+'''<p class="reader-note">اگلا ماخذی سیکشن: انگریزی فقرے نوں جبری عبارت وچ بدلو — <bdi lang="en" dir="ltr">fs-id1170654942537</bdi>۔</p></main><footer id="credits" lang="en" dir="ltr"><h2>Source, credits and bounded coverage</h2><p>Adapted from OpenStax Elementary Algebra 2e, module m82453, complete section “Identify and Combine Like Terms.” Original senior contributing authors: Lynn Marecek; MaryAnne Anthony-Smith; Andrea Honeycutt Mathis. Publisher: OpenStax/Rice University. Punjabi adaptation and original explanatory notes produced with OpenAI Codex assistance; no endorsement is implied.</p><p><a href="LICENSE.txt">CC BY-NC-SA 4.0</a>, subject to inherited component-specific notices. <a href="provenance/A10-notice.txt">Inherited A10 notice</a>. All three original JPEGs remain byte-identical and unmirrored; source descriptions and the distinct accessibility correction are traceable. Four worked examples and eight Try It exercises have twelve source-supplied solutions. New guidance is separately credited and not a source answer.</p><p>This packet supplies a complete selected-section source map and offline reader. It does not claim a translated CNXML target or modular-backend completion.</p><p>The official source is pinned at commit 38cae454e644abf9f0a623e876994553881597c9. <a href="source/a10-unit-009.cnxml">Exact section</a> · <a href="source/m82453.en.cnxml">Canonical module</a> · <a href="LANGUAGE_NOTES.md">Language evidence and limits</a> · <a href="EXPERT_REVIEW_LOG.json">Terminology and difficult-passage ledger</a> · <a href="PACKAGE.json">Coverage and next anchor</a> · <a href="QA.json">QA</a>. The full-language A10 goal remains the entire 82-module book plus actual closure and learner workflow, not merely this section.</p></footer></body></html>'''
(B/'index.html').write_text(page,encoding='utf-8',newline='\n')
print(json.dumps({'blocks':len(r.used),'source_bindings':len(r.bound),'mathml_trees':62,'index_sha256':hashlib.sha256(page.encode()).hexdigest()}))
