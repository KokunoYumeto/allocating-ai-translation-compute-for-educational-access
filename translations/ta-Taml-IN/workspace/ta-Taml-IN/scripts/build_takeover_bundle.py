#!/usr/bin/env python3
"""Build and verify the sanitized ta-Taml-IN takeover bundle.

The builder intentionally copies only the admitted/current Tamil lane and the
source/canon bytes actually used to make or review it.  It does not copy the
full downloaded book repositories or archives.  Those large inputs are pinned
in SOURCE-MATERIAL-INDEX.json and can be reacquired if later scope needs them.

The output is deterministic for a fixed working tree and Git checkpoint:

    python -X utf8 ta-Taml-IN/scripts/build_takeover_bundle.py
    python -X utf8 ta-Taml-IN/scripts/build_takeover_bundle.py --check
    python -X utf8 ta-Taml-IN/scripts/build_takeover_bundle.py \
        --verify-bundle takeover/ta-Taml-IN-20260902

The default write mode refuses to touch an existing output directory.  No
archive is created and no source file is modified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable


SCHEMA = "ta-taml-in-takeover-manifest/v1"
BUNDLE_DATE = "2026-09-02"
BUNDLE_NAME = f"ta-Taml-IN-{BUNDLE_DATE.replace('-', '')}"
CANON_COMMIT = "38cae454e644abf9f0a623e876994553881597c9"
ID_COMMIT = "3de9207f56f8b5c57c017abf973fb04e00d740f1"
PRIVATE_TASK_ID = "[local-task-id]"

TEXT_SUFFIXES = {
    ".css",
    ".csv",
    ".cnxml",
    ".html",
    ".json",
    ".jsonl",
    ".md",
    ".ncx",
    ".opf",
    ".py",
    ".svg",
    ".tsv",
    ".txt",
    ".xhtml",
    ".xml",
}

# Current/incomplete work is deliberately kept out even if an active worker
# creates another file while this script is running.
EXCLUDED_PROJECT_EXACT = {
    "assets/m81243-pdf.css",
    "output/pdf/ta-Taml-IN-A00-U001-print.pdf",
    "output/pdf/ta-Taml-IN-A00-U001-screen.pdf",
    "output/pdf/ta-Taml-IN-A00-m81243-print.pdf",
    "output/pdf/ta-Taml-IN-A00-m81243-screen.pdf",
    "qa/M81243-PDF-QA.md",
    "qa/M81243-pdf-export.json",
    "qa/M81243-pdf-receipt.json",
    "qa/M81243-print-corrected-independent-review.md",
    "qa/M81243-print-corrected-review.md",
    "qa/M81243-print-visual-review.md",
    "qa/M81243-screen-visual-review.md",
    "scripts/qa_m81243_pdf.py",
    "scripts/render_m81243_pdf.py",
    "scripts/pdf_qa.py",
}

ALLOWED_OUTPUT_PDFS = {
    "output/pdf/ta-Taml-IN-A00-U002-print.pdf",
    "output/pdf/ta-Taml-IN-A00-U002-screen.pdf",
}


@dataclass(frozen=True)
class InputFile:
    source: Path
    destination: PurePosixPath
    role: str
    origin: str


@dataclass(frozen=True)
class PayloadFile:
    path: PurePosixPath
    data: bytes
    role: str
    origin: str
    source_path: str | None
    source_bytes: int | None
    source_sha256: str | None
    sanitized: bool


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_git(repo_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout.strip()


def git_identity(repo_root: Path) -> dict[str, str]:
    return {
        "branch": run_git(repo_root, "branch", "--show-current"),
        "head": run_git(repo_root, "rev-parse", "HEAD"),
        "parent": run_git(repo_root, "rev-parse", "HEAD^"),
        "tree": run_git(repo_root, "rev-parse", "HEAD^{tree}"),
    }


def is_active_or_excluded_project_path(relative: PurePosixPath) -> bool:
    rel = relative.as_posix()
    lower = rel.lower()
    if rel in EXCLUDED_PROJECT_EXACT:
        return True
    if lower.startswith("qa/m81243-") and any(
        marker in lower for marker in ("pdf", "print", "screen")
    ):
        return True
    if lower.startswith("scripts/") and "m81243" in lower and "pdf" in lower:
        return True
    if rel.startswith("reader/"):
        return True
    if rel.startswith("scripts/__pycache__/") or lower.endswith(".pyc"):
        return True
    if rel.startswith("output/pdf/") and rel not in ALLOWED_OUTPUT_PDFS:
        return True
    if "m81245-fs-id1824154" in lower or "/u020/" in lower:
        return True
    if "u45-u0200" in lower or "m81245-u020" in lower:
        return True
    if "m81244" in lower and "missing" in lower:
        return True
    if "addition" in lower and "missing-answer" in lower:
        return True
    if "missing-answer" in lower and "m81244" in lower:
        return True
    if lower.startswith("takeover/"):
        return True
    return False


def project_role(relative: PurePosixPath) -> str:
    rel = relative.as_posix()
    if rel in {"GOAL.md", "NEXT_UNIT.md", "DECISIONS.md"}:
        return "durable-workflow-state"
    if rel == "terminology.tsv":
        return "Tamil-terminology-ledger"
    if rel == "sources.lock.json":
        return "source-pin-lock"
    if rel.startswith("canon/"):
        return "Tamil-canon-index-and-consultation-log"
    if rel.startswith("translation/"):
        return "Tamil-source-or-labelled-recovery-content"
    if rel.startswith("assets/"):
        return "Tamil-derivative-asset-or-build-resource"
    if rel.startswith("reader"):
        return "review-reader-or-offline-package"
    if rel.startswith("scripts/"):
        return "build-or-QA-tool"
    if rel.startswith("qa/"):
        return "QA-note-receipt-or-review"
    if rel.startswith("provenance/"):
        return "pinned-source-license-or-provenance-witness"
    if rel.startswith("output/pdf/"):
        return "verified-U002-PDF"
    return "Tamil-project-metadata"


def iter_project_inputs(repo_root: Path) -> Iterable[InputFile]:
    project_root = repo_root / "ta-Taml-IN"
    for source in sorted(project_root.rglob("*"), key=lambda p: p.as_posix()):
        if not source.is_file():
            continue
        relative = PurePosixPath(source.relative_to(project_root).as_posix())
        if is_active_or_excluded_project_path(relative):
            continue
        yield InputFile(
            source=source,
            destination=PurePosixPath("project/ta-Taml-IN") / relative,
            role=project_role(relative),
            origin=f"workspace:ta-Taml-IN/{relative.as_posix()}",
        )


def media_references(witness: Path) -> list[str]:
    text = witness.read_text(encoding="utf-8")
    names = sorted(set(re.findall(r'src="\.\./\.\./media/([^\"]+)"', text)))
    for name in names:
        path = PurePosixPath(name)
        if path.name != name or name in {"", ".", ".."}:
            raise RuntimeError(f"unsafe media reference in {witness}: {name!r}")
    return names


def iter_source_inputs(repo_root: Path) -> Iterable[InputFile]:
    canon_dir = repo_root / "downloads" / "tamil-canon"
    for source in sorted(canon_dir.rglob("*"), key=lambda p: p.as_posix()):
        if source.is_file():
            relative = PurePosixPath(source.relative_to(canon_dir).as_posix())
            role = (
                "Tamil-canon-original-PDF"
                if source.suffix.lower() == ".pdf"
                else "Tamil-canon-readable-OCR-or-page-image"
            )
            yield InputFile(
                source=source,
                destination=PurePosixPath("source-material/tamil-canon") / relative,
                role=role,
                origin=(
                    "Government of Tamil Nadu/SCERT Class 6 Term 1 Mathematics, "
                    "first edition 2018; mirror https://www.kulikaraighss.in/books/6t1all/6t1maths.pdf"
                ),
            )

    tessdata = repo_root / "downloads" / "tessdata" / "tam.traineddata"
    yield InputFile(
        source=tessdata,
        destination=PurePosixPath("source-material/ocr-dependency/tam.traineddata"),
        role="OCR-language-model-dependency",
        origin="tesseract-ocr/tessdata_fast 4.1.0 Tamil traineddata",
    )

    project_provenance = repo_root / "ta-Taml-IN" / "provenance"
    canonical_media = (
        repo_root / "downloads" / f"osbooks-prealgebra-bundle-{CANON_COMMIT}" / "media"
    )
    id_media = repo_root / "downloads" / "openstax-prealgebra-2e-id-ID" / "media"
    for module in ("m81243", "m81244"):
        en_witness = project_provenance / f"{module}.en.cnxml"
        id_witness = project_provenance / f"{module}.id-ID.cnxml"
        for name in media_references(en_witness):
            yield InputFile(
                source=canonical_media / name,
                destination=(
                    PurePosixPath("source-material/openstax")
                    / f"canonical-{CANON_COMMIT}"
                    / "media"
                    / name
                ),
                role="original-English-mathematical-source-media",
                origin=(
                    "openstax/osbooks-prealgebra-bundle commit "
                    f"{CANON_COMMIT}; referenced by {module}.en.cnxml"
                ),
            )
        for name in media_references(id_witness):
            yield InputFile(
                source=id_media / name,
                destination=(
                    PurePosixPath("source-material/openstax")
                    / f"prealgebra-id-{ID_COMMIT}"
                    / "media"
                    / name
                ),
                role="original-Indonesian-mathematical-source-media",
                origin=(
                    "KokunoYumeto/openstax-prealgebra-2e-id-ID commit "
                    f"{ID_COMMIT}; referenced by {module}.id-ID.cnxml"
                ),
            )

    m81245_sources = (
        (
            repo_root
            / "downloads"
            / f"osbooks-prealgebra-bundle-{CANON_COMMIT}"
            / "modules"
            / "m81245"
            / "index.cnxml",
            "en",
            f"openstax/osbooks-prealgebra-bundle commit {CANON_COMMIT}",
        ),
        (
            repo_root
            / "downloads"
            / "openstax-prealgebra-2e-id-ID"
            / "modules"
            / "m81245"
            / "index.cnxml",
            "id-ID",
            f"KokunoYumeto/openstax-prealgebra-2e-id-ID commit {ID_COMMIT}",
        ),
    )
    for source, language, origin in m81245_sources:
        yield InputFile(
            source=source,
            destination=(
                PurePosixPath("source-material/openstax/m81245")
                / language
                / "index.cnxml"
            ),
            role=f"m81245-{language}-complete-source-witness-for-admitted-U019",
            origin=origin,
        )


def sanitize_text(text: str) -> str:
    original = text
    # Make documented build commands portable before removing the personal root.
    text = re.sub(
        r"&\s*['\"]C:/Users/[^/]+/\.cache/codex-runtimes/"
        r"codex-primary-runtime/dependencies/python/python\.exe['\"]",
        "python",
        text,
    )
    text = re.sub(
        r"C:/Users/[^/]+/\.cache/codex-runtimes/"
        r"codex-primary-runtime/dependencies/python/python\.exe",
        "python",
        text,
    )
    text = re.sub(
        r"C:/Users/[^/]+/\.codex/worktrees/[0-9A-Za-z_-]+/LAN ALLOC/",
        "repo:/",
        text,
    )
    text = re.sub(
        r"C:\\Users\\[^\\]+\\\.codex\\worktrees\\[^\\]+\\LAN ALLOC\\",
        "repo:/",
        text,
    )
    text = re.sub(
        r"C:/Users/[^/]+/Documents/ChatGPT/LAN ALLOC/logs/",
        "[external-evidence-path omitted]/",
        text,
    )
    text = re.sub(r"C:/Users/[^/\s`'\"<>]+", "[private-home omitted]", text)
    text = re.sub(r"C:\\Users\\[^\\\s`'\"<>]+", "[private-home omitted]", text)
    text = re.sub(
        r"codex://threads/[0-9a-fA-F-]{20,}",
        "[private task link omitted]",
        text,
    )
    text = text.replace(PRIVATE_TASK_ID, "[coordinator task id omitted]")
    # Never copy exact raw-instruction file names as if they were bundled inputs.
    text = text.replace("USER_INSTRUCTIONS_VERBATIM.md", "[excluded root instruction record]")
    text = text.replace("FULL_ASSIGNMENT_USER_INSTRUCTION.md", "[excluded root instruction record]")
    text = text.replace("COORDINATING_TASK.md", "[excluded root coordination record]")
    return text if text != original else original


def read_payload(input_file: InputFile, repo_root: Path) -> PayloadFile:
    source = input_file.source
    if not source.is_file():
        raise FileNotFoundError(f"required bundle input is absent: {source}")
    before_stat = source.stat()
    raw = source.read_bytes()
    after_stat = source.stat()
    if (before_stat.st_size, before_stat.st_mtime_ns) != (
        after_stat.st_size,
        after_stat.st_mtime_ns,
    ):
        raise RuntimeError(f"input changed while read: {source}")
    bundled = raw
    sanitized = False
    if source.suffix.lower() in TEXT_SUFFIXES:
        try:
            decoded = raw.decode("utf-8")
        except UnicodeDecodeError:
            decoded = None
        if decoded is not None:
            cleaned = sanitize_text(decoded)
            if cleaned != decoded:
                bundled = cleaned.encode("utf-8")
                sanitized = True
    try:
        source_path = source.relative_to(repo_root).as_posix()
    except ValueError:
        source_path = "[external path omitted]"
    return PayloadFile(
        path=input_file.destination,
        data=bundled,
        role=input_file.role,
        origin=input_file.origin,
        source_path=source_path,
        source_bytes=len(raw),
        source_sha256=sha256_bytes(raw),
        sanitized=sanitized,
    )


def source_material_index() -> bytes:
    index = {
        "schema": "ta-taml-in-source-material-index/v1",
        "bundle_date": BUNDLE_DATE,
        "principle": (
            "Include exact files actually used for admitted work; do not copy unused bulk corpora. "
            "Preserve original Tamil canon bytes and referenced English/Indonesian media beside derivatives."
        ),
        "included": {
            "Tamil_canon": (
                "Full 2018 reference PDF and the complete targeted OCR/page-image cache present "
                "at checkpoint time."
            ),
            "OpenStax_source": (
                "Exact m81243/m81244 EN/ID CNXML witnesses in project provenance, every media file "
                "they reference, and complete EN/ID m81245 witnesses used for admitted U019."
            ),
            "derivatives": (
                "Tamil CNXML, labelled companions, Tamil SVG redraws, corrected current readers, "
                "verified U002 PDFs, build tools, QA evidence, license notices and provenance."
            ),
        },
        "not_bundled_reacquirable_inputs": [
            {
                "role": "canonical A00/A10/A20 all-book acquisition archive",
                "reason": "537 MB archive contains mostly unused modules; exact used modules/media are included",
                "url": (
                    "https://codeload.github.com/openstax/osbooks-prealgebra-bundle/zip/"
                    f"{CANON_COMMIT}"
                ),
                "commit": CANON_COMMIT,
                "bytes": 537455794,
                "sha256": "effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917",
                "bytes_absent_from_bundle": True,
            },
            {
                "role": "A10 editable release archive",
                "reason": "A10 translation is unstarted; archive is unused bulk for this checkpoint",
                "url": (
                    "https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id/"
                    "releases/download/v1.0.2/elementary-algebra-2e-id-ID-1.0.2-source.zip"
                ),
                "version": "v1.0.2",
                "bytes": 6397865,
                "sha256": "6f04e88387e8d4e6e710dddcebb8d41e952a315231d7e203d62170c6ad9f3456",
                "bytes_absent_from_bundle": True,
            },
            {
                "role": "A20 editable release archive",
                "reason": "A20 translation is unstarted; archive is unused bulk for this checkpoint",
                "url": (
                    "https://github.com/KokunoYumeto/openstax-intermediate-algebra-2e-id/"
                    "releases/download/v0.3.0-wip/"
                    "openstax-intermediate-algebra-2e-id-ID-0.3.0-wip-editable-source.zip"
                ),
                "version": "v0.3.0-wip",
                "bytes": 106658915,
                "sha256": "a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7",
                "bytes_absent_from_bundle": True,
            },
            {
                "role": "catalog Git checkout",
                "reason": "selected authority excerpts and pins are included; full checkout is unused bulk",
                "url": "https://github.com/KokunoYumeto/program-matematika-indonesia.git",
                "commit": "2f0e52280791854f904475e5f92392f52745ea24",
                "tree": "af8d0254ca0132fc5c8c8622052e4b50b9392fff",
                "bytes_absent_from_bundle": True,
            },
            {
                "role": "allocation Git checkout",
                "reason": "selected authority excerpt is included; old ranking is not evidence for this work",
                "url": (
                    "https://github.com/KokunoYumeto/"
                    "allocating-ai-translation-compute-for-educational-access.git"
                ),
                "commit": "2c9c129c3e693bec5a0e387c76b1c270fccf399c",
                "tree": "67e61e7ce612b73c66639383a9dbe5d99b37d970",
                "bytes_absent_from_bundle": True,
            },
            {
                "role": "EPUBCheck validation tool",
                "reason": "external QA runtime, not educational source content",
                "url": "https://github.com/w3c/epubcheck/releases/tag/v5.3.0",
                "version": "5.3.0",
                "bytes_absent_from_bundle": True,
            },
        ],
        "access_date": "2026-08-30 through 2026-09-01; bundle prepared 2026-09-02",
        "authoritative_pin_record": "project/ta-Taml-IN/sources.lock.json",
    }
    return (json.dumps(index, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def collect_payload(repo_root: Path) -> tuple[list[PayloadFile], list[str]]:
    candidates = list(iter_project_inputs(repo_root)) + list(iter_source_inputs(repo_root))
    destinations: set[PurePosixPath] = set()
    payload: list[PayloadFile] = []
    for candidate in candidates:
        if candidate.destination in destinations:
            raise RuntimeError(f"duplicate bundle path: {candidate.destination}")
        destinations.add(candidate.destination)
        payload.append(read_payload(candidate, repo_root))

    source_index_path = PurePosixPath("SOURCE-MATERIAL-INDEX.json")
    if source_index_path in destinations:
        raise RuntimeError("generated source index collides with a copied file")
    payload.append(
        PayloadFile(
            path=source_index_path,
            data=source_material_index(),
            role="source-material-inclusion-and-reacquisition-index",
            origin="generated deterministically by project/ta-Taml-IN/scripts/build_takeover_bundle.py",
            source_path=None,
            source_bytes=None,
            source_sha256=None,
            sanitized=False,
        )
    )
    payload.sort(key=lambda item: item.path.as_posix())

    status = run_git(repo_root, "status", "--porcelain", "--untracked-files=all").splitlines()
    for item in payload:
        if item.source_path is None:
            continue
        source = repo_root / Path(item.source_path)
        if (
            not source.is_file()
            or source.stat().st_size != item.source_bytes
            or sha256_file(source) != item.source_sha256
        ):
            raise RuntimeError(f"input changed during bundle snapshot: {item.source_path}")
    return payload, status


def manifest_bytes(
    payload: list[PayloadFile], git_info: dict[str, str], status: list[str]
) -> bytes:
    entries = []
    for item in payload:
        entries.append(
            {
                "path": item.path.as_posix(),
                "bytes": len(item.data),
                "sha256": sha256_bytes(item.data),
                "role": item.role,
                "origin": item.origin,
                "source_path": item.source_path,
                "source_bytes": item.source_bytes,
                "source_sha256": item.source_sha256,
                "sanitized_copy": item.sanitized,
            }
        )
    included_dirty = []
    excluded_dirty = []
    for line in status:
        path = line[3:].replace("\\", "/") if len(line) >= 4 else line
        if path.startswith("ta-Taml-IN/"):
            relative = PurePosixPath(path[len("ta-Taml-IN/") :])
            if is_active_or_excluded_project_path(relative):
                excluded_dirty.append(path)
            else:
                included_dirty.append(path)
        else:
            excluded_dirty.append("[root coordination or unrelated path omitted]")
    excluded_dirty = sorted(set(excluded_dirty))

    manifest = {
        "schema": SCHEMA,
        "locale": "ta-Taml-IN",
        "bundle_date": BUNDLE_DATE,
        "source_checkpoint": git_info,
        "payload_totals": {
            "files": len(entries),
            "bytes": sum(entry["bytes"] for entry in entries),
        },
        "files": entries,
        "working_tree": {
            "included_changes": sorted(included_dirty),
            "excluded_changes": excluded_dirty,
            "meaning": (
                "The manifest binds every bundled byte. Git HEAD identifies the base checkpoint; "
                "included working-tree changes are exact snapshot bytes, not implied commits."
            ),
        },
        "sanitization": {
            "source_bytes_preserved_by_default": True,
            "text_copies_with_private task IDs, personal home roots, or excluded root instruction filenames": (
                "rewritten only in bundle copy; each entry retains source hash and sanitized_copy=true"
            ),
            "forbidden_bundle_inputs": [
                "raw chats",
                "credentials",
                "personal account/host/task identifiers",
                "root instruction and coordination records",
                "private user-update text",
                "unused bulk corpora",
                "active U020 and m81244 missing-answer drafts",
                "unreleased m81243 PDF lane and raster/cache outputs",
            ],
        },
        "control_file_identity": {
            "manifest_scope": "payload files only; HANDOFF-RESTART.md and checksum controls are excluded",
            "method": (
                "SHA-256 of this UTF-8 JSON is recorded inside HANDOFF-RESTART.md and as the "
                "manifest.json line of MANIFEST.sha256. MANIFEST.sha256 intentionally does not hash itself."
            ),
        },
    }
    return (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def handoff_bytes(
    payload: list[PayloadFile], git_info: dict[str, str], manifest_sha256: str, status: list[str]
) -> bytes:
    included_changes = []
    excluded_changes = []
    for line in status:
        path = line[3:].replace("\\", "/") if len(line) >= 4 else line
        if path.startswith("ta-Taml-IN/"):
            relative = PurePosixPath(path[len("ta-Taml-IN/") :])
            target = (
                excluded_changes
                if is_active_or_excluded_project_path(relative)
                else included_changes
            )
            target.append(path)
        else:
            excluded_changes.append("root coordination/private operational files (not bundled)")
    included_text = "\n".join(f"  - `{p}`" for p in sorted(set(included_changes))) or "  - none"
    excluded_text = "\n".join(f"  - `{p}`" for p in sorted(set(excluded_changes))) or "  - none"
    payload_bytes = sum(len(item.data) for item in payload)
    handoff = f"""# ta-Taml-IN takeover and restart

