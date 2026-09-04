"""Separate worked answers for all135 source omissions, including chapter review/test."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
LANG=ROOT/'gu-Gujr-IN'
SOURCE=ROOT/'downloads/gu-Gujr-IN/a00-id/provenance/logbook/authority/prealgebra2e/m81256.source.cnxml'
SHA='73e8bf102d72a8c3891b1f9823c015f288ffcd2315cc452e68e4028429e93b40'
C='{http://cnx.rice.edu/cnxml}'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
source=ET.parse(SOURCE).getroot()
source_exercises={e.get('id'):e for e in source.iter(C+'exercise')}
missing=[e.get('id') for e in source.iter(C+'exercise') if e.find(C+'solution') is None]
assert len(missing)==135
items=[]


def f(n):return f'{n:,}'


def add(index,question,answer,steps,check,**extra):
    items.append(dict(source_exercise=missing[index-1],question_gu=question,answer=answer,steps=steps,check=check,**extra))


def division(index,n,d,question=None,prefix=None,unit=None,model=False):
    question=question or f'{f(n)} ÷ {f(d)} કરો અને ગુણાકારથી તપાસો.'
    steps=list(prefix or [])
    if d==0:
        steps += ['ભાજક 0 છે. 0 વડે ભાગાકાર વ્યાખ્યાયિત નથી.',
                  f'કોઈ પણ સંખ્યાનો 0 સાથે ગુણાકાર 0 થાય છે; તે {f(n)} થઈ શકતો નથી. એટલે ભાગફળ બતાવીને ગુણાકારથી તપાસ કરી શકાતી નથી.']
        add(index,question,'વ્યાખ્યાયિત નથી.',steps,dict(kind='undefined_division',operands=[n,d]))
        return
    q,r=divmod(n,d);trace=[];extra={}
    if model:
        steps += [f'{n} નાના ચોરસ લો. દરેક ચોરસ 1 એકમ છે. તેમને {d} સમાન જૂથમાં વહેંચો.',
                  f'નીચેની દરેક હરોળ એક જૂથ છે. {d} હરોળમાં દરેકમાં {q} ચોરસ આવે છે. તેથી દરેક જૂથમાં {q} એકમ મળે છે.']
        extra['equal_groups_model']=dict(groups=d,each=q)
    elif n==0:
        steps.append(f'0 વસ્તુને {d} સમાન જૂથમાં વહેંચતાં દરેક જૂથમાં 0 વસ્તુ આવે છે. ભાજક {d} શૂન્ય નથી.')
    elif d==1:
        steps.append(f'આખી {f(n)} વસ્તુઓ એક જ જૂથમાં રાખીએ, એટલે તે જૂથમાં {f(n)} વસ્તુઓ રહે છે.')
    elif n==d:
        steps.append(f'{f(n)} વસ્તુઓને {f(d)} સમાન જૂથમાં વહેંચતાં દરેક જૂથમાં 1 વસ્તુ આવે છે.')
    else:
        digits=str(n);start=0
        while start<len(digits)-1 and int(digits[:start+1])<d:start+=1
        partial=int(digits[:start+1]);remainder=0
        steps.append('ડાબેથી ભાગાકાર કરો. વચ્ચે ભાગફળનો અંક 0 આવે તો તેનું સ્થાન ખાલી છોડશો નહીં.')
        for pos in range(start,len(digits)):
            if pos==start:steps.append(f'ડાબેથી પહેલાં {pos+1} અંક લો: {f(partial)}.')
            else:
                partial=remainder*10+int(digits[pos])
                steps.append(f'બાકી {remainder}ની જમણે આગળનો અંક {digits[pos]} ઉતારો: {f(partial)}.')
            digit,remainder=divmod(partial,d);product=digit*d
            steps.append(f'ભાગફળના આ સ્થાનનો અંક {digit} છે: {f(d)} × {digit} = {f(product)}. બાદ કરો: {f(partial)} − {f(product)} = {remainder}.')
            trace.append(dict(position=pos,partial=partial,digit=digit,product=product,remainder=remainder))
    answer=f'ભાગફળ {f(q)}, શેષ {r}.' if r else f'{f(n)} ÷ {f(d)} = {f(q)}.'
    steps += [f'તપાસ: {f(d)} × {f(q)} + {r} = {f(n)}.',f'શેષની શરત પણ જુઓ: 0 ≤ {r} < {f(d)}.']
    if unit:
        assert r==0
        answer+=f' એટલે {f(q)} {unit}.'
        steps.append(f'પૂછેલી સંખ્યા એકમ સાથે લખો: {f(q)} {unit}.')
    add(index,question,answer,steps,dict(kind='division_model' if model else 'division',operands=[n,d],quotient=q,remainder=r,trace=trace,unit_gu=unit),**extra)


def arithmetic(index,operands,op,question=None,prefix=None,unit=None):
    a,b=operands[:2];steps=list(prefix or []);extra={}
    if question is None and 84<=index<=89:
        assert op=='−'
        question=f'{f(a)} − {f(b)}: બાદબાકી કરો અને સરવાળાથી તપાસો.'
    if op=='+':
        result=sum(operands)
        # Running totals expose every operation in multi-quantity stories.
        subtotal=a
        for value in operands[1:]:
            for place in reversed(range(len(str(value)))):
                part=(value//10**place)%10*10**place
                if part:
                    steps.append(f'{f(subtotal)} + {f(part)} = {f(subtotal+part)}.')
                    subtotal+=part
        if len(steps)<2:steps.append('0 ઉમેરવાથી સંખ્યા બદલાતી નથી.')
        steps.insert(0,'દરેક સંખ્યાને તેના સ્થાનનાં મૂલ્યોમાં જુઓ. ભાગો ઉમેરતાં તેમનું પૂરું મૂલ્ય રાખો.')
    elif op=='−':
        assert len(operands)==2 and a>=b
        result=a-b;subtotal=a
        steps.append('બાદ કરવાની સંખ્યાને સ્થાનકિંમતના ભાગોમાં વહેંચો. એક પછી એક ભાગ બાદ કરો.')
        for place in reversed(range(len(str(b)))):
            part=(b//10**place)%10*10**place
            if part:
                steps.append(f'{f(subtotal)} − {f(part)} = {f(subtotal-part)}.');subtotal-=part
        steps.append(f'સરવાળાથી તપાસ: {f(result)} + {f(b)} = {f(a)}.')
    elif op=='×':
        assert len(operands)==2
        result=a*b
        if 0 in operands:steps += ['0 વડે ગુણાકારનું પરિણામ 0 છે.',f'{f(a)} × {f(b)} = 0.']
        elif 1 in operands:steps += ['1 વડે ગુણાકારથી સંખ્યા બદલાતી નથી.',f'{f(a)} × {f(b)} = {f(result)}.']
        else:
            parts=lambda n:[(n//10**p)%10*10**p for p in reversed(range(len(str(n)))) if (n//10**p)%10]
            ap,bp=parts(a),parts(b)
            steps.append('અવયવોને સ્થાનકિંમતના ભાગોમાં લખો. દરેક ભાગનો બીજા અવયવના દરેક ભાગ સાથે ગુણાકાર કરો.')
            if (a,b)==(1000,8):steps.append('1,000નો દરેક જૂથ 1 હજારનો છે. આવા 8 જૂથ એટલે 8 હજાર, એટલે 8,000.')
            if len(ap)>1:steps.append(f'{f(a)} = '+' + '.join(map(f,ap))+'.')
            if len(bp)>1:steps.append(f'{f(b)} = '+' + '.join(map(f,bp))+'.')
            cells=[[x*y for x in ap] for y in bp]
            for y,row in zip(bp,cells):
                for x,product in zip(ap,row):steps.append(f'{f(x)} × {f(y)} = {f(product)}.')
            products=[v for row in cells for v in row]
            if len(products)>1:steps.append('બધાં ગુણનફળ ઉમેરો: '+' + '.join(map(f,products))+f' = {f(result)}.')
            if len(products)>1:extra['answer_table']=dict(caption_gu='સ્થાનકિંમતના ભાગોનો ગુણાકાર',corner_gu='×',row_headers=bp,column_headers=ap,cells=cells)
    else:raise ValueError(op)
    expression=f' {op} '.join(map(f,operands))
    answer=f'{expression} = {f(result)}.'
    if unit:answer+=f' એટલે {f(result)} {unit.rstrip(".")}.'
    add(index,question or f'{expression}નું સાદું રૂપ આપો.',answer,steps,
        dict(kind='arithmetic',operands=operands,operator=op,result=result,unit_gu=unit),**extra)


def words(index,a,b,aw,bw,op):
    phr={'÷':f'{aw} ભાગ્યા {bw}; એટલે {aw}ને {bw} વડે ભાગો.',
         '×':f'{aw} ગુણ્યા {bw}; એટલે {aw} અને {bw}નો ગુણાકાર.',
         '+':f'{aw} વત્તા {bw}; એટલે {aw} અને {bw}નો સરવાળો.',
         '−':f'{aw}માંથી {bw} બાદ કરો.'}[op]
    original=source_exercises[missing[index-1]].find('.//{http://www.w3.org/1998/Math/MathML}math')
    assert original is not None
    notation_text=''.join(original.itertext())
    if op=='×':
        notation_step='મધ્યબિંદુ અહીં ગુણાકાર દર્શાવે છે.' if '·' in notation_text else 'અહીં સાથે લખેલા કૌંસ ગુણાકાર દર્શાવે છે.'
    elif op=='÷':
        notation_step='મૂળ સંખ્યાઓનો ક્રમ જાળવો. લાંબા ભાગાકારની અંદરની સંખ્યાને બહારની સંખ્યા વડે ભાગવાની હોય છે.' if original.find('.//{http://www.w3.org/1998/Math/MathML}menclose') is not None else 'અપૂર્ણાંક રેખાની ઉપરની સંખ્યાને નીચેની સંખ્યા વડે ભાગો.' if original.find('.//{http://www.w3.org/1998/Math/MathML}mfrac') is not None else 'મૂળ ક્રમ જાળવો. / અથવા ÷ ચિહ્ન પહેલી સંખ્યાને બીજી વડે ભાગવાનું દર્શાવે છે.'
    else:notation_step=f'અહીં {op} ચિહ્ન મુજબ ક્રિયાનું શબ્દરૂપ લખો.'
    add(index,'નીચેનું મૂળ ગણિતીય લખાણ શબ્દોમાં લખો.',phr,
        [f'{f(a)}ને “{aw}” અને {f(b)}ને “{bw}” વાંચો.',
         notation_step,
         'આ પ્રશ્ન શબ્દરૂપ માગે છે; ફક્ત ગણતરીનું પરિણામ પૂરતું નથી.'],
        dict(kind='word_form',operands=[a,b],operator=op,word_forms=[aw,bw]),source_notation_mathml=ET.tostring(original,encoding='unicode'))


for row in [(1,56,7,'છપ્પન','સાત'),(2,42,6,'બેતાલીસ','છ'),(3,63,9,'ત્રેસઠ','નવ'),(4,72,8,'બોતેર','આઠ'),(108,42,7,'બેતાલીસ','સાત'),(109,48,6,'અડતાળીસ','છ')]:words(*row,'÷')
for i,n,d in [(5,10,5),(6,18,6),(7,15,3),(8,16,4),(110,12,3)]:division(i,n,d,f'{n} ÷ {d}નું મોડેલ બનાવો.',model=True)
for i,n,d in [(9,14,2),(10,30,3),(11,36,4),(12,35,5),(13,64,8),(14,42,7),(15,12,12),(16,37,37),(17,29,1),(18,17,1),(19,0,8),(20,9,0),(21,32,0),(22,0,16),(23,57,3),(24,78,6),(25,528,4),(26,861,7),(27,3776,8),(28,46855,5),(29,4806,3),(30,3208,4),(31,3624,6),(32,83256,8),(33,3741,7),(34,51492,9),(35,297277,4),(36,105609,2),(37,4933,21),(38,43725,75),(39,26145,415),(40,816243,462),(44,1104,23),(111,32,8),(112,26,26),(113,0,52),(114,355,5),(115,1519,31),(116,5166,42),(125,128,8),(128,26,0)]:division(i,n,d)
for i,n,d in [(45,64,16),(46,256,32),(117,572,52),(132,63,21)]:division(i,n,d,f'{n} અને {d}નું ભાગફળ — ચિહ્નોમાં લખો અને સાદું રૂપ આપો.',prefix=['ભાગફળ માટે પહેલી સંખ્યાને બીજી સંખ્યા વડે ભાગો.'])
for i,n,d,question,unit in [
    (47,42,3,'ઈવી પાસે 42 ઔંસ ક્રૅકર્સ છે. દરેક થેલીમાં 3 ઔંસ ભરે તો કેટલી થેલીઓ ભરાય?','થેલીઓ'),
    (48,152,8,'મેલિસા 152 ગુલાબમાંથી દરેકમાં 8 ગુલાબના કેટલા ગુલદસ્તા બનાવી શકે?','ગુલદસ્તા'),
    (49,54,2,'મૂળ પુસ્તકના ઉદાહરણમાં બ્રાયન રોજ 2 ફૂટ ડેન્ટલ ફ્લૉસ વાપરે છે. 54 ફૂટનું પૅકેટ કેટલા દિવસ ચાલે?','દિવસ'),
    (51,128,4,'આકી પાસે 128 ઔંસ માટી છે. દરેક કૂંડામાં 4 ઔંસ માટી ભરે તો કેટલાં કૂંડાં ભરાય?','કૂંડાં'),
    (118,128,4,'શાયલા 128 ઔંસ ફળના રસમાંથી 4 ઔંસના કેટલા કપ ભરી શકે?','કપ'),
    (134,84,12,'લાવેલ 84 કૅન્ડીને સમાન રીતે 12 ભેટની થેલીઓમાં વહેંચે તો દરેક થેલીમાં કેટલી કૅન્ડી મૂકવી?','કૅન્ડી પ્રતિ થેલી'),
]:division(i,n,d,question,prefix=['કુલ જથ્થાને આપેલી સમાન ભાગની સંખ્યા અથવા દરેક ભાગના જથ્થા વડે ભાગો.'],unit=unit)

arithmetic(41,[74,391],'×');arithmetic(42,[305,262],'−');arithmetic(43,[647,528],'+')
arithmetic(50,[71,53],'−','માયરા માતાના ઘરથી 53 માઇલ અને સાસુના ઘરથી 71 માઇલ દૂર રહે છે. સાસુના ઘરનું અંતર કેટલું વધારે છે?',unit='માઇલ')
arithmetic(52,[6,26,15,9],'+','એમિલીએ વ્યવસાયનાં 6, ઇતિહાસનાં 26, મનોવિજ્ઞાનનાં 15 અને ગણિતનાં 9 પાનાં વાંચ્યાં. કુલ કેટલાં પાનાં વાંચ્યાં?',unit='પાનાં')
arithmetic(53,[14,5],'×','ડેવની સ્કાઉટ ટુકડીના 14 છોકરામાંથી દરેકને 5 મેરિટ બૅજ મળ્યા. કુલ કેટલા બૅજ મળ્યા?',unit='બૅજ')
add(54,'એક થેલીનો ખોરાક લારાની બિલાડીને 25 દિવસ ચાલે છે. 365 દિવસ માટે કેટલી થેલીઓ જોઈએ?',
    '15 આખી થેલીઓ જોઈએ.',
    ['14 થેલીથી 25 × 14 = 350 દિવસનો ખોરાક મળે છે.','365 − 350 = 15 દિવસ હજી બાકી છે.','15 દિવસ માટે વધુ 1 થેલી લેવી પડે: 14 + 1 = 15.','તપાસ: 25 × 15 = 375 દિવસ. 350 < 365 ≤ 375 હોવાથી 14 થેલી ઓછી પડે અને 15 પૂરતી છે.'],
    dict(kind='ceiling_story',operands=[365,25],quotient=14,remainder=15,result=15))
add(55,'ઓસ્વાલ્ડોએ 300ને 8 વડે ભાગતાં ભાગફળ 37 અને શેષ 4 કહ્યાં. તેનો જવાબ કેવી રીતે તપાસશો?',
    'જવાબ સાચો છે: 8 × 37 + 4 = 300 અને 0 ≤ 4 < 8.',
    ['ભાજક અને ભાગફળનો ગુણાકાર કરો: 8 × 37 = 296.','શેષ ઉમેરો: 296 + 4 = 300. મૂળ ભાજ્ય મળ્યું.','શેષ 4 ઋણ નથી અને ભાજક 8 કરતાં નાનો છે. આ બીજી શરત પણ જરૂરી છે.'],
    dict(kind='check_remainder',operands=[300,8],quotient=37,remainder=4))
for i,values in [(56,[0,3,25]),(57,[0,1,75])]:
    add(i,', '.join(map(str,values))+'માંથી (a) ગણવાની સંખ્યાઓ અને (b) પૂર્ણ સંખ્યાઓ ઓળખો.',
        '(a) '+', '.join(map(str,values[1:]))+'; (b) '+', '.join(map(str,values))+'.',
        ['મૂળ પાઠમાં ગણવાની સંખ્યાઓ 1, 2, 3, …થી શરૂ થાય છે.','પૂર્ણ સંખ્યાઓમાં 0 અને બધી ગણવાની સંખ્યાઓ આવે છે. એટલે 0 ફક્ત બીજા સમૂહમાં આવે છે.'],
        dict(kind='classification',values=values,counting=values[1:],whole=values))
add(58,'104ને દશમાન ખંડોથી દર્શાવો અને સ્થાનકિંમત પ્રમાણે લખો.','104 = 1 × 100 + 0 × 10 + 4 × 1.',
    ['100 એકમનો 1 ચોરસ પાટિયો લો. તેના 10 હરોળ અને 10 સ્તંભમાં 100 નાના ચોરસ છે.','દશકની પટ્ટી નથી. 4 છૂટા એકમના ચોરસ લો.','સ્થાનકિંમત પ્રમાણે 100 + 0 + 4 = 104. દશકના સ્થાને 0 મૂકવાનું ભૂલશો નહીં.'],
    dict(kind='hundreds_model',value=104,hundreds=1,tens=0,ones=4),hundreds_model=dict(hundreds=1,tens=0,ones=4))
for i,n,digits,powers,names in [(59,12403295,[4,0,1,9,3],[5,4,7,1,3],['સો હજાર','દસ હજાર','દસ મિલિયન','દશક','હજાર']),(119,549362,[9,6,2,5],[3,1,0,5],['હજાર','દશક','એકમ','સો હજાર'])]:
    entries=[f'({chr(97+j)}) {d}: {name}નું સ્થાન; મૂલ્ય {f(d*10**p)}' for j,(d,p,name) in enumerate(zip(digits,powers,names))]
    add(i,f'{f(n)}માં આપેલા અંકો '+', '.join(map(str,digits))+'નાં સ્થાન અને મૂલ્ય શોધો.','; '.join(entries)+'.',
        ['જમણેથી એકમ, દશક, સો, હજાર, દસ હજાર, સો હજાર, મિલિયન, દસ મિલિયન એમ સ્થાનો ગણો.',
         'અંકનું મૂલ્ય = અંક × તે સ્થાનનું એકમમૂલ્ય. 0નું સ્થાન હોય છે, પણ તે સ્થાન પર તેનું મૂલ્ય 0 છે.']+entries,
        dict(kind='place_values',number=n,digits=digits,powers=powers,values=[d*10**p for d,p in zip(digits,powers)]))
for i,n,answer,groups in [(60,204614,'બસો ચાર હજાર છસો ચૌદ',[204000,614]),(61,31640976,'એકત્રીસ મિલિયન છસો ચાલીસ હજાર નવસો છોતેર',[31000000,640000,976])]:
    add(i,f'{f(n)}ને શબ્દોમાં લખો.',answer+'.',
        ['મૂળ પાઠની આંતરરાષ્ટ્રીય ગોઠવણી રાખો: જમણેથી ત્રણ-ત્રણ અંકનાં જૂથ વાંચો.',f'{f(n)} = '+' + '.join(map(f,groups))+'.','દરેક જૂથને તેના હજાર કે મિલિયનના નામ સાથે વાંચો. અહીં મિલિયન = 1,000,000.'],
        dict(kind='number_words',value=n,groups=groups,word_answer=answer))
for i,question,n,groups in [(62,'છસો બેને અંકોમાં લખો.',602,[600,2]),(63,'બે બિલિયન, ચારસો બાણું મિલિયન, સાતસો અગિયાર હજાર, બેને અંકોમાં લખો.',2492711002,[2000000000,492000000,711000,2])]:
    add(i,question,f(n)+'.',['સો, દશક અને એકમનાં સ્થાન જાળવો.' if i==62 else 'મૂળ પાઠની આંતરરાષ્ટ્રીય ગોઠવણી રાખો; બિલિયન = 1,000,000,000 અને મિલિયન = 1,000,000.',
        'કહેલા ભાગોનાં મૂલ્યો ઉમેરો: '+' + '.join(map(f,groups))+f' = {f(n)}.','ખાલી સ્થાન માટે 0 લખો જેથી બાકીના અંકોનું સ્થાન બદલાય નહીં.'],dict(kind='number_digits',value=n,groups=groups))
for i,n,place in [(64,648,10),(65,2734,10),(66,26849,100),(67,75992,100),(120,25849,100)]:
    lo=n//place*place;hi=lo+place;result=lo if n-lo<hi-n else hi
    add(i,f'{f(n)}ને નજીકના {"દશક" if place==10 else "સો"}માં ફેરવો.',f(result)+'.',
        [f'તે {f(lo)} અને {f(hi)} વચ્ચે છે.',f'નીચેનું અંતર: {f(n)} − {f(lo)} = {n-lo}. ઉપરનું અંતર: {f(hi)} − {f(n)} = {hi-n}.',f'નાનું અંતર ધરાવતી સંખ્યા {f(result)} છે. બરાબર મધ્યમાં હોય તો મૂળ પાઠ મુજબ મોટી સંખ્યા લો.'],
        dict(kind='round',value=n,place=place,lower=lo,upper=hi,result=result))
for row in [(68,25,18,'પચ્ચીસ','અઢાર','+'),(69,10085,3492,'દસ હજાર પંચ્યાસી','ત્રણ હજાર ચારસો બાણું','+'),(81,40,15,'ચાલીસ','પંદર','−'),(82,5724,2918,'પાંચ હજાર સાતસો ચોવીસ','બે હજાર નવસો અઢાર','−'),(93,6,14,'છ','ચૌદ','×'),(94,54,72,'ચોપન','બોતેર','×')]:words(*row)

def stage(label,tens,ones,role):return dict(label_gu=label,tens=tens,ones=ones,role=role)
add(70,'38 + 14નું મોડેલ બનાવો.','38 + 14 = 52.',
    ['38 માટે 3 દશક અને 8 એકમ લો. 14 માટે 1 દશક અને 4 એકમ લો.','ભેગાં કરતાં 4 દશક અને 12 એકમ થાય છે.','12 એકમમાંથી 10 એકમના બદલે 1 દશક લો: 5 દશક અને 2 એકમ મળે છે.','તેથી 50 + 2 = 52. જૂથ બદલ્યું, કુલ મૂલ્ય બદલાયું નથી.'],
    dict(kind='addition_model',operands=[38,14],result=52),base10_model=dict(stages=[stage('પહેલી સંખ્યા',3,8,'first'),stage('બીજી સંખ્યા',1,4,'second'),stage('ભેગાં કરેલા ખંડ',4,12,'combined'),stage('10 એકમને 1 દશકમાં બદલ્યા',5,2,'regrouped')]))
add(83,'41 − 29નું મોડેલ બનાવો.','41 − 29 = 12.',
    ['41 માટે 4 દશક અને 1 એકમ લો.','9 એકમ દૂર કરવા 1 દશકના બદલે 10 એકમ લો: હવે 3 દશક અને 11 એકમ છે; કુલ 41 જ રહે છે.','2 દશક અને 9 એકમ દૂર કરો. બાકી 1 દશક અને 2 એકમ રહે છે.','તપાસ: 12 + 29 = 41.'],
    dict(kind='subtraction_model',operands=[41,29],result=12),base10_model=dict(stages=[stage('શરૂઆત',4,1,'initial'),stage('1 દશકને 10 એકમથી બદલ્યો',3,11,'regrouped'),stage('આટલા ખંડ દૂર કરો',2,9,'removed'),stage('બાકી રહેલા ખંડ',1,2,'remaining')]))
for i,op,suffix in [(71,'+','224'),(96,'×','228')]:
    rows=list(range(6,10));cols=list(range(3,10));cells=[[(a+b if op=='+' else a*b) for b in cols] for a in rows]
    title='સરવાળાનું' if op=='+' else 'ગુણાકારનું'
    add(i,'મૂળ '+title.replace('નું','ના')+' કોષ્ટકનાં ખાલી ખાનાં ભરો.','પૂર્ણ કોષ્ટક નીચે આપેલું છે.',
        ['દરેક ખાનાની હરોળનું મથાળું ડાબેથી અને સ્તંભનું મથાળું ઉપરથી વાંચો.',f'ખૂણામાં {op} ચિહ્ન છે. તે પ્રમાણે ક્રિયા કરો: પ્રથમ ખાનું 6 {op} 3 = {cells[0][0]}.','બધાં 28 ખાલી ખાનાં એ જ રીતે ભરો. મૂળ પ્રશ્નનું કોષ્ટક ખાલી જ રાખ્યું છે.'],
        dict(kind='chart',operator=op,source_image=f'CNX_BMath_Figure_01_05_{suffix}_img.jpg',blank_count=28),
        answer_table=dict(caption_gu='પૂર્ણ '+title+' કોષ્ટક',corner_gu=op,row_headers=rows,column_headers=cols,cells=cells))
for i,pairs in [(72,[[0,480],[480,0]]),(73,[[23,18],[18,23]])]:
    add(i,'સરવાળા કરો: (a) '+' + '.join(map(str,pairs[0]))+'; (b) '+' + '.join(map(str,pairs[1]))+'.',
        f'(a) {sum(pairs[0])}; (b) {sum(pairs[1])}.',
        [f'{a} + {b} = {a+b}.' for a,b in pairs]+['સરવાળામાં સંખ્યાઓનો ક્રમ બદલવાથી સરવાળો બદલાતો નથી.'],dict(kind='addition_pair',operands=pairs,results=[sum(p) for p in pairs]))
for i,values,op in [(74,[63,29],'+'),(75,[375,591],'+'),(76,[5280,16324,9731],'+'),(84,[12,7],'−'),(85,[46,21],'−'),(86,[110,87],'−'),(87,[415,296],'−'),(88,[8355,3947],'−'),(89,[54925,35647],'−'),(97,[256,0],'×'),(98,[4789,1],'×'),(99,[25,6],'×'),(100,[48,76],'×'),(101,[1000,22],'×'),(102,[601,943],'×'),(103,[10538,22],'×'),(121,[65,42],'−'),(122,[1000,8],'×'),(123,[73,89],'+'),(124,[634,255],'+'),(126,[299,836],'+'),(127,[8528,704],'+'),(129,[4916,1538],'−'),(130,[52,983],'×')]:arithmetic(i,values,op)
for i,values,op,question in [(77,[11,8],'+','11માં 8નો વધારો'),(78,[15,50],'+','15 અને 50નો કુલ સરવાળો'),(90,[100,65],'−','એકસોમાંથી પાંસઠ બાદ કરો'),(91,[41,23],'−','એકતાલીસ કરતાં ત્રેવીસ ઓછા'),(104,[94,33],'×','ચોરાણું ગુણ્યા તેત્રીસ'),(105,[10,264],'×','બસો ચોસઠના દસ ગણા'),(131,[9,15],'×','9 અને 15નું ગુણનફળ'),(133,[32,29],'+','32 કરતાં 29 વધારે')]:
    arithmetic(i,values,op,question+' — ચિહ્નોમાં લખો અને સાદું રૂપ આપો.',prefix=['શબ્દોમાં કહેલી ક્રિયા કરો. “ઓછા” અને “માંથી બાદ”માં કઈ સંખ્યામાંથી બાદ કરવાનું છે તે પહેલાં નક્કી કરો.' if op=='−' else 'ગુણનફળ એટલે ગુણાકારનું પરિણામ.' if op=='×' else 'વધારો અને કુલ માટે સરવાળો કરો.'])
arithmetic(79,[4,12,1,8,5],'+','જૅક્સન સોમવારે 4, મંગળવારે 12, બુધવારે 1, ગુરુવારે 8 અને શુક્રવારે 5 માઇલ દોડ્યો. કુલ કેટલા માઇલ?',unit='માઇલ')
arithmetic(80,[5,12,13],'+','મૂળ ત્રિકોણની બાજુઓ 5, 12 અને 13 સે.મી. છે. તેની પરિમિતિ શોધો.',prefix=['પરિમિતિ એટલે આકૃતિની આખી સીમાની લંબાઈ. ત્રણે બાજુઓ ઉમેરો.'],unit='સે.મી.')
arithmetic(92,[2485,948],'−','લિનની ક્રૂઝનો ખર્ચ $2,485 છે અને તેણે $948 બચાવ્યા છે. હજી કેટલા ડૉલર બચાવવા પડે?',unit='ડૉલર')
add(95,'3 × 8નું મોડેલ બનાવો.','3 × 8 = 24.',
    ['3 સમાન જૂથ બનાવો. દરેક જૂથમાં 8 નાના ચોરસ મૂકો; દરેક ચોરસ 1 એકમ છે.','હરોળ પ્રમાણે ગણીને 8 + 8 + 8 = 24 મળે છે.'],
    dict(kind='multiplication_model',operands=[3,8],result=24),equal_groups_model=dict(groups=3,each=8))
arithmetic(106,[2,4],'×','રાતિકા 4 કપ ચોખા લે છે. પાણીના કપ ચોખાના કપ કરતાં બમણા જોઈએ તો કેટલા કપ પાણી જોઈએ?',prefix=['બમણા એટલે 2 ગણા. પાણી અને ચોખાના કુલ કપ પૂછ્યા નથી.'],unit='કપ પાણી')
arithmetic(107,[30,24],'×','લૂઇસની લંબચોરસ છત 30 ફૂટ × 24 ફૂટ છે. તેનું ક્ષેત્રફળ કેટલું?',prefix=['લંબચોરસનું ક્ષેત્રફળ = લંબાઈ × પહોળાઈ. ચોરસ એકમમાં જવાબ આપો.'],unit='ચોરસ ફૂટ')
arithmetic(135,[22,24],'×','ગ્રીનવિલ શાળાના દરેક વર્ગમાં 22 બાળકો છે. 24 વર્ગમાં કુલ કેટલાં બાળકો છે?',unit='બાળકો')
assert len(items)==135 and {i['source_exercise'] for i in items}==set(missing)
items.sort(key=lambda item:missing.index(item['source_exercise']))
data=dict(schema='gujarati-worked-supplement-v1',book='A00',module='m81256',role='source_omitted_answers',source_faithful_xml_unchanged=True,source_sha256=SHA,
          note_gu='આ મૂળ પાઠથી અલગ પૂરકમાં ભાગાકાર, પ્રકરણના પુનરાવર્તન અને પ્રકરણની અભ્યાસ કસોટીના જવાબ ન આપેલા તમામ 135 અભ્યાસોના ઉકેલો છે. ભાગાકારમાં ગુણાકારથી તપાસ અને શેષની શરત સાથે બતાવ્યાં છે. શબ્દરૂપ, મોડેલ, કોષ્ટક, સ્થાનકિંમત અને મિશ્ર ક્રિયાઓની મૂળ સૂચનાઓ જાળવી છે. મૂળના માપ, ચલણ અને આંતરરાષ્ટ્રીય સંખ્યાગોઠવણી બદલ્યાં નથી.',items=items)
(LANG/'translations/a00-m81256-added-solutions.gu.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Authored all135 source-omitted division/review/test answers.')
