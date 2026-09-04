"""Nine translated m81271 figures; all72 original occurrences visually reviewed."""
from html import escape
from localized_place_value import FONT,INK,TEAL,RED,PALE,_uid,_outer
from localized_a10_fractions import _math,_n

PREFIX='CNX_BMath_Figure_02_03_'
PROMPTS={'017':('x',5,False),'018':('y',2,False),'026':('x',13,True),'027':('a',43,True)}
LABELLED=frozenset([PREFIX+n+'_img-01.png' for n in PROMPTS]+[
    PREFIX+'032-01.png',PREFIX+'028_img-01.png',PREFIX+'029_img-01.png',
    PREFIX+'029_img-02.png','CNX_BMath_Figure_AppB_010.jpg'])
CYAN='#219bab'
SELF_SKILLS=('સંખ્યા સમીકરણનો ઉકેલ છે કે નહીં તે નક્કી કરવું.',
    'સમાનતાના બાદબાકીના ગુણધર્મને નમૂના દ્વારા દર્શાવવો.',
    'સમાનતાના બાદબાકીના ગુણધર્મ વડે સમીકરણો ઉકેલવાં.',
    'સમાનતાના સરવાળાના ગુણધર્મ વડે સમીકરણો ઉકેલવાં.',
    'શબ્દસમૂહોને બીજગણિતનાં સમીકરણોમાં ફેરવવાં.','સમીકરણ બનાવીને ઉકેલવું.')


def _prompt(number,alt,uid):
    variable,value,checking=PROMPTS[number]
    token=_math('<mi>'+variable+'</mi>')
    if checking:
        text='હવે ચકાસી શકીએ. ધારો કે '+_math('<mi>'+variable+'</mi><mo>=</mo>'+_n(value,RED))+'.'
    else: text=token+'ની જગ્યાએ '+_math(_n(value,RED))+' મૂકો.'
    return _outer('<p style="margin:0;line-height:2.2;color:'+TEAL+'">'+text+'</p>',alt,uid,'a00-equation-prompt-'+number)


def _arrow(uid):
    marker=uid+'-arrow'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 46" aria-hidden="true" style="display:block;width:45px;height:46px;margin:auto">'
            f'<defs><marker id="{marker}" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L5,3 L0,6" fill="none" stroke="{CYAN}" stroke-width="1.4"/></marker></defs>'
            f'<path d="M40,3 V38" stroke="{CYAN}" stroke-width="2" marker-end="url(#{marker})"/></svg>')


def _equals_words(product,alt,uid):
    phrase='8 અને 7નું ગુણનફળ' if product else '6 અને 9નો સરવાળો'
    value=56 if product else 15
    # Three semantic columns keep the boxed words and their replacement aligned.
    body='<div style="width:max-content;max-width:100%;margin:auto;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,110px) 42px;gap:0 8px;align-items:center;color:'+TEAL+'">'
    body+=f'<span>{phrase}</span><span data-equality-words="true" style="border:1px solid {INK};padding:3px;text-align:center">બરાબર છે</span><span>{value}.</span>'
    body+='<span></span>'+_arrow(uid)+'<span></span>'
    body+=f'<span>{phrase}</span><span style="text-align:center">'+_math('<mo>=</mo>')+f'</span><span>{value}.</span></div>'
    return _outer(body,alt,uid,'a00-equation-words-product' if product else 'a00-equation-words-sum')


def _twice_sentence():
    return (_math('<mi>x</mi>')+' અને 3ના તફાવતને બમણો કરતાં 18 '
            f'<span data-equality-words="true" style="border:1px solid {INK};padding:2px 4px;white-space:nowrap">મળે</span>.')


def _brace():
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 22" preserveAspectRatio="none" aria-hidden="true" '
            'style="display:block;width:100%;height:20px">'
            f'<path d="M2,2 Q2,10 12,10 H40 Q50,10 50,20 Q50,10 60,10 H88 Q98,10 98,2" fill="none" stroke="{CYAN}" stroke-width="1.7"/></svg>')


def _twice(complete,alt,uid):
    body='<p style="margin:0 0 14px;line-height:2;color:'+TEAL+'">'+_twice_sentence()+'</p>'
    if complete:
        mappings=(('બમણો','2',_n(2)),('x અને 3નો તફાવત','(x−3)','<mo>(</mo><mi>x</mi><mo>−</mo>'+_n(3)+'<mo>)</mo>'),
                  ('મળે','=', '<mo>=</mo>'),('18','18',_n(18)))
        body+='<div data-phrase-map="true" style="display:grid;grid-template-columns:17% 45% 20% 18%;max-width:620px;margin:auto;text-align:center;align-items:end;color:'+TEAL+'">'
        for label,key,formula in mappings:
            boxed=f'border:1px solid {INK};' if key=='=' else ''
            body+=f'<div data-map-token="{escape(key)}" style="min-width:0;padding:0 4px"><div style="min-height:65px;display:flex;align-items:end;justify-content:center;font-size:16px;overflow-wrap:anywhere"><span style="{boxed}padding:2px">{label}</span></div>'
            body+=_brace() if key!='=' else '<div style="height:20px"></div>'
            body+='<div style="padding-top:5px;white-space:nowrap">'+_math(formula)+'</div></div>'
        body+='</div>'
    return _outer(body,alt,uid,'a00-equation-twice-difference-map' if complete else 'a00-equation-twice-difference-phrase')


def _selfcheck(alt,uid):
    body='<p style="font-weight:700;margin:0 0 8px">હું આ કરી શકું છું…</p>'
    for skill in SELF_SKILLS:
        body+=f'<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:14px;margin-bottom:12px"><caption style="text-align:left;font-size:17px;padding:6px 0">{skill}</caption><thead><tr>'
        for label in ('વિશ્વાસપૂર્વક','થોડી મદદથી','ના—મને સમજાતું નથી!'):
            body+=f'<th scope="col" style="border:1px solid {TEAL};padding:7px;background:{PALE};overflow-wrap:anywhere">{label}</th>'
        body+='</tr></thead><tbody><tr>'+''.join(f'<td aria-label="ખાલી" style="border:1px solid {TEAL};height:35px">&#160;</td>' for _ in range(3))+'</tr></tbody></table>'
    return _outer(body,alt,uid,'a00-equation-properties-selfcheck')


def render_figure(filename,alt,unique_id):
    if filename not in LABELLED: return None
    uid=_uid(unique_id)
    if filename=='CNX_BMath_Figure_AppB_010.jpg': return _selfcheck(alt,uid)
    suffix=filename[len(PREFIX):]
    if suffix[:3] in PROMPTS: return _prompt(suffix[:3],alt,uid)
    if suffix=='032-01.png': return _equals_words(False,alt,uid)
    if suffix=='028_img-01.png': return _equals_words(True,alt,uid)
    return _twice(suffix=='029_img-02.png',alt,uid)
