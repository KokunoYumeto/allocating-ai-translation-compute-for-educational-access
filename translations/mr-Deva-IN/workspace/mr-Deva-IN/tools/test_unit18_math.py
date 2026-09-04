"""MR018 independent source/math regression, not rendered-reader acceptance.

Read-only stdlib tests on actual frozen files and bounded existing ZIP members.
Original-pixel observations were made by the reviewer and are hash-bound here;
this suite is not OCR or computer vision. No eval, downloads, extraction, corpus
copies, output files or skipped tests. Run with python -B.
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
UNIT = "MR-BRIDGE-018"
C = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
CHAPTER = "fs-id1167836524742"
TOPIC = "fs-id1167836526512"
PREVIOUS = "fs-id1167829740806"
FOLLOWING = "fs-id1167836570304"
PINS = {
    "translations/MR-BRIDGE-018.xml": (32346, "f7b37554ff6973e523952578d742fda63eaa75962cd7a32369f266d2de2ec60a"),
    "units/MR-BRIDGE-018.json": (4519, "b374350df5b6fd3db857ee8726a65ccbcdb7888fe32aabaa111eaf510482cd4c"),
    "provenance/MR-BRIDGE-018.lock.json": (97307, "d7d13b2352c6aa829db9c57e38059b730cff8faf0f9af21ae214ad8238fa6aad"),
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
    ("en", "m81371"): (123694, "a8d9b3cdd70107f7ee603d104ac9cdd4168b57acc9b19e2e8116fea3dccc2ed2"),
    ("id", "m81371"): (127034, "c306d979513478a707e5740b20eb0ac4de39bac8e3b18402a79904ae9f4f6d1a"),
}
INVENTORIES = {
    "fragments": "3dbe61b168438ae88610e34467f2d81107c106a4c62553d5724a947e85f919c5",
    "math": "c56c60188f5283e02f3280c6869db3c26c498babd681b6249258421f328edf10",
    "images": "d078860954e9592ebbaaefd4b2481c6875af808c8be26c12295dcc32b363753d",
    "witnesses": "9087661c9d6149524cd6f796f18de167df1aa4bd3c9d20d5b6cdd276cadb717c",
}
# Each EN and ID original was individually viewed and then byte-compared.
IMAGES = {
    226: (5, 80495, "b65094690ad0890fac3f02bee25032a93ed199cedd500293eba1f84a8bec582f"),
    227: (6, 80118, "46b05b78acd8e919bd6b3b46cbd2e76beba0d6491e3cc34ccd35c01b33c3d5f4"),
    228: (7, 82690, "bdac4223fddce4df86cbea4b02180908ef41be39cf8c3d5f3a64bd476c819ed0"),
    229: (8, 78286, "3ba112acfc465daef1b41e2d37fad0b8909e472522f6582ef1cf64cf4a4a41b6"),
}
IMAGE_PREFIX, IMAGE_SUFFIX = "CNX_IntAlg_Figure_03_06_", "_img_new.jpg"
VISIBLE_POINTS = {
    226: ((0, 1), (1, 3)),
    227: ((0, 5), (1, 2)),
    228: ((0, -2), (4, 1)),
    229: ((0, -4), (4, -4)),
}
# Source alts' mathematical points: source descriptions are checked, not treated
# as proof of visibility. Figure 228's (8,4) is outside the actual +/-6 frame.
SOURCE_ALT_POINTS = {
    226: ((0, 1), (1, 3), (2, 5)),
    227: ((0, 5), (1, 2), (2, -1)),
    228: ((0, -2), (4, 1), (8, 4)),
    229: ((0, -4), (1, -4), (2, -4)),
}
QUESTION_MATH = {
    1: ["1/3", "y", "(0,-6)"], 2: ["-5", "y", "(0,-3)"],
    3: ["0", "y", "(0,4)"], 4: ["-2", "y", "(0,0)"],
    5: [], 6: [], 7: [], 8: [],
    9: ["m=-1/4", "(-8,3)"], 10: ["m=3/5", "(10,6)"],
    11: ["(-2,7)"], 12: ["m=-2", "(-1,-3)"],
    13: ["(2,10)", "(-2,-2)"], 14: ["(7,1)", "(5,0)"],
    15: ["(3,8)", "(3,-4)"], 16: ["(5,2)", "(-1,2)"],
    17: ["y=-3x+6", "(1,-5)"], 18: ["2x+5y=-10", "(10,4)"],
    19: ["x=4", "(-2,-1)"], 20: ["y=-5", "(-4,3)"],
    21: ["y=-4/5x+2", "(8,9)"], 22: ["2x-3y=9", "(-4,0)"],
    23: ["y=3", "(-1,-3)"], 24: ["x=-5", "(2,1)"],
}
# Independent calculations: odd-numbered entries are reviewer calculations,
# NEVER claims that source solutions or new reader answers were supplied.
EXPECTED_LINES = {
    1: "y=1/3x-6", 2: "y=-5x-3", 3: "y=4", 4: "y=-2x",
    5: "y=2x+1", 6: "y=-3x+5", 7: "y=3/4x-2", 8: "y=-4",
    9: "y=-1/4x+1", 10: "y=3/5x", 11: "y=7", 12: "y=-2x-5",
    13: "y=3x+4", 14: "y=1/2x-5/2", 15: "x=3", 16: "y=2",
    17: "y=-3x-2", 18: "y=-2/5x+8", 19: "x=-2", 20: "y=3",
    21: "y=5/4x-1", 22: "y=-3/2x-6", 23: "x=-1", 24: "y=1",
}
ORIGINAL_MATH = {
    "slope-intercept-form", "intercept-point", "given-point",
    "point-slope-form", "intercept-substitution", "two-point-condition",
    "two-point-slope", "perpendicular-product", "vertical-line-form",
}
EXTRA_KEYS = ORIGINAL_MATH | {"src-fs-id1167829716068-plain-zero"}
SYMBOL_PATTERN = r"[xym]_[12]|[xymbc]"
SYMBOLS = {"x", "y", "m", "b", "c", "x_1", "x_2", "y_1", "y_2", "m_1", "m_2"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def inventory(rows):
    return sha(("\n".join(sorted(rows)) + "\n").encode("utf-8"))


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def inside(base, relative):
    target = (base / relative).resolve()
    if base.resolve() not in target.parents:
        raise ValueError("input is not a file below the expected base")
    return target


def text(node):
    return "".join(node.itertext())


def by_id(root):
    return {e.get("id"): e for e in root.iter() if e.get("id")}


def parents(root):
    return {child: node for node in root.iter() for child in node}


def nearest_id(node, mapping, allowed):
    while node in mapping:
        node = mapping[node]
        if node.get("id") in allowed:
            return node.get("id")
    return None


def shape(node):
    return (node.tag, tuple(sorted(node.attrib.items())), node.text,
            tuple((shape(child), child.tail) for child in node))


def norm(value):
    return re.sub(r"\s+", "", value.replace("−", "-").replace("₁", "_1").replace("₂", "_2"))


def without_punctuation(value):
    value = norm(value)
    return value[:-1] if value.endswith(",") else value


def clean(poly):
    return {key: value for key, value in poly.items() if value}


def add(first, second, sign=1):
    result = dict(first)
    for key, value in second.items():
        result[key] = result.get(key, F(0)) + sign * value
    return clean(result)


def multiply(first, second):
    result = {}
    for left, a in first.items():
        for right, b in second.items():
            key = tuple(sorted(left + right))
            result[key] = result.get(key, F(0)) + a * b
    return clean(result)


def substitute(poly, replacements):
    result = {}
    for monomial, coefficient in poly.items():
        term = {(): coefficient}
        for name in monomial:
            term = multiply(term, replacements.get(name, {(name,): F(1)}))
        result = add(result, term)
    return result


def polynomial(value):
    """Parse only exact arithmetic; arbitrary Python syntax is never executed."""
    value = norm(value)
    tokens = re.findall(r"\d+(?:\.\d+)?|" + SYMBOL_PATTERN + r"|[()+*/-]", value)
    if not value or "".join(tokens) != value:
        raise ValueError("unsupported expression token")

    def atom(token):
        return token in SYMBOLS or bool(re.fullmatch(r"\d+(?:\.\d+)?", token))

    explicit = []
    for token in tokens:
        if explicit and (atom(explicit[-1]) or explicit[-1] == ")") and (atom(token) or token == "("):
            explicit.append("*")
        explicit.append(token)
    code = "".join(explicit)
    try:
        tree = ast.parse(code, mode="eval")
    except SyntaxError as exc:
        raise ValueError("malformed arithmetic") from exc

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in {int, float}:
            return clean({(): F(ast.get_source_segment(code, node))})
        if isinstance(node, ast.Name) and node.id in SYMBOLS:
            return {(node.id,): F(1)}
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            sign = -1 if isinstance(node.op, ast.USub) else 1
            return {key: sign * value for key, value in visit(node.operand).items()}
        if isinstance(node, ast.BinOp):
            first, second = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                return add(first, second)
            if isinstance(node.op, ast.Sub):
                return add(first, second, -1)
            if isinstance(node.op, ast.Mult):
                return multiply(first, second)
            if isinstance(node.op, ast.Div):
                if set(second) != {()} or not second[()]:
                    raise ValueError("division requires a nonzero constant")
                return clean({key: value / second[()] for key, value in first.items()})
        raise ValueError("unsupported arithmetic syntax")

    return visit(tree)


def scalar(value):
    poly = polynomial(value)
    if set(poly) - {()}:
        raise ValueError("expected a scalar, not a variable")
    return poly.get((), F(0))


def equality(value):
    parts = without_punctuation(value).split("=")
    if len(parts) != 2:
        raise ValueError("exactly one equality required")
    return add(polynomial(parts[0]), polynomial(parts[1]), -1)


def split_pair(value):
    value = norm(value)
    if not (value.startswith("(") and value.endswith(")")):
        raise ValueError("ordered pair requires parentheses")
    parts = value[1:-1].split(",")
    if len(parts) != 2:
        raise ValueError("exactly two coordinates required")
    return parts


def point(value):
    return tuple(scalar(v) for v in split_pair(value))


def semantics(value):
    value = without_punctuation(value)
    if "=" in value:
        return ("equation", tuple(sorted(equality(value).items())))
    if "," in value:
        return ("pair", tuple(tuple(sorted(polynomial(v).items())) for v in split_pair(value)))
    return ("polynomial", tuple(sorted(polynomial(value).items())))


def math_text(node):
    name = node.tag.removeprefix(M)
    if name in {"math", "mrow"}:
        return "".join(math_text(child) for child in node)
    if name in {"mi", "mn", "mo", "mtext"} and not list(node):
        return node.text or ""
    if name == "mfrac" and len(node) == 2:
        numerator, denominator = map(math_text, node)
        if not re.fullmatch(r"[−-]?\d+", numerator) or not re.fullmatch(r"\d+", denominator):
            raise ValueError("unexpected source fraction form")
        if not scalar(denominator):
            raise ValueError("zero source denominator")
        return f"({numerator}/{denominator})"
    raise ValueError(f"unsupported MathML: {node.tag}")


def line(value):
    poly = equality(value)
    if set(poly) - {("x",), ("y",), ()}:
        raise ValueError("not a numeric affine equation in x and y")
    a, b = poly.get(("x",), F(0)), poly.get(("y",), F(0))
    if not (a or b):
        raise ValueError("equation does not specify a line")
    return (a, b, -poly.get((), F(0)))


def canonical(coefficients):
    a, b, c = map(F, coefficients)
    divisor = a if a else b
    if not divisor:
        raise ValueError("zero normal vector")
    return (a / divisor, b / divisor, c / divisor)


def slope(coefficients):
    a, b, _ = coefficients
    return -a / b if b else None


def contains(coefficients, coordinate):
    a, b, c = coefficients
    x, y = coordinate
    return a * x + b * y == c


def slope_point(m, coordinate):
    x, y = coordinate
    return (-F(m), F(1), F(y) - F(m) * F(x))


def two_points(first, second):
    x1, y1 = map(F, first)
    x2, y2 = map(F, second)
    if (x1, y1) == (x2, y2):
        raise ValueError("two distinct points required")
    a, b = y2 - y1, x1 - x2
    return (a, b, a * x1 + b * y1)


def parallel_through(coefficients, coordinate):
    a, b, _ = coefficients
    x, y = coordinate
    return (a, b, a * x + b * y)


def perpendicular_through(coefficients, coordinate):
    a, b, _ = coefficients
    x, y = coordinate
    return (-b, a, -b * x + a * y)


def relationship(first, second):
    a, b, c = first
    d, e, f = second
    if a * e == b * d:
        return "coincident" if a * f == c * d and b * f == c * e else "parallel"
    return "perpendicular" if a * d + b * e == 0 else "neither"


def image_name(number):
    return f"{IMAGE_PREFIX}{number}{IMAGE_SUFFIX}"


class Unit18MathTests(unittest.TestCase):
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
                for module in ["m81374", "m81371"]:
                    data = zipped.read(f"{prefix}/modules/{module}/index.cnxml")
                    cls.module_bytes[locale, module] = data
                    cls.modules[locale, module] = ET.fromstring(data)
                for number in IMAGES:
                    cls.image_bytes[locale, number] = zipped.read(f"{prefix}/media/{image_name(number)}")
        cls.sources = {locale: by_id(cls.modules[locale, "m81374"]) for locale in ARCHIVES}
        cls.blocks = [e for e in cls.sources["en"][TOPIC] if e.tag != C + "title"]
        cls.exercises = [e for e in cls.blocks if e.tag == C + "exercise"]
        cls.images = {int(e.get("src").removeprefix("asset:" + IMAGE_PREFIX).removesuffix(IMAGE_SUFFIX)): e
                      for e in cls.root.iter("img")}

    def exercise(self, number, locale="en"):
        return self.sources[locale][self.exercises[number - 1].get("id")]

    def question(self, number):
        return self.target[self.exercises[number - 1].get("id")]

    def problem(self, number):
        return self.target[self.exercise(number).find(C + "problem").get("id")]

    def question_math(self, number):
        return [text(e) for e in self.problem(number).iter() if e.get("data-check")]

    def source_solution(self, number, locale="en"):
        return self.exercise(number, locale).find(C + "solution")

    def expected_line(self, number):
        return line(EXPECTED_LINES[number])

    def derived_line(self, number):
        values = self.question_math(number)
        if number <= 4:
            return slope_point(scalar(values[0]), point(values[2]))
        if number <= 8:
            return two_points(*VISIBLE_POINTS[number + 221])
        if number in {9, 10, 12}:
            return slope_point(scalar(without_punctuation(values[0]).split("=")[1]), point(values[1]))
        if number == 11:
            return slope_point(F(0), point(values[0]))
        if number <= 16:
            return two_points(*map(point, values))
        given, coordinate = line(values[0]), point(values[1])
        return (parallel_through if number <= 20 else perpendicular_through)(given, coordinate)

    def test_01_frozen_inputs_locale_and_unicode(self):
        for path, pin in PINS.items():
            data = inside(BASE, path).read_bytes()
            self.assertEqual((len(data), sha(data)), pin, path)
        self.assertEqual((self.root.tag, self.root.get("id"), self.root.get("lang")), ("article", UNIT, "mr-Deva-IN"))
        self.assertEqual((self.lock["unit"], self.lock["locale"]), (UNIT, "mr-Deva-IN"))
        decoded = self.raw.decode("utf-8")
        self.assertNotIn("\ufffd", decoded)
        self.assertEqual(unicodedata.normalize("NFC", decoded), decoded)

    def test_02_pinned_source_and_backreference_members(self):
        for key, pin in MODULE_PINS.items():
            data = self.module_bytes[key]
            self.assertEqual((len(data), sha(data)), pin, key)

    def test_03_complete_thirty_five_selector_scope(self):
        for source in self.sources.values():
            groups = source[CHAPTER].findall(C + "section")
            self.assertEqual(len(groups), 6)
            self.assertEqual([e.get("id") for e in groups[1:4]], [PREVIOUS, TOPIC, FOLLOWING])
            blocks = [e for e in source[TOPIC] if e.tag != C + "title"]
            self.assertEqual((len(blocks), blocks[0].get("id"), blocks[-1].get("id")),
                             (35, "fs-id1167836613250", "fs-id1167836686948"))
            self.assertEqual(len(list(source[TOPIC].iter(C + "table"))), 0)
        for identity in [PREVIOUS, FOLLOWING, "fs-id1167836628671"]:
            self.assertNotIn(identity, self.target)
        for key, expected in {"source_count": 35, "translated_practice_items": 24,
                              "translated_worked_examples": 0, "translated_definitions": 0,
                              "translated_resource_notes": 0, "original_practice_items": 0,
                              "question_ids": []}.items():
            self.assertEqual(self.config[key], expected)

    def test_04_all_seventy_frozen_fragments_and_order(self):
        identities = [e.get("id") for e in self.blocks]
        records = self.lock["source_selections"]
        self.assertEqual([r["target_id"] for r in records], identities)
        locators = ["A20:m81374#" + identity for identity in identities]
        self.assertEqual([r["locator"] for r in records], locators)
        selected = [e for e in self.root.iter() if e.get("data-source")]
        self.assertEqual([e.get("id") for e in selected], identities)
        self.assertEqual([e.get("data-source") for e in selected], locators)
        self.assertTrue(all(e.get("data-kind") == "translation" for e in selected))
        witnesses = {r["path"]: r["sha256"] for r in self.lock["witnesses"]}
        total, rows = 0, []
        for selection in records:
            self.assertEqual([r["locale"] for r in selection["sources"]], ["en", "id"])
            for record in selection["sources"]:
                locale = record["locale"]
                archive, prefix, archive_sha = ARCHIVES[locale]
                self.assertEqual(record["archive"], "downloads/mr-Deva-IN/releases/" + archive)
                self.assertEqual(record["archive_sha256"], archive_sha)
                self.assertEqual(record["member"], f"{prefix}/modules/m81374/index.cnxml")
                self.assertEqual(record["module_sha256"], MODULE_PINS[locale, "m81374"][1])
                data = inside(BASE, record["fragment_path"]).read_bytes()
                self.assertEqual(sha(data), record["fragment_sha256"])
                self.assertEqual(witnesses[record["fragment_path"]], sha(data))
                self.assertEqual(shape(ET.fromstring(data)), shape(self.sources[locale][selection["target_id"]]))
                total += len(data)
                rows.append(selection["target_id"] + "|" + locale + "|" + sha(data))
        self.assertEqual((len(rows), total, inventory(rows)), (70, 41374, INVENTORIES["fragments"]))

    def test_05_all_original_ids_preorder_and_ancestry(self):
        ordered = [CHAPTER] + [e.get("id") for e in self.sources["en"][TOPIC].iter() if e.get("id")]
        actual = [e.get("id") for e in self.root.iter() if e.get("id")]
        self.assertEqual((len(ordered), len(actual), len(set(actual))), (109, 111, 111))
        allowed = set(ordered)
        self.assertEqual([identity for identity in actual if identity in allowed], ordered)
        self.assertEqual(set(actual) - allowed, {UNIT, "credits"})
        for locale, source in self.sources.items():
            self.assertEqual([CHAPTER] + [e.get("id") for e in source[TOPIC].iter() if e.get("id")], ordered)
            mapping = parents(self.modules[locale, "m81374"])
            for identity in ordered:
                self.assertEqual(nearest_id(source[identity], mapping, allowed),
                                 nearest_id(self.target[identity], self.target_parents, allowed), identity)

    def test_06_all_eleven_heading_and_instruction_paragraphs(self):
        paragraphs = [e for e in self.blocks if e.tag == C + "para"]
        headings = [e for e in paragraphs if e.find(C + "emphasis[@effect='bold']") is not None]
        self.assertEqual((len(paragraphs), len(headings)), (11, 5))
        for original in paragraphs:
            translated = self.target[original.get("id")]
            self.assertEqual(translated.tag, "p")
            self.assertRegex(text(translated), r"[\u0900-\u097f]")
            self.assertEqual(translated.find("strong") is not None, original in headings)
            if original not in headings:
                self.assertIn("समीकरण उतार–खंड रूपात लिहा", text(translated))
        self.assertIn("समांतर", text(self.target["fs-id1167836366759"]))
        self.assertIn("लंब", text(self.target["fs-id1167824585096"]))

    def test_07_all_sixty_four_unique_math_strings_regression_only(self):
        self.assertEqual((len(self.math_nodes), len(self.math)), (64, 64))
        self.assertEqual(self.math, self.config["expected_math"])
        self.assertEqual(inventory([k + "|" + v for k, v in self.math.items()]), INVENTORIES["math"])
        originals = []
        for node in self.math_nodes:
            current = node
            while current in self.target_parents and current.get("data-kind") is None:
                current = self.target_parents[current]
            if current.get("data-kind") == "original":
                originals.append(node.get("data-check"))
        self.assertEqual(set(originals), ORIGINAL_MATH)
        self.assertEqual(len(originals), 9)

    def test_08_all_fifty_four_mathml_items_in_each_original(self):
        for locale, source in self.sources.items():
            counts, used = {}, set()
            mapping = parents(source[TOPIC])
            for node in source[TOPIC].iter(M + "math"):
                identity = nearest_id(node, mapping, set(source))
                index = counts.get(identity, 0) + 1
                counts[identity] = index
                key = f"src-{identity}-{index}"
                self.assertEqual(semantics(math_text(node)), semantics(self.math[key]), (locale, key))
                self.assertNotIn(key, used)
                used.add(key)
            self.assertEqual(sum(counts.values()), 54)
            self.assertEqual(set(self.math) - used, EXTRA_KEYS)
        for locale, word in [("en", "slope 0"), ("id", "gradien 0")]:
            self.assertIn(word, text(self.sources[locale]["fs-id1167829716068"]))
        self.assertEqual(self.math["src-fs-id1167829716068-plain-zero"], "0")

    def test_09_all_twenty_four_question_constraints(self):
        self.assertEqual(len(self.exercises), 24)
        count = 0
        for number, expected in QUESTION_MATH.items():
            actual = self.question_math(number)
            self.assertEqual(len(actual), len(expected), number)
            self.assertEqual([semantics(v) for v in actual], [semantics(v) for v in expected], number)
            self.assertEqual(text(self.question(number).find("h4")), f"प्रश्न {number}")
            count += len(list(self.exercise(number).find(C + "problem").iter(M + "math")))
        self.assertEqual(count, 42)
        self.assertIn("आडवी रेषा", text(self.problem(11)))
        self.assertIn("Horizontal line containing", text(self.exercise(11).find(C + "problem")))
        self.assertIn("Garis horizontal", text(self.exercise(11, "id").find(C + "problem")))

    def test_10_slope_and_intercept_constraints_one_to_four(self):
        for number, m, intercept_value in [(1, F(1, 3), -6), (2, -5, -3), (3, 0, 4), (4, -2, 0)]:
            candidate = self.derived_line(number)
            self.assertEqual(slope(candidate), m)
            self.assertTrue(contains(candidate, (0, intercept_value)))
            self.assertEqual(canonical(candidate), canonical(self.expected_line(number)))
            self.assertEqual(self.question_math(number)[1], "y")

    def test_11_all_four_graph_equations_and_visible_points(self):
        for image_number, pair in VISIBLE_POINTS.items():
            question = IMAGES[image_number][0]
            descriptions = re.findall(r"\(([+-]?\d+),([+-]?\d+)\)", norm(self.images[image_number].get("alt")))
            self.assertEqual([tuple(map(F, p)) for p in descriptions], list(pair))
            candidate = self.derived_line(question)
            self.assertTrue(all(contains(candidate, p) for p in pair))
            self.assertEqual(canonical(candidate), canonical(self.expected_line(question)))
        self.assertEqual([slope(self.derived_line(q)) for q in range(5, 9)], [2, -3, F(3, 4), 0])

    def test_12_slope_and_point_constraints_nine_to_twelve(self):
        for number, m, point_value in [(9, F(-1, 4), (-8, 3)), (10, F(3, 5), (10, 6)),
                                       (11, 0, (-2, 7)), (12, -2, (-1, -3))]:
            candidate = self.derived_line(number)
            self.assertTrue(contains(candidate, point_value))
            self.assertEqual(slope(candidate), m)
            self.assertEqual(canonical(candidate), canonical(self.expected_line(number)))
        self.assertEqual(self.derived_line(9)[2], 1)
        self.assertEqual(self.derived_line(10)[2], 0)
        self.assertEqual(self.derived_line(12)[2], -5)

    def test_13_two_point_constraints_including_horizontal_and_vertical(self):
        for number in range(13, 17):
            first, second = map(point, self.question_math(number))
            candidate = self.derived_line(number)
            self.assertTrue(contains(candidate, first))
            self.assertTrue(contains(candidate, second))
            self.assertEqual(canonical(candidate), canonical(two_points(second, first)))
            self.assertEqual(canonical(candidate), canonical(self.expected_line(number)))
        self.assertEqual([slope(self.derived_line(q)) for q in range(13, 17)], [3, F(1, 2), None, 0])
        self.assertEqual(canonical(self.derived_line(15)), (1, 0, 3))
        self.assertEqual(canonical(self.derived_line(16)), (0, 1, 2))

    def test_14_all_four_parallel_lines(self):
        for number in range(17, 21):
            given_text, coordinate_text = self.question_math(number)
            given, coordinate = line(given_text), point(coordinate_text)
            candidate = self.derived_line(number)
            self.assertTrue(contains(candidate, coordinate))
            self.assertEqual(relationship(given, candidate), "parallel")
            self.assertEqual(canonical(candidate), canonical(self.expected_line(number)))
        self.assertEqual([slope(self.derived_line(q)) for q in range(17, 21)], [-3, F(-2, 5), None, 0])

    def test_15_all_four_perpendicular_lines(self):
        for number in range(21, 25):
            given_text, coordinate_text = self.question_math(number)
            given, coordinate = line(given_text), point(coordinate_text)
            candidate = self.derived_line(number)
            self.assertTrue(contains(candidate, coordinate))
            self.assertEqual(relationship(given, candidate), "perpendicular")
            self.assertEqual(canonical(candidate), canonical(self.expected_line(number)))
        self.assertEqual([slope(self.derived_line(q)) for q in range(21, 25)], [F(5, 4), F(-3, 2), None, 0])

    def test_16_all_twelve_supplied_equations_satisfy_actual_constraints(self):
        supplied = []
        for number in range(1, 25):
            for locale in ARCHIVES:
                source = self.source_solution(number, locale)
                if source is None:
                    self.assertEqual(number % 2, 1)
                    continue
                if locale == "en":
                    supplied.append(number)
                source_math = list(source.iter(M + "math"))
                self.assertEqual(len(source_math), 1)
                source_equation = line(math_text(source_math[0]))
                translated = self.target[source.get("id")]
                translated_math = [e for e in translated.iter() if e.get("data-check")]
                self.assertEqual(len(translated_math), 1)
                self.assertEqual(canonical(line(text(translated_math[0]))), canonical(source_equation))
                self.assertEqual(canonical(source_equation), canonical(self.derived_line(number)))
                self.assertEqual(canonical(source_equation), canonical(self.expected_line(number)))
        self.assertEqual(supplied, list(range(2, 25, 2)))

    def test_17_authored_point_slope_and_intercept_coefficient_identity(self):
        general = equality(self.math["slope-intercept-form"])
        point_slope = equality(self.math["point-slope-form"])
        self.assertEqual(general, equality("y=mx+b"))
        self.assertEqual(point_slope, equality("y-y_1=m(x-x_1)"))
        self.assertEqual(equality(self.math["intercept-substitution"]), equality("b=y_1-mx_1"))
        # Substitute the displayed b expression, then compare every coefficient.
        value = self.math["intercept-substitution"].split("=")[1]
        self.assertEqual(substitute(general, {"b": polynomial(value)}), point_slope)
        self.assertEqual(semantics(self.math["intercept-point"]), semantics("(0,b)"))
        self.assertEqual(semantics(self.math["given-point"]), semantics("(x_1,y_1)"))
        self.assertEqual(substitute(point_slope, {"x": polynomial("x_1"), "y": polynomial("y_1")}), {})
        intro = text(self.target[TOPIC].find("aside"))
        for phrase in ["उभ्या नसलेल्या रेषेसाठी", "b हे y-अक्षावरील छेदाचे y-मूल्य", "दोन्ही बाजूंवर समान क्रिया",
                       "भाजक शून्येतर", "पहिला सहनिर्देशक x आणि दुसरा y"]:
            self.assertIn(phrase, intro)

    def test_18_authored_two_point_formula_and_denominator_condition(self):
        self.assertEqual(norm(self.math["two-point-condition"]), "x_2≠x_1")
        match = re.fullmatch(r"m=\((.+)\)/\((.+)\)", norm(self.math["two-point-slope"]))
        self.assertIsNotNone(match)
        numerator, denominator = map(polynomial, match.groups())
        self.assertEqual(numerator, polynomial("y_2-y_1"))
        self.assertEqual(denominator, polynomial("x_2-x_1"))
        cleared = add(multiply(polynomial("m"), denominator), numerator, -1)
        point_slope_at_second = substitute(equality(self.math["point-slope-form"]),
                                           {"x": polynomial("x_2"), "y": polynomial("y_2")})
        self.assertEqual(add(cleared, point_slope_at_second), {})
        self.assertIn("दोन वेगळ्या बिंदूंचे x-सहनिर्देशक भिन्न", text(self.target[TOPIC].find("aside")))
        # Equal x coordinates in the real source q15 give a vertical line.
        self.assertIsNone(slope(self.derived_line(15)))
        self.assertEqual(point(self.question_math(15)[0])[0], point(self.question_math(15)[1])[0])

    def test_19_authored_perpendicular_product_and_finite_slope_caveat(self):
        self.assertEqual(equality(self.math["perpendicular-product"]), equality("m_1m_2=-1"))
        for number in [21, 22]:
            given = line(self.question_math(number)[0])
            wanted = self.derived_line(number)
            self.assertEqual(slope(given) * slope(wanted), -1)
        for number in [23, 24]:
            values = [slope(line(self.question_math(number)[0])), slope(self.derived_line(number))]
            self.assertIn(None, values)
            self.assertIn(0, values)
        intro = text(self.target[TOPIC].find("aside"))
        for phrase in ["दोन्ही रेषांचे उतार परिभाषित", "दोन्ही उतार परिभाषित आणि शून्येतर",
                       "आडवी व उभी रेषा", "उभ्या रेषेचा उतार परिभाषित नसतो"]:
            self.assertIn(phrase, intro)
        self.assertNotIn("∞", intro)

    def test_20_three_vertical_exceptions_are_original_not_source_answers(self):
        self.assertEqual(equality(self.math["vertical-line-form"]), equality("x=c"))
        note = next(e for e in self.root.iter("p") if "स्रोत-सूचनेची मर्यादा" in text(e))
        self.assertEqual(note.get("data-kind"), "original")
        for phrase in ["प्रश्न 15, 19 आणि 23", "उभ्या रेषेला लागू होत नाही",
                       "समान x-सहनिर्देशक", "स्रोत-उत्तर नाही"]:
            self.assertIn(phrase, text(note))
        for number, value in [(15, 3), (19, -2), (23, -1)]:
            self.assertEqual(canonical(self.derived_line(number)), (1, 0, value))
            self.assertIsNone(self.source_solution(number))
            self.assertIsNone(self.source_solution(number, "id"))
        for locale, source in self.sources.items():
            for identity in ["fs-id1167833086732", "fs-id1167836366759", "fs-id1167824585096"]:
                wanted = "slope–intercept form" if locale == "en" else "gradien–titik potong sumbu y"
                self.assertIn(wanted, text(source[identity]))

    def test_21_all_twelve_answer_pairs_and_twelve_explicit_omissions(self):
        supplied, missing = [], []
        for number in range(1, 25):
            source = self.source_solution(number)
            target = self.question(number)
            solutions = [e for e in target.iter() if e.get("class") == "solution"]
            omissions = [e for e in target.iter() if e.get("class") == "source-answer-missing"]
            if source is None:
                missing.append(number)
                self.assertEqual(solutions, [])
                self.assertEqual(len(omissions), 1)
                self.assertEqual(omissions[0].get("data-kind"), "original")
                self.assertIn("स्रोतात या प्रश्नाचे उत्तर दिलेले नाही", text(omissions[0]))
            else:
                supplied.append(number)
                self.assertEqual(omissions, [])
                answer_id, problem_id = source.get("id"), self.problem(number).get("id")
                self.assertEqual([e.get("id") for e in solutions], [answer_id])
                self.assertEqual([e.get("href") for e in self.problem(number).iter("a")], ["#" + answer_id])
                self.assertEqual([e.get("href") for e in self.target[answer_id].iter("a")], ["#" + problem_id])
        self.assertEqual((supplied, missing), (list(range(2, 25, 2)), list(range(1, 25, 2))))
        local = [e.get("href") for e in self.root.iter("a") if e.get("href").startswith("#")]
        self.assertEqual(len(local), 30)
        self.assertTrue(all(href[1:] in self.target for href in local))

    def test_22_all_four_canonical_assets_and_original_media_ids(self):
        self.assertEqual((len(list(self.root.iter("img"))), list(self.images)), (4, list(IMAGES)))
        self.assertEqual(set(self.config["assets"]), {image_name(n) for n in IMAGES})
        for number, (question, size, digest) in IMAGES.items():
            name = image_name(number)
            expected = {"path": f"assets/{UNIT}/{name}", "sha256": digest, "mime": "image/jpeg"}
            self.assertEqual(self.config["assets"][name], expected)
            data = inside(BASE, expected["path"]).read_bytes()
            self.assertEqual((len(data), sha(data)), (size, digest))
            self.assertTrue(data.startswith(b"\xff\xd8\xff"))
            for locale in ARCHIVES:
                self.assertEqual(data, self.image_bytes[locale, number])
            source_media = self.exercise(question).find(".//" + C + "media")
            figure = self.target[source_media.get("id")]
            self.assertEqual(figure.tag, "figure")
            self.assertIs(figure.find("img"), self.images[number])
            self.assertEqual(nearest_id(figure, self.target_parents, set(self.target)), self.problem(question).get("id"))
            self.assertEqual(self.images[number].get("src"), "asset:" + name)
        self.assertEqual(sum(v[1] for v in IMAGES.values()), 321589)

    def test_23_all_eight_original_review_copies_and_pins(self):
        records = self.lock["source_images"]
        self.assertEqual(len(records), 8)
        seen, rows = set(), []
        for record in records:
            locale = record["locale"]
            name = record["member"].split("/")[-1]
            number = int(name.removeprefix(IMAGE_PREFIX).removesuffix(IMAGE_SUFFIX))
            self.assertNotIn((locale, number), seen)
            seen.add((locale, number))
            archive, prefix, archive_hash = ARCHIVES[locale]
            data = self.image_bytes[locale, number]
            self.assertEqual(record["archive"], "downloads/mr-Deva-IN/releases/" + archive)
            self.assertEqual(record["archive_sha256"], archive_hash)
            self.assertEqual(record["member"], f"{prefix}/media/{name}")
            self.assertEqual(record["locator"], "A20:m81374#" + self.exercise(IMAGES[number][0]).get("id"))
            self.assertEqual((record["bytes"], record["sha256"]), (len(data), sha(data)))
            self.assertEqual(record["review_copy"], f"downloads/mr-Deva-IN/source-image-qa/{UNIT}/{locale}-{name}")
            self.assertEqual(inside(WORKSPACE, record["review_copy"]).read_bytes(), data)
            if locale == "en":
                self.assertEqual(record["committed_asset"], f"assets/{UNIT}/{name}")
            rows.append(locale + "|" + name + "|" + sha(data) + "|" + str(len(data)))
        self.assertEqual(seen, {(locale, n) for locale in ARCHIVES for n in IMAGES})
        self.assertEqual(inventory(rows), INVENTORIES["images"])
        self.assertEqual(sum(len(d) for d in self.image_bytes.values()), 643178)

    def test_24_axis_alt_corrections_and_228_out_of_frame_point(self):
        for number, (question, _, _) in IMAGES.items():
            target_alt = self.images[number].get("alt")
            self.assertIn("−6 ते 6", target_alt)
            self.assertNotIn("−10 ते 10", target_alt)
            self.assertIn("दोन्ही टोकांना बाण", target_alt)
            self.assertRegex(target_alt, r"[\u0900-\u097f]")
            expected_direction = "उतरणारी" if number == 227 else "आडवी" if number == 229 else "चढणारी"
            self.assertIn(expected_direction, target_alt)
            for locale in ARCHIVES:
                media = self.exercise(question, locale).find(".//" + C + "media")
                alt = media.get("alt")
                self.assertIn("negative 10 to 10" if locale == "en" else "negatif 10 hingga 10", alt)
                replaced = norm(alt.replace("negative ", "-").replace("negatif ", "-"))
                points = [tuple(map(F, p)) for p in re.findall(r"\((-?\d+),(-?\d+)\)", replaced)]
                self.assertEqual(points, list(SOURCE_ALT_POINTS[number]))
                self.assertTrue(all(contains(self.derived_line(question), p) for p in points))
        self.assertTrue(contains(self.derived_line(7), (8, 4)))
        self.assertFalse(-6 <= 8 <= 6)
        self.assertNotIn("(8, 4)", self.images[228].get("alt"))
        note = next(text(e) for e in self.root.iter("p") if e.get("data-kind") == "original" and "226–229" in text(e))
        for phrase in ["EN आणि ID", "−10 ते 10", "−6 ते 6", "(8, 4)", "चित्राच्या चौकटीबाहेर", "मूळ चित्रे बदललेली नाहीत"]:
            self.assertIn(phrase, note)

    def test_25_title_backreference_external_links_and_scope_notice(self):
        links = [e.get("href") for e in self.root.iter("a")]
        external = [v for v in links if not v.startswith("#")]
        backref = "https://openstax.org/books/intermediate-algebra-2e/pages/3-3-find-the-equation-of-a-line"
        self.assertEqual((len(links), len(external)), (33, 3))
        self.assertEqual(set(external), {backref, "https://openstax.org/books/intermediate-algebra-2e/pages/3-introduction",
                                        "https://creativecommons.org/licenses/by-nc-sa/4.0/"})
        translated_link = self.target[TOPIC].find("h3/a")
        self.assertEqual((translated_link.get("data-source-document"), translated_link.get("href")), ("m81371", backref))
        for locale, title in [("en", "Find the Equation of a Line"), ("id", "Menentukan Persamaan Garis")]:
            original = self.sources[locale][TOPIC].find(C + "title")
            self.assertEqual(text(original), title)
            self.assertEqual([e.attrib for e in original.iter(C + "link")], [{"document": "m81371"}])
            module = self.modules[locale, "m81371"]
            self.assertEqual(text(module.find(C + "title")), title)
            self.assertIn("b7d62225-c09f-478e-8c1d-df46042de0b0", text(module.find(C + "metadata")))
        for phrase in ["इंटरनेट लागते", "त्या पूर्ण विभागाचा मराठी अनुवाद येथे नाही"]:
            self.assertIn(phrase, text(self.target[TOPIC].find("aside")))
        credits = text(self.target["credits"])
        for phrase in ["CC BY-NC-SA 4.0", "संबंधित घटकांच्या स्वतंत्र सूचना", FOLLOWING, "fs-id1167836628671",
                       "नवीन प्रश्न किंवा त्या रिकाम्या स्रोत-उत्तरांसाठी नवीन उत्तरे जोडलेली नाहीत"]:
            self.assertIn(phrase, credits)
        for term in self.config["required_terms"]:
            self.assertIn(term, text(self.root))

    def test_26_all_eighty_three_witnesses_and_offline_xml_media(self):
        records = self.lock["witnesses"]
        self.assertEqual((len(records), len({r["path"] for r in records})), (83, 83))
        rows = []
        for record in records:
            data = inside(BASE, record["path"]).read_bytes()
            self.assertEqual(sha(data), record["sha256"])
            if "bytes" in record:
                self.assertEqual(len(data), record["bytes"])
            rows.append(record["path"] + "|" + sha(data))
        self.assertEqual(inventory(rows), INVENTORIES["witnesses"])
        lookup = {r["path"]: r["sha256"] for r in records}
        for value in self.config["assets"].values():
            self.assertEqual(lookup[value["path"]], value["sha256"])
        self.assertTrue(all(e.tag not in {"script", "iframe", "svg", "audio", "video"} for e in self.root.iter()))
        self.assertTrue(all(e.get("src", "").startswith("asset:") for e in self.root.iter("img")))

    def test_27_parser_and_mathematical_negative_controls(self):
        self.assertEqual(semantics("m=−(1/4),"), semantics("m=-1/4"))
        self.assertEqual(scalar("0.25"), F(1, 4))
        self.assertEqual(canonical(line("y=1/2x-5/2")), canonical(line("2y=x-5")))
        self.assertEqual(relationship(line("x=2"), line("y=3")), "perpendicular")
        self.assertEqual(relationship(line("y=x"), line("2y=2x")), "coincident")
        self.assertEqual(relationship(line("x=2"), line("x=3")), "parallel")
        self.assertNotEqual(canonical(line("y=-3/2x-6")), canonical(line("y=3/2x-6")))
        self.assertFalse(contains(line("y=3/4x-2"), (4, 2)))  # altered plotted y value
        self.assertFalse(contains(line("y=-2x-5"), (-1, 3)))  # altered given y sign
        for value in ["y=x*x", "y=x/x", "y=1/0", "y=x**2", "y=sin(x)", "x=y=1", "y=(x",
                      "y=__import__('os')", "0=0", "1=0"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                line(value)
        with self.assertRaises(ValueError):
            two_points((3, 8), (3, 8))
        with self.assertRaises(ValueError):
            point("(1,2,3)")
        with self.assertRaises(ValueError):
            json.loads('{"math":{"k":1,"k":2}}', object_pairs_hook=unique_object)
        with self.assertRaises(ValueError):
            math_text(ET.fromstring(f'<msqrt xmlns="{M[1:-1]}"><mn>4</mn></msqrt>'))


if __name__ == "__main__":
    unittest.main(verbosity=2)

