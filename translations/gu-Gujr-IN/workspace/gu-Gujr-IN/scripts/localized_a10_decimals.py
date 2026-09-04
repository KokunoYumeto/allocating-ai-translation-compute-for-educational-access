"""All49 m82458 media:28 Gujarati redraws and21 inspected math-only originals."""
from html import escape
from localized_place_value import FONT,INK,TEAL,RED,PALE,_uid,_outer
from localized_a10_fractions import _n,_frac,_math

PREFIX='CNX_ElemAlg_Figure_01_07_'
CYAN='#168d92'; AQUA='#1b9f93'; GREEN='#697700'
VERIFIED_MATH_ONLY=frozenset(PREFIX+s for s in (
 '005d_img_new.jpg','006d_img_new.jpg','009b_img_new.jpg','009c_img_new.jpg',
 '010b_img_new.jpg','010c_img_new.jpg','011_img_new.jpg','013a_img_new.jpg',
 '013b_img_new.jpg','014a_img_new.jpg','014b_img_new.jpg','015_img_new.jpg',
 '019_img_new.jpg','023_img_new.jpg','020a_img_new.jpg','020b_img_new.jpg',
 '020c_img_new.jpg','021_img_new.jpg','022a_img_new.jpg','022b_img_new.jpg','022c_img_new.jpg'))


def _blank(width=120): return f'<span aria-label="ખાલી" style="display:inline-block;width:{width}px;max-width:45%;border-bottom:1px solid {INK}">&#160;</span>'


def _grid(columns,alt,uid,mode):
    body='<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,250px),1fr));gap:0">'
    for i,column in enumerate(columns):
        blank=' aria-label="ખાલી"' if not column else ''
        body+=f'<div data-column="{i+1}"{blank} style="min-width:0;min-height:42px;padding:12px;border:1px solid #b8cecb;'+(f'background:{PALE};' if i==0 else '')+'">'+column+'</div>'
    return _outer(body+'</div>',alt,uid,mode)


def _place_chart(alt,uid):
    labels=('સો હજાર','દસ હજાર','હજાર','સો','દશક','એકમ','','દશાંશ','શતાંશ','સહસ્રાંશ','દસ-સહસ્રાંશ','લક્ષાંશ')
    body='<div role="region" tabindex="0" aria-label="સ્થાનકિંમતનું આખું કોષ્ટક; આડું સરકાવી શકાય છે" style="max-width:100%;overflow-x:auto"><table style="width:980px;border-collapse:collapse;table-layout:fixed;text-align:center"><caption style="position:sticky;left:0;text-align:left;background:white;font-weight:700;font-size:20px;padding:8px 12px">સ્થાનકિંમત</caption><thead><tr>'
    for i,label in enumerate(labels): body+=f'<th scope="col"'+(' aria-label="દશાંશ ચિહ્ન"' if i==6 else '')+f' style="border:1px solid {TEAL};padding:9px;overflow-wrap:anywhere">{label or "&#160;"}</th>'
    body+='</tr></thead><tbody><tr>'+''.join(f'<td style="border:1px solid {TEAL};height:38px">{"." if i==6 else "&#160;"}</td>' for i in range(12))+'</tr></tbody></table></div>'
    return _outer(body,alt,uid,'a10-decimal-place-chart')


def _name_decimal(step,alt,uid):
    instructions={1:'દશાંશ ચિહ્નની ડાબી બાજુની સંખ્યાને શબ્દોમાં લખો.',2:'દશાંશ ચિહ્ન માટે ‘અને’ લખો.',
      3:'દશાંશ ચિહ્નની જમણી બાજુના સંખ્યાભાગને પૂર્ણ સંખ્યા ગણીને શબ્દોમાં લખો.',4:'દશાંશ સ્થાનનું નામ લખો.'}
    middle={1:'દશાંશ ચિહ્નની ડાબે 4 છે.',2:'',3:'દશાંશ ચિહ્નની જમણે 3 છે.',4:''}[step]
    right={1:'<strong>4.3</strong><br>ચાર '+_blank(),2:'ચાર અને '+_blank(),3:'ચાર અને ત્રણ '+_blank(),4:'ચાર અને ત્રણ દશાંશ'}[step]
    return _grid((f'<strong>પગલું {step}.</strong> '+instructions[step],middle,right),alt,uid,'a10-decimal-name-step-'+str(step))


