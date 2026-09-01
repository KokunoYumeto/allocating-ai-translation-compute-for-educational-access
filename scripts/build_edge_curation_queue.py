from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def rows(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    candidates = {row["intervention_id"]: row for row in rows("candidate_interventions_master.csv")}
    observations = {row["observation_id"]: row for row in rows("population_observations_master.csv")}
    joins = rows("candidate_population_join_suggestions.csv")

    preferred_component_candidates = {
        row["intervention_id"]
        for row in joins
        if observations[row["observation_id"]]["target_mapping_status"]
        == "same_name_mother_tongue_component_preferred_for_standard_edition"
    }
    thai_union_candidates = {
        row["intervention_id"]
        for row in joins
        if observations[row["observation_id"]]["target_mapping_status"] == "derived_exact_thai_usable_union"
    }
    preferred_direct_access_union_candidates = {
        row["intervention_id"]
        for row in joins
        if observations[row["observation_id"]]["observation_use"]
        == "direct_literacy_observation_pending_intervention_edges"
        and observations[row["observation_id"]]["target_mapping_status"].startswith("derived_exact_named_language_union")
    }

    output: list[dict[str, str]] = []
    for join in joins:
        candidate = candidates[join["intervention_id"]]
        observation = observations[join["observation_id"]]
        declared_candidate_match = (
            join["intervention_id"] in observation["edition_profile"]
            or join["intervention_id"] in observation["target_mapping_status"]
        )
        exact_join_for_queue = (
            join["suggestion_status"] == "strong_join_suggestion"
            or declared_candidate_match
        )
        status = "manual_review"
        reason = "Machine suggestion requires exact target, measure, and overlap review."

        if candidate["target_type"] not in {"natural_language", "natural_language_completion"}:
            status = "route_to_interlanguage_or_accessibility_edges"
            reason = "This queue only auto-classifies named written-language and completion interventions."
        elif not exact_join_for_queue:
            status = "not_automatic_cross_territory_or_name_only"
            reason = "The target territory or exact code/profile does not match; explicit many-to-many curation is required."
        elif observation["negative_control"] == "true":
            status = "exclude_negative_control"
            reason = "The source row is a negative control rather than a missing-edition beneficiary observation."
        elif candidate["rankability_status"].startswith("discovery_only"):
            status = "exclude_unresolved_target"
            reason = "The candidate's exact variety, script, register, or standard is unresolved."
        elif join["intervention_id"] in preferred_component_candidates and observation["target_mapping_status"] == "c16_census_language_aggregate":
            status = "exclude_superseded_parent_aggregate"
            reason = "A same-name C-16 mother-tongue component is available; the broader category remains context only."
        elif join["intervention_id"] in thai_union_candidates and observation["target_mapping_status"] == "source_aggregate_or_component_context":
            status = "exclude_nonadditive_union_component"
            reason = "The exact mutually exclusive Thai union is the preferred demographic ceiling."
        elif (
            join["intervention_id"] in preferred_direct_access_union_candidates
            and observation["observation_use"] == "direct_literacy_observation_pending_intervention_edges"
            and not observation["target_mapping_status"].startswith("derived_exact_named_language_union")
        ):
            status = "exclude_nested_direct_access_component"
            reason = "A derived exact union of mutually exclusive literacy cells is available; the nested component is retained only as context."
        elif observation["count_unit"] not in {"persons", "estimated_persons"}:
            status = "exclude_nonperson_measure_from_population_rank"
            reason = "Households, percentages, cases, or another nonperson unit cannot be ranked as people; published person estimates remain eligible with their intervals."
        elif observation["target_mapping_status"] in {
            "household_proxy",
            "non_language_population_proxy",
            "macro_or_unresolved_source_label",
            "generic_signed_source_label_unresolved",
            "oral_or_speaking_ability_observation",
            "source_observation_not_candidate_ready",
            "source_named_label_pending_edition_profile_evidence",
        } or observation["observation_use"].startswith("context_or_sensitivity_only"):
            status = "context_until_specific_mapping_or_written_access"
            reason = "The observation is a proxy, aggregate, oral-only measure, or unresolved mapping rather than an exact written-edition audience."
        elif observation["observation_use"] in {
            "gross_upper_bound_pending_intervention_edges",
            "gross_language_ceiling_pending_intervention_edges",
            "gross_lower_bound_pending_intervention_edges",
        } or observation["target_mapping_status"] in {
            "same_name_mother_tongue_component_preferred_for_standard_edition",
            "derived_exact_thai_usable_union",
            "gross_named_spoken_language_observation",
        }:
            status = "eligible_exact_gross_ceiling"
            reason = "Exact code/profile/territory and person-count measure match; the source measure role and factor/overlap assignment remain downstream."
        elif observation["observation_use"] == "direct_literacy_observation_pending_intervention_edges":
            status = "eligible_exact_direct_access_floor"
            reason = "The person count is already restricted to a directly observed literacy/access stratum; use it as a floor and do not multiply it by another literacy proxy."

        output.append(
            {
                "curation_id": f"CUR-{len(output)+1:04d}",
                "intervention_id": join["intervention_id"],
                "target_name": candidate["target_name"],
                "target_profile": candidate["variety_or_register"],
                "target_type": candidate["target_type"],
                "candidate_rankability_status": candidate["rankability_status"],
                "observation_id": join["observation_id"],
                "population_language_label": observation["language_label"],
                "population_profile": observation["edition_profile"],
                "territory": observation["territory"],
                "reference_year": observation["reference_date_or_year"],
                "measure_type": observation["measure_type"],
                "count_unit": observation["count_unit"],
                "exact_source_population": observation["population_base"],
                "source_id": observation["source_id"],
                "source_locator": observation["source_locator"],
                "join_suggestion_status": join["suggestion_status"],
                "target_mapping_status": observation["target_mapping_status"],
                "observation_use": observation["observation_use"],
                "overlap_group_id": observation["overlap_group_id"],
                "automatic_curation_status": status,
                "automatic_curation_reason": reason,
                "manual_disposition": "pending",
                "manual_notes": "",
            }
        )

    fields = list(output[0].keys())
    with (ROOT / "candidate_population_edge_curation_queue.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    counts: dict[str, int] = {}
    for row in output:
        counts[row["automatic_curation_status"]] = counts.get(row["automatic_curation_status"], 0) + 1
    print({"rows": len(output), "status_counts": counts})


if __name__ == "__main__":
    main()
