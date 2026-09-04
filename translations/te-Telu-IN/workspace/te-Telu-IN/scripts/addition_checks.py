"""Bounded B013 checks of actual notation, word answers and optional arithmetic.

This is a reviewed finite unit validator, not a general Telugu parser or a
linguistic-approval claim. Mathematical expressions are classified by their
content, never by the legacy CNXML ``equation`` container name.
"""
from hashlib import sha256
from collections import Counter
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from naming_checks import english_name, text_of

CN = "{http://cnx.rice.edu/cnxml}"
MATH = "{http://www.w3.org/1998/Math/MathML}"
SOURCE = Path(__file__).resolve().parents[1] / "sources/TE-B013.en.cnxml"
SOURCE_SHA = "dc2f2c8ad88edb588df364026e9e5b4301d416ef641fc7c833d5ca4fe0f93b35"
PAIRS = ((3, 4), (7, 1), (12, 14), (8, 4), (18, 11), (21, 16), (100, 200))
EXERCISES = (
    ("fs-id2294573", "eip-id1168287109262", "eip-id1168287334447", ((7, 1), (12, 14))),
    ("fs-id1386428", "eip-id1168289469583", "eip-id1168288479736", ((8, 4), (18, 11))),
    ("fs-id2334163", "eip-id1168289631763", "eip-id1168288338262", ((21, 16), (100, 200))),
)
TE_NAMES = {0: "శూన్యం", 1: "ఒకటి", 2: "రెండు", 3: "మూడు", 4: "నాలుగు",
            5: "ఐదు", 6: "ఆరు", 7: "ఏడు", 8: "ఎనిమిది", 9: "తొమ్మిది",
            11: "పదకొండు", 12: "పన్నెండు", 14: "పద్నాలుగు", 16: "పదహారు",
            18: "పద్దెనిమిది", 21: "ఇరవై ఒకటి", 100: "వంద", 200: "రెండు వందలు"}
ADDITION = re.compile(r"(?<![\w,])([0-9]+)\s*\+\s*([0-9]+)(?!\d|,\d)")
EQUALITY = re.compile(r"(?<![\w,])([0-9]+)\s*\+\s*([0-9]+)\s*=\s*([0-9]+)(?!\d|,\d)")
RELATION = re.compile(r"(?<![\w.,])[0-9]+(?:\s*\+\s*[0-9]+)*(?:\s*=\s*[0-9]+(?:\s*\+\s*[0-9]+)*)+(?!\d|,\d|\.[0-9])")
XH = "{http://www.w3.org/1999/xhtml}"


def _ids(root):
    nodes = [n for n in root.iter() if n.get("id")]
    ids = {n.get("id"): n for n in nodes}
    assert len(ids) == len(nodes), "Duplicate B013 ID"
    return ids


def _node(ids, ident):
    assert ident in ids, "Missing B013 node: " + ident
    return ids[ident]


def _tokens(math):
    return [(e.tag, tuple(sorted(e.attrib.items())), (e.text or "").strip())
            for e in math.iter()]


def _math_signature(root):
    return [_tokens(e) for e in root.iter(MATH + "math")]


def _structure(root):
    # Only text/accessible descriptions and document language are localized.
    return [(e.tag, tuple(sorted((k, v) for k, v in e.attrib.items()
                                if k not in {"aria-label", "{http://www.w3.org/XML/1998/namespace}lang"})),
             len(e)) for e in root.iter()]


def _math_pair(node):
    maths = list(node.iter(MATH + "math"))
    assert len(maths) == 1, "Expected one B013 addition expression"
    tokens = [(e.tag, (e.text or "").strip()) for e in maths[0].iter()
              if e.tag in {MATH + "mn", MATH + "mo"}]
    assert len(tokens) == 3 and [t[0] for t in tokens] == [MATH + "mn", MATH + "mo", MATH + "mn"], "B013 expression shape changed"
    assert tokens[1][1] == "+", "B013 operation changed"
    return int(tokens[0][1]), int(tokens[2][1])


