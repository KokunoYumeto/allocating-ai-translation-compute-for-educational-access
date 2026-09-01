"""Reflow the source's18 word-cloud fragments without conflating number types."""
from html import escape as esc

WORDS=[('બીજગણિત',34),('ટકા',26),('આલેખો',29),('નમૂનાઓ',29),('વાસ્તવિક',23),('દશાંશ',23),
       ('પૂર્ણાંક',24),('ઘાતાંકો',24),('સમીકરણ',30),('ભૂમિતિ',28),('બહુપદીઓ',28),('સમીકરણો',29),
       ('પૂર્ણ',23),('પદાવલીઓ',23),('સંખ્યાઓ',46),('ગણિત',28),('અપૂર્ણાંક',29),('રૈખિક',26)]

def render_figure(filename,alt,unique_id):
    if filename!='CNX_BMath_Figure_02_00_001.jpg':return None
    description='મૂળ ચિત્રના બધા 18 ગણિત શબ્દો; નાના પડદા માટે આડી હરોળોમાં ફરી ગોઠવ્યા છે. વાસ્તવિક અને પૂર્ણ એ સંખ્યાઓના પ્રકાર દર્શાવતા શબ્દો છે.'
    colors=['#52240f','#613f00','#451920','#151337']
    out=f'<div role="group" aria-label="{esc(description)}" class="localized-figure"><div class="algebra-word-cloud" style="display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:.25rem 1rem;padding:1rem;line-height:1.65;background:white">'
    out+=''.join(f'<span style="font-size:{size}px;color:{colors[i%len(colors)]};font-weight:bold">{esc(word)}</span>' for i,(word,size) in enumerate(WORDS))
    return out+'</div><p>મૂળ ચિત્રના શબ્દો નાના પડદા માટે ફરી ગોઠવ્યા છે; બધા શબ્દો જાળવ્યા છે.</p></div>'
