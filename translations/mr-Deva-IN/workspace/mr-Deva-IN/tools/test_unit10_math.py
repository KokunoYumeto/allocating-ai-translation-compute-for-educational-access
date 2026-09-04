"""Independent MR010 source, exact-polynomial and media regressions.

Run with python -B. Stdlib only; reads selected pinned ZIP members in memory.
Does not download, extract, build, render, or write. Pixel hashes bind images
personally reviewed separately; these tests are not OCR or native-language QA.
"""
import ast
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import unittest
import xml.etree.ElementTree as ET
import zipfile


BASE = Path(__file__).resolve().parents[1]
UNIT = "MR-BRIDGE-010"
C = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SECTION = "fs-id1167824731607"
SELECTED = (
    "fs-id1167836315013", "fs-id1167824735502", "fs-id1167833186483",
    "fs-id1167829620795", "fs-id1167836362234", "fs-id1167833051398",
    "fs-id1167833202337", "fs-id1167829718470", "fs-id1167836560949",
    "fs-id1167836326537", "fs-id1167836456485", "fs-id1167836629682",
    "fs-id1167836388368", "fs-id1167824578714", "fs-id1167836518536",
    "fs-id1167836730594", "fs-id1167825766170", "fs-id1167836283159",
)
EXCLUDED = {
    "fs-id1167836521479": "MR-BRIDGE-001",
    "fs-id1167829859398": "MR-BRIDGE-001",
    "fs-id1167833158753": "MR-BRIDGE-002",
    "fs-id1167833369424": "MR-BRIDGE-002",
    "fs-id1167836481611": "MR-BRIDGE-002",
    "fs-id1167833128952": "MR-BRIDGE-002",
}
# source wrapper, formula paragraph, arguments paragraph, answer paragraph
EXERCISES = (
    (SELECTED[12], "fs-id1167836363586", "fs-id1167836625930", "fs-id1167825884792"),
    (SELECTED[13], "fs-id1167833269888", "fs-id1167829579645", "fs-id1167836732807"),
    (SELECTED[15], "fs-id1167829788687", "fs-id1167829906594", "fs-id1167836554185"),
    (SELECTED[16], "fs-id1167836293432", "fs-id1167823012018", "fs-id1167829717717"),
)
PINS = {
    "en": ("downloads/mr-Deva-IN/releases/A20-canonical.zip",
           "osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/",
           "effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917",
           "2b606026c2b34cdf69acfa29bfe4b90abdb6961a322a78c7ec20107e0948b05c"),
    "id": ("downloads/mr-Deva-IN/releases/A20-v0.3.0-source.zip", "source/",
           "a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7",
           "e9e593b31587995170c520b9175f2e0c0cb335282c951bb1d769f775344311ee"),
}
# These are the actual independently inspected rasters, not inferred alt values.
IMAGE_PINS = (
    ("013a", "fs-id1167836353205", 15640,
     "15dc68980fadea9e7ba3f45424660e0a0d250d887eec3d4ff2868c9b5caf0e9d",
     "4784dcfb3c1383925f742da34ffb5b23a43ec5ecc7fa38d37890fa5d3f3b0347", "y = 4x − 5"),
    ("013b", "fs-id1167836433912", 17286,
     "e848a25b5ab599bcaed5af5663b1e29e6794b038548d12cf86eb1db04100f8a5",
     "a1738ecbe38f2ad27ba4cf9bcb7136e828521d4a31bfa3105d9172f4d8bae29a", "y = 4 · 2 − 5"),
    ("013c", "fs-id1167832926879", 14440,
     "6325f8076b62e3d302e189448ec013b0f491c9fe3b34459fb2b4c4c331f45d19",
     "1b0341a662f9305e7e8837990fb8902bd9edf4a60153b8f106a3fb56f16de884", "y = 3"),
    ("014a", "fs-id1167836447887", 16628,
     "ea1677c72a05ebd74da8fa57fd50aab6eecc596582592b3fee11eceeb3aa8524",
     "68dd8fb5ff531bc0ddb6882b190b087f706075973c2922806f777d8e6a341f2d", "f(x) = 4x − 5"),
    ("014b", "fs-id1167836314769", 18508,
     "9e2bfcd6881e9e350bb261ba99fbca33dcee66798f79ef44aa1eddcd2ef8f9d9",
     "58a8fe28a0943805fa070f44764c3e1aa74ffb9c39a28cc4c0de306d77e343b2", "f(2) = 4 · 2 − 5"),
    ("014c", "fs-id1167836399865", 15652,
     "651b0da087ab2e5061a8880ca3712a524f5480882ebafc8ceb0906a8ee107b82",
     "c6dd366d48e3f5ba67147b4c9a2a76f18eddb86e9ea76863436ce9690829d81e", "f(2) = 3"),
)


