#!/usr/bin/env python3
"""Read-only QA for the original m81244 U012-U013 recovery companion."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET


BASE = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = BASE / "translation/recovery-addition-phrases-applications.xhtml"
H = "http://www.w3.org/1999/xhtml"
M = "http://www.w3.org/1998/Math/MathML"
NS = {"h": H, "m": M}
H_TAG = f"{{{H}}}"
M_TAG = f"{{{M}}}"

PHRASE_ITEMS = {
    "D1": [[26, "+", 18, "=", 44], [41, "+", 9, "=", 50]],
    "P1": [[37, "+", 28, "=", 65], [54, "+", 16, "=", 70]],
    "M1": [[48, "+", 35, "=", 83], [67, "+", 12, "=", 79]],
    "T1": [[29, "+", 46, "=", 75], [62, "+", 18, "=", 80]],
}
APPLICATION_ITEMS = {
    "D2": ([148, 76], [148, "+", 76, "=", 224], "224 புத்தகங்கள்"),
    "P2": ([24, 18, 27], [24, "+", 18, "+", 27, "=", 69], "69 கிலோமீட்டர்"),
    "M2": ([128, 95, 77], [128, "+", 95, "+", 77, "=", 300], "300 புத்தகங்கள்"),
    "T2": ([186, 139], [186, "+", 139, "=", 325], "325 குறிப்பேடுகள்"),
}
APPLICATION_MATHS = {
    "D2": [
        [148, "+", 76],
        [8, "+", 6, "=", 14],
        [1, "+", 4, "+", 7, "=", 12],
        [1, "+", 1, "+", 0, "=", 2],
        [148, "+", 76, "=", 224],
    ],
    "P2": [
        [24, "+", 18, "+", 27],
        [4, "+", 8, "+", 7, "=", 19],
        [1, "+", 2, "+", 1, "+", 2, "=", 6],
        [24, "+", 18, "+", 27, "=", 69],
    ],
    "M2": [
        [128, "+", 95, "+", 77],
        [8, "+", 5, "+", 7, "=", 20],
        [2, "+", 2, "+", 9, "+", 7, "=", 20],
        [2, "+", 1, "+", 0, "+", 0, "=", 3],
        [128, "+", 95, "+", 77, "=", 300],
    ],
    "T2": [
        [186, "+", 139],
        [6, "+", 9, "=", 15],
        [1, "+", 8, "+", 3, "=", 12],
        [1, "+", 1, "+", 1, "=", 3],
        [186, "+", 139, "=", 325],
    ],
}
APPLICATION_FINAL_SENTENCES = {
    "D2": "அந்தத் தட்டில் மொத்தம் 224 புத்தகங்கள் உள்ளன.",
    "P2": "மூன்று நாட்களில் அவர் மொத்தம் 69 கிலோமீட்டர் சென்றார்.",
    "M2": "வாசிப்பு அறையில் மொத்தம் 300 புத்தகங்கள் உள்ளன.",
    "T2": "இரண்டு பெட்டிகளிலும் மொத்தம் 325 குறிப்பேடுகள் உள்ளன.",
}
PERIMETER_ITEMS = {
    "D3": ([8, 5], [8, "+", 5, "+", 8, "+", 5, "=", 26], "26 மீட்டர்"),
    "P3": ([4, 7, 3, 6, 2, 5], [4, "+", 7, "+", 3, "+", 6, "+", 2, "+", 5, "=", 27], "27 சென்டிமீட்டர்"),
    "M3": ([15, 9], [15, "+", 9, "+", 15, "+", 9, "=", 48], "48 சென்டிமீட்டர்"),
    "T3": ([5, 8, 3, 4, 2, 7], [5, "+", 8, "+", 3, "+", 4, "+", 2, "+", 7, "=", 29], "29 மீட்டர்"),
}
R1_TABLE = [
    ([4, "+", 7], [4, "+", 7, "=", 11]),
    ([12, "+", 9], [12, "+", 9, "=", 21]),
    ([15, "+", 8], [15, "+", 8, "=", 23]),
    ([21, "+", 6], [21, "+", 6, "=", 27]),
    ([11, "+", 14], [11, "+", 14, "=", 25]),
    ([32, "+", 5], [32, "+", 5, "=", 37]),
]


def text_content(element: ET.Element) -> str:
    return " ".join("".join(element.itertext()).split())


def math_parts(math: ET.Element) -> list[int | str]:
    out: list[int | str] = []
    for element in math.iter():
        tag = element.tag.rsplit("}", 1)[-1]
        if tag == "mn":
            value = (element.text or "").strip()
            assert re.fullmatch(r"[0-9]+(?:,[0-9]{3})*", value), value
            out.append(int(value.replace(",", "")))
        elif tag == "mo":
            value = (element.text or "").strip()
            assert value in {"+", "=", "−", "×", "□"}, value
            out.append(value)
    return out


def maths(element: ET.Element) -> list[ET.Element]:
    return element.findall(".//m:math", NS)


def evaluate(tokens: list[int | str]) -> int:
    assert tokens and isinstance(tokens[0], int) and len(tokens) % 2 == 1, tokens
    value = tokens[0]
    for operator, operand in zip(tokens[1::2], tokens[2::2]):
        assert isinstance(operand, int), tokens
        if operator == "+":
            value += operand
        elif operator == "−":
            value -= operand
        elif operator == "×":
            value *= operand
        else:
            raise AssertionError(tokens)
    return value


def arithmetic_check(root: ET.Element) -> tuple[int, int, int]:
    equations = expressions = unknowns = 0
    for math in maths(root):
        tokens = math_parts(math)
        if "□" in tokens:
            assert tokens == [47, "+", "□", "=", 82]
            unknowns += 1
            continue
        if "=" in tokens:
            assert tokens.count("=") == 1, tokens
            at = tokens.index("=")
            assert evaluate(tokens[:at]) == evaluate(tokens[at + 1 :]), tokens
            equations += 1
        else:
            assert "□" not in tokens
            evaluate(tokens)
            expressions += 1
    return equations, expressions, unknowns


def get_by_id(root: ET.Element) -> dict[str, ET.Element]:
    return {e.get("id"): e for e in root.iter() if e.get("id")}


def question_numbers(item: ET.Element) -> list[int]:
    question = item.find("h:p", NS)
    assert question is not None
    return [int(x) for x in re.findall(r"(?<![A-Za-z0-9])([0-9]+)(?![A-Za-z0-9])", text_content(question))]


def require_equation(answer: ET.Element, expected: list[int | str]) -> None:
    actual = [math_parts(m) for m in maths(answer)]
    assert expected in actual, (answer.get("id"), expected, actual)


def replace_text(element: ET.Element, old: str, new: str) -> None:
    changed = False
    for node in element.iter():
        if node.text and old in node.text:
            node.text = node.text.replace(old, new)
            changed = True
        if node.tail and old in node.tail:
            node.tail = node.tail.replace(old, new)
            changed = True
    assert changed, old


def primary_content_check(root: ET.Element) -> dict[str, object]:
    by_id = get_by_id(root)
    checked: list[dict[str, object]] = []
    whole_text = text_content(root)

    assert "D/P/M/T குறியீடுள்ள கேள்விகளும் R1–R3-இன் மாதிரிக் கணக்குகளும் இந்தத் துணைப்பகுதிக்காகப் புதிதாக எழுதப்பட்டவை" in whole_text
    assert "மூல U012" in whole_text

    for code, equations in PHRASE_ITEMS.items():
        item = by_id[f"ta-add-pa-{code}"]
        answer = by_id[f"ta-add-pa-{code}-answer"]
        expected_numbers = [n for equation in equations for n in (equation[0], equation[2])]
        assert question_numbers(item) == expected_numbers, (code, question_numbers(item), expected_numbers)
        for equation in equations:
            require_equation(answer, equation)
        assert all("−" not in math_parts(m) for m in maths(answer))
        reason = text_content(answer.find("h:p[@class='reason']", NS))
        assert "சேரும் அளவு" in reason or "கூட்டப்படும் எண்கள்" in reason or "தொடக்க அளவு" in reason
        checked.append({"item": code, "equations": equations})

    for code, (inputs, equation, unit_answer) in APPLICATION_ITEMS.items():
        item = by_id[f"ta-add-pa-{code}"]
        answer = by_id[f"ta-add-pa-{code}-answer"]
        assert question_numbers(item) == inputs, (code, question_numbers(item), inputs)
        require_equation(answer, equation)
        assert [math_parts(m) for m in maths(answer)] == APPLICATION_MATHS[code]
        reason = text_content(answer.find("h:p[@class='reason']", NS))
        assert "காண வேண்டியது" in reason and "சொற்றொடர்" in reason
        assert ("கோவை" in reason or "கணிதக் குறியீடு" in reason) and unit_answer in reason
        assert APPLICATION_FINAL_SENTENCES[code] in reason
        assert len(reason) > 300
        checked.append({"item": code, "inputs": inputs, "equation": equation, "unit_answer": unit_answer})

    for code, (prompt_sides, equation, unit_answer) in PERIMETER_ITEMS.items():
        item = by_id[f"ta-add-pa-{code}"]
        answer = by_id[f"ta-add-pa-{code}-answer"]
        assert question_numbers(item) == prompt_sides, (code, question_numbers(item), prompt_sides)
        require_equation(answer, equation)
        reason = text_content(answer.find("h:p[@class='reason']", NS))
        feedback = text_content(answer.find("h:p[@class='feedback']", NS))
        assert "சுற்றளவு" in reason and unit_answer in reason
        assert "சதுர" in feedback or "பரப்பளவு" in reason or "பக்கத்தை" in feedback
        checked.append({"item": code, "prompt_sides": prompt_sides, "equation": equation, "unit_answer": unit_answer})

    r1 = by_id["ta-add-pa-R1"]
    rows = r1.findall("h:table/h:tbody/h:tr", NS)
    assert len(rows) == len(R1_TABLE)
    for row, expected in zip(rows, R1_TABLE):
        actual = [math_parts(m) for m in maths(row)]
        assert actual == list(expected), (actual, expected)

    optional = text_content(r1)
    assert "விருப்பச் சரிபார்ப்பு" in optional
    assert "விடுபட்ட சேரும் அளவுச் சரிபார்ப்பு" in optional
    assert "U012 மூலமொழிபெயர்ப்பின் பகுதி அல்ல" in optional
    assert "D/P/M/T வழியின் கட்டாயப் பகுதியாகவும் இல்லை" in optional
    assert "U012-இன் முதன்மை வழி சொற்றொடரிலிருந்து கூட்டல் கோவையையும் அதன் மதிப்பையும் எழுதுவதாகவே உள்ளது" in optional
    r1_maths = [math_parts(m) for m in maths(r1)]
    assert [7, "+", 8] in r1_maths and [4, "+", 6] in r1_maths
    assert "இந்த இரண்டு சொற்றொடர்களும் மூலமொழிபெயர்ப்பிலிருந்து சுட்டப்பட்டவை" in optional
    for equation in ([3, "+", 30, "+", 2, "=", 35], [47, "+", 35, "=", 82], [82, "−", 47, "=", 35]):
        require_equation(r1, equation)
    assert "47-இலிருந்து 50 வரை 3; 50-இலிருந்து 80 வரை 30; 80-இலிருந்து 82 வரை 2" in optional
    assert [math_parts(m) for m in maths(root) if "−" in math_parts(m)] == [[82, "−", 47, "=", 35]]
    r2 = by_id["ta-add-pa-R2"]
    require_equation(r2, [135, "+", 86, "=", 221])
    r2_text = text_content(r2)
    assert "1 ஒன்றை எழுதிச் 1 பத்தை எடுத்துச் செல்கிறோம்" in r2_text
    assert "2 பத்துகளை எழுதிச் 1 நூறை எடுத்துச் செல்கிறோம்" in r2_text
    assert "221 குறிப்பேடுகள்" in r2_text
    r3 = by_id["ta-add-pa-R3"]
    require_equation(r3, [11, "+", 4, "+", 11, "+", 4])
    require_equation(r3, [22, "+", 8, "=", 30])
    r3_text = text_content(r3)
    assert "சுற்றளவு என்பது" in r3_text and "பரப்பளவு என்பது" in r3_text
    assert "30 சென்டிமீட்டர்" in r3_text
    assert "அதிகரிக்க வேண்டிய அளவு" not in whole_text
    return {"checked_items": checked, "r1_table_rows": len(rows), "count_up_scope": "optional"}


def structure_check(root: ET.Element) -> dict[str, int]:
    assert root.tag == H_TAG + "div"
    assert root.get("id") == "ta-add-pa-companion"
    assert root.get("data-strand") == "original-companion"
    assert root.get("lang") == "ta-Taml-IN"
    assert root.get("{http://www.w3.org/XML/1998/namespace}lang") == "ta-Taml-IN"
    allowed = {"div", "section", "h2", "h3", "p", "a", "nav", "ul", "li", "table", "caption", "thead", "tbody", "tr", "th", "td", "math", "mrow", "mn", "mo"}
    for element in root.iter():
        assert element.tag.startswith((H_TAG, M_TAG)), element.tag
        assert element.tag.rsplit("}", 1)[-1] in allowed, element.tag
        for attr, value in element.attrib.items():
            name = attr.rsplit("}", 1)[-1].lower()
            assert not name.startswith("on") and name not in {"src", "href"} or (name == "href" and value.startswith("#")), (attr, value)

    ids = [e.get("id") for e in root.iter() if e.get("id")]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("ta-add-pa-") for i in ids)
    by_id = get_by_id(root)
    links = root.findall(".//h:a", NS)
    assert all(a.get("href", "").startswith("#") and a.get("href")[1:] in by_id for a in links)
    sections = root.findall("h:section", NS)
    assert len(sections) == 13

    items = root.findall(".//h:div[@data-kind]", NS)
    answers = root.findall(".//h:div[@data-answer-for]", NS)
    assert Counter(i.get("data-kind") for i in items) == {"diagnostic": 3, "practice": 3, "mastery": 3, "retry": 3}
    assert len(answers) == 12
    assert {a.get("data-answer-for") for a in answers} == {i.get("id") for i in items}
    for item in items:
        code = item.get("id").rsplit("-", 1)[-1]
        assert item.get("data-remediation") == f"ta-add-pa-R{code[-1]}"
        visible_answer_links = [a.get("href") for a in item.findall(".//h:a", NS)]
        assert visible_answer_links == [f"#ta-add-pa-{code}-answer"], (code, visible_answer_links)
    for answer in answers:
        code = answer.get("data-answer-for").rsplit("-", 1)[-1]
        reason = answer.find("h:p[@class='reason']", NS)
        feedback = answer.find("h:p[@class='feedback']", NS)
        assert reason is not None and feedback is not None
        assert len(text_content(reason)) > 120 and len(text_content(feedback)) > 80
        route = f"#ta-add-pa-R{code[-1]}"
        assert feedback.find(f"h:a[@href='{route}']", NS) is not None
        if code.startswith("P"):
            assert feedback.find(f"h:a[@href='#ta-add-pa-{code}']", NS) is not None
        if code.startswith("M"):
            assert feedback.find(f"h:a[@href='#ta-add-pa-T{code[-1]}']", NS) is not None
        if code.startswith("T"):
            assert feedback.find(f"h:a[@href='#ta-add-pa-{code}']", NS) is not None

    for index in range(1, 4):
        lesson = by_id[f"ta-add-pa-R{index}"]
        for target in (f"#ta-add-pa-P{index}", f"#ta-add-pa-T{index}"):
            assert lesson.find(f".//h:a[@href='{target}']", NS) is not None

    required_gate_links = {
        "ta-add-pa-diagnostic-gate": {"#ta-add-pa-practice"},
        "ta-add-pa-practice-gate": {"#ta-add-pa-practice", "#ta-add-pa-mastery"},
        "ta-add-pa-mastery-gate": {"#ta-add-pa-finish", "#ta-add-pa-mastery"},
        "ta-add-pa-retry-gate": {"#ta-add-pa-retry", "#ta-add-pa-mastery", "#ta-add-pa-mastery-gate"},
    }
    for gate_id, expected in required_gate_links.items():
        gate = by_id[gate_id]
        section = next(s for s in sections if gate in list(s))
        actual = {a.get("href") for a in section.findall(".//h:a", NS)}
        assert expected <= actual, (gate_id, expected, actual)

    tables = root.findall(".//h:table", NS)
    assert len(tables) == 3
    for table in tables:
        assert table.find("h:caption", NS) is not None
        headers = table.findall("h:thead/h:tr/h:th[@scope='col']", NS)
        assert headers
        width = len(headers)
        for row in table.findall("h:tbody/h:tr", NS):
            assert len(row) == width
    for table in tables[1:]:
        assert all(row[0].tag == H_TAG + "th" and row[0].get("scope") == "row" for row in table.findall("h:tbody/h:tr", NS))

    return {"sections": len(sections), "ids": len(ids), "links": len(links), "items": len(items), "answers": len(answers), "tables": len(tables)}


def check_all(root: ET.Element) -> dict[str, object]:
    structure = structure_check(root)
    content = primary_content_check(root)
    equations, expressions, unknowns = arithmetic_check(root)
    return {**structure, **content, "mathml": equations + expressions + unknowns, "equations": equations, "expressions": expressions, "unknowns": unknowns}


def expect_reject(root: ET.Element, mutate) -> None:
    clone = copy.deepcopy(root)
    mutate(clone)
    try:
        check_all(clone)
    except AssertionError:
        return
    raise AssertionError("negative fixture was accepted")


def negative_fixtures(root: ET.Element) -> int:
    by_id = get_by_id(root)

    def reverse_more_than(clone: ET.Element) -> None:
        answer = get_by_id(clone)["ta-add-pa-D1-answer"]
        target = next(m for m in maths(answer) if math_parts(m) == [41, "+", 9, "=", 50])
        numbers = target.findall(".//m:mn", NS)
        numbers[0].text, numbers[1].text = numbers[1].text, numbers[0].text

    def remove_application_field(clone: ET.Element) -> None:
        replace_text(get_by_id(clone)["ta-add-pa-P2-answer"], "காண வேண்டியது", "தேவை")

    def true_but_wrong_perimeter(clone: ET.Element) -> None:
        answer = get_by_id(clone)["ta-add-pa-M3-answer"]
        target = next(m for m in maths(answer) if math_parts(m) == [15, "+", 9, "+", 15, "+", 9, "=", 48])
        numbers = target.findall(".//m:mn", NS)
        numbers[2].text = "14"
        numbers[3].text = "10"

    def relabel_count_up_as_source(clone: ET.Element) -> None:
        replace_text(get_by_id(clone)["ta-add-pa-R1"], "U012 மூலமொழிபெயர்ப்பின் பகுதி அல்ல", "U012 மூலமொழிபெயர்ப்பின் பகுதி")

    def wrong_route(clone: ET.Element) -> None:
        get_by_id(clone)["ta-add-pa-M2"].set("data-remediation", "ta-add-pa-R3")

    def wrong_visible_answer_link(clone: ET.Element) -> None:
        link = get_by_id(clone)["ta-add-pa-D1"].find(".//h:a", NS)
        assert link is not None
        link.set("href", "#ta-add-pa-D2-answer")

    def unrelated_true_carry_row(clone: ET.Element) -> None:
        answer = get_by_id(clone)["ta-add-pa-D2-answer"]
        target = next(m for m in maths(answer) if math_parts(m) == [8, "+", 6, "=", 14])
        numbers = target.findall(".//m:mn", NS)
        numbers[0].text = "9"
        numbers[1].text = "5"

    def wrong_count_up_prose(clone: ET.Element) -> None:
        replace_text(get_by_id(clone)["ta-add-pa-R1"], "47-இலிருந்து 50 வரை 3", "47-இலிருந்து 51 வரை 3")

    def negate_final_sentence(clone: ET.Element) -> None:
        replace_text(get_by_id(clone)["ta-add-pa-D2-answer"], "அந்தத் தட்டில் மொத்தம் 224 புத்தகங்கள் உள்ளன.", "அந்தத் தட்டில் மொத்தம் 224 புத்தகங்கள் இல்லை.")

    def subtraction_outside_optional_check(clone: ET.Element) -> None:
        answer = get_by_id(clone)["ta-add-pa-D1-answer"]
        target = next(m for m in maths(answer) if math_parts(m) == [41, "+", 9])
        numbers = target.findall(".//m:mn", NS)
        operator = target.find(".//m:mo", NS)
        assert operator is not None
        numbers[0].text = "50"
        operator.text = "−"

    for mutation in (
        reverse_more_than,
        remove_application_field,
        true_but_wrong_perimeter,
        relabel_count_up_as_source,
        wrong_route,
        wrong_visible_answer_link,
        unrelated_true_carry_row,
        wrong_count_up_prose,
        negate_final_sentence,
        subtraction_outside_optional_check,
    ):
        expect_reject(root, mutation)
    return 10


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--check", action="store_true", help="accepted for consistency; validation is always read-only")
    args = parser.parse_args()
    path = args.input.resolve()
    raw = path.read_bytes()
    decoded = raw.decode("utf-8")
    assert decoded.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    assert unicodedata.normalize("NFC", decoded) == decoded
    root = ET.fromstring(raw)
    result = check_all(root)
    result["negative_fixtures_rejected"] = negative_fixtures(root)
    result["status"] = "PASS"
    result["path"] = str(path)
    result["bytes"] = path.stat().st_size
    result["sha256"] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
