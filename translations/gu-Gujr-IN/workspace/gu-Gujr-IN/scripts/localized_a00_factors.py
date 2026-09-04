"""Gujarati redraws for the nine inspected figures in A00 m81272.

Five language-bearing originals are replaced with native markup. The four
enumerated number grids contain only mathematical numerals/highlights and
return None. This module performs no file or source mutation.
"""
from html import escape

from localized_place_value import FONT, INK, TEAL, PALE, _uid, _outer


PREFIX = "CNX_BMath_Figure_02_04_"
SELF_CHECK = "CNX_BMath_Figure_AppB_011.jpg"
VERIFIED_MATH_ONLY = frozenset(
    PREFIX + f"00{number}.jpg" for number in range(1, 5)
)
PRIMES = frozenset((2, 3, 5, 7, 11, 13, 17, 19))
PRIME_FILL = "#d1e1e1"
HEADER_FILL = "#a9ccce"


def _cell_style(header=False, extra=""):
    background = HEADER_FILL if header else "#fff"
    return (
        f"border:1px solid {TEAL};padding:6px 8px;text-align:center;"
        f"vertical-align:middle;background:{background};{extra}"
    )


def _region(table, label, min_width, sticky_caption=False):
    caption_style = "position:sticky;left:0;text-align:left;" if sticky_caption else ""
    return (
        f'<div role="region" aria-label="{escape(label)}; આડું સરકાવી શકાય છે" '
        'tabindex="0" style="overflow-x:auto;max-width:100%">'
        f'<table style="border-collapse:collapse;min-width:{min_width}px;width:100%;'
        'table-layout:fixed;font-size:15px">'
        f'<caption style="{caption_style}font-weight:700;padding:4px 0 8px">'
        f'{escape(label)}</caption>{table}</table></div>'
    )


def _factor_product(alt, uid):
    body = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 440 120" '
        f'aria-hidden="true" style="display:block;width:min(100%,520px);height:auto;margin:auto;'
        f'font-family:{FONT};color:{INK}">'
        f'<text x="65" y="42" text-anchor="middle" font-size="30" fill="{INK}">8 · 9</text>'
        f'<text x="185" y="42" text-anchor="middle" font-size="30" fill="{INK}">=</text>'
        f'<text x="315" y="42" text-anchor="middle" font-size="30" fill="{INK}">72</text>'
        f'<path d="M20 60 V68 Q20 77 31 77 H99 Q110 77 110 88 Q110 77 121 77 H189 '
        f'Q200 77 200 68 V60" fill="none" stroke="{TEAL}" stroke-width="3"/>'
        f'<path d="M275 60 V68 Q275 77 286 77 H304 Q315 77 315 88 Q315 77 326 77 H344 '
        f'Q355 77 355 68 V60" fill="none" stroke="{TEAL}" stroke-width="3"/>'
        f'<text x="110" y="112" text-anchor="middle" font-size="22" fill="{TEAL}">અવયવ</text>'
        f'<text x="315" y="112" text-anchor="middle" font-size="22" fill="{TEAL}">ગુણનફળ</text>'
        '</svg>'
    )
    return _outer(body, alt, uid, "a00-factors-product")


def _factor_72(alt, uid):
    headers = ("ભાજ્ય", "ભાજક", "ભાગફળ", "અવયવ")
    rows = (
        (72, 1, 72, "1, 72"),
        (72, 2, 36, "2, 36"),
        (72, 3, 24, "3, 24"),
        (72, 4, 18, "4, 18"),
        (72, 5, "14.4", "–"),
        (72, 6, 12, "6, 12"),
        (72, 7, "~10.29", "–"),
        (72, 8, 9, "8, 9"),
    )
    table = "<thead><tr>" + "".join(
        f'<th scope="col" style="{_cell_style(True)}">{header}</th>' for header in headers
    ) + "</tr></thead><tbody>"
    for row in rows:
        table += "<tr>" + "".join(
            f'<td style="{_cell_style()}">{escape(str(value))}</td>' for value in row
        ) + "</tr>"
    table += "</tbody>"
    body = _region(table, "72ના અવયવો શોધવાનું કોષ્ટક", 560, True)
    return _outer(body, alt, uid, "a00-factors-72-table")


