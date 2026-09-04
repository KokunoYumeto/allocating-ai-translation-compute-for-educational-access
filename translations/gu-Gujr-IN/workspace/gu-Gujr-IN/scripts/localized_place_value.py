"""Gujarati redraws for all 32 media occurrences in A00 m81243 part03.

Pure rendering: no file reads, downloads, script execution, or source mutation.
Source IDs and mathematical strings remain the integrating caller's authority.
Every recognized image is redrawn; unknown filenames return None.
"""
from html import escape
import hashlib
import re

FONT = "Gujarati,'Nirmala UI',sans-serif"
INK = '#182c35'
TEAL = '#08656b'
RED = '#a52d18'
PALE = '#edf6f4'
PREFIX = 'CNX_BMath_Figure_'


def _e(value):
    return escape(str(value), quote=True)


def _uid(value):
    clean = re.sub(r'[^A-Za-z0-9_-]', '-', str(value)) or 'figure'
    digest = hashlib.sha256(str(value).encode('utf-8')).hexdigest()[:8]
    return 'gu-pv-' + clean + '-' + digest


def _outer(body, alt, uid, mode):
    return (f'<div id="{uid}" class="gu-place-redraw" data-redraw="{mode}" '
            f'role="group" aria-label="{_e(alt)}" lang="gu-Gujr-IN" '
            f'style="font-family:{FONT};color:{INK};background:white;'
            'border:1px solid #b8cecb;border-radius:6px;padding:12px;'
            'margin:8px 0;max-width:100%;box-sizing:border-box;line-height:1.65">'
            + body + '</div>')


def _place_chart(number, alt, uid, title=True):
    """Retain all 15 places and all five groups; blank is never silently zero."""
    digits = list(number.replace(',', '').rjust(15))
    periods = ['ટ્રિલિયન', 'બિલિયન', 'મિલિયન', 'હજાર', 'એકમ']
    places = [
        ['સો ટ્રિલિયન', 'દસ ટ્રિલિયન', 'ટ્રિલિયન'],
        ['સો બિલિયન', 'દસ બિલિયન', 'બિલિયન'],
        ['સો મિલિયન', 'દસ મિલિયન', 'મિલિયન'],
        ['સો હજાર', 'દસ હજાર', 'હજાર'],
        ['સો', 'દશક', 'એકમ'],
    ]
    body = '<p style="margin:0 0 8px;font-weight:700">સ્થાનકિંમત</p>' if title else ''
    body += '<div style="display:flex;flex-wrap:wrap;gap:8px;align-items:stretch">'
    for group, period in enumerate(periods):
        body += ('<table style="border-collapse:collapse;table-layout:fixed;'
                 'flex:1 1 155px;width:155px;min-width:155px;max-width:100%;margin:0;font-size:16px">'
                 f'<caption style="background:{PALE};border:1px solid {TEAL};'
                 f'padding:5px;font-weight:700">{period}</caption><thead><tr>')
        for place in places[group]:
            body += (f'<th scope="col" style="border:1px solid {TEAL};padding:6px 3px;'
                     f'text-align:center;font-weight:500;vertical-align:bottom;overflow-wrap:anywhere">{place}</th>')
        body += '</tr></thead><tbody><tr>'
        for digit in digits[group * 3: group * 3 + 3]:
            content = _e(digit) if digit != ' ' else '&nbsp;'
            label = ' aria-label="ખાલી"' if digit == ' ' else ''
            body += (f'<td{label} style="border:1px solid {TEAL};padding:6px 3px;'
                     f'text-align:center;font-size:21px;min-height:36px">{content}</td>')
        body += '</tr></tbody></table>'
    return _outer(body + '</div>', alt, uid, 'place-chart')


