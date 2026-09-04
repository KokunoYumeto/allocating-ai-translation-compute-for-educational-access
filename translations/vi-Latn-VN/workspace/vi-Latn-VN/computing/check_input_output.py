"""U004 source-preservation and exact arithmetic checks; not native review.

Polynomial coefficient identities are exact. Finite sample evaluations are
regression checks, not proofs of claims over an infinite domain.
"""
from collections import Counter
from decimal import Decimal
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import re
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SECTION = "fs-id1165137503241"
STOP = "fs-id1165135422920"
TABLE = [(1, 8), (2, 6), (3, 7), (4, 6), (5, 8)]
PETS = [
    ("Puppy", "Chó con", "0.008"),
    ("Adult dog", "Chó trưởng thành", "0.083"),
    ("Cat", "Mèo", "16"),
    ("Goldfish", "Cá vàng", "2160"),
    ("Beta fish", "Cá betta", "3600"),
]
ASSETS = {
    "CNX_Precalc_Figure_01_01_006-5f6f.jpg": "af834802492b337155a0056c0d70961f3a003e41df6e571c082ae227241d2675",
    "CNX_Precalc_Figure_01_01_007-985e.jpg": "02cde0483837d9e0327b2d969c153dc4e05bb19f2edcab5ceff627bdab00013d",
    "CNX_Precalc_Figure_01_01_008.jpg": "bbf8ad74f4c6abe5882a3bf246a4834a3aa1d72e638b4199a40d51941a95efa3",
    "CNX_Precalc_Figure_01_01_009-4a94.jpg": "cf77d80db8d2616f63ef758adbccd016eac20df35a3e1699c2d4da131820736b",
}


