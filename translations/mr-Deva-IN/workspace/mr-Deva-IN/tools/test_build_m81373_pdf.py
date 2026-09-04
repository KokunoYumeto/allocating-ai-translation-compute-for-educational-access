"""Full-module PDF preservation/layout-contract tests, not visual acceptance.

Reads the actual released assembly and generates comparison bytes in memory.
No original-unit PDF generation, source mutation, browser or HTML/CSS reads.
"""
from collections import Counter
from copy import deepcopy
from io import BytesIO
from pathlib import Path
import re
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import build_m81373_pdf as b
from pypdf.generic import ContentStream


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
        read = Path.read_bytes
        def guard(path):
            cls.read_paths.append(str(path))
            if path.suffix.lower() in {".html", ".htm", ".css"}:
                raise AssertionError("forbidden HTML/CSS read")
            return read(path)
        with patch.object(Path, "read_bytes", guard):
            cls.data = b.load_inputs()
            cls.raw, cls.receipt = b.render_pdf(cls.data)
        cls.reader = b.core.PdfReader(BytesIO(cls.raw))
        cls.texts = actual_text(cls.reader)

    def test_00_standalone_subpart_labels_are_not_orphaned(self):
        story = b.ModuleStory(self.data)
        story.walk(ET.fromstring("<p>(c)</p>"))
        self.assertTrue(story.story[-1].keepWithNext)
        for page in self.reader.pages:
            texts = []
            for operands, operation in ContentStream(page.get_contents(), self.reader).operations:
                if operation == b"BDC" and len(operands) == 2 and "/ActualText" in operands[1]:
                    texts.append(str(operands[1]["/ActualText"]).strip())
            self.assertFalse(texts and re.fullmatch(r"\([a-z]\)", texts[-1]),
                             "standalone subpart label is last content on page")

    def test_00_symbol_words_use_one_font_and_draw_no_missing_glyph(self):
        for value in ("5′4″", "5′11′′"):
            markup = b.markup(value+" उंची")
            self.assertTrue(markup.startswith('<font name="Symbols">'+value+'</font>'))
            paragraph = b.core.ReadingParagraph(markup, b.core.styles()["p"], value+" उंची")
            self.assertEqual([(f.fontName, f.text) for f in paragraph.frags],
                             [("Symbols", value), ("MR", " उंची")])
            paragraph.wrap(b.core.CONTENT_WIDTH, 700)
            for line in paragraph.blPara.lines:
                for frag in line.words:
                    cmap = b.core.pdfmetrics.getFont(frag.fontName).face.charToGlyph
                    self.assertTrue(all(c.isspace() or cmap.get(ord(c)) for c in frag.text),
                                    "shaped fallback word contains missing glyph")

    def test_01_exact_339_input_pins_and_source_counts(self):
        receipt = self.receipt
        self.assertEqual(receipt["pinned_inputs_checked"], 339)
        self.assertEqual(len(receipt["input_pins"]), 339)
        self.assertEqual(sum(n["bytes"] for n in receipt["input_pins"].values()), 3701872)
        self.assertEqual(receipt["source_sha256"], b.SOURCE_SHA)
        self.assertEqual(tuple(receipt[k] for k in ("canonical_ids", "source_blocks", "source_exercises",
                                                   "source_supplied_answers", "authored_answers_to_source_omissions", "math_checks")),
                         (625, 134, 84, 55, 29, 437))

    def test_02_only_authorized_header_changes_and_original_attachment(self):
        b.validate_render_clone(self.data)
        self.assertEqual(self.reader.attachments[b.UNIT+".xml"], [self.data["xml"]])
        self.assertEqual(self.reader.pdf_header, "%PDF-1.7")
        self.assertEqual(str(self.reader.trailer["/Root"]["/Lang"]), "mr-Deva-IN")
        self.assertIn(b.PDF_FRAMING, self.texts)
        self.assertNotIn(b.ORIGINAL_FRAMING, self.texts)
        self.assertEqual(self.receipt["header_transformation"]["all_other_XML_content"], "unchanged")
        self.assertEqual(b.sha((b.BASE/"translations/A20-m81373.xml").read_bytes()), b.SOURCE_SHA)

    def test_03_all_source_leaves_all_437_math_and_every_image_description(self):
        counts = Counter(self.texts)
        wanted = Counter()
        for node in self.data["root"].iter():
            if node.tag in b.core.LEAVES and all(c.tag in b.core.INLINE for c in node):
                wanted[b.core.logical(node).strip()] += 1
            elif node.tag == "li" and node.find("ul") is not None:
                lead = deepcopy(node)
                for child in list(lead):
                    if child.tag not in b.core.INLINE:
                        lead.remove(child)
                wanted[b.core.logical(lead).strip()] += 1
        for text, count in wanted.items():
            self.assertGreaterEqual(counts[text], count, text)
        combined = squeeze("\n".join(self.texts))
        checks = [n for n in self.data["root"].iter() if n.get("data-check")]
        self.assertEqual(len(checks), 437)
        for node in checks:
            self.assertIn(squeeze(b.core.logical(node)), combined, node.get("data-check"))
        for node in self.data["root"].iter("img"):
            self.assertIn(squeeze(node.get("alt")), combined)

    def test_04_all_664_ids_drawn_named_and_printed(self):
        self.assertEqual(len(self.data["ids"]), 664)
        self.assertEqual(set(self.reader.named_destinations), set(self.data["ids"]))
        self.assertEqual(set(self.receipt["anchor_pages_zero_based"]), set(self.data["ids"]))
        for ident in self.data["ids"]:
            self.assertIn(ident, self.texts)
            self.assertTrue(0 <= self.receipt["anchor_pages_zero_based"][ident] < len(self.reader.pages))

    def test_05_all_11_tables_54_rows_and_nested_cells_preserved(self):
        tables = list(self.data["root"].iter("table"))
        records = self.receipt["tables"]
        self.assertEqual(len(tables), 11)
        self.assertEqual(tuple(r["rows"] for r in records), b.TABLE_ROWS)
        self.assertEqual(sum(r["rows"] for r in records), 54)
        self.assertEqual([r["columns"] for r in records], [2]*10+[4])
        self.assertEqual([r["header_rows"] for r in records], [0, 0]+[1]*9)
        self.assertEqual(Counter(c.tag for table in tables for cell in table.iter("td") for c in cell),
                         Counter(figure=6, span=37, div=1, p=3))
        for table, record in zip(tables, records):
            self.assertEqual(record["cell_logical_text"], [[b.core.logical(c).strip() for c in row] for row in table.iter("tr")])
            for row in table.iter("tr"):
                for cell in row:
                    if all(c.tag in b.core.INLINE for c in cell):
                        self.assertIn(b.core.logical(cell).strip(), self.texts)
        self.assertEqual(sum(r["inside_table"] for r in self.receipt["image_geometry"]), 6)
        for image in self.receipt["image_geometry"]:
            self.assertLessEqual(image["width_points"], image["available_width_points"]+.001)

    def test_06_all_metadata_pairs_credits_and_blank_ratings(self):
        self.assertEqual(len(self.receipt["metadata"]), 4)
        for record in self.receipt["metadata"]:
            self.assertIn(record["term"]+": "+record["value"], self.texts)
        self.assertEqual(self.receipt["metadata"][3]["value"], "59fe6dc4-6e09-4a88-aa1c-b5f72bd79a20")
        joined = "\n".join(self.texts)
        for value in ("Lynn Marecek", "Andrea Honeycutt Mathis", "MaryAnne Anthony-Smith", "CC BY-NC-SA 4.0"):
            self.assertIn(value, joined)
        self.assertEqual(self.texts.count("□"), 9)
        self.assertEqual(self.receipt["empty_rating_cells"], 9)
        self.assertNotIn("/AcroForm", self.reader.trailer["/Root"])

    def test_07_all_28_canonical_image_streams_byte_exact(self):
        hashes = []
        for page in self.reader.pages:
            for reference in page.get("/Resources", {}).get("/XObject", {}).values():
                item = reference.get_object()
                if item.get("/Subtype") == "/Image":
                    hashes.append(b.sha(item.get_data()))
        self.assertCountEqual(hashes, [a["sha256"] for a in self.data["asset_records"]])
        self.assertEqual(len(hashes), 28)
        self.assertEqual(sum(a["bytes"] for a in self.data["asset_records"]), 1551848)

    def test_08_real_shaping_and_all_six_verified_fallback_symbols(self):
        for name in ("MR", "MRBold"):
            font = b.core.pdfmetrics.getFont(name)
            sample = "प्रत्येक मूल्यसंच विश्वास"
            buf = b.core.hb.Buffer()
            buf.add_str(sample)
            buf.guess_segment_properties()
            b.core.hb.shape(font.hbFont(11), buf)
            glyphs = [i.codepoint for i in buf.glyph_infos]
            self.assertNotIn(0, glyphs)
            self.assertNotEqual(glyphs, [font.face.charToGlyph[ord(c)] for c in sample])
            self.assertEqual(font.hbFace.index, font.collection_index)
        self.assertEqual({v["character"] for v in self.receipt["fallback_glyphs"]}, set("′″⇒≠≤□"))
        self.assertTrue(all(v["glyph_id"] > 0 for v in self.receipt["fallback_glyphs"]))
        b.validate_coverage("".join(self.data["root"].itertext())+"".join(n.get("alt", "") for n in self.data["root"].iter()))
        with self.assertRaisesRegex(ValueError, "missing glyphs"):
            b.validate_coverage(chr(0x10FFFF))

    def test_09_fonts_embedded_and_no_actions_forms_or_javascript(self):
        details = b.core.inspect_pdf(self.raw, self.data["ids"])
        self.assertEqual(len(details["embedded_fonts"]), 3)
        self.assertTrue(all(f["embedded"] and f["to_unicode"] for f in details["embedded_fonts"].values()))
        self.assertEqual(details["widgets"], 0)
        root = self.reader.trailer["/Root"]
        self.assertNotIn("/OpenAction", root)
        self.assertNotIn("/JavaScript", root.get("/Names", {}))
        for font in self.receipt["fonts"]:
            self.assertEqual(font["embedding_fsType"], 8)

    def test_10_https_and_internal_links_match_source(self):
        urls, internal = set(), 0
        for page in self.reader.pages:
            for reference in page.get("/Annots", []):
                annotation = reference.get_object()
                self.assertEqual(annotation["/Subtype"], "/Link")
                if annotation.get("/A"):
                    urls.add(str(annotation["/A"]["/URI"]))
                elif annotation.get("/Dest"):
                    self.assertEqual(annotation["/Dest"][0].get_object()["/Type"], "/Page")
                    internal += 1
        self.assertEqual(urls, set(self.data["urls"]))
        self.assertGreaterEqual(internal, len(self.data["local_links"]))
        self.assertEqual(len(self.data["urls"])+len(self.data["local_links"]), 180)

    def test_11_repeated_render_is_byte_reproducible(self):
        raw, receipt = b.render_pdf(self.data)
        self.assertEqual(raw, self.raw)
        self.assertEqual(receipt, self.receipt)

    def test_12_helper_and_prior_PDFs_are_unchanged(self):
        self.assertEqual(b.sha((b.BASE/"tools/build_pdf.py").read_bytes()), b.HELPER_SHA)
        prior = {
            "006": "68e5dd2cfde2629dca7b9177cdd5bd9e2a4986ab21ab63480ea00d61a9121729",
            "007": "122c4e96ac42d724ec1dd6eecdefbed1fa33416096cd9251354f207296bedf41",
            "008": "db6620fa37a3c5748db3612aff34ca6c6901e118ee4f7a2a06e6f782520e3551",
        }
        for unit, digest in prior.items():
            self.assertEqual(b.sha((b.BASE/f"output/pdf/MR-BRIDGE-{unit}.pdf").read_bytes()), digest)
        self.assertFalse(any(Path(p).suffix.lower() in {".html", ".htm", ".css"} for p in self.read_paths))

    def test_13_mutated_clone_math_and_ratings_are_rejected(self):
        for selector in (".//span[@data-check]", ".//table[@id='MR-BRIDGE-007--mr-checklist']/tbody/tr/td"):
            data = dict(self.data, root=deepcopy(self.data["root"]))
            node = data["root"].find(selector)
            self.assertIsNotNone(node)
            node.text = "wrong"
            with self.assertRaisesRegex(ValueError, "beyond the authorized header"):
                b.validate_render_clone(data)

    def test_14_mutated_input_pin_is_rejected(self):
        original = Path.read_bytes
        path_to_change = next(p for p in self.receipt["input_pins"] if p.endswith(".xml"))
        def changed(path):
            raw = original(path)
            return raw+b" " if path.resolve() == (b.BASE/path_to_change).resolve() else raw
        with patch.object(Path, "read_bytes", changed):
            with self.assertRaisesRegex(ValueError, "assembly input drift"):
                b.load_inputs()

    def test_15_unsafe_routes_unsupported_cells_and_overflow_rejected(self):
        for href in ("javascript:alert(1)", "file:///C:/secret", "http://example.org"):
            node = ET.Element("p")
            ET.SubElement(node, "a", href=href).text = "bad"
            with self.assertRaisesRegex(ValueError, "unsafe link"):
                b.inline(node)
        with self.assertRaises(ValueError):
            b.assembly.safe_path(b.BASE, "../outside.jpg")
        paragraph = b.core.ReadingParagraph("x"*200, b.core.styles()["p"], "x"*200)
        with self.assertRaisesRegex(ValueError, "overflows"):
            paragraph.wrap(100, 100)
        story = b.ModuleStory(self.data)
        with self.assertRaisesRegex(ValueError, "unsupported table cell block"):
            story.cell(ET.fromstring("<td><script>bad</script></td>"), 100)

    def test_16_final_artifact_receipt_current_and_not_visual_acceptance(self):
        disk, disk_raw = b.read_json(b.BASE/"qa/A20-m81373-pdf-build-receipt.json")
        pdf = (b.BASE/"output/pdf/A20-m81373.pdf").read_bytes()
        self.assertEqual(pdf, self.raw)
        self.assertEqual(disk, self.receipt)
        self.assertEqual(disk["pdf_sha256"], b.sha(pdf))
        self.assertEqual(disk["builder_sha256"], b.sha(Path(b.__file__).read_bytes()))
        self.assertEqual(disk["result"], "PASS")
        self.assertIn("visual review separate", disk["status"])
        self.assertIn("Not asserted by builder", disk["visual_review"])
        self.assertIn("universal text extraction", disk["not_claimed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
