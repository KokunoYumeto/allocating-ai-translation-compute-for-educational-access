"""Replay the source lock. Dry-run by default; never overwrite existing source files."""
import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import tempfile
from urllib.request import Request, urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT / "vi-Latn-VN"


def digest(path):
    h = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def download_path(relative):
    path = (ROOT / relative).resolve()
    boundary = (ROOT / "downloads").resolve()
    if path == boundary or not path.is_relative_to(boundary):
        raise ValueError(f"Target must be strictly under downloads: {relative}")
    return path


def git(path, *args):
    return subprocess.check_output(["git", "-C", str(path), *args], text=True, encoding="utf-8").strip()


def checkout(record):
    path = download_path(record["local_path"])
    if path.exists():
        if not (path / ".git").exists():
            raise ValueError(f"Existing non-checkout; refusing to replace: {path}")
        assert git(path, "remote", "get-url", "origin") == record["url"], path
        assert git(path, "rev-parse", "HEAD") == record["commit"], path
        assert not git(path, "status", "--porcelain"), f"Modified checkout: {path}"
        # verify_sources checks physical scope; matching HEAD is not sufficient.
        return
    path.mkdir(parents=True)
    git(path, "init", "--quiet")
    git(path, "remote", "add", "origin", record["url"])
    git(path, "fetch", "--filter=blob:none", "--depth=1", "origin", record["commit"])
    if record["sparse_paths"]:
        git(path, "sparse-checkout", "init", "--cone")
        git(path, "sparse-checkout", "set", *record["sparse_paths"])
    git(path, "checkout", "--detach", "--quiet", record["commit"])
    assert git(path, "rev-parse", "HEAD^{tree}") == record["tree"]


def fetch_file(record):
    path = download_path(record["path"])
    if path.exists():
        assert digest(path) == record["sha256"], f"Existing file differs: {path}"
        return path
    assert record.get("url"), f"Acquire the repository containing this embedded archive: {path}"
    path.parent.mkdir(parents=True, exist_ok=True)
    # A failed transfer remains a uniquely named .part file for diagnosis.
    with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".part", delete=False) as output:
        partial = Path(output.name)
        request = Request(record["url"], headers={"User-Agent": "VietnameseTranslationSources/1.0"})
        with urlopen(request, timeout=60) as response:
            shutil.copyfileobj(response, output)
    assert partial.stat().st_size == record["bytes"], partial
    assert digest(partial) == record["sha256"], f"Hash mismatch; kept at {partial}"
    assert not path.exists(), path
    partial.rename(path)
    return path


def archive_target(destination, name):
    member = PurePosixPath(name.replace("\\", "/"))
    if member.is_absolute() or ".." in member.parts or ":" in name:
        raise ValueError(f"Unsafe archive member: {name}")
    target = (destination / Path(*member.parts)).resolve()
    if target == destination.resolve() or not target.is_relative_to(destination.resolve()):
        raise ValueError(f"Archive member escapes destination: {name}")
    return target


def extract_checked(path, destination):
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None, f"Archive CRC failure: {path}"
        for entry in archive.infolist():
            if entry.is_dir():
                continue
            if stat.S_ISLNK(entry.external_attr >> 16):
                raise ValueError(f"Archive symlink not supported: {entry.filename}")
            target = archive_target(destination, entry.filename)
            data = archive.read(entry)
            if target.exists():
                assert target.is_file() and digest(target) == sha256(data).hexdigest(), f"Existing extracted file differs: {target}"
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as output:
                    output.write(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--with-canon", action="store_true", help="also fetch language witnesses; live HTML can change")
    args = parser.parse_args()
    if args.apply and shutil.disk_usage(ROOT).free < 3 * 1024**3:
        raise RuntimeError("Less than 3 GiB free: no acquisition. Reuse verified local sources; do not delete data automatically.")
    lock = json.loads((LANG / "sources.lock.json").read_text(encoding="utf-8"))
    for record in lock["repositories"]:
        print(f"Checkout {record['id']}: {record['commit']} -> {record['local_path']}", flush=True)
        if args.apply:
            checkout(record)
    for record in lock["archives"]:
        print(f"Verify/extract {record['id']} -> {record['extracted_path']}", flush=True)
        if args.apply:
            extract_checked(fetch_file(record), download_path(record["extracted_path"]))
    if args.with_canon:
        for record in lock["language_canon"]:
            print(f"Language witness {record['id']} -> {record['path']}", flush=True)
            if args.apply:
                fetch_file(record)
    if args.apply:
        subprocess.run([sys.executable, str(LANG / "tools/verify_sources.py")], check=True)
    else:
        print("Dry-run only. --apply downloads; no existing data is replaced.")


if __name__ == "__main__":
    main()
