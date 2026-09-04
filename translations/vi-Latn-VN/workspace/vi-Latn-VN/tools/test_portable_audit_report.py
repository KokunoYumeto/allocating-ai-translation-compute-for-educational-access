"""Focused tests for portable_audit_report; all files are temporary."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

from portable_audit_report import (
    canonical_json_sha256,
    compact_math_evidence,
    rewrite_workspace_paths,
)


class PortableAuditReportTests(unittest.TestCase):
    ROOT = r"C:/portable-test-home\work\LAN ALLOC"

    def test_rewrites_values_and_keys_with_boundary(self):
        report = {
            "source": {"path": self.ROOT + r"\vi-Latn-VN\source.xml"},
            "input_sha256": {self.ROOT + r"\vi-Latn-VN\units.json": "abc"},
            "root": self.ROOT,
            "near_prefix_is_not_a_child": self.ROOT + "-copy/file.json",
            "language": "tập xác định",
        }
        portable = rewrite_workspace_paths(report, self.ROOT)
        self.assertEqual(portable["source"]["path"], "vi-Latn-VN/source.xml")
        self.assertEqual(portable["input_sha256"], {"vi-Latn-VN/units.json": "abc"})
        self.assertEqual(portable["root"], ".")
        self.assertEqual(portable["near_prefix_is_not_a_child"], self.ROOT + "-copy/file.json")
        self.assertEqual(portable["language"], "tập xác định")

    def test_rejects_key_collision_after_rewrite(self):
        report = {
            self.ROOT + r"\same.json": "one",
            self.ROOT.lower().replace("\\", "/") + "/same.json": "two",
        }
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            rewrite_workspace_paths(report, self.ROOT)

    def test_projection_hashes_portable_full_report_before_omission(self):
        report = rewrite_workspace_paths({
            "schema": 1,
            "source": {"path": self.ROOT + r"\source.xml"},
            "missing_direct_math_evidence": [{"key": "a"}, {"key": "b"}],
        }, self.ROOT)
        expected_hash = canonical_json_sha256(report)
        compact = compact_math_evidence(report, "python -B audit.py")
        self.assertNotIn("missing_direct_math_evidence", compact)
        projection = compact["checkpoint_projection"]
        self.assertEqual(projection["omitted_source_math_records"], 2)
        self.assertEqual(projection["canonical_full_report_sha256"], expected_hash)
        self.assertEqual(projection["full_report_command"], "python -B audit.py")
        self.assertIn("Portable workspace-relative", projection["canonical_report_basis"])

    def test_cli_reads_stdin_and_emits_utf8_json(self):
        script = Path(__file__).with_name("portable_audit_report.py")
        source = json.dumps({"path": self.ROOT + r"\đại-số.json"}, ensure_ascii=False).encode()
        result = subprocess.run(
            [sys.executable, "-B", str(script), "--workspace-root", self.ROOT],
            input=source, capture_output=True, check=True,
        )
        self.assertTrue(result.stdout.endswith(b"\n"))
        self.assertEqual(json.loads(result.stdout.decode("utf-8")), {"path": "đại-số.json"})
        self.assertEqual(result.stderr, b"")

    def test_cli_reads_and_writes_explicit_files(self):
        script = Path(__file__).with_name("portable_audit_report.py")
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "full.json"
            output = Path(directory) / "portable.json"
            source.write_text(json.dumps({"path": self.ROOT + r"\x.json"}), encoding="utf-8")
            subprocess.run(
                [sys.executable, "-B", str(script), str(source),
                 "--workspace-root", self.ROOT, "--output", str(output)],
                capture_output=True, check=True,
            )
            self.assertEqual(json.loads(output.read_text("utf-8")), {"path": "x.json"})


if __name__ == "__main__":
    unittest.main()