def text(node):
    return "".join(node.itertext()).strip()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_bytes(), object_pairs_hook=json_object)


def local(relative):
    path = (BASE / relative).resolve()
    if not path.is_relative_to(BASE):
        raise ValueError("witness escapes language directory")
    return path


def image_name(part):
    return "CNX_IntAlg_Figure_03_05_" + part + "_img.jpg"


def source_math(node):
    """Serialize this slice's arithmetic MathML without flattening powers."""
    if node.tag == M + "msup":
        return "(" + source_math(node[0]) + ")**(" + source_math(node[1]) + ")"
    if node.tag == M + "mspace":
        return " "
    if node.tag.split("}")[-1] not in {"math", "mrow", "mi", "mn", "mo"}:
        raise ValueError("unsupported source MathML")
    return (node.text or "") + "".join(source_math(n) + (n.tail or "") for n in node)


def maths(node):
    return [source_math(n).strip().rstrip(".,") for n in node.iter(M + "math")]


def normalized(expression):
    expression = expression.replace("−", "-").replace("²", "**2").replace("·", "*")
    expression = re.sub(r"\s+", "", expression)
    # Only implied multiplication following a numeric literal or grouped value.
    return re.sub(r"(?<=[0-9)])(?=[a-z(])", "*", expression)


def syntax(expression):
    return ast.dump(ast.parse(normalized(expression), mode="eval"), include_attributes=False)


def cleaned(poly):
    return {monomial: Fraction(coefficient) for monomial, coefficient in poly.items() if coefficient}


def add(a, b):
    result = dict(a)
    for monomial, coefficient in b.items():
        result[monomial] = result.get(monomial, 0) + coefficient
    return cleaned(result)


def multiply(a, b):
    result = {}
    for left, lvalue in a.items():
        for right, rvalue in b.items():
            monomial = tuple(sorted(left + right))
            result[monomial] = result.get(monomial, 0) + lvalue * rvalue
    return cleaned(result)


def polynomial(expression, functions=None, bindings=None):
    """Exact coefficient algebra, not a finite-grid or equality-string check."""
    functions, bindings = functions or {}, bindings or {}

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return cleaned({(): node.value})
        if isinstance(node, ast.Name) and re.fullmatch(r"[a-z]", node.id):
            return bindings.get(node.id, {(node.id,): Fraction(1)})
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = visit(node.operand)
            return value if isinstance(node.op, ast.UAdd) else {m: -c for m, c in value.items()}
        if isinstance(node, ast.BinOp):
            a, b = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                return add(a, b)
            if isinstance(node.op, ast.Sub):
                return add(a, {m: -c for m, c in b.items()})
            if isinstance(node.op, ast.Mult):
                return multiply(a, b)
            if isinstance(node.op, ast.Pow) and set(b) <= {()}:
                exponent = b.get((), Fraction(0))
                if exponent.denominator != 1 or not 0 <= exponent <= 8:
                    raise ValueError("unsupported exponent")
                result = {(): Fraction(1)}
                for _ in range(int(exponent)):
                    result = multiply(result, a)
                return result
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in functions and len(node.args) == 1 and not node.keywords):
            return polynomial(functions[node.func.id], bindings={"x": visit(node.args[0])})
        raise ValueError("unsupported polynomial syntax")

    return visit(ast.parse(normalized(expression), mode="eval").body)


def structure(node):
    return (node.tag, sorted(node.attrib.items()), node.text,
            [(structure(child), child.tail) for child in node])


