#!/usr/bin/env python3
"""Replace the human-facing provisional ranking section from current tables.

This is deliberately a small, deterministic projection: it reads only the
current ranker outputs and writes the section between the two stable paper
headings.  It never changes the underlying scores or source evidence.
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "PAPER.md"
TOP10 = ROOT / "structured/TOP10_NEEDS_ONLY_v3.csv"
TOP100 = ROOT / "structured/TOP100_NEEDS_ONLY_v3.csv"
STAGE = ROOT / "structured/TOP100_STAGE_OPPORTUNITY_v3.csv"
QA = ROOT / "qa/GLOBAL_ACCESS_RANKINGS_V3_QA.json"
TRACE_QA = ROOT / "qa/TOP100_SOURCE_TRACE_AUDIT_v2.json"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as h:
        return list(csv.DictReader(h))


def n(value: str) -> str:
    try:
        return f"{float(value):,.0f}"
    except (TypeError, ValueError):
        return value or "unknown"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_section() -> str:
    top10 = rows(TOP10)
    top100 = rows(TOP100)
    stage = rows(STAGE) if STAGE.is_file() else []
    lines = [
        "### 6.1 Provisional needs-only order (current source-authorized snapshot)",
        "",
        f"The current deterministic run contains {len(top100)} needs-only rows in the published Top 100 projection and {len(top10)} displayed Top-10 rows. These are model-conditional results, not observed global rankings: the population inputs are source-bound points or explicit intervals; missing need factors use one common prior; and the compute denominator is reported separately as a standardized script-envelope assumption unless a measured target cost exists. The OER sweep now converts a cell grade to a numeric scarcity factor only when every controlled cell for a target is `RESOURCE_FOUND`; unresolved cells remain missing and use the common prior. Current ranker QA is recorded in `qa/GLOBAL_ACCESS_RANKINGS_V3_QA.json` (SHA-256 `{sha(QA)}`). The independent source-trace audit is recorded in `qa/TOP100_SOURCE_TRACE_AUDIT_v2.json` (SHA-256 `{sha(TRACE_QA)}`) when present.",
        "",
        "| Rank | Exact intervention target | Language tag | Source-bound base population | Model median unmet-need | Standard compute p50 (FECU) |",
        "|---:|---|---|---:|---:|---:|",
    ]
    for r in top10:
        lines.append(
            f"| {r.get('decision_rank','')} | {r.get('label','')} | `{r.get('language_tag','')}` | {n(r.get('population_base',''))} | {n(r.get('intrinsic_need_median',''))} | {n(r.get('standard_compute_p50_fecu',''))} |"
        )
    lines += [
        "",
        "The table is a reproducible display projection; retain the low/base/high fields, factor bases, source IDs, and uncertainty fields in the machine-readable tables. A source point estimate with blank source endpoints is not an uncertainty interval. The authorization layer preserves that distinction; downstream arithmetic may use a degenerate point representation only for the point estimand.",
        "",
        f"The current needs-only Top 100 contains {sum(1 for r in top100 if r.get('authorization_tier') == 'A_DIRECT_TYPED_PERSON')} direct typed person rows, {sum(1 for r in top100 if r.get('authorization_tier') in {'A_REGIONAL_EXACT_TYPED_PERSON', 'B_REGIONAL_ESTIMATE', 'B_REGIONAL_INTERVAL_TYPED_PERSON'})} regional typed person rows, and {sum(1 for r in top100 if r.get('population_bound_type') == 'INTERVAL')} explicit interval rows. Regional point rows retain null low/high in their source bundles; they are not presented as measured confidence bounds. Non-degenerate source ranges are labelled interval-only and retain their raw endpoints; point rows with blank source endpoints use normalized endpoints only inside the arithmetic adapter.",
        "",
        "Population rows that share a person denominator or aggregate a macro language are not additive. The portfolio register and conservative union/intersection bounds therefore remain separate from standalone rank order; no shared-population correction is hidden in the table.",
        "",
    ]
    if stage:
        lines += [
            "Mainland Standard Written Chinese and Japanese remain visible in a separate stage-opportunity lane. Stage rows are not mixed into the person Top 100:",
            "",
            "| Stage rank | Exact opportunity target | Language tag | Opportunity base | Model median unmet-need |",
            "|---:|---|---|---:|---:|",
        ]
        for r in stage[:10]:
            lines.append(
                f"| {r.get('opportunity_rank', r.get('decision_rank',''))} | {r.get('label','')} | `{r.get('language_tag','')}` | {n(r.get('population_base',''))} | {n(r.get('intrinsic_need_median',''))} |"
            )
        lines += [
            "",
            "These are formal enrolment or support cohorts, not whole-language reader counts. Their inclusion prevents a missing whole-language denominator from becoming an omission, while preserving denominator comparability.",
            "",
        ]
    return "\n".join(lines)


def main() -> None:
    text = PAPER.read_text(encoding="utf-8")
    start = text.index("### 6.1 Provisional needs-only order")
    # Keep the hand-written efficiency and commissioning subsections stable;
    # only replace the generated 6.1 block.  Older drafts had no 6.2 marker,
    # so retain the fallback boundary for backward-compatible regeneration.
    efficiency_marker = "### 6.2 Standardized compute-efficiency view"
    end = text.index(efficiency_marker, start) if efficiency_marker in text[start:] else text.index("## 7. Material priorities", start)
    updated = text[:start] + build_section() + text[end:]
    tmp = PAPER.with_suffix(".md.tmp")
    tmp.write_text(updated, encoding="utf-8")
    tmp.replace(PAPER)
    print(f"updated {PAPER} bytes={PAPER.stat().st_size} sha256={sha(PAPER)}")


if __name__ == "__main__":
    main()
