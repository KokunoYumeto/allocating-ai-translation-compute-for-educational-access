#!/usr/bin/env python3
"""Build the v1.1 Top 10 and Top 100 commissioning exposure portfolio.

The output is ordered because the research brief requires an actionable queue,
but the order is a stratified allocation decision, not a claim that mixed
population denominator classes form one cardinal welfare score.  Direct reader
reach and shared-core compute reuse are recorded separately.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from allocation_policy_v1_1 import rank_portfolio, work_component_key
from opportunity_planning_v1_1 import assemble_context, file_identity, load_calibrations, scenario_context
from component_scope_v1_1 import CONTRACT_PATH, attach_components, component_need_edges, load_contract


ROOT = Path(__file__).resolve().parents[1]
# Legacy table is used only as an ID-to-display/observation descriptor for
# entries that predate the normalized candidate table.  It never seeds order,
# needs, population values, or recommendation status.
LEGACY_DESCRIPTOR = ROOT / "table5_top100_members.csv"
CANDIDATES = ROOT / "candidate_interventions_master.csv"
OBSERVATIONS = ROOT / "population_observations_master.csv"
POPULATION_EDGES = ROOT / "candidate_population_edge_curation_queue.csv"
EXPANSION = ROOT / "staging" / "expand_rankable_candidates" / "candidate_expansion.csv"
CURRICULUM = ROOT / "curriculum_portfolios.csv"
EXPECTED = ROOT / "staging" / "global_expected_universe" / "expected_language_profiles_v1_1.csv"
JOINS = ROOT / "staging" / "global_expected_universe" / "expected_profile_population_joins_v1_1.csv"
NEEDS = ROOT / "staging" / "high_reach_education_needs" / "high_reach_education_needs_v1_1.csv"
NEEDS_EDGES = ROOT / "staging" / "high_reach_education_needs" / "high_reach_needs_portfolio_edges_v1_1.csv"
ARCH = ROOT / "staging" / "global_expected_universe" / "bridge_shared_core_hypotheses_v1_1.csv"
RECOVERED_GAPS = ROOT / "model_inputs" / "GLOBAL_GAP_REGISTER.csv"
OUT_DIR = ROOT / "staging" / "authoritative_exposure_portfolio_v1_1"
OUT_TOP100 = ROOT / "TOP_100.csv"
OUT_TOP10 = ROOT / "TOP_10.csv"
OUT_TOP100_ALIAS = ROOT / "top100_commissioning_portfolio_v1_1.csv"
OUT_TOP10_ALIAS = ROOT / "top10_commissioning_wave_v1_1.csv"
OUT_VALIDATION = ROOT / "top100_commissioning_portfolio_v1_1_validation.json"

FIELDS = [
    "exposure_position", "wave", "allocation_lane", "entry_id", "entry_type",
    "entry_name", "target_profiles", "territory_or_scope", "component_profile_ids",
    "population_context", "population_denominator_classes", "population_source_ids",
    "direct_reader_reach_claim", "shared_core_compute_reuse", "education_stages",
    "needs_profile_ids", "named_output_profile_ids",
    "why_now", "first_bounded_package", "follow_on_package",
    "prerequisite_route", "existing_supply_state", "delivery_formats",
    "teacher_independent_requirements", "accessibility_requirements",
    "delivery_and_accessibility", "non_overlap_rule", "package_evidence_status",
    "recommendation_status", "ordering_basis", "evidence_confidence",
    "source_urls", "uncertainty",
]


PROFILE_GROUPS = {
    "SHC-BN": ["GLB-010", "GLB-011"],
    "IL-AR": ["GLB-031", "GLB-032", "GLB-033"],
    "IL-HU": ["GLB-007", "GLB-008", "GLB-009"],
    "SHC-SWAHILI": ["GLB-036"],
    "SHC-HAUSA": ["GLB-037"],
    "IL-PUNJABI": ["GLB-019", "GLB-020"],
    "IL-PDT": ["GLB-034"],
    "IL-IDMS": ["GLB-054"],
    "NAT-033": ["GLB-046"],
    "NAT-028": ["GLB-041"],
    "NAT-003": ["GLB-012"],
    "NAT-121": ["GLB-039"],
    "NAT-122": ["GLB-002"],
    "NAT-123": ["GLB-043"],
    "NAT-065": ["GLB-048"],
    "NAT-066": ["GLB-049"],
    "NAT-069": ["GLB-037"],
    "NAT-072": ["GLB-038"],
    "NAT-125": ["GLB-052"],
}


# The recall universe can describe a wider architecture than its first action.
# These exact outputs alone may supply that action's population/ownership views;
# other country observations remain in the source register and follow-on context.
FIRST_PACKAGE_PROFILE_SCOPES = {
    "SHC-SWAHILI": ("swc-Latn-CD", "swh-Latn-UG"),
}


PACKAGE_OVERRIDES = {
    "SHC-BN": {
        "entry_name": "Bangla Bangladesh–India shared-source package",
        "entry_type": "pluricentric_shared_core_with_named_outputs",
        "target_profiles": "bn-Beng-BD; bn-Beng-IN",
        "territory_or_scope": "Bangladesh; West Bengal and other Indian Bengali contexts",
        "education_stages": "pre-primary through primary recovery; secondary/TVET transition",
        "why_now": "Two very large, separately measured Bangla populations have different immediate deficits but can reuse one semantic source and script toolchain.",
        "first_bounded_package": "Produce in parallel: a 24-week Bangladesh caregiver/ECE and grades 2–5 mastery-recovery system, and an Indian Bengali secondary/TVET workshop-mathematics, safety, coding, finance and entrepreneurship bridge.",
        "follow_on_package": "Separate Bangladesh disaster-resilience and Indian Bengali first-year university overlays; then postgraduate research methods.",
        "shared_core_compute_reuse": "High same-script semantic, terminology, formula, accessibility and QA reuse; two separately localized curricula and examples.",
        "direct_reader_reach_claim": "Only the two named outputs receive direct reach; no locale-neutral Bangla audience is counted.",
        "non_overlap_rule": "Do not add a shared-core audience to the Bangladesh and India population cells; never count the same reader twice.",
        "existing_supply_state": "Current school books exist in both jurisdictions; the gap is mastery/continuity in Bangladesh and TVET/tertiary transition in India.",
        "source_urls": "https://www.unicef.org/bangladesh/en/data-situation-children-bangladesh ; https://banglarshiksha.wb.gov.in/Frontend/e_textbook",
    },
    "IL-AR": {
        "entry_name": "Modern Standard Arabic core with named spoken-language scaffolds",
        "entry_type": "learned_written_standard_with_locale_scaffolds",
        "target_profiles": "arb-Arab core; Egyptian, Levantine, Iraqi, Gulf, Maghrebi, Yemeni, Sudanese and Hassaniya layers",
        "territory_or_scope": "Arabic-using countries, separately localized",
        "education_stages": "early literacy; emergency education; secondary/TVET; professional and research methods",
        "why_now": "The gross Arabic universe is very large, educational diglossia is documented, and one formal core can support many named local oral and glossary layers without pretending they are one spoken language.",
        "first_bounded_package": "In parallel, build fully vowelled leveled ECE–grade 3 MSA with local-spoken narration and offline accelerated literacy/science/health/WASH packages for crisis-affected country profiles.",
        "follow_on_package": "Country-specific disciplinary literacy, TVET and research-method paths in health, climate/agriculture, finance, computing, statistics and reproducibility.",
        "shared_core_compute_reuse": "High formal-register, RTL, terminology and source reuse; every spoken scaffold remains a named output.",
        "direct_reader_reach_claim": "No direct 400M MSA-reader claim; direct reach is assigned only to separately evidenced country/stage outputs.",
        "non_overlap_rule": "Never award blanket MSA comprehension or collapse Arabic varieties and non-Arabic home-language communities.",
        "existing_supply_state": "Substantial but fragmented Arabic material exists; sequencing, country localization, accessibility, offline delivery and diglossic scaffolding remain uneven.",
        "source_urls": "https://www.unesco.org/en/world-arabic-language-day ; https://documents1.worldbank.org/curated/en/909741624654308046/pdf/Advancing-Arabic-Language-Teaching-and-Learning-A-Path-to-Reducing-Learning-Poverty-in-the-Middle-East-and-North-Africa.pdf",
    },
    "IL-HU": {
        "entry_name": "Hindi–Urdu shared semantic core with three named script/locale outputs",
        "entry_type": "dual_script_pluricentric_shared_core",
        "target_profiles": "hi-Deva-IN; ur-Aran-IN; ur-Aran-PK",
        "territory_or_scope": "India and Pakistan",
        "education_stages": "first-year tertiary; professional/continuing; postgraduate research methods",
        "why_now": "The exact named population cells are large and the semantic/formula core is highly reusable, while Devanagari/Nastaliq and academic-register differences prohibit a single reader surface.",
        "first_bounded_package": "Produce separate Hindi and Urdu first-year physics, chemistry, biology, statistics, computing, economics and management bridges with research design, R/Python and open-science methods.",
        "follow_on_package": "Current health, agriculture, cyber-finance, SME and postgraduate reproducibility modules, maintaining distinct India/Pakistan examples and law.",
        "shared_core_compute_reuse": "High semantic, formula, exercise and terminology-graph reuse; separate scripts, render QA and locale registers.",
        "direct_reader_reach_claim": "Direct reach belongs to hi-Deva-IN, ur-Aran-IN and ur-Aran-PK separately; no cross-script comprehension multiplier is used.",
        "non_overlap_rule": "Exclude Bhojpuri and other Hindi-umbrella returns; never sum Hindi/Urdu functional umbrellas with same-name L1 cells.",
        "existing_supply_state": "Hindi school supply is extensive; Urdu supply varies. The strongest shared residual is tertiary/professional/research continuity.",
        "source_urls": "https://pmevidya.education.gov.in/diksha.html ; https://nptel.ac.in/translation",
    },
    "SHC-SWAHILI": {
        "entry_name": "Kiswahili DRC grades 1–3 and Uganda P4 package",
        "entry_type": "learned_lingua_franca_shared_core_with_named_outputs",
        "target_profiles": "swc-Latn-CD; swh-Latn-UG",
        "territory_or_scope": "Named Kiswahili-using DRC regions (grades 1–3); Uganda (P4 Kiswahili L2)",
        "education_stages": "DRC grades 1–3 literacy/numeracy and Uganda P4 Kiswahili-L2 support",
        "why_now": "The first action addresses exact DRC early-grade self-study, regional-variety and accessibility gaps plus Uganda P4 L2 delivery; country curricula and L1/L2 situations remain distinct.",
        "first_bounded_package": "Reuse/adapt the DRC ministry's listed Kiswahili grades 1–3 and literacy materials where rights permit; complete missing worked feedback, science/health, semantic/offline and regional-variety components with French bridges. Add separate Uganda P4 L2 self-study scripts and audio; do not duplicate existing schoolbooks.",
        "follow_on_package": "Follow-on context only: separately scope Tanzania swh-Latn-TZ and Kenya swh-Latn-KE secondary/advanced outputs; their populations do not enter this first action. Extend separately evidenced country routes into Kiswahili↔English/French biology, chemistry, climate/agriculture, health, computing and finance, then TVET and statistics/R/Python/open-science paths.",
        "prerequisite_route": "DRC grades 1–3 literacy/numeracy entry -> exact regional-variety and French-bridge support -> missing worked feedback; Uganda P4 Kiswahili-L2 entry -> self-study scripts and offline audio.",
        "shared_core_compute_reuse": "High standard-core reuse, but every country/DRC regional surface is separately rendered and audited.",
        "direct_reader_reach_claim": "Only DRC grades 1–3 and Uganda P4 are current outputs. Uganda's territory count is a gross ceiling, not a P4 or Kiswahili-reader count; the exact DRC learner denominator remains unresolved. Neither the global 200M headline nor Tanzania/Kenya populations enter this action's dispatch.",
        "non_overlap_rule": "Do not use East African Standard Kiswahili as blanket coverage for DRC varieties or non-Kiswahili L1 communities. Tanzania/Kenya outputs are follow-on context only and add no current first-package audience.",
        "existing_supply_state": "DRC lists Kiswahili grades 1–3 pupil books, workbooks, teacher guides and literacy packages. Exact usable-file, self-study, regional-variety and format gaps remain separate from Uganda L2 provision. Follow-on comparison context: Tanzania/Kenya already have substantial material.",
        "source_urls": "https://edu-nc.gouv.cd/national-programmes ; https://www.unesco.org/en/articles/kiswahili-bridge-cultural-diversity-dialogue-and-digital-innovation ; https://kiswahili.eac.int/wp-content/uploads/2022/10/EAKC-Strategic-Plan-FINAL.pdf",
    },
    "SHC-HAUSA": {
        "entry_name": "Hausa boko Nigeria–Niger package with optional established Ajami layers",
        "entry_type": "cross_border_shared_core_with_named_orthographies",
        "target_profiles": "ha-Latn-NG; ha-Latn-NE; optional locally established ha-Arab layers",
        "territory_or_scope": "Nigeria and Niger; cross-border communities",
        "education_stages": "foundational literacy/numeracy; secondary/TVET; practical professional learning",
        "why_now": "Hausa has a very large L1/L2 universe and unusually strong cross-border reuse potential, but script, literacy and country-curriculum reach are not one number.",
        "first_bounded_package": "Build boko structured literacy/numeracy with diagnostics and Hausa↔English in Nigeria / Hausa↔French in Niger; add print, radio, IVR and optional established Ajami parallel text/audio.",
        "follow_on_package": "Secondary/TVET science, agriculture, public health, computing, mobile-money safety, microenterprise, livestock/water and solar/GSM trades; then tertiary statistics/R/Python.",
        "shared_core_compute_reuse": "High semantic core reuse; country orthographies and every Ajami layer stay explicit and separately validated.",
        "direct_reader_reach_claim": "No 94M written-reader claim; L1 and total-user estimates remain alternative gross universes.",
        "non_overlap_rule": "Never invent one universal Ajami or convert oral user estimates into written educational reach.",
        "existing_supply_state": "Foundational Hausa resources exist, but progression, offline feedback and advanced/practical supply remain thinner.",
        "source_urls": "https://assets.cambridge.org/97810091/24300/excerpt/9781009124300_excerpt.pdf ; https://education.gov.ng/e-learning-resources/",
    },
    "NAT-033": {
        "entry_name": "Filipino–English STEM–Kabuhayan package",
        "entry_type": "natural_language_locale_output",
        "target_profiles": "fil-Latn-PH with replaceable home-language audio/glossary tracks",
        "territory_or_scope": "Philippines",
        "education_stages": "grades 7–12; Alternative Learning System; TVET; first-year tertiary",
        "why_now": "A national-scale ceiling, uneven household connectivity and existing offline infrastructure make a practical, extensible package more useful than another generic textbook.",
        "first_bounded_package": "Produce 120 Filipino–English micro-lessons in health, personal finance/SME management, agriculture/climate/disaster, core science, computing/data/AI and cybersecurity for grades 7–12, ALS and TESDA.",
        "follow_on_package": "Open science, biostatistics, public health, programming/data, accounting/management and climate-smart agriculture/renewable-energy spine.",
        "shared_core_compute_reuse": "Reuse semantic sources and STARBOOKS-style offline packaging; home-language tracks are separate outputs.",
        "direct_reader_reach_claim": "The 109,035,343 census total is a territory ceiling, not Filipino L1 or comfortable-reader reach.",
        "non_overlap_rule": "Filipino is not every learner's first language; do not count replaceable home-language tracks as one Filipino audience.",
        "existing_supply_state": "DepEd, TESDA, UPOU and STARBOOKS exist; the marginal package should integrate, localize and work offline rather than duplicate them.",
        "source_urls": "https://psa.gov.ph/content/2020-census-population-and-housing-2020-cph-population-counts-declared-official-president ; https://stii.dost.gov.ph/starbooks/",
    },
    "NAT-028": {
        "entry_name": "Vietnamese TVET–university and research-method spine",
        "entry_type": "natural_language_locale_output",
        "target_profiles": "vi-Latn-VN",
        "territory_or_scope": "Vietnam",
        "education_stages": "secondary/TVET; undergraduate; postgraduate and continuing professional",
        "why_now": "Vietnam has major existing school and OER supply, but the documented fragmentation and TVET–university discontinuity make a coherent, offline sequence a high marginal use of compute.",
        "first_bounded_package": "Build five coherent courses: data/programming/AI/cybersecurity; climate-smart rice/aquaculture/green skills; public health/evidence appraisal; MSME accounting/digital finance; applied biology/chemistry with low-cost labs.",
        "follow_on_package": "Quarterly frontier-to-field briefs plus postgraduate research design, causal inference, systematic review and reproducibility.",
        "shared_core_compute_reuse": "Single locale output with strong reuse of open labs, code and data assets across subjects.",
        "direct_reader_reach_claim": "The 89M published speaker estimate is a gross context, not a measured underserved-reader cohort.",
        "non_overlap_rule": "Vietnamese material does not replace exact oral/home-language overlays for minoritized early-years learners.",
        "existing_supply_state": "National digital textbooks and VOER exist; coherence, portability, offline use and applied progression remain the target.",
        "source_urls": "https://vnfoundation.org/en/vietnam-open-educational-resources/ ; https://documents1.worldbank.org/curated/en/099000005132229736/pdf/P174258045156b0060972302fec6a3015b8.pdf",
    },
    "NAT-003": {
        "entry_name": "Telugu applied STEM and tertiary-transition package",
        "entry_type": "natural_language_locale_output",
        "target_profiles": "te-Telu-IN with Andhra Pradesh and Telangana overlays",
        "territory_or_scope": "Andhra Pradesh and Telangana, India",
        "education_stages": "secondary/TVET; first-year tertiary; professional continuing education",
        "why_now": "A large exact L1 population and substantial school supply point to the school-to-TVET/first-year transition, not another primary textbook series.",
        "first_bounded_package": "Produce applied secondary/TVET/first-year STEM, coding, financial safety and entrepreneurship with Telugu–English terminology and offline simulations.",
        "follow_on_package": "Agriculture/climate, health and SME continuing education, then postgraduate research methods and reproducibility.",
        "shared_core_compute_reuse": "Reuse source semantics and labs across two state overlays; each curriculum crosswalk remains distinct.",
        "direct_reader_reach_claim": "The 80,912,459 census component is an L1 gross ceiling, not a measured affected learner cohort.",
        "non_overlap_rule": "Do not average Andhra Pradesh and Telangana outcomes or treat one state curriculum as the other.",
        "existing_supply_state": "Both states have substantial school stocks; audited vocational output is much smaller.",
        "source_urls": "https://www.scert.telangana.gov.in/Home.aspx/Pdf/Displaycontent.aspx?encry=ammkNW4%2Fgx+NeApstGPX+A%3D%3D ; https://nimi.gov.in/web/pdf/Annual%20Report-2025_English%20Version.pdf",
    },
    "NAT-121": {
        "entry_name": "Bahasa Indonesia Evidence-to-Practice and Research Core",
        "entry_type": "existing_program_nonduplicative_extension",
        "target_profiles": "id-Latn-ID",
        "territory_or_scope": "Indonesia",
        "education_stages": "undergraduate; professional/continuing; postgraduate and active researcher",
        "why_now": "The language choice is strongly supported by a 248.5M functional-language census measure and by the already completed 722-module Open Logic corpus and 40-course program infrastructure.",
        "first_bounded_package": "Add six nonduplicative courses: research design/open science; applied statistics and causal reasoning in R/Python; reproducible data/AI/cybersecurity; evidence appraisal; public health/One Health; climate-smart agriculture/disaster risk.",
        "follow_on_package": "Maintained professional updates for MSME finance/management, health CPD, renewable energy/water, agriculture/aquaculture and quarterly frontier briefs.",
        "shared_core_compute_reuse": "Reuse the established terminology, build, QA and offline infrastructure; Malaysian Malay localization is a separate later output.",
        "direct_reader_reach_claim": "248,501,794 is age-5+ ability to speak Indonesian, not written academic comfort or the number newly helped.",
        "non_overlap_rule": "Do not duplicate the completed Open Logic corpus or already covered 40-course roles; commission only exact residual or new-domain packages.",
        "existing_supply_state": "Indonesian program, not pilot: Open Logic 722/722 and a 40-course mathematics program with public and active-production roles.",
        "source_urls": "https://sensus.bps.go.id/topik/tabular/sp2022/196 ; https://github.com/KokunoYumeto/program-matematika-indonesia",
    },
    "NAT-122": {
        "entry_name": "Mainland Simplified Chinese accessibility and frontier residual",
        "entry_type": "strong_supply_exact_forward_residual",
        "target_profiles": "zh-Hans-CN",
        "territory_or_scope": "Mainland China",
        "education_stages": "secondary through undergraduate; accessibility; professional and research frontier",
        "why_now": "The gross opportunity is enormous, but existing supply and completed local corpora make exact residuals and accessibility—not generic translation—the efficient target.",
        "first_bounded_package": "Finish the exact 25-unit Calculus I residual (CALC1-0031 through CALC1-0055), then Calculus II/III and Statistics; produce semantic HTML/MathML, accessible EPUB, tagged-PDF, audio/transcript and low-bandwidth offline derivatives for completed corpora.",
        "follow_on_package": "Add a four-band school diagnostic overlay, a 144-hour vocational quantitative bridge, adult/workplace/financial numeracy and academic re-entry, then title-audited frontier mathematics.",
        "shared_core_compute_reuse": "Very high standardized written Chinese/toolchain reuse; Taiwan/Hong Kong locale outputs remain separate.",
        "direct_reader_reach_claim": "1,411,778,724 is a mainland territory ceiling; Putonghua communication and simplified-character use are separate measures.",
        "non_overlap_rule": "Do not claim coverage of Wu, Yue vernacular, Xiang, Hakka, Taigi or minority-language communities; do not duplicate complete Open Logic or algebra.",
        "existing_supply_state": "Large national platform supply; local Open Logic 722/722 and Algebra and Trigonometry 94/94 complete; Calculus I 30/55 with 25 exact units remaining; Open Logic has a deterministically evidenced accessibility residual.",
        "source_urls": "https://www.stats.gov.cn/english/PressRelease/202105/t20210510_1817187.html ; https://www.moe.gov.cn/fbh/live/2025/77791/mtbd/202512/t20251231_1425330.html ; https://www.moe.gov.cn/jyb_sjzl/sjzl_fztjgb/202607/t20260706_1442870.html ; https://www3.cnnic.cn/n4/2026/0304/c88-11549.html",
    },
}


BRIDGE_PACKAGE = {
    "IL-PUNJABI": ("Punjabi synchronized two-script production", "pa-Guru-IN; pa-Arab-PK", "Produce synchronized secondary/TVET and first-year STEM sources with separate Gurmukhi and Pakistan Perso-Arabic locale outputs; resolve the Pakistan census label before narrower ISO attribution."),
    "IL-PDT": ("Persian–Dari–Tajik shared-source package", "fa-Arab-IR; prs-Arab-AF; tg-Cyrl-TJ", "Reuse one semantic source for separate Iranian Persian, Afghan Dari and Tajik Cyrillic tertiary/professional paths; keep scripts, terminology and national curricula distinct."),
    "IL-NGUNI": ("Nguni shared-source production", "zu-Latn-ZA; xh-Latn-ZA; ss-Latn-ZA; nr-Latn-ZA", "Build a shared source and terminology graph, then publish named language outputs for secondary/TVET science, health, finance and computing."),
    "IL-SOTHO": ("Sotho–Tswana shared-source production", "nso-Latn-ZA; tn-Latn-ZA; st-Latn-ZA", "Build named Sepedi, Setswana and Sesotho secondary/TVET outputs from one semantic source; do not publish a synthetic reader surface."),
    "IL-MANDING": ("Manding named-standard production", "bm-Latn-ML; man-Latn; dyu-Latn-CI; named N'Ko derivatives", "Produce foundational/TVET practical-learning sources with separate national orthographies and optional named N'Ko outputs."),
    "IL-SQUECHUA": ("Southern Quechua named-standard production", "quy-Latn-PE; quz-Latn-PE; quh-Latn-BO", "Build a shared mathematics/science source with separate official orthographies and territory curricula; do not collapse Quechua into one language."),
    "IL-IDMS": ("Indonesian–Malaysian Malay localization", "id-Latn-ID; ms-Latn-MY; named Brunei/Jawi derivatives", "Use the completed Indonesian semantic corpus to measure and execute the Malaysian Malay locale delta; keep Jawi derivatives separate."),
    "IL-BCMS": ("BCMS common-source localization", "bs-Latn; hr-Latn; cnr-Latn; sr-Latn; sr-Cyrl", "Produce named standard outputs from one common source, preserving terminology, script and curriculum differences."),
    "IL-ROM": ("Romance localized reuse architecture", "es; pt-BR; fr; it; ro; ca named outputs", "Reuse terminology and QA across named editions; treat any constructed reader bridge as an unranked research hypothesis."),
    "IL-TURKIC": ("Turkic branch production architecture", "separate Oghuz, Kipchak and Karluk outputs", "Reuse semantic and terminology work within branches while commissioning only named language outputs."),
    "IL-GERM": ("Targeted Germanic reuse architecture", "Dutch–Afrikaans first; Low German, Plautdietsch, Yiddish and other residuals separate", "Test targeted West/North profiles and reuse, not one pan-Germanic reader surface."),
    "IL-SCAND": ("Mainland Scandinavian localization package", "da-DK; nb-NO; nn-NO; sv-SE", "Share source and terminology while publishing separate national and Nynorsk outputs."),
    "IL-ISV": ("Interslavic supplementary mathematics bridge", "isv-Latn; isv-Cyrl plus native-language outputs", "Continue as a supplementary mathematical-reading and terminology experiment; do not substitute it for Russian, Ukrainian or other native editions."),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def wave(position: int) -> str:
    if position <= 10:
        return "wave_1_top10"
    return f"wave_{1 + (position - 1) // 10:02d}_mixed_allocation_lanes"


def format_number(value: str) -> str:
    if not value:
        return "unresolved"
    try:
        number = float(value)
    except ValueError:
        return value
    if number.is_integer():
        return f"{int(number):,}"
    return f"{number:,.3f}".rstrip("0").rstrip(".")


def join_unique(rows: list[dict[str, str]], field: str, separator: str = " | ") -> str:
    values: list[str] = []
    for row in rows:
        value = row.get(field, "").strip()
        if value and value not in values:
            values.append(value)
    return separator.join(values)


def population_display(item: dict[str, str]) -> str:
    low, base, high = (item.get("population_low", ""), item.get("population_base", ""), item.get("population_high", ""))
    if base and low and high and low != high:
        value = f"{format_number(base)} (interval {format_number(low)}–{format_number(high)})"
    elif base:
        value = format_number(base)
    elif low and high:
        value = f"{format_number(low)}–{format_number(high)}"
    elif low:
        value = f">={format_number(low)}"
    else:
        value = "unresolved"
    return value


def curriculum_package(
    entry_id: str,
    candidate: dict[str, str],
    descriptor: dict[str, str],
    curriculum: dict[str, dict[str, str]],
) -> tuple[str, str, str, str, str, str]:
    raw_candidate_unit = candidate.get("curriculum_unit", "")
    portfolio_id = raw_candidate_unit if raw_candidate_unit in curriculum else ""
    if not portfolio_id:
        embedded = [known for known in curriculum if known in raw_candidate_unit]
        portfolio_id = embedded[0] if len(embedded) == 1 else ""
    if not portfolio_id:
        portfolio_id = descriptor.get("recommended_openstax_next_product", "")
    spec = curriculum.get(portfolio_id, {})
    if not portfolio_id or not spec:
        return "", "", "", "", "", "unresolved_no_registered_curriculum_package"
    work = spec.get("exact_content", "")
    if not work:
        raise ValueError(f"Registered curriculum {portfolio_id} has no exact_content")
    depth = candidate.get("adaptation_depth", "") or descriptor.get("recommended_openstax_depth", "") or spec.get("preferred_depth", "")
    formats = candidate.get("formats", "") or "AX-HTML;AX-PDF;AX-OFFLINE"
    package = (
        f"Produce the registered {portfolio_id} {spec.get('portfolio_name', candidate.get('curriculum_work', 'curriculum package'))} "
        f"for this exact named output: {work}; adaptation {depth}; include placement diagnostics, complete worked answers, editable source, and download-once delivery."
    )
    prerequisites = spec.get("prerequisite_portfolio", "")
    route = (
        f"Diagnostic entry -> {prerequisites} -> {portfolio_id}."
        if prerequisites else f"Diagnostic entry and any source-stated prerequisites -> {portfolio_id}."
    )
    teacher = "Placement checks, explicit prerequisite repair, complete worked examples and answers, self-check feedback, and no required teacher or live platform."
    accessibility = "Semantic headings and mathematics/MathML, keyboard navigation, captions/transcripts for media, reflow, tested fonts and text extraction, low-bandwidth assets, and printable fallback."
    evidence = "registered_curriculum_package_provisional_local_need_fit"
    return package, route, formats, teacher, accessibility, evidence


def first_package_population_rows(entry_id: str, rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Restrict action evidence without changing the broader source observations."""
    allowed = FIRST_PACKAGE_PROFILE_SCOPES.get(entry_id)
    if not allowed:
        return list(rows)
    return [row for row in rows if (
        row.get("source_profile_tag") or row.get("profile_tag") or row.get("target_profile", "")
    ).strip() in allowed]


