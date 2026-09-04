"""U030 source preservation and exact finite range/domain checks.

Default uses only the committed excerpt/draft and Python's standard library.
Explicit --originals reads the two existing pinned source modules and extractor.
Nothing is fetched, plotted or written. Finite output-level witnesses for57 are
not evaluations of an unknown f and do not assert f(y)=y. General attainment and
domain arguments remain in the draft; these checks are not proofs of fluency.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from math import isqrt
from pathlib import Path
import argparse
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SECTION = "fs-id1165137733672"
STOP = "fs-id1165137832031"
EXCERPT_SHA = "8496a2e4e29d464c95a5b7e7e8f5f6a7f372875d7b7b1744913ece5567dc086d"
EXERCISES = ["fs-id1165137442197", "fs-id1165137679047", "fs-id1165135209378"]
ANSWERS = ["fs-id1165134555582", "fs-id1165133210812"]
NUMERIC = {
    "fs-id1165133221853": ["−5", "8"],
    "fs-id1165134555584": ["0", "8"],
    "fs-id1165137645593": ["2."],
    "fs-id1165137779064": ["1", "2"],
}
ORIGINALS = (
    ("en", "downloads/upstream-openstax/modules/m49304/index.cnxml",
     "0e230c4c96d46e7962dcb3afa1f1630718f7e1cdfae9e665d640690ab6ace19c"),
    ("id", "downloads/a30-edition/source-core/repo/source/modules/m49304/index.cnxml",
     "a341bb8c05830b95c865b18d64b186fc9a88a08640bbb12f030879faa90b7539"),
)
COUNTS = {}


def canonical(node):
    return (node.tag, tuple(sorted(node.attrib.items())), (node.text or "").strip(),
            tuple((canonical(child), (child.tail or "").strip()) for child in node))


def closed_interval(node):
    tokens = "".join("".join(node.itertext()).split()).replace("−", "-")
    tokens = tokens.removesuffix(".")
    if not tokens.startswith("[") or not tokens.endswith("]"):
        raise ValueError("expected a closed source interval")
    endpoints = tokens[1:-1].split(",")
    if len(endpoints) != 2:
        raise ValueError("expected two endpoints")
    low, high = map(F, endpoints)
    if low > high:
        raise ValueError("reversed endpoints")
    return low, high


def absolute_interval(low, high):
    if low > high:
        raise ValueError("reversed input interval")
    if low >= 0:
        return low, high
    if high <= 0:
        return -high, -low
    return F(0), max(-low, high)


class IrrationalExactWitness(ValueError):
    """The expression is defined, but this finite evaluator returns rationals only."""


def rational_sqrt(value):
    value = F(value)
    if value < 0:
        raise ValueError("no real square root")
    numerator, denominator = isqrt(value.numerator), isqrt(value.denominator)
    if numerator * numerator != value.numerator or denominator * denominator != value.denominator:
        raise IrrationalExactWitness("defined irrational root, outside rational witness set")
    return F(numerator, denominator)


def evaluate(node, x):
    """Evaluate this source's actual 1/sqrt(x-2) expression, not a fitted formula."""
    kind = node.tag.rsplit("}", 1)[-1]
    if kind == "mn":
        return F((node.text or "").replace("−", "-"))
    if kind == "mi":
        assert node.text == "x"
        return F(x)
    if kind == "mrow":
        if len(node) == 1:
            return evaluate(node[0], x)
        assert len(node) == 3 and node[1].tag == M + "mo" and node[1].text == "−"
        return evaluate(node[0], x) - evaluate(node[2], x)
    if kind == "msqrt":
        assert len(node) == 1
        return rational_sqrt(evaluate(node[0], x))
    if kind == "mfrac":
        assert len(node) == 2
        return evaluate(node[0], x) / evaluate(node[1], x)
    raise AssertionError("unsupported actual source node: " + kind)


