"""Non-writing tests for PDF-specific numeric stack contracts."""
import copy,json,xml.etree.ElementTree as ET
from build_new_reading_editions import L,prepare,local,stacked_rows,verify_stack,stack_layout,paragraph_style_key,plain

main,_=prepare(L/'output/m81244/index.html','m81244')
stacks=[stacked_rows(e) for e in main.iter() if local(e)=='mtable' and any(local(n)=='munder' for n in e.iter())]
assert stacks
assert any(verify_stack(rows)==432 and rows[0]['carries']==[(0,'3')] for rows in stacks)
assert any(verify_stack(rows)==112 and rows[0]['carries']==[(0,'1')] for rows in stacks)
bad=copy.deepcopy(next(rows for rows in stacks if rows[0]['carries']))
index,value=bad[0]['carries'][0];bad[0]['carries'][0]=(index,str(int(value)+1))
try:verify_stack(bad)
except AssertionError:pass
else:raise AssertionError('Wrong carry accepted')
bad=copy.deepcopy(next(rows for rows in stacks if not rows[-1]['underlined']))
bad[-1]['text']=str(verify_stack(bad)+1)
try:verify_stack(bad)
except AssertionError:pass
else:raise AssertionError('Wrong result accepted')

# Separator regression: an unpunctuated partial result must still align by
# numeric place beneath a punctuated addend, and carries follow their digit.
sample=[{'text':'21,357','carries':[(1,'1')],'underlined':False},
        {'text':'+4,271','carries':[],'underlined':True},
        {'text':'0814','carries':[],'underlined':False}]
layout=stack_layout(sample,10,3)
def digit_positions(row):
    return {sum(c.isdigit() for c in row['text'][i+1:]):x for i,(c,x) in enumerate(layout['rows'][sample.index(row)]['glyphs']) if c.isdigit()}
top=next(x for c,x in layout['rows'][0]['glyphs'] if c=='1')
partial=layout['rows'][2]['glyphs'][0][1]
assert top==partial,(top,partial)
assert layout['rows'][0]['carries'][0][0]==next(x for c,x in layout['rows'][0]['glyphs'] if c=='1')
assert paragraph_style_key(ET.fromstring('<p class="source-label"/>'),{'p':1,'label':1})=='label'
assert plain(ET.fromstring('<math><mrow><mi>a</mi><mo>+</mo><mn>0</mn><mo>=</mo><mi>a</mi></mrow></math>'))==' a+0=a '
print(json.dumps({'numeric_stacks':len(stacks),'carry_annotations':sum(len(row['carries']) for rows in stacks for row in rows),'negative_tests':2,'geometry_regressions':2,'pagination_regressions':1,'inline_math_spacing_regressions':1,'status':'pass'}))
