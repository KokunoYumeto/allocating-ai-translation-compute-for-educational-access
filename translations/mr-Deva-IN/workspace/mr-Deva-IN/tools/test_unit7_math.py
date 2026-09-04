"""Independent source/structure and elementary-math QA for MR-BRIDGE-007.

Run with python -B. Uses stdlib only; reads pinned members without extraction,
downloads, builds, or file writes. Text assertions guard reviewed distinctions;
they do not claim Marathi-native/teacher review, OCR, or browser visual QA.
"""
import ast
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import unittest
import xml.etree.ElementTree as ET
import zipfile


BASE = Path(__file__).resolve().parents[1]
UNIT = "MR-BRIDGE-007"
C = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
WRAPPER = "fs-id1167829756260"
SELECTED = (
    "fs-id1167829756267", "fs-id1167829878971", "fs-id1167833054114",
    "fs-id1167836755014", "fs-id1167829783756", "fs-id1167829808856",
    "fs-id1167833327007", "fs-id1167833327015", "fs-id1167833382803",
)
EXERCISES = SELECTED[:4]
SELF_CHECK = SELECTED[4]
DEFINITIONS = SELECTED[5:]
IMAGE = "CNX_IntAlg_Figure_03_05_213_img_new.jpg"
MODULE_PINS = {
    "en": {
        "archive": "downloads/mr-Deva-IN/releases/A20-canonical.zip",
        "archive_sha256": "effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917",
        "prefix": "osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/",
        "module_sha256": "2b606026c2b34cdf69acfa29bfe4b90abdb6961a322a78c7ec20107e0948b05c",
        "image_sha256": "4571cd8939329c873f1251bb96128b1dbeec19fcb18fd8de736432b9f00304c3",
        "image_bytes": 53026,
    },
    "id": {
        "archive": "downloads/mr-Deva-IN/releases/A20-v0.3.0-source.zip",
        "archive_sha256": "a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7",
        "prefix": "source/",
        "module_sha256": "e9e593b31587995170c520b9175f2e0c0cb335282c951bb1d769f775344311ee",
        "image_sha256": "4960c2832d316917c88d326b3910e5255cde79905944697434cbc47e1e46c213",
        "image_bytes": 260999,
    },
}
PROMPTS = (
    "संबंध आणि फलन यांतील फरक आपल्या शब्दांत स्पष्ट करा.",
    "प्रांत आणि मूल्यसंच म्हणजे काय, ते आपल्या शब्दांत स्पष्ट करा.",
    "प्रत्येक संबंध फलन आहे का? प्रत्येक फलन संबंध आहे का?",
    "फलनाचे मूल्य कसे काढता?",
)
EXPECTED_MATH = {
    "writing-domain-example": "{(2, 5), (4, 5)}",
    "writing-domain": "{2, 4}",
    "writing-range": "{5}",
    "writing-not-function": "{(1, 2), (1, 3)}",
    "writing-function-formula": "f(x) = 2x + 3",
    "writing-function-value": "f(−2) = 2(−2) + 3 = −1",
}
HEADERS = ("मला हे करता येते…", "आत्मविश्वासाने", "थोड्या मदतीने", "नाही—हे मला समजलेले नाही!")
OBJECTIVES = (
    "संबंधाचा प्रांत आणि मूल्यसंच शोधणे.",
    "संबंध फलन आहे का ते ठरवणे.",
    "फलनाचे मूल्य काढणे.",
)


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


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def local(relative):
    result = (BASE / relative).resolve()
    if not result.is_relative_to(BASE):
        raise ValueError("witness escapes language directory")
    return result


def structure(node):
    """Compare parsed source nodes without depending on namespace prefixes."""
    return (node.tag, sorted(node.attrib.items()), node.text,
            [(structure(child), child.tail) for child in node])


def is_function(pairs):
    outputs = {}
    for domain, value in pairs:
        outputs.setdefault(domain, set()).add(value)
    return all(len(values) == 1 for values in outputs.values())


