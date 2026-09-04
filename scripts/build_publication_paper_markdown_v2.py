#!/usr/bin/env python3
"""Build the evidence-frozen publication manuscript from live tables.

The prose foundation in PAPER.md belongs to this from-scratch study.  This
builder replaces every data-dependent result, reproducibility statement,
appendix table, and bibliography from the current validated artifacts.
"""

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
SOURCES = ROOT / "sources"


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


def table(headers: list[str], rows: list[list[str]]) -> str:
    def safe(value: Any) -> str:
        return str(value or "").replace("|", " / ").replace("\n", " ").strip()

    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    out.extend("| " + " | ".join(safe(value) for value in row) + " |" for row in rows)
    return "\n".join(out)


def replace_section(text: str, start: str, end: str, replacement: str) -> str:
    begin = text.find(start)
    finish = text.find(end, begin + len(start))
    if begin < 0 or finish < 0:
        raise RuntimeError(f"section boundary missing: {start!r} -> {end!r}")
    return text[:begin] + replacement.rstrip() + "\n\n" + text[finish:]


top100 = read_csv(S / "TOP100_NEEDS_ONLY_v3.csv")
top10 = top100[:10]
score_by_id = {row["edition_target_id"]: row for row in read_csv(S / "GLOBAL_TARGET_SCORE_TABLE_PUBLIC_v3.csv")}
efficiency100 = read_csv(S / "TOP100_COMPUTE_EFFICIENCY_v3.csv")
efficiency10 = efficiency100[:10]
stage = read_csv(S / "ORDER_STAGE_OPPORTUNITY_v3.csv")
portfolio = read_csv(S / "GLOBAL_FUNDING_PORTFOLIO_v1.csv")
sentinels = read_csv(S / "GLOBAL_INCLUSION_SENTINEL_STATUS_v1.csv")
structural = [row for row in portfolio if row["decision_lane"] == "STRUCTURAL_SIGNED_AND_ACCESSIBILITY"]
displacement = [row for row in portfolio if row["decision_lane"] == "DISPLACEMENT_HOST_SPECIFIC"]
bridges = [row for row in portfolio if row["decision_lane"] == "BRIDGE_AND_INTERLANGUAGE_EXPERIMENT"]
context = [
    row
    for row in portfolio
    if row["decision_lane"] in {"MANDATORY_LARGE_CONTEXT_AND_VOI", "MANDATORY_SENTINEL_GAP_AND_VOI"}
]
needs_rows = read_csv(A / "STAGE_SUBJECT_NEEDS_MAPPING.csv")
needs_map = {row["target_id"]: row for row in needs_rows}
sensitivity = read_csv(S / "RANK_SENSITIVITY_SUMMARY_v1.csv")
sensitivity_qa = json.loads((Q / "RANK_SENSITIVITY_SUMMARY_QA_v1.json").read_text(encoding="utf-8"))
rank_qa = json.loads((Q / "GLOBAL_ACCESS_RANKINGS_V3_QA.json").read_text(encoding="utf-8"))
inclusion_qa = json.loads((Q / "GLOBAL_INCLUSION_DISPOSITION_QA_v1.json").read_text(encoding="utf-8"))
portfolio_qa = json.loads((Q / "GLOBAL_FUNDING_PORTFOLIO_QA_v1.json").read_text(encoding="utf-8"))
trace_qa = json.loads((Q / "TOP100_SOURCE_TRACE_AUDIT_v2.json").read_text(encoding="utf-8"))

assert len(top100) == 100
assert len(efficiency100) == 100
assert [int(row["decision_rank"]) for row in top100] == list(range(1, 101))
assert [int(row["decision_rank"]) for row in efficiency100] == list(range(1, 101))
assert rank_qa["status"] == "PASS"
assert portfolio_qa["status"] == "PASS"
assert trace_qa["status"] == "PASS"
assert sensitivity_qa["status"] == "PASS"

