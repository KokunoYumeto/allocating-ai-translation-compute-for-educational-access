"""Convert an audit JSON report into a portable, deterministic artifact.

Absolute paths below ``--workspace-root`` become forward-slash paths relative
to that root.  Rewriting applies to object keys as well as string values,
because audit ``input_sha256`` maps use paths as keys.

Examples (PowerShell):

    python -B portable_audit_report.py full.json --workspace-root C:\\work\\repo
    python -B portable_audit_report.py full.json --workspace-root C:\\work\\repo `
        --drop-missing-direct-math-evidence --full-report-command `
        "python -B vi-Latn-VN/tools/audit_m49304.py" --output compact.json

Use ``-`` (the default input/output) for stdin/stdout.  The compact-report hash
is over the portable full object before evidence is omitted.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path, PurePosixPath, PureWindowsPath
import argparse
import json
import re
import sys

from safe_output import write_atomic


OMISSION_REASON = (
    "Exact raw XML remains reproducible from the pinned source via the auditor; "
    "omitted from this compact review artifact."
)
CANONICAL_SERIALIZATION = (
    "UTF-8; ensure_ascii=false; sort_keys=true; separators=(comma,colon)"
)


def normalize_workspace_root(value):
    """Return a slash-normalized absolute root without a trailing separator."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("workspace root must be a nonempty absolute path")
    value = value.strip()
    if not (PureWindowsPath(value).is_absolute() or PurePosixPath(value).is_absolute()):
        raise ValueError("workspace root must be an absolute path")
    normalized = value.replace("\\", "/")
    # Keep the separator for filesystem roots, but ordinary workspace roots do
    # not need one.  This also makes prefix-boundary checks unambiguous.
    if normalized not in {"/"} and not re.fullmatch(r"[A-Za-z]:/", normalized):
        normalized = normalized.rstrip("/")
    return normalized


def relative_workspace_string(value, workspace_root):
    """Rewrite one exact-root or root-descendant string, otherwise preserve it."""
    normalized = value.replace("\\", "/")
    root = normalize_workspace_root(workspace_root)
    windows = bool(re.match(r"^[A-Za-z]:/", root))
    compare_value = normalized.casefold() if windows else normalized
    compare_root = root.casefold() if windows else root
    if compare_value == compare_root:
        return "."
    prefix = compare_root if compare_root.endswith("/") else compare_root + "/"
    if compare_value.startswith(prefix):
        return normalized[len(prefix):]
    return value


def rewrite_workspace_paths(value, workspace_root):
    """Recursively rewrite matching JSON keys and string values.

    A collision after key rewriting is rejected instead of silently discarding
    one audit binding.
    """
    root = normalize_workspace_root(workspace_root)
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            rewritten_key = relative_workspace_string(key, root)
            if rewritten_key in result:
                raise ValueError(f"path rewrite creates duplicate JSON key: {rewritten_key}")
            result[rewritten_key] = rewrite_workspace_paths(item, root)
        return result
    if isinstance(value, list):
        return [rewrite_workspace_paths(item, root) for item in value]
    if isinstance(value, str):
        return relative_workspace_string(value, root)
    return value


def canonical_json_sha256(value):
    """Hash the documented canonical UTF-8 JSON serialization."""
    data = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return sha256(data).hexdigest()


def compact_math_evidence(report, full_report_command=None):
    """Drop bulky direct-Math evidence and append its deterministic projection."""
    if not isinstance(report, dict):
        raise ValueError("compact projection requires a top-level JSON object")
    if "checkpoint_projection" in report:
        raise ValueError("input already contains checkpoint_projection")
    evidence = report.get("missing_direct_math_evidence")
    if not isinstance(evidence, list):
        raise ValueError("missing_direct_math_evidence must be present as a JSON list")
    full_hash = canonical_json_sha256(report)
    compact = deepcopy(report)
    compact.pop("missing_direct_math_evidence")
    projection = {
        "omitted_fields": ["missing_direct_math_evidence"],
        "omitted_source_math_records": len(evidence),
        "reason": OMISSION_REASON,
        "canonical_full_report_sha256": full_hash,
        "canonical_report_basis": (
            "Portable workspace-relative report before evidence omission."
        ),
        "canonical_serialization": CANONICAL_SERIALIZATION,
    }
    if full_report_command is not None:
        projection["full_report_command"] = full_report_command
    compact["checkpoint_projection"] = projection
    return compact


def read_input(path):
    data = sys.stdin.buffer.read() if path == "-" else Path(path).read_bytes()
    return json.loads(data.decode("utf-8-sig"))


def encode_output(report):
    return (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="-", help="UTF-8 JSON file, or - for stdin")
    parser.add_argument("--workspace-root", required=True,
                        help="absolute repository/workspace root to remove from paths")
    parser.add_argument("--output", default="-", help="UTF-8 JSON file, or - for stdout")
    parser.add_argument("--drop-missing-direct-math-evidence", action="store_true",
                        help="omit that evidence list and add checkpoint_projection")
    parser.add_argument("--full-report-command",
                        help="portable reproduction command recorded in checkpoint_projection")
    args = parser.parse_args(argv)
    if args.full_report_command and not args.drop_missing_direct_math_evidence:
        parser.error("--full-report-command requires --drop-missing-direct-math-evidence")
    try:
        report = rewrite_workspace_paths(read_input(args.input), args.workspace_root)
        if args.drop_missing_direct_math_evidence:
            report = compact_math_evidence(report, args.full_report_command)
        data = encode_output(report)
        if args.output == "-":
            sys.stdout.buffer.write(data)
        else:
            write_atomic(Path(args.output), data)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    sys.exit(main())
