"""Independent real-source mathematics regressions for MR-BRIDGE-013.

The reviewer did not draft this unit. Requires existing pinned archives, frozen
fragments/assets and ignored source-image review copies. Reads only bounded
members: no downloads, extraction, eval, builds, HTML, browser or PDF access.
Manually inspected pixels are hash-bound, not automatically recognized.
Run: python -B mr-Deva-IN/tools/test_unit13_math.py
"""
from fractions import Fraction as F
import hashlib
import json
from math import isqrt
from pathlib import Path
import re
import unicodedata
import unittest
import xml.etree.ElementTree as E
import zipfile

BASE = Path(__file__).resolve().parents[1]
UNIT = "MR-BRIDGE-013"
C = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SECTION = "fs-id1167836522816"
NEXT = "fs-id1167836386547"
PINS = {
    "translations/MR-BRIDGE-013.xml": "aff28c7c2fe88ea2f638c6a19c5555a043e43bba6f7d67285d46ab20cee6ae06",
    "units/MR-BRIDGE-013.json": "5044fd0797fe0412589b6ad53529770cea8dabc2956c90d975813789962f50b3",
    "provenance/MR-BRIDGE-013.lock.json": "d942abeb3bd8fd0c08439a6d0f4b9622d35e0b4fdd8bc4415b235b900e97629f",
}
MODULES = {
    "en": ("A20-canonical.zip", "osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9",
           "021c29fa9a6ab3d5b06d2ef143a82d2ac818ed25fe6fd44ebf5d7a6be07a123a"),
    "id": ("A20-v0.3.0-source.zip", "source",
           "d89a74aef766afca6a4ac7e1ae720f120d22cc771c11dd7e025c55bca1fabb8e"),
}
FRAGMENT_INVENTORY = "2a1c8af9fb1d0e20b08ea2bb0c00db4eedfedf949c51ca0698a1a746652f9f07"
IMAGE_INVENTORY = "888f705956dd190b02ff5c573b59d6d0aa821bcc518a34bf08bb48f06d5617c9"
MATH_INVENTORY = "83d158f0aa7844053b93879856d63a13a483c900f916398645d14de382291988"
# Source/pixel order, not guessed filenames or numbering.
IMAGE_NUMBERS = ("007", "008", "009a", "301", "302", "010", "011a", "303", "304",
                 "012", "013", "305", "306", "014", "015", "307", "308", "016",
                 "017", "309", "310", "018", "019", "311", "312", "020")
QUESTION_KEYS = ("example1", "try1", "try2", "example2", "try3", "try4",
                 "example3", "try5", "try6", "example4", "try7", "try8",
                 "example5", "try9", "try10", "example6", "try11", "try12")
QUESTION_RULES = ("−2x−4", "−3x−1", "−4x−5", "4", "−2", "3", "x²", "x²",
                  "−x²", "x³", "x³", "−x³", "√x", "√x", "−√x", "|x|", "|x|", "−|x|")
QUESTION_IMAGES = ("009a", "301", "302", "011a", "303", "304", "013", "305",
                   "306", "015", "307", "308", "017", "309", "310", "019", "311", "312")
