#!/usr/bin/env python3
"""Build the source-audited v1.1 paper from canonical validated tables."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "PAPER.md"
TOP100 = ROOT / "TOP_100.csv"
TOP10 = ROOT / "TOP_10.csv"
NEEDS = ROOT / "top100_needs_assignment_v2.csv"
CROSSWALK = ROOT / "top100_interlanguage_overlap_crosswalk.csv"
UNIVERSE = ROOT / "staging" / "global_expected_universe" / "expected_language_profiles_v1_1.csv"
ARCH = ROOT / "staging" / "global_expected_universe" / "bridge_shared_core_hypotheses_v1_1.csv"
SUPPLEMENT = ROOT / "staging" / "global_expected_universe" / "profile_population_estimates_supplement_v1_1.csv"
JOINS = ROOT / "staging" / "global_expected_universe" / "expected_profile_population_joins_v1_1.csv"
HIGH_NEEDS = ROOT / "staging" / "high_reach_education_needs" / "high_reach_education_needs_v1_1.csv"
FORWARD = ROOT / "table_c_forward_residual_commissioning.csv"
SCENARIOS = ROOT / "compute_scenarios.csv"
PIPELINE_RECEIPT = ROOT / "V1_1_DATA_PIPELINE_REBUILD_20260831.json"
COMPANION_RECEIPT = ROOT / "top100_companions_v1_1_validation.json"
POLICY_RECEIPT = ROOT / "allocation_policy_v1_1_validation.json"
POLICY_RECEIPT_SCHEMA = "interlanguage/allocation-policy-validation/1.1.0"
COMPUTE_RECEIPT = ROOT / "model_inputs" / "155_COMPUTE_TOKEN_AUDIT_33_ROOTS_20260830.json"
EXPECTED_COMPUTE_SHA = "1DAFEAC9EB161204DF470D247811F4E29415EE8AB3A297E412DBDD619CC0911C"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def escape(value: object) -> str:
    text = str(value).replace("\r", " ").replace("\n", " ").strip()
    return text.replace("|", "\\|")


def md_table(headers: list[str], rows: list[list[object]]) -> str:
    output = [
        "| " + " | ".join(escape(value) for value in headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    output.extend("| " + " | ".join(escape(value) for value in row) + " |" for row in rows)
    return "\n".join(output)


def policy_receipt_summary(receipt: dict[str, object] | None) -> str:
    """Report actual policy diagnostics without interpreting them as benefit estimates."""
    if receipt is None:
        return (
            "No allocation-policy diagnostic receipt was present at build time. "
            "The canonical CSV sequence is reproduced without claiming a validated "
            "policy diagnostic or a measured marginal-access optimum."
        )
    diagnostics = receipt["diagnostics"]
    policy = receipt["policy"]
    entries = diagnostics["entries"]
    unknown_r = sum(entry["dimensions"]["R"]["status"] == "unknown" for entry in entries.values())
    provisional_r = sum(entry["dimensions"]["R"]["status"] == "provisional_planning_inference" for entry in entries.values())
    rows: list[list[object]] = [
        ["Policy identity", policy["policy_id"]],
        ["Master candidates / constructed actions / selected actions", f"{receipt['registered_master_rows']} / {diagnostics['input_rows']} / {diagnostics['dispatched_rows']}"],
        ["Exact duplicate-package rows suppressed", len(diagnostics["suppressed_entries"])],
        ["Strict evidence-dominance comparisons", len(diagnostics["dominance_edges"])],
        ["Provisional source-informed R judgments / unresolved R", f"{provisional_r} / {unknown_r}"],
        ["Package-calibration memoranda", len(receipt.get("planning_calibration_inputs", []))],
        ["Declared cycle", " -> ".join(policy["lane_cycle"])],
        ["Within-view gross-scope thresholds (persons)", ", ".join(f"{value:,}" for value in policy["gross_scope_thresholds_persons"])],
        ["Mechanical validation", receipt["status"]],
    ]
    return (
        "The full-register selector separates an evidence partial order from an operational work queue. "
        "A 6:3:1 cycle reserves turns for high-reach, regional-depth and endangered/prestige work. "
        "This is an explicit allocation choice, not an estimated optimum. Within a lane, it uses "
        "the currently undominated actions, then stage-specific package evidence, then the least-exposed "
        "compatible population-measure subqueue; gross-size bands, target/format specificity and finally "
        "stable identifiers resolve remaining choices. It never renames a gross population as newly "
        "comfortable readership. Literature-constrained package-specific planning judgments are now "
        "admitted: the controlling formalism asks for plausible readership ranges, not experimentally "
        "measured uptake. A separately reported measured-only view retains those judgments as priors "
        "rather than presenting them as observations. Recovered OpenLogic R/S/A/N judgments apply only "
        "to exact-profile formal-reasoning packages; they are not copied onto ECE, TVET or small residual "
        "products. Missing magnitudes remain unknown, not zero. A static evidence-front number is only "
        "a diagnostic: once a candidate's remaining dominators clear, it can compete immediately. "
        "Unknown/incomparable rows therefore do not have to be exhausted before a well-evidenced "
        "candidate in a later static layer becomes eligible. Exact duplicate packages have one owner. "
        "A canonical component register separates locale, package, stage and modality before ranking; "
        "mixed bundles must be residualized and their opportunity recalibrated. Reused components "
        "are recorded separately and cannot retain another audience. Different stages and outputs "
        "are not silently deleted.\n\n"
        f"The operational policy diagnostic is `{POLICY_RECEIPT.name}` "
        f"(SHA-256 `{sha256(POLICY_RECEIPT)}`). Its reported fields are reproduced "
        "below. A PASS status concerns its declared deterministic checks; it does "
        "not establish a measured welfare optimum.\n\n"
        + md_table(["Policy / diagnostic field", "Reported value"], rows)
    )


def old_references(text: str) -> list[str]:
    start = text.find("## References\n")
    if start < 0:
        return []
    start += len("## References\n")
    end = text.find("\n# Appendix", start)
    if end < 0:
        end = len(text)
    return [block.strip() for block in re.split(r"\n\s*\n", text[start:end]) if block.strip()]


ADDITIONAL_REFERENCES = [
    "Bangladesh Bureau of Statistics, & UNICEF. (n.d.). *MICS 2025: Data on the situation of children in Bangladesh*. Retrieved August 31, 2026, from https://www.unicef.org/bangladesh/en/data-situation-children-bangladesh",
    "Bangladesh Bureau of Statistics. (2024). *Population and Housing Census 2022: Report on Socio-Economic and Demographic Survey 2023*. https://bbs.portal.gov.bd/pages/static-pages/6922e073933eb65569e27220",
    "China Internet Network Information Center. (2026). *The 57th statistical report on China's internet development*. https://www3.cnnic.cn/n4/2026/0304/c88-11549.html",
    "Department of Statistics Malaysia. (2022). *Key findings: Population and Housing Census of Malaysia 2020*. https://www.dosm.gov.my/portal-main/release-content/launching-of-report-on-the-key-findings-population-and-housing-census-of-malaysia-2020-",
    "Dewan Bahasa dan Pustaka. (n.d.). *Majlis Bahasa Brunei Darussalam-Indonesia-Malaysia (MABBIM)*. https://dbp.gov.my/majlis-bahasa-brunei-darussalam-indonesia-malaysia-mabbim/",
    "Ministry of Education of Japan. (2025). *Second basic plan for promoting reading accessibility*. https://www.mext.go.jp/content/20250328-mxt_kyousei02-000008669_02.pdf",
    "Ministry of Education of Japan. (2026a). *FY2025 survey of pupils requiring Japanese-language instruction*. https://www.mext.go.jp/content/20260525-mxt_kyokoku-000049811_2.pdf",
    "Ministry of Education of Japan. (2026b). *FY2026 textbook catalogue*. https://www.mext.go.jp/a_menu/shotou/kyoukasho/gaiyou/20260401-mxt_kyokasyo02-3.pdf",
    "Ministry of Education of the People's Republic of China. (2021). *Putonghua prevalence reached 80.72% in 2020*. https://www.moe.gov.cn/fbh/live/2021/53486/twwd/202106/t20210602_535078.html",
    "Ministry of Education of the People's Republic of China. (2026). *National education development statistics, 2025*. https://www.moe.gov.cn/jyb_sjzl/sjzl_fztjgb/202607/t20260706_1442870.html",
    "Ministry of Higher Education, Science and Technology, Indonesia. (2026). *Buku statistik pendidikan tinggi tahun 2025*. https://lldikti3.kemdiktisaintek.go.id/wp-content/uploads/2026/05/Buku-Statistik-Pendidikan-Tinggi-Tahun-2025.pdf",
    "Ministry of National Education and New Citizenship, Democratic Republic of the Congo. (n.d.). *School programmes*. https://edu-nc.gouv.cd/national-programmes",
    "Higher Education Commission, Pakistan. (2024). *Annual report 2023–24*. https://www.hec.gov.pk/english/news/AnnualReports/Annual-Report-2023-24.pdf",
    "Higher Education Commission, Pakistan. (n.d.). *Undergraduate education policy*. https://www.hec.gov.pk/english/policies/Pages/UGEP.aspx",
    "Department of Education, Philippines. (2021, June 4). *DepEd records 4.5M early registrants for SY 2021–2022*. https://www.deped.gov.ph/2021/06/04/deped-records-4-5m-early-registrants-for-sy-2021-2022/",
    "UNICEF. (2025, January 24). *At least 30 million children out of school in the Middle East and North Africa*. https://www.unicef.org/mena/press-releases/least-30-million-children-out-school-middle-east-and-north-africa",
    "National Bureau of Statistics of China. (2026). *Monitoring survey report on migrant workers, 2025*. https://www.stats.gov.cn/sj/zxfb/202604/t20260430_1963472.html",
    "OECD. (2024). *Survey of Adult Skills 2023 country note: Japan*. https://www.oecd.org/en/publications/survey-of-adults-skills-2023-country-notes_ab4f6b8c-en/japan_91adbde1-en.html",
    "OpenLogic-id. (2026). *Complete Indonesian Open Logic corpus, release id-olp-0722-20260814*. https://github.com/KokunoYumeto/OpenLogic-id/releases/tag/id-olp-0722-20260814",
    "Program Matematika Indonesia. (2026). *Public curriculum program, release v0.62.6*. https://github.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v0.62.6",
    "Sawaki, Y. (2017). University faculty members' perspectives on English-medium instruction in Japanese higher education. *Asian-Pacific Journal of Second and Foreign Language Education, 2*, Article 10. https://doi.org/10.1186/s40468-017-0043-2",
    "W3C. (2023). *EPUB Accessibility 1.1*. https://www.w3.org/TR/epub-a11y-11/",
    "W3C. (2025). *MathML Core*. https://www.w3.org/TR/mathml-core/",
]


def dedup_references(blocks: list[str]) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for block in blocks:
        key = re.sub(r"\s+", " ", block).casefold()
        if key not in seen:
            seen.add(key)
            output.append(block)
    return sorted(output, key=lambda value: re.sub(r"^[*_]", "", value).casefold())


def main() -> None:
    previous = PAPER.read_text(encoding="utf-8") if PAPER.exists() else ""
    references = dedup_references(old_references(previous) + ADDITIONAL_REFERENCES)
    top100 = read_csv(TOP100)
    top10 = read_csv(TOP10)
    needs = read_csv(NEEDS)
    crosswalk = read_csv(CROSSWALK)
    universe = read_csv(UNIVERSE)
    architectures = read_csv(ARCH)
    supplements = read_csv(SUPPLEMENT)
    joins = read_csv(JOINS)
    high_needs = read_csv(HIGH_NEEDS)
    forward = read_csv(FORWARD)
    scenarios = read_csv(SCENARIOS)
    pipeline = json.loads(PIPELINE_RECEIPT.read_text(encoding="utf-8"))
    companions = json.loads(COMPANION_RECEIPT.read_text(encoding="utf-8"))
    policy_receipt = None
    if POLICY_RECEIPT.exists():
        policy_receipt = json.loads(POLICY_RECEIPT.read_text(encoding="utf-8"))
        if not isinstance(policy_receipt, dict) or policy_receipt.get("schema") != POLICY_RECEIPT_SCHEMA:
            raise ValueError("Allocation-policy receipt schema mismatch")
        for field in ("checks", "inputs", "policy", "diagnostics"):
            if not isinstance(policy_receipt.get(field), dict):
                raise ValueError(f"Allocation-policy receipt {field} must be an object")
        if policy_receipt.get("status") != "PASS":
            raise ValueError("Allocation-policy diagnostic receipt is not PASS")
    if sha256(COMPUTE_RECEIPT) != EXPECTED_COMPUTE_SHA:
        raise ValueError("Indonesian compute receipt hash mismatch")
    compute = json.loads(COMPUTE_RECEIPT.read_text(encoding="utf-8"))

    if len(top100) != 100 or len(top10) != 10:
        raise ValueError("Canonical portfolio counts changed")
    if len({row["entry_id"] for row in top100}) != len(top100):
        raise ValueError("Canonical Top 100 contains duplicate entry IDs")
    if [row["exposure_position"] for row in top100] != [str(position) for position in range(1, len(top100) + 1)]:
        raise ValueError("Canonical Top 100 positions are not consecutive")
    if top10 != top100[:10]:
        raise ValueError("Canonical Top 10 differs from the exact Top 100 prefix")
    if any(not row.get("ordering_basis", "").strip() for row in top100):
        raise ValueError("Canonical portfolio row has no operational ordering basis")
    if [row["entry_id"] for row in needs] != [row["entry_id"] for row in top100]:
        raise ValueError("Needs companion order differs from Top 100")
    if [row["entry_id"] for row in crosswalk] != [row["entry_id"] for row in top100]:
        raise ValueError("Overlap companion order differs from Top 100")
    if pipeline.get("status") != "PASS" or companions.get("status") != "PASS":
        raise ValueError("Upstream validation receipt is not PASS")

    lane_counts = Counter(row["allocation_lane"] for row in top100)
    top100_by_id = {row["entry_id"]: row for row in top100}
    top10_narrative = "; ".join(
        f"{row['exposure_position']}. {row['entry_name']} ({row['entry_id']})"
        for row in top10
    )
    def current_position(entry_id: str) -> str:
        row = top100_by_id.get(entry_id)
        if row:
            return f"position {row['exposure_position']}"
        if policy_receipt:
            for suppressed in policy_receipt.get("diagnostics", {}).get("suppressed_entries", []):
                if suppressed["entry_id"] == entry_id:
                    owners = sorted(set(suppressed.get("package_owners", {}).values()))
                    return "package included through " + ", ".join(
                        f"{owner} at position {top100_by_id[owner]['exposure_position']}" if owner in top100_by_id else owner
                        for owner in owners) + "; not a second duplicate commission"
        return "outside the current Top 100; retained in the full candidate disposition"

    case_position_summary = "; ".join(
        f"{label}: {current_position(entry_id)}"
        for entry_id, label in (
            ("NAT-121", "Bahasa Indonesia"), ("NAT-122", "Mainland Simplified Chinese"),
            ("NAT-124", "Standard Hindi"), ("NAT-125", "Indian Bhojpuri"),
            ("NAT-123", "Japanese"), ("NAT-040", "Indonesian–Malaysian Malay localization"),
        )
    )
    policy_summary = policy_receipt_summary(policy_receipt)
    sensitivity_path = ROOT / "allocation_policy_sensitivity_v1_1.csv"
    sensitivity = read_csv(sensitivity_path)
    sensitivity_by_id = {}
    for item in sensitivity:
        sensitivity_by_id.setdefault(item["entry_id"], {})[item["scenario"]] = item["scenario_position"]
    sensitivity_ids = list(dict.fromkeys([r["entry_id"] for r in top10] + ["NAT-121", "NAT-122", "NAT-123", "NAT-124"]))
    sensitivity_table = md_table(["Action", "Default 6:3:1", "Balanced 1:1:1", "Scale emphasis 8:1:1"],
        [[cid, current_position(cid), sensitivity_by_id.get(cid, {}).get("balanced_1_1_1", "not emitted"),
          sensitivity_by_id.get(cid, {}).get("scale_emphasis_8_1_1", "not emitted")] for cid in sensitivity_ids])
    opportunity_path = ROOT / "opportunity_planning_sensitivity_v1_1.csv"
    opportunity_sensitivity = read_csv(opportunity_path)
    opportunity_by_id = {}
    for item in opportunity_sensitivity:
        opportunity_by_id.setdefault(item["entry_id"], {})[item["scenario"]] = item["scenario_position"]
    opportunity_table = md_table(["Action", "Base", "Cautious", "Favorable", "Range comparison", "Measured-only"],
        [[cid, current_position(cid), *[opportunity_by_id.get(cid, {}).get(label, "not emitted")
          for label in ("cautious", "favorable", "envelope", "measured_only")]] for cid in sensitivity_ids])
    calibration_rows = []
    calibration_paths = [ROOT / "staging" / "opportunity_planning_v1_1" / name
                         for name in ("asia_core.json", "large_profiles.json")]
    for path in calibration_paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        for entry in payload.get("entries", payload.get("evidence", [])):
            dimensions = entry["dimensions"]
            bands = []
            for dim in "RSAN":
                value = dimensions.get(dim, {})
                if value.get("base") is None:
                    bands.append(dim + "U" if value.get("low") is None else f"{dim}{value['low']}–{value['high']}")
                else:
                    bands.append(f"{dim}{value['base']} (range {value['low']}–{value['high']})")
            calibration_rows.append([entry["entry_id"], current_position(entry["entry_id"]), *bands,
                                     entry.get("planning_scope", ""), dimensions.get("R", {}).get("basis", "Unresolved R")])
    calibration_table = md_table(["Action", "Position", "R", "S", "A", "N", "Exact planning scope", "Reader-band reasoning"], calibration_rows)
    reproducibility_paths = [TOP100, TOP10, NEEDS, CROSSWALK, UNIVERSE, ARCH, SUPPLEMENT, JOINS, HIGH_NEEDS, FORWARD, PIPELINE_RECEIPT, COMPANION_RECEIPT]
    if policy_receipt is not None:
        reproducibility_paths.append(POLICY_RECEIPT)
    reproducibility_paths.extend([opportunity_path, *calibration_paths, ROOT / "staging/component_work_ownership_v1_1.json"])
    disposition_counts = Counter(row["disposition"] for row in universe)
    join_profiles = {row["universe_profile_id"] for row in joins if row["observation_id"]}
    forward_by_id: dict[str, list[dict[str, str]]] = {}
    for row in forward:
        forward_by_id.setdefault(row["intervention_id"], []).append(row)

    top10_summary = md_table(
        ["Position", "ID", "Intervention", "Profiles", "Planning R/S/A/N", "Population basis", "First bounded package"],
        [[row["exposure_position"], row["entry_id"], row["entry_name"], row["target_profiles"], "/".join(row.get("opportunity_" + dim, dim + "U") for dim in "RSAN"), row["population_context"], row["first_bounded_package"]] for row in top10],
    )
    top10_needs = md_table(
        ["Position", "ID", "Why now", "Follow-on", "Prerequisite route", "Access design"],
        [[row["exposure_position"], row["entry_id"], row["why_now"], row["follow_on_package"], row["prerequisite_route"], row["delivery_formats"]] for row in top10],
    )
    stage_table = md_table(
        ["Stage", "Binding access question", "Typical first product", "Evaluation unit"],
        [
            ["Pre-primary", "Is mathematical language available in the home/familiar register?", "Oral counting, comparison, shape, pattern, caregiver activities", "Child/caregiver task"],
            ["Primary", "Can a learner repair number, operation, fraction and measurement foundations?", "Diagnostic mastery cycle with worked feedback and complete answers", "Mastered prerequisite"],
            ["Lower secondary", "Can the learner cross into proportional reasoning, algebra, geometry and data?", "Catch-up and academic-register bridge", "Problem set and re-entry path"],
            ["Upper secondary/TVET", "Does the route connect to functions, precalculus, statistics and occupation-specific numeracy?", "Applied bridge, simulations and sector cases", "Course or occupational competency"],
            ["Undergraduate", "Are coherent prerequisite chains and proof practices available?", "Calculus, linear algebra, discrete math, probability and proof sequence", "Course/unit"],
            ["Professional/continuing", "Can readers update health, engineering, finance, management and data practice?", "Versioned applied modules and notebooks", "Competency/use case"],
            ["Postgraduate/doctoral", "Can students enter advanced seminars, monographs and research methods?", "Terminology, proof and literature-navigation bridge", "Course, monograph or seminar"],
            ["Active researcher", "Can specialists read, teach and extend frontier corpora?", "Title-audited canonical source and dependency graph", "Reference work/research uptake"],
        ],
    )
    scenario_table = md_table(
        ["Scenario", "Source alpha tokens", "Editable units", "Fresh input", "Cached input", "Output", "Gross tokens", "Status"],
        [[row["scenario"], row["source_alpha_tokens"], row["editable_units"], row["uncached_input_tokens"], row["cached_input_tokens"], row["output_tokens"], row["gross_tokens"], row["scope_and_caveat"]] for row in scenarios],
    )
    root = compute["root_counters"]
    compute_table = md_table(
        ["Boundary", "Gross input", "Cached input", "Fresh input", "Output", "Total", "Interpretation"],
        [
            ["33 registered owner roots", f"{root['gross_input_tokens']:,}", f"{root['cached_input_tokens']:,}", f"{root['fresh_uncached_input_tokens']:,}", f"{root['output_tokens']:,}", f"{root['total_tokens']:,}", "Exact final cumulative counters; reasoning is already inside output"],
            ["6,726-task descendant-inclusive closure", "not split", "not split", "not split", "not split", f"{compute['descendant_inclusive_closure']['inclusive_total_tokens']:,}", "Includes the 33 roots; never add to the root subtotal"],
        ],
    )
    case_rows = []
    case_ids = {"NAT-121", "NAT-122", "NAT-124", "NAT-125", "NAT-123", "NAT-040"}
    for row in top100:
        if row["entry_id"] not in case_ids:
            continue
        case_rows.append([row["exposure_position"], row["entry_name"], row["existing_supply_state"], row["first_bounded_package"], row["non_overlap_rule"]])
    case_table = md_table(["Pos.", "Case", "Credited existing supply", "Next work", "Non-overlap"], case_rows)

    text = f"""# Allocating AI Translation Compute for Marginal Educational Access

