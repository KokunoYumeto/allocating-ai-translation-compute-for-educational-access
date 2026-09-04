"""Create and verify the deterministic m82630 packet archive."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT / "PACKAGE.zip"
FIXED_TIME = (2026, 9, 4, 0, 0, 0)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    manifest = json.loads((ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
    rows = manifest["files"]
    expected = {row["path"]: (row["bytes"], row["sha256"]) for row in rows}
    expected["MANIFEST.json"] = ((ROOT / "MANIFEST.json").stat().st_size, sha((ROOT / "MANIFEST.json").read_bytes()))
    checksum_lines = (ROOT / "CHECKSUMS.sha256").read_text(encoding="utf-8").splitlines()
    indexed = {}
    for line in checksum_lines:
        digest, rel = line.split("  ", 1)
        indexed[rel] = digest
    assert set(indexed) == set(expected)
    for rel, (size, digest) in expected.items():
        data = (ROOT / rel).read_bytes()
        assert len(data) == size and sha(data) == digest and indexed[rel] == digest

    members = sorted([*expected, "CHECKSUMS.sha256"])
    temporary = ARCHIVE.with_suffix(".zip.tmp")
    if temporary.exists():
        temporary.unlink()
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for rel in members:
            info = zipfile.ZipInfo(rel, FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (ROOT / rel).read_bytes())
    temporary.replace(ARCHIVE)

    with zipfile.ZipFile(ARCHIVE, "r") as archive:
        assert archive.testzip() is None
        assert archive.namelist() == members
        for rel in members:
            assert archive.read(rel) == (ROOT / rel).read_bytes()
    print(json.dumps({
        "status": "pass",
        "archive": ARCHIVE.name,
        "entries": len(members),
        "bytes": ARCHIVE.stat().st_size,
        "sha256": sha(ARCHIVE.read_bytes()),
    }, indent=2))


if __name__ == "__main__":
    main()
