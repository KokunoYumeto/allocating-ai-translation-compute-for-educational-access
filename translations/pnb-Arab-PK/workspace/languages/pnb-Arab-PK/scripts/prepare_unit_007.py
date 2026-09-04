"""Materialize only PNB-007's pinned images and exact existing rights rows."""
from pathlib import Path
import csv
import hashlib
import json
from qa_menu import jpeg_dimensions

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
MANIFEST = BASE / 'source-excerpts/manifest-007.json'
RIGHTS = ROOT / 'downloads/extracted/A30/00_control/COMPONENT_RIGHTS.csv'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def prepare():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    assert manifest['unit'] == 'PNB-007'
    assert manifest['commit'] == '789b54099106b071d1d32bfcee454fed72eb4768'
    assert len(manifest['images']) == 3
    excerpt = BASE / 'source-excerpts' / manifest['source_excerpt']
    assert digest(excerpt.read_bytes().replace(b'\r\n', b'\n')) == manifest['excerpt_sha256']
    with RIGHTS.open(encoding='utf-8-sig', newline='') as stream:
        rights = list(csv.DictReader(stream))
    prepared = []
    fields = ['rights_component_id', 'asset_path', 'bytes', 'sha256', 'source_modules',
              'classification', 'admission', 'license_id', 'attribution', 'required_action']
    for spec in manifest['images']:
        source_root = (ROOT / 'downloads/complete-upstream/osbooks-college-algebra-bundle').resolve()
        source = (source_root / spec['source_path']).resolve()
        target = (BASE / spec['path']).resolve()
        assert source.is_relative_to(source_root) and target.is_relative_to((BASE / 'assets').resolve())
        data = source.read_bytes()
        assert digest(data) == spec['sha256']
        assert jpeg_dimensions(data) == (spec['width'], spec['height'])
        matches = [row for row in rights if row['asset_path'] == spec['source_path']]
        assert len(matches) == 1
        row = matches[0]
        assert row['sha256'] == spec['sha256'] and int(row['bytes']) == len(data)
        assert row['admission'] == 'admitted' and row['source_modules'] == 'm49301'
        assert not target.exists() or digest(target.read_bytes()) == spec['sha256'], 'Different existing asset; refusing overwrite'
        prepared.append((target, data, {key: row[key] for key in fields}))
    # No image writes until every source, notice and existing destination passes.
    for target, data, row in prepared:
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_bytes(data)
        assert digest(target.read_bytes()) == row['sha256']
    notice = BASE / 'provenance/unit-007-component-notices.json'
    notice.write_text(json.dumps([row for _, _, row in prepared], ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('Prepared PNB-007: 3 unchanged source images and exact retained rights rows; no new audit.')


if __name__ == '__main__':
    prepare()
