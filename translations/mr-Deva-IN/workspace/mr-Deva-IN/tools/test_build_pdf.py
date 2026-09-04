"""Focused direct-XML PDF tests. No browser, HTML, or rendered-page assertions.

Run: bundled-python -B mr-Deva-IN/tools/test_build_pdf.py
Visual review is deliberately a separate human/model page-inspection record.
"""
from collections import Counter
from copy import deepcopy
from io import BytesIO
from pathlib import Path
import re
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import build_pdf as b
from pypdf.generic import ContentStream


def actual_text(reader):
    texts = []
    for page in reader.pages:
        for operands, operator in ContentStream(page.get_contents(), reader).operations:
            if operator == b"BDC" and len(operands) == 2 and "/ActualText" in operands[1]:
                texts.append(str(operands[1]["/ActualText"]))
    return texts


class PDFTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = {u: b.load_inputs(u) for u in sorted(b.SUPPORTED)}
        cls.generated = {u: b.render_pdf(d) for u, d in cls.data.items()}

    def test_shaping_is_real_and_collection_index_correct(self):
        b.register_fonts()
        sample = "प्रत्येक मूल्यसंच विश्वास"
        for name in ("MR", "MRBold"):
            font = b.pdfmetrics.getFont(name)
            buf = b.hb.Buffer()
            buf.add_str(sample)
            buf.guess_segment_properties()
            b.hb.shape(font.hbFont(11), buf)
            glyphs = [i.codepoint for i in buf.glyph_infos]
            self.assertTrue(font.shapable)
            self.assertNotIn(0, glyphs)
            self.assertNotEqual(glyphs, [font.face.charToGlyph[ord(c)] for c in sample])
            self.assertEqual(font.hbFace.index, font.collection_index)

    def test_no_missing_glyphs_and_negative_coverage(self):
        for data in self.data.values():
            b.validate_coverage("".join(data["root"].itertext()) +
                                "".join(n.get("alt", "") for n in data["root"].iter()))
        with self.assertRaisesRegex(ValueError, "missing glyphs"):
            b.validate_coverage(chr(0x10FFFF))

    def test_actual_text_contains_every_source_leaf_and_math(self):
        for unit, data in self.data.items():
            reader = b.PdfReader(BytesIO(self.generated[unit][0]))
            texts = actual_text(reader)
            counts = Counter(texts)
            wanted = Counter(b.logical(n).strip() for n in data["root"].iter() if n.tag in b.LEAVES)
            for text, count in wanted.items():
                self.assertGreaterEqual(counts[text], count, (unit, text))
            joined = "\n".join(texts)
            for n in data["root"].iter():
                if n.get("data-check"):
                    self.assertIn(b.logical(n).strip(), joined, (unit, n.get("data-check")))
                if n.tag == "img":
                    self.assertIn(n.get("alt"), joined)

    def test_all_ids_preserved_as_destinations_and_visible_index(self):
        for unit, data in self.data.items():
            reader = b.PdfReader(BytesIO(self.generated[unit][0]))
            self.assertEqual(set(reader.named_destinations), set(data["ids"]))
            texts = actual_text(reader)
            for anchor in data["ids"]:
                self.assertIn(anchor, texts)
            self.assertEqual(len(data["ids"]), {"MR-BRIDGE-006": 138, "MR-BRIDGE-007": 33,
                                               "MR-BRIDGE-008": 107}[unit])

    def test_xml_attachment_is_byte_exact(self):
        for unit, data in self.data.items():
            reader = b.PdfReader(BytesIO(self.generated[unit][0]))
            self.assertEqual(reader.pdf_header, "%PDF-1.7")
            self.assertEqual(reader.attachments[unit + ".xml"], [data["xml"]])

    def test_fonts_embedded_and_no_form_or_script_actions(self):
        for unit, (raw, receipt) in self.generated.items():
            result = b.inspect_pdf(raw, self.data[unit]["ids"])
            self.assertEqual(result["widgets"], 0)
            self.assertTrue(all(f["embedded"] and f["to_unicode"] for f in result["embedded_fonts"].values()))
            root = b.PdfReader(BytesIO(raw)).trailer["/Root"]
            self.assertNotIn("/OpenAction", root)
            self.assertNotIn("/JavaScript", root.get("/Names", {}))
            self.assertEqual(receipt["result"], "PASS")

    def test_https_and_local_links_remain_exact(self):
        for unit, data in self.data.items():
            reader = b.PdfReader(BytesIO(self.generated[unit][0]))
            expected = {a.get("href") for a in data["root"].iter("a") if not a.get("href").startswith("#")}
            actual, local = set(), 0
            for page in reader.pages:
                for ref in page.get("/Annots", []):
                    a = ref.get_object()
                    if a.get("/A"):
                        actual.add(str(a["/A"]["/URI"]))
                    elif a.get("/Dest"):
                        self.assertTrue(a["/Dest"][0].get_object().get("/Type") == "/Page")
                        local += 1
            self.assertEqual(actual, expected)
            self.assertGreaterEqual(local, len(data["local_links"]))

    def test_canonical_jpegs_are_byte_exact(self):
        for unit, data in self.data.items():
            reader = b.PdfReader(BytesIO(self.generated[unit][0]))
            hashes = []
            for page in reader.pages:
                for ref in page.get("/Resources", {}).get("/XObject", {}).values():
                    obj = ref.get_object()
                    if obj.get("/Subtype") == "/Image":
                        hashes.append(b.pins.sha(obj.get_data()))
            self.assertCountEqual(hashes, [a["sha256"] for a in data["asset_records"]])

    def test_nine_ratings_empty_and_source_answers_not_filled(self):
        data = self.data["MR-BRIDGE-007"]
        self.assertEqual([b.logical(c).strip() for c in data["root"].iter("td")], ["□"] * 9)
        reader = b.PdfReader(BytesIO(self.generated["MR-BRIDGE-007"][0]))
        self.assertEqual(actual_text(reader).count("□"), 9)
        self.assertEqual(self.generated["MR-BRIDGE-007"][1]["empty_rating_cells"], 9)

    def test_source_classifications_and_final_006_chain_breaks(self):
        for unit, count in [("MR-BRIDGE-006", 31), ("MR-BRIDGE-007", 9), ("MR-BRIDGE-008", 21)]:
            self.assertEqual(self.generated[unit][1]["source_blocks"], count)
        root = self.data["MR-BRIDGE-006"]["root"]
        breaks = [b.logical(n) for n in root.iter() if n.get("data-check") and n.find("br") is not None]
        self.assertEqual(len(breaks), 2)
        self.assertTrue(any("\n=3250+1500=4750" in t for t in breaks))
        self.assertTrue(any("\n=7250+2500=9750" in t for t in breaks))

    def test_render_is_byte_reproducible_same_environment(self):
        for unit, data in self.data.items():
            raw, _ = b.render_pdf(data)
            self.assertEqual(raw, self.generated[unit][0])

    def test_rejects_unowned_units(self):
        for unit in ("MR-BRIDGE-010", "../MR-BRIDGE-007"):
            with self.assertRaises(ValueError):
                b.load_inputs(unit)

    def test_rejects_changed_math_configuration(self):
        original = b.pins.read_json
        def changed(path):
            value, raw = original(path)
            if path.parent.name == "units":
                value = deepcopy(value)
                key = next(iter(value["expected_math"]))
                value["expected_math"][key] += "wrong"
            return value, raw
        with patch.object(b.pins, "read_json", changed):
            with self.assertRaisesRegex(ValueError, "mathematical chain drift"):
                b.load_inputs("MR-BRIDGE-007")

    def test_rejects_changed_witness_hash(self):
        original = b.pins.read_json
        def changed(path):
            value, raw = original(path)
            if path.parent.name == "provenance":
                value = deepcopy(value)
                value["witnesses"][0]["sha256"] = "0" * 64
            return value, raw
        with patch.object(b.pins, "read_json", changed):
            with self.assertRaisesRegex(ValueError, "witness drift"):
                b.load_inputs("MR-BRIDGE-007")

    def test_rejects_unsafe_links_and_asset_paths(self):
        for href in ("javascript:alert(1)", "file:///C:/secret", "http://example.org"):
            root = ET.fromstring('<article><a href="' + href + '">bad</a></article>')
            with self.assertRaises(ValueError):
                b.pins.validate_markup(root, {})
        with self.assertRaises(ValueError):
            b.pins.inside(b.BASE, "../outside.jpg")

    def test_rejects_overflow_instead_of_clipping(self):
        p = b.ReadingParagraph("x" * 200, b.styles()["p"], "x" * 200)
        with self.assertRaisesRegex(ValueError, "overflows"):
            p.wrap(100, 100)


if __name__ == "__main__":
    unittest.main(verbosity=2)
