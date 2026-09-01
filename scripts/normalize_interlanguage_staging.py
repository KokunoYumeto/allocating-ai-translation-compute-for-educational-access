"""Normalize the independently authored interlanguage staging package.

This script resolves identifier/taxonomy mismatches and prevents study samples,
hypothetical surfaces, unresolved profiles, and a short-cloze score from
entering the demographic ranking model as if they were population evidence.
It does not perform population joins or assign comprehension probabilities.
"""

from __future__ import annotations

import csv
import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parent.parent
STAGE = ROOT / "staging" / "interlanguage_matrix"
CANDIDATE_IN = STAGE / "candidate_interventions_agent.csv"
OVERLAP_IN = STAGE / "interlanguage_overlap_agent.csv"
CANDIDATE_OUT = STAGE / "candidate_interventions_normalized.csv"
OVERLAP_OUT = STAGE / "interlanguage_overlap_normalized.csv"

ID_MAP = {
    "IL-001": "IL-ISV",
    "IL-002": "IL-ROM",
    "IL-003": "IL-TURKIC",
    "IL-004": "IL-GERM",
    "IL-005": "IL-IDMS",
    "IL-006": "IL-SCAND",
    "IL-007": "IL-AR",
    "IL-008": "IL-PDT",
    "IL-009": "IL-BCMS",
    "IL-010": "IL-HU",
    "IL-011": "IL-PUNJABI",
    "IL-012": "IL-NGUNI",
    "IL-013": "IL-SOTHO",
    "IL-014": "IL-MANDING",
    "IL-015": "IL-SQUECHUA",
}

# Profiles whose authored row itself says the exact variety, standard, script,
# or territory is unresolved.  They remain useful discovery candidates but are
# not scoreable until an exact population cell is supplied.
DISCOVERY_ONLY = {
    "NAT-016",
    "NAT-017",
    "NAT-020",
    "NAT-025",
    "NAT-043",
    "NAT-052",
    "NAT-059",
    "NAT-066",
    "NAT-068",
    "NAT-071",
    "NAT-084",
    "NAT-096",
    "NAT-098",
    "NAT-101",
    "NAT-104",
    "NAT-116",
    "NAT-118",
    "NAT-120",
}

NON_POPULATION_ROWS = {
    "CELL-ISV-STUDY-POOL": "study_sample",
    "CELL-ROM-CONSTRUCTED-HYP": "hypothetical_surface",
}

MECHANISM_MAP = {
    "constructed_bridge": "constructed_bridge",
    "pluricentric_shared_core": "pluricentric_reuse",
    "natural_intercomprehension_reuse": "natural_intercomprehension_reuse",
    "dual_script_register": "dual_script_or_register",
}


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: pathlib.Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def normalize_candidates() -> list[dict[str, str]]:
    rows = read_csv(CANDIDATE_IN)
    fields = list(rows[0]) + ["rankability_status"]
    normalized = []
    for row in rows:
        row = dict(row)
        original_id = row["intervention_id"]
        row["intervention_id"] = ID_MAP.get(original_id, original_id)
        # The independently authored staging return captured the Indonesian
        # Open Logic program at OLP-0321.  That is historical provenance, not
        # current coverage: the exact public closure is now 722/722.  Keep the
        # raw staging CSV untouched and apply the source-audited successor
        # state here so every regenerated master/companion inherits it.
        if row["intervention_id"] == "IL-IDMS":
            row["existing_local_status"] = (
                "Indonesian Open Logic 722 of 722 complete; "
                "Malaysian Malay unstarted"
            )
            current_status_source = "CURRENT_INDONESIAN_PROGRAM_STATUS_20260830"
            source_ids = [item for item in row.get("source_ids", "").split(";") if item]
            if current_status_source not in source_ids:
                source_ids.append(current_status_source)
            row["source_ids"] = ";".join(source_ids)
        if original_id in DISCOVERY_ONLY or row["adaptation_depth"] == "D0":
            row["rankability_status"] = "discovery_only_target_resolution_required"
        elif row["target_type"] in {"accessibility", "signed_language_access"}:
            row["rankability_status"] = "requires_exact_population_stratum_join"
        else:
            row["rankability_status"] = "requires_exact_population_join"
        normalized.append(row)
    write_csv(CANDIDATE_OUT, fields, normalized)
    return normalized


