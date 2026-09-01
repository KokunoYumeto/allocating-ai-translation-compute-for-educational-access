#!/usr/bin/env python3
"""Join the expected-profile universe to every current source observation.

The output preserves all matching observations and their denominator classes;
it deliberately does not select a globally preferred count or rank across
classes.  Missing joins remain first-class rows.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UNIVERSE = ROOT / "staging" / "global_expected_universe" / "expected_language_profiles_v1_1.csv"
UNIVERSE_VALIDATION = ROOT / "staging" / "global_expected_universe" / "expected_universe_validation_v1_1.json"
CANDIDATES = ROOT / "candidate_interventions_master.csv"
SUGGESTIONS = ROOT / "candidate_population_join_suggestions.csv"
OBSERVATIONS = ROOT / "population_observations_master.csv"
SUPPLEMENT = ROOT / "staging" / "global_expected_universe" / "profile_population_estimates_supplement_v1_1.csv"
SUPPLEMENT_VALIDATION = ROOT / "staging" / "global_expected_universe" / "profile_population_estimates_supplement_validation_v1_1.json"
OUT = ROOT / "staging" / "global_expected_universe"

FIELDS = [
    "universe_profile_id", "display_name", "profile_tag", "source_profile_tag", "disposition",
    "candidate_id", "candidate_target_name", "observation_id", "join_status",
    "suggestion_status", "semantic_join_status", "candidate_ready_for_ranking",
    "source_target_mapping_status",
    "denominator_class", "source_measure_type", "learner_stratum",
    "population_low", "population_base", "population_high", "count_unit",
    "reference_date_or_year", "source_id", "source_locator",
    "source_url", "source_value_status", "derivation_method",
    "typed_view_eligibility", "source_transcribed_exactly", "gross_population_only",
    "source_rank_ready_claim", "rank_ready_marginal_access", "source_series_id",
    "overlap_group_id", "nonadditivity_group_id", "nonadditivity_rule",
    "supersedes_observation_ids", "population_use",
    "existing_supply_state", "next_nonduplicative_action", "caveats",
]


MASTER_OVERLAP_GROUP_OVERRIDES = {
    "POP-ET-002": "AMH-ET-L1-LOI-NONADDITIVE",
    "POP-ET-001": "OROMO-ET-L1-REGION-NONADDITIVE",
}


def nonadditivity_rule(overlap_group_id: str) -> str:
    if overlap_group_id:
        return "never_sum_rows_sharing_overlap_group_id"
    return "no_cross_row_nonadditivity_group_recorded"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def measure_class(measure: str) -> str:
    text = measure.casefold()
    if "territory_population" in text or "mainland_population_gross_territory" in text:
        return "territory_all_residents_ceiling"
    if "same_name_mother_tongue_component" in text:
        return "same_name_mother_tongue_component"
    if "functional_language" in text or "able_to_speak" in text or "functional_language_users" in text:
        return "functional_language_ability_or_estimate"
    if any(token in text for token in ("mother_tongue", "first_language", "native_language", "learned_in_childhood")):
        return "mother_tongue_or_first_language"
    if any(token in text for token in (
        "home_language", "spoken_at_home", "language_used_at_home", "languages_used_at_home",
        "spoken_in_household", "daily_language_at_home", "daily_use_outside_education",
        "usually_spoken_at_home", "principal_language",
    )):
        return "home_or_usual_language_use"
    if any(token in text for token in ("read_and_written", "literate", "literacy", "direct_access")):
        return "direct_literacy_or_access_stratum"
    if any(token in text for token in ("school", "student", "enrol", "learner")):
        return "education_cohort"
    if any(token in text for token in ("estimated_speakers", "lower_bound_speakers", "speaker_estimate", "total_speakers")):
        return "published_or_derived_speaker_estimate"
    if "languages_spoken_multiple_response" in text:
        return "multiple_response_language_ability"
    if "main_language_weighted_persons" in text:
        return "survey_weighted_main_language_estimate"
    if "union_of_mutually_exclusive_census_strata" in text:
        return "derived_union_of_census_language_strata"
    return "other_dated_person_observation"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    universe_validation = json.loads(UNIVERSE_VALIDATION.read_text(encoding="utf-8"))
    supplement_validation = json.loads(SUPPLEMENT_VALIDATION.read_text(encoding="utf-8"))
    upstream_errors: list[str] = []
    if universe_validation.get("status") != "PASS":
        upstream_errors.append("expected-universe validation is not PASS")
    if universe_validation.get("outputs", {}).get(UNIVERSE.name, {}).get("sha256") != sha256(UNIVERSE):
        upstream_errors.append("expected-universe CSV hash differs from its validation receipt")
    if supplement_validation.get("status") != "PASS":
        upstream_errors.append("supplement validation is not PASS")
    if supplement_validation.get("output", {}).get("sha256") != sha256(SUPPLEMENT):
        upstream_errors.append("supplement CSV hash differs from its validation receipt")
    if upstream_errors:
        raise SystemExit("FAIL\n" + "\n".join(upstream_errors))

    profiles = read_csv(UNIVERSE)
    candidates = {row["intervention_id"]: row for row in read_csv(CANDIDATES)}
    observations = {row["observation_id"]: row for row in read_csv(OBSERVATIONS)}
    supplement_by_profile: dict[str, list[dict[str, str]]] = defaultdict(list)
    supplements = read_csv(SUPPLEMENT)
    superseded_observation_ids = {
        observation_id
        for supplement in supplements
        for observation_id in supplement["supersedes_observation_ids"].split(";")
        if observation_id
    }
    for supplement in supplements:
        supplement_by_profile[supplement["universe_profile_id"]].append(supplement)
    suggestions_by_candidate: dict[str, list[dict[str, str]]] = defaultdict(list)
    for suggestion in read_csv(SUGGESTIONS):
        suggestions_by_candidate[suggestion["intervention_id"]].append(suggestion)

    output: list[dict[str, str]] = []
    for profile in profiles:
        candidate_ids = [item for item in profile["candidate_ids"].split(";") if item]
        supplemental = supplement_by_profile.get(profile["universe_profile_id"], [])
        if not candidate_ids and not supplemental:
            output.append({
                "universe_profile_id": profile["universe_profile_id"],
                "display_name": profile["display_name"],
                "profile_tag": profile["profile_tag"],
                "source_profile_tag": "",
                "disposition": profile["disposition"],
                "candidate_id": "", "candidate_target_name": "", "observation_id": "",
                "join_status": "no_current_candidate_profile", "suggestion_status": "not_applicable",
                "semantic_join_status": "not_applicable", "candidate_ready_for_ranking": "false",
                "source_target_mapping_status": "not_applicable", "denominator_class": "",
                "source_measure_type": "", "learner_stratum": "", "population_low": "",
                "population_base": "", "population_high": "", "count_unit": "not_applicable",
                "reference_date_or_year": "", "source_id": "", "source_locator": "",
                "source_url": "", "source_value_status": "", "derivation_method": "",
                "typed_view_eligibility": "",
                "source_transcribed_exactly": "", "gross_population_only": "",
                "source_rank_ready_claim": "not_applicable", "rank_ready_marginal_access": "false",
                "source_series_id": "", "overlap_group_id": "", "nonadditivity_group_id": "",
                "nonadditivity_rule": "not_applicable",
                "supersedes_observation_ids": "",
                "population_use": "unresolved_no_current_population_join",
                "existing_supply_state": profile["existing_supply_state"],
                "next_nonduplicative_action": profile["next_nonduplicative_action"],
                "caveats": profile["population_identity_warning"],
            })
        for candidate_id in candidate_ids:
            candidate = candidates[candidate_id]
            exact = [
                item for item in suggestions_by_candidate.get(candidate_id, [])
                if item["suggestion_status"] == "strong_join_suggestion"
                and observations[item["observation_id"]]["count_unit"] == "persons"
                and observations[item["observation_id"]]["target_mapping_status"] != "sample_case_not_population"
                and item["observation_id"] not in superseded_observation_ids
            ]
            if not exact:
                output.append({
                    "universe_profile_id": profile["universe_profile_id"],
                    "display_name": profile["display_name"],
                    "profile_tag": profile["profile_tag"],
                    "source_profile_tag": "",
                    "disposition": profile["disposition"],
                    "candidate_id": candidate_id,
                    "candidate_target_name": candidate["target_name"],
                    "observation_id": "", "join_status": "candidate_without_machine_strong_population_suggestion",
                    "suggestion_status": "none", "semantic_join_status": "unresolved",
                    "candidate_ready_for_ranking": "false", "source_target_mapping_status": "unresolved",
                    "denominator_class": "", "source_measure_type": "", "learner_stratum": "",
                    "population_low": "", "population_base": "", "population_high": "",
                    "count_unit": "not_applicable", "reference_date_or_year": "", "source_id": "",
                    "source_locator": "", "source_transcribed_exactly": "",
                    "source_url": "", "source_value_status": "", "derivation_method": "",
                    "typed_view_eligibility": "",
                    "gross_population_only": "", "rank_ready_marginal_access": "false",
                    "source_rank_ready_claim": "not_applicable", "source_series_id": "",
                    "overlap_group_id": "", "nonadditivity_group_id": "",
                    "supersedes_observation_ids": "", "population_use": "unresolved_population_join",
                    "nonadditivity_rule": "not_applicable",
                    "existing_supply_state": profile["existing_supply_state"],
                    "next_nonduplicative_action": profile["next_nonduplicative_action"],
                    "caveats": profile["population_identity_warning"],
                })
                continue

            for suggestion in exact:
                observation = observations[suggestion["observation_id"]]
                denominator = measure_class(observation["measure_type"])
                rank_ready = observation["rank_ready_marginal_access"]
                population_use = "gross_or_context_typed_view_only_not_direct_residual_rank"
                overlap_group_id = MASTER_OVERLAP_GROUP_OVERRIDES.get(
                    observation["observation_id"], observation["overlap_group_id"]
                )
                output.append({
                    "universe_profile_id": profile["universe_profile_id"],
                    "display_name": profile["display_name"],
                    "profile_tag": profile["profile_tag"],
                    "source_profile_tag": observation["script_or_profile"],
                    "disposition": profile["disposition"],
                    "candidate_id": candidate_id,
                    "candidate_target_name": candidate["target_name"],
                    "observation_id": observation["observation_id"],
                    "join_status": "machine_strong_join_suggestion_pending_semantic_audit",
                    "suggestion_status": suggestion["suggestion_status"],
                    "semantic_join_status": "not_audited_machine_suggestion",
                    "candidate_ready_for_ranking": "false",
                    "source_target_mapping_status": observation["target_mapping_status"],
                    "denominator_class": denominator,
                    "source_measure_type": observation["measure_type"],
                    "learner_stratum": observation["learner_stratum"],
                    "population_low": observation["population_low"],
                    "population_base": observation["population_base"],
                    "population_high": observation["population_high"],
                    "count_unit": observation["count_unit"],
                    "reference_date_or_year": observation["reference_date_or_year"],
                    "source_id": observation["source_id"],
                    "source_locator": observation["source_locator"],
                    "source_url": "",
                    "source_value_status": "source_observation_transcribed_exactly" if observation["source_observation_transcribed_exactly"] == "true" else "source_observation_not_exactly_transcribed",
                    "derivation_method": "",
                    "typed_view_eligibility": "context_only_pending_semantic_join_audit",
                    "source_transcribed_exactly": observation["source_observation_transcribed_exactly"],
                    "gross_population_only": observation["gross_population_only"],
                    "source_rank_ready_claim": rank_ready,
                    "rank_ready_marginal_access": "false",
                    "source_series_id": observation["overlap_group_id"],
                    "overlap_group_id": overlap_group_id,
                    "nonadditivity_group_id": overlap_group_id,
                    "nonadditivity_rule": nonadditivity_rule(overlap_group_id),
                    "supersedes_observation_ids": "",
                    "population_use": population_use,
                    "existing_supply_state": profile["existing_supply_state"],
                    "next_nonduplicative_action": profile["next_nonduplicative_action"],
                    "caveats": " ".join(part for part in [profile["population_identity_warning"], observation["caveats"]] if part),
                })

        for supplement in supplemental:
            output.append({
                "universe_profile_id": profile["universe_profile_id"],
                "display_name": profile["display_name"],
                "profile_tag": profile["profile_tag"],
                "source_profile_tag": supplement["profile_tag"],
                "disposition": profile["disposition"],
                "candidate_id": "",
                "candidate_target_name": supplement["display_name"],
                "observation_id": supplement["supplement_id"],
                "join_status": "supplemental_profile_link_context_only",
                "suggestion_status": "not_applicable",
                "semantic_join_status": "profile_id_explicit_but_not_rank_approved",
                "candidate_ready_for_ranking": "false",
                "source_target_mapping_status": "supplement_context_only",
                "denominator_class": supplement["denominator_class"],
                "source_measure_type": supplement["measure_type"],
                "learner_stratum": supplement["learner_stratum"],
                "population_low": supplement["population_low"],
                "population_base": supplement["population_base"],
                "population_high": supplement["population_high"],
                "count_unit": supplement["count_unit"],
                "reference_date_or_year": supplement["reference_date_or_year"],
                "source_id": supplement["source_id"],
                "source_locator": supplement["source_locator"],
                "source_url": supplement["source_url"],
                "source_value_status": supplement["source_value_status"],
                "derivation_method": supplement["derivation_method"],
                "typed_view_eligibility": supplement["typed_view_eligibility"],
                "source_transcribed_exactly": supplement["source_transcribed_exactly"],
                "gross_population_only": "true",
                "source_rank_ready_claim": supplement["rank_ready_marginal_access"],
                "rank_ready_marginal_access": supplement["rank_ready_marginal_access"],
                "source_series_id": supplement["source_series_id"],
                "overlap_group_id": supplement["overlap_group_id"],
                "nonadditivity_group_id": supplement["nonadditivity_group_id"],
                "nonadditivity_rule": supplement["nonadditivity_rule"],
                "supersedes_observation_ids": supplement["supersedes_observation_ids"],
                "population_use": supplement["population_use"],
                "existing_supply_state": profile["existing_supply_state"],
                "next_nonduplicative_action": profile["next_nonduplicative_action"],
                "caveats": " ".join(part for part in [
                    profile["population_identity_warning"],
                    supplement["uncertainty"],
                    supplement["notes"],
                ] if part),
            })

    output.sort(key=lambda item: (
        item["universe_profile_id"], item["candidate_id"],
        item["denominator_class"], item["observation_id"],
    ))
    path = OUT / "expected_profile_population_joins_v1_1.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    profiles_with_population_evidence = {
        item["universe_profile_id"] for item in output
        if item["observation_id"]
    }
    unresolved = sorted({item["universe_profile_id"] for item in output} - profiles_with_population_evidence)
    numeric_rows = [item for item in output if any(
        item[field] for field in ("population_low", "population_base", "population_high")
    )]
    removed_duplicate_aliases = supplement_validation.get("removed_duplicate_aliases", {})
    removed_ids_present = sorted(
        set(removed_duplicate_aliases) & {item["observation_id"] for item in output}
    )
    canonical_occurrences = {
        canonical_id: sum(item["observation_id"] == canonical_id for item in output)
        for canonical_id in removed_duplicate_aliases.values()
    }
    canonical_profile = {
        "POP-PK-002": "GLB-019",
        "POP-ET-002": "GLB-048",
        "POP-ET-001": "GLB-049",
    }
    exact_source_tag_preservation = all(
        item["source_profile_tag"] == (
            observations[item["observation_id"]]["script_or_profile"]
            if item["observation_id"] in observations
            else next(
                supplement["profile_tag"] for supplement in supplements
                if supplement["supplement_id"] == item["observation_id"]
            )
        )
        for item in numeric_rows
    )
    checks = {
        "every_output_row_has_explicit_count_unit": all(item["count_unit"] != "" for item in output),
        "every_numeric_row_is_a_person_count": all(item["count_unit"] == "persons" for item in numeric_rows),
        "machine_suggestions_never_marked_candidate_ready": all(
            item["candidate_ready_for_ranking"] == "false"
            and item["rank_ready_marginal_access"] == "false"
            for item in output if item["suggestion_status"] == "strong_join_suggestion"
        ),
        "all_numeric_rows_context_only": all(
            item["population_use"] == "gross_or_context_typed_view_only_not_direct_residual_rank"
            for item in numeric_rows
        ),
        "source_profile_tags_preserved_by_exact_equality": exact_source_tag_preservation,
        "source_transcription_status_explicit_for_numeric_rows": all(
            item["source_transcribed_exactly"] in {"true", "false"} for item in numeric_rows
        ),
        "removed_duplicate_supplement_ids_absent": not removed_ids_present,
        "canonical_duplicate_targets_not_duplicated": all(
            count <= 1 for count in canonical_occurrences.values()
        ),
        "canonical_targets_present_or_profile_explicitly_unresolved": all(
            canonical_occurrences[canonical_id] == 1 or canonical_profile[canonical_id] in unresolved
            for canonical_id in canonical_occurrences
        ),
        "superseded_observations_absent": not (
            superseded_observation_ids & {item["observation_id"] for item in output}
        ),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    validation = {
        "schema": "interlanguage/expected-profile-population-join-validation/1.1.0",
        "status": status,
        "expected_profiles": len(profiles),
        "output_rows": len(output),
        "profiles_with_population_evidence": len(profiles_with_population_evidence),
        "profiles_without_population_evidence": len(unresolved),
        "unresolved_profile_ids": unresolved,
        "join_status_counts": dict(sorted(Counter(item["join_status"] for item in output).items())),
        "denominator_class_counts": dict(sorted(Counter(item["denominator_class"] for item in output if item["denominator_class"]).items())),
        "supplemental_context_rows": sum(item["join_status"] == "supplemental_profile_link_context_only" for item in output),
        "supplement": {"bytes": SUPPLEMENT.stat().st_size, "sha256": sha256(SUPPLEMENT)},
        "direct_rank_ready_rows": 0,
        "checks": checks,
        "upstream_receipts": {
            "expected_universe_validation": {"bytes": UNIVERSE_VALIDATION.stat().st_size, "sha256": sha256(UNIVERSE_VALIDATION)},
            "supplement_validation": {"bytes": SUPPLEMENT_VALIDATION.stat().st_size, "sha256": sha256(SUPPLEMENT_VALIDATION)},
        },
        "removed_duplicate_aliases": removed_duplicate_aliases,
        "canonical_duplicate_target_occurrences": canonical_occurrences,
        "superseded_observation_ids": sorted(superseded_observation_ids),
        "output": {"bytes": path.stat().st_size, "sha256": sha256(path)},
        "limitations": "Strong source-to-profile identity does not make heterogeneous denominator classes comparable or establish unique marginal access.",
    }
    receipt = OUT / "expected_profile_population_joins_validation_v1_1.json"
    receipt.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit("FAIL: population join validation did not pass")
    print(json.dumps({
        "status": status, "rows": len(output),
        "profiles_with_population_evidence": len(profiles_with_population_evidence),
        "profiles_without_population_evidence": len(unresolved),
        "csv_sha256": sha256(path), "validation_sha256": sha256(receipt),
    }, indent=2))


if __name__ == "__main__":
    main()
