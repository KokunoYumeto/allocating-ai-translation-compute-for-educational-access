"""All59 source-omitted m81255 answers, separate from the faithful translation."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
LANG=ROOT/'gu-Gujr-IN'
SOURCE=ROOT/'downloads/gu-Gujr-IN/a00-id/provenance/logbook/authority/prealgebra2e/m81255.source.cnxml'
SHA='1717786daf25223f0712f505768442007c15cf449e382d5596414460d26bd4ba'
C='{http://cnx.rice.edu/cnxml}'
items=[]


def f(n):return f'{n:,}'


def add(ident,question,answer,steps,check,**extra):
    items.append(dict(source_exercise=ident,question_gu=question,answer=answer,steps=steps,check=check,**extra))


def parts(n):
    return [int(d)*10**i for i,d in reversed(list(enumerate(str(n)[::-1]))) if d!='0'] or [0]


def product_steps(a,b):
    if a==0 or b==0:
        return ['કોઈ પૂર્ણ સંખ્યાનો 0 વડે ગુણાકાર કરીએ તો ગુણનફળ 0 થાય છે.',f'{f(a)} × {f(b)} = 0.'],None
    if a==1 or b==1:
        return ['કોઈ સંખ્યાનો 1 વડે ગુણાકાર કરીએ તો તે જ સંખ્યા મળે છે.',f'{f(a)} × {f(b)} = {f(a*b)}.'],None
    ap,bp=parts(a),parts(b)
    steps=['સ્થાનકિંમત પ્રમાણે અવયવોને ભાગોમાં લખો. દરેક ભાગનું પૂરું મૂલ્ય રાખો; દશકને એકમ ગણશો નહીં.']
    if len(ap)>1:steps.append(f'{f(a)} = '+' + '.join(map(f,ap))+'.')
    if len(bp)>1:steps.append(f'{f(b)} = '+' + '.join(map(f,bp))+'.')
    steps.append('કોષ્ટકના દરેક ખાનામાં તેની હરોળ અને સ્તંભનાં મૂલ્યોનો ગુણાકાર છે. પછી દરેક હરોળનાં ગુણનફળ ઉમેરો.')
    cells=[[x*y for x in ap] for y in bp]
    for y,row in zip(bp,cells):
        expanded=(' + '.join(map(f,row))+' = ') if len(row)>1 else ''
        steps.append(f'{f(a)} × {f(y)} = '+expanded+f'{f(sum(row))}.')
    if len(cells)>1:steps.append('બધી હરોળનાં પરિણામો ઉમેરો: '+' + '.join(f(sum(row)) for row in cells)+f' = {f(a*b)}.')
    return steps,dict(caption_gu='સ્થાનકિંમતના ભાગોનો ગુણાકાર',corner_gu='×',row_headers=bp,column_headers=ap,cells=cells)


def product(ident,a,b,question=None,kind='multiply',prefix=None,unit=None):
    steps,table=product_steps(a,b)
    answer=f'{f(a)} × {f(b)} = {f(a*b)}'
    if unit:answer+=f'; એટલે {f(a*b)} {unit}.'
    if prefix:steps=prefix+steps
    if unit:steps.append(f'એકમ સાથે જવાબ: {f(a*b)} {unit}.')
    add(ident,question or f'ગુણાકાર કરો: {f(a)} × {f(b)}.',answer,steps,
        dict(kind=kind,operands=[a,b],result=a*b,unit_gu=unit),**({'answer_table':table} if table else {}))


for ident,a,b,aw,bw,notation in [
    ('fs-id1515495',8,6,'આઠ','છ','8 × 6'),
    ('fs-id2205542',3,9,'ત્રણ','નવ','3 · 9'),
    ('fs-id1858514',20,15,'વીસ','પંદર','(20)(15)'),
    ('fs-id2352928',39,64,'ઓગણચાલીસ','ચોસઠ','39(64)'),
]:
    add(ident,notation+'ને શબ્દોમાં લખો.',f'{aw} ગુણ્યા {bw}; અથવા {aw} અને {bw}નો ગુણાકાર.',
        [f'અહીં {a}ને “{aw}” અને {b}ને “{bw}” વાંચો.',
         '×, · અને સાથે લખેલા કૌંસ અહીં ગુણાકાર દર્શાવે છે.',
         'આ પ્રશ્ન શબ્દરૂપ માગે છે. માત્ર ગણતરીનું પરિણામ લખવાથી પૂછેલો જવાબ મળતો નથી.'],
        dict(kind='word_form',operands=[a,b],word_forms=[aw,bw]))

for ident,a,b in [('fs-id1259189',4,5),('fs-id2144780',3,9)]:
    add(ident,f'{a} × {b}ને મોડેલથી દર્શાવો.',f'{a} જૂથમાં દરેકમાં {b} એકમ; કુલ {a*b} એકમ.',
        [f'{a} સમાન જૂથ બનાવો. દરેક જૂથમાં {b} નાનાં ચોરસ મૂકો.',
         'દરેક જૂથને એક હરોળમાં ગોઠવો. નીચે દરેક ચોરસ અલગ ગણી શકાય છે.',
         'પુનરાવર્તિત સરવાળો: '+' + '.join([str(b)]*a)+f' = {a*b}.',f'એટલે {a} × {b} = {a*b}.'],
        dict(kind='equal_groups',operands=[a,b],result=a*b),equal_groups_model=dict(groups=a,each=b))

charts=json.loads((LANG/'translations/a00-m81255-media-and-errata.gu.json').read_text(encoding='utf-8'))['source_chart_accessible_data']
for ident,suffix in [('fs-id3323581','207'),('fs-id2160228','211'),('fs-id2909043','215'),('fs-id2650134','219')]:
    filename=f'CNX_BMath_Figure_01_04_{suffix}.jpg'
    chart=next(c for c in charts if c['image']==filename)
    rows,cols=chart['row_headers'],chart['column_headers']
    cells=[[r*c for c in cols] for r in rows]
    blanks=[(ri,ci) for ri,row in enumerate(chart['visible_cells']) for ci,v in enumerate(row) if v is None]
    ri,ci=blanks[0];a,b=rows[ri],cols[ci]
    add(ident,'મૂળ ગુણાકારના કોષ્ટકનાં ખાલી ખાનાં ભરો.','પૂર્ણ કોષ્ટક નીચે આપેલો છે. મૂળમાં આપેલાં મૂલ્યો યથાવત્ રાખ્યાં છે.',
        ['ખાનાની ડાબી બાજુનું હરોળનું મથાળું અને ઉપરનું સ્તંભનું મથાળું વાંચો. બંનેનો ગુણાકાર તે ખાનામાં લખો.',
         f'પહેલા ખાલી ખાનાનું ઉદાહરણ: {a} × {b} = {a*b}.',
         'એ જ રીતે દરેક ખાનું ભરો. કોઈ મથાળું 0 હોય તો ગુણનફળ 0 થાય છે.'],
        dict(kind='chart',source_image=filename,source_visible_cells=chart['visible_cells'],filled_blank_count=len(blanks)),
        answer_table=dict(caption_gu='પૂર્ણ ગુણાકારનું કોષ્ટક',corner_gu='×',row_headers=rows,column_headers=cols,cells=cells))

for ident,a,b in [
    ('fs-id4351414',0,41),('fs-id1374182',77,0),('fs-id1842421',1,34),('fs-id1841687',65,1),('fs-id1462758',1,189206),
    ('fs-id2835625',58,4),('fs-id2297073',638,5),('fs-id2452591',9143,3),('fs-id2262728',37,45),('fs-id1917065',89,56),('fs-id2433725',53,98),
    ('fs-id2200779',19,10),('fs-id2266376',100,25),('fs-id3242461',1000,46),('fs-id1631570',30,1000000),
    ('fs-id2202516',156,328),('fs-id2676863',472,855),('fs-id1755202',968,926),('fs-id2700386',103,497),('fs-id1569007',485,602),('fs-id1830010',3581,724),
    ('fs-id2211473',86,29),('fs-id2172279',77,801),('fs-id2691598',15382,1),
]:product(ident,a,b)

add('fs-id3429680','ગુણાકાર કરો: (a) 8 × 9 (b) 9 × 8.','(a) 72 (b) 72.',
    ['8 × 9 = 72 અને 9 × 8 = 72.','અવયવોનો ક્રમ બદલવાથી ગુણનફળ બદલાતું નથી. 8 હરોળમાં દરેકમાં 9 ચોરસ હોય તે ગોઠવણી ફેરવતાં 9 હરોળમાં દરેકમાં 8 ચોરસ મળે છે.'],
    dict(kind='commuted_pair',operands=[[8,9],[9,8]],results=[72,72]))

for ident,a,b,question,hint in [
    ('fs-id2138252',15,22,'15 અને 22નું ગુણનફળ','ગુણનફળ એટલે આપેલી સંખ્યાઓના ગુણાકારનું પરિણામ.'),
    ('fs-id1946678',48,71,'અડતાળીસ ગુણ્યા એકોતેર','અડતાળીસ = 48 અને એકોતેર = 71.'),
    ('fs-id2223544',2,589,'589નું બમણું','બમણું એટલે 2 વડે ગુણાકાર.'),
    ('fs-id1619642',10,255,'બસો પંચાવનના દસ ગણા','દસ ગણા એટલે 10 વડે ગુણાકાર; બસો પંચાવન = 255.'),
    ('fs-id1727670',2,140,'140નું બમણું','140ને બે વખત લો: 140 + 140 = 280.'),
    ('fs-id1339075',15,905,'15 અને 905નું ગુણનફળ','ગુણનફળ એટલે ગુણાકારનું પરિણામ; 905માં સો અને એકમનાં મૂલ્યો રાખો.'),
]:product(ident,a,b,question+' — ગણિતનાં ચિહ્નોમાં લખો અને સાદું રૂપ આપો.',kind='phrase_multiply',prefix=[hint])

for ident,a,b,op,question,steps in [
    ('fs-id4131872',341,285,'−','341 − 285નું સાદું રૂપ આપો.',['અહીં − છે, એટલે બાદબાકી કરો.','285માંથી 300 સુધી 15 ઉમેરાય છે અને 300માંથી 341 સુધી 41 ઉમેરાય છે.','15 + 41 = 56. તેથી 341 − 285 = 56.','તપાસ: 285 + 56 = 341.']),
    ('fs-id2710714',3816,8184,'+','3,816 + 8,184નું સાદું રૂપ આપો.',['અહીં + છે, એટલે સરવાળો કરો.','3,816 = 3,800 + 16 અને 8,184 = 8,100 + 84.','3,800 + 8,100 = 11,900 અને 16 + 84 = 100.','11,900 + 100 = 12,000.']),
    ('fs-id1730599',947,0,'+','947 + 0નું સાદું રૂપ આપો.',['કોઈ સંખ્યામાં 0 ઉમેરવાથી સંખ્યા બદલાતી નથી.','947 + 0 = 947.']),
    ('fs-id2658557',90,66,'−','90 અને 66નો તફાવત — ચિહ્નોમાં લખો અને સાદું રૂપ આપો.',['તફાવત માટે 90માંથી 66 બાદ કરો.','90 − 60 = 30; પછી 30 − 6 = 24.','તપાસ: 66 + 24 = 90.']),
    ('fs-id1299335',325,65,'+','325 કરતાં 65 વધારે — ચિહ્નોમાં લખો અને સાદું રૂપ આપો.',['વધારે એટલે 325માં 65 ઉમેરો.','325 + 60 = 385; પછી 385 + 5 = 390.']),
    ('fs-id2299298',99,45,'−','99માંથી 45 બાદ કરો — ચિહ્નોમાં લખો અને સાદું રૂપ આપો.',['જેમાંથી બાદ કરવાનું છે તે 99 પહેલાં લખો.','99 − 40 = 59; પછી 59 − 5 = 54.','તપાસ: 45 + 54 = 99.']),
    ('fs-id2638027',6308,724,'+','6,308 અને 724નો સરવાળો — ચિહ્નોમાં લખો અને સાદું રૂપ આપો.',['6,308માં 724 ઉમેરો.','6,308 + 700 = 7,008; 7,008 + 20 = 7,028; 7,028 + 4 = 7,032.']),
    ('fs-id2427912',925,388,'−','925 કરતાં 388 ઓછું — ચિહ્નોમાં લખો અને સાદું રૂપ આપો.',['925માંથી 388 બાદ કરો; શબ્દોના ક્રમ પરથી 388 − 925 લખશો નહીં.','925 − 300 = 625; 625 − 80 = 545; 545 − 8 = 537.','તપાસ: 388 + 537 = 925.']),
]:
    result=a+b if op=='+' else a-b
    add(ident,question,f'{f(a)} {op} {f(b)} = {f(result)}',steps,dict(kind='mixed_arithmetic',operands=[a,b],operator=op,result=result))

for ident,a,b,question,unit,hint in [
    ('fs-id2676338',6,4,'કનીશાએ રજાઈ માટે બટનનાં 6 કાર્ડ ખરીદ્યાં. દરેક કાર્ડ પર 4 બટન છે. કુલ કેટલાં બટન ખરીદ્યાં?','બટન','કાર્ડની સંખ્યા × દરેક કાર્ડ પરનાં બટન.'),
    ('fs-id1727753',8,24,'કેથરીને ફૂલની ક્યારી માટે ઇમ્પેશન્સની 8 ટ્રે ખરીદી. દરેક ટ્રેમાં 24 ફૂલ છે. કુલ કેટલાં ફૂલ ખરીદ્યાં?','ફૂલ','ટ્રેની સંખ્યા × દરેક ટ્રેમાંનાં ફૂલ.'),
    ('fs-id2472006',28,26,'ઍના સી. સ્કોટ પ્રાથમિક શાળામાં 28 વર્ગખંડ છે. દરેકમાં વિદ્યાર્થીઓનાં 26 ડેસ્ક છે. કુલ કેટલાં ડેસ્ક છે?','ડેસ્ક','વર્ગખંડની સંખ્યા × દરેક વર્ગખંડનાં ડેસ્ક.'),
    ('fs-id2805135',2,12,'હિરોકોને ટામેટાંના છોડ કરતાં બમણા લેટિસના છોડ જોઈએ છે. તે ટામેટાંના 12 છોડ ખરીદે તો લેટિસના કેટલા છોડ લે?','લેટિસના છોડ','બમણા એટલે 2 ગણા. ટામેટાં અને લેટિસના કુલ છોડની સંખ્યા પૂછેલી નથી.'),
    ('fs-id1857753',2,30,'ઍન્ડ્રિયાની બટાકાના સલાડની વાનગીમાં, પીરસવાની સંખ્યા બટાકાના પાઉન્ડની સંખ્યાથી બમણી થાય છે. 30 પાઉન્ડ બટાકામાંથી કેટલાં પીરસણ બને?','પીરસણ','દરેક પાઉન્ડ માટે 2 પીરસણ: 2 × 30. પાઉન્ડને કિલોગ્રામમાં બદલવાના નથી.'),
    ('fs-id1206189',3,18,'શૉન્ટેની જાજમ 3 ફૂટ પહોળી અને 18 ફૂટ લાંબી છે. તેનું ક્ષેત્રફળ કેટલું?','ચોરસ ફૂટ','લંબચોરસનું ક્ષેત્રફળ = પહોળાઈ × લંબાઈ. ક્ષેત્રફળનો એકમ ચોરસ ફૂટ છે.'),
    ('fs-id3323621',23,28,'જૂનનો શાકભાજીનો બગીચો લંબચોરસ છે. લંબાઈ 23 ફૂટ અને પહોળાઈ 28 ફૂટ છે. ક્ષેત્રફળ કેટલું?','ચોરસ ફૂટ','ક્ષેત્રફળ = લંબાઈ × પહોળાઈ. બાજુઓનો સરવાળો અહીં ક્ષેત્રફળ આપતો નથી.'),
    ('fs-id4337742',360,160,'મૂળ પુસ્તકના NCAA ફૂટબોલના ઉદાહરણમાં લંબચોરસ મેદાન 360 ફૂટ × 160 ફૂટ છે. તેનું ક્ષેત્રફળ કેટલું?','ચોરસ ફૂટ','આ મૂળ પુસ્તકમાં આપેલાં માપ છે; આજના નિયમોની પુષ્ટિ તરીકે રજૂ કરેલાં નથી. ક્ષેત્રફળ માટે બંને માપનો ગુણાકાર કરો.'),
    ('fs-id2743395',200,24,'કાર્લ્ટનના દરેક પગારમાં $200નો વધારો થયો. વર્ષમાં તેને 24 વખત પગાર મળે છે. વાર્ષિક પગાર કેટલો વધ્યો?','ડૉલર પ્રતિ વર્ષ','દરેક ચુકવણીનો વધારો × વર્ષમાં ચુકવણીની સંખ્યા. કુલ નવો પગાર આપેલો નથી; માત્ર વાર્ષિક વધારો શોધો.'),
]:product(ident,a,b,question,kind='story_multiply',prefix=[hint],unit=unit)

add('fs-id2160208','ગુણાકારની હકીકતો શીખવામાં તમે મોડેલનો કેવી રીતે ઉપયોગ કર્યો છે?',
    'નમૂનાનો જવાબ: 4 જૂથમાં દરેકમાં 3 ચોરસ મૂક્યા. 3 + 3 + 3 + 3 = 12 ગણીને 4 × 3 = 12 સમજાયું.',
    ['તમારે વાપરેલી વસ્તુઓ, જૂથો કે હરોળનું પોતાનું ઉદાહરણ આપો.',
     'દરેક જૂથમાં સમાન સંખ્યા કેવી રીતે દેખાય છે અને કુલ કેવી રીતે મળ્યું તે સમજાવો. યોગ્ય જુદા જવાબો પણ માન્ય છે.'],
    dict(kind='open_example',groups=4,each=3,result=12))

assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
source=ET.parse(SOURCE).getroot()
missing=[e.get('id') for e in source.iter(C+'exercise') if e.find(C+'solution') is None]
assert len(items)==len(missing)==59
assert {i['source_exercise'] for i in items}==set(missing)
items.sort(key=lambda i:missing.index(i['source_exercise']))
data=dict(schema='gujarati-worked-supplement-v1',book='A00',module='m81255',role='source_omitted_answers',source_faithful_xml_unchanged=True,source_sha256=SHA,
          note_gu='આ મૂળ પાઠથી અલગ પૂરકમાં જવાબ ન આપેલા 59 અભ્યાસોના ઉકેલો છે. શબ્દરૂપ, મોડેલ અને કોષ્ટક માગતા પ્રશ્નોમાં તે પણ આપ્યાં છે. ગુણાકારના પગલાં સ્થાનકિંમતનાં ભાગો અને તેમના ગુણનફળના સરવાળા વડે સમજાવ્યાં છે. મિશ્ર અભ્યાસમાં + અને − ચિહ્નો યથાવત્ છે. મૂળનાં માપ, ચલણ અને ઉદાહરણો જાળવ્યાં છે.',items=items)
(LANG/'translations/a00-m81255-added-solutions.gu.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Authored59 source-omitted multiplication answers with completed charts and equal-group models.')