def source_cases():
    """Read the pinned source; independently derive pairs and provided words."""
    raw = SOURCE.read_bytes()
    assert sha256(raw).hexdigest() == SOURCE_SHA, "B013 frozen source changed"
    root = ET.fromstring(raw)
    ids = _ids(root)
    assert (len(list(root.iter())), len(ids), len(_math_signature(root))) == (143, 30, 19), "B013 source inventory changed"
    found = []
    for math in root.iter(MATH + "math"):
        if any((e.text or "").strip() == "+" for e in math.iter(MATH + "mo")):
            if len(list(math.iter(MATH + "mn"))) == 2:
                pair = _math_pair(math)
                if pair not in found:
                    found.append(pair)
    assert tuple(found) == PAIRS, "B013 source pair/order changed"
    for exercise, problem_list, answer_list, pairs in EXERCISES:
        assert _node(ids, exercise).tag == CN + "exercise"
        problems = _node(ids, problem_list).findall(CN + "item")
        answers = _node(ids, answer_list).findall(CN + "item")
        assert len(problems) == len(answers) == len(pairs) == 2
        for problem, answer, (a, b) in zip(problems, answers, pairs):
            assert _math_pair(problem) == (a, b), "B013 source operands changed"
            text = text_of(answer).lower()
            assert english_name(a) + " plus " + english_name(b) in text, "B013 source reading changed"
            assert "sum of " + english_name(a) + " and " + english_name(b) in text, "B013 source result name changed"
            assert "=" not in text, "Source requests words, not evaluated equations"
    return root, tuple((a, b, a + b) for a, b in found)


def _word_answer(node, a, b):
    text = text_of(node).replace(" అనే ", " ")
    assert TE_NAMES[a] + " ప్లస్ " + TE_NAMES[b] in text, "B013 Telugu reading changed"
    assert TE_NAMES[a] + ", " + TE_NAMES[b] + " సంఖ్యల మొత్తం" in text, "B013 Telugu result name changed"
    assert english_name(a) + " plus " + english_name(b) in text.lower(), "B013 English reading changed"
    assert "sum of " + english_name(a) + " and " + english_name(b) in text.lower(), "B013 English result name changed"


def validate_addition_target(target):
    source, cases = source_cases()
    assert _structure(source) == _structure(target), "B013 source structure/attributes changed"
    assert _math_signature(source) == _math_signature(target), "B013 source MathML changed"
    ids = _ids(target)
    assert _math_pair(_node(ids, "fs-id1474530")) == (3, 4)
    assert "=" not in text_of(_node(ids, "fs-id1474530")), "B013 expression acquired equality"
    opening = _node(ids, "fs-id3165690")
    assert re.search(r"సోమవారం\s*3\s*గంటలు,\s*శుక్రవారం\s*4\s*గంటలు", text_of(opening)), "B013 work hours/day association changed"
    assert "గత వారం" in text_of(opening), "B013 source time context changed"
    assert text_of(_node(ids, "term-00001")) == "మొత్తం (sum)", "B013 sum definition changed"
    definition = text_of(_node(ids, "fs-id2619407")).replace(" అనే ", " ")
    for phrase in ["మూడు ప్లస్ నాలుగు (three plus four)", "మూడు, నాలుగు సంఖ్యల మొత్తం", "కలిపే సంఖ్యలు (addends)", "గణిత రాత (expression)"]:
        assert phrase in definition, "B013 defined role/word changed: " + phrase
    table = _node(ids, "fs-id2711498")
    group = table.find(CN + "tgroup")
    assert group.get("cols") == "5" and len(group.findall(CN + "colspec")) == 5, "B013 table requires five columns"
    rows = table.findall(".//" + CN + "row")
    assert len(rows) == 2 and all(len(r.findall(CN + "entry")) == 5 for r in rows), "B013 table requires two actual five-cell rows"
    assert [text_of(e) for e in rows[0]] == ["క్రియ (operation)", "చిహ్నం (notation)", "గణిత రాత (expression)", "చదివే విధానం (read as)", "ఫలితం (result)"], "B013 table column roles changed"
    cells = list(rows[1])
    assert text_of(cells[0]) == "సంకలనం" and text_of(cells[1]) == "+", "B013 table operation changed"
    assert _math_pair(cells[2]) == (3, 4)
    assert text_of(cells[3]) == "మూడు ప్లస్ నాలుగు (three plus four)", "B013 table reading changed"
    assert text_of(cells[4]).replace(" అనే ", " ") == "మూడు, నాలుగు సంఖ్యల మొత్తం; కలిపే సంఖ్యలు 3 మరియు 4", "B013 table result must name the sum, not evaluate it"
    aria = table.get("aria-label", "")
    assert "రెండు అడ్డ వరుసలు, ఐదు నిలువు వరుసలు" in aria, "B013 accessible table dimensions changed"
    for phrase in ["క్రియ (operation)", "చిహ్నం (notation)", "గణిత రాత (expression)", "చదివే విధానం (read as)", "ఫలితం (result)"]:
        assert phrase in aria, "B013 accessible table roles changed"
    assert aria.index("క్రియ (operation)") < aria.index("చిహ్నం (notation)") < aria.index("గణిత రాత (expression)") < aria.index("చదివే విధానం (read as)") < aria.index("ఫలితం (result)"), "B013 accessible column order changed"
    assert "మూడు మరియు నాలుగు సంఖ్యల మొత్తం" in aria.replace(" అనే ", " ") and "3 + 4" in aria, "B013 accessible expression/result changed"
    assert re.findall(r"\d+", aria) == ["3", "4", "3", "4"], "B013 accessible operands changed"
    for ident in ["fs-id2703725", "fs-id1549906", "fs-id1630183"]:
        assert "గణిత చిహ్నాలతో ఇచ్చిన రాతను మాటల్లో రాయండి:" in text_of(_node(ids, ident)), "B013 requested answer type changed"
    for _, _, answer_id, pairs in EXERCISES:
        answers = _node(ids, answer_id).findall(CN + "item")
        for answer, (a, b) in zip(answers, pairs):
            _word_answer(answer, a, b)
            assert "=" not in text_of(answer), "B013 source word answer replaced/appended with evaluated equation"
            if answer_id == "eip-id1168287334447":
                assert f"{a}, {b} అనే కలిపే సంఖ్యలను" in text_of(answer), "B013 example addend roles changed"
    return cases