Bundle date: {BUNDLE_DATE}  
Locale: `ta-Taml-IN` (Indian Tamil)  
Assignment: teacher-independent Grades 2–8 numeracy recovery from A00–A20 plus AX-1/AX-3.

## Immutable checkpoint and bundle identity

- Branch: `{git_info['branch']}`
- Git HEAD/base checkpoint: `{git_info['head']}`
- Parent: `{git_info['parent']}`
- Tree: `{git_info['tree']}`
- Payload manifest: `manifest.json`
- Exact `manifest.json` SHA-256: `{manifest_sha256}`
- Manifested payload: {len(payload):,} files / {payload_bytes:,} bytes.
- `MANIFEST.sha256` hashes the manifest, this handoff, and every payload file. It intentionally does not hash itself; the builder/checker prints that checksum file's external SHA-256.

Run this first from the bundle root:

```text
python -X utf8 project/ta-Taml-IN/scripts/build_takeover_bundle.py --verify-bundle .
```

That command is read-only. It verifies every checksum, the sorted machine manifest, payload totals, sanitation markers, and control-file identity.

## Governing durable state

Read, in order:

1. `project/ta-Taml-IN/GOAL.md` — persistent approximately-3,000-character core goal plus later clarifications.
2. `project/ta-Taml-IN/NEXT_UNIT.md` — exact continuation cursor and historical checkpoints.
3. `project/ta-Taml-IN/DECISIONS.md` and `project/ta-Taml-IN/qa/STATUS.md` — evidence-backed decisions and limitations.
4. `project/ta-Taml-IN/canon/README.md`, `canon/CONSULTATION_LOG.md`, and the actual bytes under `source-material/tamil-canon/` — continual readable-canon loop.
5. `project/ta-Taml-IN/sources.lock.json`, `SOURCE-MATERIAL-INDEX.json`, provenance witnesses, and `terminology.tsv`.

