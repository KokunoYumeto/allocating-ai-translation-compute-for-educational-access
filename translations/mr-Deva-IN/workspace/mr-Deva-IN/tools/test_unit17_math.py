"""MR017 independent source/math regression; no browser or reader acceptance.

Reads real frozen files and narrowly selected members of the existing EN/ID ZIPs.
Exact Fraction polynomials are interpreted through a whitelisted AST, never eval.
Manual original-pixel observations are bound by hashes, not automated vision.
No downloads, extraction, corpus copies, output files, third-party dependencies,
or skipped tests. Run: python -B mr-Deva-IN/tools/test_unit17_math.py
"""

import ast
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import re
import unittest
import unicodedata
import xml.etree.ElementTree as ET
import zipfile


BASE = Path(__file__).resolve().parents[1]
WORKSPACE = BASE.parent
UNIT = "MR-BRIDGE-017"
C = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
CHAPTER = "fs-id1167836524742"
TOPIC = "fs-id1167829740806"
PREVIOUS = "fs-id1167824674139"
FOLLOWING = "fs-id1167836526512"
PREFIX, SUFFIX = "CNX_IntAlg_Figure_03_06_", "_img_new.jpg"
PINS = {
    "translations/MR-BRIDGE-017.xml": (43757, "f868cd613b00687a133ad6ede745749a3d78d0a7ac1e4fb4d700a9bf6b38cbf1"),
    "units/MR-BRIDGE-017.json": (4955, "48f84cca5607f9faa224a85c877b4af6e713bc2c6e0452adb39db5521a37d860"),
    "provenance/MR-BRIDGE-017.lock.json": (138123, "9b71760ec987da9622e6a55b3737b2a2da34d58e26a41e4ef0d98084f5c70c6b"),
}
ARCHIVES = {
    "en": ("A20-canonical.zip", "osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9",
           "effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917"),
    "id": ("A20-v0.3.0-source.zip", "source",
           "a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7"),
}
MODULE_PINS = {
    ("en", "m81374"): (247327, "021c29fa9a6ab3d5b06d2ef143a82d2ac818ed25fe6fd44ebf5d7a6be07a123a"),
    ("id", "m81374"): (247303, "d89a74aef766afca6a4ac7e1ae720f120d22cc771c11dd7e025c55bca1fabb8e"),
    ("en", "m81370"): (192242, "12157ddd00dae98c6c2cbddec512297110ec945d2a1e0bed207e1801ffab8ad4"),
    ("id", "m81370"): (191468, "86758280beefdbe4041ced71dd062697766d0609bc340b54eb07381a90d9edcd"),
}
INVENTORIES = {
    "fragments": "bc50b4c95fef0c69bc8f135d1827402c559d6bdde8356333c0511d9cf4d6aae6",
    "images": "d8c819b6640d82a3bf1c360b8e6a55645f7453f556dea7b277697da19ff698a1",
    "math": "2d811adf166d90fadd0bd0bdbcd30f6dea6ffca645825aca703a765208617c33",
    "witnesses": "e39cd30ffa0ca1c8a7312de470d1fa6ceb811ce3f0778d58f996646ef674a380",
}
# Question, source role, bytes, SHA-256 of EACH personally viewed EN/ID original.
IMAGES = {
    222: (1, "problem", 90732, "2df8fb519799cfdabec17cbbd4cd6da2cff9f30aa8d04772760d37e3a6b0780f"),
    223: (2, "problem", 91810, "74a804ccfcf03720c6785db1af2d3cc6bf540a937839ec195c32878d8334081a"),
    224: (3, "problem", 92004, "d8f927e1f4324f8281f0b68453d136e2ebccaa17eb4b6439f86c0d2be37fcce4"),
    225: (4, "problem", 93091, "be8232235bb72764d434e62fdfdbbc26b918f78f7fdf2a8565125caa8afe36b6"),
    368: (14, "solution", 61222, "c47373c3a1e7e840cef847920b3712e26839b95023d8596ace858f74b7779fd1"),
    370: (16, "solution", 64824, "9777a5ef85b6ca1b23c207713aca7002161e239f9ecd8386a94cd090118cadba"),
    372: (22, "solution", 76137, "c2bd6537d15b04a006a3fb54b964ecec1c1786249a9259890ffb4021da77a5fa"),
    374: (24, "solution", 77308, "ba1128cfbdadf82ecb11f8c9117deae187ce484b4cf3fd1422df8d3ed3bc6062"),
    376: (32, "solution", 59957, "23cc633bcd3f8e86c6fb1d66c7ad7057bf56e6da40ce81c1aa6d5bfc74a1a985"),
}
GRAPH_POINTS = {
    222: ((0, 0), (1, -3)), 223: ((-4, 0), (0, 4)),
    224: ((-4, -4), (2, -2)), 225: ((1, 4), (5, 2)),
    368: ((-3, 4), (0, 3)), 370: ((0, 1), (4, -2)),
    372: ((0, -1), (1, -2)), 374: ((0, -4), (3, 0)),
    376: ((0, -250), (20, 450)),
}
GRAPH_SLOPES = dict(zip(IMAGES, [-3, 1, F(1, 3), F(-1, 2), F(-1, 3), F(-3, 4), -1, F(4, 3), 35]))
QUESTION_MATH = {
    1: [], 2: [], 3: [], 4: [],
    5: ["y=2"], 6: ["x=5"], 7: ["x=-3"], 8: ["y=-1"],
    9: ["(-1,-1),(0,5)"], 10: ["(3,5),(4,-1)"],
    11: ["(-5,-2),(3,2)"], 12: ["(2,1),(4,6)"],
    13: ["(2,-2);", "m=5/2"], 14: ["(-3,4);", "m=-1/3"],
    15: ["-4", "m=3"], 16: ["1", "m=-3/4"],
    17: ["y=-4x+9"], 18: ["y=5/3x-6"], 19: ["5x+y=10"], 20: ["4x-5y=8"],
    21: ["y=2x+3"], 22: ["y=-x-1"], 23: ["y=-2/5x+3"], 24: ["4x-3y=12"],
    25: ["x=5"], 26: ["y=-3"], 27: ["2x+y=5"], 28: ["x-y=2"],
    29: ["y=2/2x+2"], 30: ["y=3/4x-1"],
    31: ["C=6.5m+42", "14"], 32: ["P=35s-250", "20"],
    33: ["4x-3y=-1;y=4/3x-3"], 34: ["y=5x-1;10x+2y=0"],
    35: ["3x-2y=5;2x+3y=6"], 36: ["2x-y=8;x-2y=4"],
}
# All 41 source MathML nodes map by original paragraph identity, with these
# explicit exceptions; nine additional target spans represent source plain text
# or the two clearly original introductory formulas.
SPECIAL_KEYS = {
    ("fs-id1167836557402", 1): "q15-x-intercept",
    ("fs-id1167836557402", 2): "q15-slope",
    ("fs-id1167829693217", 1): "q16-slope",
    ("fs-id1167836717304", 1): "q31-model",
    ("fs-id1167829694607", 1): "q32-model",
    ("fs-id1167830123746", 1): "q32-answer-a",
}
EXTRA_KEYS = {
    "slope-form", "intercept-point", "q2-answer", "q8-answer",
    "q16-y-intercept", "q31-meals", "q32-lessons",
    "q32-answer-b", "q32-answer-slope",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def inventory(rows):
    return sha(("\n".join(sorted(rows)) + "\n").encode("utf-8"))


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def inside(base, relative):
    target = (base / relative).resolve()
    if base.resolve() not in target.parents:
        raise ValueError("path is not a file below the expected base")
    return target


def text(node):
    return "".join(node.itertext())


def by_id(root):
    return {e.get("id"): e for e in root.iter() if e.get("id")}


def parents(root):
    return {child: parent for parent in root.iter() for child in parent}


def nearest(node, mapping, allowed):
    while node in mapping:
        node = mapping[node]
        if node.get("id") in allowed:
            return node.get("id")
    return None


def shape(node):
    return (node.tag, tuple(sorted(node.attrib.items())), node.text,
            tuple((shape(child), child.tail) for child in node))


def norm(value):
    return re.sub(r"\s+", "", value.replace("−", "-").replace("·", "*"))


def clean(poly):
    return {key: value for key, value in poly.items() if value}


def add(left, right, sign=1):
    result = dict(left)
    for key, value in right.items():
        result[key] = result.get(key, F(0)) + sign * value
    return clean(result)


def multiply(left, right):
    result = {}
    for a, x in left.items():
        for b, y in right.items():
            key = tuple(sorted(a + b))
            result[key] = result.get(key, F(0)) + x * y
    return clean(result)


def polynomial(value):
    """Whitelist arithmetic only; monomials are tuples of variable symbols."""
    value = norm(value)
    tokens = re.findall(r"\d+(?:\.\d+)?|[xymbCPs()+*/-]", value)
    if not value or "".join(tokens) != value:
        raise ValueError("unsupported token")
    explicit = []
    for token in tokens:
        if explicit:
            before = explicit[-1]
            left_atom = before == ")" or bool(re.fullmatch(r"\d+(?:\.\d+)?|[xymbCPs]", before))
            right_atom = token == "(" or bool(re.fullmatch(r"\d+(?:\.\d+)?|[xymbCPs]", token))
            if left_atom and right_atom:
                explicit.append("*")
        explicit.append(token)
    code = "".join(explicit)
    try:
        tree = ast.parse(code, mode="eval")
    except SyntaxError as exc:
        raise ValueError("malformed expression") from exc

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in {int, float}:
            return clean({(): F(ast.get_source_segment(code, node))})
        if isinstance(node, ast.Name) and node.id in "xymbCPs":
            return {(node.id,): F(1)}
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            return {key: (-value if isinstance(node.op, ast.USub) else value)
                    for key, value in visit(node.operand).items()}
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                return add(left, right)
            if isinstance(node.op, ast.Sub):
                return add(left, right, -1)
            if isinstance(node.op, ast.Mult):
                return multiply(left, right)
            if isinstance(node.op, ast.Div):
                if set(right) != {()} or right[()] == 0:
                    raise ValueError("nonconstant or zero denominator")
                return clean({key: value / right[()] for key, value in left.items()})
        raise ValueError("unsupported arithmetic syntax")

    return visit(tree)


def equality(value):
    parts = value.split("=")
    if len(parts) != 2:
        raise ValueError("exactly one equality required")
    return add(polynomial(parts[0]), polynomial(parts[1]), -1)


def scalar(value):
    result = polynomial(value)
    if set(result) - {()}:
        raise ValueError("expected a scalar")
    return result.get((), F(0))


def split_top(value, separator):
    depth, start, result = 0, 0, []
    for index, char in enumerate(value):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                raise ValueError("unbalanced closing parenthesis")
        elif char == separator and depth == 0:
            result.append(value[start:index])
            start = index + 1
    if depth:
        raise ValueError("unbalanced opening parenthesis")
    result.append(value[start:])
    return result


def semantics(value):
    """Separate equations, scalar values, and ordered pairs without eval."""
    result = []
    for part in split_top(norm(value), ";"):
        if not part:  # Source punctuation may end an otherwise complete item.
            continue
        if "=" in part:
            result.append(("equation", tuple(sorted(equality(part).items()))))
            continue
        for item in split_top(part, ","):
            if item.startswith("(") and item.endswith(")"):
                coordinates = split_top(item[1:-1], ",")
                if len(coordinates) == 2:
                    result.append(("point", tuple(scalar(v) for v in coordinates)))
                    continue
            result.append(("scalar", scalar(item)))
    if not result:
        raise ValueError("empty mathematical content")
    return result


def math_text(node):
    name = node.tag.removeprefix(M)
    if name in {"math", "mrow"}:
        return "".join(math_text(child) for child in node)
    if name in {"mi", "mn", "mo", "mtext"} and not list(node):
        return node.text or ""
    if name == "mfrac" and len(node) == 2:
        numerator, denominator = map(math_text, node)
        if not re.fullmatch(r"[−-]?\d+", numerator) or not re.fullmatch(r"\d+", denominator):
            raise ValueError("unsupported source fraction")
        if scalar(denominator) == 0:
            raise ValueError("zero source denominator")
        return f"({numerator}/{denominator})"
    raise ValueError(f"unsupported MathML: {node.tag}")


def line(value, independent="x", dependent="y"):
    poly = equality(value)
    allowed = {(independent,), (dependent,), ()}
    if set(poly) - allowed:
        raise ValueError("not an affine equation in the stated two variables")
    a, b, c = poly.get((independent,), F(0)), poly.get((dependent,), F(0)), -poly.get((), F(0))
    if (a, b) == (0, 0):
        raise ValueError("not a line")
    return (a, b, c)


def slope(coefficients):
    a, b, _ = coefficients
    return -a / b if b else None


def intercept(coefficients):
    _, b, c = coefficients
    return (F(0), c / b) if b else None


def slope_between(first, second):
    x1, y1 = map(F, first)
    x2, y2 = map(F, second)
    if first == second:
        raise ValueError("distinct points required")
    return (y2 - y1) / (x2 - x1) if x2 != x1 else None


def satisfies(coefficients, point):
    a, b, c = coefficients
    x, y = point
    return a * x + b * y == c


def classify(first, second):
    a, b, c = first
    d, e, f = second
    if a * e == b * d:
        return "coincident" if a * f == c * d and b * f == c * e else "parallel"
    return "perpendicular" if a * d + b * e == 0 else "neither"


def count_domain(value):
    number = F(value)
    return number >= 0 and number.denominator == 1


def image_name(number):
    return f"{PREFIX}{number}{SUFFIX}"


class Unit17MathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (BASE / "translations" / f"{UNIT}.xml").read_bytes()
        cls.root = ET.fromstring(cls.raw)
        cls.target, cls.target_parents = by_id(cls.root), parents(cls.root)
        cls.config = read_json(BASE / "units" / f"{UNIT}.json")
        cls.lock = read_json(BASE / "provenance" / f"{UNIT}.lock.json")
        cls.math_nodes = [e for e in cls.root.iter() if e.get("data-check")]
        cls.math = {e.get("data-check"): text(e) for e in cls.math_nodes}
        cls.modules, cls.module_bytes, cls.image_bytes = {}, {}, {}
        for locale, (archive, prefix, _) in ARCHIVES.items():
            with zipfile.ZipFile(WORKSPACE / "downloads/mr-Deva-IN/releases" / archive) as zipped:
                for module in ["m81374", "m81370"]:
                    data = zipped.read(f"{prefix}/modules/{module}/index.cnxml")
                    cls.module_bytes[locale, module] = data
                    cls.modules[locale, module] = ET.fromstring(data)
                for number in IMAGES:
                    cls.image_bytes[locale, number] = zipped.read(f"{prefix}/media/{image_name(number)}")
        cls.sources = {locale: by_id(cls.modules[locale, "m81374"]) for locale in ARCHIVES}
        cls.blocks = [e for e in cls.sources["en"][TOPIC] if e.tag != C + "title"]
        cls.exercises = [e for e in cls.blocks if e.tag == C + "exercise"]
        cls.images = {int(e.get("src").removeprefix("asset:" + PREFIX).removesuffix(SUFFIX)): e
                      for e in cls.root.iter("img")}

    def question(self, number):
        return self.target[self.exercises[number - 1].get("id")]

    def problem(self, number):
        return self.target[self.exercises[number - 1].find(C + "problem").get("id")]

    def question_math(self, number):
        return [text(e) for e in self.problem(number).iter() if e.get("data-check")]

    def source_solution(self, number, locale="en"):
        identity = self.exercises[number - 1].get("id")
        return self.sources[locale][identity].find(C + "solution")

    def test_01_frozen_input_pins_and_locale(self):
        for path, pin in PINS.items():
            data = inside(BASE, path).read_bytes()
            self.assertEqual((len(data), sha(data)), pin, path)
        self.assertEqual((self.root.tag, self.root.get("id"), self.root.get("lang")), ("article", UNIT, "mr-Deva-IN"))
        decoded = self.raw.decode("utf-8")
        self.assertNotIn("\ufffd", decoded)
        self.assertEqual(unicodedata.normalize("NFC", decoded), decoded)
        self.assertEqual((self.lock["unit"], self.lock["locale"]), (UNIT, "mr-Deva-IN"))

    def test_02_selected_source_and_backreference_module_pins(self):
        for key, pin in MODULE_PINS.items():
            data = self.module_bytes[key]
            self.assertEqual((len(data), sha(data)), pin, key)

    def test_03_complete_fifty_selector_topic_boundary(self):
        for source in self.sources.values():
            groups = source[CHAPTER].findall(C + "section")
            self.assertEqual([e.get("id") for e in groups[:3]], [PREVIOUS, TOPIC, FOLLOWING])
            self.assertEqual(len(groups), 6)
            blocks = [e for e in source[TOPIC] if e.tag != C + "title"]
            self.assertEqual((len(blocks), blocks[0].get("id"), blocks[-1].get("id")),
                             (50, "fs-id1167833047231", "fs-id1167836792421"))
        self.assertNotIn(PREVIOUS, self.target)
        self.assertNotIn(FOLLOWING, self.target)
        self.assertNotIn("fs-id1167836628671", self.target)
        for key, wanted in {"source_count": 50, "translated_practice_items": 36,
                            "translated_worked_examples": 0, "translated_definitions": 0,
                            "translated_resource_notes": 0, "original_practice_items": 0,
                            "question_ids": []}.items():
            self.assertEqual(self.config[key], wanted, key)

    def test_04_all_hundred_frozen_fragments_exact(self):
        identities = [e.get("id") for e in self.blocks]
        records = self.lock["source_selections"]
        self.assertEqual([s["target_id"] for s in records], identities)
        locators = ["A20:m81374#" + identity for identity in identities]
        self.assertEqual([s["locator"] for s in records], locators)
        target = [e for e in self.root.iter() if e.get("data-source")]
        self.assertEqual([e.get("id") for e in target], identities)
        self.assertEqual([e.get("data-source") for e in target], locators)
        self.assertTrue(all(e.get("data-kind") == "translation" for e in target))
        witnesses = {w["path"]: w["sha256"] for w in self.lock["witnesses"]}
        total, rows = 0, []
        for selection in records:
            self.assertEqual([r["locale"] for r in selection["sources"]], ["en", "id"])
            for record in selection["sources"]:
                locale = record["locale"]
                archive, prefix, archive_hash = ARCHIVES[locale]
                self.assertEqual(record["archive"], "downloads/mr-Deva-IN/releases/" + archive)
                self.assertEqual(record["archive_sha256"], archive_hash)
                self.assertEqual(record["member"], f"{prefix}/modules/m81374/index.cnxml")
                self.assertEqual(record["module_sha256"], MODULE_PINS[locale, "m81374"][1])
                data = inside(BASE, record["fragment_path"]).read_bytes()
                total += len(data)
                self.assertEqual(sha(data), record["fragment_sha256"])
                self.assertEqual(witnesses[record["fragment_path"]], sha(data))
                self.assertEqual(shape(ET.fromstring(data)), shape(self.sources[locale][selection["target_id"]]))
                rows.append(selection["target_id"] + "|" + locale + "|" + sha(data))
        self.assertEqual((len(rows), total, inventory(rows)), (100, 55482, INVENTORIES["fragments"]))

    def test_05_all_original_ids_preorder_and_ancestry(self):
        ordered = [CHAPTER] + [e.get("id") for e in self.sources["en"][TOPIC].iter() if e.get("id")]
        self.assertEqual(len(ordered), 167)
        allowed = set(ordered)
        actual = [e.get("id") for e in self.root.iter() if e.get("id")]
        self.assertEqual((len(actual), len(set(actual))), (169, 169))
        self.assertEqual(set(actual) - allowed, {UNIT, "credits"})
        self.assertEqual([i for i in actual if i in allowed], ordered)
        for locale, source in self.sources.items():
            mapping = parents(self.modules[locale, "m81374"])
            self.assertEqual([CHAPTER] + [e.get("id") for e in source[TOPIC].iter() if e.get("id")], ordered)
            for identity in ordered:
                self.assertEqual(nearest(source[identity], mapping, allowed),
                                 nearest(self.target[identity], self.target_parents, allowed), identity)

    def test_06_fourteen_headings_and_instructions(self):
        paragraphs = [e for e in self.blocks if e.tag == C + "para"]
        bold = [e for e in paragraphs if e.find(C + "emphasis[@effect='bold']") is not None]
        self.assertEqual((len(paragraphs), len(bold)), (14, 6))
        for original in paragraphs:
            target = self.target[original.get("id")]
            self.assertEqual(target.tag, "p")
            self.assertRegex(text(target), r"[\u0900-\u097f]")
            self.assertEqual(target.find("strong") is not None, original in bold)
        self.assertIn("सर्वांत सोयीची पद्धत", text(self.target["fs-id1167836558141"]))
        self.assertIn("उतार आणि y-अक्षावरील छेदबिंदू", text(self.target["fs-id1167836705885"]))

    def test_07_fifty_exact_unique_math_strings_regression_only(self):
        self.assertEqual((len(self.math_nodes), len(self.math)), (50, 50))
        self.assertEqual(self.math, self.config["expected_math"])
        self.assertEqual(inventory([k + "|" + v for k, v in self.math.items()]), INVENTORIES["math"])

    def test_08_all_forty_one_original_mathml_items(self):
        for locale, source in self.sources.items():
            mapping = parents(source[TOPIC])
            allowed = set(source)
            counts, used = {}, set()
            for item in source[TOPIC].iter(M + "math"):
                identity = nearest(item, mapping, allowed)
                index = counts.get(identity, 0) + 1
                counts[identity] = index
                key = SPECIAL_KEYS.get((identity, index), f"src-{identity}-{index}")
                original = math_text(item)
                if identity == "fs-id1167830123746":
                    self.assertEqual(norm(original), "-$250")
                    original = original.replace("$", "")  # Target explicitly says dollars.
                self.assertEqual(semantics(original), semantics(self.math[key]), (locale, key))
                self.assertNotIn(key, used)
                used.add(key)
            self.assertEqual(sum(counts.values()), 41)
            self.assertEqual(set(self.math) - used, EXTRA_KEYS)

    def test_09_all_thirty_six_question_mathematical_prompts(self):
        self.assertEqual(len(self.exercises), 36)
        source_problem_math = 0
        for number, expected in QUESTION_MATH.items():
            actual = self.question_math(number)
            self.assertEqual(len(actual), len(expected), number)
            self.assertEqual([semantics(v) for v in actual], [semantics(v) for v in expected], number)
            self.assertEqual(text(self.question(number).find("h4")), f"प्रश्न {number}")
            source_problem_math += len(list(self.exercises[number - 1].find(C + "problem").iter(M + "math")))
        self.assertEqual(source_problem_math, 35)

    def test_10_graph_slopes_and_all_eighteen_described_points(self):
        expected_equations = {
            222: "y=-3x", 223: "y=x+4", 224: "y=1/3x-8/3", 225: "y=-1/2x+9/2",
            368: "y=-1/3x+3", 370: "y=-3/4x+1", 372: "y=-x-1",
            374: "4x-3y=12", 376: "y=35x-250",
        }
        for number, pair in GRAPH_POINTS.items():
            found = re.findall(r"\(([+-]?\d+),([+-]?\d+)\)", norm(self.images[number].get("alt")))
            self.assertEqual([tuple(map(F, p)) for p in found], list(pair), number)
            self.assertEqual(slope_between(*pair), GRAPH_SLOPES[number], number)
            coefficients = line(expected_equations[number])
            self.assertTrue(all(satisfies(coefficients, p) for p in pair), number)
            self.assertEqual(slope(coefficients), GRAPH_SLOPES[number])
        self.assertEqual(scalar(self.math["q2-answer"]), GRAPH_SLOPES[223])
        self.assertEqual(scalar(self.math["src-fs-id1167829690314-1"]), GRAPH_SLOPES[225])

    def test_11_horizontal_zero_and_vertical_undefined(self):
        for number, expected in [(5, 0), (6, None), (7, None), (8, 0)]:
            self.assertEqual(slope(line(self.question_math(number)[0])), expected)
        for locale, expected in [("en", "undefined"), ("id", "tidak terdefinisi")]:
            answer = self.source_solution(6, locale).find(C + "para")
            self.assertEqual(text(answer), expected)
            self.assertEqual(text(self.target[answer.get("id")]), "उतार परिभाषित नाही.")
        self.assertEqual(scalar(self.math["q8-answer"]), 0)
        introduction = text(self.target[TOPIC].find("aside"))
        self.assertIn("उभ्या नसलेल्या रेषेचा", introduction)
        self.assertIn("उभ्या रेषेचा उतार परिभाषित नसतो", introduction)
        self.assertIn("केवळ खाली उतरणाऱ्या रेषेसाठी नाही", introduction)
        self.assertNotIn("∞", introduction)

    def test_12_two_point_slope_formula_and_source_answers(self):
        for number, expected in [(9, 6), (10, -6), (11, F(1, 2)), (12, F(5, 2))]:
            data = semantics(self.question_math(number)[0])
            self.assertTrue(all(kind == "point" for kind, _ in data))
            first, second = [point for _, point in data]
            self.assertEqual(slope_between(first, second), expected)
            self.assertEqual(slope_between(second, first), expected)
        self.assertEqual(scalar(self.math["src-fs-id1167836455885-1"]), -6)
        self.assertEqual(scalar(self.math["src-fs-id1167836673410-1"]), F(5, 2))

    def test_13_point_and_slope_graphs_and_scalar_intercepts(self):
        for number, expected in [(13, "y=5/2x-7"), (14, "y=-1/3x+3")]:
            coordinate, given_slope = self.question_math(number)
            point = semantics(coordinate)[0][1]
            m = scalar(given_slope.split("=")[1])
            coefficients = line(expected)
            self.assertTrue(satisfies(coefficients, point))
            self.assertEqual(slope(coefficients), m)
        self.assertEqual(slope(line("y=3x+12")), scalar(self.math["q15-slope"].split("=")[1]))
        self.assertTrue(satisfies(line("y=3x+12"), (scalar(self.math["q15-x-intercept"]), F(0))))
        self.assertEqual(intercept(line("y=-3/4x+1")), (0, scalar(self.math["q16-y-intercept"])))
        self.assertEqual(slope(line("y=-3/4x+1")), scalar(self.math["q16-slope"].split("=")[1]))
        self.assertIn("छेदाचे x-मूल्य", text(self.problem(15)))
        self.assertIn("छेदाचे y-मूल्य", text(self.problem(16)))
        self.assertEqual(equality(self.math["slope-form"]), {("y",): F(1), ("m", "x"): F(-1), ("b",): F(-1)})
        self.assertEqual(norm(self.math["intercept-point"]), "(0,b)")

    def test_14_slope_and_intercept_answers_exact(self):
        expected = {17: (-4, (0, 9)), 18: (F(5, 3), (0, -6)),
                    19: (-5, (0, 10)), 20: (F(4, 5), (0, F(-8, 5)))}
        for number, (m, point) in expected.items():
            coefficients = line(self.question_math(number)[0])
            self.assertEqual((slope(coefficients), intercept(coefficients)), (m, point))
        for number, key in [(18, "src-fs-id1167836575633-1"), (20, "src-fs-id1167836526730-1")]:
            m, point = expected[number]
            self.assertEqual(semantics(self.math[key]), semantics(f"m={m};({point[0]},{point[1]})"))

    def test_15_all_graphing_equations_and_unchanged_two_over_two(self):
        expected = {21: (2, 3), 22: (-1, -1), 23: (F(-2, 5), 3),
                    24: (F(4, 3), -4), 26: (0, -3), 27: (-2, 5),
                    28: (1, -2), 29: (1, 2), 30: (F(3, 4), -1)}
        for number, (m, b) in expected.items():
            coefficients = line(self.question_math(number)[0])
            self.assertEqual((slope(coefficients), intercept(coefficients)), (m, (0, b)), number)
        self.assertEqual(line(self.question_math(25)[0]), (1, 0, 5))
        for source in self.sources.values():
            fraction = source["fs-id1167836575257"].find(".//" + M + "mfrac")
            self.assertEqual([text(child) for child in fraction], ["2", "2"])
        self.assertEqual(self.math["src-fs-id1167836575257-1"], "y = (2/2)x + 2")
        self.assertIn("तो 22 किंवा 2 असा वाचू नका", text(self.target[TOPIC]))

    def test_16_three_source_method_answers_without_exclusivity_claim(self):
        meanings = {
            26: ("horizontal line", "garis horizontal", "आडवी रेषा काढा."),
            28: ("intercepts", "titik potong sumbu", "अक्षांवरील छेदबिंदू वापरा."),
            30: ("plotting points", "memplot titik", "बिंदू दाखवून आलेख काढा."),
        }
        for number, (en, id_text, mr) in meanings.items():
            for locale, expected in [("en", en), ("id", id_text)]:
                paragraph = self.source_solution(number, locale).find(C + "para")
                self.assertEqual(text(paragraph), expected)
                self.assertEqual(text(self.target[paragraph.get("id")]), mr)
        self.assertTrue(all(satisfies(line(self.question_math(28)[0]), p) for p in [(2, 0), (0, -2)]))
        self.assertTrue(all(satisfies(line(self.question_math(30)[0]), p) for p in [(0, -1), (4, 2)]))
        self.assertIn("एकापेक्षा अधिक योग्य मार्ग असू शकतात", text(self.target[TOPIC]))

    def test_17_meal_cost_and_dollar_per_meal_rate(self):
        coefficients = line(self.math["q31-model"], "m", "C")
        self.assertEqual(coefficients, (F(-13, 2), 1, 42))
        m, baseline = slope(coefficients), intercept(coefficients)[1]
        self.assertEqual((m, baseline), (F(13, 2), 42))
        self.assertEqual(scalar(self.math["q31-meals"]), 14)
        self.assertEqual(m * 14 + baseline, 133)
        self.assertTrue(satisfies(coefficients, (14, 133)))
        # The affine coefficient, not a sampled finite grid, is the constant rate.
        self.assertEqual(add(polynomial("6.5(m+1)+42"), polynomial("6.5m+42"), -1), {(): F(13, 2)})
        paragraph = text(self.problem(31))
        self.assertIn("डॉलरमधील आठवड्याचा खर्च", paragraph)
        self.assertIn("भोजनांची संख्या m", paragraph)
        self.assertIn("m हे भोजनांची संख्या दर्शवते", text(self.target[TOPIC]))
        self.assertIsNone(self.source_solution(31))  # These are reviewer calculations only.

    def test_18_piano_profit_all_four_supplied_subparts(self):
        coefficients = line(self.math["q32-model"], "s", "P")
        self.assertEqual(coefficients, (-35, 1, -250))
        rate, baseline = slope(coefficients), intercept(coefficients)[1]
        self.assertEqual(scalar(self.math["q32-lessons"]), 20)
        self.assertEqual(baseline, scalar(self.math["q32-answer-a"]))
        self.assertEqual(rate * 20 + baseline, scalar(self.math["q32-answer-b"]))
        self.assertEqual((baseline, rate * 20 + baseline, rate), (-250, 450, 35))
        self.assertEqual(rate, scalar(self.math["q32-answer-slope"]))
        self.assertEqual(add(polynomial("35(s+1)-250"), polynomial("35s-250"), -1), {(): F(35)})
        for locale, words in [("en", ["student lessons", "weekly profit"]),
                              ("id", ["les siswa", "laba mingguannya"])]:
            for word in words:
                self.assertIn(word, text(self.sources[locale]["fs-id1167829694607"]))
            source_answer = text(self.sources[locale]["fs-id1167830123746"])
            self.assertIn("$450", source_answer)
            self.assertIn("$35", source_answer)
            self.assertIn("$250", source_answer)
        answer = text(self.target["fs-id1167830123746"])
        self.assertIn("प्रत्येक अतिरिक्त धड्यासाठी", answer)
        self.assertIn("नफा P हा 35 डॉलरने वाढतो", answer)
        self.assertIn("250 डॉलर तोटा", answer)
        self.assertEqual(re.findall("[ⓐⓑⓒⓓ]", answer), list("ⓐⓑⓒⓓ"))

    def test_19_count_domains_lesson_student_distinction_and_plot_window(self):
        for number, explicit in [(31, "भोजनांची संख्या"), (32, "धड्यांची संख्या")]:
            self.assertIn(explicit, text(self.problem(number)))
        for value in [0, 1, 14, 20, 29, 100]:
            self.assertTrue(count_domain(value))
        for value in [-1, F(1, 2), F(50, 7)]:
            self.assertFalse(count_domain(value))
        whole = text(self.target[TOPIC])
        for phrase in ["विद्यार्थ्यांची संख्या आणि शिकवलेल्या धड्यांची संख्या या वेगळ्या गोष्टी",
                       "s म्हणजे धड्यांची संख्या", "ऋण नसलेली पूर्णसंख्या",
                       "ऋण किंवा अपूर्णांक धडे प्रत्यक्ष शिकवले जातात असा त्याचा अर्थ नाही",
                       "चित्राची चौकट ही संपूर्ण परवानगी असलेल्या मोजणीची मर्यादा नाही"]:
            self.assertIn(phrase, whole)
        self.assertEqual(35 * 7 - 250, -5)
        self.assertEqual(35 * 8 - 250, 30)

    def test_20_four_line_pair_classifications_with_exact_coefficients(self):
        expectations = {
            33: ((F(4, 3), F(4, 3)), (F(1, 3), -3), "parallel"),
            34: ((5, -5), (-1, 0), "neither"),
            35: ((F(3, 2), F(-2, 3)), (F(-5, 2), 2), "perpendicular"),
            36: ((2, F(1, 2)), (-8, -2), "neither"),
        }
        for number, (slopes, intercepts, relationship) in expectations.items():
            first, second = [line(v) for v in self.question_math(number)[0].split(";")]
            self.assertEqual((slope(first), slope(second)), slopes)
            self.assertEqual((intercept(first)[1], intercept(second)[1]), intercepts)
            self.assertEqual(classify(first, second), relationship)
        for number in [34, 36]:
            for locale, expected in [("en", "neither"), ("id", "bukan keduanya")]:
                paragraph = self.source_solution(number, locale).find(C + "para")
                self.assertEqual(text(paragraph), expected)
                self.assertEqual(text(self.target[paragraph.get("id")]), "समांतरही नाहीत आणि लंबही नाहीत.")
        for number in [33, 35]:
            self.assertIsNone(self.source_solution(number))  # No source answer fabricated.

    def test_21_eight_application_prompt_subparts_and_eighteen_answer_pairs(self):
        for number in [31, 32]:
            for locale in ["en", "id"]:
                original = self.sources[locale][self.exercises[number - 1].get("id")].find(C + "problem")
                self.assertEqual(re.findall("[ⓐⓑⓒⓓ]", text(original)), list("ⓐⓑⓒⓓ"))
            self.assertEqual(re.findall("[ⓐⓑⓒⓓ]", text(self.problem(number))), list("ⓐⓑⓒⓓ"))
        supplied, missing, graphical = [], [], []
        for number in range(1, 37):
            source_answer = self.source_solution(number)
            target = self.question(number)
            solutions = [e for e in target.iter() if e.get("class") == "solution"]
            omissions = [e for e in target.iter() if e.get("class") == "source-answer-missing"]
            if source_answer is None:
                missing.append(number)
                self.assertEqual(solutions, [])
                self.assertEqual(len(omissions), 1)
                self.assertEqual(omissions[0].get("data-kind"), "original")
                self.assertIn("स्रोतात या प्रश्नाचे उत्तर दिलेले नाही", text(omissions[0]))
            else:
                supplied.append(number)
                self.assertEqual(omissions, [])
                answer_id = source_answer.get("id")
                problem_id = self.problem(number).get("id")
                self.assertEqual([e.get("id") for e in solutions], [answer_id])
                self.assertEqual([a.get("href") for a in self.problem(number).iter("a")], ["#" + answer_id])
                self.assertEqual([a.get("href") for a in self.target[answer_id].iter("a")], ["#" + problem_id])
                if source_answer.find(".//" + C + "image") is not None:
                    graphical.append(number)
        self.assertEqual(supplied, list(range(2, 37, 2)))
        self.assertEqual(missing, list(range(1, 37, 2)))
        self.assertEqual(graphical, [14, 16, 22, 24, 32])

    def test_22_all_nine_canonical_assets_original_media_roles(self):
        self.assertEqual(list(self.images), list(IMAGES))
        self.assertEqual(set(self.config["assets"]), {image_name(n) for n in IMAGES})
        self.assertEqual(len(list(self.root.iter("img"))), 9)
        for number, (question, role, byte_count, digest) in IMAGES.items():
            name = image_name(number)
            expected = {"path": f"assets/{UNIT}/{name}", "sha256": digest, "mime": "image/jpeg"}
            self.assertEqual(self.config["assets"][name], expected)
            data = inside(BASE, expected["path"]).read_bytes()
            self.assertEqual((len(data), sha(data)), (byte_count, digest))
            self.assertTrue(data.startswith(b"\xff\xd8\xff"))
            self.assertEqual(data, self.image_bytes["en", number])
            self.assertEqual(data, self.image_bytes["id", number])
            source = self.exercises[question - 1].find(C + role).find(".//" + C + "media")
            figure = self.target[source.get("id")]
            self.assertEqual(figure.tag, "figure")
            self.assertIs(figure.find("img"), self.images[number])
            self.assertEqual(self.images[number].get("src"), "asset:" + name)
        self.assertEqual(sum(row[2] for row in IMAGES.values()), 707085)

    def test_23_all_eighteen_review_copies_and_source_image_pins(self):
        rows = self.lock["source_images"]
        self.assertEqual(len(rows), 18)
        seen, record_hashes = set(), []
        for row in rows:
            locale = row["locale"]
            name = row["member"].split("/")[-1]
            number = int(name.removeprefix(PREFIX).removesuffix(SUFFIX))
            self.assertNotIn((locale, number), seen)
            seen.add((locale, number))
            archive, prefix, archive_hash = ARCHIVES[locale]
            data = self.image_bytes[locale, number]
            self.assertEqual(row["archive"], "downloads/mr-Deva-IN/releases/" + archive)
            self.assertEqual(row["archive_sha256"], archive_hash)
            self.assertEqual(row["member"], f"{prefix}/media/{name}")
            self.assertEqual((row["bytes"], row["sha256"]), (len(data), sha(data)))
            self.assertEqual(row["review_copy"], f"downloads/mr-Deva-IN/source-image-qa/{UNIT}/{locale}-{name}")
            self.assertEqual(inside(WORKSPACE, row["review_copy"]).read_bytes(), data)
            if locale == "en":
                self.assertEqual(row["committed_asset"], f"assets/{UNIT}/{name}")
            record_hashes.append(locale + "|" + name + "|" + sha(data) + "|" + str(len(data)))
        self.assertEqual(seen, {(locale, number) for locale in ARCHIVES for number in IMAGES})
        self.assertEqual(inventory(record_hashes), INVENTORIES["images"])
        self.assertEqual(sum(len(data) for data in self.image_bytes.values()), 1414170)

    def test_24_actual_axis_windows_and_four_source_alt_errors(self):
        for number in [222, 223, 224, 225]:
            for locale, needle in [("en", "negative 6 to 6"), ("id", "negatif 6 hingga 6")]:
                role = self.sources[locale][self.exercises[IMAGES[number][0] - 1].get("id")].find(C + "problem")
                alt = role.find(".//" + C + "media").get("alt")
                self.assertEqual(alt.count(needle), 2)
            self.assertIn("−8 ते 8", self.images[number].get("alt"))
        for number in [368, 370]:
            self.assertIn("−8 ते 8", self.images[number].get("alt"))
        for number in [372, 374]:
            self.assertIn("−10 ते 10", self.images[number].get("alt"))
        for image in self.images.values():
            self.assertIn("बाण", image.get("alt"))
            self.assertRegex(image.get("alt"), r"[\u0900-\u097f]")
        notes = [text(e) for e in self.root.iter("p") if e.get("data-kind") == "original"]
        correction = next(t for t in notes if "222–225" in t)
        self.assertIn("EN आणि ID", correction)
        self.assertIn("−6 ते 6", correction)
        self.assertIn("−8 ते 8", correction)
        self.assertIn("चित्रे बदललेली नाहीत", correction)

    def test_25_376_actual_h_p_axis_labels_and_s_alias(self):
        alt = self.images[376].get("alt")
        for phrase in ["आडव्या अक्षाला h", "उभ्या अक्षाला P", "−4 ते 28", "−250 ते 450",
                       "(0, −250)", "(20, 450)", "वरच्या टोकाला बाण"]:
            self.assertIn(phrase, alt)
        notes = [text(e) for e in self.question(32).iter("p") if e.get("data-kind") == "original"]
        note = next(v for v in notes if "अक्ष-नावाची नोंद" in v)
        for phrase in ["आडव्या अक्षाला h", "प्रश्नात धड्यांची संख्या s", "आडवे मूल्य हे s मानावे",
                       "प्रत्यक्ष h, P नावे", "मूळ चित्र बदललेले नाही"]:
            self.assertIn(phrase, note)
        self.assertEqual(slope_between(*GRAPH_POINTS[376]), 35)
        self.assertEqual(F(450 - (-250), 20 - 0), 35)  # numerical units, not screen angle
        for source in self.sources.values():
            self.assertIn("x", source["fs-id1167833050702"].get("alt"))
            self.assertIn("y", source["fs-id1167833050702"].get("alt"))

    def test_26_local_links_and_pinned_m81370_title_backreference(self):
        links = [e.get("href") for e in self.root.iter("a")]
        local = [v for v in links if v.startswith("#")]
        external = [v for v in links if not v.startswith("#")]
        self.assertEqual((len(local), len(external)), (43, 3))
        self.assertTrue(all(v[1:] in self.target for v in local))
        backref = "https://openstax.org/books/intermediate-algebra-2e/pages/3-2-slope-of-a-line"
        self.assertEqual(set(external), {backref, "https://openstax.org/books/intermediate-algebra-2e/pages/3-introduction",
                                        "https://creativecommons.org/licenses/by-nc-sa/4.0/"})
        title_link = self.target[TOPIC].find("h3/a")
        self.assertEqual(title_link.get("data-source-document"), "m81370")
        self.assertEqual(title_link.get("href"), backref)
        for locale, title in [("en", "Slope of a Line"), ("id", "Gradien Garis")]:
            source_title = self.sources[locale][TOPIC].find(C + "title")
            self.assertEqual([e.attrib for e in source_title.iter(C + "link")], [{"document": "m81370"}])
            module = self.modules[locale, "m81370"]
            self.assertEqual(text(module.find(C + "title")), title)
            self.assertIn("f54f6801-0920-459c-af2e-72f85ddda846", text(module.find(C + "metadata")))
        self.assertIn("इंटरनेट लागते", text(self.target[TOPIC]))
        self.assertIn("त्या पूर्ण विभागाचा मराठी अनुवाद येथे नाही", text(self.target[TOPIC]))
        self.assertIn("CC BY-NC-SA 4.0", text(self.target["credits"]))
        for term in self.config["required_terms"]:
            self.assertIn(term, text(self.root))

    def test_27_all_118_witnesses_and_offline_media(self):
        rows = self.lock["witnesses"]
        self.assertEqual((len(rows), len({r["path"] for r in rows})), (118, 118))
        check = []
        for row in rows:
            data = inside(BASE, row["path"]).read_bytes()
            self.assertEqual(sha(data), row["sha256"], row["path"])
            if "bytes" in row:
                self.assertEqual(len(data), row["bytes"])
            check.append(row["path"] + "|" + sha(data))
        self.assertEqual(inventory(check), INVENTORIES["witnesses"])
        lookup = {r["path"]: r["sha256"] for r in rows}
        for asset in self.config["assets"].values():
            self.assertEqual(lookup[asset["path"]], asset["sha256"])
        self.assertTrue(all(e.tag not in {"script", "iframe", "audio", "video", "svg"} for e in self.root.iter()))
        self.assertTrue(all(e.get("src", "").startswith("asset:") for e in self.root.iter("img")))

    def test_28_parser_and_classification_negative_controls(self):
        self.assertEqual(semantics("m=4/5;(0,-(8/5))"), semantics("m=(4/5);(0,-8/5)"))
        self.assertEqual(scalar("6.5"), F(13, 2))
        self.assertEqual(scalar("2/2"), 1)
        self.assertEqual(classify(line("x=2"), line("y=3")), "perpendicular")
        self.assertEqual(classify(line("y=x"), line("2y=2x")), "coincident")
        self.assertEqual(classify(line("x=2"), line("x=3")), "parallel")
        self.assertIsNone(slope(line("x=2")))
        for value in ["x*y=3", "y=x/x", "y=1/0", "y=x**2", "y=sin(x)", "y=(x", "x=y=1", "y=__import__('os')"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                line(value)
        with self.assertRaises(ValueError):
            semantics("(1,2) extra")
        with self.assertRaises(ValueError):
            slope_between((0, 0), (0, 0))
        with self.assertRaises(ValueError):
            json.loads('{"math":{"k":1,"k":2}}', object_pairs_hook=unique_object)
        with self.assertRaises(ValueError):
            math_text(ET.fromstring(f'<msqrt xmlns="{M[1:-1]}"><mn>4</mn></msqrt>'))


if __name__ == "__main__":
    unittest.main(verbosity=2)