def normalize_overlap() -> list[dict[str, str]]:
    source_rows = read_csv(OVERLAP_IN)
    fields = [
        "edge_id",
        "intervention_id",
        "mechanism",
        "staging_profile_id",
        "population_cell_id",
        "population_join_status",
        "edge_role",
        "community_label",
        "territory",
        "language_tag",
        "script",
        "coverage_mode",
        "comprehension_low",
        "comprehension_base",
        "comprehension_high",
        "observed_task_score",
        "observed_task_type",
        "prior_study_required",
        "receptive_or_productive",
        "tested_task",
        "script_match",
        "existing_edition_overlap",
        "exclusions",
        "double_count_rule",
        "recommended_portfolio",
        "adaptation_depth",
        "source_ids",
        "source_locator",
        "confidence",
        "inference_flag",
        "rankable",
        "notes",
    ]
    normalized = []
    for source in source_rows:
        profile = source["population_cell_id"]
        edge_role = NON_POPULATION_ROWS.get(profile, "coverage_candidate")
        non_population = profile in NON_POPULATION_ROWS
        observed_score = ""
        observed_type = ""
        comprehension_base = source["comprehension_base"]
        if source["edge_id"] == "EDGE-ISV-000":
            observed_score = comprehension_base
            observed_type = "seven-gap short written professional-text cloze"
            comprehension_base = "unknown"
        row = {
            "edge_id": source["edge_id"],
            "intervention_id": source["interlanguage_id"],
            "mechanism": MECHANISM_MAP.get(source["mechanism"], source["mechanism"]),
            "staging_profile_id": profile,
            "population_cell_id": "",
            "population_join_status": (
                "non_population_evidence" if non_population else "pending_exact_composite_join"
            ),
            "edge_role": edge_role,
            "community_label": source["community_label"],
            "territory": source["territory"],
            "language_tag": source["language_tag"],
            "script": source["script"],
            "coverage_mode": source["coverage_mode"],
            "comprehension_low": source["comprehension_low"],
            "comprehension_base": comprehension_base,
            "comprehension_high": source["comprehension_high"],
            "observed_task_score": observed_score,
            "observed_task_type": observed_type,
            "prior_study_required": source["prior_study_required"],
            "receptive_or_productive": source["receptive_or_productive"],
            "tested_task": source["tested_task"],
            "script_match": source["script_match"],
            "existing_edition_overlap": source["existing_edition_overlap"],
            "exclusions": source["explicit_exclusions"],
            "double_count_rule": source["double_count_rule"],
            "recommended_portfolio": source["recommended_portfolio"],
            "adaptation_depth": source["adaptation_depth"],
            "source_ids": source["source_ids"],
            "source_locator": source["source_locator"],
            "confidence": source["confidence"],
            "inference_flag": source["inference_flag"],
            "rankable": "false",
            "notes": source["notes"],
        }
        if row["edge_id"] == "EDGE-IDMS-001":
            row["existing_edition_overlap"] = (
                "Indonesian Open Logic 722 of 722 complete; "
                "Malaysian Malay exact edition unstarted"
            )
            current_status_source = "CURRENT_INDONESIAN_PROGRAM_STATUS_20260830"
            source_ids = [item for item in row["source_ids"].split(";") if item]
            if current_status_source not in source_ids:
                source_ids.append(current_status_source)
            row["source_ids"] = ";".join(source_ids)
        normalized.append(row)
    write_csv(OVERLAP_OUT, fields, normalized)
    return normalized


def main() -> None:
    candidates = normalize_candidates()
    overlap = normalize_overlap()
    candidate_ids = [row["intervention_id"] for row in candidates]
    edge_ids = [row["edge_id"] for row in overlap]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("Duplicate intervention IDs after normalization")
    if len(edge_ids) != len(set(edge_ids)):
        raise ValueError("Duplicate edge IDs after normalization")
    if set(ID_MAP.values()) != {
        row["intervention_id"]
        for row in candidates
        if row["target_type"] not in {"natural_language", "accessibility", "signed_language_access"}
    }:
        raise ValueError("Normalized interlanguage candidate IDs do not match the registered set")
    if any(row["population_cell_id"] for row in overlap):
        raise ValueError("Population joins must remain blank during normalization")
    print(
        json.dumps(
            {
                "candidate_rows": len(candidates),
                "candidate_ids_unique": True,
                "discovery_only": sum(
                    row["rankability_status"].startswith("discovery_only")
                    for row in candidates
                ),
                "overlap_rows": len(overlap),
                "edge_ids_unique": True,
                "non_population_evidence_rows": sum(
                    row["population_join_status"] == "non_population_evidence"
                    for row in overlap
                ),
                "numeric_comprehension_cells": sum(
                    value not in {"", "unknown"}
                    for row in overlap
                    for value in (
                        row["comprehension_low"],
                        row["comprehension_base"],
                        row["comprehension_high"],
                    )
                ),
                "observed_task_scores": sum(bool(row["observed_task_score"]) for row in overlap),
            }
        )
    )


if __name__ == "__main__":
    main()
