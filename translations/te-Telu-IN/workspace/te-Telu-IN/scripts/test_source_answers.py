"""Practice answers remain exact but are initially collapsed in both columns."""
import unittest
import xml.etree.ElementTree as ET
from build_unit import BASE, unit_inputs, asset_map, localize, render, render_bridge


class PracticeAnswerPresentationTests(unittest.TestCase):
    def test_b008_preserves_all_answer_ids_in_closed_panels(self):
        source, _, catalog = unit_inputs("TE-B008")
        assets = asset_map("TE-B008")
        target = localize(source, catalog, assets)
        for root, prefix, english in [(source, "en-", True), (target, "", False)]:
            rendered = render(root, assets, prefix, english, collapse_solutions=True)
            self.assertEqual(rendered.count('class="cn-solution"><summary>'), 29)
            self.assertNotIn(" open", rendered)
            for node in root.iter():
                if node.tag.endswith("}solution"):
                    self.assertIn(f'<details id="{prefix}{node.get("id")}"', rendered)

    def test_other_units_keep_existing_solution_presentation(self):
        source, _, _ = unit_inputs("TE-B007")
        self.assertNotIn('class="cn-solution"', render(source, asset_map("TE-B007"), english=True))

    def test_circled_bridge_labels_are_not_doubled(self):
        bridge = ET.parse(BASE / "translations/TE-B008.bridge.xhtml").getroot()
        before = ET.tostring(bridge)
        result = render_bridge(bridge)
        self.assertEqual(result.count('class="labeled-list"'), 12)
        self.assertEqual(ET.tostring(bridge), before)


if __name__ == "__main__":
    unittest.main()