The private root task transcript and raw instruction/coordination files are intentionally absent. Their durable, non-private operational effect is: continue the whole assigned translation; treat summaries as untrusted until disk/Git are checked; consult actual readable Tamil canon at drafting, revision, and QA; log decisions; make coherent checkpoints; do not claim publication, native review, curriculum validity, efficacy, or full completion without evidence.

## Coverage ledger at takeover

| Program span | Exact state |
|---|---|
| A00 `m81243` | Complete source-faithful Tamil module: 2,122 elements, 628 IDs, 249 MathML roots, 88 exercises, 59 source solutions and 29 preserved source omissions. The corrected `reader-m81243-review` and integrated `reader-m81243-learning` are included; the latter has seven labelled companions, 75 answered new items and 58 source-exercise supports. |
| A00 `m81244` | Complete source-review package: 14 fragments, 50 SVGs, 3,576 elements, 756 IDs, 401 MathML roots, 129 exercises and 89 source solutions. Forty source omissions remain. Addition-core (16 items) and phrase/application (12 items) companions are included and source-level admitted, but no integrated learner HTML/EPUB/PDF or complete mastery/retry route exists. |
| A00 `m81245` | Only U019 `fs-id1799687` is admitted: 133 elements, 28 IDs, 14 MathML roots, three supplied solutions, one 2×5 table, zero media. |
| A00 next | Exact next contiguous source is `m81245#fs-id1824154`, Model Subtraction of Whole Numbers (U020). Any live U020 draft was excluded because it had not crossed the coherent admission boundary. |
| Remaining A00 | Later m81245 spans and subsequent A00 modules remain unstarted or unadmitted. Preface/chapter-opening gaps recorded in project state also remain. |
| A10 and A20 | Source pins/collection/license provenance are included; Tamil translation has not begun. Large release archives are omitted as unused bulk and exactly reacquirable from `SOURCE-MATERIAL-INDEX.json`. |
| AX-1 / AX-3 | Partially embodied in semantic/offline m81243 readers and labelled explanations/recovery companions. The full cross-module, full-course accessibility and teacher-independent recovery system is incomplete. |