def _groups(number, groups, alt, uid, direction='to-words', slot_digits=False):
    """One card per original group preserves group order and arrow pairing."""
    body = f'<p style="margin:0 0 8px;font-size:23px;font-weight:700;overflow-wrap:anywhere">{_e(number)}</p>'
    body += '<p style="margin:0 0 6px">સ્થાનસમૂહો</p>'
    body += '<div style="display:flex;flex-wrap:wrap;gap:9px;align-items:stretch">'
    for period, digits, words in groups:
        top, bottom = (digits, words) if direction == 'to-words' else (words, digits)
        body += (f'<div style="flex:1 1 145px;min-width:130px;max-width:100%;'
                 f'border:1px solid #b8cecb;border-radius:4px;padding:8px;text-align:center;box-sizing:border-box">'
                 f'<p style="margin:0 0 8px;color:{TEAL};font-weight:700">{_e(period)}</p>')
        if direction == 'labels-only':
            body += f'<p style="font-size:24px;margin:0">{_e(digits)}</p>'
        else:
            body += f'<p style="margin:0;min-height:30px">{_e(top) if top else "&nbsp;"}</p>'
            body += f'<p aria-hidden="true" style="font-size:25px;line-height:1;margin:7px;color:{TEAL}">↓</p>'
            if slot_digits:
                # Every group is shown in three slots, with genuinely blank leading places.
                bottom = bottom.rjust(3)
                body += '<p style="display:flex;justify-content:center;gap:5px;font-size:24px;margin:0">'
                for digit in bottom:
                    body += '<span style="display:inline-block;width:22px;border-bottom:1px solid #182c35">' + (_e(digit) if digit != ' ' else '&nbsp;') + '</span>'
                body += '</p>'
            else:
                body += f'<p style="margin:0">{_e(bottom)}</p>'
        body += '</div>'
    return _outer(body + '</div>', alt, uid, 'group-words')


def _number_line(mark, alt, uid):
    """HTML tick labels keep their font size when the SVG line becomes narrower."""
    marker = uid + '-arrow'
    body = ('<div style="position:relative;height:69px;width:100%;min-width:220px">'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 40" '
            'width="100%" height="40" preserveAspectRatio="none" aria-hidden="true" '
            'style="display:block;overflow:visible">'
            f'<defs><marker id="{marker}" viewBox="0 0 10 10" refX="5" refY="5" '
            'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            '<path d="M 0 0 L 10 5 L 0 10 Z" fill="#182c35"/></marker></defs>'
            f'<line x1="15" y1="20" x2="1085" y2="20" stroke="{INK}" '
            f'stroke-width="2" vector-effect="non-scaling-stroke" marker-start="url(#{marker})" marker-end="url(#{marker})"/>')
    for i in range(11):
        x = 50 + 100 * i
        body += (f'<line x1="{x}" y1="11" x2="{x}" y2="29" stroke="{INK}" '
                 'stroke-width="1" vector-effect="non-scaling-stroke"/>')
    body += '</svg>'
    percentage = (mark - 70 + .5) / 11 * 100
    body += (f'<span aria-hidden="true" style="position:absolute;left:calc({percentage:.8f}% - 5px);'
             'top:15px;width:10px;height:10px;border-radius:50%;background:#c85f14"></span>')
    body += '<div style="display:grid;grid-template-columns:repeat(11,minmax(0,1fr));font-size:16px;text-align:center;line-height:1.3">'
    for n in range(70, 81):
        color = RED if n in (70, 80) else INK
        body += f'<span style="color:{color};font-weight:{700 if n == mark else 400}">{n}</span>'
    return _outer(body + '</div></div>', alt, uid, 'number-line')


def _digits(number, underline=None, colors=None, cross=None):
    result = '<div style="font-size:32px;line-height:1.6;letter-spacing:2px;white-space:nowrap;text-align:center;max-width:100%">'
    colors = colors or {}
    for i, character in enumerate(number):
        styles = ['display:inline-block', 'min-width:.6em']
        if i == underline:
            styles.append('text-decoration:underline;text-underline-offset:5px;text-decoration-thickness:2px')
        if i == cross:
            styles.append('text-decoration:line-through')
        if i in colors:
            styles.append('color:' + colors[i])
        result += '<span style="' + ';'.join(styles) + '">' + _e(character) + '</span>'
    return result + '</div>'