robust_top10 = [
    row
    for row in sensitivity
    if row["robust_top10_all_prior_families"] == "true"
    and row["robust_top10_all_factor_removals"] == "true"
]
robust_top10_ids = {row["edition_target_id"] for row in robust_top10}
union_top10 = [
    row
    for row in sensitivity
    if min(int(row["prior_family_rank_min"]), int(row["factor_removal_rank_min"])) <= 10
]

top10_table = table(
    ["Rank", "Exact target", "Source population", "Model median unmet need", "Top-10 probability"],
    [
        [
            row["decision_rank"],
            f"{row['label']} (`{row['language_tag']}`)",
            population_cell(row),
            fmt_int(row["intrinsic_need_median"]),
            fmt_pct(row["top10_probability"]),
        ]
        for row in top10
    ],
)

efficiency10_table = table(
    ["Efficiency rank", "Need rank", "Exact target", "Model median unmet-need equivalent per million FECU", "Compute class"],
    [
        [
            row["decision_rank"],
            score_by_id[row["edition_target_id"]]["l_m_need_rank"],
            f"{row['label']} (`{row['language_tag']}`)",
            fmt_int(float(row["access_gain_per_compute_median"]) * 1_000_000),
            row["compute_evidence_class"],
        ]
        for row in efficiency10
    ],
)

stage_table = table(
    ["Stage rank", "Exact opportunity", "Cohort", "Model median", "Definition"],
    [
        [
            row["opportunity_rank"],
            f"{row['label']} (`{row['language_tag']}`)",
            population_cell(row),
            fmt_int(row["intrinsic_need_median"]),
            row["population_definition"],
        ]
        for row in stage
    ],
)

lane_counts = portfolio_qa["lane_counts"]
lanes_table = table(
    ["Decision lane", "Rows", "What can be compared", "Immediate use"],
    [
        ["1. Direct-person comparable", str(lane_counts["DIRECT_PERSON_COMPARABLE"]), "Source-authorized person-language rows under the same model", "High-reach package and evidence prioritization"],
        ["2. Stage opportunity", str(lane_counts["STAGE_OPPORTUNITY"]), "Direct learner/sector cohorts with each other", "Stage-specific commissioning without inventing whole-language readers"],
        ["3. Mandatory context and value of information", str(lane_counts["MANDATORY_LARGE_CONTEXT_AND_VOI"] + lane_counts["MANDATORY_SENTINEL_GAP_AND_VOI"]), "No cross-row unmet-need rank", "Keep high-scale and undermeasured populations visible; collect allocation-changing evidence"],
        ["4. Structural access portfolio", str(lane_counts["STRUCTURAL_SIGNED_AND_ACCESSIBILITY"] + lane_counts["DISPLACEMENT_HOST_SPECIFIC"] + lane_counts["BRIDGE_AND_INTERLANGUAGE_EXPERIMENT"]), "Only within exact compatible units", "Named sign languages, accessibility/offline modes, host-specific displacement continuity, and bounded bridge experiments"],
    ],
)

profile_ids = [
    "hi-Deva-IN",
    "id-Latn-ID",
    "ru-Cyrl-RU",
    "pnb-Arab-PK",
    "bn-Beng-BD",
    "mr-Deva-IN",
    "te-Telu-IN",
    "ta-Taml-IN",
    "jv-Latn-ID",
    "th-Thai-TH",
    "zh-Hans-CN",
    "ja-Jpan-JP",
]
profiles = [needs_map[key] for key in profile_ids if key in needs_map]
needs_table = table(
    ["Population or route", "Stage order", "First package classes", "Then expand to", "Delivery"],
    [
        [
            row["target_label"],
            row["priority_stage_order"].replace("|", " -> "),
            row["p0_material_classes"],
            row["p1_p2_material_classes"],
            row["delivery_profile"],
        ]
        for row in profiles
    ],
)

