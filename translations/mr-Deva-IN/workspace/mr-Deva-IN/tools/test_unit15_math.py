"""Independent MR015 source, mathematics and pixel-witness regressions.

Run with Python -B. All inputs are read-only, including ZIP members in memory.
No acquisition, extraction, build, browser, HTML geometry, PDF or cache writes.
Pixel fixtures bind 88 personally viewed original files; these tests do not
claim automated pixel recognition or final-reader visual/native-speaker QA.
"""
import ast
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import unittest
import xml.etree.ElementTree as ET
import zipfile

import build_unit


BASE = Path(__file__).resolve().parents[1]
UNIT = "MR-BRIDGE-015"
C = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
KEY = "fs-id1167836597228"
EXERCISES = "fs-id1167836310305"
PRACTICE = "fs-id1167836300671"
WRITING = "fs-id1167836602786"
SELF = "fs-id1167833057322"
PINS = {
    "en": ("downloads/mr-Deva-IN/releases/A20-canonical.zip",
           "osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/",
           "effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917",
           "021c29fa9a6ab3d5b06d2ef143a82d2ac818ed25fe6fd44ebf5d7a6be07a123a"),
    "id": ("downloads/mr-Deva-IN/releases/A20-v0.3.0-source.zip", "source/",
           "a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7",
           "d89a74aef766afca6a4ac7e1ae720f120d22cc771c11dd7e025c55bca1fabb8e"),
}
REVIEWED_XML = "ec72c545cc5d3e34446d2875c48778c69cd51bf631598842f35f1f740bc8865e"
REVIEWED_CONFIG = "dd6b3e480731effcf5c285adbc019bf26941e2ed7aa86a974244c2f289a9f9e0"
REVIEWED_LOCK = "96b15c6573e559e6ed0735aa37ca40da93c565f8fa23d49ead836616a373fc06"
# SHA256 of newline-terminated sorted "locale basename sha256" records,
# en then id. Binds every individual original image, not an altered collage.
REVIEWED_IMAGE_MANIFEST = "73f67ec9eec6d0e0b2fd99a911e3c21a4f1026b4248bc6e41191c1b8e26f4da8"
NUMBERS = tuple(f"{n:03}" for n in (*range(27, 34), *range(201, 220), *range(313, 348, 2)))

# Independently read formulas: (family, coefficient, exponent/radicand shift,
# output shift). Range proofs use the complete family, not finite sampling.
FAMILIES = {
    5: ("power", 3, 1, 4), 6: ("power", 2, 1, 5),
    7: ("power", -1, 1, -2), 8: ("power", -4, 1, -3),
    9: ("power", -2, 1, 2), 10: ("power", -3, 1, 3),
    11: ("power", F(1, 2), 1, 1), 12: ("power", F(2, 3), 1, -2),
    13: ("power", 0, 1, 5), 14: ("power", 0, 1, 2),
    15: ("power", 0, 1, -3), 16: ("power", 0, 1, -1),
    17: ("power", 2, 1, 0), 18: ("power", 3, 1, 0),
    19: ("power", -2, 1, 0), 20: ("power", -3, 1, 0),
    21: ("power", 3, 2, 0), 22: ("power", 2, 2, 0),
    23: ("power", -3, 2, 0), 24: ("power", -2, 2, 0),
    25: ("power", F(1, 2), 2, 0), 26: ("power", F(1, 3), 2, 0),
    27: ("power", 1, 2, -1), 28: ("power", 1, 2, 1),
    29: ("power", -2, 3, 0), 30: ("power", 2, 3, 0),
    31: ("power", 1, 3, 2), 32: ("power", 1, 3, -2),
    33: ("root", 2, 0, 0), 34: ("root", -2, 0, 0),
    35: ("root", 1, -1, 0), 36: ("root", 1, 1, 0),
    37: ("abs", 3, 0, 0), 38: ("abs", -2, 0, 0),
    39: ("abs", 1, 0, 1), 40: ("abs", 1, 0, -1),
}
FORMULA_POINTS = {
    5: [(-2, -2), (-1, 1), (0, 4)],
    7: [(-2, 0), (0, -2), (2, -4)],
    9: [(-2, 6), (0, 2), (1, 0), (2, -2)],
    11: [(-2, 0), (0, 1), (2, 2)],
    13: [(-2, 5), (-1, 5), (0, 5)],
    15: [(0, -3), (1, -3), (2, -3)],
    17: [(-2, -4), (0, 0), (2, 4)],
    19: [(-1, 2), (0, 0), (1, -2)],
    21: [(-1, 3), (0, 0), (1, 3)],
    23: [(-1, -3), (0, 0), (1, -3)],
    25: [(-4, 8), (-2, 2), (0, 0), (2, 2), (4, 8)],
    27: [(-2, 3), (-1, 0), (0, -1), (1, 0), (2, 3)],
    29: [(-1, 2), (0, 0), (1, -2)],
    31: [(-1, 1), (0, 2), (1, 3)],
    33: [(0, 0), (1, 2), (4, 4)],
    35: [(1, 0), (2, 1), (5, 2)],
    37: [(-1, 3), (0, 0), (1, 3)],
    39: [(-1, 2), (0, 1), (1, 2)],
}
OTHER_POINTS = {
    "201": [(-3, 0), (3, 0), (0, -3), (0, 3)],
    "202": [(-2, 6), (-1, 3), (0, 2), (1, 3), (2, 6)],
    "203": [(-1, -1), (0, 0), (1, 1)],
    "204": [(-4, 0), (4, 0), (0, -4), (0, 4)],
    "205": [(-2, 0), (-1, 1), (-1, -1), (2, 2), (2, -2)],
    "206": [(-1, -1), (0, 0), (1, 1)],
    "208": [(0, 2), (1, 3), (2, 4), (1, 1), (2, 0)],
    "209": [(2, 0), (3, 1), (6, 2)],
    "210": [(-3, 0), (-2, 1), (1, 2)],
    "211": [(-2, 6), (0, 4), (2, 6)],
    "212": [(-1, 0), (0, -1), (1, 0)],
    "213": [(-2, 0), (0, 2), (2, 0)],
    "214": [(-3, 3), (0, 6), (3, 3)],
    "217": [(-3, 2), (0, 5), (3, 2)],
    "218": [(-4, 0), (0, 4), (4, 0)],
}
PI_X = tuple(map(F, (-2, F(-3, 2), -1, F(-1, 2), 0, F(1, 2), 1, F(3, 2), 2)))
WAVES = {"215": dict(zip(PI_X, (0, -1, 0, 1, 0, -1, 0, 1, 0))),
         "216": dict(zip(PI_X, (-1, 0, 1, 0, -1, 0, 1, 0, -1)))}


