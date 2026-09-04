"""Drafting-author source/mathematics regressions for frozen MR-BRIDGE-011.

This is NOT writer-independent review, browser QA, or native-speaker approval.
Run with python -B. Stdlib only; no eval, downloads, extraction, builds, or writes.
Original raster readings are agent observations, not automated OCR. Their exact
56-file inventory and bytes are pinned below and compared with selected ZIP
members. The shared narrow interpreter uses exact Fraction coefficients.
"""
from copy import deepcopy
from fractions import Fraction as F
import hashlib
from pathlib import Path
import re
import unicodedata
import unittest
import xml.etree.ElementTree as ET
import zipfile

from test_unit6_math import evaluate, mathml_display, read_json, shape


BASE = Path(__file__).resolve().parents[1]
UNIT = "MR-BRIDGE-011"
C = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SELECTED_IDS = ("fs-id1167836692527", "fs-id1167836521479",
                "fs-id1167829859398", "fs-id1167833175472")
MODULE_PINS = {
    "en": ("A20-canonical.zip", "osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81373/index.cnxml",
           "2b606026c2b34cdf69acfa29bfe4b90abdb6961a322a78c7ec20107e0948b05c",
           "effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917"),
    "id": ("A20-v0.3.0-source.zip", "source/modules/m81373/index.cnxml",
           "e9e593b31587995170c520b9175f2e0c0cb335282c951bb1d769f775344311ee",
           "a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7"),
}
FRAGMENT_PINS = dict(zip(SELECTED_IDS, (
    ("75daadee65d12b5d1e36efe90106ea7045c4a040ebad1fcbf5c705269164425c", "3d9247609a2b1a958d818e3e1f489d7b58282b48f62572ac8249616d0fe060af"),
    ("4e17122750afabde26723bf8883a439169276e822adbbf55ee3d8b11f0fce627", "5ae74a7e35ff392448cb86dc620cac161adfec54d68c39687c2c06bc36922c6c"),
    ("29a2d685890caf0f7cafdddc7fb8109f353c3df8f611c5a3f8b8efcb61da7c28", "21f2c4802f0ce18c0de15f1cc88e8449242cd9a0b7a24cab72c79bbcceaeae48"),
    ("ead3a5935523a8c1b2c78e522f384f2e2014df160f10f1c1440d75f985bc810d", "ed2f2e408df69d965f4828c4abdcd13812f279c7363ff36e48426bc9c1c49a09"),
)))
TARGET_PINS = {
    "translations/MR-BRIDGE-011.xml": "1a5a8cca15aa154ca15f24ec2708502cd1837f4a3714d9e781483d956e1573f1",
    "units/MR-BRIDGE-011.json": "8755902abf15d4729374d5a853f7d64a105a3040de2ebe3065899e1e3e94591c",
}
# SHA-256 of sorted UTF-8 lines locale|basename|sha256|bytes, with a final LF.
# This binds every individual raster pin without duplicating the 56-line table
# already preserved in MR-BRIDGE-011-drafting-notes.md and the frozen lock.
IMAGE_INVENTORY_SHA256 = "70bbc45bfeaf09eb6f39d2b51c54009b073a0fca09c2a88a22efaa08751b9fb4"
RELATION = tuple((F(x), F(x * x)) for x in range(1, 6))
F_RULE = "f(x)=2x²+3x−1"
G_RULE = "g(x)=3x−5"
# Literal readings of the canonical pixels, including every intermediate form.
# Equality of evaluated polynomials alone would not catch a skipped source row.
PIXEL_FORMULAS = {
    "015a": "f(x)=2x²+3x−1", "015b": "f(3)=2(3)²+3·3−1",
    "015c": "f(3)=2·9+3·3−1", "015d": "f(3)=18+9−1", "015e": "f(3)=26",
    "016b": "f(x)=2x²+3x−1", "016c": "f(−2)=2(−2)²+3(−2)−1",
    "016d": "f(−2)=2·4+(−6)−1", "016e": "f(−2)=8+(−6)−1", "016f": "f(−2)=1",
    "017a": "f(x)=2x²+3x−1", "017b": "f(a)=2(a)²+3·a−1", "017c": "f(a)=2a²+3a−1",
    "018a": "g(x)=3x−5", "018b": "g(h²)=3h²−5", "018c": "g(h²)=3h²−5",
    "019a": "g(x)=3x−5", "019b": "g(x+2)=3(x+2)−5", "019c": "g(x+2)=3x+6−5", "019d": "g(x+2)=3x+1",
    "020b": "g(x)=3x−5", "020c": "g(2)=3·2−5", "020d": "g(2)=1",
    "020e": "g(x)+g(2)=3x−5+1", "020f": "g(x)+g(2)=3x−5+1", "020g": "g(x)+g(2)=3x−4",
}
TABLES = (
    ("fs-id1167836507536", 5), ("fs-id1167829740069", 5), ("fs-id1167836600305", 3),
    ("fs-id1171790386499", 3), ("fs-id1171792580965", 4), ("fs-id1167836606104", 6),
)
ROW_PROSE = (
    ("", "f(3) काढण्यासाठी x च्या जागी 3 ठेवा.", "सोपी करा.", "", ""),
    ("", "f(−2) काढण्यासाठी x च्या जागी −2 ठेवा.", "सोपी करा.", "", ""),
    ("", "f(a) काढण्यासाठी x च्या जागी a ठेवा.", "सोपी करा."),
    ("", "g(h²) काढण्यासाठी x च्या जागी h² ठेवा.", ""),
    ("", "g(x + 2) काढण्यासाठी x च्या जागी x + 2 ठेवा.", "सोपी करा.", ""),
    ("", "g(x) + g(2) काढण्यासाठी आधी g(2) काढा.", "", "आता g(x) + g(2) काढा.", "सोपी करा.", ""),
)


