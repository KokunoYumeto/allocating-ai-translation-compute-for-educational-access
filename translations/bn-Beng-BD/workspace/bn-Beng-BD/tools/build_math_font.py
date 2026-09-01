"""Build a separate OFL Noto math-capable Bengali font; never modify U01 font."""
from pathlib import Path
import hashlib,json,urllib.request
from fontTools.ttLib import TTFont
from fontTools.merge import Merger
L=Path(__file__).resolve().parents[1]
COMMIT='ffebf8c1ee449e544955a7e813c54f9b73848eac'
URL=f'https://raw.githubusercontent.com/notofonts/noto-fonts/{COMMIT}/hinted/ttf/NotoSansMath/NotoSansMath-Regular.ttf'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    math=L/'assets/NotoSansMath-Regular.ttf';receipt_path=L/'assets/math-font-receipt.json'
    if not math.exists():
        raw=urllib.request.urlopen(URL,timeout=45).read()
        assert len(raw)>10000 and raw[:4]==b'\0\1\0\0','Not a TrueType font'
        math.write_bytes(raw)
    if receipt_path.exists():
        old=json.loads(receipt_path.read_text(encoding='utf-8'))
        for item in old['inputs']:assert item['sha256']==sha(L/item['path']),'Locked font changed: '+item['path']
    font=TTFont(math);cmap=font.getBestCmap();assert 8776 in cmap
    symbols=L/'assets/NotoSansSymbols2-Regular.ttf'
    symbols_url=f'https://raw.githubusercontent.com/notofonts/noto-fonts/{COMMIT}/hinted/ttf/NotoSansSymbols2/NotoSansSymbols2-Regular.ttf'
    if not symbols.exists():
        raw=urllib.request.urlopen(symbols_url,timeout=45).read()
        assert len(raw)>10000 and raw[:4]==b'\0\1\0\0'
        symbols.write_bytes(raw)
    assert 9633 in TTFont(symbols).getBestCmap()
    paths=[L/'assets/NotoSans-Regular.ttf',L/'assets/NotoSansBengali-Regular.ttf',math,symbols]
    merged=Merger().merge([str(p) for p in paths])
    for record in merged['name'].names:
        if record.nameID in (1,4,6):
            name='NumeracyBanglaMath' if record.nameID==6 else 'Numeracy Bangla Math'
            record.string=name.encode(record.getEncoding())
    merged['head'].created=3406620153;merged['head'].modified=3406620153;merged.recalcTimestamp=False
    output=L/'assets/NumeracyBanglaMath.ttf';merged.save(output)
    result={'font':'Numeracy Bangla Math','upstream_commit':COMMIT,'new_source_urls':[URL,symbols_url],'license':'SIL Open Font License 1.1; existing Noto-LICENSE.txt applies','modification':'Merged Noto Sans, Noto Sans Bengali, Noto Sans Math and Noto Sans Symbols 2; renamed family. U01 font unchanged.','inputs':[{'path':p.relative_to(L).as_posix(),'sha256':sha(p)} for p in paths],'output_sha256':sha(output),'required_glyphs':['U+2248 almost equal to','U+25A1 white square']}
    receipt_path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
