"""A partial module cannot inherit a complete-source coverage label."""
import copy
import json
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch
from freeze_sources import BASE,module_translation_status
from check_m81243_coverage import graph


class ModuleProgressTests(unittest.TestCase):
    def setUp(self):self.progress=json.loads((BASE/"units.json").read_text("utf-8"))

    def status(self,data):
        with patch("freeze_sources.json.loads",return_value=data):
            return module_translation_status("A00","m81243")

    def test_checked_fragments_with_explicit_coverage(self):
        self.assertIn("all module source parts checked",self.status(self.progress))

    def test_without_coverage_record_is_incomplete(self):
        self.progress.pop("module_coverage")
        self.assertIn("module incomplete",self.status(self.progress))

    def test_missing_auxiliary_unit_is_incomplete(self):
        self.progress["units"]=[u for u in self.progress["units"] if u["unit"]!="TE-B010"]
        self.assertIn("module incomplete",self.status(self.progress))

    def test_draft_auxiliary_unit_is_incomplete(self):
        next(u for u in self.progress["units"] if u["unit"]=="TE-B009")["status"]="drafting"
        self.assertIn("module incomplete",self.status(self.progress))

    def test_unstarted_module_remains_unstarted(self):
        self.assertEqual(module_translation_status("A00","m81242"),"not_started")

    def test_graph_ignores_only_whitespace_not_meaningful_tail(self):
        a=ET.fromstring('<section><p>Read <term>zero</term> first.</p></section>')
        b=copy.deepcopy(a);b.tail="\n"
        self.assertEqual(graph(a),graph(b))
        b[0][0].tail=" last."
        self.assertNotEqual(graph(a),graph(b))


if __name__=="__main__":unittest.main()
