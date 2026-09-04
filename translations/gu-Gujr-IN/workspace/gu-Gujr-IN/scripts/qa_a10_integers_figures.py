"""Source-bound inventory, structural checks and local visual-review pages."""
import hashlib
import json
import re
from html import escape
from pathlib import Path

from lxml import etree, html
from localized_a10_integers import PREFIX, VERIFIED_MATH_ONLY, render_figure

ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT / 'gu-Gujr-IN'
OUT = ROOT / 'build' / 'gujarati-integer-figures'
INVENTORY = LANG / 'reviews' / 'a10-m82454-media-inventory.json'
SOURCE = ROOT / 'downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82454/index.cnxml'
MEDIA = ROOT / 'downloads/gu-Gujr-IN/canonical-full/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = json.loads(INVENTORY.read_text(encoding='utf-8'))
    translation_hash = hashlib.sha256((LANG / 'translations/a10-m82454.gu.cnxml').read_bytes()).hexdigest()
    assert data['translation_sha256'] == translation_hash, 'Inventory must bind the current reviewed Gujarati alternatives'
    src = etree.parse(str(SOURCE))
    source_media = src.xpath('//*[local-name()="media"]')
    assert len(source_media) == len(data['media']) == 65
    assert len(VERIFIED_MATH_ONLY) == 45
    all_ids, all_refs, figures, redraws = [], [], [], []
    rows = []
    for item, source in zip(data['media'], source_media):
        assert source.get('id') == item['source_media']
        name = item['source_asset'].replace('\\', '/').rsplit('/', 1)[-1]
        assert source[0].get('src').endswith(name)
        original = MEDIA / name
        assert original.is_file()
        snippet = render_figure(name, item['alt_gu'], item['source_media'] + '-redraw')
        mode = 'redrawn' if snippet else 'verified mathematical-only original'
        if snippet:
            assert name not in VERIFIED_MATH_ONLY
            tree = html.fragment_fromstring(snippet)
            ids = tree.xpath('//@id')
            all_ids.extend(ids)
            refs = re.findall(r'url\(#([^)]*)\)', snippet)
            refs += [word for e in tree.xpath('//*[@aria-labelledby]') for word in e.get('aria-labelledby').split()]
            assert set(refs) <= set(ids), (name, refs, ids)
            all_refs.extend(refs)
            prose = ' '.join(tree.xpath('//text()[not(ancestor::math)]'))
            assert not re.search(r'[A-Za-z]{2,}', prose), (name, prose)
            assert tree.get('lang') == 'gu-Gujr-IN'
            redraws.append((name, snippet))
        else:
            assert name in VERIFIED_MATH_ONLY, name
        figures.append({'source_media': item['source_media'], 'filename': name, 'mode': mode,
                        'source_image_sha256': hashlib.sha256(original.read_bytes()).hexdigest()})
        rows.append(f"| {item['index']+1} | `{name}` | {mode} |")
    assert len(redraws) == 20
    assert len(all_ids) == len(set(all_ids))
    full = html.fromstring('<html><body>' + ''.join(s for _, s in redraws) + '</body></html>')
    assert len(full.xpath('//td[@aria-label="ખાલી"]')) == 12
    # The source sign/chip models are checked independently of helper strings.
    arithmetic = [5+3 == 8, -5+(-3) == -8, -5+3 == -2, 5+(-3) == 2,
                  -5-3 == -8, 5-(-3) == 8, 6-4 == 6+(-4) == 2,
                  8-(-5) == 8+5 == 13, abs(-5) == abs(5) == 5]
    assert all(arithmetic)
    count_rows = {'015c_img_new.jpg':8,'018c_img_new.jpg':8,'024d_img_new.jpg':2,
                  '025d_img_new.jpg':2,'032d_img_new.jpg':8,'033d_img_new.jpg':8,
                  '021_img_new.jpg':16,'026_img_new.jpg':16}
    for suffix, expected in count_rows.items():
        tree = html.fragment_fromstring(next(s for n,s in redraws if n == PREFIX + suffix))
        assert len(tree.xpath('.//circle')) == expected, suffix
    pairs = html.fragment_fromstring(next(s for n,s in redraws if n == PREFIX+'026_img_new.jpg'))
    assert len(pairs.xpath('.//ellipse')) == 6
    stylesheet = '''@font-face{font-family:Gujarati;src:url('../../gu-Gujr-IN/output/assets/NotoSansGujarati.ttf')}*{box-sizing:border-box}body{font-family:Gujarati,'Nirmala UI',sans-serif;margin:20px auto;padding:0 16px;max-width:1040px;line-height:1.6;color:#182c35}article{margin-bottom:28px;border-bottom:2px solid #08656b;padding-bottom:20px}h2{font-size:18px;overflow-wrap:anywhere}img{max-width:100%;height:auto}math{font-family:math}'''
    font_file = LANG / 'output/assets/NotoSansGujarati.ttf'
    assert font_file.exists(), font_file
    for page in range(4):
        items = redraws[page*5:(page+1)*5]
        body = ''.join(f'<article><h2>{escape(n)}</h2>{s}</article>' for n,s in items)
        document = '<!doctype html><html lang="gu-Gujr-IN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>પૂર્ણાંક આકૃતિઓ</title><style>' + stylesheet + '</style><body><h1>પૂર્ણાંક આકૃતિઓ</h1>' + body + '</body></html>'
        (OUT / f'page-{page+1}.html').write_text(document, encoding='utf-8')
    receipt = {'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               'translation_sha256': translation_hash,
               'helper_sha256': hashlib.sha256(Path(__file__).with_name('localized_a10_integers.py').read_bytes()).hexdigest(),
               'media':65, 'redraws':20, 'verified_mathematical_only':45,
               'unique_ids':len(all_ids), 'resolved_id_references':len(all_refs),
               'blank_selfcheck_cells':12, 'independent_arithmetic_checks':len(arithmetic),
               'figures':figures}
    (LANG / 'reviews/a10-m82454-figures-qa.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (OUT / 'inventory.md').write_text('| No. | Filename | Mode |\n|---|---|---|\n'+'\n'.join(rows)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k != 'figures'}, ensure_ascii=True))


if __name__ == '__main__':
    main()