class Unit10Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (BASE / f"translations/{UNIT}.xml").read_bytes()
        cls.root = ET.fromstring(cls.raw)
        cls.config = read_json(BASE / f"units/{UNIT}.json")
        cls.ids = {n.get("id"): n for n in cls.root.iter() if n.get("id")}
        cls.checks = {n.get("data-check"): text(n) for n in cls.root.iter() if n.get("data-check")}
        cls.sources, cls.sections, cls.images = {}, {}, {}
        for locale, (archive_path, prefix, _, module_hash) in PINS.items():
            with zipfile.ZipFile(BASE.parent / archive_path) as archive:
                member = prefix + "modules/m81373/index.cnxml"
                if archive.namelist().count(member) != 1:
                    raise ValueError("missing/ambiguous module")
                module = archive.read(member)  # ZIP read verifies member CRC.
                if sha(module) != module_hash:
                    raise ValueError("pinned module bytes changed")
                root = ET.fromstring(module)
                cls.sources[locale] = {n.get("id"): n for n in root.iter() if n.get("id")}
                cls.sections[locale] = cls.sources[locale][SECTION]
                for part, *_ in IMAGE_PINS:
                    member = prefix + "media/" + image_name(part)
                    if archive.namelist().count(member) != 1:
                        raise ValueError("missing/ambiguous image")
                    cls.images[(locale, part)] = archive.read(member)

    def test_identity_nfc_unique_ids_and_required_terms(self):
        self.assertEqual(self.root.get("id"), UNIT)
        self.assertEqual(self.root.get("lang"), "mr-Deva-IN")
        decoded = self.raw.decode("utf-8")
        self.assertEqual(unicodedata.normalize("NFC", decoded), decoded)
        self.assertNotIn("\ufffd", decoded)
        self.assertEqual(len(self.ids), 59)
        self.assertEqual(len(self.ids), sum(bool(n.get("id")) for n in self.root.iter()))
        self.assertEqual(len(self.config["required_terms"]), 10)
        for term in self.config["required_terms"]:
            self.assertIn(term, text(self.root))

    def test_exact_section_remainder_and_eighteen_ordered_selectors(self):
        expected = ["A20:m81373#" + sid for sid in SELECTED]
        self.assertEqual([n.get("data-source") for n in self.root.iter() if n.get("data-source")], expected)
        self.assertIsNone(self.ids[SECTION].get("data-source"))
        for source in self.sections.values():
            blocks = [n for n in source if n.tag != C + "title"]
            self.assertEqual(len(blocks), 24)
            self.assertEqual([n.get("id") for n in blocks if n.get("id") not in EXCLUDED], list(SELECTED))
            self.assertEqual(sum(bool(n.get("id")) for n in source.iter()), 141)

    def test_all_fifty_three_nested_source_ids_plus_uncounted_wrapper(self):
        for locale, source in self.sources.items():
            expected = [SECTION]
            for sid in SELECTED:
                nested = [n.get("id") for n in source[sid].iter() if n.get("id")]
                self.assertEqual([n.get("id") for n in self.ids[sid].iter() if n.get("id")], nested)
                expected.extend(nested)
            self.assertEqual(len(expected), 54)
            self.assertEqual([sid for sid in self.ids if sid.startswith("fs-id")], expected)
            self.assertTrue(all(self.ids[sid].get("data-kind") == "translation" for sid in SELECTED))

    def test_exclusions_exist_in_prior_units_and_no_duplicate_selectors(self):
        others = {}
        # This is the prior001-009 selection baseline for010. Later011 is an
        # explicitly authorized fuller representation of four legacy001 blocks,
        # not a new owner of the already excluded source selections here.
        for number in range(1, 10):
            path = BASE / "translations" / f"MR-BRIDGE-{number:03d}.xml"
            root = ET.parse(path).getroot()
            for node in root.iter():
                if node.get("data-source"):
                    others.setdefault(node.get("data-source"), []).append(path.stem)
        for sid, unit in EXCLUDED.items():
            self.assertEqual(others["A20:m81373#" + sid], [unit])
            for source_node in self.sources["en"][sid].iter():
                if source_node.get("id"):
                    self.assertNotIn(source_node.get("id"), self.ids)
        for sid in SELECTED:
            self.assertNotIn("A20:m81373#" + sid, others)

    def test_classification_not_inflated_by_introductory_tables(self):
        expected = {"source_count": 18, "translated_worked_examples": 0,
                    "translated_definitions": 2, "translated_practice_items": 4,
                    "translated_resource_notes": 0, "original_practice_items": 0}
        for key, value in expected.items():
            self.assertEqual(self.config[key], value)
        self.assertEqual(self.config["question_ids"], [])
        for source in self.sources.values():
            blocks = [source[sid] for sid in SELECTED]
            self.assertEqual(sum(b.tag == C + "example" for b in blocks), 0)
            self.assertEqual(sum(b.tag == C + "table" for b in blocks), 2)
            self.assertEqual(sum(b.tag == C + "para" for b in blocks), 10)
            self.assertEqual(sum(b.tag == C + "note" and b.get("class") == "try" for b in blocks), 4)

    def test_all_forty_six_math_checks_source_bound_and_config_equal(self):
        expected = {
            "notation-intro": "f(x)", "notation-rule": "y=f(x)", "notation-range": "f(x)",
            "notation-reading": "f(x)", "variable-rule": "y=f(x)", "evaluation-process": "f(x)",
            "bridge-f": "f(x)", "bridge-g": "g(x)",
        }
        for key in ("equation-intro", "notation-equation"):
            expected[key] = maths(self.sources["en"]["fs-id1167833051398"])[0]
        expected["notation-formula"] = maths(self.sources["en"]["fs-id1167836560949"])[1]
        for key in ("equation-input", "equation-substitution", "equation-table-input", "equation-result-input",
                    "notation-input", "notation-table-input", "notation-result-input"):
            expected[key] = maths(self.sources["en"]["fs-id1167833051398"])[1]
        for index, (_, formula_id, arguments_id, answer_id) in enumerate(EXERCISES, 1):
            for locale in ("en", "id"):
                source = self.sources[locale]
                formula, = maths(source[formula_id])
                arguments, answers = maths(source[arguments_id]), maths(source[answer_id])
                if index == 2 and locale == "en":
                    self.assertEqual(normalized(answers[0]), "(2)=13")
                    answers[0] = "f" + answers[0]
                items = {f"try{index}-formula": formula}
                for letter, argument, answer in zip("abc", arguments, answers):
                    items[f"try{index}-{letter}"] = argument
                    items[f"try{index}-answer-{letter}"] = answer
                for key, source_value in items.items():
                    target_parts, source_parts = self.checks[key].split("="), source_value.split("=")
                    self.assertEqual([syntax(p) for p in target_parts], [syntax(p) for p in source_parts], (locale, key))
                expected.update(items)
        self.assertEqual(set(self.checks), set(expected))
        self.assertEqual(len(self.checks), 46)
        self.assertEqual(len(self.checks), sum(bool(n.get("data-check")) for n in self.root.iter()))
        for key, value in expected.items():
            self.assertEqual([syntax(p) for p in self.checks[key].split("=")], [syntax(p) for p in value.split("=")], key)
        self.assertEqual(self.config["expected_math"], self.checks)

    def test_four_tryits_have_exact_source_problem_solution_and_three_subparts(self):
        solutions = [n for n in self.root.iter() if "solution" in n.get("class", "").split()]
        self.assertEqual(len(solutions), 4)
        for sid, formula_id, args_id, answer_id in EXERCISES:
            for source in self.sources.values():
                exercise = source[sid].find(C + "exercise")
                self.assertIsNotNone(exercise)
                problem, solution = exercise.find(C + "problem"), exercise.find(C + "solution")
                self.assertIn("problem", self.ids[problem.get("id")].get("class", "").split())
                self.assertIn("solution", self.ids[solution.get("id")].get("class", "").split())
                self.assertIsNone(self.ids[solution.get("id")].get("data-kind"))
                self.assertIn("स्रोतातील उत्तर", text(self.ids[solution.get("id")].find("h4")))
                self.assertEqual(len(maths(source[formula_id])), 1)
                self.assertEqual(len(maths(source[args_id])), 3)
                self.assertEqual(len(maths(source[answer_id])), 3)
                self.assertEqual([text(s) for s in source[args_id].findall(C + "span")], ["ⓐ", "ⓑ", "ⓒ"])

    def test_all_twelve_answers_by_exact_polynomial_substitution(self):
        for index, (_, formula_id, args_id, _) in enumerate(EXERCISES, 1):
            for locale in ("en", "id"):
                formula, = maths(self.sources[locale][formula_id])
                lhs, rhs = formula.split("=")
                function = re.fullmatch(r"([fgh])\(x\)", normalized(lhs)).group(1)
                functions = {function: rhs}
                for letter, source_argument in zip("abc", maths(self.sources[locale][args_id])):
                    with self.subTest(locale=locale, item=index, part=letter):
                        expected = polynomial(source_argument, functions=functions)
                        answer = self.checks[f"try{index}-answer-{letter}"]
                        parts = answer.split("=")
                        if len(parts) == 2:
                            self.assertEqual(syntax(parts[0]), syntax(source_argument))
                        self.assertEqual(polynomial(parts[-1]), expected)

    def test_whole_arguments_are_not_output_addition_or_subtraction(self):
        g, h = {"g": "4x-7"}, {"h": "2x+1"}
        gb = polynomial(self.checks["try3-b"], functions=g)
        gc = polynomial(self.checks["try3-c"], functions=g)
        hb = polynomial(self.checks["try4-b"], functions=h)
        hc = polynomial(self.checks["try4-c"], functions=h)
        self.assertNotEqual(gb, gc)
        self.assertNotEqual(hb, hc)
        self.assertEqual(add(gb, {m: -v for m, v in gc.items()}), {(): Fraction(-7)})
        self.assertEqual(add(hb, {m: -v for m, v in hc.items()}), {(): Fraction(-1)})
        self.assertEqual(polynomial("g(m**2)", functions=g), polynomial("4m**2-7"))
        self.assertNotEqual(polynomial("g(m**2)", functions=g), polynomial("g(m)**2", functions=g))

    def test_source_tables_keep_all_three_rows_six_figures_and_input_two(self):
        for offset, sid in ((0, SELECTED[6]), (3, SELECTED[9])):
            target = self.ids[sid].find("table")
            self.assertIsNotNone(target)
            rows = target.findall("./tbody/tr")
            self.assertEqual(len(rows), 3)
            for row, pin in zip(rows, IMAGE_PINS[offset:offset + 3]):
                self.assertEqual([n.tag for n in row], ["td", "td"])
                figures = list(row.iter("figure"))
                self.assertEqual([f.get("id") for f in figures], [pin[1]])
            self.assertEqual(text(rows[0][0]), "")
            self.assertIn("x = 2", text(rows[1][0]))
            self.assertEqual(text(rows[2][0]), "")
            for source in self.sources.values():
                original = source[sid]
                self.assertEqual(original.tag, C + "table")
                self.assertEqual(len(list(original.iter(C + "row"))), 3)
                self.assertEqual([n.get("id") for n in original.iter(C + "media")], [p[1] for p in IMAGE_PINS[offset:offset + 3]])

    def test_both_table_calculations_recompute_every_raster_step(self):
        source_rule = maths(self.sources["en"]["fs-id1167833051398"])[0].split("=")[1]
        expected = polynomial(source_rule, bindings={"x": {(): Fraction(2)}})
        self.assertEqual(expected, {(): Fraction(3)})
        for offset in (0, 3):
            for part, media_id, _, _, _, equation in IMAGE_PINS[offset:offset + 3]:
                lhs, rhs = equation.split("=")
                self.assertEqual(polynomial(rhs, bindings={"x": {(): Fraction(2)}}), expected)
                alt = self.ids[media_id].find("img").get("alt")
                self.assertIn(equation, alt)
            if offset:
                self.assertEqual(polynomial("f(2)", functions={"f": source_rule}), expected)
        for sid in ("fs-id1167829718470", "fs-id1167836456485"):
            self.assertIn("x = 2", text(self.ids[sid]))
            self.assertIn("मूल्य 3", text(self.ids[sid]))

    def test_all_twelve_actual_raster_hashes_and_distinct_locale_bytes(self):
        for part, media_id, size, en_sha, id_sha, _ in IMAGE_PINS:
            for locale, expected in (("en", en_sha), ("id", id_sha)):
                raw = self.images[(locale, part)]
                self.assertEqual(sha(raw), expected)
                self.assertTrue(raw.startswith(b"\xff\xd8\xff"))
                self.assertTrue(raw.endswith(b"\xff\xd9"))
                image = self.sources[locale][media_id].find(C + "image")
                self.assertEqual(image.get("src"), "../../media/" + image_name(part))
                self.assertEqual(image.get("mime-type"), "image/jpeg")
            self.assertEqual(len(self.images[("en", part)]), size)
            self.assertNotEqual(self.images[("en", part)], self.images[("id", part)])
        self.assertEqual(sum(len(raw) for (loc, _), raw in self.images.items() if loc == "en"), 98154)
        self.assertEqual(sum(len(raw) for (loc, _), raw in self.images.items() if loc == "id"), 516763)

    def test_all_six_image_alts_and_disclosed_source_description_corrections(self):
        images = list(self.root.iter("img"))
        self.assertEqual(len(images), 6)
        self.assertEqual([img.get("src") for img in images], ["asset:" + image_name(p[0]) for p in IMAGE_PINS])
        self.assertTrue(all(img.get("alt", "").strip() for img in images))
        garbled = self.sources["en"]["fs-id1167836433912"].get("alt")
        self.assertIn("4 ×7 2 ×1 5", garbled)
        self.assertIn("बिघडलेली चिन्हे", text(self.ids[SELECTED[6]]))
        self.assertIn("सर्व x साठी मूल्य 3 आहे असा त्याचा अर्थ नाही", text(self.ids[SELECTED[6]]))
        self.assertIn("horizontal", self.sources["en"]["fs-id1167832926879"].get("alt"))
        self.assertIn("horizontal", self.sources["id"]["fs-id1167832926879"].get("alt"))
        self.assertNotIn("रेषा", self.ids["fs-id1167832926879"].find("img").get("alt"))
        self.assertIn("उजव्या बाजूला", self.ids["fs-id1167836314769"].find("img").get("alt"))

    def test_missing_f_is_a_documented_source_correction_not_new_answer(self):
        self.assertEqual(normalized(maths(self.sources["en"][EXERCISES[1][3]])[0]), "(2)=13")
        self.assertEqual(normalized(maths(self.sources["id"][EXERCISES[1][3]])[0]), "f(2)=13")
        self.assertEqual(self.checks["try2-answer-a"], "f(2) = 13")
        source_solution = self.ids["fs-id1167829783753"]
        self.assertIn("गाळलेले अक्षर दुरुस्त", text(source_solution.find("h4")))
        notes = [text(n) for n in source_solution if n.get("data-kind") == "original"]
        self.assertEqual(len(notes), 1)
        for token in ("इंग्रजी", "इंडोनेशियन", "(2) = 13", "हे नवीन उत्तर नाही"):
            self.assertIn(token, notes[0])

    def test_notation_and_variable_role_definitions_preserve_source_distinctions(self):
        naming = self.ids["fs-id1167829590438"].findall("./ul/li")
        roles = self.ids["fs-id1167836732021"].findall("./ul/li")
        self.assertEqual(len(naming), 3)
        self.assertEqual(len(roles), 2)
        for node, tokens in zip(naming, (("f", "नाव"), ("x", "प्रांतातील"), ("f(x)", "y-मूल्य"))):
            for token in tokens:
                self.assertIn(token, text(node))
        self.assertIn("कंस गुणाकार दाखवत नाहीत", text(self.ids[SELECTED[0]]))
        for token in ("प्रांतातील कोणतेही मूल्य", "नियंत्रणात असतोच असे नाही", "y बदललाच पाहिजे"):
            self.assertIn(token, text(self.root))
        for locale in self.sources:
            self.assertEqual(len(list(self.sources[locale]["fs-id1167829590438"].iter(M + "mtr"))), 3)
            self.assertEqual(len(list(self.sources[locale]["fs-id1167836732021"].iter(M + "mtr"))), 2)

    def test_local_navigation_and_no_dropped_selected_source_links(self):
        local_links = [a for a in self.root.iter("a") if a.get("href", "").startswith("#")]
        self.assertEqual(len(local_links), 13)
        for a in local_links:
            self.assertIn(a.get("href")[1:], self.ids)
            self.assertTrue(text(a))
        for sid, *_ in EXERCISES:
            exercise = self.sources["en"][sid].find(C + "exercise")
            problem, answer = exercise.find(C + "problem").get("id"), exercise.find(C + "solution").get("id")
            for start, end in ((problem, answer), (answer, problem)):
                self.assertIn("#" + end, [a.get("href") for a in self.ids[start].iter("a")])
        self.assertEqual(sum(a.get("href", "").startswith("https://") for a in self.root.iter("a")), 2)
        for source in self.sources.values():
            self.assertEqual([n for sid in SELECTED for n in source[sid].iter(C + "link")], [])
        self.assertIn("थेट स्थानिक वाचक-दुवे", text(self.ids["credits"]))

    def test_frozen_fragments_assets_and_all_witnesses_match_actual_sources(self):
        lock_path = BASE / f"provenance/{UNIT}.lock.json"
        if not lock_path.exists():
            self.skipTest("root provenance freeze has not occurred")
        lock = read_json(lock_path)
        self.assertEqual([s["target_id"] for s in lock["source_selections"]], list(SELECTED))
        self.assertEqual(len(lock["witnesses"]), 51)
        for witness in lock["witnesses"]:
            raw = local(witness["path"]).read_bytes()
            self.assertEqual(len(raw), witness["bytes"])
            self.assertEqual(sha(raw), witness["sha256"])
        for selection in lock["source_selections"]:
            sid = selection["target_id"]
            self.assertEqual(selection["locator"], "A20:m81373#" + sid)
            self.assertEqual([r["locale"] for r in selection["sources"]], ["en", "id"])
            for record in selection["sources"]:
                locale = record["locale"]
                archive, prefix, archive_sha, module_sha = PINS[locale]
                self.assertEqual(record["archive"], archive)
                self.assertEqual(record["archive_sha256"], archive_sha)
                self.assertEqual(record["module_sha256"], module_sha)
                self.assertEqual(record["member"], prefix + "modules/m81373/index.cnxml")
                raw = local(record["fragment_path"]).read_bytes()
                self.assertEqual(sha(raw), record["fragment_sha256"])
                self.assertEqual(structure(ET.fromstring(raw)), structure(self.sources[locale][sid]))
        self.assertEqual(len(lock["source_images"]), 12)
        self.assertEqual(set(self.config["assets"]), {image_name(p[0]) for p in IMAGE_PINS})
        for part, _, size, expected, _, _ in IMAGE_PINS:
            asset = self.config["assets"][image_name(part)]
            self.assertEqual(asset["path"], f"assets/{UNIT}/" + image_name(part))
            self.assertEqual(asset["mime"], "image/jpeg")
            self.assertEqual(asset["sha256"], expected)
            raw = local(asset["path"]).read_bytes()
            self.assertEqual(len(raw), size)
            self.assertEqual(raw, self.images[("en", part)])
        for record in lock["source_images"]:
            locale = record["locale"]
            part = re.fullmatch(r"CNX_IntAlg_Figure_03_05_(01[34][abc])_img.jpg", Path(record["member"]).name).group(1)
            raw = self.images[(locale, part)]
            self.assertEqual(record["bytes"], len(raw))
            self.assertEqual(record["sha256"], sha(raw))
            if locale == "en":
                self.assertEqual(record["committed_asset"], self.config["assets"][image_name(part)]["path"])
            else:
                self.assertNotIn("committed_asset", record)

    def test_exact_polynomial_helper_detects_wrong_grouping_and_rejects_execution(self):
        self.assertEqual(polynomial("3*(-1)**2-2*(-1)+1"), {(): Fraction(6)})
        self.assertNotEqual(polynomial("3*(-1)**2"), polynomial("3*-1**2"))
        for unsafe in ("__import__('os')", "x.real", "x[-1]", "1/x", "x**-1", "unknown(x)"):
            with self.assertRaises((ValueError, SyntaxError)):
                polynomial(unsafe)


if __name__ == "__main__":
    unittest.main(verbosity=2)
