"""Protect the reviewed source variables without allowing untranslated prose."""
import unittest
import xml.etree.ElementTree as ET
from build_unit import localize,math_signature,MATH,CN


class MathIdentifierTests(unittest.TestCase):
    def source(self,tag="mi",value="a"):
        return ET.fromstring(f'<section xmlns="{CN[1:-1]}" xmlns:m="{MATH[1:-1]}"><m:math><m:{tag}>{value}</m:{tag}></m:math></section>')

    def catalog(self,unit="TE-B015",translations=None):
        return {"unit_id":unit,"expected_text_slot_count":1,"translations":translations or {}}

    def test_registered_variables_pass_unchanged(self):
        for value in ("a","b"):
            source=self.source(value=value)
            self.assertEqual(math_signature(localize(source,self.catalog(),{})),math_signature(source))

    def test_unregistered_letter_or_unit_fails(self):
        for value,unit in (("c","TE-B015"),("a","TE-B014")):
            with self.assertRaisesRegex(AssertionError,"Untranslated prose"):
                localize(self.source(value=value),self.catalog(unit),{})

    def test_alphabetic_math_prose_is_not_a_variable(self):
        for tag in ("mtext","mn","mo"):
            with self.assertRaisesRegex(AssertionError,"Untranslated prose"):
                localize(self.source(tag=tag),self.catalog(),{})

    def test_variables_cannot_be_translated(self):
        with self.assertRaisesRegex(AssertionError,"Math token changed"):
            localize(self.source(),self.catalog(translations={"s001":"సంఖ్య"}),{})


if __name__=="__main__":unittest.main()
