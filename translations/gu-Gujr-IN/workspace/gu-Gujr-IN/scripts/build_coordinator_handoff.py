"""Build a deterministic, privacy-audited Gujarati coordinator handoff.

The committed payload is always read with ``git archive`` from the pinned
checkpoint; this script never snapshots the live working tree.  Supplemental
authority, canon, media, readable derivatives, and recovery material must be
enumerated byte-for-byte in a curated JSON index.  The index is intentionally
strict so that a misspelled key, an unlisted file, or a changed input stops the
build instead of silently changing the handoff.

The archive checkpoint is the handoff-only wrapper ``b729ed14...`` so the
committed ``HANDOFF_RESTART.md`` cursor is present.  Its parent
``2c09d5b6...`` is recorded separately as the translation-content checkpoint;
the wrapper does not widen the translation-completion claim.

The archive checkpoint is the handoff-only wrapper ``b729ed14...`` so the
committed ``HANDOFF_RESTART.md`` cursor is present.  Its parent
``2c09d5b6...`` is recorded separately as the translation-content checkpoint;
the wrapper does not widen the translation-completion claim.

Declaration schema (all top-level keys are required)::

  {
    "schema": "gujarati-coordinator-handoff-declarations-v1",
    "checkpoint": "b729ed14d3db9504e113be25131e7ab5b840aeb8",
    "selection_files": [
      {
        "path": "gu-Gujr-IN/handoff/source-cnxml-selection.tsv",
        "bytes": 123,
        "sha256": "<64 lowercase hex characters>"
      }
    ],
    "unavailable_inputs": [],
    "declared_omissions": [],
    "committed_exclusions": [
      {
        "path": "gu-Gujr-IN/path/declared-private.json",
        "type": "file",
        "reason": "Host-specific browser receipt"
      }
    ]
  }

The three fixed TSVs are exact inventories, not search roots.  Their rows bind
every selected path to its byte count and SHA-256.  CNXML and media rows must
name ignored files absent from the checkpoint.  Provenance rows may name
checkpoint files (verified in place) or curated ignored files.  Ignored bytes
and the four selection/declaration records are copied under
``provenance-inputs/`` with repository-relative paths preserved.

Examples, from the repository root::

  python gu-Gujr-IN/scripts/build_coordinator_handoff.py --input-index PATH --dry-run
  python gu-Gujr-IN/scripts/build_coordinator_handoff.py --input-index PATH --list
  python gu-Gujr-IN/scripts/build_coordinator_handoff.py --input-index PATH

The default destination is beneath ``gu-Gujr-IN/dist/handoff``.  Replacement
is guarded so that no removal can escape that directory.
"""

from __future__ import annotations

import argparse
import csv
from datetime import date
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import tarfile
import unicodedata
from urllib.parse import urlsplit
import zipfile


CHECKPOINT = "b729ed14d3db9504e113be25131e7ab5b840aeb8"
CONTENT_CHECKPOINT = "2c09d5b6be91aea2060aa2e04c4e48708164e281"
BRANCH = "codex/gujarati-numeracy-pilot"
INDEX_SCHEMA = "gujarati-coordinator-handoff-declarations-v1"
MANIFEST_SCHEMA = "gujarati-coordinator-handoff-manifest-v1"
DEFAULT_OUTPUT_NAME = f"gujarati-{CHECKPOINT[:12]}"

TOP_LEVEL_KEYS = {
    "schema",
    "checkpoint",
    "selection_files",
    "unavailable_inputs",
    "declared_omissions",
    "committed_exclusions",
}
SELECTION_LOCK_KEYS = {"path", "bytes", "sha256"}
SELECTION_SPECS = {
    "gu-Gujr-IN/handoff/source-cnxml-selection.tsv": ("path", "bytes", "sha256", "role", "program", "module"),
    "gu-Gujr-IN/handoff/source-media-selection.tsv": ("path", "bytes", "sha256", "role"),
    "gu-Gujr-IN/handoff/source-provenance-selection.tsv": ("path", "bytes", "sha256", "role"),
}
DECLARATIONS_PATH = "gu-Gujr-IN/handoff/declared-omissions.json"
EXPECTED_FIXED_SELECTIONS = {
    "gu-Gujr-IN/handoff/source-cnxml-selection.tsv": {
        "files": 87,
        "bytes": 9_312_953,
        "sha256": "288cba7821e0aba3c9da1c0bf7062d3741a3e1f25ccc2a10f10354791882cd14",
    },
    "gu-Gujr-IN/handoff/source-media-selection.tsv": {
        "files": 941,
        "bytes": 45_296_953,
        "sha256": "610fa3f2b50c4ac940dd6cebb9a5b58d99bb98de997771b945d65f17d30d311f",
    },
}
ROLE_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}\Z")
FILE_REQUIRED_KEYS = {
    "path",
    "kind",
    "bytes",
    "sha256",
    "identity",
    "locator",
    "access_date",
    "used_for",
}
FILE_OPTIONAL_KEYS = {
    "license_reference",
    "notes",
    "readable_derivative_of",
    "version",
}
UNAVAILABLE_REQUIRED_KEYS = {
    "kind",
    "identity",
    "locator",
    "access_date",
    "used_for",
    "reason",
}
UNAVAILABLE_OPTIONAL_KEYS = {"sha256", "version", "license_reference", "notes"}
OMISSION_REQUIRED_KEYS = {
    "kind",
    "identity",
    "locator",
    "access_date",
    "reason",
    "recorded_in",
}
OMISSION_OPTIONAL_KEYS = {"sha256", "bytes", "version", "license_reference", "notes"}
EXCLUSION_KEYS = {"path", "type", "reason"}
INPUT_KINDS = {
    "authority",
    "canon",
    "media",
    "source",
    "readable-derivative",
    "consultation-log",
    "license",
    "terminology",
    "build-tool",
    "recovery",
}

SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
OUTPUT_NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}\Z")
WINDOWS_RESERVED = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}

# These are path-level hard stops, including shared files that contain raw
# operational instructions rather than portable project state.
PRIVATE_PATH_PATTERNS = (
    re.compile(
        r"(?:^|/)(?:AGENTS\.md|USER_INSTRUCTIONS_VERBATIM\.md|"
        r"FULL_ASSIGNMENT_USER_INSTRUCTION\.md|COORDINATING_TASK\.md|"
        r"PROJECT_DISPATCH\.md)(?:$|/)",
        re.IGNORECASE,
    ),
    re.compile(r"(?:^|/)USER_UPDATES?(?:$|/)", re.IGNORECASE),
    re.compile(
        r"(?:^|/)(?:raw[-_]?chat|chat[-_]?export|conversation[-_]?export|"
        r"task[-_]?transcript)(?:[./_-]|$)",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:^|/)(?:\.env(?:\.[^/]*)?|credentials?|secrets?|id_rsa|"
        r"id_ed25519|\.netrc|\.npmrc|\.pypirc)(?:$|[./_-])",
        re.IGNORECASE,
    ),
    re.compile(r"(?:^|/)(?:\.git|\.codex)(?:$|/)", re.IGNORECASE),
    re.compile(r"(?:^|/)\.m\d+[^/]*$", re.IGNORECASE),
)

