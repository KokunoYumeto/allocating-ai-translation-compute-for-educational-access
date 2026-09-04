"""Finite, read-only B015 arithmetic checks of actual source/target/bridge.

Integer column arithmetic is independently derived from the frozen problems.
The source's intermediate 0814 and delayed carry marker are preserved, not
silently repaired. This is not a general Telugu parser or visual/native review.
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
SOURCE_SHA = "8fc54e5e660bd66b25739144d64fd172a61da3b1407449c1ed066dde75c5034b"
PREFIX = "CNX_BMath_Figure_01_02_"
# Source order: exercise ID, original solution ID, kind, ordered problem parts.
EXERCISES = (
    ("fs-id2323927", "fs-id4363730", "worked", ((0, 11), (42, 0))),
    ("fs-id1264596", "fs-id2144870", "try", ((0, 19), (39, 0))),
    ("fs-id2362020", "fs-id2788980", "try", ((0, 24), (57, 0))),
    ("fs-id2454866", "fs-id1824208", "worked", ((8, 7), (7, 8))),
    ("fs-id1968047", "fs-id2170740", "try", ((9, 7), (7, 9))),
    ("fs-id1577590", "fs-id1806629", "try", ((8, 6), (6, 8))),
    ("fs-id1578501", "fs-id1791758", "worked", ((28, 61),)),
    ("fs-id2325520", "fs-id2284818", "try", ((32, 54),)),
    ("fs-id1275335", "fs-id2951285", "try", ((25, 74),)),
    ("fs-id2325655", "fs-id2566312", "worked", ((43, 69),)),
    ("fs-id2758260", "fs-id2215223", "try", ((35, 98),)),
    ("fs-id1826280", "fs-id1408807", "try", ((72, 89),)),
    ("fs-id2277302", "fs-id2150007", "worked", ((324, 586),)),
    ("fs-id1462931", "fs-id1302654", "try", ((456, 376),)),
    ("fs-id2267936", "fs-id2146728", "try", ((269, 578),)),
    ("fs-id2144790", "fs-id1372016", "worked", ((1683, 479),)),
    ("fs-id2174738", "fs-id2173908", "try", ((4597, 685),)),
    ("fs-id1367785", "fs-id1362543", "try", ((5837, 695),)),
    ("fs-id2264879", "fs-id2338420", "worked", ((21357, 861, 8596),)),
    ("fs-id2224340", "fs-id2924594", "try", ((46195, 397, 6281),)),
    ("fs-id1406185", "fs-id1351725", "try", ((53762, 196, 7458),)),
)
TRY_CASES = tuple(e for e in EXERCISES if e[2] == "try")
WORKED_CASES = tuple(e for e in EXERCISES if e[2] == "worked")
# Declared columns, actual rows, actual columns. Eight known source defects.
TABLES = {"fs-id2300206": (11, 11, 11), "eip-629": (2, 2, 2),
    "eip-id1168287208889": (3, 3, 2), "eip-id1168288224694": (3, 3, 2),
    "eip-id11688224694": (3, 3, 2), "eip-id1168288293873": (3, 2, 2),
    "eip-id1168287505854": (3, 4, 2), "eip-id1168287251210": (3, 4, 2),
    "eip-id1168288687380": (3, 6, 2), "eip-id1168288531101": (3, 7, 2)}
ASSETS = ("001", "020-01", "020-02", "020-03", "020-04")
MEDIA_IDS = ("fs-id1231518", "eip-id1168289818410", "eip-id1168287268641",
             "eip-id1168287196613", "eip-id1168287121476")
ACCESSIBLE_NUMBERS = {
    "eip-629": ("0", "11", "11", "42", "0", "42"),
    "eip-id1168287208889": ("2", "3", "5", "3", "2", "5", "4", "7", "11", "7", "4", "11", "8", "9", "17", "9", "8", "17"),
    "eip-id1168288224694": ("8", "7", "15"), "eip-id11688224694": ("7", "8", "15"),
    "eip-id1168288293873": ("28", "61", "8", "1", "9", "2", "6", "8", "89"),
    "eip-id1168287505854": ("43", "69", "12", "2", "1", "1", "4", "6", "11", "112"),
    "eip-id1168287251210": ("324", "586", "0", "1", "1", "1", "9", "910"),
    "eip-id1168288687380": ("1,683", "479", "2", "62", "162", "2,162"),
    "eip-id1168288531101": ("21,357", "861", "8,596", "14", "21", "18", "10", "3", "4", "14", "814", "0814", "2", "30,814"),
    "fs-id1231518": ("17", "26", "17", "7", "26", "6", "10", "4", "3", "17", "26", "43", "17", "26", "43", "17", "1", "1", "1", "1", "2", "4"),
    "eip-id1168289818410": ("324", "586"),
    "eip-id1168287268641": ("324", "586", "4", "6", "10", "0", "1", "1", "324", "2"),
    "eip-id1168287196613": ("324", "586", "324", "3", "1", "2", "1", "10"),
    "eip-id1168287121476": ("324", "586", "910", "324", "3", "2", "1"),
}
NUMBER = r"(?:[1-9][0-9]{0,2}(?:,[0-9]{3})+|0|[1-9][0-9]*)"
EXPRESSION = NUMBER + r"(?:\s*[+×−-]\s*" + NUMBER + r")*"
RELATION = re.compile(r"(?<![0-9A-Za-z_.,])" + EXPRESSION + r"(?:\s*=\s*" + EXPRESSION + r")+(?![0-9]|,[0-9]|\.[0-9])")
ADDITION = re.compile(r"(?<![0-9A-Za-z_.,])" + NUMBER + r"(?:\s*\+\s*" + NUMBER + r")+")
PLACES = {1: "ఒకట్ల", 10: "పదుల", 100: "వందల", 1000: "వేల", 10000: "పది వేల"}
EXTRA_CASES = {"D01": ((0, 68), (68, 0)), "R01": ((73, 0), (0, 73)),
    "D02": ((306, 42),), "R02": ((504, 35),), "D03": ((497, 8),),
    "R03": ((998, 7),), "D04": ((76, 87, 59),), "R04": ((58, 76, 89),)}
DECOMPOSITIONS = {"fs-id1968047": "9+1+6=16", "fs-id1577590": "8+2+4=14"}
# Repeated equations in the explanatory paragraph, in addition to table rows.
FOOTER_COLUMNS = {"fs-id2758260": (10,), "fs-id1826280": (10,),
    "fs-id1462931": (10, 100), "fs-id2267936": (10, 100), "fs-id1367785": (1000,),
    "fs-id2224340": (10,), "fs-id1406185": (10, 100),
    "D03": (10, 100), "D04": (10,), "R04": (10,)}


def ids_of(root):
    nodes = [n for n in root.iter() if n.get("id")]
    ids = {n.get("id"): n for n in nodes}
    assert len(nodes) == len(ids), "Duplicate B015 ID"
    return ids


def compact(value):
    return re.sub(r"\s+", "", value)


def phrases(node, required, context):
    actual = compact(text_of(node) if not isinstance(node, str) else node)
    for phrase in required:
        assert compact(phrase) in actual, "B015 " + context + " changed: " + phrase


def integer(value):
    assert re.fullmatch(NUMBER, value), "Invalid B015 whole-number grouping: " + value
    return int(value.replace(",", ""))


def column_steps(addends):
    """All decimal columns, including a new final column when carry remains."""
    assert len(addends) >= 2 and all(type(a) is int and a >= 0 for a in addends)
    width = max(len(str(a)) for a in addends)
    rows, carry, position = [], 0, 0
    while position < width or carry:
        unit = 10 ** position
        digits = tuple((a // unit) % 10 for a in addends)
        total = sum(digits) + carry
        outgoing, digit = divmod(total, 10)
        rows.append({"unit": unit, "digits": digits, "incoming": carry,
                     "total": total, "digit": digit, "outgoing": outgoing,
                     "partial": str(sum(addends) % (unit * 10)).zfill(position + 1)})
        carry, position = outgoing, position + 1
    assert sum(r["digit"] * r["unit"] for r in rows) == sum(addends)
    return tuple(rows)


def problem_parts(problem):
    result = []
    for m in problem.iter(MATH + "math"):
        tokens = [(n.tag, (n.text or "").strip()) for n in m.iter()
                  if n.tag in {MATH + "mn", MATH + "mo"}]
        if tokens[-1] == (MATH + "mo", "."):
            tokens.pop()
        assert len(tokens) >= 3 and len(tokens) % 2 == 1, "B015 problem arity changed"
        assert all(t == MATH + "mn" for t, _ in tokens[::2])
        assert all(t == MATH + "mo" and v == "+" for t, v in tokens[1::2]), "B015 problem operation changed"
        result.append(tuple(integer(v) for _, v in tokens[::2]))
    return tuple(result)


def _math_signature(root):
    return [(n.tag, tuple(sorted(n.attrib.items())), (n.text or "").strip())
            for n in root.iter() if n.tag.startswith(MATH)]


def _structure(root):
    ignored = {"alt", "aria-label", "summary", "{http://www.w3.org/XML/1998/namespace}lang"}
    result = []
    for n in root.iter():
        attributes = {k: v for k, v in n.attrib.items() if k not in ignored}
        if n.tag == CN + "image":
            attributes.pop("src", None); attributes.pop("mime-type", None)
        result.append((n.tag, tuple(sorted(attributes.items())), len(n)))
    return result


def addition_table(root):
    table = ids_of(root)["fs-id2300206"]
    group = table.find(CN + "tgroup")
    headers = group.findall(CN + "thead/" + CN + "row/" + CN + "entry")
    assert [text_of(e) for e in headers] == ["+"] + list(map(str, range(10))), "B015 addition-table header changed"
    rows = group.findall(CN + "tbody/" + CN + "row")
    assert len(rows) == 10, "B015 addition-table row count changed"
    for a, row in enumerate(rows):
        cells = row.findall(CN + "entry")
        assert len(cells) == 11 and text_of(cells[0]) == str(a), "B015 addition-table row header changed"
        for b, cell in enumerate(cells[1:]):
            assert text_of(cell) == str(a + b), f"B015 addition-table sum changed: row{a} column{b}"
    return 100


def expression_value(expression):
    assert re.fullmatch(EXPRESSION, expression.strip()), "Unsupported B015 arithmetic expression"
    parts = re.split(r"\s*([+−-])\s*", expression.strip())
    product = lambda p: math.prod(integer(n.strip()) for n in p.split("×"))
    value = product(parts[0])
    for op, part in zip(parts[1::2], parts[2::2]):
        value += product(part) if op == "+" else -product(part)
    return value


def checked_relation(expression):
    sides = expression.split("=")
    assert len(sides) >= 2
    values = [expression_value(s) for s in sides]
    assert len(set(values)) == 1, "Incorrect B015 displayed equality: " + expression
    return compact(expression)


def displayed_equalities(root):
    """Inspect leaf prose blocks once, including complete chained equalities."""
    found = []
    blocks = {XH + t for t in ("p", "li", "td", "th", "dd", "summary", "caption")}
    for node in root.iter():
        if node.tag not in blocks or any(n is not node and n.tag in blocks for n in node.iter()):
            continue
        found.extend(checked_relation(m.group()) for m in RELATION.finditer(text_of(node)))
    return found


def horizontal_math(root):
    """Only non-layout numeric MathML; carry-over layout is parsed separately."""
    found = []
    for m in root.iter(MATH + "math"):
        if any(n.tag in {MATH + "mtable", MATH + "mover", MATH + "mi"} for n in m.iter()):
            continue
        value = " ".join((n.text or "").strip() for n in m.iter()
                         if n.tag in {MATH + "mn", MATH + "mo"})
        for part in value.split(";"):
            part = part.strip().rstrip(".").strip()
            if "=" in part:
                found.append(checked_relation(part))
    return found


def column_frame(table):
    """Read main digits independently of mover annotations; retain carry places."""
    rows = [r for r in table.findall(MATH + "mtr") if len(r)]
    values, carries = [], {}
    for row_number, row in enumerate(rows):
        assert len(row) == 1, "B015 vertical arithmetic row width changed"
        pieces, markers = [], []

        def walk(n):
            if n.tag == MATH + "mover":
                assert len(n) == 2 and n[1].tag == MATH + "mn"
                offset = len("".join(pieces).replace(",", ""))
                walk(n[0])
                markers.append((offset, integer(n[1].text.strip())))
            elif n.tag == MATH + "mn":
                pieces.append((n.text or "").strip())
            else:
                for child in n:
                    walk(child)
        walk(row[0])
        value = "".join(pieces)
        assert value and re.fullmatch(r"[0-9,]+", value)
        values.append(value)
        for offset, carry in markers:
            assert row_number == 0, "B015 carry moved off first addend"
            unit = 10 ** (len(value.replace(",", "")) - offset - 1)
            assert unit not in carries
            carries[unit] = carry
    return tuple(values), carries


def source_column_frames(root):
    ids = ids_of(root)
    specs = {"eip-id1168288293873": ((28, 61), (None, "89")),
             "eip-id1168287505854": ((43, 69), (None, "2", "112")),
             "eip-id1168288687380": ((1683, 479), (None, "2", "62", "162", "2,162")),
             "eip-id1168288531101": ((21357, 861, 8596), (None, "4", "14", "814", "0814", "30,814"))}
    count = 0
    for ident, (addends, partials) in specs.items():
        frames = list(ids[ident].iter(MATH + "mtable"))
        assert len(frames) == len(partials), "B015 vertical stage coverage changed"
        steps = column_steps(addends)
        for stage, (frame, partial) in enumerate(zip(frames, partials)):
            values, carries = column_frame(frame)
            expected_values = tuple(format(n, ",") for n in addends)
            if partial is not None:
                expected_values += (partial,)
            assert values == expected_values, "B015 main digits/partial result changed: " + ident
            if stage == 0:
                expected_carries = {}
            elif ident == "eip-id1168288293873":
                expected_carries = {}
            elif ident == "eip-id1168287505854":
                expected_carries = {10: 1}  # Final 11 tens are written together.
            else:
                processed = min(stage, len(str(max(addends))) - 1)
                expected_carries = {r["unit"] * 10: r["outgoing"] for r in steps[:processed] if r["outgoing"]}
                if ident == "eip-id1168288687380" and stage == 3:
                    expected_carries.pop(1000)  # Exact frozen delayed-marker quirk.
            assert carries == expected_carries, "B015 carry place/count changed: " + ident
            if partial is not None:
                if stage == len(partials) - 1:
                    assert integer(partial) == sum(addends), "B015 vertical final sum changed"
                else:
                    assert partial == steps[stage - 1]["partial"], "B015 partial place/zero changed"
            count += 1
    return count


def source_cases():
    raw = (BASE / "sources/TE-B015.en.cnxml").read_bytes()
    assert sha256(raw).hexdigest() == SOURCE_SHA, "B015 frozen source changed"
    source = ET.fromstring(raw)
    assert (len(list(source.iter())), len(ids_of(source)), len(list(source.iter(MATH + "math"))),
            len(list(source.iter(CN + "image")))) == (1480, 163, 135, 5), "B015 source inventory changed"
    nodes = list(source.iter(CN + "exercise"))
    assert len(nodes) == len(EXERCISES)
    cases = []
    for node, (ident, solution_id, kind, expected_parts) in zip(nodes, EXERCISES):
        assert node.get("id") == ident, "B015 source exercise order changed"
        solution = node.find(CN + "solution")
        assert solution.get("id") == solution_id, "B015 original solution ID changed"
        parts = problem_parts(node.find(CN + "problem"))
        assert parts == expected_parts, "B015 source problem parts changed"
        answers = tuple(sum(p) for p in parts)
        for p in parts:
            column_steps(p)
        if kind == "try" or ident == "fs-id2323927":
            expected = ["+".join(format(n, ",") for n in p) + "=" + format(sum(p), ",") for p in parts]
            assert horizontal_math(solution) == expected, "B015 source supplied Try It answer incorrect"
        if ident == "fs-id2454866":
            tables = list(solution.iter(CN + "table"))
            assert len(tables) == len(parts)
            for table, part in zip(tables, parts):
                maths = list(table.iter(MATH + "math"))
                assert len(maths) == 2
                assert compact(text_of(maths[0])) == "+".join(map(str, part))
                assert text_of(maths[1]) == str(sum(part)), "B015 commutative worked answer incorrect"
        cases.append((ident, kind, parts, answers))
    assert len(cases) == 21 and sum(len(c[2]) for c in cases) == 27
    addition_table(source)
    horizontal_math(source)
    source_column_frames(source)
    return source, tuple(cases)


def svg_arithmetic(svg, suffix):
    """Check real text positions/cells, not declared answer metadata alone."""
    assert suffix in ASSETS
    addends = (17, 26) if suffix == "001" else (324, 586)
    width = len(str(max(addends)))
    places = ("ones", "tens", "hundreds")[:width]
    actual, coordinates = {}, {}
    for n in svg.iter(SVG + "text"):
        if n.get("data-role") == "digit":
            key = (n.get("data-row"), n.get("data-place"))
            assert key not in actual and key[0] in {"first", "second", "sum"} and key[1] in places
            assert re.fullmatch(r"[0-9]", text_of(n)), "B015 SVG visible digit changed"
            actual[key] = int(text_of(n)); coordinates[key] = (float(n.get("x")), float(n.get("y")))
    expected = {(row, place): (value // 10 ** i) % 10 for row, value in zip(("first", "second"), addends)
                for i, place in enumerate(places)}
    stage = 3 if suffix == "001" else int(suffix[-1]) - 1
    result_digits = width if suffix == "001" else stage
    for i, place in enumerate(places[:result_digits]):
        expected[("sum", place)] = (sum(addends) // 10 ** i) % 10
    assert actual == expected, "B015 SVG operand/result digit or stage changed: " + suffix
    xs = {p: coordinates[("first", p)][0] for p in places}
    assert all(xs[a] > xs[b] for a, b in zip(places, places[1:])), "B015 SVG place order changed"
    for (row, place), (x, y) in coordinates.items():
        assert x == xs[place], "B015 SVG unequal-length place alignment changed"
    ys = {row: {y for (r, _), (_, y) in coordinates.items() if r == row} for row in ("first", "second", "sum")}
    assert len(ys["first"]) == len(ys["second"]) == 1 and len(ys["sum"]) == (1 if result_digits else 0)
    assert min(ys["first"]) < min(ys["second"])
    if result_digits:
        assert min(ys["second"]) < min(ys["sum"])
    carries = {}
    for n in svg.iter(SVG + "text"):
        if n.get("data-role") == "carry":
            place = n.get("data-place")
            assert place in places and place not in carries
            assert float(n.get("x")) == xs[place] and float(n.get("y")) < min(ys["first"]), "B015 SVG carry not above target place"
            assert float(n.get("font-size")) < float(next(e for e in svg.iter(SVG + "text") if e.get("data-role") == "digit").get("font-size"))
            carries[place] = integer(text_of(n))
    expected_carries = {"tens": 1} if suffix == "001" else ({p: 1 for p in places[1:min(stage, 2) + 1]} if stage else {})
    assert carries == expected_carries, "B015 SVG carry count/place changed"
    rules = [n for n in svg.iter(SVG + "line") if n.get("data-role") == "sum-rule"]
    assert len(rules) == 1 and float(rules[0].get("y1")) > min(ys["second"]), "B015 SVG rule is not below addends"
    if result_digits:
        assert float(rules[0].get("y1")) < min(ys["sum"])
    assert [text_of(n) for n in svg.iter(SVG + "text") if n.get("data-role") == "plus"] == ["+"]
    if suffix == "001":
        counts = {}
        positions = set()
        for g in svg.iter(SVG + "g"):
            assert g.get("data-role") == "block-group" and g.get("data-kind") in {"ten", "ones"}
            stage_name = g.get("data-stage")
            assert stage_name in {"before-17", "before-26", "after"}
            cells = list(g)
            assert cells and all(n.tag == SVG + "rect" and n.get("width") == n.get("height") == "22" for n in cells)
            coords = [(float(n.get("x")), float(n.get("y"))) for n in cells]
            assert len(set(coords)) == len(coords) and not positions.intersection(coords), "B015 overlapping model units"
            positions.update(coords)
            count = counts.setdefault(stage_name, [0, 0])
            if g.get("data-kind") == "ten":
                assert len(cells) == 10 and len({y for _, y in coords}) == 1, "B015 rod does not have ten cells"
                x = sorted(x for x, _ in coords)
                assert all(b - a == 22 for a, b in zip(x, x[1:]))
                count[0] += 1
            else:
                count[1] += len(cells)
        assert counts == {"before-17": [1, 7], "before-26": [2, 6], "after": [4, 3]}, "B015 before/after model values changed"
        assert [text_of(n) for n in svg.iter(SVG + "text") if n.get("data-role") == "operand-label"] == ["17", "+ 26"]
        assert [compact(text_of(n)) for n in svg.iter(SVG + "text") if n.get("data-role") == "carry-equation"] == ["1+1+2=4"], "B015 carry callout changed"
        for role in ("model-arrow", "callout-arrow"):
            assert len([n for n in svg.iter(SVG + "path") if n.get("data-role") == role]) == 1
    if suffix in {"020-03", "020-04"}:
        phrases(text_of(svg.find(SVG + "desc")), ["not fractions"], "SVG carry/fraction interpretation")
    return sum(addends)


def validate_algorithm_target(target):
    source, cases = source_cases()
    assert _structure(source) == _structure(target), "B015 frozen structure/attributes changed"
    assert _math_signature(source) == _math_signature(target), "B015 protected MathML changed"
    addition_table(target)
    horizontal_math(target)
    source_column_frames(target)
    ids = ids_of(target)
    for ident, (declared, rows, columns) in TABLES.items():
        table = ids[ident]
        assert table.find(CN + "tgroup").get("cols") == str(declared), "B015 frozen table declaration changed"
        actual_rows = table.findall(".//" + CN + "row")
        assert len(actual_rows) == rows and all(len(r.findall(CN + "entry")) == columns for r in actual_rows), "B015 actual table shape changed"
    for original, media, suffix, media_id in zip(source.iter(CN + "media"), target.iter(CN + "media"), ASSETS, MEDIA_IDS):
        assert original.get("id") == media.get("id") == media_id
        image = media.find(CN + "image")
        expected = "assets/B015/" + PREFIX + suffix + ".te.svg"
        assert image.attrib == {"mime-type": "image/svg+xml", "src": expected}, "B015 source-to-asset mapping changed"
        svg_arithmetic(ET.parse(BASE / expected).getroot(), suffix)
    target_prose(target)
    return cases


def target_prose(target):
    """Finite semantic guards for roles that can change without changing digits."""
    ids = ids_of(target)
    phrases(ids["fs-id1516824"], ["సున్నను కలిపితే అదే సంఖ్య వస్తుంది", "సంఖ్యను మార్చని మూలకం", "additive identity"], "zero identity")
    phrases(ids["fs-id2785833"], ["క్రమాన్ని తిప్పినా మొత్తం మారదు", "Commutative Property of Addition"], "commutative property")
    phrases(ids["fs-id2877345"], ["దానికంటే ఎక్కువైతే ఎడమవైపు తదుపరి స్థానానికి", "విలువ మారకుండా", "10ఒకట్లను1పదిగా", "10పదులను1వందగా"], "carry boundary/direction/exchange value")
    phrases(ids["fs-id1567373"], ["ఒకే స్థానానికి చెందిన అంకెలు", "ఒకట్ల స్థానం నుంచి", "కుడి నుంచి ఎడమకు", "దానికంటే ఎక్కువైతే తదుపరి ఎడమ స్థానానికి"], "column algorithm")
    phrases(ids["fs-id2280341"], ["అంకెల సంఖ్య ఒకేలా లేకపోతే", "ఒకట్ల స్థానం నుంచి ఎడమవైపుకు", "ఒకే స్థానానికి చెందిన అంకెలను"], "unequal-length alignment")
    dimension_words = {2: "రెండు", 3: "మూడు", 4: "నాలుగు", 6: "ఆరు", 7: "ఏడు"}
    for ident, expected_numbers in ACCESSIBLE_NUMBERS.items():
        node = ids[ident]
        key = "alt" if node.tag == CN + "media" else ("aria-label" if ident == "eip-629" else "summary")
        value = node.get(key, "")
        actual = tuple(re.findall(r"[0-9]+(?:,[0-9]{3})*", value))
        assert actual == expected_numbers, "B015 accessible numbers/order/partial zeros changed: " + ident
        if node.tag == CN + "table":
            _, rows, cols = TABLES[ident]
            phrases(value, [dimension_words[rows] + " వరుసలు", dimension_words[cols] + " నిలువు వరుసల"], "accessible actual table dimensions")
        for match in RELATION.finditer(value):
            checked_relation(match.group())
    phrases(ids["fs-id1231518"].get("alt"), ["17కు ఒక పది-కడ్డీ", "26కు రెండు పది-కడ్డీలు", "4పది-కడ్డీలు,3విడి ఒకట్ల", "పదుల అంకె1పైన", "బదిలీ చేసిన ఒక పదిని"], "model/carry alt")
    phrases(ids["eip-id1168289818410"].get("alt"), ["మొత్తం ఇంకా రాయలేదు"], "initial incomplete image")
    phrases(ids["eip-id1168287268641"].get("alt"), ["ఒకట్ల స్థానంలో0", "1పదిని సూచించే చిన్న1", "పదుల అంకె2పైన"], "ones carry/zero alt")
    phrases(ids["eip-id1168287196613"].get("alt"), ["వందల అంకె3పైన చిన్న1", "పదుల అంకె2పైన చిన్న1", "వందను, పదిని సూచిస్తాయి", "భిన్నాలు కావు", "పదుల, ఒకట్ల స్థానాల్లో పాక్షిక మొత్తం10"], "partial carry not fraction alt")
    phrases(ids["eip-id1168287121476"].get("alt"), ["పూర్తయింది", "910", "వందల అంకె3పైన", "పదుల అంకె2పైన", "భిన్నాలు కావు"], "final carry not fraction alt")
    # Place names are ordinary translated text, unlike protected MathML digits.
    rows43 = ids["eip-id1168287505854"].findall(".//" + CN + "row")
    phrases(rows43[2][0], ["ఒకట్ల స్థానంలో2రాయండి", "పదుల స్థానానికి1పదిని"], "43+69 ones carry")
    phrases(rows43[3][0], ["పదులను కలపండి", "మొత్తంలో11రాయండి"], "43+69 final eleven tens")
    rows324 = ids["eip-id1168287251210"].findall(".//" + CN + "row")
    phrases(rows324[1][0], ["ఒకట్లను కలపండి", "ఒకట్ల స్థానంలో0రాయండి", "1పదిని పదుల స్థానానికి"], "324+586 exact-ten step")
    phrases(rows324[2][0], ["పదులను కలపండి", "పదుల స్థానంలో1రాయండి", "1వందను వందల స్థానానికి"], "324+586 tens step")
    phrases(rows324[3][0], ["వందలను కలపండి", "వందల స్థానంలో9రాయండి"], "324+586 hundreds step")
    rows1683 = ids["eip-id1168288687380"].findall(".//" + CN + "row")
    expected = [(2, "ఒకట్ల", 2, "పదిని పదుల"), (3, "పదుల", 6, "వందను వందల"),
                (4, "వందల", 1, "వేయిని వేల")]
    for index, place, digit, carry in expected:
        phrases(rows1683[index][0], [place + " స్థానంలో" + str(digit) + "రాయండి", "1" + carry + " స్థానానికి"], "1683+479 carry-place explanation")
    phrases(rows1683[5][0], ["వేలను కలపండి", "వేల స్థానంలో2రాయండి"], "1683+479 final thousands")
    rows3 = ids["eip-id1168288531101"].findall(".//" + CN + "row")
    roles = [(2, "ఒకట్ల", 4, "1పదిని పదుల"), (3, "పదుల", 1, "2వందలను వందల"),
             (4, "వందల", 8, "1వేయిని వేల"), (5, "వేల", 0, "1పది వేల సమూహాన్ని పది వేల")]
    for index, place, digit, carry in roles:
        phrases(rows3[index][0], [place + " స్థానంలో" + str(digit) + "రాయండి", carry + " స్థానానికి"], "three-addend carry count/value/target")
    phrases(rows3[6][0], ["పది వేలను కలపండి", "పది వేల స్థానంలో3రాయండి"], "three-addend final place")


def equation(addends):
    return "+".join(format(n, ",") for n in addends) + "=" + format(sum(addends), ",")


def additions_in(node):
    return [tuple(integer(n.strip()) for n in m.group().split("+"))
            for m in ADDITION.finditer(text_of(node))]


def column_equation(addends, row):
    digits = row["digits"]
    if addends == (1683, 479) and row["unit"] == 10:
        digits = tuple(reversed(digits))  # Preserve the source's 1+7+8 order.
    terms = ((row["incoming"],) if row["incoming"] else ()) + digits
    return "+".join(map(str, terms)) + "=" + str(row["total"])


def bridge_column_table(table, addends):
    """Check every visible place, equation, written digit, and carry target."""
    caption = table.find(XH + "caption")
    assert caption is not None and additions_in(caption) == [addends], "B015 column-table caption operands changed"
    headers = table.findall(XH + "thead/" + XH + "tr/" + XH + "th")
    assert [text_of(n) for n in headers] == ["స్థానం", "వచ్చిన బదిలీతో సహా అంకెల మొత్తం", "ఈ స్థానంలో రాసే అంకె", "తదుపరి స్థానానికి బదిలీ చేసే సమూహాల సంఖ్య"], "B015 column-table column roles changed"
    assert all(n.get("scope") == "col" for n in headers)
    rows = table.findall(XH + "tbody/" + XH + "tr")
    steps = column_steps(addends)
    assert len(rows) == len(steps), "B015 column-table missing/extra place row"
    expressions = []
    for actual, expected in zip(rows, steps):
        unit = expected["unit"]
        assert len(actual) == 4 and actual[0].tag == XH + "th" and actual[0].get("scope") == "row", "B015 column-table row header/shape changed"
        assert text_of(actual[0]) == PLACES[unit] + " స్థానం", "B015 column-table target place changed"
        expression = column_equation(addends, expected)
        assert compact(text_of(actual[1])) == expression, "B015 column-table incoming carry/addend digits changed"
        checked_relation(text_of(actual[1]))
        assert text_of(actual[2]) == str(expected["digit"]), "B015 column-table written digit/zero changed"
        carry = str(expected["outgoing"]) + " — "
        carry += PLACES[unit * 10] + " స్థానానికి" if expected["outgoing"] else "బదిలీ లేదు"
        assert text_of(actual[3]) == carry, "B015 column-table carry count/target place changed"
        expressions.append(expression)
    return expressions


def _links(node, destinations):
    assert [n.get("href") for n in node.iter(XH + "a")] == ["#" + d for d in destinations], "B015 source/solution/routing backlink changed"


def _detail(node, ident, parts, is_source):
    strong = [compact(text_of(n)) for n in node.iter(XH + "strong")]
    expected_strong = [equation(p) for p in parts]
    decomposition = DECOMPOSITIONS.get(ident)
    if decomposition:
        expected_strong.insert(1, decomposition)
    assert strong == expected_strong, "B015 displayed final answer/ordered operands changed: " + ident
    if is_source:
        _links(node, [ident])
        summary = node.find(XH + "summary")
        assert summary is not None
        if ident != "fs-id2323927":
            assert additions_in(summary) == list(parts), "B015 source solution summary operands changed"
    else:
        assert not list(node.iter(XH + "a")), "B015 unexpected original-solution link"
    tables = list(node.iter(XH + "table"))
    expected_equations = list(expected_strong)
    rows_checked = 0
    if len(parts) == 1:
        assert len(tables) == 1, "B015 missing source/diagnostic column reasoning"
        expressions = bridge_column_table(tables[0], parts[0])
        expected_equations.extend(expressions)
        rows_checked = len(expressions)
        by_unit = {r["unit"]: column_equation(parts[0], r) for r in column_steps(parts[0])}
        expected_equations.extend(by_unit[u] for u in FOOTER_COLUMNS.get(ident, ()))
    else:
        assert not tables, "B015 changed zero/order solution type"
    assert Counter(displayed_equalities(node)) == Counter(expected_equations), "B015 complete solution equation coverage changed: " + ident
    return expected_equations, rows_checked


def bridge_prose(bridge):
    ids = ids_of(bridge)
    phrases(ids["B015-conventions"], ["0,1,2,3", "కామా ఒక అంకె కాదు", "కామాలను ఆధారంగా చేసుకుని సంఖ్యలను తప్పుగా జరపకండి", "అధికారిక పరిభాషగా ప్రకటించడం లేదు"], "number/term convention")
    phrases(ids["B015-K1"], ["క్రమం మాత్రమే మారింది", "6,60సమానం కావు", "అంకెల స్థానాలు మార్చడానికి అనుమతి కాదు", "17ను71గా మార్చడం వేరే సంఖ్య"], "zero and operand-order distinction")
    phrases(ids["B015-K2"], ["మొత్తం విలువ మారదు", "పది ఒకట్లను మళ్లీ కలపకండి", "పదుల నిలువు వరుస పైన రాసిన చిన్న1విలువ10", "భిన్నం లేదా ఘాతం కాదు", "వేల స్థానానికి బదిలీ చేసే1విలువ1,000"], "carried count versus contribution")
    phrases(ids["B015-K3"], ["ఒకట్ల స్థానాలను సరిపోల్చి", "లేని ఎడమ స్థానంలో", "సమూహాల సంఖ్య0", "ఒకట్ల వరుసలో ఆరంభ బదిలీ లేదు", "10కంటే తక్కువైతే", "10లేదా ఎక్కువైతే", "మిగిలిన0నుంచి9వరకు అంకెను", "సరిగ్గా10అయితే0రాసి1సమూహాన్ని", "ప్రతి బదిలీని ఒక్కసారి మాత్రమే", "బదిలీ2కూడా కావచ్చు", "ఎప్పుడూ1మాత్రమే కాదు", "21పదులు,విలువ210", "రాసే అంకె”1", "బదిలీ”2వందలు", "సున్నను వదిలేయమని కాదు"], "inclusive-ten/carry2/zero/column-unit meaning")
    phrases(ids["B015-W-fs-id2325655"], ["11పదులను రాయడం", "ఒకట్ల స్థానంలో11ను రాయడం కాదు"], "source eleven-tens instruction")
    phrases(ids["B015-W-fs-id2277302"], ["ఒకట్ల స్థానంలో0తప్పక రాయాలి", "1/3లేదా1/2భిన్నాలు కావు"], "source exact-ten and carry not fractions")
    phrases(ids["B015-W-fs-id2144790"], ["479లో వేల అంకె లేదు", "దాని నుంచి0మాత్రమే", "పాక్షిక రాత162", "అది చివరి వరుసలో కనిపిస్తుంది", "11వచ్చిన వెంటనే1వేయిని బదిలీగా", "162పూర్తి జవాబు కాదు"], "delayed source carry-marker explanation")
    phrases(ids["B015-W-fs-id2264879"], ["21పదులు", "2వందలను బదిలీ", "వందల లెక్కలో ప్రారంభ2", "వేల స్థానంలో0", "0814లో ఎడమ0వేల స్థానాన్ని", "అది పూర్తి జవాబు కాదు", "861లో వేల,పది వేల స్థానాల నుంచి0", "8,596లో పది వేల స్థానానికి0"], "source carry2/partial0814/missing places")
    phrases(ids["B015-S-fs-id1264596-b"], ["ఒకట్ల అంకె9,పదుల అంకె3"], "zero unchanged digits")
    phrases(ids["B015-S-fs-id2362020-b"], ["మరో సున్న అంకెను రాసి570చేయకండి"], "zero versus appending digit")
    phrases(ids["B015-S-D01"], ["680గా రాయడం కాదు", "680లో68పదుల విలువ"], "diagnostic zero versus digit concatenation")
    phrases(ids["B015-S-R01"], ["పదుల అంకె7,ఒకట్ల అంకె3మారవు"], "recheck zero digit roles")
    phrases(ids["B015-S-D02"], ["42లోని4పదుల అంకె", "306లోని పదుల0కింద", "2ఒకట్ల అంకె6కింద", "42లో వందల నుంచి0"], "diagnostic unequal-length alignment")
    phrases(ids["B015-S-R02"], ["35లోని3పదుల స్థానంలో,5ఒకట్ల స్థానంలో", "504లోని మధ్య0స్థానాన్ని వదిలేసి54గా మార్చకండి"], "recheck zero/alignment")
    phrases(ids["B015-S-D03"], ["పదుల స్థానంలో0రాసి1వందను", "505", "మధ్య0ను వదిలేస్తే వేరే సంఖ్య"], "diagnostic written zero")
    phrases(ids["B015-S-R03"], ["కొత్త వేల స్థానంలో1రాయాలి", "1,005", "పదుల,వందల రెండు సున్నలూ అవసరం"], "recheck all-carry zeros")
    phrases(ids["B015-S-D04"], ["2పదులను బదిలీ", "2వందలను బదిలీ", "2అంటే2సమూహాలు", "విలువ ఆ స్థానాన్ని బట్టి మారుతుంది"], "diagnostic carry2 count versus value")
    phrases(ids["B015-final-check"], ["ప్రతి బదిలీని ఒక్కసారి", "ప్రస్తుత స్థానంలో ఒక్క అంకె", "మొత్తం ప్రతి కలిపే సంఖ్యకంటే తక్కువ కాదు", "సున్నను కలిపితే సమానంగా ఉండవచ్చు", "పూర్తి లెక్కకు ప్రత్యామ్నాయం కాదు", "4,597+685కు528అనే జవాబు చిన్నదిగా"], "final-check limits")


def validate_b015(target, bridge):
    """Validate actual ElementTree roots; no file writes or source regeneration."""
    validate_algorithm_target(target)
    ids, target_ids = ids_of(bridge), ids_of(target)
    assert bridge.get("id") == "B015-bridge" and len(ids) == 56
    assert not (ids.keys() & target_ids.keys()), "B015 bridge collides with source ID"
    expected_details = {("B015-W-" if kind == "worked" else "B015-S-") + ident
                        for ident, _, kind, _ in EXERCISES} | {"B015-S-" + c for c in EXTRA_CASES}
    assert {n.get("id") for n in bridge.iter(XH + "details")} == expected_details, "B015 source/diagnostic detail coverage changed"
    links = list(bridge.iter(XH + "a"))
    assert len(links) == 42, "B015 bridge link count changed"
    for link in links:
        href = link.get("href", "")
        assert href.startswith("#") and href[1:] in (ids.keys() | target_ids.keys()), "B015 unresolved bridge link"
    equations, columns = [], 0
    for ident, _, kind, parts in EXERCISES:
        key = ("B015-W-" if kind == "worked" else "B015-S-") + ident
        expected, count = _detail(ids[key], ident, parts, True)
        equations.extend(expected); columns += count
        if kind == "try" and len(parts) == 2:
            items = ids[key].findall(XH + "ol/" + XH + "li")
            assert [n.get("id") for n in items] == [key + "-a", key + "-b"], "B015 source part IDs/order changed"
            for item, part in zip(items, parts):
                assert compact(text_of(next(item.iter(XH + "strong")))) == equation(part), "B015 source part primary answer changed"
    for case, parts in EXTRA_CASES.items():
        question = ids["B015-" + case]
        assert additions_in(question.find(XH + "p")) == list(parts), "B015 diagnostic/recheck requested operands changed"
        expected, count = _detail(ids["B015-S-" + case], case, parts, False)
        equations.extend(expected); columns += count
    for case, required in {"D02": ["42లోని4ఏ స్థానంలో"], "D03": ["పదుల స్థానంలో ఏ అంకె"],
        "D04": ["ప్రతి బదిలీ ఎన్ని సమూహాలో"], "R02": ["35లోని3ను ఏ స్థానంలో"],
        "R03": ["ఒకట్ల నుంచి కొత్త వేల స్థానం వరకు"], "R04": ["ఒకట్ల,పదుల దశల్లో బదిలీ ఎన్ని సమూహాలో"]}.items():
        phrases(ids["B015-" + case], required, "diagnostic/recheck target place or carry question")
    route = {"D01": ["B015-S-D01", "B015-K1", "fs-id1968047", "B015-R01"],
        "D02": ["B015-S-D02", "B015-K3", "fs-id1578501", "B015-R02"],
        "D03": ["B015-S-D03", "B015-K2", "B015-W-fs-id2277302", "B015-R03"],
        "D04": ["B015-S-D04", "B015-W-fs-id2264879", "B015-R04"]}
    for case, destinations in route.items():
        _links(ids["B015-" + case], destinations)
    for case in ("R01", "R02", "R03", "R04"):
        _links(ids["B015-" + case], ["B015-S-" + case])
    support = {"B015-conventions": ["17+26=43"],
        "B015-K1": ["8+7=15", "7+8=15", "0+11=11", "42+0=42", "0+0=0", "6+0=6", "8+2+5=15", "17+26=43", "71+26=97"],
        "B015-K2": ["10×1=1×10", "10×10=1×100", "7+6=13", "1+1+2=4", "4×10+3=43"],
        "B015-K3": ["1+5+6+9=21"]}
    for ident, expected in support.items():
        assert displayed_equalities(ids[ident]) == expected, "B015 unscored support equation changed"
        equations.extend(expected)
    bridge_prose(bridge)
    actual = displayed_equalities(bridge)
    assert Counter(actual) == Counter(equations), "B015 complete displayed equation inventory changed"
    assert len(list(bridge.iter(XH + "table"))) == 21 and columns == 70, "B015 actual carry-table coverage changed"
    return {"source_exercises": 21, "source_parts": 27, "source_try_it_parts": 18,
            "addition_table_cells": 100, "original_solution_ids": 21, "source_math_expressions": 135,
            "source_vertical_frames": 16, "source_assets": 5, "bridge_solution_details": 29,
            "entry_recheck_prompts": 8, "entry_recheck_ordered_sums": 10,
            "bridge_column_tables": 21, "bridge_column_rows": columns,
            "bridge_equation_occurrences": len(actual)}
