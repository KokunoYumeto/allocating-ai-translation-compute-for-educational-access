"""Source preservation plus finite illustrations of the two geometric tests.

Finite point sets cannot prove a claim about an entire unprovided curve.
No polynomial formula is inferred from the source's cubic-looking drawing.
"""
from collections import Counter
from copy import deepcopy
from math import isclose, sqrt
from pathlib import Path
import re
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "http://cnx.rice.edu/cnxml"
MATH = "http://www.w3.org/1998/Math/MathML"
SECTIONS = ("fs-id1165135435781", "fs-id1165137610952")
STOP = "fs-id1165135545919"


def vertical_test(points):
    """Check a finite relation on its projection onto the x-axis."""
    return all(len({b for a, b in points if a == x}) == 1 for x, _ in points)


def horizontal_test(points):
    """A geometric condition, usable without presupposing a function."""
    return vertical_test([(y, x) for x, y in points])


def injective_function(points):
    return vertical_test(points) and horizontal_test(points)


def tests():
    checks = 0

    def check(condition, message):
        nonlocal checks
        assert condition, message
        checks += 1

    source_path = ROOT / "sources/m49301-graph-tests-source.cnxml"
    tree = ET.parse(source_path).getroot()
    check(tuple(n.get("id") for n in tree) == SECTIONS, "exact two-section scope")
    check(tree.get("stop-before") == STOP, "exact next boundary")
    identities = {n.get("id"): n for n in tree.iter() if n.get("id")}
    markdown = (ROOT / "translation/A30-U006-graph-tests.vi.md").read_text(encoding="utf-8")
    check(markdown == unicodedata.normalize("NFC", markdown), "Vietnamese NFC")
    for identity in identities:
        check(f"{{#{identity}}}" in markdown or f'id="{identity}"' in markdown,
              f"explicit source anchor {identity}")
    check(len(identities) == 51, "source identity count")
    for tag, expected in (("section", 2), ("example", 2), ("exercise", 4),
                          ("problem", 4), ("solution", 4), ("figure", 6), ("table", 0)):
        check(len(list(tree.iter(f"{{{CN}}}{tag}"))) == expected, f"source {tag} count")

    original_math = list(tree.iter(f"{{{MATH}}}math"))
    inserted_math = []
    for identity, index in re.findall(r"\{\{math:([^:}]+):(\d+)\}\}", markdown):
        inserted_math.append(list(identities[identity].iter(f"{{{MATH}}}math"))[int(index)])
    check(len(original_math) == len(inserted_math) == 15, "all 15 source math insertions")
    check(Counter(map(id, original_math)) == Counter(map(id, inserted_math)),
          "each original MathML expression inserted exactly once")
    check(not list(tree.iter(f"{{{MATH}}}mtext")), "no mtext translation dictionary required")
    source_numbers = [n.text for n in identities["fs-id1165137637786"].iter(f"{{{MATH}}}mn")]
    check(source_numbers == ["0", "2", "6", "1.", "0", "2", "6", "1"],
          "Figure11 source numeric statements")

    for path in (ROOT.parent / "downloads/upstream-openstax/modules/m49301/index.cnxml",
                 ROOT.parent / "downloads/a30-edition/source-core/repo/source/modules/m49301/index.cnxml"):
        original = ET.parse(path).getroot()
        content = list(original.find(f"{{{CN}}}content"))
        start = next(i for i, n in enumerate(content) if n.get("id") == SECTIONS[0])
        check(tuple(n.get("id") for n in content[start:start + 3]) == SECTIONS + (STOP,),
              f"source adjacency {path}")
        selected = content[start:start + 2]
        check([n.get("id") for section in selected for n in section.iter() if n.get("id")]
              == list(identities), f"source ordered ID match {path}")

        def math_serials(nodes):
            serials = []
            for section in nodes:
                for node in section.iter(f"{{{MATH}}}math"):
                    copied = deepcopy(node)
                    copied.tail = None
                    serials.append(ET.tostring(copied))
            return serials
        check(math_serials(selected) == math_serials(list(tree)), f"source exact math {path}")
        if "upstream-openstax" in str(path):
            for excerpt_section, original_section in zip(tree, selected):
                check(ET.tostring(excerpt_section) == ET.tostring(original_section),
                      "excerpt equals parsed original including all prose/child order")

    assets = [Path(n.get("src")).name for n in tree.iter(f"{{{CN}}}image")]
    check(len(assets) == len(set(assets)) == 6, "six distinct untouched source images")
    for name in assets:
        check(f"(../assets/{name})" in markdown, f"original filename {name}")
    source_targets = Counter(n.get("target-id") for n in tree.iter(f"{{{CN}}}link"))
    for target, count in source_targets.items():
        check(markdown.count(f"](#{target})") >= count, f"source link target retained {target}")

    # Independent finite arithmetic and relation checks, not whole-curve proofs.
    dots = [(0, 2), (6, 1)]
    check(dict(dots)[0] == 2 and dict(dots)[6] == 1, "source marked-point readings")
    check(injective_function(dots), "two dots alone do not determine the rest of a curve")
    repeated_output = [(-1, 1), (1, 1)]
    check(vertical_test(repeated_output), "repeated outputs permit a function")
    check(not horizontal_test(repeated_output), "repeated outputs fail horizontal test")
    check(not injective_function(repeated_output), "repeated outputs fail injectivity")
    repeated_input = [(2, -1), (2, 1)]
    check(not vertical_test(repeated_input), "two outputs at one input fail vertical test")
    check(horizontal_test(repeated_input), "horizontal test alone does not guarantee a function")
    check(not injective_function(repeated_input), "injective-function predicate requires a function")
    same_point = [(0, 0), (0, 0)]
    check(vertical_test(same_point) and horizontal_test(same_point), "duplicate point is not two values")
    abs_points = [(x, abs(x)) for x in range(-4, 5)]
    check(vertical_test(abs_points), "finite absolute-value graph passes vertical test")
    check(not injective_function(abs_points), "absolute value has repeated outputs")
    check({y for x, y in abs_points if x == 0} == {0}, "V vertex is one point")
    check({y for x, y in dots if x == 3} == set(), "outside the finite domain gives no point")
    check({x for x, y in dots if y == 8} == set(), "outside the finite range gives no point")

    def circle_vertical_count(x):
        radicand = 9 - x * x
        return 0 if radicand < 0 else 1 if radicand == 0 else 2

    check([circle_vertical_count(x) for x in (-4, -3, -2, 0, 2, 3, 4)]
          == [0, 1, 2, 2, 2, 1, 0], "circle interior/endpoints/exterior")
    check(9 - 2 * 2 == 5, "circle x=2 radicand")
    for y in (sqrt(5), -sqrt(5)):
        check(isclose(2 * 2 + y * y, 9), "circle vertical intersection satisfies equation")
    check(sqrt(5) != -sqrt(5), "circle two outputs distinct")
    circle_axis_points = [(0, -3), (0, 3), (-3, 0), (3, 0)]
    check(all(x * x + y * y == 9 for x, y in circle_axis_points), "circle axis points")
    check(not vertical_test(circle_axis_points), "circle fails function condition")
    check(not horizontal_test(circle_axis_points), "circle also fails horizontal condition")
    check(not injective_function(circle_axis_points), "circle is not an injective function")
    check({x for x, y in circle_axis_points if y == 0} == {-3, 3}, "source final answer witness")
    return checks


if __name__ == "__main__":
    print(f"PASS: {tests()} source-preservation and finite graph-test assertions")