def tests():
    tree = ET.parse(ROOT / "sources/m49301-input-output-source.cnxml")
    source = tree.find(f".//{CN}section[@id='{SECTION}']")
    by_id = {node.get("id"): node for node in source.iter() if node.get("id")}
    markdown = (ROOT / "translation/A30-U004-input-output.vi.md").read_text(encoding="utf-8")
    count = 0

    def check(condition, message):
        nonlocal count
        assert condition, message
        count += 1

    def block(identity):
        result = re.search(r"^::: \{#" + re.escape(identity) + r"\}\n(.*?)^:::$",
                           markdown, re.MULTILINE | re.DOTALL)
        assert result, identity
        return result.group(1)

    check(markdown == unicodedata.normalize("NFC", markdown), "Vietnamese NFC")
    check(len(by_id) == 139, "source identity inventory")
    for tag, expected in (("section", 5), ("example", 7), ("problem", 12),
                          ("solution", 12), ("table", 3), ("figure", 4),
                          ("equation", 13), ("note", 9), ("footnote", 1)):
        check(len(list(source.iter(CN + tag))) == expected, f"source {tag} count")
    all_math = list(source.iter(M + "math"))
    check(len(all_math) == 121, "source MathML count")
    used_math = []
    for identity, index in re.findall(r"\{\{math:([^:}]+):(\d+)\}\}", markdown):
        check(identity in by_id, f"unknown math owner {identity}")
        candidates = list(by_id[identity].iter(M + "math"))
        check(int(index) < len(candidates), f"invalid MathML index {identity}:{index}")
        used_math.append(candidates[int(index)])
    check(Counter(map(id, used_math)) == Counter(map(id, all_math)),
          "every original MathML occurrence must occur exactly once in draft")

    for identity in (SECTION, "fs-id1165137425943", "fs-id1165137591827",
                     "fs-id1165137648450", "fs-id1165135696152",
                     "ti_01_01_08", "ti_01_01_09", "fs-id1165137698725",
                     "ti_01_01_06", "ti_01_01_05"):
        check("{#" + identity + "}" in markdown, f"explicit boundary/practice {identity}")
    for node in source.iter(CN + "link"):
        target = node.get("target-id")
        check(f"](#{target})" in markdown, f"translated crossreference {target}")

    for identity in ("Table_01_01_11", "Table_01_01_12"):
        rows = [["".join(cell.itertext()).strip() for cell in row.findall(CN + "entry")]
                for row in by_id[identity].findall(f"{CN}tgroup/{CN}tbody/{CN}row")]
        source_pairs = list(zip(*(list(map(int, row[1:])) for row in rows)))
        translated_pairs = [tuple(map(int, row)) for row in re.findall(
            r"^\|\s*(\d+)\s*\|\s*(\d+)\s*\|$", block(identity), re.MULTILINE)]
        check(source_pairs == TABLE, f"source data {identity}")
        check(translated_pairs == TABLE, f"translated data {identity}")
    pet_rows = [["".join(cell.itertext()).strip() for cell in row.findall(CN + "entry")]
                for row in by_id["Table_01_01_10"].findall(f"{CN}tgroup/{CN}tbody/{CN}row")]
    check(pet_rows == [[en, number] for en, vi, number in PETS], "source pet values")
    for en, vi, number in PETS:
        check(f"| {vi} | {number} |" in block("Table_01_01_10"), f"translated pet {en}")
    check(Decimal(30) / Decimal(3600) == Decimal(1) / Decimal(120), "30-second conversion")
    check(round(Decimal(30) / Decimal(3600), 3) == Decimal("0.008"), "puppy rounding")
    check(round(Decimal(5) / Decimal(60), 3) == Decimal("0.083"), "dog rounding")
    check(3 * 30 * 24 == 2160 and 5 * 30 * 24 == 3600, "stated 30-day-month convention")
    check("chưa kiểm chứng độc lập" in markdown, "illustrative biology disclaimer")

    f = lambda x: x * x + 3 * x - 4
    h = lambda p: p * p + 2 * p
    check(f(2) == 6, "Example 6 numeric answer")
    # Coefficients indexed by (power of a, power of h): exact distributive expansion.
    expanded = {(2, 0): 1, (1, 1): 2, (0, 2): 1,
                (1, 0): 3, (0, 1): 3, (0, 0): -4}
    original = {(2, 0): 1, (1, 0): 3, (0, 0): -4}
    difference = {power: coefficient - original.get(power, 0)
                  for power, coefficient in expanded.items()
                  if coefficient - original.get(power, 0)}
    factored = {(1, 1): 2, (0, 2): 1, (0, 1): 3}
    check(difference == factored, "difference quotient numerator polynomial identity")
    quotient = {(a, b - 1): coefficient for (a, b), coefficient in factored.items()}
    check(quotient == {(1, 0): 2, (0, 1): 1, (0, 0): 3}, "quotient after nonzero-h cancellation")
    check("$h\\ne 0$" in markdown, "difference quotient domain condition")
    check(h(4) == 24, "Example 7")
    check(5 - 4 == 1 ** 2, "Try It 4")
    check(h(1) == h(-3) == 3, "Example 8 roots")
    check(8 - 4 == 2 ** 2 and 8 >= 4, "Try It 5 verified root")
    for n in (-3, 0, 1, 6, Fraction(1, 2)):
        p = 2 - Fraction(1, 3) * n
        check(2 * n + 6 * p == 12, f"Example 9 sample n={n}")
    check(0 ** 2 + 1 ** 2 == 1 and 0 ** 2 + (-1) ** 2 == 1, "circle two-output witness")
    check(1 ** 2 + 0 ** 2 == (-1) ** 2 + 0 ** 2 == 1, "circle endpoints")
    for cube_root in (-4, -1, 0, 1, 4):
        x, y = cube_root ** 3, Fraction(cube_root, 2)
        check(x - 8 * y ** 3 == 0, f"Try It 6 sample root={cube_root}")
    g = dict(TABLE)
    check(g[3] == 7 and g[1] == 8, "Example 11 / Try It 7 values")
    check([n for n, output in TABLE if output == 6] == [2, 4], "Example 11 all inputs")
    for p, expected in ((-3, 3), (-2, 0), (0, 0), (1, 3), (4, 24)):
        check(h(p) == expected, f"Figure 6 embedded table p={p}")
    graph = lambda x: (x - 1) ** 2
    for x, expected in ((2, 1), (-1, 4), (3, 4), (0, 1), (1, 0)):
        check(graph(x) == expected, f"Figures 7-9 / Try It 8 point {x}")

    for filename, digest in ASSETS.items():
        check(f"../assets/{filename}" in markdown, f"figure filename {filename}")
        source_asset = ROOT.parent / "downloads/upstream-openstax/media" / filename
        if source_asset.exists():
            check(sha256(source_asset.read_bytes()).hexdigest() == digest, f"source image hash {filename}")
    # When the pinned original is present, ensure the excerpt did not alter source
    # element names, attributes, text, or child order. Namespace declarations are
    # resolved by XML parsing; source formatting whitespace is retained.
    original_path = ROOT.parent / "downloads/upstream-openstax/modules/m49301/index.cnxml"
    if original_path.exists():
        original_tree = ET.parse(original_path)
        original_section = original_tree.find(f".//{CN}section[@id='{SECTION}']")
        check(ET.tostring(source).rstrip() == ET.tostring(original_section).rstrip(),
              "excerpt XML differs from pinned source section")
        parent = next(node for node in original_tree.iter() if original_section in list(node))
        siblings = list(parent)
        check(siblings[siblings.index(original_section) + 1].get("id") == STOP, "next sibling boundary")
    return count


if __name__ == "__main__":
    print(f"PASS: {tests()} source-preservation/arithmetic assertions")
