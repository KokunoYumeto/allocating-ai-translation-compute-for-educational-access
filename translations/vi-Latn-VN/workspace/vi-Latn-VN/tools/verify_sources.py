"""Verify source scope offline; --full checks every inventoried SHA and ZIP member."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
import json
import os
import subprocess
import xml.etree.ElementTree as ET
import zipfile
import zlib

from acquire import ROOT, LANG, archive_target, digest, download_path
from safe_output import write_atomic


def git(path, *args):
    env = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
    return subprocess.check_output(["git", "-C", str(path), *args], env=env, text=True, encoding="utf-8").strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    lock_path = LANG / "sources.lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    inventory = LANG / lock["file_inventory"]
    assert digest(inventory) == lock["file_inventory_sha256"]
    with inventory.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    repo_results = []
    for record in lock["repositories"]:
        path = download_path(record["local_path"])
        assert git(path, "rev-parse", "HEAD") == record["commit"], record["id"]
        assert git(path, "rev-parse", "HEAD^{tree}") == record["tree"], record["id"]
        assert git(path, "remote", "get-url", "origin") == record["url"], record["id"]
        present = [path / p for p in git(path, "ls-files").splitlines() if (path / p).is_file()]
        assert len(present) == record["materialized_files"], f"Incomplete materialization: {record['id']}"
        repo_results.append({"id": record["id"], "commit_tree": "pass", "materialized_files": len(present)})
        print(f"Verified checkout identity/scope: {record['id']} ({len(present)} files)", flush=True)

    def check_row(row):
        path = download_path(row["local_path"])
        assert path.is_file() and path.stat().st_size == int(row["bytes"]), path
        if args.full:
            assert digest(path) == row["observed_sha256"], f"Observed checkout bytes changed: {path}"
        return True

    with ThreadPoolExecutor(max_workers=4) as pool:
        assert all(pool.map(check_row, rows))
    archive_results = []
    for record in lock["archives"]:
        path = download_path(record["path"])
        assert path.stat().st_size == record["bytes"] and digest(path) == record["sha256"], record["id"]
        destination = download_path(record["extracted_path"])
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None, record["id"]
            entries = [entry for entry in archive.infolist() if not entry.is_dir()]
            assert len(entries) == record["files"]
            for entry in entries:
                file = archive_target(destination, entry.filename)
                assert file.is_file() and file.stat().st_size == entry.file_size, file
                if args.full:
                    checksum = 0
                    with file.open("rb") as stream:
                        for block in iter(lambda: stream.read(1024 * 1024), b""):
                            checksum = zlib.crc32(block, checksum)
                    assert checksum == entry.CRC, f"Extracted content mismatch: {file}"
        archive_results.append({"id": record["id"], "sha256_crc": "pass", "extracted_files": len(entries), "extraction_crc_checked": args.full})
        print(f"Verified archive and extracted scope: {record['id']} ({len(entries)} files)", flush=True)
    mapping = json.loads((LANG / "module-map.json").read_text(encoding="utf-8"))
    for unit in mapping["native_source_units"]:
        assert digest(ROOT / unit["path"]) == unit["sha256"], unit["source_id"]
    ns = {"c": "http://cnx.rice.edu/collxml"}
    upstream = ROOT / "downloads/upstream-openstax"
    a30 = {m.get("document") for m in ET.parse(upstream / "collections/precalculus-2e.collection.xml").findall(".//c:module", ns)}
    mv1 = {m.get("document") for m in ET.parse(upstream / "collections/algebra-and-trigonometry-2e.collection.xml").findall(".//c:module", ns)}
    assert a30 & mv1 == set(mapping["MV-1_identity_crosswalk"]["shared_module_ids"])
    assert mv1 - a30 == set(mapping["MV-1_identity_crosswalk"]["MV-1_not_in_A30"])
    receipt = {"result": "pass", "mode": "full" if args.full else "scope_and_selected_hashes", "offline": True,
               "lock_sha256": digest(lock_path), "repositories": repo_results,
               "inventory_files": len(rows), "inventory_file_hashes_checked": args.full,
               "archives": archive_results, "native_units_checked": len(mapping["native_source_units"]),
               "MV1_shared_exact_ids": len(a30 & mv1), "MV1_uncovered_ids": len(mv1 - a30)}
    target = LANG / "qa" / ("sources-full.json" if args.full else "sources-scope.json")
    write_atomic(target, (json.dumps(receipt, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
