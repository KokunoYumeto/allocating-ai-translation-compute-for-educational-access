"""Read-only, finite mathematics and image semantics for TE-B019.

The frozen chapter-practice subsection is the authority for structure and
question order.  Numeric answers are recomputed here.  Image constants were
independently read from the 22 pinned original JPEGs; the source alts and
localized SVG metadata are checked against that pixel reading, not used as an
unexamined answer key.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET

from naming_checks import english_name, text_of

BASE = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
MATH = "{http://www.w3.org/1998/Math/MathML}"
XH = "{http://www.w3.org/1999/xhtml}"
SVG = "{http://www.w3.org/2000/svg}"
XML = "{http://www.w3.org/XML/1998/namespace}"
SOURCE_SHA256 = "5c0d3d631bb07b5f2251bb72018f9f6b9b530f63d9bed26857b7c66ffb335275"

GROUPS = {
    "notation": ("fs-id1386835", "fs-id2169300", "fs-id2649783", "fs-id2267610",
                 "fs-id2479137", "fs-id2459088"),
    "model": ("fs-id2431569", "fs-id2210891", "fs-id1583137", "fs-id1389381",
              "fs-id1932178", "fs-id1509761", "fs-id2495783", "fs-id1209935"),
    "chart": ("fs-id2190914", "fs-id1485179", "fs-id2307885", "fs-id1516426",
              "fs-id2216372", "fs-id2220307"),
    "property": ("fs-id3433877", "fs-id2670104", "fs-id1800383", "fs-id2700265"),
    "add": ("fs-id2165529", "fs-id1785992", "fs-id3407533", "fs-id2209807",
            "fs-id2715529", "fs-id1184179", "fs-id1612224", "fs-id1806818",
            "fs-id1360696", "fs-id2602850", "fs-id1619766", "fs-id2269768",
            "fs-id2238187", "fs-id2202157", "fs-id1257721", "fs-id1808456",
            "fs-id1791279", "fs-id1205572", "fs-id1582947", "fs-id1542190",
            "fs-id2308954", "fs-id1352693", "fs-id2611500", "fs-id1523165"),
    "phrase": ("fs-id2387977", "fs-id1233172", "fs-id1916031", "fs-id1834317",
               "fs-id2223707", "fs-id1529453", "fs-id1760728", "fs-id2671623",
               "fs-id1606377", "fs-id1614332", "fs-id2281219", "fs-id1159676"),
    "application": ("fs-id2195542", "fs-id2452678", "fs-id2264366", "fs-id1401775",
                    "fs-id2609576", "fs-id1946723", "fs-id1962359", "fs-id1410524"),
    "perimeter": ("fs-id2658194", "fs-id2130628", "fs-id1718142", "fs-id2173206",
                  "fs-id1788660", "fs-id1321391", "fs-id2427822", "fs-id1960065"),
    "everyday": ("fs-id1606437", "fs-id1215287", "fs-id1567863", "fs-id1369108"),
    "open": ("fs-id1408863", "fs-id1827602"),
}
EXERCISE_IDS = tuple(ident for group in GROUPS.values() for ident in group)

NOTATION = {
    "fs-id1386835": (5, 2), "fs-id2169300": (6, 3),
    "fs-id2649783": (13, 18), "fs-id2267610": (15, 16),
    "fs-id2479137": (214, 642), "fs-id2459088": (438, 113),
}
NOTATION_WORDS = {
    "fs-id1386835": ("ఐదు", "రెండు"),
    "fs-id2169300": ("ఆరు", "మూడు"),
    "fs-id2649783": ("పదమూడు", "పద్దెనిమిది"),
    "fs-id2267610": ("పదిహేను", "పదహారు"),
    "fs-id2479137": ("రెండు వందల పద్నాలుగు", "ఆరు వందల నలభై రెండు"),
    "fs-id2459088": ("నాలుగు వందల ముప్పై ఎనిమిది", "నూట పదమూడు"),
}
MODELS = {
    "fs-id2431569": (2, 4), "fs-id2210891": (5, 3),
    "fs-id1583137": (8, 4), "fs-id1389381": (5, 9),
    "fs-id1932178": (14, 75), "fs-id1509761": (15, 63),
    "fs-id2495783": (16, 25), "fs-id1209935": (14, 27),
}
PROPERTIES = {
    "fs-id3433877": ((0, 13), (13, 0)),
    "fs-id2670104": ((0, 5280), (5280, 0)),
    "fs-id1800383": ((8, 3), (3, 8)),
    "fs-id2700265": ((7, 5), (5, 7)),
}
ADD_TOTALS = {
    "fs-id2165529": 78, "fs-id1785992": 59, "fs-id3407533": 99,
    "fs-id2209807": 96, "fs-id2715529": 85, "fs-id1184179": 55,
    "fs-id1612224": 142, "fs-id1806818": 131, "fs-id1360696": 493,
    "fs-id2602850": 396, "fs-id1619766": 861, "fs-id2269768": 823,
    "fs-id2238187": 1031, "fs-id2202157": 1144, "fs-id1257721": 6850,
    "fs-id1808456": 9762, "fs-id1791279": 22333, "fs-id1205572": 22108,
    "fs-id1582947": 1104860, "fs-id1542190": 1226200,
    "fs-id2308954": 29191, "fs-id1352693": 34335,
    "fs-id2611500": 101531, "fs-id1523165": 89033,
}
PHRASES = {
    "fs-id2387977": (13, 18, 31), "fs-id1233172": (12, 19, 31),
    "fs-id1916031": (90, 65, 155), "fs-id1834317": (70, 38, 108),
    "fs-id2223707": (33, 49, 82), "fs-id1529453": (68, 25, 93),
    "fs-id1760728": (599, 250, 849), "fs-id2671623": (286, 115, 401),
    "fs-id1606377": (628, 77, 705), "fs-id1614332": (593, 79, 672),
    "fs-id2281219": (915, 1482, 2397), "fs-id1159676": (682, 2719, 3401),
}
APPLICATIONS = {
    "fs-id2195542": ((1100, 250, 525), 1875, "USD", ()),
    "fs-id2452678": ((299, 35, 68), 402, "USD", ()),
    "fs-id2264366": ((14, 19, 12, 25, 68), 138, "miles", ()),
    "fs-id1401775": ((19, 12, 23, 29, 44), 127, "arrangements", ()),
    "fs-id2609576": ((238, 120, 156, 196, 100, 132, 225), 1167, "square feet", (7,)),
    "fs-id1946723": ((175, 192, 148, 169, 205, 181, 225), 1295, "pounds", (7,)),
    "fs-id1962359": ((82572, 79316, 75298), 237186, "USD", ()),
    "fs-id1410524": ((292540, 505875, 423699), 1222114, "USD", (3,)),
}
PERIMETERS = {
    "fs-id2658194": ((14, 12, 18), 44, "in", "208_img", (14, 12, 18)),
    "fs-id2130628": ((5, 13, 12), 30, "cm", "209_img", (5, 13, 12)),
    "fs-id1718142": ((21, 7, 21, 7), 56, "m", "210_img", (21, 7, 21, 7)),
    "fs-id2173206": ((19, 14, 19, 14), 66, "ft", "211_img", (19, 14, 19, 14)),
    "fs-id1788660": ((19, 18, 16, 18), 71, "yd", "212_img", (19, 18, 16, 18)),
    "fs-id1321391": ((24, 17, 29, 17), 87, "m", "213_img", (24, 17, 29, 17)),
    "fs-id2427822": ((24, 7, 19, 3, 5, 4), 62, "ft", "214_img", (24, 7, 19, 3, 5, 4)),
    # The last3in is derived from10-7. It is intentionally not printed.
    "fs-id1960065": ((25, 10, 14, 7, 11, 3), 70, "in", "215_img", (25, 10, 14, 7, 11)),
}
EVERYDAY = {
    "fs-id1606437": ((320, 170, 150), 640, "calories", (16, 16), None),
    "fs-id1215287": ((420, 230, 580), 1230, "calories", (12, 12), None),
    "fs-id1567863": ((82, 91, 75, 88, 70), 406, "points", (400,), (">=", 400)),
    "fs-id1369108": ((210, 145, 183, 230, 159, 164), 1091, "pounds", (1150,), ("<", 1150)),
}

CHARTS = {
    "fs-id2190914": {"rows": tuple(range(10)), "cols": tuple(range(10)), "blank": 39,
                       "problem": "216", "solution": "217"},
    "fs-id1485179": {"rows": tuple(range(10)), "cols": tuple(range(10)), "blank": 39,
                       "problem": "218", "solution": None},
    "fs-id2307885": {"rows": tuple(range(6, 10)), "cols": tuple(range(3, 10)), "blank": 28,
                       "problem": "220", "solution": "221"},
    "fs-id1516426": {"rows": tuple(range(3, 10)), "cols": tuple(range(6, 10)), "blank": 28,
                       "problem": "222", "solution": None},
    "fs-id2216372": {"rows": tuple(range(5, 10)), "cols": tuple(range(5, 10)), "blank": 25,
                       "problem": "224", "solution": "225"},
    "fs-id2220307": {"rows": tuple(range(6, 10)), "cols": tuple(range(6, 10)), "blank": 16,
                       "problem": "226", "solution": None},
}

MODEL_ASSETS = {
    "201_img": (("ones", 2), ("ones", 4)),
    "203_img": (("tens", 1), ("ones", 2)),
    "205_img": (("tens", 8), ("ones", 9)),
    "207_img": (("tens", 4), ("ones", 1)),
}
SELF_OBJECTIVES = (
    "use addition notation.", "model addition of whole numbers.",
    "add whole numbers without models.", "translate word phrases to math notation.",
    "add whole numbers in applications.",
)

NUMBER = r"(?:0|[1-9][0-9]*(?:,[0-9]{3})*)"
RELATION = re.compile(r"(?<![0-9A-Za-z_.,])(" + NUMBER + r"(?:\s*\+\s*" + NUMBER +
                      r")+)\s*=\s*(" + NUMBER + r")(?![0-9]|,[0-9]|\.[0-9])")


def local(node):
    return node.tag.rsplit("}", 1)[-1]


def compact(value):
    return re.sub(r"\s+", "", value)


def number(value):
    return int(value.replace(",", ""))


def numbers(value):
    return [number(n) for n in re.findall(r"(?<![A-Za-z0-9_,])\$?([0-9][0-9,]*)", value)]


def ids_of(root):
    nodes = [node for node in root.iter() if node.get("id")]
    result = {node.get("id"): node for node in nodes}
    assert len(nodes) == len(result), "B019 duplicate ID"
    return result


def sha_file(path):
    return sha256(path.read_bytes()).hexdigest()


def operands(problem):
    values = []
    for node in problem.iter(MATH + "mn"):
        token = (node.text or "").strip().rstrip(".")
        assert re.fullmatch(r"\$?[0-9][0-9,]*", token), "B019 unexpected numeric token"
        values.append(number(token.lstrip("$")))
    return tuple(values)


def column_steps(values):
    assert len(values) >= 2 and all(type(value) is int and value >= 0 for value in values)
    rows, place, carry = [], 1, 0
    while place <= max(values) or carry:
        digits = tuple(value // place % 10 for value in values)
        total = sum(digits) + carry
        rows.append((place, digits, carry, total, total % 10, total // 10))
        carry = total // 10
        place *= 10
    if not rows:
        rows.append((1, tuple(0 for _ in values), 0, 0, 0, 0))
    assert sum(place * written for place, _, _, _, written, _ in rows) == sum(values)
    return tuple(rows)


def checked_equality(value):
    match = RELATION.fullmatch(value.strip())
    assert match, "B019 unsupported displayed equality"
    addends = tuple(number(n) for n in re.split(r"\s*\+\s*", match.group(1)))
    result = number(match.group(2))
    assert sum(addends) == result, "B019 incorrect displayed equality"
    return addends, result


def displayed_equalities(root):
    result = []
    for node in root.iter():
        if local(node) not in {"p", "li", "td", "dd"}:
            continue
        if any(child is not node and local(child) in {"p", "li", "td", "dd"}
               for child in node.iter()):
            continue
        for match in RELATION.finditer(text_of(node)):
            checked_equality(match.group())
            result.append(compact(match.group()))
    return result


def structure(root):
    omitted = {"alt", "aria-label", "summary", "src", "mime-type", XML + "lang"}
    return [(node.tag, depth, node.get("id"),
             tuple(sorted((key, value) for key, value in node.attrib.items() if key not in omitted)),
             len(node))
            for node, depth in _walk(root)]


def _walk(node, depth=0):
    yield node, depth
    for child in node:
        yield from _walk(child, depth + 1)


def math_signature(root, target=False):
    reverse = {"మరియు": "and", "16 ఔన్సుల": "16-ounce", "12 ఔన్సుల": "12-oz"} if target else {}
    return [(node.tag, tuple(sorted(node.attrib.items())), reverse.get((node.text or "").strip(),
             (node.text or "").strip()), len(node)) for node in root.iter() if node.tag.startswith(MATH)]


def _normalize_words(value):
    return " ".join(value.lower().replace("-", " ").replace(",", " ").rstrip(".").split())


def _source_chart_blanks(media, spec):
    if spec["problem"] in {"216", "218"}:
        quoted = re.findall(r"values “([^”]+)”", media.get("alt", ""))
        assert len(quoted) == 11
        blanks = set()
        for col, column in enumerate(quoted[1:]):
            cells = [cell.strip() for cell in column.split(";")]
            assert len(cells) == 11 and number(cells[0]) == col
            for row, cell in enumerate(cells[1:]):
                if cell == "null":
                    blanks.add((row, col))
                else:
                    assert number(cell) == row + col
        assert len(blanks) == spec["blank"]
        return frozenset(blanks)
    return frozenset((row, col) for row in spec["rows"] for col in spec["cols"])


def _expected_solution_numbers(case):
    kind = case["kind"]
    if kind == "notation":
        return list(case["operands"])
    if kind == "model":
        return [*case["operands"], case["total"]]
    if kind == "property":
        return [case["total"], case["total"]]
    if kind in {"add", "application", "perimeter", "everyday"}:
        return [case["total"]]
    if kind == "phrase":
        return [*case["operands"], case["total"]]
    return []


def _check_source_solution(case, solution):
    kind = case["kind"]
    value = text_of(solution)
    if kind == "notation":
        left, right = case["operands"]
        normalized = _normalize_words(value)
        assert _normalize_words(english_name(left) + " plus " + english_name(right)) in normalized
        assert f"the sum of {left} and {right}" in normalized
    elif kind == "chart":
        media = solution.find(".//" + CN + "media")
        assert media is not None and case["chart"]["solution"]
        assert media.find(CN + "image").get("src").endswith("_" + case["chart"]["solution"] + ".jpg")
    elif kind == "open":
        assert "Answers will vary" in value
    else:
        assert numbers(value) == _expected_solution_numbers(case), (
            "B019 supplied source solution changed: " + case["id"])


def source_cases():
    """Read and independently classify every one of the 82 source exercises."""
    raw = (BASE / "sources/TE-B019.en.cnxml").read_bytes()
    assert sha256(raw).hexdigest() == SOURCE_SHA256, "B019 frozen source changed"
    source = ET.fromstring(raw)
    assert source.get("id") == "fs-id2263283" and source.get("class") == "section-exercises"
    assert (len(list(source.iter())), len(ids_of(source)), len(list(source.iter(CN + "exercise"))),
            len(list(source.iter(CN + "solution"))), len(list(source.iter(CN + "image"))),
            len(list(source.iter(MATH + "math")))) == (1017, 366, 82, 42, 22, 135)
    exercises = list(source.iter(CN + "exercise"))
    assert tuple(node.get("id") for node in exercises) == EXERCISE_IDS
    group_of = {ident: group for group, members in GROUPS.items() for ident in members}
    records = []
    for order, exercise in enumerate(exercises, 1):
        ident = exercise.get("id")
        kind = group_of[ident]
        problem = exercise.find(CN + "problem")
        solutions = exercise.findall(CN + "solution")
        assert problem is not None and len(solutions) <= 1
        case = {"order": order, "id": ident, "problem_id": problem.get("id"), "kind": kind,
                "solution_id": solutions[0].get("id") if solutions else None}
        if kind == "notation":
            case["operands"] = NOTATION[ident]
            assert operands(problem) == case["operands"]
        elif kind == "model":
            case["operands"] = MODELS[ident]
            case["total"] = sum(case["operands"])
            assert operands(problem) == case["operands"]
            case["final_model"] = divmod(case["total"], 10)
        elif kind == "chart":
            spec = CHARTS[ident]
            media = problem.find(CN + "media")
            assert media is not None and media.find(CN + "image").get("src").endswith("_" + spec["problem"] + ".jpg")
            case["chart"] = spec
            case["blank_cells"] = _source_chart_blanks(media, spec)
            case["formula_cells"] = tuple((row, col, row + col) for row in spec["rows"] for col in spec["cols"])
        elif kind == "property":
            case["pairs"] = PROPERTIES[ident]
            case["total"] = sum(case["pairs"][0])
            assert tuple(operands(item) for item in problem.findall(CN + "list/" + CN + "item")) == case["pairs"]
            assert all(sum(pair) == case["total"] for pair in case["pairs"])
        elif kind == "add":
            case["operands"] = operands(problem)
            case["total"] = ADD_TOTALS[ident]
            assert len(case["operands"]) in {2, 3} and sum(case["operands"]) == case["total"]
            case["columns"] = column_steps(case["operands"])
        elif kind == "phrase":
            expected = PHRASES[ident]
            shown = operands(problem)
            assert set(shown) == set(expected[:2]) or shown == expected[:2]
            case["operands"], case["total"] = expected[:2], expected[2]
            assert sum(case["operands"]) == case["total"]
        elif kind == "application":
            case["operands"], case["total"], case["unit"], case["incidental"] = APPLICATIONS[ident]
            assert sum(case["operands"]) == case["total"]
            case["columns"] = column_steps(case["operands"])
        elif kind == "perimeter":
            edges, total, unit, suffix, visible = PERIMETERS[ident]
            assert sum(edges) == total
            case.update(edges=edges, total=total, unit=unit, suffix=suffix, visible_edges=visible)
            media = problem.find(CN + "media")
            assert media is not None and media.find(CN + "image").get("src").endswith("_" + suffix + ".jpg")
        elif kind == "everyday":
            vals, total, unit, incidental, comparison = EVERYDAY[ident]
            assert sum(vals) == total
            if comparison:
                op, threshold = comparison
                assert (total >= threshold) if op == ">=" else (total < threshold)
            case.update(operands=vals, total=total, unit=unit, incidental=incidental,
                        comparison=comparison, columns=column_steps(vals))
        else:
            assert kind == "open"
            case["rubric"] = "non-unique reflection; reason/action or model-use explanation"
        if solutions:
            _check_source_solution(case, solutions[0])
        records.append(case)
    assert sum(case["solution_id"] is not None for case in records) == 42
    assert sum(case["kind"] == "open" for case in records) == 2
    assert sum(case["chart"]["blank"] for case in records if case["kind"] == "chart") == 175
    return source, records


def _svg_text(root):
    return " ".join(" ".join(root.itertext()).split())


def _asset_by_suffix(manifest):
    result = {}
    for asset in manifest["assets"]:
        name = Path(asset["original_path"]).stem
        suffix = name.removeprefix("CNX_BMath_Figure_01_02_")
        if name == "CNX_BMath_Figure_AppB_002_A":
            suffix = "AppB_002_A"
        assert suffix not in result
        result[suffix] = asset
    return result


def _validate_chart_svg(root, rows, cols, blanks):
    cells = [node for node in root.iter(SVG + "g") if node.get("data-role") == "table-cell"]
    assert len(cells) == (len(rows) + 1) * (len(cols) + 1), "B019 chart dimensions changed"
    seen, actual_blanks = set(), set()
    for cell in cells:
        grid_row, grid_col = int(cell.get("data-grid-row")), int(cell.get("data-grid-col"))
        assert (grid_row, grid_col) not in seen
        seen.add((grid_row, grid_col))
        values = [node.text for node in cell.iter(SVG + "text") if node.get("data-role") == "cell-value"]
        header = cell.get("data-header") == "true"
        if header:
            if grid_row == grid_col == 0:
                assert values == ["+"]
            elif grid_row == 0:
                assert values == [str(cols[grid_col - 1])]
            else:
                assert grid_col == 0 and values == [str(rows[grid_row - 1])]
            assert cell.get("data-blank") == "false"
        else:
            row, col = int(cell.get("data-row-value")), int(cell.get("data-col-value"))
            assert row == rows[grid_row - 1] and col == cols[grid_col - 1]
            if cell.get("data-blank") == "true":
                assert not values
                actual_blanks.add((row, col))
            else:
                assert values == [str(row + col)], "B019 visible addition-table sum changed"
    assert actual_blanks == set(blanks), "B019 addition-table blank coordinates changed"


def _validate_model_svg(root, expected, expected_value, expression):
    groups = [node for node in root.iter(SVG + "g") if node.get("data-role") == "model-group"]
    actual = tuple((node.get("data-kind"), int(node.get("data-count"))) for node in groups)
    assert actual == expected, "B019 model group kind/count changed"
    for node in groups:
        multiplier = {"ones": 1, "tens": 10}[node.get("data-kind")]
        assert int(node.get("data-value")) == int(node.get("data-count")) * multiplier, (
            "B019 model group contribution changed")
    assert sum(int(node.get("data-value")) for node in groups) == expected_value, (
        "B019 model group values changed")
    assert compact(expression) + "=" not in compact(_svg_text(root)), (
        "B019 model problem asset cannot print its equation answer")


def _validate_perimeter_svg(root, edges, total, unit, visible, suffix):
    labels = [text_of(node) for node in root.iter(SVG + "text")
              if node.get("data-role") == "side-label"]
    assert labels == [f"{value} {unit}" for value in visible], (
        "B019 perimeter visible side labels/order changed")
    assert f"{total} {unit}" not in labels and sum(edges) == total
    if suffix == "215_img":
        text = _svg_text(root)
        assert "3 in" not in text and "70 in" not in text, (
            "B019 Figure215 problem asset leaked a derived length/answer")
        assert 10 - 7 == 3 and 25 - 14 == 11


def _validate_selfcheck_svg(root):
    cells = [node for node in root.iter(SVG + "g") if node.get("data-role") == "table-cell"]
    assert len(cells) == 24, "B019 self-check table shape changed"
    responses = [node for node in cells if node.get("data-response") == "true"]
    assert len(responses) == 15, "B019 self-check response-cell count changed"
    assert all(not list(node.iter(SVG + "text")) for node in responses), (
        "B019 self-check problem asset cannot preselect a response")
    assert tuple(node.text for node in root.iter(SVG + "text")
                 if node.get("data-role") == "objective-en") == SELF_OBJECTIVES


def validate_assets():
    """Validate exact pinned files and machine-readable mathematics in all22 SVGs."""
    source, cases = source_cases()
    manifest_path = BASE / "assets/B019/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["unit"] == "TE-B019" and manifest["source_subsection_sha256"] == SOURCE_SHA256
    assert len(manifest["assets"]) == 22
    by_suffix = _asset_by_suffix(manifest)
    source_srcs = {node.get("src") for node in source.iter(CN + "image")}
    assert {asset["original_src"] for asset in manifest["assets"]} == source_srcs
    for asset in manifest["assets"]:
        original = BASE / asset["original_path"]
        localized = BASE / asset["localized_path"]
        assert original.stat().st_size == asset["original_bytes"] and sha_file(original) == asset["original_sha256"]
        assert localized.stat().st_size == asset["localized_bytes"] and sha_file(localized) == asset["localized_sha256"]
        assert asset["recommended_min_width_px"] >= 0
    # Four source-solution block models.
    for suffix, expected in MODEL_ASSETS.items():
        asset = by_suffix[suffix]
        root = ET.parse(BASE / asset["localized_path"]).getroot()
        _validate_model_svg(root, expected, asset["math_checks"]["modeled_value"],
                            asset["math_checks"]["expression"])
    # Six problem charts and three source-solution charts.
    by_exercise = {case["id"]: case for case in cases if case["kind"] == "chart"}
    for case in by_exercise.values():
        spec = case["chart"]
        problem = by_suffix[spec["problem"]]
        root = ET.parse(BASE / problem["localized_path"]).getroot()
        _validate_chart_svg(root, spec["rows"], spec["cols"], case["blank_cells"])
        checks = problem["math_checks"]
        assert (checks["columns_including_header"], checks["rows_including_header"],
                checks["blank_answer_cells"]) == (len(spec["cols"]) + 1, len(spec["rows"]) + 1, spec["blank"])
        if spec["solution"]:
            solution = by_suffix[spec["solution"]]
            full = ET.parse(BASE / solution["localized_path"]).getroot()
            _validate_chart_svg(full, spec["rows"], spec["cols"], set())
            assert solution["math_checks"]["blank_answer_cells"] == 0
    # The pixel orientation correction is target/accessibility only; frozen source remains8x5.
    source222 = ids_of(source)["fs-id2263429"]
    assert "8 columns and 5 rows" in source222.get("alt")
    root222 = ET.parse(BASE / by_suffix["222"]["localized_path"]).getroot()
    cells222 = [node for node in root222.iter(SVG + "g") if node.get("data-role") == "table-cell"]
    assert max(int(node.get("data-grid-col")) for node in cells222) == 4
    assert max(int(node.get("data-grid-row")) for node in cells222) == 7
    # All eight perimeter figures retain visible labels but never print the answer.
    for ident, (edges, total, unit, suffix, visible) in PERIMETERS.items():
        asset = by_suffix[suffix]
        root = ET.parse(BASE / asset["localized_path"]).getroot()
        _validate_perimeter_svg(root, edges, total, unit, visible, suffix)
    # Self-check is open:5objectives x3blank confidence cells, never an answer key.
    self_asset = by_suffix["AppB_002_A"]
    self_root = ET.parse(BASE / self_asset["localized_path"]).getroot()
    _validate_selfcheck_svg(self_root)
    return {"localized_assets": 22, "model_assets": 4, "chart_assets": 9,
            "perimeter_assets": 8, "selfcheck_assets": 1, "chart_blank_cells": 175}


def validate_review_target(target):
    """Validate the actual localized source, including all42 supplied solutions."""
    source, cases = source_cases()
    assert structure(source) == structure(target), "B019 source structure/IDs changed"
    assert math_signature(source) == math_signature(target, target=True), "B019 protected MathML changed"
    assert target.get(XML + "lang") == "te-Telu-IN"
    ids = ids_of(target)
    manifest = json.loads((BASE / "assets/B019/manifest.json").read_text(encoding="utf-8"))
    localized_by_original = {asset["original_src"]: asset["localized_path"]
                             for asset in manifest["assets"]}
    for case in cases:
        if case["solution_id"]:
            solution = ids[case["solution_id"]]
            if case["kind"] == "notation":
                left, right = NOTATION_WORDS[case["id"]]
                first, second = case["operands"]
                require(solution, [f"{left} ప్లస్ {right}",
                                   f"{first}, {second} అనే సంఖ్యల మొత్తం"],
                        "B019 localized notation answer")
            elif case["kind"] == "chart":
                source_image = ids_of(source)[case["solution_id"]].find(".//" + CN + "image")
                target_image = solution.find(".//" + CN + "image")
                assert source_image is not None and target_image is not None
                assert target_image.get("src") == localized_by_original[source_image.get("src")]
            elif case["kind"] == "open":
                assert "జవాబులు వేర్వేరుగా ఉండవచ్చు" in text_of(solution)
            else:
                assert numbers(text_of(solution)) == _expected_solution_numbers(case), (
                    "B019 localized supplied solution changed: " + case["id"])
                if case["id"] in TARGET_SOLUTION_MARKERS:
                    assert TARGET_SOLUTION_MARKERS[case["id"]] in text_of(solution), (
                        "B019 localized supplied answer unit/context changed: " + case["id"])
    media222 = ids["fs-id2263429"]
    assert "5 నిలువు వరుసలు, 8 అడ్డ వరుసలు" in media222.get("alt", "")
    assert "మూల alt చెప్పిన8×5కు విరుద్ధంగా" in media222.get("alt", "")
    media215 = ids["fs-id2316211"]
    assert "సంఖ్యా లేబుల్ లేదు" in media215.get("alt", "")
    assert "70" not in media215.get("alt", "") and "3 అంగుళ" not in media215.get("alt", "")
    # All source media map to the exact finalized localized asset set.
    expected = {asset["localized_path"] for asset in manifest["assets"]}
    assert {node.get("src") for node in target.iter(CN + "image")} == expected
    return {"source_exercises": 82, "provided_solution_nodes": 42,
            "fixed_exercises": 80, "open_writing_exercises": 2,
            "chart_blank_cells": 175, "source_images": 22}


PLACE_TE = {1: "ఒకట్లు", 10: "పదులు", 100: "వందలు", 1000: "వేలు",
            10000: "పది వేలు", 100000: "వంద వేలు", 1000000: "మిలియన్లు"}
PERIMETER_UNIT_TEXT = {"in": "inches", "cm": "centimeters", "m": "meters",
                       "ft": "feet", "yd": "yards"}
MODEL_REASON = {
    "fs-id2431569": "2 ఒకట్లు+4 ఒకట్లు=6 ఒకట్లు",
    "fs-id2210891": "5 ఒకట్లు+3 ఒకట్లు=8 ఒకట్లు",
    "fs-id1583137": "8 ఒకట్లు+4 ఒకట్లు=12 ఒకట్లు=1 పది+2 ఒకట్లు",
    "fs-id1389381": "5 ఒకట్లు+9 ఒకట్లు=14 ఒకట్లు=1 పది+4 ఒకట్లు",
    "fs-id1932178": "1 పది4 ఒకట్లు+7 పదులు5 ఒకట్లు=8 పదులు9 ఒకట్లు",
    "fs-id1509761": "1 పది5 ఒకట్లు+6 పదులు3 ఒకట్లు=7 పదులు8 ఒకట్లు",
    "fs-id2495783": "1 పది6 ఒకట్లు+2 పదులు5 ఒకట్లు=3 పదులు11 ఒకట్లు=4 పదులు1 ఒకటి",
    "fs-id1209935": "1 పది4 ఒకట్లు+2 పదులు7 ఒకట్లు=3 పదులు11 ఒకట్లు=4 పదులు1 ఒకటి",
}
TARGET_SOLUTION_MARKERS = {
    "fs-id2195542": "$1,875", "fs-id2264366": "138 మైళ్లు",
    "fs-id2609576": "1,167 చదరపు అడుగులు", "fs-id1962359": "$237,186",
    "fs-id2658194": "44 అంగుళాలు", "fs-id1718142": "56 మీటర్లు",
    "fs-id1788660": "71 గజాలు", "fs-id2427822": "62 అడుగులు",
    "fs-id1606437": "640 కేలరీలు", "fs-id1567863": "406 పాయింట్లు",
    "fs-id1369108": "1091 పౌండ్లు",
}
BRIDGE_ANSWER_MARKERS = {
    "fs-id2195542": "$1,875", "fs-id2452678": "$402",
    "fs-id2264366": "138 మైళ్లు (miles)",
    "fs-id1401775": "127 పూల అలంకరణలు (arrangements)",
    "fs-id2609576": "1,167 చదరపు అడుగులు (square feet)",
    "fs-id1946723": "1,295 పౌండ్లు (pounds)",
    "fs-id1962359": "$237,186", "fs-id1410524": "$1,222,114",
    "fs-id1606437": "640 కేలరీలు (calories)",
    "fs-id1215287": "1,230 కేలరీలు (calories)",
    "fs-id1567863": "పరీక్షల పాయింట్ల మొత్తం",
    "fs-id1369108": "వచ్చినది 1,091 పౌండ్లు",
}


def formatted(value):
    return f"{value:,}"


def formula(values, total=None):
    total = sum(values) if total is None else total
    return "+".join(formatted(value) for value in values) + "=" + formatted(total)


def require(node_or_text, phrases, context):
    value = node_or_text if isinstance(node_or_text, str) else text_of(node_or_text)
    for phrase in phrases:
        assert phrase in value, context + ": missing/changed " + phrase


def _strong_texts(node):
    return [text_of(item) for item in node.iter(XH + "strong")]


def _expected_column_relations(values):
    result = []
    for _, digits, incoming, total, _, _ in column_steps(values):
        operands_here = digits + ((incoming,) if incoming else ())
        result.append(formula(operands_here, total))
    return result


def _validate_column_table(detail, values, total):
    tables = list(detail.iter(XH + "table"))
    assert len(tables) == 1, "B019 expected one place/carry table"
    table = tables[0]
    headings = [text_of(node) for node in table.findall(XH + "thead/" + XH + "tr/" + XH + "th")]
    assert headings == ["స్థానం", "అంకెల మొత్తం", "ఈ స్థానంలో రాసేది", "తరువాతి స్థానానికి"]
    assert all(node.get("scope") == "col" for node in table.findall(XH + "thead/" + XH + "tr/" + XH + "th"))
    rows = table.findall(XH + "tbody/" + XH + "tr")
    steps = column_steps(values)
    assert len(rows) == len(steps) and all(len(row) == 4 for row in rows)
    expected_relations = []
    for row, (place, digits, incoming, column_total, written, outgoing) in zip(rows, steps):
        cells = [text_of(cell) for cell in row]
        assert row[0].tag == XH + "th" and row[0].get("scope") == "row"
        assert cells[0] == PLACE_TE[place]
        operands_here = digits + ((incoming,) if incoming else ())
        relation = formula(operands_here, column_total)
        assert compact(cells[1]) == relation and checked_equality(cells[1]) == (operands_here, column_total)
        assert cells[2] == str(written)
        if outgoing:
            # The column header already fixes this as a count in the *next*
            # place; the cell records the count, not its base-ten value.
            assert cells[3] == f"{outgoing} ప్రమాణం బదిలీ"
        else:
            assert cells[3] == "బదిలీ లేదు"
        expected_relations.append(relation)
    final = formula(values, total)
    assert final in [compact(value) for value in _strong_texts(detail)]
    expected_relations.append(final)
    assert Counter(displayed_equalities(detail)) == Counter(expected_relations), (
        "B019 place table/final equality collection changed")
    return len(rows), len(expected_relations)


def _validate_bridge_chart(detail, spec):
    tables = list(detail.iter(XH + "table"))
    assert len(tables) == 1
    table = tables[0]
    rows = list(table.iter(XH + "tr"))
    assert len(rows) == len(spec["rows"]) + 1
    assert all(len(row) == len(spec["cols"]) + 1 for row in rows)
    expected = []
    for row_index, row in enumerate(rows):
        cells = list(row)
        if row_index == 0:
            assert [text_of(cell) for cell in cells] == ["+"] + [str(value) for value in spec["cols"]]
            assert all(cell.tag == XH + "th" and cell.get("scope") == "col" for cell in cells)
            continue
        row_value = spec["rows"][row_index - 1]
        assert text_of(cells[0]) == str(row_value)
        assert cells[0].tag == XH + "th" and cells[0].get("scope") == "row"
        for cell, col_value in zip(cells[1:], spec["cols"]):
            relation = formula((row_value, col_value))
            assert compact(text_of(cell)) == relation
            assert checked_equality(text_of(cell)) == ((row_value, col_value), row_value + col_value)
            expected.append(relation)
    # The author includes two explicit endpoint check examples after each grid.
    first = formula((spec["rows"][0], spec["cols"][0]))
    last = formula((spec["rows"][-1], spec["cols"][-1]))
    expected.extend((first, last))
    assert Counter(displayed_equalities(detail)) == Counter(expected), (
        "B019 completed bridge chart changed")
    return (len(spec["rows"]), len(spec["cols"]), len(expected) - 2)


def _difference_relations(root):
    pattern = re.compile(r"(?<![0-9,])(" + NUMBER + r")\s*−\s*(" + NUMBER +
                         r")\s*=\s*(" + NUMBER + r")(?![0-9,])")
    result = []
    for node in root.iter():
        if local(node) not in {"p", "li", "td", "dd"}:
            continue
        if any(child is not node and local(child) in {"p", "li", "td", "dd"}
               for child in node.iter()):
            continue
        for match in pattern.finditer(text_of(node)):
            left, right, answer = map(number, match.groups())
            assert left - right == answer, "B019 incorrect displayed difference"
            result.append(f"{formatted(left)}−{formatted(right)}={formatted(answer)}")
    return result


def validate_review_bridge(target, bridge):
    """Validate all82 authored solution/rubric details and all chart/carry cells."""
    _, cases = source_cases()
    target_ids = ids_of(target)
    ids = ids_of(bridge)
    assert bridge.get("id") == "B019-bridge" and bridge.get("lang") == "te"
    expected_sections = ["B019-routing", "B019-notation", "B019-models", "B019-charts",
                         "B019-properties", "B019-numeric", "B019-phrases",
                         "B019-applications", "B019-perimeter", "B019-everyday",
                         "B019-writing", "B019-selfcheck-rubric"]
    assert [node.get("id") for node in bridge.findall(XH + "section")] == expected_sections
    details = list(bridge.iter(XH + "details"))
    assert [node.get("id") for node in details] == ["B019-S-" + ident for ident in EXERCISE_IDS]
    assert len(details) == 82
    all_expected_relations = Counter()
    carry_rows = 0
    bridge_chart_cells = 0
    source_supplied, editorial = 0, 0
    for case, detail in zip(cases, details):
        ident = case["id"]
        links = list(detail.iter(XH + "a"))
        assert len(links) == 1 and links[0].get("href") == "#" + ident
        assert ident in target_ids
        status = "మూలంలో ఇచ్చిన జవాబుకు పూర్తి కారణం" if case["solution_id"] else "మూలంలో లేని జవాబుకు సంపాదకీయ పూర్తి సాధన"
        assert status in text_of(detail), "B019 source-supplied/editorial classification changed"
        source_supplied += bool(case["solution_id"])
        editorial += not bool(case["solution_id"])
        kind = case["kind"]
        if kind == "notation":
            left, right = NOTATION_WORDS[ident]
            require(detail, [f"పఠనం: {left} ప్లస్ {right}",
                             f"ఫలితపు పేరు: {left}, {right} అనే సంఖ్యల మొత్తం",
                             "ఆ మొత్తాన్ని లెక్కించి సంఖ్యగా రాయడం అడగలేదు"],
                    "B019 notation reading/result name")
            assert not displayed_equalities(detail), "B019 notation answer cannot become evaluated equation"
        elif kind == "model":
            require(detail, [MODEL_REASON[ident], "పది ఒకట్లు ఏర్పడినప్పుడే",
                             "పరిమాణం మారలేదు"], "B019 complete block-model reasoning")
            relation = formula(case["operands"], case["total"])
            assert Counter(displayed_equalities(detail)) == Counter([relation])
            all_expected_relations[relation] += 1
        elif kind == "chart":
            _, _, count = _validate_bridge_chart(detail, case["chart"])
            bridge_chart_cells += count
            relations = displayed_equalities(detail)
            all_expected_relations.update(relations)
        elif kind == "property":
            expected = [formula(pair, case["total"]) for pair in case["pairs"]]
            assert Counter(displayed_equalities(detail)) == Counter(expected)
            require(detail, ["రెండు భాగాలూ పూర్తి జవాబులో అవసరం"], "B019 two-part property response")
            all_expected_relations.update(expected)
        elif kind in {"add", "phrase", "application", "everyday"}:
            values = case["operands"]
            rows, _ = _validate_column_table(detail, values, case["total"])
            carry_rows += rows
            all_expected_relations.update(displayed_equalities(detail))
            if kind == "phrase":
                assert formatted(case["total"]) in _strong_texts(detail)
            elif kind == "application":
                assert BRIDGE_ANSWER_MARKERS[ident] in text_of(detail), (
                    "B019 application answer value/unit changed")
                for incidental in case["incidental"]:
                    assert incidental not in values
            elif kind == "everyday":
                assert BRIDGE_ANSWER_MARKERS[ident] in text_of(detail), (
                    "B019 everyday answer value/unit changed")
                if case["comparison"] is None:
                    assert any(formatted(case["total"]) in value and
                               f"({case['unit']})" in value for value in _strong_texts(detail)), (
                        "B019 everyday answer value/unit changed")
                else:
                    op, threshold = case["comparison"]
                    difference = abs(case["total"] - threshold)
                    expected_difference = (f"{formatted(case['total'])}−{formatted(threshold)}={formatted(difference)}"
                                           if op == ">=" else
                                           f"{formatted(threshold)}−{formatted(case['total'])}={formatted(difference)}")
                    assert expected_difference in [compact(value) for value in _strong_texts(detail)]
        elif kind == "perimeter":
            unit = PERIMETER_UNIT_TEXT[case["unit"]]
            relation = formula(case["edges"], case["total"])
            assert Counter(displayed_equalities(detail)) == Counter([relation])
            assert any(formatted(case["total"]) in value and f"({unit})" in value
                       for value in _strong_texts(detail)), "B019 perimeter answer value/unit changed"
            assert "చదరపు" not in text_of(detail)
            if ident == "fs-id1960065":
                require(detail, ["సమస్య చిత్రంలో తెలియని పొడవును ముందే వెల్లడించలేదు",
                                 "10−7=3 అంగుళాలు (inches)",
                                 relation + " అంగుళాలు (inches)"],
                        "B019 derived closing side/perimeter")
            all_expected_relations[relation] += 1
        else:
            assert kind == "open"
            require(detail, ["ఒకే సరైన వాక్యం లేదు", "స్వీకరించదగిన సమాధానం"],
                    "B019 open writing acceptance rubric")
            expected = [] if ident == "fs-id1408863" else ["8+4=12"]
            assert displayed_equalities(detail) == expected
            all_expected_relations.update(expected)
    assert (source_supplied, editorial) == (42, 40)
    assert bridge_chart_cells == 297
    assert len(list(bridge.iter(XH + "table"))) == 54
    assert carry_rows == 173
    actual_relations = displayed_equalities(bridge)
    assert len(actual_relations) == 555 and Counter(actual_relations) == all_expected_relations
    assert Counter(_difference_relations(bridge)) == Counter({
        "10−7=3": 2, "406−400=6": 1, "1,150−1,091=59": 1})
    routing = [(node.get("href"), text_of(node)) for node in ids["B019-routing"].iter(XH + "a")]
    assert routing == [("TE-B013.html#fs-id2601285", "B013"),
                       ("TE-B014.html#fs-id2145437", "B014"),
                       ("TE-B015.html#fs-id1385496", "B015"),
                       ("TE-B016.html#fs-id2691382", "B016"),
                       ("TE-B017.html#fs-id2197427", "B017")]
    require(ids["B019-selfcheck-rubric"], ["ఐదు లక్ష్యాలకు ఒక్కొక్కటిగా",
            "నమ్మకంగా / కొంత సహాయంతో / ఇంకా అర్థం కాలేదు",
            "ఖాళీ స్పందన గడులు", "ఒకే సరైన ఎంపిక లేదు",
            "మార్కుగా లేదా స్థాయి తీర్పుగా వాడకండి"],
            "B019 open self-check rubric")
    assert [(node.get("href"), text_of(node)) for node in ids["B019-selfcheck-rubric"].iter(XH + "a")] == [
        ("#B019-routing", "పాఠల మార్గం")]
    require(ids["B019-disclosure"], ["మూలంలో ఉన్న 82 సాధనలను అదే క్రమంలో",
            "ఇచ్చిన 42 జవాబులకు", "మిగిలిన 40కు", "సంపాదకీయ"], "B019 scope disclosure")
    require(ids["B019-boundary"], ["Figure222", "5నిలువు వరుసలు×8వరుసలు",
            "Figure215 సమస్య altలో తెలియని3 inches లేదా70 inches జవాబు ముందే చూపలేదు",
            "మొత్తం భాషా కేటాయింపు ఇంకా కొనసాగుతుంది"], "B019 completion/accessibility boundary")
    links = list(bridge.iter(XH + "a"))
    assert len(ids) == 97 and len(links) == 88
    return {"bridge_solution_details": 82, "source_supplied_details": 42,
            "editorial_completion_details": 40, "bridge_tables": 54,
            "bridge_chart_formula_cells": 297, "bridge_carry_rows": carry_rows,
            "bridge_addition_equalities": len(actual_relations),
            "bridge_difference_equalities": len(_difference_relations(bridge)),
            "bridge_ids": len(ids), "bridge_links": len(links)}


def validate_b019(target, bridge):
    result = validate_review_target(target)
    result.update(validate_assets())
    result.update(validate_review_bridge(target, bridge))
    return result
