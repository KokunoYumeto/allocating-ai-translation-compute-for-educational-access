"""Prevent image-step tables from squeezing their instructions into tiny cells."""
import unittest
from build_unit import unit_inputs, asset_map, localize, render


class StepTableLayoutTests(unittest.TestCase):
    def test_b006_instruction_columns_remain_readable(self):
        source, _, catalog = unit_inputs("TE-B006")
        assets = asset_map("TE-B006")
        target = localize(source, catalog, assets)
        for node, english in [(source, True), (target, False)]:
            page = render(node, assets, "en-" if english else "", english)
            self.assertEqual(page.count('style="min-width:300px;text-align:left"'), 21)

    def test_non_image_tables_do_not_gain_step_width(self):
        source, _, catalog = unit_inputs("TE-B004")
        assets = asset_map("TE-B004")
        page = render(localize(source, catalog, assets), assets)
        self.assertNotIn('min-width:300px', page)


if __name__ == "__main__":
    unittest.main()
