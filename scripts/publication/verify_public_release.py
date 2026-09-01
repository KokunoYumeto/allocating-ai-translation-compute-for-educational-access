#!/usr/bin/env python3
"""Verify public GitHub and Zenodo bytes against a local release directory.

The verifier is deliberately anonymous and read-only.  It never reads tokens,
credentials, Git configuration, or local repository metadata.  GitHub is
compared to the complete blob tree at an immutable resolution of the requested
ref.  Zenodo is compared separately to regular files at the top level of an
explicit local upload projection, which defaults to the release directory.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tempfile
import time
from typing import Any, Iterable
import urllib.error
import urllib.parse
import urllib.request
import zipfile


CHUNK_SIZE = 1024 * 1024
MAX_JSON_BYTES = 64 * 1024 * 1024
GITHUB_API = "https://api.github.com"
GITHUB_RAW = "https://raw.githubusercontent.com"
GITHUB_CODELOAD = "https://codeload.github.com"
ZENODO_API = "https://zenodo.org/api"
USER_AGENT = "public-release-byte-verifier/1.0"
SCHEMA = "public-release-verification-receipt/v1"
SIMPLE_GITHUB_COMPONENT = re.compile(r"^[A-Za-z0-9_.-]+$")
SHA1 = re.compile(r"^[0-9a-f]{40}$")


class VerificationError(Exception):
    """A controlled, sanitized verification error."""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Anonymously download and SHA-256 verify every GitHub blob at a "
            "repository ref and every file in a public Zenodo record. GitHub "
            "is compared to the local directory recursively; Zenodo is "
            "compared to a separately selectable directory's top-level "
            "regular files."
        ),
        epilog=(
            "No authentication is accepted or read. Exit status is 0 for an "
            "exact match, 1 for an identity mismatch, and 2 for an operational "
            "error. A JSON receipt is written for every run that passes CLI "
            "argument parsing."
        ),
    )
    parser.add_argument(
        "--local-release-dir",
        "--local-dir",
        dest="local_release_dir",
        required=True,
        type=Path,
        help="Local release directory containing the expected public files.",
    )
    parser.add_argument(
        "--zenodo-local-dir",
        type=Path,
        default=None,
        help=(
            "Local top-level upload projection expected on Zenodo; defaults "
            "to --local-release-dir."
        ),
    )
    parser.add_argument(
        "--github-owner",
        required=True,
        help="Public GitHub repository owner or organization.",
    )
    parser.add_argument(
        "--github-repo",
        "--github-name",
        dest="github_repo",
        required=True,
        help="Public GitHub repository name (without the owner).",
    )
    parser.add_argument(
        "--github-ref",
        required=True,
        help="Branch, tag, or commit to resolve and verify.",
    )
    parser.add_argument(
        "--zenodo-record-id",
        "--zenodo-record",
        dest="zenodo_record_id",
        required=True,
        help="Numeric public Zenodo record ID.",
    )
    parser.add_argument(
        "--output",
        "--receipt",
        dest="output",
        required=True,
        type=Path,
        help="Explicit destination for the sanitized JSON receipt.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="Per-request network timeout in seconds (default: 60).",
    )
    return parser.parse_args(argv)


def validate_args(args: argparse.Namespace) -> None:
    for label, value in (
        ("GitHub owner", args.github_owner),
        ("GitHub repository", args.github_repo),
    ):
        if not SIMPLE_GITHUB_COMPONENT.fullmatch(value):
            raise VerificationError(
                f"{label} must contain only letters, digits, '.', '_' or '-'."
            )
        if value in {".", ".."}:
            raise VerificationError(f"{label} is not valid.")
    if (
        not args.github_ref
        or len(args.github_ref) > 512
        or any(ord(char) < 32 for char in args.github_ref)
    ):
        raise VerificationError("GitHub ref is empty, too long, or contains controls.")
    if not re.fullmatch(r"[0-9]+", args.zenodo_record_id):
        raise VerificationError("Zenodo record ID must be numeric.")
    if not (0 < args.timeout <= 600):
        raise VerificationError("Timeout must be greater than 0 and at most 600 seconds.")


def _request(
    url: str,
    *,
    label: str,
    timeout: float,
    accept: str,
    attempts: int = 3,
) -> Any:
    """Open an anonymous GET request, returning a context-managed response."""

    headers = {"Accept": accept, "User-Agent": USER_AGENT}
    if url.startswith(GITHUB_API + "/"):
        headers["X-GitHub-Api-Version"] = "2022-11-28"
    for attempt in range(attempts):
        request = urllib.request.Request(url, headers=headers, method="GET")
        try:
            return urllib.request.urlopen(request, timeout=timeout)
        except urllib.error.HTTPError as exc:
            code = exc.code
            exc.close()
            if code in {429, 500, 502, 503, 504} and attempt + 1 < attempts:
                time.sleep(0.5 * (2**attempt))
                continue
            raise VerificationError(f"{label}: HTTP {code}.") from None
        except urllib.error.URLError as exc:
            if attempt + 1 < attempts:
                time.sleep(0.5 * (2**attempt))
                continue
            reason_name = type(exc.reason).__name__
            raise VerificationError(
                f"{label}: network failure ({reason_name})."
            ) from None
        except TimeoutError:
            if attempt + 1 < attempts:
                time.sleep(0.5 * (2**attempt))
                continue
            raise VerificationError(f"{label}: request timed out.") from None

    raise VerificationError(f"{label}: request failed.")


def _json_get(url: str, *, label: str, timeout: float, accept: str) -> Any:
    with _request(url, label=label, timeout=timeout, accept=accept) as response:
        payload = response.read(MAX_JSON_BYTES + 1)
    if len(payload) > MAX_JSON_BYTES:
        raise VerificationError(f"{label}: JSON response exceeds safety limit.")
    try:
        return json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise VerificationError(f"{label}: response is not valid UTF-8 JSON.") from None


def _hash_stream_url(url: str, *, label: str, timeout: float) -> tuple[int, str]:
    digest = hashlib.sha256()
    byte_count = 0
    with _request(
        url,
        label=label,
        timeout=timeout,
        accept="*/*",
    ) as response:
        while True:
            chunk = response.read(CHUNK_SIZE)
            if not chunk:
                break
            byte_count += len(chunk)
            digest.update(chunk)
    return byte_count, digest.hexdigest()


def _hash_local_file(path: Path, filename: str) -> dict[str, Any]:
    try:
        before = path.stat(follow_symlinks=False)
        digest = hashlib.sha256()
        byte_count = 0
        with path.open("rb") as handle:
            while True:
                chunk = handle.read(CHUNK_SIZE)
                if not chunk:
                    break
                byte_count += len(chunk)
                digest.update(chunk)
        after = path.stat(follow_symlinks=False)
    except OSError as exc:
        raise VerificationError(
            f"Could not read local file {filename!r} ({type(exc).__name__})."
        ) from None
    if (
        before.st_size != after.st_size
        or before.st_mtime_ns != after.st_mtime_ns
        or byte_count != after.st_size
    ):
        raise VerificationError(f"Local file changed while hashing: {filename!r}.")
    return {"filename": filename, "bytes": byte_count, "sha256": digest.hexdigest()}


def _same_path(left: Path, right: Path) -> bool:
    return os.path.normcase(os.path.abspath(left)) == os.path.normcase(
        os.path.abspath(right)
    )


def _is_windows_reparse_point(file_stat: os.stat_result) -> bool:
    attributes = getattr(file_stat, "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return bool(attributes & reparse_flag)


def _resolve_local_directory(root_arg: Path, *, label: str) -> Path:
    try:
        if root_arg.is_symlink():
            raise VerificationError(f"{label} may not be a symbolic link.")
        root = root_arg.resolve(strict=True)
    except (OSError, RuntimeError):
        raise VerificationError(f"{label} does not exist or is unreadable.") from None
    if not root.is_dir():
        raise VerificationError(f"{label} is not a directory.")
    return root


def _scan_local_directory(
    root: Path, output_arg: Path, *, recurse: bool, label: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, bool]]:
    """Hash a resolved local directory without recording its filesystem path."""

    output_path = Path(os.path.abspath(output_arg))
    recursive: list[dict[str, Any]] = []
    top_level: list[dict[str, Any]] = []
    exclusions = {"top_level_git_metadata": False, "receipt_output": False}

    def walk(directory: Path, relative_parts: tuple[str, ...]) -> None:
        try:
            with os.scandir(directory) as iterator:
                entries = sorted(iterator, key=lambda item: item.name)
        except OSError as exc:
            location = "/".join(relative_parts) or "."
            raise VerificationError(
                f"Could not enumerate local directory {location!r} "
                f"({type(exc).__name__})."
            ) from None

        for entry in entries:
            if not relative_parts and entry.name == ".git":
                exclusions["top_level_git_metadata"] = True
                continue
            path = Path(entry.path)
            rel_parts = relative_parts + (entry.name,)
            filename = PurePosixPath(*rel_parts).as_posix()
            if _same_path(path, output_path):
                exclusions["receipt_output"] = True
                continue
            try:
                entry_stat = entry.stat(follow_symlinks=False)
            except OSError as exc:
                raise VerificationError(
                    f"Could not inspect local entry {filename!r} "
                    f"({type(exc).__name__})."
                ) from None
            if stat.S_ISLNK(entry_stat.st_mode) or _is_windows_reparse_point(
                entry_stat
            ):
                raise VerificationError(
                    f"{label} contains unsupported link or reparse point "
                    f"{filename!r}."
                )
            if stat.S_ISDIR(entry_stat.st_mode):
                if recurse:
                    walk(path, rel_parts)
            elif stat.S_ISREG(entry_stat.st_mode):
                identity = _hash_local_file(path, filename)
                recursive.append(identity)
                if len(rel_parts) == 1:
                    top_level.append(identity.copy())
            else:
                raise VerificationError(
                    f"{label} contains unsupported special entry {filename!r}."
                )

    walk(root, ())
    recursive.sort(key=lambda item: item["filename"])
    top_level.sort(key=lambda item: item["filename"])
    return recursive, top_level, exclusions


def collect_local_inventories(
    github_root_arg: Path, zenodo_root_arg: Path, output_arg: Path
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, dict[str, bool]],
]:
    """Collect recursive GitHub and explicit top-level Zenodo expectations."""

    github_root = _resolve_local_directory(
        github_root_arg, label="Local release directory"
    )
    zenodo_root = _resolve_local_directory(
        zenodo_root_arg, label="Zenodo local projection directory"
    )
    github_recursive, github_top_level, github_exclusions = _scan_local_directory(
        github_root,
        output_arg,
        recurse=True,
        label="Local release directory",
    )
    if _same_path(github_root, zenodo_root):
        zenodo_top_level = [identity.copy() for identity in github_top_level]
        zenodo_exclusions = github_exclusions.copy()
    else:
        _unused_recursive, zenodo_top_level, zenodo_exclusions = (
            _scan_local_directory(
                zenodo_root,
                output_arg,
                recurse=False,
                label="Zenodo local projection directory",
            )
        )
    return github_recursive, zenodo_top_level, {
        "github_local_release": github_exclusions,
        "zenodo_local_projection": zenodo_exclusions,
    }


def _validate_remote_filename(name: Any, *, service: str) -> str:
    if not isinstance(name, str) or not name or "\x00" in name or "\\" in name:
        raise VerificationError(f"{service} returned an invalid filename.")
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise VerificationError(f"{service} returned an unsafe filename.")
    if path.as_posix() != name:
        raise VerificationError(f"{service} returned a non-canonical filename.")
    return name


def _github_json(url: str, *, label: str, timeout: float) -> Any:
    return _json_get(
        url,
        label=label,
        timeout=timeout,
        accept="application/vnd.github+json",
    )


def _parse_tree_entries(
    tree_payload: Any, *, prefix: str = ""
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    if not isinstance(tree_payload, dict) or not isinstance(tree_payload.get("tree"), list):
        raise VerificationError("GitHub tree response has an invalid structure.")
    blobs: list[dict[str, Any]] = []
    child_trees: list[dict[str, str]] = []
    for entry in tree_payload["tree"]:
        if not isinstance(entry, dict):
            raise VerificationError("GitHub tree contains an invalid entry.")
        relative_name = _validate_remote_filename(entry.get("path"), service="GitHub")
        filename = f"{prefix}/{relative_name}" if prefix else relative_name
        filename = _validate_remote_filename(filename, service="GitHub")
        entry_type = entry.get("type")
        mode = entry.get("mode")
        sha = entry.get("sha")
        if not isinstance(sha, str) or not SHA1.fullmatch(sha):
            raise VerificationError("GitHub tree contains an invalid object ID.")
        if entry_type == "blob":
            reported_size = entry.get("size")
            if reported_size is not None and (
                not isinstance(reported_size, int) or reported_size < 0
            ):
                raise VerificationError("GitHub blob has an invalid reported size.")
            blobs.append(
                {
                    "filename": filename,
                    "reported_bytes": reported_size,
                    "git_blob_sha1": sha,
                    "git_mode": mode,
                }
            )
        elif entry_type == "tree":
            child_trees.append({"filename": filename, "sha": sha})
        elif entry_type == "commit":
            raise VerificationError(
                f"GitHub tree contains unsupported submodule {filename!r}."
            )
        else:
            raise VerificationError("GitHub tree contains an unknown object type.")
    return blobs, child_trees


def enumerate_github_blobs(
    owner: str, repo: str, ref: str, timeout: float
) -> tuple[str, list[dict[str, Any]], bool]:
    owner_q = urllib.parse.quote(owner, safe="")
    repo_q = urllib.parse.quote(repo, safe="")
    ref_q = urllib.parse.quote(ref, safe="")
    commit_url = f"{GITHUB_API}/repos/{owner_q}/{repo_q}/commits/{ref_q}"
    commit = _github_json(commit_url, label="GitHub commit lookup", timeout=timeout)
    try:
        resolved_commit = commit["sha"]
        root_tree_sha = commit["commit"]["tree"]["sha"]
    except (KeyError, TypeError):
        raise VerificationError("GitHub commit response has an invalid structure.") from None
    if not isinstance(resolved_commit, str) or not SHA1.fullmatch(resolved_commit):
        raise VerificationError("GitHub returned an invalid resolved commit ID.")
    if not isinstance(root_tree_sha, str) or not SHA1.fullmatch(root_tree_sha):
        raise VerificationError("GitHub returned an invalid root tree ID.")

    recursive_url = (
        f"{GITHUB_API}/repos/{owner_q}/{repo_q}/git/trees/"
        f"{root_tree_sha}?recursive=1"
    )
    recursive_payload = _github_json(
        recursive_url, label="GitHub recursive tree", timeout=timeout
    )
    if not isinstance(recursive_payload, dict):
        raise VerificationError("GitHub tree response has an invalid structure.")
    was_truncated = recursive_payload.get("truncated") is True
    if not was_truncated:
        blobs, _child_trees = _parse_tree_entries(recursive_payload)
    else:
        blobs = []
        pending: list[tuple[str, str]] = [(root_tree_sha, "")]
        visited_nodes = 0
        while pending:
            tree_sha, prefix = pending.pop()
            visited_nodes += 1
            if visited_nodes > 1_000_000:
                raise VerificationError("GitHub tree exceeds verifier traversal limit.")
            tree_url = (
                f"{GITHUB_API}/repos/{owner_q}/{repo_q}/git/trees/{tree_sha}"
            )
            payload = _github_json(
                tree_url, label="GitHub tree traversal", timeout=timeout
            )
            node_blobs, child_trees = _parse_tree_entries(payload, prefix=prefix)
            blobs.extend(node_blobs)
            for child in reversed(child_trees):
                pending.append((child["sha"], child["filename"]))

    names = [entry["filename"] for entry in blobs]
    if len(names) != len(set(names)):
        raise VerificationError("GitHub tree returned duplicate filenames.")
    blobs.sort(key=lambda item: item["filename"])
    return resolved_commit, blobs, was_truncated


def download_github_commit_archive(
    owner: str, repo: str, commit: str, timeout: float
) -> list[dict[str, Any]]:
    """Download a public codeload ZIP and hash every Git-controlled file."""

    if not SHA1.fullmatch(commit):
        raise VerificationError("GitHub codeload fallback requires an exact commit ID.")
    owner_q = urllib.parse.quote(owner, safe="")
    repo_q = urllib.parse.quote(repo, safe="")
    commit_q = urllib.parse.quote(commit, safe="")
    url = f"{GITHUB_CODELOAD}/{owner_q}/{repo_q}/zip/{commit_q}"
    with _request(
        url,
        label="GitHub public commit archive",
        timeout=timeout,
        accept="application/zip,*/*;q=0.8",
    ) as response:
        payload = response.read(256 * 1024 * 1024 + 1)
    if len(payload) > 256 * 1024 * 1024:
        raise VerificationError("GitHub public commit archive exceeds safety limit.")

    inventory: list[dict[str, Any]] = []
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            if archive.testzip() is not None:
                raise VerificationError("GitHub public commit archive failed CRC validation.")
            for info in archive.infolist():
                if info.is_dir():
                    continue
                mode = (info.external_attr >> 16) & 0o170000
                if mode not in {0, stat.S_IFREG}:
                    raise VerificationError(
                        "GitHub public commit archive contains a non-regular entry."
                    )
                parts = PurePosixPath(info.filename).parts
                if len(parts) < 2:
                    raise VerificationError("GitHub commit archive has an invalid root entry.")
                filename = PurePosixPath(*parts[1:]).as_posix()
                filename = _validate_remote_filename(filename, service="GitHub")
                data = archive.read(info)
                if len(data) != info.file_size:
                    raise VerificationError(
                        f"GitHub archive size mismatch for {filename!r}."
                    )
                inventory.append(
                    {
                        "filename": filename,
                        "bytes": len(data),
                        "sha256": hashlib.sha256(data).hexdigest(),
                    }
                )
    except zipfile.BadZipFile:
        raise VerificationError("GitHub public commit archive is not a valid ZIP.") from None
    names = [item["filename"] for item in inventory]
    if len(names) != len(set(names)):
        raise VerificationError("GitHub public commit archive contains duplicate filenames.")
    inventory.sort(key=lambda item: item["filename"])
    return inventory


def verify_github(
    owner: str,
    repo: str,
    ref: str,
    expected: list[dict[str, Any]],
    timeout: float,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "repository": f"{owner}/{repo}",
        "requested_ref": ref,
        "resolved_commit": None,
        "scope": "all Git blobs recursively at the resolved commit",
        "enumerated_files": 0,
        "downloaded_files": 0,
        "total_downloaded_bytes": 0,
        "recursive_api_response_was_truncated": None,
        "transport": "github_api_plus_raw_blobs",
        "transport_note": None,
        "inventory": [],
        "metadata_mismatches": [],
        "operational_errors": [],
        "comparison": None,
    }
    try:
        resolved_commit, blobs, was_truncated = enumerate_github_blobs(
            owner, repo, ref, timeout
        )
        result["resolved_commit"] = resolved_commit
        result["recursive_api_response_was_truncated"] = was_truncated
        result["enumerated_files"] = len(blobs)
    except VerificationError as exc:
        try:
            inventory = download_github_commit_archive(owner, repo, ref, timeout)
        except VerificationError as fallback_exc:
            result["operational_errors"].extend([str(exc), str(fallback_exc)])
            return result
        result["resolved_commit"] = ref
        result["transport"] = "anonymous_github_codeload_commit_zip"
        result["transport_note"] = (
            "The unauthenticated GitHub metadata API was unavailable; the verifier "
            "downloaded the exact public commit archive instead."
        )
        result["enumerated_files"] = len(inventory)
        result["downloaded_files"] = len(inventory)
        result["total_downloaded_bytes"] = sum(
            item["bytes"] for item in inventory
        )
        result["inventory"] = inventory
        result["comparison"] = compare_inventories(expected, inventory)
        return result

    owner_q = urllib.parse.quote(owner, safe="")
    repo_q = urllib.parse.quote(repo, safe="")
    for blob in blobs:
        filename = blob["filename"]
        path_q = urllib.parse.quote(filename, safe="/")
        url = (
            f"{GITHUB_RAW}/{owner_q}/{repo_q}/"
            f"{result['resolved_commit']}/{path_q}"
        )
        try:
            byte_count, sha256 = _hash_stream_url(
                url,
                label=f"GitHub blob download for {filename!r}",
                timeout=timeout,
            )
        except VerificationError as exc:
            result["operational_errors"].append(str(exc))
            continue
        identity = {"filename": filename, "bytes": byte_count, "sha256": sha256}
        result["inventory"].append(identity)
        reported = blob["reported_bytes"]
        if reported is not None and reported != byte_count:
            result["metadata_mismatches"].append(
                {
                    "filename": filename,
                    "reported_bytes": reported,
                    "downloaded_bytes": byte_count,
                }
            )

    result["inventory"].sort(key=lambda item: item["filename"])
    result["downloaded_files"] = len(result["inventory"])
    result["total_downloaded_bytes"] = sum(
        item["bytes"] for item in result["inventory"]
    )
    result["comparison"] = compare_inventories(expected, result["inventory"])
    return result


def _validate_zenodo_download_url(url: Any) -> str:
    if not isinstance(url, str):
        raise VerificationError("Zenodo file is missing a download URL.")
    parsed = urllib.parse.urlsplit(url)
    hostname = (parsed.hostname or "").lower()
    if (
        parsed.scheme != "https"
        or parsed.username is not None
        or parsed.password is not None
        or not (hostname == "zenodo.org" or hostname.endswith(".zenodo.org"))
    ):
        raise VerificationError("Zenodo returned a non-public or invalid download URL.")
    return url


def enumerate_zenodo_files(
    record_id: str, timeout: float
) -> tuple[str, list[dict[str, Any]]]:
    url = f"{ZENODO_API}/records/{record_id}"
    record = _json_get(
        url,
        label="Zenodo record lookup",
        timeout=timeout,
        accept="application/json",
    )
    if not isinstance(record, dict) or not isinstance(record.get("files"), list):
        raise VerificationError("Zenodo record response has an invalid structure.")
    resolved_id_raw = record.get("id", record_id)
    resolved_id = str(resolved_id_raw)
    if not re.fullmatch(r"[0-9]+", resolved_id):
        raise VerificationError("Zenodo returned an invalid resolved record ID.")

    files: list[dict[str, Any]] = []
    for entry in record["files"]:
        if not isinstance(entry, dict):
            raise VerificationError("Zenodo record contains an invalid file entry.")
        filename = _validate_remote_filename(entry.get("key"), service="Zenodo")
        reported_size = entry.get("size")
        if reported_size is not None and (
            not isinstance(reported_size, int) or reported_size < 0
        ):
            raise VerificationError("Zenodo file has an invalid reported size.")
        links = entry.get("links")
        if not isinstance(links, dict):
            raise VerificationError("Zenodo file is missing public links.")
        download_url = links.get("content") or links.get("self") or links.get("download")
        download_url = _validate_zenodo_download_url(download_url)
        files.append(
            {
                "filename": filename,
                "reported_bytes": reported_size,
                "download_url": download_url,
            }
        )
    names = [entry["filename"] for entry in files]
    if len(names) != len(set(names)):
        raise VerificationError("Zenodo record returned duplicate filenames.")
    files.sort(key=lambda item: item["filename"])
    return resolved_id, files


def verify_zenodo(
    record_id: str, expected: list[dict[str, Any]], timeout: float
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "requested_record_id": record_id,
        "resolved_record_id": None,
        "scope": "all public record files compared to local top-level regular files",
        "enumerated_files": 0,
        "downloaded_files": 0,
        "total_downloaded_bytes": 0,
        "inventory": [],
        "metadata_mismatches": [],
        "operational_errors": [],
        "comparison": None,
    }
    try:
        resolved_id, files = enumerate_zenodo_files(record_id, timeout)
        result["resolved_record_id"] = resolved_id
        result["enumerated_files"] = len(files)
    except VerificationError as exc:
        result["operational_errors"].append(str(exc))
        return result

    for remote_file in files:
        filename = remote_file["filename"]
        try:
            byte_count, sha256 = _hash_stream_url(
                remote_file["download_url"],
                label=f"Zenodo file download for {filename!r}",
                timeout=timeout,
            )
        except VerificationError as exc:
            result["operational_errors"].append(str(exc))
            continue
        identity = {"filename": filename, "bytes": byte_count, "sha256": sha256}
        result["inventory"].append(identity)
        reported = remote_file["reported_bytes"]
        if reported is not None and reported != byte_count:
            result["metadata_mismatches"].append(
                {
                    "filename": filename,
                    "reported_bytes": reported,
                    "downloaded_bytes": byte_count,
                }
            )

    result["inventory"].sort(key=lambda item: item["filename"])
    result["downloaded_files"] = len(result["inventory"])
    result["total_downloaded_bytes"] = sum(
        item["bytes"] for item in result["inventory"]
    )
    result["comparison"] = compare_inventories(expected, result["inventory"])
    return result


def _identity_map(inventory: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for identity in inventory:
        filename = identity["filename"]
        if filename in result:
            raise VerificationError(f"Duplicate inventory filename {filename!r}.")
        result[filename] = identity
    return result


def compare_inventories(
    expected: list[dict[str, Any]], observed: list[dict[str, Any]]
) -> dict[str, Any]:
    expected_map = _identity_map(expected)
    observed_map = _identity_map(observed)
    expected_names = set(expected_map)
    observed_names = set(observed_map)
    missing = sorted(expected_names - observed_names)
    unexpected = sorted(observed_names - expected_names)
    mismatched: list[dict[str, Any]] = []
    matched_files = 0
    for filename in sorted(expected_names & observed_names):
        wanted = expected_map[filename]
        found = observed_map[filename]
        differing_fields = [
            field
            for field in ("bytes", "sha256")
            if wanted[field] != found[field]
        ]
        if differing_fields:
            mismatched.append(
                {
                    "filename": filename,
                    "differing_fields": differing_fields,
                    "expected": {
                        "bytes": wanted["bytes"],
                        "sha256": wanted["sha256"],
                    },
                    "observed": {
                        "bytes": found["bytes"],
                        "sha256": found["sha256"],
                    },
                }
            )
        else:
            matched_files += 1
    exact = not missing and not unexpected and not mismatched
    return {
        "exact_match": exact,
        "expected_files": len(expected),
        "observed_files": len(observed),
        "matched_files": matched_files,
        "missing_remote_files": missing,
        "unexpected_remote_files": unexpected,
        "identity_mismatches": mismatched,
    }


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def _write_receipt(output: Path, receipt: dict[str, Any]) -> None:
    try:
        parent = output.parent if output.parent != Path("") else Path(".")
        parent.mkdir(parents=True, exist_ok=True)
        fd, temporary_name = tempfile.mkstemp(
            prefix=f".{output.name}.", suffix=".tmp", dir=parent
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                json.dump(receipt, handle, ensure_ascii=False, indent=2, sort_keys=True)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_name, output)
        except BaseException:
            try:
                os.unlink(temporary_name)
            except OSError:
                pass
            raise
    except OSError as exc:
        raise VerificationError(
            f"Could not write receipt ({type(exc).__name__})."
        ) from None


def _base_receipt(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "generated_at_utc": _utc_now(),
        "status": "error",
        "anonymous_readback": True,
        "hash_algorithm": "sha256",
        "credential_sources_used": [],
        "local": {
            "path_recorded": False,
            "github_expected_scope": "recursive regular files",
            "zenodo_expected_scope": (
                "top-level regular files from the Zenodo upload projection"
            ),
            "separate_zenodo_projection": args.zenodo_local_dir is not None,
            "github_expected_inventory": [],
            "zenodo_expected_inventory": [],
            "exclusions": {
                "github_local_release": {
                    "top_level_git_metadata": False,
                    "receipt_output": False,
                },
                "zenodo_local_projection": {
                    "top_level_git_metadata": False,
                    "receipt_output": False,
                },
            },
        },
        "github": {
            "repository": f"{args.github_owner}/{args.github_repo}",
            "requested_ref": args.github_ref,
        },
        "zenodo": {"requested_record_id": args.zenodo_record_id},
        "errors": [],
    }


def execute(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    receipt = _base_receipt(args)
    try:
        validate_args(args)
        zenodo_local_dir = args.zenodo_local_dir or args.local_release_dir
        github_expected, zenodo_expected, exclusions = collect_local_inventories(
            args.local_release_dir, zenodo_local_dir, args.output
        )
    except VerificationError as exc:
        receipt["errors"].append(str(exc))
        return receipt, 2

    receipt["local"]["github_expected_inventory"] = github_expected
    receipt["local"]["zenodo_expected_inventory"] = zenodo_expected
    receipt["local"]["exclusions"] = exclusions

    github = verify_github(
        args.github_owner,
        args.github_repo,
        args.github_ref,
        github_expected,
        args.timeout,
    )
    zenodo = verify_zenodo(args.zenodo_record_id, zenodo_expected, args.timeout)
    receipt["github"] = github
    receipt["zenodo"] = zenodo

    operational_errors = list(github["operational_errors"]) + list(
        zenodo["operational_errors"]
    )
    receipt["errors"].extend(operational_errors)
    if operational_errors:
        receipt["status"] = "error"
        return receipt, 2

    integrity_failure = bool(
        github["metadata_mismatches"]
        or zenodo["metadata_mismatches"]
        or not github["comparison"]["exact_match"]
        or not zenodo["comparison"]["exact_match"]
    )
    if integrity_failure:
        receipt["status"] = "fail"
        return receipt, 1

    receipt["status"] = "pass"
    return receipt, 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    receipt, exit_code = execute(args)
    receipt["completed_at_utc"] = _utc_now()
    try:
        _write_receipt(args.output, receipt)
    except VerificationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if exit_code == 0:
        print("PASS: public GitHub and Zenodo bytes exactly match local expectations.")
    elif exit_code == 1:
        print("FAIL: public bytes differ from local expectations.", file=sys.stderr)
    else:
        print("ERROR: verification was incomplete; inspect the receipt.", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
