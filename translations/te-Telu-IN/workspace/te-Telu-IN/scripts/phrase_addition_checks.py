"""Finite B016 phrase/expression/value checks against actual displayed content.

This is an independent unit-specific mathematics check, not a general Telugu
parser, native-speaker approval, or a claim about other uses of English phrases.
All validation is read-only. No mathematical expression is passed to eval().
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from naming_checks import text_of

BASE = Path(__file__).resolve().parents[1]
CN = '{http://cnx.rice.edu/cnxml}'
MATH = '{http://www.w3.org/1998/Math/MathML}'
XH = '{http://www.w3.org/1999/xhtml}'
SOURCE_SHA = 'a185ed309ff878a6d29a714fabb8d3986c6020a82dbc7c99d89b2eb8f135aa0f'
TABLES = {'fs-id1826990': (5, 2, 4), 'eip-id1168288294973': (3, 4, 2),
          'eip-id1168288520954': (3, 4, 2)}
INTRO = ('1 plus 2', 'the sum of 3 and 4', '5 increased by 6',
         '8 more than 7', 'the total of 9 and 5', '6 added to 4')
INTRO_PAIRS = ((1, 2), (3, 4), (5, 6), (7, 8), (9, 5), (4, 6))
# exercise, supplied solution, kind, exact phrase, ordered expression
CASES = (
    ('fs-id1392862', 'fs-id1363349', 'W', 'the sum of 19 and 23', (19, 23)),
    ('fs-id1932733', 'fs-id2211062', 'S', 'the sum of 17 and 26', (17, 26)),
    ('fs-id1311804', 'fs-id1731443', 'S', 'the sum of 28 and 14', (28, 14)),
    ('fs-id1330230', 'fs-id1726814', 'W', '28 increased by 31', (28, 31)),
    ('fs-id2130020', 'fs-id2164356', 'S', '29 increased by 76', (29, 76)),
    ('fs-id2792137', 'fs-id1410392', 'S', '37 increased by 69', (37, 69)),
)
PRACTICE = {
    'D01': ('the sum of 24 and 18', (24, 18)),
    'R01': ('the total of 16 and 27', (16, 27)),
    'D02': ('8 more than 15', (15, 8)),
    'R02': ('6 added to 19', (19, 6)),
    'D03': ('46 increased by 57', (46, 57)),
    'R03': ('38 increased by 64', (38, 64)),
}
NUM = r'(?:0|[1-9][0-9]*)'
SUM = NUM + r'(?:\s*\+\s*' + NUM + r')*'
RELATION = re.compile(r'(?<![0-9A-Za-z_.,])' + SUM + r'(?:\s*=\s*' + SUM + r')+(?![0-9]|,[0-9]|\.[0-9])')


def compact(value):
    return re.sub(r'\s+', '', value)


def ids_of(root):
    nodes = [n for n in root.iter() if n.get('id')]
    result = {n.get('id'): n for n in nodes}
    assert len(result) == len(nodes), 'Duplicate B016 ID'
    return result


def require(node_or_text, phrases, context):
    value = node_or_text if isinstance(node_or_text, str) else text_of(node_or_text)
    for phrase in phrases:
        assert phrase in value, context + ': missing/changed ' + phrase


def phrase_pair(phrase):
    """Only six reviewed numeric English constructions, with explicit direction."""
    phrase = ' '.join(phrase.split())
    patterns = (
        (rf'({NUM}) plus ({NUM})', False),
        (rf'the sum of ({NUM}) and ({NUM})', False),
        (rf'({NUM}) increased by ({NUM})', False),
        (rf'({NUM}) more than ({NUM})', True),
        (rf'the total of ({NUM}) and ({NUM})', False),
        (rf'({NUM}) added to ({NUM})', True),
    )
    for pattern, reverse in patterns:
        match = re.fullmatch(pattern, phrase)
        if match:
            pair = tuple(map(int, match.groups()))
            return pair[::-1] if reverse else pair
    raise AssertionError('Unsupported/changed B016 English phrase: ' + phrase)


def expression_pair(value):
    match = re.fullmatch(rf'({NUM})\s*\+\s*({NUM})', value.strip())
    assert match, 'B016 expression must contain two addends and +, not a value/equation'
    return tuple(map(int, match.groups()))


def equality(value):
    sides = re.split(r'\s*=\s*', value.strip())
    assert len(sides) == 2, 'B016 equality shape changed'
    assert re.fullmatch(SUM, sides[0]) and re.fullmatch(NUM, sides[1]), 'B016 unsupported equality'
    operands = tuple(map(int, re.split(r'\s*\+\s*', sides[0])))
    total = int(sides[1])
    assert sum(operands) == total, 'B016 incorrect displayed equality: ' + value
    return operands, total


def displayed_equalities(root):
    found = []
    blocks = {'p', 'li', 'td', 'dd'}
    for node in root.iter():
        if node.tag.rsplit('}', 1)[-1] not in blocks:
            continue
        if any(n is not node and n.tag.rsplit('}', 1)[-1] in blocks for n in node.iter()):
            continue
        found.extend(equality(m.group()) for m in RELATION.finditer(text_of(node)))
    return found


def math_signature(root):
    # Preserve even the intentional leading space and punctuation in mn tokens.
    # A math root's exterior tail is translatable prose; its descendants' tails
    # are inside MathML and must not acquire an extra digit/operator either.
    return [[(n.tag, tuple(sorted(n.attrib.items())), n.text,
              None if n is math else n.tail, len(n)) for n in math.iter()]
            for math in root.iter(MATH + 'math')]


def structure(root):
    omitted = {'aria-label', 'summary', '{http://www.w3.org/XML/1998/namespace}lang'}
    return [(n.tag, tuple(sorted((k, v) for k, v in n.attrib.items() if k not in omitted)), len(n))
            for n in root.iter()]


def lines_of(entry):
    """Read source newline-separated cells, retaining each phrase as a unit."""
    lines = [entry.text or '']
    for child in entry:
        if child.tag == CN + 'newline':
            lines.append(child.tail or '')
        else:
            lines[-1] += ''.join(child.itertext()) + (child.tail or '')
    return [' '.join(line.split()) for line in lines]


def source_cases():
    raw = (BASE / 'sources/TE-B016.en.cnxml').read_bytes()
    assert sha256(raw).hexdigest() == SOURCE_SHA, 'B016 frozen source changed'
    source = ET.fromstring(raw)
    ids = ids_of(source)
    assert (len(list(source.iter())), len(ids), len(list(source.iter(MATH + 'math')))) == (273, 41, 52)
    rows = ids['fs-id1826990'].findall('.//' + CN + 'row')
    assert tuple(lines_of(rows[1][2])) == INTRO, 'B016 source phrase order changed'
    assert tuple(expression_pair(x) for x in lines_of(rows[1][3])) == INTRO_PAIRS
    assert tuple(phrase_pair(x) for x in INTRO) == INTRO_PAIRS
    for ident, (declared, count, width) in TABLES.items():
        table = ids[ident]
        assert table.find(CN + 'tgroup').get('cols') == str(declared)
        rows = table.findall('.//' + CN + 'row')
        assert len(rows) == count and all(len(r) == width for r in rows)
    exercises = list(source.iter(CN + 'exercise'))
    assert [n.get('id') for n in exercises] == [c[0] for c in CASES]
    derived = []
    for ex, (ident, sid, kind, phrase, pair) in zip(exercises, CASES):
        problem = ex.find(CN + 'problem')
        actual_phrase = text_of(problem).removeprefix('Translate and simplify: ').removesuffix('.')
        assert actual_phrase == phrase and phrase_pair(actual_phrase) == pair
        solution = ex.find(CN + 'solution')
        assert solution.get('id') == sid
        text = text_of(solution)
        if kind == 'W':
            rows = solution.findall('.//' + CN + 'row')
            assert expression_pair(text_of(rows[1][1])) == pair
            assert int(text_of(rows[2][1])) == sum(pair)
        else:
            match = re.fullmatch(r'Translate:?\s*(.+); Simplify:?\s*([0-9]+)', text)
            assert match and expression_pair(match[1]) == pair and int(match[2]) == sum(pair)
        derived.append((ident, pair, sum(pair)))
    return source, tuple(derived)


def validate_phrase_target(target):
    source, derived = source_cases()
    assert structure(target) == structure(source), 'B016 source structure/attributes changed'
    assert math_signature(target) == math_signature(source), 'B016 protected MathML changed'
    ids = ids_of(target)
    table = ids['fs-id1826990']
    rows = table.findall('.//' + CN + 'row')
    assert [text_of(n) for n in rows[0]] == ['గణిత క్రియ', 'మాటలు (ఆంగ్ల పదబంధాలతో)', 'ఉదాహరణ', 'గణిత రాత (expression)'], 'B016 phrase table header roles'
    assert text_of(rows[1][0]) == 'సంకలనం', 'B016 operation changed'
    assert lines_of(rows[1][1]) == ['కలిపితే (plus)', 'మొత్తం (sum)', 'ఇంత మేర పెరిగిన (increased by)',
                                  'ఇచ్చిన సంఖ్యకంటే ఇంత ఎక్కువ (more than)', 'ఈ సంఖ్యల మొత్తం (total of)', 'దీనికి చేర్చిన (added to)'], 'B016 English phrase/gloss mapping'
    assert lines_of(rows[1][2]) == ['1కు కలపవలసిన సంఖ్య 2', 'మొత్తం కనుగొనవలసిన సంఖ్యలు 3 మరియు 4',
                                  '5ను పెంచవలసిన పరిమాణం 6', '8ను కలపవలసిన ఆధార సంఖ్య 7',
                                  'కలిపి మొత్తంగా లెక్కించవలసిన సంఖ్యలు 9 మరియు 5', '6ను చేర్చవలసిన ఆధార సంఖ్య 4'], 'B016 Telugu phrase roles/order'
    assert tuple(expression_pair(x) for x in lines_of(rows[1][3])) == INTRO_PAIRS
    aria = table.get('aria-label', '')
    require(aria, ['రెండు వరుసలు, నాలుగు నిలువు వరుసల', '7కంటే 8 ఎక్కువైన సంఖ్య — 7+8',
                   '4కు 6 చేర్చడం — 4+6', 'ఆరు జతలు ఒకే ప్రధాన వరుసలో', 'వాటి విలువలు ఇక్కడ లెక్కించలేదు'], 'B016 accessible table scope/direction')
    assert re.findall(r'\d+', aria) == ['1','2','1','2','3','4','3','4','5','6','5','6','7','8','7','8','9','5','9','5','4','6','4','6'], 'B016 accessible mappings changed'
    require(ids['fs-id2649934'], ['sum (మొత్తం)', 'ఆంగ్ల పదం', 'మూల ఆంగ్ల పదబంధంలో', 'of (ఆంగ్ల పదం)', 'and (ఆంగ్ల పదం)', 'ఇచ్చిన రెండు సంఖ్యలే కలిపే సంఖ్యలు'], 'B016 English grammar scope')
    require(ids['fs-id1578716'], ['ఆంగ్ల పదబంధం', 'increased by', 'కలపాలని చెబుతుంది'], 'B016 increased-by scope')
    for ident, sid, kind, phrase, pair in CASES:
        ex = ids[ident]
        problem = text_of(ex.find(CN + 'problem'))
        require(problem, ['గణిత రాతగా రాసి, దాని విలువ కనుగొనండి'], 'B016 both requested stages')
        require(problem, ['మొత్తాన్ని గణిత రాతగా' if 'sum' in phrase else 'ను పెంచవలసిన పరిమాణం'], 'B016 requested operation')
        solution = ids[sid]
        if kind == 'W':
            table = solution.find(CN + 'table')
            summary = table.get('summary', '')
            require(summary, ['నాలుగు వరుసలు, రెండు నిలువు వరుసల', 'గణిత రాత', 'కలిపితే', 'మొదటి, చివరి వరుసల్లో ఎడమ గడి ఖాళీగా'], 'B016 solution summary shape/stages')
            a, b = pair; result = sum(pair)
            assert re.findall(r'\d+', summary) == list(map(str, [a,b,a,b,result,a,b,result])), 'B016 solution summary numbers'
            row = table.findall('.//' + CN + 'row')
            assert text_of(row[1][0]) == 'గణిత రాతగా రాయండి.' and text_of(row[2][0]) == 'కలపండి.', 'B016 translate/add stage labels'
            assert not text_of(row[0][0]) and not text_of(row[3][0]), 'B016 intentional empty cells changed'
        else:
            text = text_of(solution)
            match = re.fullmatch(r'గణిత రాత:\s*(.+); విలువ:\s*([0-9]+)', text)
            assert match and expression_pair(match[1]) == pair and int(match[2]) == sum(pair), 'B016 actual expression/value answer changed: ' + ident
    assert not list(ids['fs-id1410392'].iter(MATH + 'math')), 'B016 plain-text final solution representation changed'
    return derived


def expected_steps(pair):
    a, b = pair
    ones = (a % 10, b % 10)
    carry = sum(ones) // 10
    tens = ((carry,) if carry else ()) + tuple(n // 10 for n in pair if n >= 10)
    return ((ones, sum(ones)), (tens, sum(tens)), (pair, a + b))


def answer_detail(node, pair):
    strong = [text_of(n) for n in node.iter(XH + 'strong')]
    assert len(strong) == 5, 'B016 complete answer/reasoning coverage'
    assert expression_pair(strong[0]) == pair, 'B016 displayed ordered expression changed'
    assert re.fullmatch(NUM, strong[1]) and int(strong[1]) == sum(pair), 'B016 displayed value changed'
    require(node, ['గణిత రాత:', 'విలువ:', 'ఒకట్లలో'], 'B016 expression/value/column roles')
    value = compact(text_of(node))
    a, b = pair
    assert f'గణితరాత:{a}+{b}.విలువ:{a+b}.' in value, 'B016 expression/value label association'
    assert 'పదుల్లో' in text_of(node) or 'పదులలో' in text_of(node), 'B016 tens reasoning absent'
    expected = expected_steps(pair)
    assert tuple(equality(n) for n in strong[2:]) == expected, 'B016 ordered column arithmetic changed'
    assert tuple(displayed_equalities(node)) == expected, 'B016 answer equation coverage changed'
    ones, tens, _ = expected
    if ones[1] >= 10:
        assert re.search(str(ones[1] % 10) + r'(?:ఒకట్లు)?రాసి1పదినిబదిలీ', value), 'B016 written ones/carry destination'
    else:
        require(node, ['బదిలీ అవసరం లేదు'], 'B016 no-carry case')
    if sum(pair) >= 100:
        assert tens[1] == 10 and re.search(r'0(?:పదులు)?రాసి1వందనుబదిలీ', value), 'B016 zero tens/carry destination'
    return expected


def validate_b016(target, bridge):
    """Validate actual ElementTree roots; return finite source/bridge counts."""
    derived = validate_phrase_target(target)
    ids = ids_of(bridge)
    assert bridge.get('id') == 'B016-bridge'
    details = list(bridge.iter(XH + 'details'))
    expected_ids = {'B016-' + kind + '-' + ident for ident, _, kind, _, _ in CASES}
    expected_ids |= {'B016-S-' + ident for ident in PRACTICE}
    assert {n.get('id') for n in details} == expected_ids and len(details) == 12, 'B016 full solution coverage'
    expected_eq = Counter()
    for ident, _, kind, phrase, pair in CASES:
        node = ids['B016-' + kind + '-' + ident]
        assert text_of(node.find(XH + 'summary')).startswith(phrase + ' — '), 'B016 source phrase/case mapping'
        assert [n.get('href') for n in node.iter(XH + 'a')] == ['#' + ident], 'B016 exact source backlink'
        expected_eq.update(answer_detail(node, pair))
    routes = {'D01': ['B016-S-D01','B016-K1','B016-R01'],
              'D02': ['B016-S-D02','B016-K2','B016-K3','B016-R02'],
              'D03': ['B016-S-D03','B016-S-fs-id2130020','B016-R03']}
    for ident, (phrase, pair) in PRACTICE.items():
        question = ids['B016-' + ident]
        english = [text_of(n).strip('“”') for n in question.iter(XH + 'span') if n.get('lang') == 'en']
        assert english == [phrase] and phrase_pair(english[0]) == pair, 'B016 entry/recheck phrase or direction changed'
        require(question, ['గణిత రాత, విలువ'], 'B016 entry/recheck requires both stages')
        expected_links = routes.get(ident, ['B016-S-' + ident])
        assert [n.get('href') for n in question.iter(XH + 'a')] == ['#' + x for x in expected_links], 'B016 skill/recheck routing changed'
        expected_eq.update(answer_detail(ids['B016-S-' + ident], pair))
    role_phrases = {
        'D01': ['24, 18 సంఖ్యల మొత్తం'], 'R01': ['16, 27 సంఖ్యల మొత్తం'],
        'D02': ['15కంటే 8 ఎక్కువైన సంఖ్య'], 'R02': ['19కు 6 చేర్చితే'],
        'D03': ['46ను 57 మేర పెంచితే'], 'R03': ['38ను 64 మేర పెంచితే'],
    }
    for ident, phrases in role_phrases.items():
        require(ids['B016-' + ident], phrases, 'B016 Telugu prompt roles')
    for ident, phrases in {
        'B016-S-D02': ['ఆధార సంఖ్య 15; కలిపే పరిమాణం 8', '8+15కూ విలువ 23నే అయినా', '8>15 అనేది ఈ పదబంధానికి అనువాదం కాదు'],
        'B016-S-R02': ['ఆధార సంఖ్య 19; కలిపే పరిమాణం 6', '6+19 కూడా అదే విలువ'],
        'B016-S-fs-id1311804': ['19+23కూ విలువ 42', 'ఇచ్చిన సంఖ్యల జత, గణిత రాత వేరు'],
        'B016-S-fs-id2130020': ['1 వంద, 0 పదులు, 5 ఒకట్లు అంటే 105', 'మధ్య 0ను వదిలేస్తే తప్పు'],
        'B016-S-fs-id2792137': ['37కు 69 కలపాలి; 69నే మొత్తం అనుకోకండి', 'సాధారణ పాఠ్యంగా'],
        'B016-S-D03': ['46 ఆధార సంఖ్య; దానికి 57 కలపాలి', '103, 13 కాదు'],
        'B016-S-R03': ['పదుల స్థానంలో', 'వందల స్థానపు 1, ఒకట్ల స్థానపు 2', '12 చేయకండి'],
        'B016-W-fs-id1392862': ['4 పదులు, 2 ఒకట్లు'],
        'B016-W-fs-id1330230': ['28 ఆధార సంఖ్య', 'పెంచవలసిన పరిమాణం 31', '5 పదులు, 9 ఒకట్లు'],
        'B016-S-fs-id1932733': ['4 పదులు, 3 ఒకట్లు'],
    }.items():
        require(ids[ident], phrases, 'B016 operand/carry/zero meaning')
    k1 = ids['B016-K1']
    require(k1, ['మొదటి పని:', 'రెండవ పని:', 'ఆ లెక్క చేసి విలువ కనుగొనండి', 'ఈ పాఠ్యంలో “simplify”',
                 'సమానత్వాన్ని తెలిపే వాక్యం (equation)', 'కేవలం 42 రాస్తే', 'కేవలం 19+23 రాస్తే విలువ ఇంకా చెప్పలేదు',
                 'అధికారిక సమానార్థంగా వాడుతున్నామని అనుకోకండి'], 'B016 task/equality/terminology scope')
    numeric = [text_of(n) for n in k1.iter(XH + 'strong')][2:]
    assert numeric == ['19+23', '42', '19+23=42'], 'B016 introductory expression/value/equation distinction'
    expected_eq.update([(pair, sum(pair)) for pair in INTRO_PAIRS])
    expected_eq.update([((19,23),42)])
    k2 = ids['B016-K2']
    rows = k2.findall('.//' + XH + 'tbody/' + XH + 'tr')
    assert len(rows) == 6 and all(len(r) == 4 for r in rows), 'B016 bridge phrase mapping shape'
    glosses = ['1కు 2 కలిపితే','3, 4 సంఖ్యల మొత్తం','5ను 6 మేర పెంచితే',
               '7కంటే 8 ఎక్కువైన సంఖ్య','9, 5 సంఖ్యలను కలిపిన మొత్తం','4కు 6 చేర్చితే']
    for row, phrase, pair, gloss in zip(rows, INTRO, INTRO_PAIRS, glosses):
        assert row[0].get('lang') == 'en' and text_of(row[0]) == phrase, 'B016 English table phrase changed'
        assert phrase_pair(text_of(row[0])) == expression_pair(text_of(row[2])) == pair, 'B016 bridge phrase/expression direction'
        assert text_of(row[1]) == gloss, 'B016 Telugu table role changed'
    for row, phrases in zip(rows, [['ఇచ్చిన క్రమంలో 1, తరువాత 2'], ['of, and ఆంగ్లంలో'],
                                  ['ఆధార సంఖ్య 5; దానికి కలిపే పరిమాణం 6'], ['ఆధార సంఖ్య 7; కలిపే పరిమాణం 8'],
                                  ['రెండు సంఖ్యల మొత్తాన్ని'], ['4కు ముందున్న 6ను చేర్చాలి']]):
        require(row[3], phrases, 'B016 table addend roles')
    require(k2, ['మూలం చూపిన క్రమాన్ని రాయండి', 'ఈ తదుపరి లెక్కలు అదనపు విలువల తనిఖీ:',
                 'ఇవి మూల పట్టికలో కొత్త జవాబులుగా చేర్చినవి కావు'], 'B016 ordered/original-table scope')
    k3 = ids['B016-K3']
    assert [text_of(n) for n in k3.iter(XH + 'strong')] == ['7+8','15','8>7','9+0','9'], 'B016 addition/comparison/zero objects'
    require(k3, ['“8 more than 7”', '“8 is more than 7”', 'రెండవది పోలిక',
                 'సందర్భం చూడకుండా ఎప్పుడూ + గుర్తు పెట్టకండి', '90 కాదు', 'ఏదీ కొత్తగా చేర్చకపోవడం, అంకె పక్కన సున్నను రాయడం వేరు'], 'B016 comparison/zero scope')
    all_eq = displayed_equalities(bridge)
    assert Counter(all_eq) == expected_eq and len(all_eq) == 43, 'B016 actual equation coverage/operands changed'
    source_ids = ids_of(target)
    for link in bridge.iter(XH + 'a'):
        href = link.get('href', '')
        assert href.startswith('#') and href[1:] in (ids.keys() | source_ids.keys()), 'B016 unresolved link'
    assert len(ids) == 27 and len(list(bridge.iter(XH + 'a'))) == 20, 'B016 bridge ID/link coverage'
    return {'source_exercises': 6, 'source_try_it_parts': 4, 'source_phrase_mappings': 6,
            'source_expression_value_pairs': len(derived), 'source_math_roots': 52,
            'source_plain_text_solutions': 1, 'bridge_solution_details': 12,
            'original_entry_rechecks': 6, 'bridge_displayed_equalities': len(all_eq)}