def text(node):
    return "".join(node.itertext()).strip()


def compact(value):
    return re.sub(r"\s+", "", value).replace("−", "-")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def local_path(relative):
    result = (BASE / relative).resolve()
    if not result.is_relative_to(BASE):
        raise ValueError("path escapes language directory")
    return result


def image_name(short):
    suffix = "_img_new.jpg" if short[:3] in ("018", "019") else "_img.jpg"
    return "CNX_IntAlg_Figure_03_05_" + short + suffix


def short_name(source_media):
    name = source_media.find(C + "image").get("src").split("/")[-1]
    match = re.fullmatch(r"CNX_IntAlg_Figure_03_05_(\d{3}[a-g])_img(?:_new)?\.jpg", name)
    if not match or name != image_name(match[1]):
        raise ValueError("unexpected source media")
    return match[1]


def source_math(node):
    # Only insignificant MathML spacing is removed, not signs or grouping.
    copied = deepcopy(node)
    for parent in copied.iter():
        for child in list(parent):
            if child.tag == M + "mspace":
                parent.remove(child)
    return mathml_display(copied).rstrip(",.:")


def signature(node):
    """Namespace/attribute/text/child comparison, ignoring indentation only."""
    norm = lambda value: " ".join((value or "").split())
    return (node.tag, sorted(node.attrib.items()), norm(node.text),
            [(signature(child), norm(child.tail)) for child in node])


def pairs(display):
    value = compact(display)
    if not re.fullmatch(r"\{\(-?\d+,-?\d+\)(?:,\(-?\d+,-?\d+\))*\}", value):
        raise ValueError("expected a complete integer ordered-pair set")
    return tuple((F(x), F(y)) for x, y in re.findall(r"\((-?\d+),(-?\d+)\)", value))


def members(display):
    value = compact(display)
    if not re.fullmatch(r"\{-?\d+(?:,-?\d+)*\}", value):
        raise ValueError("expected a complete integer set")
    return tuple(F(n) for n in value[1:-1].split(","))


