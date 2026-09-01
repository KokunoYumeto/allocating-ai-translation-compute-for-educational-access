from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT


def read_csv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(name: str, fields: list[str], rows: list[dict[str, object]]) -> Path:
    path = OUT / name
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return path


def integer(value: str) -> int:
    return int(Decimal(value or "0"))


def number(value: str) -> Decimal:
    return Decimal(value or "0")


def total(rows: list[dict[str, str]], field: str) -> int:
    return sum(integer(row[field]) for row in rows if row.get(field, "") != "")


def fmt(value: object) -> str:
    if value is None or value == "":
        return "—"
    try:
        return f"{integer(str(value)):,}"
    except Exception:
        return str(value)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


OUT.mkdir(parents=True, exist_ok=True)

portfolio = read_csv("portfolio_linguistic_candidates.csv")
top10 = read_csv("TOP_10.csv")
top100 = read_csv("TOP_100.csv")
needs_register = read_csv("population_mathematics_needs_register.csv")
needs_by_intervention = {
    row["intervention_id"]: row
    for row in needs_register
    if row["intervention_id"].startswith("NAT-")
}
package_decisions = read_csv("package_replacement_decisions.csv")
package_scores = read_csv("interlanguage_package_scores.csv")
negative_controls = read_csv("negative_controls_and_profile_exclusions.csv")
scale = read_csv("portfolio_scale_planning.csv")
population_master = read_csv("population_observations_master.csv")
population_by_id = {row["observation_id"]: row for row in population_master}
portfolio_count = len(portfolio)

assert portfolio_count >= 100
assert len(top10) == 10
assert len(top100) == 100
assert len({row["intervention_id"] for row in portfolio}) == portfolio_count
assert len({row["intervention_id"] for row in top100}) == 100
assert sorted(integer(row["portfolio_position"]) for row in portfolio) == list(range(1, portfolio_count + 1))
assert sorted(integer(row["portfolio_position"]) for row in top100) == list(range(1, 101))
assert {row["intervention_type"] for row in portfolio} == {"natural_language_edition"}
assert {row["intervention_type"] for row in top100} == {"natural_language_edition"}
assert all(row["output_count"] == "1" for row in top100)
assert [row["intervention_id"] for row in top10] == [
    row["intervention_id"] for row in sorted(top100, key=lambda row: integer(row["portfolio_position"]))[:10]
]
assert all(number(row["marginal_access_low"]) == 0 for row in portfolio)
assert sum(row["selected_for_deduplicated_portfolio"] == "true" for row in package_decisions) == 0

SHORT_NEEDS_PACKAGES = {
    "NAT-122": "Finish the exact Calculus I residual, produce accessible Open Logic derivatives, then audit the remaining fixed-STEM and advanced gaps",
    "NAT-121": "Close the next verified gap in the existing 40-course program; do not duplicate complete Open Logic, Prealgebra, or Elementary Algebra",
    "NAT-001": "Bangla Grade 2-5 foundational numeracy kit",
    "NAT-003": "Telugu-English Grades 3-10 mastery bridge",
    "NAT-002": "Indian Bangla Grades 3-8 arithmetic-to-algebra catch-up",
    "NAT-028": "Precalculus-to-calculus-to-linear-algebra self-study spine",
    "NAT-006": "Marathi Grade 8-to-first-year-STEM bridge",
    "NAT-004": "Tamil Grades 2-8 teacher-independent numeracy recovery",
    "NAT-015": "Shahmukhi Punjabi-to-Urdu/English secondary-to-UG bridge",
    "NAT-038": "Bilingual Javanese-to-Bahasa foundational/academic-register scaffold",
    "NAT-007": "Gujarati Grades 2-6 diagnostic numeracy remediation",
}


def needs_assignment(row: dict[str, str]) -> dict[str, str]:
    exact = needs_by_intervention.get(row["intervention_id"])
    if exact:
        assignment_status = (
            "directly_audited_stage_specific_residual"
            if row["intervention_id"] == "NAT-122"
            else "audited_primary_or_official_proxy"
        )
        return {
            "needs_evidence_stage": exact["evidence_stage"],
            "needs_first_package": exact["first_useful_open_package"],
            "needs_first_package_short": SHORT_NEEDS_PACKAGES[row["intervention_id"]],
            "needs_assignment_status": assignment_status,
            "needs_observed_evidence": exact["observed_need"],
            "needs_source": exact["evidence_source"],
            "needs_caveat": exact["caveat"],
        }

    product = row["recommended_openstax_next_product"]
    depth = row["recommended_openstax_depth"]
    if product == "MV-1" and depth == "D2":
        stage = "foundational_or_secondary_readiness_unresolved"
        package = "Diagnose foundational readiness first; commission a numeracy-to-algebra recovery path only if the local corpus audit confirms the gap."
        short = "Foundational-readiness audit before algebra assignment"
    elif product == "MV-1":
        stage = "secondary_bridge_candidate"
        package = "Audit local secondary supply, then commission a complete algebra/functions/trigonometry bridge only where it is the binding gap."
        short = "Secondary bridge candidate; local needs audit required"
    else:
        stage = "secondary_data_or_undergraduate_candidate"
        package = "Audit local algebra/statistics and tertiary supply before choosing a secondary-data or undergraduate bridge."
        short = "Secondary-data/UG candidate; local needs audit required"
    return {
        "needs_evidence_stage": stage,
        "needs_first_package": package,
        "needs_first_package_short": short,
        "needs_assignment_status": "territory_proxy_only_not_a_content_commission",
        "needs_observed_evidence": "",
        "needs_source": "",
        "needs_caveat": "The fixed OpenStax scenario classifies compute scale only; it does not establish that this content is locally missing.",
    }

