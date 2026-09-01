#!/usr/bin/env python3
"""Refresh manuscript appendices after the equal-basis Indonesian correction.

This is a bounded mechanical renderer. It reads only named tables in this task
directory and replaces exact Appendix A/B/D2/E/F sections in PAPER.md. It does not
touch the narrative body, references, or any other project.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "PAPER.md"


def read_csv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def safe(value: object) -> str:
    text = "—" if value is None or str(value).strip() == "" else str(value).strip()
    return text.replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def integer(value: str) -> str:
    return f"{int(float(value)):,}" if value else "—"


def row(values: list[object]) -> str:
    return "| " + " | ".join(safe(value) for value in values) + " |"


def replace_between(text: str, start: str, end: str, replacement: str) -> str:
    start_at = text.index(start)
    end_at = text.index(end, start_at)
    return text[:start_at] + replacement.rstrip() + "\n\n" + text[end_at:]


def csv_rows(path: Path) -> str:
    if path.suffix.lower() != ".csv":
        return "—"
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return str(sum(1 for _ in csv.DictReader(handle)))


def appendix_a() -> str:
    tracked = [
        "population_observations_master.csv",
        "population_source_register_public.csv",
        "candidate_interventions_master.csv",
        "natural_language_scores_v3.csv",
        "candidate_expansion_scores.csv",
        "staging/interlanguage_bundle_model/interlanguage_intervention_matrix.csv",
        "staging/interlanguage_bundle_model/interlanguage_population_links.csv",
        "interlanguage_package_scores.csv",
        "portfolio_compute_scenarios.csv",
        "curriculum_units.csv",
        "curriculum_portfolios.csv",
        "openstax_workload_measurements.csv",
        "portfolio_linguistic_candidates.csv",
        "TOP_10.csv",
        "TOP_100.csv",
        "table2_exact_gross_ceilings.csv",
        "table3_marginal_access_sensitivity_ranges.csv",
        "table4_top10.csv",
        "table5_top100_grouped_lanes.csv",
        "table5_top100_members.csv",
        "table6_package_exclusions_noncardinal.csv",
        "table6a_architecture_sensitivity_noncardinal.csv",
        "table7_curriculum_allocation_summary.csv",
        "table8_negative_controls_and_exclusions.csv",
        "population_mathematics_needs_register.csv",
        "top100_needs_assignment_v2.csv",
        "indonesian_equal_basis_and_forward_allocation.csv",
        "appendix_a_existing_work_reconciliation.csv",
        "appendix_b_global_gap_map.csv",
        "appendix_b_regional_gap_summary.csv",
        "appendix_c_accessibility_safeguards.csv",
        "appendix_d_top100_curriculum_mapping.csv",
        "appendix_f_interlanguage_matrix_summary.csv",
        "top100_interlanguage_overlap_crosswalk.csv",
        "TOP100_INTERLANGUAGE_CROSSWALK_METHOD_20260830.md",
        "TOP100_INTERLANGUAGE_CROSSWALK_VALIDATION_RECEIPT_20260830.md",
        "compute_token_audit_33_roots_20260830.json",
        "INDONESIAN_TASK_TOKEN_AUDIT_20260830.md",
        "INDONESIAN_PROGRAM_COMPUTE_AND_PAGE_RECONCILIATION_PUBLIC_20260830.md",
        "INDONESIAN_PUBLIC_PROGRAM_AUDIT_20260830.md",
        "JAPANESE_STAGE_SPECIFIC_ACCESS_ASSESSMENT_20260830.md",
        "ZH_HANS_CN_EQUAL_BASIS_AND_RESIDUAL_ASSESSMENT_20260830.md",
        "RESEARCH_FRONTIER_TRANSLATION_AS_EDUCATIONAL_INFRASTRUCTURE_20260830.md",
        "MULTIDISCIPLINARY_HIGH_REACH_CASES_20260830.md",
    ]
    out = [
        "# Appendix A. Reproducibility and computational provenance",
        "",
        "Research synthesis, deterministic modeling, drafting, and document production used **OpenAI Codex gpt-5.6-sol, Ultra**. This model identity does not replace the authorities in the evidence register. Exact source labels, measures, dates, locators, caveats, and hashes remain attached to the corresponding machine-readable rows.",
        "",
        "The table identifies the principal current inputs and derived tables. The release `MANIFEST.sha256` records the complete final public-file inventory; the paper deliberately does not attempt to hash itself inside this self-referential table.",
        "",
        "| Artifact | Data rows | Bytes | SHA-256 |",
        "|---|---:|---:|---|",
    ]
    for name in tracked:
        path = ROOT / name
        if not path.exists():
            raise FileNotFoundError(path)
        out.append(row([name.replace("\\", "/"), csv_rows(path), f"{path.stat().st_size:,}", sha256(path)]))
    return "\n".join(out)


def appendix_b() -> str:
    top = sorted(read_csv("TOP_100.csv"), key=lambda item: int(item["portfolio_position"]))
    needs = {item["intervention_id"]: item for item in read_csv("top100_needs_assignment_v2.csv")}
    out = [
        "# Appendix B. Full ordered Top 100",
        "",
        "Every row is one exact named natural-language edition. Population values retain the source's own measure and date; they are not summed as unique people. `Base access` is a labelled sensitivity, not an observed harmed-population count. All 100 rows carry an explicit first-product or bounded-audit assignment. The Top 10 use directly audited primary or official evidence; the other 90 retain lower-confidence territory-proxy or audit-required status rather than fabricated language-specific findings.",
        "",
        "| Pos. | Intervention | Production profile | Territory | Gross base population | Base access | Portfolio lane | Needs-audited first product/status | Source ID |",
        "|---:|---|---|---|---:|---:|---|---|---|",
    ]
    for item in top:
        need = needs[item["intervention_id"]]
        assignment = need["needs_first_package"]
        out.append(row([
            item["portfolio_position"], item["intervention_name"], item["target_profiles"],
            item["territory_or_scope"], integer(item["population_base"]),
            integer(item["marginal_access_base_sensitivity"]), item["portfolio_lane"],
            assignment, item["population_source_ids"],
        ]))
    return "\n".join(out)


def appendix_d2() -> str:
    states = read_csv("appendix_a_state_definitions.csv")
    out = [
        "## D2. Candidate-register reconciliation states",
        "",
        "| State | Rows | Registered meaning | Deficit effect | Boundary |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for item in states:
        out.append(row([
            item["reconciliation_state"], item["registered_row_count"], item["definition"],
            item["deficit_effect"], item["evidence_boundary"],
        ]))
    out.extend([
        "",
        "Indonesian Open Logic is a complete 722/722 baseline: verified coverage is 722 units, the residual is zero, and D=0 for that exact corpus. Mainland Simplified Chinese likewise has complete Open Logic (722/722) and Algebra and Trigonometry 2e (94/94), while Calculus Volume 1 is partial at 29/55; its D=1 value belongs only to the ex-ante equal-basis comparison, and forward allocation uses zero for complete components plus the exact 26-module calculus residual. Interslavic has seven accepted units but no comparable accepted-source-token denominator, so this paper does not convert those local units into demographic bridge reach. All other partial rows remain component-level. The detailed 211-row reconciliation is machine-readable in `appendix_a_existing_work_reconciliation.csv`.",
    ])
    return "\n".join(out)


def appendix_e() -> str:
    regions = read_csv("appendix_b_regional_gap_summary.csv")
    out = [
        "# Appendix E. Global regional, source, measure, and confidence gap map",
        "",
        "| Region | Subregion | Cardinal rows | Top100 | Sources | Measures | High | Medium | Aggregation rule |",
        "| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | --- |",
    ]
    for item in regions:
        out.append(row([
            item["region"], item["subregion"], item["cardinal_rows"], item["top100_rows"],
            item["distinct_source_count"], item["measure_types"], item["high_confidence_rows"],
            item["medium_confidence_rows"], item["population_aggregation"],
        ]))
    out.extend([
        "",
        "The global detail table has one row for each of the 135 cardinal natural-language interventions and an exact join to one population observation and its registered source. The source/measure/confidence table preserves source-level groupings. Counts in this appendix describe records and coverage strata; they are not summed population claims.",
    ])
    return "\n".join(out)


def appendix_f() -> str:
    portfolios = read_csv("appendix_d_curriculum_portfolios.csv")
    depths = read_csv("appendix_d_adaptation_depths.csv")
    mapping = sorted(read_csv("appendix_d_top100_curriculum_mapping.csv"), key=lambda item: int(item["portfolio_position"]))
    out = [
        "# Appendix F. Curriculum portfolios, adaptation depths, and needs assignment",
        "",
        "## F1. Exact curriculum portfolios",
        "",
        "| ID | Portfolio | Project | Exact content | Units | Source tokens | Preferred depth | Prerequisite | Sources | Caveat |",
        "| --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- |",
    ]
    for item in portfolios:
        out.append(row([
            item["portfolio_id"], item["portfolio_name"], item["source_project"], item["exact_content"],
            item["raw_units"], item["source_alpha_tokens"], item["preferred_depth"],
            item["prerequisite_portfolio"], item["source_ids"], item["notes"],
        ]))
    out.extend([
        "",
        "## F2. Exact adaptation depths",
        "",
        "| ID | Depth | Included components | Low | Base | High | Status | Caveat |",
        "| --- | --- | --- | ---: | ---: | ---: | --- | --- |",
    ])
    for item in depths:
        out.append(row([
            item["depth_id"], item["name"], item["included_components"],
            item["workload_multiplier_low"], item["workload_multiplier_base"],
            item["workload_multiplier_high"], item["educational_status"], item["notes"],
        ]))
    out.extend([
        "",
        "## F3. Legacy fixed-source Top100 workload mapping",
        "",
        "This mapping preserves the older uniform curriculum assignment solely as a reproducible compute sensitivity. It is **not** a claim that the named book is the first missing product in every population. The distribution is MV-1/D2 = 36, MV-1/D3 = 43, and SB-1/D3 = 21. SB-1 means **MV-1 plus Introductory Statistics 2e**.",
        "",
        "| Pos. | ID | Target | Profile | Lane | First comparator | First depth | Next comparator | Next depth | Next exact content | Population source |",
        "| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ])
    for item in mapping:
        out.append(row([
            item["portfolio_position"], item["intervention_id"], item["intervention_name"],
            item["target_profiles"], item["portfolio_lane"], item["first_product_id"],
            item["first_product_depth"], item["next_portfolio_id"], item["next_depth_id"],
            item["next_portfolio_exact_content"], item["population_source_ids"],
        ]))
    out.extend([
        "",
        "## F4. Needs-audited assignment layer",
        "",
        "`top100_needs_assignment_v2.csv` replaces F3 for commissioning decisions. It contains a source-backed, territory- and stage-specific first-product or audit assignment for all 100 ranked rows, with confidence and caveats kept explicit. A row can recommend a bounded gap audit rather than a translation when current supply is already substantial or insufficiently inventoried. `population_mathematics_needs_register.csv` preserves the assessment population, indicator, source, curricular interpretation, confidence, and caveat behind the directly audited assignments.",
    ])
    return "\n".join(out)


def add_pm_s021(text: str) -> str:
    if "### PM-S021" in text:
        return text
    marker = "### TH-S001"
    block = """### PM-S021

