"""Standalone U014 source/table/exact arithmetic/rounding checks, Python stdlib.

Default requires only committed excerpt and draft. --originals also checks full
pinned EN/ID and verifies that exactly the three U001-owned exercises were omitted.
Decimal rounding is checked with rational half-unit intervals, not float equality.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "http://cnx.rice.edu/cnxml"
M = "http://www.w3.org/1998/Math/MathML"
EXCERPT_SHA = "cc1634730077b3b445ffbe05e6b56da4f257106110f3d57d233372b93ac7d620"
OMIT = ("fs-id1165133324915", "fs-id1165135245507", "fs-id1165135381342")
EXERCISES = [
    "fs-id1165137644802", "fs-id1165137771740", "fs-id1165137758640",
    "fs-id1165135541988", "fs-id1165137453742", "fs-id1165135581074",
    "fs-id1165137812524", "fs-id1165135445749", "fs-id1165137937596",
    "fs-id1165134573828", "fs-id1165133248574", "fs-id1165135575197",
    "fs-id1165134086037",
]
SOLUTIONS = [
    "fs-id1165137771736", None, "fs-id1165135641696", None,
    "fs-id1165137832462", None, "fs-id1165135192892", None,
    "fs-id1165137755505", None, "fs-id1165137770304", None,
    "fs-id1165134373506",
]
TABLES = {
    "fs-id1165137644806": [(5, 3), (10, 8), (15, 14)],
    "fs-id1165137771744": [(5, 3), (10, 8), (15, 8)],
    "fs-id1165137758645": [(5, 3), (10, 8), (10, 14)],
    "fs-id1165137727218": list(enumerate([74, 28, 1, 53, 56, 3, 36, 45, 14, 47])),
}


def notation(node):
    tag = node.tag.rsplit("}", 1)[-1]
    if tag in ("mi", "mn", "mo"):
        return (node.text or "").strip()
    if tag in ("mtext", "mspace"):
        return ""
    if tag == "msqrt":
        return "sqrt(" + "".join(map(notation, node)) + ")"
    if tag == "msup":
        return f"({notation(node[0])})^({notation(node[1])})"
    if tag == "mfrac":
        return f"({notation(node[0])})/({notation(node[1])})"
    if tag not in ("math", "mrow", "mtable", "mtr", "mtd"):
        raise ValueError(f"Unexpected MathML tag: {tag}")
    return "".join(map(notation, node))


def is_function(pairs):
    outputs = defaultdict(set)
    for x, y in pairs:
        outputs[x].add(y)
    return all(len(values) == 1 for values in outputs.values())


def tests(originals=False, details=False):
    counts = Counter()

    def check(condition, description, kind="structure"):
        assert condition, description
        counts[kind] += 1

    source = ROOT / "sources/m49301-numeric-exercises-source.cnxml"
    data = source.read_bytes()
    tree = ET.fromstring(data)
    md = (ROOT / "translation/A30-U014-numeric-exercises.vi.md").read_text("utf-8")
    check(sha256(data).hexdigest() == EXCERPT_SHA, "pinned selected excerpt bytes")
    check(tree.get("id") == "fs-id1165135342204", "Numeric parent retained")
    check(tree[0].tag == f"{{{CN}}}title" and tree[0].text == "Numeric", "source title retained")
    check(tree[1].get("id") == "fs-id1165133324912", "U001 shared instruction retained")
    check(md == unicodedata.normalize("NFC", md), "NFC Vietnamese")
    ids = {n.get("id"): n for n in tree.iter() if n.get("id")}
    check(len(ids) == 61, "61 retained source IDs")
    explicit = re.findall(r"\{#([^}\s]+)(?:\s[^}]*)?\}", md)
    for identity in ids:
        check(explicit.count(identity) == 1, f"one explicit source ID {identity}")
    for identity in OMIT:
        check(identity not in ids and identity not in explicit, "U001 exercise not duplicated")
        check(f"](A30-U001-functions.vi.html#{identity})" in md, "U001 direct reader reference")
    for tag, expected in (("exercise", 13), ("problem", 13), ("solution", 7),
                          ("para", 22), ("table", 4), ("list", 1), ("image", 0), ("link", 1)):
        check(len(list(tree.iter(f"{{{CN}}}{tag}"))) == expected, f"source {tag} count")
    check([n.get("id") for n in tree.findall(f"{{{CN}}}exercise")] == EXERCISES, "13 exercise order63-75")
    for number, identity, solution in zip(range(63, 76), EXERCISES, SOLUTIONS):
        check(f"#### Bài {number} {{#{identity}}}" in md, "source-wide exercise numbering")
        actual = ids[identity].find(f"{{{CN}}}solution")
        check((actual.get("id") if actual is not None else None) == solution, "source/new solution inventory")
        if solution:
            check(f"{{#{solution}}}" in md, "source solution ID retained")
        else:
            check(f"### Bài {number} — Lời giải bổ sung" in md, "new solution label")
    check(md.count("Nguồn không kèm lời giải cho") == 6, "six new-solution disclosures")
    for target in re.findall(r"\]\(#([^)]+)\)", md):
        check(target in explicit, f"valid local answer/table link {target}")
    shared_link = next(ids["fs-id1165135641701"].iter(f"{{{CN}}}link"))
    check(shared_link.get("target-id") == "fs-id1165137727218", "original shared-table target")
    check("[bảng dưới đây](#fs-id1165137727218)" in md, "translated shared-table reference")

    source_math = list(tree.iter(f"{{{M}}}math"))
    inserted = []
    for identity, index in re.findall(r"\{\{math:([^:}]+):(\d+)\}\}", md):
        inserted.append(list(ids[identity].iter(f"{{{M}}}math"))[int(index)])
    check(len(source_math) == len(inserted) == 31, "31 source math occurrences")
    check(Counter(map(id, source_math)) == Counter(map(id, inserted)), "every source math once")
    check([n.text for n in tree.iter(f"{{{M}}}mtext")] == ["\u2003\u2003"],
          "only mtext is two original em spaces; no translation dictionary needed")
    for identity, expected in TABLES.items():
        rows = ids[identity].findall(f".//{{{CN}}}tbody/{{{CN}}}row")
        values = [[int("".join(entry.itertext()).strip()) for entry in list(row)[1:]] for row in rows]
        pairs = list(zip(*values))
        check(pairs == expected, f"exact original table pairs {identity}", "table")
        block = md.split(f"{{#{identity}}}", 1)[1].split(":::", 1)[0]
        translated = []
        for line in block.splitlines():
            if not line.startswith("|"):
                continue
            cells = [x.strip() for x in line.strip("|").split("|")]
            try:
                translated.append(tuple(int(x) for x in cells))
            except ValueError:
                pass
        check(translated == expected, f"exact transposed Vietnamese pairs {identity}", "table")
        for original_pair, translated_pair in zip(pairs, translated):
            check(original_pair == translated_pair, "source pair retained", "table")
    check(sum(map(len, TABLES.values())) == 19, "19 table pairs", "table")

    signatures = {
        "fs-id1165134437212": "f(x)=4−2x",
        "fs-id1165137812528": "f(x)=8−3x",
        "fs-id1165135445753": "f(x)=8(x)^(2)−7x+3",
        "fs-id1165135181213": "f(x)=3+sqrt(x+3)",
        "fs-id1165134573832": "f(x)=(x−2)/(x+3)",
        "fs-id1165133248578": "f(x)=(3)^(x)",
        "fs-id1165137832464": "f(x)=1,x=2",
        "fs-id1165135192893": "f(−2)=14;f(−1)=11;f(0)=8;f(1)=5;f(2)=2",
        "fs-id1165137755506": "f(−2)=4;f(−1)=4.414;f(0)=4.732;f(1)=5;f(2)=5.236",
        "fs-id1165137770305": "f(−2)=(1)/(9);f(−1)=(1)/(3);f(0)=1;f(1)=3;f(2)=9",
        "fs-id1165135575201": "3f(1)−4g(−2)",
        "fs-id1165134086040": "f((7)/(3))−h(−2)",
    }
    for identity, expected in signatures.items():
        check(notation(next(ids[identity].iter(f"{{{M}}}math"))) == expected,
              f"independent source formula/answer transcription {identity}")
    check([notation(n) for n in ids["eip-582"].iter(f"{{{M}}}math")] ==
          ["f(x)=3x−2", "g(x)=5−(x)^(2)", "h(x)=−2(x)^(2)+3x−1"], "shared three formulas")
    for identity, expected in (("fs-id1165137771737", "function"),
                                ("fs-id1165135641697", "not a function"),
                                ("fs-id1165134373507", "20")):
        check(ids[identity].text.strip() == expected, "source plain-text answer")

    # Exact finite checks of complete finite source tables and requested inputs.
    for pairs, expected in zip(list(TABLES.values())[:3], (True, True, False)):
        check(is_function(pairs) == expected, "finite source table function classification", "arithmetic")
    table = dict(TABLES["fs-id1165137727218"])
    check(table[3] == 53, "f(3)=53", "arithmetic")
    check([x for x, y in table.items() if y == 1] == [2], "all table solutions f(x)=1", "arithmetic")
    check(table[5] == 3 and table[3] != 3, "input/output distinction", "arithmetic")
    sample_inputs = [-2, -1, 0, 1, 2]
    cases = [
        (68, lambda x: 4 - 2*x, [8, 6, 4, 2, 0]),
        (69, lambda x: 8 - 3*x, [14, 11, 8, 5, 2]),
        (70, lambda x: 8*x*x - 7*x + 3, [49, 18, 3, 4, 21]),
        (72, lambda x: (x-2)/(x+3), [Q(-4), Q(-3, 2), Q(-2, 3), Q(-1, 4), Q(0)]),
        (73, lambda x: Q(3)**int(x), [Q(1, 9), Q(1, 3), Q(1), Q(3), Q(9)]),
    ]
    for number, function, expected in cases:
        for value, answer in zip(sample_inputs, expected):
            check(function(Q(value)) == answer, f"exercise{number} exact input{value}", "arithmetic")
        # Read actual displayed answer cells, not just the independent oracle.
        block = md.split(f"### Bài {number} —", 1)[1].split("### ", 1)[0]
        displayed = []
        for line in block.splitlines():
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            try:
                input_value = int(cells[0].replace("−", "-"))
            except ValueError:
                continue
            answer_text = cells[-1].replace("$", "").replace("−", "-")
            fraction = re.fullmatch(r"(-?)\\dfrac(\d)(\d)", answer_text)
            if fraction:
                answer_value = Q(int(fraction[2]), int(fraction[3]))
                if fraction[1]:
                    answer_value = -answer_value
            else:
                answer_value = Q(answer_text)
            displayed.append((input_value, answer_value))
        check(displayed == list(zip(sample_inputs, expected)),
              f"all displayed answer cells exercise{number}", "answer_table")
    check(3 + 1 == 4 and 1**2 == -2 + 3, "root input-2 exact", "arithmetic")
    check(3 + 2 == 5 and 2**2 == 1 + 3, "root input1 exact", "arithmetic")
    for input_value, radicand, decimal in ((-1, 2, "4.414"), (0, 3, "4.732"), (2, 5, "5.236")):
        rounded = Q(decimal)
        lower, upper = rounded - 3 - Q(1, 2000), rounded - 3 + Q(1, 2000)
        check(input_value + 3 == radicand, "exact radical expression", "rounding")
        check(lower > 0 and lower**2 < radicand < upper**2,
              f"{decimal} correct nearest three decimal places", "rounding")
        check((rounded-3)**2 != radicand, f"source equality {decimal} is not exact", "rounding")
    root_block = md.split("### Bài 71 —", 1)[1].split("### ", 1)[0]
    root_rows = []
    for line in root_block.splitlines():
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if cells[0].replace("−", "-").lstrip("-").isdigit():
                root_rows.append(cells)
    check(root_rows == [
        ["−2", r"$3+\sqrt1=4$", "4 chính xác"],
        ["−1", r"$3+\sqrt2$", r"$\approx4.414$"],
        ["0", r"$3+\sqrt3$", r"$\approx4.732$"],
        ["1", r"$3+\sqrt4=5$", "5 chính xác"],
        ["2", r"$3+\sqrt5$", r"$\approx5.236$"],
    ], "all displayed exact and approximate root answer cells", "answer_table")
    check(all(x >= -3 for x in sample_inputs), "all root inputs in real domain", "domain")
    check(all(x != -3 for x in sample_inputs), "all rational inputs in domain", "domain")
    try:
        Q(-3-2) / Q(-3+3)
    except ZeroDivisionError:
        check(True, "rational excluded value-3", "domain")
    else:
        check(False, "invalid rational denominator accepted", "domain")
    f = lambda x: 3*x-2
    g = lambda x: 5-x*x
    h = lambda x: -2*x*x+3*x-1
    for actual, expected, label in (
        (f(Q(1)), 1, "f(1)"), (g(Q(-2)), 1, "g(-2)"),
        (3*f(Q(1))-4*g(Q(-2)), -1, "exercise74"),
        (f(Q(7, 3)), 5, "f(7/3)"), (h(Q(-2)), -15, "h(-2)"),
        (f(Q(7, 3))-h(Q(-2)), 20, "exercise75"),
    ):
        check(actual == expected, label, "arithmetic")

    # Prevent loss of the error notice, exact corrections or added answer values.
    bad_source_position = md.index("{{math:fs-id1165137755506:0}}")
    check(md.index("**Lưu ý về sai sót nguồn:**") < bad_source_position,
          "warning precedes preserved inaccurate source equalities")
    for text in (
        "không phải để khẳng định ba đẳng thức sai ấy",
        r"$3+\sqrt2$", r"$3+\sqrt3$", r"$3+\sqrt5$",
        r"$\approx4.414$", r"$\approx4.732$", r"$\approx5.236$",
        r"$[-3,+\infty)$", r"$\mathbb{R}\setminus\{-3\}$",
        "$f(3)=53$", "$x=2$", "=3(1)-4(1)=-1", "=5-(-15)=20",
        "| −2 | $4-2(-2)=4+4$ | 8 |",
        "| −2 | $8(-2)^2-7(-2)+3=32+14+3$ | 49 |",
        "| −1 | $8(-1)^2-7(-1)+3=8+7+3$ | 18 |",
        "| 2 | $8(2)^2-7(2)+3=32-14+3$ | 21 |",
        r"$-\dfrac32$", r"$-\dfrac23$", r"$-\dfrac14$",
        "Không tự nội suy",
    ):
        check(text in md, f"authored correction/answer retained: {text}")

    if originals:
        sys.path.insert(0, str(ROOT / "tools"))
        from extract_numeric_exercises import ORIGINALS, selected, math_serials
        for relative, digest in ORIGINALS:
            path = ROOT.parent / relative
            check(sha256(path.read_bytes()).hexdigest() == digest, "pinned full source", "original")
            original = selected(path)
            check([n.get("id") for n in original.iter() if n.get("id")] == list(ids),
                  "EN/ID ordered retained IDs", "original")
            check(math_serials(original) == math_serials(tree), "all EN/ID source MathML", "original")
            if "upstream-openstax" in relative:
                check(ET.tostring(original) == ET.tostring(tree), "exact selected EN subtree", "original")
    return dict(counts) if details else sum(counts.values())


if __name__ == "__main__":
    result = tests(originals="--originals" in sys.argv, details=True)
    print(f"PASS: {sum(result.values())} assertions; {result}")
