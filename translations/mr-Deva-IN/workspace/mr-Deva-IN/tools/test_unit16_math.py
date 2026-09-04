"""Independent MR016 source/math regression, not HTML/PDF or human acceptance.

Reads the actual frozen unit, selected existing ZIP members and reviewed rasters.
No downloads, extraction, file writes, browser, third-party packages or eval.
Exact rational coefficients establish equation identity; pixel observations are
manual evidence bound to original bytes, not automated visual understanding.
Run from any directory: python -B <workspace>/mr-Deva-IN/tools/test_unit16_math.py
"""

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
UNIT = "MR-BRIDGE-016"
C = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
CHAPTER = "fs-id1167836524742"
TOPIC = "fs-id1167824674139"
NEXT_TOPIC = "fs-id1167829740806"
PREFIX = "CNX_IntAlg_Figure_03_06_"
SUFFIX = "_img_new.jpg"
INPUT_PINS = {
    "translations/MR-BRIDGE-016.xml": (36416, "cb4f1a89aa7d0762f003898aaef5315bccad05d5b61dc94e0011a4232f229025"),
    "units/MR-BRIDGE-016.json": (4941, "85cdd3e51d3378fe82b99cf130f2f7925c948c68b52c1ba4cd65bd37de1e7b5c"),
    "provenance/MR-BRIDGE-016.lock.json": (121267, "689ddf28c14356985a14975dae9047669694643e7dcf8a95ff49927d93e4c99a"),
}
ARCHIVES = {
    "en": ("A20-canonical.zip", "osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9", "effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917"),
    "id": ("A20-v0.3.0-source.zip", "source", "a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7"),
}
MODULE_PINS = {
    ("en", "m81374"): (247327, "021c29fa9a6ab3d5b06d2ef143a82d2ac818ed25fe6fd44ebf5d7a6be07a123a"),
    ("id", "m81374"): (247303, "d89a74aef766afca6a4ac7e1ae720f120d22cc771c11dd7e025c55bca1fabb8e"),
    ("en", "m81369"): (182816, "0ca3b9284188e75f0fda3b59093ece79f5e174152095a057e69d2889be79abd2"),
    ("id", "m81369"): (171955, "bdeb65b4170314ab51629262742d77943ce6e9221a5863bca4ce294dfec6cbb2"),
}
FRAGMENT_INVENTORY = "6884770ead052c717f59e32e2754058b0c2f47638a5b6ec3faccccff719addfd"
IMAGE_INVENTORY = "451fa54011ce057c1e4d2b323cf2168c59e6d57c12aa25345dc9471b5170a007"
MATH_INVENTORY = "7973e0930031ec543e1b68190d1ea6f3383c7f1e069cb81e83959623148fb083"
WITNESS_INVENTORY = "c5e9329afa259226c7e75ab75ed3e4af36c5984737eea6ae8ca9b7bc576f1900"

# All twelve EN and all twelve ID originals personally inspected, 2026-08-31.
# Tuple: question, source role, axis extent, bytes, shared EN/ID SHA-256.
IMAGES = {
    349: (1, "solution", 5, 69596, "620da1000c5b91d660e591a7976f06ebd441fe669e1f1f699a21c1157ea0f576"),
    351: (5, "solution", 8, 68876, "10c1ece5d9a51b8810b589a12662b65ba23ef54858441e2148890dd0b6452178"),
    353: (7, "solution", 8, 68149, "945978fb6a91ed76208644f06375d39a280b83c60f0c02b289e8e727c975f3fa"),
    355: (9, "solution", 8, 66192, "3460bfb9cf8ab25bf95e10c1ed367b1ec9b64a45175c80034d14ef284ef23c0a"),
    357: (11, "solution", 8, 67492, "16a1d2c4e7005b046f886497aff6022c4bac7fa8cbe39cd3c09f07f7117132b3"),
    359: (13, "solution", 8, 63029, "3faf2645daffc6cf1e3ca1d51bb2009d1cd2b6bd6aa97b091dbd0e7ada9c84ff"),
    361: (15, "solution", 5, 73722, "13326c6df7d1e3eda526d12f33a349004a367d6fc9c7792cb546b0b8f1326ad8"),
    220: (16, "problem", 8, 89752, "d59317fcdf00670419e0ded9bed3c289700c29eef5aff0494ab0e75b5b9e7ae3"),
    221: (17, "problem", 8, 91251, "3cc11b03b1c088fabcd2900afdd6ba6b7108fc690be874cac605f74b7eebb227"),
    362: (23, "solution", 8, 64427, "dfd154e26be8cb14db6703dc3d325316590b321f15854dc8ca7b5c362f1502cc"),
    364: (25, "solution", 8, 63966, "0da4da5aafe6fa434b97723c7ebda5a8b1c73c182178280100c44bc479ee7163"),
    366: (27, "solution", 8, 64143, "602f610ce4b3f830c3a2406e819f76e502244f07f9b71e1e6ef0ebac9f12ecc4"),
}

