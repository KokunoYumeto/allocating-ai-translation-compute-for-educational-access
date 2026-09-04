"""Deterministically seal the bounded A10-009 Shahmukhi reader packet.

The manifest inventories every payload byte but excludes the three sealing
envelope files to avoid hash cycles. CHECKSUMS.sha256 covers the manifest,
handoff and every payload file; by convention it cannot cover itself.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys


B = Path(__file__).resolve().parent
ENVELOPE = {"MANIFEST.json", "CHECKSUMS.sha256", "OWNER_HANDOFF.md"}


def require(value: object, message: str) -> None:
    if not value:
        raise AssertionError(message)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def rel(path: Path) -> str:
    return path.relative_to(B).as_posix()


def payload_paths() -> list[Path]:
    paths = []
    for path in B.rglob("*"):
        if not path.is_file():
            continue
        relative = rel(path)
        require("__pycache__" not in path.parts and path.suffix != ".pyc", "transient Python cache in packet: " + relative)
        require(not relative.endswith(".tmp"), "temporary file in packet: " + relative)
        if relative not in ENVELOPE:
            paths.append(path)
    return sorted(paths, key=rel)


def record(path: str, data: bytes) -> dict:
    return {"path": path, "bytes": len(data), "sha256": sha(data)}


def atomic_write(name: str, data: bytes) -> None:
    target = B / name
    temporary = B / (name + ".tmp")
    if temporary.exists():
        temporary.unlink()
    temporary.write_bytes(data)
    temporary.replace(target)


def main() -> None:
    required = [
        "PACKAGE.json",
        "QA.json",
        "index.html",
        "reader.css",
        "build.py",
        "verify.py",
        "visual_check.py",
        "visual/RESULTS.json",
        "visual/INSPECTION.json",
        "EXPERT_REVIEW_LOG.json",
        "source/SELECTION.json",
        "source/m82453.en.cnxml",
        "source/a10-unit-009.cnxml",
        "source/collection.xml",
    ]
    require(all((B / name).is_file() for name in required), "required packet file absent")
    require(not (B / "target").exists(), "unexpected target directory; packet scope must be reviewed")
    require(not (B / "backend").exists(), "unexpected backend directory; packet scope must be reviewed")

    # Run the independent verifier again at seal time. It itself performs two
    # byte-identical builds and binds the final browser/inspection evidence.
    result = subprocess.run(
        [sys.executable, str(B / "verify.py")],
        cwd=B,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    verifier_line = result.stdout.strip().splitlines()[-1]
    verifier_result = json.loads(verifier_line)
    require(verifier_result["checks"] >= 1300, "independent verifier check count regressed")

    package = json.loads((B / "PACKAGE.json").read_bytes())
    qa = json.loads((B / "QA.json").read_bytes())
    visual = json.loads((B / "visual/RESULTS.json").read_bytes())
    inspection = json.loads((B / "visual/INSPECTION.json").read_bytes())
    review = json.loads((B / "EXPERT_REVIEW_LOG.json").read_bytes())
    selection = json.loads((B / "source/SELECTION.json").read_bytes())
    require(qa["status"] == visual["status"] == inspection["status"] == "passed", "QA or visual status is not passed")
    require(len(review["entries"]) == 14, "expert-review decision count changed")
    require(sum(entry["rationale_timing"] == "retrospective_reconstruction" for entry in review["entries"]) == 13, "retrospective review count changed")
    require(any(entry["decision_id"] == "pnb-a10-009-responsive-figure-reflow" and entry["rationale_timing"] == "contemporaneous" for entry in review["entries"]), "responsive decision timing changed")
    require(package["coverage"]["selected_section_source_map_and_reader_complete"] is True, "bounded completion basis absent")
    require(package["coverage"]["translated_cnxml_target"].startswith("absent"), "target absence not explicit")
    require(package["coverage"]["modular_backend"].startswith("absent"), "backend absence not explicit")

    final_package = copy.deepcopy(package)
    final_package["packet_status"] = "sealed selected-section source-map/reader increment; awaiting canonical-owner admission"
    final_package_bytes = canonical_json(final_package)
    overrides = {"PACKAGE.json": final_package_bytes}

    payload_inventory = []
    for path in payload_paths():
        relative = rel(path)
        data = overrides.get(relative, path.read_bytes())
        payload_inventory.append(record(relative, data))
    require(len({item["path"] for item in payload_inventory}) == len(payload_inventory), "duplicate payload path")

    manifest = {
        "schema": "a10-section-packet-manifest-v1",
        "status": "sealed; awaiting canonical-owner admission",
        "date": "2026-09-04",
        "locale": "pnb-Arab-PK",
        "unit": "A10-009",
        "module": "m82453",
        "section": "fs-id1170655163482",
        "completion_basis": "complete selected-section source map and offline reader only; no translated CNXML target or modular backend is present or claimed",
        "source": {
            "collection": "col31130",
            "commit": package["source"]["commit"],
            "collection_sha256": package["source"]["collection_sha256"],
            "module_bytes": package["source"]["module_bytes"],
            "module_sha256": package["source"]["module_sha256"],
            "raw_section_sha256": package["source"]["raw_section_sha256"],
            "wrapped_excerpt_sha256": package["source"]["wrapped_excerpt_sha256"],
        },
        "coverage": {
            "source_ids": package["coverage"]["source_ids"],
            "source_bindings": package["coverage"]["source_bindings"],
            "source_blocks": package["coverage"]["source_text_and_alt_blocks"],
            "mathml_trees": package["coverage"]["mathml_trees"],
            "exercises": package["coverage"]["exercises_total"],
            "source_supplied_solutions": package["coverage"]["source_supplied_solutions"],
            "canonical_jpegs": package["coverage"]["canonical_jpegs"],
            "responsive_reconstructions": 3,
            "expert_review_entries": len(review["entries"]),
        },
        "qa": {
            "checks_passed": qa["checks_passed"],
            "negative_controls": qa["negative_controls"],
            "reader_sha256": qa["reader_sha256"],
            "visual_results_sha256": sha((B / "visual/RESULTS.json").read_bytes()),
            "visual_inspection_sha256": sha((B / "visual/INSPECTION.json").read_bytes()),
            "verifier_replay": verifier_result,
        },
        "next_anchor": selection["next_anchor"],
        "inventory_policy": "Every payload file is listed. MANIFEST.json, OWNER_HANDOFF.md and CHECKSUMS.sha256 form the sealing envelope and are excluded here to avoid hash cycles; CHECKSUMS.sha256 covers the manifest, handoff and every payload file except itself.",
        "file_count": len(payload_inventory),
        "total_bytes": sum(item["bytes"] for item in payload_inventory),
        "files": payload_inventory,
    }
    manifest_bytes = canonical_json(manifest)
    manifest_hash = sha(manifest_bytes)

    handoff_text = f"""# Owner handoff — pnb-Arab-PK A10-009 m82453

