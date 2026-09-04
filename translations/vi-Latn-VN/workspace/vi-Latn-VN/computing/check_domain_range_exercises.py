"""U026 exact source preservation and finite interval-membership checks.

Default: committed excerpt, draft and eleven unchanged assets; standard library
only. Explicit --originals also reads existing full pinned EN/ID modules and
their eleven admitted component rows. Nothing is downloaded or written.

The finite checks verify interval arithmetic, not the interpretation of pixels
or every point of an infinite graph. Exercise34's upper range remains unknown
without its explicitly stated added interpretation; this checker does not infer
a formula, an asymptote, unbounded output, or a missing source answer.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import argparse
import csv
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SECTION = "fs-id1165137580833"
PROMPT = "fs-id1165135186809"
STOP = "fs-id1165137785119"
EXCERPT_SHA = "f92a464301e3413c7a1bb7a77ae420f7f1b57bcec2c5863989eed6004a908e9e"
ORIGINALS = (
    ("en", "downloads/upstream-openstax/modules/m49304/index.cnxml",
     "0e230c4c96d46e7962dcb3afa1f1630718f7e1cdfae9e665d640690ab6ace19c"),
    ("id", "downloads/a30-edition/source-core/repo/source/modules/m49304/index.cnxml",
     "a341bb8c05830b95c865b18d64b186fc9a88a08640bbb12f030879faa90b7539"),
)
ASSETS = [
    {
        "exercise_id": "fs-id1165135168172",
        "media_id": "fs-id1165137891294",
        "filename": "CNX_Precalc_Figure_01_02_202-95dc.jpg",
        "bytes": 44663,
        "sha256": "ecfeaf56d06fb475f2e1f8a841ae4ea27ab6b3ae5cdc515201aa58e72f5d7775",
        "rights_component_id": "rights:openstax-precalculus-2e:asset:e3ddcc55f8ce1af2e25eda60"
    },
    {
        "exercise_id": "fs-id1165135160181",
        "media_id": "fs-id1165137837830",
        "filename": "CNX_Precalc_Figure_01_02_203-38f5.jpg",
        "bytes": 45965,
        "sha256": "1f50271a4ee05818d5639b23d36b0fe284a58ef3a912e73e4d7eafaf42261d8b",
        "rights_component_id": "rights:openstax-precalculus-2e:asset:6d655af89e15262753d90121"
    },
    {
        "exercise_id": "fs-id1165137723404",
        "media_id": "fs-id1165137733767",
        "filename": "CNX_Precalc_Figure_01_02_204-d2ad.jpg",
        "bytes": 55565,
        "sha256": "3fc9715095a538e78db1afc62807a25c776dbdc5894c37656a8cf1d0904a653d",
        "rights_component_id": "rights:openstax-precalculus-2e:asset:991e5ecb83f43784902d10da"
    },
    {
        "exercise_id": "fs-id1165137590678",
        "media_id": "fs-id1165137837060",
        "filename": "CNX_Precalc_Figure_01_02_205-5a91.jpg",
        "bytes": 56707,
        "sha256": "09cfe6f534c2eed5428bf12c9ba0da183726b6eb8ac45ca9401c4cebf8f8cc85",
        "rights_component_id": "rights:openstax-precalculus-2e:asset:a4eb5b62e7121e2a915828bf"
    },
    {
        "exercise_id": "fs-id1165137737326",
        "media_id": "fs-id1165134129572",
        "filename": "CNX_Precalc_Figure_01_02_206-059d.jpg",
        "bytes": 51313,
        "sha256": "35300e4be994933c8203c892cd24e0a5fbf22ddfb690d7edaafefec8e842efbf",
        "rights_component_id": "rights:openstax-precalculus-2e:asset:e5375ba6fea7a1c3f0c3dcba"
    },
    {
        "exercise_id": "fs-id1165137404973",
        "media_id": "fs-id1165134305418",
        "filename": "CNX_Precalc_Figure_01_02_207-ec92.jpg",
        "bytes": 77354,
        "sha256": "ed6289ecd1e1b0a5e1968201dd66c41bed037af71f19c88f9d65526e7df97621",
        "rights_component_id": "rights:openstax-precalculus-2e:asset:d3397ab140df88a1b432dff8"
    },
    {
        "exercise_id": "fs-id1165137544188",
        "media_id": "fs-id1165137447903",
        "filename": "CNX_Precalc_Figure_01_02_208-7f09.jpg",
        "bytes": 50951,
        "sha256": "70bac9419797b64fedaad3abdcdd0e6fd65c4bf4e383abaaaf1bc953b4046785",
        "rights_component_id": "rights:openstax-precalculus-2e:asset:9a0e7949407fb9829b6fcf50"
    },
    {
        "exercise_id": "fs-id1165135176309",
        "media_id": "fs-id1165135192955",
        "filename": "CNX_Precalc_Figure_01_02_209-37f5.jpg",
        "bytes": 68404,
        "sha256": "f428f4ffc4557cf37f2f49172fcf4866061a921e486bb27b8f121ee01626313d",
        "rights_component_id": "rights:openstax-precalculus-2e:asset:fefd09b069df1dd0d3bb18b3"
    },
    {
        "exercise_id": "fs-id1165137642580",
        "media_id": "fs-id1165134482733",
        "filename": "CNX_Precalc_Figure_01_02_210-a5dd.jpg",
        "bytes": 120875,
        "sha256": "7ed61458984c3b13439a79ba71a56945f1a6fdd8c16d5d703aa06a3ea06dbdf8",
        "rights_component_id": "rights:openstax-precalculus-2e:asset:8a216afbdf1652e8b0122943"
    },
    {
        "exercise_id": "fs-id1165137442385",
        "media_id": "fs-id1165137645308",
        "filename": "CNX_Precalc_Figure_01_02_211-3cb1.jpg",
        "bytes": 89588,
        "sha256": "99ce24dd1b7a611929d56b7855bfd6a32369813c4ca6a5610cc02a7aed76495d",
        "rights_component_id": "rights:openstax-precalculus-2e:asset:ee32fa4fd2dc0f33e7be3069"
    },
    {
        "exercise_id": "fs-id1165137851981",
        "media_id": "fs-id1165137602824",
        "filename": "CNX_Precalc_Figure_01_02_212-f3f3.jpg",
        "bytes": 98111,
        "sha256": "fee56af52a03303e87c1a2aec39f9eb90c1a831254de73a157ff2155847fe894",
        "rights_component_id": "rights:openstax-precalculus-2e:asset:2dcf59316bdae5645e7c671d"
    }
]
SOURCE_ANSWERS = {
    27: ("fs-id1165137820038", "fs-id1165137424631", "(2,8]", "[6,8)"),
    29: ("fs-id1165137847285", "fs-id1165137541038", "[-4,4]", "[0,2]"),
    31: ("fs-id1165137657479", "fs-id1165137657482", "[-5,3)", "[0,2]"),
    33: ("fs-id1165137445711", "fs-id1165137445713", "(-∞,1]", "[0,∞)"),
    35: ("fs-id1165134043582", "fs-id1165135335983",
         "[-6,-1/6]∪[1/6,6]", "[-6,-1/6]∪[1/6,6]"),
    37: ("fs-id1165137575572", "fs-id1165137601170", "[-3,∞)", "[0,∞)"),
}
NEW_DETERMINED_ANSWERS = {
    28: ("[4,8)", "(2,8]"),
    30: ("[2,6]", "[2,6]"),
    32: ("[-3,2)", "[-5,4]"),
    36: ("(-2.5,∞)", "[-4,∞)"),
}
NUMERIC = {
    "fs-id1165137424631": [
        "2",
        "8",
        "6",
        "8"
    ],
    "fs-id1165137541038": [
        "4",
        "0"
    ],
    "fs-id1165137657482": [
        "5",
        "3",
        "0",
        "2"
    ],
    "fs-id1165137445713": [
        "1",
        "0"
    ],
    "fs-id1165135335983": [
        "6",
        "1",
        "6",
        "1",
        "6",
        "6",
        "6",
        "1",
        "6",
        "1",
        "6",
        "6"
    ],
    "fs-id1165137601170": [
        "3",
        "0"
    ]
}
COUNTS = {}


def canonical(node):
    """Whitespace-insensitive XML structure; mtext content remains exact."""
    text = node.text or ""
    if node.tag != M + "mtext":
        text = text.strip()
    return (node.tag, tuple(sorted(node.attrib.items())), text,
            tuple((canonical(child), (child.tail or "").strip()) for child in node))


def math_interval_text(node):
    """Read only this source's interval grammar, preserving rational fractions."""
    kind = node.tag.rsplit("}", 1)[-1]
    if kind == "mfrac":
        if len(node) != 2:
            raise ValueError("bad source fraction")
        return math_interval_text(node[0]) + "/" + math_interval_text(node[1])
    if kind in {"mn", "mo", "mi", "mtext"}:
        return "".join((node.text or "").split())
    if kind == "mspace":
        return ""
    if kind in {"math", "mrow"}:
        return "".join(math_interval_text(child) for child in node)
    raise ValueError("unsupported interval MathML: " + kind)


