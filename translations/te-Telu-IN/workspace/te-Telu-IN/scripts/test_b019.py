"""Independent read-only B019 inventory, answer, asset, and renderer tests."""
import copy
from collections import Counter
from hashlib import sha256
import json
import re
import unittest
import xml.etree.ElementTree as ET

from build_unit import asset_map, localize, render, render_bridge, unit_inputs
from chapter_review_checks import (
    BASE, CN, MATH, XH, SVG, SOURCE_SHA256, GROUPS, EXERCISE_IDS, NOTATION,
    NOTATION_WORDS, MODELS, PROPERTIES, ADD_TOTALS, PHRASES, APPLICATIONS,
    PERIMETERS, EVERYDAY, CHARTS, MODEL_ASSETS, TARGET_SOLUTION_MARKERS, RELATION,
    _asset_by_suffix,
    _check_source_solution, _difference_relations, _expected_solution_numbers,
    _source_chart_blanks, _strong_texts, _validate_bridge_chart,
    _validate_chart_svg, _validate_column_table, _validate_model_svg,
    _validate_perimeter_svg, _validate_selfcheck_svg, checked_equality,
    column_steps, compact, displayed_equalities, ids_of, math_signature, number,
    numbers, source_cases, structure, text_of, validate_assets, validate_b019,
    validate_review_bridge, validate_review_target)
from inspect_source import slots


def replace_text(node, before, after, all_occurrences=False):
    changed = 0
    for item in node.iter():
        for field in ("text", "tail"):
            value = getattr(item, field)
            if value and before in value:
                setattr(item, field, value.replace(before, after,
                                                    -1 if all_occurrences else 1))
                changed += 1
                if not all_occurrences:
                    return
    assert changed, "B019 test fixture did not mutate: " + before


def wrong_result(expression):
    match = re.search(r"([0-9][0-9,]*)$", expression)
    assert match
    changed = f"{number(match.group(1)) + 1:,}"
    return expression[:match.start()] + changed


def mutate_last_numeric(node):
    candidates = []
    pattern = re.compile(r"(?<![0-9])([0-9][0-9,]*)(?![0-9])")
    for item in node.iter():
        for field in ("text", "tail"):
            value = getattr(item, field)
            if value:
                candidates.extend((item, field, value, match) for match in pattern.finditer(value))
    assert candidates, "B019 test fixture has no displayed numeric token"
    item, field, value, match = candidates[-1]
    changed = f"{number(match.group(1)) + 1:,}"
    setattr(item, field, value[:match.start(1)] + changed + value[match.end(1):])


def chart_root(by_suffix, suffix):
    return ET.parse(BASE / by_suffix[suffix]["localized_path"]).getroot()


class SourceInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source, cls.cases = source_cases()
        cls.ids = ids_of(cls.source)

    def test_exact_frozen_source_inventory(self):
        raw = (BASE / "sources/TE-B019.en.cnxml").read_bytes()
        self.assertEqual(sha256(raw).hexdigest(), SOURCE_SHA256)
        self.assertEqual((len(list(self.source.iter())), len(list(slots(self.source))),
                          len(self.ids), len(list(self.source.iter(CN + "exercise"))),
                          len(list(self.source.iter(CN + "solution"))),
                          len(list(self.source.iter(CN + "image")))),
                         (1017, 494, 366, 82, 42, 22))
        self.assertEqual(len(list(self.source.iter(MATH + "math"))), 135)

    def test_all_82_exercises_are_classified_once_in_source_order(self):
        self.assertEqual(tuple(case["id"] for case in self.cases), EXERCISE_IDS)
        self.assertEqual(Counter(case["kind"] for case in self.cases),
                         Counter({name: len(members) for name, members in GROUPS.items()}))
        self.assertEqual(sum(case["solution_id"] is not None for case in self.cases), 42)
        self.assertEqual(sum(case["solution_id"] is None for case in self.cases), 40)

    def test_every_fixed_numeric_answer_is_recomputed(self):
        for case in self.cases:
            with self.subTest(exercise=case["id"], kind=case["kind"]):
                if case["kind"] == "model":
                    self.assertEqual(sum(case["operands"]), case["total"])
                elif case["kind"] == "property":
                    self.assertEqual([sum(pair) for pair in case["pairs"]],
                                     [case["total"], case["total"]])
                elif case["kind"] in {"add", "phrase", "application", "everyday"}:
                    self.assertEqual(sum(case["operands"]), case["total"])
                elif case["kind"] == "perimeter":
                    self.assertEqual(sum(case["edges"]), case["total"])

    def test_all_24_direct_addition_answers_match_inventory(self):
        self.assertEqual({case["id"]: case["total"] for case in self.cases
                          if case["kind"] == "add"}, ADD_TOTALS)
        self.assertEqual(list(ADD_TOTALS.values()),
                         [78, 59, 99, 96, 85, 55, 142, 131, 493, 396, 861, 823,
                          1031, 1144, 6850, 9762, 22333, 22108, 1104860, 1226200,
                          29191, 34335, 101531, 89033])

    def test_all_12_phrase_answers_preserve_requested_operand_direction(self):
        for case in (case for case in self.cases if case["kind"] == "phrase"):
            expected = PHRASES[case["id"]]
            self.assertEqual(case["operands"], expected[:2])
            self.assertEqual(case["total"], expected[2])
        self.assertEqual(PHRASES["fs-id1834317"], (70, 38, 108))
        self.assertEqual(PHRASES["fs-id1159676"], (682, 2719, 3401))

    def test_properties_require_both_ordered_parts(self):
        for ident, pairs in PROPERTIES.items():
            with self.subTest(exercise=ident):
                self.assertEqual(len(pairs), 2)
                self.assertEqual(pairs[0], tuple(reversed(pairs[1])))
                self.assertEqual(sum(pairs[0]), sum(pairs[1]))

    def test_notation_is_reading_and_result_name_not_evaluation(self):
        self.assertEqual(len(NOTATION), len(NOTATION_WORDS), 6)
        for case in self.cases[:6]:
            self.assertEqual(case["kind"], "notation")
            self.assertNotIn("total", case)

    def test_application_units_and_incidental_numbers_are_not_addends(self):
        for ident, (values, total, unit, incidental) in APPLICATIONS.items():
            with self.subTest(exercise=ident):
                self.assertEqual(sum(values), total)
                self.assertTrue(all(value not in values for value in incidental))
                self.assertIn(unit, {"USD", "miles", "arrangements", "square feet", "pounds"})
        self.assertEqual(APPLICATIONS["fs-id2609576"][-1], (7,))
        self.assertEqual(APPLICATIONS["fs-id1410524"][-1], (3,))

    def test_everyday_comparisons_use_totals_not_incidental_thresholds(self):
        self.assertEqual(EVERYDAY["fs-id1567863"],
                         ((82, 91, 75, 88, 70), 406, "points", (400,), (">=", 400)))
        self.assertEqual(EVERYDAY["fs-id1369108"],
                         ((210, 145, 183, 230, 159, 164), 1091, "pounds", (1150,), ("<", 1150)))
        self.assertEqual(406 - 400, 6)
        self.assertEqual(1150 - 1091, 59)

    def test_all_eight_perimeters_and_figure215_derived_side(self):
        self.assertEqual([item[1] for item in PERIMETERS.values()],
                         [44, 30, 56, 66, 71, 87, 62, 70])
        edges, total, unit, _, visible = PERIMETERS["fs-id1960065"]
        self.assertEqual((visible, 10 - 7, 25 - 14, edges, total, unit),
                         ((25, 10, 14, 7, 11), 3, 11,
                          (25, 10, 14, 7, 11, 3), 70, "in"))

    def test_chart_ranges_and_all_175_problem_blanks(self):
        self.assertEqual([spec["blank"] for spec in CHARTS.values()], [39, 39, 28, 28, 25, 16])
        self.assertEqual(sum(spec["blank"] for spec in CHARTS.values()), 175)
        self.assertEqual((CHARTS["fs-id1516426"]["rows"],
                          CHARTS["fs-id1516426"]["cols"]),
                         (tuple(range(3, 10)), tuple(range(6, 10))))
        for case in (case for case in self.cases if case["kind"] == "chart"):
            self.assertEqual(len(case["formula_cells"]),
                             len(case["chart"]["rows"]) * len(case["chart"]["cols"]))
            self.assertEqual(len(case["blank_cells"]), case["chart"]["blank"])

    def test_partial_charts216_and218_each_have_39_not_early_manual_counts(self):
        for ident in ("fs-id2190914", "fs-id1485179"):
            case = next(item for item in self.cases if item["id"] == ident)
            media = self.ids[case["problem_id"]].find(CN + "media")
            self.assertEqual(len(_source_chart_blanks(media, case["chart"])), 39)

    def test_frozen_figure222_alt_defect_is_not_silently_rewritten(self):
        alt = self.ids["fs-id2263429"].get("alt")
        self.assertIn("8 columns and 5 rows", alt)
        self.assertEqual(len(CHARTS["fs-id1516426"]["cols"]), 4)
        self.assertEqual(len(CHARTS["fs-id1516426"]["rows"]), 7)

    def test_all_42_source_supplied_solutions_reconcile(self):
        for case in (case for case in self.cases if case["solution_id"]):
            with self.subTest(exercise=case["id"]):
                _check_source_solution(case, self.ids[case["solution_id"]])

    def test_each_source_solution_corruption_is_rejected(self):
        for case in (case for case in self.cases if case["solution_id"]):
            with self.subTest(exercise=case["id"], kind=case["kind"]):
                solution = copy.deepcopy(self.ids[case["solution_id"]])
                if case["kind"] == "notation":
                    replace_text(solution, "plus", "minus")
                elif case["kind"] == "chart":
                    image = solution.find(".//" + CN + "image")
                    image.set("src", image.get("src").replace(".jpg", "-wrong.jpg"))
                elif case["kind"] == "open":
                    replace_text(solution, "Answers will vary", "Only one answer is correct")
                else:
                    mutate_last_numeric(solution)
                with self.assertRaises(AssertionError):
                    _check_source_solution(case, solution)

    def test_column_algorithm_handles_zero_digits_and_carries_above_one(self):
        self.assertEqual([row[4] for row in column_steps((71, 28))], [9, 9])
        self.assertEqual([row[4] for row in column_steps((92, 39))], [1, 3, 1])
        rows = column_steps((28925, 817, 4593))
        self.assertEqual([row[5] for row in rows], [1, 1, 2, 1, 0])
        self.assertEqual(sum(row[0] * row[4] for row in rows), 34335)

    def test_column_algorithm_rejects_bankers_rounding_style_or_nonwhole_inputs(self):
        for bad in ((1,), (-1, 2), (True, 2), (1.5, 2)):
            with self.subTest(values=bad), self.assertRaises(AssertionError):
                column_steps(bad)

    def test_indonesian_reference_preserves_exact_ids_and_math(self):
        module = ET.parse(BASE.parent / "downloads/openstax-prealgebra-2e-id-ID/modules/m81244/index.cnxml").getroot()
        reference = ids_of(module)["fs-id2263283"]
        self.assertEqual(list(ids_of(reference)), list(ids_of(self.source)))
        def language_neutral(root):
            return [(node.tag, tuple(sorted(node.attrib.items())),
                     "<localized-mtext>" if node.tag == MATH + "mtext" else (node.text or "").strip(),
                     len(node)) for node in root.iter() if node.tag.startswith(MATH)]
        self.assertEqual(language_neutral(reference), language_neutral(self.source))

    def test_source_validation_is_read_only(self):
        before = ET.tostring(self.source)
        source_cases()
        self.assertEqual(ET.tostring(self.source), before)


class AssetSemanticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source, cls.cases = source_cases()
        cls.manifest = __import__("json").loads(
            (BASE / "assets/B019/manifest.json").read_text(encoding="utf-8"))
        cls.by_suffix = _asset_by_suffix(cls.manifest)

    def test_final_22_asset_set_and_machine_readable_counts(self):
        self.assertEqual(validate_assets(), {
            "localized_assets": 22, "model_assets": 4, "chart_assets": 9,
            "perimeter_assets": 8, "selfcheck_assets": 1, "chart_blank_cells": 175})

    def test_every_visible_chart_formula_cell_rejects_wrong_sum(self):
        checks = []
        for case in (case for case in self.cases if case["kind"] == "chart"):
            spec = case["chart"]
            checks.append((spec["problem"], spec["rows"], spec["cols"], case["blank_cells"]))
            if spec["solution"]:
                checks.append((spec["solution"], spec["rows"], spec["cols"], set()))
        tested = 0
        for suffix, rows, cols, blanks in checks:
            original = chart_root(self.by_suffix, suffix)
            visible = [node for node in original.iter(SVG + "g")
                       if node.get("data-role") == "table-cell" and
                       node.get("data-header") != "true" and node.get("data-blank") == "false"]
            for index in range(len(visible)):
                with self.subTest(asset=suffix, cell=index):
                    root = copy.deepcopy(original)
                    cells = [node for node in root.iter(SVG + "g")
                             if node.get("data-role") == "table-cell" and
                             node.get("data-header") != "true" and
                             node.get("data-blank") == "false"]
                    value = next(node for node in cells[index].iter(SVG + "text")
                                 if node.get("data-role") == "cell-value")
                    value.text = str(int(value.text) + 1)
                    with self.assertRaisesRegex(AssertionError, "visible addition-table sum"):
                        _validate_chart_svg(root, rows, cols, blanks)
                    tested += 1
        self.assertEqual(tested, 275)

    def test_partial_chart_blank_coordinates_cannot_move_at_same_sum(self):
        tested = 0
        for case in (case for case in self.cases if case["kind"] == "chart" and
                     0 < len(case["blank_cells"]) < len(case["formula_cells"])):
            spec = case["chart"]
            root = chart_root(self.by_suffix, spec["problem"])
            body = [node for node in root.iter(SVG + "g")
                    if node.get("data-role") == "table-cell" and
                    node.get("data-header") != "true"]
            blank = next(node for node in body if node.get("data-blank") == "true" and
                         any(other.get("data-blank") == "false" and
                             int(other.get("data-row-value")) + int(other.get("data-col-value")) ==
                             int(node.get("data-row-value")) + int(node.get("data-col-value"))
                             for other in body))
            visible = next(node for node in body if node.get("data-blank") == "false" and
                           int(node.get("data-row-value")) + int(node.get("data-col-value")) ==
                           int(blank.get("data-row-value")) + int(blank.get("data-col-value")))
            value = next(visible.iter(SVG + "text"))
            visible.remove(value)
            blank.append(value)
            blank.set("data-blank", "false")
            visible.set("data-blank", "true")
            with self.subTest(asset=spec["problem"]), self.assertRaisesRegex(
                    AssertionError, "blank coordinates"):
                _validate_chart_svg(root, spec["rows"], spec["cols"], case["blank_cells"])
            tested += 1
        self.assertEqual(tested, 2)

    def test_figure222_true_five_by_eight_orientation_cannot_transpose(self):
        root = chart_root(self.by_suffix, "222")
        body = next(node for node in root.iter(SVG + "g")
                    if node.get("data-role") == "table-cell" and
                    node.get("data-header") != "true")
        body.set("data-grid-col", "2")
        with self.assertRaises(AssertionError):
            _validate_chart_svg(root, tuple(range(3, 10)), tuple(range(6, 10)),
                                set((r, c) for r in range(3, 10) for c in range(6, 10)))

    def test_each_model_group_count_corruption_is_rejected(self):
        for suffix, expected in MODEL_ASSETS.items():
            original = chart_root(self.by_suffix, suffix)
            groups = [node for node in original.iter(SVG + "g")
                      if node.get("data-role") == "model-group"]
            for index in range(len(groups)):
                with self.subTest(asset=suffix, group=index):
                    root = copy.deepcopy(original)
                    group = [node for node in root.iter(SVG + "g")
                             if node.get("data-role") == "model-group"][index]
                    group.set("data-count", str(int(group.get("data-count")) + 1))
                    with self.assertRaisesRegex(AssertionError, "kind/count"):
                        _validate_model_svg(root, expected,
                            self.by_suffix[suffix]["math_checks"]["modeled_value"],
                            self.by_suffix[suffix]["math_checks"]["expression"])

    def test_model_problem_asset_cannot_leak_equation_answer(self):
        suffix = "201_img"
        root = chart_root(self.by_suffix, suffix)
        answer = ET.SubElement(root, SVG + "text")
        answer.text = self.by_suffix[suffix]["math_checks"]["expression"] + "=6"
        with self.assertRaisesRegex(AssertionError, "cannot print"):
            _validate_model_svg(root, MODEL_ASSETS[suffix], 6,
                                self.by_suffix[suffix]["math_checks"]["expression"])

    def test_model_group_contribution_cannot_change_while_count_stays_same(self):
        suffix = "203_img"
        root = chart_root(self.by_suffix, suffix)
        group = next(node for node in root.iter(SVG + "g")
                     if node.get("data-role") == "model-group")
        group.set("data-value", str(int(group.get("data-value")) + 1))
        with self.assertRaisesRegex(AssertionError, "contribution"):
            _validate_model_svg(root, MODEL_ASSETS[suffix], 12,
                                self.by_suffix[suffix]["math_checks"]["expression"])

    def test_every_perimeter_visible_label_and_unit_corruption_is_rejected(self):
        for _, (edges, total, unit, suffix, visible) in PERIMETERS.items():
            original = chart_root(self.by_suffix, suffix)
            labels = [node for node in original.iter(SVG + "text")
                      if node.get("data-role") == "side-label"]
            for index in range(len(labels)):
                with self.subTest(asset=suffix, label=index):
                    root = copy.deepcopy(original)
                    label = [node for node in root.iter(SVG + "text")
                             if node.get("data-role") == "side-label"][index]
                    label.text = re.sub(r"^[0-9]+", lambda m: str(int(m.group()) + 1), label.text)
                    with self.assertRaisesRegex(AssertionError, "side labels/order"):
                        _validate_perimeter_svg(root, edges, total, unit, visible, suffix)

    def test_figure215_cannot_reveal_derived_three_or_answer70(self):
        for leak in ("3 in", "70 in"):
            with self.subTest(leak=leak):
                root = chart_root(self.by_suffix, "215_img")
                node = ET.SubElement(root, SVG + "text")
                node.text = leak
                with self.assertRaisesRegex(AssertionError, "leaked"):
                    _validate_perimeter_svg(root, (25, 10, 14, 7, 11, 3), 70,
                                            "in", (25, 10, 14, 7, 11), "215_img")

    def test_selfcheck_cannot_preselect_a_response(self):
        root = chart_root(self.by_suffix, "AppB_002_A")
        response = next(node for node in root.iter(SVG + "g")
                        if node.get("data-response") == "true")
        ET.SubElement(response, SVG + "text").text = "✓"
        with self.assertRaisesRegex(AssertionError, "cannot preselect"):
            _validate_selfcheck_svg(root)


class ActualTargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source, cls.meta, cls.catalog = unit_inputs("TE-B019")
        cls.assets = asset_map("TE-B019")
        cls.target_base = localize(cls.source, cls.catalog, cls.assets)
        cls.bridge_base = ET.parse(BASE / "translations/TE-B019.bridge.xhtml").getroot()
        _, cls.cases = source_cases()

    def setUp(self):
        self.target = copy.deepcopy(self.target_base)

    def test_actual_final_target_and_combined_export(self):
        self.assertEqual(validate_review_target(self.target), {
            "source_exercises": 82, "provided_solution_nodes": 42,
            "fixed_exercises": 80, "open_writing_exercises": 2,
            "chart_blank_cells": 175, "source_images": 22})
        result = validate_b019(self.target, copy.deepcopy(self.bridge_base))
        self.assertEqual((result["bridge_solution_details"], result["bridge_chart_formula_cells"],
                          result["bridge_carry_rows"]), (82, 297, 173))

    def test_target_preserves_complete_structure_ids_and_math(self):
        self.assertEqual(structure(self.source), structure(self.target))
        self.assertEqual(math_signature(self.source), math_signature(self.target, target=True))
        self.assertEqual(len(ids_of(self.target)), 366)

    def test_all_six_scoped_math_prose_tokens_are_exact(self):
        values = [(node.text or "").strip() for node in self.target.iter(MATH + "mtext")]
        self.assertEqual(Counter(value for value in values if value in
                                 {"16 ఔన్సుల", "12 ఔన్సుల", "మరియు"}),
                         Counter({"16 ఔన్సుల": 2, "12 ఔన్సుల": 2, "మరియు": 2}))
        for token in ("16 ఔన్సుల", "12 ఔన్సుల", "మరియు"):
            with self.subTest(token=token):
                target = copy.deepcopy(self.target)
                next(node for node in target.iter(MATH + "mtext")
                     if (node.text or "").strip() == token).text = token + " తప్పు"
                with self.assertRaisesRegex(AssertionError, "MathML"):
                    validate_review_target(target)

    def test_each_numeric_source_answer_rejects_changed_displayed_number(self):
        numeric = [case for case in self.cases if case["solution_id"] and
                   case["kind"] not in {"notation", "chart", "open"}]
        self.assertEqual(len(numeric), 35)
        for case in numeric:
            with self.subTest(exercise=case["id"]):
                target = copy.deepcopy(self.target)
                solution = ids_of(target)[case["solution_id"]]
                mutate_last_numeric(solution)
                with self.assertRaises(AssertionError):
                    validate_review_target(target)

    def test_notation_word_answer_corruption_is_rejected(self):
        target = copy.deepcopy(self.target)
        replace_text(ids_of(target)["fs-id1179382"], "ఐదు ప్లస్ రెండు", "ఐదు మైనస్ రెండు")
        with self.assertRaisesRegex(AssertionError, "localized notation answer"):
            validate_review_target(target)

    def test_chart_solution_asset_corruption_is_rejected(self):
        target = copy.deepcopy(self.target)
        image = ids_of(target)["fs-id1795710"].find(".//" + CN + "image")
        image.set("src", image.get("src").replace("217", "225"))
        with self.assertRaises(AssertionError):
            validate_review_target(target)

    def test_open_answer_marker_remains_nonunique(self):
        target = copy.deepcopy(self.target)
        replace_text(ids_of(target)["fs-id1604802"], "వేర్వేరుగా", "ఒకేలా")
        with self.assertRaises(AssertionError):
            validate_review_target(target)

    def test_each_source_supplied_answer_unit_marker_is_checked(self):
        solution_by_exercise = {case["id"]: case["solution_id"] for case in self.cases}
        for ident, marker in TARGET_SOLUTION_MARKERS.items():
            with self.subTest(exercise=ident, marker=marker):
                target = copy.deepcopy(self.target)
                if marker.startswith("$"):
                    replacement = "₹" + marker[1:]
                else:
                    prefix = re.match(r"[0-9][0-9,]*", marker).group()
                    replacement = prefix + " తప్పు ప్రమాణం"
                replace_text(ids_of(target)[solution_by_exercise[ident]], marker, replacement)
                with self.assertRaisesRegex(AssertionError, "unit/context"):
                    validate_review_target(target)

    def test_target_figure222_alt_states_true_orientation_and_source_defect(self):
        target = copy.deepcopy(self.target)
        alt = ids_of(target)["fs-id2263429"]
        alt.set("alt", alt.get("alt").replace("5 నిలువు వరుసలు, 8 అడ్డ వరుసలు",
                                               "8 నిలువు వరుసలు, 5 అడ్డ వరుసలు"))
        with self.assertRaises(AssertionError):
            validate_review_target(target)

    def test_target_figure215_alt_cannot_leak_problem_answer(self):
        for leak in ("70", "3 అంగుళ"):
            with self.subTest(leak=leak):
                target = copy.deepcopy(self.target)
                media = ids_of(target)["fs-id2316211"]
                media.set("alt", media.get("alt") + " " + leak)
                with self.assertRaises(AssertionError):
                    validate_review_target(target)

    def test_target_validation_is_read_only(self):
        before = ET.tostring(self.target)
        validate_review_target(self.target)
        self.assertEqual(ET.tostring(self.target), before)


class ActualBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source, _, catalog = unit_inputs("TE-B019")
        cls.target = localize(source, catalog, asset_map("TE-B019"))
        cls.bridge_base = ET.parse(BASE / "translations/TE-B019.bridge.xhtml").getroot()
        _, cls.cases = source_cases()

    def setUp(self):
        self.bridge = copy.deepcopy(self.bridge_base)

    def validate(self, bridge=None):
        return validate_review_bridge(self.target, self.bridge if bridge is None else bridge)

    def detail(self, ident, bridge=None):
        return ids_of(self.bridge if bridge is None else bridge)["B019-S-" + ident]

    def test_actual_bridge_complete_82_case_coverage(self):
        self.assertEqual(self.validate(), {
            "bridge_solution_details": 82, "source_supplied_details": 42,
            "editorial_completion_details": 40, "bridge_tables": 54,
            "bridge_chart_formula_cells": 297, "bridge_carry_rows": 173,
            "bridge_addition_equalities": 555, "bridge_difference_equalities": 4,
            "bridge_ids": 97, "bridge_links": 88})

    def test_each_detail_has_exact_source_backlink_and_classification(self):
        details = list(self.bridge.iter(XH + "details"))
        self.assertEqual([node.get("id") for node in details],
                         ["B019-S-" + ident for ident in EXERCISE_IDS])
        for case, detail in zip(self.cases, details):
            links = list(detail.iter(XH + "a"))
            self.assertEqual([node.get("href") for node in links], ["#" + case["id"]])
            expected = "మూలంలో ఇచ్చిన జవాబుకు" if case["solution_id"] else "మూలంలో లేని జవాబుకు"
            self.assertIn(expected, text_of(detail))

    def test_backlink_or_source_status_corruption_is_rejected(self):
        bridge = copy.deepcopy(self.bridge)
        detail = ids_of(bridge)["B019-S-fs-id2169300"]
        next(detail.iter(XH + "a")).set("href", "#fs-id1386835")
        with self.assertRaises(AssertionError):
            self.validate(bridge)
        bridge = copy.deepcopy(self.bridge)
        detail = ids_of(bridge)["B019-S-fs-id2169300"]
        replace_text(detail, "మూలంలో లేని జవాబుకు", "మూలంలో ఇచ్చిన జవాబుకు", True)
        with self.assertRaisesRegex(AssertionError, "classification"):
            self.validate(bridge)

    def test_each_of_555_actual_addition_equalities_rejects_wrong_result(self):
        relations = displayed_equalities(self.bridge)
        self.assertEqual(len(relations), 555)
        for index, relation in enumerate(relations):
            with self.subTest(occurrence=index, relation=relation), self.assertRaises(AssertionError):
                checked_equality(wrong_result(relation))

    def test_all_297_chart_cells_reject_actual_text_corruption(self):
        tested = 0
        for case in (case for case in self.cases if case["kind"] == "chart"):
            detail = self.detail(case["id"])
            table = next(detail.iter(XH + "table"))
            body_rows = table.findall(XH + "tbody/" + XH + "tr")
            for row_index, row in enumerate(body_rows):
                for col_index, cell in enumerate(list(row)[1:]):
                    with self.subTest(exercise=case["id"], row=row_index, col=col_index):
                        altered = copy.deepcopy(detail)
                        altered_cell = altered.findall(".//" + XH + "tbody/" + XH + "tr")[row_index][col_index + 1]
                        relation = compact(text_of(altered_cell))
                        replace_text(altered_cell, text_of(altered_cell), wrong_result(relation))
                        with self.assertRaises(AssertionError):
                            _validate_bridge_chart(altered, case["chart"])
                        tested += 1
        self.assertEqual(tested, 297)

    def test_chart_same_sum_but_wrong_row_column_order_is_rejected(self):
        case = next(case for case in self.cases if case["id"] == "fs-id1516426")
        detail = copy.deepcopy(self.detail(case["id"]))
        cell = detail.find(".//" + XH + "tbody/" + XH + "tr/" + XH + "td")
        replace_text(cell, "3+6=9", "6+3=9")
        with self.assertRaises(AssertionError):
            _validate_bridge_chart(detail, case["chart"])

    def test_every_place_table_row_rejects_wrong_written_digit(self):
        tested = 0
        for case in (case for case in self.cases
                     if case["kind"] in {"add", "phrase", "application", "everyday"}):
            detail = self.detail(case["id"])
            rows = detail.findall(".//" + XH + "tbody/" + XH + "tr")
            for index, row in enumerate(rows):
                with self.subTest(exercise=case["id"], row=index):
                    altered = copy.deepcopy(detail)
                    cell = altered.findall(".//" + XH + "tbody/" + XH + "tr")[index][2]
                    cell.text = str((int(text_of(cell)) + 1) % 10)
                    with self.assertRaises(AssertionError):
                        _validate_column_table(altered, case["operands"], case["total"])
                    tested += 1
        self.assertEqual(tested, 173)

    def test_every_place_table_row_rejects_wrong_carry_count(self):
        tested = 0
        for case in (case for case in self.cases
                     if case["kind"] in {"add", "phrase", "application", "everyday"}):
            detail = self.detail(case["id"])
            rows = detail.findall(".//" + XH + "tbody/" + XH + "tr")
            for index, row in enumerate(rows):
                with self.subTest(exercise=case["id"], row=index):
                    altered = copy.deepcopy(detail)
                    cell = altered.findall(".//" + XH + "tbody/" + XH + "tr")[index][3]
                    old = text_of(cell)
                    cell.text = "1 ప్రమాణం బదిలీ" if old == "బదిలీ లేదు" else old.replace(
                        old.split()[0], str(int(old.split()[0]) + 1), 1)
                    with self.assertRaises(AssertionError):
                        _validate_column_table(altered, case["operands"], case["total"])
                    tested += 1
        self.assertEqual(tested, 173)

    def test_target_place_corruption_fails_even_when_final_answer_is_same(self):
        case = next(case for case in self.cases if case["id"] == "fs-id1360696")
        detail = copy.deepcopy(self.detail(case["id"]))
        row = detail.find(".//" + XH + "tbody/" + XH + "tr")
        row[0].text = "పదులు"
        with self.assertRaises(AssertionError):
            _validate_column_table(detail, case["operands"], case["total"])

    def test_valid_same_total_but_wrong_phrase_operand_order_is_rejected(self):
        case = next(case for case in self.cases if case["id"] == "fs-id2387977")
        detail = copy.deepcopy(self.detail(case["id"]))
        strong = next(node for node in detail.iter(XH + "strong") if "13+18=31" in text_of(node))
        replace_text(strong, "13+18=31", "18+13=31")
        with self.assertRaises(AssertionError):
            _validate_column_table(detail, case["operands"], case["total"])

    def test_incidental_square_foot_count_cannot_become_an_addend(self):
        bridge = copy.deepcopy(self.bridge)
        detail = ids_of(bridge)["B019-S-fs-id2609576"]
        old = "238+120+156+196+100+132+225=1,167"
        new = "231+120+156+196+100+132+225+7=1,167"
        replace_text(detail, old, new, True)
        with self.assertRaises(AssertionError):
            self.validate(bridge)

    def test_units_and_currency_cannot_change_with_same_number(self):
        replacements = [
            ("fs-id2452678", "$402", "402 పౌండ్లు"),
            ("fs-id2264366", "138 మైళ్లు (miles)", "138 కిలోమీటర్లు (kilometers)"),
            ("fs-id2609576", "1,167 చదరపు అడుగులు (square feet)", "1,167 అడుగులు (feet)"),
            ("fs-id2658194", "44 అంగుళాలు (inches)", "44 చదరపు అంగుళాలు (square inches)"),
            ("fs-id1567863", "పరీక్షల పాయింట్ల మొత్తం", "పరీక్షల శాతం మొత్తం"),
            ("fs-id1369108", "వచ్చినది 1,091 పౌండ్లు", "వచ్చినది 1,091 కిలోగ్రాములు"),
        ]
        for ident, old, new in replacements:
            with self.subTest(exercise=ident):
                bridge = copy.deepcopy(self.bridge)
                replace_text(ids_of(bridge)["B019-S-" + ident], old, new, True)
                with self.assertRaises(AssertionError):
                    self.validate(bridge)

    def test_figure215_requires_derived_three_and_perimeter70(self):
        for old, new in (("10−7=3", "10−7=4"),
                         ("25+10+14+7+11+3=70", "25+10+14+7+11+3=71")):
            with self.subTest(old=old):
                bridge = copy.deepcopy(self.bridge)
                replace_text(ids_of(bridge)["B019-S-fs-id1960065"], old, new, True)
                with self.assertRaises(AssertionError):
                    self.validate(bridge)

    def test_notation_cannot_gain_an_unasked_evaluated_answer(self):
        bridge = copy.deepcopy(self.bridge)
        detail = ids_of(bridge)["B019-S-fs-id1386835"]
        ET.SubElement(detail, XH + "p").text = "5+2=7"
        with self.assertRaisesRegex(AssertionError, "cannot become evaluated"):
            self.validate(bridge)

    def test_open_writing_remains_acceptance_rubric_not_autograded(self):
        bridge = copy.deepcopy(self.bridge)
        detail = ids_of(bridge)["B019-S-fs-id1408863"]
        replace_text(detail, "ఒకే సరైన వాక్యం లేదు", "ఒకే సరైన సంఖ్య ఉంది", True)
        with self.assertRaisesRegex(AssertionError, "acceptance rubric"):
            self.validate(bridge)

    def test_second_open_rubric_may_show_model_example_but_not_fixed_response(self):
        detail = self.detail("fs-id1827602")
        self.assertIn("ఒకే సరైన వాక్యం లేదు", text_of(detail))
        self.assertEqual(displayed_equalities(detail), ["8+4=12"])

    def test_exact_b016_route_fragment_regression(self):
        routing = ids_of(self.bridge)["B019-routing"]
        links = {text_of(node): node.get("href") for node in routing.iter(XH + "a")}
        self.assertEqual(links["B016"], "TE-B016.html#fs-id2691382")
        bridge = copy.deepcopy(self.bridge)
        node = next(node for node in ids_of(bridge)["B019-routing"].iter(XH + "a")
                    if text_of(node) == "B016")
        node.set("href", "TE-B016.html#fs-id1611455")
        with self.assertRaises(AssertionError):
            self.validate(bridge)

    def test_all_four_difference_occurrences_are_exact(self):
        self.assertEqual(Counter(_difference_relations(self.bridge)), Counter({
            "10−7=3": 2, "406−400=6": 1, "1,150−1,091=59": 1}))

    def test_bridge_validation_is_read_only(self):
        before = ET.tostring(self.bridge)
        self.validate()
        self.assertEqual(ET.tostring(self.bridge), before)


class ActualRendererTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source, _, cls.catalog = unit_inputs("TE-B019")
        cls.assets = asset_map("TE-B019")
        cls.target = localize(cls.source, cls.catalog, cls.assets)
        cls.bridge = ET.parse(BASE / "translations/TE-B019.bridge.xhtml").getroot()

    def rendered(self, english=False):
        root = self.source if english else self.target
        return ET.fromstring("<div>" + render(root, self.assets,
            "en-" if english else "", english, collapse_solutions=True) + "</div>")

    def test_all_366_source_ids_render_in_both_columns(self):
        for english in (False, True):
            with self.subTest(english=english):
                root = self.rendered(english)
                prefix = "en-" if english else ""
                expected = {prefix + ident for ident in ids_of(self.source)}
                actual = {node.get("id") for node in root.iter() if node.get("id")}
                self.assertEqual(actual, expected)

    def test_all_22_media_render_with_correct_language_asset(self):
        for english in (False, True):
            with self.subTest(english=english):
                root = self.rendered(english)
                images = list(root.iter("img"))
                self.assertEqual(len(images), 22)
                expected = {"../" + asset["original_path" if english else "localized_path"]
                            for asset in self.assets.values()}
                self.assertEqual({node.get("src") for node in images}, expected)
                self.assertTrue(all(node.get("alt") for node in images))

    def test_figure222_renderer_keeps_source_and_corrected_target_distinct(self):
        te = self.rendered(False)
        en = self.rendered(True)
        te_alt = next(ids_of(te)["fs-id2263429"].iter("img")).get("alt")
        en_alt = next(ids_of(en)["en-fs-id2263429"].iter("img")).get("alt")
        self.assertIn("5 నిలువు వరుసలు, 8 అడ్డ వరుసలు", te_alt)
        self.assertIn("8 columns and 5 rows", en_alt)

    def test_all_42_source_answers_render_collapsed_in_both_columns(self):
        for english in (False, True):
            root = self.rendered(english)
            details = [node for node in root.iter("details")
                       if node.get("class") == "cn-solution"]
            self.assertEqual(len(details), 42)
            self.assertTrue(all(next(iter(node)).tag == "summary" for node in details))

    def test_bridge_render_preserves_97_ids_88_links_and54_scrollable_tables(self):
        before = ET.tostring(self.bridge)
        root = ET.fromstring(render_bridge(self.bridge))
        self.assertEqual((len(ids_of(root)), len(list(root.iter("a"))),
                          len(list(root.iter("table")))), (97, 88, 54))
        wrappers = [node for node in root.iter("div") if node.get("class") == "table-scroll"]
        self.assertEqual(len(wrappers), 54)
        self.assertTrue(all(node.get("tabindex") == "0" and node.get("role") == "region"
                            for node in wrappers))
        for table in root.iter("table"):
            self.assertTrue(all(node.get("scope") == "col"
                                for node in table.findall("thead/tr/th")))
            self.assertTrue(all(node.get("scope") == "row"
                                for node in table.findall("tbody/tr/th")))
        self.assertEqual(ET.tostring(self.bridge), before)

    def test_rendered_scoped_math_tokens_remain_exact(self):
        target = self.rendered(False)
        values = [(node.text or "").strip() for node in target.iter(MATH + "mtext")]
        self.assertEqual(Counter(value for value in values if value in
                                 {"16 ఔన్సుల", "12 ఔన్సుల", "మరియు"}),
                         Counter({"16 ఔన్సుల": 2, "12 ఔన్సుల": 2, "మరియు": 2}))

    def test_visual_copy_corrections_remain_readable_and_source_consistent(self):
        text = text_of(self.bridge)
        required = [
            "సున్నను 13కు", "కలిపినా 13", "సున్నను 5,280కు", "కలిపినా 5,280",
            "8, 3 క్రమాలను", "మొత్తం 11", "7, 5 క్రమాలను", "మొత్తం 12",
            "628, 77ల మొత్తం", "593, 79ల మొత్తం", "915కు 1,482",
            "682కు 2,719", "ఏడుగురు పురుషుల బరువులు",
        ]
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
        forbidden = [
            "సున్నను13కు", "కలిపినా13", "సున్నను5,280కు", "కలిపినా5,280",
            "మొత్తం11", "మొత్తం12", "628,77ల", "593,79ల", "915కు1,482",
            "682కు2,719", "జంతువుల బరువులు",
        ]
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, text)


class GeneratedArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.target_path = BASE / "generated/TE-B019.te.cnxml"
        cls.reader_path = BASE / "reader/TE-B019.html"
        cls.receipt = json.loads((BASE / "qa/TE-B019.build.json").read_text(encoding="utf-8"))

    def test_generated_target_passes_complete_actual_validator(self):
        target = ET.parse(self.target_path).getroot()
        bridge = ET.parse(BASE / "translations/TE-B019.bridge.xhtml").getroot()
        result = validate_b019(target, bridge)
        self.assertEqual((result["source_exercises"], result["provided_solution_nodes"],
                          result["bridge_addition_equalities"],
                          result["bridge_difference_equalities"]), (82, 42, 555, 4))

    def test_build_receipt_hashes_are_actual_bytes(self):
        self.assertEqual(self.receipt["source_sha256"], SOURCE_SHA256)
        self.assertEqual(self.receipt["target_sha256"],
                         sha256(self.target_path.read_bytes()).hexdigest())
        self.assertEqual(self.receipt["reader_sha256"],
                         sha256(self.reader_path.read_bytes()).hexdigest())
        self.assertEqual((self.receipt["source_elements"], self.receipt["source_ids"],
                          self.receipt["math_expressions"], self.receipt["localized_images"]),
                         (1017, 366, 135, 22))


if __name__ == "__main__":
    unittest.main()
