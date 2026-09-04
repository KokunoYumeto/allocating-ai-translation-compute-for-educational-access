"""Gujarati redraws for the 36 inspected media in A00 m81275.

Thirteen language-bearing originals have responsive native redraws. The exact
twenty-three verified mathematical-only originals return None. Rendering is
pure: the caller supplies the reviewed alt and unique media identifier.
"""
from html import escape
from pathlib import PurePath

from localized_place_value import FONT, INK, TEAL, RED, PALE, _uid, _outer


PREFIX = "CNX_BMath_Figure_03_01_"
SELF_CHECK = "CNX_BMath_Figure_AppB_013.jpg"

VERIFIED_MATH_ONLY = frozenset((
    PREFIX + "205_img.jpg",
    PREFIX + "002.jpg",
    PREFIX + "005.jpg",
    PREFIX + "007.jpg",
    PREFIX + "008.jpg",
    PREFIX + "009.jpg",
    PREFIX + "010_img.jpg",
    PREFIX + "011_img.jpg",
    PREFIX + "013.jpg",
    PREFIX + "014a_img.jpg",
    PREFIX + "014b_img.jpg",
    PREFIX + "014c_img.jpg",
    PREFIX + "015.jpg",
    PREFIX + "017.jpg",
    PREFIX + "018.jpg",
    PREFIX + "020_img-02.png",
    PREFIX + "021_img-02.png",
    PREFIX + "022_img-02.png",
    PREFIX + "023_img-02.png",
    PREFIX + "024_img-02.png",
    PREFIX + "025_img-02.png",
    PREFIX + "201_img.jpg",
    PREFIX + "203_img.jpg",
))

CONCEPTUAL = frozenset((
    PREFIX + "003.jpg",
    PREFIX + "004.jpg",
    PREFIX + "006.jpg",
    PREFIX + "012.jpg",
    PREFIX + "016.jpg",
    PREFIX + "019.jpg",
))

SUBSTITUTIONS = {
    PREFIX + "020_img-01.png": ("x", 8, "−(8)", -8),
    PREFIX + "021_img-01.png": ("x", -8, "−(−8)", 8),
    PREFIX + "022_img-01.png": ("x", -35, "|−35|", 35),
    PREFIX + "023_img-01.png": ("y", -20, "|−(−20)|", 20),
    PREFIX + "024_img-01.png": ("u", 12, "−|12|", -12),
    PREFIX + "025_img-01.png": ("p", -14, "−|−14|", -14),
}

SELF_SKILLS = (
    "સંખ્યારેખા પર ધન અને ઋણ સંખ્યાઓનાં સ્થાન દર્શાવવાં.",
    "ધન અને ઋણ સંખ્યાઓનો ક્રમ નક્કી કરવો.",
    "વિરોધી સંખ્યાઓ શોધવી.",
    "નિરપેક્ષ મૂલ્ય ધરાવતી પદાવલીઓ સરળ કરવી.",
    "શબ્દસમૂહોને પૂર્ણાંક ધરાવતી પદાવલીઓમાં ફેરવવા.",
)


def _basename(filename):
    return PurePath(str(filename).replace("\\", "/")).name


def _math(content, color=INK, size=22):
    return (
        '<math xmlns="http://www.w3.org/1998/Math/MathML" '
        f'style="font-size:{size}px;color:{color};vertical-align:middle">{content}</math>'
    )


def _number(value, color=INK):
    sign = "<mo>−</mo>" if value < 0 else ""
    return _math(sign + f"<mn>{abs(value)}</mn>", color)


def _svg_start(width, height, data=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'aria-hidden="true" {data} style="display:block;width:100%;max-width:{width}px;'
        f'height:auto;margin:auto;font-family:{FONT};fill:{INK}">'
    )


def _defs(uid, water=False):
    body = "<defs>"
    for key, color in (("ink", INK), ("teal", "#55d9c7"), ("red", "#e32322")):
        body += (
            f'<marker id="{uid}-{key}" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0 0 L10 5 L0 10 Z" fill="{color}"/></marker>'
        )
    if water:
        body += (
            f'<linearGradient id="{uid}-water" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#d9f4f8"/><stop offset="1" stop-color="#3996c0"/>'
            "</linearGradient>"
        )
    return body + "</defs>"


