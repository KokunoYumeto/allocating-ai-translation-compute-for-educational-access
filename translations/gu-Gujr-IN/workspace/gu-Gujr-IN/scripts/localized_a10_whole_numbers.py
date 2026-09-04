"""Source-inspected Gujarati redraws for all 35 A10 m82452 media occurrences.

Public API matches the A00 figure module. The renderer is pure and never edits
CNXML or errata. Visible correction notes belong to the integrating reader.
"""
from html import escape
import math

from localized_place_value import (
    FONT, INK, TEAL, RED, PALE, _uid, _outer, _digits, _place_chart, _groups,
    render_figure as render_a00,
)

PREFIX = 'CNX_ElemAlg_Figure_01_01_'


def _e(value):
    return escape(str(value), quote=True)


def _p(text):
    return '<p style="margin:5px 0">' + _e(text) + '</p>'


def _panel(step, instruction, supporting, visual, alt, uid):
    body = '<div style="display:flex;flex-wrap:wrap;gap:12px;align-items:flex-start">'
    body += (f'<div style="flex:1 1 210px;min-width:0;max-width:100%;padding:9px;background:{PALE};border-radius:4px">'
             + _p('પગલું ' + str(step) + '.'))
    for line in instruction:
        body += _p(line)
    body += '</div>'
    if supporting:
        body += '<div style="flex:1 1 200px;min-width:0;max-width:100%;padding:9px">'
        for line in supporting:
            body += _p(line)
        body += '</div>'
    body += '<div style="flex:1.25 1 235px;min-width:0;max-width:100%;padding:5px">' + visual + '</div></div>'
    return _outer(body, alt, uid, 'a10-procedure')


def _label_content(number, index, label, underline=None):
    body = _digits(number, underline=underline, colors={index: TEAL})
    return body + f'<p style="text-align:center;margin:3px 0;color:{TEAL}">{_e(label)} → <strong>{number[index]}</strong></p>'


def _action_content(number, index, result, target_lines, label=None, add_only=False):
    suffix = number[index + 1:].replace(',', '')
    colors = {index: TEAL}
    if not add_only:
        colors.update({i: RED for i in range(index + 1, len(number)) if number[i].isdigit()})
    body = _digits(number, colors=colors)
    if label:
        body += f'<p style="text-align:center;color:{TEAL};margin:3px">{_e(label)} → {number[index]}</p>'
    body += '<div style="display:flex;flex-wrap:wrap;justify-content:center;gap:8px;text-align:center">'
    body += '<div style="flex:1 1 130px;max-width:100%;padding:8px;border:1px solid #b8cecb;border-radius:4px">'
    body += _p('અંક ' + number[index] + ' →')
    for line in target_lines:
        body += _p(line)
    body += '</div>'
    if not add_only:
        body += '<div style="flex:1 1 130px;max-width:100%;padding:8px;border:1px solid #b8cecb;border-radius:4px">'
        body += _p('અંકો ' + ', '.join(suffix) + ' → 0 થી બદલો') + '</div>'
    body += '</div>'
    if result:
        body += '<p aria-hidden="true" style="text-align:center;color:#08656b;font-size:25px;margin:3px">↓</p>'
        body += _digits(result)
    return body


def _simple_line(alt, uid):
    arrow = uid + '-arrow'
    body = ('<div style="font-size:16px;display:flex;justify-content:space-between;margin:0 0 8px">'
            '<span>← નાની સંખ્યાઓ</span><span>મોટી સંખ્યાઓ →</span></div>'
            '<div style="position:relative;width:100%;height:65px">'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 40" width="100%" height="40" '
            'preserveAspectRatio="none" aria-hidden="true">'
            f'<defs><marker id="{arrow}" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" '
            'markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="#182c35"/></marker></defs>'
            f'<line x1="15" y1="20" x2="685" y2="20" stroke="#182c35" stroke-width="2" '
            f'vector-effect="non-scaling-stroke" marker-start="url(#{arrow})" marker-end="url(#{arrow})"/>')
    for i in range(7):
        x = 50 + i * 100
        body += f'<line x1="{x}" y1="11" x2="{x}" y2="29" stroke="#182c35" vector-effect="non-scaling-stroke"/>'
    body += '</svg>'
    for i in range(7):
        pct = (i + .5) / 7 * 100
        body += (f'<span aria-hidden="true" style="position:absolute;top:15px;left:calc({pct:.8f}% - 5px);'
                 f'width:10px;height:10px;background:{TEAL};border-radius:50%"></span>')
    body += '<div style="display:grid;grid-template-columns:repeat(7,minmax(0,1fr));text-align:center;font-size:17px">'
    body += ''.join('<span>' + str(i) + '</span>' for i in range(7))
    return _outer(body + '</div></div>', alt, uid, 'a10-number-line')


