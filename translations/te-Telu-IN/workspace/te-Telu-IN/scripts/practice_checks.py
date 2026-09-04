"""Bounded B008 checks of actual questions/answers, not linguistic approval.

Recompute the frozen source; do not take a catalog, bridge metadata, or QA
inventory as an answer key. The four picture counts were independently read
from the original JPEGs and are the only image-derived constants here.
"""
from fractions import Fraction
from pathlib import Path
import hashlib
import re
import xml.etree.ElementTree as ET

from naming_checks import english_name, text_of
from writing_checks import english_value
from rounding_checks import round_whole_half_up, controlling_digit

BASE = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
MATH = "{http://www.w3.org/1998/Math/MathML}"
SOURCE_SHA256 = "7f7ce451bd8f7757bd0bd515db42de196d26f68f41bec22959876e797e259a14"
MODELS = {
    "fs-id1224988": (5, 6, 1), "fs-id2646862": (3, 8, 4),
    "fs-id1462995": (4, 0, 7), "fs-id1339977": (6, 2, 0),
}
MODEL_ALT = {
    "fs-id1224988": ("చతురస్రాలు ఐదు", "కడ్డీలు ఆరు", "విడిగా ఒక చిన్న"),
    "fs-id2646862": ("చతురస్రాలు మూడు", "కడ్డీలు ఎనిమిది", "విడిగా నాలుగు"),
    "fs-id1462995": ("చతురస్రాలు నాలుగు", "విడిగా ఏడు", "కడ్డీలు లేవు"),
    "fs-id1339977": ("చతురస్రాలు ఆరు", "కడ్డీలు రెండు", "చిన్న బ్లాకులు లేవు"),
}
CONTEXT_NAMES = {
    "fs-id1825926": "seven billion, one hundred seventy-three million",
    "fs-id2926292": "four billion, five hundred sixty-eight million",
    "fs-id1733890": "thirty-nine trillion",
    "fs-id1572155": "three trillion, five hundred billion",
}
UNITS = {
    21: "feet", 22: "feet", 23: "hours", 24: "minutes", 25: "people",
    26: "people", 27: "students", 28: "automobiles", 29: "people",
    30: "people", 39: "people", 40: "years", 41: "gallons", 42: "USD",
    51: "USD", 52: "USD", 53: "USD", 54: "USD", 55: "people",
    56: "kilometers",
}
TE_UNITS = {
    "feet": "అడుగులు", "hours": "గంటలు", "minutes": "నిమిషాలు",
    "years": "సంవత్సరాలు", "gallons": "గ్యాలన్ల", "USD": "డాలర్లు",
    "people": "మంది", "students": "విద్యార్థులు", "automobiles": "కార్లు",
    "kilometers": "కిలోమీటర్లు",
}
EN_PLACES = {1: "ones", 10: "tens", 100: "hundreds", 1000: "thousands",
             10000: "ten thousands", 100000: "hundred thousands",
             1000000: "millions", 10000000: "ten millions"}
TE_PLACES = {1: "ఒకట్ల", 10: "పదుల", 100: "వందల", 1000: "వేల",
             10000: "పది వేల", 100000: "వంద వేల", 1000000: "మిలియన్ల",
             10000000: "పది మిలియన్ల", 100000000: "వంద మిలియన్ల",
             1000000000: "బిలియన్ల"}
TE_NEAREST = {10: "పదులకు", 100: "వందలకు", 1000: "వేలకు"}
CONTEXT_TARGETS = {
    "ten dollars": (10, "పది డాలర్లు"),
    "hundred dollars": (100, "వంద డాలర్లు"),
    "thousand dollars": (1000, "వెయ్యి డాలర్లు"),
    "ten-thousand dollars": (10000, "పది వేల డాలర్లు"),
    "billion people": (1000000000, "ఒక బిలియన్ మంది"),
    "hundred-million people": (100000000, "వంద మిలియన్ల మంది"),
    "million people": (1000000, "ఒక మిలియన్ మంది"),
    "hundred-million kilometers": (100000000, "వంద మిలియన్ల కిలోమీటర్లు"),
    "ten-million kilometers": (10000000, "పది మిలియన్ల కిలోమీటర్లు"),
    "million kilometers": (1000000, "ఒక మిలియన్ కిలోమీటర్లు"),
}


