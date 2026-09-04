"""Preserve only the19 B014 source images and create code-native block diagrams.

No downloads, bulk extraction, original overwrite, catalog or translation edits.
Verification and corruption tests are read-only.
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

BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parent;OUT=BASE/'assets/B014'
COMMIT='38cae454e644abf9f0a623e876994553881597c9'
SOURCE_SHA='b865a80cc39efa14f98ddd39d05d2ff688439978b39d9e153533254c9ad91352'
MODULE_SHA='b32058ce714e5fd43b010ccc81b2ae00a11567b229e9f96dda7b85b3cd82ba6b'
ARCHIVE_SHA='effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917'
SVG='{http://www.w3.org/2000/svg}'
PREFIX='CNX_BMath_Figure_01_02_'
NAMES=[PREFIX+s for s in ('019_img-02.png','019_img-03.png','019_img-04.png',
    '016_img-02.png','016_img-03.png','016_img-04.png','006_img.jpg','007_img.jpg',
    '017_img-02.png','017_img-03.png','017_img-04.png','010_img.jpg','011_img.jpg',
    '018_img-02.png','018_img-03.png','018_img-04.png','018_img-05.png','014_img.jpg','015_img.jpg')]


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
    path.parent.mkdir(parents=True,exist_ok=True);atomic_write(path,data)


def source():
    path=BASE/'sources/TE-B014.en.cnxml';raw=path.read_bytes()
    need(digest(raw)==SOURCE_SHA,'Frozen source changed')
    meta=json.loads((BASE/'sources/TE-B014.source.json').read_text('utf-8'))
    need(meta['source_commit']==COMMIT and meta['source_sha256']==SOURCE_SHA and meta['source_module']['sha256']==MODULE_SHA,'Source pin changed')
    root=ET.fromstring(raw)
    need(root.get('id')=='fs-id2145437' and len(list(root.iter()))==322 and len(list(slots(root)))==171,'Source scope/count changed')
    need([Path(e.get('src')).name for e in root.iter(CN+'image')]==NAMES,'Selected image list/order changed')
    module=(ROOT/meta['source_module']['path']).read_bytes();need(digest(module)==MODULE_SHA,'Canonical module changed')
    selected=next(e for e in ET.fromstring(module).iter() if e.get('id')=='fs-id2145437');selected.tail=None
    need(ET.tostring(selected)==ET.tostring(root),'Frozen selection differs from canonical module')
    return root


def originals(write_missing=False):
    root=source();parents={c:p for p in root.iter() for c in p}
    lock=json.loads((BASE/'sources.lock.json').read_text('utf-8'))
    record=next(r for r in lock['canonical_archives'] if r['id']=='A00-A20-en-complete-archive')
    need(record['sha256']==ARCHIVE_SHA and record['commit']==COMMIT,'Archive lock changed')
    archive=ROOT/record['path']
    need(archive.stat().st_size==537455794 and file_digest(archive)==ARCHIVE_SHA,'Archive bytes changed')
    env=os.environ.copy();env.update(GIT_NO_LAZY_FETCH='1',GIT_TERMINAL_PROMPT='0')
    listing=subprocess.check_output(['git','-C',str(ROOT/'downloads/upstream-prealgebra'),'ls-tree','-z',COMMIT,'--']+['media/'+n for n in NAMES],env=env)
    blobs={}
    for row in listing.split(b'\0'):
        if not row:continue
        header,path=row.split(b'\t');mode,kind,blob=header.split();need(kind==b'blob','Not Git blob');blobs[path.decode()]=blob.decode()
    need(set(blobs)=={'media/'+n for n in NAMES},'Pinned media set differs')
    assets=[]
    with zipfile.ZipFile(archive) as z:
        need(z.comment.decode()==COMMIT,'Archive comment changed')
        for image,name in zip(root.iter(CN+'image'),NAMES):
            member='osbooks-prealgebra-bundle-'+COMMIT+'/media/'+name
            info=z.getinfo(member);need(0<info.file_size<2_000_000,'Selected image exceeds size bound')
            data=z.read(member)
            blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            need(blob==blobs['media/'+name],'Image differs from pinned Git blob')
            destination=OUT/'original'/name
            if destination.exists():need(destination.read_bytes()==data,'Refusing original overwrite: '+name)
            elif write_missing:write(destination,data)
            else:raise FileNotFoundError(destination)
            with Image.open(io.BytesIO(data)) as opened:dimensions=list(opened.size)
            assets.append({'original_src':image.get('src'),'original_path':destination.relative_to(BASE).as_posix(),
                'original_sha256':digest(data),'original_bytes':len(data),'original_dimensions_px':dimensions,
                'source_git_blob_sha1':blob,'source_zip_crc32':f'{info.CRC:08x}','source_zip_member':member,
                'media_id':parents[image].get('id'),'figure_id':None,
                'localized_path':(OUT/(Path(name).stem+'.te.svg')).relative_to(BASE).as_posix()})
    return assets


BLUE=('#e1f0f2','#245868');RED=('#ffe0d6','#bc4931')
INK='#19354a';ACCENT='#a82880';CELL=24


def scene(name):
    """Pixel-read source layouts expressed as exact unit-cell geometry."""
    key=name.removeprefix(PREFIX);groups=[];labels=[];exchange=False
    def group(kind,count,x,y,cols=None,red=(),stage='single'):
        groups.append({'kind':kind,'count':count,'x':x,'y':y,'cols':cols or count,
            'red':list(red),'stage':stage})
    ones={'019_img-02.png':([3],['3']),'019_img-03.png':([3,4],['3','4']),
        '019_img-04.png':([7],['7']),'016_img-02.png':([2],['2']),
        '016_img-03.png':([2,6],['2','6']),'016_img-04.png':([8],['8']),
        '006_img.jpg':([3,6],['3 + 6 = 9']),'007_img.jpg':([5,1],['5 + 1 = 6']),
        '017_img-02.png':([5],['5']),'017_img-03.png':([5,8],['5','8'])}
    if key in ones:
        counts,words=ones[key];width=688 if sum(counts)>9 else 560;height=116;x=28
        for i,count in enumerate(counts):
            group('ones',count,x,24)
            if len(words)==len(counts):labels.append((words[i],x+(count-1)*32/2+12,92))
            x+=count*32+32
        if len(words)!=len(counts):labels.append((words[0],width/2,92))
    elif key=='017_img-04.png':
        width,height=688,220;exchange=True
        group('ones',5,28,30,stage='before');group('ones',5,220,30,stage='before')
        group('ones',3,444,30,stage='before')
        group('ten',10,110,158,red=range(10),stage='after')
        group('ones',3,414,158,stage='after')
    else:
        specs={'010_img.jpg':(1,2,2,False,False,'5 + 7 = 12'),
            '011_img.jpg':(1,4,4,False,False,'6 + 8 = 14'),
            '018_img-02.png':(1,7,4,False,False,None),
            '018_img-03.png':(2,6,3,False,False,None),
            '018_img-04.png':(3,13,5,False,True,None),
            '018_img-05.png':(4,3,3,True,False,None),
            '014_img.jpg':(4,2,2,False,False,'15 + 27 = 42'),
            '015_img.jpg':(4,5,5,False,False,'16 + 29 = 45')}
        tens,units,cols,last_red,red_ones,equation=specs[key]
        width=560;height=max(tens*36,((units+cols-1)//cols)*36)+40+(48 if equation else 0)
        for i in range(tens):group('ten',10,28,24+36*i,red=range(10) if last_red and i==tens-1 else ())
        group('ones',units,336,24,cols,range(10) if red_ones else ())
        if equation:labels.append((equation,width/2,height-18))
    return {'width':width,'height':height,'groups':groups,'labels':labels,'exchange':exchange}


def expected_values(name):
    """Independent value checklist transcribed after inspecting source pixels."""
    return dict(zip(NAMES,[{'single':3},{'single':7},{'single':7},
        {'single':2},{'single':8},{'single':8},{'single':9},{'single':6},
        {'single':5},{'single':13},{'before':13,'after':13},{'single':12},
        {'single':14},{'single':17},{'single':26},{'single':43},{'single':43},
        {'single':42},{'single':45}]))[name]


def element(parent,tag,attrs=None,text=None):
    e=ET.SubElement(parent,SVG+tag,{k:str(v) for k,v in (attrs or {}).items()})
    if text is not None:e.text=text
    return e


def description(spec):
    clauses=['ఒక చిన్న గడి విలువ 1; పది గడుల కడ్డీ విలువ 10.']
    for stage in dict.fromkeys(g['stage'] for g in spec['groups']):
        groups=[g for g in spec['groups'] if g['stage']==stage]
        tens=sum(g['kind']=='ten' for g in groups)
        ones=[str(g['count']) for g in groups if g['kind']=='ones']
        heading={'single':'నమూనా (model)','before':'ముందు (before)','after':'తర్వాత (after)'}[stage]
        clauses.append(heading+': పదుల కడ్డీలు (tens rods) '+str(tens)+'; ఒకట్ల బ్లాకులు (ones) '+(' + '.join(ones) or '0')+'.')
    if spec['exchange']:clauses.append('పది ఒకట్లను ఒక పదిగా మార్చినా మొత్తం విలువ మారదు. Both stages represent 13; do not add the two stages.')
    if spec['labels']:clauses.append('అంకెల గుర్తులు (numeric labels): '+ '; '.join(t for t,_,_ in spec['labels'])+'.')
    return ' '.join(clauses)


def svg(name):
    spec=scene(name);w,h=spec['width'],spec['height']
    root=ET.Element(SVG+'svg',{'width':str(w),'height':str(h),'viewBox':f'0 0 {w} {h}',
        'role':'img','aria-labelledby':'title desc','lang':'te'})
    element(root,'title',{'id':'title'},'సంకలనం: బ్లాకుల నమూనా · Addition block model')
    element(root,'desc',{'id':'desc'},description(spec))
    element(root,'rect',{'x':0,'y':0,'width':w,'height':h,'fill':'#ffffff','data-role':'background'})
    for i,g in enumerate(spec['groups']):
        group=element(root,'g',{'data-kind':g['kind'],'data-count':g['count'],'data-stage':g['stage'],'id':f'blocks-{i}'})
        for j in range(g['count']):
            gap=CELL if g['kind']=='ten' else CELL+8
            x=g['x']+(j%g['cols'])*gap;y=g['y']+(j//g['cols'])*36
            fill,stroke=RED if j in g['red'] else BLUE
            element(group,'rect',{'x':x,'y':y,'width':CELL,'height':CELL,'fill':fill,
                'stroke':stroke,'stroke-width':1.5,'data-cell':j})
    if spec['exchange']:
        element(root,'rect',{'x':16,'y':14,'width':368,'height':58,'rx':26,
            'fill':'none','stroke':ACCENT,'stroke-width':2.5,'data-role':'exchange-enclosure'})
        element(root,'line',{'x1':212,'y1':72,'x2':212,'y2':132,
            'stroke':ACCENT,'stroke-width':3,'data-role':'exchange-arrow'})
        element(root,'polygon',{'points':'204,126 220,126 212,138','fill':ACCENT,'data-role':'arrowhead'})
    for text,x,y in spec['labels']:
        element(root,'text',{'x':x,'y':y,'font-family':'Noto Sans Telugu, Nirmala UI, sans-serif',
            'font-size':28,'text-anchor':'middle','fill':INK},text)
    ET.register_namespace('',SVG[1:-1])
    return ET.tostring(root,encoding='utf-8',xml_declaration=True)+b'\n'


def check_svg(name,payload):
    spec=scene(name);root=ET.fromstring(payload);w,h=spec['width'],spec['height']
    need(root.tag==SVG+'svg' and root.get('viewBox')==f'0 0 {w} {h}','Canvas changed')
    need(root.get('width')==str(w) and root.get('height')==str(h),'Canvas size changed')
    need(root.get('role')=='img' and root.get('aria-labelledby')=='title desc','Accessibility root missing')
    need(root.find(SVG+'title').get('id')=='title' and root.find(SVG+'desc').get('id')=='desc','Accessibility references missing')
    need(root.findtext(SVG+'title')=='సంకలనం: బ్లాకుల నమూనా · Addition block model' and root.findtext(SVG+'desc')==description(spec),'Accessible quantities changed')
    need({e.tag for e in root.iter()}<={SVG+t for t in ('svg','title','desc','rect','g','text','line','polygon')},'Raster/script/unexpected element')
    need(not any(k in ('transform','display','visibility','opacity','style','href') or k.startswith('on') for e in root.iter() for k in e.attrib),'Hidden or transformed content')
    actual=list(root.iter(SVG+'g'));need(len(actual)==len(spec['groups']),'Wrong number of block groups')
    values={};actual_cells=0;cell_boxes=[];stages={}
    for group,g in zip(actual,spec['groups']):
        need(group.get('data-kind')==g['kind'] and group.get('data-count')==str(g['count']) and group.get('data-stage')==g['stage'],'Wrong group semantics')
        cells=list(group);need(len(cells)==g['count'],'Missing/extra unit cell')
        if g['kind']=='ten':need(len(cells)==10 and g['cols']==10,'Rod must contain10 units')
        for j,c in enumerate(cells):
            need(c.tag==SVG+'rect' and c.get('data-cell')==str(j),'Wrong cell/index')
            gap=CELL if g['kind']=='ten' else CELL+8
            x=g['x']+(j%g['cols'])*gap;y=g['y']+(j//g['cols'])*36
            need(tuple(float(c.get(a)) for a in ('x','y','width','height'))==(x,y,CELL,CELL),'Wrong unit scale/location')
            fill,stroke=RED if j in g['red'] else BLUE
            need((c.get('fill'),c.get('stroke'),c.get('stroke-width'))==(fill,stroke,'1.5'),'Regrouping color/stroke changed')
            need(0<=x and 0<=y and x+CELL<=w and y+CELL<=h,'Cell outside canvas')
            cell_boxes.append((x,y,CELL,CELL));actual_cells+=1
        values[g['stage']]=values.get(g['stage'],0)+len(cells)
        record=stages.setdefault(g['stage'],{'tens':0,'ones':0,'red_unit_cells':0})
        record['tens' if g['kind']=='ten' else 'ones']+=1 if g['kind']=='ten' else len(cells)
        record['red_unit_cells']+=len(g['red'])
    for i,(x,y,a,b) in enumerate(cell_boxes):
        for xx,yy,aa,bb in cell_boxes[i+1:]:need(x+a<=xx or xx+aa<=x or y+b<=yy or yy+bb<=y,'Unit cells overlap')
    need(values==expected_values(name),'Diagram values differ from inspected source')
    visible=[(e.text,float(e.get('x')),float(e.get('y'))) for e in root.iter(SVG+'text')]
    need(visible==[(t,float(x),float(y)) for t,x,y in spec['labels']],'Operand/answer label altered')
    for text,_,_ in visible:
        if '=' in text:
            left,right=text.split('=');a,b=left.split('+');need(int(a)+int(b)==int(right),'False shown equation')
    rectangles=list(root.iter(SVG+'rect'))
    need(len(rectangles)==actual_cells+1+int(spec['exchange']),'Unexpected/missing rectangle')
    need(root[2].tag==SVG+'rect' and dict(root[2].attrib)=={'x':'0','y':'0','width':str(w),'height':str(h),'fill':'#ffffff','data-role':'background'},'Background must precede and not obscure cells')
    frame=[e for e in root if e.get('data-role')=='exchange-enclosure']
    lines=list(root.iter(SVG+'line'));heads=list(root.iter(SVG+'polygon'))
    need(len(frame)==len(lines)==len(heads)==int(spec['exchange']),'Exchange indicator missing/extra')
    if spec['exchange']:
        need(dict(frame[0].attrib)=={'x':'16','y':'14','width':'368','height':'58','rx':'26','fill':'none','stroke':ACCENT,'stroke-width':'2.5','data-role':'exchange-enclosure'},'Exchange enclosure wrong')
        need(dict(lines[0].attrib)=={'x1':'212','y1':'72','x2':'212','y2':'132','stroke':ACCENT,'stroke-width':'3','data-role':'exchange-arrow'},'Exchange direction/endpoint wrong')
        need(dict(heads[0].attrib)=={'points':'204,126 220,126 212,138','fill':ACCENT,'data-role':'arrowhead'},'Arrowhead wrong')
        before=[g for g in spec['groups'] if g['stage']=='before']
        enclosed=sum(g['count'] for g in before if g['x']<384)
        need(enclosed==10 and values['before']==values['after']==13,'Exchange must preserve value13')
    return {'stage_values':values,'stage_counts':stages,'actual_unit_cells':actual_cells,
        'unit_cell_width_height':CELL,'visible_labels':[t for t,_,_ in visible],
        'exchange_preserves_value':spec['exchange'],'exact_geometry_colors_labels':True}


def self_test():
    rejected=0
    for name in NAMES:
        data=svg(name);check_svg(name,data)
        first=lambda r:next(e for e in r.iter(SVG+'g'))
        cell=lambda r:first(r)[0]
        mutations=[lambda r:first(r).remove(cell(r)),lambda r:first(r).append(copy.deepcopy(cell(r))),
            lambda r:cell(r).set('width','23'),lambda r:cell(r).set('x','0'),
            lambda r:cell(r).set('fill','#ffffff'),lambda r:first(r).set('data-count','999'),
            lambda r:r.set('opacity','0'),lambda r:r.append(ET.Element(SVG+'image',{'href':'wrong.png'})),
            lambda r:r.set('aria-labelledby','wrong'),lambda r:r.set('viewBox','0 0 1 1'),
            lambda r:setattr(r.find(SVG+'desc'),'text','wrong count'),lambda r:r[2].set('width','999')]
        if scene(name)['labels']:mutations.append(lambda r:setattr(next(r.iter(SVG+'text')),'text','999'))
        if scene(name)['exchange']:
            mutations.extend([lambda r:next(r.iter(SVG+'line')).set('y2','0'),
                lambda r:r.remove(next(e for e in r if e.get('data-role')=='exchange-enclosure'))])
        for change in mutations:
            candidate=ET.fromstring(data);change(candidate)
            try:check_svg(name,ET.tostring(candidate))
            except (ValueError,TypeError):rejected+=1
            else:raise AssertionError('Accepted corrupted diagram: '+name)
    print(json.dumps({'status':'PASS','valid_diagrams':19,'rejected_corruptions':rejected,'writes':0}))


def build(verify=False,originals_only=False):
    assets=originals(not verify)
    if originals_only:print(json.dumps(assets,ensure_ascii=False,indent=2));return
    outputs={}
    for asset,name in zip(assets,NAMES):
        data=svg(name);checks=check_svg(name,data);spec=scene(name)
        asset.update(localized_sha256=digest(data),localized_bytes=len(data),
            recommended_min_width_px=spec['width'],math_checks=checks,
            disclosure='New code-native mathematical redraw after full original pixel inspection; numeric labels/counts/stages preserved. Original raster unchanged; no image generation or raster editing.')
        if name==PREFIX+'018_img-04.png':asset['source_alt_correction']='Source alt places both rods and units on the right; inspected pixels put the3 rods on the left and13 ones on the right,including10 red ones. Frozen alt unchanged.'
        outputs[BASE/asset['localized_path']]=data
    manifest={'schema':'te-b002-assets-v1','unit':'TE-B014','source_subsection_id':'fs-id2145437',
        'source_subsection_sha256':SOURCE_SHA,'canonical_commit':COMMIT,'canonical_archive_sha256':ARCHIVE_SHA,
        'source_attribution':'OpenStax, Prealgebra 2e; existing project notices and source attribution remain applicable.',
        'generator':'scripts/make_b014_assets.py','verification_command':'python -B te-Telu-IN/scripts/make_b014_assets.py --verify',
        'assets':assets,'scope':'19exact selected unchanged source rasters and19code-native SVGs; no download,bulk extraction,catalog or bridge.',
        'choices':['Numeric-only source labels remain numeric; accessibility title/description are bilingual editorial additions.',
            'All unit cells use24x24pixels. Ten contiguous cells form each rod; separate units remain visibly spaced.',
            '017_img-04 retains the10-unit enclosure and downward exchange arrow; before/after are each13,not a combined26.',
            '018_img-04 retains10red units before exchange;018_img-05 retains the one new red ten rod.',
            'Source eip-951 declares3columns but every row contains2entries; this needs main renderer exception,not source mutation.',
            'Actual TS6PDF26/27 and TS2PDF32 OCR then complete images reread; no official AP or native-review claim.'],
        'qa':{'source_media_count':19,'localized_asset_count':19,'source_media_count_verified':True,
            'independent_visual_approval':False,'native_speaker_approval':False}}
    outputs[OUT/'manifest.json']=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    preview='<!doctype html><html lang="te"><meta charset="utf-8"><title>B014 asset author preview</title><style>body{font:18px sans-serif;margin:24px;color:#19354a}section{margin:32px 0;padding:16px;border:1px solid #ccc}img{display:block}h2{font-size:18px}</style><h1>B014 asset author preview</h1>'
    for a in assets:
        filename=Path(a['localized_path']).name
        preview+=f'<section><h2>{filename}</h2><img src="{filename}" alt="{a["media_id"]}"></section>'
    outputs[OUT/'preview.html']=(preview+'</html>\n').encode('utf-8')
    for path,data in outputs.items():
        if verify:need(path.read_bytes()==data,'Generated asset/manifest differs: '+path.name)
        else:write(path,data)
    print(json.dumps({'status':'PASS','assets':19,'original_bytes':sum(a['original_bytes'] for a in assets),
        'svg_bytes':sum(a['localized_bytes'] for a in assets),'crc_and_git_blob':'PASS','writes':0 if verify else len(outputs)}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);group=p.add_mutually_exclusive_group()
    group.add_argument('--originals-only',action='store_true');group.add_argument('--verify',action='store_true');group.add_argument('--self-test',action='store_true');args=p.parse_args()
    if args.self_test:self_test()
    else:build(args.verify,args.originals_only)
