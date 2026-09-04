"""Check exercise-fragment integrity and independently decode its number words."""
from pathlib import Path
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from prepare_m81243_exercises import C, M, SOURCE, SHA, validate_pair

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT/'gu-Gujr-IN/translations/a00-m81243-exercises.gu.cnxml'
original = ET.parse(SOURCE).getroot().find(f'.//{{{C}}}section[@id="fs-id2279009"]')
target = ET.parse(PATH).getroot().find(f'.//{{{C}}}section[@id="fs-id2279009"]')
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SHA
coverage = validate_pair(original, target)

# Scalar meanings are independent of the translation's English/Gujarati slot map.
# p13 of the OCRed Std6 Week1 canon supports છત્રીસ and સડસઠ, among others;
# GujaratiLexicon additionally confirms સિત્તોતેર=77 and અઠ્ઠોતેર=78.
WORDS = {
    'એક':1, 'બે':2, 'ત્રણ':3, 'ચાર':4, 'પાંચ':5, 'છ':6, 'સાત':7,
    'દસ':10, 'અગિયાર':11, 'બાર':12, 'તેર':13, 'ચૌદ':14, 'પંદર':15,
    'સત્તર':17, 'અઢાર':18, 'તેવીસ':23, 'ચોવીસ':24, 'છવ્વીસ':26,
    'પાંત્રીસ':35, 'છત્રીસ':36, 'સાડત્રીસ':37, 'ઓગણચાલીસ':39,
    'ચુમ્માલીસ':44, 'છેતાલીસ':46, 'ત્રેપન':53, 'છપ્પન':56,
    'એકસઠ':61, 'ચોસઠ':64, 'સડસઠ':67, 'અડસઠ':68, 'એકોતેર':71,
    'તોતેર':73, 'પંચોતેર':75, 'છોતેર':76, 'સિત્તોતેર':77,
    'અઠ્ઠોતેર':78, 'ત્ર્યાસી':83, 'નેવ્યાસી':89, 'ત્રાણું':93,
    'એકસો':100, 'બસો':200, 'ત્રણસો':300, 'ચારસો':400, 'પાંચસો':500,
    'છસો':600, 'સાતસો':700, 'આઠસો':800, 'નવસો':900,
}
SCALES = {'હજાર':10**3, 'મિલિયન':10**6, 'બિલિયન':10**9, 'ટ્રિલિયન':10**12}
CASES = {
    'fs-id1578269':1078, 'fs-id1841547':364510, 'fs-id2703955':5846103,
    'fs-id1236756':37889005, 'fs-id3398681':14410, 'fs-id1358066':613200,
    'fs-id1193287':2617176, 'fs-id1166481':23867000, 'fs-id2221988':1377583156,
    'fs-id1388718':412, 'fs-id2291517':253, 'fs-id2135363':35975,
    'fs-id2288048':61415, 'fs-id2491175':11044167, 'fs-id1397862':18102783,
    'fs-id1612747':3226512017, 'fs-id2171400':11471036106,
    'fs-id2211384':7173000000, 'fs-id1517446':4568000000,
    'fs-id1576329':39000000000000, 'fs-id2214935':3500000000000,
    'fs-id2587177':24493,
}


def decode_number_words(text):
    tokens = re.findall(r'[\u0a80-\u0aff]+', text)
    where = [i for i,t in enumerate(tokens) if t in WORDS or t in SCALES]
    assert where, text
    numeral = tokens[where[0]:where[-1]+1]
    assert all(t in WORDS or t in SCALES for t in numeral), numeral
    total = subtotal = 0
    for token in numeral:
        if token in SCALES:
            total += subtotal * SCALES[token]
            subtotal = 0
        else:
            subtotal += WORDS[token]
    return total + subtotal


for ident, expected in CASES.items():
    el = target.find(f'.//*[@id="{ident}"]')
    assert decode_number_words(''.join(el.itertext())) == expected, ident

# Check the source-supplied roundings against arithmetic, beyond token equality.
ROUNDINGS = [(386,10,390),(2931,10,2930),(13748,100,13700),
             (391794,100,391800),(1492,10,1490),(1497,10,1500),
             (63994,100,64000),(63949,100,63900),
             (24493,10,24490),(24493,100,24500),(24493,1000,24000),
             (24493,10000,20000),(1355692544,10**9,10**9),
             (1355692544,10**8,1400000000),(1355692544,10**6,1356000000)]
for number, place, expected in ROUNDINGS:
    assert ((number + place//2)//place)*place == expected

# No source-facing English remains in text, tails, or alt attributes.
for el in target.iter():
    for value in (el.text, el.tail, el.get('alt')):
        assert not re.search('[A-Za-z]', value or ''), (el.get('id'),value)

meta = json.loads((ROOT/'gu-Gujr-IN/translations/a00-m81243-metadata.gu.json').read_text(encoding='utf-8'))
assert len(meta['self_check_table']['headers']) == 4
assert len(meta['self_check_table']['rows']) == 6
for field in ('metadata_cnxml','glossary_cnxml'):
    ET.fromstring(meta[field])
print(json.dumps({'result':'pass', **coverage, 'number_word_values_checked':len(CASES),
                  'source_roundings_checked':len(ROUNDINGS),
                  'self_check_headers':4, 'self_check_rows':6,
                  'exercise_file_sha256':hashlib.sha256(PATH.read_bytes()).hexdigest()}, indent=2))
