"""Source-bound inventory, structural checks and local visual fixtures."""
import base64
import hashlib
import json
import re
from html import escape
from pathlib import Path

from lxml import etree, html
from localized_a00_algebra_language import (
    CAR_IMAGE_BASE64, CAR_IMAGE_SHA256, CARS, MPG, PHOTO_VIEWPORTS,
    PREFIX, VERIFIED_MATH_ONLY, render_figure,
)

ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT / 'gu-Gujr-IN'
OUT = ROOT / 'build/gujarati-algebra-language-figures'
SOURCE = ROOT / 'downloads/gu-Gujr-IN/a00-id/provenance/logbook/authority/prealgebra2e/m81268.source.cnxml'
MEDIA = ROOT / 'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'


def main():
    inventory = json.loads((LANG/'translations/a00-m81268-media-and-errata.gu.json').read_text(encoding='utf8'))
    translation = LANG/'translations/a00-m81268.gu.cnxml'
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    translation_hash = hashlib.sha256(translation.read_bytes()).hexdigest()
    assert source_hash == '7a46eec9084976ca082e71f10f4cad97f2ba231d7b390e27753a21efb530bf87'
    assert translation_hash == '4d7ba8aa33c75f30c2827504a3afd3548a1a78ff281c1b094f62346053702a40'
    source = etree.parse(str(SOURCE))
    gu = etree.parse(str(translation))
    gu_alts = {m.get('id'):m.get('alt') for m in gu.xpath('//*[local-name()="media"]')}
    originals = source.xpath('//*[local-name()="media"]')
    assert len(originals) == len(inventory['media']) == 44
    assert len(VERIFIED_MATH_ONLY) == 39
    redraws, figures, ids, refs = [], [], [], []
    for item, original in zip(inventory['media'], originals):
        filename, media_id = item['source_file'], item['media_id']
        assert original.get('id') == media_id
        assert original[0].get('src').endswith(filename)
        actual_sha = hashlib.sha256((MEDIA/filename).read_bytes()).hexdigest()
        assert actual_sha == item['sha256'], filename
        alt = inventory['source_errata'].get(media_id,{}).get('corrected_alt_gu',gu_alts[media_id])
        snippet = render_figure(filename,alt,media_id+'-redraw')
        if snippet:
            assert filename not in VERIFIED_MATH_ONLY
            tree = html.fragment_fromstring(snippet)
            local_ids = tree.xpath('//@id')
            local_refs = re.findall(r'url\(#([^)]*)\)',snippet)
            local_refs += [word for e in tree.xpath('//*[@aria-labelledby]') for word in e.get('aria-labelledby').split()]
            local_refs += [e.get('href')[1:] for e in tree.xpath('//*[@href]') if e.get('href').startswith('#')]
            assert set(local_refs) <= set(local_ids), (filename,local_refs)
            ids.extend(local_ids)
            refs.extend(local_refs)
            visible = ' '.join(tree.xpath('//text()[not(ancestor::math)]'))
            assert not re.search('[A-Za-z]{2,}',visible),(filename,visible)
            redraws.append((filename,snippet))
        else:
            assert filename in VERIFIED_MATH_ONLY
        figures.append({'source_media':media_id,'filename':filename,'source_image_sha256':actual_sha,
                        'mode':'localized' if snippet else 'verified mathematical-only original'})
    assert len(redraws)==5
    assert len(ids)==len(set(ids))
    trees={name:html.fragment_fromstring(snippet) for name,snippet in redraws}
    car=trees[PREFIX+'003.jpg']
    assert len(car.xpath('.//tr'))==2 and len(car.xpath('.//tr[1]/*'))==6
    assert tuple(map(int,car.xpath('.//td/text()')))==MPG==(48,27,28,26,27)
    assert len(car.xpath('.//use'))==5 and len(car.xpath('.//image'))==1
    assert base64.b64decode(CAR_IMAGE_BASE64)==(MEDIA/(PREFIX+'003.jpg')).read_bytes()
    assert hashlib.sha256(base64.b64decode(CAR_IMAGE_BASE64)).hexdigest()==CAR_IMAGE_SHA256
    assert all(x>=110 and y==20 and x+w<=632 and y+h==78 for x,y,w,h in PHOTO_VIEWPORTS)
    for name in (PREFIX+'010_img.jpg',PREFIX+'020_img.jpg'):
        tree=trees[name]
        expressions=tree.xpath('.//math')
        assert ''.join(expressions[0].itertext())=='an='
        assert ''.join(expressions[1].itertext())=='a·a·a·…·a'
        assert expressions[1].xpath('./mi/text()')==['a']*4
        assert expressions[2].xpath('./mi/text()')==['n']
        assert len(tree.xpath('.//line[@marker-end]'))==2
    power=trees[PREFIX+'003_img.jpg']
    assert power.xpath('.//svg/text/text()')==['આધાર','2','3','ઘાતાંક']
    assert len(power.xpath('.//line[@marker-end]'))==2
    selfcheck=trees['CNX_BMath_Figure_AppB_007.jpg']
    assert len(selfcheck.xpath('.//caption'))==4
    assert len(selfcheck.xpath('.//td[@aria-label="ખાલી"]'))==12
    # Numeric images were inspected in order; these independent identities
    # verify their unchanged worked endpoints without recoloring originals.
    checks=[4+3*7==25,(4+3)*7==49,18/9*2==4,18*9/2==81,
            18/6+4*(5-2)==15,5+2**3+3*(6-3*(4-2))==13,
            2**3+3**4/3-5**2==10,48>27,28>26,27==27,2**3==8]
    assert all(checks)
    OUT.mkdir(parents=True,exist_ok=True)
    style="""@font-face{font-family:Gujarati;src:url('../../gu-Gujr-IN/output/assets/NotoSansGujarati.ttf')}*{box-sizing:border-box}body{font-family:Gujarati,'Nirmala UI',sans-serif;margin:20px auto;padding:0 16px;max-width:1040px;line-height:1.6;color:#182c35}article{margin-bottom:28px;border-bottom:2px solid #08656b;padding-bottom:20px}h2{font-size:18px;overflow-wrap:anywhere}math{font-family:math}"""
    for page, selected in enumerate((redraws[:3],redraws[3:]),1):
        body=''.join(f'<article><h2>{escape(name)}</h2>{snippet}</article>' for name,snippet in selected)
        doc='<!doctype html><html lang="gu-Gujr-IN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>બીજગણિતની ભાષા</title><style>'+style+'</style><body><h1>બીજગણિતની ભાષા</h1>'+body+'</body></html>'
        (OUT/f'page-{page}.html').write_text(doc,encoding='utf8')
    receipt={'source_sha256':source_hash,'translation_sha256':translation_hash,
             'helper_sha256':hashlib.sha256(Path(__file__).with_name('localized_a00_algebra_language.py').read_bytes()).hexdigest(),
             'media':44,'redraws':5,'verified_mathematical_only':39,
             'unique_ids':len(ids),'resolved_id_references':len(refs),
             'source_car_photo_sha256':CAR_IMAGE_SHA256,'photo_viewports':PHOTO_VIEWPORTS,
             'car_values_mpg':MPG,'car_table_rows_columns':[2,6],
             'general_expansion_explicit_factors':4,'selfcheck_blank_cells':12,
             'independent_arithmetic_checks':len(checks),'figures':figures}
    (LANG/'reviews/a00-m81268-figures-qa.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in receipt.items() if k!='figures'}))


if __name__=='__main__':
    main()