# Table 2: all canonical natural-language interventions, sorted only for display by the
# source-bounded base population ceiling. This is deliberately not called a
# welfare ranking because measures and source universes differ.
table2_fields = [
    "gross_ceiling_display_order",
    "portfolio_position",
    "intervention_id",
    "intervention_type",
    "intervention_name",
    "target_profiles",
    "output_count",
    "territory_or_scope",
    "portfolio_lane",
    "population_low",
    "population_base",
    "population_high",
    "source_population_low_reported",
    "source_population_high_reported",
    "population_interval_status",
    "population_measure",
    "population_years",
    "population_observation_ids",
    "population_source_ids",
    "profile_authority_source_ids",
    "profile_population_attribution",
    "source_confidence",
    "source_tier",
    "deduplication_rule",
    "evidence_caveat",
]
table2_rows: list[dict[str, object]] = []
for display_order, row in enumerate(
    sorted(
        portfolio,
        key=lambda item: (-number(item["population_base"]), item["intervention_id"]),
    ),
    start=1,
):
    output: dict[str, object] = {field: row.get(field, "") for field in table2_fields}
    output["gross_ceiling_display_order"] = display_order
    table2_rows.append(output)

table2_path = write_csv("table2_exact_gross_ceilings.csv", table2_fields, table2_rows)

# Table 3: the three access-factor sensitivities and all tie-aware ranking views.
table3_fields = [
    "portfolio_position",
    "intervention_id",
    "intervention_name",
    "target_profiles",
    "territory_or_scope",
    "population_low",
    "population_base",
    "population_high",
    "marginal_access_low",
    "marginal_access_base_sensitivity",
    "marginal_access_high",
    "marginal_access_high_optimistic_sensitivity",
    "access_factor_status",
    "gross_tokens_low",
    "gross_tokens_base",
    "gross_tokens_high",
    "base_marginal_access_per_million_tokens",
    "conservative_access_per_million_tokens",
    "optimistic_access_per_million_tokens",
    "scarcity_adjusted_access_per_million_tokens",
    "scarcity_adjusted_access_per_million_tokens_sensitivity",
    "base_efficiency_rank_low",
    "base_efficiency_rank_high",
    "conservative_efficiency_rank_low",
    "conservative_efficiency_rank_high",
    "optimistic_efficiency_rank_low",
    "optimistic_efficiency_rank_high",
    "scarcity_efficiency_rank_low",
    "scarcity_efficiency_rank_high",
    "informative_rank_best",
    "informative_rank_worst",
    "informative_rank_views_available",
    "conservative_view_treatment",
    "admission_lane",
    "admission_lane_rank_low",
    "admission_lane_rank_high",
    "population_observation_ids",
    "population_source_ids",
    "sensitivity_label_note",
    "evidence_caveat",
]
table3_rows = [
    {field: row.get(field, "") for field in table3_fields}
    for row in sorted(portfolio, key=lambda item: integer(item["portfolio_position"]))
]
for output, source in zip(
    table3_rows, sorted(portfolio, key=lambda item: integer(item["portfolio_position"]))
):
    output["marginal_access_high_optimistic_sensitivity"] = source["marginal_access_high"]
    output["scarcity_adjusted_access_per_million_tokens_sensitivity"] = source[
        "scarcity_adjusted_access_per_million_tokens"
    ]
    output["sensitivity_label_note"] = (
        "base=neutral factor sensitivity; optimistic=high-bound factor sensitivity; "
        "scarcity=base sensitivity weighted by the disclosed scarcity proxy; none is an observed harmed-population count"
    )
table3_path = write_csv(
    "table3_marginal_access_sensitivity_ranges.csv", table3_fields, table3_rows
)

# Table 4: the published Top 10 selection with enough evidence and uncertainty
# fields to reproduce each displayed number.
table4_fields = [
    "portfolio_position",
    "intervention_id",
    "intervention_type",
    "intervention_name",
    "target_profiles",
    "output_count",
    "territory_or_scope",
    "portfolio_lane",
    "admission_lane",
    "population_low",
    "population_base",
    "population_high",
    "population_measure",
    "population_years",
    "population_observation_ids",
    "population_source_ids",
    "marginal_access_low",
    "marginal_access_base_sensitivity",
    "marginal_access_high",
    "marginal_access_high_optimistic_sensitivity",
    "access_factor_status",
    "gross_tokens_low",
    "gross_tokens_base",
    "gross_tokens_high",
    "base_marginal_access_per_million_tokens",
    "optimistic_access_per_million_tokens",
    "scarcity_adjusted_access_per_million_tokens",
    "scarcity_adjusted_access_per_million_tokens_sensitivity",
    "informative_rank_best",
    "informative_rank_worst",
    "recommended_first_product",
    "recommended_openstax_next_product",
    "recommended_openstax_depth",
    "openstax_next_gross_tokens_low",
    "openstax_next_gross_tokens_base",
    "openstax_next_gross_tokens_high",
    "deduplication_rule",
    "sensitivity_label_note",
    "evidence_caveat",
]
table4_rows = [
    {field: row.get(field, "") for field in table4_fields}
    for row in sorted(top10, key=lambda item: integer(item["portfolio_position"]))
]
for output, source in zip(
    table4_rows, sorted(top10, key=lambda item: integer(item["portfolio_position"]))
):
    output["marginal_access_high_optimistic_sensitivity"] = source["marginal_access_high"]
    output["scarcity_adjusted_access_per_million_tokens_sensitivity"] = source[
        "scarcity_adjusted_access_per_million_tokens"
    ]
    output["sensitivity_label_note"] = (
        "base, optimistic, and scarcity values are model sensitivities; none is an observed harmed-population count"
    )
