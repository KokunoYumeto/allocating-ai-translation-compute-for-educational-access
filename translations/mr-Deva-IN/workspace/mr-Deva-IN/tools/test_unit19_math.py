"""MR019 independent source/math tests; no reader or native-language acceptance.

Uses real frozen XML/config/lock, small selected ZIP members and existing images.
Fraction arithmetic and a whitelisted AST are used, never eval. Pixel observations
were personally made by the reviewer and are hash-bound, not automated vision.
No output files, downloads, extraction, corpus copies or skipped tests.
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
UNIT = "MR-BRIDGE-019"
C, M = "{http://cnx.rice.edu/cnxml}", "{http://www.w3.org/1998/Math/MathML}"
CHAPTER, TOPIC = "fs-id1167836524742", "fs-id1167836570304"
PREVIOUS, FOLLOWING = "fs-id1167836526512", "fs-id1167826172554"
PINS = {
    "translations/MR-BRIDGE-019.xml": (35111, "6526da308eb86745274ff61b66fd162b8319211df9c9d3dcdd5b87323c3986d1"),
    "units/MR-BRIDGE-019.json": (4340, "aecc60b2d9ae157e3adb75c2b240a846ec8dbf53d74d5ef53a862311c3570fcd"),
    "provenance/MR-BRIDGE-019.lock.json": (68689, "35dc46f4ebd7017cf5117091cdcabdefacf10cfd619d65fed23138954c9c3b6f"),
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
    ("en", "m81372"): (128075, "f434123faca9a5dc6fe31d6374098ba6b1138f3afc01889021de797d04f1655b"),
    ("id", "m81372"): (125770, "b46a4e3ffadedf7fedbd3b61766d9177fa7a5b2afe9454e047c29a2d4f97fd24"),
}
INVENTORIES = {
    "fragments": "7e06139f44ccf8f3d2ef72c815253c91389e1cdb7fabe790d02bd93df20c64dd",
    "math": "d1054c7fe4a45fc716ab076548ec2e36d36125d5ffadc3f966581dfb3c862ca5",
    "images": "8aeff9db340ba31a387c5478261b79e8f441e859b3c67670ed36b04e4d0ce76b",
    "witnesses": "43ae02a37fd07e8a97f5b5c47077fb2496466e88478454ef4059fb846732816d",
}
# Question, source role, bytes and SHA of EACH personally inspected EN/ID file.
IMAGES = {
    230: (3, "problem", 79537, "6b26e5539debe5701630f4bf72e250337ea5eefb7c216a7b313513713c0ccabb"),
    231: (4, "problem", 80491, "0c1fa76a22c51fec8ff0d8b5746491b125958abc2f6ea8385de5b0df18392916"),
    232: (5, "problem", 81410, "c325f83ff8b315ad78bd4c416f3fd0d1fc781f94f300505c1d7d91202d9f8b18"),
    233: (6, "problem", 77311, "5f121211a79a3c868243f62ff595a51c662acb6c848504087aa6bf9e2b3e0392"),
    378: (8, "solution", 80369, "8b922a9519cd788a77a994d317d9a892b72e087f0cc4982afbe9029462cf285e"),
    380: (10, "solution", 79109, "28b078e4a5ba79fc00bcf4538dc2926280c0f2068c44cdbd752f9591e3eb6355"),
    382: (12, "solution", 78364, "60f2051aa6f4adb98d243d770907b7628bcc0560cc9a68753220887671ee9a0e"),
    384: (14, "solution", 73136, "6723c490fa5f3292a3c1b8d4746fae14666664fbb3ff7c859b58df9088667c4c"),
}
PREFIX, SUFFIX = "CNX_IntAlg_Figure_03_06_", "_img_new.jpg"
GRAPH_POINTS = {
    230: ((0, 2), (2, 0)), 231: ((0, -3), (3, -1), (6, 1)),
    232: ((0, -4), (-4, 0)), 233: ((0, -3), (2, -2), (6, 0)),
    378: ((0, 3), (4, 2), (8, 1)), 380: ((0, 5), (2, 2), (4, -1)),
    382: ((0, 6), (1, 6), (2, 6)), 384: ((0, 40), (30, 0)),
}
GRAPH_RELATIONS = {
    230: "y<=-x+2", 231: "y>=2/3x-3", 232: "x+y>=-4", 233: "x-2y>=6",
    378: "y<=-1/4x+3", 380: "3x+2y>10", 382: "y<6", 384: "20x+15y>=600",
}
GRAPH_SIDES = {
    230: ("below", (0, 0), (0, 3)), 231: ("above", (0, 0), (0, -4)),
    232: ("above", (0, 0), (0, -5)), 233: ("below", (0, -4), (0, 0)),
    378: ("below", (0, 0), (0, 4)), 380: ("above", (0, 6), (0, 0)),
    382: ("below", (0, 0), (0, 7)), 384: ("above", (40, 40), (0, 0)),
}
QUESTIONS = {
    1: ["y<x-3", "(0,1)", "(-2,-4)", "(5,2)", "(3,-1)", "(-1,-5)"],
    2: ["x+y>4", "(6,1)", "(-3,6)", "(3,2)", "(-5,10)", "(0,0)"],
    3: ["y=-x+2"], 4: ["y=2/3x-3"], 5: ["x+y=-4"], 6: ["x-2y=6"],
    7: ["y>2/5x-4"], 8: ["y<=-1/4x+3"], 9: ["x-y<=5"],
    10: ["3x+2y>10"], 11: ["y<=-3x"], 12: ["y<6"],
    13: ["$500", "$10", "$25", "$500", "(x,y)"], 14: ["600", "20", "15"],
}
ORIGINAL_KEYS = {"inclusive-symbols", "strict-symbols", "origin-test-point",
                 "time-x-domain", "time-y-domain", "atsushi-inclusive-symbol"}
PLAIN_KEYS = {"shanthie-weekly-minimum", "shanthie-swimming-rate", "shanthie-intern-rate",
              "shanthie-minimum-repeat", "atsushi-calories", "atsushi-running-rate", "atsushi-cycling-rate"}
FLIP = {"<": ">", ">": "<", "<=": ">=", ">=": "<=", "=": "="}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def inventory(rows):
    return sha(("\n".join(sorted(rows)) + "\n").encode("utf-8"))


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def inside(base, relative):
    path = (base / relative).resolve()
    if base.resolve() not in path.parents:
        raise ValueError("not a file below the expected base")
    return path


def text(node):
    return "".join(node.itertext())


def ids(root):
    return {e.get("id"): e for e in root.iter() if e.get("id")}


def parents(root):
    return {child: e for e in root.iter() for child in e}


def nearest(node, parent_map, allowed):
    while node in parent_map:
        node = parent_map[node]
        if node.get("id") in allowed:
            return node.get("id")
    return None


def shape(node):
    return (node.tag, tuple(sorted(node.attrib.items())), node.text,
            tuple((shape(child), child.tail) for child in node))


def norm(value):
    return re.sub(r"\s+", "", value.replace("−", "-").replace("≤", "<=").replace("≥", ">="))


def no_punctuation(value):
    value = norm(value)
    return value[:-1] if value.endswith((".", ":")) else value


def add(first, second, sign=1):
    return tuple(a + sign * b for a, b in zip(first, second))


def scaled(poly, factor):
    return tuple(F(factor) * v for v in poly)


def affine(value):
    """Exact coefficients of ax+by+c, with a strict arithmetic AST whitelist."""
    value = norm(value)
    tokens = re.findall(r"\d+(?:\.\d+)?|[xy()+*/-]", value)
    if not value or "".join(tokens) != value:
        raise ValueError("unsupported token")
    explicit = []
    atom = lambda t: t in {"x", "y"} or bool(re.fullmatch(r"\d+(?:\.\d+)?", t))
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
            return (F(0), F(0), F(ast.get_source_segment(code, node)))
        if isinstance(node, ast.Name) and node.id in {"x", "y"}:
            return (F(node.id == "x"), F(node.id == "y"), F(0))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            return scaled(visit(node.operand), -1 if isinstance(node.op, ast.USub) else 1)
        if isinstance(node, ast.BinOp):
            first, second = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                return add(first, second)
            if isinstance(node.op, ast.Sub):
                return add(first, second, -1)
            if isinstance(node.op, ast.Mult):
                if first[:2] == (0, 0):
                    return scaled(second, first[2])
                if second[:2] == (0, 0):
                    return scaled(first, second[2])
                raise ValueError("nonlinear product")
            if isinstance(node.op, ast.Div):
                if second[:2] != (0, 0) or second[2] == 0:
                    raise ValueError("nonconstant or zero denominator")
                return scaled(first, 1 / second[2])
        raise ValueError("unsupported arithmetic")

    return visit(tree)


def scalar(value):
    a, b, c = affine(value)
    if a or b:
        raise ValueError("expected scalar")
    return c


def relation(value):
    value = no_punctuation(value)
    parts = re.split(r"(<=|>=|[<>=])", value)
    if len(parts) != 3 or parts[1] not in FLIP:
        raise ValueError("one comparison required")
    poly = add(affine(parts[0]), affine(parts[2]), -1)
    if poly[:2] == (0, 0):
        raise ValueError("not a two-variable line or half-plane constraint")
    return poly, parts[1]


def canonical(rel):
    poly, op = rel
    divisor = next(v for v in poly[:2] if v)
    return scaled(poly, 1 / divisor), FLIP[op] if divisor < 0 else op


def boundary(rel):
    return rel[0], "="


def boundary_point(rel):
    (a, b, c), _ = rel
    return (F(0), -c / b) if b else (-c / a, F(0))


def signed_value(rel, point):
    (a, b, c), _ = rel
    x, y = map(F, point)
    return a * x + b * y + c


def holds(rel, point):
    value, op = signed_value(rel, point), rel[1]
    return {"<": value < 0, ">": value > 0, "<=": value <= 0,
            ">=": value >= 0, "=": value == 0}[op]


def isolate_y(rel):
    (a, b, c), op = rel
    if not b:
        raise ValueError("vertical boundary cannot isolate y")
    return -a / b, -c / b, FLIP[op] if b < 0 else op


def scale_relation(rel, multiplier):
    multiplier = F(multiplier)
    if not multiplier:
        raise ValueError("zero multiplier loses the inequality")
    return scaled(rel[0], multiplier), FLIP[rel[1]] if multiplier < 0 else rel[1]


def point(value):
    value = norm(value)
    if not (value.startswith("(") and value.endswith(")")):
        raise ValueError("ordered-pair parentheses required")
    parts = value[1:-1].split(",")
    if len(parts) != 2:
        raise ValueError("two coordinates required")
    return tuple(scalar(p) for p in parts)


def semantics(value):
    value = no_punctuation(value)
    if re.search(r"[<>=]", value):
        return "relation", canonical(relation(value))
    if value.startswith("$"):
        if not re.fullmatch(r"\$\d+", value):
            raise ValueError("unsupported money format")
        return "dollars", F(value[1:])
    if "," in value:
        if not (value.startswith("(") and value.endswith(")")):
            raise ValueError("bad ordered pair")
        parts = value[1:-1].split(",")
        if len(parts) != 2:
            raise ValueError("bad pair arity")
        return "pair", tuple(affine(v) for v in parts)
    return "affine", affine(value)


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
    raise ValueError("unsupported MathML")


def image_name(number):
    return f"{PREFIX}{number}{SUFFIX}"


class Unit19MathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (BASE / "translations" / f"{UNIT}.xml").read_bytes()
        cls.root = ET.fromstring(cls.raw)
        cls.target, cls.target_parents = ids(cls.root), parents(cls.root)
        cls.config = json.loads((BASE / "units" / f"{UNIT}.json").read_text(encoding="utf-8"),
                                object_pairs_hook=unique_object)
        cls.lock = json.loads((BASE / "provenance" / f"{UNIT}.lock.json").read_text(encoding="utf-8"),
                              object_pairs_hook=unique_object)
        cls.math_nodes = [e for e in cls.root.iter() if e.get("data-check")]
        cls.math = {e.get("data-check"): text(e) for e in cls.math_nodes}
        cls.modules, cls.module_bytes, cls.image_bytes = {}, {}, {}
        for locale, (archive, prefix, _) in ARCHIVES.items():
            with zipfile.ZipFile(WORKSPACE / "downloads/mr-Deva-IN/releases" / archive) as zipped:
                for module in ["m81374", "m81372"]:
                    data = zipped.read(f"{prefix}/modules/{module}/index.cnxml")
                    cls.module_bytes[locale, module] = data
                    cls.modules[locale, module] = ET.fromstring(data)
                for number in IMAGES:
                    cls.image_bytes[locale, number] = zipped.read(f"{prefix}/media/{image_name(number)}")
        cls.sources = {locale: ids(cls.modules[locale, "m81374"]) for locale in ARCHIVES}
        cls.blocks = [e for e in cls.sources["en"][TOPIC] if e.tag != C + "title"]
        cls.exercises = [e for e in cls.blocks if e.tag == C + "exercise"]
        cls.images = {int(e.get("src").removeprefix("asset:" + PREFIX).removesuffix(SUFFIX)): e
                      for e in cls.root.iter("img")}

    def exercise(self, number, locale="en"):
        return self.sources[locale][self.exercises[number - 1].get("id")]

    def question(self, number):
        return self.target[self.exercises[number - 1].get("id")]

    def problem(self, number):
        return self.target[self.exercise(number).find(C + "problem").get("id")]

    def qmath(self, number):
        return [text(e) for e in self.problem(number).iter() if e.get("data-check")]

    def source_solution(self, number, locale="en"):
        return self.exercise(number, locale).find(C + "solution")

    def graph(self, number):
        return relation(GRAPH_RELATIONS[number])

    def time_solution(self, model, coordinate):
        return all(holds(relation(self.math[k]), coordinate) for k in ["time-x-domain", "time-y-domain"]) and holds(model, coordinate)

    def test_01_frozen_input_bytes_locale_and_unicode(self):
        for path, pin in PINS.items():
            data = inside(BASE, path).read_bytes()
            self.assertEqual((len(data), sha(data)), pin)
        self.assertEqual((self.root.tag, self.root.get("id"), self.root.get("lang")), ("article", UNIT, "mr-Deva-IN"))
        self.assertEqual((self.lock["unit"], self.lock["locale"]), (UNIT, "mr-Deva-IN"))
        value = self.raw.decode("utf-8")
        self.assertNotIn("\ufffd", value)
        self.assertEqual(unicodedata.normalize("NFC", value), value)

    def test_02_selected_module_and_backreference_pins(self):
        for key, pin in MODULE_PINS.items():
            data = self.module_bytes[key]
            self.assertEqual((len(data), sha(data)), pin)

    def test_03_entire_twenty_one_selector_topic(self):
        for source in self.sources.values():
            groups = source[CHAPTER].findall(C + "section")
            self.assertEqual(len(groups), 6)
            self.assertEqual([e.get("id") for e in groups[2:5]], [PREVIOUS, TOPIC, FOLLOWING])
            blocks = [e for e in source[TOPIC] if e.tag != C + "title"]
            self.assertEqual((len(blocks), blocks[0].get("id"), blocks[-1].get("id")),
                             (21, "fs-id1167832951212", "fs-id1167836409564"))
            self.assertEqual(len(list(source[TOPIC].iter(C + "table"))), 0)
        for identifier in [PREVIOUS, FOLLOWING, "fs-id1167836628671"]:
            self.assertNotIn(identifier, self.target)
        for key, value in {"source_count": 21, "translated_practice_items": 14, "translated_worked_examples": 0,
                           "translated_definitions": 0, "translated_resource_notes": 0,
                           "original_practice_items": 0, "question_ids": []}.items():
            self.assertEqual(self.config[key], value)

    def test_04_all_forty_two_fragments_and_locator_order(self):
        expected = [e.get("id") for e in self.blocks]
        records = self.lock["source_selections"]
        self.assertEqual([r["target_id"] for r in records], expected)
        locators = ["A20:m81374#" + v for v in expected]
        self.assertEqual([r["locator"] for r in records], locators)
        selected = [e for e in self.root.iter() if e.get("data-source")]
        self.assertEqual([e.get("id") for e in selected], expected)
        self.assertEqual([e.get("data-source") for e in selected], locators)
        self.assertTrue(all(e.get("data-kind") == "translation" for e in selected))
        witnesses = {r["path"]: r["sha256"] for r in self.lock["witnesses"]}
        rows, size = [], 0
        for record in records:
            self.assertEqual([r["locale"] for r in record["sources"]], ["en", "id"])
            for source in record["sources"]:
                locale = source["locale"]
                archive, prefix, digest = ARCHIVES[locale]
                self.assertEqual(source["archive"], "downloads/mr-Deva-IN/releases/" + archive)
                self.assertEqual(source["archive_sha256"], digest)
                self.assertEqual(source["member"], f"{prefix}/modules/m81374/index.cnxml")
                self.assertEqual(source["module_sha256"], MODULE_PINS[locale, "m81374"][1])
                data = inside(BASE, source["fragment_path"]).read_bytes()
                self.assertEqual(sha(data), source["fragment_sha256"])
                self.assertEqual(witnesses[source["fragment_path"]], sha(data))
                self.assertEqual(shape(ET.fromstring(data)), shape(self.sources[locale][record["target_id"]]))
                rows.append(record["target_id"] + "|" + locale + "|" + sha(data))
                size += len(data)
        self.assertEqual((len(rows), size, inventory(rows)), (42, 36325, INVENTORIES["fragments"]))

    def test_05_original_ids_preorder_and_ancestry(self):
        expected = [CHAPTER] + [e.get("id") for e in self.sources["en"][TOPIC].iter() if e.get("id")]
        actual = [e.get("id") for e in self.root.iter() if e.get("id")]
        self.assertEqual((len(expected), len(actual), len(set(actual))), (77, 79, 79))
        allowed = set(expected)
        self.assertEqual([v for v in actual if v in allowed], expected)
        self.assertEqual(set(actual) - allowed, {UNIT, "credits"})
        for locale, source in self.sources.items():
            self.assertEqual([CHAPTER] + [e.get("id") for e in source[TOPIC].iter() if e.get("id")], expected)
            mapping = parents(self.modules[locale, "m81374"])
            for identifier in expected:
                self.assertEqual(nearest(source[identifier], mapping, allowed),
                                 nearest(self.target[identifier], self.target_parents, allowed), identifier)

    def test_06_seven_headings_and_instructions(self):
        paragraphs = [e for e in self.blocks if e.tag == C + "para"]
        bold = [e for e in paragraphs if e.find(C + "emphasis[@effect='bold']") is not None]
        self.assertEqual((len(paragraphs), len(bold)), (7, 4))
        for source in paragraphs:
            translated = self.target[source.get("id")]
            self.assertEqual(translated.tag, "p")
            self.assertRegex(text(translated), r"[\u0900-\u097f]")
            self.assertEqual(translated.find("strong") is not None, source in bold)

    def test_07_all_thirty_nine_exact_strings_and_original_labels(self):
        self.assertEqual((len(self.math_nodes), len(self.math)), (39, 39))
        self.assertEqual(self.math, self.config["expected_math"])
        self.assertEqual(inventory([k + "|" + v for k, v in self.math.items()]), INVENTORIES["math"])
        original = []
        for node in self.math_nodes:
            ancestor = node
            while ancestor in self.target_parents and ancestor.get("data-kind") is None:
                ancestor = self.target_parents[ancestor]
            if ancestor.get("data-kind") == "original":
                original.append(node.get("data-check"))
        self.assertEqual((len(original), set(original)), (6, ORIGINAL_KEYS))

    def test_08_all_twenty_six_source_mathml_items(self):
        for locale, source in self.sources.items():
            counts, used = {}, set()
            mapping = parents(source[TOPIC])
            for node in source[TOPIC].iter(M + "math"):
                identity = nearest(node, mapping, set(source))
                counts[identity] = counts.get(identity, 0) + 1
                key = f"src-{identity}-{counts[identity]}"
                self.assertEqual(semantics(math_text(node)), semantics(self.math[key]), (locale, key))
                used.add(key)
            self.assertEqual(sum(counts.values()), 26)
            self.assertEqual(set(self.math) - used, ORIGINAL_KEYS | PLAIN_KEYS)

    def test_09_all_fourteen_question_constraints(self):
        self.assertEqual(len(self.exercises), 14)
        source_math = 0
        for number, expected in QUESTIONS.items():
            actual = self.qmath(number)
            self.assertEqual([semantics(v) for v in actual], [semantics(v) for v in expected], number)
            self.assertEqual(text(self.question(number).find("h4")), f"प्रश्न {number}")
            source_math += len(list(self.exercise(number).find(C + "problem").iter(M + "math")))
        self.assertEqual(source_math, 23)

    def test_10_all_ten_ordered_pair_substitutions(self):
        expected = {1: [False, False, False, True, True], 2: [True, False, True, True, False]}
        for number, outcomes in expected.items():
            values = self.qmath(number)
            rel, points = relation(values[0]), list(map(point, values[1:]))
            self.assertEqual([holds(rel, p) for p in points], outcomes)
            for locale in ARCHIVES:
                self.assertEqual(re.findall("[ⓐⓑⓒⓓⓔ]", text(self.exercise(number, locale).find(C + "problem"))),
                                 list("ⓐⓑⓒⓓⓔ"))
            self.assertEqual(re.findall("[ⓐⓑⓒⓓⓔ]", text(self.problem(number))), list("ⓐⓑⓒⓓⓔ"))
        self.assertEqual(signed_value(relation(self.qmath(1)[0]), (5, 2)), 0)
        self.assertFalse(holds(relation(self.qmath(1)[0]), (5, 2)))

    def test_11_actual_source_yes_no_answer(self):
        expected = [True, False, True, True, False]
        for locale, yes, no in [("en", "yes", "no"), ("id", "ya", "tidak")]:
            answer = self.source_solution(2, locale)
            found = re.findall(r"\b(?:" + yes + "|" + no + r")\b", text(answer))
            self.assertEqual([v == yes for v in found], expected)
        translated = text(self.target["fs-id1167836621309"])
        self.assertEqual([v == "होय" for v in re.findall("होय|नाही", translated)], expected)
        self.assertEqual(re.findall("[ⓐⓑⓒⓓⓔ]", translated), list("ⓐⓑⓒⓓⓔ"))
        self.assertIsNone(self.source_solution(1))

    def test_12_four_problem_graphs_and_two_supplied_inequalities(self):
        for number in [230, 231, 232, 233]:
            question = IMAGES[number][0]
            original_boundary = relation(self.qmath(question)[0])
            self.assertEqual(original_boundary[1], "=")
            self.assertEqual(canonical(original_boundary), canonical(boundary(self.graph(number))))
            self.assertIn(self.graph(number)[1], {"<=", ">="})
        for question, image_number in [(4, 231), (6, 233)]:
            for locale in ARCHIVES:
                answer = list(self.source_solution(question, locale).iter(M + "math"))
                self.assertEqual(len(answer), 1)
                self.assertEqual(canonical(relation(math_text(answer[0]))), canonical(self.graph(image_number)))

    def test_13_all_six_graphing_prompt_halfplanes(self):
        expected = {
            7: (F(2, 5), -4, ">"), 8: (F(-1, 4), 3, "<="), 9: (1, -5, ">="),
            10: (F(-3, 2), 5, ">"), 11: (-3, 0, "<="), 12: (0, 6, "<"),
        }
        for number, wanted in expected.items():
            self.assertEqual(isolate_y(relation(self.qmath(number)[0])), wanted)
        for number, image_number in [(8, 378), (10, 380), (12, 382)]:
            self.assertEqual(canonical(relation(self.qmath(number)[0])), canonical(self.graph(image_number)))

    def test_14_negative_division_reverses_the_inequality(self):
        cases = [("x-2y>=6", "y<=1/2x-3"), ("x-y<=5", "y>=x-5")]
        for source, solved in cases:
            original, wanted = relation(source), relation(solved)
            self.assertEqual(canonical(original), canonical(wanted))
            b = original[0][1]
            self.assertLess(b, 0)
            transformed = scale_relation(original, 1 / b)
            self.assertEqual(transformed, wanted)
        for multiplier in [F(1, 3), F(7), F(-1, 2), F(-5)]:
            rel = relation(self.qmath(9)[0])
            transformed = scale_relation(rel, multiplier)
            self.assertEqual(transformed[0], scaled(rel[0], multiplier))
            self.assertEqual(transformed[1], rel[1] if multiplier > 0 else FLIP[rel[1]])
            self.assertEqual(canonical(transformed), canonical(rel))
        intro = text(self.target[TOPIC].find("aside"))
        for phrase in ["धन संख्येने", "ऋण संख्येने", "चिन्हाची दिशा उलटते", "शून्याने भागाकार करता येत नाही",
                       "समीकरणांसाठीच्या समान-क्रिया नियमाचा अर्थ"]:
            self.assertIn(phrase, intro)

    def test_15_solid_dashed_boundary_inclusion(self):
        self.assertEqual(self.math["inclusive-symbols"], "≤ किंवा ≥")
        self.assertEqual(self.math["strict-symbols"], "< किंवा >")
        for image_number in IMAGES:
            rel = self.graph(image_number)
            inclusive = rel[1] in {"<=", ">="}
            self.assertEqual(holds(rel, boundary_point(rel)), inclusive)
            alt = self.images[image_number].get("alt")
            self.assertIn("सलग" if inclusive else "तुटक", alt)
            self.assertIn("सीमारेषाही उकलसंचात समाविष्ट आहे" if inclusive else "सीमारेषा उकलसंचात समाविष्ट नाही", alt)
        for number in range(7, 13):
            rel = relation(self.qmath(number)[0])
            self.assertEqual(holds(rel, boundary_point(rel)), number in {8, 9, 11})

    def test_16_all_graph_points_and_shaded_side_observations(self):
        for number, points in GRAPH_POINTS.items():
            rel = self.graph(number)
            self.assertTrue(all(signed_value(rel, p) == 0 for p in points))
            alt = self.images[number].get("alt")
            if number != 382:
                found = [tuple(map(F, p)) for p in re.findall(r"\((-?\d+),(-?\d+)\)", norm(alt))]
                self.assertEqual(found, list(points))
            else:
                self.assertIn("y = 6", alt)
                self.assertIn("आडवी", alt)
            direction, shaded, white = GRAPH_SIDES[number]
            self.assertTrue(holds(rel, shaded))
            self.assertFalse(holds(rel, white))
            self.assertIn("गुलाबी छायांकित", alt)
            self.assertIn("वरच्या" if direction == "above" else "खालील", alt)
            if number != 384:
                self.assertIn("दोन्ही टोकांना बाण", alt)
            self.assertIn("लाल" if number < 300 else "निळी", alt)
            # Source-alternative-text coordinates are checked arithmetically
            # even where its line-style or axis-window description is wrong.
            source_points = ((0, 2), (1, 1), (2, 0)) if number == 230 else (
                ((0, -4), (-2, -2), (-4, 0)) if number == 232 else points)
            question, role, _, _ = IMAGES[number]
            for locale in ARCHIVES:
                source_alt = self.exercise(question, locale).find(C + role).find(".//" + C + "media").get("alt")
                normalized = norm(source_alt.replace("negative ", "-").replace("negatif ", "-"))
                actual = [tuple(map(F, p)) for p in re.findall(r"\((-?\d+),(-?\d+)\)", normalized)]
                self.assertEqual(actual, list(source_points))
                self.assertTrue(all(signed_value(rel, p) == 0 for p in actual))

    def test_17_affine_normal_direction_coefficient_identity(self):
        # F(p0+t*(a,b)) = t*(a*a+b*b) exactly: constant and t coefficient.
        # This is a coefficient argument, not a finite sampled-grid proof.
        for number in IMAGES:
            rel = self.graph(number)
            (a, b, c), op = rel
            p0 = boundary_point(rel)
            constant = a * p0[0] + b * p0[1] + c
            t_coefficient = a * a + b * b
            self.assertEqual(constant, 0)
            self.assertGreater(t_coefficient, 0)
            expected_positive_side = op in {">", ">="}
            positive = (p0[0] + a, p0[1] + b)
            negative = (p0[0] - a, p0[1] - b)
            self.assertEqual(holds(rel, positive), expected_positive_side)
            self.assertEqual(holds(rel, negative), not expected_positive_side)

    def test_18_origin_boundary_is_not_a_side_test(self):
        rel = relation(self.qmath(11)[0])
        origin = point(self.math["origin-test-point"])
        self.assertEqual(origin, (0, 0))
        self.assertEqual(signed_value(rel, origin), 0)
        self.assertTrue(holds(rel, origin))  # inclusive boundary, but not a side selector
        self.assertFalse(holds(rel, (0, 1)))
        self.assertTrue(holds(rel, (0, -1)))
        intro = text(self.target[TOPIC].find("aside"))
        for phrase in ["सीमारेषेवर नसलेला चाचणीबिंदू", "दुसरा बिंदू घ्या",
                       "सीमेवरील बिंदूची उकल म्हणून तपासणी करता येत नाही असा नाही"]:
            self.assertIn(phrase, intro)

    def test_19_shanthie_rates_minimum_and_three_prompt_parts(self):
        values = [F(v[1:]) for v in self.qmath(13)[:4]]
        self.assertEqual(values, [500, 10, 25, 500])
        minimum, swimming, intern, repeated = values
        model = relation(f"{swimming}x+{intern}y>={minimum}")
        self.assertEqual(canonical(model), canonical(relation("10x+25y>=500")))
        for locale in ARCHIVES:
            paragraph = text(self.sources[locale]["fs-id1167836567305"])
            self.assertEqual(list(map(int, re.findall(r"\$(\d+)", paragraph))), [500, 10, 25, 500])
            self.assertIn("at least" if locale == "en" else "sedikitnya", paragraph)
            self.assertIn("hour" if locale == "en" else "jam", paragraph)
        for p in [(50, 0), (0, 20), (25, 10), (F(1, 2), F(99, 5))]:
            self.assertTrue(self.time_solution(model, p))
            self.assertEqual(signed_value(model, p), 0)
        self.assertFalse(self.time_solution(model, (0, 19)))
        self.assertIsNone(self.source_solution(13))  # calculations here are reviewer-only
        for phrase in ["आठवड्याला किमान", "तासाला", "वकिलांच्या कार्यालयात"]:
            self.assertIn(phrase, text(self.problem(13)))
        self.assertEqual(re.findall("[ⓐⓑⓒ]", text(self.problem(13))), list("ⓐⓑⓒ"))

    def test_20_atsushi_model_units_and_unchanged_answers_vary(self):
        minimum, running, cycling = map(scalar, self.qmath(14))
        self.assertEqual((minimum, running, cycling), (600, 20, 15))
        expected = relation(f"{running}x+{cycling}y>={minimum}")
        target = relation(self.math["src-fs-id1167829704681-1"])
        self.assertEqual(canonical(target), canonical(expected))
        for locale in ARCHIVES:
            source_para = self.sources[locale]["fs-id1167836553948"]
            self.assertEqual(list(map(int, re.findall(r"\d+", text(source_para)))), [600, 20, 15])
            self.assertIn("minute" if locale == "en" else "menit", text(source_para))
            answer = self.source_solution(14, locale)
            self.assertEqual(len(list(answer.iter(M + "math"))), 1)
            self.assertEqual(canonical(relation(math_text(next(answer.iter(M + "math"))))), canonical(expected))
            self.assertIn("Answers will vary." if locale == "en" else "Jawaban dapat bervariasi.", text(answer))
        self.assertEqual(self.math["atsushi-inclusive-symbol"], "≥")
        answer = self.target["fs-id1167829704681"]
        self.assertIn("उत्तरे वेगवेगळी असू शकतात", text(answer))
        self.assertEqual(re.findall("[ⓐⓑⓒ]", text(answer)), list("ⓐⓑⓒ"))
        self.assertEqual(len([e for e in answer.iter() if e.get("data-check")]), 1)
        self.assertEqual(re.findall("[ⓐⓑⓒ]", text(self.problem(14))), list("ⓐⓑⓒ"))
        for phrase in ["दर मिनिटाला", "दररोज", "धावतो त्या मिनिटांची"]:
            self.assertIn(phrase, text(self.problem(14)))
        for phrase in ["लक्ष्याइतक्या किंवा त्याहून अधिक", "वेळेचे संयोगही", "दुसऱ्या क्रियेचा कालावधी शून्य",
                       "नवीन तीन उत्तरे जोडलेली नाहीत"]:
            self.assertIn(phrase, text(self.question(14)))

    def test_21_nonnegative_continuous_time_and_window_not_domain(self):
        self.assertEqual(canonical(relation(self.math["time-x-domain"])), canonical(relation("x>=0")))
        self.assertEqual(canonical(relation(self.math["time-y-domain"])), canonical(relation("y>=0")))
        rel = self.graph(384)
        for p in [(0, 40), (30, 0), (15, 20), (F(3, 4), 39), (70, 0)]:
            self.assertTrue(self.time_solution(rel, p))
        for p in [(0, 39), (29, 0), (0, 0), (-1, 50), (40, -1)]:
            self.assertFalse(self.time_solution(rel, p))
        self.assertTrue(holds(rel, (-1, 50)))  # inequality alone is not the physical domain
        whole = text(self.target[TOPIC])
        for phrase in ["वेळ फक्त पूर्णांकातच असावी अशी अट स्रोतात नाही",
                       "अक्षांवरील पात्र बिंदूंसह", "प्रश्न 13 मधील चल तास", "प्रश्न 14 मधील चल मिनिटे",
                       "60 ही मॉडेलमधील वेळेची कमाल मर्यादा नाही"]:
            self.assertIn(phrase, whole)
        for number in [13, 14]:
            for locale in ARCHIVES:
                problem = self.exercise(number, locale).find(C + "problem")
                self.assertEqual([text(e) for e in problem.iter(C + "emphasis")], ["x", "y"])
                self.assertEqual(re.findall("[ⓐⓑⓒ]", text(problem)), list("ⓐⓑⓒ"))
            self.assertEqual([text(e) for e in self.problem(number).iter("em")], ["x", "y"])

    def test_22_seven_source_pairs_and_seven_explicit_omissions(self):
        supplied, omitted, graphical = [], [], []
        for number in range(1, 15):
            source = self.source_solution(number)
            target = self.question(number)
            answers = [e for e in target.iter() if e.get("class") == "solution"]
            omissions = [e for e in target.iter() if e.get("class") == "source-answer-missing"]
            if source is None:
                omitted.append(number)
                self.assertEqual(answers, [])
                self.assertEqual(len(omissions), 1)
                self.assertEqual(omissions[0].get("data-kind"), "original")
                self.assertIn("स्रोतात या प्रश्नाचे उत्तर दिलेले नाही", text(omissions[0]))
            else:
                supplied.append(number)
                self.assertEqual(omissions, [])
                answer_id, problem_id = source.get("id"), self.problem(number).get("id")
                self.assertEqual([e.get("id") for e in answers], [answer_id])
                self.assertEqual([e.get("href") for e in self.problem(number).iter("a")], ["#" + answer_id])
                self.assertEqual([e.get("href") for e in self.target[answer_id].iter("a")], ["#" + problem_id])
                if source.find(".//" + C + "image") is not None:
                    graphical.append(number)
        self.assertEqual((supplied, omitted, graphical), (list(range(2, 15, 2)), list(range(1, 15, 2)), [8, 10, 12, 14]))

    def test_23_all_eight_assets_and_original_media_ancestry(self):
        self.assertEqual((len(list(self.root.iter("img"))), list(self.images)), (8, list(IMAGES)))
        self.assertEqual(set(self.config["assets"]), {image_name(n) for n in IMAGES})
        for number, (question, role, size, digest) in IMAGES.items():
            name = image_name(number)
            expected = {"path": f"assets/{UNIT}/{name}", "sha256": digest, "mime": "image/jpeg"}
            self.assertEqual(self.config["assets"][name], expected)
            data = inside(BASE, expected["path"]).read_bytes()
            self.assertEqual((len(data), sha(data)), (size, digest))
            self.assertTrue(data.startswith(b"\xff\xd8\xff"))
            for locale in ARCHIVES:
                self.assertEqual(data, self.image_bytes[locale, number])
            media = self.exercise(question).find(C + role).find(".//" + C + "media")
            self.assertEqual(self.target[media.get("id")].tag, "figure")
            self.assertIs(self.target[media.get("id")].find("img"), self.images[number])
            self.assertEqual(self.images[number].get("src"), "asset:" + name)
        self.assertEqual(sum(row[2] for row in IMAGES.values()), 629727)

    def test_24_all_sixteen_original_review_pins(self):
        records = self.lock["source_images"]
        self.assertEqual(len(records), 16)
        seen, rows = set(), []
        for record in records:
            locale, name = record["locale"], record["member"].split("/")[-1]
            number = int(name.removeprefix(PREFIX).removesuffix(SUFFIX))
            self.assertNotIn((locale, number), seen)
            seen.add((locale, number))
            archive, prefix, digest = ARCHIVES[locale]
            data = self.image_bytes[locale, number]
            self.assertEqual(record["archive"], "downloads/mr-Deva-IN/releases/" + archive)
            self.assertEqual(record["archive_sha256"], digest)
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
        self.assertEqual(sum(len(v) for v in self.image_bytes.values()), 1259454)

    def test_25_original_dash_discrepancies_and_visible_notes(self):
        for number in [378, 380, 382]:
            question, role, _, _ = IMAGES[number]
            en = self.exercise(question).find(C + role).find(".//" + C + "media").get("alt")
            id_text = self.exercise(question, "id").find(C + role).find(".//" + C + "media").get("alt")
            self.assertIn("dashed", en)
            self.assertNotIn("putus", id_text)
            self.assertEqual(self.graph(number)[1] in {"<=", ">="}, number == 378)
        note = text(self.question(8))
        for phrase in ["EN पर्यायी वर्णनात सीमारेषा तुटक", "प्रत्यक्ष EN आणि ID चित्रांत ती सलग",
                       "ID वर्णनात तुटक असा शब्द नाही", "मूळ चित्र बदललेले नाही"]:
            self.assertIn(phrase, note)
        for question in [10, 12]:
            for phrase in ["EN आणि ID चित्रांत सीमारेषा तुटक", "ID वर्णनात तुटकपणाचा उल्लेख नाही"]:
                self.assertIn(phrase, text(self.question(question)))

    def test_26_axis_ranges_and_384_fifty_to_sixty_correction(self):
        for number, image in self.images.items():
            self.assertIn("0 ते 60" if number == 384 else "−10 ते 10", image.get("alt"))
            self.assertRegex(image.get("alt"), r"[\u0900-\u097f]")
        for locale in ARCHIVES:
            alt = self.exercise(14, locale).find(".//" + C + "media").get("alt")
            self.assertEqual(alt.count("0 to 50" if locale == "en" else "0 hingga 50"), 2)
        note = text(self.question(14))
        for phrase in ["EN आणि ID", "0 ते 50", "0 ते 60", "चित्राबाहेरही असमा"]:
            self.assertIn(phrase, note)
        self.assertIn("पहिल्या चतुर्थांश", self.images[384].get("alt"))
        self.assertEqual([signed_value(self.graph(384), p) for p in [(0, 40), (30, 0)]], [0, 0])

    def test_27_all_links_pinned_m81372_backreference_and_credits(self):
        links = [e.get("href") for e in self.root.iter("a")]
        local, external = [v for v in links if v.startswith("#")], [v for v in links if not v.startswith("#")]
        self.assertEqual((len(local), len(external)), (19, 3))
        self.assertTrue(all(v[1:] in self.target for v in local))
        url = "https://openstax.org/books/intermediate-algebra-2e/pages/3-4-graph-linear-inequalities-in-two-variables"
        self.assertEqual(set(external), {url, "https://openstax.org/books/intermediate-algebra-2e/pages/3-introduction",
                                        "https://creativecommons.org/licenses/by-nc-sa/4.0/"})
        link = self.target[TOPIC].find("h3/a")
        self.assertEqual((link.get("data-source-document"), link.get("href")), ("m81372", url))
        for locale, title in [("en", "Graph Linear Inequalities in Two Variables"),
                               ("id", "Menggambar Grafik Pertidaksamaan Linear dalam Dua Variabel")]:
            source_title = self.sources[locale][TOPIC].find(C + "title")
            self.assertEqual(text(source_title), title)
            self.assertEqual([e.attrib for e in source_title.iter(C + "link")], [{"document": "m81372"}])
            module = self.modules[locale, "m81372"]
            self.assertEqual(text(module.find(C + "title")), title)
            self.assertIn("eccd2fd2-0d20-4486-a61a-9ec728c76cf1", text(module.find(C + "metadata")))
        whole, credits = text(self.target[TOPIC]), text(self.target["credits"])
        for phrase in ["इंटरनेट लागते", "त्या पूर्ण विभागाचा मराठी अनुवाद येथे नाही"]:
            self.assertIn(phrase, whole)
        for phrase in ["CC BY-NC-SA 4.0", "संबंधित घटकांच्या स्वतंत्र सूचना", FOLLOWING]:
            self.assertIn(phrase, credits)
        for term in self.config["required_terms"]:
            self.assertIn(term, text(self.root))

    def test_28_all_fifty_nine_witnesses_and_offline_xml_images(self):
        records = self.lock["witnesses"]
        self.assertEqual((len(records), len({r["path"] for r in records})), (59, 59))
        rows = []
        for record in records:
            data = inside(BASE, record["path"]).read_bytes()
            self.assertEqual(sha(data), record["sha256"])
            if "bytes" in record:
                self.assertEqual(len(data), record["bytes"])
            rows.append(record["path"] + "|" + sha(data))
        self.assertEqual(inventory(rows), INVENTORIES["witnesses"])
        lookup = {r["path"]: r["sha256"] for r in records}
        for asset in self.config["assets"].values():
            self.assertEqual(lookup[asset["path"]], asset["sha256"])
        self.assertTrue(all(e.tag not in {"script", "iframe", "svg", "audio", "video"} for e in self.root.iter()))
        self.assertTrue(all(e.get("src", "").startswith("asset:") for e in self.root.iter("img")))

    def test_29_parser_and_math_mutation_controls(self):
        self.assertEqual(scalar("0.25"), F(1, 4))
        self.assertEqual(semantics("y ≤ −(1/4)x+3."), semantics("4y<=-x+12"))
        self.assertNotEqual(semantics("x-2y>=6"), semantics("y>=1/2x-3"))  # wrong reversal
        self.assertNotEqual(semantics("y<6"), semantics("y<=6"))  # wrong boundary
        self.assertFalse(holds(relation("x+y>4"), (0, 0)))
        self.assertTrue(holds(relation("x+y>4"), (6, 1)))
        for value in ["x*y<2", "x/x>1", "x/0>=1", "x**2<3", "0<x<1", "x<sin(y)", "0<1",
                      "x=__import__('os')", "x<y+(", "x!=y"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                relation(value)
        with self.assertRaises(ValueError):
            scale_relation(relation("x<y"), 0)
        with self.assertRaises(ValueError):
            point("(1,2,3)")
        with self.assertRaises(ValueError):
            isolate_y(relation("x>=3"))
        with self.assertRaises(ValueError):
            json.loads('{"math":{"a":1,"a":2}}', object_pairs_hook=unique_object)
        with self.assertRaises(ValueError):
            math_text(ET.fromstring(f'<msqrt xmlns="{M[1:-1]}"><mn>4</mn></msqrt>'))


if __name__ == "__main__":
    unittest.main(verbosity=2)
