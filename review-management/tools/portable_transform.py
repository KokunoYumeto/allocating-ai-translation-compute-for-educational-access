"""Narrow, pure export transforms; never execute a worker or acquire inputs.

Call transform(original_repository_relative_path, blob_bytes). Unknown files are
unchanged. Known changed layouts fail closed. Run this file with --self-test and
the two local repository paths to syntax-check exact pinned Git blobs in memory.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import PurePosixPath
import re
import subprocess


VERSION = "portable-export-transform-v1"
BN_HEAD = "cbc493d825dd412d27e3efc7414dc3ce25a833cc"
TE_HEAD = "cf491833721b268fe4a826cd6da142d72ca3d87d"
CANONICAL_DIR = "osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9"
BN_PREFIX = "languages/bn-Beng-IN/scripts/"
BN_PY = {
    BN_PREFIX + name for name in (
        "build_sections.py", "freeze_sources.py", "stage_shared_canonical.py",
        "verify_acquisition.py",
    )
}
BN_JS = BN_PREFIX + "visual_qa.cjs"
TE_JS = {
    "te-Telu-IN/scripts/visual_qa.cjs",
    "te-Telu-IN/scripts/visual_unit.cjs",
    *(f"te-Telu-IN/assets/{unit}/render-author.cjs" for unit in ("B006", "B008", "B011")),
}
TARGETS = BN_PY | TE_JS | {BN_JS}
PRIVATE_HOME = re.compile(r"(?i)[a-z]:[/\\]+Users[/\\]+[^/\\\s'\"]+[/\\]")
PATH_CALL = re.compile(r"Path\((['\"])([^'\"\r\n]+)\1\)")
PLAYWRIGHT_IMPORT = re.compile(
    r"(?m)^const\s+\{\s*chromium\s*\}\s*=\s*require\(([^\r\n;]+)\);\s*$"
)

PY_HELPERS = '''
import os  # portable-export-transform-v1

def _portable_input_path(variable, default):
    """Resolve optional configured inputs without touching disk during import."""
    value = os.environ.get(variable)
    result = Path(value).expanduser() if value else default
    return result if result.is_absolute() else ROOT / result

def _require_portable_input(value, variable):
    if not value.exists():
        raise FileNotFoundError(
            f"Required pinned input is absent: {value}. Set {variable} to its "
            "existing location or restore the exact source-lock inputs under "
            "workspace downloads. This helper does not acquire sources."
        )
    return value

'''


def _once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise ValueError(f"Unsupported source layout for {label}; review transform")
    return text.replace(old, new, 1)


def _canonical_expression() -> str:
    return f"_portable_input_path('BN_CANONICAL_ROOT', ROOT / 'downloads' / {CANONICAL_DIR!r})"


def _python_transform(path: str, text: str) -> tuple[str, list[str]]:
    replaced = 0

    def replace_path(match: re.Match[str]) -> str:
        nonlocal replaced
        original = match.group(2)
        if not PRIVATE_HOME.search(original):
            return match.group(0)
        normalized = original.replace("\\", "/").rstrip("/")
        if normalized.endswith("/" + CANONICAL_DIR):
            replacement = _canonical_expression()
        elif path.endswith("/freeze_sources.py") and normalized.endswith("/" + CANONICAL_DIR + "/media"):
            replacement = "(" + _canonical_expression() + " / 'media')"
        elif path.endswith("/stage_shared_canonical.py") and normalized.endswith("/downloads"):
            replacement = "_portable_input_path('BN_DONOR_DOWNLOADS', ROOT / 'downloads')"
        else:
            raise ValueError(f"Unrecognized private input in {path}; review transform")
        replaced += 1
        return replacement

    result = PATH_CALL.sub(replace_path, text)
    expected = 2 if path.endswith("/stage_shared_canonical.py") else 1
    if replaced != expected:
        raise ValueError(f"Expected {expected} private input expressions in {path}, found {replaced}")
    result = _once(result, "from pathlib import Path\n", "from pathlib import Path\n" + PY_HELPERS, path)
    labels = [
        "BN_CANONICAL_ROOT: existing pinned extraction; default workspace/downloads/" + CANONICAL_DIR,
        "Required source paths resolve lazily; no acquisition or full-build claim",
        "Code bytes changed: original builder-hash receipts do not attest transformed code",
    ]
    if path.endswith("/build_sections.py"):
        result = _once(result, "original=SHARED/'media'/name", "original=_require_portable_input(SHARED/'media'/name, 'BN_CANONICAL_ROOT')", path)
        result = _once(
            result, "str(ROOT/'downloads/osbooks-prealgebra-bundle')",
            "str(_require_portable_input(_portable_input_path('BN_CANONICAL_GIT_ROOT', ROOT/'downloads/osbooks-prealgebra-bundle'), 'BN_CANONICAL_GIT_ROOT'))", path,
        )
        labels.append("Frozen media-lock fast path retained; new media also needs BN_CANONICAL_GIT_ROOT or default pinned workspace Git repository")
    elif path.endswith("/freeze_sources.py"):
        result = _once(result, "copy(src,dest)", "copy(_require_portable_input(src, 'BN_CANONICAL_ROOT'),dest)", path)
        labels.append("Full acquisition/freezing still needs all source-lock workspace downloads; not an ordinary reader-build prerequisite")
    elif path.endswith("/stage_shared_canonical.py"):
        result = _once(result, "source=DONOR/source_name", "source=_require_portable_input(DONOR/source_name, 'BN_DONOR_DOWNLOADS')", path)
        labels.append("BN_DONOR_DOWNLOADS defaults to workspace/downloads; original explicit bulk-staging flag and 3GB guard retained")
        labels.append("Acquisition receipts may contain receiving-PC configured paths; review before later publication")
    elif path.endswith("/verify_acquisition.py"):
        result = _once(result, "p=base/'media'/name", "p=_require_portable_input(base/'media'/name, 'BN_CANONICAL_ROOT' if c['course']!='A30' else 'the source-lock A30 workspace path')", path)
        labels.append("Full verification still requires pinned workspace Git objects, A30 inputs and canon/OCR files")
    return result, labels


def _javascript_transform(path: str, text: str) -> tuple[str, list[str]]:
    language = "BN" if path == BN_JS else "TE"
    matches = list(PLAYWRIGHT_IMPORT.finditer(text))
    if len(matches) != 1 or not PRIVATE_HOME.search(matches[0].group(1)):
        raise ValueError(f"Unsupported Playwright import layout in {path}")
    replacement = f'''// {VERSION}
let chromium;
try {{
  ({{chromium}} = require(process.env.{language}_PLAYWRIGHT_MODULE || process.env.PLAYWRIGHT_MODULE_PATH || 'playwright'));
}} catch (error) {{
  throw new Error('Playwright is unavailable. Configure {language}_PLAYWRIGHT_MODULE or PLAYWRIGHT_MODULE_PATH for this PC, or install it through your normal dependency workflow. No automatic acquisition is performed.');
}}
'''.rstrip()
    result = PLAYWRIGHT_IMPORT.sub(lambda _: replacement, text, count=1)
    if language == "BN":
        old = "executablePath:process.env.BN_BROWSER_PATH || 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'"
        new = "...(process.env.BN_BROWSER_PATH ? {executablePath:process.env.BN_BROWSER_PATH} : {channel:process.env.BN_BROWSER_CHANNEL || 'msedge'})"
        result = _once(result, old, new, path)
    else:
        result, count = re.subn(
            r"channel:\s*'msedge'",
            "...(process.env.TE_BROWSER_PATH ? {executablePath:process.env.TE_BROWSER_PATH} : {channel:process.env.TE_BROWSER_CHANNEL || 'msedge'})",
            result,
        )
        if count != 1:
            raise ValueError(f"Expected one Edge launch in {path}, found {count}")
    # Receipt wording must not misidentify a user-configured Chromium browser as Edge.
    for old in (
        "Isolated headless Edge", "Headless Microsoft Edge via Playwright", "Headless Edge via Playwright",
        "isolated Edge headless via bundled Playwright",
    ):
        result = result.replace(old, "Configured headless Chromium-family browser via Playwright")
    result = result.replace(
        "reason:'In-app Node runtime failed to write kernel assets before bootstrap'",
        "reason:'Portable configured runtime; originating in-app bootstrap failure is historical'",
    ).replace(
        "Configured headless Chromium-family browser via Playwright; in-app runtime unavailable",
        "Configured headless Chromium-family browser via Playwright; originating runtime failure is historical",
    )
    labels = [
        f"Playwright resolution: {language}_PLAYWRIGHT_MODULE, PLAYWRIGHT_MODULE_PATH, then normal node module lookup",
        f"Browser: {language}_BROWSER_PATH or {language}_BROWSER_CHANNEL (default msedge); installed runtime required",
        "Original navigation/profile/access restrictions retained; no browser execution or new visual QA performed",
        "Transformed runtime code has not been covered by original environment-specific visual receipts",
    ]
    if language == "TE" and "/scripts/" in path:
        labels.append("Existing local reader server at 127.0.0.1:8763 remains required; not started by this transform")
    return result, labels


def transform(path: str, data: bytes) -> tuple[bytes, list[str]]:
    """Pure bytes-in/bytes-out; path is the original repository-relative path.

    Prefixed export paths are accepted only when their suffix is a known target.
    Unknown paths are unchanged. No environment, filesystem or subprocess access.
    """
    normalized = str(PurePosixPath(path.replace("\\", "/")))
    target = next((p for p in TARGETS if normalized == p or normalized.endswith("/" + p)), None)
    if target is None:
        return data, []
    text = data.decode("utf-8")
    if VERSION in text:
        if PRIVATE_HOME.search(text):
            raise ValueError(f"Transformed marker with remaining private input in {target}")
        return data, ["Already transformed: " + VERSION]
    if not PRIVATE_HOME.search(text):
        return data, ["Known target has no private-home input; no code transformation performed"]
    # Known Git inputs use LF; accepting CRLF creates a recorded LF derivative.
    text = text.replace("\r\n", "\n")
    result, labels = _python_transform(target, text) if target in BN_PY else _javascript_transform(target, text)
    if PRIVATE_HOME.search(result):
        raise ValueError(f"Unresolved private input remains in {target}")
    if target.endswith(".py"):
        ast.parse(result, filename=target)
    return result.encode("utf-8"), [VERSION, *labels]


def self_test(telugu_repo: str, bengali_repo: str, node: str = "node") -> list[dict]:
    """Read pinned Git bytes; compile syntax only. No worker code is executed."""
    results = []
    if transform("unrelated.bin", b"\x00\xff") != (b"\x00\xff", []):
        raise AssertionError("Unknown files must be unchanged")
    for path in sorted(TARGETS):
        is_bn = path.startswith("languages/")
        repo, head = (bengali_repo, BN_HEAD) if is_bn else (telugu_repo, TE_HEAD)
        original = subprocess.check_output(["git", "--no-optional-locks", "-C", repo, "show", head + ":" + path])
        output, labels = transform(path, original)
        if output == original or PRIVATE_HOME.search(output.decode("utf-8")):
            raise AssertionError(f"Expected complete targeted transformation: {path}")
        if transform(path, output)[0] != output:
            raise AssertionError(f"Not idempotent: {path}")
        # A newly introduced private input must not silently become a placeholder.
        unexpected = original + b"\n# extra C:/Users/EXAMPLE/private-input\n" if path.endswith(".py") else original + b"\n// extra C:/Users/EXAMPLE/private-input\n"
        try:
            transform(path, unexpected)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Unexpected private input did not fail closed: {path}")
        if path.endswith(".py"):
            compile(output, path, "exec")
            before = ast.parse(original)
            after = ast.parse(output)
            old_functions = {n.name for n in ast.walk(before) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
            new_functions = {n.name for n in ast.walk(after) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
            if not old_functions <= new_functions:
                raise AssertionError(f"Original functions removed: {path}")
            if path.endswith("stage_shared_canonical.py"):
                for guard in (b"'--allow-bulk-staging' not in sys.argv", b"shutil.disk_usage(ROOT).free < 3_000_000_000"):
                    if guard not in output:
                        raise AssertionError("Original bulk-staging guards were changed")
        else:
            checked = subprocess.run([node, "--check", "-"], input=output, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            if checked.returncode:
                raise AssertionError(f"JavaScript syntax failed: {path}: {checked.stderr.decode('utf-8', 'replace')}")
        results.append({"path": path, "source_commit": head, "source_sha256": hashlib.sha256(original).hexdigest(), "export_sha256": hashlib.sha256(output).hexdigest(), "syntax": "pass", "labels": labels})
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", required=True)
    parser.add_argument("--telugu-repo", required=True)
    parser.add_argument("--bengali-repo", required=True)
    parser.add_argument("--node", default="node")
    arguments = parser.parse_args()
    print(json.dumps({"tests": self_test(arguments.telugu_repo, arguments.bengali_repo, arguments.node), "scope": "Git bytes, idempotence, retained Python functions and syntax only; no worker execution"}, indent=2))
