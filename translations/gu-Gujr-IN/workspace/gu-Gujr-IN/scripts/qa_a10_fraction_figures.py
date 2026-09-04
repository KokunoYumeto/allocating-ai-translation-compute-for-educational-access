"""Source-bound checks and local visual fixtures for all19 fraction images."""
import base64
import hashlib
import json
import re
from fractions import Fraction
from html import escape
from pathlib import Path

from lxml import etree, html
from localized_a10_fractions import (
    PREFIX, PIZZA_SOURCE_BASE64, PIZZA_SOURCE_SHA256, VERIFIED_MATH_ONLY, render_figure,
)

ROOT=Path(__file__).resolve().parents[2]
LANG=ROOT/'gu-Gujr-IN'
OUT=ROOT/'build/gujarati-fraction-figures'
SOURCE=ROOT/'downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82456/index.cnxml'
MEDIA=ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'


VERIFIED_IMAGE_SHA256 = {'CNX_ElemAlg_Figure_01_05_001_img_new.jpg': '062cce04fcde5dfaf7ef5ac1d4f7c8b40bb479eedc36d2949037d3b9583a604a', 'CNX_ElemAlg_Figure_01_05_002_new.jpg': '705dad7d99f2f1a8a94000c35b21b3b2e3b0f030926951d3809400382ce5d6ed', 'CNX_ElemAlg_Figure_01_05_003_img_new.jpg': '7973fa10df25af92152a69735ef54cb2a9fe21b55b33437b20dd2e2d83020b8b', 'CNX_ElemAlg_Figure_01_05_004_new.jpg': '04105c8c8421d01623427071b22a71e918e7c682dd370dad5d272625213e3e02', 'CNX_ElemAlg_Figure_01_05_005_img_new.jpg': '86426c9f60253249e81c6f99a08357f65c20e5973deadfb5bd4f589eb6654627', 'CNX_ElemAlg_Figure_01_05_006_img_new.jpg': '6fcdd2441cfc11ea3c761a55e4b921859d9cd1cb97e1097b282fb79a4a14e443', 'CNX_ElemAlg_Figure_01_05_007_img_new.jpg': '0924adbb93c4a7504256cef428ae6b844e5ad627b99f3146ca57cac0d2f3f041', 'CNX_ElemAlg_Figure_01_05_008a_new.jpg': 'a6fb3a62ad4d88b3ae6b81fbe1f52e7a3c2f9d186c5519af70ba024a96216c2c', 'CNX_ElemAlg_Figure_01_05_008b_new.jpg': '640ac3822736e7f9a64e1577558ddc0195d962bae7420242c12e0cfaf63cb961', 'CNX_ElemAlg_Figure_01_05_008c_new.jpg': '96cea8d47e8ef12be0b9c78a04e99bbc849a468caf7d07c9ea470e78dd28790d', 'CNX_ElemAlg_Figure_01_05_009_img_new.jpg': '7009d04718b8392753f42b87d5bf1f262d7f8903cbe5aafe3a3f41ad60ead43e', 'CNX_ElemAlg_Figure_01_05_010_img_new.jpg': '012c28d720042e10fcc13d6263b692c0fd1894578f6498b10255a6b2c562609e', 'CNX_ElemAlg_Figure_01_05_011_img_new.jpg': 'f5aced039c6722e8babea53edce91e8c6cd2e2f167553df0c77f28838bdc5494', 'CNX_ElemAlg_Figure_01_05_012_img_new.jpg': '2b0545e32b95073d26d1f68d32d6a2334039498646ab8561bdfc2bf759f23e47', 'CNX_ElemAlg_Figure_01_05_013_img_new.jpg': 'caa39bf84d7ee3ddffc69513985775803ea0c2726c2fb3fc3cce8fa74df6dfc3', 'CNX_ElemAlg_Figure_01_05_016_img_new.jpg': '289d8bcef983dc36af72c81d2dba6437da8c642512a777e659e8f6e126322476', 'CNX_ElemAlg_Figure_01_05_014_img_new.jpg': 'd955ecbb61c373dbb8b7d4b8d51256dc7cf6fbd29ac18e518cb89a883154222f', 'CNX_ElemAlg_Figure_01_05_015_img_new.jpg': 'f08e748f38bd3c316472ecd00a17a2b60bc0b7c8e78d8ff1b1667d85053cd25d', 'CNX_ElemAlg_Figure_01_05_201_img_new.jpg': 'f314ef88d89bd9ef6b34b8c3391009a1ef96bc8f20a1e950907b4c8de1e0cb5c'}

