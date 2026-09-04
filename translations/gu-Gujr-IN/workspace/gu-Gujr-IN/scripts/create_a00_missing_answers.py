"""Added worked answers for the29 m81243 exercises omitted by the source key."""
from fractions import Fraction
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
LANG=ROOT/'gu-Gujr-IN'
C='http://cnx.rice.edu/cnxml'
items=[]


def add(identifier,question,answer,steps,check):
    items.append({'source_exercise':identifier,'question_gu':question,'answer':answer,'steps':steps,'check':check})


for identifier,terms,counting,whole in [
    ('fs-id834824',['0','7/10','3','20.5','300'],[3,300],[0,3,300]),
    ('fs-id2134956',['0','3/5','10','303','422.6'],[10,303],[0,10,303])]:
    numbers=[Fraction(x) for x in terms]
    assert [int(n) for n in numbers if n.denominator==1 and n>0]==counting
    assert [int(n) for n in numbers if n.denominator==1 and n>=0]==whole
    a=', '.join(map(str,counting));b=', '.join(map(str,whole))
    add(identifier,', '.join(terms)+'માંથી (a) ગણતરીની સંખ્યાઓ અને (b) પૂર્ણ સંખ્યાઓ પસંદ કરો.',
        f'(a) {a}; (b) {b}',
        ['ગણતરીની સંખ્યાઓ 1થી શરૂ થાય છે અને આખા એકમોમાં આગળ વધે છે. તેથી અપૂર્ણાંક અને દશાંશ ભાગ ધરાવતી સંખ્યાઓ પસંદ ન કરો.',
         'યાદીમાં ગણતરીની સંખ્યાઓ છે: '+a+'.','પૂર્ણ સંખ્યાઓ માટે ગણતરીની સંખ્યાઓ સાથે 0નો સમાવેશ કરો: '+b+'.'],
        {'kind':'classification','terms':terms,'counting':counting,'whole':whole})

for identifier,h,t,o in [('fs-id2646862',3,8,4),('fs-id1339977',6,2,0)]:
    n=100*h+10*t+o
    add(identifier,f'ચિત્રમાં {h} સો, {t} દશક અને {o} એકમ છે. દર્શાવેલી સંખ્યા શોધો.',str(n),
        [f'{h} સો એટલે {h} × 100 = {100*h}.',f'{t} દશક એટલે {t} × 10 = {10*t}; એકમની કિંમત {o} છે.',
         f'આ કિંમતો ઉમેરો: {100*h} + {10*t} + {o} = {n}.'+(f' એકમના સ્થાને 0 રાખવો જરૂરી છે; {n} અને {n//10} જુદી સંખ્યાઓ છે.' if o==0 else '')],
        {'kind':'base10','parts':[h,t,o],'result':n})

for identifier,n,parts in [
    ('fs-id1522372',398127,[(9,10000,'દસ હજાર'),(3,100000,'સો હજાર'),(2,10,'દશક'),(8,1000,'હજાર'),(7,1,'એકમ')]),
    ('fs-id1350682',78320465,[(8,1000000,'મિલિયન'),(4,100,'સો'),(2,10000,'દસ હજાર'),(6,10,'દશક'),(7,10000000,'દસ મિલિયન')])]:
    steps=['જમણી બાજુથી એકમ, દશક, સો, હજાર અને આગળનાં સ્થાન ગણો. અંક અને તેની સ્થાનકિંમતને જુદાં ઓળખો.']
    answer=[]
    for index,(digit,place,name) in enumerate(parts):
        assert n//place%10==digit
        label='('+chr(97+index)+')'
        steps.append(f'{label} અંક {digit}નું સ્થાન {name} છે; તેની કિંમત {digit} × {place:,} = {digit*place:,} છે.')
        answer.append(label+' '+name)
    add(identifier,f'{n:,}માં જણાવેલા અંકોનાં સ્થાન શોધો: '+', '.join(str(p[0]) for p in parts)+'.',
        '; '.join(answer),steps,{'kind':'places','number':n,'parts':[{'digit':d,'place':p} for d,p,name in parts]})

