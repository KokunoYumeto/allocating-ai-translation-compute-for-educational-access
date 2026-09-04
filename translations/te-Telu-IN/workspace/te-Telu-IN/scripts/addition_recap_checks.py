"""Read-only finite mathematics for B018's addition key-concepts recap.

The frozen source has no exercise answers. Source notation/properties/algorithm
are checked separately from any explicitly original bridge practice.
"""
from hashlib import sha256
from collections import Counter
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from naming_checks import text_of

BASE = Path(__file__).resolve().parents[1]
CN = '{http://cnx.rice.edu/cnxml}'
MATH = '{http://www.w3.org/1998/Math/MathML}'
XH = '{http://www.w3.org/1999/xhtml}'
SOURCE_SHA = '2ed4ba3ccb103953b8df710aacd5c956f26563c1c5fb6da2429ac138058b1a82'
TABLE = 'eip-id1170324017502'
IDENTITY = 'eip-id1170325229876'
COMMUTATION = 'eip-id1170325285133'
ALGORITHM = 'eip-id1170325253924'
SOURCE_MATH = ('+','3+4','3','4','a','0','a+0=a','0+a=a','a','b','a+b=b+a')
NUMBER = r'(?:0|[1-9][0-9]*)'
EXPRESSION = NUMBER + r'(?:\s*\+\s*' + NUMBER + r')*'
RELATION = re.compile(r'(?<![0-9A-Za-z_.,])'+EXPRESSION+r'(?:\s*=\s*'+EXPRESSION+r')+(?![0-9]|,[0-9]|\.[0-9])')


def compact(value):
    return re.sub(r'\s+', '', value)


def ids_of(root):
    nodes = [n for n in root.iter() if n.get('id')]
    result = {n.get('id'): n for n in nodes}
    assert len(result) == len(nodes), 'B018 duplicate ID'
    return result


def math_signature(root):
    return [tuple((n.tag, tuple(sorted(n.attrib.items())), n.text,
                   None if n is math else n.tail, len(n)) for n in math.iter())
            for math in root.iter(MATH+'math')]


def structure(root):
    omitted = {'alt','aria-label','summary','{http://www.w3.org/XML/1998/namespace}lang'}
    return [(n.tag,tuple(sorted((k,v) for k,v in n.attrib.items() if k not in omitted)),len(n))
            for n in root.iter()]


def addition(value):
    assert re.fullmatch(EXPRESSION, value.strip()), 'B018 unsigned addition expression changed'
    return tuple(int(s) for s in re.split(r'\s*\+\s*',value.strip()))


def equality(value):
    """Validate all sides, including same-sum order reversals, using integers."""
    sides = re.split(r'\s*=\s*',value.strip())
    assert len(sides) >= 2, 'B018 equality relation missing'
    operands = tuple(addition(side) for side in sides)
    assert len({sum(side) for side in operands}) == 1, 'B018 incorrect displayed equality'
    return operands


