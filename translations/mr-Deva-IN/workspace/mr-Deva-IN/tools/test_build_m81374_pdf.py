"""Complete m81374 PDF preservation/layout contract; visual QA is separate.

The suite reads the accepted assembly and renders comparison bytes in memory.
It neither mutates source nor reads HTML/CSS/browser output.
"""
from collections import Counter
from copy import deepcopy
from io import BytesIO
from pathlib import Path
import re
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import build_m81374_pdf as b
from pypdf.generic import ContentStream


BUILDER_SHA = "055805e87ae65d1112336837c32ee233d77bf866671a1edc4a578d7a0110d988"


def actual_text(reader):
    result = []
    for page in reader.pages:
        for operands, operation in ContentStream(page.get_contents(), reader).operations:
            if operation == b"BDC" and len(operands) == 2 and "/ActualText" in operands[1]:
                result.append(str(operands[1]["/ActualText"]))
    return result


def squeeze(value):
    return re.sub(r"\s+", "", value)


class ModulePDFTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read_paths = []
        original_open = Path.open

        def guarded_open(path, *args, **kwargs):
            mode = args[0] if args else kwargs.get("mode", "r")
            if "r" in mode:
                cls.read_paths.append(str(path))
                if path.suffix.lower() in {".html", ".htm", ".css"}:
                    raise AssertionError("forbidden HTML/CSS read")
            return original_open(path, *args, **kwargs)

        if b.sha(Path(b.__file__).read_bytes()) != BUILDER_SHA:
            raise AssertionError("test is not bound to the current PDF builder")
        with patch.object(Path, "open", guarded_open):
            cls.data = b.load_inputs()
            cls.raw, cls.receipt = b.render_pdf(cls.data)
        cls.reader = b.core.PdfReader(BytesIO(cls.raw))
        cls.texts = actual_text(cls.reader)

    def test_00_no_html_css_or_browser_route_was_read(self):
        self.assertFalse(any(Path(path).suffix.lower() in {".html", ".htm", ".css"}
                             for path in self.read_paths))
        self.assertEqual(self.receipt["method"],
                         "Direct accepted assembly XML to ReportLab PDF; no HTML/CSS/browser input")

    def test_01_exact_954_pins_and_complete_source_counts(self):
        receipt = self.receipt
        self.assertEqual(receipt["pinned_inputs_checked"], 954)
        self.assertEqual(len(receipt["input_pins"]), 954)
        self.assertEqual(receipt["pinned_input_bytes"], 13527010)
        self.assertEqual(sum(row["bytes"] for row in receipt["input_pins"].values()), 13527010)
        self.assertEqual(receipt["source_sha256"], b.SOURCE_SHA)
        self.assertEqual(receipt["assembly_receipt_sha256"], b.ASSEMBLY_RECEIPT_SHA)
        self.assertEqual(receipt["assembly_builder_sha256"], b.ASSEMBLY_BUILDER_SHA)
        self.assertEqual(receipt["immutable_pdf_helper_sha256"], b.HELPER_SHA)
        self.assertEqual(receipt["independent_source_oracle_sha256"], b.PRIMARY_SOURCE_TEST_SHA)
        self.assertEqual(tuple(receipt[key] for key in (
            "source_elements_per_locale", "canonical_ids", "source_blocks", "source_exercises",
            "source_supplied_answers", "explicit_source_answer_omissions", "source_mathml",
            "math_checks")), (7223, 1366, 380, 255, 141, 114, 481, 685))

    def test_02_only_authorized_header_changes_and_exact_attachment(self):
        b.validate_render_clone(self.data)
        self.assertEqual(self.reader.attachments[b.UNIT + ".xml"], [self.data["xml"]])
        self.assertEqual(self.reader.pdf_header, "%PDF-1.7")
        self.assertEqual(str(self.reader.trailer["/Root"]["/Lang"]), "mr-Deva-IN")
        self.assertIn(b.PDF_FRAMING, self.texts)
        self.assertNotIn(b.ORIGINAL_FRAMING, self.texts)
        self.assertEqual(self.receipt["header_transformation"]["all_other_XML_content"], "unchanged")
        self.assertEqual(b.sha((b.BASE / "translations/A20-m81374.xml").read_bytes()), b.SOURCE_SHA)

    def test_03_complete_logical_leaves_all_math_and_all_image_descriptions(self):
        available = Counter(self.texts)
        wanted = Counter()
        for node in self.data["root"].iter():
            if node.tag in b.LEAVES and all(child.tag in b.core.INLINE for child in node):
                text = b.core.logical(node).strip()
                if text:
                    wanted[text] += 1
        for text, count in wanted.items():
            self.assertGreaterEqual(available[text], count, text)

        combined = squeeze("\n".join(self.texts))
        checks = [node for node in self.data["root"].iter() if node.get("data-check")]
        self.assertEqual(len(checks), 685)
        for node in checks:
            self.assertIn(squeeze(b.core.logical(node)), combined, node.get("data-check"))
        for node in self.data["root"].iter("img"):
            self.assertIn(squeeze(node.get("alt")), combined)
        mixed = self.data["root"].find(".//div[@id='fs-id1167829704681']")
        self.assertIsNotNone(mixed)
        self.assertIn("ⓐ", self.texts)

    def test_04_all_1371_ids_are_drawn_named_and_printed(self):
        ids = self.data["ids"]
        self.assertEqual(len(ids), 1371)
        self.assertEqual(tuple(ident for ident in ids
                               if ident not in set(self.data["assembly_receipt"]["canonical_id_order"])),
                         b.ASSEMBLY_ONLY_IDS)
        self.assertEqual(set(self.reader.named_destinations), set(ids))
        self.assertEqual(set(self.receipt["anchor_pages_zero_based"]), set(ids))
        for ident in ids:
            self.assertIn(ident, self.texts)
            self.assertTrue(0 <= self.receipt["anchor_pages_zero_based"][ident] < len(self.reader.pages))

    def test_05_all_nine_tables_49_rows_and_blank_ratings(self):
        tables = list(self.data["root"].iter("table"))
        records = self.receipt["tables"]
        self.assertEqual(len(tables), len(records), 9)
        self.assertEqual(tuple(row["rows"] for row in records), b.TABLE_ROWS)
        self.assertEqual(sum(row["rows"] for row in records), 49)
        self.assertEqual(tuple(row["columns"] for row in records), b.TABLE_COLUMNS)
        self.assertEqual(tuple(row["header_rows"] for row in records), b.TABLE_HEADERS)
        for table, record in zip(tables, records):
            expected = [[b.core.logical(cell).strip() for cell in row] for row in table.iter("tr")]
            self.assertEqual(record["cell_logical_text"], expected)
            for row in expected:
                for text in row:
                    if text:
                        self.assertIn(text, self.texts)
        rating = tables[-1]
        self.assertEqual(len(list(rating.iter("td"))), 9)
        self.assertTrue(all(not b.core.logical(cell).strip() for cell in rating.iter("td")))
        self.assertEqual(self.receipt["empty_rating_cells"], 9)
        self.assertNotIn("/AcroForm", self.reader.trailer["/Root"])

    def test_06_all_nested_lists_and_block_list_items_are_preserved(self):
        lists = list(self.data["root"].iter("ul"))
        self.assertEqual(len(lists), 5)
        self.assertEqual(sum(len(node.findall("li")) for node in lists), 16)
        self.assertEqual([len(node.findall("li")) for node in lists], [3, 1, 9, 2, 1])
        for item in self.data["root"].iter("li"):
            if all(child.tag in b.core.INLINE for child in item):
                text = b.core.logical(item).strip()
                if text:
                    self.assertIn(text, self.texts)
        self.assertEqual([child.tag for child in lists[2].findall("li")[0]], ["h3", "ul"])
        self.assertEqual([child.tag for child in lists[4].find("li")][-1], "table")

    def test_07_all_exercise_solution_and_omission_roles(self):
        root = self.data["root"]
        problems = [node for node in root.iter() if node.get("class") == "problem"]
        solutions = [node for node in root.iter() if node.get("class") == "solution"]
        self.assertEqual((len(problems), len(solutions), len(problems) - len(solutions)),
                         (255, 141, 114))
        problem_ids = {node.get("id") for node in problems}
        solution_ids = {node.get("id") for node in solutions}
        paired_problems = set()
        for solution in solutions:
            targets = {link.get("href", "")[1:] for link in solution.iter("a")
                       if link.get("href", "").startswith("#")}
            self.assertEqual(len(targets & problem_ids), 1)
            problem_id = next(iter(targets & problem_ids))
            paired_problems.add(problem_id)
            problem = next(node for node in problems if node.get("id") == problem_id)
            self.assertIn(solution.get("id"), {link.get("href", "")[1:] for link in problem.iter("a")
                                                if link.get("href", "").startswith("#")})
        self.assertEqual(len(paired_problems), 141)
        self.assertEqual(len(problem_ids - paired_problems), 114)

    def test_08_all_149_canonical_image_streams_are_byte_exact(self):
        hashes = []
        for page in self.reader.pages:
            for reference in page.get("/Resources", {}).get("/XObject", {}).values():
                item = reference.get_object()
                if item.get("/Subtype") == "/Image":
                    hashes.append(b.sha(item.get_data()))
        self.assertCountEqual(hashes, [asset["sha256"] for asset in self.data["asset_records"]])
        self.assertEqual(len(hashes), 149)
        self.assertEqual(sum(asset["bytes"] for asset in self.data["asset_records"]), 9908130)
        self.assertTrue(all(not item["inside_table"] for item in self.receipt["image_geometry"]))
        self.assertTrue(all(item["width_points"] <= item["available_width_points"] + .001
                            for item in self.receipt["image_geometry"]))

    def test_09_real_shaping_and_both_pinned_fallback_fonts(self):
        for name in ("MR", "MRBold"):
            font = b.core.pdfmetrics.getFont(name)
            sample = "प्रत्येक मूल्यसंच विश्वास"
            buffer = b.core.hb.Buffer()
            buffer.add_str(sample)
            buffer.guess_segment_properties()
            b.core.hb.shape(font.hbFont(11), buffer)
            glyphs = [item.codepoint for item in buffer.glyph_infos]
            self.assertNotIn(0, glyphs)
            self.assertNotEqual(glyphs, [font.face.charToGlyph[ord(character)] for character in sample])
            self.assertEqual(font.hbFace.index, font.collection_index)
        self.assertEqual(b.markup("f(−3π/2) पुढे"),
                         '<font name="Symbols">f(−3π/2)</font> पुढे')
        self.assertEqual(b.markup("ⓓ–ⓔ पर्याय"),
                         '<font name="Circled">ⓓ–ⓔ</font> पर्याय')
        fallbacks = self.receipt["fallback_glyphs"]
        self.assertEqual({item["character"] for item in fallbacks},
                         b.MATH_SYMBOLS | b.CIRCLED_SYMBOLS)
        self.assertTrue(all(item["glyph_id"] > 0 for item in fallbacks))
        with self.assertRaisesRegex(ValueError, "missing glyphs"):
            b.validate_coverage(chr(0x10FFFF))

    def test_10_four_fonts_embedded_and_no_actions_forms_or_javascript(self):
        details = b.core.inspect_pdf(self.raw, self.data["ids"])
        self.assertEqual(len(details["embedded_fonts"]), 4)
        self.assertTrue(all(font["embedded"] and font["to_unicode"]
                            for font in details["embedded_fonts"].values()))
        self.assertEqual(details["widgets"], 0)
        root = self.reader.trailer["/Root"]
        self.assertNotIn("/OpenAction", root)
        self.assertNotIn("/JavaScript", root.get("/Names", {}))
        self.assertTrue(all(font["embedding_fsType"] in {0, 8} for font in self.receipt["fonts"]))

    def test_11_all_298_safe_links_and_source_policy_counts(self):
        urls, internal = [], 0
        for page in self.reader.pages:
            for reference in page.get("/Annots", []):
                annotation = reference.get_object()
                self.assertEqual(annotation["/Subtype"], "/Link")
                if annotation.get("/A"):
                    urls.append(str(annotation["/A"]["/URI"]))
                elif annotation.get("/Dest"):
                    self.assertEqual(annotation["/Dest"][0].get_object()["/Type"], "/Page")
                    internal += 1
        self.assertCountEqual(urls, self.data["urls"])
        self.assertEqual((internal, len(urls)), (288, 10))
        self.assertEqual(self.receipt["source_link_policy"],
                         {"localized_same_module": 6, "external_outside_module": 8,
                          "optional_external_resource": 1})
        self.assertEqual(self.receipt["rendered_links"], {"internal": 288, "https": 10})

    def test_12_metadata_roles_credits_adaptations_and_limits(self):
        self.assertEqual(len(self.receipt["metadata"]), 4)
        for row in self.receipt["metadata"]:
            self.assertIn(row["term"] + ": " + row["value"], self.texts)
        self.assertEqual(self.receipt["metadata"][3]["value"],
                         "4b2bbf1b-2df7-4b9a-9933-dd70d1fd8ada")
        self.assertEqual(self.receipt["role_census"],
                         {"adaptation": 1, "original": 340,
                          "source-context": 16, "translation": 380})
        self.assertEqual([(row["source_rows"], row["source_entries"])
                          for row in self.receipt["linear_source_table_adaptations"]],
                         [(4, 8), (3, 6)])
        joined = "\n".join(self.texts)
        for value in ("Lynn Marecek", "Andrea Honeycutt Mathis", "OpenStax, Rice University",
                      "CC BY-NC-SA 4.0", "149 मूळ इंग्रजी स्रोत-आकृत्या",
                      "संपूर्ण A20 पुस्तक", "संपूर्ण पाच-पुस्तकांचे काम"):
            self.assertIn(value, joined)

    def test_13_repeated_render_is_byte_reproducible(self):
        raw, receipt = b.render_pdf(self.data)
        self.assertEqual(raw, self.raw)
        self.assertEqual(receipt, self.receipt)

    def test_14_helper_and_all_prior_pdf_artifacts_are_unchanged(self):
        self.assertEqual(b.sha((b.BASE / "tools/build_pdf.py").read_bytes()), b.HELPER_SHA)
        prior = {
            "MR-BRIDGE-006.pdf": "68e5dd2cfde2629dca7b9177cdd5bd9e2a4986ab21ab63480ea00d61a9121729",
            "MR-BRIDGE-007.pdf": "122c4e96ac42d724ec1dd6eecdefbed1fa33416096cd9251354f207296bedf41",
            "MR-BRIDGE-008.pdf": "db6620fa37a3c5748db3612aff34ca6c6901e118ee4f7a2a06e6f782520e3551",
            "A20-m81373.pdf": "e1d9142794ddd56d807f2606855b84baa46b592f05cd8041acbefe99142b6090",
        }
        for filename, digest in prior.items():
            self.assertEqual(b.sha((b.BASE / "output/pdf" / filename).read_bytes()), digest)

    def test_15_mutated_clone_math_rating_and_role_are_rejected(self):
        selectors = (".//span[@data-check]",
                     ".//table[@id='MR-BRIDGE-015--MR-BRIDGE-015-self-rating']/tbody/tr/td",
                     ".//*[@data-kind='translation']")
        for selector in selectors:
            data = dict(self.data, root=deepcopy(self.data["root"]))
            node = data["root"].find(selector)
            self.assertIsNotNone(node)
            if selector.endswith("translation']"):
                node.set("data-kind", "original")
            else:
                node.text = "wrong"
            with self.assertRaisesRegex(ValueError, "beyond the authorized header"):
                b.validate_render_clone(data)

    def test_16_mutated_live_input_pin_is_rejected(self):
        original = Path.read_bytes
        path_to_change = next(path for path in self.receipt["input_pins"]
                              if path.endswith(".xml"))

        def changed(path):
            raw = original(path)
            return raw + b" " if path.resolve() == (b.BASE / path_to_change).resolve() else raw

        with patch.object(Path, "read_bytes", changed):
            with self.assertRaisesRegex(ValueError, "assembly input drift"):
                b.load_inputs()

    def test_17_unsafe_routes_bad_tables_missing_glyphs_and_overflow_rejected(self):
        for href in ("javascript:alert(1)", "file:///C:/secret", "http://example.org"):
            node = ET.Element("p")
            ET.SubElement(node, "a", href=href).text = "bad"
            with self.assertRaisesRegex(ValueError, "unsafe link"):
                b.inline(node)
        with self.assertRaises(ValueError):
            b.assembly.safe_path(b.BASE, "../outside.jpg")
        story = b.ModuleStory(self.data)
        story.styles = b.module_styles()
        with self.assertRaisesRegex(ValueError, "unexpected image route"):
            story.image(ET.fromstring('<img src="../../outside.jpg" alt="bad"/>'))
        with self.assertRaisesRegex(ValueError, "irregular table"):
            story.table(ET.fromstring("<table><tr><td>a</td><td>b</td></tr><tr><td>c</td></tr></table>"))
        paragraph = b.core.ReadingParagraph("x" * 200, b.core.styles()["p"], "x" * 200)
        with self.assertRaisesRegex(ValueError, "overflows"):
            paragraph.wrap(100, 100)

    def test_18_headings_and_standalone_subparts_are_not_page_orphans(self):
        headings = {b.core.logical(node).strip() for node in self.data["root"].iter()
                    if node.tag in {"h1", "h2", "h3", "h4", "h5"}}
        for page in self.reader.pages:
            page_text = []
            for operands, operation in ContentStream(page.get_contents(), self.reader).operations:
                if operation == b"BDC" and len(operands) == 2 and "/ActualText" in operands[1]:
                    page_text.append(str(operands[1]["/ActualText"]).strip())
            self.assertFalse(page_text and page_text[-1] in headings,
                             "heading is last logical content on a page")
            self.assertFalse(page_text and re.fullmatch(r"[ⓐ-ⓗ]", page_text[-1]),
                             "standalone circled subpart is last content on a page")

    def test_19_saved_artifact_and_receipt_are_current_but_not_visual_acceptance(self):
        disk, disk_raw = b.read_json(b.BASE / "qa/A20-m81374-pdf-build-receipt.json")
        pdf = (b.BASE / "output/pdf/A20-m81374.pdf").read_bytes()
        self.assertEqual(pdf, self.raw)
        self.assertEqual(disk, self.receipt)
        self.assertEqual(disk["pdf_sha256"], b.sha(pdf))
        self.assertEqual(disk["builder_sha256"], BUILDER_SHA)
        self.assertEqual(disk["result"], "PASS")
        self.assertIn("visual review separate", disk["status"])
        self.assertIn("Not asserted by builder", disk["visual_review"])
        self.assertIn("universal text extraction", disk["not_claimed"])
        self.assertEqual(b.sha(disk_raw), b.sha((b.BASE / "qa/A20-m81374-pdf-build-receipt.json").read_bytes()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