Status: **sealed locally; not admitted**. Canonical ownership, integration and publication remain with the owner task.

This packet completes exactly one source-ordered section, `fs-id1170655163482` (“Identify and Combine Like Terms”), as a source-bound Shahmukhi Punjabi offline reader and source map. It does **not** contain a translated CNXML `target/` or modular `backend/`, and it must not be counted as CNXML/backend, whole-module or whole-book completion.

## Frozen authority and coverage

- Collection: `col31130`, 82 ordered modules; SHA-256 `{package['source']['collection_sha256']}`.
- Repository commit: `{package['source']['commit']}`.
- Module `m82453`: {package['source']['module_bytes']:,} bytes; SHA-256 `{package['source']['module_sha256']}`.
- Raw section `[89018,108818)`: 19,800 bytes; SHA-256 `{package['source']['raw_section_sha256']}`.
- Wrapped excerpt: SHA-256 `{package['source']['wrapped_excerpt_sha256']}`.
- Preserved: 108 source IDs, 253 source bindings, 66 source text/alt blocks, 62 MathML trees, 12 exercises, 12 source-supplied solutions and three byte-identical canonical JPEGs.
- Responsive repair: the page shell fills desktop width; each 594px JPEG fits wholly at 390px without sideways scrolling; three separately marked semantic reconstructions preserve the exact expressions and make them readable at narrow width.
- Expert-review ledger: 14 decisions—13 honest retrospective backfills and one contemporaneous responsive-layout decision.
- Actual audio: absent and not claimed.

