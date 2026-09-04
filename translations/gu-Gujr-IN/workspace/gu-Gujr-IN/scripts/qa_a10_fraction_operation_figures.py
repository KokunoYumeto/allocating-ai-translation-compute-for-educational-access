"""Validate all33 inspected source images,15 redraws and exact fraction arithmetic."""
import hashlib
import json
import math
import re
from fractions import Fraction as F
from html import escape
from pathlib import Path

from lxml import etree,html
from localized_a10_fraction_operations import PREFIX,VERIFIED_MATH_ONLY,LOCALIZED_SUFFIXES,render_figure,RED,CYAN,YELLOW_GREEN

ROOT=Path(__file__).resolve().parents[2]
LANG=ROOT/'gu-Gujr-IN'
MEDIA=ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'
SOURCE=ROOT/'downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82457/index.cnxml'
OUT=ROOT/'build/gujarati-fraction-operation-figures'


def main():
    pins=json.loads((LANG/'reviews/a10-m82457-figure-source-pins.json').read_text(encoding='utf8'))
    inventory=json.loads((LANG/'reviews/a10-m82457-media-inventory.json').read_text(encoding='utf8'))
    translation=LANG/'translations/a10-m82457.gu.cnxml'
    source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    gu_hash=hashlib.sha256(translation.read_bytes()).hexdigest()
    assert source_hash=='a8db22ca9c8c10c7f95fa3aa4dcb18596711741478515c220a75e291273983e9'
    assert gu_hash==inventory['translation_sha256']=='17c091fc838850c1c8d611b768cf727998b9afc34993098d959b2483fdcf8a58'
    original=etree.parse(str(SOURCE)); gu=etree.parse(str(translation))
    original_media=original.xpath('//*[local-name()="media"]')
    gu_alts={e.get('id'):e.get('alt') for e in gu.xpath('//*[local-name()="media"]')}
    assert len(original_media)==len(pins)==len(inventory['media'])==33
    assert len(VERIFIED_MATH_ONLY)==18
    ids,refs,redraws,figures=[],[],[],[]
    for media,pin,item in zip(original_media,pins,inventory['media']):
        media_id=media.get('id');filename=Path(media[0].get('src')).name
        assert media_id==pin['source_media']==item['source_media']
        assert filename==pin['filename']==Path(item['source_asset']).name
        sha=hashlib.sha256((MEDIA/filename).read_bytes()).hexdigest()
        assert sha==pin['sha256'],filename
        snippet=render_figure(filename,gu_alts[media_id],media_id+'-redraw')
        if snippet:
            assert filename not in VERIFIED_MATH_ONLY
            tree=html.fragment_fromstring(snippet)
            text=' '.join(tree.xpath('.//text()[not(ancestor::math)]'))
            assert not re.search(r'[A-Za-z]{2,}',text),(filename,text)
            ids+=tree.xpath('//@id')
            refs+=tree.xpath('//@aria-labelledby')
            refs+=re.findall(r'url\(#([^\)]+)\)',snippet)
            redraws.append((filename,snippet))
        else: assert filename in VERIFIED_MATH_ONLY
        figures.append({'source_media':media_id,'filename':filename,'sha256':sha,'mode':'localized' if snippet else 'verified mathematical-only original'})
    assert len(redraws)==len(LOCALIZED_SUFFIXES)==15
    assert len(ids)==len(set(ids)) and all(ref in ids for ref in refs)
    trees={name[len(PREFIX):]:html.fragment_fromstring(snippet) for name,snippet in redraws}
    assert trees['001c_new.jpg'].xpath('.//*[@data-step-column="3"]/@aria-label')==['ખાલી']
    assert '1 સિવાય' in ''.join(trees['001c_new.jpg'].itertext())
    assert trees['002_img_new.jpg'].xpath('.//*[@data-missing-target]/@data-missing-target')==['12-last','18-second']
    assert trees['002_img_new.jpg'].xpath('.//*[@data-lcd-factor]/@x')==['260','310','360','410']
    assert trees['002_img_new.jpg'].xpath('.//*[@data-lcd-factor]/text()')==['2','2','3','3']
    for name,lcd,blank_slots in [('001a_new.jpg','36',2),('003a_img_new.jpg','120',4),('004b_img_new.jpg','40',4)]:
        tree=trees[name]
        assert tree.xpath('.//table/@data-lcd')==[lcd]
        assert len(tree.xpath('.//mspace'))==blank_slots
    assert trees['001a_new.jpg'].xpath('.//mn[@style]/text()')==['3','3','2','2']
    complex_first=trees['010a_new.jpg']
    assert len(complex_first.xpath('.//mfrac[mrow/mfrac]'))==1
    assert len(complex_first.xpath('.//msup'))==4
    complex_last=trees['010c_new.jpg'].xpath('.//*[@data-step-column="2"]')[0]
    assert complex_last.xpath('.//mo/text()')==['÷','·'] # no invented equals signs between rows
    for name,variable,nums in [('005a_img_new.jpg','x',['1','3']),('006a_img_new.jpg','x',['3','4']),('007a_img_new.jpg','y',['2','3'])]:
        tree=trees[name]
        assert tree.xpath('.//mi/text()')==[variable]
        assert tree.xpath('.//mstyle[@mathcolor=$red]//mn/text()',red=RED)==nums
        assert tree.xpath('.//mstyle[@mathcolor=$red]/mo/text()',red=RED)==['−']
    assert trees['008a_img_new.jpg'].xpath('.//mstyle/@mathcolor')==[RED,CYAN]
    assert trees['009a_img_new.jpg'].xpath('.//mi/text()')==['p','q','r']
    assert trees['009a_img_new.jpg'].xpath('.//mn/text()')==['4','2','8']
    assert YELLOW_GREEN in trees['009a_img_new.jpg'].xpath('.//mn[text()="8"]/@style')[0]
    selfcheck=trees['201_img_new.jpg']
    assert len(selfcheck.xpath('.//caption'))==4
    assert len(selfcheck.xpath('.//td[@aria-label="ખાલી"]'))==12
    checks={
        'LCD12,18':math.lcm(12,18)==36,'LCD15,24':math.lcm(15,24)==120,'LCD5,8':math.lcm(5,8)==40,
        'prime31':all(31%i for i in range(2,6)),'common factor1':math.gcd(31,36)==1,
        '7/12+5/18':F(7,12)+F(5,18)==F(31,36),'7/15-19/24':F(7,15)-F(19,24)==F(-13,40),
        '3/5+x/8 constant':F(3,5)==F(24,40),'3/5+x/8 coefficient':F(1,8)==F(5,40),
        'complex fraction':(F(1,2)**2)/(4+3**2)==F(1,52),
        'substitute-1/3':F(-1,3)+F(1,3)==0,'substitute-3/4':F(-3,4)+F(1,3)==F(-5,12),
        'subtract negative':F(-5,6)-F(-2,3)==F(-1,6),'two variable substitution':2*F(1,4)**2*F(-2,3)==F(-1,12),
        'three variable substitution':F(-4-2,8)==F(-3,4),
    }
    assert all(checks.values())
    OUT.mkdir(parents=True,exist_ok=True)
    style="""@font-face{font-family:Gujarati;src:url('../../gu-Gujr-IN/output/assets/NotoSansGujarati.ttf')}*{box-sizing:border-box}body{font-family:Gujarati,'Nirmala UI',sans-serif;margin:20px auto;padding:0 16px;max-width:1100px;line-height:1.6;color:#182c35}article{margin-bottom:24px;border-bottom:2px solid #08656b;padding-bottom:16px}h2{font-size:18px;overflow-wrap:anywhere}math{font-family:math}"""
    groups=(redraws[:3],redraws[3:6],redraws[6:9],redraws[9:14],redraws[14:])
    for page,selected in enumerate(groups,1):
        body=''.join(f'<article><h2>{escape(name)}</h2>{snippet}</article>' for name,snippet in selected)
        doc='<!doctype html><html lang="gu-Gujr-IN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>અપૂર્ણાંકોનો સરવાળો અને બાદબાકી</title><style>'+style+'</style><body><h1>અપૂર્ણાંકોનો સરવાળો અને બાદબાકી</h1>'+body+'</body></html>'
        (OUT/f'page-{page}.html').write_text(doc,encoding='utf8')
    receipt={'source_sha256':source_hash,'translation_sha256':gu_hash,'helper_sha256':hashlib.sha256(Path(__file__).with_name('localized_a10_fraction_operations.py').read_bytes()).hexdigest(),
             'media':33,'redraws':15,'verified_math_only':18,'unique_ids':len(ids),'resolved_references':len(refs),'selfcheck_blank_cells':12,
             'mathematical_checks':checks,'figures':figures}
    (LANG/'reviews/a10-m82457-figures-qa.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in receipt.items() if k!='figures'}))


if __name__=='__main__': main()