def arithmetic(display, x=None):
    """Tiny integer interpreter for the original linear example; never eval."""
    normalized = display.replace("−", "-")
    normalized = re.sub(r"(?<=\d)(?=x|\()", "*", normalized)

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return node.value
        if isinstance(node, ast.Name) and node.id == "x" and x is not None:
            return x
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            value = visit(node.operand)
            return -value if isinstance(node.op, ast.USub) else value
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
        raise ValueError("unsupported example arithmetic")

    return visit(ast.parse(normalized.strip(), mode="eval").body)


class Unit7RegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (BASE / f"translations/{UNIT}.xml").read_bytes()
        cls.root = ET.fromstring(cls.raw)
        cls.config = read_json(BASE / f"units/{UNIT}.json")
        cls.lock = read_json(BASE / f"provenance/{UNIT}.lock.json")
        cls.ids = {node.get("id"): node for node in cls.root.iter() if node.get("id")}
        cls.checks = {node.get("data-check"): text(node) for node in cls.root.iter()
                      if node.get("data-check")}
        cls.fragments, cls.modules, cls.images = {}, {}, {}
        for selection in cls.lock["source_selections"]:
            for source in selection["sources"]:
                key = (selection["target_id"], source["locale"])
                if key in cls.fragments:
                    raise ValueError("duplicate source fragment")
                raw = local(source["fragment_path"]).read_bytes()
                if sha(raw) != source["fragment_sha256"]:
                    raise ValueError("frozen source fragment hash mismatch")
                cls.fragments[key] = ET.fromstring(raw)
        for locale, pin in MODULE_PINS.items():
            with zipfile.ZipFile(BASE.parent / pin["archive"]) as archive:
                member = pin["prefix"] + "modules/m81373/index.cnxml"
                if archive.namelist().count(member) != 1:
                    raise ValueError("missing/ambiguous pinned source module")
                module = archive.read(member)  # Only selected members; CRC checked.
                if sha(module) != pin["module_sha256"]:
                    raise ValueError("pinned source module hash mismatch")
                cls.modules[locale] = ET.fromstring(module)
                image_member = pin["prefix"] + "media/" + IMAGE
                if archive.namelist().count(image_member) != 1:
                    raise ValueError("missing/ambiguous pinned source image")
                cls.images[locale] = archive.read(image_member)

    def test_identity_nfc_unique_ids_and_exact_counts(self):
        self.assertEqual(self.root.get("id"), UNIT)
        self.assertEqual(self.root.get("lang"), "mr-Deva-IN")
        decoded = self.raw.decode("utf-8")
        self.assertEqual(unicodedata.normalize("NFC", decoded), decoded)
        self.assertNotIn("\ufffd", decoded)
        self.assertEqual(len(self.ids), 33)
        self.assertEqual(len(self.ids), sum(bool(n.get("id")) for n in self.root.iter()))
        for key, value in {"source_count": 9, "translated_practice_items": 4,
                           "translated_definitions": 4, "translated_worked_examples": 0,
                           "translated_resource_notes": 0, "original_practice_items": 0}.items():
            self.assertEqual(self.config[key], value, key)
        self.assertEqual(self.config["question_ids"], [])
        self.assertEqual(len(self.config["required_terms"]), 9)
        for term in self.config["required_terms"]:
            self.assertIn(term, text(self.root))

    def test_exact_nine_ordered_locators_and_both_locales(self):
        expected = ["A20:m81373#" + sid for sid in SELECTED]
        self.assertEqual([n.get("data-source") for n in self.root.iter() if n.get("data-source")], expected)
        self.assertEqual([s["locator"] for s in self.lock["source_selections"]], expected)
        self.assertEqual([s["target_id"] for s in self.lock["source_selections"]], list(SELECTED))
        self.assertEqual(set(self.fragments), {(sid, locale) for sid in SELECTED for locale in ("en", "id")})
        for selection in self.lock["source_selections"]:
            self.assertEqual([s["locale"] for s in selection["sources"]], ["en", "id"])
            for source in selection["sources"]:
                pin = MODULE_PINS[source["locale"]]
                for field in ("archive", "archive_sha256", "module_sha256"):
                    self.assertEqual(source[field], pin[field])
                self.assertEqual(source["member"], pin["prefix"] + "modules/m81373/index.cnxml")

    def test_all_frozen_fragments_equal_actual_pinned_module_nodes(self):
        for locale, module in self.modules.items():
            original = {n.get("id"): n for n in module.iter() if n.get("id")}
            for sid in SELECTED:
                with self.subTest(locale=locale, source=sid):
                    self.assertEqual(structure(self.fragments[(sid, locale)]), structure(original[sid]))

    def test_all_24_selected_ids_plus_uncounted_writing_wrapper_in_order(self):
        target_ids = [n.get("id") for n in self.root.iter() if n.get("id", "").startswith("fs-id")]
        for locale in ("en", "id"):
            original = [n.get("id") for sid in SELECTED for n in self.fragments[(sid, locale)].iter() if n.get("id")]
            self.assertEqual(len(original), 24)
            self.assertEqual(len(set(original)), 24)
            self.assertEqual(target_ids, [WRAPPER] + original)
            wrapper = next(n for n in self.modules[locale].iter() if n.get("id") == WRAPPER)
            self.assertEqual([n.get("id") for n in wrapper if n.tag == C + "exercise"], list(EXERCISES))
            self.assertEqual(text(wrapper.find(C + "title")), "Writing Exercises" if locale == "en" else "Latihan Menulis")
        self.assertEqual(len(target_ids), 25)
        self.assertIsNone(self.ids[WRAPPER].get("data-source"))
        self.assertEqual(text(self.ids[WRAPPER].find("h2")), "लेखी सराव")
        for duplicate in ("fs-id1167833175472", "fs-id1167833175475"):
            self.assertNotIn(duplicate, self.ids)

    def test_four_writing_prompts_preserve_problem_and_paragraph_ids(self):
        for sid, expected in zip(EXERCISES, PROMPTS):
            target = self.ids[sid]
            self.assertEqual(target.get("data-kind"), "translation")
            for locale in ("en", "id"):
                source = self.fragments[(sid, locale)]
                self.assertEqual(source.tag, C + "exercise")
                self.assertEqual(len(source.findall(C + "problem")), 1)
                problem = source.find(C + "problem")
                self.assertEqual(len(problem.findall(C + "para")), 1)
                self.assertIn("problem", self.ids[problem.get("id")].get("class", "").split())
                self.assertEqual(text(self.ids[problem.find(C + "para").get("id")]), expected)
                self.assertEqual(list(source.iter(C + "solution")), [])

    def test_four_sample_answers_are_original_not_source_or_new_questions(self):
        answers = [n for n in self.root.iter() if "solution" in n.get("class", "").split()]
        self.assertEqual(len(answers), 4)
        for sid in EXERCISES:
            answer = self.ids["mr-answer-" + sid]
            self.assertEqual(answer.get("data-kind"), "original")
            self.assertEqual(text(answer.find("h4")), "नव्याने लिहिलेले नमुना उत्तर")
            self.assertIsNone(answer.get("data-source"))
            self.assertIn(answer, list(self.ids[sid]))
        notice = self.ids[WRAPPER].find("p")
        self.assertEqual(notice.get("data-kind"), "original")
        self.assertIn("मूळ इंग्रजी किंवा इंडोनेशियन स्रोतात या प्रश्नांची उत्तरे दिलेली नाहीत", text(notice))
        self.assertIn("योग्य अर्थ सांगणारी इतर उत्तरेही चालतील", text(notice))

    def test_four_answer_navigation_pairs_and_all_twelve_local_links(self):
        links = [a for a in self.root.iter("a") if a.get("href", "").startswith("#")]
        self.assertEqual(len(links), 12)
        for link in links:
            self.assertIn(link.get("href")[1:], self.ids)
            self.assertTrue(text(link))
        for sid in EXERCISES:
            problem_id = self.fragments[(sid, "en")].find(C + "problem").get("id")
            answer_id = "mr-answer-" + sid
            for start, end in ((problem_id, answer_id), (answer_id, problem_id)):
                self.assertIn("#" + end, [a.get("href") for a in self.ids[start].iter("a")])

    def test_exact_six_math_checks_only_inside_original_answers(self):
        self.assertEqual(self.checks, EXPECTED_MATH)
        self.assertEqual(self.config["expected_math"], EXPECTED_MATH)
        nodes = [n for n in self.root.iter() if n.get("data-check")]
        self.assertEqual(len(nodes), 6)
        authored = {id(n) for sid in EXERCISES for n in self.ids["mr-answer-" + sid].iter()}
        self.assertTrue(all(id(n) in authored for n in nodes))

    def test_original_finite_set_examples_and_unique_output_condition(self):
        pairs = ast.literal_eval(self.checks["writing-domain-example"])
        self.assertEqual(pairs, {(2, 5), (4, 5)})
        self.assertEqual({x for x, _ in pairs}, ast.literal_eval(self.checks["writing-domain"]))
        self.assertEqual({y for _, y in pairs}, ast.literal_eval(self.checks["writing-range"]))
        self.assertTrue(is_function(pairs), "different inputs may share one output")
        counterexample = ast.literal_eval(self.checks["writing-not-function"])
        self.assertEqual(counterexample, {(1, 2), (1, 3)})
        self.assertFalse(is_function(counterexample))
        self.assertIn("वेगवेगळ्या आदानांना एकच प्रदान मिळणे मात्र मान्य आहे", text(self.ids["mr-answer-" + EXERCISES[0]]))
        self.assertIn("मूल्यसंचात घोषित सहप्रांतातील सर्व घटक असतीलच असे नाही", text(self.ids["mr-answer-" + EXERCISES[1]]))
        answer3 = text(self.ids["mr-answer-" + EXERCISES[2]])
        self.assertIn("पहिल्या प्रश्नाचे उत्तर नाही", answer3)
        self.assertIn("दुसऱ्या प्रश्नाचे उत्तर होय", answer3)

    def test_original_linear_example_parentheses_domain_and_all_chain_steps(self):
        lhs, rhs = self.checks["writing-function-formula"].split("=")
        self.assertEqual(lhs.strip(), "f(x)")
        call, substituted, answer = self.checks["writing-function-value"].split("=")
        self.assertEqual(call.strip(), "f(−2)")
        expected = arithmetic(rhs, x=-2)
        self.assertEqual(expected, -1)
        self.assertEqual(arithmetic(substituted), expected)
        self.assertEqual(arithmetic(answer), expected)
        prose = text(self.ids["mr-answer-" + EXERCISES[3]])
        for token in ("प्रांतात", "कंसात", "सर्व वास्तविक संख्यांवर", "जोड्यांनी, तक्त्याने किंवा बाणांनी", "गुणाकार नाही"):
            self.assertIn(token, prose)

    def test_four_glossary_definitions_keep_source_meanings_and_xy_roles(self):
        glossary = self.ids["glossary"]
        self.assertEqual([n.get("id") for n in glossary.findall("section")], list(DEFINITIONS))
        expected_titles = ("संबंधाचा प्रांत", "फलन", "प्रतिचित्रण", "संबंधाचा मूल्यसंच")
        for sid, title in zip(DEFINITIONS, expected_titles):
            self.assertEqual(text(self.ids[sid].find("h3")), title)
            self.assertEqual(self.ids[sid].get("data-kind"), "translation")
            for locale in ("en", "id"):
                source = self.fragments[(sid, locale)]
                self.assertEqual(source.tag, C + "definition")
                meaning = source.find(C + "meaning")
                self.assertEqual(self.ids[meaning.get("id")].tag, "p")
        self.assertIn("x-मूल्यांचा संच", text(self.ids[DEFINITIONS[0]]))
        self.assertIn("y-मूल्यांचा संच", text(self.ids[DEFINITIONS[3]]))
        self.assertIn("प्रत्येक घटकाला मूल्यसंचातील नेमका एक घटक", text(self.ids[DEFINITIONS[1]]))
        self.assertIn("बाण प्रांतातील घटक आणि मूल्यसंचातील घटक यांच्या जोड्या दाखवतात", text(self.ids[DEFINITIONS[2]]))

    def test_self_check_keeps_exact_two_personal_prompts_without_answers(self):
        section = self.ids[SELF_CHECK]
        prompt_ids = ("fs-id1167829783762", "fs-id1167836607297")
        expected = (
            "(a) सराव पूर्ण केल्यानंतर, या विभागातील उद्दिष्टे तुम्हाला कितपत साध्य झाली आहेत याचे मूल्यमापन करण्यासाठी ही तपासणी-यादी वापरा.",
            "(b) तपासणी-यादी पाहिल्यानंतर, पुढील विभागासाठी तुमची चांगली तयारी झाली आहे असे तुम्हाला वाटते का? का किंवा का नाही?",
        )
        self.assertEqual([p.get("id") for p in section.findall("p") if p.get("id")], list(prompt_ids))
        self.assertEqual([text(self.ids[sid]) for sid in prompt_ids], list(expected))
        for locale in ("en", "id"):
            source = self.fragments[(SELF_CHECK, locale)]
            self.assertEqual([p.get("id") for p in source.findall(C + "para")], list(prompt_ids))
            self.assertEqual([text(p.find(C + "span")) for p in source.findall(C + "para")], ["ⓐ", "ⓑ"])
        self.assertEqual([n for n in section.iter() if "solution" in n.get("class", "").split()], [])
        self.assertEqual([n for n in section.iter() if n.get("id", "").startswith("mr-answer-")], [])
        self.assertIn("येथे तुमच्यावतीने तयार असल्याची खूण केलेली नाही", text(section))

    def test_exact_four_by_four_accessible_checklist_and_nine_blank_cells(self):
        table = self.ids["mr-checklist"]
        self.assertEqual(table.get("data-kind"), "adaptation")
        self.assertEqual(len(list(table.iter("tr"))), 4)
        headers = table.findall("./thead/tr/th")
        self.assertEqual([text(n) for n in headers], list(HEADERS))
        self.assertTrue(all(n.get("scope") == "col" for n in headers))
        rows = table.findall("./tbody/tr")
        self.assertEqual(len(rows), 3)
        for row, objective in zip(rows, OBJECTIVES):
            self.assertEqual(len(row), 4)
            self.assertEqual([n.tag for n in row], ["th", "td", "td", "td"])
            self.assertEqual(row[0].get("scope"), "row")
            self.assertEqual(text(row[0]), objective)
            self.assertEqual([text(n) for n in row.findall("td")], ["□", "□", "□"])
        self.assertEqual(text(table).count("□"), 9)
        for node in self.ids[SELF_CHECK].iter():
            self.assertNotIn(node.tag, ("input", "select", "option", "button", "textarea", "script"))
            self.assertFalse({"checked", "selected", "aria-checked", "value"} & node.attrib.keys())
        for checked in ("☑", "☒", "✓", "✔", "✗", "✘"):
            self.assertNotIn(checked, text(table))

    def test_single_figure_exact_canonical_bytes_and_distinct_id_review(self):
        self.assertEqual(set(self.config["assets"]), {IMAGE})
        asset = self.config["assets"][IMAGE]
        self.assertEqual(asset["path"], f"assets/{UNIT}/{IMAGE}")
        self.assertEqual(asset["mime"], "image/jpeg")
        self.assertEqual(asset["sha256"], MODULE_PINS["en"]["image_sha256"])
        self.assertEqual(local(asset["path"]).read_bytes(), self.images["en"])
        self.assertNotEqual(self.images["en"], self.images["id"])
        self.assertEqual(len(self.lock["source_images"]), 2)
        for record in self.lock["source_images"]:
            locale = record["locale"]
            pin, raw = MODULE_PINS[locale], self.images[locale]
            self.assertEqual(record["locator"], "A20:m81373#" + SELF_CHECK)
            self.assertEqual(record["member"], pin["prefix"] + "media/" + IMAGE)
            self.assertEqual(record["bytes"], pin["image_bytes"])
            self.assertEqual(len(raw), pin["image_bytes"])
            self.assertEqual(record["sha256"], pin["image_sha256"])
            self.assertEqual(sha(raw), pin["image_sha256"])
            self.assertTrue(raw.startswith(b"\xff\xd8\xff"))
            self.assertTrue(raw.endswith(b"\xff\xd9"))
            if locale == "en":
                self.assertEqual(record["committed_asset"], asset["path"])
            else:
                self.assertNotIn("committed_asset", record)

    def test_image_caption_alt_and_adaptation_do_not_overwrite_source_pixels(self):
        images = list(self.root.iter("img"))
        self.assertEqual(len(images), 1)
        image = images[0]
        self.assertEqual(image.get("src"), "asset:" + IMAGE)
        figure = self.ids["fs-id1167836607305"]
        self.assertIn(image, list(figure))
        for token in ("चार ओळी व चार स्तंभ", "रिकामी", "तीन जागा", "रिकाम्या आहेत"):
            self.assertIn(token, image.get("alt"))
        caption = figure.find("figcaption")
        self.assertEqual(caption.get("data-kind"), "original")
        self.assertIn("मूळ इंग्रजी तपासणी-यादी बदल न करता", text(caption))
        self.assertIn("वजाबाकीची खूण नाही", text(caption))
        self.assertIn("निवडी साठवल्या जात नाहीत", text(self.ids[SELF_CHECK]))
        en_alt = self.fragments[(SELF_CHECK, "en")].find(C + "media").get("alt")
        id_alt = self.fragments[(SELF_CHECK, "id")].find(C + "media").get("alt")
        self.assertIn("no minus I don’t get it!", en_alt)
        self.assertIn("Belum—saya belum memahaminya!", id_alt)

    def test_witness_pins_and_no_omitted_source_math_links_or_extra_media(self):
        witnesses = self.lock["witnesses"]
        self.assertEqual(len(witnesses), 28)
        self.assertEqual(len({w["path"] for w in witnesses}), 28)
        for witness in witnesses:
            raw = local(witness["path"]).read_bytes()
            self.assertEqual(len(raw), witness["bytes"], witness["path"])
            self.assertEqual(sha(raw), witness["sha256"], witness["path"])
        witness_pins = {(w["path"], w["sha256"]) for w in witnesses}
        for selection in self.lock["source_selections"]:
            for source in selection["sources"]:
                self.assertIn((source["fragment_path"], source["fragment_sha256"]), witness_pins)
                self.assertEqual(source["math_sha256"], [])
                self.assertEqual(source["outgoing_urls"], [])
        for locale in ("en", "id"):
            media = []
            for sid in SELECTED:
                fragment = self.fragments[(sid, locale)]
                self.assertEqual(list(fragment.iter(M + "math")), [])
                self.assertEqual(list(fragment.iter(C + "link")), [])
                media.extend(fragment.iter(C + "image"))
            self.assertEqual(len(media), 1)
            self.assertEqual(media[0].get("src"), "../../media/" + IMAGE)
            self.assertEqual(media[0].get("mime-type"), "image/jpeg")


if __name__ == "__main__":
    unittest.main(verbosity=2)
