"""Actual B008 source/catalog/bridge corruption tests; no output files written."""
from pathlib import Path
import copy
import json
import unittest
import xml.etree.ElementTree as ET

from practice_checks import (CN, MATH, source_cases, validate_practice_target,
                             round_whole_half_up, controlling_digit, validate_b008,
                             validate_practice_bridge, TE_PLACES, EN_PLACES, _children)

BASE = Path(__file__).resolve().parents[1]


class SourcePracticeTests(unittest.TestCase):
    def test_every_exercise_and_response_count(self):
        source, cases = source_cases()
        self.assertEqual(len(cases), 58)
        self.assertEqual(sum(len(c["parts"]) for c in cases), 96)
        self.assertEqual(sum(c["kind"] == "open" for c in cases), 2)
        self.assertEqual(sum(c["solution_id"] is not None for c in cases), 29)
        self.assertEqual(sum(len(c["parts"]) for c in cases if c["solution_id"]), 48)
        self.assertEqual(len(list(source.iter(MATH + "math"))), 57)

    def test_all_thirty_rounding_results_have_strictly_nearer_multiple(self):
        parts = [p for c in source_cases()[1] if c["kind"] == "round" for p in c["parts"]]
        self.assertEqual(len(parts), 30)
        for p in parts:
            with self.subTest(p=p):
                self.assertEqual(p["expected"] % p["place"], 0)
                self.assertLess(2 * abs(p["input"] - p["expected"]), p["place"])
                self.assertEqual(p["expected"], round_whole_half_up(p["input"], p["place"]))

    def test_same_answer_does_not_imply_same_target(self):
        number = 149597888
        self.assertEqual(round_whole_half_up(number, 10000000), 150000000)
        self.assertEqual(round_whole_half_up(number, 1000000), 150000000)
        self.assertEqual(controlling_digit(number, 10000000), 9)
        self.assertEqual(controlling_digit(number, 1000000), 5)

    def test_direct_rounding_not_previous_part_answer(self):
        self.assertEqual(round_whole_half_up(24493, 1000), 24000)
        self.assertEqual(round_whole_half_up(round_whole_half_up(24493, 100), 1000), 25000)
        self.assertEqual(round_whole_half_up(18549, 100), 18500)
        self.assertEqual(round_whole_half_up(round_whole_half_up(18549, 10), 100), 18600)


class _TargetFixture(unittest.TestCase):
    def setUp(self):
        # Compose actual catalog text in memory. Original paths are retained
        # only for these non-rendering mathematical fixtures; no fake SVG is
        # written and no generated-reader result is inferred from this step.
        from build_unit import localize
        self.source, self.cases = source_cases()
        catalog = json.loads((BASE / "translations/TE-B008.te.json").read_text(encoding="utf-8"))
        assets = {e.get("src"): {"localized_path": e.get("src")}
                  for e in self.source.iter(CN + "image")}
        self.target = localize(self.source, catalog, assets)

    def node(self, root, ident):
        return next(e for e in root.iter() if e.get("id") == ident)

    def mutate(self, root, ident, before, after):
        for node in self.node(root, ident).iter():
            for key in ("text", "tail"):
                value = getattr(node, key)
                if value and before in value:
                    setattr(node, key, value.replace(before, after, 1))
                    return
        self.fail("Fixture did not mutate actual text: " + before)

    def rejects(self, fragment=None):
        if fragment:
            with self.assertRaisesRegex(AssertionError, fragment):
                validate_practice_target(self.target)
        else:
            with self.assertRaises(AssertionError):
                validate_practice_target(self.target)


