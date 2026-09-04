"""Author all40 source-omitted addition answers as a separate Gujarati supplement."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT/'gu-Gujr-IN'
SOURCE = ROOT/'downloads/gu-Gujr-IN/a00-id/provenance/logbook/authority/prealgebra2e/m81244.source.cnxml'
MEDIA = ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'
C = '{http://cnx.rice.edu/cnxml}'
items = []


def add(ident, question, answer, steps, check, **extra):
    items.append(dict(source_exercise=ident, question_gu=question, answer=answer,
                      steps=steps, check=check, **extra))


def f(n):
    return f'{n:,}'


def column_steps(numbers):
    """Expose every column, including carries greater than1 in multi-addend sums."""
    names = ['એકમ', 'દશક', 'સો', 'હજાર', 'દસ હજાર', 'સો હજાર', 'મિલિયન']
    steps = ['એકમ નીચે એકમ, દશક નીચે દશક, એમ સમાન સ્થાનના અંકો એકબીજાની નીચે લખો. જમણી બાજુના એકમથી શરૂ કરો.']
    carry = 0
    width = len(str(max(numbers)))
    for p in range(width):
        digits = [(n//(10**p)) % 10 for n in numbers]
        terms = digits + ([carry] if carry else [])
        total = sum(terms)
        expression = ' + '.join(map(str, terms))
        incoming = f' અગાઉના સ્થાનથી આવેલો {carry} પણ ઉમેરો.' if carry else ''
        outgoing, digit = divmod(total, 10)
        explanation = f'{names[p]}ના સ્થાને:{incoming} {expression} = {total}. '
        if outgoing:
            explanation += f'આ સ્થાને {digit} લખો અને આગળના {names[p+1]}ના સ્થાને {outgoing} લઈ જાઓ.'
        else:
            explanation += f'આ સ્થાને {digit} લખો.'
        steps.append(explanation)
        carry = outgoing
    if carry:
        steps.append(f'છેલ્લે આગળના {names[width]}ના સ્થાને બાકી રહેલો {carry} લખો.')
    steps.append('ડાબેથી જમણે જવાબ વાંચો: '+f(sum(numbers))+'.')
    return steps


# These first three tasks ask for words, not evaluation. Their source siblings
# explicitly answer with two equivalent phrases. Preserve that instructional aim.
for ident, a, b, aw, bw in [
    ('fs-id2169300', 6, 3, 'છ', 'ત્રણ'),
    ('fs-id2267610', 15, 16, 'પંદર', 'સોળ'),
    ('fs-id2459088', 438, 113, 'ચારસો આડત્રીસ', 'એકસો તેર'),
]:
    add(ident, f'{a} + {b} ને શબ્દોમાં લખો.',
        f'{aw} વત્તા {bw}; અથવા {aw} અને {bw}નો સરવાળો.',
        [f'પ્રથમ સંખ્યા {a}ને “{aw}” વાંચો. + ચિહ્ન “વત્તા” અથવા “સરવાળો” સૂચવે છે.',
         f'બીજી સંખ્યા {b}ને “{bw}” વાંચો. બંને શબ્દરૂપોને વત્તા વડે જોડો.',
         'અહીં પદાવલીને શબ્દોમાં લખવાની છે; તેનું મૂલ્ય ગણવાનું પૂછ્યું નથી.'],
        {'kind': 'words', 'addends': [a, b], 'word_forms': [aw, bw]})


def stage(label, tens, ones):
    return {'label_gu': label, 'tens': tens, 'ones': ones}


for ident, a, b, stages, reasoning in [
    ('fs-id2210891', 5, 3,
     [stage('પ્રથમ સમૂહ', 0, 5), stage('બીજો સમૂહ', 0, 3), stage('બંને સમૂહ ભેગા', 0, 8)],
     ['5 એકમના ચોરસ અને બીજા 3 એકમના ચોરસ લો.', 'બધા ચોરસ ભેગા કરીને ગણો: 8 એકમ થાય છે.']),
    ('fs-id1389381', 5, 9,
     [stage('પ્રથમ સમૂહ', 0, 5), stage('બીજો સમૂહ', 0, 9), stage('બંને સમૂહ ભેગા', 0, 14), stage('10 એકમને 1 દશકથી બદલો', 1, 4)],
     ['5 અને 9 એકમના ચોરસ ભેગા કરો; 14 એકમ થાય છે.',
      'તેમાંથી 10 એકમના બદલે 1 દશકની પટ્ટી લો. હવે 1 દશક અને 4 એકમ છે; કુલ સંખ્યા બદલાતી નથી.', '10 + 4 = 14.']),
    ('fs-id1509761', 15, 63,
     [stage('15નું મોડેલ', 1, 5), stage('63નું મોડેલ', 6, 3), stage('બંને મોડેલ ભેગાં', 7, 8)],
     ['15 માટે 1 દશક અને 5 એકમ લો. 63 માટે 6 દશક અને 3 એકમ લો.',
      'દશકની પટ્ટીઓ ભેગી કરતાં 1 + 6 = 7 દશક થાય. એકમના ચોરસ ભેગા કરતાં 5 + 3 = 8 એકમ થાય.', '70 + 8 = 78.']),
    ('fs-id1209935', 14, 27,
     [stage('14નું મોડેલ', 1, 4), stage('27નું મોડેલ', 2, 7), stage('બંને મોડેલ ભેગાં', 3, 11), stage('10 એકમને 1 દશકથી બદલો', 4, 1)],
     ['14 માટે 1 દશક અને 4 એકમ લો. 27 માટે 2 દશક અને 7 એકમ લો.',
      'ભેગા કરતાં 3 દશક અને 11 એકમ થાય. 11માંથી 10 એકમના બદલે 1 દશકની પટ્ટી લો.',
      'હવે 4 દશક અને 1 એકમ છે. 40 + 1 = 41.']),
]:
    add(ident, f'{a} + {b}નું મોડેલ બનાવો.', f'{a} + {b} = {a+b}', reasoning,
        {'kind': 'model', 'addends': [a, b], 'result': a+b}, base10_model={'stages': stages})


for ident, filename, rows, columns in [
    ('fs-id1485179', 'CNX_BMath_Figure_01_02_218.jpg', list(range(10)), list(range(10))),
    ('fs-id1516426', 'CNX_BMath_Figure_01_02_222.jpg', list(range(3, 10)), list(range(6, 10))),
    ('fs-id2220307', 'CNX_BMath_Figure_01_02_226.jpg', list(range(6, 10)), list(range(6, 10))),
]:
    a, b = rows[0], columns[0]
    add(ident, 'આપેલા સરવાળાના કોષ્ટકનાં ખાલી ખાનાં ભરો.',
        'પૂર્ણ કોષ્ટક નીચે આપ્યું છે. દરેક ખાનું તેની પંક્તિની સંખ્યા અને સ્તંભની સંખ્યાનો સરવાળો છે.',
        ['ડાબે આપેલી પંક્તિની સંખ્યા અને ઉપર આપેલી સ્તંભની સંખ્યા પસંદ કરો.',
         f'જ્યાં તે પંક્તિ અને સ્તંભ મળે ત્યાં તેમનો સરવાળો લખો. ઉદાહરણ: {a} + {b} = {a+b}.',
         'આ જ રીતે બાકીનાં ખાલી ખાનાં ભરો; મૂળમાં પહેલેથી ભરેલાં ખાનાં પણ પૂર્ણ કોષ્ટક સાથે સરખાવો.'],
        {'kind': 'grid', 'source_image': filename, 'source_image_sha256': hashlib.sha256((MEDIA/filename).read_bytes()).hexdigest()},
        answer_table={'caption_gu': 'પૂર્ણ સરવાળાનું કોષ્ટક', 'corner_gu': '+',
                      'row_headers': rows, 'column_headers': columns,
                      'cells': [[r+c for c in columns] for r in rows]})

add('fs-id2670104', '(a) 0 + 5,280 અને (b) 5,280 + 0 નો સરવાળો કરો.',
    '(a) 5,280; (b) 5,280.',
    ['કોઈ સંખ્યામાં 0 ઉમેરવાથી કંઈ વધતું નથી; સંખ્યા એ જ રહે છે.',
     '(a) 0 + 5,280 = 5,280. (b) 5,280 + 0 = 5,280. બંનેમાં શૂન્ય ઉમેરવાનો ગુણધર્મ લાગુ પડે છે.'],
    {'kind': 'two_sums', 'addends': [[0, 5280], [5280, 0]], 'results': [5280, 5280]})
add('fs-id2700265', '(a) 7 + 5 અને (b) 5 + 7 નો સરવાળો કરો.',
    '(a) 12; (b) 12.',
    ['(a) 7માં 3 ઉમેરતાં 10 થાય. 5માંથી બાકીના 2 ઉમેરતાં 12 થાય.',
     '(b) 5 + 7 = 12. સરવાળામાં સંખ્યાઓનો ક્રમ બદલવાથી જવાબ બદલાતો નથી.'],
    {'kind': 'two_sums', 'addends': [[7, 5], [5, 7]], 'results': [12, 12]})

for ident, numbers in [
    ('fs-id1785992', [37, 22]), ('fs-id2209807', [43, 53]),
    ('fs-id1184179', [38, 17]), ('fs-id1806818', [92, 39]),
    ('fs-id2602850', [247, 149]), ('fs-id2269768', [175, 648]),
    ('fs-id2202157', [775, 369]), ('fs-id1808456', [9184, 578]),
    ('fs-id1205572', [6118, 15990]), ('fs-id1542190', [368911, 857289]),
    ('fs-id1352693', [28925, 817, 4593]), ('fs-id1523165', [6291, 54107, 28635]),
]:
    expression = ' + '.join(map(f, numbers))
    add(ident, expression+'નો સરવાળો કરો.', expression+' = '+f(sum(numbers)),
        column_steps(numbers), {'kind': 'sum', 'addends': numbers, 'result': sum(numbers)})

for ident, question, numbers, hint in [
    ('fs-id1233172', '12 અને 19નો સરવાળો', [12, 19], '“સરવાળો” માટે + વાપરો.'),
    ('fs-id1834317', '70 અને 38નો સરવાળો', [70, 38], '“સરવાળો” માટે + વાપરો.'),
    ('fs-id1529453', '68માં 25નો વધારો', [68, 25], '“વધારો” માટે 68માં 25 ઉમેરો.'),
    ('fs-id2671623', '286 કરતાં 115 વધારે', [286, 115], 'શરૂઆતની સંખ્યા 286 છે; તેમાં 115 ઉમેરો.'),
    ('fs-id1614332', '593 અને 79નું કુલ', [593, 79], '“કુલ” માટે બંને સંખ્યાઓ ઉમેરો.'),
    ('fs-id1159676', '682માં 2,719 ઉમેરેલા', [682, 2719], '682માં 2,719 ઉમેરો. શબ્દક્રમનો અર્થ સમજીને પદાવલી લખો.'),
]:
    expression = ' + '.join(map(f, numbers))
    add(ident, question+' — ગણિતનાં ચિહ્નોમાં લખો અને સાદું રૂપ આપો.',
        expression+' = '+f(sum(numbers)), [hint, 'પદાવલી: '+expression+'.']+column_steps(numbers),
        {'kind': 'phrase_sum', 'addends': numbers, 'result': sum(numbers)})

for ident, question, numbers, unit, opening in [
    ('fs-id2452678', 'એઇડનના બેટની કિંમત $299, હેલ્મેટની $35 અને ગ્લવની $68 છે. કુલ કિંમત કેટલી?',
     [299, 35, 68], 'ડૉલર', 'ત્રણે સાધનોની કિંમત ઉમેરો. બધી કિંમતો ડૉલરમાં છે; રૂપિયામાં ફેરવવાની નથી.'),
    ('fs-id1401775', 'ક્લોઇએ સોમવારે 19, મંગળવારે 12, બુધવારે 23, ગુરુવારે 29 અને શુક્રવારે 44 ફૂલસજાવટ બનાવી. કુલ કેટલી?',
     [19, 12, 23, 29, 44], 'ફૂલસજાવટ', 'આ પાંચ દિવસની ફૂલસજાવટની સંખ્યાઓ ઉમેરો.'),
    ('fs-id1946723', 'સાત પુરુષોનાં વજન 175, 192, 148, 169, 205, 181 અને 225 પાઉન્ડ છે. તેમનું કુલ વજન કેટલું?',
     [175, 192, 148, 169, 205, 181, 225], 'પાઉન્ડ', 'સાતેય વજન પાઉન્ડમાં છે; દરેક વજન એક જ વાર ઉમેરો.'),
    ('fs-id1410524', 'એમાએ વેચેલાં ત્રણ ઘરની કિંમતો $292,540, $505,875 અને $423,699 છે. ત્રણેય વેચાણકિંમતનું કુલ કેટલું?',
     [292540, 505875, 423699], 'ડૉલર', 'ત્રણેય વેચાણકિંમત ઉમેરો. આ કિંમતનું કુલ છે; કમિશન કે નફો પૂછ્યો નથી.'),
    ('fs-id1215287', 'ફ્રેડના સેન્ડવિચમાં 420, ફ્રાઇઝમાં 230 અને 12 ઔંસના શેકમાં 580 કૅલરી છે. ભોજનની કુલ કૅલરી કેટલી?',
     [420, 230, 580], 'કૅલરી', 'ફક્ત કૅલરીની સંખ્યાઓ ઉમેરો. 12 ઔંસ પીણાનું માપ છે, કૅલરી નથી; તેને સરવાળામાં ઉમેરશો નહીં.'),
]:
    expression = ' + '.join(map(f, numbers))
    add(ident, question, f'{f(sum(numbers))} {unit}.',
        [opening, expression+' = '+f(sum(numbers))+'.']+column_steps(numbers)+[f'પ્રશ્નના એકમ સાથે જવાબ લખો: {f(sum(numbers))} {unit}.'],
        {'kind': 'story_sum', 'addends': numbers, 'result': sum(numbers), 'unit_gu': unit})

for ident, filename, sides, unit, explanation in [
    ('fs-id2130628', 'CNX_BMath_Figure_01_02_209_img.jpg', [12, 5, 13], 'સેમી',
     'ત્રિકોણની ત્રણેય બાજુઓ 12, 5 અને 13 સેમી છે. પરિમિતિ માટે ત્રણેય બાજુઓની લંબાઈ ઉમેરો.'),
    ('fs-id2173206', 'CNX_BMath_Figure_01_02_211_img.jpg', [19, 14, 19, 14], 'ફૂટ',
     'લંબચોરસમાં 19 ફૂટની બે અને 14 ફૂટની બે બાજુઓ છે. ફક્ત બે જુદી લંબાઈ નહીં, ચારેય બાજુઓ ઉમેરો.'),
    ('fs-id1321391', 'CNX_BMath_Figure_01_02_213_img.jpg', [24, 17, 29, 17], 'મીટર',
     'બહારની ચારેય બાજુઓ 24, 17, 29 અને 17 મીટર છે. બંને ત્રાંસી બાજુઓ ગણવી જરૂરી છે.'),
    ('fs-id1960065', 'CNX_BMath_Figure_01_02_215_img.jpg', [25, 10, 14, 7, 11, 3], 'ઇંચ',
     'બહારની છ બાજુઓ ફરતે ચાલીને બધાની લંબાઈ ઉમેરવાની છે. નાની ડાબી ઊભી બાજુનું માપ ચિત્રમાં આપેલું નથી.'),
]:
    steps = [explanation]
    if ident == 'fs-id1960065':
        steps += ['જમણી આખી ઊંચાઈ 10 ઇંચ છે. ડાબે નાની ઊભી બાજુ અને અંદરની 7 ઇંચની ઊભી બાજુ મળીને એટલી જ ઊંચાઈ આપે છે.',
                  'નાની બાજુ = 10 − 7 = 3 ઇંચ. આ માપ અહીં ગણ્યું છે; મૂળ ચિત્રમાં લખેલું માપ નથી.',
                  'આડી લંબાઈ પણ મેળ ખાતી હોવી જોઈએ: 11 + 14 = 25 ઇંચ.']
    steps += ['પરિમિતિ = '+' + '.join(map(str, sides))+' = '+str(sum(sides))+f' {unit}.',
              'પરિમિતિ લંબાઈ છે; જવાબમાં ચોરસ એકમ વાપરશો નહીં.']
    add(ident, 'આપેલી આકૃતિની પરિમિતિ શોધો.', f'{sum(sides)} {unit}.', steps,
        {'kind': 'perimeter', 'source_image': filename, 'source_image_sha256': hashlib.sha256((MEDIA/filename).read_bytes()).hexdigest(),
         'sides': sides, 'result': sum(sides), 'unit_gu': unit})

add('fs-id1827602', 'સરવાળો શીખવા તમે મોડેલનો ઉપયોગ કેવી રીતે કર્યો છે?',
    'નમૂનાનો જવાબ: મેં 5 અને 9 એકમના ચોરસ ભેગા કર્યા. 10 ચોરસને 1 દશકની પટ્ટીથી બદલતાં 1 દશક અને 4 એકમ મળ્યા. તેથી 5 + 9 = 14 સમજાયું.',
    ['તમે વાપરેલું મોડેલ જણાવો: વસ્તુઓ, એકમના ચોરસ, દશકની પટ્ટી કે સંખ્યારેખા.',
     'ચોક્કસ સરવાળામાં મોડેલે કેવી મદદ કરી તે સમજાવો. આ વ્યક્તિગત અનુભવનો પ્રશ્ન છે; યોગ્ય જુદા જવાબો પણ માન્ય છે.'],
    {'kind': 'open_example', 'addends': [5, 9], 'result': 14})

source = ET.parse(SOURCE).getroot()
missing = [e.get('id') for e in source.iter(C+'exercise') if e.find(C+'solution') is None]
assert len(items) == len(missing) == 40
assert {i['source_exercise'] for i in items} == set(missing)
items.sort(key=lambda i: missing.index(i['source_exercise']))
output = {'schema': 'gujarati-worked-supplement-v1', 'book': 'A00', 'module': 'm81244',
          'role': 'source_omitted_answers', 'source_faithful_xml_unchanged': True,
          'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'note_gu': 'આ પૂરકમાં મૂળ સ્રોતે જવાબ ન આપેલા 40 અભ્યાસોના ઉકેલો છે. પ્રશ્ન જ્યાં શબ્દરૂપ કે મોડેલ માગે છે ત્યાં તે જ પ્રકારનો જવાબ આપ્યો છે. નાણાં, માપ અને સંખ્યાલેખન મૂળ પ્રમાણે રાખ્યાં છે. ચિત્રમાંથી ગણેલી છૂટી બાજુનું માપ અલગ સમજાવ્યું છે.',
          'items': items}
(LANG/'translations/a00-m81244-added-solutions.gu.json').write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
print('Authored40 addition answers:3 word forms,4 models,3 grids,30 other worked responses.')
