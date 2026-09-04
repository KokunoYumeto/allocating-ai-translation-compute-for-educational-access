"""Independent MR024 real-source and mathematics regression.

This suite reads the frozen Marathi XML/config/provenance/build artifacts, the
complete pinned EN and ID m81427 modules, every selected fragment, and all four
original equation-image members.  The companion report records the manual
source, pixel, and canon reading.  These tests bind that review to exact bytes;
they are deliberately not browser, PDF, reader-layout, or native-speaker QA.
"""

from fractions import Fraction as F
import hashlib
import json
import re
import unicodedata
import unittest
import zipfile
from pathlib import Path
import xml.etree.ElementTree as E


BASE = Path(__file__).resolve().parents[1]
WORKSPACE = BASE.parent
UNIT = "MR-BRIDGE-024"
C = "{http://cnx.rice.edu/cnxml}"
MD = "{http://cnx.rice.edu/mdml}"
M = "{http://www.w3.org/1998/Math/MathML}"

PINS = {
    "translations/MR-BRIDGE-024.xml": (
        26332,
        "7468c2fe7bb4017eecbed7035708a71905bbba2744ecb25f0f5aea3226709570",
    ),
    "units/MR-BRIDGE-024.json": (
        2646,
        "f5dac85f9438bd37badd12e8009e6e1629e5b2361685b06b007169cc50eacdd0",
    ),
    "provenance/MR-BRIDGE-024.lock.json": (
        47535,
        "9ba9e64443f20a8e9e376ab9f405bb558ce007a4588fdfb2c419452cbefeeb52",
    ),
    "qa/MR-BRIDGE-024-build-receipt.json": (
        3100,
        "a783d40b4bca75d695b29ad8580b7b84e622c3c96dab631847de825556887148",
    ),
    "output/MR-BRIDGE-024.html": (
        258855,
        "388156272dad163a82ce9dab51a01c59928a91eeea54bfc355fdf8aac681ce22",
    ),
}

ARCHIVES = {
    "en": (
        "A20-canonical.zip",
        "osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9",
        "effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917",
    ),
    "id": (
        "A20-v0.3.0-source.zip",
        "source",
        "a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7",
    ),
}
MODULE_PINS = {
    "en": (166406, "2f3b5391a9845dc34cccb4c903ee25f2b4f23eceef25ee574d36ebe224b163e5"),
    "id": (168909, "2efbe62eb5cc35c1e1b51cf591cd52f234d8241c368e86573a3bcb350661c112"),
}

WRAPPER = "fs-id1167835596566"
NEXT = "fs-id1167832086919"
EXPECTED_SELECTORS = [
    "para-00001",
    "list-00001",
    "fs-id1167830925402",
    "fs-idm321747056",
    "fs-idm337329376",
    "fs-id1167831883449",
    "fs-id1167835194597",
    "fs-id1167834061509",
    "fs-id1167831040311",
    "fs-id1167834479634",
    "fs-id1167835513953",
    "fs-id1167835301937",
    "fs-id1167834063240",
    "fs-id1167835167507",
    "fs-id1167835326515",
    "fs-id1167832066187",
    "fs-id1167834132168",
]
BOUNDARY_ROOTS = [
    "para-00001",
    "list-00001",
    "fs-id1167830925402",
    "fs-idm321747056",
    "fs-idm337329376",
    WRAPPER,
]
EXERCISES = [
    ("fs-idm301559296", "fs-idm351011648", "fs-idm325318272"),
    ("fs-idm301109616", "fs-idm319366096", "fs-idm337570480"),
    ("fs-idm327937056", "fs-idm341410000", "fs-idm329340480"),
    ("fs-id1167835360973", "fs-id1167832056984", "fs-id1167834397737"),
    ("fs-id1167834346678", "fs-id1167832056851", "fs-id1167835253906"),
    ("fs-id1167835331532", "fs-id1167831106822", "fs-id1167835545439"),
]
SOURCE_MATH_KEYS = [
    "ready1-equation",
    "ready1-pair-a",
    "ready1-pair-b",
    "ready2-equation",
    "ready2-answer",
    "ready3-equation",
    "ready3-answer",
    "intro-system",
    "line-equation",
    "solution-pair",
    "definition-pair",
    "example-system",
    "example-pair-a",
    "example-pair-b",
    "try1-system",
    "try1-pair-a",
    "try1-pair-b",
    "try2-system",
    "try2-pair-a",
    "try2-pair-b",
]
EXPECTED_MATH = {
    "ready1-equation": "y = (2/3)x − 4",
    "ready1-pair-a": "(6, 0)",
    "ready1-pair-b": "(−3, −2)",
    "ready2-equation": "3x − y = 12",
    "ready2-answer": "m = 3; b = −12",
    "ready3-equation": "2x − 3y = 12",
    "ready3-answer": "(6, 0), (0, −4)",
    "intro-system": "{ 2x + y = 7; x − 2y = 6 }",
    "line-equation": "2x + y = 7",
    "solution-pair": "(x, y)",
    "definition-pair": "(x, y)",
    "example-system": "{ x − y = −1; 2x − y = −5 }",
    "example-pair-a": "(−2, −1)",
    "example-pair-b": "(−4, −3)",
    "example-a-substitution": "x = −2, y = −1",
    "example-a-first-check": "−2 − (−1) ?= −1",
    "example-a-first-result": "−1 = −1",
    "example-a-second-check": "2(−2) − (−1) ?= −5",
    "example-a-second-result": "−3 ≠ −5",
    "example-a-conclusion-pair": "(−2, −1)",
    "example-b-substitution": "x = −4, y = −3",
    "example-b-first-check": "−4 − (−3) ?= −1",
    "example-b-first-result": "−1 = −1",
    "example-b-second-check": "2(−4) − (−3) ?= −5",
    "example-b-second-result": "−5 = −5",
    "example-b-conclusion-pair": "(−4, −3)",
    "try1-system": "{ 3x + y = 0; x + 2y = −5 }",
    "try1-pair-a": "(1, −3)",
    "try1-pair-b": "(0, 0)",
    "try2-system": "{ x − 3y = −8; −3x − y = 4 }",
    "try2-pair-a": "(2, −2)",
    "try2-pair-b": "(−2, 2)",
}

