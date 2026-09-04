#!/usr/bin/env python3
"""Build the publication-facing multi-lane funding portfolio.

The direct-person Top 100 is one comparable lane, not a universal ordering of
every educational intervention.  Stage cohorts, structural access, displaced
learners, bridge experiments, and unresolved high-consequence coverage checks
remain separate so incompatible denominators are never converted into one
score.  Prior or local production is not read by this builder.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "structured"
A = ROOT / "agent_reports"
Q = ROOT / "qa"

TOP100 = S / "TOP100_NEEDS_ONLY_v3.csv"
STAGE = S / "ORDER_STAGE_OPPORTUNITY_v3.csv"
LARGE = S / "LARGE_POPULATION_OMISSION_SUPPLEMENT_v1.csv"
STRUCTURAL = S / "STRUCTURAL_ACCESS_COMMISSIONING_REGISTER_v1.csv"
DISPLACEMENT = S / "DISPLACEMENT_EDUCATION_PORTFOLIO_v1.csv"
BRIDGES = A / "INTERLANGUAGE_STRUCTURED_EVIDENCE_MATRIX.csv"
SENTINELS = S / "GLOBAL_INCLUSION_SENTINEL_STATUS_v1.csv"
OVERLAP = S / "PORTFOLIO_OVERLAP_REGISTER_v1.csv"
AUTHORIZATION = S / "EVIDENCE_AUTHORIZATION_v1.csv"

OUT = S / "GLOBAL_FUNDING_PORTFOLIO_v1.csv"
LANES_OUT = S / "GLOBAL_DECISION_LANES_v1.csv"
QA_OUT = Q / "GLOBAL_FUNDING_PORTFOLIO_QA_v1.json"


FIELDS = [
    "portfolio_row_id",
    "decision_lane",
    "lane_rank",
    "target_id",
    "target_label",
    "language_tag_or_mode",
    "territory_or_community",
    "population_low_persons",
    "population_base_persons",
    "population_high_persons",
    "population_definition",
    "population_reference_year",
    "model_median_unmet_need_or_opportunity",
    "standard_compute_p50_fecu",
    "evidence_status",
    "recommendation_basis",
    "priority_action",
    "publication_caveat",
    "source_ids",
    "source_urls",
    "nonadditivity_rule",
    "local_work_exclusion",
    "row_sha256",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def file_id(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest().upper(),
    }


def digest(row: dict[str, Any]) -> str:
    body = {key: clean(value) for key, value in row.items() if key != "row_sha256"}
    data = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest().upper()


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for raw in rows:
            row = {field: clean(raw.get(field, "")) for field in fields}
            if "row_sha256" in fields:
                row["row_sha256"] = digest(row)
            writer.writerow(row)


def number_sort(value: str) -> tuple[int, float]:
    try:
        return (0, -float(value))
    except (TypeError, ValueError):
        return (1, 0.0)


overlap_by_target: dict[str, list[dict[str, str]]] = {}
for item in read_csv(OVERLAP):
    overlap_by_target.setdefault(item["edition_target_id"], []).append(item)
authorization_by_id = {
    item["authorization_id"]: item for item in read_csv(AUTHORIZATION)
}

rows: list[dict[str, Any]] = []

# Lane 1: the only globally ordered comparison, limited to compatible,
# source-authorized person-language measures.
for item in read_csv(TOP100):
    overlaps = overlap_by_target.get(item["edition_target_id"], [])
    authorization = authorization_by_id.get(item["authorization_id"], {})
    overlap_note = " ".join(sorted({entry["assessment"] for entry in overlaps}))
    rows.append(
        {
            "portfolio_row_id": f"direct:{item['decision_rank']}:{item['edition_target_id']}",
            "decision_lane": "DIRECT_PERSON_COMPARABLE",
            "lane_rank": item["decision_rank"],
            "target_id": item["edition_target_id"],
            "target_label": item["label"],
            "language_tag_or_mode": item["language_tag"],
            "population_low_persons": item["population_low"],
            "population_base_persons": item["population_base"],
            "population_high_persons": item["population_high"],
            "population_definition": item["population_definition"],
            "population_reference_year": item["population_reference_year"],
            "model_median_unmet_need_or_opportunity": item["intrinsic_need_median"],
            "standard_compute_p50_fecu": item["standard_compute_p50_fecu"],
            "evidence_status": item["population_confidence"],
            "recommendation_basis": "Source-authorized person denominator under the common hierarchical prior; rank is model-conditional and currently population-dominant.",
            "priority_action": "Measure target-stage resource fit and commission the highest-value open package without changing the population need estimate for prior production.",
            "publication_caveat": "Comparable-subset rank, not a moral ranking or a complete global allocation order. Missing target-specific factors use common priors.",
            "source_ids": item["population_source_id"],
            "source_urls": authorization.get("source_urls", ""),
            "nonadditivity_rule": overlap_note or "Standalone intervention only; do not sum with another language, stage, script, or territory row without a proved disjoint-person crosswalk.",
            "local_work_exclusion": item["local_work_exclusion"],
        }
    )

# Lane 2: direct educational-stage cohorts that are not whole-language reader
# populations and therefore never compete numerically with Lane 1.
for item in read_csv(STAGE):
    authorization = authorization_by_id.get(item["authorization_id"], {})
    rows.append(
        {
            "portfolio_row_id": f"stage:{item['opportunity_rank']}:{item['edition_target_id']}",
            "decision_lane": "STAGE_OPPORTUNITY",
            "lane_rank": item["opportunity_rank"],
            "target_id": item["edition_target_id"],
            "target_label": item["label"],
            "language_tag_or_mode": item["language_tag"],
            "population_low_persons": item["population_low"],
            "population_base_persons": item["population_base"],
            "population_high_persons": item["population_high"],
            "population_definition": item["population_definition"],
            "population_reference_year": item["population_reference_year"],
            "model_median_unmet_need_or_opportunity": item["intrinsic_need_median"],
            "standard_compute_p50_fecu": item["standard_compute_p50_fecu"],
            "evidence_status": item["population_confidence"],
            "recommendation_basis": "Directly defined learner or sector opportunity; not a whole-language population.",
            "priority_action": "Audit stage, subject, openness, accessibility, and academic-language gaps inside the measured cohort; commission only the fitted package.",
            "publication_caveat": "Stage-opportunity order is separate from the direct-person language order and cannot be summed with it.",
            "source_ids": item["population_source_id"],
            "source_urls": authorization.get("source_urls", ""),
            "nonadditivity_rule": "This learner/sector cohort may be nested in language, age, disability, migration, or enrolment totals.",
            "local_work_exclusion": item["local_work_exclusion"],
        }
    )

# Lane 3a: very large or strategically mandatory constructs retained for
# evidence acquisition and package decisions, not relabelled as comfortable
# readers or unmet-need counts.
large_rows = sorted(
    read_csv(LARGE),
    key=lambda row: (number_sort(row.get("population_base_persons", "")), row.get("label", "")),
)
for index, item in enumerate(large_rows, start=1):
    rows.append(
        {
            "portfolio_row_id": f"context:{item['stratum_id']}",
            "decision_lane": "MANDATORY_LARGE_CONTEXT_AND_VOI",
            "lane_rank": index,
            "target_id": item["stratum_id"],
            "target_label": item["label"],
            "language_tag_or_mode": item["script_or_mode"],
            "territory_or_community": item["territory"],
            "population_low_persons": item["population_low_persons"],
            "population_base_persons": item["population_base_persons"],
            "population_high_persons": item["population_high_persons"],
            "population_definition": item["population_definition"],
            "population_reference_year": item["population_reference_year"],
            "evidence_status": item["evidence_confidence"],
            "recommendation_basis": "High-scale context that could change allocation if converted into an exact stage-language-access denominator.",
            "priority_action": "Acquire an exact comfortable-reader or stage-subject denominator and audit the functional supply endpoint before comparison.",
            "publication_caveat": item["uncertainty_incompatibilities"],
            "source_ids": item["source_ids"],
            "source_urls": item["source_urls"],
            "nonadditivity_rule": "Context, exposure, home-use, policy, ability, and mixed-proficiency constructs are not automatically additive or interchangeable.",
            "local_work_exclusion": "true",
        }
    )

# Lane 3b: exact global sentinel gaps stay visible even when no population
# measure can be assigned.  They receive no synthetic count or score.
gap_statuses = {
    "MISSING_EXACT_TARGET",
    "PRESENT_BASE_LANGUAGE_ONLY_EXACT_TERRITORY_SCRIPT_OR_STANDARD_PROFILE_MISSING",
    "PRESENT_CONTEXT_STRATUM_NO_EXACT_EDITION_TARGET",
}
gap_rows = [item for item in read_csv(SENTINELS) if item["presence_status"] in gap_statuses]
for index, item in enumerate(gap_rows, start=1):
    rows.append(
        {
            "portfolio_row_id": f"sentinel-gap:{item['sentinel_id']}",
            "decision_lane": "MANDATORY_SENTINEL_GAP_AND_VOI",
            "lane_rank": index,
            "target_id": item["expected_edition_target_id"],
            "target_label": item["target_label"],
            "language_tag_or_mode": item["expected_language_tag"] or item["script_or_mode"],
            "territory_or_community": item["territory_or_community"],
            "evidence_status": item["presence_status"],
            "recommendation_basis": item["why_required"],
            "priority_action": item["preferred_evidence_action"],
            "publication_caveat": "Coverage sentinel only; absence of a source-bound denominator is not zero need.",
            "nonadditivity_rule": "Zero population credit until an exact identity and source-bound denominator are registered.",
            "local_work_exclusion": "true",
        }
    )

# Lane 4a: signed-language and accessibility formats use their own functional
# denominators.  Proxy values remain visibly labelled as proxies.
structural_rows = sorted(
    read_csv(STRUCTURAL),
    key=lambda row: (row.get("structural_lane", ""), number_sort(row.get("allocation_denominator_base_persons", "")), row.get("target_or_intervention", "")),
)
for index, item in enumerate(structural_rows, start=1):
    rows.append(
        {
            "portfolio_row_id": f"structural:{item['structural_id']}",
            "decision_lane": "STRUCTURAL_SIGNED_AND_ACCESSIBILITY",
            "lane_rank": index,
            "target_id": item["edition_target_id"] or item["structural_id"],
            "target_label": item["target_or_intervention"],
            "language_tag_or_mode": item["language_tag"] or item["structural_lane"],
            "territory_or_community": item["territory_or_community"],
            "population_base_persons": item["allocation_denominator_base_persons"],
            "population_definition": item["context_unit"],
            "evidence_status": item["evidence_status"],
            "recommendation_basis": item["commissioning_band"],
            "priority_action": "Commission the exact functional mode or acquire its missing denominator; never substitute a hearing-loss, disability, or national-population proxy for language users.",
            "publication_caveat": item["rank_use"],
            "source_ids": item["source_record_id"],
            "source_urls": item["source_url"],
            "nonadditivity_rule": item["nonadditivity_rule"],
            "local_work_exclusion": "true",
        }
    )

# Lane 4b: displaced learners require host-specific multilingual portfolios.
displacement_rows = sorted(
    read_csv(DISPLACEMENT),
    key=lambda row: (number_sort(row.get("population_base_persons", "")), row.get("portfolio_label", "")),
)
for index, item in enumerate(displacement_rows, start=1):
    rows.append(
        {
            "portfolio_row_id": f"displacement:{item['portfolio_id']}",
            "decision_lane": "DISPLACEMENT_HOST_SPECIFIC",
            "lane_rank": index,
            "target_id": item["portfolio_id"],
            "target_label": item["portfolio_label"],
            "language_tag_or_mode": item["language_script_arms"],
            "territory_or_community": item["host_scope"],
            "population_low_persons": item["population_low_persons"],
            "population_base_persons": item["population_base_persons"],
            "population_high_persons": item["population_high_persons"],
            "population_definition": item["population_definition"],
            "population_reference_year": item["population_reference_year"],
            "evidence_status": item["evidence_status"],
            "recommendation_basis": item["education_stage_needs"],
            "priority_action": item["delivery_needs"],
            "publication_caveat": item["rank_use"],
            "source_ids": item["source_ids"],
            "source_urls": item["source_urls"],
            "nonadditivity_rule": item["nonadditivity_rule"],
            "local_work_exclusion": "true",
        }
    )

# Lane 4c: bridge/interlanguage designs may reduce production cost or improve
# comprehension, but receive no reader count without endpoint-specific evidence.
grade_order = {"A": 0, "B": 1, "C": 2, "D": 3}
bridge_rows = sorted(
    read_csv(BRIDGES),
    key=lambda row: (grade_order.get(row.get("evidence_grade", ""), 9), row.get("bridge_name", "")),
)
for index, item in enumerate(bridge_rows, start=1):
    rows.append(
        {
            "portfolio_row_id": f"bridge:{item['bridge_id']}",
            "decision_lane": "BRIDGE_AND_INTERLANGUAGE_EXPERIMENT",
            "lane_rank": index,
            "target_id": item["bridge_id"],
            "target_label": item["bridge_name"],
            "language_tag_or_mode": item["scripts_or_modalities"],
            "territory_or_community": item["communities_potentially_served"],
            "evidence_status": f"EVIDENCE_GRADE_{item['evidence_grade']}",
            "recommendation_basis": item["current_evidence_disposition"],
            "priority_action": "Measure functional comprehension by community, script, educational stage, and genre; separately account for shared-source production reuse.",
            "publication_caveat": item["uncertainty_and_evidence_gap"],
            "source_ids": item["source_ids"],
            "source_urls": item["source_urls_or_dois"],
            "nonadditivity_rule": f"{item['unique_gain_rule']} {item['double_count_rule']}",
            "local_work_exclusion": "true",
        }
    )


lane_rows = [
    {
        "lane_order": "1",
        "decision_lane": "DIRECT_PERSON_COMPARABLE",
        "row_count": "100",
        "comparison_rule": "Ordered only within source-authorized compatible person-language measures under the published common model.",
        "allocation_use": "High-reach comparison and standardized compute-efficiency planning.",
        "prohibited_use": "Do not call it a complete world ranking; do not sum overlapping rows; do not infer target-specific scarcity from common priors.",
    },
    {
        "lane_order": "2",
        "decision_lane": "STAGE_OPPORTUNITY",
        "row_count": str(len(read_csv(STAGE))),
        "comparison_rule": "Ordered only among directly measured learner or sector opportunity cohorts.",
        "allocation_use": "Large stage-specific packages even when no whole-language denominator is comparable.",
        "prohibited_use": "Do not compare or add directly to whole-language person measures.",
    },
    {
        "lane_order": "3",
        "decision_lane": "MANDATORY_CONTEXT_AND_VALUE_OF_INFORMATION",
        "row_count": str(len(large_rows) + len(gap_rows)),
        "comparison_rule": "Visible evidence-acquisition and package-decision lane; sorting is not an unmet-need rank.",
        "allocation_use": "Prevent large or undermeasured populations from disappearing and target the evidence most likely to change allocation.",
        "prohibited_use": "Do not relabel exposure, policy, macro, or territorial ceilings as unique beneficiaries.",
    },
    {
        "lane_order": "4",
        "decision_lane": "STRUCTURAL_ACCESS_PORTFOLIO",
        "row_count": str(len(structural_rows) + len(displacement_rows) + len(bridge_rows)),
        "comparison_rule": "Signed-language, accessibility, displacement, and bridge interventions retain their own units and evidence grades.",
        "allocation_use": "Minimum-service, functional-access, host-specific continuity, and bounded bridge experiments.",
        "prohibited_use": "Do not use disability proxies as sign-language populations; do not award family-wide interlanguage reach; do not assign a displacement cohort to one language.",
    },
]

write_csv(OUT, rows, FIELDS)
lane_fields = ["lane_order", "decision_lane", "row_count", "comparison_rule", "allocation_use", "prohibited_use"]
write_csv(LANES_OUT, lane_rows, lane_fields)

written = read_csv(OUT)
lane_counts: dict[str, int] = {}
for row in written:
    lane_counts[row["decision_lane"]] = lane_counts.get(row["decision_lane"], 0) + 1

direct = [row for row in written if row["decision_lane"] == "DIRECT_PERSON_COMPARABLE"]
direct_ranks = sorted(int(row["lane_rank"]) for row in direct)
non_direct_synthetic_scores = [
    row["portfolio_row_id"]
    for row in written
    if row["decision_lane"] != "DIRECT_PERSON_COMPARABLE"
    and row["model_median_unmet_need_or_opportunity"]
    and row["decision_lane"] not in {"STAGE_OPPORTUNITY"}
]
hashes_valid = all(digest(row) == row["row_sha256"] for row in written)
checks = {
    "portfolio_ids_unique": len({row["portfolio_row_id"] for row in written}) == len(written),
    "row_hashes_valid": hashes_valid,
    "direct_top100_count": len(direct) == 100,
    "direct_ranks_exact_1_to_100": direct_ranks == list(range(1, 101)),
    "all_direct_rows_exclude_local_work": all(row["local_work_exclusion"].lower() == "true" for row in direct),
    "stage_rows_present": lane_counts.get("STAGE_OPPORTUNITY", 0) >= 2,
    "large_context_rows_present": lane_counts.get("MANDATORY_LARGE_CONTEXT_AND_VOI", 0) == len(large_rows),
    "sentinel_gap_rows_present": lane_counts.get("MANDATORY_SENTINEL_GAP_AND_VOI", 0) == len(gap_rows),
    "structural_rows_complete": lane_counts.get("STRUCTURAL_SIGNED_AND_ACCESSIBILITY", 0) == len(structural_rows),
    "displacement_rows_complete": lane_counts.get("DISPLACEMENT_HOST_SPECIFIC", 0) == len(displacement_rows),
    "bridge_rows_complete": lane_counts.get("BRIDGE_AND_INTERLANGUAGE_EXPERIMENT", 0) == len(bridge_rows),
    "no_nonstage_non_direct_model_score": not non_direct_synthetic_scores,
    "taiwan_overlap_warning_present": all(
        "source_declared_overlapping_language_response_universe" in row["nonadditivity_rule"]
        for row in direct
        if row["language_tag_or_mode"] in {"cmn-Hant-TW", "nan-Hant-TW", "hak-Hant-TW"}
    ),
}
status = "PASS" if all(checks.values()) else "FAIL"
payload = {
    "schema": "interlanguage/global-funding-portfolio/1.0.0",
    "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "status": status,
    "purpose": "Expose coequal allocation lanes without converting incompatible denominators into one global score.",
    "inputs": [file_id(path) for path in (TOP100, STAGE, LARGE, STRUCTURAL, DISPLACEMENT, BRIDGES, SENTINELS, OVERLAP, AUTHORIZATION)],
    "outputs": [file_id(OUT), file_id(LANES_OUT)],
    "row_count": len(written),
    "lane_counts": lane_counts,
    "checks": checks,
    "non_direct_synthetic_score_rows": non_direct_synthetic_scores,
    "interpretation": [
        "Only DIRECT_PERSON_COMPARABLE has a cross-language rank.",
        "Lane ranks outside the direct-person and stage-opportunity lanes are deterministic display orders, not comparable benefit scores.",
        "Prior or local production is excluded from every need, benefit, cost, rank, and recommendation field.",
        "Missing population evidence is represented by an empty field, never zero or a world-population prior.",
    ],
}
Q.mkdir(parents=True, exist_ok=True)
QA_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(payload, ensure_ascii=False, indent=2))
