"""Independent exact mathematics/source/pixel regression for MR-BRIDGE-009.

Run with python -B. No eval, downloads, extraction, builds, or file writes.
Pixel readings are human-readable agent observations bound to exact image hashes,
not automated image recognition. Browser and native-speaker review are separate.
"""
from collections import defaultdict
from fractions import Fraction as F
import hashlib
from pathlib import Path
import re
import unicodedata
import unittest
import xml.etree.ElementTree as ET
import zipfile

from test_unit6_math import evaluate, mathml_display, read_json


BASE = Path(__file__).resolve().parents[1]
UNIT = "MR-BRIDGE-009"
C = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
CONTEXT_ID = "fs-id1167836610583"
SELECTED_IDS = (
    "fs-id1167826171759", "fs-id1167836614987", "fs-id1167836532939", "fs-id1167836601426",
    "fs-id1167829719636", "fs-id1167829742590", "fs-id1167836362682", "fs-id1167836539582",
    "fs-id1167836378848", "fs-id1167836511080", "fs-id1167836568027", "fs-id1167836683566",
    "fs-id1167833379684", "fs-id1167833369174",
)
MODULE_PINS = {
    "en": ("A20-canonical.zip", "osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81373/index.cnxml",
           "2b606026c2b34cdf69acfa29bfe4b90abdb6961a322a78c7ec20107e0948b05c"),
    "id": ("A20-v0.3.0-source.zip", "source/modules/m81373/index.cnxml",
           "e9e593b31587995170c520b9175f2e0c0cb335282c951bb1d769f775344311ee"),
}
FINITE = (
    ((-3, 27), (-2, 8), (-1, 1), (0, 0), (1, 1), (2, 8), (3, 27)),
    ((9, -3), (4, -2), (1, -1), (0, 0), (1, 1), (4, 2), (9, 3)),
    ((-3, -6), (-2, -4), (-1, -2), (0, 0), (1, 2), (2, 4), (3, 6)),
    ((8, -4), (4, -2), (2, -1), (0, 0), (2, 1), (4, 2), (8, 4)),
    ((27, -3), (8, -2), (1, -1), (0, 0), (1, 1), (8, 2), (27, 3)),
    ((7, -3), (-5, -4), (8, 0), (0, 0), (-6, 4), (-2, 2), (-1, 3)),
)
FINITE_JUDGMENTS = (True, False, True, False, False, True)
MAPPINGS = (
    (("Lydia", "321-549-3327"), ("Lydia", "321-964-7324"), ("Eugene", "427-658-2314"),
     ("Janet", "427-658-2314"), ("Rick", "798-367-8541"), ("Marty", "684-358-7961"), ("Marty", "684-369-7231")),
    (("NBC", "Ellen Degeneres Show"), ("NBC", "Law and Order"), ("NBC", "Tonight Show"),
     ("HGTV", "Property Brothers"), ("HGTV", "House Hunters"), ("HGTV", "Love It or List It"),
     ("HBO", "Game of Thrones"), ("HBO", "True Detective"), ("HBO", "Sesame Street")),
    (("Neal", "753-469-9731"), ("Krystal", "684-369-7231"), ("Kelvin", "231-378-5941"),
     ("George", "123-567-4839"), ("George", "639-847-6971"), ("Christa", "567-534-2970"),
     ("Mike", "567-534-2970"), ("Mike", "798-367-8541")),
)
EQUATIONS = ("2x+y=7", "y=x²+1", "x+y²=3", "4x+y=−3", "x+y²=1", "y−x²=2",
             "x+y²=4", "y=x²−7", "y=5x−4")
