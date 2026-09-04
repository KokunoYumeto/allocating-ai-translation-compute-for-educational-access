"""Gujarati labels for every language-bearing A00 m81244 image.

All 50 originals were inspected. Forty mathematical-only figures deliberately
retain their original media via None; the nine measured shapes and self-check
are redrawn. Unknown names also return None. No source files are mutated.
"""
from html import escape

from localized_place_value import FONT, INK, TEAL, PALE, _uid, _outer

PREFIX = 'CNX_BMath_Figure_01_02_'

VERIFIED_MATH_ONLY = frozenset(PREFIX + suffix for suffix in (
    '001_img.jpg', '019_img-02.png', '019_img-03.png', '019_img-04.png',
    '016_img-02.png', '016_img-03.png', '016_img-04.png', '006_img.jpg',
    '007_img.jpg', '017_img-02.png', '017_img-03.png', '017_img-04.png',
    '010_img.jpg', '011_img.jpg', '018_img-02.png', '018_img-03.png',
    '018_img-04.png', '018_img-05.png', '014_img.jpg', '015_img.jpg',
    '001.jpg', '020-01.png', '020-02.png', '020-03.png', '020-04.png',
    '003.jpg', '004.jpg', '201_img.jpg', '203_img.jpg', '205_img.jpg',
    '207_img.jpg', '216.jpg', '217.jpg', '218.jpg', '220.jpg', '221.jpg',
    '222.jpg', '224.jpg', '225.jpg', '226.jpg',
))

# Labels pair a source number/unit with a position adjoining its original side.
# Drawings preserve topology/orientation, not an unstated scale convention.
SHAPES = {
    '002.jpg': {
        'size': (480, 245),
        'points': [(70, 50), (394, 50), (394, 122), (286, 122), (286, 194), (70, 194)],
        'labels': [('9 ફૂટ', 232, 31, 'middle'), ('4 ફૂટ', 57, 129, 'end'),
                   ('2 ફૂટ', 410, 94, 'start'), ('3 ફૂટ', 342, 150, 'middle'),
                   ('2 ફૂટ', 220, 143, 'middle'), ('6 ફૂટ', 178, 229, 'middle')],
        'arrow': (248, 147, 281, 163),
    },
    '208_img.jpg': {
        'size': (490, 240),
        'points': [(100, 175), (270, 35), (410, 175)],
        'labels': [('14 ઇંચ', 177, 103, 'end'), ('12 ઇંચ', 350, 103, 'start'),
                   ('18 ઇંચ', 255, 211, 'middle')],
    },
    '209_img.jpg': {
        'size': (520, 255),
        'points': [(120, 50), (444, 195), (120, 195)],
        'labels': [('5 સેમી', 105, 133, 'end'), ('13 સેમી', 299, 105, 'middle'),
                   ('12 સેમી', 282, 231, 'middle')],
    },
    '210_img.jpg': {
        'size': (500, 235),
        'points': [(90, 60), (405, 60), (405, 165), (90, 165)],
        'labels': [('21 મી', 247.5, 39, 'middle'), ('7 મી', 75, 119, 'end'),
                   ('7 મી', 420, 119, 'start'), ('21 મી', 247.5, 201, 'middle')],
    },
    '211_img.jpg': {
        'size': (500, 295),
        'points': [(126, 50), (373, 50), (373, 232), (126, 232)],
        'labels': [('19 ફૂટ', 249.5, 29, 'middle'), ('14 ફૂટ', 110, 148, 'end'),
                   ('14 ફૂટ', 390, 148, 'start'), ('19 ફૂટ', 249.5, 269, 'middle')],
    },
    '212_img.jpg': {
        'size': (530, 305),
        'points': [(110, 50), (395, 50), (360, 245), (145, 245)],
        'labels': [('19 યાર્ડ', 252.5, 29, 'middle'), ('18 યાર્ડ', 112, 154, 'end'),
                   ('18 યાર્ડ', 400, 154, 'start'), ('16 યાર્ડ', 252.5, 281, 'middle')],
    },
    '213_img.jpg': {
        'size': (520, 270),
        'points': [(185, 55), (335, 55), (420, 205), (100, 205)],
        'labels': [('24 મી', 260, 34, 'middle'), ('17 મી', 132, 135, 'end'),
                   ('17 મી', 388, 135, 'start'), ('29 મી', 260, 242, 'middle')],
    },
    '214_img.jpg': {
        'size': (550, 230),
        'points': [(80, 50), (440, 50), (440, 155), (155, 155), (155, 110), (80, 110)],
        'labels': [('24 ફૂટ', 260, 29, 'middle'), ('4 ફૂટ', 65, 87, 'end'),
                   ('7 ફૂટ', 457, 109, 'start'), ('19 ફૂટ', 297.5, 190, 'middle'),
                   ('5 ફૂટ', 117.5, 141, 'middle'), ('3 ફૂટ', 175, 139, 'start')],
    },
    '215_img.jpg': {
        'size': (565, 255),
        'points': [(80, 45), (455, 45), (455, 195), (245, 195), (245, 90), (80, 90)],
        'labels': [('25 ઇંચ', 267.5, 27, 'middle'), ('10 ઇંચ', 475, 127, 'start'),
                   ('14 ઇંચ', 350, 232, 'middle'), ('7 ઇંચ', 268, 151, 'start'),
                   ('11 ઇંચ', 162.5, 123, 'middle')],
        # The source omits its short left-side length. Do not add the inferred 3.
    },
}