## A global language, interlanguage, accessibility, and open-curriculum portfolio model

**Research report**  
**Version:** 1.1.0  
**Date:** 2026-08-31  
**Model provenance:** OpenAI Codex gpt-5.6-sol, Ultra

## Abstract

AI can reduce the production cost of multilingual educational resources, but a
speaker-count sort does not identify where one more edition creates the most usable
access. This paper defines the relevant outcome as *marginal intelligibility*: the
additional comfortable, practical educational access created for an exact
language/variety/script/territory/learner profile after subtracting current native-
language supply, usable academic-lingua-franca access, completed local work, format
barriers, and overlap with other proposed editions. It joins 477 population
observations and 83 source records to a {len(universe)}-profile global recall universe, {len(architectures)} bridge
or shared-production architectures, {len(supplements)} conservative supplemental observations, {len(joins)}
profile-population join rows, {len(high_needs)} intensive needs studies, 24 normalized needs edges,
and 100 concrete commissioning profiles. Population measures remain typed: territory,
mother tongue, home use, functional use, institutional estimate and learner cohort are
never silently added or treated as one measured harmed-person denominator.

The resulting Top 10 is a transparent operational commissioning sequence, not a
cardinal global welfare leaderboard. In the current canonical order it comprises:
{top10_narrative}.
The current positions of the separately discussed cases are {case_position_summary}.
Every Top-100 row states its stage or unresolved stage scope, first and follow-on
package, prerequisite route, delivery and accessibility requirements, existing supply,
uncertainty, double-count rule and operational ordering basis. Sourced need and supply
evidence are distinct from the policy choices that resolve an uncertain marginal-access
partial order into a useful work sequence.

