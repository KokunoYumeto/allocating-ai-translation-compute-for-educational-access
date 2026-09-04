"""Pinned TE-B006 rounding media: selected originals and code-native SVGs.

No downloads or bulk extraction. --verify and --self-test perform no writes.
"""
from pathlib import Path
import argparse
import hashlib
import html
import json
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile

from make_b005_assets import need, digest, file_digest, node, label

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parent
OUT = BASE / "assets/B006"
SOURCE = BASE / "sources/TE-B006.en.cnxml"
SOURCE_SHA = "b0644c64501fbf41c50c2119a5e1b68c7d0c4294eeaa82dca3f495c4853df2af"
COMMIT = "38cae454e644abf9f0a623e876994553881597c9"
ARCHIVE_SHA = "effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917"
PREFIX = "osbooks-prealgebra-bundle-" + COMMIT + "/"
CN = "{http://cnx.rice.edu/cnxml}"
SVG = "{http://www.w3.org/2000/svg}"
STEM = "CNX_BMath_Figure_01_01_"
NAMES = ([f"{STEM}{n:03}.jpg" for n in (19,20,21,22)] +
         [f"{STEM}{n:03}_img.jpg" for n in (31,32,33)] +
         [f"{STEM}034_img-{n:02}.png" for n in (1,2,3,4)] +
         [f"{STEM}{n:03}_img-{p:02}.png" for n in (35,36,37,38) for p in (1,2,3)])
ET.register_namespace("", SVG[1:-1])
INK, TEAL, RED, MUTED = "#153a4b", "#006b67", "#ad292e", "#426271"
PLACES = {
    10: ("పదుల స్థానం", "tens place", "దగ్గరి పదులకు సవరించండి", "round to the nearest ten"),
    100: ("వందల స్థానం", "hundreds place", "దగ్గరి వందలకు సవరించండి", "round to the nearest hundred"),
    1000: ("వేల స్థానం", "thousands place", "దగ్గరి వేలకు సవరించండి", "round to the nearest thousand"),
}
# The specification below was transcribed from all 23 inspected original images
# AND the surrounding frozen source. Intermediate-only images stay intermediate.
SPECS = {
    "019": dict(kind="line", n=76, place=10),
    "020": dict(kind="line", n=72, place=10),
    "021": dict(kind="line", n=75, place=10),
    "022": dict(kind="compare", n=76, place=10),
    "031_img": dict(kind="operation", n=76, place=10, result=80, cross=True, caption=True),
    "032_img": dict(kind="compare", n=72, place=10),
    "033_img": dict(kind="operation", n=72, place=10, result=70, cross=True),
    "034_img-01": dict(kind="locate", n=843, place=10),
    "034_img-02": dict(kind="neighbor", n=843, place=10),
    "034_img-03": dict(kind="neighbor", n=843, place=10),
    "034_img-04": dict(kind="answer", n=843, place=10, result=840, underline=0),
    "035_img-01": dict(kind="locate", n=23658, place=100),
    "035_img-03": dict(kind="neighbor", n=23658, place=100),
    "035_img-02": dict(kind="operation", n=23658, place=100, result=23700),
    "036_img-01": dict(kind="locate", n=3978, place=100),
    "036_img-03": dict(kind="neighbor", n=3978, place=100),
    "036_img-02": dict(kind="operation", n=3978, place=100, result=4000, carry=True),
    "037_img-01": dict(kind="locate", n=147032, place=1000),
    "037_img-02": dict(kind="neighbor", n=147032, place=1000),
    "037_img-03": dict(kind="answer", n=147032, place=1000, result=147000),
    "038_img-01": dict(kind="locate", n=29504, place=1000),
    "038_img-02": dict(kind="neighbor", n=29504, place=1000),
    "038_img-03": dict(kind="operation", n=29504, place=1000, result=30000, carry=True),
}
DISCREPANCIES = {
    **{key: {"source_alt_claim": "orange dot; all non-endpoint labels black",
              "inspected_pixels": "teal/turquoise dot and selected label; red endpoints",
              "adaptation": "Dark teal selected point/label; red endpoints; exact locations unchanged."}
       for key in ("019", "020", "021")},
    "032_img": {"inspected_pixels": "ten's place", "source_alt_claim": "tens place",
                "adaptation": "Use standard English tens place alongside Telugu; apostrophe typo not reproduced."},
    "036_img-02": {
        "source_alt_claim": "nearest thousand; hundreds digit9 controls",
        "inspected_pixels": "add1 (9+1=10); Write0 in the hundreds place. Add1 to the thousands place.; 3,978 to4,000",
        "source_context": "eip-379 and fs-id3407439 request nearest hundred; tens7 controls",
        "adaptation": "Nearest hundred, target hundreds9; add1 gives10, write0 hundreds and carry1 to thousands3. Frozen source and original PNG unchanged."},
    "038_img-03": {
        "source_alt_claim": "nearest ten thousand",
        "inspected_pixels": "add1 (9+1=10); Write0 in the thousands place. Add1 to the ten thousands place.; 29,504 to30,000",
        "source_context": "eip-596 and fs-id1263758 request nearest thousand; hundreds5 controls",
        "adaptation": "Nearest thousand, target thousands9; add1 gives10, write0 thousands and carry1 to ten-thousands2. Frozen source and original PNG unchanged."},
}


