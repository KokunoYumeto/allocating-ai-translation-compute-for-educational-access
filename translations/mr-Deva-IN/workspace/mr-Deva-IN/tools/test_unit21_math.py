"""MR021 independent source/mathematics regression, not reader acceptance.

Reads real frozen XML/config/fragments and only selected original ZIP members.
Exact Fraction arithmetic and a bounded AST/MathML interpreter; never eval.
Manual observations of 36 original rasters are hash-bound, not automated vision.
No writes, downloads, whole-archive extraction, optional skips or other unit imports.
"""
import ast
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import unittest
import xml.etree.ElementTree as E
import zipfile

BASE = Path(__file__).resolve().parents[1]
WORKSPACE = BASE.parent
UNIT = "MR-BRIDGE-021"
C = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
CHAPTER, TOPIC = "fs-id1167836524742", "fs-id1167836699953"
PREVIOUS, FOLLOWING = "fs-id1167826172554", "fs-id1167836628671"
PINS = {
    "translations/MR-BRIDGE-021.xml": [
        49033,
        "d179b984c1f22e796831e9f7d001e3b40634df8cc269c6c6b2e76e0fe0fcc5c9"
    ],
    "units/MR-BRIDGE-021.json": [
        7709,
        "6f210e5cb2266acf23214379684efa336f32c39bb0c3e1aa4621f275826ac4a6"
    ],
    "provenance/MR-BRIDGE-021.lock.json": [
        110903,
        "0128fa9f9e7fab0b5e9e68cfbd70d58e84495a13eb79260b2b9d1e41af8fcbc8"
    ]
}
IMAGE_PINS = {
    "238:en": [
        60666,
        "c9d3bd5d527430a74cba19b4bb5a4215bd217ffe8117fd6a4f9e1bdca2b1ea5f"
    ],
    "238:id": [
        60666,
        "c9d3bd5d527430a74cba19b4bb5a4215bd217ffe8117fd6a4f9e1bdca2b1ea5f"
    ],
    "239:en": [
        59326,
        "6b5c8309a1536afad670ed6c35ffd21cfbe0a71956e6a4be1cfd466587696634"
    ],
    "239:id": [
        59326,
        "6b5c8309a1536afad670ed6c35ffd21cfbe0a71956e6a4be1cfd466587696634"
    ],
    "240:en": [
        63527,
        "f4f66b8ada6e28df48a35f601cbd9be1650bedecb00583cd1e959edfd25dd7fa"
    ],
    "240:id": [
        63527,
        "f4f66b8ada6e28df48a35f601cbd9be1650bedecb00583cd1e959edfd25dd7fa"
    ],
    "241:en": [
        61255,
        "c294f4d9e193db4c8fd4319abb13d10b198ad0baf14949af08110d92c122958f"
    ],
    "241:id": [
        61255,
        "c294f4d9e193db4c8fd4319abb13d10b198ad0baf14949af08110d92c122958f"
    ],
    "242:en": [
        70256,
        "7fe327900f8184b690c3ec0e4e81a3ddbe6f8745fc29cce3d284eb78170ecd89"
    ],
    "242:id": [
        70256,
        "7fe327900f8184b690c3ec0e4e81a3ddbe6f8745fc29cce3d284eb78170ecd89"
    ],
    "243:en": [
        75317,
        "514f0e759e5bb9ab421fe53b712ba82e618c03ee1ea88e8477b86e99dcd92267"
    ],
    "243:id": [
        75317,
        "514f0e759e5bb9ab421fe53b712ba82e618c03ee1ea88e8477b86e99dcd92267"
    ],
    "244:en": [
        73577,
        "bc483225bc9abe5cd1f044028617b93735c3ffc1a990f25613b7a915ad588d22"
    ],
    "244:id": [
        73577,
        "bc483225bc9abe5cd1f044028617b93735c3ffc1a990f25613b7a915ad588d22"
    ],
    "386:en": [
        60424,
        "ab171ad4a8e50f32c7d1580c89accd56b4ab7328d54f80f2ec2097fff2d9d9f7"
    ],
    "386:id": [
        60424,
        "ab171ad4a8e50f32c7d1580c89accd56b4ab7328d54f80f2ec2097fff2d9d9f7"
    ],
    "388:en": [
        57305,
        "4f4461770b3bc5cad39b9525dd09183d05f6e823a771cdf2143c170d3049cb8f"
    ],
    "388:id": [
        57305,
        "4f4461770b3bc5cad39b9525dd09183d05f6e823a771cdf2143c170d3049cb8f"
    ],
    "390:en": [
        65200,
        "fbfe0c7291dadbe7e21d97f847f765f6af9b1893dd87d3d95ae14c7d16ca65fc"
    ],
    "390:id": [
        65200,
        "fbfe0c7291dadbe7e21d97f847f765f6af9b1893dd87d3d95ae14c7d16ca65fc"
    ],
    "392:en": [
        59804,
        "0d19ef498951647b0c2394271422e05a401fae74b7a9a87293dd5f69981f6463"
    ],
    "392:id": [
        59804,
        "0d19ef498951647b0c2394271422e05a401fae74b7a9a87293dd5f69981f6463"
    ],
    "394:en": [
        42900,
        "013dd59a0893bb1e212da42376cb422078914cf7a06150e52db4688d18293b9d"
    ],
    "394:id": [
        42900,
        "013dd59a0893bb1e212da42376cb422078914cf7a06150e52db4688d18293b9d"
    ],
    "396:en": [
        63261,
        "0b5f751f7296c357a95ad935ae8b2b3ee9d874dbd4f571ec11c440c3e8ad7752"
    ],
    "396:id": [
        63261,
        "0b5f751f7296c357a95ad935ae8b2b3ee9d874dbd4f571ec11c440c3e8ad7752"
    ],
    "245:en": [
        54043,
        "ce84d0bc1735dbcc8edf05245e03c422bdc673952ba5130e1c159586996e836b"
    ],
    "245:id": [
        54043,
        "ce84d0bc1735dbcc8edf05245e03c422bdc673952ba5130e1c159586996e836b"
    ],
    "246:en": [
        59643,
        "1f4bd3f0837aaefd66ba06326cdfec5e12eaf08afa7f38d5bc3faf2ccc4324c7"
    ],
    "246:id": [
        59643,
        "1f4bd3f0837aaefd66ba06326cdfec5e12eaf08afa7f38d5bc3faf2ccc4324c7"
    ],
    "247:en": [
        71630,
        "3c647479f45adb7e70c61550aa17cf3feaae3bc54d9fdb02e4cd2746141daeff"
    ],
    "247:id": [
        71630,
        "3c647479f45adb7e70c61550aa17cf3feaae3bc54d9fdb02e4cd2746141daeff"
    ],
    "248:en": [
        58088,
        "975930511beac19bf91733646033c5796cb3bbe36f4ac05a32f1e8d84dde2eb9"
    ],
    "248:id": [
        58088,
        "975930511beac19bf91733646033c5796cb3bbe36f4ac05a32f1e8d84dde2eb9"
    ],
    "249:en": [
        67175,
        "e445bfce3807e1df8c29ce6faf80a2afee50165bdc01d218253e1b3231180b24"
    ],
    "249:id": [
        67175,
        "e445bfce3807e1df8c29ce6faf80a2afee50165bdc01d218253e1b3231180b24"
    ]
}
ARCHIVES = {
    "en": ("A20-canonical.zip", "osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9",
           "effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917"),
    "id": ("A20-v0.3.0-source.zip", "source",
           "a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7"),
}
MODULE_PINS = {
    "en": (247327, "021c29fa9a6ab3d5b06d2ef143a82d2ac818ed25fe6fd44ebf5d7a6be07a123a"),
    "id": (247303, "d89a74aef766afca6a4ac7e1ae720f120d22cc771c11dd7e025c55bca1fabb8e"),
}
# Independently read formulas in both selected modules, not copied config answers.
FORMULAS = {
    8: "5x+1", 9: "-4x-2", 10: "(2/3)x-1", 11: "-6", 12: "2x",
    13: "3x^2", 14: "-(1/2)x^2", 15: "x^2+2", 16: "x^3-2",
    17: "√(x+2)", 18: "-|x|", 19: "|x|+1",
}
# Finite display windows, NOT mathematical domain/range.
WINDOWS = {
    238: (-4,4,-2,6,1), 239: (-4,4,-4,4,1),
    240: (-8,8,-8,8,2), 241: (-8,8,-8,8,2), 242: (-8,8,-8,8,2),
    243: (-8,8,-8,8,2), 244: (-8,8,-8,8,2),
    245: (-2,10,-2,8,2), 246: (-6,6,-2,10,2),
    247: (-8,8,-8,8,2), 248: (-2,2,-6,6,"π/2;1"), 249: (-8,8,-8,8,2),
    386: (-4,4,-4,4,1), 388: (-4,4,-7,2,1), 390: (-4,4,-1,10,1),
    392: (-8,8,-2,10,2), 394: (-4,8,-4,8,2), 396: (-8,8,-2,10,2),
}
IMAGE_Q = {238:1,239:2,240:3,241:4,242:5,243:6,244:7,
           386:9,388:11,390:13,392:15,394:17,396:19,245:20,246:21,
           247:22,248:23,249:24}
