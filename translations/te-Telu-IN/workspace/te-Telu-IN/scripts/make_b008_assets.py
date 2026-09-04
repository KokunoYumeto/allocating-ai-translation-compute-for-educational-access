"""B008 selected preserved originals and code-native mathematical redraws.

No downloads or bulk extraction. Verification modes perform no writes.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from make_b003_assets import need,digest,file_digest
from make_b002_assets import SVG,WORDS,VALUES,COLORS,child,text,frame,block

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parent
OUT=BASE/'assets/B008'
SOURCE=BASE/'sources/TE-B008.en.cnxml'
SOURCE_SHA='7f7ce451bd8f7757bd0bd515db42de196d26f68f41bec22959876e797e259a14'
COMMIT='38cae454e644abf9f0a623e876994553881597c9'
ARCHIVE_SHA='effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917'
CN='{http://cnx.rice.edu/cnxml}'
NAMES=[f'CNX_BMath_Figure_01_01_{n}_img.jpg' for n in range(201,205)]+['CNX_BMath_Figure_AppB_001.jpg']
MODELS={201:(5,6,1),202:(3,8,4),203:(4,0,7),204:(6,2,0)}
NUMERALS={201:561,202:384,203:407,204:620}
KINDS=('hundred','ten','one')
HEADERS=[(['నేను చేయగలను…'],['I can…']),(['నమ్మకంగా'],['Confidently']),
         (['కొంత సహాయంతో'],['With some help']),(['లేదు—ఇంకా','అర్థం కాలేదు!'],['No—I don’t','get it!'])]
ROWS=[(['సహజ సంఖ్యలను, పూర్ణాంకాలను గుర్తించడం'],'identify counting numbers and whole numbers.'),
      (['పూర్ణాంకాలకు నమూనాలు చూపడం'],'model whole numbers.'),
      (['అంకె ఉన్న స్థానాన్ని గుర్తించడం'],'identify the place value of a digit.'),
      (['స్థాన విలువతో పూర్ణాంకాలను','అక్షరాలలో రాయడం'],'use place value to name whole numbers.'),
      (['స్థాన విలువతో పూర్ణాంకాలను','అంకెలలో రాయడం'],'use place value to write whole numbers.'),
      (['పూర్ణాంకాలను నిర్దిష్ట స్థానానికి','సవరించి రాయడం'],'round whole numbers.')]
TX=(20,740,980,1220,1460)
TY=(20,156,256,356,456,556,656,756)


def model(number):
    counts=MODELS[number]
    root=frame(900,560,'వందలు, పదులు, ఒకట్లు / Base-ten block model',
        f'వందలు: {counts[0]}; పదులు: {counts[1]}; ఒకట్లు: {counts[2]}. '
        f'{counts[0]} hundred squares, each a 10-by-10 grid; {counts[1]} ten rods, each 10 unit cells; '
        f'{counts[2]} single unit cells. A zero-count column contains no blocks. The numerical answer is not printed.')
    for x in (436,666):
        child(root,'line',{'x1':x,'x2':x,'y1':94,'y2':534,'stroke':'#cad8de','stroke-width':1.5,
                          'data-role':'column-divider'})
    for kind,count,center in zip(KINDS,counts,(222,550,775)):
        lane=child(root,'g',{'data-role':'place-column','data-place':kind})
        text(lane,center,44,WORDS[kind][0],27,**{'data-role':'place-label','lang':'te'})
        text(lane,center,73,WORDS[kind][1],18,'#526573',**{'data-role':'place-gloss','lang':'en'})
        for i in range(count):
            if kind=='hundred':x,y=70+144*(i%2),112+144*(i//2)
            elif kind=='ten':x,y=490,122+30*i
            else:x,y=732+24*(i%4),132+30*(i//4)
            group=block(lane,kind,x,y)
            group.set('data-origin-x',str(x));group.set('data-origin-y',str(y))
    return root


def selfcheck():
    desc='స్వీయ పరిశీలన పట్టిక. ఆరు లక్ష్యాలు; మూడు స్వీయ అంచనా ఎంపికలు. మొత్తం 18 ఎంపిక గడులు ఖాళీగా ఉన్నాయి. '
    desc+='Self-assessment: six objectives, three confidence options, all 18 response cells blank. '
    desc+='Options: Confidently; With some help; No—I don’t get it! Objectives: '
    desc+='; '.join(' '.join(te)+' / '+en for te,en in ROWS)
    root=frame(1480,780,'స్వీయ పరిశీలన / Self-assessment checklist',desc)
    for row in range(7):
        for col in range(4):
            cell=child(root,'g',{'data-role':'table-cell','data-row':row,'data-col':col,
                               'data-response':'true' if row>0 and col>0 else 'false'})
            child(cell,'rect',{'x':TX[col],'y':TY[row],'width':TX[col+1]-TX[col],
                'height':TY[row+1]-TY[row],'fill':'#d9f0f0' if row==0 else '#f1f7f8' if row%2 else '#ffffff',
                'stroke':'#38767a','stroke-width':1.5,'data-role':'cell-boundary'})
            if row==0:
                te,en=HEADERS[col];cx=(TX[col]+TX[col+1])/2
                for i,line in enumerate(te):
                    text(cell,cx,(54 if len(te)>1 else 76)+32*i,line,26,**{'data-role':'header-te','lang':'te'})
                for i,line in enumerate(en):
                    text(cell,cx,118+22*i,line,20,'#334e5d',**{'data-role':'header-en','lang':'en'})
            elif col==0:
                te,en=ROWS[row-1]
                for i,line in enumerate(te):
                    text(cell,TX[col]+18,TY[row]+(31 if len(te)>1 else 40)+32*i,line,26,
                         anchor='start',**{'data-role':'objective-te','lang':'te'})
                text(cell,TX[col]+18,TY[row]+87,en,21,'#334e5d',anchor='start',
                     **{'data-role':'objective-en','lang':'en'})
    return root


def svg_bytes(number):
    root=model(number) if number in MODELS else selfcheck()
    ET.indent(root,space='  ')
    return ET.tostring(root,encoding='utf-8',xml_declaration=True)+b'\n'


def inside(rect,bounds):
    x,y,w,h=(float(rect.get(k,'0')) for k in ('x','y','width','height'))
    a,b,c,d=bounds
    return x>=a and y>=b and w>0 and h>0 and x+w<=c and y+h<=d


def math_check(number,payload):
    root=ET.fromstring(payload)
    need(root.tag==SVG+'svg' and root.get('role')=='img' and root.get('aria-labelledby')=='title desc','Accessible SVG root changed')
    need(root.find(SVG+'title') is not None and root.find(SVG+'desc') is not None,'Missing accessible title/description')
    need(not any(e.tag in (SVG+'image',SVG+'script',SVG+'foreignObject',SVG+'use') for e in root.iter()),'Not static code-native SVG')
    need(not any(k.startswith('on') or k in ('href','transform','style','display','visibility','opacity') for e in root.iter() for k in e.attrib),'Hidden/interactive/transformed SVG content')
    size=(900,560) if number in MODELS else (1480,780)
    need(root.get('viewBox')==f'0 0 {size[0]} {size[1]}' and root.get('width')==str(size[0]) and root.get('height')==str(size[1]),'Canvas changed')
    need(all(inside(e,(0,0,*size)) for e in root.iter(SVG+'rect')),'Rectangle outside canvas')
    if number in MODELS:
        lanes=[e for e in root if e.get('data-role')=='place-column']
        need([e.get('data-place') for e in lanes]==list(KINDS),'Place columns lost/reordered')
        count_cells=[];geometries=[]
        for kind,count,lane,center in zip(KINDS,MODELS[number],lanes,(222,550,775)):
            labels=list(lane.iter(SVG+'text'))
            need([(t.get('data-role'),t.text,t.get('x')) for t in labels]==[
                ('place-label',WORDS[kind][0],str(center)),('place-gloss',WORDS[kind][1],str(center))],'Place labels changed')
            groups=list(lane.findall(SVG+'g'))
            need(len(groups)==count,'Wrong block group count')
            for i,g in enumerate(groups):
                need(g.get('data-kind')==kind and g.get('data-value')==str(VALUES[kind]),'Wrong group kind/value')
                if kind=='hundred':ox,oy=70+144*(i%2),112+144*(i//2)
                elif kind=='ten':ox,oy=490,122+30*i
                else:ox,oy=732+24*(i%4),132+30*(i//4)
                need(g.get('data-origin-x')==str(ox) and g.get('data-origin-y')==str(oy),'Origin metadata changed')
                cells=list(g)
                nr,nc=(10,10) if kind=='hundred' else (1,10) if kind=='ten' else (1,1)
                need(len(cells)==VALUES[kind],'Wrong unit-cell count')
                need({(int(e.get('data-row','-1')),int(e.get('data-col','-1'))) for e in cells}=={(r,c) for r in range(nr) for c in range(nc)},'Grid row/column set changed')
                for cell in cells:
                    r,c=int(cell.get('data-row')),int(cell.get('data-col'))
                    need(cell.tag==SVG+'rect' and cell.get('data-cell')=='1','Not a unit rectangle')
                    need((float(cell.get('x')),float(cell.get('y')),float(cell.get('width')),float(cell.get('height')))==(ox+12*c,oy+12*r,12,12),'Unit-cell geometry or scale changed')
                    need(cell.get('fill')==COLORS[kind][0] and cell.get('stroke')==COLORS[kind][1],'Block visibility/color changed')
                geometries.append((ox,oy,12*nc,12*nr));count_cells.append(len(cells))
        # These are actual group bounding rectangles, not only count metadata.
        for i,(x,y,w,h) in enumerate(geometries):
            for a,b,c,d in geometries[i+1:]:
                need(x+w<=a or a+c<=x or y+h<=b or b+d<=y,'Overlapping block groups')
        need(len(list(root.iter(SVG+'text')))==6,'Visible answer or extra label introduced')
        need(len(list(root.iter(SVG+'rect')))==1+sum(count_cells),'Extra/missing shape introduced')
        need(sum(count_cells)==NUMERALS[number],'Modeled value mismatch')
        return {'groups_hundreds_tens_ones':list(MODELS[number]),'unit_cells_per_group':[100,10,1],
            'actual_unit_cells':sum(count_cells),'value':NUMERALS[number],'zero_count_columns':[k for k,c in zip(KINDS,MODELS[number]) if c==0],
            'visible_answer':False,'exact_grid_geometry_scale_and_nonoverlap':True}
    cells=[e for e in root if e.get('data-role')=='table-cell']
    need(len(cells)==28,'Wrong table cell count')
    need({(int(c.get('data-row','-1')),int(c.get('data-col','-1'))) for c in cells}=={(r,c) for r in range(7) for c in range(4)},'Wrong table row/column coverage')
    responses=0
    for cell in cells:
        row,col=int(cell.get('data-row')),int(cell.get('data-col'));rects=cell.findall(SVG+'rect');labels=cell.findall(SVG+'text')
        need(len(rects)==1,'Cell boundary missing/repeated')
        rect=rects[0]
        need(tuple(float(rect.get(k)) for k in ('x','y','width','height'))==(TX[col],TY[row],TX[col+1]-TX[col],TY[row+1]-TY[row]),'Table geometry changed')
        need(rect.get('fill')==('#d9f0f0' if row==0 else '#f1f7f8' if row%2 else '#ffffff') and rect.get('stroke')=='#38767a','Table visibility changed')
        if row>0 and col>0:
            responses+=1
            need(cell.get('data-response')=='true' and len(cell)==1 and not labels,'Self-assessment response not blank')
        else:
            need(cell.get('data-response')=='false','Header/label marked as response')
            te,en=HEADERS[col] if row==0 else (ROWS[row-1][0],[ROWS[row-1][1]])
            need([e.text for e in labels]==te+en,'Checklist words/order changed')
            need([e.get('lang') for e in labels]==['te']*len(te)+['en']*len(en),'Checklist language metadata changed')
            need(len(cell)==1+len(labels),'Extra checklist mark/shape')
    need(responses==18 and len(list(root.iter(SVG+'rect')))==29,'Incorrect blank response grid')
    need(len(list(root.iter(SVG+'text')))==sum(len(c.findall(SVG+'text')) for c in cells),'Extra visible text outside table')
    need(not list(root.iter(SVG+'path')) and not list(root.iter(SVG+'line')) and not list(root.iter(SVG+'circle')),'Invented response mark')
    return {'columns':4,'rows_including_header':7,'objectives':6,'confidence_options':3,
        'blank_response_cells':18,'preselected_or_correct_state':False,'english_objective_text_preserved':True}


def self_test():
    rejected=0
    def reject(number,mutate,label):
        nonlocal rejected
        root=ET.fromstring(svg_bytes(number));mutate(root)
        try:math_check(number,ET.tostring(root))
        except (ValueError,TypeError,KeyError):rejected+=1
        else:raise AssertionError(f'Accepted corruption: {number} {label}')
    for number in (*MODELS,0):
        math_check(number,svg_bytes(number))
        reject(number,lambda r:r.set('viewBox','0 0 10 10'),'clipped canvas')
        reject(number,lambda r:child(r,'image',{'href':'wrong.jpg'}),'raster embedding')
        reject(number,lambda r:r.set('opacity','0'),'invisible diagram')
        if number in MODELS:
            def groups(r):return [e for e in r.iter(SVG+'g') if e.get('data-kind') in KINDS]
            reject(number,lambda r:groups(r)[0].remove(list(groups(r)[0])[0]),'missing unit cell')
            reject(number,lambda r:list(groups(r)[0])[1].set('x',list(groups(r)[0])[0].get('x')),'overlap unit cells')
            reject(number,lambda r:list(groups(r)[0])[0].set('width','13'),'unequal unit scale')
            reject(number,lambda r:list(groups(r)[0])[0].set('data-col','9'),'false grid index')
            reject(number,lambda r:list(groups(r)[0])[0].set('fill','white'),'invisible cell')
            reject(number,lambda r:next(e for e in r if e.get('data-role')=='place-column').append(copy.deepcopy(groups(r)[0])),'extra block')
            reject(number,lambda r:text(r,300,540,str(NUMERALS[number])),'answer leaked')
            reject(number,lambda r:next(r.iter(SVG+'text')).set('x','899'),'label position changed')
            if 0 in MODELS[number]:
                zero=KINDS[MODELS[number].index(0)]
                reject(number,lambda r:block(next(e for e in r if e.get('data-place')==zero),zero,490,122),'false zero-count block')
        else:
            def response(r):return next(e for e in r if e.get('data-response')=='true')
            reject(number,lambda r:text(response(r),850,200,'✓'),'checked response')
            reject(number,lambda r:child(response(r),'path',{'d':'M800 180L820 210L840 170'}),'response mark without text')
            reject(number,lambda r:r.remove(response(r)),'missing response cell')
            reject(number,lambda r:response(r).set('data-response','false'),'false blank metadata')
            reject(number,lambda r:response(r)[0].set('x','0'),'wrong cell geometry')
            reject(number,lambda r:response(r)[0].set('fill','white'),'response background changed')
            reject(number,lambda r:setattr(next(e for e in r.iter(SVG+'text') if e.get('data-role')=='objective-te'),'text','పూర్ణ సంఖ్యలు'),'wrong number-set label')
            reject(number,lambda r:setattr(next(e for e in r.iter(SVG+'text') if e.get('data-role')=='objective-en'),'text','write fractions.'),'English objective changed')
            reject(number,lambda r:next(e for e in r.iter(SVG+'text') if e.get('data-role')=='objective-en').set('lang','te'),'wrong language metadata')
    print(json.dumps({'valid_diagrams':5,'rejected_corruptions':rejected,'writes':0,'status':'PASS'}))


def source_assets(write=False):
    need(file_digest(SOURCE)==SOURCE_SHA,'B008 source changed')
    meta=json.loads((BASE/'sources/TE-B008.source.json').read_text('utf-8'))
    need(meta['source_sha256']==SOURCE_SHA and meta['source_commit']==COMMIT,'Unpinned B008 metadata')
    source=ET.parse(SOURCE).getroot();need(source.get('id')=='fs-id2279009','Wrong subsection')
    parents={c:p for p in source.iter() for c in p};images=list(source.iter(CN+'image'))
    need(len(images)==5 and {Path(e.get('src')).name for e in images}==set(NAMES),'Wrong selected media set')
    lock=json.loads((BASE/'sources.lock.json').read_text('utf-8'));a=next(a for a in lock['canonical_archives'] if a['id']=='A00-A20-en-complete-archive')
    need(a['sha256']==ARCHIVE_SHA and a['commit']==COMMIT,'Unpinned archive')
    path=ROOT/a['path'];need(path.stat().st_size==a['bytes'] and file_digest(path)==ARCHIVE_SHA,'Archive size/SHA mismatch')
    selected=['media/'+Path(e.get('src')).name for e in images]
    env=os.environ.copy();env.update(GIT_NO_LAZY_FETCH='1',GIT_TERMINAL_PROMPT='0')
    tree=subprocess.check_output(['git','-C',str(ROOT/'downloads/upstream-prealgebra'),'ls-tree','-r','-z',COMMIT,'--',*selected],env=env)
    blobs={}
    for line in tree.split(b'\0'):
        if line:
            header,name=line.split(b'\t');mode,kind,oid=header.split();need(kind==b'blob','Selected object not blob');blobs[name.decode()]=oid.decode()
    need(set(blobs)==set(selected),'Missing pinned blob')
    records=[];total=0
    if write:need(shutil.disk_usage(BASE).free>32*1024*1024,'Insufficient free space')
    with zipfile.ZipFile(path) as archive:
        need(archive.comment.decode()==COMMIT,'Wrong ZIP comment')
        for image,name in zip(images,selected):
            member='osbooks-prealgebra-bundle-'+COMMIT+'/'+name;info=archive.getinfo(member)
            need(0<info.file_size<2_000_000,'Selected original exceeds bound');data=archive.read(member);total+=len(data)
            need(total<8_000_000,'Selected total exceeds bound')
            blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();need(blob==blobs[name],'Selected original differs from pinned Git blob')
            target=OUT/'original'/Path(name).name
            if target.exists():need(target.read_bytes()==data,'Original changed; no overwrite')
            elif write:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
            else:raise FileNotFoundError(target)
            media=parents[image];parent=parents.get(media)
            records.append({'original_src':image.get('src'),'original_path':target.relative_to(BASE).as_posix(),
                'original_sha256':digest(data),'original_bytes':len(data),'source_git_blob_sha1':blob,
                'source_zip_member':member,'source_zip_crc32':f'{info.CRC:08x}',
                'media_id':media.get('id'),'figure_id':parent.get('id') if parent.tag==CN+'figure' else None,
                'localized_path':'assets/B008/'+Path(name).stem+'.te.svg'})
    return records,total


def build(verify=False,originals_only=False):
    records,total=source_assets(write=not verify)
    if originals_only:
        print(json.dumps({'originals':len(records),'total_bytes':total,'archive_sha_crc_git_blobs':'PASS'}));return
    for record in records:
        filename=Path(record['original_path']).name
        number=next((n for n in MODELS if f'_{n}_' in filename),0)
        payload=svg_bytes(number);record['math_checks']=math_check(number,payload)
        record.update(localized_sha256=digest(payload),localized_bytes=len(payload),
            recommended_min_width_px=900 if number else 1480,
            disclosure='New code-native bilingual redraw; source JPEG unchanged, no raster pixels edited or embedded. '
                +('B002 unit-cell primitive reused with new B008 count/layout specifications; visible answers omitted.' if number else
                  'All six source objectives and three confidence options retained, all 18 response cells blank. '
                  'Telugu third objective explicitly names the occupied place, following the source supplied-answer convention; English wording is retained.'))
        target=BASE/record['localized_path']
        if verify:
            math_check(number,target.read_bytes());need(target.read_bytes()==payload,'SVG differs from deterministic generator: '+filename)
        else:target.write_bytes(payload)
    manifest={'schema':'te-b002-assets-v1','unit':'TE-B008','source_subsection_id':'fs-id2279009',
        'source_subsection_sha256':SOURCE_SHA,'canonical_commit':COMMIT,'canonical_archive_sha256':ARCHIVE_SHA,
        'source_attribution':'OpenStax, Prealgebra 2e; existing project notices and source attribution remain applicable.',
        'generator':'scripts/make_b008_assets.py','verification_command':'python -B te-Telu-IN/scripts/make_b008_assets.py --verify',
        'scope':'Exactly five selected unchanged JPEGs and five code-native SVGs; no download or bulk extraction.',
        'choices':[
            'Read the frozen media and self-check context and visually inspected every original at full supplied image size before redraw.',
            'Pixel-confirmed original counts: 201=5/6/1, 202=3/8/4, 203=4/0/7, 204=6/2/0 (hundreds/tens/ones).',
            'Reuse B002 equal-size 12px unit-cell primitives; lay out up to six hundred squares without overlap. Original placement/color is not asserted identical.',
            'Retain three labeled place columns even when the count is zero; print no numeral answer or count/equation in the four practice diagrams.',
            'Reread TS Class 2 PDF42/printed30 OCR and complete page image: వందలు, పదులు, ఒకట్లు, స్థాన విలువ and zero-contribution examples guide labels and empty columns.',
            'Self-check has six objective rows plus header, four columns and 18 blank response cells; do not add scoring, correct-state marks or an invented completed assessment.',
            'Checklist Telugu wording aligned with the B008 translator; retain exact six English objective sentences as glosses.',
            'The source uses place value for place-name answers; Telugu third objective says occupied place, with the original English line retained. The prose bridge separately distinguishes contribution.',
            'సహజ సంఖ్యలు and పూర్ణాంకాలు follow witnessed course conventions; no AP regional difference or native-speaker approval is claimed.',
            'Browser runtime discovery returned no connected browser; isolated headless Edge author render is separate from main independent reader inspection.'
        ],'assets':records,
        'qa':{'selected_original_count':5,'original_bytes':total,'localized_svg_count':5,
              'localized_bytes':sum(r['localized_bytes'] for r in records),
              'all_unit_counts_geometry_values_and_blank_cells':'PASS','original_crc_git_blob_archive_sha':'PASS',
              'visual_review':'All five originals inspected; see AUTHOR-REVIEW.md for author render receipt. Independent integrated reader review remains main-task work.'}}
    encoded=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    target=OUT/'manifest.json'
    if verify:need(target.read_bytes()==encoded,'Manifest differs from current source/generator')
    else:
        target.write_bytes(encoded)
        sections=[]
        for r in records:
            sections.append(f'<section><h2>{r["media_id"]}</h2><p>Unchanged source JPEG</p>'
                f'<img class="original" src="original/{Path(r["original_path"]).name}" alt="Preserved source image for comparison">'
                f'<p>New code-native bilingual SVG. Horizontal scrolling is available.</p><div tabindex="0" class="scroll">'
                f'<img width="{r["recommended_min_width_px"]}" src="{Path(r["localized_path"]).name}" alt="B008 localized diagram for visual QA"></div></section>')
        preview='<!doctype html><html lang="te"><meta charset="utf-8"><meta name="viewport" content="width=device-width">'+\
            '<title>B008 asset QA</title><style>body{font-family:"Nirmala UI",sans-serif;color:#153a4b;background:#edf2f4;margin:24px}'+\
            'main{max-width:1480px;margin:auto}section{background:white;padding:20px;margin:24px 0;border:1px solid #cbd9de}'+\
            '.scroll{max-width:100%;overflow:auto}.scroll:focus{outline:3px solid #385e8c}.scroll img{max-width:none;display:block}'+\
            'img.original{max-width:100%;height:auto;display:block}h1{font-size:28px}h2{font-size:20px}</style>'+\
            '<main><h1>B008 originals and localized diagrams</h1><p>Author QA preview, not an independently approved reader.</p>'+''.join(sections)+'</main></html>\n'
        (OUT/'preview.html').write_text(preview,encoding='utf-8')
    print(json.dumps({'status':'PASS',**manifest['qa']},ensure_ascii=False))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--originals-only',action='store_true')
    p.add_argument('--verify',action='store_true');p.add_argument('--self-test',action='store_true');args=p.parse_args()
    need(sum((args.verify,args.self_test,args.originals_only))<=1,'Choose at most one operation')
    if args.self_test:self_test()
    else:build(args.verify,args.originals_only)
