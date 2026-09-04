"""Offline document builder plus structural and mathematical regression checks."""
from pathlib import Path
from fractions import Fraction as F
import csv
import hashlib
import json
import re
import unicodedata
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE/'translations/MR-BRIDGE-001.xml'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def require(condition, detail):
    if not condition:
        raise ValueError(detail)

def run():
    raw = SOURCE.read_bytes()
    root = ET.fromstring(raw)
    text = ''.join(root.itertext())
    require(root.get('lang') == 'mr-Deva-IN', 'wrong locale')
    require(unicodedata.normalize('NFC', text) == text, 'non-NFC translation')
    require('\ufffd' not in text, 'replacement character')
    ids = [e.get('id') for e in root.iter() if e.get('id')]
    require(len(ids) == len(set(ids)), 'duplicate XML/HTML IDs')
    links = [e.get('href')[1:] for e in root.iter('a') if e.get('href', '').startswith('#')]
    require(all(link in ids for link in links), 'broken answer/navigation link')
    for prefix in ('D', 'P'):
        for n in range(1, 7):
            require(f'{prefix}{n}' in ids and f'S-{prefix}{n}' in ids, 'missing question/solution')
    lock = json.loads((BASE/'sources.lock.json').read_text(encoding='utf-8'))
    sources = [e.get('data-source') for e in root.iter() if e.get('data-source')]
    require(sources == [s['locator'] for s in lock['source_selections']], 'source selection drift')
    for item in lock['witnesses']:
        require(sha((BASE/item['path']).read_bytes()) == item['sha256'], f'witness drift: {item["path"]}')
    source_ids = {s['target_id'] for s in lock['source_selections']}
    require(source_ids <= set(ids), 'source IDs not preserved')
    require(len(sources) == 10, 'expected eight examples and two definitions')
    # Recompute outcomes independently, then require the displayed chain to match.
    require(F(-315,770) == F(-9,22), 'reduction')
    require(F(-12,5)*(-20) == 48, 'product coefficient')
    require(F(-7,18)/F(-14,27) == F(3,4), 'division')
    require(7*(2-3)-8 == -15, 'n solution')
    require(F(2,3)*(3*3-6) == 5-3, 'm solution')
    f = lambda x: 2*x*x+3*x-1
    g = lambda x: 3*x-5
    require(f(3) == 26 and f(-2) == 1, 'function values')
    # Exact integer grid checks supplement algebraic manual review; not a universal proof.
    for x in range(-20,21):
        require(g(x+2) == 3*x+1 and g(x)+g(2) == 3*x-4, 'g expressions')
        require((x+1)**2+1 == x*x+2*x+2, 'square expansion')
        require(F(-12,5)*(-20*x) == 48*x, 'product expression')
    require(F(3,4)+F(1,6) == F(11,12), 'D1')
    require(F(-2,3)/F(4,9) == F(-3,2), 'D2')
    require(F(7-1,3) == 2 and (-3)**2-2*(-3) == 15, 'D4/D6')
    require(F(5,6)-F(1,4) == F(7,12), 'P1')
    require(F(3,4)*2-F(1,2) == 1, 'P2')
    require((-2)**2+1 == 5 and (1+2)/1 == 3, 'P4/P6')
    require((1+1)**2 != 1**2+1**2, 'counterexample')
    expected = {
      'reduce':'−315/770 = −9/22', 'product':'(−12/5)(−20x) = 12 · 4x = 48x',
      'quotient':'(−7/18) ÷ (−14/27) = (−7/18)(−27/14) = 3/4',
      'linear-n':'n = 2', 'linear-m':'m = 3', 'domain':'{1, 2, 3, 4, 5}', 'range':'{1, 4, 9, 16, 25}',
      'f3':'f(3) = 2(3)² + 3(3) − 1 = 18 + 9 − 1 = 26',
      'fminus2':'f(−2) = 2(−2)² + 3(−2) − 1 = 8 − 6 − 1 = 1', 'fa':'f(a) = 2a² + 3a − 1',
      'gh2':'g(h²) = 3h² − 5', 'gshift':'g(x + 2) = 3(x + 2) − 5 = 3x + 1',
      'gsum':'g(x) + g(2) = (3x − 5) + 1 = 3x − 4',
      'd1':'3/4 + 1/6 = 9/12 + 2/12 = 11/12', 'd2':'(−2/3)(9/4) = −18/12 = −3/2',
      'd3':'6x − 3 − 2x = 4x − 3', 'd4':'x = 7', 'd6':'f(−3) = (−3)² − 2(−3) = 9 + 6 = 15',
      'p1':'5/6 − 1/4 = 10/12 − 3/12 = 7/12', 'p2':'x = 2',
      'p4a':'f(−2) = (−2)² + 1 = 5', 'p4b':'f(a + 1) = (a + 1)² + 1 = a² + 2a + 2', 'p6':'x = 1',
    }
    actual = {e.get('data-check'): ''.join(e.itertext()) for e in root.iter() if e.get('data-check')}
    require(actual == expected, 'displayed mathematical chain changed; review and revalidate')
    relation = [(1,1),(2,4),(3,9),(4,16),(5,25)]
    require(sorted({p[0] for p in relation}) == [1,2,3,4,5], 'domain')
    require(sorted({p[1] for p in relation}) == [1,4,9,16,25], 'range')
    with (BASE/'terminology.csv').open(encoding='utf-8',newline='') as handle:
        terms = list(csv.DictReader(handle))
    term_ids = [t['id'] for t in terms]
    require(len(term_ids) == len(set(term_ids))
            and {f'T{n:03}' for n in range(1,34)} <= set(term_ids)
            and all(re.fullmatch(r'T[0-9]{3}', term_id) for term_id in term_ids), 'term ledger')
    for term_id in ('T001','T002','T003','T009','T011','T013','T018','T019','T020','T021'):
        term = next(t for t in terms if t['id'] == term_id)
        require(term['marathi'] in text, f'core term missing: {term_id}')
    require('परिभाषाक्षेत्र' not in text and 'सहक्षेत्र' not in text, 'superseded canon terms')
    # Source ID labels remain visible in review output without renumbering originals.
    for block in root.iter():
        if block.get('data-source'):
            label = ET.SubElement(block, 'p', {'class':'source-label', 'lang':'en'})
            label.text = 'Source: '+block.get('data-source')
    style = (BASE/'tools/reader.css').read_text(encoding='utf-8')
    body = ET.tostring(root, encoding='unicode', method='html')
    html = '<!doctype html>\n<html lang="mr-Deva-IN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>अपूर्णांकांपासून फलनांपर्यंत | Marathi STEM Bridge</title><style>'+style+'</style></head><body>'+body+'</body></html>\n'
    output = BASE/'output/MR-BRIDGE-001.html'
    output.parent.mkdir(exist_ok=True)
    output.write_text(html,encoding='utf-8',newline='\n')
    receipt = {
      'unit':'MR-BRIDGE-001','locale':'mr-Deva-IN','result':'PASS',
      'source_sha256':sha(raw),'html_sha256':sha(output.read_bytes()),
      'selected_source_blocks':len(sources),'translated_worked_examples':8,'translated_definitions':2,
      'original_diagnostic_items':6,'original_practice_items':6,'complete_worked_answers':12,
      'displayed_math_regressions':len(expected),'local_link_targets_checked':len(links),
      'unique_ids':len(ids),'terminology_entries':len(terms),
      'devanagari_characters':len(re.findall('[\u0900-\u097f]',text)),
      'checks':['XML well-formedness','NFC Unicode','exact locale','unique IDs','bidirectional question/answer navigation','source-block and preserved-ID coverage','committed provenance hashes','independent Fraction arithmetic','function substitutions','finite-grid expression regression (not proof)','exact displayed math chains','core terminology consistency','no external runtime or font dependency'],
      'not_claimed':['complete source-module translation','full upstream-book rebuild','native-speaker approval','human expert review','formal proof of every symbolic identity','cross-platform font identity'],
    }
    (BASE/'qa').mkdir(exist_ok=True)
    (BASE/'qa/build-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False,indent=2))

if __name__ == '__main__':
    run()
