"""Acquisition, output and reader-link tests using temporary generated fixtures."""
from hashlib import sha256
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile
import xml.etree.ElementTree as ET

from acquire import archive_target, download_path, extract_checked
from safe_output import write_atomic
import build
from build import prune_empty_math_layout, serialize_math, validate_reader_links, validate_math_markup


class AcquisitionTests(unittest.TestCase):
    def test_math_markup_rejects_broken_or_injected_html(self):
        for value in [
            '<math><mi>n</mi></div><p></math>',
            '<math><mi>x</mi>',
            '</math>',
            '<math><div><mi>x</mi></div></math>',
        ]:
            with self.subTest(value=value), self.assertRaises(AssertionError):
                validate_math_markup(value)

    def test_math_markup_keeps_valid_source_and_generated_math(self):
        html = '<p><math data-source="source:0"><mi>n</mi></math></p>'
        html += '<math xmlns="http://www.w3.org/1998/Math/MathML"><mtext> x &amp; y </mtext></math>'
        self.assertEqual(validate_math_markup(html), 2)
        self.assertEqual(validate_math_markup('<p>No math.</p>'), 0)

    def test_multiline_table_math_boundary_regression(self):
        import shutil
        import subprocess
        if not shutil.which('pandoc'):
            self.skipTest('Pandoc unavailable')
        first = '<math data-source="Table_01_01_11:0">\n<mi>n</mi>\n</math>'
        second = '<math data-source="Table_01_01_11:1">\n<mi>g</mi><mo>(</mo><mi>n</mi><mo>)</mo>\n</math>'
        def render(md):
            return subprocess.run(['pandoc', '--from=markdown+fenced_divs+raw_html', '--to=html5'],
                                  input=md, text=True, encoding='utf-8', capture_output=True, check=True).stdout
        broken = render(f'::: {{#table}}\n\n| {first} | {second} |\n|---|---|\n| 1 | 8 |\n:::\n')
        with self.assertRaises(AssertionError):
            validate_math_markup(broken)
        repaired = render(f'::: {{#table}}\n\nInput: {first}. Output: {second}.\n\n| Input | Output |\n|---|---|\n| 1 | 8 |\n:::\n')
        self.assertEqual(validate_math_markup(repaired), 2)
        self.assertIn('<table>', repaired)

    def test_math_blank_lines_preserve_token_text(self):
        node = ET.fromstring('<math><mrow>\n\n  <mi>x</mi>\n <mtext> + text </mtext>\n\n </mrow></math>')
        rendered = serialize_math(node)
        self.assertNotIn('\n\n', rendered)
        result = ET.fromstring(rendered)
        self.assertEqual(result.find('.//mtext').text, ' + text ')
        self.assertEqual(result.find('.//mi').text, 'x')

    def test_raw_inline_currency_math_preserves_tokens(self):
        import shutil
        import subprocess
        if not shutil.which('pandoc'):
            self.skipTest('Pandoc unavailable')
        expressions = [
            '<math xmlns="http://www.w3.org/1998/Math/MathML" data-source="tax:0">\n'
            '<mrow><mi>S</mi><mo>≤</mo><mtext>$</mtext><mn>10</mn>'
            '<mtext>,</mtext><mn>000</mn></mrow></math>',
            '<math xmlns="http://www.w3.org/1998/Math/MathML" data-source="tax:1">\n'
            '<mrow><mtext>$</mtext><mn>1000</mn><mtext> nếu </mtext></mrow></math>',
        ]
        markdown = ' hoặc '.join('`' + value + '`{=html}' for value in expressions)
        html = subprocess.run(
            ['pandoc', '--from=markdown+fenced_divs+raw_html', '--to=html5',
             '--mathml', '--fail-if-warnings'], input=markdown, text=True,
            encoding='utf-8', capture_output=True, check=True).stdout
        self.assertEqual(validate_math_markup(html), 2)
        inspector = build.Inspector()
        inspector.feed(html)
        self.assertEqual(inspector.source_math, ['tax:0', 'tax:1'])
        import re
        rendered = re.findall(r'<math\b[^>]*>.*?</math>', html, re.DOTALL)
        ns = '{http://www.w3.org/1998/Math/MathML}'
        for original, result in zip(expressions, rendered):
            def tokens(xml):
                return [(n.tag, n.text) for n in ET.fromstring(xml).iter()
                        if n.tag in {ns + t for t in ('mi', 'mn', 'mo', 'mtext')}]
            self.assertEqual(tokens(original), tokens(result))

    def test_math_without_blank_lines_retains_serialization(self):
        node = ET.fromstring('<math>\n  <mi>x</mi>\n</math>')
        before = ET.tostring(node, encoding='unicode', short_empty_elements=False)
        self.assertEqual(serialize_math(node), before)

    def test_prune_only_empty_math_layout(self):
        node = ET.fromstring('<math><mrow><mtable><mtr><mtd><mrow /></mtd></mtr></mtable><mi>x</mi><mspace width="1em" /></mrow></math>')
        self.assertGreater(prune_empty_math_layout(node), 0)
        self.assertEqual(node.find('.//mi').text, 'x')
        self.assertIsNotNone(node.find('.//mspace'))

    def test_download_boundary(self):
        for value in [".", "downloads", "downloads/../vi-Latn-VN", "C:/Windows"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                download_path(value)

    def test_zip_boundary(self):
        with tempfile.TemporaryDirectory() as folder:
            for name in ["../bad", "/absolute", "C:/bad", "x/../../bad", "..\\bad"]:
                with self.subTest(name=name), self.assertRaises(ValueError):
                    archive_target(Path(folder), name)

    def test_extraction_is_idempotent_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            archive = root / "fixture.zip"
            with zipfile.ZipFile(archive, "w") as output:
                output.writestr("safe/example.txt", "original source")
            destination = root / "extract"
            extract_checked(archive, destination)
            extract_checked(archive, destination)
            target = destination / "safe/example.txt"
            self.assertEqual(target.read_text(), "original source")
            target.write_text("user changes")
            with self.assertRaises(AssertionError):
                extract_checked(archive, destination)
            self.assertEqual(target.read_text(), "user changes")

    def test_atomic_output(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "reader.html"
            write_atomic(target, b"complete version one")
            write_atomic(target, b"complete version two")
            self.assertEqual(target.read_bytes(), b"complete version two")
            self.assertEqual(list(Path(folder).iterdir()), [target])

    def test_low_space_preserves_previous_output(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "reader.html"
            target.write_bytes(b"previous complete reader")
            with patch("safe_output.shutil.disk_usage") as usage:
                usage.return_value.free = 0
                with self.assertRaises(OSError):
                    write_atomic(target, b"new output")
            self.assertEqual(target.read_bytes(), b"previous complete reader")
            self.assertEqual(list(Path(folder).iterdir()), [target])


class ReaderLinkTests(unittest.TestCase):
    CONFIGS = {"A30-U001": {"slug": "A30-U001-functions"},
               "A30-U008": {"slug": "A30-U008-summary"}}
    TARGET = "A30-U001-functions.vi.html"

    def test_local_anchors_and_external_links_need_no_file_or_network_access(self):
        links = ["#local", "#%C4%91%C3%ADch", "https://example.invalid/a?b=c#d",
                 "http://example.invalid", "mailto:reader@example.invalid?subject=Review"]
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(Path, "read_bytes", side_effect=AssertionError("unexpected file read")):
                result = validate_reader_links(links, ["local", "đích"], folder, self.CONFIGS)
        self.assertEqual(result["local_anchor_links"], 2)
        self.assertEqual(result["cross_reader_links"], [])
        self.assertEqual(len(result["external_links"]), 3)
        self.assertTrue(all(item["verification"] == "unverified" and item["fetched"] is False
                            for item in result["external_links"]))

    def test_registered_cross_reader_anchors_have_exact_target_hash_without_rewrites(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / self.TARGET
            original = '<html lang="vi-Latn-VN"><div id="Example_01"></div><span id="đích"></span></html>'.encode("utf-8")
            target.write_bytes(original)
            hrefs = [self.TARGET + "#Example_01", self.TARGET + "#%C4%91%C3%ADch"]
            result = validate_reader_links(hrefs, [], folder, self.CONFIGS)
            self.assertEqual(len(result["cross_reader_links"]), 2)
            for entry in result["cross_reader_links"]:
                self.assertEqual(entry["target_reader"], self.TARGET)
                self.assertEqual(entry["target_unit"], "A30-U001")
                self.assertEqual(entry["target_sha256"], sha256(original).hexdigest())
            self.assertEqual(result["cross_reader_links"][1]["target_anchor"], "đích")
            self.assertEqual(target.read_bytes(), original)

    def test_multiple_links_read_one_consistent_target_snapshot(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / self.TARGET
            target.write_bytes(b'<div id="a"></div><div id="b"></div>')
            read_bytes = Path.read_bytes
            reads = []

            def tracked_read(path):
                reads.append(path)
                return read_bytes(path)

            with patch.object(Path, "read_bytes", tracked_read):
                result = validate_reader_links([self.TARGET + "#a", self.TARGET + "#b",
                                                self.TARGET + "#a"], [], folder, self.CONFIGS)
            self.assertEqual(len(reads), 1)
            self.assertEqual(len(result["cross_reader_links"]), 3)
            self.assertEqual(len({row["target_sha256"] for row in result["cross_reader_links"]}), 1)

    def test_missing_file_missing_anchor_and_duplicate_anchor_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / self.TARGET
            with self.assertRaisesRegex(AssertionError, "does not exist"):
                validate_reader_links([self.TARGET + "#a"], [], folder, self.CONFIGS)
            target.write_bytes(b'<div id="b"></div>')
            with self.assertRaisesRegex(AssertionError, "missing or ambiguous"):
                validate_reader_links([self.TARGET + "#a"], [], folder, self.CONFIGS)
            target.write_bytes(b'<div id="a"></div><span id="a"></span>')
            with self.assertRaisesRegex(AssertionError, "missing or ambiguous"):
                validate_reader_links([self.TARGET + "#a"], [], folder, self.CONFIGS)
            with self.assertRaisesRegex(AssertionError, "broken local"):
                validate_reader_links(["#absent"], ["present"], folder, self.CONFIGS)

    def test_paths_schemes_queries_and_unsupported_targets_are_rejected(self):
        unsafe = [
            "../" + self.TARGET + "#a", "./" + self.TARGET + "#a",
            "nested/" + self.TARGET + "#a", "/" + self.TARGET + "#a",
            "C:/" + self.TARGET + "#a", "C:\\" + self.TARGET + "#a",
            "\\\\server\\share\\" + self.TARGET + "#a",
            "..\\" + self.TARGET + "#a", "//example.invalid/" + self.TARGET + "#a",
            "%2e%2e%2f" + self.TARGET + "#a", self.TARGET.replace("-", "%2D") + "#a",
            "other.vi.html#a", "notes.md#a", "file:///reader.vi.html#a",
            "javascript:alert(1)", "data:text/html,unsafe", "ftp://example.invalid/file",
            self.TARGET, self.TARGET + "#", self.TARGET + "?mode=x#a",
            self.TARGET + "?#a", "#", "", "#bad%ZZ", "#%FF", "#%0A",
            " https://example.invalid", "https://", "http:relative", "mailto:",
        ]
        with tempfile.TemporaryDirectory() as folder:
            for href in unsafe:
                with self.subTest(href=href), self.assertRaises(AssertionError):
                    validate_reader_links([href], ["a"], folder, self.CONFIGS)

    def test_registry_itself_cannot_authorize_unsafe_paths_or_duplicate_names(self):
        invalid = [
            {"bad": {"slug": "../outside"}},
            {"bad": {"slug": "nested/reader"}},
            {"bad": {"slug": "C:\\reader"}},
            {"a": {"slug": "same"}, "b": {"slug": "same"}},
        ]
        with tempfile.TemporaryDirectory() as folder:
            for config in invalid:
                with self.subTest(config=config), self.assertRaises(AssertionError):
                    validate_reader_links([], [], folder, config)

    def test_resolved_target_must_stay_in_the_reader_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = root / self.TARGET
            target.write_bytes(b'<div id="a"></div>')
            resolve = Path.resolve

            def redirected_resolve(path, *args, **kwargs):
                if path.name == self.TARGET:
                    return resolve(root.parent / self.TARGET)
                return resolve(path, *args, **kwargs)

            with patch.object(Path, "resolve", redirected_resolve):
                with self.assertRaisesRegex(AssertionError, "escapes"):
                    validate_reader_links([self.TARGET + "#a"], [], root, self.CONFIGS)
            self.assertEqual(target.read_bytes(), b'<div id="a"></div>')

    def test_non_utf8_target_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / self.TARGET).write_bytes(b"\xff")
            with self.assertRaisesRegex(AssertionError, "not UTF-8"):
                validate_reader_links([self.TARGET + "#a"], [], folder, self.CONFIGS)

    def test_builder_receipt_contains_checked_target_hash_and_unverified_external_link(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ("sources", "translation", "computing", "canon", "review"):
                (root / name).mkdir()
            source = '<section xmlns="http://cnx.rice.edu/cnxml" id="section"><para id="paragraph">Text</para></section>'
            (root / "sources/fixture.cnxml").write_text(source, encoding="utf-8")
            markdown = "# Fixture\n"
            (root / "translation/A30-U008-summary.vi.md").write_bytes(markdown.encode("utf-8"))
            (root / "computing/check_fixture.py").write_text("def tests():\n    return 0\n", encoding="utf-8")
            target_bytes = b'<html><p id="Example_01">Target</p></html>'
            (root / "review" / self.TARGET).write_bytes(target_bytes)
            configs = {
                "A30-U001": {"slug": "A30-U001-functions"},
                "A30-U008": {
                    "slug": "A30-U008-summary", "source": "sources/fixture.cnxml",
                    "math_text": {}, "images": 0, "required_ids": ["section", "paragraph"],
                    "numeric_checks": {}, "computing_check": "computing/check_fixture.py",
                    "minimum_canon_examples": 1, "source_examples": 0,
                    "try_it_exercises": 0, "selected_end_exercises": 0,
                    "visual_receipt": "qa/fixture-visual.json",
                },
            }
            (root / "units.json").write_text(json.dumps(configs), encoding="utf-8")
            canon = {"unit": "A30-U008", "examples_consulted": ["fixture"],
                     "draft_checked": True, "final_checked": True,
                     "translation_sha256": sha256(markdown.encode("utf-8")).hexdigest()}
            (root / "canon/review-A30-U008.json").write_text(json.dumps(canon), encoding="utf-8")
            rendered = ('<html lang="vi-Latn-VN"><h1 id="section">Fixture</h1>'
                        '<p id="paragraph">Text</p><a href="#paragraph">Local</a>'
                        f'<a href="{self.TARGET}#Example_01">Previous</a>'
                        '<a href="https://example.invalid">Optional</a></html>')
            with patch.object(build, "ROOT", root), \
                    patch("sys.argv", ["build.py", "--unit", "A30-U008"]), \
                    patch.object(build.subprocess, "run", return_value=SimpleNamespace(stdout=rendered)), \
                    patch.object(build.subprocess, "check_output", return_value="pandoc fixture\n"), \
                    patch("builtins.print"):
                build.main()
            receipt = json.loads((root / "qa/build-A30-U008.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["cross_reader_link_count"], 1)
            self.assertEqual(receipt["cross_reader_links"][0]["target_sha256"],
                             sha256(target_bytes).hexdigest())
            self.assertEqual(receipt["external_link_count"], 1)
            self.assertEqual(receipt["external_links"][0]["verification"], "unverified")
            self.assertFalse(receipt["external_links"][0]["fetched"])
            self.assertEqual(receipt["internal_links"], 1)
            self.assertEqual((root / "review/A30-U008-summary.vi.html").read_bytes(),
                             rendered.encode("utf-8"))
            self.assertEqual((root / "review" / self.TARGET).read_bytes(), target_bytes)


if __name__ == "__main__":
    unittest.main()