def text(node):
    return "".join(node.itertext()).strip()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key " + key)
            result[key] = value
        return result
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def local(path):
    result = (BASE / path).resolve()
    if not result.is_relative_to(BASE):
        raise ValueError("path outside language tree")
    return result


def image_name(number):
    return f"CNX_IntAlg_Figure_03_06_{number}_img_new.jpg"


def norm(value):
    return re.sub(r"\s+", "", value).replace("−", "-").rstrip(".,")


def structure(node):
    return (node.tag, tuple(sorted(node.attrib.items())), (node.text or "").strip(),
            tuple((structure(n), (n.tail or "").strip()) for n in node))


def math_text(node):
    tag = node.tag.removeprefix(M)
    if tag == "mfrac":
        return "(" + math_text(node[0]) + "/" + math_text(node[1]) + ")"
    if tag == "msup":
        exponent = text(node[1])
        if exponent not in {"2", "3"}:
            raise ValueError("unreviewed exponent")
        return math_text(node[0]) + {"2": "²", "3": "³"}[exponent]
    if tag == "msqrt":
        return "√(" + "".join(map(math_text, node)) + ")"
    if tag == "mfenced":
        separators = re.sub(r"\s", "", node.get("separators", ","))
        children = list(map(math_text, node))
        result = children[0] if children else ""
        for i, child in enumerate(children[1:]):
            result += (separators[min(i, len(separators)-1)] if separators else "") + child
        return node.get("open", "(") + result + node.get("close", ")")
    if tag == "mspace":
        return ""
    if tag not in {"math", "mrow", "mi", "mn", "mo", "mtext", "mtable", "mtr", "mtd"}:
        raise ValueError("unreviewed MathML " + tag)
    return (node.text or "") + "".join(math_text(n)+(n.tail or "") for n in node)


def maths(node):
    return [norm(math_text(n)) for n in node.iter(M + "math")]


def source_content(node):
    """Read mixed prose/MathML without dropping implicit mathematical fences."""
    if node.tag == M+"math":
        return math_text(node)
    if node.tag == C+"media":
        return ""
    return (node.text or "") + "".join(source_content(n)+(n.tail or "") for n in node)


def coefficient(value):
    value = F(value)
    return str(value.numerator) if value.denominator == 1 else f"({value.numerator}/{value.denominator})"


def family_formula(family):
    kind, a, p, b = family
    if a == 0:
        return "f(x)=" + coefficient(b)
    prefix = "" if a == 1 else "-" if a == -1 else coefficient(a)
    if kind == "power":
        body = "x" + {1: "", 2: "²", 3: "³"}[p]
    elif kind == "root":
        body = "√(x" + ("+"+str(p) if p > 0 else str(p) if p else "") + ")"
    elif kind == "abs":
        body = "|x|"
    else:
        raise ValueError("unreviewed family")
    return "f(x)=" + prefix + body + ("+"+str(b) if b > 0 else str(b) if b else "")


def family_domain_range(family):
    kind, a, p, b = family
    domain = f"[{-p},∞)" if kind == "root" else "(-∞,∞)"
    if a == 0:
        return domain, "{" + coefficient(b) + "}"
    if kind == "power" and p % 2:
        return domain, "(-∞,∞)"
    return domain, f"[{b},∞)" if a > 0 else f"(-∞,{b}]"


def on_family(family, x, y):
    kind, a, p, b = family
    x, y = F(x), F(y)
    if kind == "root":
        return x+p >= 0 and (y-b)/a >= 0 and ((y-b)/a)**2 == x+p
    return y == a*(abs(x) if kind == "abs" else x**p)+b


