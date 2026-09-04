"""Independent MR026 source, mathematics, image, and artifact regression.

The suite reads the two complete pinned m81427 modules, every frozen bilingual
fragment, every original EN/ID image, the Marathi source/config/lock/receipt,
and the final structural HTML.  Constants below are reviewer-owned evidence;
no builder/freezer helper is imported.  This is deliberately not browser,
layout, PDF, native-speaker, or teacher acceptance.
"""

from __future__ import annotations

import base64
from fractions import Fraction as F
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unicodedata
import unittest
import xml.etree.ElementTree as E
import zipfile


BASE = Path(__file__).resolve().parents[1]
WORKSPACE = BASE.parent
UNIT = "MR-BRIDGE-026"
C = "{http://cnx.rice.edu/cnxml}"
MD = "{http://cnx.rice.edu/mdml}"
M = "{http://www.w3.org/1998/Math/MathML}"

# Updated only after the independent review is rerun against final bytes.
PINS = {
    "translations/MR-BRIDGE-026.xml": (
        26973,
        "f90d539d816a180694a3bca98f128de26ae6d66f21ca90eb8f68b8d6e86c328d",
    ),
    "units/MR-BRIDGE-026.json": (
        5583,
        "4631a274d8f47e971434473ddd3f4ad871a7a322dc1b3c2eb43d4242bf13c86a",
    ),
    "provenance/MR-BRIDGE-026.lock.json": (
        58670,
        "1ce2f87d48e078611264fc1734d03d24ddbf1728d9f0ac2092ceef7c1b177eec",
    ),
    "qa/MR-BRIDGE-026-build-receipt.json": (
        6046,
        "b4f1854bb4a2c90899e8a4e2720dc482eeb7425b98324e8814d24b0e75a6aff2",
    ),
    "qa/MR-BRIDGE-026-drafting-notes.md": (
        13314,
        "0e484a4312421608233523e240bf728ea57026f6be352eed6d8cab33239c1ef3",
    ),
    "output/MR-BRIDGE-026.html": (
        613346,
        "df2c0a2c7900dd62f19f24f545b91621ee266c30248c2bd25213c0c83c51f261",
    ),
}

ARCHIVES = {
    "en": (
        "A20-canonical.zip",
        "osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9",
        537455794,
        "effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917",
    ),
    "id": (
        "A20-v0.3.0-source.zip",
        "source",
        106658915,
        "a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7",
    ),
}
MODULE_PINS = {
    "en": (166406, "2f3b5391a9845dc34cccb4c903ee25f2b4f23eceef25ee574d36ebe224b163e5"),
    "id": (168909, "2efbe62eb5cc35c1e1b51cf591cd52f234d8241c368e86573a3bcb350661c112"),
}

WRAPPER = "fs-id1167834233994"
NEXT = "fs-id1167834222378"
NEXT_FIRST = "fs-id1167834132598"
SELECTORS = [
    "fs-id1167834234000",
    "fs-id1167835334266",
    "fs-id1167835334269",
    "fs-id1167827943012",
    "fs-id1167834063721",
    "fs-id1167834301188",
    "fs-id1167835328722",
    "fs-id1167834099143",
    "fs-id1167835363503",
    "fs-id1167830925047",
    "fs-id1167835415479",
    "fs-id1167835415482",
    "fs-id1167826782993",
    "fs-id1167834536415",
]
EXERCISES = [
    ("fs-id1167835328724", "fs-id1167835328726", "fs-id1167835332322"),
    ("fs-id1167835594824", "fs-id1167835594827", "fs-id1167834533520"),
    ("fs-id1167835363506", "fs-id1167835363508", "fs-id1167832016014"),
    ("fs-id1167832057897", "fs-id1167832057899", "fs-id1167835595520"),
    ("fs-id1167826782996", "fs-id1167826782998", "fs-id1167834523798"),
    ("fs-id1167835360488", "fs-id1167835360490", "fs-id1167835351996"),
]

SOURCE_MATH_KEYS = [
    "intro-system",
    "example1-system",
    "try1-system",
    "try1-answer",
    "try2-system",
    "try2-answer",
    "example2-system",
    "table-expression-1",
    "table-expression-2",
    "table-x-value",
    "table-first-equation",
    "table-ordered-pair",
    "table-solution-pair",
    "try3-system",
    "try3-answer",
    "try4-system",
    "try4-answer",
]

