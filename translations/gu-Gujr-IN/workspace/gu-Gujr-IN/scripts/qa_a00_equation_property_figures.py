"""Bind all72 media to inspected originals and validate nine Gujarati diagrams."""
import hashlib,json,re
from html import escape
from pathlib import Path
from lxml import etree,html
from localized_a00_equation_properties import PREFIX,PROMPTS,LABELLED,SELF_SKILLS,RED,render_figure

ROOT=Path(__file__).resolve().parents[2]
LANG=ROOT/'gu-Gujr-IN'
SOURCE=ROOT/'downloads/gu-Gujr-IN/a00-id/provenance/logbook/authority/prealgebra2e/m81271.source.cnxml'
MEDIA=ROOT/'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'
OUT=ROOT/'build/gujarati-equation-property-figures'


def main():
    data=json.loads((LANG/'translations/a00-m81271-media-and-errata.gu.json').read_text(encoding='utf8'))
    translation=LANG/'translations/a00-m81271.gu.cnxml'
    source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    gu_hash=hashlib.sha256(translation.read_bytes()).hexdigest()
    assert source_hash==data['source_sha256']=='f74029642f7833d2a8596b2973d8789ae180d238052a0460c6eaa0a83277cde7'
    assert gu_hash==data['translation_sha256']=='c732a4354fbd034700765eb2901b21a8faeed9a3c9a77237caa2ccb84d0fa7e4'
    source=etree.parse(str(SOURCE));gu=etree.parse(str(translation))
    originals=source.xpath('//*[local-name()="media"]')
    alts={e.get('id'):e.get('alt') for e in gu.xpath('//*[local-name()="media"]')}
    assert len(originals)==len(data['media'])==72
    ids,refs,figures,redraws=[],[],[],[]
    for original,item in zip(originals,data['media']):
        filename=Path(original[0].get('src')).name;media_id=original.get('id')
        assert media_id==item['media_id'] and filename==item['source_file']
        sha=hashlib.sha256((MEDIA/filename).read_bytes()).hexdigest()
        assert sha==item['sha256'],filename
        alt=data['source_errata'].get(media_id,{}).get('corrected_alt_gu',alts[media_id])
        snippet=render_figure(filename,alt,media_id+'-redraw')
        if snippet:
            assert filename in LABELLED
            tree=html.fragment_fromstring(snippet)
            text=' '.join(tree.xpath('.//text()[not(ancestor::math)]'))
            assert not re.search(r'[A-Za-z]{2,}',text),(filename,text)
            ids+=tree.xpath('//@id');refs+=re.findall(r'url\(#([^\)]+)\)',snippet)
            redraws.append((filename,snippet))
        else: assert filename not in LABELLED
        figures.append({'media_id':media_id,'filename':filename,'sha256':sha,'mode':'localized' if snippet else 'visually verified original; no embedded English'})
    assert len(set(i['filename'] for i in figures))==71
    assert len(redraws)==9 and len(ids)==len(set(ids)) and all(ref in ids for ref in refs)
    trees={name:html.fragment_fromstring(snippet) for name,snippet in redraws}
    for index,(variable,value,checking) in PROMPTS.items():
        tree=trees[PREFIX+index+'_img-01.png']
        assert tree.xpath('.//mi/text()')==[variable]
        assert tree.xpath('.//mn/text()')==[str(value)]
        assert RED in tree.xpath('.//mn/@style')[0]
        assert tree.xpath('.//mo/text()')==(['='] if checking else [])
    for suffix,values in [('032-01.png',['6','9','15']),('028_img-01.png',['8','7','56'])]:
        tree=trees[PREFIX+suffix]
        assert tree.xpath('.//*[@data-equality-words]/text()')==['બરાબર છે']
        text=' '.join(tree.itertext())
        for n in values: assert len(re.findall(r'(?<!\d)'+n+r'(?!\d)',text))==2
        assert tree.xpath('.//mo/text()')==['=']
    twice=trees[PREFIX+'029_img-02.png']
    assert twice.xpath('.//*[@data-map-token]/@data-map-token')==['2','(x−3)','=','18']
    tokens=twice.xpath('.//*[@data-phrase-map]//math//text()')
    assert ''.join(tokens)=='2(x−3)=18'
    assert len(twice.xpath('.//*[@data-phrase-map]//*[local-name()="svg"]'))==3
    assert twice.xpath('.//*[@data-equality-words]/text()')==['મળે']
    selfcheck=trees['CNX_BMath_Figure_AppB_010.jpg']
    assert selfcheck.xpath('.//caption/text()')==list(SELF_SKILLS)==data['self_check']['rows']
    assert len(selfcheck.xpath('.//td[@aria-label="ખાલી"]'))==18
    checks={
        'x5 not a solution':6*5-17==13!=16,'y2 solution':6*2-4==5*2-2==8,
        'remove3':8-3==5,'remove4':5-4==1,'model1+envelope7':7-1==6,
        'model3+envelope4':4-3==1,'model2+envelope5':5-2==3,'model4+envelope7':7-4==3,
        'model3+envelope6':6-3==3,'model5+envelope9':9-5==4,
        'x+8=17':9+8==17,'100=y+74':26+74==100,'x-5=8':13-5==8,
        '27=a-16':43-16==27,'sum words':6+9==15,'product words':8*7==56,
        'twice whole difference':2*(12-3)==18 and 2*12-3!=18,
        'x+3=47':44+3==47,'y-14=18':32-14==18,
    }
    assert all(checks.values())
    OUT.mkdir(parents=True,exist_ok=True)
    style="""@font-face{font-family:Gujarati;src:url('../../gu-Gujr-IN/output/assets/NotoSansGujarati.ttf')}*{box-sizing:border-box}body{font-family:Gujarati,'Nirmala UI',sans-serif;margin:20px auto;padding:0 16px;max-width:1060px;line-height:1.6;color:#182c35}article{margin-bottom:24px;border-bottom:2px solid #08656b;padding-bottom:16px}h2{font-size:18px;overflow-wrap:anywhere}math{font-family:math}"""
    for page,selected in enumerate((redraws[:4],redraws[4:8],redraws[8:]),1):
        body=''.join(f'<article><h2>{escape(name)}</h2>{snippet}</article>' for name,snippet in selected)
        doc='<!doctype html><html lang="gu-Gujr-IN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>સમીકરણો ઉકેલવાં</title><style>'+style+'</style><body><h1>સમીકરણો ઉકેલવાં</h1>'+body+'</body></html>'
        (OUT/f'page-{page}.html').write_text(doc,encoding='utf8')
    receipt={'source_sha256':source_hash,'translation_sha256':gu_hash,
             'helper_sha256':hashlib.sha256(Path(__file__).with_name('localized_a00_equation_properties.py').read_bytes()).hexdigest(),
             'media':72,'unique_source_files':71,'redraws':9,'verified_unlabelled_occurrences':63,
             'unique_ids':len(ids),'resolved_references':len(refs),'selfcheck_blank_cells':18,'mathematical_checks':checks,'figures':figures}
    (LANG/'reviews/a00-m81271-figures-qa.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in receipt.items() if k!='figures'}))


if __name__=='__main__':main()
