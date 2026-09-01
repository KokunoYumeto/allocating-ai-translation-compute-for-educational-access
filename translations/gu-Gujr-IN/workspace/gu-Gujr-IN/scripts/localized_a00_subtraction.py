"""Gujarati labels for the43 regrouping diagram, preserving every source block."""
from html import escape as esc


def render_figure(filename, alt, unique_id):
    if filename != 'CNX_BMath_Figure_01_03_014_img.jpg':
        return None
    out = f'<div role="group" aria-label="{esc(alt)}" class="localized-figure" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(260px,100%),1fr));gap:1rem">'
    for side, (tens, ones) in enumerate([(4, 3), (3, 13)]):
        out += '<div><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 155" style="display:block;width:100%;height:auto" aria-hidden="true">'
        out += f'<text x="82" y="23" text-anchor="middle" font-size="18">{tens} દશક</text><text x="229" y="23" text-anchor="middle" font-size="18">{ones} એકમ</text>'
        for r in range(tens):
            for c in range(10):
                red = side == 0 and r == 3
                out += cell(12+c*14, 40+r*22, red)
        for n in range(ones):
            if n < 3:
                x, y, red = 190+n*18, 40, False
            else:
                x, y, red = 190+((n-3)%5)*18, 62+((n-3)//5)*22, True
            out += cell(x, y, red)
        if side == 0:
            out += '<path d="M120 140 H178 M169 134 L179 140 L169 146" fill="none" stroke="#08656b" stroke-width="2"/>'
        out += f'</svg><p>{tens} દશક અને {ones} એકમ = 43.</p></div>'
    return out+'</div>'


def cell(x, y, red):
    fill, stroke = ('#f5c7c9', '#b62534') if red else ('#e6f5f7', '#244d50')
    return f'<rect x="{x}" y="{y}" width="14" height="14" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>'