table4_path = write_csv("table4_top10.csv", table4_fields, table4_rows)

# Table 5: compact three-lane summary plus an exact 100-row membership supplement.
lane_order = [
    "high_reach_underserved",
    "regional_depth",
    "small_population_prestige_domain_screen",
]
table5_fields = [
    "portfolio_lane",
    "intervention_count",
    "localized_output_count",
    "base_admission_count",
    "optimistic_admission_count",
    "scarcity_admission_count",
    "portfolio_positions",
    "member_intervention_ids",
    "member_names",
    "fr2_gross_tokens_low_sum",
    "fr2_gross_tokens_base_sum",
    "fr2_gross_tokens_high_sum",
    "accessibility_treatment",
    "admission_views_treatment",
    "aggregation_caveat",
]
table5_rows: list[dict[str, object]] = []
for lane in lane_order:
    members = sorted(
        [row for row in top100 if row["portfolio_lane"] == lane],
        key=lambda row: integer(row["portfolio_position"]),
    )
    admissions = Counter(row["admission_lane"] for row in members)
    table5_rows.append(
        {
            "portfolio_lane": lane,
            "intervention_count": len(members),
            "localized_output_count": total(members, "output_count"),
            "base_admission_count": admissions["base"],
            "optimistic_admission_count": admissions["optimistic"],
            "scarcity_admission_count": admissions["scarcity"],
            "portfolio_positions": ";".join(row["portfolio_position"] for row in members),
            "member_intervention_ids": ";".join(row["intervention_id"] for row in members),
            "member_names": ";".join(row["intervention_name"] for row in members),
            "fr2_gross_tokens_low_sum": total(members, "gross_tokens_low"),
            "fr2_gross_tokens_base_sum": total(members, "gross_tokens_base"),
            "fr2_gross_tokens_high_sum": total(members, "gross_tokens_high"),
            "accessibility_treatment": "separate_non_cardinal_safeguard_backlog_not_a_numbered_language_slot",
            "admission_views_treatment": "base_optimistic_and_scarcity_are_sensitivity_views_not_observed_welfare_values",
            "aggregation_caveat": (
                "Counts and compute may be summed. Population and marginal-access columns are not summed here "
                "because source universes, years, and measures differ; a raw sum is not a unique-person count."
            ),
        }
    )

table5_path = write_csv("table5_top100_grouped_lanes.csv", table5_fields, table5_rows)
assert sum(integer(str(row["intervention_count"])) for row in table5_rows) == 100
assert sum(integer(str(row["localized_output_count"])) for row in table5_rows) == 100
for token_field in ["gross_tokens_low", "gross_tokens_base", "gross_tokens_high"]:
    summary_field = f"fr2_{token_field}_sum"
    assert sum(integer(str(row[summary_field])) for row in table5_rows) == total(top100, token_field)

table5_member_fields = [
    "portfolio_position",
    "portfolio_lane",
    "admission_lane",
    "intervention_id",
    "intervention_type",
    "intervention_name",
    "target_profiles",
    "output_count",
    "territory_or_scope",
    "population_base",
    "population_measure",
    "population_years",
    "population_observation_ids",
    "population_source_ids",
    "marginal_access_base_sensitivity",
    "gross_tokens_base",
    "informative_rank_best",
    "informative_rank_worst",
    "recommended_openstax_next_product",
    "recommended_openstax_depth",
    "needs_evidence_stage",
    "needs_first_package",
    "needs_first_package_short",
    "needs_assignment_status",
    "needs_observed_evidence",
    "needs_source",
    "needs_caveat",
]
table5_member_rows = []
for row in sorted(
    top100,
    key=lambda row: (
        lane_order.index(row["portfolio_lane"]),
        integer(row["portfolio_position"]),
    ),
):
    enriched = dict(row)
    enriched.update(needs_assignment(row))
    table5_member_rows.append(
        {field: enriched.get(field, "") for field in table5_member_fields}
    )
table5_members_path = write_csv(
    "table5_top100_members.csv", table5_member_fields, table5_member_rows
)
top100_needs_path = write_csv(
    "top100_needs_assignment.csv",
    [
        "portfolio_position",
        "intervention_id",
        "intervention_name",
        "target_profiles",
        "territory_or_scope",
        "needs_evidence_stage",
        "needs_first_package",
        "needs_assignment_status",
        "needs_observed_evidence",
        "needs_source",
        "needs_caveat",
    ],
    sorted(table5_member_rows, key=lambda row: integer(row["portfolio_position"])),
)

