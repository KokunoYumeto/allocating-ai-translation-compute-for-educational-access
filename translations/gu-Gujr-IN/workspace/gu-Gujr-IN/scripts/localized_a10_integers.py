"""Gujarati figure-language coverage for A10 m82454: 65 inspected originals.

Twenty language-bearing originals have code-native redraws; forty-five
explicitly enumerated mathematical-only originals remain unchanged.
The caller supplies the reviewed Gujarati alternative and unique media ID.
008a corrects the printed instruction's erroneous -x to x; the integrating
reader must retain the keyed visible erratum fs-id1169754375291.
"""
from html import escape

from localized_place_value import FONT, INK, TEAL, RED, PALE, _uid, _outer

PREFIX = 'CNX_ElemAlg_Figure_01_03_'
POSITIVE = '#d3fff3'
POSITIVE_EDGE = '#22cbb6'
NEGATIVE = '#f7b5a8'
NEGATIVE_EDGE = '#e02526'
PAIR = '#b500db'

VERIFIED_MATH_ONLY = frozenset(PREFIX + suffix for suffix in (
    '003_new.jpg', '004_img_new.jpg', '005_new.jpg',
    '006a_img_new.jpg', '006b_img_new.jpg', '006c_img_new.jpg',
    '007c_img_new.jpg', '007d_img.jpg', '008c_img_new.jpg',
    '010b_img_new.jpg', '011b_img_new.jpg', '012b_img_new.jpg', '013b_img_new.jpg',
    '014_img_new.jpg', '015a_img_new.jpg', '015b_img_new.jpg',
    '018a_img_new.jpg', '018b_img_new.jpg', '022_img_new.jpg', '023_img_new.jpg',
    '024a_img_new.jpg', '024b_img_new.jpg', '024c_img_new.jpg',
    '025a_img_new.jpg', '025b_img_new.jpg', '025c_img_new.jpg',
    '027_img_new.jpg', '028_img_new.jpg', '029a_img_new.jpg', '029b_img_new.jpg',
    '030a_img_new.jpg', '030b_img_new.jpg', '031_img_new.jpg',
    '032a_img_new.jpg', '032b_img_new.jpg', '032c_img_new.jpg',
    '033a_img_new.jpg', '033b_img_new.jpg', '033c_img_new.jpg',
    '034a_img_new.jpg', '034b_img_new.jpg', '034c_img_new.jpg', '034d_img_new.jpg',
    '035_img_new.jpg', '036_img_new.jpg',
))


def _math(content, color=INK):
    return ('<math xmlns="http://www.w3.org/1998/Math/MathML" '
            f'style="font-size:23px;color:{color}">{content}</math>')


def _number(value, color=INK):
    sign = '<mo>−</mo>' if value < 0 else ''
    return _math(sign + f'<mn>{abs(value)}</mn>', color)


def _variable(letter):
    return _math(f'<mi>{escape(letter)}</mi>')


def _svg_start(width, height, uid, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'role="img" aria-labelledby="{uid}-title" '
            f'style="display:block;width:100%;max-width:{width}px;height:auto;margin:auto;font-family:{FONT}">'
            f'<title id="{uid}-title">{escape(label)}</title>')


def _arrow_defs(uid):
    result = '<defs>'
    for key, color in [('ink', INK), ('teal', TEAL), ('red', RED)]:
        result += (f'<marker id="{uid}-{key}" viewBox="0 0 10 10" refX="9" refY="5" '
                   'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
                   f'<path d="M0 0 L10 5 L0 10 Z" fill="{color}"/></marker>')
    return result + '</defs>'


def _arrow(x1, y1, x2, y2, uid, key='ink', both=False):
    start = f' marker-start="url(#{uid}-{key})"' if both else ''
    color = {'ink': INK, 'teal': TEAL, 'red': RED}[key]
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="2"{start} marker-end="url(#{uid}-{key})"/>')


def _text(x, y, text, size=26, color=INK):
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}" '
            f'fill="{color}">{escape(str(text))}</text>')


def _bracket(x1, x2, y, downward=False):
    mid = (x1 + x2) / 2
    direction = -1 if downward else 1
    # A brace's central notch stays aligned with the quantity it names.
    return (f'<path d="M{x1} {y+direction*6} Q{x1} {y} {x1+6} {y} '
            f'L{mid-7} {y} Q{mid} {y} {mid} {y-direction*6} '
            f'Q{mid} {y} {mid+7} {y} L{x2-6} {y} Q{x2} {y} {x2} {y+direction*6}" '
            f'fill="none" stroke="{TEAL}" stroke-width="1.7"/>')


def _axis(uid, y, minimum=-4, maximum=4, labels=None):
    body = _arrow(12, y, 548, y, uid, both=True)
    for value in range(minimum, maximum + 1):
        x = 40 + (value - minimum) * 480 / (maximum - minimum)
        body += f'<line x1="{x}" y1="{y-9}" x2="{x}" y2="{y+9}" stroke="{INK}"/>'
        if labels is None or value in labels:
            body += _text(x, y + 36, str(value).replace('-', '−'), 25)
    return body


