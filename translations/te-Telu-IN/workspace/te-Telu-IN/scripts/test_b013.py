"""B013 actual-target/bridge corruption tests; no generated files are written."""
import copy
import unittest
import xml.etree.ElementTree as ET

from addition_checks import (CN, MATH, XH, PAIRS, EXERCISES, classify_notation,
                             source_cases, validate_addition_target, validate_b013)
from build_unit import BASE, localize, math_signature, structural_signature, unit_inputs
from inspect_source import slots


class AdditionTargetTests(unittest.TestCase):
    def setUp(self):
        self.source, self.meta, self.catalog = unit_inputs("TE-B013")
        self.target = localize(self.source, self.catalog, {})

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

    def test_source_inventory_and_derived_sums(self):
        source, cases = source_cases()
        self.assertEqual(len(list(source.iter())), 143)
        self.assertEqual(len(list(slots(source))), 93)
        self.assertEqual(len([n for n in source.iter() if n.get("id")]), 30)
        self.assertEqual(len(list(source.iter(MATH + "math"))), 19)
        self.assertEqual([x[2] for x in cases], [7, 8, 26, 12, 29, 37, 300])
        self.assertEqual(tuple(x[:2] for x in cases), PAIRS)

    def test_actual_target_preserves_source_and_words(self):
        self.assertEqual(len(validate_addition_target(self.target)), 7)
        self.assertEqual(math_signature(self.source), math_signature(self.target))
        self.assertEqual(structural_signature(self.source), structural_signature(self.target))

    def test_cnxml_equation_container_is_actually_expression(self):
        node = self.node(self.target, "fs-id1474530")
        self.assertEqual(node.tag, CN + "equation")
        text = "".join(node.itertext()).strip()
        self.assertEqual(classify_notation(text), ("expression", (3, 4)))
        self.assertEqual(classify_notation("3 + 4 = 7"), ("equation", (3, 4, 7)))
        for bad in ["3 + 4 = 8", "3 = 4", "3 - 4", "3 + 4 = 7 = 8", "3 + 4 trailing"]:
            with self.subTest(bad=bad), self.assertRaises(AssertionError):
                classify_notation(bad)

    def test_changed_operator_rejected(self):
        self.mutate(self.target, "fs-id1474530", "+", "-")
        with self.assertRaisesRegex(AssertionError, "MathML"):
            validate_addition_target(self.target)

    def test_operand_order_reversal_with_same_sum_rejected(self):
        numbers = list(self.node(self.target, "eip-id1168287109262").findall(CN + "item")[0].iter(MATH + "mn"))
        self.assertEqual(sum(int(n.text) for n in numbers), 8)
        numbers[0].text, numbers[1].text = numbers[1].text, numbers[0].text
        self.assertEqual(sum(int(n.text) for n in numbers), 8)
        with self.assertRaisesRegex(AssertionError, "MathML"):
            validate_addition_target(self.target)

    def test_different_pair_with_same_sum_rejected(self):
        numbers = list(self.node(self.target, "eip-id1168289469583").findall(CN + "item")[0].iter(MATH + "mn"))
        numbers[0].text, numbers[1].text = "9", "3"
        self.assertEqual(sum(int(n.text) for n in numbers), 12)
        with self.assertRaisesRegex(AssertionError, "MathML"):
            validate_addition_target(self.target)

    def test_source_expression_cannot_gain_equal_sign(self):
        math = self.node(self.target, "fs-id1474530").find(MATH + "math")
        ET.SubElement(math, MATH + "mo").text = "="
        ET.SubElement(math, MATH + "mn").text = "7"
        with self.assertRaises(AssertionError):
            validate_addition_target(self.target)

    def test_all_six_provided_readings_reject_corruption(self):
        for _, _, answer_id, pairs in EXERCISES:
            for index, (a, b) in enumerate(pairs):
                with self.subTest(answer=answer_id, part=index):
                    target = copy.deepcopy(self.target)
                    item = self.node(target, answer_id).findall(CN + "item")[index]
                    for e in item.iter():
                        for field in ("text", "tail"):
                            value = getattr(e, field)
                            if value:
                                setattr(e, field, value.replace("plus", "minus"))
                    with self.assertRaisesRegex(AssertionError, "English reading"):
                        validate_addition_target(target)

    def test_numeric_answer_does_not_replace_word_answer(self):
        item = self.node(self.target, "eip-id1168288479736").findall(CN + "item")[0]
        item.find(CN + "span").tail = " 12"
        with self.assertRaisesRegex(AssertionError, "reading"):
            validate_addition_target(self.target)

    def test_numeric_equation_cannot_append_to_source_word_answer(self):
        item = self.node(self.target, "eip-id1168288479736").findall(CN + "item")[0]
        item.find(CN + "span").tail += " 8 + 4 = 12"
        with self.assertRaisesRegex(AssertionError, "evaluated equation"):
            validate_addition_target(self.target)

    def test_source_sum_name_operand_swap_rejected(self):
        self.mutate(self.target, "eip-id1168287334447", "sum of seven and one", "sum of one and seven")
        with self.assertRaisesRegex(AssertionError, "English result name"):
            validate_addition_target(self.target)

    def test_example_addend_role_cannot_use_result_instead(self):
        self.mutate(self.target, "eip-id1168287334447", "7, 1 అనే కలిపే సంఖ్యలను", "7, 8 అనే కలిపే సంఖ్యలను")
        with self.assertRaisesRegex(AssertionError, "addend roles"):
            validate_addition_target(self.target)

    def test_telugu_reading_cannot_hide_behind_correct_english(self):
        self.mutate(self.target, "eip-id1168288479736", "ఎనిమిది ప్లస్ నాలుగు", "నాలుగు ప్లస్ ఎనిమిది")
        with self.assertRaisesRegex(AssertionError, "Telugu reading"):
            validate_addition_target(self.target)

    def test_telugu_sum_name_cannot_hide_behind_correct_reading(self):
        self.mutate(self.target, "eip-id1168288479736", "ఎనిమిది, నాలుగు", "నాలుగు, ఎనిమిది")
        with self.assertRaisesRegex(AssertionError, "Telugu result name"):
            validate_addition_target(self.target)

    def test_table_five_column_declaration_required(self):
        self.node(self.target, "fs-id2711498").find(CN + "tgroup").set("cols", "4")
        with self.assertRaises(AssertionError):
            validate_addition_target(self.target)

    def test_table_actual_cell_cannot_be_removed(self):
        row = self.node(self.target, "fs-id2711498").find(".//" + CN + "tbody/" + CN + "row")
        row.remove(list(row)[-1])
        with self.assertRaises(AssertionError):
            validate_addition_target(self.target)

    def test_table_role_header_swap_rejected(self):
        row = self.node(self.target, "fs-id2711498").find(".//" + CN + "thead/" + CN + "row")
        row[2].text, row[4].text = row[4].text, row[2].text
        with self.assertRaisesRegex(AssertionError, "column roles"):
            validate_addition_target(self.target)

    def test_table_accessible_dimension_corruption_rejected(self):
        table = self.node(self.target, "fs-id2711498")
        table.set("aria-label", table.get("aria-label").replace("ఐదు నిలువు", "నాలుగు నిలువు"))
        with self.assertRaisesRegex(AssertionError, "dimensions"):
            validate_addition_target(self.target)

    def test_table_accessible_operand_corruption_rejected(self):
        table = self.node(self.target, "fs-id2711498")
        table.set("aria-label", table.get("aria-label").replace("3 మరియు 4", "3 మరియు 7"))
        with self.assertRaisesRegex(AssertionError, "accessible operands"):
            validate_addition_target(self.target)

    def test_table_result_cannot_be_evaluated_seven(self):
        row = self.node(self.target, "fs-id2711498").find(".//" + CN + "tbody/" + CN + "row")
        row[4].text = "7; కలిపే సంఖ్యలు "
        with self.assertRaisesRegex(AssertionError, "name the sum"):
            validate_addition_target(self.target)

    def test_work_hours_stay_associated_with_correct_days(self):
        self.mutate(self.target, "fs-id3165690", "సోమవారం", "శుక్రవారం")
        with self.assertRaisesRegex(AssertionError, "hours/day"):
            validate_addition_target(self.target)

    def test_words_question_cannot_become_compute_question(self):
        self.mutate(self.target, "fs-id1549906", "మాటల్లో రాయండి:", "విలువను కనుక్కోండి:")
        with self.assertRaisesRegex(AssertionError, "answer type"):
            validate_addition_target(self.target)

    def test_id_mutation_rejected(self):
        self.node(self.target, "fs-id1386428").set("id", "wrong-source-exercise")
        with self.assertRaisesRegex(AssertionError, "structure"):
            validate_addition_target(self.target)


