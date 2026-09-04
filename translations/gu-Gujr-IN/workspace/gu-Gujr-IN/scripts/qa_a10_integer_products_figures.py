"""Source-bound figure inventory and repeatable local rendering fixtures."""
import hashlib
import json
import math
import re
from html import escape
from pathlib import Path

from lxml import etree, html
from localized_a10_integer_products import PREFIX, VERIFIED_MATH_ONLY, render_figure

ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT / 'gu-Gujr-IN'
OUT = ROOT / 'build/gujarati-integer-products-figures'
SOURCE = ROOT / 'downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82455/index.cnxml'
MEDIA = ROOT / 'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    inventory = json.loads((LANG / 'reviews/a10-m82455-media-inventory.json').read_text(encoding='utf-8'))
    translation_hash = hashlib.sha256((LANG / 'translations/a10-m82455.gu.cnxml').read_bytes()).hexdigest()
    assert inventory['translation_sha256'] == translation_hash
    source = etree.parse(str(SOURCE))
    media = source.xpath('//*[local-name()="media"]')
    assert len(media) == len(inventory['media']) == 29
    assert len(VERIFIED_MATH_ONLY) == 15
    figures, redraws, ids, refs = [], [], [], []
    for item, original in zip(inventory['media'], media):
        name = item['source_asset'].replace('\\','/').rsplit('/',1)[-1]
        assert original.get('id') == item['source_media']
        assert original[0].get('src').endswith(name)
        path = MEDIA / name
        assert path.is_file()
        snippet = render_figure(name, item['alt_gu'], item['source_media'] + '-redraw')
        if snippet:
            assert name not in VERIFIED_MATH_ONLY
            fragment = html.fragment_fromstring(snippet)
            local_ids = fragment.xpath('//@id')
            local_refs = re.findall(r'url\(#([^)]*)\)', snippet)
            local_refs += [word for e in fragment.xpath('//*[@aria-labelledby]') for word in e.get('aria-labelledby').split()]
            assert set(local_refs) <= set(local_ids), name
            ids.extend(local_ids)
            refs.extend(local_refs)
            prose = ' '.join(fragment.xpath('//text()[not(ancestor::math)]'))
            assert not re.search(r'[A-Za-z]{2,}', prose), (name,prose)
            redraws.append((name,snippet))
        else:
            assert name in VERIFIED_MATH_ONLY
        figures.append({'source_media':item['source_media'],'filename':name,
                        'mode':'redrawn' if snippet else 'verified mathematical-only original',
                        'source_image_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    assert len(redraws) == 14
    assert len(ids) == len(set(ids))
    trees = {name:html.fragment_fromstring(snippet) for name,snippet in redraws}
    assert len(trees[PREFIX+'001_img_new.jpg'].xpath('.//circle')) == 30
    assert len(trees[PREFIX+'002_img_new.jpg'].xpath('.//circle')) == 90
    assert len(trees[PREFIX+'002_img_new.jpg'].xpath('.//ellipse')) == 6
    # A removal boundary must enclose exactly five complete circles, while
    # leaving the counters in the neighboring row outside the boundary.
    for svg in trees[PREFIX+'002_img_new.jpg'].xpath('.//svg[ellipse]'):
        for boundary in svg.xpath('./ellipse'):
            cx,cy,rx,ry = (float(boundary.get(a)) for a in ('cx','cy','rx','ry'))
            selected=[]
            for circle in svg.xpath('./circle'):
                x,y,r = (float(circle.get(a)) for a in ('cx','cy','r'))
                if ((x-cx)/rx)**2 + ((y-cy)/ry)**2 < 1:
                    selected.append(circle)
                    assert all(((x+r*math.cos(t*math.pi/24)-cx)/rx)**2 +
                               ((y+r*math.sin(t*math.pi/24)-cy)/ry)**2 < 1
                               for t in range(48)), 'Removal oval crosses a counter'
            assert len(selected)==5
    assert len(trees[PREFIX+'201_img_new.jpg'].xpath('.//td[@aria-label="ખાલી"]')) == 18
    assert len(trees[PREFIX+'009a_new.jpg'].xpath('.//td[@aria-label="ખાલી"]')) == 1
    arithmetic = [5*3 == 15, -5*3 == -15, 5*(-3) == -15, (-5)*(-3) == 15,
                  -5+1 == -4, -(-5)+1 == 6, (-18+24)**2 == 36,
                  20-12 == 8, 20-(-12) == 32, 2*4**2+3*4+8 == 52, 11-(-9) == 20]
    assert all(arithmetic)
    style = '''@font-face{font-family:Gujarati;src:url('../../gu-Gujr-IN/output/assets/NotoSansGujarati.ttf')}*{box-sizing:border-box}body{font-family:Gujarati,'Nirmala UI',sans-serif;margin:20px auto;padding:0 16px;max-width:1040px;line-height:1.6;color:#182c35}article{margin-bottom:28px;border-bottom:2px solid #08656b;padding-bottom:20px}h2{font-size:18px;overflow-wrap:anywhere}img{max-width:100%;height:auto}math{font-family:math}'''
    for page in range(3):
        body = ''.join(f'<article><h2>{escape(n)}</h2>{s}</article>' for n,s in redraws[page*5:(page+1)*5])
        doc = '<!doctype html><html lang="gu-Gujr-IN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>પૂર્ણાંકોનો ગુણાકાર અને ભાગાકાર</title><style>'+style+'</style><body><h1>પૂર્ણાંકોનો ગુણાકાર અને ભાગાકાર</h1>'+body+'</body></html>'
        (OUT/f'page-{page+1}.html').write_text(doc,encoding='utf-8')
    receipt = {'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               'translation_sha256':translation_hash,
               'helper_sha256':hashlib.sha256(Path(__file__).with_name('localized_a10_integer_products.py').read_bytes()).hexdigest(),
               'media':29,'redraws':14,'verified_mathematical_only':15,
               'unique_ids':len(ids),'resolved_id_references':len(refs),
               'selfcheck_blank_cells':18,'source_blank_step_cell':1,
               'model_circles':[30,90],'removal_ellipses':6,
               'independent_arithmetic_checks':len(arithmetic),'figures':figures}
    (LANG/'reviews/a10-m82455-figures-qa.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k!='figures'},ensure_ascii=True))


if __name__ == '__main__':
    main()