def _numberline(kind, alt, uid):
    label = ('ઋણ સંખ્યાઓ 0ની ડાબે; ધન સંખ્યાઓ 0ની જમણે; શૂન્ય અલગ.'
             if kind == 'signs' else 'જમણી તરફ સંખ્યાઓ મોટી અને ડાબી તરફ નાની થાય છે.')
    body = _svg_start(560, 198, uid + '-line', label) + _arrow_defs(uid)
    if kind == 'signs':
        body += _axis(uid, 24)
        body += _bracket(40, 273, 93, downward=True) + _bracket(287, 520, 93, downward=True)
        body += _text(155, 139, 'ઋણ સંખ્યાઓ', 25) + _text(405, 139, 'ધન સંખ્યાઓ', 25)
        body += _arrow(280, 134, 280, 68, uid) + _text(280, 170, 'શૂન્ય', 25)
    else:
        body += _axis(uid, 79)
        body += _arrow(220, 36, 481, 36, uid, 'teal') + _text(350, 25, 'મોટી', 25)
        body += _arrow(340, 142, 90, 142, uid, 'red') + _text(215, 173, 'નાની', 25)
    return _outer(body + '</svg>', alt, uid, 'a10-integers-numberline-' + kind)


def _distance(alt, uid):
    body = _svg_start(560, 290, uid + '-line', '−5 અને 5 બંને 0થી 5 એકમ દૂર છે; |−5|=5 અને |5|=5.')
    body += _arrow_defs(uid)
    for center, value in [(143, '−5'), (417, '5')]:
        body += _text(center, 30, value + ' એ 0થી', 25)
        body += _text(center, 64, '5 એકમ દૂર છે, એટલે', 23)
        body += _text(center, 98, '|' + value + '| = 5.', 26)
    body += _arrow(100, 110, 154, 147, uid, 'teal')
    body += _arrow(460, 110, 406, 147, uid, 'teal')
    body += _text(157, 172, '5 એકમ', 25) + _text(403, 172, '5 એકમ', 25)
    body += _bracket(40, 278, 190) + _bracket(282, 520, 190)
    # Only -5, 0, 5 are ticked in the source image; no invented unit ticks.
    body += _arrow(12, 222, 548, 222, uid, both=True)
    for x, value in [(40, '−5'), (280, '0'), (520, '5')]:
        body += f'<line x1="{x}" y1="212" x2="{x}" y2="232" stroke="{INK}"/>'
        body += _text(x, 262, value, 26)
    return _outer(body + '</svg>', alt, uid, 'a10-integers-absolute-distance')


def _substitute(letter, value, introductory, alt, uid):
    variable = _variable(letter)
    replacement = _number(value, RED)
    if introductory:
        body = ('જ્યારે ' + variable + ' = ' + _number(value)
                + ' હોય ત્યારે કિંમત શોધવાનો અર્થ ' + variable
                + ' ની જગ્યાએ ' + replacement + ' મૂકવો થાય છે.')
    else:
        body = variable + ' ની જગ્યાએ ' + replacement + ' મૂકો.'
    return _outer('<p style="font-size:20px;margin:2px 0">' + body + '</p>', alt, uid, 'a10-integers-substitution')


def _circle(x, y, positive):
    fill, edge = (POSITIVE, POSITIVE_EDGE) if positive else (NEGATIVE, NEGATIVE_EDGE)
    return f'<circle cx="{x}" cy="{y}" r="16" fill="{fill}" stroke="{edge}" stroke-width="1.7"/>'


def _counter_row(count, positive, split=None):
    width = count * 41 + (18 if split else 0)
    body = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 46" '
            f'aria-hidden="true" style="display:block;width:100%;max-width:{width}px;height:auto;margin:auto">')
    for index in range(count):
        x = 20 + index * 41 + (18 if split and index >= split else 0)
        body += _circle(x, 23, positive)
    return body + '</svg>'


def _counters(count, positive, split, alt, uid):
    sign = 'ધન' if positive else 'ઋણ'
    body = _counter_row(count, positive, split)
    body += f'<p style="text-align:center;font-size:20px;margin:6px 0">{count} {sign} ચકતીઓ</p>'
    return _outer(body, alt, uid, 'a10-integers-counter-total')


def _same_sign_sum(alt, uid):
    body = '<div style="display:flex;flex-wrap:wrap;gap:24px;justify-content:center">'
    for positive, equation in [(True, '<mn>5</mn><mo>+</mo><mn>3</mn><mo>=</mo><mn>8</mn>'),
                               (False, '<mo>−</mo><mn>5</mn><mo>+</mo><mo>(</mo><mo>−</mo><mn>3</mn><mo>)</mo><mo>=</mo><mo>−</mo><mn>8</mn>')]:
        body += '<div style="flex:1 1 300px;min-width:0;text-align:center">'
        body += _counter_row(8, positive)
        body += '<p style="margin:5px 0;font-size:20px">8 ' + ('ધન' if positive else 'ઋણ') + ' ચકતીઓ</p>'
        body += _math(equation) + '</div>'
    return _outer(body + '</div>', alt, uid, 'a10-integers-same-sign-sum')


