#!/usr/bin/env python3
"""Build and verify the bounded public v2 reproducibility package."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


TEXT_SUFFIXES = {".csv", ".json", ".jsonl", ".md", ".txt", ".py", ".ps1", ".cff", ""}
EXCLUDED_SCRIPTS = {"zenodo_publish_v2.py"}
ROOT_METADATA = {
    "README.md",
    "CITATION.cff",
    "LICENSE",
    "CODE_LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "zenodo_metadata_v2.json",
}
EXTRA_PUBLIC = {
    "qa/FINAL_ARTIFACT_QA_SUMMARY_v1.json",
    "qa/HTML_BUILD_REPORT_v1.json",
}


class HrefParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self.hrefs.append(href)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def local_links(root: Path) -> set[str]:
    parser = HrefParser()
    parser.feed((root / "index.html").read_text(encoding="utf-8"))
    result: set[str] = set()
    for href in parser.hrefs:
        parsed = urlparse(href)
        if parsed.scheme or href.startswith(("#", "//")):
            continue
        rel = unquote(parsed.path).replace("\\", "/").lstrip("./")
        if rel:
            result.add(rel)
    return result


def privacy_findings(root: Path, paths: list[str]) -> list[dict[str, object]]:
    patterns = {
        "profile_name": re.compile(r"\bfloris\b", re.I),
        "windows_profile_path": re.compile(r"[A-Za-z]:\\Users\\", re.I),
        "codex_private_path": re.compile(r"\\\.codex(?:\\|/)", re.I),
        "github_token": re.compile(r"github_pat_[A-Za-z0-9_]+", re.I),
        "bearer_credential": re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}", re.I),
        "zenodo_token_locator": re.compile(r"New\s+zenodo\s+token", re.I),
    }
    findings: list[dict[str, object]] = []
    for rel in paths:
        path = root / rel
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"LICENSE", "CODE_LICENSE"}:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            continue
        for name, pattern in patterns.items():
            matches = list(pattern.finditer(text))
            if matches:
                findings.append({"path": rel, "pattern": name, "count": len(matches)})
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = local_links(root) | ROOT_METADATA | EXTRA_PUBLIC
    for path in sorted((root / "scripts").iterdir()):
        if path.is_file() and path.name not in EXCLUDED_SCRIPTS and path.suffix.lower() in {".py", ".ps1", ".json", ".md", ".txt"}:
            paths.add(path.relative_to(root).as_posix())

    missing = sorted(rel for rel in paths if not (root / rel).is_file())
    if missing:
        raise RuntimeError(f"Missing public files: {missing}")

    ordered = sorted(paths)
    privacy = privacy_findings(root, ordered)
    if privacy:
        raise RuntimeError(f"Privacy/credential patterns found: {privacy}")

    records = [
        {"path": rel, "bytes": (root / rel).stat().st_size, "sha256": digest(root / rel)}
        for rel in ordered
    ]
    manifest = {
        "schema": "interlanguage/public-release-manifest/2.0.0",
        "generated_utc": utc_now(),
        "version": "2.0.0",
        "root_file_count": len(records),
        "root_total_bytes": sum(record["bytes"] for record in records),
        "privacy_scan": {
            "status": "PASS",
            "findings": privacy,
            "patterns": [
                "profile name",
                "Windows profile paths",
                "private .codex paths",
                "GitHub token prefix",
                "Bearer credential values",
                "Zenodo token locator",
            ],
        },
        "files": records,
    }
    manifest_path = output_dir / "RELEASE_MANIFEST_v2.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    sha_lines = [f'{record["sha256"]}  {record["path"]}' for record in records]
    sha_path = output_dir / "MANIFEST.sha256"
    sha_path.write_text("\n".join(sha_lines) + "\n", encoding="utf-8")

    zip_path = output_dir / "REPRODUCIBILITY_PACKAGE_v2.0.0_20260904.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for rel in ordered:
            zf.write(root / rel, rel)
        zf.write(manifest_path, manifest_path.name)
        zf.write(sha_path, sha_path.name)

    failures: list[dict[str, object]] = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        bad_member = zf.testzip()
        names = zf.namelist()
        for record in records:
            info = zf.getinfo(record["path"])
            with zf.open(info) as f:
                h = hashlib.sha256()
                total = 0
                for chunk in iter(lambda: f.read(1024 * 1024), b""):
                    total += len(chunk)
                    h.update(chunk)
            if total != record["bytes"] or h.hexdigest().upper() != record["sha256"]:
                failures.append({"path": record["path"], "bytes": total, "sha256": h.hexdigest().upper()})

    validation = {
        "schema": "interlanguage/public-release-package-validation/2.0.0",
        "generated_utc": utc_now(),
        "status": "PASS" if not bad_member and not failures else "FAIL",
        "zip": {"path": str(zip_path), "bytes": zip_path.stat().st_size, "sha256": digest(zip_path)},
        "manifest": {"path": str(manifest_path), "bytes": manifest_path.stat().st_size, "sha256": digest(manifest_path)},
        "sha256_list": {"path": str(sha_path), "bytes": sha_path.stat().st_size, "sha256": digest(sha_path)},
        "expected_payload_files": len(records),
        "zip_entries": len(names),
        "zip_testzip_result": bad_member,
        "identity_failures": failures,
        "privacy_scan_status": "PASS" if not privacy else "FAIL",
        "credential_recorded": False,
    }
    validation_path = root / "qa" / "RELEASE_PACKAGE_VALIDATION_v2.json"
    validation_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