IMAGES = {
    "CNX_IntAlg_Figure_04_01_001_img.jpg": {
        "en": (97207, "91523ae06f844c76cfa90cd410bb6a0237969334a4922132e09434bb684ffb02", (426, 216)),
        "id": (82575, "b1814e1dd3b4bfbcc8493e832367b005f89abf57849dc8c25ddb8d039cbac594", (1340, 660)),
    },
    "CNX_IntAlg_Figure_04_01_002_img_new.jpg": {
        "en": (73865, "2ed7001540a6eca5079fc199f19f7812816813f36b685f448db4a309f6707d64", (409, 154)),
        "id": (85859, "881d3da3e258328d5405420c4084f39fa226deb3ad6daf8686ab14225d3b921e", (1340, 660)),
    },
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def sha_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def unique(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate JSON key")
        out[key] = value
    return out


def inside(base, relative):
    path = (base / relative).resolve()
    if base.resolve() not in path.parents:
        raise ValueError("path escape")
    return path


def node_text(node):
    return "".join(node.itertext())


def id_map(root):
    return {node.get("id"): node for node in root.iter() if node.get("id")}


def parent_map(root):
    return {child: parent for parent in root.iter() for child in parent}


def nearest_source_parent(node, parents, allowed):
    while node in parents:
        node = parents[node]
        if node.get("id") in allowed:
            return node.get("id")
    return None


def shape(node):
    return (
        node.tag,
        tuple(sorted(node.attrib.items())),
        node.text,
        tuple((shape(child), child.tail) for child in node),
    )


def mathml(node):
    local = node.tag.removeprefix(M)
    if local in {"mi", "mn", "mo", "mtext"}:
        if len(node):
            raise ValueError("MathML token has children")
        return node.text or ""
    if local in {"math", "mrow", "mtd"}:
        return "".join(mathml(child) for child in node)
    if local == "mspace":
        return ""
    if local == "mfrac" and len(node) == 2:
        return "(" + mathml(node[0]) + "/" + mathml(node[1]) + ")"
    if local == "mfenced":
        return (
            node.get("open", "(")
            + node.get("separators", ",").join(mathml(child) for child in node)
            + node.get("close", ")")
        )
    if local == "mtr":
        return "".join(mathml(child) for child in node)
    if local == "mtable":
        rows = [mathml(child) for child in node]
        return ";".join(row for row in rows if row)
    raise ValueError("unsupported MathML " + local)


def semantic_math(value):
    value = re.sub(r"\s+", "", value).replace("−", "-")
    value = value.replace("{", "").replace("}", "")
    return value.rstrip(".,;?")


def jpeg_size(data):
    if not data.startswith(b"\xff\xd8\xff"):
        raise ValueError("not JPEG")
    index = 2
    start_of_frame = {
        0xC0,
        0xC1,
        0xC2,
        0xC3,
        0xC5,
        0xC6,
        0xC7,
        0xC9,
        0xCA,
        0xCB,
        0xCD,
        0xCE,
        0xCF,
    }
    while index < len(data):
        while index < len(data) and data[index] == 0xFF:
            index += 1
        if index >= len(data):
            break
        marker = data[index]
        index += 1
        if marker in {0x01, 0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
            continue
        if index + 2 > len(data):
            break
        length = int.from_bytes(data[index : index + 2], "big")
        if length < 2 or index + length > len(data):
            raise ValueError("bad JPEG segment")
        if marker in start_of_frame:
            height = int.from_bytes(data[index + 3 : index + 5], "big")
            width = int.from_bytes(data[index + 5 : index + 7], "big")
            return width, height
        index += length
    raise ValueError("JPEG dimensions missing")


def line_value(a, b, c, point):
    x, y = map(F, point)
    return F(a) * x + F(b) * y + F(c)


class Unit24Math(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (BASE / f"translations/{UNIT}.xml").read_bytes()
        cls.root = E.fromstring(cls.raw)
        cls.target = id_map(cls.root)
        cls.target_parents = parent_map(cls.root)
        cls.config = json.loads(
            (BASE / f"units/{UNIT}.json").read_text(encoding="utf-8"),
            object_pairs_hook=unique,
        )
        cls.lock = json.loads(
            (BASE / f"provenance/{UNIT}.lock.json").read_text(encoding="utf-8"),
            object_pairs_hook=unique,
        )
        cls.receipt = json.loads(
            (BASE / f"qa/{UNIT}-build-receipt.json").read_text(encoding="utf-8"),
            object_pairs_hook=unique,
        )
        cls.check_nodes = [node for node in cls.root.iter() if node.get("data-check")]
        cls.checks = {node.get("data-check"): node_text(node) for node in cls.check_nodes}
        cls.archive_paths = {}
        cls.modules = {}
        cls.source_roots = {}
        cls.source = {}
        cls.archive_images = {}
        for locale, (archive_name, prefix, _) in ARCHIVES.items():
            archive = WORKSPACE / "downloads/mr-Deva-IN/releases" / archive_name
            cls.archive_paths[locale] = archive
            with zipfile.ZipFile(archive) as zf:
                module = zf.read(f"{prefix}/modules/m81427/index.cnxml")
                for name in IMAGES:
                    cls.archive_images[(locale, name)] = zf.read(f"{prefix}/media/{name}")
            cls.modules[locale] = module
            cls.source_roots[locale] = E.fromstring(module)
            cls.source[locale] = id_map(cls.source_roots[locale])

    def test_01_reviewed_artifact_pins(self):
        for relative, expected in PINS.items():
            data = (BASE / relative).read_bytes()
            self.assertEqual((len(data), sha(data)), expected, relative)

    def test_02_archive_module_bytes_and_metadata(self):
        titles = {
            "en": "Solve Systems of Linear Equations with Two Variables",
            "id": "Menyelesaikan Sistem Persamaan Linear dengan Dua Variabel",
        }
        for locale, (_, _, archive_digest) in ARCHIVES.items():
            self.assertEqual(sha_file(self.archive_paths[locale]), archive_digest)
            self.assertEqual((len(self.modules[locale]), sha(self.modules[locale])), MODULE_PINS[locale])
            root = self.source_roots[locale]
            self.assertEqual(root.tag, C + "document")
            self.assertEqual(root.get("{http://www.w3.org/XML/1998/namespace}lang"), None if locale == "en" else "id-ID")
            self.assertEqual(root.findtext(C + "title"), titles[locale])
            metadata = root.find(C + "metadata")
            self.assertEqual(metadata.findtext(MD + "content-id"), "m81427")
            self.assertEqual(metadata.findtext(MD + "title"), titles[locale])
            self.assertEqual(metadata.findtext(MD + "uuid"), "b9f8475e-9490-4f24-995f-2923b1ed9644")

    def test_03_complete_objectives_and_exact_teaching_boundary(self):
        objective_text = {
            "en": [
                "Determine whether an ordered pair is a solution of a system of equations",
                "Solve a system of linear equations by graphing",
                "Solve a system of equations by substitution",
                "Solve a system of equations by elimination",
                "Choose the most convenient method to solve a system of linear equations",
            ],
            "id": [
                "Menentukan apakah pasangan berurutan merupakan solusi suatu sistem persamaan",
                "Menyelesaikan sistem persamaan linear dengan menggambar grafik",
                "Menyelesaikan sistem persamaan dengan substitusi",
                "Menyelesaikan sistem persamaan dengan eliminasi",
                "Memilih metode yang paling praktis untuk menyelesaikan sistem persamaan linear",
            ],
        }
        for locale in ARCHIVES:
            source = self.source[locale]
            self.assertEqual([node_text(item) for item in source["list-00001"]], objective_text[locale])
            content = self.source_roots[locale].find(C + "content")
            self.assertEqual([node.get("id") for node in list(content)[:4]], [
                "fs-id1167830925402",
                "fs-idm321747056",
                "fs-idm337329376",
                WRAPPER,
            ])
            wrapper = source[WRAPPER]
            children = [node for node in wrapper if node.tag != C + "title"]
            self.assertEqual([node.get("id") for node in children], EXPECTED_SELECTORS[5:])
            self.assertEqual(len(children), 12)
            self.assertEqual(list(content)[4].get("id"), NEXT)
            self.assertEqual(
                list(content)[4].findtext(C + "title"),
                "Solve a System of Linear Equations by Graphing"
                if locale == "en"
                else "Menyelesaikan Sistem Persamaan Linear dengan Menggambar Grafik",
            )

    def test_04_exact_ordered_seventeen_selectors(self):
        actual = [node.get("data-source") for node in self.root.iter() if node.get("data-source")]
        expected = ["A20:m81427#" + ident for ident in EXPECTED_SELECTORS]
        self.assertEqual(actual, expected)
        self.assertEqual([entry["locator"] for entry in self.lock["source_selections"]], expected)
        self.assertEqual([entry["target_id"] for entry in self.lock["source_selections"]], EXPECTED_SELECTORS)
        self.assertIsNone(self.target[WRAPPER].get("data-source"))

    def test_05_all_thirty_four_fragments_match_real_sources(self):
        count = 0
        total = 0
        for selection in self.lock["source_selections"]:
            self.assertEqual(len(selection["sources"]), 2)
            for record in selection["sources"]:
                locale = record["locale"]
                fragment = inside(BASE, record["fragment_path"]).read_bytes()
                source = self.source[locale][selection["target_id"]]
                self.assertEqual(sha(fragment), record["fragment_sha256"])
                self.assertEqual(shape(E.fromstring(fragment)), shape(source))
                self.assertEqual(record["module_sha256"], MODULE_PINS[locale][1])
                self.assertEqual(record["archive_sha256"], ARCHIVES[locale][2])
                self.assertEqual(
                    record["math_sha256"],
                    [sha(E.tostring(math, encoding="utf-8")) for math in source.iter(M + "math")],
                )
                self.assertEqual(record["outgoing_urls"], [])
                count += 1
                total += len(fragment)
        self.assertEqual((count, total), (34, 30471))

    def test_06_all_forty_five_local_witnesses(self):
        witnesses = self.lock["witnesses"]
        self.assertEqual(len(witnesses), 45)
        self.assertEqual(len({entry["path"] for entry in witnesses}), 45)
        for entry in witnesses:
            data = inside(BASE, entry["path"]).read_bytes()
            self.assertEqual((len(data), sha(data)), (entry["bytes"], entry["sha256"]), entry["path"])

    def test_07_exact_fifty_nine_source_ids_order_and_ancestry(self):
        locale_orders = {}
        for locale in ARCHIVES:
            order = []
            for ident in BOUNDARY_ROOTS:
                order.extend(node.get("id") for node in self.source[locale][ident].iter() if node.get("id"))
            self.assertEqual(len(order), 59)
            self.assertEqual(len(set(order)), 59)
            locale_orders[locale] = order
        self.assertEqual(locale_orders["en"], locale_orders["id"])
        order = locale_orders["en"]
        target_order = [node.get("id") for node in self.root.iter() if node.get("id") in set(order)]
        self.assertEqual(target_order, order)
        self.assertEqual(set(self.target) - set(order), {UNIT, "readiness", "credits"})
        self.assertEqual(len(self.target), 62)
        allowed = set(order)
        for locale in ARCHIVES:
            source_parents = parent_map(self.source_roots[locale])
            for ident in order:
                self.assertEqual(
                    nearest_source_parent(self.source[locale][ident], source_parents, allowed),
                    nearest_source_parent(self.target[ident], self.target_parents, allowed),
                    (locale, ident),
                )

    def test_08_six_complete_problem_solution_pairs_and_accounting(self):
        for locale in ARCHIVES:
            source = self.source[locale]
            self.assertEqual(
                [(exercise, problem, solution) for exercise, problem, solution in EXERCISES],
                [
                    (
                        exercise.get("id"),
                        exercise.find(C + "problem").get("id"),
                        exercise.find(C + "solution").get("id"),
                    )
                    for exercise in [source[triple[0]] for triple in EXERCISES]
                ],
            )
        for exercise_id, problem_id, solution_id in EXERCISES:
            self.assertEqual(self.target[exercise_id].tag, "section")
            self.assertEqual(self.target[problem_id].get("class"), "problem")
            self.assertEqual(self.target[solution_id].get("class"), "solution")
            self.assertEqual(len(self.target[problem_id].findall(f".//a[@href='#{solution_id}']")), 1)
            self.assertEqual(len(self.target[solution_id].findall(f".//a[@href='#{problem_id}']")), 1)
        for key, value in {
            "source_count": 17,
            "translated_worked_examples": 1,
            "translated_definitions": 2,
            "translated_practice_items": 5,
            "translated_resource_notes": 0,
            "original_practice_items": 0,
        }.items():
            self.assertEqual(self.config[key], value)
        self.assertEqual(self.config["question_ids"], [])

    def test_09_all_twenty_source_math_occurrences_match_target_semantics(self):
        for locale in ARCHIVES:
            source_math = []
            for selection_id in EXPECTED_SELECTORS:
                source_math.extend(mathml(node) for node in self.source[locale][selection_id].iter(M + "math"))
            self.assertEqual(len(source_math), 20)
            self.assertEqual(
                [semantic_math(value) for value in source_math],
                [semantic_math(EXPECTED_MATH[key]) for key in SOURCE_MATH_KEYS],
            )

    def test_10_all_thirty_two_display_math_keys_exact(self):
        self.assertEqual(len(self.check_nodes), 32)
        self.assertEqual(len(self.checks), 32)
        self.assertEqual(self.checks, EXPECTED_MATH)
        self.assertEqual(self.config["expected_math"], EXPECTED_MATH)

    def test_11_readiness_one_equation_and_yes_no_answer(self):
        equation = lambda x: F(2, 3) * F(x) - 4
        self.assertEqual(equation(6), 0)
        self.assertNotEqual(equation(-3), -2)
        for locale, yes, no in [("en", "yes", "no"), ("id", "ya", "tidak")]:
            answer = node_text(self.source[locale]["fs-idm317621568"]).lower()
            self.assertIn(yes, answer)
            self.assertIn(no, answer)
        target = node_text(self.target["fs-idm317621568"])
        self.assertIn("ⓐ होय", target)
        self.assertIn("ⓑ नाही", target)

    def test_12_readiness_two_slope_and_intercept(self):
        # 3x-y=12 rearranges exactly to y=3x-12.
        self.assertEqual(F(3), F(3))
        self.assertEqual(line_value(3, -1, -12, (0, -12)), 0)
        self.assertEqual(line_value(3, -1, -12, (1, -9)), 0)
        self.assertEqual(self.checks["ready2-answer"], "m = 3; b = −12")

    def test_13_readiness_three_axis_intercepts(self):
        self.assertEqual(line_value(2, -3, -12, (6, 0)), 0)
        self.assertEqual(line_value(2, -3, -12, (0, -4)), 0)
        self.assertEqual(self.checks["ready3-answer"], "(6, 0), (0, −4)")

    def test_14_worked_example_substitutions_and_conclusions(self):
        system = [(1, -1, 1), (2, -1, 5)]  # ax+by+c=0
        a_values = [line_value(*line, (-2, -1)) for line in system]
        b_values = [line_value(*line, (-4, -3)) for line in system]
        self.assertEqual(a_values, [0, 2])
        self.assertEqual(b_values, [0, 0])
        self.assertEqual(-2 - (-1), -1)
        self.assertEqual(2 * -2 - (-1), -3)
        self.assertNotEqual(-3, -5)
        self.assertEqual(-4 - (-3), -1)
        self.assertEqual(2 * -4 - (-3), -5)

    def test_15_both_try_it_answer_sets(self):
        try_one = [(3, 1, 0), (1, 2, 5)]
        self.assertEqual([line_value(*line, (1, -3)) for line in try_one], [0, 0])
        self.assertNotEqual([line_value(*line, (0, 0)) for line in try_one], [0, 0])
        try_two = [(1, -3, 8), (-3, -1, -4)]
        self.assertNotEqual([line_value(*line, (2, -2)) for line in try_two], [0, 0])
        self.assertEqual([line_value(*line, (-2, 2)) for line in try_two], [0, 0])
        self.assertIn("ⓐ होय", node_text(self.target["fs-id1167835287970"]))
        self.assertIn("ⓑ नाही", node_text(self.target["fs-id1167835287970"]))
        self.assertIn("ⓐ नाही", node_text(self.target["fs-id1167826967139"]))
        self.assertIn("ⓑ होय", node_text(self.target["fs-id1167826967139"]))

    def test_16_all_source_answer_material_is_present_not_invented(self):
        answer_ids = [solution for _, _, solution in EXERCISES]
        for locale in ARCHIVES:
            for answer_id in answer_ids:
                self.assertIn(answer_id, self.source[locale])
        self.assertNotIn("source-answer-missing", self.raw.decode("utf-8"))
        example = self.target["fs-id1167834397737"]
        self.assertEqual(len(example.findall(".//figure")), 2)
        self.assertEqual(len(example.findall(".//div[@class='image-transcript']")), 2)
        self.assertIn("ही प्रणालीची उकल नाही", node_text(example))
        self.assertIn("ही प्रणालीची उकल आहे", node_text(example))

    def test_17_all_four_original_images_review_copies_assets_and_dimensions(self):
        records = self.lock["source_images"]
        self.assertEqual(len(records), 4)
        self.assertEqual(len({(record["locale"], Path(record["member"]).name) for record in records}), 4)
        for record in records:
            locale = record["locale"]
            name = Path(record["member"]).name
            data = self.archive_images[(locale, name)]
            size, digest, dimensions = IMAGES[name][locale]
            self.assertEqual((len(data), sha(data), jpeg_size(data)), (size, digest, dimensions))
            self.assertEqual((record["bytes"], record["sha256"]), (size, digest))
            self.assertEqual(inside(WORKSPACE, record["review_copy"]).read_bytes(), data)
            if locale == "en":
                self.assertEqual(inside(BASE, record["committed_asset"]).read_bytes(), data)
                self.assertEqual(self.config["assets"][name], {
                    "path": f"assets/{UNIT}/{name}",
                    "sha256": digest,
                    "mime": "image/jpeg",
                })

    def test_18_image_source_alts_and_target_placement(self):
        source_alt_markers = {
            "en": ["x minus y equals minus 1", "minus 3 not equal to minus 5", "minus 5 equals minus 5"],
            "id": ["x dikurangi y sama dengan negatif 1", "negatif 3 tidak sama dengan negatif 5", "negatif 5 sama dengan negatif 5"],
        }
        for locale in ARCHIVES:
            alts = [
                self.source[locale]["fs-id1167834135019"].get("alt"),
                self.source[locale]["fs-id1167835319876"].get("alt"),
            ]
            joined = " ".join(alts).lower()
            for marker in source_alt_markers[locale]:
                self.assertIn(marker, joined)
        expected = [
            ("fs-id1167834135019", "CNX_IntAlg_Figure_04_01_001_img.jpg"),
            ("fs-id1167835319876", "CNX_IntAlg_Figure_04_01_002_img_new.jpg"),
        ]
        for figure_id, name in expected:
            figure = self.target[figure_id]
            self.assertEqual(figure.tag, "figure")
            self.assertEqual(figure.find("img").get("src"), "asset:" + name)
            self.assertIn(figure, list(self.target["fs-id1167834397737"].iter()))

    def test_19_marathi_alt_and_transcript_match_manually_viewed_pixels(self):
        first = self.target["fs-id1167834135019"].find("img").get("alt")
        second = self.target["fs-id1167835319876"].find("img").get("alt")
        for marker in ["x = −2, y = −1", "−1 = −1", "−3, जे −5 नाही", "उकल नाही"]:
            self.assertIn(marker, first)
        for marker in ["x = −4, y = −3", "−4 − (−3) = −1", "2(−4) − (−3) = −5", "उकल आहे"]:
            self.assertIn(marker, second)
        transcript = node_text(self.target["fs-id1167834397737"])
        for marker in [
            "2(−2) − (−1) ?= −5",
            "−3 ≠ −5",
            "2(−4) − (−3) ?= −5",
            "−5 = −5",
        ]:
            self.assertIn(marker, transcript)
        self.assertTrue(re.search("[\u0900-\u097f]", first + second))

    def test_20_locale_image_difference_is_disclosed_without_false_identity(self):
        for name in IMAGES:
            self.assertNotEqual(self.archive_images[("en", name)], self.archive_images[("id", name)])
        note = " ".join(
            node_text(node)
            for node in self.root.findall(".//*[@data-kind='original']")
            if "ID आकृती" in node_text(node) or "EN आणि ID" in node_text(node)
        )
        for phrase in [
            "EN आणि ID आकृत्यांतील सर्व प्रतिस्थापने व निष्कर्ष जुळतात",
            "वेगळ्या आकारात पुन्हा मांडलेल्या",
            "पहिल्या ID आकृतीत वरची मूळ प्रणाली स्वतंत्रपणे पुन्हा दाखवलेली नाही",
            "कॅननिकल EN आकृत्या",
        ]:
            self.assertIn(phrase, note)

    def test_21_objectives_definitions_and_core_prose_claims_retained(self):
        target = node_text(self.root)
        for phrase in [
            "क्रमित जोडी ही समीकरण-प्रणालीची उकल आहे का ते ठरवणे",
            "आलेख काढून रेषीय समीकरणांची प्रणाली सोडवणे",
            "प्रतिस्थापन पद्धतीने समीकरणांची प्रणाली सोडवणे",
            "विलोपन पद्धतीने समीकरणांची प्रणाली सोडवणे",
            "सर्वांत सोयीची पद्धत निवडणे",
            "दोन किंवा अधिक रेषीय समीकरणे एकत्र गटबद्ध",
            "दोन अज्ञात चल असलेल्या दोन रेषीय समीकरणांच्या प्रणाली",
            "महिरपी कंस",
            "अनंत उकली",
            "प्रत्येक बिंदू त्या समीकरणाची उकल",
            "सर्व समीकरणे सत्य करणारी चलांची मूल्ये",
            "चलांची मूल्ये प्रत्येक समीकरणात प्रतिस्थापित करा",
        ]:
            self.assertIn(phrase, target)
        self.assertEqual([node.get("id") for node in self.root.iter("dfn")], ["term-00001", "term-00002"])

    def test_22_all_links_resolve_and_source_cross_references_are_exact(self):
        hrefs = [node.get("href") for node in self.root.iter("a")]
        local = [href for href in hrefs if href.startswith("#")]
        external = [href for href in hrefs if not href.startswith("#")]
        self.assertEqual(len(local), 17)
        for href in local:
            self.assertIn(href[1:], self.target)
        self.assertEqual(external, [
            "https://openstax.org/books/intermediate-algebra-2e/pages/3-1-graph-linear-equations-in-two-variables#fs-id1167835400321",
            "https://openstax.org/books/intermediate-algebra-2e/pages/3-2-slope-of-a-line#fs-id1167835342973",
            "https://openstax.org/books/intermediate-algebra-2e/pages/3-1-graph-linear-equations-in-two-variables#fs-id1167827987818",
            "https://openstax.org/books/intermediate-algebra-2e/pages/2-introduction",
            "https://creativecommons.org/licenses/by-nc-sa/4.0/",
            "https://vishwakosh.marathi.gov.in/24316/",
        ])
        crossrefs = [node for node in self.root.iter("a") if node.get("data-source-document")]
        self.assertEqual(
            [(node.get("data-source-document"), node.get("data-source-target-id")) for node in crossrefs],
            [
                ("m81369", "fs-id1167835400321"),
                ("m81370", "fs-id1167835342973"),
                ("m81369", "fs-id1167827987818"),
                ("m81361", None),
            ],
        )

    def test_23_locale_unicode_offline_media_and_safe_structure(self):
        self.assertEqual(self.root.get("id"), UNIT)
        self.assertEqual(self.root.get("lang"), "mr-Deva-IN")
        decoded = self.raw.decode("utf-8")
        self.assertEqual(decoded, unicodedata.normalize("NFC", decoded))
        self.assertNotIn("\ufffd", decoded)
        self.assertNotIn("id=\"" + NEXT + "\"", decoded)
        for image in self.root.iter("img"):
            self.assertTrue(image.get("src").startswith("asset:"))
            self.assertTrue(image.get("alt"))
        for tag in ["script", "iframe", "object", "embed", "svg", "audio", "video"]:
            self.assertFalse(list(self.root.iter(tag)), tag)

    def test_24_credit_scope_and_next_boundary_are_explicit(self):
        credits = node_text(self.target["credits"])
        for phrase in [
            "m81427",
            "b9f8475e-9490-4f24-995f-2923b1ed9644",
            "Solve Systems of Linear Equations with Two Variables",
            "Menyelesaikan Sistem Persamaan Linear dengan Dua Variabel",
            "17 थेट स्रोत-निवडी",
            "15 content selectors",
            "56 IDs",
            "57",
            "59 स्रोत IDs",
            "सहा स्रोत-प्रश्न",
            "सहा स्रोत-उत्तरे",
            NEXT,
            "येथे घेतलेला नाही",
            "संपूर्ण module",
            "पाचही पुस्तकांचे काम पूर्ण झाल्याचा दावा नाही",
        ]:
            self.assertIn(phrase, credits if phrase not in {"संपूर्ण module", "पाचही पुस्तकांचे काम पूर्ण झाल्याचा दावा नाही"} else node_text(self.root))

    def test_25_actual_marathi_canon_witnesses_and_honest_limits(self):
        expected = {
            "downloads/mr-Deva-IN/canon/pages/balbharati8-85.png": (
                255250,
                "284d9c7e4dc21f183189750421e65c97acfae02fd642df0457321cfe627a7f69",
            ),
            "downloads/mr-Deva-IN/canon/ocr/balbharati8-85.txt": (
                2474,
                "f9bf9c42edb3e126573bc14f4671aa5c062920ee145c50590fdac6733af52a9b",
            ),
            "downloads/mr-Deva-IN/canon/pages/balbharati8-86.png": (
                195482,
                "87e2c859c7d3445466e28b1050bb86bc52b1014fb6f2dd2c75d356dda620ce49",
            ),
            "downloads/mr-Deva-IN/canon/ocr/balbharati8-86.txt": (
                1539,
                "497332d70fb096c86e468261e37186b888099b86830234a26d5c86253188ee57",
            ),
        }
        for relative, pin in expected.items():
            data = (WORKSPACE / relative).read_bytes()
            self.assertEqual((len(data), sha(data)), pin)
        page_85 = (WORKSPACE / "downloads/mr-Deva-IN/canon/ocr/balbharati8-85.txt").read_text(encoding="utf-8")
        page_86 = (WORKSPACE / "downloads/mr-Deva-IN/canon/ocr/balbharati8-86.txt").read_text(encoding="utf-8")
        for phrase in ["समीकरणाची उकल", "दोन्ही बाजूंवर समान क्रिया", "शून्येतर समान संख्येने भागणे"]:
            self.assertIn(phrase, page_85)
        for phrase in [
            "पुढील समीकरणे सोडवा",
            "दोन्ही बाजूंना 5 ने गुणून",
            "दोन्ही बाजूंतून 2 वजा करून",
            "दोन्ही बाजूंना 5 ने भागून",
        ]:
            self.assertIn(phrase, page_86)
        canon_lock = json.loads((BASE / "canon/witnesses.lock.json").read_text(encoding="utf-8"), object_pairs_hook=unique)
        web = {item["ids"][0]: item for item in canon_lock["additional_web_readings"]}
        self.assertEqual(web["C18"]["url"], "https://vishwakosh.marathi.gov.in/24316/")
        self.assertEqual(web["C22"]["url"], "https://vishwakosh.marathi.gov.in/28194/")
        notes = node_text(self.root)
        for phrase in [
            "रेषीय समीकरणांची प्रणाली",
            "स्पष्टपणे तयार केलेला कार्यपर्याय",
            "अक्षरशः संज्ञा असल्याचा दावा नाही",
            "प्रतिस्थापन पद्धत",
            "विलोपन पद्धत",
            "अक्षरशः प्रमाणित असल्याचा दावा नाही",
        ]:
            self.assertIn(phrase, notes)

    def test_26_build_receipt_and_structural_html_are_bound_not_visually_accepted(self):
        receipt = self.receipt
        self.assertEqual((receipt["unit"], receipt["locale"], receipt["result"]), (UNIT, "mr-Deva-IN", "PASS"))
        self.assertEqual(receipt["source_sha256"], PINS["translations/MR-BRIDGE-024.xml"][1])
        self.assertEqual(receipt["config_sha256"], PINS["units/MR-BRIDGE-024.json"][1])
        self.assertEqual(receipt["provenance_lock_sha256"], PINS["provenance/MR-BRIDGE-024.lock.json"][1])
        self.assertEqual((receipt["html_bytes"], receipt["html_sha256"]), PINS["output/MR-BRIDGE-024.html"])
        self.assertEqual(
            (
                receipt["selected_source_blocks"],
                receipt["pinned_witnesses_checked"],
                receipt["displayed_math_regressions"],
                receipt["local_links_checked"],
                receipt["optional_external_citation_links"],
                receipt["unique_ids"],
                receipt["embedded_image_count"],
            ),
            (17, 45, 32, 17, 6, 62, 2),
        )
        self.assertIn("visual browser QA", receipt["not_claimed"])
        self.assertIn("human expert or native-speaker approval", receipt["not_claimed"])

    def test_27_helpers_reject_unsafe_or_false_equivalence(self):
        with self.assertRaises(ValueError):
            unique([("x", 1), ("x", 2)])
        with self.assertRaises(ValueError):
            inside(BASE, "../escape")
        with self.assertRaises(ValueError):
            jpeg_size(b"not a jpeg")
        with self.assertRaises(ValueError):
            mathml(E.fromstring(f'<math xmlns="{M[1:-1]}"><mphantom /></math>'))
        self.assertNotEqual(line_value(1, -1, 1, (-2, -1)), line_value(2, -1, 5, (-2, -1)))
        self.assertNotEqual(semantic_math("x-y=-1"), semantic_math("x-y=1"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
