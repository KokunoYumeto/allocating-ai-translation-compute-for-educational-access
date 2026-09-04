"""Independent MR014 source/graph/mathematical regressions; stdlib, read-only.

Run with Python -B. Reads pinned ZIP members in memory and existing artifacts.
No downloads, extraction, browser, HTML geometry inspection, builds or writes.
Pixel observations below bind personally viewed diagrams, not inferred alt text.
Receipt checks certify structural currency only, never reader visual acceptance.
"""
import ast
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import unittest
import xml.etree.ElementTree as ET
import zipfile

import build_unit


BASE = Path(__file__).resolve().parents[1]
UNIT = "MR-BRIDGE-014"
C = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SECTION = "fs-id1167836386547"
SELECTED = (
    "fs-id1167833022366", "fs-id1167836620724", "fs-id1167836514287",
    "fs-id1167825884739", "fs-id1167829756085", "fs-id1167836529485",
    "fs-id1167833060073", "fs-id1167836515910", "fs-id1167836731462",
    "fs-id1167836507624", "fs-id1167829999559", "fs-id1167832982157",
)
PINS = {
    "en": ("downloads/mr-Deva-IN/releases/A20-canonical.zip",
           "osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/",
           "effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917",
           "021c29fa9a6ab3d5b06d2ef143a82d2ac818ed25fe6fd44ebf5d7a6be07a123a"),
    "id": ("downloads/mr-Deva-IN/releases/A20-v0.3.0-source.zip", "source/",
           "a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7",
           "d89a74aef766afca6a4ac7e1ae720f120d22cc771c11dd7e025c55bca1fabb8e"),
}
IMAGES = (
    ("021", "fs-id1167836538244", 54157, "de4aa43fed8405eecd5c2b374de9de22ac05cc5671dc724fc6011d770cbc329e"),
    ("022", "fs-id1167829597137", 52220, "39d13f9e14959fde61119ba84591dd98665e62e6e8b9b0ab025b2ef35ab6f5d8"),
    ("023", "fs-id1167833128692", 55962, "0daa3919143f4279d61d1e26b70fbb78110a7b4e98971ad0c450bbabd0275556"),
    ("024", "fs-id1167836493218", 68566, "7e37d1d621f9291e7a543e53ceea6586ca389e178ff1673078c532408f7c7c93"),
    ("025", "fs-id1167836539761", 59176, "ceefe1e03a19fe0d5f88df9caa5fa722a4e4d64afe23293dcd815d112841fceb"),
    ("026", "fs-id1167836287943", 56643, "a961ce18529cd108247ddd1b6cd093eff3946f8df52b110c116525962521d504"),
)
# The extrema/closed endpoints below were personally read from all six locale
# pairs. No polynomial is fitted to the first three arbitrary drawn curves.
FINITE = (
    ("example1", SELECTED[4], (-3, 3), (-1, 3)),
    ("try1", SELECTED[5], (-5, 1), (-4, 2)),
    ("try2", SELECTED[6], (-2, 4), (-5, 3)),
)
WAVES = (
    ("example2", SELECTED[8], "fs-id1167836377545", "fs-id1167836507194", 1, 0),
    ("try3", SELECTED[9], "fs-id1167836418791", "fs-id1167836550513", 2, 0),
    ("try4", SELECTED[10], "fs-id1167836526481", "fs-id1167836612647", 1, F(1, 2)),
)
# x coordinates in multiples of pi, and exact y values at the visible nodes.
# These are lookup witnesses from the actual pixels, not trigonometric formulae
# inserted into the source. Global continuation is checked separately below.
PIXEL_NODES = {
    "example2": dict(zip(map(F, (-2, F(-3, 2), -1, F(-1, 2), 0, F(1, 2), 1, F(3, 2), 2)),
                         (0, 1, 0, -1, 0, 1, 0, -1, 0))),
    "try3": dict(zip(map(F, (-2, F(-3, 2), -1, F(-1, 2), 0, F(1, 2), 1, F(3, 2), 2)),
                     (0, 2, 0, -2, 0, 2, 0, -2, 0))),
    "try4": dict(zip(map(F, (-2, F(-3, 2), -1, F(-1, 2), 0, F(1, 2), 1, F(3, 2), 2)),
                     (1, 0, -1, 0, 1, 0, -1, 0, 1))),
}


