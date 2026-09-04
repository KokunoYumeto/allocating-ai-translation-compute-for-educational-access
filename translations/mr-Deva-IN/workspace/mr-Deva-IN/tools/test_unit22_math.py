"""MR022 independent real-source/math regression; not reader acceptance.

Reads frozen XML/config/lock, selected module/image ZIP members and local witnesses.
Exact Fraction arithmetic plus a bounded AST polynomial interpreter; never eval.
All 24 source pixels were manually viewed; tests hash-bind, not automate, that review.
"""
import ast
from fractions import Fraction as F
import hashlib,json,re,unicodedata,unittest,zipfile
from pathlib import Path
import xml.etree.ElementTree as E

BASE=Path(__file__).resolve().parents[1]; WORKSPACE=BASE.parent
UNIT="MR-BRIDGE-022"; TOPIC="fs-id1167836628671"
C="{http://cnx.rice.edu/cnxml}"; M="{http://www.w3.org/1998/Math/MathML}"
PINS={
    "translations/MR-BRIDGE-022.xml": [
        44623,
        "ec136afe3b909a855882c2b50dd1a34fb2ecd90aeaf15206326bbd2e9a176b66"
    ],
    "units/MR-BRIDGE-022.json": [
        6669,
        "17d561931c667a68ba00b9644fc9a5ef15e5ab5eb52ffbeca291c925cb7e39ea"
    ],
    "provenance/MR-BRIDGE-022.lock.json": [
        100801,
        "a3f0e9ade78d7e967bc4a47bc29b2a06158e15aa9d600bc2d7ea4ca08553275c"
    ]
}
ARCHIVES={
"en":("A20-canonical.zip","osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9","effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917"),
"id":("A20-v0.3.0-source.zip","source","a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7")}
MODULE_PINS={"en":(247327,"021c29fa9a6ab3d5b06d2ef143a82d2ac818ed25fe6fd44ebf5d7a6be07a123a"),
"id":(247303,"d89a74aef766afca6a4ac7e1ae720f120d22cc771c11dd7e025c55bca1fabb8e")}
NEXT_PINS={"en":(1568,"5577a5087c332c7c6eb5ee185dee43b98e8a754687985410be8b84e4173d53e9"),
"id":(1610,"e1204520eb35f8ade93655696d814c560deded28c18c5d7cfb525b38ffc2df23")}
WINDOWS={397:(-8,8,-8,8,2),250:(-6,6,-6,6,1),251:(-6,6,-6,6,1),
398:(-8,8,-8,8,2),400:(-10,10,-10,10,F(5,2)),402:(-10,10,-10,10,F(5,2)),
252:(-10,10,-10,10,F(5,2)),403:(-10,10,-10,10,F(5,2)),
405:(-8,8,-8,8,2),253:(-8,8,-8,8,2),407:(-8,8,-4,10,2),254:(-8,8,-8,8,2)}
POINTS={397:[(2,5),(-1,-3),(0,2),(-4,F(3,2)),(5,0)],
250:[(-5,2),(0,-1),(5,-4)],251:[(2,0),(2,-1),(2,1)],
398:[(-3,-4),(-1,-3),(1,-2)],400:[(-3,-6),(0,-1),(3,4)],
402:[(-1,2),(0,2),(1,2)],252:[(-3,0),(0,-3),(1,-4)],
403:[(-2,2),(0,5),(2,8)],405:[(-1,5),(0,0),(1,-5)],
253:[(-1,1),(0,2),(1,3)],407:[(-2,5),(-1,2),(0,1),(1,2),(2,5)],
254:[(-2,0),(-1,-3),(0,-4),(1,-3),(2,0)]}
IMAGE_Q={397:1,250:3,251:3,398:5,400:7,402:9,252:14,403:15,405:17,253:22,407:23,254:25}
ORIGINAL_KEYS={"hiro-hours-x","hiro-hours-y","intercepts-x-left","intercepts-x-right","intercept-y","slope-intercept-form"}

def sha(d):return hashlib.sha256(d).hexdigest()
def unique(pairs):
 out={}
 for k,v in pairs:
  if k in out:raise ValueError("duplicate JSON key")
  out[k]=v
 return out
