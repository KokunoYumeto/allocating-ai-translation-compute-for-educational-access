"""Freeze contiguous, text/table-only units from the already acquired source."""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import xml.etree.ElementTree as ET
import csv
import shutil
from qa_menu import jpeg_dimensions

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
CNXML = 'http://cnx.rice.edu/cnxml'
ET.register_namespace('',CNXML)
ET.register_namespace('m','http://www.w3.org/1998/Math/MathML')
parser = argparse.ArgumentParser()
parser.add_argument('--unit',required=True,choices=['003','004'])
args = parser.parse_args()
selections = {'003':['Example_01_01_02','fs-id1165137588587'], '004':['fs-id1165134474160']}
next_ids = {'003':'fs-id1165134474160', '004':'fs-id1165137804204'}
prior = json.loads((BASE/'source-excerpts/manifest.json').read_text(encoding='utf-8'))
source = ROOT/'downloads/m49301.cnxml'
assert hashlib.sha256(source.read_bytes()).hexdigest() == prior['full_module_sha256']
document = ET.parse(source).getroot()
by_id = {e.get('id'):e for e in document.iter() if e.get('id')}
parents = {c:p for p in document.iter() for c in p}
selected = [by_id[sid] for sid in selections[args.unit]]
siblings = list(parents[selected[0]])
start = siblings.index(selected[0])
assert siblings[start:start+len(selected)] == selected
assert siblings[start+len(selected)].get('id') == next_ids[args.unit]
excerpt = ET.Element('{'+CNXML+'}document',{'id':f'm49301-unit-{args.unit}-excerpt'})
for node in selected:
    clone = copy.deepcopy(node)
    clone.tail = None
    excerpt.append(clone)
images = []
notices = []
with (ROOT/'downloads/extracted/A30/00_control/COMPONENT_RIGHTS.csv').open(encoding='utf-8-sig',newline='') as f:
    existing_notices = list(csv.DictReader(f))
for figure in excerpt.iter('{'+CNXML+'}figure'):
    media = figure.find('{'+CNXML+'}media')
    image = media.find('{'+CNXML+'}image')
    filename = image.get('src').split('/')[-1]
    source_path = 'media/'+filename
    original = ROOT/'downloads/complete-upstream/osbooks-college-algebra-bundle'/source_path
    notice = next(row for row in existing_notices if row['asset_path'] == source_path)
    data = original.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    assert digest == notice['sha256'], 'Image differs from retained component witness'
    assert notice['admission'] == 'admitted', 'Selected component is not admitted in existing supplied record'
    width,height = jpeg_dimensions(data)
    target = BASE/'assets'/(figure.get('id')+'.jpg')
    shutil.copyfile(original,target)
    images.append({'figure_id':figure.get('id'),'source_path':source_path,'path':target.relative_to(BASE).as_posix(),
                   'sha256':digest,'width':width,'height':height,'local_label':'1.1.5',
                   'treatment':'unchanged English image with translated alt and original bilingual legend'})
    notices.append(notice)
if notices:
    (BASE/f'provenance/unit-{args.unit}-component-notices.json').write_text(json.dumps(notices,indent=2)+'\n',encoding='utf-8')
filename = f'm49301-unit-{args.unit}.cnxml'
destination = BASE/'source-excerpts'/filename
ET.ElementTree(excerpt).write(destination,encoding='utf-8',xml_declaration=True)
references = []
for index,table in enumerate(excerpt.iter('{'+CNXML+'}table'),1):
    references.append({'id':table.get('id'),'kind':'table','local_label':f'1.1.{index}'})
manifest = {key:prior[key] for key in ('commit','module','path','upstream_url','full_module_sha256')}
manifest.update({'unit':f'PNB-{args.unit}','purpose':'bounded translation source witness; not training or fine-tuning',
                 'source_excerpt':filename,'selection_ids':selections[args.unit],'next_source_id':next_ids[args.unit],
                 'excerpt_sha256':hashlib.sha256(destination.read_bytes().replace(b'\r\n',b'\n')).hexdigest(),'images':images,'references':references})
(BASE/f'source-excerpts/manifest-{args.unit}.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps(manifest,indent=2))
