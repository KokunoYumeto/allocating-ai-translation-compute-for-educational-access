"""Read-only, independent arithmetic/source-anchor QA for MR-BRIDGE-002.

Run: python -B mr-Deva-IN/tools/test_unit2_math.py
Reads the real unit, config, and small pinned fragments. No builds or downloads.
Fraction arithmetic and polynomial coefficients supplement, not replace, review
of Marathi prose, model assumptions, source images, and rendered presentation.
"""
import ast
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET


BASE = Path(__file__).resolve().parents[1]
UNIT = "MR-BRIDGE-002"
CNXML = "{http://cnx.rice.edu/cnxml}"
MATHML = "{http://www.w3.org/1998/Math/MathML}"
MODELS = {
    "sylvia": (F(75), F(10), F(5), F(125), "fs-id1167833158753"),
    "bryan": (F(100), F(15), F(7), F(205), "fs-id1167833369424"),
    "anthony": (F(110), F(25), F(14), F(460), "fs-id1167836481611"),
}
RESOURCE_ID = "fs-id1167833128952"
RESOURCE_URL = "https://openstax.org/l/37introfunction"


def text(node):
    return "".join(node.itertext()).strip()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def domain_contains(value):
    value = F(value)
    return value.denominator == 1 and value >= 0


def range_contains(value, model):
    intercept, slope = model
    return domain_contains((F(value) - intercept) / slope)


def trim(coefficients):
    result = list(coefficients)
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return tuple(result)


def add(left, right, sign=1):
    return trim([(left[i] if i < len(left) else F(0))
                 + sign * (right[i] if i < len(right) else F(0))
                 for i in range(max(len(left), len(right)))])


