"""Freeze the next contiguous worked example and its unchanged local assets."""
from pathlib import Path
import copy
import csv
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
CNXML = 'http://cnx.rice.edu/cnxml'
ET.register_namespace('', CNXML)
prior = json.loads((BASE/'source-excerpts/manifest.json').read_text(encoding='utf-8'))
source = ROOT/'downloads/m49301.cnxml'
assert hashlib.sha256(source.read_bytes()).hexdigest() == prior['full_module_sha256']
doc = ET.parse(source).getroot()
example = next(e for e in doc.iter() if e.get('id') == 'Example_01_01_01')
excerpt = ET.Element('{'+CNXML+'}document', {'id':'m49301-menu-excerpt'})
selected = copy.deepcopy(example)
selected.tail = None
excerpt.append(selected)
output = BASE/'source-excerpts/m49301-menu.cnxml'
ET.ElementTree(excerpt).write(output, encoding='utf-8', xml_declaration=True)
images = []
for number, label in [('004','1.1.2'),('027','1.1.3'),('028','1.1.4')]:
    filename = f'CNX_Precalc_Figure_01_01_{number}.jpg'
    original = ROOT/'downloads/complete-upstream/osbooks-college-algebra-bundle/media'/filename
    target = BASE/'assets'/f'Figure_01_01_{number}.jpg'
    shutil.copyfile(original, target)
    images.append({'figure_id':f'Figure_01_01_{number}', 'source_path':'media/'+filename,
                   'path':target.relative_to(BASE).as_posix(), 'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
                   'width':584,'height':281,'local_label':label,'treatment':'unchanged English source image; Punjabi alt and labeled bilingual legend'})
with (ROOT/'downloads/extracted/A30/00_control/COMPONENT_RIGHTS.csv').open(encoding='utf-8-sig',newline='') as f:
    notices = [row for row in csv.DictReader(f) if any(image['source_path'].split('/')[-1] in str(row) for image in images)]
assert len(notices) == 3, 'Expected existing component notices for all three images'
(BASE/'provenance/menu-component-notices.json').write_text(json.dumps(notices,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest = {'unit':'PNB-002','purpose':'bounded translation source witness; not training or fine-tuning',
            'commit':prior['commit'],'module':prior['module'],'path':prior['path'],
            'upstream_url':prior['upstream_url'],'full_module_sha256':prior['full_module_sha256'],
            'source_excerpt':'m49301-menu.cnxml','selection':'Example_01_01_01 in full, including its two solutions and three figures',
            'excerpt_sha256':hashlib.sha256(output.read_bytes().replace(b'\r\n',b'\n')).hexdigest(),
            'next_source_id':'Example_01_01_02','images':images}
(BASE/'source-excerpts/manifest-002.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(manifest,indent=2))
