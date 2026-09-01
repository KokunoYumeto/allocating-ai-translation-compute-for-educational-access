#!/usr/bin/env python3
"""Build denominator-stratified opportunity, access, and forward-residual tables.

This is an additive v1.1 analysis layer.  It deliberately does not replace the
existing portfolio or manuscript tables.  Three estimands are kept separate:

* Table A: an ex-ante gross-opportunity *screen* over source-reported population
  measures.  Heterogeneous measures are labelled and receive ranks only within
  their measure class.
* Table B: target-readable access sensitivities.  Proxy and ignorance-midpoint
  factors remain explicit; the conservative all-zero view receives one tie
  interval rather than manufactured unique ranks.
* Table C: forward residual work after verified current coverage.  Exact completed
  units receive D=0.  Unknown residual units, token fractions, or workloads stay
  blank and unranked.

The script fails closed on missing columns, joins, expected coverage assertions,
duplicate IDs, or arithmetic inconsistencies.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]

INPUTS = {
    "natural_scores": ROOT / "natural_language_scores_v3.csv",
    "expansion_scores": ROOT / "candidate_expansion_scores.csv",
    "portfolio": ROOT / "portfolio_linguistic_candidates.csv",
    "candidates": ROOT / "candidate_interventions_master.csv",
    "observations": ROOT / "population_observations_master.csv",
    "compute": ROOT / "portfolio_compute_scenarios.csv",
}

OUTPUTS = {
    "table_a": ROOT / "table_a_ex_ante_gross_opportunity.csv",
    "table_b": ROOT / "table_b_target_readable_access_sensitivity.csv",
    "table_c": ROOT / "table_c_forward_residual_commissioning.csv",
    "validation": ROOT / "denominator_stratified_rankings_v1_1_validation.json",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def read_csv(path: Path, required: Iterable[str]) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing = set(required) - fields
        if missing:
            raise ValueError(f"{path.name} lacks required columns: {sorted(missing)}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path.name} has no data rows")
    return rows


def unique_index(rows: list[dict[str, str]], key: str, label: str) -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {}
    for row in rows:
        value = row.get(key, "")
        if not value:
            raise ValueError(f"Blank {key} in {label}")
        if value in index:
            raise ValueError(f"Duplicate {key}={value!r} in {label}")
        index[value] = row
    return index


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty output {path.name}")
    fields = list(rows[0])
    if any(list(row) != fields for row in rows):
        raise ValueError(f"Nonuniform row schema for {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def number(value: str | int | float | None, *, field: str) -> float:
    if value in (None, ""):
        raise ValueError(f"Required numeric field {field} is blank")
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"Required numeric field {field} is not finite: {value!r}")
    return parsed


def integer(value: str | int | float | None, *, field: str) -> int:
    parsed = number(value, field=field)
    rounded = round(parsed)
    if abs(parsed - rounded) > 1e-9:
        raise ValueError(f"Required integer field {field} is not integral: {value!r}")
    return rounded


def fmt_number(value: float) -> str:
    return f"{value:.6f}"


def split_values(value: str) -> list[str]:
    return [part for part in value.split(";") if part]


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
        "home_language", "spoken_at_home", "language_used_at_home",
        "languages_used_at_home", "spoken_in_household", "daily_language_at_home",
        "daily_use_outside_education", "usually_spoken_at_home", "principal_language",
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


def competition_intervals(rows: list[dict[str, object]], field: str) -> dict[str, tuple[int, int]]:
    ordered = sorted(
        rows,
        key=lambda row: (-float(row[field]), str(row["intervention_id"])),
    )
    result: dict[str, tuple[int, int]] = {}
    start = 0
    while start < len(ordered):
        value = float(ordered[start][field])
        end = start
        while end + 1 < len(ordered) and float(ordered[end + 1][field]) == value:
            end += 1
        for position in range(start, end + 1):
            result[str(ordered[position]["intervention_id"])] = (start + 1, end + 1)
        start = end + 1
    return result


def evidence_class(practical_status: str, nonoverlap_status: str) -> str:
    statuses = f"{practical_status};{nonoverlap_status}".casefold()
    has_unknown = "unmeasured" in statuses
    has_proxy = "proxy" in statuses
    if has_unknown and has_proxy:
        return "proxy_plus_ignorance_midpoint"
    if has_unknown:
        return "contains_ignorance_midpoint"
    if has_proxy:
        return "contains_proxy"
    return "direct_or_source_restricted_factors"


def require_contains(row: dict[str, str], field: str, pattern: str, label: str) -> re.Match[str]:
    value = row.get(field, "")
    match = re.search(pattern, value, flags=re.IGNORECASE)
    if match is None:
        raise ValueError(f"{label}: {field} does not match required evidence pattern {pattern!r}: {value!r}")
    return match


def main() -> None:
    natural = read_csv(
        INPUTS["natural_scores"],
        {
            "intervention_id", "target_name", "target_profile", "territory",
            "observation_id", "population_low", "population_base", "population_high",
            "population_measure", "content_deficit_FR2",
            "comprehension_exact_target_conditional_on_standard_literacy",
            "practical_access_low", "practical_access_base", "practical_access_high",
            "practical_access_status", "academic_nonoverlap_low",
            "academic_nonoverlap_base", "academic_nonoverlap_high",
            "academic_nonoverlap_status", "marginal_access_low",
            "marginal_access_base_sensitivity", "marginal_access_high",
            "conservative_access_per_million_high_tokens",
        },
    )
    expansion = read_csv(INPUTS["expansion_scores"], set(natural[0]))
    score_by_id = unique_index(natural + expansion, "intervention_id", "combined score rows")

    portfolio = read_csv(
        INPUTS["portfolio"],
        {
            "intervention_id", "intervention_type", "intervention_name", "target_profiles",
            "territory_or_scope", "population_low", "population_base", "population_high",
            "population_measure", "population_years", "population_observation_ids",
            "population_source_ids", "gross_tokens_low", "gross_tokens_base",
            "gross_tokens_high", "gross_people_per_million_base_tokens",
            "marginal_access_low", "marginal_access_base_sensitivity",
            "marginal_access_high", "base_marginal_access_per_million_tokens",
            "conservative_access_per_million_tokens", "optimistic_access_per_million_tokens",
            "scarcity_adjusted_access_per_million_tokens", "base_efficiency_rank_low",
            "base_efficiency_rank_high", "gross_efficiency_rank_low",
            "gross_efficiency_rank_high", "conservative_efficiency_rank_low",
            "conservative_efficiency_rank_high", "optimistic_efficiency_rank_low",
            "optimistic_efficiency_rank_high", "scarcity_efficiency_rank_low",
            "scarcity_efficiency_rank_high", "portfolio_position",
        },
    )
    portfolio_by_id = unique_index(portfolio, "intervention_id", "portfolio")
    missing_scores = sorted(set(portfolio_by_id) - set(score_by_id))
    if missing_scores:
        raise ValueError(f"Portfolio rows lack source factor rows: {missing_scores}")

    candidate_rows = read_csv(
        INPUTS["candidates"],
        {
            "intervention_id", "target_name", "variety_or_register", "territory_scope",
            "curriculum_unit", "adaptation_depth", "existing_local_status", "source_ids",
            "evidence_status", "overlap_rule", "notes",
        },
    )
    candidates = unique_index(candidate_rows, "intervention_id", "candidate master")
    # Expansion rows are canonical score/portfolio rows but intentionally are not
    # duplicated into the seed candidate master.  Candidate-master membership is
    # therefore required only for the four explicit forward profiles below.

    observation_rows = read_csv(
        INPUTS["observations"],
        {
            "observation_id", "learner_stratum", "measure_type", "count_unit",
            "population_low", "population_base", "population_high",
            "reference_date_or_year", "source_id", "source_locator", "caveats",
        },
    )
    observations = unique_index(observation_rows, "observation_id", "population observations")

    compute_rows = read_csv(
        INPUTS["compute"],
        {
            "portfolio_id", "adaptation_depth", "scenario", "source_tokens_before_depth",
            "editable_units", "gross_tokens",
        },
    )
    compute_index: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in compute_rows:
        key = (row["portfolio_id"], row["adaptation_depth"], row["scenario"])
        if key in compute_index:
            raise ValueError(f"Duplicate compute row {key}")
        compute_index[key] = row
    fr2_compute = {
        scenario: compute_index.get(("FR-2", "D3", scenario))
        for scenario in ("low", "base", "high")
    }
    if any(row is None for row in fr2_compute.values()):
        raise ValueError("Missing FR-2/D3 low/base/high compute rows")
    fr2_units = {integer(row["editable_units"], field="FR-2 editable_units") for row in fr2_compute.values() if row}
    fr2_source_tokens = {integer(row["source_tokens_before_depth"], field="FR-2 source tokens") for row in fr2_compute.values() if row}
    if len(fr2_units) != 1 or len(fr2_source_tokens) != 1:
        raise ValueError("FR-2 unit or source-token denominator changes across scenarios")
    fr2_unit_count = next(iter(fr2_units))
    fr2_source_token_count = next(iter(fr2_source_tokens))

    # Table A: global order is only a descriptive screen.  Cardinal ranks are
    # computed solely inside exact measure classes.
    table_a_work: list[dict[str, object]] = []
    for row in portfolio:
        intervention_id = row["intervention_id"]
        observation_ids = split_values(row["population_observation_ids"])
        if len(observation_ids) != 1:
            raise ValueError(
                f"Table A requires one canonical source observation per row; "
                f"{intervention_id} has {observation_ids}"
            )
        observation = observations.get(observation_ids[0])
        if observation is None:
            raise ValueError(f"Unknown observation {observation_ids[0]} for {intervention_id}")
        if observation["measure_type"] != row["population_measure"]:
            raise ValueError(
                f"Measure mismatch for {intervention_id}: portfolio={row['population_measure']!r}, "
                f"observation={observation['measure_type']!r}"
            )
        population_base = integer(row["population_base"], field=f"{intervention_id}.population_base")
        observed_base = integer(observation["population_base"], field=f"{observation_ids[0]}.population_base")
        if population_base != observed_base:
            raise ValueError(f"Population mismatch for {intervention_id}: {population_base} != {observed_base}")
        gross_tokens = integer(row["gross_tokens_base"], field=f"{intervention_id}.gross_tokens_base")
        gross_efficiency = number(
            row["gross_people_per_million_base_tokens"],
            field=f"{intervention_id}.gross_people_per_million_base_tokens",
        )
        recomputed = population_base * 1_000_000 / gross_tokens
        if abs(recomputed - gross_efficiency) > 0.01:
            raise ValueError(f"Gross-efficiency mismatch for {intervention_id}: {recomputed} != {gross_efficiency}")
        table_a_work.append({
            "intervention_id": intervention_id,
            "intervention_name": row["intervention_name"],
            "target_profile": row["target_profiles"],
            "territory": row["territory_or_scope"],
            "source_year": observation["reference_date_or_year"],
            "population_measure_class": measure_class(row["population_measure"]),
            "source_population_measure": row["population_measure"],
            "learner_or_age_stratum": observation["learner_stratum"],
            "source_population_ceiling": population_base,
            "source_population_low": row["population_low"],
            "source_population_high": row["population_high"],
            "population_source_id": observation["source_id"],
            "population_source_locator": observation["source_locator"],
            "FR2_D3_base_gross_tokens": gross_tokens,
            "gross_ceiling_per_million_base_tokens": f"{gross_efficiency:.3f}",
            "_gross_score": gross_efficiency,
        })

    by_measure: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in table_a_work:
        by_measure[str(row["population_measure_class"])].append(row)
    within_class: dict[str, tuple[int, int]] = {}
    for rows in by_measure.values():
        within_class.update(competition_intervals(rows, "_gross_score"))
    table_a_work.sort(
        key=lambda row: (-float(row["_gross_score"]), str(row["intervention_id"]))
    )
    table_a: list[dict[str, object]] = []
    for screen_order, row in enumerate(table_a_work, 1):
        low, high = within_class[str(row["intervention_id"])]
        table_a.append({
            "gross_screen_order_descriptive": screen_order,
            "intervention_id": row["intervention_id"],
            "intervention_name": row["intervention_name"],
            "target_profile": row["target_profile"],
            "territory": row["territory"],
            "source_year": row["source_year"],
            "population_measure_class": row["population_measure_class"],
            "source_population_measure": row["source_population_measure"],
            "learner_or_age_stratum": row["learner_or_age_stratum"],
            "source_population_ceiling": row["source_population_ceiling"],
            "source_population_low": row["source_population_low"],
            "source_population_high": row["source_population_high"],
            "population_source_id": row["population_source_id"],
            "population_source_locator": row["population_source_locator"],
            "FR2_D3_base_gross_tokens": row["FR2_D3_base_gross_tokens"],
            "gross_ceiling_per_million_base_tokens": row["gross_ceiling_per_million_base_tokens"],
            "within_measure_class_rank_low": low,
            "within_measure_class_rank_high": high,
            "cross_measure_rank_status": "not_estimated_heterogeneous_population_measures",
            "interpretation": "Ex-ante gross opportunity screen only; not a harmed-person, comfortable-reader, or forward-commissioning estimate.",
        })

    # Table B: retain the exact current factor model but expose its evidence class.
    # Conservative ranks are recomputed tie-aware from the final cardinal set.
    conservative_rows = [
        {
            "intervention_id": row["intervention_id"],
            "score": number(row["conservative_access_per_million_tokens"], field="conservative score"),
        }
        for row in portfolio
    ]
    conservative_intervals = competition_intervals(conservative_rows, "score")
    table_b: list[dict[str, object]] = []
    for row in sorted(portfolio, key=lambda item: integer(item["portfolio_position"], field="portfolio_position")):
        intervention_id = row["intervention_id"]
        score = score_by_id[intervention_id]
        observation_id = score["observation_id"]
        observation = observations.get(observation_id)
        if observation is None:
            raise ValueError(f"Unknown observation {observation_id} for {intervention_id}")
        if observation_id != row["population_observation_ids"]:
            raise ValueError(f"Score/portfolio observation mismatch for {intervention_id}")

        n_low = number(row["population_low"], field=f"{intervention_id}.population_low")
        n_base = number(row["population_base"], field=f"{intervention_id}.population_base")
        n_high = number(row["population_high"], field=f"{intervention_id}.population_high")
        d = number(score["content_deficit_FR2"], field=f"{intervention_id}.D")
        c = number(
            score["comprehension_exact_target_conditional_on_standard_literacy"],
            field=f"{intervention_id}.C",
        )
        p_values = [
            number(score[field], field=f"{intervention_id}.{field}")
            for field in ("practical_access_low", "practical_access_base", "practical_access_high")
        ]
        u_values = [
            number(score[field], field=f"{intervention_id}.{field}")
            for field in ("academic_nonoverlap_low", "academic_nonoverlap_base", "academic_nonoverlap_high")
        ]
        populations = [n_low, n_base, n_high]
        readable = [populations[i] * c * p_values[i] for i in range(3)]
        recomputed_ma = [readable[i] * d * u_values[i] for i in range(3)]
        reported_ma = [
            number(row[field], field=f"{intervention_id}.{field}")
            for field in ("marginal_access_low", "marginal_access_base_sensitivity", "marginal_access_high")
        ]
        tolerance = max(2.0, n_base * 0.000002)
        if any(abs(recomputed_ma[i] - reported_ma[i]) > tolerance for i in range(3)):
            raise ValueError(
                f"Marginal-access formula mismatch for {intervention_id}: "
                f"computed={recomputed_ma}, reported={reported_ma}, tolerance={tolerance}"
            )
        cons_low, cons_high = conservative_intervals[intervention_id]
        table_b.append({
            "portfolio_exposure_position": row["portfolio_position"],
            "intervention_id": intervention_id,
            "intervention_name": row["intervention_name"],
            "target_profile": row["target_profiles"],
            "territory": row["territory_or_scope"],
            "population_observation_id": observation_id,
            "population_measure_class": measure_class(row["population_measure"]),
            "source_population_measure": row["population_measure"],
            "learner_or_age_stratum": observation["learner_stratum"],
            "source_year": observation["reference_date_or_year"],
            "population_low": row["population_low"],
            "population_base": row["population_base"],
            "population_high": row["population_high"],
            "content_deficit_D_ex_ante": score["content_deficit_FR2"],
            "target_identity_C_conditional_on_standard_literacy": score["comprehension_exact_target_conditional_on_standard_literacy"],
            "target_readable_N_low": f"{readable[0]:.0f}",
            "target_readable_N_base_sensitivity": f"{readable[1]:.0f}",
            "target_readable_N_high": f"{readable[2]:.0f}",
            "practical_access_P_low": score["practical_access_low"],
            "practical_access_P_base": score["practical_access_base"],
            "practical_access_P_high": score["practical_access_high"],
            "practical_access_evidence_status": score["practical_access_status"],
            "academic_nonoverlap_U_low": score["academic_nonoverlap_low"],
            "academic_nonoverlap_U_base": score["academic_nonoverlap_base"],
            "academic_nonoverlap_U_high": score["academic_nonoverlap_high"],
            "academic_nonoverlap_evidence_status": score["academic_nonoverlap_status"],
            "factor_evidence_class": evidence_class(score["practical_access_status"], score["academic_nonoverlap_status"]),
            "marginal_access_low": row["marginal_access_low"],
            "marginal_access_base_sensitivity": row["marginal_access_base_sensitivity"],
            "marginal_access_high": row["marginal_access_high"],
            "base_midpoint_sensitivity_per_million_tokens": row["base_marginal_access_per_million_tokens"],
            "base_midpoint_sensitivity_rank_low": row["base_efficiency_rank_low"],
            "base_midpoint_sensitivity_rank_high": row["base_efficiency_rank_high"],
            "conservative_score_per_million_tokens": row["conservative_access_per_million_tokens"],
            "conservative_rank_low": cons_low,
            "conservative_rank_high": cons_high,
            "optimistic_sensitivity_per_million_tokens": row["optimistic_access_per_million_tokens"],
            "optimistic_sensitivity_rank_low": row["optimistic_efficiency_rank_low"],
            "optimistic_sensitivity_rank_high": row["optimistic_efficiency_rank_high"],
            "bibliographic_scarcity_proxy_per_million_tokens": row["scarcity_adjusted_access_per_million_tokens"],
            "bibliographic_scarcity_proxy_rank_low": row["scarcity_efficiency_rank_low"],
            "bibliographic_scarcity_proxy_rank_high": row["scarcity_efficiency_rank_high"],
            "direct_evidence_rank_status": (
                "not_directly_rankable_contains_proxy_or_ignorance_midpoint"
                if evidence_class(score["practical_access_status"], score["academic_nonoverlap_status"])
                != "direct_or_source_restricted_factors"
                else "factor_sources_direct_or_source_restricted_but_population_measure_class_still_controls_comparability"
            ),
            "interpretation": "Base and optimistic values are factor-model sensitivities. Neutral 0.5 values are ignorance midpoints, not empirical estimates; cross-measure population comparisons remain descriptive.",
        })

    # Table C: explicit, nonadditive work-level forward rows for the four profiles.
    forward_ids = ("NAT-122", "NAT-121", "NAT-124", "NAT-123")
    for intervention_id in forward_ids:
        if intervention_id not in candidates or intervention_id not in portfolio_by_id:
            raise ValueError(f"Missing required forward profile {intervention_id}")

    cn = candidates["NAT-122"]
    idn = candidates["NAT-121"]
    hi = candidates["NAT-124"]
    ja = candidates["NAT-123"]
    require_contains(cn, "existing_local_status", r"Open Logic 722 of 722", "Chinese Open Logic")
    require_contains(cn, "existing_local_status", r"Algebra and Trigonometry 2e 94 of 94", "Chinese Algebra and Trigonometry")
    calc_match = require_contains(cn, "existing_local_status", r"Calculus Volume 1 (\d+) of (\d+)", "Chinese Calculus I")
    calc_complete, calc_total = map(int, calc_match.groups())
    if not (0 <= calc_complete < calc_total):
        raise ValueError("Chinese Calculus coverage must be partial")
    require_contains(cn, "existing_local_status", r"six additional fixed STEM books pending", "Chinese fixed STEM")
    require_contains(idn, "existing_local_status", r"Open Logic complete 722 of 722", "Indonesian Open Logic")
    id_roles = require_contains(
        idn,
        "existing_local_status",
        r"(\d+) of (\d+) roles published and (\d+) in production",
        "Indonesian program roles",
    )
    id_published, id_total, id_production = map(int, id_roles.groups())
    if id_published + id_production != id_total:
        raise ValueError("Indonesian published/production role counts do not close")
    require_contains(hi, "existing_local_status", r"complete local Hindi formal-reasoning edition", "Hindi FR-2")
    if hi["curriculum_unit"] != "FR-2" or hi["adaptation_depth"] != "D3":
        raise ValueError("Hindi completed formal-reasoning row is not the FR-2/D3 comparator")
    require_contains(ja, "existing_local_status", r"no complete exact local FR-2 edition registered", "Japanese FR-2")

    def forward_common(intervention_id: str) -> dict[str, object]:
        candidate = candidates[intervention_id]
        portfolio_row = portfolio_by_id[intervention_id]
        observation_id = portfolio_row["population_observation_ids"]
        observation = observations[observation_id]
        return {
            "intervention_id": intervention_id,
            "target_name": portfolio_row["intervention_name"],
            "target_profile": portfolio_row["target_profiles"],
            "territory": portfolio_row["territory_or_scope"],
            "population_observation_id": observation_id,
            "population_measure_class": measure_class(portfolio_row["population_measure"]),
            "source_population_base": portfolio_row["population_base"],
            "population_source_id": observation["source_id"],
            "candidate_source_ids": candidate["source_ids"],
        }

    table_c: list[dict[str, object]] = []

    def add_forward(
        row_id: str,
        intervention_id: str,
        work_or_gap: str,
        stage: str,
        format_scope: str,
        unit_type: str,
        total_units: str | int,
        complete_units: str | int,
        residual_units: str | int,
        residual_status: str,
        d_forward: str,
        d_status: str,
        existing_coverage: str,
        next_action: str,
        need_status: str,
        evidence_basis: str,
    ) -> None:
        common = forward_common(intervention_id)
        completed_exact = d_forward == "0.000000"
        table_c.append({
            "forward_row_id": row_id,
            **common,
            "decision_frame": "current_forward_allocation_after_verified_coverage",
            "exact_work_stage_format": work_or_gap,
            "curriculum_or_research_stage": stage,
            "format_scope": format_scope,
            "unit_type": unit_type,
            "total_units": total_units,
            "verified_complete_units": complete_units,
            "residual_units": residual_units,
            "residual_units_status": residual_status,
            "content_deficit_D_forward": d_forward,
            "content_deficit_status": d_status,
            "incremental_gross_tokens_low": "0" if completed_exact else "",
            "incremental_gross_tokens_base": "0" if completed_exact else "",
            "incremental_gross_tokens_high": "0" if completed_exact else "",
            "forward_marginal_access_low": "0" if completed_exact else "",
            "forward_marginal_access_base_sensitivity": "0" if completed_exact else "",
            "forward_marginal_access_high": "0" if completed_exact else "",
            "forward_efficiency_per_million_tokens": "",
            "forward_rank_low": "",
            "forward_rank_high": "",
            "verified_existing_coverage": existing_coverage,
            "next_nonduplicative_action": next_action,
            "need_evidence_status": need_status,
            "coverage_evidence_basis": evidence_basis,
            "duplication_rule": "Completed exact units receive D=0 and no duplicate benefit; unknown residual units or tokens remain blank and unranked.",
        })

    add_forward(
        "FWD-CN-OLP", "NAT-122", "Open Logic complete target set", "formal_reasoning",
        "registered exact Chinese edition", "modules", 722, 722, 0,
        "exact_complete_unit_count", "0.000000", "exact_completed_corpus",
        "Open Logic 722/722", "Do not retranslate; commission only a separately demonstrated format or semantic-access derivative.",
        "complete_exact_corpus", cn["existing_local_status"],
    )
    add_forward(
        "FWD-CN-AT2E", "NAT-122", "Algebra and Trigonometry 2e", "upper_secondary_to_undergraduate_bridge",
        "registered exact Chinese edition", "modules", 94, 94, 0,
        "exact_complete_unit_count", "0.000000", "exact_completed_corpus",
        "Algebra and Trigonometry 2e 94/94", "Do not retranslate; audit only accessibility, maintenance, or edition-version residuals.",
        "complete_exact_corpus", cn["existing_local_status"],
    )
    add_forward(
        "FWD-CN-CALC1", "NAT-122", "Calculus Volume 1", "undergraduate",
        "registered Chinese course modules", "modules", calc_total, calc_complete, calc_total - calc_complete,
        "exact_module_residual_but_source_token_fraction_unmeasured", "", "unknown_until_residual_source_tokens_are_measured",
        f"Calculus Volume 1 {calc_complete}/{calc_total}", "Finish the exact residual after measuring residual source tokens; do not infer D from module count alone.",
        "partial_exact_corpus_with_unknown_token_weight", cn["existing_local_status"],
    )
    add_forward(
        "FWD-CN-STEM6", "NAT-122", "Six further fixed STEM books", "multidisciplinary_undergraduate",
        "six candidate titles in the current program ledger; completion not audited", "candidate_books", 6, "", "",
        "six_candidate_titles_not_six_verified_residuals", "", "unknown_work_weight",
        "Six candidate STEM titles; completion and residual unknown", "Audit exact titles, current unit coverage, source tokens, and local supply before ordering.",
        "bounded_program_gap_not_yet_compute_rankable", cn["existing_local_status"],
    )
    add_forward(
        "FWD-CN-ACCESS-FRONTIER", "NAT-122", "Semantic accessibility and demonstrated advanced/research-frontier gaps", "accessibility_postgraduate_research",
        "HTML/MathML/offline/advanced corpus scope unresolved", "unknown", "", "", "",
        "unknown_scope", "", "unknown_until_exact_target_work_format_is_registered",
        "No exact cardinal residual registered", "Define exact format or advanced corpus first; then measure its source and residual units.",
        "research_assignment_not_cardinal_score", f"{cn['evidence_status']} | {cn['notes']}",
    )

    add_forward(
        "FWD-ID-OLP", "NAT-121", "Open Logic complete target set", "formal_reasoning",
        "registered exact Indonesian edition", "modules", 722, 722, 0,
        "exact_complete_unit_count", "0.000000", "exact_completed_corpus",
        "Open Logic 722/722", "Do not retranslate; preserve and maintain the completed corpus.",
        "complete_exact_corpus", idn["existing_local_status"],
    )
    add_forward(
        "FWD-ID-PROGRAM13", "NAT-121", "Nonpublic roles in the registered 40-course program", "multi_stage_mathematics_program",
        "course-role publication status; heterogeneous works", "course_roles", id_total, id_published, id_production,
        "13_not_public_roles_but_partial_content_and_token_residuals_unknown", "", "unknown_heterogeneous_role_weights",
        f"{id_published}/{id_total} roles published; {id_production} in production", "Select an exact role, work, version, and format; then measure its remaining source tokens.",
        "bounded_program_roles_not_yet_compute_comparable", idn["existing_local_status"],
    )
    add_forward(
        "FWD-ID-ACCESS", "NAT-121", "Accessibility, offline-delivery, and maintenance residuals", "cross_stage_accessibility",
        "format-specific scope unresolved", "unknown", "", "", "",
        "unknown_scope", "", "unknown_until_exact_format_gap_is_registered",
        "No exact cardinal residual registered", "Audit each published role for semantic HTML/MathML, screen-reader, offline, and maintenance gaps.",
        "research_assignment_not_cardinal_score", f"{idn['evidence_status']} | {idn['notes']}",
    )

    add_forward(
        "FWD-HI-FR2", "NAT-124", "FR-2 Formal Reasoning Core at D3", "formal_reasoning",
        "registered exact Hindi edition", "editable_units", fr2_unit_count, fr2_unit_count, 0,
        "exact_completed_comparator_mapping", "0.000000", "exact_completed_corpus",
        f"Complete local Hindi FR-2/D3 edition; comparator has {fr2_unit_count} units and {fr2_source_token_count} source alpha tokens",
        "Do not retranslate FR-2; commission only a separately demonstrated subject, stage, or format residual.",
        "complete_exact_corpus", hi["existing_local_status"],
    )
    add_forward(
        "FWD-HI-OTHER", "NAT-124", "Uncovered Hindi subject, stage, and accessibility residuals", "cross_stage",
        "exact work/format unresolved", "unknown", "", "", "",
        "unknown_scope", "", "unknown_until_exact_target_work_format_is_registered",
        "Only the completed formal-reasoning edition is credited", "Name and audit an exact missing work, stage, and format before computing a residual score.",
        "research_assignment_not_cardinal_score", f"{hi['evidence_status']} | {hi['notes']}",
    )

    add_forward(
        "FWD-JA-FR2", "NAT-123", "FR-2 Formal Reasoning Core at D3", "formal_reasoning",
        "current task-local exact-edition register", "editable_units", fr2_unit_count, "", "",
        "no_complete_exact_edition_registered_but_partial_unit_count_unknown", "", "unknown_partial_or_missing_fraction",
        "No complete exact local FR-2 edition is registered; this does not prove zero translated units or zero substitute supply.",
        "Audit exact local/open equivalents and any partial FR-2 units before deciding whether FR-2 itself is the next product.",
        "stage_specific_supply_audit_required", ja["existing_local_status"],
    )
    add_forward(
        "FWD-JA-STAGE", "NAT-123", "Proof bridge, semantic accessibility, postgraduate, monograph, and research-frontier gaps", "undergraduate_to_research_and_accessibility",
        "exact work/format unresolved", "unknown", "", "", "",
        "unknown_scope", "", "unknown_until_exact_target_work_format_is_registered",
        "Strong compulsory-school and advanced supply is registered; exact open/accessibility/frontier residuals are not.",
        "Commission only the exact stage/corpus/format gap established by the needs audit; do not infer a generic school-algebra need.",
        "research_assignment_not_cardinal_score", f"{ja['evidence_status']} | {ja['notes']}",
    )

    write_csv(OUTPUTS["table_a"], table_a)
    write_csv(OUTPUTS["table_b"], table_b)
    write_csv(OUTPUTS["table_c"], table_c)

    table_a_ids = [str(row["intervention_id"]) for row in table_a]
    table_b_ids = [str(row["intervention_id"]) for row in table_b]
    conservative_scores = {str(row["conservative_score_per_million_tokens"]) for row in table_b}
    conservative_intervals_found = {
        (str(row["conservative_rank_low"]), str(row["conservative_rank_high"]))
        for row in table_b
    }
    expected_zero_interval = {("1", str(len(table_b)))}
    if conservative_scores == {"0.000"} and conservative_intervals_found != expected_zero_interval:
        raise ValueError(
            f"Conservative zero scores must have one [1,{len(table_b)}] interval; "
            f"found {conservative_intervals_found}"
        )
    completed_rows = [row for row in table_c if row["content_deficit_D_forward"] == "0.000000"]
    if any(str(row["residual_units"]) != "0" for row in completed_rows):
        raise ValueError("A D=0 completed row has nonzero residual units")
    if any(row["forward_rank_low"] or row["forward_rank_high"] for row in table_c):
        raise ValueError("Forward residual rows must remain unranked until residual compute is measured")

    validation = {
        "schema": "interlanguage/denominator-stratified-rankings-validation/1.0.0",
        "build": "build_denominator_stratified_rankings_v1_1.py",
        "estimands": {
            "table_a": "ex_ante gross opportunity screen; ranks only within source-measure classes",
            "table_b": "target-readable factor sensitivities; proxy and ignorance midpoints explicit",
            "table_c": "forward residual work after verified coverage; unknown residuals unranked",
        },
        "input_files": {
            key: {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}
            for key, path in INPUTS.items()
        },
        "output_files": {
            key: {
                "path": str(path),
                "rows": len({"table_a": table_a, "table_b": table_b, "table_c": table_c}[key]),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for key, path in OUTPUTS.items()
            if key != "validation"
        },
        "checks": {
            "portfolio_rows": len(portfolio),
            "table_a_rows_equal_portfolio": len(table_a) == len(portfolio),
            "table_b_rows_equal_portfolio": len(table_b) == len(portfolio),
            "table_a_unique_intervention_ids": len(table_a_ids) == len(set(table_a_ids)),
            "table_b_unique_intervention_ids": len(table_b_ids) == len(set(table_b_ids)),
            "table_a_and_b_same_interventions": set(table_a_ids) == set(table_b_ids),
            "population_measure_class_count": len(by_measure),
            "heterogeneous_measure_classes_explicit": len(by_measure) > 1,
            "conservative_distinct_scores": sorted(conservative_scores),
            "conservative_rank_intervals": sorted([list(item) for item in conservative_intervals_found]),
            "zero_conservative_unique_ranks_forbidden": conservative_scores != {"0.000"} or conservative_intervals_found == expected_zero_interval,
            "forward_profile_ids": sorted({str(row["intervention_id"]) for row in table_c}),
            "required_forward_profiles_present": set(forward_ids) == {str(row["intervention_id"]) for row in table_c},
            "forward_rows": len(table_c),
            "forward_completed_D0_rows": len(completed_rows),
            "forward_unknown_or_partial_rows": len(table_c) - len(completed_rows),
            "forward_rows_all_unranked": all(not row["forward_rank_low"] and not row["forward_rank_high"] for row in table_c),
            "completed_rows_have_zero_residual": all(str(row["residual_units"]) == "0" for row in completed_rows),
        },
        "measure_class_counts": dict(sorted(Counter(str(row["population_measure_class"]) for row in table_a).items())),
        "forward_row_counts_by_profile": dict(sorted(Counter(str(row["intervention_id"]) for row in table_c).items())),
        "warnings": [
            "Table A cross-measure screen order is descriptive, not a harmed-person or comfortable-reader rank.",
            "Table B neutral 0.5 factors are ignorance midpoints when labelled unmeasured.",
            "OpenAlex-derived scarcity remains a bibliographic proxy, not an educational-material inventory.",
            "Table C intentionally has no ranks because nonzero residual source-token workloads are not yet measured consistently.",
        ],
    }
    OUTPUTS["validation"].write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({
        "table_a_rows": len(table_a),
        "table_b_rows": len(table_b),
        "table_c_rows": len(table_c),
        "measure_classes": len(by_measure),
        "conservative_intervals": sorted([list(item) for item in conservative_intervals_found]),
        "outputs": {
            key: {"bytes": path.stat().st_size, "sha256": sha256(path)}
            for key, path in OUTPUTS.items()
        },
    }, indent=2))


if __name__ == "__main__":
    main()