# These editorial strings were read against their independently computed
# English/value pairs. They are regression witnesses, not a general Telugu
# parser or exact-string keys imposed on learners' own responses.
TE_REVIEWED_NAMES = {
    "1078": {
        "bridge": "వెయ్యి డెబ్బై ఎనిమిది",
        "target": "వెయ్యి డెబ్బై ఎనిమిది"
    },
    "5902": {
        "bridge": "ఐదు వేల, తొమ్మిది వందల రెండు"
    },
    "12276": {
        "bridge": "పన్నెండు వేల, రెండు వందల డెబ్బై ఆరు"
    },
    "14410": {
        "bridge": "పద్నాలుగు వేల, నాలుగు వందల పది",
        "target": "పద్నాలుగు వేల, నాలుగు వందల పది"
    },
    "18549": {
        "bridge": "పద్దెనిమిది వేల, ఐదు వందల నలభై తొమ్మిది డాలర్లు"
    },
    "24493": {
        "bridge": "ఇరవై నాలుగు వేల, నాలుగు వందల తొంభై మూడు డాలర్లు",
        "target": "ఇరవై నాలుగు వేల, నాలుగు వందల తొంభై మూడు డాలర్లు"
    },
    "146023": {
        "bridge": "నూట నలభై ఆరు వేల, ఇరవై మూడు"
    },
    "364510": {
        "bridge": "మూడు వందల అరవై నాలుగు వేల, ఐదు వందల పది",
        "target": "మూడు వందల అరవై నాలుగు వేల, ఐదు వందల పది"
    },
    "525600": {
        "bridge": "ఐదు వందల ఇరవై ఐదు వేల, ఆరు వందలు"
    },
    "613200": {
        "bridge": "ఆరు వందల పదమూడు వేల, రెండు వందలు",
        "target": "ఆరు వందల పదమూడు వేల, రెండు వందలు"
    },
    "1458398": {
        "bridge": "ఒక మిలియన్, నాలుగు వందల యాభై ఎనిమిది వేల, మూడు వందల తొంభై ఎనిమిది"
    },
    "2617176": {
        "bridge": "రెండు మిలియన్ల, ఆరు వందల పదిహేడు వేల, నూట డెబ్బై ఆరు",
        "target": "రెండు మిలియన్ల, ఆరు వందల పదిహేడు వేల, నూట డెబ్బై ఆరు"
    },
    "2718782": {
        "bridge": "రెండు మిలియన్ల, ఏడు వందల పద్దెనిమిది వేల, ఏడు వందల ఎనభై రెండు"
    },
    "5846103": {
        "bridge": "ఐదు మిలియన్ల, ఎనిమిది వందల నలభై ఆరు వేల, నూట మూడు",
        "target": "ఐదు మిలియన్ల, ఎనిమిది వందల నలభై ఆరు వేల, నూట మూడు"
    },
    "20665415": {
        "bridge": "ఇరవై మిలియన్ల, ఆరు వందల అరవై ఐదు వేల, నాలుగు వందల పదిహేను"
    },
    "23867000": {
        "bridge": "ఇరవై మూడు మిలియన్ల, ఎనిమిది వందల అరవై ఏడు వేలు",
        "target": "ఇరవై మూడు మిలియన్ల, ఎనిమిది వందల అరవై ఏడు వేలు"
    },
    "37889005": {
        "bridge": "ముప్పై ఏడు మిలియన్ల, ఎనిమిది వందల ఎనభై తొమ్మిది వేల, ఐదు",
        "target": "ముప్పై ఏడు మిలియన్ల, ఎనిమిది వందల ఎనభై తొమ్మిది వేల, ఐదు"
    },
    "62008465": {
        "bridge": "అరవై రెండు మిలియన్ల, ఎనిమిది వేల, నాలుగు వందల అరవై ఐదు"
    },
    "1267401849": {
        "bridge": "ఒక బిలియన్, రెండు వందల అరవై ఏడు మిలియన్ల, నాలుగు వందల ఒక వేల, ఎనిమిది వందల నలభై తొమ్మిది"
    },
    "1377583156": {
        "bridge": "ఒక బిలియన్, మూడు వందల డెబ్బై ఏడు మిలియన్ల, ఐదు వందల ఎనభై మూడు వేల, నూట యాభై ఆరు",
        "target": "ఒక బిలియన్, మూడు వందల డెబ్బై ఏడు మిలియన్ల, ఐదు వందల ఎనభై మూడు వేల, నూట యాభై ఆరు"
    }
}
TE_REVIEWED_INPUTS = {
    "253": "రెండు వందల యాభై మూడు",
    "412": "నాలుగు వందల పన్నెండు",
    "35975": "ముప్పై ఐదు వేల, తొమ్మిది వందల డెబ్బై ఐదు",
    "61415": "అరవై ఒక వేల, నాలుగు వందల పదిహేను",
    "11044167": "పదకొండు మిలియన్ల, నలభై నాలుగు వేల, నూట అరవై ఏడు",
    "18102783": "పద్దెనిమిది మిలియన్ల, నూట రెండు వేల, ఏడు వందల ఎనభై మూడు",
    "3226512017": "మూడు బిలియన్ల, రెండు వందల ఇరవై ఆరు మిలియన్ల, ఐదు వందల పన్నెండు వేల, పదిహేడు",
    "11471036106": "పదకొండు బిలియన్ల, నాలుగు వందల డెబ్బై ఒక మిలియన్ల, ముప్పై ఆరు వేల, నూట ఆరు",
    "7173000000": "ప్రపంచ జనాభా ఏడు బిలియన్ల, నూట డెబ్బై మూడు మిలియన్ల మంది అని అంచనా వేశారు",
    "4568000000": "సౌర వ్యవస్థ వయస్సు నాలుగు బిలియన్ల, ఐదు వందల అరవై ఎనిమిది మిలియన్ల సంవత్సరాలు అని అంచనా",
    "39000000000000": "టాహో సరస్సులో ముప్పై తొమ్మిది ట్రిలియన్ల గ్యాలన్ల నీరు పట్టగలదు",
    "3500000000000": "సమాఖ్య ప్రభుత్వ అప్పటి బడ్జెట్ మూడు ట్రిలియన్ల, ఐదు వందల బిలియన్ల డాలర్లు"
}
TE_REVIEWED_SUMMARIES = {
    "253": "రెండు వందల యాభై మూడు",
    "412": "నాలుగు వందల పన్నెండు",
    "35975": "ముప్పై ఐదు వేల, తొమ్మిది వందల డెబ్బై ఐదు",
    "61415": "అరవై ఒక వేల, నాలుగు వందల పదిహేను",
    "11044167": "పదకొండు మిలియన్ల, నలభై నాలుగు వేల, నూట అరవై ఏడు",
    "18102783": "పద్దెనిమిది మిలియన్ల, నూట రెండు వేల, ఏడు వందల ఎనభై మూడు",
    "3226512017": "మూడు బిలియన్ల, రెండు వందల ఇరవై ఆరు మిలియన్ల, ఐదు వందల పన్నెండు వేల, పదిహేడు",
    "11471036106": "పదకొండు బిలియన్ల, నాలుగు వందల డెబ్బై ఒక మిలియన్ల, ముప్పై ఆరు వేల, నూట ఆరు"
}