def column_steps(numbers):
    """Return unit, addend digits, incoming, total, write, outgoing for each place."""
    assert len(numbers) >= 2 and all(type(n) is int and n >= 0 for n in numbers)
    unit, carry, rows = 1, 0, []
    while unit <= max(numbers) or carry:
        digits = tuple(n//unit % 10 for n in numbers)
        total = sum(digits)+carry
        rows.append((unit,digits,carry,total,total%10,total//10))
        carry = total//10
        unit *= 10
    if not rows:
        rows.append((1,tuple(0 for _ in numbers),0,0,0,0))
    assert sum(r[0]*r[4] for r in rows) == sum(numbers)
    return tuple(rows)


def source_baseline():
    raw = (BASE/'sources/TE-B018.en.cnxml').read_bytes()
    assert sha256(raw).hexdigest() == SOURCE_SHA, 'B018 frozen source changed'
    source = ET.fromstring(raw)
    ids = ids_of(source)
    assert source.get('id') == 'fs-id1611455' and source.get('class') == 'key-concepts'
    assert (len(list(source.iter())),len(ids),len(list(source.iter(MATH+'math')))) == (81,6,11)
    assert [len(list(source.iter(MATH+x))) for x in ('mi','mn','mo')] == [11,7,9]
    assert not any(source.iter(CN+'exercise')) and not any(source.iter(CN+'solution'))
    assert not any(source.iter(CN+'media')) and not any(source.iter(CN+'link'))
    assert len(list(source.iter(CN+'table'))) == 1
    assert tuple(compact(text_of(n)) for n in source.iter(MATH+'math')) == SOURCE_MATH
    assert {n.text for n in source.iter(MATH+'mi')} == {'a','b'}
    rows = ids[TABLE].findall('.//'+CN+'row')
    assert ids[TABLE].find(CN+'tgroup').get('cols') == '5' and [len(r) for r in rows] == [5,5]
    assert [text_of(n) for n in rows[0]] == ['Operation','Notation','Expression','Read as','Result']
    assert [text_of(n) for n in rows[1]] == ['Addition','+','3+4','three plus four','the sum of 3 and 4']
    assert [compact(text_of(n)) for n in ids[IDENTITY].iter(MATH+'math')] == ['a','0','a+0=a','0+a=a']
    assert [compact(text_of(n)) for n in ids[COMMUTATION].iter(MATH+'math')] == ['a','b','a+b=b+a']
    steps = ids[ALGORITHM]
    assert steps.attrib == {'id':ALGORITHM,'list-type':'enumerated','number-style':'arabic','class':'stepwise'}
    assert [text_of(n) for n in steps] == [
        'Write the numbers so each place value lines up vertically.',
        'Add the digits in each place value. Work from right to left starting with the ones place. If a sum in a place value is more than 9, carry to the next place value.',
        'Continue adding each place value from right to left, adding each place value and carrying if needed.']
    return source


def require(node_or_text, phrases, context):
    value=node_or_text if isinstance(node_or_text,str) else text_of(node_or_text)
    for phrase in phrases:assert phrase in value, context+': missing/changed '+phrase


def displayed_relations(root):
    result=[]
    for node in root.iter():
        if node.tag.rsplit('}',1)[-1] not in {'p','li','td','dd'}:continue
        if any(n is not node and n.tag.rsplit('}',1)[-1] in {'p','li','td','dd'} for n in node.iter()):continue
        for match in RELATION.finditer(text_of(node)):
            equality(match.group());result.append(compact(match.group()))
    return result


def validate_recap_target(target):
    source=source_baseline();ids=ids_of(target)
    assert structure(source)==structure(target), 'B018 source structure/attributes changed'
    assert math_signature(source)==math_signature(target), 'B018 protected MathML changed'
    assert target.get('{http://www.w3.org/XML/1998/namespace}lang')=='te-Telu-IN'
    table=ids[TABLE];rows=table.findall('.//'+CN+'row')
    assert table.find(CN+'tgroup').get('cols')=='5' and [len(r) for r in rows]==[5,5]
    assert [text_of(n) for n in rows[0]]==['క్రియ (operation)','చిహ్నం (notation)','గణిత రాత (expression)',
        'చదివే విధానం (read as)','ఫలితం (result)'], 'B018 notation table column roles'
    assert [text_of(n) for n in rows[1]]==['సంకలనం','+','3+4','మూడు ప్లస్ నాలుగు (three plus four)',
        'మూడు, నాలుగు అనే సంఖ్యల మొత్తం; కలిపే సంఖ్యలు 3 మరియు 4'], 'B018 actual notation/result-name row'
    assert '7' not in text_of(rows[1][4]), 'B018 source result-name cannot become evaluated value'
    require(ids[IDENTITY],['ఏ సంఖ్య అయినా','కలిపితే అదే సంఖ్య వస్తుంది'],
            'B018 identity meaning')
    require(ids[COMMUTATION],['కలిపే సంఖ్యలు','క్రమం మారినా వాటి మొత్తం మారదు'],
            'B018 commutative meaning')
    steps=ids[ALGORITHM]
    assert [text_of(n) for n in steps]==[
        'ఒకే స్థానపు అంకెలు ఒకే నిలువు వరుసలో ఉండేలా సంఖ్యలను రాయండి.',
        'ప్రతి స్థానంలోని అంకెలను కలపండి. ఒకట్ల స్థానం నుంచి ప్రారంభించి కుడి నుంచి ఎడమకు పని చేయండి. ఏ స్థానంలోనైనా మొత్తం 9 కంటే ఎక్కువైతే, ఆ మొత్తాన్ని మళ్లీ సమూహాలుగా అమర్చి, తరువాతి ఎడమ స్థానానికి అవసరమైన ప్రమాణాలను బదిలీ చేయండి.',
        'ఇలాగే కుడి నుంచి ఎడమకు ప్రతి స్థానంలోని అంకెలను కలుపుతూ, అవసరమైనప్పుడు బదిలీ చేస్తూ కొనసాగించండి.'], 'B018 exact three-step algorithm'
    assert '10 కంటే ఎక్కువ' not in text_of(steps), 'B018 exact10 carry boundary changed'
    return {'source_elements':81,'source_slots':53,'source_ids':6,'source_math_roots':11,
            'source_tables':1,'source_exercises':0}


def bridge_table(node, expected_rows):
    tables=list(node.iter(XH+'table'));assert len(tables)==2, 'B018 K3 two distinct place/carry tables'
    placement,carry=tables
    assert [text_of(n) for n in placement.findall(XH+'thead/'+XH+'tr/'+XH+'th')] == ['సంఖ్య పాత్ర','పదులు','ఒకట్లు']
    rows=placement.findall(XH+'tbody/'+XH+'tr');assert len(rows)==3 and all(len(r)==3 for r in rows)
    actual=[(text_of(r[0]),text_of(r[1]),text_of(r[2]),r[0].tag,r[0].get('scope')) for r in rows]
    assert actual==expected_rows, 'B018 actual place-alignment table changed'
    assert [text_of(n) for n in carry.findall(XH+'thead/'+XH+'tr/'+XH+'th')] == [
        'స్థానం','లెక్క','రాసే అంకె','తరువాతి స్థానానికి బదిలీ']
    rows=carry.findall(XH+'tbody/'+XH+'tr');assert len(rows)==2 and all(len(r)==4 for r in rows)
    expected=[('ఒకట్లు','8+7=15','5','1 పది'),('పదులు','3+2+1=6','6','0 వందలు; బదిలీ లేదు')]
    assert [(text_of(r[0]),text_of(r[1]),text_of(r[2]),text_of(r[3])) for r in rows]==expected
    assert all(r[0].tag==XH+'th' and r[0].get('scope')=='row' for r in rows)


def validate_recap_bridge(bridge):
    ids=ids_of(bridge);assert bridge.get('id')=='B018-bridge'
    sections=[n.get('id') for n in bridge.findall(XH+'section')]
    assert sections==['B018-K1','B018-K2','B018-K3','B018-K4','B018-selfcheck'], 'B018 compact support sections/order'
    details=list(bridge.iter(XH+'details'))
    assert [n.get('id') for n in details]==['B018-S01','B018-S02','B018-S03'], 'B018 three reused-example self-checks'
    k1=ids['B018-K1'];strong=[text_of(n) for n in k1.iter(XH+'strong')]
    assert strong==['+','3+4','మూడు ప్లస్ నాలుగు','మూడు, నాలుగు అనే సంఖ్యల మొత్తం',
        'ఈ లెక్క అదనపు వివరణ:','3+4=7'], 'B018 result-name versus optional value'
    k2=ids['B018-K2']
    require(k2,['a+0=a','0+a=a','0+0=0','47+0=47','0+47=47','a+b=b+a',
        '18+25=43','25+18=43','81+25=106','43 కాదు'], 'B018 identity/commutation support')
    require(k2,['సంఖ్యలోని అంకెలను తిప్పవచ్చని చెప్పదు','అధికారిక ప్రాంతీయ పరిభాషగా ధృవీకరించబడినట్లు చూపడం లేదు'],
            'B018 property limits')
    expected_rows=[('మొదటి కలిపే సంఖ్య 38','3','8',XH+'th','row'),
                   ('రెండవ కలిపే సంఖ్య 27','2','7',XH+'th','row'),
                   ('మొత్తం 65','6','5',XH+'th','row')]
    bridge_table(ids['B018-K3'],expected_rows)
    require(ids['B018-K3'],['38+27=65','1 పదిని మరోసారి అదనంగా కలపకూడదు',
        '“9 కంటే ఎక్కువ” అనే మాటను “10 కంటే ఎక్కువ”గా మార్చకండి','సరిగ్గా 10 వచ్చినప్పుడూ బదిలీ అవసరమే'],
        'B018 aligned algorithm/exact10')
    require(ids['B018-K4'],['8+2=10','1 పది, 0 ఒకట్లు','9+0=9','బదిలీ లేదు',
        '18+29+37+46=130','8+9+7+6=30','0 ఒకట్లు రాసి 3 పదులు','1+2+3+4+3=13'],
        'B018 zero/carry greater than1')
    expected=Counter({'3+4=7':1,'47+0=47':2,'0+47=47':2,'0+0=0':1,
        '18+25=43':2,'25+18=43':2,'81+25=106':1,'8+7=15':2,'3+2+1=6':2,
        '38+27=65':1,'8+2=10':1,'9+0=9':1,'18+29+37+46=130':1,
        '8+9+7+6=30':1,'1+2+3+4+3=13':1})
    actual=Counter(displayed_relations(bridge))
    assert actual==expected and sum(actual.values())==21, 'B018 all displayed numeric equalities'
    for formula in ('a+0=a','0+a=a','a+b=b+a'):
        assert text_of(k2).count(formula)==1, 'B018 exact symbolic property occurrence'
    answers={
        'B018-S01':['మూడు ప్లస్ నాలుగు','మూడు, నాలుగు అనే సంఖ్యల మొత్తం','7','మూల పట్టికలో పేరే ఉంది'],
        'B018-S02':['47+0=47','0+47=47','18+25=43','25+18=43','అంకెలను మార్చడానికి అనుమతి కాదు'],
        'B018-S03':['8+7=15','1 పది, 5 ఒకట్లు','3+2+1=6','65','10 ఒకట్లు','9వచ్చినప్పుడు బదిలీ లేదు','30ఒకట్లు వస్తే3పదులు'],
    }
    for ident,phrases in answers.items():require(ids[ident],phrases,'B018 complete self-check answer')
    links=[n.get('href') for n in bridge.iter(XH+'a')]
    assert links==['#eip-id1170324017502','TE-B013.html#fs-id2601285','TE-B015.html#fs-id1385496',
        'TE-B017.html#B017-S-D02','TE-B017.html#B017-tryits','#B018-K1','#B018-K2','#B018-K3','#B018-K4'], 'B018 exact earlier-unit/selfcheck routes'
    assert len(ids)==11 and len(links)==9
    require(ids['B018-boundary'],['మూల recap తరువాత అభ్యాస ప్రశ్నల విభాగం ఇంకా ఉంది',
        'ప్రతి పాఠానికి జరిగిన సమీక్ష స్థితి వేరుగా నమోదు అవుతుంది'], 'B018 continuation boundary')
    require(ids['B018-disclosure'],['మొత్తం అధ్యాయం, పుస్తకం లేదా పూర్తి భాషా కేటాయింపు ముగిసిందని అనుకోకండి'],
            'B018 assignment-completion boundary')
    return {'bridge_sections':len(sections),'bridge_self_checks':len(details),
            'bridge_numeric_equalities':sum(actual.values()),'bridge_ids':len(ids),'bridge_links':len(links)}


def validate_b018(target,bridge):
    result=validate_recap_target(target);result.update(validate_recap_bridge(bridge));return result