def inside(base,rel):
 p=(base/rel).resolve()
 if base.resolve() not in p.parents:raise ValueError("path escape")
 return p
def text(n):return "".join(n.itertext())
def ids(r):return {e.get("id"):e for e in r.iter() if e.get("id")}
def parents(r):return {c:e for e in r.iter() for c in e}
def nearest(n,p,allowed):
 while n in p:
  n=p[n]
  if n.get("id") in allowed:return n.get("id")
def shape(n):return (n.tag,tuple(sorted(n.attrib.items())),n.text,tuple((shape(c),c.tail) for c in n))
def norm(s):return re.sub(r"\s+","",s.replace("−","-").replace("²","^2"))
def mathml(n):
 tag=n.tag.removeprefix(M)
 if tag in {"mi","mn","mo","mtext"}:
  if len(n):raise ValueError("token children")
  return n.text or ""
 if tag in {"math","mrow"}:return "".join(mathml(c) for c in n)
 if tag=="mfrac" and len(n)==2:return "(("+mathml(n[0])+")/("+mathml(n[1])+"))"
 if tag=="msup" and len(n)==2:
  e=mathml(n[1]);return mathml(n[0])+({"2":"²"}.get(e,"^("+e+")"))
 if tag=="msqrt":return "√("+"".join(mathml(c) for c in n)+")"
 if tag=="mfenced":return n.get("open","(")+n.get("separators",",").join(mathml(c) for c in n)+n.get("close",")")
 raise ValueError("unsupported MathML "+tag)
def compact_source(n):return re.sub(r"\s+","",mathml(n)).rstrip(".?")
def add(a,b):
 out=dict(a)
 for p,c in b.items():out[p]=out.get(p,F(0))+c
 return {p:c for p,c in out.items() if c}
def mul(a,b):
 out={}
 for (ax,ay),ac in a.items():
  for (bx,by),bc in b.items():out[(ax+bx,ay+by)]=out.get((ax+bx,ay+by),F(0))+ac*bc
 return {p:c for p,c in out.items() if c}
def poly(value):
 value=norm(value).replace("^","**")
 toks=re.findall(r"\*\*|\d+|[xyc()+*/-]",value)
 if not value or "".join(toks)!=value:raise ValueError("unsafe polynomial")
 atom=lambda z:z.isdigit() or z in "xyc"
 code=[]
 for z in toks:
  if code and (atom(code[-1]) or code[-1]==")") and (atom(z) or z=="("):code.append("*")
  code.append(z)
 try:tree=ast.parse("".join(code),mode="eval").body
 except SyntaxError as e:raise ValueError("bad expression") from e
 def walk(n):
  if isinstance(n,ast.Constant) and type(n.value)is int:return {(0,0):F(n.value)}
  if isinstance(n,ast.Name) and n.id in {"x","y","c"}:return {(1,0):F(1)} if n.id in {"x","c"} else {(0,1):F(1)}
  if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.UAdd,ast.USub)):return mul({(0,0):F(-1 if isinstance(n.op,ast.USub) else 1)},walk(n.operand))
  if isinstance(n,ast.BinOp):
   a,b=walk(n.left),walk(n.right)
   if isinstance(n.op,ast.Add):return add(a,b)
   if isinstance(n.op,ast.Sub):return add(a,mul({(0,0):F(-1)},b))
   if isinstance(n.op,ast.Mult):return mul(a,b)
   if isinstance(n.op,ast.Div) and set(b)=={(0,0)} and b[(0,0)]:return mul(a,{(0,0):1/b[(0,0)]})
   if isinstance(n.op,ast.Pow) and set(b)=={(0,0)} and b[(0,0)]==2:return mul(a,a)
  raise ValueError("unsupported expression")
 return walk(tree)
def value(p,x,y=0):return sum(c*F(x)**a*F(y)**b for (a,b),c in p.items())
def equation(s):
 left,right=norm(s).split("=");return add(poly(left),mul({(0,0):F(-1)},poly(right)))