NAME_CASES=[
    ('fs-id1190749',5902,'પાંચ હજાર, નવસો બે'),
    ('fs-id1822153',146023,'એકસો છેતાલીસ હજાર, તેવીસ'),
    ('fs-id1798411',1458398,'એક મિલિયન, ચારસો અઠ્ઠાવન હજાર, ત્રણસો અઠ્ઠાણું'),
    ('fs-id1166761301603',62008465,'બાસઠ મિલિયન, આઠ હજાર, ચારસો પાંસઠ'),
    ('fs-id3014390',12276,'બાર હજાર, બસો છોતેર'),
    ('fs-id1300121',525600,'પાંચસો પચ્ચીસ હજાર, છસો'),
    ('fs-id1386002',2718782,'બે મિલિયન, સાતસો અઢાર હજાર, સાતસો બ્યાસી'),
    ('fs-id1362934',20665415,'વીસ મિલિયન, છસો પાંસઠ હજાર, ચારસો પંદર'),
    ('fs-id1544452',1267401849,'એક બિલિયન, બસો સડસઠ મિલિયન, ચારસો એક હજાર, આઠસો ઓગણપચાસ'),
    ('fs-id2610406',18549,'અઢાર હજાર, પાંચસો ઓગણપચાસ ડૉલર')
]
for identifier,n,words in NAME_CASES:
    groups=f'{n:,}'.split(',')
    values=[int(g)*1000**(len(groups)-i-1) for i,g in enumerate(groups)]
    assert sum(values)==n
    money=identifier=='fs-id2610406'
    add(identifier,(f'સ્રોતમાં આપેલી ચેકની રકમ ${n:,} શબ્દોમાં લખો.' if money else f'સ્રોતમાં આપેલી સંખ્યા {n:,} શબ્દોમાં લખો.'),words,
        ['સ્રોતની આંતરરાષ્ટ્રીય પદ્ધતિ મુજબ જમણી બાજુથી ત્રણ-ત્રણ અંકોના ગાળા પાડો: '+' | '.join(groups)+'.',
         'દરેક ગાળાનું મૂલ્ય છે: '+' + '.join(f'{v:,}' for v in values)+f' = {n:,}.',
         'ડાબેથી દરેક ગાળાનું નામ વાંચો. શરૂઆતનાં શૂન્યો બોલવાના નથી, પરંતુ તેમનાં સ્થાન સાચવવાના છે.',
         'શબ્દોમાં: '+words+'.'],
        {'kind':'number_name','number':n,'group_values':values,'words':words})

for identifier,words,values in [
    ('fs-id1384471','બસો ત્રેપન',[200,53]),
    ('fs-id2760170','એકસઠ હજાર, ચારસો પંદર',[61000,415]),
    ('fs-id2353124','અઢાર મિલિયન, એકસો બે હજાર, સાતસો ત્ર્યાસી',[18000000,102000,783]),
    ('fs-id2241247','અગિયાર બિલિયન, ચારસો એકોતેર મિલિયન, છત્રીસ હજાર, એકસો છ',[11000000000,471000000,36000,106]),
    ('fs-id2926292','ચાર બિલિયન, પાંચસો અડસઠ મિલિયન',[4000000000,568000000]),
    ('fs-id1572155','ત્રણ ટ્રિલિયન, પાંચસો બિલિયન',[3000000000000,500000000000])]:
    n=sum(values)
    add(identifier,'સ્રોતનું શબ્દરૂપ અંકોમાં લખો: '+words+'.',f'{n:,}',
        ['દરેક શબ્દસમૂહનું સ્થાનમૂલ્ય અલગ લખો: '+' + '.join(f'{v:,}' for v in values)+'.',
         'આ મૂલ્યો ઉમેરતાં મળે છે: '+f'{n:,}.',
         'કોઈ ગાળો આપેલો ન હોય તો તેના સ્થાને ત્રણ શૂન્ય રાખો. બધા ગાળા જોડતાં મૂળ શબ્દરૂપ ફરી મળે છે.'],
        {'kind':'compose','parts':values,'result':n})