BPS-Statistics Indonesia. (2022). *Jumlah Penduduk Berumur 5 Tahun ke Atas Menurut Wilayah, Jenis Kelamin, dan Kemampuan Berbahasa Indonesia, di INDONESIA* [Long Form Population Census 2020 table]. https://sensus.bps.go.id/topik/tabular/sp2022/196

*Source type and time:* Official long-form census table; 2022 release/measure.

*Source note:* PM-S021 supplies the total population aged five or older reported able to understand spoken Indonesian and produce Indonesian words intelligible to another person: 248,501,794 able and 5,177,554 unable, total 253,679,348. This is oral functional ability, not written literacy, home language, mother tongue, academic reading comfort, or demand for a particular curriculum. The model uses it only as the gross Bahasa Indonesia reach ceiling and applies written-access and non-overlap factors separately.

"""
    return text.replace(marker, block + marker, 1)


def add_pm_s022(text: str) -> str:
    if "### PM-S022" in text:
        return text
    marker = "### TH-S001"
    block = """### PM-S022

National Bureau of Statistics of China. (2021). *Communique of the Seventh National Population Census (No. 2)*. https://www.stats.gov.cn/english/PressRelease/202105/t20210510_1817187.html

*Source type and time:* Official census communique; population at 2020-11-01, released 2021.