def text(node):
    return "".join(node.itertext()).strip()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate key: " + key)
            result[key] = value
        return result
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def local(relative):
    path = (BASE / relative).resolve()
    if not path.is_relative_to(BASE):
        raise ValueError("path escapes language directory")
    return path


def image_name(number):
    return "CNX_IntAlg_Figure_03_06_" + number + "_img_new.jpg"


def structure(node):
    return (node.tag, tuple(sorted(node.attrib.items())), (node.text or "").strip(),
            tuple((structure(child), (child.tail or "").strip()) for child in node))


def math_text(node):
    if node.tag == M + "mfrac":
        return "(" + math_text(node[0]) + ")/(" + math_text(node[1]) + ")"
    if node.tag == M + "mspace":
        return ""
    if node.tag.split("}")[-1] not in {"math", "mrow", "mi", "mn", "mo", "mtext"}:
        raise ValueError("unsupported MathML: " + node.tag)
    return (node.text or "") + "".join(math_text(n) + (n.tail or "") for n in node)


def normalized(value):
    return re.sub(r"\s+", "", value).replace("−", "-").rstrip(".,")


def maths(node):
    return [normalized(math_text(n)) for n in node.iter(M + "math")]


def math_parts(node):
    result = {}
    part = None
    for child in node:
        if child.tag == C + "span" and child.get("class") == "token":
            part = chr(ord("a") + ord(text(child)) - ord("ⓐ"))
            result[part] = []
        elif child.tag == M + "math":
            if part is None:
                raise ValueError("unlabeled component")
            result[part].append(normalized(math_text(child)))
    return result


def rational(expression, pi=False):
    expression = normalized(expression)
    if pi:
        if "π" not in expression and expression not in {"0", "(0)"}:
            raise ValueError("nonzero pi coordinate lacks pi")
        if expression.count("π") > 1:
            raise ValueError("coordinate must be a rational multiple of one pi")
        expression = re.sub(r"(?<=[0-9)])(?=π)", "*", expression).replace("π", "p")
    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return F(node.value)
        if pi and isinstance(node, ast.Name) and node.id == "p":
            return F(1)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            return (-1 if isinstance(node.op, ast.USub) else 1) * visit(node.operand)
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                if any(isinstance(n, ast.Name) for n in ast.walk(node.right)):
                    raise ValueError("pi cannot appear in a coefficient denominator")
                return left / right
        raise ValueError("not a supported exact coefficient")
    return visit(ast.parse(expression, mode="eval").body)


def split_top(expression):
    result, start, depth = [], 0, 0
    for i, char in enumerate(expression):
        depth += char == "("
        depth -= char == ")"
        if depth < 0:
            raise ValueError("unbalanced parentheses")
        if char == "," and depth == 0:
            result.append(expression[start:i])
            start = i + 1
    if depth:
        raise ValueError("unbalanced parentheses")
    return result + [expression[start:]]


def inputs(expression):
    expression = normalized(expression).removeprefix("x=")
    return [rational(value, pi=True) for value in split_top(expression)]


def points(expression):
    result = []
    for pair in split_top(normalized(expression)):
        if not (pair.startswith("(") and pair.endswith(")")):
            raise ValueError("ordered pair required")
        x, y = split_top(pair[1:-1])
        result.append((rational(x, pi=True), rational(y)))
    return result


def call(expression, source_correction=False):
    expression = normalized(expression)
    if source_correction:
        expression = expression.replace("f=(", "f(", 1)
    match = re.fullmatch(r"f\((.*)\)(?:=(.+))?", expression)
    if not match:
        raise ValueError("function application required: " + expression)
    return rational(match[1], pi=True), None if match[2] is None else rational(match[2])


