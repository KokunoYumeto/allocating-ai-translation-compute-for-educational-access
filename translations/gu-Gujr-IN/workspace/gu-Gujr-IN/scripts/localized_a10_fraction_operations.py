"""Source-bound m82457:15 Gujarati redraws;18 inspected math-only originals."""
from html import escape

from localized_place_value import FONT, INK, TEAL, RED, PALE, _uid, _outer
from localized_a10_fractions import _n, _frac, _math, _product

PREFIX='CNX_ElemAlg_Figure_01_06_'
CYAN='#00777b'
YELLOW_GREEN='#697700'
LCD='લઘુત્તમ સામાન્ય છેદ'
VERIFIED_MATH_ONLY=frozenset(PREFIX+s+'_img_new.jpg' for s in (
    '003b','003c','004a','004c','004d','004e','005b','005c',
    '006b','006c','006d','006e','007b','007c','007d','007e','008b','009b'))
LOCALIZED_SUFFIXES=('001a_new.jpg','001b_new.jpg','001c_new.jpg','002_img_new.jpg',
    '003a_img_new.jpg','004b_img_new.jpg','010a_new.jpg','010b_new.jpg','010c_new.jpg',
    '005a_img_new.jpg','006a_img_new.jpg','007a_img_new.jpg','008a_img_new.jpg',
    '009a_img_new.jpg','201_img_new.jpg')


def _fraction(a,b,color=None,negative=False):
    fraction=('<mo>−</mo>' if negative else '')+_frac(_n(a),_n(b))
    return f'<mstyle mathcolor="{color}">{fraction}</mstyle>' if color else fraction


def _equation(a,b,op='+'):
    return _math(a+'<mo>'+op+'</mo>'+b)


def _factor_slots(values):
    """Blank source columns stay genuinely blank, not hidden mathematical factors."""
    output=''
    for index,value in enumerate(values):
        if value is None: output+='<mspace width="1.5em"/>'
        else:
            dot='<mo lspace="0" rspace="0">·</mo>' if any(v is not None for v in values[index+1:]) else ''
            output+=f'<mpadded width="1.5em">{_n(value)}{dot}</mpadded>'
    return output


def _lcd(rows,factors,result,include_rows=True):
    body='<table data-lcd="'+str(result)+'" style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:16px"><colgroup><col style="width:45%"><col style="width:55%"></colgroup><tbody>'
    entries=([(str(number),values,False) for number,values in rows] if include_rows else [])
    entries += [(LCD,factors,True),(LCD,(result,),False)]
    for label,values,rule in entries:
        border='border-top:1.5px solid '+INK+';' if rule else ''
        formula='<mo>=</mo>'+_factor_slots(values)
        body+=f'<tr><th scope="row" style="font-weight:400;text-align:right;padding:6px 8px 6px 0;overflow-wrap:anywhere;{border}">{escape(label)}</th><td style="padding:6px 0;text-align:left;{border}">'+_math(formula).replace('font-size:24px','font-size:19px')+'</td></tr>'
    return body+'</tbody></table>'


def _stack(expressions):
    return ''.join('<div style="margin:14px 0;text-align:center">'+expression+'</div>' for expression in expressions)


def _steps(columns,uid,alt,mode):
    body='<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,250px),1fr));gap:0">'
    for index,column in enumerate(columns):
        blank=' aria-label="ખાલી"' if not column else ''
        background=f'background:{PALE};' if index==0 else ''
        body+=f'<div data-step-column="{index+1}"{blank} style="min-width:0;min-height:35px;padding:12px;border:1px solid #b8cecb;{background}">{column}</div>'
    return _outer(body+'</div>',alt,uid,mode)


def _common_denominator_step(step,alt,uid):
    if step==1:
        first='<strong>પગલું 1.</strong> શું છેદ સમાન છે?<p>ના—દરેક અપૂર્ણાંકને લઘુત્તમ સામાન્ય છેદ સાથે ફરી લખો.</p>'
        second=('<p>ના.<br>12 અને 18નો લઘુત્તમ સામાન્ય છેદ શોધો.</p><p>લઘુત્તમ સામાન્ય છેદ 36 ધરાવતા સમ અપૂર્ણાંકોમાં ફેરવો.</p>'
                '<p>આ સમ અપૂર્ણાંકોને સાદું રૂપ ન આપો! એમ કરશો તો મૂળ અપૂર્ણાંકો પાછા મળશે અને સમાન છેદ રહેશે નહીં!</p>')
        third=_lcd(((12,(2,2,3,None)),(18,(2,None,3,3))),(2,2,3,3),36)
        first_sum=_equation(_fraction(7,12),_fraction(5,18))
        converted=_equation(_frac(_product([_n(7),_n(3,RED)]),_product([_n(12),_n(3,RED)])),
                            _frac(_product([_n(5),_n(2,RED)]),_product([_n(18),_n(2,RED)])))
        third+=_stack((first_sum,converted,_equation(_fraction(21,36),_fraction(10,36))))
    elif step==2:
        first='<strong>પગલું 2.</strong> અપૂર્ણાંકોનો સરવાળો કે બાદબાકી કરો.'
        second='સરવાળો કરો.'
        third=_math(_fraction(31,36))
    else:
        first='<strong>પગલું 3.</strong> શક્ય હોય તો સાદું રૂપ આપો.'
        second='31 અવિભાજ્ય સંખ્યા હોવાથી તેનો 36 સાથે 1 સિવાય કોઈ સામાન્ય અવયવ નથી. જવાબ સાદામાં સાદા રૂપમાં છે.'
        third=''  # The source's right column is blank; do not invent a repeated answer.
    return _steps((first,second,third),uid,alt,'a10-fraction-common-denominator-step-'+str(step))


