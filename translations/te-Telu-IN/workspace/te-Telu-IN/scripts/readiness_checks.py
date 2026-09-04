"""Author math validation of B011/B012 actual targets and bridge answers.

The author also wrote these two prose bridges. This finite validator is not
independent prose approval, an asset-author review, or a general Telugu parser.
It reads source/model data and checks displayed content, not catalog metadata.
"""
from hashlib import sha256
from pathlib import Path
import math
import re
import xml.etree.ElementTree as ET

from naming_checks import text_of
from writing_checks import english_value

BASE = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
MATH = "{http://www.w3.org/1998/Math/MathML}"
XH = "{http://www.w3.org/1999/xhtml}"
SVG = "{http://www.w3.org/2000/svg}"
MODEL_PATH = "assets/B011/CNX_BMath_Figure_01_02_001_img.te.svg"
SPECS = {
    "TE-B011": ("cdd73289f869830dcc51fb3df012c1b50d5ef191698dcfbea244d39dbc45cb83", 18, 8, 2, "fs-idm207409024", "fs-id2222880"),
    "TE-B012": ("9b680f02649625b9263c6fa2bc9aa9defaa93d94fec588ea203c7bbc7f291287", 13, 6, 1, "fs-idm218505136", "fs-id3202693"),
}
NUMBER = r"[0-9][0-9,]*"
EXPRESSION = NUMBER + r"(?:\s*[+×]\s*" + NUMBER + r")*"
RELATION = re.compile(r"(?<![\w.,])" + EXPRESSION + r"(?:\s*=\s*" + EXPRESSION + r")+(?![\d,]|\.[0-9])")


def _ids(root):
    all_ids = [e for e in root.iter() if e.get("id")]
    ids = {e.get("id"): e for e in all_ids}
    assert len(ids) == len(all_ids), "Duplicate readiness ID"
    return ids


def _node(ids, ident):
    assert ident in ids, "Missing readiness node: " + ident
    return ids[ident]


def _math_signature(root):
    return [(e.tag, tuple(sorted(e.attrib.items())), (e.text or "").strip())
            for e in root.iter() if e.tag.startswith(MATH)]


def _structure(root):
    ignored = {"alt", "{http://www.w3.org/XML/1998/namespace}lang"}
    rows = []
    for e in root.iter():
        attributes = {k: v for k, v in e.attrib.items() if k not in ignored}
        if e.tag == CN + "image":
            attributes.pop("src", None)
            attributes.pop("mime-type", None)
        rows.append((e.tag, tuple(sorted(attributes.items())), len(e)))
    return rows


def _source(unit, target):
    assert unit in SPECS, "Unsupported readiness unit"
    digest, elements, id_count, math_count, _, destination = SPECS[unit]
    raw = (BASE / "sources" / (unit + ".en.cnxml")).read_bytes()
    assert sha256(raw).hexdigest() == digest, "Readiness frozen source changed"
    source = ET.fromstring(raw)
    assert (len(list(source.iter())), len(_ids(source)), len(list(source.iter(MATH + "math")))) == (elements, id_count, math_count)
    assert _structure(target) == _structure(source), "Readiness source structure/attributes changed"
    assert _math_signature(target) == _math_signature(source), "Readiness source MathML changed"
    assert [e.attrib for e in target.iter(CN + "link")] == [{"target-id": destination, "document": "m81243"}], "Readiness source cross-module link changed"
    assert target.find(CN + "title") is None, "Readiness editorial title inserted into source"
    images = list(target.iter(CN + "image"))
    if unit == "TE-B011":
        assert len(images) == 1 and images[0].attrib == {"mime-type": "image/svg+xml", "src": MODEL_PATH}, "Readiness model asset mapping changed"
    else:
        assert not images, "Unexpected B012 source media"
    return source, _ids(target)