def _line_arrow(x1, y1, x2, y2, uid, key="ink", both=False):
    start = f' marker-start="url(#{uid}-{key})"' if both else ""
    color = {"ink": INK, "teal": "#55d9c7", "red": "#e32322"}[key]
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
        f'stroke-width="2"{start} marker-end="url(#{uid}-{key})"/>'
    )


def _text(x, y, value, size=22, anchor="middle", color=INK, weight=400):
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
        f'font-weight="{weight}" fill="{color}">{escape(str(value))}</text>'
    )


def _brace(x1, x2, y, upward=True):
    notch = -7 if upward else 7
    edge = 7 if upward else -7
    mid = (x1 + x2) / 2
    return (
        f'<path d="M{x1} {y+edge} Q{x1} {y} {x1+7} {y} '
        f'L{mid-8} {y} Q{mid} {y} {mid} {y+notch} '
        f'Q{mid} {y} {mid+8} {y} L{x2-7} {y} Q{x2} {y} {x2} {y+edge}" '
        'fill="none" stroke="#55d9c7" stroke-width="1.8"/>'
    )


def _axis(uid, y, minimum=-4, maximum=4, point_values=(), label_values=None):
    body = _line_arrow(12, y, 548, y, uid, both=True)
    label_values = range(minimum, maximum + 1) if label_values is None else label_values
    positions = {}
    for value in range(minimum, maximum + 1):
        x = 40 + (value - minimum) * 480 / (maximum - minimum)
        positions[value] = x
        body += f'<line x1="{x}" y1="{y-9}" x2="{x}" y2="{y+9}" stroke="{INK}"/>'
        if value in label_values:
            body += _text(x, y + 34, str(value).replace("-", "−"), 22)
    for value in point_values:
        body += f'<circle cx="{positions[value]}" cy="{y}" r="6" fill="#319aa5"/>'
    return body, positions


def _coast(alt, uid):
    labels = (
        "ભૂમધ્ય સમુદ્ર (0 ફૂટ)",
        "ઇઝરાયલ",
        "મૃત સમુદ્ર (−1302 ફૂટ)",
        "જોર્ડન",
    )
    body = (
        '<div style="display:grid;grid-template-columns:1.35fr .7fr 1.25fr .7fr;'
        'gap:4px;text-align:center;align-items:end;font-size:15px;line-height:1.35">'
        + "".join(f'<span style="overflow-wrap:anywhere">{escape(label)}</span>' for label in labels)
        + "</div>"
    )
    body += _svg_start(720, 155, 'data-elevations="0,-1302"')
    body += (
        '<rect x="0" y="0" width="720" height="155" fill="#d9fbf5"/>'
        '<path d="M0 90 Q35 98 65 90 Q95 98 125 90 L235 90 L188 155 H0 Z" fill="#187ca8"/>'
        '<path d="M188 155 L235 90 Q330 92 395 58 Q450 35 510 72 Q545 95 575 130 '
        'Q615 145 647 68 Q681 0 720 14 L720 155 Z" fill="#e596aa" stroke="#b84254"/>'
        '<path d="M0 90 Q35 98 65 90 Q95 98 125 90 Q160 98 195 90" '
        'fill="none" stroke="#126eaa" stroke-width="2"/>'
        '<g stroke="#5f777c" stroke-width="1.5">'
        '<line x1="115" y1="0" x2="115" y2="88"/><line x1="330" y1="0" x2="330" y2="65"/>'
        '<line x1="560" y1="0" x2="560" y2="123"/><line x1="665" y1="0" x2="665" y2="45"/>'
        "</g></svg>"
    )
    return _outer(body, alt, uid, "a00-integers-coast-elevation")


