"""Gujarati redraws for the 72 inspected media occurrences in A00 m81276.

Twelve unique language-bearing originals have semantic Gujarati redraws. The
exact fifty-nine verified mathematical-only unique originals return ``None``.
The caller supplies the reviewed alternative and stable unique media ID.
"""
from html import escape
from pathlib import PurePath

from localized_place_value import FONT, INK, TEAL, RED, PALE, _uid, _outer


PREFIX = "CNX_BMath_Figure_03_02_"
SELF_CHECK = "CNX_BMath_Figure_AppB_014.jpg"

VERIFIED_MATH_ONLY = frozenset((
    PREFIX + "001.jpg",
    PREFIX + "025_img-01.png", PREFIX + "025_img-02.png",
    PREFIX + "005_img.jpg", PREFIX + "006_img.jpg",
    PREFIX + "026_img-01.png", PREFIX + "026_img-02.png",
    PREFIX + "010_img.jpg", PREFIX + "011_img.jpg",
    PREFIX + "027_img-01.png", PREFIX + "027_img-02.png", PREFIX + "027_img-03.png",
    PREFIX + "016_img.jpg", PREFIX + "023_img.jpg",
    PREFIX + "028_img-01.png", PREFIX + "028_img-02.png", PREFIX + "028_img-03.png",
    PREFIX + "022_img.jpg", PREFIX + "017_img.jpg",
    PREFIX + "035_img-01.png", PREFIX + "035_img-02.png",
    PREFIX + "036_img-01.png", PREFIX + "036_img-02.png", PREFIX + "036_img-03.png", PREFIX + "036_img-04.png",
    PREFIX + "037_img-01.png", PREFIX + "037_img-02.png", PREFIX + "037_img-03.png", PREFIX + "037_img-04.png",
    PREFIX + "038_img-01.png", PREFIX + "038_img-02.png",
    PREFIX + "039_img.jpg", PREFIX + "040_img.jpg", PREFIX + "041_img.jpg", PREFIX + "042_img.jpg",
    PREFIX + "043_img.jpg", PREFIX + "044_img.jpg", PREFIX + "045_img.jpg", PREFIX + "046_img.jpg",
    PREFIX + "029_img-03.png", PREFIX + "029_img-04.png",
    PREFIX + "030_img-02.png", PREFIX + "030_img-03.png", PREFIX + "030_img-04.png",
    PREFIX + "031_img-02.png", PREFIX + "031_img-03.png", PREFIX + "031_img-04.png",
    PREFIX + "032_img-02.png", PREFIX + "032_img-03.png", PREFIX + "032_img-04.png", PREFIX + "032_img-05.png",
    PREFIX + "033_img-02.png", PREFIX + "033_img-03.png", PREFIX + "033_img-04.png", PREFIX + "033_img-05.png",
    PREFIX + "201_img.jpg", PREFIX + "203_img.jpg", PREFIX + "205_img.jpg", PREFIX + "207_img.jpg",
))

COUNTERS = {
    PREFIX + "025_img-03.png": (8, "positive", "8 ધન", (5, 3)),
    PREFIX + "026_img-03.png": (8, "negative", "8 ઋણ", (5, 3)),
    PREFIX + "027_img-04.png": (2, "negative", "2 ઋણ", (2,)),
    PREFIX + "028_img-04.png": (2, "positive", "2 ધન", (2,)),
}

SUBSTITUTIONS = {
    PREFIX + "029_img-01.png": (("x",), ((-2, "red"),), "xની જગ્યાએ {0} મૂકો.", "−2+7=5"),
    PREFIX + "030_img-01.png": (("x",), ((-11, "red"),), "xની જગ્યાએ {0} મૂકો.", "−11+7=−4"),
    PREFIX + "031_img-01.png": (("n",), ((-5, "red"),), "nની જગ્યાએ {0} મૂકો.", "−5+1=−4"),
    PREFIX + "032_img-01.png": (("n",), ((-5, "red"),), "nની જગ્યાએ {0} મૂકો.", "−(−5)+1=6"),
    PREFIX + "033_img-01.png": (("a", "b"), ((12, "red"), (-30, "cyan")), "aની જગ્યાએ {0} અને bની જગ્યાએ {1} મૂકો.", "3(12)+(−30)=6"),
    PREFIX + "034_img-01.png": (("x", "y"), ((-18, "red"), (24, "cyan")), "xની જગ્યાએ {0} અને yની જગ્યાએ {1} મૂકો.", "(−18+24)^2=36"),
}

SELF_SKILLS = (
    "પૂર્ણાંકોના સરવાળાને નમૂના દ્વારા દર્શાવી શકું.",
    "પૂર્ણાંકો ધરાવતી પદાવલીઓ સરળ કરી શકું.",
    "પૂર્ણાંકો ધરાવતી ચલ પદાવલીઓની કિંમત શોધી શકું.",
    "શબ્દસમૂહોને બીજગણિતીય પદાવલીઓમાં ફેરવી શકું.",
    "વ્યવહારુ પ્રશ્નોમાં પૂર્ણાંકોનો સરવાળો કરી શકું.",
)

