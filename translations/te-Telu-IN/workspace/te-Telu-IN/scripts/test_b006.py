"""B006 exact-integer, source, localized-answer and corruption checks."""
from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
import copy
import unittest
import xml.etree.ElementTree as ET

from rounding_checks import (controlling_digit, round_whole_half_up,
                             validate_english_rounding_source,
                             validate_rounding_structure,
                             validate_rounding_target, validate_b006)

BASE = Path(__file__).resolve().parents[1]


class _RenderedSource(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = Counter()
        self.tables = {}
        self.table = None
        self.links = []
        self.anchor = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids[attrs["id"]] += 1
        if tag == "table":
            assert self.table is None
            self.table = attrs["id"]
            self.tables[self.table] = []
        elif tag == "tr" and self.table is not None:
            self.tables[self.table].append(0)
        elif tag in {"td", "th"} and self.table is not None:
            self.tables[self.table][-1] += 1
        elif tag == "a":
            self.anchor = [attrs.get("href"), []]

    def handle_data(self, data):
        if self.anchor is not None:
            self.anchor[1].append(data)

    def handle_endtag(self, tag):
        if tag == "table":
            self.table = None
        elif tag == "a" and self.anchor is not None:
            self.links.append((self.anchor[0], " ".join("".join(self.anchor[1]).split())))
            self.anchor = None


class RoundingArithmeticTests(unittest.TestCase):
    def test_halfway_is_not_ties_to_even(self):
        for n, unit, expected in [(75, 10, 80), (85, 10, 90), (250, 100, 300),
                                   (24500, 1000, 25000), (9999500, 1000, 10000000)]:
            with self.subTest(n=n, unit=unit):
                self.assertEqual(round_whole_half_up(n, unit), expected)

    def test_zero_five_boundary_and_carry(self):
        for n, unit, expected in [(0, 10, 0), (4000, 1000, 4000),
                                   (147032, 1000, 147000), (949, 100, 900),
                                   (950, 100, 1000), (999, 10, 1000),
                                   (99999, 1000, 100000), (29504, 1000, 30000)]:
            with self.subTest(n=n, unit=unit):
                self.assertEqual(round_whole_half_up(n, unit), expected)
        self.assertEqual(controlling_digit(147032, 1000), 0)
        self.assertEqual(controlling_digit(29504, 1000), 5)
        self.assertEqual(controlling_digit(3978, 100), 7)

    def test_large_integers_no_float_loss(self):
        self.assertEqual(round_whole_half_up(10**40 + 5, 10), 10**40 + 10)
        self.assertEqual(round_whole_half_up(10**40 + 4, 10), 10**40)
        self.assertEqual(round_whole_half_up(987654321, 1), 987654321)

    def test_nearest_multiple_properties_exhaustively(self):
        for unit in (10, 100, 1000):
            for number in range(10001):
                result = round_whole_half_up(number, unit)
                self.assertEqual(result % unit, 0)
                self.assertLessEqual(2 * abs(result - number), unit)
                if 2 * (number % unit) == unit:
                    self.assertGreater(result, number)

    def test_invalid_domains_rejected(self):
        for n, unit in [(-1, 10), (1.5, 10), (True, 10), (1, 0),
                        (1, 20), (1, 100.0), (1, True), (1, -10)]:
            with self.subTest(n=n, unit=unit), self.assertRaises(ValueError):
                round_whole_half_up(n, unit)

    def test_direct_rounding_differs_from_double_rounding(self):
        self.assertEqual(round_whole_half_up(149, 100), 100)
        self.assertEqual(round_whole_half_up(round_whole_half_up(149, 10), 100), 200)

    def test_actual_frozen_source_seventeen_cases(self):
        source = ET.parse(BASE / "sources/TE-B006.en.cnxml").getroot()
        self.assertEqual(validate_english_rounding_source(source), 17)

    def test_five_source_table_exceptions(self):
        source = ET.parse(BASE / "sources/TE-B006.en.cnxml").getroot()
        self.assertEqual(len(validate_rounding_structure(source)), 104)


class _LocalizedFixture(unittest.TestCase):
    def setUp(self):
        from build_unit import unit_inputs, localize, asset_map
        self.source, self.meta, self.catalog = unit_inputs("TE-B006")
        self.target = localize(self.source, self.catalog, asset_map("TE-B006"))

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


class RoundingTargetTests(_LocalizedFixture):

    def test_all_seventeen_actual_localized_cases(self):
        self.assertEqual(validate_rounding_target(self.target), 17)

    def test_exact_source_math_and_structure(self):
        from build_unit import math_signature, structural_signature
        from inspect_source import slots
        self.assertEqual(len(list(slots(self.source))), 258)
        self.assertEqual(math_signature(self.source), math_signature(self.target))
        self.assertEqual(structural_signature(self.source), structural_signature(self.target))

    def test_equal_answer_different_target_3978_alt_rejected(self):
        self.assertEqual(round_whole_half_up(3978, 100), round_whole_half_up(3978, 1000))
        node = self.node(self.target, "eip-id1168289428689")
        node.set("alt", node.get("alt").replace("దగ్గరి వందలకు", "దగ్గరి వేలకు"))
        with self.assertRaisesRegex(AssertionError, "target place"):
            validate_rounding_target(self.target)

    def test_equal_answer_different_target_29504_alt_rejected(self):
        self.assertEqual(round_whole_half_up(29504, 1000), round_whole_half_up(29504, 10000))
        node = self.node(self.target, "eip-id1168288313851")
        node.set("alt", node.get("alt").replace("దగ్గరి వేలకు", "దగ్గరి పది వేలకు"))
        with self.assertRaisesRegex(AssertionError, "target place"):
            validate_rounding_target(self.target)

    def test_wrong_target_in_worked_statement_rejected(self):
        self.mutate(self.target, "eip-379", "దగ్గరి వందలకు", "దగ్గరి వేలకు")
        with self.assertRaisesRegex(AssertionError, "target place"):
            validate_rounding_target(self.target)

    def test_wrong_first_target_position_rejected(self):
        self.mutate(self.target, "eip-596", "వేల స్థానాన్ని", "పది వేల స్థానాన్ని")
        with self.assertRaisesRegex(AssertionError, "selected position"):
            validate_rounding_target(self.target)

    def test_worked_question_number_mutation_rejected(self):
        self.mutate(self.target, "fs-id2351315", "3,978", "3,798")
        with self.assertRaisesRegex(AssertionError, "worked input"):
            validate_rounding_target(self.target)

    def test_corrected_alt_carry_digit_mutation_rejected(self):
        node = self.node(self.target, "eip-id1168289428689")
        node.set("alt", node.get("alt").replace("3 కు 1", "3 కు 2"))
        with self.assertRaisesRegex(AssertionError, "carry/digits"):
            validate_rounding_target(self.target)

    def test_zero_controlling_digit_must_not_be_skipped(self):
        self.mutate(self.target, "eip-695", "అంకె 0", "అంకె 3")
        with self.assertRaisesRegex(AssertionError, "controlling digit"):
            validate_rounding_target(self.target)

    def test_five_must_remain_in_upward_branch(self):
        self.mutate(self.target, "fs-id1545266", "సమానమైన లేదా పెద్ద", "పెద్ద")
        with self.assertRaisesRegex(AssertionError, "tie boundary"):
            validate_rounding_target(self.target)

    def test_target_nine_does_not_always_carry(self):
        self.mutate(self.target, "eip-id1168287215567", "9 అయి, పైకి సవరించవలసి", "9 అయి, కిందికి సవరించవలసి")
        with self.assertRaisesRegex(AssertionError, "carry condition"):
            validate_rounding_target(self.target)

    def test_all_six_try_answer_mutations_rejected(self):
        from rounding_checks import TRY_CASES
        for _, _, answer, number, unit in TRY_CASES:
            with self.subTest(answer=answer):
                target = copy.deepcopy(self.target)
                self.node(target, answer).text = f"{round_whole_half_up(number, unit) + unit:,}"
                with self.assertRaisesRegex(AssertionError, "Try It answer"):
                    validate_rounding_target(target)

    def test_wrong_declared_columns_rejected(self):
        from rounding_checks import CN
        self.node(self.target, "eip-379").find(CN + "tgroup").set("cols", "2")
        with self.assertRaisesRegex(AssertionError, "Declared source columns"):
            validate_rounding_target(self.target)

    def test_worked_answer_commas_not_just_value(self):
        self.mutate(self.target, "eip-379", "రాస్తే 4,000", "రాస్తే 4,00,0")
        with self.assertRaisesRegex(AssertionError, "comma grouping"):
            validate_rounding_target(self.target)


class RoundingBridgeTests(_LocalizedFixture):
    def setUp(self):
        super().setUp()
        self.bridge = ET.parse(BASE / "translations/TE-B006.bridge.xhtml").getroot()

    def test_actual_bridge_cases_distances_and_equalities(self):
        self.assertEqual(validate_b006(self.target, self.bridge), {
            "canonical_cases": 17, "entry_recheck_cases": 12,
            "source_bridge_solutions": 6, "bridge_equalities": 24})

    def test_practice_target_changed_same_given_number(self):
        self.mutate(self.bridge, "B006-D01", "దగ్గరి వేలకు", "దగ్గరి వందలకు")
        with self.assertRaisesRegex(AssertionError, "target place"):
            validate_b006(self.target, self.bridge)

    def test_solution_target_label_changed(self):
        self.mutate(self.bridge, "B006-S-D01", "లక్ష్యం వేల స్థానం", "లక్ష్యం వందల స్థానం")
        with self.assertRaisesRegex(AssertionError, "target/neighbor place"):
            validate_b006(self.target, self.bridge)

    def test_zero_neighbor_skipping_rejected(self):
        self.mutate(self.bridge, "B006-S-D01", "వందల అంకె 0", "వందల అంకె 8")
        with self.assertRaisesRegex(AssertionError, "target/controlling digit"):
            validate_b006(self.target, self.bridge)

    def test_bridge_result_commas_not_just_value(self):
        self.mutate(self.bridge, "B006-S-D01", "భర్తీ చేస్తే 46,000", "భర్తీ చేస్తే 4,60,00")
        with self.assertRaisesRegex(AssertionError, "comma grouping"):
            validate_b006(self.target, self.bridge)

    def test_all_twelve_primary_results_reject_corruption(self):
        phrases = {"D01": "భర్తీ చేస్తే 46,000", "D02": "భర్తీ చేస్తే 46,100",
                   "D03": "పెద్ద గుణిజం 250", "D04": "పైకి సవరించి 2,500",
                   "D05": "రాస్తే 10,000", "D06": "భర్తీ చేస్తే 99,000",
                   "R01": "ఫలితం 73,000", "R02": "భర్తీ చేస్తే 73,100",
                   "R03": "నియమంతో 370", "R04": "పైకి సవరించి 6,800",
                   "R05": "రాస్తే 100,000", "R06": "భర్తీ చేస్తే 9,900"}
        for case, phrase in phrases.items():
            with self.subTest(case=case):
                bridge = copy.deepcopy(self.bridge)
                self.mutate(bridge, "B006-S-" + case, phrase, phrase.rsplit(" ", 1)[0] + " 1")
                with self.assertRaisesRegex(AssertionError, "rounded answer"):
                    validate_b006(self.target, bridge)

    def test_correct_distance_does_not_hide_wrong_result(self):
        self.mutate(self.bridge, "B006-S-D03", "పెద్ద గుణిజం 250", "పెద్ద గుణిజం 240")
        with self.assertRaisesRegex(AssertionError, "rounded answer"):
            validate_b006(self.target, self.bridge)

    def test_distance_list_mutation_rejected(self):
        self.mutate(self.bridge, "B006-S-D02", "దూరాలు 82, 18", "దూరాలు 82, 28")
        with self.assertRaisesRegex(AssertionError, "distance pair"):
            validate_b006(self.target, self.bridge)

    def test_actual_distance_equation_mutation_rejected(self):
        self.mutate(self.bridge, "B006-S-D04", "2,500 − 2,451 = 49", "2,500 − 2,451 = 51")
        with self.assertRaisesRegex(AssertionError, "distance equation"):
            validate_b006(self.target, self.bridge)

    def test_above_midpoint_value_mutation_rejected(self):
        self.mutate(self.bridge, "B006-S-R04", "మధ్య విలువ 6,750", "మధ్య విలువ 6,752")
        with self.assertRaisesRegex(AssertionError, "above-midpoint"):
            validate_b006(self.target, self.bridge)

    def test_no_carry_despite_target_nine(self):
        self.mutate(self.bridge, "B006-S-D06", "బదిలీ లేదు", "బదిలీ ఉంది")
        with self.assertRaisesRegex(AssertionError, "no-carry"):
            validate_b006(self.target, self.bridge)

    def test_all_nines_carry_equation_rejected(self):
        self.mutate(self.bridge, "B006-S-R05", "99,900 + 100 = 100,000", "99,900 + 100 = 99,000")
        with self.assertRaisesRegex(AssertionError, "all-nine carry"):
            validate_b006(self.target, self.bridge)

    def test_new_leading_carry_digit_rejected(self):
        self.mutate(self.bridge, "B006-S-D05", "పది వేల స్థానంలో కొత్త 1", "పది వేల స్థానంలో కొత్త 0")
        with self.assertRaisesRegex(AssertionError, "leading carry digit"):
            validate_b006(self.target, self.bridge)

    def test_exact_multiple_result_mutation_rejected(self):
        self.mutate(self.bridge, "B006-zero-exact", "సవరించినా 0 గానే", "సవరించినా 10 గానే")
        with self.assertRaisesRegex(AssertionError, "Exact-multiple"):
            validate_b006(self.target, self.bridge)

    def test_double_rounding_must_not_equal_direct_result(self):
        self.mutate(self.bridge, "B006-round-once", "సవరించితే 200", "సవరించితే 100")
        with self.assertRaisesRegex(AssertionError, "Direct/double-rounding"):
            validate_b006(self.target, self.bridge)

    def test_all_six_source_solution_distance_mutations_rejected(self):
        from rounding_checks import TRY_CASES
        for exercise, _, _, number, unit in TRY_CASES:
            lower = number // unit * unit
            original = f"{number:,} − {lower:,} = {number-lower:,}"
            with self.subTest(exercise=exercise):
                bridge = copy.deepcopy(self.bridge)
                self.mutate(bridge, "B006-S-" + exercise, original, original + "1")
                with self.assertRaises(AssertionError):
                    validate_b006(self.target, bridge)

    def test_3978_guide_target_corruption_rejected(self):
        raw = ET.tostring(self.bridge, encoding="unicode")
        before = "3,978 ను దగ్గరి వందలకు"
        self.assertIn(before, raw)
        bridge = ET.fromstring(raw.replace(before, "3,978 ను దగ్గరి వేలకు", 1))
        with self.assertRaisesRegex(AssertionError, "target place"):
            validate_b006(self.target, bridge)

    def test_source_solution_missing_rejected(self):
        self.node(self.bridge, "B006-S-fs-id1312230").set("id", "removed")
        with self.assertRaisesRegex(AssertionError, "Missing rounding node"):
            validate_b006(self.target, self.bridge)

    def test_support_carry_arithmetic_mutation_rejected(self):
        raw = ET.tostring(self.bridge, encoding="unicode")
        self.assertIn("9 + 1 = 10", raw)
        bridge = ET.fromstring(raw.replace("9 + 1 = 10", "9 + 1 = 11", 1))
        with self.assertRaisesRegex(AssertionError, "Incorrect rounding equality"):
            validate_b006(self.target, bridge)


class RoundingRenderTests(_LocalizedFixture):
    def render_checked(self, english=False):
        from build_unit import render, asset_map
        root = self.source if english else self.target
        parser = _RenderedSource()
        parser.feed(render(root, asset_map("TE-B006"), "en-" if english else "", english))
        parser.close()
        return root, parser

    def test_rendered_five_two_cell_tables_and_media_ids(self):
        from rounding_checks import CN, TABLE_CASES
        for english in (False, True):
            with self.subTest(english=english):
                source, rendered = self.render_checked(english)
                prefix = "en-" if english else ""
                expected = {prefix + ident: [2] * count for ident, _, _, count in TABLE_CASES}
                self.assertEqual(rendered.tables, expected)
                media_ids = [prefix + e.get("id") for e in source.iter(CN + "media")]
                self.assertEqual(len(media_ids), 23)
                self.assertTrue(all(rendered.ids[ident] == 1 for ident in media_ids))
                expected_ids = {prefix + e.get("id") for e in source.iter() if e.get("id")}
                self.assertEqual(set(rendered.ids), expected_ids)
                self.assertTrue(all(count == 1 for count in rendered.ids.values()))

    def test_both_registered_url_labels_and_hrefs_preserved(self):
        from rounding_checks import CN
        from naming_checks import text_of
        for english in (False, True):
            with self.subTest(english=english):
                source, rendered = self.render_checked(english)
                expected = [(node.get("url"), text_of(node)) for node in source.iter(CN + "link") if node.get("url")]
                self.assertEqual(len(expected), 2)
                actual = [link for link in rendered.links if link[0].startswith("https:")]
                self.assertEqual(actual, expected)

    def test_unregistered_and_unsafe_url_rejected(self):
        from build_unit import render, asset_map
        from rounding_checks import CN
        original = next(e for e in self.target.iter(CN + "link") if e.get("url"))
        for url in ["https://example.invalid/unregistered", "javascript:alert(1)",
                    "data:text/html,unsafe", "http://www.openstax.org/l/24detplaceval"]:
            with self.subTest(url=url):
                link = copy.deepcopy(original)
                link.set("url", url)
                with self.assertRaises(AssertionError):
                    render(link, asset_map("TE-B006"))

    def test_structurally_skipped_container_id_cannot_disappear(self):
        from build_unit import render, asset_map
        from rounding_checks import CN
        entry = self.node(self.target, "eip-379").find(".//" + CN + "entry")
        entry.set("id", "must-not-disappear")
        with self.assertRaises(AssertionError):
            render(self.target, asset_map("TE-B006"))

if __name__ == "__main__":
    unittest.main()