The corrected analysis does not infer that interlanguages are useless for
mathematics. Formal notation and conventional proof structure plausibly increase
receptive access for expert, symbol-dense tasks. The present evidence cannot turn that
prior into a family-population multiplier: {companions['matched_entries']} Top-100 entries have exact normalized
interlanguage/shared-core relations, but all matched cross-language reach rows remain
non-rankable. Additional demographic reach is unestimated, not demonstrated absent;
no family population is added. Semantic-source, terminology, formula, script and
QA reuse remain separate production opportunities.

The established Indonesian program, with its completed Open Logic corpus and a
registered snapshot of 27 public course roles and 13 production roles, provides the
first measured production anchor. A
bounded 33-root window recorded 83,638,632,771 accounting tokens, of which
81,480,422,656 were cached input, 1,906,326,611 fresh input, and 251,883,504 output.
The descendant-inclusive 6,726-task closure recorded 10,253,232,856,362 cumulative
tokens but includes the roots and lacks category splits. These numbers cannot be
converted directly to money, FLOPs, energy or a universal token-per-page rate. They
show that cumulative program accounting is not translated-prose volume. These
counters do not isolate the cost of translation, critique, correction, builds or
accessibility work, so no stage-specific cost dominance is inferred.

## 1. Research problem

The policy problem is how to allocate a finite amount of model work so that the next
bounded edition produces the largest credible increase in usable education. “Forty
percent lack education in a language they understand” is not itself a language list.
Walter and Benson's (2012, p. 283, Table 14.2) historical calculation assigned
3,741,110,588 people to languages used in formal education and 2,300,263,716 to
languages not used, 61.9% and 38.1% of its covered population. The same table counted
97 languages above ten million speakers: 52 used in education and 45 not used. Those
45 represented 1,120,220,125 people. The chapter prints size bands, not the names of
all 97 languages. The figure is directly related to the language-of-education concern
but does not identify modern commissions. Crawford et al.'s separate set of 96
alphabetic EGRA assessment languages is unrelated and is not substituted for it.

