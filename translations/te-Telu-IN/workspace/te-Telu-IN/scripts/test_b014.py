"""Read-only B014 arithmetic/model and actual-text corruption regressions."""
import copy
import re
import unittest
import xml.etree.ElementTree as ET

from addition_model_checks import (BASE, CN, MATH, XH, SVG, PREFIX, MODELS, ALT_CHECKS,
    EXERCISES, TRY_CASES, EXTRA_CASES, regroup, source_cases, model_counts,
    displayed_equalities, validate_model_target, validate_b014, RELATION, EN_NUMBERS)


class SourceModelTests(unittest.TestCase):
    def svg(self, suffix):
        return ET.parse(BASE / ("assets/B014/" + PREFIX + suffix + ".te.svg")).getroot()

    def test_actual_source_inventory_and_answers(self):
        from inspect_source import slots
        source, cases = source_cases()
        self.assertEqual(len(list(slots(source))), 171)
        self.assertEqual([c[3] for c in cases], [8, 9, 6, 13, 12, 14, 43, 42, 45])
        self.assertEqual(len(TRY_CASES), 6)
        self.assertEqual(len(set((c[1], c[2]) for c in cases) | {(3, 4)}), 10)

    def test_all_actual_svg_counts_and_visible_answers(self):
        values = [model_counts(self.svg(s), s) for s in MODELS]
        self.assertEqual(len(values), 19)
        self.assertEqual(values[10], {"before": 13, "after": 13})
        self.assertEqual(values[-4:], [{"single": 43}, {"single": 43}, {"single": 42}, {"single": 45}])

    def test_all_source_pairs_conserve_value(self):
        for _, _, a, b, _ in EXERCISES:
            with self.subTest(a=a, b=b):
                state = regroup(a, b)
                self.assertEqual(state["value"], a + b)
                self.assertEqual(state["after"][1], (a + b) % 10)
                self.assertEqual(state["before"][1] - state["after"][1], 10 * state["carry"])

    def test_six_regrouping_source_states(self):
        expected = [(5, 8, (0, 13), (1, 3)), (5, 7, (0, 12), (1, 2)),
                    (6, 8, (0, 14), (1, 4)), (17, 26, (3, 13), (4, 3)),
                    (15, 27, (3, 12), (4, 2)), (16, 29, (3, 15), (4, 5))]
        for a, b, before, after in expected:
            with self.subTest(pair=(a, b)):
                self.assertEqual(regroup(a, b)["before"], before)
                self.assertEqual(regroup(a, b)["after"], after)

    def test_exact_ten_boundary_and_zero(self):
        self.assertEqual(regroup(7, 3)["after"], (1, 0))
        self.assertEqual(regroup(27, 13)["after"], (4, 0))
        self.assertEqual(regroup(4, 0)["after"], (0, 4))
        self.assertEqual(regroup(4, 5)["carry"], 0)
        self.assertEqual(regroup(4, 6)["carry"], 1)
        self.assertEqual(regroup(0, 0)["value"], 0)

    def test_invalid_nonwhole_or_negative_inputs_rejected(self):
        for pair in [(1.0, 2), (True, 4), (-1, 2), (3, 100)]:
            with self.subTest(pair=pair), self.assertRaises(AssertionError):
                regroup(*pair)

    def test_every_model_rejects_deleted_actual_cell(self):
        for suffix in MODELS:
            with self.subTest(suffix=suffix):
                svg = self.svg(suffix)
                group = next(svg.iter(SVG + "g"))
                group.remove(group[-1])
                with self.assertRaises(AssertionError):
                    model_counts(svg, suffix)

    def test_changed_actual_cells_cannot_hide_behind_changed_metadata(self):
        svg = self.svg("019_img-03")
        groups = list(svg.iter(SVG + "g"))
        groups[0].remove(groups[0][-1])
        groups[0].set("data-count", "2")
        cell = copy.deepcopy(groups[1][-1]); cell.set("x", str(float(cell.get("x")) + 32))
        groups[1].append(cell); groups[1].set("data-count", "5")
        self.assertEqual(sum(len(g) for g in groups), 7)
        with self.assertRaisesRegex(AssertionError, "counts/states"):
            model_counts(svg, "019_img-03")

    def test_correct_sum_does_not_allow_swapped_addend_groups(self):
        svg = self.svg("016_img-03")
        groups = list(svg.iter(SVG + "g"))
        svg.remove(groups[0]); svg.remove(groups[1])
        svg.append(groups[1]); svg.append(groups[0])
        with self.assertRaisesRegex(AssertionError, "counts/states"):
            model_counts(svg, "016_img-03")

    def test_rod_metadata_cannot_replace_cell_count(self):
        svg = self.svg("010_img")
        rod = next(g for g in svg.iter(SVG + "g") if g.get("data-kind") == "ten")
        rod.remove(rod[-1]); rod.set("data-count", "9")
        with self.assertRaisesRegex(AssertionError, "ten actual cells"):
            model_counts(svg, "010_img")

    def test_rod_cells_must_be_contiguous(self):
        svg = self.svg("018_img-02")
        cell = next(g for g in svg.iter(SVG + "g") if g.get("data-kind") == "ten")[-1]
        cell.set("x", str(float(cell.get("x")) + 4))
        with self.assertRaisesRegex(AssertionError, "contiguous"):
            model_counts(svg, "018_img-02")

    def test_duplicate_actual_cell_is_not_an_extra_unit(self):
        svg = self.svg("019_img-02")
        cells = next(svg.iter(SVG + "g"))
        cells[1].set("x", cells[0].get("x"))
        with self.assertRaisesRegex(AssertionError, "duplicate/overlapping"):
            model_counts(svg, "019_img-02")

    def test_exchange_stages_cannot_be_merged_into_twenty_six(self):
        svg = self.svg("017_img-04")
        for group in svg.iter(SVG + "g"):
            group.set("data-stage", "before")
        with self.assertRaisesRegex(AssertionError, "counts/states"):
            model_counts(svg, "017_img-04")

    def test_exchange_cannot_keep_thirteen_ones_and_add_rod(self):
        svg = self.svg("017_img-04")
        group = next(g for g in svg.iter(SVG + "g") if g.get("data-kind") == "ones" and g.get("data-stage") == "before")
        added = copy.deepcopy(group); added.set("data-stage", "after")
        svg.append(added)
        with self.assertRaisesRegex(AssertionError, "counts/states"):
            model_counts(svg, "017_img-04")

    def test_exchange_warning_is_not_optional(self):
        svg = self.svg("017_img-04")
        desc = svg.find(SVG + "desc")
        desc.text = desc.text.replace("do not add the two stages", "add the two stages")
        with self.assertRaisesRegex(AssertionError, "double-counting"):
            model_counts(svg, "017_img-04")

    def test_exchange_arrow_is_retained(self):
        svg = self.svg("017_img-04")
        svg.remove(next(e for e in svg if e.get("data-role") == "exchange-arrow"))
        with self.assertRaisesRegex(AssertionError, "arrow missing"):
            model_counts(svg, "017_img-04")

    def test_every_visible_equation_rejects_different_total(self):
        for suffix in ["006_img", "007_img", "010_img", "011_img", "014_img", "015_img"]:
            with self.subTest(suffix=suffix):
                svg = self.svg(suffix)
                text = next(svg.iter(SVG + "text"))
                text.text += "0"
                with self.assertRaisesRegex(AssertionError, "visible model"):
                    model_counts(svg, suffix)

    def test_same_total_different_visible_operands_rejected(self):
        svg = self.svg("014_img")
        next(svg.iter(SVG + "text")).text = "16 + 26 = 42"
        with self.assertRaisesRegex(AssertionError, "visible model"):
            model_counts(svg, "014_img")

    def test_cells_on_wrong_side_rejected(self):
        svg = self.svg("018_img-04")
        for group in svg.iter(SVG + "g"):
            for cell in group:
                offset = 600 if group.get("data-kind") == "ten" else 0
                cell.set("x", str(float(cell.get("x")) + offset))
        with self.assertRaisesRegex(AssertionError, "LEFT"):
            model_counts(svg, "018_img-04")

    def test_accessible_rod_count_cannot_be_replaced_by_contribution(self):
        svg = self.svg("018_img-04")
        desc = svg.find(SVG + "desc")
        desc.text = desc.text.replace("(tens rods) 3;", "(tens rods) 30;")
        with self.assertRaisesRegex(AssertionError, "accessible stage counts"):
            model_counts(svg, "018_img-04")

    def test_accessible_after_ones_cannot_keep_exchanged_ten(self):
        svg = self.svg("017_img-04")
        desc = svg.find(SVG + "desc")
        desc.text = desc.text.replace("(ones) 3.", "(ones) 13.")
        with self.assertRaisesRegex(AssertionError, "accessible stage counts"):
            model_counts(svg, "017_img-04")

    def test_accessible_equation_cannot_hide_behind_correct_visible_one(self):
        svg = self.svg("014_img")
        desc = svg.find(SVG + "desc")
        desc.text = desc.text.replace("15 + 27 = 42", "15 + 27 = 43")
        with self.assertRaisesRegex(AssertionError, "accessible numeric labels"):
            model_counts(svg, "014_img")

    def test_complete_equation_chains_recomputed(self):
        root = ET.fromstring('<section xmlns="http://www.w3.org/1999/xhtml"><p>3 × 10 + 13 = 30 + 13 = 43.</p><p>13 − 10 = 3.</p></section>')
        self.assertEqual(displayed_equalities(root), ["3×10+13=30+13=43", "13−10=3"])
        root[0].text = "3 × 10 + 13 = 43 = 53"
        with self.assertRaisesRegex(AssertionError, "Incorrect B014"):
            displayed_equalities(root)