EQUATION_JUDGMENTS = (True, True, False, True, False, True, False, True, True)
RULES = {0: "−2x+7", 1: "x²+1", 3: "−4x−3", 5: "x²+2", 7: "x²−7", 8: "5x−4"}
COUNTEREXAMPLES = {2: ((2, 1), (2, -1)), 4: ((0, 1), (0, -1)), 6: ((0, 2), (0, -2))}
PIXEL_FORMULAS = {
    "010a": "y=−2x+7", "010b": "y=−2·3+7", "010c": "y=1",
    "011a": "y=x²+1", "011b": "y=2²+1", "011c": "y=5",
    "012a": "x+y²=3", "012b": "y²=−x+3", "012c": "y²=−2+3", "012d": "y²=1",
}
IMAGE_HASHES = {
    "007_img_new": "e502cd7ed908fe4785dca6fb57d8ccd67425bd56415d7b7972da7ff68fe6d69f",
    "008_img_new": "ac51a11877478d6b2d41ce234dbce4d547465d570816029493f1edd370997cad",
    "009_img_new": "82c31e08740c9fb05b6d9cd632c6b07dc87393b9f44d17e1f6c99143313a1433",
    "010a_img": "3e9b8a4c1cf5ef3b08781e502616bc65a50c873074f50a5b90e483c9d71fcf3a",
    "010b_img": "b2603c67c11a2506987927b736add284a6201e5463f790869bf855c567b4aefd",
    "010c_img": "0a443bc6ded251a53f6ea3fcf1ca4fb70e179913d09b0d4ce197150cefd7bbfa",
    "011a_img": "a5189cb2ddec28ae0cd4f34fddd93bf79cadc72bfb1312ff86859642ad524f21",
    "011b_img": "0dbaf2a19ba23b7767a2f6fbb863c0eb69a20880c38cb8c6793949640a240593",
    "011c_img": "3d9ad0758dd113630c9bf0fa13edfe3d9b8a7ea2eb7f4878b4528a1e5b107858",
    "012a_img": "ea0897c954e00320fb9c4d302c5ea8f9ec886bf0fd723e7a1cf87e9e195bd325",
    "012b_img": "2e2465e139741da30ce67cd6d5e56527a92ca749e46a68cb80127cbbd7ca6780",
    "012c_img": "3453d5ce4efd493a56b47d9c6231ec5258b60297c61f0a221e878532ff13e35d",
    "012d_img": "069c357c2f57f416358582ba677d2c3d2f4d4ab55d55f1c1fefd6ec8d7ee65c0",
}
ID_IMAGE_HASHES = dict(zip(IMAGE_HASHES, (
    "35b658f2c9e7080484b3f7d81a0e3ab0a9c7e22d341f8a03931d368bf8dcc4fb",
    "c0b14a0f5104b6245f0f47b768e9c9c8968190057d8f65ad09c149f08bb328c2",
    "f2ca2c75955f09d5be73d448afe3f270de45c77bfcb7de5fff0b24925cfa8533",
    "a7fd01301eb7c5e12d5421808efd08c61c4ecfd25550e589239a896dd04d26ee",
    "d632a88685815659c287bac0aa9161dc6f4f6253336c9d0f0e6772103be1743c",
    "165e3258e7915415e049b3791aeaff596747247adc3ede9e37ee25a9bb66669c",
    "3067de50b74418d296d2f31e972b9dc60cc9aebc685973318e8f5f2d967532b4",
    "cf5a56fb00b2c8610fcf5b44386559fb59780373443fac5998d4082b6d9b8aff",
    "55e0d152412d55fc919731a8f8beab65814239553d3b094fd8c9216b9f3a06ad",
    "8c3c38ac636b845079f881712d67900065d6a1f7c1477f5dfeb7963ee04355a5",
    "b224e5a4e83e33cafe6ddaf64142057840a03f494e907c14e2d3707c5c6c9246",
    "b67b08ad1043968cd020110bfa31f64730e9e9a002c5b6df0627e8cdb27c4c32",
    "5a7b4663450c3606051912e67e24bc0d0174d7153bead5f5a3da73f2ef51c624",
)))


def text(node):
    return "".join(node.itertext()).strip()


def filename(short):
    return "CNX_IntAlg_Figure_03_05_" + short + ".jpg"


def local_path(relative):
    path = (BASE / relative).resolve()
    if not path.is_relative_to(BASE):
        raise ValueError("path escapes language directory")
    return path


def load_sources():
    lock_path = BASE / f"provenance/{UNIT}.lock.json"
    fragments = {}
    if lock_path.is_file():
        lock = read_json(lock_path)
        if [s["target_id"] for s in lock["source_selections"]] != list(SELECTED_IDS):
            raise ValueError("unexpected source selection")
        witnesses = {(w["path"], w["sha256"]) for w in lock["witnesses"]}
        for selection in lock["source_selections"]:
            if selection["locator"] != "A20:m81373#" + selection["target_id"]:
                raise ValueError("source locator mismatch")
            for source in selection["sources"]:
                locale = source["locale"]
                if source["module_sha256"] != MODULE_PINS[locale][2]:
                    raise ValueError("source-module pin drift")
                if (source["fragment_path"], source["fragment_sha256"]) not in witnesses:
                    raise ValueError("fragment missing from witnesses")
                raw = local_path(source["fragment_path"]).read_bytes()
                if hashlib.sha256(raw).hexdigest() != source["fragment_sha256"]:
                    raise ValueError("source fragment drift")
                key = (selection["target_id"], locale)
                if key in fragments:
                    raise ValueError("duplicate source fragment")
                fragments[key] = ET.fromstring(raw)
        if set(fragments) != {(sid, locale) for sid in SELECTED_IDS for locale in MODULE_PINS}:
            raise ValueError("missing source fragment")
        return lock, fragments
    for locale, (archive, member, digest) in MODULE_PINS.items():
        with zipfile.ZipFile(BASE.parent / "downloads/mr-Deva-IN/releases" / archive) as handle:
            raw = handle.read(member)
        if hashlib.sha256(raw).hexdigest() != digest:
            raise ValueError("source-module pin drift")
        root = ET.fromstring(raw)
        section = next(n for n in root.iter() if n.get("id") == CONTEXT_ID)
        selected = [n for n in section if n.get("id")]
        if [n.get("id") for n in selected] != list(SELECTED_IDS):
            raise ValueError("complete teaching-section scope changed")
        fragments.update({(n.get("id"), locale): n for n in selected})
    return None, fragments