def _require_link(node, destination):
    assert any(e.tag.rsplit("}", 1)[-1] == "a" and e.get("href") == "#" + destination for e in node.iter()), "B013 answer backlink changed: " + destination


def _pair_mentions(node):
    return [(int(m[1]), int(m[2])) for m in ADDITION.finditer(text_of(node))]


def classify_notation(text):
    """Classify this unit's finite nonnegative addition notation by relation."""
    text = " ".join(text.split())
    equation = EQUALITY.fullmatch(text)
    if equation:
        a, b, total = map(int, equation.groups())
        assert a + b == total, "Incorrect B013 addition equality: " + text
        return "equation", (a, b, total)
    expression = ADDITION.fullmatch(text)
    assert expression, "Invalid B013 addition notation: " + text
    return "expression", tuple(map(int, expression.groups()))


def _equalities(root):
    """Return and recompute every displayed addition equation, once per leaf block."""
    found = []
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] not in {"p", "li", "td", "dd"}:
            continue
        if any(e is not node and e.tag.rsplit("}", 1)[-1] in {"p", "li", "td", "dd"} for e in node.iter()):
            continue
        for match in RELATION.finditer(text_of(node)):
            complete = EQUALITY.fullmatch(match.group())
            assert complete, "Unsupported/changed B013 relation: " + match.group()
            a, b, total = map(int, complete.groups())
            assert a + b == total, "Incorrect B013 addition equality: " + match.group()
            found.append((a, b, total))
    return found


def _strong_word_answer(node, a, b):
    _word_answer(node, a, b)
    actual = [text_of(e) for e in node.iter(XH + "strong")]
    expected = [TE_NAMES[a] + " ప్లస్ " + TE_NAMES[b],
                TE_NAMES[a] + ", " + TE_NAMES[b] + " అనే సంఖ్యల మొత్తం"]
    assert actual == expected, "B013 displayed strong word answers changed"
    roles = re.findall(r"the addends are (?:the whole numbers )?(\d+) and (\d+)", text_of(node).lower())
    assert roles == [(str(a), str(b))], "B013 English addend roles changed"


def _classification_answer(node, a, b):
    expected = [("expression", (a, b)), ("equation", (a, b, a + b))]
    displayed = []
    for strong in node.iter(XH + "strong"):
        match = re.fullmatch(r"(.+) ఒక (expression|equation)", text_of(strong))
        assert match, "B013 displayed classification missing"
        classification, numbers = classify_notation(match[1])
        assert classification == match[2], "B013 expression/equation label contradicts notation"
        displayed.append((classification, numbers))
    assert displayed == expected, "B013 classified operands/result changed"
    english = " ".join(text_of(p) for p in node.findall(XH + "p") if p.get("lang") == "en")
    classified = []
    for match in re.finditer(r"(\d+\s*\+\s*\d+(?:\s*=\s*\d+)?) is an (expression|equation)", english):
        classification, numbers = classify_notation(match[1])
        assert classification == match[2], "B013 English classification contradicts notation"
        classified.append((classification, numbers))
    assert classified == expected, "B013 English classification changed"