def first_package_needs_edges(entry_id: str, edges: list[dict[str, str]]) -> list[dict[str, str]]:
    """Keep needs provenance, but expose only the current named output keys."""
    allowed = FIRST_PACKAGE_PROFILE_SCOPES.get(entry_id)
    if not allowed:
        return [dict(edge) for edge in edges]
    scoped = []
    for edge in edges:
        outputs = [tag.strip() for tag in edge.get("named_output_profile_id", "").split(";")
                   if tag.strip() in allowed]
        if outputs:
            scoped.append({**edge, "named_output_profile_id": ";".join(dict.fromkeys(outputs))})
    return scoped


def observation_action_has_exact_scope(
    candidate: dict[str, str],
    observation: dict[str, str],
    needs_edges: list[dict[str, str]],
    needs_by_id: dict[str, dict[str, str]],
) -> bool:
    """A census-derived profile is not an action until a separate need defines one.

    Output locale and beneficiary territory are separate: a Marshallese standard
    may serve an explicitly defined US cohort, but the US observation cannot be
    relabelled as a Marshall Islands population. A source-script mapping alone
    does not establish this production or learner scope.
    """
    entry_id = candidate.get("intervention_id", "")
    target = candidate.get("variety_or_register", "").strip()
    territory = observation.get("territory", "").strip().casefold()
    if not observation or not target or not territory:
        return False
    for edge in needs_edges:
        if (edge.get("portfolio_entry_id") != entry_id or edge.get("edge_status") != "resolved"
                or edge.get("edge_role") == "cross_locale_compute_reuse_only"):
            continue
        need = needs_by_id.get(edge.get("needs_profile_id", ""), {})
        named_outputs = {tag.strip() for tag in edge.get("named_output_profile_id", "").split(";")}
        need_outputs = {tag.strip() for tag in need.get("target_profiles", "").split(";")}
        need_territories = {value.strip().casefold() for value in need.get("territory_or_scope", "").split(";")}
        if (target in named_outputs and target in need_outputs and territory in need_territories
                and all(need.get(field, "").strip() for field in (
                    "first_priority_stage", "first_package", "need_evidence", "source_urls", "delivery_spec",
                ))):
            return True
    return False