# Forty-seven point occurrences on eleven straight-line images. These describe
# points ON lines, not plotted dot markers. Fractional locations use exact source
# equations as well as compatible pixels; the rasters do not measure fractions.
LINE_POINTS = {
    351: "(-1,-7),(0,-3),(1,1),(2,5)",
    353: "(-6,0),(0,3),(2,4),(4,5)",
    355: "(-1,-7),(0,-6),(3,-3),(6,0)",
    357: "(-2,-6),(0,-3),(2,0),(4,3)",
    359: "(3,-1),(3,0),(3,1)",
    361: "(0,4/3),(1,4/3),(2,4/3),(0,0),(1,4/3),(2,8/3)",
    220: "(-6,-2),(-4,0),(-2,2),(0,4),(2,6),(4,8)",
    221: "(-2,5),(-1,4),(0,3),(3,0),(6,-3)",
    362: "(-3,0),(0,1),(3,2),(6,3)",
    364: "(0,-5),(1,-3),(2,-1),(3,1)",
    366: "(-1,-4),(0,0),(1,4)",
}
GRAPH_KEYS = {351: "q5", 353: "q7", 355: "q9", 357: "q11", 359: "q13", 362: "q23", 364: "q25", 366: "q27"}

# Ax + By = C, independently reduced from all 25 source equation prompts.
EQUATIONS = {
    "q3-equation": (5, 1, 10), "q4-equation": (-6, 1, -2),
    "q5": (-4, 1, -3), "q6": (3, 1, 0), "q7": (F(-1, 2), 1, 3),
    "q8": (F(4, 5), 1, -1), "q9": (1, -1, 6), "q10": (2, 1, 7),
    "q11": (3, -2, 6), "q12": (0, 1, -2), "q13": (1, 0, 3),
    "q14a": (2, 1, 0), "q14b": (0, 1, -2),
    "q15a": (F(-4, 3), 1, 0), "q15b": (0, 1, F(4, 3)),
    "q18": (1, -1, -1), "q19": (1, 2, 6), "q20": (2, 3, 12),
    "q21": (F(-3, 4), 1, -12), "q22": (-3, 1, 0),
    "q23": (-1, 3, 3), "q24": (1, -1, 4), "q25": (2, -1, 5),
    "q26": (2, -4, 8), "q27": (-4, 1, 0),
}
INTERCEPTS = {
    "q5": ((F(3, 4), 0), (0, -3)), "q6": ((0, 0), (0, 0)),
    "q7": ((-6, 0), (0, 3)), "q8": ((F(-5, 4), 0), (0, -1)),
    "q9": ((6, 0), (0, -6)), "q10": ((F(7, 2), 0), (0, 7)),
    "q11": ((2, 0), (0, -3)), "q18": ((-1, 0), (0, 1)),
    "q19": ((6, 0), (0, 3)), "q20": ((6, 0), (0, 4)),
    "q21": ((16, 0), (0, -12)), "q22": ((0, 0), (0, 0)),
    "q23": ((-3, 0), (0, 1)), "q24": ((4, 0), (0, -4)),
    "q25": ((F(5, 2), 0), (0, -5)), "q26": ((4, 0), (0, -2)),
    "q27": ((0, 0), (0, 0)),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def inventory(rows):
    return digest(("\n".join(sorted(rows)) + "\n").encode("utf-8"))


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
        raise ValueError(f"not a file within {base}: {relative}")
    return target


def text(node):
    return "".join(node.itertext())


def by_id(root):
    return {e.get("id"): e for e in root.iter() if e.get("id")}


def parent_map(root):
    return {child: parent for parent in root.iter() for child in parent}


def nearest(node, parents, allowed):
    while node in parents:
        node = parents[node]
        if node.get("id") in allowed:
            return node.get("id")
    return None


def shape(node):
    # Namespace prefix spelling and root tail are serialization details, whereas
    # internal text/tails, tags, attributes, order and ancestry must all survive.
    return (node.tag, tuple(sorted(node.attrib.items())), node.text,
            tuple((shape(child), child.tail) for child in node))


def math_text(node):
    name = node.tag.removeprefix(M)
    if name in {"math", "mrow"}:
        return "".join(math_text(child) for child in node)
    if name in {"mi", "mn", "mo"} and not list(node):
        return node.text or ""
    if name == "mfrac" and len(node) == 2:
        numerator, denominator = map(math_text, node)
        if re.fullmatch(r"[−-]?\d+", numerator) and re.fullmatch(r"\d+", denominator):
            if F(denominator) == 0:
                raise ValueError("zero source denominator")
            return numerator + "/" + denominator
    raise ValueError(f"unsupported source MathML: {node.tag}")


def normalized(value):
    return re.sub(r"\s+", "", value.replace("−", "-").replace("·", "*"))


class LinearParser:
    """Small exact affine grammar; nonconstant products/divisors are rejected."""

    def __init__(self, value):
        value = normalized(value)
        self.tokens = re.findall(r"\d+(?:\.\d+)?|[xy()+*/-]", value)
        if not value or "".join(self.tokens) != value:
            raise ValueError("unsupported expression token")
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def take(self):
        token = self.peek()
        if token is None:
            raise ValueError("incomplete expression")
        self.pos += 1
        return token

    def atom(self):
        token = self.take()
        if token in {"+", "-"}:
            factor = 1 if token == "+" else -1
            return tuple(factor * v for v in self.atom())
        if token == "(":
            value = self.sum()
            if self.take() != ")":
                raise ValueError("unbalanced group")
            return value
        if token in {"x", "y"}:
            return (F(token == "x"), F(token == "y"), F(0))
        if re.fullmatch(r"\d+(?:\.\d+)?", token):
            return (F(0), F(0), F(token))
        raise ValueError("expected scalar, variable or group")

    def product(self):
        left = self.atom()
        while self.peek() not in {None, "+", "-", ")"}:
            op = self.take() if self.peek() in {"*", "/"} else "*"
            right = self.atom()
            if op == "/":
                if right[:2] != (0, 0) or right[2] == 0:
                    raise ValueError("nonconstant or zero denominator")
                left = tuple(v / right[2] for v in left)
            elif left[:2] == (0, 0):
                left = tuple(left[2] * v for v in right)
            elif right[:2] == (0, 0):
                left = tuple(right[2] * v for v in left)
            else:
                raise ValueError("nonlinear product")
        return left

    def sum(self):
        left = self.product()
        while self.peek() in {"+", "-"}:
            sign = 1 if self.take() == "+" else -1
            right = self.product()
            left = tuple(a + sign * b for a, b in zip(left, right))
        return left

    def parse(self):
        result = self.sum()
        if self.peek() is not None:
            raise ValueError("unconsumed expression")
        return result


def equation(value):
    sides = value.rstrip(";").split("=")
    if len(sides) != 2:
        raise ValueError("expected one equality")
    lhs, rhs = (LinearParser(side).parse() for side in sides)
    a, b, constant = (x - y for x, y in zip(lhs, rhs))
    return (a, b, -constant)


POINT = re.compile(r"\(([+-]?\d+(?:\.\d+)?(?:/\d+)?),([+-]?\d+(?:\.\d+)?(?:/\d+)?)\)")


def points(value, prose=False):
    value = normalized(value)
    matches = list(POINT.finditer(value))
    if not matches:
        raise ValueError("no coordinate pair")
    if not prose and POINT.sub("", value).strip(",.;"):
        raise ValueError("unexpected coordinate-list content")
    return [(F(m[1]), F(m[2])) for m in matches]


def satisfies(coefficients, point):
    a, b, c = coefficients
    x, y = point
    return a * x + b * y == c


def line_through(first, second):
    if first == second:
        raise ValueError("two distinct points required")
    x1, y1 = first
    x2, y2 = second
    a, b = y2 - y1, x1 - x2
    return (a, b, a * x1 + b * y1)


def same_line(left, right):
    return (left[:2] != (0, 0) and right[:2] != (0, 0)
            and all(left[i] * right[j] == left[j] * right[i]
                    for i, j in [(0, 1), (0, 2), (1, 2)]))


def axis_intercepts(coefficients):
    a, b, c = coefficients
    return ((c / a, F(0)) if a else None,
            (F(0), c / b) if b else None)


def filename(number):
    return f"{PREFIX}{number}{SUFFIX}"


class Unit16MathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (BASE / "translations" / f"{UNIT}.xml").read_bytes()
        cls.root = ET.fromstring(cls.raw)
        cls.target = by_id(cls.root)
        cls.parents = parent_map(cls.root)
        cls.config = read_json(BASE / "units" / f"{UNIT}.json")
        cls.lock = read_json(BASE / "provenance" / f"{UNIT}.lock.json")
        cls.math_nodes = [e for e in cls.root.iter() if e.get("data-check")]
        cls.math = {e.get("data-check"): text(e) for e in cls.math_nodes}
        cls.modules, cls.module_bytes, cls.source_images = {}, {}, {}
        for locale, (archive, prefix, _) in ARCHIVES.items():
            with zipfile.ZipFile(WORKSPACE / "downloads/mr-Deva-IN/releases" / archive) as zipped:
                for module in ["m81374", "m81369"]:
                    data = zipped.read(f"{prefix}/modules/{module}/index.cnxml")
                    cls.module_bytes[locale, module] = data
                    cls.modules[locale, module] = ET.fromstring(data)
                for number in IMAGES:
                    cls.source_images[locale, number] = zipped.read(f"{prefix}/media/{filename(number)}")
        cls.en = by_id(cls.modules["en", "m81374"])
        cls.id_source = by_id(cls.modules["id", "m81374"])
        cls.blocks = [e for e in cls.en[TOPIC] if e.tag != C + "title"]
        cls.exercises = [e for e in cls.blocks if e.tag == C + "exercise"]
        cls.target_images = {int(e.get("src").removeprefix("asset:" + PREFIX).removesuffix(SUFFIX)): e
                             for e in cls.root.iter("img")}

    def question(self, number):
        return self.target[self.exercises[number - 1].get("id")]

    def original_note(self, key):
        node = next(e for e in self.math_nodes if e.get("data-check") == key)
        parent = self.parents[node]
        self.assertEqual(parent.get("data-kind"), "original")
        return text(parent)

    def test_01_frozen_inputs_and_locale(self):
        for relative, pin in INPUT_PINS.items():
            data = inside(BASE, relative).read_bytes()
            self.assertEqual((len(data), digest(data)), pin, relative)
        self.assertEqual(self.root.tag, "article")
        self.assertEqual(self.root.get("id"), UNIT)
        self.assertEqual(self.root.get("lang"), "mr-Deva-IN")
        decoded = self.raw.decode("utf-8")
        self.assertNotIn("\ufffd", decoded)
        self.assertEqual(unicodedata.normalize("NFC", decoded), decoded)
        self.assertEqual((self.lock["unit"], self.lock["locale"]), (UNIT, "mr-Deva-IN"))

    def test_02_actual_selected_module_and_backref_pins(self):
        for key, pin in MODULE_PINS.items():
            data = self.module_bytes[key]
            self.assertEqual((len(data), digest(data)), pin, key)

    def test_03_complete_first_topic_boundary(self):
        for source in [self.en, self.id_source]:
            groups = source[CHAPTER].findall(C + "section")
            self.assertEqual(len(groups), 6)
            self.assertEqual([e.get("id") for e in groups[:2]], [TOPIC, NEXT_TOPIC])
            children = [e for e in source[TOPIC] if e.tag != C + "title"]
            self.assertEqual(len(children), 40)
            self.assertEqual(children[-1].get("id"), "fs-id1167836626758")
        self.assertNotIn(NEXT_TOPIC, self.target)
        self.assertNotIn("fs-id1167836628671", self.target)
        for key, expected in {"source_count": 40, "translated_practice_items": 27,
                              "translated_worked_examples": 0, "translated_definitions": 0,
                              "original_practice_items": 0, "question_ids": []}.items():
            self.assertEqual(self.config[key], expected, key)

    def test_04_all_80_frozen_fragments_match_both_actual_sources(self):
        expected_ids = [e.get("id") for e in self.blocks]
        records = self.lock["source_selections"]
        self.assertEqual([s["target_id"] for s in records], expected_ids)
        self.assertEqual([s["locator"] for s in records], ["A20:m81374#" + i for i in expected_ids])
        translated = [e for e in self.root.iter() if e.get("data-source")]
        self.assertEqual([e.get("id") for e in translated], expected_ids)
        self.assertEqual([e.get("data-source") for e in translated], [s["locator"] for s in records])
        self.assertTrue(all(e.get("data-kind") == "translation" for e in translated))
        witness = {w["path"]: w["sha256"] for w in self.lock["witnesses"]}
        rows, total = [], 0
        for selection in records:
            self.assertEqual([s["locale"] for s in selection["sources"]], ["en", "id"])
            for record in selection["sources"]:
                locale = record["locale"]
                archive, prefix, archive_hash = ARCHIVES[locale]
                self.assertEqual(record["archive"], "downloads/mr-Deva-IN/releases/" + archive)
                self.assertEqual(record["archive_sha256"], archive_hash)
                self.assertEqual(record["member"], f"{prefix}/modules/m81374/index.cnxml")
                self.assertEqual(record["module_sha256"], MODULE_PINS[locale, "m81374"][1])
                data = inside(BASE, record["fragment_path"]).read_bytes()
                total += len(data)
                self.assertEqual(digest(data), record["fragment_sha256"])
                self.assertEqual(witness[record["fragment_path"]], digest(data))
                original = (self.en if locale == "en" else self.id_source)[selection["target_id"]]
                self.assertEqual(shape(ET.fromstring(data)), shape(original))
                rows.append(selection["target_id"] + "|" + locale + "|" + digest(data))
        self.assertEqual((len(rows), total, inventory(rows)), (80, 48636, FRAGMENT_INVENTORY))

    def test_05_all_134_source_ids_preorder_and_ancestry(self):
        ordered = [CHAPTER] + [e.get("id") for e in self.en[TOPIC].iter() if e.get("id")]
        self.assertEqual(len(ordered), 134)
        allowed = set(ordered)
        ids = [e.get("id") for e in self.root.iter() if e.get("id")]
        self.assertEqual(len(ids), 136)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual([i for i in ids if i in allowed], ordered)
        self.assertEqual(set(ids) - allowed, {UNIT, "credits"})
        for locale in ["en", "id"]:
            source = self.modules[locale, "m81374"]
            mapping, parents = by_id(source), parent_map(source)
            self.assertEqual([CHAPTER] + [e.get("id") for e in mapping[TOPIC].iter() if e.get("id")], ordered)
            for identity in ordered:
                self.assertEqual(nearest(self.target[identity], self.parents, allowed),
                                 nearest(mapping[identity], parents, allowed), identity)

    def test_06_all_heading_and_instruction_paragraphs(self):
        paragraphs = [e for e in self.blocks if e.tag == C + "para"]
        self.assertEqual(len(paragraphs), 13)
        bold = [e for e in paragraphs if e.find(C + "emphasis[@effect='bold']") is not None]
        self.assertEqual(len(bold), 5)
        for source in paragraphs:
            target = self.target[source.get("id")]
            self.assertEqual(target.tag, "p")
            self.assertRegex(text(target), r"[\u0900-\u097f]")
            self.assertEqual(bool(target.find("strong") is not None), source in bold)
        self.assertIn("प्रत्येक समीकरण-जोडीचे दोन्ही आलेख एकाच", text(self.target["fs-id1167833207874"]))
        self.assertIn("उकल कोणत्या क्रमित जोड्या", text(self.target["fs-id1167836408579"]))

    def test_07_exact_49_math_keys_not_an_independent_proof(self):
        self.assertEqual(len(self.math_nodes), 49)
        self.assertEqual(len(self.math), 49)
        self.assertEqual(self.math, self.config["expected_math"])
        self.assertEqual(inventory([k + "|" + v for k, v in self.math.items()]), MATH_INVENTORY)

    def test_08_all_39_source_question_expressions(self):
        self.assertEqual(len(self.exercises), 27)
        for locale, mapping in [("en", self.en), ("id", self.id_source)]:
            expression_count = 0
            for number, example in enumerate(self.exercises, 1):
                source = mapping[example.get("id")].find(C + "problem")
                target = self.target[source.get("id")]
                source_math = [math_text(e) for e in source.iter(M + "math")]
                target_math = [text(e) for e in target.iter() if e.get("data-check")]
                self.assertEqual(len(source_math), len(target_math), (locale, number))
                expression_count += len(source_math)
                for original, translated in zip(source_math, target_math):
                    if "=" in original:
                        self.assertEqual(equation(original), equation(translated), (locale, number))
                    else:
                        self.assertEqual(points(original), points(translated), (locale, number))
                self.assertEqual(text(self.question(number).find("h4")), f"प्रश्न {number}")
            self.assertEqual(expression_count, 39)

    def test_09_all_25_equations_exact_rational_coefficients(self):
        self.assertEqual(len(EQUATIONS), 25)
        for key, coefficients in EQUATIONS.items():
            self.assertEqual(equation(self.math[key]), coefficients, key)
        self.assertEqual(equation(self.math["q8"]), (F(4, 5), F(1), F(-1)))
        self.assertEqual(equation(self.math["q15a"]), (F(-4, 3), F(1), F(0)))

    def test_10_coordinate_order_quadrants_and_axes(self):
        first = [points(self.math[f"q1{k}"])[0] for k in "abcd"]
        self.assertEqual(first, [(-1, -5), (-3, 4), (2, -3), (1, F(5, 2))])
        self.assertEqual([(x > 0, y > 0) for x, y in first], [(False, False), (False, True), (True, False), (True, True)])
        self.assertEqual(points(self.target_images[349].get("alt"), prose=True), first)
        self.assertIn("बिंदू जोडलेले नाहीत", self.target_images[349].get("alt"))
        second = [points(self.math[f"q2{k}"])[0] for k in "abcd"]
        self.assertEqual(second, [(-2, 0), (0, -4), (0, 5), (3, 0)])
        self.assertTrue(all((x == 0) != (y == 0) for x, y in second))
        self.assertIn("x-अक्ष आडवा आणि y-अक्ष उभा", text(self.target[TOPIC]))

    def test_11_membership_q3_and_q4_without_fabricated_source_answer(self):
        for number, expected in [(3, [False, True, True]), (4, [True, True, False])]:
            eq = equation(self.math[f"q{number}-equation"])
            self.assertEqual([satisfies(eq, points(self.math[f"q{number}{k}"])[0]) for k in "abc"], expected)
        source = self.exercises[2].find(C + "solution")
        self.assertEqual(re.findall("[ⓐⓑⓒ]", text(source)), ["ⓑ", "ⓒ"])
        self.assertEqual(re.findall("[ⓐⓑⓒ]", text(self.target[source.get("id")]).split("प्रश्नाकडे")[0]), ["ⓑ", "ⓒ"])
        self.assertIsNone(self.exercises[3].find(C + "solution"))

    def test_12_all_47_described_line_points_and_exact_line_identity(self):
        count = 0
        for number, description in LINE_POINTS.items():
            actual = points(self.target_images[number].get("alt"), prose=True)
            self.assertEqual(actual, points(description), number)
            count += len(actual)
            if number == 361:
                branches = [("q15b", actual[:3]), ("q15a", actual[3:])]
            elif number in {220, 221}:
                branches = [(None, actual)]
            else:
                branches = [(GRAPH_KEYS[number], actual)]
            for key, branch in branches:
                coefficients = equation(self.math[key]) if key else ((-1, 1, 4) if number == 220 else (1, 1, 3))
                self.assertTrue(all(satisfies(coefficients, p) for p in branch), number)
                # Straightness was inspected; two distinct points determine this
                # line. Coefficient proportionality is not a sampled grid proof.
                self.assertTrue(same_line(line_through(branch[0], branch[-1]), coefficients), number)
        self.assertEqual(count, 47)

    def test_13_fractional_pair_of_lines_and_intersection(self):
        horizontal, slanted = equation(self.math["q15b"]), equation(self.math["q15a"])
        self.assertEqual(horizontal, (0, 1, F(4, 3)))
        self.assertEqual(slanted, (F(-4, 3), 1, 0))
        common = (F(1), F(4, 3))
        self.assertTrue(satisfies(horizontal, common) and satisfies(slanted, common))
        a, b, _ = slanted
        d, e, _ = horizontal
        self.assertNotEqual(a * e - b * d, 0)  # unique intersection, exact determinant
        self.assertIn("आडवी रेषा", self.target_images[361].get("alt"))
        self.assertIn("तिरपी रेषा", self.target_images[361].get("alt"))

    def test_14_four_text_answers_preserved_and_correct(self):
        textual = [(i, e.find(C + "solution")) for i, e in enumerate(self.exercises, 1)
                   if e.find(C + "solution") is not None and e.find(C + "solution").find(".//" + C + "image") is None]
        self.assertEqual([i for i, _ in textual], [3, 17, 19, 21])
        wanted = {17: [(0, 3), (3, 0)], 19: [(6, 0), (0, 3)], 21: [(16, 0), (0, -12)]}
        for number in [17, 19, 21]:
            for source in [self.en, self.id_source]:
                solution = source[self.exercises[number - 1].get("id")].find(C + "solution")
                self.assertEqual(points(math_text(solution.find(".//" + M + "math"))), wanted[number])
            answer = points(self.math[f"q{number}-answer"])
            self.assertEqual(answer, wanted[number])
            coefficients = (F(1), F(1), F(3)) if number == 17 else equation(self.math[f"q{number}"])
            self.assertEqual(set(answer), set(axis_intercepts(coefficients)))
            self.assertTrue(all(satisfies(coefficients, p) for p in answer))

    def test_15_all_single_line_intercepts_including_unsupplied_questions(self):
        # These computations are reviewer checks, not extra translated answers.
        for key, answer in INTERCEPTS.items():
            self.assertEqual(axis_intercepts(equation(self.math[key])), answer, key)
        self.assertEqual(axis_intercepts((F(-1), F(1), F(4))), ((-4, 0), (0, 4)))
        self.assertIsNone(self.exercises[15].find(C + "solution"))

    def test_16_vertical_horizontal_and_function_distinction(self):
        self.assertEqual(axis_intercepts(equation(self.math["q13"])), ((3, 0), None))
        self.assertEqual(axis_intercepts(equation(self.math["q12"])), (None, (0, -2)))
        self.assertIn("उभी सरळ रेषा", self.target_images[359].get("alt"))
        vertical = equation(self.math["q13"])
        self.assertTrue(satisfies(vertical, (F(3), F(0))))
        self.assertTrue(satisfies(vertical, (F(3), F(1))))
        self.assertEqual(vertical[1], 0)  # y is unrestricted, not a function y(x)
        self.assertEqual(equation(self.math["q14b"]), equation(self.math["q12"]))
        self.assertNotEqual(equation(self.math["q14a"]), equation(self.math["q14b"]))
        self.assertIn("रेषीय समीकरण", text(self.target[TOPIC].find("h3")))
        self.assertNotIn("फलन", text(self.target[TOPIC].find("h3")))

    def test_17_source_351_error_is_explicit_not_reintroduced(self):
        for source in [self.en, self.id_source]:
            alt = source["fs-id1167829850431"].get("alt").replace("negative ", "-").replace("negatif ", "-")
            self.assertEqual(points(alt, prose=True), [(-1, -7), (0, -3), (1, -1), (2, 3)])
        coefficients = equation(self.math["q5"])
        self.assertTrue(all(not satisfies(coefficients, p) for p in points(self.math["q5-bad-alt"])))
        self.assertTrue(all(satisfies(coefficients, p) for p in points(self.math["q5-fixed-alt"])))
        self.assertIn("दुरुस्ती", self.original_note("q5-bad-alt"))
        self.assertIn("चित्र किंवा प्रश्नाचे समीकरण बदललेले नाही", self.original_note("q5-fixed-alt"))

    def test_18_source_366_error_is_explicit_not_reintroduced(self):
        for source in [self.en, self.id_source]:
            alt = source["fs-id1167829755848"].get("alt").replace("negative ", "-").replace("negatif ", "-")
            self.assertEqual(points(alt, prose=True), [(-1, 4), (0, 0), (1, -4)])
        coefficients = equation(self.math["q27"])
        self.assertTrue(all(not satisfies(coefficients, p) for p in points(self.math["q27-bad-alt"])))
        self.assertTrue(all(satisfies(coefficients, p) for p in points(self.math["q27-fixed-alt"])))
        self.assertIn("दुरुस्ती", self.original_note("q27-bad-alt"))
        self.assertIn("चित्र किंवा प्रश्नाचे समीकरण बदललेले नाही", self.original_note("q27-fixed-alt"))

    def test_19_authored_q27_origin_and_second_point_method(self):
        origin = points(self.math["q27-origin"])[0]
        second = points(self.math["q27-second-point"])[0]
        self.assertEqual((origin, second), ((0, 0), (1, 4)))
        coefficients = equation(self.math["q27"])
        self.assertEqual(axis_intercepts(coefficients), (origin, origin))
        self.assertNotEqual(origin, second)
        self.assertTrue(same_line(line_through(origin, second), coefficients))
        self.assertEqual(equation(self.math["q27-substitution"]), (0, 0, 0))
        note = self.original_note("q27-origin")
        self.assertIn("एका बिंदूवरून एकच रेषा ठरत नाही", note)
        self.assertIn("नव्याने जोडलेली", note)
        self.assertIn("स्रोताने फक्त वरील उत्तर-आकृती दिली", note)

    def test_20_fourteen_bidirectional_supplied_pairs_thirteen_missing(self):
        supplied, missing, graphical = [], [], []
        for number, example in enumerate(self.exercises, 1):
            source_solution = example.find(C + "solution")
            target = self.question(number)
            solutions = [e for e in target.iter() if e.get("class") == "solution"]
            missing_notes = [e for e in target.iter() if e.get("class") == "source-answer-missing"]
            if source_solution is None:
                missing.append(number)
                self.assertEqual(solutions, [])
                self.assertEqual(len(missing_notes), 1)
                self.assertEqual(missing_notes[0].get("data-kind"), "original")
                self.assertIn("स्रोतात या प्रश्नाचे उत्तर दिलेले नाही", text(missing_notes[0]))
            else:
                supplied.append(number)
                self.assertEqual(missing_notes, [])
                self.assertEqual([e.get("id") for e in solutions], [source_solution.get("id")])
                problem_id = example.find(C + "problem").get("id")
                solution_id = source_solution.get("id")
                self.assertEqual([a.get("href") for a in self.target[problem_id].iter("a")], ["#" + solution_id])
                self.assertEqual([a.get("href") for a in self.target[solution_id].iter("a")], ["#" + problem_id])
                if source_solution.find(".//" + C + "image") is not None:
                    graphical.append(number)
        self.assertEqual(supplied, list(range(1, 28, 2)))
        self.assertEqual(missing, list(range(2, 28, 2)))
        self.assertEqual(graphical, [1, 5, 7, 9, 11, 13, 15, 23, 25, 27])

    def test_21_all_12_canonical_assets_and_original_media_roles(self):
        self.assertEqual(list(self.target_images), list(IMAGES))
        self.assertEqual(set(self.config["assets"]), {filename(i) for i in IMAGES})
        total = 0
        for number, (question, role, _, size, sha) in IMAGES.items():
            name = filename(number)
            record = self.config["assets"][name]
            self.assertEqual(record, {"path": f"assets/{UNIT}/{name}", "sha256": sha, "mime": "image/jpeg"})
            data = inside(BASE, record["path"]).read_bytes()
            self.assertEqual((len(data), digest(data)), (size, sha))
            self.assertTrue(data.startswith(b"\xff\xd8\xff"))
            self.assertEqual(data, self.source_images["en", number])
            self.assertEqual(data, self.source_images["id", number])
            source_role = self.exercises[question - 1].find(C + role)
            media = next(source_role.iter(C + "media"))
            target_media = self.target[media.get("id")]
            self.assertEqual(target_media.tag, "figure")
            self.assertIs(target_media.find("img"), self.target_images[number])
            self.assertEqual(target_media.find("img").get("src"), "asset:" + name)
            total += len(data)
        self.assertEqual(total, 850595)

    def test_22_all_24_source_image_records_and_reviewed_bytes(self):
        rows = self.lock["source_images"]
        self.assertEqual(len(rows), 24)
        seen, inventory_rows = set(), []
        for record in rows:
            locale = record["locale"]
            name = record["member"].split("/")[-1]
            number = int(name.removeprefix(PREFIX).removesuffix(SUFFIX))
            self.assertNotIn((locale, number), seen)
            seen.add((locale, number))
            archive, prefix, archive_hash = ARCHIVES[locale]
            data = self.source_images[locale, number]
            self.assertEqual(record["member"], f"{prefix}/media/{name}")
            self.assertEqual(record["archive"], "downloads/mr-Deva-IN/releases/" + archive)
            self.assertEqual(record["archive_sha256"], archive_hash)
            self.assertEqual((record["bytes"], record["sha256"]), (len(data), digest(data)))
            self.assertEqual(record["review_copy"], f"downloads/mr-Deva-IN/source-image-qa/{UNIT}/{locale}-{name}")
            self.assertEqual(inside(WORKSPACE, record["review_copy"]).read_bytes(), data)
            if locale == "en":
                self.assertEqual(record["committed_asset"], f"assets/{UNIT}/{name}")
            inventory_rows.append(locale + "|" + name + "|" + digest(data) + "|" + str(len(data)))
        self.assertEqual(seen, {(locale, n) for locale in ["en", "id"] for n in IMAGES})
        self.assertEqual(inventory(inventory_rows), IMAGE_INVENTORY)
        self.assertEqual(sum(len(b) for b in self.source_images.values()), 1701190)

    def test_23_alt_axes_arrows_and_finite_point_limit(self):
        for number, (_, _, extent, _, _) in IMAGES.items():
            alt = self.target_images[number].get("alt", "")
            self.assertRegex(alt, r"[\u0900-\u097f]")
            self.assertIn(f"−{extent} ते {extent}", alt)
            if number == 349:
                self.assertIn("स्वतंत्र", alt)
                self.assertNotIn("बाण", alt)
            else:
                self.assertIn("बाण", alt)
        for term in self.config["required_terms"]:
            self.assertIn(term, text(self.root))
        self.assertIn("सर्व उकलींची सरळ रेषा", text(self.target[TOPIC]))

    def test_24_links_and_pinned_title_backreference(self):
        links = [e.get("href") for e in self.root.iter("a")]
        local, external = [v for v in links if v.startswith("#")], [v for v in links if not v.startswith("#")]
        self.assertEqual((len(local), len(external)), (34, 3))
        self.assertTrue(all(v[1:] in self.target for v in local))
        backref = "https://openstax.org/books/intermediate-algebra-2e/pages/3-1-graph-linear-equations-in-two-variables"
        self.assertEqual(set(external), {backref, "https://openstax.org/books/intermediate-algebra-2e/pages/3-introduction",
                                        "https://creativecommons.org/licenses/by-nc-sa/4.0/"})
        target_link = self.target[TOPIC].find("h3/a")
        self.assertEqual(target_link.get("data-source-document"), "m81369")
        self.assertEqual(target_link.get("href"), backref)
        for locale in ["en", "id"]:
            source = by_id(self.modules[locale, "m81374"])[TOPIC]
            self.assertEqual([e.attrib for e in source.iter(C + "link")], [{"document": "m81369"}])
            module = self.modules[locale, "m81369"]
            expected_title = "Graph Linear Equations in Two Variables" if locale == "en" else "Menggambar Grafik Persamaan Linear dalam Dua Variabel"
            self.assertEqual(" ".join(text(module.find(C + "title")).split()), expected_title)
            self.assertIn("9d3bc1f0-6330-4e24-b67a-6f07f074d79c", text(module.find(C + "metadata")))
        self.assertIn("त्या विभागाचा पूर्ण मराठी अनुवाद येथे नाही", text(self.target[TOPIC]))
        self.assertIn("इंटरनेट लागते", text(self.target[TOPIC]))
        self.assertIn("CC BY-NC-SA 4.0", text(self.target["credits"]))
        self.assertTrue(all(e.tag not in {"script", "iframe", "video", "audio", "svg"} for e in self.root.iter()))

    def test_25_all_101_witness_pins_and_asset_membership(self):
        witnesses = self.lock["witnesses"]
        self.assertEqual(len(witnesses), 101)
        self.assertEqual(len({w["path"] for w in witnesses}), 101)
        rows = []
        for witness in witnesses:
            data = inside(BASE, witness["path"]).read_bytes()
            self.assertEqual(digest(data), witness["sha256"], witness["path"])
            if "bytes" in witness:
                self.assertEqual(len(data), witness["bytes"], witness["path"])
            rows.append(witness["path"] + "|" + digest(data))
        self.assertEqual(inventory(rows), WITNESS_INVENTORY)
        lookup = {w["path"]: w["sha256"] for w in witnesses}
        for asset in self.config["assets"].values():
            self.assertEqual(lookup[asset["path"]], asset["sha256"])

    def test_26_strict_parser_negative_controls(self):
        self.assertEqual(equation("3x - 2y = 6"), (3, -2, 6))
        self.assertEqual(equation("y=-(4/5)x-1"), (F(4, 5), 1, -1))
        self.assertEqual(equation("y=4/3"), (0, 1, F(4, 3)))
        for invalid in ["x*y=3", "x/x=1", "y=1/0", "y=sin(x)", "y=x**2", "y=x;importos", "y=(x", "x=y=3"]:
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                equation(invalid)
        with self.assertRaises(ValueError):
            points("(1,2) hidden (3,4)")
        with self.assertRaises(ValueError):
            json.loads('{"expected_math":{"q1":"a","q1":"b"}}', object_pairs_hook=unique_object)
        with self.assertRaises(ValueError):
            line_through((F(0), F(0)), (F(0), F(0)))
        with self.assertRaises(ValueError):
            math_text(ET.fromstring(f'<msqrt xmlns="{M[1:-1]}"><mn>4</mn></msqrt>'))
        self.assertFalse(same_line((F(0), F(0), F(0)), (F(1), F(1), F(3))))


if __name__ == "__main__":
    unittest.main(verbosity=2)