# Table 6: package architectures are never cardinal substitutions in the
# fail-closed head. Four fully joined architectures remain as a separate,
# nonadditive diagnostic sensitivity panel; all other proposals remain in an
# exclusion panel. The base reuse fraction is unobserved for every row.
base_package_rows = {
    row["intervention_id"]: row
    for row in package_scores
    if row["token_scenario"] == "base"
    and row["reuse_assumption_scenario"] == "reuse_base"
}
assert set(base_package_rows) == {row["intervention_id"] for row in package_decisions}
architecture_ids = {"IL-PUNJABI", "IL-HU", "IL-NGUNI", "IL-SOTHO"}
architecture_decisions = [
    row for row in package_decisions if row["intervention_id"] in architecture_ids
]
assert len(architecture_decisions) == 4
assert all(row["selected_for_deduplicated_portfolio"] == "false" for row in package_decisions)
assert all(row["named_outputs_with_exact_population"] == row["expected_new_named_outputs"] for row in architecture_decisions)
assert all(row["base_marginal_joined_outputs"] == row["expected_new_named_outputs"] for row in architecture_decisions)
assert all(row["territory_proxy_derived_outputs"] == "0" for row in architecture_decisions)
assert all(row["access_interval_reconciled"] == "true" for row in architecture_decisions)
assert all(row["upstream_population_union_admissible"] == "false" for row in architecture_decisions)
assert all(row["decision_reason"] == "exclude_upstream_population_union_not_admissible" for row in architecture_decisions)
assert all(integer(row["modeled_token_savings"]) > 0 for row in architecture_decisions)
assert all(base_package_rows[row["intervention_id"]]["rankable_as_observed_population_gross_sum"] == "false" for row in architecture_decisions)
assert base_package_rows["IL-ISV"]["population_evidence_status"] == "constructed_bridge_zero_conservative_reach"
assert base_package_rows["IL-ISV"]["exact_named_output_population_base"] == "0"

table6_fields = [
    "intervention_id",
    "mechanism_class",
    "table6_panel",
    "cardinal_ranking_treatment",
    "component_subtotal_treatment",
    "base_reuse_status",
    "selected_for_deduplicated_portfolio",
    "decision_reason",
    "upstream_population_union_admissible",
    "expected_new_named_outputs",
    "named_outputs_with_exact_population",
    "population_coverage_fraction_of_named_outputs",
    "included_target_profiles",
    "included_population_observation_ids",
    "included_population_source_ids",
    "population_years",
    "included_population_observation_measures",
    "included_population_source_locators",
    "included_population_observation_caveats",
    "population_evidence_status",
    "exact_named_output_population_low",
    "exact_named_output_population_base",
    "exact_named_output_population_high",
    "marginal_access_low_sum",
    "base_marginal_access_sensitivity_sum",
    "marginal_access_high_sum",
    "marginal_access_high_optimistic_sensitivity_sum",
    "marginal_score_joined_output_count",
    "marginal_score_territory_proxy_derived_output_count",
    "independent_named_output_tokens_base",
    "shared_core_tokens_base",
    "modeled_token_savings_base",
    "named_output_compute_savings_fraction_base_sensitivity",
    "rankable_as_observed_population_gross_sum",
    "exclusions_and_nonadditivity",
    "caveat",
    "interpretation",
]
table6_rows: list[dict[str, object]] = []
for decision in sorted(
    package_decisions,
    key=lambda row: (row["intervention_id"] not in architecture_ids, row["intervention_id"]),
):
    score = base_package_rows[decision["intervention_id"]]
    row: dict[str, object] = {}
    for field in table6_fields:
        row[field] = decision.get(field, score.get(field, ""))
    row["independent_named_output_tokens_base"] = decision[
        "independent_named_output_tokens_base"
    ]
    row["shared_core_tokens_base"] = decision["shared_core_tokens_base"]
    row["modeled_token_savings_base"] = decision["modeled_token_savings"]
    row["named_output_compute_savings_fraction_base_sensitivity"] = score[
        "named_output_compute_savings_fraction"
    ]
    if decision["intervention_id"] in architecture_ids:
        row["table6_panel"] = "architecture_sensitivity_noncardinal"
        row["cardinal_ranking_treatment"] = "excluded_no_package_substitution"
        row["component_subtotal_treatment"] = (
            "diagnostic_component_subtotals_only_nonadditive_noncardinal_not_unique_people"
        )
    else:
        row["table6_panel"] = "excluded_package_proposals"
        row["cardinal_ranking_treatment"] = "excluded"
        row["component_subtotal_treatment"] = (
            "partial_or_zero_diagnostic_component_subtotals_nonadditive_noncardinal"
        )
    row["base_reuse_status"] = (
        "unobserved_base_reuse_sensitivity_not_empirical_production_saving"
    )
    row["marginal_access_high_optimistic_sensitivity_sum"] = score["marginal_access_high_sum"]
    observation_ids = [
        observation_id
        for observation_id in score["included_population_observation_ids"].split(";")
        if observation_id
    ]
    assert all(observation_id in population_by_id for observation_id in observation_ids)
    row["included_population_observation_measures"] = ";".join(
        f"{observation_id}={population_by_id[observation_id]['measure_type']}"
        for observation_id in observation_ids
    )
    row["included_population_source_locators"] = ";".join(
        f"{observation_id}={population_by_id[observation_id]['source_locator']}"
        for observation_id in observation_ids
    )
    row["included_population_observation_caveats"] = ";".join(
        f"{observation_id}={population_by_id[observation_id]['caveats']}"
        for observation_id in observation_ids
    )
    row["caveat"] = decision["caveat"]
    row["interpretation"] = score["interpretation"]
    table6_rows.append(row)

table6_architecture_rows = [
    row for row in table6_rows if row["table6_panel"] == "architecture_sensitivity_noncardinal"
]
table6_exclusion_rows = [
    row for row in table6_rows if row["table6_panel"] == "excluded_package_proposals"
]
assert len(table6_architecture_rows) == 4
assert len(table6_exclusion_rows) == 11
table6a_path = write_csv(
    "table6a_architecture_sensitivity_noncardinal.csv", table6_fields, table6_architecture_rows
)
table6b_path = write_csv(
    "table6_package_exclusions_noncardinal.csv", table6_fields, table6_exclusion_rows
)
stale_table6 = OUT / "table6_shared_core_packages.csv"
if stale_table6.exists():
    stale_table6.unlink()

