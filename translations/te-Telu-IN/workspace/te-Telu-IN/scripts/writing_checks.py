"""Bounded B005 checks of actual localized XML; not linguistic approval.

Source English names, positional zeros, units, and every side of the sixteen
bridge equation chains are checked independently of the builder/asset code.
"""
import math
import re

from naming_checks import english_name, text_of

CN = "{http://cnx.rice.edu/cnxml}"
MATH = "{http://www.w3.org/1998/Math/MathML}"
SMALL_VALUES = {english_name(n): n for n in range(1000)}
SCALE_VALUES = {"thousand": 1000, "million": 1000000,
                "billion": 1000000000, "trillion": 1000000000000}
NUMBER = r"[0-9][0-9,]*"
EXPRESSION = NUMBER + r"(?:\s*[+×]\s*" + NUMBER + r")*"
EQUALITY = re.compile(r"(?<![\w,])" + EXPRESSION +
                      r"(?:\s*=\s*" + EXPRESSION + r")+")
GROUPS = re.compile(r"(?<![\w|])\d+(?:\s*\|\s*\d+)+")


def english_value(name):
    """Only the source's comma-separated, no-and whole-number grammar."""
    name = " ".join(name.lower().strip().rstrip(".").split())
    total, previous = 0, 1000 ** 5
    for group in name.split(", "):
        last = group.rsplit(" ", 1)[-1]
        scale = SCALE_VALUES.get(last, 1)
        coefficient = group[:-(len(last) + 1)] if scale != 1 else group
        assert coefficient in SMALL_VALUES, "Invalid English coefficient: " + group
        assert scale < previous, "English period order changed: " + name
        total += SMALL_VALUES[coefficient] * scale
        previous = scale
    assert english_name(total) == name, "Noncanonical English number name: " + name
    return total


def verify_writing_equalities(root, expected=16):
    """Check complete chains, including expanded = sum = numeral, not prefixes."""
    chains = []
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] not in {"p", "li", "dd"}:
            continue
        for match in EQUALITY.finditer(text_of(node)):
            chain = match.group()
            values = []
            for side in chain.split("="):
                values.append(sum(math.prod(int(n.strip().replace(",", ""))
                                            for n in term.split("×"))
                                  for term in side.split("+")))
            assert len(set(values)) == 1, "Incorrect bridge equality: " + chain
            chains.append(chain)
    assert len(chains) == expected, "Missing/extra B005 equality chains"
    return len(chains)


def _ids(root):
    nodes = [e for e in root.iter() if e.get("id")]
    result = {e.get("id"): e for e in nodes}
    assert len(result) == len(nodes), "Duplicate B005 ID"
    return result


def _node(ids, ident):
    assert ident in ids, "Missing B005 node: " + ident
    return ids[ident]


def _groups(value):
    return f"{value:,}".split(",")


def _require_groups(node, value):
    actual = [re.split(r"\s*\|\s*", m.group())
              for m in GROUPS.finditer(text_of(node))]
    assert actual and all(g == _groups(value) for g in actual), (
        "Zero-group changed: " + (node.get("id") or "support"))


def _require_numeral_mentions(node, value):
    """Catch a wrong prose answer even when a correct equality remains nearby."""
    contributions = {int(g) * 1000 ** i
                     for i, g in enumerate(reversed(_groups(value)))}
    allowed = {f"{n:,}" for n in contributions | {value, 1000, 1000000,
                                               1000000000}}
    text = text_of(node)
    assert re.search(r"(?<![\d,])" + re.escape(f"{value:,}") + r"(?![\d,])", text), (
        "Missing B005 answer numeral: " + node.get("id", ""))
    stated_pattern = r"జవాబు\s+(\$?[0-9][0-9,]*)"
    if node.get("id") == "B005-S-D02":
        stated_pattern = r"కాబట్టి\s+(\$?[0-9][0-9,]*)"
    for stated in re.findall(stated_pattern, text):
        assert stated.lstrip("$").rstrip(",") == f"{value:,}", (
            "Wrong B005 answer numeral (stated): " + stated)
    for token in re.findall(r"(?<![\w,])[0-9][0-9,]*", text):
        token = token.rstrip(",")
        if "," in token:
            assert token in allowed, "Wrong B005 answer numeral: " + token