def _te_plain(text):
    return re.sub(r"[\s,.;:!?]+", "", text)


def _local(node):
    return node.tag.rsplit("}", 1)[-1]


def _ids(root):
    nodes = [e for e in root.iter() if e.get("id")]
    result = {e.get("id"): e for e in nodes}
    assert len(nodes) == len(result), "Duplicate B008 ID"
    return result


def _node(ids, ident):
    assert ident in ids, "Missing B008 node: " + ident
    return ids[ident]


def _raw_math(node):
    if node.tag == MATH + "mfrac":
        return _raw_math(node[0]) + "/" + _raw_math(node[1])
    return (node.text or "") + "".join(_raw_math(c) + (c.tail or "") for c in node)


def _clean(node):
    return re.sub(r"^[ⓐ-ⓔ]\s*", "", text_of(node)).strip()


def _number_strings(text):
    return [n.rstrip(",") for n in
            re.findall(r"(?<![A-Za-z0-9_,])\$?[0-9][0-9,]*", text)]


def _numbers(text):
    return [int(n.lstrip("$").replace(",", "")) for n in _number_strings(text)]


def _input_number(problem):
    node = problem.find(".//" + MATH + "mn")
    if node is None:
        node = problem.find(".//" + MATH + "mtext")
    assert node is not None and len(_numbers(node.text or "")) == 1
    return _numbers(node.text)[0]


def _english_gloss(node):
    found = re.search(r"మూల ఇంగ్లీషు (?:సంఖ్యా )?పేరు:\s*(.+)$", text_of(node))
    assert found, "Missing B008 English number-name gloss: " + node.get("id", "")
    return found.group(1).strip().rstrip(".")


def _name_normalized(name):
    return " ".join(name.lower().strip().rstrip(".").replace("-", " ").split())


def _require_name(actual, value, unit=None):
    if unit == "USD":
        assert actual.lower().rstrip(".").endswith(" dollars"), "B008 English currency unit changed"
        actual = re.sub(r" dollars\.?$", "", actual, flags=re.I)
    assert _name_normalized(actual) == _name_normalized(english_name(value)), (
        "B008 English number value changed: " + actual)


def _shape(root):
    def walk(node, depth):
        yield node.tag, depth, node.get("id")
        for child in node:
            yield from walk(child, depth + 1)
    return list(walk(root, 0))


def _math_signature(root):
    return [(e.tag, sorted(e.attrib.items()), (e.text or "").strip())
            for e in root.iter() if e.tag.startswith(MATH)]


