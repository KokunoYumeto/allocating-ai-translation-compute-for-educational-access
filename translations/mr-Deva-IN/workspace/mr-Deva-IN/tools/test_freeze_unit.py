"""Regression tests for the small, pinned-source unit freezer.

All inputs are generated in a temporary directory.  These tests never read or
copy the acquired production archives.
"""
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import warnings
import zipfile


TOOLS = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("source_freezer", TOOLS / "freeze_unit.py")
freezer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(freezer)

UNIT = "MR-BRIDGE-919"
JPEG_EN = b"\xff\xd8\xff\xe0canonical-english-jpeg\xff\xd9"
JPEG_ID = b"\xff\xd8\xff\xe0indonesian-reference-jpeg\xff\xd9"
PNG_EN = b"\x89PNG\r\n\x1a\ncanonical-english-png"
PNG_ID = b"\x89PNG\r\n\x1a\nindonesian-reference-png"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def module_xml(locale, selected_images=("diagram.jpg", "chart.png"),
               extra_images=("not-selected.jpg",), source="fs-alpha"):
    images = "".join(
        '<image id="image-%s-%d" src="../../media/%s"/>' % (locale, number, name)
        for number, name in enumerate(selected_images, 1)
    )
    extras = "".join(
        '<image id="other-%s-%d" src="../../media/%s"/>' % (locale, number, name)
        for number, name in enumerate(extra_images, 1)
    )
    return ('''<?xml version="1.0" encoding="UTF-8"?>
<document xmlns="http://cnx.rice.edu/cnxml"
 xmlns:m="http://www.w3.org/1998/Math/MathML">
  <section id="%s"><para>%s selected</para>%s
    <m:math><m:mi>%s</m:mi></m:math>
    <link url="https://example.test/%s"/>
  </section>
  <section id="fs-other"><para>%s other</para>%s</section>
</document>''' % (source, locale, images, locale, locale, locale, extras)).encode("utf-8")


class FreezeUnitTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="mr-freezer-small-test-")
        self.root = Path(self.temporary.name)
        self.base = self.root / "mr-Deva-IN"
        for directory in ("translations", "units", "provenance", "downloads/fixtures"):
            (self.base / directory).mkdir(parents=True)
        self.translation = self.base / "translations" / f"{UNIT}.xml"
        self.config_path = self.base / "units" / f"{UNIT}.json"
        self.translation.write_text(self.translation_xml(), encoding="utf-8")
        self.config = {"title": "लहान चाचणी", "source_count": 1}
        self.save_config()
        self.master = {
            "schema": 1,
            "archives": [],
            "witnesses": [],
        }
        self.archive_entries = {}
        self.make_course("A20")
        self.make_course("A30")
        self.save_master()
        self.base_patch = patch.object(freezer, "BASE", self.base)
        self.base_patch.start()

    def tearDown(self):
        self.base_patch.stop()
        self.temporary.cleanup()

    def translation_xml(self, course="A20", source="fs-alpha", asset_names=()):
        figures = "".join(
            f'<figure id="figure-{number}"><img src="asset:{name}" alt="आकृती"/></figure>'
            for number, name in enumerate(asset_names, 1)
        )
        return (f'<article lang="mr-Deva-IN" id="{UNIT}">'
                f'<section id="{source}" data-source="{course}:m100#{source}">'
                f'<p>निवड</p>{figures}</section></article>')

    def save_config(self):
        self.config_path.write_text(json.dumps(self.config, ensure_ascii=False), encoding="utf-8")

    def save_master(self):
        (self.base / "sources.lock.json").write_text(
            json.dumps(self.master, ensure_ascii=False), encoding="utf-8")

    def archive_prefix(self, course, locale):
        if course == "A30" and locale == "id":
            return "repo/source"
        if locale == "id":
            return "source"
        return "canonical-tree"

    def make_course(self, course):
        for locale in ("en", "id"):
            prefix = self.archive_prefix(course, locale)
            entries = {
                f"{prefix}/modules/m100/index.cnxml": module_xml(locale),
                f"{prefix}/media/diagram.jpg": JPEG_EN if locale == "en" else JPEG_ID,
                f"{prefix}/media/chart.png": PNG_EN if locale == "en" else PNG_ID,
                f"{prefix}/media/not-selected.jpg": b"not selected",
            }
            # A30 Indonesian packages contain a distinct upstream authority tree.
            if course == "A30" and locale == "id":
                entries["authority/upstream/modules/m100/index.cnxml"] = module_xml("authority")
                entries["authority/upstream/media/diagram.jpg"] = b"authority-not-ID"
                entries["authority/upstream/media/chart.png"] = b"authority-not-ID-png"
            self.set_archive(f"{course}-{locale}", entries)

    def set_archive(self, key, entries, duplicate_entries=()):
        relative = f"downloads/fixtures/{key}.zip"
        archive = self.root / relative
        archive.parent.mkdir(parents=True, exist_ok=True)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as handle:
                for name, data in entries.items():
                    handle.writestr(name, data)
                for name, data in duplicate_entries:
                    handle.writestr(name, data)
        raw = archive.read_bytes()
        self.archive_entries[key] = (dict(entries), tuple(duplicate_entries))
        record = {"id": key, "path": relative, "bytes": len(raw), "sha256": digest(raw)}
        current = [item for item in self.master["archives"] if item["id"] != key]
        self.master["archives"] = current + [record]
        if hasattr(self, "master"):
            self.save_master()
        return archive

    def rewrite_archive(self, key, entries=None, duplicate_entries=None):
        old_entries, old_duplicates = self.archive_entries[key]
        return self.set_archive(key, entries if entries is not None else old_entries,
                                old_duplicates if duplicate_entries is None else duplicate_entries)

    def pin(self, key):
        return next(item for item in self.master["archives"] if item["id"] == key)

    def run_freeze(self):
        stream = io.StringIO()
        with redirect_stdout(stream):
            freezer.freeze(UNIT)
        return json.loads(stream.getvalue())

    def lock(self):
        return json.loads((self.base / "provenance" / f"{UNIT}.lock.json").read_text(encoding="utf-8"))

    def output_snapshot(self):
        paths = [path for path in self.root.rglob("*") if path.is_file()
                 and ("provenance" in path.parts or "assets" in path.parts or
                      "source-image-qa" in path.parts or path == self.config_path)]
        return {path.relative_to(self.root).as_posix(): path.read_bytes() for path in paths}

    def assert_no_unit_outputs(self):
        self.assertFalse((self.base / "provenance" / f"{UNIT}.lock.json").exists())
        self.assertFalse((self.base / "provenance" / UNIT).exists())
        self.assertFalse((self.base / "assets" / UNIT).exists())
        self.assertFalse((self.root / "downloads/mr-Deva-IN/source-image-qa" / UNIT).exists())

    def test_selected_fragments_and_bilingual_provenance_only(self):
        receipt = self.run_freeze()
        self.assertEqual(receipt["selections"], 1)
        self.assertEqual(receipt["committed_assets"], 0)
        lock = self.lock()
        master_raw = (self.base / "sources.lock.json").read_bytes()
        self.assertEqual(lock["witnesses"][0], {
            "path": "sources.lock.json", "sha256": digest(master_raw),
            "bytes": len(master_raw), "source": "existing corpus lock",
        })
        selection = lock["source_selections"][0]
        self.assertEqual(selection["locator"], "A20:m100#fs-alpha")
        self.assertEqual([item["locale"] for item in selection["sources"]], ["en", "id"])
        self.assertEqual(selection["sources"][0]["outgoing_urls"], ["https://example.test/en"])
        self.assertEqual(selection["sources"][1]["outgoing_urls"], ["https://example.test/id"])
        self.assertEqual(len(selection["sources"][0]["math_sha256"]), 1)
        for locale in ("en", "id"):
            path = self.base / "provenance" / UNIT / f"{locale}-m100-fs-alpha.xml"
            data = path.read_bytes()
            self.assertIn(b'fs-alpha', data)
            self.assertNotIn(b'fs-other', data)
            witness = next(item for item in lock["witnesses"]
                           if item["path"] == f"provenance/{UNIT}/{locale}-m100-fs-alpha.xml")
            self.assertEqual((witness["sha256"], witness["bytes"]), (digest(data), len(data)))
        self.assertFalse((self.base / "provenance" / UNIT / "en-m100-fs-other.xml").exists())
        self.assertFalse((self.root / "downloads/mr-Deva-IN/source-image-qa" / UNIT /
                          "en-not-selected.jpg").exists())

    def test_applicable_original_notice_is_verified_and_reused(self):
        notice = self.base / "provenance/notices/A20-en/LICENSE"
        notice.parent.mkdir(parents=True)
        notice.write_bytes(b"small original notice\n")
        record = {"path": "provenance/notices/A20-en/LICENSE",
                  "sha256": digest(notice.read_bytes()), "bytes": notice.stat().st_size,
                  "source": "fixture archive:LICENSE"}
        self.master["witnesses"] = [record]
        self.save_master()
        self.run_freeze()
        self.assertIn(record, self.lock()["witnesses"])

        notice.write_bytes(b"drifted notice")
        before = self.output_snapshot()
        with self.assertRaisesRegex(ValueError, "original notice drift"):
            self.run_freeze()
        self.assertEqual(before, self.output_snapshot())

    def test_exact_canonical_assets_config_witnesses_and_review_copies(self):
        self.translation.write_text(
            self.translation_xml(asset_names=("diagram.jpg", "chart.png")), encoding="utf-8")
        receipt = self.run_freeze()
        self.assertEqual(receipt["committed_assets"], 2)
        self.assertEqual(receipt["committed_asset_bytes"], len(JPEG_EN) + len(PNG_EN))
        config = json.loads(self.config_path.read_text(encoding="utf-8"))
        lock = self.lock()
        expected = {"chart.png": (PNG_EN, "image/png"),
                    "diagram.jpg": (JPEG_EN, "image/jpeg")}
        for name, (raw, mime) in expected.items():
            relative = f"assets/{UNIT}/{name}"
            self.assertEqual((self.base / relative).read_bytes(), raw)
            self.assertEqual(config["assets"][name],
                             {"path": relative, "sha256": digest(raw), "mime": mime})
            witness = next(item for item in lock["witnesses"] if item["path"] == relative)
            self.assertEqual((witness["sha256"], witness["bytes"], witness["mime"]),
                             (digest(raw), len(raw), mime))
            self.assertEqual(witness["serialization"], "unchanged original canonical image bytes")
            self.assertEqual((self.root / "downloads/mr-Deva-IN/source-image-qa" / UNIT /
                              f"en-{name}").read_bytes(), raw)
            self.assertEqual((self.root / "downloads/mr-Deva-IN/source-image-qa" / UNIT /
                              f"id-{name}").read_bytes(), JPEG_ID if name.endswith("jpg") else PNG_ID)
        self.assertEqual(len(lock["source_images"]), 4)
        self.assertEqual(sum("committed_asset" in item for item in lock["source_images"]), 2)

    def test_A30_uses_repo_source_not_authority_upstream(self):
        self.translation.write_text(
            self.translation_xml(course="A30", asset_names=("diagram.jpg",)), encoding="utf-8")
        self.run_freeze()
        selection = self.lock()["source_selections"][0]
        source = next(item for item in selection["sources"] if item["locale"] == "id")
        self.assertTrue(source["member"].startswith("repo/source/"))
        self.assertNotIn("authority/upstream", source["member"])
        self.assertIn(b"id selected", (self.base / source["fragment_path"]).read_bytes())
        image = next(item for item in self.lock()["source_images"] if item["locale"] == "id")
        self.assertTrue(image["member"].startswith("repo/source/"))

    def test_archive_byte_count_hash_and_selected_member_crc_are_checked(self):
        original = self.pin("A20-en").copy()
        self.pin("A20-en")["bytes"] += 1
        self.save_master()
        with self.assertRaisesRegex(ValueError, "archive byte count drift"):
            self.run_freeze()
        self.assert_no_unit_outputs()

        self.master["archives"] = [original if item["id"] == "A20-en" else item
                                   for item in self.master["archives"]]
        self.pin("A20-en")["sha256"] = "0" * 64
        self.save_master()
        with self.assertRaisesRegex(ValueError, "archive hash drift"):
            self.run_freeze()
        self.assert_no_unit_outputs()

        archive = self.rewrite_archive("A20-en")
        raw = archive.read_bytes()
        needle = b"en selected"
        self.assertEqual(raw.count(needle), 1)
        archive.write_bytes(raw.replace(needle, b"XX selected"))
        corrupt = archive.read_bytes()
        self.pin("A20-en").update(bytes=len(corrupt), sha256=digest(corrupt))
        self.save_master()
        with self.assertRaises(zipfile.BadZipFile):
            self.run_freeze()
        self.assert_no_unit_outputs()

    def test_source_wrapper_and_archive_source_ids_are_exact(self):
        self.translation.write_text(self.translation_xml(source="different"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "missing/duplicate source ID"):
            self.run_freeze()
        self.assert_no_unit_outputs()

        self.translation.write_text(self.translation_xml(), encoding="utf-8")
        entries, _ = self.archive_entries["A20-id"]
        changed = dict(entries)
        changed[next(name for name in changed if name.endswith("index.cnxml"))] = module_xml(
            "id", source="fs-missing")
        self.rewrite_archive("A20-id", changed)
        with self.assertRaisesRegex(ValueError, "missing/duplicate source ID"):
            self.run_freeze()
        self.assert_no_unit_outputs()

    def test_translation_source_wrapper_id_must_match_locator(self):
        self.translation.write_text(
            self.translation_xml().replace('id="fs-alpha"', 'id="wrong"', 1), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "source wrapper ID must be preserved"):
            self.run_freeze()
        self.assert_no_unit_outputs()

    def test_duplicate_source_wrapper_cannot_overwrite_one_fragment_path(self):
        xml = self.translation_xml()
        duplicate = ('<section id="fs-alpha" data-source="A20:m100#fs-alpha">'
                     '<p>निवड पुन्हा</p></section>')
        self.translation.write_text(xml.replace('</article>', duplicate + '</article>'), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate source selection"):
            self.run_freeze()
        self.assert_no_unit_outputs()

    def test_module_and_image_ambiguity_are_rejected(self):
        entries, _ = self.archive_entries["A20-en"]
        extra = dict(entries)
        extra["second/modules/m100/index.cnxml"] = module_xml("second")
        self.rewrite_archive("A20-en", extra)
        with self.assertRaisesRegex(ValueError, "ambiguous module member"):
            self.run_freeze()
        self.assert_no_unit_outputs()

        self.rewrite_archive("A20-en", entries)
        image_member = next(name for name in entries if name.endswith("/media/diagram.jpg"))
        self.rewrite_archive("A20-en", entries,
                             duplicate_entries=((image_member, JPEG_EN + b"duplicate"),))
        with self.assertRaisesRegex(ValueError, "missing/duplicate archive image member"):
            self.run_freeze()
        self.assert_no_unit_outputs()

    def test_missing_image_and_conflicting_basename_are_rejected(self):
        entries, _ = self.archive_entries["A20-en"]
        missing = {name: data for name, data in entries.items()
                   if not name.endswith("/media/diagram.jpg")}
        self.rewrite_archive("A20-en", missing)
        with self.assertRaisesRegex(ValueError, "missing/duplicate archive image member"):
            self.run_freeze()
        self.assert_no_unit_outputs()

        # Two selected source images with one basename would overwrite one review path.
        changed = dict(entries)
        module_name = next(name for name in changed if name.endswith("index.cnxml"))
        changed[module_name] = changed[module_name].replace(
            b'</section>', b'<image id="same-name" src="../../other/diagram.jpg"/></section>', 1)
        changed[next(name for name in changed if name.endswith("/media/diagram.jpg"))
                .replace("/media/", "/other/")] = b"different same basename"
        self.rewrite_archive("A20-en", changed)
        with self.assertRaisesRegex(ValueError, "conflicting image basename"):
            self.run_freeze()
        self.assert_no_unit_outputs()

    def test_image_path_traversal_backslash_colon_and_bad_basename_are_rejected(self):
        entries, _ = self.archive_entries["A20-en"]
        module_name = next(name for name in entries if name.endswith("index.cnxml"))
        for source, message in (("../../../../escape.jpg", "unsafe archive image member"),
                                (r"..\\..\\media\\diagram.jpg", "unsafe archive image source"),
                                ("C:/outside.jpg", "unsafe archive image source"),
                                ("bad%name.jpg", "unsafe archive image basename")):
            with self.subTest(source=source):
                changed = dict(entries)
                changed[module_name] = module_xml("en", selected_images=(source,))
                member = module_name.rsplit("/modules/", 1)[0] + "/media/bad%name.jpg"
                if "%" in source:
                    changed[member] = JPEG_EN
                self.rewrite_archive("A20-en", changed)
                with self.assertRaisesRegex(ValueError, message):
                    self.run_freeze()
                self.assert_no_unit_outputs()

    def test_requested_asset_missing_ambiguous_bad_magic_and_unsafe_name(self):
        self.translation.write_text(
            self.translation_xml(asset_names=("unseen.jpg",)), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "asset must identify one selected canonical"):
            self.run_freeze()
        self.assert_no_unit_outputs()

        self.translation.write_text(
            self.translation_xml(asset_names=("diagram.jpg",)), encoding="utf-8")
        entries, _ = self.archive_entries["A20-en"]
        bad = dict(entries)
        image_name = next(name for name in bad if name.endswith("/media/diagram.jpg"))
        bad[image_name] = b"not a JPEG"
        self.rewrite_archive("A20-en", bad)
        with self.assertRaisesRegex(ValueError, "image extension/signature mismatch"):
            self.run_freeze()
        self.assert_no_unit_outputs()

        for source in ("asset:../diagram.jpg", "asset:/diagram.jpg", "asset:a/diagram.jpg",
                       "asset:diagram.svg", "https://example.test/diagram.jpg", ""):
            with self.subTest(source=source):
                self.rewrite_archive("A20-en", entries)
                xml = self.translation_xml(asset_names=("diagram.jpg",))
                self.translation.write_text(xml.replace("asset:diagram.jpg", source), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "unsupported image reference"):
                    self.run_freeze()
                self.assert_no_unit_outputs()

    def test_canonical_asset_is_ambiguous_across_two_selected_members(self):
        entries, _ = self.archive_entries["A20-en"]
        changed = dict(entries)
        module_name = next(name for name in changed if name.endswith("index.cnxml"))
        changed[module_name] = changed[module_name].replace(
            b'</section>', b'<image id="same-name" src="../../other/diagram.jpg"/></section>', 1)
        changed[next(name for name in changed if name.endswith("/media/diagram.jpg"))
                .replace("/media/", "/other/")] = JPEG_EN
        self.rewrite_archive("A20-en", changed)
        self.translation.write_text(
            self.translation_xml(asset_names=("diagram.jpg",)), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "asset must identify one selected canonical"):
            self.run_freeze()
        self.assert_no_unit_outputs()

    def test_staging_failure_preserves_previous_checkpoint_and_cleans_temps(self):
        self.translation.write_text(
            self.translation_xml(asset_names=("diagram.jpg",)), encoding="utf-8")
        self.run_freeze()
        before = self.output_snapshot()
        real_named = tempfile.NamedTemporaryFile
        count = 0

        def fail_while_staging(**kwargs):
            nonlocal count
            count += 1
            if count == 3:
                raise OSError("synthetic staging failure")
            return real_named(**kwargs)

        with patch.object(freezer.tempfile, "NamedTemporaryFile", side_effect=fail_while_staging):
            with self.assertRaisesRegex(OSError, "synthetic staging failure"):
                self.run_freeze()
        self.assertEqual(before, self.output_snapshot())
        self.assertEqual([], list(self.root.rglob("*.tmp")))

    def test_refreeze_without_images_removes_stale_asset_configuration(self):
        self.translation.write_text(
            self.translation_xml(asset_names=("diagram.jpg",)), encoding="utf-8")
        self.run_freeze()
        self.assertIn("assets", json.loads(self.config_path.read_text(encoding="utf-8")))

        self.translation.write_text(self.translation_xml(), encoding="utf-8")
        self.run_freeze()
        config = json.loads(self.config_path.read_text(encoding="utf-8"))
        self.assertNotIn("assets", config)
        self.assertFalse(any(item["path"].startswith(f"assets/{UNIT}/")
                             for item in self.lock()["witnesses"]))

    def test_review_images_checks_pins_selection_and_A30_repo_source(self):
        stream = io.StringIO()
        with redirect_stdout(stream):
            freezer.review_images(UNIT, "A30", ["diagram.jpg"])
        records = [json.loads(line) for line in stream.getvalue().splitlines()]
        self.assertEqual([item["locale"] for item in records], ["en", "id"])
        self.assertTrue(records[1]["member"].startswith("repo/source/"))
        self.assertEqual((self.root / "downloads/mr-Deva-IN/source-image-qa" / UNIT /
                          "en-diagram.jpg").read_bytes(), JPEG_EN)
        self.assertEqual((self.root / "downloads/mr-Deva-IN/source-image-qa" / UNIT /
                          "id-diagram.jpg").read_bytes(), JPEG_ID)

        self.pin("A30-en")["bytes"] += 1
        self.save_master()
        with self.assertRaisesRegex(ValueError, "archive byte count drift"):
            freezer.review_images(UNIT, "A30", ["diagram.jpg"])

    def test_review_images_rejects_invalid_and_ambiguous_requests_without_writes(self):
        for unit, course, names in (("../bad", "A20", ["diagram.jpg"]),
                                    (UNIT, "B20", ["diagram.jpg"]),
                                    (UNIT, "A20", []),
                                    (UNIT, "A20", ["../diagram.jpg"])):
            with self.subTest(unit=unit, course=course, names=names), \
                    self.assertRaisesRegex(ValueError, "invalid"):
                freezer.review_images(unit, course, names)
        self.assertFalse((self.root / "downloads/mr-Deva-IN/source-image-qa" / UNIT).exists())

        entries, _ = self.archive_entries["A20-en"]
        extra = dict(entries)
        extra["second/media/diagram.jpg"] = JPEG_EN
        self.rewrite_archive("A20-en", extra)
        with self.assertRaisesRegex(ValueError, "ambiguous image member"):
            freezer.review_images(UNIT, "A20", ["diagram.jpg"])
        self.assertFalse((self.root / "downloads/mr-Deva-IN/source-image-qa" / UNIT).exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
