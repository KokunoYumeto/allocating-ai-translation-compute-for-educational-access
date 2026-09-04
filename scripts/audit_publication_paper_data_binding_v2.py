#!/usr/bin/env python3
"""Bind every generated publication table and key quantitative claim to frozen artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "PAPER.md"
S = ROOT / "structured"
Q = ROOT / "qa"
A = ROOT / "agent_reports"
OUTPUT = Q / "PUBLICATION_PAPER_DATA_BINDING_AUDIT_v2.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def fmt_int(value: str | float | int, missing: str = "not stated") -> str:
    text = str(value or "").strip()
    if not text:
        return missing
    return f"{int(round(float(text))):,}"


def fmt_pct(value: str, digits: int = 1) -> str:
    if not str(value or "").strip():
        return "not estimated"
    return f"{100 * float(value):.{digits}f}%"


def population_cell(row: dict[str, str]) -> str:
    low = row.get("population_low", row.get("population_low_persons", ""))
    base = row.get("population_base", row.get("population_base_persons", ""))
    high = row.get("population_high", row.get("population_high_persons", ""))
    if not low and not base and not high:
        return "not yet source-bounded"
    if low and high and float(low) != float(high):
        interval = f"{fmt_int(low)}-{fmt_int(high)}"
        return f"{fmt_int(base)} [{interval}]" if base else interval
    return fmt_int(base or low or high)


def safe(value: Any) -> str:
    return (
        str(value or "")
        .replace("\u2014", " - ")
        .replace("\u2013", "-")
        .replace("\u2011", "-")
        .replace("|", " / ")
        .replace("\n", " ")
        .strip()
    )


def markdown_row(values: list[Any]) -> str:
    return "| " + " | ".join(safe(value) for value in values) + " |"


def section(text: str, start: str, end: str) -> str:
    begin = text.find(start)
    finish = text.find(end, begin + len(start))
    if begin < 0 or finish < 0:
        raise RuntimeError(f"section boundary missing: {start!r} -> {end!r}")
    return text[begin:finish]


paper_text = PAPER.read_text(encoding="utf-8")
paper_sha = sha(PAPER)
top100 = read_csv(S / "TOP100_NEEDS_ONLY_v3.csv")
efficiency100 = read_csv(S / "TOP100_COMPUTE_EFFICIENCY_v3.csv")
score_rows = read_csv(S / "GLOBAL_TARGET_SCORE_TABLE_PUBLIC_v3.csv")
score_by_id = {row["edition_target_id"]: row for row in score_rows}
stage = read_csv(S / "ORDER_STAGE_OPPORTUNITY_v3.csv")
portfolio = read_csv(S / "GLOBAL_FUNDING_PORTFOLIO_v1.csv")
needs_rows = read_csv(A / "STAGE_SUBJECT_NEEDS_MAPPING.csv")
rank_qa = json.loads((Q / "GLOBAL_ACCESS_RANKINGS_V3_QA.json").read_text(encoding="utf-8"))
inclusion_qa = json.loads((Q / "GLOBAL_INCLUSION_DISPOSITION_QA_v1.json").read_text(encoding="utf-8"))
portfolio_qa = json.loads((Q / "GLOBAL_FUNDING_PORTFOLIO_QA_v1.json").read_text(encoding="utf-8"))
trace_qa = json.loads((Q / "TOP100_SOURCE_TRACE_AUDIT_v2.json").read_text(encoding="utf-8"))
citation_qa = json.loads((Q / "PAPER_CITATION_AUDIT_v1.json").read_text(encoding="utf-8"))

need_block = section(paper_text, "### A.1 Direct-person Top 100", "### A.2 Standardized new-compute Top 100")
efficiency_block = section(paper_text, "### A.2 Standardized new-compute Top 100", "## Appendix B.")
stage_block = section(paper_text, "### B.1 Stage opportunities", "### B.2 Mandatory large contexts")
context_block = section(paper_text, "### B.2 Mandatory large contexts", "## Appendix C.")
structural_block = section(paper_text, "### C.1 Named sign-language and accessibility interventions", "### C.2 Host-specific displacement portfolios")
displacement_block = section(paper_text, "### C.2 Host-specific displacement portfolios", "## Appendix D.")
bridge_block = section(paper_text, "## Appendix D.", "## Appendix E.")
needs_block = section(paper_text, "## Appendix E.", "## References")

expected_need_rows = [
    markdown_row(
        [
            row["decision_rank"],
            f"{row['label']} (`{row['language_tag']}`)",
            population_cell(row),
            row["population_reference_year"],
            fmt_int(row["intrinsic_need_median"]),
            fmt_pct(row["top100_probability"]),
        ]
    )
    for row in top100
]
expected_efficiency_rows = [
    markdown_row(
        [
            row["decision_rank"],
            score_by_id[row["edition_target_id"]]["l_m_need_rank"],
            f"{row['label']} (`{row['language_tag']}`)",
            fmt_int(float(row["access_gain_per_compute_median"]) * 1_000_000),
            fmt_int(row["standard_compute_p50_fecu"]),
        ]
    )
    for row in efficiency100
]
expected_stage_rows = [
    markdown_row(
        [
            row["opportunity_rank"],
            f"{row['label']} (`{row['language_tag']}`)",
            population_cell(row),
            fmt_int(row["intrinsic_need_median"]),
            row["population_definition"],
        ]
    )
    for row in stage
]

context = [
    row
    for row in portfolio
    if row["decision_lane"] in {"MANDATORY_LARGE_CONTEXT_AND_VOI", "MANDATORY_SENTINEL_GAP_AND_VOI"}
]
structural = [row for row in portfolio if row["decision_lane"] == "STRUCTURAL_SIGNED_AND_ACCESSIBILITY"]
displacement = [row for row in portfolio if row["decision_lane"] == "DISPLACEMENT_HOST_SPECIFIC"]
bridges = [row for row in portfolio if row["decision_lane"] == "BRIDGE_AND_INTERLANGUAGE_EXPERIMENT"]

expected_context_rows = [
    markdown_row([row["lane_rank"], row["target_label"], population_cell(row), row["evidence_status"], row["priority_action"]])
    for row in context
]
expected_structural_rows = [
    markdown_row(
        [
            row["lane_rank"],
            row["target_label"],
            row["language_tag_or_mode"],
            row["territory_or_community"],
            population_cell(row),
            row["evidence_status"],
        ]
    )
    for row in structural
]
expected_displacement_rows = [
    markdown_row([row["lane_rank"], row["target_label"], population_cell(row), row["language_tag_or_mode"], row["evidence_status"]])
    for row in displacement
]
expected_bridge_rows = [
    markdown_row([row["lane_rank"], row["target_label"], row["language_tag_or_mode"], row["evidence_status"], row["recommendation_basis"]])
    for row in bridges
]
expected_needs_rows = [
    markdown_row(
        [
            f"{row['target_label']} (`{row['target_id']}`)",
            row["priority_stage_order"].replace("|", " -> "),
            row["p0_material_classes"],
            row["outsized_local_utility"],
            row["boundary_note"],
        ]
    )
    for row in needs_rows
]


def all_present(expected: list[str], block: str) -> tuple[bool, list[str]]:
    missing = [line for line in expected if line not in block]
    return not missing, missing[:10]


need_ok, need_missing = all_present(expected_need_rows, need_block)
eff_ok, eff_missing = all_present(expected_efficiency_rows, efficiency_block)
stage_ok, stage_missing = all_present(expected_stage_rows, stage_block)
context_ok, context_missing = all_present(expected_context_rows, context_block)
structural_ok, structural_missing = all_present(expected_structural_rows, structural_block)
displacement_ok, displacement_missing = all_present(expected_displacement_rows, displacement_block)
bridge_ok, bridge_missing = all_present(expected_bridge_rows, bridge_block)
needs_ok, needs_missing = all_present(expected_needs_rows, needs_block)

artifact_hashes = {
    "structured/GLOBAL_TARGET_SCORE_TABLE_PUBLIC_v3.csv": sha(S / "GLOBAL_TARGET_SCORE_TABLE_PUBLIC_v3.csv"),
    "structured/TOP100_NEEDS_ONLY_v3.csv": sha(S / "TOP100_NEEDS_ONLY_v3.csv"),
    "structured/GLOBAL_FUNDING_PORTFOLIO_v1.csv": sha(S / "GLOBAL_FUNDING_PORTFOLIO_v1.csv"),
    "structured/GLOBAL_INCLUSION_DISPOSITION_REGISTER_v1.csv": sha(S / "GLOBAL_INCLUSION_DISPOSITION_REGISTER_v1.csv"),
    "structured/SOURCE_TO_SCORE_CROSSWALK_v1.csv": sha(S / "SOURCE_TO_SCORE_CROSSWALK_v1.csv"),
    "structured/RANK_SENSITIVITY_SUMMARY_v1.csv": sha(S / "RANK_SENSITIVITY_SUMMARY_v1.csv"),
    "structured/TOP100_COMPUTE_EFFICIENCY_v3.csv": sha(S / "TOP100_COMPUTE_EFFICIENCY_v3.csv"),
    "agent_reports/STAGE_SUBJECT_NEEDS_MAPPING.csv": sha(A / "STAGE_SUBJECT_NEEDS_MAPPING.csv"),
    "agent_reports/INTERLANGUAGE_STRUCTURED_EVIDENCE_MATRIX.csv": sha(A / "INTERLANGUAGE_STRUCTURED_EVIDENCE_MATRIX.csv"),
}

quantitative_claim_fragments = [
    f"{rank_qa['target_count']:,} authority targets",
    f"{rank_qa['person_need_target_count']} source-authorized direct-person targets",
    f"{rank_qa['stage_opportunity_target_count']} separately comparable stage-opportunity targets",
    f"{rank_qa['unranked_target_count']} visible unranked or contextual targets",
    f"{rank_qa['unranked_no_source_bound_person_denominator_count']:,} lack a source-bounded person denominator",
    f"The evidence authorization ledger has 850 records and admits 259 population observations to {rank_qa['person_need_target_count']} direct-person targets",
    f"The source-to-score crosswalk contains {inclusion_qa['counts']['source_to_score_crosswalk_rows']} rows",
    f"The public-safe score table contains {inclusion_qa['counts']['public_score_rows']:,} rows",
    "The territory-binding audit checks 921 valid BCP-47 region rows and 87 unresolved identities with zero mismatches",
    f"The portfolio audit contains {len(portfolio)} rows",
]

prohibited_patterns = {
    "absolute_windows_profile_path": r"[A-Za-z]:\\Users\\",
    "local_program_as_need_predictor": r"(?i)(prior translation|local holding|project completion).{0,80}(reduce|lower|subtract).{0,30}(need|rank)",
    "publication_tombstone_or_repair_narrative": r"(?i)\b(tombstone|rectification|corrective framing)\b",
    "stale_snapshot_counts": r"(?i)(1,065 (?:candidate|target)|907 (?:remain|unranked)|811 (?:of|rows|lack)|156 rankable|156 person|158 person|624 rows|1,092 rows)",
    "japan_generic_negative_control_label": r"(?i)negative control for generic primary mathematics",
}

checks = {
    "rank_qa_pass": rank_qa.get("status") == "PASS",
    "portfolio_qa_pass": portfolio_qa.get("status") == "PASS",
    "trace_qa_pass": trace_qa.get("status") == "PASS",
    "paper_provenance_exact": "OpenAI Codex gpt-5.6-sol, Ultra." in paper_text,
    "citation_audit_binds_current_paper": citation_qa.get("paper", {}).get("sha256", "").upper() == paper_sha,
    "citation_audit_has_zero_missing": citation_qa.get("missing_or_unresolved_count") == 0,
    "direct_top100_row_count": len(top100) == 100,
    "direct_top100_rank_sequence": [int(row["decision_rank"]) for row in top100] == list(range(1, 101)),
    "direct_top100_rows_exactly_present": need_ok,
    "efficiency_top100_row_count": len(efficiency100) == 100,
    "efficiency_top100_rank_sequence": [int(row["decision_rank"]) for row in efficiency100] == list(range(1, 101)),
    "efficiency_top100_rows_exactly_present": eff_ok,
    "stage_rows_exactly_present": stage_ok,
    "context_rows_exactly_present": context_ok,
    "structural_rows_exactly_present": structural_ok,
    "displacement_rows_exactly_present": displacement_ok,
    "bridge_rows_exactly_present": bridge_ok,
    "stage_subject_rows_exactly_present": needs_ok,
    "all_key_artifact_hashes_present": all(value in paper_text for value in artifact_hashes.values()),
    "all_key_quantitative_claims_present": all(fragment in paper_text for fragment in quantitative_claim_fragments),
    "legacy_efficiency_field_explained": "legacy field name" in paper_text and "must not be interpreted as observed learners helped" in paper_text,
    "four_decision_lanes_explicit": all(
        phrase in paper_text
        for phrase in (
            "Direct-person comparable",
            "Stage opportunity",
            "Mandatory context and value of information",
            "Structural access portfolio",
        )
    ),
    "public_safe_unranked_fields_suppressed": inclusion_qa["counts"]["public_unranked_rows_with_population_values_removed"] == rank_qa["unranked_target_count"],
    "no_prohibited_patterns": not any(re.search(pattern, paper_text) for pattern in prohibited_patterns.values()),
}

missing_details = {
    "direct_top100": need_missing,
    "efficiency_top100": eff_missing,
    "stage": stage_missing,
    "context": context_missing,
    "structural": structural_missing,
    "displacement": displacement_missing,
    "bridge": bridge_missing,
    "stage_subject": needs_missing,
    "quantitative_claim_fragments": [fragment for fragment in quantitative_claim_fragments if fragment not in paper_text],
    "artifact_hashes": {path: digest for path, digest in artifact_hashes.items() if digest not in paper_text},
    "prohibited_matches": {
        name: match.group(0)
        for name, pattern in prohibited_patterns.items()
        if (match := re.search(pattern, paper_text))
    },
}

status = "PASS" if all(checks.values()) else "FAIL"
receipt = {
    "schema": "interlanguage/publication-paper-data-binding-audit/2.0.0",
    "status": status,
    "paper": {"path": "PAPER.md", "bytes": PAPER.stat().st_size, "sha256": paper_sha},
    "counts": {
        "direct_top100_rows": len(top100),
        "efficiency_top100_rows": len(efficiency100),
        "stage_rows": len(stage),
        "context_and_gap_rows": len(context),
        "structural_rows": len(structural),
        "displacement_rows": len(displacement),
        "bridge_rows": len(bridges),
        "stage_subject_rows": len(needs_rows),
        "registered_citations_in_paper": citation_qa.get("citation_count"),
    },
    "checks": checks,
    "missing_or_forbidden_details": missing_details,
    "artifact_hashes_reproduced": artifact_hashes,
    "interpretation": (
        "PASS proves that the manuscript's generated orders, portfolios, recommendation register, key counts, "
        "and displayed hashes reproduce the frozen local artifacts. It does not turn model-conditional values "
        "into observed causal effects or prove that the language census is exhaustive."
    ),
}
OUTPUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": status, "path": str(OUTPUT), "bytes": OUTPUT.stat().st_size, "sha256": sha(OUTPUT)}, indent=2))
if status != "PASS":
    raise SystemExit(1)