def _submarine(alt, uid):
    body = _svg_start(560, 310, 'data-depths="0,-500"')
    body += _defs(uid, water=True)
    body += (
        f'<rect x="0" y="20" width="560" height="280" fill="url(#{uid}-water)"/>'
        '<path d="M0 24 Q20 10 40 24 T80 24 T120 24 T160 24 T200 24 T240 24 '
        'T280 24 T320 24 T360 24 T400 24 T440 24 T480 24 T520 24 T560 24" '
        'fill="none" stroke="#126ec4" stroke-width="3"/>'
        f'<line x1="250" y1="20" x2="250" y2="270" stroke="{INK}" stroke-width="2"/>'
    )
    for index in range(6):
        y = 20 + index * 50
        body += f'<line x1="239" y1="{y}" x2="261" y2="{y}" stroke="{INK}"/>'
    body += _text(238, 15, "0 ફૂટ", 20, "end")
    body += _text(238, 278, "−500 ફૂટ", 20, "end")
    body += (
        '<g transform="translate(302 240)">'
        '<ellipse cx="0" cy="0" rx="47" ry="21" fill="#598bdc" stroke="#295cbb" stroke-width="2"/>'
        '<path d="M-6 -20 V-36 H12 V-20" fill="#598bdc" stroke="#295cbb" stroke-width="2"/>'
        '<path d="M47 0 L69 -13 V13 Z" fill="#598bdc" stroke="#295cbb" stroke-width="2"/>'
        '<circle cx="−20" cy="0" r="5" fill="#b7daf7"/><circle cx="0" cy="0" r="5" fill="#b7daf7"/>'
        '<circle cx="20" cy="0" r="5" fill="#b7daf7"/></g></svg>'
    )
    return _outer(body, alt, uid, "a00-integers-submarine-depth")


def _signed_line(alt, uid):
    body = _svg_start(560, 190, 'data-range="-4,4"')
    body += _defs(uid)
    axis, positions = _axis(uid, 32)
    body += axis
    body += _brace(positions[-4], positions[0] - 8, 100, upward=False)
    body += _brace(positions[0] + 8, positions[4], 100, upward=False)
    body += _text(151, 142, "ઋણ સંખ્યાઓ", 23)
    body += _text(409, 142, "ધન સંખ્યાઓ", 23)
    body += _line_arrow(positions[0], 154, positions[0], 80, uid)
    body += _text(positions[0], 184, "શૂન્ય", 22)
    return _outer(body + "</svg>", alt, uid, "a00-integers-sign-categories")


def _ordering_line(alt, uid):
    body = _svg_start(560, 180, 'data-range="-4,4" data-increasing="right" data-decreasing="left"')
    body += _defs(uid)
    axis, _ = _axis(uid, 85)
    body += axis
    body += _line_arrow(280, 38, 476, 38, uid, "teal")
    body += _text(378, 27, "વધતું", 23)
    body += _line_arrow(280, 138, 90, 138, uid, "red")
    body += _text(185, 174, "ઘટતું", 23)
    return _outer(body + "</svg>", alt, uid, "a00-integers-order-directions")


def _opposite_panel(distance, letter, uid):
    point_values = (-distance, distance)
    body = _svg_start(560, 116, f'data-opposites="{-distance},{distance}"')
    body += _defs(uid)
    axis, positions = _axis(uid, 58, point_values=point_values)
    body += axis
    body += _brace(positions[-distance], positions[0], 22, upward=True)
    body += _brace(positions[0], positions[distance], 22, upward=True)
    body += _text((positions[-distance] + positions[0]) / 2, 14, distance, 21)
    body += _text((positions[0] + positions[distance]) / 2, 14, distance, 21)
    body += "</svg>"
    sentence = f"સંખ્યાઓ −{distance} અને {distance} એકબીજાની વિરોધી સંખ્યાઓ છે."
    body += f'<p style="margin:0;text-align:center;font-size:18px">{sentence}</p>'
    body += f'<p style="margin:2px 0 10px;text-align:center">({letter})</p>'
    return body


def _opposites(alt, uid):
    body = _opposite_panel(2, "a", uid + "-a")
    body += _opposite_panel(3, "b", uid + "-b")
    return _outer(body, alt, uid, "a00-integers-opposite-pairs")