def _number_only(number, underline, alt, uid):
    return _outer(_digits(number, underline), alt, uid, 'number-underline')


def _label(number, index, label, alt, uid, compare=None):
    colors = {index: TEAL}
    if compare:
        colors[compare[0]] = RED
    body = _digits(number, underline=(compare[0] if compare else None), colors=colors)
    body += '<div style="display:flex;flex-wrap:wrap;gap:10px;justify-content:center;text-align:center">'
    body += (f'<p style="margin:4px 0;color:{TEAL}">{_e(label)} → '
             f'<strong>{_e(number[index])}</strong></p>')
    if compare:
        body += (f'<p style="margin:4px 0;color:{RED}"><strong>{_e(number[compare[0]])}</strong> → '
                 f'{_e(compare[1])}</p>')
    return _outer(body + '</div>', alt, uid, 'place-label')


def _round(number, index, result, alt, uid, add=True, carry=None, cross=False):
    suffix = number[index + 1:].replace(',', '')
    colors = {index: TEAL}
    colors.update({i: RED for i in range(index + 1, len(number)) if number[i].isdigit()})
    body = _digits(number, colors=colors, cross=(index + 1 if cross else None))
    body += '<div style="display:flex;flex-wrap:wrap;gap:12px;justify-content:center;text-align:center">'
    body += (f'<div style="flex:1 1 145px;max-width:100%;padding:7px;border:1px solid #b8cecb;border-radius:4px">'
             f'<p style="margin:0;color:{TEAL}">અંક <strong>{_e(number[index])}</strong> → '
             + ('1 ઉમેરો' if add else '1 ઉમેરશો નહીં') + '</p>')
    for line in carry or []:
        body += f'<p style="margin:3px 0">{_e(line)}</p>'
    body += '</div>'
    body += (f'<div style="flex:1 1 145px;max-width:100%;padding:7px;border:1px solid #b8cecb;border-radius:4px">'
             f'<p style="margin:0;color:{RED}">અંક{("ો" if len(suffix) > 1 else "")} '
             f'<strong>{_e(", ".join(suffix))}</strong> → 0 થી બદલો</p></div></div>')
    body += f'<p aria-hidden="true" style="margin:3px;text-align:center;font-size:26px;color:{TEAL}">↓</p>'
    body += _digits(result)
    if number == '76':
        body += '<p style="margin:4px 0;text-align:center">76 ને સૌથી નજીકના દશકમાં ફેરવતાં 80 મળે છે.</p>'
    return _outer(body, alt, uid, 'rounding-action')