def parse_intervals(expression):
    """Return a finite union of exact rational intervals; None denotes infinity."""
    expression = "".join(expression.split()).replace("−", "-")
    expression = expression.replace(r"\infty", "∞").replace(r"\cup", "∪")
    expression = expression.rstrip(",;.")
    result = []
    for part in expression.split("∪"):
        if len(part) < 5 or part[0] not in "([" or part[-1] not in ")]":
            raise ValueError("invalid interval boundary")
        left_closed, right_closed = part[0] == "[", part[-1] == "]"
        endpoints = part[1:-1].split(",")
        if len(endpoints) != 2:
            raise ValueError("exactly two interval endpoints required")
        low_text, high_text = endpoints
        if low_text == "∞" or high_text == "-∞":
            raise ValueError("infinity has the wrong sign")
        low = None if low_text == "-∞" else F(low_text)
        high = None if high_text == "∞" else F(high_text)
        if (low is None and left_closed) or (high is None and right_closed):
            raise ValueError("infinity is not an included endpoint")
        if low is not None and high is not None:
            if low > high or (low == high and not (left_closed and right_closed)):
                raise ValueError("empty or reversed interval")
        result.append((low, high, left_closed, right_closed))
    return tuple(result)


def contains(intervals, value):
    value = F(value)
    return any(
        (low is None or value > low or (left_closed and value == low))
        and (high is None or value < high or (right_closed and value == high))
        for low, high, left_closed, right_closed in intervals
    )