class ModelTargetTests(unittest.TestCase):
    def setUp(self):
        from build_unit import asset_map, localize, unit_inputs
        self.source, self.meta, self.catalog = unit_inputs("TE-B014")
        self.target = localize(self.source, self.catalog, asset_map("TE-B014"))

    def node(self, root, ident):
        return next(e for e in root.iter() if e.get("id") == ident)

    def mutate(self, root, ident, before, after):
        pattern = r"\s*".join(re.escape(c) for c in re.sub(r"\s+", "", before))
        for node in self.node(root, ident).iter():
            for field in ("text", "tail"):
                value = getattr(node, field)
                if value and before in value:
                    setattr(node, field, value.replace(before, after, 1))
                    return
                if value and re.search(pattern, value):
                    setattr(node, field, re.sub(pattern, lambda _: after, value, count=1))
                    return
        self.fail("Mutation did not touch actual XML: " + before)

    def test_actual_target_preserves_all_source_math_and_ids(self):
        cases = validate_model_target(self.target)
        self.assertEqual(len(cases), 9)
        self.assertEqual(len(list(self.target.iter(MATH + "math"))), 30)
        self.assertEqual(len([e for e in self.target.iter() if e.get("id")]), 86)

    def test_all_nine_problem_operand_corruptions_rejected(self):
        for ident, _, a, b, _ in EXERCISES:
            with self.subTest(exercise=ident):
                target = copy.deepcopy(self.target)
                problem = self.node(target, ident).find(CN + "problem")
                next(problem.iter(MATH + "mn")).text = str(a + 1)
                with self.assertRaisesRegex(AssertionError, "MathML"):
                    validate_model_target(target)

    def test_same_sum_different_target_operands_rejected(self):
        problem = self.node(self.target, "fs-id2137714").find(CN + "problem")
        numbers = list(problem.iter(MATH + "mn"))
        numbers[0].text, numbers[1].text = "18", "24"
        self.assertEqual(sum(int(e.text) for e in numbers), 42)
        with self.assertRaisesRegex(AssertionError, "MathML"):
            validate_model_target(self.target)

    def test_operand_order_matters_even_when_sum_unchanged(self):
        problem = self.node(self.target, "fs-id1886370").find(CN + "problem")
        numbers = list(problem.iter(MATH + "mn"))
        numbers[0].text, numbers[1].text = "1", "5"
        with self.assertRaisesRegex(AssertionError, "MathML"):
            validate_model_target(self.target)

    def test_source_addition_operation_cannot_change(self):
        self.mutate(self.target, "fs-id1939376", "+", "−")
        with self.assertRaisesRegex(AssertionError, "MathML"):
            validate_model_target(self.target)

    def test_equal_sign_cannot_be_removed_from_source_equation(self):
        self.mutate(self.target, "fs-id1607848", "=", "+")
        with self.assertRaisesRegex(AssertionError, "MathML"):
            validate_model_target(self.target)

    def test_all_nine_original_solution_ids_are_preserved(self):
        for _, solution, _, _, _ in EXERCISES:
            with self.subTest(solution=solution):
                target = copy.deepcopy(self.target)
                self.node(target, solution).set("id", "changed-solution")
                with self.assertRaisesRegex(AssertionError, "structure"):
                    validate_model_target(target)

    def test_nonmathml_five_plus_eight_equation_is_protected(self):
        self.mutate(self.target, "eip-555", "5 + 8 = 13", "5 + 8 = 14")
        with self.assertRaisesRegex(AssertionError, "non-MathML"):
            validate_model_target(self.target)

    def test_nonmathml_same_total_wrong_pair_rejected(self):
        self.mutate(self.target, "eip-555", "5 + 8 = 13", "6 + 7 = 13")
        with self.assertRaisesRegex(AssertionError, "non-MathML"):
            validate_model_target(self.target)

    def test_source_table_defect_is_not_silently_rewritten(self):
        self.node(self.target, "eip-951").find(CN + "tgroup").set("cols", "2")
        with self.assertRaisesRegex(AssertionError, "structure"):
            validate_model_target(self.target)

    def test_two_digit_table_cannot_drop_final_equation_row(self):
        body = self.node(self.target, "eip-93").find(".//" + CN + "tbody")
        body.remove(body[-1])
        with self.assertRaisesRegex(AssertionError, "structure"):
            validate_model_target(self.target)

    def test_every_model_mapping_is_specific_to_its_source(self):
        for index in range(19):
            with self.subTest(image=index):
                target = copy.deepcopy(self.target)
                images = list(target.iter(CN + "image"))
                images[index].set("src", images[(index + 1) % 19].get("src"))
                with self.assertRaisesRegex(AssertionError, "image mapping"):
                    validate_model_target(target)

    def test_same_value_before_and_after_images_cannot_swap(self):
        before = self.node(self.target, "eip-id1168289744408").find(CN + "image")
        after = self.node(self.target, "eip-id1168289429860").find(CN + "image")
        before.set("src", after.get("src"))
        with self.assertRaisesRegex(AssertionError, "image mapping"):
            validate_model_target(self.target)

    def test_exact_ten_boundary_cannot_become_strictly_above_ten(self):
        self.mutate(self.target, "fs-id1825926", " లేదా అంతకంటే ఎక్కువైతే", " కంటే ఎక్కువైతే")
        with self.assertRaisesRegex(AssertionError, "inclusive-ten"):
            validate_model_target(self.target)

    def test_exchange_cannot_add_rod_without_removing_units(self):
        self.mutate(self.target, "fs-id1825926", "బ్లాకుల స్థానంలో", "బ్లాకులకు అదనంగా")
        with self.assertRaisesRegex(AssertionError, "inclusive-ten"):
            validate_model_target(self.target)

    def test_every_question_must_still_request_a_model(self):
        for ident, _, _, _, _ in EXERCISES:
            with self.subTest(exercise=ident):
                target = copy.deepcopy(self.target)
                self.mutate(target, ident, "నమూనాతో చూపండి", "విలువను కనుక్కోండి")
                with self.assertRaisesRegex(AssertionError, "modeling request"):
                    validate_model_target(target)

    def test_unit_block_value_cannot_be_ten(self):
        self.mutate(self.target, "fs-id1484984", "ఒక చిన్న బ్లాకు విలువ", "ఒక పదుల కడ్డీ విలువ")
        with self.assertRaisesRegex(AssertionError, "unit value"):
            validate_model_target(self.target)

    def test_worked_addend_roles_cannot_substitute_result(self):
        self.mutate(self.target, "fs-id1883656", "రెండు, ఆరు", "రెండు, ఎనిమిది")
        with self.assertRaisesRegex(AssertionError, "addend roles"):
            validate_model_target(self.target)

    def test_equation_definition_requires_equal_values(self):
        self.mutate(self.target, "fs-id1607848", "విలువలు సమానమని", "విలువలు వేరని")
        with self.assertRaisesRegex(AssertionError, "equation definition"):
            validate_model_target(self.target)

    def test_four_tens_is_not_forty_tens(self):
        self.mutate(self.target, "eip-93", "4పదులు,3ఒకట్లు", "40పదులు,3ఒకట్లు")
        with self.assertRaisesRegex(AssertionError, "stage counts"):
            validate_model_target(self.target)

    def test_correct_forty_three_does_not_allow_before_after_state_swap(self):
        self.mutate(self.target, "eip-93", "3పదులు,13ఒకట్లు", "4పదులు,3ఒకట్లు")
        self.assertEqual(3 * 10 + 13, 4 * 10 + 3)
        with self.assertRaisesRegex(AssertionError, "stage counts"):
            validate_model_target(self.target)

    def test_exchange_cannot_leave_thirteen_ones_afterward(self):
        self.mutate(self.target, "eip-93", "4పదులు,3ఒకట్లు", "4పదులు,13ఒకట్లు")
        with self.assertRaisesRegex(AssertionError, "stage counts"):
            validate_model_target(self.target)

    def test_one_ten_plus_three_ones_cannot_be_one_plus_three(self):
        self.mutate(self.target, "eip-555", "1పది,3ఒకట్లు", "1ఒకటి,3ఒకట్లు")
        with self.assertRaisesRegex(AssertionError, "regrouped model"):
            validate_model_target(self.target)

    def test_all_nineteen_alts_reject_wrong_actual_word_quantity(self):
        for index, suffix in enumerate(MODELS):
            with self.subTest(suffix=suffix):
                target = copy.deepcopy(self.target)
                media = list(target.iter(CN + "media"))[index]
                first_phrase = ALT_CHECKS[suffix][1][0]
                self.assertIn(first_phrase, media.get("alt"))
                media.set("alt", media.get("alt").replace(first_phrase, "తప్పు నమూనా", 1))
                with self.assertRaisesRegex(AssertionError, "target alt"):
                    validate_model_target(target)

    def test_alt_wrong_total_cannot_hide_behind_correct_source_image(self):
        media = self.node(self.target, "fs-id1546073")
        media.set("alt", media.get("alt").replace("15+27=42", "15+27=43"))
        with self.assertRaisesRegex(AssertionError, "alt numbers"):
            validate_model_target(self.target)

    def test_alt_same_total_other_source_pair_rejected(self):
        media = self.node(self.target, "fs-id1546073")
        media.set("alt", media.get("alt").replace("15+27=42", "18+24=42"))
        with self.assertRaisesRegex(AssertionError, "alt numbers"):
            validate_model_target(self.target)

    def test_known_english_alt_side_error_cannot_reappear(self):
        media = self.node(self.target, "eip-id1168289744408")
        media.set("alt", media.get("alt").replace("ఎడమవైపు", "కుడివైపు", 1))
        with self.assertRaisesRegex(AssertionError, "target alt model/side"):
            validate_model_target(self.target)

    def test_alt_before_and_after_cannot_be_counted_twice(self):
        media = self.node(self.target, "eip-id1168288217527")
        media.set("alt", media.get("alt").replace("కొత్త సమూహాలు కావు", "కొత్త సమూహాలు"))
        with self.assertRaisesRegex(AssertionError, "target alt"):
            validate_model_target(self.target)

    def test_all_four_table_accessible_dimensions_reject_corruption(self):
        for ident in ["eip-167", "eip-951", "eip-555", "eip-93"]:
            with self.subTest(table=ident):
                target = copy.deepcopy(self.target)
                table = self.node(target, ident)
                table.set("aria-label", table.get("aria-label").replace("అడ్డ వరుసలు", "నిలువు వరుసలు", 1))
                with self.assertRaisesRegex(AssertionError, "table dimensions"):
                    validate_model_target(target)

    def test_accessible_table_same_total_wrong_stage_rejected(self):
        table = self.node(self.target, "eip-93")
        before = table.get("aria-label")
        after = re.sub(r"3\s*పదులు,\s*13\s*ఒకట్లు", "4పదులు,3ఒకట్లు", before)
        self.assertNotEqual(before, after)
        table.set("aria-label", after)
        with self.assertRaisesRegex(AssertionError, "table quantities"):
            validate_model_target(self.target)


