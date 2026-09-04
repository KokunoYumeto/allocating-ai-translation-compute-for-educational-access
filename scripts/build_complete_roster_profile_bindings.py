#!/usr/bin/env python3
"""Create an exhaustive, conservative roster/profile binding registry.

No name, code, territory, family, or script similarity is promoted to a direct
profile binding.  In the absence of an independently audited exact-standard
crosswalk, every roster row receives either an explicit no-direct-profile
status or a not-applicable-mode status.  The complete-roster predictive model
uses the FLORES profiles as calibration observations, not as relabelled target
measurements.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping


DEFAULT_ROSTER = Path("structured/SUCCESSOR_TARGET_ROSTER_v2.json")
DEFAULT_MEASUREMENTS = Path("structured/standardized_compute_measurement_profiles.csv")
DEFAULT_OUTPUT = Path("structured/complete_roster_compute_target_profile_bindings.csv")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical_sha256(value: Any) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def load_compute_module(base: Path):
    path = base / "scripts" / "build_complete_roster_compute_model.py"
    spec = importlib.util.spec_from_file_location("complete_roster_compute_model", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load complete-roster compute module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_rows(base: Path, roster_path: Path, measurement_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    module = load_compute_module(base)
    roster = json.loads(roster_path.read_text(encoding="utf-8"))
    if roster.get("schema") != "interlanguage/successor-target-roster/2.0.0":
        raise RuntimeError("unsupported successor target roster")
    measurements = read_csv(measurement_path)
    if len(measurements) != 203 or len({row["benchmark_profile_id"] for row in measurements}) != 203:
        raise RuntimeError("expected 203 unique direct calibration profiles")
    measurement_set_hashes = {row["profile_set_hash"] for row in measurements}
    if len(measurement_set_hashes) != 1:
        raise RuntimeError("measurement profile set hash is not uniform")

    rows: list[dict[str, Any]] = []
    for target in roster["roster_targets"]:
        feature = module.extract_target_features(target)
        applicable = feature["model_applicability_status"] == "MODEL_CONDITIONAL_APPLICABLE"
        row = {
            "successor_snapshot_id": roster["snapshot_id"],
            "successor_snapshot_payload_sha256": roster["snapshot_payload_sha256"],
            "successor_file_sha256": sha256_file(roster_path),
            "roster_target_id": feature["roster_target_id"],
            "roster_row_sha256": feature["source_target_row_sha256"],
            "production_applicable": str(feature["production_applicable"]).lower(),
            "model_applicability_status": feature["model_applicability_status"],
            "profile_binding_requirement": target["profile_binding_requirement"],
            "binding_status": (
                "EXPLICIT_NO_DIRECT_PROFILE_MODEL_CONDITIONAL"
                if applicable
                else "NOT_APPLICABLE_WRITTEN_TOKEN_MODEL"
            ),
            "profile_input_class": "NO_PROFILE" if applicable else "NOT_APPLICABLE_MODE",
            "profile_match_scope": "",
            "benchmark_profile_id": "",
            "direct_measurement_row_sha256": "",
            "measurement_profile_set_sha256": next(iter(measurement_set_hashes)),
            "calibration_profile_count": str(len(measurements)),
            "calibration_use": "FLORES_PROFILES_AS_MODEL_TRAINING_NOT_TARGET_BINDINGS",
            "unavailable_reason": (
                "no independently audited exact-standard target-to-profile crosswalk"
                if applicable
                else feature["not_applicable_reason"]
            ),
            "binding_prohibition": "NO_CODE_NAME_SCRIPT_TERRITORY_OR_FAMILY_SIMILARITY_PROMOTION",
        }
        row["binding_row_sha256"] = canonical_sha256(row)
        rows.append(row)
    rows.sort(key=lambda row: row["roster_target_id"])
    if len(rows) != int(roster["target_selector"]["all_binding_row_count"]):
        raise RuntimeError("binding row count does not equal frozen roster count")
    if len({row["roster_target_id"] for row in rows}) != len(rows):
        raise RuntimeError("duplicate roster target in binding registry")
    set_hash = canonical_sha256(rows)
    for row in rows:
        row["binding_set_sha256"] = set_hash
    receipt = {
        "schema": "interlanguage/complete-roster-profile-binding-receipt/1.0.0",
        "status": "PASS",
        "successor_snapshot_id": roster["snapshot_id"],
        "successor_file_sha256": sha256_file(roster_path),
        "measurement_profile_file_sha256": sha256_file(measurement_path),
        "rows": len(rows),
        "model_conditional_explicit_missing_rows": sum(
            row["binding_status"] == "EXPLICIT_NO_DIRECT_PROFILE_MODEL_CONDITIONAL" for row in rows
        ),
        "not_applicable_rows": sum(
            row["binding_status"] == "NOT_APPLICABLE_WRITTEN_TOKEN_MODEL" for row in rows
        ),
        "direct_binding_rows": 0,
        "binding_set_sha256": set_hash,
        "policy": "conservative explicit missing; calibration profiles are never relabelled as target measurements",
    }
    return rows, receipt


def write_rows(output: Path, rows: list[Mapping[str, Any]]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_suffix(output.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(tmp, output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=Path("."))
    parser.add_argument("--roster", type=Path, default=DEFAULT_ROSTER)
    parser.add_argument("--measurements", type=Path, default=DEFAULT_MEASUREMENTS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--receipt",
        type=Path,
        default=Path("qa/COMPLETE_ROSTER_PROFILE_BINDING_RECEIPT.json"),
    )
    args = parser.parse_args()
    base = args.base.resolve()
    roster = args.roster if args.roster.is_absolute() else base / args.roster
    measurements = args.measurements if args.measurements.is_absolute() else base / args.measurements
    output = args.output if args.output.is_absolute() else base / args.output
    receipt_path = args.receipt if args.receipt.is_absolute() else base / args.receipt
    rows, receipt = build_rows(base, roster.resolve(), measurements.resolve())
    write_rows(output.resolve(), rows)
    receipt["output_file"] = {
        "path": str(output.resolve().relative_to(base)).replace("\\", "/"),
        "bytes": output.stat().st_size,
        "sha256": sha256_file(output),
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
