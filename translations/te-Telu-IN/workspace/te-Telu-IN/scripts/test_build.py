"""Mutation tests for the bounded pilot; no network or full-corpus dependencies."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from build import BASE, load_source, localize, math_signature, MATH, check_math_cases, build, atomic_write


class PilotTests(unittest.TestCase):
    def setUp(self):
        self.source=load_source()
        self.catalog=json.loads((BASE/"translations/TE-B001.te.json").read_text(encoding="utf-8"))

    def test_translation_preserves_math(self):
        self.assertEqual(math_signature(self.source),math_signature(localize(self.source,self.catalog)))

    def test_missing_prose_fails(self):
        del self.catalog["translations"]["s001"]
        with self.assertRaisesRegex(AssertionError,"Untranslated prose"):
            localize(self.source,self.catalog)

    def test_unused_slot_fails(self):
        self.catalog["translations"]["s999"]="సంఖ్య"
        with self.assertRaisesRegex(AssertionError,"Unused"):
            localize(self.source,self.catalog)

    def test_math_translation_fails(self):
        self.catalog["translations"]["s005"]="ఒకటి"
        with self.assertRaisesRegex(AssertionError,"Math token"):
            localize(self.source,self.catalog)

    def test_source_slot_drift_fails(self):
        self.catalog["expected_text_slot_count"]=163
        with self.assertRaisesRegex(AssertionError,"Source slot drift"):
            localize(self.source,self.catalog)

    def test_numeric_mutation_detected(self):
        target=copy.deepcopy(self.source)
        next(target.iter(MATH+"mn")).text="99"
        self.assertNotEqual(math_signature(self.source),math_signature(target))

    def test_exact_math_cases(self):
        self.assertIn("passed",check_math_cases())

    def test_verified_ts_number_set_labels(self):
        terms=self.catalog["translations"]
        self.assertEqual(terms["s047"],"పూర్ణాంకాలు (whole numbers)")
        self.assertEqual(terms["s016"],"సహజ సంఖ్యలు (counting numbers)")
        self.assertNotIn("పూర్ణ సంఖ్య", " ".join(terms.values()))
        bridge=(BASE/"translations/bridge.xhtml").read_text(encoding="utf-8")
        self.assertIn("పూర్ణాంకాలు (whole numbers) 0",bridge)
        self.assertEqual(bridge.count("పూర్ణ సంఖ్యలు (integers)"),1)
        self.assertNotIn("పూర్ణాంకాలు (integers)",bridge)

    def test_failed_atomic_replace_preserves_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"artifact.txt"
            path.write_bytes(b"original")
            with patch("build.os.replace",side_effect=OSError("simulated failure")):
                with self.assertRaises(OSError):
                    atomic_write(path,b"new")
            self.assertEqual(path.read_bytes(),b"original")
            self.assertEqual(list(Path(directory).iterdir()),[path])

    def test_no_build_writes_when_disk_full(self):
        from collections import namedtuple
        usage=namedtuple("usage","total used free")(100,100,0)
        with patch("build.shutil.disk_usage",return_value=usage), patch("build.atomic_write") as writer:
            with self.assertRaisesRegex(AssertionError,"32 MiB"):
                build()
            writer.assert_not_called()

    def test_two_builds_identical(self):
        build()
        first=[(BASE/path).read_bytes() for path in ("generated/TE-B001.te.cnxml","reader/TE-B001.html","qa/build-receipt.json")]
        build()
        second=[(BASE/path).read_bytes() for path in ("generated/TE-B001.te.cnxml","reader/TE-B001.html","qa/build-receipt.json")]
        self.assertEqual(first,second)


if __name__=="__main__":
    unittest.main()
