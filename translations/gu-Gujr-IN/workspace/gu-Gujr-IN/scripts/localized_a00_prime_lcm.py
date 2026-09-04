"""Gujarati redraws for the 26 inspected figures in A00 m81273.

The three LCM diagrams and the self-check are localized. The exact 22
enumerated mathematical-only originals return None. No source mutation occurs.
"""
from html import escape

from localized_place_value import FONT, INK, TEAL, PALE, _uid, _outer


PREFIX = "CNX_BMath_Figure_02_05_"
SELF_CHECK = "CNX_BMath_Figure_AppB_012.jpg"
VERIFIED_MATH_ONLY = frozenset((
    PREFIX + "018_img.jpg",
    PREFIX + "019_img.jpg",
    PREFIX + "009_img.jpg",
    PREFIX + "022_img-01.png",
    PREFIX + "022_img-02.png",
    PREFIX + "022_img-03.png",
    PREFIX + "023_img-01.png",
    PREFIX + "023_img-02.png",
    PREFIX + "010_img.jpg",
    PREFIX + "011_img.jpg",
    PREFIX + "012_img.jpg",
    PREFIX + "024_img-01.png",
    PREFIX + "024_img-03.png",
    PREFIX + "024_img-02.png",
    PREFIX + "025_img-01.png",
    PREFIX + "025_img-02.png",
    PREFIX + "026_img-01.png",
    PREFIX + "026_img-02.png",
    PREFIX + "027_img-01.png",
    PREFIX + "027_img-02.png",
    PREFIX + "201.jpg",
    PREFIX + "202.jpg",
))


DIAGRAMS = {
    PREFIX + "006_img.jpg": {
        "numbers": (12, 18),
        "top": (2, 2, 3, None),
        "bottom": (2, None, 3, 3),
        "merged": (2, 2, 3, 3),
        "final": 36,
    },
    PREFIX + "026_img-03.png": {
        "numbers": (15, 18),
        "top": (None, 3, None, 5),
        "bottom": (2, 3, 3, None),
        "merged": (2, 3, 3, 5),
        "final": None,
    },
    PREFIX + "027_img-03.png": {
        "numbers": (50, 100),
        "top": (None, 2, 5, 5),
        "bottom": (2, 2, 5, 5),
        "merged": (2, 2, 5, 5),
        "final": None,
    },
}


def _factor_row(number, factors, y):
    xs = (220, 290, 360, 430)
    body = f'<text x="105" y="{y}" text-anchor="end" font-size="24">{number} =</text>'
    for index, (x, factor) in enumerate(zip(xs, factors)):
        if factor is None:
            continue
        body += f'<text x="{x}" y="{y}" text-anchor="middle" font-size="24">{factor}</text>'
        if any(value is not None for value in factors[index + 1:]):
            body += f'<text x="{x + 35}" y="{y}" text-anchor="middle" font-size="24">·</text>'
    return body


def _merged_row(factors, y):
    xs = (220, 290, 360, 430)
    body = f'<text x="145" y="{y}" text-anchor="end" font-size="23">LCM =</text>'
    for index, (x, factor) in enumerate(zip(xs, factors)):
        body += f'<text x="{x}" y="{y}" text-anchor="middle" font-size="24">{factor}</text>'
        if index < len(factors) - 1:
            body += f'<text x="{x + 35}" y="{y}" text-anchor="middle" font-size="24">·</text>'
    return body


def _lcm_diagram(spec, alt, uid):
    arrow = uid + "-column-arrow"
    height = 215 if spec["final"] else 178
    slots = lambda values: ",".join("_" if value is None else str(value) for value in values)
    body = (
        '<p style="margin:0 0 4px;text-align:center;font-weight:700">'
        'લઘુત્તમ સામાન્ય અવયવી (LCM)</p>'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 {height}" '
        f'data-numbers="{slots(spec["numbers"])}" data-top="{slots(spec["top"])}" '
        f'data-bottom="{slots(spec["bottom"])}" data-merged="{slots(spec["merged"])}" '
        f'data-final="{spec["final"] if spec["final"] is not None else ""}" '
        f'aria-hidden="true" style="display:block;width:min(100%,620px);height:auto;margin:auto;'
        f'font-family:{FONT};fill:{INK}">'
        f'<defs><marker id="{arrow}" viewBox="0 0 10 10" refX="8" refY="5" '
        f'markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 Z" '
        f'fill="{TEAL}"/></marker></defs>'
    )
    body += _factor_row(spec["numbers"][0], spec["top"], 36)
    body += _factor_row(spec["numbers"][1], spec["bottom"], 78)
    body += f'<line x1="16" y1="98" x2="486" y2="98" stroke="{INK}" stroke-width="2"/>'
    for x, top, bottom in zip((220, 290, 360, 430), spec["top"], spec["bottom"]):
        start = 43 if top is not None else 82
        body += (
            f'<line x1="{x}" y1="{start}" x2="{x}" y2="126" stroke="{TEAL}" '
            f'stroke-width="2.5" marker-end="url(#{arrow})"/>'
        )
    body += _merged_row(spec["merged"], 151)
    if spec["final"] is not None:
        expression = " · ".join(map(str, spec["merged"]))
        body += (
            f'<text x="260" y="198" text-anchor="middle" font-size="23">'
            f'LCM = {expression} = {spec["final"]}</text>'
        )
    body += "</svg>"
    return _outer(body, alt, uid, "a00-prime-lcm-aligned")


def _cell_style(header=False):
    background = PALE if not header else "#a9ccce"
    return (
        f"border:1px solid {TEAL};padding:7px;text-align:center;vertical-align:middle;"
        f"background:{background};overflow-wrap:anywhere"
    )


def _selfcheck(alt, uid):
    skills = (
        "સંયુક્ત સંખ્યાનું અવિભાજ્ય અવયવીકરણ શોધવું.",
        "બે સંખ્યાઓનો લઘુત્તમ સામાન્ય અવયવી (LCM) શોધવો.",
    )
    choices = ("આત્મવિશ્વાસથી", "થોડી મદદથી", "ના—મને સમજાતું નથી!")
    body = '<p style="margin:0 0 8px;font-weight:700">હું કરી શકું છું…</p>'
    for skill in skills:
        body += (
            '<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:14px;margin:0 0 12px">'
            f'<caption style="text-align:left;font-size:17px;padding:6px 0">{escape(skill)}</caption>'
            '<thead><tr>'
        )
        body += "".join(
            f'<th scope="col" style="{_cell_style(True)}">{choice}</th>' for choice in choices
        )
        body += '</tr></thead><tbody><tr>'
        body += "".join(
            f'<td aria-label="ખાલી" style="{_cell_style()}height:35px">&#160;</td>' for _ in choices
        )
        body += "</tr></tbody></table>"
    return _outer(body, alt, uid, "a00-prime-lcm-selfcheck")


def render_figure(filename, alt, unique_id):
    """Return localized markup, or None for verified math-only/unknown files."""
    name = str(filename).replace("\\", "/").rsplit("/", 1)[-1]
    if name in VERIFIED_MATH_ONLY:
        return None
    uid = _uid(unique_id)
    if name in DIAGRAMS:
        return _lcm_diagram(DIAGRAMS[name], alt, uid)
    if name == SELF_CHECK:
        return _selfcheck(alt, uid)
    return None