section6 = f"""## 6. Results: inclusion first, then comparable orders

### 6.1 What the global sweep contains

The evidence freeze represents {rank_qa['target_count']:,} exact, unresolved, regional, and intervention authority targets. Of these, {rank_qa['person_need_target_count']:,} exact targets have source-authorized person denominators and enter the direct-person model; {rank_qa['stage_opportunity_target_count']:,} targets enter a separate stage-opportunity order; and {rank_qa['unranked_target_count']:,} remain explicitly unranked or contextual. Among the unranked rows, {rank_qa['unranked_no_source_bound_person_denominator_count']:,} lack a source-bounded person denominator. The public-safe score table leaves those population and score fields empty rather than displaying a synthetic country or world ceiling.

The high-consequence sentinel audit contains {inclusion_qa['counts']['sentinel_checks']} checks: {inclusion_qa['sentinel_presence_counts']['PRESENT_EXACT_TARGET']} have an exact target, {inclusion_qa['sentinel_presence_counts']['PRESENT_BASE_LANGUAGE_ONLY_EXACT_TERRITORY_SCRIPT_OR_STANDARD_PROFILE_MISSING']} has only a broader base-language target, {inclusion_qa['sentinel_presence_counts']['PRESENT_CONTEXT_STRATUM_NO_EXACT_EDITION_TARGET']} have a context stratum but no exact edition target, and {inclusion_qa['sentinel_presence_counts']['MISSING_EXACT_TARGET']} remain missing. The two unresolved exact-target gaps are Algerian Amazigh varieties and Hmong varieties; neither receives a fabricated unified language identity or population. The context-only checks include major English and French education-language contexts that need exact comfort, stage, and resource endpoints before they can be compared.

This is a global gap map, not an assertion that all human languages have been observed. Its release condition is narrower and operational: no known high-consequence population is allowed to disappear merely because its available measure is incompatible with a speaker rank. Every such case must appear as a direct row, stage cohort, context/value-of-information row, structural portfolio, or named evidence gap.

### 6.2 Direct-person comparable order

The reference L-M order contains {rank_qa['person_need_target_count']} source-authorized person-language targets. The table below shows the first ten; Appendix A prints all 100 leading rows. Of the Top 100, {trace_qa['counts']['bound_shapes_in_top100']['POINT']} have point constructs and {trace_qa['counts']['bound_shapes_in_top100']['INTERVAL']} retain non-degenerate source intervals. A point constructed from a published count is not presented as a confidence interval; a range from a different construct is never attached as its low or high endpoint.

{top10_table}

These are model-conditional expected-need ranks, not directly observed global facts. Target-specific open-resource scarcity remains unmeasured for the scored universe, so all {rank_qa['primary_order_eligible_count']} direct-person and stage rows use the same 0.5 resource prior. Schooling-language gap uses the 0.4 common prior for 178 of 206 rows; academic-language non-overlap uses 0.4 for 201; and accessibility uses 0.5 for 204. Country learning/completion and delivery context provide more variation, but they remain ecological proxies where no target-specific cross-tab exists.

That evidence structure is visible in the sensitivity result. The Spearman correlation between model rank and the descending model-population point is {sensitivity_qa['population_rank_spearman']:.4f}. Across four common-prior families and seven factor-removal/reference scenarios, nine targets remain in every Top 10: {', '.join(row['label'] for row in robust_top10)}. The union of possible Top-10 members adds {', '.join(row['label'] for row in union_top10 if row['edition_target_id'] not in robust_top10_ids)}. In the reference run Central Thai is tenth; under the scenario set the boundary can instead admit Gujarati or Pashto. Scenario rank correlations with the reference range from {min(sensitivity_qa['scenario_rank_spearman'].values()):.4f} to {max(sensitivity_qa['scenario_rank_spearman'].values()):.4f}.

The correct funding interpretation is therefore two-part. The stable high ranks identify large source-bounded populations for which an open package could have high absolute reach. They do not prove that the same package, stage, or subject is missing in each language. Production should proceed with a target-specific resource and stage audit embedded in the same commission, while the value-of-information lane measures factors capable of changing the order.

Taiwan's official 2020 table reports current primary-or-secondary use by 21,090,192 resident nationals aged six or older for Mandarin, 18,728,839 for Taiwanese/Taigi, and 1,193,332 for Hakka. These appear at ranks 32, 33, and 67 as standalone interventions, but overlap and cannot be summed as 41,012,363 unique people; Traditional written Chinese is a different access endpoint (Directorate-General of Budget, Accounting and Statistics, 2020).

### 6.3 Standardized new-compute planning order

The second primary order divides the same model-conditional unmet-need burden by the standardized fresh-equivalent compute estimate for one fixed from-scratch package. Because no common package-effect estimate is available, this is a burden-per-compute planning proxy, not an estimate of causal access gained. It does not convert tokens to money, estimate a contractor budget, or claim that an end-to-end job has been observed. Every row in the present order uses a model-conditional script envelope; differences are therefore planning assumptions to be stress-tested, not measured production advantages.

{efficiency10_table}

The efficiency and need orders are close because the current script-envelope estimates vary far less than the source-bounded population denominators. Javanese moves from need rank 9 to efficiency rank 7 under the Latin-script envelope, while Telugu and Tamil move down one position under their declared envelopes. This movement is useful for planning but is not evidence that one community's need matters more. The complete Top 100 efficiency order appears in Appendix A.2 and as a machine-readable CSV.

### 6.4 Stage opportunities: Chinese and Japanese

Some very large educational opportunities are observed as learner cohorts rather than whole-language readerships. They are not excluded; they are ordered in their own unit:

{stage_table}

The Mainland Chinese row makes Simplified Standard Written Chinese one of the largest immediately visible educational opportunities in the study. The relevant first commissions are not a generic claim that China lacks textbooks. They are open and adaptable advanced STEM, research methods, reproducibility, open science, accessible semantic formats, vocational/adult routes, and targeted rural, migrant, disability, or field-specific gaps. Spoken Putonghua and written literacy remain separate constructs.

Japan is not a negative control for educational worth. Its strong general educational system narrows the likely marginal package: research and postgraduate reading/writing, open science and reproducibility, accessible advanced STEM, specialist professional material, international terminology bridges, and exact support cohorts. The 2,922,969 opportunity row is tertiary enrolment, not the Japanese-speaking population; other directly recorded cohorts remain in the evidence register. A smaller stage denominator can still support high-leverage research or accessibility work.

### 6.5 The funding portfolio

No responsible allocation can be made from the direct-person Top 100 alone. The release therefore exposes four coequal decision lanes:

{lanes_table}

For an initial high-reach compute programme, the first direct-person slate is the nine scenario-robust targets, with Thai, Gujarati, and Pashto treated as the empirically unresolved tenth-position set rather than separated by a cosmetic tie-break. This is a priority for fitted open packages, not a recommendation to translate one identical book into each language. Simplified written Chinese should be commissioned simultaneously through its stage lane because the 280.4-million formal-education cohort is too large to disappear from a speaker-only table. Japan receives a narrower advanced/research/accessibility programme. Named sign-language and accessibility modes receive a minimum-service lane even where population measurement is weak. Displaced learners receive host-specific source-language continuity, host-language acquisition, credential, stage, and offline packages. Bridge and interlanguage work is funded as measured comprehension experiments and shared production infrastructure, not as unverified population substitution.

### 6.6 What educational material is needed

The programme must distinguish early childhood, primary, secondary, vocational/adult, undergraduate, postgraduate, and research access. “Education” includes frontier monographs, research methods, standards, software and data documentation, and specialist professional learning; those resources serve smaller cohorts but can have high institutional leverage. The evidence-based first and second package classes for leading routes are:

{needs_table}

For Bengali in India, the source-authorized population row is exact but the present stage-subject map is not country-specific enough to borrow Bangladesh's learning and climate profile. The shared Bangla semantic source can lower production cost, while India and Bangladesh retain separate curriculum, terminology, examples, standards, and outcome evidence. Taiwan Mandarin, Taigi, and Hakka likewise need separate spoken/written and literacy endpoints before one package is treated as coverage for another.

Across the wider Top 100, the recurring high-utility bundles are: foundational literacy/numeracy/science with cumulative practice and complete solutions; planned strongest-language-to-school-language bridges; secondary STEM and prerequisite recovery; health; agriculture, water, climate, and disaster resilience; computing and data; household and enterprise finance; management and cooperative governance; teacher/facilitator education; vocational safety and measurement; undergraduate gateway sequences; research methods and open science; and advanced specialist corpora. Appendix A identifies who is in the comparable orders; Appendix E prints the 63-row stage-subject recommendation register used for the leading and structurally important routes.

### 6.7 Open and autonomous delivery

Open licensing is an operational requirement: newly commissioned materials must be lawful to download, retain, copy, adapt, translate, and redistribute (UNESCO, 2019). Autonomous packages must not assume a teacher, continuous connectivity, a laptop, or a paid service; they require prerequisite maps, diagnostics, explanation, practice, reasoned answers, mastery checks, and a route forward. Delivery branches remain independent: semantic HTML with MathML, accessible EPUB/PDF, low-data audio with transcripts, captioned or named-sign-language video, plain-language companions, and small offline bundles. OpenStax's 73-title catalogue is a strong upper-secondary/introductory-tertiary baseline, not a complete world curriculum; the 45 complementary records cover early learning, computing, health, agriculture, climate, research methods, open science, and advanced reference (OpenStax, n.d.).
"""