def _number_words(step,alt,uid):
    words='ચૌદ અને ચોવીસ સહસ્રાંશ'
    instructions={1:'‘અને’ શબ્દ શોધો—તે દશાંશ ચિહ્નનું સ્થાન સૂચવે છે. ‘અને’ની નીચે દશાંશ ચિહ્ન મૂકો. ‘અને’ પહેલાંના શબ્દોને પૂર્ણ સંખ્યામાં ફેરવીને દશાંશ ચિહ્નની ડાબે લખો.',
      2:'છેલ્લા શબ્દમાં આપેલી સ્થાનકિંમત પરથી દશાંશ ચિહ્નની જમણે જરૂરી સ્થાનો ચિહ્નિત કરો.',
      3:'‘અને’ પછીના શબ્દોને સંખ્યામાં ફેરવીને દશાંશ ચિહ્નની જમણે લખો. છેલ્લો અંક છેલ્લા સ્થાને આવે તેમ લખો.',4:'જરૂર મુજબ ખાલી સ્થાનોમાં શૂન્ય ભરો.'}
    middle={1:'',2:'છેલ્લો શબ્દ ‘સહસ્રાંશ’ છે.',3:'',4:'દશાંશના સ્થાને શૂન્ય જરૂરી છે.'}[step]
    slots={1:'14. '+_blank(150),2:'14. '+_blank(42)+' '+_blank(42)+' '+_blank(42),
           3:'14. '+_blank(42)+' <u>2</u> <u>4</u>',4:'14. <u>0</u> <u>2</u> <u>4</u>'}[step]
    if step==1: right=f'{words}<br>ચૌદ <u>અને</u> ચોવીસ સહસ્રાંશ<br>{_blank(45)}. {_blank(90)}<br>{slots}'
    else: right=slots
    if step==2: right+='<br><span style="color:'+CYAN+'">દશાંશ&#160;&#160;&#160; શતાંશ&#160;&#160;&#160; સહસ્રાંશ</span>'
    if step==4: right+=f'<br>“{words}”ને 14.024 લખાય છે.'
    return _grid((f'<strong>પગલું {step}.</strong> '+instructions[step],middle,right),alt,uid,'a10-decimal-write-step-'+str(step))


