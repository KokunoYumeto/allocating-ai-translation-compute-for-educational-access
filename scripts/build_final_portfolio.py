#!/usr/bin/env python3
"""Build the deduplicated linguistic portfolio and, when ready, Top 10/100.

Shared-core packages replace their exact named-output alternatives only when
the package has complete observed output coverage, a complete base marginal
factor join, and lower modeled compute than independent editions. Constructed
bridge surfaces never receive demographic reach from a family label.

The final exposure order is a deterministic round robin across the informative
base, optimistic, and scarcity views.  The conservative view is retained but
does not allocate positions when every admissible row has the same zero floor.
Accessibility edges remain in their separate non-cardinal backlog until a
residual access gain is measured or bounded.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NATURAL = ROOT / "natural_language_scores_v3.csv"
EXPANSION = ROOT / "candidate_expansion_scores.csv"
PACKAGES = ROOT / "interlanguage_package_scores.csv"
PACKAGE_NAMES = ROOT / "interlanguage_candidates.csv"
SOURCES = ROOT / "population_source_register_master.csv"
RECOVERED_PROFILES = (
    ROOT / "staging" / "resolve_unresolved_profiles" / "profiles.csv"
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if fields is None:
        if not rows:
            raise ValueError(f"No rows for {path}")
        fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def number(value: str | int | float | None) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def integer(value: str | int | float | None) -> int:
    parsed = number(value)
    return round(parsed) if parsed is not None else 0


def split_values(value: str) -> list[str]:
    return [part for part in value.split(";") if part]


def joined(values: list[str]) -> str:
    return ";".join(dict.fromkeys(value for value in values if value))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()


def lane_for_reach(reach_band: str) -> str:
    if reach_band in {"R5_50m_plus", "R4_10m_to_49m"}:
        return "high_reach_underserved"
    if reach_band in {"R3_1m_to_9m", "R2_100k_to_999k"}:
        return "regional_depth"
    return "small_population_prestige_domain_screen"


def apply_recovered_profiles(
    natural_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, dict[str, str]]]:
    """Apply source-audited profile resolutions without changing reach numerators.

    A recovered multi-output bundle retains its one pooled population interval
    exactly once and pays the full modeled output cost for every byte edition.
    The recovery study credits no speculative shared-core savings.
    """
    if not RECOVERED_PROFILES.is_file():
        return natural_rows, {}

    recoveries = {
        row["intervention_id"]: row for row in read_csv(RECOVERED_PROFILES)
    }
    score_ids = {row["intervention_id"] for row in natural_rows}
    missing = sorted(set(recoveries) - score_ids)
    if missing:
        raise ValueError(f"Recovered profile rows lack score rows: {missing}")

    token_fields = (
        "fr2_gross_tokens_low",
        "fr2_gross_tokens_base",
        "fr2_gross_tokens_high",
        "openstax_next_gross_tokens_low",
        "openstax_next_gross_tokens_base",
        "openstax_next_gross_tokens_high",
    )
    applied: dict[str, dict[str, str]] = {}
    for row in natural_rows:
        recovery = recoveries.get(row["intervention_id"])
        row["_profile_authority_source_ids"] = ""
        row["_profile_population_attribution"] = ""
        row["_output_count"] = "1"
        if recovery is None or recovery["rankability_class"] != "cardinal_ceiling_rankable":
            continue
        if recovery["population_observation_id"] != row["observation_id"]:
            raise ValueError(
                f"Profile recovery observation mismatch for {row['intervention_id']}"
            )
        for field in ("population_low", "population_base", "population_high"):
            if integer(recovery[field]) != integer(row[field]):
                raise ValueError(
                    f"Profile recovery {field} mismatch for {row['intervention_id']}"
                )

        output_count = integer(recovery["output_count"])
        if output_count < 1:
            raise ValueError(f"Invalid output count for {row['intervention_id']}")
        for field in token_fields:
            if row.get(field, ""):
                row[field] = str(integer(row[field]) * output_count)
        if row.get("fr2_api_equivalent_usd_base", ""):
            row["fr2_api_equivalent_usd_base"] = (
                f"{float(row['fr2_api_equivalent_usd_base']) * output_count:.2f}"
            )

        row["target_profile_ready"] = "true"
        row["profile_tag_status"] = "source_audited_profile_resolution"
        row["profile_resolution_status"] = (
            "resolved_exact_multi_output_bundle"
            if output_count > 1
            else "resolved_exact_single_edition"
        )
        row["profile_ranking_treatment"] = (
            f"{recovery['decision']}; pooled population counted once; "
            f"{output_count} full output cost(s); no shared-core savings credited"
        )
        row["resolved_edition_name"] = recovery["production_unit"]
        row["target_profile"] = recovery["output_profiles"]
        row["_profile_authority_source_ids"] = recovery["source_ids"]
        row["_profile_population_attribution"] = recovery["population_attribution"]
        row["_output_count"] = str(output_count)
        row["interpretation"] = (
            f"{row['interpretation']} Profile recovery: "
            f"{recovery['population_attribution']} "
            f"Caveat: {recovery['blocker_or_uncertainty']}"
        )
        applied[row["intervention_id"]] = recovery
    return natural_rows, applied


def competition_ranks(rows: list[dict[str, object]], field: str) -> dict[str, int]:
    ordered = sorted(
        rows,
        key=lambda row: (
            float(row[field]) if row[field] not in (None, "") else -1.0,
            float(row["population_base"]),
            str(row["intervention_id"]),
        ),
        reverse=True,
    )
    ranks: dict[str, int] = {}
    prior: float | None = None
    prior_rank = 0
    for position, row in enumerate(ordered, 1):
        value = float(row[field]) if row[field] not in (None, "") else -1.0
        if prior is None or value != prior:
            prior_rank = position
            prior = value
        ranks[str(row["intervention_id"])] = prior_rank
    return ranks


def competition_rank_intervals(
    rows: list[dict[str, object]], field: str
) -> dict[str, tuple[int, int]]:
    """Return tie-aware [low, high] rank intervals for a numeric field."""
    ordered = sorted(
        rows,
        key=lambda row: (
            float(row[field]) if row[field] not in (None, "") else -1.0,
            str(row["intervention_id"]),
        ),
        reverse=True,
    )
    intervals: dict[str, tuple[int, int]] = {}
    start = 0
    while start < len(ordered):
        value = (
            float(ordered[start][field])
            if ordered[start][field] not in (None, "")
            else -1.0
        )
        end = start
        while end + 1 < len(ordered):
            next_value = (
                float(ordered[end + 1][field])
                if ordered[end + 1][field] not in (None, "")
                else -1.0
            )
            if next_value != value:
                break
            end += 1
        for index in range(start, end + 1):
            intervals[str(ordered[index]["intervention_id"])] = (start + 1, end + 1)
        start = end + 1
    return intervals


def main() -> None:
    natural_rows = read_csv(NATURAL)
    if EXPANSION.is_file():
        expansion_rows = read_csv(EXPANSION)
        expected_fields = set(natural_rows[0])
        for row in expansion_rows:
            missing = expected_fields - set(row)
            if missing:
                raise ValueError(
                    f"Expansion row {row.get('intervention_id')} lacks fields: {sorted(missing)}"
                )
        natural_rows.extend(expansion_rows)
    natural_rows, recovered_profiles = apply_recovered_profiles(natural_rows)
    package_rows = read_csv(PACKAGES)
    package_names = {
        row["interlanguage_id"]: row for row in read_csv(PACKAGE_NAMES)
    }
    source_rows = {row["source_id"]: row for row in read_csv(SOURCES)}

    eligible_natural = [
        row for row in natural_rows
        if row["recommendation_eligibility"] == "provisional_eligible"
        and not row.get("profile_resolution_status", "").startswith("requires_")
    ]
    natural_by_observation = {
        row["observation_id"]: row for row in eligible_natural
    }

    package_by_key = {
        (row["intervention_id"], row["token_scenario"], row["reuse_assumption_scenario"]): row
        for row in package_rows
    }
    base_packages = [
        row for row in package_rows
        if row["token_scenario"] == "base"
        and row["reuse_assumption_scenario"] == "reuse_base"
    ]

    replacement_decisions: list[dict[str, object]] = []
    selected_packages: list[dict[str, str]] = []
    consumed_observations: set[str] = set()
    for row in sorted(base_packages, key=lambda item: item["intervention_id"]):
        expected = integer(row["expected_new_named_outputs"])
        populated = integer(row["named_outputs_with_exact_population"])
        base_access = number(row["base_marginal_access_sensitivity_sum"])
        package_cost = integer(row["total_modeled_gross_tokens"])
        independent_cost = integer(row["named_outputs_no_reuse_gross_tokens"])
        complete = expected >= 2 and expected == populated
        proxy_count = integer(row.get("marginal_score_territory_proxy_derived_output_count"))
        marginal_complete = (
            base_access is not None
            and integer(row["marginal_score_joined_output_count"]) == populated
            and proxy_count == 0
        )
        upstream_population_union_admissible = (
            row.get("rankable_as_observed_population_gross_sum", "").lower() == "true"
            and row.get("all_selected_links_usable_as_package_population_total", "").lower() == "true"
            and row.get("all_planned_matrix_rows_rankable_under_current_evidence", "").lower() == "true"
        )
        cheaper = independent_cost > 0 and package_cost < independent_cost
        positive_reach = integer(row["exact_named_output_population_base"]) > 0
        observations = split_values(row["included_population_observation_ids"])
        members = [natural_by_observation[item] for item in observations if item in natural_by_observation]
        constituent_complete = len(observations) == populated and len(members) == populated
        access_reconciled = constituent_complete and all(
            abs(
                sum(integer(member[field]) for member in members)
                - integer(row[package_field])
            ) <= max(2, len(members))
            for field, package_field in (
                ("marginal_access_low", "marginal_access_low_sum"),
                ("marginal_access_base_sensitivity", "base_marginal_access_sensitivity_sum"),
                ("marginal_access_high", "marginal_access_high_sum"),
            )
        )
        select = (
            complete
            and marginal_complete
            and constituent_complete
            and access_reconciled
            and cheaper
            and positive_reach
            and upstream_population_union_admissible
        )
        if set(observations) & consumed_observations:
            select = False
            reason = "exclude_overlapping_selected_package"
        elif select:
            reason = "select_pareto_dominant_complete_named_output_package"
            selected_packages.append(row)
            consumed_observations.update(observations)
        elif not complete:
            reason = "exclude_incomplete_observed_population_coverage"
        elif not upstream_population_union_admissible:
            reason = "exclude_upstream_population_union_not_admissible"
        elif proxy_count:
            reason = "exclude_territory_proxy_marginal_join_not_constituent_reconciled"
        elif not constituent_complete:
            reason = "exclude_missing_constituent_natural_score_rows"
        elif not access_reconciled:
            reason = "exclude_package_access_interval_does_not_reconcile"
        elif not marginal_complete:
            reason = "exclude_incomplete_constituent_marginal_join"
        elif not cheaper:
            reason = "exclude_no_modeled_compute_dominance"
        else:
            reason = "exclude_zero_observed_reach"
        replacement_decisions.append({
            "intervention_id": row["intervention_id"],
            "mechanism_class": row["mechanism_class"],
            "expected_new_named_outputs": expected,
            "named_outputs_with_exact_population": populated,
            "base_marginal_joined_outputs": row["marginal_score_joined_output_count"],
            "territory_proxy_derived_outputs": proxy_count,
            "constituent_natural_rows_found": len(members),
            "access_interval_reconciled": str(access_reconciled).lower(),
            "upstream_population_union_admissible": str(
                upstream_population_union_admissible
            ).lower(),
            "observed_population_base": row["exact_named_output_population_base"],
            "base_marginal_access_sensitivity": row["base_marginal_access_sensitivity_sum"],
            "independent_named_output_tokens_base": independent_cost,
            "shared_core_tokens_base": package_cost,
            "modeled_token_savings": independent_cost - package_cost,
            "selected_for_deduplicated_portfolio": str(select).lower(),
            "decision_reason": reason,
            "constituent_observation_ids": row["included_population_observation_ids"],
            "caveat": "Reuse is an unobserved sensitivity; selection is architecture dominance within that scenario, not empirical production savings.",
        })

    linguistic: list[dict[str, object]] = []
    for row in eligible_natural:
        if row["observation_id"] in consumed_observations:
            continue
        source = source_rows.get(row["population_source_id"], {})
        scarcity_access = number(row["scarcity_adjusted_access_base"])
        tokens_low = integer(row["fr2_gross_tokens_low"])
        tokens_base = integer(row["fr2_gross_tokens_base"])
        tokens_high = integer(row["fr2_gross_tokens_high"])
        access_low = integer(row["marginal_access_low"])
        access_base = integer(row["marginal_access_base_sensitivity"])
        access_high = integer(row["marginal_access_high"])
        population_base = integer(row["population_base"])
        linguistic.append({
            "intervention_id": row["intervention_id"],
            "intervention_type": "natural_language_edition",
            "intervention_name": row["resolved_edition_name"] or row["target_name"],
            "target_profiles": row["target_profile"],
            "output_count": row.get("_output_count", "1"),
            "territory_or_scope": row["territory"],
            "portfolio_lane": lane_for_reach(row["reach_band"]),
            "lane_basis": f"{row['reach_band']}; vitality is not inferred from population band",
            "population_low": row["population_low"],
            "population_base": row["population_base"],
            "population_high": row["population_high"],
            "source_population_low_reported": row["source_population_low_reported"],
            "source_population_high_reported": row["source_population_high_reported"],
            "population_interval_status": row["population_interval_status"],
            "population_measure": row["population_measure"],
            "population_years": row["population_reference_year"],
            "population_observation_ids": row["observation_id"],
            "population_source_ids": row["population_source_id"],
            "profile_authority_source_ids": row.get("_profile_authority_source_ids", ""),
            "profile_population_attribution": row.get("_profile_population_attribution", ""),
            "source_confidence": source.get("confidence", ""),
            "source_tier": source.get("source_tier", ""),
            "marginal_access_low": access_low,
            "marginal_access_base_sensitivity": access_base,
            "marginal_access_high": access_high,
            "access_factor_status": f"{row['practical_access_status']};{row['academic_nonoverlap_status']}",
            "gross_tokens_low": tokens_low,
            "gross_tokens_base": tokens_base,
            "gross_tokens_high": tokens_high,
            "api_equivalent_usd_base": row["fr2_api_equivalent_usd_base"],
            "gross_people_per_million_base_tokens": f"{population_base * 1_000_000 / tokens_base:.3f}",
            "base_marginal_access_per_million_tokens": f"{access_base * 1_000_000 / tokens_base:.3f}",
            "conservative_access_per_million_tokens": f"{access_low * 1_000_000 / tokens_high:.3f}",
            "optimistic_access_per_million_tokens": f"{access_high * 1_000_000 / tokens_low:.3f}",
            "scarcity_adjusted_access_per_million_tokens": "" if scarcity_access is None else f"{scarcity_access * 1_000_000 / tokens_base:.3f}",
            "recommended_first_product": "FR-2 Formal Reasoning Core",
            "recommended_openstax_next_product": row["recommended_openstax_next_product"],
            "recommended_openstax_depth": row["recommended_openstax_depth"],
            "openstax_next_gross_tokens_low": row["openstax_next_gross_tokens_low"],
            "openstax_next_gross_tokens_base": row["openstax_next_gross_tokens_base"],
            "openstax_next_gross_tokens_high": row["openstax_next_gross_tokens_high"],
            "profile_resolution_status": row["profile_resolution_status"],
            "profile_ranking_treatment": row["profile_ranking_treatment"],
            "deduplication_rule": "one exact population observation; excluded if consumed by a selected shared-core package",
            "evidence_caveat": row["interpretation"],
        })

    natural_by_territory: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in eligible_natural:
        natural_by_territory[row["territory"]].append(row)

    for base_row in selected_packages:
        intervention_id = base_row["intervention_id"]
        optimistic = package_by_key[(intervention_id, "low", "reuse_optimistic")]
        conservative = package_by_key[(intervention_id, "high", "reuse_conservative")]
        observations = split_values(base_row["included_population_observation_ids"])
        members = [natural_by_observation[item] for item in observations if item in natural_by_observation]
        source_ids = split_values(base_row["included_population_source_ids"])
        confidences = [source_rows[item]["confidence"] for item in source_ids if item in source_rows]
        tiers = [source_rows[item]["source_tier"] for item in source_ids if item in source_rows]
        names = package_names.get(intervention_id, {})
        products = joined([row["recommended_openstax_next_product"] for row in members])
        depths = joined([row["recommended_openstax_depth"] for row in members])
        if not products:
            # Complete packages with territory-proxy-only members receive the
            # conservative algebra/trigonometry bridge used by the natural model.
            products = "MV-1"
            depths = "D3"
        pop_base = integer(base_row["exact_named_output_population_base"])
        access_low = integer(base_row["marginal_access_low_sum"])
        access_base = integer(base_row["base_marginal_access_sensitivity_sum"])
        access_high = integer(base_row["marginal_access_high_sum"])
        tokens_low = integer(optimistic["total_modeled_gross_tokens"])
        tokens_base = integer(base_row["total_modeled_gross_tokens"])
        tokens_high = integer(conservative["total_modeled_gross_tokens"])
        linguistic.append({
            "intervention_id": intervention_id,
            "intervention_type": "shared_core_named_output_package",
            "intervention_name": names.get("name", intervention_id),
            "target_profiles": base_row["included_target_profiles"],
            "output_count": base_row["expected_new_named_outputs"],
            "territory_or_scope": joined([row["territory"] for row in members]) or names.get("proposed_surfaces", ""),
            "portfolio_lane": "shared_core_interlanguage_architecture",
            "lane_basis": f"{base_row['mechanism_class']}; complete exact named-output coverage; no family-level comprehension credit",
            "population_low": base_row["exact_named_output_population_low"],
            "population_base": pop_base,
            "population_high": base_row["exact_named_output_population_high"],
            "source_population_low_reported": base_row["exact_named_output_population_low"],
            "source_population_high_reported": base_row["exact_named_output_population_high"],
            "population_interval_status": "sum_of_disjoint_or_separately_territorial_named_output_cells",
            "population_measure": "package_sum_of_exact_named_output_observations",
            "population_years": base_row["population_years"],
            "population_observation_ids": base_row["included_population_observation_ids"],
            "population_source_ids": base_row["included_population_source_ids"],
            "profile_authority_source_ids": "",
            "profile_population_attribution": "Each named output has a separate exact population observation; no constructed-surface family reach is credited.",
            "source_confidence": joined(confidences),
            "source_tier": joined(tiers),
            "marginal_access_low": access_low,
            "marginal_access_base_sensitivity": access_base,
            "marginal_access_high": access_high,
            "access_factor_status": f"member natural-score joins plus {base_row['marginal_score_territory_proxy_derived_output_count']} disclosed territory-proxy derivations",
            "gross_tokens_low": tokens_low,
            "gross_tokens_base": tokens_base,
            "gross_tokens_high": tokens_high,
            "api_equivalent_usd_base": "",
            "gross_people_per_million_base_tokens": f"{pop_base * 1_000_000 / tokens_base:.3f}",
            "base_marginal_access_per_million_tokens": f"{access_base * 1_000_000 / tokens_base:.3f}",
            "conservative_access_per_million_tokens": f"{access_low * 1_000_000 / tokens_high:.3f}",
            "optimistic_access_per_million_tokens": f"{access_high * 1_000_000 / tokens_low:.3f}",
            "scarcity_adjusted_access_per_million_tokens": "",
            "recommended_first_product": "FR-2 Formal Reasoning Core across separately named outputs",
            "recommended_openstax_next_product": products,
            "recommended_openstax_depth": depths,
            "openstax_next_gross_tokens_low": "",
            "openstax_next_gross_tokens_base": "",
            "openstax_next_gross_tokens_high": "",
            "profile_resolution_status": "complete_named_output_package",
            "profile_ranking_treatment": "shared semantic/formula core; every surface remains a separately named localized edition",
            "deduplication_rule": f"replaces constituent natural rows {base_row['included_population_observation_ids']}",
            "evidence_caveat": base_row["interpretation"],
        })

    rank_fields = {
        "base": "base_marginal_access_per_million_tokens",
        "gross": "gross_people_per_million_base_tokens",
        "conservative": "conservative_access_per_million_tokens",
        "optimistic": "optimistic_access_per_million_tokens",
        "scarcity": "scarcity_adjusted_access_per_million_tokens",
    }
    rank_maps = {
        name: competition_rank_intervals(linguistic, field)
        for name, field in rank_fields.items()
    }
    for row in linguistic:
        informative: list[tuple[int, int]] = []
        for rank_name, rank_map in rank_maps.items():
            low, high = rank_map[str(row["intervention_id"])]
            row[f"{rank_name}_efficiency_rank_low"] = low
            row[f"{rank_name}_efficiency_rank_high"] = high
            if (
                rank_name in {"base", "optimistic", "scarcity"}
                and row[rank_fields[rank_name]] not in (None, "")
            ):
                informative.append((low, high))
        row["informative_rank_best"] = min(item[0] for item in informative)
        row["informative_rank_worst"] = max(item[1] for item in informative)
        row["informative_rank_views_available"] = len(informative)
        row["conservative_view_treatment"] = (
            "reported_tie_interval_but_not_used_for_admission_when_globally_degenerate"
        )

    def consensus_midpoint(row: dict[str, object]) -> float:
        values: list[float] = []
        for name in ("base", "optimistic", "scarcity"):
            if row[rank_fields[name]] in (None, ""):
                continue
            values.append(
                (
                    float(row[f"{name}_efficiency_rank_low"])
                    + float(row[f"{name}_efficiency_rank_high"])
                ) / 2.0
            )
        return sum(values) if values else float("inf")

    lane_specs = [
        ("base", rank_fields["base"]),
        ("optimistic", rank_fields["optimistic"]),
        ("scarcity", rank_fields["scarcity"]),
    ]
    lane_orders: dict[str, list[dict[str, object]]] = {}
    for lane, field in lane_specs:
        lane_orders[lane] = sorted(
            [row for row in linguistic if row[field] not in (None, "")],
            key=lambda row: (
                -float(row[field]),
                consensus_midpoint(row),
                str(row["intervention_id"]),
            ),
        )

    exposure_order: list[dict[str, object]] = []
    admitted: set[str] = set()
    while len(admitted) < len(linguistic):
        progressed = False
        for lane, _field in lane_specs:
            candidate = next(
                (
                    row
                    for row in lane_orders[lane]
                    if str(row["intervention_id"]) not in admitted
                ),
                None,
            )
            if candidate is None:
                continue
            intervention_id = str(candidate["intervention_id"])
            admitted.add(intervention_id)
            low = candidate[f"{lane}_efficiency_rank_low"]
            high = candidate[f"{lane}_efficiency_rank_high"]
            candidate["admission_lane"] = lane
            candidate["admission_lane_rank_low"] = low
            candidate["admission_lane_rank_high"] = high
            candidate["portfolio_position"] = len(exposure_order) + 1
            exposure_order.append(candidate)
            progressed = True
        if not progressed:
            raise RuntimeError("No informative lane can admit the remaining candidates")

    conservative_values = {
        str(row[rank_fields["conservative"]]) for row in linguistic
    }
    conservative_degenerate = len(conservative_values) == 1

    write_csv(ROOT / "package_replacement_decisions.csv", replacement_decisions)
    write_csv(ROOT / "portfolio_linguistic_candidates.csv", exposure_order)

    controls = [
        {
            "intervention_id": row["intervention_id"],
            "target_name": row["target_name"],
            "target_profile": row["target_profile"],
            "territory": row["territory"],
            "population_base": row["population_base"],
            "control_or_exclusion": (
                "richly_served_negative_control"
                if row["explicit_negative_control"] == "true"
                else (
                    "unresolved_localized_output_profile"
                    if row.get("profile_resolution_status", "").startswith("requires_")
                    else "not_recommendation_eligible"
                )
            ),
            "basis": row["profile_ranking_treatment"] or row["recommendation_eligibility"],
            "population_observation_id": row["observation_id"],
            "population_source_id": row["population_source_id"],
        }
        for row in natural_rows
        if row["recommendation_eligibility"] != "provisional_eligible"
        or row.get("profile_resolution_status", "").startswith("requires_")
    ]
    write_csv(ROOT / "negative_controls_and_profile_exclusions.csv", controls)

    cardinal_unfilled = max(0, 100 - len(exposure_order))
    status = {
        "natural_score_rows_considered": len(natural_rows),
        "eligible_natural_before_package_replacement": len(eligible_natural),
        "selected_pareto_dominant_packages": len(selected_packages),
        "source_audited_profile_recoveries_applied": len(recovered_profiles),
        "consumed_natural_observations": len(consumed_observations & set(natural_by_observation)),
        "deduplicated_cardinal_linguistic_rows": len(exposure_order),
        "top_100_cardinal_positions_filled": min(100, len(exposure_order)),
        "top_100_cardinal_positions_unfilled": cardinal_unfilled,
        "top_100_ready": len(exposure_order) >= 100,
        "conservative_view_degenerate": conservative_degenerate,
        "admission_lane_cycle": [lane for lane, _field in lane_specs],
        "accessibility_treatment": "separate_non_cardinal_safeguard_backlog",
    }
    if status["top_100_ready"]:
        write_csv(ROOT / "TOP_100.csv", exposure_order[:100])
        write_csv(ROOT / "TOP_10.csv", exposure_order[:10])
    else:
        for stale in (ROOT / "TOP_100.csv", ROOT / "TOP_10.csv"):
            if stale.is_file():
                stale.unlink()

    status_path = ROOT / "PORTFOLIO_BUILD_STATUS.json"
    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(status, indent=2))
    print({
        "linguistic_sha256": sha256(ROOT / "portfolio_linguistic_candidates.csv"),
        "replacement_sha256": sha256(ROOT / "package_replacement_decisions.csv"),
        "status_sha256": sha256(status_path),
    })


if __name__ == "__main__":
    main()
