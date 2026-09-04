"""Gujarati redraws for the29 inspected originals in A10 m82455.

Fourteen language-bearing originals are redrawn. The fifteen enumerated
mathematical-only figures return None. No source/file mutation occurs here.
"""
from html import escape

from localized_place_value import FONT, INK, TEAL, RED, PALE, _uid, _outer
from localized_a10_integers import _circle, _svg_start, _math, _number, _variable, _substitute, PAIR

PREFIX = 'CNX_ElemAlg_Figure_01_04_'
BLUE = '#087fa3'
VERIFIED_MATH_ONLY = frozenset(PREFIX + suffix for suffix in (
    '003b_img_new.jpg', '003c_img_new.jpg',
    '004b_img_new.jpg', '004c_img_new.jpg', '004d_img_new.jpg',
    '005b_img_new.jpg', '005c_img.jpg', '006b_img_new.jpg', '006c_img_new.jpg',
    '007b_img_new.jpg', '007c_img_new.jpg',
    '008a_img_new.jpg', '008b_img_new.jpg', '008c_img_new.jpg', '008d_img_new.jpg',
))


def _grid(positive, uid):
    sign = 'ધન' if positive else 'ઋણ'
    body = _svg_start(230, 128, uid, f'5 ચકતીઓની 3 હરોળમાં 15 {sign} ચકતીઓ.')
    for row in range(3):
        for col in range(5):
            body += _circle(25 + 45 * col, 23 + 40 * row, positive)
    return body + '</svg>'


def _removal(removed_positive, uid):
    removed_sign = 'ધન' if removed_positive else 'ઋણ'
    body = _svg_start(270, 394, uid, f'3 વખત 5 {removed_sign} ચકતીઓ દૂર કરો; દરેક દૂર કરાતી હરોળની આસપાસ જાંબલી અંડાકાર અને નીચે ડાબી તરફનું તીર છે.')
    body += (f'<defs><marker id="{uid}-remove-arrow" viewBox="0 0 10 10" refX="9" refY="5" '
             'markerWidth="7" markerHeight="7" orient="auto">'
             f'<path d="M0 0 L10 5 L0 10 Z" fill="{PAIR}"/></marker></defs>')
    for group in range(3):
        y = 22 + group * 130
        for col in range(5):
            x = 45 + col * 45
            body += _circle(x, y, not removed_positive)
            body += _circle(x, y + 55, removed_positive)
        body += f'<ellipse cx="135" cy="{y+55}" rx="132" ry="28" fill="none" stroke="{PAIR}" stroke-width="2"/>'
        body += (f'<path d="M267 {y+55} Q269 {y+87} 68 {y+92}" fill="none" stroke="{PAIR}" '
                 f'stroke-width="2" marker-end="url(#{uid}-remove-arrow)"/>')
    return body + '</svg>'


def _formula(negative_first, negative_second):
    if negative_second:
        first = '<mo>(</mo><mo>−</mo><mn>5</mn><mo>)</mo>' if negative_first else '<mn>5</mn>'
        return first + '<mo>(</mo><mo>−</mo><mn>3</mn><mo>)</mo>'
    if negative_first:
        return '<mo>−</mo><mn>5</mn><mo>(</mo><mn>3</mn><mo>)</mo>'
    return '<mn>5</mn><mo>·</mo><mn>3</mn>'


def _multiplication(remove, alt, uid):
    body = '<div style="display:flex;flex-wrap:wrap;gap:26px;justify-content:center">'
    for negative_first in (False, True):
        panel = uid + ('-right' if negative_first else '-left')
        formula = _formula(negative_first, remove)
        first = '−5' if negative_first else '5'
        instruction = first + ('ને 3 વખત દૂર કરો.' if remove else 'ને 3 વખત ઉમેરો.')
        body += '<div style="flex:1 1 290px;min-width:0;text-align:center">'
        body += _math(formula) + f'<p style="font-size:20px;margin:5px 0">{instruction}</p>'
        if remove:
            body += _removal(not negative_first, panel + '-removal')
            body += '<p style="font-size:20px;margin:6px 0">શું બાકી રહ્યું?</p>'
        positive_result = negative_first == remove
        body += _grid(positive_result, panel + '-remaining')
        body += '<p style="font-size:20px;margin:5px 0">15 ' + ('ધન' if positive_result else 'ઋણ') + ' ચકતીઓ</p>'
        result = ('<mo>−</mo>' if not positive_result else '') + '<mn>15</mn>'
        body += _math(formula + '<mo>=</mo>' + result) + '</div>'
    return _outer(body + '</div>', alt, uid, 'a10-integer-products-removal' if remove else 'a10-integer-products-addition')


