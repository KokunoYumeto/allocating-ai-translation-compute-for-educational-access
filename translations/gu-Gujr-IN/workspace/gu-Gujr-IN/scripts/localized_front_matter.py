"""Localized diagram of the three visually inspected line relationships."""
from html import escape


def render_figure(filename,alt,unique_id):
    if filename!='CNX_ElemAlg_Figure_05_01_015_img.jpg':return None
    captions=['છેદતી રેખાઓ','સમાંતર રેખાઓ','એકબીજા પર આવતી રેખાઓ']
    # Original image contains unnumbered grids and these three short labels.
    # Coordinates below are schematic drawing positions, not invented equations.
    paths=[[(20,170,180,90),(95,20,180,190)],[(42,187,142,18),(72,187,172,18)],[(82,187,162,18)]]
    panels=[]
    for i,(caption,lines) in enumerate(zip(captions,paths)):
        marker=f'{unique_id}-arrow-{i}'
        grid=''.join(f'<path d="M{x} 20V180 M20 {x}H180"/>' for x in range(20,181,20))
        axes='<path d="M10 100H190 M100 190V10"/>'
        plot=''.join(f'<path d="M{x1} {y1}L{x2} {y2}"/>' for x1,y1,x2,y2 in lines)
        dot='<circle cx="140" cy="110" r="3.5" fill="#25b7c2"/>' if i==0 else ''
        panels.append(f'<figure style="margin:0;min-width:0"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="250" height="250" aria-hidden="true" style="display:block;max-width:100%;height:auto;margin:auto"><defs><marker id="{marker}" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto-start-reverse"><path d="M0 0L6 3L0 6Z" fill="#173e4b"/></marker></defs><g stroke="#bac5c6" stroke-width=".7" fill="none">{grid}</g><g stroke="#222" stroke-width="1" fill="none" marker-start="url(#{marker})" marker-end="url(#{marker})">{axes}</g><g stroke="#173e4b" stroke-width="2.5" fill="none" marker-start="url(#{marker})" marker-end="url(#{marker})">{plot}</g>{dot}</svg><figcaption style="text-align:center;font-weight:700">{caption}</figcaption></figure>')
    return '<div role="group" aria-label="'+escape(alt)+'" lang="gu-Gujr-IN" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,200px),1fr));gap:1rem">'+''.join(panels)+'</div>'
