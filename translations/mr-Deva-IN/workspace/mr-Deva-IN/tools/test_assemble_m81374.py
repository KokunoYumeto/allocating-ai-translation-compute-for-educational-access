"""Assembler-author regressions; no reader, browser, HTML or PDF acceptance.

Stdlib only.  The portability test copies only receipt-listed repository inputs
and forbids ZIP access before reproducing the exact XML and receipt bytes.
"""
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock
import xml.etree.ElementTree as ET

import assemble_m81374 as a


def normalized_copy(node):
    """Undo only documented assembly transport; retain authored content."""
    node = deepcopy(node)
    for current in node.iter():
        if current.get("data-origin-id"):
            current.set("id", current.get("data-origin-id"))
        if current.get("data-origin-check"):
            current.set("data-check", current.get("data-origin-check"))
        if current.get("data-origin-src"):
            current.set("src", current.get("data-origin-src"))
        if current.get("data-prior-href") is not None:
            current.set("href", current.get("data-prior-href"))
        elif current.tag == "a" and current.get("href", "").startswith("#MR-BRIDGE-"):
            current.set("href", "#" + current.get("href").split("--", 1)[1])
        for key in ("data-origin-unit", "data-origin-id", "data-origin-check", "data-origin-src",
                    "data-source-tag", "data-prior-href", "data-assembly-note",
                    "data-assembly-header-note"):
            current.attrib.pop(key, None)
    return node


def remove_node(root, node):
    parent = next(parent for parent in root.iter() if node in list(parent))
    parent.remove(node)


class AssemblyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assembly = a.Assembly()
        cls.raw, cls.receipt_raw = cls.assembly.build()
        cls.root = ET.fromstring(cls.raw)
        cls.ids = a.unique_index(cls.root)
        cls.receipt = json.loads(cls.receipt_raw, object_pairs_hook=a.object_pairs)
        cls.source = cls.assembly.source
        cls.source_index = cls.assembly.source_index

    def test_01_exact_current_rebuild_and_nonreader_status(self):
        self.assertEqual((a.BASE / a.OUTPUT).read_bytes(), self.raw)
        self.assertEqual((a.BASE / a.RECEIPT).read_bytes(), self.receipt_raw)
        self.assertEqual(self.root.get("data-status"), "assembled-translation-draft")
        self.assertEqual(self.root.get("data-reader-accepted"), "false")
        self.assertFalse(self.receipt["reader_accepted"])
        self.assertFalse(self.receipt["pdf_generated"])
        self.assertFalse(self.receipt["full_workflow_complete"])
        self.assertEqual(self.receipt["output"], {"path": a.OUTPUT, "sha256": a.sha(self.raw),
                                                  "bytes": len(self.raw)})
        self.assertNotIn(b"file://", self.raw)
        self.assertNotIn(b"C:\\", self.receipt_raw)

    def test_02_raw_source_pins_full_tree_and_metadata(self):
        for locale, pin in a.SOURCE_PINS.items():
            raw = (a.BASE / a.SOURCE_DIR / (locale + "-m81374.cnxml")).read_bytes()
            self.assertEqual((len(raw), a.sha(raw)), (pin[3], pin[2]))
            source = ET.fromstring(raw)
            self.assertEqual(sum(1 for _ in source.iter()), 7223)
            self.assertEqual(a.source_ids(source), list(self.source_index))
            metadata = source.find(a.C + "metadata")
            self.assertEqual(a.text(metadata.find(a.MD + "content-id")), "m81374")
            self.assertEqual(a.text(metadata.find(a.MD + "uuid")), a.UUID)
        self.assertEqual(a.normalized_text(self.root.find("header/h1")), "फलनांचे आलेख")
        self.assertEqual(self.root.get("data-source-document"), "m81374")
        self.assertEqual(self.root.get("data-source-uuid"), a.UUID)
        self.assertIn("Graphs of Functions", a.text(self.root.find("header")))
        self.assertIn("Grafik Fungsi", a.text(self.root.find("header")))

    def test_03_all_1366_ids_in_exact_order_and_ancestry(self):
        source_ids = a.source_ids(self.source)
        self.assertEqual(len(source_ids), 1366)
        self.assertEqual(len(set(source_ids)), 1366)
        actual = [node.get("id") for node in self.root.iter() if node.get("id") in self.source_index]
        self.assertEqual(actual, source_ids)
        for identity, original in self.source_index.items():
            current = [node.get("id") for node in self.ids[identity].iter()
                       if node.get("id") in self.source_index]
            self.assertEqual(current, a.source_ids(original), identity)

    def test_04_380_ordered_nonnested_selectors_cover_1352_ids(self):
        selected = [node for node in self.root.iter()
                    if node.get("data-source", "").startswith("A20:m81374#")]
        self.assertEqual(len(selected), 380)
        self.assertEqual(len({node.get("id") for node in selected}), 380)
        covered = Counter(identity for node in selected
                          for identity in a.source_ids(self.source_index[node.get("id")]))
        self.assertEqual(set(covered.values()), {1})
        self.assertEqual(len(covered), 1352)
        self.assertEqual(set(self.source_index) - set(covered), set(a.WRAPPER_OWNERS))
        by_unit = Counter(node.get("data-origin-unit") for node in selected)
        self.assertEqual(tuple(by_unit[unit] for unit in a.UNITS), a.EXPECTED_COUNTS)

    def test_05_every_selected_translation_is_preserved_after_transport(self):
        for identity, (unit, original) in self.assembly.selected.items():
            self.assertEqual(a.signature(normalized_copy(self.ids[identity])), a.signature(original),
                             (unit, identity))

    def test_06_fourteen_wrappers_and_one_collapsed_chapter_review(self):
        for identity, owner in a.WRAPPER_OWNERS.items():
            wrapper = self.ids[identity]
            self.assertEqual(wrapper.get("data-kind"), "source-context")
            self.assertEqual(wrapper.get("data-origin-unit"), owner)
            self.assertIsNone(wrapper.get("data-source"))
            headings = [child for child in wrapper if child.tag in {"h2", "h3", "h4", "h5", "h6"}]
            self.assertEqual(len(headings), 1, identity)
        chapter = self.ids["fs-id1167836524742"]
        source_chapter = self.source_index["fs-id1167836524742"]
        expected_children = [child.get("id") for child in source_chapter if child.get("id")]
        actual_children = [child.get("id") for child in chapter if child.get("id") in a.WRAPPER_OWNERS]
        self.assertEqual(actual_children, expected_children)
        self.assertEqual([self.ids[identity].get("data-origin-unit") for identity in actual_children],
                         list(a.UNITS[4:10]))
        self.assertEqual(sum(node.get("id") == "fs-id1167836524742" for node in self.root.iter()), 1)

    def test_07_all_26_outer_notes_plus_header_clarification_preserved(self):
        markers = {node.get("data-assembly-note"): node for node in self.root.iter()
                   if node.get("data-assembly-note")}
        self.assertEqual(len(markers), 26)
        self.assertEqual(len(self.receipt["outer_authored_node_dispositions"]), 26)
        for record in self.receipt["outer_authored_node_dispositions"]:
            marker = f"{record['unit']}:{record['outer_note_index']}"
            original = self.assembly.outer_notes(self.assembly.roots[record["unit"]])[record["outer_note_index"]]
            self.assertEqual(a.signature(normalized_copy(markers[marker])), a.signature(original), marker)
            self.assertEqual(record["treatment"], "retain complete node")
        header_notes = [node for node in self.root.iter() if node.get("data-assembly-header-note")]
        self.assertEqual(len(header_notes), 1)
        original = self.assembly.roots["MR-BRIDGE-013"].find("header/aside")
        self.assertEqual(a.signature(normalized_copy(header_notes[0])), a.signature(original))

    def test_08_255_exercises_141_supplied_114_explicit_omissions(self):
        exercises = list(self.source.iter(a.C + "exercise"))
        self.assertEqual(len(exercises), 255)
        self.assertEqual(len(list(self.source.iter(a.C + "solution"))), 141)
        omissions = 0
        for source in exercises:
            target = self.ids[source.get("id")]
            problem = source.find(a.C + "problem")
            supplied = source.find(a.C + "solution")
            self.assertIn(problem.get("id"), a.source_ids(target))
            missing = a.Assembly.omission_nodes(target)
            if supplied is None:
                self.assertEqual(len(missing), 1, source.get("id"))
                omissions += 1
            else:
                self.assertFalse(missing, source.get("id"))
                self.assertIn(supplied.get("id"), a.source_ids(target))
                hrefs = [link.get("href") for link in target.iter("a")]
                self.assertIn("#" + supplied.get("id"), hrefs)
                self.assertIn("#" + problem.get("id"), hrefs)
        self.assertEqual(omissions, 114)
        self.assertFalse(any(identity.startswith("mr-answer-") for identity in self.ids))

    def test_09_481_source_mathml_and_685_exact_namespaced_checks(self):
        self.assertEqual(len(list(self.source.iter(a.M + "math"))), 481)
        checks = {node.get("data-check"): a.text(node) for node in self.root.iter()
                  if node.get("data-check")}
        self.assertEqual(len(checks), 685)
        self.assertTrue(all("::" in key for key in checks))
        self.assertEqual(checks, self.receipt["expected_math"])
        self.assertEqual(checks["MR-BRIDGE-013::all-reals"], "(−∞, ∞)")
        self.assertEqual(checks["MR-BRIDGE-013::nonnegative"], "[0, ∞)")

    def test_10_all_149_exact_canonical_en_assets_in_source_order(self):
        images = list(self.root.iter("img"))
        self.assertEqual(len(images), 149)
        self.assertEqual(len(self.receipt["assets"]), 149)
        self.assertEqual(sum(record["bytes"] for record in self.receipt["assets"].values()), 9908130)
        source_names = [Path(node.get("src")).name for node in self.source.iter(a.C + "image")]
        target_names = [node.get("data-origin-src")[6:] for node in images]
        self.assertEqual(target_names, source_names)
        self.assertEqual(len(set(target_names)), 149)
        for node in images:
            relative = node.get("src").removeprefix("../")
            pin = self.receipt["assets"][relative]
            raw = a.safe_path(a.BASE, relative).read_bytes()
            self.assertEqual((len(raw), a.sha(raw)), (pin["bytes"], pin["sha256"]))
            self.assertTrue(node.get("alt"))

    def test_11_nine_self_rating_cells_remain_empty(self):
        tables = [node for node in self.root.iter("table")
                  if node.get("data-origin-id") == "MR-BRIDGE-015-self-rating"]
        self.assertEqual(len(tables), 1)
        cells = list(tables[0].iter("td"))
        self.assertEqual(len(cells), 9)
        self.assertTrue(all(not cell.attrib and len(cell) == 0 and not a.normalized_text(cell) for cell in cells))

    def test_12_two_linear_table_adaptations_account_for_7_rows_14_entries(self):
        rows = entries = 0
        for identity, policy in a.TABLE_ADAPTATIONS.items():
            source = self.source_index[identity]
            target = self.ids[identity]
            current_rows = len(list(source.iter(a.C + "row")))
            current_entries = len(list(source.iter(a.C + "entry")))
            self.assertEqual((current_rows, current_entries),
                             (policy["source_rows"], policy["source_entries"]))
            self.assertEqual(target.tag, "div")
            self.assertFalse(list(target.iter("table")))
            rows += current_rows; entries += current_entries
        self.assertEqual((rows, entries), (7, 14))
        first = self.ids["fs-id1167836688758"]
        second = self.ids["fs-id1167836560655"]
        self.assertIn("m = −2", a.text(first)); self.assertIn("b = −4", a.text(first))
        self.assertIn("(0, 4)", a.text(second))

    def test_13_same_module_links_local_outside_module_links_https(self):
        links = [node for node in self.root.iter("a")
                 if node.get("data-source-document") is not None
                 or node.get("data-source-target-id") is not None]
        local = [node for node in links if node.get("data-source-document", "m81374") == "m81374"]
        external = [node for node in links if node.get("data-source-document", "m81374") != "m81374"]
        self.assertEqual((len(local), len(external)), (6, 8))
        self.assertTrue(all(node.get("href", "").startswith("#") for node in local))
        self.assertTrue(all(node.get("data-prior-href") is not None for node in local))
        self.assertTrue(all(node.get("href", "").startswith("https://") for node in external))
        self.assertEqual(sum(node.get("href") == "https://openstax.org/l/37domainrange"
                             for node in self.root.iter("a")), 1)
        for node in self.root.iter("a"):
            if node.get("href", "").startswith("#"):
                self.assertIn(node.get("href")[1:], self.ids)

    def test_14_one_synthesized_header_footer_and_explicit_dispositions(self):
        self.assertEqual(len(self.root.findall("header")), 1)
        self.assertEqual(len(self.root.findall("footer")), 1)
        self.assertEqual(self.root.find("footer").get("id"), "credits")
        policy = self.receipt["footer_policy"]
        self.assertEqual(policy["synthesized_module_footers"], 1)
        self.assertEqual(len(policy["unit_footer_dispositions"]), 11)
        self.assertEqual(len(self.receipt["header_policy"]["unit_header_dispositions"]), 11)
        self.assertEqual(self.receipt["header_policy"]["objective_selectors_retained"],
                         ["para-00001", "list-00001"])
        self.assertIn("not a complete A20 book", " ".join(self.receipt["limits"]))

    def test_15_default_rebuild_is_exact_portable_and_pin_drift_fails(self):
        with tempfile.TemporaryDirectory(prefix="mr-m81374-rebuild-") as temporary:
            base = Path(temporary) / "mr-Deva-IN"
            for relative, pin in self.receipt["inputs"].items():
                self.assertFalse(relative.startswith("downloads/"))
                source = a.safe_path(a.BASE, relative)
                self.assertEqual((source.stat().st_size, a.sha(source.read_bytes())),
                                 (pin["bytes"], pin["sha256"]))
                destination = a.safe_path(base, relative)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
            self.assertFalse((base.parent / "downloads").exists())
            with mock.patch.object(a.zipfile, "ZipFile", side_effect=AssertionError("archive access forbidden")):
                raw, receipt = a.Assembly(base).build()
            self.assertEqual(raw, self.raw)
            self.assertEqual(receipt, self.receipt_raw)
            witness = base / a.SOURCE_DIR / "en-m81374.cnxml"
            witness.write_bytes(witness.read_bytes() + b"drift")
            with self.assertRaisesRegex(ValueError, "raw source witness drift"):
                a.Assembly(base)

    def test_16_missing_id_fails(self):
        changed = deepcopy(self.root)
        next(node for node in changed.iter() if node.get("id") == "fs-id1167836579284").set("id", "missing")
        with self.assertRaises(ValueError):
            self.assembly.validate(changed)

    def test_17_extra_duplicate_id_fails(self):
        changed = deepcopy(self.root)
        changed.find(".//*[@id='assembly-content']").append(ET.Element("p", {"id": "fs-id1167836579284"}))
        with self.assertRaisesRegex(ValueError, "duplicate ID"):
            self.assembly.validate(changed)

    def test_18_reordered_ids_fail(self):
        changed = deepcopy(self.root)
        content = changed.find(".//*[@id='assembly-content']")
        first, second = content[0], content[1]
        content.remove(first); content.remove(second)
        content.insert(0, second); content.insert(1, first)
        with self.assertRaises(ValueError):
            self.assembly.validate(changed)

    def test_19_answer_and_omission_mutations_fail(self):
        supplied = deepcopy(self.root)
        exercise = next(source for source in self.source.iter(a.C + "exercise")
                        if source.find(a.C + "solution") is not None)
        solution_id = exercise.find(a.C + "solution").get("id")
        current = next(node for node in supplied.iter() if node.get("id") == exercise.get("id"))
        link = next(node for node in current.iter("a") if node.get("href") == "#" + solution_id)
        remove_node(current, link)
        with self.assertRaises(ValueError):
            self.assembly.validate(supplied)
        omitted = deepcopy(self.root)
        exercise = next(source for source in self.source.iter(a.C + "exercise")
                        if source.find(a.C + "solution") is None)
        current = next(node for node in omitted.iter() if node.get("id") == exercise.get("id"))
        note = a.Assembly.omission_nodes(current)[0]
        note.text = "उत्तर भरलेले आहे."
        with self.assertRaises(ValueError):
            self.assembly.validate(omitted)

    def test_20_check_image_and_unsafe_route_mutations_fail(self):
        changed = deepcopy(self.root)
        node = next(node for node in changed.iter() if node.get("data-check") == "MR-BRIDGE-013::example1-slope")
        node.text = "m = 2"
        with self.assertRaises(ValueError):
            self.assembly.validate(changed)
        changed = deepcopy(self.root)
        next(changed.iter("img")).set("src", "../assets/../../outside.jpg")
        with self.assertRaises(ValueError):
            self.assembly.validate(changed)
        changed = deepcopy(self.root)
        next(changed.iter("a")).set("href", "file:///private")
        with self.assertRaises(ValueError):
            self.assembly.validate(changed)

    def test_21_unsafe_paths_duplicate_json_and_staging_failure_fail_closed(self):
        for path in ("../outside", "C:/private", "a\\b", "/tmp/outside"):
            with self.assertRaises(ValueError):
                a.safe_path(a.BASE, path)
        with self.assertRaises(ValueError):
            json.loads('{"a":1,"a":2}', object_pairs_hook=a.object_pairs)
        with tempfile.TemporaryDirectory(prefix="mr-m81374-stage-") as temporary:
            base = Path(temporary)
            (base / "one.xml").write_bytes(b"previous-one")
            (base / "two.json").write_bytes(b"previous-two")
            original = Path.write_bytes
            counter = [0]
            def fail_second(path, raw):
                counter[0] += 1
                if counter[0] == 2:
                    raise OSError("simulated staging failure")
                return original(path, raw)
            with mock.patch.object(Path, "write_bytes", fail_second):
                with self.assertRaises(OSError):
                    a.stage_write(base, {"one.xml": b"new-one", "two.json": b"new-two"})
            self.assertEqual((base / "one.xml").read_bytes(), b"previous-one")
            self.assertEqual((base / "two.json").read_bytes(), b"previous-two")


if __name__ == "__main__":
    unittest.main(verbosity=2)
