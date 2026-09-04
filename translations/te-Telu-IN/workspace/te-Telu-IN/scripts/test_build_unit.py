"""Real TE-B002 fixture regression tests; no downloads or large extractions."""
import copy
import json
import unittest
import xml.etree.ElementTree as ET
from build_unit import BASE, unit_inputs, asset_map, localize, math_signature, structural_signature, render, build, validate_b002_bridge, MATH, CN
from inspect_source import slots


class NextUnitTests(unittest.TestCase):
    def setUp(self):
        self.source,self.meta,self.catalog=unit_inputs("TE-B002")
        self.assets=asset_map("TE-B002")

    def test_full_source_slots_include_accessibility_text(self):
        self.assertEqual(len(list(slots(self.source))),129)
        self.assertEqual(sum(key=="aria-label" for _,key,_ in slots(self.source)),2)
        self.assertEqual(len(list(self.source.iter())),310)

    def test_math_and_nesting_preserved(self):
        target=localize(self.source,self.catalog,self.assets)
        self.assertEqual(math_signature(self.source),math_signature(target))
        self.assertEqual(structural_signature(self.source),structural_signature(target))
        strings=[e.text for e in target.iter(MATH+"mtext")]
        self.assertIn("మొత్తం = ",strings)
        self.assertIn("base-10",strings)
        self.assertTrue({"$100","$10","$1","$374"}.issubset(strings))

    def test_missing_prose_fails(self):
        del self.catalog["translations"]["s001"]
        with self.assertRaisesRegex(AssertionError,"Untranslated prose"):
            localize(self.source,self.catalog,self.assets)

    def test_numeric_translation_rejected(self):
        name=next(f"s{i:03d}" for i,(e,k,v) in enumerate(slots(self.source),1) if e.tag==MATH+"mn" and k=="text")
        self.catalog["translations"][name]="తప్పు"
        with self.assertRaisesRegex(AssertionError,"Math token"):
            localize(self.source,self.catalog,self.assets)

    def test_unregistered_math_word_translation_rejected(self):
        name=next(f"s{i:03d}" for i,(e,k,v) in enumerate(slots(self.source),1) if e.tag==MATH+"mtext" and v=="base-10")
        self.catalog["translations"][name]="పది"
        with self.assertRaisesRegex(AssertionError,"Math token"):
            localize(self.source,self.catalog,self.assets)

    def test_missing_asset_mapping_rejected(self):
        self.assets.pop(next(iter(self.assets)))
        with self.assertRaisesRegex(AssertionError,"asset mapping"):
            localize(self.source,self.catalog,self.assets)

    def test_tables_have_five_real_columns(self):
        target=localize(self.source,self.catalog,self.assets)
        for table in target.iter(CN+"table"):
            self.assertEqual(table.find(CN+"tgroup").get("cols"),"5")
            self.assertTrue("ఐదు" in table.get("aria-label") or "5" in table.get("aria-label"))
            self.assertEqual(len(list(table.iter(CN+"row"))),5)
            self.assertTrue(all(len(r)==5 for r in table.iter(CN+"row")))
        english=render(self.source,self.assets,"en-",True)
        self.assertEqual(english.count('scope="col"'),10)
        self.assertNotIn("table with 3 columns",english)
        self.assertEqual(english.count("Place-value table with five columns"),2)

    def test_source_quotes_are_valid_not_repaired(self):
        alt=next(e.get("alt") for e in self.source.iter() if e.get("alt"))
        self.assertIn("\u201c",alt)
        self.assertNotIn("\ufffd",alt)
        self.assertIn("\u201c",render(self.source,self.assets,"en-",True))

    def test_table_descendant_id_cannot_silently_disappear(self):
        table=copy.deepcopy(next(self.source.iter(CN+"table")))
        next(table.iter(CN+"entry")).set("id","test-cell")
        with self.assertRaises(AssertionError):
            render(table,self.assets,"en-",True)

    def test_block_diagram_uses_valid_html_container(self):
        para=next(e for e in self.source.iter(CN+"para") if e.get("id")=="fs-id3302675")
        self.assertTrue(render(para,self.assets,"en-",True).startswith('<div id="en-fs-id3302675"'))

    def test_deterministic_reader(self):
        first=build("TE-B002")
        data=(BASE/"reader/TE-B002.html").read_bytes()
        second=build("TE-B002")
        self.assertEqual(first,second)
        self.assertEqual(data,(BASE/"reader/TE-B002.html").read_bytes())

    def test_actual_worked_answer_mutation_rejected(self):
        raw=(BASE/"translations/TE-B002.bridge.xhtml").read_text(encoding="utf-8")
        validate_b002_bridge(ET.fromstring(raw))
        for valid,invalid in [("100 + 70 + 6 = 176","100 + 70 + 6 = 177"),("100 + 0 + 7","100 + 0 + 8"),("$300 + $70 + $4 = $374","$300 + $70 + $4 = $375")]:
            with self.assertRaisesRegex(AssertionError,"Worked expression"):
                validate_b002_bridge(ET.fromstring(raw.replace(valid,invalid)))

    def test_source_list_markers_and_italics(self):
        node=ET.fromstring('<list xmlns="http://cnx.rice.edu/cnxml" list-type="enumerated" class="circled"><item><span>ⓐ</span> <emphasis effect="italics">word</emphasis></item></list>')
        result=render(node,{})
        self.assertTrue(result.startswith('<ol class="cn-list labeled-list">'))
        self.assertIn('<em>word</em>',result)

    def test_table_scroll_keyboard_access(self):
        result=render(self.source,self.assets,"en-",True)
        self.assertEqual(result.count('class="table-scroll" tabindex="0" role="region"'),2)


if __name__=="__main__":
    unittest.main()
