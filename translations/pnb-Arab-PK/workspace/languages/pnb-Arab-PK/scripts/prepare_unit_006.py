"""Copy PNB-006's declared original asset and preserve its audited rights row."""
from pathlib import Path
import csv
import hashlib
import json
import shutil

BASE = Path(__file__).resolve().parents[1]
WORKSPACE = BASE.parents[1]
manifest = json.loads((BASE / "source-excerpts/manifest-006.json").read_text(encoding="utf-8"))
assert manifest["unit"] == "PNB-006" and len(manifest["images"]) == 1
spec = manifest["images"][0]
source = WORKSPACE / "downloads/complete-upstream/osbooks-college-algebra-bundle" / spec["source_path"]
target = BASE / spec["path"]
rights_path = WORKSPACE / "downloads/extracted/A30/00_control/COMPONENT_RIGHTS.csv"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

assert source.is_file() and source.stat().st_size == 107515
assert digest(source) == spec["sha256"]
target.parent.mkdir(parents=True, exist_ok=True)
if target.exists():
    assert digest(target) == spec["sha256"] and target.stat().st_size == source.stat().st_size
else:
    shutil.copyfile(source, target)
assert digest(target) == spec["sha256"]

with rights_path.open(encoding="utf-8-sig", newline="") as stream:
    rows = list(csv.DictReader(stream))
matches = [row for row in rows if row["asset_path"] == spec["source_path"]]
assert len(matches) == 1
row = matches[0]
assert row["sha256"] == spec["sha256"] and int(row["bytes"]) == target.stat().st_size
fields = [
    "rights_component_id", "asset_path", "bytes", "sha256", "source_modules",
    "classification", "admission", "license_id", "attribution", "required_action",
]
notice = [{key: row[key] for key in fields}]
notice_path = BASE / "provenance/unit-006-component-notices.json"
notice_path.write_text(json.dumps(notice, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Prepared unchanged {target.relative_to(BASE)} and exact retained component-rights row")
