"""Independent real-source mathematics/pixel regressions for MR-BRIDGE-012.

The reviewer did not draft this unit. No eval, downloads, extraction, writes,
builds, or browser/HTML inspection. Run with python -B and the pinned archives
and existing review copies available. Pixel observations are manually read and
hash-bound; they are not automated recognition or reader visual acceptance.
"""
from fractions import Fraction as F
import hashlib
from math import isqrt
from pathlib import Path
import re
import unicodedata
import unittest
import xml.etree.ElementTree as ET
import zipfile

from test_unit6_math import evaluate, read_json


BASE = Path(__file__).resolve().parents[1]
UNIT = "MR-BRIDGE-012"
C = "{http://cnx.rice.edu/cnxml}"
D = "{http://cnx.rice.edu/mdml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SECTION = "fs-id1167836579284"
NEXT_SECTION = "fs-id1167836522816"
SELECTED_IDS = (
    "para-00001", "list-00001", "fs-id1167826157468", "fs-idm664502240", "fs-idm263727344",
    "fs-id1167829579930", "fs-id1167836691995", "fs-id1167829924871", "fs-id1167836625879",
    "CNX_IntAlg_Figure_03_06_001", "fs-id1167836547061", "fs-id1167829717392", "fs-id1167836600350",
    "fs-id1167836293137", "fs-id1167833386905", "fs-id1167836731467", "fs-id1167836289482", "fs-id1167836537878",
)
MODULE_PINS = {
    "en": ("A20-canonical.zip", "osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9",
           "021c29fa9a6ab3d5b06d2ef143a82d2ac818ed25fe6fd44ebf5d7a6be07a123a"),
    "id": ("A20-v0.3.0-source.zip", "source", "d89a74aef766afca6a4ac7e1ae720f120d22cc771c11dd7e025c55bca1fabb8e"),
}
# Sorted lines target_id|locale|fragment_sha256, UTF-8 with final LF. This
# independent pin binds all 36 individually checked fragment hashes.
FRAGMENT_INVENTORY = "0dcf0a4c8aafa871a4af37ce29b77f9f3a206951928f4b165a09783eb75154da"
TARGET_PINS = {
    "translations/MR-BRIDGE-012.xml": "1883fddbb24d1d3518e6d34ebdec38c608ebcee78872af069dc7030f6920402b",
    "units/MR-BRIDGE-012.json": "cb9c08d87b32ca61cfc2a59b3638700197666c3375a91a343e51c32516263454",
}
IMAGE_PINS = (
    ("fs-id1167836424063", 120547, "de8ad8b7a7c2fed56a79b196866575e70a0e54b2ca70520342ce9081d92e3467"),
    ("fs-id1167836552272", 91065, "50b51fdbccf8bbcc32fd4ce26bc0b255ae76e365026d772980f115506bf3486b"),
    ("fs-id1167836557713", 84283, "109cdaa78c4bd812e17c70f304673faf5f36590ad133afc956c859f3f586eda8"),
    ("fs-id1167833339591", 66942, "e0ec3c2945b43a91e675c6631f14c076dc7cac0c4927c14e1372414e5cd09b99"),
    ("fs-id1167836728309", 91655, "9ccbba7c423566ea6c7a5ded367b840b81f3f799ba4634610d5d7a1910b1794e"),
    ("fs-id1167836299681", 72667, "af4e418454ff1d2ce11c63566bba63c562db3e81fe6145b1af2d52af83d2660e"),
)
TABLE_POINTS = ((-2, -7), (-1, -5), (0, -3), (3, 3), (4, 5))
DESCENDING_LINE = ((0, 2), (3, 0), (6, -2))
SIDEWAYS_PARABOLA = ((-1, 0), (0, 1), (0, -1), (3, 2), (3, -2))
UPWARD_PARABOLA = ((0, -1), (-1, 0), (1, 0), (-2, 3), (2, 3))
CIRCLE = ((-2, 0), (2, 0), (0, -2), (0, 2))
ELLIPSE = ((0, -3), (-2, 0), (2, 0), (0, 3))
ASCENDING_LINE = ((0, -2), (2, 0), (4, 2))
ALT_POINTS = (
    ((0, -3), (1, -1), (2, 1)) + TABLE_POINTS,
    DESCENDING_LINE + SIDEWAYS_PARABOLA, DESCENDING_LINE, SIDEWAYS_PARABOLA,
    UPWARD_PARABOLA + CIRCLE, ELLIPSE + ASCENDING_LINE,
)
BACKREFS = (
    ("m81422", "fs-id1167829586631", "1-1-use-the-language-of-algebra", "772b200d-b3d4-4654-bc37-a1d3fb70efd7",
     ("16beaa33746959c3561c4b6c6f3390f736f4cf2f9da837c1777ef2b3a53c6bed", "bba2e724579e7d586a426c37344947c3ca79205bbf5de771f2df8120a26aa8c4")),
    ("m81423", "fs-id1167835365552", "1-2-integers", "59ccdc10-4ea2-46d9-b94c-10312203255e",
     ("bc82f81bbf9f751fac83ff1acce7464fbacad342bbaf642649509a62ffec8428", "4be95316787f366809ce9f8f2ccd1c307f5ad5dbff4b8c7d87a7d60598e736a2")),
    ("m81425", "fs-id1167833056590", "1-4-decimals", "a140725d-a6e3-4705-8430-b4f350efb27f",
     ("342336ae6607762b8b6e6fd1e3b237a7a5822adb56f0d6eb44880f83000d7f5e", "5535b7a4f397ff261689ed99f3b1829b104e0f0e15bc1f2ef3995fe6b64f8760")),
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


def filename(index):
    return f"CNX_IntAlg_Figure_03_06_{index:03d}_img_new.jpg"


def signature(node):
    norm = lambda value: " ".join((value or "").split())
    return (node.tag, sorted(node.attrib.items()), norm(node.text),
            [(signature(child), norm(child.tail)) for child in node])


def source_math(node):
    tag = node.tag.removeprefix(M)
    if tag in ("math", "mrow"):
        return "".join(source_math(child) for child in node).rstrip(",.")
    if tag in ("mi", "mn", "mo", "mtext"):
        return text(node)
    if tag == "msup" and len(node) == 2:
        return "(" + source_math(node[0]) + ")**(" + source_math(node[1]) + ")"
    if tag == "msqrt" and len(node) == 1:
        return "√(" + source_math(node[0]) + ")"
    raise ValueError("unsupported source MathML: " + tag)


def numeric_value(display):
    """Exact nonnegative perfect-square root, otherwise narrow Fraction AST."""
    value = compact(display)
    root = re.fullmatch(r"([+-]?)√(?:\((\d+)\)|(\d+))", value)
    if root:
        radicand = int(root[2] if root[2] is not None else root[3])
        result = isqrt(radicand)
        if result * result != radicand:
            raise ValueError("this bounded test supports exact square roots only")
        return F(-result if root[1] == "-" else result)
    result = evaluate(display)
    if set(result) - {()}:
        raise ValueError("expected a numeric value")
    return result.get((), F(0))


def coordinates(display):
    value = display.replace("negative ", "-").replace("negatif ", "-").replace("−", "-")
    return tuple((F(x), F(y)) for x, y in re.findall(r"\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)", value))


def one_pair(display):
    if not re.fullmatch(r"\(-?\d+,-?\d+\)", compact(display)):
        raise ValueError("expected exactly one integer coordinate pair")
    return coordinates(display)[0]


def linear_coefficients(points):
    """Given a source-declared straight line, two distinct x determine m,b."""
    (x1, y1), (x2, y2) = points[:2]
    if x1 == x2:
        raise ValueError("not a nonvertical-line witness")
    slope = F(y2 - y1, x2 - x1)
    intercept = F(y1) - slope * x1
    if any(F(y) != slope * x + intercept for x, y in points):
        raise ValueError("source line coordinates disagree")
    return slope, intercept


class Unit12IndependentTests(unittest.TestCase):
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
                    raise ValueError("duplicate data-check")
                cls.checks[node.get("data-check")] = text(node)
        records = [(s["target_id"], x) for s in cls.lock["source_selections"] for x in s["sources"]]
        lines = sorted(f"{sid}|{x['locale']}|{x['fragment_sha256']}" for sid, x in records)
        if sha(("\n".join(lines) + "\n").encode()) != FRAGMENT_INVENTORY:
            raise ValueError("independently reviewed source inventory changed")
        cls.sources = {}
        for sid, source in records:
            raw = local_path(source["fragment_path"]).read_bytes()
            if sha(raw) != source["fragment_sha256"]:
                raise ValueError("fragment pin drift")
            key = sid, source["locale"]
            if key in cls.sources:
                raise ValueError("duplicate source fragment")
            cls.sources[key] = ET.fromstring(raw)

    def test_01_all_36_frozen_fragments_and_51_witnesses_match(self):
        self.assertEqual(self.lock["unit"], UNIT)
        self.assertEqual(self.lock["locale"], "mr-Deva-IN")
        self.assertEqual([s["target_id"] for s in self.lock["source_selections"]], list(SELECTED_IDS))
        self.assertEqual(set(self.sources), {(sid, lang) for sid in SELECTED_IDS for lang in MODULE_PINS})
        witnesses = {(w["path"], w["sha256"]) for w in self.lock["witnesses"]}
        self.assertEqual(len(witnesses), 51)
        self.assertEqual(len(self.lock["witnesses"]), 51)
        for path, digest in witnesses:
            self.assertEqual(sha(local_path(path).read_bytes()), digest, path)
        for selection in self.lock["source_selections"]:
            self.assertEqual(selection["locator"], "A20:m81374#" + selection["target_id"])
            for source in selection["sources"]:
                self.assertEqual(source["module_sha256"], MODULE_PINS[source["locale"]][2])
                self.assertIn((source["fragment_path"], source["fragment_sha256"]), witnesses)

    def test_02_actual_module_metadata_complete_first_section_and_next_marker(self):
        for locale, (archive, prefix, digest) in MODULE_PINS.items():
            with zipfile.ZipFile(BASE.parent / "downloads/mr-Deva-IN/releases" / archive) as handle:
                raw = handle.read(prefix + "/modules/m81374/index.cnxml")
            self.assertEqual(sha(raw), digest)
            module = ET.fromstring(raw)
            metadata = module.find(C + "metadata")
            self.assertEqual(metadata.find(D + "content-id").text, "m81374")
            self.assertEqual(metadata.find(D + "uuid").text, "4b2bbf1b-2df7-4b9a-9933-dd70d1fd8ada")
            abstract = metadata.find(D + "abstract")
            self.assertEqual([n.get("id") for n in abstract], list(SELECTED_IDS[:2]))
            content = list(module.find(C + "content"))
            self.assertEqual([n.get("id") for n in content[:5]], list(SELECTED_IDS[2:5]) + [SECTION, NEXT_SECTION])
            self.assertEqual([n.get("id") for n in content[3] if n.tag != C + "title"], list(SELECTED_IDS[5:]))
            self.assertEqual(text(content[3].find(C + "title")), "Use the Vertical Line Test" if locale == "en" else "Menggunakan Uji Garis Vertikal")
            source_index = {n.get("id"): n for n in module.iter() if n.get("id")}
            for sid in SELECTED_IDS:
                self.assertEqual(signature(source_index[sid]), signature(self.sources[(sid, locale)]))
            self.assertNotIn(NEXT_SECTION, self.ids)

    def test_03_57_selected_ids_plus_wrapper_preserve_order_and_ancestry(self):
        self.assertEqual(len(self.ids), 61)
        for locale in MODULE_PINS:
            expected = [n.get("id") for sid in SELECTED_IDS for n in self.sources[(sid, locale)].iter() if n.get("id")]
            self.assertEqual(len(expected), 57)
            self.assertEqual(len(set(expected)), 57)
            actual = [n.get("id") for n in self.root.iter() if n.get("id") in set(expected)]
            self.assertEqual(actual, expected)
            self.assertEqual(set(self.ids) - set(expected), {UNIT, "readiness", SECTION, "credits"})
            for sid in SELECTED_IDS:
                for source in self.sources[(sid, locale)].iter():
                    if source.get("id"):
                        nested = [n.get("id") for n in source.iter() if n.get("id")]
                        self.assertEqual([n.get("id") for n in self.ids[source.get("id")].iter() if n.get("id") in set(expected)], nested)
            section_ids = [n.get("id") for sid in SELECTED_IDS[5:] for n in self.sources[(sid, locale)].iter() if n.get("id")]
            self.assertEqual([n.get("id") for n in self.ids[SECTION].iter() if n.get("id")], [SECTION] + section_ids)
        self.assertIsNone(self.ids[SECTION].get("data-source"))
        self.assertEqual([n.get("data-source") for n in self.root.iter() if n.get("data-source")], ["A20:m81374#" + sid for sid in SELECTED_IDS])

    def test_04_current_reviewed_bytes_locale_counts_and_38_math_strings(self):
        for path, digest in TARGET_PINS.items():
            self.assertEqual(sha((BASE / path).read_bytes()), digest)
        self.assertEqual(self.root.get("id"), UNIT)
        self.assertEqual(self.root.get("lang"), "mr-Deva-IN")
        decoded = self.raw.decode("utf-8")
        self.assertEqual(unicodedata.normalize("NFC", decoded), decoded)
        self.assertNotIn("\ufffd", decoded)
        self.assertEqual(self.checks, self.config["expected_math"])
        self.assertEqual(len(self.checks), 38)
        for key, count in (("source_count", 18), ("translated_worked_examples", 1), ("translated_definitions", 1),
                           ("translated_practice_items", 5), ("translated_resource_notes", 0), ("original_practice_items", 0)):
            self.assertEqual(self.config[key], count)
        self.assertEqual(self.config["question_ids"], [])
        for term in self.config["required_terms"]:
            self.assertIn(term, text(self.root))

    def test_05_all_three_objectives_and_limited_scope_survive(self):
        expected = ("उभ्या रेषेची कसोटी वापरणे.", "मूलभूत फलनांचे आलेख ओळखणे.", "फलनाच्या आलेखातून माहिती वाचणे.")
        self.assertEqual(tuple(text(n) for n in self.ids["list-00001"].iter("li")), expected)
        for locale in MODULE_PINS:
            self.assertEqual(len(list(self.sources[("list-00001", locale)].iter(C + "item"))), 3)
        self.assertIn("पहिल्या उद्दिष्टाचा", text(self.root.find("header")))
        self.assertIn("पूर्ण झाल्याचा हा दावा नाही", text(self.root.find("header")))
        self.assertIn("Identify Graphs of Basic Functions", text(self.ids["credits"]))
        current = {"A20:m81374#" + sid for sid in SELECTED_IDS}
        prior = set()
        for index in range(1, 12):
            root = ET.parse(BASE / f"translations/MR-BRIDGE-{index:03d}.xml").getroot()
            prior.update(n.get("data-source") for n in root.iter() if n.get("data-source"))
        self.assertFalse(current & prior)

    def test_06_all_six_actual_source_readiness_questions_and_supplied_answers(self):
        expected_questions = (("2³", "3²"), ("|7|", "|−3|"), ("√4", "√16"))
        expected_answers = ((8, 9), (7, 3), (2, 4))
        for index, sid in enumerate(SELECTED_IDS[2:5], 1):
            for locale in MODULE_PINS:
                source = self.sources[(sid, locale)]
                problem = next(source.iter(C + "problem"))
                solution = next(source.iter(C + "solution"))
                questions = [source_math(n) for n in problem.iter(M + "math")]
                answers = [source_math(n) for n in solution.iter(M + "math")]
                self.assertEqual(len(questions), 2)
                self.assertEqual(len(answers), 2)
                self.assertEqual(tuple(map(numeric_value, questions)), tuple(map(F, expected_answers[index - 1])))
                self.assertEqual(tuple(map(numeric_value, answers)), tuple(map(F, expected_answers[index - 1])))
            for part, query, answer in zip("ab", expected_questions[index - 1], expected_answers[index - 1]):
                self.assertEqual(compact(self.checks[f"ready{index}-{part}"]), compact(query))
                self.assertEqual(numeric_value(self.checks[f"ready{index}-{part}"]), F(answer))
                self.assertEqual(numeric_value(self.checks[f"ready{index}-answer-{part}"]), F(answer))

    def test_07_all_added_numeric_working_and_principal_root_convention(self):
        keys = [key for key in self.checks if key.startswith("ready") and ("working" in key or "square" in key)]
        self.assertEqual(len(keys), 8)
        for key in keys:
            values = [numeric_value(side) for side in self.checks[key].split("=")]
            self.assertGreaterEqual(len(values), 2)
            self.assertTrue(all(value == values[0] for value in values), key)
        square_note = text(self.ids["fs-idm214674176"])
        self.assertIn("शून्य किंवा धन वर्गमूळ", square_note)
        self.assertIn("± अशी दोन मूल्ये लिहायची नाहीत", square_note)
        abs_note = text(self.ids["fs-idm260165584"])
        for phrase in ("केवल मूल्य", "0 पासूनचे अंतर", "अंतर ऋण नसते"):
            self.assertIn(phrase, abs_note)
        for index, sid in enumerate(SELECTED_IDS[2:5], 1):
            self.assertTrue([n for n in self.ids[sid].iter() if n.get("data-kind") == "original" and "जोडले" in text(n)])

    def test_08_original_line_equation_and_exact_five_row_table(self):
        self.assertEqual(compact(self.checks["ordered-pair"]), "(x,y)")
        for locale in MODULE_PINS:
            pair = next(self.sources[("fs-id1167836691995", locale)].iter(M + "math"))
            self.assertEqual(compact(source_math(pair)), "(x,y)")
        for key in ("line-rule-intro", "line-table-rule", "line-rule-function"):
            self.assertEqual(compact(self.checks[key]), "y=2x-3")
        for sid in ("fs-id1167836625879", "fs-id1167836547061"):
            for locale in MODULE_PINS:
                formula = source_math(next(self.sources[(sid, locale)].iter(M + "math")))
                self.assertEqual(compact(formula), "y=2x-3")
        table = self.ids["CNX_IntAlg_Figure_03_06_001"].find("div/table")
        self.assertEqual([text(n) for n in table.findall("thead/tr/th")], ["x", "y", "(x, y)"])
        rows = table.findall("tbody/tr")
        self.assertEqual(len(rows), 5)
        for index, (row, expected) in enumerate(zip(rows, TABLE_POINTS), 1):
            self.assertEqual(len(row), 3)
            x, y = (numeric_value(text(cell)) for cell in row[:2])
            self.assertEqual((x, y), expected)
            self.assertEqual(one_pair(text(row[2])), expected)
            self.assertEqual(one_pair(self.checks[f"table-pair{index}"]), expected)
            self.assertEqual(y, 2 * x - 3)
        note = text(self.ids["CNX_IntAlg_Figure_03_06_001"].find("div"))
        self.assertIn("फक्त या पाच बिंदूंपुरता मर्यादित नाही", note)
        self.assertIn("पूर्ण प्रांत", note)

    def test_09_every_alt_coordinate_matches_pinned_pixel_reading(self):
        for index, ((media_id, size, digest), expected) in enumerate(zip(IMAGE_PINS, ALT_POINTS), 1):
            image = self.ids[media_id].find("img")
            self.assertEqual(image.get("src"), "asset:" + filename(index))
            self.assertEqual(coordinates(image.get("alt")), expected)
            for locale in MODULE_PINS:
                source = next(n for sid in SELECTED_IDS for n in self.sources[(sid, locale)].iter(C + "media") if n.get("id") == media_id)
                self.assertEqual(set(coordinates(source.get("alt"))), set(expected))
        self.assertIn("−10 ते 10", self.ids[IMAGE_PINS[0][0]].find("img").get("alt"))
        for index in (1, 2, 3, 5):
            self.assertIn("−6 ते 6", self.ids[IMAGE_PINS[index][0]].find("img").get("alt"))
        self.assertIn("−2 ते 10", self.ids[IMAGE_PINS[4][0]].find("img").get("alt"))

    def test_10_six_source_graph_judgments_and_complete_worked_prose(self):
        for sid, expected in (("fs-id1167829879758", (True, False)), ("fs-id1167829693572", (False, True))):
            self.assertEqual(tuple(value == "होय" for value in re.findall(r"\([ab]\)\s*(होय|नाही)", text(self.ids[sid]))), expected)
            for locale in MODULE_PINS:
                paragraph = next(n for selected_id in SELECTED_IDS
                                 for n in self.sources[(selected_id, locale)].iter() if n.get("id") == sid)
                words = re.findall(r"\b(?:yes|no|ya|tidak)\b", text(paragraph))
                self.assertEqual(tuple(word in ("yes", "ya") for word in words), expected)
        worked = self.ids["fs-id1167836542012"]
        paragraphs = worked.findall("p")
        self.assertEqual(len(paragraphs), 2)
        self.assertIn("कोणतीही उभी रेषा", text(paragraphs[0]))
        self.assertIn("जास्तीत जास्त एका", text(paragraphs[0]))
        self.assertIn("फलनाचा आलेख आहे", text(paragraphs[0]))
        self.assertIn("दोन बिंदूंमध्ये", text(paragraphs[1]))
        self.assertIn("फलन दर्शवत नाही", text(paragraphs[1]))
        for locale in MODULE_PINS:
            source = self.sources[("fs-id1167836731467", locale)]
            paragraph = next(n for n in source.iter() if n.get("id") == "fs-id1167836542012")
            self.assertEqual([n.get("id") for n in paragraph.iter(C + "media")], [IMAGE_PINS[2][0], IMAGE_PINS[3][0]])

    def test_11_positive_graph_arguments_are_geometric_not_finite_grid_proofs(self):
        # Source identifies straight lines, not arbitrary curves through samples.
        # Distinct x-coordinates prove nonvertical orientation. Their full line
        # has y=m*x+b, a unique y for each real x, independent of plotted samples.
        self.assertEqual(linear_coefficients(DESCENDING_LINE), (F(-2, 3), F(2)))
        self.assertEqual(linear_coefficients(ASCENDING_LINE), (F(1), F(-2)))
        self.assertEqual(linear_coefficients(TABLE_POINTS), (F(2), F(-3)))
        source_note = text(self.ids["fs-id1167833102413"])
        self.assertIn("निष्कर्ष फक्त दाखवलेल्या तीन तपासण्यांवर अवलंबून नाही", source_note)
        # A vertical-axis upward parabola has form y=a(x-h)^2+k (a>0),
        # hence unique output by its form. We do NOT derive its full curve from
        # five points. The following is only exact consistency of its read points.
        self.assertTrue(all(y == x * x - 1 for x, y in UPWARD_PARABOLA))
        note = text(self.ids["fs-id1167833061214"])
        self.assertIn("वर उघडणाऱ्या", note)
        self.assertIn("कोणतीही उभी रेषा जास्तीत जास्त एका", note)
        self.assertIn("त्यांची x-मूल्ये वेगळी", note)
        self.assertIn("ही सरळ रेषा उभी नाही", text(self.ids["fs-id1167836700357"]))

    def test_12_three_negative_graphs_have_same_input_distinct_output_witnesses(self):
        for prefix, expected_y, observed in (("example", 1, SIDEWAYS_PARABOLA), ("try1", 2, CIRCLE), ("try2", 3, ELLIPSE)):
            up = one_pair(self.checks[prefix + "-counterexample-up"])
            down = one_pair(self.checks[prefix + "-counterexample-down"])
            self.assertEqual(up, (F(0), F(expected_y)))
            self.assertEqual(down, (F(0), F(-expected_y)))
            self.assertIn(up, observed)
            self.assertIn(down, observed)
            self.assertEqual(up[0], down[0])
            self.assertNotEqual(up[1], down[1])
            if prefix != "example":
                self.assertEqual(compact(self.checks[prefix + "-counterexample-line"]), "x=0")

    def test_13_vertical_quantifier_domain_and_orientation_are_not_weakened(self):
        for sid in ("fs-id1167836293137", "fs-id1167836608668"):
            self.assertIn("प्रत्येक उभी रेषा जास्तीत जास्त एका", text(self.ids[sid]))
        self.assertIn("एखादी जरी उभी रेषा", text(self.ids["fs-id1167836608075"]))
        self.assertIn("एकापेक्षा जास्त", text(self.ids["fs-id1167836608075"]))
        for locale in MODULE_PINS:
            definition = self.sources[("fs-id1167833386905", locale)]
            self.assertIn("at most one" if locale == "en" else "paling banyak di satu", text(definition))
        note = text(self.ids[SECTION].find("aside"))
        for phrase in ("y-अक्षाला समांतर", "x-मूल्य एकच", "शून्य किंवा एक", "प्रांत आधीच वेगळा दिला असेल",
                       "त्यातील प्रत्येक x-मूल्यासाठी", "आडव्या रेषेची नाही", "समान y-मूल्य", "काही निवडलेल्या उभ्या रेषा"):
            self.assertIn(phrase, note)

    def test_14_axis_and_dashed_line_source_errors_are_explicitly_corrected(self):
        for locale in MODULE_PINS:
            media = {n.get("id"): n for sid in SELECTED_IDS for n in self.sources[(sid, locale)].iter(C + "media")}
            for index in (1, 2):
                self.assertIn("10", media[IMAGE_PINS[index][0]].get("alt"))
                self.assertNotIn("10", self.ids[IMAGE_PINS[index][0]].find("img").get("alt"))
            self.assertIn("12", media[IMAGE_PINS[5][0]].get("alt"))
            self.assertNotIn("12", self.ids[IMAGE_PINS[5][0]].find("img").get("alt"))
        self.assertEqual(compact(self.checks["example-dashed-line"]), "x=2")
        alt = self.ids[IMAGE_PINS[3][0]].find("img").get("alt")
        for phrase in ("x = −2 रेषेला छेदनबिंदू नाही", "x = −1 रेषेला एक छेदनबिंदू", "x = 2 रेषेला दोन वेगळे"):
            self.assertIn(phrase, alt)
        # A right-opening parabola x=h+a(y-k)^2 (a>0) has 0,1,2
        # intersections as x is below,equal to,above h. The visible vertex h=-1
        # makes these three statements rigorous; no exact sqrt(3) coordinate is
        # invented for the x=2 intersections.
        self.assertLess(F(-2), F(-1))
        self.assertGreater(F(2), F(-1))
        corrections = " ".join(text(n) for n in self.root.iter() if n.get("data-kind") == "original")
        for phrase in ("−10 ते 10", "−12 ते 12", "x = 3", "इंडोनेशियन वर्णनातही 2"):
            self.assertIn(phrase, corrections)

    def test_15_all_six_supplied_answers_keep_original_two_way_ids(self):
        count = 0
        for sid in SELECTED_IDS:
            for exercise in self.sources[(sid, "en")].iter(C + "exercise"):
                count += 1
                problem, solution = exercise.find(C + "problem"), exercise.find(C + "solution")
                self.assertIsNotNone(solution)
                target = self.ids[exercise.get("id")]
                self.assertEqual([n.get("id") for n in target if n.get("id")], [problem.get("id"), solution.get("id")])
                for start, end, kind in ((problem, solution, "problem"), (solution, problem, "solution")):
                    node = self.ids[start.get("id")]
                    self.assertIn(kind, node.get("class", "").split())
                    self.assertNotEqual(node.get("data-kind"), "original")
                    self.assertIn("#" + end.get("id"), [a.get("href") for a in node.iter("a") if text(a)])
                self.assertTrue(text(self.ids[solution.get("id")].find("h4")).startswith("स्रोतातील"))
        self.assertEqual(count, 6)
        self.assertEqual(sum("solution" in n.get("class", "").split() for n in self.root.iter()), 6)

    def test_16_four_source_backreferences_and_disclosed_integer_addition_target(self):
        expected = [(module, sid) for module, sid, route, uuid, pins in BACKREFS] + [(None, "CNX_IntAlg_Figure_03_06_001")]
        for locale in MODULE_PINS:
            source_links = [n for sid in SELECTED_IDS for n in self.sources[(sid, locale)].iter(C + "link")]
            self.assertEqual([(n.get("document"), n.get("target-id")) for n in source_links], expected)
        target_links = [n for n in self.root.iter("a") if n.get("data-source-target-id")]
        self.assertEqual([(n.get("data-source-document"), n.get("data-source-target-id")) for n in target_links], expected)
        self.assertEqual(target_links[-1].get("href"), "#CNX_IntAlg_Figure_03_06_001")
        for locale_index, (locale, (archive, prefix, module_digest)) in enumerate(MODULE_PINS.items()):
            with zipfile.ZipFile(BASE.parent / "downloads/mr-Deva-IN/releases" / archive) as handle:
                for link, (module, sid, route, uuid, pins) in zip(target_links, BACKREFS):
                    self.assertEqual(link.get("href"), "https://openstax.org/books/intermediate-algebra-2e/pages/" + route + "#" + sid)
                    raw = handle.read(prefix + "/modules/" + module + "/index.cnxml")
                    self.assertEqual(sha(raw), pins[locale_index])
                    source = ET.fromstring(raw)
                    self.assertEqual(source.find(C + "metadata").find(D + "uuid").text, uuid)
                    matching = [n for n in source.iter() if n.get("id") == sid]
                    self.assertEqual(len(matching), 1)
                    problem = matching[0].find(".//" + C + "problem")
                    formulas = [source_math(n) for n in problem.iter(M + "math")]
                    if module == "m81423":
                        self.assertEqual([compact(x) for x in formulas], ["-1+(-4)", "-1+5", "1+(-5)"])
                        self.assertEqual([numeric_value(x) for x in formulas], list(map(F, (-5, 4, -4))))
                    elif module == "m81425":
                        self.assertEqual([numeric_value(x) for x in formulas], list(map(F, (5, 11, -12))))
                    else:
                        self.assertEqual(len(formulas), 1)
                        self.assertEqual(numeric_value(formulas[0].replace("[", "(").replace("]", ")")), F(13))
        note = text(self.ids["fs-idm664502240"])
        for phrase in ("पूर्णांकांच्या बेरजेचे उदाहरण", "केवल मूल्याचे नाही", "दुवा शांतपणे बदललेला नाही"):
            self.assertIn(phrase, note)

    def test_17_all_twelve_image_members_and_six_embedded_assets_are_pinned(self):
        images = self.lock["source_images"]
        self.assertEqual(len(images), 12)
        indexed = {(r["locale"], r["member"].split("/")[-1]): r for r in images}
        self.assertEqual(len(indexed), 12)
        self.assertEqual(set(self.config["assets"]), {filename(i) for i in range(1, 7)})
        self.assertEqual(len(list(self.root.iter("img"))), 6)
        witnesses = {(w["path"], w["sha256"]) for w in self.lock["witnesses"]}
        for locale, (archive, prefix, module_digest) in MODULE_PINS.items():
            total = 0
            with zipfile.ZipFile(BASE.parent / "downloads/mr-Deva-IN/releases" / archive) as handle:
                for index, (media_id, size, digest) in enumerate(IMAGE_PINS, 1):
                    name = filename(index)
                    record = indexed[(locale, name)]
                    self.assertEqual(record["member"], prefix + "/media/" + name)
                    self.assertEqual(record["sha256"], digest)
                    self.assertEqual(record["bytes"], size)
                    raw = handle.read(record["member"])
                    self.assertEqual(sha(raw), digest)
                    self.assertEqual(len(raw), size)
                    self.assertTrue(raw.startswith(b"\xff\xd8\xff"))
                    review = f"downloads/mr-Deva-IN/source-image-qa/{UNIT}/{locale}-{name}"
                    self.assertEqual(record["review_copy"], review)
                    self.assertEqual((BASE.parent / review).read_bytes(), raw)
                    source_sid = next(sid for sid in SELECTED_IDS if any(n.get("id") == media_id for n in self.sources[(sid, locale)].iter()))
                    self.assertEqual(record["locator"], "A20:m81374#" + source_sid)
                    if locale == "en":
                        asset = self.config["assets"][name]
                        self.assertEqual(asset["path"], f"assets/{UNIT}/{name}")
                        self.assertEqual(asset["sha256"], digest)
                        self.assertEqual(asset["mime"], "image/jpeg")
                        self.assertEqual(record["committed_asset"], asset["path"])
                        self.assertIn((asset["path"], digest), witnesses)
                        self.assertEqual(local_path(asset["path"]).read_bytes(), raw)
                    total += size
            self.assertEqual(total, 527159)

    def test_18_offline_link_targets_attribution_and_explicit_limits(self):
        internal = [a for a in self.root.iter("a") if a.get("href", "").startswith("#")]
        external = [a for a in self.root.iter("a") if a.get("href", "").startswith("https://")]
        self.assertEqual(len(internal), 18)
        self.assertEqual(len(external), 8)
        for a in internal:
            self.assertIn(a.get("href")[1:], self.ids)
            self.assertTrue(text(a))
        self.assertFalse(list(self.root.iter("script")))
        self.assertIn("https://creativecommons.org/licenses/by-nc-sa/4.0/", [a.get("href") for a in external])
        self.assertNotIn("https://creativecommons.org/licenses/by/4.0/", [a.get("href") for a in external])
        credits = text(self.ids["credits"])
        for phrase in ("संपूर्ण संज्ञा या संदर्भांत सापडल्याचा दावा नाही", "मानवी मराठी गणित-शिक्षकाचे पुनरावलोकन झालेले नाही", "स्थानिक वाचक-दुवे अद्याप नाहीत"):
            self.assertIn(phrase, credits)

    def test_19_exact_helpers_reject_unsupported_or_wrong_inputs(self):
        self.assertEqual(numeric_value("√0"), F(0))
        self.assertEqual(numeric_value("−√144"), F(-12))
        self.assertNotEqual(numeric_value("√4"), F(-2))
        for malformed in ("√−4", "√2", "√4+1", "__import__('os')", "[1]", "x"):
            with self.assertRaises(ValueError):
                numeric_value(malformed)
        for malformed in ("(0,1)junk", "(0,1),(0,-1)", "(x,y)"):
            with self.assertRaises(ValueError):
                one_pair(malformed)
        with self.assertRaises(ValueError):
            linear_coefficients(((0, 1), (0, -1)))
        with self.assertRaises(ValueError):
            linear_coefficients(((0, 2), (3, 0), (6, 2)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
