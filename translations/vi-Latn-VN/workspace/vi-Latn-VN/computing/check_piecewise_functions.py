"""U022 source preservation and finite piecewise-function witnesses.

The source/draft record is module-qualified. This checker neither proves
infinite-domain claims by sampling nor builds readers or changes source images.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from math import sqrt
from pathlib import Path
import csv
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
EXCERPT_SHA = "407afaa10cb03396147e0c73ffa829ff71e49510d05575db90b62ecc6d355878"
MATH_TEXT = {"formula": "công thức", "is\u00a0in\u00a0domain": "thuộc phần tập xác định", "if": "nếu"}
ASSETS = [
    {
        "media_id": "fs-id1165137419948",
        "filename": "CNX_Precalc_Figure_01_02_021.jpg",
        "sha256": "5557c0f6b8e4fdc2ce05553651f44d3c6d8c3e5c2e79dd3b3992c2e7820f7021",
        "bytes": 78529,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:69b71653986b55fc439d2286"
    },
    {
        "media_id": "fs-id1165135453346",
        "filename": "CNX_Precalc_Figure_01_02_022-75d8.jpg",
        "sha256": "9d5778127b65ddd752d164a49a43c204e4df78ab131455d9bc0b7b626d77a6e2",
        "bytes": 76824,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:dabb6f9a797aa0bdc18837e5"
    },
    {
        "media_id": "fs-id1165137439226",
        "filename": "CNX_Precalc_Figure_01_02_023abc-8709.jpg",
        "sha256": "d6aa56befaf73b4e930bbea5d48346fc1aed934ad8f9711ab1dc2820bacce196",
        "bytes": 129811,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:7b89d7cc639ebcdb1c239de3"
    },
    {
        "media_id": "fs-id1165137646696",
        "filename": "CNX_Precalc_Figure_01_02_026-e20a.jpg",
        "sha256": "766b4d313af3c3771276b3f7612b46a68d68d83a30feb0b6cbddeedadc39bb4f",
        "bytes": 83700,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:9c226fb87342c6994f5bcf6e"
    },
    {
        "media_id": "fs-id1165134302462",
        "filename": "CNX_Precalc_Figure_01_02_027-55b5.jpg",
        "sha256": "19540d3037451b565401ef2414cdad92a95f3ccd3bcdb3a2e9c7f862451c4dfd",
        "bytes": 95837,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:31847fa79c156fae8159f3de"
    }
]
NUMBER_TOKENS = {
    "fs-id1165135194329": [
        "0"
    ],
    "fs-id1165133112779": [
        "0"
    ],
    "fs-id1165134042316": [
        "0.1",
        "10",
        "000",
        "1000",
        "0.2",
        "10",
        "000",
        "10",
        "000."
    ],
    "fs-id1165135190749": [
        "0",
        "0"
    ],
    "fs-id1165135331729": [
        "5",
        "50."
    ],
    "fs-id1165135208951": [
        "5",
        "0",
        "10",
        "50",
        "10"
    ],
    "fs-id1165135196985": [
        "0",
        "10",
        "10"
    ],
    "fs-id1165137660470": [
        "25",
        "0",
        "2",
        "25",
        "10",
        "2",
        "2"
    ],
    "fs-id1165134373545": [
        "1.5"
    ],
    "fs-id1165134300204": [
        "1.5",
        "25"
    ],
    "fs-id1165135440213": [
        "4"
    ],
    "fs-id1165135383665": [
        "4",
        "25",
        "10",
        "4",
        "2",
        "45"
    ],
    "fs-id1165137601265": [
        "2."
    ],
    "fs-id1165137475346": [
        "2",
        "1",
        "3",
        "1",
        "2",
        "2"
    ],
    "Figure_01_02_023": [
        "2",
        "1",
        "3",
        "2",
        "2"
    ],
    "fs-id1165134389893": [
        "1",
        "2",
        "1",
        "3",
        "2",
        "2",
        "1",
        "1",
        "2",
        "3"
    ],
    "fs-id1165137433350": [
        "3",
        "1",
        "2",
        "1",
        "4",
        "4"
    ]
}


def canonical(node, without_mtext=False):
    text = "" if without_mtext and node.tag == M + "mtext" else (node.text or "").strip()
    return (node.tag, tuple(sorted(node.attrib.items())), text,
            tuple((canonical(child, without_mtext), (child.tail or "").strip()) for child in node))


def tax(income):
    return income / 10 if income <= 10000 else 1000 + F(1, 5) * (income - 10000)


def museum(n):
    if n <= 0:
        return None
    return 5 * n if n < 10 else 50


def phone(g):
    if g <= 0:
        return None
    return 25 if g < 2 else 25 + 10 * (g - 2)


def example13(x):
    if x <= 1:
        return x * x
    if x <= 2:
        return 3
    return x


def try_it8(x):
    if x < -1:
        return x ** 3
    if -1 < x < 4:
        return -2
    if x > 4:
        return sqrt(x)
    return None


def tests():
    count = 0

    def check(condition, label):
        nonlocal count
        assert condition, label
        count += 1

    data = (ROOT / "sources/m49304-piecewise-functions-source.cnxml").read_bytes()
    check(sha256(data).hexdigest() == EXCERPT_SHA, "pinned full section excerpt")
    root = ET.fromstring(data)
    draft = (ROOT / "translation/A30-U022-piecewise-functions.vi.md").read_text(encoding="utf-8")
    check(draft == unicodedata.normalize("NFC", draft), "Vietnamese NFC")
    ids = [n.get("id") for n in root.iter() if n.get("id")]
    by_id = {n.get("id"): n for n in root.iter() if n.get("id")}
    anchors = re.findall(r"\{#([^}]+)\}", draft)
    check(len(ids) == len(set(ids)) == 78, "78 module-local source IDs")
    check(all(n == 1 for n in Counter(anchors).values()), "unique draft anchors")
    for identity in ids:
        check(anchors.count(identity) == 1, f"retained source ID {identity}")
    check(root.find(CN + "metadata") is None and len(root.find(CN + "content")) == 1,
          "complete section only, without repeated module metadata")
    check("fs-id1165134077347" not in ids, "Key Concepts stop excluded")
    math = list(root.iter(M + "math"))
    refs = re.findall(r"\{\{math:([^:}]+):(\d+)\}\}", draft)
    check(len(refs) == len(math) == 38, "38 source math expressions")
    captured = [list(by_id[identity].iter(M + "math"))[int(index)] for identity, index in refs]
    check(Counter(map(id, captured)) == Counter(map(id, math)), "every source expression captured exactly once")
    for identity, expected in NUMBER_TOKENS.items():
        check([n.text for n in by_id[identity].iter(M + "mn")] == expected,
              f"original numeric tokens {identity}")
    mtexts = [n.text for n in root.iter(M + "mtext")]
    check(len(mtexts) == 32, "32 mtext nodes, including currency and numeric payload")
    localized_mtext = []
    for original in mtexts:
        localized = original
        for before, after in MATH_TEXT.items():
            localized = localized.replace(before, after)
        localized_mtext.append(localized)
        check(re.findall(r"[\d<,$]+", original) == re.findall(r"[\d<,$]+", localized),
              "all mtext numerals/inequality/currency punctuation preserved")
    check("\u00a0nếu\u00a01<\u00a0" in localized_mtext, "caption(b) retains numeric lower bound1< inside mtext")
    check(all(word not in " ".join(localized_mtext) for word in ("formula", "if", "is\u00a0in\u00a0domain")),
          "English mathematical prose localized")
    check([n.get("id") for n in root.iter(CN + "example")] ==
          ["Example_01_02_11", "Example_01_02_12", "Example_01_02_13"], "complete example order")
    check([n.get("id") for n in root.iter(CN + "exercise")] ==
          ["fs-id1165137452506", "fs-id1165135436662", "fs-id1165137781618", "ti_01_02_06"],
          "three worked exercises and source Try It")
    check([n.get("id") for n in root.iter(CN + "solution")] ==
          ["fs-id1165137807421", "fs-id1165135177567", "fs-id1165135487148", "fs-id1165137784656"],
          "four source-supplied solutions")
    check(draft.count("**Lời giải nguồn.**") == 3 and draft.count("**Đáp án nguồn — đồ thị:**") == 1,
          "all source solution labels")
    check(draft.count("**Phân tích nguồn.**") == 3, "three source analysis passages")
    check("Tự thử 8" in draft and "{#ti_01_02_06}" in draft, "continuous visible numbering with original Try It ID")
    check(len(list(root.iter(CN + "figure"))) == 4 and len(list(root.iter(CN + "image"))) == 5,
          "four figures plus one bare solution media image")
    check(len(list(root.iter(CN + "table"))) == 0, "no CNXML data tables; piecewise mtables are math")
    links = re.findall(r"\]\(#([^)]+)\)", draft)
    check(len(links) == 4 and all(anchors.count(identity) == 1 for identity in links),
          "four original local figure links")
    urls = [n.get("url") for n in by_id["fs-id1165135190393"].iter(CN + "link")]
    check(len(urls) == 5 and all(draft.count("(" + url + ")") == 1 for url in urls),
          "all five optional source links retained exactly once")
    check("chưa" in draft and "được kiểm tra trong lần dịch này" in draft and
          "không được đóng gói" in draft, "external source resources not claimed fetched or packaged")
    image_refs = re.findall(r"!\[([^\]]+)\]\(([^)]+)\)", draft)
    check([path for _, path in image_refs] == ["../assets/" + a["filename"] for a in ASSETS],
          "all five exact source image references/order")
    check(all(len(alt) > 100 for alt, _ in image_refs), "substantial Vietnamese alt for each source image")
    for phrase in ("phần tập xác định", "số nguyên dương", "mô hình thuế minh họa",
                   "không phải quy định thuế hiện hành", "**$n>0$**", "**$g>0$**",
                   "hai đầu ra khác nhau", "cùng đầu ra", "không thay thế đáp án nguồn"):
        check(phrase in draft, f"source/context qualification {phrase}")
    check(r"\mathbb{R}\setminus\{-1,4\}" in draft and r"(-\infty,-1)\cup(2,\infty)" in draft,
          "supplemental Try It domain/range retains holes")
    for point in ("$(-1,-1)$", "$(-1,-2)$", "$(4,-2)$", "$(4,2)$"):
        check(point in draft, "all four source Try It open endpoints described")
    check("**Lời đáp nguồn:** Không." in draft and "**Hiệu chỉnh bổ sung:**" in draft,
          "overstrong source Q&A retained with explicit correction")
    check("có đúng một **giá trị đầu ra**" in draft, "output uniqueness context")
    check("kiểm tra hữu hạn" in draft, "finite checks not presented as universal proof")

    # Exactly52 finite mathematical witnesses.
    start_math = count
    for x in (-3, -1, 0, 1, 3):
        check((x if x >= 0 else -x) == abs(x), "absolute-value branch")
    for income, value in ((0, 0), (5000, 500), (10000, 1000), (15000, 2000)):
        check(tax(F(income)) == value, "illustrative marginal tax")
    check(F(1, 10) * 10000 == 1000 + F(1, 5) * (10000 - 10000), "tax threshold agreement")
    for n, value in ((1, 5), (9, 45), (10, 50), (25, 50)):
        check(museum(n) == value, "actual integer museum cost")
    check(museum(0) is None, "museum zero excluded")
    check(museum(F(3, 2)) == F(15, 2), "continuous extension explicitly separate")
    check(F(3, 2).denominator != 1, "fractional group size excluded in real counting model")
    check(phone(0) is None, "phone zero excluded")
    for g, value in ((F(3, 2), 25), (2, 25), (4, 45)):
        check(phone(g) == value, "phone branch/threshold/source answer")
    for x, value in ((-2, 4), (-1, 1), (0, 0), (1, 1), (F(3, 2), 3), (2, 3), (3, 3)):
        check(example13(x) == value, "example13 branch witness")
    for x, y, included in ((1, 3, False), (2, 2, False), (1, 1, True), (2, 3, True)):
        check((example13(x) == y) == included, "example13 open/closed source graph point")
    for x, value in ((-2, -8), (-1, None), (F(-1, 2), -2), (0, -2),
                     (2, -2), (4, None), (9, 3), (16, 4)):
        check(try_it8(x) == value, "TryIt8 source branch and excluded input")
    for x, y in ((-1, -1), (-1, -2), (4, -2), (4, 2)):
        check(try_it8(x) is None, f"source graph open endpoint {(x, y)}")
    for y, included in ((-8, True), (-2, True), (-1, False), (0, False), (2, False), (3, True), (4, True)):
        check((y < -1 or y > 2) == included, "supplemental range finite membership")
    check(0 == 2 * 0, "overlapping branch example agrees on entire singleton overlap")
    assert count - start_math == 52

    rights_path = ROOT.parent / "downloads/a30-edition/source-core/00_control/COMPONENT_RIGHTS.csv"
    rights = {}
    if rights_path.is_file():
        with rights_path.open(encoding="utf-8-sig", newline="") as handle:
            rights = {row["asset_path"]: row for row in csv.DictReader(handle)}
    for asset in ASSETS:
        check(by_id[asset["media_id"]].find(CN + "image").get("src") ==
              "../../media/" + asset["filename"], "exact source image path")
        copies = [p for p in (ROOT / "assets" / asset["filename"],
                             ROOT.parent / "downloads/upstream-openstax/media" / asset["filename"]) if p.is_file()]
        check(bool(copies) and all(p.stat().st_size == asset["bytes"] and
                                  sha256(p.read_bytes()).hexdigest() == asset["sha256"] for p in copies),
              "original pixels/hash")
        if rights:
            row = rights["media/" + asset["filename"]]
            check(row["rights_component_id"] == asset["rights_component_id"] and
                  row["sha256"] == asset["sha256"] and row["admission"] == "admitted",
                  "inherited admitted asset evidence")

    spec = spec_from_file_location("u022_extract", ROOT / "tools/extract_piecewise_functions.py")
    extractor = module_from_spec(spec)
    spec.loader.exec_module(extractor)
    for language, path in (
        ("en", ROOT.parent / "downloads/upstream-openstax/modules/m49304/index.cnxml"),
        ("id", ROOT.parent / "downloads/a30-edition/source-core/repo/source/modules/m49304/index.cnxml"),
    ):
        if not path.is_file():
            continue
        selected = ET.fromstring(extractor.extract(path))
        check([n.get("id") for n in selected.iter() if n.get("id")] == ids, f"all original source IDs {language}")
        check([canonical(n, True) for n in selected.iter(M + "math")] ==
              [canonical(n, True) for n in math], f"non-mtext math unchanged {language}")
        other_mtext = [n.text for n in selected.iter(M + "mtext")]
        check([re.findall(r"[\d<,$]+", t) for t in other_mtext] ==
              [re.findall(r"[\d<,$]+", t) for t in mtexts], f"mtext payload agrees {language}")
        check([n.get("src") for n in selected.iter(CN + "image")] ==
              [n.get("src") for n in root.iter(CN + "image")], f"all original image references {language}")
        if language == "en":
            check(extractor.extract(path) == data.decode("utf-8"), "reproducible exact English section")
            check(canonical(selected) == canonical(root), "all English content unchanged")
    return count


if __name__ == "__main__":
    print(f"PASS: {tests()} mixed source/structure/asset and finite piecewise assertions (52 mathematical witnesses)")