def _number_svg(uid,place,underline=None,add=None,delete=(),number='18.379',no_add=None):
    title,marker=uid+'-title',uid+'-arrow';digits=[c for c in number];x=[26+29*i for i in range(len(digits))]
    target={'શતાંશનું સ્થાન':4,'દશાંશનું સ્થાન':3,'એકમનું સ્થાન':1}.get(place)
    body=(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 245 135" role="img" aria-labelledby="{title}" style="display:block;width:245px;max-width:100%;height:auto;margin:auto;font-family:{FONT}"><title id="{title}">{escape(place)}; સંખ્યા {number}.</title>'
          f'<defs><marker id="{marker}" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="none" stroke="{CYAN}" stroke-width="1.4"/></marker></defs>')
    if target is not None:
        body+=f'<text x="205" y="23" text-anchor="end" font-size="18" fill="{CYAN}">{escape(place)}</text><path d="M190,29 Q180,47 {x[target]},72" fill="none" stroke="{CYAN}" stroke-width="1.8" marker-end="url(#{marker})"/>'
    for i,(c,xi) in enumerate(zip(digits,x)):body+=f'<text data-digit="{i}" x="{xi}" y="101" text-anchor="middle" font-size="26" fill="{INK}">{c}</text>'
    if underline is not None: body+=f'<line data-underlined="{underline}" x1="{x[underline]-9}" x2="{x[underline]+9}" y1="107" y2="107" stroke="{INK}"/>'
    if add is not None: body+=f'<text x="5" y="132" font-size="17" fill="{CYAN}">1 ઉમેરો</text><path data-add-target="{add}" d="M65,124 Q75,114 {x[add]},105" fill="none" stroke="{CYAN}" stroke-width="1.8" marker-end="url(#{marker})"/>'
    if no_add is not None: body+=f'<text x="2" y="132" font-size="16" fill="{CYAN}">1 ઉમેરશો નહીં</text><path data-no-add-target="{no_add}" d="M103,124 Q96,113 {x[no_add]},105" fill="none" stroke="{CYAN}" stroke-width="1.8" marker-end="url(#{marker})"/>'
    if delete:
        start=x[min(delete)]-8;end=x[max(delete)]+10
        body+=f'<text x="218" y="132" text-anchor="end" font-size="17" fill="{CYAN}">કાઢો</text><path d="M177,123 Q168,113 {(start+end)/2},105" fill="none" stroke="{CYAN}" stroke-width="1.8" marker-end="url(#{marker})"/><line data-delete-indices="{",".join(map(str,delete))}" x1="{start}" y1="88" x2="{end}" y2="105" stroke="{CYAN}" stroke-width="1.4"/>'
    return body+'</svg>'


def _round_step(step,alt,uid):
    instruction={1:'આપેલી સ્થાનકિંમત શોધીને તેના પર તીર મૂકો.',2:'આપેલી સ્થાનકિંમતની જમણી બાજુના અંકને રેખાંકિત કરો.',
      3:'શું આ અંક 5 કરતાં મોટો અથવા બરાબર છે?<br><strong>હા:</strong> આપેલી સ્થાનકિંમતના અંકમાં 1 ઉમેરો.<br><strong>ના:</strong> આપેલી સ્થાનકિંમતના અંકને બદલશો નહીં.',
      4:'જે અંક સુધી ફેરવવાનું છે તેની જમણી બાજુના બધા અંક કાઢીને સંખ્યા ફરી લખો.'}[step]
    middle='9 એ 5 કરતાં મોટો અથવા બરાબર છે, એટલે 7માં 1 ઉમેરો.' if step==3 else ''
    if step==4:right='<strong>18.38</strong><p>18.379ને નજીકના શતાંશમાં ફેરવતાં 18.38 મળે છે.</p>'
    else:right=_number_svg(uid+'-number','શતાંશનું સ્થાન' if step<3 else '',5 if step>=2 else None,4 if step==3 else None,(5,) if step==3 else ())
    return _grid((f'<strong>પગલું {step}.</strong> '+instruction,middle,right),alt,uid,'a10-decimal-round-step-'+str(step))


def _round_fragment(group,step,alt,uid):
    place='દશાંશનું સ્થાન' if group=='005' else 'એકમનું સ્થાન'
    target=4 if group=='005' else 3
    if step=='a':svg=_number_svg(uid+'-n',place)
    elif step=='b':svg=_number_svg(uid+'-n',place,target)
    else:svg=_number_svg(uid+'-n','',None,3 if group=='005' else None,(4,5) if group=='005' else (2,3,4,5),no_add=1 if group=='006' else None)
    return _outer(svg,alt,uid,'a10-decimal-round-fragment-'+group+step)


def _place_counts(values,alt,uid,mode):
    body='<div style="display:flex;flex-wrap:wrap;justify-content:space-around;gap:18px">'
    for value,count in values:
        body+=f'<div style="text-align:center"><div style="font-size:22px">({value})</div><div style="color:{CYAN};border-top:2px solid {CYAN};padding-top:4px">{count} દશાંશ સ્થાન</div></div>'
    return _outer(body+'</div>',alt,uid,mode)


