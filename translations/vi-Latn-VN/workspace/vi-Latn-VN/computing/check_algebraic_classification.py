"""U010 preservation, answer-label and finite algebraic checks.

Finite substitutions check the displayed examples/counterexamples; they are not
proofs of uniqueness on infinite domains. The draft gives the algebraic reasons.
All tests use the standard library and do not alter sources or readers.
"""
from collections import Counter
from fractions import Fraction as F
from importlib.util import module_from_spec, spec_from_file_location
from math import isclose, sqrt
from pathlib import Path
import re
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
NON_FUNCTIONS = {6, 10, 12, 16, 18, 24, 25}
SUPPLIED = set(range(7, 26, 2))
FLAT_FORMULAS = (
    "{(a,b),(c,d),(a,c)}", "{(a,b),(b,c),(c,c)}", "5x+2y=10",
    "y=x2", "x=y2", "3x2+y=14", "2x+y2=6", "y=−2x2+40x",
    "y=1x", "x=3y+57y−1", "x=1−y2", "y=3x+57x−1",
    "x2+y2=9", "2xy=1", "x=y3", "y=x3", "y=1−x2",
    "x=±1−y", "y=±1−x", "y2=x2", "y3=x2",
)
SHAPES = {
    9: {"msup": 1}, 10: {"msup": 1}, 11: {"msup": 1},
    12: {"msup": 1}, 13: {"msup": 1}, 14: {"mfrac": 1},
    15: {"mfrac": 1}, 16: {"msqrt": 1, "msup": 1},
    17: {"mfrac": 1}, 18: {"msup": 2}, 20: {"msup": 1},
    21: {"msup": 1}, 22: {"msqrt": 1, "msup": 1},
    23: {"msqrt": 1}, 24: {"msqrt": 1},
    25: {"msup": 2}, 26: {"msup": 2},
}


def canonical(node):
    """Compare XML content/attributes while disregarding layout whitespace."""
    return (node.tag, tuple(sorted(node.attrib.items())), (node.text or "").strip(),
            tuple((canonical(child), (child.tail or "").strip()) for child in node))


def relation(number, x, y):
    """Real relation transcriptions, bound below to source tokens and shapes."""
    if number == 8:
        return 5 * x + 2 * y == 10
    if number == 9:
        return y == x ** 2
    if number == 10:
        return x == y ** 2
    if number == 11:
        return 3 * x ** 2 + y == 14
    if number == 12:
        return 2 * x + y ** 2 == 6
    if number == 13:
        return y == -2 * x ** 2 + 40 * x
    if number == 14:
        return x != 0 and y == 1 / x
    if number == 15:
        return 7 * y - 1 != 0 and x == (3 * y + 5) / (7 * y - 1)
    if number == 16:
        return 1 - y ** 2 >= 0 and isclose(x, sqrt(1 - y ** 2), abs_tol=1e-12)
    if number == 17:
        return 7 * x - 1 != 0 and y == (3 * x + 5) / (7 * x - 1)
    if number == 18:
        return x ** 2 + y ** 2 == 9
    if number == 19:
        return 2 * x * y == 1
    if number == 20:
        return x == y ** 3
    if number == 21:
        return y == x ** 3
    if number == 22:
        return 1 - x ** 2 >= 0 and isclose(y, sqrt(1 - x ** 2), abs_tol=1e-12)
    if number == 23:
        return 1 - y >= 0 and isclose(abs(x), sqrt(1 - y), abs_tol=1e-12)
    if number == 24:
        return 1 - x >= 0 and isclose(abs(y), sqrt(1 - x), abs_tol=1e-12)
    if number == 25:
        return y ** 2 == x ** 2
    if number == 26:
        return isclose(y ** 3, x ** 2, abs_tol=1e-12)
    raise ValueError(number)


def is_function(pairs):
    return all(len({output for first, output in pairs if first == value}) == 1
               for value in {first for first, output in pairs})


