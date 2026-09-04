"""B011 exact selected image preservation and verified B002 SVG reuse.

B012/B013 have no source media. No download or bulk extraction. Existing
original bytes are never overwritten; --verify/--self-test perform no writes.
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
from make_b002_assets import SVG,WORDS,VALUES,COLORS,math_check

BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parent;OUT=BASE/'assets/B011'
COMMIT='38cae454e644abf9f0a623e876994553881597c9'
ARCHIVE_SHA='effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917'
MODULE_SHA='b32058ce714e5fd43b010ccc81b2ae00a11567b229e9f96dda7b85b3cd82ba6b'
CN='{http://cnx.rice.edu/cnxml}'
SPECS={'TE-B011':('fs-id2299412','cdd73289f869830dcc51fb3df012c1b50d5ef191698dcfbea244d39dbc45cb83',1),
       'TE-B012':('fs-id1122444','9b680f02649625b9263c6fa2bc9aa9defaa93d94fec588ea203c7bbc7f291287',0),
       'TE-B013':('fs-id2601285','dc2f2c8ad88edb588df364026e9e5b4301d416ef641fc7c833d5ca4fe0f93b35',0)}
NAME='CNX_BMath_Figure_01_02_001_img.jpg'
DERIVATIVE=BASE/'assets/B002/CNX_BMath_Figure_01_01_007.te.svg'
DERIVATIVE_SHA='31998fa3ea7fb944eaa92768def5cadef79d463b8f639a390dcd12df6d3aa7c3'


def sources():
    roots={}
    for unit,(ident,sha,count) in SPECS.items():
        path=BASE/'sources'/f'{unit}.en.cnxml';need(file_digest(path)==sha,'Frozen source changed')
        meta=json.loads((BASE/'sources'/f'{unit}.source.json').read_text('utf-8'))
        need(meta['source_commit']==COMMIT and meta['source_sha256']==sha and meta['source_module']['sha256']==MODULE_SHA,'Unpinned source metadata')
        root=ET.parse(path).getroot();need(root.get('id')==ident,'Wrong source selection')
        need(len(list(root.iter(CN+'image')))==count,'Source media count changed');roots[unit]=root
    return roots


def original(write=False):
    root=sources()['TE-B011'];parents={c:p for p in root.iter() for c in p};image=next(root.iter(CN+'image'))
    need(image.get('src')=='../../media/'+NAME and parents[image].get('id')=='fs-id2778433','Wrong B011 media')
    lock=json.loads((BASE/'sources.lock.json').read_text('utf-8'))
    a=next(r for r in lock['canonical_archives'] if r['id']=='A00-A20-en-complete-archive')
    need(a['sha256']==ARCHIVE_SHA and a['commit']==COMMIT,'Unpinned archive record')
    archive=ROOT/a['path'];need(archive.stat().st_size==537455794 and file_digest(archive)==ARCHIVE_SHA,'Canonical archive changed')
    member_path='media/'+NAME;env=os.environ.copy();env.update(GIT_NO_LAZY_FETCH='1',GIT_TERMINAL_PROMPT='0')
    tree=subprocess.check_output(['git','-C',str(ROOT/'downloads/upstream-prealgebra'),'ls-tree','-z',COMMIT,'--',member_path],env=env)
    rows=[r for r in tree.split(b'\0') if r];need(len(rows)==1,'Pinned image missing')
    header,name=rows[0].split(b'\t');mode,kind,blob=header.split();need(kind==b'blob' and name.decode()==member_path,'Wrong Git member')
    member='osbooks-prealgebra-bundle-'+COMMIT+'/'+member_path
    with zipfile.ZipFile(archive) as z:
        need(z.comment.decode()==COMMIT,'Wrong ZIP comment');info=z.getinfo(member)
        need(0<info.file_size<2_000_000,'Selected image exceeds bound');data=z.read(member)
    need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==blob.decode(),'Image differs from pinned Git blob')
    destination=OUT/'original'/NAME
    if destination.exists():need(destination.read_bytes()==data,'Original differs; refusing overwrite')
    elif write:
        need(shutil.disk_usage(BASE).free>=32*1024*1024,'Below free-space guard')
        destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(data)
    else:raise FileNotFoundError(destination)
    return {'original_src':image.get('src'),'original_path':destination.relative_to(BASE).as_posix(),
        'original_sha256':digest(data),'original_bytes':len(data),'source_git_blob_sha1':blob.decode(),
        'source_zip_member':member,'source_zip_crc32':f'{info.CRC:08x}','media_id':'fs-id2778433','figure_id':None,
        'localized_path':'assets/B011/CNX_BMath_Figure_01_02_001_img.te.svg'}


def check_svg(payload):
    result=math_check(7,payload);root=ET.fromstring(payload)
    need(root.get('viewBox')=='0 0 960 370' and root.get('width')=='960' and root.get('height')=='370','Wrong SVG canvas')
    need(root.get('role')=='img' and root.get('aria-labelledby')=='title desc','Accessibility root changed')
    need({e.tag for e in root.iter()}<={SVG+t for t in ('svg','title','desc','rect','text','g')},'Unexpected raster/script/shape')
    need(not any(k in ('transform','display','visibility','opacity','style','href') or k.startswith('on') for e in root.iter() for k in e.attrib),'Hidden or transformed content')
    groups=[e for e in root.iter(SVG+'g') if e.get('data-kind') in VALUES]
    expected=[('hundred',31,128),('hundred',169,128),('ten',420,110),
              ('one',758,146),('one',782,146),('one',806,146),('one',830,146),('one',758,176)]
    need(len(groups)==len(expected),'Wrong actual group count');boxes=[]
    for group,(kind,ox,oy) in zip(groups,expected):
        need(group.get('data-kind')==kind and group.get('data-value')==str(VALUES[kind]),'Kind/value/order changed')
        nr,nc=(10,10) if kind=='hundred' else (1,10) if kind=='ten' else (1,1)
        cells=list(group);need(len(cells)==nr*nc,'Unit cell missing/extra')
        need({(int(e.get('data-row','-1')),int(e.get('data-col','-1'))) for e in cells}=={(r,c) for r in range(nr) for c in range(nc)},'False cell-index set')
        for cell in cells:
            row,col=int(cell.get('data-row')),int(cell.get('data-col'))
            need(tuple(float(cell.get(a)) for a in ('x','y','width','height'))==(ox+12*col,oy+12*row,12,12),'Wrong cell scale/location')
            need(cell.get('fill')==COLORS[kind][0] and cell.get('stroke')==COLORS[kind][1],'Cell visibility changed')
        boxes.append((ox,oy,12*nc,12*nr))
    for i,(x,y,w,h) in enumerate(boxes):
        for a,b,c,d in boxes[i+1:]:need(x+w<=a or a+c<=x or y+h<=b or b+d<=y,'Overlapping groups')
    need(len(list(root.iter(SVG+'rect')))==216,'Wrong total cell shapes')
    for rect in root.iter(SVG+'rect'):
        x,y=float(rect.get('x',0)),float(rect.get('y',0));w,h=float(rect.get('width')),float(rect.get('height'))
        need(x>=0 and y>=0 and x+w<=960 and y+h<=370 and w>0 and h>0,'Rectangle outside canvas')
    expected_text=[(WORDS[k][i],str(center),str(40+25*i)) for k,center in zip(('hundred','ten','one'),(160,480,800)) for i in (0,1)]
    need([(e.text,e.get('x'),e.get('y')) for e in root.iter(SVG+'text')]==expected_text,'Labels altered or visible answer added')
    result.update(actual_unit_rectangles=215,visible_answer=False,exact_cell_geometry_and_nonoverlap=True)
    return result


def reused_svg():
    payload=DERIVATIVE.read_bytes();need(digest(payload)==DERIVATIVE_SHA,'B002 reused derivative changed')
    manifest=json.loads((BASE/'assets/B002/manifest.json').read_text('utf-8'))
    asset=next(a for a in manifest['assets'] if a['localized_path']==DERIVATIVE.relative_to(BASE).as_posix())
    need(asset['localized_sha256']==DERIVATIVE_SHA,'B002 derivative manifest mismatch')
    check_svg(payload)
    return payload,{'unit':'TE-B002','path':asset['localized_path'],'sha256':DERIVATIVE_SHA,
        'original_basis':asset['original_path'],'original_basis_sha256':asset['original_sha256'],
        'difference':'Visible artwork and SVG bytes unchanged. Exact B011 source has different JPEG bytes/layout but the inspected mathematical groups agree.'}


def self_test():
    payload,_=reused_svg();mutators=[]
    group=lambda r:next(e for e in r.iter(SVG+'g') if e.get('data-kind')=='hundred')
    cell=lambda r:group(r)[0]
    mutators.extend([
        lambda r:r.set('viewBox','0 0 10 10'),lambda r:r.set('opacity','0'),
        lambda r:r.append(ET.Element(SVG+'image',{'href':'wrong.jpg'})),
        lambda r:group(r).remove(cell(r)),lambda r:group(r).append(copy.deepcopy(cell(r))),
        lambda r:cell(r).set('width','13'),lambda r:cell(r).set('x','0'),
        lambda r:cell(r).set('data-col','9'),lambda r:cell(r).set('fill','white'),
        lambda r:group(r).set('data-value','10'),lambda r:group(r).set('data-kind','ten'),
        lambda r:r.remove(next(e for e in r if e.get('data-kind')=='ten')),
        lambda r:r.append(copy.deepcopy(next(e for e in r if e.get('data-kind')=='one'))),
        lambda r:r.append(ET.Element(SVG+'text',{'x':'700','y':'300'})),
        lambda r:setattr(next(r.iter(SVG+'text')),'text','215'),
        lambda r:next(r.iter(SVG+'text')).set('x','959')])
    for mutate in mutators:
        candidate=ET.fromstring(payload);mutate(candidate)
        try:check_svg(ET.tostring(candidate))
        except (ValueError,TypeError):pass
        else:raise AssertionError('Accepted corrupted B011 image')
    print(json.dumps({'status':'PASS','valid_svg':1,'rejected_corruptions':len(mutators),'writes':0}))


def build(verify=False,originals_only=False):
    roots=sources();asset=original(write=not verify)
    if originals_only:print(json.dumps(asset,indent=2));return
    payload,reuse=reused_svg();asset.update(localized_sha256=digest(payload),localized_bytes=len(payload),
        recommended_min_width_px=960,math_checks=check_svg(payload),reused_derivative=reuse,
        original_dimensions_px=[261,151],disclosure='Reused verified B002 code-native bilingual block artwork after exact B011 JPEG pixel inspection. Original B011 bytes unchanged; no visible answer or raster editing.')
    outputs={BASE/asset['localized_path']:payload}
    for unit,(ident,source_sha,count) in SPECS.items():
        manifest={'schema':'te-b002-assets-v1','unit':unit,'source_subsection_id':ident,'source_subsection_sha256':source_sha,
            'canonical_commit':COMMIT,'source_attribution':'OpenStax, Prealgebra 2e; existing project notices and source attribution remain applicable.',
            'generator':'scripts/make_b011_assets.py','verification_command':'python -B te-Telu-IN/scripts/make_b011_assets.py --verify',
            'assets':[asset] if count else [],
            'scope':'One selected unchanged source JPEG and verified reused code-native SVG; no download or bulk extraction.' if count else 'Exact frozen source contains no media; no diagrams invented.',
            'qa':{'source_media_count':count,'localized_asset_count':count,'source_media_count_verified':True}}
        if count:
            manifest['canonical_archive_sha256']=ARCHIVE_SHA
            manifest['choices']=['Exact B011 JPEG is not the B002 JPEG; both full original images were inspected and contain two 100-cell flats,one 10-cell rod,five unit cells.',
                'Preserve the B011 original layout/bytes as provenance; reuse B002 artwork with an explicit derivative mapping,not a pixel-identity claim.',
                'Every unit cell has the same scale; the visible SVG has only Telugu/English place labels,no215 answer or numerical group counts.',
                'Revisited actual TS6 PDF27 and TS2 PDF44 OCR then complete images; preserve place labels and counting/group contribution distinction.',
                'No native-speaker or independent visual approval is claimed; main integrated-reader review remains separate.']
        outputs=outputs|{BASE/'assets'/unit.replace('TE-','')/'manifest.json':(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf-8')}
    for path,data in outputs.items():
        if verify:need(path.read_bytes()==data,'Existing asset/manifest differs: '+path.name)
        else:
            need(shutil.disk_usage(BASE).free>=32*1024*1024,'Below free-space guard')
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    print(json.dumps({'status':'PASS','source_units':3,'original_bytes':asset['original_bytes'],'localized_svg_bytes':len(payload),
        'selected_original_sha_crc_git_blob':'PASS','block_geometry_counts':'PASS','empty_asset_manifests':['TE-B012','TE-B013']}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);g=parser.add_mutually_exclusive_group()
    g.add_argument('--originals-only',action='store_true');g.add_argument('--verify',action='store_true');g.add_argument('--self-test',action='store_true');args=parser.parse_args()
    if args.self_test:self_test()
    else:build(args.verify,args.originals_only)
