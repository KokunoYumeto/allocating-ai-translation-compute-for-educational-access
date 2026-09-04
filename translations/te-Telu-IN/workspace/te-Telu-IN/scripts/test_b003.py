"""Actual B003 regression fixtures, plus B004's explicitly registered source table."""
import copy
import unittest
import xml.etree.ElementTree as ET
from build_unit import BASE,CN,MATH,unit_inputs,asset_map,localize,math_signature,structural_signature,render,render_bridge,validate_b003_bridge
from inspect_source import slots


class PlaceValueTests(unittest.TestCase):
    def setUp(self):
        self.source,self.meta,self.catalog=unit_inputs("TE-B003")
        self.assets=asset_map("TE-B003")
        self.bridge=ET.parse(BASE/"translations/TE-B003.bridge.xhtml").getroot()

    def test_exact_source_and_math(self):
        self.assertEqual(len(list(slots(self.source))),131)
        self.assertEqual(len(list(self.source.iter())),216)
        self.assertEqual(len(list(self.source.iter(MATH+"math"))),40)
        target=localize(self.source,self.catalog,self.assets)
        self.assertEqual(math_signature(self.source),math_signature(target))
        self.assertEqual(structural_signature(self.source),structural_signature(target))

    def test_actual_worked_values(self):
        validate_b003_bridge(self.bridge)

    def test_wrong_contribution_rejected(self):
        raw=ET.tostring(self.bridge,encoding="unicode")
        wrong=raw.replace("9 × 1,000,000,000 = 9,000,000,000","9 × 1,000,000,000 = 90,000,000,000")
        with self.assertRaisesRegex(AssertionError,"Wrong contribution"):
            validate_b003_bridge(ET.fromstring(wrong))

    def test_wrong_position_rejected(self):
        raw=ET.tostring(self.bridge,encoding="unicode").replace(">10వ<",">11వ<")
        with self.assertRaisesRegex(AssertionError,"Wrong place"):
            validate_b003_bridge(ET.fromstring(raw))

    def test_zero_contribution_rejected(self):
        raw=ET.tostring(self.bridge,encoding="unicode").replace("0 × 10,000 = 0","0 × 10,000 = 10,000")
        with self.assertRaisesRegex(AssertionError,"worked expression"):
            validate_b003_bridge(ET.fromstring(raw))

    def test_missing_recheck_solution_rejected(self):
        raw=ET.tostring(self.bridge,encoding="unicode").replace('id="B003-S-R04"','id="wrong"')
        with self.assertRaises(AssertionError):
            validate_b003_bridge(ET.fromstring(raw))

    def test_bridge_tables_scoped_scroll_preserves_source(self):
        before=ET.tostring(self.bridge)
        result=render_bridge(self.bridge)
        self.assertEqual(before,ET.tostring(self.bridge))
        self.assertEqual(result.count('class="table-scroll" tabindex="0"'),2)
        self.assertEqual(result.count('scope="col"'),8)

    def test_charts_keep_all_columns_with_local_scroll(self):
        target=localize(self.source,self.catalog,self.assets)
        result=render(target,self.assets)
        self.assertEqual(result.count('class="cn-media media-scroll" tabindex="0"'),2)
        self.assertEqual(result.count('min-width:2240px'),2)

    def test_b004_known_declared_column_error_is_explicit(self):
        source=ET.parse(BASE/"sources/TE-B004.en.cnxml").getroot()
        table=next(source.iter(CN+"table"))
        self.assertEqual(table.find(CN+"tgroup").get("cols"),"3")
        self.assertEqual({len(row) for row in table.iter(CN+"row")},{2})
        result=render(table,{},"en-",True)
        self.assertEqual(result.count("<td>"),10)
        self.assertIn("all 2 content columns",result)
        unregistered=copy.deepcopy(table); unregistered.set("id","unknown-table")
        with self.assertRaises(AssertionError):
            render(unregistered,{},"en-",True)


if __name__=="__main__":
    unittest.main()