def half_up(n, place):
    """Nonnegative whole-number rule in this lesson; never Python round()."""
    need(isinstance(n, int) and n >= 0 and place in (10, 100, 1000), "Unsupported rounding domain")
    q, r = divmod(n, place)
    return (q + (2*r >= place)) * place


def exponent(place):
    return {10: 1, 100: 2, 1000: 3}[place]


def dimensions(key):
    kind = SPECS[key]["kind"]
    return {"line": (900, 180), "compare": (680, 290), "locate": (600, 220),
            "neighbor": (600, 150), "answer": (600, 150), "operation": (1080, 530)}[kind]


def selected(root, role):
    return [el for el in root.iter() if el.get("data-role") == role]


def exact_text(root, role, expected):
    need([el.text or "" for el in selected(root, role)] == expected, "Wrong visible " + role)


def numeral(parent, value, center, y, role, size=54, step=43):
    text = f"{value:,}"
    group = node(parent, "g", {"data-role": role})
    positions, power = {}, len(str(value))-1
    for i, char in enumerate(text):
        x = center + (i-(len(text)-1)/2)*step
        if char == ",":
            label(group, x, y, char, size, **{"data-role": "comma"})
        else:
            label(group, x, y, char, size, **{"data-role": "digit", "data-power": power})
            positions[power] = x
            power -= 1
    return positions


def arrow(parent, x1, y1, x2, y2, role, **attrs):
    return node(parent, "line", {"x1": x1, "y1": y1, "x2": x2, "y2": y2,
        "stroke": TEAL, "stroke-width": 3, "marker-end": "url(#arrowhead)",
        "data-role": role, **attrs})


def underline(parent, x, y, power, role="neighbor-underline"):
    return node(parent, "line", {"x1": x-17, "x2": x+17, "y1": y, "y2": y,
        "stroke": INK, "stroke-width": 3, "data-role": role, "data-power": power})