def multiply(left, right):
    result = [F(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return trim(result)


def polynomial(expression, model=None, t_value=None):
    """Parse a tiny arithmetic grammar, never eval source text.

    Coefficients are ascending powers of t. Decimal literals are converted from
    their source spelling to Fraction, not from their binary float AST values.
    Calls to N at numeric inputs enforce the explicitly chosen discrete domain.
    """
    normalized = expression.replace("−", "-").replace("·", "*")
    normalized = normalized.replace("[", "(").replace("]", ")").strip()
    normalized = re.sub(r"(?<=[0-9)])\s*(?=[t(])", "*", normalized)
    tree = ast.parse(normalized, mode="eval")

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return (F(ast.get_source_segment(normalized, node)),)
        if isinstance(node, ast.Name) and node.id == "t":
            return (F(t_value),) if t_value is not None else (F(0), F(1))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            result = visit(node.operand)
            return result if isinstance(node.op, ast.UAdd) else tuple(-n for n in result)
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                return add(left, right)
            if isinstance(node.op, ast.Sub):
                return add(left, right, -1)
            if isinstance(node.op, ast.Mult):
                return multiply(left, right)
            if isinstance(node.op, ast.Div) and len(right) == 1:
                return trim([number / right[0] for number in left])
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "N" and len(node.args) == 1 and not node.keywords and model is not None):
            argument = visit(node.args[0])
            if len(argument) == 1 and not domain_contains(argument[0]):
                raise ValueError("N is undefined outside the chosen nonnegative-integer domain")
            return add((model[0],), multiply((model[1],), argument))
        raise ValueError(f"unsupported arithmetic syntax: {ast.dump(node)}")

    return visit(tree.body)


def number(expression, model=None, t_value=None):
    coefficients = polynomial(expression, model=model, t_value=t_value)
    if len(coefficients) != 1:
        raise ValueError("numeric expression still contains t")
    return coefficients[0]


def displayed_model(rule):
    left, right = rule.split("=")
    if re.sub(r"\s", "", left) != "N(t)":
        raise ValueError("expected a rule for N(t)")
    coefficients = polynomial(right)
    if len(coefficients) != 2:
        raise ValueError("expected a nonconstant linear rule")
    return coefficients


def sequence_prefix(display):
    match = re.fullmatch(r"\{(.*),\s*…\}", display)
    if not match:
        raise ValueError("expected an explicitly continuing sequence")
    return [F(value.strip()) for value in match.group(1).split(",")]


class Unit2MathematicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = ET.fromstring((BASE / f"translations/{UNIT}.xml").read_bytes())
        cls.config = json.loads((BASE / f"units/{UNIT}.json").read_text(encoding="utf-8"),
                                object_pairs_hook=unique_object)
        cls.lock = json.loads((BASE / f"provenance/{UNIT}.lock.json").read_text(encoding="utf-8"),
                              object_pairs_hook=unique_object)
        cls.ids = {}
        cls.checks = {}
        for node in cls.root.iter():
            if "id" in node.attrib:
                if node.get("id") in cls.ids:
                    raise ValueError("duplicate XML ID")
                cls.ids[node.get("id")] = node
            if "data-check" in node.attrib:
                if node.get("data-check") in cls.checks:
                    raise ValueError("duplicate math-check ID")
                cls.checks[node.get("data-check")] = text(node)
        cls.models = {name: displayed_model(cls.checks[name + "-rule"]) for name in MODELS}
        cls.fragments = {}
        for selection in cls.lock["source_selections"]:
            for witness in selection["sources"]:
                path = (BASE / witness["fragment_path"]).resolve()
                if not path.is_relative_to(BASE):
                    raise ValueError("fragment path escapes language directory")
                raw = path.read_bytes()
                if hashlib.sha256(raw).hexdigest() != witness["fragment_sha256"]:
                    raise ValueError("pinned fragment hash changed")
                cls.fragments[(selection["target_id"], witness["locale"])] = ET.fromstring(raw)

    def assert_numeric_chain(self, display, expected, model=None, t_value=None):
        expressions = display.split("=")
        self.assertGreaterEqual(len(expressions), 2)
        for expression in expressions:
            with self.subTest(expression=expression):
                self.assertEqual(number(expression, model=model, t_value=t_value), expected)

    def test_real_config_and_xml_math_agree(self):
        self.assertEqual(self.config["expected_math"], self.checks)
        self.assertEqual(self.root.get("id"), UNIT)
        self.assertEqual(self.root.get("lang"), "mr-Deva-IN")

    def test_three_models_match_source_numbers_and_independent_answers(self):
        for name, (initial, rate, day, result, source_id) in MODELS.items():
            with self.subTest(model=name):
                model = self.models[name]
                self.assertEqual(model, (initial, rate))
                self.assertEqual(model[0] + model[1] * day, result)
                self.assert_numeric_chain(self.checks[name + "-result"], result, model=model)
                for locale in ("en", "id"):
                    source = self.fragments[(source_id, locale)]
                    first_math = next(source.iter(MATHML + "math"))
                    numeric_tokens = [F(text(node)) for node in first_math.iter(MATHML + "mn")]
                    self.assertEqual(numeric_tokens, [initial, rate])
                # All three source solutions state the result in prose, even
                # though Sylvia's preceding working is supplied as images.
                source = self.fragments[(source_id, "en")]
                solution = next(source.iter(CNXML + "solution"))
                self.assertRegex(text(solution), rf"\b{result.numerator}\b")
                problem_id = next(source.iter(CNXML + "problem")).get("id")
                displayed_queries = re.findall(r"N\(\s*([0-9]+)\s*\)", text(self.ids[problem_id]))
                self.assertEqual([F(value) for value in displayed_queries], [day])

    def test_sylvia_working_and_initial_count(self):
        for key in ("sylvia-substitution", "sylvia-sum", "sylvia-result"):
            self.assert_numeric_chain(self.checks[key], F(125), model=self.models["sylvia"])
        self.assert_numeric_chain(self.checks["initial-count"], F(75), model=self.models["sylvia"])
        self.assertEqual(F(125) - F(75), F(10) * F(5))

    def test_daily_count_table_all_six_rows(self):
        rows = self.ids["daily-counts"].findall("tbody/tr")
        self.assertEqual(len(rows), 6)
        parsed = []
        for row in rows:
            cells = row.findall("td")
            self.assertEqual(len(cells), 2)
            day, count = (F(text(cell)) for cell in cells)
            self.assertTrue(domain_contains(day))
            self.assertEqual(count, self.models["sylvia"][0] + self.models["sylvia"][1] * day)
            parsed.append((day, count))
        self.assertEqual([row[0] for row in parsed], [F(day) for day in range(6)])
        self.assertEqual([row[1] for row in parsed], [F(value) for value in (75, 85, 95, 105, 115, 125)])

    def test_daily_increment_by_polynomial_coefficients_not_samples(self):
        parts = self.checks["daily-increment"].split("=")
        self.assertEqual(len(parts), 3)
        coefficients = [polynomial(part, model=self.models["sylvia"]) for part in parts]
        self.assertEqual(coefficients, [(F(10),)] * 3)
        # The cancellation is symbolic; domain use additionally assumes t >= 0
        # integral, so both t and t+1 belong to the declared daily-record domain.
        initial, rate = self.models["sylvia"]
        self.assertEqual(add((initial + rate, rate), (initial, rate), -1), (rate,))

    def test_original_p1_to_p4_answers_and_equations(self):
        model = self.models["sylvia"]
        self.assertEqual(self.config["question_ids"], ["P1", "P2", "P3", "P4"])
        expected_p1 = model[0] + model[1] * F(8)
        expected_p2 = (F(145) - model[0]) / model[1]
        expected_p3 = model[0] + model[1] * F(2)
        expected_p4 = (F(100) - model[0]) / model[1]
        self.assertEqual((expected_p1, expected_p2, expected_p3, expected_p4),
                         (F(155), F(7), F(95), F(5, 2)))
        self.assert_numeric_chain(self.checks["p1"], expected_p1, model=model)
        self.assert_numeric_chain(self.checks["p2"], expected_p2, t_value=expected_p2)
        self.assert_numeric_chain(self.checks["p3"], expected_p3, model=model)
        self.assert_numeric_chain(self.checks["p4"], expected_p4, t_value=expected_p4)
        self.assertTrue(domain_contains(expected_p2))
        self.assertFalse(domain_contains(expected_p4))
        self.assertFalse(range_contains(F(100), model))
        # Check additional untagged working in the two inverse problems.
        for answer_id, solution in (("S-P2", expected_p2), ("S-P4", expected_p4)):
            for span in self.ids[answer_id].iter("span"):
                display = text(span)
                if "=" in display:
                    values = [number(part, model=model, t_value=solution) for part in display.split("=")]
                    self.assertTrue(all(value == values[0] for value in values))
        growth = [text(span) for span in self.ids["S-P1"].iter("span") if "−" in text(span)]
        self.assertEqual(len(growth), 1)
        self.assert_numeric_chain(growth[0], F(80))

    def test_discrete_domain_and_range(self):
        model = self.models["sylvia"]
        self.assertEqual(sequence_prefix(self.checks["counting-domain"]), [F(n) for n in range(4)])
        self.assertEqual(sequence_prefix(self.checks["counting-range"]),
                         [model[0] + model[1] * n for n in range(4)])
        for value in (F(0), F(1), F(5), F(7), F(1000)):
            self.assertTrue(domain_contains(value))
            self.assertTrue(range_contains(model[0] + model[1] * value, model))
        for value in (F(-1), F(-1000), F(5, 4), F(5, 2), F(1, 2)):
            self.assertFalse(domain_contains(value))
        for value in (F(65), F(76), F(100), F(175, 2), F(-1)):
            self.assertFalse(range_contains(value, model))

    def test_outside_domain_examples_are_expressions_not_function_values(self):
        self.assert_numeric_chain(self.checks["fractional-count"], F(175, 2))
        self.assert_numeric_chain(self.checks["negative-time"], F(65))
        for key in ("fractional-count", "negative-time"):
            self.assertNotIn("N(", self.checks[key])
        self.assertNotRegex(text(self.root), r"N\s*\(\s*(?:1\.25|[−-]1)\s*\)\s*=")
        for expression in ("N(1.25)", "N(-1)", "N(2.5)"):
            with self.assertRaisesRegex(ValueError, "undefined outside"):
                number(expression, model=self.models["sylvia"])

    def test_nested_source_exercise_problem_and_solution_ids(self):
        for (source_id, locale), fragment in self.fragments.items():
            with self.subTest(source=source_id, locale=locale):
                translated = self.ids[source_id]
                translated_ids = {node.get("id"): node for node in translated.iter() if node.get("id")}
                source_ids = {node.get("id") for node in fragment.iter() if node.get("id")}
                self.assertTrue(source_ids <= set(translated_ids), source_ids - set(translated_ids))
                for exercise in fragment.iter(CNXML + "exercise"):
                    target_exercise = translated_ids[exercise.get("id")]
                    children = {node.get("id"): node for node in target_exercise}
                    for kind in ("problem", "solution"):
                        for part in exercise.findall(CNXML + kind):
                            self.assertIn(part.get("id"), children)
                            self.assertIn(kind, children[part.get("id")].get("class", "").split())

    def test_source_try_navigation_and_original_resource_url(self):
        for name in ("bryan", "anthony"):
            source_id = MODELS[name][-1]
            source = self.fragments[(source_id, "en")]
            problem_id = next(source.iter(CNXML + "problem")).get("id")
            solution_id = next(source.iter(CNXML + "solution")).get("id")
            self.assertIn("#" + solution_id, [a.get("href") for a in self.ids[problem_id].iter("a")])
            self.assertIn("#" + problem_id, [a.get("href") for a in self.ids[solution_id].iter("a")])
        links = [a.get("href") for a in self.ids[RESOURCE_ID].iter("a")]
        self.assertEqual(links, [RESOURCE_URL])
        for locale in ("en", "id"):
            source_links = [a.get("url") for a in self.fragments[(RESOURCE_ID, locale)].iter(CNXML + "link")]
            self.assertEqual(source_links, [RESOURCE_URL])


class ArithmeticParserTests(unittest.TestCase):
    def test_exact_decimal_arithmetic(self):
        self.assertEqual(number("0.1 + 0.2"), F(3, 10))
        self.assertEqual(number("75 + 10 · (−1)"), F(65))

    def test_unexpected_code_is_never_executed(self):
        for expression in ("__import__('os')", "t.__class__", "[x for x in t]", "2 ** 3"):
            with self.subTest(expression=expression), self.assertRaises((ValueError, SyntaxError)):
                polynomial(expression)


if __name__ == "__main__":
    unittest.main(verbosity=2)
