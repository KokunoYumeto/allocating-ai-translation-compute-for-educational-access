#!/usr/bin/env python3
"""Publish a preservation-safe Zenodo v1.1 successor to record 22172596.

The default ``preflight`` action is anonymous and read-only.  Both mutating
actions additionally require ``--execute`` and read a credential only after all
available public/local gates pass:

* ``reserve`` creates one same-concept new-version draft, verifies its inherited
  v1.0 inventory, records the reserved version DOI, and stops.
* ``publish`` resumes only that transaction-owned draft, reconciles its files to
  an explicit 14-file v1.1 upload projection, verifies the exact draft, updates
  v1.1 metadata, publishes, and anonymously hash-reads every public file.

The script never calls ``actions/edit`` on v1.0, never deletes a public record,
never changes access away from open, and never prints or persists credentials.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile
import time
from typing import Any
import urllib.error
import urllib.parse
import urllib.request

import build_standalone_release_v1_1 as release_tools


ROOT = Path(__file__).resolve().parents[1]
ZENODO = "https://zenodo.org"
API = f"{ZENODO}/api"
PREDECESSOR_RECORD_ID = 22172596
CONCEPT_RECORD_ID = 22172595
PREDECESSOR_DOI = "10.5281/zenodo.22172596"
CONCEPT_DOI = "10.5281/zenodo.22172595"
SUCCESSOR_VERSION = "1.1.0"
FROZEN_UPLOAD_DIR = ROOT / "staging" / "zenodo_upload_20260830"
USER_AGENT = "standalone-v1.1-zenodo-publisher/1.0"
MAX_RESPONSE = 256 * 1024 * 1024
SAFE_FILE = re.compile(r"^[^/\\\x00]+$")


class GateError(RuntimeError):
    """A sanitized, fail-closed transaction error."""


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().lower()


def md5_file(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().lower()


def identity(path: Path, name: str | None = None) -> dict[str, Any]:
    return {
        "filename": name or path.name,
        "bytes": path.stat().st_size,
        "md5": md5_file(path),
        "sha256": sha256_file(path),
    }


def public_identity(row: dict[str, Any]) -> dict[str, Any]:
    return {key: row[key] for key in ("filename", "bytes", "sha256")}


def inventory_digest(rows: list[dict[str, Any]]) -> str:
    canonical = json.dumps(
        [public_identity(row) for row in rows],
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


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


def validate_filename(name: str) -> str:
    if not SAFE_FILE.fullmatch(name) or PurePosixPath(name).name != name or name in {".", ".."}:
        raise GateError("Zenodo inventory contains an unsafe filename")
    return name


def local_inventory(directory: Path, expected_count: int | None = 14) -> list[dict[str, Any]]:
    directory = task_path(directory, "upload projection")
    if not directory.is_dir():
        raise GateError(f"upload projection is missing: {directory.name}")
    rows: list[dict[str, Any]] = []
    for path in sorted(directory.iterdir()):
        if path.is_symlink():
            raise GateError(f"upload projection contains a symlink: {path.name}")
        if not path.is_file():
            raise GateError("Zenodo upload projection must contain only top-level regular files")
        name = validate_filename(path.name)
        rows.append(identity(path, name))
    if expected_count is not None and len(rows) != expected_count:
        raise GateError(f"Zenodo upload projection must contain exactly {expected_count} files, observed {len(rows)}")
    return rows


def read_limited(response) -> bytes:
    payload = response.read(MAX_RESPONSE + 1)
    if len(payload) > MAX_RESPONSE:
        raise GateError("Zenodo response exceeded the bounded size limit")
    return payload


def request_bytes(
    method: str,
    url: str,
    *,
    token: str | None = None,
    payload: Any | None = None,
    raw: bytes | None = None,
    content_type: str | None = None,
    expected: tuple[int, ...] = (200,),
    timeout: int = 180,
) -> tuple[int, bytes, dict[str, str]]:
    parsed = urllib.parse.urlsplit(url)
    hostname = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not (hostname == "zenodo.org" or hostname.endswith(".zenodo.org")):
        raise GateError("refusing an unexpected Zenodo transport host")
    body = raw
    if payload is not None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        content_type = "application/json"
    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if content_type:
        headers["Content-Type"] = content_type
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response_host = (urllib.parse.urlsplit(response.geturl()).hostname or "").lower()
            if not (response_host == "zenodo.org" or response_host.endswith(".zenodo.org")):
                raise GateError("Zenodo redirected to an unexpected host")
            data = read_limited(response)
            if response.status not in expected:
                raise GateError(f"Zenodo returned unexpected HTTP {response.status}")
            return response.status, data, dict(response.headers.items())
    except urllib.error.HTTPError as exc:
        raise GateError(f"Zenodo {method} request failed with HTTP {exc.code}") from None
    except urllib.error.URLError as exc:
        raise GateError(f"Zenodo transport failed ({type(exc.reason).__name__})") from None


def request_json(
    method: str,
    url: str,
    *,
    token: str | None = None,
    payload: Any | None = None,
    expected: tuple[int, ...] = (200,),
    timeout: int = 180,
) -> Any:
    _, raw, _ = request_bytes(
        method, url, token=token, payload=payload, expected=expected, timeout=timeout,
    )
    try:
        return json.loads(raw.decode("utf-8")) if raw else None
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GateError("Zenodo returned invalid JSON") from exc


def row_name(row: dict[str, Any]) -> str:
    return validate_filename(str(row.get("key") or row.get("filename") or ""))


def row_size(row: dict[str, Any]) -> int:
    value = row.get("size", row.get("filesize"))
    try:
        size = int(value)
    except (TypeError, ValueError) as exc:
        raise GateError("Zenodo returned an invalid file size") from exc
    if size < 0:
        raise GateError("Zenodo returned a negative file size")
    return size


def row_md5(row: dict[str, Any]) -> str:
    checksum = str(row.get("checksum") or "").lower().removeprefix("md5:")
    if not re.fullmatch(r"[0-9a-f]{32}", checksum):
        raise GateError("Zenodo returned an invalid MD5 checksum")
    return checksum


def file_rows(record: dict[str, Any]) -> list[dict[str, Any]]:
    rows = record.get("files")
    if isinstance(rows, dict):
        rows = rows.get("entries")
        if isinstance(rows, dict):
            rows = [dict(value, key=key) for key, value in rows.items()]
    if not isinstance(rows, list):
        raise GateError("Zenodo record has an invalid file list")
    return rows


def public_record(record_id: int) -> dict[str, Any]:
    value = request_json("GET", f"{API}/records/{record_id}")
    if not isinstance(value, dict) or int(value.get("id", -1)) != record_id:
        raise GateError("Zenodo public record response is invalid")
    return value


def file_content_url(record_id: int, row: dict[str, Any]) -> str:
    links = row.get("links") or {}
    url = links.get("content") or links.get("download") or links.get("self")
    if not isinstance(url, str) or not url:
        url = f"{API}/records/{record_id}/files/{urllib.parse.quote(row_name(row), safe='')}/content"
    return url


def public_inventory(record_id: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    record = public_record(record_id)
    rows: list[dict[str, Any]] = []
    for remote in file_rows(record):
        name = row_name(remote)
        _, data, _ = request_bytes(
            "GET", file_content_url(record_id, remote),
            expected=(200,), timeout=900,
        )
        if len(data) != row_size(remote):
            raise GateError(f"Zenodo public byte count disagrees for {name}")
        if hashlib.md5(data).hexdigest().lower() != row_md5(remote):
            raise GateError(f"Zenodo public MD5 metadata disagrees for {name}")
        rows.append({
            "filename": name,
            "bytes": len(data),
            "md5": hashlib.md5(data).hexdigest().lower(),
            "sha256": hashlib.sha256(data).hexdigest().lower(),
        })
    rows.sort(key=lambda row: row["filename"])
    return record, rows


def concept_id(record: dict[str, Any]) -> str:
    return str(record.get("conceptrecid") or (record.get("parent") or {}).get("id") or "")


def record_doi(record: dict[str, Any]) -> str:
    return str(
        ((record.get("pids") or {}).get("doi") or {}).get("identifier")
        or record.get("doi")
        or (record.get("metadata") or {}).get("doi")
        or ""
    )


def baseline_gate() -> dict[str, Any]:
    local = local_inventory(FROZEN_UPLOAD_DIR, expected_count=None)
    record, remote = public_inventory(PREDECESSOR_RECORD_ID)
    if sorted((public_identity(row) for row in remote), key=lambda row: row["filename"]) != sorted(
        (public_identity(row) for row in local), key=lambda row: row["filename"]
    ):
        raise GateError("public v1.0 Zenodo bytes differ from the frozen upload projection")
    if concept_id(record) != str(CONCEPT_RECORD_ID):
        raise GateError("v1.0 Zenodo record is no longer in the expected concept")
    if record_doi(record) != PREDECESSOR_DOI:
        raise GateError("v1.0 Zenodo record DOI changed unexpectedly")
    metadata = record.get("metadata") or {}
    access = str(metadata.get("access_right") or (record.get("access") or {}).get("status") or "").lower()
    if access not in {"open", "open access"}:
        raise GateError("v1.0 Zenodo record is not open access")
    return {
        "record_id": PREDECESSOR_RECORD_ID,
        "version_doi": PREDECESSOR_DOI,
        "concept_record_id": CONCEPT_RECORD_ID,
        "concept_doi": CONCEPT_DOI,
        "file_count": len(remote),
        "total_bytes": sum(row["bytes"] for row in remote),
        "inventory_sha256": inventory_digest(remote),
        "files": remote,
    }


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GateError(f"cannot read {label}") from exc
    if not isinstance(value, dict):
        raise GateError(f"{label} must be a JSON object")
    return value


def qa_gate(path: Path) -> dict[str, Any]:
    value = load_json(path, "v1.1 QA receipt")
    if value.get("schema") != "research-paper-final-document-qa/1.1":
        raise GateError("v1.1 QA receipt has an unexpected schema")
    if value.get("status") != "PASS" or value.get("release_version") != SUCCESSOR_VERSION:
        raise GateError("v1.1 QA receipt must declare release_version 1.1.0 and status PASS")
    try:
        checked = release_tools.validate_qa(path.parent)
    except release_tools.GateError as exc:
        raise GateError(f"v1.1 QA does not bind current release inputs: {exc}") from exc
    return {"filename": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path), "bound_artifacts": checked}


def privacy_gate(directory: Path) -> None:
    patterns = (
        re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+", re.I),
        re.compile(r"(?:github_pat_|ghp_)[A-Za-z0-9_]+", re.I),
        re.compile(r"Authorization\s*:\s*Bearer\s+\S+", re.I),
        re.compile(r"access_token\s*[=:]\s*[^\s\"']+", re.I),
    )
    binary = {".docx", ".pdf", ".zip"}
    for path in sorted(directory.iterdir()):
        if path.suffix.lower() in binary:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise GateError(f"non-UTF-8 public text file: {path.name}") from exc
        if any(pattern.search(text) for pattern in patterns):
            raise GateError(f"public projection privacy scan failed: {path.name}")


def metadata_gate(metadata_path: Path, upload_dir: Path, reserved_doi: str) -> dict[str, Any]:
    wrapper = load_json(metadata_path, "v1.1 Zenodo metadata")
    metadata = wrapper.get("metadata")
    if not isinstance(metadata, dict):
        raise GateError("Zenodo metadata file must contain a metadata object")
    if str(metadata.get("version")) != SUCCESSOR_VERSION:
        raise GateError("Zenodo metadata version is not 1.1.0")
    if str(metadata.get("access_right", "")).lower() != "open":
        raise GateError("Zenodo metadata access_right must remain open")
    if not re.fullmatch(r"10\.5281/zenodo\.[0-9]+", reserved_doi):
        raise GateError("transaction state lacks a concrete reserved v1.1 DOI")
    if reserved_doi in {PREDECESSOR_DOI, CONCEPT_DOI}:
        raise GateError("reserved v1.1 DOI collides with v1.0 or the concept DOI")
    texts = [json.dumps(wrapper, ensure_ascii=False)]
    for name in ("CITATION.cff", "README.md", "PROVENANCE.md"):
        path = upload_dir / name
        if not path.is_file():
            raise GateError(f"Zenodo upload projection is missing {name}")
        texts.append(path.read_text(encoding="utf-8"))
    if any(reserved_doi not in text for text in texts):
        raise GateError("reserved v1.1 DOI is not embedded in every controlling metadata file")
    return wrapper


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = load_json(path, "Zenodo transaction state")
    if value.get("schema") != "standalone-zenodo-v1.1-transaction/1.0":
        raise GateError("Zenodo transaction state has an unexpected schema")
    if int(value.get("predecessor_record_id", -1)) != PREDECESSOR_RECORD_ID:
        raise GateError("Zenodo transaction state has the wrong predecessor")
    if int(value.get("concept_record_id", -1)) != CONCEPT_RECORD_ID:
        raise GateError("Zenodo transaction state has the wrong concept")
    return value


def load_token(path: Path) -> str:
    try:
        content = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise GateError("could not read the execution credential file") from exc
    patterns = (
        r"(?i)(?:access[_ -]?token|zenodo[_ -]?token|token)\s*(?:is|:|=)\s*[`'\"]?([A-Za-z0-9._-]{30,})",
        r"\b([A-Fa-f0-9]{64})\b",
        r"`([A-Za-z0-9._-]{40,})`",
    )
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            return match.group(1)
    candidates = re.findall(r"\b[A-Za-z0-9._-]{40,}\b", content)
    candidates = [value for value in candidates if any(character.isdigit() for character in value)]
    if len(candidates) != 1:
        raise GateError("credential file does not contain exactly one recognizable token")
    return candidates[0]


def deposit(token: str, draft_id: int) -> dict[str, Any]:
    value = request_json("GET", f"{API}/deposit/depositions/{draft_id}", token=token)
    if not isinstance(value, dict) or int(value.get("id", -1)) != draft_id:
        raise GateError("Zenodo draft response is invalid")
    return value


def deposit_inventory(draft: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in file_rows(draft):
        name = row_name(row)
        if name in result:
            raise GateError("Zenodo draft contains duplicate filenames")
        result[name] = {
            "bytes": row_size(row),
            "md5": row_md5(row),
            "id": row.get("id"),
            "links": row.get("links") or {},
        }
    return dict(sorted(result.items()))


def lineage_drafts(token: str) -> list[dict[str, Any]]:
    rows = request_json(
        "GET", f"{API}/deposit/depositions?status=draft&size=100", token=token,
    )
    if not isinstance(rows, list):
        raise GateError("Zenodo draft listing is invalid")
    return [
        row for row in rows
        if not bool(row.get("submitted"))
        if str(row.get("conceptrecid") or row.get("concept_record_id") or "") == str(CONCEPT_RECORD_ID)
    ]


def authenticated_draft_gate(token: str, state: dict[str, Any], *, allow_create: bool) -> dict[str, Any] | None:
    drafts = lineage_drafts(token)
    owned_id = int(state["draft_id"]) if state.get("draft_id") else None
    foreign = [row for row in drafts if int(row.get("id", -1)) != owned_id]
    if foreign:
        if owned_id is None and allow_create and state.get("reserve_attempted_at_utc") and len(foreign) == 1:
            # A timed-out newversion POST can create exactly one discoverable
            # draft before its response reaches us.  Return that one candidate;
            # reserve() adopts it only after its inherited bytes match v1.0.
            return foreign[0]
        raise GateError("a same-concept draft exists without this transaction's ownership")
    if owned_id is None:
        if drafts:
            raise GateError("an unowned same-concept draft already exists")
        return None
    try:
        owned = deposit(token, owned_id)
    except GateError:
        if allow_create:
            raise
        raise
    if bool(owned.get("submitted")) and not state.get("published_record_id") and not state.get("publish_attempted_at_utc"):
        raise GateError("transaction-owned draft is submitted without a recorded public successor")
    return owned


def wait_for_inventory(token: str, draft_id: int, expected: dict[str, dict[str, Any]], label: str) -> dict[str, Any]:
    for delay in (0, 5, 20):
        if delay:
            time.sleep(delay)
        current = deposit(token, draft_id)
        observed = {
            name: {"bytes": row["bytes"], "md5": row["md5"]}
            for name, row in deposit_inventory(current).items()
        }
        if observed == expected:
            return current
    raise GateError(f"Zenodo draft did not settle to the exact {label} inventory")


def reserve(token: str, state: dict[str, Any], baseline: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    owned = authenticated_draft_gate(token, state, allow_create=True)
    if owned is not None and not state.get("draft_id"):
        expected = {row["filename"]: {"bytes": row["bytes"], "md5": row["md5"]} for row in baseline["files"]}
        observed = {
            name: {"bytes": row["bytes"], "md5": row["md5"]}
            for name, row in deposit_inventory(owned).items()
        }
        if observed != expected:
            raise GateError("uncertain new-version draft does not exactly inherit the frozen predecessor")
        state.update({
            "schema": "standalone-zenodo-v1.1-transaction/1.0",
            "predecessor_record_id": PREDECESSOR_RECORD_ID,
            "concept_record_id": CONCEPT_RECORD_ID,
            "predecessor_inventory_sha256": baseline["inventory_sha256"],
            "draft_id": int(owned.get("id", -1)),
            "status": "uncertain_newversion_reconciled_to_unique_exact_draft",
            "updated_at_utc": utc_now(),
            "credential_material_persisted": False,
        })
        atomic_json(args.state, state)
    if owned is None:
        # Persist the intent before transport. An uncertain creation must be
        # reconciled against a discoverable draft, never submitted again blindly.
        if state.get("reserve_attempted_at_utc"):
            raise GateError("prior new-version creation has an uncertain result; resolve that exact attempt before any new POST")
        state.update({
            "schema": "standalone-zenodo-v1.1-transaction/1.0",
            "predecessor_record_id": PREDECESSOR_RECORD_ID, "concept_record_id": CONCEPT_RECORD_ID,
            "predecessor_inventory_sha256": baseline["inventory_sha256"],
            "reserve_attempted_at_utc": utc_now(), "credential_material_persisted": False,
        })
        atomic_json(args.state, state)
        response = request_json(
            "POST",
            f"{API}/deposit/depositions/{PREDECESSOR_RECORD_ID}/actions/newversion",
            token=token,
            payload={},
            expected=(200, 201, 202),
        )
        latest = str(((response or {}).get("links") or {}).get("latest_draft") or "")
        if not latest:
            raise GateError("new-version response did not expose latest_draft")
        owned = request_json("GET", latest, token=token)
        if not isinstance(owned, dict):
            raise GateError("new-version draft response is invalid")
        draft_id = int(owned.get("id", -1))
        state.update({
            "schema": "standalone-zenodo-v1.1-transaction/1.0",
            "predecessor_record_id": PREDECESSOR_RECORD_ID,
            "concept_record_id": CONCEPT_RECORD_ID,
            "predecessor_inventory_sha256": baseline["inventory_sha256"],
            "draft_id": draft_id,
            "status": "draft_created",
            "created_at_utc": utc_now(),
            "credential_material_persisted": False,
        })
        atomic_json(args.state, state)
    draft_id = int(state["draft_id"])
    if not state.get("reserved_doi"):
        expected = {row["filename"]: {"bytes": row["bytes"], "md5": row["md5"]} for row in baseline["files"]}
        owned = wait_for_inventory(token, draft_id, expected, "inherited complete predecessor")
    if str(owned.get("conceptrecid") or owned.get("concept_record_id") or "") != str(CONCEPT_RECORD_ID):
        raise GateError("reserved draft is outside the standalone concept lineage")
    metadata = owned.get("metadata") or {}
    reserved_doi = str((metadata.get("prereserve_doi") or {}).get("doi") or state.get("reserved_doi") or "")
    if not re.fullmatch(r"10\.5281/zenodo\.[0-9]+", reserved_doi):
        raise GateError("Zenodo draft did not expose a concrete reserved DOI")
    if reserved_doi in {PREDECESSOR_DOI, CONCEPT_DOI}:
        raise GateError("Zenodo reserved DOI collides with v1.0 or the concept DOI")
    state.update({
        "reserved_doi": reserved_doi,
        "status": "doi_reserved_and_inherited_v1_verified",
        "updated_at_utc": utc_now(),
    })
    atomic_json(args.state, state)
    return {
        "schema": "standalone-zenodo-v1.1-reservation-receipt/1.0",
        "status": "DOI_RESERVED_DRAFT_NOT_PUBLISHED",
        "draft_id": draft_id,
        "reserved_doi": reserved_doi,
        "concept_record_id": CONCEPT_RECORD_ID,
        "public_mutation": False,
        "credential_material_persisted": False,
    }


def delete_draft_file(token: str, draft_id: int, row: dict[str, Any]) -> None:
    url = str((row.get("links") or {}).get("self") or "")
    if not url:
        if row.get("id") is None:
            raise GateError("Zenodo draft file lacks a deletion identifier")
        url = f"{API}/deposit/depositions/{draft_id}/files/{row['id']}"
    request_bytes("DELETE", url, token=token, expected=(204,))


def upload_file(token: str, bucket: str, path: Path) -> None:
    name = validate_filename(path.name)
    url = bucket.rstrip("/") + "/" + urllib.parse.quote(name, safe="")
    request_bytes(
        "PUT", url, token=token, raw=path.read_bytes(),
        content_type="application/octet-stream", expected=(200, 201), timeout=900,
    )


def reconcile_files(token: str, draft: dict[str, Any], desired_rows: list[dict[str, Any]]) -> dict[str, Any]:
    draft_id = int(draft["id"])
    desired = {row["filename"]: row for row in desired_rows}
    current_rows = {row_name(row): row for row in file_rows(draft)}
    for name, row in current_rows.items():
        wanted = desired.get(name)
        observed = {"bytes": row_size(row), "md5": row_md5(row)}
        if wanted is None or observed != {"bytes": wanted["bytes"], "md5": wanted["md5"]}:
            delete_draft_file(token, draft_id, row)
    draft = deposit(token, draft_id)
    after_delete = deposit_inventory(draft)
    bucket = str((draft.get("links") or {}).get("bucket") or "")
    if not bucket:
        raise GateError("Zenodo draft does not expose a bucket URL")
    for name, wanted in desired.items():
        retained = after_delete.get(name)
        if retained and {"bytes": retained["bytes"], "md5": retained["md5"]} == {"bytes": wanted["bytes"], "md5": wanted["md5"]}:
            continue
        upload_file(token, bucket, args_upload_path(draft, name))
    expected = {name: {"bytes": row["bytes"], "md5": row["md5"]} for name, row in desired.items()}
    return wait_for_inventory(token, draft_id, expected, "v1.1 upload")


def set_pdf_default_preview(token: str, draft: dict[str, Any]) -> dict[str, Any]:
    """Put PAPER.pdf first in the deposition's explicit file order.

    Zenodo documents that the first file in this order is the default preview.
    This makes the article, rather than a manifest or source file, the landing-
    page object while preserving every companion file.
    """
    draft_id = int(draft["id"])
    rows = file_rows(draft)
    by_name = {row_name(row): row for row in rows}
    paper = by_name.get("PAPER.pdf")
    if paper is None:
        raise GateError("Zenodo draft lacks PAPER.pdf for the default preview")
    ordered = [paper, *(row for row in rows if row_name(row) != "PAPER.pdf")]
    payload: list[dict[str, Any]] = []
    for row in ordered:
        file_id = row.get("id")
        if not file_id:
            raise GateError("Zenodo draft file lacks an ID needed to set preview order")
        payload.append({"id": file_id})
    request_json(
        "PUT", f"{API}/deposit/depositions/{draft_id}/files",
        token=token, payload=payload, expected=(200,),
    )
    refreshed = deposit(token, draft_id)
    names = [row_name(row) for row in file_rows(refreshed)]
    if not names or names[0] != "PAPER.pdf":
        raise GateError("Zenodo did not retain PAPER.pdf as the first/default-preview file")
    return refreshed


# Set only for the bounded duration of publish(); it avoids placing absolute
# local paths in Zenodo state or receipts.
_UPLOAD_DIRECTORY: Path | None = None


def args_upload_path(_draft: dict[str, Any], name: str) -> Path:
    if _UPLOAD_DIRECTORY is None:
        raise GateError("internal upload-directory state is unavailable")
    path = _UPLOAD_DIRECTORY / name
    if not path.is_file():
        raise GateError(f"local upload file disappeared: {name}")
    return path


def metadata_matches(draft: dict[str, Any], reserved_doi: str) -> None:
    metadata = draft.get("metadata") or {}
    if str(metadata.get("version")) != SUCCESSOR_VERSION:
        raise GateError("Zenodo draft metadata version is not 1.1.0")
    if str(metadata.get("access_right", "")).lower() != "open":
        raise GateError("Zenodo draft access_right is not open")
    observed_reserved = str((metadata.get("prereserve_doi") or {}).get("doi") or reserved_doi)
    if observed_reserved != reserved_doi:
        raise GateError("Zenodo draft reserved DOI changed unexpectedly")


def verify_successor_public(record_id: int, desired: list[dict[str, Any]], reserved_doi: str) -> dict[str, Any]:
    deadline = time.monotonic() + 600
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            record, observed = public_inventory(record_id)
            if sorted((public_identity(row) for row in observed), key=lambda row: row["filename"]) != sorted(
                (public_identity(row) for row in desired), key=lambda row: row["filename"]
            ):
                raise GateError("public v1.1 Zenodo inventory differs from local bytes")
            if concept_id(record) != str(CONCEPT_RECORD_ID):
                raise GateError("public v1.1 record is outside the expected concept")
            if record_doi(record) != reserved_doi:
                raise GateError("public v1.1 DOI differs from the reserved DOI")
            metadata = record.get("metadata") or {}
            if str(metadata.get("version")) != SUCCESSOR_VERSION:
                raise GateError("public Zenodo version is not 1.1.0")
            access = str(metadata.get("access_right") or (record.get("access") or {}).get("status") or "").lower()
            if access not in {"open", "open access"}:
                raise GateError("public v1.1 Zenodo record is not open access")
            public_order = [row_name(row) for row in file_rows(record)]
            if not public_order or public_order[0] != "PAPER.pdf":
                raise GateError("public Zenodo record does not front PAPER.pdf")
            return {
                "record_id": record_id,
                "version_doi": reserved_doi,
                "concept_record_id": CONCEPT_RECORD_ID,
                "concept_doi": CONCEPT_DOI,
                "file_count": len(observed),
                "total_bytes": sum(row["bytes"] for row in observed),
                "inventory_sha256": inventory_digest(observed),
                "default_preview_file": "PAPER.pdf",
                "files": sorted((public_identity(row) for row in observed), key=lambda row: row["filename"]),
            }
        except GateError as exc:
            last_error = exc
            time.sleep(5)
    raise GateError(f"public Zenodo v1.1 readback did not settle ({type(last_error).__name__})")


def publish(token: str, state: dict[str, Any], baseline: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    global _UPLOAD_DIRECTORY
    if not state.get("draft_id") or not state.get("reserved_doi"):
        raise GateError("publish requires a completed transaction-owned reserve step")
    if state.get("predecessor_inventory_sha256") != baseline["inventory_sha256"]:
        raise GateError("v1.0 baseline changed after DOI reservation")
    if state.get("published_record_id"):
        desired = local_inventory(args.upload_dir)
        successor = verify_successor_public(
            int(state["published_record_id"]), desired, str(state["reserved_doi"])
        )
        baseline_after = baseline_gate()
        if baseline_after != baseline:
            raise GateError("frozen public v1.0 Zenodo identities changed after publication")
        return finalize_receipt(state, baseline, successor, args)
    if state.get("publish_attempted_at_utc"):
        # The publish request may have succeeded even if its response was lost.
        # Zenodo uses the deposition ID as the public record ID; adopt it only
        # after the complete anonymous byte/DOI/preview gate succeeds.
        candidate_id = int(state.get("expected_public_record_id") or state["draft_id"])
        try:
            candidate = public_record(candidate_id)
        except GateError:
            candidate = None
        if candidate is not None and record_doi(candidate) == str(state["reserved_doi"]):
            successor = verify_successor_public(
                candidate_id, local_inventory(args.upload_dir), str(state["reserved_doi"])
            )
            state.update({
                "published_record_id": candidate_id,
                "published_at_utc": utc_now(),
                "status": "uncertain_publish_reconciled_by_anonymous_readback",
            })
            atomic_json(args.state, state)
            baseline_after = baseline_gate()
            if baseline_after != baseline:
                raise GateError("frozen public v1.0 Zenodo identities changed after recovered publication")
            return finalize_receipt(state, baseline, successor, args)
    draft = authenticated_draft_gate(token, state, allow_create=False)
    if draft is None:
        if state.get("published_record_id"):
            successor = verify_successor_public(int(state["published_record_id"]), local_inventory(args.upload_dir), str(state["reserved_doi"]))
            return finalize_receipt(state, baseline, successor, args)
        raise GateError("transaction-owned Zenodo draft is missing")

    if bool(draft.get("submitted")):
        successor = verify_successor_public(
            int(state.get("expected_public_record_id") or state["draft_id"]),
            local_inventory(args.upload_dir), str(state["reserved_doi"]),
        )
        state.update({
            "published_record_id": successor["record_id"],
            "published_at_utc": utc_now(),
            "status": "submitted_draft_reconciled_by_anonymous_readback",
        })
        atomic_json(args.state, state)
        return finalize_receipt(state, baseline, successor, args)

    desired = local_inventory(args.upload_dir)
    privacy_gate(args.upload_dir)
    wrapper = metadata_gate(args.metadata_json, args.upload_dir, str(state["reserved_doi"]))
    _UPLOAD_DIRECTORY = args.upload_dir
    try:
        draft = reconcile_files(token, draft, desired)
    finally:
        _UPLOAD_DIRECTORY = None
    draft = set_pdf_default_preview(token, draft)
    observed = deposit_inventory(draft)
    expected = {row["filename"]: {"bytes": row["bytes"], "md5": row["md5"]} for row in desired}
    reduced = {name: {"bytes": row["bytes"], "md5": row["md5"]} for name, row in observed.items()}
    if reduced != expected:
        raise GateError("Zenodo v1.1 draft failed its exact pre-publication file gate")
    draft = request_json(
        "PUT", f"{API}/deposit/depositions/{int(state['draft_id'])}",
        token=token, payload={"metadata": wrapper["metadata"]}, expected=(200,),
    )
    if not isinstance(draft, dict):
        raise GateError("Zenodo metadata update returned an invalid draft")
    metadata_matches(draft, str(state["reserved_doi"]))
    state.update({
        "upload_inventory_sha256": inventory_digest(desired),
        "default_preview_file": "PAPER.pdf",
        "status": "draft_files_and_metadata_exact_ready_to_publish",
        "updated_at_utc": utc_now(),
    })
    atomic_json(args.state, state)

    state.update({
        "publish_attempted_at_utc": utc_now(),
        "expected_public_record_id": int(state["draft_id"]),
        "status": "publish_post_intent_persisted",
    })
    atomic_json(args.state, state)
    published = request_json(
        "POST", f"{API}/deposit/depositions/{int(state['draft_id'])}/actions/publish",
        token=token, payload={}, expected=(200, 201, 202), timeout=900,
    )
    if not isinstance(published, dict):
        raise GateError("Zenodo publish response is invalid")
    record_id = int(published.get("record_id") or published.get("id") or state["draft_id"])
    state.update({
        "published_record_id": record_id,
        "published_at_utc": utc_now(),
        "status": "published_awaiting_anonymous_readback",
    })
    atomic_json(args.state, state)
    successor = verify_successor_public(record_id, desired, str(state["reserved_doi"]))
    baseline_after = baseline_gate()
    if baseline_after != baseline:
        raise GateError("frozen public v1.0 Zenodo identities changed during publication")
    return finalize_receipt(state, baseline, successor, args)


def finalize_receipt(state: dict[str, Any], baseline: dict[str, Any], successor: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    receipt = {
        "schema": "standalone-zenodo-v1.1-publication-receipt/1.0",
        "status": "PUBLISHED_AND_ANONYMOUSLY_VERIFIED",
        "recorded_at_utc": utc_now(),
        "predecessor": baseline,
        "successor": successor,
        "same_concept_preserved": successor["concept_record_id"] == CONCEPT_RECORD_ID,
        "predecessor_record_edited": False,
        "access": "open",
        "credential_material_persisted": False,
    }
    atomic_json(args.receipt, receipt)
    state.update({"status": "complete", "completed_at_utc": utc_now(), "receipt": args.receipt.name})
    atomic_json(args.state, state)
    return receipt


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--action", choices=("preflight", "reserve", "publish"), default="preflight")
    parser.add_argument("--qa-receipt", type=Path, required=True)
    parser.add_argument("--upload-dir", type=Path)
    parser.add_argument("--metadata-json", type=Path)
    parser.add_argument("--token-file", type=Path, help="read only for --execute reserve/publish; never logged")
    parser.add_argument("--state", type=Path, default=ROOT / "ZENODO_V1_1_TRANSACTION_STATE_20260830.json")
    parser.add_argument("--receipt", type=Path, default=ROOT / "03_publication_receipts" / "ZENODO_V1_1_PUBLICATION_RECEIPT_20260830.json")
    parser.add_argument("--execute", action="store_true", help="permit the selected mutating action; preflight never mutates")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    state: dict[str, Any] = {}
    try:
        args.qa_receipt = task_path(args.qa_receipt, "QA receipt")
        args.state = task_path(args.state, "state path")
        args.receipt = task_path(args.receipt, "receipt path")
        qa = qa_gate(args.qa_receipt)
        state = load_state(args.state)
        baseline = baseline_gate()

        upload_rows: list[dict[str, Any]] | None = None
        metadata_summary: dict[str, Any] | None = None
        if args.action == "publish" or args.upload_dir is not None:
            if args.upload_dir is None or args.metadata_json is None:
                raise GateError("publish preflight requires --upload-dir and --metadata-json")
            args.upload_dir = task_path(args.upload_dir, "upload directory")
            args.metadata_json = task_path(args.metadata_json, "metadata JSON")
            upload_rows = local_inventory(args.upload_dir)
            privacy_gate(args.upload_dir)
            if not state.get("reserved_doi"):
                raise GateError("publish preflight requires a reserved DOI in transaction state")
            wrapper = metadata_gate(args.metadata_json, args.upload_dir, str(state["reserved_doi"]))
            metadata_summary = {
                "version": wrapper["metadata"].get("version"),
                "publication_date": wrapper["metadata"].get("publication_date"),
                "access_right": wrapper["metadata"].get("access_right"),
                "reserved_doi": state["reserved_doi"],
            }

        plan = {
            "schema": "standalone-zenodo-v1.1-publication-plan/1.0",
            "status": "PREFLIGHT_PASS",
            "action": args.action,
            "execute": args.execute,
            "predecessor": baseline,
            "qa_gate": qa,
            "transaction_state": "new" if not state else state.get("status"),
            "draft_id": state.get("draft_id"),
            "reserved_doi": state.get("reserved_doi"),
            "upload_files": None if upload_rows is None else len(upload_rows),
            "upload_inventory_sha256": None if upload_rows is None else inventory_digest(upload_rows),
            "metadata": metadata_summary,
            "credential_read": False,
            "mutations_performed": [],
        }
        if args.action == "preflight":
            if args.execute:
                raise GateError("--execute is invalid with the read-only preflight action")
            print(json.dumps(plan, indent=2, ensure_ascii=False))
            return 0
        if not args.execute:
            raise GateError(f"{args.action} is mutating and requires explicit --execute")
        if args.token_file is None:
            raise GateError("mutating actions require --token-file")
        token = load_token(args.token_file)
        if args.action == "reserve":
            result = reserve(token, state, baseline, args)
        else:
            if args.upload_dir is None or args.metadata_json is None:
                raise GateError("publish requires --upload-dir and --metadata-json")
            result = publish(token, state, baseline, args)
        print(json.dumps(result, indent=2, ensure_ascii=False))
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
        print(json.dumps({
            "schema": "standalone-zenodo-v1.1-publication-error/1.0",
            "status": "FAIL_CLOSED",
            "error": str(exc),
            "predecessor_record_edited": False,
            "public_record_deleted": False,
            "credential_material_persisted": False,
        }, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