class ModelBridgeTests(unittest.TestCase):
    node = ModelTargetTests.node
    mutate = ModelTargetTests.mutate

    def setUp(self):
        ModelTargetTests.setUp(self)
        self.bridge = ET.parse(BASE / "translations/TE-B014.bridge.xhtml").getroot()

    def test_actual_bridge_full_math_and_answer_coverage(self):
        self.assertEqual(validate_b014(self.target, self.bridge), {
            "source_pairs": 10, "source_exercises": 9, "source_try_its": 6,
            "original_entry_rechecks": 6, "model_assets": 19,
            "original_solution_ids": 9, "bridge_solution_details": 12,
            "displayed_equation_chains": 43})

    def test_every_actual_equation_occurrence_rejects_incorrect_value(self):
        def occurrences(root):
            return [(node, field, match) for node in root.iter() for field in ("text", "tail")
                    for match in RELATION.finditer(getattr(node, field) or "")]
        self.assertEqual(len(occurrences(self.bridge)), 43)
        for index in range(43):
            with self.subTest(occurrence=index):
                bridge = copy.deepcopy(self.bridge)
                node, field, match = occurrences(bridge)[index]
                value = getattr(node, field)
                wrong = re.sub(r"\d+$", lambda m: str(int(m[0]) + 1), match[0])
                self.assertNotEqual(match[0], wrong)
                setattr(node, field, value[:match.start()] + wrong + value[match.end():])
                with self.assertRaisesRegex(AssertionError, "Incorrect B014 displayed equality"):
                    validate_b014(self.target, bridge)

    def test_all_twelve_strong_answers_reject_wrong_value(self):
        for answer in self.bridge.iter(XH + "details"):
            with self.subTest(answer=answer.get("id")):
                bridge = copy.deepcopy(self.bridge)
                strong = self.node(bridge, answer.get("id")).find(".//" + XH + "strong")
                strong.text = strong.text.replace("=", "= 1 +", 1)
                with self.assertRaisesRegex(AssertionError, "Incorrect B014"):
                    validate_b014(self.target, bridge)

    def test_same_forty_two_does_not_allow_different_answer_pair(self):
        self.mutate(self.bridge, "B014-S-T05", "15 + 27 = 42", "18 + 24 = 42")
        with self.assertRaisesRegex(AssertionError, "displayed final answer"):
            validate_b014(self.target, self.bridge)

    def test_same_total_does_not_allow_reversed_answer_operands(self):
        self.mutate(self.bridge, "B014-S-T02", "5 + 1 = 6", "1 + 5 = 6")
        with self.assertRaisesRegex(AssertionError, "displayed final answer"):
            validate_b014(self.target, self.bridge)

    def test_same_forty_two_wrong_summary_target_rejected(self):
        self.mutate(self.bridge, "B014-S-T05", "Try It 5 · 15 + 27", "Try It 5 · 18 + 24")
        with self.assertRaisesRegex(AssertionError, "summary target"):
            validate_b014(self.target, self.bridge)

    def test_all_six_diagnostic_recheck_pairs_are_specific(self):
        for case, (a, b) in EXTRA_CASES.items():
            with self.subTest(case=case):
                bridge = copy.deepcopy(self.bridge)
                self.mutate(bridge, "B014-" + case, f"{a} + {b}", f"{b} + {a}")
                with self.assertRaisesRegex(AssertionError, "requested pair"):
                    validate_b014(self.target, bridge)

    def test_source_solution_backlink_cannot_point_to_other_existing_question(self):
        for i, (exercise, _, _, _, _) in enumerate(TRY_CASES, 1):
            with self.subTest(case=i):
                bridge = copy.deepcopy(self.bridge)
                answer = self.node(bridge, f"B014-S-T{i:02d}")
                answer.find(".//" + XH + "a").set("href", "#" + TRY_CASES[i % 6][0])
                with self.assertRaisesRegex(AssertionError, "specific source/solution"):
                    validate_b014(self.target, bridge)

    def test_all_twelve_solution_state_counts_are_checked(self):
        pattern = r"(\d+)(\s*(?:పదులు|పది)\s*[,;]\s*)(\d+)(\s*ఒకట్ల)"
        for answer in self.bridge.iter(XH + "details"):
            with self.subTest(answer=answer.get("id")):
                bridge = copy.deepcopy(self.bridge)
                changed = False
                for e in self.node(bridge, answer.get("id")).iter():
                    for field in ("text", "tail"):
                        value = getattr(e, field)
                        if value and re.search(pattern, value):
                            setattr(e, field, re.sub(pattern, lambda m: str(int(m[1]) + 1) + m[2] + m[3] + m[4], value, count=1))
                            changed = True
                            break
                    if changed:
                        break
                self.assertTrue(changed)
                with self.assertRaisesRegex(AssertionError, "stage counts"):
                    validate_b014(self.target, bridge)

    def test_same_total_before_and_after_state_cannot_swap(self):
        self.mutate(self.bridge, "B014-S-D03", "3 పదులు, 12 ఒకట్లు", "4 పదులు, 2 ఒకట్లు")
        self.assertEqual(3 * 10 + 12, 4 * 10 + 2)
        with self.assertRaisesRegex(AssertionError, "stage counts"):
            validate_b014(self.target, self.bridge)

    def test_coincident_forty_two_does_not_allow_wrong_stage_equation(self):
        self.mutate(self.bridge, "B014-S-D03", "30 + 12 = 42", "40 + 2 = 42")
        with self.assertRaisesRegex(AssertionError, "place-value equations"):
            validate_b014(self.target, self.bridge)

    def test_exchange_cannot_keep_original_ones_after_adding_rod(self):
        self.mutate(self.bridge, "B014-S-T03", "1 పది, 2 ఒకట్లు", "1 పది, 12 ఒకట్లు")
        with self.assertRaisesRegex(AssertionError, "stage counts"):
            validate_b014(self.target, self.bridge)

    def test_unchanged_final_answer_does_not_allow_exchange_of_nine(self):
        self.mutate(self.bridge, "B014-S-T05", "12 ఒకట్లలో 10 బ్లాకులను", "12 ఒకట్లలో 9 బ్లాకులను")
        with self.assertRaisesRegex(AssertionError, "exchange reasoning"):
            validate_b014(self.target, self.bridge)

    def test_partition_of_second_seven_must_leave_two(self):
        self.mutate(self.bridge, "B014-S-T03", "రెండో సమూహంలో మరో రెండు", "రెండో సమూహంలో మరో మూడు")
        with self.assertRaisesRegex(AssertionError, "exchange reasoning"):
            validate_b014(self.target, self.bridge)

    def test_six_plus_eight_requires_four_of_second_group_for_ten(self):
        self.mutate(self.bridge, "B014-S-T04", "రెండో సమూహం నుంచి నాలుగు", "రెండో సమూహం నుంచి ఐదు")
        with self.assertRaisesRegex(AssertionError, "exchange reasoning"):
            validate_b014(self.target, self.bridge)

    def test_all_twelve_english_model_counts_cannot_conflict_with_telugu(self):
        pattern = r"\b(?:" + "|".join(EN_NUMBERS) + r")\b"
        for answer in self.bridge.iter(XH + "details"):
            with self.subTest(answer=answer.get("id")):
                bridge = copy.deepcopy(self.bridge)
                english = next(p for p in self.node(bridge, answer.get("id")).findall(XH + "p") if p.get("lang") == "en")
                match = re.search(pattern, english.text, re.I)
                self.assertIsNotNone(match)
                replacement = "nine" if match[0].lower() != "nine" else "eight"
                english.text = english.text[:match.start()] + replacement + english.text[match.end():]
                with self.assertRaisesRegex(AssertionError, "English model counts"):
                    validate_b014(self.target, bridge)

    def test_zero_addend_must_not_add_a_unit_block(self):
        self.mutate(self.bridge, "B014-S-R01", "అదనపు బ్లాకును గీయకండి", "అదనపు బ్లాకును గీయండి")
        with self.assertRaisesRegex(AssertionError, "exchange reasoning"):
            validate_b014(self.target, self.bridge)

    def test_zero_remaining_ones_must_be_written(self):
        self.mutate(self.bridge, "B014-S-R03", "ఒకట్ల స్థానంలో 0 రాయాలి", "ఒకట్ల స్థానంలో 1 రాయాలి")
        with self.assertRaisesRegex(AssertionError, "exchange reasoning"):
            validate_b014(self.target, self.bridge)

    def test_correct_ten_total_does_not_allow_strict_boundary(self):
        self.mutate(self.bridge, "B014-ten-boundary", "10 కంటే ఎక్కువ కావాల్సిన అవసరం లేదు", "10 కంటే ఎక్కువ కావాలి")
        with self.assertRaisesRegex(AssertionError, "inclusive-ten"):
            validate_b014(self.target, self.bridge)

    def test_before_after_warning_cannot_instruct_double_counting(self):
        self.mutate(self.bridge, "B014-state-warning", "కలిపి లెక్కించవద్దు", "కలిపి లెక్కించండి")
        with self.assertRaisesRegex(AssertionError, "double-counting warning"):
            validate_b014(self.target, self.bridge)

    def test_color_does_not_add_value(self):
        self.mutate(self.bridge, "B014-ten-boundary", "ఎరుపు రంగు అదనపు విలువ ఇవ్వదు", "ఎరుపు రంగు అదనపు విలువ ఇస్తుంది")
        with self.assertRaisesRegex(AssertionError, "color boundary"):
            validate_b014(self.target, self.bridge)

    def test_model_table_same_value_rows_are_not_interchangeable(self):
        rows = self.node(self.bridge, "B014-K3").findall(".//" + XH + "tbody/" + XH + "tr")
        for column in (1, 2, 3):
            rows[2][column].text, rows[3][column].text = rows[3][column].text, rows[2][column].text
        with self.assertRaisesRegex(AssertionError, "support equations|table counts"):
            validate_b014(self.target, self.bridge)

    def test_model_table_stage_labels_must_match_counts(self):
        rows = self.node(self.bridge, "B014-K3").findall(".//" + XH + "tbody/" + XH + "tr")
        rows[2][0].text, rows[3][0].text = rows[3][0].text, rows[2][0].text
        with self.assertRaisesRegex(AssertionError, "stage roles"):
            validate_b014(self.target, self.bridge)

    def test_model_table_rod_count_cannot_be_its_contribution(self):
        rows = self.node(self.bridge, "B014-K3").findall(".//" + XH + "tbody/" + XH + "tr")
        rows[2][1].text = "30"
        with self.assertRaisesRegex(AssertionError, "table counts"):
            validate_b014(self.target, self.bridge)

    def test_model_table_all_four_rows_are_not_same_value(self):
        caption = self.node(self.bridge, "B014-K3").find(XH + "table/" + XH + "caption")
        caption.text = "అదే మొత్తం విలువకు దశలవారీ నమూనా"
        with self.assertRaisesRegex(AssertionError, "distinct addend/combined-stage caption"):
            validate_b014(self.target, self.bridge)

    def test_piece_count_is_not_model_value(self):
        self.mutate(self.bridge, "B014-K1", "ప్రతి కడ్డీని ఒక్క ఒకట్ల బ్లాకుగా లెక్కించకండి", "ప్రతి కడ్డీని ఒక్క ఒకట్ల బ్లాకుగా లెక్కించండి")
        with self.assertRaisesRegex(AssertionError, "unit/count/equality"):
            validate_b014(self.target, self.bridge)

    def test_two_digit_carry_must_add_new_ten(self):
        self.mutate(self.bridge, "B014-K3", "కొత్త 1 పది చేరితే 4 పదులు", "కొత్త 1 పది చేరితే 3 పదులు")
        with self.assertRaisesRegex(AssertionError, "count/value/carry"):
            validate_b014(self.target, self.bridge)

    def test_routing_cannot_select_different_existing_recheck(self):
        route = self.node(self.bridge, "B014-route")
        next(a for a in route.iter(XH + "a") if a.get("href") == "#B014-R02").set("href", "#B014-R01")
        with self.assertRaisesRegex(AssertionError, "routing link"):
            validate_b014(self.target, self.bridge)

    def test_entry_question_cannot_become_only_calculation(self):
        self.mutate(self.bridge, "B014-D03", "చూపండి", "లెక్కించండి")
        with self.assertRaisesRegex(AssertionError, "model request"):
            validate_b014(self.target, self.bridge)

    def test_missing_source_detail_rejected(self):
        self.node(self.bridge, "B014-S-T06").set("id", "B014-S-wrong")
        with self.assertRaisesRegex(AssertionError, "solution coverage"):
            validate_b014(self.target, self.bridge)

    def test_duplicate_solution_id_rejected(self):
        self.node(self.bridge, "B014-S-T06").set("id", "B014-S-T05")
        with self.assertRaisesRegex(AssertionError, "Duplicate"):
            validate_b014(self.target, self.bridge)

    def test_extra_relation_after_correct_answer_rejected(self):
        self.mutate(self.bridge, "B014-S-T01", "3 + 6 = 9", "3 + 6 = 9 = 10")
        with self.assertRaisesRegex(AssertionError, "Incorrect B014"):
            validate_b014(self.target, self.bridge)

    def test_worksheet_not_falsely_claimed_bundled(self):
        self.mutate(self.bridge, "B014-activity-boundary", "వర్క్‌షీట్ జతచేయలేదు", "వర్క్‌షీట్ జతచేశాం")
        with self.assertRaisesRegex(AssertionError, "worksheet acquisition"):
            validate_b014(self.target, self.bridge)


if __name__ == "__main__":
    unittest.main()
