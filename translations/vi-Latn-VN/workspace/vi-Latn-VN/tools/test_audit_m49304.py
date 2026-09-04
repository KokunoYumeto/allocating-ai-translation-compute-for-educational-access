"""Focused coverage-audit tests; isolated generated fixtures, never real readers."""
import base64
from copy import deepcopy
from html import escape
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from audit_m49304 import (audit, CN, MD, MATH, EXERCISES_ID, Inventory,
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
        excerpt_path = self.root / f"sources/m49304-{unit}.cnxml"
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
            "slug": slug, "source": f"sources/m49304-{unit}.cnxml",
            "images": 1, "math_text": {}, "minimum_canon_examples": 1,
            "visual_receipt": f"qa/visual-{unit}.json",
        }
        self.write_json("units.json", self.configs)
        self.seal(unit)

    def seal(self, unit="A30-U001"):
        """Generate receipt-consistent fixtures; does not assert mathematical truth."""
        from audit_m49304 import PLACEHOLDER
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
                if node.tag == "mtext" and node.text:
                    for old, new in config.get("math_text", {}).items():
                        node.text = node.text.replace(old, new)
            if config.get("prune_empty_math_layout"):
                from build import prune_empty_math_layout
                prune_empty_math_layout(copied)
            copied.set("xmlns", MATH)
            copied.set("data-source", identity + ":" + index)
            parts.append(ET.tostring(copied, encoding="unicode"))
        for node in ET.fromstring(excerpt_data).iter(f"{{{CN}}}link"):
            if node.get("url"):
                parts.append(f'<a href="{escape(node.get("url"), quote=True)}">Optional source link</a>')
            elif node.get("target-id") in inv.ids and node.get("document", "m49304") == "m49304":
                parts.append(f'<a href="#{node.get("target-id")}">Source reference</a>')
        parts.append('<img alt="Image" src="data:image/jpeg;base64,' +
                     base64.b64encode(self.asset).decode() + '"/></body></html>')
        reader = "".join(parts).encode("utf-8")
        path = self.root / f"review/{config['slug']}.vi.html"
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(reader)
        from build import Inspector, validate_reader_links
        inspector = Inspector()
        inspector.feed(reader.decode("utf-8"))
        links = validate_reader_links(inspector.links, inspector.ids, path.parent, self.configs)
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
            "technical_anchor_aliases": [], "cross_reader_links": links["cross_reader_links"],
            "external_links": links["external_links"],
        })
        self.write_json(config["visual_receipt"], {
            "unit": unit, "result": "pass", "html_sha256": digest(reader),
        })

    def run_audit(self):
        return audit(self.root, self.source, self.original_sha)

    def codes(self, result):
        return {row["code"] for row in result["issues"]}

    def replace_full_source(self, text):
        """Replace only a temporary fixture and regenerate its bound unit."""
        self.source.write_bytes(text.encode("utf-8"))
        self.original_sha = digest(self.source.read_bytes())
        self.make_unit("A30-U001")

    def rebind_reader(self, data, *, rebind_links=False):
        path = self.root / "review/A30-U001-fixture.vi.html"
        path.write_bytes(data)
        for relative in ["qa/build-A30-U001.json", "qa/visual-A30-U001.json"]:
            receipt = self.read_json(relative)
            receipt["html_sha256"] = digest(data)
            if rebind_links and relative.startswith("qa/build"):
                from build import Inspector, validate_reader_links
                inspector = Inspector()
                inspector.feed(data.decode("utf-8"))
                links = validate_reader_links(inspector.links, inspector.ids, path.parent, self.configs)
                receipt["external_links"] = links["external_links"]
                receipt["cross_reader_links"] = links["cross_reader_links"]
            self.write_json(relative, receipt)

    def add_archival_comment(self):
        body = ('<solution id="inactive-solution">\r\n'
                '<para id="inactive-answer">Archived <m:math><m:mn>6</m:mn></m:math>'
                '</para>\r\n</solution>')
        source = self.source.read_text(encoding="utf-8").replace(
            '</media></problem></exercise>',
            '</media></problem><!--' + body + '--></exercise>')
        self.replace_full_source(source)
        return body

    def add_source_urls(self):
        source = self.source.read_text(encoding="utf-8").replace(
            '</content>', '<para id="optional-links">'
            '<link url="https://example.invalid/optional?a=1&amp;b=2"/>'
            '<link url="mailto:reader@example.invalid"/>'
            '</para></content>')
        self.replace_full_source(source)

    def add_source_references(self, count=1, target="example", document=None):
        attributes = (f' target-id="{target}"' if target else '')
        attributes += (f' document="{document}"' if document else '')
        source = self.source.read_text(encoding="utf-8").replace(
            '</content>', '<para id="source-references">See ' +
            f'<link{attributes}/>' * count + '</para></content>')
        self.replace_full_source(source)

    def make_foreign_reference_target(self):
        path = self.root / "sources/m49301-foreign.cnxml"
        path.write_text(
            f'<document xmlns="{CN}" xmlns:md="{MD}">'
            '<metadata><md:content-id>m49301</md:content-id></metadata>'
            '<content><para id="para-00001">Foreign module.</para></content></document>',
            encoding="utf-8")
        reader = self.root / "review/A30-U777-foreign.vi.html"
        reader.write_text('<html><span id="para-00001">Foreign source paragraph</span>'
                          '<span id="vi-guide">Guide</span></html>', encoding="utf-8")
        self.configs["A30-U777"] = {"slug": "A30-U777-foreign", "source": "sources/m49301-foreign.cnxml"}
        self.write_json("units.json", self.configs)
        return reader

    def add_localized_mtext(self, substitutions):
        source = self.source.read_text(encoding="utf-8").replace(
            '<m:mn>2</m:mn>',
            '<m:mrow><m:mtext>if\u00a01&lt;\u00a0</m:mtext><m:mi>x</m:mi></m:mrow>', 1)
        self.replace_full_source(source)
        self.configs["A30-U001"]["math_text"] = substitutions
        self.write_json("units.json", self.configs)
        self.seal()

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
        self.write_json("provenance/m49304-rendered-equivalents.json", {
            "schema": 1, "module": "m49304", "source_module_sha256": self.original_sha,
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
        self.configs["A30-U001"]["source"] = "../m49304-escape.cnxml"
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
        relative = "provenance/m49304-rendered-equivalents.json"
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
        relative = "provenance/m49304-rendered-equivalents.json"
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

    def test_foreign_module_colliding_ids_do_not_contribute_coverage(self):
        text = self.source.read_text(encoding="utf-8").replace("abstract-p", "para-00001")
        text = text.replace("objective-list", "list-00001").replace("end-ex", "fs-id1165134380351")
        self.replace_full_source(text)
        foreign = self.root / "sources/m49301-foreign.cnxml"
        foreign.write_text(
            f'<document xmlns="{CN}" xmlns:md="{MD}">'
            '<metadata><md:content-id>m49301</md:content-id></metadata>'
            '<content><para id="para-00001">Different module.</para>'
            '<list id="list-00001"><item>Different objective.</item></list>'
            '<problem id="fs-id1165134380351">Old-module problem, not exercise.</problem>'
            '</content></document>', encoding="utf-8")
        self.configs["A30-U777"] = {"slug": "A30-foreign", "source": "sources/m49301-foreign.cnxml"}
        self.write_json("units.json", self.configs)
        result = self.run_audit()
        self.assertEqual(result["result"], "structural_checks_pass")
        self.assertNotIn("A30-U777", result["units"])
        self.assertEqual(result["module_routing"]["A30-U777"]["reason"], "explicit_other_module")
        self.assertEqual(result["counts"]["end_exercises"]["accepted_occurrences"], 1)

    def test_target_content_hidden_behind_foreign_filename_is_a_conflict(self):
        target = self.root / "sources/m49301-mislabeled.cnxml"
        target.write_bytes(self.source.read_bytes())
        self.configs["A30-U001"]["source"] = "sources/m49301-mislabeled.cnxml"
        self.write_json("units.json", self.configs)
        result = self.run_audit()
        self.assertIn("excerpt_module_conflict", self.codes(result))
        self.assertEqual(result["coverage"]["source_ids"]["accepted_unique"], 0)

    def test_conflicting_registry_and_actual_metadata_module_is_rejected(self):
        path = self.root / self.configs["A30-U001"]["source"]
        path.write_text(path.read_text().replace(
            '<metadata>', '<metadata><md:content-id>m49301</md:content-id>'), encoding="utf-8")
        self.seal()
        self.assertIn("excerpt_module_conflict", self.codes(self.run_audit()))

    def test_unclaimed_filename_requires_actual_nongeneric_source_evidence(self):
        path = self.root / "sources/extracted.cnxml"
        path.write_bytes(self.source.read_bytes())
        self.configs["A30-U001"]["source"] = "sources/extracted.cnxml"
        self.write_json("units.json", self.configs)
        self.seal()
        self.assertEqual(self.run_audit()["result"], "structural_checks_pass")
        path.write_text(f'<section xmlns="{CN}"><para id="para-00001">Words</para></section>',
                        encoding="utf-8")
        result = self.run_audit()
        self.assertEqual(result["result"], "incomplete_or_unverified")
        self.assertEqual(result["coverage"]["source_ids"]["accepted_unique"], 0)
        self.assertEqual(result["module_routing"]["A30-U001"]["reason"], "ambiguous_or_other_content")

    def test_archival_comment_has_zero_active_answers_ids_and_math(self):
        self.add_archival_comment()
        result = self.run_audit()
        self.assertEqual(result["result"], "structural_checks_pass")
        archive = result["archival_comments"]
        self.assertEqual(archive["inactive_ids"], ["inactive-solution", "inactive-answer"])
        self.assertEqual(archive["inactive_math_keys"], ["inactive-answer:0"])
        self.assertEqual(archive["active_coverage_contribution"], 0)
        self.assertEqual(archive["missing_accepted_keys"], [])
        self.assertEqual(result["coverage"]["source_mathml"]["original"], 2)
        self.assertEqual(result["counts"]["active_source_solutions"]["original"], 0)
        self.assertEqual(result["counts"]["end_exercises"]["original_sequence"][0]["active_source_solution_ids"], [])

    def test_archival_crlf_conversion_is_explicit_not_raw_byte_identity(self):
        self.add_archival_comment()
        path = self.root / self.configs["A30-U001"]["source"]
        path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n"))
        self.seal()
        result = self.run_audit()
        self.assertEqual(result["result"], "structural_checks_pass")
        original = result["archival_comments"]["source"][0]
        excerpt = result["units"]["A30-U001"]["archival_comments"][0]
        self.assertNotEqual(original["raw_payload_sha256"], excerpt["raw_payload_sha256"])
        self.assertEqual(original["lf_payload_sha256"], excerpt["lf_payload_sha256"])
        self.assertGreater(original["raw_crlf_count"], 0)
        self.assertEqual(excerpt["raw_crlf_count"], 0)

    def test_omitted_archival_payload_fails_retention_without_inventing_answer(self):
        body = self.add_archival_comment()
        path = self.root / self.configs["A30-U001"]["source"]
        path.write_bytes(path.read_bytes().replace(b"<!--" + body.encode() + b"-->", b""))
        self.seal()
        result = self.run_audit()
        self.assertIn("archival_comment_missing_or_changed", self.codes(result))
        self.assertEqual(result["counts"]["active_source_solutions"]["original"], 0)
        self.assertEqual(result["coverage"]["source_mathml"]["original"], 2)

    def test_activating_archived_answer_is_rejected_even_with_rebound_receipts(self):
        self.add_archival_comment()
        path = self.root / self.configs["A30-U001"]["source"]
        path.write_bytes(path.read_bytes().replace(b"<!--", b"").replace(b"-->", b""))
        self.seal()
        result = self.run_audit()
        self.assertIn("inactive_source_content_activated", self.codes(result))
        self.assertFalse(result["units"]["A30-U001"]["accepted_receipts"])
        self.assertEqual(result["coverage"]["source_mathml"]["original"], 2)

    def test_comment_alone_cannot_supply_an_active_source_anchor(self):
        path = self.root / self.configs["A30-U001"]["source"]
        text = path.read_text().replace('<meaning id="meaning">A rule.</meaning>',
                                        '<!--<meaning id="meaning">A rule.</meaning>-->')
        path.write_text(text, encoding="utf-8")
        self.seal()
        result = self.run_audit()
        self.assertIn("meaning", result["coverage"]["source_ids"]["missing_from_registered_excerpts"])
        self.assertNotEqual(result["result"], "structural_checks_pass")

    def test_media_image_without_figure_wrapper_is_counted_and_required(self):
        result = self.run_audit()
        self.assertEqual(result["coverage"]["source_assets"]["original_image_occurrences"], 1)
        self.assertEqual(result["source_image_media_without_figure"], ["id:media/image[1]"])
        reader = self.root / "review/A30-U001-fixture.vi.html"
        import re
        self.rebind_reader(re.sub(rb"<img\b[^>]*>", b"", reader.read_bytes()))
        result = self.run_audit()
        self.assertIn("source_image_occurrence_not_rendered", self.codes(result))

    def test_two_source_image_occurrences_cannot_be_satisfied_by_one_copy(self):
        source = self.source.read_text(encoding="utf-8").replace(
            '</media>', '<image src="../../media/fixture.jpg"/></media>')
        self.replace_full_source(source)
        result = self.run_audit()
        self.assertEqual(result["coverage"]["source_assets"]["original_unique_files"], 1)
        self.assertEqual(result["coverage"]["source_assets"]["original_image_occurrences"], 2)
        self.assertIn("source_image_occurrence_not_rendered", self.codes(result))

    def test_nested_existing_notice_schemas_require_exact_inherited_hash(self):
        relative = "provenance/fixture-asset-notices.json"
        rights = self.read_json(relative)[0]
        for field in ("rights", "inherited_rights"):
            with self.subTest(field=field):
                notice = {"unit": "A30-U001", "module": "m49304", "assets": [
                    {"filename": "fixture.jpg", "actual_sha256": digest(self.asset), field: rights}]}
                self.write_json(relative, notice)
                self.assertEqual(self.run_audit()["result"], "structural_checks_pass")
                notice["assets"][0]["actual_sha256"] = "wrong"
                self.write_json(relative, notice)
                self.assertIn("asset_notice_error", self.codes(self.run_audit()))

    def test_localized_mtext_retains_numeric_and_inequality_payload(self):
        self.add_localized_mtext({"if": "nếu"})
        result = self.run_audit()
        self.assertEqual(result["result"], "structural_checks_pass")
        rows = result["units"]["A30-U001"]["mtext_localizations"]
        self.assertEqual(rows[0]["source_text"], "if\u00a01<\u00a0")
        self.assertEqual(rows[0]["localized_text"], "nếu\u00a01<\u00a0")

    def test_numeric_mtext_change_is_not_authorized_by_localization_config(self):
        self.add_localized_mtext({"if": "nếu", "1": "2"})
        result = self.run_audit()
        self.assertIn("mtext_numeric_or_operator_payload_changed", self.codes(result))
        self.assertFalse(result["units"]["A30-U001"]["accepted_receipts"])

    def test_excerpt_mtext_nbsp_is_not_silently_normalized_as_original(self):
        self.add_localized_mtext({"if": "nếu"})
        path = self.root / self.configs["A30-U001"]["source"]
        path.write_bytes(path.read_bytes().replace("if\u00a01&lt;\u00a0".encode(), b"if 1&lt; "))
        self.seal()
        self.assertIn("source_math_mismatch", self.codes(self.run_audit()))

    def test_external_source_links_are_retained_but_never_fetched(self):
        self.add_source_urls()
        with patch("socket.create_connection", side_effect=AssertionError("unexpected network")):
            result = self.run_audit()
        self.assertEqual(result["result"], "structural_checks_pass")
        self.assertEqual(result["coverage"]["source_external_urls"]["original_occurrences"], 2)
        for row in result["units"]["A30-U001"]["external_links_unverified"]:
            self.assertFalse(row["fetched"])
            self.assertEqual(row["verification"], "unverified")

    def test_missing_source_external_link_rejected_even_with_current_link_receipt(self):
        self.add_source_urls()
        reader = self.root / "review/A30-U001-fixture.vi.html"
        import re
        data = re.sub(rb'<a href="https:[^"]+">[^<]*</a>', b"Optional source link", reader.read_bytes())
        self.rebind_reader(data, rebind_links=True)
        self.assertIn("source_external_url_not_rendered", self.codes(self.run_audit()))

    def test_external_link_receipt_cannot_claim_fetched_verification(self):
        self.add_source_urls()
        receipt = self.read_json("qa/build-A30-U001.json")
        receipt["external_links"][0]["fetched"] = True
        self.write_json("qa/build-A30-U001.json", receipt)
        self.assertIn("external_link_receipt_mismatch", self.codes(self.run_audit()))

    def test_all_math_fragments_are_checked_including_unmarked_added_math(self):
        reader = self.root / "review/A30-U001-fixture.vi.html"
        good = reader.read_bytes()
        for bad in (b"<math><mrow></math>", b"<math><mi>x</mi>",
                    b"<math><table><tr><td>x</td></tr></table></math>"):
            with self.subTest(bad=bad):
                self.rebind_reader(good.replace(b"</body>", bad + b"</body>"))
                self.assertIn("reader_math_markup_invalid", self.codes(self.run_audit()))

    def test_stale_declared_observed_counts_are_rejected(self):
        relative = "qa/build-A30-U001.json"
        receipt = self.read_json(relative)
        receipt["mathml_expressions"] = 999
        self.write_json(relative, receipt)
        self.assertIn("build_observed_count_mismatch", self.codes(self.run_audit()))

    def test_mroot_empty_index_is_preserved_and_not_pruned_as_layout(self):
        source = self.source.read_text(encoding="utf-8").replace(
            '<m:mn>2</m:mn>', '<m:mroot><m:mi>x</m:mi><m:mrow/></m:mroot>', 1)
        self.replace_full_source(source)
        self.assertEqual(self.run_audit()["result"], "structural_checks_pass")
        self.configs["A30-U001"]["prune_empty_math_layout"] = True
        self.write_json("units.json", self.configs)
        self.seal()
        self.assertIn("source_root_arity_changed_by_pruning", self.codes(self.run_audit()))

    def test_moved_source_node_cannot_keep_coverage_by_retaining_ids_and_text(self):
        path = self.root / self.configs["A30-U001"]["source"]
        phrase = '<meaning id="meaning">A rule.</meaning>'
        text = path.read_text().replace(phrase, '').replace('</media></problem>', '</media>' + phrase + '</problem>')
        path.write_text(text, encoding="utf-8")
        self.seal()
        self.assertIn("source_excerpt_parentage_mismatch", self.codes(self.run_audit()))

    def test_invalid_module_declaration_is_reported_not_crashed(self):
        self.configs["A30-U001"]["source_module"] = ["m49304"]
        self.write_json("units.json", self.configs)
        self.assertIn("unit_input_or_integrity_error", self.codes(self.run_audit()))

    def test_author_checked_but_not_root_accepted_canon_is_not_accepted(self):
        relative = "canon/review-A30-U001.json"
        receipt = self.read_json(relative)
        receipt["final_checked"] = False
        self.write_json(relative, receipt)
        result = self.run_audit()
        self.assertIn("canon_not_accepted", self.codes(result))
        self.assertEqual(result["result"], "incomplete_or_unverified")
        self.assertEqual(result["coverage"]["source_ids"]["accepted_unique"], 0)

    def test_pending_visual_with_current_hash_is_incomplete_not_accepted(self):
        relative = "qa/visual-A30-U001.json"
        receipt = self.read_json(relative)
        receipt["result"] = "pending_root"
        self.write_json(relative, receipt)
        result = self.run_audit()
        self.assertEqual(result["result"], "incomplete_or_unverified")
        self.assertEqual(result["integrity_error_count"], 0)
        self.assertEqual(result["unverified_issue_count"], 1)
        self.assertFalse(result["units"]["A30-U001"]["accepted_receipts"])

    def test_canon_acceptance_requires_actual_json_booleans_not_truthy_values(self):
        relative = "canon/review-A30-U001.json"
        good = self.read_json(relative)
        for value in ("false", "true", 1, 0, [], {}, None):
            for field in ("draft_checked", "final_checked"):
                with self.subTest(value=value, field=field):
                    receipt = deepcopy(good)
                    receipt[field] = value
                    self.write_json(relative, receipt)
                    result = self.run_audit()
                    self.assertIn("canon_acceptance_flag_type_error", self.codes(result))
                    self.assertEqual(result["result"], "integrity_errors")
                    self.assertFalse(result["units"]["A30-U001"]["accepted_receipts"])

    def test_malformed_localization_config_returns_json_integrity_error(self):
        self.add_localized_mtext({"if": "nếu"})
        for value in ([], ["bad"], "bad", None, {"if": 2}, {"": "nếu"}):
            with self.subTest(value=value):
                self.configs["A30-U001"]["math_text"] = value
                self.write_json("units.json", self.configs)
                result = self.run_audit()
                self.assertIn("unit_input_or_integrity_error", self.codes(result))
                self.assertEqual(result["result"], "integrity_errors")
                self.assertFalse(result["units"]["A30-U001"]["accepted_receipts"])

    def test_wrong_canon_example_and_receipt_types_fail_closed(self):
        relative = "canon/review-A30-U001.json"
        good = self.read_json(relative)
        for value in ("VI-C01", {"VI-C01": True}, [None], [[]]):
            with self.subTest(value=value):
                receipt = deepcopy(good)
                receipt["examples_consulted"] = value
                self.write_json(relative, receipt)
                result = self.run_audit()
                self.assertEqual(result["result"], "integrity_errors")
                self.assertFalse(result["units"]["A30-U001"]["accepted_receipts"])
        self.write_json(relative, good)
        self.write_json("qa/build-A30-U001.json", ["not an object"])
        self.assertEqual(self.run_audit()["result"], "integrity_errors")

    def test_wrong_registry_scalar_types_are_not_truthy_substitutes(self):
        good = deepcopy(self.configs["A30-U001"])
        for field, value in (("minimum_canon_examples", True), ("images", True),
                             ("prune_empty_math_layout", "false")):
            with self.subTest(field=field):
                self.configs["A30-U001"] = dict(good, **{field: value})
                self.write_json("units.json", self.configs)
                result = self.run_audit()
                self.assertEqual(result["result"], "integrity_errors")
                self.assertFalse(result["units"]["A30-U001"]["accepted_receipts"])

    def test_source_target_link_omission_is_rejected_with_rebound_receipts(self):
        self.add_source_references()
        self.assertEqual(self.run_audit()["result"], "structural_checks_pass")
        reader = self.root / "review/A30-U001-fixture.vi.html"
        self.rebind_reader(reader.read_bytes().replace(
            b'<a href="#example">Source reference</a>', b"Source reference"), rebind_links=True)
        result = self.run_audit()
        self.assertIn("source_target_reference_not_rendered", self.codes(result))
        self.assertFalse(result["units"]["A30-U001"]["accepted_receipts"])

    def test_source_reference_occurrences_need_distinct_reader_links(self):
        self.add_source_references(count=2)
        result = self.run_audit()
        self.assertEqual(result["coverage"]["source_references"]["accepted_retained_occurrences"], 2)
        reader = self.root / "review/A30-U001-fixture.vi.html"
        self.rebind_reader(reader.read_bytes().replace(
            b'<a href="#example">Source reference</a>', b"Source reference", 1), rebind_links=True)
        result = self.run_audit()
        rows = result["units"]["A30-U001"]["source_reference_retention"]
        self.assertEqual(sum(row["retained"] for row in rows), 1)
        self.assertIn("source_target_reference_not_rendered", self.codes(result))

    def test_toc_navigation_cannot_replace_a_dropped_source_reference(self):
        self.add_source_references()
        reader = self.root / "review/A30-U001-fixture.vi.html"
        data = reader.read_bytes().replace(b'<a href="#example">Source reference</a>', b"Source reference")
        data = data.replace(b"<body>", b'<body><nav id="TOC" role="doc-toc"><a href="#example">Navigation</a></nav>')
        self.rebind_reader(data, rebind_links=True)
        result = self.run_audit()
        self.assertIn("source_target_reference_not_rendered", self.codes(result))
        self.assertEqual(result["units"]["A30-U001"]["navigation_links_not_source_references"], 1)

    def test_registered_cross_reader_source_reference_resolves_actual_module_and_id(self):
        self.add_source_references()
        self.make_unit("A30-U002")
        reader = self.root / "review/A30-U001-fixture.vi.html"
        data = reader.read_bytes().replace(b'href="#example"', b'href="A30-U002-fixture.vi.html#example"')
        self.rebind_reader(data, rebind_links=True)
        result = self.run_audit()
        self.assertEqual(result["result"], "structural_checks_pass")
        row = result["units"]["A30-U001"]["source_reference_retention"][0]["reader_reference"]
        self.assertEqual(row["target_module"], "m49304")
        self.assertEqual(row["target_unit"], "A30-U002")
        self.assertTrue(row["target_is_source_id"])
        self.assertEqual(row["target_source_excerpt_sha256"], digest((self.root / self.configs["A30-U002"]["source"]).read_bytes()))

    def test_document_only_reference_can_resolve_a_vietnamese_guide_anchor(self):
        self.add_source_references(target=None, document="m49301")
        self.make_foreign_reference_target()
        reader = self.root / "review/A30-U001-fixture.vi.html"
        data = reader.read_bytes().replace(b"</body>", b'<a href="A30-U777-foreign.vi.html#vi-guide">Prior module</a></body>')
        self.rebind_reader(data, rebind_links=True)
        result = self.run_audit()
        self.assertEqual(result["result"], "structural_checks_pass")
        row = result["units"]["A30-U001"]["source_reference_retention"][0]
        self.assertEqual(row["resolution"], "source_module_only")
        self.assertFalse(row["reader_reference"]["target_is_source_id"])
        self.rebind_reader(data.replace(b'<a href="A30-U777-foreign.vi.html#vi-guide">Prior module</a>', b"Prior module"), rebind_links=True)
        self.assertIn("source_target_reference_not_rendered", self.codes(self.run_audit()))

    def test_same_anchor_in_wrong_module_cannot_satisfy_qualified_source_reference(self):
        self.replace_full_source(self.source.read_text(encoding="utf-8").replace("abstract-p", "para-00001"))
        self.add_source_references(target="para-00001", document="m49301")
        self.make_foreign_reference_target()
        reader = self.root / "review/A30-U001-fixture.vi.html"
        good = reader.read_bytes().replace(b"</body>", b'<a href="A30-U777-foreign.vi.html#para-00001">Other module</a></body>')
        self.rebind_reader(good, rebind_links=True)
        self.assertEqual(self.run_audit()["result"], "structural_checks_pass")
        wrong = good.replace(b'A30-U777-foreign.vi.html#para-00001', b'#para-00001')
        self.rebind_reader(wrong, rebind_links=True)
        self.assertIn("source_target_reference_not_rendered", self.codes(self.run_audit()))

    def test_specified_source_id_cannot_resolve_to_an_added_guide_anchor(self):
        self.add_source_references(target="vi-guide", document="m49301")
        self.make_foreign_reference_target()
        reader = self.root / "review/A30-U001-fixture.vi.html"
        data = reader.read_bytes().replace(b"</body>", b'<a href="A30-U777-foreign.vi.html#vi-guide">Guide</a></body>')
        self.rebind_reader(data, rebind_links=True)
        result = self.run_audit()
        self.assertIn("source_target_reference_not_rendered", self.codes(result))
        self.assertFalse(result["units"]["A30-U001"]["accepted_receipts"])

    def test_external_url_multiplicity_is_preserved(self):
        self.add_source_urls()
        source = self.source.read_text(encoding="utf-8").replace(
            '<link url="mailto:reader@example.invalid"/>',
            '<link url="mailto:reader@example.invalid"/><link url="mailto:reader@example.invalid"/>')
        self.replace_full_source(source)
        self.assertEqual(self.run_audit()["result"], "structural_checks_pass")
        reader = self.root / "review/A30-U001-fixture.vi.html"
        self.rebind_reader(reader.read_bytes().replace(
            b'<a href="mailto:reader@example.invalid">Optional source link</a>', b"Optional source link", 1), rebind_links=True)
        self.assertIn("source_external_url_not_rendered", self.codes(self.run_audit()))

    def test_foreign_or_mixed_namespace_cannot_masquerade_as_mathml_number(self):
        reader = self.root / "review/A30-U001-fixture.vi.html"
        good = reader.read_bytes()
        for replacement in (b'<bad:mn xmlns:bad="urn:not-mathml">2</bad:mn>', b'<mn xmlns="">2</mn>'):
            with self.subTest(replacement=replacement):
                self.rebind_reader(good.replace(b'<mn>2</mn>', replacement, 1))
                result = self.run_audit()
                self.assertIn("reader_math_namespace_invalid", self.codes(result))
                self.assertFalse(result["units"]["A30-U001"]["accepted_receipts"])
        bare = good.replace(f' xmlns="{MATH}"'.encode(), b'')
        self.rebind_reader(bare)
        self.assertEqual(self.run_audit()["result"], "structural_checks_pass")

    def test_malformed_json_container_shapes_report_errors_without_crashing(self):
        self.write_json("provenance/fixture-asset-notices.json", ["bad row"])
        self.assertIn("asset_notice_error", self.codes(self.run_audit()))
        self.write_json("provenance/m49304-rendered-equivalents.json", [])
        self.assertIn("equivalence_ledger_error", self.codes(self.run_audit()))
        self.write_json("units.json", {"A30-U001": []})
        result = self.run_audit()
        self.assertIn("unit_input_or_integrity_error", self.codes(result))
        self.assertEqual(result["result"], "integrity_errors")

    def test_plain_cli_emits_utf8_json_even_with_cp1252_stdout_default(self):
        source = self.root / "nguồn-kiểm-tra.cnxml"
        source.write_bytes(self.source.read_bytes())
        environment = dict(os.environ, PYTHONIOENCODING="cp1252", PYTHONDONTWRITEBYTECODE="1")
        process = subprocess.run(
            [sys.executable, "-B", str(Path(__file__).with_name("audit_m49304.py")),
             "--root", str(self.root), "--source", str(source)],
            capture_output=True, env=environment, check=False)
        self.assertEqual(process.returncode, 1)  # Fixture deliberately is not the production source pin.
        self.assertEqual(process.stderr, b"")
        result = json.loads(process.stdout.decode("utf-8"))
        self.assertEqual(result["result"], "integrity_errors")
        self.assertIn("nguồn-kiểm-tra.cnxml", result["source"]["path"])

    def test_sixty_one_exercises_counted_from_source_not_registry_claims(self):
        text = self.source.read_text(encoding="utf-8").replace(
            '</section></content>', ''.join(
                f'<exercise id="extra-ex-{i}"><problem id="extra-p-{i}">Prompt {i}</problem></exercise>'
                for i in range(2, 62)) + '</section></content>')
        self.replace_full_source(text)
        self.configs["A30-U001"]["selected_end_exercises"] = 999
        self.write_json("units.json", self.configs)
        result = self.run_audit()
        self.assertEqual(result["counts"]["end_exercises"]["original"], 61)
        self.assertEqual(result["counts"]["end_exercises"]["accepted_reader_unique"], 61)
        self.assertEqual(result["counts"]["end_exercises"]["original_sequence"][-1]["number"], 61)
        self.write_json("units.json", {})
        result = self.run_audit()
        self.assertEqual(result["result"], "incomplete_or_unverified")
        self.assertEqual(result["counts"]["end_exercises"]["accepted_reader_unique"], 0)


if __name__ == "__main__":
    unittest.main()