def _tree_svg(nodes, edges, circled, uid, width=420, height=280):
    """Each node is (numeric value, x, y); all edge products are asserted."""
    children = {}
    for parent, child in edges:
        children.setdefault(parent, []).append(child)
    for parent, child_nodes in children.items():
        assert math.prod(nodes[child][0] for child in child_nodes) == nodes[parent][0]
    for node in circled:
        value = nodes[node][0]
        assert value > 1 and all(value % d for d in range(2, math.isqrt(value)+1))
    description = 'અવયવવૃક્ષ: ' + '; '.join(
        str(nodes[parent][0]) + ' = ' + ' · '.join(str(nodes[child][0]) for child in child_nodes)
        for parent, child_nodes in children.items())
    description += '. વર્તુળમાં દર્શાવેલા અવિભાજ્ય અવયવો: ' + ', '.join(
        str(nodes[node][0]) for node in nodes if node in circled) + '.' if circled else '.'
    title = uid + '-title'
    body = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'role="img" aria-labelledby="{title}" style="width:100%;max-width:{width}px;'
            f'height:auto;display:block;margin:auto;font-family:{FONT}">'
            f'<title id="{title}">{_e(description)}</title>')
    for parent, child in edges:
        _, x1, y1 = nodes[parent]
        _, x2, y2 = nodes[child]
        body += f'<line x1="{x1}" y1="{y1+12}" x2="{x2}" y2="{y2-19}" stroke="#182c35" stroke-width="2"/>'
    for node, (value, x, y) in nodes.items():
        if node in circled:
            body += f'<circle cx="{x}" cy="{y-1}" r="19" fill="white" stroke="#08656b" stroke-width="2"/>'
        body += f'<text x="{x}" y="{y+7}" text-anchor="middle" font-size="24" fill="#182c35">{value}</text>'
    return body + '</svg>'


def _tree48(stage, uid):
    nodes = {'r': (48, 185, 30), 'a': (2, 65, 95), 'b': (24, 240, 95)}
    edges = [('r', 'a'), ('r', 'b')]
    circled = {'a'} if stage >= 2 else set()
    height = 130
    if stage >= 3:
        nodes.update({'c': (4, 180, 160), 'd': (6, 310, 160)})
        edges += [('b', 'c'), ('b', 'd')]
        height = 195
    if stage >= 4:
        nodes.update({'e': (2, 135, 230), 'f': (2, 225, 230), 'g': (2, 285, 230), 'h': (3, 365, 230)})
        edges += [('c', 'e'), ('c', 'f'), ('d', 'g'), ('d', 'h')]
        circled |= {'e', 'f', 'g', 'h'}
        height = 265
    return _tree_svg(nodes, edges, circled, uid, 410, height)


def _tree252(uid):
    nodes = {'r': (252, 210, 30), 'a': (12, 110, 100), 'b': (21, 310, 100),
             'c': (2, 50, 170), 'd': (6, 160, 170), 'e': (3, 260, 170), 'f': (7, 365, 170),
             'g': (2, 120, 240), 'h': (3, 205, 240)}
    edges = [('r', 'a'), ('r', 'b'), ('a', 'c'), ('a', 'd'), ('b', 'e'), ('b', 'f'), ('d', 'g'), ('d', 'h')]
    return _tree_svg(nodes, edges, {'c', 'e', 'f', 'g', 'h'}, uid)