def coordinate_pairs(value):
    pairs = [tuple(map(int, p)) for p in re.findall(r"\((-?\d+),(-?\d+)\)", norm(value))]
    return list(dict.fromkeys(pairs))


def rational(value, pi=False):
    value = norm(value)
    if pi:
        if "π" not in value and value not in {"0", "(0)"}:
            raise ValueError("nonzero pi coefficient without pi")
        if value.count("π") > 1:
            raise ValueError("only a linear pi coefficient is supported")
        value = re.sub(r"(?<=[0-9)])(?=π)", "*", value).replace("π", "p")
    def visit(n):
        if isinstance(n, ast.Constant) and type(n.value) is int:
            return F(n.value)
        if pi and isinstance(n, ast.Name) and n.id == "p":
            return F(1)
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
            return (-1 if isinstance(n.op, ast.USub) else 1)*visit(n.operand)
        if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Mult, ast.Div)):
            left, right = visit(n.left), visit(n.right)
            if isinstance(n.op, ast.Div):
                if any(isinstance(x, ast.Name) for x in ast.walk(n.right)):
                    raise ValueError("pi in denominator")
                return left/right
            return left*right
        raise ValueError("unsafe or unsupported rational expression")
    return visit(ast.parse(value, mode="eval").body)


def call(value, pi=False):
    match = re.fullmatch(r"f\((.+)\)(?:=(.+))?", norm(value))
    if not match:
        raise ValueError("not a function evaluation")
    return rational(match[1], pi), None if match[2] is None else rational(match[2])


def parts(node):
    result, part = {}, None
    for child in node:
        if child.tag == C+"span" and child.get("class") == "token":
            part = chr(ord("a")+ord(text(child))-ord("ⓐ"))
            result[part] = []
        elif child.tag == M+"math":
            if part is None:
                raise ValueError("unlabeled MathML component")
            result[part].append(norm(math_text(child)))
    return result


