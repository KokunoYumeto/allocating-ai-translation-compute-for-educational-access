"""Seal the bounded, non-temporary packet inventory and owner handoff."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELF_OUTPUTS = {"MANIFEST.json", "CHECKSUMS.sha256", "OWNER_HANDOFF.json"}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def atomic_text(path: Path, text: str) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    temporary.replace(path)


def admitted_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if relative.parts[0] == "tmp" or "__pycache__" in relative.parts:
            continue
        if relative.as_posix() in SELF_OUTPUTS or path.name.endswith(".tmp"):
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(ROOT).as_posix())


qa = json.loads((ROOT / "QA.json").read_text(encoding="utf-8"))
browser = json.loads((ROOT / "BROWSER_QA.json").read_text(encoding="utf-8"))
audio = json.loads((ROOT / "audio/AUDIO.json").read_text(encoding="utf-8"))
package = json.loads((ROOT / "PACKAGE.json").read_text(encoding="utf-8"))
if qa.get("status") != "pass" or browser.get("status") != "pass":
    raise RuntimeError("QA and browser QA must pass before sealing")
if package.get("status") != "admit-ready":
    raise RuntimeError("PACKAGE.json is not marked admit-ready")
if set(audio.get("tracks", {})) != {"jv-academic", "jv-conversation"}:
    raise RuntimeError("Both Javanese audio tracks are required before sealing")

entries = []
for path in admitted_files():
    relative = path.relative_to(ROOT).as_posix()
    entries.append({"path": relative, "bytes": path.stat().st_size, "sha256": sha(path)})
manifest = {
    "schema": "a10.bounded-packet-manifest.v1",
    "date": "2026-09-04",
    "scope": "m82453/fs-id1170654942537",
    "status": "admit-ready",
    "exclusions": ["tmp/", "MANIFEST.json self-reference", "CHECKSUMS.sha256 self-reference", "OWNER_HANDOFF.json self-reference"],
    "file_count": len(entries),
    "total_bytes": sum(item["bytes"] for item in entries),
    "files": entries,
}
atomic_text(ROOT / "MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

checksum_lines = [f"{sha(ROOT / 'MANIFEST.json')}  MANIFEST.json"]
checksum_lines.extend(f"{item['sha256']}  {item['path']}" for item in entries)
atomic_text(ROOT / "CHECKSUMS.sha256", "\n".join(checksum_lines) + "\n")

handoff = {
    "schema": "a10.owner-handoff.v1",
    "date": "2026-09-04",
    "status": "ADMIT",
    "packet": str(ROOT),
    "scope": {
        "collection": "col31130",
        "module": "m82453",
        "section": "fs-id1170654942537",
        "truth": "one complete source section; not a complete module or book",
        "next_source_anchor": "fs-id1170655188891",
    },
    "coverage": {
        "source_slots_per_javanese_track": 206,
        "indonesian_bridge_revisions": 67,
        "source_ids": 106,
        "mathml_roots": 63,
        "exercises": 15,
        "supplied_solutions": 15,
        "figures": 3,
    },
    "authority": {
        "canonical_commit": "38cae454e644abf9f0a623e876994553881597c9",
        "source_section_sha256": "f8b281215e7630e8425e26bd28d54b26ed707fe9840bfb2edd417d40da666d9f",
        "indonesian_pivot_zip_sha256": "6f04e88387e8d4e6e710dddcebb8d41e952a315231d7e203d62170c6ad9f3456",
        "license": "CC-BY-NC-SA-4.0",
        "license_sha256": "ab1a44bbba58252630134574d7b2534813339240eb645825ffcc2487dbe8114a",
    },
    "validation": {
        "qa_file": "QA.json",
        "qa_sha256": sha(ROOT / "QA.json"),
        "qa_checks": f"{qa['passed_count']}/{qa['check_count']}",
        "browser_qa_file": "BROWSER_QA.json",
        "browser_qa_sha256": sha(ROOT / "BROWSER_QA.json"),
        "browser_checks": len(browser["checks"]),
        "visual_screenshots": len(browser["screenshots"]),
        "draft_build_replay": "byte-identical for 15 generated outputs",
    },
    "audio": {
        "status": audio["status"],
        "human_recording": False,
        "human_pronunciation_certification": False,
        "tracks": {track: {key: record[key] for key in ["file", "bytes", "sha256", "duration_seconds", "voice", "voice_locale", "narration_ssml_sha256"]} for track, record in audio["tracks"].items()},
    },
    "inventory": {
        "manifest_file": "MANIFEST.json",
        "manifest_sha256": sha(ROOT / "MANIFEST.json"),
        "payload_file_count": manifest["file_count"],
        "payload_total_bytes": manifest["total_bytes"],
        "checksums_file": "CHECKSUMS.sha256",
        "checksums_sha256": sha(ROOT / "CHECKSUMS.sha256"),
        "excluded_from_release": ["tmp/"],
    },
    "model": "OpenAI Codex gpt-5.6-sol, Ultra",
    "expert_review_truth": "no Javanese-speaking human expert or pronunciation assessor was consulted; all language/register/audio judgments remain provisional and reversible",
    "residual_limitations": [
        "Only section fs-id1170654942537 is complete; the remainder of m82453 and the book are outside this packet.",
        "Javanese terminology, register, pronunciation, dialect suitability, and intelligibility have not been human-certified.",
        "Synthetic-service regeneration is not promised to be byte-stable; admitted MP3 bytes are pinned by SHA-256.",
        "Canonical-owner integration and publication are intentionally outside this helper packet's write authority."
    ]
}
atomic_text(ROOT / "OWNER_HANDOFF.json", json.dumps(handoff, ensure_ascii=False, indent=2) + "\n")

# Read back every payload entry and the two inventory files after the transaction.
for item in manifest["files"]:
    path = ROOT / item["path"]
    if not path.is_file() or path.stat().st_size != item["bytes"] or sha(path) != item["sha256"]:
        raise RuntimeError(f"Manifest readback failed: {item['path']}")
if any(item["path"].startswith("tmp/") for item in manifest["files"]):
    raise RuntimeError("Temporary dependency content leaked into the manifest")
if len((ROOT / "CHECKSUMS.sha256").read_text(encoding="utf-8").splitlines()) != len(entries) + 1:
    raise RuntimeError("Checksum inventory line count mismatch")
print(f"Sealed {manifest['file_count']} payload files / {manifest['total_bytes']} bytes; owner handoff status ADMIT.")