EXPECTED_MATH = {
    "intro-system": "{ 2x + y = 7; x − 2y = 6 }",
    "example1-system": "{ 2x + y = 7; x − 2y = 6 }",
    "img009a-equation": "2x + y = 7",
    "img009a-result": "y = 7 − 2x",
    "img009b-substitution": "x − 2(7 − 2x) = 6",
    "img009c-line1": "x − 2(7 − 2x) = 6",
    "img009c-line2": "x − 14 + 4x = 6",
    "img009c-line3": "5x = 20",
    "img009c-result": "x = 4",
    "img009d-source": "2x + y = 7",
    "img009d-line1": "2(4) + y = 7",
    "img009d-line2": "8 + y = 7",
    "img009d-result": "y = −1",
    "img009e-form": "(x, y)",
    "img009e-pair": "(4, −1)",
    "img009f-values": "x = 4, y = −1",
    "img009f-check1": "2(4) + (−1) = 7",
    "img009f-check2": "4 − 2(−1) = 6",
    "img009f-answer": "(4, −1)",
    "try1-system": "{ −2x + y = −11; x + 3y = 9 }",
    "try1-answer": "(6, 1)",
    "try2-system": "{ 2x + y = −1; 4x + 3y = 3 }",
    "try2-answer": "(−3, 5)",
    "example2-system": "{ 4x + 2y = 4; 6x − y = 8 }",
    "img010b-system": "{ 4x + 2y = 4; 6x − y = 8 }",
    "table-expression-1": "−2x + 2",
    "img010c-line1": "4x + 2y = 4",
    "img010c-line2": "2y = −4x + 4",
    "img010c-result": "y = −2x + 2",
    "table-expression-2": "−2x + 2",
    "img010d-equation": "6x − (−2x + 2) = 8",
    "img010e-line1": "6x + 2x − 2 = 8",
    "img010e-line2": "8x − 2 = 8",
    "img010e-line3": "8x = 10",
    "img010e-result": "x = 5/4",
    "table-x-value": "x = 5/4",
    "table-first-equation": "4x + 2y = 4",
    "img010f-line1": "4(5/4) + 2y = 4",
    "img010f-line2": "5 + 2y = 4",
    "img010f-line3": "2y = −1",
    "img010f-result": "y = −1/2",
    "table-ordered-pair": "(5/4, −1/2)",
    "img010a-check1": "4(5/4) + 2(−1/2) = 4",
    "img010a-check2": "6(5/4) − (−1/2) = 8",
    "table-solution-pair": "(5/4, −1/2)",
    "try3-system": "{ x − 4y = −4; −3x + 4y = 0 }",
    "try3-answer": "(2, 3/2)",
    "try4-system": "{ 4x − y = 0; 2x − 3y = 5 }",
    "try4-answer": "(−1/2, −2)",
}

IMAGE_ORDER = [
    "CNX_IntAlg_Figure_04_01_009a_img_new.jpg",
    "CNX_IntAlg_Figure_04_01_009b_img_new.jpg",
    "CNX_IntAlg_Figure_04_01_009c_img_new.jpg",
    "CNX_IntAlg_Figure_04_01_009d_img_new.jpg",
    "CNX_IntAlg_Figure_04_01_009e_img_new.jpg",
    "CNX_IntAlg_Figure_04_01_009f_img_new.jpg",
    "CNX_IntAlg_Figure_04_01_010b_img.jpg",
    "CNX_IntAlg_Figure_04_01_010c_img.jpg",
    "CNX_IntAlg_Figure_04_01_010d_img.jpg",
    "CNX_IntAlg_Figure_04_01_010e_img.jpg",
    "CNX_IntAlg_Figure_04_01_010f_img.jpg",
    "CNX_IntAlg_Figure_04_01_010a_img.jpg",
]
FIGURES = [
    ("fs-id1167835332325", IMAGE_ORDER[0]),
    ("fs-id1167834567460", IMAGE_ORDER[1]),
    ("fs-id1167835198382", IMAGE_ORDER[2]),
    ("fs-id1167835229691", IMAGE_ORDER[3]),
    ("fs-id1167832066001", IMAGE_ORDER[4]),
    ("fs-id1167831086582", IMAGE_ORDER[5]),
    ("fs-id1167835254444", IMAGE_ORDER[6]),
    ("fs-id1167835379481", IMAGE_ORDER[7]),
    ("fs-id1167831239705", IMAGE_ORDER[8]),
    ("fs-id1167834432973", IMAGE_ORDER[9]),
    ("fs-id1167835609313", IMAGE_ORDER[10]),
    ("fs-id1167835175410", IMAGE_ORDER[11]),
]