*Source note:* PM-S022 supplies the 1,411,778,724 mainland territory population ceiling. The source excludes Hong Kong, Macao, Taiwan, and foreigners in the mainland jurisdictions under its own definitions. It is not an exact count of Standard Simplified Chinese comfortable readers, academic-language users, or people lacking educational access. Standard-character prevalence and regional language variation are modeled separately.

"""
    return text.replace(marker, block + marker, 1)


def main() -> None:
    text = PAPER.read_text(encoding="utf-8")
    text = replace_between(text, "# Appendix A. Reproducibility and computational provenance", "# Appendix B. Full ordered Top 100", appendix_a())
    text = replace_between(text, "# Appendix B. Full ordered Top 100", "# Appendix C. Ordered accessibility safeguard portfolio", appendix_b())
    text = replace_between(text, "## D2. Candidate-register reconciliation states", "# Appendix E. Global regional, source, measure, and confidence gap map", appendix_d2())
    text = replace_between(text, "# Appendix E. Global regional, source, measure, and confidence gap map", "# Appendix F. Curriculum portfolios", appendix_e())
    text = replace_between(text, "# Appendix F. Curriculum portfolios", "# Appendix G. Unresolved output profiles and D0 exclusions", appendix_f())
    text = add_pm_s021(text)
    text = add_pm_s022(text)
    PAPER.write_text(text.rstrip() + "\n", encoding="utf-8")
    print(f"updated={PAPER}")


if __name__ == "__main__":
    main()