# Coordinate values independently compared to all original pixels/source data.
POINTS = {
    238: [(-2,5),(-1,2),(0,1),(1,2),(2,5)],
    239: [(-1,-1),(0,0),(1,1)],
    240: [(-5,0),(5,0),(0,-5),(0,5)],
    241: [(-2,0),(-1,1),(-1,-1),(2,2),(2,-2)],
    242: [(-1,-1),(0,0),(1,1)],
    243: [(-3,0),(3,0),(-4,2),(-4,-2),(4,2),(4,-2)],
    244: [(0,-1),(1,0),(2,1),(1,-2),(2,-3)],
    386: [(-1,2),(0,-2),(-2,6)], 388: [(0,-6),(1,-6),(2,-6)],
    390: [(0,0),(-1,3),(1,3)], 392: [(0,2),(-2,6),(-1,3),(1,3),(2,6)],
    394: [(-2,0),(-1,1),(2,2)], 396: [(0,1),(-1,2),(1,2)],
    245: [(1,0),(2,1),(5,2)], 246: [(0,2),(-1,3),(1,3)],
    247: [(-2,-4),(0,0),(2,4)], 249: [(-2,0),(0,2),(2,0)],
}
WAVE = {F(-2):0,F(-3,2):1,F(-1):0,F(-1,2):-1,F(0):0,
        F(1,2):1,F(1):0,F(3,2):-1,F(2):0}
ORIGINAL_KEYS = {"infinity-open-endpoints","constant-line-correction",
                 "constant-singleton-interval","wave-all-zeros","wave-all-intercepts"}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def unique_object(pairs):
    result = {}
    for key,value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result

def inside(base, relative):
    path = (base / relative).resolve()
    if base.resolve() not in path.parents:
        raise ValueError("path escapes expected directory")
    return path

def text(node):
    return "".join(node.itertext())

def norm(value):
    return re.sub(r"\s+","",value.replace("−","-").replace("²","^2").replace("³","^3"))

def ids(root):
    return {e.get("id"): e for e in root.iter() if e.get("id")}

def parents(root):
    return {child:e for e in root.iter() for child in e}

def nearest(node, mapping, allowed):
    while node in mapping:
        node = mapping[node]
        if node.get("id") in allowed:
            return node.get("id")
    return None

def shape(node):
    return (node.tag,tuple(sorted(node.attrib.items())),node.text,
            tuple((shape(c),c.tail) for c in node))

def mathml(node):
    """Only presentation constructs actually read in the pinned topic."""
    tag=node.tag.removeprefix(M)
    if tag in {"mi","mn","mo","mtext"}:
        if len(node):
            raise ValueError("token with children")
        return node.text or ""
    if tag in {"math","mrow"}:
        return "".join(mathml(c) for c in node)
    if tag=="mfrac" and len(node)==2:
        return "(("+mathml(node[0])+")/("+mathml(node[1])+"))"
    if tag=="msup" and len(node)==2:
        return "("+mathml(node[0])+")^("+mathml(node[1])+")"
    if tag=="msqrt":
        return "√("+"".join(mathml(c) for c in node)+")"
    if tag=="mfenced":
        return node.get("open","(")+node.get("separators",",").join(mathml(c) for c in node)+node.get("close",")")
    raise ValueError("unsupported MathML " + tag)

def clean(poly):
    return {p:F(c) for p,c in poly.items() if c}

def plus(a,b):
    result=dict(a)
    for p,c in b.items():
        result[p]=result.get(p,F(0))+c
    return clean(result)

def times(a,b):
    result={}
    for pa,ca in a.items():
        for pb,cb in b.items():
            p=pa+pb
            result[p]=result.get(p,F(0))+ca*cb
    return clean(result)