def _absolute_distance(alt, uid):
    left_eq = _math("<mo>|</mo><mo>−</mo><mn>5</mn><mo>|</mo><mo>=</mo><mn>5</mn>")
    right_eq = _math("<mo>|</mo><mn>5</mn><mo>|</mo><mo>=</mo><mn>5</mn>")
    body = (
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));'
        'gap:10px;text-align:center;align-items:start">'
        f'<p style="margin:0">−5 શૂન્યથી 5 એકમ દૂર છે,<br>તેથી {left_eq}.</p>'
        f'<p style="margin:0">5 શૂન્યથી 5 એકમ દૂર છે,<br>તેથી {right_eq}.</p>'
        "</div>"
    )
    body += _svg_start(560, 180, 'data-points="-5,0,5" data-distances="5,5"')
    body += _defs(uid)
    body += _line_arrow(95, 10, 157, 55, uid, "teal")
    body += _line_arrow(465, 10, 403, 55, uid, "teal")
    body += _text(157, 75, "5 એકમ", 22)
    body += _text(403, 75, "5 એકમ", 22)
    body += _brace(40, 280, 93, upward=True) + _brace(280, 520, 93, upward=True)
    body += _line_arrow(12, 126, 548, 126, uid, both=True)
    for x, value in ((40, "−5"), (280, "0"), (520, "5")):
        body += f'<line x1="{x}" y1="116" x2="{x}" y2="136" stroke="{INK}"/>'
        body += _text(x, 168, value, 23)
    return _outer(body + "</svg>", alt, uid, "a00-integers-absolute-distance")


def _substitution(spec, alt, uid):
    variable, value, following, result = spec
    variable_math = _math(f"<mi>{escape(variable)}</mi>")
    value_math = _number(value, RED)
    body = (
        f'<p data-variable="{escape(variable)}" data-value="{value}" '
        f'data-following="{escape(following)}" data-result="{result}" '
        f'style="font-size:20px;margin:2px 0;color:{TEAL}">'
        f'{variable_math}ની જગ્યાએ {value_math} મૂકો.</p>'
    )
    return _outer(body, alt, uid, "a00-integers-substitution")


def _cell_style(header=False):
    background = "#a9ccce" if header else PALE
    return (
        f"border:1px solid {TEAL};padding:7px;text-align:center;vertical-align:middle;"
        f"background:{background};overflow-wrap:anywhere"
    )


def _selfcheck(alt, uid):
    choices = ("આત્મવિશ્વાસથી", "થોડી મદદથી", "ના—મને સમજાતું નથી!")
    body = '<p style="margin:0 0 8px;font-weight:700">હું કરી શકું છું…</p>'
    for skill in SELF_SKILLS:
        body += (
            '<table style="width:100%;border-collapse:collapse;table-layout:fixed;'
            'font-size:14px;margin:0 0 12px">'
            f'<caption style="text-align:left;font-size:17px;padding:6px 0">{escape(skill)}</caption>'
            "<thead><tr>"
        )
        body += "".join(
            f'<th scope="col" style="{_cell_style(True)}">{choice}</th>' for choice in choices
        )
        body += "</tr></thead><tbody><tr>"
        body += "".join(
            f'<td aria-label="ખાલી" style="{_cell_style()}height:35px">&#160;</td>'
            for _ in choices
        )
        body += "</tr></tbody></table>"
    return _outer(body, alt, uid, "a00-integers-selfcheck")


def render_figure(filename, alt, unique_id):
    """Return localized markup, or None for verified math-only/unknown files."""
    name = _basename(filename)
    if name in VERIFIED_MATH_ONLY:
        return None
    uid = _uid(unique_id)
    if name == PREFIX + "003.jpg":
        return _coast(alt, uid)
    if name == PREFIX + "004.jpg":
        return _submarine(alt, uid)
    if name == PREFIX + "006.jpg":
        return _signed_line(alt, uid)
    if name == PREFIX + "012.jpg":
        return _ordering_line(alt, uid)
    if name == PREFIX + "016.jpg":
        return _opposites(alt, uid)
    if name == PREFIX + "019.jpg":
        return _absolute_distance(alt, uid)
    if name in SUBSTITUTIONS:
        return _substitution(SUBSTITUTIONS[name], alt, uid)
    if name == SELF_CHECK:
        return _selfcheck(alt, uid)
    return None
