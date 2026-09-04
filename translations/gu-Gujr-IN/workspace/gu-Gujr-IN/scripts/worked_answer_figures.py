"""Semantic tables and countable base10 diagrams for the separate answer layer."""
from html import escape as esc


def answer_table(table):
    label = esc(table['caption_gu'])
    out = f'<div class="table-scroll" role="region" aria-label="{label}; જરૂર પડે તો આડું ખસેડીને વાંચો" tabindex="0"><table style="min-width:0"><caption>{label}</caption><thead><tr><th scope="col">{esc(table["corner_gu"])}</th>'
    out += ''.join(f'<th scope="col">{esc(str(c))}</th>' for c in table['column_headers'])+'</tr></thead><tbody>'
    for row, cells in zip(table['row_headers'], table['cells']):
        out += '<tr><th scope="row">'+esc(str(row))+'</th>'+''.join('<td aria-label="ખાલી"></td>' if v is None else '<td>'+esc(str(v))+'</td>' for v in cells)+'</tr>'
    return out+'</tbody></table></div>'


def base10_model(model):
    out = '<div class="answer-model"><p>દરેક લાંબી પટ્ટીમાં 10 એકમ છે. નાનો ચોરસ 1 એકમ દર્શાવે છે.</p>'
    for stage in model['stages']:
        tens, ones = stage['tens'], stage['ones']
        description = f'{tens} દશક અને {ones} એકમ; કુલ {tens*10+ones}.'
        # Every rod has exactly10 square units. Both rod and unit squares have
        # the same geometric size. Text alternatives do not rely on color.
        width = max(220, tens*18+85)
        out += '<figure style="margin:1rem 0;max-width:310px"><figcaption>'+esc(stage['label_gu'])+'</figcaption>'
        out += f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 120" role="img" aria-label="{esc(description)}" style="display:block;width:100%;height:auto">'
        for rod in range(tens):
            for unit in range(10):
                out += f'<rect x="{8+rod*18}" y="{8+unit*10}" width="10" height="10" fill="#dbece8" stroke="#244d50" stroke-width=".8"/>'
        start = max(tens*18+12, 12)
        for unit in range(ones):
            out += f'<rect x="{start+(unit%5)*14}" y="{8+(unit//5)*14}" width="10" height="10" fill="#fce3a3" stroke="#244d50" stroke-width=".8"/>'
        out += '</svg><p>'+esc(description)+'</p></figure>'
    return out+'</div>'


def equal_groups_model(model):
    groups,each=model['groups'],model['each']
    label=f'{groups} હરોળમાં દરેકમાં {each} ચોરસ છે. દરેક ચોરસ 1 એકમ દર્શાવે છે. કુલ {groups*each} ચોરસ.'
    width,height=each*24+20,groups*36+16
    out='<figure class="equal-groups-model" style="margin:1rem 0;max-width:350px"><figcaption>'+esc(label)+'</figcaption>'
    out+=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(label)}" style="display:block;width:100%;height:auto;max-width:{min(350,width*1.5):g}px">'
    for row in range(groups):
        for col in range(each):
            out+=f'<rect x="{10+col*24}" y="{8+row*36}" width="18" height="18" fill="#dbece8" stroke="#244d50" stroke-width="1.2"/>'
    return out+'</svg></figure>'


def hundreds_model(model):
    """A100-flat and four single units, distinct from ten separate rods."""
    assert model=={'hundreds':1,'tens':0,'ones':4}
    label='100 એકમનો 1 પાટિયો, દશકની 0 પટ્ટી અને 4 છૂટા એકમ; કુલ 104. પાટિયાના 10 હરોળ અને 10 સ્તંભમાં દરેક નાનો ચોરસ 1 એકમ છે.'
    out='<figure class="hundreds-model" style="margin:1rem 0;max-width:320px"><figcaption>'+esc(label)+'</figcaption>'
    out+=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 164 120" role="img" aria-label="{esc(label)}" style="display:block;width:100%;height:auto">'
    for row in range(10):
        for col in range(10):out+=f'<rect x="{8+col*10}" y="{8+row*10}" width="10" height="10" fill="#dbece8" stroke="#244d50" stroke-width=".8"/>'
    for unit in range(4):out+=f'<rect x="{124+(unit%2)*16}" y="{8+(unit//2)*16}" width="10" height="10" fill="#fce3a3" stroke="#244d50" stroke-width=".8"/>'
    return out+'</svg></figure>'
