"""Regression tests for the nine finite A10 like-terms asset products."""
from __future__ import annotations

import copy
import base64
import json
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import like_terms_checks as checks
import prepare_like_terms_assets as prepare


class LikeTermsAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules_raw = checks.RULES_PATH.read_bytes()
        cls.rules = json.loads(cls.rules_raw)
        cls.manifest = json.loads(checks.ASSETS_PATH.read_text(encoding="utf-8"))

    def test_deterministic_products_match_disk(self):
        products = prepare.products()
        self.assertEqual(products, prepare.products())
        for relative, raw in products.items():
            self.assertEqual((checks.LANG / relative).read_bytes(), raw)
        self.assertEqual(len(products), 10)  # three exact JPEGs, six SVGs, manifest

    def test_exact_source_and_six_derivative_bindings(self):
        summary = checks.verify_assets(self.rules, self.rules_raw)
        self.assertEqual(summary["source_assets"], 3)
        self.assertEqual(summary["javanese_derivatives"], 6)
        self.assertEqual(len({row["source_binding"]["source_image_sha256"] for row in self.manifest["assets"]}), 3)

    def test_exact_jpeg_formula_panels_are_embedded_before_bounded_overlays(self):
        for asset in self.manifest["assets"]:
            for track in ("jv-academic", "jv-conversation"):
                svg = ET.parse(checks.LANG / asset["outputs"][track]["path"]).getroot()
                children = list(svg)
                image = next(node for node in children if checks.local(node) == "image")
                overlay = next(node for node in children if checks.local(node) == "g")
                self.assertLess(children.index(image), children.index(overlay))
                encoded = image.get("href").split(",", 1)[1]
                embedded = base64.b64decode(encoded, validate=True)
                source = (checks.LANG / asset["outputs"]["id-academic"]["path"]).read_bytes()
                self.assertEqual(embedded, source)
                cover = next(node for node in overlay if checks.local(node) == "rect")
                self.assertEqual((cover.get("x"), cover.get("width")), ("2", "354"))
                self.assertEqual(overlay.get("clip-path"), "url(#instruction-clip)")

    def _temporary_manifest(self):
        temporary = tempfile.TemporaryDirectory(prefix="like-terms-assets-")
        root = Path(temporary.name)
        for asset in self.manifest["assets"]:
            for output in asset["outputs"].values():
                source = checks.LANG / output["path"]
                target = root / output["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
        manifest_path = root / f"translation/{checks.UNIT}.assets.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(self.manifest, ensure_ascii=False), encoding="utf-8")
        return temporary, root, manifest_path

    def test_changed_old_label_binding_is_rejected(self):
        temporary, root, manifest_path = self._temporary_manifest()
        try:
            mutated = copy.deepcopy(self.manifest)
            mutated["assets"][0]["corrections"][0]["old_value"] = "Step 1. Changed."
            manifest_path.write_text(json.dumps(mutated, ensure_ascii=False), encoding="utf-8")
            with patch.object(checks, "LANG", root), patch.object(checks, "ASSETS_PATH", manifest_path):
                with self.assertRaises(AssertionError):
                    checks.verify_assets(self.rules, self.rules_raw)
        finally:
            temporary.cleanup()

    def test_changed_derivative_bytes_are_rejected(self):
        temporary, root, manifest_path = self._temporary_manifest()
        try:
            output = self.manifest["assets"][1]["outputs"]["jv-conversation"]
            path = root / output["path"]
            path.write_bytes(path.read_bytes().replace(b"#a0b3bd", b"#000000", 1))
            with patch.object(checks, "LANG", root), patch.object(checks, "ASSETS_PATH", manifest_path):
                with self.assertRaises(AssertionError):
                    checks.verify_assets(self.rules, self.rules_raw)
        finally:
            temporary.cleanup()

    def test_unknown_asset_track_and_fixture_fail_closed(self):
        chart = self.rules["chart_fixtures"][0]
        source = (checks.LANG / self.manifest["assets"][0]["outputs"]["id-academic"]["path"]).read_bytes()
        with self.assertRaisesRegex(ValueError, "unsupported_like_terms_asset_track"):
            prepare.svg_bytes(chart, "jv-fallback", source)
        with self.assertRaisesRegex(ValueError, "unsupported_like_terms_source_asset"):
            prepare.svg_bytes(chart, "jv-academic", source + b"changed")
        changed = copy.deepcopy(chart)
        changed["id"] = "A10-COMB-D99"
        with self.assertRaisesRegex(ValueError, "unsupported_like_terms_chart_fixture"):
            prepare.svg_bytes(changed, "jv-academic", source)


if __name__ == "__main__":
    unittest.main()
