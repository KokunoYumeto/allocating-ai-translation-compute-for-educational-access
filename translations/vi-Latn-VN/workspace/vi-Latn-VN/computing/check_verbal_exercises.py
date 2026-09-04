"""Committed-source checks and finite witnesses for verbal answers.

These finite checks illustrate definitions; they do not prove whole-curve claims.
The prose supplies the forward and reverse arguments for the two line tests.
"""
from hashlib import sha256
from pathlib import Path
import re
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "http://cnx.rice.edu/cnxml"
EXERCISES = ("fs-id1165137432993", "fs-id1165137870912", "fs-id1165137870922",
             "fs-id1165135570273", "fs-id1165134391600")
SOLUTIONS = ("fs-id1165137667225", "fs-id1165134118515", "fs-id1165137679053")
EXCERPT_SHA = "3ce98e0feb51307709b8edb4fffd1f4decfb9c755648971830fec43786535a94"


def function_on(points, domain=None):
    domain = {x for x, _ in points} if domain is None else set(domain)
    return all(x in domain for x, _ in points) and all(
        len({y for a, y in points if a == x}) == 1 for x in domain)


def horizontal_test(points):
    return all(len({x for x, b in points if b == y}) == 1 for _, y in points)


def injective(points, domain=None):
    return function_on(points, domain) and horizontal_test(points)


def tests():
    checks = 0

    def check(condition, message):
        nonlocal checks
        assert condition, message
        checks += 1

    source = ROOT / "sources/m49301-verbal-exercises-source.cnxml"
    tree = ET.parse(source).getroot()
    markdown = (ROOT / "translation/A30-U009-verbal-exercises.vi.md").read_text(encoding="utf-8")
    check(sha256(source.read_bytes()).hexdigest() == EXCERPT_SHA, "reviewed complete source excerpt")
    check(tree.get("stop-before") == "fs-id1165134080937", "next source category")
    check([n.get("id") for n in tree] == ["fs-id1165137432988"], "complete Verbal category only")
    check(tuple(n.get("id") for n in tree.iter(f"{{{CN}}}exercise")) == EXERCISES, "all five in source order")
    check(tuple(n.get("id") for n in tree.iter(f"{{{CN}}}solution")) == SOLUTIONS, "exact three source solutions")
    check(not list(tree.iter("{http://www.w3.org/1998/Math/MathML}math")), "no source MathML")
    check(not list(tree.iter(f"{{{CN}}}image")), "no source images")
    ids = [n.get("id") for n in tree.iter() if n.get("id")]
    check(len(ids) == 22, "source identity count")
    check(markdown == unicodedata.normalize("NFC", markdown), "Vietnamese NFC")
    for identity in ids:
        check(markdown.count(f"{{#{identity}}}") == 1, f"one explicit source anchor {identity}")
    positions = [markdown.index(f"{{#{identity}}}") for identity in EXERCISES]
    check(positions == sorted(positions), "prompt order preserved")
    check("**ba bài tập mới**" in markdown and "không phải năm bài mới" in markdown,
          "duplicate scope disclosed")
    for target in (*SOLUTIONS, "vi-sol-verbal-2", "vi-sol-verbal-4"):
        check(f"](#{target})" in markdown and f"{{#{target}}}" in markdown, f"answer link {target}")
    check(markdown.count("Nguồn không kèm lời giải cho câu này") == 2, "two newly written solutions labeled")
    sibling_links = re.findall(r"\]\((A30-[^ )]+\.vi\.html#[^ )]+)\)", markdown)
    check(len(sibling_links) == 5, "five supplemental reader links; builder checks target identities")
    for phrase in ("hai cặp phân biệt", "nhiều nhất một", "đúng một", "ngoài tập xác định",
                   "ngoài tập giá trị", "đã là hàm số", "không chỉ một vài điểm lấy mẫu"):
        check(phrase in markdown, f"reviewed boundary wording {phrase}")

    # Finite counterexamples in the actual translated explanations.
    check(not function_on([(7, 11), (7, 9)]), "one input with two outputs")
    check(function_on([(3, 6)]), "input/output example")
    check(function_on([(0, 1), (2, 1)]), "repeated outputs still define function")
    check(not injective([(0, 1), (2, 1)]), "repeated outputs not injective")
    check(not function_on([(2, -1), (2, 1)]), "vertical counterexample")
    check(horizontal_test([(2, -1), (2, 1)]), "horizontal condition alone can pass")
    check(not injective([(2, -1), (2, 1)]), "function prerequisite essential")
    check(injective([(3, 6), (3, 6)]), "duplicate point is not two distinct outputs")
    check(not function_on([(3, 6)], [3, 4]), "separately prescribed domain needs totality")
    check(function_on([(3, 6)], [3]), "exactly one on stated domain")
    check({y for x, y in [(3, 6)] if x == 4} == set(), "zero outside attained domain")
    check({x for x, y in [(3, 6)] if y == 7} == set(), "zero outside range")
    check(injective([(-1, -1), (0, 0), (1, 1)]), "finite injective example")
    return checks


if __name__ == "__main__":
    print(f"PASS: {tests()} source/structure and finite verbal-answer checks")
