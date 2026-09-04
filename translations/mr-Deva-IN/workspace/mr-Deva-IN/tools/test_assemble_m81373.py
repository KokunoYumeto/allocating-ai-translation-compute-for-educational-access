"""Assembler-author regressions, not independent review or reader acceptance.

Stdlib only. No ignored archives, network, browser or HTML/PDF needed. A bounded
temporary repo copy contains only the small receipt-listed rebuild inputs.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock
import xml.etree.ElementTree as ET

import assemble_m81373 as a


def normalized_copy(node):
    """Undo only documented transport attributes/link routes; retain content."""
    node = deepcopy(node)
    for current in node.iter():
        if current.get("data-origin-id"):
            current.set("id", current.get("data-origin-id"))
        if current.get("data-origin-check"):
            current.set("data-check", current.get("data-origin-check"))
        if current.get("data-origin-src"):
            current.set("src", current.get("data-origin-src"))
        if current.get("data-prior-href"):
            current.set("href", current.get("data-prior-href"))
            current.text = current.get("data-prior-label")
        elif current.tag == "a" and current.get("href", "").startswith("#MR-BRIDGE-"):
            current.set("href", "#" + current.get("href").split("--", 1)[1])
        for key in ("data-origin-unit", "data-origin-id", "data-origin-check", "data-origin-src",
                    "data-source-tag", "data-prior-href", "data-prior-label"):
            current.attrib.pop(key, None)
    return node


class AssemblyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assembly = a.Assembly()
        cls.raw, cls.receipt_raw = cls.assembly.build()
        cls.root = ET.fromstring(cls.raw)
        cls.ids = a.unique_index(cls.root)
        cls.receipt = json.loads(cls.receipt_raw)
        cls.source = cls.assembly.source
        cls.source_index = cls.assembly.source_index

    def test_01_exact_current_rebuild_and_pending_status(self):
        self.assertEqual((a.BASE / a.OUTPUT).read_bytes(), self.raw)
        self.assertEqual((a.BASE / a.RECEIPT).read_bytes(), self.receipt_raw)
        self.assertEqual(self.root.get("data-status"), "assembled-translation-draft")
        self.assertEqual(self.root.get("data-reader-accepted"), "false")
        self.assertFalse(self.receipt["reader_accepted"])
        self.assertFalse(self.receipt["full_workflow_complete"])
        self.assertEqual(self.receipt["output"]["sha256"], a.sha(self.raw))
        self.assertEqual(self.receipt["output"]["bytes"], len(self.raw))
        self.assertNotIn(b"file://", self.raw)
        self.assertNotIn(b"C:\\", self.receipt_raw)

    def test_02_raw_source_pins_and_full_metadata(self):
        for locale, pin in a.SOURCE_PINS.items():
            raw = (a.BASE / a.SOURCE_DIR / (locale + "-m81373.cnxml")).read_bytes()
            self.assertEqual(a.sha(raw), pin[2])
            self.assertEqual(len(raw), pin[3])
            source = ET.fromstring(raw)
            metadata = source.find(a.C + "metadata")
            self.assertEqual(a.text(metadata.find(a.MD + "content-id")), "m81373")
            self.assertEqual(a.text(metadata.find(a.MD + "uuid")), "59fe6dc4-6e09-4a88-aa1c-b5f72bd79a20")
            self.assertEqual(a.source_ids(source), list(self.source_index))
        self.assertEqual(a.text(self.root.find("header/h1")), "संबंध आणि फलने")
        self.assertEqual(self.root.get("data-source-document"), "m81373")
        self.assertEqual(self.root.get("data-source-uuid"), a.UUID)
        self.assertIn("Relations and Functions", a.text(self.root.find("header")))
        self.assertIn("Relasi dan Fungsi", a.text(self.root.find("header")))

    def test_03_every_625_canonical_id_order_and_ancestry(self):
        source_ids = a.source_ids(self.source)
        self.assertEqual(len(source_ids), 625)
        self.assertEqual(len(set(source_ids)), 625)
        actual = [n.get("id") for n in self.root.iter() if n.get("id") in self.source_index]
        self.assertEqual(actual, source_ids)
        for sid, original in self.source_index.items():
            self.assertEqual([n.get("id") for n in self.ids[sid].iter() if n.get("id") in self.source_index],
                             a.source_ids(original), sid)

    def test_04_134_nonoverlapping_selections_exact_011_replacement(self):
        selected = [n for n in self.root.iter() if n.get("data-source", "").startswith("A20:m81373#")]
        self.assertEqual(len(selected), 134)
        self.assertEqual(len({n.get("id") for n in selected}), 134)
        covered = Counter(sid for n in selected for sid in a.source_ids(self.source_index[n.get("id")]))
        self.assertEqual(set(covered.values()), {1})
        self.assertEqual(len(covered), 619)
        by_unit = Counter(n.get("data-origin-unit") for n in selected)
        self.assertEqual(tuple(by_unit[u] for u in a.UNITS), (4, 1, 16, 16, 31, 9, 21, 14, 18, 4))
        self.assertNotIn("MR-BRIDGE-001", by_unit)
        self.assertEqual({n.get("id") for n in selected if n.get("data-origin-unit") == "MR-BRIDGE-011"}, set(a.REPLACED))
        self.assertEqual(a.sha((a.BASE / "translations/MR-BRIDGE-001.xml").read_bytes()), a.LEGACY_SHA)
        self.assertEqual(a.sha((a.BASE / "translations/MR-BRIDGE-002.xml").read_bytes()),
                         "0a46a929a80df9755bc4f4df95102049c524f2506daf03c37952a368f01a1172")

    def test_05_all_133_unrepaired_selections_preserve_entire_translation(self):
        for sid, (unit, original) in self.assembly.selected.items():
            if sid == "fs-id1167833158753":
                continue
            self.assertEqual(a.signature(normalized_copy(self.ids[sid])), a.signature(original), (unit, sid))

    def test_06_sylvia_repair_restores_four_rows_original_media_and_prose(self):
        table = self.ids["fs-id1167829709312"]
        self.assertEqual(table.tag, "table")
        rows = table.findall("tbody/tr")
        self.assertEqual(len(rows), 4)
        expected = (
            ("fs-id1167829850506", "N(t) = 75 + 10t"),
            ("fs-id1167832971244", "N(5) = 75 + 10 · 5"),
            ("fs-id1167833270224", "N(5) = 75 + 50"),
            ("fs-id1167833309949", "N(5) = 125"),
        )
        for row, (sid, equation) in zip(rows, expected):
            self.assertEqual([n.get("id") for n in row.iter() if n.get("id")], [sid])
            self.assertEqual(a.text(row[1]), equation)
        self.assertEqual([a.text(row[0]) for row in rows], ["", "येथे t = 5 ठेवा.", "सोपी करा.", ""])
        problem = self.ids["fs-id1167836533836"]
        self.assertNotIn("fs-id1167829850506", a.source_ids(problem))
        self.assertIn("N(t) = 75 + 10t", a.text(problem))
        self.assertIn("या उत्तराचा अर्थ स्पष्ट करा", a.text(self.ids["fs-id1167833347223"]))
        self.assertIn("दिवसांच्या संख्येचे फलन", a.text(self.ids["fs-id1167829715385"]))
        self.assertEqual(Fraction(75) + Fraction(10) * 5, Fraction(125))
        for locale, source in self.assembly.sources.items():
            source_table = next(n for n in source.iter() if n.get("id") == table.get("id"))
            for row, (sid, _) in zip(source_table.iter(a.C + "row"), expected):
                self.assertEqual([n.get("id") for n in row.iter(a.C + "media")], [sid])

    def test_07_every_source_table_row_and_media_order_preserved(self):
        tables = list(self.source.iter(a.C + "table"))
        self.assertEqual(len(tables), 12)
        linear = {
            "fs-id1167836429672": (3, ["y = −2x + 7", "उदाहरणार्थ, x = 3 असताना:", "y = −2 · 3 + 7", "y = 1"]),
            "fs-id1167836533787": (3, ["y = x² + 1", "उदाहरणार्थ, x = 2 असताना:", "y = 2² + 1", "y = 5"]),
            "fs-id1167829596595": (5, ["x + y² = 3", "y असलेले पद एका बाजूला वेगळे काढा.", "y² = −x + 3", "x = 2 ठेवू.", "y² = −2 + 3", "y² = 1", "यामुळे y ची दोन मूल्ये मिळतात: y = 1 आणि y = −1."]),
        }
        for source in tables:
            target = self.ids[source.get("id")]
            if source.get("id") in linear:
                row_count, paragraphs = linear[source.get("id")]
                self.assertEqual(len(list(source.iter(a.C + "row"))), row_count)
                self.assertEqual(target.get("data-kind"), "adaptation")
                self.assertEqual([" ".join(a.text(n).split()) for n in target], paragraphs)
                self.assertEqual([n.get("id") for n in source.iter(a.C + "media")],
                                 [n.get("id") for n in target.iter() if n.get("id") in self.source_index and n is not target])
                continue
            if target.tag != "table":
                target = target.find("table")
            self.assertIsNotNone(target)
            old_rows, rows = list(source.iter(a.C + "row")), target.findall("tbody/tr")
            self.assertEqual(len(old_rows), len(rows))
            for old, new in zip(old_rows, rows):
                self.assertEqual([n.get("id") for n in old.iter(a.C + "media")],
                                 [n.get("id") for n in new.iter() if n.get("id") in self.source_index])

    def test_08_84_exercises_55_source_answers_29_authored_answers(self):
        exercises = list(self.source.iter(a.C + "exercise"))
        self.assertEqual(len(exercises), 84)
        self.assertEqual(len(list(self.source.iter(a.C + "solution"))), 55)
        authored = []
        for source in exercises:
            target = self.ids[source.get("id")]
            supplied = source.find(a.C + "solution")
            sid = supplied.get("id") if supplied is not None else "mr-answer-" + source.get("id")
            self.assertIn(sid, a.source_ids(target))
            if supplied is None:
                authored.append(sid)
                self.assertEqual(self.ids[sid].get("data-kind"), "original")
            else:
                self.assertNotEqual(self.ids[sid].get("data-kind"), "original")
            pid = source.find(a.C + "problem").get("id")
            self.assertIn("#" + sid, [n.get("href") for n in self.ids[pid].iter("a")])
            self.assertIn("#" + pid, [n.get("href") for n in self.ids[sid].iter("a")])
        self.assertEqual(len(authored), 29)
        self.assertEqual(set(authored), {sid for sid in self.ids if sid.startswith("mr-answer-fs-id")})

    def test_09_missing_wrappers_headings_objectives_and_five_glossary_entries(self):
        wrapper = self.ids["fs-id1167826170977"]
        self.assertEqual(wrapper.get("data-source-class"), "section-exercises")
        self.assertIn("fs-id1167826189010", a.source_ids(wrapper))
        self.assertEqual(a.text(self.ids["fs-id1167826189010"].find("h2")), "सरावातून प्रावीण्य")
        for sid, (_, heading) in a.CONTEXTS.items():
            self.assertEqual(a.text(self.ids[sid].find("h2")), heading)
            self.assertIsNone(self.ids[sid].get("data-source"))
        self.assertEqual(len(self.ids["list-00001"].findall("ul/li")), 3)
        glossary = self.ids["assembly-glossary"]
        self.assertEqual([n.get("id") for n in glossary if n.get("id")],
                         [n.get("id") for n in self.source.find(a.C + "glossary")])
        self.assertEqual(len(self.source.find(a.C + "glossary")), 5)

    def test_10_three_present_refs_local_three_untranslated_refs_external(self):
        links = [n for n in self.root.iter("a") if n.get("data-source-document")]
        self.assertEqual(len(links), 6)
        local = [n for n in links if n.get("data-source-document") == "m81373"]
        self.assertEqual(Counter(n.get("data-source-target-id") for n in local),
                         {"fs-id1167829683746": 2, "fs-id1167833057329": 1})
        for n in local:
            self.assertEqual(n.get("href"), "#" + n.get("data-source-target-id"))
            self.assertTrue(n.get("data-prior-href").startswith("https://"))
            self.assertNotIn("इंग्रजी स्रोत-दुवा", a.text(n))
        external = [n for n in links if n.get("data-source-document") == "m81422"]
        self.assertEqual(Counter(n.get("data-source-target-id") for n in external),
                         {"fs-id1167836530265": 2, "fs-id1167836652573": 1})
        for n in external:
            self.assertTrue(n.get("href").startswith("https://"))
            self.assertNotIn(n.get("data-source-target-id"), self.ids)
        for n in self.root.iter("a"):
            if n.get("href", "").startswith("#"):
                self.assertIn(n.get("href")[1:], self.ids)
        self.assertEqual(sum(n.get("href") == "https://openstax.org/l/37introfunction" for n in self.root.iter("a")), 1)

    def test_11_original_notes_source_corrections_and_no_excerpt_exclusions(self):
        visible = a.text(self.root)
        for phrase in ("BMI हा उंचीच्या तुलनेतील वजनाचा निर्देशांक", "बिंदू जोडून", "संचात पुनरावृत्ती लिहू नका",
                       "प्रांताबाहेर", "निव्वळ वाढ", "दूरध्वनी क्रमांकांतील आडव्या खुणा", "संपूर्ण राशी", "सार्वत्रिक नियम नाही"):
            self.assertIn(phrase, visible)
        for obsolete in ("ते येथे पुन्हा छापलेले किंवा मोजलेले नाही", "येथे वगळली आहे", "या घटकात पहिल्या उद्दिष्टावरील विभाग",
                         "सध्याच्या वाचकात एका ऑफलाइन घटकातून दुसऱ्यात", "या चार स्रोतनोंदींचा हा पहिलाच अनुवाद"):
            self.assertNotIn(obsolete, visible)
        bmi = self.ids["MR-BRIDGE-004--bmi-note"]
        self.assertEqual(bmi.get("data-kind"), "original")
        self.assertEqual(sum(n.get("href") == "#MR-BRIDGE-004--bmi-note" for n in self.root.iter("a")), 2)
        self.assertNotIn("MR-BRIDGE-002--P1", self.ids)
        self.assertNotIn("MR-BRIDGE-002--S-P1", self.ids)

    def test_12_self_check_remains_unanswered(self):
        checklist = self.ids["MR-BRIDGE-007--mr-checklist"]
        rows = checklist.findall("tbody/tr")
        self.assertEqual(len(rows), 3)
        self.assertEqual([[a.text(n) for n in row.findall("td")] for row in rows], [["□"] * 3] * 3)
        before = self.assembly.roots["MR-BRIDGE-007"].find(".//*[@id='mr-checklist']")
        self.assertEqual(a.signature(normalized_copy(checklist)), a.signature(before))

    def test_13_all_437_math_strings_and_28_canonical_assets(self):
        checks = {n.get("data-check"): a.text(n) for n in self.root.iter() if n.get("data-check")}
        self.assertEqual(len(checks), 437)
        self.assertEqual(checks, self.receipt["expected_math"])
        self.assertEqual(len(self.receipt["assets"]), 28)
        images = list(self.root.iter("img"))
        self.assertEqual(len(images), 28)
        for n in images:
            relative = n.get("src").removeprefix("../")
            pin = self.receipt["assets"][relative]
            raw = a.safe_path(a.BASE, relative).read_bytes()
            self.assertEqual(a.sha(raw), pin["sha256"])
            self.assertEqual(len(raw), pin["bytes"])
            self.assertTrue(n.get("alt"))

    def test_14_default_rebuild_portable_without_archives_or_network(self):
        with tempfile.TemporaryDirectory(prefix="mr-m81373-rebuild-") as temporary:
            base = Path(temporary) / "mr-Deva-IN"
            for relative in self.receipt["inputs"]:
                self.assertFalse(relative.startswith("downloads/"))
                destination = a.safe_path(base, relative)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(a.safe_path(a.BASE, relative), destination)
            self.assertFalse((base.parent / "downloads").exists())
            with mock.patch.object(a.zipfile, "ZipFile", side_effect=AssertionError("archive access forbidden")):
                raw, receipt = a.Assembly(base).build()
            self.assertEqual(raw, self.raw)
            self.assertEqual(receipt, self.receipt_raw)

    def test_15_mutated_ids_order_math_notes_and_ratings_fail_validation(self):
        cases = []
        changed = deepcopy(self.root)
        n = next(n for n in changed.iter() if n.get("id") == "fs-id1167826189010")
        n.set("id", "missing-wrapper"); cases.append(changed)
        changed = deepcopy(self.root)
        n = next(n for n in changed.iter() if n.get("data-check") == "MR-BRIDGE-011::raster-015e")
        n.text = "f(3) = 25"; cases.append(changed)
        changed = deepcopy(self.root)
        n = next(n for n in changed.iter() if n.get("id") == "MR-BRIDGE-007--mr-checklist")
        n.find("tbody/tr/td").text = "✓"; cases.append(changed)
        changed = deepcopy(self.root)
        n = next(n for n in changed.iter() if n.get("id") == "fs-id1167836442406")
        n.text = "नवीन असंबद्ध प्रश्न"; cases.append(changed)
        for changed in cases:
            with self.assertRaises(ValueError):
                self.assembly.validate(changed)

    def test_16_unsafe_paths_and_duplicate_json_fail_closed(self):
        for path in ("../outside", "C:/private", "a\\b", "/tmp/outside"):
            with self.assertRaises(ValueError):
                a.safe_path(a.BASE, path)
        with self.assertRaises(ValueError):
            json.loads('{"a":1,"a":2}', object_pairs_hook=a.object_pairs)
        with self.assertRaises(ValueError):
            a.unique_index(ET.fromstring('<x><p id="same"/><p id="same"/></x>'))

    def test_17_staging_failure_preserves_previous_artifacts(self):
        with tempfile.TemporaryDirectory(prefix="mr-m81373-stage-") as temporary:
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
