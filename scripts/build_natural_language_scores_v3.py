from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_csv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"No rows for {name}")
    with (ROOT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def number(value: str | float | int | None) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def mean_semicolon(value: str) -> float | None:
    values = [number(item) for item in value.split(";") if item]
    values = [item for item in values if item is not None]
    return sum(values) / len(values) if values else None


def rank_desc(rows: list[dict[str, object]], field: str) -> dict[str, int]:
    ordered = sorted(
        rows,
        key=lambda row: (
            float(row[field]) if row[field] not in (None, "") else -1.0,
            float(row["population_base"]),
            str(row["intervention_id"]),
        ),
        reverse=True,
    )
    return {str(row["intervention_id"]): index for index, row in enumerate(ordered, 1)}


def reach_band(value: float) -> str:
    if value >= 50_000_000:
        return "R5_50m_plus"
    if value >= 10_000_000:
        return "R4_10m_to_49m"
    if value >= 1_000_000:
        return "R3_1m_to_9m"
    if value >= 100_000:
        return "R2_100k_to_999k"
    return "R1_below_100k"


def scarcity_band(value: float | None) -> str:
    if value is None:
        return "S_unknown"
    if value >= 0.80:
        return "S5_acutely_scarce_relative_proxy"
    if value >= 0.60:
        return "S4_high_scarcity_relative_proxy"
    if value >= 0.40:
        return "S3_middle_relative_proxy"
    if value >= 0.20:
        return "S2_lower_scarcity_relative_proxy"
    return "S1_resource_abundance_control_candidate"


def main() -> None:
    candidates = {row["intervention_id"]: row for row in read_csv("candidate_interventions_master.csv")}
    observations = {row["observation_id"]: row for row in read_csv("population_observations_master.csv")}
    context = {row["intervention_id"]: row for row in read_csv("candidate_context_features.csv")}
    education = {
        (row["territory"].casefold(), row["language_or_census_label"].casefold()): row
        for row in read_csv("education_access_observations.csv")
    }
    india_overlap = {
        row["census_language_category"].casefold(): row
        for row in read_csv("india_c17_overlap.csv")
    }
    compute_rows = read_csv("portfolio_compute_scenarios.csv")
    compute = {
        (row["portfolio_id"], row["adaptation_depth"], row["scenario"]): row
        for row in compute_rows
    }
    fr2 = {scenario: compute[("FR-2", "D3", scenario)] for scenario in ("low", "base", "high")}
    queue = read_csv("candidate_population_edge_curation_queue.csv")

    admitted_statuses = {"eligible_exact_gross_ceiling", "eligible_exact_direct_access_floor"}
    rows: list[dict[str, object]] = []
    intervention_counts: defaultdict[str, int] = defaultdict(int)

    for queued in queue:
        if queued["automatic_curation_status"] not in admitted_statuses:
            continue
        intervention_id = queued["intervention_id"]
        candidate = candidates[intervention_id]
        if candidate["target_type"] != "natural_language":
            continue
        observation = observations[queued["observation_id"]]
        feature = context[intervention_id]
        intervention_counts[intervention_id] += 1

        source_population_low = observation["population_low"]
        source_population_high = observation["population_high"]
        population_base = float(observation["population_base"])
        population_low = (
            float(source_population_low) if source_population_low else 0.0
        )
        population_high = (
            float(source_population_high) if source_population_high else population_base
        )
        if source_population_low and source_population_high:
            population_interval_status = "source_interval_or_exact_bounds"
        elif source_population_low:
            population_interval_status = "source_lower_bound_only_model_high_uses_reported_threshold"
        elif source_population_high:
            population_interval_status = "source_upper_bound_only_model_low_zero"
        else:
            population_interval_status = "source_point_without_interval_model_low_zero_high_point"
        direct_access_stratum = queued["automatic_curation_status"] == "eligible_exact_direct_access_floor"

        edu = education.get((observation["territory"].casefold(), observation["language_label"].casefold()))
        if direct_access_stratum:
            practical_low = practical_base = practical_high = 1.0
            practical_status = "source_population_already_restricted_to_direct_literacy_access_stratum"
            practical_source_id = observation["source_id"]
        elif edu and edu["literacy_rate"]:
            practical_low = practical_base = practical_high = float(edu["literacy_rate"])
            practical_status = "direct_language_specific_literacy_rate"
            practical_source_id = edu["source_id"]
        else:
            country_literacy_percent = mean_semicolon(feature["country_adult_literacy_percent_values"])
            practical_low = 0.0
            practical_base = country_literacy_percent / 100.0 if country_literacy_percent is not None else 0.5
            practical_high = 1.0
            practical_status = (
                "territory_adult_literacy_proxy_sensitivity"
                if country_literacy_percent is not None
                else "unmeasured_low0_neutral0.5_high1_sensitivity"
            )
            practical_source_id = "ACE-E021" if country_literacy_percent is not None else ""

        overlap = india_overlap.get(observation["language_label"].casefold()) if observation["territory"] == "India" else None
        if overlap:
            nonoverlap_low = float(overlap["nonoverlap_low"])
            nonoverlap_base = float(overlap["nonoverlap_base"])
            nonoverlap_high = float(overlap["nonoverlap_high"])
            nonoverlap_status = "India_C17_category_proxy_sensitivity"
            nonoverlap_source_id = overlap["source_id"]
        else:
            nonoverlap_low = 0.0
            nonoverlap_base = 0.5
            nonoverlap_high = 1.0
            nonoverlap_status = "unmeasured_low0_neutral0.5_high1_sensitivity"
            nonoverlap_source_id = ""

        # D=1 is absence of this exact FR-2 product, not an assertion that the
        # entire language population is educationally harmed.
        local_status = candidate["existing_local_status"].casefold()
        equal_basis_counterfactual = (
            "ex-ante equal-basis" in local_status
            or "ex-ante equal-treatment" in local_status
            or "ex-ante equal-basis" in candidate.get("notes", "").casefold()
            or "ex-ante equal-treatment" in candidate.get("notes", "").casefold()
        )
        target_status_clause = local_status.split(";", 1)[0]
        duplicate_exact_edition = (
            "complete" in target_status_clause
            and "missing" not in target_status_clause
            and "not_found" not in target_status_clause
            and not equal_basis_counterfactual
        )
        content_deficit = 0.0 if duplicate_exact_edition else 1.0
        comprehension = 1.0
        relevance = 1.0

        access_low = population_low * content_deficit * comprehension * practical_low * nonoverlap_low * relevance
        access_base = population_base * content_deficit * comprehension * practical_base * nonoverlap_base * relevance
        access_high = population_high * content_deficit * comprehension * practical_high * nonoverlap_high * relevance

        scarcity = number(feature["openalex_scarcity_percentile_among_observed_candidates"])
        scarcity_access = None if access_base is None or scarcity is None else access_base * scarcity
        base_million_tokens = float(fr2["base"]["gross_tokens"]) / 1_000_000.0
        low_million_tokens = float(fr2["low"]["gross_tokens"]) / 1_000_000.0
        high_million_tokens = float(fr2["high"]["gross_tokens"]) / 1_000_000.0

        tertiary_percent = mean_semicolon(feature["country_tertiary_enrollment_percent_values"])
        literacy_percent = mean_semicolon(feature["country_adult_literacy_percent_values"])
        if literacy_percent is not None and literacy_percent < 70:
            next_product = "MV-1"
            next_depth = "D2"
            foundational_gap = True
            curriculum_basis = "Territory adult-literacy proxy below 70%; the selected corpus lacks foundational numeracy/pre-algebra, so Algebra and Trigonometry is a second step rather than a substitute."
        elif tertiary_percent is not None and tertiary_percent >= 25 and population_base >= 10_000_000:
            next_product = "SB-1"
            next_depth = "D3"
            foundational_gap = False
            curriculum_basis = "Large exact population plus territory tertiary-enrollment proxy at or above 25%; scenario selects algebra/trigonometry plus statistics."
        elif tertiary_percent is not None and tertiary_percent >= 15:
            next_product = "MV-1"
            next_depth = "D3"
            foundational_gap = False
            curriculum_basis = "Territory tertiary-enrollment proxy at or above 15%; scenario selects a complete algebra/trigonometry bridge."
        else:
            next_product = "MV-1"
            next_depth = "D2"
            foundational_gap = False
            curriculum_basis = "Conservative default when exact learner-demand evidence is absent or the territory tertiary-enrollment proxy is below 15%."

        next_compute = {
            scenario: compute.get((next_product, next_depth, scenario))
            for scenario in ("low", "base", "high")
        }
        profile_tag_status = candidate.get("profile_tag_status", "")
        profile_ready = (
            "zzzz" not in candidate["variety_or_register"].casefold()
            and "unresolved" not in candidate["variety_or_register"].casefold()
            and profile_tag_status != "no_single_profile"
        )
        explicit_negative_control = (
            observation["negative_control"] == "true"
            or duplicate_exact_edition
            or candidate.get("profile_negative_control_status", "").startswith("negative_control")
        )
        abundance_control_candidate = scarcity is not None and scarcity < 0.20

        rows.append({
            "intervention_id": intervention_id,
            "target_name": candidate["target_name"],
            "target_profile": candidate["variety_or_register"],
            "target_profile_ready": str(profile_ready).lower(),
            "profile_tag_status": profile_tag_status,
            "profile_resolution_status": candidate.get("profile_resolution_status", ""),
            "profile_ranking_treatment": candidate.get("profile_ranking_treatment", ""),
            "resolved_edition_name": candidate.get("resolved_edition_name", "") or candidate["target_name"],
            "territory": observation["territory"],
            "observation_id": observation["observation_id"],
            "source_population_low_reported": source_population_low,
            "source_population_high_reported": source_population_high,
            "population_interval_status": population_interval_status,
            "population_low": f"{population_low:.0f}",
            "population_base": f"{population_base:.0f}",
            "population_high": f"{population_high:.0f}",
            "population_unit": observation["count_unit"],
            "population_measure": observation["measure_type"],
            "population_role": observation["alternative_measure_role"],
            "population_reference_year": observation["reference_date_or_year"],
            "population_source_id": observation["source_id"],
            "population_source_locator": observation["source_locator"],
            "reach_band": reach_band(population_base),
            "content_deficit_FR2": f"{content_deficit:.6f}",
            "comprehension_exact_target_conditional_on_standard_literacy": f"{comprehension:.6f}",
            "practical_access_low": f"{practical_low:.6f}",
            "practical_access_base": f"{practical_base:.6f}",
            "practical_access_high": f"{practical_high:.6f}",
            "practical_access_status": practical_status,
            "practical_access_source_id": practical_source_id,
            "academic_nonoverlap_low": f"{nonoverlap_low:.6f}",
            "academic_nonoverlap_base": f"{nonoverlap_base:.6f}",
            "academic_nonoverlap_high": f"{nonoverlap_high:.6f}",
            "academic_nonoverlap_status": nonoverlap_status,
            "academic_nonoverlap_source_id": nonoverlap_source_id,
            "marginal_access_low": f"{access_low:.0f}",
            "marginal_access_base_sensitivity": f"{access_base:.0f}",
            "marginal_access_high": f"{access_high:.0f}",
            "gross_ceiling_per_million_base_tokens": f"{population_base / base_million_tokens:.3f}",
            "conservative_access_per_million_high_tokens": f"{access_low / high_million_tokens:.3f}",
            "neutral_access_per_million_base_tokens": f"{access_base / base_million_tokens:.3f}",
            "optimistic_access_per_million_low_tokens": f"{access_high / low_million_tokens:.3f}",
            "openalex_math_open_access": feature["openalex_math_open_access"],
            "openalex_math_open_access_books": feature["openalex_math_open_access_books"],
            "scarcity_relative_percentile": "" if scarcity is None else f"{scarcity:.6f}",
            "scarcity_band": scarcity_band(scarcity),
            "scarcity_adjusted_access_base": "" if scarcity_access is None else f"{scarcity_access:.0f}",
            "ai_support_resource_levels": feature["ai_support_resource_levels"],
            "internet_percent_context": feature["country_internet_percent_values"],
            "electricity_percent_context": feature["country_electricity_percent_values"],
            "tertiary_enrollment_percent_context": feature["country_tertiary_enrollment_percent_values"],
            "fr2_units": fr2["base"]["editable_units"],
            "fr2_source_tokens": fr2["base"]["source_tokens_before_depth"],
            "fr2_gross_tokens_low": fr2["low"]["gross_tokens"],
            "fr2_gross_tokens_base": fr2["base"]["gross_tokens"],
            "fr2_gross_tokens_high": fr2["high"]["gross_tokens"],
            "fr2_api_equivalent_usd_base": fr2["base"]["api_equivalent_usd"],
            "recommended_openstax_next_product": next_product,
            "recommended_openstax_depth": next_depth,
            "foundational_numeracy_pre_algebra_source_gap": str(foundational_gap).lower(),
            "curriculum_selection_basis": curriculum_basis,
            "openstax_next_gross_tokens_low": "" if next_compute["low"] is None else next_compute["low"]["gross_tokens"],
            "openstax_next_gross_tokens_base": "" if next_compute["base"] is None else next_compute["base"]["gross_tokens"],
            "openstax_next_gross_tokens_high": "" if next_compute["high"] is None else next_compute["high"]["gross_tokens"],
            "explicit_negative_control": str(explicit_negative_control).lower(),
            "resource_abundance_control_candidate": str(abundance_control_candidate).lower(),
            "recommendation_eligibility": "exclude_duplicate_or_explicit_control" if explicit_negative_control else ("target_profile_evidence_pending" if not profile_ready else "provisional_eligible"),
            "interpretation": "Population values retain the source universe and reported interval status. Missing population intervals use a zero-to-point ranking sensitivity; missing practical access or academic overlap uses low 0, neutral 0.5, high 1. Base access is therefore a labelled sensitivity, not a measured harmed-population count.",
        })

    duplicate_edges = {key: count for key, count in intervention_counts.items() if count > 1}
    if duplicate_edges:
        raise RuntimeError(f"Multiple admitted edges require explicit set aggregation: {duplicate_edges}")

    rank_fields = {
        "gross_ceiling_rank": "population_base",
        "conservative_efficiency_rank": "conservative_access_per_million_high_tokens",
        "neutral_efficiency_rank": "neutral_access_per_million_base_tokens",
        "optimistic_efficiency_rank": "optimistic_access_per_million_low_tokens",
        "scarcity_adjusted_rank": "scarcity_adjusted_access_base",
    }
    rank_maps = {name: rank_desc(rows, field) for name, field in rank_fields.items()}
    for row in rows:
        intervention_id = str(row["intervention_id"])
        ranks = []
        for rank_name, mapping in rank_maps.items():
            row[rank_name] = mapping[intervention_id]
            ranks.append(mapping[intervention_id])
        row["rank_best_across_views"] = min(ranks)
        row["rank_worst_across_views"] = max(ranks)

    rows.sort(key=lambda row: int(row["gross_ceiling_rank"]))
    write_csv("natural_language_scores_v3.csv", rows)
    print({
        "rows": len(rows),
        "profile_ready": sum(row["target_profile_ready"] == "true" for row in rows),
        "profile_pending": sum(row["target_profile_ready"] == "false" for row in rows),
        "direct_access_floor_rows": sum("direct_literacy" in str(row["practical_access_status"]) or "direct_literacy" in str(row["population_measure"]) for row in rows),
        "explicit_controls": sum(row["explicit_negative_control"] == "true" for row in rows),
        "top_gross": rows[0]["target_name"] if rows else None,
    })


if __name__ == "__main__":
    main()