The World Bank's later estimate—about 37% of students in low- and middle-income
countries, roughly 370 million—uses a student/instructional-language universe and asks
whether teaching occurs in a learner's first or best-understood language (World Bank,
2021). It is not Walter and Benson's global language-population denominator. Neither
percentage can be multiplied by every modern language count.

Functional increase in intelligibility is more concrete: a reader who currently
cannot comfortably use the available source can successfully navigate the new
edition, prerequisites, notation, examples, exercises, feedback and delivery format
for the intended task. This can be a child's first numeracy bridge, a vocational
learner's quantitative module, a disabled student's semantic-math edition, or a
researcher's access to a canonical monograph. Education includes research and
continuing self-education; the audience and outcome must be stated rather than erased.

## 2. Formal allocation framework

The controlling recovered formalism uses four separate opportunity dimensions:
`R` (plausible newly comfortable readers), `S` (scarcity of usable material),
`A` (practical accessibility) and `N` (non-overlap with current comfortable access).
Vitality/marginalization `V`, prestige-domain value `P`, production feasibility `F`
and dialect/standardization risk `D` remain separate. R5 means more than 50 million;
R4 10–50 million; R3 1–10 million; R2 100,000–1 million; R1 below 100,000; R0 no
material incremental cohort identified; RU unknown. These are planning categories,
not measured beneficiary counts. A plausible literature-backed judgment is admissible
without experimentally measured uptake. An ordinal label is not multiplied by another
ordinal label as though their product were a cardinal welfare quantity.

