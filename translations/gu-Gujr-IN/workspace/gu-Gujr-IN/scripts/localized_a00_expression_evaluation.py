"""A00 m81270: six substitution prompts, selfcheck,42 inspected math originals."""
from html import escape
from localized_place_value import FONT, INK, RED, TEAL, PALE, _uid, _outer

PREFIX='CNX_BMath_Figure_02_02_'
PROMPTS={16:5,17:1,18:10,19:5,20:10,21:4}
VERIFIED_MATH_ONLY=frozenset(
    [PREFIX+s for s in (
        '007_img-01.png','007_img-02.png','007_img-03.png','008_img-02.png','008_img-03.png',
        '016_img-02.png','016_img-03.png','016_img-04.png','016_img-05.png',
        '017_img-02.png','017_img-03.png','017_img-04.png','017_img-05.png',
        '018_img-02.png','018_img-03.png','018_img-04.png','018_img-05.png',
        '019_img-02.png','019_img-03.png','019_img-04.png','019_img-05.png',
        '020_img-02.png','020_img-03.png','020_img-04.png','020_img-05.png',
        '021_img-02.png','021_img-03.png','021_img-04.png','021_img-05.png','021_img-06.png',
        '001_img.jpg','015_img.jpg',
        '022_img-01.png','022_img-02.png','022_img-03.png','022_img-04.png','022_img-05.png',
        '023_img-01.png','023_img-02.png','023_img-03.png','023_img-04.png',
    )]+['CNX_BMAth_Figure_02_02_008_img-01.png']
)


def _math(token,tag,color=INK):
    return (f'<math xmlns="http://www.w3.org/1998/Math/MathML" style="font-size:23px;color:{color}">'
            f'<{tag}>{escape(str(token))}</{tag}></math>')


def _substitution(index,alt,uid):
    body='<p style="font-size:21px;margin:2px 0;line-height:1.7">'
    if index==21: body+='દરેક '
    body+=_math('x','mi')+'ની જગ્યાએ '+_math(PROMPTS[index],'mn',RED)
    if index==20:
        body+=' અને '+_math('y','mi')+'ની જગ્યાએ '+_math(2,'mn',TEAL)
    body+=' મૂકો.</p>'
    return _outer(body,alt,uid,'a00-expression-substitution')


def _selfcheck(alt,uid):
    objectives=('બીજગણિતની પદાવલીઓની કિંમત શોધવી.','પદ, સહગુણક અને સજાતીય પદો ઓળખવાં.',
                'સજાતીય પદો ભેગાં કરીને પદાવલીઓ સરળ કરવી.','શબ્દસમૂહોને બીજગણિતની પદાવલીઓમાં ફેરવવાં.')
    body='<p style="margin:0 0 8px;font-weight:700">હું આ કરી શકું છું…</p>'
    for objective in objectives:
        body+=f'<table style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:14px;margin-bottom:12px"><caption style="text-align:left;font-size:17px;padding:6px 0">{objective}</caption><thead><tr>'
        for label in ('વિશ્વાસપૂર્વક','થોડી મદદથી','ના—મને સમજાતું નથી!'):
            body+=f'<th scope="col" style="border:1px solid {TEAL};padding:7px;background:{PALE};overflow-wrap:anywhere">{label}</th>'
        body+='</tr></thead><tbody><tr>'+''.join(f'<td aria-label="ખાલી" style="border:1px solid {TEAL};height:35px">&#160;</td>' for _ in range(3))+'</tr></tbody></table>'
    return _outer(body,alt,uid,'a00-expression-selfcheck')


def render_figure(filename,alt,unique_id):
    uid=_uid(unique_id)
    for index in PROMPTS:
        if filename==PREFIX+f'{index:03}_img-01.png': return _substitution(index,alt,uid)
    if filename=='CNX_BMath_Figure_AppB_008.jpg': return _selfcheck(alt,uid)
    return None
