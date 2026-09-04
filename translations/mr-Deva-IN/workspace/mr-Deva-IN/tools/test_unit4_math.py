"""Independent finite-relation/source QA for actual MR-BRIDGE-004 files.

Run with python -B. No eval, downloads, bulk extraction, builds, or file writes.
The eight EN raster interpretations were directly visually checked; fixed image
hashes bind those readings to exact pixels. Tests do not perform image OCR or
claim human/native-speaker review, rendering QA, or clinical BMI validation.
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import unittest
import xml.etree.ElementTree as ET
import zipfile


BASE = Path(__file__).resolve().parents[1]
UNIT = "MR-BRIDGE-004"
C = "{http://cnx.rice.edu/cnxml}"
SELECTED_IDS = (
    "fs-id1167833041789", "fs-id1167836701331", "fs-id1167836694560", "fs-id1167829738657",
    "fs-id1167836289174", "fs-id1167836513003", "fs-id1167836309438", "fs-id1167824736897",
    "fs-id1167836600990", "fs-id1167833128978", "fs-id1167829590523", "fs-id1167825791209",
    "fs-id1167836621459", "fs-id1167833274699", "fs-id1167836707143", "fs-id1167836509162",
)
EXERCISE_IDS = tuple(SELECTED_IDS[i] for i in (2, 3, 4, 5, 7, 8, 9, 10, 12, 13, 14, 15))
MODULE_PINS = {
    "en": ("A20-canonical.zip", "osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81373/index.cnxml",
           "2b606026c2b34cdf69acfa29bfe4b90abdb6961a322a78c7ec20107e0948b05c"),
    "id": ("A20-v0.3.0-source.zip", "source/modules/m81373/index.cnxml",
           "e9e593b31587995170c520b9175f2e0c0cb335282c951bb1d769f775344311ee"),
}
IMAGE_HASHES = {
    201: "01f56acce910e4c6354242e9307bbd458b4a76fd74856cf90b9bad5ebd4b364b",
    202: "c374c8edb5c175f0919dd49695c40c0ef1b14266c9ae7919c80091a1f612a3bf",
    203: "2b9abc6b43618bd4ffe50bee7349233943eddaeb24b20aa4b1028174cdf149af",
    204: "cf667d126d49115d78fdc12db15d195b255a1793a90374ff6dcd1dedca70875b",
    205: "904bf393939f9ba87479847d835cae3f2fdd9ec680b094a04ec6099f8ac43d02",
    206: "6c5c583d3f4021fa0b5bea778795ec84c0369132690ac21e70cfa178e31c2092",
    207: "df7a43ec42177e9d3b5bc4fb594633ee4d721b92298073311e2c07083daa86fb",
    208: "7d86642fff819ff6419b0f786494458b3f5b5144f48011fade0866b3e4201d05",
}
MONTHS_MR = dict(zip("जानेवारी फेब्रुवारी मार्च एप्रिल मे जून जुलै ऑगस्ट सप्टेंबर ऑक्टोबर नोव्हेंबर डिसेंबर".split(), range(1, 13)))
MONTHS_EN = dict(zip("January February March April May June July August September October November December".split(), range(1, 13)))
NUMERIC = re.compile(r"[+-]?[0-9]+(?:\.[0-9]+)?\Z")


def numeric_pairs(pairs):
    return tuple((F(str(x)), F(str(y))) for x, y in pairs)


# Independent readings: E1-E4 from canonical MathML; E5-E12 from the EN pixels.
RELATIONS = {
    1: numeric_pairs(((1, 4), (2, 8), (3, 12), (4, 16), (5, 20))),
    2: numeric_pairs(((1, -2), (2, -4), (3, -6), (4, -8), (5, -10))),
    3: numeric_pairs(((1, 7), (5, 3), (7, 9), (-2, -3), (-2, 8))),
    4: numeric_pairs(((11, 3), (-2, -7), (4, -8), (4, 17), (-6, 9))),
    5: (("Rebecca", (1, 18)), ("Jennifer", (4, 1)), ("John", (1, 18)), ("Hector", (6, 23)),
        ("Luis", (2, 15)), ("Ebony", (4, 7)), ("Raphael", (11, 6)), ("Meredith", (8, 19)),
        ("Karen", (8, 19)), ("Joseph", (7, 30))),
    6: (("Amy", (2, 24)), ("Carol", (5, 30)), ("Devon", (1, 5)), ("Harrison", (1, 7)),
        ("Jackson", (11, 26)), ("Labron", (4, 7)), ("Mason", (7, 20)), ("Natalie", (3, 1)),
        ("Paul", (8, 1)), ("Sylvester", (11, 13))),
    7: numeric_pairs(((100, "17.2"), (110, "18.9"), (120, "20.6"), (130, "22.3"),
                      (140, "24.0"), (150, "25.7"), (160, "27.5"))),
    8: numeric_pairs(((130, "18.1"), (140, "19.5"), (150, "20.9"), (160, "22.3"),
                      (170, "23.7"), (180, "25.1"), (190, "26.5"), (200, "27.9"))),
    9: numeric_pairs(((-3, 4), (-2, -1), (0, -3), (2, 3), (4, -1), (4, -3))),
    10: numeric_pairs(((-3, 4), (-3, -4), (-2, 0), (-1, 3), (1, 5), (4, -2))),
    11: numeric_pairs(((-1, 4), (-1, -4), (0, 3), (0, -3), (1, 4), (1, -4))),
    12: numeric_pairs(((-2, -6), (-1, -3), (0, 0), ("0.5", "1.5"), (1, 3), (2, 6))),
}


def text(node):
    return "".join(node.itertext()).strip()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def local_path(relative):
    path = (BASE / relative).resolve()
    if not path.is_relative_to(BASE):
        raise ValueError("path escapes language directory")
    return path


def atom(value, source=False):
    value = value.strip().replace("−", "-")
    if source:
        # Source E7 contains the printed decimal-space artifact "17. 2".
        value = re.sub(r"(?<=[0-9])\.\s+(?=[0-9])", ".", value)
    if NUMERIC.fullmatch(value):
        return F(value)
    parts = value.split()
    if len(parts) == 2:
        if parts[0] in MONTHS_EN and parts[1].isdigit():
            return (MONTHS_EN[parts[0]], int(parts[1]))
        if parts[0].isdigit() and parts[1] in MONTHS_MR:
            return (MONTHS_MR[parts[1]], int(parts[0]))
    if re.fullmatch(r"[A-Za-z]+", value):
        return value
    raise ValueError(f"unsupported relation atom: {value!r}")


def pairs(display, source=False):
    display = display.strip()
    if display.startswith("{"):
        if not display.endswith("}"):
            raise ValueError("unclosed relation set")
        display = display[1:-1].strip()
    matches = list(re.finditer(r"\(([^(),]+),([^(),]+)\)", display))
    if not matches or re.sub(r"\([^()]*\)", "", display).strip(" ,\n\r\t"):
        raise ValueError("expected a finite list of ordered pairs")
    return [(atom(m[1], source), atom(m[2], source)) for m in matches]


def members(display, source=False):
    match = re.fullmatch(r"\{([^{}]*)\}", display.strip())
    if not match:
        raise ValueError("expected an explicit finite set")
    values = match[1].split(",")
    if source and not values[-1].strip():
        values.pop()  # E7 source domain has a trailing delimiter.
    return [atom(value, source) for value in values]


def load_sources():
    """Prefer frozen fragments; before freezing, read two small ZIP members."""
    lock_path = BASE / f"provenance/{UNIT}.lock.json"
    fragments = {}
    if lock_path.is_file():
        lock = read_json(lock_path)
        if [s["target_id"] for s in lock["source_selections"]] != list(SELECTED_IDS):
            raise ValueError("unexpected frozen source selection")
        for selection in lock["source_selections"]:
            for witness in selection["sources"]:
                locale = witness["locale"]
                if witness["module_sha256"] != MODULE_PINS[locale][2]:
                    raise ValueError("wrong source-module pin")
                raw = local_path(witness["fragment_path"]).read_bytes()
                if hashlib.sha256(raw).hexdigest() != witness["fragment_sha256"]:
                    raise ValueError("source fragment hash drift")
                key = (selection["target_id"], locale)
                if key in fragments:
                    raise ValueError("duplicate source fragment")
                fragments[key] = ET.fromstring(raw)
        return lock, fragments
    for locale, (archive, member, digest) in MODULE_PINS.items():
        with zipfile.ZipFile(BASE.parent / "downloads/mr-Deva-IN/releases" / archive) as handle:
            raw = handle.read(member)  # ZIP CRC is checked; nothing is extracted.
        if hashlib.sha256(raw).hexdigest() != digest:
            raise ValueError("source-module hash drift")
        lookup = {n.get("id"): n for n in ET.fromstring(raw).iter() if n.get("id")}
        for source_id in SELECTED_IDS:
            fragments[(source_id, locale)] = lookup[source_id]
    return None, fragments


class Unit4MathematicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (BASE / f"translations/{UNIT}.xml").read_bytes()
        cls.root = ET.fromstring(cls.raw)
        cls.config = read_json(BASE / f"units/{UNIT}.json")
        cls.lock, cls.sources = load_sources()
        cls.ids = {}
        cls.checks = {}
        for node in cls.root.iter():
            if node.get("id"):
                if node.get("id") in cls.ids:
                    raise ValueError("duplicate XML ID")
                cls.ids[node.get("id")] = node
            if "data-check" in node.attrib:
                key = node.get("data-check")
                if key in cls.checks:
                    raise ValueError("duplicate mathematical check key")
                cls.checks[key] = text(node)
        cls.images = {node.get("src").removeprefix("asset:"): node for node in cls.root.iter("img")}

    def test_unit_structure_and_real_config(self):
        self.assertEqual(self.root.get("id"), UNIT)
        self.assertEqual(self.root.get("lang"), "mr-Deva-IN")
        self.assertEqual(unicodedata.normalize("NFC", self.raw.decode("utf-8")), self.raw.decode("utf-8"))
        self.assertEqual(self.checks, self.config["expected_math"])
        self.assertEqual(len(self.checks), 40)
        self.assertEqual(self.config["source_count"], 16)
        self.assertEqual(self.config["translated_practice_items"], 12)
        self.assertEqual(self.config["original_practice_items"], 0)
        self.assertEqual(self.config["question_ids"], [])

    def test_all_twelve_relations_and_computed_projections(self):
        for n, expected in RELATIONS.items():
            with self.subTest(exercise=n):
                key = f"e{n}-relation" if n <= 4 else f"e{n}-pairs"
                actual = pairs(self.checks[key])
                self.assertEqual(len(actual), len(expected))
                self.assertEqual(len(actual), len(set(actual)), "duplicate relation pair")
                self.assertEqual(set(actual), set(expected), "relation differs from canonical reading")
                for kind, index in (("domain", 0), ("range", 1)):
                    answer = members(self.checks[f"e{n}-{kind}"])
                    self.assertEqual(len(answer), len(set(answer)), "answer set has duplicate members")
                    self.assertEqual(set(answer), {pair[index] for pair in expected})

    def test_first_four_relations_match_actual_en_and_id_mathml(self):
        for n, source_id in enumerate(EXERCISE_IDS[:4], 1):
            for locale in ("en", "id"):
                with self.subTest(exercise=n, locale=locale):
                    problem = self.sources[(source_id, locale)].find(C + "problem")
                    self.assertEqual(set(pairs(text(problem), source=True)), set(RELATIONS[n]))

    def test_six_preserved_source_answers_match_canonical_content(self):
        for n in (1, 3, 5, 7, 9, 11):
            source = self.sources[(EXERCISE_IDS[n - 1], "en")]
            solution = source.find(C + "solution")
            self.assertIsNotNone(solution)
            parts = [part.strip() for part in re.split("[ⓐⓑⓒ]", text(solution)) if part.strip()]
            if n <= 4:
                self.assertEqual(len(parts), 2)
                domains, ranges = parts
            else:
                self.assertEqual(len(parts), 3)
                self.assertEqual(set(pairs(parts[0], source=True)), set(RELATIONS[n]))
                domains, ranges = parts[1:]
            self.assertEqual(set(members(domains, source=True)), {x for x, _ in RELATIONS[n]})
            self.assertEqual(set(members(ranges, source=True)), {y for _, y in RELATIONS[n]})
        self.assertIn("+100", self.checks["e7-pairs"])
        self.assertIn("+100", self.checks["e7-domain"])

    def test_exact_six_source_and_six_visibly_authored_answers(self):
        counts = {"source": 0, "original": 0}
        for n, source_id in enumerate(EXERCISE_IDS, 1):
            target = self.ids[source_id]
            original = self.sources[(source_id, "en")].find(C + "solution")
            target_solutions = [node for node in target.iter() if "solution" in node.get("class", "").split()]
            self.assertEqual(len(target_solutions), 1)
            answer = target_solutions[0]
            if original is not None:
                counts["source"] += 1
                self.assertEqual(answer.get("id"), original.get("id"))
                self.assertNotEqual(answer.get("data-kind"), "original")
                self.assertEqual(text(answer.find("h4")), "स्रोतातील उत्तर")
            else:
                counts["original"] += 1
                self.assertEqual(answer.get("id"), "mr-answer-" + source_id)
                self.assertEqual(answer.get("data-kind"), "original")
                self.assertEqual(text(answer.find("h4")), "नव्याने जोडलेले उत्तर")
                self.assertIn("मूळ", text(answer))
                self.assertIn("नाही", text(answer))
            for locale in ("en", "id"):
                self.assertEqual(self.sources[(source_id, locale)].find(C + "solution") is not None,
                                 n in (1, 3, 5, 7, 9, 11))
        self.assertEqual(counts, {"source": 6, "original": 6})

    def test_all_sixteen_source_blocks_and_sixty_original_ids(self):
        self.assertEqual([node.get("data-source") for node in self.root.iter() if node.get("data-source")],
                         ["A20:m81373#" + source_id for source_id in SELECTED_IDS])
        actual_ids = [node.get("id") for node in self.root.iter() if node.get("id", "").startswith("fs-id")]
        for locale in ("en", "id"):
            source_ids = [node.get("id") for source_id in SELECTED_IDS
                          for node in self.sources[(source_id, locale)].iter() if node.get("id")]
            self.assertEqual(len(source_ids), 60)
            self.assertEqual(len(set(source_ids)), 60)
            self.assertEqual(actual_ids, source_ids)
            for source_id in SELECTED_IDS:
                source = self.sources[(source_id, locale)]
                target = self.ids[source_id]
                target_ids = {node.get("id") for node in target.iter() if node.get("id")}
                self.assertTrue({node.get("id") for node in source.iter() if node.get("id")} <= target_ids)
                if source.tag == C + "exercise":
                    children = {node.get("id"): node for node in target if node.get("id")}
                    for kind in ("problem", "solution"):
                        for part in source.findall(C + kind):
                            self.assertIn(part.get("id"), children)
                            self.assertIn(kind, children[part.get("id")].get("class", "").split())

    def test_all_twelve_question_answer_navigation_pairs(self):
        for source_id in EXERCISE_IDS:
            source = self.sources[(source_id, "en")]
            problem_id = source.find(C + "problem").get("id")
            source_answer = source.find(C + "solution")
            answer_id = source_answer.get("id") if source_answer is not None else "mr-answer-" + source_id
            for start, end in ((problem_id, answer_id), (answer_id, problem_id)):
                self.assertIn("#" + end, [a.get("href") for a in self.ids[start].iter("a") if text(a)])
        for anchor in self.root.iter("a"):
            if anchor.get("href", "").startswith("#"):
                self.assertIn(anchor.get("href")[1:], self.ids)

    def test_mapping_alt_describes_actual_arrow_endpoints(self):
        for n in range(5, 9):
            image_id = f"CNX_IntAlg_Figure_03_05_{196 + n}_img_new.jpg"
            alt = self.images[image_id].get("alt")
            rows = alt.split(":", 1)[1].strip().rstrip(".").split(";")
            actual = [tuple(atom(value) for value in row.strip().split(" ते ")) for row in rows]
            self.assertEqual(len(actual), len(RELATIONS[n]))
            self.assertEqual(set(actual), set(RELATIONS[n]))
        self.assertIn(("Amy", (2, 24)), pairs(self.checks["e6-pairs"]))
        self.assertNotIn(("Amy", (2, 14)), pairs(self.checks["e6-pairs"]))

    def test_graph_alt_coordinates_and_visible_axis_labels(self):
        for n, bound in ((9, 5), (10, 6), (11, 6), (12, 7)):
            image_id = f"CNX_IntAlg_Figure_03_05_{196 + n}_img_new.jpg"
            alt = self.images[image_id].get("alt")
            actual = pairs(", ".join(re.findall(r"\([^()]+,[^()]+\)", alt)))
            self.assertEqual(len(actual), 6)
            self.assertEqual(set(actual), set(RELATIONS[n]))
            bounds = re.search(r"दोन्ही अक्षांवर\s+([−-]?[0-9]+)\s+ते\s+([0-9]+)", alt)
            self.assertIsNotNone(bounds)
            self.assertEqual((atom(bounds[1]), atom(bounds[2])), (F(-bound), F(bound)))
        self.assertIn((F(-2), F(-1)), RELATIONS[9])
        self.assertNotIn((F(-3), F(-1)), RELATIONS[9])
        self.assertIn((F(1, 2), F(3, 2)), RELATIONS[12])
        self.assertNotIn((F(-2), F(-3)), RELATIONS[12])
        self.assertNotIn((F(3), F(6)), RELATIONS[12])

    def test_all_eight_assets_are_the_exact_visually_read_en_rasters(self):
        self.assertIsNotNone(self.lock, "unit source/asset freezing is still required")
        assets = self.config.get("assets", {})
        expected_names = {f"CNX_IntAlg_Figure_03_05_{n}_img_new.jpg" for n in IMAGE_HASHES}
        self.assertEqual(set(assets), expected_names)
        self.assertEqual(set(self.images), expected_names)
        self.assertEqual(len(list(self.root.iter("img"))), 8)
        pins = {(item["path"], item["sha256"]) for item in self.lock["witnesses"]}
        for n, expected_sha in IMAGE_HASHES.items():
            name = f"CNX_IntAlg_Figure_03_05_{n}_img_new.jpg"
            asset = assets[name]
            self.assertEqual(asset["mime"], "image/jpeg")
            self.assertEqual(asset["sha256"], expected_sha)
            self.assertIn((asset["path"], expected_sha), pins)
            raw = local_path(asset["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), expected_sha)
            self.assertTrue(raw.startswith(b"\xff\xd8\xff"))
            source = self.sources[(EXERCISE_IDS[n - 197], "en")]
            media = next(source.iter(C + "media"))
            figure = self.ids[media.get("id")]
            self.assertEqual(figure.tag, "figure")
            self.assertEqual(figure.find("img").get("src"), "asset:" + name)
            self.assertEqual(figure.find("figcaption").get("data-kind"), "original")

    def test_bmi_values_are_preserved_labels_not_new_clinical_calculations(self):
        self.assertEqual(self.checks["e7-height"], "5′4″")
        self.assertEqual(self.checks["e8-height"], "5′11′′")
        self.assertEqual(self.checks["e7-source-bmi-band"], "18.5–24.9")
        self.assertEqual(self.checks["e8-source-bmi-band"], "18.5–24.9")
        self.assertEqual(self.ids["bmi-note"].get("data-kind"), "original")
        for n in (7, 8):
            source = self.sources[(EXERCISE_IDS[n - 1], "en")]
            problem_id = source.find(C + "problem").get("id")
            self.assertIn("#bmi-note", [a.get("href") for a in self.ids[problem_id].iter("a")])


class RelationParserTests(unittest.TestCase):
    def test_exact_decimal_and_equivalent_signed_values(self):
        self.assertEqual(atom("0.5"), F(1, 2))
        self.assertEqual(atom("+100"), atom("100"))
        self.assertEqual(atom("17. 2", source=True), F(86, 5))
        self.assertEqual(atom("February 24"), atom("24 फेब्रुवारी"))

    def test_unsupported_expressions_are_not_evaluated(self):
        for value in ("__import__('os')", "1 + 2", "0.5;bad", "1/2"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                atom(value)
        with self.assertRaises(ValueError):
            pairs("(1, 2), execute(3)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