SELF_CHOICES = (
    "આત્મવિશ્વાસ સાથે",
    "થોડી મદદથી",
    "નહીં—મને સમજાયું નથી!",
)


def _basename(filename):
    return PurePath(str(filename).replace("\\", "/")).name


def _svg_start(width, height, data=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'aria-hidden="true" {data} style="display:block;width:100%;max-width:{width}px;'
        f'height:auto;margin:auto;font-family:{FONT};fill:{INK}">'
    )


def _counter(cx, cy, kind, radius=25):
    fill, stroke = (("#cbeff2", "#258aa1") if kind == "positive" else ("#f3a89d", "#bc3030"))
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="2"/>'
    )


def _legend(alt, uid):
    body = _svg_start(420, 165, 'data-positive-count="1" data-negative-count="1"')
    body += _counter(105, 65, "positive", 35)
    body += _counter(315, 65, "negative", 35)
    body += '<text x="105" y="140" text-anchor="middle" font-size="24">ધન</text>'
    body += '<text x="315" y="140" text-anchor="middle" font-size="24">ઋણ</text></svg>'
    return _outer(body, alt, uid, "a00-integer-addition-counter-key")


def _counter_label(spec, alt, uid):
    count, kind, label, groups = spec
    width = 500
    positions = []
    x = 42
    for group_index, group_size in enumerate(groups):
        for _ in range(group_size):
            positions.append(x)
            x += 52
        if group_index < len(groups) - 1:
            x += 34
    used = positions[-1] - positions[0]
    offset = (width - used) / 2 - positions[0]
    positions = [position + offset for position in positions]
    group_data = ",".join(str(group) for group in groups)
    data = (f'data-counter-count="{count}" data-counter-kind="{kind}" '
            f'data-counter-groups="{group_data}"')
    body = _svg_start(width, 145, data)
    for position in positions:
        body += _counter(position, 48, kind, 21)
    body += f'<text x="250" y="125" text-anchor="middle" font-size="25">{escape(label)}</text></svg>'
    return _outer(body, alt, uid, "a00-integer-addition-counter-label")


def _signed_math(value, color):
    ink = RED if color == "red" else "#2aa6bd"
    sign = "<mo>−</mo>" if value < 0 else ""
    return (
        '<math xmlns="http://www.w3.org/1998/Math/MathML" '
        f'style="font-size:23px;color:{ink};vertical-align:middle" data-signed-value="{value}" '
        f'data-highlight="{color}">{sign}<mn>{abs(value)}</mn></math>'
    )


def _substitution(spec, alt, uid):
    variables, values, template, paired = spec
    rendered_values = tuple(_signed_math(value, color) for value, color in values)
    sentence = template.format(*rendered_values)
    variable_data = ",".join(variables)
    value_data = ",".join(str(value) for value, _ in values)
    color_data = ",".join(color for _, color in values)
    body = (
        f'<p data-variables="{escape(variable_data)}" data-values="{escape(value_data)}" '
        f'data-colors="{escape(color_data)}" data-paired-expression="{escape(paired)}" '
        f'style="margin:2px 0;font-size:21px;line-height:1.7;color:{TEAL};overflow-wrap:anywhere">'
        f'{sentence}</p>'
    )
    return _outer(body, alt, uid, "a00-integer-addition-substitution")


def _cell_style(header=False):
    background = "#a9ccce" if header else PALE
    return (
        f"border:1px solid {TEAL};padding:7px;text-align:center;vertical-align:middle;"
        f"background:{background};overflow-wrap:anywhere"
    )


def _selfcheck(alt, uid):
    body = '<p style="margin:0 0 8px;font-weight:700">હું આ કરી શકું છું...</p>'
    for skill in SELF_SKILLS:
        body += (
            '<table style="width:100%;border-collapse:collapse;table-layout:fixed;'
            'font-size:14px;margin:0 0 12px">'
            f'<caption style="text-align:left;font-size:17px;padding:6px 0">{escape(skill)}</caption>'
            '<thead><tr>'
        )
        body += "".join(
            f'<th scope="col" style="{_cell_style(True)}">{escape(choice)}</th>'
            for choice in SELF_CHOICES
        )
        body += '</tr></thead><tbody><tr>'
        body += "".join(
            f'<td aria-label="ખાલી" style="{_cell_style()}height:35px">&#160;</td>'
            for _ in SELF_CHOICES
        )
        body += '</tr></tbody></table>'
    return _outer(body, alt, uid, "a00-integer-addition-selfcheck")


def render_figure(filename, alt, unique_id):
    """Return localized markup, or ``None`` for verified math-only/unknown files."""
    name = _basename(filename)
    if name in VERIFIED_MATH_ONLY:
        return None
    uid = _uid(unique_id)
    if name == PREFIX + "024_img.jpg":
        return _legend(alt, uid)
    if name in COUNTERS:
        return _counter_label(COUNTERS[name], alt, uid)
    if name in SUBSTITUTIONS:
        return _substitution(SUBSTITUTIONS[name], alt, uid)
    if name == SELF_CHECK:
        return _selfcheck(alt, uid)
    return None