IMAGES = {
    "CNX_IntAlg_Figure_04_01_009a_img_new.jpg": {
        "en": (41822, "e60e5f1ceceae3b4e0d699baeeee3312261e3a869a2582c4fb59e28a2f70fc6c", (818, 146)),
        "id": (88070, "1715d39200f25311444a902b703d00021a0638e4aa0240e6ed2ddf393d39274f", (1540, 500)),
    },
    "CNX_IntAlg_Figure_04_01_009b_img_new.jpg": {
        "en": (38626, "57d7b4a848363c90cd25c828455afd01da0c27a42591989867d4e42048bc0d07", (818, 95)),
        "id": (85264, "95c3d2c8ede0cc819288eac847c95b159789dc192b5f95a5fcefd702c7ff85be", (1540, 460)),
    },
    "CNX_IntAlg_Figure_04_01_009c_img_new.jpg": {
        "en": (41821, "5a0f118bcdace3e96db74aa5b94bc84654232cacc92d80dd6fc21f84f5bc7918", (818, 157)),
        "id": (88961, "6513c95ac493bf42dc54744ce48ebfc2fff875efa703ff11f09b91c3feea6ca3", (1540, 520)),
    },
    "CNX_IntAlg_Figure_04_01_009d_img_new.jpg": {
        "en": (43604, "95771946cbd1901b365d5e9320b3b09036231012bcedcf4468d400f779c10e9a", (818, 157)),
        "id": (93224, "8a98759c5aa2c796c567a5ee9155c9e01c101e156f378e34bed990168787d077", (1540, 500)),
    },
    "CNX_IntAlg_Figure_04_01_009e_img_new.jpg": {
        "en": (28967, "ed24eb754a4b1a395292ae29c675ed4144f59a4856718299c083f73c2021a489", (818, 72)),
        "id": (65336, "6ccac607289a38358df64857985e17649f97b69f085a22ed8eafd2ac952c2ba3", (1540, 340)),
    },
    "CNX_IntAlg_Figure_04_01_009f_img_new.jpg": {
        "en": (56413, "5a1505b1327c9aecc2b54c6f74a609b6125434dd2fbaa97f7e3986fd7dc5e9ed", (818, 199)),
        "id": (125663, "ee6fa89a39da77c10648d3ab49467b0725dd2c3866223ada83e460366a4bc45e", (1540, 640)),
    },
    "CNX_IntAlg_Figure_04_01_010b_img.jpg": {
        "en": (17872, "255356d19663a7d38445cf7669ab437ff3a1fb854ddf7a76cb5058c7999d9af6", (195, 43)),
        "id": (64546, "66e5303ed5468fefee90dc0a19a5a17b72e40ad3513a76265e9c825ca51290b6", (1240, 776)),
    },
    "CNX_IntAlg_Figure_04_01_010c_img.jpg": {
        "en": (35148, "cc11a5a5a0cfe2fcf9a990a52e790d7835db49c6ccceb0f2b9dd6026ca612f43", (195, 100)),
        "id": (94727, "c56cb21370bdcbd13e2a44336cdf09b3dbecebcf118c7fa719a23d8caa8cc578", (1240, 960)),
    },
    "CNX_IntAlg_Figure_04_01_010d_img.jpg": {
        "en": (18145, "cba1f32666b3947d745103afff99d2b128c664a6fccff89a35cd97fe57062ef9", (195, 15)),
        "id": (38273, "8ca2c74ade8f3a567e3f68d00e08fe41c8a04688dab5d2a600fec304a759927b", (1240, 448)),
    },
    "CNX_IntAlg_Figure_04_01_010e_img.jpg": {
        "en": (35533, "92e3719364ef59ef144496c2b839e6a71b86747284a987974ea524e3f4e930ef", (195, 111)),
        "id": (104434, "e1d7e60ce393477b2867b3b92c9d7275790696eb2a34f425080eec191827e3ba", (1240, 1092)),
    },
    "CNX_IntAlg_Figure_04_01_010f_img.jpg": {
        "en": (33127, "70a8e249ca6fca1d96566c939fc5bc855b57215e7258c284d14047755ae1e249", (195, 130)),
        "id": (104521, "7a89a70aefb72876bc193cc7ad58f3c71f629dc08820de86669f432cbd7406c0", (1200, 1240)),
    },
    "CNX_IntAlg_Figure_04_01_010a_img.jpg": {
        "en": (45701, "7adfc3ac37e9aa83f9c477d05c6b31830fabab442758a97771f23e3a1a8948f5", (323, 179)),
        "id": (78481, "72231763f88d78317148eb6015d3f25cf388d6512709de25bb58c2445f009973", (1240, 815)),
    },
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def inside(base: Path, relative: str) -> Path:
    path = (base / relative).resolve()
    root = base.resolve()
    if path == root or root not in path.parents:
        raise ValueError("path escape")
    return path


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def normalized_text(node: E.Element) -> str:
    return re.sub(r"\s+", " ", "".join(node.itertext())).strip()


def id_map(root: E.Element) -> dict[str, E.Element]:
    pairs = [(node.get("id"), node) for node in root.iter() if node.get("id")]
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate XML id")
    return result


def parent_map(root: E.Element):
    return {child: parent for parent in root.iter() for child in parent}


def nearest_source_parent(node, parents, allowed):
    while node in parents:
        node = parents[node]
        if node.get("id") in allowed:
            return node.get("id")
    return None


def shape(node: E.Element):
    return (
        node.tag,
        tuple(sorted(node.attrib.items())),
        node.text,
        tuple((shape(child), child.tail) for child in node),
    )


def mathml(node: E.Element) -> str:
    name = local(node.tag)
    if name in {"mi", "mn", "mo", "mtext"}:
        if len(node):
            raise ValueError("MathML token has children")
        return node.text or ""
    if name in {"math", "mrow", "mtd"}:
        return "".join(mathml(child) for child in node)
    if name == "mspace":
        return ""
    if name == "mfrac" and len(node) == 2:
        return "(" + mathml(node[0]) + "/" + mathml(node[1]) + ")"
    if name == "mfenced":
        return (
            node.get("open", "(")
            + node.get("separators", ",").join(mathml(child) for child in node)
            + node.get("close", ")")
        )
    if name == "mtr":
        return "".join(mathml(child) for child in node)
    if name == "mtable":
        return ";".join(filter(None, (mathml(child) for child in node)))
    raise ValueError("unsupported MathML " + name)


def semantic_math(value: str) -> str:
    value = re.sub(r"\s+", "", value).replace("−", "-")
    value = value.replace("{", "").replace("}", "")
    value = re.sub(r"\((-?\d+/-?\d+)\)", r"\1", value)
    return value.rstrip(".,;?")


def jpeg_size(data: bytes) -> tuple[int, int]:
    if not data.startswith(b"\xff\xd8\xff"):
        raise ValueError("not JPEG")
    index = 2
    start_of_frame = {
        0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
        0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF,
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
        length = int.from_bytes(data[index:index + 2], "big")
        if length < 2 or index + length > len(data):
            raise ValueError("bad JPEG segment")
        if marker in start_of_frame:
            height = int.from_bytes(data[index + 3:index + 5], "big")
            width = int.from_bytes(data[index + 5:index + 7], "big")
            return width, height
        index += length
    raise ValueError("JPEG dimensions missing")


def solve(a1, b1, c1, a2, b2, c2):
    a1, b1, c1, a2, b2, c2 = map(F, (a1, b1, c1, a2, b2, c2))
    determinant = a1 * b2 - a2 * b1
    if determinant == 0:
        raise ValueError("non-unique system")
    return (
        (c1 * b2 - c2 * b1) / determinant,
        (a1 * c2 - a2 * c1) / determinant,
    )


class HTMLFacts(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.hrefs = []
        self.sources = []
        self.images = []
        self.tags = []
        self.meta = []

    def handle_starttag(self, tag, attrs):
        self._record(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self._record(tag, attrs)

    def _record(self, tag, attrs):
        values = dict(attrs)
        self.tags.append(tag)
        if values.get("id"):
            self.ids.append(values["id"])
        if values.get("href"):
            self.hrefs.append(values["href"])
        if values.get("data-source"):
            self.sources.append(values["data-source"])
        if tag == "img":
            self.images.append(values)
        if tag == "meta":
            self.meta.append(values)


class Unit26IndependentReview(unittest.TestCase):
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
        cls.notes = (BASE / f"qa/{UNIT}-drafting-notes.md").read_text(encoding="utf-8")
        cls.check_nodes = [node for node in cls.root.iter() if node.get("data-check")]
        cls.checks = {node.get("data-check"): normalized_text(node) for node in cls.check_nodes}
        cls.archive_paths = {}
        cls.modules = {}
        cls.source_roots = {}
        cls.source = {}
        cls.archive_images = {}
        for locale, (archive_name, prefix, _, _) in ARCHIVES.items():
            archive = WORKSPACE / "downloads/mr-Deva-IN/releases" / archive_name
            cls.archive_paths[locale] = archive
            with zipfile.ZipFile(archive) as zf:
                module = zf.read(f"{prefix}/modules/m81427/index.cnxml")
                for name in IMAGES:
                    cls.archive_images[(locale, name)] = zf.read(f"{prefix}/media/{name}")
            cls.modules[locale] = module
            cls.source_roots[locale] = E.fromstring(module)
            cls.source[locale] = id_map(cls.source_roots[locale])
        cls.html_raw = (BASE / f"output/{UNIT}.html").read_bytes()
        cls.html = HTMLFacts()
        cls.html.feed(cls.html_raw.decode("utf-8"))

    def test_01_exact_reviewed_artifact_pins(self):
        for relative, expected in PINS.items():
            data = (BASE / relative).read_bytes()
            self.assertEqual((len(data), sha(data)), expected, relative)

    def test_02_complete_archives_modules_and_metadata(self):
        titles = {
            "en": "Solve Systems of Linear Equations with Two Variables",
            "id": "Menyelesaikan Sistem Persamaan Linear dengan Dua Variabel",
        }
        for locale, (_, _, archive_bytes, archive_digest) in ARCHIVES.items():
            self.assertEqual(
                (self.archive_paths[locale].stat().st_size, sha_file(self.archive_paths[locale])),
                (archive_bytes, archive_digest),
            )
            self.assertEqual((len(self.modules[locale]), sha(self.modules[locale])), MODULE_PINS[locale])
            root = self.source_roots[locale]
            metadata = root.find(C + "metadata")
            self.assertEqual(root.findtext(C + "title"), titles[locale])
            self.assertEqual(metadata.findtext(MD + "content-id"), "m81427")
            self.assertEqual(metadata.findtext(MD + "uuid"), "b9f8475e-9490-4f24-995f-2923b1ed9644")
            self.assertEqual(metadata.findtext(MD + "title"), titles[locale])
            self.assertEqual(
                root.get("{http://www.w3.org/XML/1998/namespace}lang"),
                None if locale == "en" else "id-ID",
            )

    def test_03_exact_complete_wrapper_and_next_sibling(self):
        titles = {
            "en": "Solve a System of Equations by Substitution",
            "id": "Menyelesaikan Sistem Persamaan dengan Substitusi",
        }
        next_titles = {
            "en": "Solve a System of Equations by Elimination",
            "id": "Menyelesaikan Sistem Persamaan dengan Eliminasi",
        }
        for locale in ARCHIVES:
            wrapper = self.source[locale][WRAPPER]
            self.assertEqual(wrapper.findtext(C + "title"), titles[locale])
            children = [node for node in wrapper if node.tag != C + "title"]
            self.assertEqual([node.get("id") for node in children], SELECTORS)
            parent = next(node for node in self.source_roots[locale].iter() if wrapper in list(node))
            following = list(parent)[list(parent).index(wrapper) + 1]
            self.assertEqual(following.get("id"), NEXT)
            self.assertEqual(following.findtext(C + "title"), next_titles[locale])
            self.assertEqual(next(node.get("id") for node in following.iter() if node.get("id")), NEXT)
            descendants = [node.get("id") for node in following.iter() if node.get("id")]
            self.assertEqual(descendants[1], NEXT_FIRST)

    def test_04_exact_fourteen_selection_order_and_wrapper_contract(self):
        expected = ["A20:m81427#" + ident for ident in SELECTORS]
        self.assertEqual(
            [node.get("data-source") for node in self.root.iter() if node.get("data-source")],
            expected,
        )
        self.assertEqual([item["locator"] for item in self.lock["source_selections"]], expected)
        self.assertEqual([item["target_id"] for item in self.lock["source_selections"]], SELECTORS)
        self.assertIsNone(self.target[WRAPPER].get("data-source"))

    def test_05_all_twenty_eight_fragments_match_archive_nodes(self):
        count = 0
        byte_count = 0
        for selection in self.lock["source_selections"]:
            self.assertEqual([record["locale"] for record in selection["sources"]], ["en", "id"])
            for record in selection["sources"]:
                locale = record["locale"]
                fragment = inside(BASE, record["fragment_path"]).read_bytes()
                source_node = self.source[locale][selection["target_id"]]
                self.assertEqual(sha(fragment), record["fragment_sha256"])
                self.assertEqual(shape(E.fromstring(fragment)), shape(source_node))
                self.assertEqual(record["module_sha256"], MODULE_PINS[locale][1])
                self.assertEqual(record["archive_sha256"], ARCHIVES[locale][3])
                self.assertEqual(
                    record["math_sha256"],
                    [sha(E.tostring(node, encoding="utf-8")) for node in source_node.iter(M + "math")],
                )
                self.assertEqual(record["outgoing_urls"], [])
                count += 1
                byte_count += len(fragment)
        self.assertEqual((count, byte_count), (28, 33776))

    def test_06_all_forty_nine_lock_witnesses_are_exact(self):
        witnesses = self.lock["witnesses"]
        self.assertEqual(len(witnesses), 49)
        self.assertEqual(len({entry["path"] for entry in witnesses}), 49)
        for entry in witnesses:
            data = inside(BASE, entry["path"]).read_bytes()
            self.assertEqual((len(data), sha(data)), (entry["bytes"], entry["sha256"]), entry["path"])

    def test_07_exact_fifty_eight_source_ids_order_and_ancestry(self):
        locale_orders = {}
        for locale in ARCHIVES:
            order = [node.get("id") for node in self.source[locale][WRAPPER].iter() if node.get("id")]
            self.assertEqual((len(order), len(set(order))), (58, 58))
            locale_orders[locale] = order
        self.assertEqual(locale_orders["en"], locale_orders["id"])
        order = locale_orders["en"]
        allowed = set(order)
        target_order = [node.get("id") for node in self.root.iter() if node.get("id") in allowed]
        self.assertEqual(target_order, order)
        self.assertEqual(set(self.target) - allowed, {UNIT, "credits"})
        self.assertEqual(len(self.target), 60)
        for locale in ARCHIVES:
            parents = parent_map(self.source_roots[locale])
            for ident in order:
                self.assertEqual(
                    nearest_source_parent(self.source[locale][ident], parents, allowed),
                    nearest_source_parent(self.target[ident], self.target_parents, allowed),
                    (locale, ident),
                )

    def test_08_six_complete_source_problem_solution_pairs_and_links(self):
        for locale in ARCHIVES:
            source = self.source[locale]
            actual = []
            for exercise_id, _, _ in EXERCISES:
                exercise = source[exercise_id]
                actual.append(
                    (
                        exercise.get("id"),
                        exercise.find(C + "problem").get("id"),
                        exercise.find(C + "solution").get("id"),
                    )
                )
            self.assertEqual(actual, EXERCISES)
        for exercise_id, problem_id, solution_id in EXERCISES:
            self.assertEqual(self.target[exercise_id].tag, "section")
            self.assertEqual(self.target[problem_id].get("class"), "problem")
            self.assertEqual(self.target[solution_id].get("class"), "solution")
            self.assertEqual(len(self.target[problem_id].findall(f".//a[@href='#{solution_id}']")), 1)
            self.assertEqual(len(self.target[solution_id].findall(f".//a[@href='#{problem_id}']")), 1)

    def test_09_config_census_is_exact(self):
        expected = {
            "source_count": 14,
            "translated_worked_examples": 2,
            "translated_definitions": 0,
            "translated_practice_items": 4,
            "translated_resource_notes": 0,
            "original_practice_items": 0,
        }
        for key, value in expected.items():
            self.assertEqual(self.config[key], value)
        self.assertEqual(self.config["question_ids"], [])

    def test_10_all_seventeen_source_math_occurrences_match_bilingually(self):
        expected = [semantic_math(EXPECTED_MATH[key]) for key in SOURCE_MATH_KEYS]
        for locale in ARCHIVES:
            actual = []
            for ident in SELECTORS:
                actual.extend(mathml(node) for node in self.source[locale][ident].iter(M + "math"))
            self.assertEqual(len(actual), 17)
            self.assertEqual([semantic_math(value) for value in actual], expected)

    def test_11_all_forty_nine_display_checks_are_independently_constant(self):
        self.assertEqual((len(self.check_nodes), len(self.checks)), (49, 49))
        self.assertEqual(self.checks, EXPECTED_MATH)
        self.assertEqual(self.config["expected_math"], EXPECTED_MATH)

    def test_12_recompute_all_six_supplied_solutions(self):
        cases = [
            ((2, 1, 7, 1, -2, 6), (F(4), F(-1)), "img009f-answer"),
            ((-2, 1, -11, 1, 3, 9), (F(6), F(1)), "try1-answer"),
            ((2, 1, -1, 4, 3, 3), (F(-3), F(5)), "try2-answer"),
            ((4, 2, 4, 6, -1, 8), (F(5, 4), F(-1, 2)), "table-solution-pair"),
            ((1, -4, -4, -3, 4, 0), (F(2), F(3, 2)), "try3-answer"),
            ((4, -1, 0, 2, -3, 5), (F(-1, 2), F(-2)), "try4-answer"),
        ]
        for coefficients, expected, key in cases:
            self.assertEqual(solve(*coefficients), expected)
            a1, b1, c1, a2, b2, c2 = map(F, coefficients)
            x, y = expected
            self.assertEqual((a1 * x + b1 * y, a2 * x + b2 * y), (c1, c2))
            self.assertIn(EXPECTED_MATH[key], self.config["expected_math"].values())

    def test_13_recompute_every_first_worked_step(self):
        self.assertEqual(F(7) - 2 * F(4), F(-1))
        self.assertEqual(F(4) - 2 * (F(7) - 2 * F(4)), F(6))
        self.assertEqual(F(4) - 14 + 4 * F(4), F(6))
        self.assertEqual(5 * F(4), F(20))
        self.assertEqual(2 * F(4) + F(-1), F(7))
        self.assertEqual(F(4) - 2 * F(-1), F(6))

    def test_14_recompute_every_fractional_worked_step_and_denominator(self):
        x = F(5, 4)
        y = F(-1, 2)
        self.assertEqual(-2 * x + 2, y)
        self.assertEqual(6 * x - (-2 * x + 2), F(8))
        self.assertEqual(6 * x + 2 * x - 2, F(8))
        self.assertEqual(8 * x - 2, F(8))
        self.assertEqual(8 * x, F(10))
        self.assertEqual(4 * x + 2 * y, F(4))
        self.assertEqual(6 * x, F(15, 2))
        self.assertNotEqual(6 * x, F(15, 4))
        self.assertEqual(F(15, 2) - F(-1, 2), F(16, 2))
        self.assertEqual(F(16, 2), F(8))

    def test_15_all_source_answers_are_retained_and_none_invented(self):
        answer_ids = [solution for _, _, solution in EXERCISES]
        for locale in ARCHIVES:
            for answer_id in answer_ids:
                self.assertIn(answer_id, self.source[locale])
        decoded = self.raw.decode("utf-8")
        self.assertNotIn("source-answer-missing", decoded)
        self.assertNotIn("data-kind=\"original-answer\"", decoded)

    def test_16_exact_eight_row_table_and_nonlexical_image_order(self):
        for locale in ARCHIVES:
            table = self.source[locale]["fs-id1167826998205"]
            rows = table.findall(f".//{C}row")
            self.assertEqual((len(rows), sum(len(row.findall(C + "entry")) for row in rows)), (8, 16))
            refs = [Path(image.get("src")).name for image in table.iter(C + "image")]
            self.assertEqual(refs, IMAGE_ORDER[6:])
        target_table = self.target["fs-id1167826998205"]
        self.assertEqual((len(target_table.findall(".//tr")), len(target_table.findall(".//td"))), (8, 16))
        self.assertEqual([image.get("src").removeprefix("asset:") for image in target_table.iter("img")], IMAGE_ORDER[6:])

    def test_17_all_twenty_four_source_images_review_copies_and_assets(self):
        records = self.lock["source_images"]
        self.assertEqual(len(records), 24)
        self.assertEqual(len({(item["locale"], Path(item["member"]).name) for item in records}), 24)
        totals = {"en": 0, "id": 0}
        for record in records:
            locale = record["locale"]
            name = Path(record["member"]).name
            data = self.archive_images[(locale, name)]
            size, digest, dimensions = IMAGES[name][locale]
            self.assertEqual((len(data), sha(data), jpeg_size(data)), (size, digest, dimensions))
            self.assertEqual((record["bytes"], record["sha256"]), (size, digest))
            self.assertEqual(inside(WORKSPACE, record["review_copy"]).read_bytes(), data)
            totals[locale] += len(data)
            if locale == "en":
                asset = inside(BASE, record["committed_asset"]).read_bytes()
                self.assertEqual(asset, data)
                self.assertEqual(
                    self.config["assets"][name],
                    {"path": f"assets/{UNIT}/{name}", "sha256": digest, "mime": "image/jpeg"},
                )
            else:
                self.assertNotEqual(data, self.archive_images[("en", name)])
        self.assertEqual(totals, {"en": 436779, "id": 1031500})

    def test_18_exact_twelve_target_figures_refs_alts_and_captions(self):
        self.assertEqual([image.get("src").removeprefix("asset:") for image in self.root.iter("img")], IMAGE_ORDER)
        for figure_id, name in FIGURES:
            figure = self.target[figure_id]
            self.assertEqual(figure.tag, "figure")
            image = figure.find("img")
            self.assertEqual(image.get("src"), "asset:" + name)
            self.assertTrue(re.search("[\u0900-\u097f]", image.get("alt", "")))
            self.assertIsNotNone(figure.find("figcaption"))

    def test_19_bilingual_010a_source_error_is_visibly_disclosed(self):
        # Manual original-pixel review established that both byte-pinned rasters
        # print 15/4, while 6*(5/4) is 15/2.  The accessible correction must say
        # both what the image prints and what the arithmetic requires.
        alt = self.target["fs-id1167835175410"].find("img").get("alt")
        for token in ["15/4", "15/2", "EN", "ID"]:
            self.assertIn(token, alt)
        self.assertTrue(any(word in alt for word in ["चूक", "चुकीने", "दुरुस्त"]))
        correction_notes = " ".join(
            normalized_text(node)
            for node in self.root.findall(".//*[@data-kind='original']")
            if "010a" in normalized_text(node)
        )
        for token in ["010a", "15/4", "15/2", "EN", "ID"]:
            self.assertIn(token, correction_notes)
        self.assertTrue(any(word in correction_notes for word in ["चूक", "चुकीने", "दुरुस्त"]))
        for token in ["010a", "15/4", "15/2", "EN", "ID", "source"]:
            self.assertIn(token.lower(), self.notes.lower())
        self.assertNotIn("pixel-accurate `15/2`", self.notes)
        self.assertNotIn("target-only alt", self.notes)

    def test_20_marathi_image_transcripts_match_all_other_viewed_pixels(self):
        alts = {name: self.target[figure].find("img").get("alt") for figure, name in FIGURES}
        markers = {
            IMAGE_ORDER[0]: ["2x + y = 7", "y = 7 − 2x", "लाल"],
            IMAGE_ORDER[1]: ["x − 2(7 − 2x) = 6", "लाल"],
            IMAGE_ORDER[2]: ["x − 14 + 4x = 6", "5x = 20", "x = 4"],
            IMAGE_ORDER[3]: ["2(4) + y = 7", "8 + y = 7", "y = −1"],
            IMAGE_ORDER[4]: ["(x, y)", "(4, −1)"],
            IMAGE_ORDER[5]: ["2(4) + (−1) = 7", "4 − 2(−1) = 6", "(4, −1)"],
            IMAGE_ORDER[6]: ["4x + 2y = 4", "6x − y = 8"],
            IMAGE_ORDER[7]: ["2y = −4x + 4", "y = −2x + 2", "लाल"],
            IMAGE_ORDER[8]: ["6x − (−2x + 2) = 8", "लाल"],
            IMAGE_ORDER[9]: ["8x − 2 = 8", "8x = 10", "x = 5/4"],
            IMAGE_ORDER[10]: ["4(5/4) + 2y = 4", "2y = −1", "y = −1/2"],
        }
        for name, expected in markers.items():
            for marker in expected:
                self.assertIn(marker, alts[name], (name, marker))

    def test_21_complete_method_prose_and_six_steps_are_source_faithful(self):
        target = normalized_text(self.root)
        for phrase in [
            "आता रेषीय समीकरणांच्या प्रणाली प्रतिस्थापन पद्धतीने सोडवू",
            "आलेख काढताना प्रथम वापरलेली तीच प्रणाली",
            "कोणतेही समीकरण आणि कोणताही चल निवडता येतो",
            "गणना सोपी राहील अशी निवड",
            "मिळालेली राशी दुसऱ्या समीकरणात प्रतिस्थापित",
            "फक्त एक चल असलेले समीकरण",
            "दोन्ही समीकरणे सत्य करते याची तपासणी",
            "पुढील उदाहरणात चिन्हांची विशेष काळजी",
        ]:
            self.assertIn(phrase, target)
        steps = [normalized_text(item) for item in self.target["fs-id1167830925054"].findall("li")]
        self.assertEqual(len(steps), 6)
        self.assertIn("राशी दुसऱ्या समीकरणात प्रतिस्थापित", steps[1])
        self.assertIn("क्रमित जोडी", steps[4])
        self.assertIn("दोन्ही मूळ समीकरणांची उकल", steps[5])

    def test_22_canon_pins_terms_and_authored_limits_are_honest(self):
        canon = {
            "downloads/mr-Deva-IN/canon/pages/balbharati8-85.png": (
                255250, "284d9c7e4dc21f183189750421e65c97acfae02fd642df0457321cfe627a7f69"
            ),
            "downloads/mr-Deva-IN/canon/ocr/balbharati8-85.txt": (
                2474, "f9bf9c42edb3e126573bc14f4671aa5c062920ee145c50590fdac6733af52a9b"
            ),
            "downloads/mr-Deva-IN/canon/pages/balbharati8-86.png": (
                195482, "87e2c859c7d3445466e28b1050bb86bc52b1014fb6f2dd2c75d356dda620ce49"
            ),
            "downloads/mr-Deva-IN/canon/ocr/balbharati8-86.txt": (
                1539, "497332d70fb096c86e468261e37186b888099b86830234a26d5c86253188ee57"
            ),
        }
        for relative, expected in canon.items():
            data = inside(WORKSPACE, relative).read_bytes()
            self.assertEqual((len(data), sha(data)), expected)
        page85 = inside(WORKSPACE, "downloads/mr-Deva-IN/canon/ocr/balbharati8-85.txt").read_text(encoding="utf-8")
        for phrase in ["समीकरणाची उकल", "समीकरण सोडवणे", "दोन्ही बाजूंवर समान क्रिया", "शून्येतर"]:
            self.assertIn(phrase, page85)
        terminology = (BASE / "terminology.csv").read_text(encoding="utf-8")
        for row in [
            "T011,equation,समीकरण",
            "T013,solution,उकल",
            "T014,substitution,प्रतिस्थापन",
            "T016,ordered pair,क्रमित जोडी",
            "T046,system of linear equations,रेषीय समीकरणांची प्रणाली",
        ]:
            self.assertIn(row, terminology)
        note = normalized_text(next(node for node in self.root.iter("aside") if "संज्ञा-नोंद" in normalized_text(node)))
        for phrase in ["C12/C13", "प्रमाणित नाहीत", "तयार केलेली कार्यपदे", "अक्षरशः संज्ञा असल्याचा दावा नाही"]:
            self.assertIn(phrase, note)

    def test_23_all_links_resolve_and_external_links_are_exact(self):
        hrefs = [node.get("href") for node in self.root.iter("a")]
        local_links = [href for href in hrefs if href.startswith("#")]
        external = [href for href in hrefs if not href.startswith("#")]
        self.assertEqual(len(local_links), 16)
        for href in local_links:
            self.assertIn(href[1:], self.target)
        self.assertEqual(
            external,
            [
                "https://openstax.org/books/intermediate-algebra-2e/pages/4-1-solve-systems-of-linear-equations-with-two-variables",
                "https://creativecommons.org/licenses/by-nc-sa/4.0/",
            ],
        )

    def test_24_scope_counts_next_boundary_and_exclusion_are_explicit(self):
        all_text = normalized_text(self.root)
        credits = normalized_text(self.target["credits"])
        for phrase in [
            "14 थेट स्रोत-निवडी",
            "58 स्रोत-ओळखचिन्हे",
            "सहा प्रश्न व सहा पुरवलेली उत्तरे",
            "17 स्रोत MathML राशी",
            "12 स्रोत-आकृत्या",
            "आठ ओळी/सोळा कप्प्यांचा",
            NEXT,
            NEXT_FIRST,
            "येथे घेतलेला नाही",
        ]:
            self.assertIn(phrase, credits)
        for phrase in ["संपूर्ण module", "पाचही पुस्तकांचे काम पूर्ण झाल्याचा दावा नाही"]:
            self.assertIn(phrase, all_text)
        self.assertNotIn(f'id="{NEXT}"', self.raw.decode("utf-8"))
        self.assertNotIn(f'id="{NEXT_FIRST}"', self.raw.decode("utf-8"))

    def test_25_locale_unicode_offline_media_and_safe_structure(self):
        self.assertEqual((self.root.get("id"), self.root.get("lang")), (UNIT, "mr-Deva-IN"))
        decoded = self.raw.decode("utf-8")
        self.assertEqual(decoded, unicodedata.normalize("NFC", decoded))
        self.assertNotIn("\ufffd", decoded)
        for image in self.root.iter("img"):
            self.assertTrue(image.get("src").startswith("asset:"))
            self.assertTrue(image.get("alt"))
        for tag in ["script", "iframe", "object", "embed", "svg", "audio", "video"]:
            self.assertFalse(list(self.root.iter(tag)), tag)

    def test_26_receipt_cross_pins_counts_and_nonclaims(self):
        receipt = self.receipt
        self.assertEqual((receipt["unit"], receipt["locale"], receipt["result"]), (UNIT, "mr-Deva-IN", "PASS"))
        self.assertEqual(receipt["source_sha256"], PINS["translations/MR-BRIDGE-026.xml"][1])
        self.assertEqual(receipt["config_sha256"], PINS["units/MR-BRIDGE-026.json"][1])
        self.assertEqual(receipt["provenance_lock_sha256"], PINS["provenance/MR-BRIDGE-026.lock.json"][1])
        self.assertEqual((receipt["html_bytes"], receipt["html_sha256"]), PINS["output/MR-BRIDGE-026.html"])
        self.assertEqual(
            (
                receipt["selected_source_blocks"], receipt["pinned_witnesses_checked"],
                receipt["displayed_math_regressions"], receipt["local_links_checked"],
                receipt["optional_external_citation_links"], receipt["unique_ids"],
                receipt["embedded_image_count"], receipt["distinct_embedded_assets"],
            ),
            (14, 49, 49, 16, 2, 60, 12, 12),
        )
        self.assertIn("visual browser QA", receipt["not_claimed"])
        self.assertIn("human expert or native-speaker approval", receipt["not_claimed"])

    def test_27_structural_html_is_exact_and_embeds_canonical_bytes(self):
        xml_ids = [node.get("id") for node in self.root.iter() if node.get("id")]
        self.assertEqual(self.html.ids, xml_ids)
        self.assertEqual(self.html.sources, ["A20:m81427#" + ident for ident in SELECTORS])
        self.assertEqual(self.html.hrefs, [node.get("href") for node in self.root.iter("a")])
        xml_images = list(self.root.iter("img"))
        self.assertEqual(len(self.html.images), len(xml_images))
        for html_image, xml_image, name in zip(self.html.images, xml_images, IMAGE_ORDER):
            self.assertEqual(html_image["alt"], xml_image.get("alt"))
            self.assertTrue(html_image["src"].startswith("data:image/jpeg;base64,"))
            embedded = base64.b64decode(html_image["src"].split(",", 1)[1], validate=True)
            self.assertEqual(embedded, (BASE / f"assets/{UNIT}/{name}").read_bytes())
        csp = next(meta["content"] for meta in self.html.meta if meta.get("http-equiv") == "Content-Security-Policy")
        self.assertIn("default-src 'none'", csp)
        self.assertIn("img-src data:", csp)
        self.assertNotIn("script", self.html.tags)

    def test_28_adversarial_helpers_and_plausible_regressions(self):
        with self.assertRaises(ValueError):
            unique([("x", 1), ("x", 2)])
        with self.assertRaises(ValueError):
            inside(BASE, "../escape")
        with self.assertRaises(ValueError):
            jpeg_size(b"not a jpeg")
        with self.assertRaises(ValueError):
            mathml(E.fromstring(f'<math xmlns="{M[1:-1]}"><mphantom /></math>'))
        with self.assertRaises(ValueError):
            solve(1, 1, 2, 2, 2, 4)
        self.assertNotEqual(semantic_math("6x-y=8"), semantic_math("6x+y=8"))
        self.assertNotEqual(semantic_math("x=5/4"), semantic_math("x=5/2"))
        self.assertNotEqual(F(15, 4), F(15, 2))
        self.assertNotEqual(sha(b"source"), sha(b"sourc"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
