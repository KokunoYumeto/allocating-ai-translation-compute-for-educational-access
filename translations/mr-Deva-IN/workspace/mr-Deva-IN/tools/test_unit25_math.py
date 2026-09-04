"""Independent MR025 source, mathematics, media, and release regression.

This suite intentionally reopens the pinned EN/ID archives.  It does not treat
the unit configuration or build receipt as mathematical authority, and it does
not perform or imply browser/PDF visual acceptance.
"""

from __future__ import annotations

import base64
from copy import deepcopy
import hashlib
from html.parser import HTMLParser
import json
from fractions import Fraction
from pathlib import Path
import re
import unicodedata
import unittest
import xml.etree.ElementTree as E
import zipfile


BASE = Path(__file__).resolve().parents[1]
WORKSPACE = BASE.parent
UNIT = "MR-BRIDGE-025"
C = "{http://cnx.rice.edu/cnxml}"
MD = "{http://cnx.rice.edu/mdml}"
M = "{http://www.w3.org/1998/Math/MathML}"

PINS = {
    "translations/MR-BRIDGE-025.xml": (
        62861,
        "a585a299dc9fc23a22fb2735f239a497b28653947a4cc894fe40bf821deeb072",
    ),
    "units/MR-BRIDGE-025.json": (
        9394,
        "e78b3bf238c93bfb6871c300ca93df6b336c7b89487cd6c3ccc9f2eac03ecf8c",
    ),
    "provenance/MR-BRIDGE-025.lock.json": (
        137115,
        "6d7b76030c218a42dab05e307b06a33d0ddb6d0126912c935b667133072d8878",
    ),
    "qa/MR-BRIDGE-025-build-receipt.json": (
        9243,
        "78b783c72e76031367551d0a7f3d65839403cab48c25aac6559df7684ede7f67",
    ),
    "output/MR-BRIDGE-025.html": (
        1449777,
        "035ba56c25a5dcfb3655e0f7c0f1473d9916fe5cf36aba037f061589d9d02405",
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

WRAPPER = "fs-id1167832086919"
NEXT = "fs-id1167834233994"
SELECTORS = [
    "fs-id1167831893670",
    "fs-id1167831239781",
    "fs-id1167835267322",
    "fs-id1167832082005",
    "CNX_IntAlg_Figure_04_01_003",
    "fs-id1167834053646",
    "fs-id1167834279490",
    "fs-id1167832195749",
    "fs-id1167832065745",
    "fs-id1167826804684",
    "fs-id1167835310198",
    "fs-id1167832055393",
    "fs-id1167835410272",
    "fs-id1167832086965",
    "fs-id1167835366362",
    "fs-id1167834462906",
    "fs-id1167835307740",
    "fs-id1167835329190",
    "fs-id1167835364524",
    "fs-id1168754384001",
    "fs-id1167835418145",
    "fs-id1167832076598",
    "fs-id1167835186730",
    "fs-id1167831954237",
    "fs-id1167835530462",
    "fs-id1167831191430",
    "fs-id1167827987930",
    "fs-id1167834063977",
    "fs-id1167831880100",
    "fs-id1167835370836",
    "fs-id1167835343554",
    "fs-id1167835421108",
    "fs-id1167832057993",
    "fs-id1167835170706",
    "fs-id1167832096973",
    "fs-id1167834191318",
    "fs-id1167832151520",
    "fs-id1167831910867",
    "fs-id1167832060470",
]

EXERCISES = [
    ("fs-id1167828420938", "fs-id1167832057850", "fs-id1167832041475"),
    ("fs-id1167835367659", "fs-id1167826864846", "fs-id1167826799434"),
    ("fs-id1167834289447", "fs-id1167835368946", "fs-id1167835350532"),
    ("fs-id1167834185475", "fs-id1167830706036", "fs-id1167832042531"),
    ("fs-id1167835639953", "fs-id1167835332201", "fs-id1167832153624"),
    ("fs-id1167832056565", "fs-id1167834301215", "fs-id1167832058926"),
    ("fs-id1167835609626", "fs-id1167834222410", "fs-id1167827943084"),
    ("fs-id1167835354645", "fs-id1167830702759", "fs-id1167835262981"),
    ("fs-id1167834448636", "fs-id1167835350341", "fs-id1167835423011"),
    ("fs-id1167835333601", "fs-id1167834431373", "fs-id1167835307320"),
    ("fs-id1167835420544", "fs-id1167835288349", "fs-id1167832043521"),
    ("fs-id1167834516134", "fs-id1167831887685", "fs-id1167826782418"),
    ("fs-id1167834156729", "fs-id1167834184039", "fs-id1167831882192"),
    ("fs-id1167832151097", "fs-id1167832151099", "fs-id1167832076368"),
    ("fs-id1167835356197", "fs-id1167835356199", "fs-id1167834059399"),
]

IMAGE_REFS = [
    ("fs-id1167834188679", "CNX_IntAlg_Figure_04_01_003_img_new.jpg"),
    ("fs-id1167831893528", "CNX_IntAlg_Figure_04_01_004a_img_new.jpg"),
    ("fs-id1167835174193", "CNX_IntAlg_Figure_04_01_004b_img_new.jpg"),
    ("fs-id1167835321614", "CNX_IntAlg_Figure_04_01_004c_img_new.jpg"),
    ("fs-id1167832138637", "CNX_IntAlg_Figure_04_01_004d_img_new.jpg"),
    ("fs-id1167834161795", "CNX_IntAlg_Figure_04_01_005b_img.jpg"),
    ("fs-id1167826804609", "CNX_IntAlg_Figure_04_01_005c_img.jpg"),
    ("fs-id1167835327264", "CNX_IntAlg_Figure_04_01_005d_img.jpg"),
    ("fs-id1167834224888", "CNX_IntAlg_Figure_04_01_005e_img.jpg"),
    ("fs-id1167835510205", "CNX_IntAlg_Figure_04_01_005f_img.jpg"),
    ("fs-id1167835422879", "CNX_IntAlg_Figure_04_01_005g_img.jpg"),
    ("fs-id1167835369250", "CNX_IntAlg_Figure_04_01_005a_img.jpg"),
    ("fs-id1167835340829", "CNX_IntAlg_Figure_04_01_006a_img.jpg"),
    ("fs-id1167834195984", "CNX_IntAlg_Figure_04_01_006b_img.jpg"),
    ("fs-id1167835365745", "CNX_IntAlg_Figure_04_01_006c_img.jpg"),
    ("fs-id1167834309752", "CNX_IntAlg_Figure_04_01_006d_img.jpg"),
    ("fs-id1167835595311", "CNX_IntAlg_Figure_04_01_006e_img.jpg"),
    ("fs-id1167834191115", "CNX_IntAlg_Figure_04_01_007a_img.jpg"),
    ("fs-id1167835334409", "CNX_IntAlg_Figure_04_01_007b_img.jpg"),
    ("fs-id1167831891526", "CNX_IntAlg_Figure_04_01_007c_img.jpg"),
    ("fs-id1167835240354", "CNX_IntAlg_Figure_04_01_007d_img.jpg"),
    ("fs-id1167835258752", "CNX_IntAlg_Figure_04_01_007e_img.jpg"),
    ("fs-id1167835170706", "CNX_IntAlg_Figure_04_01_008_img_new.jpg"),
]

TABLES = {
    "fs-id1167826993913": (9, 18),
    "fs-id1167834537193": (6, 12),
    "fs-id1167835327859": (6, 12),
    "fs-id1167832096973": (4, 16),
    "fs-idm341212944": (4, 8),
    "fs-idm341515088": (4, 8),
}

REQUIRED_TERMS = [
    "रेषीय समीकरणांची प्रणाली",
    "आलेख",
    "क्रमित जोडी",
    "उकल",
    "उतार",
    "y-अक्षावरील छेद",
    "छेदणाऱ्या रेषा",
    "समांतर रेषा",
    "संपाती रेषा",
    "सुसंगत समीकरण-प्रणाली",
    "असुसंगत समीकरण-प्रणाली",
    "स्वतंत्र",
    "अवलंबी",
]

EXPECTED_MATH = {
    "src-m01": "{ 2x + y = 7; x − 2y = 6 }",
    "img-004a-form": "2x + y = 7 ⇒ y = −2x + 7",
    "img-004a-values": "m = −2, b = 7",
    "img-004b-equation": "x − 2y = 6",
    "img-004b-intercepts": "(0, −3), (6, 0)",
    "img-004d-point": "(4, −1)",
    "img-004d-check1": "2(4) + (−1) = 7",
    "img-004d-check2": "4 − 2(−1) = 6",
    "img-004d-answer": "(4, −1)",
    "src-m02": "{ x − 3y = −3; x + y = 5 }",
    "src-m03": "(3, 2)",
    "src-m04": "{ −x + y = 1; 3x + 2y = 12 }",
    "src-m05": "(2, 3)",
    "src-m06": "{ 3x + y = −1; 2x + y = 0 }",
    "src-m07": "y",
    "img-005b-system": "{ 3x + y = −1; 2x + y = 0 }",
    "img-005c-form": "3x + y = −1 ⇒ y = −3x − 1",
    "img-005d-values": "m = −3, b = −1",
    "img-005e-form": "2x + y = 0 ⇒ y = −2x",
    "img-005f-values": "m = −2, b = 0",
    "img-005g-point": "(−1, 2)",
    "src-m08": "(−1, 2)",
    "img-005a-checks": "3(−1) + 2 = −1; 2(−1) + 2 = 0",
    "src-m09": "(−1, 2)",
    "src-m10": "{ −x + y = 1; 2x + y = 10 }",
    "src-m11": "(3, 4)",
    "src-m12": "{ 2x + y = 6; x + y = 1 }",
    "src-m13": "(5, −4)",
    "src-m14": "{ y = (1/2)x − 3; x − 2y = 4 }",
    "img-006a-system": "{ y = (1/2)x − 3; x − 2y = 4 }",
    "img-006b-values": "y = (1/2)x − 3; m = 1/2; b = −3",
    "img-006c-equation": "x − 2y = 4",
    "img-006d-intercepts": "(0, −2), (4, 0)",
    "img-006e-blue": "y = (1/2)x − 2",
    "img-006e-red": "y = (1/2)x − 3",
    "src-m15": "{ y = −(1/4)x + 2; x + 4y = −8 }",
    "src-m16": "{ y = 3x − 1; 6x − 2y = 6 }",
    "src-m17": "{ y = 2x − 3; −6x + 3y = −9 }",
    "img-007a-system": "{ y = 2x − 3; −6x + 3y = −9 }",
    "img-007b-values": "y = 2x − 3; m = 2; b = −3",
    "img-007c-equation": "−6x + 3y = −9",
    "img-007d-intercepts": "(0, −3), (3/2, 0)",
    "img-007e-line": "y = 2x − 3",
    "src-m18": "{ y = −3x − 6; 6x + 2y = −12 }",
    "src-m19": "{ y = (1/2)x − 4; 2x − 4y = 16 }",
    "src-m20": "{ y = 3x − 1; 6x − 2y = 12 }",
    "src-m21": "{ 2x + y = −3; x − 5y = 5 }",
    "src-m22": "{ y = 3x − 1; 6x − 2y = 12 }; y = 3x − 1",
    "src-m23": "6x − 2y = 12; −2y = −6x + 12; (−2y)/(−2) = (−6x + 12)/(−2); y = 3x − 6",
    "src-m24": "y = 3x − 1: m = 3, b = −1; y = 3x − 6: m = 3, b = −6",
    "src-m25": "{ 2x + y = −3; x − 5y = 5 }",
    "src-m26": "2x + y = −3 ⇒ y = −2x − 3; x − 5y = 5 ⇒ −5y = −x + 5 ⇒ (−5y)/(−5) = (−x + 5)/(−5) ⇒ y = (1/5)x − 1",
    "src-m27": "y = −2x − 3: m = −2, b = −3; y = (1/5)x − 1: m = 1/5, b = −1",
    "src-m28": "{ y = −2x − 4; 4x + 2y = 9 }",
    "src-m29": "{ 3x + 2y = 2; 2x + y = 1 }",
    "src-m30": "{ y = (1/3)x − 5; x − 3y = 6 }",
    "src-m31": "{ x + 4y = 12; −x + y = 3 }",
    "src-m32": "−10",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def inside(base: Path, relative: str) -> Path:
    candidate = (base / relative).resolve()
    root = base.resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("path escape")
    return candidate


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def node_text(node: E.Element) -> str:
    return re.sub(r"\s+", " ", "".join(node.itertext())).strip()


def ids(root: E.Element) -> dict[str, E.Element]:
    return {node.get("id"): node for node in root.iter() if node.get("id")}


def nearest_id_parents(root: E.Element, allowed: set[str]) -> dict[str, str | None]:
    parent = {child: node for node in root.iter() for child in node}
    answer = {}
    for node in root.iter():
        ident = node.get("id")
        if ident not in allowed:
            continue
        ancestor = parent.get(node)
        while ancestor is not None and ancestor.get("id") not in allowed:
            ancestor = parent.get(ancestor)
        answer[ident] = None if ancestor is None else ancestor.get("id")
    return answer


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
        return node.get("open", "(") + node.get("separators", ",").join(
            mathml(child) for child in node
        ) + node.get("close", ")")
    if name == "mtr":
        return "".join(mathml(child) for child in node)
    if name == "mtable":
        rows = [mathml(child) for child in node]
        return ";".join(row for row in rows if row)
    raise ValueError("unsupported MathML " + name)


def semantic_math(value: str) -> str:
    value = re.sub(r"\s+", "", value).replace("−", "-").replace("⇒", "=")
    value = value.replace("{", "").replace("}", "")
    value = re.sub(r"\((-?\d+/-?\d+)\)", r"\1", value)
    return value.rstrip(".,;?")


def element_bytes_without_tail(node) -> bytes:
    """Serialize one element without unrelated following prose in its XML tail."""
    clone = deepcopy(node)
    clone.tail = None
    return E.tostring(clone, encoding="utf-8")


def canonical_bytes_without_tail(node) -> bytes:
    return E.canonicalize(element_bytes_without_tail(node)).encode("utf-8")


def jpeg_size(data: bytes) -> tuple[int, int]:
    if not data.startswith(b"\xff\xd8\xff"):
        raise ValueError("not JPEG")
    index = 2
    sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    while index < len(data):
        if data[index] != 0xFF:
            index += 1
            continue
        while index < len(data) and data[index] == 0xFF:
            index += 1
        if index >= len(data):
            break
        marker = data[index]
        index += 1
        if marker in {0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
            continue
        if index + 2 > len(data):
            break
        length = int.from_bytes(data[index:index + 2], "big")
        if length < 2 or index + length > len(data):
            raise ValueError("bad JPEG segment")
        if marker in sof:
            height = int.from_bytes(data[index + 3:index + 5], "big")
            width = int.from_bytes(data[index + 5:index + 7], "big")
            return width, height
        index += length
    raise ValueError("JPEG dimensions missing")


def solve(a1, b1, c1, a2, b2, c2):
    values = [Fraction(value) for value in (a1, b1, c1, a2, b2, c2)]
    a1, b1, c1, a2, b2, c2 = values
    determinant = a1 * b2 - a2 * b1
    if determinant:
        return "one", ((c1 * b2 - c2 * b1) / determinant, (a1 * c2 - a2 * c1) / determinant)
    if a1 * c2 == a2 * c1 and b1 * c2 == b2 * c1:
        return "infinite", None
    return "none", None


SYSTEM_CASES = [
    ("01", (2, 1, 7, 1, -2, 6), ("one", (Fraction(4), Fraction(-1)))),
    ("02", (1, -3, -3, 1, 1, 5), ("one", (Fraction(3), Fraction(2)))),
    ("03", (-1, 1, 1, 3, 2, 12), ("one", (Fraction(2), Fraction(3)))),
    ("04", (3, 1, -1, 2, 1, 0), ("one", (Fraction(-1), Fraction(2)))),
    ("05", (-1, 1, 1, 2, 1, 10), ("one", (Fraction(3), Fraction(4)))),
    ("06", (2, 1, 6, 1, 1, 1), ("one", (Fraction(5), Fraction(-4)))),
    ("07", (1, -2, 6, 1, -2, 4), ("none", None)),
    ("08", (1, 4, 8, 1, 4, -8), ("none", None)),
    ("09", (3, -1, 1, 6, -2, 6), ("none", None)),
    ("10", (2, -1, 3, -6, 3, -9), ("infinite", None)),
    ("11", (3, 1, -6, 6, 2, -12), ("infinite", None)),
    ("12", (1, -2, 8, 2, -4, 16), ("infinite", None)),
    ("13a", (3, -1, 1, 6, -2, 12), ("none", None)),
    ("13b", (2, 1, -3, 1, -5, 5), ("one", (Fraction(-10, 11), Fraction(-13, 11)))),
    ("14a", (2, 1, -4, 4, 2, 9), ("none", None)),
    ("14b", (3, 2, 2, 2, 1, 1), ("one", (Fraction(0), Fraction(1)))),
    ("15a", (1, -3, 15, 1, -3, 6), ("none", None)),
    ("15b", (1, 4, 12, -1, 1, 3), ("one", (Fraction(0), Fraction(3)))),
]


class HTMLFacts(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.hrefs = []
        self.sources = []
        self.images = []
        self.tags = []

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


class Unit25IndependentReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (BASE / f"translations/{UNIT}.xml").read_bytes()
        cls.root = E.fromstring(cls.raw)
        cls.target = ids(cls.root)
        cls.config = json.loads(
            (BASE / f"units/{UNIT}.json").read_text(encoding="utf-8"), object_pairs_hook=unique
        )
        cls.lock = json.loads(
            (BASE / f"provenance/{UNIT}.lock.json").read_text(encoding="utf-8"), object_pairs_hook=unique
        )
        cls.receipt = json.loads(
            (BASE / f"qa/{UNIT}-build-receipt.json").read_text(encoding="utf-8"), object_pairs_hook=unique
        )
        cls.check_nodes = [node for node in cls.root.iter() if node.get("data-check")]
        cls.checks = {node.get("data-check"): node_text(node) for node in cls.check_nodes}
        cls.source_roots = {}
        cls.source = {}
        cls.archive_images = {}
        for locale, (archive_name, prefix, _, _) in ARCHIVES.items():
            archive = WORKSPACE / "downloads/mr-Deva-IN/releases" / archive_name
            with zipfile.ZipFile(archive) as zf:
                module = zf.read(f"{prefix}/modules/m81427/index.cnxml")
                for _, name in IMAGE_REFS:
                    cls.archive_images[(locale, name)] = zf.read(f"{prefix}/media/{name}")
            root = E.fromstring(module)
            cls.source_roots[locale] = root
            cls.source[locale] = ids(root)
        cls.html_raw = (BASE / f"output/{UNIT}.html").read_bytes()
        cls.html = HTMLFacts()
        cls.html.feed(cls.html_raw.decode("utf-8"))

    def test_01_exact_release_pins(self):
        for relative, expected in PINS.items():
            data = (BASE / relative).read_bytes()
            self.assertEqual((len(data), sha(data)), expected, relative)

    def test_02_pinned_archives_modules_and_metadata(self):
        titles = {
            "en": "Solve Systems of Linear Equations with Two Variables",
            "id": "Menyelesaikan Sistem Persamaan Linear dengan Dua Variabel",
        }
        for locale, (archive_name, _, archive_bytes, archive_sha) in ARCHIVES.items():
            archive = WORKSPACE / "downloads/mr-Deva-IN/releases" / archive_name
            data = archive.read_bytes()
            self.assertEqual((len(data), sha(data)), (archive_bytes, archive_sha))
            root = self.source_roots[locale]
            self.assertEqual(root.tag, C + "document")
            metadata = root.find(C + "metadata")
            self.assertEqual(root.findtext(C + "title"), titles[locale])
            self.assertEqual(metadata.findtext(MD + "content-id"), "m81427")
            self.assertEqual(metadata.findtext(MD + "uuid"), "b9f8475e-9490-4f24-995f-2923b1ed9644")
            self.assertEqual(metadata.findtext(MD + "title"), titles[locale])
            module = E.tostring(root, encoding="utf-8", xml_declaration=True)
            # ElementTree may normalize the declaration; the archive member pin remains authoritative.
            self.assertEqual(len(self.source[locale]), len(set(self.source[locale])))
            self.assertGreater(len(module), 160000)

    def test_03_exact_wrapper_children_titles_and_next_boundary(self):
        titles = {
            "en": "Solve a System of Linear Equations by Graphing",
            "id": "Menyelesaikan Sistem Persamaan Linear dengan Menggambar Grafik",
        }
        next_titles = {
            "en": "Solve a System of Equations by Substitution",
            "id": "Menyelesaikan Sistem Persamaan dengan Substitusi",
        }
        for locale in ("en", "id"):
            wrapper = self.source[locale][WRAPPER]
            self.assertEqual(wrapper.findtext(C + "title"), titles[locale])
            children = [node for node in wrapper if node.tag != C + "title"]
            self.assertEqual([node.get("id") for node in children], SELECTORS)
            parent = next(node for node in self.source_roots[locale].iter() if wrapper in list(node))
            siblings = list(parent)
            following = siblings[siblings.index(wrapper) + 1]
            self.assertEqual(following.get("id"), NEXT)
            self.assertEqual(following.findtext(C + "title"), next_titles[locale])

    def test_04_bilingual_wrapper_shape_1191_tags_and_154_ids(self):
        shapes = {}
        id_pairs = {}
        for locale in ("en", "id"):
            wrapper = self.source[locale][WRAPPER]
            shapes[locale] = [(local(node.tag), node.get("id")) for node in wrapper.iter()]
            id_pairs[locale] = [item for item in shapes[locale] if item[1]]
            self.assertEqual(len(shapes[locale]), 1191)
            self.assertEqual(len(id_pairs[locale]), 154)
            self.assertEqual(len({ident for _, ident in id_pairs[locale]}), 154)
        self.assertEqual(shapes["en"], shapes["id"])
        self.assertEqual(id_pairs["en"], id_pairs["id"])
        allowed = {ident for _, ident in id_pairs["en"]}
        self.assertEqual(
            nearest_id_parents(self.source["en"][WRAPPER], allowed),
            nearest_id_parents(self.source["id"][WRAPPER], allowed),
        )

    def test_05_lock_and_target_have_exact_39_locator_order(self):
        expected = ["A20:m81427#" + ident for ident in SELECTORS]
        self.assertEqual([entry["locator"] for entry in self.lock["source_selections"]], expected)
        self.assertEqual([entry["target_id"] for entry in self.lock["source_selections"]], SELECTORS)
        self.assertEqual([node.get("data-source") for node in self.root.iter() if node.get("data-source")], expected)
        self.assertIsNone(self.target[WRAPPER].get("data-source"))
        self.assertEqual(self.target[WRAPPER].get("data-kind"), "translation")

    def test_06_fragments_math_hashes_and_zero_source_urls(self):
        for selection in self.lock["source_selections"]:
            self.assertEqual(len(selection["sources"]), 2)
            for record in selection["sources"]:
                locale = record["locale"]
                fragment = inside(BASE, record["fragment_path"]).read_bytes()
                source = self.source[locale][selection["target_id"]]
                self.assertEqual((len(fragment), sha(fragment)), (
                    next(item["bytes"] for item in self.lock["witnesses"] if item["path"] == record["fragment_path"]),
                    record["fragment_sha256"],
                ))
                self.assertEqual(element_bytes_without_tail(E.fromstring(fragment)), element_bytes_without_tail(source))
                self.assertEqual(record["module_sha256"], MODULE_PINS[locale][1])
                self.assertEqual(record["archive_sha256"], ARCHIVES[locale][3])
                self.assertEqual(
                    record["math_sha256"],
                    [sha(E.tostring(math, encoding="utf-8")) for math in source.iter(M + "math")],
                )
                self.assertEqual(record["outgoing_urls"], [])

    def test_07_all_110_lock_witnesses_are_exact_and_confined(self):
        witnesses = self.lock["witnesses"]
        self.assertEqual(len(witnesses), 110)
        self.assertEqual(len({entry["path"] for entry in witnesses}), 110)
        for entry in witnesses:
            data = inside(BASE, entry["path"]).read_bytes()
            self.assertEqual((len(data), sha(data)), (entry["bytes"], entry["sha256"]), entry["path"])

    def test_08_target_preserves_all_154_ids_order_and_nearest_ancestry(self):
        wrapper = self.source["en"][WRAPPER]
        order = [node.get("id") for node in wrapper.iter() if node.get("id")]
        allowed = set(order)
        target_order = [node.get("id") for node in self.root.iter() if node.get("id") in allowed]
        self.assertEqual(target_order, order)
        self.assertEqual(set(self.target) - allowed, {UNIT, "credits"})
        self.assertEqual(len(self.target), 156)
        self.assertEqual(nearest_id_parents(self.root, allowed), nearest_id_parents(wrapper, allowed))

    def test_09_exact_15_exercise_problem_solution_pairs_and_anchors(self):
        for locale in ("en", "id"):
            actual = []
            for ident in SELECTORS:
                for exercise in self.source[locale][ident].iter(C + "exercise"):
                    problem = exercise.find(C + "problem")
                    solution = exercise.find(C + "solution")
                    actual.append((exercise.get("id"), problem.get("id"), solution.get("id")))
            self.assertEqual(actual, EXERCISES)
        for exercise_id, problem_id, solution_id in EXERCISES:
            self.assertIn(self.target[problem_id], list(self.target[exercise_id].iter()))
            self.assertIn(self.target[solution_id], list(self.target[exercise_id].iter()))
            self.assertEqual(self.target[problem_id].get("class"), "problem")
            self.assertEqual(self.target[solution_id].get("class"), "solution")
            self.assertEqual(len(self.target[problem_id].findall(f".//a[@href='#{solution_id}']")), 1)
            self.assertEqual(len(self.target[solution_id].findall(f".//a[@href='#{problem_id}']")), 1)

    def test_10_config_census_and_source_types(self):
        expected = {
            "source_count": 39,
            "translated_worked_examples": 5,
            "translated_definitions": 3,
            "translated_practice_items": 10,
            "translated_resource_notes": 0,
            "original_practice_items": 0,
        }
        for key, value in expected.items():
            self.assertEqual(self.config[key], value)
        self.assertEqual(self.config["question_ids"], [])
        wrapper = self.source["en"][WRAPPER]
        self.assertEqual(sum(local(node.tag) == "example" for node in list(wrapper)), 5)
        self.assertEqual(sum(local(node.tag) == "note" and node.get("class") == "try" for node in list(wrapper)), 10)
        self.assertEqual(len(list(wrapper.iter(C + "term"))), 3)

    def test_11_exact_32_source_mathml_nodes_are_bilingual_identical(self):
        math_by_locale = {}
        bytes_by_locale = {}
        for locale in ("en", "id"):
            nodes = list(self.source[locale][WRAPPER].iter(M + "math"))
            self.assertEqual(len(nodes), 32)
            math_by_locale[locale] = [mathml(node) for node in nodes]
            bytes_by_locale[locale] = b"".join(canonical_bytes_without_tail(node) for node in nodes)
        self.assertEqual(math_by_locale["en"], math_by_locale["id"])
        self.assertEqual(bytes_by_locale["en"], bytes_by_locale["id"])
        self.assertEqual((len(bytes_by_locale["en"]), sha(bytes_by_locale["en"])), (
            19562, "3be6e9e04d6225dea6a712fcaa22c4f21b9c8bc612639808e3b3cf920168c12a"
        ))

    def test_12_all_58_target_config_values_are_independently_pinned(self):
        self.assertEqual(len(self.check_nodes), 58)
        self.assertEqual(len(self.checks), 58)
        self.assertEqual(self.config["expected_math"], EXPECTED_MATH)
        self.assertEqual(self.checks, EXPECTED_MATH)

    def test_13_source_math_maps_in_order_to_src_m01_through_src_m32(self):
        source_math = [mathml(node) for node in self.source["en"][WRAPPER].iter(M + "math")]
        target_math = [EXPECTED_MATH[f"src-m{index:02d}"] for index in range(1, 33)]
        source_semantic = [semantic_math(value) for value in source_math]
        target_semantic = [semantic_math(value) for value in target_math]
        self.assertEqual(source_semantic[:22], target_semantic[:22])
        self.assertEqual(source_semantic[27:], target_semantic[27:])
        complex_markers = [
            ["6x-2y=12", "-2y=-6x+12", "y=3x-6"],
            ["y=3x-1", "y=3x-6", "m=3", "b=-1", "b=-6"],
            ["2x+y=-3", "x-5y=5"],
            ["y=-2x-3", "y=(1/5)x-1"],
            ["m=-2", "m=1/5", "b=-3", "b=-1"],
        ]
        for source_value, target_value, markers in zip(
            source_semantic[22:27], target_semantic[22:27], complex_markers
        ):
            for marker in markers:
                normalized_marker = semantic_math(marker)
                self.assertIn(normalized_marker, source_value)
                self.assertIn(normalized_marker, target_value)

    def test_14_recompute_point_answers_01_through_06(self):
        for label, coefficients, expected in SYSTEM_CASES[:6]:
            self.assertEqual(solve(*coefficients), expected, label)
        for key in ["img-004d-check1", "img-004d-check2", "img-005a-checks"]:
            self.assertIn("=", EXPECTED_MATH[key])

    def test_15_recompute_parallel_and_coincident_answers_07_through_12(self):
        for label, coefficients, expected in SYSTEM_CASES[6:12]:
            self.assertEqual(solve(*coefficients), expected, label)
        self.assertEqual([case[2][0] for case in SYSTEM_CASES[6:12]], [
            "none", "none", "none", "infinite", "infinite", "infinite"
        ])

    def test_16_recompute_all_multisystem_classifications_13_through_15(self):
        for label, coefficients, expected in SYSTEM_CASES[12:]:
            self.assertEqual(solve(*coefficients), expected, label)
        self.assertEqual(solve(*SYSTEM_CASES[13][1])[1], (Fraction(-10, 11), Fraction(-13, 11)))
        self.assertEqual(solve(*SYSTEM_CASES[15][1])[1], (Fraction(0), Fraction(1)))
        self.assertEqual(solve(*SYSTEM_CASES[17][1])[1], (Fraction(0), Fraction(3)))

    def test_17_all_supplied_target_answers_match_recomputation(self):
        markers = [
            "(4, −1)", "(3, 2)", "(2, 3)", "(−1, 2)", "(3, 4)", "(5, −4)",
            "उकल नाही", "उकल नाही", "उकल नाही", "अनंत उकली", "अनंत उकली", "अनंत उकली",
        ]
        for (_, _, solution_id), marker in zip(EXERCISES[:12], markers):
            self.assertIn(marker, node_text(self.target[solution_id]))
        for solution_id in ["fs-id1167831882192", "fs-id1167832076368", "fs-id1167834059399"]:
            answer = node_text(self.target[solution_id])
            self.assertRegex(answer, r"उकल (?:नाही|नसते)")
            for marker in ["असुसंगत", "स्वतंत्र", "एक उकल", "सुसंगत"]:
                self.assertIn(marker, answer)

    def test_18_source_supplied_answer_evidence_is_identical_in_meaning(self):
        exact_plain = {
            "en": {
                "fs-id1167835262981": "no solution",
                "fs-id1167835423011": "no solution",
                "fs-id1167832043521": "infinitely many solutions",
                "fs-id1167826782418": "infinitely many solutions",
            },
            "id": {
                "fs-id1167835262981": "tidak ada solusi",
                "fs-id1167835423011": "tidak ada solusi",
                "fs-id1167832043521": "tak hingga banyak solusi",
                "fs-id1167826782418": "tak hingga banyak solusi",
            },
        }
        for locale in ("en", "id"):
            for ident, expected in exact_plain[locale].items():
                self.assertEqual(node_text(self.source[locale][ident]), expected)
            for ident in ["fs-id1167832076370", "fs-id1167834059401"]:
                text = node_text(self.source[locale][ident]).lower()
                self.assertIn("inconsistent" if locale == "en" else "tidak konsisten", text)
                self.assertIn("independent" if locale == "en" else "independen", text)

    def test_19_all_six_tables_have_exact_row_entry_counts(self):
        for locale in ("en", "id"):
            for ident, expected in TABLES.items():
                table = self.source[locale][ident]
                self.assertEqual((len(list(table.iter(C + "row"))), len(list(table.iter(C + "entry")))), expected)
        for ident, expected in TABLES.items():
            table = self.target[ident]
            self.assertEqual((len(list(table.iter("tr"))), len(list(table.iter("td"))) + len(list(table.iter("th")))), expected)

    def test_20_howto_examples_try_its_and_definitions_are_complete(self):
        source = self.source["en"]["fs-id1167835310198"]
        main = source.find(C + "list")
        nested = main.find(f"{C}item/{C}list")
        self.assertEqual(len(main.findall(C + "item")), 5)
        self.assertEqual(len(nested.findall(C + "item")), 3)
        target = self.target["fs-id1167835310198"]
        main_target = target.find("ol")
        self.assertEqual(len(main_target.findall("li")), 5)
        self.assertEqual(len(main_target.findall("li/ul/li")), 3)
        self.assertEqual([node.get("id") for node in self.root.iter("dfn")], [
            "term-00003", "term-00004", "term-00005"
        ])

    def test_21_exact_ordered_23_media_references(self):
        for locale in ("en", "id"):
            actual = []
            for media in self.source[locale][WRAPPER].iter(C + "media"):
                image = media.find(C + "image")
                actual.append((media.get("id"), Path(image.get("src")).name))
            self.assertEqual(actual, IMAGE_REFS)
        target = [(node.get("id"), node.find("img").get("src").removeprefix("asset:"))
                  for node in self.root.iter() if node.get("id") in {ident for ident, _ in IMAGE_REFS}
                  and node.find("img") is not None]
        self.assertEqual(target, IMAGE_REFS)
        self.assertEqual(set(self.config["assets"]), {name for _, name in IMAGE_REFS})

    def test_22_all_46_source_image_records_review_copies_and_assets_are_exact(self):
        records = self.lock["source_images"]
        self.assertEqual(len(records), 46)
        self.assertEqual(len({(item["locale"], Path(item["member"]).name) for item in records}), 46)
        by_key = {(item["locale"], Path(item["member"]).name): item for item in records}
        for locale in ("en", "id"):
            for _, name in IMAGE_REFS:
                record = by_key[(locale, name)]
                data = self.archive_images[(locale, name)]
                self.assertEqual((len(data), sha(data)), (record["bytes"], record["sha256"]))
                self.assertEqual(inside(WORKSPACE, record["review_copy"]).read_bytes(), data)
                if locale == "en":
                    self.assertEqual(inside(BASE, record["committed_asset"]).read_bytes(), data)
                    self.assertEqual(self.config["assets"][name], {
                        "path": f"assets/{UNIT}/{name}", "sha256": sha(data), "mime": "image/jpeg"
                    })
                else:
                    self.assertNotIn("committed_asset", record)

    def test_23_all_en_id_images_are_distinct_redraws_and_exact_aggregates(self):
        totals = {}
        for locale in ("en", "id"):
            ordered = [self.archive_images[(locale, name)] for _, name in IMAGE_REFS]
            totals[locale] = (sum(map(len, ordered)), sha(b"".join(ordered)))
        self.assertEqual(totals["en"], (1035840, "8e632558cd50df91bbe6f6cfb71114078de5a3d3e13b9aa1773c3aae45259d5f"))
        self.assertEqual(totals["id"], (2119298, "fa9eb1e2e8ed58bda192436f934dff180ed58ded32dc1075918824e60965fd79"))
        for _, name in IMAGE_REFS:
            en = self.archive_images[("en", name)]
            ind = self.archive_images[("id", name)]
            self.assertNotEqual(en, ind, name)
            self.assertNotEqual(jpeg_size(en), jpeg_size(ind), name)

    def test_24_006e_alt_error_is_corrected_to_pixel_equation_values(self):
        en_alt = self.source["en"]["fs-id1167835595311"].get("alt")
        id_alt = self.source["id"]["fs-id1167835595311"].get("alt")
        self.assertIn("blue line has a y-intercept of -2", en_alt)
        self.assertIn("red line has a y-intercept of -4", en_alt)
        self.assertIn("biru mempunyai titik potong sumbu y sebesar negatif 2", id_alt)
        self.assertIn("merah mempunyai titik potong sumbu y sebesar negatif 3", id_alt)
        target = self.target["fs-id1167835595311"]
        alt = target.find("img").get("alt")
        self.assertIn("निळ्या रेषेचा y-अक्षावरील छेद −2", alt)
        self.assertIn("लाल रेषेचा −3", alt)
        self.assertNotIn("−4", alt)
        disclosure = " ".join(node_text(node) for node in self.root.findall(".//*[@data-kind='original']"))
        for marker in ["कॅननिकल EN पर्यायी वर्णनात", "चुकून −4", "प्रत्यक्ष EN pixels", "लाल छेद −3"]:
            self.assertIn(marker, disclosure)

    def test_25_id_duplicate_y_and_five_missing_spaces_are_disclosed(self):
        defects = [
            ("fs-id1167835418145", "dari"),
            ("fs-id1167835418145", "yang"),
            ("fs-id1167831954237", "yang"),
            ("fs-id1167835530462", "yang"),
            ("fs-id1167834191318", "berbeda"),
        ]
        for ident, word in defects:
            tails = [node.tail or "" for node in self.source["id"][ident].iter()
                     if local(node.tag) == "emphasis" and node_text(node) == "y"]
            self.assertTrue(any(tail.startswith(word) for tail in tails), (ident, word, tails))
        duplicated = node_text(self.source["id"]["fs-id1167832060470"])
        self.assertIn("x dan y dan y keduanya", duplicated)
        target_text = node_text(self.root)
        self.assertNotIn("x आणि y आणि y", target_text)
        for marker in ["x dan y dan y", "पाच ID missing-space joins"]:
            self.assertIn(marker, target_text)

    def test_26_marathi_alts_are_nonempty_and_key_pixel_transcripts_are_complete(self):
        images = list(self.root.iter("img"))
        self.assertEqual(len(images), 23)
        for image in images:
            self.assertTrue(image.get("src", "").startswith("asset:"))
            self.assertTrue(image.get("alt"))
            self.assertRegex(image.get("alt"), "[\u0900-\u097f]")
        all_alt = " ".join(image.get("alt") for image in images)
        for marker in [
            "(3, −1)", "y = −2x + 7", "(0, −3) आणि (6, 0)", "(4, −1)",
            "(−1, 2)", "(0, −2) आणि (4, 0)", "(3/2, 0)", "संपाती रेषा",
        ]:
            self.assertIn(marker, all_alt)

    def test_27_all_local_anchors_resolve_and_external_links_are_exact(self):
        hrefs = [node.get("href") for node in self.root.iter("a")]
        local_links = [href for href in hrefs if href.startswith("#")]
        external = [href for href in hrefs if not href.startswith("#")]
        self.assertEqual(len(local_links), 41)
        for href in local_links:
            self.assertIn(href[1:], self.target)
        self.assertEqual(external, [
            "https://creativecommons.org/licenses/by-nc-sa/4.0/",
            "https://vishwakosh.marathi.gov.in/24316/",
            "https://vishwakosh.marathi.gov.in/28194/",
        ])

    def test_28_marathi_canon_pins_terms_and_authored_limits_are_honest(self):
        canon = {
            "downloads/mr-Deva-IN/canon/pages/balbharati8-85.png": (255250, "284d9c7e4dc21f183189750421e65c97acfae02fd642df0457321cfe627a7f69"),
            "downloads/mr-Deva-IN/canon/ocr/balbharati8-85.txt": (2474, "f9bf9c42edb3e126573bc14f4671aa5c062920ee145c50590fdac6733af52a9b"),
            "downloads/mr-Deva-IN/canon/pages/balbharati8-86.png": (195482, "87e2c859c7d3445466e28b1050bb86bc52b1014fb6f2dd2c75d356dda620ce49"),
            "downloads/mr-Deva-IN/canon/ocr/balbharati8-86.txt": (1539, "497332d70fb096c86e468261e37186b888099b86830234a26d5c86253188ee57"),
        }
        for relative, expected in canon.items():
            data = (WORKSPACE / relative).read_bytes()
            self.assertEqual((len(data), sha(data)), expected)
        page85 = (WORKSPACE / "downloads/mr-Deva-IN/canon/ocr/balbharati8-85.txt").read_text(encoding="utf-8")
        page86 = (WORKSPACE / "downloads/mr-Deva-IN/canon/ocr/balbharati8-86.txt").read_text(encoding="utf-8")
        for phrase in ["समीकरणाची उकल", "दोन्ही बाजूंवर समान क्रिया", "शून्येतर समान संख्येने भागणे"]:
            self.assertIn(phrase, page85)
        for phrase in ["पुढील समीकरणे सोडवा", "दोन्ही बाजूंना 5 ने गुणून", "दोन्ही बाजूंना 5 ने भागून"]:
            self.assertIn(phrase, page86)
        lock = json.loads((BASE / "canon/witnesses.lock.json").read_text(encoding="utf-8"), object_pairs_hook=unique)
        web = {item["ids"][0]: item for item in lock["additional_web_readings"]}
        self.assertEqual(web["C18"]["url"], "https://vishwakosh.marathi.gov.in/24316/")
        self.assertEqual(web["C22"]["url"], "https://vishwakosh.marathi.gov.in/28194/")
        self.assertEqual(self.config["required_terms"], REQUIRED_TERMS)
        target = node_text(self.root)
        for phrase in [
            "लेखकाने तयार केलेली स्रोत-अर्थाधारित कार्यरूपे",
            "अक्षरशः प्रमाणित असल्याचा दावा नाही",
            "मानवी मराठी गणित-शिक्षकाचे पुनरावलोकन अद्याप आवश्यक",
        ]:
            self.assertIn(phrase, target)

    def test_29_scope_disclosure_and_next_boundary_exclusion(self):
        self.assertNotIn(NEXT, self.target)
        self.assertNotIn("A20:m81427#" + NEXT, [node.get("data-source") for node in self.root.iter()])
        text = node_text(self.root)
        for phrase in [
            "39 थेट non-title selectors", "154 स्रोत-IDs", "15 स्रोत-प्रश्न", "15 स्रोत-उत्तरे",
            "32 MathML nodes", "23 प्रतिमा", "सहा table elements", "fs-id1167834233994",
            "येथे समाविष्ट केलेला नाही", "संपूर्ण module", "पाचही पुस्तकांचे काम पूर्ण झाल्याचा दावा नाही",
        ]:
            self.assertIn(phrase, text)

    def test_30_build_receipt_and_structural_html_are_exact_not_visual_acceptance(self):
        receipt = self.receipt
        self.assertEqual((receipt["unit"], receipt["locale"], receipt["result"]), (UNIT, "mr-Deva-IN", "PASS"))
        self.assertEqual(receipt["source_sha256"], PINS["translations/MR-BRIDGE-025.xml"][1])
        self.assertEqual(receipt["config_sha256"], PINS["units/MR-BRIDGE-025.json"][1])
        self.assertEqual(receipt["provenance_lock_sha256"], PINS["provenance/MR-BRIDGE-025.lock.json"][1])
        self.assertEqual((receipt["html_bytes"], receipt["html_sha256"]), PINS["output/MR-BRIDGE-025.html"])
        self.assertEqual((
            receipt["selected_source_blocks"], receipt["pinned_witnesses_checked"],
            receipt["displayed_math_regressions"], receipt["local_links_checked"],
            receipt["optional_external_citation_links"], receipt["unique_ids"],
            receipt["embedded_image_count"], receipt["distinct_embedded_assets"],
        ), (39, 110, 58, 41, 3, 156, 23, 23))
        for style in receipt["stylesheet_files"]:
            self.assertEqual(sha(inside(BASE, style["path"]).read_bytes()), style["sha256"])
        self.assertIn("visual browser QA", receipt["not_claimed"])
        self.assertIn("human expert or native-speaker approval", receipt["not_claimed"])
        self.assertEqual(len(self.html.ids), len(set(self.html.ids)))
        self.assertEqual(len(self.html.ids), 156)
        self.assertEqual(self.html.sources, ["A20:m81427#" + ident for ident in SELECTORS])
        self.assertEqual(len(self.html.images), 23)
        decoded = []
        for image, (_, name) in zip(self.html.images, IMAGE_REFS):
            self.assertTrue(image["src"].startswith("data:image/jpeg;base64,"))
            decoded.append(base64.b64decode(image["src"].split(",", 1)[1], validate=True))
            self.assertEqual(decoded[-1], self.archive_images[("en", name)])
        self.assertEqual(sum(map(len, decoded)), receipt["embedded_image_raw_bytes"])
        self.assertNotIn(b"asset:", self.html_raw)
        self.assertNotIn("script", self.html.tags)

    def test_31_unicode_security_and_adversarial_helpers(self):
        decoded = self.raw.decode("utf-8")
        self.assertEqual(self.root.get("id"), UNIT)
        self.assertEqual(self.root.get("lang"), "mr-Deva-IN")
        self.assertEqual(decoded, unicodedata.normalize("NFC", decoded))
        self.assertNotIn("\ufffd", decoded)
        for tag in ["script", "iframe", "object", "embed", "svg", "audio", "video"]:
            self.assertEqual(list(self.root.iter(tag)), [])
        with self.assertRaises(ValueError):
            unique([("x", 1), ("x", 2)])
        with self.assertRaises(ValueError):
            inside(BASE, "../escape")
        with self.assertRaises(ValueError):
            jpeg_size(b"not a jpeg")
        with self.assertRaises(ValueError):
            mathml(E.fromstring(f'<math xmlns="{M[1:-1]}"><mphantom /></math>'))
        self.assertNotEqual(solve(1, 1, 2, 1, -1, 0), solve(1, 1, 2, 2, 2, 4))
        self.assertNotEqual(semantic_math("x-y=-1"), semantic_math("x-y=1"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