class PracticeTargetTests(_TargetFixture):
    def test_all_actual_localized_questions_and_supplied_answers(self):
        self.assertEqual(validate_practice_target(self.target), {
            "source_exercises": 58, "response_parts": 96, "determined_parts": 94,
            "open_writing_parts": 2, "provided_solution_nodes": 29,
            "rounding_parts": 30, "place_parts": 20})

    def test_actual_source_id_long_form_is_preserved(self):
        self.node(self.target, "fs-id1166761301603").set("id", "fs-id116676130160")
        self.rejects("structure/IDs")

    def test_duplicate_id_rejected(self):
        self.node(self.target, "fs-id1190749").set("id", "fs-id2221898")
        self.rejects("Duplicate")

    def test_fraction_denominator_change_rejected(self):
        frac = self.node(self.target, "fs-id2475713").find(".//" + MATH + "mfrac")
        frac[1].text = "4"
        self.rejects("MathML")

    def test_decimal_change_rejected(self):
        self.mutate(self.target, "fs-id2475713", "8.1", "8.0")
        self.rejects("MathML")

    def test_zero_added_to_counting_answer_rejected(self):
        self.mutate(self.target, "fs-id2686692", "5, 125", "0, 5, 125")
        self.rejects("numeric/source")

    def test_whole_and_integer_labels_cannot_be_swapped(self):
        self.mutate(self.target, "fs-id2686876", "పూర్ణాంకాలను", "పూర్ణ సంఖ్యలను")
        self.rejects("whole-number")

    def test_model_alt_actual_square_count_mutation_rejected(self):
        media = self.node(self.target, "fs-id1393361")
        media.set("alt", media.get("alt").replace("చతురస్రాలు ఐదు", "చతురస్రాలు మూడు"))
        self.rejects("model alt count")

    def test_model_alt_zero_group_mutation_rejected(self):
        media = self.node(self.target, "fs-id2675330")
        media.set("alt", media.get("alt").replace("కడ్డీలు లేవు", "కడ్డీలు ఉన్నాయి"))
        self.rejects("model alt count/zero")

    def test_model_alt_unit_value_mutation_rejected(self):
        media = self.node(self.target, "fs-id1393361")
        media.set("alt", media.get("alt").replace("100 బ్లాకుల", "1,000 బ్లాకుల"))
        self.rejects("model unit values")

    def test_supplied_model_answer_changed_rejected(self):
        self.mutate(self.target, "fs-id1385187", "561", "651")
        self.rejects("numeric/source")

    def test_zero_occupied_place_changed_rejected(self):
        self.mutate(self.target, "fs-id2279435", "పదుల స్థానం", "ఒకట్ల స్థానం")
        self.rejects("supplied place name")

    def test_hundred_thousand_place_changed_rejected(self):
        self.mutate(self.target, "fs-id2323011", "వంద వేల స్థానం", "పది వేల స్థానం")
        self.rejects("supplied place name")

    def test_supplied_english_name_changed_rejected(self):
        self.mutate(self.target, "fs-id1231920", "seventy-eight", "eighty-seven")
        self.rejects("supplied English name")

    def test_english_input_coefficient_changed_rejected(self):
        self.mutate(self.target, "fs-id1387432", "one hundred two thousand", "one hundred twenty thousand")
        self.rejects("source English phrase")

    def test_supplied_leading_zero_group_corruption_rejected(self):
        self.mutate(self.target, "fs-id2474599", "11,044,167", "11,440,167")
        self.rejects("numeric/source")

    def test_supplied_trailing_zero_group_omission_rejected(self):
        self.mutate(self.target, "fs-id1617818", "7,173,000,000", "7,173,000")
        self.rejects("numeric/source")

    def test_actual_rounding_question_target_changed_rejected(self):
        self.mutate(self.target, "fs-id2751447", "దగ్గరి పదులకు", "దగ్గరి వందలకు")
        self.rejects("target rounding place")

    def test_coincident_answer_target_swap_rejected(self):
        self.mutate(self.target, "fs-id1792359", "పది మిలియన్ల కిలోమీటర్లు", "ఒక మిలియన్ కిలోమీటర్లు")
        self.rejects("target rounding place/unit")

    def test_population_target_unit_changed_rejected(self):
        self.mutate(self.target, "fs-id2058233", "వంద మిలియన్ల మంది", "పది మిలియన్ల మంది")
        self.rejects("target rounding place/unit")

    def test_currency_symbol_conversion_rejected(self):
        self.mutate(self.target, "fs-id1744657", "$24,493", "₹24,493")
        self.rejects("MathML")

    def test_distance_unit_conversion_rejected(self):
        self.mutate(self.target, "fs-id1270274", "కిలోమీటర్లు", "మైళ్లు")
        self.rejects("source unit")

    def test_open_source_sample_not_a_unique_key(self):
        self.mutate(self.target, "fs-id1948767", "భిన్నంగా ఉండవచ్చు", "ఒకటే ఉండాలి")
        self.rejects("open response")

    def test_self_check_blank_cells_not_solved_answers(self):
        media = self.node(self.target, "eip-id1165721974707")
        media.set("alt", media.get("alt").replace("మొత్తం 18 గడులు ఖాళీగా", "మొత్తం 12 గడులు ఖాళీగా"))
        self.rejects("self-check blank")

    def test_telugu_supplied_name_is_not_masked_by_correct_english(self):
        self.mutate(self.target, "fs-id1231920", "డెబ్బై ఎనిమిది", "ఎనభై ఏడు")
        self.rejects("reviewed Telugu supplied name")

    def test_telugu_source_coefficient_is_not_masked_by_correct_english(self):
        self.mutate(self.target, "fs-id1387432", "నూట రెండు వేల", "నూట ఇరవై వేల")
        self.rejects("reviewed Telugu input name")


