"""Complete image-language coverage for A10 m82453 (50 inspected originals).

Fourteen language-bearing figures are redrawn; the enumerated thirty-six
mathematical-only originals return None. Source variables/operators are kept.
"""
from html import escape

from localized_place_value import FONT, INK, TEAL, RED, PALE, _uid, _outer

PREFIX = 'CNX_ElemAlg_Figure_01_02_'
GREEN = '#367316'
VERIFIED_MATH_ONLY = frozenset(PREFIX + suffix for suffix in (
    '001_img_new.jpg', '002_img_new.jpg',
    '005a_img_new.jpg', '005b_img_new.jpg', '005c_img_new.jpg', '005d_img_new.jpg',
    '006a_img_new.jpg', '006b_img_new.jpg', '006c_img_new.jpg', '006d_img_new.jpg',
    '007b_img.jpg', '007f_img_new.jpg', '007c_img_new.jpg', '007d_img_new.jpg', '007e_img_new.jpg',
    '008a_img_new.jpg', '008b_img_new.jpg', '008c_img_new.jpg', '008d_img_new.jpg', '008e_img_new.jpg',
    '008f_img_new.jpg', '008g_img_new.jpg', '008h_img_new.jpg', '008i_img_new.jpg', '008j_img_new.jpg',
    '009b_img_new.jpg', '009c_img_new.jpg', '009d_img_new.jpg', '009e_img_new.jpg',
    '010b_img_new.jpg', '010c_img_new.jpg', '010d_img_new.jpg', '010e_img_new.jpg',
    '011b_img_new.jpg', '012b_img_new.jpg', '013b_img_new.jpg',
))


def _m(content, color=None):
    return (f'<math xmlns="http://www.w3.org/1998/Math/MathML" style="font-size:24px;color:{color or INK}">'
            + content + '</math>')


def _v(letter):
    return _m('<mi>' + escape(letter) + '</mi>')


def _term(coefficient=None, power=None):
    result = '<mn>' + str(coefficient) + '</mn>' if coefficient is not None else ''
    if power is not None:
        result += '<mi>x</mi>' if power == 1 else '<msup><mi>x</mi><mn>' + str(power) + '</mn></msup>'
    return '<mrow>' + result + '</mrow>'


def _power_diagram(base, exponent, uid):
    arrow, title = uid + '-arrow', uid + '-title'
    italic = ' font-style="italic"' if base.isalpha() else ''
    label = f'આધાર {base}; ઘાતાંક {exponent}.'
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 120" '
        f'role="img" aria-labelledby="{title}" style="width:100%;max-width:500px;height:auto;display:block;margin:auto;font-family:{FONT}">'
        f'<title id="{title}">{escape(label)}</title>'
        f'<defs><marker id="{arrow}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
        f'<path d="M0 0 L10 5 L0 10 Z" fill="{INK}"/></marker></defs>'
        f'<text x="110" y="77" text-anchor="end" font-size="25" fill="{RED}">આધાર</text>'
        f'<text x="235" y="84" text-anchor="middle" font-size="44" fill="{INK}"{italic}>{base}</text>'
        f'<text x="259" y="55" text-anchor="middle" font-size="27" fill="{INK}"{italic}>{exponent}</text>'
        f'<text x="362" y="47" font-size="25" fill="{TEAL}">ઘાતાંક</text>'
        f'<line x1="128" y1="69" x2="216" y2="69" stroke="{INK}" stroke-width="2" marker-end="url(#{arrow})"/>'
        f'<line x1="345" y1="39" x2="278" y2="43" stroke="{INK}" stroke-width="2" marker-end="url(#{arrow})"/>'
        '</svg>'
    )


def _power_example(alt, uid):
    body = _power_diagram('2', '3', uid + '-power')
    body += '<p style="margin:3px 0">અર્થાત્ ગુણાકારમાં 2 ત્રણ વખત આવે: '
    body += '<span style="display:inline-block;white-space:nowrap">' + _m('<mn>2</mn><mo>·</mo><mn>2</mn><mo>·</mo><mn>2</mn>') + '.</span></p>'
    return _outer(body, alt, uid, 'a10-algebra-power-example')


