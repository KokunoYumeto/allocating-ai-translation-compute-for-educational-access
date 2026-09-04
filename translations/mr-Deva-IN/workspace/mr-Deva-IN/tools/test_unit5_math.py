"""Independent mathematical/source regression tests for actual MR-BRIDGE-005.

Run with python -B. Stdlib only: no eval, downloads, extraction, builds or writes.
Finite relations are checked exhaustively. Equation claims use exact polynomial
coefficients (not a sampled grid); failures of uniqueness use two real outputs.
Image readings below were visually checked against all four EN and ID rasters.
Fixed EN image hashes bind those readings to pixels; this test does not do OCR,
browser QA, native-speaker review, or a general theorem-proving procedure.
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


BASE = Path(__file__).resolve().parents[1]
UNIT = "MR-BRIDGE-005"
C = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SELECTED_IDS = (
    "fs-id1167836513559", "fs-id1167833060894", "fs-id1167829666517", "fs-id1167836688996",
    "fs-id1167829745706", "fs-id1167833138708", "fs-id1167836552752", "fs-id1167829742787",
    "fs-id1167829741614", "fs-id1167836697708", "fs-id1167833024527", "fs-id1167836705602",
    "fs-id1167836705606", "fs-id1167836480280", "fs-id1167836526018", "fs-id1167833212947",
)
EXERCISE_IDS = tuple(SELECTED_IDS[i] for i in (2, 3, 4, 5, 7, 8, 9, 10, 12, 13, 14, 15))
MODULE_PINS = {
    "en": ("A20-canonical.zip", "osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81373/index.cnxml",
           "2b606026c2b34cdf69acfa29bfe4b90abdb6961a322a78c7ec20107e0948b05c"),
    "id": ("A20-v0.3.0-source.zip", "source/modules/m81373/index.cnxml",
           "e9e593b31587995170c520b9175f2e0c0cb335282c951bb1d769f775344311ee"),
}
IMAGE_HASHES = {
    209: "2c4708d126a4b2973f8d66f6bbcee026342764f917a1a911d47f5498521ffa08",
    210: "2ca4bbd57f42b6014a93278db4f373b36f4c8d83daf79f21fa22f414a7e5ff69",
    211: "580ca185896cb8c30325548d4cacb9fc058c14b36b45d9faf2703f1026d7b6e9",
    212: "899112b8cfcff1d6049555fcccac5d6d4a1a293f431ae44caf7246b59e36e172",
}

# E1-E4: independently read canonical MathML. E5-E8: direct EN pixel readings.
RELATIONS = {
    1: tuple(zip(map(F, range(-3, 4)), map(F, (9, 4, 1, 0, 1, 4, 9)))),
    2: tuple(zip(map(F, (9, 4, 1, 0, 1, 4, 9)), map(F, range(-3, 4)))),
    3: tuple(zip(map(F, range(-3, 4)), map(F, (27, 8, 1, 0, 1, 8, 27)))),
    4: tuple(zip(map(F, range(-3, 4)), map(F, (-27, -8, -1, 0, 1, 8, 27)))),
    5: tuple(zip(map(F, range(-3, 4)), map(F, (3, 2, 1, 0, 1, 2, 3)))),
    6: tuple(zip(map(F, range(-3, 4)), map(F, (9, 4, 1, 0, 1, 4, 9)))),
    7: (("Jenny", "JKim@gmail.com"), ("Jenny", "jenny@aol.com"),
        ("Randy", "Randy@gmail.com"), ("Dennis", "DBrown@aol.com"),
        ("Emily", "ESmith@state.edu"), ("Raul", "RHernandez@state.edu"),
        ("Raul", "Raul@gmail.com")),
    8: (("Jon", "jong@gmail.com"), ("Rachel", "rachel@state.edu"),
        ("Matt", "mattg@gmail.com"), ("Leslie", "leslie@aol.com"),
        ("Chris", "chrisg@gmail.com"), ("Beth", "bethc@gmail.com"), ("Liz", "lizzie@aol.com")),
}
# A polynomial maps (power of x, power of y) to the coefficient in LHS - RHS.
# These explicit coefficients are a second check on both source and target parses.
EQUATIONS = {
    (9, "a"): {(1, 0): 2, (0, 1): 1, (0, 0): 3},
    (9, "b"): {(0, 1): 1, (2, 0): -1},
    (9, "c"): {(1, 0): 1, (0, 2): 1, (0, 0): 5},
    (10, "a"): {(0, 1): 1, (1, 0): -3, (0, 0): 5},
    (10, "b"): {(0, 1): 1, (3, 0): -1},
    (10, "c"): {(1, 0): 2, (0, 2): 1, (0, 0): -4},
    (11, "a"): {(0, 1): 1, (3, 0): -3, (0, 0): -2},
    (11, "b"): {(1, 0): 1, (0, 2): 1, (0, 0): -3},
    (11, "c"): {(1, 0): 3, (0, 1): -2, (0, 0): -6},
    (12, "a"): {(1, 0): 2, (0, 1): -4, (0, 0): -8},
    (12, "b"): {(0, 0): -4, (2, 0): -1, (0, 1): 1},
    (12, "c"): {(0, 2): 1, (1, 0): 1, (0, 0): -5},
}
COUNTEREXAMPLES = {(9, "c"): (-6, 1, -1), (10, "c"): (0, 2, -2),
                   (11, "b"): (2, 1, -1), (12, "c"): (4, 1, -1)}
SOURCE_CORRECTIONS = {"R and y": "Randy", "RHern and ez@state.edu": "RHernandez@state.edu",
                      "DBroen@aol.com": "DBrown@aol.com", "jenny@aol.cvom": "jenny@aol.com",
                      "R and y@gmail.com": "Randy@gmail.com"}


def text(node):
    return "".join(node.itertext()).strip()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def local_path(relative):
    path = (BASE / relative).resolve()
    if not path.is_relative_to(BASE):
        raise ValueError("path escapes language directory")
    return path


def load_sources():
    """Frozen source fragments are preferred; ZIP fallback reads no other member."""
    lock_path = BASE / f"provenance/{UNIT}.lock.json"
    fragments = {}
    if lock_path.is_file():
        lock = read_json(lock_path)
        if [s["target_id"] for s in lock["source_selections"]] != list(SELECTED_IDS):
            raise ValueError("unexpected frozen selection")
        pins = {(w["path"], w["sha256"]) for w in lock["witnesses"]}
        for selection in lock["source_selections"]:
            if selection["locator"] != "A20:m81373#" + selection["target_id"]:
                raise ValueError("source locator/target mismatch")
            for source in selection["sources"]:
                locale = source["locale"]
                if source["module_sha256"] != MODULE_PINS[locale][2]:
                    raise ValueError("source-module pin drift")
                if (source["fragment_path"], source["fragment_sha256"]) not in pins:
                    raise ValueError("fragment missing from witness list")
                raw = local_path(source["fragment_path"]).read_bytes()
                if hashlib.sha256(raw).hexdigest() != source["fragment_sha256"]:
                    raise ValueError("source-fragment hash drift")
                key = (selection["target_id"], locale)
                if key in fragments:
                    raise ValueError("duplicate source fragment")
                fragments[key] = ET.fromstring(raw)
        if set(fragments) != {(sid, locale) for sid in SELECTED_IDS for locale in ("en", "id")}:
            raise ValueError("missing source fragment")
        return lock, fragments
    for locale, (archive, member, expected_sha) in MODULE_PINS.items():
        with zipfile.ZipFile(BASE.parent / "downloads/mr-Deva-IN/releases" / archive) as handle:
            raw = handle.read(member)
        if hashlib.sha256(raw).hexdigest() != expected_sha:
            raise ValueError("source-module hash drift")
        root = ET.fromstring(raw)
        parent = next(p for p in root.iter() if any(n.get("id") == SELECTED_IDS[0] for n in p))
        children = list(parent)
        start = next(i for i, n in enumerate(children) if n.get("id") == SELECTED_IDS[0])
        end = next(i for i, n in enumerate(children) if n.get("id") == "fs-id1167836714017")
        selected = children[start:end]
        if [n.get("id") for n in selected] != list(SELECTED_IDS):
            raise ValueError("source group is not the complete contiguous selection")
        fragments.update({(node.get("id"), locale): node for node in selected})
    return None, fragments


def atom(value):
    value = value.strip().replace("−", "-")
    if re.fullmatch(r"[+-]?[0-9]+", value):
        return F(value)
    if re.fullmatch(r"[A-Za-z]+(?:@[A-Za-z]+\.[A-Za-z]+)?", value):
        return value
    raise ValueError(f"unsupported finite-relation value: {value!r}")


def pairs(display):
    match = re.fullmatch(r"\{(.*)\}", display.strip(), re.S)
    if not match:
        raise ValueError("expected braced relation")
    body = match[1]
    found = list(re.finditer(r"\(([^(),]+),([^(),]+)\)", body))
    if not found or re.sub(r"\([^()]*\)", "", body).strip(" ,\n\r\t"):
        raise ValueError("invalid ordered-pair list")
    return tuple((atom(m[1]), atom(m[2])) for m in found)


def members(display):
    match = re.fullmatch(r"\{([^{}]*)\}", display.strip())
    if not match:
        raise ValueError("expected braced finite set")
    return [atom(value) for value in match[1].split(",")]


def outputs(relation):
    result = {}
    for x, y in relation:
        result.setdefault(x, set()).add(y)
    return result


def is_function(relation):
    return all(len(values) == 1 for values in outputs(relation).values())


def mapping_alt(alt, numeric):
    body = alt.split(":", 1)[1].strip().removesuffix(".")
    result = []
    for row in body.split("," if numeric else ";"):
        left, right = row.strip().split(" ते ")
        result.extend((atom(left), atom(value)) for value in right.split(" आणि "))
    return tuple(result)


def compact_poly(poly):
    return {power: F(value) for power, value in poly.items() if value}


def add(left, right, scale=F(1)):
    result = left.copy()
    for power, value in right.items():
        result[power] = result.get(power, F(0)) + scale * value
    return compact_poly(result)


def multiply(left, right):
    result = {}
    for (a, b), u in left.items():
        for (c, d), v in right.items():
            power = (a + c, b + d)
            result[power] = result.get(power, F(0)) + u * v
    return compact_poly(result)


def normalize_expression(display):
    display = re.sub(r"\s+", "", display).replace("−", "-").replace("·", "*")
    display = display.replace("²", "**2").replace("³", "**3")
    # Restricted textbook implicit multiplication, not arbitrary identifiers.
    return re.sub(r"(?<=[0-9)])(?=[xy(])|(?<=[xy])(?=[xy(])", "*", display)


def polynomial(display):
    """Whitelist AST syntax, then use exact coefficient arithmetic; never eval."""
    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return compact_poly({(0, 0): F(node.value)})
        if isinstance(node, ast.Name) and node.id in ("x", "y"):
            return {(1, 0) if node.id == "x" else (0, 1): F(1)}
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            return {p: v * (-1 if isinstance(node.op, ast.USub) else 1) for p, v in visit(node.operand).items()}
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, (ast.Add, ast.Sub)):
                return add(left, right, F(-1) if isinstance(node.op, ast.Sub) else F(1))
            if isinstance(node.op, ast.Mult):
                return multiply(left, right)
            if isinstance(node.op, ast.Div) and set(right) == {(0, 0)}:
                return compact_poly({p: v / right[(0, 0)] for p, v in left.items()})
            if isinstance(node.op, ast.Pow):
                exponent = right.get((0, 0), F(0))
                if set(right) <= {(0, 0)} and exponent.denominator == 1 and 0 <= exponent <= 4:
                    result = {(0, 0): F(1)}
                    for _ in range(int(exponent)):
                        result = multiply(result, left)
                    return result
        raise ValueError("unsupported polynomial syntax")
    try:
        return visit(ast.parse(normalize_expression(display), mode="eval").body)
    except (SyntaxError, TypeError, ZeroDivisionError) as error:
        raise ValueError("invalid polynomial") from error


def equation(display):
    parts = display.split("=")
    if len(parts) != 2:
        raise ValueError("expected one equality")
    return add(polynomial(parts[0]), polynomial(parts[1]), F(-1))


def mathml_display(node):
    tag = node.tag.removeprefix(M)
    if tag in ("mi", "mn", "mo", "mtext"):
        return text(node)
    if tag == "msup" and len(node) == 2:
        return "(" + mathml_display(node[0]) + ")**(" + mathml_display(node[1]) + ")"
    if tag in ("math", "mrow"):
        return "".join(mathml_display(child) for child in node)
    raise ValueError(f"unsupported source MathML: {tag}")


def unique_y_polynomial(poly):
    """For c*y+p(x)=0, c constant !=0, return the unique y=-p(x)/c.

    This coefficient identity covers every real x: integer-power polynomials
    are defined and single-valued there, and division is by a nonzero constant.
    It is a sufficient criterion for these eight equations, not for all curves.
    """
    c = poly.get((0, 1), F(0))
    if not c or any(b and (a, b) != (0, 1) for a, b in poly):
        raise ValueError("not the supported linear-in-y form")
    return compact_poly({(a, b): -value / c for (a, b), value in poly.items() if b == 0})


def value_at(poly, x, y):
    return sum((coefficient * F(x) ** a * F(y) ** b for (a, b), coefficient in poly.items()), F(0))


def arithmetic_tree(display, x=None, y=None):
    """Keep each printed operation, so an unrelated true equality cannot pass."""
    polynomial(display)  # Enforce the same non-executing syntax whitelist.
    expression = normalize_expression(display)
    for name, value in (("x", x), ("y", y)):
        if value is not None:
            expression = re.sub(rf"\b{name}\b", f"({value})", expression)
    return ast.dump(ast.parse(expression, mode="eval").body, include_attributes=False)


class Unit5MathematicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (BASE / f"translations/{UNIT}.xml").read_bytes()
        cls.root = ET.fromstring(cls.raw)
        cls.config = read_json(BASE / f"units/{UNIT}.json")
        cls.lock, cls.sources = load_sources()
        cls.ids, cls.checks = {}, {}
        for node in cls.root.iter():
            if node.get("id"):
                if node.get("id") in cls.ids:
                    raise ValueError("duplicate XML ID")
                cls.ids[node.get("id")] = node
            if "data-check" in node.attrib:
                key = node.get("data-check")
                if key in cls.checks:
                    raise ValueError("duplicate mathematical check key")
                cls.checks[key] = text(node)
        cls.images = {node.get("src").removeprefix("asset:"): node for node in cls.root.iter("img")}

    def test_real_unit_structure_and_config(self):
        self.assertEqual(self.root.get("id"), UNIT)
        self.assertEqual(self.root.get("lang"), "mr-Deva-IN")
        raw_text = self.raw.decode("utf-8")
        self.assertEqual(unicodedata.normalize("NFC", raw_text), raw_text)
        self.assertNotIn("\ufffd", raw_text)
        self.assertEqual(self.checks, self.config["expected_math"])
        self.assertEqual(len(self.checks), 61)
        self.assertEqual(self.config["source_count"], 16)
        self.assertEqual(self.config["translated_practice_items"], 12)
        self.assertEqual(self.config["translated_worked_examples"], 0)
        self.assertEqual(self.config["original_practice_items"], 0)
        self.assertEqual(self.config["question_ids"], [])

    def test_four_pair_relations_match_both_pinned_mathml_sources(self):
        for n in range(1, 5):
            self.assertEqual(pairs(self.checks[f"e{n}-relation"]), RELATIONS[n])
            for locale in ("en", "id"):
                with self.subTest(exercise=n, locale=locale):
                    problem = self.sources[(EXERCISE_IDS[n - 1], locale)].find(C + "problem")
                    self.assertEqual(pairs(text(problem)), RELATIONS[n])

    def test_four_mapping_alts_preserve_every_visually_read_arrow(self):
        for n in range(5, 9):
            with self.subTest(exercise=n):
                image = self.images[f"CNX_IntAlg_Figure_03_05_{n + 204}_img_new.jpg"]
                actual = mapping_alt(image.get("alt"), numeric=n <= 6)
                self.assertEqual(actual, RELATIONS[n])
                self.assertEqual(len(actual), 7)
                self.assertEqual(len(set(actual)), 7)

    def test_eight_finite_judgments_and_sixteen_domain_range_answers(self):
        for n, relation in RELATIONS.items():
            with self.subTest(exercise=n):
                self.assertEqual(self.checks[f"e{n}-function"], "होय" if is_function(relation) else "नाही")
                for kind, index in (("domain", 0), ("range", 1)):
                    answer = members(self.checks[f"e{n}-{kind}"])
                    self.assertEqual(len(answer), len(set(answer)))
                    self.assertEqual(set(answer), {pair[index] for pair in relation})
        self.assertEqual(outputs(RELATIONS[2])[F(9)], {F(-3), F(3)})
        self.assertEqual(outputs(RELATIONS[7])["Jenny"], {"JKim@gmail.com", "jenny@aol.com"})
        self.assertEqual(outputs(RELATIONS[7])["Raul"], {"RHernandez@state.edu", "Raul@gmail.com"})
        # Many-to-one is still a function; only the actually listed finite domain is used.
        self.assertEqual(outputs(RELATIONS[1])[F(-3)], outputs(RELATIONS[1])[F(3)])
        self.assertNotIn(F(1, 2), outputs(RELATIONS[4]))
        self.assertNotIn(F(4), outputs(RELATIONS[4]))

    def test_all_twelve_equations_match_source_mathml_and_independent_coefficients(self):
        for n in range(9, 13):
            for locale in ("en", "id"):
                source = self.sources[(EXERCISE_IDS[n - 1], locale)].find(C + "problem")
                source_math = list(source.iter(M + "math"))
                self.assertEqual(len(source_math), 3)
                for part, node in zip("abc", source_math):
                    with self.subTest(exercise=n, part=part, locale=locale):
                        expected = EQUATIONS[(n, part)]
                        self.assertEqual(equation(mathml_display(node)), expected)
                        self.assertEqual(equation(self.checks[f"e{n}-{part}-equation"]), expected)

    def test_eight_yes_equations_have_unique_y_by_coefficient_identity(self):
        count = 0
        for key, expected in EQUATIONS.items():
            if key in COUNTEREXAMPLES:
                continue
            count += 1
            n, part = key
            actual = equation(self.checks[f"e{n}-{part}-equation"])
            y_expression = unique_y_polynomial(actual)
            self.assertEqual(y_expression, unique_y_polynomial(expected))
            self.assertFalse(any(b for a, b in y_expression))
            self.assertEqual(self.checks[f"e{n}-{part}-function"], "होय")
            rearranged = self.checks.get(f"e{n}-{part}-rearranged")
            if rearranged:
                chain = rearranged.split("=")
                self.assertEqual(chain[0].strip(), "y")
                for rhs in chain[1:]:
                    self.assertEqual(polynomial(rhs), y_expression, "rearrangement changes a coefficient")
        self.assertEqual(count, 8)

    def test_four_no_equations_have_two_distinct_real_outputs(self):
        for (n, part), (x, y1, y2) in COUNTEREXAMPLES.items():
            with self.subTest(exercise=n, part=part):
                self.assertNotEqual(y1, y2)
                actual = equation(self.checks[f"e{n}-{part}-equation"])
                self.assertEqual(value_at(actual, x, y1), 0)
                self.assertEqual(value_at(actual, x, y2), 0)
                self.assertEqual(self.checks[f"e{n}-{part}-function"], "नाही")
                statements = self.checks[f"e{n}-counterexample"].split(";")
                self.assertEqual(len(statements), 2)
                source_sides = self.checks[f"e{n}-{part}-equation"].split("=")
                for statement, y in zip(statements, (y1, y2)):
                    self.assertEqual(equation(statement), {}, "printed numerical equality is false")
                    for side, source_side in zip(statement.split("="), source_sides):
                        self.assertTrue(set(polynomial(side)) <= {(0, 0)})
                        self.assertEqual(arithmetic_tree(side), arithmetic_tree(source_side, x, y),
                                         "counterexample does not substitute the stated x and y")
                prose = text(self.ids[EXERCISE_IDS[n - 1]]).replace("−", "-")
                for name, value in (("x", x), ("y", y1), ("y", y2)):
                    self.assertRegex(prose, rf"\b{name}\s*=\s*{value}(?![0-9])")
        intro = text(self.ids["equations"])
        self.assertIn("वास्तविक", intro)
        self.assertIn("y हे x चे फलन", intro)
        self.assertIn("ऋण y-मूल्य वगळू नका", intro)

    def test_six_source_answers_match_mathematics_with_only_declared_corrections(self):
        for n in (1, 3, 5, 7, 9, 11):
            for locale in ("en", "id"):
                source = self.sources[(EXERCISE_IDS[n - 1], locale)].find(C + "solution")
                parts = [p.strip() for p in re.split("[ⓐⓑⓒ]", text(source)) if p.strip()]
                self.assertEqual(len(parts), 3)
                yes, no = ("yes", "no") if locale == "en" else ("ya", "tidak")
                if n <= 8:
                    self.assertEqual(parts[0], yes if is_function(RELATIONS[n]) else no)
                    if n == 3 and locale == "en":
                        self.assertEqual(parts[2], "0, 1, 8, 27}")
                        parts[2] = "{" + parts[2]
                    if n == 7 and locale == "en":
                        raw_answer = text(source)
                        for wrong in SOURCE_CORRECTIONS:
                            self.assertIn(wrong, raw_answer)
                        # Longest-first avoids replacing a substring before its full token.
                        for wrong, right in sorted(SOURCE_CORRECTIONS.items(), key=lambda p: -len(p[0])):
                            parts = [p.replace(wrong, right) for p in parts]
                    self.assertEqual(set(members(parts[1])), {x for x, y in RELATIONS[n]})
                    self.assertEqual(set(members(parts[2])), {y for x, y in RELATIONS[n]})
                else:
                    self.assertEqual(parts, [no if (n, p) in COUNTEREXAMPLES else yes for p in "abc"])

    def test_corrections_visible_and_rachel_case_follows_canonical_pixels(self):
        answer3 = self.ids[EXERCISE_IDS[2]]
        notes3 = " ".join(text(p) for p in answer3.iter("p") if p.get("data-kind") == "original")
        self.assertIn("कंस", notes3)
        self.assertIn("दुरुस्ती", notes3)
        self.assertIn("इंडोनेशियन", notes3)
        notes7 = [p for p in self.ids[EXERCISE_IDS[6]].iter("p") if p.get("data-kind") == "original"]
        cited_typos = {text(code) for p in notes7 for code in p.iter("code")}
        self.assertEqual(cited_typos, set(SOURCE_CORRECTIONS))
        for wrong in SOURCE_CORRECTIONS:
            self.assertNotIn(wrong, self.checks["e7-domain"] + self.checks["e7-range"])
        self.assertIn("rachel@state.edu", members(self.checks["e8-range"]))
        self.assertNotIn("Rachel@state.edu", members(self.checks["e8-range"]))
        for locale in ("en", "id"):
            media = next(self.sources[(EXERCISE_IDS[7], locale)].iter(C + "media"))
            self.assertIn("Rachel@state.edu", media.get("alt").replace("state. edu", "state.edu"))
        self.assertIn("लहान r", text(self.ids["fs-id1167833256812"]))
        self.assertFalse(any(a.get("href", "").startswith("mailto:") for a in self.root.iter("a")))

    def test_all_sixteen_blocks_and_fifty_six_original_ids_preserved_in_order(self):
        self.assertEqual([n.get("data-source") for n in self.root.iter() if n.get("data-source")],
                         ["A20:m81373#" + sid for sid in SELECTED_IDS])
        actual_ids = [n.get("id") for n in self.root.iter() if n.get("id", "").startswith("fs-id")]
        for locale in ("en", "id"):
            source_ids = [n.get("id") for sid in SELECTED_IDS for n in self.sources[(sid, locale)].iter() if n.get("id")]
            self.assertEqual(len(source_ids), 56)
            self.assertEqual(len(set(source_ids)), 56)
            self.assertEqual(actual_ids, source_ids)
            for sid in SELECTED_IDS:
                source = self.sources[(sid, locale)]
                target = self.ids[sid]
                self.assertTrue({n.get("id") for n in source.iter() if n.get("id")} <=
                                {n.get("id") for n in target.iter() if n.get("id")})
                for kind in ("problem", "solution"):
                    for part in source.findall(C + kind):
                        child = next(n for n in target if n.get("id") == part.get("id"))
                        self.assertIn(kind, child.get("class", "").split())

    def test_six_preserved_answers_and_six_visibly_new_answers(self):
        counts = {"source": 0, "original": 0}
        for n, sid in enumerate(EXERCISE_IDS, 1):
            answers = [node for node in self.ids[sid].iter() if "solution" in node.get("class", "").split()]
            self.assertEqual(len(answers), 1)
            answer = answers[0]
            for locale in ("en", "id"):
                self.assertEqual(self.sources[(sid, locale)].find(C + "solution") is not None, n % 2 == 1)
            source_answer = self.sources[(sid, "en")].find(C + "solution")
            if source_answer is not None:
                counts["source"] += 1
                self.assertEqual(answer.get("id"), source_answer.get("id"))
                self.assertNotEqual(answer.get("data-kind"), "original")
                self.assertTrue(text(answer.find("h4")).startswith("स्रोतातील उत्तर"))
            else:
                counts["original"] += 1
                self.assertEqual(answer.get("id"), "mr-answer-" + sid)
                self.assertEqual(answer.get("data-kind"), "original")
                self.assertEqual(text(answer.find("h4")), "नव्याने जोडलेले उत्तर")
                self.assertIn("हे उत्तर मूळ स्रोतामध्ये दिलेले नाही", text(answer))
        self.assertEqual(counts, {"source": 6, "original": 6})

    def test_all_twelve_question_answer_links_are_bidirectional(self):
        for sid in EXERCISE_IDS:
            source = self.sources[(sid, "en")]
            problem_id = source.find(C + "problem").get("id")
            source_answer = source.find(C + "solution")
            answer_id = source_answer.get("id") if source_answer is not None else "mr-answer-" + sid
            for start, end in ((problem_id, answer_id), (answer_id, problem_id)):
                self.assertIn("#" + end, [a.get("href") for a in self.ids[start].iter("a") if text(a)])
        for anchor in self.root.iter("a"):
            if anchor.get("href", "").startswith("#"):
                self.assertIn(anchor.get("href")[1:], self.ids)

    def test_four_embedded_assets_are_exact_pinned_visually_read_en_rasters(self):
        self.assertIsNotNone(self.lock, "source/asset freezing is required before unit QA passes")
        assets = self.config.get("assets", {})
        expected_names = {f"CNX_IntAlg_Figure_03_05_{n}_img_new.jpg" for n in IMAGE_HASHES}
        self.assertEqual(set(assets), expected_names)
        self.assertEqual(set(self.images), expected_names)
        self.assertEqual(len(list(self.root.iter("img"))), 4)
        pins = {(item["path"], item["sha256"]) for item in self.lock["witnesses"]}
        for n, expected_sha in IMAGE_HASHES.items():
            name = f"CNX_IntAlg_Figure_03_05_{n}_img_new.jpg"
            asset = assets[name]
            self.assertEqual(asset["mime"], "image/jpeg")
            self.assertEqual(asset["sha256"], expected_sha)
            self.assertIn((asset["path"], expected_sha), pins)
            raw = local_path(asset["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), expected_sha)
            self.assertTrue(raw.startswith(b"\xff\xd8\xff"))
            media = next(self.sources[(EXERCISE_IDS[n - 205], "en")].iter(C + "media"))
            figure = self.ids[media.get("id")]
            self.assertEqual(figure.tag, "figure")
            self.assertEqual(figure.find("img").get("src"), "asset:" + name)
            self.assertEqual(figure.find("figcaption").get("data-kind"), "original")


class ExactParserTests(unittest.TestCase):
    def test_coefficients_signs_and_fractional_rearrangements(self):
        self.assertEqual(polynomial("(3x − 6)/2"), {(1, 0): F(3, 2), (0, 0): F(-3)})
        self.assertEqual(polynomial("(−2)²"), {(0, 0): F(4)})
        self.assertEqual(polynomial("−2²"), {(0, 0): F(-4)})
        self.assertEqual(polynomial("(x + 1)²"), {(2, 0): F(1), (1, 0): F(2), (0, 0): F(1)})
        self.assertEqual(unique_y_polynomial(equation("2x − 4y = 8")), polynomial("x/2 − 2"))

    def test_unsupported_code_and_nonpolynomial_syntax_fail_closed(self):
        for display in ("__import__('os')", "x.real", "abs(x)", "x[0]", "True", "y/x", "1/0", "x**-1", "x**y"):
            with self.subTest(display=display), self.assertRaises(ValueError):
                polynomial(display)
        with self.assertRaises(ValueError):
            pairs("{(1, 2), execute(3)}")
        with self.assertRaises(ValueError):
            atom("R and y")

    def test_uniqueness_criterion_does_not_promote_quadratic_or_variable_divisor(self):
        for display in ("y² = x", "x*y = 1", "x = 0"):
            with self.subTest(display=display), self.assertRaises(ValueError):
                unique_y_polynomial(equation(display))
        self.assertFalse(is_function(((F(0), F(1)), (F(0), F(-1)))))
        self.assertTrue(is_function(((F(-1), F(1)), (F(1), F(1)))))


if __name__ == "__main__":
    unittest.main(verbosity=2)