def _missing_factors(alt,uid):
    title,arrow=uid+'-title',uid+'-arrow'
    svg=(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 490 265" role="img" aria-labelledby="{title}" '
         f'style="display:block;width:100%;max-width:490px;margin:auto;height:auto;font-family:{FONT}">'
         f'<title id="{title}">12ના અવયવો 2·2·3 છે અને છેલ્લું સ્થાન ખાલી છે; 18ના અવયવો 2·3·3 છે અને બીજા 2નું સ્થાન ખાલી છે. બે તીર ખૂટતા અવયવોની જગ્યાઓ બતાવે છે.</title>'
         f'<defs><marker id="{arrow}" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="none" stroke="{RED}" stroke-width="1.3"/></marker></defs>'
         f'<text x="307" y="25" font-size="24" fill="{RED}">ખૂટતા અવયવો</text>'
         f'<path data-missing-target="12-last" d="M408,32 Q427,42 414,65" fill="none" stroke="{RED}" stroke-width="1.7" marker-end="url(#{arrow})"/>'
         f'<path data-missing-target="18-second" d="M345,33 Q318,63 310,111" fill="none" stroke="{RED}" stroke-width="1.7" marker-end="url(#{arrow})"/>')
    for y,label,values in ((80,12,(2,2,3,None)),(138,18,(2,None,3,3))):
        svg+=f'<text x="191" y="{y}" font-size="27" fill="{INK}">{label}</text><text x="229" y="{y}" font-size="27" fill="{INK}">=</text>'
        for index,value in enumerate(values):
            if value is None: continue
            x=260+50*index
            svg+=f'<text x="{x}" y="{y}" text-anchor="middle" font-size="27" fill="{INK}">{value}</text>'
            if any(v is not None for v in values[index+1:]):
                svg+=f'<text x="{x+25}" y="{y}" text-anchor="middle" font-size="27" fill="{INK}">·</text>'
    svg+=f'<line x1="5" x2="480" y1="160" y2="160" stroke="{INK}" stroke-width="1.5"/>'
    for y in (198,246):
        svg+=f'<text x="8" y="{y}" font-size="22" fill="{INK}">{LCD}</text><text x="229" y="{y}" font-size="27" fill="{INK}">=</text>'
    for index,value in enumerate((2,2,3,3)):
        x=260+50*index
        svg+=f'<text data-lcd-factor="{index+1}" x="{x}" y="198" text-anchor="middle" font-size="27" fill="{INK}">{value}</text>'
        if index<3: svg+=f'<text x="{x+25}" y="198" text-anchor="middle" font-size="27" fill="{INK}">·</text>'
    svg+=f'<text x="252" y="246" font-size="27" fill="{INK}">36</text>'
    svg+='</svg>'
    body=svg
    return _outer(body,alt,uid,'a10-fraction-missing-factors')


def _lcd_example(kind,alt,uid):
    if kind=='003a':
        initial=_equation(_fraction(7,15),_fraction(19,24),'−')
        factors=_lcd(((15,(None,None,None,3,5)),(24,(2,2,2,3,None))),(2,2,2,3,5),120)
    else:
        initial=''
        factors=_lcd(((5,(None,None,None,5)),(8,(2,2,2,None))),(2,2,2,5),40)
    return _outer('<div style="max-width:460px;margin:auto;text-align:center">'+initial+factors+'</div>',alt,uid,'a10-fraction-lcd-'+kind)