The new package-calibration layer specifies R/S/A/N for exact current outputs and
cohorts. A formal-reasoning readership prior cannot silently become an early-years
audience, a national speaker total cannot become a calculus audience, and an optional
future course cannot inflate a smaller first package. S is explicitly generalized
from the earlier advanced-material definition to scarcity of the selected curricular
or format function at its own stage. Because R already discounts existing-language,
edition and modality overlap, N documents that residual rather than subtracting the
same people a second time. The baseline and cautious/favorable bands are disclosed
research judgments. A separate measured-only view makes the difference from observation
visible; it is not the sole legitimate way to make a recommendation.

For a secondary numeric sensitivity, let `P_i` be a source-defined population or learner universe, `L_i`
the probability or bounded share able to use the target written/spoken modality,
`A_i` practical accessibility, `O_i` comfortable overlap with existing editions or
academic lingua francas, and `D_i` the exact remaining content/format deficit. A
within-measure-class marginal-access sensitivity is:

`M_i = P_i × L_i × A_i × (1 − O_i) × D_i`.

Here the indexed `D_i` denotes a content deficit, not the formalism's dialect-risk
band D. Factors must be interpreted conditionally on the same learner universe;
independent marginal percentages cannot identify their intersection. This numeric
diagnostic does not replace the controlling ordinal opportunity framework.

`M_i` is not reported as an observed harmed-person count unless every factor and joint
universe is directly supported. Unknown factors remain intervals; an ignorance
midpoint is labelled a sensitivity, not evidence. Territory, L1, L2, home-language,
institutional and learner-cohort denominators are not cardinally compared as though
they measured the same thing. Sourced observations can support bounded comparisons,
but unknown marginal-access factors leave a partial order with ties or incomparable
profiles. The operational allocation policy produces a usable Top 10 and Top 100 from
that incomplete evidence. Its declared criteria and tie-breaking rules are decision
rules, not additional measurements of educational benefit. Each emitted row retains
its `ordering_basis`; the current policy diagnostic is reported in Section 3.

For a bounded product with lifecycle accounting tokens `C_i`, a compatible efficiency
sensitivity is `E_i = M_i / C_i`. Source tokens, editable units, requests, fresh input,
cached input, output, critique passes, correction, builds, accessibility conversion
and maintenance are recorded separately. Gross accounting tokens are not hardware
compute or price.

For an architecture with a shared semantic core and named outputs *j*:

`C_bundle = C_core + Σ(C_locale,j + C_script,j + C_QA,j)`.

The core has no readers of its own. Direct access is credited only to exact named
outputs after overlap controls. For constructed or naturally intercomprehensible
surfaces, comprehension is a function of direction, script, prior study, expertise,
formal density and task. Mathematics raises the prior for expert receptive reading;
it does not prove novice explanation, word-problem, writing or oral-instruction reach.

## 3. Data and reproducibility

The independent universe contains {len(universe)} profiles and {len(architectures)}
architectures. Of the profiles, {len(join_profiles)} currently have at least one
source-specific population observation and {len(universe) - len(join_profiles)} remain
explicitly unresolved rather than disappearing. Dispositions are:
{', '.join(f'{key}={value}' for key, value in sorted(disposition_counts.items()))}.
The supplemental layer has {len(supplements)} rows and the join has {len(joins)} rows.
All supplement and join rows are gross/context evidence and remain non-rank-ready for
unique marginal access.

The {len(pipeline['steps'])}-step rebuild starts with normalized interlanguage staging and equal-basis
augmentation, then rebuilds candidates, population evidence, needs, exact forward
residuals, the canonical portfolio and its companions. The current pipeline receipt
is `{PIPELINE_RECEIPT.name}` (SHA-256 `{sha256(PIPELINE_RECEIPT)}`). The Top-100
companion receipt is `{COMPANION_RECEIPT.name}` (SHA-256
`{sha256(COMPANION_RECEIPT)}`).

{policy_summary}

The following is a policy-sensitivity experiment, not a confidence interval.
Only the lane allocation cycle changes; the source observations and opportunity
dimensions remain byte-for-byte equivalent in the computation. Positions can
therefore move without any new claim about a population's educational need.
This makes the discretionary part of the recommendations visible.

{sensitivity_table}

The next comparison changes the explicitly supplied opportunity judgments while
keeping the lane schedule fixed. Cautious and favorable select the disclosed ordinal
endpoints; the baseline uses an explicit analyst-selected band when supplied, never
an automatically invented midpoint. Range comparison preserves the full supplied
envelope. Measured-only deliberately withholds provisional judgments from active
comparisons, without claiming zero access. These are conditional planning scenarios,
not statistical confidence intervals or probabilities of success.

{opportunity_table}

{len(calibration_rows)} current packages have source-informed calibrations; Appendix G gives every
scope and band rationale. Other exact-profile formal-reasoning priors are retained
only in their compatible domain. Observation-only census rows remain in the evidence
register but are not manufactured into extra translation commissions. In particular,
a US home-language count does not become a population in the language's country of
origin, and a supply-rich comparison row does not automatically commission another
generic formal-reasoning translation.