This is a takeover checkpoint, not a release, publication, rank-evidence claim, or completion of the assignment.

## Next safe work cursor

1. Reread the actual English/Indonesian m81245 witnesses under `source-material/openstax/m81245/`, then relevant real OCR+PNG canon pages (subtraction reviewers used pages 007, 008, 011, 012, 020, 028, 030–038 and 175).
2. Continue U020 from direct sibling `m81245#fs-id1824154`; preserve IDs, hierarchy, MathML, operators, numbers, supplied solutions and media identity. Keep new explanations and missing-answer work separate.
3. Independently review and admit U020 before assembly. Expand canon only if the topic needs evidence not in the included targeted set.
4. Separately finish m81244 answer completion, reasoning, diagnostic/remediation/mastery/retry routing, then deterministic HTML/EPUB and rendered QA. The active missing-answer draft at checkpoint time was excluded.
5. Reconstruct/finalize the m81243 PDF lane from corrected reader inputs only after the excluded active repair is safely checkpointed; do not reuse stale PDF receipts.

## Deterministic build and QA commands

Run from the bundle root. All paths are relative and avoid a personal home directory:

```text
python -X utf8 project/ta-Taml-IN/scripts/assemble_m81243.py --check
python -X utf8 project/ta-Taml-IN/scripts/build_m81243_review.py --check
python -X utf8 project/ta-Taml-IN/scripts/build_m81243_learning.py --check
python -X utf8 project/ta-Taml-IN/scripts/assemble_m81244.py --check-only
python -X utf8 project/ta-Taml-IN/scripts/assemble_m81244.py --check
python -X utf8 project/ta-Taml-IN/scripts/qa_recovery_addition_phrases_applications.py --check
python -X utf8 project/ta-Taml-IN/scripts/qa_u002.py
```