def _tree18_12(uid):
    pieces = '<div style="display:flex;flex-wrap:wrap;gap:10px">'
    for number, second, children in [(18, 6, (2, 3)), (12, 4, (2, 2))]:
        nodes = {'r': (number, 140, 30), 'a': (3, 65, 95), 'b': (second, 190, 95),
                 'c': (children[0], 140, 165), 'd': (children[1], 240, 165)}
        svg = _tree_svg(nodes, [('r', 'a'), ('r', 'b'), ('b', 'c'), ('b', 'd')], {'a', 'c', 'd'}, uid+'-'+str(number), 290, 200)
        pieces += '<div style="flex:1 1 210px;min-width:0;max-width:100%">' + svg + '</div>'
    return pieces + '</div>'


def _factor_alignment(a, b, rows, factors, uid, arrows):
    """Preserve blank columns and vertical source-factor-to-LCM arrows."""
    assert math.prod(x for x in rows[0] if x) == a
    assert math.prod(x for x in rows[1] if x) == b
    assert math.prod(factors) == math.lcm(a, b)
    marker, title = uid + '-arrow', uid + '-title'
    width = 155 + 48 * len(factors)
    height = 175 if arrows else 112
    body = '<p style="font-size:16px;margin:0 0 5px">લઘુત્તમ સામાન્ય અવયવી (લ.સા.અ.)</p>' if arrows else ''
    description = '; '.join(str(n) + ' = ' + ' · '.join(str(x) for x in values if x) for n, values in [(a,rows[0]),(b,rows[1])])
    if arrows:
        description += '; લઘુત્તમ સામાન્ય અવયવી માટે દરેક સ્તંભમાંથી લેવાતા અવયવો: ' + ' · '.join(map(str,factors))
    body += (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" '
             f'aria-labelledby="{title}" style="width:100%;max-width:{width}px;height:auto;display:block;margin:auto;font-family:{FONT}">'
             f'<title id="{title}">{_e(description)}</title>')
    if arrows:
        body += (f'<defs><marker id="{marker}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" '
                 'markerHeight="5" orient="auto"><path d="M0 0 L10 5 L0 10 Z" fill="#08656b"/></marker></defs>')
        for i in range(len(factors)):
            x = 145 + i * 48
            top = 41 if rows[0][i] else 86
            body += f'<line x1="{x}" y1="{top}" x2="{x}" y2="136" stroke="#08656b" stroke-width="2" marker-end="url(#{marker})"/>'
    body += f'<line x1="20" y1="101" x2="{width-12}" y2="101" stroke="#182c35" stroke-width="2"/>'
    for n, values, y in [(a, rows[0], 30), (b, rows[1], 75)]:
        body += f'<text x="95" y="{y}" text-anchor="end" font-size="22">{n} =</text>'
        occupied = [i for i, factor in enumerate(values) if factor]
        for i, factor in enumerate(values):
            if not factor:
                continue
            x = 145 + 48 * i
            body += f'<rect x="{x-10}" y="{y-20}" width="20" height="25" fill="white"/>'
            body += f'<text x="{x}" y="{y}" text-anchor="middle" font-size="22">{factor}</text>'
            if i != occupied[-1]:
                body += f'<text x="{x+22}" y="{y}" text-anchor="middle" font-size="22">·</text>'
    if arrows:
        body += '<text x="112" y="163" text-anchor="end" font-size="18">લ.સા.અ. =</text>'
        for i, factor in enumerate(factors):
            x = 145 + 48 * i
            body += f'<text x="{x}" y="163" text-anchor="middle" font-size="22">{factor}</text>'
            if i < len(factors)-1:
                body += f'<text x="{x+22}" y="163" text-anchor="middle" font-size="22">·</text>'
    return body + '</svg>'


def _multiples_grid(base, alt, uid):
    body = '<div style="display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:4px;text-align:center;font-size:16px">'
    for i in range(1, 7):
        body += f'<div><p style="margin:0 0 6px">{base*i},{" …" if i==6 else ""}</p><p style="margin:0;color:{RED}">{base} · {i}</p></div>'
    return _outer(body+'</div>', alt, uid, 'a10-multiples-products')


def _multiples_row(number, values, highlighted, ellipsis=False):
    items = []
    for n in values:
        if n in highlighted:
            items.append(f'<strong style="color:{RED};text-decoration:underline;text-underline-offset:3px">{n}</strong>')
        else:
            items.append(str(n))
    return f'<p style="margin:6px 0"><strong>{number}:</strong> ' + ', '.join(items) + (' …' if ellipsis else '') + '</p>'