The component ownership correction is substantive, not a language exclusion.
NAT-001 owns Bangladesh grades 2–5 recovery; SHC-BN retains caregiver-mediated
preschool learning and Indian Bengali secondary/TVET. NAT-124 owns the Hindi
first-year/methods package; IL-HU retains only the Indian and Pakistani Urdu
outputs. Their R/S/A/N judgments are recalibrated to those active components.
Caregivers are delivery intermediaries, not extra children counted as beneficiaries.
The Malaysian Malay FR-2 core appears once as NAT-040; IL-IDMS remains its
shared-source architecture alias rather than a second commission. Distinct
school catch-up, advanced modules, regional surfaces and Jawi derivatives are
not silently collapsed. SHC-SWAHILI's current population/dispatch scope is
DRC/Uganda only; Tanzania/Kenya are follow-on context, not active first-package
audiences.

OpenStax and Open Logic are auditable, editable baselines for zero-price reuse, not
universal books. Need is measured by population profile × learner stage × subject ×
format × current supply.

## 4. Educational stages and product selection

{stage_table}

The product baseline is teacher-independent without assuming that teachers are
irrelevant: a motivated reader should be able to download once, diagnose prerequisites,
follow worked examples, attempt exercises, inspect complete answers and recover from
errors without an account, LMS or persistent connection. Classroom use remains an
additional valid route. Semantic HTML/MathML, reflowable EPUB, tagged/print PDF,
captions, audio transcripts, keyboard operation, large print and low-bandwidth bundles
are separate access axes, not decoration.

The content universe is wider than mathematics. OpenStax provides an auditable starting
catalog for physics, chemistry, biology, statistics, business, economics, management,
health and social science. Local evidence may instead prioritize financial capability,
workplace numeracy, agriculture, climate/disaster resilience, public health, computing,
data practice, entrepreneurship or research methods. Advanced mathematical corpora such
as EGA, SGA and FGA are educational infrastructure for specialist readers, not mass
foundational substitutes.

## 5. Results: operational commissioning order

{top10_summary}

The canonical Top 10 above is reproduced from `TOP_10.csv`, the exact prefix of
`TOP_100.csv`; it is not a separately fixed shortlist. Its ordering is the operational
policy result, while each row's evidence and uncertainty must be read on their own terms.
Across the broader portfolio, Bangla shares one semantic source but requires
separate Bangladesh and Indian curricula. MSA is a learned written standard and must be
paired with named spoken-language scaffolds. Hindi and Urdu reuse semantics while
keeping Devanagari, Nastaliq, country standards and exact population cells separate.
Kiswahili and Hausa require country and orthography outputs rather than umbrella reach.
Filipino is not every Philippine learner's first language. Vietnamese and Telugu enter
with explicit transition packages. The Indonesian and Chinese cases are at
{current_position('NAT-121')} and {current_position('NAT-122')}, respectively. Their
prior work is credited in the forward deficit rather than used to erase either
profile from opportunity analysis; these facts alone do not prove either position.

### 5.1 What the Top 10 actually need

{top10_needs}

### 5.2 Large-profile completeness and omitted billions

After Indian Bhojpuri was added at the exact 2011 C-16 mother-tongue count of
50,579,447, every direct person-count language observation at or above 50 million in
the current official master maps to the expected universe. The 528,347,193 Census
“Hindi” umbrella is never added to its same-name Hindi component or Bhojpuri and other
children. The remaining billion-scale defect was a modality conflation: written
`zh-Hans-CN` and spoken Putonghua. The latter now has its own profile. Applying the
official rounded 80.72% communication prevalence to the mainland census denominator
gives a derived sensitivity of 1,139,587,786, with a rounding-only interval of
1,139,517,198–1,139,658,374. It is not an official speaker, L1, literacy or academic-
comfort count and is wholly nonadditive with written Chinese and Sinitic profiles
(Ministry of Education of the People's Republic of China, 2021; National Bureau of
Statistics of China, 2021).

Malaysian Malay is also explicit. The 32.4 million Malaysia total is a rounded
territory ceiling, not a Malay-reader count. MABBIM supports strong terminology and
production reuse with Indonesian, not blanket direct comprehension. The named
Indonesian–Malaysian architecture's first action is represented once by NAT-040 at {current_position('NAT-040')}; it begins by measuring and executing
the `ms-Latn-MY` locale delta from the completed Indonesian semantic corpus; Brunei
Rumi and Jawi outputs stay separate (Department of Statistics Malaysia, 2022; Dewan
Bahasa dan Pustaka, n.d.).

### 5.3 Existing work and exact forward residuals

{case_table}

The Indonesian program is established, not a pilot and not a wholly completed
40-course program. The registered public snapshot records Open Logic 722/722, a
1,116-page linked reader, 40 selected course roles, 27 effective published roles and
13 production roles. Its documented page universes—19,745 teaching-package pages,
20,763 selected-corpus working pages and 27,705 rendered-universe pages—are not
interchangeable, and final Indonesian pagination is unknown. Its next package therefore
adds six nonduplicative evidence-to-practice and research courses rather than repeating
Open Logic (OpenLogic-id, 2026; Program Matematika Indonesia, 2026).

Mainland China likewise receives no duplicate Open Logic or algebra. The current exact
state is Open Logic 722/722, *Algebra and Trigonometry 2e* 94/94 and *Calculus Volume
1* 30/55. The first bounded work is CALC1-0031 through CALC1-0055, followed by
Calculus II/III and Statistics, semantic accessibility, a curriculum-aligned school
diagnostic overlay, a 144-hour vocational quantitative bridge, adult/workplace/
financial numeracy, academic re-entry and title-audited frontier work. Six further
STEM titles are candidate scope, not six verified residual books: their completion and
remaining units stay unknown until the exact works and coverage are audited. Official
platform abundance rules out “China lacks native-language education” as the diagnosis;
it does not prove open licences, no-login offline permanence, independent-study closure
or accessibility (Ministry of Education of the People's Republic of China, 2026;
National Bureau of Statistics of China, 2026; W3C, 2023, 2025).