# Table 7: initial FR-2 allocations and separately costed OpenStax next steps.
scale_one = {
    (row["portfolio_id"], row["adaptation_depth"], row["scenario"]): row
    for row in scale
    if row["language_or_localized_output_count"] == "1"
}
table7_fields = [
    "allocation_stage",
    "allocation_group_id",
    "intervention_class",
    "intervention_count",
    "localized_output_count",
    "member_intervention_ids",
    "curriculum_portfolio_ids",
    "adaptation_depths",
    "editable_units_per_output",
    "source_tokens_per_output_or_scenario_range",
    "gross_tokens_low_total",
    "gross_tokens_base_total",
    "gross_tokens_high_total",
    "token_status",
    "source_ids",
    "caveat",
]
table7_rows: list[dict[str, object]] = []
members = top100
table7_rows.append(
    {
        "allocation_stage": "initial_common_denominator",
        "allocation_group_id": "FR2_FAIL_CLOSED_NATURAL_EDITIONS",
        "intervention_class": "natural_language_edition",
        "intervention_count": len(members),
        "localized_output_count": total(members, "output_count"),
        "member_intervention_ids": ";".join(row["intervention_id"] for row in members),
        "curriculum_portfolio_ids": "FR-2",
        "adaptation_depths": "D3",
        "editable_units_per_output": "210",
        "source_tokens_per_output_or_scenario_range": "120083",
        "gross_tokens_low_total": total(members, "gross_tokens_low"),
        "gross_tokens_base_total": total(members, "gross_tokens_base"),
        "gross_tokens_high_total": total(members, "gross_tokens_high"),
        "token_status": "frozen_fail_closed_independent_natural_output_scenario_totals",
        "source_ids": "ACE-A013",
        "caveat": "No package substitution or shared-core reuse is credited in the cardinal portfolio.",
    }
)

natural = [row for row in top100 if row["intervention_type"] == "natural_language_edition"]
natural_groups: dict[tuple[str, str], list[dict[str, str]]] = {}
for row in natural:
    natural_groups.setdefault(
        (row["recommended_openstax_next_product"], row["recommended_openstax_depth"]), []
    ).append(row)

for (portfolio_id, depth), members in sorted(natural_groups.items()):
    low = scale_one[(portfolio_id, depth, "low")]
    base = scale_one[(portfolio_id, depth, "base")]
    high = scale_one[(portfolio_id, depth, "high")]
    assert total(members, "openstax_next_gross_tokens_low") == sum(
        integer(row["openstax_next_gross_tokens_low"]) for row in members
    )
    table7_rows.append(
        {
            "allocation_stage": "next_openstax",
            "allocation_group_id": f"{portfolio_id}_{depth}_NATURAL",
            "intervention_class": "natural_language_edition",
            "intervention_count": len(members),
            "localized_output_count": total(members, "output_count"),
            "member_intervention_ids": ";".join(row["intervention_id"] for row in members),
            "curriculum_portfolio_ids": portfolio_id,
            "adaptation_depths": depth,
            "editable_units_per_output": base["editable_units_per_output"],
            "source_tokens_per_output_or_scenario_range": ";".join(
                [
                    low["source_tokens_per_output"],
                    base["source_tokens_per_output"],
                    high["source_tokens_per_output"],
                ]
            ),
            "gross_tokens_low_total": total(members, "openstax_next_gross_tokens_low"),
            "gross_tokens_base_total": total(members, "openstax_next_gross_tokens_base"),
            "gross_tokens_high_total": total(members, "openstax_next_gross_tokens_high"),
            "token_status": "linear_independent_output_scaling_from_frozen_portfolio",
            "source_ids": base["source_ids"],
            "caveat": base["assumption"],
        }
    )

table7_path = write_csv("table7_curriculum_allocation_summary.csv", table7_fields, table7_rows)
fr2_allocation_rows = [row for row in table7_rows if row["allocation_stage"] == "initial_common_denominator"]
assert sum(integer(str(row["intervention_count"])) for row in fr2_allocation_rows) == 100
assert sum(integer(str(row["localized_output_count"])) for row in fr2_allocation_rows) == 100
for suffix in ["low", "base", "high"]:
    assert sum(integer(str(row[f"gross_tokens_{suffix}_total"])) for row in fr2_allocation_rows) == total(
        top100, f"gross_tokens_{suffix}"
    )
natural_next_rows = [
    row
    for row in table7_rows
    if row["allocation_stage"] == "next_openstax"
    and row["intervention_class"] == "natural_language_edition"
]
assert sum(integer(str(row["intervention_count"])) for row in natural_next_rows) == 100
assert sum(integer(str(row["localized_output_count"])) for row in natural_next_rows) == 100