def polynomial(value, variable="x"):
    """Strict univariate rational polynomial AST; no executable evaluation."""
    value=norm(value).replace("π",variable).replace("^","**")
    tokens=re.findall(r"\*\*|\d+|[xpk()+*/-]",value)
    if not value or "".join(tokens)!=value or variable not in {"x","p","k"}:
        raise ValueError("unsupported polynomial token")
    code=[]
    atom=lambda t:t.isdigit() or t==variable
    for token in tokens:
        if code and (atom(code[-1]) or code[-1]==")") and (atom(token) or token=="("):
            code.append("*")
        code.append(token)
    try:
        tree=ast.parse("".join(code),mode="eval").body
    except SyntaxError as exc:
        raise ValueError("bad expression") from exc
    def walk(n):
        if isinstance(n,ast.Constant) and type(n.value) is int:
            return clean({0:F(n.value)})
        if isinstance(n,ast.Name) and n.id==variable:
            return {1:F(1)}
        if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.UAdd,ast.USub)):
            return times({0:F(-1 if isinstance(n.op,ast.USub) else 1)},walk(n.operand))
        if isinstance(n,ast.BinOp):
            a,b=walk(n.left),walk(n.right)
            if isinstance(n.op,ast.Add): return plus(a,b)
            if isinstance(n.op,ast.Sub): return plus(a,times({0:F(-1)},b))
            if isinstance(n.op,ast.Mult): return times(a,b)
            if isinstance(n.op,ast.Div) and set(b)=={0} and b[0]:
                return times(a,{0:1/b[0]})
            if isinstance(n.op,ast.Pow) and set(b)<= {0}:
                exponent=b.get(0,F(0))
                if exponent.denominator==1 and 0<=exponent<=6:
                    result={0:F(1)}
                    for _ in range(int(exponent)): result=times(result,a)
                    return result
        raise ValueError("unsupported expression or nonconstant division")
    return walk(tree)

def substitute(poly,x):
    return sum((c*F(x)**p for p,c in poly.items()),F(0))

def model(value):
    value=norm(value)
    if value.startswith("f(x)="):
        value=value[5:]
    if value.startswith("√(") and value.endswith(")"):
        return ("sqrt",polynomial(value[2:-1]))
    if "|" in value:
        m=re.fullmatch(r"(-?)\|x\|([+-]\d+)?",value)
        if not m: raise ValueError("unsupported absolute-value model")
        return ("abs",F(-1 if m[1] else 1),F(m[2] or 0))
    return ("poly",polynomial(value))

def model_value(m,x):
    x=F(x)
    if m[0]=="poly": return substitute(m[1],x)
    if m[0]=="abs": return m[1]*abs(x)+m[2]
    if m[0]=="sqrt":
        value=substitute(m[1],x)
        if value<0: raise ValueError("outside real domain")
        # Exact only for rational perfect-square witnesses.
        from math import isqrt
        a,b=isqrt(value.numerator),isqrt(value.denominator)
        if a*a!=value.numerator or b*b!=value.denominator:
            raise ValueError("irrational witness: use algebraic range argument")
        return F(a,b)
    raise ValueError("unknown model")

def interval(value):
    value=norm(value)
    if value.startswith(("D:","R:")): value=value[2:]
    if value.startswith("{") and value.endswith("}"):
        c=F(value[1:-1]); return (c,c,True,True)
    if len(value)<5 or value[0] not in "([" or value[-1] not in ")]":
        raise ValueError("not an interval")
    parts=value[1:-1].split(",")
    if len(parts)!=2: raise ValueError("interval arity")
    lo=None if parts[0]=="-∞" else F(parts[0])
    hi=None if parts[1]=="∞" else F(parts[1])
    lc,hc=value[0]=="[",value[-1]=="]"
    if (lo is None and lc) or (hi is None and hc):
        raise ValueError("closed infinity")
    if lo is not None and hi is not None and (lo>hi or (lo==hi and not(lc and hc))):
        raise ValueError("empty/reversed interval")
    return (lo,hi,lc,hc)

ALL=(None,None,False,False)

def contains(iv,x):
    # Infinity is not a real input, even for an unbounded interval.
    x=F(x);lo,hi,lc,hc=iv
    return (lo is None or x>lo or (lc and x==lo)) and (hi is None or x<hi or (hc and x==hi))

def domain_range(m):
    """Classify these exact forms by coefficient identities, not finite samples.

    Nonzero affine: inverse (y-b)/a; constant: singleton. a*x²+b:
    square>=0 and every nonnegative square has a real root. Odd monomial
    plus constant: real cube root inverse. Principal sqrt has nonnegative
    value and inverse x=y²-b; abs uses ±x with x>=0 / x<=0.
    """
    if m[0]=="sqrt":
        p=m[1]
        if p.get(1)!=1 or set(p)-{0,1}: raise ValueError("outside reviewed root form")
        b=p.get(0,F(0));return ((-b,None,True,False),(F(0),None,True,False))
    if m[0]=="abs":
        a,b=m[1:]
        return ALL,((b,None,True,False) if a>0 else (None,b,False,True))
    p=m[1];degree=max(p,default=0);b=p.get(0,F(0))
    if degree==0: return ALL,(b,b,True,True)
    if degree==1 or degree==3 and set(p)<= {0,3}: return ALL,ALL
    if degree==2 and set(p)<= {0,2}:
        return ALL,((b,None,True,False) if p[2]>0 else (None,b,False,True))
    raise ValueError("outside analytically reviewed model family")

def pi_coefficient(value):
    p=polynomial(value,"p")
    if not p: return F(0)
    if set(p)!={1}: raise ValueError("not a rational multiple of pi")
    return p[1]

def call(value):
    value=norm(value).rstrip(".,")
    if not value.startswith("f("): raise ValueError("expected f call")
    depth=1; end=2
    while end<len(value) and depth:
        depth += (value[end]=="(")-(value[end]==")")
        end+=1
    if depth: raise ValueError("unbalanced f call")
    arg=value[2:end-1]
    arg=("x",) if arg=="x" else ("pi",pi_coefficient(arg))
    tail=value[end:]
    if tail and not tail.startswith("="): raise ValueError("bad call tail")
    return arg, F(tail[1:]) if tail else None

