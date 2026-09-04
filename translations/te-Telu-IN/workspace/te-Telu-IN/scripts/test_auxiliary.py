"""B009/B010 actual source, protected metadata and semantic reader regressions."""
import copy
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch
from build_unit import (BASE,CN,MD,unit_inputs,localize,asset_map,render,build,
                        serialize,HTMLCheck)
from auxiliary_checks import validate_auxiliary


class AuxiliaryTests(unittest.TestCase):
    def fixture(self,unit):
        source,meta,cat=unit_inputs(unit)
        target=localize(source,cat,asset_map(unit))
        bridge=ET.parse(BASE/"translations"/(unit+".bridge.xhtml")).getroot()
        return source,meta,cat,target,bridge

    def test_complete_two_units(self):
        for unit,counts in [("TE-B009",(22,14,14,7,5)),("TE-B010",(15,11,9,12,1))]:
            source,meta,cat,target,bridge=self.fixture(unit)
            result=validate_auxiliary(unit,source,target,meta,cat,bridge)
            self.assertEqual((len(list(source.iter())),cat["expected_text_slot_count"],len(cat["translations"]),result["support_links"],result["actual_equations"]),counts)

    def test_semantic_glossary_and_both_language_ids(self):
        source,_,_,target,_=self.fixture("TE-B009")
        self.assertIsNone(target.find(CN+"title"))
        self.assertIsNone(target.get("id"))
        for node,prefix,english in [(source,"en-",True),(target,"",False)]:
            result=render(node,{},prefix,english)
            self.assertEqual(result.count("<dt>"),7)
            self.assertEqual(result.count("<dd "),7)
            self.assertIn('<dl class="cn-glossary">',result)
            check=HTMLCheck();check.feed(result)
            self.assertEqual(set(check.ids),{prefix+e.get("id") for e in node.iter() if e.get("id")})

    def test_glossary_structure_change_rejected(self):
        source,_,_,_,_=self.fixture("TE-B009")
        source[0].remove(source[0][0])
        with self.assertRaisesRegex(AssertionError,"definition structure"):
            render(source,{})

    def test_both_metadata_identifiers_are_unchanged(self):
        source,_,_,target,_=self.fixture("TE-B010")
        for field in ("content-id","uuid"):
            self.assertEqual(source.findtext(CN+"metadata/"+MD+field),target.findtext(CN+"metadata/"+MD+field))
        self.assertEqual(target.findtext(CN+"title"),target.findtext(CN+"metadata/"+MD+"title"))
        self.assertEqual(len(target.findall(".//"+CN+"item")),6)
        self.assertIsNone(target.find(CN+"content"))
        self.assertIsNone(target.find(CN+"glossary"))

    def test_protected_slot_cannot_also_be_translated(self):
        source,_,cat,_,_=self.fixture("TE-B010")
        cat["translations"]["s002"]="మూలం"
        with self.assertRaisesRegex(AssertionError,"cannot be translated"):
            localize(source,cat,{})

    def test_metadata_protection_does_not_allow_ordinary_prose(self):
        source,_,cat,_,_=self.fixture("TE-B010")
        cat["translations"].pop("s001")
        cat["protected_slots"]["s001"]={"tag":CN+"title","value":source[0].text,"reason":"Not authorized"}
        with self.assertRaisesRegex(AssertionError,"Only registered metadata"):
            localize(source,cat,{})

    def test_protected_wrong_value_tag_and_unused_slot(self):
        source,_,original,_,_=self.fixture("TE-B010")
        for change in ("value","tag","unused"):
            with self.subTest(change=change):
                cat=copy.deepcopy(original)
                if change=="unused":cat["protected_slots"]["s999"]=cat["protected_slots"]["s002"]
                else:cat["protected_slots"]["s002"][change]="different"
                with self.assertRaises(AssertionError):localize(source,cat,{})

    def test_unregistered_metadata_does_not_pass(self):
        source,_,cat,_,_=self.fixture("TE-B010")
        cat["protected_slots"].pop("s002")
        with self.assertRaisesRegex(AssertionError,"Untranslated prose s002"):
            localize(source,cat,{})

    def test_unknown_metadata_renderer_fails(self):
        with self.assertRaisesRegex(AssertionError,"Unsupported metadata"):
            render(ET.Element(MD+"unknown"),{})

    def test_actual_target_identifier_corruption_rejected(self):
        source,meta,cat,target,bridge=self.fixture("TE-B010")
        target.find(CN+"metadata/"+MD+"uuid").text="different"
        with self.assertRaisesRegex(AssertionError,"target differs"):
            validate_auxiliary("TE-B010",source,target,meta,cat,bridge)

    def test_actual_target_whole_set_corruption_rejected(self):
        source,meta,cat,target,bridge=self.fixture("TE-B009")
        target[-1].find(CN+"meaning").text="పూర్ణాంకాలు 1, 2, 3."
        with self.assertRaisesRegex(AssertionError,"target differs"):
            validate_auxiliary("TE-B009",source,target,meta,cat,bridge)

    def test_actual_equations_and_links_reject_corruption(self):
        for unit in ("TE-B009","TE-B010"):
            for mode in ("equation","link"):
                with self.subTest(unit=unit,mode=mode):
                    source,meta,cat,target,bridge=self.fixture(unit)
                    if mode=="equation":
                        node=next(e for e in bridge.iter() if e.text and " × " in e.text)
                        node.text=node.text.replace(" = 30"," = 31").replace(" = 40"," = 41")
                    else:
                        next(e for e in bridge.iter() if e.get("href")).set("href","TE-B001.html#missing")
                    with self.assertRaises(ValueError):validate_auxiliary(unit,source,target,meta,cat,bridge)

    def test_no_synthetic_source_fragment_in_page_scope(self):
        for unit in ("TE-B009","TE-B010"):
            with patch("build_unit.atomic_write") as writes:
                build(unit)
            page=next(c.args[1].decode("utf-8") for c in writes.call_args_list if c.args[0].suffix==".html")
            self.assertNotIn("m81243#@",page)
            self.assertNotIn("One complete subsection:",page)
            self.assertIn("Source selection:",page)
            if unit=="TE-B010":self.assertIn("production numbering is not teaching order",page)

    def test_existing_b008_render_remains_byte_identical(self):
        with patch("build_unit.atomic_write") as writes:build("TE-B008")
        page=next(c.args[1] for c in writes.call_args_list if c.args[0].suffix==".html")
        self.assertEqual(page,(BASE/"reader/TE-B008.html").read_bytes())


if __name__=="__main__":unittest.main()
