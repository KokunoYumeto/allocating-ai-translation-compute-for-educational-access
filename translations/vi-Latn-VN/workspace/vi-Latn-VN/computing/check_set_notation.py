"""U019 source/structure/assets plus exact finite set-membership checks.

This is not a proof that two infinite sets are equal. The draft retains source
algebra/interval reasoning and labels all additional finite examples separately.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
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
EXCERPT_SHA = "ca72339615158e3e3b6235b1ea755e874a631224b3a2dde07f4408a21c707827"
MATH_TEXT = {"statement\u00a0about\u00a0": "mệnh đề về\u00a0", "or": "hoặc"}
ASSETS = [
    {
        "media_id": "fs-id1165135315543",
        "filename": "CNX_Precalc_Figure_01_02_003-832b.jpg",
        "sha256": "8fc57ac2c501abca395bdbbee8539ab566e6404b7addd06e4345a6cb057308d7",
        "bytes": 144015,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:bdbe96fa98fd545080e767e4",
        "id_image_src": "../../media/id-ID/CNX_Precalc_Figure_01_02_003-id.svg"
    },
    {
        "media_id": "fs-id1165135177575",
        "filename": "CNX_Precalc_Figure_01_02_004-13c7.jpg",
        "sha256": "39bcbb7e74412e9af4d2505025cccaa1faa9ca47573ef314f1cdb1ee035b6ff6",
        "bytes": 41708,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:5a44809d0cf3cde8fcc84af6",
        "id_image_src": "../../media/CNX_Precalc_Figure_01_02_004-13c7.jpg"
    },
    {
        "media_id": "fs-id1165137424715",
        "filename": "CNX_Precalc_Figure_01_02_005-eba2.jpg",
        "sha256": "8b09e5908e5f0956e6c5bd91392a2d9e6c92824456cdaf53c5992424783e6794",
        "bytes": 43854,
        "rights_component_id": "rights:openstax-precalculus-2e:asset:9c0dd25392979bbc02752783",
        "id_image_src": "../../media/CNX_Precalc_Figure_01_02_005-eba2.jpg"
    }
]
NUMBER_TOKENS = {
    "fs-id1165137410091": [
        "10",
        "30",
        "10",
        "30"
    ],
    "fs-id1165137911528": [
        "2",
        "3",
        "5",
        "4",
        "6",
        "2",
        "3",
        "4",
        "5",
        "6"
    ],
    "fs-id1165135311695": [
        "3",
        "3",
        "3"
    ],
    "fs-id1165137543047": [
        "4",
        "12"
    ],
    "fs-id1165137443063": [
        "4",
        "12"
    ],
    "fs-id1165137447518": [
        "1",
        "3",
        "5",
        "1",
        "3",
        "5",
        "1",
        "3",
        "5"
    ],
    "fs-id1165135188577": [
        "2",
        "1",
        "3",
        "2",
        "1",
        "3"
    ],
    "fs-id1165135528963": [
        "2",
        "1",
        "3",
        "2",
        "1",
        "3"
    ]
}


def canonical(node, without_mtext=False):
    body = (node.text or "").strip()
    if without_mtext and node.tag == M + "mtext":
        body = ""
    return (node.tag, tuple(sorted(node.attrib.items())), body,
            tuple((canonical(child, without_mtext), (child.tail or "").strip()) for child in node))


def interval_member(value, lower, upper, left_closed=False, right_closed=False):
    left = lower is None or value > lower or (left_closed and value == lower)
    right = upper is None or value < upper or (right_closed and value == upper)
    return left and right


def tests():
    count = 0

    def check(condition, label):
        nonlocal count
        assert condition, label
        count += 1

    data = (ROOT / "sources/m49304-set-notation-source.cnxml").read_bytes()
    check(sha256(data).hexdigest() == EXCERPT_SHA, "pinned complete section excerpt")
    root = ET.fromstring(data)
    draft = (ROOT / "translation/A30-U019-set-notation.vi.md").read_text(encoding="utf-8")
    check(draft == unicodedata.normalize("NFC", draft), "Vietnamese NFC")
    ids = [n.get("id") for n in root.iter() if n.get("id")]
    by_id = {n.get("id"): n for n in root.iter() if n.get("id")}
    anchors = re.findall(r"\{#([^}]+)\}", draft)
    check(len(ids) == len(set(ids)) == 36, "36 distinct module-local source IDs")
    check(all(n == 1 for n in Counter(anchors).values()), "no duplicate draft anchors")
    for identity in ids:
        check(anchors.count(identity) == 1, f"source anchor {identity}")
    check(root.find(CN + "metadata") is None and len(root.find(CN + "content")) == 1,
          "excerpt has only complete selected section; no repeated module metadata")
    check("fs-id1165137653855" not in ids, "next section excluded")
    math = list(root.iter(M + "math"))
    refs = re.findall(r"\{\{math:([^:}]+):(\d+)\}\}", draft)
    check(len(refs) == len(math) == 24, "24 source math occurrences")
    captured = [list(by_id[identity].iter(M + "math"))[int(index)] for identity, index in refs]
    check(Counter(map(id, captured)) == Counter(map(id, math)), "every MathML occurrence exactly once")
    for identity, expected in NUMBER_TOKENS.items():
        check([n.text for n in by_id[identity].iter(M + "mn")] == expected,
              f"all original numeric tokens {identity}")
    mtexts = [n.text for n in root.iter(M + "mtext")]
    check(mtexts == ["\u00a0\u00a0", "statement\u00a0about\u00a0", "or", "or", "or"],
          "five source mtext nodes, one only spacing")
    translated = []
    for original in mtexts:
        localized = original
        for before, after in MATH_TEXT.items():
            localized = localized.replace(before, after)
        translated.append(localized)
    check(translated == ["\u00a0\u00a0", "mệnh đề về\u00a0", "hoặc", "hoặc", "hoặc"],
          "only prose mtext localized; spacing retained")
    check([n.get("id") for n in root.iter(CN + "example")] == ["Example_01_02_05"],
          "one complete source worked example")
    check([n.get("id") for n in root.iter(CN + "exercise")] ==
          ["fs-id1165134342702", "ti_01_02_03"], "worked and Try It exercise IDs/order")
    check([n.get("id") for n in root.iter(CN + "solution")] ==
          ["fs-id1165135412904", "fs-id1165135209390"], "two source solutions")
    check(draft.count("**Lời giải nguồn.**") == draft.count("**Đáp án nguồn:**") == 1,
          "source answer labels")
    check("Tự thử 5" in draft and "Ví dụ 5" in draft, "visible module-continuous numbering")
    check("không thay thế lời giải và đáp án nguồn" in draft, "new reasoning separately labeled")
    tables = list(root.iter(CN + "table"))
    check(len(tables) == 1 and tables[0].get("id") == "fs-id1165137447518",
          "one original source table retained")
    check(len(list(tables[0].iter(CN + "row"))) == 3, "three complete source table rows")
    check([f"fs-id1165137447518:{i}" for i in range(3)] ==
          [identity + ":" + index for identity, index in refs if identity == "fs-id1165137447518"],
          "three row formulas retained in source order")
    check("trình bày ba hàng theo chiều dọc" in draft, "source table layout adaptation disclosed")
    expected_rows = [
        r"| $5<h\le10$ | $\{h\mid5<h\le10\}$ | $(5,10]$ |",
        r"| $5\le h<10$ | $\{h\mid5\le h<10\}$ | $[5,10)$ |",
        r"| $5<h<10$ | $\{h\mid5<h<10\}$ | $(5,10)$ |",
        r"| $h<10$ | $\{h\mid h<10\}$ | $(-\infty,10)$ |",
        r"| $h\ge10$ | $\{h\mid h\ge10\}$ | $[10,\infty)$ |",
        r"| Mọi số thực | $\mathbb{R}$ | $(-\infty,\infty)$ |",
    ]
    for row in expected_rows:
        check(row in draft, "six original image-table rows transcribed")
    check(draft.count("ⓐ") == draft.count("ⓑ") == draft.count("ⓒ") == 2,
          "all three problem and source answer labels")
    for phrase in ("không loại trừ", "phần chung", "giá trị tuyệt đối",
                   "vô cực không phải", "“and”", "ghi nhầm"):
        check(phrase in draft, f"mathematical/source qualification {phrase}")
    check(r"$-2\le x$" in draft and r"$x\le-2$" in draft, "source reversed-alt error explicitly disclosed")
    links = re.findall(r"\]\(#([^)]+)\)", draft)
    check(len(links) == 3 and all(anchors.count(identity) == 1 for identity in links),
          "three original figure crossreferences")
    check(re.findall(r"\]\((A30-[^)]+)\)", draft) ==
          ["A30-U018-domain-equations.vi.html#fs-id1165135193832"], "prior section cross-reader link")
    prior = (ROOT / "translation/A30-U018-domain-equations.vi.md").read_text(encoding="utf-8")
    check(prior.count("{#fs-id1165135193832}") == 1, "prior draft exact target anchor")
    image_refs = re.findall(r"!\[([^\]]+)\]\(([^)]+)\)", draft)
    check([p for _, p in image_refs] == ["../assets/" + a["filename"] for a in ASSETS],
          "three original images/order retained")
    check(all(len(alt) > 80 for alt, _ in image_refs), "substantial Vietnamese alt descriptions")

    # 46 finite mathematical assertions, not a general infinite-set proof.
    math_start = count
    row_cases = [
        ((5, 10, False, True), [(5, False), (7, True), (10, True)]),
        ((5, 10, True, False), [(5, True), (7, True), (10, False)]),
        ((5, 10, False, False), [(5, False), (7, True), (10, False)]),
        ((None, 10, False, False), [(9, True), (10, False), (11, False)]),
        ((10, None, True, False), [(9, False), (10, True), (11, True)]),
        ((None, None, False, False), [(-1000, True), (0, True), (1000, True)]),
    ]
    for bounds, values in row_cases:
        for value, expected in values:
            check(interval_member(F(value), *bounds) == expected, "image interval endpoint/interior membership")
    for value, expected in [(10, True), (30, False), (9, False), (20, True)]:
        check((10 <= value < 30) == interval_member(value, 10, 30, True, False) == expected,
              "intro set-builder interval")
    for value, expected in [(4, False), (12, True), (5, True), (13, False)]:
        check((4 < value <= 12) == interval_member(value, 4, 12, False, True) == expected,
              "definition interval")
    for value, expected in [(-3, True), (3, True), (0, False), (-4, True), (4, True), (-2, False)]:
        union = interval_member(value, None, -3, False, True) or interval_member(value, 3, None, True)
        check((abs(value) >= 3) == union == expected, "absolute-value union finite membership")
    for value, expected in [(1, True), (2, True), (3, True), (4, False), (5, False), (6, True)]:
        union = interval_member(value, 1, 3, True, True) or interval_member(value, 5, None)
        check(((1 <= value <= 3) or value > 5) == union == expected, "example5 endpoint/gap membership")
    for value, expected in [(-3, True), (-2, True), (F(-3, 2), False), (-1, True), (0, True), (3, False)]:
        union = interval_member(value, None, -2, False, True) or interval_member(value, -1, 3, True, False)
        check((value <= -2 or -1 <= value < 3) == union == expected, "TryIt5 endpoint/gap membership")
    check({2, 3, 5} | {4, 6} == {2, 3, 4, 5, 6}, "source finite union")
    check({2, 3, 5} | {3, 4} == {2, 3, 4, 5}, "inclusive or and no repeated elements")
    assert count - math_start == 46

    rights_path = ROOT.parent / "downloads/a30-edition/source-core/00_control/COMPONENT_RIGHTS.csv"
    rights = {}
    if rights_path.is_file():
        with rights_path.open(encoding="utf-8-sig", newline="") as handle:
            rights = {row["asset_path"]: row for row in csv.DictReader(handle)}
    for asset in ASSETS:
        check(by_id[asset["media_id"]].find(CN + "image").get("src") ==
              "../../media/" + asset["filename"], "exact original image reference")
        copies = [path for path in
                  (ROOT / "assets" / asset["filename"],
                   ROOT.parent / "downloads/upstream-openstax/media" / asset["filename"]) if path.is_file()]
        check(bool(copies) and all(path.stat().st_size == asset["bytes"] and
                                  sha256(path.read_bytes()).hexdigest() == asset["sha256"] for path in copies),
              "original pixels/hash")
        if rights:
            row = rights["media/" + asset["filename"]]
            check(row["sha256"] == asset["sha256"] and row["admission"] == "admitted" and
                  row["rights_component_id"] == asset["rights_component_id"], "inherited admission row")

    spec = spec_from_file_location("u019_extract", ROOT / "tools/extract_set_notation.py")
    extractor = module_from_spec(spec)
    spec.loader.exec_module(extractor)
    for language, path in (
        ("en", ROOT.parent / "downloads/upstream-openstax/modules/m49304/index.cnxml"),
        ("id", ROOT.parent / "downloads/a30-edition/source-core/repo/source/modules/m49304/index.cnxml"),
    ):
        if not path.is_file():
            continue
        original = ET.parse(path).getroot()
        selected = ET.fromstring(extractor.extract(path))
        check([n.get("id") for n in selected.iter() if n.get("id")] == ids, f"actual source IDs {language}")
        check([canonical(n, True) for n in selected.iter(M + "math")] ==
              [canonical(n, True) for n in math], f"all non-mtext MathML identical {language}")
        children = list(original.find(CN + "content"))
        index = next(i for i, n in enumerate(children) if n.get("id") == extractor.SECTION)
        check(children[index + 1].get("id") == extractor.STOP, f"next direct section {language}")
        if language == "en":
            check(extractor.extract(path) == data.decode("utf-8"), "reproducible exact source section")
            check(canonical(selected) == canonical(root), "complete English content unchanged")
        else:
            check([n.text for n in selected.iter(M + "mtext")] ==
                  ["\u00a0\u00a0", "pernyataan\u00a0tentang\u00a0", "atau", "atau", "atau"],
                  "all localized Indonesian mtext differences confined to prose")
            for asset in ASSETS:
                medium = selected.find(f".//{CN}media[@id='{asset['media_id']}']")
                check(medium.find(CN + "image").get("src") == asset["id_image_src"],
                      "actual Indonesian image path retained as edition evidence")
    return count


if __name__ == "__main__":
    print(f"PASS: {tests()} mixed source/structure/asset and finite set-membership assertions (46 mathematical witnesses)")