def _two_substitutions(alt, uid):
    body = (_variable('x') + ' ની જગ્યાએ ' + _number(-18, RED)
            + ' અને ' + _variable('y') + ' ની જગ્યાએ ' + _number(24, BLUE) + ' મૂકો.')
    return _outer('<p style="font-size:20px;margin:2px 0">' + body + '</p>', alt, uid, 'a10-integer-products-two-substitutions')


def _temperature_step(step, alt, uid):
    instructions = {
        1: 'પ્રશ્ન વાંચો. બધા શબ્દો અને વિચારો સમજાયા છે તેની ખાતરી કરો.',
        2: 'આપણને શું શોધવાનું કહ્યું છે તે ઓળખો.',
        3: 'તે શોધવા માટેની માહિતી આપતો શબ્દસમૂહ લખો.',
        4: 'શબ્દસમૂહને પદાવલીમાં ફેરવો.',
        5: 'પદાવલીને સાદું રૂપ આપો.',
        6: 'પ્રશ્નનો જવાબ આપતું પૂર્ણ વાક્ય લખો.',
    }
    answers = {
        1: '&nbsp;',
        2: 'સવાર અને બપોરના તાપમાનનો તફાવત',
        3: ('11 <span style="color:' + RED + ';font-style:italic">અને</span> −9'
            '<span style="color:' + RED + ';font-style:italic">નો તફાવત</span>'),
        4: _math('<mn>11</mn><mo>−</mo><mo>(</mo><mo>−</mo><mn>9</mn><mo>)</mo>'),
        5: _number(20),
        6: 'તાપમાનનો તફાવત 20 ડિગ્રી હતો.',
    }
    blank = ' aria-label="ખાલી"' if step == 1 else ''
    body = ('<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:17px;margin:0"><tbody><tr>'
            f'<th scope="row" style="width:52%;font-weight:400;text-align:left;vertical-align:top;background:{PALE};border:1px solid {TEAL};padding:10px">'
            f'<strong>પગલું {step}.</strong> {instructions[step]}</th>'
            f'<td{blank} style="vertical-align:top;border:1px solid {TEAL};padding:10px">{answers[step]}</td>'
            '</tr></tbody></table>')
    return _outer(body, alt, uid, 'a10-integer-products-temperature-step')


def _selfcheck(alt, uid):
    objectives = ['પૂર્ણાંકોનો ગુણાકાર કરવો.', 'પૂર્ણાંકોનો ભાગાકાર કરવો.',
                  'પૂર્ણાંકોવાળી પદાવલીઓને સાદું રૂપ આપવું.',
                  'પૂર્ણાંકોવાળી ચલ પદાવલીઓની કિંમત શોધવી.',
                  'અંગ્રેજી શબ્દસમૂહોને બીજગણિતીય પદાવલીઓમાં ફેરવવા.',
                  'વ્યવહારુ પ્રશ્નોમાં પૂર્ણાંકોનો ઉપયોગ કરવો.']
    body = '<p style="margin:0 0 8px;font-weight:700">હું કરી શકું છું…</p>'
    for objective in objectives:
        body += ('<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:14px;margin:0 0 12px">'
                 f'<caption style="text-align:left;font-size:17px;padding:6px 0">{escape(objective)}</caption><thead><tr>')
        for label in ['આત્મવિશ્વાસથી', 'થોડી મદદથી', 'ના—મને સમજાતું નથી!']:
            body += f'<th scope="col" style="border:1px solid {TEAL};padding:7px;background:{PALE};overflow-wrap:anywhere">{label}</th>'
        body += '</tr></thead><tbody><tr>'
        body += ''.join(f'<td aria-label="ખાલી" style="border:1px solid {TEAL};height:35px">&nbsp;</td>' for _ in range(3))
        body += '</tr></tbody></table>'
    return _outer(body, alt, uid, 'a10-integer-products-selfcheck')


def render_figure(filename, alt, unique_id):
    name = str(filename).replace('\\', '/').rsplit('/', 1)[-1]
    if name in VERIFIED_MATH_ONLY or not name.startswith(PREFIX):
        return None
    suffix = name[len(PREFIX):]
    uid = _uid(unique_id)
    if suffix in ('001_img_new.jpg', '002_img_new.jpg'):
        return _multiplication(suffix.startswith('002'), alt, uid)
    substitutions = {'003a_img_new.jpg': ('n', -5), '004a_img_new.jpg': ('n', -5),
                     '006a_img_new.jpg': ('z', 12), '007a_img_new.jpg': ('z', -12)}
    if suffix in substitutions:
        letter, value = substitutions[suffix]
        return _substitute(letter, value, False, alt, uid)
    if suffix == '005a_img_new.jpg':
        return _two_substitutions(alt, uid)
    if suffix in tuple('009' + letter + '_new.jpg' for letter in 'abcdef'):
        return _temperature_step('abcdef'.index(suffix[3]) + 1, alt, uid)
    if suffix == '201_img_new.jpg':
        return _selfcheck(alt, uid)
    return None
