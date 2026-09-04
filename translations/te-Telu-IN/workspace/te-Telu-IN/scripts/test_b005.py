"""B005 source, actual-answer, zero-group, currency and corruption tests."""
import copy
import unittest
import xml.etree.ElementTree as ET

from build_unit import (BASE, asset_map, localize, math_signature,
                        structural_signature, unit_inputs)
from inspect_source import slots
from writing_checks import english_value, validate_b005


class WritingTests(unittest.TestCase):
    def setUp(self):
        self.source, self.meta, self.catalog = unit_inputs("TE-B005")
        self.target = localize(self.source, self.catalog, asset_map("TE-B005"))
        self.bridge = ET.parse(BASE / "translations/TE-B005.bridge.xhtml").getroot()

    def node(self, root, ident):
        return next(e for e in root.iter() if e.get("id") == ident)

    def mutate(self, root, ident, before, after):
        node = self.node(root, ident)
        for e in node.iter():
            for key in ("text", "tail"):
                value = getattr(e, key)
                if value and before in value:
                    setattr(e, key, value.replace(before, after, 1))
                    return
        self.fail("Mutation did not touch actual XML: " + before)

    def test_source_math_and_slots(self):
        self.assertEqual(len(list(self.source.iter())), 97)
        self.assertEqual(len(list(slots(self.source))), 55)
        self.assertEqual(len(self.catalog["translations"]), 40)
        self.assertEqual(math_signature(self.source), math_signature(self.target))
        self.assertEqual(structural_signature(self.source), structural_signature(self.target))

    def test_actual_answers_and_all_equation_sides(self):
        self.assertEqual(validate_b005(self.target, self.bridge), 16)

    def test_exact_english_grammar(self):
        for name, value in [("zero", 0), ("seventy-three thousand", 73000),
                            ("nine billion, two hundred forty-six million, seventy-three thousand, one hundred eighty-nine", 9246073189),
                            ("two billion, five thousand", 2000005000)]:
            self.assertEqual(english_value(name), value)
        for name in ["seventy-three thousand, zero", "nine billions", "one hundred and one",
                     "one million, one billion", "one thousand, one thousand"]:
            with self.subTest(name=name), self.assertRaises(AssertionError):
                english_value(name)

    def test_source_written_name_mutation_rejected(self):
        self.mutate(self.target, "fs-id2149876", "eight hundred nine thousand", "eight hundred ninety thousand")
        with self.assertRaisesRegex(AssertionError, "Source English name changed"):
            validate_b005(self.target, self.bridge)

    def test_source_math_answer_zero_mutation_rejected(self):
        self.mutate(self.target, "fs-id1374355", "9,246,073,189", "9,246,730,189")
        with self.assertRaisesRegex(AssertionError, "Source answer changed"):
            validate_b005(self.target, self.bridge)

    def test_all_four_source_try_answers_reject_corruption(self):
        for ident, old, new in [("fs-id4163187", "53,809,051", "53,809,501"),
                                ("fs-id1885399", "2,022,714,466", "2,220,714,466"),
                                ("fs-id865214", "34,000,000", "34,000"),
                                ("fs-id1395137", "204,000,000", "24,000,000")]:
            with self.subTest(ident=ident):
                target = copy.deepcopy(self.target)
                self.mutate(target, ident, old, new)
                with self.assertRaises(AssertionError):
                    validate_b005(target, self.bridge)

    def test_017_wrong_742_alt_rejected(self):
        node = self.node(self.target, "fs-id2903601")
        node.set("alt", node.get("alt").replace("073", "742"))
        with self.assertRaisesRegex(AssertionError, "Source017"):
            validate_b005(self.target, self.bridge)

    def test_source_currency_symbol_mutation_rejected(self):
        self.mutate(self.target, "fs-id2319817", "$77,000,000,000.", "₹77,000,000,000.")
        with self.assertRaisesRegex(AssertionError, "budget answer/currency"):
            validate_b005(self.target, self.bridge)

    def test_source_measurement_unit_mutation_rejected(self):
        self.mutate(self.target, "fs-id865214", "మైళ్లు", "కిలోమీటర్లు")
        with self.assertRaisesRegex(AssertionError, "measurement answer/unit"):
            validate_b005(self.target, self.bridge)

    def test_practice_name_mutation_rejected(self):
        self.mutate(self.bridge, "B005-R01", "thirty-seven thousand", "seventy-three thousand")
        with self.assertRaisesRegex(AssertionError, "Practice name/unit"):
            validate_b005(self.target, self.bridge)

    def test_practice_zero_group_width_mutation_rejected(self):
        self.mutate(self.bridge, "B005-S-D01", "6 | 024 | 009", "6 | 24 | 009")
        with self.assertRaisesRegex(AssertionError, "Zero-group"):
            validate_b005(self.target, self.bridge)

    def test_practice_prose_answer_not_hidden_by_correct_equality(self):
        self.mutate(self.bridge, "B005-S-D01", "జవాబు 6,024,009", "జవాబు 6,024,010")
        with self.assertRaisesRegex(AssertionError, "Wrong B005 answer numeral"):
            validate_b005(self.target, self.bridge)

    def test_stated_answer_cannot_be_one_of_its_contributions(self):
        self.mutate(self.bridge, "B005-S-D01", "జవాబు 6,024,009", "జవాబు 6,000,000")
        with self.assertRaisesRegex(AssertionError, "Wrong B005 answer numeral"):
            validate_b005(self.target, self.bridge)

    def test_accessible_word_digit_mapping_mutation_rejected(self):
        node = self.node(self.target, "fs-id2668978")
        node.set("alt", node.get("alt").replace("401 కు", "410 కు"))
        with self.assertRaisesRegex(AssertionError, "Accessible word/digit mapping"):
            validate_b005(self.target, self.bridge)

    def test_all_twelve_solution_groups_reject_corruption(self):
        values = {"D01": "6 | 024 | 009", "D02": "3 | 042 | 005 | 800",
                  "D03": "2 | 000 | 005 | 000", "D04": "5 | 000 | 000",
                  "R01": "8 | 037 | 006", "R02": "4 | 053 | 007 | 900",
                  "R03": "6 | 000 | 007 | 000", "R04": "18 | 000 | 000",
                  "fs-id2646708": "53 | 809 | 051", "fs-id2202956": "2 | 022 | 714 | 466",
                  "fs-id1485641": "34 | 000 | 000", "fs-id2133886": "204 | 000 | 000"}
        for ident, original in values.items():
            with self.subTest(ident=ident):
                bridge = copy.deepcopy(self.bridge)
                changed = original.rsplit(" | ", 1)[0] + " | 999"
                self.mutate(bridge, "B005-S-" + ident, original, changed)
                with self.assertRaisesRegex(AssertionError, "Zero-group"):
                    validate_b005(self.target, bridge)

    def test_actual_chained_middle_expression_mutation_rejected(self):
        self.mutate(self.bridge, "B005-worked-first", "53,000,000 + 809,000 + 51", "53,000,000 + 890,000 + 51")
        with self.assertRaisesRegex(AssertionError, "Incorrect bridge equality"):
            validate_b005(self.target, self.bridge)

    def test_actual_chained_final_answer_mutation_rejected(self):
        self.mutate(self.bridge, "B005-worked-second", "= 2,022,714,466", "= 2,022,714,467")
        with self.assertRaisesRegex(AssertionError, "Incorrect bridge equality"):
            validate_b005(self.target, self.bridge)

    def test_actual_coefficient_mutation_rejected(self):
        self.mutate(self.bridge, "B005-worked-first", "809 × 1,000", "890 × 1,000")
        with self.assertRaisesRegex(AssertionError, "Incorrect bridge equality"):
            validate_b005(self.target, self.bridge)

    def test_comparison_indian_comma_value_mutation_rejected(self):
        self.mutate(self.bridge, "B005-conventions", "1,000,000 = 10,00,000", "1,000,000 = 1,00,000")
        with self.assertRaisesRegex(AssertionError, "Incorrect bridge equality"):
            validate_b005(self.target, self.bridge)

    def test_currency_and_measurement_bridge_mutations_rejected(self):
        for ident, old, new in [("B005-S-D03", "$2,000,005,000", "₹2,000,005,000"),
                                ("B005-S-R04", "18,000,000 మైళ్లు", "18,000,000 కిలోమీటర్లు"),
                                ("B005-S-fs-id2133886", "204,000,000 పౌండ్లు", "204,000,000 కిలోగ్రాములు")]:
            with self.subTest(ident=ident):
                bridge = copy.deepcopy(self.bridge)
                self.mutate(bridge, ident, old, new)
                with self.assertRaisesRegex(AssertionError, "unit changed"):
                    validate_b005(self.target, bridge)

    def test_missing_source_solution_rejected(self):
        self.node(self.bridge, "B005-S-fs-id2646708").set("id", "removed")
        with self.assertRaisesRegex(AssertionError, "Missing B005 node"):
            validate_b005(self.target, self.bridge)

    def test_missing_actual_equation_rejected(self):
        self.mutate(self.bridge, "B005-worked-first", "53 × 1,000,000 + 809 × 1,000 + 51 = 53,000,000 + 809,000 + 51 = 53,809,051", "తనిఖీ")
        with self.assertRaises(AssertionError):
            validate_b005(self.target, self.bridge)


if __name__ == "__main__":
    unittest.main()