def equality(display, definition):
    sides = display.split("=")
    if len(sides) != 2:
        raise ValueError("expected one equality")
    return evaluate(sides[0], definition) == evaluate(sides[1], definition)


class Unit11RegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (BASE / f"translations/{UNIT}.xml").read_bytes()
        cls.root = ET.fromstring(cls.raw)
        cls.config = read_json(BASE / f"units/{UNIT}.json")
        cls.lock = read_json(BASE / f"provenance/{UNIT}.lock.json")
        cls.ids, cls.checks = {}, {}
        for node in cls.root.iter():
            if node.get("id"):
                if node.get("id") in cls.ids:
                    raise ValueError("duplicate target ID")
                cls.ids[node.get("id")] = node
            if "data-check" in node.attrib:
                if node.get("data-check") in cls.checks:
                    raise ValueError("duplicate math key")
                cls.checks[node.get("data-check")] = text(node)
        cls.sources = {}
        for selection in cls.lock["source_selections"]:
            sid = selection["target_id"]
            for source in selection["sources"]:
                locale = source["locale"]
                expected = FRAGMENT_PINS[sid][("en", "id").index(locale)]
                raw = local_path(source["fragment_path"]).read_bytes()
                if source["fragment_sha256"] != expected or sha(raw) != expected:
                    raise ValueError("reviewed fragment pin drift")
                if (sid, locale) in cls.sources:
                    raise ValueError("duplicate source fragment")
                cls.sources[(sid, locale)] = ET.fromstring(raw)

    def test_01_frozen_scope_fragment_and_witness_pins(self):
        self.assertEqual(self.lock["unit"], UNIT)
        self.assertEqual(self.lock["locale"], "mr-Deva-IN")
        selections = self.lock["source_selections"]
        self.assertEqual([s["target_id"] for s in selections], list(SELECTED_IDS))
        self.assertEqual(set(self.sources), {(sid, lang) for sid in SELECTED_IDS for lang in MODULE_PINS})
        witnesses = {(w["path"], w["sha256"]) for w in self.lock["witnesses"]}
        self.assertEqual(len(witnesses), 17)
        self.assertEqual(len(self.lock["witnesses"]), 17)
        for path, digest in witnesses:
            self.assertEqual(sha(local_path(path).read_bytes()), digest, path)
        for s in selections:
            self.assertEqual(s["locator"], "A20:m81373#" + s["target_id"])
            self.assertEqual([x["locale"] for x in s["sources"]], ["en", "id"])
            for source in s["sources"]:
                self.assertEqual(source["module_sha256"], MODULE_PINS[source["locale"]][2])
                self.assertIn((source["fragment_path"], source["fragment_sha256"]), witnesses)

    def test_02_complete_frozen_blocks_match_actual_pinned_archive_module(self):
        for locale, (archive, member, digest, archive_digest) in MODULE_PINS.items():
            with zipfile.ZipFile(BASE.parent / "downloads/mr-Deva-IN/releases" / archive) as handle:
                raw = handle.read(member)  # One module member, never extraction.
            self.assertEqual(sha(raw), digest)
            module = ET.fromstring(raw)
            blocks = [n for n in module.iter() if n.get("id") in SELECTED_IDS]
            self.assertEqual([n.get("id") for n in blocks], list(SELECTED_IDS))
            for block in blocks:
                self.assertEqual(signature(block), signature(self.sources[(block.get("id"), locale)]))

    def test_03_reviewed_target_bytes_locale_and_config(self):
        for path, digest in TARGET_PINS.items():
            self.assertEqual(sha((BASE / path).read_bytes()), digest, path)
        self.assertEqual(self.root.get("id"), UNIT)
        self.assertEqual(self.root.get("lang"), "mr-Deva-IN")
        decoded = self.raw.decode("utf-8")
        self.assertEqual(unicodedata.normalize("NFC", decoded), decoded)
        self.assertNotIn("\ufffd", decoded)
        self.assertEqual(self.checks, self.config["expected_math"])
        self.assertEqual(len(self.checks), 54)
        for key, count in (("source_count", 4), ("translated_worked_examples", 3), ("translated_definitions", 1),
                           ("translated_practice_items", 0), ("translated_resource_notes", 0), ("original_practice_items", 0)):
            self.assertEqual(self.config[key], count)
        self.assertEqual(self.config["question_ids"], [])
        self.assertFalse(self.config.get("assets"))
        for term in self.config["required_terms"]:
            self.assertIn(term, text(self.root))

    def test_04_all_65_original_ids_order_and_ancestry(self):
        actual = [n.get("id") for n in self.root.iter() if n.get("id", "").startswith("fs-id")]
        self.assertEqual(len(self.ids), 67)
        for locale in MODULE_PINS:
            expected = [n.get("id") for sid in SELECTED_IDS for n in self.sources[(sid, locale)].iter() if n.get("id")]
            self.assertEqual(len(expected), 65)
            self.assertEqual(len(set(expected)), 65)
            self.assertEqual(actual, expected)
            self.assertEqual([sum(bool(n.get("id")) for n in self.sources[(sid, locale)].iter()) for sid in SELECTED_IDS], [10, 26, 27, 2])
            for sid in SELECTED_IDS:
                for source in self.sources[(sid, locale)].iter():
                    if source.get("id"):
                        source_children = [n.get("id") for n in source.iter() if n.get("id")]
                        target_children = [n.get("id") for n in self.ids[source.get("id")].iter() if n.get("id", "").startswith("fs-id")]
                        self.assertEqual(target_children, source_children)
        self.assertEqual([n.get("data-source") for n in self.root.iter() if n.get("data-source")],
                         ["A20:m81373#" + sid for sid in SELECTED_IDS])

    def test_05_zero_new_unique_selectors_and_legacy_unchanged(self):
        raw = (BASE / "translations/MR-BRIDGE-001.xml").read_bytes()
        self.assertEqual(sha(raw), "367314e8948ae28ba17de187ebca4e09d294e2c472a20c433538adb8dd06aac9")
        pilot = ET.fromstring(raw)
        legacy = {n.get("data-source") for n in pilot.iter() if n.get("data-source")}
        current = {n.get("data-source") for n in self.root.iter() if n.get("data-source")}
        self.assertEqual(len(current), 4)
        self.assertEqual(current - legacy, set())
        self.assertEqual(len(legacy - current), 6)
        pilot_ids = {n.get("id") for n in pilot.iter() if n.get("id")}
        self.assertEqual(len({sid for sid in self.ids if sid.startswith("fs-id")} - pilot_ids), 61)
        scope = text(self.root.find("header"))
        for phrase in ("अद्वितीय स्रोतभाग शून्य", "पुन्हा भर घालायची नाही", "बदललेला किंवा हटवलेला नाही", "पूर्ण झाल्याचा हा दावा नाही"):
            self.assertIn(phrase, scope)

    def test_06_source_relation_questions_answers_and_complete_glossary(self):
        for locale in MODULE_PINS:
            block = self.sources[(SELECTED_IDS[0], locale)]
            math = [source_math(n) for n in block.iter(M + "math")]
            self.assertEqual(len(math), 4)
            self.assertEqual(pairs(math[0]), RELATION)
            self.assertEqual(pairs(math[1]), RELATION)
            self.assertEqual(set(members(math[2])), {x for x, y in RELATION})
            self.assertEqual(set(members(math[3])), {y for x, y in RELATION})
            meaning = self.sources[(SELECTED_IDS[3], locale)].find(C + "meaning")
            self.assertEqual(meaning.get("id"), "fs-id1167833175475")
            self.assertEqual(compact(source_math(next(meaning.iter(M + "math")))), "(x,y)")
            for phrase in (("any set", "All the x-values", "All the y-values") if locale == "en"
                           else ("sembarang himpunan", "Semua nilai x", "Semua nilai y")):
                self.assertIn(phrase, text(meaning))
        meaning = text(self.ids["fs-id1167833175475"])
        for phrase in ("क्रमित जोड्यांचा कोणताही संच", "सर्व x-मूल्ये मिळून प्रांत", "सर्व y-मूल्ये मिळून मूल्यसंच"):
            self.assertIn(phrase, meaning)
        self.assertEqual(compact(self.checks["glossary-pair"]), "(x,y)")

    def test_07_actual_source_f_and_g_rules_and_six_requested_expressions(self):
        for index, prefix, definition, queries in (
                (1, "f", F_RULE, ("f(3)", "f(−2)", "f(a)")),
                (2, "g", G_RULE, ("g(h²)", "g(x+2)", "g(x)+g(2)"))):
            for locale in MODULE_PINS:
                problem = next(self.sources[(SELECTED_IDS[index], locale)].iter(C + "problem"))
                actual = [source_math(n) for n in problem.iter(M + "math")]
                self.assertEqual(len(actual), 4)
                source_sides = actual[0].split("=")
                self.assertEqual([shape(side) for side in source_sides], [shape(side) for side in definition.split("=")])
                self.assertEqual([shape(q) for q in actual[1:]], [shape(q) for q in queries])
            self.assertEqual(compact(self.checks[prefix + "-question-formula"]), compact(definition))
            for part, query in zip("abc", queries):
                self.assertEqual(shape(self.checks[prefix + "-question-" + part]), shape(query))

    def test_08_six_tables_all_26_rows_and_every_media_in_original_row(self):
        self.assertEqual([(n.get("id"), len(n.findall("tbody/tr"))) for n in self.root.iter("table")], list(TABLES))
        for locale in MODULE_PINS:
            sources = {n.get("id"): n for sid in SELECTED_IDS for n in self.sources[(sid, locale)].iter(C + "table")}
            self.assertEqual(tuple(sources), tuple(sid for sid, count in TABLES))
            for sid, count in TABLES:
                target = self.ids[sid]
                self.assertEqual(target.get("data-kind"), "adaptation")
                self.assertEqual(target.find("caption").get("data-kind"), "original")
                self.assertEqual(target.find("thead").get("data-kind"), "original")
                rows = list(sources[sid].iter(C + "row"))
                self.assertEqual(len(rows), count)
                for source_row, target_row in zip(rows, target.findall("tbody/tr")):
                    media = [n.get("id") for n in source_row.iter(C + "media")]
                    preserved = [n.get("id") for n in target_row.iter() if n.get("id")]
                    self.assertEqual(preserved, media)
                    self.assertEqual(len(target_row), 2)
                    # Source's intervening cells are empty spacers, not lost prose.
                    for spacer in list(source_row)[1:-1]:
                        self.assertFalse(text(spacer))
                        self.assertFalse(list(spacer.iter(C + "media")))

    def test_09_every_translated_table_row_instruction(self):
        for (sid, count), expected in zip(TABLES, ROW_PROSE):
            actual = tuple(text(row[0]) for row in self.ids[sid].findall("tbody/tr"))
            self.assertEqual(actual, expected)
        for locale in MODULE_PINS:
            tables = [n for sid in SELECTED_IDS for n in self.sources[(sid, locale)].iter(C + "table")]
            for table, expected in zip(tables, ROW_PROSE):
                for source_row, translated in zip(table.iter(C + "row"), expected):
                    source_first = source_row[0]
                    has_instruction = bool(text(source_first)) or bool(list(source_first.iter(C + "media")))
                    self.assertEqual(bool(translated), has_instruction)
                    if text(source_first) in ("Simplify.", "Sederhanakan."):
                        self.assertEqual(translated, "सोपी करा.")

    def test_10_all_26_literal_equation_raster_transcriptions(self):
        self.assertEqual(len(PIXEL_FORMULAS), 26)
        self.assertEqual({key.removeprefix("raster-") for key in self.checks if key.startswith("raster-")}, set(PIXEL_FORMULAS))
        media = [n for sid in SELECTED_IDS for n in self.sources[(sid, "en")].iter(C + "media")]
        self.assertEqual(len(media), 28)
        for source in media:
            short = short_name(source)
            if short not in PIXEL_FORMULAS:
                self.assertIn(short, ("016a", "020a"))
                continue
            target = self.ids[source.get("id")]
            nodes = [n for n in target.iter() if n.get("data-check") == "raster-" + short]
            self.assertEqual(len(nodes), 1)
            self.assertEqual(compact(text(nodes[0])), compact(PIXEL_FORMULAS[short]))
        self.assertFalse(list(self.root.iter("img")))

    def test_11_two_prose_rasters_and_020e_underbrace_meanings(self):
        self.assertEqual(text(self.ids["fs-id1171792372816"]), ROW_PROSE[1][1])
        self.assertEqual(text(self.ids["fs-id1167836693279"]), ROW_PROSE[5][3])
        annotations = {"annotation-020e-first": "3x−5", "annotation-020e-gx": "g(x)",
                       "annotation-020e-second": "1", "annotation-020e-g2": "g(2)"}
        node = self.ids["fs-id1167836322927"]
        self.assertEqual({n.get("data-check") for n in node.iter() if n.get("data-check")}, set(annotations) | {"raster-020e"})
        for key, expected in annotations.items():
            self.assertEqual(compact(self.checks[key]), compact(expected))
        self.assertEqual(evaluate(self.checks["annotation-020e-first"], G_RULE), evaluate(self.checks["annotation-020e-gx"], G_RULE))
        self.assertEqual(evaluate(self.checks["annotation-020e-second"], G_RULE), evaluate(self.checks["annotation-020e-g2"], G_RULE))
        self.assertIn("खालच्या कंसांची खूण", text(node))
        self.assertEqual(text(node).count("मधून"), 2)

    def test_12_all_30_displayed_equalities_hold_exactly(self):
        equations = {key: value for key, value in self.checks.items() if "=" in value}
        self.assertEqual(len(equations), 30)
        for key, equation in equations.items():
            with self.subTest(key=key):
                self.assertTrue(equality(equation, F_RULE if equation.startswith("f(") else G_RULE))

    def test_13_six_requested_values_use_exact_numeric_or_polynomial_results(self):
        for key, definition, expected in (
                ("f-question-a", F_RULE, {(): F(26)}), ("f-question-b", F_RULE, {(): F(1)}),
                ("f-question-c", F_RULE, {("a", "a"): F(2), ("a",): F(3), (): F(-1)}),
                ("g-question-a", G_RULE, {("h", "h"): F(3), (): F(-5)}),
                ("g-question-b", G_RULE, {("x",): F(3), (): F(1)}),
                ("g-question-c", G_RULE, {("x",): F(3), (): F(-4)})):
            self.assertEqual(evaluate(self.checks[key], definition), expected)
        # In particular, (-2)^2 is +4, not -4, and the source result is 1.
        self.assertEqual(evaluate("(−2)²"), {(): F(4)})
        self.assertNotEqual(evaluate("(−2)²"), evaluate("−2²"))

    def test_14_finite_relation_projections_do_not_extend_the_given_set(self):
        self.assertEqual(pairs(self.checks["relation-question"]), RELATION)
        self.assertEqual(pairs(self.checks["relation-solution"]), RELATION)
        for key, coordinate in (("relation-domain", 0), ("relation-range", 1)):
            values = members(self.checks[key])
            self.assertEqual(len(values), len(set(values)))
            self.assertEqual(set(values), {pair[coordinate] for pair in RELATION})
        self.assertNotIn((F(6), F(36)), pairs(self.checks["relation-question"]))
        aside = next(n for n in self.root.findall("aside") if n.get("data-kind") == "original")
        self.assertIn("पाच क्रमित जोड्याच", text(aside))
        self.assertIn("गृहीत धरू नका", text(aside))
        self.assertIn("सर्व x-मूल्यांचा संच", text(self.ids["fs-id1167829691118"]))
        self.assertIn("सर्व y-मूल्यांचा संच", text(self.ids["fs-id1167829593929"]))

    def test_15_final_comparison_has_constant_nonzero_difference_not_sample_proof(self):
        for locale in MODULE_PINS:
            paragraph = next(n for n in self.sources[(SELECTED_IDS[2], locale)].iter() if n.get("id") == "fs-id1167832981642")
            values = [source_math(n) for n in paragraph.iter(M + "math")]
            self.assertEqual(len(values), 3)
            for value in values[:2]:
                self.assertTrue(equality(value, G_RULE))
            self.assertEqual(compact(values[2]), compact("g(x+2)≠g(x)+g(2)"))
        left, right = self.checks["g-final-inequality"].split("≠")
        self.assertEqual(shape(left), shape("g(x+2)"))
        self.assertEqual(shape(right), shape("g(x)+g(2)"))
        # The exact polynomial difference is the constant 5 for every real x.
        self.assertEqual(evaluate("(" + left + ")-(" + right + ")", G_RULE), {(): F(5)})
        note = text(self.ids[SELECTED_IDS[2]].find("aside"))
        self.assertIn("या दिलेल्या g फलनासाठी", note)
        self.assertIn("प्रत्येक फलनाचा सार्वत्रिक नियम नाही", note)

    def test_16_variant_disclosures_and_repeated_steps_remain_visible(self):
        note = text(self.ids[SELECTED_IDS[1]].find("aside"))
        for phrase in ("स्रोत-आवृत्तीची नोंद", "इंग्रजी", "इंडोनेशियन", "मधली पायरी", "स्वतंत्रपणे जतन"):
            self.assertIn(phrase, note)
        self.assertNotEqual(compact(self.checks["raster-017b"]), compact(self.checks["raster-017c"]))
        self.assertEqual(self.checks["raster-018b"], self.checks["raster-018c"])
        source_table = next(n for n in self.sources[(SELECTED_IDS[2], "en")].iter(C + "table") if n.get("id") == TABLES[3][0])
        self.assertIn("Simplify.", source_table.get("aria-label"))
        self.assertFalse(text(list(source_table.iter(C + "row"))[-1][0]))
        note = text(self.ids["fs-id1167836754871"].find("p[@data-kind='original']"))
        for phrase in ("वर्णनात", "सोपी करा", "रंग", "स्वतंत्र"):
            self.assertIn(phrase, note)
        self.assertEqual(self.checks["raster-020e"], self.checks["raster-020f"])

    def test_17_three_supplied_solutions_with_original_two_way_anchor_pairs(self):
        count = 0
        for sid in SELECTED_IDS:
            for exercise in self.sources[(sid, "en")].iter(C + "exercise"):
                count += 1
                problem, solution = exercise.find(C + "problem"), exercise.find(C + "solution")
                self.assertIsNotNone(solution)
                target = self.ids[exercise.get("id")]
                self.assertEqual([n.get("id") for n in target], [problem.get("id"), solution.get("id")])
                for start, end, kind in ((problem, solution, "problem"), (solution, problem, "solution")):
                    node = self.ids[start.get("id")]
                    self.assertIn(kind, node.get("class", "").split())
                    self.assertNotEqual(node.get("data-kind"), "original")
                    self.assertIn("#" + end.get("id"), [a.get("href") for a in node.iter("a") if text(a)])
                self.assertTrue(text(self.ids[solution.get("id")].find("h3")).startswith("स्रोतातील"))
        self.assertEqual(count, 3)
        self.assertEqual(sum("solution" in n.get("class", "").split() for n in self.root.iter()), 3)
        links = list(self.root.iter("a"))
        internal = [a for a in links if a.get("href", "").startswith("#")]
        self.assertEqual(len(internal), 11)
        self.assertEqual(len(links) - len(internal), 3)
        for a in internal:
            self.assertIn(a.get("href")[1:], self.ids)
            self.assertTrue(text(a))
        for locale in MODULE_PINS:
            self.assertFalse([n for sid in SELECTED_IDS for n in self.sources[(sid, locale)].iter(C + "link")])

    def test_18_all_56_original_image_members_and_review_copies_are_pinned(self):
        records = self.lock["source_images"]
        self.assertEqual(len(records), 56)
        inventory = sorted(f"{r['locale']}|{r['member'].split('/')[-1]}|{r['sha256']}|{r['bytes']}" for r in records)
        self.assertEqual(sha(("\n".join(inventory) + "\n").encode("utf-8")), IMAGE_INVENTORY_SHA256)
        indexed = {(r["locale"], r["member"].split("/")[-1]): r for r in records}
        self.assertEqual(len(indexed), 56)
        totals = {}
        for locale, (archive, module_member, module_digest, archive_digest) in MODULE_PINS.items():
            selected_media = [(sid, n) for sid in SELECTED_IDS for n in self.sources[(sid, locale)].iter(C + "media")]
            self.assertEqual(len(selected_media), 28)
            total = 0
            with zipfile.ZipFile(BASE.parent / "downloads/mr-Deva-IN/releases" / archive) as handle:
                for sid, media in selected_media:
                    name = image_name(short_name(media))
                    record = indexed[(locale, name)]
                    member = module_member.split("/modules/")[0] + "/media/" + name
                    self.assertEqual(record["member"], member)
                    self.assertEqual(record["archive"], "downloads/mr-Deva-IN/releases/" + archive)
                    self.assertEqual(record["archive_sha256"], archive_digest)
                    self.assertEqual(record["locator"], "A20:m81373#" + sid)
                    self.assertNotIn("committed_asset", record)
                    raw = handle.read(member)
                    self.assertTrue(raw.startswith(b"\xff\xd8\xff"))
                    self.assertEqual(sha(raw), record["sha256"])
                    self.assertEqual(len(raw), record["bytes"])
                    review = f"downloads/mr-Deva-IN/source-image-qa/{UNIT}/{locale}-{name}"
                    self.assertEqual(record["review_copy"], review)
                    self.assertEqual((BASE.parent / review).read_bytes(), raw)
                    total += len(raw)
            totals[locale] = total
        self.assertEqual(totals, {"en": 752063, "id": 2899820})

    def test_19_arithmetic_helpers_fail_closed_and_detect_material_mutations(self):
        for malformed in ("{(1,1)}junk", "{(1,1),(2,4),}", "{(1,1.5)}", "__import__('os')"):
            with self.assertRaises(ValueError):
                pairs(malformed)
        for malformed in ("{1,2}junk", "{1,2,}", "{1,2+3}"):
            with self.assertRaises(ValueError):
                members(malformed)
        for malformed in ("__import__('os')", "x.attr", "[x]", "f(1,2)", "unknown(1)"):
            with self.assertRaises(ValueError):
                evaluate(malformed, F_RULE)
        self.assertFalse(equality("f(−2)=−15", F_RULE))
        self.assertFalse(equality("f(3)=25", F_RULE))
        self.assertFalse(equality("g(x+2)=3x−4", G_RULE))
        self.assertFalse(equality("g(h²)=3h−5", G_RULE))
        # A universal-looking identity cannot pass just because x=0 was sampled.
        self.assertFalse(equality("g(x)+g(2)=3x²−4", G_RULE))


if __name__ == "__main__":
    unittest.main(verbosity=2)
