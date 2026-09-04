"""Deterministic manifest/checksum/ZIP assembly, limited to this package."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parent
ARCHIVE_NAME = "levin-dmoi4-opening-pnb-Arab-PK-2026.09.04.zip"
EXCLUDED = {"MANIFEST.json", "CHECKSUMS.sha256", "qa/OFFLINE_REPLAY_PROGRESS.json", "qa/OFFLINE_REPLAY_FAILURE.json"}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def included(path):
    rel = path.relative_to(BASE)
    return path.is_file() and not path.is_symlink() and rel.as_posix() not in EXCLUDED and "__pycache__" not in rel.parts and path.suffix != ".pyc"


def inventory():
    result = []
    for p in sorted(BASE.rglob("*"), key=lambda p: p.relative_to(BASE).as_posix()):
        if included(p):
            b = p.read_bytes()
            result.append({"path": p.relative_to(BASE).as_posix(), "bytes": len(b), "sha256": digest(b)})
    return result


def assemble():
    rows = inventory()
    manifest = {"schema": "b10.package-inventory.v1", "version": "2026.09.04", "locale": "pnb-Arab-PK", "files": rows,
                "file_count": len(rows), "total_bytes": sum(r["bytes"] for r in rows),
                "coverage": "Front matter, complete Chapter 0, Chapter 1 opening and Section 1.1; not the whole textbook.",
                "excluded": sorted(EXCLUDED),
                "self_reference_policy": "Manifest lists all payload files except itself and CHECKSUMS.sha256. CHECKSUMS includes MANIFEST.json but not itself. ZIP readback binds every entry."}
    m = (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    (BASE / "MANIFEST.json").write_bytes(m)
    sealed = rows + [{"path": "MANIFEST.json", "bytes": len(m), "sha256": digest(m)}]
    sealed.sort(key=lambda r: r["path"])
    c = "".join(r["sha256"] + "  " + r["path"] + "\n" for r in sealed).encode("utf-8")
    (BASE / "CHECKSUMS.sha256").write_bytes(c)
    return sealed + [{"path": "CHECKSUMS.sha256", "bytes": len(c), "sha256": digest(c)}]


def zip_bytes(rows):
    target = io.BytesIO()
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for row in sorted(rows, key=lambda r: r["path"]):
            p = BASE / row["path"]
            raw = p.read_bytes()
            assert len(raw) == row["bytes"] and digest(raw) == row["sha256"], row["path"]
            info = zipfile.ZipInfo(row["path"], (2026, 9, 4, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            z.writestr(info, raw, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return target.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory-only", action="store_true")
    args = parser.parse_args()
    rows = assemble()
    if args.inventory_only:
        print(json.dumps({"result": "inventory_written", "files_including_seals": len(rows)}))
        return
    for required in ["qa/PACKAGE_VALIDATION.json", "qa/OFFLINE_REPLAY.json", "qa/VISUAL_QA.json"]:
        record = json.loads((BASE / required).read_text("utf-8"))
        assert record["result"].startswith("pass"), required
    first = zip_bytes(rows)
    second = zip_bytes(rows)
    assert first == second, "ZIP replay differs"
    with zipfile.ZipFile(io.BytesIO(first)) as z:
        assert z.testzip() is None
        assert sorted(z.namelist()) == sorted(r["path"] for r in rows)
        for r in rows:
            raw = z.read(r["path"])
            assert len(raw) == r["bytes"] and digest(raw) == r["sha256"], r["path"]
    out = BASE.parent / "release"
    out.mkdir(exist_ok=True)
    path = out / ARCHIVE_NAME
    if path.exists():
        assert path.read_bytes() == first, "Existing ZIP differs; preserve it and choose a deliberate new version instead of overwriting."
    else:
        with path.open("xb") as f:
            f.write(first)
    receipt = {"schema": "b10.deterministic-zip-readback.v1", "result": "pass", "archive": ARCHIVE_NAME,
               "bytes": len(first), "sha256": digest(first), "file_count": len(rows),
               "uncompressed_bytes": sum(r["bytes"] for r in rows), "two_assemblies_byte_identical": True,
               "every_entry_name_size_and_sha256_verified": True, "files": sorted(rows, key=lambda r: r["path"])}
    (out / "ZIP_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in receipt.items() if k != "files"}))


if __name__ == "__main__":
    main()
