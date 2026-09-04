#!/usr/bin/env python3
"""Build a bounded, source-traceable results pack for the global-access paper.

The pack is deliberately descriptive: it does not recompute scores, alter the
ranker, or treat model-conditional values as observed need.  It joins only the
current v3 ranking outputs, their QA receipt, and the bounded portfolio-overlap
register.  Output hashes are omitted from the output itself to avoid a
self-referential identity; the caller records the final hash in the durable
evidence log.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STRUCTURED = ROOT / "structured"
QA = ROOT / "qa"
REPORTS = ROOT / "agent_reports"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(name: str) -> tuple[Path, list[dict[str, str]]]:
    path = STRUCTURED / name
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return path, rows


def read_json(name: str) -> tuple[Path, dict[str, Any]]:
    path = QA / name
    with path.open("r", encoding="utf-8") as fh:
        return path, json.load(fh)


def as_number(value: str | None) -> float | None:
    if value in (None, "", "NA", "null"):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def compact_row(row: dict[str, str]) -> dict[str, Any]:
    """Keep fields needed for a human-facing results table and traceability."""
    numeric = {
        "population_low",
        "population_base",
        "population_high",
        "intrinsic_need_low",
        "intrinsic_need_model",
        "intrinsic_need_high",
        "l_m_need_p05",
        "l_m_need_median",
        "l_m_need_mean",
        "l_m_need_p95",
        "standard_compute_p50_fecu",
        "l_m_efficiency_median",
        "l_m_need_rank",
        "l_m_efficiency_rank",
        "l_m_need_top100_probability",
        "l_m_need_top10_probability",
    }
    wanted = [
        "decision_rank",
        "edition_target_id",
        "label",
        "language_tag",
        "script",
        "mode",
        "territory_community",
        "country_iso3",
        "population_basis_class",
        "order_lane",
        "population_low",
        "population_base",
        "population_high",
        "population_source_id",
        "population_definition",
        "population_reference_year",
        "population_confidence",
        "population_atom_id",
        "population_rank_eligible",
        "primary_order_eligible",
        "primary_order_class",
        "primary_order_exclusion_reason",
        "authorization_status",
        "authorization_tier",
        "source_lane",
        "source_record_id",
        "evidence_role",
        "target_row_sha256",
        "evidence_row_sha256",
        "source_evidence_row_sha256",
        "schooling_language_gap",
        "learning_completion_gap",
        "open_resource_scarcity",
        "academic_lingua_franca_nonoverlap",
        "delivery_gap",
        "accessibility_gap",
        "intrinsic_need_low",
        "intrinsic_need_model",
        "intrinsic_need_high",
        "l_m_need_p05",
        "l_m_need_median",
        "l_m_need_mean",
        "l_m_need_p95",
        "standard_compute_p50_fecu",
        "compute_evidence_class",
        "need_evidence_basis",
        "vitality_marginalization_status",
        "dialect_risk_status",
        "production_feasibility_status",
        "model_conditioning_status",
        "synthetic_or_model_prior",
    ]
    out: dict[str, Any] = {}
    for key in wanted:
        value = row.get(key, "")
        out[key] = as_number(value) if key in numeric else value
    return out


def source_identity(path: Path, rows: int | None = None) -> dict[str, Any]:
    item = {"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256(path)}
    if rows is not None:
        item["rows"] = rows
    return item


def main() -> None:
    score_path, score_rows = read_csv("GLOBAL_TARGET_SCORE_TABLE_v3.csv")
    top10_path, top10_rows = read_csv("TOP10_NEEDS_ONLY_v3.csv")
    top100_path, top100_rows = read_csv("TOP100_NEEDS_ONLY_v3.csv")
    stage10_path, stage10_rows = read_csv("TOP10_STAGE_OPPORTUNITY_v3.csv")
    stage100_path, stage100_rows = read_csv("TOP100_STAGE_OPPORTUNITY_v3.csv")
    overlap_path, overlap_rows = read_csv("PORTFOLIO_OVERLAP_REGISTER_v1.csv")
    qa_path, qa = read_json("GLOBAL_ACCESS_RANKINGS_V3_QA.json")
    overlap_qa_path, overlap_qa = read_json("PORTFOLIO_OVERLAP_AUDIT_v1.json")

    # Structural checks are intentionally strict and deterministic.
    top10_ranks = [int(r["decision_rank"]) for r in top10_rows]
    top100_ranks = [int(r["decision_rank"]) for r in top100_rows]
    assert top10_ranks == list(range(1, 11)), top10_ranks
    assert top100_ranks == list(range(1, 101)), (top100_ranks[:3], top100_ranks[-3:])
    assert [r["edition_target_id"] for r in top10_rows] == [r["edition_target_id"] for r in top100_rows[:10]]
    assert len({r["edition_target_id"] for r in score_rows}) == len(score_rows)
    assert qa["status"] == "PASS"
    assert qa["target_set_checks"]["needs_top100_exact_prefix"] is True

    by_country = Counter((r.get("country_iso3") or "UNSPECIFIED") for r in top100_rows)
    by_lane = Counter((r.get("order_lane") or "UNSPECIFIED") for r in top100_rows)
    by_basis = Counter((r.get("population_basis_class") or "UNSPECIFIED") for r in top100_rows)
    by_source_lane = Counter((r.get("source_lane") or "UNSPECIFIED") for r in top100_rows)
    overlap_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in overlap_rows:
        overlap_groups[row.get("overlap_group", "UNSPECIFIED")].append(row)

    required_labels = {}
    for row in score_rows:
        label = row.get("label", "")
        if label in {"Bahasa Indonesia", "Mainland Simplified Chinese", "Japan", "Japanese"} or row.get("language_tag") in {"id-Latn-ID", "zh-Hans-CN", "ja-Jpan-JP"}:
            required_labels.setdefault(label or row.get("language_tag", ""), compact_row(row))

    pack: dict[str, Any] = {
        "schema": "interlanguage/paper-results-evidence-pack/1.0.0",
        "status": "PROVISIONAL_MODEL_CONDITIONAL_RESULTS",
        "created_from": "current v3 source-authorized ranking snapshot",
        "scope": {
            "score_rows": len(score_rows),
            "needs_top10_rows": len(top10_rows),
            "needs_top100_rows": len(top100_rows),
            "stage_top10_rows": len(stage10_rows),
            "stage_top100_rows": len(stage100_rows),
            "portfolio_overlap_rows": len(overlap_rows),
            "portfolio_overlap_groups": len(overlap_groups),
        },
        "qa_summary": {
            "ranker_status": qa.get("status"),
            "target_count": qa.get("target_count"),
            "person_need_target_count": qa.get("person_need_target_count"),
            "stage_opportunity_target_count": qa.get("stage_opportunity_target_count"),
            "unranked_target_count": qa.get("unranked_target_count"),
            "primary_order_eligible_count": qa.get("primary_order_eligible_count"),
            "unranked_no_source_bound_person_denominator_count": qa.get("unranked_no_source_bound_person_denominator_count"),
            "required_large_cohort_presence": qa.get("required_large_cohort_presence"),
            "cost_source": qa.get("cost_source"),
            "draws_per_target": qa.get("draws_per_target"),
            "weights": qa.get("weights"),
        },
        "top10_needs_only": [compact_row(r) for r in top10_rows],
        "top100_needs_only": [compact_row(r) for r in top100_rows],
        "stage_opportunity": {
            "top10": [compact_row(r) for r in stage10_rows],
            "top100": [compact_row(r) for r in stage100_rows],
        },
        "portfolio_overlap": {
            "groups": {k: v for k, v in sorted(overlap_groups.items())},
            "qa": overlap_qa,
            "interpretation": "Rows with probable shared denominators are distinct edition interventions but are non-additive for a portfolio total until a disjoint person crosswalk is proved. The repeated-base warning is not a unique-person estimate.",
        },
        "top100_descriptive_breakdowns": {
            "country_iso3": dict(sorted(by_country.items())),
            "order_lane": dict(sorted(by_lane.items())),
            "population_basis_class": dict(sorted(by_basis.items())),
            "source_lane": dict(sorted(by_source_lane.items())),
        },
        "required_profiles_in_score_table": required_labels,
        "interpretation_rules": [
            "The order is a model-conditional common-prior order, not an observed global ranking.",
            "Population values are source-bound only where the row says so; unresolved exact-shaped rows remain visible but unranked.",
            "Standardized compute is a script-envelope fallback, not measured end-to-end translation cost.",
            "Standalone Top-100 ranks must not be summed across probable overlap groups.",
            "No local production, prior translation completion, sunk compute, or project convenience enters the model.",
            "Stage-opportunity rows are reported separately from the needs-only person order.",
        ],
        "source_artifacts": [
            source_identity(score_path, len(score_rows)),
            source_identity(top10_path, len(top10_rows)),
            source_identity(top100_path, len(top100_rows)),
            source_identity(stage10_path, len(stage10_rows)),
            source_identity(stage100_path, len(stage100_rows)),
            source_identity(overlap_path, len(overlap_rows)),
            source_identity(qa_path),
            source_identity(overlap_qa_path),
        ],
    }

    out_json = STRUCTURED / "PAPER_RESULTS_EVIDENCE_PACK_v1.json"
    out_md = REPORTS / "PAPER_RESULTS_EVIDENCE_PACK_v1.md"
    out_json.write_text(json.dumps(pack, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    top_lines = [
        "# Paper results evidence pack (v1)",
        "",
        "This bounded pack is generated from the current v3 ranking outputs. It is a provisional, model-conditional results table; it is not a claim that the order is an observed global need ranking.",
        "",
        f"- Score rows: {len(score_rows)}; needs-only Top 10/100: {len(top10_rows)}/{len(top100_rows)}; stage rows: {len(stage10_rows)}/{len(stage100_rows)}.",
        f"- Ranker QA: `{qa.get('status')}`; person targets: {qa.get('person_need_target_count')}; stage targets: {qa.get('stage_opportunity_target_count')}; unranked/context targets: {qa.get('unranked_target_count')}.",
        f"- Portfolio overlap register: {len(overlap_rows)} rows in {len(overlap_groups)} probable groups; repeated-base warning: {overlap_qa.get('potentially_repeated_base_persons_upper_warning')} (not a unique-person estimate).",
        "",
        "## Current needs-only Top 10",
        "",
        "| Rank | Target | Language tag | Population base | Intrinsic model | Compute p50 |",
        "|---:|---|---|---:|---:|---:|",
    ]
    for row in top10_rows:
        top_lines.append(
            f"| {row['decision_rank']} | {row['label']} | `{row['language_tag']}` | {row['population_base']} | {row['intrinsic_need_model']} | {row['standard_compute_p50_fecu']} |"
        )
    top_lines += [
        "",
        "The machine-readable JSON contains all 100 rows, source identities, stage opportunities, required-profile rows, and the overlap register.",
        "",
        "## Caveat",
        "",
        "This pack does not convert model priors into measured need, does not add overlapping denominators, and does not treat a missing source-bound denominator as zero need. It is an intermediate evidence artifact for paper integration and further independent audit.",
        "",
    ]
    out_md.write_text("\n".join(top_lines), encoding="utf-8")
    print(json.dumps({
        "json": str(out_json),
        "json_bytes": out_json.stat().st_size,
        "json_sha256": sha256(out_json),
        "markdown": str(out_md),
        "markdown_bytes": out_md.stat().st_size,
        "markdown_sha256": sha256(out_md),
        "top10_rows": len(top10_rows),
        "top100_rows": len(top100_rows),
        "overlap_groups": len(overlap_groups),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