def point(value):
    value=norm(value).rstrip(",")
    if not(value.startswith("(") and value.endswith(")")): raise ValueError("point delimiters")
    parts=value[1:-1].split(",")
    if len(parts)!=2: raise ValueError("point arity")
    return pi_coefficient(parts[0]),F(parts[1])

class Unit21(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=(BASE/f"translations/{UNIT}.xml").read_bytes()
        cls.root=E.fromstring(cls.raw);cls.target=ids(cls.root);cls.target_parents=parents(cls.root)
        cls.config=json.loads((BASE/f"units/{UNIT}.json").read_text(encoding="utf-8"),object_pairs_hook=unique_object)
        cls.lock=json.loads((BASE/f"provenance/{UNIT}.lock.json").read_text(encoding="utf-8"),object_pairs_hook=unique_object)
        cls.check_nodes=[n for n in cls.root.iter() if n.get("data-check")]
        cls.checks={n.get("data-check"):text(n) for n in cls.check_nodes}
        cls.modules={};cls.module_bytes={};cls.topics={};cls.source_ids={};cls.archive_images={}
        for locale,(archive,prefix,_) in ARCHIVES.items():
            with zipfile.ZipFile(WORKSPACE/"downloads/mr-Deva-IN/releases"/archive) as z:
                data=z.read(prefix+"/modules/m81374/index.cnxml")
                cls.module_bytes[locale]=data; cls.modules[locale]=E.fromstring(data)
                cls.source_ids[locale]=ids(cls.modules[locale])
                cls.topics[locale]=cls.source_ids[locale][TOPIC]
                for n in WINDOWS:
                    name=f"CNX_IntAlg_Figure_03_06_{n}_img_new.jpg"
                    cls.archive_images[(n,locale)]=z.read(prefix+"/media/"+name)
        cls.exercises=[e for e in cls.topics["en"] if e.tag==C+"exercise"]
        cls.questions={n:cls.target[e.get("id")] for n,e in enumerate(cls.exercises,1)}
        cls.source_questions={loc:[e for e in cls.topics[loc] if e.tag==C+"exercise"] for loc in ARCHIVES}
        cls.images={int(n.get("src").split("_")[5]):n for n in cls.root.iter("img")}

    def test_01_exact_input_pins(self):
        for path,expected in PINS.items():
            data=(BASE/path).read_bytes()
            self.assertEqual([len(data),sha(data)],expected,path)

    def test_02_source_module_pins_metadata_boundary(self):
        for locale in ARCHIVES:
            data=self.module_bytes[locale]
            self.assertEqual((len(data),sha(data)),MODULE_PINS[locale])
            chapter=self.source_ids[locale][CHAPTER]
            self.assertEqual([e.get("id") for e in list(chapter)[-2:]],[PREVIOUS,TOPIC])
            content=next(e for e in self.modules[locale].iter() if chapter in list(e))
            self.assertEqual(list(content)[list(content).index(chapter)+1].get("id"),FOLLOWING)
            metadata=self.modules[locale].find(C+"metadata")
            self.assertIn("m81374",text(metadata));self.assertIn("4b2bbf1b-2df7-4b9a-9933-dd70d1fd8ada",text(metadata))
            self.assertEqual(self.topics[locale].find(C+"title/"+C+"link").get("document"),"m81374")

    def test_03_full_ordered_31_selectors(self):
        target=[e.get("data-source") for e in self.root.iter() if e.get("data-source")]
        expected=["A20:m81374#"+e.get("id") for e in list(self.topics["en"])[1:]]
        self.assertEqual(len(expected),31);self.assertEqual(target,expected)
        self.assertEqual([s["locator"] for s in self.lock["source_selections"]],expected)
        self.assertEqual([s["target_id"] for s in self.lock["source_selections"]],[e.get("id") for e in list(self.topics["en"])[1:]])
        self.assertEqual([e.get("id") for e in list(self.topics["id"])[1:]],[e.get("id") for e in list(self.topics["en"])[1:]])

    def test_04_all_62_frozen_fragments_against_archive(self):
        count=total=0
        for selection in self.lock["source_selections"]:
            self.assertEqual([r["locale"] for r in selection["sources"]],["en","id"])
            for r in selection["sources"]:
                data=inside(BASE,r["fragment_path"]).read_bytes()
                self.assertEqual(sha(data),r["fragment_sha256"])
                source=self.source_ids[r["locale"]][selection["target_id"]]
                self.assertEqual(shape(E.fromstring(data)),shape(source),r["fragment_path"])
                self.assertEqual(r["module_sha256"],MODULE_PINS[r["locale"]][1])
                self.assertEqual(r["archive_sha256"],ARCHIVES[r["locale"]][2])
                self.assertEqual(len(r["math_sha256"]),len(list(source.iter(M+"math"))))
                self.assertEqual(r["math_sha256"],
                                 [sha(E.tostring(m,encoding="utf-8")) for m in source.iter(M+"math")])
                count+=1;total+=len(data)
        self.assertEqual((count,total),(62,52245))

    def test_05_all_89_local_witnesses(self):
        records=self.lock["witnesses"]
        self.assertEqual(len(records),89);self.assertEqual(len({r["path"] for r in records}),89)
        for r in records:
            data=inside(BASE,r["path"]).read_bytes()
            self.assertEqual((len(data),sha(data)),(r["bytes"],r["sha256"]),r["path"])

    def test_06_113_source_ids_preorder_and_ancestry(self):
        source_order=[CHAPTER]+[e.get("id") for e in self.topics["en"].iter() if e.get("id")]
        self.assertEqual(len(source_order),113)
        self.assertEqual([e.get("id") for e in self.root.iter() if e.get("id") in source_order],source_order)
        self.assertEqual(len(self.target),115)
        self.assertEqual(len([e for e in self.root.iter() if e.get("id")]),115)
        self.assertEqual(set(self.target)-set(source_order),{UNIT,"credits"})
        for locale in ARCHIVES:
            source=self.source_ids[locale];mapping=parents(self.modules[locale])
            self.assertEqual([CHAPTER]+[e.get("id") for e in self.topics[locale].iter() if e.get("id")],source_order)
            for ident in source_order[1:]:
                self.assertEqual(nearest(source[ident],mapping,set(source_order)),
                                 nearest(self.target[ident],self.target_parents,set(source_order)),ident)

    def test_07_questions_solutions_and_omissions(self):
        self.assertEqual(len(self.questions),24)
        for n,e in enumerate(self.exercises,1):
            target=self.questions[n]
            self.assertEqual(text(target.find("h4")),f"प्रश्न {n}")
            sol=e.find(C+"solution"); omissions=target.findall("./p[@class='source-answer-missing']")
            self.assertEqual(sol is not None,n%2==1)
            if sol is not None:
                self.assertEqual(len(omissions),0)
                self.assertEqual(self.target[sol.get("id")].get("class"),"solution")
            else:
                self.assertEqual(len(omissions),1)
                self.assertEqual(omissions[0].get("data-kind"),"original")
                self.assertIn("उत्तर दिलेले नाही",text(omissions[0]))
                self.assertFalse(target.findall(".//*[@class='solution']"))
            self.assertEqual([x.tag for x in e],[x.tag for x in self.source_questions["id"][n-1]])
        self.assertEqual(len(self.root.findall(".//*[@class='solution']")),12)
        self.assertEqual(len(self.root.findall(".//*[@class='source-answer-missing']")),12)

    def test_08_all_12_bidirectional_source_pairs_and_links(self):
        for e in self.exercises:
            sol=e.find(C+"solution")
            if sol is None: continue
            p=e.find(C+"problem");pid,sid=p.get("id"),sol.get("id")
            self.assertEqual(len(self.target[pid].findall(f".//a[@href='#{sid}']")),1)
            self.assertEqual(len(self.target[sid].findall(f".//a[@href='#{pid}']")),1)
        links=[a.get("href") for a in self.root.iter("a")]
        local=[h for h in links if h.startswith("#")]
        self.assertEqual(len(local),28)
        for h in local:self.assertIn(h[1:],self.target)
        self.assertEqual([h for h in links if not h.startswith("#")],[
            "https://openstax.org/books/intermediate-algebra-2e/pages/3-6-graphs-of-functions",
            "https://openstax.org/books/intermediate-algebra-2e/pages/3-introduction",
            "https://creativecommons.org/licenses/by-nc-sa/4.0/"])
        refs=self.root.findall(".//a[@data-source-document]")
        self.assertEqual(len(refs),1);self.assertEqual(refs[0].get("data-source-document"),"m81374")
        self.assertIn("इंटरनेट",text(self.root))

    def test_09_all_36_original_image_bytes_and_18_assets(self):
        self.assertEqual(len(self.lock["source_images"]),36)
        seen=set()
        for rec in self.lock["source_images"]:
            n=int(Path(rec["member"]).name.split("_")[5]);loc=rec["locale"]
            self.assertNotIn((n,loc),seen);seen.add((n,loc))
            data=self.archive_images[(n,loc)]
            self.assertEqual([len(data),sha(data)],IMAGE_PINS[f"{n}:{loc}"])
            self.assertEqual((len(data),sha(data)),(rec["bytes"],rec["sha256"]))
            self.assertEqual(inside(WORKSPACE,rec["review_copy"]).read_bytes(),data)
            self.assertTrue(data.startswith(b"\xff\xd8\xff"))
            if loc=="en":
                self.assertEqual(inside(BASE,rec["committed_asset"]).read_bytes(),data)
        self.assertEqual(set(self.images),set(WINDOWS))
        self.assertEqual(len(self.config["assets"]),18)
        self.assertEqual(sum(len(self.archive_images[(n,"en")]) for n in WINDOWS),1123397)
        for n in WINDOWS:
            self.assertEqual(self.archive_images[(n,"en")],self.archive_images[(n,"id")])
            name=f"CNX_IntAlg_Figure_03_06_{n}_img_new.jpg"
            cfg=self.config["assets"][name]
            self.assertEqual(cfg["mime"],"image/jpeg")
            self.assertEqual(cfg["sha256"],IMAGE_PINS[f"{n}:en"][1])
            self.assertEqual(inside(BASE,cfg["path"]).read_bytes(),self.archive_images[(n,"en")])

    def test_10_media_ids_placement_and_accessible_text(self):
        for locale in ARCHIVES:
            for source in self.topics[locale].iter(C+"media"):
                ident=source.get("id");image=source.find(C+"image")
                name=Path(image.get("src")).name
                target=self.target[ident]
                self.assertEqual(target.tag,"figure")
                self.assertEqual(target.find("img").get("src"),"asset:"+name)
                self.assertTrue(re.search("[\u0900-\u097f]",target.find("img").get("alt","")))
                self.assertEqual(target.find("figcaption").get("data-kind"),"original")
        for n,q in IMAGE_Q.items():
            self.assertIn(self.images[n],list(self.questions[q].iter()))

    def test_11_all_18_manually_read_axis_windows(self):
        for n,(xmin,xmax,ymin,ymax,step) in WINDOWS.items():
            alt=norm(self.images[n].get("alt"))
            if n==248:
                for s in ["x:-2πते2π","y:-6ते6","π/2","एकएकक"]:self.assertIn(s,alt)
            elif xmin==ymin and xmax==ymax and "दोन्हीअक्षांवर" in alt:
                self.assertIn(f"दोन्हीअक्षांवर{xmin}ते{xmax}",alt)
            else:
                self.assertIn(f"x:{xmin}ते{xmax}",alt);self.assertIn(f"y:{ymin}ते{ymax}",alt)
            if n!=248:self.assertIn("एकएकक" if step==1 else "दोनएकके",alt)
            fig=self.target_parents[self.images[n]]
            if n not in {246,248}:self.assertIn("दुरुस्ती",text(fig.find("figcaption")))

    def test_12_all_manual_coordinates_in_marathi_alt(self):
        for n,points in POINTS.items():
            alt=norm(self.images[n].get("alt"))
            for x,y in points:self.assertIn(f"({x},{y})",alt,(n,x,y))
        alt=norm(self.images[248].get("alt"))
        expected=["(-2π,0)","(-3π/2,1)","(-π,0)","(-π/2,-1)","(0,0)",
                  "(π/2,1)","(π,0)","(3π/2,-1)","(2π,0)"]
        for p in expected:self.assertIn(p,alt)

    def test_13_vertical_criterion_source_answers_and_counterexamples(self):
        expected={1:"होय.",3:"नाही.",5:"होय.",7:"नाही."}
        for n,answer in expected.items():
            for loc,yes,no in [("en","yes","no"),("id","ya","tidak")]:
                sol=self.source_questions[loc][n-1].find(C+"solution")
                self.assertEqual(text(sol).strip(),yes if answer=="होय." else no)
            sol=self.exercises[n-1].find(C+"solution")
            ident=sol.find(C+"para").get("id")
            self.assertEqual(text(self.target[ident]),answer)
        # One pair of different y values at the same x disproves function.
        for n,x,ys in [(240,0,[-5,5]),(241,-1,[-1,1]),(243,4,[-2,2]),(244,1,[-2,0])]:
            self.assertNotEqual(ys[0],ys[1])
            self.assertTrue(all((x,y) in POINTS[n] for y in ys))
        intro=text(self.target[TOPIC].find("aside"))
        self.assertIn("प्रांतातील प्रत्येक x",intro);self.assertIn("नेमके एक y",intro)
        self.assertIn("प्रांतात नसते",intro)
        # Positive judgments are the manually read complete graph criterion,
        # NOT a universal assertion inferred from the finite POINTS fixture.

    def test_14_all_twelve_formulas_source_target_coefficient_identity(self):
        for n,expected in FORMULAS.items():
            para=self.exercises[n-1].find(C+"problem/"+C+"para")
            target_math=self.target[para.get("id")].find("span")
            self.assertEqual(model(text(target_math)),model(expected),n)
            for loc in ARCHIVES:
                source=self.source_questions[loc][n-1].find(C+"problem/"+C+"para/"+M+"math")
                self.assertEqual(model(mathml(source)),model(expected),(n,loc))

    def test_15_analytic_domain_range_for_all_formulas(self):
        expected={8:(ALL,ALL),9:(ALL,ALL),10:(ALL,ALL),
            11:(ALL,(F(-6),F(-6),True,True)),12:(ALL,ALL),
            13:(ALL,(F(0),None,True,False)),14:(ALL,(None,F(0),False,True)),
            15:(ALL,(F(2),None,True,False)),16:(ALL,ALL),
            17:((F(-2),None,True,False),(F(0),None,True,False)),
            18:(ALL,(None,F(0),False,True)),19:(ALL,(F(1),None,True,False))}
        for n,formula in FORMULAS.items():
            self.assertEqual(domain_range(model(formula)),expected[n])
            # The symbolic family conditions above, not these witnesses,
            # justify the universal domain/range classification.
            for x in [-3,-2,0,F(1,2),2,10]:
                d,r=expected[n]
                if contains(d,x):
                    if n==17 and x not in {-2,2}:continue
                    self.assertTrue(contains(r,model_value(model(formula),x)))

    def test_16_all_seven_literal_domain_range_answers(self):
        expected={9:("fs-id1167836688777",ALL,ALL),
            11:("fs-id1167829693240",ALL,(F(-6),F(-6),True,True)),
            13:("fs-id1167836429712",ALL,(F(0),None,True,False)),
            15:("fs-id1167836387844",ALL,(F(2),None,True,False)),
            17:("fs-id1167833279765",(F(-2),None,True,False),(F(0),None,True,False)),
            19:("fs-id1167829693688",ALL,(F(1),None,True,False)),
            21:("fs-id1167829596918",ALL,(F(2),None,True,False))}
        for q,(ident,d,r) in expected.items():
            ds=self.checks[f"literal-{ident}-D"]
            rs=self.checks[f"{'corrected' if q==11 else 'literal'}-{ident}-R"]
            self.assertEqual((interval(ds),interval(rs)),(d,r),q)
            for loc in ARCHIVES:
                source=norm(text(self.source_ids[loc][ident]))
                match=re.search(r"D:(.*),R:(.*)$",source)
                self.assertIsNotNone(match)
                self.assertEqual(interval(match[1]),d)
                if q!=11:self.assertEqual(interval(match[2]),r)

    def test_17_negative_six_correction_and_degenerate_interval(self):
        for loc,bad in [("en","R:(6)"),("id","R:{6}")]:
            self.assertIn(bad,norm(text(self.source_ids[loc]["fs-id1167829693240"])))
        self.assertEqual(self.checks["constant-line-correction"],"y = −6")
        self.assertEqual(interval(self.checks["constant-singleton-interval"]),interval("R:{−6}"))
        iv=interval(self.checks["corrected-fs-id1167829693240-R"])
        self.assertTrue(contains(iv,-6));self.assertFalse(contains(iv,6));self.assertFalse(contains(iv,F(-11,2)))
        note=text(self.questions[11].find("./p[@data-kind='original']"))
        for s in ["EN","ID","ऋणचिन्ह","एकच मूल्य"]:self.assertIn(s,note)

    def test_18_fractional_signs_root_full_grouping_and_principal_value(self):
        self.assertEqual(model(FORMULAS[10])[1],{0:F(-1),1:F(2,3)})
        self.assertEqual(model(FORMULAS[14])[1],{2:F(-1,2)})
        root=self.source_questions["en"][16].find(".//"+M+"msqrt")
        self.assertEqual(polynomial(mathml(root[0])),{0:F(2),1:F(1)})
        self.assertEqual(model_value(model(FORMULAS[17]),-2),0)
        self.assertEqual(model_value(model(FORMULAS[17]),-1),1)
        self.assertEqual(model_value(model(FORMULAS[17]),2),2)
        with self.assertRaises(ValueError):model_value(model(FORMULAS[17]),F(-201,100))
        # y²=x+2 and y>=0; construct x=y²-2 for arbitrary y>=0.
        for y in [F(0),F(1,2),F(17,3)]:
            self.assertEqual(model_value(model(FORMULAS[17]),y*y-2),y)

    def test_19_formula_graph_points_and_root_curvature(self):
        for n,q in [(386,9),(388,11),(390,13),(392,15),(394,17),(396,19)]:
            for x,y in POINTS[n]:self.assertEqual(model_value(model(FORMULAS[q]),x),y,(n,x,y))
        self.assertEqual(model_value(model(FORMULAS[9]),-2),6)
        self.assertGreater(6,WINDOWS[386][3])
        self.assertIn("चौकटीबाहेर",self.images[386].get("alt"))
        for n in [245,394]:
            points=POINTS[n];a,b,c=points
            first=F(b[1]-a[1],b[0]-a[0]);second=F(c[1]-b[1],c[0]-b[0])
            self.assertNotEqual(first,second)  # Even these 3 points refute a straight ray.
            self.assertIn("सरळ किरण नाही",self.images[n].get("alt"))
            fig=self.target_parents[self.images[n]]
            self.assertIn("half-line/setengah garis",text(fig))
        for loc in ARCHIVES:
            for n in [245,394]:
                media=next(m for m in self.topics[loc].iter(C+"media") if str(n)+"_img" in m.find(C+"image").get("src"))
                self.assertIn("half-line" if loc=="en" else ("Setengah garis" if n==394 else "Setengah garis"),media.get("alt"))

    def test_20_wave_all_source_question_calls_and_answer_calls(self):
        questions=[m for m in self.source_ids["en"]["fs-id1167836622098"].iter(M+"math")]
        self.assertEqual(len(questions),6)
        for i in range(1,5):
            self.assertEqual(call(mathml(questions[i-1])),call(self.checks[f"src-fs-id1167836622098-{i}"]))
        for i,axis in [(5,"x"),(6,"y")]:
            self.assertEqual(mathml(questions[i-1]),axis)
            self.assertEqual(self.checks[f"src-fs-id1167836622098-{i}"],axis)
        expected=[(F(0),0),(F(1,2),1),(F(-3,2),1)]
        for i,(arg,answer) in enumerate(expected,1):
            key=f"{'corrected' if i==1 else 'src'}-fs-id1167824720942-{i}"
            self.assertEqual(call(self.checks[key]),(("pi",arg),F(answer)))
            self.assertEqual(WAVE[arg],answer)
        for loc in ARCHIVES:
            source=list(self.source_ids[loc]["fs-id1167824720942"].iter(M+"math"))
            self.assertEqual(len(source),13)
            self.assertEqual(call(mathml(source[0])),(("x",),F(0)))
            for i in [1,2,3]:
                self.assertEqual(call(mathml(source[i])),call(self.checks[f"src-fs-id1167824720942-{i+1}"]))

    def test_21_wave_five_zeros_intercepts_and_all_eight_subparts(self):
        zeroes=tuple(p for p,y in WAVE.items() if y==0)
        self.assertEqual(zeroes,tuple(map(F,[-2,-1,0,1,2])))
        for loc in ARCHIVES:
            para=self.source_ids[loc]["fs-id1167824720942"]
            source=list(para.iter(M+"math"))
            for i,k in enumerate(zeroes,6):
                target=self.checks[f"src-fs-id1167824720942-{i}"]
                self.assertEqual(point(target),(k,F(0)))
                self.assertEqual(point(mathml(source[i-1])),point(target))
            self.assertEqual(point(mathml(source[10])),point(self.checks["src-fs-id1167824720942-11"]))
            src_zero_values=mathml(source[4]).split("=")[1].split(",")
            target_zero_values=self.checks["src-fs-id1167824720942-5"].split("=")[1].split(",")
            self.assertEqual(tuple(map(pi_coefficient,src_zero_values)),zeroes)
            self.assertEqual(tuple(map(pi_coefficient,target_zero_values)),zeroes)
        self.assertEqual(point(self.checks["src-fs-id1167824720942-11"]),(F(0),F(0)))
        for ident in ["fs-id1167836622098","fs-id1167824720942"]:
            self.assertEqual(re.findall("[ⓐ-ⓗ]",text(self.target[ident])),list("ⓐⓑⓒⓓⓔⓕⓖⓗ"))
        self.assertIn("दृश्य चौकटीतील",text(self.target["fs-id1167824720942"]))

    def test_22_wave_corrected_open_infinity_and_closed_extrema(self):
        for loc in ARCHIVES:
            source=list(self.source_ids[loc]["fs-id1167824720942"].iter(M+"math"))
            self.assertEqual(norm(mathml(source[11])),"[-∞,∞]")
            with self.assertRaises(ValueError):interval(mathml(source[11]))
            self.assertEqual(interval(mathml(source[12])),(F(-1),F(1),True,True))
        self.assertEqual(interval(self.checks["corrected-fs-id1167824720942-12"]),ALL)
        self.assertEqual(interval(self.checks["src-fs-id1167824720942-13"]),(F(-1),F(1),True,True))
        note=text(self.questions[23])
        for s in ["दोन्ही स्रोतांतील MathML","गोल कंस","वगळलेले नाहीत"]:self.assertIn(s,note)

    def test_23_wave_extension_is_explicitly_conditional_not_sine_inference(self):
        source_alt={}
        for loc in ARCHIVES:
            media=self.source_ids[loc]["fs-id1167829748062"]
            source_alt[loc]=media.get("alt")
        self.assertIn("The pattern extends infinitely to the left and right.",source_alt["en"])
        self.assertIn("Pola ini memanjang ke kiri dan kanan tanpa batas.",source_alt["id"])
        for alt in source_alt.values():
            self.assertNotIn("sin",alt.lower());self.assertNotIn("kπ",alt)
        node=next(n for n in self.check_nodes if n.get("data-check")=="wave-all-zeros")
        paragraph=self.target_parents[node]
        self.assertEqual(paragraph.get("data-kind"),"original")
        for s in ["सशर्त","जर","आणि त्यांखेरीज इतर शून्य-मूल्ये येत नाहीत","अतिरिक्त अट",
                  "लेखकनिर्मित","सिद्ध केलेला निष्कर्ष नाही","कोणताही पूर्णांक"]:
            self.assertIn(s,text(paragraph))
        self.assertEqual(self.checks["wave-all-zeros"],"x = kπ")
        self.assertEqual(self.checks["wave-all-intercepts"],"(kπ, 0)")
        # Logical scope is guarded in prose. No finite sine sampling "proof"
        # or automatic universal periodic-function claim occurs here.

    def test_24_semicircle_six_subparts_and_closed_endpoints(self):
        for loc in ARCHIVES:
            para=self.source_ids[loc]["fs-id1167832926094"]
            maths=list(para.iter(M+"math"))
            self.assertEqual(len(maths),4)
            for i in [0,1]:
                self.assertEqual(call(mathml(maths[i])),call(self.checks[f"src-fs-id1167832926094-{i+1}"]))
            for i,axis in [(3,"x"),(4,"y")]:
                self.assertEqual(mathml(maths[i-1]),axis)
                self.assertEqual(self.checks[f"src-fs-id1167832926094-{i}"],axis)
            self.assertEqual(re.findall("[ⓐ-ⓕ]",text(para)),list("ⓐⓑⓒⓓⓔⓕ"))
        self.assertEqual(re.findall("[ⓐ-ⓕ]",text(self.target["fs-id1167832926094"])),list("ⓐⓑⓒⓓⓔⓕ"))
        # Independent intended upper semicircle: x²+y²=4 and y>=0.
        for x,y in POINTS[249]:self.assertEqual(x*x+y*y,4);self.assertGreaterEqual(y,0)
        self.assertEqual((0,2),POINTS[249][1])
        self.assertTrue(all(contains(interval("[-2,2]"),x) for x in [-2,0,2]))
        self.assertFalse(contains(interval("[-2,2]"),F(201,100)))
        self.assertTrue(contains(interval("[0,2]"),2));self.assertFalse(contains(interval("[0,2]"),-1))
        self.assertIn("बाण किंवा रिकामी वर्तुळे नाहीत",self.images[249].get("alt"))
        self.assertEqual(len(self.questions[24].findall("./p[@class='source-answer-missing']")),1)

    def test_25_graph_only_domain_range_not_window_or_unique_formula(self):
        # Intended full source curves/readings, not fits to a finite point set.
        for n in [245,246,247]:
            self.assertIn("बाण",self.images[n].get("alt"))
        self.assertIn("स्थानिक उंचवटा",self.images[247].get("alt"))
        self.assertIn("स्थानिक खोलगट",self.images[247].get("alt"))
        self.assertNotIn("f(x)=",norm(self.images[247].get("alt")))
        self.assertNotIn("f(x)=",norm(self.images[245].get("alt")))
        self.assertEqual(interval(self.checks["literal-fs-id1167829596918-D"]),ALL)
        self.assertEqual(interval(self.checks["literal-fs-id1167829596918-R"]),(F(2),None,True,False))
        self.assertIn("दृश्य चौकटीचा विस्तार",text(self.root))
        self.assertIn("सहप्रांताशी आपोआप समान नसतो",text(self.root))

    def test_26_all_54_math_keys_source_location_and_config(self):
        self.assertEqual(len(self.check_nodes),54);self.assertEqual(len(self.checks),54)
        self.assertEqual(self.checks,self.config["expected_math"])
        sourcekeys={}; covered=0
        for loc in ARCHIVES:
            for para in self.topics[loc].iter(C+"para"):
                for i,m in enumerate(para.iter(M+"math"),1):
                    ident=para.get("id");covered+=1
                    if ident=="fs-id1167833279765":
                        self.assertEqual(norm(mathml(m)),"-2,")
                        self.assertIn("-2",norm(self.checks[f"literal-{ident}-D"]))
                        continue
                    key=f"{'corrected' if ident=='fs-id1167824720942' and i in {1,12} else 'src'}-{ident}-{i}"
                    self.assertIn(key,self.checks)
                    node=next(n for n in self.check_nodes if n.get("data-check")==key)
                    self.assertIn(node,list(self.target[ident].iter()))
                    sourcekeys[key]=m
        self.assertEqual(covered,72);self.assertEqual(len(sourcekeys),35)
        literal={k for k in self.checks if k.startswith("literal-") or k=="corrected-fs-id1167829693240-R"}
        self.assertEqual(len(literal),14)
        self.assertEqual(set(self.checks)-set(sourcekeys)-literal,ORIGINAL_KEYS)
        for key in ORIGINAL_KEYS:
            node=next(n for n in self.check_nodes if n.get("data-check")==key)
            ancestors=[];p=node
            while p in self.target_parents:p=self.target_parents[p];ancestors.append(p)
            self.assertTrue(any(p.get("data-kind")=="original" for p in ancestors))

    def test_27_seven_instructions_complete_question_grouping(self):
        source=[e for e in self.topics["en"] if e.tag==C+"para"]
        self.assertEqual(len(source),7)
        for e in source:
            target=self.target[e.get("id")]
            self.assertTrue(re.search("[\u0900-\u097f]",text(target)))
            self.assertEqual(bool(e.find(C+"emphasis") is not None),bool(target.find("strong") is not None))
        self.assertIn("ⓐ प्रत्येक फलनाचा आलेख काढा",text(self.target["fs-id1167826205174"]))
        self.assertIn("ⓑ त्याचा प्रांत आणि मूल्यसंच",text(self.target["fs-id1167826205174"]))
        for ident in ["fs-id1167826205174","fs-id1167836310456"]:
            self.assertIn("अंतराल-संकेतलेखनात",text(self.target[ident]))

    def test_28_accounting_locale_no_new_answers_or_network_assets(self):
        self.assertEqual(self.root.attrib,{"id":UNIT,"lang":"mr-Deva-IN"})
        self.assertEqual(self.raw.decode("utf-8"),unicodedata.normalize("NFC",self.raw.decode("utf-8")))
        self.assertNotIn("\ufffd",self.raw.decode("utf-8"))
        for key,value in {"source_count":31,"translated_practice_items":24,
                          "translated_worked_examples":0,"translated_definitions":0,
                          "original_practice_items":0,"translated_resource_notes":0}.items():
            self.assertEqual(self.config[key],value)
        self.assertEqual(self.config["question_ids"],[])
        for term in self.config["required_terms"]:self.assertIn(term,text(self.root))
        for img in self.root.iter("img"):self.assertTrue(img.get("src").startswith("asset:"))
        for tag in ["script","iframe","object","embed","svg","audio","video"]:
            self.assertFalse(list(self.root.iter(tag)))
        self.assertIn("CC BY-NC-SA 4.0",text(self.target["credits"]))
        self.assertIn("स्वतंत्र सूचना",text(self.target["credits"]))
        self.assertIn(FOLLOWING,text(self.target["credits"]))
        self.assertIn("पाच-पुस्तकांचे काम सुरू",text(self.target["credits"]))

    def test_29_interpreter_rejects_mutations_and_unsupported_content(self):
        for bad in ["__import__('os')","x.__class__","x[0]","1/(x-1)","x**-1","x^7","nan","x;1"]:
            with self.subTest(bad=bad),self.assertRaises(ValueError):polynomial(bad)
        with self.assertRaises(ValueError):mathml(E.fromstring(f'<math xmlns="{M[1:-1]}"><mphantom/></math>'))
        with self.assertRaises(ValueError):unique_object([("x",1),("x",2)])
        for bad in ["[-∞,∞]","(-∞,∞]","[2,-2]","(-6,-6)"]:
            with self.assertRaises(ValueError):interval(bad)
        self.assertNotEqual(model("√(x+2)"),model("x+2"))
        with self.assertRaises(ValueError):model("√(x)+2")
        self.assertNotEqual(model("-|x|"),model("|x|"))
        self.assertNotEqual(model("-6"),model("6"))
        self.assertNotEqual(polynomial("-(1/2)x^2"),polynomial("(-x/2)^2"))
        with self.assertRaises(ValueError):inside(BASE,"../outside.txt")

if __name__=="__main__":
    unittest.main(verbosity=2)