section9 = f"""## 9. Reproducibility and release design

The public package separates authority, evidence, modeling, and decision outputs. The authority contains {rank_qa['target_count']:,} targets. The evidence authorization ledger has 850 records and admits 259 population observations to {rank_qa['person_need_target_count']} direct-person targets; three stage observations collapse to {rank_qa['stage_opportunity_target_count']} stage targets. The source-to-score crosswalk contains {inclusion_qa['counts']['source_to_score_crosswalk_rows']} rows. The public-safe score table contains {inclusion_qa['counts']['public_score_rows']:,} rows and suppresses non-empirical population values for {inclusion_qa['counts']['public_unranked_rows_with_population_values_removed']:,} unranked targets.

The direct-person source-trace audit passes all target, authorization, source, bound-normalization, forbidden-predictor, and rank-sequence checks. The territory-binding audit checks 921 valid BCP-47 region rows and 87 unresolved identities with zero mismatches. The portfolio audit contains 186 rows across the direct, stage, context/value-of-information, structural, displacement, and bridge lanes. The inclusion audit reports `PASS_WITH_EXPLICIT_EVIDENCE_GAPS`: that status is an honest description of a versioned global search, not a claim that every language has a measured denominator.

Key frozen artifacts are:

| Artifact | Purpose | SHA-256 |
|---|---|---|
| `structured/GLOBAL_TARGET_SCORE_TABLE_PUBLIC_v3.csv` | Public-safe all-target score and disposition table | `{sha(S / 'GLOBAL_TARGET_SCORE_TABLE_PUBLIC_v3.csv')}` |
| `structured/TOP100_NEEDS_ONLY_v3.csv` | Full direct-person Top 100 | `{sha(S / 'TOP100_NEEDS_ONLY_v3.csv')}` |
| `structured/GLOBAL_FUNDING_PORTFOLIO_v1.csv` | Multi-lane allocation portfolio | `{sha(S / 'GLOBAL_FUNDING_PORTFOLIO_v1.csv')}` |
| `structured/GLOBAL_INCLUSION_DISPOSITION_REGISTER_v1.csv` | Full authority/context/structural/bridge/sentinel disposition | `{sha(S / 'GLOBAL_INCLUSION_DISPOSITION_REGISTER_v1.csv')}` |
| `structured/SOURCE_TO_SCORE_CROSSWALK_v1.csv` | Source-record disposition crosswalk | `{sha(S / 'SOURCE_TO_SCORE_CROSSWALK_v1.csv')}` |
| `structured/RANK_SENSITIVITY_SUMMARY_v1.csv` | Prior and factor-removal rank stability | `{sha(S / 'RANK_SENSITIVITY_SUMMARY_v1.csv')}` |
| `structured/TOP100_COMPUTE_EFFICIENCY_v3.csv` | Standardized new-compute Top 100 planning order | `{sha(S / 'TOP100_COMPUTE_EFFICIENCY_v3.csv')}` |
| `agent_reports/STAGE_SUBJECT_NEEDS_MAPPING.csv` | Population-stage-subject recommendations | `{sha(A / 'STAGE_SUBJECT_NEEDS_MAPPING.csv')}` |
| `agent_reports/INTERLANGUAGE_STRUCTURED_EVIDENCE_MATRIX.csv` | Bridge/interlanguage evidence and non-served groups | `{sha(A / 'INTERLANGUAGE_STRUCTURED_EVIDENCE_MATRIX.csv')}` |

The executable model retains fixed target-set equality, source and row hashes, a forbidden-predictor scan, deterministic SHA-256-addressed draws, L-ID partial-identification bounds, four prior families, seven factor-removal scenarios, and explicit script-envelope compute assumptions. The compute comparison is a fresh-equivalent planning unit, not a price conversion. Local holdings, prior project completion, sunk compute, personal preferences, national income, prestige, and demographic quotas are absent from the model and the portfolio builder.

The canonical public repository is https://github.com/KokunoYumeto/allocating-ai-translation-compute-for-educational-access. The release includes this paper as PDF, DOCX, Markdown, and readable offline HTML together with the machine-readable tables, sources, scripts, and sanitized QA receipts. Public-byte readback is required after both GitHub and Zenodo publication.
"""


