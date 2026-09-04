"""Table summary prose must be localized, not silently left in English."""
import unittest
import xml.etree.ElementTree as ET
from inspect_source import slots, CN
from build_unit import BASE, localize, render, unit_inputs, asset_map, serialize


class SummarySlotTests(unittest.TestCase):
    def source(self):
        return ET.fromstring(f'<table xmlns="{CN[1:-1]}" id="summary-test" summary="Addition steps"><tgroup cols="2"><tbody><row><entry>3</entry><entry>4</entry></row></tbody></tgroup></table>')

    def test_summary_is_explicit_prose_slot(self):
        fields=list(slots(self.source()))
        self.assertEqual([(key,value) for _,key,value in fields],[("summary","Addition steps"),("text","3"),("text","4")])

    def test_summary_localizes_without_mutating_source(self):
        source=self.source();before=ET.tostring(source)
        catalog={"expected_text_slot_count":3,"translations":{"s001":"సంకలనం చేసే దశలు"}}
        target=localize(source,catalog,{})
        self.assertEqual(target.get("summary"),"సంకలనం చేసే దశలు")
        self.assertEqual(ET.tostring(source),before)
        self.assertIn('aria-label="సంకలనం చేసే దశలు"',render(target,{}))
        self.assertIn('aria-label="Addition steps"',render(source,{},english=True))

    def test_missing_summary_translation_fails(self):
        with self.assertRaisesRegex(AssertionError,"Untranslated prose s001"):
            localize(self.source(),{"expected_text_slot_count":3,"translations":{}},{})

    def test_blank_summary_does_not_shift_slots(self):
        source=self.source();source.set("summary","  ")
        self.assertEqual(len(list(slots(source))),2)

    def test_existing_aria_label_has_precedence(self):
        source=self.source();source.set("aria-label","Specific label")
        self.assertIn('aria-label="Specific label"',render(source,{},english=True))

    def test_prior_unit_localizations_are_byte_identical(self):
        for number in range(2,14):
            unit=f"TE-B{number:03d}"
            with self.subTest(unit=unit):
                source,metadata,catalog=unit_inputs(unit)
                self.assertFalse(any(e.get("summary") for e in source.iter()))
                self.assertEqual(len(list(slots(source))),metadata["text_slots"])
                actual=serialize(localize(source,catalog,asset_map(unit)))
                self.assertEqual(actual,(BASE/"generated"/(unit+".te.cnxml")).read_bytes())


if __name__=="__main__":unittest.main()
