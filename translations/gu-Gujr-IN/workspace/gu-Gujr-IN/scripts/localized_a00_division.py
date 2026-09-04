"""Actual-source division check figures, place model and perimeter labels."""
from html import escape as esc
from localized_a00_multiplication import text
from worked_answer_figures import answer_table

CHECKS={
 'CNX_BMath_Figure_01_05_047_img-06.png': {
   'quotient':359,'divisor':4,'remainder':3,'dividend':1439,
   'rows':[('ભાગફળ','359','',False),('ભાજક','4','×',True),('ગુણનફળ','1436','',False),('શેષ ઉમેરો','3','+',True),('મૂળ ભાજ્ય મળ્યું','1439','',False)],
   'carries':[(82,'2'),(104,'3')]},
 'CNX_BMath_Figure_01_05_048_img-06.png': {
   'quotient':112,'divisor':13,'remainder':5,'dividend':1461,
   'rows':[('ભાગફળ','112','',False),('ભાજક','13','×',True),('આંશિક ગુણનફળ','336','',False),('આંશિક ગુણનફળ','1120','',False),('શેષ ઉમેરો','5','+',True),('મૂળ ભાજ્ય મળ્યું','1461','',False)],
   'carries':[]},
 'CNX_BMath_Figure_01_05_049d_img.jpg': {
   'quotient':309,'divisor':241,'remainder':52,'dividend':74521,
   'rows':[('ભાગફળ','309','',False),('ભાજક','241','×',True),('આંશિક ગુણનફળ','309','',False),('આંશિક ગુણનફળ','12360','',False),('આંશિક ગુણનફળ','61800','',True),('ગુણનફળ','74469','',False),('શેષ ઉમેરો','52','+',True),('મૂળ ભાજ્ય મળ્યું','74521','',False)],
   'carries':[(104,'3')]},
}

def check_figure(record):
    out='<dl class="division-check" aria-label="ગુણાકાર અને શેષથી ભાગાકારની તપાસ" style="margin:0">'
    positions=[16,38,60,82,104,126]
    for index,(label,value,operation,line) in enumerate(record['rows']):
        carries=record['carries'] if index==0 else []
        y=49 if carries else 25; height=64 if carries else 40
        xs=positions[-len(value):]
        body=''.join(text(x,y,digit,21,'middle') for x,digit in zip(xs,value))
        body+=''.join(text(x,17,digit,14,'middle') for x,digit in carries)
        if len(value)>3:body+=text(71,y,',',17,'middle')
        if operation:body+=text(16,y,operation,20,'middle')
        if line:body+=f'<path d="M4 {y+9} H138" stroke="#182c35"/>'
        row_alt=(operation+' ' if operation else '')+f'{int(value):,}'
        if carries:row_alt+='; આગળ લઈ જવાયેલા અંકો '+', '.join(d for _,d in carries)
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 145 {height}" role="img" aria-label="{esc(row_alt)}" style="display:block;width:145px;max-width:100%;height:auto">{body}</svg>'
        out+='<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(145px,100%),1fr));align-items:center;gap:.25rem;padding:.4rem 0;border-bottom:1px solid #c4d5d8"><dt>'+label+'</dt><dd style="margin:0">'+svg+'</dd></div>'
    out+='</dl>'
    # The source checkmark is expressed in text so its meaning survives fonts.
    return out+'<p>તપાસ સાચી છે: ભાગફળ × ભાજક + શેષ = ભાજ્ય.</p>'

def place_model():
    def square(x,y):return f'<rect x="{x}" y="{y}" width="7" height="7" fill="#dbece8" stroke="#244d50" stroke-width=".5"/>'
    body=''.join(square(8+block*82+c*7,8+r*7) for block in range(2) for r in range(10) for c in range(10))
    body+=''.join(square(174+c*7,8+r*14) for r in range(5) for c in range(10))
    body+=''.join(square(259+(n%4)*13,8+(n//4)*13) for n in range(8))
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 310 89" aria-hidden="true" style="display:block;width:100%;height:auto">{body}</svg>'
    table=answer_table({'caption_gu':'258ની સ્થાનકિંમત','corner_gu':'સ્થાનકિંમત','column_headers':['અંક','કુલ કિંમત'],
                        'row_headers':['સો','દશક','એકમ',''],'cells':[[2,200],[5,50],[8,8],[None,258]]})
    table=table.replace('<th scope="row"></th>','<th scope="row" aria-label="કુલ"></th>')
    return svg+table

def perimeter(triangle):
    if triangle:
        body='<path d="M83 33 V123 H299 Z" fill="white" stroke="#182c35" stroke-width="2"/>'
        body+=text(77,83,'5 સે.મી.',18,'end')+text(191,151,'12 સે.મી.',18,'middle')+text(207,62,'13 સે.મી.',18,'middle')
    else:
        body='<rect x="65" y="40" width="210" height="112" fill="white" stroke="#182c35" stroke-width="2"/>'
        body+=text(170,28,'15 ફૂટ',18,'middle')+text(170,179,'15 ફૂટ',18,'middle')+text(57,101,'8 ફૂટ',18,'end')+text(283,101,'8 ફૂટ',18)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 350 {174 if triangle else 195}" aria-hidden="true" style="display:block;width:100%;height:auto">{body}</svg>'

def render_figure(filename,alt,unique_id):
    if filename in CHECKS:body=check_figure(CHECKS[filename])
    elif filename=='CNX_BMath_Figure_01_05_209_img.jpg':body=place_model()
    elif filename=='CNX_BMath_Figure_01_05_213_img.jpg':body=perimeter(False)
    elif filename=='CNX_BMath_Figure_01_05_214_img.jpg':body=perimeter(True)
    else:return None
    return f'<div role="group" aria-label="{esc(alt)}" class="localized-figure division-figure">'+body+'</div>'
