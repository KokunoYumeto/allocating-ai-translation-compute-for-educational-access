#!/usr/bin/env python3
"""Build the independent large-profile and shared-core recall universe.

This is an exhaustive *disposition* register, not a population leaderboard.
Rows may be ranked only later, inside a compatible denominator view.  The
register prevents a failed join or abundant existing supply from making a
large language disappear.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "staging" / "global_expected_universe"

RECALL_50M = {
    "en", "zh", "hi", "es", "ar", "fr", "ur", "bn", "pt", "ru", "sw",
    "id", "pa-Arab", "de", "ja", "te", "lah", "mr", "jv", "vi", "ta",
    "fa", "wuu", "tr", "yue", "ko", "fil", "arz", "it", "gu", "ps",
    "th", "kn", "bho", "cmn", "ms",
}
WATCH_40M = {"pcm", "ml", "or", "apc", "pa", "ha", "sd", "pl", "hsn"}

ALLOWED_DISPOSITIONS = {
    "ranked_in_typed_view",
    "forward_residual_audit",
    "supply_rich_negative_control",
    "shared_core_only",
    "unresolved_no_comparable_count",
    "excluded_with_evidence",
}

PROFILE_FIELDS = [
    "universe_profile_id", "recall_code", "display_name", "profile_tag",
    "profile_kind", "region", "threshold_band", "denominator_classes_available",
    "candidate_ids", "disposition", "disposition_basis", "source_basis",
    "population_identity_warning", "existing_supply_state",
    "next_nonduplicative_action",
]

BRIDGE_FIELDS = [
    "architecture_id", "display_name", "mechanism_class", "named_outputs",
    "diagnostic_universe", "threshold_band", "direct_reader_reach_status",
    "compute_reuse_status", "candidate_ids", "evidence_basis",
    "mandatory_exclusions", "next_measurement",
]


def p(
    uid: str, code: str, name: str, tag: str, kind: str, region: str,
    band: str, measures: str, candidates: str, disposition: str, basis: str,
    sources: str, warning: str, supply: str, action: str,
) -> dict[str, str]:
    return dict(zip(PROFILE_FIELDS, [
        uid, code, name, tag, kind, region, band, measures, candidates,
        disposition, basis, sources, warning, supply, action,
    ]))


PROFILES = [
    p("GLB-001", "en", "Global learned English access baseline", "en-Latn; locale outputs required", "learned_lingua_franca", "Global", ">=1B functional ceiling", "L1;home;functional;territory", "", "supply_rich_negative_control", "Explicitly enumerate English; residual is academic comfort, plain language, bilingual access, offline and accessibility rather than generic translation.", "US ACS 2024; England Census 2021; British Council global estimate as diagnostic only", "Global L2/use estimates are not academic-reading comfort and overlap nearly every other profile.", "Very high but licensing, login, accessibility and stage gaps remain.", "Audit exact stage/subject/format residuals and keep English overlap out of unique-language reach."),
    p("GLB-002", "zh", "Standard Written Chinese, Mainland Simplified", "zh-Hans-CN", "learned_written_standard", "Eastern Asia", ">=1B territory; >=1B derived functional sensitivity", "territory;functional", "NAT-122", "forward_residual_audit", "Equal-basis profile with completed exact corpora subtracted only in forward allocation.", "PRC 2020 census; MOE 2020 Putonghua 80.72%; MOE standardized-character evidence", "Territory, Putonghua communication and simplified-character use are different universes; not spoken-Sinitic mutual intelligibility.", "Large national supply; exact OLP and algebra corpus complete; accessibility/frontier residuals remain.", "Finish registered partial works and commission only exact open, accessible, professional or frontier gaps."),
    p("GLB-003", "zh", "Standard Written Chinese, Taiwan Traditional", "zh-Hant-TW", "pluricentric_written_standard", "Eastern Asia", "regional constituent", "first-learned;main-use;functional", "", "forward_residual_audit", "Traditional-script locale must be explicit and cannot inherit mainland population or terminology.", "Taiwan 2020 census Guoyu first-learned/current-use tables", "Taiwan Guoyu and traditional-character literacy are not mainland Hans reach.", "Strong local supply; exact open/accessibility/frontier inventory pending.", "Audit exact residual and reuse semantic source with a Taiwan locale layer."),
    p("GLB-004", "wuu", "Wu varieties and written-access profiles", "wuu-Hans-CN; exact variety outputs unresolved", "macrolanguage_resolution", "Eastern Asia", ">=50M recall", "functional estimate only", "", "unresolved_no_comparable_count", "Large Sinitic recall case; one academic written Wu profile and comfortable-reader population are not established.", "Pinned CLDR recall; Chinese dialectology/standard-language evidence required", "Standard Written Chinese schooling does not make spoken Wu identical to Mandarin or prove vernacular written demand.", "Mainstream schooling uses Standard Written Chinese; vernacular supply unresolved.", "Resolve exact varieties, modality and product need before any rank."),
    p("GLB-005", "yue", "Yue/Cantonese written and spoken profiles", "yue-Hant-HK; yue-Hans-CN; locale outputs", "language_register_split", "Eastern Asia", ">=50M recall", "home;functional", "", "unresolved_no_comparable_count", "Large directed spoken/written profile requiring Hans/Hant and vernacular/formal separation.", "Pinned CLDR recall; Hong Kong 2021 census Putonghua/Cantonese language tables", "Formal written Chinese and written vernacular Cantonese are not the same target.", "Strong Hong Kong and Guangdong supply but reuse/licensing/access gaps unquantified.", "Build separate HK/Guangdong profile inventory before commissioning."),
    p("GLB-006", "hsn", "Xiang varieties", "hsn-Hans-CN; exact standard unresolved", "macrolanguage_resolution", "Eastern Asia", "40-50M watch", "functional estimate only", "", "unresolved_no_comparable_count", "Watch-band Sinitic population with no validated single academic written target.", "Pinned CLDR recall", "Do not substitute the Sinitic family or mainland population.", "Standard Written Chinese school supply exists; vernacular residual unknown.", "Resolve exact community, written modality and incremental use."),
    p("GLB-007", "hi", "Standard Hindi, India", "hi-Deva-IN", "standard_variety", "South Asia", ">=250M exact same-name L1", "L1;functional umbrella", "NAT-124", "forward_residual_audit", "Use 322,230,097 same-name C-16 component, never the 528M Hindi umbrella as Standard Hindi.", "India C-16/C-17", "Bhojpuri and other named returns are nested in the census Hindi umbrella.", "Strong school supply and exact formal-reasoning edition; higher/professional gaps remain.", "Commission exact bilingual tertiary, research-method, professional and accessibility residuals."),
    p("GLB-008", "ur", "Urdu, Pakistan", "ur-Aran-PK", "national_standard", "South Asia", ">=50M functional/bridge recall", "L1;territory;functional unresolved", "NAT-012", "ranked_in_typed_view", "Exact Pakistan L1 cell and separate national-bridge sensitivity.", "Pakistan 2023 Census Table 11", "National status is not universal comfortable Nastaliq readership.", "School and media supply exists; advanced open sequence unresolved.", "Audit secondary-to-tertiary and professional gaps with offline Nastaliq rendering."),
    p("GLB-009", "ur", "Urdu, India", "ur-Aran-IN", "regional_standard", "South Asia", ">=50M exact L1", "L1;functional", "NAT-013", "ranked_in_typed_view", "Separate India curriculum and population cell with shared Hindi-Urdu source tooling.", "India C-16/C-17", "Do not merge with Pakistan Urdu or Standard Hindi readership.", "Supply varies by state and stage.", "Audit exact state/stage open supply and terminology transitions."),
    p("GLB-010", "bn", "Bangla, Bangladesh", "bn-Beng-BD", "national_standard", "South Asia", ">=150M", "territory;derived L1", "NAT-001", "ranked_in_typed_view", "Use official territory and survey-derived L1 in their own views; replace stale CLDR point.", "Bangladesh PHC 2022; SEDS 2023", "Derived L1 is not an exact census language count; Bangladesh and India need separate overlays.", "Current NCTB supply; foundational mastery and continuity gaps documented.", "Prioritize ECE/grades 2-5 recovery, emergency continuity, then TVET/applied pathways."),
    p("GLB-011", "bn", "Bengali, India", "bn-Beng-IN", "regional_standard", "South Asia", ">=90M exact L1", "L1;functional", "NAT-002", "ranked_in_typed_view", "Separate Indian curriculum and terminology layer; share semantic core with Bangladesh.", "India C-16/C-17", "Do not use one locale-neutral Bangla edition.", "School supply substantial; vocational/tertiary discontinuities remain.", "Prioritize secondary/TVET and Bengali-English first-year bridges."),
    p("GLB-012", "te", "Telugu", "te-Telu-IN", "regional_standard", "South Asia", ">=80M exact L1", "L1;functional", "NAT-003", "ranked_in_typed_view", "Exact C-16/C-17 profile with state curriculum overlays.", "India C-16/C-17", "Andhra Pradesh and Telangana require separate curriculum crosswalks.", "School supply substantial; TVET/tertiary transition thin.", "Applied secondary/TVET/first-year STEM, coding, finance and entrepreneurship."),
    p("GLB-013", "mr", "Marathi", "mr-Deva-IN", "regional_standard", "South Asia", ">=80M exact L1", "L1;functional", "NAT-006", "ranked_in_typed_view", "Exact C-16/C-17 profile.", "India C-16/C-17", "Functional total is not additive to L1.", "Strong grade 1-12 provision; vocational/tertiary residual.", "Secondary/TVET and first-year applied science, computing, finance and agriculture."),
    p("GLB-014", "ta", "Tamil, India", "ta-Taml-IN", "regional_standard", "South Asia", ">=50M exact L1", "L1;functional", "NAT-004", "ranked_in_typed_view", "Keep Indian and Sri Lankan outputs separate with reusable source.", "India C-16/C-17", "Sri Lankan Tamil is a distinct locale and population cell.", "Comparatively strong school/vocational supply; tertiary/research continuity residual.", "Tamil-English first-year STEM, management and research methods."),
    p("GLB-015", "gu", "Gujarati", "gu-Gujr-IN", "regional_standard", "South Asia", ">=50M exact L1", "L1;functional", "NAT-007", "ranked_in_typed_view", "Exact C-16/C-17 profile.", "India C-16/C-17", "Functional total is not additive to L1.", "Supply audit incomplete beyond school baseline.", "Audit microenterprise, applied science, finance and first-year transition."),
    p("GLB-016", "kn", "Kannada", "kn-Knda-IN", "regional_standard", "South Asia", ">=50M functional; L1 below threshold", "L1;functional", "NAT-008", "ranked_in_typed_view", "Qualifies only in functional view; label denominator explicitly.", "India C-16/C-17", "C-17 L2/L3 total cannot be compared as L1.", "School supply exists; advanced open continuity unresolved.", "Audit TVET/tertiary and professional residual before selecting package."),
    p("GLB-017", "ml", "Malayalam", "ml-Mlym-IN", "regional_standard", "South Asia", "40-50M watch", "L1;functional", "NAT-009", "ranked_in_typed_view", "Material watch-band profile; neither verified measure exceeds 50M.", "India C-16/C-17", "Do not inflate using Kerala territory without language evidence.", "Local supply exists; residual not yet inventoried.", "Audit exact advanced/open/accessibility gaps."),
    p("GLB-018", "or", "Odia", "ory-Orya-IN", "regional_standard", "South Asia", "40-50M watch", "L1;functional", "NAT-010", "ranked_in_typed_view", "Use ISO 639-3 `ory` in research tables; keep `or` as tooling alias.", "India C-16/C-17; IANA", "Below 50M on verified measures.", "Supply inventory incomplete.", "Audit secondary/TVET/tertiary discontinuity."),
    p("GLB-019", "pa-Arab", "Punjabi, Pakistan", "pa-Arab-PK; Aran when Nastaliq asserted", "census_label_to_profile_resolution", "South Asia", ">=80M exact source label", "L1", "NAT-015", "unresolved_no_comparable_count", "The census says Punjabi, not specifically `pnb`; retain conservative locale profile pending variety evidence.", "Pakistan 2023 Census Table 11", "Do not equate every Punjabi return with one Western Punjabi variety or standardized readership.", "Written/scientific supply and readership unresolved.", "Resolve variety and orthography, then commission a separate Pakistan output."),
    p("GLB-020", "pa", "Punjabi, India", "pa-Guru-IN", "regional_standard", "South Asia", "40-50M watch", "L1;functional", "NAT-014", "ranked_in_typed_view", "Separate Gurmukhi population and edition; share semantics with Pakistan output.", "India C-16/C-17", "No cross-script population credit.", "Supply inventory incomplete.", "Audit exact secondary/tertiary residual and synchronized dual-script production."),
    p("GLB-021", "lah", "Lahnda-labelled recall universe", "und-Arab-PK-Lahnda; resolve Saraiki/Hindko/Punjabi labels", "invalid_aggregation", "South Asia", ">=50M recall", "database-derived only", "NAT-019", "unresolved_no_comparable_count", "Lahnda is not accepted as one educational edition or additive population.", "Pinned CLDR recall; Pakistan census named categories", "Overlaps Punjabi, Saraiki, Hindko and classification conventions.", "No coherent single supply inventory.", "Resolve named outputs and never rank the macro-label."),
    p("GLB-022", "ps", "Pashto, Pakistan and Afghanistan profiles", "ps-Arab-PK; ps-Arab-AF", "cross_border_standard_profiles", "South/Central Asia", ">=50M combined mixed diagnostic", "L1;derived functional", "NAT-016;NAT-017", "unresolved_no_comparable_count", "Pakistan exact L1 and Afghanistan derived L1/L2 must remain separate.", "Pakistan Census 2023; Afghanistan derived source", "Mixed denominator and dialect/orthography profiles cannot form one rank.", "Supply and displaced-cohort access unresolved.", "Resolve each profile; reuse a shared semantic source without blanket reach."),
    p("GLB-023", "sd", "Sindhi, Pakistan", "sd-Arab-PK", "regional_standard", "South Asia", "40-50M watch", "L1", "NAT-018", "ranked_in_typed_view", "Exact census profile below 50M retained as major regional target.", "Pakistan 2023 Census Table 11", "Shared RTL tooling is not intelligibility.", "Supply inventory incomplete.", "Audit school-to-tertiary and professional residual."),
    p("GLB-024", "es", "Latin American Spanish localized core", "es-419 with country overlays", "pluricentric_standard", "Americas", ">=250M", "L1;home;functional", "", "supply_rich_negative_control", "Spanish remains explicit; need is mastery, open/offline/accessibility and country overlays, not absence of all textbooks.", "Cervantes 2025 diagnostic; national censuses; UNESCO ERCE", "Headline global totals are models and do not equal unique underserved readers.", "Very high supply; substantial mastery and licensing/access residuals.", "Country-specific grades 3-9 recovery and exact professional/frontier gaps."),
    p("GLB-025", "pt", "Brazilian Portuguese", "pt-BR", "national_pluricentric_standard", "Americas", ">=200M territory proxy", "territory;institutional speaker estimate", "", "supply_rich_negative_control", "Explicit large profile; focus on no-login/offline/reuse/accessibility and exact residuals.", "Brazil Census 2022; UN Portuguese estimate", "Brazil population is not a Portuguese-reader count; global Portuguese totals lack disclosed proficiency method.", "Extensive school/health supply, often authenticated or DRM constrained.", "Build lawful offline teacher-independent bundles and exact research residuals."),
    p("GLB-026", "fr", "Global/French regional localized standards", "fr-Latn with country overlays", "learned_lingua_franca", "Global", ">=250M institutional functional model", "functional model;school", "", "supply_rich_negative_control", "Keep French as learned-language overlap and localization architecture, not unique reach.", "OIF 2026 methods 1 and 2", "Modeled Francophone totals include heterogeneous competence and schooling.", "High global supply with regional licensing/access/comfort gaps.", "Audit country/stage-specific residuals and local-language bridges."),
    p("GLB-027", "ru", "Russian learned standard", "ru-Cyrl-RU; localized successor-state overlays", "learned_lingua_franca", "Europe/Central Asia", ">=100M functional", "functional;daily-use", "", "supply_rich_negative_control", "Rosstat direct functional/daily-use evidence; global learned-standard reach remains separate.", "Rosstat 2021 language table; UNESCO diagnostic", "Knowledge may mean speaking only; no automatic written competence or ex-Soviet community coverage.", "Strong university/research infrastructure; reuse and accessibility vary.", "Open no-login professional/research-methods stack and exact frontier gaps."),
    p("GLB-028", "de", "German, Germany", "de-Latn-DE", "national_standard", "Europe", ">=50M home-language", "home", "", "supply_rich_negative_control", "Explicit supply-rich control with measurable home-language denominator.", "Destatis Microcensus 2024", "Home use is not a literacy test and does not cover all Germanic minorities.", "Very high educational and scientific supply.", "Only exact open/accessibility/frontier residuals; do not use for Germanic minority coverage."),
    p("GLB-029", "it", "Italian, Italy", "it-Latn-IT", "national_standard", "Europe", ">=50M derived L1", "mother-tongue;habitual-use", "", "supply_rich_negative_control", "Explicit supply-rich profile; direct L1 threshold is derived from rounded official quantities.", "Istat 2015/2024", "No direct Italian literacy census in located source.", "High mainstream supply.", "Audit only exact open/accessibility/professional/frontier residuals."),
    p("GLB-030", "pl", "Polish", "pl-Latn-PL", "national_standard", "Europe", "40-50M watch", "harmonized survey;territory", "", "supply_rich_negative_control", "Near-threshold supply-rich control retained rather than silently omitted.", "EU Eurobarometer; national source audit pending", "Rounded survey shares are not exact population cells.", "High mainstream supply.", "Exact residual audit only."),
    p("GLB-031", "ar", "Modern Standard Arabic plus locale scaffolds", "arb-Arab; country spoken-language layers", "learned_written_standard", "MENA/Global", ">=250M umbrella", "institutional speaker estimate;school", "IL-AR", "forward_residual_audit", "MSA is a learned formal standard; existing exact corpus is credited while country/diglossia residuals remain.", "UNESCO/UN Arabic estimates; World Bank diglossia reviews", "Nobody's ordinary home language can be presumed to be MSA; Arabic umbrella varieties are not one comfort population.", "Substantial but fragmented formal/professional supply.", "Country-specific MSA-literacy plus local-spoken scaffolds, emergency and research pathways."),
    p("GLB-032", "arz", "Egyptian Arabic scaffold", "arz-Arab-EG; Saidi and other profiles separate", "spoken_scaffold", "North Africa", ">=50M recall", "territory proxy;spoken estimate unresolved", "", "shared_core_only", "Named spoken scaffold under MSA; zero independent written reach until modality is specified.", "Pinned CLDR recall; World Bank Arabic-learning evidence", "Egypt territory is not Egyptian-Arabic reader population; regional varieties remain.", "Large media supply; educational written convention unresolved.", "Specify oral/audio/plain-language functions and exact orthography before reach credit."),
    p("GLB-033", "apc", "Levantine Arabic profiles", "apc-Arab with SY/LB/JO/PS locale layers", "spoken_scaffold", "West Asia", "40-50M watch", "spoken estimate unresolved", "", "shared_core_only", "Country-specific oral scaffolds under MSA, not one replacement written edition.", "Pinned CLDR recall; national education evidence required", "Conflict/displacement and country varieties prevent one additive comfort count.", "Formal MSA supply exists; emergency/local oral access varies.", "Build country-specific emergency and spoken-to-MSA bridges."),
    p("GLB-034", "fa", "Iranian Persian", "fa-Arab-IR", "national_standard", "West/Central Asia", ">=50M recall", "L1/functional unresolved", "", "ranked_in_typed_view", "Large standard-language profile requiring its own authoritative denominator and supply audit.", "Pinned CLDR recall; Iran census/language source pending", "Do not merge Dari and Tajik populations or scripts.", "National supply substantial; open/advanced accessibility unknown.", "Resolve denominator and exact tertiary/professional/frontier residual."),
    p("GLB-035", "tr", "Turkish, Turkey", "tr-Latn-TR", "national_standard", "West Asia/Europe", ">=50M territory/official proxy", "territory;literacy proxy", "", "ranked_in_typed_view", "Strong territory and statutory-language proxy; no current nationwide use count located.", "TurkStat 2024 population/literacy; Constitution", "Territory and language-neutral literacy are not Turkish reader counts.", "Strong mainstream supply.", "Rank only in territory/proxy view; audit exact open/accessibility/frontier residual."),
    p("GLB-036", "sw", "Standard Kiswahili with country layers", "swh-Latn-TZ; swh-Latn-KE; swh-Latn-UG; swc-Latn-CD", "learned_lingua_franca", "Eastern/Central Africa", ">=100M gross regional functional estimate", "territory;institutional speaker estimate", "NAT-063;NAT-064", "ranked_in_typed_view", "Genuine learned regional bridge; country and DRC-variety layers are mandatory.", "UNESCO/AU >200M diagnostic; Tanzania/Kenya/Uganda censuses", "Global headline is not a deduplicated written-reader count; DRC Congo Swahili is distinct.", "Tanzania primary supply; DRC/Uganda gaps stronger.", "DRC early-grade/local variety and Uganda L2 first; later bilingual STEM/TVET/research."),
    p("GLB-037", "ha", "Hausa Boko country outputs", "ha-Latn-NG; ha-Latn-NE", "cross_border_standard", "West Africa", "40-50M watch L1; >=50M gross functional estimates", "speaker estimate;literacy shares unjoined", "NAT-069", "unresolved_no_comparable_count", "Nigeria/Niger orthographies and written readership must be separated.", "Cambridge/Newman estimate; Nigeria/Niger official evidence", "60M and 94M source universes differ; optional Ajami has separate unknown readership.", "Early readers exist; advanced STEM/TVET/professional supply thinner.", "Resolve denominator; foundational/functional boko, country bridges, optional Ajami/audio."),
    p("GLB-038", "pcm", "Nigerian Pidgin / Naijá", "pcm-Latn-NG", "oral_lingua_franca", "West Africa", "40-50M watch; >50M oral estimate", "oral estimate;territory", "NAT-072", "unresolved_no_comparable_count", "Separate oral/audio access from written-reader reach.", "Peer-reviewed 80-112M oral estimate; NLA orthography", "Nigeria territory and oral users do not establish standardized written readership.", "Strong oral reach; educational written uptake uncertain.", "Audio/basic-phone practical modules first; measure orthography uptake before text rank."),
    p("GLB-039", "id", "Bahasa Indonesia", "id-Latn-ID", "national_standard", "Southeast Asia", ">=200M functional", "functional oral", "NAT-121;CMP-ID-ID", "forward_residual_audit", "Official 248.5M functional oral ceiling; completed Indonesian program is credited exactly.", "BPS 2022 long-form census; public program receipts", "Oral ability is not written academic comfort; overlaps Javanese and other home languages.", "Open Logic 722/722 and broad 40-course program; remaining roles/access/professional needs exact.", "No duplicate logic/basic math; finish exact program roles then evidence-to-practice/research core."),
    p("GLB-040", "jv", "Javanese", "jv-Latn-ID", "regional_language", "Southeast Asia", ">=50M home-language", "home/daily-use", "NAT-038", "ranked_in_typed_view", "Large home-language population nested within Bahasa Indonesia functional reach.", "Indonesia census/home-language evidence", "Explicit subset/overlap edge with Indonesian is mandatory.", "Advanced Indonesian bridge supply exists; Javanese scientific supply limited.", "Bilingual/audio terminology transfer before duplicating the full advanced corpus."),
    p("GLB-041", "vi", "Vietnamese", "vi-Latn-VN", "national_standard", "Southeast Asia", ">=50M speaker/territory", "speaker estimate;territory", "NAT-028", "ranked_in_typed_view", "Replace rounded speaker estimate with official territory/standard evidence in typed views.", "Peer-reviewed 89M lower bound; Vietnam official population evidence", "Territory and language reach are distinct; minority-language early grades remain separate.", "National digital supply exists but is fragmented.", "Coherent TVET-university data, green industry, health, MSME and research-method packages."),
    p("GLB-042", "th", "Thai", "th-Thai-TH", "national_standard", "Southeast Asia", ">=50M home/functional", "derived home-language union", "NAT-029", "ranked_in_typed_view", "Retain direct Thai census union with derivation explicit.", "Thailand census language union", "Derived union assumptions and minority-language overlap must remain visible.", "National supply substantial; open/self-study residual unquantified.", "Audit exact secondary/TVET/tertiary/open/accessibility gaps."),
    p("GLB-043", "ja", "Japanese, Japan", "ja-Jpan-JP", "national_standard", "Eastern Asia", ">=100M territory ceiling", "territory", "NAT-123", "forward_residual_audit", "Not a language-wide negative control; strong school supply and stage-specific residuals coexist.", "Japan 2020 Census; OECD PISA; MEXT/JMOOC/J-STAGE supply audit", "Territory is not Japanese-language or underserved-reader count.", "Strong school and research supply; open/accessibility/nonattendance/frontier gaps remain.", "Accessible grades 5-9 bridge, research methods, then exact advanced algebraic-geometry gaps."),
    p("GLB-044", "ko", "Korean, Republic of Korea", "ko-Kore-KR", "national_standard", "Eastern Asia", ">=50M territory ceiling", "territory", "", "forward_residual_audit", "Large profile absent from old candidate universe; ROK evidence cannot stand for DPRK.", "ROK census/territory; K-MOOC/KOCW/NIA supply evidence", "Territory is not a Korean reader count and excludes DPRK conditions.", "Strong digital course supply with portability/accessibility gaps.", "Offline life-capability and research reproducibility packages; exact advanced residual audit."),
    p("GLB-045", "ko", "Korean, DPRK", "ko-Kore-KP", "national_standard_locale", "Eastern Asia", "regional constituent", "territory only", "", "unresolved_no_comparable_count", "Separate locale and educational-supply evidence required.", "UN territory estimate; no current comparable supply audit", "Do not infer DPRK access from ROK platforms or combine populations silently.", "Unresolved.", "Obtain authoritative current supply/connectivity/access evidence before ranking."),
    p("GLB-046", "fil", "Filipino, Philippines", "fil-Latn-PH", "learned_national_standard", "Southeast Asia", ">=50M functional recall; >100M territory ceiling", "territory;functional unresolved", "NAT-033", "unresolved_no_comparable_count", "Old data used Tagalog-speaking households, not persons or Filipino functional reach.", "Philippines 2020 territory; pinned CLDR; PSA language source pending", "Filipino is not every learner's L1 and Tagalog household counts are not national competence.", "DepEd/TESDA/UPOU/STARBOOKS exist; home Internet gaps large.", "Resolve functional denominator; Filipino-English STEM-Kabuhayan with replaceable home-language tracks."),
    p("GLB-047", "my", "Burmese", "my-Mymr-MM", "national_standard", "Southeast Asia", ">=50M territory; functional below threshold", "territory;functional estimate", "NAT-030", "ranked_in_typed_view", "Keep territory and Burmese functional reach separate; displaced populations explicit.", "Myanmar territory and CLDR functional evidence", "Territory includes non-Burmese L1 communities.", "Supply disrupted and uneven.", "Emergency/offline foundational and transition packages with exact minority-language overlays."),
    p("GLB-048", "am", "Amharic", "am-Ethi-ET", "national_federal_working_standard", "Horn of Africa", ">=50M broad school/speaker estimate; L1 below", "L1;school estimate", "NAT-065", "ranked_in_typed_view", "Use exact old L1 and broad school estimate in separate views.", "Ethiopia 2007 census; UNICEF LOI estimate", "Broad estimate is not an exact written-reader count.", "Primary/official supply exists; tertiary/professional discontinuity.", "Secondary-tertiary STEM, professional/research bridge and offline delivery."),
    p("GLB-049", "om", "Oromo exact variety profiles", "gaz/hae/gax/orc; locale outputs unresolved", "macrolanguage_resolution", "Horn of Africa", "large regional; exact L1 below 50M in old census", "L1;territory", "NAT-066", "unresolved_no_comparable_count", "Replace macro-target with exact variety/standard outputs.", "Ethiopia 2007 census; Oromia projection", "Oromia territory and Oromo macrolanguage are not one edition population.", "Supply varies by variety and region.", "Resolve exact profiles and secondary/agriculture/health need."),
    p("GLB-050", "yo", "Standard Yoruba", "yo-Latn-NG", "regional_standard", "West Africa", "near/above 50M range", "speaker range;literacy shares unjoined", "NAT-070", "unresolved_no_comparable_count", "Retain range for recall but do not invent a joined written-reader denominator.", "Nigeria government approximation; NLSS literacy", "Nigeria territory and unjoined literacy percentages cannot be multiplied without matching strata.", "School/cultural supply exists; advanced practical supply thin.", "Resolve population/literacy join; STEM, health, finance and agriculture sequence."),
    p("GLB-051", "ig", "Standard Igbo", "ig-Latn-NG", "regional_standard", "West Africa", "material 25-33M", "speaker range;literacy shares unjoined", "NAT-071", "unresolved_no_comparable_count", "Below 50M but retained because the current candidate is unresolved and regionally important.", "Nigeria government approximation; NLSS", "Continuum and standardized literacy require evidence.", "Supply inventory incomplete.", "Resolve standard/profile and exact foundational-to-tertiary residual."),
    p("GLB-052", "bho", "Bhojpuri, India", "bho-Deva-IN", "regional_language_variety_set", "South Asia", ">=50M exact named L1 return", "L1", "NAT-125", "ranked_in_typed_view", "The exact 50,579,447 Indian Bhojpuri mother-tongue return is independently enumerated even though the printed census nests it inside the Hindi umbrella; this is a gross L1 opportunity view, not marginal reach.", "India Census 2011 C-16 Statement 1/workbook; ORGI Linguistic Survey of India—Bihar; Bihar SCERT/BSTBPC; IANA/Unicode CLDR", "The 50,579,447 count is a 2011 India mother-tongue return nested within the 528,347,193 Census Hindi umbrella; it is not a current, all-variety, literacy, academic-comfort, India-plus-Nepal, or diaspora count. Devanagari is a production default, not proof of one transregional standard.", "Official evidence shows Hindi-medium schooling and some Bhojpuri subject provision; no continuous open Bhojpuri-medium mathematics/STEM sequence has yet been evidenced.", "Declare a versioned Devanagari editorial register, inventory exact current supply, and commission the missing teacher-independent phone/offline foundational-numeracy-through-algebra sequence with Bhojpuri-to-Hindi bridge terms; keep Nepal and Mauritius outputs separate."),
    p("GLB-053", "cmn", "Putonghua, Mainland spoken standard", "cmn-Hans-CN for aligned text/audio; cmn-CN for speech-only metadata", "learned_spoken_standard", "Eastern Asia", ">=1B derived functional sensitivity", "functional communication prevalence", "NAT-122", "forward_residual_audit", "The spoken learned standard is a separate modality profile from Standard Written Chinese; it is relevant to narration, lectures, audio worked examples and spoken scaffolding.", "PRC 2020 census denominator; MOE/State Language Commission 2020 Putonghua prevalence survey", "The 1,139,587,786 sensitivity is 80.72% of the mainland census denominator, not an official speaker count, L1 count, home-language count, literacy measure or academic-comfort count. It is wholly nonadditive with zh-Hans-CN and all Sinitic profiles.", "Large broadcast and platform supply exists; no-account open/offline mathematical audio, transcript and speech-access coverage remains an exact format audit.", "Register spoken/audio outputs separately, preserve text/audio alignment, and award no direct written-reader or Sinitic-variety reach from this profile."),
    p("GLB-054", "ms", "Malaysian Malay", "ms-Latn-MY", "national_pluricentric_standard", "Southeast Asia", "regional constituent of >=250M architecture", "territory ceiling; direct language count unresolved", "NAT-040", "forward_residual_audit", "Malaysian Malay is a separately named output inside the Indonesian–Malaysian shared-source architecture and must not disappear behind the completed Indonesian edition.", "Malaysia PHC 2020; Dewan Bahasa dan Pustaka/MABBIM", "The rounded 32.4M Malaysia territory population and 20.6M Bumiputera count are not Malay-reader counts. Indonesian contributes zero direct Malaysian demographic reach without directed evidence.", "Malay-medium supply exists; the exact open/offline/teacher-independent advanced-mathematics and accessibility residual is not yet inventoried.", "Reuse the completed Indonesian semantic and terminology assets, but produce and audit an explicit ms-Latn-MY locale output; keep Brunei Rumi/Jawi derivatives separate."),
]


def b(
    aid: str, name: str, mechanism: str, outputs: str, universe: str,
    band: str, reach: str, reuse: str, candidates: str, evidence: str,
    exclusions: str, measurement: str,
) -> dict[str, str]:
    return dict(zip(BRIDGE_FIELDS, [
        aid, name, mechanism, outputs, universe, band, reach, reuse,
        candidates, evidence, exclusions, measurement,
    ]))


BRIDGES = [
    b("ARCH-001", "Standard Written Chinese localized package", "learned_written_standard", "zh-Hans-CN; zh-Hant-TW; zh-Hant-HK; zh-Hant-MO; zh-Hans-SG; optional zh-Hans-MY", "Mainland territory >1.4B plus separate locale cells", ">=1B", "No blanket spoken-Sinitic reach; named written-standard outputs only", "Very high semantic/toolchain reuse", "NAT-122", "PRC law/MOE; Taiwan/HK census; Unicode regional variation", "Wu, Yue vernacular, Taigi, Hakka and other Sinitic products remain separate", "Measure locale-specific source/QA token reuse and written academic comfort"),
    b("ARCH-002", "South Asian multilingual production system", "parallel_semantic_core_compute_only", "separate India/Pakistan/Bangladesh language-script outputs", ">1.35B current disjoint planning envelope", ">=1B", "Zero direct reader reach of the core", "Potentially very high shared formula/semantic/accessibility QA reuse", "", "Official India/Pakistan/Bangladesh population audits", "No pan-South-Asian reader surface or genealogy multiplier", "Measure core, locale, script and QA tokens per named output"),
    b("ARCH-003", "Global English overlap/accessibility baseline", "learned_lingua_franca", "plain English; locale overlays; bilingual glossaries", ">2B institutional first/additional-language diagnostic", ">=1B", "Unmeasured academic comfort; never unique reach by default", "High source reuse and accessibility leverage", "", "British Council diagnostic; national census cells", "Does not replace local-language editions", "Measure stage/subject comfort and exact plain/offline access gain"),
    b("ARCH-004", "Arabic MSA plus spoken-language scaffolds", "learned_written_standard", "arb written core plus Egyptian/Levantine/Iraqi/Gulf/Maghrebi/Yemeni/Sudanese/Hassaniya layers", "400-450M umbrella diagnostic", ">=250M", "Named outputs only; MSA not L1", "High formal-core and RTL reuse", "IL-AR", "UNESCO/UN; World Bank diglossia literature", "Non-Arabic L1 communities and dialect comfort remain separate", "Measure local oral scaffold effect by stage/task"),
    b("ARCH-005", "Romance localized/intercomprehension core", "natural_intercomprehension_and_pluricentric_reuse", "Spanish; Portuguese; French; optional research bridge", "Nonadditive >1B headline speaker estimates", ">=250M", "Only directed written comprehension receives reach", "High terminology/source reuse", "IL-ROM", "Spanish-Portuguese directed studies; MICReLa", "No one pan-Romance replacement or summed audience", "Measure mathematical expert/novice written comprehension and locale token reuse"),
    b("ARCH-006", "Hindi-Urdu two-script core", "pluricentric_shared_core", "hi-Deva-IN; ur-Aran-IN; ur-Aran-PK", "395,205,166 exact named L1 cells", ">=250M", "No demonstrated untrained academic-text cross-script reach", "High semantic/formula reuse", "IL-HU;NAT-124;NAT-012;NAT-013", "India/Pakistan censuses; ACL transfer evidence", "Hindi umbrella subsidiaries remain separate", "Measure transliteration/locale QA and directed educational comprehension"),
    b("ARCH-007", "Indonesian-Malaysian Malay package", "pluricentric_shared_core", "id-Latn-ID; ms-Latn-MY; Brunei/Jawi named derivatives", "~274M functional diagnostic; ~319M territory ceiling", ">=250M", "Only each named locale population receives direct reach", "Very high MABBIM/terminology reuse", "IL-IDMS;NAT-121;NAT-040", "BPS; MABBIM; current Indonesian completion receipts", "Javanese, Sundanese, Madurese and other languages excluded", "Measure Malaysian/Bruneian locale delta after completed Indonesian source"),
    b("ARCH-008", "Bangla Bangladesh-India shared core", "pluricentric_shared_core", "bn-Beng-BD; bn-Beng-IN", "~264.6M L1 diagnostic", ">=250M", "Two distinct locale outputs", "High same-script semantic reuse", "NAT-001;NAT-002", "Bangladesh PHC/SEDS; India C-16/C-17", "No locale-neutral curriculum or professional overlay", "Measure source reuse and locale-specific terminology/examples"),
    b("ARCH-009", "Russian learned-standard overlap", "learned_lingua_franca", "ru-Cyrl locale/localization outputs", ">250M institutional diagnostic", ">=250M", "Unique residual unmeasured", "High source/localization reuse", "", "Rosstat; UNESCO diagnostic", "No blanket ex-Soviet/Indigenous/displaced coverage", "Measure academic comfort and local-language nonoverlap"),
    b("ARCH-010", "Standard Kiswahili country package", "learned_lingua_franca", "swh-TZ; swh-KE; swh-UG; swc-CD regional outputs", ">200M institutional diagnostic", ">=100M", "Named country/variety outputs only", "High standard-core reuse", "NAT-063;NAT-064", "UNESCO/AU; country censuses; EAKC", "DRC varieties and non-Swahili L1 communities remain", "Measure country-layer delta and written comfort"),
    b("ARCH-011", "Dravidian parallel pipeline", "parallel_semantic_core_compute_only", "te; ta-IN/ta-LK; kn; ml outputs", "228,084,103 exact Indian L1 components before Sri Lanka", ">=100M", "Zero core reach", "Shared formula, layout and QA only unless measured", "NAT-003;NAT-004;NAT-005;NAT-008;NAT-009", "India C-16/C-17; Sri Lanka census", "Genealogy supplies no comprehension multiplier", "Measure actual reused tokens across named scripts/outputs"),
    b("ARCH-012", "Slavic/Interslavic supplementary bridge", "constructed_bridge", "dual-script Interslavic plus native outputs", "~266-320M family ceiling", ">=250M", "Current short-task evidence is not demographic reach", "Terminology/semantic reuse plausible", "IL-ISV", "Interslavic seven-gap study", "Russian/Ukrainian bias and communities not tested remain explicit", "Test mathematics by expertise, script and task; measure production reuse"),
    b("ARCH-013", "Turkic branch production", "parallel_semantic_core_and_constructed_hypothesis", "Oghuz, Kipchak, Karluk named outputs", "~200M family; Oghuz ~110-120M", ">=100M", "No pan-Turkic direct reach", "Branch terminology/model reuse plausible", "IL-TURKIC", "Directed Turkish-Azerbaijani evidence; regional population sources", "No family-wide standard or comprehension", "Measure per-branch reuse and directed text comprehension"),
    b("ARCH-014", "Persian-Dari-Tajik core", "pluricentric_shared_core", "fa-IR; prs-AF; tg-Cyrl-TJ", "~102M functional diagnostic; ~147M territory ceiling", ">=100M", "Named outputs only", "High semantic reuse with script/locale deltas", "IL-PDT;NAT-058;NAT-049", "National/diagnostic sources", "No one script/register or additive comfort count", "Resolve exact counts and measure script/terminology delta"),
    b("ARCH-015", "Punjabi dual-script core", "dual_script_register", "pa-Guru-IN; pa-Arab-PK", "120,059,639 exact source-labelled L1 cells", ">=100M", "Separate scripts/locale reach only", "High semantic and transliteration assistance", "IL-PUNJABI;NAT-014;NAT-015", "India/Pakistan censuses; COLING transliteration study", "Pakistan variety identity and cross-script literacy unresolved", "Resolve Pakistan profile and measure post-edit/QA cost"),
    b("ARCH-016", "Hausa country/orthography package", "learned_lingua_franca_shared_core", "ha-Latn-NG; ha-Latn-NE; optional established Ajami layers", "Cross-border >=100M plausible but unverified", "80-100M watch / unresolved", "No bankable cross-border written reach", "Strong shared-source potential", "NAT-069", "Hausa scholarship; Nigeria/Niger orthography evidence", "No universal Ajami or territory-wide reach", "Obtain compatible population/literacy evidence and measure country delta"),
]


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest().upper()
    return digest


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    candidate_path = ROOT / "candidate_interventions_master.csv"
    with candidate_path.open("r", encoding="utf-8-sig", newline="") as handle:
        candidate_ids = {row["intervention_id"] for row in csv.DictReader(handle)}

    profile_ids = [row["universe_profile_id"] for row in PROFILES]
    errors: list[str] = []
    if len(profile_ids) != len(set(profile_ids)):
        errors.append("duplicate expected-profile IDs")
    unexpected_dispositions = sorted({
        row["disposition"] for row in PROFILES
        if row["disposition"] not in ALLOWED_DISPOSITIONS
    })
    if unexpected_dispositions:
        errors.append(f"unexpected profile dispositions: {unexpected_dispositions}")
    observed_codes = {row["recall_code"] for row in PROFILES}
    missing_50 = sorted(RECALL_50M - observed_codes)
    missing_watch = sorted(WATCH_40M - observed_codes)
    if missing_50 or missing_watch:
        errors.append(f"recall universe incomplete: 50M={missing_50}, watch={missing_watch}")

    unknown_candidate_refs: dict[str, list[str]] = {}
    for row in PROFILES:
        unknown = [item for item in row["candidate_ids"].split(";") if item and item not in candidate_ids]
        if unknown:
            unknown_candidate_refs[row["universe_profile_id"]] = unknown
    for row in BRIDGES:
        unknown = [item for item in row["candidate_ids"].split(";") if item and item not in candidate_ids]
        if unknown:
            unknown_candidate_refs[row["architecture_id"]] = unknown
    if unknown_candidate_refs:
        errors.append(f"unknown candidate references: {unknown_candidate_refs}")

    profile_path = OUT / "expected_language_profiles_v1_1.csv"
    bridge_path = OUT / "bridge_shared_core_hypotheses_v1_1.csv"
    validation_path = OUT / "expected_universe_validation_v1_1.json"
    checks = {
        "unique_profile_ids": len(profile_ids) == len(set(profile_ids)),
        "allowed_dispositions_only": not unexpected_dispositions,
        "recall_50m_complete": not missing_50,
        "watch_40m_complete": not missing_watch,
        "all_candidate_references_resolve": not unknown_candidate_refs,
        "bhojpuri_india_exact_profile_present": sum(
            row["universe_profile_id"] == "GLB-052"
            and row["candidate_ids"] == "NAT-125"
            and row["profile_tag"] == "bho-Deva-IN"
            for row in PROFILES
        ) == 1,
        "putonghua_spoken_modality_present": sum(
            row["universe_profile_id"] == "GLB-053"
            and row["recall_code"] == "cmn"
            and "spoken" in row["display_name"].lower()
            for row in PROFILES
        ) == 1,
        "malaysian_malay_constituent_present": sum(
            row["universe_profile_id"] == "GLB-054"
            and row["candidate_ids"] == "NAT-040"
            and row["profile_tag"] == "ms-Latn-MY"
            for row in PROFILES
        ) == 1,
    }
    status = "PASS" if all(checks.values()) and not errors else "FAIL"
    if status != "PASS":
        validation_path.write_text(json.dumps({
            "schema": "interlanguage/global-expected-universe-validation/1.1.0",
            "status": status,
            "checks": checks,
            "errors": errors,
            "missing_recall_codes": {"50m": missing_50, "watch_40m": missing_watch},
            "unknown_candidate_references": unknown_candidate_refs,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        raise SystemExit("FAIL\n" + "\n".join(errors))

    write_csv(profile_path, PROFILE_FIELDS, PROFILES)
    write_csv(bridge_path, BRIDGE_FIELDS, BRIDGES)

    validation = {
        "schema": "interlanguage/global-expected-universe-validation/1.1.0",
        "status": status,
        "checks": checks,
        "profile_rows": len(PROFILES),
        "bridge_rows": len(BRIDGES),
        "recall_50m_expected": sorted(RECALL_50M),
        "recall_50m_covered": sorted(RECALL_50M & observed_codes),
        "watch_40m_expected": sorted(WATCH_40M),
        "watch_40m_covered": sorted(WATCH_40M & observed_codes),
        "missing_recall_codes": {"50m": missing_50, "watch_40m": missing_watch},
        "unknown_candidate_references": unknown_candidate_refs,
        "disposition_counts": {
            disposition: sum(row["disposition"] == disposition for row in PROFILES)
            for disposition in sorted(ALLOWED_DISPOSITIONS)
        },
        "invariants": {
            "independent_universe_before_ranking": True,
            "typed_denominators_only": True,
            "macrolanguage_not_single_rankable_population": True,
            "shared_core_has_no_automatic_demographic_reach": True,
            "supply_rich_profiles_remain_enumerated": True,
        },
        "outputs": {
            profile_path.name: {"bytes": profile_path.stat().st_size, "sha256": sha256(profile_path)},
            bridge_path.name: {"bytes": bridge_path.stat().st_size, "sha256": sha256(bridge_path)},
        },
        "inputs": {
            candidate_path.name: {"bytes": candidate_path.stat().st_size, "sha256": sha256(candidate_path)},
        },
        "limitations": [
            "This is a recall/disposition universe, not a cardinal rank.",
            "Several profiles remain unresolved because comparable written-reader or academic-comfort counts do not exist in the current evidence base.",
            "The 50M and 40M thresholds are recall gates, not normative priorities.",
        ],
    }
    validation_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "profiles": len(PROFILES),
        "bridges": len(BRIDGES),
        "profile_sha256": sha256(profile_path),
        "bridge_sha256": sha256(bridge_path),
        "validation_sha256": sha256(validation_path),
    }, indent=2))


if __name__ == "__main__":
    main()