Japan's current placement is {current_position('NAT-123')} in the operational sequence; this is not a
measured estimate of its relative marginal benefit. Free compulsory textbooks, multiple
approved series and high PISA/TIMSS attainment make another ordinary school textbook a
low-additionality comparator. Concrete overlapping residual cohorts include 84,759
pupils requiring Japanese-language instruction, 353,970 compulsory-school pupils
meeting the nonattendance definition, and roughly 10% of the PIAAC age-16–65
population at or below numeracy Level 1. Upper-secondary accessible-audio coverage was
reported far below elementary coverage, and a bounded MEXT audit found independent
screen-reader operation inconsistent. The commission is a Japanese Open Mathematics
Access and Research Bridge: open offline self-study, easy Japanese/ruby/multilingual
scaffolding, semantic mathematics, adult re-entry, proof/foreign-language reading and
title-audited frontier translations (Ministry of Education of Japan, 2025, 2026a,
2026b; OECD, 2024; Sawaki, 2017).

## 6. Interlanguage and shared-core result

The overlap companion finds exact normalized relations for
{companions['matched_entries']} of 100 portfolio entries. No matched matrix row is
currently rankable for cross-language demographic reach, so the cross-language credit
is conservatively zero. This is not an estimate of zero mathematical utility. It means
that family ceilings, short cloze tests, names and scripts are not multiplied into
reader populations without directed task evidence.

The production recommendation remains positive where reuse is coherent: Bangla,
Hindi–Urdu, Arabic, Indonesian–Malaysian Malay, BCMS, Nguni, Sotho–Tswana, Persian–
Dari–Tajik, Punjabi, Scandinavian, Turkic-branch and other packages can share semantic
source, terminology, formulas, accessibility structure, rendering tests and QA while
publishing named outputs. Interslavic remains a useful supplementary mathematics-
reading and terminology experiment. Its observed short professional-text result does
not establish sustained mathematical comprehension or blanket Slavic coverage.

The next research design should cross expertise (novice, undergraduate, specialist),
formal density (expository prose, worked example, theorem-proof, notation-heavy
reference), direction, script, prior study and task (gist, exact proposition,
error-detection, problem solution). This tests the user's mathematically plausible
hypothesis directly instead of importing a general-prose prior.

## 7. Compute evidence and planning

{compute_table}

The 33-root total partitions as cached + fresh + cache-write gross input, with
cache-write zero. Reasoning output is already contained in output. The closure total is
an inclusive superset, not a descendant add-on. A tail scan found 7,970 distinct
cumulative-token progressions, an evidenced lower bound rather than a complete request
count. These boundaries are the reason “a million gross tokens” cannot be converted
directly into a million fresh tokens or into weekly monetary spend.

For a fixed 722-unit Open Logic source, the pre-existing planning scenarios are:

{scenario_table}

Those scenarios are hypothetical workflow coefficients, not measured Indonesian usage.
They demonstrate how source preparation, per-unit calls, critique, correction, build QA
and retry allowance can change gross workload. Future grants should report at least:
source tokens, editable units, fresh input, cached input, output, model/request boundary,
formula/structure checks, build/render checks, accessibility conversion, corrections and
maintenance. Package comparisons should use the same boundary.

## 8. Grant and implementation design

1. **Use open, editable sources.** Global reuse requires lawful translation,
   correction, redistribution, printing and preservation at zero learner price.
2. **Select an exact profile and exact deficit.** Record variety, script, territory,
   stage, subject, format, current supply and non-overlap before production.
3. **Build once, localize explicitly.** Reuse semantic cores and toolchains while
   retaining named locale/script outputs and zero automatic demographic reach.
4. **Make self-study a baseline.** Include diagnostics, prerequisites, worked examples,
   exercises, complete answers, misconception feedback and download-once delivery.
5. **Treat accessibility as content.** Semantic math, keyboard operation, captions,
   transcripts, reflow, large print, Braille/speech compatibility and low-bandwidth
   bundles are independently commissioned and checked.
6. **Maintain separate foundational and frontier lanes.** A small specialist corpus
   can have high research and teaching leverage without masquerading as mass reach.
7. **Instrument the lifecycle.** Persist source identities, terminology decisions,
   formula/structure checks, builds, renders, model critiques, corrections, token
   categories and public-byte receipts.
8. **Evaluate use without creating a human-dependent release gate.** Learning and
   comprehension evidence should inform later revisions; complete deterministic work
   remains publishable while uncertainty is disclosed.

## 9. Limitations

Population observations span incompatible measures and years. Territory ceilings are
not reader counts; L1 is not literacy; home use is not academic comfort; an official
language is not universal competence; and a learner cohort is not a language
population. Several expected profiles remain unresolved. Top-100 positions are a
decision-aid sequence, not a measured global welfare ordering.

Needs evidence is deepest for {len(high_needs)} high-reach profiles. Other Top-100 rows use explicit
provisional local-need fits from registered curriculum portfolios and are labelled as
such. A package recommendation can be reasonable before a full local supply census,
but it cannot be described as a demonstrated absence. Clinical, legal, financial,
agricultural and warning information requires local versioning.

AI mathematical competence improves semantic checking relative to blind machine
translation, but it is not infallibility or linguistic authority. Source-faithful
formula and structure checks, terminology evidence, independent model critique,
compilation, rendering and versioned correction remain necessary deterministic parts
of the workflow. Missing human evidence is uncertainty, not a reason to halt a
complete provisional edition.

The compute audit is unusually large but not a universal cost model. Its earliest
Open Logic work is outside the registered boundary, cached inputs dominate the root
total, the descendant closure lacks category splits, and page universes include
different source/reference roles. No cost, energy or carbon claim is derived.

## 10. Conclusion

An evidence-conscious educational translation program need not choose between large
languages, small endangered languages, interlanguages, accessibility and advanced
research. It separates their outcomes and builds a portfolio. Large exact profiles
can create vast aggregate access; regional and endangered editions create depth and
prestige-domain function; semantic accessibility reaches readers whom language count
misses; and research-frontier translation supports advanced education and knowledge
production.

The current Top 10 is the canonical sequence reproduced in Section 5, not a claim that
its members are the ten empirically best uses of compute. The broader portfolio credits
completed Indonesian and Chinese work, retains Japan's specific access needs, and keeps
their operational positions distinct from unmeasured marginal benefit. The analysis
explicitly represents Indian Bhojpuri, separates spoken Putonghua from written Chinese,
and exposes Malaysian Malay as its own output. It uses
interlanguage mechanisms where they save production work and gives direct readership
only where evidence supports comprehension. Most importantly, it says what to build:
from caregiver numeracy and mastery recovery through TVET, statistics, financial and
workplace capability, undergraduate proof, professional updating, semantic access and
canonical research corpora.

The next production decision can now be bounded and auditable: choose one emitted
profile, take its stated first package rather than a generic textbook, measure exact
source units and workflow tokens, publish open offline accessible outputs, and update
the evidence after use. That is a tractable path from AI compute to additional
educational access.