def model_counts(svg):
    """Count actual drawn cells/group geometry; do not trust manifest totals."""
    groups = list(svg.iter(SVG + "g"))
    expected = [("hundred", 100), ("hundred", 100), ("ten", 10)] + [("one", 1)] * 5
    assert len(groups) == len(expected), "Readiness model group count changed"
    for group, (kind, cells_expected) in zip(groups, expected):
        cells = list(group)
        assert len(cells) == cells_expected and all(e.tag == SVG + "rect" for e in cells), "Readiness drawn cell count changed"
        assert group.get("data-kind") == kind and group.get("data-value") == str(cells_expected), "Readiness group/unit role changed"
        assert all(float(c.get("width", 0)) == float(c.get("height", 0)) == 12 for c in cells), "Readiness cell scale changed"
        positions = {(float(c.get("x")), float(c.get("y"))) for c in cells}
        assert len(positions) == cells_expected, "Readiness duplicate cell geometry"
        xs = sorted({x for x, _ in positions}); ys = sorted({y for _, y in positions})
        assert len(xs) == (10 if cells_expected >= 10 else 1), "Readiness model width changed"
        assert len(ys) == (10 if cells_expected == 100 else 1), "Readiness model height changed"
        assert positions == {(x, y) for x in xs for y in ys}, "Readiness model grid has holes"
        assert all(b - a == 12 for axis in (xs, ys) for a, b in zip(axis, axis[1:])), "Readiness model cell gaps changed"
    labels = [text_of(e) for e in svg.iter(SVG + "text")]
    assert labels == ["వందలు", "hundreds", "పదులు", "tens", "ఒకట్లు", "ones"], "Readiness model labels/visible answer changed"
    sizes = [len(g) for g in groups]
    return tuple(sizes.count(n) for n in (100, 10, 1))


def _number(token):
    assert re.fullmatch(r"0|[1-9][0-9]*|[1-9][0-9]{0,2}(?:,[0-9]{3})+", token), "Invalid readiness integer/grouping: " + token
    return int(token.replace(",", ""))


def _expression_value(expression):
    return sum(math.prod(_number(n.strip()) for n in product.split("×"))
               for product in expression.split("+"))


def readiness_equalities(root):
    """Recompute every complete displayed addition/multiplication chain."""
    found = []
    for node in root.iter():
        if node.tag not in {XH + "p", XH + "li"}:
            continue
        if any(e is not node and e.tag in {XH + "p", XH + "li"} for e in node.iter()):
            continue
        for match in RELATION.finditer(text_of(node)):
            expression = match.group()
            values = [_expression_value(side) for side in expression.split("=")]
            assert len(set(values)) == 1, "Incorrect readiness equality: " + expression
            found.append(re.sub(r"\s+", "", expression))
    return found


def readiness_name_value(name):
    """Only this source's coefficient-thousand-remainder naming form."""
    groups = name.split(" thousand ")
    assert len(groups) == 2, "Readiness English scale/group changed"
    values = [english_value(group) for group in groups]
    assert 1 <= values[0] <= 999 and 1 <= values[1] <= 999, "Readiness English coefficient out of range"
    return values[0] * 1000 + values[1]


def _bridge_links(unit, target_ids, bridge):
    expected = {
        "TE-B011": [("#fs-idm207409024", None), ("TE-B002.html#fs-id2222880", "sources/TE-B002.en.cnxml"), ("TE-B002.html#fs-id1227376", "sources/TE-B002.en.cnxml")],
        "TE-B012": [("#fs-idm218505136", None), ("TE-B005.html#fs-id3202693", "sources/TE-B005.en.cnxml"), ("TE-B005.html#B005-R01", "translations/TE-B005.bridge.xhtml")],
    }[unit]
    actual = [e.get("href") for e in bridge.iter(XH + "a")]
    assert actual == [href for href, _ in expected], "Readiness source/practice bridge links changed"
    for href, path in expected:
        ids = target_ids if path is None else _ids(ET.parse(BASE / path).getroot())
        assert href.split("#")[1] in ids, "Readiness destination anchor missing: " + href


