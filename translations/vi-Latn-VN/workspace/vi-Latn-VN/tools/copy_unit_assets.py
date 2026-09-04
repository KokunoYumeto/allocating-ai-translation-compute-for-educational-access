"""Copy only a configured unit's unchanged, inherited admitted original assets.

No new rights audit: verify exact names/hashes against the already accepted
source package's component ledger. Refuse any conflicting destination.
"""
import argparse
import csv
from hashlib import sha256
import json
from pathlib import Path
import re
from safe_output import write_atomic

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("unit")
    args = parser.parse_args()
    config = json.loads((ROOT / "units.json").read_text(encoding="utf-8"))[args.unit]
    markdown = (ROOT / "translation" / (config["slug"] + ".vi.md")).read_text(encoding="utf-8")
    names = sorted(set(re.findall(r"\.\./assets/([^/)]+)\)", markdown)))
    ledger = ROOT.parent / "downloads/a30-edition/source-core/00_control/COMPONENT_RIGHTS.csv"
    with ledger.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    accepted = []
    for name in names:
        candidates = [row for row in rows if Path(row["asset_path"]).name == name]
        assert len(candidates) == 1, name
        row = candidates[0]
        assert row["admission"] == "admitted", name
        original = ROOT.parent / "downloads/upstream-openstax/media" / name
        data = original.read_bytes()
        assert len(data) == int(row["bytes"]), name
        assert sha256(data).hexdigest() == row["sha256"], name
        destination = ROOT / "assets" / name
        if destination.exists():
            assert destination.read_bytes() == data, f"refusing conflicting asset: {name}"
        else:
            write_atomic(destination, data)
        accepted.append(row)
    notice = ROOT / "provenance" / f"{args.unit}-asset-notice.json"
    write_atomic(notice, (json.dumps(accepted, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({"unit": args.unit, "admitted_unchanged_assets": len(accepted)}))


if __name__ == "__main__":
    main()
