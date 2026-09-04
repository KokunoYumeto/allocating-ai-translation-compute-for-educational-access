import unittest
import xml.etree.ElementTree as ET
from build_unit import BASE,CN,MATH,unit_inputs,asset_map,localize,math_signature,structural_signature
from naming_checks import english_name,validate_b004,verify_numeric_equalities
from inspect_source import slots


class NamingTests(unittest.TestCase):
    def setUp(self):
        self.source,self.meta,self.catalog=unit_inputs("TE-B004")
        self.target=localize(self.source,self.catalog,asset_map("TE-B004"))
        self.bridge=ET.parse(BASE/"translations/TE-B004.bridge.xhtml").getroot()

    def test_source_math_and_all_slots(self):
        self.assertEqual(len(list(self.source.iter())),112)
        self.assertEqual(len(list(slots(self.source))),60)
        self.assertEqual(len(self.catalog["translations"]),49)
        self.assertEqual(sum(bool(e.get("id")) for e in self.source.iter()),53)
        self.assertEqual(len(list(self.source.iter(MATH+"math"))),9)
        self.assertEqual(math_signature(self.source),math_signature(self.target))
        self.assertEqual(structural_signature(self.source),structural_signature(self.target))

    def test_actual_names_and_equalities(self):
        self.assertEqual(validate_b004(self.target,self.bridge),11)

    def test_english_name_boundaries(self):
        for value,name in [(0,"zero"),(19,"nineteen"),(20,"twenty"),(31,"thirty-one"),(100,"one hundred"),(710,"seven hundred ten"),(2000305,"two million, three hundred five"),(1000000000000,"one trillion")]:
            self.assertEqual(english_name(value),name)

    def test_source_name_digit_mutation_rejected(self):
        node=next(e for e in self.target.iter() if e.get("id")=="fs-id1469854")
        node.text=node.text.replace("nine trillion","eight trillion")
        with self.assertRaisesRegex(AssertionError,"Canonical English name"):
            validate_b004(self.target,self.bridge)

    def test_leading_zero_deletion_rejected(self):
        raw=ET.tostring(self.bridge,encoding="unicode").replace("9 | 258 | 137 | 904 | 061","9 | 258 | 137 | 904 | 61")
        with self.assertRaisesRegex(AssertionError,"Zero-group"):
            validate_b004(self.target,ET.fromstring(raw))

    def test_arithmetic_mutation_rejected(self):
        with self.assertRaisesRegex(AssertionError,"Incorrect bridge equality"):
            verify_numeric_equalities("24,000,000 + 315,000 + 608 = 24,315,609",1)

    def test_missing_recheck_solution_rejected(self):
        raw=ET.tostring(self.bridge,encoding="unicode").replace('id="B004-S-R04"','id="wrong"')
        with self.assertRaises(KeyError):
            validate_b004(self.target,ET.fromstring(raw))

    def test_source_column_declaration_preserved(self):
        table=next(self.target.iter(CN+"table"))
        self.assertEqual(table.find(CN+"tgroup").get("cols"),"3")
        self.assertEqual({len(row) for row in table.iter(CN+"row")},{2})


if __name__=="__main__":
    unittest.main()