def source_cases():
    """Recompute all 58 frozen exercises, including 96 response parts."""
    raw = (BASE / "sources/TE-B008.en.cnxml").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA256, "B008 source changed"
    source = ET.fromstring(raw)
    exercises = list(source.iter(CN + "exercise"))
    assert len(exercises) == 58 and len(list(source.iter())) == 659
    records = []
    for order, exercise in enumerate(exercises, 1):
        problem = exercise.find(CN + "problem")
        solution = exercise.find(CN + "solution")
        ident = exercise.get("id")
        case = {"order": order, "id": ident, "problem_id": problem.get("id"),
                "solution_id": solution.get("id") if solution is not None else None,
                "unit": UNITS.get(order), "parts": []}
        if order <= 4:
            case["kind"] = "membership"
            row = problem.find(".//" + MATH + "mrow")
            values = [Fraction(_raw_math(e)) for e in row if e.tag != MATH + "mo"]
            case["inputs"] = values
            case["parts"] = [{"label": label, "expected": [int(n) for n in values
                              if n.denominator == 1 and n >= minimum]}
                             for label, minimum in (("a", 1), ("b", 0))]
        elif order <= 8:
            case["kind"] = "model"
            counts = MODELS[ident]
            case["media_id"] = problem.find(CN + "media").get("id")
            case["counts"] = counts
            case["parts"] = [{"label": "single", "expected":
                              sum(n * p for n, p in zip(counts, (100, 10, 1)))}]
        elif order <= 12:
            case["kind"] = "place"
            number = _input_number(problem)
            case["input"] = number
            for label, item in zip("abcde", problem.findall(".//" + CN + "item")):
                digit = int(_clean(item))
                assert str(number).count(str(digit)) == 1
                place = 10 ** (len(str(number)) - 1 - str(number).index(str(digit)))
                case["parts"].append({"label": label, "digit": digit, "place": place,
                                      "contribution": digit * place})
        elif order <= 30 or order in (51, 52):
            case["kind"] = "name"
            value = _input_number(problem)
            case["parts"] = [{"label": "single", "input": value,
                              "english": english_name(value)}]
        elif order <= 42:
            case["kind"] = "digits"
            phrase = CONTEXT_NAMES.get(ident, text_of(problem))
            assert phrase in text_of(problem)
            case["parts"] = [{"label": "single", "english": phrase,
                              "expected": english_value(phrase)}]
        elif order <= 50:
            case["kind"] = "round"
            text = text_of(problem)
            place = next(p for p, name in ((10, "ten"), (100, "hundred"),
                                          (1000, "thousand"))
                         if "nearest " + name + ":" in text)
            for label, item in zip("ab", problem.findall(".//" + CN + "item")):
                number = _input_number(item)
                case["parts"].append({"label": label, "input": number, "place": place,
                                      "expected": round_whole_half_up(number, place)})
        elif order <= 56:
            case["kind"] = "round"
            number = _input_number(problem)
            for label, item in zip("abcd", problem.findall(".//" + CN + "item")):
                source_label = _clean(item)
                place, target_label = CONTEXT_TARGETS[source_label]
                case["parts"].append({"label": label, "input": number, "place": place,
                                      "target_label": target_label,
                                      "expected": round_whole_half_up(number, place)})
        else:
            case["kind"] = "open"
            case["parts"] = [{"label": "single", "expected": None}]
        if solution is not None:
            items = solution.findall(".//" + CN + "item")
            provided = [_clean(x) for x in items] if items else [text_of(solution)]
            case["provided"] = provided
            if case["kind"] == "membership":
                assert [_numbers(s) for s in provided] == [p["expected"] for p in case["parts"]]
            elif case["kind"] == "place":
                assert provided == [EN_PLACES[p["place"]] for p in case["parts"]]
            elif case["kind"] in {"model", "digits", "round"}:
                assert [_numbers(s)[0] for s in provided] == [p["expected"] for p in case["parts"]]
            elif case["kind"] == "name":
                _require_name(provided[0], case["parts"][0]["input"], case["unit"])
        records.append(case)
    assert sum(len(c["parts"]) for c in records) == 96
    assert sum(c["solution_id"] is not None for c in records) == 29
    assert sum(c["kind"] == "open" for c in records) == 2
    return source, records