def _complex_step(step,alt,uid):
    half=_fraction(1,2)
    quarter=_fraction(1,4)
    square_half='<msup><mrow><mo>(</mo>'+half+'<mo>)</mo></mrow>'+_n(2)+'</msup>'
    denominator=_n(4)+'<mo>+</mo><msup>'+_n(3)+_n(2)+'</msup>'
    if step==1:
        instruction='<strong>પગલું 1.</strong> અંશને સાદું રૂપ આપો.'
        instruction+='<p>* યાદ રાખો, '+_math(square_half)+' એટલે '+_math(half+'<mo>·</mo>'+half)+'.</p>'
        expressions=(_math(_frac(square_half,denominator)),_math(_frac(quarter,denominator)))
    elif step==2:
        instruction='<strong>પગલું 2.</strong> છેદને સાદું રૂપ આપો.'
        expressions=(_math(_frac(quarter,_n(4)+'<mo>+</mo>'+_n(9))),_math(_frac(quarter,_n(13))))
    else:
        instruction='<strong>પગલું 3.</strong> અંશને છેદ વડે ભાગો. શક્ય હોય તો સાદું રૂપ આપો.'
        instruction+='<p>* યાદ રાખો, '+_math(_n(13)+'<mo>=</mo>'+_fraction(13,1))+'.</p>'
        expressions=(_math(quarter+'<mo>÷</mo>'+_n(13)),_math(quarter+'<mo>·</mo>'+_fraction(1,13)),_math(_fraction(1,52)))
    return _steps((instruction,_stack(expressions)),uid,alt,'a10-fraction-complex-step-'+str(step))


def _substitute(kind,alt,uid):
    def variable(name): return _math('<mi>'+name+'</mi>')
    if kind in ('005a','006a','007a'):
        number,denominator,name={'005a':(1,3,'x'),'006a':(3,4,'x'),'007a':(2,3,'y')}[kind]
        instruction=variable(name)+'ની જગ્યાએ '+_math(_fraction(number,denominator,RED,True))+' મૂકો.'
    elif kind=='008a':
        instruction=variable('x')+'ની જગ્યાએ '+_math(_fraction(1,4,RED))+' અને '+variable('y')+'ની જગ્યાએ '+_math(_fraction(2,3,CYAN,True))+' મૂકો.'
    else:
        instruction=(variable('p')+'ની જગ્યાએ '+_math(f'<mstyle mathcolor="{RED}"><mo>−</mo>'+_n(4)+'</mstyle>')+', '+
                     variable('q')+'ની જગ્યાએ '+_math(f'<mstyle mathcolor="{CYAN}"><mo>−</mo>'+_n(2)+'</mstyle>')+' અને '+
                     variable('r')+'ની જગ્યાએ '+_math(_n(8,YELLOW_GREEN))+' મૂકો.')
    return _outer('<p style="margin:0;line-height:2.5">'+instruction+'</p>',alt,uid,'a10-fraction-substitution-'+kind)


def _selfcheck(alt,uid):
    skills=('જુદા છેદવાળા અપૂર્ણાંકોનો સરવાળો અને બાદબાકી કરવી.',
            'અપૂર્ણાંકો પરની ક્રિયાઓ ઓળખવી અને વાપરવી.',
            'ક્રિયાઓનો ક્રમ વાપરીને જટિલ અપૂર્ણાંકોને સાદું રૂપ આપવું.',
            'અપૂર્ણાંકવાળી ચલ પદાવલીઓની કિંમત શોધવી.')
    body='<p style="font-weight:700;margin:0 0 8px">હું કરી શકું છું…</p>'
    for skill in skills:
        body+=f'<table style="width:100%;border-collapse:collapse;table-layout:fixed;margin-bottom:12px;font-size:14px"><caption style="text-align:left;font-size:17px;padding:6px 0">{skill}</caption><thead><tr>'
        for label in ('આત્મવિશ્વાસથી','થોડી મદદથી','ના—મને સમજાયું નથી!'):
            body+=f'<th scope="col" style="border:1px solid {TEAL};padding:7px;background:{PALE};overflow-wrap:anywhere">{label}</th>'
        body+='</tr></thead><tbody><tr>'+''.join(f'<td aria-label="ખાલી" style="border:1px solid {TEAL};height:35px">&#160;</td>' for _ in range(3))+'</tr></tbody></table>'
    return _outer(body,alt,uid,'a10-fraction-operations-selfcheck')


def render_figure(filename,alt,unique_id):
    if not filename.startswith(PREFIX): return None
    suffix=filename[len(PREFIX):]
    if suffix not in LOCALIZED_SUFFIXES: return None
    uid=_uid(unique_id)
    if suffix.startswith('001'): return _common_denominator_step('abc'.index(suffix[3])+1,alt,uid)
    if suffix=='002_img_new.jpg': return _missing_factors(alt,uid)
    if suffix.startswith(('003a','004b')): return _lcd_example(suffix[:4],alt,uid)
    if suffix.startswith('010'): return _complex_step('abc'.index(suffix[3])+1,alt,uid)
    if suffix=='201_img_new.jpg': return _selfcheck(alt,uid)
    return _substitute(suffix[:4],alt,uid)
