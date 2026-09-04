"""Small offline fixtures: no corpus downloads or full-language temporary copy."""
import base64
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


TOOLS = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("unit_builder", TOOLS / "build_unit.py")
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)
UNIT = "MR-BRIDGE-002"
XML = '''<article lang="mr-Deva-IN" id="MR-BRIDGE-002">
<h1>फलन</h1><nav><a href="#P1">सराव</a></nav>
<section id="fs-source" data-source="A20:m123#fs-source">
<p>फलन: <span data-check="value">f(2) = 3</span></p></section>
<ol><li id="P1">f(2)? <a href="#S-P1">उत्तर</a></li></ol>
<p id="S-P1"><a href="#P1">प्रश्न</a> f(2) = 3.</p>
<p><a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">परवाना</a></p>
</article>'''
# Signature fixtures test pinning/embedding, not complete codec validity.
JPEG = b"\xff\xd8\xff\xe0tiny-jpeg-fixture\xff\xd9"
PNG = b"\x89PNG\r\n\x1a\ntiny-png-fixture"


class ImagesInOutput(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.images.append(dict(attrs))


class BuildUnitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mr-unit-small-test-")
        self.base = Path(self.temp.name)
        for directory in ("translations", "units", "provenance", "tools"):
            (self.base / directory).mkdir()
        self.source = self.base / "translations" / (UNIT + ".xml")
        self.config_path = self.base / "units" / (UNIT + ".json")
        self.lock_path = self.base / "provenance" / (UNIT + ".lock.json")
        self.source.write_text(XML, encoding="utf-8")
        (self.base / "tools/reader.css").write_bytes((TOOLS / "reader.css").read_bytes())
        (self.base / "provenance/witness.txt").write_bytes(b"pinned source\n")
        self.config = {"title": "फलन", "source_count": 1, "translated_worked_examples": 1,
                       "translated_definitions": 0, "original_practice_items": 1,
                       "question_ids": ["P1"], "expected_math": {"value": "f(2) = 3"},
                       "required_terms": ["फलन"]}
        self.lock = {"source_selections": [{"locator": "A20:m123#fs-source", "target_id": "fs-source"}],
                     "witnesses": [{"path": "provenance/witness.txt",
                                    "sha256": hashlib.sha256(b"pinned source\n").hexdigest()}]}
        self.save_config()
        self.save_lock()

    def tearDown(self):
        self.temp.cleanup()

    def save_config(self):
        self.config_path.write_text(json.dumps(self.config, ensure_ascii=False), encoding="utf-8")

    def save_lock(self):
        self.lock_path.write_text(json.dumps(self.lock), encoding="utf-8")

    def mutate(self, before, after):
        text = self.source.read_text(encoding="utf-8")
        self.assertIn(before, text)
        self.source.write_text(text.replace(before, after, 1), encoding="utf-8")

    def run_build(self):
        return builder.build(UNIT, base=self.base)

    def fails(self, message):
        with self.assertRaisesRegex(ValueError, message):
            self.run_build()
        self.assertFalse((self.base / "output").exists())

    def add_asset(self, name="diagram.jpg", raw=JPEG, mime="image/jpeg", pin=True, use=True):
        relative = f"assets/{UNIT}/{name}"
        path = self.base / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        record = {"path": relative, "sha256": hashlib.sha256(raw).hexdigest(), "mime": mime}
        self.config.setdefault("assets", {})[name] = record
        if pin:
            self.lock["witnesses"].append({"path": relative, "sha256": record["sha256"]})
        self.save_config()
        self.save_lock()
        if use:
            self.mutate("</article>", f'<figure id="figure-{len(self.config["assets"])}">'
                        f'<img src="asset:{name}" alt="मूळ आकृती"/></figure></article>')
        return record

    def test_deterministic_offline_build_and_counts(self):
        receipt = self.run_build()
        output = self.base / "output" / (UNIT + ".html")
        receipt_path = self.base / "qa" / (UNIT + "-build-receipt.json")
        first = (output.read_bytes(), receipt_path.read_bytes())
        self.assertEqual(receipt, self.run_build())
        self.assertEqual(first, (output.read_bytes(), receipt_path.read_bytes()))
        self.assertEqual(receipt["html_sha256"], hashlib.sha256(first[0]).hexdigest())
        self.assertEqual(receipt["html_bytes"], len(first[0]))
        self.assertEqual(receipt["source_labels_checked"], 1)
        self.assertEqual(receipt["question_answer_pairs"], 1)
        self.assertEqual(receipt["local_links_checked"], 3)
        self.assertEqual(receipt["optional_external_citation_links"], 1)
        self.assertIn(b"Source: A20:m123#fs-source", first[0])
        self.assertIn(b"default-src 'none'", first[0])
        self.assertNotIn(b"<script", first[0])
        self.assertFalse((self.base / "downloads").exists())
        self.assertEqual(self.source.read_text(encoding="utf-8"), XML)

    def test_wrong_locale(self):
        self.mutate('lang="mr-Deva-IN"', 'lang="hi-Deva-IN"')
        self.fails("wrong locale")

    def test_wrong_unit(self):
        self.mutate('id="MR-BRIDGE-002"', 'id="MR-BRIDGE-003"')
        self.fails("wrong article/unit ID")

    def test_wrong_math(self):
        self.mutate('data-check="value">f(2) = 3', 'data-check="value">f(2) = 4')
        self.fails("mathematical chain")

    def test_broken_local_link(self):
        self.mutate('href="#S-P1"', 'href="#missing"')
        self.fails("broken answer/navigation")

    def test_existing_targets_without_reverse_link(self):
        self.mutate('href="#P1">प्रश्न', 'href="#fs-source">प्रश्न')
        self.fails("bidirectional")

    def test_empty_anchor_is_not_navigation(self):
        self.mutate('href="#P1">प्रश्न', 'href="#P1">')
        self.fails("bidirectional")

    def test_extra_solution(self):
        self.mutate('</article>', '<p id="S-P2">unlisted</p></article>')
        self.fails("unexpected question/solution")

    def test_unlisted_question(self):
        self.mutate('</article>', '<p id="P2">unlisted</p></article>')
        self.fails("unlisted original question")

    def test_source_locator_drift(self):
        self.mutate('data-source="A20:m123#fs-source"', 'data-source="A20:m999#fs-source"')
        self.fails("source selection drift")

    def test_source_order_drift(self):
        self.lock["source_selections"].append({"locator": "A20:m123#fs-second", "target_id": "fs-second"})
        self.save_lock()
        self.config["source_count"] = 2
        self.save_config()
        self.mutate('<section id="fs-source"',
                    '<div id="fs-second" data-source="A20:m123#fs-second">second</div><section id="fs-source"')
        self.fails("source selection drift")

    def test_source_id_elsewhere_does_not_pass(self):
        self.mutate('id="fs-source" data-source', 'id="incorrect" data-source')
        self.mutate('</article>', '<p id="fs-source">misplaced</p></article>')
        self.fails("source ID not preserved on source block")

    def test_witness_drift(self):
        (self.base / "provenance/witness.txt").write_bytes(b"changed")
        self.fails("witness drift")

    def test_missing_witness(self):
        self.lock["witnesses"][0]["path"] = "provenance/missing.txt"
        self.save_lock()
        with self.assertRaises(FileNotFoundError):
            self.run_build()

    def test_missing_config(self):
        with self.assertRaises(FileNotFoundError):
            builder.build("MR-BRIDGE-003", base=self.base)

    def test_duplicate_data_check_even_with_equal_text(self):
        self.mutate('</article>', '<p data-check="value">f(2) = 3</p></article>')
        self.fails("duplicate data-check")

    def test_duplicate_json_math_key(self):
        text = self.config_path.read_text(encoding="utf-8")
        self.config_path.write_text(text.replace('"value": "f(2) = 3"',
                                                '"value": "f(2) = 0", "value": "f(2) = 3"'),
                                    encoding="utf-8")
        self.fails("duplicate JSON key")

    def test_duplicate_ids(self):
        self.mutate('</article>', '<p id="P1">duplicate</p></article>')
        self.fails("duplicate XML/HTML IDs")

    def test_non_nfc_rejected(self):
        self.mutate('<h1>फलन</h1>', '<h1>फलन e\u0301</h1>')
        self.fails("non-NFC")

    def test_replacement_character_rejected(self):
        self.mutate('<h1>फलन</h1>', '<h1>फलन \ufffd</h1>')
        self.fails("replacement character")

    def test_missing_term(self):
        self.config["required_terms"] = ["उकल"]
        self.save_config()
        self.fails("required term missing")

    def test_count_drift(self):
        self.config["source_count"] = 2
        self.save_config()
        self.fails("source count drift")

    def test_question_count_drift(self):
        self.config["original_practice_items"] = 2
        self.save_config()
        self.fails("question count drift")

    def test_optional_source_classifications_remain_separate(self):
        self.config["translated_worked_examples"] = 0
        for key in ("translated_practice_items", "translated_resource_notes"):
            with self.subTest(key=key):
                self.config[key] = 1
                self.save_config()
                receipt = self.run_build()
                self.assertEqual(receipt[key], 1)
                self.assertEqual(receipt["translated_worked_examples"], 0)
                self.assertEqual(receipt["unclassified_source_blocks"], 0)
                self.config[key] = 0

    def test_source_classifications_cannot_exceed_source_count(self):
        self.config["translated_practice_items"] = 1
        self.save_config()
        self.fails("source classification counts exceed")

    def test_path_traversal(self):
        for unit in ("../MR-BRIDGE-002", "MR-BRIDGE-002/", "MR-BRIDGE-002.xml", "C:/MR-BRIDGE-002"):
            with self.subTest(unit=unit), self.assertRaisesRegex(ValueError, "invalid unit name"):
                builder.build(unit, base=self.base)
        for path in ("../witness.txt", "/witness.txt", "C:/witness.txt", "provenance/../witness.txt",
                     "provenance\\witness.txt"):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "unsafe relative path"):
                builder.inside(self.base, path)

    def test_script_and_network_dependencies(self):
        for markup in ('<script>alert(1)</script>', '<img src="https://example.com/a.png"/>',
                       '<p onclick="alert(1)">x</p>', '<p style="background:url(https://example.com)">x</p>'):
            with self.subTest(markup=markup):
                self.source.write_text(XML.replace('</article>', markup + '</article>'), encoding="utf-8")
                self.fails("unsupported or executable")

    def test_stylesheet_dependency(self):
        (self.base / "tools/reader.css").write_text('@import "https://example.com/a.css";', encoding="utf-8")
        self.fails("stylesheet dependency")

    def test_javascript_anchor(self):
        self.mutate('href="#S-P1"', 'href="javascript:alert(1)"')
        self.fails("only same-document")

    def test_title_is_escaped(self):
        self.config["title"] = "फलन <script>"
        self.save_config()
        self.run_build()
        output = (self.base / "output" / (UNIT + ".html")).read_text(encoding="utf-8")
        self.assertIn("&lt;script&gt;", output)
        self.assertNotIn("<script>", output)

    def test_staging_failure_preserves_both_previous_artifacts(self):
        self.run_build()
        paths = [self.base / "output" / (UNIT + ".html"),
                 self.base / "qa" / (UNIT + "-build-receipt.json")]
        before = [path.read_bytes() for path in paths]
        real_named = tempfile.NamedTemporaryFile
        count = 0

        def fail_second(**kwargs):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError("synthetic disk full")
            return real_named(**kwargs)

        with patch.object(builder.tempfile, "NamedTemporaryFile", side_effect=fail_second):
            with self.assertRaisesRegex(OSError, "synthetic disk full"):
                self.run_build()
        self.assertEqual(before, [path.read_bytes() for path in paths])
        self.assertEqual([], list(self.base.rglob("*.tmp")))

    def test_offline_pinned_jpeg_and_png_embedding(self):
        (self.base / "tools/unit-reader.css").write_bytes((TOOLS / "unit-reader.css").read_bytes())
        self.add_asset()
        self.add_asset("diagram.png", PNG, "image/png")
        original = self.source.read_bytes()
        receipt = self.run_build()
        output = self.base / "output" / (UNIT + ".html")
        first = output.read_bytes()
        self.assertEqual(receipt, self.run_build())
        self.assertEqual(first, output.read_bytes())
        parsed = ImagesInOutput()
        parsed.feed(first.decode("utf-8"))
        self.assertEqual(len(parsed.images), 2)
        for image, mime, raw in zip(parsed.images, ("image/jpeg", "image/png"), (JPEG, PNG)):
            prefix, encoded = image["src"].split(",", 1)
            self.assertEqual(prefix, "data:" + mime + ";base64")
            self.assertEqual(base64.b64decode(encoded, validate=True), raw)
            self.assertEqual(image["alt"], "मूळ आकृती")
        self.assertIn(b"img-src data:;", first)
        self.assertIn(b"max-width:100%; height:auto", first)
        self.assertNotIn(b"asset:", first)
        self.assertEqual(receipt["embedded_image_count"], 2)
        self.assertEqual(receipt["distinct_embedded_assets"], 2)
        self.assertEqual(receipt["embedded_image_raw_bytes"], len(JPEG) + len(PNG))
        self.assertEqual(receipt["distinct_asset_bytes"], len(JPEG) + len(PNG))
        for record, raw in zip(receipt["embedded_assets"], (JPEG, PNG)):
            self.assertEqual(record["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(record["bytes"], len(raw))
            self.assertEqual(record["uses"], 1)
        self.assertEqual(self.source.read_bytes(), original)

    def test_no_assets_no_image_policy_or_generated_css(self):
        receipt = self.run_build()
        output = (self.base / "output" / (UNIT + ".html")).read_bytes()
        self.assertNotIn(b"img-src", output)
        self.assertNotIn(builder.IMAGE_STYLE, output)
        self.assertEqual(receipt["embedded_image_count"], 0)
        self.assertEqual(receipt["embedded_assets"], [])

    def test_repeated_image_use_is_counted_without_duplicate_records(self):
        self.add_asset()
        self.mutate("</article>", '<figure id="second-figure"><img src="asset:diagram.jpg" '
                    'alt="पुन्हा दाखवलेली आकृती"/></figure></article>')
        receipt = self.run_build()
        self.assertEqual(receipt["embedded_image_count"], 2)
        self.assertEqual(receipt["distinct_embedded_assets"], 1)
        self.assertEqual(receipt["embedded_image_raw_bytes"], 2 * len(JPEG))
        self.assertEqual(receipt["distinct_asset_bytes"], len(JPEG))
        self.assertEqual(receipt["embedded_assets"][0]["uses"], 2)

    def test_unconfigured_image_asset(self):
        self.mutate("</article>", '<figure id="unconfigured"><img src="asset:missing.png" '
                    'alt="आकृती"/></figure></article>')
        self.fails("image asset is not configured")

    def test_missing_asset_file(self):
        asset = self.add_asset()
        asset["path"] = f"assets/{UNIT}/missing.jpg"
        self.lock["witnesses"][-1]["path"] = asset["path"]
        self.save_config()
        self.save_lock()
        with self.assertRaises(FileNotFoundError):
            self.run_build()
        self.assertFalse((self.base / "output").exists())

    def test_unhashed_asset(self):
        asset = self.add_asset()
        del asset["sha256"]
        self.save_config()
        self.fails("invalid asset SHA-256")

    def test_unpinned_asset(self):
        self.add_asset(pin=False)
        self.fails("asset is not pinned in provenance")

    def test_asset_pin_must_match_config_hash(self):
        asset = self.add_asset()
        asset["sha256"] = "0" * 64
        self.save_config()
        self.fails("asset is not pinned in provenance")

    def test_asset_bytes_cannot_drift(self):
        asset = self.add_asset()
        (self.base / asset["path"]).write_bytes(JPEG + b"changed")
        self.fails("witness drift")

    def test_asset_path_traversal(self):
        asset = self.add_asset()
        asset["path"] = "../outside.jpg"
        self.save_config()
        self.fails("unsafe relative path")

    def test_asset_id_traversal(self):
        asset = self.add_asset()
        self.config["assets"] = {"../diagram.jpg": asset}
        self.save_config()
        self.fails("invalid asset ID")

    def test_asset_mime_must_be_supported(self):
        asset = self.add_asset()
        asset["mime"] = "image/svg+xml"
        self.save_config()
        self.fails("unsupported asset MIME")

    def test_asset_mime_must_match_extension(self):
        asset = self.add_asset()
        asset["mime"] = "image/png"
        self.save_config()
        self.fails("asset ID/MIME mismatch")

    def test_asset_magic_must_match_declared_mime(self):
        self.add_asset("diagram.png", JPEG, "image/png")
        self.fails("asset MIME/magic mismatch")

    def test_svg_bytes_cannot_masquerade_as_jpeg(self):
        self.add_asset(raw=b'<svg xmlns="http://www.w3.org/2000/svg"><script/></svg>')
        self.fails("asset MIME/magic mismatch")

    def test_untrusted_image_sources_are_rejected(self):
        self.add_asset()
        before = self.source.read_text(encoding="utf-8")
        for source in ("https://example.com/a.jpg", "//example.com/a.jpg", "../a.jpg",
                       "data:image/jpeg;base64,/9j/", "data:image/svg+xml,&lt;svg/&gt;", "javascript:alert(1)"):
            with self.subTest(source=source):
                self.source.write_text(before.replace("asset:diagram.jpg", source), encoding="utf-8")
                self.fails("unsupported or executable image source")

    def test_image_needs_nonempty_alt(self):
        self.add_asset()
        before = self.source.read_text(encoding="utf-8")
        for replacement in ('', ' alt="   "'):
            with self.subTest(replacement=replacement):
                self.source.write_text(before.replace(' alt="मूळ आकृती"', replacement), encoding="utf-8")
                self.fails("image alt text")

    def test_image_needs_identified_figure(self):
        self.add_asset()
        self.mutate('<figure id="figure-1">', '<figure>')
        self.fails("identified figure ancestor")

    def test_configured_asset_must_be_used(self):
        self.add_asset(use=False)
        self.fails("configured assets must all be used")

    def test_image_event_and_srcset_attributes_are_rejected(self):
        self.add_asset()
        before = self.source.read_text(encoding="utf-8")
        for attribute in ('onerror="alert(1)"', 'srcset="https://example.com/a.jpg 2x"'):
            with self.subTest(attribute=attribute):
                self.source.write_text(before.replace('<img ', '<img ' + attribute + ' '), encoding="utf-8")
                self.fails("unsupported or executable attribute")

    def test_assets_must_be_object(self):
        self.config["assets"] = []
        self.save_config()
        self.fails("assets must be an object")


if __name__ == "__main__":
    unittest.main(verbosity=2)
