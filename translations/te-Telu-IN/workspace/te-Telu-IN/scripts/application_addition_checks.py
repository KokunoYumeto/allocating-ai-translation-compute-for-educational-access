"""Finite B017 application-addition checks against actual source and answers.

Read-only integer mathematics, dimensional labels and finite source structure.
Not a general Telugu parser, native-speaker approval, or a diagram scale claim.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET

from naming_checks import text_of

BASE = Path(__file__).resolve().parents[1]
CN = '{http://cnx.rice.edu/cnxml}'
MATH = '{http://www.w3.org/1998/Math/MathML}'
XH = '{http://www.w3.org/1999/xhtml}'
SVG = '{http://www.w3.org/2000/svg}'
SOURCE_SHA = '749a7764e3df7024919ddf26db57a6ad1c6628aa8b44929a204527d58ea746cf'
TABLES = {'eip-id1168288617772': (3, 5, 2), 'eip-id1168289453960': (3, 6, 2)}
URLS = ('https://www.openstax.org/l/24add2blocks',
        'https://www.openstax.org/l/24add3blocks',
        'https://www.openstax.org/l/24addwhlnumb')
# exercise, original solution, ordered quantities, result, canonical unit
NUMERIC_CASES = (
    ('fs-id1899571', 'fs-id1944399', (87,93,68,95,89), 432, 'points'),
    ('fs-id1564459', 'fs-id2146653', (18,15,26,49,32), 140, 'miles'),
    ('fs-id1761942', 'fs-id2296132', (230,165,325), 720, 'students'),
)
PERIMETER_IDS = (('fs-id1628979','fs-id1568241',26,'feet'),
                 ('fs-id2483376','fs-id2284683',30,'inches'),
                 ('fs-id2427950','fs-id2136690',36,'inches'))
# Traversals below were independently reconciled to all three actual original
# image pixels on 2026-09-01; localized SVG topology remains a separate check.
PERIMETER_EDGES = {'fs-id1628979':(4,6,2,3,2,9),
                   'fs-id2483376':(4,9,4,3,2,3,2,3),
                   'fs-id2427950':(2,12,6,4,2,4,2,4)}
PRACTICE = {'D01':((12,18,15),'పుస్తకాలు'), 'R01':((16,14,20),'పాయింట్లు'),
            'D02':((18,29,37,46),'పాయింట్లు'), 'R02':((29,38,47,56),'పాయింట్లు'),
            'D03':((6,4,6,4),'అంగుళాలు'), 'R03':((7,3,7,3),'అడుగులు')}
NUM = r'(?:0|[1-9][0-9]*)'
ADDITION = NUM + r'(?:\s*\+\s*' + NUM + r')+'
EXPRESSION = NUM + r'(?:\s*[+×]\s*' + NUM + r')*'
RELATION = re.compile(r'(?<![0-9A-Za-z_.,])' + EXPRESSION + r'(?:\s*=\s*' + EXPRESSION + r')+(?![0-9]|,[0-9]|\.[0-9])')
DIAGRAMS = {
    'fs-id588598': ('CNX_BMath_Figure_01_02_002.te.svg',(9,2,3,2,6,4),26,'feet'),
    'fs-id2175999': ('CNX_BMath_Figure_01_02_003.te.svg',(9,4,3,2,3,2,3,4),30,'inches'),
    'fs-id1381557': ('CNX_BMath_Figure_01_02_004.te.svg',(12,6,4,2,4,2,4,2),36,'inches'),
}


def ids_of(root):
    elements = [n for n in root.iter() if n.get('id')]
    result = {n.get('id'):n for n in elements}
    assert len(result) == len(elements), 'Duplicate B017 ID'
    return result


def compact(value):
    return re.sub(r'\s+', '', value)


def require(node_or_text, phrases, context):
    value = node_or_text if isinstance(node_or_text,str) else text_of(node_or_text)
    for phrase in phrases:
        assert phrase in value, context + ': missing/changed ' + phrase


def addends(value):
    assert re.fullmatch(ADDITION,value.strip()), 'B017 addition expression shape changed'
    return tuple(map(int,re.split(r'\s*\+\s*',value.strip())))


def equality(value):
    match = re.fullmatch(r'(' + ADDITION + r')\s*=\s*(' + NUM + r')', value.strip())
    assert match, 'B017 equality shape changed'
    nums, total = addends(match[1]), int(match[2])
    assert sum(nums) == total, 'B017 incorrect displayed equality: ' + value
    return nums,total


def evaluate(value):
    assert re.fullmatch(EXPRESSION,value.strip()), 'B017 unsupported integer expression'
    total=0
    for term in re.split(r'\s*\+\s*',value.strip()):
        product=1
        for factor in re.split(r'\s*×\s*',term):product*=int(factor)
        total+=product
    return total


def checked_relation(value):
    sides=re.split(r'\s*=\s*',value.strip())
    assert len(sides)==2 and evaluate(sides[0])==evaluate(sides[1]), 'B017 incorrect/changed displayed relation: '+value
    return compact(value)


def displayed_relations(root):
    result=[];blocks={'p','li','td','dd'}
    for node in root.iter():
        if node.tag.rsplit('}',1)[-1] not in blocks:continue
        if any(n is not node and n.tag.rsplit('}',1)[-1] in blocks for n in node.iter()):continue
        result.extend(checked_relation(m.group()) for m in RELATION.finditer(text_of(node)))
    return result


def formula(numbers):
    return '+'.join(map(str,numbers))+'='+str(sum(numbers))


def column_steps(numbers):
    """Actual digits + incoming carry, written digit and next-place carry count."""
    assert len(numbers) >= 2 and all(type(n) is int and n >= 0 for n in numbers)
    unit, carry, result = 1, 0, []
    while unit <= max(numbers) or carry:
        digits = tuple(n // unit % 10 for n in numbers)
        total = sum(digits) + carry
        result.append((unit,digits,carry,total,total%10,total//10))
        carry = total//10;unit *= 10
    if not result:
        result.append((1,tuple(0 for _ in numbers),0,0,0,0))
    assert sum(row[4]*row[0] for row in result) == sum(numbers)
    return tuple(result)


def protected_math_signature(root, target=False):
    """Only the two source mtext 'and' tokens may become Telugu 'మరియు'."""
    result=[]
    for math in root.iter(MATH+'math'):
        tokens=[]
        for node in math.iter():
            value=node.text
            if target and node.tag==MATH+'mtext' and value=='మరియు':value='and'
            tokens.append((node.tag,tuple(sorted(node.attrib.items())),value,
                           None if node is math else node.tail,len(node)))
        result.append(tokens)
    return result


def source_cases():
    raw=(BASE/'sources/TE-B017.en.cnxml').read_bytes()
    assert sha256(raw).hexdigest()==SOURCE_SHA, 'B017 frozen source changed'
    source=ET.fromstring(raw);ids=ids_of(source)
    assert (len(list(source.iter())),len(ids),len(list(source.iter(MATH+'math'))))==(210,46,16)
    assert [n.text for n in source.iter(MATH+'mtext')]==['and','____','and','base-10','base-10']
    assert [n.get('id') for n in source.iter(CN+'exercise')]==[x[0] for x in NUMERIC_CASES]+[x[0] for x in PERIMETER_IDS]
    for ident,sid,numbers,total,unit in NUMERIC_CASES:
        ex=ids[ident];problem=ex.find(CN+'problem')
        assert tuple(int(n.text) for n in problem.iter(MATH+'mn'))==numbers
        assert sum(numbers)==total
        assert ex.find(CN+'solution').get('id')==sid
        require(ids[sid],[str(total)+' '+unit], 'B017 source answer unit')
    require(ids['fs-id1746953'],['Hao','five tests of the semester','total number of points'], 'B017 source requested quantity')
    require(ids['fs-id1919047'],['last week','18 miles on Monday','15 miles on Wednesday',
                               '26 miles on Friday','49 miles on Saturday','32 miles on Sunday'], 'B017 source day/distance association')
    require(ids['fs-id2295551'],['Lincoln Middle School has three grades','total number of students'], 'B017 source school quantity')
    for ident,sid,total,unit in PERIMETER_IDS:
        assert ids[ident].find(CN+'solution').get('id')==sid
        require(ids[sid],[str(total)+' '+unit], 'B017 source perimeter answer')
    for ident,(declared,count,width) in TABLES.items():
        table=ids[ident]
        assert table.find(CN+'tgroup').get('cols')==str(declared)
        rows=table.findall('.//'+CN+'row')
        assert len(rows)==count and all(len(r)==width for r in rows)
    table=ids['eip-id1168288617772'];rows=table.findall('.//'+CN+'row')
    assert addends(text_of(rows[1][1]))==NUMERIC_CASES[0][2]
    assert not text_of(rows[2][1])
    require(rows[4][1],['Hao earned a total of 432 points.'], 'B017 answer sentence')
    assert hao_frame(rows[3][1])==((87,93,68,95,89),3,432)
    table=ids['eip-id1168289453960'];rows=table.findall('.//'+CN+'row')
    patio=addends(text_of(rows[2][1]))
    assert patio==(4,6,2,3,2,9) and sum(patio)==int(text_of(rows[3][1]))==26
    assert not text_of(rows[0][1]) and not text_of(rows[4][1])
    assert tuple(n.get('url') for n in source.iter(CN+'link'))==URLS
    return source,NUMERIC_CASES


def hao_frame(node):
    """Read base87 separately from the raised carry3; never flatten it to837."""
    table=node.find('.//'+MATH+'mtable')
    assert table is not None
    rows=list(table)
    assert len(rows)==9 and all(r.tag==MATH+'mtr' for r in rows)
    assert all(len(r)==0 for r in rows[:3]), 'B017 source blank layout rows changed'
    first=rows[3].find(MATH+'mtd');carry=first.find(MATH+'mover')
    assert carry is not None and len(carry)==2
    assert carry[0].tag==carry[1].tag==MATH+'mn' and carry[1].get('mathsize')=='small'
    base=int(carry[0].text+first.find(MATH+'mn').text)
    operands=[base]
    for row in rows[4:8]:
        operands.append(int(next(row.iter(MATH+'mn')).text))
    total=int(next(rows[8].iter(MATH+'mn')).text)
    actual_carry=int(carry[1].text)
    assert sum(operands)==total and sum(n%10 for n in operands)//10==actual_carry, 'B017 actual raised carry/result'
    assert carry[0].text=='8' and base==87, 'B017 raised carry target must be first addend tens'
    return tuple(operands),actual_carry,total


def structure(root):
    translated={'alt','summary','aria-label','{http://www.w3.org/XML/1998/namespace}lang'}
    result=[]
    for node in root.iter():
        omit=translated|({'src','mime-type'} if node.tag==CN+'image' else set())
        result.append((node.tag,tuple(sorted((k,v) for k,v in node.attrib.items() if k not in omit)),len(node)))
    return result


def svg_geometry(svg, lengths, perimeter, unit):
    """Validate one actual code-native redraw without assuming visual scale."""
    assert svg.tag == SVG+'svg' and svg.get('role') == 'img' and svg.get('aria-labelledby') == 'title desc'
    view = tuple(map(int,svg.get('viewBox','').split()))
    assert len(view) == 4 and view[:2] == (0,0) and view[2:] == (int(svg.get('width')),int(svg.get('height')))
    title=svg.find(SVG+'title');desc=svg.find(SVG+'desc');metadata=svg.find(SVG+'metadata')
    assert title is not None and title.get('id')=='title' and 'చుట్టుకొలత' in text_of(title)
    assert desc is not None and desc.get('id')=='desc' and 'Closed' in text_of(desc)
    assert metadata is not None and 'No answer is inserted' in text_of(metadata)
    boundary=[n for n in svg.iter(SVG+'polygon') if n.get('data-role')=='boundary']
    assert len(boundary)==1
    points=tuple(tuple(map(int,p.split(','))) for p in boundary[0].get('points','').split())
    assert len(points)==len(lengths) and len(set(points))==len(points), 'B017 SVG boundary vertex coverage'
    pixels=[]
    for first,second in zip(points,points[1:]+points[:1]):
        dx,dy=abs(second[0]-first[0]),abs(second[1]-first[1])
        assert (dx==0) != (dy==0), 'B017 SVG boundary must be orthogonal/nonzero'
        pixels.append(dx+dy)
    scales={p//n for p,n in zip(pixels,lengths) if p%n==0}
    assert len(scales)==1 and next(iter(scales))>0 and tuple(p//next(iter(scales)) for p in pixels)==lengths, 'B017 SVG edge geometry/length mismatch'
    labels=[n for n in svg.iter(SVG+'text') if n.get('data-role')=='side-label']
    assert len(labels)==len(lengths)
    assert [(int(n.get('data-edge')),int(n.get('data-length')),text_of(n)) for n in labels] == [
        (i,value,str(value)) for i,value in enumerate(lengths,1)], 'B017 SVG displayed edge labels/order'
    for label in labels:
        assert 0<=float(label.get('x'))<=view[2] and 0<=float(label.get('y'))<=view[3]
    note=[n for n in svg.iter(SVG+'text') if n.get('data-role')=='unit-note']
    assert len(note)==1
    if unit=='feet':require(note[0],['అడుగు','feet'],'B017 SVG feet unit note')
    else:require(note[0],['అంగుళా','inches'],'B017 SVG inches unit note')
    value=' '.join(svg.itertext())
    assert 'The answer is not shown' in value and str(perimeter) not in value, 'B017 SVG must not display problem answer'
    assert sum(lengths)==perimeter
    return {'vertices':len(points),'perimeter':perimeter,'unit':unit}


def validate_diagram_assets():
    manifest=json.loads((BASE/'assets/B017/manifest.json').read_text(encoding='utf-8'))
    assert manifest['unit']=='TE-B017' and manifest['source_subsection_sha256']==SOURCE_SHA
    assert manifest['qa']['source_media_count']==manifest['qa']['localized_asset_count']==3
    assert manifest['qa']['originals_preserved'] is True and manifest['qa']['answer_not_in_problem_svg'] is True
    assets={a['media_id']:a for a in manifest['assets']}
    assert set(assets)==set(DIAGRAMS) and len(assets)==3
    result=[]
    for media,(filename,lengths,total,unit) in DIAGRAMS.items():
        asset=assets[media]
        assert Path(asset['localized_path']).name==filename
        assert tuple(asset['source_side_lengths_clockwise_from_top'])==lengths
        assert asset['verified_perimeter_not_displayed']==total
        for key,digest in [('original_path','original_sha256'),('localized_path','localized_sha256')]:
            path=(BASE/asset[key]).resolve();assert path.is_relative_to(BASE.resolve()) and path.is_file()
            assert sha256(path.read_bytes()).hexdigest()==asset[digest], 'B017 asset bytes changed'
        result.append(svg_geometry(ET.parse(BASE/asset['localized_path']).getroot(),lengths,total,unit))
    return tuple(result)


def validate_application_target(target):
    """Direct target content checks; final integration also checks image geometry."""
    source,cases=source_cases();ids=ids_of(target)
    assert structure(source)==structure(target), 'B017 source structure/attributes changed'
    assert protected_math_signature(source)==protected_math_signature(target,target=True), 'B017 protected MathML changed'
    assert [n.text for n in target.iter(MATH+'mtext')]==['మరియు','____','మరియు','base-10','base-10'], 'B017 exact MathML conjunction exceptions'
    require(ids['fs-id2926269'],['మొదట సమస్యను చదివి, ఏమి కనుక్కోవాలో గుర్తించాలి',
            'సమాచారాన్ని మాటల్లో రాయాలి','గణిత సంకేతాలతో రాసి, విలువ కనుక్కోవాలి',
            'జవాబును ఒక వాక్యంగా రాయాలి'], 'B017 requested application stages')
    require(ids['fs-id1746953'],['ఈ సెమిస్టర్‌లో జరిగిన ఐదు పరీక్షల్లో హావో పొందిన పాయింట్లు',
            'ఆ ఐదు పరీక్షల్లో అతను పొందిన మొత్తం పాయింట్లు'], 'B017 Hao quantity/context')
    require(ids['fs-id1919047'],['మార్క్ సైకిల్ పోటీ కోసం శిక్షణ తీసుకుంటున్నాడు','గత వారం',
            'సోమవారం 18 మైళ్లు','బుధవారం 15 మైళ్లు','శుక్రవారం 26 మైళ్లు',
            'శనివారం 49 మైళ్లు','ఆదివారం 32 మైళ్లు','మొత్తం దూరం ఎన్ని మైళ్లు'], 'B017 day/distance units')
    assert text_of(ids['fs-id1390222'])=='అతను 140 మైళ్లు సైకిల్ తొక్కాడు.', 'B017 actual Mark answer/unit'
    require(ids['fs-id2295551'],['లింకన్ మిడిల్ స్కూల్‌లో మూడు తరగతి స్థాయులు','విద్యార్థుల సంఖ్యలు వరుసగా',
            'మొత్తం విద్యార్థులు ఎంతమంది'], 'B017 school count/context')
    assert text_of(ids['fs-id1931675'])=='మొత్తం 720 మంది విద్యార్థులు ఉన్నారు.', 'B017 actual student answer/unit'
    require(ids['fs-id2703969'],['మనం కలిపినవి పాయింట్లు కాబట్టి మొత్తం 432 పాయింట్లు',
            'తగిన ప్రమాణాలను కూడా పేర్కొనడం ముఖ్యం'], 'B017 answer-unit principle')
    require(ids['fs-id2594070'],['మూసుకున్న సరిహద్దు గల జ్యామితీయ ఆకారం',
            'సరిహద్దు వెంబడి ఉన్న మొత్తం దూరాన్ని చుట్టుకొలత',
            'భుజాలు గల ఆకారం చుట్టుకొలత దాని భుజాల పొడవుల మొత్తం'], 'B017 perimeter is boundary length')
    assert text_of(ids['fs-id1357069'])=='చుట్టుకొలత 30 అంగుళాలు.', 'B017 actual figure003 answer/unit'
    assert text_of(ids['fs-id1613173'])=='చుట్టుకొలత 36 అంగుళాలు.', 'B017 actual figure004 answer/unit'
    for ident in ('fs-id1365334','fs-id1884028'):
        assert text_of(ids[ident])=='ఆకారం చుట్టుకొలత కనుక్కోండి. పొడవులన్నీ అంగుళాల్లో ఉన్నాయి.', 'B017 requested perimeter units'
    hao=ids['eip-id1168288617772'];rows=hao.findall('.//'+CN+'row')
    assert text_of(rows[0][1])=='పరీక్షల్లో పొందిన పాయింట్ల మొత్తం', 'B017 point total phrase'
    assert text_of(rows[4][1])=='హావో మొత్తం 432 పాయింట్లు పొందాడు.', 'B017 actual Hao answer sentence'
    assert hao_frame(rows[3][1])==((87,93,68,95,89),3,432)
    require(hao.get('summary',''),['ఐదు అడ్డ వరుసలు, రెండు నిలువు వరుసల','నిలువుగా కలిపి 432',
            'మొత్తం 432 పాయింట్లు'], 'B017 Hao accessible table meaning')
    assert re.findall(r'\d+',hao.get('summary',''))==['87','93','68','95','89','432','432'], 'B017 Hao summary quantities'
    patio=ids['eip-id1168289453960'];rows=patio.findall('.//'+CN+'row')
    assert text_of(rows[1][1])=='భుజాల పొడవుల మొత్తం', 'B017 perimeter must sum lengths, not number of sides'
    assert text_of(rows[5][0])=='అడుగుల్లో ఉన్న పొడవులను కలిపాం కాబట్టి మొత్తం 26 అడుగులు.', 'B017 patio dimensional sum/unit'
    assert text_of(rows[5][1])=='ఆరుబయటి ప్రదేశం చుట్టుకొలత 26 అడుగులు.', 'B017 patio answer/unit'
    require(patio.get('summary',''),['ఆరు అడ్డ వరుసలు, రెండు నిలువు వరుసల','భుజాల పొడవుల మొత్తాన్ని',
            'చుట్టుకొలత 26 అడుగులు'], 'B017 patio accessible table meaning')
    assert re.findall(r'\d+',patio.get('summary',''))==['4','6','2','3','2','9','26','26'], 'B017 patio summary quantities'
    for table in (hao,patio):
        for row in table.findall('.//'+CN+'row'):
            first=text_of(row[0])
            if first.startswith('గణిత సంకేతాలతో'):
                assert first=='గణిత సంకేతాలతో రాయండి.', 'B017 expression stage label'
    links=list(target.iter(CN+'link'))
    assert tuple(n.get('url') for n in links)==URLS, 'B017 source resource href changed'
    expected=['రెండు అంకెల సంఖ్యల సంకలనం: base-10 బ్లాకులతో',
              'మూడు అంకెల సంఖ్యల సంకలనం: base-10 బ్లాకులతో','పూర్ణాంకాల సంకలనం']
    assert [text_of(n) for n in links]==expected, 'B017 resource label/source association'
    # Asset paths are checked against the actual pinned manifest, not fabricated
    # placeholders merely to allow the shared localization path to run.
    manifest=json.loads((BASE/'assets/B017/manifest.json').read_text(encoding='utf-8'))
    assert manifest['unit']=='TE-B017' and manifest['source_subsection_sha256']==SOURCE_SHA
    assets=manifest['assets'];assert len(assets)==3
    mapping={a['original_src']:a for a in assets};assert len(mapping)==3
    for original,image in zip(source.iter(CN+'image'),target.iter(CN+'image')):
        asset=mapping[original.get('src')]
        assert image.get('src')==asset['localized_path'] and image.get('mime-type')=='image/svg+xml', 'B017 source/localized image mapping'
        for key,hashkey in [('original_path','original_sha256'),('localized_path','localized_sha256')]:
            path=(BASE/asset[key]).resolve();assert path.is_relative_to(BASE.resolve())
            assert sha256(path.read_bytes()).hexdigest()==asset[hashkey], 'B017 asset bytes changed'
    validate_diagram_assets()
    return cases


def bridge_column_table(node,numbers):
    tables=list(node.iter(XH+'table'));assert len(tables)==1, 'B017 one carry table per selected case'
    table=tables[0]
    assert [text_of(n) for n in table.findall(XH+'thead/'+XH+'tr/'+XH+'th')]==[
        'స్థానం','నిలువు వరుస లెక్క','ఈ స్థానంలో రాసే అంకె','తరువాతి స్థానానికి బదిలీ'], 'B017 carry table column roles'
    rows=table.findall(XH+'tbody/'+XH+'tr');steps=column_steps(numbers)
    assert len(rows)==len(steps)==3 and all(len(row)==4 for row in rows), 'B017 carry table complete place coverage'
    places={1:'ఒకట్లు',10:'పదులు',100:'వందలు'}
    actual=[]
    for row,(unit,digits,incoming,total,written,carry) in zip(rows,steps):
        assert row[0].tag==XH+'th' and row[0].get('scope')=='row' and text_of(row[0])==places[unit], 'B017 carry target place changed'
        operands=digits+((incoming,) if incoming else ())
        assert equality(text_of(row[1]))==(operands,total), 'B017 actual column digits/incoming carry changed'
        assert text_of(row[2])==str(written), 'B017 actual written digit changed'
        if unit==1:expected=f'{carry} '+('పది' if carry==1 else 'పదులు')
        elif unit==10:expected=f'{carry} '+('వంద' if carry==1 else 'వందలు')
        else:expected='0 వేల ప్రమాణాలు; ఇక బదిలీ లేదు';assert carry==0
        assert text_of(row[3])==expected, 'B017 carry count/destination changed'
        actual.append(formula(operands))
    return actual


def _answer(node,numbers,sentence):
    strong=[text_of(n) for n in node.iter(XH+'strong')]
    assert len(strong)==3, 'B017 expression/equality/unit answer coverage'
    assert addends(strong[0])==numbers, 'B017 actual requested quantities/order changed'
    assert equality(strong[1])==(numbers,sum(numbers)), 'B017 actual total changed'
    assert strong[2]==sentence, 'B017 actual answer sentence/value/unit changed'
    require(node,['జవాబు:'], 'B017 answer sentence role')
    return formula(numbers)


def _sequential(numbers):
    partial=numbers[0];result=[]
    for number in numbers[1:]:
        result.append(formula((partial,number)));partial+=number
    return result


def validate_application_bridge(bridge,source):
    """Check actual bridge arithmetic, labels and routes; image checks separate."""
    ids=ids_of(bridge);assert bridge.get('id')=='B017-bridge'
    source_details={
        'B017-W-fs-id1899571':((87,93,68,95,89),'హావో మొత్తం 432 పాయింట్లు పొందాడు.'),
        'B017-S-fs-id1564459':((18,15,26,49,32),'మార్క్ గత వారం మొత్తం 140 మైళ్లు సైకిల్ తొక్కాడు.'),
        'B017-S-fs-id1761942':((230,165,325),'లింకన్ మిడిల్ స్కూల్‌లో మొత్తం 720 మంది విద్యార్థులు ఉన్నారు.'),
        'B017-W-fs-id1628979':(PERIMETER_EDGES['fs-id1628979'],'ఆరుబయటి ప్రదేశం చుట్టుకొలత 26 అడుగులు.'),
        'B017-S-fs-id2483376':(PERIMETER_EDGES['fs-id2483376'],'చుట్టుకొలత 30 అంగుళాలు.'),
        'B017-S-fs-id2427950':(PERIMETER_EDGES['fs-id2427950'],'చుట్టుకొలత 36 అంగుళాలు.'),
    }
    practice_sentences={'D01':'మొత్తం 45 పుస్తకాలు ఉన్నాయి.','R01':'జట్టు మొత్తం 50 పాయింట్లు పొందింది.',
        'D02':'మొత్తం 130 పాయింట్లు.','R02':'మొత్తం 170 పాయింట్లు.',
        'D03':'చుట్టుకొలత 20 అంగుళాలు.','R03':'చుట్టుకొలత 20 అడుగులు.'}
    expected_ids=set(source_details)|{'B017-S-'+ident for ident in PRACTICE}
    details=list(bridge.iter(XH+'details'))
    assert len(details)==12 and {n.get('id') for n in details}==expected_ids, 'B017 complete solution details'
    expected=Counter()
    for ident,(numbers,sentence) in source_details.items():
        node=ids[ident]
        assert [n.get('href') for n in node.iter(XH+'a')]==['#'+ident.split('-',2)[2]], 'B017 exact source backlink'
        expected.update([_answer(node,numbers,sentence)])
    for ident,(numbers,unit) in PRACTICE.items():
        node=ids['B017-S-'+ident]
        expected.update([_answer(node,numbers,practice_sentences[ident])])
        question=ids['B017-'+ident]
        require(question,[', '.join(map(str,numbers))+' '+unit if ident not in {'D02','R02'} else 'పాయింట్లు '+', '.join(map(str,numbers)),
                          'చుట్టుకొలత కనుక్కోండి' if ident.endswith('03') else ('మొత్తం పుస్తకాలు' if ident=='D01' else 'మొత్తం పాయింట్లు')], 'B017 actual practice question/units')
        assert [n.get('href') for n in question.iter(XH+'a')]==['#B017-S-'+ident], 'B017 practice answer route'
    carry_cases={'B017-W-fs-id1899571':NUMERIC_CASES[0][2],
                 'B017-S-fs-id1564459':NUMERIC_CASES[1][2],
                 'B017-S-fs-id1761942':NUMERIC_CASES[2][2],
                 'B017-S-D02':PRACTICE['D02'][0], 'B017-S-R02':PRACTICE['R02'][0]}
    for ident,numbers in carry_cases.items():expected.update(bridge_column_table(ids[ident],numbers))
    extra={
        'B017-W-fs-id1899571':[(87,93),(68,95),(180,163,89)],
        'B017-S-fs-id1564459':[(18,32),(15,26,49),(50,90)],
        'B017-S-fs-id1761942':[(165,325),(490,230)],
        'B017-W-fs-id1628979':[(9,2,3,2,6,4)],
        'B017-S-fs-id2483376':[(4,4),(3,3,3),(2,2),(8,9,4,9)],
        'B017-S-fs-id2427950':[(2,2,2),(4,4,4),(6,12,12,6)],
        'B017-S-D01':[(12,18),(30,15)], 'B017-S-R01':[(16,14),(30,20)],
        'B017-S-D02':[(18,29),(37,46),(47,83)], 'B017-S-R02':[(29,56),(38,47),(85,85)],
        'B017-S-D03':[(6,4),(10,10)], 'B017-S-R03':[(7,3),(10,10)],
    }
    for ident,pairs in extra.items():expected.update(formula(p) for p in pairs)
    for ident,edges in PERIMETER_EDGES.items():expected.update(_sequential(edges))
    expected.update(['12+18+15=45','32=30+2','3×10=30'])
    for ident in expected_ids:
        numbers=(source_details[ident][0] if ident in source_details else PRACTICE[ident.removeprefix('B017-S-')][0])
        local_expected=Counter([formula(numbers)])
        local_expected.update(formula(p) for p in extra[ident])
        if ident in carry_cases:local_expected.update(bridge_column_table(ids[ident],numbers))
        exid=ident.split('-',2)[2]
        if exid in PERIMETER_EDGES:local_expected.update(_sequential(numbers))
        assert Counter(displayed_relations(ids[ident]))==local_expected, 'B017 case-specific checking equations changed'
    critical={
        'B017-context':['miles అంటే మైళ్లు, feet అంటే అడుగులు, inches అంటే అంగుళాలు',
            'కిలోమీటర్లు లేదా సెంటీమీటర్లుగా మార్చడం లేదు','పరీక్షల పాయింట్ల మొత్తం శాతం లేదా సగటు కాదు',
            'ఏ తరగతి సంఖ్యలుగా అనుకోవాలో మూలం చెప్పలేదు'],
        'B017-K1':['సమస్యలో కనిపించిన ప్రతి సంఖ్యను విచక్షణ లేకుండా కలపకండి',
            'ఒకే ప్రమాణంలో ఉన్న','పూర్తి వాక్యం రాయండి'],
        'B017-K2':['3 పదులు, 2 ఒకట్లు','ఒకట్ల స్థానంలో 2 రాసి, పదుల స్థానానికి 3 పదులను',
            '3 ఇక్కడ 3 ఒకట్లు కాదు','దాని విలువ 3×10=30','43 పదులైతే, అది 4 వందలు, 3 పదులు',
            'వందల స్థానానికి 4 వందలను','140లో ఒకట్ల స్థానంలో 0 ఉండాలి; 14 అని రాయకండి',
            'అసలు మొత్తానికి మరోసారి అదనంగా కలపకండి'],
        'B017-K3':['మూసుకున్న ఆకారం సరిహద్దు వెంబడి ఒక పూర్తి చుట్టు తిరిగి రావడానికి ప్రయాణించవలసిన మొత్తం దూరం',
            'సరిహద్దు భుజాల పొడవులను ఒక్కొక్కసారి కలపాలి',
            'చిన్న భుజాలూ సరిహద్దులో భాగమే; వాటిని వదిలేయకండి','ప్రారంభ మూలకు చేరగానే ఆపండి',
            'భుజాల సంఖ్యను లెక్కించడం, వాటి పొడవులను కలపడం వేరు','చదరపు అడుగులు లేదా చదరపు అంగుళాలు కాదు',
            'ఇచ్చిన లేబుళ్లను వాడండి','లేబుల్ లేని కొత్త రేఖలు ఊహించి కలపకండి'],
        'B017-W-fs-id1899571':['పరీక్షల సంఖ్య 5ను మరో పాయింట్ల పరిమాణంగా కలపకూడదు',
            '87లోని 8 పైన ఉన్న చిన్న 3, ఒకట్ల నుంచి వచ్చిన 3 పదులు','అది భిన్నం కాదు',
            '4 వందలు, 3 పదులు, 2 ఒకట్లు','సగటు లేదా శాతం అడగలేదు'],
        'B017-S-fs-id1564459':['సోమవారం 18, బుధవారం 15, శుక్రవారం 26, శనివారం 49, ఆదివారం 32 మైళ్లు',
            '1 వంద, 4 పదులు, 0 ఒకట్లు','మంగళవారం, గురువారం దూరాలను సమస్య ఇవ్వలేదు',
            'తప్పనిసరిగా 0 అని ఊహించి చేర్చడం లేదు','140 కిలోమీటర్లు అని ప్రమాణాన్ని మార్చకండి'],
        'B017-S-fs-id1761942':['మరో 3 మంది విద్యార్థుల పరిమాణం కాదు','7 వందలు, 2 పదులు, 0 ఒకట్లు',
            '720 తరగతులు అని రాయకండి'],
        'B017-W-fs-id1628979':['ఆరు సరిహద్దు భుజాల పొడవులు అన్నీ అడుగుల్లో','లోపలి వైశాల్యం కాదు',
            'ఎడమ భుజం, కింది భుజం, లోపలి మలుపులోని 2 అడుగుల భుజం, 3 అడుగుల భుజం, కుడి 2 అడుగుల భుజం, పై భుజం',
            'ప్రతి భుజం ఒక్కసారి','రెండు చిన్న 2 అడుగుల భుజాలనూ కలపాలి','ఒకదాన్ని తీసివేయకూడదు'],
        'B017-S-fs-id2483376':['4, 9, 4, 3, 2, 3, 2, 3 అంగుళాలు',
            '3 అంగుళాలు ఉన్న మూడు వేర్వేరు భుజాలు, 2 అంగుళాలు ఉన్న రెండు వేర్వేరు భుజాలు',
            'చివరి 9 పై భుజం పొడవు; ముందు వచ్చిన 9 మూడు చిన్న భుజాల మొత్తం'],
        'B017-S-fs-id2427950':['2, 12, 6, 4, 2, 4, 2, 4 అంగుళాలు',
            'మూడు 2 అంగుళాల భుజాలు, మూడు 4 అంగుళాల భుజాలు, ఒక 12 అంగుళాల భుజం, ఒక 6 అంగుళాల భుజం',
            'కేవలం పై 12, కుడి 6 భుజాలను మాత్రమే కలపడం పూర్తి చుట్టు కాదు',
            'జవాబు అడుగులు లేదా చదరపు అంగుళాలు కాదు'],
        'B017-S-D01':['అదనంగా 3 పుస్తకాలు ఇచ్చినట్లు కాదు','45 అరలు అని రాసినా కోరిన పరిమాణం మారుతుంది'],
        'B017-S-R01':['3ను పాయింట్లకు అదనంగా కలపలేదు'],
        'B017-S-D02':['30 ఒకట్లు 3 పదులు, 0 ఒకట్లు','బదిలీ 3, కేవలం 1 కాదు','చివరి 0 ఒకట్ల స్థానాన్ని ఉంచుతుంది'],
        'B017-S-R02':['ఒకట్ల స్థానంలో 0 రాసి, పదుల స్థానానికి 3 పదులు','17 నుంచి 7 పదులు రాసి, 1 వంద',
            'రెండు జతలనూ కలపాలి'],
        'B017-S-D03':['4 అనేది భుజాల సంఖ్య మాత్రమే','సరిహద్దు పొడవు అడిగారు కాబట్టి అంగుళాలే సరైనవి'],
        'B017-S-R03':['D03లో 20 అంగుళాలు, ఇక్కడ 20 అడుగులు','సమాన దూరాలని అనుకోకండి'],
        'B017-resource-boundary':['ప్రస్తుత అందుబాటు, భాష లేదా కార్యాచరణను ధృవీకరించడం లేదు',
            'వాటిని పూర్తి చేశామని సూచించవు'],
    }
    for ident,phrases in critical.items():require(ids[ident],phrases,'B017 context/unit/carry/boundary meaning')
    route=ids['B017-route'].findall('.//'+XH+'tbody/'+XH+'tr')
    expected_routes=[['B017-D01','B017-K1','fs-id1761942','B017-R01'],
                     ['B017-D02','B017-K2','fs-id1899571','B017-R02'],
                     ['B017-D03','B017-K3','fs-id2483376','B017-R03']]
    assert [[n.get('href') for n in row.iter(XH+'a')] for row in route]==[
        ['#'+i for i in row] for row in expected_routes], 'B017 skill/source/recheck mapping'
    assert len(ids)==30 and len(list(bridge.iter(XH+'a')))==24, 'B017 bridge ID/link coverage'
    for link in bridge.iter(XH+'a'):
        href=link.get('href','')
        assert href.startswith('#') and href[1:] in ids_of(source).keys()|ids.keys(), 'B017 unresolved source/bridge link'
    actual=displayed_relations(bridge)
    assert len(actual)==79 and Counter(actual)==expected, 'B017 all displayed relations/ordered quantities coverage'
    return {'bridge_solution_details':len(details),'bridge_carry_tables':len(carry_cases),
            'bridge_carry_rows':15,'bridge_displayed_relations':len(actual)}


def validate_b017(target, bridge):
    """Shared-build entry point: validate actual localized target and bridge."""
    source,_=source_cases()
    cases=validate_application_target(target)
    bridge_counts=validate_application_bridge(bridge,source)
    return {'source_exercises':len(cases)+len(PERIMETER_IDS),
            'source_numeric_applications':len(cases),
            'source_perimeter_applications':len(PERIMETER_IDS),
            'localized_diagrams':len(DIAGRAMS),**bridge_counts}