def _multiply100(alt,uid):
    title=uid+'-title'
    right=(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 235 165" role="img" aria-labelledby="{title}" style="display:block;width:235px;max-width:100%;height:auto;margin:auto;font-family:{FONT}">'
           f'<title id="{title}">5.63ને100વડે ગુણતાં દશાંશ ચિહ્ન બે સ્થાન જમણે ખસે અને563 મળે.</title>'
           f'<text x="118" y="30" text-anchor="middle" font-size="25" fill="{INK}">5.63 (100)</text><text x="118" y="72" text-anchor="middle" font-size="25" fill="{INK}">5.63</text>'
           f'<path data-shift="1" d="M103,80 Q113,119 123,80" fill="none" stroke="{CYAN}" stroke-width="3"/><path data-shift="2" d="M123,80 Q133,119 143,80" fill="none" stroke="{CYAN}" stroke-width="3"/>'
           f'<text x="138" y="150" text-anchor="middle" font-size="27" fill="{INK}">563</text></svg>')
    return _grid(('100માં 2 શૂન્ય છે, તેથી દશાંશ ચિહ્ન 2 સ્થાન જમણે ખસેડો.','',right),alt,uid,'a10-decimal-multiply-100')


def _place_labels(alt,uid):
    body='<div style="display:flex;justify-content:space-around;gap:15px;flex-wrap:wrap">'
    for number,label,color in [('0.3','દશાંશ',RED),('7','શતાંશ',CYAN),('4','સહસ્રાંશ',GREEN)]:
        body+=f'<div style="text-align:center;font-size:21px"><div>{number}</div><div style="color:{color}">{label}</div></div>'
    return _outer(body+'</div>',alt,uid,'a10-decimal-place-labels')


def _negative_fraction(alt,uid):
    rows=('0.625','8⟌5.000','48','20','16','40','40')
    body='<div style="max-width:260px;margin:auto;text-align:center">'
    for i,r in enumerate(rows):
        content='8⟌<span style="border-top:1px solid '+INK+'">5.000</span>' if i==1 else r
        body+=f'<div style="width:{"80px" if i==1 else "55px" if i else "auto"};margin:auto;border-bottom:{"1px solid "+INK if i in (2,4,6) else "none"};font:22px math">{content}</div>'
    body+='<p>તેથી, '+_math('<mo>−</mo>'+_frac(_n(5),_n(8))+'<mo>=</mo><mo>−</mo>'+_n('0.625'))+'</p></div>'
    return _outer(body,alt,uid,'a10-decimal-negative-fraction')


def _recurring(alt,uid):
    rows=[('1.95454',''),('22⟌43.00000',''),('22',''),('210',''),('198',''),('120','← 120 ફરી આવે છે'),('110',''),('100','← 100 ફરી આવે છે'),('88',''),('120','←'),('110',''),('100','←'),('88',''),('…','')]
    body='<p>'+_math(_frac(_n(43),_n(22)))+'; 43ને 22 વડે ભાગો.</p><table style="margin:auto;border-collapse:collapse;font:20px math"><tbody>'
    for i,(value,note) in enumerate(rows):
        border='border-bottom:1px solid '+INK+';' if i in (2,4,6,8,10,12) else ''
        shown='22⟌<span style="border-top:1px solid '+INK+'">43.00000</span>' if i==1 else value
        body+=f'<tr><td style="padding:2px 12px;text-align:right;{border}">{shown}</td><td style="padding-left:14px;color:{CYAN};font-family:{FONT};font-size:16px">{note}</td></tr>'
    body+='</tbody></table><p style="color:'+RED+'">પેટર્ન ફરી આવે છે, એટલે ભાગફળના અંકો પણ ફરી આવશે.</p>'
    body+='<p>તેથી, '+_math(_frac(_n(43),_n(22))+'<mo>=</mo>'+_n('1.9')+'<mover>'+_n(54)+'<mo>―</mo></mover>')+'</p>'
    return _outer(body,alt,uid,'a10-decimal-recurring-division')


