"""MR020 independent source/math regressions, not rendered-reader acceptance.

Real frozen inputs and selected original ZIP members only. Exact Fraction
arithmetic, explicit polynomial coefficients and a strict AST whitelist; no eval.
Manual observations of all eight original rasters are hash-bound, not automated
vision. No writes, downloads, extraction, corpus copies or skipped tests.
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
UNIT = "MR-BRIDGE-020"
C, M = "{http://cnx.rice.edu/cnxml}", "{http://www.w3.org/1998/Math/MathML}"
CHAPTER, TOPIC = "fs-id1167836524742", "fs-id1167826172554"
PREVIOUS, FOLLOWING = "fs-id1167836570304", "fs-id1167836699953"
PINS = {
    "translations/MR-BRIDGE-020.xml": (31109, "29bd937f6d0e23cd68a6c4a1061d7115cc4a5838fa50373a405e951aaf6f57c7"),
    "units/MR-BRIDGE-020.json": (4285, "22051ef0fa149c8a4e0f432a7172d2d23159d08224beb0014f5be1c352fbbe36"),
    "provenance/MR-BRIDGE-020.lock.json": (89571, "6ce2fc3934f8c3b27c229dd0c5623b4bf37893c6ad54e9708f10c53e1c1b2382"),
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
    ("en", "m81373"): (151578, "2b606026c2b34cdf69acfa29bfe4b90abdb6961a322a78c7ec20107e0948b05c"),
    ("id", "m81373"): (143952, "e9e593b31587995170c520b9175f2e0c0cb335282c951bb1d769f775344311ee"),
}
INVENTORIES = {
    "fragments": "4df9fd350ea71db18111de191212ed9d55ad930ed6fc9162c661b27539da2842",
    "math": "9afa5503d7e4d178b9529c684b3c2abf899129148c050b87193a8c714caeec6e",
    "images": "4c3a36a4f7dc0f20e64afae147054b9cb820f57f2d3715fd09818c38611867f8",
    "witnesses": "e377cf07f4d0acf4562f930619f9fa4898f850ced4ccecaa9c6f1a4c539052f3",
}
IMAGE_PINS = {
    (234, "en"): (64160, "cd7fa2289ce16fa4d23665f4a818a268cbec29417e95f122f7975d24bc471c17"),
    (234, "id"): (48878, "d44704c739145fc582b783a84efe51803e1fa3946744660b203435cd812d208d"),
    (235, "en"): (64448, "6bb7f78ff8c0d1dc3024dfc28f6865d3913e02a4f0497d386ceac61d66857e31"),
    (235, "id"): (64448, "6bb7f78ff8c0d1dc3024dfc28f6865d3913e02a4f0497d386ceac61d66857e31"),
    (236, "en"): (59305, "b22f9f064d0a5ae59fc27c4cfa6c1bbf07ce274d1751eec2891b0d9c903c0a47"),
    (236, "id"): (59305, "b22f9f064d0a5ae59fc27c4cfa6c1bbf07ce274d1751eec2891b0d9c903c0a47"),
    (237, "en"): (67142, "67d75bb3b5ba3975b3ad5a6ccd19044025c0faf9f5ec3ad81332f59dd6a3f511"),
    (237, "id"): (67142, "67d75bb3b5ba3975b3ad5a6ccd19044025c0faf9f5ec3ad81332f59dd6a3f511"),
}
IMAGE_QUESTIONS = {234: 3, 235: 4, 236: 7, 237: 8}
# Actual text pairs and personally observed canonical arrows/points, not a grid.
RELATIONS = {
    1: [(5, -2), (5, -4), (7, -6), (8, -8), (9, -10)],
    2: [(-3, 7), (-2, 3), (-1, 9), (0, -3), (-1, 8)],
    3: [(1, 20), (2, 25), (3, 30), (4, 35), (5, 40), (6, 45), (7, 50)],
    4: [(-3, 1), (-2, -1), (-2, -3), (0, -1), (0, 4), (4, 3)],
    5: [(9, -5), (4, -3), (1, -1), (0, 0), (1, 1), (4, 3), (9, 5)],
    6: [(-3, 27), (-2, 8), (-1, 1), (0, 0), (1, 1), (2, 8), (3, 27)],
    7: [(-3, 81), (-2, 16), (-1, 1), (0, 0), (1, 1), (2, 16), (3, 81)],
    8: [(-3, -243), (-2, -32), (-1, -1), (0, 0), (1, 1), (2, 32), (3, 243)],
}
EXPECTED_DR = {
    1: ({5, 7, 8, 9}, {-2, -4, -6, -8, -10}),
    2: ({-3, -2, -1, 0}, {7, 3, 9, -3, 8}),
    3: ({1, 2, 3, 4, 5, 6, 7}, {20, 25, 30, 35, 40, 45, 50}),
    4: ({-3, -2, 0, 4}, {-3, -1, 1, 3, 4}),
    5: ({0, 1, 4, 9}, {-5, -3, -1, 0, 1, 3, 5}),
    6: ({-3, -2, -1, 0, 1, 2, 3}, {0, 1, 8, 27}),
    7: ({-3, -2, -1, 0, 1, 2, 3}, {0, 1, 16, 81}),
    8: ({-3, -2, -1, 0, 1, 2, 3}, {-243, -32, -1, 0, 1, 32, 243}),
}
EQUATIONS = {9: "2x+y=-3", 10: "y=x^2", 11: "y=3x-5", 12: "y=x^3", 13: "2x+y^2=4"}
DEFINITIONS = {
    14: ("f", "x", "3x-4"), 15: ("f", "x", "-2x+5"),
    16: ("f", "x", "x^2-5x+6"), 17: ("f", "x", "3x^2-2x+1"),
    18: ("g", "x", "3x^2-5x"), 19: ("F", "x", "2x^2-3x+1"),
    20: ("h", "t", "4|t-1|+2"), 21: ("f", "x", "((x+2)/(x-1))"),
}
ORIGINAL_KEYS = {"ordered-pair", "absolute-value-bars", "corrected-fifth-power-arrow", "rational-input-condition"}
VARS = ("x", "y", "a", "t")
ZERO = (0, 0, 0, 0)
Y = (0, 1, 0, 0)


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
        raise ValueError("path not below expected base")
    return path


def text(node):
    return "".join(node.itertext())


def ids(root):
    return {e.get("id"): e for e in root.iter() if e.get("id")}


def parents(root):
    return {child: e for e in root.iter() for child in e}


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
    value = value.replace("−", "-")
    for source, replacement in [("²", "^2"), ("³", "^3"), ("⁴", "^4"), ("⁵", "^5")]:
        value = value.replace(source, replacement)
    return re.sub(r"\s+", "", value)


def arithmetic_tree(value):
    """Whitelist lexical input, preserving decimal text and function-name case."""
    value = norm(value).replace("^", "**")
    if "|" in value:
        if value.count("|") != 2:
            raise ValueError("one balanced absolute value required")
        before, middle, after = value.split("|")
        if not middle:
            raise ValueError("empty absolute value")
        value = before + "abs(" + middle + ")" + after
    tokens = re.findall(r"abs|\*\*|\d+(?:\.\d+)?|[xyat()+*/-]", value)
    if not value or "".join(tokens) != value:
        raise ValueError("unsupported arithmetic token")
    is_atom = lambda v: v in VARS or bool(re.fullmatch(r"\d+(?:\.\d+)?", v))
    explicit = []
    for token in tokens:
        if explicit and (is_atom(explicit[-1]) or explicit[-1] == ")") and (
                is_atom(token) or token in {"(", "abs"}):
            explicit.append("*")
        explicit.append(token)
    code = "".join(explicit)
    try:
        tree = ast.parse(code, mode="eval")
    except SyntaxError as exc:
        raise ValueError("malformed arithmetic") from exc
    return tree.body, code


def clean(poly):
    return {powers: F(coefficient) for powers, coefficient in poly.items() if coefficient}


def p_add(first, second, sign=1):
    result = dict(first)
    for powers, coefficient in second.items():
        result[powers] = result.get(powers, F(0)) + sign * coefficient
    return clean(result)


def p_scale(poly, coefficient):
    return clean({powers: value * coefficient for powers, value in poly.items()})


def p_mul(first, second):
    result = {}
    for p1, c1 in first.items():
        for p2, c2 in second.items():
            powers = tuple(a + b for a, b in zip(p1, p2))
            result[powers] = result.get(powers, F(0)) + c1 * c2
    return clean(result)


def polynomial_node(node, code):
    if isinstance(node, ast.Constant) and type(node.value) in {int, float}:
        return clean({ZERO: F(ast.get_source_segment(code, node))})
    if isinstance(node, ast.Name) and node.id in VARS:
        return {tuple(int(v == node.id) for v in VARS): F(1)}
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        return p_scale(polynomial_node(node.operand, code), -1 if isinstance(node.op, ast.USub) else 1)
    if isinstance(node, ast.BinOp):
        first, second = polynomial_node(node.left, code), polynomial_node(node.right, code)
        if isinstance(node.op, ast.Add):
            return p_add(first, second)
        if isinstance(node.op, ast.Sub):
            return p_add(first, second, -1)
        if isinstance(node.op, ast.Mult):
            return p_mul(first, second)
        if isinstance(node.op, ast.Div):
            if set(second) != {ZERO} or not second[ZERO]:
                raise ValueError("not polynomial division by a nonzero constant")
            return p_scale(first, 1 / second[ZERO])
        if isinstance(node.op, ast.Pow):
            exponent = second.get(ZERO, F(0))
            if any(p != ZERO for p in second) or exponent.denominator != 1 or not 0 <= exponent <= 5:
                raise ValueError("unsupported polynomial exponent")
            result = {ZERO: F(1)}
            for _ in range(int(exponent)):
                result = p_mul(result, first)
            return result
    raise ValueError("unsupported polynomial form")


def polynomial(value):
    return polynomial_node(*arithmetic_tree(value))


def numeric(value, bindings=None):
    bindings = {} if bindings is None else {k: F(v) for k, v in bindings.items()}
    root, code = arithmetic_tree(value)

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) in {int, float}:
            return F(ast.get_source_segment(code, node))
        if isinstance(node, ast.Name) and node.id in bindings and node.id in VARS:
            return bindings[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            return visit(node.operand) * (-1 if isinstance(node.op, ast.USub) else 1)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "abs":
            if len(node.args) != 1 or node.keywords:
                raise ValueError("absolute-value arity")
            return abs(visit(node.args[0]))
        if isinstance(node, ast.BinOp):
            first, second = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                return first + second
            if isinstance(node.op, ast.Sub):
                return first - second
            if isinstance(node.op, ast.Mult):
                return first * second
            if isinstance(node.op, ast.Div):
                if not second:
                    raise ValueError("undefined at zero denominator")
                return first / second
            if isinstance(node.op, ast.Pow):
                if second.denominator != 1 or not 0 <= second <= 5:
                    raise ValueError("unsupported exponent")
                return first ** int(second)
        raise ValueError("unsupported numeric arithmetic or unbound variable")

    return visit(root)


def equation(value):
    parts = norm(value).split("=")
    if len(parts) != 2:
        raise ValueError("one equality required")
    return p_add(polynomial(parts[0]), polynomial(parts[1]), -1)


def unique_y(value):
    poly = equation(value)
    y_terms = {p: c for p, c in poly.items() if p[1]}
    if set(y_terms) != {Y} or any(p[2] or p[3] for p in poly):
        raise ValueError("not a constant nonzero coefficient times y plus an x polynomial")
    return p_scale({p: c for p, c in poly.items() if not p[1]}, -1 / y_terms[Y])


def definition(value):
    parts = norm(value).rstrip(".;").split("=")
    if len(parts) != 2:
        raise ValueError("one function definition required")
    left = re.fullmatch(r"([fFgh])\(([xt])\)", parts[0])
    if left is None:
        raise ValueError("unsupported function definition")
    arithmetic_tree(parts[1])
    return left[1], left[2], parts[1]


def call(value):
    match = re.fullmatch(r"([fFgh])\((.+)\)", norm(value).rstrip(".;"))
    if match is None:
        raise ValueError("one function call required")
    arithmetic_tree(match[2])
    return match[1], match[2]


def evaluate_definition(definition_text, call_text):
    name, variable, body = definition(definition_text)
    called_name, argument = call(call_text)
    if name != called_name:
        raise ValueError("case-sensitive function identity mismatch")
    return numeric(body, {variable: numeric(argument)})


def substitute_name(poly, old, new):
    if any(p[VARS.index(new)] for p in poly):
        raise ValueError("replacement name already present")
    result = {}
    for powers, coefficient in poly.items():
        changed = list(powers)
        changed[VARS.index(new)] = changed[VARS.index(old)]
        changed[VARS.index(old)] = 0
        result[tuple(changed)] = coefficient
    return clean(result)


def pairs(value, braces=False):
    value = norm(value)
    if braces:
        if not (value.startswith("{") and value.endswith("}")):
            raise ValueError("complete relation braces required")
        value = value[1:-1]
    expression = r"\((-?\d+),(-?\d+)\)"
    if not re.fullmatch(expression + r"(?:," + expression + r")*,?", value):
        raise ValueError("unsupported or malformed ordered-pair sequence")
    return [tuple(map(F, row)) for row in re.findall(expression, value)]


def set_values(value):
    value = norm(value)
    if value.startswith(("D:", "R:")):
        value = value[2:]
    if not re.fullmatch(r"\{-?\d+(?:,-?\d+)*\}", value):
        raise ValueError("unsupported set")
    values = list(map(F, value[1:-1].split(",")))
    if len(values) != len(set(values)):
        raise ValueError("duplicate set value")
    return values


def domain_range(relation):
    return {x for x, _ in relation}, {y for _, y in relation}


def is_function(relation):
    outputs = {}
    for x, y in relation:
        outputs.setdefault(x, set()).add(y)
    return bool(outputs) and all(len(values) == 1 for values in outputs.values())


def math_text(node):
    name = node.tag.removeprefix(M)
    if name in {"math", "mrow"}:
        return "".join(math_text(child) for child in node)
    if name in {"mn", "mi", "mo", "mtext"} and not list(node):
        return node.text or ""
    if name == "msup" and len(node) == 2 and node[1].tag == M + "mn":
        exponent = math_text(node[1])
        if not re.fullmatch(r"[0-5]", exponent):
            raise ValueError("unsupported MathML exponent")
        return math_text(node[0]) + "^" + exponent
    if name == "mfrac" and len(node) == 2:
        numerator, denominator = map(math_text, node)
        return "((" + numerator + ")/(" + denominator + "))"
    raise ValueError("unsupported MathML")


def image_name(number):
    return f"CNX_IntAlg_Figure_03_06_{number}_img_new.jpg"


class Unit20MathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (BASE / "translations" / f"{UNIT}.xml").read_bytes()
        cls.root = ET.fromstring(cls.raw)
        cls.target, cls.target_parents = ids(cls.root), parents(cls.root)
        cls.config = json.loads((BASE / "units" / f"{UNIT}.json").read_text("utf-8"), object_pairs_hook=unique_object)
        cls.lock = json.loads((BASE / "provenance" / f"{UNIT}.lock.json").read_text("utf-8"), object_pairs_hook=unique_object)
        cls.math_nodes = [e for e in cls.root.iter() if e.get("data-check")]
        cls.math = {e.get("data-check"): text(e) for e in cls.math_nodes}
        cls.module_bytes, cls.modules, cls.image_bytes = {}, {}, {}
        for locale, (archive, prefix, _) in ARCHIVES.items():
            with zipfile.ZipFile(WORKSPACE / "downloads/mr-Deva-IN/releases" / archive) as zipped:
                for module in ["m81374", "m81373"]:
                    data = zipped.read(f"{prefix}/modules/{module}/index.cnxml")
                    cls.module_bytes[locale, module] = data
                    cls.modules[locale, module] = ET.fromstring(data)
                for number in IMAGE_QUESTIONS:
                    cls.image_bytes[number, locale] = zipped.read(f"{prefix}/media/{image_name(number)}")
        cls.sources = {loc: ids(cls.modules[loc, "m81374"]) for loc in ARCHIVES}
        cls.blocks = [e for e in cls.sources["en"][TOPIC] if e.tag != C + "title"]
        cls.exercises = [e for e in cls.blocks if e.tag == C + "exercise"]
        cls.images = {number: next(e for e in cls.root.iter("img") if e.get("src") == "asset:" + image_name(number))
                      for number in IMAGE_QUESTIONS}

    def exercise(self, number, locale="en"):
        return self.sources[locale][self.exercises[number - 1].get("id")]

    def question(self, number):
        return self.target[self.exercise(number).get("id")]

    def problem(self, number):
        return self.target[self.exercise(number).find(C + "problem").get("id")]

    def source_solution(self, number, locale="en"):
        return self.exercise(number, locale).find(C + "solution")

    def target_solution(self, number):
        return self.target[self.source_solution(number).get("id")]

    def qmath(self, number):
        return [text(e) for e in self.problem(number).iter() if e.get("data-check")]

    def answer_math(self, number):
        return [text(e) for e in self.target_solution(number).iter() if e.get("data-check")]

    def source_alt(self, number, locale):
        return self.exercise(IMAGE_QUESTIONS[number], locale).find(".//" + C + "media").get("alt")

    def target_relation(self, number):
        if number in {1, 2, 5, 6}:
            return pairs("".join(self.qmath(number)), braces=True)
        if number == 4:
            alt = norm(self.images[235].get("alt"))
            return [tuple(map(F, row)) for row in re.findall(r"\((-?\d+),(-?\d+)\)", alt)]
        image_number = {3: 234, 7: 236, 8: 237}[number]
        return [tuple(map(F, row)) for row in re.findall(r"(-?\d+)→(-?\d+)", norm(self.images[image_number].get("alt")))]

    def test_01_frozen_pins_unicode_and_config(self):
        for path, pin in PINS.items():
            data = inside(BASE, path).read_bytes()
            self.assertEqual((len(data), sha(data)), pin)
        self.assertEqual((self.root.tag, self.root.get("id"), self.root.get("lang")), ("article", UNIT, "mr-Deva-IN"))
        value = self.raw.decode("utf-8")
        self.assertNotIn("\ufffd", value)
        self.assertEqual(unicodedata.normalize("NFC", value), value)
        self.assertEqual((self.lock["unit"], self.lock["locale"]), (UNIT, "mr-Deva-IN"))
        for key, expected in {"source_count": 33, "translated_practice_items": 21, "translated_worked_examples": 0,
                              "translated_definitions": 0, "translated_resource_notes": 0,
                              "original_practice_items": 0, "question_ids": []}.items():
            self.assertEqual(self.config[key], expected)

    def test_02_actual_module_and_backreference_member_pins(self):
        for key, expected in MODULE_PINS.items():
            self.assertEqual((len(self.module_bytes[key]), sha(self.module_bytes[key])), expected)

    def test_03_complete_thirty_three_block_boundary(self):
        for source in self.sources.values():
            topics = source[CHAPTER].findall(C + "section")
            self.assertEqual(len(topics), 6)
            self.assertEqual([e.get("id") for e in topics[3:6]], [PREVIOUS, TOPIC, FOLLOWING])
            selected = [e for e in source[TOPIC] if e.tag != C + "title"]
            self.assertEqual((len(selected), selected[0].get("id"), selected[-1].get("id")),
                             (33, "fs-id1167836486019", "fs-id1167829786785"))
            self.assertEqual(len(list(source[TOPIC].iter(C + "table"))), 0)
        for identifier in [PREVIOUS, FOLLOWING, "fs-id1167836628671"]:
            self.assertNotIn(identifier, self.target)

    def test_04_all_sixty_six_frozen_fragment_shapes_and_order(self):
        expected = [e.get("id") for e in self.blocks]
        records = self.lock["source_selections"]
        self.assertEqual([r["target_id"] for r in records], expected)
        locators = ["A20:m81374#" + identifier for identifier in expected]
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
                loc = source["locale"]
                archive, prefix, digest = ARCHIVES[loc]
                self.assertEqual(source["archive"], "downloads/mr-Deva-IN/releases/" + archive)
                self.assertEqual(source["archive_sha256"], digest)
                self.assertEqual(source["member"], f"{prefix}/modules/m81374/index.cnxml")
                self.assertEqual(source["module_sha256"], MODULE_PINS[loc, "m81374"][1])
                data = inside(BASE, source["fragment_path"]).read_bytes()
                self.assertEqual(sha(data), source["fragment_sha256"])
                self.assertEqual(sha(data), witnesses[source["fragment_path"]])
                self.assertEqual(shape(ET.fromstring(data)), shape(self.sources[loc][record["target_id"]]))
                rows.append(record["target_id"] + "|" + loc + "|" + sha(data))
                size += len(data)
        self.assertEqual((len(rows), size, inventory(rows)), (66, 47046, INVENTORIES["fragments"]))

    def test_05_all_ninety_eight_source_ids_preorder_and_ancestry(self):
        expected = [CHAPTER] + [e.get("id") for e in self.sources["en"][TOPIC].iter() if e.get("id")]
        actual = [e.get("id") for e in self.root.iter() if e.get("id")]
        self.assertEqual((len(expected), len(actual), len(set(actual))), (98, 100, 100))
        allowed = set(expected)
        self.assertEqual([identifier for identifier in actual if identifier in allowed], expected)
        self.assertEqual(set(actual) - allowed, {UNIT, "credits"})
        for loc, source in self.sources.items():
            self.assertEqual([CHAPTER] + [e.get("id") for e in source[TOPIC].iter() if e.get("id")], expected)
            mapping = parents(self.modules[loc, "m81374"])
            for identifier in expected:
                self.assertEqual(nearest(source[identifier], mapping, allowed),
                                 nearest(self.target[identifier], self.target_parents, allowed))

    def test_06_twelve_headings_instructions_and_subpart_markers(self):
        paragraphs = [e for e in self.blocks if e.tag == C + "para"]
        bold = [e for e in paragraphs if e.find(C + "emphasis[@effect='bold']") is not None]
        self.assertEqual((len(paragraphs), len(bold)), (12, 3))
        for source in paragraphs:
            target = self.target[source.get("id")]
            self.assertEqual(target.tag, "p")
            if source.get("id") == "fs-id1167833386368":
                # The source's three-call input line has no prose to translate.
                self.assertEqual(len(list(source.iter(M + "math"))), 3)
                self.assertEqual(len([e for e in target.iter() if e.get("data-check")]), 3)
            else:
                self.assertRegex(text(target), r"[\u0900-\u097f]")
            self.assertEqual(target.find("strong") is not None, source in bold)
            for loc in ARCHIVES:
                self.assertEqual(re.findall("[ⓐⓑⓒ]", text(self.sources[loc][source.get("id")])),
                                 re.findall("[ⓐⓑⓒ]", text(target)))
        self.assertEqual(len(self.exercises), 21)
        for number in range(1, 22):
            self.assertEqual(text(self.question(number).find("h4")), f"प्रश्न {number}")

    def test_07_all_forty_nine_strings_and_thirty_four_source_mathml(self):
        self.assertEqual((len(self.math_nodes), len(self.math)), (49, 49))
        self.assertEqual(self.math, self.config["expected_math"])
        self.assertEqual(inventory([k + "|" + v for k, v in self.math.items()]), INVENTORIES["math"])
        for loc, source in self.sources.items():
            counts, used = {}, set()
            mapping = parents(source[TOPIC])
            for node in source[TOPIC].iter(M + "math"):
                identifier = nearest(node, mapping, set(source))
                counts[identifier] = counts.get(identifier, 0) + 1
                key = f"src-{identifier}-{counts[identifier]}"
                self.assertEqual(norm(math_text(node)), norm(self.math[key]), (loc, key))
                used.add(key)
            self.assertEqual((sum(counts.values()), len(used)), (34, 34))
            self.assertEqual(set(self.math) - used, {k for k in self.math if k.startswith("literal-")} | ORIGINAL_KEYS)
        self.assertEqual(len([k for k in self.math if k.startswith("literal-")]), 11)
        original = []
        for node in self.math_nodes:
            ancestor = node
            while ancestor in self.target_parents and ancestor.get("data-kind") is None:
                ancestor = self.target_parents[ancestor]
            if ancestor.get("data-kind") == "original":
                original.append(node.get("data-check"))
        self.assertEqual((len(original), set(original)), (4, ORIGINAL_KEYS))

    def test_08_four_text_relations_preserve_order_and_complete_braces(self):
        for number in [1, 2, 5, 6]:
            self.assertEqual(self.target_relation(number), RELATIONS[number])
            for loc in ARCHIVES:
                nodes = self.exercise(number, loc).find(C + "problem").iter(M + "math")
                self.assertEqual(pairs("".join(math_text(e) for e in nodes), braces=True), RELATIONS[number])
            self.assertEqual(len(self.qmath(number)), 2)
            self.assertEqual(len(list(self.problem(number).iter("br"))), 1)

    def test_09_all_twenty_one_mapping_arrows_and_literal_headers(self):
        for number in [3, 7, 8]:
            actual = self.target_relation(number)
            self.assertEqual(actual, RELATIONS[number])
            self.assertEqual(len(actual), 7)
        for x, y in self.target_relation(3):
            self.assertEqual(y, 5 * x + 15)
        for question, power in [(7, 4), (8, 5)]:
            for x, y in self.target_relation(question):
                self.assertEqual(y, x ** power)
        for phrase in ["Age (years)", "Weight (pounds)", "20, 35, 30, 45, 40, 25, 50", "पाउंडमध्ये"]:
            self.assertIn(phrase, self.images[234].get("alt"))
        self.assertIn("0, 1, 16, 81", self.images[236].get("alt"))
        self.assertIn("x⁴", self.images[236].get("alt"))
        self.assertIn("0, 1, 32, 243, −1, −32, −243", self.images[237].get("alt"))
        self.assertIn("x⁵", self.images[237].get("alt"))

    def test_10_all_six_plot_points_axis_window_and_no_interpolation(self):
        actual = self.target_relation(4)
        self.assertEqual(actual, RELATIONS[4])
        self.assertEqual(len(actual), 6)
        for loc in ARCHIVES:
            alt = norm(self.source_alt(235, loc).replace("negative ", "-").replace("negatif ", "-"))
            self.assertEqual([tuple(map(F, p)) for p in re.findall(r"\((-?\d+),(-?\d+)\)", alt)], actual)
        for phrase in ["−6 ते 6", "स्वतंत्र बिंदू", "जोडणाऱ्या रेषा नाहीत"]:
            self.assertIn(phrase, self.images[235].get("alt"))
        self.assertNotIn(F(-6), domain_range(actual)[0])
        self.assertNotIn(F(6), domain_range(actual)[1])
        self.assertNotIn((F(0), F(0)), actual)

    def test_11_all_eight_finite_domains_ranges_and_function_statuses(self):
        for number in range(1, 9):
            actual = self.target_relation(number)
            self.assertEqual(domain_range(actual), EXPECTED_DR[number])
            self.assertEqual(is_function(actual), number in {3, 6, 7, 8})
        self.assertEqual(sum(len(self.target_relation(n)) for n in range(1, 9)), 51)

    def test_12_all_four_supplied_finite_set_answers(self):
        for number in [2, 4, 6, 8]:
            values = self.answer_math(number)
            found_domain, found_range = map(set_values, values[-2:])
            self.assertEqual((set(found_domain), set(found_range)), domain_range(self.target_relation(number)))
            for loc in ARCHIVES:
                source_para = self.source_solution(number, loc).find(C + "para")
                parts = [p.strip() for p in re.split("[ⓐⓑⓒ]", text(source_para)) if p.strip()]
                self.assertEqual([norm(p) for p in parts[-2:]], [norm(p) for p in values[-2:]])
            self.assertEqual(re.findall("[ⓐⓑⓒ]", text(self.target_solution(number))),
                             list("ⓐⓑ") if number == 2 else list("ⓐⓑⓒ"))
        source_order = [(4, 3), (-2, -3), (-2, -1), (-3, 1), (0, -1), (0, 4)]
        self.assertEqual(pairs(self.answer_math(4)[0]), source_order)
        self.assertEqual(set(source_order), set(self.target_relation(4)))
        for loc in ARCHIVES:
            source_first = re.split("[ⓐⓑⓒ]", text(self.source_solution(4, loc).find(C + "para")))[1].strip()
            self.assertEqual(pairs(source_first), source_order)
        self.assertEqual(set_values(self.answer_math(2)[1]), [7, 3, 9, -3, 8])  # source order retained

    def test_13_many_to_one_is_allowed_and_nonfunctions_have_actual_witnesses(self):
        for number in [6, 7]:
            relation = self.target_relation(number)
            self.assertTrue(is_function(relation))
            self.assertEqual(dict(relation)[-1], dict(relation)[1])
            self.assertLess(len(domain_range(relation)[1]), len(domain_range(relation)[0]))
        for number, x, y1, y2 in [(1, 5, -2, -4), (2, -1, 9, 8), (4, -2, -1, -3), (5, 1, -1, 1)]:
            actual = self.target_relation(number)
            self.assertIn((x, y1), actual)
            self.assertIn((x, y2), actual)
            self.assertNotEqual(y1, y2)
            self.assertFalse(is_function(actual))
        for number in [6, 8]:
            self.assertIn("होय", text(self.target_solution(number)))
            for loc in ARCHIVES:
                self.assertIn("yes" if loc == "en" else "ya", text(self.source_solution(number, loc)))

    def test_14_all_five_equation_constraints(self):
        for number, expected in EQUATIONS.items():
            self.assertEqual(len(self.qmath(number)), 1)
            self.assertEqual(equation(self.qmath(number)[0]), equation(expected))
        whole = text(self.target[TOPIC])
        self.assertIn("y हे x चे फलन", whole)
        self.assertIn("x हे y चे फलन आहे का, असा उलटा प्रश्न", whole)

    def test_15_four_function_equations_by_exact_coefficient_form(self):
        # A nonzero constant coefficient of y gives exactly one polynomial
        # output for each real x. No finite sampling is a universal proof.
        solved = {9: "-2x-3", 10: "x^2", 11: "3x-5", 12: "x^3"}
        for number, expected in solved.items():
            self.assertEqual(unique_y(self.qmath(number)[0]), polynomial(expected))
            self.assertEqual(equation(self.qmath(number)[0]).get(Y), F(1))
        for number in [10, 12]:
            self.assertEqual(text(self.target_solution(number).find("p")), "होय")
            for loc in ARCHIVES:
                self.assertEqual(text(self.source_solution(number, loc).find(C + "para")),
                                 "yes" if loc == "en" else "ya")

    def test_16_nonfunction_equation_has_same_input_two_outputs(self):
        actual = self.qmath(13)[0]
        self.assertEqual(equation(actual), polynomial("2x+y^2-4"))
        with self.assertRaises(ValueError):
            unique_y(actual)
        left, right = norm(actual).split("=")
        for y in [F(2), F(-2)]:
            self.assertEqual(numeric(left, {"x": 0, "y": y}), numeric(right))
        self.assertNotEqual(F(2), F(-2))
        # y^2 = 4-2x; domain x<=2. At x=2 the only real output is zero.
        self.assertEqual(polynomial("4-2x"), p_scale(p_add(equation(actual), polynomial("y^2"), -1), -1))
        self.assertEqual(numeric("4-2x", {"x": 2}), 0)
        self.assertLess(numeric("4-2x", {"x": F(5, 2)}), 0)
        self.assertIsNone(self.source_solution(13))

    def test_17_common_evaluation_arguments_and_all_four_f_definitions(self):
        values = [self.math[f"src-fs-id1167833386368-{n}"] for n in range(1, 4)]
        self.assertEqual([call(v) for v in values], [("f", "-2"), ("f", "3"), ("f", "a")])
        for number in range(14, 18):
            self.assertEqual(definition(self.qmath(number)[0]), DEFINITIONS[number])
            self.assertEqual(len(self.qmath(number)), 1)

    def test_18_six_supplied_f_evaluations_including_symbolic_identity(self):
        cases = {14: [-10, 5, "3a-4"], 16: [20, 0, "a^2-5a+6"]}
        for number, expected in cases.items():
            definition_text = self.qmath(number)[0]
            actual = self.answer_math(number)
            self.assertEqual(len(actual), 3)
            for index, argument in enumerate(["-2", "3", "a"]):
                left, right = norm(actual[index]).split("=")
                self.assertEqual(call(left), ("f", argument))
                if index < 2:
                    value = evaluate_definition(definition_text, left)
                    self.assertEqual(value, numeric(right))
                    self.assertEqual(value, expected[index])
                else:
                    symbolic = substitute_name(polynomial(definition(definition_text)[2]), "x", "a")
                    self.assertEqual(symbolic, polynomial(right))
                    self.assertEqual(symbolic, polynomial(expected[index]))
            self.assertEqual(re.findall("[ⓐⓑⓒ]", text(self.target_solution(number))), list("ⓐⓑⓒ"))

    def test_19_omitted_polynomial_evaluations_remain_reviewer_only(self):
        for number, first, second, symbolic in [(15, 9, -1, "-2a+5"), (17, 17, 22, "3a^2-2a+1")]:
            definition_text = self.qmath(number)[0]
            self.assertEqual(evaluate_definition(definition_text, "f(-2)"), first)
            self.assertEqual(evaluate_definition(definition_text, "f(3)"), second)
            self.assertEqual(substitute_name(polynomial(definition(definition_text)[2]), "x", "a"),
                             polynomial(symbolic))
            self.assertIsNone(self.source_solution(number))

    def test_20_all_four_single_evaluation_definitions_and_calls(self):
        calls = {18: ("g", "2"), 19: ("F", "-1"), 20: ("h", "-3"), 21: ("f", "3")}
        answers = {18: F(2), 19: F(6), 20: F(18), 21: F(5, 2)}
        for number in range(18, 22):
            values = self.qmath(number)
            self.assertEqual(len(values), 2)
            self.assertEqual(definition(values[0]), DEFINITIONS[number])
            self.assertEqual(call(values[1]), calls[number])
            self.assertEqual(evaluate_definition(*values), answers[number])

    def test_21_supplied_g_and_absolute_value_answers(self):
        for number, value in [(18, F(2)), (20, F(18))]:
            answer = self.answer_math(number)
            self.assertEqual(len(answer), 1)
            self.assertEqual(numeric(answer[0]), value)
            for loc in ARCHIVES:
                self.assertEqual(numeric(text(self.source_solution(number, loc).find(C + "para"))), value)
        self.assertEqual(numeric("|t-1|", {"t": -3}), 4)
        self.assertEqual(numeric("4|t-1|+2", {"t": -3}), 18)
        self.assertNotEqual(numeric("4(|t|-1)+2", {"t": -3}), 18)
        self.assertEqual(numeric("4|t-1|+2", {"t": 1}), 2)
        self.assertEqual(self.math["absolute-value-bars"], "|u|")

    def test_22_rational_parentheses_denominator_and_excluded_input(self):
        definition_text, evaluation = self.qmath(21)
        name, variable, body = definition(definition_text)
        tree, code = arithmetic_tree(body)
        self.assertIsInstance(tree, ast.BinOp)
        self.assertIsInstance(tree.op, ast.Div)
        self.assertEqual(polynomial_node(tree.left, code), polynomial("x+2"))
        self.assertEqual(polynomial_node(tree.right, code), polynomial("x-1"))
        self.assertEqual(self.math["rational-input-condition"], "x ≠ 1")
        self.assertEqual((name, variable), ("f", "x"))
        self.assertEqual(evaluate_definition(definition_text, evaluation), F(5, 2))
        with self.assertRaises(ValueError):
            evaluate_definition(definition_text, "f(1)")
        self.assertNotEqual(numeric("x+2/x-1", {"x": 3}), F(5, 2))
        self.assertEqual(numeric("x-1", {"x": 1}), 0)
        self.assertIsNone(self.source_solution(21))
        note = text(self.question(21))
        for phrase in ["संपूर्ण छेदाची रास", "प्रश्नात विचारलेले आदान या अटीत बसते", "नवीन स्रोत-उत्तर जोडणे नव्हे"]:
            self.assertIn(phrase, note)

    def test_23_uppercase_F_preserved_not_renamed_to_f(self):
        values = self.qmath(19)
        self.assertEqual(evaluate_definition(*values), F(6))
        self.assertEqual(call(values[1]), ("F", "-1"))
        with self.assertRaises(ValueError):
            evaluate_definition(values[0], "f(-1)")
        for loc in ARCHIVES:
            paragraph = self.exercise(19, loc).find(".//" + C + "para")
            names = [text(e) for e in paragraph.iter(M + "mi") if text(e) in {"f", "F"}]
            self.assertEqual(names, ["F", "F"])
        self.assertIn("मोठे F आणि लहान f यांचा भेद जपा", text(self.target[TOPIC]))
        self.assertIsNone(self.source_solution(19))

    def test_24_ten_source_answer_pairs_and_eleven_omissions(self):
        supplied, missing = [], []
        for number in range(1, 22):
            source = self.source_solution(number)
            question = self.question(number)
            answers = [e for e in question.iter() if e.get("class") == "solution"]
            omissions = [e for e in question.iter() if e.get("class") == "source-answer-missing"]
            if source is None:
                missing.append(number)
                self.assertEqual(answers, [])
                self.assertEqual(len(omissions), 1)
                self.assertEqual(omissions[0].get("data-kind"), "original")
                self.assertIn("स्रोतात या प्रश्नाचे उत्तर दिलेले नाही", text(omissions[0]))
            else:
                supplied.append(number)
                self.assertEqual(omissions, [])
                source_id, problem_id = source.get("id"), self.problem(number).get("id")
                self.assertEqual([e.get("id") for e in answers], [source_id])
                self.assertEqual([e.get("href") for e in self.problem(number).iter("a")], ["#" + source_id])
                self.assertEqual([e.get("href") for e in answers[0].iter("a")], ["#" + problem_id])
                self.assertEqual(self.source_solution(number, "id").get("id"), source_id)
        self.assertEqual(supplied, list(range(2, 21, 2)))
        self.assertEqual(missing, list(range(1, 22, 2)))

    def test_25_original_reminders_do_not_reclassify_source_answers(self):
        intro = text(self.target[TOPIC].find("aside"))
        for phrase in ["प्रांतातील प्रत्येक घटकाला नेमका एक", "भिन्न आदानांना एकच निर्गम",
                       "मूल्यसंच हा सहप्रांताशी आपोआप समान नसतो", "बाण ज्या नोंदीपर्यंत पोहोचतो",
                       "संचात एकच मूल्य पुन्हा पुन्हा", "ते रेषांनी जोडू नका",
                       "अक्षांची चौकट म्हणजे संबंधाचा संपूर्ण प्रांत", "प्रतिस्थापन",
                       "ऋण आदानासाठी कंस", "छेद शून्य होणारे आदान"]:
            self.assertIn(phrase, intro)
        self.assertEqual(self.math["ordered-pair"], "(x, y)")
        self.assertTrue(all(e.get("data-kind") == "original" for e in self.root.iter("figcaption")))
        for number in IMAGE_QUESTIONS.values():
            self.assertEqual(len(self.qmath(number)), 0)
        self.assertEqual(sum(len(self.answer_math(n)) for n in [14, 16, 18, 20]), 8)

    def test_26_four_assets_and_all_eight_original_image_pins(self):
        self.assertEqual(len(list(self.root.iter("img"))), 4)
        self.assertEqual(set(self.config["assets"]), {image_name(n) for n in IMAGE_QUESTIONS})
        rows, seen = [], set()
        for record in self.lock["source_images"]:
            loc = record["locale"]
            name = record["member"].split("/")[-1]
            number = next(n for n in IMAGE_QUESTIONS if image_name(n) == name)
            data = self.image_bytes[number, loc]
            archive, prefix, digest = ARCHIVES[loc]
            self.assertNotIn((number, loc), seen)
            seen.add((number, loc))
            self.assertEqual((len(data), sha(data)), IMAGE_PINS[number, loc])
            self.assertEqual((record["bytes"], record["sha256"]), IMAGE_PINS[number, loc])
            self.assertEqual(record["member"], f"{prefix}/media/{name}")
            self.assertEqual(record["archive"], "downloads/mr-Deva-IN/releases/" + archive)
            self.assertEqual(record["archive_sha256"], digest)
            self.assertEqual(record["locator"], "A20:m81374#" + self.exercise(IMAGE_QUESTIONS[number]).get("id"))
            self.assertEqual(record["review_copy"], f"downloads/mr-Deva-IN/source-image-qa/{UNIT}/{loc}-{name}")
            self.assertEqual(inside(WORKSPACE, record["review_copy"]).read_bytes(), data)
            rows.append(loc + "|" + name + "|" + sha(data) + "|" + str(len(data)))
        self.assertEqual(seen, set(IMAGE_PINS))
        self.assertEqual(inventory(rows), INVENTORIES["images"])
        self.assertEqual(sum(len(data) for data in self.image_bytes.values()), 494828)
        for number, question in IMAGE_QUESTIONS.items():
            name = image_name(number)
            size, digest = IMAGE_PINS[number, "en"]
            expected = {"path": f"assets/{UNIT}/{name}", "sha256": digest, "mime": "image/jpeg"}
            self.assertEqual(self.config["assets"][name], expected)
            data = inside(BASE, expected["path"]).read_bytes()
            self.assertEqual((len(data), sha(data)), (size, digest))
            self.assertEqual(data, self.image_bytes[number, "en"])
            self.assertTrue(data.startswith(b"\xff\xd8\xff"))
            media = self.exercise(question).find(".//" + C + "media")
            self.assertEqual(self.target[media.get("id")].tag, "figure")
            self.assertIs(self.target[media.get("id")].find("img"), self.images[number])
            if number == 234:
                self.assertNotEqual(data, self.image_bytes[number, "id"])
            else:
                self.assertEqual(data, self.image_bytes[number, "id"])
        self.assertEqual(sum(IMAGE_PINS[n, "en"][0] for n in IMAGE_QUESTIONS), 255055)

    def test_27_source_description_differences_and_visible_corrections(self):
        for number, question in [(234, 3), (236, 7), (237, 8)]:
            for loc in ARCHIVES:
                alt = self.source_alt(number, loc).replace("negative ", "-").replace("negatif ", "-")
                expression = r"from (-?\d+) to (-?\d+)" if loc == "en" else r"(-?\d+) ke (-?\d+)"
                observed = [tuple(map(F, p)) for p in re.findall(expression, alt)]
                expected = list(RELATIONS[question])
                if (number, loc) == (237, "en"):
                    expected[2] = (-1, 1)  # defective alt preserved in the source witness, not target data
                self.assertEqual(observed, expected)
        self.assertEqual(self.math["corrected-fifth-power-arrow"], "−1 → −1")
        self.assertIn((-1, -1), self.target_relation(8))
        self.assertNotIn((-1, 1), self.target_relation(8))
        for phrase in ["EN पर्यायी वर्णनात −1 पासून 1", "प्रत्यक्ष EN आणि ID चित्रांत",
                       "ID वर्णन आणि स्रोत-उत्तरातील मूल्यसंचही", "मूळ चित्र बदललेले नाही"]:
            self.assertIn(phrase, text(self.question(8)))
        for phrase in ["नोंदी चढत्या क्रमात नाहीत", "ID आकृतीत त्या चढत्या क्रमात पुन्हा",
                       "बाणांनी दाखवलेला संबंध तोच", "पाउंडच आहे", "किलोग्रॅममध्ये रूपांतर केलेले नाही",
                       "अद्ययावत वैद्यकीय मार्गदर्शक सारणी नाही"]:
            self.assertIn(phrase, text(self.question(3)))
        self.assertIn("20, 35, 30, 45, 40, 25, and 50", self.source_alt(234, "en"))
        self.assertIn("20, 25, 30, 35, 40, 45, serta 50", self.source_alt(234, "id"))

    def test_28_twenty_four_local_links_three_https_and_original_backreference(self):
        links = [e.get("href") for e in self.root.iter("a")]
        local = [v for v in links if v.startswith("#")]
        external = [v for v in links if not v.startswith("#")]
        self.assertEqual((len(local), len(external)), (24, 3))
        self.assertTrue(all(v[1:] in self.target for v in local))
        url = "https://openstax.org/books/intermediate-algebra-2e/pages/3-5-relations-and-functions"
        self.assertEqual(set(external), {url, "https://openstax.org/books/intermediate-algebra-2e/pages/3-introduction",
                                        "https://creativecommons.org/licenses/by-nc-sa/4.0/"})
        target_link = self.target[TOPIC].find("h3/a")
        self.assertEqual((target_link.get("data-source-document"), target_link.get("href")), ("m81373", url))
        for loc, title in [("en", "Relations and Functions"), ("id", "Relasi dan Fungsi")]:
            source_title = self.sources[loc][TOPIC].find(C + "title")
            self.assertEqual(text(source_title), title)
            self.assertEqual([e.attrib for e in source_title.iter(C + "link")], [{"document": "m81373"}])
            module = self.modules[loc, "m81373"]
            self.assertEqual(text(module.find(C + "title")), title)
            self.assertIn("59fe6dc4-6e09-4a88-aa1c-b5f72bd79a20", text(module.find(C + "metadata")))
            self.assertEqual(len(list(module.find(C + "metadata").iter(C + "item"))), 3)
        intro, credits = text(self.target[TOPIC].find("aside")), text(self.target["credits"])
        for phrase in ["इंटरनेट लागते", "स्थानिक जोडणी असल्याचा दावा नाही"]:
            self.assertIn(phrase, intro)
        for phrase in ["CC BY-NC-SA 4.0", "संबंधित घटकांच्या स्वतंत्र सूचना", FOLLOWING]:
            self.assertIn(phrase, credits)
        for term in self.config["required_terms"]:
            self.assertIn(term, text(self.root))

    def test_29_all_seventy_nine_witnesses_and_offline_xml_media(self):
        records = self.lock["witnesses"]
        self.assertEqual((len(records), len({r["path"] for r in records})), (79, 79))
        rows, lookup = [], {}
        for record in records:
            data = inside(BASE, record["path"]).read_bytes()
            self.assertEqual(sha(data), record["sha256"])
            if "bytes" in record:
                self.assertEqual(len(data), record["bytes"])
            rows.append(record["path"] + "|" + sha(data))
            lookup[record["path"]] = sha(data)
        self.assertEqual(inventory(rows), INVENTORIES["witnesses"])
        for asset in self.config["assets"].values():
            self.assertEqual(lookup[asset["path"]], asset["sha256"])
        self.assertTrue(all(e.tag not in {"script", "svg", "iframe", "audio", "video"} for e in self.root.iter()))
        self.assertTrue(all(e.get("src", "").startswith("asset:") for e in self.root.iter("img")))

    def test_30_strict_parser_and_mathematical_negative_controls(self):
        self.assertEqual(numeric("0.25"), F(1, 4))
        self.assertEqual(polynomial("(x+1)(x-1)"), polynomial("x^2-1"))
        self.assertNotEqual(polynomial("-2x+5"), polynomial("2x+5"))
        self.assertNotEqual(polynomial("-x^2"), polynomial("(-x)^2"))
        self.assertTrue(is_function([(1, 4), (2, 4)]))
        self.assertFalse(is_function([(1, 4), (1, -4)]))
        for value in ["__import__('os')", "sin(x)", "x.y", "x[0]", "x**-1", "x**6", "|x", "||", "1/0", "x+("]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                numeric(value, {"x": 2})
        for value in ["1/x", "|x|", "x**y"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                polynomial(value)
        for value in ["(1,2,3)", "(1,2)junk", "{(1,2)"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                pairs(value)
        with self.assertRaises(ValueError):
            set_values("{1,1}")
        with self.assertRaises(ValueError):
            json.loads('{"math":{"a":1,"a":2}}', object_pairs_hook=unique_object)
        with self.assertRaises(ValueError):
            math_text(ET.fromstring(f'<msqrt xmlns="{M[1:-1]}"><mn>4</mn></msqrt>'))


if __name__ == "__main__":
    unittest.main(verbosity=2)