def line(s):
 p=equation(s)
 if set(p)-{(1,0),(0,1),(0,0)}:raise ValueError("not linear")
 return p.get((1,0),F(0)),p.get((0,1),F(0)),p.get((0,0),F(0))
def slope(a,b):
 dx=F(b[0])-F(a[0]);dy=F(b[1])-F(a[1])
 if dx==0:raise ZeroDivisionError("vertical line")
 return dy/dx
def intercept_from_point(m,p):return F(p[1])-m*F(p[0])
def inequality(s):
 s=norm(s)
 for op in [">=","<=",">","<"]:
  if op in s:
   left,right=s.split(op);return add(poly(left),mul({(0,0):F(-1)},poly(right))),op
 raise ValueError("no inequality")
def satisfies(rule,p):
 expr,op=rule;z=value(expr,*p)
 return {">":z>0,">=":z>=0,"<":z<0,"<=":z<=0}[op]
def interval(s):
 s=norm(s)
 if s.startswith(("D:","R:")):s=s[2:]
 if not re.fullmatch(r"[\[(].*,.*[\])]?",s):raise ValueError("bad interval")
 lo,hi=s[1:-1].split(",");a=None if lo=="-∞" else F(lo);b=None if hi=="∞" else F(hi)
 lc,hc=s[0]=="[",s[-1]=="]"
 if a is None and lc or b is None and hc:raise ValueError("closed infinity")
 return a,b,lc,hc

