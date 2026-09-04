"""Verify the exact B007 PNG and reuse the checked B003 code-native artwork.

No network, lazy fetch or bulk extraction. --verify/--self-test are read-only.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from make_b003_assets import need, digest, file_digest, chart, math_check, SVG

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parent
OUT=BASE/'assets/B007'
SOURCE=BASE/'sources/TE-B007.en.cnxml'
SOURCE_SHA='56a5347ea8916c1d263ccf643fd6fd64ad98a2fdc8dcce33e7e1917d6e8b4f10'
COMMIT='38cae454e644abf9f0a623e876994553881597c9'
ARCHIVE_SHA='effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917'
NAME='CNX_BMath_Figure_01_01_011.png'
SOURCE_SVG='assets/B003/CNX_BMath_Figure_01_01_011.te.svg'
SOURCE_SVG_SHA='39c8e72b46a9f900a5c8837f22edcf10a99b5c8219b2a8f33e70c38c0b9c7fba'
CN='{http://cnx.rice.edu/cnxml}'


def original(write=False):
    need(file_digest(SOURCE)==SOURCE_SHA,'B007 source changed')
    meta=json.loads((BASE/'sources/TE-B007.source.json').read_text('utf-8'))
    need(meta['source_sha256']==SOURCE_SHA and meta['source_commit']==COMMIT,'Unpinned B007 metadata')
    root=ET.parse(SOURCE).getroot();images=list(root.iter(CN+'image'));media=list(root.iter(CN+'media'))
    need(root.get('id')=='fs-id2296006' and len(images)==len(media)==1,'Wrong source subsection/media count')
    need(images[0].get('src')=='../../media/'+NAME and media[0].get('id')=='eip-id1170196618449','Wrong B007 media')
    lock=json.loads((BASE/'sources.lock.json').read_text('utf-8'))
    archive=next(x for x in lock['canonical_archives'] if x['id']=='A00-A20-en-complete-archive')
    need(archive['commit']==COMMIT and archive['sha256']==ARCHIVE_SHA,'Wrong archive pin')
    path=ROOT/archive['path'];need(path.stat().st_size==archive['bytes'] and file_digest(path)==ARCHIVE_SHA,'Archive size/SHA mismatch')
    env=os.environ.copy();env.update(GIT_NO_LAZY_FETCH='1',GIT_TERMINAL_PROMPT='0')
    name='media/'+NAME
    tree=subprocess.check_output(['git','-C',str(ROOT/'downloads/upstream-prealgebra'),'ls-tree','-z',COMMIT,'--',name],env=env)
    header,listed=tree.rstrip(b'\0').split(b'\t');mode,kind,oid=header.split()
    need(kind==b'blob' and listed.decode()==name,'Wrong pinned Git object')
    with zipfile.ZipFile(path) as z:
        need(z.comment.decode()==COMMIT,'Wrong ZIP comment')
        member='osbooks-prealgebra-bundle-'+COMMIT+'/'+name;info=z.getinfo(member)
        need(0<info.file_size<2_000_000,'Original exceeds small-file limit')
        data=z.read(member)
    need(data.startswith(b'\x89PNG\r\n\x1a\n'),'B007 original is not PNG')
    blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();need(blob==oid.decode(),'Original Git blob mismatch')
    target=OUT/'original'/NAME
    if target.exists():need(target.read_bytes()==data,'Preserved original changed; no overwrite')
    elif write:
        need(shutil.disk_usage(BASE).free>32*1024*1024,'Insufficient free space')
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    else:raise FileNotFoundError(target)
    return {'original_src':'../../media/'+NAME,'original_path':target.relative_to(BASE).as_posix(),
        'original_sha256':digest(data),'original_bytes':len(data),'source_git_blob_sha1':blob,
        'source_zip_member':member,'source_zip_crc32':f'{info.CRC:08x}',
        'media_id':'eip-id1170196618449','figure_id':'eip-id1170196618448',
        'localized_path':'assets/B007/CNX_BMath_Figure_01_01_011.te.svg'}


def localized():
    source=(BASE/SOURCE_SVG).read_bytes()
    need(digest(source)==SOURCE_SVG_SHA and source==chart(11),'B003 artwork changed')
    math_check(11,source)
    # Artwork remains identical. Update only accessible provenance for the PNG
    # used by this recap; do not call the B007 original a JPEG.
    tree=ET.fromstring(source);desc=tree.find(SVG+'desc')
    desc.text=desc.text.replace('New code-native redraw, not an altered source JPEG.',
        'Code-native B003 artwork reused after inspecting the exact B007 source PNG; original PNG unchanged.')
    ET.indent(tree,space='  ')
    return ET.tostring(tree,encoding='utf-8',xml_declaration=True)+b'\n'


def check(payload):
    result=math_check(11,payload)
    need(payload==localized(),'Reused artwork or accessible provenance differs')
    return result


def self_test():
    data=localized();check(data);rejected=0
    for case in range(7):
        tree=ET.fromstring(data);cols=[e for e in tree.iter(SVG+'g') if e.get('data-role')=='place-column']
        if case==0: next(e for e in cols[-1] if e.get('data-role')=='digit').text='9'
        elif case==1:cols[8].set('data-exponent','7')
        elif case==2:cols[0].append(ET.Element(SVG+'text',{'data-role':'digit'}));cols[0][-1].text='0'
        elif case==3:next(e for e in cols[8] if e.get('data-role')=='place-name-en').text='Lakhs'
        elif case==4:next(e for e in tree.iter(SVG+'g') if e.get('data-role')=='period').set('data-column-count','2')
        elif case==5:tree.find(SVG+'desc').text='Wrong JPEG provenance'
        else:next(e for e in cols[-1] if e.get('data-role')=='digit').set('x','1')
        try:check(ET.tostring(tree))
        except ValueError:rejected+=1
        else:raise AssertionError('Accepted corruption'+str(case))
    print(f'PASS:15 places,5 periods,8 leading blanks,5,278,194;{rejected} corruptions rejected;no writes')


def build(verify=False,originals_only=False):
    record=original(write=not verify)
    if originals_only:print(json.dumps(record));return
    need(shutil.disk_usage(BASE).free>32*1024*1024,'Insufficient free space')
    data=localized();record.update(localized_sha256=digest(data),localized_bytes=len(data),
        recommended_min_width_px=2240,math_checks=check(data),
        reused_derivative={'unit':'TE-B003','path':SOURCE_SVG,'sha256':SOURCE_SVG_SHA,
            'original_basis':'assets/B003/original/CNX_BMath_Figure_01_01_011.jpg',
            'difference':'Visible artwork unchanged; accessible desc updated to identify exact B007 PNG and reuse.'},
        disclosure='Reused code-native B003 bilingual artwork after independent inspection of exact B007 PNG; not raster editing. Original B007 PNG unchanged.')
    path=BASE/record['localized_path']
    if verify:check(path.read_bytes());need(path.read_bytes()==data,'Localized bytes changed')
    else:path.write_bytes(data)
    manifest={'schema':'te-b002-assets-v1','unit':'TE-B007','source_subsection_id':'fs-id2296006',
        'source_subsection_sha256':SOURCE_SHA,'canonical_commit':COMMIT,'canonical_archive_sha256':ARCHIVE_SHA,
        'source_attribution':'OpenStax, Prealgebra 2e; existing project notices and attribution remain applicable.',
        'generator':'scripts/make_b007_assets.py','verification_command':'python -B te-Telu-IN/scripts/make_b007_assets.py --verify',
        'scope':'One exact pinned B007 PNG and one reused code-native SVG; no download or bulk extraction.',
        'choices':['Read complete frozen English and Indonesian Key Concepts; reread TS6 OCR13/14/15 then complete page images for naming/writing, rounding and zero positions.',
            '011.png is a distinct pinned source member from B003 011.jpg; preserve exact PNG bytes and inspect before reuse. Source declares JPEG MIME despite PNG signature.',
            'Viewed both full original images: B007 PNG uses a blue-gray header/blue grid whereas B003 JPEG uses teal. Their15 place columns,labels and5278194 positions agree; this is content equivalence, not byte/pixel equivalence.',
            'Inspected B007 PNG:15 columns,5 periods,8 initial blanks,then5/2/7/8/1/9/4; title/place header/period bands preserved by B003 artwork.',
            'Retain international three-digit periods; million/billion/trillion Telugu forms are editorial bilingual labels, not claimed official TS/AP vocabulary.',
            'Only accessible provenance text differs from B003 SVG. Correct B007 media and figure IDs map independently to this derivative.',
            'Rendered integrated reader inspection remains main-task work; no independent visual or native-speaker approval is claimed.'],
        'assets':[record],'qa':{'selected_original_count':1,'original_bytes':record['original_bytes'],'localized_svg_count':1,
            'localized_bytes':len(data),'all_values_positions_labels':'PASS','original_crc_git_blob_archive_sha':'PASS',
            'visual_review':'B007 original PNG inspected; reused artwork identified exactly. Main integrated render review pending.'}}
    encoded=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()
    if verify:need((OUT/'manifest.json').read_bytes()==encoded,'Manifest changed')
    else:
        (OUT/'manifest.json').write_bytes(encoded)
        (OUT/'preview.html').write_text('<!doctype html><html lang="te"><meta charset="utf-8"><title>B007 chart</title><style>body{font-family:Nirmala UI,sans-serif}img{display:block}.pan{overflow-x:auto;max-width:100%}</style><h1>B007 source and reused chart</h1><img src="original/'+NAME+'" alt="Preserved B007 source PNG"><div class="pan" tabindex="0" role="region" aria-label="15-column bilingual chart"><img src="CNX_BMath_Figure_01_01_011.te.svg" width="2240" alt="Place values, five periods and5,278,194"></div></html>\n',encoding='utf-8')
    print(json.dumps({'status':'PASS',**manifest['qa']}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--originals-only',action='store_true');p.add_argument('--verify',action='store_true');p.add_argument('--self-test',action='store_true');args=p.parse_args()
    need(sum((args.originals_only,args.verify,args.self_test))<=1,'Choose one action')
    if args.self_test:self_test()
    else:build(args.verify,args.originals_only)
