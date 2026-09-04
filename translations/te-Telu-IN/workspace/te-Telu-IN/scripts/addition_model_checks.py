"""Independent, finite B014 checks of source models and displayed reasoning.

The source pairs are read from the pinned CNXML. Counts are recomputed with
integer arithmetic; SVG cells are counted directly, never from manifest totals.
This is not a general Telugu parser or native-speaker/reader-layout approval.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import math
import re
import xml.etree.ElementTree as ET

from naming_checks import text_of

BASE = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
MATH = "{http://www.w3.org/1998/Math/MathML}"
XH = "{http://www.w3.org/1999/xhtml}"
SVG = "{http://www.w3.org/2000/svg}"
SOURCE_SHA = "b865a80cc39efa14f98ddd39d05d2ff688439978b39d9e153533254c9ad91352"
PREFIX = "CNX_BMath_Figure_01_02_"
EXERCISES = (
    ("fs-id1471255", "fs-id1969376", 2, 6, "worked"),
    ("fs-id2792546", "fs-id1833338", 3, 6, "try"),
    ("fs-id1886370", "fs-id1241970", 5, 1, "try"),
    ("fs-id1792383", "fs-id1471782", 5, 8, "worked"),
    ("fs-id2265162", "fs-id2140822", 5, 7, "try"),
    ("fs-id1863239", "fs-id2129995", 6, 8, "try"),
    ("fs-id1939376", "fs-id1966628", 17, 26, "worked"),
    ("fs-id2137714", "fs-id2483638", 15, 27, "try"),
    ("fs-id2813270", "fs-id2267850", 16, 29, "try"),
)
TRY_CASES = tuple(e for e in EXERCISES if e[-1] == "try")
EXTRA_CASES = {"D01": (2, 4), "D02": (7, 3), "D03": (18, 24),
               "R01": (4, 0), "R02": (6, 7), "R03": (27, 13)}
TABLES = {"eip-167": (2, 3, 2), "eip-951": (3, 3, 2),
          "eip-555": (2, 5, 2), "eip-93": (3, 5, 3)}
# Source order. Each stage lists (number of ten rods, groups of separate ones).
# These are pixel-witnessed stage counts, not copied manifest answer fields.
MODELS = {
    "019_img-02": ({"single": (0, (3,))}, ("3",)),
    "019_img-03": ({"single": (0, (3, 4))}, ("3", "4")),
    "019_img-04": ({"single": (0, (7,))}, ("7",)),
    "016_img-02": ({"single": (0, (2,))}, ("2",)),
    "016_img-03": ({"single": (0, (2, 6))}, ("2", "6")),
    "016_img-04": ({"single": (0, (8,))}, ("8",)),
    "006_img": ({"single": (0, (3, 6))}, ("3 + 6 = 9",)),
    "007_img": ({"single": (0, (5, 1))}, ("5 + 1 = 6",)),
    "017_img-02": ({"single": (0, (5,))}, ("5",)),
    "017_img-03": ({"single": (0, (5, 8))}, ("5", "8")),
    "017_img-04": ({"before": (0, (5, 5, 3)), "after": (1, (3,))}, ()),
    "010_img": ({"single": (1, (2,))}, ("5 + 7 = 12",)),
    "011_img": ({"single": (1, (4,))}, ("6 + 8 = 14",)),
    "018_img-02": ({"single": (1, (7,))}, ()),
    "018_img-03": ({"single": (2, (6,))}, ()),
    "018_img-04": ({"single": (3, (13,))}, ()),
    "018_img-05": ({"single": (4, (3,))}, ()),
    "014_img": ({"single": (4, (2,))}, ("15 + 27 = 42",)),
    "015_img": ({"single": (4, (5,))}, ("16 + 29 = 45",)),
}
ALT_CHECKS = {
    "019_img-02": ((3,), ("మూడు చిన్న",)),
    "019_img-03": ((3, 4), ("ఎడమ సమూహంలో మూడు", "కుడి సమూహంలో నాలుగు")),
    "019_img-04": ((7,), ("ఏడు చిన్న",)),
    "016_img-02": ((2,), ("రెండు చిన్న",)),
    "016_img-03": ((2, 6), ("ఎడమ సమూహంలో రెండు", "కుడి సమూహంలో ఆరు")),
    "016_img-04": ((8,), ("ఎనిమిది చిన్న",)),
    "006_img": ((3, 6, 9), ("మూడు ఒకట్ల", "ఆరు ఒకట్ల", "మొత్తం తొమ్మిది ఒకట్లు")),
    "007_img": ((5, 1, 6), ("ఐదు ఒకట్ల", "ఒక విడి బ్లాకు", "మొత్తం ఆరు ఒకట్లు")),
    "017_img-02": ((5,), ("ఐదు చిన్న",)),
    "017_img-03": ((5, 8), ("ఎడమ సమూహంలో ఐదు", "కుడి సమూహంలో ఎనిమిది")),
    "017_img-04": ((13,), ("ఐదు చొప్పున రెండు సమూహాల్లోని పది", "మరో మూడు బ్లాకులు బయట",
                              "పది బ్లాకుల స్థానంలో", "ఒక ఎరుపు పదుల కడ్డీ", "పక్కన మూడు విడి బ్లాకులు",
                              "రెండు నమూనాలూ13విలువనే", "కలిపి లెక్కించాల్సిన రెండు కొత్త సమూహాలు కావు")),
    "010_img": ((5, 7, 12, 5, 7), ("ఒక పదుల కడ్డీ", "రెండు విడి ఒకట్ల", "కలిపిన తరువాతి నమూనా")),
    "011_img": ((6, 8, 14, 6, 8), ("ఒక పదుల కడ్డీ", "నాలుగు విడి ఒకట్ల", "కలిపిన తరువాతి నమూనా")),
    "018_img-02": ((), ("ఎడమవైపు పది చిన్న గడులు గల ఒక పదుల కడ్డీ", "కుడివైపు ఏడు విడి ఒకట్ల")),
    "018_img-03": ((), ("ఎడమవైపు పది చిన్న గడులు చొప్పున గల రెండు పదుల కడ్డీలు", "కుడివైపు ఆరు విడి ఒకట్ల")),
    "018_img-04": ((), ("ఎడమవైపు పది చిన్న గడులు చొప్పున గల మూడు పదుల కడ్డీలు", "కుడివైపు పదమూడు విడి ఒకట్ల",
                         "పది బ్లాకులను ఎరుపుతో", "మరో మూడు బ్లాకులు మిగిలాయి")),
    "018_img-05": ((), ("ఎడమవైపు నాలుగు పదుల కడ్డీలు", "ముందు ఉన్న మూడు కడ్డీల కింద కొత్త ఎరుపు కడ్డీ",
                         "ప్రతి కడ్డీలో పది చిన్న గడులు", "కుడివైపు మూడు విడి ఒకట్ల")),
    "014_img": ((15, 27, 42, 40, 2), ("నాలుగు పదుల కడ్డీలు", "రెండు విడి ఒకట్ల", "నాలుగు పదుల విలువ40", "రెండు ఒకట్ల విలువ2")),
    "015_img": ((16, 29, 45, 40, 5, 45), ("నాలుగు పదుల కడ్డీలు", "ఐదు విడి ఒకట్ల", "నాలుగు పదుల విలువ40", "ఐదు ఒకట్ల విలువ5")),
}
TABLE_NUMBERS = {
    "eip-167": (3, 3, 4, 3, 4, 3, 4, 7),
    "eip-951": (2, 2, 2, 6, 2, 6, 8, 8, 2, 6, 8),
    "eip-555": (10, 5, 5, 5, 8, 13, 1, 3, 13, 5, 8, 13),
    "eip-93": (17, 1, 7, 26, 2, 6, 3, 13, 10, 1, 4, 3, 40, 3, 43, 17, 26, 43),
}
NUMBER = r"(?:0|[1-9][0-9]*)"
EXPRESSION = NUMBER + r"(?:\s*[+×−-]\s*" + NUMBER + r")*"
RELATION = re.compile(r"(?<![\w.,])" + EXPRESSION + r"(?:\s*=\s*" + EXPRESSION + r")+(?![\d,]|\.[0-9])")
PAIR = re.compile(r"(?<![\w,])(\d+)\s*\+\s*(\d+)(?![\d,])")


def _ids(root):
    nodes = [e for e in root.iter() if e.get("id")]
    ids = {e.get("id"): e for e in nodes}
    assert len(nodes) == len(ids), "Duplicate B014 ID"
    return ids


def _node(ids, ident):
    assert ident in ids, "Missing B014 node: " + ident
    return ids[ident]


def regroup(a, b):
    """Return counted states and conserved value for this two-digit model unit."""
    assert type(a) is type(b) is int and 0 <= a < 100 and 0 <= b < 100
    at, ao = divmod(a, 10)
    bt, bo = divmod(b, 10)
    before = (at + bt, ao + bo)
    carry, remaining = divmod(before[1], 10)
    after = (before[0] + carry, remaining)
    value = after[0] * 10 + after[1]
    assert before[0] * 10 + before[1] == value == a + b
    return {"addends": ((at, ao), (bt, bo)), "before": before,
            "carry": carry, "after": after, "value": value}


def _math_signature(root):
    return [(e.tag, tuple(sorted(e.attrib.items())), (e.text or "").strip())
            for e in root.iter() if e.tag.startswith(MATH)]


def _structure(root):
    ignored = {"alt", "aria-label", "{http://www.w3.org/XML/1998/namespace}lang"}
    signature = []
    for e in root.iter():
        attributes = {k: v for k, v in e.attrib.items() if k not in ignored}
        if e.tag == CN + "image":
            attributes.pop("src", None)
            attributes.pop("mime-type", None)
        signature.append((e.tag, tuple(sorted(attributes.items())), len(e)))
    return signature


def _problem_pair(problem):
    tokens = [(e.tag, (e.text or "").strip()) for e in problem.iter()
              if e.tag in {MATH + "mn", MATH + "mo"}]
    assert len(tokens) == 4 and [v for _, v in tokens][1::2] == ["+", "."], "B014 problem expression changed"
    assert tokens[0][0] == tokens[2][0] == MATH + "mn"
    return int(tokens[0][1]), int(tokens[2][1])


def source_cases():
    raw = (BASE / "sources/TE-B014.en.cnxml").read_bytes()
    assert sha256(raw).hexdigest() == SOURCE_SHA, "B014 frozen source changed"
    source = ET.fromstring(raw)
    assert (len(list(source.iter())), len(_ids(source)), len(list(source.iter(MATH + "math"))),
            len(list(source.iter(CN + "image")))) == (322, 86, 30, 19), "B014 source inventory changed"
    exercises = list(source.iter(CN + "exercise"))
    assert len(exercises) == len(EXERCISES)
    cases = []
    for node, (ident, solution, a, b, kind) in zip(exercises, EXERCISES):
        assert node.get("id") == ident, "B014 source exercise order changed"
        pair = _problem_pair(node.find(CN + "problem"))
        assert pair == (a, b), "B014 source pair changed"
        assert node.find(CN + "solution").get("id") == solution, "B014 original solution ID changed"
        cases.append((ident, a, b, regroup(*pair)["value"], kind))
    return source, tuple(cases)


def model_counts(svg, suffix):
    """Inspect actual rects/positions, stage separation, and visible labels."""
    assert suffix in MODELS
    expected, labels = MODELS[suffix]
    stages = {}
    positions = {}
    for group in svg.iter(SVG + "g"):
        kind, stage = group.get("data-kind"), group.get("data-stage")
        assert kind in {"ten", "ones"} and stage in expected, "B014 model group/stage changed"
        cells = list(group)
        assert cells and all(c.tag == SVG + "rect" for c in cells), "B014 drawn cells missing"
        assert all(c.get("width") == c.get("height") == "24" for c in cells), "B014 drawn unit scale changed"
        coords = [(float(c.get("x")), float(c.get("y"))) for c in cells]
        assert len(set(coords)) == len(coords), "B014 duplicate/overlapping drawn cells"
        assert group.get("data-count") == str(len(cells)), "B014 group metadata disagrees with actual cells"
        count = stages.setdefault(stage, [0, []])
        taken = positions.setdefault(stage, set())
        assert not taken.intersection(coords), "B014 overlapping groups"
        taken.update(coords)
        if kind == "ten":
            assert len(cells) == 10, "B014 rod must contain ten actual cells"
            assert len({y for _, y in coords}) == 1, "B014 rod is not one row"
            xs = sorted(x for x, _ in coords)
            assert all(b - a == 24 for a, b in zip(xs, xs[1:])), "B014 rod cells must be contiguous"
            count[0] += 1
        else:
            count[1].append(len(cells))
    actual = {stage: (tens, tuple(ones)) for stage, (tens, ones) in stages.items()}
    assert actual == expected, "B014 drawn model counts/states changed: " + suffix
    assert tuple(text_of(e) for e in svg.iter(SVG + "text")) == labels, "B014 visible model labels/answer changed: " + suffix
    desc = text_of(svg.find(SVG + "desc"))
    assert "ఒక చిన్న గడి విలువ 1; పది గడుల కడ్డీ విలువ 10." in desc, "B014 accessible model unit value changed"
    descriptions = re.findall(r"\((model|before|after)\): పదుల కడ్డీలు \(tens rods\) (\d+); ఒకట్ల బ్లాకులు \(ones\) ([\d +]+)\.", desc)
    expected_descriptions = [("model" if s == "single" else s, str(t), " + ".join(map(str, ones)))
                             for s, (t, ones) in actual.items()]
    assert descriptions == expected_descriptions, "B014 accessible stage counts disagree with drawn cells"
    label_text = re.findall(r"\(numeric labels\): ([^.]+)\.", desc)
    assert label_text == (["; ".join(labels)] if labels else []), "B014 accessible numeric labels changed"
    values = {stage: t * 10 + sum(ones) for stage, (t, ones) in actual.items()}
    if suffix == "017_img-04":
        assert values == {"before": 13, "after": 13}, "B014 exchange must conserve 13, not create 26"
        assert "Both stages represent 13; do not add the two stages." in text_of(svg.find(SVG + "desc")), "B014 model double-counting warning changed"
        assert any(e.get("data-role") == "exchange-enclosure" for e in svg), "B014 exchange enclosure missing"
        assert any(e.get("data-role") == "exchange-arrow" for e in svg), "B014 exchange arrow missing"
    if suffix.startswith("018_img-"):
        rods = [c for g in svg.iter(SVG + "g") if g.get("data-kind") == "ten" for c in g]
        ones = [c for g in svg.iter(SVG + "g") if g.get("data-kind") == "ones" for c in g]
        assert max(float(c.get("x")) + 24 for c in rods) < min(float(c.get("x")) for c in ones), "B014 actual rods must be LEFT of ones"
    return values


def _expression_value(expression):
    # Strict finite grammar: nonnegative integers, +, subtraction, and × only.
    # Evaluate products before addition/subtraction, without eval or rounding.
    assert re.fullmatch(EXPRESSION, expression.strip()), "Unsupported B014 arithmetic expression"
    parts = re.split(r"\s*([+−-])\s*", expression.strip())
    product = lambda p: math.prod(int(n.strip()) for n in p.split("×"))
    result = product(parts[0])
    for op, part in zip(parts[1::2], parts[2::2]):
        result += product(part) if op == "+" else -product(part)
    return result


def displayed_equalities(root):
    """Recompute complete visible equation chains, including tables and lists."""
    found = []
    block_tags = {XH + n for n in ("p", "li", "td", "dd", "summary")}
    for node in root.iter():
        if node.tag not in block_tags or any(e is not node and e.tag in block_tags for e in node.iter()):
            continue
        for match in RELATION.finditer(text_of(node)):
            expression = match.group()
            values = [_expression_value(side) for side in expression.split("=")]
            assert len(set(values)) == 1, "Incorrect B014 displayed equality: " + expression
            found.append(re.sub(r"\s+", "", expression))
    return found


def _compact(text):
    return re.sub(r"\s+", "", text)


def _phrases(text, phrases, context):
    compact = _compact(text)
    for phrase in phrases:
        assert _compact(phrase) in compact, "B014 " + context + " changed: " + phrase


def _target_prose(target):
    ids = _ids(target)
    _phrases(text_of(_node(ids, "fs-id1484984")), ["ఒక చిన్న బ్లాకు విలువ 1", "ఒక కడ్డీ విలువ 10"], "block/rod unit value")
    _phrases(text_of(_node(ids, "fs-id1567091")), ["కలిపే సంఖ్యలన్నిటికంటే పెద్దది 10"], "strict less-than-ten condition")
    _phrases(text_of(_node(ids, "fs-id1607848")), ["రెండు గణిత రాతల విలువలు సమానమని", "సమానత్వాన్ని తెలిపే వాక్యం (equation)"], "equation definition")
    _phrases(text_of(_node(ids, "fs-id1825926")), ["10 లేదా అంతకంటే ఎక్కువైతే", "10 బ్లాకుల స్థానంలో ఒక పదుల కడ్డీ"], "inclusive-ten exchange boundary")
    for ident, _, _, _, _ in EXERCISES:
        _phrases(text_of(_node(ids, ident).find(CN + "problem")), ["నమూనాతో చూపండి"], "source modeling request")
    _phrases(text_of(_node(ids, "fs-id1883656")), ["రెండు, ఆరు అనే సంఖ్యల మొత్తం", "కలిపే సంఖ్యలు 2 మరియు 6"], "worked addend roles")
    _phrases(text_of(_node(ids, "fs-id1171103442800")), ["ఐదు, ఎనిమిది అనే సంఖ్యల మొత్తం", "కలిపే సంఖ్యలు 5 మరియు 8"], "worked addend roles")
    _phrases(text_of(_node(ids, "eip-id2450011")), ["అంటే17,26అనే సంఖ్యల మొత్తం"], "two-digit addend roles")
    _phrases(text_of(_node(ids, "eip-571")), ["ఒకట్ల బ్లాకులు, పదుల కడ్డీలు", "ఒకట్లు మరియు పదులు", "ఈ సందర్భంలో వాటి అర్థం ఒకటే"], "ones/tens model shorthand")
    worksheet = _node(ids, "fs-id1171103645619")
    assert "Model Addition of Whole Numbers" in text_of(worksheet) and not list(worksheet.iter(CN + "link")), "B014 source worksheet title/link changed"
    for table in target.iter(CN + "table"):
        ident = table.get("id")
        _, rows, cols = TABLES[ident]
        label = table.get("aria-label", "")
        words = {2: "రెండు", 3: "మూడు", 5: "ఐదు"}
        _phrases(label, [words[rows] + " అడ్డ వరుసలు, " + words[cols] + " నిలువు వరుసలు"], "accessible table dimensions")
        assert tuple(map(int, re.findall(r"\d+", label))) == TABLE_NUMBERS[ident], "B014 accessible table quantities/order changed: " + ident
    rows = _node(ids, "eip-93").findall(".//" + CN + "row")
    expected_states = [*regroup(17, 26)["addends"], regroup(17, 26)["before"], regroup(17, 26)["after"]]
    for row, (tens, ones) in zip(rows[:4], expected_states):
        expected = f"{tens}{'పది' if tens == 1 else 'పదులు'},{ones}ఒకట్లు"
        assert _compact(text_of(row[1])).startswith(expected), "B014 two-digit displayed stage counts changed"
    _phrases(text_of(rows[3][0]), ["10ఒకట్ల స్థానంలో1పది"], "two-digit exchange size")
    _phrases(text_of(_node(ids, "eip-555").findall(".//" + CN + "row")[-1][0]), ["1పది,3ఒకట్లు", "వాటి విలువ13"], "single-digit regrouped model")
    for media, suffix in zip(target.iter(CN + "media"), MODELS):
        label = media.get("alt", "")
        numbers, phrases = ALT_CHECKS[suffix]
        assert tuple(map(int, re.findall(r"\d+", label))) == numbers, "B014 target alt numbers changed: " + suffix
        _phrases(label, phrases, "target alt model/side/quantity " + suffix)


def validate_model_target(target):
    source, cases = source_cases()
    assert _structure(source) == _structure(target), "B014 source structure/attributes changed"
    assert _math_signature(source) == _math_signature(target), "B014 source MathML changed"
    ids = _ids(target)
    for ident, (declared, row_count, actual_cols) in TABLES.items():
        table = _node(ids, ident)
        assert table.find(CN + "tgroup").get("cols") == str(declared), "B014 frozen table declaration changed"
        rows = table.findall(".//" + CN + "row")
        assert len(rows) == row_count and all(len(r.findall(CN + "entry")) == actual_cols for r in rows), "B014 actual table shape changed"
    raw_equation = _node(ids, "eip-555").findall(".//" + CN + "row")[-1][-1]
    assert text_of(raw_equation) == "5 + 8 = 13", "B014 non-MathML source equation changed"
    source_images = list(source.iter(CN + "image"))
    target_images = list(target.iter(CN + "image"))
    for original, image, suffix in zip(source_images, target_images, MODELS):
        assert Path(original.get("src")).stem == PREFIX + suffix
        expected = "assets/B014/" + PREFIX + suffix + ".te.svg"
        assert image.attrib == {"mime-type": "image/svg+xml", "src": expected}, "B014 source model/answer image mapping changed"
        model_counts(ET.parse(BASE / expected).getroot(), suffix)
    for node, (ident, solution, a, b, _) in zip(target.iter(CN + "exercise"), EXERCISES):
        assert node.get("id") == ident and node.find(CN + "solution").get("id") == solution
        assert _problem_pair(node.find(CN + "problem")) == (a, b)
    _target_prose(target)
    return cases


def _require_links(node, destinations):
    assert [e.get("href") for e in node.iter(XH + "a")] == ["#" + d for d in destinations], "B014 specific source/solution/routing link changed"


def _pairs(node):
    return [tuple(map(int, m.groups())) for m in PAIR.finditer(text_of(node))]


def _state_list(node):
    return [tuple(map(int, m)) for m in re.findall(r"(\d+)\s*(?:పదులు|పది)\s*[,;]\s*(\d+)\s*ఒకట్ల", text_of(node))]


EN_NUMBERS = {word: n for n, word in enumerate(("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"))}
EN_NUMBERS["forty"] = 40
EN_COUNTS = {"D01": [2, 4, 6, 10], "D02": [10, 1, 10, 0, 10],
    "D03": [1, 10, 8, 2, 4, 3, 12, 10, 4, 2], "R01": [0, 4],
    "R02": [13, 1, 10, 3, 10], "R03": [3, 10, 4, 0, 0, 40],
    "T01": [3, 6, 9], "T02": [5, 1, 6], "T03": [12, 1, 10, 2, 10, 2],
    "T04": [14, 1, 10, 4], "T05": [1, 10, 5, 2, 7, 3, 12, 10, 4, 2],
    "T06": [3, 15, 4, 5, 4, 40, 4]}
CASE_REASONS = {
    "D01": ["రెండు ఒకట్ల బ్లాకులు", "పక్కన నాలుగు ఒకట్ల", "పది ఒకట్లు లేవు"],
    "D02": ["ఏడు ఒకట్ల", "పక్కన మూడు ఒకట్ల", "వాటన్నిటి స్థానంలో1పదుల కడ్డీ", "పది ఒకట్లు సరిగ్గా ఉన్నా ఈ మార్పు చెల్లుతుంది", "విలువ ఒకటి అనకూడదు"],
    "D03": ["12ఒకట్లలో10ను కొత్త పదుల కడ్డీగా", "కొత్త పదిని ముందున్న పదులకు చేర్చాలి", "పది ఒకట్లను విడిగా మళ్లీ ఉంచకూడదు"],
    "R01": ["4ఒకట్ల బ్లాకులు", "రెండో సమూహానికి0", "అందులో బ్లాకులు ఉండవు", "అదనపు బ్లాకును గీయకండి", "కలిపినా4ఒకట్లే"],
    "R02": ["ఆరు ఒకట్ల బ్లాకుల పక్కన ఏడు", "10బ్లాకుల స్థానంలో1పదుల కడ్డీ", "మిగిలిన మూడు బ్లాకులనే"],
    "R03": ["ఆ పది ఒకట్ల స్థానంలో కొత్త పదుల కడ్డీ", "ఒకట్ల స్థానంలో0రాయాలి", "జవాబును కేవలం నాలుగు అని రాయకూడదు"],
    "T01": ["3ఒకట్ల బ్లాకులు, పక్కన6ఒకట్ల", "4,5,6,7,8,9", "పది కంటే తక్కువ కాబట్టి మార్పు అవసరం లేదు"],
    "T02": ["5ఒకట్ల బ్లాకులు, పక్కన1ఒకట్ల", "పది ఒకట్లు లేవు", "కొత్త బ్లాకు ముందున్న ఐదింటికి చేరుతుంది", "వాటి స్థానంలో రావడం కాదు"],
    "T03": ["5ఒకట్ల బ్లాకులు, పక్కన7ఒకట్ల", "మొదటి ఐదింటికి రెండో సమూహం నుంచి ఐదు", "రెండో సమూహంలో మరో రెండు", "10బ్లాకుల స్థానంలో1పదుల కడ్డీ"],
    "T04": ["6ఒకట్ల బ్లాకులు, పక్కన8ఒకట్ల", "మొదటి ఆరింటికి రెండో సమూహం నుంచి నాలుగు", "రెండో సమూహంలో మరో నాలుగు", "10బ్లాకుల స్థానంలో1పదుల కడ్డీ"],
    "T05": ["12ఒకట్లలో10బ్లాకులను కొత్త పదుల కడ్డీగా", "ముందున్న మూడు కడ్డీలకు అది చేరితే4పదులు"],
    "T06": ["15ఒకట్లలో10బ్లాకుల స్థానంలో కొత్త పదుల కడ్డీ", "విలువను నాలుగుగా తీసుకోకండి"],
}


def _solution(node, case, a, b):
    summary = node.find(XH + "summary")
    assert summary is not None and _pairs(summary) == [(a, b)], "B014 solution summary target pair changed"
    state = regroup(a, b)
    total = state["value"]
    equation = f"{a}+{b}={total}"
    assert [_compact(text_of(e)) for e in node.iter(XH + "strong")] == [equation], "B014 displayed final answer/operand order changed: " + case
    if a >= 10 or b >= 10:
        expected_states = [*state["addends"], state["before"], state["after"]]
        expected_equations = [f"{t * 10}+{o}={t * 10 + o}" for t, o in expected_states]
        if case == "T05":
            expected_states.append(state["after"])  # Repeated explicit final model.
    elif state["carry"]:
        expected_states = [state["before"], state["after"]]
        t, o = state["after"]
        expected_equations = [f"{t * 10}+{o}={total}"]
    else:
        expected_states = [state["after"]]
        expected_equations = []
    assert _state_list(node) == expected_states, "B014 displayed tens/ones stage counts changed: " + case
    expected_equations.append(equation)
    assert displayed_equalities(node) == expected_equations, "B014 solution place-value equations changed: " + case
    _phrases(text_of(node), CASE_REASONS[case], "model/exchange reasoning " + case)
    english = " ".join(text_of(e) for e in node.findall(XH + "p") if e.get("lang") == "en").lower()
    actual_counts = [EN_NUMBERS[w] for w in re.findall(r"\b(?:" + "|".join(EN_NUMBERS) + r")\b", english)]
    assert actual_counts == EN_COUNTS[case], "B014 English model counts/values changed: " + case
    return expected_equations


def validate_b014(target, bridge):
    """Validate actual ElementTree roots; return exact bounded coverage counts."""
    validate_model_target(target)
    ids, target_ids = _ids(bridge), _ids(target)
    assert bridge.get("id") == "B014-bridge"
    assert len(ids) == 33 and not (ids.keys() & target_ids.keys()), "B014 bridge ID coverage changed"
    expected_detail_ids = {"B014-S-" + c for c in EXTRA_CASES} | {f"B014-S-T{i:02d}" for i in range(1, 7)}
    assert {e.get("id") for e in bridge.iter(XH + "details")} == expected_detail_ids, "B014 source/entry/recheck solution coverage changed"
    all_links = list(bridge.iter(XH + "a"))
    assert len(all_links) == 20, "B014 bridge link count changed"
    for link in all_links:
        href = link.get("href", "")
        assert href.startswith("#") and href[1:] in (ids.keys() | target_ids.keys()), "B014 unresolved bridge link"
    all_equations = displayed_equalities(bridge)
    expected_all = []
    for case, (a, b) in EXTRA_CASES.items():
        question = _node(ids, "B014-" + case)
        assert _pairs(question) == [(a, b)], "B014 entry/recheck requested pair changed: " + case
        _phrases(text_of(question), ["చూపండి"], "entry/recheck model request")
        _require_links(question, ["B014-S-" + case])
        answer = _node(ids, "B014-S-" + case)
        expected_all.extend(_solution(answer, case, a, b))
    for i, (exercise, _, a, b, _) in enumerate(TRY_CASES, 1):
        case = f"T{i:02d}"
        answer = _node(ids, "B014-S-" + case)
        _require_links(answer, [exercise])
        expected_all.extend(_solution(answer, case, a, b))

    _require_links(_node(ids, "B014-route"), ["B014-" + role + str(i).zfill(2) if role == "R" else "B014-K" + str(i)
                    for i in range(1, 4) for role in ("K", "R")])
    _require_links(_node(ids, "B014-K2"), ["fs-id1792383"])
    _require_links(_node(ids, "B014-K3"), ["fs-id1939376"])
    _phrases(text_of(_node(ids, "B014-D02")), ["సరిగ్గా పది ఒకట్లు"], "exact-ten question target")
    _phrases(text_of(_node(ids, "B014-D03")), ["కలిపిన వెంటనే ఉన్న పదులు–ఒకట్లు", "మార్పు తరువాత ఉన్న పదులు–ఒకట్లు"], "two-stage question target")
    _phrases(text_of(_node(ids, "B014-R01")), ["రెండో కలిపే సంఖ్య", "మొత్తం విలువ మారుతుందా"], "zero question target")
    _phrases(text_of(_node(ids, "B014-R02")), ["మార్చిన బ్లాకుల సంఖ్య"], "exchange question target")
    _phrases(text_of(_node(ids, "B014-R03")), ["విడి ఒకట్లు మిగలకపోతే", "ఒకట్ల స్థానంలో"], "zero-remainder question target")

    k1, k2, k3 = (_node(ids, "B014-K" + str(i)) for i in range(1, 4))
    support_equations = [["3+4=7", "10+7=17", "3+4=7"], ["10+3=13", "5+8=13"],
        ["10+7=17", "20+6=26", "30+13=43", "40+3=43", "30+13=40+3=43", "17+26=43"]]
    for section, equations in zip((k1, k2, k3), support_equations):
        assert displayed_equalities(section) == equations, "B014 unscored support equations changed"
        expected_all.extend(equations)
    _phrases(text_of(k1), ["మొదటి సమూహాన్ని చెరిపి దాని స్థానంలో రెండోదాన్ని గీయకూడదు", "ప్రతి కడ్డీని ఒక్క ఒకట్ల బ్లాకుగా లెక్కించకండి", "ఒక కడ్డీ, ఏడు విడి బ్లాకులు ఎనిమిది వస్తువులు", "రెండు వైపుల విలువలు సమానమని"], "unit/count/equality support")
    _phrases(text_of(k2), ["సరిగ్గా10బ్లాకులను", "పది విడి బ్లాకులను తీసివేసి, వాటి స్థానంలో ఒక పదుల కడ్డీ", "మూడు విడి బ్లాకులు మిగులుతాయి"], "value-preserving exchange support")
    _phrases(text_of(_node(ids, "B014-state-warning")), ["వాటిని రెండు వేరు మొత్తాలుగా కలిపి లెక్కించవద్దు", "పది విడి బ్లాకులను మళ్లీ లెక్కించకండి", "సూచించే విలువ మాత్రం మారదు"], "double-counting warning")
    _phrases(text_of(_node(ids, "B014-ten-boundary")), ["సరిగ్గా10ఒకట్లు ఉన్నా మార్పు చేయవచ్చు", "10కంటే ఎక్కువ కావాల్సిన అవసరం లేదు", "విడి ఒకట్లు0ఉంటాయి", "పది కంటే తక్కువ ఒకట్లు ఉంటే ఈ మార్పు చేయలేము", "ఎరుపు రంగు అదనపు విలువ ఇవ్వదు"], "inclusive-ten/zero/color boundary")
    _phrases(text_of(k3), ["మూడు కడ్డీల విలువ30,మూడు కాదు", "ముందున్న3పదులకు కొత్త1పది చేరితే4పదులు", "13ఒకట్లలో10ను మార్చాం కాబట్టి3ఒకట్లు", "చివరి రెండు వరుసలు ఒకే మొత్తం విలువకు రెండు దశలు", "వాటిని మళ్లీ కలిపి లెక్కించకూడదు", "పక్కపక్కన రాసి కొత్త సంఖ్యగా చదవడం సరైన పద్ధతి కాదు"], "two-digit count/value/carry support")
    table = k3.find(XH + "table")
    _phrases(text_of(table.find(XH + "caption")), ["రెండు కలిపే సంఖ్యల నుంచి చివరి నమూనా వరకు"], "distinct addend/combined-stage caption")
    rows = table.findall(XH + "tbody/" + XH + "tr")
    assert len(rows) == 4 and all(len(row) == 4 for row in rows), "B014 bridge model table shape changed"
    assert [text_of(e) for e in table.findall(XH + "thead/" + XH + "tr/" + XH + "th")] == ["దశ", "పదుల కడ్డీల సంఖ్య", "విడి ఒకట్ల సంఖ్య", "ఆ నమూనా విలువ"], "B014 model table column roles changed"
    assert [text_of(r[0]) for r in rows] == ["మొదటి కలిపే సంఖ్య", "రెండో కలిపే సంఖ్య", "రెండింటినీ కలిపాక, మార్పుకు ముందు", "పది ఒకట్లను ఒక పదిగా మార్చాక"], "B014 model table stage roles changed"
    state = regroup(17, 26)
    for row, (t, o) in zip(rows, [*state["addends"], state["before"], state["after"]]):
        assert [text_of(row[1]), text_of(row[2])] == [str(t), str(o)], "B014 bridge model table counts changed"
        assert _compact(text_of(row[3])) == f"{t * 10}+{o}={t * 10 + o}", "B014 bridge model table place contribution changed"
    _phrases(text_of(_node(ids, "B014-additions-note")), ["ఇవి మూలపాఠంలో భాగం కావు"], "original-support scope")
    _phrases(text_of(_node(ids, "B014-materials")), ["విలువ1", "విలువ10", "రంగు మారినా ఆ విలువ మారదు"], "materials unit value")
    _phrases(text_of(_node(ids, "B014-task-convention")), ["ప్రతి కలిపే సంఖ్యకు నమూనా చూపి", "మొత్తం విలువను సమానత్వంతో రాయాలి"], "modeling task scope")
    _phrases(text_of(_node(ids, "B014-activity-boundary")), ["వర్క్‌షీట్ జతచేయలేదు", "లింకూ ఇవ్వలేదు", "ఆ వర్క్‌షీట్ అనువాదమో", "ధృవీకరణో కావు"], "worksheet acquisition/completion scope")
    assert Counter(all_equations) == Counter(expected_all) and len(all_equations) == 43, "B014 complete displayed equation coverage changed"
    return {"source_pairs": 10, "source_exercises": 9, "source_try_its": 6,
            "original_entry_rechecks": 6, "model_assets": 19, "original_solution_ids": 9,
            "bridge_solution_details": 12, "displayed_equation_chains": len(all_equations)}