def _selfcheck(alt,uid):
    skills=('દશાંશને શબ્દોમાં અને અંકોમાં લખવા.','દશાંશને નજીકની આપેલી સ્થાનકિંમતમાં ફેરવવા.',
      'દશાંશનો સરવાળો અને બાદબાકી કરવા.','દશાંશનો ગુણાકાર અને ભાગાકાર કરવા.',
      'દશાંશ, અપૂર્ણાંક અને ટકાને એકબીજાના સ્વરૂપમાં ફેરવવા.')
    body='<p style="font-weight:700">હું કરી શકું છું…</p>'
    for skill in skills:
        body+=f'<table style="width:100%;border-collapse:collapse;table-layout:fixed;margin-bottom:12px;font-size:14px"><caption style="text-align:left;font-size:17px;padding:6px 0">{skill}</caption><thead><tr>'
        for label in ('વિશ્વાસપૂર્વક','થોડી મદદથી','ના—હજુ સમજાયું નથી!'):body+=f'<th scope="col" style="border:1px solid {TEAL};background:{PALE};padding:7px;overflow-wrap:anywhere">{label}</th>'
        body+='</tr></thead><tbody><tr>'+''.join(f'<td aria-label="ખાલી" style="border:1px solid {TEAL};height:35px">&#160;</td>' for _ in range(3))+'</tr></tbody></table>'
    return _outer(body,alt,uid,'a10-decimal-selfcheck')


def render_figure(filename,alt,unique_id):
    if filename in VERIFIED_MATH_ONLY or not (filename.startswith(PREFIX) or filename=='CNX_ElemAlg_Figure_01_07_201_img_new.jpg'):return None
    uid=_uid(unique_id);suffix=filename[len(PREFIX):]
    if suffix=='001_new.jpg':return _place_chart(alt,uid)
    if suffix[:3]=='002':return _name_decimal('abcd'.index(suffix[3])+1,alt,uid)
    if suffix[:3]=='003':return _number_words('abcd'.index(suffix[3])+1,alt,uid)
    if suffix[:3]=='004':return _round_step('abcd'.index(suffix[3])+1,alt,uid)
    if suffix[:3] in ('005','006'):return _round_fragment(suffix[:3],suffix[3],alt,uid)
    if suffix=='009a_img_new.jpg':return _place_counts((('0.3',1),('0.7',1),('0.2',1),('0.46',2)),alt,uid,'a10-decimal-product-place-counts')
    if suffix=='009d_img_new.jpg':return _place_counts((('0.21',2),('0.092',3)),alt,uid,'a10-decimal-result-place-counts')
    if suffix=='010a_img_new.jpg':return _place_counts((('−3.9',1),('4.075',3)),alt,uid,'a10-decimal-negative-product-counts')
    if suffix=='010d_img_new.jpg':
        return _outer('<div style="text-align:center;font:22px math"><div>4.075</div><div>× 3.9</div><hr style="width:95px"><div>36675</div><div style="transform:translateX(-.55em)">12225</div><hr style="width:95px"><div>15.8925</div><div style="color:'+CYAN+';font-family:'+FONT+';font-size:17px">4 દશાંશ સ્થાન</div></div>',alt,uid,'a10-decimal-product-four-places')
    if suffix=='012_img_new.jpg':return _multiply100(alt,uid)
    if suffix=='016_img_new.jpg':return _place_labels(alt,uid)
    if suffix=='017_img_new.jpg':return _negative_fraction(alt,uid)
    if suffix=='018_img_new.jpg':return _recurring(alt,uid)
    if suffix=='201_img_new.jpg':return _selfcheck(alt,uid)
    return None