class PracticeBridgeTests(_TargetFixture):
    def setUp(self):
        super().setUp()
        self.bridge = ET.parse(BASE / "translations/TE-B008.bridge.xhtml").getroot()

    def bridge_rejects(self, fragment=None, bridge=None):
        bridge = self.bridge if bridge is None else bridge
        if fragment:
            with self.assertRaisesRegex(AssertionError, fragment):
                validate_practice_bridge(self.target, bridge)
        else:
            with self.assertRaises(AssertionError):
                validate_practice_bridge(self.target, bridge)

    def answer(self, bridge, ident):
        return next(e for e in self.node(bridge, ident).iter() if e.tag.endswith("}strong"))

    def test_complete_actual_bridge_and_catalog(self):
        result = validate_b008(self.target, self.bridge)
        self.assertEqual(result["determined_parts"], 94)
        self.assertEqual(result["open_writing_parts"], 2)
        self.assertEqual(result["source_bridge_solutions"], 58)
        self.assertEqual(result["bridge_response_parts"], 96)
        self.assertEqual(result["bridge_equalities"], 64)
        self.assertEqual(result["bridge_equality_relations"], 68)

    def test_missing_full_solution_rejected(self):
        self.node(self.bridge, "B008-S-fs-id1166761301603").set("id", "missing-long-id")
        self.bridge_rejects("source-solution coverage")

    def test_missing_part_rejected(self):
        self.node(self.bridge, "B008-S-fs-id1350682-e").set("id", "missing-part")
        self.bridge_rejects("response-part coverage")

    def test_duplicate_solution_id_rejected(self):
        self.node(self.bridge, "B008-S-fs-id1190749").set("id", "B008-S-fs-id2221898")
        self.bridge_rejects("Duplicate")

    def test_wrong_existing_source_backlink_rejected(self):
        detail = self.node(self.bridge, "B008-S-fs-id2221898")
        next(e for e in detail.iter() if e.tag.endswith("}a")).set("href", "#fs-id1190749")
        self.bridge_rejects("wrong source-question backlink")

    def test_dangling_and_unsafe_links_rejected(self):
        for href in ("#missing", "javascript:alert(1)", "https://example.invalid/"):
            with self.subTest(href=href):
                bridge = copy.deepcopy(self.bridge)
                next(e for e in bridge.iter() if e.tag.endswith("}a")).set("href", href)
                self.bridge_rejects("dangling/foreign", bridge)

    def test_every_one_of_94_displayed_determined_answers_rejects_corruption(self):
        changed = 0
        for case in self.cases:
            if case["kind"] == "open":
                continue
            for part in case["parts"]:
                with self.subTest(case=case["id"], part=part["label"]):
                    bridge = copy.deepcopy(self.bridge)
                    ident = "B008-S-" + case["id"]
                    if part["label"] != "single":
                        ident += "-" + part["label"]
                    if case["kind"] == "place":
                        row = self.node(bridge, ident)
                        cell = _children(row, "td")[1]
                        wrong_place = 10 if part["place"] == 1 else 1
                        cell.text = TE_PLACES[wrong_place] + " స్థానం (" + EN_PLACES[wrong_place] + ")"
                    elif case["kind"] == "name":
                        self.answer(bridge, ident).text += " ఒకటి"
                    elif case["kind"] == "membership":
                        self.answer(bridge, ident).text += ", 999"
                    else:
                        answer = self.answer(bridge, ident)
                        display = f"{part['expected']:,}"
                        self.assertIn(display, answer.text)
                        answer.text = answer.text.replace(display, f"{part['expected']+1:,}", 1)
                    self.bridge_rejects(bridge=bridge)
                    changed += 1
        self.assertEqual(changed, 94)

    def test_all_twenty_added_contributions_checked_separately_from_place_names(self):
        changed = 0
        for case in self.cases:
            if case["kind"] != "place":
                continue
            for part in case["parts"]:
                with self.subTest(case=case["id"], part=part["label"]):
                    bridge = copy.deepcopy(self.bridge)
                    row = self.node(bridge, "B008-S-" + case["id"] + "-" + part["label"])
                    cell = _children(row, "td")[2]
                    cell.text = f"{part['digit']} × {part['place']:,} = {part['contribution']+1:,}"
                    self.bridge_rejects("contribution/digit/place equation", bridge)
                    changed += 1
        self.assertEqual(changed, 20)

    def test_counting_and_whole_label_swap_rejected(self):
        self.mutate(self.bridge, "B008-S-fs-id1617693-a", "సహజ సంఖ్యలు:", "పూర్ణాంకాలు:")
        self.bridge_rejects("answer-set label")

    def test_true_zero_equality_wrong_place_unit_rejected(self):
        self.mutate(self.bridge, "B008-S-fs-id2197876-e", "0 × 10,000 = 0", "0 × 1,000 = 0")
        self.bridge_rejects("contribution/digit/place")

    def test_place_name_changed_but_correct_contribution_not_enough(self):
        self.mutate(self.bridge, "B008-S-fs-id1522372-a", "పది వేల స్థానం", "వేల స్థానం")
        self.bridge_rejects("place-name answer")

    def test_displayed_part_label_changed(self):
        self.mutate(self.bridge, "B008-S-fs-id1522372-a", "ⓐ 9", "ⓑ 9")
        self.bridge_rejects("displayed part label")

    def test_intermediate_model_sum_not_just_final_answer(self):
        self.mutate(self.bridge, "B008-S-fs-id1224988", "500 + 60 + 1", "500 + 50 + 1")
        self.bridge_rejects("explanatory equation")

    def test_model_counts_not_only_a_sum_with_same_total(self):
        self.mutate(self.bridge, "B008-S-fs-id1224988", "5 × 100 + 6 × 10", "4 × 100 + 16 × 10")
        self.bridge_rejects("explanatory equation")

    def test_padded_group_width_must_survive_same_value(self):
        self.mutate(self.bridge, "B008-S-fs-id2241247", "11 | 471 | 036 | 106", "11 | 471 | 36 | 106")
        self.bridge_rejects("zero/period groups")

    def test_all_zero_group_cannot_disappear(self):
        self.mutate(self.bridge, "B008-S-fs-id1733890", "39 | 000 | 000 | 000 | 000", "39 | 000 | 000 | 000")
        self.bridge_rejects("zero/period groups")

    def test_wrong_english_name_with_correct_telugu_and_sum(self):
        self.mutate(self.bridge, "B008-S-fs-id1166761301603", "eight thousand", "eighty thousand")
        self.bridge_rejects("English number value")

    def test_wrong_telugu_name_with_correct_english_and_sum(self):
        self.mutate(self.bridge, "B008-S-fs-id1166761301603", "ఎనిమిది వేల, నాలుగు", "ఎనభై వేల, నాలుగు")
        self.bridge_rejects("reviewed Telugu displayed name")

    def test_same_answer_different_rounding_target_rejected(self):
        self.mutate(self.bridge, "B008-S-fs-id1806959-b", "లక్ష్యం పది మిలియన్ల స్థానం", "లక్ష్యం మిలియన్ల స్థానం")
        self.bridge_rejects("rounding input/target/control")

    def test_same_upward_result_wrong_neighbor_rejected(self):
        self.mutate(self.bridge, "B008-S-fs-id1806959-b", "మిలియన్ల అంకె 9", "మిలియన్ల అంకె 5")
        self.bridge_rejects("rounding input/target/control")

    def test_rounding_summary_target_not_only_part_answers(self):
        self.mutate(self.bridge, "B008-S-fs-id1341642", "దగ్గరి వందలకు", "దగ్గరి వేలకు")
        self.bridge_rejects("rounding summary target")

    def test_direct_thousand_answer_not_double_rounded(self):
        self.answer(self.bridge, "B008-S-fs-id2792494-c").text = "$25,000"
        self.bridge_rejects("displayed rounded answer")

    def test_direct_hundred_answer_not_double_rounded(self):
        self.answer(self.bridge, "B008-S-fs-id1604312-b").text = "$18,600"
        self.bridge_rejects("displayed rounded answer")

    def test_warning_double_round_result_checked_independently(self):
        detail = self.node(self.bridge, "B008-S-fs-id2792494")
        warning = _children(detail, "p")[-1]
        self.assertIn("$25,000", warning.text)
        warning.text = warning.text.replace("$25,000", "$24,000")
        self.bridge_rejects("direct/double-rounding warning")

    def test_all_thirty_distance_explanations_checked(self):
        for case in self.cases:
            if case["kind"] != "round":
                continue
            for part in case["parts"]:
                with self.subTest(case=case["id"], part=part["label"]):
                    bridge = copy.deepcopy(self.bridge)
                    low = part["input"] // part["place"] * part["place"]
                    a, b = part["input"] - low, low + part["place"] - part["input"]
                    self.mutate(bridge, "B008-S-" + case["id"] + "-" + part["label"],
                                f"దూరాలు వరుసగా {a:,}, {b:,}", f"దూరాలు వరుసగా {a+1:,}, {b:,}")
                    self.bridge_rejects("adjacent multiples/distances", bridge)

    def test_false_midpoint_claim_rejected(self):
        self.mutate(self.bridge, "B008-S-fs-id1372149-a", "సమాన దూరపు సందర్భం కాదు", "సమాన దూరపు సందర్భం")
        self.bridge_rejects("above-midpoint")

    def test_wrong_midpoint_even_when_correct_result_remains(self):
        self.mutate(self.bridge, "B008-S-fs-id1372149-a", "మధ్య విలువ 163,500", "మధ్య విలువ 163,584")
        self.bridge_rejects("adjacent multiples/distances")

    def test_five_boundary_is_in_upward_branch(self):
        self.mutate(self.bridge, "B008-S-fs-id1372149-a", "5 లేదా అంతకన్నా ఎక్కువ", "5 కన్నా ఎక్కువ")
        self.bridge_rejects("up/five branch")

    def test_target_nine_does_not_require_carry(self):
        self.mutate(self.bridge, "B008-S-fs-id1185521-b", "9 అయినంత మాత్రాన బదిలీ చేయము", "9 అయినంత మాత్రాన బదిలీ చేస్తాం")
        self.bridge_rejects("target-nine no-carry")

    def test_carry_destination_with_same_correct_answer(self):
        self.mutate(self.bridge, "B008-S-fs-id1806959-c", "పది మిలియన్ల స్థానానికి 1 బదిలీ", "వంద మిలియన్ల స్థానానికి 1 బదిలీ")
        self.bridge_rejects("carry destination")

    def test_calendar_product_not_merely_name_checked(self):
        self.mutate(self.bridge, "B008-S-fs-id1341564", "70 × 365 × 24", "70 × 366 × 24")
        self.bridge_rejects("explanatory equation")

    def test_historical_date_in_own_explanation_retained(self):
        self.mutate(self.bridge, "B008-S-fs-id1544452", "జూలై 1, 2014", "జూలై 1, 2026")
        self.bridge_rejects("historical naming date")

    def test_repeated_prose_result_not_masked_by_correct_strong_answer(self):
        detail = self.node(self.bridge, "B008-S-fs-id2926292")
        tail = _children(detail, "p")[-1]
        self.assertIn("4,568,000,000", tail.text)
        tail.text = tail.text.replace("4,568,000,000", "4,586,000,000")
        self.bridge_rejects("repeated displayed answer")

    def test_original_dollars_not_converted_in_bridge(self):
        detail = self.node(self.bridge, "B008-S-fs-id1572155")
        tail = _children(detail, "p")[-1]
        tail.text = tail.text.replace("అమెరికా డాలర్లు", "భారత రూపాయలు")
        self.bridge_rejects("numeric-quantity unit")

    def test_round_answer_units_are_checked(self):
        strong = self.answer(self.bridge, "B008-S-fs-id1806959-b")
        strong.text = strong.text.replace("కిలోమీటర్లు", "మైళ్లు")
        self.bridge_rejects("displayed rounded answer/unit")

    def test_correct_metadata_cannot_mask_wrong_displayed_answer(self):
        part = self.node(self.bridge, "B008-S-fs-id1604312-b")
        part.set("data-correct-answer", "18500")
        self.answer(self.bridge, part.get("id")).text = "$18,600"
        self.bridge_rejects("displayed rounded answer")

    def test_open_example_numeric_answer_can_change_if_reasoning_stays_true(self):
        self.mutate(self.bridge, "B008-S-fs-id1258379", "137 పుస్తకాలు", "138 పుస్తకాలు")
        self.mutate(self.bridge, "B008-S-fs-id1258379", "ఒకట్ల అంకె 7", "ఒకట్ల అంకె 8")
        self.mutate(self.bridge, "B008-S-fs-id1258379", "137 కు", "138 కు")
        self.mutate(self.bridge, "B008-S-fs-id1258379", "దూరాలు 7, 3", "దూరాలు 8, 2")
        self.mutate(self.bridge, "B008-S-fs-id1258379", "137 నే", "138 నే")
        self.assertEqual(validate_practice_bridge(self.target, self.bridge)["bridge_open_writing_parts"], 2)

    def test_open_example_math_still_checked_without_fixed_input_key(self):
        self.mutate(self.bridge, "B008-S-fs-id1258379", "సుమారు 140 పుస్తకాలు", "సుమారు 130 పుస్తకాలు")
        self.bridge_rejects("illustrative rounded value")

    def test_writing_rubric_does_not_require_numeric_example(self):
        self.mutate(self.bridge, "B008-S-fs-id1258379", "సంఖ్యలు ఇవ్వకపోయినా", "సంఖ్యలు తప్పనిసరిగా ఇచ్చి")
        self.bridge_rejects("optional numeric example")

    def test_one_place_unit_is_its_numeric_value(self):
        self.mutate(self.bridge, "B008-conventions", "వంద అంటే 100", "వంద అంటే 10")
        self.bridge_rejects("one-place-unit amount")

    def test_incrementing_target_does_not_mean_adding_one_to_whole_number(self):
        self.mutate(self.bridge, "B008-conventions", "సంఖ్యకు కేవలం 1 కలపడం కాదు", "సంఖ్యకు కేవలం 1 కలపడం")
        self.bridge_rejects("place unit confused")

    def test_self_confidence_not_turned_into_automatic_score(self):
        self.mutate(self.bridge, "B008-self-check-support", "స్వయంచాలక మార్కులు వేయదు", "స్వయంచాలక మార్కులు వేస్తుంది")
        self.bridge_rejects("non-autograding")


if __name__ == "__main__":
    unittest.main()