# Table 8: retain both richly served controls and non-control profile/ranking
# exclusions so the denominator is fully auditable. Join the exact population
# measure/year/locator back from the population master rather than allowing the
# compact control file to obscure its source universe.
table8_fields = list(negative_controls[0].keys()) + [
    "population_low",
    "population_high",
    "population_measure",
    "reference_date_or_year",
    "count_unit",
    "source_locator",
    "population_observation_caveats",
]
table8_enriched: list[dict[str, object]] = []
for control in negative_controls:
    observation_id = control["population_observation_id"]
    assert observation_id in population_by_id
    observation = population_by_id[observation_id]
    assert observation["source_id"] == control["population_source_id"]
    assert observation["population_base"] == control["population_base"]
    table8_enriched.append(
        {
            **control,
            "population_low": observation["population_low"],
            "population_high": observation["population_high"],
            "population_measure": observation["measure_type"],
            "reference_date_or_year": observation["reference_date_or_year"],
            "count_unit": observation["count_unit"],
            "source_locator": observation["source_locator"],
            "population_observation_caveats": observation["caveats"],
        }
    )
table8_rows = sorted(
    table8_enriched,
    key=lambda row: (row["control_or_exclusion"], -integer(row["population_base"]), row["intervention_id"]),
)
table8_path = write_csv("table8_negative_controls_and_exclusions.csv", table8_fields, table8_rows)

# Concise replacement prose. Tables 2 and 3 remain full machine-readable tables;
# the Markdown embeds only the compact paper-facing summaries.
top_by_gross = table2_rows[:10]
architecture_sensitivities = table6_architecture_rows
rich_controls = [row for row in negative_controls if row["control_or_exclusion"] == "richly_served_negative_control"]
profile_exclusions = [row for row in negative_controls if row["control_or_exclusion"] != "richly_served_negative_control"]

lines: list[str] = []
lines.extend(
    [
        "## 7. Results",
        "",
        "### 7.1 Which populations are most affected?",
        "",
        f"Table 2 reports all {portfolio_count} canonical natural-language interventions as source-bounded gross ceilings. "
        "These values retain each source's territory, year, age universe, question, and measure; they "
        "are not interchangeable estimates of people harmed by language mismatch. The largest base "
        "ceilings in the frozen candidate set are:",
        "",
        "| Display order | Intervention | Profile(s) | Gross base ceiling | Measure | Year(s) | Source ID(s) |",
        "|---:|---|---|---:|---|---|---|",
    ]
)
for row in top_by_gross:
    lines.append(
        f"| {row['gross_ceiling_display_order']} | {row['intervention_name']} | "
        f"{row['target_profiles']} | {fmt(row['population_base'])} | {row['population_measure']} | "
        f"{row['population_years']} | {row['population_source_ids']} |"
    )
lines.extend(
    [
        "",
        "The gross ceilings cannot answer how many readers newly gain comfortable access. Table 3 "
        "therefore keeps low, base, and high marginal-access values separate. The base and optimistic "
        f"columns are factor-model sensitivities, not observed harmed-population counts. All {portfolio_count} low "
        "values are zero because at least one access or non-overlap factor lacks a positive direct lower "
        "bound. The conservative efficiency view is consequently degenerate: every intervention ties "
        f"on the interval [1, {portfolio_count}], and that view is reported but not used to fill portfolio positions.",
        "",
        "### 7.2 Top 10 interventions",
        "",
        "The selector alternates base, optimistic, and scarcity sensitivity lanes. Under the fail-closed "
        "rule, no shared-core package substitutes for its constituent natural-language rows. This is a portfolio order, "
        "not a claim of a uniquely identified welfare ranking.",
        "",
        "| Position | Intervention | Profile(s) | Gross base ceiling | Base marginal sensitivity | "
        "Base gross tokens | Informative rank range | Demonstrated-needs first package |",
        "|---:|---|---|---:|---:|---:|---:|---|",
    ]
)
for row in sorted(top10, key=lambda item: integer(item["portfolio_position"])):
    need = needs_assignment(row)
    lines.append(
        f"| {row['portfolio_position']} | {row['intervention_name']} | {row['target_profiles']} | "
        f"{fmt(row['population_base'])} | {fmt(row['marginal_access_base_sensitivity'])} | "
        f"{fmt(row['gross_tokens_base'])} | {row['informative_rank_best']}–{row['informative_rank_worst']} | "
        f"{need['needs_first_package_short']} |"
    )
lines.extend(
    [
        "",
        "### 7.3 What mathematics does the Top 10 actually need?",
        "",
        "Population rank does not select content. The audited needs layer distinguishes foundational "
        "recovery, bilingual transfer, secondary-to-tertiary bridging, a coherent undergraduate spine, "
        "and advanced/reference work. OpenStax and Open Logic remain concrete reusable source baselines, "
        "but no project title is assigned merely because its source-token denominator is convenient.",
        "",
        "| Intervention | Measured need or best available proxy | First useful open package | Evidence / package confidence |",
        "|---|---|---|---|",
    ]
)
for row in sorted(top10, key=lambda item: integer(item["portfolio_position"])):
    exact = needs_by_intervention[row["intervention_id"]]
    lines.append(
        f"| {row['intervention_name']} | {exact['observed_need']} | "
        f"{SHORT_NEEDS_PACKAGES[row['intervention_id']]} | "
        f"{exact['observed_need_confidence']} / {exact['package_inference_confidence']} |"
    )
