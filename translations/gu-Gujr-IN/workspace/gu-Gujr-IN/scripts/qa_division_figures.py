"""Independent source-bound values, chart blanks, blocks and cloud inventory."""
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from localized_a00_division import render_figure
from localized_a00_algebra_intro import render_figure as cloud

LANG=Path(__file__).resolve().parents[1]
ROOT=LANG.parent
MEDIA=ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'
r=json.loads((LANG/'translations/a00-m81256-media-and-errata.gu.json').read_text(encoding='utf-8'))
review={m['source_file']:m for m in r['media']}
S='{http://www.w3.org/2000/svg}'
rows_checked=0
cases=[('CNX_BMath_Figure_01_05_047_img-06.png',359,4,3,1439,[359,4,1436,3,1439],[(82,'2'),(104,'3')]),
       ('CNX_BMath_Figure_01_05_048_img-06.png',112,13,5,1461,[112,13,336,1120,5,1461],[]),
       ('CNX_BMath_Figure_01_05_049d_img.jpg',309,241,52,74521,[309,241,309,12360,61800,74469,52,74521],[(104,'3')])]
for file,q,d,remainder,n,expected,carry in cases:
    assert hashlib.sha256((MEDIA/file).read_bytes()).hexdigest()==review[file]['sha256']
    assert q*d+remainder==n and 0<=remainder<d
    root=ET.fromstring(render_figure(file,'તપાસ','independent'))
    svgs=root.findall('.//'+S+'svg');actual=[]
    for svg in svgs:
        digits=[e for e in svg.findall(S+'text') if e.get('font-size')=='21']
        # Decode place positions; a digit one column left is worth10 times as much.
        value=sum(int(e.text)*10**((126-int(e.get('x')))//22) for e in digits)
        assert len({e.get('x') for e in digits})==len(digits)
        actual.append(value);assert svg.get('role')=='img' and svg.get('aria-label')
        rows_checked+=1
    assert actual==expected,(file,actual)
    assert [(int(t.get('x')),t.text) for t in svgs[0].findall(S+'text') if t.get('font-size')=='14']==carry
    if d==4:assert actual[2]==q*d
    if d==13:assert actual[2:4]==[q*3,q*10]
    if d==241:assert actual[2:6]==[q,q*40,q*200,q*d]

model=ET.fromstring(render_figure('CNX_BMath_Figure_01_05_209_img.jpg','258','model'))
rects=model.findall('.//'+S+'rect');assert len(rects)==258
assert len([e for e in rects if int(e.get('x'))<172])==200
assert len([e for e in rects if 172<=int(e.get('x'))<250])==50
assert len([e for e in rects if int(e.get('x'))>=250])==8
assert [[e.text or '' for e in row] for row in model.findall('.//tbody/tr')]==[['સો','2','200'],['દશક','5','50'],['એકમ','8','8'],['','','258']]

rectangle=ET.fromstring(render_figure('CNX_BMath_Figure_01_05_213_img.jpg','લંબચોરસ','rect'))
rect=rectangle.find('.//'+S+'rect');assert int(rect.get('width'))/int(rect.get('height'))==15/8
assert sorted(t.text for t in rectangle.findall('.//'+S+'text'))==sorted(['15 ફૂટ','15 ફૂટ','8 ફૂટ','8 ફૂટ'])
triangle=ET.fromstring(render_figure('CNX_BMath_Figure_01_05_214_img.jpg','ત્રિકોણ','triangle'))
assert sorted(t.text for t in triangle.findall('.//'+S+'text'))==sorted(['5 સે.મી.','12 સે.મી.','13 સે.મી.'])
assert 216/90==12/5 and 5*5+12*12==13*13

visible=blanks=0
rendered_chart_checks=0
reader=(LANG/'output/library/a00-m81256.html').read_text(encoding='utf-8')
for table in r['source_chart_accessible_data']:
    media_id=review[table['image']]['media_id']
    fragment=re.search(r'<div id="'+re.escape(media_id)+r'" class="source-media">(.*?)<p class="figure-description">',reader,re.S)
    assert fragment is not None,table['image']
    rendered=ET.fromstring('<section>'+fragment[1]+'</section>')
    assert rendered.find('.//thead/tr/th').text==table['operation'],(table['image'],'Rendered chart operator')
    assert rendered.find('.//caption').text=={'+':'સરવાળાનું કોષ્ટક','×':'ગુણાકારનું કોષ્ટક'}[table['operation']]
    assert [int(e.text) for e in rendered.findall('.//thead/tr/th')[1:]]==table['column_headers']
    actual_rows=rendered.findall('.//tbody/tr')
    assert [int(row[0].text) for row in actual_rows]==table['row_headers']
    assert [[None if e.text is None else int(e.text) for e in row[1:]] for row in actual_rows]==table['visible_cells']
    rendered_chart_checks+=1
    for a,cells in zip(table['row_headers'],table['visible_cells']):
        for b,value in zip(table['column_headers'],cells):
            if value is None:blanks+=1;continue
            assert value==(a+b if table['operation']=='+' else a*b)
            visible+=1
assert visible==321

c=json.loads((LANG/'translations/a00-m81266-media.gu.json').read_text(encoding='utf-8'))
assert hashlib.sha256((MEDIA/c['source_file']).read_bytes()).hexdigest()==c['source_media_sha256']
root=ET.fromstring(cloud(c['source_file'],c['accessible_alt_gu'],'cloud'))
words=[s.text for s in root.findall('.//span')]
assert words==[gu for en,gu in c['figure_label_translations']] and len(words)==18
assert {'પૂર્ણ','પૂર્ણાંક','વાસ્તવિક','સંખ્યાઓ','સમીકરણ','સમીકરણો'}<=set(words)
receipt={'result':'pass','source_bound_division_redraws':6,'arithmetic_rows_checked':rows_checked,'division_remainder_identities':3,
         'countable_place_model_units':258,'visible_chart_cells_checked':visible,'chart_blanks_preserved':blanks,
         'rendered_chart_operators_captions_and_cells_checked':rendered_chart_checks,
         'word_cloud_fragments':18,'geometry_labels_checked':7,
         'limits':['Original media were visually inspected, not merely inferred from source alternatives.','Actual assistive-technology and educator review remain pending.']}
(LANG/'DIVISION_FIGURE_QA.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(receipt))
