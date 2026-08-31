# SPDX-License-Identifier: MIT
"""Read-only, offline validation of the coordinator packet (Python 3.9+)."""

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys


EXPECTED = {
    ".gitattributes", "README.md", "ASSIGNMENTS.md", "STATUS.md",
    "CHECKPOINTS.json", "ISSUES.md", "SOURCES.md", "SOURCE_CORRECTIONS.md",
    "WORKFLOW.md", "INTEGRATION.md", "DECISIONS.md", "validate.py",
    "MANIFEST.sha256",
}
RANKS = {
    2: "bn-Beng-BD", 3: "te-Telu-IN", 4: "bn-Beng-IN", 5: "vi-Latn-VN",
    6: "mr-Deva-IN", 7: "ta-Taml-IN", 8: "pnb-Arab-PK",
    9: "jv-Latn-ID", 10: "gu-Gujr-IN",
}
PRIVATE_PATTERNS = {
    "host home path": r"(?i)(?:[a-z]:[\\/]+users[\\/]|/(?:Users|home)/)",
    "private worktree path": r"(?i)\.codex[\\/]worktrees[\\/]",
    "task identifier": r"(?i)\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
    "GitHub token": r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b",
    "API key": r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b",
    "private key": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
}


def safe_relative(value):
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and str(path) == value


def require(condition):
    """Scope checks must remain active under Python optimization."""
    if not condition:
        raise ValueError("packet invariant failed")


def validate_packet(blobs):
    """Accept a filename->bytes map; return errors without writing anything."""
    errors = []
    if set(blobs) != EXPECTED:
        errors.append("file allowlist mismatch")
    text = {}
    for name, data in blobs.items():
        if not safe_relative(name) or "/" in name:
            errors.append("unsafe or nested packet filename")
        if len(data) > 200_000:
            errors.append(f"oversized packet file: {name}")
        try:
            text[name] = data.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"non-UTF-8 file: {name}")
            continue
        if b"\r" in data or data.startswith(b"\xef\xbb\xbf"):
            errors.append(f"not canonical LF/no-BOM UTF-8: {name}")
        for label, pattern in PRIVATE_PATTERNS.items():
            if re.search(pattern, text[name]):
                errors.append(f"possible {label} in {name}; inspect privately")

    manifest = {}
    for line in text.get("MANIFEST.sha256", "").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_.-]+)", line)
        if not match:
            errors.append("invalid hash manifest line")
            continue
        digest, name = match.groups()
        if name in manifest:
            errors.append(f"duplicate hash entry: {name}")
        manifest[name] = digest
    if set(manifest) != EXPECTED - {"MANIFEST.sha256"}:
        errors.append("hash manifest coverage mismatch")
    for name, digest in manifest.items():
        if name not in blobs or hashlib.sha256(blobs[name]).hexdigest() != digest:
            errors.append(f"hash mismatch: {name}")

    try:
        record = json.loads(text.get("CHECKPOINTS.json", ""))
        require(record["schema"] == "language-allocation-coordination-v1")
        require(re.fullmatch(r"[0-9a-f]{40}", record["remote_base_commit"]))
        require(record["handoff_branch"] == "codex/language-allocation-handoff-2026-08-31")
        require(record["repository"] == "https://github.com/KokunoYumeto/allocating-ai-translation-compute-for-educational-access")
        for key in ("worker_git_objects_included", "worker_content_included", "ignored_source_assets_included"):
            require(record[key] is False)
        lanes = record["lanes"]
        require(len(lanes) == 9)
        require({lane["rank"]: lane["locale"] for lane in lanes} == RANKS)
        for lane in lanes:
            require(re.fullmatch(r"[0-9a-f]{40}", lane["checkpoint_commit"]))
            require(lane["checkpoint_verified_locally"] is True)
            require(lane["checkpoint_availability"] == "local_only_not_transferred")
            require(lane["whole_assignment_complete"] is False)
            require(lane["remote_configured_at_snapshot"] is False)
            require(lane["dirty_at_snapshot"] is True)
            require(safe_relative(lane["language_root"]))
            require(lane["branch"].startswith("codex/"))
            require(lane["assigned_materials"] and lane["committed_coverage"])
            require(lane["uncommitted_working_notes"] and lane["readiness_and_limits"])
            require(lane["rebuild"]["coordinator_replayed_this_build"] is False)
            require(len(lane["evidence"]) >= 6)
            for evidence in lane["evidence"]:
                require(safe_relative(evidence["path"]))
                require(evidence["path"].startswith(lane["language_root"] + "/"))
                require(evidence["present_at_checkpoint"] is True)
                require(evidence["present_in_working_tree_at_check"] is True)
                require(evidence["bundled"] is False)
    except (ValueError, KeyError, TypeError, AttributeError):
        errors.append("checkpoint schema/scope invariant failed")

    for name, body in text.items():
        if not name.endswith(".md"):
            continue
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", body):
            if target.startswith(("https://", "http://", "#")):
                continue
            local = target.split("#", 1)[0]
            if local not in blobs:
                errors.append(f"broken bundled document link: {name} -> {local}")
    return errors


def main():
    root = Path(__file__).resolve().parent
    entries = list(root.iterdir())
    if any(entry.is_symlink() or not entry.is_file() for entry in entries):
        print("FAIL: unexpected directory, symlink or non-file in packet")
        return 1
    errors = validate_packet({entry.name: entry.read_bytes() for entry in entries})
    if errors:
        for error in errors:
            print("FAIL:", error)
        return 1
    print("PASS: 13 allowlisted files; 12 SHA-256 entries; 9 local-only lane checkpoints; document links and privacy patterns checked.")
    print("This validates the coordination packet, not translation quality, external evidence availability or worker builds.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
