#!/usr/bin/env python3
"""Rebuild the current v1.1 research data in the only valid order.

The canonical exposure portfolio and both Top-100 companions are downstream
of the corrected expected universe, typed population supplements, population
joins, high-reach needs, and work-level forward residual table.  This driver
therefore runs every dependency and fails if an equal-basis profile, exact
completion state, or companion membership/order regresses.
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent

STEPS = [
    "normalize_interlanguage_staging.py",
    "augment_equal_basis_east_asia_v1_1.py",
    "build_candidate_master_and_join_suggestions.py",
    "build_edge_curation_queue.py",
    "build_natural_language_scores_v3.py",
    "build_final_portfolio.py",
    "build_global_expected_universe_v1_1.py",
    "build_supplemental_typed_population_estimates_v1_1.py",
    "join_expected_universe_to_population_v1_1.py",
    "build_high_reach_education_needs_v1_1.py",
    "build_denominator_stratified_rankings_v1_1.py",
    "test_allocation_policy_v1_1.py",
    "test_opportunity_planning_v1_1.py",
    "test_portfolio_unit_identity_v1_1.py",
    "test_component_scope_v1_1.py",
    "build_authoritative_exposure_portfolio_v1_1.py",
    "build_top100_companions_v1_1.py",
]

REQUIRED_PROFILES = {
    "NAT-121": "id-Latn-ID",
    "NAT-122": "zh-Hans-CN",
    "NAT-123": "ja-Jpan-JP",
    "NAT-124": "hi-Deva-IN",
    "NAT-125": "bho-Deva-IN",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> None:
    step_receipts: list[dict[str, object]] = []
    for script_name in STEPS:
        script = SCRIPTS / script_name
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        step_receipts.append(
            {
                "script": script_name,
                "exit_code": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
            }
        )
        if result.returncode:
            raise RuntimeError(
                f"{script_name} failed with {result.returncode}:\n{result.stderr}"
            )

    candidate_path = ROOT / "candidate_interventions_master.csv"
    candidates = {row["intervention_id"]: row for row in read_csv(candidate_path)}
    missing = sorted(set(REQUIRED_PROFILES) - set(candidates))
    if missing:
        raise RuntimeError(f"Equal-basis profiles disappeared: {missing}")
    wrong_tags = {
        intervention_id: candidates[intervention_id]["variety_or_register"]
        for intervention_id, expected_tag in REQUIRED_PROFILES.items()
        if candidates[intervention_id]["variety_or_register"] != expected_tag
    }
    if wrong_tags:
        raise RuntimeError(f"Equal-basis profile tags changed: {wrong_tags}")

    idms = candidates.get("IL-IDMS")
    if not idms or "722 of 722 complete" not in idms["existing_local_status"]:
        raise RuntimeError("IL-IDMS regressed from the verified 722/722 state")
    if "321 of 722" in idms["existing_local_status"]:
        raise RuntimeError("IL-IDMS contains the superseded 321/722 state")
    chinese = candidates["NAT-122"]
    if "Calculus Volume 1 30 of 55" not in chinese["existing_local_status"]:
        raise RuntimeError("NAT-122 regressed from the verified Calculus I 30/55 state")

    top100_rows = read_csv(ROOT / "TOP_100.csv")
    needs_rows = read_csv(ROOT / "top100_needs_assignment_v2.csv")
    crosswalk_rows = read_csv(ROOT / "top100_interlanguage_overlap_crosswalk.csv")
    top_ids = [row["entry_id"] for row in top100_rows]
    if len(top_ids) != 100 or len(set(top_ids)) != 100:
        raise RuntimeError("Canonical Top 100 is not exactly 100 unique entries")
    if [row["entry_id"] for row in needs_rows] != top_ids:
        raise RuntimeError("Needs companion membership/order differs from canonical Top 100")
    if [row["entry_id"] for row in crosswalk_rows] != top_ids:
        raise RuntimeError("Interlanguage crosswalk membership/order differs from canonical Top 100")

    outputs = [
        candidate_path,
        ROOT / "candidate_population_join_suggestions.csv",
        ROOT / "candidate_population_edge_curation_queue.csv",
        ROOT / "natural_language_scores_v3.csv",
        ROOT / "portfolio_linguistic_candidates.csv",
        ROOT / "TOP_10.csv",
        ROOT / "TOP_100.csv",
        ROOT / "table_a_ex_ante_gross_opportunity.csv",
        ROOT / "table_b_target_readable_access_sensitivity.csv",
        ROOT / "table_c_forward_residual_commissioning.csv",
        ROOT / "denominator_stratified_rankings_v1_1_validation.json",
        ROOT / "staging" / "global_expected_universe" / "expected_language_profiles_v1_1.csv",
        ROOT / "staging" / "global_expected_universe" / "expected_universe_validation_v1_1.json",
        ROOT / "staging" / "global_expected_universe" / "profile_population_estimates_supplement_v1_1.csv",
        ROOT / "staging" / "global_expected_universe" / "profile_population_estimates_supplement_validation_v1_1.json",
        ROOT / "staging" / "global_expected_universe" / "expected_profile_population_joins_v1_1.csv",
        ROOT / "staging" / "global_expected_universe" / "expected_profile_population_joins_validation_v1_1.json",
        ROOT / "staging" / "high_reach_education_needs" / "high_reach_education_needs_v1_1.csv",
        ROOT / "staging" / "high_reach_education_needs" / "high_reach_needs_portfolio_edges_v1_1.csv",
        ROOT / "top100_commissioning_portfolio_v1_1_validation.json",
        ROOT / "allocation_policy_v1_1_validation.json",
        ROOT / "allocation_policy_sensitivity_v1_1.csv",
        ROOT / "opportunity_planning_sensitivity_v1_1.csv",
        ROOT / "staging" / "authoritative_exposure_portfolio_v1_1" / "full_computed_allocation_queue.csv",
        ROOT / "staging" / "authoritative_exposure_portfolio_v1_1" / "candidate_dispositions.json",
        ROOT / "staging" / "authoritative_exposure_portfolio_v1_1" / "recovered_lane_and_prior_band_crosswalk.json",
        ROOT / "staging" / "authoritative_exposure_portfolio_v1_1" / "scope_calibrated_planning_crosswalk.json",
        ROOT / "top100_needs_assignment_v2.csv",
        ROOT / "top100_interlanguage_overlap_crosswalk.csv",
        ROOT / "top100_companions_v1_1_validation.json",
    ]
    receipt = {
        "schema": "interlanguage/v1-1-data-pipeline-rebuild/1.1.0",
        "status": "PASS",
        "steps": step_receipts,
        "required_equal_basis_profiles": REQUIRED_PROFILES,
        "indonesian_openlogic_state": idms["existing_local_status"],
        "chinese_calculus_state": chinese["existing_local_status"],
        "top100_membership": top_ids,
        "outputs": {
            path.name: {
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in outputs
        },
    }
    receipt_path = ROOT / "V1_1_DATA_PIPELINE_REBUILD_20260831.json"
    receipt_path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "steps": len(STEPS),
                "candidate_rows": len(candidates),
                "required_profiles": sorted(REQUIRED_PROFILES),
                "receipt": str(receipt_path),
                "receipt_sha256": sha256(receipt_path),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
