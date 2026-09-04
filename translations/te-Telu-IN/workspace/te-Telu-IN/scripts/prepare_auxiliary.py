"""Freeze only m81243's omitted glossary and module opening as B009/B010.

The glossary keeps its original root without a synthetic section, ID or title.
The module-opening document is an explicit title+metadata selection, excluding
content and glossary. No download, corpus scan or translation/build mutation.
--verify and --self-test are read-only. Existing differing outputs are refused.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urlsplit
from inspect_source import slots, CN, MATH

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parent
MD='{http://cnx.rice.edu/mdml}'
COMMIT='38cae454e644abf9f0a623e876994553881597c9'
MODULE_SHA='396b0029798e054e5db6d7acde738cec9f9d8b86bc81da8cc3690d01ec07cf2b'
MODULE_BLOB='612244f80ecb6bce0f811c9d99204ae2f9f7a4f5'
MODULE_PATH='downloads/upstream-prealgebra/modules/m81243/index.cnxml'
UUID='7cbc90c7-60c8-4211-bffe-b77aadc95509'
UNITS={'TE-B009':('@glossary',22,14),'TE-B010':('@module-frontmatter',15,11)}
ET.register_namespace('',CN[1:-1]);ET.register_namespace('md',MD[1:-1]);ET.register_namespace('m',MATH[1:-1])


def need(value,message):
    if not value:raise ValueError(message)


def sha(data):return hashlib.sha256(data).hexdigest()


def module_input():
    lock=json.loads((BASE/'sources.lock.json').read_text('utf-8'))
    rows=[r for r in lock['source_files'] if r['course']=='A00' and r['module']=='m81243' and r['role']=='canonical_english']
    need(len(rows)==1,'Canonical module record missing/ambiguous');record=rows[0]
    need(record['path']==MODULE_PATH and record['bytes']==99062 and record['sha256']==MODULE_SHA,'Canonical source record drift')
    collection=next(r for r in lock['collections'] if r['course']=='A00')
    repo=next(r for r in lock['repositories'] if r['id']==collection['upstream_repository_id'])
    need(repo['commit']==COMMIT,'Canonical commit drift')
    raw=(ROOT/MODULE_PATH).read_bytes()
    need(len(raw)==99062 and sha(raw)==MODULE_SHA,'Canonical module bytes changed')
    env=os.environ.copy();env.update(GIT_NO_LAZY_FETCH='1',GIT_TERMINAL_PROMPT='0')
    tree=subprocess.check_output(['git','-C',str(ROOT/'downloads/upstream-prealgebra'),'ls-tree','-z',COMMIT,'--','modules/m81243/index.cnxml'],env=env)
    entries=[e for e in tree.split(b'\0') if e];need(len(entries)==1,'Pinned Git module missing')
    header,name=entries[0].split(b'\t');mode,kind,blob=header.split()
    need(kind==b'blob' and name==b'modules/m81243/index.cnxml' and blob.decode()==MODULE_BLOB,'Pinned Git blob changed')
    need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==MODULE_BLOB,'Source differs from pinned Git blob')
    root=ET.fromstring(raw)
    need(root.tag==CN+'document' and [e.tag for e in root]==[CN+'title',CN+'metadata',CN+'content',CN+'glossary'],'Unexpected module root/order')
    need(root.findtext(CN+'metadata/'+MD+'content-id')=='m81243' and root.findtext(CN+'metadata/'+MD+'uuid')==UUID,'Protected metadata drift')
    return root,record


def selection(unit,module):
    if unit=='TE-B009':
        result=copy.deepcopy(module.find(CN+'glossary'));result.tail=None
    elif unit=='TE-B010':
        result=ET.Element(module.tag,dict(module.attrib));result.text=module.text
        for tag in ('title','metadata'):result.append(copy.deepcopy(module.find(CN+tag)))
        result.tail=None
    else:raise ValueError('Only TE-B009/TE-B010 are authorized')
    return result


def signature(root):
    return (root.tag,tuple(sorted(root.attrib.items())),root.text,root.tail,tuple(signature(e) for e in root))


def validate_selection(unit,selected,module):
    expected=selection(unit,module)
    need(signature(selected)==signature(expected),'Auxiliary source selection altered source structure/text')
    sentinel,elements,count=UNITS[unit]
    need(len(list(selected.iter()))==elements and len(list(slots(selected)))==count,'Auxiliary source counts changed')
    need(selected.get('id') is None and not list(selected.iter(CN+'image')),'Synthetic ID or unexpected media')
    if unit=='TE-B009':
        need(selected.tag==CN+'glossary' and len(selected)==7 and selected.find(CN+'title') is None,'Glossary root/title changed')
    else:
        need(selected.tag==CN+'document' and [e.tag for e in selected]==[CN+'title',CN+'metadata'],'Opening selection changed')
        need(selected.find(CN+'content') is None and selected.find(CN+'glossary') is None,'Excluded module content leaked into opening')


def products(unit,module,record):
    selected=selection(unit,module);validate_selection(unit,selected,module)
    payload=ET.tostring(selected,encoding='utf-8',xml_declaration=True)+b'\n'
    parsed=ET.fromstring(payload);validate_selection(unit,parsed,module)
    sentinel,elements,count=UNITS[unit]
    detail={'kind':'exact-root-child' if unit=='TE-B009' else 'document-child-subset',
        'original_document_tag':module.tag,'selected_root_tag':selected.tag,'synthetic_source_id':False,
        'selected_paths':['/document/glossary'] if unit=='TE-B009' else ['/document/title','/document/metadata'],
        'excluded_paths':['/document/title','/document/metadata','/document/content'] if unit=='TE-B009' else ['/document/content','/document/glossary'],
        'serialization':'UTF-8 XML serialization of unchanged selected element graph; namespace declarations normalized, only selected root exterior tail removed.',
        'section_sentinel_is_catalog_metadata_only':True}
    protected={}
    if unit=='TE-B010':
        protected={'s002':{'tag':MD+'content-id','value':'m81243','reason':'Canonical module identifier; not prose.'},
                   's011':{'tag':MD+'uuid','value':UUID,'reason':'Canonical module UUID; not prose.'}}
        items=list(slots(selected))
        for key,value in protected.items():
            e,field,text=items[int(key[1:])-1]
            need(e.tag==value['tag'] and field=='text' and text==value['value'],'Protected slot mapping drift')
    meta={'schema':'te-source-unit-v1','unit':unit,'course':'A00','module':'m81243','section':sentinel,
        'title_en':selected.findtext(CN+'title'),'source_commit':COMMIT,'source_module':record,
        'source_module_git_blob_sha1':MODULE_BLOB,'source_sha256':sha(payload),'text_slots':count,'element_count':elements,
        'selection':detail,'protected_slots':protected,
        'scope':'Exact complete glossary only; module opening/content excluded.' if unit=='TE-B009' else 'Module title and complete metadata/objectives only; content and glossary explicitly excluded.',
        'purpose':'human-reviewable translation input; never model training data'}
    manifest={'schema':'te-b002-assets-v1','unit':unit,'source_subsection_id':sentinel,'source_subsection_sha256':sha(payload),
        'canonical_commit':COMMIT,'generator':'scripts/prepare_auxiliary.py',
        'verification_command':'python -B te-Telu-IN/scripts/prepare_auxiliary.py --verify',
        'scope':'This exact source selection contains no media; no diagrams invented.','assets':[],
        'qa':{'source_media_count':0,'localized_asset_count':0,'empty_manifest_verified_against_source':True}}
    encode=lambda v:(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    return {BASE/'sources'/f'{unit}.en.cnxml':payload,BASE/'sources'/f'{unit}.source.json':encode(meta),
            BASE/'assets'/unit.replace('TE-','')/'manifest.json':encode(manifest)}


def atomic_write(path,data):
    need(shutil.disk_usage(BASE).free>=32*1024*1024,'Below 32 MiB free-space guard')
    need(len(data)<65536,'Unexpected auxiliary output size')
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=None
    try:
        with tempfile.NamedTemporaryFile(prefix=path.name+'.',suffix='.tmp',dir=path.parent,delete=False) as stream:
            temp=Path(stream.name);stream.write(data);stream.flush();os.fsync(stream.fileno())
        need(temp.read_bytes()==data,'Atomic-write verification failed')
        os.replace(temp,path);temp=None
    finally:
        if temp is not None and temp.exists():temp.unlink()


def run(verify=False):
    module,record=module_input();outputs={}
    for unit in UNITS:outputs.update(products(unit,module,record))
    # Preflight all six destinations before any mutation, preserving prior files.
    for path,data in outputs.items():
        if path.exists():need(path.read_bytes()==data,'Existing auxiliary output differs; refusing overwrite: '+str(path))
        else:need(not verify,'Missing frozen output: '+str(path))
    if not verify:
        need(shutil.disk_usage(BASE).free>=32*1024*1024,'Below 32 MiB free-space guard')
        for path,data in outputs.items():
            if not path.exists():atomic_write(path,data)
    print(json.dumps({'status':'PASS','mode':'verify-read-only' if verify else 'prepare','outputs':[
        {'path':p.relative_to(BASE).as_posix(),'bytes':len(d),'sha256':sha(d)} for p,d in outputs.items()]},indent=2))


def self_test():
    module,record=module_input();rejected=0
    def reject(unit,mutate):
        nonlocal rejected
        candidate=selection(unit,module);mutate(candidate)
        try:validate_selection(unit,candidate,module)
        except ValueError:rejected+=1
        else:raise AssertionError('Corrupted source selection accepted')
    for unit in UNITS:
        products(unit,module,record)
        reject(unit,lambda r:r.set('id','invented-id'))
        reject(unit,lambda r:r.append(ET.Element(CN+'section')))
        reject(unit,lambda r:r.remove(list(r)[0]))
        reject(unit,lambda r:setattr(next(e for e in r.iter() if e.text and e.text.strip()),'text','Changed English'))
    reject('TE-B009',lambda r:r.insert(0,ET.Element(CN+'title')))
    reject('TE-B010',lambda r:setattr(r.find(CN+'metadata/'+MD+'content-id'),'text','m81244'))
    reject('TE-B010',lambda r:setattr(r.find(CN+'metadata/'+MD+'uuid'),'text','new-uuid'))
    reject('TE-B010',lambda r:r.append(copy.deepcopy(module.find(CN+'content'))))
    print(json.dumps({'status':'PASS','valid_selections':2,'rejected_corruptions':rejected,'writes':0}))


def review_catalog(unit,source,meta,catalog):
    """Author-only in-memory content checks; not the general unit compiler."""
    need(catalog['unit_id']==unit and catalog['module_id']=='m81243' and catalog['source_commit']==COMMIT,'Catalog identity drift')
    need(catalog['section_id']==meta['section']==UNITS[unit][0],'Catalog sentinel drift')
    need(catalog['protected_slots']==meta['protected_slots'],'Protected metadata declarations changed')
    need(catalog['editorial_title_is_source_content'] is False and catalog['editorial_title_te'] and catalog['editorial_title_en'],'Editorial heading not disclosed')
    target=copy.deepcopy(source);items=list(slots(target))
    need(len(items)==catalog['expected_text_slot_count']==UNITS[unit][2],'Catalog slot count changed')
    expected={f's{i:03}' for i in range(1,len(items)+1)}-set(meta['protected_slots'])
    need(set(catalog['translations'])==expected,'Missing/extra/protected translation slot')
    for i,(element,field,value) in enumerate(items,1):
        key=f's{i:03}'
        if key in meta['protected_slots']:
            protected=meta['protected_slots'][key]
            need(element.tag==protected['tag'] and field=='text' and value==protected['value'],'Protected slot altered')
        else:
            translated=catalog['translations'][key]
            need(re.search('[\u0c00-\u0c7f]',translated),'Missing Telugu prose')
            need(re.findall(r'\d+',value)==re.findall(r'\d+',translated),'Source numeric text changed')
            setattr(element,field,translated)
    need([(e.tag,e.get('id'),dict(e.attrib)) for e in source.iter()]==[(e.tag,e.get('id'),dict(e.attrib)) for e in target.iter()],'Structure/IDs/attributes changed')
    if unit=='TE-B009':
        for slot,term in {'s001':'నిరూపకం (coordinate)','s003':'సహజ సంఖ్యలు (counting numbers)',
                          's005':'సంఖ్యారేఖ (number line)','s007':'మూలబిందువు (origin)',
                          's013':'పూర్ణాంకాలు (whole numbers)'}.items():
            need(catalog['translations'][slot]==term,'Course glossary label changed')
        need('ఈ పాఠంలో' in catalog['translations']['s012'],'Broad rounding definition lost its context qualification')
    else:
        need(catalog['translations']['s001']==catalog['translations']['s003']=='పూర్ణాంకాలకు పరిచయం','Module titles inconsistent')
        need('అక్షరాలలో' in catalog['translations']['s008'] and 'అంకెలలో' in catalog['translations']['s009'],'Naming/writing objectives confused')
        need(target.findtext(CN+'metadata/'+MD+'content-id')=='m81243' and target.findtext(CN+'metadata/'+MD+'uuid')==UUID,'Protected metadata not retained')
    target.set('{http://www.w3.org/XML/1998/namespace}lang','te-Telu-IN')
    return target


class ReaderIds(HTMLParser):
    def __init__(self):super().__init__();self.ids=set()
    def handle_starttag(self,tag,attrs):self.ids.update(v for k,v in attrs if k=='id')


def review_bridge(unit,bridge,source):
    need(bridge.tag=='{http://www.w3.org/1999/xhtml}section' and bridge.get('id')==unit.replace('TE-','')+'-bridge','Wrong bridge root')
    ids=[e.get('id') for e in bridge.iter() if e.get('id')]
    need(len(ids)==len(set(ids)) and not set(ids)&{e.get('id') for e in source.iter() if e.get('id')},'Duplicate/colliding IDs')
    need(not any(e.tag.rsplit('}',1)[-1] in ('script','form','iframe','img','svg') for e in bridge.iter()),'Unexpected interactive/media bridge addition')
    by_id={e.get('id'):''.join(e.itertext()) for e in bridge.iter() if e.get('id')}
    expected={'B009-place-example':['3 × 10 = 30','3 × 1 = 3'],
              'B009-rounding-example':['76 − 70 = 6','80 − 76 = 4'],
              'B009-estimation-example':['10 × 5 = 50']} if unit=='TE-B009' else {'B010-place-example':['4 × 10 = 40']}
    for key,values in expected.items():need(key in by_id and all(v in by_id[key] for v in values),'Added worked example changed')
    text=' '.join(bridge.itertext());equations=re.findall(r'(\d+)\s*([×−])\s*(\d+)\s*=\s*(\d+)',text)
    for a,op,b,value in equations:need((int(a)*int(b) if op=='×' else int(a)-int(b))==int(value),'Incorrect actual bridge equation')
    need(len(equations)==(5 if unit=='TE-B009' else 1),'Unexpected equation count')
    links=[]
    for element in bridge.iter():
        if element.get('href'):
            url=urlsplit(element.get('href'))
            need(not url.scheme and not url.netloc and not url.query and re.fullmatch(r'TE-B00[1-6]\.html',url.path),'Unexpected support URL')
            reader=ReaderIds();reader.feed((BASE/'reader'/url.path).read_text('utf-8'))
            need(url.fragment in reader.ids,'Missing existing-reader anchor: '+element.get('href'));links.append(element.get('href'))
    need(len(links)==(7 if unit=='TE-B009' else 12),'Support link coverage drift')
    if unit=='TE-B009':
        need('not every kind' in text and 'not round a previously known exact count' in text,'Estimation/rounding distinction missing')
        need('నిర్ధారణ లేదు' in by_id['B009-term-status'],'Provisional terminology disclosure missing')
    else:need('TE-B002.html#fs-id1227376' in links and 'no separate recheck bank' in text,'B002 source-practice routing misrepresented')
    return {'bridge_ids':len(ids),'support_links':len(links),'actual_equations':len(equations)}


def check_translations():
    module,record=module_input();reports=[]
    for unit in UNITS:
        for path,data in products(unit,module,record).items():need(path.read_bytes()==data,'Prepared source/metadata/manifest changed')
        source_raw=(BASE/'sources'/f'{unit}.en.cnxml').read_bytes();source=ET.fromstring(source_raw)
        meta=json.loads((BASE/'sources'/f'{unit}.source.json').read_text('utf-8'))
        cat_raw=(BASE/'translations'/f'{unit}.te.json').read_bytes();catalog=json.loads(cat_raw)
        bridge_raw=(BASE/'translations'/f'{unit}.bridge.xhtml').read_bytes();bridge=ET.fromstring(bridge_raw)
        target=review_catalog(unit,source,meta,catalog);checks=review_bridge(unit,bridge,source)
        out=ET.tostring(target,encoding='utf-8',xml_declaration=True)+b'\n'
        reports.append({'unit':unit,'status':'PASS','source_sha256':sha(source_raw),'catalog_sha256':sha(cat_raw),'bridge_sha256':sha(bridge_raw),
            'elements':len(list(target.iter())),'source_ids':sum(bool(e.get('id')) for e in source.iter()),
            'source_slots':len(list(slots(source))),'localized_slots':len(catalog['translations']),
            'protected_slots':len(catalog['protected_slots']),**checks,
            'in_memory_target_bytes':len(out),'in_memory_target_sha256':sha(out),'generated_output_written':False})
    print(json.dumps({'scope':'Author-only content checks; no independent or rendered review claim','reports':reports},ensure_ascii=False,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group()
    group.add_argument('--verify',action='store_true');group.add_argument('--self-test',action='store_true')
    group.add_argument('--check-translations',action='store_true');args=parser.parse_args()
    if args.self_test:self_test()
    elif args.check_translations:check_translations()
    else:run(args.verify)