def render_figure(filename, alt, unique_id):
    """Return a localized HTML/SVG redraw for a supported source filename."""
    name = str(filename).replace('\\', '/').rsplit('/', 1)[-1]
    if not name.startswith(PREFIX):
        return None
    name = name[len(PREFIX):]
    uid = _uid(unique_id)
    if name in ('01_01_011.jpg', '01_01_011.png'):
        return _place_chart('5,278,194', alt, uid)
    if name == '01_01_012_img.jpg':
        return _place_chart('63,407,218', alt, uid, title=False)
    group_images = {
        '01_01_013_img.jpg': ('37,519,248', [
            ('મિલિયન', '37', 'સાડત્રીસ મિલિયન'), ('હજાર', '519', 'પાંચસો ઓગણીસ હજાર'),
            ('એકમ', '248', 'બસો અડતાલીસ')], 'to-words', False),
        '01_01_014_img.jpg': ('8,165,432,098,710', [
            ('ટ્રિલિયન', '8', 'આઠ ટ્રિલિયન'), ('બિલિયન', '165', 'એકસો પાંસઠ બિલિયન'),
            ('મિલિયન', '432', 'ચારસો બત્રીસ મિલિયન'), ('હજાર', '098', 'અઠ્ઠાણું હજાર'),
            ('એકમ', '710', 'સાતસો દસ')], 'to-words', False),
        '01_01_015_img.jpg': ('327,577,529', [
            ('મિલિયન', '327', ''), ('હજાર', '577', ''), ('એકમ', '529', '')], 'labels-only', False),
        '01_01_016_img.jpg': ('53,401,742', [
            ('મિલિયન', '53', 'ત્રેપન મિલિયન'), ('હજાર', '401', 'ચારસો એક હજાર'),
            ('એકમ', '742', 'સાતસો બેતાલીસ')], 'to-digits', True),
        '01_01_017_img.jpg': ('9,246,073,189', [
            ('બિલિયન', '9', 'નવ બિલિયન'), ('મિલિયન', '246', 'બસો છેતાલીસ મિલિયન'),
            ('હજાર', '073', 'તોતેર હજાર'), ('એકમ', '189', 'એકસો નેવ્યાસી')], 'to-digits', True),
        '01_01_018_img.jpg': ('77,000,000,000', [
            ('બિલિયન', '77', '77 બિલિયન'), ('મિલિયન', '000', ''),
            ('હજાર', '000', ''), ('એકમ', '000', '')], 'to-digits', True),
    }
    if name in group_images:
        number, groups, direction, slots = group_images[name]
        return _groups(number, groups, alt, uid, direction, slots)
    line_images = {'01_01_019.jpg': 76, '01_01_020.jpg': 72, '01_01_021.jpg': 75}
    if name in line_images:
        return _number_line(line_images[name], alt, uid)
    labels = {
        '01_01_022.jpg': ('76', 0, 'દશકનું સ્થાન', (1, '5 કરતાં મોટો છે')),
        '01_01_032_img.jpg': ('72', 0, 'દશકનું સ્થાન', (1, '5 કરતાં નાનો છે')),
        '01_01_034_img-01.png': ('843', 1, 'દશકનું સ્થાન', None),
        '01_01_035_img-01.png': ('23,658', 3, 'સોનું સ્થાન', None),
        '01_01_036_img-01.png': ('3,978', 2, 'સોનું સ્થાન', None),
        '01_01_037_img-01.png': ('147,032', 2, 'હજારનું સ્થાન', None),
        '01_01_038_img-01.png': ('29,504', 1, 'હજારનું સ્થાન', None),
    }
    if name in labels:
        number, index, label, comparison = labels[name]
        return _label(number, index, label, alt, uid, comparison)
    number_images = {
        '01_01_034_img-02.png': ('843', 2), '01_01_034_img-03.png': ('843', 2),
        '01_01_034_img-04.png': ('840', 2), '01_01_035_img-03.png': ('23,658', 4),
        '01_01_036_img-03.png': ('3,978', 3), '01_01_037_img-02.png': ('147,032', 4),
        '01_01_037_img-03.png': ('147,000', None), '01_01_038_img-02.png': ('29,504', 3),
    }
    if name in number_images:
        number, underline = number_images[name]
        return _number_only(number, underline, alt, uid)
    actions = {
        '01_01_031_img.jpg': ('76', 0, '80', True, [], True),
        '01_01_033_img.jpg': ('72', 0, '70', False, [], True),
        '01_01_035_img-02.png': ('23,658', 3, '23,700', True, [], False),
        '01_01_036_img-02.png': ('3,978', 2, '4,000', True,
            ['9 + 1 = 10', 'સોના સ્થાનમાં 0 લખો.', 'હજારના સ્થાનમાં 1 ઉમેરો.'], False),
        '01_01_038_img-03.png': ('29,504', 1, '30,000', True,
            ['9 + 1 = 10', 'હજારના સ્થાનમાં 0 લખો.', 'દસ હજારના સ્થાનમાં 1 ઉમેરો.'], False),
    }
    if name in actions:
        number, index, result, add, carry, cross = actions[name]
        return _round(number, index, result, alt, uid, add, carry, cross)
    return None