def validate_practice_target(target):
    """Read actual localized CNXML: IDs, math, names, places, units and alts."""
    source, cases = source_cases()
    ids = _ids(target)
    assert _shape(target) == _shape(source), "B008 source structure/IDs changed"
    assert len(ids) == 273 and len(list(target.iter(MATH + "math"))) == 57
    assert _math_signature(target) == _math_signature(source), "B008 source MathML changed"
    # Numeric-only passthrough text includes solutions not encoded in MathML.
    for original, localized in zip(source.iter(), target.iter()):
        for key in ("text", "tail"):
            old = getattr(original, key) or ""
            new = getattr(localized, key) or ""
            if re.search(r"[0-9]", old) and not re.search(r"[A-Za-z]", old):
                assert old == new, "B008 numeric/source currency text changed"
            if "whole number" in old.lower():
                assert "పూర్ణాంక" in new, "B008 whole-number terminology changed"
            if "counting numbers" in old.lower():
                assert "సహజ సంఖ్య" in new, "B008 counting-number terminology changed"
    assert "సహజ సంఖ్యలు" in text_of(_node(ids, "eip-498"))
    assert "పూర్ణాంకాలు" in text_of(_node(ids, "eip-498"))
    assert "స్థానాల పేర్లు" in text_of(_node(ids, "eip-439")), "B008 place-name convention changed"
    for case in cases:
        problem = _node(ids, case["problem_id"])
        if case["kind"] == "model":
            alt = _node(ids, case["media_id"]).get("alt", "")
            for fragment in MODEL_ALT[case["id"]]:
                assert fragment in alt, "B008 model alt count/zero changed: " + case["id"]
            assert _numbers(alt) == ([10, 10, 100] if case["order"] == 7 else [10, 10, 100, 10]), "B008 model unit values changed"
        elif case["kind"] == "digits":
            assert _english_gloss(problem) == case["parts"][0]["english"], "B008 source English phrase changed"
            assert english_value(_english_gloss(problem)) == case["parts"][0]["expected"]
            prefix = text_of(problem).split("మూల ఇంగ్లీషు")[0]
            assert _te_plain(prefix) == _te_plain(TE_REVIEWED_INPUTS[str(case["parts"][0]["expected"])]), "B008 reviewed Telugu input name changed"
        elif case["kind"] == "round":
            if case["order"] <= 50:
                assert "దగ్గరి " + TE_NEAREST[case["parts"][0]["place"]] in text_of(problem), "B008 target rounding place changed"
            else:
                items = problem.findall(".//" + CN + "item")
                assert len(items) == len(case["parts"])
                for item, part in zip(items, case["parts"]):
                    assert _clean(item) == part["target_label"], "B008 target rounding place/unit changed"
        if case["order"] in (21, 22, 23, 24, 27, 28, 39, 40, 41, 42, 56):
            assert TE_UNITS[case["unit"]] in text_of(problem.find(CN + "para")), "B008 source unit changed"
        if case["solution_id"]:
            solution = _node(ids, case["solution_id"])
            if case["kind"] == "place":
                for item, part in zip(solution.findall(".//" + CN + "item"), case["parts"]):
                    assert _clean(item) == TE_PLACES[part["place"]] + " స్థానం", "B008 supplied place name changed"
            elif case["kind"] == "name":
                assert _english_gloss(solution) == case["provided"][0], "B008 supplied English name changed"
                _require_name(_english_gloss(solution), case["parts"][0]["input"], case["unit"])
                prefix = text_of(solution).split("మూల ఇంగ్లీషు")[0]
                assert _te_plain(prefix) == _te_plain(TE_REVIEWED_NAMES[str(case["parts"][0]["input"])]["target"]), "B008 reviewed Telugu supplied name changed"
            elif case["kind"] == "open":
                assert "భిన్నంగా ఉండవచ్చు" in text_of(solution), "B008 open response forced into one answer"
                assert "సున్నాను" in text_of(solution) and "పూర్ణాంకాల" in text_of(solution)
    self_alt = _node(ids, "eip-id1165721974707").get("alt", "")
    for fragment in ("నాలుగు నిలువు వరుసలు", "ఆరు నైపుణ్యాల", "మొత్తం 18 గడులు ఖాళీగా",
                     "ఏ ఎంపికకూ గుర్తు పెట్టలేదు", "అక్షరాలలో", "అంకెలలో", "నమూనాలు"):
        assert fragment in self_alt, "B008 self-check blank structure/labels changed"
    return {"source_exercises": 58, "response_parts": 96, "determined_parts": 94,
            "open_writing_parts": 2, "provided_solution_nodes": 29,
            "rounding_parts": 30, "place_parts": 20}


def _children(node, tag):
    return [e for e in node if _local(e) == tag]


def _strong_answer(node):
    answers = [e for e in node.iter() if _local(e) == "strong"]
    assert len(answers) == 1, "B008 missing/extra displayed answer: " + node.get("id", "")
    return text_of(answers[0])


def _compact(text):
    return re.sub(r"\s+", "", text)


def _expression_value(expression):
    terms = re.split(r"\s*([+−-])\s*", expression.strip())
    def product(text):
        value = 1
        for number in text.split("×"):
            value *= int(number.strip().replace(",", ""))
        return value
    value = product(terms[0])
    for op, term in zip(terms[1::2], terms[2::2]):
        value += product(term) if op == "+" else -product(term)
    return value


def _equations(node):
    number = r"[0-9][0-9,]*"
    expression = number + r"(?:\s*[+−×-]\s*" + number + r")*"
    pattern = re.compile(r"(?<![\w,])" + expression + r"(?:\s*=\s*" + expression + r")+")
    return [m.group() for m in pattern.finditer(text_of(node))]


def _require_equation(node, expected):
    assert _compact(expected) in [_compact(e) for e in _equations(node)], (
        "B008 missing/changed explanatory equation: " + expected)


def verify_practice_equalities(bridge):
    """Check every side, once per leaf block; table cells are included."""
    count, relations = 0, 0
    block_tags = {"p", "li", "td", "dd"}
    for node in bridge.iter():
        if _local(node) not in block_tags:
            continue
        if any(child is not node and _local(child) in block_tags for child in node.iter()):
            continue  # A li containing p nodes must not double-count them.
        for equation in _equations(node):
            values = [_expression_value(side) for side in equation.split("=")]
            assert len(set(values)) == 1, "B008 incorrect displayed equality: " + equation
            count += 1
            relations += len(values) - 1
    assert count >= 64, "B008 missing worked equalities"
    return count, relations


def _require_groups(node, value, required=True):
    actual = [re.split(r"\s*\|\s*", m.group()) for m in
              re.finditer(r"(?<![\d|])\d+(?:\s*\|\s*\d+)+", text_of(node))]
    expected = f"{value:,}".split(",")
    assert (actual or not required) and all(g == expected for g in actual), (
        "B008 zero/period groups changed: " + node.get("id", ""))


def _require_sum(node, value):
    groups = f"{value:,}".split(",")
    if value == 412:
        expression = "400 + 12"
    elif value == 253:
        expression = "200 + 50 + 3"
    else:
        terms = [int(g) * 1000 ** (len(groups) - index - 1)
                 for index, g in enumerate(groups)]
        expression = " + ".join(f"{term:,}" for term in terms)
    _require_equation(node, expression + f" = {value:,}")


