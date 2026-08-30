#!/usr/bin/env python3
"""Verify a standalone release directory, its SHA-256 manifest, and ZIP mirror."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def parse_manifest(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        digest, separator, relative = line.partition("  ")
        if not separator or len(digest) != 64 or not relative:
            raise ValueError(f"invalid manifest line {number}")
        if relative in entries:
            raise ValueError(f"duplicate manifest path: {relative}")
        entries[relative] = digest.upper()
    return entries


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release_dir", type=Path)
    parser.add_argument("zip_path", type=Path)
    args = parser.parse_args()

    release = args.release_dir.resolve()
    archive_path = args.zip_path.resolve()
    manifest_path = release / "MANIFEST.sha256"
    entries = parse_manifest(manifest_path)
    actual_files = {
        path.relative_to(release).as_posix(): path
        for path in release.rglob("*")
        if path.is_file() and path.name != "MANIFEST.sha256"
    }
    if set(entries) != set(actual_files):
        raise RuntimeError("manifest and release inventories differ")
    mismatches = [
        relative for relative, path in actual_files.items()
        if sha256_file(path) != entries[relative]
    ]
    if mismatches:
        raise RuntimeError(f"manifest hash mismatches: {mismatches}")

    expected_zip_names = sorted(
        path.relative_to(release).as_posix()
        for path in release.rglob("*")
        if path.is_file()
    )
    with zipfile.ZipFile(archive_path) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("ZIP CRC verification failed")
        if sorted(archive.namelist()) != expected_zip_names:
            raise RuntimeError("ZIP and release inventories differ")
        zip_mismatches = []
        for relative in expected_zip_names:
            local = release / relative
            if sha256_bytes(archive.read(relative)) != sha256_file(local):
                zip_mismatches.append(relative)
        if zip_mismatches:
            raise RuntimeError(f"ZIP member hash mismatches: {zip_mismatches}")

    result = {
        "status": "PASS",
        "release_file_count": len(expected_zip_names),
        "manifest_entry_count": len(entries),
        "release_total_bytes": sum(path.stat().st_size for path in release.rglob("*") if path.is_file()),
        "zip_bytes": archive_path.stat().st_size,
        "zip_sha256": sha256_file(archive_path),
        "manifest_sha256": sha256_file(manifest_path),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