class Unit15Math(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = local(f"translations/{UNIT}.xml").read_bytes()
        cls.root = ET.fromstring(cls.raw)
        cls.ids = {n.get("id"): n for n in cls.root.iter() if n.get("id")}
        cls.config = read_json(local(f"units/{UNIT}.json"))
        cls.checks = {n.get("data-check"): text(n) for n in cls.root.iter() if n.get("data-check")}
        cls.q = [n for n in cls.root.iter("section") if n.find("h4") is not None]
        cls.modules, cls.sources, cls.images, cls.sq = {}, {}, {}, {}
        for locale, (archive, prefix, _, module_hash) in PINS.items():
            with zipfile.ZipFile(BASE.parent/archive) as z:
                raw = z.read(prefix+"modules/m81374/index.cnxml")
                if sha(raw) != module_hash:
                    raise ValueError("pinned module hash mismatch")
                module = ET.fromstring(raw)
                cls.modules[locale] = module
                selected = [n for n in module.iter() if n.get("id") in {KEY, EXERCISES}]
                cls.sources[locale] = {n.get("id"): n for s in selected for n in s.iter() if n.get("id")}
                cls.sq[locale] = list(selected[1].iter(C+"exercise"))
                for number in NUMBERS:
                    cls.images[locale, number] = z.read(prefix+"media/"+image_name(number))
        cls.figures = {n.find("img").get("src").split("_")[5]: n for n in cls.root.iter("figure")}

    def test_01_complete_source_boundary_and_63_selectors(self):
        target = [n.get("data-source") for n in self.root.iter() if n.get("data-source")]
        for locale, source in self.sources.items():
            expected = [KEY] + [n.get("id") for n in list(source[PRACTICE])[1:]]
            expected += [n.get("id") for n in list(source[WRITING])[1:]] + [SELF]
            self.assertEqual(len(expected), 63)
            self.assertEqual(target, ["A20:m81374#"+sid for sid in expected])
            content = self.modules[locale].find(C+"content")
            roots = [n.get("id") for n in content]
            index = roots.index(KEY)
            self.assertEqual(roots[index-1:index+4], ["fs-id1167836386547", KEY, EXERCISES,
                                                    "fs-id1167836524742", "fs-id1167836628671"])
            self.assertEqual([n.get("id") for n in source[EXERCISES] if n.tag == C+"section"],
                             [PRACTICE, WRITING, SELF])
        for sid in (EXERCISES, PRACTICE, WRITING):
            self.assertNotIn("data-source", self.ids[sid].attrib)

    def test_02_268_original_ids_order_and_all_ancestry(self):
        target = [n.get("id") for n in self.root.iter() if n.get("id")]
        self.assertEqual(len(target), 271)
        self.assertEqual(len(set(target)), 271)
        for source in self.sources.values():
            self.assertEqual(len(source), 268)
            self.assertEqual([sid for sid in target if sid in source], list(source))
            self.assertEqual(set(target)-set(source), {UNIT, UNIT+"-self-rating", "credits"})
            for sid, node in source.items():
                self.assertEqual({n.get("id") for n in node.iter() if n.get("id")},
                                 {n.get("id") for n in self.ids[sid].iter()} & set(source), sid)

    def test_03_classification_54_questions_25_supplied_29_missing(self):
        expected = dict(source_count=63, translated_worked_examples=0, translated_definitions=0,
                        translated_practice_items=54, translated_resource_notes=0, original_practice_items=0)
        self.assertEqual({k: self.config[k] for k in expected}, expected)
        self.assertEqual(self.config["question_ids"], [])
        self.assertEqual(len(self.q), 54)
        supplied = set(range(1, 50, 2))
        for locale, questions in self.sq.items():
            self.assertEqual(len(questions), 54)
            self.assertEqual({i for i, n in enumerate(questions, 1) if n.find(C+"solution") is not None}, supplied)
        for i, q in enumerate(self.q, 1):
            self.assertEqual(text(q.find("h4")), f"प्रश्न {i}")
            solutions = [n for n in q.iter() if n.get("class") == "solution"]
            self.assertEqual(len(solutions), int(i in supplied))
            if i not in supplied:
                missing = [n for n in q.findall("p") if "उत्तर दिलेले नाही" in text(n)]
                self.assertEqual(len(missing), 1)
                self.assertEqual(missing[0].get("data-kind"), "original")
            else:
                self.assertIn("स्रोतातील उत्तर", text(solutions[0]))
                self.assertNotIn("उत्तर दिलेले नाही", text(q))

    def test_04_all_question_subparts_and_inherited_instructions(self):
        self.assertIn("(a)", text(self.ids["fs-id1167836356048"]))
        self.assertIn("(b)", text(self.ids["fs-id1167836356048"]))
        self.assertIn("प्रांत आणि मूल्यसंच", text(self.ids["fs-id1167836579171"]))
        self.assertEqual(4*2 + 36*2 + 6*2 + 8+8+8+6, 122)
        for locale, questions in self.sq.items():
            for number in range(1, 5):
                problem = questions[number-1].find(C+"problem")
                self.assertEqual([text(n) for n in problem.iter(C+"span")], ["ⓐ", "ⓑ"])
            for number, letters in ((47, "abcdefgh"), (48, "abcdefgh"), (49, "abcdefgh"), (50, "abcdef")):
                para = questions[number-1].find(C+"problem").find(C+"para")
                self.assertEqual(list(parts(para)), list(letters))
                self.assertEqual(re.findall(r"\(([a-h])\)", text(self.ids[para.get("id")])), list(letters))
        for number, term in ((51, "प्रांत"), (52, "मूल्यसंच"), (53, "उभ्या रेषेची कसोटी")):
            self.assertIn(term, text(self.q[number-1]))
            self.assertIn("स्वतःच्या शब्दांत", text(self.q[number-1]))
        self.assertIn("साम्ये", text(self.q[53]))
        self.assertIn("फरक", text(self.q[53]))

    def test_05_all_71_exercise_mathml_trees_have_locale_parity(self):
        values = [[structure(n) for n in source[EXERCISES].iter(M+"math")] for source in self.sources.values()]
        self.assertEqual(len(values[0]), 71)
        self.assertEqual(values[0], values[1])
        # All constructors, including implicit mfenced delimiters, are visited.
        for source in self.sources.values():
            self.assertEqual(len(maths(source[KEY])), 4)
            for value in maths(source[EXERCISES]):
                self.assertTrue(value)

    def test_06_all_36_formulas_match_source_and_independent_families(self):
        for number, family in FAMILIES.items():
            expected = family_formula(family)
            self.assertEqual(norm(self.checks[f"q{number}-function"]), expected)
            for questions in self.sq.values():
                self.assertEqual(maths(questions[number-1].find(C+"problem")), [expected])

    def test_07_all_18_formula_solution_domains_ranges_and_graph_points(self):
        for number, observed in FORMULA_POINTS.items():
            family = FAMILIES[number]
            domain, result = family_domain_range(family)
            self.assertEqual(norm(self.checks[f"q{number}-domain"]), domain)
            self.assertEqual(norm(self.checks[f"q{number}-range"]), result)
            for questions in self.sq.values():
                answer = norm(source_content(questions[number-1].find(C+"solution")))
                self.assertEqual(answer.count("ⓐ"), 1)
                self.assertEqual(answer.count("ⓑ"), 1)
                actual = answer.split("ⓑ")[1]
                if actual.startswith("D:"):
                    actual = actual[2:]
                self.assertEqual(actual.split(",R:"), [domain, result])
            figure = self.q[number-1].find(".//figure")
            self.assertEqual(coordinate_pairs(figure.find("img").get("alt")), observed)
            for point in observed:
                self.assertTrue(on_family(family, *point), (number, point))

    def test_08_recap33_entries_and_explicit_linear_constant_corrections(self):
        expected = {
            "summary-pair": "(x,y)", "summary-function-pair": "(x,f(x))", "summary-value": "y=f(x)",
            "summary-name": "f", "summary-input": "x", "summary-output": "f(x)",
            "linear-form": "f(x)=mx+b", "linear-domain": "(-∞,∞)", "linear-source-range": "(-∞,∞)",
            "linear-nonzero": "m≠0", "linear-zero": "m=0", "linear-constant-range": "{b}",
            "constant-form": "f(x)=b", "constant-domain": "(-∞,∞)", "constant-source-range": "b",
            "constant-range": "{b}", "identity-form": "f(x)=x", "identity-slope": "m=1", "identity-intercept": "b=0",
            "identity-domain": "(-∞,∞)", "identity-range": "(-∞,∞)", "square-form": "f(x)=x²",
            "square-domain": "(-∞,∞)", "square-range": "[0,∞)", "cube-form": "f(x)=x³",
            "cube-domain": "(-∞,∞)", "cube-range": "(-∞,∞)", "root-form": "f(x)=√x",
            "root-domain": "[0,∞)", "root-range": "[0,∞)", "absolute-form": "f(x)=|x|",
            "absolute-domain": "(-∞,∞)", "absolute-range": "[0,∞)",
        }
        self.assertEqual(len(expected), 33)
        self.assertEqual({k: norm(self.checks[k]) for k in expected}, expected)
        for source in self.sources.values():
            self.assertEqual(maths(source[KEY])[:3], ["(x,y)", "(x,f(x))", "y=f(x)"])
        additions = " ".join(text(n) for n in self.ids[KEY].iter() if n.get("data-kind") == "original")
        for phrase in ("स्रोत-दुरुस्ती", "इंडोनेशियन", "एका घटकाचा संच", "(0, b)", "[b, b]"):
            self.assertIn(phrase, additions)
        self.assertNotIn("m ≠ 0", self.sources["en"]["fs-id1167833240439"].get("alt"))
        self.assertIn("m ≠ 0", self.sources["id"]["fs-id1167833240439"].get("alt"))
        self.assertIn("Range: b", self.sources["en"]["fs-id1167836699152"].get("alt"))
        self.assertIn("{b}", self.sources["id"]["fs-id1167836699152"].get("alt"))
        # All-real range of mx+b follows from solving x=(y-b)/m when m!=0;
        # when m=0 every x maps to b, hence precisely the singleton {b}.
        for m in (-3, F(1, 2), 7):
            for b in (-4, 0, 9):
                for y in (-11, F(2, 3), 20):
                    self.assertEqual(m*((F(y)-b)/m)+b, y)

    def test_09_vertical_test_answers_and_pixel_counterexamples(self):
        for number in (1, 3):
            solution = self.q[number-1].find(".//div[@class='solution']/p")
            self.assertEqual(text(solution), "(a) नाही. (b) होय.")
            for locale, questions in self.sq.items():
                answer = norm(text(questions[number-1].find(C+"solution")))
                self.assertEqual(answer, "ⓐnoⓑyes" if locale == "en" else "ⓐtidakⓑya")
        for image in ("201", "205"):
            coords = OTHER_POINTS[image]
            self.assertTrue(any(x == u and y != v for x, y in coords for u, v in coords))
        for number in (2, 4):
            self.assertIsNone(self.q[number-1].find(".//div[@class='solution']"))
        self.assertIn("जास्तीत जास्त एका", text(self.ids[KEY]))
        self.assertIn("एकापेक्षा जास्त", text(self.ids[KEY]))

    def test_10_three_graph_only_supplied_domain_range_pairs(self):
        expected = {41: ("[2,∞)", "[0,∞)"), 43: ("(-∞,∞)", "[4,∞)"),
                    45: ("[-2,2]", "[0,2]")}
        for number, pair in expected.items():
            self.assertEqual(tuple(norm(self.checks[f"q{number}-{k}"]) for k in ("domain", "range")), pair)
            for questions in self.sq.values():
                para = questions[number-1].find(C+"solution").find(C+"para")
                value = norm(text(para))
                self.assertEqual(value.removeprefix("D:").split(",R:"), list(pair))

    def test_11_all_wave_nodes_and_question_inputs(self):
        for number, image, xs in ((47, "215", (0, F(1, 2), F(-3, 2))),
                                  (48, "216", (0, 1, -1))):
            alt = norm(self.figures[image].find("img").get("alt"))
            pairs = re.findall(r"\(([^,()]+),([^,()]+)\)", alt)
            self.assertEqual([(rational(x, True), rational(y)) for x, y in pairs], list(WAVES[image].items()))
            for index, x in enumerate(xs, 1):
                self.assertEqual(call(self.checks[f"q{number}-input-{index}"], True), (x, None))
            for locale, questions in self.sq.items():
                para = questions[number-1].find(C+"problem").find(C+"para")
                entries = parts(para)
                self.assertEqual([call(entries[p][0], True) for p in "abc"], [(x, None) for x in xs])
                self.assertEqual(entries["d"], ["f(x)=0"])
                source_alt = questions[number-1].find(".//"+C+"media").get("alt")
                self.assertIn("The pattern extends infinitely" if locale == "en" else "Pola ini memanjang", source_alt)
            self.assertEqual(norm(self.checks[f"q{number}-zeros-question"]), "f(x)=0")

    def test_12_all_eight_q47_answers_and_conditional_global_extension(self):
        expected = {"a": (F(0), 0), "b": (F(1, 2), -1), "c": (F(-3, 2), -1)}
        for part, pair in expected.items():
            self.assertEqual(call(self.checks["q47-answer-"+part], True), pair)
            self.assertEqual(WAVES["215"][pair[0]], pair[1])
        zeros = [x for x, y in WAVES["215"].items() if not y]
        self.assertEqual([rational(x, True) for x in norm(self.checks["q47-answer-d"]).removeprefix("x=").split(",")], zeros)
        points = re.findall(r"\(([^,()]+),([^,()]+)\)", norm(self.checks["q47-answer-e"]))
        self.assertEqual([(rational(x, True), rational(y)) for x, y in points], [(x, 0) for x in zeros])
        for key, value in {"f": "(0,0)", "g": "(-∞,∞)", "h": "[-1,1]"}.items():
            self.assertEqual(norm(self.checks["q47-answer-"+key]), value)
        for questions in self.sq.values():
            entries = parts(questions[46].find(C+"solution").find(C+"para"))
            for part, pair in expected.items():
                self.assertEqual(call(entries[part][0], True), pair)
            self.assertEqual(",".join(entries["e"]), norm(self.checks["q47-answer-e"]))
            for part in "dfgh":
                self.assertEqual(entries[part][-1], norm(self.checks["q47-answer-"+part]))
        self.assertEqual(norm(self.checks["q47-source-window"]), "[-2π,2π]")
        self.assertEqual(norm(self.checks["q47-all-zeros"]), "x=nπ,n∈ℤ")
        self.assertEqual(norm(self.checks["q47-all-intercepts"]), "(nπ,0),n∈ℤ")
        extension = next(n for n in self.q[46].iter("p") if n.get("data-kind") == "original")
        for phrase in ("स्रोताच्या वर्णनानुसार", "त्या सांगितलेल्या विस्तारात", "स्वतंत्र जोडलेली नोंद", "केवळ काही बिंदू"):
            self.assertIn(phrase, text(extension))
        self.assertEqual(zeros, [F(n) for n in range(-2, 3)])

    def test_13_q49_semicircle_all_answers_and_q50_six_parts(self):
        expected = {"a": "5", "b": "2", "c": "2", "d": "f(x)=0", "f": "(0,5)", "g": "[-3,3]", "h": "[2,5]"}
        self.assertEqual({k: norm(self.checks["q49-answer-"+k]) for k in expected}, expected)
        for questions in self.sq.values():
            entries = parts(questions[48].find(C+"solution").find(C+"para"))
            for k in expected:
                self.assertEqual(entries[k], [expected[k]])
            for number, inputs in ((49, (0, -3, 3)), (50, (0,))):
                problem = parts(questions[number-1].find(C+"problem").find(C+"para"))
                self.assertEqual([call(problem[p][0]) for p in "abc"[:len(inputs)]], [(x, None) for x in inputs])
        # Upper circle centred at (0,2), radius 3: y=2+sqrt(9-x*x).
        # Exact endpoint/maximum checks plus the nonnegative-root bound give
        # the entire closed range [2,5], hence no possible zero/x-intercept.
        for x, y in OTHER_POINTS["217"]:
            self.assertGreaterEqual(y, 2)
            self.assertEqual(F(x)**2+(F(y)-2)**2, 9)
        self.assertIn("कोणत्याही x साठी", text(self.q[48]))
        self.assertIn("असे छेदबिंदू नाहीत", text(self.q[48]))
        for i, x in enumerate((0, -3, 3), 1):
            self.assertEqual(call(self.checks[f"q49-input-{i}"]), (x, None))
        self.assertEqual(call(self.checks["q50-input-1"]), (0, None))
        for number in (49, 50):
            self.assertEqual(norm(self.checks[f"q{number}-zeros-question"]), "f(x)=0")

    def test_14_all_caption_coordinates_and_axis_windows(self):
        for number, expected in OTHER_POINTS.items():
            self.assertEqual(coordinate_pairs(self.figures[number].find("img").get("alt")), expected)
        for number in range(201, 209):
            self.assertIn("दोन्ही अक्षांवर −8 ते 8", self.figures[str(number)].find("img").get("alt"))
        # Explicit bounds are the displayed grid, never the domain/range.
        bounds = {"209": (-2, 12, -2, 8), "210": (-4, 10, -2, 8), "211": (-6, 6, -2, 12),
                  "212": (-6, 6, -2, 10), "214": (-6, 6, -2, 10), "217": (-6, 6, -2, 10),
                  "218": (-6, 6, -2, 10), "329": (-8, 8, -2, 10), "331": (-8, 8, -10, 2),
                  "333": (-8, 8, -2, 10), "335": (-8, 8, -2, 10), "341": (-2, 10, -2, 8),
                  "343": (-2, 10, -2, 8), "345": (-8, 8, -2, 10), "347": (-8, 8, -2, 10)}
        for number, observed in bounds.items():
            alt = self.figures[number].find("img").get("alt").replace("−", "-")
            found = re.search(r"x=(-?\d+) ते (-?\d+), y=(-?\d+) ते (-?\d+)", alt)
            self.assertIsNotNone(found, number)
            self.assertEqual(tuple(map(int, found.groups())), observed)
        for number, figure in self.figures.items():
            if int(number) >= 201 and number != "219":
                self.assertEqual(text(figure.find("figcaption")), "मूळ आकृती "+number+". "+figure.find("img").get("alt"))
                self.assertEqual(figure.find("figcaption").get("data-kind"), "original")
        self.assertIn("जवळून", self.figures["207"].find("img").get("alt"))
        self.assertIn("चौकटीच्या बाहेर", self.figures["031"].find("img").get("alt"))

    def test_15_source_correction_notes_not_silent_formula_changes(self):
        for number, required in ((1, ("दोनदा", "(−1, 3)")), (2, ("(−1, 1)", "(−1, −1)")),
                                 (3, ("(−2, 2)", "(2, −2)")), (4, ("V-आकार", "ठरवायचे")),
                                 (9, ("−2x − 2", "−2x + 2", "चित्र बदललेले नाही"))):
            original = " ".join(text(n) for n in self.q[number-1].iter("p") if n.get("data-kind") == "original")
            for phrase in required:
                self.assertIn(phrase, original)
        for locale, questions in self.sq.items():
            alt = questions[8].find(".//"+C+"media").get("alt")
            self.assertIn("negative 2" if locale == "en" else "negatif 2", alt)
        self.assertIn("23, 25, 27", text(self.root))

    def test_16_nine_empty_self_rating_cells_and_instructions(self):
        table = self.ids[UNIT+"-self-rating"]
        self.assertEqual(table.get("data-kind"), "adaptation")
        rows = table.findall("tbody/tr")
        self.assertEqual(len(rows), 3)
        self.assertEqual(len(table.findall("thead/tr/th")), 4)
        cells = table.findall("tbody/tr/td")
        self.assertEqual(len(cells), 9)
        for cell in cells:
            self.assertEqual(text(cell), "")
            self.assertEqual(list(cell), [])
            self.assertEqual(cell.attrib, {})
        self.assertIn("सर्व नऊ चौकटी रिकाम्या", self.figures["219"].find("img").get("alt"))
        for sid, label in (("fs-id1167829599017", "(a)"), ("fs-id1167836729385", "(b)")):
            self.assertTrue(text(self.ids[sid]).startswith(label))

    def test_17_all_143_math_keys_are_semantically_covered_and_config_exact(self):
        recap = {k for k in self.checks if not k.startswith("q")}
        formula = {f"q{i}-function" for i in range(5, 41)}
        ranges = {f"q{i}-{k}" for i in (*range(5, 40, 2), 41, 43, 45) for k in ("domain", "range")}
        graph = {f"q{i}-input-{j}" for i in (47, 48, 49) for j in (1, 2, 3)}
        graph |= {f"q{i}-zeros-question" for i in (47, 48, 49, 50)} | {"q50-input-1"}
        graph |= {"q47-answer-"+p for p in "abcdefgh"} | {"q49-answer-"+p for p in "abcdfgh"}
        graph |= {"q47-source-window", "q47-all-zeros", "q47-all-intercepts"}
        self.assertEqual((len(recap), len(formula), len(ranges), len(graph)), (33, 36, 42, 32))
        self.assertEqual(set(self.checks), recap | formula | ranges | graph)
        self.assertEqual(len([n for n in self.root.iter() if n.get("data-check")]), 143)
        self.assertEqual(self.checks, self.config["expected_math"])

    def test_18_88_original_bytes_44_assets_and_review_manifest(self):
        rows, unequal = [], []
        self.assertEqual(len(self.figures), 44)
        self.assertEqual(set(self.config["assets"]), {image_name(n) for n in NUMBERS})
        for locale in ("en", "id"):
            for number in NUMBERS:
                raw = self.images[locale, number]
                rows.append(f"{locale} {image_name(number)} {sha(raw)}")
                review = BASE.parent/"downloads/mr-Deva-IN/source-image-qa"/UNIT/(locale+"-"+image_name(number))
                self.assertEqual(review.read_bytes(), raw)
                self.assertTrue(raw.startswith(b"\xff\xd8\xff"))
                if locale == "en":
                    entry = self.config["assets"][image_name(number)]
                    self.assertEqual(entry["mime"], "image/jpeg")
                    self.assertEqual(entry["sha256"], sha(raw))
                    self.assertEqual(local(entry["path"]).read_bytes(), raw)
                    if raw != self.images["id", number]:
                        unequal.append(number)
        self.assertEqual(sha(("\n".join(rows)+"\n").encode()), REVIEWED_IMAGE_MANIFEST)
        self.assertEqual(unequal, [*map(lambda n: f"{n:03}", range(27, 34)), "219"])
        self.assertEqual(sum(len(self.images["en", n]) for n in NUMBERS), 2694271)
        self.assertEqual(sum(len(self.images["id", n]) for n in NUMBERS), 2606257)

    def test_19_all_25_forward_return_pairs_and_62_links(self):
        links = [n.get("href") for n in self.root.iter("a")]
        internal = [s for s in links if s.startswith("#")]
        external = [s for s in links if s.startswith("https://")]
        self.assertEqual((len(internal), len(external), len(links)), (55, 7, 62))
        self.assertTrue(all(s[1:] in self.ids for s in internal))
        for source in self.sources.values():
            self.assertFalse(any(n.tag == C+"link" for s in (KEY, EXERCISES) for n in source[s].iter()))
        for q in self.sq["en"]:
            answer = q.find(C+"solution")
            if answer is not None:
                problem = q.find(C+"problem")
                qid, aid = problem.get("id"), answer.get("id")
                self.assertIn("#"+aid, [n.get("href") for n in self.ids[qid].iter("a")])
                self.assertIn("#"+qid, [n.get("href") for n in self.ids[aid].iter("a")])
        self.assertEqual(set(external), {
            "https://creativecommons.org/licenses/by-nc-sa/4.0/", "https://marathivishwakosh.org/21979/",
            *[f"https://vishwakosh.marathi.gov.in/{n}/" for n in (24316, 27548, 21279, 21277, 32824)]})

    def test_20_markup_unicode_license_and_honest_review_boundaries(self):
        self.assertEqual(self.root.get("id"), UNIT)
        self.assertEqual(self.root.get("lang"), "mr-Deva-IN")
        self.assertEqual(unicodedata.normalize("NFC", self.raw.decode()), self.raw.decode())
        self.assertNotIn("\ufffd", self.raw.decode())
        for term in self.config["required_terms"]:
            self.assertIn(term, text(self.root))
        build_unit.validate_markup(self.root, self.config["assets"])
        footer = text(self.ids["credits"])
        for phrase in ("CC BY-NC-SA 4.0", "Lynn Marecek", "Andrea Honeycutt Mathis", "तृतीय-पक्षांच्या",
                       "प्रशिक्षण", "29", "268", "HTML/PDF", "पूर्ण झाल्याचे मानू नये"):
            self.assertIn(phrase, footer)

    def test_21_exact_126_source_fragments_88_media_and_179_witnesses(self):
        lock = read_json(local(f"provenance/{UNIT}.lock.json"))
        self.assertEqual(len(lock["source_selections"]), 63)
        for selection in lock["source_selections"]:
            self.assertEqual(selection["locator"], "A20:m81374#"+selection["target_id"])
            self.assertEqual([n["locale"] for n in selection["sources"]], ["en", "id"])
            for entry in selection["sources"]:
                locale = entry["locale"]
                archive, prefix, archive_sha, module_sha = PINS[locale]
                self.assertEqual((entry["archive"], entry["archive_sha256"], entry["member"], entry["module_sha256"]),
                                 (archive, archive_sha, prefix+"modules/m81374/index.cnxml", module_sha))
                raw = local(entry["fragment_path"]).read_bytes()
                self.assertEqual(sha(raw), entry["fragment_sha256"])
                self.assertEqual(structure(ET.fromstring(raw)), structure(self.sources[locale][selection["target_id"]]))
                self.assertEqual(entry["outgoing_urls"], [])
        self.assertEqual(len(lock["source_images"]), 88)
        for entry in lock["source_images"]:
            number = entry["member"].split("_")[-3]
            raw = self.images[entry["locale"], number]
            self.assertEqual((entry["bytes"], entry["sha256"]), (len(raw), sha(raw)))
        self.assertEqual(len(lock["witnesses"]), 179)
        for witness in lock["witnesses"]:
            raw = local(witness["path"]).read_bytes()
            self.assertEqual((len(raw), sha(raw)), (witness["bytes"], witness["sha256"]), witness["path"])

    def test_22_current_structural_receipt_only_not_reader_acceptance(self):
        receipt = read_json(local(f"qa/{UNIT}-build-receipt.json"))
        self.assertEqual(sha(self.raw), REVIEWED_XML)
        self.assertEqual(sha(local(f"units/{UNIT}.json").read_bytes()), REVIEWED_CONFIG)
        self.assertEqual(sha(local(f"provenance/{UNIT}.lock.json").read_bytes()), REVIEWED_LOCK)
        self.assertEqual((receipt["source_sha256"], receipt["config_sha256"], receipt["provenance_lock_sha256"]),
                         (REVIEWED_XML, REVIEWED_CONFIG, REVIEWED_LOCK))
        self.assertEqual(receipt["result"], "PASS")
        # HTML is read as opaque bytes for currency only, never converted,
        # parsed, loaded in a browser, or treated as inspected reader geometry.
        self.assertEqual(sha(local(f"output/{UNIT}.html").read_bytes()), receipt["html_sha256"])
        for style in receipt["stylesheet_files"]:
            self.assertEqual(sha(local(style["path"]).read_bytes()), style["sha256"])
        self.assertEqual(tuple(receipt[k] for k in ("selected_source_blocks", "unique_ids", "displayed_math_regressions",
                                                   "embedded_image_count", "pinned_witnesses_checked")),
                         (63, 271, 143, 44, 179))
        self.assertIn("visual browser QA", receipt["not_claimed"])

    def test_23_parser_regressions_and_rejection(self):
        fenced = ET.fromstring(f'<mfenced xmlns="{M[1:-1]}"><mn>0</mn><mn>5</mn></mfenced>')
        self.assertEqual(math_text(fenced), "(0,5)")
        self.assertEqual(rational("-(3/2)π", True), F(-3, 2))
        self.assertEqual(rational("(-3π/2)", True), F(-3, 2))
        for unsafe in ("__import__('os')", "x", "1+1", "2**100", "π/π"):
            with self.assertRaises((ValueError, SyntaxError)):
                rational(unsafe, True)
        with self.assertRaises(ValueError):
            math_text(ET.fromstring(f'<mroot xmlns="{M[1:-1]}"><mn>1</mn><mn>3</mn></mroot>'))


if __name__ == "__main__":
    unittest.main(verbosity=2)