def _require_link(node, destination):
    assert any(e.tag.rsplit("}", 1)[-1] == "a" and
               e.get("href") == "#" + destination for e in node.iter()), (
        "Wrong B005 solution link: " + destination)


def _source_name(node, expected):
    text = text_of(node)
    marker = "మూల ఇంగ్లీషు పేరు: "
    assert marker in text, "Missing source English name"
    name = text.split(marker, 1)[1].strip().rstrip(".")
    assert name == expected, "Source English name changed: " + expected
    return english_value(name)


def _math_text(node, tag):
    return [(e.text or "").strip() for e in node.iter(MATH + tag)]


def _source_checks(target):
    ids = _ids(target)
    items = _node(ids, "fs-id2264653").findall(CN + "item")
    assert len(items) == 2, "Source writing examples changed"
    pairs = [
        (items[0], "fifty-three million, four hundred one thousand, seven hundred forty-two", "fs-id1726897"),
        (items[1], "nine billion, two hundred forty-six million, seventy-three thousand, one hundred eighty-nine", "fs-id1374355"),
        (_node(ids, "fs-id2149876"), "fifty-three million, eight hundred nine thousand, fifty-one", "fs-id4163187"),
        (_node(ids, "fs-id1792489"), "two billion, twenty-two million, seven hundred fourteen thousand, four hundred sixty-six", "fs-id1885399"),
    ]
    for question, expected, answer_id in pairs:
        value = _source_name(question, expected)
        answer = _node(ids, answer_id)
        if answer_id in {"fs-id1726897", "fs-id1374355"}:
            assert _math_text(answer, "mn") == [f"{value:,}"], "Source answer changed: " + answer_id
        else:
            assert text_of(answer) == f"{value:,}", "Source answer changed: " + answer_id

    for problem_id, answer_id, coefficient, unit in [
        ("fs-id1800228", "fs-id865214", 34, "మైళ్లు"),
        ("fs-id1586764", "fs-id1395137", 204, "పౌండ్లు"),
    ]:
        problem = _node(ids, problem_id)
        actual = _math_text(problem, "mn")
        assert actual == [str(coefficient)], "Source measurement coefficient changed"
        assert "మిలియన్ " + unit in text_of(problem), "Source measurement unit changed"
        value = int(actual[0]) * SCALE_VALUES["million"]
        assert text_of(_node(ids, answer_id)) == f"{value:,} {unit}", "Source measurement answer/unit changed"

    budget = _node(ids, "fs-id2590590")
    assert _math_text(budget, "mtext") == ["$77"], "Source budget currency/coefficient changed"
    assert all(s in text_of(budget) for s in ["బిలియన్ డాలర్లు", "సుమారు"]), "Source budget units/approximation changed"
    budget_value = int(_math_text(budget, "mtext")[0][1:]) * SCALE_VALUES["billion"]
    budget_answer = _node(ids, "fs-id2319817")
    assert _math_text(budget_answer, "mtext") == [f"${budget_value:,}."], "Source budget answer/currency changed"
    assert "సుమారు" in text_of(budget_answer), "Source budget approximation removed"

    alt = _node(ids, "fs-id2903601").get("alt", "")
    for fragment in ["nine billion", "two hundred forty-six million", "seventy-three thousand", "one hundred eighty-nine", "9,246,073,189"]:
        assert fragment in alt, "Source017 accessible number/name changed"
    assert re.search(r"seventy-three thousand[^.]*?\b073\b", alt), "Source017 must map seventy-three thousand to073"
    assert not re.search(r"\b742\b", alt), "Source017 copied incorrect742 alt"
    for media_id, mapping in [
        ("fs-id2668978", [("fifty-three million", "53"),
                          ("four hundred one thousand", "401"),
                          ("seven hundred forty-two", "742")]),
        ("fs-id2903601", [("nine billion", "9"),
                          ("two hundred forty-six million", "246"),
                          ("seventy-three thousand", "073"),
                          ("one hundred eighty-nine", "189")]),
    ]:
        description = _node(ids, media_id).get("alt", "")
        for name, digits in mapping:
            pattern = re.escape(name) + r"[^.]*?(?<![\d,])" + digits + r"(?![\d,])"
            assert re.search(pattern, description), "Accessible word/digit mapping changed: " + name
    assert "వంద వేల స్థానాన్ని" in text_of(_node(ids, "fs-id2880619")), "Source073 placeholder place changed"
    return ids


