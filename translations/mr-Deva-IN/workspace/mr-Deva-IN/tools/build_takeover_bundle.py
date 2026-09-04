#!/usr/bin/env python3
"""Build a transcript-free, deterministic Marathi takeover directory.

The Git payload is exported from an exact commit. Only actually used ignored
source/canon/review inputs are added. The output path must not already exist.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import tempfile


ROOT = Path(__file__).resolve().parents[2]
LANE = ROOT / "mr-Deva-IN"

USED_ARCHIVE_IDS = {
    "A20-id-old",
    "A20-id",
    "A20-en",
    "A30-id",
    "A30-en",
}

REMOTE_ROWS = [
    ("C14-C17", "Marathi Vishwakosh — फलन (Function)", "https://marathivishwakosh.org/21979/", "2026-08-30", "unknown", "absent", "Readable definition/domain/codomain/dependence/constant-function prose; image-only formulas not read; local acquisition failed."),
    ("C18", "Marathi Vishwakosh — आलेख", "https://vishwakosh.marathi.gov.in/24316/", "2026-08-31", "unknown", "absent", "Graph/coordinate and inequality-graph search-reader prose; no local HTML bytes."),
    ("C19", "Marathi Vishwakosh — फलन", "https://vishwakosh.marathi.gov.in/27548/", "2026-08-31", "unknown", "absent", "Opening definition/domain/codomain/image-set prose; no local HTML bytes."),
    ("C20", "Marathi Vishwakosh — गणितीय संकेतने, चिन्हे व संज्ञा", "https://vishwakosh.marathi.gov.in/21279/", "2026-08-31", "unknown", "absent", "Absolute-value, brace and interval rows via readable search results; direct opens failed."),
    ("C21", "Marathi Vishwakosh — गणितीय प्रतिरूपे", "https://vishwakosh.marathi.gov.in/21277/", "2026-08-31", "unknown", "absent", "Conic paragraph naming parabola/ellipse terms; no local HTML bytes."),
    ("C22", "Marathi Vishwakosh — भूमिती", "https://vishwakosh.marathi.gov.in/28194/", "2026-09-01", "unknown", "absent", "Slope and line-relation passages, including उतार/समांतर/छेदणाऱ्या/संपाती; search-reader text only."),
    ("HEALTH-CONTEXT-1", "CDC — About BMI", "https://www.cdc.gov/bmi/about/index.html", "2026-08-30", "unknown", "absent", "Used only for the clearly separate BMI context correction; no local page bytes."),
    ("HEALTH-CONTEXT-2", "CDC — BMI FAQ", "https://www.cdc.gov/bmi/faq/", "2026-08-30", "unknown", "absent", "Used only for the clearly separate BMI context correction; no local page bytes."),
]

ENTRY_TESTS = [
    [sys.executable, "-B", "mr-Deva-IN/tools/test_unit25_math.py"],
    [sys.executable, "-B", "mr-Deva-IN/tools/test_assemble_m81374.py"],
    [sys.executable, "-B", "mr-Deva-IN/tools/test_m81374_primary_source.py"],
]


def run(*args: str, cwd: Path = ROOT, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=text)


def git_text(*args: str) -> str:
    return run("git", *args).stdout.strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_extract(archive: Path, destination: Path) -> None:
    with tarfile.open(archive, "r:") as tar:
        for member in tar.getmembers():
            name = PurePosixPath(member.name)
            if name.is_absolute() or ".." in name.parts:
                raise ValueError(f"unsafe Git archive member: {member.name}")
        tar.extractall(destination)


def link_or_copy(source: Path, destination: Path) -> str:
    if not source.is_file():
        raise FileNotFoundError(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(source, destination)
        return "hardlink"
    except OSError:
        shutil.copy2(source, destination)
        return "copy"


def add_verified(source_rel: str, expected_sha: str, output_repo: Path, modes: dict[str, int]) -> None:
    source = ROOT / Path(source_rel)
    observed = sha256(source)
    if observed != expected_sha:
        raise ValueError(f"hash mismatch for {source_rel}: {observed} != {expected_sha}")
    mode = link_or_copy(source, output_repo / Path(source_rel))
    modes[mode] = modes.get(mode, 0) + 1


def write_remote_table(path: Path) -> None:
    header = "id\ttitle\turl\taccess_date\tknown_sha256\tlocal_bytes\tscope_and_limit\n"
    rows = ["\t".join(row) for row in REMOTE_ROWS]
    path.write_text(header + "\n".join(rows) + "\n", encoding="utf-8", newline="\n")


def build_manifest(output: Path) -> tuple[int, int, str, int]:
    manifest_path = output / "MANIFEST.sha256"
    files = sorted(
        (path for path in output.rglob("*") if path.is_file() and path != manifest_path),
        key=lambda path: path.relative_to(output).as_posix(),
    )
    total_bytes = 0
    lines: list[str] = []
    for path in files:
        size = path.stat().st_size
        total_bytes += size
        lines.append(f"{sha256(path)}  {path.relative_to(output).as_posix()}")
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return len(files), total_bytes, sha256(manifest_path), manifest_path.stat().st_size


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", default="HEAD", help="exact commit or ref to export")
    parser.add_argument("--output", required=True, type=Path, help="new output directory")
    parser.add_argument("--skip-entry-tests", action="store_true")
    args = parser.parse_args()

    checkpoint = git_text("rev-parse", f"{args.checkpoint}^{{commit}}")
    parent = git_text("rev-parse", f"{checkpoint}^")
    tree = git_text("rev-parse", f"{checkpoint}^{{tree}}")
    branch = git_text("branch", "--show-current")
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(f"output already exists: {output}")
    output.mkdir(parents=True)
    output_repo = output / "repo"
    output_repo.mkdir()

    with tempfile.NamedTemporaryFile(suffix=".tar", delete=False) as handle:
        temp_tar = Path(handle.name)
    try:
        run("git", "archive", "--format=tar", f"--output={temp_tar}", checkpoint, "mr-Deva-IN", ".gitattributes", ".gitignore")
        safe_extract(temp_tar, output_repo)
    finally:
        temp_tar.unlink(missing_ok=True)

    source_lock = json.loads((LANE / "sources.lock.json").read_text(encoding="utf-8"))
    canon_lock = json.loads((LANE / "canon" / "witnesses.lock.json").read_text(encoding="utf-8"))
    modes: dict[str, int] = {}
    included_archives: list[str] = []
    for archive in source_lock["archives"]:
        if archive["id"] not in USED_ARCHIVE_IDS:
            continue
        add_verified(archive["path"], archive["sha256"], output_repo, modes)
        included_archives.append(archive["path"])
    included_canon: list[str] = []
    for item in canon_lock["files"]:
        add_verified(item["path"], item["sha256"], output_repo, modes)
        included_canon.append(item["path"])

    review_root = ROOT / "downloads" / "mr-Deva-IN" / "source-image-qa"
    review_files: list[str] = []
    if review_root.is_dir():
        for unit_dir in sorted(review_root.glob("MR-BRIDGE-*")):
            try:
                number = int(unit_dir.name.rsplit("-", 1)[1])
            except ValueError:
                continue
            if number > 26:
                continue
            for source in sorted(path for path in unit_dir.rglob("*") if path.is_file()):
                rel = source.relative_to(ROOT).as_posix()
                mode = link_or_copy(source, output_repo / source.relative_to(ROOT))
                modes[mode] = modes.get(mode, 0) + 1
                review_files.append(rel)

    write_remote_table(output / "REMOTE_ONLY_SOURCES.tsv")

    test_results: list[dict[str, object]] = []
    if not args.skip_entry_tests:
        for command in ENTRY_TESTS:
            completed = subprocess.run(command, cwd=output_repo, capture_output=True, text=True)
            test_results.append({
                "command": command,
                "exit_code": completed.returncode,
                "stdout_tail": completed.stdout[-4000:],
                "stderr_tail": completed.stderr[-4000:],
            })
            if completed.returncode != 0:
                raise RuntimeError(f"bundle entry test failed: {command}")

    checkpoint_record = {
        "schema": 1,
        "locale": "mr-Deva-IN",
        "purpose": "transcript-free coordinator-collectable takeover bundle; translation inputs only, never training/fine-tuning data",
        "checkpoint_head": checkpoint,
        "checkpoint_parent": parent,
        "checkpoint_tree": tree,
        "branch_at_bundle_build": branch,
        "git_payload": ["mr-Deva-IN/**", ".gitattributes", ".gitignore"],
        "included_used_source_archives": included_archives,
        "included_local_canon_files": included_canon,
        "included_source_review_files": review_files,
        "remote_only_registry": "REMOTE_ONLY_SOURCES.tsv",
        "copy_modes": modes,
        "entry_test_results": test_results,
        "sanitation": {
            "excluded": [
                "raw chats and task transcripts",
                "credentials and personal host/account/task records",
                "USER_UPDATES.md and private instruction captures",
                "unused B10/B20/B40 bulk corpora and checkouts",
                "active/unaccepted MR026/MR027/MR028 and A20-m81374 PDF files",
                "transient browser/PDF renders and broken outputs",
            ],
            "note": "See repo/mr-Deva-IN/HANDOFF_RESTART.md for the durable resume cursor and active-work facts.",
        },
        "manifest_contract": "MANIFEST.sha256 covers every regular bundle file except MANIFEST.sha256 itself, in relative POSIX path order.",
    }
    (output / "CHECKPOINT.json").write_text(
        json.dumps(checkpoint_record, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    file_count, total_bytes, manifest_sha, manifest_bytes = build_manifest(output)
    summary = {
        "output": str(output),
        "checkpoint_head": checkpoint,
        "checkpoint_parent": parent,
        "checkpoint_tree": tree,
        "branch": branch,
        "manifest_file_count": file_count,
        "manifest_payload_bytes": total_bytes,
        "manifest_sha256": manifest_sha,
        "manifest_bytes": manifest_bytes,
        "entry_tests": len(test_results),
        "copy_modes": modes,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