## Model and contributor provenance

Research synthesis, analysis, deterministic data generation, drafting and document
production used **OpenAI Codex gpt-5.6-sol, Ultra**. The model identity does not replace
the authorities cited below. Original source authors, OpenStax/Open Logic contributors,
public-program contributors and human contributors retain their credits. First-party
paper and data are intended for CC BY 4.0 release; first-party code is intended for
MIT release; third-party material retains its own terms.

## References

{"\n\n".join(references)}

# Appendix A. Full ordered Top 100: population, stage, and product

{md_table(
    ["Pos.", "ID", "Intervention", "Profiles", "Scope", "Population context", "Stages", "First package", "Evidence", "Operational ordering basis"],
    [[row["exposure_position"], row["entry_id"], row["entry_name"], row["target_profiles"], row["territory_or_scope"], row["population_context"], row["education_stages"], row["first_bounded_package"], row["package_evidence_status"], row["ordering_basis"]] for row in top100],
)}

# Appendix B. Full ordered Top 100: continuation, prerequisites, and access

{md_table(
    ["Pos.", "Intervention", "Follow-on", "Prerequisite route", "Delivery", "Teacher-independent requirements", "Accessibility", "Non-overlap"],
    [[row["exposure_position"], row["entry_name"], row["follow_on_package"], row["prerequisite_route"], row["delivery_formats"], row["teacher_independent_requirements"], row["accessibility_requirements"], row["non_overlap_rule"]] for row in top100],
)}

# Appendix C. Interlanguage/shared-core crosswalk and exact forward work

{md_table(
    ["Pos.", "ID", "Matrix rows", "Mechanisms", "Credited cross-language reach (not estimated utility)", "Compute reuse", "Current completion", "Forward deficit", "Next action"],
    [[row["exposure_position"], row["entry_id"], row["matched_matrix_row_ids"] or "none", row["matched_mechanism_classes"] or "none", row["current_cross_language_demographic_reach_credit"], row["shared_core_compute_reuse"], row["current_direct_component_completion_overlap"], row["forward_component_deficit_D"], row["forward_next_nonduplicative_actions"]] for row in crosswalk],
)}

# Appendix D. Expected global profiles and dispositions

{md_table(
    ["ID", "Profile", "Tag", "Kind", "Region", "Band", "Disposition", "Population warning", "Next action"],
    [[row["universe_profile_id"], row["display_name"], row["profile_tag"], row["profile_kind"], row["region"], row["threshold_band"], row["disposition"], row["population_identity_warning"], row["next_nonduplicative_action"]] for row in universe],
)}

# Appendix E. Bridge and shared-production architectures

{md_table(
    ["ID", "Architecture", "Mechanism", "Named outputs", "Diagnostic universe", "Direct reach status", "Compute reuse", "Exclusions", "Next measurement"],
    [[row["architecture_id"], row["display_name"], row["mechanism_class"], row["named_outputs"], row["diagnostic_universe"], row["direct_reader_reach_status"], row["compute_reuse_status"], row["mandatory_exclusions"], row["next_measurement"]] for row in architectures],
)}

# Appendix F. Reproducibility identities

{md_table(
    ["Artifact", "Rows", "Bytes", "SHA-256"],
    [[path.name, len(read_csv(path)) if path.suffix == ".csv" else "—", path.stat().st_size, sha256(path)] for path in reproducibility_paths],
)}

The source-to-claim research memos are `JAPAN_EQUAL_BASIS_RESEARCH_20260831.md`
(SHA-256 `{sha256(ROOT / 'JAPAN_EQUAL_BASIS_RESEARCH_20260831.md')}`),
`SIMPLIFIED_CHINESE_RESIDUAL_RESEARCH_20260831.md` (SHA-256
`{sha256(ROOT / 'SIMPLIFIED_CHINESE_RESIDUAL_RESEARCH_20260831.md')}`),
`GLOBAL_LARGE_PROFILE_AND_MODALITY_AUDIT_20260831.md` (SHA-256
`{sha256(ROOT / 'GLOBAL_LARGE_PROFILE_AND_MODALITY_AUDIT_20260831.md')}`), and
`INDONESIAN_PROGRAM_COMPUTE_AND_SCALE_AUDIT_20260831.md` (SHA-256
`{sha256(ROOT / 'INDONESIAN_PROGRAM_COMPUTE_AND_SCALE_AUDIT_20260831.md')}`).

# Appendix G. Scope-calibrated planning judgments

The following are literature-constrained commissioning judgments, not measured
intervention effects or guaranteed positive floors. The population facts and
curriculum/supply sources constrain the reasoning; the residual audience is an
explicit inference. R already incorporates overlap, and no additional N multiplier
is applied. Exact source chains, confidence, assumptions and threshold tests are
preserved in `asia_core.json` and `large_profiles.json`.

{calibration_table}

Sources: Several source checks materially changed package scope. The DRC ministry already
lists Kiswahili early-grade pupil books, workbooks, teacher guides and literacy
materials, so the proposal targets specified feedback, accessible/offline and
regional-variety gaps rather than claiming all such textbooks absent (Ministry of
National Education and New Citizenship, n.d.). UNICEF's 30-million figure concerns
out-of-school children aged 5–18 across 12 MENA countries, not 30 million Arabic
readers (UNICEF, 2025). Final BBS/UNICEF MICS 2025 reports foundational numeracy for
39.2% of ages 7–14, reading for 50.2%, and ECE attendance for 16.6% at ages 36–59
months; those outcome/attendance measures are not a causal count of language exclusion
(Bangladesh Bureau of Statistics & UNICEF, n.d.).

Source: The Indonesian 2025 higher-education report extraction gives 10,754,154 enrolled
students; the live portal shows a different snapshot near ten million. The 33.9-MB
report was not page-audited in this bounded pass, so the exact extraction remains
provisional and the snapshots are not averaged; only their order of magnitude informs
the recommendation. Pakistan's indexed 2022-23 enrollment anchor is 1,964,147, not a
measure of Urdu readership (Higher Education Commission, 2024, p. 202). Indian Hindi
evidence is not independent Urdu evidence. These are source limits, not zero-access
findings.
"""

    PAPER.write_text(text.rstrip() + "\n", encoding="utf-8")
    print(json.dumps({
        "paper": str(PAPER),
        "bytes": PAPER.stat().st_size,
        "sha256": sha256(PAPER),
        "top100_rows": len(top100),
        "references": len(references),
        "lane_counts": dict(sorted(lane_counts.items())),
    }, indent=2))


if __name__ == "__main__":
    main()
