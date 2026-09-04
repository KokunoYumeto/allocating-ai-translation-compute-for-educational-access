"""Source-bound complete Gujarati translation builder for A10 m82453."""
from pathlib import Path
import xml.etree.ElementTree as ET
import json, re, hashlib
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82453/index.cnxml'
MAP=Path(__file__).with_name('a10-m82453.slots.json')
TSV=Path(__file__).with_name('a10-m82453.gu.tsv')
OUT=Path(__file__).with_name('a10-m82453.gu.cnxml')
SHA='a8fdd235aa254c5a0a1248fa858e9b3579d9b40982bbc514cbe6a18c3e6fcbed'
CNX='http://cnx.rice.edu/cnxml';MATH='http://www.w3.org/1998/Math/MathML'
def polish(root, source):
    """Source-bound sentence review. Only prose and descriptive mtext change.

    An exact-fragment dictionary cannot distinguish an italic variable m from
    the highlighted first letter of multiplication. These explicit contexts
    retain the source tree and mathematical tokens while resolving that case
    and Gujarati postpositions split across inline source elements.
    """
    byid={e.get('id'):e for e in root.iter() if e.get('id')}
    parents={c:p for p in source.iter() for c in p}
    def ancestry(e):
        out=set()
        while e in parents:
            e=parents[e]
            if e.get('id'):out.add(e.get('id'))
        return out
    def flow(e, text, tails, texts=None):
        children=list(e);assert len(children)==len(tails),(e.get('id'),len(children),len(tails))
        e.text=text
        for c,t in zip(children,tails):c.tail=t
        if texts:
            for i,t in texts.items():children[i].text=t
    def idflow(i,text,tails,texts=None):flow(byid[i],text,tails,texts)
    styled={'fs-id1170654932101','fs-id1167833022118','fs-id1167829713618'}
    for s,g in zip(source.iter(),root.iter()):
        local=s.tag.rsplit('}',1)[-1];raw=(s.text or '').strip()
        if local=='emphasis' and raw in {'m','p','d','e'} and not (ancestry(s)&styled):g.text=raw
        if local=='mtext':
            # The mnemonic deliberately remains English with Gujarati labels.
            fixed={'P':'P','E':'E','M':'M','D':'D','A':'A','S':'S','lease':'lease','xcuse':'xcuse','ear':'ear','unt':'unt','ally':'ally','ddition':'ddition—સરવાળો','ubtraction':'ubtraction—બાદબાકી','of':'of',
                   'Seventeen more than':'આ સંખ્યાથી સત્તર વધારે:', 'Seventeen added to':'આ સંખ્યામાં સત્તર ઉમેરો:', 'Nine less than':'આ પદાવલીથી નવ ઓછું:', 'Nine subtracted from':'આ પદાવલીમાંથી નવ બાદ કરો:',
                   'the sum of':'સરવાળો:', 'the difference of':'તફાવત:', 'the product of':'ગુણાકારનું પરિણામ:', 'the quotient of':'ભાગફળ:', 'five times the sum of':'સરવાળાનું પાંચ ગણું:'}
            if raw in fixed:g.text=fixed[raw]
    idflow('fs-id1170654932101','અંગ્રેજી યાદવાક્યમાં “',[
        'y ','ear” જોડે આવે છે; તેથી ','ણાકાર અને ','ગાકારને સરખી પ્રાથમિકતા છે તે યાદ રહે છે. આપણે હંમેશાં ગુણાકારને ભાગાકાર પહેલાં કે ભાગાકારને ગુણાકાર પહેલાં કરતા નથી. બંને ડાબેથી જમણે ક્રમમાં કરીએ છીએ.'],{0:'M',1:'D',2:'ગુ',3:'ભા'})
    idflow('fs-id1170654914381','એ જ રીતે અંગ્રેજી યાદવાક્યમાં “',[
        'unt ','ally” જોડે આવે છે; તેથી ','રવાળો અને ','દબાકીને પણ સરખી પ્રાથમિકતા છે અને બંને ડાબેથી જમણે ક્રમમાં કરીએ છીએ તે યાદ રહે છે.'],{0:'A',1:'S',2:'સ',3:'બા'})
    for tid in ['fs-id1167833022118','fs-id1167829713618']:
        for e in byid[tid].iter():
            if e.tag==f'{{{CNX}}}emphasis' and e.text=='ગુ':e.tail='ણાકાર કે '
            if e.tag==f'{{{CNX}}}emphasis' and e.text=='ભા':e.tail='ગાકાર છે? હા.'
    intro=byid['fs-id1170655151082']
    intro.text=intro.text.replace('ગ્રેગ અને એલેક્સની ઉંમરો છે','ગ્રેગ અને એલેક્સની ઉંમરોને')
    intro[0].tail='';intro[1].tail=' અને 3ને '
    intro[2].tail=' કહીએ છીએ. બંને ઉંમરો બદલાય (“ચલે”) છે, પરંતુ તેમની વચ્ચેનો 3 વર્ષનો તફાવત હંમેશાં સરખો (“અચળ”) રહે છે. ગ્રેગ અને એલેક્સની ઉંમરમાં હંમેશાં 3 વર્ષનો તફાવત હોવાથી 3 એ '
    intro[3].tail=' છે.'
    idflow('fs-id1170655059811','બીજગણિતમાં ચલ દર્શાવવા મૂળાક્ષરના અક્ષરો વાપરીએ છીએ. જો ગ્રેગની ઉંમરને ',[' કહીએ, તો એલેક્સની ઉંમર ',' વડે દર્શાવી શકીએ. જુઓ ','.'])
    idflow('fs-id1170655195814','આ બદલાતી ઉંમરો દર્શાવતા અક્ષરોને ',[' કહે છે. ચલ માટે સૌથી વધુ વપરાતા અક્ષરો ', ', ', ', ', ', ', ' અને ', ' છે.'])
    byid['fs-id1170654981807'][4].tail=' છે. નીચેના કોષ્ટકમાં આ ક્રિયાઓ દર્શાવતા સંકેતો આપેલા છે. તેમાંના કેટલાક તમે કદાચ ઓળખતા હશો.'
    idflow('fs-id1170655208137','બે રાશિઓનાં મૂલ્યો સરખાં હોય ત્યારે તેમને સમાન કહીએ અને તેમની વચ્ચે ',[' મૂકીએ.'])
    idflow('fs-id1170655126926','આ સંકેત ',[' ને ', ' કહે છે.'])
    idflow('fs-id1170654880176','અહીં કેટલીક પદાવલીઓ છે જેમાં ',[' આવે છે. આ વિભાગમાં આગળ આવી પદાવલીઓને સાદું રૂપ આપીશું.'])
    idflow('fs-id1170654982105','ધારો કે 2ને અવયવ તરીકે નવ વખત લખીને તેમનો ગુણાકાર કરવાનો છે. તેને આ રીતે લખી શકીએ: ',[' આ લાંબું પડે અને કેટલા 2 લખ્યા તેનો હિસાબ રાખવો મુશ્કેલ બની શકે, તેથી ઘાતાંક વાપરીએ છીએ. ', ' ને આ રીતે લખીએ: ', ' અને ', ' ને આ રીતે લખીએ: ', ' આવી પદાવલીમાં, જેમ કે ', ' 2ને ', ' અને 3ને ', ' કહે છે. ઘાતાંક બતાવે છે કે આધારને અવયવ તરીકે કેટલી વખત લખવાનો છે.'])
    idflow('fs-id1166420392829','',[' ને “બેની ત્રીજી ઘાત” અથવા “બેનો ઘન” તરીકે વાંચીએ છીએ.'])
    idflow('fs-id1170654953415','',[' એ ', ' માં અને ', ' એ ', ' માં છે.'])
    idflow('fs-id1170654937018','',[' ને “', ' ની ', ' ઘાત” તરીકે વાંચીએ છીએ, પરંતુ નીચેની ઘાતો માટે સામાન્ય રીતે આ શબ્દો વાપરીએ છીએ:'])
    idflow('fs-id1170654905788','પદાવલીને સાદું રૂપ આપતી વખતે ',[' નો ઉપયોગ ન કરવાથી પદાવલી અને સમીકરણ વચ્ચે ગૂંચવણ થતી ટાળી શકાય છે.'])
    idflow('fs-id1170655107395','', [' એટલે તેમાં આપેલી બધી ક્રિયાઓ કરવી.'])
    idflow('fs-id1170655108012','સહગુણકને ચલની આગળની સંખ્યા સમજો. 3',[' પદનો સહગુણક 3 છે. જ્યારે આપણે ', ' લખીએ ત્યારે સહગુણક 1 છે, કારણ કે ', ''])
    idflow('fs-id1170654943862','',[' અને 3',' બંને પદોમાં ',' છે.'])
    idflow('fs-id1170654944183','',[' અને ',' બંનેમાં આ જ ચલ અને ઘાતાંક છે: ',''])
    idflow('fs-id1170654943110','પદાવલીમાં સજાતીય પદો હોય તો તેમને ભેગાં કરીને પદાવલીને સાદું રૂપ આપી શકાય છે. તમારા મત મુજબ ',[' નું સાદું રૂપ શું થાય? જો તમે 12',' વિચાર્યું હોય તો તમે સાચા છો!'])
    idflow('fs-id1170654990403','',[' ને “',' બરાબર ','” તરીકે વાંચીએ છીએ.'])
    idflow('fs-id1166422863914','“',['” ને સમાનતાની નિશાની કહે છે. ',' ને “',' બરાબર ','” તરીકે વાંચીએ છીએ.'])
    idflow('fs-id1170655155145','પદાવલીઓ ',[' < b અથવા a > ',' ને ડાબેથી જમણે કે જમણેથી ડાબે વાંચી શકાય છે; જોકે અંગ્રેજીમાં આપણે સામાન્ય રીતે ડાબેથી જમણે વાંચીએ છીએ (','). સામાન્ય રીતે, ',' < b એ b > ',' ને સમકક્ષ છે. ઉદાહરણ તરીકે 7 < 11 એ 11 > 7ને સમકક્ષ છે. અને ',' > ',' એ ',' < a ને સમકક્ષ છે. ઉદાહરણ તરીકે 17 > 4 એ 4 < 17ને સમકક્ષ છે.'])
    idflow('fs-id1170655174214','પદોનો સરવાળો કે બાદબાકી કરવાથી પદાવલી બને છે. ',[' પદાવલીમાં (જુઓ ','), ત્રણ પદો છે: ',' અને 8.'])
    byid['term-00012'].text='પદાવલી (અભિવ્યક્તિ)'
    idflow('fs-id1170655213989','',[' નો અર્થ: ',' ને અવયવ તરીકે ',' વખત લખીને ગુણાકાર કરવો.'])
    idflow('fs-id1170655228836','પદાવલી ',[' ને ',' ની ',' ઘાત તરીકે વાંચીએ છીએ; અહીં અંગ્રેજી ક્રમવાચક અંત “th”નો અર્થ n-મી ઘાત છે.'])
    idflow('fs-id1170655227649','દરેક શબ્દસમૂહ બે સંખ્યાઓ પર ક્રિયા કરવાનું કહે છે. સંખ્યાઓ શોધવા અંગ્રેજીમાં ',[' અને ',' શબ્દો શોધો.'],{0:'“of”',1:'“and”'})
    coefficient=byid['fs-id1166425225066']
    coefficient[0].tail=' 14';coefficient[1].tail=' નો સહગુણક 14 છે.'
    coefficient[4].tail=' ';coefficient[5].tail=' નો સહગુણક 15 છે.'
    coefficient[8].tail=' ';coefficient[9].tail=' નો સહગુણક 1 છે, કારણ કે '
    idflow('fs-id1170655161313','અંગ્રેજી શબ્દસમૂહને બીજગણિતીય પદાવલીમાં ફેરવો: ',[' સરવાળો: ',' અને ','; ',' ગુણાકારનું પરિણામ: ',' અને ',''])
    for i in ['fs-id1170655129489','fs-id1170655202549','fs-id1170655133650']:
        idflow(i,'જ્યારે ',[' ત્યારે નીચેની પદાવલીઓની કિંમત શોધો: ',' ','; ',' ',''])
    idflow('fs-id1170655355494','દરેક અંગ્રેજી શબ્દસમૂહને બીજગણિતીય પદાવલીમાં ફેરવો: ',[' તફાવત: ',' અને ','; ',' ભાગફળ: ',' અને ',''])
    idflow('fs-id1170655208557','અંગ્રેજી શબ્દસમૂહને બીજગણિતીય પદાવલીમાં ફેરવો: ',[' ',' અને 13 વચ્ચેનો તફાવત; ',' 12',' અને 2નું ભાગફળ.'])
    idflow('fs-id1170654972286','અંગ્રેજી શબ્દસમૂહને બીજગણિતીય પદાવલીમાં ફેરવો: ',[' ',' કરતાં સત્તર વધારે; ',' આ પદાવલીથી નવ ઓછું: ',''])
    idflow('fs-id1170655204430','અંગ્રેજી શબ્દસમૂહને બીજગણિતીય પદાવલીમાં ફેરવો: ',[' ',' કરતાં અગિયાર વધારે; ',' આ પદાવલીથી ચૌદ ઓછું: ',''])
    idflow('fs-id1170655164748','અંગ્રેજી શબ્દસમૂહને બીજગણિતીય પદાવલીમાં ફેરવો: ',[' ',' કરતાં 13 વધારે; ',' 8',' કરતાં 18 ઓછું.'])
    idflow('fs-id1170655113791','અંગ્રેજી શબ્દસમૂહને બીજગણિતીય પદાવલીમાં ફેરવો: ',[' 2',' અને 8 વચ્ચેનો તફાવત; ',' ',' અને 8 વચ્ચેના તફાવતનું 2 ગણું.'])
    for i,n in [('fs-id1170655104999','5'),('fs-id1170655177758','4')]:
        idflow(i,'અંગ્રેજી શબ્દસમૂહને બીજગણિતીય પદાવલીમાં ફેરવો: ',[' ',' અને ',f' ના સરવાળાનું {n} ગણું; ',f' {n}',' અને ',' નો સરવાળો.'])
    for i in ['fs-id1170655201628','fs-id1170655196339']:idflow(i,'',[' અને 3',' નો સરવાળો'])
    idflow('fs-id1170655150293','',[' અને 3નું ભાગફળ'])
    idflow('fs-id1170655229796','',[' અને 8નું ભાગફળ'])
    idflow('fs-id1170655114665','',[' અને નવ વચ્ચેના તફાવતનું આઠ ગણું'])
    idflow('fs-id1170654888990','',[' અને એક વચ્ચેના તફાવતનું સાત ગણું'])
    idflow('fs-id1170655150880','“',[' અને ',' ના સરવાળાનું 4 ગણું” તથા “4',' અને ',' નો સરવાળો” શબ્દસમૂહો વચ્ચેનો તફાવત સમજાવો.'])
    # The source phrase bank has hard line breaks. Keep those lines and their
    # operand sequence, but place Gujarati postpositions on the correct tail.
    for s,g in zip(source.iter(),root.iter()):
        if s.tag!=f'{{{CNX}}}entry':continue
        raw=' '.join(''.join(s.itertext()).split())
        simple={'the sum of a and b':' નો સરવાળો','the difference of a and b':' વચ્ચેનો તફાવત','the product of a and b':' નો ગુણાકાર','the quotient of x and y':' નું ભાગફળ'}
        if raw in simple:flow(g,'',[' અને ',simple[raw]])
        elif raw=='the quotient of a and b, a is called the dividend, and b is called the divisor':flow(g,'',[' અને ',' નું ભાગફળ; ',' ને ભાજ્ય અને ',' ને ભાજક કહે છે.'])
        elif raw=='the difference of n and one':flow(g,'',[' અને એક વચ્ચેનો તફાવત'])
        elif raw.startswith('a is ') and len(g)==3:
            ending={'a is not equal to b':' ની બરાબર નથી','a is less than b':' કરતાં નાનું છે','a is less than or equal to b':' કરતાં નાનું અથવા તેની બરાબર છે','a is greater than b':' કરતાં મોટું છે','a is greater than or equal to b':' કરતાં મોટું અથવા તેની બરાબર છે'}.get(raw)
            if ending:flow(g,'',[' એ ','',ending],{1:''})
        elif raw=='6 less than l':flow(g,'',[' કરતાં 6 ઓછું'])
        elif raw=='6 subtracted from l':flow(g,'',[' માંથી 6 બાદ કરેલું'])
        elif raw=='3 less than 4 times q':flow(g,'4 ગુણ્યા ',[' કરતાં 3 ઓછું'])
        elif raw=='Translate "4 times q."':flow(g,'“4 ગુણ્યા ',['”ને બીજગણિતીય પદાવલીમાં ફેરવો.'])
        elif raw=='3 less than 4q':flow(g,'',[' કરતાં 3 ઓછું'])
        elif raw=='Substitute l for "the length."':flow(g,'“લંબાઈ” માટે ',[' મૂકો.'])
        elif raw=='Substitute q for the number of quarters.':flow(g,'ક્વાર્ટરની સંખ્યા માટે ',[' મૂકો.'])
        elif raw.startswith('a plus b the sum of a and b '):
            flow(g,'',[' વત્તા ','','\n',' અને ',' નો સરવાળો','\n',' માં ',' નો વધારો','\n',' જેટલો વધારો ધરાવતું ','','\n',' અને ',' નો કુલ સરવાળો','\n',' ઉમેરેલું હોય તેવું ',''])
        elif raw.startswith('a minus b the difference of a and b '):
            flow(g,'',[' ઓછા ','','\n',' અને ',' વચ્ચેનો તફાવત','\n',' માંથી ',' ઘટાડેલું','\n',' જેટલો ઘટાડો ધરાવતું ','','\n',' બાદ કરેલું હોય તેવું ',''])
        elif raw.startswith('a times b the product of a and b '):
            flow(g,'',[' ગુણ્યા ','','\n',' અને ',' નો ગુણાકાર','\n',' નું બમણું'])
        elif raw.startswith('a divided by b the quotient of a and b '):
            flow(g,'',[' ભાગ્યા ','','\n',' અને ',' નું ભાગફળ','\n',' અને ',' નો ગુણોત્તર','\n',' વડે ભાગેલું હોય તેવું ',''])
    # Phrase parsing explanations: retain the English keyword as such, not a
    # mistranslated duplicate of “of and and”.
    items=list(byid['fs-id1166424761248'])
    items[0][0].tail=' સરવાળાનું 5 ગણું કરવાનું હોવાથી સરવાળાની આસપાસ કૌંસ જોઈએ: '
    items[0][1].tail=' અને ';items[0][2].tail=', '
    items[0][3].tail=' આ કૌંસથી પહેલાં સરવાળો જ કરવો પડે છે. (ક્રિયાઓનો ક્રમ યાદ રાખો.)'
    items[1][0].tail=' સરવાળો ઓળખવા અંગ્રેજી શબ્દસમૂહમાં “of” અને “and” જોઈએ. અહીં સરવાળો '
    items[1][1].text='“of”';items[1][1].tail=' પછીના 5'
    items[1][2].tail=' અને ';items[1][3].tail=' નો છે.'
    item=list(byid['fs-id1166425197914'])[0]
    item[0].tail=' મુખ્ય શબ્દ ';item[1].text='difference (તફાવત)'
    item[1].tail=' છે, જે બતાવે છે કે ક્રિયા બાદબાકી છે. બાદ કરવાની સંખ્યાઓ શોધવા અંગ્રેજીમાં '
    item[2].text='“of”';item[2].tail=' અને ';item[3].text='“and”';item[3].tail=' શબ્દો જુઓ.'
    # Full Gujarati reading of comparison mtext rows. Operand tokens and their
    # order remain intact; the final mtext carries the Gujarati postposition.
    for s,g in zip(source.iter(),root.iter()):
        if s.tag!=f'{{{MATH}}}mtd':continue
        raw=''.join(s.itertext());sm=s.findall(f'{{{MATH}}}mtext');gm=g.findall(f'{{{MATH}}}mtext')
        comparison={'not equal to':' નીચે આપેલી સંખ્યાની બરાબર નથી: ','less than':' નીચે આપેલી સંખ્યા કરતાં નાનું છે: ','less than or equal to':' નીચે આપેલી સંખ્યા કરતાં નાનું અથવા તેની બરાબર છે: ','greater than':' નીચે આપેલી સંખ્યા કરતાં મોટું છે: ','greater than or equal to':' નીચે આપેલી સંખ્યા કરતાં મોટું અથવા તેની બરાબર છે: '}
        if len(sm)==2 and sm[0].text=='is' and sm[1].text in comparison:
            gm[0].text='';gm[1].text=comparison[sm[1].text]
        if 'is less than' in raw or 'is greater than' in raw:
            for x,y in zip(sm,gm):
                if x.text=='is read “':y.text=' ને “'
                elif x.text=='is read':y.text=' ને '
                elif x.text in {'is less than','is greater than'}:y.text=' એ '
                elif x.text=='”':y.text=(' કરતાં નાનું છે”' if 'is less than' in raw else ' કરતાં મોટું છે”')+' તરીકે વાંચીએ છીએ.'
        if 'is to the left of' in raw or 'is to the right of' in raw:
            for x,y in zip(sm,gm):
                if x.text in {'is to the left of','is to the right of'}:y.text=' એ સંખ્યારેખા પર '
                elif x.text=='on the number line':y.text=' ની ડાબી બાજુએ છે.' if 'is to the left of' in raw else ' ની જમણી બાજુએ છે.'
    for i in ['fs-id1170655224688','fs-id1170653192952','fs-id1170655041754','fs-id1170655111048']:
        alt=byid[i].get('alt','')
        alt=re.sub(r'(\d*)xના વર્ગ',r'\1x²',alt)
        alt=re.sub(r'(\d*)xનો વર્ગ',r'\1x²',alt)
        byid[i].set('alt',alt)
    errata=json.loads(Path(__file__).with_name('a10-m82453-errata.gu.json').read_text(encoding='utf8'))
    for i,entry in errata['entries'].items():
        if entry.get('alt_gu'):byid[i].set('alt',entry['alt_gu'])
        if entry.get('summary_gu'):byid[i].set('summary',entry['summary_gu'])