def answer_block(draft, anchor):
    marker = "{#" + anchor + "}"
    assert draft.count(marker) == 1, "unique answer anchor"
    return draft.split(marker, 1)[1].split("\n### ", 1)[0]


def tests(originals=False):
    counts = {"source_structure_asset": 0, "finite_interval_checks": 0,
              "optional_original_source": 0}

    def check(condition, label, category="source_structure_asset"):
        assert condition, label
        counts[category] += 1

    def finite(condition, label):
        check(condition, label, "finite_interval_checks")

    excerpt_data = (ROOT / "sources/m49304-domain-range-exercises-source.cnxml").read_bytes()
    check(sha256(excerpt_data).hexdigest() == EXCERPT_SHA, "pinned complete excerpt bytes")
    excerpt = ET.fromstring(excerpt_data)
    draft = (ROOT / "translation/A30-U026-domain-range-exercises.vi.md").read_text(encoding="utf-8")
    check(draft == unicodedata.normalize("NFC", draft), "Vietnamese NFC")
    flat = " ".join(draft.split())
    source_ids = [node.get("id") for node in excerpt.iter() if node.get("id")]
    by_id = {node.get("id"): node for node in excerpt.iter() if node.get("id")}
    check(len(source_ids) == len(set(source_ids)) == 47, "47 unique original IDs")
    anchors = re.findall(r"\{#([^}]+)\}", draft)
    check(all(n == 1 for n in Counter(anchors).values()), "all draft anchors unique")
    for identity in source_ids:
        check(anchors.count(identity) == 1, "source anchor " + identity)
    check(STOP not in source_ids and "fs-id1165135176628" not in source_ids,
          "exclude next shared prompt and U024-owned outer exercise wrapper")

    section = excerpt.find(CN + "content/" + CN + "section")
    exercises = list(section.iter(CN + "exercise"))
    check(section.get("id") == SECTION, "Graphical parent retained here")
    check(section[0].tag == CN + "title" and section[0].text == "Graphical",
          "exact shared Graphical title")
    check(section[1].get("id") == PROMPT, "first shared interval prompt")
    check(len(section) == 13 and section[-1].get("id") == "fs-id1165137851981",
          "eleven complete exercises after title/prompt")
    check([node.get("id") for node in exercises] == [a["exercise_id"] for a in ASSETS],
          "eleven selected exercises in original order")
    check([node.get("id") for node in section.iter(CN + "solution")] ==
          [value[0] for value in SOURCE_ANSWERS.values()], "six supplied source solutions")
    check(not list(section.iter(CN + "example")), "no source examples")
    check(not list(section.iter(CN + "table")), "no source tables")
    check(not list(section.iter(CN + "figure")), "media nodes, not figure wrappers")
    check(not list(section.iter(CN + "link")), "no original source crossreferences")
    check(draft.count("**Đáp án nguồn:") == 6, "six source-answer labels")
    check(draft.count("**Lời giải bổ sung — nguồn không kèm đáp án.**") == 5,
          "five visibly supplementary answers")
    check("bằng ký hiệu khoảng" in flat, "shared instruction translated")
    for number, exercise in enumerate(exercises, 27):
        check("### Bài " + str(number) + " {#" + exercise.get("id") + "}" in draft,
              "continuous source exercise number " + str(number))
        check((exercise.find(CN + "solution") is not None) == (number in SOURCE_ANSWERS),
              "source answer presence/absence " + str(number))

    source_math = list(excerpt.iter(M + "math"))
    refs = re.findall(r"\{\{math:([^:}]+):(\d+)\}\}", draft)
    check(len(source_math) == len(refs) == 12, "twelve source MathML captures")
    captures = [list(by_id[owner].iter(M + "math"))[int(index)] for owner, index in refs]
    check(Counter(map(id, captures)) == Counter(map(id, source_math)), "each source math once")
    check(captures == source_math, "unchanged source-math sequence")
    check([node.text for node in excerpt.iter(M + "mtext")] == ["\u00a04],", "\u00a02]"],
          "numeric mtext endpoints, brackets and punctuation retained exactly")
    for identity, expected in NUMERIC.items():
        check([node.text for node in by_id[identity].iter(M + "mn")] == expected,
              "source numeric tokens " + identity)

    source_targets = {n: answer[0] for n, answer in SOURCE_ANSWERS.items()}
    expected_links = [source_targets.get(n, "vi-answer-" + str(n)) for n in range(27, 38)]
    local_links = re.findall(r"(?<!!)\[[^\]]+\]\(#([^)]+)\)", draft)
    check(local_links == expected_links, "eleven source/supplement answer links")
    for target in local_links:
        check(anchors.count(target) == 1, "answer target " + target)
    check(not re.findall(r"\]\(A30-[^)]+\.html", draft), "no cross-reader dependencies")
    external = re.findall(r"\]\((https?://[^)]+)\)", draft)
    check(len(external) == 3, "three attribution links only; not fetched")
    for expected in ("789b54099106b071d1d32bfcee454fed72eb4768",
                     "0.1.0-alpha.58-reader.1", "creativecommons.org/licenses/by-nc-sa/4.0/",
                     "Copyright Rice University, OpenStax", "chưa có thẩm định của người bản ngữ"):
        check(expected in flat, "standalone provenance statement " + expected)

    image_refs = re.findall(r"!\[[^\n]+\]\(\.\./assets/([^)]+)\)", draft)
    check(image_refs == [a["filename"] for a in ASSETS], "eleven unchanged image references")
    check(len(list(section.iter(CN + "media"))) == 11, "eleven media wrappers")
    check([Path(node.get("src")).name for node in section.iter(CN + "image")] == image_refs,
          "source images in draft order")
    committed_assets = {}
    for asset in ASSETS:
        data = (ROOT / "assets" / asset["filename"]).read_bytes()
        committed_assets[asset["filename"]] = data
        check(len(data) == asset["bytes"], "exact image byte count " + asset["filename"])
        check(sha256(data).hexdigest() == asset["sha256"], "exact image hash " + asset["filename"])
        check(asset["filename"] in ET.tostring(by_id[asset["media_id"]], encoding="unicode"),
              "correct source media/image binding " + asset["media_id"])

    for phrase in ("tăng theo hướng xuống dưới", "Không đổi dấu",
                   "Tập giá trị không phải $[-6,-2]$",
                   "đáp án nguồn và mô tả Indonesia đều xác nhận cận phải là 1",
                   "Mô tả Indonesia ghi điểm nối đầu tiên là $(-1,5)$",
                   "điểm đó nằm trên trục đứng", "không phải một nhánh của hàm số",
                   "không kéo dài đường cong qua các đầu mút",
                   "Mô tả Indonesia nêu rõ nhánh bên phải đi lên không bị chặn"):
        check(phrase in flat, "explicit source-image qualification " + phrase)
    check(by_id["fs-id1165137447903"].get("alt") ==
          "Graph of a function from (-infinity, 2].", "wrong English208 alt preserved in excerpt")
    check(by_id["fs-id1165135192955"].get("alt") ==
          "Graph of a function from [-4, infinity).", "English209 domain evidence retained")
    check(by_id["fs-id1165137645308"].get("alt") ==
          "Graph of a function from (-2.5, infinity).", "English211 domain evidence retained")

    actual = {}
    for number, (solution, owner, domain, range_) in SOURCE_ANSWERS.items():
        pair = list(by_id[owner].iter(M + "math"))
        actual[number] = tuple(parse_intervals(math_interval_text(node)) for node in pair)
        finite(len(pair) == 2, "source answer domain/range pair " + str(number))
        finite(actual[number] == (parse_intervals(domain), parse_intervals(range_)),
               "actual original interval answers " + str(number))
        check("**Đáp án nguồn:" in answer_block(draft, solution),
              "source answer label bound to correct solution " + str(number))
    for number, expected in NEW_DETERMINED_ANSWERS.items():
        block = answer_block(draft, "vi-answer-" + str(number))
        tokens = re.findall(r"\$([^$\n]+)\$", block)
        finite(len(tokens) >= 2, "supplementary interval pair present " + str(number))
        actual[number] = tuple(parse_intervals(token) for token in tokens[:2])
        finite(actual[number] == tuple(parse_intervals(token) for token in expected),
               "supplementary intervals read from draft " + str(number))

    qualified = answer_block(draft, "vi-answer-34")
    qualified_flat = " ".join(qualified.split())
    for phrase in ("**Giới hạn thông tin nguồn:**",
                   "không tự chứng minh rằng đầu ra tăng không bị chặn",
                   "chưa thể khẳng định chính xác cận trên",
                   "**giả thiết bổ sung rằng nhánh tiếp tục tăng không bị chặn trên**",
                   "Đây là kết luận có điều kiện", "không phải đáp án nguồn"):
        check(phrase in qualified_flat, "exercise34 explicit uncertainty " + phrase)
    check("**Đáp án nguồn" not in qualified, "exercise34 has no fabricated source answer")
    domain34 = parse_intervals(re.findall(r"\$([^$\n]+)\$", qualified)[0])
    finite(domain34 == parse_intervals("[-4,∞)"), "exercise34 source-supported domain")
    check(r"$[-2,\infty)$" in qualified, "conditional range displayed, not silently omitted")
    conditional_range34 = parse_intervals("[-2,∞)")
    finite(contains(domain34, -4) and not contains(domain34, F(-401, 100)),
           "exercise34 included domain endpoint")
    finite(contains(conditional_range34, -2) and not contains(conditional_range34, -3),
           "conditional interval arithmetic only; not evidence for its upper bound")
    actual[34] = (domain34, None)
    finite(sum(value[1] is not None for value in actual.values()) == 10,
           "ten determined ranges, not eleven")

    # Exact boundary and inside/outside tests on the intervals just read above.
    # These do not sample an inferred curve or claim universal graph coverage.
    for number in sorted(actual):
        for axis, intervals in zip(("domain", "range"), actual[number]):
            if intervals is None:
                continue
            for low, high, left_closed, right_closed in intervals:
                for bound, closed, direction in (
                    (low, left_closed, 1), (high, right_closed, -1)
                ):
                    if bound is None:
                        continue
                    epsilon = F(1, 100)
                    if low is not None and high is not None:
                        epsilon = min(epsilon, (high - low) / 100)
                    finite(contains(intervals, bound) == closed,
                           f"{number} {axis} endpoint {bound}")
                    finite(contains(intervals, bound + direction * epsilon),
                           f"{number} {axis} immediately inside {bound}")
                    finite(not contains(intervals, bound - direction * epsilon),
                           f"{number} {axis} immediately outside {bound}")
    for number, x, y, x_expected, y_expected in (
        (27, 8, 8, True, False),
        (31, 3, 2, False, True),
        (32, 2, 0, False, True),
        (36, F(-5, 2), 10, False, True),
    ):
        finite(contains(actual[number][0], x) == x_expected
               and contains(actual[number][1], y) == y_expected,
               f"{number}: excluded point need not exclude its output")
    for point, expected in (
        (-7, False), (-6, True), (F(-1, 6), True), (F(-1, 7), False),
        (0, False), (F(1, 7), False), (F(1, 6), True), (6, True), (7, False)
    ):
        finite(all(contains(intervals, point) == expected for intervals in actual[35]),
               "bounded rational union at " + str(point))
    finite(contains(actual[30][1], 6) and not contains(actual[30][1], -6),
           "downward-positive y values are not negated")
    for invalid in ("[-∞,0)", "(0,∞]", "(∞,2]", "[2,-∞)", "[3,2]", "(1,1)"):
        try:
            parse_intervals(invalid)
        except ValueError:
            rejected = True
        else:
            rejected = False
        finite(rejected, "interval parser rejects " + invalid)

    if originals:
        trees, raw = {}, {}
        for language, relative, digest in ORIGINALS:
            data = (ROOT.parent / relative).read_bytes()
            check(sha256(data).hexdigest() == digest, "full pinned source " + language,
                  "optional_original_source")
            trees[language] = ET.fromstring(data)
            raw[language] = ROOT.parent / relative
        extractor_path = ROOT / "tools/extract_domain_range_exercises.py"
        spec = spec_from_file_location("u026_extractor", extractor_path)
        extractor = module_from_spec(spec)
        spec.loader.exec_module(extractor)
        check(extractor.extract(raw["en"]).encode("utf-8") == excerpt_data,
              "exact current English extraction and source adjacency", "optional_original_source")
        id_excerpt = ET.fromstring(extractor.extract(raw["id"]))
        check([node.get("id") for node in id_excerpt.iter() if node.get("id")] == source_ids,
              "all selected Indonesian IDs/order and source exercise positions", "optional_original_source")
        check([canonical(node) for node in id_excerpt.iter(M + "math")] ==
              [canonical(node) for node in source_math],
              "all twelve EN/ID MathML including exact numeric mtext", "optional_original_source")
        check([node.text for node in id_excerpt.iter(M + "mtext")] == ["\u00a04],", "\u00a02]"],
              "Indonesian numeric mtext unchanged", "optional_original_source")
        id_by_id = {node.get("id"): node for node in id_excerpt.iter() if node.get("id")}
        for media, phrase in (
            ("fs-id1165137837060", "sumbu y bertambah ke bawah"),
            ("fs-id1165137447903", "(1, 0)"),
            ("fs-id1165135192955", "terus naik ke kanan dengan panah"),
            ("fs-id1165137645308", "naik tanpa batas ke kanan"),
            ("fs-id1165137602824", "(−1, 5)"),
        ):
            check(phrase in id_by_id[media].get("alt"),
                  "exact Indonesian alt evidence " + media, "optional_original_source")
        rights = ROOT.parent / "downloads/a30-edition/source-core/00_control/COMPONENT_RIGHTS.csv"
        with rights.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        for asset in ASSETS:
            filename = asset["filename"]
            for directory in ("downloads/upstream-openstax/media",
                              "downloads/a30-edition/source-core/repo/source/media"):
                data = (ROOT.parent / directory / filename).read_bytes()
                check(data == committed_assets[filename], "original asset bytes " + directory + "/" + filename,
                      "optional_original_source")
            matches = [row for row in rows if row["asset_path"] == "media/" + filename]
            check(len(matches) == 1, "one inherited component row " + filename,
                  "optional_original_source")
            row = matches[0]
            check(row["sha256"] == asset["sha256"] and int(row["bytes"]) == asset["bytes"],
                  "inherited component bytes/hash " + filename, "optional_original_source")
            check(row["rights_component_id"] == asset["rights_component_id"]
                  and row["source_modules"] == "m49304"
                  and row["admission"] == "admitted"
                  and row["classification"] == "WORK_DEFAULT_UNCREDITED_ART"
                  and row["license_id"] == "CC-BY-NC-SA-4.0",
                  "exact already-admitted component identity/status " + filename,
                  "optional_original_source")
            check(row["attribution"] ==
                  "Copyright Rice University, OpenStax, under CC BY-NC-SA 4.0."
                  and row["required_action"] ==
                  "Preserve work attribution, change notice, ShareAlike, and non-endorsement.",
                  "inherited attribution/required action " + filename, "optional_original_source")

    COUNTS.clear()
    COUNTS.update(counts)
    return sum(counts.values())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--originals", action="store_true")
    total = tests(parser.parse_args().originals)
    print(f"PASS: {total} mixed assertions; breakdown {COUNTS}")
    print("Exercise34 upper range remains qualified; counts are not semantic or native-fluency proof.")