class Unit22(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=(BASE/f"translations/{UNIT}.xml").read_bytes();cls.root=E.fromstring(cls.raw)
  cls.target=ids(cls.root);cls.tp=parents(cls.root)
  cls.config=json.loads((BASE/f"units/{UNIT}.json").read_text(encoding="utf-8"),object_pairs_hook=unique)
  cls.lock=json.loads((BASE/f"provenance/{UNIT}.lock.json").read_text(encoding="utf-8"),object_pairs_hook=unique)
  cls.nodes=[n for n in cls.root.iter() if n.get("data-check")];cls.checks={n.get("data-check"):text(n) for n in cls.nodes}
  cls.modules={};cls.roots={};cls.source={};cls.topics={};cls.archimgs={};cls.next={}
  for loc,(archive,prefix,_) in ARCHIVES.items():
   with zipfile.ZipFile(WORKSPACE/"downloads/mr-Deva-IN/releases"/archive) as z:
    d=z.read(prefix+"/modules/m81374/index.cnxml");cls.modules[loc]=d
    root=E.fromstring(d);cls.roots[loc]=root;cls.source[loc]=ids(root);cls.topics[loc]=cls.source[loc][TOPIC]
    cls.next[loc]=z.read(prefix+"/modules/m81375/index.cnxml")
    for n in WINDOWS:
     name=f"CNX_IntAlg_Figure_03_06_{n}_img_new.jpg";cls.archimgs[(n,loc)]=z.read(prefix+"/media/"+name)
  cls.exercises=[e for e in cls.topics["en"] if e.tag==C+"exercise"]
  cls.questions={i:cls.target[e.get("id")] for i,e in enumerate(cls.exercises,1)}
  cls.images={int(n.get("src").split("_")[5]):n for n in cls.root.iter("img")}
 def test_01_frozen_input_pins(self):
  for p,e in PINS.items():
   d=(BASE/p).read_bytes();self.assertEqual([len(d),sha(d)],e)
 def test_02_actual_modules_metadata_and_next_boundary(self):
  for loc in ARCHIVES:
   self.assertEqual((len(self.modules[loc]),sha(self.modules[loc])),MODULE_PINS[loc])
   root=E.fromstring(self.modules[loc]);topic=ids(root)[TOPIC]
   content=next(e for e in root.iter() if topic in list(e))
   self.assertEqual(list(content)[-1].get("id"),TOPIC)
   self.assertEqual((len(self.next[loc]),sha(self.next[loc])),NEXT_PINS[loc])
   nxt=E.fromstring(self.next[loc]);self.assertEqual(nxt.find(C+"metadata/{http://cnx.rice.edu/mdml}content-id").text,"m81375")
   self.assertEqual(nxt.find(C+"title").text,"Introduction" if loc=="en" else "Pendahuluan")
   first=nxt.find(C+"content")[0];self.assertEqual(first.get("id"),"CNX_IntAlg_Figure_04_00_001")
   self.assertEqual(nxt.find(C+"content")[1].get("id"),"fs-id1167836596342")
 def test_03_exact_ordered_30_selectors(self):
  expected=["A20:m81374#"+e.get("id") for e in list(self.topics["en"])[1:]]
  actual=[e.get("data-source") for e in self.root.iter() if e.get("data-source")]
  self.assertEqual(len(expected),30);self.assertEqual(actual,expected)
  self.assertEqual([r["locator"] for r in self.lock["source_selections"]],expected)
  self.assertEqual([e.get("id") for e in self.topics["id"]],[e.get("id") for e in self.topics["en"]])
 def test_04_all_60_fragments_exact_sources_math_hashes(self):
  count=total=0
  for s in self.lock["source_selections"]:
   for r in s["sources"]:
    data=inside(BASE,r["fragment_path"]).read_bytes();source=self.source[r["locale"]][s["target_id"]]
    self.assertEqual((sha(data),shape(E.fromstring(data))),(r["fragment_sha256"],shape(source)))
    self.assertEqual(r["math_sha256"],[sha(E.tostring(m,encoding="utf-8")) for m in source.iter(M+"math")])
    self.assertEqual(r["module_sha256"],MODULE_PINS[r["locale"]][1]);self.assertEqual(r["archive_sha256"],ARCHIVES[r["locale"]][2])
    count+=1;total+=len(data)
  self.assertEqual((count,total),(60,57808))
 def test_05_all_81_local_witnesses(self):
  self.assertEqual(len(self.lock["witnesses"]),81)
  self.assertEqual(len({r["path"] for r in self.lock["witnesses"]}),81)
  for r in self.lock["witnesses"]:
   d=inside(BASE,r["path"]).read_bytes();self.assertEqual((len(d),sha(d)),(r["bytes"],r["sha256"]),r["path"])
 def test_06_all_124_source_ids_preorder_ancestry(self):
  order=[e.get("id") for e in self.topics["en"].iter() if e.get("id")]
  self.assertEqual(len(order),124);self.assertEqual([e.get("id") for e in self.root.iter() if e.get("id") in order],order)
  self.assertEqual(len(self.target),126);self.assertEqual(set(self.target)-set(order),{UNIT,"credits"})
  for loc in ARCHIVES:
   sp=parents(self.roots[loc]);allowed=set(order)
   self.assertEqual([e.get("id") for e in self.topics[loc].iter() if e.get("id")],order)
   for ident in order:self.assertEqual(nearest(self.source[loc][ident],sp,allowed),nearest(self.target[ident],self.tp,allowed),ident)
 def test_07_25_questions_13_solutions_12_omissions(self):
  self.assertEqual(len(self.exercises),25)
  for q,e in enumerate(self.exercises,1):
   target=self.questions[q];self.assertEqual(text(target.find("h4")),f"प्रश्न {q}")
   sol=e.find(C+"solution");missing=target.findall("./p[@class='source-answer-missing']")
   self.assertEqual(sol is not None,q%2==1);self.assertEqual(len(missing),0 if sol is not None else 1)
   if sol is not None:self.assertEqual(self.target[sol.get("id")].get("class"),"solution")
   else:
    self.assertEqual(missing[0].get("data-kind"),"original");self.assertIn("उत्तर दिलेले नाही",text(missing[0]))
  self.assertEqual(len(self.root.findall(".//*[@class='solution']")),13);self.assertEqual(len(self.root.findall(".//*[@class='source-answer-missing']")),12)
 def test_08_all_answer_backlinks_local_and_https_links(self):
  for e in self.exercises:
   sol=e.find(C+"solution")
   if sol is None:continue
   p=e.find(C+"problem");pid,sid=p.get("id"),sol.get("id")
   self.assertEqual(len(self.target[pid].findall(f".//a[@href='#{sid}']")),1)
   self.assertEqual(len(self.target[sid].findall(f".//a[@href='#{pid}']")),1)
  href=[a.get("href") for a in self.root.iter("a")];local=[x for x in href if x.startswith("#")]
  self.assertEqual(len(local),31)
  for x in local:self.assertIn(x[1:],self.target)
  self.assertEqual([x for x in href if not x.startswith("#")],["https://openstax.org/books/intermediate-algebra-2e/pages/3-practice-test","https://creativecommons.org/licenses/by-nc-sa/4.0/"])
 def test_09_all_24_original_pixels_assets_and_review_copies(self):
  self.assertEqual(len(self.lock["source_images"]),24);seen=set()
  for r in self.lock["source_images"]:
   n=int(Path(r["member"]).name.split("_")[5]);loc=r["locale"];self.assertNotIn((n,loc),seen);seen.add((n,loc))
   d=self.archimgs[(n,loc)];self.assertEqual((len(d),sha(d)),(r["bytes"],r["sha256"]))
   self.assertEqual(inside(WORKSPACE,r["review_copy"]).read_bytes(),d);self.assertTrue(d.startswith(b"\xff\xd8\xff"))
   if loc=="en":self.assertEqual(inside(BASE,r["committed_asset"]).read_bytes(),d)
  self.assertEqual(set(self.images),set(WINDOWS));self.assertEqual(len(self.config["assets"]),12)
  self.assertEqual(sum(len(self.archimgs[(n,"en")]) for n in WINDOWS),778637)
  for n in WINDOWS:
   self.assertEqual(self.archimgs[(n,"en")],self.archimgs[(n,"id")])
   name=f"CNX_IntAlg_Figure_03_06_{n}_img_new.jpg";cfg=self.config["assets"][name]
   self.assertEqual(cfg["sha256"],sha(self.archimgs[(n,"en")]));self.assertEqual(cfg["mime"],"image/jpeg")
 def test_10_image_ids_placement_alt_and_windows(self):
  for loc in ARCHIVES:
   for m in self.topics[loc].iter(C+"media"):
    name=Path(m.find(C+"image").get("src")).name;n=int(name.split("_")[5]);fig=self.target[m.get("id")]
    self.assertEqual(fig.tag,"figure");self.assertEqual(fig.find("img").get("src"),"asset:"+name)
    self.assertTrue(re.search("[\u0900-\u097f]",fig.find("img").get("alt","")))
    self.assertIn(fig,list(self.questions[IMAGE_Q[n]].iter()))
  for n,(xmin,xmax,ymin,ymax,step) in WINDOWS.items():
   alt=norm(self.images[n].get("alt"))
   if xmin==ymin and xmax==ymax:self.assertIn(f"दोन्हीअक्षांवर{xmin}ते{xmax}",alt)
   else:self.assertIn(f"x:{xmin}ते{xmax}",alt);self.assertIn(f"y:{ymin}ते{ymax}",alt)
   phrase="प्रत्येकचौकटएकएकक" if step==1 else ("प्रत्येकचौकटदोनएकके" if step==2 else "प्रत्येकचौकट2.5एकके")
   self.assertIn(phrase,alt)
 def test_11_all_manually_read_pixel_points(self):
  for n,pts in POINTS.items():
   alt=norm(self.images[n].get("alt"))
   for x,y in pts:
    value=f"({x},{float(y) if isinstance(y,F) and y.denominator!=1 else y})"
    value=value.replace(".0","")
    self.assertIn(value,alt,(n,value))
 def test_12_points_equation_q2_and_intercepts_q6(self):
  eq=equation("3x-y=6");candidates=[(3,3),(2,0),(4,-6)]
  self.assertEqual([value(eq,*p)==0 for p in candidates],[True,True,False])
  q6=line("4x+2y=-8");self.assertEqual(value({(1,0):q6[0],(0,1):q6[1],(0,0):q6[2]},-2,0),0)
  self.assertEqual(value({(1,0):q6[0],(0,1):q6[1],(0,0):q6[2]},0,-4),0)
 def test_13_slopes_q3_q4_q5_and_vertical(self):
  self.assertEqual(slope((-5,2),(0,-1)),F(-3,5))
  with self.assertRaises(ZeroDivisionError):slope((2,-1),(2,1))
  self.assertIn("परिभाषित नाही",text(self.target["fs-id1167833412508"]));self.assertNotIn("शून्य",text(self.target["fs-id1167833412508"]))
  self.assertEqual(slope((5,2),(-1,-4)),1)
  self.assertEqual(slope((-3,-4),(-1,-3)),F(1,2))
 def test_14_line_formulas_q7_to_q13(self):
  formulas={7:"y=(5/3)x-1",8:"y=-x",9:"y=2",10:"y=-(3/4)x-2",
   11:"y=2x+5",12:"y=(1/2)x-4",13:"y=-(4/5)x-5"}
  givens={7:[(-3,-6),(0,-1),(3,4)],8:[(-2,2),(0,0),(2,-2)],9:[(-1,2),(0,2),(1,2)],
   10:[(0,-2),(4,-5)],11:[(-3,-1)],12:[(10,1),(6,-1)],13:[(-10,3)]}
  for q,s in formulas.items():
   p=equation(s)
   for point in givens[q]:self.assertEqual(value(p,*point),0,(q,point))
  self.assertEqual(slope((10,1),(6,-1)),F(1,2))
  self.assertEqual(F(5,4)*F(-4,5),-1)
  self.assertEqual(norm(self.checks["src-fs-id1167833138135-1"]),norm(formulas[11]))
  self.assertEqual(equation(self.checks["src-fs-id1167836706979-1"]),equation(formulas[13]))
 def test_15_inequality_boundary_direction_and_test_points(self):
  q14=inequality("y<=-x-3");q15=inequality("y>(3/2)x+5");q16=inequality("x-y>=-4");q17=inequality("y<=-5x")
  self.assertTrue(satisfies(q14,(-5,0)));self.assertFalse(satisfies(q14,(5,0)));self.assertTrue(satisfies(q14,(-3,0)))
  self.assertTrue(satisfies(q15,(-5,5)));self.assertFalse(satisfies(q15,(5,5)));self.assertFalse(satisfies(q15,(0,5)))
  self.assertTrue(satisfies(q16,(0,0)));self.assertFalse(satisfies(q16,(0,5)));self.assertTrue(satisfies(q16,(0,4)))
  self.assertTrue(satisfies(q17,(-5,0)));self.assertFalse(satisfies(q17,(5,0)));self.assertTrue(satisfies(q17,(0,0)))
  # Solving x-y>=-4 for y multiplies by -1, so the direction reverses.
  p,op=q16;self.assertEqual((p,op),(poly("x-y+4"),">="))
 def test_16_inequality_pixel_styles_and_source_disclosures(self):
  for n,word in [(252,"सलग"),(403,"तुटक"),(405,"सलग")]:self.assertIn(word,self.images[n].get("alt"))
  self.assertIn("समाविष्ट नाही",self.images[403].get("alt"));self.assertIn("समाविष्ट आहे",self.images[252].get("alt"));self.assertIn("समाविष्ट आहे",self.images[405].get("alt"))
  for loc in ARCHIVES:
   a=self.source[loc]["fs-id1167833053641"].get("alt")
   self.assertEqual("dashed" in a.lower(),loc=="en")
   self.assertIn("red" if loc=="en" else "merah",self.source[loc]["fs-id1167829877506"].get("alt").lower())
  self.assertIn("ID वर्णनात",text(self.target["fs-id1167833053641"]))
  note=text(self.target["fs-id1167829877506"]);self.assertIn("गडद निळी",note);self.assertIn("गुलाबी",note)
 def test_17_hiro_model_domain_clarification_not_answer(self):
  model=inequality("10x+15y>=450")
  for p in [(45,0),(0,30),(15,20)]:self.assertTrue(satisfies(model,p));self.assertGreaterEqual(p[0],0);self.assertGreaterEqual(p[1],0)
  for p in [(0,0),(-45,60),(60,-10)]:self.assertTrue(not satisfies(model,p) or min(p)<0)
  q=self.questions[18];self.assertEqual(len(q.findall("./p[@class='source-answer-missing']")),1)
  note=q.findall("./p[@data-kind='original']")[-1]
  for key in ["hiro-hours-x","hiro-hours-y"]:
   node=next(n for n in self.nodes if n.get("data-check")==key);self.assertIn(node,list(note.iter()))
  self.assertIn("उत्तर येथे भरलेले नाही",text(note));self.assertNotIn("10x",text(note));self.assertNotIn("15y",text(note))
  for loc in ARCHIVES:self.assertIsNone([e for e in self.topics[loc] if e.tag==C+"exercise"][17].find(C+"solution"))
 def test_18_finite_relation_q19_is_function_domain_range(self):
  pairs=[(-3,27),(-2,8),(-1,1),(0,0),(1,1),(2,8),(3,27)]
  self.assertEqual(len({x for x,y in pairs}),len(pairs))
  self.assertTrue(all(y==abs(x)**3 for x,y in pairs))
  self.assertEqual({x for x,y in pairs},{-3,-2,-1,0,1,2,3});self.assertEqual({y for x,y in pairs},{0,1,8,27})
  self.assertIn("होय",text(self.target["fs-id1167836476901"]))
 def test_19_function_evaluations_q20_q21(self):
  f=poly("4x^2-2x-3")
  self.assertEqual((value(f,-1),value(f,2)),(3,9))
  expected=add(f,mul({(0,0):F(-1)},poly("4c^2-2c-3")))
  self.assertEqual(expected,{})
  self.assertEqual(3*abs(F(-4)-1)-3,12)
  self.assertEqual(F(self.checks["literal-fs-id1167836571262-answer"]),12)
  self.assertEqual(len(self.questions[20].findall("./p[@class='source-answer-missing']")),1)
 def test_20_function_graph_q22_and_domain_range_q23_q24(self):
  # Complete manually read q22 cubic-shaped curve passes each vertical line.
  self.assertIn("घन-आकाराचा S-वक्र",self.images[253].get("alt"));self.assertIn("बाण",self.images[253].get("alt"))
  q23=poly("x^2+1")
  for p in POINTS[407]:self.assertEqual(value(q23,p[0]),p[1])
  self.assertEqual(interval(self.checks["literal-fs-id1167836531082-domain"]),(None,None,False,False))
  self.assertEqual(interval(self.checks["literal-fs-id1167836531082-range"]),(F(1),None,True,False))
  # x²>=0 and every nonnegative value is a square; not a finite-grid proof.
  for x in [F(-3),F(0),F(1,2),F(9)]:self.assertGreaterEqual(value(q23,x),1)
  # q24: principal sqrt(x+1): x>=-1, output>=0; inverse x=y²-1.
  for y in [F(0),F(1,2),F(3)]:self.assertEqual(y*y-1+1,y*y)
  self.assertEqual(norm(self.checks["src-fs-id1167833380263-1"]),"f(x)=√(x+1)")
 def test_21_q25_source_values_and_original_ordered_pairs(self):
  f=poly("x^2-4")
  for p in POINTS[254]:self.assertEqual(value(f,p[0]),p[1])
  source={"src-fs-id1167833071738-1":"x = −2,2","src-fs-id1167833071738-2":"y = −4",
   "src-fs-id1167833071738-3":"f(−1) = −3","src-fs-id1167833071738-4":"f(1) = −3"}
  for k,v in source.items():self.assertEqual(self.checks[k],v)
  self.assertEqual(interval(self.checks["literal-fs-id1167833071738-domain"]),(None,None,False,False))
  self.assertEqual(interval(self.checks["literal-fs-id1167833071738-range"]),(F(-4),None,True,False))
  self.assertEqual([self.checks[k] for k in ["intercepts-x-left","intercepts-x-right","intercept-y"]],["(−2, 0)","(2, 0)","(0, −4)"])
  note=text(self.questions[25].find("./p[@data-kind='original']"))
  for s in ["स्रोताने दिलेली सहनिर्देशक-मूल्ये","पूर्ण क्रमित-जोडी","जोडलेली मांडणी"]:self.assertIn(s,note)
 def test_22_all_54_source_math_occurrences_and_65_keys(self):
  self.assertEqual(len(self.nodes),65);self.assertEqual(self.checks,self.config["expected_math"])
  for loc in ARCHIVES:
   count=matched=0
   for para in self.topics[loc].iter(C+"para"):
    for i,m in enumerate(para.iter(M+"math"),1):
     count+=1;key=f"src-{para.get('id')}-{i}"
     if para.get("id")=="fs-id1167833071738" and i==5:
      self.assertEqual(norm(compact_source(m)),"-4,");continue
     self.assertIn(key,self.checks);self.assertEqual(norm(compact_source(m)),norm(self.checks[key]),(loc,key));matched+=1
   self.assertEqual((count,matched),(54,53))
  self.assertEqual(sum(k.startswith("literal-") for k in self.checks),6)
  self.assertEqual(set(self.checks)-{k for k in self.checks if k.startswith(("src-","literal-"))},ORIGINAL_KEYS)
  for key in ORIGINAL_KEYS:
   n=next(n for n in self.nodes if n.get("data-check")==key);p=n;original=False
   while p in self.tp:
    p=self.tp[p];original|=p.get("data-kind")=="original"
   self.assertTrue(original,key)
 def test_23_five_source_instruction_paras_and_labels(self):
  paras=[e for e in self.topics["en"] if e.tag==C+"para"];self.assertEqual(len(paras),5)
  for e in paras:self.assertTrue(re.search("[\u0900-\u097f]",text(self.target[e.get("id")])))
  for loc in ARCHIVES:self.assertEqual([e.get("id") for e in self.topics[loc] if e.tag==C+"para"],[e.get("id") for e in paras])
  for ident,labels in [("fs-id1167829590742","ⓐⓑⓒⓓⓔ"),("fs-id1167832951073","ⓐⓑⓒ"),("fs-id1167836629848","ⓐⓑⓒⓓⓔⓕ"),("fs-id1167833071738","ⓐⓑⓒⓓⓔⓕ")]:
   self.assertEqual("".join(re.findall("[ⓐ-ⓕ]",text(self.target[ident]))),labels)
 def test_24_accounting_locale_credits_offline_and_next_marker(self):
  self.assertEqual(self.root.attrib,{"id":UNIT,"lang":"mr-Deva-IN"})
  s=self.raw.decode();self.assertEqual(s,unicodedata.normalize("NFC",s));self.assertNotIn("\ufffd",s)
  for k,v in {"source_count":30,"translated_practice_items":25,"translated_worked_examples":0,
   "translated_definitions":0,"translated_resource_notes":0,"original_practice_items":0}.items():self.assertEqual(self.config[k],v)
  self.assertEqual(self.config["question_ids"],[])
  for term in self.config["required_terms"]:self.assertIn(term,text(self.root))
  for im in self.root.iter("img"):self.assertTrue(im.get("src").startswith("asset:"))
  for tag in ["script","iframe","object","embed","svg","audio","video"]:self.assertFalse(list(self.root.iter(tag)))
  credits=text(self.target["credits"])
  for s in ["CC BY-NC-SA 4.0","m81375","Introduction","Pendahuluan","CNX_IntAlg_Figure_04_00_001","fs-id1167836596342","पाच-पुस्तकांचे काम सुरू"]:self.assertIn(s,credits)
 def test_25_interpreters_reject_unsafe_or_false_forms(self):
  for bad in ["__import__('os')","x.__class__","x[0]","1/(x-1)","x^3","nan","x;1"]:
   with self.subTest(bad=bad),self.assertRaises(ValueError):poly(bad)
  with self.assertRaises(ValueError):mathml(E.fromstring(f'<math xmlns="{M[1:-1]}"><mphantom/></math>'))
  with self.assertRaises(ValueError):unique([("x",1),("x",2)])
  for bad in ["[-∞,∞]","(-∞,∞]"]:
   with self.assertRaises(ValueError):interval(bad)
  self.assertNotEqual(equation("y=2x+5"),equation("y=2x-5"))
  self.assertNotEqual(inequality("y>-5x")[1],inequality("y<=-5x")[1])
  with self.assertRaises(ValueError):inside(BASE,"../escape")
if __name__=="__main__":unittest.main(verbosity=2)