These scripts resolve their inputs relative to their own project directory. Run EPUBCheck 5.3.0 independently against included EPUBs where the QA notes require it. Browser/visual checks are human evidence and are not recreated by a structural script.

## Runtime and dependency record

- Bundle construction/checking: Python 3.12.13 tested; standard library only. Python 3.12.10 also existed on PATH.
- XML/build gates: Python standard library, UTF-8 mode (`-X utf8`).
- EPUB conformance: EPUBCheck 5.3.0; tested with Java 15.0.2. Tool bytes are not bundled; official release locator is in `SOURCE-MATERIAL-INDEX.json`.
- Tamil OCR: Tesseract 5.5.0.20241111; exact `tam.traineddata` SHA-256 `d02fbec24be4b07e32e80d0ccfc3b6b67a3c5d61c9d0a7c8532677990912c6ec` is bundled.
- PDF logical text: Poppler `pdftotext` 25.07.0. Page rendering observed with `pdftoppm` 26.05.0.
- Repository utilities: Git 2.55.0.windows.1 and ripgrep 15.1.0 were present. They are not bundle payloads.
- PDF creation/browser inspection needs a modern Chromium-family print engine plus the bundled Noto Sans Tamil font. No browser binary or personal profile is included.

## Source/canon rebuild and acquisition

