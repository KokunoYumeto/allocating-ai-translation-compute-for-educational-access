"""Regressions for the recap's actual values, zero groups and cross-unit links."""
import unittest
import xml.etree.ElementTree as ET
from build_unit import BASE, unit_inputs, asset_map, localize, validate_reader_link
from recap_checks import validate_b007


class RecapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source, _, catalog = unit_inputs("TE-B007")
        cls.target = localize(source, catalog, asset_map("TE-B007"))
        cls.raw = (BASE / "translations/TE-B007.bridge.xhtml").read_text(encoding="utf-8")

    def test_final_actual_bridge(self):
        self.assertEqual(validate_b007(self.target, ET.fromstring(self.raw))["equalities"], 7)

    def test_corrupted_values_are_rejected(self):
        for before, after in [
            ("seventy-eight thousand", "seventy-nine thousand"),
            ("6 | 004 | 020", "6 | 040 | 020"),
            ("194 = 5,278,194", "194 = 5,278,195"),
            ("6,004,020", "6,004,200"),
            ("దగ్గరి వందలకు", "దగ్గరి వేలకు"),
            ("వందల అంకె 1;", "వందల అంకె 2;"),
            ("పదుల అంకె 9.", "పదుల అంకె 1."),
            ("5,278,200", "5,278,100"),
            ("= 806", "= 805"),
            ("9 + 1 = 10", "9 + 1 = 11"),
            ("TE-B006.html#B006-recheck", "TE-B005.html#B005-recheck"),
        ]:
            with self.subTest(before=before):
                self.assertIn(before, self.raw)
                with self.assertRaises(AssertionError):
                    validate_b007(self.target, ET.fromstring(self.raw.replace(before, after)))

    def test_existing_cross_unit_fragments_resolve(self):
        for node in ET.fromstring(self.raw).iter():
            if node.get("href", "").startswith("TE-"):
                validate_reader_link(node.get("href"), [])

    def test_missing_fragment_fails_even_when_file_exists(self):
        with self.assertRaises(AssertionError):
            validate_reader_link("TE-B006.html#missing-anchor", [])

    def test_missing_file_fails(self):
        with self.assertRaises(AssertionError):
            validate_reader_link("TE-B999.html#B999-recheck", [])

    def test_outside_base_fails(self):
        with self.assertRaises(AssertionError):
            validate_reader_link("../../AGENTS.md", [])


if __name__ == "__main__":
    unittest.main()
