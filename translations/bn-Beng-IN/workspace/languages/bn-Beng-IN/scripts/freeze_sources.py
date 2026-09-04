"""Freeze source-text inventories and small exact witnesses from acquired inputs."""
from pathlib import Path

import os  # portable-export-transform-v1

def _portable_input_path(variable, default):
    """Resolve optional configured inputs without touching disk during import."""
    value = os.environ.get(variable)
    result = Path(value).expanduser() if value else default
    return result if result.is_absolute() else ROOT / result

def _require_portable_input(value, variable):
    if not value.exists():
        raise FileNotFoundError(
            f"Required pinned input is absent: {value}. Set {variable} to its "
            "existing location or restore the exact source-lock inputs under "
            "workspace downloads. This helper does not acquire sources."
        )
    return value

import hashlib
import json
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[3]
LANG = ROOT / 'languages/bn-Beng-IN'
PIN = '38cae454e644abf9f0a623e876994553881597c9'
A30PIN = '789b54099106b071d1d32bfcee454fed72eb4768'
REPOS = {'catalog': 'program-matematika-indonesia', 'A00': 'openstax-prealgebra-2e-id-ID',
         'A10': 'openstax-elementary-algebra-2e-id', 'A20': 'openstax-intermediate-algebra-2e-id',
         'A30': 'openstax-precalculus-2e-id', 'upstream-A00-A20': 'canonical-prealgebra',
         'upstream-A30': 'canonical-precalculus'}

def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def git(repo, *args):
    snapshot=ROOT/'downloads'/repo/'ACQUISITION.json'
    if snapshot.exists():
        rec=json.loads(snapshot.read_text())
        keys={('remote','get-url','origin'):'url',('rev-parse','HEAD'):'commit',('rev-parse','HEAD^{tree}'):'tree'}
        if args==('rev-parse','--is-shallow-repository'):
            return b'false'
        return rec[keys[args]].encode()
    return subprocess.check_output(['git', '-C', str(ROOT/'downloads'/repo), *args])

def copy(src, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)

