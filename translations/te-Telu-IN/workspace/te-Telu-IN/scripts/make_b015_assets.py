"""Preserve only five pinned B015 media members; create faithful code-native SVGs.

No network, corpus extraction, source rewrite or translation-catalog changes.
--verify and --self-test are read-only.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import io
import json
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from PIL import Image
from build import atomic_write
from inspect_source import slots, CN, MATH

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parent
OUT=BASE/'assets/B015'
COMMIT='38cae454e644abf9f0a623e876994553881597c9'
SOURCE_SHA='8fc54e5e660bd66b25739144d64fd172a61da3b1407449c1ed066dde75c5034b'
MODULE_SHA='b32058ce714e5fd43b010ccc81b2ae00a11567b229e9f96dda7b85b3cd82ba6b'
ARCHIVE_SHA='effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917'
PREFIX='CNX_BMath_Figure_01_02_'
NAMES=[PREFIX+s for s in ('001.jpg','020-01.png','020-02.png','020-03.png','020-04.png')]
SVG='{http://www.w3.org/2000/svg}'


def need(value,message):
    if not value:raise ValueError(message)


def digest(data):return hashlib.sha256(data).hexdigest()


def file_digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def write(path,data):
    need(shutil.disk_usage(BASE).free>=32*1024*1024+len(data),'Free-space guard')
    path.parent.mkdir(parents=True,exist_ok=True)
    atomic_write(path,data)


def source():
    raw=(BASE/'sources/TE-B015.en.cnxml').read_bytes()
    need(digest(raw)==SOURCE_SHA,'Frozen source changed')
    meta=json.loads((BASE/'sources/TE-B015.source.json').read_text('utf-8'))
    need(meta['source_commit']==COMMIT and meta['source_sha256']==SOURCE_SHA and meta['source_module']['sha256']==MODULE_SHA and meta['text_slots']==859,'Source pin/count changed')
    root=ET.fromstring(raw)
    need(root.get('id')=='fs-id1385496' and len(list(root.iter()))==1480 and len(list(slots(root)))==859,'Source scope/count changed')
    need([Path(e.get('src')).name for e in root.iter(CN+'image')]==NAMES,'Selected image list/order changed')
    module=(ROOT/meta['source_module']['path']).read_bytes()
    need(digest(module)==MODULE_SHA,'Canonical module changed')
    selected=next(e for e in ET.fromstring(module).iter() if e.get('id')=='fs-id1385496')
    selected.tail=None
    need(ET.tostring(selected)==ET.tostring(root),'Frozen selection differs from canonical module')
    return root


def originals(write_missing=False):
    root=source()
    parents={c:p for p in root.iter() for c in p}
    lock=json.loads((BASE/'sources.lock.json').read_text('utf-8'))
    record=next(r for r in lock['canonical_archives'] if r['id']=='A00-A20-en-complete-archive')
    need(record['sha256']==ARCHIVE_SHA and record['commit']==COMMIT,'Archive lock changed')
    archive=ROOT/record['path']
    need(archive.stat().st_size==537455794 and file_digest(archive)==ARCHIVE_SHA,'Archive bytes changed')
    env=os.environ.copy()
    env.update(GIT_NO_LAZY_FETCH='1',GIT_TERMINAL_PROMPT='0')
    listing=subprocess.check_output(['git','-C',str(ROOT/'downloads/upstream-prealgebra'),'ls-tree','-z',COMMIT,'--']+['media/'+n for n in NAMES],env=env)
    blobs={}
    for row in listing.split(b'\0'):
        if not row:continue
        header,path=row.split(b'\t')
        mode,kind,blob=header.split()
        need(kind==b'blob','Not a Git blob')
        blobs[path.decode()]=blob.decode()
    need(set(blobs)=={'media/'+n for n in NAMES},'Pinned media set differs')
    assets=[]
    with zipfile.ZipFile(archive) as z:
        need(z.comment.decode()==COMMIT,'Archive comment changed')
        for image,name in zip(root.iter(CN+'image'),NAMES):
            member='osbooks-prealgebra-bundle-'+COMMIT+'/media/'+name
            info=z.getinfo(member)
            need(0<info.file_size<2_000_000,'Selected image exceeds size bound')
            data=z.read(member)
            blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            need(blob==blobs['media/'+name],'Image differs from pinned Git blob')
            destination=OUT/'original'/name
            if destination.exists():need(destination.read_bytes()==data,'Refusing original overwrite: '+name)
            elif write_missing:write(destination,data)
            else:raise FileNotFoundError(destination)
            with Image.open(io.BytesIO(data)) as opened:dimensions=list(opened.size)
            media=parents[image]
            ancestor=media
            while ancestor in parents and ancestor.tag!=CN+'figure':ancestor=parents[ancestor]
            assets.append({'original_src':image.get('src'),'original_path':destination.relative_to(BASE).as_posix(),
                'original_sha256':digest(data),'original_bytes':len(data),'original_dimensions_px':dimensions,
                'source_git_blob_sha1':blob,'source_zip_crc32':f'{info.CRC:08x}','source_zip_member':member,
                'media_id':media.get('id'),'figure_id':ancestor.get('id') if ancestor.tag==CN+'figure' else None,
                'localized_path':(OUT/(Path(name).stem+'.te.svg')).relative_to(BASE).as_posix()})
    return assets


INK='#19354a'
BLUE_FILL='#e1f0f2'
BLUE_STROKE='#245868'
RED='#b32a22'
ARROW='#008d86'
FONT='Noto Sans Telugu, Nirmala UI, sans-serif'


def element(parent,tag,attrs=None,text=None):
    e=ET.SubElement(parent,SVG+tag,{k:str(v) for k,v in (attrs or {}).items()})
    if text is not None:e.text=text
    return e


def text(parent,value,x,y,role,size=34,fill=INK,**attrs):
    return element(parent,'text',{'x':x,'y':y,'font-family':FONT,'font-size':size,
        'text-anchor':'middle','fill':fill,'data-role':role,**attrs},value)


def root_svg(width,height,title,desc):
    ET.register_namespace('',SVG[1:-1])
    root=ET.Element(SVG+'svg',{'viewBox':f'0 0 {width} {height}','width':str(width),'height':str(height),
        'role':'img','aria-labelledby':'title desc','lang':'te'})
    element(root,'title',{'id':'title'},title)
    element(root,'desc',{'id':'desc'},desc)
    element(root,'metadata',text='New code-native mathematical redraw of the pinned OpenStax image; original raster retained unchanged. Not a scan edit, official Telugu terminology claim, or native-speaker approval.')
    element(root,'rect',{'x':0,'y':0,'width':width,'height':height,'fill':'#ffffff','data-role':'background'})
    return root


def block_group(root,kind,count,x,y,cols,stage,group_id):
    group=element(root,'g',{'data-role':'block-group','data-kind':kind,'data-stage':stage,'data-group':group_id})
    for i in range(count):
        step=22 if kind=='ten' else 32
        element(group,'rect',{'x':x+(i%cols)*step,'y':y+(i//cols)*34,'width':22,'height':22,
            'fill':BLUE_FILL,'stroke':BLUE_STROKE,'stroke-width':1.6,'data-role':'unit-cell'})
    return group


def model_svg():
    desc=('17 + 26 నమూనా (model): ఎడమ పై భాగంలో పదుల కడ్డీ 1, ఒకట్ల బ్లాకులు 7 (2 + 5); '
          'ఎడమ కింది భాగంలో పదుల కడ్డీలు 2, ఒకట్ల బ్లాకులు 6 (5 + 1). కుడివైపు పదుల కడ్డీలు 4, ఒకట్ల బ్లాకులు 3. '
          'ఒక్కో కడ్డీలో 10 గడులు; ఒక్కో విడి బ్లాకు విలువ 1. బాణం ఎడమ నమూనా నుంచి కుడి నమూనాకు చూపుతుంది. '
          'కుడి అంచున 17 + 26 = 43 నిలువుగా రాయబడింది; పదుల అంకె 1 పైన చిన్న ఎరుపు 1 ఉంది. '
          '1 + 1 + 2 = 4 అనే పెట్టె నుంచి ఆ చిన్న 1 వైపు మరో బాణం చూపుతుంది. '
          'English: 17 (one ten and seven ones) plus 26 (two tens and six ones) becomes four tens and three ones; '
          'the adjacent column sum is 43 with a red carry 1 over the tens digit. Callout: 1 + 1 + 2 = 4.')
    root=root_svg(1260,304,'17 + 26: నమూనా, నిలువు సంకలనం (model and column addition)',desc)
    # Exact source groups; the after state is the same43, not43 more.
    block_group(root,'ten',10,70,76,10,'before-17','a-ten')
    block_group(root,'ones',2,322,76,2,'before-17','a-ones-top')
    block_group(root,'ones',5,322,110,5,'before-17','a-ones-bottom')
    for i in range(2):block_group(root,'ten',10,70,198+34*i,10,'before-26',f'b-ten-{i}')
    block_group(root,'ones',5,322,198,5,'before-26','b-ones-top')
    block_group(root,'ones',1,322,232,1,'before-26','b-ones-bottom')
    for i in range(4):block_group(root,'ten',10,632,76+34*i,10,'after',f'c-ten-{i}')
    block_group(root,'ones',3,888,76,3,'after','c-ones')
    text(root,'17',30,98,'operand-label',26)
    text(root,'+ 26',30,220,'operand-label',26)
    element(root,'line',{'x1':4,'x2':57,'y1':236,'y2':236,'stroke':INK,'stroke-width':2,'data-role':'left-rule'})
    element(root,'line',{'x1':588,'x2':588,'y1':60,'y2':275,'stroke':'#83979d','stroke-width':1.5,'data-role':'state-divider'})
    defs=element(root,'defs')
    marker=element(defs,'marker',{'id':'arrowhead','markerWidth':9,'markerHeight':8,'refX':8,'refY':4,'orient':'auto','markerUnits':'strokeWidth'})
    element(marker,'path',{'d':'M0,0 L8,4 L0,8 Z','fill':ARROW})
    element(root,'path',{'d':'M510,154 L563,154','stroke':ARROW,'stroke-width':3,'fill':'none','marker-end':'url(#arrowhead)','data-role':'model-arrow'})
    for row,value,y in [('first','17',146),('second','26',198),('sum','43',259)]:
        for digit,place,x in zip(value,['tens','ones'],[1110,1170]):
            text(root,digit,x,y,'digit',36,**{'data-row':row,'data-place':place})
    text(root,'+',1040,198,'plus')
    text(root,'1',1110,98,'carry',22,RED,**{'data-place':'tens'})
    element(root,'line',{'x1':1020,'x2':1198,'y1':217,'y2':217,'stroke':INK,'stroke-width':2,'data-role':'sum-rule'})
    element(root,'rect',{'x':874,'y':8,'width':314,'height':42,'fill':'#ffffff','stroke':INK,'stroke-width':1.2,'data-role':'callout-box'})
    text(root,'1 + 1 + 2 = 4',1031,37,'carry-equation',28)
    element(root,'path',{'d':'M1040,51 L1089,82','stroke':ARROW,'stroke-width':2,'fill':'none','marker-end':'url(#arrowhead)','data-role':'callout-arrow'})
    return root


def column_svg(step):
    partial=['','0','10','910'][step-1]
    carry_places=[[],['tens'],['hundreds','tens'],['hundreds','tens']][step-1]
    meanings=[
        '324, 586లను స్థానాలు సరిపడేలా నిలువుగా రాశారు; ఇంకా ఫలితం రాయలేదు. Aligned operands324 and586; no result shown.',
        '4 + 6 = 10: ఒకట్ల స్థానంలో 0; పదుల అంకె 2 పైన చిన్న 1. Ones sum10: write0, carry1 above the tens digit2.',
        '1 + 2 + 8 = 11: కింది పాక్షిక ఫలితం 10; వందల అంకె 3, పదుల అంకె 2 పైన చిన్న 1లు. '
        'Partial result10; carry1 above3 and1 above2. These are carry digits, not fractions.',
        '1 + 3 + 5 = 9: పూర్తి ఫలితం 910; వందల అంకె 3, పదుల అంకె 2 పైన చిన్న 1లు అలాగే ఉన్నాయి. '
        'Completed sum324 +586 =910; carry1 above3 and1 above2. These are carry digits, not fractions.']
    root=root_svg(304,260,f'324 + 586: దశ {step} (step {step})',meanings[step-1])
    places=['hundreds','tens','ones'];xs=[126,182,238]
    for row,value,y in [('first','324',105),('second','586',163),('sum',partial,236)]:
        for digit,place,x in zip(value,places[-len(value):] if value else [],xs[-len(value):] if value else []):
            text(root,digit,x,y,'digit',40,**{'data-row':row,'data-place':place})
    text(root,'+',61,163,'plus',36)
    element(root,'line',{'x1':40,'x2':268,'y1':185,'y2':185,'stroke':INK,'stroke-width':2,'data-role':'sum-rule'})
    for place in carry_places:text(root,'1',xs[places.index(place)],57,'carry',22,**{'data-place':place})
    return root


def svg_for(name):return model_svg() if name==NAMES[0] else column_svg(NAMES.index(name))


def check_svg(name,root):
    """Check actual rendered text, cells, coordinates, carry alignment and arrows."""
    need(root.tag==SVG+'svg' and root.get('role')=='img','Missing SVG accessibility root')
    for tag in ['title','desc','metadata']:need(bool(root.findtext(SVG+tag)),f'Missing {tag}')
    need(root.get('aria-labelledby')=='title desc','Accessible name changed')
    need(not list(root.iter(SVG+'image')),'Raster embedded in redraw')
    is_model=name==NAMES[0]
    need(root.get('viewBox')==('0 0 1260 304' if is_model else '0 0 304 260'),'SVG bounds changed')
    texts=list(root.iter(SVG+'text'))
    visible=[x for x in texts if x.get('data-role')=='digit']
    expected={('first','tens'):'1',('first','ones'):'7',('second','tens'):'2',('second','ones'):'6',('sum','tens'):'4',('sum','ones'):'3'} if is_model else {('first',p):d for p,d in zip(['hundreds','tens','ones'],'324')}
    if not is_model:
        step=NAMES.index(name)
        expected.update({('second',p):d for p,d in zip(['hundreds','tens','ones'],'586')})
        part=['','0','10','910'][step-1]
        expected.update({('sum',p):d for p,d in zip(['hundreds','tens','ones'][-len(part):] if part else [],part)})
    need(len(visible)==len(expected),'Digit count changed')
    need({(t.get('data-row'),t.get('data-place')):t.text for t in visible}==expected,'Visible operand/partial/result digit changed')
    xs={'tens':1110,'ones':1170} if is_model else {'hundreds':126,'tens':182,'ones':238}
    ys={'first':146,'second':198,'sum':259} if is_model else {'first':105,'second':163,'sum':236}
    for t in visible:
        need(float(t.get('x'))==xs[t.get('data-place')] and float(t.get('y'))==ys[t.get('data-row')],'Place alignment changed')
    plus=[t for t in texts if t.get('data-role')=='plus']
    need(len(plus)==1 and plus[0].text=='+','Addition operator changed')
    carries=[t for t in texts if t.get('data-role')=='carry']
    expected_carries=['tens'] if is_model else [[],['tens'],['hundreds','tens'],['hundreds','tens']][NAMES.index(name)-1]
    need([t.get('data-place') for t in carries]==expected_carries,'Carry destination/count changed')
    for t in carries:
        need(t.text=='1' and float(t.get('x'))==xs[t.get('data-place')] and float(t.get('y'))==(98 if is_model else 57),'Carry digit/alignment changed')
        need(t.get('font-size')=='22' and t.get('fill')==(RED if is_model else INK),'Carry emphasis changed')
    rules=[e for e in root.iter(SVG+'line') if e.get('data-role')=='sum-rule']
    need(len(rules)==1 and rules[0].get('y1')==rules[0].get('y2')==('217' if is_model else '185'),'Sum rule changed')
    if not is_model:
        need(len(list(root.iter(SVG+'line')))==1,'Unexpected line: carry digits must not become fractions')
        need(not list(root.iter(SVG+'path')) and not list(root.iter(SVG+'g')),'Unexpected graphic in column sum')
        need(324+586==910,'Arithmetic invariant')
        return
    expected_groups={'a-ten':('ten','before-17',10,70,76,10),'a-ones-top':('ones','before-17',2,322,76,2),
        'a-ones-bottom':('ones','before-17',5,322,110,5),'b-ten-0':('ten','before-26',10,70,198,10),
        'b-ten-1':('ten','before-26',10,70,232,10),'b-ones-top':('ones','before-26',5,322,198,5),
        'b-ones-bottom':('ones','before-26',1,322,232,1),'c-ones':('ones','after',3,888,76,3)}
    expected_groups.update({f'c-ten-{i}':('ten','after',10,632,76+34*i,10) for i in range(4)})
    groups=[e for e in root.iter(SVG+'g') if e.get('data-role')=='block-group']
    need(len(groups)==len(expected_groups) and {e.get('data-group') for e in groups}==set(expected_groups),'Model groups changed')
    values={}
    for g in groups:
        kind,stage,count,x,y,cols=expected_groups[g.get('data-group')]
        need(g.get('data-kind')==kind and g.get('data-stage')==stage,'Group kind/stage changed')
        cells=list(g)
        need(len(cells)==count,'Block count changed')
        for i,c in enumerate(cells):
            need(c.tag==SVG+'rect' and c.get('data-role')=='unit-cell','Block shape changed')
            need(c.get('width')==c.get('height')=='22' and float(c.get('x'))==x+(i%cols)*(22 if kind=='ten' else 32) and float(c.get('y'))==y+(i//cols)*34,'Unit-cell geometry changed')
            need(c.get('fill')==BLUE_FILL and c.get('stroke')==BLUE_STROKE,'Block styling changed')
        values[stage]=values.get(stage,0)+len(cells)
    need(values=={'before-17':17,'before-26':26,'after':43},'Model stage values changed')
    need(values['before-17']+values['before-26']==values['after'],'Conservation failure')
    labels=[t.text for t in texts if t.get('data-role')=='operand-label']
    need(labels==['17','+ 26'],'Model operand labels changed')
    eq=[t.text for t in texts if t.get('data-role')=='carry-equation']
    need(eq==['1 + 1 + 2 = 4'] and 1+1+2==4,'Tens callout changed')
    for role,path in [('model-arrow','M510,154 L563,154'),('callout-arrow','M1040,51 L1089,82')]:
        arrows=[e for e in root.iter(SVG+'path') if e.get('data-role')==role]
        need(len(arrows)==1 and arrows[0].get('d')==path and arrows[0].get('marker-end')=='url(#arrowhead)','Arrow direction/destination changed')


def self_test():
    rejected=0
    def reject(name,root):
        nonlocal rejected
        try:check_svg(name,root)
        except (ValueError,KeyError,TypeError):rejected+=1
        else:raise AssertionError('Corrupt actual SVG accepted: '+name)
    for name in NAMES:
        baseline=ET.parse(OUT/(Path(name).stem+'.te.svg')).getroot()
        check_svg(name,baseline)
        text_nodes=list(baseline.iter(SVG+'text'))
        for index in range(len(text_nodes)):
            corrupt=copy.deepcopy(baseline)
            list(corrupt.iter(SVG+'text'))[index].text='999'
            reject(name,corrupt)
        for index,t in enumerate(text_nodes):
            if t.get('data-role') not in ['digit','carry']:continue
            corrupt=copy.deepcopy(baseline)
            list(corrupt.iter(SVG+'text'))[index].set('x',str(float(t.get('x'))+25))
            reject(name,corrupt)
        corrupt=copy.deepcopy(baseline)
        corrupt.find(SVG+'desc').text=''
        reject(name,corrupt)
        if name==NAMES[0]:
            groups=list(baseline.iter(SVG+'g'))
            for index in range(len(groups)):
                corrupt=copy.deepcopy(baseline)
                g=list(corrupt.iter(SVG+'g'))[index]
                g.remove(g[-1])
                reject(name,corrupt)
                corrupt=copy.deepcopy(baseline)
                g=list(corrupt.iter(SVG+'g'))[index]
                g[0].set('width','23')
                reject(name,corrupt)
            for role in ['model-arrow','callout-arrow']:
                corrupt=copy.deepcopy(baseline)
                next(e for e in corrupt.iter(SVG+'path') if e.get('data-role')==role).set('d','M0,0 L1,1')
                reject(name,corrupt)
        else:
            corrupt=copy.deepcopy(baseline)
            element(corrupt,'line',{'x1':112,'x2':140,'y1':70,'y2':70})
            reject(name,corrupt)
    print(json.dumps({'status':'PASS','negative_fixtures_rejected':rejected,'writes':0}))


def build(verify=False,preserve_only=False):
    assets=originals(write_missing=not verify)
    if preserve_only:
        print(json.dumps({'status':'PASS','originals':len(assets),'bytes':sum(a['original_bytes'] for a in assets)},ensure_ascii=False))
        return
    outputs={}
    for index,(name,asset) in enumerate(zip(NAMES,assets)):
        root=svg_for(name)
        check_svg(name,root)
        raw=ET.tostring(root,encoding='utf-8',xml_declaration=True)+b'\n'
        path=BASE/asset['localized_path']
        if verify:check_svg(name,ET.fromstring(path.read_bytes()))
        outputs[path]=raw
        asset.update({'localized_sha256':digest(raw),'localized_bytes':len(raw),
            'localized_dimensions_px':[1260,304] if index==0 else [304,260],
            'recommended_min_width_px':1260 if index==0 else 304,
            'adaptation':'new code-native mathematical redraw; no raster editing; original bytes unchanged',
            'pixel_read_notes':[
                'Original001:17 group1ten+7ones(2+5),26 group2tens+6ones(5+1); arrow to4tens+3ones; embedded17+26=43 with redcarry1 and1+1+2=4 callout retained.',
                'Original020-01: aligned324 and586 with plus sign and sum rule; no carry or result.',
                'Original020-02: carry1 over tens digit2; partial result0 in ones.',
                'Original020-03: carry1 over hundreds3 and carry1 over tens2; partial result10. Not fractions1/3 or1/2.',
                'Original020-04: same two carry1s and complete910. Not fractions1/3 or1/2.'][index]})
    manifest={'schema':'te-code-native-assets-v1','unit':'TE-B015','source_sha256':SOURCE_SHA,'source_text_slots':859,
        'source_commit':COMMIT,'source_archive_sha256':ARCHIVE_SHA,
        'source_url':'https://github.com/openstax/osbooks-prealgebra-bundle/tree/'+COMMIT,
        'source_archive_url':'https://codeload.github.com/openstax/osbooks-prealgebra-bundle/zip/'+COMMIT,
        'acquisition_note':'No download in this task. Read only5 named media members from the already verified complete archive, which was copied pre-alert from another task; sparse checkout remains sparse.',
        'disclosure':'New code-native mathematical redraws after direct inspection of all5 full source images. Original pixels retained separately. Source stage counts, digits, carry places, colors and both001arrows preserved; spacing/font/drawing geometry newly authored.',
        'assets':assets,'qa':{'source_media_count':5,'localized_asset_count':5,'selected_crc_and_git_blob_verified':True,
            'independent_visual_approval':False,'native_speaker_approval':False},
        'source_quirks':[
            '020-03 and020-04 canonical English alt texts call carry1s fractions1/3 and1/2. Pixels, source solution and Indonesian descriptions show carry digits, not fractions; future target alt must clarify without changing frozen source.',
            '001 canonical alt omits the adjacent numerical column sum, redcarry1 and1+1+2=4 callout. Redraw retains every visible mathematical component.',
            '1683+479 hundreds-step source MathML has partial162 but omits the carried1 above thousands until the final row; not one of these image assets and not rewritten here.'],
        'canon_consultation':['TS2PDF42/printed30:actualOCR then fullPNG,ones/tens/hundreds labels and zero contribution.',
            'TS2PDF44/printed32:actualOCR then fullPNG,vertical place alignment465/805; lower600+30+0 verified against OCR80 error.',
            'TS6PDF27/printed17:actualOCR then fullPNG,2+3=5 and witnessed సంకలనం. No new official property/carry terminology claim.',
            'TS2PDF32/printed20:actualOCR then fullPNG,80is8tens and19is1ten9ones; count versus value retained.',
            'TS6PDF28/printed18:actualOCR then fullPNG,5+3and3+5number-line practice; no formal commutative/identity-property labels on this page.']}
    outputs[OUT/'manifest.json']=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    preview='<!doctype html><html lang="te"><meta charset="utf-8"><title>B015 asset author preview</title><style>body{font:18px sans-serif;margin:24px;color:#19354a}section{margin:32px 0;padding:16px;border:1px solid #ccc}img{display:block}h2{font-size:18px}</style><h1>B015 asset author preview</h1>'
    for asset in assets:
        name=Path(asset['localized_path']).name
        preview+=f'<section><h2>{name}</h2><img src="{name}" alt="{asset["media_id"]}"></section>'
    outputs[OUT/'preview.html']=(preview+'</html>\n').encode('utf-8')
    for path,raw in outputs.items():
        if verify:need(path.read_bytes()==raw,'Generated asset/manifest differs: '+path.name)
        else:write(path,raw)
    print(json.dumps({'status':'PASS','assets':5,'original_bytes':sum(a['original_bytes'] for a in assets),
        'svg_bytes':sum(a['localized_bytes'] for a in assets),'crc_and_git_blob':'PASS','writes':0 if verify else len(outputs)}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group()
    group.add_argument('--preserve-only',action='store_true')
    group.add_argument('--verify',action='store_true')
    group.add_argument('--self-test',action='store_true')
    args=parser.parse_args()
    if args.self_test:self_test()
    else:build(args.verify,args.preserve_only)
