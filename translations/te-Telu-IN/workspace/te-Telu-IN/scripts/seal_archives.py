"""Verify complete pinned canonical ZIPs without downloads, extraction, or writes.

Default: stream-check both archives and print reproducible source-lock records.
--verify: additionally compare those records with sources.lock.json. Git is used
only for existing commit/tree metadata; lazy fetching and prompts are disabled.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import os
import subprocess
import zipfile

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parent
CHUNK = 1024 * 1024
ARCHIVES = (
    {
        "id": "A00-A20-en-complete-archive",
        "upstream_repository_id": "A00-A20-en",
        "checkout": "downloads/upstream-prealgebra",
        "repository": "openstax/osbooks-prealgebra-bundle",
        "commit": "38cae454e644abf9f0a623e876994553881597c9",
        "tree": "7907e4c81d43de1c3b6da173f0eb273c01dc5b55",
        "path": "downloads/canonical-archives/osbooks-prealgebra-bundle-pinned.zip",
        "bytes": 537455794,
        "sha256": "effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917",
        "git_blob_count": 13738,
        "acquisition": {
            "method": "local_copy_of_shared_pinned_archive_before_storage_alert",
            "copy_origin": "[local-home]/.codex/worktrees/e4ec/LAN ALLOC/downloads/osbooks-prealgebra-bundle-pinned.zip",
            "note": "Official source URL identifies upstream; this task copied the Marathi task's already-downloaded archive, not a direct network transfer.",
        },
    },
    {
        "id": "A30-en-complete-archive",
        "upstream_repository_id": "A30-en",
        "checkout": "downloads/upstream-precalculus",
        "repository": "openstax/osbooks-college-algebra-bundle",
        "commit": "789b54099106b071d1d32bfcee454fed72eb4768",
        "tree": "05b39123f698772482c0c33a43fa2d2d4ea562ae",
        "path": "downloads/canonical-archives/osbooks-college-algebra-bundle-pinned.zip",
        "bytes": 167391934,
        "sha256": "2fdf5495f5f11dbe3c8f6d4705a257a2ed7f13db1968cc6b2be409e0202a94f9",
        "git_blob_count": 3202,
        "acquisition": {"method": "direct_pinned_codeload_download_before_storage_alert"},
    },
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256_file(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def local_git(checkout, *args):
    env = os.environ.copy()
    env.update(GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
    return subprocess.check_output(["git", "-C", str(checkout), *args], env=env)


def git_blobs(checkout, commit, expected_tree):
    actual_tree = local_git(checkout, "rev-parse", commit + "^{tree}").decode().strip()
    require(actual_tree == expected_tree, f"Git tree mismatch: {checkout}")
    entries = local_git(checkout, "ls-tree", "-r", "-z", "--full-tree", commit)
    blobs = {}
    for entry in entries.split(b"\0"):
        if not entry:
            continue
        metadata, path = entry.split(b"\t", 1)
        mode, kind, oid = metadata.split()
        require(kind == b"blob", "Non-blob tree entry needs separate coverage: " + repr(path))
        name = path.decode("utf-8")
        require(name not in blobs, "Duplicate Git tree path: " + name)
        blobs[name] = oid.decode("ascii")
    return blobs


def verify_members(package, prefix, blobs):
    """Read each file once: ZipExtFile checks CRC at EOF; SHA-1 checks Git bytes."""
    names = set()
    seen = set()
    for member in package.infolist():
        name = member.filename
        require(name not in names, "Duplicate ZIP member: " + name)
        names.add(name)
        require(name.startswith(prefix), "Unexpected archive prefix: " + name)
        relative = name[len(prefix):]
        require("\\" not in relative, "Backslash in archive member: " + name)
        parts = PurePosixPath(relative).parts
        require(not relative.startswith("/") and ".." not in parts,
                "Unsafe archive member: " + name)
        if member.is_dir():
            require(member.file_size == 0 and member.CRC == 0,
                    "Non-empty ZIP directory: " + name)
            continue
        require(relative in blobs, "ZIP file absent from pinned Git tree: " + relative)
        require(relative not in seen, "Duplicate relative ZIP file: " + relative)
        digest = hashlib.sha1(b"blob " + str(member.file_size).encode("ascii") + b"\0")
        size = 0
        with package.open(member) as stream:
            while chunk := stream.read(CHUNK):
                size += len(chunk)
                digest.update(chunk)
        require(size == member.file_size, "ZIP size mismatch: " + relative)
        require(digest.hexdigest() == blobs[relative], "Git blob mismatch: " + relative)
        seen.add(relative)
    missing = blobs.keys() - seen
    require(not missing, f"ZIP omits {len(missing)} Git blobs: {sorted(missing)[:5]}")
    return {"zip_entries": len(names), "git_blob_count": len(seen),
            "zip_crc": "PASS", "git_blob_hashes": "PASS"}


def verify_archive(spec, root=ROOT):
    archive = root / spec["path"]
    require(archive.stat().st_size == spec["bytes"], "Archive size mismatch: " + spec["path"])
    require(sha256_file(archive) == spec["sha256"], "Archive SHA-256 mismatch: " + spec["path"])
    blobs = git_blobs(root / spec["checkout"], spec["commit"], spec["tree"])
    require(len(blobs) == spec["git_blob_count"], "Unexpected pinned Git blob count")
    prefix = spec["repository"].split("/")[1] + "-" + spec["commit"] + "/"
    with zipfile.ZipFile(archive) as package:
        require(package.comment == spec["commit"].encode("ascii"), "ZIP commit comment mismatch")
        receipt = verify_members(package, prefix, blobs)
    return {
        "id": spec["id"], "upstream_repository_id": spec["upstream_repository_id"],
        "url": f"https://codeload.github.com/{spec['repository']}/zip/{spec['commit']}",
        "commit": spec["commit"], "tree": spec["tree"], "path": spec["path"],
        "bytes": spec["bytes"], "sha256": spec["sha256"],
        "archive_prefix": prefix, **receipt,
        "coverage": "all_blobs_in_pinned_git_tree",
        "materialization": "complete_zip_not_extracted",
        "acquisition": spec["acquisition"],
        "verification": "python te-Telu-IN/scripts/seal_archives.py --verify",
    }


def verified_records():
    return [verify_archive(spec) for spec in ARCHIVES]


def verify_registered_archives(registered):
    """Verify required records without discarding additional provenance fields."""
    actual = verified_records()
    by_id = {record["id"]: record for record in registered}
    require(len(by_id) == len(registered), "Duplicate canonical archive IDs")
    require(set(by_id) == {record["id"] for record in actual},
            "Missing or unexpected canonical archive record")
    for record in actual:
        for key, value in record.items():
            require(by_id[record["id"]].get(key) == value,
                    f"Canonical archive record mismatch: {record['id']} / {key}")
    return registered


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="also check sources.lock.json")
    args = parser.parse_args()
    if args.verify:
        lock = json.loads((BASE / "sources.lock.json").read_text(encoding="utf-8"))
        records = verify_registered_archives(lock.get("canonical_archives", []))
        print(f"PASS: {len(records)} complete canonical ZIPs, "
              f"{sum(r['git_blob_count'] for r in records)} pinned Git blobs, all ZIP CRCs; no writes/extraction/downloads")
    else:
        print(json.dumps(verified_records(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