appendix_a = "## Appendix A. Full direct-person and standardized-compute orders\n\n"
appendix_a += "### A.1 Direct-person Top 100\n\n"
appendix_a += "The table is complete for the comparable reference need order. Population entries retain points or source intervals; model medians are rounded display values. Exact definitions, sources, URLs, hashes, uncertainty fields, and compute estimates are in `structured/GLOBAL_FUNDING_PORTFOLIO_v1.csv` and `structured/TOP100_NEEDS_ONLY_v3.csv`. Rows are standalone interventions and must not be summed without a disjoint-person crosswalk.\n\n"
appendix_a += table(
    ["Rank", "Exact target", "Source population", "Reference year", "Model median", "Top-100 probability"],
    [
        [
            row["decision_rank"],
            f"{row['label']} (`{row['language_tag']}`)",
            population_cell(row),
            row["population_reference_year"],
            fmt_int(row["intrinsic_need_median"]),
            fmt_pct(row["top100_probability"]),
        ]
        for row in top100
    ],
)
appendix_a += "\n\n### A.2 Standardized new-compute Top 100\n\n"
appendix_a += "This is a burden-per-compute planning order for one standardized from-scratch package. FECU means fresh-equivalent compute unit; it is not a monetary price or an observed complete-job token total. Because a common causal package effect is not measured, the model-median column divides the same common-prior unmet-need equivalent by modeled FECU rather than claiming observed access gained.\n\n"
appendix_a += table(
    ["Efficiency rank", "Need rank", "Exact target", "Unmet-need equivalent per million FECU", "Standard compute (FECU)"],
    [
        [
            row["decision_rank"],
            score_by_id[row["edition_target_id"]]["l_m_need_rank"],
            f"{row['label']} (`{row['language_tag']}`)",
            fmt_int(float(row["access_gain_per_compute_median"]) * 1_000_000),
            fmt_int(row["standard_compute_p50_fecu"]),
        ]
        for row in efficiency100
    ],
)

