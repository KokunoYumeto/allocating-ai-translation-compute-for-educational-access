"""Read-only input verification; writes only a compact QA receipt, never copies corpora."""
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

import hashlib,json,subprocess,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[3]
LANG=ROOT/'languages/bn-Beng-IN'
PIN='38cae454e644abf9f0a623e876994553881597c9'
A30PIN='789b54099106b071d1d32bfcee454fed72eb4768'
SHARED=_portable_input_path('BN_CANONICAL_ROOT', ROOT / 'downloads' / 'osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9')

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def blob(raw):return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def tree(repo,pin):
    raw=subprocess.check_output(['git','-C',str(ROOT/'downloads'/repo),'ls-tree','-r','-z',pin])
    return {r.split(b'\t',1)[1].decode():r.split(b'\t',1)[0].split()[2].decode() for r in raw.split(b'\0') if r}

def main():
    lock=json.loads((LANG/'sources.lock.json').read_text(encoding='utf-8'))
    trees={'A00':tree('osbooks-prealgebra-bundle',PIN),'A30':tree('osbooks-college-algebra-bundle',A30PIN)}
    modules=0;assets={};normalized=0
    for c in lock['collections']:
        t=trees['A30' if c['course']=='A30' else 'A00']
        for m in c['source_modules']:
            p=ROOT/m['path'];raw=p.read_bytes()
            assert sha(p)==m['sha256']
            expected=t[f'modules/{m["module"]}/index.cnxml']
            if blob(raw)!=expected:
                assert blob(raw.replace(b'\r\n',b'\n'))==expected
                normalized+=1
            modules+=1
            for e in ET.fromstring(raw).iter():
                src=e.get('src','')
                if '/media/' not in src:continue
                name=Path(src).name
                base=(ROOT/'downloads/canonical-precalculus') if c['course']=='A30' else SHARED
                p=_require_portable_input(base/'media'/name, 'BN_CANONICAL_ROOT' if c['course']!='A30' else 'the source-lock A30 workspace path')
                assert p.is_file(),str(p)
                key=(str(base),name)
                if key not in assets:
                    raw=p.read_bytes();assert blob(raw)==t['media/'+name],name
                    assets[key]=len(raw)
    references=0
    for s in json.loads((LANG/'canon/references.lock.json').read_text(encoding='utf-8'))['sources']:
        assert sha(ROOT/s['path'])==s['sha256'];references+=1
        for page in s['read_pages']:
            for field in ['ocr','render']:
                r=page[field];assert sha(ROOT/r['path'])==r['sha256'];references+=1
    a30=json.loads((LANG/'provenance/A30/selected-media.lock.json').read_text(encoding='utf-8'))
    for a in a30['assets']:
        assert sha(ROOT/'downloads/canonical-precalculus/media'/a['name'])==a['sha256']
    result={'result':'pass','canonical_module_references':modules,'text_files_CRLF_normalized_for_git_blob_check':normalized,
            'unique_referenced_media_verified_against_pinned_git_blobs':len(assets),
            'referenced_media_bytes':sum(assets.values()),'A30_selected_media':len(a30['assets']),
            'reference_pdf_ocr_render_hashes_checked':references,
            'A00_A20_media_source':str(SHARED),'A00_A20_media_access':'read-only shared extraction; independent local full copy not claimed',
            'pins':[PIN,A30PIN],'large_copy_or_extraction_performed':False}
    (LANG/'qa/acquisition-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