def _power_general(alt, uid):
    body = _power_diagram('a', 'n', uid + '-power')
    body += '<div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;align-items:flex-start">'
    body += _m('<msup><mi>a</mi><mi>n</mi></msup><mo>=</mo>')
    body += (f'<div style="text-align:center"><div style="padding-bottom:4px;border-bottom:2px solid {TEAL};'
             'border-radius:0 0 7px 7px">')
    body += _m('<mi>a</mi><mo>·</mo><mi>a</mi><mo>·</mo><mo>…</mo><mo>·</mo><mi>a</mi>')
    body += '</div><p style="margin:3px 0;color:' + TEAL + '">' + _m('<mi>n</mi>', TEAL) + ' અવયવો</p></div></div>'
    return _outer(body, alt, uid, 'a10-algebra-power-general')


def _instruction(kind, number, alt, uid):
    value = _m('<mn>' + str(number) + '</mn>', RED)
    if kind == 'when':
        content = 'જ્યારે ' + _v('x') + ' = ' + value
    elif kind == 'replace':
        content = _v('x') + ' ની જગ્યાએ ' + value + ' મૂકો.'
    else:
        content = _v('x') + ' = ' + value + ' મૂકો.'
    return _outer('<p style="font-size:21px;margin:2px 0">' + content + '</p>', alt, uid, 'a10-algebra-substitution')


def _terms(terms, colors=None, plus_colors=None):
    body = '<div style="display:flex;flex-wrap:wrap;gap:5px;align-items:baseline;margin:5px 0">'
    for index, term in enumerate(terms):
        color = colors[index] if colors else INK
        body += '<span style="display:inline-flex;align-items:baseline;gap:5px;white-space:nowrap">'
        if index:
            body += _m('<mo>+</mo>', plus_colors[index] if plus_colors else INK)
        body += _m(term, color) + '</span>'
    return body + '</div>'


def _like_terms(step, alt, uid):
    instructions = {
        1: 'સજાતીય પદો ઓળખો.',
        2: 'પદાવલીને ફરી ગોઠવો જેથી સજાતીય પદો સાથે આવે.',
        3: 'સજાતીય પદો ભેગાં કરો.',
    }
    body = '<div style="display:flex;flex-wrap:wrap;gap:12px;align-items:flex-start">'
    body += (f'<div style="flex:1 1 230px;min-width:0;background:{PALE};padding:10px">'
             f'<p style="margin:0 0 4px">પગલું {step}.</p><p style="margin:0">{instructions[step]}</p></div>')
    body += '<div style="flex:1.4 1 300px;min-width:0;max-width:100%;padding:5px">'
    if step == 1:
        terms = [_term(2,2), _term(3,1), _term(7), _term(None,2), _term(4,1), _term(5)]
        body += _terms(terms)
        body += _terms(terms, [RED, TEAL, GREEN, RED, TEAL, GREEN])
    elif step == 2:
        terms = [_term(2,2), _term(None,2), _term(3,1), _term(4,1), _term(7), _term(5)]
        body += _terms(terms, [RED, RED, TEAL, TEAL, GREEN, GREEN], [INK, RED, INK, TEAL, INK, GREEN])
    else:
        body += _terms([_term(3,2), _term(7,1), _term(12)], [RED, TEAL, GREEN])
    return _outer(body + '</div></div>', alt, uid, 'a10-algebra-like-terms')


def _red(text):
    return '<span style="color:' + RED + '">' + escape(text) + '</span>'


def _word_phrases(alt, uid):
    body = ''
    for noun, suffix in [('સરવાળો','નો'), ('તફાવત','નો'), ('ગુણાકારનું પરિણામ','ના'), ('ભાગફળ','નું')]:
        body += ('<p style="margin:7px 0">' + _v('a') + ' ' + _red('અને') + ' ' + _v('b')
                 + _red(suffix) + ' <strong>' + noun + '</strong></p>')
    return _outer(body, alt, uid, 'a10-algebra-word-phrases')


