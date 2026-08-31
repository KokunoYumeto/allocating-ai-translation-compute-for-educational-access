"""Pure repair of the two admitted Bangladesh offline-package manifests.

Input members are (ZipInfo, bytes) AFTER export filtering/text transforms. The
function never reads/writes files and never changes retained content/QA receipts.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import PurePosixPath
import re
import zipfile

VERSION = "portable-archive-manifest-v1"
SCHEMAS = {"bn-Beng-BD.offline.v1", "bn-Beng-BD.offline.v2"}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and ".." not in path.parts and "\\" not in name and ":" not in name


def _renamed(info: zipfile.ZipInfo, name: str) -> zipfile.ZipInfo:
    result = copy.copy(info)
    result.filename = result.orig_filename = name
    return result


def repair_archive(members: list[tuple[zipfile.ZipInfo, bytes]]) -> tuple[list[tuple[zipfile.ZipInfo, bytes]], list[str]]:
    """Preserve the old manifest, then hash the current transformed member set.

    Known schemas retain their fields and standard path/bytes/sha256 entries.
    Unsupported layouts fail closed rather than silently rewriting an authority.
    Original QA hashes remain historical and are explicitly not rebound here.
    """
    records = {}
    for info, payload in members:
        if not _safe(info.filename) or info.filename in records:
            raise ValueError("Unsafe or duplicate offline-package member")
        if (info.external_attr >> 16) & 0o170000 == 0o120000:
            raise ValueError("Offline-package symlink rejected")
        records[info.filename] = (info, payload)
    manifests = [name for name in records if PurePosixPath(name).name == "MANIFEST.json"]
    if len(manifests) != 1:
        raise ValueError("Changed archive needs one reviewed MANIFEST.json layout")
    name = manifests[0]
    manifest_info, manifest_bytes = records[name]
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") not in SCHEMAS or not isinstance(manifest.get("files"), list):
        raise ValueError("Unsupported changed-archive manifest schema")
    for entry in manifest["files"]:
        if not isinstance(entry, dict) or set(entry) != {"path", "bytes", "sha256"}:
            raise ValueError("Unsupported offline manifest file entry")
        if not _safe(entry["path"]) or not isinstance(entry["bytes"], int) or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]):
            raise ValueError("Malformed offline manifest file identity")
    prefix = str(PurePosixPath(name).parent)
    prefix = "" if prefix == "." else prefix + "/"
    if any(not key.startswith(prefix) for key in records):
        raise ValueError("Archive members escape manifest-relative package root")
    entrypoint = manifest.get("entrypoint")
    if not isinstance(entrypoint, str) or not _safe(entrypoint) or prefix + entrypoint not in records:
        raise ValueError("Offline package entrypoint is absent")
    original_name = prefix + "ORIGINAL-MANIFEST.json"
    notice_name = prefix + "PORTABLE-EXPORT-NOTICE.md"
    already = manifest.get("portable_export", {}).get("version") == VERSION
    if already:
        if original_name not in records or _sha(records[original_name][1]) != manifest["portable_export"].get("original_manifest_sha256"):
            raise ValueError("Preserved original manifest identity is inconsistent")
        original_bytes = records[original_name][1]
    else:
        if original_name in records or notice_name in records:
            raise ValueError("Refusing to replace existing package historical/notice member")
        original_bytes = manifest_bytes
        records[original_name] = (_renamed(manifest_info, original_name), original_bytes)
    original_sha = _sha(original_bytes)
    notice = (
        "# Portable review export\n\n"
        "MANIFEST.json describes the actual members of this transformed review package. "
        "ORIGINAL-MANIFEST.json is historical source-package evidence, not a verifier "
        "for these changed bytes. It may refer to removed operational instructions.\n\n"
        f"Preserved original manifest SHA-256: {original_sha}\n\n"
        "Private operational text was filtered/redacted by the export process. "
        "Existing translation/source/QA receipts retain their original identities; "
        "this member-hash repair does not rerun builds, certify translation quality "
        "or rebind historical QA to changed code. The containing repository's export "
        "manifest records original and exported archive hashes and transformations.\n"
    ).encode("utf-8")
    records[notice_name] = (_renamed(manifest_info, notice_name), notice)
    current = copy.deepcopy(manifest)
    current["files"] = [
        {"path": key[len(prefix):], "bytes": len(payload), "sha256": _sha(payload)}
        for key, (info, payload) in sorted(records.items())
        if key != name and not info.is_dir()
    ]
    current["portable_export"] = {
        "version": VERSION,
        "original_manifest": "ORIGINAL-MANIFEST.json",
        "original_manifest_sha256": original_sha,
        "notice": "PORTABLE-EXPORT-NOTICE.md",
        "scope": "Current member bytes only; historical QA is not rebound or rerun",
    }
    records[name] = (manifest_info, (json.dumps(current, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    # Preserve original order (important to archive formats), append only new files.
    order = [info.filename for info, _ in members]
    order.extend(key for key in (original_name, notice_name) if key not in order)
    return [records[key] for key in order], [
        VERSION,
        f"Original package manifest retained as {original_name}; SHA-256 {original_sha}",
        f"Current {name} hashes {len(current['files'])} retained/added members; excluded raw instructions are no longer listed",
        "Historical source/QA receipts remain unmodified and do not certify transformed bytes",
    ]
