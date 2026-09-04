"""Focused coverage-audit tests; isolated generated fixtures, never real readers."""
import base64
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from audit_m49301 import (audit, CN, MD, MATH, EXERCISES_ID, Inventory,
                         digest, source_math_bytes)


class CoverageAuditTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "full.cnxml"
        self.source.write_text(
            f'<document xmlns="{CN}" xmlns:md="{MD}" xmlns:m="{MATH}">'
            '<metadata><md:abstract><para id="abstract-p">Objectives</para>'
            '<list id="objective-list"><item>Read a function.</item></list>'
            '</md:abstract></metadata><content>'
            '<example id="example"><title>Example</title>'
            '<exercise id="example-ex"><problem id="example-p">Example prompt.</problem>'
            '</exercise></example>'
            '<note id="try-note" class="precalculus try"><label>Try It</label>'
            '<exercise id="try-ex"><problem id="try-p">Try prompt.</problem></exercise></note>'
            f'<section id="{EXERCISES_ID}"><title>Section Exercises</title>'
            '<exercise id="end-ex"><problem id="end-p">'
            '<para id="math-a">First <m:math><m:mn>2</m:mn></m:math></para>'
            '<para id="math-b">Second <m:math><m:mn>2</m:mn></m:math></para>'
            '<media id="media" alt="Original"><image src="../../media/fixture.jpg"/>'
            '</media></problem></exercise></section></content>'
            '<glossary><definition id="definition"><term>function</term>'
            '<meaning id="meaning">A rule.</meaning></definition></glossary></document>',
            encoding="utf-8")
        self.original_sha = digest(self.source.read_bytes())
        self.asset = b"synthetic fixture image bytes; no real corpus needed"
        (self.root / "assets").mkdir()
        (self.root / "assets/fixture.jpg").write_bytes(self.asset)
        self.write_json("provenance/fixture-asset-notices.json", [
            {"asset_path": "media/fixture.jpg", "admission": "admitted",
             "sha256": digest(self.asset)}
        ])
        self.configs = {}
        self.make_unit("A30-U001")

    def write_json(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

    def read_json(self, relative):
        return json.loads((self.root / relative).read_text("utf-8"))

    def make_unit(self, unit):
        slug = unit + "-fixture"
        excerpt_path = self.root / f"sources/m49301-{unit}.cnxml"
        excerpt_path.parent.mkdir(exist_ok=True)
        excerpt_path.write_bytes(self.source.read_bytes())
        inv = Inventory([ET.fromstring(excerpt_path.read_bytes())])
        draft = "\n\n".join(f"## Heading {{#{identity}}}" for identity in inv.ids)
        draft += "\n\n{{math:math-a:0}}\n\n{{math:math-b:0}}\n\n"
        draft += "![Image](../assets/fixture.jpg)\n"
        path = self.root / f"translation/{slug}.vi.md"
        path.parent.mkdir(exist_ok=True)
        path.write_text(draft, encoding="utf-8")
        self.configs[unit] = {
            "slug": slug, "source": f"sources/m49301-{unit}.cnxml",
            "images": 1, "math_text": {}, "minimum_canon_examples": 1,
            "visual_receipt": f"qa/visual-{unit}.json",
        }
        self.write_json("units.json", self.configs)
        self.seal(unit)

    def seal(self, unit="A30-U001"):
        """Generate receipt-consistent fixtures; does not assert mathematical truth."""
        from audit_m49301 import PLACEHOLDER
        config = self.configs[unit]
        excerpt_data = (self.root / config["source"]).read_bytes()
        inv = Inventory([ET.fromstring(excerpt_data)])
        draft = (self.root / f"translation/{config['slug']}.vi.md").read_bytes()
        parts = ['<html lang="vi-Latn-VN"><body>']
        parts += [f'<span id="{identity}"></span>' for identity in inv.ids]
        insertions = []
        for identity, index in PLACEHOLDER.findall(draft.decode("utf-8")):
            math = list(inv.ids[identity].iter(f"{{{MATH}}}math"))[int(index)]
            insertions.append({"source_id": identity, "math_index": int(index),
                               "source_math_sha256": digest(source_math_bytes(math))})
            copied = deepcopy(math)
            copied.tail = None
            for node in copied.iter():
                node.tag = node.tag.rsplit("}", 1)[-1]
            copied.set("xmlns", MATH)
            copied.set("data-source", identity + ":" + index)
            parts.append(ET.tostring(copied, encoding="unicode"))
        parts.append('<img alt="Image" src="data:image/jpeg;base64,' +
                     base64.b64encode(self.asset).decode() + '"/></body></html>')
        reader = "".join(parts).encode("utf-8")
        path = self.root / f"review/{config['slug']}.vi.html"
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(reader)
        self.write_json(f"canon/review-{unit}.json", {
            "unit": unit, "translation_sha256": digest(draft),
            "source_excerpt_sha256": digest(excerpt_data),
            "draft_checked": True, "final_checked": True,
            "examples_consulted": ["VI-C01"],
        })
        self.write_json(f"qa/build-{unit}.json", {
            "unit": unit, "result": "pass", "translation_sha256": digest(draft),
            "source_excerpt_sha256": digest(excerpt_data), "html_sha256": digest(reader),
            "canon_review": f"canon/review-{unit}.json",
            "visual_review": config["visual_receipt"], "source_math_insertions": insertions,
            "technical_anchor_aliases": [], "cross_reader_links": [],
        })
        self.write_json(config["visual_receipt"], {
            "unit": unit, "result": "pass", "html_sha256": digest(reader),
        })

    def run_audit(self):
        return audit(self.root, self.source, self.original_sha)

    def codes(self, result):
        return {row["code"] for row in result["issues"]}

    def add_equivalence(self):
        path = self.root / "translation/A30-U001-fixture.vi.md"
        path.write_text(path.read_text().replace("{{math:math-a:0}}", "Manually written 2."),
                        encoding="utf-8")
        self.seal()
        gap = self.run_audit()["units"]["A30-U001"]["direct_math_capture_gaps"][0]
        reader = self.root / "review/A30-U001-fixture.vi.html"
        data = reader.read_bytes().replace(b"</body>", b"<p>Manually rendered 2.</p></body>")
        reader.write_bytes(data)
        for relative in ["qa/build-A30-U001.json", "qa/visual-A30-U001.json"]:
            receipt = self.read_json(relative)
            receipt["html_sha256"] = digest(data)
            self.write_json(relative, receipt)
        entry = {
            "unit": "A30-U001", "source_math_key": "math-a:0",
            "source_math_sha256": gap["source_math_sha256"],
            "translation_sha256": digest(path.read_bytes()), "reader_sha256": digest(data),
            "review_status": "approved_equivalent", "reviewer": "fixture-reviewer",
            "draft_snippets": ["Manually written 2."],
            "rendered_snippets": ["<p>Manually rendered 2.</p>"],
            "rationale": "Fixture records a specific review; audit does not prove this judgment.",
        }
        self.write_json("provenance/m49301-rendered-equivalents.json", {
            "schema": 1, "module": "m49301", "source_module_sha256": self.original_sha,
            "entries": [entry],
        })
        return entry

    def test_complete_fixture_passes_without_writing_or_network(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        with patch.object(Path, "write_bytes", side_effect=AssertionError("unexpected write")), \
             patch.object(Path, "write_text", side_effect=AssertionError("unexpected write")), \
             patch("socket.create_connection", side_effect=AssertionError("unexpected network")):
            result = self.run_audit()
        self.assertEqual(result["issues"], [])
        self.assertEqual(result["result"], "structural_checks_pass")
        self.assertEqual(result["counts"]["end_exercises"]["accepted_reader_unique"], 1)
        self.assertEqual(result["counts"]["examples"]["original"], 1)
        self.assertEqual(result["counts"]["try_it_exercises"]["original"], 1)
        self.assertEqual(result["counts"]["glossary_definitions"]["original"], 1)
        self.assertEqual(result["counts"]["learning_objectives"]["accepted"], 1)
        self.assertEqual(result["coverage"]["source_mathml"]["accepted_unique"], 2)
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_omitted_unit_is_not_counted_from_files_alone(self):
        self.write_json("units.json", {})
        result = self.run_audit()
        self.assertNotEqual(result["result"], "structural_checks_pass")
        self.assertEqual(result["counts"]["end_exercises"]["accepted_reader_unique"], 0)
        self.assertEqual(len(result["unregistered_drafts_not_counted"]), 1)

    def test_missing_draft_anchor_rejected_even_with_current_hashes(self):
        path = self.root / "translation/A30-U001-fixture.vi.md"
        path.write_text(path.read_text().replace("{#end-ex}", ""), encoding="utf-8")
        self.seal()
        result = self.run_audit()
        self.assertIn("draft_source_anchor_missing", self.codes(result))
        self.assertFalse(result["units"]["A30-U001"]["accepted_receipts"])

    def test_explicit_raw_html_anchor_is_valid(self):
        path = self.root / "translation/A30-U001-fixture.vi.md"
        path.write_text(path.read_text().replace("## Heading {#end-ex}", '<span id="end-ex">Exercise</span>'),
                        encoding="utf-8")
        self.seal()
        self.assertEqual(self.run_audit()["result"], "structural_checks_pass")

    def test_missing_math_capture_is_not_silently_approved_as_equivalent(self):
        path = self.root / "translation/A30-U001-fixture.vi.md"
        path.write_text(path.read_text().replace("{{math:math-a:0}}", "$2$"), encoding="utf-8")
        self.seal()
        result = self.run_audit()
        self.assertEqual(result["result"], "incomplete_or_unverified")
        self.assertTrue(result["units"]["A30-U001"]["accepted_receipts"])
        gaps = result["units"]["A30-U001"]["direct_math_capture_gaps"]
        self.assertEqual([row["source_math_key"] for row in gaps], ["math-a:0"])
        self.assertIn("not_assessed", gaps[0]["rendered_equivalence"])
        self.assertIn("math", gaps[0]["source_mathml"])
        self.assertEqual(result["coverage"]["source_mathml"]["accepted_unique"], 1)

    def test_stale_build_draft_hash_rejected(self):
        path = self.root / "translation/A30-U001-fixture.vi.md"
        path.write_text(path.read_text() + "\nChanged prose.\n", encoding="utf-8")
        self.assertIn("receipt_draft_hash_mismatch", self.codes(self.run_audit()))

    def test_unaccepted_or_missing_visual_receipt_rejected(self):
        self.write_json("qa/visual-A30-U001.json", {
            "unit": "A30-U001", "result": "pending", "html_sha256": "wrong",
        })
        result = self.run_audit()
        self.assertIn("receipt_not_pass", self.codes(result))
        self.assertEqual(result["counts"]["end_exercises"]["accepted_reader_unique"], 0)
        (self.root / "qa/visual-A30-U001.json").unlink()
        self.assertIn("unit_input_or_integrity_error", self.codes(self.run_audit()))

    def test_omitted_anonymous_objective_is_detected_despite_all_ids(self):
        path = self.root / self.configs["A30-U001"]["source"]
        path.write_text(path.read_text().replace("<item>Read a function.</item>", ""), encoding="utf-8")
        self.seal()
        result = self.run_audit()
        self.assertNotEqual(result["result"], "structural_checks_pass")
        self.assertEqual(result["coverage"]["source_ids"]["missing_from_registered_excerpts"], [])
        self.assertEqual(result["counts"]["learning_objectives"]["accepted"], 0)

    def test_changed_source_math_rejected_even_if_receipts_are_rebound(self):
        path = self.root / self.configs["A30-U001"]["source"]
        path.write_text(path.read_text().replace("<m:mn>2</m:mn>", "<m:mn>3</m:mn>", 1), encoding="utf-8")
        self.seal()
        self.assertIn("source_math_mismatch", self.codes(self.run_audit()))

    def test_changed_reader_math_rejected_even_if_reader_hashes_are_rebound(self):
        path = self.root / "review/A30-U001-fixture.vi.html"
        data = path.read_bytes().replace(b"<mn>2</mn>", b"<mn>9</mn>", 1)
        path.write_bytes(data)
        for relative in ["qa/build-A30-U001.json", "qa/visual-A30-U001.json"]:
            receipt = self.read_json(relative)
            receipt["html_sha256"] = digest(data)
            self.write_json(relative, receipt)
        self.assertIn("rendered_source_math_mismatch", self.codes(self.run_audit()))

    def test_changed_asset_rejected(self):
        (self.root / "assets/fixture.jpg").write_bytes(b"changed fixture image")
        self.assertIn("source_asset_admitted_hash_missing", self.codes(self.run_audit()))

    def test_original_pin_mismatch_rejected(self):
        self.source.write_bytes(self.source.read_bytes() + b"\n")
        result = self.run_audit()
        self.assertEqual(result["result"], "integrity_errors")
        self.assertIn("input_error", self.codes(result))

    def test_duplicates_count_ids_not_registry_claims(self):
        self.make_unit("A30-U002")
        result = self.run_audit()
        self.assertEqual(result["result"], "structural_checks_pass")
        category = result["counts"]["end_exercises"]
        self.assertEqual(category["accepted_reader_unique"], 1)
        self.assertEqual(category["accepted_occurrences"], 2)
        self.assertEqual(category["duplicate_accepted_ids"]["end-ex"], ["A30-U001", "A30-U002"])

    def test_registry_path_traversal_rejected(self):
        self.configs["A30-U001"]["source"] = "../m49301-escape.cnxml"
        self.write_json("units.json", self.configs)
        self.assertIn("unit_input_or_integrity_error", self.codes(self.run_audit()))

    def test_individual_equivalence_is_counted_separately_from_direct_capture(self):
        self.add_equivalence()
        result = self.run_audit()
        self.assertEqual(result["result"], "structural_checks_pass")
        math = result["coverage"]["source_mathml"]
        self.assertEqual(math["accepted_direct_unique"], 1)
        self.assertEqual(math["accepted_reviewed_equivalent_unique"], 1)
        self.assertEqual(math["accepted_unique"], 2)
        self.assertEqual(math["direct_and_reviewed_overlap"], [])
        self.assertIn("math-a:0", math["missing_direct_capture"])
        self.assertIn("not automated", result["equivalence_ledger"]["basis"])

    def test_equivalence_requires_exact_individual_bindings_and_snippets(self):
        self.add_equivalence()
        relative = "provenance/m49301-rendered-equivalents.json"
        good = self.read_json(relative)
        mutations = {
            "source_math_sha256": "wrong", "translation_sha256": "wrong",
            "reader_sha256": "wrong", "source_math_key": "math-z:0",
            "draft_snippets": ["not in draft"], "rendered_snippets": ["not in reader"],
            "review_status": "pending", "reviewer": "", "rationale": "",
        }
        for field, bad_value in mutations.items():
            with self.subTest(field=field):
                bad = deepcopy(good)
                bad["entries"][0][field] = bad_value
                self.write_json(relative, bad)
                result = self.run_audit()
                self.assertIn("equivalent_review_binding_error", self.codes(result))
                self.assertEqual(result["coverage"]["source_mathml"]["accepted_reviewed_equivalent_unique"], 0)

    def test_equivalence_duplicate_or_wrong_full_source_binding_rejected(self):
        self.add_equivalence()
        relative = "provenance/m49301-rendered-equivalents.json"
        good = self.read_json(relative)
        bad = deepcopy(good)
        bad["entries"].append(deepcopy(bad["entries"][0]))
        self.write_json(relative, bad)
        self.assertIn("equivalence_ledger_error", self.codes(self.run_audit()))
        good["source_module_sha256"] = "wrong"
        self.write_json(relative, good)
        self.assertIn("equivalence_ledger_error", self.codes(self.run_audit()))

    def test_snapshot_retains_first_digest_across_repeated_reads(self):
        asset = self.root / "assets/fixture.jpg"
        original_read = Path.read_bytes
        calls = 0

        def read_changes(path):
            nonlocal calls
            if path == asset:
                calls += 1
                return self.asset if calls == 1 else b"changed during audit"
            return original_read(path)

        with patch.object(Path, "read_bytes", new=read_changes):
            result = self.run_audit()
        self.assertFalse(result["snapshot_stable"])
        self.assertIn("snapshot_changed_during_audit", self.codes(result))
        self.assertEqual(result["input_sha256"][str(asset)], digest(self.asset))

    def test_cross_reader_target_outside_audited_module_is_snapshotted(self):
        from build import Inspector, validate_reader_links
        self.configs["B20-U001"] = {"slug": "B20-target", "source": "sources/other.cnxml"}
        self.write_json("units.json", self.configs)
        target = self.root / "review/B20-target.vi.html"
        target.write_text('<html><span id="target">Target</span></html>', encoding="utf-8")
        reader = self.root / "review/A30-U001-fixture.vi.html"
        data = reader.read_bytes().replace(
            b"</body>", b'<a href="B20-target.vi.html#target">Target</a></body>')
        reader.write_bytes(data)
        inspector = Inspector()
        inspector.feed(data.decode())
        links = validate_reader_links(inspector.links, inspector.ids, self.root / "review", self.configs)
        for relative in ["qa/build-A30-U001.json", "qa/visual-A30-U001.json"]:
            receipt = self.read_json(relative)
            receipt["html_sha256"] = digest(data)
            if relative.startswith("qa/build"):
                receipt["cross_reader_links"] = links["cross_reader_links"]
            self.write_json(relative, receipt)
        result = self.run_audit()
        self.assertEqual(result["result"], "structural_checks_pass")
        self.assertEqual(result["input_sha256"][str(target)], digest(target.read_bytes()))

    def test_bytecode_writing_is_disabled(self):
        import sys
        self.assertTrue(sys.dont_write_bytecode)

    def test_source_math_digest_is_independent_of_global_namespace_registration(self):
        math = ET.fromstring(f'<math xmlns="{MATH}" display="block"><mi>x</mi></math>')
        before = source_math_bytes(math)
        with patch.dict(ET._namespace_map, {MATH: "m"}):
            self.assertEqual(source_math_bytes(math), before)
        self.assertIn(b'xmlns:ns0=', before)


if __name__ == "__main__":
    unittest.main()