def tests(originals=False):
    counts = {"source_structure": 0, "exact_finite_arithmetic": 0,
              "optional_original_source": 0}

    def check(condition, label, category="source_structure"):
        assert condition, label
        counts[category] += 1

    def finite(condition, label):
        check(condition, label, "exact_finite_arithmetic")

    data = (ROOT / "sources/m49304-domain-extensions-source.cnxml").read_bytes()
    check(sha256(data).hexdigest() == EXCERPT_SHA, "exact owned excerpt")
    root = ET.fromstring(data)
    draft = (ROOT / "translation/A30-U030-domain-extensions.vi.md").read_text(encoding="utf-8")
    flat = " ".join(draft.split())
    check(unicodedata.normalize("NFC", draft) == draft, "Vietnamese NFC")
    ids = [node.get("id") for node in root.iter() if node.get("id")]
    by_id = {node.get("id"): node for node in root.iter() if node.get("id")}
    check(len(ids) == len(set(ids)) == 14, "fourteen unique original IDs")
    anchors = re.findall(r"\{#([^}]+)\}", draft)
    check(len(anchors) == len(set(anchors)), "all translated anchors unique")
    for identity in ids:
        check(anchors.count(identity) == 1, "explicit source anchor " + identity)
    section = root.find(CN + "content/" + CN + "section")
    check(section.get("id") == SECTION and STOP not in ids, "exact Extensions boundary")
    check("fs-id1165135176628" not in ids, "outer exercise wrapper owned by U024")
    check(section[0].tag == CN + "title" and section[0].text.strip() == "Extension",
          "source category title")
    check(len(section) == 4, "title and three whole exercises")
    exercises = list(section.iter(CN + "exercise"))
    check([node.get("id") for node in exercises] == EXERCISES, "exact three exercises")
    check([node.get("id") for node in section.iter(CN + "solution")] == ANSWERS,
          "two source answers")
    for number, exercise in enumerate(exercises, 57):
        check(f"### Bài {number} {{#{exercise.get('id')}}}" in draft,
              "original global exercise number " + str(number))
        check((exercise.find(CN + "solution") is not None) == (number != 58),
              "source answer availability " + str(number))
    for tag in ("image", "figure", "table", "link", "example"):
        check(not list(section.iter(CN + tag)), "no source " + tag)
    check(not re.search(r"!\[", draft), "no unrequested supplemental image")
    check(draft.count("**Đáp án nguồn:") == 2, "two source-answer labels")
    check(draft.count("**Lời giải bổ sung — nguồn không kèm đáp án.**") == 1,
          "one source-absent answer visibly identified")
    check(draft.count("*Giải thích bổ sung:*") == 2, "two expanded-source explanation labels")
    math = list(root.iter(M + "math"))
    refs = re.findall(r"\{\{math:([^:}]+):(\d+)\}\}", draft)
    check(len(math) == len(refs) == 6, "six source MathML captures")
    captured = [list(by_id[owner].iter(M + "math"))[int(index)] for owner, index in refs]
    check(Counter(map(id, captured)) == Counter(map(id, math)), "every source formula captured once")
    check(refs == [("fs-id1165133221853", "0"), ("fs-id1165133221853", "1"),
                   ("fs-id1165133221853", "2"), ("fs-id1165137645593", "0"),
                   ("fs-id1165134555584", "0"), ("fs-id1165137779064", "0")],
          "declared questions-before-answers reflow, with original owners retained")
    check(not list(root.iter(M + "mtext")), "no mtext translation dictionary needed")
    for identity, expected in NUMERIC.items():
        check([node.text for node in by_id[identity].iter(M + "mn")] == expected,
              "source numerical tokens " + identity)
    condition = next(by_id["fs-id1165137645593"].iter(M + "math"))
    check([node.text for node in condition.iter(M + "mi")] == ["x"]
          and [node.text for node in condition.iter(M + "mo")] == [">"]
          and [node.text for node in condition.iter(M + "mn")] == ["2."],
          "strict source x>2 with original mn punctuation unchanged")
    links = re.findall(r"(?<!!)\[[^\]]+\]\(#([^)]+)\)", draft)
    check(links == [ANSWERS[0], "vi-answer-58", ANSWERS[1]], "three answer links")
    for target in links:
        check(anchors.count(target) == 1, "unique answer target " + target)
    check(not re.findall(r"\]\(A30-[^)]+\.html", draft), "no cross-reader dependency")
    check(len(re.findall(r"\]\(https?://[^)]+\)", draft)) == 3,
          "three attribution links retained, not fetched")
    for text in ("789b54099106b071d1d32bfcee454fed72eb4768", "0.1.0-alpha.58-reader.1",
                 "creativecommons.org/licenses/by-nc-sa/4.0/", "Copyright Rice University, OpenStax",
                 "chưa có thẩm định của người bản ngữ", "mọi giá trị trong tập ấy đều thực sự được nhận",
                 "không cần biết công thức của $f$ hoặc giả thiết $f$ liên tục",
                 "không suy ra rằng $f(0)=0$ hay $f(8)=8$",
                 "tập xác định lớn nhất trong các số thực mà công thức này cho phép"):
        check(text in flat, "explicit provenance/mathematical qualification: " + text)
    for expression in (r"$$f(x)=x^2,\qquad x\in\mathbb{R}.$$",
                       r"$$f(\sqrt{y})=(\sqrt{y})^2=y.$$",
                       r"$x-2\ge0$", r"$\sqrt{x-2}\ne0$",
                       r"$$x>2,\qquad X=(2,\infty).$$"):
        check(expression in draft, "supplemental mathematical statement " + expression)

    source_range = closed_interval(list(by_id["fs-id1165133221853"].iter(M + "math"))[1])
    source_answer = closed_interval(next(by_id["fs-id1165134555584"].iter(M + "math")))
    finite(source_range == (F(-5), F(8)), "actual source range")
    finite(source_answer == absolute_interval(*source_range) == (F(0), F(8)),
           "actual source absolute-value answer")
    for output in (F(-5), F(-1), F(0), F(1, 3), F(5), F(8)):
        finite(source_range[0] <= output <= source_range[1]
               and source_answer[0] <= abs(output) <= source_answer[1],
               "57 output-level absolute-value witness " + str(output))
    for wanted in (F(0), F(1, 3), F(5), F(8)):
        finite(source_range[0] <= wanted <= source_range[1] and abs(wanted) == wanted,
               "57 unchanged nonnegative output witness, not f(y)=y: " + str(wanted))
    for low, high, expected in ((-8, 5, (0, 8)), (-8, -5, (5, 8)), (5, 8, (5, 8))):
        finite(absolute_interval(F(low), F(high)) == tuple(map(F, expected)),
               "absolute-interval routine sign case")
    for x, y in ((F(-3), F(9)), (F(-1, 2), F(1, 4)), (F(0), F(0)),
                 (F(1, 2), F(1, 4)), (F(3), F(9))):
        finite(x*x == y and y >= 0, "58 newly authored square-function witness " + str(x))
    for y in (F(0), F(1, 4), F(1), F(9), F(49, 9)):
        x = rational_sqrt(y)
        finite(x*x == y and x >= 0, "58 finite converse witness " + str(y))

    source_formula = next(by_id["fs-id1165137779064"].iter(M + "math"))
    fraction = next(source_formula.iter(M + "mfrac"))
    square_root = next(fraction.iter(M + "msqrt"))
    radicand = square_root[0]
    finite(len(list(source_formula.iter(M + "mfrac"))) == 1
           and len(list(source_formula.iter(M + "msqrt"))) == 1,
           "source denominator is one square root")
    # Only this pinned source prompt stores its sentence period inside mn'2.'.
    # Interpret that known token as boundary2 without changing any source XML.
    boundary = F(next(condition.iter(M + "mn")).text.removesuffix("."))
    finite(boundary == F(2), "source strict-domain boundary")
    for x in (F(-1), F(0), F(1), F(2), F(201, 100), F(9, 4), F(3), F(4), F(6)):
        real_and_nonzero_denominator = evaluate(radicand, x) > 0
        finite(real_and_nonzero_denominator == (x > boundary),
               "59 necessary and sufficient radicand sign at " + str(x))
    for x, expected in ((F(9, 4), F(2)), (F(3), F(1)), (F(6), F(1, 2)), (F(11), F(1, 3))):
        finite(evaluate(fraction, x) == expected, "59 exact source-function evaluation " + str(x))
    try:
        evaluate(fraction, F(2))
    except ZeroDivisionError:
        rejected_zero = True
    else:
        rejected_zero = False
    finite(rejected_zero, "59 endpoint2 excluded by zero denominator")
    try:
        evaluate(fraction, F(1))
    except ValueError:
        rejected_negative = True
    else:
        rejected_negative = False
    finite(rejected_negative, "59 x1 excluded by negative real radicand")
    try:
        evaluate(fraction, F(4))
    except IrrationalExactWitness:
        defined_irrational = evaluate(radicand, F(4)) > 0
    else:
        defined_irrational = False
    finite(defined_irrational, "59 defined irrational output is not a domain exclusion")

    if originals:
        originals_by_language = {}
        for language, relative, digest in ORIGINALS:
            path = ROOT.parent / relative
            check(sha256(path.read_bytes()).hexdigest() == digest,
                  "pinned full source " + language, "optional_original_source")
            originals_by_language[language] = path
        spec = spec_from_file_location("u030_extractor", ROOT / "tools/extract_domain_extensions.py")
        extractor = module_from_spec(spec)
        spec.loader.exec_module(extractor)
        check(extractor.extract(originals_by_language["en"]).encode("utf-8") == data,
              "complete EN extraction and exact previous/next/global-number boundary", "optional_original_source")
        id_excerpt = ET.fromstring(extractor.extract(originals_by_language["id"]))
        check([node.get("id") for node in id_excerpt.iter() if node.get("id")] == ids,
              "complete ID scope,14IDs and global numbers57–59", "optional_original_source")
        check([canonical(node) for node in id_excerpt.iter(M + "math")] ==
              [canonical(node) for node in math], "all six EN/ID MathML identical", "optional_original_source")
        check([node.get("id") for node in id_excerpt.iter(CN + "solution")] == ANSWERS,
              "two identical source answer identities", "optional_original_source")
        check(not list(id_excerpt.iter(CN + "image")) and not list(id_excerpt.iter(CN + "table")),
              "no omitted Indonesian source images/tables", "optional_original_source")

    COUNTS.clear()
    COUNTS.update(counts)
    return sum(counts.values())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--originals", action="store_true")
    total = tests(parser.parse_args().originals)
    print(f"PASS: {total} mixed assertions; breakdown {COUNTS}")
    print("Finite witnesses do not replace the draft's all-values arguments or native review.")