def observation_candidate_dispositions(
    candidates: dict[str, dict[str, str]],
    observations: dict[str, dict[str, str]],
    expected: dict[str, dict[str, str]],
    needs_edges: list[dict[str, str]],
    needs_by_id: dict[str, dict[str, str]],
) -> dict[str, dict[str, str]]:
    """Keep mechanically surfaced observation rows as evidence, not quota filler."""
    owners_by_profile: dict[str, list[str]] = defaultdict(list)
    for entry_id, candidate in candidates.items():
        if not entry_id.startswith("OBS-") and candidate.get("target_type") != "accessibility":
            owners_by_profile[candidate.get("variety_or_register", "").strip()].append(entry_id)
    for profile_id, profile in expected.items():
        owners_by_profile[profile.get("profile_tag", "").strip()].append(profile_id)

    dispositions: dict[str, dict[str, str]] = {}
    for entry_id, candidate in candidates.items():
        if not entry_id.startswith("OBS-"):
            continue
        observation_id = entry_id.removeprefix("OBS-")
        observation = observations.get(observation_id, {})
        if observation_action_has_exact_scope(candidate, observation, needs_edges, needs_by_id):
            continue
        treatment = candidate.get("profile_ranking_treatment", "")
        control = candidate.get("profile_negative_control_status", "")
        owners = sorted(set(owners_by_profile.get(candidate.get("variety_or_register", "").strip(), [])))
        if not observation:
            disposition = "observation_reference_unresolved_not_a_commission"
        elif "deprioritize_generic_translation" in treatment or control.startswith("negative_control"):
            disposition = "observation_only_supply_rich_control"
        elif "rank only after scarcity/non-overlap evidence" in treatment or control.startswith("comparison_control"):
            disposition = "observation_only_scarcity_overlap_control"
        elif owners:
            disposition = "observation_evidence_for_existing_profile_not_a_new_commission"
        else:
            disposition = "observation_only_pending_independent_action_definition"
        dispositions[entry_id] = {
            "entry_id": entry_id,
            "disposition": disposition,
            "owner": ";".join(owners) or "population_observations_master.csv",
            "observation_id": observation_id,
            "source_territory": observation.get("territory", "unresolved"),
            "source_learner_stratum": observation.get("learner_stratum", "unresolved"),
            "target_profile_context": candidate.get("variety_or_register", ""),
            "profile_ranking_treatment": treatment,
            "profile_negative_control_status": control,
            "scope_rule": "Retain the unaltered census observation and source cohort; a matching edition profile is context only, not permission to transfer its population to the edition's origin country or create another edition.",
            "next_action": "Use the observation as source-defined evidence. Register a separate exact output, beneficiary locale/cohort, stage, need and package before treating it as an independent commission; supply-rich controls require a specific residual rather than generic FR-2.",
        }
    return dispositions


