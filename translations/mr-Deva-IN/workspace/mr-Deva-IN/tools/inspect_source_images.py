"""Render contact sheets of source equation images for translation QA only."""
from pathlib import Path
import hashlib
import json
import zipfile
import xml.etree.ElementTree as ET
from PIL import Image, ImageOps, ImageDraw
import io

LANG = Path(__file__).resolve().parents[1]
BASE = LANG.parent/'downloads/mr-Deva-IN'
scratch = BASE/'source-image-qa'
scratch.mkdir(exist_ok=True)
tree = ET.parse(LANG/'provenance/selected-source-blocks.xml')
records = []
tiles = []
with zipfile.ZipFile(BASE/'releases/A20-canonical.zip') as archive:
    for selection in tree.getroot():
        english = next(e for e in selection if e.get('locale') == 'en')
        names = list(dict.fromkeys(e.get('src').rsplit('/',1)[-1] for e in english.iter() if e.tag.endswith('}image')))
        for name in names:
            found = [n for n in archive.namelist() if n.endswith('/media/'+name)]
            assert len(found) == 1,(name,found)
            raw = archive.read(found[0])
            image = Image.open(io.BytesIO(raw)).convert('RGB')
            # Inspection-scale conversion only; raw source bytes remain unchanged.
            image.thumbnail((900,180))
            tile = Image.new('RGB',(940,220),'white')
            draw = ImageDraw.Draw(tile)
            draw.text((12,7),f'{len(records)+1:02d} {name}',fill='black')
            tile.paste(image,(12,32))
            tiles.append(tile)
            records.append({'source':selection.get('locator'),'archive_member':found[0],'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'replacement':'Unicode equation/step text in selected adaptation; no binary in reader'})
for start in range(0,len(tiles),7):
    batch=tiles[start:start+7]
    sheet=Image.new('RGB',(940,len(batch)*220),(225,230,230))
    for i,tile in enumerate(batch):
        sheet.paste(tile,(0,i*220))
    sheet.save(scratch/f'sheet-{start//7+1:02d}.png')
(LANG/'provenance/selected-equation-images.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'source_equation_images':len(records),'contact_sheets':(len(tiles)+6)//7}))
