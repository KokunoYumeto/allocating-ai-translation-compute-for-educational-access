"""Bound all49 source media and inspect local Gujarati figure fixtures."""
import hashlib
import json
import re
from html import escape
from pathlib import Path

from lxml import etree, html
from localized_a00_expression_evaluation import PREFIX,PROMPTS,VERIFIED_MATH_ONLY,render_figure
from localized_place_value import RED,TEAL

ROOT=Path(__file__).resolve().parents[2]
LANG=ROOT/'gu-Gujr-IN'
OUT=ROOT/'build/gujarati-expression-evaluation-figures'
SOURCE=ROOT/'downloads/gu-Gujr-IN/a00-id/provenance/logbook/authority/prealgebra2e/m81270.source.cnxml'
MEDIA=ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'


def main():
    data=json.loads((LANG/'translations/a00-m81270-media-and-errata.gu.json').read_text(encoding='utf8'))
    source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    translation=LANG/'translations/a00-m81270.gu.cnxml'
    gu_hash=hashlib.sha256(translation.read_bytes()).hexdigest()
    assert source_hash==data['source_sha256']=='f48a03a92672e647cfcab21b800ca51d0626c92991a1fd7699fab6b8ab1c9661'
    assert gu_hash==data['translation_sha256']=='7b36c6ad0e135c9e1fed58155bc284e85f49f4938692c71ee37f4acaa2cae556'
    source=etree.parse(str(SOURCE));gu=etree.parse(str(translation))
    originals=source.xpath('//*[local-name()="media"]')
    gu_alts={e.get('id'):e.get('alt') for e in gu.xpath('//*[local-name()="media"]')}
    assert len(originals)==len(data['media'])==49
    assert len(VERIFIED_MATH_ONLY)==42
    redraws,figures,ids=[],[],[]
    for original,item in zip(originals,data['media']):
        filename,media_id=item['source_file'],item['media_id']
        assert original.get('id')==media_id and original[0].get('src').endswith(filename)
        sha=hashlib.sha256((MEDIA/filename).read_bytes()).hexdigest()
        assert sha==item['sha256'],filename
        snippet=render_figure(filename,gu_alts[media_id],media_id+'-redraw')
        if snippet:
            assert filename not in VERIFIED_MATH_ONLY
            tree=html.fragment_fromstring(snippet);ids+=tree.xpath('//@id')
            text=' '.join(tree.xpath('//text()[not(ancestor::math)]'))
            assert not re.search('[A-Za-z]{2,}',text),(filename,text)
            redraws.append((filename,snippet))
        else: assert filename in VERIFIED_MATH_ONLY
        figures.append({'source_media':media_id,'filename':filename,'source_image_sha256':sha,
                        'mode':'localized' if snippet else 'verified mathematical-only original'})
    assert len(redraws)==7 and len(ids)==len(set(ids))==7
    trees={name:html.fragment_fromstring(snippet) for name,snippet in redraws}
    for index,value in PROMPTS.items():
        tree=trees[PREFIX+f'{index:03}_img-01.png']
        assert tree.xpath('.//mi/text()')==(['x','y'] if index==20 else ['x'])
        assert tree.xpath('.//mn/text()')==([str(value),'2'] if index==20 else [str(value)])
        colors=tree.xpath('.//math[mn]/@style')
        assert RED in colors[0]
        if index==20: assert TEAL in colors[1]
        if index==21: assert 'દરેક' in ''.join(tree.itertext())
    selfcheck=trees['CNX_BMath_Figure_AppB_008.jpg']
    assert selfcheck.xpath('.//caption/text()')==data['self_check']['rows']
    assert len(selfcheck.xpath('.//td[@aria-label="ખાલી"]'))==12
    checks=[3+7==10,12+7==19,9*5-2==43,9*1-2==7,10**2==100,
            2**5==2*2*2*2*2==32,3*10+4*2-6==32,2*4**2+3*4+8==52,
            3+6==9,3-2==1,4+6==10,3+4==7,7+5==12,7-1==6,8-4==4]
    assert all(checks)
    OUT.mkdir(parents=True,exist_ok=True)
    style="""@font-face{font-family:Gujarati;src:url('../../gu-Gujr-IN/output/assets/NotoSansGujarati.ttf')}*{box-sizing:border-box}body{font-family:Gujarati,'Nirmala UI',sans-serif;margin:20px auto;padding:0 16px;max-width:1040px;line-height:1.6;color:#182c35}article{margin-bottom:24px;border-bottom:2px solid #08656b;padding-bottom:16px}h2{font-size:18px;overflow-wrap:anywhere}math{font-family:math}"""
    for page,selected in enumerate((redraws[:4],redraws[4:]),1):
        body=''.join(f'<article><h2>{escape(name)}</h2>{snippet}</article>' for name,snippet in selected)
        doc='<!doctype html><html lang="gu-Gujr-IN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>પદાવલીની કિંમત શોધવી</title><style>'+style+'</style><body><h1>પદાવલીની કિંમત શોધવી</h1>'+body+'</body></html>'
        (OUT/f'page-{page}.html').write_text(doc,encoding='utf8')
    receipt={'source_sha256':source_hash,'translation_sha256':gu_hash,
             'helper_sha256':hashlib.sha256(Path(__file__).with_name('localized_a00_expression_evaluation.py').read_bytes()).hexdigest(),
             'media':49,'redraws':7,'verified_mathematical_only':42,'unique_ids':7,
             'substitution_values':[5,1,10,5,10,4],'second_variable_substitution':{'y':2},
             'selfcheck_blank_cells':12,'independent_arithmetic_checks':len(checks),'figures':figures}
    (LANG/'reviews/a00-m81270-figures-qa.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in receipt.items() if k!='figures'}))


if __name__=='__main__': main()
