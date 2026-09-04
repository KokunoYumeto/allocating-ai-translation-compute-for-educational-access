"""Readiness source links and freezing cannot silently lose document context."""
import copy
import unittest
import xml.etree.ElementTree as ET
from build_unit import BASE,CN,render,unit_inputs,localize,asset_map,validate_reader_link,HTMLCheck
from prepare_unit import select_source_unit


class ReadinessRenderingTests(unittest.TestCase):
    def test_exact_crossmodule_destinations_in_both_languages(self):
        for unit,filename,anchor in [("TE-B011","TE-B002.html","fs-id2222880"),("TE-B012","TE-B005.html","fs-id3202693")]:
            source,_,catalog=unit_inputs(unit);assets=asset_map(unit)
            for root,prefix,english in [(source,"en-",True),(localize(source,catalog,assets),"",False)]:
                before=ET.tostring(root)
                result=render(root,assets,prefix,english,True)
                link=filename+"#"+prefix+anchor
                self.assertIn('href="'+link+'"',result)
                validate_reader_link(link,[])
                self.assertEqual(ET.tostring(root),before)
                self.assertEqual(result.count('class="cn-solution"><summary>'),1)
                self.assertNotIn(" open",result)

    def test_unknown_document_or_target_fails(self):
        for document,target in [("m99999","fs-id2222880"),("m81243","missing")]:
            node=ET.Element(CN+"link",{"document":document,"target-id":target})
            with self.assertRaisesRegex(AssertionError,"Unregistered cross-module"):
                render(node,{})

    def test_regular_local_link_unchanged(self):
        node=ET.Element(CN+"link",{"target-id":"figure"})
        self.assertIn('href="#en-figure"',render(node,{},"en-",True))

    def test_section_and_both_readiness_notes_freeze_exactly(self):
        for unit in ("TE-B007","TE-B011","TE-B012"):
            node=ET.parse(BASE/"sources"/(unit+".en.cnxml")).getroot()
            expected=ET.tostring(node);node.tail="\n"
            document=ET.Element(CN+"document");document.append(node)
            self.assertEqual(ET.tostring(select_source_unit(document,node.get("id"))),expected)

    def test_nonsection_prose_cannot_be_frozen_as_unit(self):
        root=ET.fromstring(f'<document xmlns="{CN[1:-1]}"><para id="x">Text</para></document>')
        with self.assertRaises(AssertionError):select_source_unit(root,"x")

    def test_duplicate_source_selection_fails(self):
        root=ET.fromstring(f'<document xmlns="{CN[1:-1]}"><note id="x"/><section id="x"/></document>')
        with self.assertRaises(AssertionError):select_source_unit(root,"x")


if __name__=="__main__":unittest.main()