def _prime_table(alt, uid):
    body = '<div style="display:flex;flex-wrap:wrap;gap:12px">'
    for low, high in [(2, 10), (11, 19)]:
        body += ('<table style="border-collapse:collapse;flex:1 1 330px;width:330px;min-width:0;max-width:100%;font-size:15px;margin:0">'
                 '<thead><tr>')
        for heading in ['સંખ્યા', 'અવયવો', 'અવિભાજ્ય કે સંયુક્ત?']:
            body += f'<th scope="col" style="border:1px solid {TEAL};padding:6px;background:{PALE};overflow-wrap:anywhere">{heading}</th>'
        body += '</tr></thead><tbody>'
        for number in range(low, high+1):
            factors = [n for n in range(1, number+1) if number % n == 0]
            kind = 'અવિભાજ્ય' if len(factors) == 2 else 'સંયુક્ત'
            body += f'<tr><th scope="row" style="border:1px solid {TEAL};padding:6px;text-align:center">{number}</th>'
            body += f'<td style="border:1px solid {TEAL};padding:6px;overflow-wrap:anywhere">{", ".join(map(str,factors))}</td>'
            body += f'<td style="border:1px solid {TEAL};padding:6px;overflow-wrap:anywhere">{kind}</td></tr>'
        body += '</tbody></table>'
    return _outer(body+'</div>', alt, uid, 'a10-prime-composite-table')


def _selfcheck(alt, uid):
    objectives = ['પૂર્ણ સંખ્યાઓમાં સ્થાનકિંમતનો ઉપયોગ કરવો.',
                  'અવયવીઓ ઓળખવા અને વિભાજ્યતાના નિયમો લાગુ કરવા.',
                  'અવિભાજ્ય અવયવીકરણ અને લઘુત્તમ સામાન્ય અવયવી શોધવા.']
    body = '<p style="margin:0 0 8px;font-weight:700">હું કરી શકું છું…</p>'
    for objective in objectives:
        body += ('<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:14px;margin:0 0 12px">'
                 f'<caption style="text-align:left;font-size:17px;padding:6px 0">{_e(objective)}</caption><thead><tr>')
        for label in ['આત્મવિશ્વાસથી', 'થોડી મદદથી', 'ના—મને સમજાતું નથી!']:
            body += f'<th scope="col" style="border:1px solid {TEAL};padding:7px;background:{PALE};overflow-wrap:anywhere">{label}</th>'
        body += '</tr></thead><tbody><tr>'
        body += ''.join(f'<td aria-label="ખાલી" style="border:1px solid {TEAL};height:35px">&nbsp;</td>' for _ in range(3))
        body += '</tr></tbody></table>'
    return _outer(body, alt, uid, 'a10-selfcheck-table')