class AdditionBridgeTests(unittest.TestCase):
    node = AdditionTargetTests.node
    mutate = AdditionTargetTests.mutate

    def setUp(self):
        AdditionTargetTests.setUp(self)
        self.bridge = ET.parse(BASE / "translations/TE-B013.bridge.xhtml").getroot()

    def test_actual_bridge_answers_and_equations(self):
        self.assertEqual(validate_b013(self.target, self.bridge), {
            "source_pairs": 7, "source_word_parts": 6, "source_try_parts": 4,
            "original_entry_rechecks": 4, "optional_source_values": 7,
            "displayed_addition_equalities": 16})

    def test_all_seven_displayed_optional_answers_reject_corruption(self):
        for index, (a, b, total) in enumerate(source_cases()[1]):
            with self.subTest(pair=(a, b)):
                bridge = copy.deepcopy(self.bridge)
                row = self.node(bridge, "B013-extra-values").findall(".//" + XH + "tbody/" + XH + "tr")[index]
                row[1].text = row[1].text.replace("= " + str(total), "= " + str(total + 1))
                with self.assertRaisesRegex(AssertionError, "Incorrect B013 addition"):
                    validate_b013(self.target, bridge)

    def test_same_optional_total_different_operands_rejected(self):
        self.mutate(self.bridge, "B013-extra-values", "3 + 4 = 7", "2 + 5 = 7")
        with self.assertRaisesRegex(AssertionError, "optional pair/result"):
            validate_b013(self.target, self.bridge)

    def test_optional_operand_order_reversal_rejected(self):
        self.mutate(self.bridge, "B013-extra-values", "7 + 1 = 8", "1 + 7 = 8")
        with self.assertRaisesRegex(AssertionError, "optional pair/result"):
            validate_b013(self.target, self.bridge)

    def test_optional_source_part_mapping_rejected(self):
        self.mutate(self.bridge, "B013-extra-values", "మొదటి Try It ⓐ", "రెండో Try It ⓐ")
        with self.assertRaisesRegex(AssertionError, "source-part mapping"):
            validate_b013(self.target, self.bridge)

    def test_optional_values_cannot_lose_editorial_scope(self):
        self.mutate(self.bridge, "B013-extra-values", "మూలం అడిగిన మాటల జవాబులు కావు", "మూలం అడిగిన మాటల జవాబులు")
        with self.assertRaisesRegex(AssertionError, "optional/source"):
            validate_b013(self.target, self.bridge)

    def test_optional_carry_reason_must_keep_remaining_two(self):
        self.mutate(self.bridge, "B013-extra-values", "మిగిలిన రెండు కలిపితే పన్నెండు", "మిగిలిన మూడు కలిపితే పన్నెండు")
        with self.assertRaisesRegex(AssertionError, "arithmetic reason"):
            validate_b013(self.target, self.bridge)

    def test_optional_tens_and_ones_reason_cannot_hide_behind_correct_equation(self):
        self.mutate(self.bridge, "B013-extra-values", "రెండు పదులు, ఆరు ఒకట్లు", "రెండు పదులు, ఏడు ఒకట్లు")
        with self.assertRaisesRegex(AssertionError, "arithmetic reason"):
            validate_b013(self.target, self.bridge)

    def test_all_four_source_strong_answers_reject_corruption(self):
        for case in ["T01a", "T01b", "T02a", "T02b"]:
            with self.subTest(case=case):
                bridge = copy.deepcopy(self.bridge)
                strong = self.node(bridge, "B013-S-" + case).find(".//" + XH + "strong")
                strong.text = strong.text.replace("ప్లస్", "మైనస్")
                with self.assertRaisesRegex(AssertionError, "Telugu reading|strong word answers"):
                    validate_b013(self.target, bridge)

    def test_source_strong_numeric_answer_not_hidden_by_correct_english(self):
        strong = self.node(self.bridge, "B013-S-T01a").find(".//" + XH + "strong")
        strong.text = "12"
        with self.assertRaisesRegex(AssertionError, "Telugu reading"):
            validate_b013(self.target, self.bridge)

    def test_source_english_reading_order_reversal_rejected(self):
        self.mutate(self.bridge, "B013-S-T01a", "Eight plus four", "Four plus eight")
        with self.assertRaisesRegex(AssertionError, "English reading"):
            validate_b013(self.target, self.bridge)

    def test_source_named_sum_cannot_change_to_computed_name(self):
        self.mutate(self.bridge, "B013-S-T01a", "the sum of eight and four", "twelve")
        with self.assertRaisesRegex(AssertionError, "English result name"):
            validate_b013(self.target, self.bridge)

    def test_source_backlink_to_other_existing_try_it_rejected(self):
        answer = self.node(self.bridge, "B013-S-T01a")
        answer.find(".//" + XH + "a").set("href", "#fs-id2334163")
        with self.assertRaisesRegex(AssertionError, "backlink"):
            validate_b013(self.target, self.bridge)

    def test_source_solution_summary_wrong_pair_same_total_rejected(self):
        self.mutate(self.bridge, "B013-S-T01a", "8 + 4", "9 + 3")
        with self.assertRaisesRegex(AssertionError, "source bridge question pair"):
            validate_b013(self.target, self.bridge)

    def test_zero_place_operands_cannot_be_reduced_to_one_two(self):
        self.mutate(self.bridge, "B013-S-T02b", "The addends are 100 and 200", "The addends are 1 and 2")
        with self.assertRaisesRegex(AssertionError, "English addend roles"):
            validate_b013(self.target, self.bridge)

    def test_telugu_digit_word_mapping_cannot_hide_behind_correct_strong_answer(self):
        self.mutate(self.bridge, "B013-S-T02a", "మొదటి సంఖ్య 21", "మొదటి సంఖ్య 12")
        with self.assertRaisesRegex(AssertionError, "operand/reading explanation"):
            validate_b013(self.target, self.bridge)

    def test_source_solution_cannot_append_evaluation(self):
        self.node(self.bridge, "B013-S-T01a").find(XH + "p").tail = "8 + 4 = 12"
        with self.assertRaisesRegex(AssertionError, "substituted with evaluation"):
            validate_b013(self.target, self.bridge)

    def test_missing_source_solution_id_rejected(self):
        self.node(self.bridge, "B013-S-T02b").set("id", "removed-source-part")
        with self.assertRaisesRegex(AssertionError, "Missing B013 node"):
            validate_b013(self.target, self.bridge)

    def test_diagnostic_same_value_operand_swap_rejected(self):
        self.mutate(self.bridge, "B013-D01", "6 + 2", "2 + 6")
        with self.assertRaisesRegex(AssertionError, "target pair"):
            validate_b013(self.target, self.bridge)

    def test_diagnostic_word_request_cannot_become_value_request(self):
        self.mutate(self.bridge, "B013-D01", "మాటల్లో చదవండి", "విలువను కనుక్కోండి")
        with self.assertRaisesRegex(AssertionError, "requested answer type"):
            validate_b013(self.target, self.bridge)

    def test_recheck_word_request_cannot_become_value_request(self):
        self.mutate(self.bridge, "B013-R01", "మాటల్లో చదవండి", "విలువను కనుక్కోండి")
        with self.assertRaisesRegex(AssertionError, "requested answer type"):
            validate_b013(self.target, self.bridge)

    def test_recheck_zero_swapped_to_other_operand_rejected(self):
        self.mutate(self.bridge, "B013-R01", "9 + 0", "0 + 9")
        with self.assertRaisesRegex(AssertionError, "target pair"):
            validate_b013(self.target, self.bridge)

    def test_zero_stays_in_displayed_word_answer(self):
        self.mutate(self.bridge, "B013-S-R01", "తొమ్మిది ప్లస్ శూన్యం", "తొమ్మిది")
        with self.assertRaisesRegex(AssertionError, "Telugu reading"):
            validate_b013(self.target, self.bridge)

    def test_zero_addend_value_unchanged_explanation_guard(self):
        self.mutate(self.bridge, "B013-S-R01", "విలువ మారదు", "విలువ పెరుగుతుంది")
        with self.assertRaisesRegex(AssertionError, "zero/operand-result"):
            validate_b013(self.target, self.bridge)

    def test_same_nine_value_does_not_allow_operand_result_role_swap(self):
        self.mutate(self.bridge, "B013-S-R01", "కుడివైపు 9 ఫలితం", "ఎడమవైపు 9 ఫలితం")
        with self.assertRaisesRegex(AssertionError, "zero/operand-result"):
            validate_b013(self.target, self.bridge)

    def test_addend_cannot_be_replaced_by_computed_result(self):
        self.mutate(self.bridge, "B013-S-D01", "కలిపే సంఖ్యలు 6, 2", "కలిపే సంఖ్యలు 6, 8")
        with self.assertRaisesRegex(AssertionError, "Telugu addend roles"):
            validate_b013(self.target, self.bridge)

    def test_expression_label_cannot_be_equation_even_with_correct_arithmetic_nearby(self):
        self.mutate(self.bridge, "B013-S-D02", "5 + 1 ఒక expression", "5 + 1 ఒక equation")
        with self.assertRaisesRegex(AssertionError, "label contradicts"):
            validate_b013(self.target, self.bridge)

    def test_equation_label_cannot_be_expression(self):
        self.mutate(self.bridge, "B013-S-R02", "2 + 5 = 7 ఒక equation", "2 + 5 = 7 ఒక expression")
        with self.assertRaisesRegex(AssertionError, "label contradicts"):
            validate_b013(self.target, self.bridge)

    def test_expression_cannot_acquire_equal_sign(self):
        self.mutate(self.bridge, "B013-S-D02", "5 + 1 ఒక expression", "5 + 1 = 6 ఒక expression")
        with self.assertRaisesRegex(AssertionError, "label contradicts"):
            validate_b013(self.target, self.bridge)

    def test_equation_cannot_lose_equal_sign(self):
        self.mutate(self.bridge, "B013-S-R02", "2 + 5 = 7 ఒక equation", "2 + 5 ఒక equation")
        with self.assertRaisesRegex(AssertionError, "label contradicts"):
            validate_b013(self.target, self.bridge)

    def test_classification_same_total_wrong_target_rejected(self):
        self.mutate(self.bridge, "B013-S-D02", "5 + 1 = 6 ఒక equation", "4 + 2 = 6 ఒక equation")
        with self.assertRaisesRegex(AssertionError, "classified operands"):
            validate_b013(self.target, self.bridge)

    def test_english_classification_cannot_conflict_with_telugu(self):
        self.mutate(self.bridge, "B013-S-D02", "5 + 1 is an expression", "5 + 1 is an equation")
        with self.assertRaisesRegex(AssertionError, "English classification contradicts"):
            validate_b013(self.target, self.bridge)

    def test_question_equation_answer_rejected_independent_of_solution(self):
        self.mutate(self.bridge, "B013-D02", "5 + 1 = 6", "5 + 1 = 7")
        with self.assertRaisesRegex(AssertionError, "Incorrect B013 addition"):
            validate_b013(self.target, self.bridge)

    def test_unscored_support_equation_also_recomputed(self):
        self.mutate(self.bridge, "B013-K2", "3 + 4 = 7", "3 + 4 = 8")
        with self.assertRaisesRegex(AssertionError, "Incorrect B013 addition"):
            validate_b013(self.target, self.bridge)

    def test_partial_correct_equation_cannot_hide_extra_chain(self):
        self.mutate(self.bridge, "B013-K2", "3 + 4 = 7", "3 + 4 = 7 = 8")
        with self.assertRaisesRegex(AssertionError, "Unsupported/changed B013 relation"):
            validate_b013(self.target, self.bridge)

    def test_reading_plus_role_is_not_number_role(self):
        self.mutate(self.bridge, "B013-K1", "ఇది ఒక సంఖ్య కాదు", "ఇది ఒక సంఖ్య")
        with self.assertRaisesRegex(AssertionError, "role-guide explanation"):
            validate_b013(self.target, self.bridge)

    def test_role_table_result_cannot_move_into_addend_cell(self):
        guide = self.node(self.bridge, "B013-K1")
        rows = guide.findall(".//" + XH + "tbody/" + XH + "tr")
        rows[0][0].text, rows[3][0].text = rows[3][0].text, rows[0][0].text
        with self.assertRaisesRegex(AssertionError, "role-guide objects"):
            validate_b013(self.target, self.bridge)

    def test_skill_route_to_wrong_existing_recheck_rejected(self):
        route = self.node(self.bridge, "B013-route")
        next(e for e in route.iter(XH + "a") if e.get("href") == "#B013-R01").set("href", "#B013-R02")
        with self.assertRaisesRegex(AssertionError, "routing changed"):
            validate_b013(self.target, self.bridge)

    def test_duplicate_bridge_id_rejected(self):
        self.node(self.bridge, "B013-S-T01b").set("id", "B013-S-T01a")
        with self.assertRaisesRegex(AssertionError, "Duplicate"):
            validate_b013(self.target, self.bridge)


if __name__ == "__main__":
    unittest.main()