def main():
    records=[]
    for key, repo in REPOS.items():
        folder=ROOT/'downloads'/repo
        rec={'id':key,'path':folder.relative_to(ROOT).as_posix(),
             'url':git(repo,'remote','get-url','origin').decode().strip(),
             'commit':git(repo,'rev-parse','HEAD').decode().strip(),
             'tree':git(repo,'rev-parse','HEAD^{tree}').decode().strip(),
             'shallow':git(repo,'rev-parse','--is-shallow-repository').decode().strip()=='true'}
        rec['notices']=[]
        if (folder/'ACQUISITION.json').exists():
            rec['shallow']=None
            rec['acquisition_method']='clean pinned working-tree snapshot copied from a parent-distributed local source; no history'
            rec['acquisition_inventory_sha256']=sha(folder/'ACQUISITION.json')
            acquisition=json.loads((folder/'ACQUISITION.json').read_text())
            rec['canonical_tracked_files']=acquisition['tracked_files']
            rec['snapshot_receipt_scope']='Original sparse snapshot receipt only; later bulk media staging was interrupted and is not certified by this receipt.'
            rec['sparse_receipt_unmaterialized_path_count']=len(acquisition['not_materialized_in_donor'])
            rec['full_sparse_receipt']=(folder/'ACQUISITION.json').relative_to(ROOT).as_posix()
            if key=='upstream-A30':
                rec['selected_media_receipt']='provenance/A30/selected-media.lock.json'
        for name in ['README.md','LICENSE','LICENSE.txt','SOURCE_AUTHORITY.md','MODEL_PROVENANCE.md','RELEASE_MANIFEST.json','PUBLICATION.json']:
            p=folder/name
            if p.is_file():
                dest=LANG/'provenance'/key/'repository'/name
                copy(p,dest)
                rec['notices'].append({'path':dest.relative_to(ROOT).as_posix(),'sha256':sha(dest)})
        records.append(rec)
    assert next(r['commit'] for r in records if r['id']=='upstream-A00-A20')==PIN
    assert next(r['commit'] for r in records if r['id']=='upstream-A30')==A30PIN
    collections=[]
    for course,book,repo,selected in [
        ('A00','prealgebra-2e','canonical-prealgebra',None),
        ('A10','elementary-algebra-2e','canonical-prealgebra',None),
        ('A20','intermediate-algebra-2e','canonical-prealgebra',None),
        ('A30','precalculus-2e','canonical-precalculus',['m49301','m49324'])]:
        base=ROOT/'downloads'/repo
        path=base/'collections'/f'{book}.collection.xml'
        tree=ET.parse(path)
        mids=[n.get('document') for n in tree.iter() if n.tag.endswith('}module')]
        inventory=[]
        for mid in (selected or mids):
            p=base/'modules'/mid/'index.cnxml'
            doc=ET.parse(p)
            inventory.append({'module':mid,'title':doc.find('{http://cnx.rice.edu/cnxml}title').text,
                              'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
        dest=LANG/'provenance'/course/f'{book}.collection.xml'
        copy(path,dest)
        collections.append({'course':course,'book':book,'collection_id':tree.find('{http://cnx.rice.edu/collxml}metadata/{http://cnx.rice.edu/mdml}uuid').text if tree.find('{http://cnx.rice.edu/collxml}metadata/{http://cnx.rice.edu/mdml}uuid') is not None else None,'collection_modules':len(mids),
                            'selected_modules':len(inventory),'collection_sha256':sha(path),'source_modules':inventory,
                            'media_scope':'Text verified against pinned Git objects. Media verified separately in qa/acquisition-check.json; original sparse snapshot counts do not certify the interrupted bulk copy.'})
    # Exact canonical files needed for replayable pilot, including attribution front matter.
    pilot=LANG/'provenance/pilot'
    base=ROOT/'downloads/canonical-prealgebra'
    for mid in ['m81241','m81285','m81289','m81320']:
        copy(base/'modules'/mid/'index.cnxml',pilot/f'{mid}.source.cnxml')
    section=ET.parse(pilot/'m81285.source.cnxml').find('.//*[@id="fs-id1726667"]')
    assets=[]
    for element in section.iter('{http://cnx.rice.edu/cnxml}image'):
        name=Path(element.get('src')).name
        dest=pilot/'media'/name
        dest.parent.mkdir(parents=True,exist_ok=True)
        src=base/'media'/name
        if not src.is_file():
            src=(_portable_input_path('BN_CANONICAL_ROOT', ROOT / 'downloads' / 'osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9') / 'media')/name
        copy(_require_portable_input(src, 'BN_CANONICAL_ROOT'),dest)
        assets.append({'name':name,'path':dest.relative_to(ROOT).as_posix(),'sha256':sha(dest),'bytes':dest.stat().st_size})
    catalog=ROOT/'downloads/program-matematika-indonesia'
    for name in ['curriculum_portfolios.jsonl','accessibility_derivatives.jsonl','portfolio_relations.jsonl']:
        copy(catalog/'backend/v2.1/planning/educational-access'/name,LANG/'provenance/AX-3'/name)
    copy(catalog/'docs/courses.js',LANG/'provenance/catalog/courses.js')
    archives=[]
    release_lock=json.loads((LANG/'provenance/releases.lock.json').read_text(encoding='utf-8'))
    expected={a['path']:a['expected_sha256'] for r in release_lock['releases'] for a in r['assets']}
    for p in sorted((ROOT/'downloads/releases').rglob('*.zip')):
        digest=sha(p)
        assert digest==expected[p.relative_to(ROOT).as_posix()],'Release SHA-256 mismatch'
        with zipfile.ZipFile(p) as z:
            assert z.testzip() is None
            # CRC validates the archive without materializing a redundant full copy.
            dest=ROOT/'downloads/extracted'/p.parent.name
            for info in z.infolist():
                target=(dest/info.filename).resolve()
                if not target.is_relative_to(dest.resolve()):
                    raise ValueError('Unsafe archive path')
                if (info.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError('Archive symlink rejected')
            archives.append({'path':p.relative_to(ROOT).as_posix(),'sha256':digest,'bytes':p.stat().st_size,
                             'entries':len(z.infolist()),'crc':'pass','extraction':'not required for pilot; skipped because disk space is critically low'})
    result={'schema':'bn-Beng-IN.translation-sources.v1','locale':'bn-Beng-IN','acquired_on':'2026-08-30',
            'purpose':'translation inputs only; no training/fine-tuning dataset',
            'repositories':records,'collections':collections,'pilot_assets':assets,'release_archives':archives,
            'release_lock':'provenance/releases.lock.json','pilot_scope':'A00 m81285/fs-id1726667; separate AX-3 U01 companion',
            'storage_recovery':'Source files retained; partial duplicate extraction is not an authority. No full extraction is performed by this script.',
            'A30_selection_reason':'Function notation and linear-function prerequisite bridges only; no calculus/trigonometry claim.'}
    (LANG/'sources.lock.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('FROZEN',[(c['course'],c['selected_modules']) for c in collections])

if __name__=='__main__':
    main()