def render_figure(filename, alt, unique_id):
    name = str(filename).replace('\\', '/').rsplit('/', 1)[-1]
    if not name.startswith(PREFIX):
        return None
    name = name[len(PREFIX):]
    uid = _uid(unique_id)
    if name == '001_new.jpg':
        return _simple_line(alt, uid)
    reuse = {'002_new.jpg': '01_01_011.jpg', '003_img_new.jpg': '01_01_012_img.jpg',
             '005_img_new.jpg': '01_01_014_img.jpg', '022_img_new.jpg': '01_01_017_img.jpg'}
    if name in reuse:
        return render_a00('CNX_BMath_Figure_'+reuse[name], alt, unique_id)
    if name == '004_new.jpg':
        return _groups('74,218,369', [('મિલિયન','74','ચુમ્મોતેર મિલિયન'),('હજાર','218','બસો અઢાર હજાર'),
                       ('એકમ','369','ત્રણસો ઓગણસિત્તેર')], alt, uid)
    if name == '008a_new.jpg':
        return _panel(1, ['આપેલું સ્થાન તીરથી દર્શાવો. તેની ડાબી બાજુના બધા અંકો બદલાતા નથી.'],
                      ['23,658 માં સોનું સ્થાન શોધો.'], _label_content('23,658',3,'સોનું સ્થાન'), alt, uid)
    if name == '008b_new.jpg':
        return _panel(2, ['આપેલા સ્થાનની તરત જમણી બાજુના અંકની નીચે લીટી દોરો.'],
                      ['સોના સ્થાનની જમણી બાજુના 5 ની નીચે લીટી દોરો.'], _label_content('23,658',3,'સોનું સ્થાન',4), alt, uid)
    if name == '008c_new.jpg':
        return _panel(3, ['શું આ અંક 5 કરતાં મોટો કે તેના જેટલો છે?', 'હા—આપેલા સ્થાનના અંકમાં 1 ઉમેરો.',
                         'ના—આપેલા સ્થાનનો અંક બદલશો નહીં.'], ['5 એ 5 કરતાં મોટો કે તેના જેટલો હોવાથી સોના સ્થાનના 6 માં 1 ઉમેરો.'],
                      _action_content('23,658',3,None,['1 ઉમેરો'],add_only=True), alt, uid)
    if name == '008d_new.jpg':
        body = _digits('23,758',colors={4:RED,5:RED}) + _p('અંકો 5, 8 → 0 થી બદલો')
        body += _p('આમ, સૌથી નજીકના સોમાં ફેરવતાં 23,700 મળે છે.')
        return _panel(4, ['આપેલા સ્થાનની જમણી બાજુના બધા અંકોની જગ્યાએ શૂન્ય મૂકો.'],
                      ['સોના સ્થાનની જમણી બાજુના બધા અંકોની જગ્યાએ શૂન્ય મૂકો.'], body, alt, uid)
    labels = {'009a_img_new.jpg': (4,'સોનું સ્થાન',None), '009b_img_new.jpg': (4,'સોનું સ્થાન',5),
              '010a_img_new.jpg': (2,'હજારનું સ્થાન',4), '011a_img_new.jpg': (1,'દસ હજારનું સ્થાન',2)}
    if name in labels:
        index,label,underline=labels[name]
        return _outer(_label_content('103,978',index,label,underline),alt,uid,'a10-place-label')
    if name == '009c_img_new.jpg':
        return _outer(_action_content('103,978',4,'104,000',['1 ઉમેરો: 9 + 1 = 10','9 ની જગ્યાએ 0 લખો અને 1 આગળ લઈ જાઓ.'], 'સોનું સ્થાન'),alt,uid,'a10-rounding-carry')
    if name == '010b_img_new.jpg':
        return _outer(_action_content('103,978',2,'104,000',['1 ઉમેરો: 3 + 1 = 4','3 ની જગ્યાએ 4 લખો.'],'હજારનું સ્થાન'),alt,uid,'a10-rounding-action')
    if name == '011b_img_new.jpg':
        return _outer(_digits('100,000'),alt,uid,'a10-number')
    if name in ('012_img_new.jpg','013_img_new.jpg'):
        return _multiples_grid(2 if name.startswith('012') else 3, alt, uid)
    if name == '014_img_new.jpg':
        body = ('<div style="display:flex;gap:20px;justify-content:center;text-align:center;align-items:flex-start">'
                '<div><p style="font-size:28px;margin:0;border-bottom:2px solid #08656b">8 · 9</p>'+_p('અવયવો')+'</div>'
                '<span style="font-size:28px">=</span><div><p style="font-size:28px;margin:0;border-bottom:2px solid #08656b">72</p>'
                +_p('ગુણાકારનું પરિણામ')+'</div></div>')
        return _outer(body,alt,uid,'a10-factors-product')
    if name == '015_img_new.jpg':
        return _prime_table(alt,uid)
    if name == '016a_new.jpg':
        return _panel(1,['આપેલી સંખ્યા જેટલો ગુણાકાર થાય તેવા બે અવયવો શોધો. તેમનાથી બે શાખાઓ બનાવો.'],
                      ['48 = 2 · 24'],_tree48(1,uid+'-tree'),alt,uid)
    if name == '016b_new.jpg':
        return _panel(2,['અવયવ અવિભાજ્ય હોય તો તે શાખા પૂરી થાય છે. અવિભાજ્ય સંખ્યા ફરતે વર્તુળ દોરો.'],
                      ['2 અવિભાજ્ય છે. તેની ફરતે વર્તુળ દોરો.'],_tree48(2,uid+'-tree'),alt,uid)
    if name == '016c_new.jpg':
        visual = _p('24 અવિભાજ્ય નથી. તેના વધુ બે અવયવો પાડો.') + _tree48(3,uid+'-partial')
        visual += _p('4 અને 6 અવિભાજ્ય નથી. દરેકના બે અવયવો પાડો.') + _tree48(4,uid+'-complete')
        visual += _p('2 અને 3 અવિભાજ્ય છે; તેથી તેમની ફરતે વર્તુળ દોરો.')
        return _panel(3,['અવયવ અવિભાજ્ય ન હોય તો તેને બે અવયવોના ગુણાકારરૂપે લખો અને પ્રક્રિયા ચાલુ રાખો.'],[],visual,alt,uid)
    if name == '016d_new.jpg':
        return _panel(4,['સંયુક્ત સંખ્યાને વર્તુળમાંની બધી અવિભાજ્ય સંખ્યાઓના ગુણાકારરૂપે લખો.'],[],
                      '<p style="font-size:22px">48 = 2 · 2 · 2 · 2 · 3</p>',alt,uid)
    if name == '017_img_new.jpg':
        return _outer(_tree252(uid+'-tree'),alt,uid,'a10-factor-tree')
    if name == '018_img_new.jpg':
        body = _multiples_row(12,list(range(12,109,12)),{36,72,108},True)
        body += _multiples_row(18,list(range(18,109,18)),{36,72,108},True)
        body += f'<p><strong>સામાન્ય અવયવીઓ:</strong> <span style="color:{RED}">36, 72, 108 …</span></p>'
        body += f'<p><strong>લઘુત્તમ સામાન્ય અવયવી:</strong> <strong style="color:{TEAL}">36</strong></p>'
        return _outer(body,alt,uid,'a10-common-multiples')
    if name == '019_img_new.jpg':
        body = _multiples_row(15,list(range(15,121,15)),{60}) + _multiples_row(20,list(range(20,161,20)),{60})
        return _outer(body,alt,uid,'a10-multiples-lists')
    if name == '020a_new.jpg':
        return _panel(1,['દરેક સંખ્યાને અવિભાજ્ય અવયવોના ગુણાકારરૂપે લખો.'],[],_tree18_12(uid+'-trees'),alt,uid)
    if name == '020b_new.jpg':
        return _panel(2,['દરેક સંખ્યાના અવિભાજ્ય અવયવો લખો. શક્ય હોય ત્યાં સરખા અવયવો એકની નીચે એક ગોઠવો.'],
                      ['12 ના અવિભાજ્ય અવયવો લખો.','18 ના અવિભાજ્ય અવયવો લખો. શક્ય હોય ત્યાં 12 ના સરખા અવયવોની નીચે ગોઠવો; નહીં તો નવો સ્તંભ બનાવો.'],
                      _factor_alignment(12,18,[[2,2,3,None],[2,None,3,3]],[2,2,3,3],uid+'-alignment',False),alt,uid)
    if name == '020c_new.jpg':
        return _panel(3,['દરેક સ્તંભમાંથી સંખ્યા નીચે ઉતારો.'],[],
                      _factor_alignment(12,18,[[2,2,3,None],[2,None,3,3]],[2,2,3,3],uid+'-alignment',True),alt,uid)
    if name == '020d_new.jpg':
        return _panel(4,['અવયવોનો ગુણાકાર કરો.'],[],_p('લઘુત્તમ સામાન્ય અવયવી = 36'),alt,uid)
    if name == '021a_img_new.jpg':
        return _outer(_factor_alignment(24,36,[[2,2,2,3,None],[2,2,None,3,3]],[2,2,2,3,3],uid+'-alignment',True),alt,uid,'a10-lcm-alignment')
    if name == '021b_img_new.jpg':
        return _outer('<p style="font-size:23px;text-align:center;margin:3px">લઘુત્તમ સામાન્ય અવયવી = 72</p>',alt,uid,'a10-lcm-result')
    if name == '201_img_new.jpg':
        return _selfcheck(alt,uid)
    return None