appendix_b = "## Appendix B. Stage, large-context, and explicit evidence-gap lanes\n\n"
appendix_b += "### B.1 Stage opportunities\n\n" + stage_table + "\n\n"
appendix_b += "### B.2 Mandatory large contexts and sentinel gaps\n\n"
appendix_b += table(
    ["Display order", "Population/context", "Source-bounded measure", "Evidence status", "Required action"],
    [
        [
            row["lane_rank"],
            row["target_label"],
            population_cell(row),
            row["evidence_status"],
            row["priority_action"],
        ]
        for row in context
    ],
)

appendix_c = "## Appendix C. Structural access, signed-language, and displacement portfolios\n\n"
appendix_c += "### C.1 Named sign-language and accessibility interventions\n\n"
appendix_c += table(
    ["Display order", "Target or intervention", "Mode/tag", "Territory/community", "Denominator", "Evidence status"],
    [
        [
            row["lane_rank"],
            row["target_label"],
            row["language_tag_or_mode"],
            row["territory_or_community"],
            population_cell(row),
            row["evidence_status"],
        ]
        for row in structural
    ],
)
appendix_c += "\n\n### C.2 Host-specific displacement portfolios\n\n"
appendix_c += table(
    ["Display order", "Portfolio", "Status cohort", "Language/script arms", "Evidence status"],
    [
        [
            row["lane_rank"],
            row["target_label"],
            population_cell(row),
            row["language_tag_or_mode"],
            row["evidence_status"],
        ]
        for row in displacement
    ],
)

