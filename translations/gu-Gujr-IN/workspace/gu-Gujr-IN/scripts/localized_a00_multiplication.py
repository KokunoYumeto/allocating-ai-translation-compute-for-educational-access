"""Source-bound Gujarati multiplication labels and positional arithmetic redraws."""
from html import escape as esc


def text(x, y, value, size=18, anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}">{esc(str(value))}</text>'


def arrow(x1, y1, x2, y2):
    # Direction-independent vector arrow with a short perpendicular arrowhead.
    dx, dy = x2-x1, y2-y1
    length = (dx*dx+dy*dy)**.5
    ux, uy = dx/length, dy/length
    bx, by = x2-8*ux, y2-8*uy
    return f'<path d="M{x1} {y1} L{x2} {y2} M{bx-4*uy:.2f} {by+4*ux:.2f} L{x2} {y2} L{bx+4*uy:.2f} {by-4*ux:.2f}" fill="none" stroke="#087e80" stroke-width="1.6"/>'


def carry_diagram(complete):
    body = text(64, 27, '2', 17)+text(72, 70, '27', 28, 'middle')
    body += text(37, 110, '×', 25)+text(85, 110, '3', 28, 'middle')
    body += '<path d="M28 123 H106" stroke="#182c35"/>'
    body += text(85, 163, '1', 28, 'middle')
    if complete:
        body += text(61, 163, '8', 28, 'middle')
        body += text(192, 134, 'આ 3 × 2માં આગળ')+text(192, 161, 'લઈ જવાયેલો 2')+text(192, 188, 'ઉમેરવાથી મળે છે.')
        body += arrow(180, 176, 67, 176)
    else:
        body += text(192, 29, '21માંના 2 દશક')+text(192, 57, 'અહીં છે.')
        body += text(192, 140, '21માંનો 1 એકમ')+text(192, 168, 'અહીં છે.')
        body += arrow(180, 41, 81, 24)+arrow(180, 155, 111, 156)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 430 210" aria-hidden="true" style="display:block;width:100%;height:auto">{body}</svg>'


def partial_products(zero):
    if zero:
        upper, lower, products, total = '896', '201', ['896', '000', '1792'], '180096'
        labels = ['ગુણાકાર કરો: 1(896)', 'ગુણાકાર કરો: 0(896)', 'ગુણાકાર કરો: 2(896)']
    else:
        upper, lower, products, total = '354', '438', ['2832', '1062', '1416'], '155052'
        labels = ['ગુણાકાર કરો: 8(354)', 'ગુણાકાર કરો: 3(354)', 'ગુણાકાર કરો: 4(354)']
    # Native labels wrap at phone widths instead of becoming tiny raster-sized
    # text. Fixed numeric columns preserve every original positional blank.
    positions = [16, 38, 60, 82, 104, 126]

    def row(label, value, shift=0, multiply=False, line=False, comma=False):
        xs = positions[len(positions)-len(value)-shift:len(positions)-shift]
        assert len(xs) == len(value)
        body = ''.join(text(x, 25, v, 21, 'middle') for x, v in zip(xs, value))
        if multiply:
            body += text(59, 25, '×', 20, 'middle')
        if comma:
            body += text(71, 25, ',', 17, 'middle')
        if line:
            body += '<path d="M4 34 H138" stroke="#182c35"/>'
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 145 40" aria-hidden="true" style="display:block;width:145px;max-width:100%;height:auto">{body}</svg>'
        return '<tr><th scope="row" style="font-weight:normal">'+esc(label)+'</th><td style="width:46%;padding:.3rem">'+svg+'</td></tr>'

    out = '<div class="table-scroll" role="region" aria-label="આંશિક ગુણનફળોની ઊભી ગોઠવણી" tabindex="0"><table style="min-width:0"><thead><tr><th scope="col">પગલું</th><th scope="col">ઊભી ગોઠવણી</th></tr></thead><tbody>'
    out += row('ઉપરની સંખ્યા', upper)+row('નીચેની સંખ્યા', lower, multiply=True, line=True)
    for i, (product, label) in enumerate(zip(products, labels)):
        out += row(label, product, shift=i, line=i == 2)
    out += row('આંશિક ગુણનફળોનો સરવાળો કરો', total, comma=True)
    return out+'</tbody></table></div>'


def square_units():
    out = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(250px,100%),1fr));gap:1rem">'
    for size, unit, area, short in [(50, '1 સે.મી.', '1 ચોરસ સેન્ટિમીટર', '1 ચો. સે.મી. અથવા 1 સે.મી.²'),
                                   (127, '1 ઇંચ', '1 ચોરસ ઇંચ', '1 ચો. ઇંચ અથવા 1 ઇંચ²')]:
        body = f'<rect x="80" y="{145-size}" width="{size}" height="{size}" fill="white" stroke="#182c35"/>'
        body += text(72, 148-size/2, unit, 17, 'end')+text(80+size/2, 173, unit, 17, 'middle')
        out += f'<div><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 270 190" aria-hidden="true" style="display:block;width:100%;height:auto">{body}</svg><p>{area}<br>({short})</p></div>'
    return out+'</div>'


def area_grid():
    body = ''.join(f'<rect x="{56+c*42}" y="{27+r*42}" width="42" height="42" fill="#d9f7ef" stroke="#087e80"/>' for r in range(2) for c in range(3))
    body += text(48, 77, '2 ફૂટ', 18, 'end')+text(119, 138, '3 ફૂટ', 18, 'middle')
    body += text(210, 65, '2 · 3 = 6', 20)+text(210, 94, 'ચોરસ ફૂટ', 18)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 350 158" aria-hidden="true" style="display:block;width:100%;height:auto">{body}</svg>'


def render_figure(filename, alt, unique_id):
    factories = {'CNX_BMath_Figure_01_04_008_img.jpg': lambda: carry_diagram(False),
                 'CNX_BMath_Figure_01_04_010_img.jpg': lambda: carry_diagram(True),
                 'CNX_BMath_Figure_01_04_011_img.jpg': lambda: partial_products(False),
                 'CNX_BMath_Figure_01_04_012_img.jpg': lambda: partial_products(True),
                 'CNX_BMath_Figure_01_04_014.jpg': square_units,
                 'CNX_BMath_Figure_01_04_013.jpg': area_grid}
    factory = factories.get(filename)
    if factory is None:
        return None
    return f'<div role="group" aria-label="{esc(alt)}" class="localized-figure">'+factory()+'</div>'