def _prime_composite(alt, uid):
    headers = ("સંખ્યા", "અવયવ", "અવિભાજ્ય કે સંયુક્ત?")
    left = (
        (2, "1, 2", "અવિભાજ્ય"), (3, "1, 3", "અવિભાજ્ય"),
        (4, "1, 2, 4", "સંયુક્ત"), (5, "1, 5", "અવિભાજ્ય"),
        (6, "1, 2, 3, 6", "સંયુક્ત"), (7, "1, 7", "અવિભાજ્ય"),
        (8, "1, 2, 4, 8", "સંયુક્ત"), (9, "1, 3, 9", "સંયુક્ત"),
        (10, "1, 2, 5, 10", "સંયુક્ત"), (11, "1, 11", "અવિભાજ્ય"),
    )
    right = (
        (12, "1, 2, 3, 4, 6, 12", "સંયુક્ત"), (13, "1, 13", "અવિભાજ્ય"),
        (14, "1, 2, 7, 14", "સંયુક્ત"), (15, "1, 3, 5, 15", "સંયુક્ત"),
        (16, "1, 2, 4, 8, 16", "સંયુક્ત"), (17, "1, 17", "અવિભાજ્ય"),
        (18, "1, 2, 3, 6, 9, 18", "સંયુક્ત"), (19, "1, 19", "અવિભાજ્ય"),
        (20, "1, 2, 4, 5, 10, 20", "સંયુક્ત"), ("", "", ""),
    )
    table = "<colgroup><col style=\"width:11%\"><col style=\"width:21%\"><col style=\"width:18%\">"
    table += '<col style="width:3%"><col style="width:11%"><col style="width:21%"><col style="width:18%"></colgroup>'
    table += "<thead><tr>" + "".join(
        f'<th scope="col" style="{_cell_style(True)}">{header}</th>' for header in headers
    )
    table += f'<th scope="col" aria-hidden="true" style="border:0;background:#fff"></th>'
    table += "".join(
        f'<th scope="col" style="{_cell_style(True)}">{header}</th>' for header in headers
    ) + "</tr></thead><tbody>"
    for lrow, rrow in zip(left, right):
        table += "<tr>"
        for index, value in enumerate(lrow):
            extra = f"background:{PRIME_FILL};" if index == 0 and value in PRIMES else ""
            table += f'<td style="{_cell_style(False, extra)}">{escape(str(value))}</td>'
        table += '<td aria-hidden="true" style="border:0;background:#fff"></td>'
        for index, value in enumerate(rrow):
            extra = f"background:{PRIME_FILL};" if index == 0 and value in PRIMES else ""
            blank = ' aria-label="ખાલી"' if value == "" else ""
            table += f'<td{blank} style="{_cell_style(False, extra)}">{escape(str(value)) or "&#160;"}</td>'
        table += "</tr>"
    table += "</tbody>"
    body = _region(table, "2થી 20 સુધી અવિભાજ્ય અને સંયુક્ત સંખ્યાઓ", 940, True)
    return _outer(body, alt, uid, "a00-factors-prime-composite")


def _frank(alt, uid):
    headers = (
        "ભણતર પૂરું થયા પછીનાં અઠવાડિયાં",
        "ફ્રૅન્કે ખાતામાં મૂકેલા કુલ ડૉલર",
        "સરળ કરેલો સરવાળો",
    )
    rows = (
        ("0", "100", "100"), ("1", "100 + 15", "115"),
        ("2", "100 + 15 · 2", "130"), ("3", "100 + 15 · 3", "145"),
        ("4", "100 + 15 · 4", "160"), ("5", "100 + 15 · 5", "175"),
        ("6", "100 + 15 · 6", "190"), ("20", "100 + 15 · 20", "400"),
        ("x", "100 + 15 · x", "100 + 15x"),
    )
    table = "<thead><tr>" + "".join(
        f'<th scope="col" style="{_cell_style(True)}overflow-wrap:anywhere">{header}</th>'
        for header in headers
    ) + "</tr></thead><tbody>"
    for row in rows:
        table += "<tr>" + "".join(
            f'<td style="{_cell_style()}">{escape(value)}</td>' for value in row
        ) + "</tr>"
    table += "</tbody>"
    body = _region(table, "ફ્રૅન્કના બેંક ખાતાનો પૂર્ણ ઉકેલ", 650, True)
    return _outer(body, alt, uid, "a00-factors-frank-table")


def _selfcheck(alt, uid):
    skills = (
        "સંખ્યાઓના અવયવી ઓળખવા.",
        "વિભાજ્યતાની સામાન્ય ચાવીઓ વાપરવી.",
        "સંખ્યાના બધા અવયવ શોધવા.",
        "અવિભાજ્ય અને સંયુક્ત સંખ્યાઓ ઓળખવી.",
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
            f'<th scope="col" style="{_cell_style(True)}overflow-wrap:anywhere">{choice}</th>'
            for choice in choices
        )
        body += '</tr></thead><tbody><tr>'
        body += "".join(
            f'<td aria-label="ખાલી" style="{_cell_style()}height:35px">&#160;</td>' for _ in choices
        )
        body += "</tr></tbody></table>"
    return _outer(body, alt, uid, "a00-factors-selfcheck")


def render_figure(filename, alt, unique_id):
    """Return localized figure markup, or None for verified math-only/unknown files."""
    name = str(filename).replace("\\", "/").rsplit("/", 1)[-1]
    if name in VERIFIED_MATH_ONLY:
        return None
    uid = _uid(unique_id)
    if name == PREFIX + "008_img.jpg":
        return _factor_product(alt, uid)
    if name == PREFIX + "009.jpg":
        return _factor_72(alt, uid)
    if name == PREFIX + "014_Errata.jpg":
        return _prime_composite(alt, uid)
    if name == "CNX_BMath_Figure_02_05_203_img.jpg":
        return _frank(alt, uid)
    if name == SELF_CHECK:
        return _selfcheck(alt, uid)
    return None
