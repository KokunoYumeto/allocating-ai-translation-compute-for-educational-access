#!/usr/bin/env python3
"""Build source-defined population observations missing from the legacy master.

This supplement is intentionally conservative.  It records the denominator a
source actually reports (home use, functional ability, institutional estimate,
or territory population) and never promotes a territorial or gross language
count into a count of underserved comfortable readers.  Alternative measures
for the same profile are explicitly non-additive.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from decimal import Decimal, ROUND_CEILING
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UNIVERSE = ROOT / "staging" / "global_expected_universe" / "expected_language_profiles_v1_1.csv"
UNIVERSE_VALIDATION = ROOT / "staging" / "global_expected_universe" / "expected_universe_validation_v1_1.json"
MASTER_OBSERVATIONS = ROOT / "population_observations_master.csv"
OUT_DIR = ROOT / "staging" / "global_expected_universe"
OUT_CSV = OUT_DIR / "profile_population_estimates_supplement_v1_1.csv"
OUT_JSON = OUT_DIR / "profile_population_estimates_supplement_validation_v1_1.json"

FIELDS = [
    "supplement_id", "universe_profile_id", "display_name", "profile_tag",
    "denominator_class", "measure_type", "learner_stratum", "count_unit",
    "population_low", "population_base", "population_high",
    "reference_date_or_year", "source_id", "source_authority", "source_url",
    "source_locator", "source_value_status", "derivation_method",
    "source_transcribed_exactly", "source_series_id", "overlap_group_id",
    "nonadditivity_group_id", "nonadditivity_rule", "supersedes_observation_ids",
    "typed_view_eligibility", "population_use",
    "rank_ready_marginal_access", "uncertainty", "notes",
]


def row(
    sid: str,
    profile_id: str,
    display_name: str,
    profile_tag: str,
    denominator_class: str,
    measure_type: str,
    learner_stratum: str,
    base: int | float | str,
    year: str,
    authority: str,
    url: str,
    locator: str,
    status: str,
    overlap_group_id: str,
    uncertainty: str,
    notes: str,
    *,
    low: int | float | str = "",
    high: int | float | str = "",
    unit: str = "persons",
    derivation: str = "none",
    typed_view_eligibility: str = "context_only",
) -> dict[str, str]:
    return {
        "supplement_id": sid,
        "universe_profile_id": profile_id,
        "display_name": display_name,
        "profile_tag": profile_tag,
        "denominator_class": denominator_class,
        "measure_type": measure_type,
        "learner_stratum": learner_stratum,
        "count_unit": unit,
        "population_low": str(low),
        "population_base": str(base),
        "population_high": str(high),
        "reference_date_or_year": year,
        "source_id": "",
        "source_authority": authority,
        "source_url": url,
        "source_locator": locator,
        "source_value_status": status,
        "derivation_method": derivation,
        "source_transcribed_exactly": "",
        "source_series_id": overlap_group_id,
        "overlap_group_id": overlap_group_id,
        "nonadditivity_group_id": "",
        "nonadditivity_rule": "",
        "supersedes_observation_ids": "",
        "typed_view_eligibility": typed_view_eligibility,
        "population_use": "gross_or_context_typed_view_only_not_direct_residual_rank",
        "rank_ready_marginal_access": "false",
        "uncertainty": uncertainty,
        "notes": notes,
    }


ROWS = [
    row(
        "SUP-001", "GLB-001", "English at home, United States", "en-Latn-US",
        "home_or_usual_language_use", "acs_speak_only_english_at_home_age5plus",
        "United States residents age 5+", 247_695_110, "2024",
        "United States Census Bureau, ACS 1-year S1601",
        "https://data.census.gov/table/ACSST1Y2024.S1601?g=010XX00US",
        "S1601, United States, population age 5+, Speak only English",
        "published_estimate", "EN-US-ACS-2024",
        "Sampling estimate; not L1, literacy, academic comfort, or unique access.",
        "Negative-control context for existing English supply.",
    ),
    row(
        "SUP-002", "GLB-001", "English-only or very-well English, United States", "en-Latn-US",
        "functional_language_ability_or_estimate", "acs_english_only_or_speaks_english_very_well_age5plus",
        "United States residents age 5+", 292_827_195, "2024",
        "United States Census Bureau, ACS 1-year S1601",
        "https://data.census.gov/table/ACSST1Y2024.S1601?g=010XX00US",
        "S1601; English only plus non-English home-language population speaking English very well",
        "published_or_exactly_summed_source_cells", "EN-US-ACS-2024",
        "Self-rated speaking ability; not reading, academic comfort, or unique educational access.",
        "Alternative to SUP-001; never add them.",
        derivation="sum of mutually exclusive published S1601 strata",
    ),
    row(
        "SUP-003", "GLB-001", "English main language or proficient, England", "en-Latn-GB-ENG",
        "functional_language_ability_or_estimate", "census_main_language_or_speaks_english_well_very_well_age3plus",
        "England residents age 3+", 53_667_911, "2021",
        "Office for National Statistics via Nomis, Census 2021 TS029",
        "https://www.nomisweb.co.uk/api/v01/dataset/NM_2048_1.data.csv?geography=E92000001&c2021_engprf_6=0,1,2,3,4,5&measures=20100",
        "England; English main language plus speaks English well and very well",
        "exact_census_cells_summed", "EN-GB-CENSUS-2021",
        "Speaking proficiency and main language; not an academic-reading measure.",
        "Country observation; do not add to a modeled global English total without overlap control.",
        derivation="49,652,172 + 2,212,300 + 1,803,439",
    ),
    row(
        "SUP-004", "GLB-003", "Taiwan resident nationals age 6+", "zh-Hant-TW",
        "territory_age_restricted_ceiling", "census_resident_nationals_age6plus",
        "Taiwan resident nationals age 6+", 21_786_490, "2020",
        "Taiwan Directorate-General of Budget, Accounting and Statistics, 2020 Census",
        "https://ws.dgbas.gov.tw/001/Upload/463/relfile/11064/230649/0b703c3e-23af-471f-a1f6-555315ca0ce2.pdf",
        "language-use tables, resident nationals age 6+ universe",
        "published_census_universe", "ZH-HANT-TW-2020",
        "Territory/age universe, not a Guoyu or traditional-character comfort count.",
        "Hard ceiling for the two derived percentage observations below.",
    ),
    row(
        "SUP-005", "GLB-003", "Guoyu first learned, Taiwan", "zh-Hant-TW",
        "first_learned_language_derived_from_percentage", "census_first_learned_guoyu_share",
        "Taiwan resident nationals age 6+", 8_801_742, "2020",
        "Taiwan Directorate-General of Budget, Accounting and Statistics, 2020 Census",
        "https://ws.dgbas.gov.tw/001/Upload/463/relfile/11064/230649/0b703c3e-23af-471f-a1f6-555315ca0ce2.pdf",
        "40.4% first learned Guoyu; age 6+ census universe 21,786,490",
        "derived_from_published_rounded_percentage", "ZH-HANT-TW-2020",
        "Bounds reflect only rounding of 40.4% to the nearest 0.1 percentage point; source nonresponse/model uncertainty is not quantified.",
        "First-learned Guoyu is not total Guoyu use or literacy in traditional characters.",
        low=8_790_849, high=8_812_635,
        derivation="21,786,490 × 40.4%; bounds use 40.35%–40.45%",
        typed_view_eligibility="typed_first_learned_view",
    ),
    row(
        "SUP-006", "GLB-003", "Guoyu primary-or-secondary use, Taiwan", "zh-Hant-TW",
        "functional_language_ability_or_estimate", "census_primary_or_secondary_guoyu_use_share",
        "Taiwan resident nationals age 6+", 21_089_322, "2020",
        "Taiwan Directorate-General of Budget, Accounting and Statistics, 2020 Census",
        "https://ws.dgbas.gov.tw/001/Upload/463/relfile/11064/230649/0b703c3e-23af-471f-a1f6-555315ca0ce2.pdf",
        "96.8% primary-or-secondary Guoyu use; age 6+ census universe 21,786,490",
        "derived_from_published_rounded_percentage", "ZH-HANT-TW-2020",
        "Bounds reflect percentage rounding only; use does not establish reading comfort or unique access.",
        "Alternative to SUP-004 and SUP-005; never add them.",
        low=21_078_430, high=21_100_215,
        derivation="21,786,490 × 96.8%; bounds use 96.75%–96.85%",
        typed_view_eligibility="typed_functional_use_view",
    ),
    row(
        "SUP-008", "GLB-024", "Spanish native-domain group, global model", "es; locale outputs required",
        "published_or_derived_speaker_estimate", "instituto_cervantes_grupo_dominio_nativo",
        "Modeled global native-domain group", 519_115_258, "2025",
        "Instituto Cervantes, El español en el mundo 2025",
        "https://cvc.cervantes.es/lengua/anuario/anuario_25/el_espanol_en_el_mundo_anuario_instituto_cervantes_2025.pdf",
        "Table 4, p. 67; Grupo de Dominio Nativo (GDN)",
        "published_institutional_model", "ES-CERVANTES-2025",
        "Not a synchronized global census; not locale-specific and not an underserved-reader count.",
        "Negative-control gross context. Do not add GCL or learners to this row unless reproducing the report's total model.",
    ),
    row(
        "SUP-009", "GLB-024", "Spanish spoken at home, United States", "es-US",
        "home_or_usual_language_use", "acs_spanish_spoken_at_home_age5plus",
        "United States residents age 5+", 44_867_699, "2024",
        "United States Census Bureau, ACS 1-year B16001",
        "https://data.census.gov/table/ACSDT1Y2024.B16001?g=010XX00US",
        "B16001 Spanish spoken at home; published 90% margin of error 143,192",
        "published_estimate_with_margin", "ES-US-ACS-2024",
        "Home use is not L1, literacy, academic comfort, or an es-419 curriculum profile.",
        "Country observation; no addition to SUP-008 without a global overlap model.",
        low=44_724_507, high=45_010_891,
        typed_view_eligibility="typed_home_language_view",
    ),
    row(
        "SUP-010", "GLB-025", "Portuguese speakers, global institutional estimate", "pt; locale outputs required",
        "published_or_derived_speaker_estimate", "un_global_portuguese_speaker_estimate",
        "Unspecified global speaker universe", "", "2026",
        "United Nations, Secretary-General message for World Portuguese Language Day",
        "https://www.un.org/sg/en/content/sg/statements/2026-05-05/secretary-generals-message-world-portuguese-language-day",
        "Statement: Portuguese unites more than 265 million speakers",
        "published_rounded_lower_bound", "PT-UN-2026",
        "No disclosed L1/L2, age, proficiency, literacy, or census method.",
        "Gross threshold evidence only; never substitute for pt-BR, pt-PT, or PALOP locale populations.",
        low=265_000_000,
    ),
    row(
        "SUP-011", "GLB-025", "Brazil territory population", "pt-BR",
        "territory_all_residents_ceiling", "official_census_territory_population",
        "Brazil residents", 203_080_756, "2022",
        "Instituto Brasileiro de Geografia e Estatística, 2022 Census",
        "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Populacao_e_domicilios_Primeiros_resultados/Resultados_da_2a_apuracao_20231027/POP2022_Municipios_Primeiros_Resultados_20231222.pdf",
        "Brazil total population, second apportionment",
        "published_exact_census_total", "PT-BR-2022",
        "Territory population is not a Portuguese-language or literacy count.",
        "Country ceiling and non-additive alternative to global SUP-010.",
    ),
    row(
        "SUP-012", "GLB-026", "Francophones, continuing OIF method", "fr; locale outputs required",
        "functional_language_ability_or_estimate", "oif_method_1_french_competence_estimate",
        "Modeled global French-competence population", 348_000_000, "2025",
        "Organisation internationale de la Francophonie, 2026 report",
        "https://www.francophonie.org/sites/default/files/2026-03/La_langue_francaise_dans_le_monde_Edition_2026.pdf",
        "2025 estimate under continuing method 1",
        "published_rounded_institutional_model", "FR-OIF-2025",
        "Heterogeneous source model; not L1, uniform literacy, locale fit, or unique access.",
        "Preferred continuity series; do not add to SUP-013.",
    ),
    row(
        "SUP-013", "GLB-026", "Francophones, broadened OIF method", "fr; locale outputs required",
        "functional_language_ability_or_estimate", "oif_method_2_including_schooled_literate_children_6_9",
        "Modeled global French-competence and schooling population", 396_000_000, "2025",
        "Organisation internationale de la Francophonie, 2026 report",
        "https://www.francophonie.org/sites/default/files/2026-03/La_langue_francaise_dans_le_monde_Edition_2026.pdf",
        "2025 estimate under method 2",
        "published_rounded_institutional_model", "FR-OIF-2025",
        "Method 2 adds pupils age 6–9 in 30 Global-South countries; not comparable to the older time series.",
        "Sensitivity alternative to SUP-012; never add them.",
    ),
    row(
        "SUP-014", "GLB-027", "Russian knowledge, Russian Federation", "ru-Cyrl-RU",
        "functional_language_ability_or_estimate", "census_reports_knowledge_of_russian",
        "Respondents answering language-knowledge question", 134_319_233, "2021-10-01",
        "Rosstat, 2020 Census Volume 5 Table 4",
        "https://rosstat.gov.ru/storage/mediabank/Tom5_tab4_VPN-2020.xlsx",
        "Russian knowledge row; census reference date 1 October 2021",
        "published_exact_census_cell", "RU-ROSSTAT-2021",
        "Knowledge means speak/read/write or only speak; written competence cannot be isolated.",
        "Alternative to daily-use SUP-015; never add them.",
        typed_view_eligibility="typed_functional_knowledge_view",
    ),
    row(
        "SUP-015", "GLB-027", "Russian daily use, Russian Federation", "ru-Cyrl-RU",
        "home_or_usual_language_use", "census_reports_daily_use_of_russian",
        "Respondents answering language-use question", 132_317_159, "2021-10-01",
        "Rosstat, 2020 Census Volume 5 Table 4",
        "https://rosstat.gov.ru/storage/mediabank/Tom5_tab4_VPN-2020.xlsx",
        "Russian daily-use row; census reference date 1 October 2021",
        "published_exact_census_cell", "RU-ROSSTAT-2021",
        "Daily use does not isolate literacy, academic comfort, or exclusive Russian reliance.",
        "Alternative to knowledge SUP-014; never add them.",
        typed_view_eligibility="typed_daily_use_view",
    ),
    row(
        "SUP-016", "GLB-028", "Only German at home, Germany", "de-Latn-DE",
        "home_or_usual_language_use", "microcensus_only_german_used_at_home",
        "Germany private-household population", 63_433_000, "2024",
        "German Federal Statistical Office, Microcensus table 12211-47",
        "https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Bevoelkerung/Migration-Integration/Publikationen/Downloads-Migration/statistischer-bericht-migrationshintergrund-end-2010220247005.xlsx?__blob=publicationFile&v=3",
        "Table 12211-47, only German at home",
        "published_rounded_survey_estimate", "DE-MICROCENSUS-2024",
        "Annual 1% survey; communal accommodation excluded; home use is not literacy or academic need.",
        "Negative-control same-country measure.",
        typed_view_eligibility="typed_home_language_view",
    ),
    row(
        "SUP-017", "GLB-028", "Any German at home, Germany", "de-Latn-DE",
        "home_or_usual_language_use", "derived_any_german_used_at_home",
        "Germany private-household population", 77_847_000, "2024",
        "German Federal Statistical Office, Microcensus table 12211-47",
        "https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Bevoelkerung/Migration-Integration/Publikationen/Downloads-Migration/statistischer-bericht-migrationshintergrund-end-2010220247005.xlsx?__blob=publicationFile&v=3",
        "Only German + predominantly German + German with another language",
        "derived_sum_of_published_rounded_cells", "DE-MICROCENSUS-2024",
        "Derived from cells published in thousands; not a proficiency or literacy test.",
        "Alternative to SUP-016; never add them.",
        derivation="63,433,000 + 3,810,000 + 10,604,000",
    ),
    row(
        "SUP-018", "GLB-029", "Italian used in at least one social context", "it-Latn-IT",
        "home_or_usual_language_use", "survey_speaks_italian_in_at_least_one_context",
        "Italy resident population age 6+", 47_611_000, "2024",
        "Italian National Institute of Statistics, language-use survey",
        "https://www.istat.it/comunicato-stampa/luso-della-lingua-italiana-dei-dialetti-e-delle-lingue-straniere-anno-2024/",
        "Italian used in at least one of family, friends, or strangers contexts",
        "published_survey_estimate", "IT-ISTAT-2024",
        "Below 50 million on this measure; not literacy or academic comfort.",
        "Retains Italian as a supply-rich watch profile rather than manufacturing a threshold crossing.",
        typed_view_eligibility="typed_habitual_use_view",
    ),
    row(
        "SUP-019", "GLB-030", "Poland territory population", "pl-Latn-PL",
        "territory_all_residents_ceiling", "official_population_balance_territory_population",
        "Poland residents", 37_489_000, "2024-12-31",
        "Statistics Poland, Demographic situation in Poland up to 2024",
        "https://stat.gov.pl/files/gfx/portalinformacyjny/pl/defaultaktualnosci/5468/40/5/1/sytuacja_demograficzna_polski_do_2024.pdf",
        "Population at end of 2024",
        "published_rounded_official_total", "PL-STAT-2024",
        "Territory only and below 50 million; not a Polish-language count.",
        "Negative-control watch profile.",
    ),
    row(
        "SUP-020", "GLB-031", "Arabic forms, UNESCO gross global estimate", "arb-Arab plus spoken-language scaffolds",
        "published_or_derived_speaker_estimate", "unesco_arabic_used_daily_gross_estimate",
        "Unspecified global users across Arabic forms", "", "current UNESCO page",
        "UNESCO, World Arabic Language Day",
        "https://www.unesco.org/en/world-arabic-language-day",
        "Arabic used daily by more than 400 million people",
        "published_rounded_lower_bound", "AR-UNESCO-GROSS",
        "Arabic is internally diverse; the figure does not measure MSA literacy, one spoken variety, or academic comfort.",
        "Gross recall evidence only. It must not be credited as direct reach for one MSA-only edition.",
        low=400_000_000,
    ),
    row(
        "SUP-021", "GLB-035", "Türkiye territory population", "tr-Latn-TR",
        "territory_all_residents_ceiling", "administrative_register_territory_population",
        "Residents of Türkiye", 85_664_944, "2024-12-31",
        "Turkish Statistical Institute, Address Based Population Registration System 2024",
        "https://veriportali.tuik.gov.tr/en/press/53783",
        "National resident population as of 31 December 2024",
        "published_exact_administrative_total", "TR-TUIK-2024",
        "Territory population is not a Turkish reader or academic-comfort count.",
        "Strong official-language/territory proxy only.",
    ),
    row(
        "SUP-022", "GLB-036", "Tanzania territory population", "swh-Latn-TZ",
        "territory_all_residents_ceiling", "official_census_territory_population",
        "Tanzania residents", 61_741_120, "2022",
        "Tanzania National Bureau of Statistics, 2022 Census",
        "https://sensa.nbs.go.tz/dissemination/results",
        "2022 national census population",
        "published_exact_census_total", "SWAHILI-COUNTRY-TERRITORY",
        "Territory does not equal comfortable Standard Kiswahili readership.",
        "Country ceiling; keep separate from Kenya, Uganda, DRC, and global users.",
    ),
    row(
        "SUP-023", "GLB-036", "Kenya territory population", "swh-Latn-KE",
        "territory_all_residents_ceiling", "official_census_territory_population",
        "Kenya residents", 47_564_296, "2019",
        "Kenya National Bureau of Statistics, 2019 Census",
        "https://www.knbs.or.ke/2019-kenya-population-and-housing-census-results/",
        "2019 national census population",
        "published_exact_census_total", "SWAHILI-COUNTRY-TERRITORY",
        "Territory does not equal comfortable Standard Kiswahili readership.",
        "Country ceiling; not additive to the UNESCO global gross count.",
    ),
    row(
        "SUP-024", "GLB-036", "Uganda territory population", "swh-Latn-UG",
        "territory_all_residents_ceiling", "official_census_territory_population",
        "Uganda residents", 45_905_417, "2024",
        "Uganda Bureau of Statistics, 2024 Census",
        "https://statistics.ubos.org/nphc/index",
        "2024 national census population",
        "published_exact_census_total", "SWAHILI-COUNTRY-TERRITORY",
        "Kiswahili is being expanded largely as an L2; territory is not current functional reach.",
        "Country ceiling; not additive to the UNESCO global gross count.",
    ),
    row(
        "SUP-025", "GLB-036", "Kiswahili gross global users", "swh/swc; locale outputs required",
        "published_or_derived_speaker_estimate", "unesco_kiswahili_global_user_estimate",
        "Unspecified L1/L2 global user universe", "", "2025",
        "UNESCO",
        "https://www.unesco.org/en/articles/kiswahili-bridge-cultural-diversity-dialogue-and-digital-innovation",
        "More than 200 million speakers/users",
        "published_rounded_lower_bound", "SWAHILI-GLOBAL-GROSS",
        "No synchronized proficiency, literacy, age, or locale definition; includes very different L1/L2 situations.",
        "Gross shared-core sensitivity only; do not allocate it to any one country edition.",
        low=200_000_000,
    ),
    row(
        "SUP-026", "GLB-037", "Hausa L1 estimate", "ha-Latn-NG; ha-Latn-NE",
        "published_or_derived_speaker_estimate", "literature_estimated_first_language_speakers",
        "Unspecified global L1 universe", 58_000_000, "2022",
        "Paul Newman, A History of the Hausa Language",
        "https://assets.cambridge.org/97810091/24300/excerpt/9781009124300_excerpt.pdf",
        "Introductory speaker estimate near 60 million L1",
        "published_rounded_literature_estimate", "HAUSA-GLOBAL-ESTIMATES",
        "Rounded literature estimate; does not define literacy, script, or country locale.",
        "Alternative to total-user SUP-027; never add them.",
    ),
    row(
        "SUP-027", "GLB-037", "Hausa total-user estimate", "ha-Latn-NG; ha-Latn-NE",
        "published_or_derived_speaker_estimate", "literature_estimated_l1_l2_users",
        "Unspecified global L1/L2 universe", 94_000_000, "2022",
        "Paul Newman / World Bank cross-border education synthesis",
        "https://documents1.worldbank.org/curated/en/099150306212220991/pdf/P176149083852a0500af9a09c2327c00d37.pdf",
        "Broad Hausa user universe reported in cross-border synthesis",
        "published_rounded_literature_estimate", "HAUSA-GLOBAL-ESTIMATES",
        "Rounded heterogeneous estimate; written boko/Ajami proficiency and locale not established.",
        "Alternative to L1 SUP-026; never add them.",
    ),
    row(
        "SUP-028", "GLB-038", "Nigerian Pidgin oral-use estimate", "pcm-Latn-NG",
        "published_or_derived_speaker_estimate", "literature_estimated_oral_users",
        "Nigeria oral L1/L2 user universe", "", "2024",
        "Kofi Yakpo, language-use synthesis",
        "https://journals.sagepub.com/doi/10.1177/00020397241263364",
        "Published range 80–112 million oral users",
        "published_literature_interval", "PCM-NG-ORAL-2024",
        "Oral use does not establish written orthography uptake or educational reading.",
        "Audio-first sensitivity; written reader reach stays unresolved.",
        low=80_000_000, high=112_000_000,
        derivation="published interval only; no point estimate",
    ),
    row(
        "SUP-029", "GLB-044", "Republic of Korea territory population", "ko-Kore-KR",
        "territory_all_residents_ceiling", "official_census_territory_population",
        "Republic of Korea census population", 51_829_136, "2020",
        "Statistics Korea, 2020 Population and Housing Census",
        "https://sri.kostat.go.kr/boardDownload.es?bid=203&list_no=391020&seq=17",
        "National total population",
        "published_exact_census_total", "KO-KR-2020",
        "Territory includes non-Korean home-language populations and does not measure literacy or academic comfort.",
        "ROK only; no inference about DPRK.",
    ),
    row(
        "SUP-030", "GLB-046", "Philippines territory population", "fil-Latn-PH",
        "territory_all_residents_ceiling", "official_census_territory_population",
        "Philippines residents", 109_035_343, "2020-05-01",
        "Philippine Statistics Authority, 2020 Census of Population and Housing",
        "https://psa.gov.ph/content/2020-census-population-and-housing-2020-cph-population-counts-declared-official-president",
        "Official national population count",
        "published_exact_census_total", "FIL-PH-2020",
        "Territory is not Filipino L1, functional literacy, or comfortable-reader reach; Filipino is not every learner's home language.",
        "Use only as a ceiling while functional Filipino reach remains unresolved.",
    ),
    row(
        "SUP-032", "GLB-048", "Amharic language-of-instruction reach estimate", "am-Ethi-ET",
        "education_cohort", "published_language_of_instruction_population_estimate",
        "Broad school language-of-instruction population", 56_900_000, "2018 estimate",
        "UNICEF Foundational Learning Hub, language-of-instruction module",
        "https://www.unicef.org/flnhub/fr/media/1866/file/Module-4-Language-of-instruction-PPT-%28English%29.pdf.pdf",
        "Amharic broad language-of-instruction estimate",
        "published_rounded_program_estimate", "AMH-ET-LOI",
        "Not L1, not a census, and not measured comfortable readership.",
        "Alternative educational-reach sensitivity to master observation POP-ET-002; never add them.",
    ),
    row(
        "SUP-034", "GLB-049", "Oromia territory projection", "gaz/hae/gax/orc unresolved",
        "territory_all_residents_ceiling", "official_regional_population_projection",
        "Residents of Oromia region", 42_689_000, "2025 projection",
        "Ethiopian Statistics Service, projected population 2025",
        "https://ess.gov.et/wp-content/uploads/2026/04/projected_population-2025-g.c.pdf",
        "Oromia regional projection",
        "published_rounded_official_projection", "OROMO-ET-REGION",
        "Region is multilingual; projection is not an Oromo-language or reader count.",
        "Alternative ceiling to master observation POP-ET-001; never add them.",
    ),
    row(
        "SUP-035", "GLB-005", "Cantonese usual spoken language, Hong Kong", "yue-Hant-HK spoken profile",
        "home_or_usual_language_use", "census_cantonese_usual_spoken_language_age5plus",
        "Hong Kong residents age 5+", 6_335_398, "2021",
        "Hong Kong Census and Statistics Department, 2021 Population Census",
        "https://www.censtatd.gov.hk/en/data/stat_report/product/B1120109/att/B11201092021XXXXB0100.pdf",
        "Table 3.12: 88.2%; Table 8.4: 7,182,991 residents age 5+",
        "derived_from_published_rounded_percentage", "YUE-HK-2021",
        "Bounds reflect only rounding of 88.2% to the nearest 0.1 percentage point; this is spoken use, not written vernacular Cantonese readership.",
        "Do not treat ability to read standard written Chinese as evidence of ability or demand for written vernacular Cantonese.",
        low=6_331_807, high=6_338_989,
        derivation="7,182,991 × 88.2%; bounds use 88.15%–88.25%",
        typed_view_eligibility="typed_home_language_view",
    ),
    row(
        "SUP-036", "GLB-005", "Cantonese spoken ability, Hong Kong", "yue-Hant-HK spoken profile",
        "functional_language_ability_or_estimate", "census_cantonese_usual_or_other_spoken_language_age5plus",
        "Hong Kong residents age 5+", 6_730_463, "2021",
        "Hong Kong Census and Statistics Department, 2021 Population Census",
        "https://www.censtatd.gov.hk/en/data/stat_report/product/B1120109/att/B11201092021XXXXB0100.pdf",
        "Table 3.12: 93.7%; Table 8.4: 7,182,991 residents age 5+",
        "derived_from_published_rounded_percentage", "YUE-HK-2021",
        "Bounds reflect percentage rounding only; spoken ability is not written vernacular Cantonese or academic-register comfort.",
        "Alternative to SUP-035; never add them. Guangdong/Hans and Hong Kong/Hant profiles remain separate.",
        low=6_726_872, high=6_734_054,
        derivation="7,182,991 × 93.7%; bounds use 93.65%–93.75%",
        typed_view_eligibility="typed_functional_use_view",
    ),
    row(
        "SUP-037", "GLB-032", "Egypt territory population", "arz-Arab-EG scaffold ceiling",
        "territory_all_residents_ceiling", "official_census_territory_population",
        "Egypt residents", 94_798_827, "2017",
        "Central Agency for Public Mobilization and Statistics, 2017 Census",
        "https://www.capmas.gov.eg/Admin/Pages%20Files/201710914947book.pdf",
        "Final census results, national total",
        "published_exact_census_total", "ARZ-EG-TERRITORY-2017",
        "Territory population is not an Egyptian Arabic oral-use, MSA literacy, or comfortable-reader count.",
        "A locale scaffold ceiling only; no direct reach is assigned to an Egyptian-Arabic written edition.",
    ),
    row(
        "SUP-038", "GLB-034", "Iran territory population", "fa-Arab-IR",
        "territory_all_residents_ceiling", "official_census_territory_population",
        "Iran residents", 79_926_270, "2016",
        "Statistical Centre of Iran, 2016 National Population and Housing Census",
        "https://irandataportal.syr.edu/wp-content/uploads/Iran_Census_2016_Selected_Results.pdf",
        "Selected results: total population 79,926,270; mirror identifies Statistical Centre of Iran",
        "mirrored_primary_source_document", "FA-IR-TERRITORY-2016",
        "Territory includes non-Persian language populations and does not measure Persian literacy or academic comfort; cited URL is a mirror of the official selected-results document.",
        "Country ceiling only while an exact Persian-use census measure remains unresolved.",
    ),
    row(
        "SUP-039", "GLB-010", "Bangla mother-tongue population, Bangladesh", "bn-Beng-BD; source variety not stated",
        "mother_tongue_or_first_language", "derived_official_survey_share_times_official_adjusted_population",
        "Bangladesh residents represented by the official 2023 SEDS mother-tongue estimate", 168_419_331, "2022 population / 2023 survey",
        "Bangladesh Bureau of Statistics, Population and Housing Census 2022 and SEDS 2023",
        "https://bbs.portal.gov.bd/pages/static-pages/6922e073933eb65569e27220",
        "SEDS 2023 Table 3.6, printed p. 66: Bangla mother tongue 99.17%; PHC 2022 National Report Volume I Table 3.1.3, printed p. 43: adjusted population 169,828,911",
        "derived_cross_source_from_official_percentage_and_population", "BD-BBS-PHC2022-SEDS2023",
        "Rounding interval reflects only the published 99.17% to two decimal places; the survey does not print a weighted-person denominator and names all non-Bangla mother tongues only as Other.",
        "Official replacement for the provisional CLDR functional-language estimate; it remains a gross L1 context, not written academic comfort or unique marginal access.",
        low=168_410_840, high=168_427_822,
        derivation="round(169,828,911 × 99.17%); bounds use 99.165%–99.175% with integer endpoints",
        typed_view_eligibility="typed_derived_l1_view",
    ),
    row(
        "SUP-040", "GLB-053", "Putonghua functional-communication sensitivity, Mainland China", "cmn-Hans-CN",
        "functional_language_ability_or_estimate", "derived_official_putonghua_prevalence_times_official_census_population",
        "Mainland residents under a cross-source communication-prevalence sensitivity", 1_139_587_786, "2020 census and 2020 survey",
        "National Bureau of Statistics of China; Ministry of Education and State Language Commission",
        "https://www.moe.gov.cn/fbh/live/2021/53486/twwd/202106/t20210602_535078.html",
        "MOE: Putonghua prevalence 80.72% from a national sample covering 31 provincial jurisdictions, XPCC and 245 counties; NBS census denominator 1,411,778,724",
        "derived_cross_source_from_official_rounded_percentage_and_census_population", "ZH-CN-PUTONGHUA-2020",
        "Bounds reflect only rounding of 80.72% to two decimal places. Survey and census universes differ; no sampling interval is supplied here.",
        "Spoken-standard modality sensitivity only; never add to written Chinese or Sinitic language profiles and never treat as a direct speaker or academic-comfort count.",
        low=1_139_517_198, high=1_139_658_374,
        derivation="round(1,411,778,724 × 80.72%); bounds use 80.715%–80.725%",
        typed_view_eligibility="typed_functional_use_view",
    ),
    row(
        "SUP-041", "GLB-054", "Malaysia territory ceiling for Malaysian Malay output", "ms-Latn-MY",
        "territory_all_residents_ceiling", "official_census_territory_population_rounded",
        "Malaysia residents", 32_400_000, "2020",
        "Department of Statistics Malaysia, Population and Housing Census 2020",
        "https://www.dosm.gov.my/portal-main/release-content/launching-of-report-on-the-key-findings-population-and-housing-census-of-malaysia-2020-",
        "Key findings release: total population 32.4 million; citizens 29.8 million; Bumiputera 20.6 million",
        "published_rounded_territory_total", "MS-MY-TERRITORY-2020",
        "Rounded territory total only. It is not a Malay-language, literacy, academic-comfort, ethnicity or newly served count.",
        "Context ceiling for a separately named ms-Latn-MY output; Indonesian receives zero direct Malaysian reach absent directed evidence.",
        low=32_350_000, high=32_449_999,
        derivation="32.4 million rounded to one decimal million; displayed-rounding sensitivity only",
        typed_view_eligibility="typed_territory_context_view",
    ),
]


# Explicit source-transcription decisions.  These are deliberately keyed by
# row identity rather than inferred from prose in ``source_value_status``.
SOURCE_TRANSCRIBED_EXACTLY = {
    "SUP-001": "true", "SUP-002": "false", "SUP-003": "false",
    "SUP-004": "true", "SUP-005": "false", "SUP-006": "false",
    "SUP-008": "true", "SUP-009": "true", "SUP-010": "true",
    "SUP-011": "true", "SUP-012": "true", "SUP-013": "true",
    "SUP-014": "true", "SUP-015": "true", "SUP-016": "true",
    "SUP-017": "false", "SUP-018": "true", "SUP-019": "true",
    "SUP-020": "true", "SUP-021": "true", "SUP-022": "true",
    "SUP-023": "true", "SUP-024": "true", "SUP-025": "true",
    "SUP-026": "true", "SUP-027": "true", "SUP-028": "true",
    "SUP-029": "true", "SUP-030": "true", "SUP-032": "true",
    "SUP-034": "true", "SUP-035": "false", "SUP-036": "false",
    "SUP-037": "true", "SUP-038": "true", "SUP-039": "false",
    "SUP-040": "false", "SUP-041": "false",
}


SOURCE_ID_BY_ROW = {
    "SUP-001": "SUPSRC-US-ACS-S1601-2024", "SUP-002": "SUPSRC-US-ACS-S1601-2024",
    "SUP-003": "SUPSRC-GB-ONS-TS029-2021",
    "SUP-004": "SUPSRC-TW-DGBAS-CENSUS-2020", "SUP-005": "SUPSRC-TW-DGBAS-CENSUS-2020", "SUP-006": "SUPSRC-TW-DGBAS-CENSUS-2020",
    "SUP-008": "SUPSRC-ES-CERVANTES-2025", "SUP-009": "SUPSRC-US-ACS-B16001-2024",
    "SUP-010": "SUPSRC-UN-PORTUGUESE-2026", "SUP-011": "SUPSRC-BR-IBGE-CENSUS-2022",
    "SUP-012": "SUPSRC-OIF-FRENCH-2025", "SUP-013": "SUPSRC-OIF-FRENCH-2025",
    "SUP-014": "SUPSRC-RU-ROSSTAT-CENSUS-2021", "SUP-015": "SUPSRC-RU-ROSSTAT-CENSUS-2021",
    "SUP-016": "SUPSRC-DE-DESTATIS-MICROCENSUS-2024", "SUP-017": "SUPSRC-DE-DESTATIS-MICROCENSUS-2024",
    "SUP-018": "SUPSRC-IT-ISTAT-LANGUAGE-2024", "SUP-019": "SUPSRC-PL-STAT-POPULATION-2024",
    "SUP-020": "SUPSRC-UNESCO-ARABIC", "SUP-021": "SUPSRC-TR-TUIK-ABPRS-2024",
    "SUP-022": "SUPSRC-TZ-CENSUS-2022", "SUP-023": "SUPSRC-KE-CENSUS-2019", "SUP-024": "SUPSRC-UG-CENSUS-2024",
    "SUP-025": "SUPSRC-UNESCO-SWAHILI-2025", "SUP-026": "SUPSRC-NEWMAN-HAUSA-2022",
    "SUP-027": "SUPSRC-WORLDBANK-HAUSA-2022", "SUP-028": "SUPSRC-YAKPO-PCM-2024",
    "SUP-029": "SUPSRC-KR-CENSUS-2020", "SUP-030": "SUPSRC-PH-CENSUS-2020",
    "SUP-032": "SUPSRC-UNICEF-AMHARIC-LOI", "SUP-034": "SUPSRC-ET-POPULATION-PROJECTION-2025",
    "SUP-035": "SUPSRC-HK-CENSUS-2021", "SUP-036": "SUPSRC-HK-CENSUS-2021",
    "SUP-037": "SUPSRC-EG-CENSUS-2017", "SUP-038": "SUPSRC-IR-CENSUS-2016",
    "SUP-039": "SUPSRC-BD-BBS-PHC2022-SEDS2023",
    "SUP-040": "SUPSRC-CN-MOE-PUTONGHUA-NBS-2020",
    "SUP-041": "SUPSRC-MY-DOSM-PHC-2020",
}


# Rows sharing one of these IDs are alternatives, subsets, or territorial
# decompositions and must never be summed.  Cross-file matches to master
# observations are applied in the join builder.
NONADDITIVITY_GROUP = {
    "SUP-001": "EN-US-ACS-2024-ALTERNATIVES",
    "SUP-002": "EN-US-ACS-2024-ALTERNATIVES",
    "SUP-004": "ZH-HANT-TW-2020-ALTERNATIVES",
    "SUP-005": "ZH-HANT-TW-2020-ALTERNATIVES",
    "SUP-006": "ZH-HANT-TW-2020-ALTERNATIVES",
    "SUP-008": "ES-GLOBAL-US-NONADDITIVE",
    "SUP-009": "ES-GLOBAL-US-NONADDITIVE",
    "SUP-010": "PT-GLOBAL-BR-NONADDITIVE",
    "SUP-011": "PT-GLOBAL-BR-NONADDITIVE",
    "SUP-012": "FR-OIF-2025-ALTERNATIVES",
    "SUP-013": "FR-OIF-2025-ALTERNATIVES",
    "SUP-014": "RU-ROSSTAT-2021-ALTERNATIVES",
    "SUP-015": "RU-ROSSTAT-2021-ALTERNATIVES",
    "SUP-016": "DE-MICROCENSUS-2024-ALTERNATIVES",
    "SUP-017": "DE-MICROCENSUS-2024-ALTERNATIVES",
    "SUP-022": "SWAHILI-GLOBAL-COUNTRY-NONADDITIVE",
    "SUP-023": "SWAHILI-GLOBAL-COUNTRY-NONADDITIVE",
    "SUP-024": "SWAHILI-GLOBAL-COUNTRY-NONADDITIVE",
    "SUP-025": "SWAHILI-GLOBAL-COUNTRY-NONADDITIVE",
    "SUP-026": "HAUSA-GLOBAL-ESTIMATES-ALTERNATIVES",
    "SUP-027": "HAUSA-GLOBAL-ESTIMATES-ALTERNATIVES",
    "SUP-032": "AMH-ET-L1-LOI-NONADDITIVE",
    "SUP-034": "OROMO-ET-L1-REGION-NONADDITIVE",
    "SUP-035": "YUE-HK-2021-ALTERNATIVES",
    "SUP-036": "YUE-HK-2021-ALTERNATIVES",
    "SUP-040": "ZH-CN-WRITTEN-SPOKEN-NONADDITIVE",
}


REMOVED_DUPLICATE_ALIASES = {
    "SUP-007": "POP-PK-002",
    "SUP-031": "POP-ET-002",
    "SUP-033": "POP-ET-001",
}


SUPERSEDES_OBSERVATION_IDS = {
    "SUP-039": "ASSEC-BD-BN-001",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def numeric(value: str) -> bool:
    if value == "":
        return True
    return value.isdigit() and int(value) >= 0


def rounded_percentage_interval(universe: int, displayed_percent: str) -> tuple[int, int]:
    proportion = Decimal(displayed_percent) / Decimal(100)
    decimal_places = len(displayed_percent.partition(".")[2])
    half_display_unit_percent = Decimal(5).scaleb(-(decimal_places + 1))
    half_unit = half_display_unit_percent / Decimal(100)
    low = (Decimal(universe) * (proportion - half_unit)).to_integral_value(rounding=ROUND_CEILING)
    high_exclusive = (Decimal(universe) * (proportion + half_unit)).to_integral_value(rounding=ROUND_CEILING)
    return int(low), int(high_exclusive - 1)


def main() -> None:
    universe_validation = json.loads(UNIVERSE_VALIDATION.read_text(encoding="utf-8"))
    with UNIVERSE.open("r", encoding="utf-8-sig", newline="") as handle:
        profiles = {r["universe_profile_id"]: r for r in csv.DictReader(handle)}
    with MASTER_OBSERVATIONS.open("r", encoding="utf-8-sig", newline="") as handle:
        master_observations = list(csv.DictReader(handle))

    ids = [r["supplement_id"] for r in ROWS]
    errors: list[str] = []
    expected_universe_identity = universe_validation.get("outputs", {}).get(UNIVERSE.name, {})
    if universe_validation.get("status") != "PASS":
        errors.append("upstream expected-universe validation is not PASS")
    if expected_universe_identity.get("sha256") != sha256(UNIVERSE):
        errors.append("upstream expected-universe CSV hash does not match its validation receipt")
    if set(ids) != set(SOURCE_TRANSCRIBED_EXACTLY):
        errors.append("source-transcription decisions do not exactly cover supplement rows")
    if set(ids) != set(SOURCE_ID_BY_ROW):
        errors.append("stable source IDs do not exactly cover supplement rows")
    for item in ROWS:
        sid = item["supplement_id"]
        item["source_transcribed_exactly"] = SOURCE_TRANSCRIBED_EXACTLY.get(sid, "")
        item["source_id"] = SOURCE_ID_BY_ROW.get(sid, "")
        item["supersedes_observation_ids"] = SUPERSEDES_OBSERVATION_IDS.get(sid, "")
        if sid in NONADDITIVITY_GROUP:
            item["overlap_group_id"] = NONADDITIVITY_GROUP[sid]
            item["nonadditivity_group_id"] = NONADDITIVITY_GROUP[sid]
            item["nonadditivity_rule"] = "never_sum_rows_sharing_overlap_group_id"
        else:
            item["nonadditivity_group_id"] = ""
            item["nonadditivity_rule"] = "no_internal_alternative_row_registered"
    if len(ids) != len(set(ids)):
        errors.append("duplicate supplement_id")
    for item in ROWS:
        if item["universe_profile_id"] not in profiles:
            errors.append(f"unknown profile {item['universe_profile_id']}")
        if not all(numeric(item[k]) for k in ("population_low", "population_base", "population_high")):
            errors.append(f"invalid numeric field in {item['supplement_id']}")
        if item["rank_ready_marginal_access"] != "false":
            errors.append(f"supplement row promoted to marginal rank: {item['supplement_id']}")
        if not item["source_url"].startswith("https://"):
            errors.append(f"non-HTTPS source URL: {item['supplement_id']}")
        if item["source_transcribed_exactly"] not in {"true", "false"}:
            errors.append(f"missing explicit transcription status: {item['supplement_id']}")
        if not item["source_id"]:
            errors.append(f"missing stable source ID: {item['supplement_id']}")
        if item["count_unit"] == "persons" and not any(
            item[field] for field in ("population_low", "population_base", "population_high")
        ):
            errors.append(f"person-count row has no numeric value: {item['supplement_id']}")
        low = int(item["population_low"]) if item["population_low"] else None
        base = int(item["population_base"]) if item["population_base"] else None
        high = int(item["population_high"]) if item["population_high"] else None
        if low is not None and high is not None and low > high:
            errors.append(f"reversed interval: {item['supplement_id']}")
        if base is not None and low is not None and base < low:
            errors.append(f"base below low: {item['supplement_id']}")
        if base is not None and high is not None and base > high:
            errors.append(f"base above high: {item['supplement_id']}")
        if item["source_value_status"] == "published_rounded_lower_bound":
            if item["population_base"] or item["population_high"] or not item["population_low"]:
                errors.append(f"lower bound encoded as point estimate: {item['supplement_id']}")

    percentage_interval_expectations = {
        "SUP-005": rounded_percentage_interval(21_786_490, "40.4"),
        "SUP-006": rounded_percentage_interval(21_786_490, "96.8"),
        "SUP-035": rounded_percentage_interval(7_182_991, "88.2"),
        "SUP-036": rounded_percentage_interval(7_182_991, "93.7"),
        "SUP-040": rounded_percentage_interval(1_411_778_724, "80.72"),
    }
    for sid, (expected_low, expected_high) in percentage_interval_expectations.items():
        item = next(row for row in ROWS if row["supplement_id"] == sid)
        if (int(item["population_low"]), int(item["population_high"])) != (expected_low, expected_high):
            errors.append(f"rounded-percentage interval mismatch: {sid}")

    master_signatures = {
        (item["measure_type"], item["population_base"], item["reference_date_or_year"])
        for item in master_observations if item["population_base"]
    }
    duplicate_signatures = [
        item["supplement_id"] for item in ROWS
        if item["population_base"] and (
            item["measure_type"], item["population_base"], item["reference_date_or_year"]
        ) in master_signatures
    ]
    if duplicate_signatures:
        errors.append(f"duplicate master observations: {','.join(duplicate_signatures)}")
    master_ids = {item["observation_id"] for item in master_observations}
    missing_canonical_alias_targets = sorted(set(REMOVED_DUPLICATE_ALIASES.values()) - master_ids)
    if missing_canonical_alias_targets:
        errors.append(f"missing canonical duplicate targets: {missing_canonical_alias_targets}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if errors:
        failure = {
            "schema": "interlanguage/supplemental-typed-population-estimates-validation/1.1.0",
            "status": "FAIL",
            "errors": errors,
        }
        OUT_JSON.write_text(json.dumps(failure, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        raise SystemExit("FAIL\n" + "\n".join(errors))

    ordered = sorted(ROWS, key=lambda r: (r["universe_profile_id"], r["supplement_id"]))
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(ordered)

    profile_counts = Counter(r["universe_profile_id"] for r in ordered)
    checks = {
        "unique_supplement_ids": len(ids) == len(set(ids)),
        "explicit_transcription_status_for_every_row": all(
            item["source_transcribed_exactly"] in {"true", "false"} for item in ordered
        ),
        "no_duplicate_master_observation_signature": not duplicate_signatures,
        "removed_duplicate_alias_targets_exist": not missing_canonical_alias_targets,
        "stable_source_id_for_every_row": all(item["source_id"] for item in ordered),
        "all_population_values_are_person_counts": all(item["count_unit"] == "persons" for item in ordered),
        "all_rows_context_or_typed_only": all(item["rank_ready_marginal_access"] == "false" for item in ordered),
        "lower_bounds_not_encoded_as_point_estimates": all(
            item["source_value_status"] != "published_rounded_lower_bound"
            or (
                item["population_low"] != ""
                and item["population_base"] == ""
                and item["population_high"] == ""
            )
            for item in ordered
        ),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    validation = {
        "schema": "interlanguage/supplemental-typed-population-estimates-validation/1.1.0",
        "status": status,
        "row_count": len(ordered),
        "profile_count": len(profile_counts),
        "profile_ids": sorted(profile_counts),
        "denominator_class_counts": dict(sorted(Counter(r["denominator_class"] for r in ordered).items())),
        "checks": checks,
        "removed_duplicate_aliases": REMOVED_DUPLICATE_ALIASES,
        "superseded_observation_ids": SUPERSEDES_OBSERVATION_IDS,
        "upstream_expected_universe": {
            "bytes": UNIVERSE.stat().st_size,
            "sha256": sha256(UNIVERSE),
            "validation_sha256": sha256(UNIVERSE_VALIDATION),
        },
        "territory_rows_not_promoted": all(
            r["population_use"] == "gross_or_context_typed_view_only_not_direct_residual_rank"
            for r in ordered if r["denominator_class"].startswith("territory")
        ),
        "output": {"bytes": OUT_CSV.stat().st_size, "sha256": sha256(OUT_CSV)},
        "limitations": (
            "The supplement closes source-profile recall gaps only. It does not estimate underserved readers, "
            "deduplicate cross-border users, or make heterogeneous denominator classes cardinally comparable."
        ),
    }
    OUT_JSON.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit("FAIL: post-build validation did not pass")
    print(json.dumps({
        "status": "PASS",
        "rows": len(ordered),
        "profiles": len(profile_counts),
        "csv_sha256": sha256(OUT_CSV),
        "validation_sha256": sha256(OUT_JSON),
    }, indent=2))


if __name__ == "__main__":
    main()
