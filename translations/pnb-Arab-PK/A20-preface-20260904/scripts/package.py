"""Freeze a compact reader/source payload after completed QA; no publication."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(p,value):
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

def identity(p):
    return {'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}

def main():
    qa=json.loads((ROOT/'qa/verification.json').read_text(encoding='utf-8'))
    visual=json.loads((ROOT/'qa/visual.json').read_text(encoding='utf-8'))
    assert qa['status']==visual['status']=='pass'
    pdf=ROOT/'output/pdf/a20-preface-shahmukhi.pdf'
    assert sha(pdf)==qa['pdf_sha256']==visual['pdf_sha256']
    intake='https://github.com/KokunoYumeto/allocating-ai-translation-compute-for-educational-access/blob/ed6f2e2020118723c2a12fe3377d2273c3d8ec50/translations/pnb-Arab-PK/workspace/languages/pnb-Arab-PK/'
    mapping={
      'source/a20-preface.cnxml':'source-excerpts/a20-preface.cnxml',
      'source/recovered-manifest.json':'source-excerpts/manifest-a20-preface.json',
      'source/recovered-translation.json':'translations/a20-preface.json',
      'canon/examples.json':'canon/examples.json',
      'canon/terminology.tsv':'terminology.tsv',
      'styles/recovered-reader.css':'styles/reader.css',
    }
    for n in ('tryit.png','howtoicon.png','media.png','CNX_ElemAlg_Figure_05_01_015_img.jpg'):
        mapping['assets/a20/'+n]='assets/a20/'+n
    pins={
      'schema':'a20-recovered-preface-pins-v1',
      'book':'OpenStax Intermediate Algebra 2e', 'collection':'col31234','module':'m81357','locale':'pnb-Arab-PK',
      'upstream_commit':'38cae454e644abf9f0a623e876994553881597c9',
      'upstream_tree':'7907e4c81d43de1c3b6da173f0eb273c01dc5b55',
      'upstream_url':'https://github.com/openstax/osbooks-prealgebra-bundle/blob/38cae454e644abf9f0a623e876994553881597c9/modules/m81357/index.cnxml',
      'intake_commit':'ed6f2e2020118723c2a12fe3377d2273c3d8ec50',
      'intake_export_manifest_sha256':'772c054d8b6f9337f62a89df2fc2c726ed2d97c9077cb07f07dd0150e5ffe5a1',
      'unchanged_intake_files':[{**identity(ROOT/p),'public_intake_url':intake+src} for p,src in mapping.items()],
      'font_dependency':{
        'repository':'https://github.com/notofonts/noto-fonts','commit':'f3bdec9c1ef567dd6780fd5c20b154158d46f037',
        'files':[identity(ROOT/'assets/fonts'/n) for n in ('NotoNaskhArabic-Regular.ttf','NotoNaskhArabic-Bold.ttf','OFL.txt')],
        'font_paths':['hinted/ttf/NotoNaskhArabic/NotoNaskhArabic-Regular.ttf','hinted/ttf/NotoNaskhArabic/NotoNaskhArabic-Bold.ttf'],
        'license_path':'LICENSE','license':'SIL OFL 1.1',
        'selection':'Static font replaces a rejected variable-font PDF with missing/null extraction characters. No other source/style canon changed.'
      },
      'coverage':{'source_text_owners':89,'source_ids':66,'source_elements':194,'sections':26,'paragraphs':33,'list_items':25,'images':4,'source_mathml':0,'source_exercises':0,'source_solutions':0,'added_exercises':0,'added_solutions':0,'preface_complete':True,'book_complete':False,'next_module':'m81358'},
      'separation':'Faithful source translation, original bridge, recovery notes and font/style adaptations are separate. The historical recovered manifest preserves comparison/notice locators but is not this package dependency closure.',
      'model_provenance':'OpenAI Codex gpt-5.6-sol, Ultra',
    }
    save(ROOT/'source-pins.json',pins)
    excluded={'PACKAGE_MANIFEST.json','checksums.sha256'}
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.relative_to(ROOT).parts[0]!='tmp' and p.name not in excluded and p.suffix!='.zip')
    payload=[identity(p) for p in files]
    save(ROOT/'PACKAGE_MANIFEST.json',{'schema':'a20-pnb-preface-package-v1','date':'2026-09-04','status':'complete bounded preface; not complete book','primary_html':'index.html','primary_pdf':'output/pdf/a20-preface-shahmukhi.pdf','pdf_pages':qa['pdf_pages'],'files':payload,'payload_files_excluding_manifest_and_checksums':len(payload),'payload_bytes_excluding_manifest_and_checksums':sum(p['bytes'] for p in payload),'publication':'Canonical owner handles the existing GitHub lineage; this helper did not publish.'})
    files.append(ROOT/'PACKAGE_MANIFEST.json')
    files.sort()
    (ROOT/'checksums.sha256').write_text(''.join(sha(p)+'  '+p.relative_to(ROOT).as_posix()+'\n' for p in files),encoding='utf-8',newline='\n')
    files.append(ROOT/'checksums.sha256')
    out=ROOT/'a20-preface-shahmukhi-20260904.zip'
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(files):
            info=zipfile.ZipInfo(p.relative_to(ROOT).as_posix(),date_time=(2026,9,4,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16
            z.writestr(info,p.read_bytes())
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        assert len(z.infolist())==len(files)
        for p in files:
            assert hashlib.sha256(z.read(p.relative_to(ROOT).as_posix())).hexdigest()==sha(p)
    print(json.dumps({'zip':identity(out),'manifest':identity(ROOT/'PACKAGE_MANIFEST.json'),'files':len(files),'uncompressed_bytes':sum(p.stat().st_size for p in files),'pdf':identity(pdf)},indent=2))


if __name__=='__main__':
    main()