def validate_readiness(unit, target, bridge):
    """Validate actual ElementTree roots. B011 has five chains; B012 has three."""
    source, target_ids = _source(unit, target)
    ids = _ids(bridge)
    prefix = unit.replace("TE-", "")
    assert bridge.get("id") == prefix + "-bridge"
    assert len(ids) == (6 if unit == "TE-B011" else 5), "Readiness bridge ID coverage changed"
    assert len(list(bridge.iter(XH + "details"))) == 1, "Readiness source solution coverage changed"
    answer = _node(ids, prefix + "-S-" + SPECS[unit][4])
    assert "ఇవి మూలపాఠంలో భాగం కావు" in text_of(_node(ids, prefix + "-additions-note")), "Readiness original-support scope removed"
    _bridge_links(unit, target_ids, bridge)
    equalities = readiness_equalities(bridge)
    if unit == "TE-B011":
        counts = model_counts(ET.parse(BASE / MODEL_PATH).getroot())
        units = (100, 10, 1)
        contributions = tuple(c * u for c, u in zip(counts, units))
        value = sum(contributions)
        assert text_of(_node(target_ids, "fs-idm216142416")) == str(value), "Readiness model source answer changed"
        alt = _node(target_ids, "fs-id2778433").get("alt", "")
        assert re.findall(r"\d+", alt) == ["10", "10", "100", "10"], "Readiness model accessible unit counts changed"
        for phrase in ["చతురస్రాలు రెండు", "ఒక అడ్డ కడ్డీ", "విడిగా ఐదు చిన్న బ్లాకులు"]:
            assert phrase in alt, "Readiness model accessible group count changed"
        assert "ఏ సంఖ్యను సూచిస్తుంది?" in text_of(_node(target_ids, "fs-idm214637312")), "Readiness model question type changed"
        expected = [f"{c}×{u}={v}" for c, u, v in zip(counts, units, contributions)]
        expected += ["+".join(map(str, contributions)) + "=" + str(value), "+".join(map(str, counts)) + "=" + str(sum(counts))]
        assert equalities == expected, "Readiness model count/unit/contribution equation changed"
        assert [text_of(e) for e in answer.iter(XH + "strong")] == [str(value)], "Readiness displayed model answer changed"
        for li, phrase in zip(answer.findall(".//" + XH + "li"), ["వందల చతురస్రాలు రెండు", "పదుల కడ్డీ ఒకటి", "విడి చిన్న బ్లాకులు ఐదు"]):
            assert phrase in text_of(li), "Readiness block-type/count wording changed"
        total = text_of(_node(ids, "B011-total"))
        assert "రెండు వందల పదిహేను" in total and "వందలు, పదులు, ఒకట్ల స్థానాల్లో వరుసగా 2, 1, 5" in total, "Readiness model name/place order changed"
        contrast = text_of(_node(ids, "B011-count-versus-value"))
        assert "నమూనా సూచించే సంఖ్య 8 కాదు" in contrast and "అవన్నీ ఒకే విలువ గలవి కావు" in contrast, "Readiness shape count conflated with value"
    else:
        source_problem = _node(_ids(source), "fs-idm218825920")
        source_name = re.search(r"Write the number (.*?) using digits\?", text_of(source_problem)).group(1)
        value = readiness_name_value(source_name)
        problem = text_of(_node(target_ids, "fs-idm218825920"))
        target_name = re.search(r"మూల ఇంగ్లీషు పేరు: ([^.]+)\.", problem)
        assert target_name and target_name[1] == source_name, "Readiness source English number name changed"
        assert "మూడు వందల నలభై రెండు వేల ఆరు అనే సంఖ్యను అంకెలలో రాయండి" in problem, "Readiness Telugu source name/question changed"
        assert text_of(_node(target_ids, "fs-idm221421664")) == f"{value:,}", "Readiness zero-group source answer changed"
        assert [text_of(e) for e in answer.iter(XH + "strong")] == [f"{value:,}"], "Readiness displayed grouped answer changed"
        assert source_name in text_of(answer) and "మూడు వందల నలభై రెండు వేల ఆరు" in text_of(answer), "Readiness bridge source name changed"
        thousands, remainder = divmod(value, 1000)
        hundreds, tens, ones = remainder // 100, remainder // 10 % 10, remainder % 10
        expected = [f"{thousands}×1,000={thousands * 1000:,}", f"{hundreds}×100+{tens}×10+{ones}×1={remainder}", f"{thousands * 1000:,}+{remainder}={value:,}"]
        assert equalities == expected, "Readiness group coefficient/place equation changed"
        assert "వెయ్యి విలువగల 342 సమూహాలు" in text_of(answer), "Readiness coefficient count/unit wording changed"
        groups = re.findall(r"\d+\s*\|\s*\d+", text_of(answer))
        assert groups == ["342 | 006"], "Readiness zero-period width/order changed"
        assert "ఆ మూడు స్థానాల్లో 006 రాయాలి" in text_of(answer), "Readiness final-period zeros omitted"
        zero = text_of(_node(ids, "B012-zero-place"))
        for phrase in ["రెండు సున్నాలు వందల, పదుల స్థానాలను", "006 విలువ ఆరు; 600 విలువ ఆరు వందలు", "అంతర్జాతీయ మూడంకెల సమూహాల"]:
            assert phrase in zero, "Readiness zero-place/value/grouping explanation changed"
        assert "The groups are 342 and 006, giving 342,006" in text_of(bridge), "Readiness English grouped answer changed"
    return {"unit": unit, "source_answer": value, "displayed_equation_chains": len(equalities), "source_cross_module_links": 1, "bridge_links": 3}