## Deterministic QA

- Independent verifier: {qa['checks_passed']:,} passed checks plus four rejected mutation controls.
- Reader SHA-256: `{qa['reader_sha256']}`.
- Visual results SHA-256: `{sha((B / 'visual/RESULTS.json').read_bytes())}`.
- Visual inspection SHA-256: `{sha((B / 'visual/INSPECTION.json').read_bytes())}`.
- Payload manifest: {len(payload_inventory)} files, {sum(item['bytes'] for item in payload_inventory):,} bytes; SHA-256 `{manifest_hash}`.
- `CHECKSUMS.sha256` covers every payload file plus this handoff and `MANIFEST.json`; it conventionally excludes itself.

Replay from this directory:

```text
python build.py
python visual_check.py
# inspect and bind the regenerated PNGs in visual/INSPECTION.json
python verify.py
python seal.py
```

The next exact source anchor is `{selection['next_anchor']}` (“{selection['next_title']}”).
"""
    handoff_bytes = handoff_text.encode("utf-8")

    checksum_material = {item["path"]: overrides.get(item["path"], (B / item["path"]).read_bytes()) for item in payload_inventory}
    checksum_material["MANIFEST.json"] = manifest_bytes
    checksum_material["OWNER_HANDOFF.md"] = handoff_bytes
    checksum_bytes = "".join(f"{sha(data)}  {path}\n" for path, data in sorted(checksum_material.items())).encode("utf-8")

    # Write the safety-status-changing PACKAGE last. A partial envelope write
    # therefore leaves the old explicit do-not-admit status in place.
    atomic_write("MANIFEST.json", manifest_bytes)
    atomic_write("OWNER_HANDOFF.md", handoff_bytes)
    atomic_write("CHECKSUMS.sha256", checksum_bytes)
    atomic_write("PACKAGE.json", final_package_bytes)

    for path, expected_data in checksum_material.items():
        actual = (B / path).read_bytes()
        require(actual == expected_data and sha(actual) == sha(expected_data), "sealed byte mismatch: " + path)
    checksum_lines = (B / "CHECKSUMS.sha256").read_text(encoding="utf-8").splitlines()
    require(len(checksum_lines) == len(checksum_material), "checksum line count mismatch")
    for line in checksum_lines:
        digest, path = line.split("  ", 1)
        require(sha((B / path).read_bytes()) == digest, "checksum verification failed: " + path)

    final_paths = sorted((path for path in B.rglob("*") if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"), key=rel)
    final_records = [record(rel(path), path.read_bytes()) for path in final_paths]
    aggregate = sha(json.dumps(final_records, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    print(json.dumps({
        "status": "sealed; awaiting canonical-owner admission",
        "final_file_count": len(final_records),
        "final_total_bytes": sum(item["bytes"] for item in final_records),
        "final_inventory_sha256": aggregate,
        "manifest_sha256": sha((B / "MANIFEST.json").read_bytes()),
        "checksums_sha256": sha((B / "CHECKSUMS.sha256").read_bytes()),
        "owner_handoff_sha256": sha((B / "OWNER_HANDOFF.md").read_bytes()),
        "reader_sha256": sha((B / "index.html").read_bytes()),
        "qa_sha256": sha((B / "QA.json").read_bytes()),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