def _mixed_sign_sum(alt, uid):
    body = '<div style="display:flex;flex-wrap:wrap;gap:24px;justify-content:center">'
    for positive, formula in [(False, '<mo>−</mo><mn>5</mn><mo>+</mo><mn>3</mn>'),
                              (True, '<mn>5</mn><mo>+</mo><mo>−</mo><mn>3</mn>')]:
        sign = 'ધન' if positive else 'ઋણ'
        panel = uid + ('-positive' if positive else '-negative')
        body += '<div style="flex:1 1 270px;min-width:0;text-align:center">' + _math(formula)
        body += _svg_start(270, 128, panel, f'5 {sign} ચકતીઓ અને વિરોધી રંગની 3 ચકતીઓ; 3 શૂન્ય બનાવતી જોડીઓ.')
        for index in range(5):
            body += _circle(28 + index * 52, 37, positive)
        for index in range(3):
            x = 28 + index * 52
            body += _circle(x, 84, not positive)
            body += f'<ellipse cx="{x}" cy="60.5" rx="25" ry="52" fill="none" stroke="{PAIR}" stroke-width="2"/>'
        body += '</svg><p style="margin:4px 0;font-size:19px">' + sign + ' ચકતીઓ વધુ છે—સરવાળો ' + sign + ' છે.</p></div>'
    return _outer(body + '</div>', alt, uid, 'a10-integers-mixed-sign-sum')


def _selfcheck(alt, uid):
    objectives = ['ઋણ સંખ્યાઓ અને પૂર્ણાંકોની વિરોધી સંખ્યાઓનો ઉપયોગ કરવો.',
                  'નિરપેક્ષ મૂલ્યવાળી પદાવલીઓને સાદું રૂપ આપવું.',
                  'પૂર્ણાંકોનો સરવાળો કરવો.', 'પૂર્ણાંકોની બાદબાકી કરવી.']
    body = '<p style="margin:0 0 8px;font-weight:700">હું કરી શકું છું…</p>'
    for objective in objectives:
        body += ('<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:14px;margin:0 0 12px">'
                 f'<caption style="text-align:left;font-size:17px;padding:6px 0">{escape(objective)}</caption><thead><tr>')
        for label in ['આત્મવિશ્વાસથી', 'થોડી મદદથી', 'ના—મને સમજાતું નથી!']:
            body += f'<th scope="col" style="border:1px solid {TEAL};padding:7px;background:{PALE};overflow-wrap:anywhere">{label}</th>'
        body += '</tr></thead><tbody><tr>'
        body += ''.join(f'<td aria-label="ખાલી" style="border:1px solid {TEAL};height:35px">&nbsp;</td>' for _ in range(3))
        body += '</tr></tbody></table>'
    return _outer(body, alt, uid, 'a10-integers-selfcheck')


def render_figure(filename, alt, unique_id):
    name = str(filename).replace('\\', '/').rsplit('/', 1)[-1]
    if name in VERIFIED_MATH_ONLY or not name.startswith(PREFIX):
        return None
    suffix = name[len(PREFIX):]
    uid = _uid(unique_id)
    if suffix in ('001_new.jpg', '002_new.jpg'):
        return _numberline('signs' if suffix == '001_new.jpg' else 'order', alt, uid)
    if suffix == '009_new.jpg':
        return _distance(alt, uid)
    substitution = {
        '007a_img_new.jpg': ('x', 8, True), '007b_img_new.jpg': ('x', 8, False),
        '008a_img_new.jpg': ('x', -8, True), '008b_img_new.jpg': ('x', -8, False),
        '010a_img_new.jpg': ('x', -35, False), '011a_img_new.jpg': ('y', -20, False),
        '012a_img_new.jpg': ('u', 12, False), '013a_img_new.jpg': ('p', -14, False),
    }
    if suffix in substitution:
        return _substitute(*substitution[suffix], alt, uid)
    counters = {
        '015c_img_new.jpg': (8, True, None), '018c_img_new.jpg': (8, False, None),
        '024d_img_new.jpg': (2, False, None), '025d_img_new.jpg': (2, True, None),
        '032d_img_new.jpg': (8, False, 5), '033d_img_new.jpg': (8, True, 5),
    }
    if suffix in counters:
        return _counters(*counters[suffix], alt, uid)
    if suffix == '021_img_new.jpg':
        return _same_sign_sum(alt, uid)
    if suffix == '026_img_new.jpg':
        return _mixed_sign_sum(alt, uid)
    if suffix == '201_img_new.jpg':
        return _selfcheck(alt, uid)
    return None