def main():
    inventory=json.loads((LANG/'reviews/a10-m82456-media-inventory.json').read_text(encoding='utf8'))
    translation=LANG/'translations/a10-m82456.gu.cnxml'
    source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    translation_hash=hashlib.sha256(translation.read_bytes()).hexdigest()
    assert source_hash=='1d3b69d74603175eb3c8aae95319b14bee988a56345c67384c0090b29995ab33'
    assert translation_hash=='f9216e5286eb2551550e6943c3f678889571c55fadba633515c4ab5923a12b4c'
    assert inventory['translation_sha256']==translation_hash
    source=etree.parse(str(SOURCE))
    originals=source.xpath('//*[local-name()="media"]')
    assert len(originals)==len(inventory['media'])==19
    assert len(VERIFIED_MATH_ONLY)==12
    redraws,figures,ids,refs=[],[],[],[]
    for item,original in zip(inventory['media'],originals):
        filename=item['source_asset'].rsplit('/',1)[-1]
        media_id=item['source_media']
        assert original.get('id')==media_id
        assert original.get('alt')==item['source_alt']
        assert original[0].get('src').endswith(filename)
        actual_sha=hashlib.sha256((MEDIA/filename).read_bytes()).hexdigest()
        assert actual_sha==VERIFIED_IMAGE_SHA256[filename],filename
        snippet=render_figure(filename,item['alt_gu'],media_id+'-redraw')
        if snippet:
            assert filename not in VERIFIED_MATH_ONLY
            tree=html.fragment_fromstring(snippet)
            local_ids=tree.xpath('//@id')
            local_refs=re.findall(r'url\(#([^)]*)\)',snippet)
            local_refs+=[word for e in tree.xpath('//*[@aria-labelledby]') for word in e.get('aria-labelledby').split()]
            assert set(local_refs)<=set(local_ids),filename
            ids+=local_ids
            refs+=local_refs
            prose=' '.join(tree.xpath('//text()[not(ancestor::math)]'))
            assert not re.search('[A-Za-z]{2,}',prose),(filename,prose)
            redraws.append((filename,snippet))
        else:
            assert filename in VERIFIED_MATH_ONLY
        figures.append({'source_media':media_id,'filename':filename,'source_image_sha256':actual_sha,
                        'mode':'localized' if snippet else 'verified mathematical-only original'})
    assert len(redraws)==7
    assert len(ids)==len(set(ids))
    trees={name:html.fragment_fromstring(snippet) for name,snippet in redraws}
    first=trees[PREFIX+'005_img_new.jpg']
    assert len(first.xpath('.//mn[@style]'))==6
    assert first.xpath('.//mn[@style]/text()')==['2','2','3','3','10','10']
    assert len(first.xpath('.//mo[text()="·"]'))==6
    step1=trees[PREFIX+'008a_new.jpg']
    step2=trees[PREFIX+'008b_new.jpg']
    assert step1.xpath('.//svg/text/text()')==['−','2','·','3','·','5','·','7','5','·','7','·','11']
    assert step2.xpath('.//svg/text/text()')==step1.xpath('.//svg/text/text()')
    assert step2.xpath('.//line[@data-cancel-factor]/@data-cancel-factor')==['5','7','5','7']
    assert len(step2.xpath('.//math//mfrac'))==1
    assert len(trees[PREFIX+'008c_new.jpg'].xpath('.//*[@aria-label="ખાલી"]'))==1
    cancel=trees[PREFIX+'009_img_new.jpg']
    assert cancel.xpath('.//line[@data-cancel-factor]/@data-cancel-factor')==['5','5']
    assert len(cancel.xpath('.//td[@aria-label="ખાલી"]'))==1
    models=trees[PREFIX+'016_img_new.jpg']
    assert len(models.xpath('.//circle[@data-quarter="1/4"]'))==8
    assert sorted(set(models.xpath('.//circle[@data-quarter]/@cy')))==['132','44']
    assert len(models.xpath('.//math'))==8
    assert len(models.xpath('.//mo[text()="÷"]'))==2
    assert len(models.xpath('.//mo[text()="·"]'))==3
    assert models.xpath('.//image/@width')==['669']
    assert models.xpath('.//image/@height')==['408']
    assert models.xpath('.//svg[image]/@viewbox')==['0 42 312 150']
    original=(MEDIA/(PREFIX+'016_img_new.jpg')).read_bytes()
    assert base64.b64decode(PIZZA_SOURCE_BASE64)==original
    assert hashlib.sha256(original).hexdigest()==PIZZA_SOURCE_SHA256
    assert '$2.00' in ''.join(models.itertext())
    selfcheck=trees[PREFIX+'201_img_new.jpg']
    assert len(selfcheck.xpath('.//caption'))==6
    assert len(selfcheck.xpath('.//td[@aria-label="ખાલી"]'))==18
    checks=[Fraction(1,2)==Fraction(2,4)==Fraction(3,6)==Fraction(10,20),
            2*3*5*7==210,5*7*11==385,Fraction(-210,385)==Fraction(-6,11),
            Fraction(-32,56)==Fraction(-4,7),Fraction(2,5)==Fraction(4,10)==Fraction(6,15)==Fraction(10,25),
            Fraction(1,2)*Fraction(3,4)==Fraction(3,8),Fraction(-12,5)*(-20)==48,
            Fraction(-7,18)/Fraction(-14,27)==Fraction(3,4),Fraction(3,4)/Fraction(5,8)==Fraction(6,5),
            2*Fraction(1,4)==Fraction(1,2),Fraction(2)/Fraction(1,4)==8,
            8*Fraction(1,4)==2]
    assert all(checks)
    OUT.mkdir(parents=True,exist_ok=True)
    style="""@font-face{font-family:Gujarati;src:url('../../gu-Gujr-IN/output/assets/NotoSansGujarati.ttf')}*{box-sizing:border-box}body{font-family:Gujarati,'Nirmala UI',sans-serif;margin:20px auto;padding:0 16px;max-width:1040px;line-height:1.6;color:#182c35}article{margin-bottom:28px;border-bottom:2px solid #08656b;padding-bottom:20px}h2{font-size:18px;overflow-wrap:anywhere}math{font-family:math}"""
    for page,selected in enumerate((redraws[:4],redraws[4:]),1):
        body=''.join(f'<article><h2>{escape(name)}</h2>{snippet}</article>' for name,snippet in selected)
        doc='<!doctype html><html lang="gu-Gujr-IN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>અપૂર્ણાંકોને આકૃતિથી સમજીએ</title><style>'+style+'</style><body><h1>અપૂર્ણાંકોને આકૃતિથી સમજીએ</h1>'+body+'</body></html>'
        (OUT/f'page-{page}.html').write_text(doc,encoding='utf8')
    receipt={'source_sha256':source_hash,'translation_sha256':translation_hash,
             'helper_sha256':hashlib.sha256(Path(__file__).with_name('localized_a10_fractions.py').read_bytes()).hexdigest(),
             'media':19,'redraws':7,'verified_mathematical_only':12,
             'unique_ids':len(ids),'resolved_id_references':len(refs),
             'common_factor_cancellation_marks':6,'source_blank_instruction_cells':2,
             'quarter_models':8,'quarter_rows':2,'quarter_columns':4,
             'source_pizza_image_sha256':PIZZA_SOURCE_SHA256,'source_pizza_viewport':[0,42,312,150],
             'selfcheck_blank_cells':18,'independent_arithmetic_checks':len(checks),'figures':figures}
    (LANG/'reviews/a10-m82456-figures-qa.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in receipt.items() if k!='figures'}))


if __name__=='__main__':
    main()
