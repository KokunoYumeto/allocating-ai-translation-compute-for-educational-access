#!/usr/bin/env python3
"""Anonymously verify every public GitHub release asset against local bytes."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import tempfile
import urllib.error
import urllib.parse
import urllib.request


USER_AGENT = "standalone-release-byte-verifier/1.0"
CHUNK = 1024 * 1024


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self.links.append(href)


def get(url: str, *, accept: str = "*/*"):
    request = urllib.request.Request(
        url,
        headers={"Accept": accept, "User-Agent": USER_AGENT},
        method="GET",
    )
    return urllib.request.urlopen(request, timeout=90)


def local_identity(path: Path) -> dict[str, object]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(CHUNK), b""):
            size += len(block)
            digest.update(block)
    return {"filename": path.name, "bytes": size, "sha256": digest.hexdigest()}


def remote_identity(filename: str, url: str) -> dict[str, object]:
    digest = hashlib.sha256()
    size = 0
    with get(url) as response:
        for block in iter(lambda: response.read(CHUNK), b""):
            size += len(block)
            digest.update(block)
    return {"filename": filename, "bytes": size, "sha256": digest.hexdigest()}


def write_atomic(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local-dir", required=True, type=Path)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    for value in (args.owner, args.repo, args.tag):
        if not re.fullmatch(r"[A-Za-z0-9._-]+", value):
            raise SystemExit("unsafe owner, repository, or tag")

    local_files = sorted(path for path in args.local_dir.resolve(strict=True).iterdir() if path.is_file())
    expected = [local_identity(path) for path in local_files]
    expected_by_name = {item["filename"]: item for item in expected}
    if len(expected_by_name) != len(expected):
        raise SystemExit("duplicate local filenames")

    fragment_url = (
        f"https://github.com/{args.owner}/{args.repo}/releases/expanded_assets/{args.tag}"
    )
    try:
        with get(fragment_url, accept="text/html,*/*;q=0.8") as response:
            fragment = response.read(4 * 1024 * 1024 + 1)
        if len(fragment) > 4 * 1024 * 1024:
            raise RuntimeError("expanded asset inventory exceeded safety limit")
        parser_html = LinkCollector()
        parser_html.feed(fragment.decode("utf-8"))
        prefix = f"/{args.owner}/{args.repo}/releases/download/{args.tag}/"
        links: dict[str, str] = {}
        for href in parser_html.links:
            if not href.startswith(prefix):
                continue
            filename = urllib.parse.unquote(href[len(prefix):])
            if not filename or "/" in filename or "\\" in filename or filename in links:
                raise RuntimeError("invalid or duplicate remote asset filename")
            links[filename] = "https://github.com" + href

        observed = [remote_identity(name, links[name]) for name in sorted(links)]
        observed_by_name = {item["filename"]: item for item in observed}
        missing = sorted(set(expected_by_name) - set(observed_by_name))
        unexpected = sorted(set(observed_by_name) - set(expected_by_name))
        mismatches = sorted(
            name for name in set(expected_by_name) & set(observed_by_name)
            if expected_by_name[name] != observed_by_name[name]
        )
        status = "PASS" if not missing and not unexpected and not mismatches else "FAIL"
        receipt: dict[str, object] = {
            "schema": "standalone-github-release-asset-readback/1.0.0",
            "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
            "status": status,
            "anonymous_readback": True,
            "credential_sources_used": [],
            "repository": f"{args.owner}/{args.repo}",
            "tag": args.tag,
            "expected_files": len(expected),
            "observed_files": len(observed),
            "matched_files": len(expected) - len(missing) - len(mismatches),
            "missing_remote_files": missing,
            "unexpected_remote_files": unexpected,
            "identity_mismatches": mismatches,
            "inventory": observed,
        }
    except (urllib.error.URLError, UnicodeDecodeError, RuntimeError) as exc:
        receipt = {
            "schema": "standalone-github-release-asset-readback/1.0.0",
            "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
            "status": "ERROR",
            "anonymous_readback": True,
            "credential_sources_used": [],
            "error_type": type(exc).__name__,
        }
        write_atomic(args.output, receipt)
        raise SystemExit(2)

    write_atomic(args.output, receipt)
    if status != "PASS":
        raise SystemExit(1)
    print(f"PASS: {len(observed)} GitHub release assets exactly match local bytes.")


if __name__ == "__main__":
    main()