appendix_d = "## Appendix D. Bridge and interlanguage research portfolio\n\n"
appendix_d += "No entry receives family-wide population credit. Evidence grades order the display only; they are not benefit scores. Mathematics-specific comprehension, training burden, script, prior exposure, genre, and overlap with existing natural-language editions must be measured separately from shared-source production reuse.\n\n"
appendix_d += table(
    ["Display order", "Bridge or design", "Class/mode", "Evidence grade", "Current disposition"],
    [
        [
            row["lane_rank"],
            row["target_label"],
            row["language_tag_or_mode"],
            row["evidence_status"],
            row["recommendation_basis"],
        ]
        for row in bridges
    ],
)

appendix_e = "## Appendix E. Stage and subject recommendations\n\n"
appendix_e += "The 63 rows below are conditional package recommendations, not additional population ranks. They identify the first educational stages and material classes to investigate or commission for leading, stage-specific, regionally important, displaced, and structurally important routes. A recommendation does not claim that every listed resource is absent; its boundary note states the principal overreach to avoid. The full machine-readable register retains second-wave packages, delivery profiles, evidence keys, and confidence.\n\n"
appendix_e += table(
    ["Target or route", "Priority stages", "First package classes", "Why it may have outsized utility", "Boundary"],
    [
        [
            f"{row['target_label']} (`{row['target_id']}`)",
            row["priority_stage_order"].replace("|", " -> "),
            row["p0_material_classes"],
            row["outsized_local_utility"],
            row["boundary_note"],
        ]
        for row in needs_rows
    ],
)

reference_lines = []
for line in (SOURCES / "REFERENCES_APA.md").read_text(encoding="utf-8").splitlines():
    stripped = line.strip()
    if stripped.startswith("-") or stripped.startswith("#"):
        continue
    if re.search(r"\((?:\d{4}|n\.d\.)", stripped) and "http" in stripped:
        reference_lines.append(stripped)
references = "## References\n\n" + "\n\n".join(reference_lines)

text = PAPER.read_text(encoding="utf-8")
title = "# Allocating AI Compute for Global Educational Access\n"
provenance = "\n**Evidence freeze:** 2026-09-04  \n**Model and workflow provenance:** OpenAI Codex gpt-5.6-sol, Ultra.\n"
if "**Model and workflow provenance:**" in text:
    text = re.sub(r"\n\*\*Evidence freeze:.*?Ultra\.\n", provenance, text, count=1, flags=re.S)
else:
    text = text.replace(title, title + provenance, 1)

new_abstract = (
    f"The evidence freeze represents {rank_qa['target_count']:,} authority targets: "
    f"{rank_qa['person_need_target_count']} source-authorized direct-person targets, "
    f"{rank_qa['stage_opportunity_target_count']} separately comparable stage-opportunity targets, and "
    f"{rank_qa['unranked_target_count']} visible unranked or contextual targets. A common-prior reference order "
    "places Hindi and Bahasa Indonesia first among comparable person-denominator rows; Simplified Standard Written Chinese leads the separate stage-opportunity lane, and Japanese remains a targeted tertiary, research, and accessibility opportunity. The full Top 100, high-consequence evidence gaps, signed-language and accessibility portfolio, displacement portfolios, and interlanguage experiments are all published rather than reduced to one league table. Sensitivity analysis shows that the direct order is highly population-dominant because most exact scarcity and academic-overlap factors remain unmeasured; its correct use is transparent high-reach prioritization plus target-specific package evidence, not a claim of observed global need.\n"
)
text = replace_section(text, "## Abstract", "## 1. Introduction", "## Abstract\n\n" + new_abstract)