def tests():
    count = 0

    def check(condition, message):
        nonlocal count
        assert condition, message
        count += 1

    spec = spec_from_file_location("u010_extractor", ROOT / "tools/extract_algebraic_classification.py")
    extractor = module_from_spec(spec)
    spec.loader.exec_module(extractor)
    excerpt_path = ROOT / "sources/m49301-algebraic-classification-source.cnxml"
    excerpt_text = excerpt_path.read_text(encoding="utf-8")
    source = ET.fromstring(excerpt_text)
    markdown = (ROOT / "translation/A30-U010-algebraic-classification.vi.md").read_text(encoding="utf-8")
    section = source.find(f".//{CN}section")
    exercises = list(source.iter(CN + "exercise"))
    by_id = {node.get("id"): node for node in source.iter() if node.get("id")}
    source_ids = [node.get("id") for node in source.iter() if node.get("id")]
    check(markdown == unicodedata.normalize("NFC", markdown), "Vietnamese NFC")
    check(len(source_ids) == len(set(source_ids)) == 86, "86 distinct source IDs")
    check(len(exercises) == 21, "21 exercise prompts")
    check([node.get("id") for node in exercises] == list(extractor.EXERCISE_IDS), "exact source order")
    check([node.get("id") for node in section if node.tag == CN + "para"] ==
          [extractor.START_PROMPT, extractor.SECOND_PROMPT], "two complete shared instructions")
    check(len(list(source.iter(CN + "solution"))) == 10, "ten supplied answers")
    check(not list(source.iter(CN + "example")), "no source examples")
    check(not list(source.iter(CN + "image")), "no source images")
    check(not list(source.iter(CN + "table")), "no source tables")
    check(extractor.STOP not in by_id, "next shared prompt excluded")
    explicit_ids = re.findall(r"\{#([^}]+)\}", markdown)
    for identity in source_ids:
        check(explicit_ids.count(identity) == 1, f"one explicit source anchor {identity}")
    check(len(explicit_ids) == len(set(explicit_ids)), "no duplicate translation anchors")
    local_targets = re.findall(r"\]\(#([^)]+)\)", markdown)
    check(len(local_targets) == 42, "21 answer and 21 return links")
    check(all(target in explicit_ids for target in local_targets), "all local link targets explicit")

    maths = list(source.iter(M + "math"))
    check(len(maths) == 23, "23 original MathML expressions")
    inserted = []
    for identity, index in re.findall(r"\{\{math:([^:}]+):(\d+)\}\}", markdown):
        candidates = list(by_id[identity].iter(M + "math"))
        check(int(index) < len(candidates), f"valid source math index {identity}:{index}")
        inserted.append(candidates[int(index)])
    check(Counter(map(id, maths)) == Counter(map(id, inserted)), "every source math inserted exactly once")
    check(not list(source.iter(M + "mtext")), "no MathML prose replacement needed")
    for number, (exercise, flat) in enumerate(zip(exercises, FLAT_FORMULAS), 6):
        formula = exercise.find(f"{CN}problem/{CN}para/{M}math")
        check("".join("".join(formula.itertext()).split()) == flat, f"source tokens for exercise {number}")
        actual_shape = {tag: len(list(formula.iter(M + tag))) for tag in ("mfrac", "msqrt", "msup", "mroot")
                        if list(formula.iter(M + tag))}
        check(actual_shape == SHAPES.get(number, {}), f"fractions/radicals/powers for exercise {number}")
        check(f"### Bài {number} {{#{exercise.get('id')}}}" in markdown, f"visible source number {number}")
        solution = exercise.find(CN + "solution")
        check((solution is not None) == (number in SUPPLIED), f"source-answer availability {number}")
        answer_id = solution.get("id") if solution is not None else f"vi-sol-{number}"
        match = re.search(rf"### Bài {number} — Lời giải \{{#{answer_id}\}}\n(.*?)(?=\n### |\n## )", markdown, re.S)
        check(match is not None, f"answer block {number}")
        block = match.group(1)
        if solution is not None:
            source_answer = " ".join("".join(solution.itertext()).split())
            check(source_answer == ("not a function" if number in NON_FUNCTIONS else "function"),
                  f"source answer agrees with reviewed classification {number}")
            expected = "Không phải là hàm số." if number in NON_FUNCTIONS else "Là hàm số."
            check(f"**Đáp án nguồn:** {expected}" in block, f"translated source answer {number}")
            check("*Lời giải bổ sung:*" in block, f"expanded reasoning separated {number}")
        else:
            check("**Đáp án và lời giải bổ sung — nguồn không kèm lời giải:**" in block,
                  f"authored answer explicitly labeled {number}")
            check("**Đáp án nguồn:**" not in block, f"no invented source answer {number}")
            expected = "**Không phải là hàm số" if number in NON_FUNCTIONS else "**Là hàm số"
            check(expected in block, f"authored classification {number}")
    check(len(NON_FUNCTIONS) == 7 and 21 - len(NON_FUNCTIONS) == 14, "classification totals")

    original_paths = (
        ROOT.parent / "downloads/upstream-openstax/modules/m49301/index.cnxml",
        ROOT.parent / "downloads/a30-edition/source-core/repo/source/modules/m49301/index.cnxml",
    )
    # Downloaded corpora are ignored by Git; keep the tracked excerpt usable
    # elsewhere while checking both pinned originals whenever they are present.
    for language, path in zip(("en", "id"), original_paths):
        if not path.is_file():
            continue
        original = ET.parse(path)
        parent = original.find(f".//{CN}section[@id='{extractor.PARENT}']")
        selected = []
        for node in parent:
            if node.get("id") == extractor.STOP:
                break
            selected.append(node)
        check(list(parent)[len(selected)].get("id") == extractor.STOP, f"exact next boundary {language}")
        check([node.get("id") for node in selected if node.tag == CN + "exercise"] ==
              list(extractor.EXERCISE_IDS), f"original exercise order {language}")
        selected_ids = [parent.get("id")] + [node.get("id") for item in selected for node in item.iter() if node.get("id")]
        check(selected_ids == source_ids, f"all original selected IDs {language}")
        original_math = [node for item in selected for node in item.iter(M + "math")]
        check([canonical(node) for node in original_math] == [canonical(node) for node in maths],
              f"all original MathML unchanged {language}")
        if language == "en":
            check([canonical(node) for node in selected] == [canonical(node) for node in section],
                  "all English content attributes and source answers preserved")
            check(extractor.extract(path) == excerpt_text, "reproducible exact excerpt")
        else:
            translated_source_answers = [" ".join("".join(node.itertext()).split())
                                         for item in selected for node in item.iter(CN + "solution")]
            check(translated_source_answers == ["fungsi"] * 9 + ["bukan fungsi"],
                  "Indonesian answers agree")

    # Finite checks verify the draft's examples, not universal uniqueness claims.
    check(not is_function([("a", "b"), ("c", "d"), ("a", "c")]), "exercise6 distinct-label counterexample")
    check(is_function([("a", "b"), ("b", "c"), ("c", "c")]), "exercise7 repeated outputs allowed")
    counterexamples = {10: (1, -1, 1), 12: (1, -2, 2), 16: (0, -1, 1),
                       18: (0, -3, 3), 24: (0, -1, 1), 25: (1, -1, 1)}
    for number, (x, first, second) in counterexamples.items():
        check(first != second and relation(number, x, first) and relation(number, x, second),
              f"two distinct outputs for one input in exercise {number}")
    formulas = {8: lambda x: 5 - F(5, 2) * x, 9: lambda x: x ** 2,
                11: lambda x: 14 - 3 * x ** 2, 13: lambda x: -2 * x ** 2 + 40 * x,
                14: lambda x: 1 / x, 15: lambda x: (x + 5) / (7 * x - 3),
                17: lambda x: (3 * x + 5) / (7 * x - 1), 19: lambda x: 1 / (2 * x),
                21: lambda x: x ** 3, 23: lambda x: 1 - x ** 2}
    for number, formula in formulas.items():
        inputs = [F(-3), F(-1), F(0), F(1), F(2)]
        if number in (14, 19):
            inputs.remove(F(0))
        check(all(relation(number, x, formula(x)) for x in inputs),
              f"finite exact substitutions in exercise {number}")
    for number, pairs in {
        16: [(F(0), F(1)), (F(1), F(0)), (F(3, 5), F(4, 5))],
        20: [(F(-8), F(-2)), (F(0), F(0)), (F(27), F(3))],
        22: [(F(-1), F(0)), (F(0), F(1)), (F(3, 5), F(4, 5)), (F(1), F(0))],
        26: [(F(-8), F(4)), (F(-1), F(1)), (F(0), F(0)), (F(8), F(4))],
    }.items():
        check(all(relation(number, x, y) for x, y in pairs), f"root examples in exercise {number}")
    check(not relation(14, F(0), F(0)), "exercise14 denominator exclusion")
    check(F(3, 7) + 5 == F(38, 7), "exercise15 excluded input contradiction")
    check(7 * F(1, 7) - 1 == 0, "exercise15 original denominator restriction")
    check(all(7 * ((x + 5) / (7 * x - 3)) - 1 == 38 / (7 * x - 3)
              for x in map(F, (-3, -1, 0, 1, 2))), "exercise15 transformed denominator identity samples")
    check(not relation(16, F(-1), F(0)), "exercise16 squaring cannot add negative input")
    check(not relation(17, F(1, 7), F(0)), "exercise17 denominator exclusion")
    check(not relation(19, F(0), F(1)), "exercise19 zero input has no solution")
    check(not relation(22, F(0), F(-1)), "exercise22 principal root excludes negative branch")
    check(not relation(22, F(2), F(0)), "exercise22 radicand domain restriction")
    check(not relation(24, F(2), F(0)), "exercise24 radicand domain restriction")
    check(not relation(26, F(-1), F(-1)), "exercise26 no negative cube-root branch")
    return count


if __name__ == "__main__":
    print(f"PASS: {tests()} source/structure/answer-label and finite algebraic assertions")
