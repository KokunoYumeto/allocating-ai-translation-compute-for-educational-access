"""U021 source preservation and exact finite domain/range checks.

Default: committed excerpt, draft and ten assets; Python standard library only.
--originals explicitly checks existing full pinned EN/ID sources and inherited
asset rows. Nothing is fetched or written. Finite evaluations do not prove the
infinite-domain/range claims; the draft's arguments and review remain essential.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from math import isqrt
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
SECTION = "fs-id1165134384565"
STOP = "fs-id1165135440477"
EXCERPT_SHA = "59ca3d84c8aa0b36d90873c7c502974e2d218ee56c91e8dc763bec68b121b149"
ORIGINALS = (
    ("en", "downloads/upstream-openstax/modules/m49304/index.cnxml",
     "0e230c4c96d46e7962dcb3afa1f1630718f7e1cdfae9e665d640690ab6ace19c"),
    ("id", "downloads/a30-edition/source-core/repo/source/modules/m49304/index.cnxml",
     "a341bb8c05830b95c865b18d64b186fc9a88a08640bbb12f030879faa90b7539"),
)
ASSETS = [
    {
        "figure_id": "Figure_01_02_011",
        "media_id": "fs-id1165137661673",
        "filename": "CNX_Precalc_Figure_01_02_011-7288.jpg",
        "bytes": 66851,
        "sha256": "8eb7081bfbe416a6d06ca99899d3fda64842fad30516536ba9511e8597c26cf3"
    },
    {
        "figure_id": "Figure_01_02_012",
        "media_id": "fs-id1165137543965",
        "filename": "CNX_Precalc_Figure_01_02_012-7156.jpg",
        "bytes": 83392,
        "sha256": "48edd0ff56f73361ba4c1167fe3169e19bb85153d6999a0f54cea30fbac65753"
    },
    {
        "figure_id": "Figure_01_02_013",
        "media_id": "fs-id1165137757797",
        "filename": "CNX_Precalc_Figure_01_02_013-f38f.jpg",
        "bytes": 81812,
        "sha256": "cd336d07625d4618944cbd15058e2ce9c17bc78f49f69c5b35ed130e4a199bbd"
    },
    {
        "figure_id": "Figure_01_02_014",
        "media_id": "fs-id1165137448012",
        "filename": "CNX_Precalc_Figure_01_02_014-babe.jpg",
        "bytes": 78839,
        "sha256": "9ac0a70921e7cb66b6a7acd2293720bc8ed5d48b536885413ecfa3c73dc4c2f9"
    },
    {
        "figure_id": "Figure_01_02_015",
        "media_id": "fs-id1165137660840",
        "filename": "CNX_Precalc_Figure_01_02_015-2cf1.jpg",
        "bytes": 78203,
        "sha256": "f9ac62ad099b1950b9b760778690291296e745a02a646a2ffdb89ea3d963beb6"
    },
    {
        "figure_id": "Figure_01_02_016",
        "media_id": "fs-id1165137582779",
        "filename": "CNX_Precalc_Figure_01_02_016-44f1.jpg",
        "bytes": 84972,
        "sha256": "aa28ed9357d2ec909aa5102604679049f7e5c555b548ec39b9fc3faac1f7f3fc"
    },
    {
        "figure_id": "Figure_01_02_017",
        "media_id": "fs-id1165133004481",
        "filename": "CNX_Precalc_Figure_01_02_017-7cac.jpg",
        "bytes": 82903,
        "sha256": "b1d8278ad3cba150b89ef9a1a1578d5c802ea4d9a68df8b9fbd5b20a240fb026"
    },
    {
        "figure_id": "Figure_01_02_018",
        "media_id": "fs-id1165137401809",
        "filename": "CNX_Precalc_Figure_01_02_018-edda.jpg",
        "bytes": 74809,
        "sha256": "39ac9d3cbefdffd04002cb315ed1d5745da073c45559f5849b36fc8c34cc3876"
    },
    {
        "figure_id": "Figure_01_02_019",
        "media_id": "fs-id1165137730429",
        "filename": "CNX_Precalc_Figure_01_02_019-5e97.jpg",
        "bytes": 78601,
        "sha256": "2f3a89aad4f7c12781f370e4c33f16325855c53054c189de7ec34090cd27673e"
    },
    {
        "figure_id": "Figure_01_02_020",
        "media_id": "fs-id1165135582217",
        "filename": "CNX_Precalc_Figure_01_02_020-d001.jpg",
        "bytes": 68309,
        "sha256": "28653095d1f66d1facec9784b6ff3a437a84691a9d144e687f8747c1b78beefd"
    }
]
NUMERIC = {
    "Figure_01_02_014": [
        "2"
    ],
    "Figure_01_02_015": [
        "3"
    ],
    "Figure_01_02_016": [
        "1",
        "0"
    ],
    "Figure_01_02_017": [
        "1",
        "2",
        "0",
        "0"
    ],
    "Figure_01_02_019": [
        "3"
    ],
    "fs-id1165135613224": [
        "2",
        "3"
    ],
    "fs-id1165137419507": [
        "2",
        "1"
    ],
    "fs-id1165137855321": [
        "−1",
        "−1",
        "−1",
        "0",
        "0"
    ],
    "fs-id1165137661054": [
        "2",
        "4"
    ],
    "eip-id1165137567088": [
        "4",
        "0",
        "4"
    ],
    "fs-id1165137465335": [
        "4"
    ],
    "fs-id1165137544393": [
        "4",
        "0",
        "0"
    ],
    "fs-id1165137475545": [
        "2"
    ],
    "fs-id1165137725047": [
        "2",
        "0"
    ]
}

COUNTS = {}


def canonical(node):
    return (node.tag, tuple(sorted(node.attrib.items())), (node.text or "").strip(),
            tuple((canonical(child), (child.tail or "").strip()) for child in node))


def integer_root(number, degree):
    """Return an exact integer root or reject an irrational result."""
    if degree == 2:
        result = isqrt(number)
        if result ** 2 == number:
            return result
        raise ValueError("non-square input to exact finite evaluator")
    assert degree == 3
    low, high = 0, max(1, number)
    while low <= high:
        middle = (low + high) // 2
        power = middle ** degree
        if power == number:
            return middle
        if power < number:
            low = middle + 1
        else:
            high = middle - 1
    raise ValueError("non-cube input to exact finite evaluator")


def rational_root(value, degree):
    """Principal real square root; real cube root, including negative inputs."""
    value = F(value)
    if value < 0 and degree == 2:
        raise ValueError("negative real radicand")
    sign = -1 if value < 0 else 1
    return F(sign * integer_root(abs(value.numerator), degree),
             integer_root(value.denominator, degree))


def evaluate_sequence(nodes, env):
    """Only the +, -, implicit-product and absolute-value grammar used here."""
    nodes = list(nodes)
    if (len(nodes) >= 2 and nodes[0].tag == nodes[-1].tag == M + "mo"
            and nodes[0].text == nodes[-1].text == "|"):
        return abs(evaluate_sequence(nodes[1:-1], env))
    total, product, sign, has_atom = F(0), F(1), 1, False
    for node in nodes:
        if node.tag == M + "mo":
            operator = (node.text or "").strip()
            assert operator in {"+", "-", "−"}, "unsupported arithmetic operator"
            if has_atom:
                total += sign * product
                product, sign, has_atom = F(1), 1, False
            if operator in {"-", "−"}:
                sign *= -1
        else:
            product *= evaluate_node(node, env)
            has_atom = True
    assert has_atom, "missing arithmetic operand"
    return total + sign * product


def evaluate_node(node, env):
    kind = node.tag.rsplit("}", 1)[-1]
    if kind == "mn":
        return F((node.text or "").strip().replace("−", "-"))
    if kind == "mi":
        return F(env[(node.text or "").strip()])
    if kind in {"mrow", "math"}:
        return evaluate_sequence(list(node), env)
    if kind == "mfrac":
        assert len(node) == 2
        return evaluate_node(node[0], env) / evaluate_node(node[1], env)
    if kind == "msup":
        exponent = evaluate_node(node[1], env)
        assert exponent.denominator == 1
        return evaluate_node(node[0], env) ** exponent.numerator
    if kind == "msqrt":
        return rational_root(evaluate_sequence(list(node), env), 2)
    if kind == "mroot":
        assert len(node) == 2
        # Figure018's original empty index encodes the intended square root.
        # Retain both original children; never prune this empty index.
        if node[1].tag == M + "mrow" and not len(node[1]) and not (node[1].text or "").strip():
            degree = 2
        else:
            degree_value = evaluate_node(node[1], env)
            assert degree_value.denominator == 1
            degree = degree_value.numerator
        assert degree in {2, 3}
        return rational_root(evaluate_node(node[0], env), degree)
    raise AssertionError("unsupported source node: " + kind)


def evaluate_function(source_math, x, c=F(0)):
    """Evaluate the RHS of an actual preserved f(x)=... source expression."""
    node = source_math
    while node.tag in {M + "math", M + "mrow"} and len(node) == 1:
        node = node[0]
    children = list(node)
    equals = [i for i, child in enumerate(children)
              if child.tag == M + "mo" and child.text == "="]
    assert len(equals) == 1
    rhs = children[equals[0] + 1:]
    while rhs and rhs[-1].tag == M + "mo" and rhs[-1].text in {",", "."}:
        rhs.pop()
    return evaluate_sequence(rhs, {"x": F(x), "c": F(c)})


def tests(originals=False):
    counts = {"source_structure_asset": 0, "exact_finite_arithmetic": 0,
              "optional_original_source": 0}

    def check(condition, label, category="source_structure_asset"):
        assert condition, label
        counts[category] += 1

    excerpt_path = ROOT / "sources/m49304-toolkit-domains-ranges-source.cnxml"
    data = excerpt_path.read_bytes()
    check(sha256(data).hexdigest() == EXCERPT_SHA, "pinned complete excerpt")
    excerpt = ET.fromstring(data)
    draft = (ROOT / "translation/A30-U021-toolkit-domains-ranges.vi.md").read_text(encoding="utf-8")
    check(draft == unicodedata.normalize("NFC", draft), "Vietnamese NFC")
    flat = " ".join(draft.split())
    source_ids = [node.get("id") for node in excerpt.iter() if node.get("id")]
    by_id = {node.get("id"): node for node in excerpt.iter() if node.get("id")}
    check(len(source_ids) == len(set(source_ids)) == 55, "55 unique source IDs")
    anchors = re.findall(r"\{#([^}]+)\}", draft)
    check(all(n == 1 for n in Counter(anchors).values()), "unique translated anchors")
    for identity in source_ids:
        check(anchors.count(identity) == 1, "explicit source anchor " + identity)

    section = excerpt.find(CN + "content/" + CN + "section")
    check(section.get("id") == SECTION and STOP not in source_ids, "bounded selected section")
    check(section[-1].get("id") == "fs-id1165137430800", "complete final Try It note")
    check(section[-1].find(CN + "exercise").get("id") == "ti_01_02_05", "final Try It exercise")
    check([n.get("id") for n in section.iter(CN + "example")] ==
          ["Example_01_02_08", "Example_01_02_09", "Example_01_02_10"], "three source examples")
    check([n.get("id") for n in section.iter(CN + "exercise")] ==
          ["fs-id1165137558723", "fs-id1165137448155", "fs-id1165137574740", "ti_01_02_05"],
          "three example exercises plus one Try It")
    check([n.get("id") for n in section.iter(CN + "solution")] ==
          ["fs-id1165135458670", "fs-id1165137871182", "fs-id1165137584342", "fs-id1165137833252"],
          "all four source-supplied answers")
    check(draft.count("**Lời giải nguồn.**") == 3, "three supplied worked-solution labels")
    check(draft.count("**Đáp án nguồn:**") == 1, "one supplied Try It answer label")
    check("### Tự thử 7 {#fs-id1165137430800}" in draft, "continuous Try It display numbering")
    check(len(list(section.iter(CN + "caption"))) == 9, "nine full source captions")
    check(draft.count("*Chú thích nguồn:*") == 9, "nine translated source-caption labels")
    check(draft.count("Nhãn trong hình:") == 9, "nine accessible domain/range label transcriptions")
    check(len(list(by_id["fs-id1165137405229"].iter(CN + "item"))) == 4, "all four How To items")
    check(not list(section.iter(CN + "table")), "no source table omitted")
    check([n.get("id") for n in section.iter(CN + "commentary")] ==
          ["fs-id1165137572635"], "Example10 analysis")
    check([n.get("id") for n in section.iter(CN + "equation")] ==
          ["eip-id1165137567088"], "radicand inequality equation")

    math = list(excerpt.iter(M + "math"))
    references = re.findall(r"\{\{math:([^:}]+):(\d+)\}\}", draft)
    check(len(math) == len(references) == 41, "41 source MathML captures")
    captured = [list(by_id[identity].iter(M + "math"))[int(index)]
                for identity, index in references]
    check(Counter(map(id, captured)) == Counter(map(id, math)), "each source expression exactly once")
    check(captured == math, "source math sequence retained")
    check([n.text for n in excerpt.iter(M + "mtext")] == ["\u00a0when\u00a0"], "exact mtext dictionary key")
    for identity, numbers in NUMERIC.items():
        check([n.text for n in by_id[identity].iter(M + "mn")] == numbers,
              "unchanged source numerical tokens " + identity)
    square_root = list(by_id["Figure_01_02_018"].iter(M + "math"))[0]
    encoded_root = next(square_root.iter(M + "mroot"))
    check(len(encoded_root) == 2 and encoded_root[1].tag == M + "mrow"
          and len(encoded_root[1]) == 0 and not (encoded_root[1].text or "").strip(),
          "square-root empty index retained as source encodes it")
    check(by_id["fs-id1165137660840"].get("alt") == "Cubic function f(x)-x^3.",
          "original mistaken cubic alt retained in source")
    check("“f(x)-x^3”" in draft and "Không sửa ảnh nguồn" in draft,
          "Vietnamese cubic-alt correction explicitly disclosed")
    check("nhân với 2" in draft and "Câu giải thích tiếng Anh" in draft,
          "Example8 full arithmetic prose and source clarification")
    for phrase in ("không phải tập rỗng", "không phải khái niệm hàm số ngược",
                   "không âm", "không có nghĩa là đầu ra phải là số nguyên lẻ",
                   "mọi giá trị nằm giữa hai giá trị đầu ra",
                   "không giả định hàm số đồng biến", "không thay cho lập luận",
                   "chưa có thẩm định của người bản ngữ"):
        check(phrase in flat, "explicit mathematical/review qualification: " + phrase)
    for expression in (r"$x=1/y$", r"$x=1/\sqrt{y}$", r"$x=y^2$", r"$x=y^3$",
                       r"$M=|y|+1$", r"$$x=\frac{2}{y}-1.$$",
                       r"$$x=\left(\frac{y}{2}\right)^2-4.$$",
                       r"$x=2-y^2$", r"$$f(x)=-\sqrt{y^2}=-|y|=y.$$"):
        check(expression in draft, "labeled range converse present: " + expression)

    source_links = [n.get("target-id") for n in section.iter(CN + "link")]
    local_links = re.findall(r"\]\(#([^)]+)\)", draft)
    check(source_links == ["Figure_01_02_020"], "one original figure crossreference")
    check(local_links == source_links + ["fs-id1165137833252"], "source link and added answer link")
    for target in local_links:
        check(anchors.count(target) == 1, "unique local link target " + target)
    check(not re.findall(r"\]\((A30-[^)]+\.html[^)]*)\)", draft), "no cross-reader dependencies")
    external_links = re.findall(r"\]\((https?://[^)]+)\)", draft)
    check(len(external_links) == 3, "three unchanged-scope attribution links only")
    check("789b54099106b071d1d32bfcee454fed72eb4768" in draft and
          "0.1.0-alpha.58-reader.1" in draft and
          "Copyright Rice University, OpenStax." in draft,
          "source pins and Rice/OpenStax attribution")
    check("https://creativecommons.org/licenses/by-nc-sa/4.0/" in external_links,
          "inherited CC-BY-NC-SA license link")

    images = re.findall(r"!\[([^\]]+)\]\(([^)]+)\)", draft)
    check(len(images) == 10 and all(len(alt) >= 70 for alt, _ in images),
          "ten accessible original-image descriptions")
    check([target for _, target in images] == ["../assets/" + a["filename"] for a in ASSETS],
          "ten original filenames and source order")
    check([n.get("id") for n in section.iter(CN + "figure")] ==
          [a["figure_id"] for a in ASSETS], "all ten source figures")
    for asset in ASSETS:
        source_image = by_id[asset["media_id"]].find(CN + "image")
        check(source_image.get("src") == "../../media/" + asset["filename"], "source image reference")
        path = ROOT / "assets" / asset["filename"]
        check(path.is_file(), "committed original asset exists: " + asset["filename"])
        actual = path.read_bytes()
        check(len(actual) == asset["bytes"] and sha256(actual).hexdigest() == asset["sha256"],
              "unchanged admitted bytes " + asset["filename"])

    functions = {identity: list(by_id[identity].iter(M + "math"))[0]
                 for identity in [a["figure_id"] for a in ASSETS[:9]] +
                 ["fs-id1165135613224", "fs-id1165137419507", "fs-id1165137661054",
                  "fs-id1165137475545"]}
    category = "exact_finite_arithmetic"

    def value(identity, x, c=F(0)):
        return evaluate_function(functions[identity], x, c)

    def rejects(identity, x, error):
        try:
            value(identity, x)
        except error:
            check(True, "forbidden real input " + identity, category)
        else:
            raise AssertionError("forbidden input was accepted: " + identity)

    for c in [F(-2), F(0), F(3, 2)]:
        for x in [F(-5), F(0), F(4, 3)]:
            check(value("Figure_01_02_011", x, c) == c, "constant singleton output", category)
    pairs = {
        "Figure_01_02_012": [(F(-2), F(-2)), (F(0), F(0)), (F(3, 2), F(3, 2))],
        "Figure_01_02_013": [(F(-2), F(2)), (F(-1, 2), F(1, 2)), (F(0), F(0)), (F(3), F(3))],
        "Figure_01_02_014": [(F(-2), F(4)), (F(0), F(0)), (F(1, 2), F(1, 4))],
        "Figure_01_02_015": [(F(-2), F(-8)), (F(-1, 2), F(-1, 8)), (F(0), F(0)), (F(3), F(27))],
        "Figure_01_02_016": [(F(-4), F(-1, 4)), (F(-1, 2), F(-2)), (F(1, 2), F(2)), (F(2), F(1, 2))],
        "Figure_01_02_017": [(F(-2), F(1, 4)), (F(-1, 2), F(4)), (F(1, 2), F(4)), (F(2), F(1, 4))],
        "Figure_01_02_018": [(F(0), F(0)), (F(1, 4), F(1, 2)), (F(4), F(2)), (F(9), F(3))],
        "Figure_01_02_019": [(F(-8), F(-2)), (F(-1, 8), F(-1, 2)), (F(0), F(0)),
                               (F(1, 8), F(1, 2)), (F(27), F(3))],
        "fs-id1165135613224": [(F(-2), F(-14)), (F(-1), F(-1)), (F(0), F(0)),
                                (F(1), F(1)), (F(2), F(14))],
        "fs-id1165137419507": [(F(-3), F(-1)), (F(-2), F(-2)), (F(0), F(2)),
                                (F(1), F(1)), (F(3), F(1, 2))],
        "fs-id1165137661054": [(F(-4), F(0)), (F(-15, 4), F(1)), (F(0), F(4)), (F(5), F(6))],
        "fs-id1165137475545": [(F(2), F(0)), (F(7, 4), F(-1, 2)), (F(1), F(-1)),
                                (F(-2), F(-2)), (F(-7), F(-3))],
    }
    for identity, witnesses in pairs.items():
        for x, expected in witnesses:
            check(value(identity, x) == expected, f"exact source evaluation {identity}({x})", category)
    rejects("Figure_01_02_016", F(0), ZeroDivisionError)
    rejects("Figure_01_02_017", F(0), ZeroDivisionError)
    rejects("Figure_01_02_018", F(-1), ValueError)
    rejects("fs-id1165137419507", F(-1), ZeroDivisionError)
    rejects("fs-id1165137661054", F(-5), ValueError)
    rejects("fs-id1165137475545", F(3), ValueError)

    for y in [F(-3), F(-1, 2), F(1, 2), F(7)]:
        check(value("Figure_01_02_016", 1 / y) == y, "reciprocal converse", category)
        x = 2 / y - 1
        check(x != -1 and value("fs-id1165137419507", x) == y, "Example9 converse", category)
    for y in [F(1, 4), F(1), F(4), F(9)]:
        x = 1 / rational_root(y, 2)
        check(x != 0 and value("Figure_01_02_017", x) == y, "reciprocal-square converse", category)
    for y in [F(0), F(1, 2), F(2), F(5)]:
        check(value("Figure_01_02_018", y ** 2) == y, "principal square-root converse", category)
        x = (y / 2) ** 2 - 4
        check(x >= -4 and value("fs-id1165137661054", x) == y, "Example10 converse", category)
    for y in [F(-3), F(-1, 2), F(0), F(1, 2), F(3)]:
        check(value("Figure_01_02_019", y ** 3) == y, "cube-root converse", category)
    for y in [F(0), F(-1, 2), F(-2), F(-7, 3)]:
        x = 2 - y ** 2
        check(x <= 2 and value("fs-id1165137475545", x) == -abs(y) == y,
              "negative-square-root converse on y<=0", category)
    for y in [F(-100), F(-1), F(0), F(2, 3), F(51, 2)]:
        bound = abs(y) + 1
        check(value("fs-id1165135613224", -bound) < y <
              value("fs-id1165135613224", bound), "cubic finite bracketing witnesses", category)

    if originals:
        category = "optional_original_source"
        spec = spec_from_file_location("u021_extract", ROOT / "tools/extract_toolkit_domains_ranges.py")
        extractor = module_from_spec(spec)
        spec.loader.exec_module(extractor)
        for language, relative, expected_sha in ORIGINALS:
            path = ROOT.parent / relative
            check(path.is_file(), "actual source exists " + language, category)
            check(sha256(path.read_bytes()).hexdigest() == expected_sha, "pinned full source " + language, category)
            selected_text = extractor.extract(path)
            selected = ET.fromstring(selected_text)
            check([n.get("id") for n in selected.iter() if n.get("id")] == source_ids,
                  "actual selected IDs/order " + language, category)
            selected_math = list(selected.iter(M + "math"))
            if language == "id":
                differences = [index for index, (actual, original) in
                               enumerate(zip(selected_math, math))
                               if canonical(actual) != canonical(original)]
                check(differences == [30], "sole raw ID MathML difference is occurrence30", category)
                equation = selected.find(f".//{CN}equation[@id='eip-id1165137567088']")
                localized_math = equation.find(M + "math")
                check(selected_math[30] is localized_math and
                      [node.text for node in localized_math.iter(M + "mtext")] == ["\u00a0ketika\u00a0"],
                      "exact ID owner and localized when text", category)
                normalized = deepcopy(localized_math)
                next(normalized.iter(M + "mtext")).text = "\u00a0when\u00a0"
                selected_math[30] = normalized
            check([canonical(n) for n in selected_math] == [canonical(n) for n in math],
                  "all actual MathML; only explicitly pinned ID ketika->when localized" + language, category)
            if language == "en":
                check(selected_text == data.decode("utf-8"), "exact reproducible English excerpt", category)
                check(canonical(selected) == canonical(excerpt), "full English section content", category)
            for asset in ASSETS:
                medium = selected.find(f".//{CN}media[@id='{asset['media_id']}']")
                check(medium.find(CN + "image").get("src") == "../../media/" + asset["filename"],
                      "same original image reference " + language, category)
                prefix = ("downloads/upstream-openstax/media" if language == "en"
                          else "downloads/a30-edition/source-core/repo/source/media")
                actual = (ROOT.parent / prefix / asset["filename"]).read_bytes()
                check(len(actual) == asset["bytes"] and sha256(actual).hexdigest() == asset["sha256"],
                      "actual pinned original image " + language, category)
        ledger_path = ROOT.parent / "downloads/a30-edition/source-core/00_control/COMPONENT_RIGHTS.csv"
        with ledger_path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        for asset in ASSETS:
            matches = [row for row in rows if row["asset_path"] == "media/" + asset["filename"]]
            check(len(matches) == 1 and matches[0]["admission"] == "admitted"
                  and matches[0]["license_id"] == "CC-BY-NC-SA-4.0"
                  and matches[0]["sha256"] == asset["sha256"]
                  and int(matches[0]["bytes"]) == asset["bytes"],
                  "existing admitted component binding " + asset["filename"], category)
    COUNTS.clear()
    COUNTS.update(counts)
    return sum(counts.values())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--originals", action="store_true")
    total = tests(parser.parse_args().originals)
    print(f"PASS: {total} mixed assertions; breakdown {COUNTS}")