def _shape(name, alt, uid):
    shape = SHAPES[name]
    width, height = shape['size']
    title = uid + '-title'
    body = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'role="img" aria-labelledby="{title}" style="width:100%;max-width:{width}px;'
            f'height:auto;display:block;margin:auto;font-family:{FONT}">'
            f'<title id="{title}">{escape(alt, quote=True)}</title>')
    points = ' '.join(f'{x},{y}' for x, y in shape['points'])
    body += (f'<polygon points="{points}" fill="white" stroke="{INK}" stroke-width="1.5" '
             'vector-effect="non-scaling-stroke"/>')
    if 'arrow' in shape:
        marker = uid + '-arrow'
        body += (f'<defs><marker id="{marker}" viewBox="0 0 10 10" refX="9" refY="5" '
                 'markerWidth="6" markerHeight="6" orient="auto">'
                 f'<path d="M0 0 L10 5 L0 10 Z" fill="{TEAL}"/></marker></defs>')
        x1, y1, x2, y2 = shape['arrow']
        body += (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{TEAL}" '
                 f'stroke-width="1.5" marker-end="url(#{marker})" vector-effect="non-scaling-stroke"/>')
    for label, x, y, anchor in shape['labels']:
        body += f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="24" fill="{INK}">{escape(label)}</text>'
    return _outer(body + '</svg>', alt, uid, 'a00-addition-perimeter')


def _selfcheck(alt, uid):
    objectives = ['સરવાળાની લખાવટનો ઉપયોગ.',
                  'પૂર્ણ સંખ્યાઓનો સરવાળો નમૂના દ્વારા દર્શાવવો.',
                  'નમૂના વિના પૂર્ણ સંખ્યાઓનો સરવાળો.',
                  'શબ્દોમાં આપેલી વાતને ગણિતની લખાવટમાં ફેરવવી.',
                  'વ્યવહારુ પ્રશ્નોમાં પૂર્ણ સંખ્યાઓનો સરવાળો.']
    body = '<p style="margin:0 0 8px;font-weight:700">હું આ કરી શકું છું…</p>'
    for objective in objectives:
        body += ('<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:14px;margin:0 0 12px">'
                 f'<caption style="text-align:left;font-size:17px;padding:6px 0">{escape(objective)}</caption><thead><tr>')
        for label in ['વિશ્વાસપૂર્વક', 'થોડી મદદથી', 'ના—મને સમજાતું નથી!']:
            body += f'<th scope="col" style="border:1px solid {TEAL};padding:7px;background:{PALE};overflow-wrap:anywhere">{label}</th>'
        body += '</tr></thead><tbody><tr>'
        body += ''.join(f'<td aria-label="ખાલી" style="border:1px solid {TEAL};height:35px">&nbsp;</td>' for _ in range(3))
        body += '</tr></tbody></table>'
    return _outer(body, alt, uid, 'a00-addition-selfcheck')


def render_figure(filename, alt, unique_id):
    name = str(filename).replace('\\', '/').rsplit('/', 1)[-1]
    if name in VERIFIED_MATH_ONLY:
        return None
    uid = _uid(unique_id)
    if name == 'CNX_BMath_Figure_AppB_002_A.jpg':
        return _selfcheck(alt, uid)
    if name.startswith(PREFIX) and name[len(PREFIX):] in SHAPES:
        return _shape(name[len(PREFIX):], alt, uid)
    return None