lines.extend(
    [
        "",
        "The Indian rows use rural state proxies and therefore do not turn one state percentage into a "
        "whole-language learning rate. Western Punjabi is the Pakistan/Shahmukhi profile, not Indian "
        "Gurmukhi Punjabi. Indonesia's PISA evidence is not Javanese-specific. Those limits change the "
        "confidence label and product form; they do not justify replacing unknowns with zero.",
        "",
        "### 7.4 Top 100 portfolio",
        "",
        "The numbered Top 100 contains 100 natural-language interventions and 100 separately named "
        "localized outputs; no package occupies a cardinal position. Accessibility "
        "remains a separate, non-cardinal safeguard backlog and does not consume a linguistic position. "
        "The frozen FR-2 workload sums to 91,273,700 low, 407,304,900 base, and 1,866,457,100 high "
        "gross tokens. These compute totals are additive; the heterogeneous population measures are not "
        "summed as a count of unique people.",
        "",
        "| Portfolio lane | Interventions | Localized outputs | Base / optimistic / scarcity admissions | "
        "FR-2 base gross tokens |",
        "|---|---:|---:|---:|---:|",
    ]
)
for row in table5_rows:
    lines.append(
        f"| {row['portfolio_lane']} | {row['intervention_count']} | {row['localized_output_count']} | "
        f"{row['base_admission_count']} / {row['optimistic_admission_count']} / "
        f"{row['scarcity_admission_count']} | {fmt(row['fr2_gross_tokens_base_sum'])} |"
    )
lines.extend(
    [
        "",
        "### 7.5 Interlanguage and shared-core comparisons",
        "",
        "No package replaces a natural-language row in the fail-closed cardinal portfolio. IL-PUNJABI, "
        "IL-HU, IL-NGUNI, and IL-SOTHO retain complete component joins and positive modeled savings, "
        "but their upstream population unions are not admissible. Their displayed population values are "
        "diagnostic component subtotals only: they are nonadditive, noncardinal, and not unique-person, "
        "family-level, or constructed-bridge comprehension reach. Base reuse is an unobserved sensitivity, "
        "not an empirical production saving.",
        "",
        "| Architecture | Named outputs | Profiles | Diagnostic component subtotal (noncardinal) | "
        "Independent base tokens | Shared-core base sensitivity | Modeled saving sensitivity |",
        "|---|---:|---|---:|---:|---:|---:|",
    ]
)
for row in architecture_sensitivities:
    lines.append(
        f"| {row['intervention_id']} | {row['expected_new_named_outputs']} | "
        f"{row['included_target_profiles']} | {fmt(row['exact_named_output_population_base'])} | "
        f"{fmt(row['independent_named_output_tokens_base'])} | {fmt(row['shared_core_tokens_base'])} | "
        f"{fmt(row['modeled_token_savings_base'])} |"
    )