def validate_b013(target, bridge):
    """Validate actual ElementTree roots; return bounded answer/structure counts."""
    cases = validate_addition_target(target)
    ids = _ids(bridge)
    assert bridge.get("id") == "B013-bridge"
    assert len(ids) == 24, "B013 bridge ID coverage changed"
    assert len(list(bridge.iter(XH + "a"))) == 14, "B013 bridge link coverage changed"
    assert len(list(bridge.iter(XH + "details"))) == 9, "B013 solution/optional-detail coverage changed"
    source_ids = _ids(target)
    for link in bridge.iter(XH + "a"):
        href = link.get("href", "")
        assert href.startswith("#") and href[1:] in (ids.keys() | source_ids.keys()), "B013 unresolved source/bridge link: " + href

    for case, pair in [("D01", (6, 2)), ("R01", (9, 0))]:
        question = _node(ids, "B013-" + case)
        answer = _node(ids, "B013-S-" + case)
        assert _pair_mentions(question) == [pair], "B013 entry/recheck target pair changed: " + case
        assert "మాటల్లో చదవండి" in text_of(question) and "ఫలితానికి" in text_of(question), "B013 entry/recheck requested answer type changed"
        _require_link(question, "B013-S-" + case)
        _strong_word_answer(answer, *pair)
        assert f"కలిపే సంఖ్యలు {pair[0]}, {pair[1]}" in text_of(answer), "B013 Telugu addend roles changed: " + case
        assert _pair_mentions(answer) and all(p == pair for p in _pair_mentions(answer)), "B013 answer expression drift: " + case
    assert "=" not in text_of(_node(ids, "B013-S-D01")), "B013 reading-only entry was replaced by computation"
    zero = text_of(_node(ids, "B013-S-R01"))
    for phrase in ["రెండో కలిపే సంఖ్య 0", "విలువ మారదు", "కుడివైపు 9 ఫలితం; ఎడమవైపు 9 ఇచ్చిన కలిపే సంఖ్య", "zero must still be read"]:
        assert phrase in zero, "B013 zero/operand-result roles changed"

    for case, pair in [("D02", (5, 1)), ("R02", (2, 5))]:
        question = _node(ids, "B013-" + case)
        answer = _node(ids, "B013-S-" + case)
        assert _pair_mentions(question) == [pair, pair], "B013 classification question operands changed"
        assert _equalities(question) == [(*pair, sum(pair))], "B013 classification question relation changed"
        assert "expression" in text_of(question) and "equation" in text_of(question), "B013 classification question type changed"
        _require_link(question, "B013-S-" + case)
        _classification_answer(answer, *pair)

    source_solutions = [
        ("T01a", "fs-id1386428", (8, 4), ["మొదటి కలిపే సంఖ్య 8; రెండోది 4", "8 ను “ఎనిమిది”, + ను “ప్లస్”, 4 ను “నాలుగు”"]),
        ("T01b", "fs-id1386428", (18, 11), ["కలిపే సంఖ్యలు 18, 11", "18 ను “పద్దెనిమిది”, 11 ను “పదకొండు”"]),
        ("T02a", "fs-id2334163", (21, 16), ["మొదటి సంఖ్య 21 ను “ఇరవై ఒకటి”, రెండో సంఖ్య 16 ను “పదహారు”"]),
        ("T02b", "fs-id2334163", (100, 200), ["కలిపే సంఖ్యలు 100, 200", "100 ను “వంద”, 200 ను “రెండు వందలు”", "not 1 and 2"]),
    ]
    for case, source_id, pair, phrases in source_solutions:
        answer = _node(ids, "B013-S-" + case)
        assert "=" not in text_of(answer), "B013 source bridge word answer substituted with evaluation"
        assert _pair_mentions(answer) == [pair], "B013 source bridge question pair changed: " + case
        _strong_word_answer(answer, *pair)
        _require_link(answer, source_id)
        for phrase in phrases:
            assert phrase in text_of(answer), "B013 source operand/reading explanation changed: " + case

    optional = _node(ids, "B013-extra-values")
    assert "ఐచ్ఛికం" in text_of(optional.find(XH + "summary")), "B013 computed values no longer labeled optional"
    assert "మూలం అడిగిన మాటల జవాబులు కావు" in text_of(optional), "B013 optional/source answer distinction removed"
    rows = optional.findall(".//" + XH + "tbody/" + XH + "tr")
    assert len(rows) == 7 and all(len(row) == 3 for row in rows), "B013 optional computation coverage changed"
    reasons = ["మూడు గంటలకు నాలుగు గంటలు కలిపితే ఏడు గంటలు.",
               "ఏడుకు ఒకటి కలిపితే తరువాతి సంఖ్య ఎనిమిది.",
               "రెండు సంఖ్యల్లో కలిపి రెండు పదులు, ఆరు ఒకట్లు ఉంటాయి.",
               "ఎనిమిదికి రెండు కలిపితే పది; మిగిలిన రెండు కలిపితే పన్నెండు.",
               "కలిపి రెండు పదులు, తొమ్మిది ఒకట్లు ఉంటాయి.",
               "కలిపి మూడు పదులు, ఏడు ఒకట్లు ఉంటాయి.",
               "ఒక వందకు రెండు వందలు కలిపితే మూడు వందలు."]
    contexts = ["పరిచయం: పని గంటలు", "పరిష్కరించిన ఉదాహరణ ⓐ", "పరిష్కరించిన ఉదాహరణ ⓑ",
                "మొదటి Try It ⓐ", "మొదటి Try It ⓑ", "రెండో Try It ⓐ", "రెండో Try It ⓑ"]
    for row, expected, reason, context in zip(rows, cases, reasons, contexts):
        assert text_of(row[0]) == context, "B013 optional value source-part mapping changed"
        kind, actual = classify_notation(text_of(row[1]))
        assert kind == "equation" and actual == expected, "B013 displayed optional pair/result changed"
        assert text_of(row[2]) == reason, "B013 optional arithmetic reason changed"

    guide = _node(ids, "B013-K1")
    roles = guide.findall(".//" + XH + "tbody/" + XH + "tr")
    assert len(roles) == 4 and all(len(row) == 2 for row in roles), "B013 role guide shape changed"
    assert [text_of(row[0]) for row in roles] == ["3, 4", "+", "3 + 4", "మూడు, నాలుగు అనే సంఖ్యల మొత్తం"], "B013 role-guide objects changed"
    for row, phrase in zip(roles, ["కలిపే సంఖ్యలు (addends)", "ఇది ఒక సంఖ్య కాదు", "గణిత రాత (expression)", "ఇది మరో కలిపే సంఖ్య కాదు"]):
        assert phrase in text_of(row[1]), "B013 role-guide explanation changed"
    assert "సోమవారం పనిచేసిన గంటల సంఖ్య 3; శుక్రవారం పనిచేసిన గంటల సంఖ్య 4" in text_of(guide), "B013 bridge work hours/day association changed"

    convention = text_of(_node(ids, "B013-task-convention"))
    assert "చిహ్నాలతో ఉన్న రాతను మాటల్లో చెప్పడం" in convention and "అవి మూలంలోని మాటల జవాబుల స్థానంలో రావు" in convention, "B013 requested-word-answer scope changed"
    distinction = text_of(_node(ids, "B013-K2"))
    for phrase in ["అది ఒక గణిత రాత (expression)", "అందులో = లేదు", "సమానమని చెప్పే వాక్యం (equation)",
                   "+ క్రియను సూచిస్తుంది; = సమానత్వాన్ని సూచిస్తుంది", "An expression such as 3 + 4",
                   "The additional statement 3 + 4 = 7 asserts equality", "Reading an expression and evaluating it are different tasks"]:
        assert phrase in distinction, "B013 expression/equality explanation changed"
    route = _node(ids, "B013-route")
    assert [e.get("href") for e in route.iter(XH + "a")] == ["#B013-K1", "#B013-R01", "#B013-K2", "#B013-R02", "#fs-id1386428", "#fs-id2334163"], "B013 skill/source routing changed"

    equalities = _equalities(bridge)
    expected = Counter(cases)
    expected.update({(3, 4, 7): 2, (5, 1, 6): 3, (2, 5, 7): 3, (9, 0, 9): 1})
    assert Counter(equalities) == expected, "B013 displayed equation coverage/ordered operands changed"
    return {"source_pairs": 7, "source_word_parts": 6, "source_try_parts": 4,
            "original_entry_rechecks": 4, "optional_source_values": 7,
            "displayed_addition_equalities": len(equalities)}
