"""Merge OFL Noto Bengali + Latin into one shaping font to avoid mixed-fragment errors."""
from pathlib import Path
import hashlib,json
from fontTools.merge import Merger
L=Path(__file__).resolve().parents[1]
def main():
    paths=[L/'assets/NotoSans-Regular.ttf',L/'assets/NotoSansBengali-Regular.ttf']
    merged=Merger().merge([str(p) for p in paths])
    for record in merged['name'].names:
        if record.nameID in (1,4,6):
            name='NumeracyBangla' if record.nameID==6 else 'Numeracy Bangla'
            record.string=name.encode(record.getEncoding())
    merged['head'].created=3406620153;merged['head'].modified=3406620153
    merged.recalcTimestamp=False
    out=L/'assets/NumeracyBangla.ttf';merged.save(out)
    receipt={'font':'Numeracy Bangla','modification':'Merged Noto Sans and Noto Sans Bengali, renamed family; original glyphs retained.','upstream_commit':'ffebf8c1ee449e544955a7e813c54f9b73848eac','upstream':'https://github.com/notofonts/noto-fonts','license':'SIL Open Font License 1.1; see Noto-LICENSE.txt','inputs':[{'path':str(p.relative_to(L)).replace('\\','/'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
    (L/'assets/font-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