lines.extend(
    [
        "",
        "The other 11 package proposals are excluded because planned named-output coverage, "
        "exact population joins, constituent score joins, or interval reconciliation is incomplete. "
        "Constructed Interslavic has a zero registered cardinal lower bound because no exact sustained "
        "mathematical-reading population result is available; that is not a substantive estimate of zero "
        "mathematical usefulness. Mathematical formalism can reduce prose dependence for expert readers, "
        "while novice word problems and explanations remain language-heavy. The paper therefore treats "
        "expertise and formal density as a stage-specific interlanguage prior to be measured, not as a "
        "blanket family multiplier or a reason to dismiss the architecture. Reuse fractions remain modeled "
        "sensitivities rather than observed production savings.",
        "",
        "### 7.6 Fixed-source OpenStax and Open Logic compute comparators",
        "",
        "FR-2 at D3 (210 editable units; 120,083 measured source alpha tokens) remains the common "
        "language-priority compute comparator. The older territory-proxy rule also groups the 100 rows "
        "into fixed OpenStax scenarios. These are reproducible workload counterfactuals, not claims that "
        "all populations need Formal Reasoning Core first or that the listed OpenStax bundle is locally missing. "
        "Actual commissioning follows Table 5b and `top100_needs_assignment.csv`; the 90 non-audited rows "
        "retain a needs-audit status rather than a fabricated book recommendation.",
        "",
        "| Next portfolio | Depth | Interventions | Outputs | Low tokens | Base tokens | High tokens |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
)
for row in table7_rows:
    if row["allocation_stage"] != "next_openstax" or row["intervention_class"] != "natural_language_edition":
        continue
    lines.append(
        f"| {row['curriculum_portfolio_ids']} | {row['adaptation_depths']} | "
        f"{row['intervention_count']} | {row['localized_output_count']} | "
        f"{fmt(row['gross_tokens_low_total'])} | {fmt(row['gross_tokens_base_total'])} | "
        f"{fmt(row['gross_tokens_high_total'])} |"
    )
lines.extend(
    [
        "",
        "Table 7 costs only the 100 cardinal natural-language interventions under fixed-source comparator "
        "scenarios. Architecture sensitivities remain in Table 6 and are not transferred into OpenStax "
        "compute or cardinal output totals. These totals must not be relabeled as the needs-optimal curriculum.",
        "",
        "### 7.7 Sensitivity and negative controls",
        "",
        "The informative rank range spans the base, optimistic, and scarcity views. The conservative "
        "zero floor is disclosed separately and does not manufacture an arbitrary strict order. "
        "Richly served controls remain available for non-overlap, subgroup, and accessibility tests but "
        "are not generic translation priorities. Unresolved profiles and D0 profile/population mismatches "
        "are exclusions, not evidence that their communities are already served.",
        "",
        "| Target | Profile | Territory | Gross base population | Measure | Year | Source ID | Classification |",
        "|---|---|---|---:|---|---|---|---|",
    ]
)
for row in rich_controls:
    lines.append(
        f"| {row['target_name']} | {row['target_profile']} | {row['territory']} | "
        f"{fmt(row['population_base'])} | {population_by_id[row['population_observation_id']]['measure_type']} | "
        f"{population_by_id[row['population_observation_id']]['reference_date_or_year']} | "
        f"{row['population_source_id']} | {row['control_or_exclusion']} |"
    )
lines.extend(
    [
        "",
        f"Table 8 also preserves {len(profile_exclusions)} non-control exclusions: three unresolved "
        "localized-output profiles and two D0 profile/population mismatches. They are not counted as "
        "negative controls and must not be silently converted into recommendations.",
        "",
        "The complete machine-readable tables preserve exact population measures, years, observation "
        "IDs, source IDs, factor statuses, compute scenarios, package exclusions, and tie-aware ranks.",
        "",
    ]
)

results_path = OUT / "RESULTS_SECTION_GENERATED.md"
results_path.write_text("\n".join(lines), encoding="utf-8")

verified_top10 = ", ".join(
    row["intervention_id"]
    for row in sorted(top10, key=lambda row: integer(row["portfolio_position"]))
)
validation_lines = [
    "# Results tables validation",
    "",
    f"- PASS: the fail-closed candidate file has {portfolio_count} unique natural-language intervention IDs and positions 1–{portfolio_count}.",
    "- PASS: `TOP_10.csv` exactly matches frozen Top-100 positions 1–10.",
    f"- VERIFIED TOP 10: {verified_top10}.",
    "- PASS: `TOP_100.csv` has 100 unique natural-language intervention IDs, 100 named outputs, and positions 1–100; no package is cardinal.",
    f"- PASS: every one of the {portfolio_count} conservative marginal-access lower bounds is zero; the conservative rank is a global tie and is not used for admission.",
    "- PASS: zero package substitutions are selected.",
    "- PASS: IL-PUNJABI, IL-HU, IL-NGUNI, and IL-SOTHO are isolated in Table 6a as nonadditive, noncardinal architecture sensitivities; their upstream population unions are inadmissible and their base reuse is explicitly unobserved.",
    "- PASS: constructed Interslavic has zero conservative population reach and is not selected.",
    "- PASS: Table 5 lane counts sum to 100 interventions and 100 separately named outputs; its low/base/high token totals reconcile exactly to `TOP_100.csv`.",
    "- PASS: Table 7 initial FR-2 allocations sum to 100 natural-language interventions and 100 outputs and reconcile to all three frozen token scenarios.",
    "- PASS: Table 7 natural-language OpenStax-next allocations sum to 100 interventions and 100 outputs; no architecture sensitivity is transferred into cardinal compute.",
    "- PASS: all Table 6 package and Table 8 control/exclusion population observation IDs join exactly to `population_observations_master.csv`; Table 8 source IDs and base counts reconcile.",
    "- PASS: accessibility occupies zero numbered linguistic positions and remains a separate non-cardinal safeguard backlog.",
    "",
    "No population arithmetic sum is presented as a unique-person total. Base and optimistic marginal-access quantities are labelled sensitivities, and package reuse savings are labelled modeled sensitivities.",
    "",
]
validation_path = OUT / "RESULTS_TABLES_VALIDATION.md"
validation_path.write_text("\n".join(validation_lines), encoding="utf-8")

generated = [
    table2_path,
    table3_path,
    table4_path,
    table5_path,
    table5_members_path,
    table6a_path,
    table6b_path,
    table7_path,
    table8_path,
    results_path,
    validation_path,
]

manifest = {
    "input_identity": {
        name: {
            "bytes": (ROOT / name).stat().st_size,
            "sha256": sha256(ROOT / name),
        }
        for name in [
            "portfolio_linguistic_candidates.csv",
            "TOP_10.csv",
            "TOP_100.csv",
            "package_replacement_decisions.csv",
            "interlanguage_package_scores.csv",
            "negative_controls_and_profile_exclusions.csv",
            "portfolio_scale_planning.csv",
            "population_observations_master.csv",
            "PAPER.md",
        ]
    },
    "validation": {
        "portfolio_rows": len(portfolio),
        "portfolio_all_natural": all(
            row["intervention_type"] == "natural_language_edition" for row in portfolio
        ),
        "top10_rows": len(top10),
        "top10_order": [
            {
                "position": integer(row["portfolio_position"]),
                "intervention_id": row["intervention_id"],
                "intervention_name": row["intervention_name"],
            }
            for row in sorted(top10, key=lambda row: integer(row["portfolio_position"]))
        ],
        "top100_rows": len(top100),
        "top100_all_natural": all(
            row["intervention_type"] == "natural_language_edition" for row in top100
        ),
        "top100_lane_counts": dict(sorted(Counter(row["portfolio_lane"] for row in top100).items())),
        "top100_admission_lane_counts": dict(
            sorted(Counter(row["admission_lane"] for row in top100).items())
        ),
        "top100_fr2_gross_tokens": {
            scenario: total(top100, f"gross_tokens_{scenario}")
            for scenario in ["low", "base", "high"]
        },
        "selected_packages": sum(
            row["selected_for_deduplicated_portfolio"] == "true" for row in package_decisions
        ),
        "noncardinal_architecture_sensitivities": len(architecture_sensitivities),
        "architecture_sensitivity_ids": sorted(architecture_ids),
        "conservative_zero_rows": sum(number(row["marginal_access_low"]) == 0 for row in portfolio),
        "top100_localized_outputs": total(top100, "output_count"),
        "accessibility_cardinal_slots": 0,
    },
    "outputs": {
        path.name: {"bytes": path.stat().st_size, "sha256": sha256(path)} for path in generated
    },
}
manifest_path = OUT / "RESULTS_TABLES_MANIFEST.json"
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps({"manifest": str(manifest_path), **manifest["validation"]}, indent=2))