def slots(root):
    for e in root.iter():
        local=e.tag.rsplit('}',1)[-1]
        if local in {'content-id','uuid'}:continue
        for attr in ['text','tail']:
            value=getattr(e,attr)
            if value and re.search('[A-Za-z]',value) and not(e.tag.startswith('{'+MATH+'}')and attr=='text'and local!='mtext'):
                yield e,attr,value.strip()
        for attr in ['alt','summary','aria-label']:
            value=e.get(attr)
            if value and re.search('[A-Za-z]',value):yield e,'@'+attr,value.strip()
def main():
    assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SHA
    tree=ET.parse(SRC);root=tree.getroot();unique=list(dict.fromkeys(t for _,_,t in slots(root)))
    if MAP.exists():data=json.loads(MAP.read_text(encoding='utf8'))
    else:data={'source_sha256':SHA,'slots':[]}
    assert data['source_sha256']==SHA
    rows=data['slots'];assert[x['en']for x in rows]==unique[:len(rows)]
    for i in range(len(rows),len(unique)):rows.append({'n':i,'en':unique[i],'gu':None})
    authored={}
    if TSV.exists():
        for line in TSV.read_text(encoding='utf8').splitlines():
            if not line.strip():continue
            n,gu=line.split('\t',1);n=int(n);assert n not in authored;authored[n]=gu
    for row in rows:row['gu']=authored.get(row['n'])
    MAP.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    missing=[r['n']for r in rows if r['gu']is None]
    if missing:print('Source slots',len(rows),'authored',len(rows)-len(missing),'next',missing[0]);return
    trans={r['en']:r['gu']for r in rows}
    for e,attr,src in slots(root):
        value=trans[src]
        if attr.startswith('@'):e.set(attr[1:],value)
        else:
            old=getattr(e,attr);setattr(e,attr,old[:len(old)-len(old.lstrip())]+value+old[len(old.rstrip()):])
    polish(root,ET.parse(SRC).getroot())
    root.set('{http://www.w3.org/XML/1998/namespace}lang','gu-Gujr-IN')
    ET.register_namespace('',CNX);ET.register_namespace('m',MATH);ET.register_namespace('md','http://cnx.rice.edu/mdml')
    tree.write(OUT,encoding='utf-8',xml_declaration=True)
    originals=ET.parse(SRC).getroot();source_by_id={e.get('id'):e for e in originals.iter() if e.get('id')}
    language={'003_img_new.jpg','004_img_new.jpg','009a_img_new.jpg','010a_img_new.jpg','011a_img_new.jpg','012a_img_new.jpg','013a_img_new.jpg','014a_new.jpg','014b_new.jpg','014c_new.jpg','015_img_new.jpg','016_img_new.jpg','018_img_new.jpg','201_img_new.jpg'}
    inventory=[]
    for e in root.iter():
        if e.tag!=f'{{{CNX}}}media':continue
        path=next(iter(e)).get('src');name=Path(path).name;short=name.replace('CNX_ElemAlg_Figure_01_02_','')
        inventory.append({'source_media':e.get('id'),'source_src':path,'source_alt':source_by_id[e.get('id')].get('alt'),'gu_alt':e.get('alt'),'needs_localization':short in language,'image_review':'actual original visually inspected2026-08-31','integration_status':'Gujarati redraw prepared by figure worker' if short in language else 'mathematical-only original retained with Gujarati alternative'})
    report={'schema':'gujarati-media-inventory-v1','book':'A10','module':'m82453','source_sha256':SHA,'media_count':len(inventory),'language_bearing':sum(x['needs_localization']for x in inventory),'mathematical_only':sum(not x['needs_localization']for x in inventory),'items':inventory}
    (ROOT/'gu-Gujr-IN/reviews/a10-m82453-media-inventory.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Translated',len(rows),'slots; inventoried',len(inventory),'media')
if __name__=='__main__':main()