- Exact used source XML/media bytes and all Tamil canon OCR/PNG bytes are present. No network is required for the admitted source checks.
- The complete canon PDF is included at `source-material/tamil-canon/tn-scert-6-term1-maths-2018.pdf`; preserve its original bytes. To regenerate targeted OCR, use `project/ta-Taml-IN/scripts/ocr_canon.py` with Tesseract/Poppler and the bundled traineddata, then compare hashes before replacing evidence.
- Large unused archive/repository checkouts are not included. `SOURCE-MATERIAL-INDEX.json` records their URLs, commits/versions, byte counts and hashes. Download only when the next source span actually needs material not already included; verify the recorded SHA-256 before extraction.
- `project/ta-Taml-IN/provenance/` contains exact source/license/collection witnesses. Original referenced source media are under `source-material/openstax/`; Tamil SVG derivatives remain under the project asset directories.

## Known defects and hard limits

- No included artifact has native-speaker, Tamil educator, learner, current-board, placement-validity, efficacy, assistive-technology, Braille-math or PDF/UA approval.
- Cross-module terminology still needs qualified review, especially result `கூடுதல்` versus earlier project-used `கூட்டுத்தொகை`; arithmetic `கோவை`, addend wording, carrying language and some measurement headwords remain provisional as documented.
- Source omissions remain source omissions. Never insert companion answers into canonical CNXML or fabricate a canonical answer for the open reflection.
- The m81244 confidence chart is self-estimate only, never a mastery gate.
- The current m81243 PDF repair/export/review lane is intentionally absent. Known repair involved answer-opening pagination and final full-page review. Rebuild with fresh identities and QA; do not cite any stale candidate.
- Historical U001 generated reader/PDF outputs are absent because their number-line redraw lacked the upper-right arrowhead. Corrected source asset and current m81243 readers are present. U002 print/screen PDFs are included because their exact verified hashes are `ad7652a4ea6f75625a4a3ec002b8542f891a17e0abc37f4aa78aa6fc8d5ef4e0` and `8506af70826e548f430e51a3d1e9f647be24d581597256233ea3ca4f7d525f90`.
- Before m81293 use, preserve intended `0.04` and `0.40 > 0.04` while independently checking the reported plot-position error. Before A20 m81373 figures, independently inspect the documented source discrepancies. Private cross-lane evidence paths were removed from bundle copies.
- OCR is readable register evidence, not mathematical source truth. Resolve spelling, operators and alignment against the included PNG/PDF.