def validate_b005(target, bridge):
    """Validate actual ElementTree roots; return sixteen checked equation chains."""
    source_ids = _source_checks(target)
    ids = _ids(bridge)
    cases = {
        "D01": ("six million, twenty-four thousand, nine", None),
        "D02": ("three billion, forty-two million, five thousand, eight hundred", None),
        "D03": ("two billion, five thousand", "$"),
        "D04": ("five million", "పౌండ్లు"),
        "R01": ("eight million, thirty-seven thousand, six", None),
        "R02": ("four billion, fifty-three million, seven thousand, nine hundred", None),
        "R03": ("six billion, seven thousand", "$"),
        "R04": ("eighteen million", "మైళ్లు"),
    }
    question_fragments = {
        "D03": "రెండు బిలియన్ల, ఐదు వేల అమెరికా డాలర్లు",
        "R03": "ఆరు బిలియన్ల, ఏడు వేల అమెరికా డాలర్లు",
        "D04": "5 million pounds", "R04": "18 million miles",
    }
    for case, (name, unit) in cases.items():
        question = _node(ids, "B005-" + case)
        answer = _node(ids, "B005-S-" + case)
        fragment = question_fragments.get(case, name)
        assert fragment in text_of(question), "Practice name/unit changed: " + case
        value = english_value(name)
        _require_groups(answer, value)
        _require_numeral_mentions(answer, value)
        _require_link(answer, "B005-" + case)
        if unit:
            expected = f"${value:,}" if unit == "$" else f"{value:,} {unit}"
            assert expected in text_of(answer), "Practice answer currency/unit changed: " + case

    source_cases = [
        ("fs-id2646708", "fs-id4163187", "B005-worked-first", None),
        ("fs-id2202956", "fs-id1885399", "B005-worked-second", None),
        ("fs-id1485641", "fs-id865214", "B005-worked-third", "మైళ్లు"),
        ("fs-id2133886", "fs-id1395137", "B005-worked-fourth", "పౌండ్లు"),
    ]
    for exercise_id, source_answer, container_id, unit in source_cases:
        answer = _node(ids, "B005-S-" + exercise_id)
        numeric = re.match(NUMBER, text_of(source_ids[source_answer]))
        assert numeric, "Source answer numeral missing"
        value = int(numeric.group().replace(",", ""))
        _require_groups(answer, value)
        _require_numeral_mentions(answer, value)
        _require_link(answer, exercise_id)
        assert EQUALITY.search(text_of(_node(ids, container_id))), "Missing full source arithmetic"
        if unit:
            assert f"{value:,} {unit}" in text_of(answer), "Source bridge answer/unit changed"

    # Check unnumbered support too; incorrect widths cannot hide outside D/R.
    for match in GROUPS.finditer(text_of(bridge)):
        groups = re.split(r"\s*\|\s*", match.group())
        assert 1 <= len(groups[0]) <= 3 and not groups[0].startswith("0"), "Invalid first period"
        assert all(len(g) == 3 for g in groups[1:]), "Zero-group width changed"
    whole = text_of(bridge)
    assert "3 | 000 | 005" in whole, "Missing middle-zero support"
    assert "77 | 000 | 000 | 000" in whole and "$77,000,000,000" in whole, "Budget zero groups/currency changed"
    return verify_writing_equalities(bridge)