TABLE_ROWS = (
    ((-2, -7), (-1, -5), (0, -3), (3, 3), (4, 5)),
    ((-3, 9), (-2, 4), (-1, 1), (0, 0), (1, 1), (2, 4), (3, 9)),
    ((-2, -8), (-1, -1), (0, 0), (1, 1), (2, 8)),
    ((0, 0), (1, 1), (4, 2), (9, 3)),
    ((-3, 3), (-2, 2), (-1, 1), (0, 0), (1, 1), (2, 2), (3, 3)),
)
TABLE_RULES = ("2x−3", "x²", "x³", "√x", "|x|")
# Actual printed labels, or explicitly described grid extent where appropriate.
AXIS_TEXT = {
    "007": ("−10 ते 10",), "009a": ("−8 ते 8",), "301": ("−8 ते 8",),
    "302": ("−8 ते 8",), "011a": ("−6 ते 6", "0 ते 10", "जाळी"),
    "303": ("−12 ते 12",), "304": ("−12 ते 12",), "012": ("−12 ते 12",),
    "013": ("−6 ते 6", "−2 ते 10"), "305": ("−4 ते 4", "−2 ते 6", "तक्ता नाही"),
    "306": ("−4 ते 4", "−6 ते 2", "खाली उघडणारा", "तक्ता नाही"),
    "014": ("−4 ते 4", "−2 ते 6"), "015": ("−8 ते 8",), "307": ("−8 ते 8",),
    "308": ("−8 ते 8",), "016": ("−4 ते 4", "खिडकीबाहेर"),
    "017": ("0 ते 10",), "309": ("−2 ते 10", "−2 ते 8"),
    "310": ("−2 ते 10", "−10 ते 2"), "018": ("0 ते 8",),
    "019": ("−4 ते 4", "0 ते 6", "−1"), "311": ("−8 ते 8", "−2 ते 10"),
    "312": ("−6 ते 6", "−8 ते 4"), "020": ("−4 ते 4", "0 ते 6", "−1"),
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def inventory(lines):
    return sha(("\n".join(sorted(lines)) + "\n").encode("utf-8"))


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate JSON key: " + key)
        out[key] = value
    return out


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def text(node):
    return "".join(node.itertext())


def compact(value):
    return re.sub(r"\s+", "", value).replace("-", "−")


def image_number(name):
    match = re.fullmatch(r"CNX_IntAlg_Figure_03_06_(\d+[a-z]?)_img(?:_new)?\.jpg", name)
    if not match:
        raise ValueError(name)
    return match[1]


def shape(node, translate_mtext=False):
    token = "<translated prose>" if translate_mtext and node.tag == M + "mtext" else (node.text or "").strip()
    return node.tag, sorted(node.attrib.items()), token, [
        (shape(child, translate_mtext), (child.tail or "").strip()) for child in node]


def math_text(node):
    """Strict source-MathML renderer, never Python evaluation."""
    tag = node.tag.removeprefix(M)
    if tag in ("mi", "mn", "mo", "mtext"):
        return (node.text or "").strip()
    if tag in ("math", "mrow"):
        return "".join(math_text(child) for child in node)
    if tag == "mspace":
        return ""
    if tag == "msup":
        return math_text(node[0]) + {"2": "²", "3": "³"}[math_text(node[1])]
    if tag == "msqrt":
        return "√" + "".join(math_text(child) for child in node)
    raise ValueError("unsupported mathematical shape: " + tag)


def root_fraction(value):
    """Only exact rational roots; rejecting a nonsquare is not domain exclusion."""
    value = F(value)
    if value < 0:
        raise ValueError("outside real square-root domain")
    a, b = isqrt(value.numerator), isqrt(value.denominator)
    if a*a != value.numerator or b*b != value.denominator:
        raise ValueError("real but not a rational square root")
    return F(a, b)


def value(rule, x):
    x = F(x)
    functions = {
        "2x−3": lambda: 2*x-3, "−2x−4": lambda: -2*x-4,
        "−3x−1": lambda: -3*x-1, "−4x−5": lambda: -4*x-5,
        "4": lambda: F(4), "−2": lambda: F(-2), "3": lambda: F(3),
        "x": lambda: x, "x²": lambda: x*x, "−x²": lambda: -(x*x),
        "x³": lambda: x*x*x, "−x³": lambda: -(x*x*x),
        "√x": lambda: root_fraction(x), "−√x": lambda: -root_fraction(x),
        "|x|": lambda: abs(x), "−|x|": lambda: -abs(x),
    }
    return functions[rule]()


class Unit13Math(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.target_raw = (BASE / "translations" / (UNIT + ".xml")).read_bytes()
        cls.target = E.fromstring(cls.target_raw)
        cls.by_id = {n.get("id"): n for n in cls.target.iter() if n.get("id")}
        cls.config = read_json(BASE / "units" / (UNIT + ".json"))
        cls.lock = read_json(BASE / "provenance" / (UNIT + ".lock.json"))
        cls.modules, cls.module_raw, cls.sections = {}, {}, {}
        for locale, (archive, prefix, pin) in MODULES.items():
            with zipfile.ZipFile(BASE.parent / "downloads/mr-Deva-IN/releases" / archive) as z:
                raw = z.read(prefix + "/modules/m81374/index.cnxml")
            cls.module_raw[locale] = raw
            cls.modules[locale] = E.fromstring(raw)
            cls.sections[locale] = next(n for n in cls.modules[locale].iter() if n.get("id") == SECTION)
        cls.source = cls.sections["en"]
        cls.source_ids = [n.get("id") for n in cls.source.iter() if n.get("id")]
        cls.exercises = list(cls.source.iter(C + "exercise"))
        cls.check_pairs = [(n.get("data-check"), text(n)) for n in cls.target.iter() if n.get("data-check")]
        cls.math = dict(cls.check_pairs)
        cls.images = {image_number(n.get("src")[6:]): n for n in cls.target.iter("img")}
        cls.all_text = text(cls.target)

    def test_01_reviewed_target_bytes_and_locale(self):
        for path, pin in PINS.items():
            self.assertEqual(sha((BASE / path).read_bytes()), pin, path)
        self.assertEqual(self.target.attrib, {"id": UNIT, "lang": "mr-Deva-IN"})
        for raw in [self.target_raw, (BASE / "units" / (UNIT + ".json")).read_bytes()]:
            txt = raw.decode("utf-8")
            self.assertEqual(unicodedata.normalize("NFC", txt), txt)
            self.assertNotIn("\ufffd", txt)

    def test_02_actual_module_boundary(self):
        for locale, (_, _, pin) in MODULES.items():
            self.assertEqual(sha(self.module_raw[locale]), pin)
            source = self.sections[locale]
            content = self.modules[locale].find(C + "content")
            self.assertEqual(list(content)[list(content).index(source)+1].get("id"), NEXT)
            blocks = [n for n in source if n.tag != C + "title"]
            self.assertEqual(len(blocks), 47)
            self.assertEqual(blocks[0].get("id"), "fs-id1167836293187")
            self.assertEqual(blocks[-1].get("id"), "fs-id1167836389848")
            self.assertEqual([n.get("id") for n in blocks],
                             [s["target_id"] for s in self.lock["source_selections"]])
        self.assertEqual(len(list(self.source.iter(M+"math"))), 46)

    def test_03_frozen_fragments_equal_actual_source(self):
        lines = []
        for selection in self.lock["source_selections"]:
            for record in selection["sources"]:
                raw = (BASE / record["fragment_path"]).read_bytes()
                self.assertEqual(sha(raw), record["fragment_sha256"])
                original = next(n for n in self.sections[record["locale"]].iter()
                                if n.get("id") == selection["target_id"])
                self.assertEqual(shape(E.fromstring(raw)), shape(original))
                lines.append(selection["target_id"]+"|"+record["locale"]+"|"+sha(raw))
        self.assertEqual(len(lines), 94)
        self.assertEqual(inventory(lines), FRAGMENT_INVENTORY)
        for record in self.lock["witnesses"]:
            self.assertEqual(sha((BASE / record["path"]).read_bytes()), record["sha256"])
        self.assertEqual(len(self.lock["witnesses"]), 129)

    def test_04_all_original_ids_order_and_ancestry(self):
        ids = [n.get("id") for n in self.target.iter() if n.get("id")]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ids), 170)
        self.assertEqual(len(self.source_ids), 168)
        self.assertEqual([i for i in ids if i in self.source_ids], self.source_ids)
        self.assertEqual([n.get("id") for n in self.sections["id"].iter() if n.get("id")], self.source_ids)
        def ancestors(root):
            parents = {c:p for p in root.iter() for c in p}
            out = {}
            for node in root.iter():
                if node.get("id") not in self.source_ids:
                    continue
                current = node
                while current in parents:
                    current = parents[current]
                    if current.get("id") in self.source_ids:
                        out[node.get("id")] = current.get("id")
                        break
                else:
                    out[node.get("id")] = None
            return out
        self.assertEqual(ancestors(self.target), ancestors(self.source))

    def test_05_source_counts_and_order(self):
        actual = [n.get("data-source") for n in self.target.iter() if n.get("data-source")]
        self.assertEqual(actual, [s["locator"] for s in self.lock["source_selections"]])
        counts = {C+"para":20, C+"figure":1, C+"note":20, C+"example":6}
        for tag, count in counts.items():
            self.assertEqual(sum(n.tag == tag for n in self.source), count)
        for key, count in {"source_count":47, "translated_worked_examples":6,
                           "translated_definitions":8, "translated_practice_items":12,
                           "translated_resource_notes":0, "original_practice_items":0}.items():
            self.assertEqual(self.config[key], count)
        self.assertEqual(self.config["question_ids"], [])
        self.assertEqual(len(self.exercises), 18)

    def test_06_all_original_question_solution_pairs(self):
        for ex, num in zip(self.exercises, QUESTION_IMAGES):
            p, s = ex.find(C+"problem"), ex.find(C+"solution")
            self.assertIsNotNone(s)
            dest_p, dest_s = self.by_id[p.get("id")], self.by_id[s.get("id")]
            self.assertIn("#"+s.get("id"), [n.get("href") for n in dest_p.iter("a")])
            self.assertIn("#"+p.get("id"), [n.get("href") for n in dest_s.iter("a")])
            self.assertEqual([image_number(Path(n.get("src")).name) for n in s.iter(C+"image")], [num])
            self.assertEqual([image_number(n.get("src")[6:]) for n in dest_s.iter("img")], [num])

    def test_07_all_80_display_regressions(self):
        self.assertEqual(len(self.check_pairs), 80)
        self.assertEqual(len(self.math), 80)
        self.assertEqual(self.math, self.config["expected_math"])
        self.assertEqual(inventory([k+"|"+v for k,v in self.check_pairs]), MATH_INVENTORY)
        for term in self.config["required_terms"]:
            self.assertIn(term, self.all_text)

    def test_08_all_18_questions_against_source_mathml(self):
        for ex, key, rule in zip(self.exercises, QUESTION_KEYS, QUESTION_RULES):
            maths = list(ex.find(C+"problem").iter(M+"math"))
            self.assertEqual(len(maths), 1)
            self.assertEqual(compact(math_text(maths[0])).rstrip("."), "f(x)="+rule)
            self.assertEqual(compact(self.math[key]), "f(x)="+rule)

    def test_09_all_28_pixel_table_rows_recomputed(self):
        tables = [t for t in self.target.iter("table") if t.get("id") != "fs-id1167829719082"]
        self.assertEqual(len(tables), 5)
        for table, expected, rule in zip(tables, TABLE_ROWS, TABLE_RULES):
            rows = list(table.iter("tr"))[1:]
            self.assertEqual(len(rows), len(expected))
            for row, (x,y) in zip(rows, expected):
                cells = [text(cell).strip() for cell in row]
                self.assertEqual(len(cells), 3)
                self.assertEqual(F(cells[0].replace("−","-")), x)
                self.assertEqual(F(cells[1].replace("−","-")), y)
                self.assertEqual(compact(cells[2]), compact(f"({x},{y})"))
                self.assertEqual(value(rule, x), y)

    def test_10_notation_meaning_table(self):
        rows = [[text(c) for c in row] for row in self.by_id["fs-id1167829719082"].iter("tr")]
        self.assertEqual(rows, [["f","फलनाचे नाव"], ["x","क्रमित जोडीचा x-सहनिर्देशक"],
                                ["f(x)","क्रमित जोडीचा y-सहनिर्देशक"]])
        source = next(n for n in self.source.iter() if n.get("id")=="fs-id1167829719082")
        self.assertIn("name of function", text(source))
        self.assertIn("x-coordinate", text(source))
        self.assertIn("y-coordinate", text(source))

    def test_11_original_worked_table_rows(self):
        first = self.by_id["fs-id1167836688758"]
        second = self.by_id["fs-id1167836560655"]
        for fragment in ["f(x) = −2x − 4", "m = −2", "b = −4", "उतार", "आलेख काढा"]:
            self.assertIn(fragment, text(first))
        self.assertIn("f(x) = 4", text(second))
        self.assertIn("(0, 4)", text(second))
        self.assertIn("आडवी रेषा", text(second))
        self.assertEqual(self.math["example1-slope"], "m = −2")
        self.assertEqual(self.math["example1-intercept"], "b = −4")

    def test_12_linear_zero_slope_and_singleton_range(self):
        self.assertEqual(self.math["nonzero-slope"], "m ≠ 0")
        self.assertEqual(self.math["zero-slope"], "m = 0")
        self.assertEqual(self.math["constant-exception-range"], "{b}")
        self.assertEqual(self.math["constant-range"], "{b}")
        self.assertEqual(self.math["intercept-point"], "(0, b)")
        self.assertIn("प्रांत मात्र दोन्ही प्रकरणांत सर्व वास्तव संख्या", self.all_text)
        # Arithmetic regressions for the algebraic inverse x=(y-b)/m;
        # the universal argument is the identity m*((y-b)/m)+b=y, m != 0.
        for slope in [F(-3), F(1,2), F(4)]:
            for b in [F(-7), F(0), F(2,3)]:
                for y in [F(-101,7), F(0), F(35,2)]:
                    self.assertEqual(slope*((y-b)/slope)+b, y)
        self.assertEqual({0*x+F(2,3) for x in [F(-7),F(0),F(1,2)]}, {F(2,3)})

    def test_13_all_basic_domain_range_statements(self):
        for key in ["all-reals","square-domain","cube-domain","cube-range","absolute-domain"]:
            self.assertEqual(self.math[key], "(−∞, ∞)")
        for key in ["nonnegative","square-range","root-domain","root-range","absolute-range"]:
            self.assertEqual(self.math[key], "[0, ∞)")
        self.assertEqual(self.math["identity-slope"], "m = 1")
        self.assertEqual(self.math["identity-intercept"], "b = 0")
        self.assertEqual(self.math["identity-rule"], "f(x) = x")
        self.assertIn("x = √y घेतल्यास x² = y", self.all_text)
        self.assertIn("वास्तव घनमूळ x घेतल्यास x³ = y", self.all_text)
        self.assertIn("प्रत्येक द्विघाती फलनाचा मूल्यसंच हाच असेल असे नाही", self.all_text)

    def test_14_negative_powers_and_absolute_values(self):
        self.assertEqual(self.math["negative-square"], "−x² = −(x²)")
        self.assertEqual(self.math["squared-negative"], "(−x)² = x²")
        # The checked expressions put the minus outside the square. The
        # substitutions below are arithmetic regressions, not universal proof.
        for x in [F(-3),F(-1,2),F(0),F(2,3)]:
            self.assertEqual(value("−x²",x), -value("x²",x))
            self.assertEqual(value("−x³",x), -value("x³",x))
            self.assertEqual(value("−|x|",x), -abs(x))
            self.assertLessEqual(value("−|x|",x),0)
            self.assertEqual(value("x³",-x),-value("x³",x))

    def test_15_square_root_real_domain_not_just_table_inputs(self):
        self.assertEqual(self.math["negative-root"], "−√x = −(√x)")
        self.assertIn("पूर्ण वर्ग ही सोयीची निवड आहे, प्रांतावरील बंधन नाही", self.all_text)
        self.assertIn("2, 1/2", self.all_text)
        self.assertIn("एकच ऋणेतर वर्गमूळ", self.all_text)
        for x in [F(0),F(1,4),F(9,16),F(4)]:
            y=value("√x",x)
            self.assertGreaterEqual(y,0)
            self.assertEqual(y*y,x)
            self.assertEqual(value("−√x",x),-y)
        for x in [F(-1),F(-1,2)]:
            with self.assertRaisesRegex(ValueError,"outside real"):
                value("√x",x)
        # 2 is within the real domain although this rational-only helper cannot
        # return its irrational root; that computational limit is kept distinct.
        self.assertGreater(F(2),0)
        with self.assertRaisesRegex(ValueError,"real but not"):
            value("√x",2)

    def test_16_all_52_original_image_pins(self):
        records=self.lock["source_images"]
        self.assertEqual(len(records),52)
        self.assertEqual(inventory([r["locale"]+"|"+Path(r["member"]).name+"|"+r["sha256"]+"|"+str(r["bytes"])
                                    for r in records]), IMAGE_INVENTORY)
        all_bytes={}
        for locale,(archive,prefix,pin) in MODULES.items():
            with zipfile.ZipFile(BASE.parent/"downloads/mr-Deva-IN/releases"/archive) as z:
                for record in [r for r in records if r["locale"]==locale]:
                    name=Path(record["member"]).name
                    self.assertEqual(record["member"], prefix+"/media/"+name)
                    raw=z.read(record["member"])
                    self.assertEqual(len(raw),record["bytes"])
                    self.assertEqual(sha(raw),record["sha256"])
                    self.assertEqual((BASE.parent/record["review_copy"]).read_bytes(),raw)
                    all_bytes[locale,name]=raw
                    if locale=="en":
                        asset=self.config["assets"][name]
                        self.assertEqual((BASE/asset["path"]).read_bytes(),raw)
                        self.assertEqual(asset["sha256"],sha(raw))
                        self.assertEqual(asset["mime"],"image/jpeg")
        self.assertEqual(sum(len(v) for v in all_bytes.values()),3242112)
        changed={image_number(name) for locale,name in all_bytes if locale=="en"
                 and all_bytes["en",name]!=all_bytes["id",name]}
        self.assertEqual(changed,{"008","010","012","014","016","018","020"})
        self.assertEqual(tuple(self.images),IMAGE_NUMBERS)
        self.assertEqual(set(self.config["assets"]),{n.get("src")[6:] for n in self.target.iter("img")})

    def test_17_every_numeric_alt_point_matches_its_formula(self):
        rules=dict(zip(QUESTION_IMAGES,QUESTION_RULES))
        rules.update({"007":"2x−3","012":"x","014":"x²","016":"x³","018":"√x","020":"|x|"})
        for num,rule in rules.items():
            alt=self.images[num].get("alt").replace("−","-")
            points=re.findall(r"\((-?\d+),\s*(-?\d+)\)",alt)
            self.assertTrue(points,num)
            for x,y in points:
                self.assertEqual(value(rule,F(x)),F(y),(num,x,y))
        for num in ("008","010"):
            self.assertIn("(0, b)",self.images[num].get("alt"))

    def test_18_actual_axis_and_shape_observations(self):
        for num,phrases in AXIS_TEXT.items():
            for phrase in phrases:
                self.assertIn(phrase,self.images[num].get("alt"),num)
        self.assertIn("खाली उघडणारा",self.images["306"].get("alt"))
        self.assertIn("दोन सरळ किरण",self.images["019"].get("alt"))
        self.assertIn("दोन सरळ किरण",self.images["020"].get("alt"))
        self.assertIn("जाळीची खिडकी आणि फलनाचा प्रांत वेगळे",self.all_text)

    def test_19_preserved_source_errors_explicit_not_silently_adopted(self):
        en8=next(n for n in self.sections["en"].iter() if n.get("id")=="fs-id1167829790631")
        id8=next(n for n in self.sections["id"].iter() if n.get("id")=="fs-id1167829790631")
        self.assertNotIn("≠",en8.get("alt"))
        self.assertIn("m ≠ 0",id8.get("alt"))
        for locale in ("en","id"):
            src=next(n for n in self.sections[locale].iter() if n.get("id")=="fs-id1167833197255")
            self.assertIn("opening up" if locale=="en" else "membuka ke atas",src.get("alt"))
        self.assertIn("स्रोत-दुरुस्ती",self.all_text)
        self.assertIn("ती खाली उघडते",self.all_text)
        self.assertIn("प्रत्यक्ष इंग्रजी आकृती",self.all_text)
        self.assertIn("फक्त धन आणि ऋण मूल्ये मिळतात एवढ्यावरून",self.all_text)

    def test_20_source_crossrefs_and_local_links(self):
        source_refs=[n.get("target-id") for n in self.source.iter(C+"link")]
        self.assertEqual(source_refs,["CNX_IntAlg_Figure_03_06_001","CNX_IntAlg_Figure_03_06_007",
                                      "fs-id1167836683384","fs-id1167832966170"])
        refs=[n for n in self.target.iter("a") if n.get("data-source-target-id")]
        self.assertEqual([n.get("data-source-target-id") for n in refs],source_refs)
        module_ids={n.get("id") for n in self.modules["en"].iter() if n.get("id")}
        for ref in refs:
            target=ref.get("data-source-target-id")
            self.assertIn(target,module_ids)
            if target==source_refs[0]:
                self.assertEqual(ref.get("data-source-document"),"m81374")
                self.assertEqual(ref.get("href"),"https://openstax.org/books/intermediate-algebra-2e/pages/3-6-graphs-of-functions#"+target)
            else:self.assertEqual(ref.get("href"),"#"+target)
        links=[n.get("href") for n in self.target.iter("a")]
        self.assertEqual(sum(h.startswith("#") for h in links),48)
        self.assertEqual(sum(h.startswith("https://") for h in links),6)
        for link in links:
            if link.startswith("#"):self.assertIn(link[1:],self.by_id)

    def test_21_missing_source_graph_instructions_disclosed(self):
        for ex_index in [8,12]:
            source=self.exercises[ex_index].find(C+"problem")
            self.assertNotIn("Graph",text(source))
            target=self.by_id[source.get("id")]
            notes=[n for n in target.iter() if n.get("data-kind")=="original"]
            self.assertTrue(any("जोडलेली सूचना" in text(n) for n in notes))
        self.assertIn("थेट स्थानिक आंतरघटक-दुवा अद्याप उपलब्ध नाही",self.all_text)

    def test_22_graph_definition_and_sample_limit(self):
        self.assertIn("(x, f(x))",text(self.by_id["fs-id1167829598148"]))
        self.assertIn("काही बिंदू हे संपूर्ण आलेखाचे नमुने आहेत",self.all_text)
        self.assertIn("तेच सर्व बिंदू नव्हेत",self.all_text)
        self.assertIn("संतत",self.all_text)
        self.assertIn("दोन सरळ किरणांनी",self.all_text)
        self.assertIn("∞ ही वास्तव संख्या",self.all_text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