def main() -> None:
    work_contract = load_contract()
    descriptors = {r["intervention_id"]: r for r in read_csv(LEGACY_DESCRIPTOR)}
    candidates = {r["intervention_id"]: r for r in read_csv(CANDIDATES)}
    observations = {r["observation_id"]: r for r in read_csv(OBSERVATIONS)}
    expansions = {r["candidate_id"]: r for r in read_csv(EXPANSION)}
    population_edges = read_csv(POPULATION_EDGES)
    expansion_aliases = {}
    expansions_for_candidate = defaultdict(list)
    for xid, expansion in expansions.items():
        existing_id = expansion.get("existing_intervention_id", "")
        # An existing-language link is not automatically a locale alias (e.g.
        # Samoan in New Zealand and Samoa). Collapse only identical exact tags.
        if existing_id in candidates and candidates[existing_id].get("variety_or_register") == expansion.get("target_profile"):
            expansion_aliases[xid] = existing_id
            expansions_for_candidate[existing_id].append(expansion)
    curriculum = {r["portfolio_id"]: r for r in read_csv(CURRICULUM)}
    for pid, spec in curriculum.items():
        if not spec.get("exact_content") or not spec.get("preferred_depth"):
            raise ValueError(f"Curriculum {pid} missing exact content/depth")
        if spec.get("prerequisite_portfolio") and spec["prerequisite_portfolio"] not in curriculum:
            raise ValueError(f"Curriculum {pid} prerequisite is unregistered")
    expected = {r["universe_profile_id"]: r for r in read_csv(EXPECTED)}
    joins = read_csv(JOINS)
    needs_rows = read_csv(NEEDS)
    needs_by_id = {r["needs_profile_id"]: r for r in needs_rows}
    needs_edges = read_csv(NEEDS_EDGES)
    arch_rows = read_csv(ARCH)
    candidate_dispositions = []
    candidate_ids = set()
    observation_dispositions = observation_candidate_dispositions(
        candidates, observations, expected, needs_edges, needs_by_id,
    )
    for cid, candidate in candidates.items():
        if cid in observation_dispositions:
            candidate_dispositions.append(observation_dispositions[cid])
        elif candidate.get("target_type") == "accessibility":
            candidate_dispositions.append({"entry_id": cid, "disposition": "cross_cutting_accessibility_axis", "owner": "all_applicable_language_outputs"})
        elif candidate.get("target_type") == "natural_language_baseline":
            candidate_dispositions.append({"entry_id": cid, "disposition": "completed_program_baseline_not_new_commission", "owner": "NAT-121"})
        else:
            candidate_ids.add(cid)
    for xid in expansions:
        if xid in expansion_aliases:
            candidate_dispositions.append({"entry_id": xid, "disposition": "exact_profile_alias", "owner": expansion_aliases[xid]})
        else:
            candidate_ids.add(xid)
    for pid, profile in expected.items():
        owners = sorted(cid for cid in set(profile["candidate_ids"].split(";")) & candidate_ids
                        if cid not in PROFILE_GROUPS or pid in PROFILE_GROUPS[cid])
        if owners:
            candidate_dispositions.append({"entry_id": pid, "disposition": "represented_by_registered_candidate", "owner": ";".join(owners)})
        else:
            candidate_ids.add(pid)
    candidate_ids.update(PACKAGE_OVERRIDES)
    candidate_ids.update(BRIDGE_PACKAGE)
    arch_by_candidate: dict[str, dict[str, str]] = {}
    for a in arch_rows:
        for cid in a["candidate_ids"].split(";"):
            if cid:
                arch_by_candidate[cid] = a

    needs_by_portfolio_entry: dict[str, list[dict[str, str]]] = defaultdict(list)
    for edge in needs_edges:
        if edge["edge_status"] != "resolved" or not edge["portfolio_entry_id"] or edge["edge_role"] == "cross_locale_compute_reuse_only":
            continue
        need = needs_by_id[edge["needs_profile_id"]]
        if need not in needs_by_portfolio_entry[edge["portfolio_entry_id"]]:
            needs_by_portfolio_entry[edge["portfolio_entry_id"]].append(need)

    profile_by_candidate: dict[str, list[str]] = defaultdict(list)
    for pid, profile in expected.items():
        for cid in profile["candidate_ids"].split(";"):
            if cid:
                profile_by_candidate[cid].append(pid)

    def profiles_for(entry_id: str) -> list[str]:
        if entry_id in work_contract:
            return work_contract[entry_id]["component_profile_ids"]
        if entry_id in PROFILE_GROUPS:
            return PROFILE_GROUPS[entry_id]
        if entry_id.startswith("GLB-"):
            return [entry_id]
        return profile_by_candidate.get(entry_id, [])

    def population_rows_for(entry_id: str) -> list[dict[str, str]]:
        pids = profiles_for(entry_id)
        selected = [
            r for r in joins
            if r["universe_profile_id"] in pids
            and any(r[field] for field in ("population_low", "population_base", "population_high"))
        ]
        if entry_id in candidates and candidates[entry_id].get("target_type") == "natural_language":
            target = candidates[entry_id].get("variety_or_register", "")
            # sw is used for the national standard in the registered TZ/KE
            # candidates; this explicit alias is not a Swahili-family union.
            source_tag = {"sw-Latn-TZ": "swh-Latn-TZ", "sw-Latn-KE": "swh-Latn-KE"}.get(target, target)
            selected = [r for r in selected if r.get("candidate_id") == entry_id
                        or r.get("source_profile_tag") == source_tag
                        or r.get("profile_tag") == target]
        if not selected:
            selected = [observations[edge["observation_id"]] for edge in population_edges
                        if edge["intervention_id"] == entry_id and edge["automatic_curation_status"] in
                        {"eligible_exact_gross_ceiling", "eligible_exact_direct_access_floor"}]
        descriptor = descriptors.get(entry_id, {})
        if not selected and descriptor.get("population_observation_ids"):
            for observation_id in descriptor["population_observation_ids"].split(";"):
                if observation_id in observations:
                    selected.append(observations[observation_id])
        if not selected and entry_id in expansions:
            selected.append(expansions[entry_id])
        if not selected:
            selected.extend(expansions_for_candidate.get(entry_id, []))
        selected = first_package_population_rows(entry_id, selected)
        # Same observation may arrive through multiple explicit profile edges.
        selected = list({(r.get("observation_id", ""), r.get("universe_profile_id", "")): r for r in selected}.values())
        return sorted(selected, key=lambda r: (r.get("universe_profile_id", ""), r.get("observation_id", r.get("candidate_id", ""))))

    def population_for(entry_id: str) -> tuple[str, str, str, str]:
        selected = population_rows_for(entry_id)
        if not selected:
            return (
                "unresolved—no comparable source-defined population count",
                "unresolved",
                "",
                "No direct reach is assigned until an exact source-defined population universe is registered.",
            )
        selected.sort(key=lambda r: (
            r.get("universe_profile_id", ""),
            r.get("denominator_class", r.get("measure_type", r.get("population_measure", ""))),
            r.get("observation_id", r.get("candidate_id", "")),
        ))
        contexts = []
        classes = []
        sources = []
        for item in selected[:8]:
            label = item.get("display_name") or item.get("language_label") or item.get("resolved_edition_name") or item.get("target_name") or entry_id
            if entry_id in FIRST_PACKAGE_PROFILE_SCOPES:
                label = item.get("candidate_target_name") or label
            value = population_display(item)
            denominator = item.get("denominator_class") or item.get("measure_type") or item.get("population_measure") or "source_defined_person_observation"
            year = item.get("reference_date_or_year") or item.get("population_reference_year") or "date unresolved"
            contexts.append(f"{label}: {value} [{denominator}; {year}]")
            classes.append(denominator)
            sources.extend(x for x in [item.get("observation_id", ""), item.get("source_id", ""), item.get("population_source_id", "")] if x)
        suffix = "" if len(selected) <= 8 else f"; plus {len(selected) - 8} additional typed observations"
        return (
            " | ".join(contexts) + suffix,
            ";".join(dict.fromkeys(classes)),
            ";".join(dict.fromkeys(sources)),
            "Listed measures are alternatives or separate territories unless the source explicitly establishes disjointness; they are not summed into direct reach.",
        )

    output: list[dict[str, str]] = []
    unresolved_ids: list[str] = []
    for entry_id in sorted(candidate_ids):
        custom = dict(PACKAGE_OVERRIDES.get(entry_id, {}))
        cand = dict(candidates.get(entry_id, {}))
        old = descriptors.get(entry_id, {})
        expansion = expansions.get(entry_id, {})
        if expansion and not cand:
            prior = candidates.get(expansion.get("existing_intervention_id", ""), {})
            cand = {"target_name": expansion["resolved_edition_name"], "target_type": "natural_language",
                    "variety_or_register": expansion["target_profile"], "territory_scope": expansion["territory"],
                    "curriculum_unit": prior.get("curriculum_unit") or old.get("recommended_openstax_next_product") or "FR-1",
                    "source_ids": expansion.get("profile_source_ids", ""), "notes": expansion.get("priority_basis", ""),
                    "existing_local_status": "External and local supply not yet assessed for this exact output.",
                    "overlap_rule": expansion.get("additivity_rule", "")}
        glb = expected.get(entry_id, {})
        entry_profile_ids = profiles_for(entry_id)
        if not glb and len(entry_profile_ids) == 1:
            glb = expected.get(entry_profile_ids[0], {})
        entry_edges = [
            dict(edge) for edge in needs_edges
            if edge["edge_status"] == "resolved" and edge["portfolio_entry_id"] == entry_id
            and edge["edge_role"] != "cross_locale_compute_reuse_only"
        ]
        entry_edges = first_package_needs_edges(entry_id, entry_edges)
        for edge in entry_edges:
            if edge["portfolio_entry_id"] != entry_id:
                exact_target = cand.get("variety_or_register", "")
                if exact_target in edge["named_output_profile_id"].split(";"):
                    edge["named_output_profile_id"] = exact_target
        entry_edges = component_need_edges(entry_id, work_contract, entry_edges)
        needs = list({edge["needs_profile_id"]: needs_by_id[edge["needs_profile_id"]] for edge in entry_edges}.values())
        architecture = arch_by_candidate.get(entry_id, {})
        registered_package, registered_prerequisite, registered_formats, registered_teacher, registered_accessibility, registered_evidence = curriculum_package(
            entry_id, cand, old, curriculum
        )

        if entry_id in BRIDGE_PACKAGE:
            bname, bprofiles, bpackage = BRIDGE_PACKAGE[entry_id]
            custom = {
                "entry_name": bname,
                "entry_type": "shared_core_compute_architecture",
                "target_profiles": bprofiles,
                "territory_or_scope": cand.get("territory_scope", architecture.get("diagnostic_universe", "named territories")),
                "education_stages": "stage-specific named outputs; exact first stage follows the component needs audit",
                "why_now": architecture.get("compute_reuse_status", "Potential production reuse without a blanket direct-reach claim."),
                "first_bounded_package": bpackage,
                "follow_on_package": architecture.get("next_measurement", "Measure reused source, localization and QA tokens per named output."),
                "shared_core_compute_reuse": architecture.get("compute_reuse_status", "Potential shared-source reuse; not a reader count."),
                "direct_reader_reach_claim": architecture.get("direct_reader_reach_status", "Named outputs only; no blanket bridge reach."),
                "non_overlap_rule": architecture.get("mandatory_exclusions", cand.get("overlap_rule", "No blanket regional coverage.")),
                "existing_supply_state": cand.get("existing_local_status", "mixed or unresolved"),
                "source_urls": "",
            }

        if entry_id.startswith("SHC-") and not custom:
            raise SystemExit(f"Missing custom shared-core definition: {entry_id}")

        if entry_id == "IL-IDMS":
            custom.update({
                "target_profiles": "ms-Latn-MY",
                "territory_or_scope": "Malaysia; Indonesian is the source-reuse program, not the newly served audience",
                "education_stages": "upper-secondary, undergraduate and research reference; exact Malaysian course alignment required",
                "existing_supply_state": expected["GLB-054"]["existing_supply_state"] + " Source-reuse asset: completed Indonesian Open Logic 722/722.",
                "prerequisite_route": "Malaysian learner diagnostic -> exact source-stated prerequisites -> localized Malaysian Malay module; do not require completion of the Indonesian program.",
                "delivery_formats": "Open offline HTML/MathML, EPUB and print PDF in ms-Latn-MY; separately scoped Jawi derivatives.",
                "source_urls": "https://dbp.gov.my/majlis-bahasa-brunei-darussalam-indonesia-malaysia-mabbim/ ; https://www.dosm.gov.my/portal-main/release-content/launching-of-report-on-the-key-findings-population-and-housing-census-of-malaysia-2020-",
            })
        if entry_id == "NAT-072":
            custom.update({
                "education_stages": "adult/community practical numeracy with oral access; written pathway separately scoped",
                "first_bounded_package": "Produce Naija/Nigerian Pidgin audio and basic-phone practical numeracy modules with spoken worked examples, money/measurement/data tasks and optional aligned Latin-script transcripts; do not presume standardized written readership.",
                "follow_on_package": "Extend into locally evidenced livelihood, financial-safety and health-data modules; use explicit orthography and reading-demand profiles before a text-heavy algebra course.",
                "prerequisite_route": "Oral number and measurement diagnostic -> short spoken worked examples -> practice with answers -> optional transcript/text bridge.",
                "delivery_formats": "Downloadable audio, radio/IVR scripts, basic-phone prompts and low-bandwidth transcript/PDF companions.",
                "why_now": expected["GLB-038"]["disposition_basis"],
            })

        custom.update(work_contract.get(entry_id, {}).get("row_overrides", {}))
        entry_name = custom.get("entry_name") or cand.get("resolved_edition_name") or cand.get("target_name") or glb.get("display_name") or old.get("intervention_name")
        if not entry_name:
            unresolved_ids.append(entry_id)
            entry_name = f"UNRESOLVED {entry_id}"

        target_profiles = (
            custom.get("target_profiles") or cand.get("variety_or_register") or glb.get("profile_tag") or old.get("target_profiles")
            or cand.get("script_or_profile", "")
        )
        territory = (
            custom.get("territory_or_scope") or cand.get("territory_scope") or glb.get("region") or old.get("territory_or_scope", "")
        )
        pop_context, pop_classes, pop_sources, pop_uncertainty = population_for(entry_id)

        first_package = (
            custom.get("first_bounded_package") or join_unique(needs, "first_package")
            or (
                old.get("needs_first_package", "")
                if old.get("needs_assignment_status") in {"audited_primary_or_official_proxy", "directly_audited_stage_specific_residual"}
                else ""
            )
            or registered_package or glb.get("next_nonduplicative_action")
            or "Resolve the exact language, script and orthography against registered source evidence, then scope the FR-1 proof/logic foundations diagnostic; this row is a profile-resolution action, not a completed content commission."
        )
        follow_on = (
            custom.get("follow_on_package") or join_unique(needs, "follow_on_package")
            or (
                f"After the bounded {cand.get('curriculum_unit', old.get('recommended_openstax_next_product', 'registered'))} package, extend only after an itemized local supply and stage audit; preserve the same named profile and non-overlap rules."
                if registered_package else ""
            )
            or "After target/profile resolution, select a bounded content package from the registered source inventory."
        )
        existing_supply = (
            custom.get("existing_supply_state") or join_unique(needs, "existing_supply") or glb.get("existing_supply_state")
            or cand.get("existing_local_status", "External/local supply has not been assessed for this exact output.")
        )
        if existing_supply.strip().casefold() == "missing":
            existing_supply = "No edition recorded in the bounded project inventory; external/local educational supply has not been assessed by this field."
        stages = (
            custom.get("education_stages") or join_unique(needs, "first_priority_stage")
            or (
                old.get("needs_evidence_stage", "")
                if old.get("needs_assignment_status") in {"audited_primary_or_official_proxy", "directly_audited_stage_specific_residual"}
                else ""
            )
            or (
                "secondary through first-year tertiary"
                if cand.get("curriculum_unit", old.get("recommended_openstax_next_product", "")).startswith(("MV", "SB"))
                else "upper-secondary through undergraduate formal reasoning"
                if cand.get("curriculum_unit", old.get("recommended_openstax_next_product", "")).startswith("FR")
                else "target/profile resolution before stage-specific production"
            )
        )
        why_now = (
            custom.get("why_now") or join_unique(needs, "need_evidence") or (
                old.get("needs_observed_evidence", "")
                if old.get("needs_assignment_status") != "territory_proxy_only_not_a_content_commission" else ""
            )
            or glb.get("disposition_basis") or cand.get("notes", "")
        )
        delivery_formats = custom.get("delivery_formats") or join_unique(needs, "delivery_spec") or registered_formats or "research dossier and source inventory only until the target profile is resolved"
        teacher_independent = custom.get("teacher_independent_requirements") or join_unique(needs, "teacher_independent_requirements") or registered_teacher or "For any later content edition: diagnostics, complete worked answers, self-check feedback and no mandatory teacher or live service."
        accessibility = custom.get("accessibility_requirements") or join_unique(needs, "accessibility_requirements") or registered_accessibility or "For any later edition: semantic structure and mathematics, keyboard/reflow support, tested fonts/text extraction, captions/transcripts and printable low-bandwidth fallback."
        prerequisite_route = custom.get("prerequisite_route") or join_unique(needs, "prerequisite_route") or registered_prerequisite or "Resolve the exact target, population and existing supply before assigning a curriculum prerequisite chain."
        delivery = " | ".join(value for value in [delivery_formats, teacher_independent, accessibility] if value)
        non_overlap = (
            custom.get("non_overlap_rule") or join_unique(needs, "non_overlap_rule") or glb.get("population_identity_warning")
            or cand.get("overlap_rule", "Do not assign blanket mutual-intelligibility coverage.")
        )
        reuse = custom.get("shared_core_compute_reuse") or (
            architecture.get("compute_reuse_status") if architecture else "Single named output; source, notation and accessibility tooling may be reused, but no extra reader reach is inferred."
        )
        reuse += " Package-specific token savings are unmeasured unless separately quantified in a named compute receipt."
        direct_claim = custom.get("direct_reader_reach_claim") or pop_uncertainty

        if entry_id.startswith("ACC-") or entry_id == "OBS-GRG-PL-008":
            status = "commission_bounded_signed_language_access_after_exact_language_and_lexicon_scope"
        elif entry_id in {"GLB-004", "GLB-006", "GLB-045", "GLB-033"}:
            status = "resolve_exact_profile_and_population_before_reader_surface"
        elif entry_id.startswith("IL-") and entry_id not in {"IL-AR", "IL-HU", "IL-PUNJABI", "IL-PDT", "IL-IDMS", "IL-NGUNI", "IL-SOTHO", "IL-MANDING", "IL-SQUECHUA"}:
            status = "shared_source_or_research_architecture_not_blanket_direct_reach"
        elif glb.get("disposition") == "supply_rich_negative_control" or entry_id in {"NAT-122", "NAT-123", "GLB-044"}:
            status = "commission_exact_accessibility_professional_or_frontier_residual_only"
        elif needs:
            status = "commission_documented_bounded_nonduplicative_package"
        else:
            status = "commission_after_exact_work_stage_format_scope"

        source_urls = custom.get("source_urls") or join_unique(needs, "source_urls", " ; ") or (
            old.get("needs_source", "") if old.get("needs_assignment_status") != "territory_proxy_only_not_a_content_commission" else ""
        ) or cand.get("source_ids", "") or glb.get("source_basis", "") or expansions.get(entry_id, {}).get("profile_source_ids", "") or pop_sources or "candidate_interventions_master.csv: exact candidate registration; independent local-need evidence unresolved"
        caveats = " ".join(x for x in [
            pop_uncertainty,
            join_unique(needs, "caveat"),
            old.get("needs_caveat", ""),
            glb.get("population_identity_warning", ""),
        ] if x)
        confidence = custom.get("evidence_confidence") or join_unique(needs, "evidence_confidence") or (
            "population provenance registered; local need fit provisional; marginal increment unmeasured" if pop_sources
            else "population/profile evidence unresolved; local need fit provisional; marginal increment unmeasured"
        )
        entry_type = custom.get("entry_type") or cand.get("target_type") or glb.get("profile_kind") or old.get("intervention_type", "language_profile")
        if custom.get("package_evidence_status"):
            package_evidence_status = custom["package_evidence_status"]
        elif needs:
            package_evidence_status = "literature_backed_high_reach_need"
        elif registered_package:
            package_evidence_status = registered_evidence
        elif glb:
            package_evidence_status = "profile_resolution_or_exact_residual_action_from_expected_universe"
        else:
            package_evidence_status = "profile_resolution_action_local_need_unresolved"

        source_resolution_flags = [cand.get("rankability_status", ""), cand.get("profile_resolution_status", "")]
        source_resolution_flags.extend(r.get("gross_rankability", "") for r in ([expansion] if expansion else expansions_for_candidate.get(entry_id, [])))
        requires_resolution = any(flag == "discovery_only_target_resolution_required" or flag.startswith("requires_")
                                  and flag != "requires_exact_population_join" or "exact_variety_unresolved" in flag
                                  for flag in source_resolution_flags)
        if requires_resolution:
            first_package = ("First resolve the exact variety, script, orthography and learner locale using the registered source/profile evidence; "
                             "retain any broader census count as a ceiling only. Then scope the appropriate registered curriculum package; "
                             "this is a bounded target-resolution commission, not authorization to translate into a fabricated common standard.")
            status = "bounded_target_resolution_before_exact_content_scope"
            package_evidence_status = "profile_resolution_action_local_need_unresolved"
            stages = "target and learner-cohort resolution; curriculum stage remains provisional"
            prerequisite_route = "Resolve exact production profile -> check source-stated learner prerequisites -> scope a bounded content package."

        ranking_treatment = cand.get("profile_ranking_treatment", "")
        negative_control = cand.get("profile_negative_control_status", "")
        residual_only = (
            "deprioritize_generic_translation" in ranking_treatment
            or "rank only after scarcity/non-overlap evidence" in ranking_treatment
            or negative_control.startswith(("negative_control", "comparison_control"))
        )
        if residual_only and not needs and not custom.get("first_bounded_package"):
            first_package = (
                "Identify an exact unmet work, learner subgroup, non-overlap or accessibility-format residual "
                "against current supply; retain the source's supply-rich/comparison-control treatment. "
                "Do not commission generic FR-2 from a census count or a resolved language tag alone."
            )
            stages = "exact work, learner subgroup and accessibility-format residual resolution"
            prerequisite_route = "Audit exact current supply and beneficiary need -> specify the residual -> apply its source-stated prerequisites."
            status = "exact_residual_resolution_no_generic_translation"
            package_evidence_status = "profile_resolution_action_local_need_unresolved"

        output.append(attach_components({
            "exposure_position": "",
            "wave": "",
            "allocation_lane": "",
            "entry_id": entry_id,
            "entry_type": entry_type,
            "entry_name": entry_name,
            "target_profiles": target_profiles,
            "territory_or_scope": territory,
            "component_profile_ids": ";".join(profiles_for(entry_id)),
            "population_context": pop_context,
            "population_denominator_classes": pop_classes,
            "population_source_ids": pop_sources,
            "direct_reader_reach_claim": direct_claim,
            "shared_core_compute_reuse": reuse,
            "education_stages": stages,
            "needs_profile_ids": ";".join(dict.fromkeys(edge["needs_profile_id"] for edge in entry_edges)),
            "named_output_profile_ids": ";".join(dict.fromkeys(edge["named_output_profile_id"] for edge in entry_edges)) or ("ms-Latn-MY" if entry_id == "IL-IDMS" else target_profiles),
            "why_now": why_now,
            "first_bounded_package": first_package,
            "follow_on_package": follow_on,
            "prerequisite_route": prerequisite_route,
            "existing_supply_state": existing_supply,
            "delivery_formats": delivery_formats,
            "teacher_independent_requirements": teacher_independent,
            "accessibility_requirements": accessibility,
            "delivery_and_accessibility": delivery,
            "non_overlap_rule": non_overlap,
            "package_evidence_status": package_evidence_status,
            "recommendation_status": status,
            "ordering_basis": "pending_computed_allocation_policy",
            "evidence_confidence": confidence,
            "source_urls": source_urls,
            "uncertainty": caveats,
            "target_resolution_status": ";".join(flag for flag in source_resolution_flags if flag) or "no_source_resolution_flag_registered",
            "_population_observations": population_rows_for(entry_id),
            "_needs_edges": entry_edges,
            "_profile_resolution_status": cand.get("profile_resolution_status", ""),
        }, work_contract))

    if unresolved_ids:
        raise SystemExit("Unresolved portfolio entries: " + ", ".join(unresolved_ids))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    recovered = read_csv(RECOVERED_GAPS)
    recovered_by_exact_tag = {r["tag"]: r for r in recovered if ";" not in r["tag"]}
    lane_context = {"evidence": {}}
    lane_crosswalk = []
    for row in output:
        exact_tags = {tag.strip() for tag in row["named_output_profile_ids"].split(";")}
        exact_tags.update(tag.strip() for tag in row["target_profiles"].split(";"))
        matches = [recovered_by_exact_tag[tag] for tag in sorted(exact_tags) if tag in recovered_by_exact_tag]
        for match in matches:
            lane_crosswalk.append({"entry_id": row["entry_id"], "exact_tag": match["tag"], "profile_id": match["profile_id"],
                                   "lane": match["lane"], "evidence_ids": match["evidence_ids"],
                                   "prior_bands": {dim: match[dim] for dim in "RSANVPFD"},
                                   "treatment": "lane mapping plus separately scoped planning-prior crosswalk; never an observed reader count or inherited rank"})
        lanes = {match["lane"] for match in matches}
        selected_lane = ("high_reach_underserved" if "high_reach_underserved" in lanes else
                         "regional_depth" if "regional_depth" in lanes else
                         "endangered_prestige" if lanes & {"endangered_prestige", "accessibility_prestige"} else "")
        if selected_lane:
            lane_context["evidence"][row["entry_id"]] = {"lane": selected_lane,
                "lane_basis": "Exact-tag match to recovered GLOBAL_GAP_REGISTER.csv: " + ";".join(m["profile_id"] for m in matches) + ". Lane only; no inherited position or numerical access estimate."}
    calibration_paths = [ROOT / "staging" / "opportunity_planning_v1_1" / name
                         for name in ("asia_core.json", "large_profiles.json")]
    calibrations, calibration_inputs = load_calibrations(calibration_paths)
    for entry_id, contract in work_contract.items():
        if not contract.get("requires_calibration_binding", True):
            continue
        calibration = calibrations[entry_id]
        active = contract["active_components"]
        source_components = calibration["component_planning"]
        if {(c["locale"], c["package_id"]) for c in active} != {(c["profile"], c["component_id"]) for c in source_components}:
            raise ValueError("Calibration and active work scope differ: " + entry_id)
        calibration["opportunity_component_keys"] = [work_component_key(c) for c in active]
        calibration["component_ownership_source"] = file_identity(CONTRACT_PATH)
    planning_envelope, planning_crosswalk = assemble_context(
        output, recovered, file_identity(RECOVERED_GAPS), lane_context, calibrations)
    evidence_context = scenario_context(planning_envelope, "base")
    policy_inputs = {path.name: {"bytes": path.stat().st_size, "sha256": sha256(path)}
                     for path in [CANDIDATES, OBSERVATIONS, POPULATION_EDGES, EXPANSION, CURRICULUM, EXPECTED, JOINS, NEEDS, NEEDS_EDGES, ARCH,
                                  RECOVERED_GAPS,
                                  Path(__file__), Path(__file__).with_name("allocation_policy_v1_1.py"),
                                  Path(__file__).with_name("opportunity_planning_v1_1.py"),
                                  Path(__file__).with_name("component_scope_v1_1.py"), CONTRACT_PATH, *calibration_paths]}
    ranked, diagnostics = rank_portfolio(output, evidence_context)
    reranked, _ = rank_portfolio(list(reversed(output)), evidence_context)
    sensitivity_rows = []
    sensitivity_checks = []
    alternatives = {
        "balanced_1_1_1": ["high_reach_underserved", "regional_depth", "endangered_prestige"],
        "scale_emphasis_8_1_1": ["high_reach_underserved"] * 8 + ["regional_depth", "endangered_prestige"],
    }
    for scenario, cycle in alternatives.items():
        alternative_context = {**evidence_context, "policy": {"lane_cycle": cycle}}
        alternative_rows, alternative_diagnostics = rank_portfolio(output, alternative_context)
        sensitivity_checks.append(all(diagnostics["entries"][cid]["dimensions"] == alternative_diagnostics["entries"][cid]["dimensions"] for cid in diagnostics["entries"]))
        alternative_positions = {r["entry_id"]: r["exposure_position"] for r in alternative_rows}
        default_positions = {r["entry_id"]: r["exposure_position"] for r in ranked}
        for cid in sorted(diagnostics["entries"]):
            sensitivity_rows.append({"scenario": scenario, "entry_id": cid,
                                     "default_position": default_positions.get(cid, "owned_by_other_selected_package"),
                                     "scenario_position": alternative_positions.get(cid, "owned_by_other_selected_package"),
                                     "interpretation": "Policy sensitivity only; source observations and opportunity dimensions unchanged."})
    opportunity_rows = []
    opportunity_scenario_summaries = {}
    baseline_positions = {r["entry_id"]: r["exposure_position"] for r in ranked}
    for scenario in ("cautious", "favorable", "envelope", "measured_only"):
        scenario_rows, scenario_diagnostics = rank_portfolio(output, scenario_context(planning_envelope, scenario))
        positions = {r["entry_id"]: r["exposure_position"] for r in scenario_rows}
        opportunity_scenario_summaries[scenario] = {
            "top10": [r["entry_id"] for r in scenario_rows[:10]],
            "dispatched_rows": len(scenario_rows),
            "opportunity_status_counts": scenario_diagnostics["opportunity_status_counts"],
        }
        for cid in sorted(diagnostics["entries"]):
            dimensions = scenario_diagnostics["entries"][cid]["dimensions"]
            opportunity_rows.append({
                "scenario": scenario, "entry_id": cid,
                "base_position": baseline_positions.get(cid, "owned_by_other_selected_package"),
                "scenario_position": positions.get(cid, "owned_by_other_selected_package"),
                **{dim: dimensions[dim]["band"] for dim in "RSANVPFD"},
                "interpretation": "Conditional planning/scope sensitivity; not measured benefits, probability bounds or a confidence interval.",
            })
    policy_checks = {
        "input_permutation_invariant": [r["entry_id"] for r in ranked] == [r["entry_id"] for r in reranked],
        "all_registered_candidates_have_disposition": all(cid in candidate_ids or any(d["entry_id"] == cid for d in candidate_dispositions) for cid in candidates),
        "at_least_100_nonduplicate_actions": len(ranked) >= 100,
        "unique_ranked_ids": len({r["entry_id"] for r in ranked}) == len(ranked),
        "equal_basis_profiles_enter_selection": all(cid in {r["entry_id"] for r in output} for cid in ["NAT-121", "NAT-122", "NAT-123", "NAT-124", "NAT-125"]),
        "no_old_position_input": all(not r["exposure_position"] for r in output),
        "opportunity_evidence_unchanged_under_alternative_lane_policies": all(sensitivity_checks),
        "package_specific_calibrations_loaded": len(calibrations) >= 10,
        "planning_view_admits_nonzero_provisional_dimension_count": diagnostics["opportunity_status_counts"]["provisional_planning_inference"] > 0,
        "measured_only_does_not_present_provisional_judgments_as_measurements": opportunity_scenario_summaries["measured_only"]["opportunity_status_counts"]["provisional_planning_inference"] == 0,
        "spoken_putonghua_not_absorbed_into_written_chinese": "GLB-053" in {r["entry_id"] for r in output}
            and next(r for r in output if r["entry_id"] == "NAT-122")["component_profile_ids"] == "GLB-002",
        "country_specific_pashto_population_not_cross_inherited": all(
            {r.get("candidate_id") for r in population_rows_for(cid) if r.get("candidate_id")} <= {cid}
            for cid in ("NAT-016", "NAT-017")),
    }
    for row in ranked:
        row["wave"] = wave(int(row["exposure_position"]))
        metadata = diagnostics["entries"][row["entry_id"]]
        row.update({"opportunity_" + dim: metadata["dimensions"][dim]["band"] for dim in "RSANVPFD"})
        row["opportunity_view"] = "provisional_planning_base"
        row["opportunity_scope"] = str(evidence_context["evidence"].get(row["entry_id"], {}).get("dimensions", {}).get("R", {}).get("planning_scope", "Unresolved newly comfortable reader scope; not zero"))
    fields = FIELDS + sorted({key for row in ranked for key in row if key not in FIELDS and not key.startswith("_")})
    for path, items in [(OUT_DIR / "full_computed_allocation_queue.csv", ranked)]:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(items)
    (OUT_DIR / "candidate_dispositions.json").write_text(json.dumps(candidate_dispositions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "recovered_lane_and_prior_band_crosswalk.json").write_text(json.dumps(lane_crosswalk, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "scope_calibrated_planning_crosswalk.json").write_text(json.dumps(planning_crosswalk, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    opportunity_path = ROOT / "opportunity_planning_sensitivity_v1_1.csv"
    with opportunity_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(opportunity_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(opportunity_rows)
    sensitivity_path = ROOT / "allocation_policy_sensitivity_v1_1.csv"
    with sensitivity_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(sensitivity_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(sensitivity_rows)
    policy_receipt = {"schema": "interlanguage/allocation-policy-validation/1.1.0",
                      "status": "PASS" if all(policy_checks.values()) else "FAIL", "checks": policy_checks,
                      "inputs": policy_inputs, "policy": diagnostics.get("policy", {}), "diagnostics": diagnostics,
                      "planning_calibration_inputs": calibration_inputs,
                      "planning_sensitivity": {"scenarios": opportunity_scenario_summaries,
                                               "rows": len(opportunity_rows), "bytes": opportunity_path.stat().st_size,
                                               "sha256": sha256(opportunity_path)},
                      "policy_sensitivity": {"scenarios": list(alternatives), "rows": len(sensitivity_rows),
                                             "bytes": sensitivity_path.stat().st_size, "sha256": sha256(sensitivity_path)},
                      "registered_master_rows": len(candidates), "constructed_action_rows": len(output),
                      "ranked_unique_action_rows": len(ranked)}
    (ROOT / "allocation_policy_v1_1_validation.json").write_text(json.dumps(policy_receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not all(policy_checks.values()):
        raise SystemExit("Allocation-policy integration checks failed")
    full_output = ranked
    output = ranked[:100]
    staging_path = OUT_DIR / "authoritative_exposure_portfolio_v1_1.csv"
    with staging_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)

    checks = {
        "portfolio_has_100_rows": len(output) == 100,
        "positions_exact_1_to_100": [int(r["exposure_position"]) for r in output] == list(range(1, 101)),
        "unique_entry_ids": len({r["entry_id"] for r in output}) == 100,
        "required_large_profiles_in_full_computed_universe": all(x in {r["entry_id"] for r in full_output} for x in [
            "NAT-121", "NAT-122", "NAT-123", "NAT-125", "GLB-044", "GLB-024", "GLB-025", "GLB-026", "GLB-027",
        ]),
        "bhojpuri_component_profile_present": any(
            r["entry_id"] == "NAT-125" and "GLB-052" in r["component_profile_ids"].split(";")
            for r in full_output
        ),
        "direct_and_reuse_fields_complete": all(r["direct_reader_reach_claim"] and r["shared_core_compute_reuse"] for r in output),
        "population_context_complete": all(r["population_context"] for r in output),
        "first_package_complete": all(r["first_bounded_package"] for r in output),
        "no_blank_registered_work": not any("output: ;" in r["first_bounded_package"] for r in output),
        "malaysian_beneficiary_not_indonesian": all(
            r["component_profile_ids"] == "GLB-054" and r["named_output_profile_ids"] == "ms-Latn-MY"
            and not r["needs_profile_ids"]
            for r in full_output if r["entry_id"] == "NAT-040"
        ),
        "malaysian_beneficiary_row_exists": any(r["entry_id"] == "NAT-040" for r in full_output),
        "malay_first_action_architecture_alias_not_double_commissioned": not any(r["entry_id"] == "IL-IDMS" for r in full_output),
        "nigerian_pidgin_row_exists": any(r["entry_id"] == "NAT-072" for r in full_output),
        "nigerian_pidgin_audio_first": all("audio" in r["first_bounded_package"] and "oral" in r["education_stages"] for r in full_output if r["entry_id"] == "NAT-072"),
        "ambiguous_missing_supply_absent": all(r["existing_supply_state"] != "missing" for r in output),
        "evidence_field_not_empty": all(r["source_urls"] for r in output),
        "follow_on_package_complete": all(r["follow_on_package"] for r in output),
        "prerequisite_route_complete": all(r["prerequisite_route"] for r in output),
        "delivery_formats_complete": all(r["delivery_formats"] for r in output),
        "teacher_independent_requirements_complete": all(r["teacher_independent_requirements"] for r in output),
        "accessibility_requirements_complete": all(r["accessibility_requirements"] for r in output),
        "non_overlap_complete": all(r["non_overlap_rule"] for r in output),
        "package_evidence_status_explicit": all(
            r["package_evidence_status"] != "unresolved_no_registered_package" for r in output
        ),
        "top10_is_computed_prefix": output[:10] == ranked[:10],
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    if status != "PASS":
        OUT_VALIDATION.write_text(json.dumps({
            "schema": "interlanguage/authoritative-exposure-portfolio-validation/1.1.0",
            "status": status,
            "checks": checks,
            "staging_output": {"bytes": staging_path.stat().st_size, "sha256": sha256(staging_path)},
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        raise SystemExit("FAIL: authoritative portfolio validation did not pass")

    for path, rows in (
        (OUT_TOP100, output), (OUT_TOP10, output[:10]),
        (OUT_TOP100_ALIAS, output), (OUT_TOP10_ALIAS, output[:10]),
    ):
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    validation = {
        "schema": "interlanguage/authoritative-exposure-portfolio-validation/1.1.0",
        "status": status,
        "portfolio_rows": len(output),
        "top10_rows": 10,
        "checks": checks,
        "top10_contains": [r["entry_id"] for r in output[:10]],
        "lane_counts": dict(sorted(Counter(r["allocation_lane"] for r in output).items())),
        "status_counts": dict(sorted(Counter(r["recommendation_status"] for r in output).items())),
        "top100": {"bytes": OUT_TOP100.stat().st_size, "sha256": sha256(OUT_TOP100)},
        "top10": {"bytes": OUT_TOP10.stat().st_size, "sha256": sha256(OUT_TOP10)},
        "top100_alias": {"bytes": OUT_TOP100_ALIAS.stat().st_size, "sha256": sha256(OUT_TOP100_ALIAS)},
        "top10_alias": {"bytes": OUT_TOP10_ALIAS.stat().st_size, "sha256": sha256(OUT_TOP10_ALIAS)},
        "inputs": {
            "expected_profiles": {"bytes": EXPECTED.stat().st_size, "sha256": sha256(EXPECTED)},
            "population_joins": {"bytes": JOINS.stat().st_size, "sha256": sha256(JOINS)},
            "high_reach_needs": {"bytes": NEEDS.stat().st_size, "sha256": sha256(NEEDS)},
            "high_reach_needs_edges": {"bytes": NEEDS_EDGES.stat().st_size, "sha256": sha256(NEEDS_EDGES)},
            "bridge_hypotheses": {"bytes": ARCH.stat().st_size, "sha256": sha256(ARCH)},
            "curriculum_portfolios": {"bytes": CURRICULUM.stat().st_size, "sha256": sha256(CURRICULUM)},
        },
        "interpretation": (
            "Positions are a transparent commissioning exposure order. They are not a proof that territory, L1, L2, "
            "home-use, functional-use and institutional speaker estimates are cardinally comparable."
        ),
    }
    OUT_VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status, "top100_rows": len(output),
        "top10": [r["entry_id"] for r in output[:10]],
        "top100_sha256": sha256(OUT_TOP100),
        "top10_sha256": sha256(OUT_TOP10),
        "validation_sha256": sha256(OUT_VALIDATION),
    }, indent=2))


if __name__ == "__main__":
    main()
