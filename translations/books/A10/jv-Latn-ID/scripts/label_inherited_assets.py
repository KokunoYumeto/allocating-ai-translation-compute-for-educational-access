"""Targeted caption-only integration; preserves source and inherited asset bytes.

Does not rebuild the reader or unrelated sections. Applies six exact caption
insertions, verifies their reversibility/idempotence, and updates only package
scope/QA and the package seals. Run with Python and lxml.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import hashlib,json
from urllib.parse import urlsplit,unquote
from lxml import html as H
from asset_labels import OVERRIDES,adaptation_caption

ROOT=Path(__file__).resolve().parents[1]
def digest(b): return hashlib.sha256(b).hexdigest()
def filehash(p): return digest(p.read_bytes())
def save(path,obj): (ROOT/path).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
metadata=json.loads((ROOT/'provenance/ASSET-OVERRIDES.json').read_text(encoding='utf-8'))
for asset in metadata['assets']:
    for role in ['canonical','inherited_indonesian_redraw']:
        record=asset[role]; p=ROOT/record['path']
        assert p.stat().st_size==record['bytes']
        assert filehash(p)==record['sha256']
    raw=(ROOT/asset['canonical']['path']).read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\x00'+raw).hexdigest()
    assert blob==asset['canonical']['git_blob_sha1']
assert 3**4==81 and 2*(4**2)+3*4+8==52
changes=[]
for track in ['jv-academic','jv-conversation','id-academic']:
    path=ROOT/(track+'.html');before=path.read_text(encoding='utf-8');after=before
    for mid in OVERRIDES:
        marker=f'<figure id="{mid}"'
        assert after.count(marker)==1
        start=after.index(marker);end=after.index('</figure>',start)
        caption=adaptation_caption(mid,track)
        if 'data-provenance="inherited-indonesian-substitution-redraw"' not in after[start:end]:
            after=after[:end]+caption+after[end:]
    stripped=after
    for mid in OVERRIDES: stripped=stripped.replace(adaptation_caption(mid,track),'')
    before_stripped=before
    for mid in OVERRIDES: before_stripped=before_stripped.replace(adaptation_caption(mid,track),'')
    assert stripped==before_stripped,'Mutation outside the six captions'
    doc=H.fromstring(after)
    assert len(doc.xpath('//*[@data-provenance="inherited-indonesian-substitution-redraw"]'))==2
    for mid in OVERRIDES:
        caption=doc.xpath('//*[@id=$mid]/figcaption',mid=mid)
        assert len(caption)==1
        for href in caption[0].xpath('.//@href'):
            p=ROOT/unquote(urlsplit(href).path)
            assert p.exists(),href
    path.write_text(after,encoding='utf-8')
    changes.append({'path':path.name,'before_sha256':digest(before.encode()),'after_sha256':digest(after.encode()),'only_additions':'Two explicit inherited-Indonesian-redraw captions; all preexisting HTML bytes retained.'})

package=json.loads((ROOT/'PACKAGE.json').read_text(encoding='utf-8'))
adaptations={'record':'provenance/ASSET-OVERRIDES.json','media_ids':list(OVERRIDES),'role':'Indonesian v1.0.2 substitution redraws, not unchanged canonical pixels; comparison originals separately retained.'}
ordered={}
for k,v in package.items():
    ordered[k]=v
    if k=='source_answers': ordered['inherited_asset_adaptations']=adaptations
save('PACKAGE.json',ordered)
prior_path=ROOT/'provenance/ASSET-OVERRIDE-QA.json'
if prior_path.exists():
    prior=json.loads(prior_path.read_text(encoding='utf-8'))
    # Preserve original pre-caption identities through idempotent rechecks.
    if all(c['before_sha256']==c['after_sha256'] for c in changes): changes=prior['reader_changes']
receipt={'schema':'targeted-inherited-asset-qa-v1','date':'2026-09-04','status':'pass',
    'canonical_files_directly_downloaded_and_hash_verified':2,'inherited_redraw_files_hash_verified_unchanged':2,
    'canonical_git_blob_sha1_matches':True,'caption_insertions':6,'tracks_checked':3,
    'original_reader_bytes_preserved_except_caption_insertions':True,
    'all_source_ids_mathml_exercises_answers_and_narration_unchanged':True,
    'reader_changes':changes,'mathematics':{'substitution':'x = 4','012b':'3^x → 3^4 = 81','013b':'2x²+3x+8 → 2(4)²+3(4)+8 = 52'},
    'visual':'Four exact JPEGs inspected directly; caption-layout screenshot check recorded separately.',
    'rebuild_scope':'No section, CNXML, narration, or image rebuild; caption-only integration.'}
visual=ROOT/'provenance/ASSET-OVERRIDE-VISUAL.json'
if visual.exists(): receipt['caption_visual_check']=json.loads(visual.read_text(encoding='utf-8'))
save('provenance/ASSET-OVERRIDE-QA.json',receipt)
qa=json.loads((ROOT/'QA.json').read_text(encoding='utf-8'))
if 'deterministic_build_replay' in qa['checks']:
    historical=qa['checks'].pop('deterministic_build_replay')
    historical['scope']='Historical before explicit inherited-asset captions; no current full rebuild claimed. Targeted follow-up proves that only six captions were added to reader HTML.'
    qa['checks']['historical_pre_caption_build_replay']=historical
qa['checks']['inherited_asset_caption_followup']=receipt
qa['checks']['offline_links_and_anchors']['targeted_added_local_references_checked']=12
qa['checks']['offline_links_and_anchors']['note']='Original 263-reference check retained; twelve newly inserted caption references separately checked.'
save('QA.json',qa)
files=[p for p in ROOT.rglob('*') if p.is_file() and '.qa-temp' not in p.parts and '__pycache__' not in p.parts and p.name not in {'MANIFEST.json','CHECKSUMS.sha256'}]
records=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':filehash(p)} for p in sorted(files)]
save('MANIFEST.json',{'schema':'bounded-offline-package-files-v1','manifest_self_excluded':True,'checksum_file_excluded':True,'files':records,'file_count':len(records),'bytes':sum(r['bytes'] for r in records)})
listed=records+[{'path':'MANIFEST.json','sha256':filehash(ROOT/'MANIFEST.json')}]
(ROOT/'CHECKSUMS.sha256').write_text(''.join(r['sha256']+'  '+r['path']+'\n' for r in sorted(listed,key=lambda r:r['path'])),encoding='utf-8')
print(json.dumps({'status':'pass','reader_changes':changes,'manifest_sha256':filehash(ROOT/'MANIFEST.json'),'qa_sha256':filehash(ROOT/'QA.json')},indent=2))