# Text is rejected for personal absolute paths, task-routing records, raw user
# message exports, and common credential encodings.  Standard system paths
# such as /usr/bin/env are intentionally not treated as personal host paths.
PRIVATE_TEXT_PATTERNS = (
    ("Windows absolute path", re.compile(rb"(?i)(?:file:/+)?[A-Z]:[\\/]")),
    (
        "personal Windows path",
        re.compile(rb"(?i)(?:file:/+)?[A-Z]:[\\/](?:Users|Documents and Settings)[\\/]"),
    ),
    ("UNC host path", re.compile(rb"\\\\[^\\/\s]+[\\/][^\\/\s]+")),
    ("personal POSIX path", re.compile(rb"/(?:Users|home)/[^/\s]+/|/root/(?:\.|[A-Za-z0-9_-])")),
    ("Codex workspace path", re.compile(rb"(?i)\.codex[\\/]worktrees[\\/]")),
    ("delegation record", re.compile(rb"(?i)<codex_delegation>|<source_thread_id>|clientThreadId|hostId")),
    ("raw verbatim user-message export", re.compile(rb"(?i)#\s*User instructions\s+.{0,8}\s*verbatim|##\s*User message\s+\d+")),
    (
        "coordinator task identity",
        re.compile(
            rb"(?i)coordinat(?:or|ing task)[^\r\n]{0,120}"
            rb"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        ),
    ),
    (
        "sibling task routing identity",
        re.compile(rb"(?i)sibling[-_ ]task[^\r\n]{0,40}(?:[:=][ ]*)?[A-Za-z0-9_-]{4,}"),
    ),
    ("private key", re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("AWS access key", re.compile(rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("GitHub token", re.compile(rb"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b")),
    (
        "credential assignment",
        re.compile(
            rb"(?i)\b(?:api[_-]?key|access[_-]?token|refresh[_-]?token|"
            rb"client[_-]?secret|password)\s*[=:]\s*['\"]?[A-Za-z0-9_./+=-]{8,}"
        ),
    ),
    ("credential-bearing URL", re.compile(rb"(?i)https?://[^/@\s:]+:[^/@\s]+@")),
    ("secret query parameter", re.compile(rb"(?i)[?&](?:token|access_token|api_key|key|secret)=[^&#\s]+")),
)
TEXT_ONLY_PATTERN_LABELS = {"Windows absolute path", "UNC host path"}

ZIP_SUFFIXES = {".zip", ".docx", ".xlsx", ".pptx", ".odt", ".ods", ".odp", ".epub", ".jar"}


class HandoffError(RuntimeError):
    """A fail-closed validation error."""


def is_link_or_reparse(path: Path) -> bool:
    metadata = path.lstat()
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    file_attributes = getattr(metadata, "st_file_attributes", 0)
    return stat.S_ISLNK(metadata.st_mode) or bool(reparse_flag and file_attributes & reparse_flag)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def git(repo: Path, *args: str, allow_failure: bool = False) -> subprocess.CompletedProcess[bytes]:
    env = os.environ.copy()
    env.update({"LC_ALL": "C", "LANG": "C", "GIT_CONFIG_NOSYSTEM": "1"})
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        check=False,
    )
    if result.returncode and not allow_failure:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise HandoffError(f"git {' '.join(args)} failed: {detail}")
    return result


def expect_exact_keys(value: dict, required: set[str], optional: set[str], label: str) -> None:
    keys = set(value)
    missing = sorted(required - keys)
    extra = sorted(keys - required - optional)
    if missing or extra:
        raise HandoffError(f"{label} keys mismatch; missing={missing}, extra={extra}")


def validate_relative_path(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise HandoffError(f"{label} must be a non-empty repository-relative string")
    if value != unicodedata.normalize("NFC", value):
        raise HandoffError(f"{label} is not NFC-normalized: {value!r}")
    if "\\" in value or "\x00" in value or any(ord(c) < 32 for c in value):
        raise HandoffError(f"{label} contains a backslash, NUL, or control character: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or str(path) != value or value in {".", ".."}:
        raise HandoffError(f"{label} is not a canonical relative POSIX path: {value!r}")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise HandoffError(f"{label} contains an unsafe component: {value!r}")
    for part in path.parts:
        if part.endswith((" ", ".")) or ":" in part:
            raise HandoffError(f"{label} is unsafe on Windows: {value!r}")
        if part.split(".", 1)[0].upper() in WINDOWS_RESERVED:
            raise HandoffError(f"{label} contains a reserved Windows name: {value!r}")
    return value


def private_path_reason(path: str) -> str | None:
    for pattern in PRIVATE_PATH_PATTERNS:
        if pattern.search(path):
            return pattern.pattern
    return None


def ensure_public_path(path: str, label: str) -> None:
    reason = private_path_reason(path)
    if reason:
        raise HandoffError(f"{label} matches a private/scratch path rule ({reason}): {path}")


def ensure_no_symlink(path: Path, repo: Path, label: str) -> None:
    try:
        relative = path.relative_to(repo)
    except ValueError as exc:
        raise HandoffError(f"{label} escapes the repository") from exc
    current = repo
    for part in relative.parts:
        current = current / part
        if not os.path.lexists(current):
            raise HandoffError(f"{label} is missing: {relative.as_posix()}")
        if is_link_or_reparse(current):
            raise HandoffError(f"{label} traverses a symlink: {current.relative_to(repo).as_posix()}")


def repo_path(repo: Path, value: str, label: str) -> Path:
    relative = validate_relative_path(value, label)
    path = repo.joinpath(*PurePosixPath(relative).parts)
    ensure_no_symlink(path, repo, label)
    return path


def validate_string(value: object, label: str, *, nonempty: bool = True) -> str:
    if not isinstance(value, str) or (nonempty and not value.strip()):
        raise HandoffError(f"{label} must be a{' non-empty' if nonempty else ''} string")
    if any(ord(c) < 32 for c in value):
        raise HandoffError(f"{label} contains control characters")
    return value


def validate_locator(value: object, label: str) -> str:
    locator = validate_string(value, label)
    parsed = urlsplit(locator)
    if parsed.scheme:
        if parsed.scheme.lower() not in {"http", "https", "urn", "doi"}:
            raise HandoffError(f"{label} uses unsupported scheme {parsed.scheme!r}")
        if parsed.username or parsed.password:
            raise HandoffError(f"{label} contains URL credentials")
        if re.search(r"(?i)(?:^|[?&])(?:token|access_token|api_key|key|secret)=", parsed.query):
            raise HandoffError(f"{label} contains a secret-like query parameter")
    else:
        validate_relative_path(locator, label)
    return locator


def validate_date(value: object, label: str) -> str:
    text = validate_string(value, label)
    try:
        parsed = date.fromisoformat(text)
    except ValueError as exc:
        raise HandoffError(f"{label} must be YYYY-MM-DD") from exc
    if parsed.isoformat() != text:
        raise HandoffError(f"{label} must be canonical YYYY-MM-DD")
    return text


def validate_used_for(value: object, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise HandoffError(f"{label} must be a non-empty array")
    items = [validate_string(item, f"{label}[]") for item in value]
    if len(items) != len(set(items)):
        raise HandoffError(f"{label} contains duplicates")
    return sorted(items)


def audit_text(display_path: str, data: bytes, *, binary: bool = False) -> list[str]:
    issues: list[str] = []
    for label, pattern in PRIVATE_TEXT_PATTERNS:
        if binary and label in TEXT_ONLY_PATTERN_LABELS:
            continue
        if pattern.search(data):
            issues.append(f"{display_path}: {label}")
    return issues


def probably_text(data: bytes) -> bool:
    if not data:
        return True
    if b"\x00" in data[:8192]:
        return False
    try:
        data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return False
    return True


def audit_zip(display_path: str, data: bytes, depth: int = 0) -> list[str]:
    issues: list[str] = []
    if depth > 3:
        return [f"{display_path}: nested ZIP depth exceeds 3"]
    try:
        archive = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        return [f"{display_path}: ZIP-signature file is not a valid ZIP"]
    names: set[str] = set()
    folded: dict[str, str] = {}
    total_uncompressed = 0
    with archive:
        for info in archive.infolist():
            try:
                name = info.filename.rstrip("/") if info.is_dir() else info.filename
                name = validate_relative_path(name, f"ZIP member in {display_path}")
            except HandoffError as exc:
                issues.append(str(exc))
                continue
            if name in names:
                issues.append(f"{display_path}!/{name}: duplicate ZIP member")
            names.add(name)
            previous = folded.setdefault(name.casefold(), name)
            if previous != name:
                issues.append(f"{display_path}: case-colliding ZIP members {previous!r} and {name!r}")
            reason = private_path_reason(name)
            if reason:
                issues.append(f"{display_path}!/{name}: private/scratch member path")
            unix_mode = info.external_attr >> 16
            if stat.S_ISLNK(unix_mode):
                issues.append(f"{display_path}!/{name}: symlink ZIP member")
            if info.flag_bits & 1:
                issues.append(f"{display_path}!/{name}: encrypted ZIP member cannot be audited")
            total_uncompressed += info.file_size
            if total_uncompressed > 8 * 1024**3:
                issues.append(f"{display_path}: ZIP expands beyond the 8 GiB audit ceiling")
                break
            if info.is_dir() or (info.flag_bits & 1):
                continue
            try:
                member_data = archive.read(info)
            except (RuntimeError, zipfile.BadZipFile) as exc:
                issues.append(f"{display_path}!/{name}: cannot read member ({exc})")
                continue
            member_display = f"{display_path}!/{name}"
            issues.extend(audit_text(member_display, member_data, binary=not probably_text(member_data)))
            if PurePosixPath(name).suffix.lower() in ZIP_SUFFIXES or member_data.startswith(b"PK\x03\x04"):
                issues.extend(audit_zip(member_display, member_data, depth + 1))
    return issues


def audit_payload(display_path: str, data: bytes) -> list[str]:
    # ASCII host paths and common secret formats can be visible even inside an
    # otherwise binary container, so scan every byte stream.  ZIP members are
    # additionally decompressed and audited below.
    issues = audit_text(display_path, data, binary=not probably_text(data))
    if PurePosixPath(display_path.split("!/", 1)[0]).suffix.lower() in ZIP_SUFFIXES or data.startswith(b"PK\x03\x04"):
        issues.extend(audit_zip(display_path, data))
    return issues


def read_git_tree(repo: Path, checkpoint: str) -> dict[str, tuple[str, str]]:
    raw = git(repo, "ls-tree", "-r", "-z", "--full-tree", checkpoint, "--", "gu-Gujr-IN").stdout
    entries: dict[str, tuple[str, str]] = {}
    folded: dict[str, str] = {}
    for record in raw.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, kind, _object_id = metadata.decode("ascii").split(" ")
        path = raw_path.decode("utf-8", "strict")
        path = validate_relative_path(path, "checkpoint tree path")
        if not path.startswith("gu-Gujr-IN/"):
            raise HandoffError(f"git tree returned an out-of-scope path: {path}")
        if kind != "blob" or mode not in {"100644", "100755"}:
            raise HandoffError(f"unsupported checkpoint entry {mode} {kind} {path}; symlinks/submodules are forbidden")
        if path in entries:
            raise HandoffError(f"duplicate checkpoint tree path: {path}")
        previous = folded.setdefault(path.casefold(), path)
        if previous != path:
            raise HandoffError(f"case-colliding checkpoint paths: {previous!r} and {path!r}")
        entries[path] = (mode, kind)
    if not entries:
        raise HandoffError("checkpoint contains no gu-Gujr-IN files")
    return entries


def read_git_archive(repo: Path, checkpoint: str, expected: dict[str, tuple[str, str]]) -> dict[str, dict]:
    archive_bytes = git(repo, "archive", "--format=tar", checkpoint, "--", "gu-Gujr-IN").stdout
    files: dict[str, dict] = {}
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:") as archive:
        for member in archive.getmembers():
            if member.isdir():
                continue
            if not member.isfile() or member.issym() or member.islnk():
                raise HandoffError(f"git archive contains a non-regular entry: {member.name}")
            path = validate_relative_path(member.name, "git archive path")
            if path in files:
                raise HandoffError(f"git archive contains duplicate path: {path}")
            extracted = archive.extractfile(member)
            if extracted is None:
                raise HandoffError(f"cannot read git archive member: {path}")
            data = extracted.read()
            if len(data) != member.size:
                raise HandoffError(f"git archive member size mismatch: {path}")
            mode = expected.get(path, (None, None))[0]
            if mode is None:
                raise HandoffError(f"git archive has an extra path not in git ls-tree: {path}")
            files[path] = {"data": data, "mode": mode}
    missing = sorted(set(expected) - set(files))
    extra = sorted(set(files) - set(expected))
    if missing or extra:
        raise HandoffError(f"git archive/tree mismatch; missing={missing[:20]}, extra={extra[:20]}")
    return files


def normalize_index(raw: object) -> dict:
    if not isinstance(raw, dict):
        raise HandoffError("input index must be a JSON object")
    expect_exact_keys(raw, TOP_LEVEL_KEYS, set(), "input index")
    if raw["schema"] != INDEX_SCHEMA:
        raise HandoffError(f"input index schema must be {INDEX_SCHEMA!r}")
    if raw["checkpoint"] != CHECKPOINT:
        raise HandoffError(f"input index checkpoint must be {CHECKPOINT}")

    selection_value = raw["selection_files"]
    if not isinstance(selection_value, list):
        raise HandoffError("selection_files must be an array")
    selection_files: list[dict] = []
    seen_selection_paths: set[str] = set()
    for index, item in enumerate(selection_value):
        label = f"selection_files[{index}]"
        if not isinstance(item, dict):
            raise HandoffError(f"{label} must be an object")
        expect_exact_keys(item, SELECTION_LOCK_KEYS, set(), label)
        path = validate_relative_path(item["path"], f"{label}.path")
        if path not in SELECTION_SPECS:
            raise HandoffError(f"{label}.path is not one of the three fixed selection TSVs: {path}")
        if path in seen_selection_paths:
            raise HandoffError(f"duplicate selection file: {path}")
        seen_selection_paths.add(path)
        size = item["bytes"]
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            raise HandoffError(f"{label}.bytes must be a non-negative integer")
        digest = validate_string(item["sha256"], f"{label}.sha256")
        if not SHA256_RE.fullmatch(digest):
            raise HandoffError(f"{label}.sha256 must be 64 lowercase hexadecimal characters")
        selection_files.append({"path": path, "bytes": size, "sha256": digest})
    missing_selections = sorted(set(SELECTION_SPECS) - seen_selection_paths)
    if missing_selections or len(selection_files) != len(SELECTION_SPECS):
        raise HandoffError(f"selection_files must lock exactly the three fixed TSVs; missing={missing_selections}")

    unavailable_value = raw["unavailable_inputs"]
    if not isinstance(unavailable_value, list):
        raise HandoffError("unavailable_inputs must be an array")
    unavailable: list[dict] = []
    unavailable_identities: set[tuple[str, str]] = set()
    for index, item in enumerate(unavailable_value):
        label = f"unavailable_inputs[{index}]"
        if not isinstance(item, dict):
            raise HandoffError(f"{label} must be an object")
        expect_exact_keys(item, UNAVAILABLE_REQUIRED_KEYS, UNAVAILABLE_OPTIONAL_KEYS, label)
        kind = validate_string(item["kind"], f"{label}.kind")
        if kind not in INPUT_KINDS:
            raise HandoffError(f"{label}.kind must be one of {sorted(INPUT_KINDS)}")
        normalized = {
            "kind": kind,
            "identity": validate_string(item["identity"], f"{label}.identity"),
            "locator": validate_locator(item["locator"], f"{label}.locator"),
            "access_date": validate_date(item["access_date"], f"{label}.access_date"),
            "used_for": validate_used_for(item["used_for"], f"{label}.used_for"),
            "reason": validate_string(item["reason"], f"{label}.reason"),
        }
        key = (normalized["identity"], normalized["locator"])
        if key in unavailable_identities:
            raise HandoffError(f"duplicate unavailable input: {key}")
        unavailable_identities.add(key)
        for optional in sorted(UNAVAILABLE_OPTIONAL_KEYS & set(item)):
            value = item[optional]
            if optional == "sha256":
                if value is not None and (not isinstance(value, str) or not SHA256_RE.fullmatch(value)):
                    raise HandoffError(f"{label}.sha256 must be null or 64 lowercase hexadecimal characters")
                normalized[optional] = value
            elif optional == "license_reference":
                normalized[optional] = validate_locator(value, f"{label}.{optional}")
            else:
                normalized[optional] = validate_string(value, f"{label}.{optional}")
        unavailable.append(normalized)

    omissions_value = raw["declared_omissions"]
    if not isinstance(omissions_value, list):
        raise HandoffError("declared_omissions must be an array")
    omissions: list[dict] = []
    omission_identities: set[tuple[str, str]] = set()
    for index, item in enumerate(omissions_value):
        label = f"declared_omissions[{index}]"
        if not isinstance(item, dict):
            raise HandoffError(f"{label} must be an object")
        expect_exact_keys(item, OMISSION_REQUIRED_KEYS, OMISSION_OPTIONAL_KEYS, label)
        kind = validate_string(item["kind"], f"{label}.kind")
        if kind not in INPUT_KINDS:
            raise HandoffError(f"{label}.kind must be one of {sorted(INPUT_KINDS)}")
        normalized = {
            "kind": kind,
            "identity": validate_string(item["identity"], f"{label}.identity"),
            "locator": validate_locator(item["locator"], f"{label}.locator"),
            "access_date": validate_date(item["access_date"], f"{label}.access_date"),
            "reason": validate_string(item["reason"], f"{label}.reason"),
            "recorded_in": validate_locator(item["recorded_in"], f"{label}.recorded_in"),
        }
        key = (normalized["identity"], normalized["locator"])
        if key in omission_identities:
            raise HandoffError(f"duplicate declared omission: {key}")
        omission_identities.add(key)
        for optional in sorted(OMISSION_OPTIONAL_KEYS & set(item)):
            value = item[optional]
            if optional == "sha256":
                if value is not None and (not isinstance(value, str) or not SHA256_RE.fullmatch(value)):
                    raise HandoffError(f"{label}.sha256 must be null or 64 lowercase hexadecimal characters")
                normalized[optional] = value
            elif optional == "bytes":
                if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < 0):
                    raise HandoffError(f"{label}.bytes must be null or a non-negative integer")
                normalized[optional] = value
            elif optional == "license_reference":
                normalized[optional] = validate_locator(value, f"{label}.{optional}")
            else:
                normalized[optional] = validate_string(value, f"{label}.{optional}")
        if ("sha256" in normalized) != ("bytes" in normalized):
            raise HandoffError(f"{label} must record sha256 and bytes together, or neither")
        omissions.append(normalized)

    exclusions_value = raw["committed_exclusions"]
    if not isinstance(exclusions_value, list):
        raise HandoffError("committed_exclusions must be an array")
    exclusions: list[dict] = []
    exclusion_paths: set[str] = set()
    for index, item in enumerate(exclusions_value):
        label = f"committed_exclusions[{index}]"
        if not isinstance(item, dict):
            raise HandoffError(f"{label} must be an object")
        expect_exact_keys(item, EXCLUSION_KEYS, set(), label)
        path = validate_relative_path(item["path"], f"{label}.path")
        if not path.startswith("gu-Gujr-IN/"):
            raise HandoffError(f"{label}.path must be beneath gu-Gujr-IN/")
        if path in exclusion_paths:
            raise HandoffError(f"duplicate committed exclusion: {path}")
        exclusion_paths.add(path)
        exclusion_type = validate_string(item["type"], f"{label}.type")
        if exclusion_type not in {"file", "directory"}:
            raise HandoffError(f"{label}.type must be 'file' or 'directory'")
        exclusions.append(
            {
                "path": path,
                "type": exclusion_type,
                "reason": validate_string(item["reason"], f"{label}.reason"),
            }
        )

    return {
        "schema": INDEX_SCHEMA,
        "checkpoint": CHECKPOINT,
        "selection_files": sorted(selection_files, key=lambda item: item["path"]),
        "unavailable_inputs": sorted(unavailable, key=lambda item: (item["locator"], item["identity"])),
        "declared_omissions": sorted(omissions, key=lambda item: (item["locator"], item["identity"])),
        "committed_exclusions": sorted(exclusions, key=lambda item: item["path"]),
    }


def parse_selection_tsv(path: str, data: bytes) -> list[dict]:
    if data.startswith(b"\xef\xbb\xbf") or b"\r" in data or (data and not data.endswith(b"\n")):
        raise HandoffError(f"selection TSV must be UTF-8 without BOM, LF-only, and newline-terminated: {path}")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HandoffError(f"selection TSV is not UTF-8: {path}") from exc
    reader = csv.reader(io.StringIO(text, newline=""), delimiter="\t", strict=True)
    rows = list(reader)
    expected_header = list(SELECTION_SPECS[path])
    if not rows or rows[0] != expected_header:
        raise HandoffError(f"selection TSV header mismatch for {path}; expected {expected_header}")
    records: list[dict] = []
    seen_paths: set[str] = set()
    for row_number, row in enumerate(rows[1:], 2):
        if len(row) != len(expected_header) or not any(row):
            raise HandoffError(f"{path}:{row_number} has a blank or wrong-width row")
        item = dict(zip(expected_header, row))
        selected_path = validate_relative_path(item["path"], f"{path}:{row_number}.path")
        ensure_public_path(selected_path, f"{path}:{row_number}.path")
        if selected_path in seen_paths:
            raise HandoffError(f"{path}:{row_number} duplicates selected path {selected_path}")
        seen_paths.add(selected_path)
        if not item["bytes"].isdigit() or str(int(item["bytes"])) != item["bytes"]:
            raise HandoffError(f"{path}:{row_number}.bytes is not a canonical non-negative integer")
        digest = item["sha256"]
        if not SHA256_RE.fullmatch(digest):
            raise HandoffError(f"{path}:{row_number}.sha256 is not 64 lowercase hexadecimal characters")
        role = validate_string(item["role"], f"{path}:{row_number}.role")
        if not ROLE_RE.fullmatch(role):
            raise HandoffError(f"{path}:{row_number}.role is not a portable role token")
        record = {
            "path": selected_path,
            "bytes": int(item["bytes"]),
            "sha256": digest,
            "role": role,
            "selection_file": path,
            "selection_row": row_number,
        }
        if path.endswith("source-cnxml-selection.tsv"):
            program = validate_string(item["program"], f"{path}:{row_number}.program")
            module = validate_string(item["module"], f"{path}:{row_number}.module")
            if program not in {"A00", "A10"} or not re.fullmatch(r"m\d{5}", module):
                raise HandoffError(f"{path}:{row_number} has invalid program/module {program}/{module}")
            record.update({"program": program, "module": module, "selection_kind": "cnxml"})
        elif path.endswith("source-media-selection.tsv"):
            record["selection_kind"] = "media"
        else:
            record["selection_kind"] = "provenance"
        records.append(record)
    if not records:
        raise HandoffError(f"selection TSV has no data rows: {path}")
    return records


def load_selection_files(repo: Path, index: dict) -> tuple[list[dict], dict[str, bytes]]:
    records: list[dict] = []
    blobs: dict[str, bytes] = {}
    all_selected_paths: set[str] = set()
    for lock in index["selection_files"]:
        path = lock["path"]
        source = repo_path(repo, path, f"selection file {path}")
        if not source.is_file() or not stat.S_ISREG(source.stat().st_mode):
            raise HandoffError(f"selection file is not a regular file: {path}")
        data = source.read_bytes()
        digest = sha256(data)
        if len(data) != lock["bytes"] or digest != lock["sha256"]:
            raise HandoffError(
                f"selection lock mismatch for {path}: bytes={len(data)}, sha256={digest}"
            )
        fixed = EXPECTED_FIXED_SELECTIONS.get(path)
        if fixed and digest != fixed["sha256"]:
            raise HandoffError(f"fixed selection digest changed for {path}: {digest} != {fixed['sha256']}")
        parsed = parse_selection_tsv(path, data)
        if fixed:
            selected_bytes = sum(item["bytes"] for item in parsed)
            if len(parsed) != fixed["files"] or selected_bytes != fixed["bytes"]:
                raise HandoffError(
                    f"fixed selection totals changed for {path}: files={len(parsed)}, bytes={selected_bytes}"
                )
        for item in parsed:
            if item["path"] in all_selected_paths:
                raise HandoffError(f"selected path occurs in more than one TSV: {item['path']}")
            all_selected_paths.add(item["path"])
        records.extend(parsed)
        blobs[path] = data

    cnxml_groups: dict[tuple[str, str], list[dict]] = {}
    for item in records:
        if item["selection_kind"] == "cnxml":
            cnxml_groups.setdefault((item["program"], item["module"]), []).append(item)
    if len(cnxml_groups) != 29:
        raise HandoffError(f"CNXML selection must cover exactly 29 modules; found {len(cnxml_groups)}")
    malformed_groups = [
        f"{program}/{module}"
        for (program, module), items in sorted(cnxml_groups.items())
        if len(items) != 3 or len({item["role"] for item in items}) != 3
    ]
    if malformed_groups:
        raise HandoffError(f"CNXML modules must each have three distinct roles: {malformed_groups}")
    return sorted(records, key=lambda item: item["path"]), blobs


def inventory_root(repo: Path, relative: str) -> set[str]:
    root = repo_path(repo, relative, f"inventory root {relative}")
    if root.is_file():
        if not stat.S_ISREG(root.stat().st_mode):
            raise HandoffError(f"inventory root is not a regular file: {relative}")
        return {relative}
    if not root.is_dir():
        raise HandoffError(f"inventory root is neither a file nor directory: {relative}")
    files: set[str] = set()
    for current_text, directories, filenames in os.walk(root, topdown=True, followlinks=False):
        current = Path(current_text)
        for name in list(directories):
            candidate = current / name
            if is_link_or_reparse(candidate):
                raise HandoffError(f"inventory contains a symlink directory: {candidate.relative_to(repo).as_posix()}")
        for name in filenames:
            candidate = current / name
            mode = candidate.lstat().st_mode
            if is_link_or_reparse(candidate) or not stat.S_ISREG(mode):
                raise HandoffError(f"inventory contains a non-regular file: {candidate.relative_to(repo).as_posix()}")
            path = candidate.relative_to(repo).as_posix()
            validate_relative_path(path, "inventory file")
            ensure_public_path(path, "inventory file")
            files.add(path)
    return files


def git_ignored(repo: Path, relative: str) -> bool:
    result = git(repo, "check-ignore", "--quiet", "--", relative, allow_failure=True)
    if result.returncode not in {0, 1}:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise HandoffError(f"git check-ignore failed for {relative}: {detail}")
    return result.returncode == 0


def apply_exclusions(files: dict[str, dict], exclusions: list[dict]) -> tuple[dict[str, dict], list[dict]]:
    excluded_paths: dict[str, str] = {}
    for exclusion in exclusions:
        path = exclusion["path"]
        if exclusion["type"] == "file":
            matches = [path] if path in files else []
        else:
            prefix = path + "/"
            matches = [candidate for candidate in files if candidate.startswith(prefix)]
        if not matches:
            raise HandoffError(f"committed exclusion matches no checkpoint files: {path}")
        for match in matches:
            if match in excluded_paths:
                raise HandoffError(f"overlapping committed exclusions both match: {match}")
            excluded_paths[match] = exclusion["reason"]
    retained = {path: item for path, item in files.items() if path not in excluded_paths}
    receipt = [
        {
            "path": path,
            "bytes": len(files[path]["data"]),
            "sha256": sha256(files[path]["data"]),
            "reason": excluded_paths[path],
        }
        for path in sorted(excluded_paths)
    ]
    return retained, receipt


def build_plan(repo: Path, index: dict, declarations_bytes: bytes) -> dict:
    resolved = git(repo, "rev-parse", "--verify", f"{CHECKPOINT}^{{commit}}").stdout.decode("ascii").strip()
    if resolved != CHECKPOINT:
        raise HandoffError(f"checkpoint resolved unexpectedly to {resolved}")
    parents = git(repo, "show", "-s", "--format=%P", CHECKPOINT).stdout.decode("ascii").strip().split()
    if len(parents) != 1:
        raise HandoffError(f"checkpoint must have exactly one parent; found {parents}")
    if parents[0] != CONTENT_CHECKPOINT:
        raise HandoffError(
            f"handoff checkpoint parent changed: {parents[0]} != content checkpoint {CONTENT_CHECKPOINT}"
        )
    tree = git(repo, "rev-parse", f"{CHECKPOINT}^{{tree}}").stdout.decode("ascii").strip()
    content_parents = git(repo, "show", "-s", "--format=%P", CONTENT_CHECKPOINT).stdout.decode("ascii").strip().split()
    if len(content_parents) != 1:
        raise HandoffError(f"content checkpoint must have exactly one parent; found {content_parents}")
    content_tree = git(repo, "rev-parse", f"{CONTENT_CHECKPOINT}^{{tree}}").stdout.decode("ascii").strip()
    commit_epoch_text = git(repo, "show", "-s", "--format=%ct", CHECKPOINT).stdout.decode("ascii").strip()
    if not commit_epoch_text.isdigit():
        raise HandoffError("checkpoint commit timestamp is not numeric")
    branch_check = git(repo, "merge-base", "--is-ancestor", CHECKPOINT, f"refs/heads/{BRANCH}", allow_failure=True)
    if branch_check.returncode != 0:
        raise HandoffError(f"local branch {BRANCH!r} does not contain checkpoint {CHECKPOINT}")

    expected = read_git_tree(repo, CHECKPOINT)
    archived = read_git_archive(repo, CHECKPOINT, expected)
    retained, excluded_receipt = apply_exclusions(archived, index["committed_exclusions"])
    if "gu-Gujr-IN/HANDOFF_RESTART.md" not in retained:
        raise HandoffError("handoff checkpoint cursor gu-Gujr-IN/HANDOFF_RESTART.md must be preserved")

    issues: list[str] = []
    for path, item in sorted(retained.items()):
        reason = private_path_reason(path)
        if reason:
            issues.append(f"{path}: private/scratch path was not declared as a committed exclusion")
        issues.extend(audit_payload(path, item["data"]))

    selection_rows, selection_blobs = load_selection_files(repo, index)
    indexed_paths = {item["path"] for item in selection_rows}
    supplemental: dict[str, dict] = {}
    checkpoint_selections: list[dict] = []
    copied_selections: list[dict] = []
    for entry in selection_rows:
        relative = entry["path"]
        if relative.startswith(("gu-Gujr-IN/dist/handoff/", "gu-Gujr-IN/handoff/")):
            raise HandoffError(f"selected source cannot come from handoff metadata/output: {relative}")
        if relative in archived:
            if entry["selection_kind"] != "provenance":
                raise HandoffError(f"CNXML/media selection unexpectedly names a checkpoint file: {relative}")
            if relative not in retained:
                raise HandoffError(f"selected checkpoint provenance was declared excluded: {relative}")
            data = retained[relative]["data"]
            digest = sha256(data)
            if len(data) != entry["bytes"] or digest != entry["sha256"]:
                raise HandoffError(
                    f"checkpoint provenance selection mismatch for {relative}: bytes={len(data)}, sha256={digest}"
                )
            checkpoint_selections.append(entry)
            continue
        if not git_ignored(repo, relative):
            raise HandoffError(f"selected non-checkpoint input is not ignored by Git: {relative}")
        source = repo_path(repo, relative, f"supplemental file {relative}")
        if not source.is_file() or not stat.S_ISREG(source.stat().st_mode):
            raise HandoffError(f"supplemental input is not a regular file: {relative}")
        data = source.read_bytes()
        if len(data) != entry["bytes"]:
            raise HandoffError(f"supplemental byte count changed for {relative}: {len(data)} != {entry['bytes']}")
        digest = sha256(data)
        if digest != entry["sha256"]:
            raise HandoffError(f"supplemental SHA-256 changed for {relative}: {digest} != {entry['sha256']}")
        destination = f"provenance-inputs/{relative}"
        validate_relative_path(destination, "supplemental destination")
        ensure_public_path(destination, "supplemental destination")
        issues.extend(audit_payload(destination, data))
        supplemental[destination] = {"data": data, "mode": "100644", "entry": entry}
        copied_selections.append(entry)

    metadata_blobs = dict(selection_blobs)
    metadata_blobs[DECLARATIONS_PATH] = declarations_bytes
    for relative, data in sorted(metadata_blobs.items()):
        destination = f"provenance-inputs/{relative}"
        validate_relative_path(destination, "selection metadata destination")
        ensure_public_path(destination, "selection metadata destination")
        issues.extend(audit_payload(destination, data))
        if destination in supplemental:
            raise HandoffError(f"selection metadata destination collides with selected input: {destination}")
        supplemental[destination] = {
            "data": data,
            "mode": "100644",
            "entry": {"path": relative, "selection_kind": "selection-metadata"},
        }

    available_source_paths = set(retained) | indexed_paths
    available_source_paths.update(SELECTION_SPECS)
    available_source_paths.add(DECLARATIONS_PATH)
    for entry in index["unavailable_inputs"]:
        if not urlsplit(entry["locator"]).scheme:
            raise HandoffError(
                f"unavailable input must have a portable remote/identifier locator: {entry['identity']}"
            )
    for entry in index["declared_omissions"]:
        if not urlsplit(entry["locator"]).scheme:
            raise HandoffError(f"declared omission must have a portable remote locator: {entry['identity']}")
        for field in ("recorded_in", "license_reference"):
            if field not in entry:
                continue
            reference = entry[field]
            if not urlsplit(reference).scheme and reference not in available_source_paths:
                raise HandoffError(
                    f"declared omission has a local {field} absent from bundle inputs: {reference}"
                )

    normalized_index_bytes = canonical_json(index)
    issues.extend(audit_payload("PROVENANCE_INPUTS.json", normalized_index_bytes))
    if issues:
        shown = "\n  - ".join(issues[:100])
        remainder = len(issues) - min(100, len(issues))
        suffix = f"\n  ... and {remainder} more" if remainder else ""
        raise HandoffError(f"privacy/export audit failed:\n  - {shown}{suffix}")

    payload: dict[str, dict] = {}
    for path, item in retained.items():
        payload[path] = {"data": item["data"], "mode": item["mode"], "component": "checkpoint"}
    for path, item in supplemental.items():
        payload[path] = {"data": item["data"], "mode": item["mode"], "component": "provenance-input"}
    payload["PROVENANCE_INPUTS.json"] = {
        "data": normalized_index_bytes,
        "mode": "100644",
        "component": "generated-provenance-index",
    }

    folded: dict[str, str] = {}
    for path in payload:
        previous = folded.setdefault(path.casefold(), path)
        if previous != path:
            raise HandoffError(f"case-colliding bundle paths: {previous!r} and {path!r}")

    file_records = [
        {
            "path": path,
            "bytes": len(item["data"]),
            "sha256": sha256(item["data"]),
            "mode": item["mode"],
            "component": item["component"],
        }
        for path, item in sorted(payload.items())
    ]
    component_totals = {}
    for component in ("checkpoint", "provenance-input", "generated-provenance-index"):
        selected = [record for record in file_records if record["component"] == component]
        component_totals[component] = {
            "files": len(selected),
            "bytes": sum(record["bytes"] for record in selected),
        }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "checkpoint": {
            "commit": CHECKPOINT,
            "parent": parents[0],
            "tree": tree,
            "branch": BRANCH,
        },
        "content_checkpoint": {
            "commit": CONTENT_CHECKPOINT,
            "parent": content_parents[0],
            "tree": content_tree,
            "branch": BRANCH,
        },
        "construction": {
            "committed_source": "git archive of checkpoint, path gu-Gujr-IN",
            "supplemental_source": "exact ignored files enumerated by the three locked selection TSVs",
            "working_tree_snapshot_used": False,
            "deterministic_mtime_epoch": int(commit_epoch_text),
        },
        "excluded_checkpoint_files": excluded_receipt,
        "unavailable_inputs": index["unavailable_inputs"],
        "declared_omissions": index["declared_omissions"],
        "curated_selection": {
            "selection_files": [
                {
                    "path": path,
                    "bytes": len(data),
                    "sha256": sha256(data),
                    "rows": sum(1 for item in selection_rows if item["selection_file"] == path),
                    "selected_bytes": sum(
                        item["bytes"] for item in selection_rows if item["selection_file"] == path
                    ),
                }
                for path, data in sorted(selection_blobs.items())
            ],
            "checkpoint_files_verified_in_place": len(checkpoint_selections),
            "ignored_files_copied": len(copied_selections),
            "selected_files": len(selection_rows),
            "selected_bytes": sum(item["bytes"] for item in selection_rows),
        },
        "files": file_records,
        "totals": {
            "scope": "files array; excludes MANIFEST.json and sha256sums.txt",
            "files": len(file_records),
            "bytes": sum(record["bytes"] for record in file_records),
            "components": component_totals,
        },
    }
    manifest_bytes = canonical_json(manifest)
    sums_records = [(record["path"], record["sha256"]) for record in file_records]
    sums_records.append(("MANIFEST.json", sha256(manifest_bytes)))
    sums_bytes = "".join(f"{digest}  {path}\n" for path, digest in sorted(sums_records)).encode("utf-8")
    return {
        "payload": payload,
        "manifest": manifest,
        "manifest_bytes": manifest_bytes,
        "sums_bytes": sums_bytes,
        "commit_epoch": int(commit_epoch_text),
    }


def assert_directory_has_no_symlinks(path: Path) -> None:
    if not path.exists():
        return
    if is_link_or_reparse(path) or not path.is_dir():
        raise HandoffError(f"replacement target is not a real directory: {path}")
    for current_text, directories, filenames in os.walk(path, topdown=True, followlinks=False):
        current = Path(current_text)
        for name in [*directories, *filenames]:
            candidate = current / name
            if is_link_or_reparse(candidate):
                raise HandoffError(f"replacement target contains a symlink: {candidate}")


def guarded_remove(path: Path, handoff_root: Path) -> None:
    if path.parent != handoff_root or handoff_root.name != "handoff" or handoff_root.parent.name != "dist":
        raise HandoffError(f"refusing removal outside gu-Gujr-IN/dist/handoff: {path}")
    if not path.exists():
        return
    assert_directory_has_no_symlinks(path)
    shutil.rmtree(path)


def write_file(path: Path, data: bytes, mode: str, epoch: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    path.chmod(0o755 if mode == "100755" else 0o644)
    os.utime(path, (epoch, epoch), follow_symlinks=False)


def set_tree_times(root: Path, epoch: int) -> None:
    directories = [path for path in root.rglob("*") if path.is_dir()]
    for path in sorted(directories, key=lambda item: len(item.parts), reverse=True):
        os.utime(path, (epoch, epoch), follow_symlinks=False)
    os.utime(root, (epoch, epoch), follow_symlinks=False)


def write_bundle(repo: Path, output_name: str, plan: dict) -> Path:
    if not OUTPUT_NAME_RE.fullmatch(output_name) or output_name in {".", ".."}:
        raise HandoffError("--output-name must be a simple portable name of at most 80 characters")
    language_root = repo / "gu-Gujr-IN"
    handoff_root = language_root / "dist" / "handoff"
    for existing in (language_root, language_root / "dist", handoff_root):
        if os.path.lexists(existing) and is_link_or_reparse(existing):
            raise HandoffError(f"handoff output path traverses a symlink: {existing}")
    handoff_root.mkdir(parents=True, exist_ok=True)
    if handoff_root.resolve() != (repo / "gu-Gujr-IN" / "dist" / "handoff").resolve():
        raise HandoffError("handoff output root resolved unexpectedly")

    destination = handoff_root / output_name
    staging = handoff_root / f".{output_name}.staging"
    backup = handoff_root / f".{output_name}.previous"
    guarded_remove(staging, handoff_root)
    guarded_remove(backup, handoff_root)
    staging.mkdir()
    try:
        for relative, item in sorted(plan["payload"].items()):
            target = staging.joinpath(*PurePosixPath(relative).parts)
            write_file(target, item["data"], item["mode"], plan["commit_epoch"])
        write_file(staging / "MANIFEST.json", plan["manifest_bytes"], "100644", plan["commit_epoch"])
        write_file(staging / "sha256sums.txt", plan["sums_bytes"], "100644", plan["commit_epoch"])

        # Re-read the staged bytes before replacement; no generated file is
        # trusted merely because it was present in the in-memory plan.
        for record in plan["manifest"]["files"]:
            actual = staging.joinpath(*PurePosixPath(record["path"]).parts).read_bytes()
            if len(actual) != record["bytes"] or sha256(actual) != record["sha256"]:
                raise HandoffError(f"staged payload verification failed: {record['path']}")
        if sha256((staging / "MANIFEST.json").read_bytes()) != sha256(plan["manifest_bytes"]):
            raise HandoffError("staged MANIFEST.json verification failed")
        if (staging / "sha256sums.txt").read_bytes() != plan["sums_bytes"]:
            raise HandoffError("staged sha256sums.txt verification failed")
        assert_directory_has_no_symlinks(staging)
        expected_paths = {record["path"] for record in plan["manifest"]["files"]}
        expected_paths.update({"MANIFEST.json", "sha256sums.txt"})
        actual_paths = {
            path.relative_to(staging).as_posix()
            for path in staging.rglob("*")
            if path.is_file()
        }
        if actual_paths != expected_paths:
            missing = sorted(expected_paths - actual_paths)
            extra = sorted(actual_paths - expected_paths)
            raise HandoffError(f"staged file inventory mismatch; missing={missing}, extra={extra}")
        set_tree_times(staging, plan["commit_epoch"])

        if destination.exists():
            assert_directory_has_no_symlinks(destination)
            destination.rename(backup)
        try:
            staging.rename(destination)
        except Exception:
            if backup.exists() and not destination.exists():
                backup.rename(destination)
            raise
        set_tree_times(destination, plan["commit_epoch"])
        guarded_remove(backup, handoff_root)
    except Exception:
        guarded_remove(staging, handoff_root)
        raise
    return destination


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-index", required=True, help="Curated JSON index, relative to the repository root")
    parser.add_argument("--output-name", default=DEFAULT_OUTPUT_NAME, help=f"Directory name below gu-Gujr-IN/dist/handoff (default: {DEFAULT_OUTPUT_NAME})")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Validate and summarize without writing output")
    mode.add_argument("--list", action="store_true", help="Validate and list every planned payload path without writing output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    script = Path(__file__).resolve()
    repo_text = git(script.parent, "rev-parse", "--show-toplevel").stdout.decode("utf-8").strip()
    repo = Path(repo_text).resolve()
    expected_script = repo / "gu-Gujr-IN" / "scripts" / "build_coordinator_handoff.py"
    if script != expected_script.resolve():
        raise HandoffError("script must run from gu-Gujr-IN/scripts inside its repository")
    index_value = validate_relative_path(args.input_index.replace("\\", "/"), "--input-index")
    ensure_public_path(index_value, "--input-index")
    if index_value.startswith("gu-Gujr-IN/dist/handoff/"):
        raise HandoffError("--input-index cannot be read from a prior or replacement handoff directory")
    index_path = repo_path(repo, index_value, "--input-index")
    if not index_path.is_file() or not stat.S_ISREG(index_path.stat().st_mode):
        raise HandoffError("--input-index must name a regular file")
    raw_index_bytes = index_path.read_bytes()
    issues = audit_payload(index_value, raw_index_bytes)
    if issues:
        raise HandoffError("input index privacy audit failed:\n  - " + "\n  - ".join(issues))
    try:
        raw_index = json.loads(raw_index_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HandoffError(f"input index is not strict UTF-8 JSON: {exc}") from exc
    index = normalize_index(raw_index)
    plan = build_plan(repo, index)

    summary = {
        "result": "pass",
        "mode": "list" if args.list else "dry-run" if args.dry_run else "build",
        "checkpoint": plan["manifest"]["checkpoint"],
        "payload_files": plan["manifest"]["totals"]["files"],
        "payload_bytes": plan["manifest"]["totals"]["bytes"],
        "manifest_sha256": sha256(plan["manifest_bytes"]),
        "sha256sums_sha256": sha256(plan["sums_bytes"]),
    }
    if args.list:
        for record in plan["manifest"]["files"]:
            print(f"{record['sha256']}  {record['path']}")
        print(f"{sha256(plan['manifest_bytes'])}  MANIFEST.json")
    if not args.dry_run and not args.list:
        destination = write_bundle(repo, args.output_name, plan)
        summary["output"] = destination.relative_to(repo).as_posix()
        summary["final_files"] = plan["manifest"]["totals"]["files"] + 2
        summary["final_bytes"] = (
            plan["manifest"]["totals"]["bytes"]
            + len(plan["manifest_bytes"])
            + len(plan["sums_bytes"])
        )
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except HandoffError as exc:
        raise SystemExit(f"handoff build refused: {exc}")