def closed_interval(expression):
    value = normalized(expression)
    if not (value.startswith("[") and value.endswith("]")):
        raise ValueError("closed interval required")
    return tuple(rational(v) for v in value[1:-1].split(","))


class Unit14Math(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.xml = local(f"translations/{UNIT}.xml").read_bytes()
        cls.root = ET.fromstring(cls.xml)
        cls.ids = {n.get("id"): n for n in cls.root.iter() if n.get("id")}
        cls.config = read_json(local(f"units/{UNIT}.json"))
        cls.checks = {n.get("data-check"): text(n) for n in cls.root.iter() if n.get("data-check")}
        cls.modules, cls.sources, cls.source_raw, cls.images = {}, {}, {}, {}
        for locale, (archive, prefix, _, module_hash) in PINS.items():
            with zipfile.ZipFile(BASE.parent / archive) as zipped:
                raw = zipped.read(prefix + "modules/m81374/index.cnxml")
                if sha(raw) != module_hash:
                    raise ValueError("actual pinned module hash mismatch")
                root = ET.fromstring(raw)
                cls.modules[locale] = root
                cls.source_raw[locale] = raw
                section = next(n for n in root.iter() if n.get("id") == SECTION)
                cls.sources[locale] = {n.get("id"): n for n in section.iter() if n.get("id")}
                for number, _, _, _ in IMAGES:
                    cls.images[locale, number] = zipped.read(prefix + "media/" + image_name(number))

    def test_01_source_boundary_and_exact_selector_order(self):
        actual = [n.get("data-source") for n in self.root.iter() if n.get("data-source")]
        self.assertEqual(actual, ["A20:m81374#" + sid for sid in SELECTED])
        for locale, source in self.sources.items():
            section = source[SECTION]
            self.assertEqual([n.get("id") for n in list(section)[1:]], list(SELECTED))
            parent = next(n for n in self.modules[locale].iter() if section in list(n))
            index = list(parent).index(section)
            self.assertEqual(parent[index-1].get("id"), "fs-id1167836522816")
            self.assertEqual(parent[index+1].get("id"), "fs-id1167836597228")

    def test_02_all_ids_and_source_ancestor_relationships(self):
        ids = [n.get("id") for n in self.root.iter() if n.get("id")]
        self.assertEqual(len(ids), 57)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(self.sources["en"]), 55)
        for source in self.sources.values():
            self.assertEqual(set(source) - set(self.ids), set())
            self.assertEqual([ident for ident in ids if ident in source], list(source))
            for ident, node in source.items():
                source_descendants = {n.get("id") for n in node.iter() if n.get("id")}
                target_descendants = {n.get("id") for n in self.ids[ident].iter() if n.get("id")}
                self.assertEqual(source_descendants, target_descendants & set(source))
        self.assertNotIn("data-source", self.ids[SECTION].attrib)

    def test_03_source_classification_and_thirty_components(self):
        self.assertEqual({key: self.config[key] for key in (
            "source_count", "translated_worked_examples", "translated_definitions",
            "translated_practice_items", "translated_resource_notes", "original_practice_items")},
            dict(source_count=12, translated_worked_examples=2, translated_definitions=0,
                 translated_practice_items=4, translated_resource_notes=1, original_practice_items=0))
        self.assertEqual(self.config["question_ids"], [])
        section = self.sources["en"][SECTION]
        self.assertEqual(sum(n.tag == C+"example" for n in section), 2)
        self.assertEqual(sum(n.get("class") == "try" for n in section), 4)
        self.assertEqual(len(list(section.iter(C+"solution"))), 6)
        self.assertEqual(len([n for n in self.root.iter() if n.get("class") == "solution"]), 6)
        for _, _, qid, aid, _, _ in WAVES:
            self.assertEqual(set(math_parts(self.sources["en"][qid])), set("abcdefgh"))
            self.assertEqual(set(math_parts(self.sources["en"][aid])), set("abcdefgh"))
            for ident in (qid, aid):
                self.assertEqual(re.findall(r"\(([a-h])\)", text(self.ids[ident])), list("abcdefgh"))
        self.assertEqual(3*2 + len(WAVES)*8, 30)

    def test_04_all_fiftyeight_mathml_trees_match_between_locales(self):
        en = [structure(n) for n in self.sources["en"][SECTION].iter(M+"math")]
        other = [structure(n) for n in self.sources["id"][SECTION].iter(M+"math")]
        self.assertEqual(len(en), 58)
        self.assertEqual(en, other)

    def test_05_six_closed_intervals_from_pixels_and_source_answers(self):
        for key, sid, domain, value_range in FINITE:
            self.assertEqual(closed_interval(self.checks[key+"-domain"]), domain)
            self.assertEqual(closed_interval(self.checks[key+"-range"]), value_range)
            for source in self.sources.values():
                answer = source[sid].find(".//"+C+"solution")
                actual = [closed_interval(value) for value in maths(answer)]
                self.assertEqual(actual, [domain, value_range])

    def test_06_nine_evaluations_use_actual_inputs_and_pixel_values(self):
        total = 0
        for key, _, qid, aid, _, _ in WAVES:
            for part in "abc":
                x, empty = call(self.checks[key+"-question-"+part])
                self.assertIsNone(empty)
                answer_x, answer_y = call(self.checks[key+"-answer-"+part])
                self.assertEqual(x, answer_x)
                self.assertEqual(answer_y, PIXEL_NODES[key][x])
                for source in self.sources.values():
                    qmath = math_parts(source[qid])[part][-1]
                    self.assertEqual(call(qmath), (x, None))
                    amat = [v for v in math_parts(source[aid])[part] if v.startswith("f")][-1]
                    self.assertEqual(call(amat, source_correction=key == "try3"), (x, answer_y))
                total += 1
        self.assertEqual(total, 9)

    def test_07_all_visible_zeros_and_fourteen_x_intercepts(self):
        count = 0
        for key, _, _, aid, _, _ in WAVES:
            expected = [x for x, y in PIXEL_NODES[key].items() if y == 0]
            self.assertEqual(inputs(self.checks[key+"-answer-d"]), expected)
            actual_pairs = points(self.checks[key+"-answer-e"])
            self.assertEqual(actual_pairs, [(x, 0) for x in expected])
            count += len(actual_pairs)
            for source in self.sources.values():
                parts = math_parts(source[aid])
                self.assertEqual(inputs(parts["d"][-1]), expected)
                self.assertEqual(points(parts["e"][-1]), actual_pairs)
        self.assertEqual(count, 14)
        self.assertEqual(points(self.checks["example2-zero-points"]),
                         points(self.checks["example2-answer-e"]))

    def test_08_y_intercepts_ranges_and_real_domains(self):
        for key, _, _, aid, amplitude, _ in WAVES:
            self.assertEqual(points(self.checks[key+"-answer-f"]), [(0, PIXEL_NODES[key][F(0)])])
            self.assertEqual(closed_interval(self.checks[key+"-answer-h"]), (-amplitude, amplitude))
            self.assertEqual(normalized(self.checks[key+"-answer-g"]), "(-∞,∞)")
            for source in self.sources.values():
                parts = math_parts(source[aid])
                self.assertEqual(points(parts["f"][-1]), points(self.checks[key+"-answer-f"]))
                self.assertEqual(parts["g"][-1], "(-∞,∞)")
                self.assertEqual(closed_interval(parts["h"][-1]), (-amplitude, amplitude))

    def test_09_preserved_question_window_distinctions(self):
        for key, _, qid, _, _, _ in WAVES:
            self.assertEqual(normalized(self.checks[key+"-question-d"]), "f(x)=0")
            for source in self.sources.values():
                paragraph = source[qid]
                self.assertEqual("[" in text(paragraph), key != "example2")
            if key != "example2":
                value = normalized(self.checks[key+"-question-window"])
                self.assertEqual(value[0]+value[-1], "[]")
                self.assertEqual(inputs(value[1:-1]), [F(-2), F(2)])
        self.assertEqual(normalized(self.checks["example2-shown-window"]), "[-2π,2π]")

    def test_10_periodic_extension_is_explicit_and_not_finite_sample_proof(self):
        for key, _, _, _, _, phase in WAVES:
            family = normalized(self.checks[key+"-all-intercepts"])
            self.assertEqual(family, "(nπ,0),n∈ℤ" if phase == 0 else "(π/2+nπ,0),n∈ℤ")
            # Enumerate this affine family only in the requested window. The
            # universal continuation is a stated premise, not proven by this loop.
            visible = [F(n)+phase for n in range(-3, 3) if -2 <= F(n)+phase <= 2]
            self.assertEqual(visible, inputs(self.checks[key+"-answer-d"]))
        self.assertEqual(normalized(self.checks["example2-all-zeros"]), "x=nπ,n∈ℤ")
        for locale, source in self.sources.items():
            alt = source["fs-id1167836539761"].get("alt")
            self.assertIn("The line extends infinitely" if locale == "en" else "Garis ini memanjang", alt)
            self.assertNotIn("pattern" if locale == "en" else "Pola", alt)
        # Regression for the independently reported 025 attribution issue.
        alt = self.ids["fs-id1167836539761"].find("img").get("alt")
        self.assertNotIn("स्रोताच्या वर्णनानुसार तोच नमुना", alt)
        additions = " ".join(text(n) for n in self.ids[SELECTED[9]].iter()
                             if n.get("data-kind") == "original")
        self.assertIn("गृहीत", additions)
        self.assertIn("केवळ काही बिंदू", text(self.root))

    def test_11_malformed_f_equal_application_is_disclosed_not_silently_rewritten(self):
        for source in self.sources.values():
            parts = math_parts(source["fs-id1167836550513"])
            for part in "bc":
                self.assertTrue(parts[part][0].startswith("f=("))
        solution = self.ids["fs-id1167829753187"]
        self.assertIn("दुरुस्त", text(solution.find("h4")))
        additions = " ".join(text(n) for n in solution if n.get("data-kind") == "original")
        for token in ("f = (π/2) = 2", "f = (−3π/2) = 2", "पहिले समानचिन्ह", "संख्यात्मक उत्तरे बदललेली नाहीत"):
            self.assertIn(token, additions)

    def test_12_symbolic_intervals_fractional_pi_and_exact_54_regressions(self):
        self.assertEqual(normalized(self.checks["interval-closed"]), "[a,b]")
        self.assertEqual(normalized(self.checks["interval-real"]), "(-∞,∞)")
        for key, expected in (("pi-half", F(1, 2)), ("pi-three-halves", F(3, 2))):
            left, right = self.checks[key].split("=")
            self.assertEqual(rational(left, pi=True), expected)
            self.assertEqual(rational(right, pi=True), expected)
        nodes = [n for n in self.root.iter() if n.get("data-check")]
        self.assertEqual(len(nodes), 54)
        self.assertEqual(len(self.checks), 54)
        self.assertEqual(self.checks, self.config["expected_math"])
        covered = {"interval-closed", "interval-real", "pi-half", "pi-three-halves",
                   "example2-zero-points", "example2-shown-window", "example2-all-zeros"}
        for key, *_ in FINITE:
            covered.update((key+"-domain", key+"-range"))
        for key, *_ in WAVES:
            covered.update(key+"-question-"+p for p in "abcd")
            covered.update(key+"-answer-"+p for p in "abcdefgh")
            covered.add(key+"-all-intercepts")
            if key != "example2":
                covered.add(key+"-question-window")
        self.assertEqual(set(self.checks), covered)

    def test_13_all_twelve_pixel_witnesses_and_six_original_assets(self):
        for number, media_id, size, expected in IMAGES:
            for locale in PINS:
                data = self.images[locale, number]
                self.assertEqual(len(data), size)
                self.assertEqual(sha(data), expected)
                self.assertEqual(self.sources[locale][media_id].find(C+"image").get("src"),
                                 "../../media/"+image_name(number))
            self.assertEqual(self.images["en", number], self.images["id", number])
            img = self.ids[media_id].find("img")
            self.assertEqual(img.get("src"), "asset:"+image_name(number))
            self.assertIn("−6 ते 6", img.get("alt"))
        self.assertEqual(sum(len(raw) for raw in self.images.values()), 693448)
        self.assertEqual(len(list(self.root.iter("img"))), 6)

    def test_14_axis_corrections_and_domain_range_tracing_are_explicit(self):
        for media_id, source_words in (
            ("fs-id1167836538244", "negative 4 to 4"),
            ("fs-id1167833128692", "negative 4 to 5"),
            ("fs-id1167836493218", "negative 4 to 4")):
            self.assertIn(source_words, self.sources["en"][media_id].get("alt"))
            self.assertIn("−6 ते 6", self.ids[media_id].find("img").get("alt"))
        self.assertEqual(text(self.root).count("वर्णन-दुरुस्ती:"), 3)
        self.assertIn("उभ्या दिशेने", text(self.ids[SELECTED[2]]))
        self.assertIn("आडव्या दिशेने", text(self.ids[SELECTED[3]]))
        self.assertIn("अक्षांवरील संपूर्ण खुणा", text(self.root))
        self.assertIn("मोठे y-मूल्य उजव्या टोकावरच असेल असे नाही", text(self.root))

    def test_15_six_source_answer_links_and_all_navigation_and_urls(self):
        anchors = list(self.root.iter("a"))
        links = [n.get("href") for n in anchors if n.get("href", "").startswith("#")]
        self.assertEqual(len(links), 17)
        self.assertTrue(all(value[1:] in self.ids for value in links))
        self.assertTrue(all(text(n) for n in anchors))
        for exercise in self.sources["en"][SECTION].iter(C+"exercise"):
            problem = exercise.find(C+"problem").get("id")
            answer = exercise.find(C+"solution").get("id")
            for start, end in ((problem, answer), (answer, problem)):
                self.assertIn("#"+end, [a.get("href") for a in self.ids[start].iter("a")])
        for source in self.sources.values():
            outgoing = list(source[SECTION].iter(C+"link"))
            self.assertEqual([n.attrib for n in outgoing], [{"url": "https://openstax.org/l/37domainrange"}])
        external = [n.get("href") for n in anchors if not n.get("href", "").startswith("#")]
        self.assertEqual(len(external), 5)
        self.assertIn("https://openstax.org/l/37domainrange", external)
        self.assertTrue(all(re.fullmatch(r"https://[^\s/]+/[^\s]*", value) for value in external))

    def test_16_markup_unicode_terms_and_settled_component_notices(self):
        links, external, images = build_unit.validate_markup(self.root, self.config["assets"])
        self.assertEqual((len(links), external, len(images)), (17, 5, 6))
        self.assertEqual(self.root.attrib, {"id": UNIT, "lang": "mr-Deva-IN"})
        value = self.xml.decode("utf8")
        self.assertEqual(value, unicodedata.normalize("NFC", value))
        self.assertNotIn("\ufffd", value)
        for term in self.config["required_terms"]:
            self.assertIn(term, text(self.root))
        credits = text(self.ids["credits"])
        for token in ("CC BY-NC-SA 4.0", "OpenStax", "Lynn Marecek", "Andrea Honeycutt Mathis",
                      "तृतीय-पक्षांच्या स्वतंत्र सूचना", "प्रशिक्षण", "पुनरावलोकन"):
            self.assertIn(token, credits)
        self.assertIn("https://creativecommons.org/licenses/by-nc-sa/4.0/",
                      [a.get("href") for a in self.ids["credits"].iter("a")])

    def test_17_freeze_all_fragments_images_and_39_witnesses(self):
        lock = read_json(local(f"provenance/{UNIT}.lock.json"))
        self.assertEqual([n["target_id"] for n in lock["source_selections"]], list(SELECTED))
        self.assertEqual(len(lock["witnesses"]), 39)
        for witness in lock["witnesses"]:
            raw = local(witness["path"]).read_bytes()
            self.assertEqual((len(raw), sha(raw)), (witness["bytes"], witness["sha256"]))
        for selection in lock["source_selections"]:
            self.assertEqual(selection["locator"], "A20:m81374#"+selection["target_id"])
            for item in selection["sources"]:
                locale = item["locale"]
                archive, prefix, archive_sha, module_sha = PINS[locale]
                self.assertEqual((item["archive"], item["archive_sha256"], item["module_sha256"]),
                                 (archive, archive_sha, module_sha))
                self.assertEqual(item["member"], prefix+"modules/m81374/index.cnxml")
                raw = local(item["fragment_path"]).read_bytes()
                self.assertEqual(sha(raw), item["fragment_sha256"])
                self.assertEqual(structure(ET.fromstring(raw)), structure(self.sources[locale][selection["target_id"]]))
        self.assertEqual(len(lock["source_images"]), 12)
        self.assertEqual(set(self.config["assets"]), {image_name(row[0]) for row in IMAGES})
        for number, _, size, expected in IMAGES:
            asset = self.config["assets"][image_name(number)]
            self.assertEqual(asset["path"], f"assets/{UNIT}/"+image_name(number))
            self.assertEqual((asset["mime"], asset["sha256"]), ("image/jpeg", expected))
            self.assertEqual(local(asset["path"]).read_bytes(), self.images["en", number])
        for item in lock["source_images"]:
            number = Path(item["member"]).name.split("_")[5]
            self.assertEqual(sha(self.images[item["locale"], number]), item["sha256"])

    def test_18_existing_build_receipt_is_current_structural_evidence_only(self):
        receipt = read_json(local(f"qa/{UNIT}-build-receipt.json"))
        self.assertEqual((receipt["unit"], receipt["locale"], receipt["result"]), (UNIT, "mr-Deva-IN", "PASS"))
        for field, relative in (("source_sha256", f"translations/{UNIT}.xml"),
                                ("config_sha256", f"units/{UNIT}.json"),
                                ("provenance_lock_sha256", f"provenance/{UNIT}.lock.json"),
                                ("html_sha256", f"output/{UNIT}.html")):
            self.assertEqual(receipt[field], sha(local(relative).read_bytes()))
        for item in receipt["stylesheet_files"]:
            self.assertEqual(item["sha256"], sha(local(item["path"]).read_bytes()))
        for field, expected in (("selected_source_blocks", 12), ("displayed_math_regressions", 54),
                                ("unique_ids", 57), ("embedded_image_count", 6),
                                ("embedded_image_raw_bytes", 346724), ("pinned_witnesses_checked", 39)):
            self.assertEqual(receipt[field], expected)
        self.assertIn("visual browser QA", receipt["not_claimed"])
        self.assertIn("independent mathematical proof", receipt["not_claimed"])

    def test_19_exact_parser_rejects_execution_and_bad_coordinate_grouping(self):
        self.assertEqual(rational("(3/2)π", pi=True), F(3, 2))
        self.assertEqual(rational("-3π/2", pi=True), F(-3, 2))
        self.assertEqual(points("(-(3π)/(2),0),(π/2,0)"), [(F(-3, 2), F(0)), (F(1, 2), F(0))])
        for value in ("__import__('os')", "p.real", "p[0]", "π+1", "1/2", "1/π", "π*π", "π/π"):
            with self.assertRaises((ValueError, SyntaxError)):
                rational(value, pi=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