def atom(value):
    value = value.strip().replace("−", "-")
    if re.fullmatch(r"[+-]?[0-9]+", value):
        return F(value)
    phone = re.fullmatch(r"([0-9]{3}-[0-9]{3}-[0-9]{4})(?: (?:home|cell|work|rumah|seluler|kantor|घरचा|भ्रमणध्वनी|कामाचा))?", value)
    if phone:
        return phone[1]
    if re.fullmatch(r"[A-Za-z]+(?: [A-Za-z]+)*", value):
        return value
    raise ValueError(f"unsupported finite value: {value!r}")


def pairs(display):
    display = display.strip()
    if display.startswith("{") and display.endswith("}"):
        display = display[1:-1]
    matches = list(re.finditer(r"\(([^(),]+),([^(),]+)\)", display))
    if not matches or re.sub(r"\([^()]*\)", "", display).strip(" ,\n\r\t"):
        raise ValueError("expected a complete finite ordered-pair list")
    return tuple((atom(m[1]), atom(m[2])) for m in matches)


def members(display):
    match = re.fullmatch(r"\{([^{}]*)\}", display.strip())
    if not match:
        raise ValueError("expected a finite braced set")
    return [atom(value) for value in match[1].split(",")]


def fibers(relation):
    result = defaultdict(set)
    for x, y in relation:
        result[x].add(y)
    return dict(result)


def is_function(relation):
    return all(len(outputs) == 1 for outputs in fibers(relation).values())


def residual(equation):
    sides = equation.split("=")
    if len(sides) != 2:
        raise ValueError("expected one equation")
    return evaluate("(" + sides[0] + ")-(" + sides[1] + ")")


def unique_polynomial_y(equation):
    """Prove unique real y from c*y+p(x)=0, constant c!=0; no samples."""
    polynomial = residual(equation)
    coefficient = polynomial.get(("y",), F(0))
    if not coefficient or any(monomial != ("y",) and any(v != "x" for v in monomial) for monomial in polynomial):
        raise ValueError("not the supported constant-nonzero linear-in-y form")
    return {monomial: -value / coefficient for monomial, value in polynomial.items() if monomial != ("y",)}


def at(polynomial, x, y):
    coordinates = {"x": F(x), "y": F(y)}
    value = F(0)
    for monomial, coefficient in polynomial.items():
        term = coefficient
        for variable in monomial:
            term *= coordinates[variable]
        value += term
    return value


class ExactReasoningTests(unittest.TestCase):
    def test_finite_shared_outputs_allowed_but_multiple_outputs_rejected(self):
        self.assertTrue(is_function(((1, 0), (2, 0))))
        self.assertTrue(is_function(((1, 0), (1, 0))))
        self.assertFalse(is_function(((1, 0), (1, 2))))
        self.assertEqual(tuple(map(is_function, FINITE)), FINITE_JUDGMENTS)
        self.assertEqual(tuple(map(is_function, MAPPINGS)), (False, False, False))

    def test_six_universal_function_results_use_coefficients_not_sampling(self):
        for index, rule in RULES.items():
            self.assertEqual(unique_polynomial_y(EQUATIONS[index]), evaluate(rule))
        for index in COUNTEREXAMPLES:
            with self.assertRaises(ValueError):
                unique_polynomial_y(EQUATIONS[index])

    def test_three_nonfunctions_have_exact_same_input_distinct_output_witnesses(self):
        for index, witnesses in COUNTEREXAMPLES.items():
            self.assertEqual(witnesses[0][0], witnesses[1][0])
            self.assertNotEqual(witnesses[0][1], witnesses[1][1])
            for x, y in witnesses:
                self.assertEqual(at(residual(EQUATIONS[index]), x, y), 0)
        # The source's "for any x" two-output claim is false at the boundary.
        self.assertEqual(at(residual("x+y²=3"), 3, 0), 0)
        self.assertEqual(residual("3+y²=3"), {("y", "y"): F(1)})
        self.assertEqual(residual("4+y²=3"), {(): F(1), ("y", "y"): F(1)})
        # y²=0 has only y=0; y²+1=0 has no real y, since real squares >=0.

    def test_fail_closed_parsing_and_literal_phone_numbers(self):
        self.assertEqual(atom("753-469-9731"), "753-469-9731")
        self.assertNotEqual(atom("753-469-9731"), atom("743-469-9731"))
        for value in ("__import__('os')", "1+2", "123-567", "name()"):
            with self.assertRaises(ValueError):
                atom(value)
        for equation in ("y=x+y²", "xy=1", "y²=x", "x=0", "y=__import__('os')"):
            with self.assertRaises(ValueError):
                unique_polynomial_y(equation)


class PinnedSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lock, cls.sources = load_sources()

    def test_complete_section_scope_103_ids_nine_supplied_solutions(self):
        all_ids = []
        for locale in MODULE_PINS:
            blocks = [self.sources[(sid, locale)] for sid in SELECTED_IDS]
            identifiers = [n.get("id") for block in blocks for n in block.iter() if n.get("id")]
            self.assertEqual(len(identifiers), 103)
            self.assertEqual(len(set(identifiers)), 103)
            all_ids.append(identifiers)
            self.assertEqual(sum(n.tag == C + "example" for n in blocks), 3)
            self.assertEqual(sum(n.get("class") == "try" for n in blocks), 6)
            self.assertEqual(sum(n.tag == C + "para" for n in blocks), 4)
            exercises = [n for block in blocks for n in block.iter(C + "exercise")]
            self.assertEqual(len(exercises), 9)
            self.assertTrue(all(n.find(C + "solution") is not None for n in exercises))
            media = [n for block in blocks for n in block.iter(C + "media")]
            self.assertEqual(len(media), 13)
            self.assertEqual({n.find(C + "image").get("src").split("/")[-1] for n in media},
                             {filename(short) for short in IMAGE_HASHES})
        self.assertEqual(*all_ids)

    def test_actual_source_six_numeric_relations_and_corrected_range(self):
        for locale in MODULE_PINS:
            actual = []
            for block_index, sid in enumerate(SELECTED_IDS[4:7]):
                problem = next(self.sources[(sid, locale)].iter(C + "problem"))
                actual += [pairs(text(n)) for n in problem.iter(M + "math")]
                solution = next(self.sources[(sid, locale)].iter(C + "solution"))
                projections = [members(value) for value in re.findall(r"\{[^{}]*\}", text(solution)) if "(" not in value]
                self.assertEqual(len(projections), 4)
                for part, values in enumerate(projections):
                    relation = FINITE[block_index * 2 + part // 2]
                    if locale == "en" and block_index == 2 and part == 1:
                        continue  # Explicit original defect checked below.
                    self.assertEqual(len(values), len(set(values)))
                    self.assertEqual(set(values), {F(pair[part % 2]) for pair in relation})
            self.assertEqual(tuple(actual), FINITE)
            # EN's wrong range is a source defect, not a test oracle to copy.
            answer = next(self.sources[(SELECTED_IDS[6], locale)].iter(C + "solution"))
            sets = re.findall(r"\{[^{}]*\}", text(answer))
            self.assertEqual(len(sets), 4)
            first_range = members(sets[1])
            if locale == "en":
                self.assertEqual(first_range, list(map(F, (-3, -2, -1, 0, 2, 2, 3))))
                self.assertNotIn(F(1), first_range)
            else:
                self.assertEqual(set(first_range), {F(y) for x, y in FINITE[4]})

    def test_actual_source_nine_equations_and_supplied_try_judgments(self):
        for locale in MODULE_PINS:
            actual = []
            for index in (11, 12, 13):
                problem = next(self.sources[(SELECTED_IDS[index], locale)].iter(C + "problem"))
                actual += [mathml_display(n) for n in problem.iter(M + "math") if "=" in text(n)]
            self.assertEqual(len(actual), 9)
            self.assertEqual([residual(n) for n in actual], [residual(n) for n in EQUATIONS])
            for index, truth in ((12, (True, False, True)), (13, (False, True, True))):
                answer = text(next(self.sources[(SELECTED_IDS[index], locale)].iter(C + "solution")))
                words = re.findall(r"\b(?:yes|no|ya|tidak)\b", answer.lower())
                self.assertEqual(tuple(word in ("yes", "ya") for word in words), truth)

    def test_source_phone_errors_and_universal_overstatement_remain_witnessed(self):
        for locale in MODULE_PINS:
            source = self.sources[(SELECTED_IDS[9], locale)]
            alt = next(source.iter(C + "media")).get("alt")
            answer = text(next(source.iter(C + "solution")))
            self.assertIn("123-567-4389" if locale == "en" else "123-567-4839", alt)
            self.assertIn("743-469-9731" if locale == "en" else "753-469-9731", answer)
            example = self.sources[(SELECTED_IDS[11], locale)]
            paragraph = next(n for n in example.iter() if n.get("id") == "fs-id1167836539656")
            self.assertIn("any value of x" if locale == "en" else "setiap nilai x", text(paragraph))


class Unit9MathematicsTests(unittest.TestCase):
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
                if node.get("data-check") in cls.checks:
                    raise ValueError("duplicate math check")
                cls.checks[node.get("data-check")] = text(node)

    def test_actual_locale_config_counts_and_math_map(self):
        self.assertEqual(self.root.get("id"), UNIT)
        self.assertEqual(self.root.get("lang"), "mr-Deva-IN")
        decoded = self.raw.decode("utf-8")
        self.assertEqual(unicodedata.normalize("NFC", decoded), decoded)
        self.assertNotIn("\ufffd", decoded)
        self.assertEqual(self.checks, self.config["expected_math"])
        self.assertEqual(len(self.checks), 68)
        for key, expected in (("source_count", 14), ("translated_worked_examples", 3),
                              ("translated_definitions", 1), ("translated_practice_items", 6),
                              ("original_practice_items", 0)):
            self.assertEqual(self.config[key], expected)
        self.assertEqual(self.config["question_ids"], [])
        for term in self.config["required_terms"]:
            self.assertIn(term, text(self.root))

    def test_all_103_selected_ids_and_context_remain_in_order_and_nested(self):
        self.assertEqual([n.get("data-source") for n in self.root.iter() if n.get("data-source")],
                         ["A20:m81373#" + sid for sid in SELECTED_IDS])
        actual = [n.get("id") for n in self.root.iter() if re.match(r"(?:fs-id|term-)", n.get("id", ""))]
        for locale in MODULE_PINS:
            expected = [n.get("id") for sid in SELECTED_IDS for n in self.sources[(sid, locale)].iter() if n.get("id")]
            self.assertEqual(actual, [CONTEXT_ID] + expected)
            self.assertEqual(len(actual), 104)
            for sid in SELECTED_IDS:
                source_ids = {n.get("id") for n in self.sources[(sid, locale)].iter() if n.get("id")}
                target_ids = {n.get("id") for n in self.ids[sid].iter() if n.get("id")}
                self.assertTrue(source_ids <= target_ids)
        self.assertEqual(text(self.ids["term-00004"]), "फलन")
        self.assertIn("प्रत्येक", text(self.ids["fs-id1167829714644"]))
        self.assertIn("नेमका एक", text(self.ids["fs-id1167829714644"]))

    def test_six_finite_relations_twelve_projections_and_every_judgment(self):
        prefixes = ("pairs-example-a", "pairs-example-b", "pairs-try1-a", "pairs-try1-b", "pairs-try2-a", "pairs-try2-b")
        for prefix, expected in zip(prefixes, FINITE):
            actual = pairs(self.checks[prefix])
            self.assertEqual(actual, expected)
            self.assertEqual(len(actual), 7)
            for suffix, index in (("domain", 0), ("range", 1)):
                values = members(self.checks[prefix + "-" + suffix])
                self.assertEqual(len(values), len(set(values)))
                self.assertEqual(set(values), {pair[index] for pair in actual})
        for prefix in prefixes[:2]:
            self.assertEqual(pairs(self.checks[prefix + "-repeat"]), pairs(self.checks[prefix]))
        self.assertIn("फलन आहे", text(self.ids["fs-id1167836691895"]))
        self.assertIn("फलन नाही", text(self.ids["fs-id1167833223866"]))
        for sid, expected in (("fs-id1167826188989", (True, False)), ("fs-id1167836798080", (False, True))):
            actual = re.findall(r"\([ab]\)\s+(होय|नाही)", text(self.ids[sid]))
            self.assertEqual(tuple(value == "होय" for value in actual), expected)
        for prefix, expected_index in (("pairs-try1-b", 3), ("pairs-try2-a", 4)):
            witness = pairs(self.checks[prefix + "-counterexample"])
            self.assertEqual(len(witness), 2)
            self.assertEqual(witness[0][0], witness[1][0])
            self.assertNotEqual(witness[0][1], witness[1][1])
            self.assertTrue(set(witness) <= set(FINITE[expected_index]))

    def test_three_mapping_alts_six_projections_and_source_answers(self):
        prefixes = ("mapping-example", "mapping-try3", "mapping-try4")
        for index, (prefix, expected) in enumerate(zip(prefixes, MAPPINGS)):
            image = next(n for n in self.root.iter("img") if n.get("src") == "asset:" + filename(f"{index + 7:03d}_img_new"))
            rows = image.get("alt").split(":", 1)[1].split(".", 1)[0].split(";")
            actual = []
            for row in rows:
                source, outputs = row.strip().split(" ते ", 1)
                for output in re.split(",| आणि ", outputs):
                    actual.append((atom(source), atom(output)))
            self.assertEqual(tuple(actual), expected)
            self.assertFalse(is_function(actual))
            for suffix, coordinate in (("domain", 0), ("range", 1)):
                values = members(self.checks[prefix + "-" + suffix])
                self.assertEqual(len(values), len(set(values)))
                self.assertEqual(set(values), {pair[coordinate] for pair in expected})
            sid = SELECTED_IDS[7 + index]
            for locale in MODULE_PINS:
                solution = next(self.sources[(sid, locale)].iter(C + "solution"))
                content = text(solution)
                if locale == "en" and index == 1:
                    content = content.replace("Love it or List it", "Love It or List It")
                if locale == "en" and index == 2:
                    content = content.replace("743-469-9731", "753-469-9731")
                projections = re.findall(r"\{[^{}]*\}", content)
                self.assertEqual(len(projections), 2)
                for coordinate, projection in enumerate(projections):
                    self.assertEqual(set(members(projection)), {pair[coordinate] for pair in expected})
            target_solution = self.ids[next(self.sources[(sid, "en")].iter(C + "solution")).get("id")]
            self.assertIn("फलन नाही", text(target_solution))

    def test_source_corrections_are_visible_and_do_not_change_questions(self):
        notes = lambda sid: " ".join(text(n) for n in self.ids[sid].iter("p") if n.get("data-kind") == "original")
        self.assertIn("संबंधाचा मूल्यसंच", text(self.ids["fs-id1167833060073"]))
        self.assertIn("फलनाचा मूल्यसंच", notes(SELECTED_IDS[5]))
        for required in ("स्रोत-दुरुस्ती", "1 ऐवजी 2", "इंडोनेशियन"):
            self.assertIn(required, notes(SELECTED_IDS[6]))
        for required in ("Love it or List it", "Love It or List It"):
            self.assertIn(required, notes(SELECTED_IDS[8]))
        for required in ("123-567-4389", "123-567-4839", "743-469-9731", "753-469-9731"):
            self.assertIn(required, notes(SELECTED_IDS[9]))
        self.assertNotIn("743-469-9731", self.checks["mapping-try4-range"])
        self.assertNotIn("123-567-4389", self.checks["mapping-try4-range"])

    def test_all_nine_equations_and_six_universal_positive_results(self):
        prefixes = tuple(f"equation-{group}-{part}" for group in ("example", "try5", "try6") for part in "abc")
        for index, prefix in enumerate(prefixes):
            self.assertEqual(residual(self.checks[prefix]), residual(EQUATIONS[index]))
            if index in RULES:
                self.assertEqual(unique_polynomial_y(self.checks[prefix]), evaluate(RULES[index]))
            else:
                for x, y in COUNTEREXAMPLES[index]:
                    self.assertEqual(at(residual(self.checks[prefix]), x, y), 0)
        for prefix in ("equation-example-a", "equation-example-b"):
            self.assertEqual(residual(self.checks[prefix + "-repeat"]), residual(self.checks[prefix]))
        for prefix in ("equation-try5-a", "equation-try5-c"):
            self.assertEqual(unique_polynomial_y(self.checks[prefix + "-working"]), unique_polynomial_y(self.checks[prefix]))
        for sid, expected in (("fs-id1167833255910", (True, False, True)), ("fs-id1167829859295", (False, True, True))):
            words = re.findall(r"\([abc]\)\s+(होय|नाही)", text(self.ids[sid]))
            self.assertEqual(tuple(word == "होय" for word in words), expected)
        for sid in ("fs-id1167833056514", "fs-id1167829936815"):
            self.assertIn("फलन ठरवते", text(self.ids[sid]))
        self.assertIn("फलन ठरवत नाही", text(self.ids["fs-id1167836539656"]))

    def test_ten_equation_raster_transcriptions_and_working_values(self):
        media = [n for n in self.sources[(SELECTED_IDS[11], "en")].iter(C + "media")]
        for source_media in media:
            short = source_media.find(C + "image").get("src").split("_")[-2]
            target = self.ids[source_media.get("id")]
            self.assertEqual(target.get("data-check"), "raster-" + short)
            self.assertEqual(residual(text(target)), residual(PIXEL_FORMULAS[short]))
        self.assertEqual(len(media), 10)
        for table_id in ("fs-id1167836429672", "fs-id1167836533787", "fs-id1167829596595"):
            self.assertEqual(self.ids[table_id].get("data-kind"), "adaptation")
        for key, expected in (("linear-example-input", "x=3"), ("square-example-input", "x=2"),
                              ("two-output-example-input", "x=2")):
            self.assertEqual(residual(self.checks[key]), residual(expected))
        self.assertEqual(residual(self.checks["raster-010b"]), residual(self.checks["raster-010c"]))
        self.assertEqual(residual(self.checks["raster-011b"]), residual(self.checks["raster-011c"]))
        self.assertEqual(residual(self.checks["raster-012a"]), residual(self.checks["raster-012b"]))
        self.assertEqual(residual(self.checks["raster-012c"]), residual(self.checks["raster-012d"]))
        for key, expected in (("linear-example-result", "x=3⇒y=1"), ("square-example-result", "x=2⇒y=5")):
            self.assertEqual(re.sub(r"\s", "", self.checks[key]), expected)
        for prefix, index in (("two-output-example", 2), ("equation-try5-b", 4), ("equation-try6-a", 6)):
            input_text = self.checks[prefix + "-input"]
            self.assertRegex(input_text, r"^x\s*=\s*[0-9]+$")
            x = F(input_text.split("=")[1].strip())
            y_values = [F(n.replace("−", "-")) for n in re.findall(r"y\s*=\s*([−-]?[0-9]+)", self.checks[prefix + "-values"])]
            self.assertEqual(len(y_values), 2)
            self.assertNotEqual(*y_values)
            for y in y_values:
                self.assertEqual(at(residual(EQUATIONS[index]), x, y), 0)
                if prefix != "two-output-example":
                    self.assertEqual(at(residual(self.checks[prefix + "-square"]), x, y), 0)

    def test_real_domain_boundary_and_overgeneralization_correction(self):
        self.assertEqual(re.sub(r"\s", "", self.checks["two-output-relation-domain"]), "x≤3")
        self.assertEqual(re.sub(r"\s", "", self.checks["two-output-boundary"]), "x=3⇒y=0")
        self.assertEqual(re.sub(r"\s", "", self.checks["two-output-outside"]), "x>3")
        notes = " ".join(text(n) for n in self.ids[SELECTED_IDS[11]].iter("p") if n.get("data-kind") == "original")
        for required in ("स्रोत-दुरुस्ती", "प्रत्येक x-मूल्यासाठी", "वास्तविक y-मूल्य मिळत नाही", "विशिष्ट x", "लाल"):
            self.assertIn(required, notes)
        # Algebraic reduction is y²=3-x: a real square is nonnegative, and any
        # nonnegative real has a square root. Boundary and outside claims are
        # thus sign/domain arguments, not a finite sampling proof.
        self.assertEqual(residual("x+y²=3"), {("x",): F(1), ("y", "y"): F(1), (): F(-3)})

    def test_all_nine_original_solutions_and_two_way_navigation(self):
        count = 0
        for sid in SELECTED_IDS:
            for exercise in self.sources[(sid, "en")].iter(C + "exercise"):
                count += 1
                problem, solution = exercise.find(C + "problem"), exercise.find(C + "solution")
                target_exercise = self.ids[exercise.get("id")]
                for source, kind in ((problem, "problem"), (solution, "solution")):
                    target = next(n for n in target_exercise if n.get("id") == source.get("id"))
                    self.assertIn(kind, target.get("class", "").split())
                answer = self.ids[solution.get("id")]
                self.assertNotEqual(answer.get("data-kind"), "original")
                self.assertTrue(text(answer.find("h4")).startswith("स्रोतातील"))
                for start, end in ((problem.get("id"), solution.get("id")), (solution.get("id"), problem.get("id"))):
                    self.assertIn("#" + end, [a.get("href") for a in self.ids[start].iter("a") if text(a)])
        self.assertEqual(count, 9)
        self.assertEqual(sum("solution" in n.get("class", "").split() for n in self.root.iter()), 9)
        self.assertFalse(any(sid.startswith("mr-answer-") for sid in self.ids))

    def test_three_prior_unit_references_keep_exact_original_targets(self):
        expected = ("fs-id1167829683746", "fs-id1167829683746", "fs-id1167833057329")
        for locale in MODULE_PINS:
            source_links = [n for sid in SELECTED_IDS for n in self.sources[(sid, locale)].iter(C + "link")]
            self.assertEqual(tuple(n.get("target-id") for n in source_links), expected)
        target_links = [n for n in self.root.iter("a") if n.get("data-source-target-id")]
        self.assertEqual(tuple(n.get("data-source-target-id") for n in target_links), expected)
        prior = ET.parse(BASE / "translations/MR-BRIDGE-008.xml").getroot()
        prior_ids = {n.get("id") for n in prior.iter()}
        for node, sid in zip(target_links, expected):
            self.assertIn(sid, prior_ids)
            self.assertNotIn(sid, self.ids)
            self.assertEqual(node.get("data-source-document"), "m81373")
            self.assertEqual(node.get("data-source-target"), "A20:m81373#" + sid)
            self.assertEqual(node.get("href"), "https://openstax.org/books/intermediate-algebra-2e/pages/3-5-relations-and-functions#" + sid)
            self.assertTrue(text(node))
        self.assertEqual(pairs(self.checks["graph-reference-pair1"]), ((-3, -1),))
        self.assertEqual(pairs(self.checks["graph-reference-pair2"]), ((-3, 4),))

    def test_frozen_images_bind_three_assets_and_ten_transcriptions_to_pixels(self):
        self.assertIsNotNone(self.lock, "final source/image freeze is required")
        self.assertEqual(len(self.sources), 28)
        records = self.lock["source_images"]
        self.assertEqual(len(records), 26)
        indexed = {(record["locale"], record["member"].split("/")[-1]): record for record in records}
        self.assertEqual(len(indexed), 26)
        total_bytes = {"en": 0, "id": 0}
        for locale, image_pins in (("en", IMAGE_HASHES), ("id", ID_IMAGE_HASHES)):
            archive, module_member, unused_digest = MODULE_PINS[locale]
            archive_path = BASE.parent / "downloads/mr-Deva-IN/releases" / archive
            # Only 13 small selected images are read, never extracted. This
            # verifies nonembedded equation rasters too; source archives are
            # required for this stronger independent review, not for building.
            with zipfile.ZipFile(archive_path) as handle:
                for short, digest in image_pins.items():
                    name = filename(short)
                    record = indexed[(locale, name)]
                    member = module_member.split("/modules/")[0] + "/media/" + name
                    self.assertEqual(record["member"], member)
                    self.assertEqual(record["archive"], "downloads/mr-Deva-IN/releases/" + archive)
                    self.assertEqual(record["sha256"], digest)
                    source_block = next(sid for sid in SELECTED_IDS for n in self.sources[(sid, locale)].iter(C + "image")
                                        if n.get("src").endswith("/" + name))
                    self.assertEqual(record["locator"], "A20:m81373#" + source_block)
                    raw = handle.read(member)
                    self.assertEqual(hashlib.sha256(raw).hexdigest(), digest)
                    self.assertEqual(record["bytes"], len(raw))
                    total_bytes[locale] += len(raw)
                    self.assertTrue(raw.startswith(b"\xff\xd8\xff"))
        self.assertEqual(total_bytes, {"en": 409059, "id": 1703462})
        assets = self.config.get("assets", {})
        expected_assets = {filename(f"{n:03d}_img_new") for n in (7, 8, 9)}
        self.assertEqual(set(assets), expected_assets)
        images = list(self.root.iter("img"))
        self.assertEqual(len(images), 3)
        self.assertEqual({n.get("src") for n in images}, {"asset:" + name for name in expected_assets})
        witnesses = {(w["path"], w["sha256"]) for w in self.lock["witnesses"]}
        for name, asset in assets.items():
            record = indexed[("en", name)]
            self.assertEqual(asset["mime"], "image/jpeg")
            self.assertEqual(asset["sha256"], record["sha256"])
            self.assertEqual(asset["path"], record["committed_asset"])
            self.assertIn((asset["path"], asset["sha256"]), witnesses)
            self.assertEqual(hashlib.sha256(local_path(asset["path"]).read_bytes()).hexdigest(), asset["sha256"])
            source_media = next(n for sid in SELECTED_IDS for n in self.sources[(sid, "en")].iter(C + "media")
                                if n.find(C + "image").get("src").endswith("/" + name))
            self.assertEqual(self.ids[source_media.get("id")].find("img").get("src"), "asset:" + name)
        self.assertEqual(sum(local_path(a["path"]).stat().st_size for a in assets.values()), 265628)


if __name__ == "__main__":
    unittest.main(verbosity=2)