def _require_commas(text):
    for raw in _number_strings(text):
        number = raw.lstrip("$")
        if "," in number:
            assert number == f"{int(number.replace(',', '')):,}", "B008 international comma grouping changed: " + number


def _check_round_part(node, part, unit):
    paragraphs = _children(node, "p")
    assert len(paragraphs) == 2, "B008 rounding reasoning/distance paragraph missing"
    first, distances = map(text_of, paragraphs)
    token = chr(ord("ⓐ") + ord(part["label"]) - ord("a"))
    assert first.startswith(token + " "), "B008 displayed part label changed"
    number, place = part["input"], part["place"]
    digit, neighbor = number // place % 10, controlling_digit(number, place)
    heading = re.search(r"^[ⓐ-ⓔ]\s+([0-9,]+)(?:\s+(డాలర్లు|మంది|కిలోమీటర్లు))?\s+—\s+"
                        r"లక్ష్యం (.+?) స్థానం; అక్కడి అంకె ([0-9])\. వెంటనే కుడి (.+?) అంకె ([0-9])\.", first)
    assert heading, "B008 rounding input/target/neighbor labels missing"
    expected_unit = TE_UNITS[unit] if unit else None
    expected = (f"{number:,}", expected_unit, TE_PLACES[place], str(digit),
                TE_PLACES[place // 10], str(neighbor))
    assert heading.groups() == expected, "B008 rounding input/target/control changed: " + node.get("id", "")
    answer = round_whole_half_up(number, place)
    display = ("$" if unit == "USD" else "") + f"{answer:,}"
    if unit and unit != "USD":
        display += " " + expected_unit
    assert _strong_answer(node) == display, "B008 displayed rounded answer/unit changed: " + node.get("id", "")
    if neighbor < 5:
        assert "ఈ అంకె 5 కన్నా తక్కువ" in first and "లక్ష్య అంకెను పెంచము" in first, "B008 rounding down branch changed"
        if digit == 9:
            assert "9 అయినంత మాత్రాన బదిలీ చేయము" in first, "B008 target-nine no-carry condition changed"
    else:
        assert "ఈ అంకె 5 లేదా అంతకన్నా ఎక్కువ" in first and "లక్ష్య స్థానానికి చెందిన ఒక ప్రమాణాన్ని కలిపి" in first, "B008 rounding up/five branch changed"
        if digit == 9:
            _require_equation(paragraphs[0], "9 + 1 = 10")
            _require_equation(paragraphs[0], f"{number//place*place:,} + {place:,} = {answer:,}")
            assert TE_PLACES[place] + " స్థానంలో 0" in first, "B008 carry target digit changed"
            assert TE_PLACES[place * 10] + " స్థానానికి 1 బదిలీ" in first, "B008 carry destination changed"
    lower, upper = number // place * place, (number // place + 1) * place
    expected_numbers = [lower, upper, number - lower, upper - number, answer]
    if neighbor == 5:
        midpoint = (lower + upper) // 2
        assert number > midpoint  # Every B008 controlling-5 case is above, not on, a tie.
        expected_numbers.extend([number, midpoint])
        assert "మధ్య విలువ" in distances and "సమాన దూరపు సందర్భం కాదు" in distances, "B008 above-midpoint qualification changed"
    assert _numbers(distances) == expected_numbers, "B008 adjacent multiples/distances/result changed: " + node.get("id", "")
    if unit:
        stem = {"USD": "డాలర", "people": "మంది", "kilometers": "కిలోమీటర్"}[unit]
        assert distances.count(stem) >= 3, "B008 distance units changed"


def _check_direct_rounding(details, number, first_place, final_place):
    warning = text_of(_children(details, "p")[-1])
    first = round_whole_half_up(number, first_place)
    expected = [first, round_whole_half_up(first, final_place), number,
                round_whole_half_up(number, final_place)]
    assert _numbers(warning) == expected, "B008 direct/double-rounding warning changed"
    words = re.findall(r"పదులకు|వందలకు|వేలకు", warning)
    assert words == [TE_NEAREST[first_place], TE_NEAREST[final_place], TE_NEAREST[final_place]], "B008 direct/double-rounding target changed"
    assert len(re.findall(r"\$[0-9][0-9,]*", warning)) == 4, "B008 warning currency unit changed"


def _check_open_writing(ids):
    # These are examples/rubrics, never a unique learner answer. Only check
    # arithmetic in the actual numeric illustration, without fixing its input.
    explanation = text_of(_node(ids, "B008-open-writing"))
    assert "ఒకే పదబంధం సరైన జవాబు కాదు" in explanation, "B008 open writing turned into an exact key"
    sets = text_of(_node(ids, "B008-S-fs-id3202450"))
    for phrase in ("నమూనా", "ప్రతి సహజ సంఖ్య పూర్ణాంకమే", "ఇక్కడి సహజ సంఖ్య కాదు", "వేరే మాటలు"):
        assert phrase in sets, "B008 open counting/whole rubric changed"
    example = _node(ids, "B008-S-fs-id1258379")
    paragraphs = _children(example, "p")
    assert len(paragraphs) >= 3, "B008 open example/rubric missing"
    text = text_of(example)
    assert "నమూనా" in text and "వేరే సరైన సందర్భాలకు" in text, "B008 varied-response rubric missing"
    rubric = text_of(paragraphs[-1])
    for phrase in ("సంఖ్యలు ఇవ్వకపోయినా", "సంఖ్యలతో ఉదాహరణ ఇస్తే",
                   "తప్పనిసరి అదనపు షరతు కాదు"):
        assert phrase in rubric, "B008 optional numeric example became a required writing answer"
    match = re.search(r"లో ([0-9,]+) పుస్తకాలు", text)
    if match:
        number = int(match.group(1).replace(",", ""))
        target_word = re.search(r"దగ్గరి (పదులకు|వందలకు|వేలకు) సవరించాను", text)
        assert target_word, "B008 illustrative rounding target missing"
        place = next(p for p, word in TE_NEAREST.items() if word == target_word.group(1))
        answer = round_whole_half_up(number, place)
        stated = re.search(r"సుమారు ([0-9,]+) పుస్తకాలు", text)
        assert stated and int(stated.group(1).replace(",", "")) == answer, "B008 illustrative rounded value changed"
        lower, upper = number // place * place, (number // place + 1) * place
        expected = [number // place % 10, controlling_digit(number, place), number,
                    lower, upper, number-lower, upper-number, answer, number, answer]
        assert _numbers(text_of(paragraphs[1])) == expected, "B008 illustrative rounding reasoning changed"
    self_check = text_of(_node(ids, "B008-self-check-support"))
    for phrase in ("18 ఎంపిక గడులు ఖాళీగా", "స్వీయ అభిప్రాయం", "జవాబు పరీక్ష కాదు",
                   "స్వయంచాలక మార్కులు వేయదు", "వ్యక్తిగత సమాచారం పంపాల్సిన అవసరం లేదు"):
        assert phrase in self_check, "B008 self-report/non-autograding qualification changed"


def _check_place_unit_explanation(ids):
    # These are explanations, not three new assessed response parts.
    text = text_of(_node(ids, "B008-conventions"))
    for place_word, unit_word, value in (("పదుల", "పది", 10),
                                        ("వందల", "వంద", 100),
                                        ("వేల", "వెయ్యి", 1000)):
        match = re.search(re.escape(place_word + " స్థానానికి ఒక " + unit_word + " అంటే ")
                          + r"([0-9,]+)", text)
        assert match and _numbers(match.group(1)) == [value], "B008 one-place-unit amount changed"
    assert "సంఖ్యకు కేవలం 1 కలపడం కాదు" in text, "B008 place unit confused with adding one"


def validate_practice_bridge(target, bridge):
    """Require all actual displayed answers, parts, reasoning, and source links."""
    _, cases = source_cases()
    ids, source_ids = _ids(bridge), _ids(target)
    expected_details = {"B008-S-" + c["id"] for c in cases}
    actual_details = {ident for ident in ids if re.fullmatch(r"B008-S-fs-id[0-9]+", ident)}
    assert actual_details == expected_details, "B008 source-solution coverage changed"
    expected_parts = {"B008-S-" + c["id"] + "-" + p["label"] for c in cases
                      for p in c["parts"] if p["label"] != "single"}
    actual_parts = {ident for ident in ids if re.fullmatch(r"B008-S-fs-id[0-9]+-[a-e]", ident)}
    assert actual_parts == expected_parts, "B008 response-part coverage changed"
    for node in bridge.iter():
        if _local(node) == "a":
            href = node.get("href", "")
            assert href.startswith("#") and href[1:] in (set(ids) | set(source_ids)), "B008 dangling/foreign bridge link"
    _require_commas(text_of(bridge))
    for case in cases:
        detail = _node(ids, "B008-S-" + case["id"])
        assert _local(detail) == "details", "B008 source solution is not a details block"
        links = [e.get("href") for e in detail.iter() if _local(e) == "a"]
        assert links.count("#" + case["id"]) == 1, "B008 wrong source-question backlink: " + case["id"]
        summaries = _children(detail, "summary")
        assert len(summaries) == 1, "B008 solution summary missing/duplicated"
        summary = text_of(summaries[0])
        if case["kind"] == "membership":
            for part in case["parts"]:
                node = _node(ids, detail.get("id") + "-" + part["label"])
                assert _local(node) == "li" and node in list(detail.iter()), "B008 membership part misplaced"
                assert _numbers(_strong_answer(node)) == part["expected"], "B008 displayed membership answer changed"
                label = "సహజ సంఖ్యలు" if part["label"] == "a" else "పూర్ణాంకాలు"
                assert text_of(node).startswith(label + ":"), "B008 answer-set label changed"
        elif case["kind"] == "model":
            value = case["parts"][0]["expected"]
            assert _strong_answer(detail) == str(value), "B008 displayed model answer changed"
            h, t, o = case["counts"]
            _require_equation(detail, f"{h} × 100 + {t} × 10 + {o} × 1 = {h*100} + {t*10} + {o} = {value}")
        elif case["kind"] == "place":
            assert _numbers(summary) == [case["input"]], "B008 place source numeral changed"
            for part in case["parts"]:
                row = _node(ids, detail.get("id") + "-" + part["label"])
                cells = _children(row, "td")
                assert _local(row) == "tr" and row in list(detail.iter()) and len(cells) == 3, "B008 place row coverage changed"
                token = chr(ord("ⓐ") + ord(part["label"]) - ord("a"))
                assert text_of(cells[0]).startswith(token + " "), "B008 displayed part label changed"
                assert _numbers(text_of(cells[0])) == [part["digit"]], "B008 requested digit changed"
                expected = TE_PLACES[part["place"]] + " స్థానం (" + EN_PLACES[part["place"]] + ")"
                assert text_of(cells[1]) == expected, "B008 place-name answer changed"
                expected_equation = f"{part['digit']} × {part['place']:,} = {part['contribution']:,}"
                assert [_compact(e) for e in _equations(cells[2])] == [_compact(expected_equation)], "B008 contribution/digit/place equation changed"
            _require_groups(detail, case["input"], required=False)
        elif case["kind"] == "name":
            value = case["parts"][0]["input"]
            answer = _strong_answer(detail)
            assert _te_plain(answer) == _te_plain(TE_REVIEWED_NAMES[str(value)]["bridge"]), "B008 reviewed Telugu displayed name changed"
            english = [text_of(e) for e in detail if _local(e) == "p" and e.get("lang") == "en"]
            assert len(english) == 1, "B008 English name answer missing/duplicated"
            _require_name(english[0], value, case["unit"])
            _require_groups(detail, value)
            _require_sum(detail, value)
            if case["order"] <= 30:
                assert _numbers(summary) == [value], "B008 naming source input changed"
        elif case["kind"] == "digits":
            value = case["parts"][0]["expected"]
            assert _strong_answer(detail) == f"{value:,}", "B008 displayed written numeral changed"
            _require_groups(detail, value, required=value >= 1000)
            _require_sum(detail, value)
            if str(value) in TE_REVIEWED_SUMMARIES:
                assert _te_plain(summary.split(" · ")[0]) == _te_plain(TE_REVIEWED_SUMMARIES[str(value)]), "B008 reviewed Telugu question name changed"
        elif case["kind"] == "round":
            if case["order"] <= 50:
                assert _numbers(summary) == [p["input"] for p in case["parts"]], "B008 rounding source-pair changed"
                assert "దగ్గరి " + TE_NEAREST[case["parts"][0]["place"]] in summary, "B008 rounding summary target changed"
            for part in case["parts"]:
                node = _node(ids, detail.get("id") + "-" + part["label"])
                assert _local(node) == "li" and node in list(detail.iter()), "B008 rounding part misplaced"
                _check_round_part(node, part, case["unit"])
        elif case["kind"] == "open":
            assert len(case["parts"]) == 1 and case["parts"][0]["expected"] is None
        if case["order"] in (21, 22, 23, 24):
            last = text_of(_children(detail, "p")[-1])
            stem = {"feet": "అడుగుల", "hours": "గంటలు", "minutes": "నిమిషాలు"}[case["unit"]]
            assert stem in last, "B008 bridge named-quantity unit changed"
        if case["order"] in (39, 40, 41, 42):
            last = text_of(_children(detail, "p")[-1])
            value = case["parts"][0]["expected"]
            assert _numbers(last) == [value], "B008 repeated displayed answer changed"
            unit = {"people": "మంది", "years": "సంవత్సరాలు", "gallons": "గ్యాలన్లు", "USD": "డాలర్లు"}[case["unit"]]
            assert re.search(re.escape(f"{value:,}") + r"(?: అమెరికా)? " + unit, last), "B008 bridge numeric-quantity unit changed"
        if case["order"] in (29, 30):
            expected_date = [2016] if case["order"] == 29 else [1, 2014]
            assert _numbers(text_of(_children(detail, "p")[-1])) == expected_date, "B008 historical naming date changed"
    _require_equation(_node(ids, "B008-S-fs-id1341564"), "70 × 365 × 24 = 613,200")
    _require_equation(_node(ids, "B008-S-fs-id1300121"), "365 × 24 × 60 = 525,600")
    _check_direct_rounding(_node(ids, "B008-S-fs-id2792494"), 24493, 100, 1000)
    _check_direct_rounding(_node(ids, "B008-S-fs-id1604312"), 18549, 10, 100)
    _check_open_writing(ids)
    _check_place_unit_explanation(ids)
    equalities, relations = verify_practice_equalities(bridge)
    return {"source_bridge_solutions": len(expected_details),
            "bridge_response_parts": 96, "bridge_determined_parts": 94,
            "bridge_open_writing_parts": 2, "bridge_equalities": equalities,
            "bridge_equality_relations": relations}


def validate_b008(target, bridge):
    """Accept actual ElementTree roots, in target/bridge order; read-only."""
    return {**validate_practice_target(target), **validate_practice_bridge(target, bridge)}