def _difference_phrase(alt, uid):
    expr = _m(_term(17,1))
    body = '<div style="text-align:center">'
    body += '<p style="margin:6px 0">' + expr + ' ' + _red('અને') + ' ' + _m('<mn>5</mn>') + _red('નો') + ' <em>તફાવત</em></p>'
    body += '<p style="margin:6px 0">' + expr + ' ઓછા ' + _m('<mn>5</mn>') + '</p>'
    body += '<p style="margin:6px 0">' + _m('<mrow><mn>17</mn><mi>x</mi><mo>−</mo><mn>5</mn></mrow>') + '</p></div>'
    return _outer(body, alt, uid, 'a10-algebra-difference-phrase')


def _quotient_phrase(alt, uid):
    numerator = _m(_term(10,2))
    seven = _m('<mn>7</mn>')
    body = '<div style="text-align:center">'
    body += '<p style="margin:6px 0">' + numerator + ' ' + _red('અને') + ' ' + seven + _red('નું') + ' <em>ભાગફળ</em></p>'
    body += '<p style="margin:6px 0">' + numerator + ' ને ' + seven + ' વડે ભાગો</p>'
    body += '<p style="margin:6px 0">' + _m('<mrow><mn>10</mn><msup><mi>x</mi><mn>2</mn></msup><mo>÷</mo><mn>7</mn></mrow>') + '</p></div>'
    return _outer(body, alt, uid, 'a10-algebra-quotient-phrase')


def _selfcheck(alt, uid):
    objectives = ['ચલ અને બીજગણિતીય સંકેતોનો ઉપયોગ કરવો.',
                  'ક્રિયાઓના ક્રમથી પદાવલીઓને સાદું રૂપ આપવું.',
                  'પદાવલીની કિંમત શોધવી.',
                  'સજાતીય પદો ઓળખવા અને ભેગાં કરવા.',
                  'અંગ્રેજી શબ્દસમૂહોને બીજગણિતીય પદાવલીઓમાં ફેરવવા.']
    body = '<p style="margin:0 0 8px;font-weight:700">હું કરી શકું છું…</p>'
    for objective in objectives:
        body += ('<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:14px;margin:0 0 12px">'
                 f'<caption style="text-align:left;font-size:17px;padding:6px 0">{escape(objective)}</caption><thead><tr>')
        for label in ['આત્મવિશ્વાસથી', 'થોડી મદદથી', 'ના—મને સમજાતું નથી!']:
            body += f'<th scope="col" style="border:1px solid {TEAL};padding:7px;background:{PALE};overflow-wrap:anywhere">{label}</th>'
        body += '</tr></thead><tbody><tr>'
        body += ''.join(f'<td aria-label="ખાલી" style="border:1px solid {TEAL};height:35px">&nbsp;</td>' for _ in range(3))
        body += '</tr></tbody></table>'
    return _outer(body, alt, uid, 'a10-algebra-selfcheck')


def render_figure(filename, alt, unique_id):
    name = str(filename).replace('\\', '/').rsplit('/', 1)[-1]
    if name in VERIFIED_MATH_ONLY or not name.startswith(PREFIX):
        return None
    suffix = name[len(PREFIX):]
    uid = _uid(unique_id)
    if suffix == '003_img_new.jpg':
        return _power_example(alt, uid)
    if suffix == '004_img_new.jpg':
        return _power_general(alt, uid)
    instruction = {'009a_img_new.jpg': ('when',5), '010a_img_new.jpg': ('when',1),
                   '011a_img_new.jpg': ('replace',4), '012a_img_new.jpg': ('replace',4),
                   '013a_img_new.jpg': ('substitute',4)}
    if suffix in instruction:
        kind, number = instruction[suffix]
        return _instruction(kind, number, alt, uid)
    if suffix in ('014a_new.jpg','014b_new.jpg','014c_new.jpg'):
        return _like_terms({'014a_new.jpg':1,'014b_new.jpg':2,'014c_new.jpg':3}[suffix], alt, uid)
    if suffix == '015_img_new.jpg':
        return _word_phrases(alt, uid)
    if suffix == '016_img_new.jpg':
        return _difference_phrase(alt, uid)
    if suffix == '018_img_new.jpg':
        return _quotient_phrase(alt, uid)
    if suffix == '201_img_new.jpg':
        return _selfcheck(alt, uid)
    return None
