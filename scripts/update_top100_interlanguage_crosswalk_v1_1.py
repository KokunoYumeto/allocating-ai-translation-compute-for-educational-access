from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    top = read("TOP_100.csv")
    needs = {row["intervention_id"]: row for row in read("top100_needs_assignment_v2.csv")}
    old = read("top100_interlanguage_overlap_crosswalk.csv")
    fields = list(old[0])
    by_id = {row["intervention_id"]: row for row in old}

    rebuilt: list[dict[str, str]] = []
    for item in sorted(top, key=lambda row: int(row["portfolio_position"])):
        intervention_id = item["intervention_id"]
        need = needs[intervention_id]
        if intervention_id in by_id:
            row = dict(by_id[intervention_id])
        else:
            row = {field: "" for field in fields}
            row.update({
                "overlap_relation_status": "no_exact_relation_in_current_matrix",
                "profile_match_basis": "none",
                "integrability_status": "not_assessed_from_current_interlanguage_matrix",
                "integrability_basis": "No exact target-profile relation appears in the current normalized interlanguage matrix.",
                "shared_core_compute_reuse_potential": "none_credited",
                "shared_core_compute_reuse_basis": "No exact shared-core or interlanguage edge is registered for this Top-100 profile.",
                "named_localized_output_status": "not_applicable_no_matrix_relation",
                "current_direct_component_completion_overlap": "not assessed in this crosswalk",
                "forward_component_deficit_D": "not_applicable",
                "current_cross_language_demographic_reach_credit": "0",
                "demographic_reach_credit_basis": "No exact current matrix relation exists, so no cross-language demographic reach can be credited.",
                "double_count_rule": "No family or interlanguage multiplier is applied.",
                "exclusions": "No matrix relation; no inferred family coverage.",
                "rankable_under_current_evidence": "false",
                "crosswalk_note": "No exact relation in the current normalized matrices. Equal-basis native-language ranking and exact forward residual remain separate.",
            })

        row.update({
            "portfolio_position": item["portfolio_position"],
            "intervention_id": intervention_id,
            "intervention_name": item["intervention_name"],
            "target_profile": item["target_profiles"],
            "territory_or_scope": item["territory_or_scope"],
            "population_source_ids": item["population_source_ids"],
            "needs_assignment_status": need["needs_assignment_status"],
            "learner_stage": need["learner_stage"],
            "need_class": need["need_class"],
            "first_open_package_or_sequence": need["first_open_package_or_sequence"],
        })
        rebuilt.append({field: row.get(field, "") for field in fields})

    if len(rebuilt) != 100 or len({row['intervention_id'] for row in rebuilt}) != 100:
        raise RuntimeError("Crosswalk is not a unique 100-row current portfolio")
    output = ROOT / "top100_interlanguage_overlap_crosswalk.csv"
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rebuilt)
    print({
        "rows": len(rebuilt),
        "exact_profile": sum(row["overlap_relation_status"] == "exact_profile_match" for row in rebuilt),
        "no_exact": sum(row["overlap_relation_status"] == "no_exact_relation_in_current_matrix" for row in rebuilt),
        "first": rebuilt[0]["intervention_id"],
    })


if __name__ == "__main__":
    main()

