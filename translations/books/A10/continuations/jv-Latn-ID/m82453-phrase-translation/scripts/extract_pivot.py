from pathlib import Path
from lxml import etree as E
import zipfile,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
archive=ROOT/'source/pivot-source.zip'
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='6f04e88387e8d4e6e710dddcebb8d41e952a315231d7e203d62170c6ad9f3456'
with zipfile.ZipFile(archive) as z:
 license_raw=z.read('LICENSE.txt')
 assert hashlib.sha256(license_raw).hexdigest()=='ab1a44bbba58252630134574d7b2534813339240eb645825ffcc2487dbe8114a'
 (ROOT/'LICENSE.txt').write_bytes(license_raw)
 raw=z.read('translated/modules/m82453/index.cnxml')
 assert hashlib.sha256(raw).hexdigest()=='2c0b688d569044b128d589579e9ba7d871a0fb9ac7a670ac6f22d0ef2b66e635'
 root=E.fromstring(raw);s=root.xpath('//*[@id="fs-id1170654942537"]')[0]
 (ROOT/'source/id-pivot.cnxml').write_bytes(E.tostring(s,encoding='utf-8',xml_declaration=True,with_tail=False))
 names=['CNX_ElemAlg_Figure_01_02_015_img_new.jpg','CNX_ElemAlg_Figure_01_02_016_img_new.jpg','CNX_ElemAlg_Figure_01_02_018_img_new.jpg']
 missing=[name for name in names if 'translated/media/'+name not in z.namelist()]
 assert len(missing)==3
 receipt={'source_zip_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'module_sha256':hashlib.sha256(raw).hexdigest(),'section_sha256':hashlib.sha256((ROOT/'source/id-pivot.cnxml').read_bytes()).hexdigest(),'source_release':'v1.0.2','member':'translated/modules/m82453/index.cnxml','license_member':'LICENSE.txt','license_sha256':hashlib.sha256(license_raw).hexdigest(),'media_overrides_absent':missing}
 (ROOT/'source/PIVOT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
 print(f"Verified pinned Indonesian module and extracted section {s.get('id')}, license, and receipt.")
