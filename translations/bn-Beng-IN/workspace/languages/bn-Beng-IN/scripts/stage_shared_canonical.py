"""Copy clean, parent-distributed canonical working files, never mutate the donor."""
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
import sys

ROOT=Path(__file__).resolve().parents[3]
if '--allow-bulk-staging' not in sys.argv:
    raise SystemExit('Bulk staging is paused. Reuse shared inputs read-only. Explicit --allow-bulk-staging is required after storage coordination.')
if shutil.disk_usage(ROOT).free < 3_000_000_000:
    raise SystemExit('Insufficient free space for bulk staging; no files copied.')
DONOR=_portable_input_path('BN_DONOR_DOWNLOADS', ROOT / 'downloads')
for source_name,dest_name,pin in [
    ('upstream-prealgebra','canonical-prealgebra','38cae454e644abf9f0a623e876994553881597c9'),
    ('upstream-precalculus','canonical-precalculus','789b54099106b071d1d32bfcee454fed72eb4768')]:
    source=_require_portable_input(DONOR/source_name, 'BN_DONOR_DOWNLOADS')
    dest=ROOT/'downloads'/dest_name
    def git(*args):
        return subprocess.check_output(['git','-C',str(source),*args])
    assert git('rev-parse','HEAD').decode().strip()==pin
    assert not git('status','--porcelain','--untracked-files=no').strip(), 'Donor tracked changes detected'
    names=git('ls-files','-z').decode().strip('\0').split('\0')
    files=[]
    omitted=[]
    fallback=_portable_input_path('BN_CANONICAL_ROOT', ROOT / 'downloads' / 'osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9') if source_name=='upstream-prealgebra' else None
    for name in names:
        original=source/name
        if not original.is_file() and fallback and (fallback/name).is_file():
            original=fallback/name
        if not original.is_file():
            omitted.append(name)
            continue
        target=dest/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(original,target)
        raw=target.read_bytes()
        files.append({'path':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    record={'method':'byte-copy of clean pinned tracked working files; no Git history needed',
            'donor':str(source),'commit':pin,'tree':git('rev-parse','HEAD^{tree}').decode().strip(),
            'url':git('remote','get-url','origin').decode().strip(),'files':files,'tracked_files':len(files),
            'not_materialized_in_donor':omitted,'fallback_materialization':str(fallback) if fallback else None}
    (dest/'ACQUISITION.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print(dest_name,len(files),sum(f['bytes'] for f in files),flush=True)
