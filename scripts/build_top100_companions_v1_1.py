#!/usr/bin/env python3
"""Regenerate the Top-100 needs and interlanguage-overlap companions.

The canonical portfolio is the only source of membership and position.  This
builder deliberately uses exact identifiers/profile tags only; it never infers
family coverage from names and never converts compute reuse into demographic
reach.  Work-level completion comes from Table C independently of whether an
interlanguage relation exists.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOP100 = ROOT / "TOP_100.csv"
MATRIX = ROOT / "staging" / "interlanguage_bundle_model" / "interlanguage_intervention_matrix.csv"
FORWARD = ROOT / "table_c_forward_residual_commissioning.csv"
OUT_NEEDS = ROOT / "top100_needs_assignment_v2.csv"
OUT_CROSSWALK = ROOT / "top100_interlanguage_overlap_crosswalk.csv"
OUT_VALIDATION = ROOT / "top100_companions_v1_1_validation.json"


NEEDS_FIELDS = [
    "exposure_position", "wave", "allocation_lane", "entry_id", "entry_type",
    "entry_name", "target_profiles", "territory_or_scope", "component_profile_ids",
    "population_context", "population_denominator_classes", "population_source_ids",
    "direct_reader_reach_claim", "shared_core_compute_reuse", "education_stages",
    "needs_profile_ids", "named_output_profile_ids", "why_now",
    "first_bounded_package", "follow_on_package", "prerequisite_route",
    "existing_supply_state", "delivery_formats", "teacher_independent_requirements",
    "accessibility_requirements", "non_overlap_rule", "package_evidence_status",
    "recommendation_status", "ordering_basis", "evidence_confidence", "source_urls",
    "uncertainty",
]

CROSSWALK_FIELDS = [
    "exposure_position", "entry_id", "entry_type", "entry_name", "target_profiles",
    "territory_or_scope", "component_profile_ids", "named_output_profile_ids",
    "population_source_ids", "matched_matrix_row_ids",
    "matched_interlanguage_intervention_ids", "matched_mechanism_classes",
    "matched_edge_roles", "profile_match_basis", "comprehension_evidence_statuses",
    "rankable_matrix_rows", "current_cross_language_demographic_reach_credit",
    "demographic_reach_credit_basis", "shared_core_compute_reuse",
    "current_direct_component_completion_overlap", "forward_component_deficit_D",
    "forward_next_nonduplicative_actions", "double_count_rules", "exclusions",
    "interlanguage_source_ids", "matrix_confidence", "crosswalk_note",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def split_values(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def unique_join(values: list[str], separator: str = ";") -> str:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        value = value.strip()
        if value and value not in seen:
            seen.add(value)
            output.append(value)
    return separator.join(output)


def summarize_forward(rows: list[dict[str, str]]) -> tuple[str, str, str]:
    if not rows:
        return (
            "No exact work-level completion row is registered in Table C.",
            "unregistered_not_zero",
            "Register an exact work, stage and format before assigning a forward content deficit.",
        )
    completion: list[str] = []
    deficits: list[str] = []
    actions: list[str] = []
    for row in rows:
        complete = row.get("verified_complete_units", "")
        total = row.get("total_units", "")
        residual = row.get("residual_units", "")
        label = row["exact_work_stage_format"]
        if complete or total or residual:
            completion.append(f"{row['forward_row_id']} {label}: complete={complete or 'unknown'}/{total or 'unknown'}; residual={residual or 'unknown'}")
        else:
            completion.append(f"{row['forward_row_id']} {label}: scope unresolved")
        d_value = row.get("content_deficit_D_forward", "")
        d_status = row.get("content_deficit_status", "")
        deficits.append(f"{row['forward_row_id']}={d_value if d_value else 'unmeasured'} [{d_status or 'unmeasured'}]")
        actions.append(f"{row['forward_row_id']}: {row['next_nonduplicative_action']}")
    return " | ".join(completion), " | ".join(deficits), " | ".join(actions)


def main() -> None:
    top = read_csv(TOP100)
    policy_receipt = json.loads((ROOT / "allocation_policy_v1_1_validation.json").read_text(encoding="utf-8"))
    policy_entries = policy_receipt["diagnostics"]["entries"]
    matrix = read_csv(MATRIX)
    forward_rows = read_csv(FORWARD)
    forward_by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in forward_rows:
        forward_by_id[row["intervention_id"]].append(row)

    needs_rows: list[dict[str, str]] = []
    crosswalk_rows: list[dict[str, str]] = []

    for expected_position, item in enumerate(top, start=1):
        position = int(item["exposure_position"])
        if position != expected_position:
            raise ValueError(f"Top-100 position mismatch at row {expected_position}: {position}")
        needs_rows.append({field: item.get(field, "") for field in NEEDS_FIELDS})

        exact_profiles = set(split_values(item.get("target_profiles", "")))
        exact_profiles.update(split_values(item.get("named_output_profile_ids", "")))
        matches: list[tuple[dict[str, str], str]] = []
        for row in matrix:
            bases: list[str] = []
            if row["intervention_id"] == item["entry_id"]:
                bases.append("exact_intervention_id")
            matrix_tag = row.get("language_or_profile_tag", "").strip()
            if matrix_tag and matrix_tag in exact_profiles:
                bases.append("exact_profile_tag")
            if bases:
                matches.append((row, "+".join(bases)))

        match_rows = [row for row, _basis in matches]
        rankable = [row for row in match_rows if row.get("rankable_under_current_evidence", "").lower() == "true"]
        # The current normalized matrix intentionally has no rankable cross-language
        # demographic rows. Fail closed if that changes until a separate aggregation
        # rule is implemented; never silently sum edge-level gains here.
        if rankable:
            raise ValueError(
                f"{item['entry_id']} has rankable matrix rows; direct-reach aggregation requires an explicit nonadditive rule"
            )

        completion, deficits, actions = summarize_forward(forward_by_id[item["entry_id"]])
        if matches:
            basis = unique_join([match_basis for _row, match_basis in matches])
            match_note = (
                "Exact matrix relations are listed for production reuse and evidence routing. "
                "Every matched row is currently non-rankable for demographic reach, so direct cross-language credit remains zero."
            )
        else:
            basis = "none_exact"
            match_note = (
                "No exact intervention-ID or exact profile-tag relation exists in the normalized matrix. "
                "No family, script or name-based coverage is inferred."
            )

        crosswalk_rows.append({
            "exposure_position": item["exposure_position"],
            "entry_id": item["entry_id"],
            "entry_type": item["entry_type"],
            "entry_name": item["entry_name"],
            "target_profiles": item["target_profiles"],
            "territory_or_scope": item["territory_or_scope"],
            "component_profile_ids": item["component_profile_ids"],
            "named_output_profile_ids": item["named_output_profile_ids"],
            "population_source_ids": item["population_source_ids"],
            "matched_matrix_row_ids": unique_join([row["matrix_row_id"] for row in match_rows]),
            "matched_interlanguage_intervention_ids": unique_join([row["intervention_id"] for row in match_rows]),
            "matched_mechanism_classes": unique_join([row["mechanism_class"] for row in match_rows]),
            "matched_edge_roles": unique_join([row["edge_role"] for row in match_rows]),
            "profile_match_basis": basis,
            "comprehension_evidence_statuses": unique_join([row["comprehension_evidence_status"] for row in match_rows]),
            "rankable_matrix_rows": "0",
            "current_cross_language_demographic_reach_credit": "0",
            "demographic_reach_credit_basis": (
                "Conservative zero under the current evidence: no matched matrix row is rankable for cross-language demographic reach. "
                "This does not set production reuse to zero."
            ),
            "shared_core_compute_reuse": item["shared_core_compute_reuse"],
            "current_direct_component_completion_overlap": completion,
            "forward_component_deficit_D": deficits,
            "forward_next_nonduplicative_actions": actions,
            "double_count_rules": unique_join([row["double_count_rule"] for row in match_rows], " | ") or item["non_overlap_rule"],
            "exclusions": unique_join([row["communities_excluded"] for row in match_rows], " | ") or item["non_overlap_rule"],
            "interlanguage_source_ids": unique_join([row["source_ids"] for row in match_rows]),
            "matrix_confidence": unique_join([row["confidence"] for row in match_rows]),
            "crosswalk_note": match_note,
        })

    write_csv(OUT_NEEDS, NEEDS_FIELDS, needs_rows)
    write_csv(OUT_CROSSWALK, CROSSWALK_FIELDS, crosswalk_rows)

    required_need_fields = [
        "entry_id", "entry_name", "education_stages", "first_bounded_package",
        "follow_on_package", "prerequisite_route", "delivery_formats",
        "teacher_independent_requirements", "accessibility_requirements",
        "non_overlap_rule", "package_evidence_status", "evidence_confidence",
    ]
    current_ids = [row["entry_id"] for row in top]
    checks = {
        "top100_exactly_100_unique": len(top) == 100 and len(set(current_ids)) == 100,
        "needs_exactly_100_unique": len(needs_rows) == 100 and len({row["entry_id"] for row in needs_rows}) == 100,
        "crosswalk_exactly_100_unique": len(crosswalk_rows) == 100 and len({row["entry_id"] for row in crosswalk_rows}) == 100,
        "needs_membership_and_order_equal_top100": [row["entry_id"] for row in needs_rows] == current_ids,
        "crosswalk_membership_and_order_equal_top100": [row["entry_id"] for row in crosswalk_rows] == current_ids,
        "needs_required_fields_nonempty": all(all(row[field] for field in required_need_fields) for row in needs_rows),
        "no_unresolved_package_status": all(row["package_evidence_status"] != "unresolved_no_registered_package" for row in needs_rows),
        "crosswalk_direct_reach_zero_without_rankable_edges": all(
            row["rankable_matrix_rows"] == "0" and row["current_cross_language_demographic_reach_credit"] == "0"
            for row in crosswalk_rows
        ),
        "forward_completion_not_conditioned_on_matrix": all(
            row["current_direct_component_completion_overlap"] for row in crosswalk_rows
        ),
        "chinese_calc_cursor_current": any(
            row["entry_id"] == "NAT-122"
            and "complete=30/55" in row["current_direct_component_completion_overlap"]
            and "residual=25" in row["current_direct_component_completion_overlap"]
            for row in crosswalk_rows
        ),
        "major_profiles_considered_on_equal_basis_not_forced_into_top10": all(identifier in policy_entries for identifier in ("NAT-121", "NAT-122", "NAT-123", "NAT-124", "NAT-125")),
        "policy_selection_checks_pass": policy_receipt["status"] == "PASS" and all(policy_receipt["checks"].values()),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    validation = {
        "schema": "interlanguage/top100-companions-validation/1.1.0",
        "status": status,
        "checks": checks,
        "top100": {"bytes": TOP100.stat().st_size, "sha256": sha256(TOP100)},
        "needs": {"bytes": OUT_NEEDS.stat().st_size, "sha256": sha256(OUT_NEEDS)},
        "crosswalk": {"bytes": OUT_CROSSWALK.stat().st_size, "sha256": sha256(OUT_CROSSWALK)},
        "matrix": {"bytes": MATRIX.stat().st_size, "sha256": sha256(MATRIX)},
        "forward_table": {"bytes": FORWARD.stat().st_size, "sha256": sha256(FORWARD)},
        "matched_entries": sum(bool(row["matched_matrix_row_ids"]) for row in crosswalk_rows),
        "direct_reach_rule": "No cross-language demographic gain is aggregated while all exact matched matrix rows are non-rankable. Compute reuse remains separately recorded.",
    }
    OUT_VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit("FAIL: Top-100 companion validation did not pass")
    print(json.dumps({
        "status": status,
        "needs_rows": len(needs_rows),
        "crosswalk_rows": len(crosswalk_rows),
        "matched_entries": validation["matched_entries"],
        "needs_sha256": sha256(OUT_NEEDS),
        "crosswalk_sha256": sha256(OUT_CROSSWALK),
        "validation_sha256": sha256(OUT_VALIDATION),
    }, indent=2))


if __name__ == "__main__":
    main()