def rounded(identifier,values,places,unit=''):
    steps=[];answers=[];checks=[]
    for i,(n,place) in enumerate(zip(values,places)):
        low=(n//place)*place;high=low+place
        result=low if n-low<high-n else high
        letter='('+chr(97+i)+')'
        steps += [f'{letter} {n:,}ની બાજુનાં {place:,}ના ગુણિત {low:,} અને {high:,} છે.',
                  f'અંતર અનુક્રમે {n-low:,} અને {high-n:,} છે. '+('બીજું અંતર નાનું છે' if result==high and n-low!=high-n else 'પહેલું અંતર નાનું છે' if result==low else 'અંતર સરખું હોય ત્યારે ઉપરનું ગુણિત પસંદ કરીએ છીએ')+f'; પરિણામ {result:,}{unit}.']
        answers.append(f'{letter} {result:,}{unit}')
        checks.append({'number':n,'place':place,'result':result})
    question='આપેલી સંખ્યાઓને દર્શાવેલા સૌથી નજીકના ગુણિતમાં ફેરવો: '+'; '.join(f'{n:,} → {p:,}ના ગુણિત' for n,p in zip(values,places))+'.'
    add(identifier,question,'; '.join(answers),steps,{'kind':'rounding','cases':checks})


rounded('fs-id1621308',[792,5647],[10,10])
rounded('fs-id2240116',[28166,481628],[100,100])
rounded('fs-id1516723',[2391,2795],[1000,1000])
rounded('fs-id1372149',[163584,163246],[1000,1000])
rounded('fs-id1604312',[18549]*4,[10,100,1000,10000],' ડૉલર')
rounded('fs-id1806959',[149597888]*3,[100000000,10000000,1000000],' કિલોમીટર')

add('fs-id1258379','રોજિંદા જીવનમાં નજીકનું મૂલ્ય કાઢવું ક્યારે ઉપયોગી છે? એક ઉદાહરણ આપો.',
    'નમૂનાનો જવાબ: 47 છોડ હોય તો લગભગ50 છોડ કહીને બગીચાના કદનો ઝડપથી અંદાજ આપી શકાય.',
    ['ચોક્કસ ગણતરીમાં47 છે. સૌથી નજીકનાં દશકના ગુણિત40 અને50 છે.',
     '47થી40નું અંતર7 છે અને47થી50નું અંતર3 છે, તેથી50 નજીક છે.',
     'અંદાજ બતાવતા લગભગ શબ્દ વાપરો. ચોક્કસ રોપણી કે ગણતરી માટે મૂળ47 જ વાપરવું. જુદું યોગ્ય ઉદાહરણ પણ માન્ય છે.'],
    {'kind':'open_example','number':47,'place':10,'rounded':50})

source=ET.parse(ROOT/'downloads/gu-Gujr-IN/a00-id/provenance/logbook/authority/prealgebra2e/m81243.source.cnxml').getroot()
missing={e.get('id') for e in source.iter('{'+C+'}exercise') if e.find('{'+C+'}solution') is None}
assert len(items)==len(missing)==29
assert {i['source_exercise'] for i in items}==missing
assert all(len(i['steps'])>=2 for i in items)
result={'schema':'gujarati-worked-supplement-v1','book':'A00','module':'m81243','role':'source_omitted_answers',
        'source_faithful_xml_unchanged':True,'note_gu':'આ ઉમેરેલા ઉકેલો મૂળ સ્રોતમાં જવાબ ન આપેલા અભ્યાસો માટે છે. નામો અને ગાળાઓમાં મૂળની આંતરરાષ્ટ્રીય પદ્ધતિ જાળવી છે. ઐતિહાસિક વસ્તી, બજેટ અને અંતરના આંકડા મૂળનાં અભ્યાસો છે; તેઓને નવા વર્તમાન આંકડા તરીકે રજૂ કર્યાં નથી.',
        'items':items}
(LANG/'translations/a00-m81243-added-solutions.gu.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Added29 source-omitted answers with reasoning; complete missing-exercise ID coverage.')
