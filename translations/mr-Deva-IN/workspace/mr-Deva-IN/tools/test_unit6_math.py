"""Independent exact-arithmetic/source QA for the actual MR-BRIDGE-006 unit.

Run with python -B. No eval, downloads, extraction, builds, or writes. The narrow
AST interpreter evaluates Fraction polynomials, numeric absolute values, and
numeric rational values. Symbolic substitutions use coefficient identities,
not finite samples. This is not browser QA or Marathi-native/teacher review.
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
UNIT = "MR-BRIDGE-006"
C = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SELECTED_IDS = (
    "fs-id1167836714017", "fs-id1167829717540", "fs-id1167823013283", "fs-id1167829590640",
    "fs-id1167829744293", "fs-id1167836391029", "fs-id1167829877909", "fs-id1167836787728",
    "fs-id1167836574347", "fs-id1167829877536", "fs-id1167836575175", "fs-id1167829595951",
    "fs-id1167836399733", "fs-id1167833054462", "fs-id1167829924597", "fs-id1167836613442",
    "fs-id1167833381469", "fs-id1167826171384", "fs-id1167826025131", "fs-id1167833240212",
    "fs-id1167829713382", "fs-id1167833382456", "fs-id1167833052040", "fs-id1167836649081",
    "fs-id1167829906037", "fs-id1167833309035", "fs-id1167836409828", "fs-id1167836409832",
    "fs-id1167825884747", "fs-id1167833380107", "fs-id1167829749356",
)
EXERCISE_IDS = tuple(sid for i, sid in enumerate(SELECTED_IDS) if i not in (0, 1, 10, 17, 26))
MODULE_PINS = {
    "en": ("A20-canonical.zip", "osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81373/index.cnxml",
           "2b606026c2b34cdf69acfa29bfe4b90abdb6961a322a78c7ec20107e0948b05c"),
    "id": ("A20-v0.3.0-source.zip", "source/modules/m81373/index.cnxml",
           "e9e593b31587995170c520b9175f2e0c0cb335282c951bb1d769f775344311ee"),
}
# Independent transcriptions of the actual pinned MathML, not target config data.
RULES = dict(enumerate((
    "f(x)=5x−3", "f(x)=3x+4", "f(x)=−4x+2", "f(x)=−6x−3",
    "f(x)=x²−x+3", "f(x)=x²+x−2", "f(x)=2x²−x+3", "f(x)=3x²+x−2",
    "g(x)=2x+1", "g(x)=5x−8", "g(x)=−3x−2", "g(x)=−8x+2", "g(x)=3−x", "g(x)=7−5x",
    "f(x)=3x²−5x", "g(x)=4x²−3x", "F(x)=2x²−3x+1", "G(x)=3x²−5x+2",
    "h(t)=2|t−5|+4", "h(y)=3|y−1|−3", "f(x)=(x+2)/(x−1)", "g(x)=(x−2)/(x+2)",
    "N(t)=85+20t", "N(t)=43+t", "C(x)=3.25x+1500", "C(x)=7.25x+2500",
), 1))
SINGLE_QUERIES = dict(zip(range(15, 23), ("f(2)", "g(3)", "F(−1)", "G(−2)", "h(−4)", "h(−4)", "f(2)", "g(4)")))
SINGLE_ANSWERS = dict(zip(range(15, 23), map(F, (2, 27, 6, 24, 22, 12, 4, "1/3"))))
NUMERIC_BASIC = ((7, -8), (10, 1), (-6, 6), (-15, 3), (5, 5), (4, -2), (9, 6), (12, 0))
SYMBOLS = frozenset(("x", "a", "h", "t", "y"))
FUNCTION_NAMES = frozenset(("f", "g", "F", "G", "h", "N", "C", "abs"))


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
    lock_path = BASE / f"provenance/{UNIT}.lock.json"
    fragments = {}
    if lock_path.is_file():
        lock = read_json(lock_path)
        if [s["target_id"] for s in lock["source_selections"]] != list(SELECTED_IDS):
            raise ValueError("unexpected source selection")
        pins = {(w["path"], w["sha256"]) for w in lock["witnesses"]}
        for selection in lock["source_selections"]:
            if selection["locator"] != "A20:m81373#" + selection["target_id"]:
                raise ValueError("source locator mismatch")
            for source in selection["sources"]:
                locale = source["locale"]
                if source["module_sha256"] != MODULE_PINS[locale][2]:
                    raise ValueError("source module pin drift")
                if (source["fragment_path"], source["fragment_sha256"]) not in pins:
                    raise ValueError("unpinned source fragment")
                raw = local_path(source["fragment_path"]).read_bytes()
                if hashlib.sha256(raw).hexdigest() != source["fragment_sha256"]:
                    raise ValueError("source fragment hash drift")
                key = (selection["target_id"], locale)
                if key in fragments:
                    raise ValueError("duplicate source fragment")
                fragments[key] = ET.fromstring(raw)
        if set(fragments) != {(sid, locale) for sid in SELECTED_IDS for locale in ("en", "id")}:
            raise ValueError("missing source fragment")
        return lock, fragments
    for locale, (archive, member, digest) in MODULE_PINS.items():
        with zipfile.ZipFile(BASE.parent / "downloads/mr-Deva-IN/releases" / archive) as handle:
            raw = handle.read(member)  # Read only this member; no extraction.
        if hashlib.sha256(raw).hexdigest() != digest:
            raise ValueError("source module hash drift")
        root = ET.fromstring(raw)
        parent = next(p for p in root.iter() if any(n.get("id") == SELECTED_IDS[0] for n in p))
        children = list(parent)
        start = next(i for i, n in enumerate(children) if n.get("id") == SELECTED_IDS[0])
        selected = children[start:]
        if [n.get("id") for n in selected] != list(SELECTED_IDS):
            raise ValueError("group no longer ends the Practice Makes Perfect section")
        fragments.update({(n.get("id"), locale): n for n in selected})
    return None, fragments


def mathml_display(node):
    tag = node.tag.removeprefix(M)
    if tag == "msup" and len(node) == 2:
        return "(" + mathml_display(node[0]) + ")**(" + mathml_display(node[1]) + ")"
    if tag == "mfrac" and len(node) == 2:
        return "(" + mathml_display(node[0]) + ")/(" + mathml_display(node[1]) + ")"
    if tag in ("mi", "mn", "mo"):
        value = text(node)
        # ID decimal commas are normalized only inside numeric MathML tokens.
        return value.replace(",", ".") if tag == "mn" and re.fullmatch(r"[0-9]+,[0-9]+", value) else value
    if tag in ("math", "mrow"):
        return "".join(mathml_display(child) for child in node)
    raise ValueError(f"unsupported source MathML: {tag}")


def mixed_display(node):
    if node.tag.startswith(M):
        return mathml_display(node)
    return (node.text or "") + "".join(mixed_display(child) + (child.tail or "") for child in node)


def normalize(display):
    display = re.sub(r"\s+", "", display).replace("−", "-").replace("·", "*")
    display = display.replace("²", "**2").replace("³", "**3")
    if display.count("|") % 2:
        raise ValueError("unmatched absolute-value delimiter")
    while "|" in display:
        left = display.index("|")
        right = display.index("|", left + 1)
        if right == left + 1:
            raise ValueError("empty absolute-value expression")
        display = display[:left] + "abs(" + display[left + 1:right] + ")" + display[right + 1:]
    # Rewrite decimal literals before AST parsing, so no binary float is used.
    display = re.sub(r"([0-9]+)\.([0-9]+)", lambda m: f"({int(m[1] + m[2])}/{10 ** len(m[2])})", display)
    return re.sub(r"(?<=[0-9)])(?=[A-Za-z(])|(?<=[xaty])(?=\()", "*", display)


def expression(display):
    try:
        tree = ast.parse(normalize(display), mode="eval").body
    except SyntaxError as error:
        raise ValueError("invalid expression") from error
    allowed = (ast.BinOp, ast.UnaryOp, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow,
               ast.UAdd, ast.USub, ast.Name, ast.Load, ast.Constant, ast.Call)
    for node in ast.walk(tree):
        if not isinstance(node, allowed):
            raise ValueError("unsupported expression syntax")
        if isinstance(node, ast.Constant) and type(node.value) is not int:
            raise ValueError("only exact integer/rewritten decimal literals are allowed")
        if isinstance(node, ast.Name) and node.id not in SYMBOLS | FUNCTION_NAMES:
            raise ValueError("unknown symbol")
        if isinstance(node, ast.Call) and (not isinstance(node.func, ast.Name) or
                node.func.id not in FUNCTION_NAMES or len(node.args) != 1 or node.keywords):
            raise ValueError("unsupported call")
    return tree


def shape(display):
    return ast.dump(expression(display), include_attributes=False)


def rule(display):
    parts = display.split("=")
    if len(parts) != 2:
        raise ValueError("expected a single function definition")
    left, right = map(expression, parts)
    if not isinstance(left, ast.Call) or left.func.id == "abs" or not isinstance(left.args[0], ast.Name):
        raise ValueError("expected named function and parameter")
    parameter = left.args[0].id
    if parameter not in SYMBOLS:
        raise ValueError("invalid function parameter")
    names = {n.id for n in ast.walk(right) if isinstance(n, ast.Name)}
    if not names <= {parameter, "abs"}:
        raise ValueError("function has an undeclared variable")
    return left.func.id, parameter, right


def compact(poly):
    return {term: F(coefficient) for term, coefficient in poly.items() if coefficient}


def constant(value):
    return compact({(): F(value)})


def add(left, right, scale=F(1)):
    result = left.copy()
    for term, value in right.items():
        result[term] = result.get(term, F(0)) + scale * value
    return compact(result)


def multiply(left, right):
    result = {}
    for a, u in left.items():
        for b, v in right.items():
            term = tuple(sorted(a + b))
            result[term] = result.get(term, F(0)) + u * v
    return compact(result)


def scalar(poly):
    if set(poly) - {()}:
        raise ValueError("numeric value required")
    return poly.get((), F(0))


def calculate(node, functions, bindings=None, depth=0):
    """Exact coefficient interpreter; it never compiles or executes source text."""
    if depth > 30:
        raise ValueError("expression nesting limit")
    bindings = {} if bindings is None else bindings
    def visit(child):
        return calculate(child, functions, bindings, depth + 1)
    if isinstance(node, ast.Constant):
        return constant(node.value)
    if isinstance(node, ast.Name) and node.id in SYMBOLS:
        return bindings.get(node.id, {(node.id,): F(1)})
    if isinstance(node, ast.UnaryOp):
        operand = visit(node.operand)
        return {term: value * (-1 if isinstance(node.op, ast.USub) else 1) for term, value in operand.items()}
    if isinstance(node, ast.BinOp):
        left, right = visit(node.left), visit(node.right)
        if isinstance(node.op, (ast.Add, ast.Sub)):
            return add(left, right, F(-1) if isinstance(node.op, ast.Sub) else F(1))
        if isinstance(node.op, ast.Mult):
            return multiply(left, right)
        if isinstance(node.op, ast.Div):
            denominator = scalar(right)
            if not denominator:
                raise ValueError("zero denominator: value outside the function domain")
            return compact({term: value / denominator for term, value in left.items()})
        if isinstance(node.op, ast.Pow):
            exponent = scalar(right)
            if exponent.denominator != 1 or not 0 <= exponent <= 4:
                raise ValueError("unsupported exponent")
            result = constant(1)
            for _ in range(int(exponent)):
                result = multiply(result, left)
            return result
    if isinstance(node, ast.Call):
        argument = visit(node.args[0])
        if node.func.id == "abs":
            return constant(abs(scalar(argument)))
        if node.func.id not in functions:
            raise ValueError("undefined or wrongly cased function")
        parameter, body = functions[node.func.id]
        return calculate(body, functions, {parameter: argument}, depth + 1)
    raise ValueError("unsupported expression")


def evaluate(display, definition=None):
    functions = {}
    if definition is not None:
        name, parameter, body = rule(definition)
        functions[name] = (parameter, body)
    return calculate(expression(display), functions)


def queries(n):
    if n <= 8:
        return ("f(2)", "f(−1)", "f(a)")
    if n <= 14:
        return ("g(h²)", "g(x+2)", "g(x)+g(2)")
    if n <= 22:
        return (SINGLE_QUERIES[n],)
    return ("N(4)",) if n == 23 else ("N(30)",) if n == 24 else ("C(0)", "C(1000)")


class Unit6MathematicsTests(unittest.TestCase):
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
                    raise ValueError("duplicate mathematical check key")
                cls.checks[node.get("data-check")] = text(node)
        cls.source_rules = {}
        for n, sid in enumerate(EXERCISE_IDS, 1):
            for locale in ("en", "id"):
                problem = cls.sources[(sid, locale)].find(C + "problem")
                displays = [mathml_display(m) for m in problem.iter(M + "math")]
                cls.source_rules[(n, locale)] = next(s for s in displays if "=" in s).split(";")[0]

    def assert_chain(self, display, definition, query):
        parts = display.split("=")
        self.assertGreaterEqual(len(parts), 2)
        self.assertEqual(shape(parts[0]), shape(query), "answer addresses a different input")
        expected = evaluate(query, definition)
        for step in parts:
            self.assertEqual(evaluate(step, definition), expected, "an equality-chain step changes the value")

    def test_actual_structure_and_all_107_config_entries(self):
        self.assertEqual(self.root.get("id"), UNIT)
        self.assertEqual(self.root.get("lang"), "mr-Deva-IN")
        decoded = self.raw.decode("utf-8")
        self.assertEqual(unicodedata.normalize("NFC", decoded), decoded)
        self.assertNotIn("\ufffd", decoded)
        self.assertEqual(self.checks, self.config["expected_math"])
        self.assertEqual(len(self.checks), 107)
        self.assertEqual(self.config["source_count"], 31)
        self.assertEqual(self.config["translated_practice_items"], 26)
        self.assertEqual(self.config["translated_worked_examples"], 0)
        self.assertEqual(self.config["original_practice_items"], 0)
        self.assertEqual(self.config["question_ids"], [])
        for term in self.config["required_terms"]:
            self.assertIn(term, text(self.root))

    def test_all_26_rules_match_actual_en_id_mathml_and_independent_reading(self):
        for n, expected in RULES.items():
            key = f"q{n}-rule" if n <= 14 else f"q{n}-prompt" if n <= 22 else f"q{n}-model"
            target = self.checks[key].split(";")[0]
            for locale in ("en", "id"):
                with self.subTest(question=n, locale=locale):
                    actual = self.source_rules[(n, locale)]
                    for definition in (actual, target):
                        got_name, got_parameter, got_body = rule(definition)
                        name, parameter, body = rule(expected)
                        self.assertEqual((got_name, got_parameter), (name, parameter))
                        self.assertEqual(ast.dump(got_body), ast.dump(body))

    def test_all_source_request_arguments_and_function_letter_cases_are_preserved(self):
        for locale in ("en", "id"):
            for sid, expected in ((SELECTED_IDS[1], queries(1)), (SELECTED_IDS[10], queries(9))):
                source_queries = [mathml_display(m) for m in self.sources[(sid, locale)].iter(M + "math")]
                self.assertEqual([shape(q.rstrip(".;")) for q in source_queries], [shape(q) for q in expected])
            for n in range(15, 27):
                source = self.sources[(EXERCISE_IDS[n - 1], locale)].find(C + "problem")
                # Application introductions may mention C(x) as a quantity;
                # the requested evaluations are in the following subpart paras.
                query_nodes = list(source) if n <= 22 else source.findall(C + "para")[1:]
                source_queries = [mathml_display(m).rstrip(".;") for node in query_nodes for m in node.iter(M + "math")
                                  if "=" not in mathml_display(m)]
                self.assertEqual([shape(q) for q in source_queries], [shape(q) for q in queries(n)])
                if n <= 22:
                    self.assertEqual(shape(self.checks[f"q{n}-prompt"].split(";")[1]), shape(queries(n)[0]))

    def test_24_basic_subparts_and_all_intermediate_steps(self):
        for n in range(1, 9):
            definition = self.source_rules[(n, "en")]
            for part, query in zip("abc", queries(n)):
                self.assert_chain(self.checks[f"q{n}-{part}"], definition, query)
                work = self.checks.get(f"q{n}-work-{part}")
                if work:
                    self.assert_chain(work, definition, query)
            self.assertEqual(tuple(scalar(evaluate(q, definition)) for q in queries(n)[:2]),
                             tuple(map(F, NUMERIC_BASIC[n - 1])))

    def test_18_expression_subparts_are_polynomial_identities_not_grid_samples(self):
        for n in range(9, 15):
            definition = self.source_rules[(n, "en")]
            for part, query in zip("abc", queries(n)):
                self.assert_chain(self.checks[f"q{n}-{part}"], definition, query)
                work = self.checks.get(f"q{n}-work-{part}")
                if work:
                    self.assert_chain(work, definition, query)
            shifted = evaluate("g(x+2)", definition)
            sum_of_values = evaluate("g(x)+g(2)", definition)
            self.assertNotEqual(shifted, sum_of_values)
            # For g(x)=m*x+b, the difference is exactly b, for every real x.
            self.assertEqual(add(sum_of_values, shifted, F(-1)), evaluate("g(0)", definition))

    def test_eight_single_values_and_every_shown_step(self):
        for n, expected in SINGLE_ANSWERS.items():
            query = SINGLE_QUERIES[n]
            definition = self.source_rules[(n, "en")]
            self.assertEqual(scalar(evaluate(query, definition)), expected)
            self.assert_chain(self.checks[f"q{n}-work"], definition, query)
            if f"q{n}-answer" in self.checks:
                self.assertEqual(scalar(evaluate(self.checks[f"q{n}-answer"])), expected)

    def test_absolute_values_keep_signs_and_rational_inputs_exclude_zero_denominators(self):
        self.assertEqual(scalar(evaluate("|−4−5|")), F(9))
        self.assertEqual(scalar(evaluate("|−4−1|")), F(5))
        self.assertEqual(scalar(evaluate("(−2)²")), F(4))
        self.assertNotEqual(evaluate("(−2)²"), evaluate("−2²"))
        for n, forbidden in ((21, "f(1)"), (22, "g(−2)")):
            with self.subTest(question=n), self.assertRaisesRegex(ValueError, "zero denominator"):
                evaluate(forbidden, self.source_rules[(n, "en")])
        self.assertEqual(evaluate("g(4)", self.source_rules[(22, "en")]), constant(F(1, 3)))
        self.assertIn("छेद 1", text(self.ids[EXERCISE_IDS[20]]))
        self.assertIn("छेद 6", text(self.ids[EXERCISE_IDS[21]]))

    def test_all_six_application_values_and_decimal_coefficients_are_exact(self):
        applications = {23: (("N(4)", 165, "work"),), 24: (("N(30)", 73, "work"),),
                        25: (("C(0)", 1500, "work-zero"), ("C(1000)", 4750, "work-thousand")),
                        26: (("C(0)", 2500, "work-zero"), ("C(1000)", 9750, "work-thousand"))}
        for n, entries in applications.items():
            definition = self.source_rules[(n, "en")]
            for query, expected, key in entries:
                self.assertEqual(evaluate(query, definition), constant(expected))
                self.assert_chain(self.checks[f"q{n}-{key}"], definition, query)
            for key, query in (("answer", queries(n)[0]), ("zero", "C(0)"), ("thousand", "C(1000)")):
                if f"q{n}-{key}" in self.checks:
                    self.assert_chain(self.checks[f"q{n}-{key}"], definition, query)
        self.assertEqual(evaluate("3.25"), constant(F(13, 4)))
        self.assertEqual(evaluate("7.25"), constant(F(29, 4)))
        for n, decimal in ((25, "3,25"), (26, "7,25")):
            source = self.sources[(EXERCISE_IDS[n - 1], "id")]
            self.assertIn(decimal, [text(node) for node in source.iter(M + "mn")])

    def test_application_roles_units_counts_and_interpretations(self):
        for n in (23, 24):
            self.assertEqual(self.checks[f"q{n}-variables"], "t स्वतंत्र; N अवलंबी")
        self.assertEqual(self.checks["q25-variables"], "x स्वतंत्र; C अवलंबी")
        self.assertEqual(self.checks["q26-variables"], "x स्वतंत्र; C(x) अवलंबी")
        for n, tokens in ((23, ("Sylvia", "DVR", "85", "20", "आठवड्य", "165")),
                          (24, ("Ken", "43", "दिवस", "30", "73", "कोड")),
                          (25, ("दैनिक", "डॉलर", "पुस्तक", "1500", "4750", "1000")),
                          (26, ("दैनिक", "वस्तू", "2500", "9750", "1000"))):
            target = text(self.ids[EXERCISE_IDS[n - 1]])
            for token in tokens:
                self.assertIn(token, target)
        self.assertIn("weeks", text(self.sources[(EXERCISE_IDS[22], "en")]))
        self.assertIn("days", text(self.sources[(EXERCISE_IDS[23], "en")]))
        self.assertIn("dollars", text(self.sources[(EXERCISE_IDS[24], "en")]))
        source26 = text(self.sources[(EXERCISE_IDS[25], "en")])
        target26 = text(self.ids[EXERCISE_IDS[25]])
        self.assertNotIn("dollars", source26)
        for invented_unit in ("डॉलर", "रुपय", "USD", "$"):
            self.assertNotIn(invented_unit, target26)
        # Requested contextual inputs are nonnegative whole periods/items.
        for n in range(23, 27):
            for query in queries(n):
                argument = expression(query).args[0]
                self.assertIsInstance(argument, ast.Constant)
                self.assertGreaterEqual(argument.value, 0)

    def test_all_13_supplied_answers_match_actual_sources_and_math(self):
        for n in range(1, 27, 2):
            for locale in ("en", "id"):
                source = self.sources[(EXERCISE_IDS[n - 1], locale)].find(C + "solution")
                definition = self.source_rules[(n, locale)]
                if n <= 13:
                    parts = [p.strip() for p in re.split("[ⓐⓑⓒ]", mixed_display(source)) if p.strip()]
                    self.assertEqual(len(parts), 3)
                    for answer, query in zip(parts, queries(n)):
                        self.assert_chain(answer, definition, query)
                elif n <= 21:
                    self.assertEqual(evaluate(text(source)), constant(SINGLE_ANSWERS[n]))
                else:
                    roles = "t IND; N DEP" if n == 23 else "x IND; C DEP"
                    if locale == "id":
                        roles = roles.replace("IND", "BEBAS").replace("DEP", "TERIKAT")
                    self.assertIn(roles, text(source))
                    answers = [mathml_display(m) for m in source.iter(M + "math")]
                    self.assertEqual(len(answers), len(queries(n)))
                    for answer, query in zip(answers, queries(n)):
                        if n == 25 and locale == "en":
                            self.assertTrue(answer.startswith("N("))
                            answer = "C" + answer[1:]  # Only the documented symbol correction.
                        self.assert_chain(answer, definition, query)

    def test_printing_cost_symbol_correction_is_explicit_not_codified_as_n(self):
        target = self.ids[EXERCISE_IDS[24]]
        source = self.sources[(EXERCISE_IDS[24], "en")]
        source_answer = source.find(C + "solution")
        self.assertEqual([mathml_display(m) for m in source_answer.iter(M + "math")],
                         ["N(0)=1500", "N(1000)=4750"])
        id_answer = self.sources[(EXERCISE_IDS[24], "id")].find(C + "solution")
        self.assertEqual([mathml_display(m) for m in id_answer.iter(M + "math")],
                         ["C(0)=1500", "C(1000)=4750"])
        notes = " ".join(text(p) for p in target.iter("p") if p.get("data-kind") == "original")
        for token in ("स्रोतदुरुस्ती", "N(0)", "N(1000)", "C(0)", "C(1000)", "इंडोनेशियन"):
            self.assertIn(token, notes)
        for key, value in self.checks.items():
            if key.startswith("q25-"):
                self.assertNotIn("N(", value)
        self.assertIn("दुरुस्ती", text(self.ids[source_answer.get("id")].find("h3")))

    def test_all_31_blocks_and_119_original_ids_preserved_in_order(self):
        self.assertEqual([n.get("data-source") for n in self.root.iter() if n.get("data-source")],
                         ["A20:m81373#" + sid for sid in SELECTED_IDS])
        actual_ids = [n.get("id") for n in self.root.iter() if n.get("id", "").startswith("fs-id")]
        for locale in ("en", "id"):
            original = [n.get("id") for sid in SELECTED_IDS for n in self.sources[(sid, locale)].iter() if n.get("id")]
            self.assertEqual(len(original), 119)
            self.assertEqual(len(set(original)), 119)
            self.assertEqual(actual_ids, original)
            for sid in SELECTED_IDS:
                target = self.ids[sid]
                source = self.sources[(sid, locale)]
                self.assertTrue({n.get("id") for n in source.iter() if n.get("id")} <=
                                {n.get("id") for n in target.iter() if n.get("id")})
                for kind in ("problem", "solution"):
                    for part in source.findall(C + kind):
                        child = next(n for n in target if n.get("id") == part.get("id"))
                        self.assertIn(kind, child.get("class", "").split())

    def test_13_preserved_and_13_visibly_authored_answers_and_26_navigation_pairs(self):
        counts = {"source": 0, "original": 0}
        for n, sid in enumerate(EXERCISE_IDS, 1):
            answers = [node for node in self.ids[sid].iter() if "solution" in node.get("class", "").split()]
            self.assertEqual(len(answers), 1)
            answer = answers[0]
            for locale in ("en", "id"):
                self.assertEqual(self.sources[(sid, locale)].find(C + "solution") is not None, n % 2 == 1)
            source = self.sources[(sid, "en")]
            source_answer = source.find(C + "solution")
            if source_answer is not None:
                counts["source"] += 1
                self.assertEqual(answer.get("id"), source_answer.get("id"))
                self.assertNotEqual(answer.get("data-kind"), "original")
                self.assertTrue(text(answer.find("h3")).startswith("स्रोतातील उत्तर"))
            else:
                counts["original"] += 1
                self.assertEqual(answer.get("id"), "mr-answer-" + sid)
                self.assertEqual(answer.get("data-kind"), "original")
                self.assertEqual(text(answer.find("h3")), "नव्याने जोडलेले उत्तर")
                self.assertIn("हे उत्तर मूळ स्रोतात दिलेले नाही", text(answer))
            problem_id = source.find(C + "problem").get("id")
            for start, end in ((problem_id, answer.get("id")), (answer.get("id"), problem_id)):
                self.assertIn("#" + end, [a.get("href") for a in self.ids[start].iter("a") if text(a)])
        self.assertEqual(counts, {"source": 13, "original": 13})
        for anchor in self.root.iter("a"):
            if anchor.get("href", "").startswith("#"):
                self.assertIn(anchor.get("href")[1:], self.ids)

    def test_frozen_witnesses_complete_and_no_source_media_or_links_omitted(self):
        self.assertIsNotNone(self.lock, "freeze selected source fragments before final unit QA")
        self.assertEqual(len(self.sources), 62)
        self.assertEqual(self.config.get("assets", {}), {})
        self.assertEqual(list(self.root.iter("img")), [])
        for fragment in self.sources.values():
            self.assertEqual(list(fragment.iter(C + "media")), [])
            self.assertEqual(list(fragment.iter(C + "image")), [])
            self.assertEqual(list(fragment.iter(C + "link")), [])


class ExactInterpreterTests(unittest.TestCase):
    def test_decimal_fraction_and_negative_square_are_exact(self):
        self.assertEqual(evaluate("3.25"), constant(F(13, 4)))
        self.assertEqual(evaluate("0.1+0.2"), constant(F(3, 10)))
        self.assertEqual(evaluate("2/6"), constant(F(1, 3)))
        self.assertEqual(evaluate("2(−1)²−(−1)+3"), constant(6))
        self.assertEqual(evaluate("(−2)²"), constant(4))
        self.assertEqual(evaluate("−2²"), constant(-4))

    def test_symbolic_substitution_and_function_case(self):
        self.assertEqual(evaluate("g(x+2)", "g(x)=−3x−2"), {("x",): F(-3), (): F(-8)})
        self.assertEqual(evaluate("g(h²)", "g(x)=−3x−2"), {("h", "h"): F(-3), (): F(-2)})
        self.assertEqual(evaluate("f(a)", "f(x)=x²−x+3"), {("a", "a"): F(1), ("a",): F(-1), (): F(3)})
        with self.assertRaises(ValueError):
            evaluate("f(−1)", "F(x)=2x²−3x+1")

    def test_numeric_absolute_value_and_rational_domain(self):
        self.assertEqual(evaluate("h(−4)", "h(t)=2|t−5|+4"), constant(22))
        self.assertEqual(evaluate("h(−4)", "h(y)=3|y−1|−3"), constant(12))
        with self.assertRaisesRegex(ValueError, "zero denominator"):
            evaluate("f(1)", "f(x)=(x+2)/(x−1)")
        with self.assertRaises(ValueError):
            evaluate("|x|")  # Do not pretend an absolute-value expression is one polynomial.

    def test_unsafe_or_unsupported_syntax_is_rejected_without_execution(self):
        for display in ("__import__('os')", "x.real", "x[0]", "True", "1e3", "1/0", "x**-1",
                        "x**x", "abs(x,2)", "abs(x=2)", "|−4", "||", "1;2", "z+1"):
            with self.subTest(display=display), self.assertRaises(ValueError):
                evaluate(display)
        with self.assertRaises(ValueError):
            rule("f(x)=x+y")


if __name__ == "__main__":
    unittest.main(verbosity=2)
