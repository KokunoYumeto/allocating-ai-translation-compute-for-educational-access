"""All42 omitted subtraction answers, separate from the faithful source XML."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT/'gu-Gujr-IN'
SOURCE = ROOT/'downloads/gu-Gujr-IN/a00-id/provenance/logbook/authority/prealgebra2e/m81245.source.cnxml'
C = '{http://cnx.rice.edu/cnxml}'
items = []


def f(n):
    return f'{n:,}'


def add(ident, question, answer, steps, check, **extra):
    items.append(dict(source_exercise=ident, question_gu=question, answer=answer, steps=steps, check=check, **extra))


def subtract_steps(a, b):
    places = ['એકમ', 'દશક', 'સો', 'હજાર', 'દસ હજાર', 'સો હજાર']
    top = list(map(int, reversed(str(a))))
    bottom = list(map(int, reversed(str(b))))+[0]*(len(top)-len(str(b)))
    steps = ['એકમ નીચે એકમ, દશક નીચે દશક, એમ સમાન સ્થાનના અંકો એકબીજાની નીચે લખો. જમણી બાજુથી બાદબાકી શરૂ કરો.']
    transfers = []
    for i in range(len(top)):
        if top[i] < bottom[i]:
            j = i+1
            while top[j] == 0:
                j += 1
            steps.append(f'{places[i]}ના સ્થાને ઉપરનો અંક {top[i]}, નીચેના અંક {bottom[i]} કરતાં નાનો છે. ડાબે જ્યાં શૂન્ય કરતાં મોટો અંક મળે તે સ્થાનથી મૂલ્ય બદલીને લો.')
            for k in range(j, i, -1):
                before = top[:]
                top[k] -= 1
                top[k-1] += 10
                steps.append(f'{places[k]}ના સ્થાનેથી 1 લેતાં ત્યાં {top[k]} બાકી રહે છે. લીધેલા 1 {places[k]}ના બદલે 10 {places[k-1]} લો; {places[k-1]}ના સ્થાને હવે {top[k-1]} થાય છે.')
                transfers.append({'from_place': 10**k, 'before': before, 'after': top[:]})
        steps.append(f'{places[i]}ના સ્થાને: {top[i]} − {bottom[i]} = {top[i]-bottom[i]}. જવાબના આ સ્થાને {top[i]-bottom[i]} લખો.')
    steps.append(f'જવાબ ડાબેથી જમણે વાંચો: {f(a-b)}. ડાબે અગ્રશૂન્ય હોય તો તેને લખવાની જરૂર નથી.')
    steps.append(f'સરવાળાથી તપાસ: {f(a-b)} + {f(b)} = {f(a)}. મૂળ સંખ્યા મળી, તેથી બાદબાકી સાચી છે.')
    return steps, transfers


for ident, a, b, aw, bw in [
    ('fs-id1730448', 18, 16, 'અઢાર', 'સોળ'),
    ('fs-id1372720', 83, 64, 'ત્ર્યાસી', 'ચોસઠ'),
    ('fs-id4876753', 790, 525, 'સાતસો નેવું', 'પાંચસો પચ્ચીસ'),
]:
    add(ident, f'{a} − {b} ને શબ્દોમાં લખો.', f'{aw} ઓછા {bw}; અથવા {aw}માંથી {bw} બાદ કરો.',
        [f'{a}ને “{aw}” અને {b}ને “{bw}” વાંચો.',
         '− ચિહ્ન બાદબાકી દર્શાવે છે. પહેલી સંખ્યામાંથી બીજી સંખ્યા બાદ કરવાની છે; ક્રમ ઉલટાવશો નહીં.',
         'આ પ્રશ્નમાં શબ્દરૂપ પૂછ્યું છે, ગણતરીનો જવાબ નહીં.'],
        {'kind': 'words', 'operands': [a, b], 'word_forms': [aw, bw]})


def stage(label, tens, ones, role):
    return {'label_gu': label, 'tens': tens, 'ones': ones, 'role': role}


for ident, a, b in [('fs-id1328354', 8, 4), ('fs-id1961690', 7, 5), ('fs-id1522580', 19, 8),
                    ('fs-id2436539', 17, 9), ('fs-id1298412', 32, 11), ('fs-id1714624', 55, 36)]:
    tens, ones = divmod(a, 10)
    bt, bo = divmod(b, 10)
    stages = [stage('શરૂઆતનું મોડેલ', tens, ones, 'initial')]
    steps = [f'{a} માટે {tens} દશકની પટ્ટી અને {ones} એકમના ચોરસ લો.']
    if ones < bo:
        tens -= 1
        ones += 10
        stages.append(stage('1 દશકને 10 એકમથી બદલો', tens, ones, 'regrouped'))
        steps.append(f'{bo} એકમ દૂર કરવા પૂરતા છૂટા ચોરસ નથી. 1 દશકની પટ્ટીના બદલે 10 એકમના ચોરસ લો. હવે {tens} દશક અને {ones} એકમ છે; કુલ {a} જ રહે છે.')
    stages.append(stage('આટલા ખંડ દૂર કરો', bt, bo, 'removed'))
    stages.append(stage('બાકી રહેલા ખંડ', tens-bt, ones-bo, 'remaining'))
    steps += [f'{bt} દશકની પટ્ટી અને {bo} એકમના ચોરસ દૂર કરો.',
              f'બાકી {tens-bt} દશક અને {ones-bo} એકમ છે. {a} − {b} = {a-b}.',
              f'તપાસ: બાકી રહેલા અને દૂર કરેલા ખંડ ભેગા કરીએ તો {a-b} + {b} = {a} થાય.']
    add(ident, f'{a} − {b}નું મોડેલ બનાવો.', f'{a} − {b} = {a-b}', steps,
        {'kind': 'model', 'operands': [a, b], 'result': a-b}, base10_model={'stages': stages})


for ident, a, b in [
    ('fs-id2471849', 9, 3), ('fs-id1841800', 2, 0), ('fs-id2792515', 45, 21),
    ('fs-id2219134', 99, 47), ('fs-id1919629', 268, 106), ('fs-id2754481', 7775, 3251),
    ('fs-id1760864', 63, 59), ('fs-id1512473', 486, 257), ('fs-id1987704', 542, 288),
    ('fs-id1834531', 8153, 3978), ('fs-id1605974', 4245, 899), ('fs-id1393492', 35162, 7885),
]:
    steps, transfers = subtract_steps(a, b)
    add(ident, f'{f(a)} − {f(b)} બાદ કરો અને સરવાળાથી તપાસો.', f'{f(a)} − {f(b)} = {f(a-b)}', steps,
        {'kind': 'subtract_check', 'operands': [a, b], 'result': a-b, 'transfers': transfers})


for ident, question, a, b, hint in [
    ('fs-id1988183', '12 અને 8નો તફાવત', 12, 8, 'આ શબ્દસમૂહમાં પહેલી સંખ્યા 12માંથી બીજી 8 બાદ કરો.'),
    ('fs-id1806820', '18 અને 7નો તફાવત', 18, 7, 'પહેલી સંખ્યા 18માંથી બીજી 7 બાદ કરો.'),
    ('fs-id1988475', '9માંથી 8 બાદ કરો', 9, 8, 'જે સંખ્યામાંથી બાદ કરીએ તે 9 પહેલાં લખો; બાદ કરવાની સંખ્યા 8 પછી લખો.'),
    ('fs-id1377076', '81માંથી 59 બાદ કરો', 81, 59, 'શરૂઆતની સંખ્યા 81 છે; તેમાંથી 59 બાદ કરો.'),
    ('fs-id2579422', '37માં 24નો ઘટાડો', 37, 24, 'ઘટાડો એટલે 37માંથી 24 બાદ કરો.'),
    ('fs-id1739503', '75માં 49નો ઘટાડો', 75, 49, '75માંથી 49 બાદ કરો.'),
    ('fs-id1361076', '19 કરતાં 15 ઓછું', 19, 15, '19થી શરૂઆત કરો અને 15 ઓછા કરો; 15 − 19 લખશો નહીં.'),
    ('fs-id1701801', '62 કરતાં 47 ઓછું', 62, 47, '62થી શરૂઆત કરો અને 47 ઓછા કરો; શબ્દસમૂહનો અર્થ જોઈને ક્રમ નક્કી કરો.'),
    ('fs-id3400285', '36 કરતાં 28 ઓછું', 36, 28, '36માંથી 28 બાદ કરો.'),
    ('fs-id2319783', '1,000 અને 945નો તફાવત', 1000, 945, '1,000માંથી 945 બાદ કરો. શૂન્યોની વચ્ચે સ્થાનકિંમતનું મૂલ્ય બદલતાં દરેક પગલું નોંધો.'),
]:
    steps, transfers = subtract_steps(a, b)
    add(ident, question+' — ગણિતનાં ચિહ્નોમાં લખો અને સાદું રૂપ આપો.', f'{f(a)} − {f(b)} = {f(a-b)}',
        [hint, f'પદાવલી: {f(a)} − {f(b)}.']+steps,
        {'kind': 'phrase_subtract', 'operands': [a, b], 'result': a-b, 'transfers': transfers})


for ident, a, b in [('fs-id1717619', 91, 53), ('fs-id2196772', 305, 262), ('fs-id2279892', 2020, 1984)]:
    steps, transfers = subtract_steps(a, b)
    add(ident, f'{f(a)} − {f(b)}નું સાદું રૂપ આપો.', f'{f(a)} − {f(b)} = {f(a-b)}', steps,
        {'kind': 'subtract', 'operands': [a, b], 'result': a-b, 'transfers': transfers})

add('fs-id2660683', '647 + 528નું સાદું રૂપ આપો.', '647 + 528 = 1,175',
    ['ચિહ્ન + છે, તેથી અહીં સરવાળો કરવાનો છે. આ બાદબાકીના પાઠમાંનો મિશ્ર અભ્યાસ છે.',
     'એકમ: 7 + 8 = 15. 5 લખો અને 1 દશક આગળ લઈ જાઓ.',
     'દશક: 4 + 2 + 1 = 7. 7 લખો.', 'સો: 6 + 5 = 11. 1 સો લખો અને 1 હજાર આગળ લખો.',
     'ડાબેથી જમણે વાંચતાં 1,175 થાય છે.'],
    {'kind': 'mixed_addition', 'operands': [647, 528], 'result': 1175})
add('fs-id1842028', 'ત્રાણું કરતાં સાઠ વધારે — ગણિતનાં ચિહ્નોમાં લખો અને સાદું રૂપ આપો.', '93 + 60 = 153',
    ['ત્રાણું = 93 અને સાઠ = 60. “વધારે” એટલે અહીં 93માં 60 ઉમેરો.',
     'દશક: 90 + 60 = 150. પછી 3 એકમ ઉમેરો: 150 + 3 = 153.'],
    {'kind': 'word_addition', 'operands': [93, 60], 'result': 153})

for ident, question, a, b, unit, hint in [
    ('fs-id1057274', 'મૂળના ઉદાહરણમાં 1 જૂને ફીનિક્સનું મહત્તમ તાપમાન 97 ડિગ્રી અને લઘુત્તમ 73 ડિગ્રી છે. તફાવત કેટલો?', 97, 73, 'ડિગ્રી',
     'ઊંચા તાપમાનમાંથી નીચું તાપમાન બાદ કરો. તારીખનો 1 ગણતરીમાં ઉમેરવાનો નથી. આ મૂળ પુસ્તકનું ઉદાહરણ છે, આજનું હવામાન નહીં.'),
    ('fs-id1341997', 'શાળાના બેન્ડમાં 82 અને ઑર્કેસ્ટ્રામાં 46 વિદ્યાર્થીઓ છે. સંખ્યાનો તફાવત કેટલો?', 82, 46, 'વિદ્યાર્થી',
     'બેન્ડની સંખ્યામાંથી ઑર્કેસ્ટ્રાની સંખ્યા બાદ કરો; કેટલા વધુ વિદ્યાર્થીઓ છે તે મળે.'),
    ('fs-id2661110', 'ગાદલાના સેટની સામાન્ય કિંમત $1,600 અને વેચાણની ખાસ કિંમત $755 છે. કિંમતનો તફાવત કેટલો?', 1600, 755, 'ડૉલર',
     'સામાન્ય કિંમતમાંથી ખાસ વેચાણકિંમત બાદ કરો. બંને કિંમતો ડૉલરમાં જ રાખો.'),
    ('fs-id3227881', 'મેસનના ખાતામાં $1,125 હતા. તેણે $892 ખર્ચ્યા. કેટલા પૈસા બાકી?', 1125, 892, 'ડૉલર',
     'શરૂઆતની રકમમાંથી ખર્ચેલી રકમ બાદ કરો.'),
]:
    steps, transfers = subtract_steps(a, b)
    add(ident, question, f'{f(a-b)} {unit}.', [hint]+steps+[f'એકમ સાથે જવાબ: {f(a-b)} {unit}.'],
        {'kind': 'story_subtract', 'operands': [a, b], 'result': a-b, 'unit_gu': unit, 'transfers': transfers})

steps, transfers = subtract_steps(350, 275)
add('fs-id1835207', 'સારાને અભ્યાસક્રમમાં પાસ થવા 350 ગુણ જોઈએ. તેના પહેલા ચાર પરીક્ષાના ગુણ 75, 50, 70 અને 80 છે. હજી કેટલા ગુણ જોઈએ?', '75 ગુણ.',
    ['પહેલા મેળવેલા ગુણ ઉમેરો: 75 + 50 = 125; 125 + 70 = 195; 195 + 80 = 275.',
     'જરૂરી 350 ગુણમાંથી મળેલા 275 ગુણ બાદ કરો: 350 − 275 = 75.']+steps+['275 + 75 = 350. એટલે હજી 75 ગુણ જોઈએ.'],
    {'kind': 'two_step_story', 'target': 350, 'scores': [75, 50, 70, 80], 'result': 75, 'transfers': transfers})
add('fs-id1394772', 'સરવાળાની હકીકતો જાણવાથી બાદબાકી કરવામાં કેવી મદદ મળે?',
    'નમૂનાનો જવાબ: 5 + 4 = 9 જાણું છું, તેથી 9 − 5 = 4 અને 9 − 4 = 5 પણ જાણું છું.',
    ['સરવાળો અને બાદબાકી વિપરીત ક્રિયાઓ છે. સરવાળામાં કુલ અને એક ભાગ જાણીએ તો બાદબાકીથી બીજો ભાગ મળે.',
     'તમારું પોતાનું યોગ્ય ઉદાહરણ આપો. તે જ સંખ્યાઓથી સરવાળો કરીને બાદબાકીનો જવાબ તપાસો. યોગ્ય જુદા જવાબો પણ માન્ય છે.'],
    {'kind': 'open_example', 'part_a': 5, 'part_b': 4, 'total': 9})

source = ET.parse(SOURCE).getroot()
missing = [e.get('id') for e in source.iter(C+'exercise') if e.find(C+'solution') is None]
assert len(items) == len(missing) == 42
assert {i['source_exercise'] for i in items} == set(missing)
items.sort(key=lambda item: missing.index(item['source_exercise']))
data = {'schema': 'gujarati-worked-supplement-v1', 'book': 'A00', 'module': 'm81245', 'role': 'source_omitted_answers',
        'source_faithful_xml_unchanged': True, 'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'note_gu': 'આ મૂળ પાઠથી અલગ પૂરકમાં જવાબ ન આપેલા 42 અભ્યાસોના ઉકેલો છે. જ્યાં પ્રશ્ન શબ્દરૂપ, મોડેલ કે સરવાળાથી તપાસ માગે છે ત્યાં તે પણ આપ્યાં છે. મિશ્ર અભ્યાસના + અને − ચિહ્નો ધ્યાનથી વાંચો. મૂળનાં નાણાં, માપ અને ઐતિહાસિક ઉદાહરણો જાળવ્યાં છે.',
        'items': items}
(LANG/'translations/a00-m81245-added-solutions.gu.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
print('Authored42 source-omitted subtraction answers, with models and inverse checks.')
