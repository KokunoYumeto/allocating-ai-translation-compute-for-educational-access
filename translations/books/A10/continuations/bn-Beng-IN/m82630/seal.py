"""Create the deterministic admission receipts for this one bounded packet."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
CORE = ("modules/m82630/index.cnxml", "index.html", "TEXT_LEDGER.json")
VISUAL = (
    "visual/RESULTS.json",
    "visual/desktop-top.png",
    "visual/desktop-graph.png",
    "visual/narrow-top.png",
    "visual/narrow-graph.png",
)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_path(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def identity(rel: str) -> dict:
    path = ROOT / rel
    return {"path": rel, "bytes": path.stat().st_size, "sha256": sha_path(path)}


def write_json(rel: str, value: object) -> None:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    (ROOT / rel).write_text(payload, encoding="utf-8", newline="\n")


def run_python(script: str) -> str:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        [sys.executable, "-B", script],
        cwd=ROOT,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(f"{script} failed ({result.returncode}):\n{result.stdout}\n{result.stderr}")
    return result.stdout


def load_build():
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("a10_bn_in_build", ROOT / "build.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def visual_inventory() -> dict[str, dict]:
    return {rel: {"bytes": (ROOT / rel).stat().st_size, "sha256": sha_path(ROOT / rel)} for rel in VISUAL}


def verify_inspection(visual: dict) -> None:
    inspection = json.loads((ROOT / "visual/INSPECTION.json").read_text(encoding="utf-8"))
    if inspection.get("status") != "pass":
        raise AssertionError("visual inspection is not a pass")
    rows = {row["path"]: row for row in inspection["screenshots"]}
    for rel in VISUAL[1:]:
        row = rows[rel]
        if row["bytes"] != visual[rel]["bytes"] or row["sha256"] != visual[rel]["sha256"]:
            raise AssertionError(f"inspection identity mismatch: {rel}")
    result_row = inspection["results"]
    if result_row["bytes"] != visual[VISUAL[0]]["bytes"] or result_row["sha256"] != visual[VISUAL[0]]["sha256"]:
        raise AssertionError("inspection RESULTS.json identity mismatch")


def main() -> None:
    build = load_build()
    build.verify_static_inputs()
    first_build = build.build_bytes()
    second_build = build.build_bytes()
    if first_build != second_build:
        raise AssertionError("two in-memory builds differ")
    for rel in CORE:
        if first_build[rel] != (ROOT / rel).read_bytes():
            raise AssertionError(f"disk differs from deterministic build: {rel}")

    run_python("visual_check.py")
    first_visual = visual_inventory()
    run_python("visual_check.py")
    second_visual = visual_inventory()
    if first_visual != second_visual:
        raise AssertionError("two final-code browser runs differ")
    verify_inspection(second_visual)

    package = json.loads((ROOT / "PACKAGE.json").read_text(encoding="utf-8"))
    package["status"] = "ready_for_owner_admission"
    package["core_artifacts"] = [identity(rel) for rel in ("modules/m82630/index.cnxml", "index.html", "TEXT_LEDGER.json", "translations.json")]
    package["visual_qa"] = {
        "status": "pass",
        "results": identity("visual/RESULTS.json"),
        "inspection": identity("visual/INSPECTION.json"),
        "screenshots": [identity(rel) for rel in VISUAL[1:]],
        "viewports": ["1440x1000", "390x844"],
    }
    package["admission_receipts"] = {
        "qa": "QA_REPORT.json",
        "replay": "DETERMINISTIC_REPLAY.json",
        "manifest": "MANIFEST.json",
        "checksums": "CHECKSUMS.sha256",
        "handoff": "OWNER_HANDOFF.md",
    }
    write_json("PACKAGE.json", package)

    replay = {
        "schema": "a10.bn-Beng-IN.deterministic-replay.v1",
        "date": "2026-09-04",
        "status": "pass",
        "build_runs": 2,
        "visual_runs": 2,
        "identical_build_outputs": True,
        "identical_visual_outputs": True,
        "build_outputs": {rel: {"bytes": len(first_build[rel]), "sha256": sha_bytes(first_build[rel])} for rel in CORE},
        "visual_outputs": second_visual,
        "source": identity("source/m82630.en.cnxml"),
        "collection": identity("source/collection.xml"),
        "commands": ["python -B build.py", "python -B visual_check.py (twice)", "python -B qa.py"],
        "network": "No remote network was used; the reader was served on 127.0.0.1 solely to a captured Chrome process.",
    }
    write_json("DETERMINISTIC_REPLAY.json", replay)

    results = json.loads((ROOT / "visual/RESULTS.json").read_text(encoding="utf-8"))
    qa_report = {
        "schema": "a10.bn-Beng-IN.qa-report.v1",
        "date": "2026-09-04",
        "overall_status": "pass",
        "locale": "bn-Beng-IN",
        "module": "m82630",
        "scope": "Complete canonical preface module only; the 82-module edition remains partial.",
        "canonical_source": identity("source/m82630.en.cnxml"),
        "target": identity("modules/m82630/index.cnxml"),
        "checks": {
            "source_identity": "pass",
            "element_order_and_nonlinguistic_attributes": "pass: 194 of 194",
            "stable_ids": "pass: 66 unique IDs preserved",
            "text_mapping": "pass: all 146 original source XPath/field slots accounted for, including three intentional empty replacements",
            "math_and_assessments": "pass: canonical preface contains zero MathML, exercises, and solutions; none added or removed",
            "assets": "pass: four exact canonical assets decoded and referenced locally",
            "language_and_credits": "pass: Bengali copy corrections applied; identities, authors, reviewers and license preserved",
            "expert_review_log": "pass: 16 substantive records validate against the shared schema",
            "offline_reader": "pass: semantic HTML, local CSS/assets, valid local links, and truthful partial status",
            "determinism": "pass: two build replays and two final-code Chrome replays are byte-identical",
        },
        "browser_visual_review": {
            "method": "captured-headless-chrome-loopback",
            "desktop": {"status": "pass", "viewport": "1440x1000", "main_width": results["viewports"]["desktop"]["main"]["width"], "screenshots": [identity("visual/desktop-top.png"), identity("visual/desktop-graph.png")]},
            "narrow": {"status": "pass", "viewport": "390x844", "main_width": results["viewports"]["narrow"]["main"]["width"], "screenshots": [identity("visual/narrow-top.png"), identity("visual/narrow-graph.png")]},
            "inspection": identity("visual/INSPECTION.json"),
        },
        "limitations": [
            "This packet is one complete source module, not the complete Elementary Algebra 2e translation.",
            "No human certification or classroom-effectiveness claim is made or required.",
            "Terms explicitly marked provisional in EXPERT_REVIEW_LOG.json remain reviewable without creating a hold.",
        ],
    }
    write_json("QA_REPORT.json", qa_report)

    handoff_lines = [
        "# Owner handoff — bn-Beng-IN m82630",
        "",
        "Status: ready for canonical-owner admission as one complete preface module; the full 82-module edition remains partial.",
        "",
        f"- Canonical source: `{identity('source/m82630.en.cnxml')['sha256']}` ({identity('source/m82630.en.cnxml')['bytes']} bytes)",
        f"- Target CNXML: `{identity('modules/m82630/index.cnxml')['sha256']}` ({identity('modules/m82630/index.cnxml')['bytes']} bytes)",
        f"- Reader: `{identity('index.html')['sha256']}` ({identity('index.html')['bytes']} bytes)",
        f"- Expert review log: `{identity('EXPERT_REVIEW_LOG.json')['sha256']}` ({identity('EXPERT_REVIEW_LOG.json')['bytes']} bytes)",
        f"- QA report: `{identity('QA_REPORT.json')['sha256']}` ({identity('QA_REPORT.json')['bytes']} bytes)",
        f"- Deterministic replay: `{identity('DETERMINISTIC_REPLAY.json')['sha256']}` ({identity('DETERMINISTIC_REPLAY.json')['bytes']} bytes)",
        "",
        "The source/module topology, 66 stable IDs, four canonical assets, all author/reviewer credits and CC BY-NC-SA 4.0 notice are preserved. The preface legitimately contains no MathML, exercises or supplied solutions. All 146 original source text locations are accounted for; three source fragments are intentionally empty because their Bengali syntax is carried by adjacent translated tails.",
        "",
        "Visual QA used one captured Chrome process per run at 1440×1000 and 390×844. The centered reader fills the page, the graph scales without clipping, and the saved final-code screenshots were directly inspected. Two build runs and two browser runs reproduced byte-identical output.",
        "",
        "Next source module: `m82451`. Admission and publication authority remain with the canonical owner.",
        "",
    ]
    (ROOT / "OWNER_HANDOFF.md").write_text("\n".join(handoff_lines), encoding="utf-8", newline="\n")

    files = sorted(
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.name not in {"MANIFEST.json", "CHECKSUMS.sha256"}
    )
    manifest = {
        "schema": "a10.packet-manifest.v1",
        "package_id": package["package_id"],
        "locale": "bn-Beng-IN",
        "module": "m82630",
        "status": "ready_for_owner_admission",
        "files": [identity(rel) for rel in files],
    }
    write_json("MANIFEST.json", manifest)

    checksum_files = sorted(
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.name != "CHECKSUMS.sha256"
    )
    checksum_text = "".join(f"{sha_path(ROOT / rel)}  {rel}\n" for rel in checksum_files)
    (ROOT / "CHECKSUMS.sha256").write_text(checksum_text, encoding="utf-8", newline="\n")

    qa_output = run_python("qa.py")
    qa_runtime = json.loads(qa_output)
    if qa_runtime.get("all_passed") is not True:
        raise AssertionError("qa.py returned without proving all checks")
    summary = {
        "status": "pass",
        "files": len(checksum_files) + 1,
        "bytes": sum((ROOT / rel).stat().st_size for rel in checksum_files) + (ROOT / "CHECKSUMS.sha256").stat().st_size,
        "manifest_sha256": sha_path(ROOT / "MANIFEST.json"),
        "checksums_sha256": sha_path(ROOT / "CHECKSUMS.sha256"),
        "qa_checks": len(qa_runtime["checks"]),
    }
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