## Working-tree snapshot and exclusions

Bundled changes beyond the stated Git base, if any, are exact byte snapshots listed in `manifest.json`:
{included_text}

Dirty paths deliberately excluded from the bundle:
{excluded_text}

In addition, raw chats, credentials, private account/host/task identifiers, root coordination/instruction records, private user-update text, browser profiles, caches, `tmp/` rasters, broken/transient PDFs, unused repository clones and large archives are absent. Active U020 and m81244 missing-answer authors must make separate coherent checkpoints; their exclusion here is deliberate and recorded so another PC does not mistake partial bytes for admitted work.

## Checkpoint safety boundary

The directory is safe for coordinator capture after `--verify-bundle` passes. It is a sanitized review/takeover snapshot only. It must not be merged to main, released, publicly certified, or described as complete without the unfinished work and human-review limits above.
"""
    return handoff.encode("utf-8")


def build_expected(repo_root: Path) -> tuple[dict[PurePosixPath, bytes], dict[str, object]]:
    git_info = git_identity(repo_root)
    payload, status = collect_payload(repo_root)
    if git_identity(repo_root) != git_info:
        raise RuntimeError("Git checkpoint changed during bundle snapshot; rerun at a safe boundary")
    manifest = manifest_bytes(payload, git_info, status)
    manifest_sha = sha256_bytes(manifest)
    handoff = handoff_bytes(payload, git_info, manifest_sha, status)
    files: dict[PurePosixPath, bytes] = {item.path: item.data for item in payload}
    files[PurePosixPath("manifest.json")] = manifest
    files[PurePosixPath("HANDOFF-RESTART.md")] = handoff
    checksum_paths = [PurePosixPath("manifest.json"), PurePosixPath("HANDOFF-RESTART.md")]
    checksum_paths.extend(item.path for item in payload)
    lines = [
        f"{sha256_bytes(files[path])}  {path.as_posix()}\n"
        for path in sorted(set(checksum_paths), key=lambda p: p.as_posix())
    ]
    checksums = "".join(lines).encode("utf-8")
    files[PurePosixPath("MANIFEST.sha256")] = checksums
    meta = {
        "git": git_info,
        "payload_files": len(payload),
        "payload_bytes": sum(len(item.data) for item in payload),
        "bundle_files": len(files),
        "bundle_bytes": sum(len(data) for data in files.values()),
        "manifest_sha256": manifest_sha,
        "checksums_sha256": sha256_bytes(checksums),
        "sanitized_files": sum(1 for item in payload if item.sanitized),
    }
    return files, meta


def validate_relative_path(path: PurePosixPath) -> None:
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise RuntimeError(f"unsafe output path: {path}")


def write_bundle(output: Path, expected: dict[PurePosixPath, bytes]) -> None:
    if output.exists():
        raise FileExistsError(
            f"refusing to overwrite existing bundle: {output}; use --check or a distinct --output"
        )
    output.mkdir(parents=True, exist_ok=False)
    for relative, data in sorted(expected.items(), key=lambda item: item[0].as_posix()):
        validate_relative_path(relative)
        destination = output.joinpath(*relative.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)


def compare_bundle(output: Path, expected: dict[PurePosixPath, bytes]) -> None:
    if not output.is_dir():
        raise FileNotFoundError(f"bundle directory does not exist: {output}")
    actual_paths = {
        PurePosixPath(path.relative_to(output).as_posix())
        for path in output.rglob("*")
        if path.is_file()
    }
    expected_paths = set(expected)
    if actual_paths != expected_paths:
        missing = sorted(p.as_posix() for p in expected_paths - actual_paths)
        extra = sorted(p.as_posix() for p in actual_paths - expected_paths)
        raise RuntimeError(f"bundle file-set mismatch; missing={missing}; extra={extra}")
    for relative, data in sorted(expected.items(), key=lambda item: item[0].as_posix()):
        actual = output.joinpath(*relative.parts).read_bytes()
        if actual != data:
            raise RuntimeError(f"bundle byte mismatch: {relative}")


def verify_existing_bundle(bundle: Path) -> dict[str, object]:
    bundle = bundle.resolve()
    checksum_path = bundle / "MANIFEST.sha256"
    manifest_path = bundle / "manifest.json"
    handoff_path = bundle / "HANDOFF-RESTART.md"
    if not checksum_path.is_file() or not manifest_path.is_file() or not handoff_path.is_file():
        raise FileNotFoundError("bundle control files are incomplete")
    checksum_lines = checksum_path.read_text(encoding="utf-8").splitlines()
    recorded: dict[str, str] = {}
    for line in checksum_lines:
        match = re.fullmatch(r"([0-9a-f]{64})  ([^\r\n]+)", line)
        if not match:
            raise RuntimeError(f"invalid checksum line: {line!r}")
        digest, path_text = match.groups()
        relative = PurePosixPath(path_text)
        validate_relative_path(relative)
        if path_text in recorded:
            raise RuntimeError(f"duplicate checksum path: {path_text}")
        recorded[path_text] = digest
        path = bundle.joinpath(*relative.parts)
        if not path.is_file():
            raise FileNotFoundError(f"checksummed file is absent: {path_text}")
        if sha256_file(path) != digest:
            raise RuntimeError(f"checksum mismatch: {path_text}")
    actual_files = {
        path.relative_to(bundle).as_posix()
        for path in bundle.rglob("*")
        if path.is_file() and path.name != "MANIFEST.sha256"
    }
    if actual_files != set(recorded):
        raise RuntimeError(
            "checksum file-set mismatch; "
            f"missing={sorted(set(recorded)-actual_files)}; extra={sorted(actual_files-set(recorded))}"
        )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != SCHEMA:
        raise RuntimeError("unexpected manifest schema")
    entries = manifest.get("files")
    if not isinstance(entries, list):
        raise RuntimeError("manifest files is not a list")
    entry_paths = [entry["path"] for entry in entries]
    if entry_paths != sorted(entry_paths) or len(entry_paths) != len(set(entry_paths)):
        raise RuntimeError("manifest paths are not sorted and unique")
    for entry in entries:
        path_text = entry["path"]
        relative = PurePosixPath(path_text)
        validate_relative_path(relative)
        path = bundle.joinpath(*relative.parts)
        if not path.is_file():
            raise FileNotFoundError(f"manifested payload is absent: {path_text}")
        if path.stat().st_size != entry["bytes"] or sha256_file(path) != entry["sha256"]:
            raise RuntimeError(f"manifest payload mismatch: {path_text}")
    totals = manifest.get("payload_totals", {})
    if totals.get("files") != len(entries) or totals.get("bytes") != sum(
        entry["bytes"] for entry in entries
    ):
        raise RuntimeError("manifest payload totals mismatch")
    manifest_sha = sha256_file(manifest_path)
    handoff = handoff_path.read_text(encoding="utf-8")
    if manifest_sha not in handoff:
        raise RuntimeError("handoff does not bind the exact manifest hash")
    forbidden = [
        PRIVATE_TASK_ID,
        "codex://threads/",
        "C:/Users/",
        "C:\\Users\\",
        "USER_INSTRUCTIONS_VERBATIM.md",
        "FULL_ASSIGNMENT_USER_INSTRUCTION.md",
        "COORDINATING_TASK.md",
    ]
    for path_text in sorted(recorded):
        path = bundle.joinpath(*PurePosixPath(path_text).parts)
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for needle in forbidden:
            if needle in text:
                raise RuntimeError(f"forbidden private locator {needle!r} remains in {path_text}")
    return {
        "bundle": str(bundle),
        "files": len(actual_files) + 1,
        "bytes": sum(path.stat().st_size for path in bundle.rglob("*") if path.is_file()),
        "manifest_sha256": manifest_sha,
        "checksums_sha256": sha256_file(checksum_path),
        "checksummed_files": len(recorded),
        "payload_files": len(entries),
        "payload_bytes": totals["bytes"],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        help=f"bundle directory (default: takeover/{BUNDLE_NAME})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare the existing output with freshly derived expected bytes; never write",
    )
    parser.add_argument(
        "--plan",
        action="store_true",
        help="derive and report identities/counts without writing",
    )
    parser.add_argument(
        "--verify-bundle",
        type=Path,
        help="verify an existing self-contained bundle from its manifest/checksums",
    )
    args = parser.parse_args(argv)
    selected = sum(bool(value) for value in (args.check, args.plan, args.verify_bundle))
    if selected > 1:
        parser.error("choose only one of --check, --plan, or --verify-bundle")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.verify_bundle:
        result = verify_existing_bundle(args.verify_bundle)
        print(json.dumps({"status": "verified", **result}, ensure_ascii=False, sort_keys=True))
        return 0

    repo_root = Path(__file__).resolve().parents[2]
    output = (args.output or (repo_root / "takeover" / BUNDLE_NAME)).resolve()
    expected, meta = build_expected(repo_root)
    if args.plan:
        print(json.dumps({"status": "planned", "output": str(output), **meta}, sort_keys=True))
        return 0
    if args.check:
        compare_bundle(output, expected)
        verified = verify_existing_bundle(output)
        print(json.dumps({"status": "checked", **meta, **verified}, ensure_ascii=False, sort_keys=True))
        return 0
    write_bundle(output, expected)
    verified = verify_existing_bundle(output)
    print(json.dumps({"status": "built", **meta, **verified}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