def operation_lines(spec):
    up = (spec["n"] // (spec["place"]//10)) % 10 >= 5
    if spec.get("carry"):
        lower_te, upper_te = (("వందల స్థానంలో 0 రాయండి.", "వేల స్థానంలో 1 కలపండి.")
            if spec["place"] == 100 else ("వేల స్థానంలో 0 రాయండి.", "పది వేల స్థానంలో 1 కలపండి."))
        lower_en, upper_en = (("Write 0 in the hundreds place.", "Add 1 to the thousands place.")
            if spec["place"] == 100 else ("Write 0 in the thousands place.", "Add 1 to the ten thousands place."))
        return [("1 కలపండి: 9 + 1 = 10", "add 1: 9 + 1 = 10"),
                (lower_te, lower_en), (upper_te, upper_en)]
    return [("1 కలపండి" if up else "1 కలపవద్దు", "add 1" if up else "do not add 1")]


def description(key):
    s = SPECS[key]
    n, place, kind = s["n"], s["place"], s["kind"]
    p = exponent(place)
    target, neighbor = n//place % 10, n//(place//10) % 10
    result = s.get("result")
    if kind == "line":
        text = f"సంఖ్యారేఖ / number line: 70 through80, unit intervals; teal point at{n}. Red endpoints70/80. No rounding answer is added in this figure."
    elif kind == "locate":
        text = f"{n:,}: {PLACES[place][0]} ({PLACES[place][1]}) points to digit{target}. No answer added."
    elif kind == "neighbor":
        text = f"{n:,}: immediately right of the {PLACES[place][1]}, digit{neighbor} in the 10^{p-1} place is underlined. No answer added."
    elif kind == "answer":
        text = f"{result:,}" + (": final zero underlined." if "underline" in s else ".")
    elif kind == "compare":
        relation = "greater than" if neighbor > 5 else "less than"
        text = f"{n}: Telugu and English labels identify{target} as tens digit; underlined ones digit{neighbor} is{relation}5."
    else:
        action = "; ".join(en for te, en in operation_lines(s))
        text = f"{PLACES[place][2]} / {PLACES[place][3]}. {n:,} to{result:,}; target digit{target}; {action}; replace all digits to the right with0s."
        if s.get("cross"):
            text += f" Source ones digit{neighbor} is crossed out."
        if s.get("caption"):
            text += " Source caption retained bilingually:76 rounded to the nearest ten is80."
    return text + " New code-native bilingual redraw. Original raster unchanged. Arrows, underlines and numeral positions carry meaning independently of color."


def diagram(key):
    s = SPECS[key]
    n, place, kind = s["n"], s["place"], s["kind"]
    p = exponent(place)
    width, height = dimensions(key)
    root = ET.Element(SVG+"svg", {"width": str(width), "height": str(height),
        "viewBox": f"0 0 {width} {height}", "role": "img", "aria-labelledby": "title desc",
        "lang": "te", "font-family": "Nirmala UI, Noto Sans Telugu, sans-serif",
        "data-source-number": str(n), "data-rounding-unit": str(place), "data-kind": kind})
    node(root, "title", {"id": "title"}, "సవరించి రాయడం / rounding: " + key)
    node(root, "desc", {"id": "desc"}, description(key))
    node(root, "rect", {"width": width, "height": height, "fill": "white"})
    defs = node(root, "defs")
    marker = node(defs, "marker", {"id": "arrowhead", "viewBox": "0 0 10 10", "refX": 8,
        "refY": 5, "markerWidth": 7, "markerHeight": 7, "orient": "auto-start-reverse"})
    node(marker, "path", {"d": "M0 0L10 5L0 10Z", "fill": TEAL})
    if kind == "line":
        node(root, "line", {"x1": 25, "x2": 875, "y1": 100, "y2": 100,
            "stroke": INK, "stroke-width": 3, "marker-start": "url(#arrowhead)",
            "marker-end": "url(#arrowhead)", "data-role": "number-line-axis"})
        for value in range(70,81):
            x = 60 + (value-70)*78
            group = node(root, "g", {"data-role": "tick", "data-value": value})
            node(group, "line", {"x1": x, "x2": x, "y1": 90, "y2": 110,
                "stroke": INK, "stroke-width": 2})
            color = RED if value in (70,80) else TEAL if value == n else INK
            label(group, x, 65, str(value), 28, color, **{"data-role": "tick-label"})
        node(root, "circle", {"cx": 60+(n-70)*78, "cy": 100, "r": 9,
            "fill": TEAL, "data-role": "selected-point", "data-value": n})
    elif kind in ("neighbor", "answer"):
        value = s.get("result", n)
        positions = numeral(root, value, width//2, 85, "result" if kind == "answer" else "input")
        if kind == "neighbor":
            underline(root, positions[p-1], 99, p-1)
        elif "underline" in s:
            underline(root, positions[s["underline"]], 99, s["underline"], "result-underline")
    elif kind == "locate":
        positions = numeral(root, n, width//2, 183, "input")
        x = positions[p]
        label(root, x, 45, PLACES[place][0], 28, TEAL, **{"data-role": "place-te"})
        label(root, x, 78, PLACES[place][1], 23, TEAL, **{"lang": "en", "data-role": "place-en"})
        arrow(root, x, 98, x, 132, "target-arrow", **{"data-power": p})
    elif kind == "compare":
        positions = numeral(root, n, width//2, 230, "input")
        neighbor = n%10
        label(root, 155, 50, PLACES[place][0], 27, TEAL, **{"data-role": "place-te"})
        label(root, 155, 82, PLACES[place][1], 22, TEAL, **{"lang": "en", "data-role": "place-en"})
        relation_te = "5 కంటే పెద్దది" if neighbor > 5 else "5 కంటే చిన్నది"
        relation_en = "is greater than 5" if neighbor > 5 else "is less than 5"
        label(root, 525, 50, relation_te, 27, RED, **{"data-role": "comparison-te"})
        label(root, 525, 82, relation_en, 22, RED, **{"lang": "en", "data-role": "comparison-en"})
        arrow(root, 155, 103, positions[p], 178, "target-arrow", **{"data-power": p})
        arrow(root, 525, 103, positions[p-1], 178, "neighbor-arrow", **{"data-power": p-1})
        underline(root, positions[p-1], 244, p-1)
    else:
        # Wider than compact source snippets so the bilingual carry explanation
        # has its own column; no text is placed over the numeral or its links.
        label(root, width//2, 37, PLACES[place][2], 27, TEAL, **{"data-role": "rounding-te"})
        label(root, width//2, 70, PLACES[place][3], 22, TEAL, **{"lang": "en", "data-role": "rounding-en"})
        positions = numeral(root, n, 610, 164, "input")
        lines = operation_lines(s)
        for i, (te, en) in enumerate(lines):
            label(root, 24, 190+i*67, te, 24, RED, anchor="start", **{"data-role": "operation-te"})
            label(root, 24, 220+i*67, en, 21, RED, anchor="start", **{"lang": "en", "data-role": "operation-en"})
        arrow(root, 395, 180, positions[p]-5, 172, "target-arrow", **{"data-power": p})
        suffix_left, suffix_right = positions[p-1]-18, positions[0]+18
        if s.get("cross"):
            node(root, "line", {"x1": positions[0]-20, "x2": positions[0]+20,
                "y1": 124, "y2": 168, "stroke": RED, "stroke-width": 3,
                "data-role": "cross-out", "data-power": 0})
        else:
            node(root, "path", {"d": f"M{suffix_left} 178V191H{suffix_right}V178",
                "fill": "none", "stroke": TEAL, "stroke-width": 2,
                "data-role": "suffix-bracket", "data-low-power": 0, "data-high-power": p-1})
        replace_te = "0 తో భర్తీ చేయండి" if place == 10 else "0లతో భర్తీ చేయండి"
        replace_en = "replace with 0" if place == 10 else "replace with 0s"
        label(root, 874, 257, replace_te, 25, RED, **{"data-role": "replace-te"})
        label(root, 874, 289, replace_en, 22, RED, **{"lang": "en", "data-role": "replace-en"})
        arrow(root, 874, 216, (suffix_left+suffix_right)/2, 198, "replace-arrow",
              **{"data-low-power": 0, "data-high-power": p-1})
        arrow(root, 610, 222, 610, 375, "result-arrow")
        numeral(root, s["result"], 610, 437, "result")
        if s.get("caption"):
            label(root, 540, 485, "76 ను దగ్గరి పదులకు సవరిస్తే 80 వస్తుంది.", 25,
                  **{"data-role": "source-caption-te"})
            label(root, 540, 515, "76 rounded to the nearest ten is 80.", 21,
                  **{"lang": "en", "data-role": "source-caption-en"})
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"


def check_numeral(root, role, value, center, y):
    groups = selected(root, role)
    need(len(groups) == 1, "Missing or duplicate " + role)
    group = groups[0]
    text = f"{value:,}"
    need("".join(el.text or "" for el in group) == text, "Wrong visible " + role + " numeral/comma")
    power, positions = len(str(value))-1, {}
    need(len(group) == len(text), "Wrong numeral character count")
    for i, (el, char) in enumerate(zip(group, text)):
        x = center+(i-(len(text)-1)/2)*43
        need(el.tag == SVG+"text" and float(el.get("x")) == x and float(el.get("y")) == y,
             "Wrong numeral geometry")
        if char == ",":
            need(el.get("data-role") == "comma", "Missing numeral comma")
        else:
            need(el.get("data-role") == "digit" and el.get("data-power") == str(power), "Wrong digit power")
            positions[power] = x
            power -= 1
    return positions


def check_arrow(root, role, x1, y1, x2, y2, power=None):
    arrows = selected(root, role)
    need(len(arrows) == 1, "Missing/duplicate " + role)
    arrow_node = arrows[0]
    need(arrow_node.tag == SVG+"line" and arrow_node.get("marker-end") == "url(#arrowhead)", "Arrowhead missing")
    need([float(arrow_node.get(k)) for k in ("x1", "y1", "x2", "y2")] == [x1,y1,x2,y2], "Wrong arrow endpoint: " + role)
    if power is not None:
        need(arrow_node.get("data-power") == str(power), "Arrow targets wrong place")


def check_underline(root, x, y, power, role="neighbor-underline"):
    lines = selected(root, role)
    need(len(lines) == 1, "Missing/duplicate underline")
    line = lines[0]
    need(line.tag == SVG+"line" and line.get("data-power") == str(power), "Underline marks wrong place")
    need([float(line.get(k)) for k in ("x1", "y1", "x2", "y2")] == [x-17,y,x+17,y], "Underline geometry wrong")


def math_check(key, payload):
    """Parse actual SVG text and geometry, not only a metadata assertion."""
    s, root = SPECS[key], ET.fromstring(payload)
    n, place, kind = s["n"], s["place"], s["kind"]
    p, (width, height) = exponent(place), dimensions(key)
    need(root.tag == SVG+"svg" and root.get("viewBox") == f"0 0 {width} {height}", "Wrong canvas")
    need(not list(root.iter(SVG+"image")) and not list(root.iter(SVG+"script")), "Not code-native/static")
    need(root.get("role") == "img" and root.get("aria-labelledby") == "title desc", "Missing accessible name")
    need(root.find(SVG+"title") is not None and root.find(SVG+"desc").text == description(key), "Changed accessible description")
    need(root.get("data-source-number") == str(n) and root.get("data-rounding-unit") == str(place)
         and root.get("data-kind") == kind, "Wrong number/place/kind")
    if "result" in s:
        need(s["result"] == half_up(n, place), "Rounding arithmetic wrong")
    # Output cannot be invented in figures which contain no source answer.
    need(len(selected(root, "result")) == int("result" in s), "Invented or missing answer")
    if kind == "line":
        need(not selected(root, "input"), "Added numeral outside number line")
        ticks = selected(root, "tick")
        need([el.get("data-value") for el in ticks] == [str(v) for v in range(70,81)], "Tick values/count changed")
        for value, tick in zip(range(70,81), ticks):
            x = 60+(value-70)*78
            need(len(tick) == 2 and tick[0].tag == SVG+"line", "Tick mark missing")
            need([float(tick[0].get(k)) for k in ("x1","y1","x2","y2")] == [x,90,x,110], "Non-unit tick spacing")
            need(tick[1].text == str(value) and float(tick[1].get("x")) == x and tick[1].get("y") == "65", "Visible tick label changed")
            need(tick[1].get("fill") == (RED if value in (70,80) else TEAL if value == n else INK), "Endpoint/selected color changed")
        points = selected(root, "selected-point")
        need(len(points) == 1 and points[0].get("data-value") == str(n), "Wrong point value/count")
        need([float(points[0].get(k)) for k in ("cx","cy")] == [60+(n-70)*78,100]
             and points[0].get("fill") == TEAL, "Point geometry/color wrong")
        axis = selected(root, "number-line-axis")
        need(len(axis) == 1 and axis[0].get("marker-start") == axis[0].get("marker-end") == "url(#arrowhead)", "Missing two number-line directions")
    elif kind in ("neighbor", "answer"):
        positions = check_numeral(root, "result" if kind == "answer" else "input", s.get("result",n), width//2,85)
        if kind == "neighbor":
            check_underline(root, positions[p-1],99,p-1)
        elif "underline" in s:
            check_underline(root, positions[s["underline"]],99,s["underline"],"result-underline")
        else:
            need(not selected(root,"result-underline"), "Invented answer underline")
    elif kind in ("locate", "compare"):
        y = 183 if kind == "locate" else 230
        positions = check_numeral(root,"input",n,width//2,y)
        exact_text(root,"place-te",[PLACES[place][0]])
        exact_text(root,"place-en",[PLACES[place][1]])
        if kind == "locate":
            check_arrow(root,"target-arrow",positions[p],98,positions[p],132,p)
        else:
            check_arrow(root,"target-arrow",155,103,positions[p],178,p)
            check_arrow(root,"neighbor-arrow",525,103,positions[p-1],178,p-1)
            check_underline(root,positions[p-1],244,p-1)
            exact_text(root,"comparison-te",["5 కంటే పెద్దది" if n%10 >5 else "5 కంటే చిన్నది"])
            exact_text(root,"comparison-en",["is greater than 5" if n%10 >5 else "is less than 5"])
    else:
        positions = check_numeral(root,"input",n,610,164)
        check_numeral(root,"result",s["result"],610,437)
        exact_text(root,"rounding-te",[PLACES[place][2]])
        exact_text(root,"rounding-en",[PLACES[place][3]])
        exact_text(root,"operation-te",[te for te,en in operation_lines(s)])
        exact_text(root,"operation-en",[en for te,en in operation_lines(s)])
        exact_text(root,"replace-te",["0 తో భర్తీ చేయండి" if place==10 else "0లతో భర్తీ చేయండి"])
        exact_text(root,"replace-en",["replace with 0" if place==10 else "replace with 0s"])
        check_arrow(root,"target-arrow",395,180,positions[p]-5,172,p)
        a, b = positions[p-1]-18, positions[0]+18
        check_arrow(root,"replace-arrow",874,216,(a+b)/2,198)
        replace = selected(root,"replace-arrow")[0]
        need(replace.get("data-low-power") == "0" and replace.get("data-high-power") == str(p-1), "Wrong replaced digit range")
        check_arrow(root,"result-arrow",610,222,610,375)
        if s.get("cross"):
            crosses = selected(root,"cross-out")
            need(len(crosses) == 1 and crosses[0].get("data-power") == "0", "Wrong crossed-out place")
            need([float(crosses[0].get(k)) for k in ("x1","y1","x2","y2")] == [positions[0]-20,124,positions[0]+20,168], "Cross-out geometry wrong")
        else:
            brackets = selected(root,"suffix-bracket")
            need(len(brackets)==1 and brackets[0].get("d") == f"M{a} 178V191H{b}V178", "Bracket does not group replaced suffix")
            need(brackets[0].get("data-low-power") == "0" and brackets[0].get("data-high-power") == str(p-1), "Wrong suffix bracket range")
        exact_text(root,"source-caption-en",["76 rounded to the nearest ten is 80."] if s.get("caption") else [])
        exact_text(root,"source-caption-te",["76 ను దగ్గరి పదులకు సవరిస్తే 80 వస్తుంది."] if s.get("caption") else [])
        target, adjacent = n//place%10, n//(place//10)%10
        up = adjacent >=5
        need(bool(s.get("carry")) == bool(up and target==9), "Carry condition wrong")
        need(s["result"] == ((n//place)+int(up))*place, "Adjacent-digit procedure differs from half-up oracle")
    # No opaque off-canvas figures; actual rendered text still needs visual QA.
    for text_node in root.iter(SVG+"text"):
        need(0 <= float(text_node.get("x")) <= width and 0 <= float(text_node.get("y")) <= height, "Text anchor outside canvas")
    return {"source_number": n, "rounding_unit": place, "target_digit": n//place%10,
        "controlling_digit": n//(place//10)%10, "controlling_place_unit": place//10,
        "source_answer_displayed": s.get("result"), "half_up_result": half_up(n,place),
        "intermediate_answer_not_invented": "result" not in s, "visible_digits_and_geometry": "PASS",
        "carry_to_next_place": bool(s.get("carry")), "source_international_commas": "PASS"}


def self_test():
    rejected = 0
    for key,s in SPECS.items():
        payload = diagram(key)
        math_check(key,payload)
        mutations = ["number", "place", "digit", "answer"]
        if s["kind"] == "line":
            mutations += ["point", "tick", "line-direction"]
        if s["kind"] in ("locate", "compare", "operation"):
            mutations += ["target-arrow", "target-text"]
        if s["kind"] in ("neighbor","compare") or "underline" in s:
            mutations += ["underline"]
        if s["kind"] == "operation":
            mutations += ["operation", "zeros", "replace-arrow", "result-arrow", "carry-place"]
        for mutation in mutations:
            root = ET.fromstring(payload)
            if mutation == "number":
                root.set("data-source-number","0")
            elif mutation == "place":
                root.set("data-rounding-unit", str(s["place"]*10))
            elif mutation == "digit":
                el = (selected(root,"digit") or selected(root,"tick-label"))[-1]
                el.text = "1" if el.text != "1" else "2"
            elif mutation == "answer":
                answers = selected(root,"result")
                if answers:
                    root.remove(answers[0])
                else:
                    numeral(root,half_up(s["n"],s["place"]),10,10,"result")
            elif mutation == "point":
                selected(root,"selected-point")[0].set("cx","60")
            elif mutation == "tick":
                selected(root,"tick")[1][0].set("x1","61")
            elif mutation == "line-direction":
                selected(root,"number-line-axis")[0].attrib.pop("marker-start")
            elif mutation == "target-arrow":
                selected(root,"target-arrow")[0].set("x2","1")
            elif mutation == "target-text":
                (selected(root,"place-en") or selected(root,"rounding-en"))[0].text = "ten thousands place"
            elif mutation == "underline":
                (selected(root,"neighbor-underline") or selected(root,"result-underline"))[0].set("data-power","9")
            elif mutation == "operation":
                selected(root,"operation-en")[0].text = "add 2"
            elif mutation == "zeros":
                result = selected(root,"result")[0]
                result.remove(list(result)[-1])
            elif mutation == "replace-arrow":
                selected(root,"replace-arrow")[0].set("data-high-power","9")
            elif mutation == "result-arrow":
                selected(root,"result-arrow")[0].set("y2","111")
            elif mutation == "carry-place":
                lines = selected(root,"operation-te")
                lines[-1].text = "పదుల స్థానంలో 1 కలపండి."
            try:
                math_check(key,ET.tostring(root))
            except ValueError:
                rejected += 1
            else:
                raise AssertionError("Accepted corruption: " + key + "/" + mutation)
    # Same-answer, wrong-target regressions are intentionally separate checks.
    need(half_up(3978,100) == half_up(3978,1000) == 4000, "Carry regression setup")
    need(half_up(29504,1000) == 30000, "Carry regression setup")
    need(half_up(75,10)==80 and half_up(85,10)==90 and half_up(0,10)==0, "Tie convention changed")
    need(half_up(147032,1000)==147000, "Skipped adjacent zero")
    need(half_up(149,100)==100 and half_up(half_up(149,10),100)==200, "Direct rounding regression")
    print(f"PASS:23 SVGs;{rejected} actual-SVG corruption fixtures rejected; integer half-up and target-place tests; no writes")


def build(verify=False, originals_only=False):
    records,total = source_assets(write_originals=not verify)
    if originals_only:
        print(json.dumps({"original_count":len(records),"original_bytes":total,"pinned_originals":"PASS"}))
        return
    for record in records:
        key = record.pop("key")
        payload = diagram(key)
        record.update(math_checks=math_check(key,payload), localized_sha256=digest(payload),
            localized_bytes=len(payload), recommended_min_width_px=dimensions(key)[0],
            disclosure="New code-native bilingual mathematical redraw; original raster bytes unchanged. Added target headings contextualize operation panels; no answers added to intermediate-only source images.")
        if key in DISCREPANCIES:
            record["source_discrepancy"] = DISCREPANCIES[key]
        record["source_pixel_notes"] = {
            "031_img":"Only031 includes visible bottom caption76 rounded to nearest ten is80; retained bilingually.",
            "034_img-02":"843, ones3 underlined; same mathematical image as034_img-03.",
            "034_img-03":"843, ones3 underlined; preserved as a distinct source media mapping.",
            "034_img-04":"840 with final0 underlined; no deleted digit.",
            "037_img-02":"147,032; hundreds0 underlined, not tens3 or ones2.",
            "037_img-03":"147,000 without a place label or underline; no extra source caption invented."
        }.get(key,"Exact input, visible place labels, arrows, underlines and displayed result checked against original raster.")
        target = BASE/record["localized_path"]
        if verify:
            actual = target.read_bytes()
            math_check(key,actual)
            need(actual == payload,"SVG differs from deterministic generator")
        else:
            target.write_bytes(payload)
    manifest = {"schema":"te-b002-assets-v1", "unit":"TE-B006", "source_subsection_id":"fs-id2472737",
        "source_subsection_sha256":SOURCE_SHA,"canonical_commit":COMMIT,"canonical_archive_sha256":ARCHIVE_SHA,
        "source_attribution":"OpenStax, Prealgebra 2e; existing project notices and attribution remain applicable.",
        "generator":"scripts/make_b006_assets.py",
        "verification_command":"python -B te-Telu-IN/scripts/make_b006_assets.py --verify",
        "self_test_command":"python -B te-Telu-IN/scripts/make_b006_assets.py --self-test",
        "scope":"Exactly23 selected unchanged raster originals and23 newly generated SVGs; no downloads or bulk extraction.",
        "canon_consulted":["canon/B006-rounding-witness.md","TS6 PDF14/printed4","TS6 PDF15/printed5 valid5078/29,500 expansions","TS6 PDF17/printed7 carry sequence"],
        "choices":[
            "Read complete frozen source, rounding witness, and existing Telugu+English OCR14/15/17 before inspecting their complete page images. Existing OCR reused, not a new OCR run.",
            "Read all23 selected original raster members from the SHA-verified archive; inspected each full image before drawing. Original bytes checked by selected-member ZIP CRC and pinned Git blob SHA1. Sparse repository stays sparse.",
            "Use witnessed nearby-place wording with English glosses: tens/hundreds/thousands labels distinguish target from the immediately-right control digit. AP terminology/native approval remain open.",
            "Line019/020/021 is70..80 with unit spacing, teal selected76/72/75 and red endpoints. Source alt orange color conflicts with viewed pixels; use darker teal for contrast. No rounding answers added to these source line figures.",
            "Visible neighbor marks are underlines, not circles. Retain single-digit underlines including147,032 hundreds0; do not skip it. Retain exact source commas, digits and required result zeros.",
            "036_img-02 nearest-hundred and038_img-03 nearest-thousand source-alt errors are corrected only in the localized adaptation, with explicit per-asset evidence. Same numerical answers at wrong targets do not pass target/neighbor checks.",
            "Carry panels preserve9+1=10, write0 at requested position and add1 to the next position. Replacement brackets cover only lower places; carry0 at the target is separate. Intermediate source images never acquire a new answer.",
            "031 source bottom caption is retained bilingually.032 apostrophe typo ten's place becomes standard tens place.034 source PNG files declare JPEG MIME; originals unchanged, SVG localized MIME is image/svg+xml.",
            "Bilingual code-native geometry adapts layout and palette; operation panels add an explicit contextual target heading. These are editorial diagram adaptations, not original-image edits or new canon quotations.",
            "Nonnegative whole-number half-up convention verified with integer quotient/remainder, never Python round. Original75 midpoint goes up; digit5 does not imply every source number is exactly halfway.",
            "Reader must honor minimum widths within keyboard-focusable local scroll containers. Text-anchor bounds/geometry tests are not a substitute for actual font rendering; main visual QA remains separate."
        ],
        "assets":records,
        "qa":{"selected_original_count":len(records),"original_bytes":total,"localized_svg_count":len(records),
            "localized_bytes":sum(r["localized_bytes"] for r in records),"selected_original_crc_and_git_blob_hashes":"PASS",
            "actual_svg_digits_targets_neighbors_answers_geometry":"PASS",
            "visual_svg_review":"Pending separate rendered inspection; author inspected all23 original rasters, not an independent review of generated SVGs."}}
    encoded = (json.dumps(manifest,ensure_ascii=False,indent=2)+"\n").encode()
    if verify:
        need((OUT/"manifest.json").read_bytes()==encoded,"Manifest differs from source/generator")
    else:
        (OUT/"manifest.json").write_bytes(encoded)
        sections=[]
        for record in records:
            sections.append('<section><h2>'+html.escape(record["media_id"])+'</h2><p>Unchanged source: '+html.escape(Path(record["original_path"]).name)+'</p><img class="original" src="original/'+Path(record["original_path"]).name+'" alt="Preserved original rounding diagram"><p>New bilingual code-native redraw</p><div class="pan" tabindex="0" role="region" aria-label="Bilingual diagram, horizontally scrollable"><img style="width:'+str(record["recommended_min_width_px"])+'px" src="'+Path(record["localized_path"]).name+'" alt="Bilingual rounding diagram; full description in SVG"></div></section>')
        preview='<!doctype html><html lang="te"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>B006 diagram QA</title><style>body{font-family:"Nirmala UI",sans-serif;color:#153a4b;background:#edf4f3;margin:24px}main{max-width:1140px;margin:auto}section{background:white;padding:20px;margin:24px 0}.original{max-width:100%;height:auto}.pan{max-width:100%;overflow-x:auto;border:1px solid #9bc9c0}.pan img{display:block;max-width:none;height:auto}</style><main><h1>B006 source and localized diagrams</h1>'+''.join(sections)+'</main></html>\n'
        (OUT/"preview.html").write_text(preview,encoding="utf-8")
    print(json.dumps({"status":"PASS",**manifest["qa"]}))


def source_assets(write_originals=False):
    need(file_digest(SOURCE) == SOURCE_SHA, "Frozen B006 changed")
    metadata = json.loads((BASE / "sources/TE-B006.source.json").read_text("utf-8"))
    need(metadata["unit"] == "TE-B006" and metadata["source_sha256"] == SOURCE_SHA
         and metadata["source_commit"] == COMMIT, "Unpinned metadata")
    source = ET.parse(SOURCE).getroot()
    need(source.get("id") == "fs-id2472737", "Wrong subsection")
    parents = {child: parent for parent in source.iter() for child in parent}
    images = list(source.iter(CN + "image"))
    need(len(images) == 23 and {im.get("src") for im in images} ==
         {"../../media/" + n for n in NAMES}, "Source media set changed")
    lock = json.loads((BASE / "sources.lock.json").read_text("utf-8"))
    archive = next(a for a in lock["canonical_archives"] if a["id"] == "A00-A20-en-complete-archive")
    need(archive["sha256"] == ARCHIVE_SHA and archive["commit"] == COMMIT, "Unpinned archive")
    path = ROOT / archive["path"]
    need(path.stat().st_size == archive["bytes"] and file_digest(path) == ARCHIVE_SHA, "Archive size/SHA mismatch")
    selected = ["media/" + Path(im.get("src")).name for im in images]
    env = os.environ.copy()
    env.update(GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
    tree = subprocess.check_output(["git", "-C", str(ROOT / "downloads/upstream-prealgebra"),
        "ls-tree", "-r", "-z", COMMIT, "--", *selected], env=env)
    blobs = {}
    for row in tree.split(b"\0"):
        if row:
            header, name = row.split(b"\t", 1)
            _, kind, oid = header.split()
            need(kind == b"blob", "Selected object is not a blob")
            blobs[name.decode()] = oid.decode()
    need(set(blobs) == set(selected), "Selected pinned blobs missing")
    if write_originals:
        need(shutil.disk_usage(BASE).free >= 32*1024*1024, "Insufficient free space")
    records, total = [], 0
    with zipfile.ZipFile(path) as package:
        need(package.comment.decode() == COMMIT, "Wrong ZIP commit comment")
        for image, name in zip(images, selected):
            member = PREFIX + name
            info = package.getinfo(member)
            need(0 < info.file_size < 2_000_000, "Selected original exceeds small-file bound")
            payload = package.read(member)
            total += len(payload)
            need(total < 8_000_000, "Selected originals exceed output bound")
            blob = hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()
            need(blob == blobs[name], "Selected original differs from pinned Git blob")
            target = OUT / "original" / Path(name).name
            if target.exists():
                need(target.read_bytes() == payload, "Preserved original changed; refusing overwrite")
            elif write_originals:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(payload)
            else:
                raise FileNotFoundError("Missing preserved original: " + str(target))
            media = parents[image]
            parent = parents.get(media)
            records.append({"key": Path(name).stem.removeprefix(STEM),
                "original_src": image.get("src"), "original_path": target.relative_to(BASE).as_posix(),
                "original_sha256": digest(payload), "original_bytes": len(payload),
                "source_git_blob_sha1": blob, "source_zip_member": member, "source_zip_crc32": f"{info.CRC:08x}",
                "media_id": media.get("id"),
                "figure_id": parent.get("id") if parent is not None and parent.tag == CN+"figure" else None,
                "localized_path": f"assets/B006/{Path(name).stem}.te.svg"})
    return records, total


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--originals-only", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    need(sum((args.originals_only,args.verify,args.self_test)) <= 1,"Choose at most one operation")
    if args.self_test:
        self_test()
    else:
        build(args.verify,args.originals_only)
