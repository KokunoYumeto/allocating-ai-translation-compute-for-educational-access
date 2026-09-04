"""Independent source/pixel/mathematics checks for actual MR-BRIDGE-008.

Run with python -B. No eval, downloads, extraction, builds, or file writes.
Readiness uses the previously tested exact coefficient interpreter from unit6;
relation projections are computed here from independently read source/pixels.
Fixed image hashes bind visual readings, not automatic image OCR. No browser,
Marathi-native/teacher, or whole-assignment approval is implied.
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

from test_unit6_math import evaluate, mathml_display


BASE = Path(__file__).resolve().parents[1]
UNIT = "MR-BRIDGE-008"
C = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
CONTEXT_ID = "fs-id1167829789538"
EXCLUDED_ID = "fs-id1167836692527"
SELECTED_IDS = (
    "para-00001", "list-00001", "fs-id1167836299681", "fs-idm404421072", "fs-idm387231616",
    "fs-id1167836538118", "fs-id1167829921677", "fs-id1167836418492", "fs-id1167836547061",
    "fs-id1167833059636", "fs-id1167836378970", "fs-id1167836629801", "fs-id1167833021555",
    "fs-id1167836509402", "fs-id1167829683746", "fs-id1167836340432", "fs-id1167824754892",
    "fs-id1167836532042", "fs-id1167833057329", "fs-id1167829750323", "fs-id1167829738598",
)
RELATION_SOURCE_IDS = dict(zip(("try1", "try2", "map1", "map2", "map3", "graph1", "graph2", "graph3"),
                               (SELECTED_IDS[i] for i in (11, 12, 14, 15, 16, 18, 19, 20))))
MODULE_PINS = {
    "en": ("A20-canonical.zip", "osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81373/index.cnxml",
           "2b606026c2b34cdf69acfa29bfe4b90abdb6961a322a78c7ec20107e0948b05c"),
    "id": ("A20-v0.3.0-source.zip", "source/modules/m81373/index.cnxml",
           "e9e593b31587995170c520b9175f2e0c0cb335282c951bb1d769f775344311ee"),
}
IMAGE_HASHES = {
    1: "b7187d1cd61e336d2ad7368cbe2710471f1d75f733aca9eef3b9674776c483c8",
    2: "ce00276b81f2e4ec1deea697515ddfb257580f23859d8017fb0ea0c3f4d2c3be",
    3: "da8bcab15681b37fde889ec049a04824e64ccdd6eda9934646d9aadf70c1e566",
    4: "c65297a087d98e313dc944b8ab60c55d9748dbfd4a786168e92075d467d3b1d0",
    5: "dddc2892ca12cfb8e3001d6c90c81dd3508ad43b04f373d9263212d3bc42f64c",
    6: "b743ed6e890e2f2b683f5b7bf242a6fc968b930ab4832706cceeab2bb1d180fc",
}
MONTHS = {}
for names in ("January February March April May June July August September October November December",
              "Januari Februari Maret April Mei Juni Juli Agustus September Oktober November Desember",
              "जानेवारी फेब्रुवारी मार्च एप्रिल मे जून जुलै ऑगस्ट सप्टेंबर ऑक्टोबर नोव्हेंबर डिसेंबर"):
    MONTHS.update(zip(names.split(), range(1, 13)))


def numeric_pairs(values):
    return tuple((F(x), F(y)) for x, y in values)


# Direct independent readings: first two from MathML, the rest from EN pixels.
RELATIONS = {
    "try1": numeric_pairs(((1, 1), (2, 8), (3, 27), (4, 64), (5, 125))),
    "try2": numeric_pairs(((1, 3), (2, 6), (3, 9), (4, 12), (5, 15))),
    "map1": (("Alison", (4, 25)), ("Penelope", (5, 23)), ("June", (8, 2)),
             ("Gregory", (9, 15)), ("Geoffrey", (1, 12)), ("Lauren", (5, 10)),
             ("Stephen", (7, 24)), ("Alice", (2, 3)), ("Liz", (8, 2)), ("Danny", (7, 24))),
    "map2": (("Khan Nguyen", "kn68413"), ("Abigail Brown", "ab56781"),
             ("Sumantha Mishal", "sm32479"), ("Jose Hernandez", "jh47983")),
    "map3": (("Maria", (11, 6)), ("Armando", (1, 18)), ("Cynthia", (12, 8)),
             ("Kelly", (3, 15)), ("Rachel", (11, 6))),
    "graph1": numeric_pairs(((1, 5), (-3, -1), (4, -2), (0, 3), (2, -2), (-3, 4))),
    "graph2": numeric_pairs(((-3, 3), (-2, 2), (-1, 0), (0, -1), (2, -2), (4, -4))),
    "graph3": numeric_pairs(((-3, 0), (-3, 5), (-3, -6), (-1, -2), (1, 2), (4, -4))),
}


def text(node):
    return "".join(node.itertext()).strip()


def source_math(node):
    display = mathml_display(node)
    leaves = [child for child in node.iter() if len(child) == 0]
    if leaves and leaves[-1].tag == M + "mo" and text(leaves[-1]) == ".":
        return display.removesuffix(".")  # Sentence punctuation inside source MathML.
    if leaves and leaves[-1].tag == M + "mn" and re.fullmatch(r"[0-9]+\.", text(leaves[-1])):
        # Readiness 3 includes its sentence period in the final <mn>5.</mn>.
        # An integer followed by a decimal point has that same exact value.
        return display.removesuffix(".")
    return display


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


def load_sources():
    lock_path = BASE / f"provenance/{UNIT}.lock.json"
    fragments = {}
    if lock_path.is_file():
        lock = read_json(lock_path)
        if [s["target_id"] for s in lock["source_selections"]] != list(SELECTED_IDS):
            raise ValueError("unexpected source selection")
        pins = {(w["path"], w["sha256"]) for w in lock["witnesses"]}
        for selection in lock["source_selections"]:
            if selection["locator"] != "A20:m81373#" + selection["target_id"]:
                raise ValueError("source locator mismatch")
            for source in selection["sources"]:
                locale = source["locale"]
                if source["module_sha256"] != MODULE_PINS[locale][2]:
                    raise ValueError("source-module pin drift")
                if (source["fragment_path"], source["fragment_sha256"]) not in pins:
                    raise ValueError("fragment missing from witnesses")
                raw = local_path(source["fragment_path"]).read_bytes()
                if hashlib.sha256(raw).hexdigest() != source["fragment_sha256"]:
                    raise ValueError("source fragment drift")
                key = (selection["target_id"], locale)
                if key in fragments:
                    raise ValueError("duplicate source fragment")
                fragments[key] = ET.fromstring(raw)
        if set(fragments) != {(sid, locale) for sid in SELECTED_IDS for locale in ("en", "id")}:
            raise ValueError("missing source fragment")
        return lock, fragments
    for locale, (archive, member, digest) in MODULE_PINS.items():
        with zipfile.ZipFile(BASE.parent / "downloads/mr-Deva-IN/releases" / archive) as handle:
            raw = handle.read(member)
        if hashlib.sha256(raw).hexdigest() != digest:
            raise ValueError("source-module pin drift")
        root = ET.fromstring(raw)
        ids = {node.get("id"): node for node in root.iter() if node.get("id")}
        opening = list(root.find(C + "content"))
        expected = list(SELECTED_IDS[:2]) + [n.get("id") for n in opening[:3]]
        expected += [n.get("id") for n in ids[CONTEXT_ID] if n.get("id") and n.get("id") != EXCLUDED_ID]
        if expected != list(SELECTED_IDS):
            raise ValueError("opening/first-section scope differs from the reviewed source")
        for sid in SELECTED_IDS:
            fragments[(sid, locale)] = ids[sid]
    return None, fragments


def atom(value):
    value = value.strip().replace("−", "-")
    if re.fullmatch(r"[+-]?[0-9]+", value):
        return F(value)
    parts = value.split()
    if len(parts) == 2:
        if parts[0] in MONTHS and parts[1].isdigit():
            return (MONTHS[parts[0]], int(parts[1]))
        if parts[0].isdigit() and parts[1] in MONTHS:
            return (MONTHS[parts[1]], int(parts[0]))
    if re.fullmatch(r"[a-z]{2}[0-9]{5}|[A-Za-z]+(?: [A-Za-z]+)*", value):
        return value
    raise ValueError(f"unsupported relation value: {value!r}")


def pairs(display):
    display = display.strip()
    if display.startswith("{"):
        if not display.endswith("}"):
            raise ValueError("unclosed pair set")
        display = display[1:-1]
    matches = list(re.finditer(r"\(([^(),]+),([^(),]+)\)", display))
    if not matches or re.sub(r"\([^()]*\)", "", display).strip(" ,\n\r\t"):
        raise ValueError("expected a finite ordered-pair list")
    return tuple((atom(m[1]), atom(m[2])) for m in matches)


def members(display):
    match = re.fullmatch(r"\{([^{}]*)\}", display.strip())
    if not match:
        raise ValueError("expected a braced finite set")
    return [atom(item) for item in match[1].split(",")]


def corrected_source(display, key, locale):
    # Deliberately narrow declared discrepancies, not general name normalization.
    if key == "map2":
        display = display.replace("Khanh Nguyen", "Khan Nguyen")
        if locale == "en":
            display = display.replace("Jose Hern and ez", "Jose Hernandez")
    if key == "map3" and locale == "en":
        display = display.replace("Arm and o", "Armando")
    return display


class Unit8MathematicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (BASE / f"translations/{UNIT}.xml").read_bytes()
        cls.root = ET.fromstring(cls.raw)
        cls.config = read_json(BASE / f"units/{UNIT}.json")
        cls.lock, cls.sources = load_sources()
        cls.ids, cls.checks = {}, {}
        for node in cls.root.iter():
            if node.get("id"):
                if node.get("id") in cls.ids:
                    raise ValueError("duplicate XML ID")
                cls.ids[node.get("id")] = node
            if "data-check" in node.attrib:
                if node.get("data-check") in cls.checks:
                    raise ValueError("duplicate mathematical check key")
                cls.checks[node.get("data-check")] = text(node)
        cls.images = {node.get("src").removeprefix("asset:"): node for node in cls.root.iter("img")}

    def test_actual_config_counts_and_35_math_entries(self):
        self.assertEqual(self.root.get("id"), UNIT)
        self.assertEqual(self.root.get("lang"), "mr-Deva-IN")
        decoded = self.raw.decode("utf-8")
        self.assertEqual(unicodedata.normalize("NFC", decoded), decoded)
        self.assertNotIn("\ufffd", decoded)
        self.assertEqual(self.checks, self.config["expected_math"])
        self.assertEqual(len(self.checks), 35)
        for key, expected in (("source_count", 21), ("translated_worked_examples", 2),
                              ("translated_definitions", 2), ("translated_practice_items", 9),
                              ("original_practice_items", 0)):
            self.assertEqual(self.config[key], expected)
        self.assertEqual(self.config["question_ids"], [])
        for term in self.config["required_terms"]:
            self.assertIn(term, text(self.root))
        sources = [self.sources[(sid, "en")] for sid in SELECTED_IDS]
        self.assertEqual(sum(n.tag == C + "example" for n in sources), 2)
        self.assertEqual(sum(1 for n in sources for _ in n.iter(C + "exercise")), 11)

    def test_three_readiness_questions_and_source_answers_by_exact_arithmetic(self):
        expected = ("3x−5", "2x²−x−3", "7x−1−4x+5")
        for n, source_id in enumerate(SELECTED_IDS[2:5], 1):
            target_expression = self.checks[f"ready{n}-expression"]
            self.assertEqual(evaluate(target_expression), evaluate(expected[n - 1]))
            for locale in ("en", "id"):
                source = self.sources[(source_id, locale)]
                problem = next(source.iter(C + "problem"))
                formulae = [source_math(node) for node in problem.iter(M + "math")]
                self.assertEqual(evaluate(formulae[0]), evaluate(expected[n - 1]))
                if n <= 2:
                    self.assertEqual(re.sub(r"\s+", "", formulae[1]).rstrip("."), ("x=−2", "x=a")[n - 1])
                solution = next(source.iter(C + "solution"))
                answer = "".join(source_math(node) for node in solution.iter(M + "math")) or text(solution)
                actual = evaluate(self.checks[f"ready{n}-answer"])
                self.assertEqual(actual, evaluate(answer))
                if n == 1:
                    self.assertEqual(actual, evaluate("f(−2)", "f(x)=" + formulae[0]))
                    self.assertEqual(actual, {(): F(-11)})
                elif n == 2:
                    self.assertEqual(actual, evaluate("f(a)", "f(x)=" + formulae[0]))
                    self.assertEqual(actual, {("a", "a"): F(2), ("a",): F(-1), (): F(-3)})
                else:
                    self.assertEqual(actual, evaluate(formulae[0]))
                    self.assertEqual(actual, {("x",): F(3), (): F(4)})
        self.assertEqual(self.checks["ready1-input"].replace(" ", ""), "x=−2")
        self.assertEqual(self.checks["ready2-input"].replace(" ", ""), "x=a")
        for step in self.checks["ready1-working"].split("="):
            self.assertEqual(evaluate(step), {(): F(-11)})

    def test_eight_relations_and_all_sixteen_domain_range_projections(self):
        for key, expected in RELATIONS.items():
            with self.subTest(relation=key):
                actual = pairs(self.checks[key + ("-relation" if key.startswith("try") else "-pairs")])
                self.assertEqual(len(actual), len(expected))
                self.assertEqual(len(set(actual)), len(actual))
                self.assertEqual(set(actual), set(expected))
                for kind, index in (("domain", 0), ("range", 1)):
                    answer = members(self.checks[f"{key}-{kind}"])
                    self.assertEqual(len(answer), len(set(answer)))
                    self.assertEqual(set(answer), {pair[index] for pair in expected})
        self.assertEqual(len({x for x, y in RELATIONS["graph3"]}), 4)
        self.assertIn((F(-3), F(-6)), RELATIONS["graph3"])
        self.assertNotIn(F(0), {x for x, y in RELATIONS["try1"]})
        self.assertNotIn(F(1, 2), {x for x, y in RELATIONS["graph2"]})

    def test_all_eight_relation_source_solutions_preserved_with_declared_name_readings(self):
        for key, sid in RELATION_SOURCE_IDS.items():
            for locale in ("en", "id"):
                source = self.sources[(sid, locale)]
                solution = next(source.iter(C + "solution"))
                content = corrected_source(text(solution), key, locale)
                parts = [part.strip() for part in re.split("[ⓐⓑⓒ]", content) if part.strip()]
                self.assertEqual(len(parts), 2 if key.startswith("try") else 3)
                if key.startswith("try"):
                    problem = next(source.iter(C + "problem"))
                    displayed = next(re.finditer(r"\{[^{}]*\}", text(problem)))[0]
                    self.assertEqual(set(pairs(displayed)), set(RELATIONS[key]))
                else:
                    pair_text = parts.pop(0)
                    match = re.search(r"\{[^{}]*\}", pair_text)
                    self.assertEqual(set(pairs(match[0] if match else pair_text)), set(RELATIONS[key]))
                for part, index in zip(parts, (0, 1)):
                    match = re.search(r"\{[^{}]*\}", part)
                    answer = members(match[0])
                    self.assertEqual(set(answer), {pair[index] for pair in RELATIONS[key]})

    def test_mapping_alts_keep_every_arrow_and_literal_student_id(self):
        for n in range(1, 4):
            alt = self.images[f"CNX_IntAlg_Figure_03_05_{n:03d}_img_new.jpg"].get("alt")
            rows = alt.split(":", 1)[1].strip().removesuffix(".").split(";")
            actual = tuple(tuple(atom(value) for value in row.strip().split(" ते ")) for row in rows)
            self.assertEqual(actual, RELATIONS[f"map{n}"])
        self.assertIn(("Liz", (8, 2)), RELATIONS["map1"])
        self.assertNotIn(("Liz", (7, 24)), RELATIONS["map1"])
        self.assertEqual({y for x, y in RELATIONS["map2"]}, {"kn68413", "ab56781", "sm32479", "jh47983"})

    def test_graph_alts_keep_coordinates_axis_bounds_and_the_lower_edge_point(self):
        for n in range(4, 7):
            alt = self.images[f"CNX_IntAlg_Figure_03_05_{n:03d}_img_new.jpg"].get("alt")
            # The final alt repeats its edge point as a separate explanatory note.
            listed = alt.split(".", 1)[0].split(":", 1)[1]
            self.assertEqual(set(pairs(listed)), set(RELATIONS[f"graph{n - 3}"]))
            self.assertEqual(len(pairs(listed)), 6)
            self.assertIn("−6 ते 6", alt)
        self.assertIn("खालच्या कडेवरील (−3, −6)", self.images["CNX_IntAlg_Figure_03_05_006_img_new.jpg"].get("alt"))

    def test_liz_and_name_disagreements_are_visibly_documented(self):
        source1 = self.sources[(RELATION_SOURCE_IDS["map1"], "en")]
        self.assertIn("July 24: one from Stephen and one from Liz", next(source1.iter(C + "media")).get("alt"))
        notes1 = " ".join(text(p) for p in self.ids[RELATION_SOURCE_IDS["map1"]].iter("p") if p.get("data-kind") == "original")
        for token in ("Liz", "24 जुलै", "2 ऑगस्ट", "इंग्रजी"):
            self.assertIn(token, notes1)
        for locale in ("en", "id"):
            source2 = next(self.sources[(RELATION_SOURCE_IDS["map2"], locale)].iter(C + "solution"))
            self.assertIn("Khanh Nguyen", text(source2))
        for key, required in (("map2", {"Khanh Nguyen", "Khan Nguyen", "Jose Hern and ez", "Jose Hernandez"}),
                              ("map3", {"Arm and o", "Armando"})):
            original_notes = [p for p in self.ids[RELATION_SOURCE_IDS[key]].iter("p") if p.get("data-kind") == "original"]
            self.assertTrue(required <= {text(code) for p in original_notes for code in p.iter("code")})
        self.assertNotIn("Khanh Nguyen", self.checks["map2-domain"])
        self.assertNotIn("Hern and ez", self.checks["map2-domain"])
        self.assertNotIn("Arm and o", self.checks["map3-domain"])

    def test_objectives_definition_order_and_prior_example_exclusion(self):
        for locale in ("en", "id"):
            self.assertEqual(len(self.sources[("list-00001", locale)].findall(C + "item")), 3)
            for sid in ("fs-id1167836378970", "fs-id1167836509402"):
                self.assertEqual(list(self.sources[(sid, locale)].iter(C + "exercise")), [])
        self.assertEqual(len(self.ids["list-00001"].findall("ul/li")), 3)
        self.assertEqual(self.checks["student-pair"], "(विद्यार्थ्याचे नाव, विद्यार्थी ओळख क्रमांक)")
        self.assertEqual(self.checks["ordered-pair"].replace(" ", ""), "(x,y)")
        self.assertEqual(text(self.ids["term-00001"]), "संबंध")
        self.assertEqual(text(self.ids["term-00002"]), "प्रांत")
        self.assertEqual(text(self.ids["term-00003"]), "प्रतिचित्रण")
        self.assertNotIn(EXCLUDED_ID, self.ids)
        self.assertNotIn(EXCLUDED_ID, SELECTED_IDS)
        previous = ET.parse(BASE / "translations/MR-BRIDGE-001.xml").getroot()
        self.assertEqual(sum(node.get("data-source") == "A20:m81373#" + EXCLUDED_ID for node in previous.iter()), 1)

    def test_101_selected_original_ids_plus_the_retained_context_id(self):
        self.assertEqual([n.get("data-source") for n in self.root.iter() if n.get("data-source")],
                         ["A20:m81373#" + sid for sid in SELECTED_IDS])
        actual = [n.get("id") for n in self.root.iter() if re.match(r"(?:fs-id|para-|list-|term-)", n.get("id", ""))]
        for locale in ("en", "id"):
            source_ids = [n.get("id") for sid in SELECTED_IDS for n in self.sources[(sid, locale)].iter() if n.get("id")]
            self.assertEqual(len(source_ids), 101)
            self.assertEqual(len(set(source_ids)), 101)
            source_ids.insert(21, CONTEXT_ID)
            self.assertEqual(actual, source_ids)
            for sid in SELECTED_IDS:
                source = self.sources[(sid, locale)]
                target_ids = {n.get("id") for n in self.ids[sid].iter() if n.get("id")}
                self.assertTrue({n.get("id") for n in source.iter() if n.get("id")} <= target_ids)

    def test_all_eleven_supplied_solutions_and_bidirectional_navigation(self):
        count = 0
        for sid in SELECTED_IDS:
            for exercise in self.sources[(sid, "en")].iter(C + "exercise"):
                count += 1
                problem, solution = exercise.find(C + "problem"), exercise.find(C + "solution")
                self.assertIsNotNone(solution)
                target_exercise = self.ids[exercise.get("id")]
                for source, kind in ((problem, "problem"), (solution, "solution")):
                    target = next(n for n in target_exercise if n.get("id") == source.get("id"))
                    self.assertIn(kind, target.get("class", "").split())
                answer = self.ids[solution.get("id")]
                self.assertNotEqual(answer.get("data-kind"), "original")
                self.assertTrue(text(answer.find("h4")).startswith("स्रोतातील"))
                for start, end in ((problem.get("id"), solution.get("id")), (solution.get("id"), problem.get("id"))):
                    self.assertIn("#" + end, [a.get("href") for a in self.ids[start].iter("a") if text(a)])
        self.assertEqual(count, 11)
        self.assertFalse(any(sid.startswith("mr-answer-") for sid in self.ids))
        self.assertEqual(sum("solution" in n.get("class", "").split() for n in self.root.iter()), 11)

    def test_three_original_readiness_references_keep_document_and_target(self):
        references = [a for a in self.root.iter("a") if a.get("data-source-document")]
        self.assertEqual(len(references), 3)
        for sid, anchor, target_id in zip(SELECTED_IDS[2:5], references,
                                         ("fs-id1167836530265", "fs-id1167836530265", "fs-id1167836652573")):
            for locale in ("en", "id"):
                source_links = list(self.sources[(sid, locale)].iter(C + "link"))
                self.assertEqual(len(source_links), 1)
                self.assertEqual(source_links[0].get("document"), "m81422")
                self.assertEqual(source_links[0].get("target-id"), target_id)
            self.assertEqual(anchor.get("data-source-document"), "m81422")
            self.assertEqual(anchor.get("data-source-target-id"), target_id)
            self.assertEqual(anchor.get("href"), "https://openstax.org/books/intermediate-algebra-2e/pages/1-1-use-the-language-of-algebra#" + target_id)
            self.assertTrue(text(anchor))
        for anchor in self.root.iter("a"):
            if anchor.get("href", "").startswith("#"):
                self.assertIn(anchor.get("href")[1:], self.ids)

    def test_six_assets_are_exact_pinned_canonical_pixels_under_original_media_ids(self):
        self.assertIsNotNone(self.lock, "final source/asset freeze is required")
        self.assertEqual(len(self.sources), 42)
        assets = self.config.get("assets", {})
        expected_names = {f"CNX_IntAlg_Figure_03_05_{n:03d}_img_new.jpg" for n in IMAGE_HASHES}
        self.assertEqual(set(assets), expected_names)
        self.assertEqual(set(self.images), expected_names)
        self.assertEqual(len(list(self.root.iter("img"))), 6)
        pins = {(w["path"], w["sha256"]) for w in self.lock["witnesses"]}
        for n, digest in IMAGE_HASHES.items():
            name = f"CNX_IntAlg_Figure_03_05_{n:03d}_img_new.jpg"
            asset = assets[name]
            self.assertEqual(asset["sha256"], digest)
            self.assertEqual(asset["mime"], "image/jpeg")
            self.assertIn((asset["path"], digest), pins)
            raw = local_path(asset["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), digest)
            self.assertTrue(raw.startswith(b"\xff\xd8\xff"))
            key = f"map{n}" if n <= 3 else f"graph{n - 3}"
            source_media = next(self.sources[(RELATION_SOURCE_IDS[key], "en")].iter(C + "media"))
            figure = self.ids[source_media.get("id")]
            self.assertEqual(figure.tag, "figure")
            self.assertEqual(figure.find("img").get("src"), "asset:" + name)
            self.assertEqual(figure.find("figcaption").get("data-kind"), "original")


class RelationParserTests(unittest.TestCase):
    def test_date_languages_names_and_student_codes_remain_distinct(self):
        self.assertEqual(atom("August 2"), atom("2 ऑगस्ट"))
        self.assertEqual(atom("2 Agustus"), atom("2 ऑगस्ट"))
        self.assertNotEqual(atom("July 24"), atom("2 ऑगस्ट"))
        self.assertEqual(atom("June"), "June")
        self.assertNotEqual(atom("Khan Nguyen"), atom("Khanh Nguyen"))
        self.assertEqual(atom("kn68413"), "kn68413")

    def test_no_code_or_unparsed_tail_is_accepted(self):
        for value in ("__import__('os')", "1+2", "2/3", "kn 68413"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                atom(value)
        with self.assertRaises(ValueError):
            pairs("(1, 2), execute(3)")
        with self.assertRaises(ValueError):
            members("{1,2")


if __name__ == "__main__":
    unittest.main(verbosity=2)
