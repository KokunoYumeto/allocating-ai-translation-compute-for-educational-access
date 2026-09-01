#!/usr/bin/env python3
"""Publish the standalone v1.1 GitHub successor without rewriting v1.0.

Default operation is an anonymous, read-only preflight.  ``--execute`` is the
only mode that reads a GitHub credential or mutates GitHub.  Execution uses the
Git Data API and base64 blobs, so committed bytes are exactly the local bytes
and cannot be changed by working-tree line-ending normalization.

The transaction is resumable through a sanitized state file.  It creates a
single descendant commit, advances ``main`` without force, creates a new
lightweight ``v1.1.0`` tag, uploads a complete draft release, verifies every
draft asset, publishes the release, then anonymously re-verifies v1.1 and the
frozen v1.0 commit/assets.  It never moves or replaces ``v1.0.0``.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
import time
from typing import Any
import urllib.error
import urllib.parse
import urllib.request
import zipfile

import build_standalone_release_v1_1 as release_tools


ROOT = Path(__file__).resolve().parents[1]
OWNER = "KokunoYumeto"
REPOSITORY = "allocating-ai-translation-compute-for-educational-access"
API = f"https://api.github.com/repos/{OWNER}/{REPOSITORY}"
UPLOADS = f"https://uploads.github.com/repos/{OWNER}/{REPOSITORY}"
CODELOAD = f"https://codeload.github.com/{OWNER}/{REPOSITORY}"
PAGES = f"https://{OWNER.lower()}.github.io/{REPOSITORY}/"
PREDECESSOR_COMMIT = "2c9c129c3e693bec5a0e387c76b1c270fccf399c"
PREDECESSOR_TAG = "v1.0.0"
SUCCESSOR_TAG = "v1.1.0"
BRANCH = "main"
FROZEN_RELEASE_DIR = ROOT / "standalone_release_20260830"
FROZEN_ASSET_DIR = ROOT / "staging" / "github_release_assets_20260830"
USER_AGENT = "standalone-v1.1-github-publisher/1.0"
MAX_RESPONSE = 256 * 1024 * 1024
SHA1 = re.compile(r"^[0-9a-f]{40}$")
SAFE_NAME = re.compile(r"^[A-Za-z0-9._-]+$")


class GateError(RuntimeError):
    """A sanitized, fail-closed transaction error."""


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().lower()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().lower()


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def identity(path: Path, name: str | None = None) -> dict[str, Any]:
    return {
        "filename": name or path.name,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def inventory_digest(rows: list[dict[str, Any]]) -> str:
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(canonical)


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, indent=2, sort_keys=True, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def task_path(path: Path, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise GateError(f"{label} escapes the task root") from exc
    return resolved


def disjoint_from_frozen(path: Path, label: str) -> None:
    resolved = path.resolve()
    for frozen in (FROZEN_RELEASE_DIR.resolve(), FROZEN_ASSET_DIR.resolve()):
        if resolved == frozen or resolved in frozen.parents or frozen in resolved.parents:
            raise GateError(f"{label} overlaps the immutable v1.0 snapshot")


def validate_remote_filename(name: str) -> str:
    path = PurePosixPath(name)
    if not name or "\\" in name or path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise GateError("remote inventory contains an unsafe filename")
    if path.as_posix() != name:
        raise GateError("remote inventory contains a non-canonical filename")
    return name


def local_inventory(directory: Path, *, recursive: bool) -> list[dict[str, Any]]:
    directory = task_path(directory, "local inventory directory")
    if not directory.is_dir():
        raise GateError(f"local inventory directory is missing: {directory.name}")
    rows: list[dict[str, Any]] = []
    iterator = directory.rglob("*") if recursive else directory.iterdir()
    for path in sorted(iterator):
        if path == directory / ".git" or (recursive and ".git" in path.relative_to(directory).parts):
            continue
        if path.is_symlink():
            raise GateError(f"local release contains a symlink: {path.name}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise GateError(f"local release contains a non-regular entry: {path.name}")
        relative = path.relative_to(directory).as_posix() if recursive else path.name
        validate_remote_filename(relative)
        row = identity(path, relative)
        row["git_blob_sha1"] = git_blob_sha(path.read_bytes())
        rows.append(row)
    names = [row["filename"] for row in rows]
    if len(names) != len(set(names)):
        raise GateError("local inventory contains duplicate filenames")
    rows.sort(key=lambda row: row["filename"])
    return rows


def verify_manifest(release_dir: Path, inventory: list[dict[str, Any]]) -> None:
    manifest = release_dir / "MANIFEST.sha256"
    entries: dict[str, str] = {}
    try:
        lines = manifest.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise GateError("cannot read MANIFEST.sha256") from exc
    for number, line in enumerate(lines, 1):
        digest, separator, name = line.partition("  ")
        if not separator or not re.fullmatch(r"[0-9A-Fa-f]{64}", digest) or not name:
            raise GateError(f"invalid manifest line {number}")
        name = validate_remote_filename(name)
        if name in entries:
            raise GateError(f"duplicate manifest filename: {name}")
        entries[name] = digest.lower()
    observed = {row["filename"]: row["sha256"] for row in inventory if row["filename"] != "MANIFEST.sha256"}
    if entries != observed:
        raise GateError("MANIFEST.sha256 does not exactly govern the local release tree")
    validation_path = release_dir / "PACKAGE_VALIDATION.json"
    try:
        validation = json.loads(validation_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GateError("cannot read PACKAGE_VALIDATION.json") from exc
    if validation.get("status") != "PASS" or validation.get("release_version") != "1.1.0":
        raise GateError("PACKAGE_VALIDATION.json is not a v1.1.0 PASS receipt")


def expected_asset_topology(rows: list[dict[str, Any]]) -> None:
    names = {row["filename"] for row in rows}
    required = {"MANIFEST.sha256", "PACKAGE_VALIDATION.json", "PAPER.docx", "PAPER.md", "PAPER.pdf"}
    zips = [name for name in names if name.lower().endswith(".zip")]
    if len(rows) != 6 or not required.issubset(names) or len(zips) != 1:
        raise GateError("v1.1 GitHub asset projection must contain the five controlled files and one ZIP")


def request_bytes(
    method: str,
    url: str,
    *,
    token: str | None = None,
    body: bytes | None = None,
    content_type: str | None = None,
    accept: str = "application/vnd.github+json",
    expected: tuple[int, ...] = (200,),
    timeout: int = 180,
    allow_404: bool = False,
) -> tuple[int, bytes, dict[str, str]]:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in {
        "api.github.com", "uploads.github.com", "codeload.github.com",
        "github.com", "objects.githubusercontent.com", "release-assets.githubusercontent.com", f"{OWNER.lower()}.github.io",
    }:
        raise GateError("refusing an unexpected GitHub transport host")
    headers = {"Accept": accept, "User-Agent": USER_AGENT, "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if content_type:
        headers["Content-Type"] = content_type
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read(MAX_RESPONSE + 1)
            if len(payload) > MAX_RESPONSE:
                raise GateError("GitHub response exceeded the bounded size limit")
            status = response.status
            final_host = (urllib.parse.urlsplit(response.geturl()).hostname or "").lower()
            if final_host not in {
                "api.github.com", "uploads.github.com", "codeload.github.com",
                "github.com", "objects.githubusercontent.com", "release-assets.githubusercontent.com", f"{OWNER.lower()}.github.io",
            }:
                raise GateError("GitHub redirected to an unexpected host")
            if status not in expected:
                raise GateError(f"GitHub returned unexpected HTTP {status}")
            return status, payload, dict(response.headers.items())
    except urllib.error.HTTPError as exc:
        if allow_404 and exc.code == 404:
            return 404, b"", {}
        raise GateError(f"GitHub {method} request failed with HTTP {exc.code}") from None
    except urllib.error.URLError as exc:
        raise GateError(f"GitHub transport failed ({type(exc.reason).__name__})") from None


def api_json(
    method: str,
    path_or_url: str,
    *,
    token: str | None = None,
    payload: dict[str, Any] | None = None,
    expected: tuple[int, ...] = (200,),
    allow_404: bool = False,
) -> tuple[int, Any]:
    url = path_or_url if path_or_url.startswith("https://") else API + path_or_url
    body = None if payload is None else json.dumps(payload, separators=(",", ":")).encode("utf-8")
    status, raw, _ = request_bytes(
        method, url, token=token, body=body,
        content_type="application/json" if body is not None else None,
        expected=expected, allow_404=allow_404,
    )
    if status == 404:
        return status, None
    try:
        value = json.loads(raw.decode("utf-8")) if raw else None
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GateError("GitHub returned invalid JSON") from exc
    return status, value


def branch_head(token: str | None = None) -> str:
    _, value = api_json("GET", f"/git/ref/heads/{BRANCH}", token=token)
    sha = str(((value or {}).get("object") or {}).get("sha") or "")
    if not SHA1.fullmatch(sha):
        raise GateError("GitHub main ref returned an invalid commit ID")
    return sha


def peel_tag(tag: str, token: str | None = None) -> str | None:
    status, value = api_json("GET", f"/git/ref/tags/{urllib.parse.quote(tag, safe='')}", token=token, allow_404=True)
    if status == 404:
        return None
    obj = (value or {}).get("object") or {}
    object_type = obj.get("type")
    sha = str(obj.get("sha") or "")
    if not SHA1.fullmatch(sha):
        raise GateError(f"GitHub tag {tag} has an invalid object ID")
    for _ in range(4):
        if object_type == "commit":
            return sha
        if object_type != "tag":
            raise GateError(f"GitHub tag {tag} does not resolve to a commit")
        _, tag_obj = api_json("GET", f"/git/tags/{sha}", token=token)
        obj = (tag_obj or {}).get("object") or {}
        object_type = obj.get("type")
        sha = str(obj.get("sha") or "")
        if not SHA1.fullmatch(sha):
            raise GateError(f"GitHub annotated tag {tag} has an invalid object ID")
    raise GateError(f"GitHub tag {tag} exceeds the peel-depth limit")


def release_by_tag(tag: str, token: str | None = None) -> dict[str, Any] | None:
    status, value = api_json("GET", f"/releases/tags/{urllib.parse.quote(tag, safe='')}", token=token, allow_404=True)
    if status == 404:
        return None
    if not isinstance(value, dict):
        raise GateError(f"GitHub release {tag} response is invalid")
    return value


def commit_tree(commit: str, token: str | None = None) -> str:
    _, value = api_json("GET", f"/git/commits/{commit}", token=token)
    tree = str((((value or {}).get("tree") or {}).get("sha")) or "")
    if not SHA1.fullmatch(tree):
        raise GateError("GitHub commit returned an invalid tree ID")
    return tree


def tree_inventory(tree_sha: str, token: str | None = None) -> list[dict[str, Any]]:
    _, value = api_json("GET", f"/git/trees/{tree_sha}?recursive=1", token=token)
    if not isinstance(value, dict) or value.get("truncated") is True or not isinstance(value.get("tree"), list):
        raise GateError("GitHub recursive tree is invalid or truncated")
    rows: list[dict[str, Any]] = []
    for entry in value["tree"]:
        if entry.get("type") == "tree":
            continue
        if entry.get("type") != "blob":
            raise GateError("GitHub tree contains an unsupported submodule or object")
        name = validate_remote_filename(str(entry.get("path") or ""))
        sha = str(entry.get("sha") or "")
        if not SHA1.fullmatch(sha):
            raise GateError("GitHub tree contains an invalid blob ID")
        rows.append({"filename": name, "git_blob_sha1": sha, "mode": str(entry.get("mode") or "")})
    rows.sort(key=lambda row: row["filename"])
    return rows


def codeload_inventory(commit: str) -> list[dict[str, Any]]:
    if not SHA1.fullmatch(commit):
        raise GateError("codeload verification requires an exact commit")
    _, raw, _ = request_bytes(
        "GET", f"{CODELOAD}/zip/{commit}", accept="application/zip,*/*;q=0.8", expected=(200,), timeout=300,
    )
    rows: list[dict[str, Any]] = []
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            if archive.testzip() is not None:
                raise GateError("GitHub codeload ZIP failed CRC validation")
            for info in archive.infolist():
                if info.is_dir():
                    continue
                parts = PurePosixPath(info.filename).parts
                if len(parts) < 2:
                    raise GateError("GitHub codeload ZIP has an invalid root")
                name = validate_remote_filename(PurePosixPath(*parts[1:]).as_posix())
                data = archive.read(info)
                rows.append({"filename": name, "bytes": len(data), "sha256": sha256_bytes(data)})
    except zipfile.BadZipFile as exc:
        raise GateError("GitHub codeload response is not a valid ZIP") from exc
    rows.sort(key=lambda row: row["filename"])
    return rows


def stripped(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{key: row[key] for key in ("filename", "bytes", "sha256")} for row in rows]


def compare_exact(expected: list[dict[str, Any]], observed: list[dict[str, Any]], label: str) -> None:
    if stripped(expected) != stripped(observed):
        raise GateError(f"{label} filename/byte/SHA-256 inventory mismatch")


def download_url_identity(name: str, url: str, token: str | None = None) -> dict[str, Any]:
    _, raw, _ = request_bytes("GET", url, token=token, accept="application/octet-stream", expected=(200,), timeout=300)
    return {"filename": name, "bytes": len(raw), "sha256": sha256_bytes(raw)}


def public_release_asset_inventory(tag: str) -> list[dict[str, Any]]:
    release = release_by_tag(tag)
    if release is None:
        raise GateError(f"public GitHub release {tag} is missing")
    rows: list[dict[str, Any]] = []
    for asset in release.get("assets") or []:
        name = str(asset.get("name") or "")
        if not SAFE_NAME.fullmatch(name):
            raise GateError("GitHub release contains an unsafe asset filename")
        url = str(asset.get("browser_download_url") or "")
        rows.append(download_url_identity(name, url))
    rows.sort(key=lambda row: row["filename"])
    return rows


def credential_from_gh() -> str:
    try:
        result = subprocess.run(["gh", "auth", "token"], check=False, capture_output=True, text=True)
    except OSError as exc:
        raise GateError("could not invoke gh for an execution credential") from exc
    token = result.stdout.strip()
    if result.returncode != 0 or not token:
        raise GateError("gh did not provide an execution credential")
    return token


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GateError("cannot read the GitHub transaction state") from exc
    if not isinstance(value, dict) or value.get("schema") != "standalone-github-v1.1-transaction/1.0":
        raise GateError("GitHub transaction state has an unexpected schema")
    return value


def release_by_id(release_id: int, token: str) -> dict[str, Any]:
    _, value = api_json("GET", f"/releases/{release_id}", token=token)
    if not isinstance(value, dict) or int(value.get("id", -1)) != release_id:
        raise GateError("transaction-owned GitHub release response is invalid")
    return value


def local_preflight(args: argparse.Namespace) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    release_dir = task_path(args.release_dir, "release directory")
    asset_dir = task_path(args.asset_dir, "asset directory")
    state_path = task_path(args.state, "state path")
    receipt_path = task_path(args.receipt, "receipt path")
    notes = task_path(args.notes_file, "release notes")
    for path, label in (
        (release_dir, "release directory"), (asset_dir, "asset directory"),
        (state_path, "state path"), (receipt_path, "receipt path"), (notes, "release notes"),
    ):
        disjoint_from_frozen(path, label)
    if not notes.is_file() or notes.stat().st_size == 0:
        raise GateError("release notes file is missing or empty")
    try:
        notes_text = notes.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise GateError("release notes must be UTF-8 text") from exc
    forbidden_notes = (
        re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+", re.I),
        re.compile(r"(?:github_pat_|ghp_)[A-Za-z0-9_]+", re.I),
        re.compile(r"Authorization\s*:\s*Bearer\s+\S+", re.I),
        re.compile(r"access_token\s*[=:]\s*[^\s\"']+", re.I),
    )
    if any(pattern.search(notes_text) for pattern in forbidden_notes):
        raise GateError("release notes failed the private-path/credential scan")
    release_rows = local_inventory(release_dir, recursive=True)
    asset_rows = local_inventory(asset_dir, recursive=False)
    verify_manifest(release_dir, release_rows)
    try:
        release_tools.validate_qa(release_dir)
    except release_tools.GateError as exc:
        raise GateError(f"current release QA failed: {exc}") from exc
    if not (release_dir / "index.html").is_file() or not (release_dir / ".nojekyll").is_file():
        raise GateError("release lacks its readable root index or Pages marker")
    if identity(release_dir / "index.html")["sha256"] != identity(release_dir / "staging/reader_surface_v1_1/index.html")["sha256"]:
        raise GateError("root reader differs from the audited HTML")
    expected_asset_topology(asset_rows)
    state = load_state(args.state)
    release_digest = inventory_digest(stripped(release_rows))
    asset_digest = inventory_digest(stripped(asset_rows))
    if state:
        if state.get("release_inventory_sha256") != release_digest or state.get("asset_inventory_sha256") != asset_digest:
            raise GateError("local v1.1 bytes changed after the GitHub transaction began")
        if state.get("predecessor_commit") != PREDECESSOR_COMMIT:
            raise GateError("transaction state has the wrong predecessor")
    return release_rows, asset_rows, state


def baseline_gate() -> dict[str, Any]:
    frozen_release = local_inventory(FROZEN_RELEASE_DIR, recursive=True)
    frozen_assets = local_inventory(FROZEN_ASSET_DIR, recursive=False)
    compare_exact(frozen_release, codeload_inventory(PREDECESSOR_COMMIT), "frozen v1.0 commit")
    compare_exact(frozen_assets, public_release_asset_inventory(PREDECESSOR_TAG), "frozen v1.0 release assets")
    if peel_tag(PREDECESSOR_TAG) != PREDECESSOR_COMMIT:
        raise GateError("v1.0.0 no longer resolves to the frozen predecessor commit")
    return {
        "commit": PREDECESSOR_COMMIT,
        "repository_files": len(frozen_release),
        "repository_inventory_sha256": inventory_digest(stripped(frozen_release)),
        "release_assets": len(frozen_assets),
        "asset_inventory_sha256": inventory_digest(stripped(frozen_assets)),
    }


def remote_preflight(state: dict[str, Any]) -> dict[str, Any]:
    new_commit = state.get("new_commit")
    head = branch_head()
    if new_commit:
        allowed_heads = {str(new_commit), str(state.get("base_commit") or "")}
    else:
        allowed_heads = {str(state.get("base_commit") or head)}
    if head not in allowed_heads:
        raise GateError("main does not point to the transaction's expected head")
    old_tag = peel_tag(PREDECESSOR_TAG)
    if old_tag != PREDECESSOR_COMMIT:
        raise GateError("v1.0.0 was moved from the frozen predecessor")
    new_tag = peel_tag(SUCCESSOR_TAG)
    if new_tag is not None and (not new_commit or new_tag != new_commit):
        raise GateError("v1.1.0 already exists at an unexpected commit")
    release = release_by_tag(SUCCESSOR_TAG) if not state.get("release_id") else None
    if state.get("release_id"):
        # Anonymous preflight cannot necessarily see an unpublished draft by
        # ID.  Its ownership is revalidated with authentication in --execute.
        release_id = int(state["release_id"])
    else:
        release_id = None if release is None else int(release.get("id", -1))
    if release is not None:
        if not state.get("release_id") or int(release.get("id", -1)) != int(state["release_id"]):
            raise GateError("a v1.1.0 release exists without transaction ownership")
    return {
        "branch_head": head,
        "base_commit": state.get("base_commit") or head,
        "v1_tag_commit": old_tag,
        "v1_1_tag_commit": new_tag,
        "v1_1_release_id": release_id,
        "v1_1_release_draft": None if release is None else bool(release.get("draft")),
    }


def create_commit(token: str, release_rows: list[dict[str, Any]], state: dict[str, Any], args: argparse.Namespace) -> str:
    if state.get("new_commit"):
        return str(state["new_commit"])
    base_commit = str(state.get("base_commit") or "")
    if not SHA1.fullmatch(base_commit):
        raise GateError("transaction lacks a pinned current base commit")
    base_tree = commit_tree(base_commit, token)
    predecessor_rows = tree_inventory(base_tree, token)
    local_by_name = {row["filename"]: row for row in release_rows}
    tree_entries: list[dict[str, Any]] = []
    predecessor_map = {row["filename"]: row for row in predecessor_rows}
    for name in sorted(local_by_name):
        row = local_by_name[name]
        if predecessor_map.get(name, {}).get("git_blob_sha1") == row["git_blob_sha1"]:
            continue
        data = (args.release_dir / Path(name)).read_bytes()
        _, blob = api_json(
            "POST", "/git/blobs", token=token,
            payload={"content": base64.b64encode(data).decode("ascii"), "encoding": "base64"},
            expected=(201,),
        )
        blob_sha = str((blob or {}).get("sha") or "")
        if blob_sha != row["git_blob_sha1"]:
            raise GateError(f"GitHub blob identity mismatch for {name}")
        tree_entries.append({"path": name, "mode": "100644", "type": "blob", "sha": blob_sha})
    _, tree = api_json(
        "POST", "/git/trees", token=token,
        payload={"base_tree": base_tree, "tree": tree_entries}, expected=(201,),
    )
    tree_sha = str((tree or {}).get("sha") or "")
    if not SHA1.fullmatch(tree_sha):
        raise GateError("GitHub returned an invalid successor tree ID")
    observed_tree = tree_inventory(tree_sha, token)
    observed_map = {row["filename"]: row["git_blob_sha1"] for row in observed_tree}
    expected_map = {row["filename"]: row["git_blob_sha1"] for row in predecessor_rows}
    expected_map.update({row["filename"]: row["git_blob_sha1"] for row in release_rows})
    if observed_map != expected_map:
        raise GateError("created Git tree differs from the exact local raw-byte inventory")
    _, commit = api_json(
        "POST", "/git/commits", token=token,
        payload={"message": args.commit_message, "tree": tree_sha, "parents": [base_commit]},
        expected=(201,),
    )
    commit_sha = str((commit or {}).get("sha") or "")
    if not SHA1.fullmatch(commit_sha):
        raise GateError("GitHub returned an invalid successor commit ID")
    state.update({"new_tree": tree_sha, "new_commit": commit_sha, "status": "commit_created", "updated_at_utc": utc_now()})
    atomic_json(args.state, state)
    return commit_sha


def advance_branch(token: str, commit: str, state: dict[str, Any], args: argparse.Namespace) -> None:
    head = branch_head(token)
    if head == commit:
        return
    if head != state.get("base_commit"):
        raise GateError("main changed after preflight; refusing to advance it")
    api_json(
        "PATCH", f"/git/refs/heads/{BRANCH}", token=token,
        payload={"sha": commit, "force": False}, expected=(200,),
    )
    if branch_head(token) != commit:
        raise GateError("main did not resolve to the new commit after the non-force update")
    state.update({"status": "branch_advanced_without_force", "updated_at_utc": utc_now()})
    atomic_json(args.state, state)


def create_tag(token: str, commit: str, state: dict[str, Any], args: argparse.Namespace) -> None:
    current = peel_tag(SUCCESSOR_TAG, token)
    if current is not None:
        if current != commit:
            raise GateError("v1.1.0 exists at an unexpected commit")
        return
    api_json(
        "POST", "/git/refs", token=token,
        payload={"ref": f"refs/tags/{SUCCESSOR_TAG}", "sha": commit}, expected=(201,),
    )
    if peel_tag(SUCCESSOR_TAG, token) != commit:
        raise GateError("v1.1.0 did not resolve to the intended commit")
    state.update({"status": "immutable_successor_tag_created", "updated_at_utc": utc_now()})
    atomic_json(args.state, state)


def get_or_create_draft_release(token: str, commit: str, state: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    if state.get("release_id"):
        owned = release_by_id(int(state["release_id"]), token)
        if owned.get("tag_name") != SUCCESSOR_TAG:
            raise GateError("transaction-owned release has the wrong tag")
        if not owned.get("draft") and not state.get("publish_attempted_at_utc") and not state.get("published_at_utc") and state.get("status") != "complete":
            raise GateError("transaction-owned v1.1.0 release is unexpectedly public")
        return owned
    existing = release_by_tag(SUCCESSOR_TAG, token)
    if existing is not None:
        intent = state.get("release_create_intent") or {}
        if (not state.get("release_id") and intent.get("commit") == commit
                and intent.get("tag") == SUCCESSOR_TAG
                and existing.get("tag_name") == SUCCESSOR_TAG
                and existing.get("name") == intent.get("name")
                and sha256_bytes(str(existing.get("body") or "").encode("utf-8")) == intent.get("notes_sha256")):
            state["release_id"] = int(existing["id"])
            atomic_json(args.state, state)
        if not state.get("release_id") or int(existing.get("id", -1)) != int(state["release_id"]):
            raise GateError("v1.1.0 release exists without transaction ownership")
        if not existing.get("draft") and not state.get("publish_attempted_at_utc") and state.get("status") != "complete":
            raise GateError("transaction-owned v1.1.0 release is unexpectedly public")
        return existing
    notes = args.notes_file.read_text(encoding="utf-8")
    state["release_create_intent"] = {
        "commit": commit, "tag": SUCCESSOR_TAG, "name": args.release_name,
        "notes_sha256": sha256_bytes(notes.encode("utf-8")),
    }
    atomic_json(args.state, state)
    _, release = api_json(
        "POST", "/releases", token=token,
        payload={
            "tag_name": SUCCESSOR_TAG,
            "target_commitish": commit,
            "name": args.release_name,
            "body": notes,
            "draft": True,
            "prerelease": False,
        },
        expected=(201,),
    )
    if not isinstance(release, dict) or not release.get("draft"):
        raise GateError("GitHub did not create a draft v1.1.0 release")
    state.update({"release_id": int(release["id"]), "status": "draft_release_created", "updated_at_utc": utc_now()})
    atomic_json(args.state, state)
    return release


def authenticated_asset_identity(token: str, asset: dict[str, Any]) -> dict[str, Any]:
    name = str(asset.get("name") or "")
    url = str(asset.get("url") or "")
    return download_url_identity(name, url, token)


def upload_assets(token: str, release: dict[str, Any], asset_rows: list[dict[str, Any]], state: dict[str, Any], args: argparse.Namespace) -> None:
    release_id = int(release["id"])
    _, current = api_json("GET", f"/releases/{release_id}/assets?per_page=100", token=token)
    if not isinstance(current, list):
        raise GateError("GitHub draft asset inventory is invalid")
    existing = {str(row.get("name") or ""): row for row in current}
    desired = {row["filename"]: row for row in asset_rows}
    unexpected = sorted(set(existing) - set(desired))
    if unexpected:
        raise GateError("draft release contains unexpected assets")
    for name, wanted in desired.items():
        prior = existing.get(name)
        if prior is not None:
            if authenticated_asset_identity(token, prior) != {key: wanted[key] for key in ("filename", "bytes", "sha256")}:
                raise GateError(f"existing draft asset differs from local bytes: {name}")
            continue
        data = (args.asset_dir / name).read_bytes()
        url = f"{UPLOADS}/releases/{release_id}/assets?name={urllib.parse.quote(name, safe='')}"
        # Asset uploads are raw octet streams rather than JSON requests.
        _, raw, _ = request_bytes(
            "POST", url, token=token, body=data, content_type="application/octet-stream",
            accept="application/vnd.github+json", expected=(201,), timeout=900,
        )
        try:
            uploaded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise GateError("GitHub returned invalid JSON after an asset upload") from exc
        if authenticated_asset_identity(token, uploaded) != {key: wanted[key] for key in ("filename", "bytes", "sha256")}:
            raise GateError(f"uploaded draft asset differs from local bytes: {name}")
    _, final_rows = api_json("GET", f"/releases/{release_id}/assets?per_page=100", token=token)
    observed = sorted((authenticated_asset_identity(token, row) for row in final_rows), key=lambda row: row["filename"])
    compare_exact(asset_rows, observed, "authenticated draft release assets")
    state.update({"status": "draft_assets_exact", "updated_at_utc": utc_now()})
    atomic_json(args.state, state)


def publish_release(token: str, release_id: int, state: dict[str, Any], args: argparse.Namespace) -> None:
    current = release_by_id(release_id, token)
    if current.get("tag_name") != SUCCESSOR_TAG:
        raise GateError("transaction-owned v1.1.0 release has the wrong tag")
    if not current.get("draft"):
        return
    state["publish_attempted_at_utc"] = utc_now()
    atomic_json(args.state, state)
    _, published = api_json(
        "PATCH", f"/releases/{release_id}", token=token,
        payload={"draft": False, "prerelease": False}, expected=(200,),
    )
    if not isinstance(published, dict) or published.get("draft"):
        raise GateError("GitHub did not publish the v1.1.0 release")
    state.update({"status": "published_awaiting_anonymous_readback", "published_at_utc": utc_now()})
    atomic_json(args.state, state)


def anonymous_successor_gate(commit: str, release_rows: list[dict[str, Any]], asset_rows: list[dict[str, Any]]) -> dict[str, Any]:
    last_error: Exception | None = None
    for delay in (0, 5, 20):
        if delay:
            time.sleep(delay)
        try:
            compare_exact(release_rows, codeload_inventory(commit), "public v1.1 commit")
            compare_exact(asset_rows, public_release_asset_inventory(SUCCESSOR_TAG), "public v1.1 release assets")
            if peel_tag(SUCCESSOR_TAG) != commit:
                raise GateError("public v1.1.0 tag does not resolve to the intended commit")
            return {
                "commit": commit,
                "repository_files": len(release_rows),
                "repository_inventory_sha256": inventory_digest(stripped(release_rows)),
                "release_assets": len(asset_rows),
                "asset_inventory_sha256": inventory_digest(stripped(asset_rows)),
            }
        except GateError as exc:
            last_error = exc
    raise GateError(f"public v1.1 readback did not settle ({type(last_error).__name__})")


def merged_inventory(base_rows: list[dict[str, Any]], updates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged = {row["filename"]: {key: row[key] for key in ("filename", "bytes", "sha256")} for row in base_rows}
    merged.update({row["filename"]: {key: row[key] for key in ("filename", "bytes", "sha256")} for row in updates})
    return [merged[name] for name in sorted(merged)]


def pages_gate(release_dir: Path) -> dict[str, Any]:
    expected = [identity(release_dir / name, name) for name in ("index.html", "PAPER.pdf")]
    last_error: Exception | None = None
    for delay in (0, 10, 30):
        if delay:
            time.sleep(delay)
        try:
            observed = [download_url_identity(row["filename"], PAGES + ("" if row["filename"] == "index.html" else row["filename"])) for row in expected]
            compare_exact(expected, observed, "public Pages reader and PDF")
            return {"url": PAGES, "files": observed, "status": "ANONYMOUS_EXACT_BYTE_PASS"}
        except GateError as exc:
            last_error = exc
    raise GateError(f"Pages has not served the exact current HTML/PDF ({type(last_error).__name__}); resume readback, do not republish")


def execute(args: argparse.Namespace, release_rows: list[dict[str, Any]], asset_rows: list[dict[str, Any]], state: dict[str, Any], baseline: dict[str, Any], remote: dict[str, Any]) -> dict[str, Any]:
    token = credential_from_gh()
    if not state:
        state = {
            "schema": "standalone-github-v1.1-transaction/1.0",
            "status": "authenticated_preflight_passed",
            "created_at_utc": utc_now(),
            "repository": f"{OWNER}/{REPOSITORY}",
            "branch": BRANCH,
            "base_commit": remote["base_commit"],
            "predecessor_commit": PREDECESSOR_COMMIT,
            "predecessor_tag": PREDECESSOR_TAG,
            "successor_tag": SUCCESSOR_TAG,
            "release_inventory_sha256": inventory_digest(stripped(release_rows)),
            "asset_inventory_sha256": inventory_digest(stripped(asset_rows)),
            "credential_material_persisted": False,
        }
        atomic_json(args.state, state)
    base_rows = codeload_inventory(str(state["base_commit"]))
    base_digest = inventory_digest(base_rows)
    if state.get("base_inventory_sha256") not in {None, base_digest}:
        raise GateError("pinned base-commit bytes changed")
    expected_tree = merged_inventory(base_rows, release_rows)
    state.update({"base_inventory_sha256": base_digest, "merged_inventory_sha256": inventory_digest(expected_tree)})
    atomic_json(args.state, state)
    commit = create_commit(token, release_rows, state, args)
    advance_branch(token, commit, state, args)
    compare_exact(expected_tree, codeload_inventory(commit), "preserving merged commit after branch advance")
    create_tag(token, commit, state, args)
    release = get_or_create_draft_release(token, commit, state, args)
    upload_assets(token, release, asset_rows, state, args)
    publish_release(token, int(state["release_id"]), state, args)
    successor = anonymous_successor_gate(commit, expected_tree, asset_rows)
    pages = pages_gate(args.release_dir)
    baseline_after = baseline_gate()
    if baseline_after != baseline:
        raise GateError("frozen v1.0 public identities changed during the v1.1 transaction")
    receipt = {
        "schema": "standalone-github-v1.1-publication-receipt/1.0",
        "status": "PUBLISHED_AND_ANONYMOUSLY_VERIFIED",
        "recorded_at_utc": utc_now(),
        "repository": f"https://github.com/{OWNER}/{REPOSITORY}",
        "predecessor": baseline,
        "successor": successor,
        "pages": pages,
        "preserved_current_base": {
            "commit": state["base_commit"], "inventory_sha256": base_digest,
            "unmodified_files": len(set(row["filename"] for row in base_rows) - set(row["filename"] for row in release_rows)),
            "implicit_deletions": [], "prior_updated_bytes_reachable_in_parent_commit": True,
        },
        "new_public_files": stripped(release_rows),
        "new_public_assets": stripped(asset_rows),
        "successor_tag": SUCCESSOR_TAG,
        "successor_release_url": f"https://github.com/{OWNER}/{REPOSITORY}/releases/tag/{SUCCESSOR_TAG}",
        "credential_material_persisted": False,
        "force_update_used": False,
        "raw_blob_transport": "GitHub Git Data API base64 blobs",
    }
    atomic_json(args.receipt, receipt)
    state.update({"status": "complete", "completed_at_utc": utc_now(), "receipt": args.receipt.name})
    atomic_json(args.state, state)
    return receipt


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-dir", type=Path, required=True)
    parser.add_argument("--asset-dir", type=Path, required=True)
    parser.add_argument("--notes-file", type=Path, required=True)
    parser.add_argument("--state", type=Path, default=ROOT / "GITHUB_V1_1_TRANSACTION_STATE_20260830.json")
    parser.add_argument("--receipt", type=Path, default=ROOT / "03_publication_receipts" / "GITHUB_V1_1_PUBLICATION_RECEIPT_20260830.json")
    parser.add_argument("--commit-message", default="Release standalone research package v1.1.0")
    parser.add_argument("--release-name", default="Allocating AI Translation Compute for Marginal Educational Access v1.1.0")
    parser.add_argument("--execute", action="store_true", help="mutate GitHub; default is anonymous read-only preflight")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    state: dict[str, Any] = {}
    try:
        args.release_dir = task_path(args.release_dir, "release directory")
        args.asset_dir = task_path(args.asset_dir, "asset directory")
        args.notes_file = task_path(args.notes_file, "release notes")
        args.state = task_path(args.state, "state path")
        args.receipt = task_path(args.receipt, "receipt path")
        release_rows, asset_rows, state = local_preflight(args)
        baseline = baseline_gate()
        remote = remote_preflight(state)
        plan = {
            "schema": "standalone-github-v1.1-publication-plan/1.0",
            "status": "PREFLIGHT_PASS",
            "mode": "execute" if args.execute else "dry-run",
            "repository": f"{OWNER}/{REPOSITORY}",
            "branch": BRANCH,
            "predecessor": baseline,
            "remote": remote,
            "successor_tag": SUCCESSOR_TAG,
            "release_files": len(release_rows),
            "release_inventory_sha256": inventory_digest(stripped(release_rows)),
            "release_assets": len(asset_rows),
            "asset_inventory_sha256": inventory_digest(stripped(asset_rows)),
            "credential_read": False,
            "mutations_performed": [],
        }
        if not args.execute:
            print(json.dumps(plan, indent=2, ensure_ascii=False))
            return 0
        receipt = execute(args, release_rows, asset_rows, state, baseline, remote)
        print(json.dumps(receipt, indent=2, ensure_ascii=False))
        return 0
    except GateError as exc:
        if args.execute and state:
            state.update({
                "status": "failed_closed_resumable",
                "failure_at_utc": utc_now(),
                "failure_type": type(exc).__name__,
                "credential_material_persisted": False,
            })
            try:
                atomic_json(args.state, state)
            except OSError:
                pass
        error = {
            "schema": "standalone-github-v1.1-publication-error/1.0",
            "status": "FAIL_CLOSED",
            "error": str(exc),
            "v1_tag_move_attempted": False,
            "force_update_used": False,
            "credential_material_persisted": False,
        }
        print(json.dumps(error, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