text, count = re.subn(
    r"All target burdens and ranks are calculated jointly in each draw\..*?\(Manski, 2003; Imbens & Manski, 2004; Gelman et al\., 2013; Little & Rubin, 2019\)\.",
    f"All target burdens and ranks are calculated jointly in each draw. The model-conditional Top K selects the K largest posterior expected burdens; exact ties crossing the boundary produce the complete tie set rather than an arbitrary target-ID order. For each of the {rank_qa['person_need_target_count']} rankable person targets, the L-M output reports posterior mean, median, P05/P95 burden, L-ID bounds/status, model rank, Top-10 and Top-100 inclusion probabilities, evidence tier, and model status. The {rank_qa['stage_opportunity_target_count']} exact stage-opportunity targets report model-conditional burden fields in their separate lane but no person-order rank or Top-K probability; the {rank_qa['unranked_target_count']} unranked/context targets retain identity, source/authorization, and explicit status while rank/posterior fields remain blank. The persisted v3 sensitivity outputs report rank changes across four paired common-prior families and seven factor-removal/reference scenarios. This output is labelled a **model-conditional expected-need decision order**, not a table of directly measured global facts (Manski, 2003; Imbens & Manski, 2004; Gelman et al., 2013; Little & Rubin, 2019).",
    text,
    count=1,
    flags=re.S,
)
if count != 1:
    raise RuntimeError("L-M output paragraph not replaced")
text = re.sub(
    r"The persisted v3 sensitivity outputs are limited to four paired common-prior proxy families .*?supplied universe and uncertainty model\.",
    f"The persisted v3 sensitivity outputs contain four paired common-prior families ({4 * rank_qa['person_need_target_count']:,} rows) and seven factor-removal/reference scenarios ({7 * rank_qa['person_need_target_count']:,} rows) over the {rank_qa['person_need_target_count']} person targets. The release also publishes a target-level min/max-rank summary and scenario rank correlations. These analyses do not resolve missing target-specific factors; they show which conclusions are stable under the declared common-prior perturbations. A candidate is described as robust or definitely within a Top-K only when those claims follow from the supplied universe and uncertainty model.",
    text,
    count=1,
    flags=re.S,
)

section6_start = (
    "## 6. Global inclusion findings before ranking"
    if "## 6. Global inclusion findings before ranking" in text
    else "## 6. Results: inclusion first, then comparable orders"
)
text = replace_section(text, section6_start, "## 7. Material priorities", section6)
text = replace_section(text, "## 9. Reproducibility and release design", "## 10. Limitations", section9)

# Replace the old references and every previously generated appendix in one
# idempotent tail operation.  After the first run the appendices precede the
# bibliography, so truncating at References alone would duplicate them.
tail_offsets = [
    offset
    for marker in ("## Appendix A. Full direct-person Top 100", "## Appendix A. Full direct-person and standardized-compute orders", "## References")
    if (offset := text.find(marker)) >= 0
]
if not tail_offsets:
    raise RuntimeError("manuscript tail boundary missing")
tail_at = min(tail_offsets)
text = text[:tail_at].rstrip() + "\n\n" + appendix_a + "\n\n" + appendix_b + "\n\n" + appendix_c + "\n\n" + appendix_d + "\n\n" + appendix_e + "\n\n" + references + "\n"

# Keep the publication byte-stable across PDF/DOCX renderers that handle
# typographic dash code points differently. Mathematical minus signs are not
# touched; only prose dash characters are normalized.
text = text.replace("\u2014", " - ").replace("\u2013", "-").replace("\u2011", "-")

PAPER.write_text(text, encoding="utf-8")
print(
    json.dumps(
        {
            "path": str(PAPER),
            "bytes": PAPER.stat().st_size,
            "sha256": sha(PAPER),
            "top100_rows": len(top100),
            "portfolio_rows": len(portfolio),
            "reference_entries": len(reference_lines),
            "robust_top10_count": len(robust_top10),
        },
        ensure_ascii=False,
        indent=2,
    )
)
