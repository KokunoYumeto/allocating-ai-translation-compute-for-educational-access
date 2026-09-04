"""B011/B012 author-math regression tests using actual target/bridge content."""
import copy
import unittest
import xml.etree.ElementTree as ET

from build_unit import BASE, asset_map, localize, unit_inputs
from inspect_source import slots
from readiness_checks import (CN, MATH, XH, SVG, MODEL_PATH, RELATION,
                              model_counts, readiness_equalities,
                              readiness_name_value, validate_readiness)


class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.source = {}; self.target = {}; self.bridge = {}; self.catalog = {}
        for unit in ("TE-B011", "TE-B012"):
            source, _, catalog = unit_inputs(unit)
            self.source[unit] = source
            self.catalog[unit] = catalog
            self.target[unit] = localize(source, catalog, asset_map(unit))
            self.bridge[unit] = ET.parse(BASE / "translations" / (unit + ".bridge.xhtml")).getroot()

    def node(self, root, ident):
        return next(e for e in root.iter() if e.get("id") == ident)

    def mutate(self, root, ident, before, after):
        for node in self.node(root, ident).iter():
            for field in ("text", "tail"):
                value = getattr(node, field)
                if value and before in value:
                    setattr(node, field, value.replace(before, after, 1))
                    return
        self.fail("Mutation did not touch actual XML: " + before)

    def validate(self, unit):
        return validate_readiness(unit, self.target[unit], self.bridge[unit])

    def test_actual_source_target_inventory(self):
        for unit, counts in [("TE-B011", (18, 8, 8, 2, 5)), ("TE-B012", (13, 6, 6, 1, 2))]:
            with self.subTest(unit=unit):
                root = self.source[unit]
                self.assertEqual((len(list(root.iter())), len([e for e in root.iter() if e.get("id")]), len(list(slots(root))), len(list(root.iter(MATH + "math"))), len(self.catalog[unit]["translations"])), counts)
                self.assertIsNone(self.target[unit].find(CN + "title"))

    def test_actual_answers_and_all_eight_equations(self):
        results = [self.validate(unit) for unit in self.target]
        self.assertEqual([r["source_answer"] for r in results], [215, 342006])
        self.assertEqual([r["displayed_equation_chains"] for r in results], [5, 3])
        self.assertEqual(sum(r["displayed_equation_chains"] for r in results), 8)
        self.assertEqual([r["source_cross_module_links"] for r in results], [1, 1])

    def test_actual_svg_cells_determine_counts(self):
        root = ET.parse(BASE / MODEL_PATH).getroot()
        self.assertEqual(model_counts(root), (2, 1, 5))
        self.assertEqual(sum(len(g) for g in root.iter(SVG + "g")), 215)

    def test_actual_english_name_recomputed(self):
        self.assertEqual(readiness_name_value("three hundred forty-two thousand six"), 342006)
        for invalid in ["three hundred forty-two million six", "three hundred forty-two thousand six thousand one", "three hundreds forty-two thousand six"]:
            with self.subTest(invalid=invalid), self.assertRaises(AssertionError):
                readiness_name_value(invalid)

    def test_all_eight_displayed_equations_reject_wrong_results(self):
        tested = 0
        for unit, original in self.bridge.items():
            for index, node in enumerate(original.iter()):
                for field in ("text", "tail"):
                    value = getattr(node, field)
                    if not value:
                        continue
                    for match in RELATION.finditer(value):
                        with self.subTest(unit=unit, equation=match.group()):
                            bridge = copy.deepcopy(original)
                            changed = list(bridge.iter())[index]
                            left, right = match.group().rsplit("=", 1)
                            wrong = int(right.strip().replace(",", "")) + 1
                            setattr(changed, field, value.replace(match.group(), left + "= " + f"{wrong:,}", 1))
                            with self.assertRaisesRegex(AssertionError, "Incorrect readiness equality"):
                                validate_readiness(unit, self.target[unit], bridge)
                            tested += 1
        self.assertEqual(tested, 8)

    def test_correct_chain_prefix_cannot_hide_wrong_final_side(self):
        self.mutate(self.bridge["TE-B011"], "B011-total", "200 + 10 + 5 = 215", "200 + 10 + 5 = 215 = 216")
        with self.assertRaisesRegex(AssertionError, "Incorrect readiness equality"):
            self.validate("TE-B011")

    def test_model_source_answer_mutation(self):
        self.mutate(self.target["TE-B011"], "fs-idm216142416", "215", "251")
        with self.assertRaisesRegex(AssertionError, "MathML"):
            self.validate("TE-B011")

    def test_base_ten_math_text_cannot_change(self):
        self.mutate(self.target["TE-B011"], "fs-idm214637312", "base-10", "base-100")
        with self.assertRaisesRegex(AssertionError, "MathML"):
            self.validate("TE-B011")

    def test_model_alt_group_count_mutation(self):
        media = self.node(self.target["TE-B011"], "fs-id2778433")
        media.set("alt", media.get("alt").replace("చతురస్రాలు రెండు", "చతురస్రాలు మూడు"))
        with self.assertRaisesRegex(AssertionError, "accessible group count"):
            self.validate("TE-B011")

    def test_model_alt_cell_count_mutation(self):
        media = self.node(self.target["TE-B011"], "fs-id2778433")
        media.set("alt", media.get("alt").replace("100 బ్లాకుల", "10 బ్లాకుల"))
        with self.assertRaisesRegex(AssertionError, "accessible unit counts"):
            self.validate("TE-B011")

    def test_model_alt_cannot_reveal_answer(self):
        media = self.node(self.target["TE-B011"], "fs-id2778433")
        media.set("alt", media.get("alt") + " జవాబు 215.")
        with self.assertRaisesRegex(AssertionError, "accessible unit counts"):
            self.validate("TE-B011")

    def test_model_asset_mapping_cannot_point_at_other_picture(self):
        next(self.target["TE-B011"].iter(CN + "image")).set("src", "assets/B002/CNX_BMath_Figure_01_01_008.te.svg")
        with self.assertRaisesRegex(AssertionError, "asset mapping"):
            self.validate("TE-B011")

    def test_svg_missing_cell_cannot_hide_behind_metadata(self):
        root = ET.parse(BASE / MODEL_PATH).getroot()
        group = next(root.iter(SVG + "g"))
        group.remove(group[0])
        self.assertEqual(group.get("data-value"), "100")
        with self.assertRaisesRegex(AssertionError, "drawn cell count"):
            model_counts(root)

    def test_svg_same_cell_count_duplicate_position_rejected(self):
        root = ET.parse(BASE / MODEL_PATH).getroot()
        group = next(root.iter(SVG + "g"))
        group[1].set("x", group[0].get("x"))
        with self.assertRaisesRegex(AssertionError, "duplicate cell geometry"):
            model_counts(root)

    def test_svg_unit_label_cannot_disagree_with_drawn_hundred(self):
        root = ET.parse(BASE / MODEL_PATH).getroot()
        next(root.iter(SVG + "g")).set("data-value", "10")
        with self.assertRaisesRegex(AssertionError, "group/unit role"):
            model_counts(root)

    def test_count_unit_swap_same_product_rejected(self):
        self.mutate(self.bridge["TE-B011"], "B011-S-fs-idm207409024", "2 × 100 = 200", "100 × 2 = 200")
        with self.assertRaisesRegex(AssertionError, "count/unit/contribution"):
            self.validate("TE-B011")

    def test_model_count_eight_is_not_displayed_answer(self):
        self.node(self.bridge["TE-B011"], "B011-total").find(XH + "strong").text = "8"
        with self.assertRaisesRegex(AssertionError, "displayed model answer"):
            self.validate("TE-B011")

    def test_true_count_equality_needs_negative_value_explanation(self):
        self.mutate(self.bridge["TE-B011"], "B011-count-versus-value", "సంఖ్య 8 కాదు", "సంఖ్య 8")
        with self.assertRaisesRegex(AssertionError, "shape count conflated"):
            self.validate("TE-B011")

    def test_model_telugu_number_name_must_match_215(self):
        self.mutate(self.bridge["TE-B011"], "B011-total", "రెండు వందల పదిహేను", "రెండు వందల యాభై")
        with self.assertRaisesRegex(AssertionError, "name/place order"):
            self.validate("TE-B011")

    def test_model_place_order_cannot_swap_tens_and_ones(self):
        self.mutate(self.bridge["TE-B011"], "B011-total", "వరుసగా 2, 1, 5", "వరుసగా 2, 5, 1")
        with self.assertRaisesRegex(AssertionError, "name/place order"):
            self.validate("TE-B011")

    def test_grouped_source_answer_cannot_drop_zero(self):
        self.mutate(self.target["TE-B012"], "fs-idm221421664", "006", "06")
        with self.assertRaisesRegex(AssertionError, "MathML"):
            self.validate("TE-B012")

    def test_grouped_source_answer_cannot_change_zero_place(self):
        self.mutate(self.target["TE-B012"], "fs-idm221421664", "006", "600")
        with self.assertRaisesRegex(AssertionError, "MathML"):
            self.validate("TE-B012")

    def test_source_comma_token_is_protected(self):
        self.mutate(self.target["TE-B012"], "fs-idm221421664", ",", ".")
        with self.assertRaisesRegex(AssertionError, "MathML"):
            self.validate("TE-B012")

    def test_source_english_name_must_stay_three_hundred_forty_two(self):
        self.mutate(self.target["TE-B012"], "fs-idm218825920", "forty-two", "twenty-four")
        with self.assertRaisesRegex(AssertionError, "English number name"):
            self.validate("TE-B012")

    def test_source_telugu_name_cannot_disagree_with_english(self):
        self.mutate(self.target["TE-B012"], "fs-idm218825920", "నలభై రెండు", "ఇరవై నాలుగు")
        with self.assertRaisesRegex(AssertionError, "Telugu source name"):
            self.validate("TE-B012")

    def test_source_digit_request_cannot_become_word_request(self):
        self.mutate(self.target["TE-B012"], "fs-idm218825920", "అంకెలలో రాయండి", "మాటల్లో రాయండి")
        with self.assertRaisesRegex(AssertionError, "source name/question"):
            self.validate("TE-B012")

    def test_displayed_grouped_answer_cannot_hide_behind_correct_equation(self):
        self.node(self.bridge["TE-B012"], "B012-S-fs-idm218505136").find(".//" + XH + "strong").text = "342,600"
        with self.assertRaisesRegex(AssertionError, "displayed grouped answer"):
            self.validate("TE-B012")

    def test_period_width_must_preserve_all_three_places(self):
        self.mutate(self.bridge["TE-B012"], "B012-S-fs-idm218505136", "342 | 006", "342 | 06")
        with self.assertRaisesRegex(AssertionError, "zero-period width/order"):
            self.validate("TE-B012")

    def test_period_zero_place_must_not_move(self):
        self.mutate(self.bridge["TE-B012"], "B012-S-fs-idm218505136", "342 | 006", "342 | 600")
        with self.assertRaisesRegex(AssertionError, "zero-period width/order"):
            self.validate("TE-B012")

    def test_zero_times_wrong_place_same_value_still_rejected(self):
        self.mutate(self.bridge["TE-B012"], "B012-S-fs-idm218505136", "0 × 100 + 0 × 10", "0 × 1000 + 0 × 10")
        self.assertEqual(len(readiness_equalities(self.bridge["TE-B012"])), 3)
        with self.assertRaisesRegex(AssertionError, "coefficient/place equation"):
            self.validate("TE-B012")

    def test_zero_place_order_swap_same_value_still_rejected(self):
        self.mutate(self.bridge["TE-B012"], "B012-S-fs-idm218505136", "0 × 100 + 0 × 10", "0 × 10 + 0 × 100")
        self.assertEqual(len(readiness_equalities(self.bridge["TE-B012"])), 3)
        with self.assertRaisesRegex(AssertionError, "coefficient/place equation"):
            self.validate("TE-B012")

    def test_thousand_coefficient_unit_swap_same_value_rejected(self):
        self.mutate(self.bridge["TE-B012"], "B012-S-fs-idm218505136", "342 × 1,000", "1,000 × 342")
        with self.assertRaisesRegex(AssertionError, "coefficient/place equation"):
            self.validate("TE-B012")

    def test_closed_group_count_ambiguity_does_not_regress(self):
        self.mutate(self.bridge["TE-B012"], "B012-S-fs-idm218505136", "వెయ్యి విలువగల 342 సమూహాలు", "342 వేల సమూహాలు")
        with self.assertRaisesRegex(AssertionError, "count/unit wording"):
            self.validate("TE-B012")

    def test_zero_place_names_must_remain_hundreds_tens(self):
        self.mutate(self.bridge["TE-B012"], "B012-zero-place", "వందల, పదుల స్థానాలను", "వేల, వందల స్థానాలను")
        with self.assertRaisesRegex(AssertionError, "zero-place/value"):
            self.validate("TE-B012")

    def test_006_600_contrast_values_cannot_swap(self):
        self.mutate(self.bridge["TE-B012"], "B012-zero-place", "006 విలువ ఆరు", "006 విలువ ఆరు వందలు")
        with self.assertRaisesRegex(AssertionError, "zero-place/value"):
            self.validate("TE-B012")

    def test_english_grouped_answer_cannot_contradict_strong_answer(self):
        self.mutate(self.bridge["TE-B012"], "B012-bridge", "The groups are 342 and 006, giving 342,006", "The groups are 342 and 600, giving 342,600")
        with self.assertRaisesRegex(AssertionError, "English grouped answer"):
            self.validate("TE-B012")

    def test_both_source_cross_module_attributes_protected(self):
        for unit in self.target:
            for attribute, changed in [("document", "m81244"), ("target-id", "fs-id2601285")]:
                with self.subTest(unit=unit, attribute=attribute):
                    target = copy.deepcopy(self.target[unit])
                    next(target.iter(CN + "link")).set(attribute, changed)
                    with self.assertRaises(AssertionError):
                        validate_readiness(unit, target, self.bridge[unit])

    def test_both_source_bridge_backlinks_protected(self):
        for unit in self.bridge:
            with self.subTest(unit=unit):
                bridge = copy.deepcopy(self.bridge[unit])
                next(bridge.iter(XH + "a")).set("href", "#fs-id2601285")
                with self.assertRaisesRegex(AssertionError, "bridge links"):
                    validate_readiness(unit, self.target[unit], bridge)

    def test_existing_practice_link_cannot_point_to_answer(self):
        next(e for e in self.bridge["TE-B012"].iter(XH + "a") if e.get("href") == "TE-B005.html#B005-R01").set("href", "TE-B005.html#B005-S-R01")
        with self.assertRaisesRegex(AssertionError, "bridge links"):
            self.validate("TE-B012")

    def test_source_title_not_injected_from_editorial_metadata(self):
        ET.SubElement(self.target["TE-B012"], CN + "title").text = self.catalog["TE-B012"]["editorial_title_te"]
        with self.assertRaisesRegex(AssertionError, "structure"):
            self.validate("TE-B012")

    def test_source_solution_id_cannot_change(self):
        self.node(self.target["TE-B011"], "fs-idm219309424").set("id", "new-editorial-id")
        with self.assertRaisesRegex(AssertionError, "structure"):
            self.validate("TE-B011")

    def test_duplicate_bridge_id_rejected(self):
        self.node(self.bridge["TE-B011"], "B011-total").set("id", "B011-next")
        with self.assertRaisesRegex(AssertionError, "Duplicate readiness"):
            self.validate("TE-B011")


if __name__ == "__main__":
    unittest.main()
