"""Check exact source structure and independently evaluate all image-table data.

All 39 sample pairs were transcribed from the nine visually inspected originals.
Finite samples check arithmetic, not entire graph shapes or infinite-domain proofs.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import re
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "http://cnx.rice.edu/cnxml"
MATH = "http://www.w3.org/1998/Math/MathML"
SECTION = "fs-id1165135545919"
STOP = "fs-id1165135203679"
SAMPLES = [
    ("vi-constant", "Constant", [("-2", "2"), ("0", "2"), ("2", "2")]),
    ("vi-identity", "Identity", [("-2", "-2"), ("0", "0"), ("2", "2")]),
    ("vi-absolute-value", "Absolute value", [("-2", "2"), ("0", "0"), ("2", "2")]),
    ("vi-quadratic", "Quadratic", [("-2", "4"), ("-1", "1"), ("0", "0"), ("1", "1"), ("2", "4")]),
    ("vi-cubic", "Cubic", [("-1", "-1"), ("-0.5", "-0.125"), ("0", "0"), ("0.5", "0.125"), ("1", "1")]),
    ("vi-reciprocal", "Reciprocal", [("-2", "-0.5"), ("-1", "-1"), ("-0.5", "-2"), ("0.5", "2"), ("1", "1"), ("2", "0.5")]),
    ("vi-reciprocal-squared", "Reciprocal squared", [("-2", "0.25"), ("-1", "1"), ("-0.5", "4"), ("0.5", "4"), ("1", "1"), ("2", "0.25")]),
    ("vi-square-root", "Square root", [("0", "0"), ("1", "1"), ("4", "2")]),
    ("vi-cube-root", "Cube root", [("-1", "-1"), ("-0.125", "-0.5"), ("0", "0"), ("0.125", "0.5"), ("1", "1")]),
]


def exact_root(value, degree):
    """Exact rational roots for these small perfect-power samples only."""
    if value < 0 and degree % 2 == 0:
        raise ValueError("negative radicand has no real even root")

    def positive_integer_root(number):
        candidate = 0
        while (candidate + 1) ** degree <= number:
            candidate += 1
        if candidate ** degree != number:
            raise ValueError("sample is not a rational perfect power")
        return candidate

    sign = -1 if value < 0 else 1
    return sign * Fraction(positive_integer_root(abs(value.numerator)),
                           positive_integer_root(value.denominator))


def evaluate(node, x, c=Fraction(2)):
    """Evaluate the preserved MathML right-hand side, not a duplicated formula."""
    tag = node.tag.rsplit("}", 1)[-1]
    if tag == "mi":
        return {"x": x, "c": c}[node.text]
    if tag == "mn":
        return Fraction(node.text)
    if tag == "mrow":
        if len(node) == 1:
            return evaluate(node[0], x, c)
        if node[0].text == "|" and node[-1].text == "|":
            return abs(evaluate(node[1], x, c))
    if tag == "msup":
        return evaluate(node[0], x, c) ** int(evaluate(node[1], x, c))
    if tag == "mfrac":
        return evaluate(node[0], x, c) / evaluate(node[1], x, c)
    if tag == "msqrt":
        return exact_root(evaluate(node[0], x, c), 2)
    if tag == "mroot":
        return exact_root(evaluate(node[0], x, c), int(evaluate(node[1], x, c)))
    raise ValueError(f"unsupported source MathML: {tag}")


def tests():
    count = 0

    def check(condition, description):
        nonlocal count
        assert condition, description
        count += 1

    tree = ET.parse(ROOT / "sources/m49301-toolkit-functions-source.cnxml").getroot()
    markdown = (ROOT / "translation/A30-U007-toolkit-functions.vi.md").read_text(encoding="utf-8")
    check(tree.get("id") == SECTION, "correct source section")
    check(markdown == unicodedata.normalize("NFC", markdown), "NFC Vietnamese")
    identities = {n.get("id"): n for n in tree.iter() if n.get("id")}
    check(len(identities) == 16, "all source ID count")
    for identity in identities:
        check(f"{{#{identity}}}" in markdown or f'id="{identity}"' in markdown,
              f"explicit source ID {identity}")
    for tag, expected in (("table", 1), ("media", 9), ("image", 9), ("para", 3),
                          ("note", 1), ("list", 1), ("exercise", 0), ("solution", 0)):
        check(len(list(tree.iter(f"{{{CN}}}{tag}"))) == expected, f"source {tag} count")

    def math_serials(node):
        result = []
        for math in node.iter(f"{{{MATH}}}math"):
            copied = deepcopy(math)
            copied.tail = None
            result.append(ET.tostring(copied))
        return result

    original_math = list(tree.iter(f"{{{MATH}}}math"))
    inserted = []
    for identity, index in re.findall(r"\{\{math:([^:}]+):(\d+)\}\}", markdown):
        inserted.append(list(identities[identity].iter(f"{{{MATH}}}math"))[int(index)])
    check(len(original_math) == len(inserted) == 12, "12 MathML insertions")
    check(Counter(map(id, original_math)) == Counter(map(id, inserted)), "all source math once")
    check(not list(tree.iter(f"{{{MATH}}}mtext")), "no mtext dictionary required")

    for path in (ROOT.parent / "downloads/upstream-openstax/modules/m49301/index.cnxml",
                 ROOT.parent / "downloads/a30-edition/source-core/repo/source/modules/m49301/index.cnxml"):
        content = list(ET.parse(path).getroot().find(f"{{{CN}}}content"))
        index = next(i for i, n in enumerate(content) if n.get("id") == SECTION)
        check(content[index + 1].get("id") == STOP, "next source boundary")
        original = content[index]
        check([n.get("id") for n in original.iter() if n.get("id")] == list(identities),
              "ordered EN/ID source IDs")
        check(math_serials(original) == math_serials(tree), "unchanged EN/ID MathML")
        if "upstream-openstax" in str(path):
            check(ET.tostring(original) == ET.tostring(tree), "complete original excerpt")

    images = [Path(n.get("src")).name for n in tree.iter(f"{{{CN}}}image")]
    check(len(set(images)) == 9, "nine distinct originals")
    for name in images:
        check(f"(../assets/{name})" in markdown, f"untouched original filename {name}")
    for link in tree.iter(f"{{{CN}}}link"):
        if link.get("url"):
            check(f"]({link.get('url')})" in markdown, "optional source media URL retained")
        else:
            check(f"](#{link.get('target-id')})" in markdown, "Table14 source reference")

    rows = tree.findall(f".//{{{CN}}}tbody/{{{CN}}}row")
    check(len(rows) == len(SAMPLES) == 9, "nine named toolkit functions")
    check(sum(len(pairs) for _, _, pairs in SAMPLES) == 39, "39 source image-table pairs")
    formulas = []
    for (identity, name, samples), row in zip(SAMPLES, rows):
        check("".join(row[0].itertext()).strip() == name, "source function name/order")
        math = next(row[1].iter(f"{{{MATH}}}math"))
        rhs = math[0][3]
        formulas.append(rhs)
        # Only the intended row table is parsed, not duplicate image alt data.
        block = markdown.split(f"{{#{identity}}}", 1)[1].split("#### ", 1)[0]
        table_pairs = []
        for line in block.splitlines():
            if not line.startswith("|"):
                continue
            cells = [cell.strip().replace("−", "-") for cell in line.strip("|").split("|")]
            try:
                pair = tuple(Fraction(cell) for cell in cells)
            except ValueError:
                continue
            table_pairs.append(pair)
        expected_pairs = [(Fraction(x), Fraction(y)) for x, y in samples]
        check(table_pairs == expected_pairs, f"complete image-table transcription {identity}")
        for x, y in expected_pairs:
            check(evaluate(rhs, x) == y, f"exact MathML arithmetic {name} at {x}")

    # Explicit domain/range edge cases and distinctions in supplemental text.
    check(evaluate(formulas[0], Fraction(-17), Fraction(7)) == 7,
          "constant c is fixed but not necessarily 2")
    check(evaluate(formulas[1], Fraction(-17)) == -17, "identity is not a constant")
    check(evaluate(formulas[2], Fraction(-2)) == evaluate(formulas[2], Fraction(2)),
          "absolute-value repeated output")
    check(evaluate(formulas[3], Fraction(-2)) == evaluate(formulas[3], Fraction(2)),
          "quadratic repeated output")
    for rhs in formulas[5:7]:
        try:
            evaluate(rhs, Fraction(0))
        except ZeroDivisionError:
            check(True, "reciprocal zero excluded")
        else:
            check(False, "reciprocal zero erroneously accepted")
    for x in (Fraction(-2), Fraction(-1, 2), Fraction(1, 2), Fraction(2)):
        check(evaluate(formulas[6], x) == evaluate(formulas[5], x) ** 2,
              "reciprocal of square equals square of reciprocal")
        check(evaluate(formulas[6], x) > 0, "reciprocal square excludes zero output")
    check(evaluate(formulas[7], Fraction(4)) == 2, "square-root output is nonnegative")
    try:
        evaluate(formulas[7], Fraction(-1))
    except ValueError:
        check(True, "negative square-root input excluded over reals")
    else:
        check(False, "negative square-root input erroneously accepted")
    check(evaluate(formulas[8], Fraction(-1)) == -1, "negative real cube root")
    check(evaluate(formulas[8], Fraction(-1, 8)) == Fraction(-1, 2), "negative fractional cube root")
    check(evaluate(formulas[7], Fraction(0)) == evaluate(formulas[8], Fraction(0)) == 0,
          "zero allowed for both root functions")
    return count


if __name__ == "__main__":
    print(f"PASS: {tests()} toolkit source, table-transcription and exact arithmetic assertions")
