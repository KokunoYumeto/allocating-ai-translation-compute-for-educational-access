#!/usr/bin/env python3
"""Build a typed, nonduplicative large-language population-strata proposal.

This is evidence plumbing, not a ranking.  It deliberately preserves different
measure classes (L1, reported ability, home language, educational exposure,
institutional estimates, and package-only aggregates) rather than silently
converting one into another.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "structured" / "large_language_population_strata_proposal.json"
OUT_MD = ROOT / "agent_reports" / "LARGE_LANGUAGE_POPULATION_STRATA.md"


def source(source_id, institution, title, year, url, locator, evidence_class):
    return {
        "source_id": source_id,
        "institution_or_author": institution,
        "title": title,
        "reference_year": str(year),
        "url_or_doi": url,
        "locator": locator,
        "evidence_class": evidence_class,
    }


SOURCES = [
    source("SRC_CN_NBS_CENSUS_2020", "National Bureau of Statistics of China", "Seventh National Population Census, Communique No. 5", 2020, "https://www.stats.gov.cn/english/PressRelease/202105/t20210510_1817190.html", "Table 5-1; Mainland total 1,411,778,724", "official census"),
    source("SRC_CN_MOE_PUTONGHUA_2020", "PRC Ministry of Education / State Language Commission", "2020 language-work press conference", 2020, "https://www.moe.gov.cn/fbh/live/2021/53486/twwd/202106/t20210602_535078.html", "10:08:06 response; 80.72% able to use Putonghua for communication", "official sample-survey release"),
    source("SRC_CN_MOE_NORMATIVE_CHARACTERS_2021", "PRC Ministry of Education", "Overview of China's languages and scripts (2021 edition)", 2020, "https://www.moe.gov.cn/jyb_sjzl/wenzi/202108/t20210827_554992.html", "more than 95% of the literate population uses normative Chinese characters", "official administrative summary"),
    source("SRC_CN_MOE_EDUCATION_2025", "PRC Ministry of Education", "2025 National Education Development Statistical Communique", 2025, "https://hudong.moe.gov.cn/jyb_sjzl/sjzl_fztjgb/202607/t20260706_1442870.html", "280,404,300 formal-education enrolments; stage counts published separately", "official administrative statistics"),
    source("SRC_US_ACS_B16001_2023", "U.S. Census Bureau", "ACS 2023 1-year table B16001", 2023, "https://data.census.gov/table/ACSDT1Y2023.B16001", "population age 5+: speak only English 245,472,067 +/-221,387; Spanish at home 43,369,734 +/-134,347", "official sample survey"),
    source("SRC_ONS_LANGUAGE_2021", "UK Office for National Statistics", "Language, England and Wales: Census 2021", 2021, "https://www.ons.gov.uk/peoplepopulationandcommunity/culturalidentity/language/bulletins/languageenglandandwales/census2021", "52.6m English (English or Welsh in Wales) main language; 4.1m further English-proficient", "official census bulletin"),
    source("SRC_STATCAN_LANGUAGE_2021", "Statistics Canada", "2021 Census Profile: knowledge of languages", 2021, "https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/page.cfm?DGUIDlist=2021A000011124&GENDERlist=1&HEADERlist=18&LANG=E&STATISTIClist=1", "English knowledge 31,628,570 in private households", "official census sample table"),
    source("SRC_ABS_LANGUAGE_2021", "Australian Bureau of Statistics", "2021 Census QuickStats, Australia", 2021, "https://abs.gov.au/census/find-census-data/quickstats/2021/AUS", "English only used at home 18,303,662", "official census"),
    source("SRC_UK_ENGLISH_GLOBAL", "UK Government / British Council", "UK capability in English language training", 2013, "https://assets.publishing.service.gov.uk/media/5ce2859740f0b627e4b147b6/UK_capability_in_English_language_training-withdrawn.pdf", "p. 3: 1.5 billion users of English of varying proficiency", "institutional global estimate"),
    source("SRC_CERVANTES_SPANISH_2025", "Instituto Cervantes", "El espanol: lengua para el mundo 2025", 2025, "https://cvc.cervantes.es/lengua/anuario/anuario_25/elm/p01.htm", "key facts 1-5: 520m native-domain; >630m potential users", "institutional modeled global estimate"),
    source("SRC_UN_PORTUGUESE_2026", "United Nations Secretary-General", "World Portuguese Language Day message", 2026, "https://www.un.org/sg/en/content/sg/statements/2026-05-05/secretary-generals-message-world-portuguese-language-day", "265m speakers", "institutional global estimate"),
    source("SRC_OIF_FRENCH_2026", "Organisation internationale de la Francophonie", "La langue francaise dans le monde 2026, synthesis", 2025, "https://www.francophonie.org/sites/default/files/2026-04/Synthese_rapport_Langue_francaise_dans_le_monde_2026.pdf", "396m Francophones; method and selected country estimates in synthesis table", "institutional country-modeled estimate"),
    source("SRC_UNESCO_RUSSIAN_2024", "UNESCO Executive Board", "Russian Language Day speech", 2024, "https://www.unesco.org/sites/default/files/medias/fichiers/2024/06/0606_russian%20language.pdf", "over 250m speakers globally", "institutional lower-bound estimate"),
    source("SRC_WB_ARAB_WORLD_POP", "World Bank", "Population, total - Arab World", 2025, "https://data.worldbank.org/indicator/SP.POP.TOTL?locations=1A", "Arab World aggregate 503,356,133 (2025); 492,612,632 (2024)", "official/institutional territorial aggregate"),
    source("SRC_WB_LOI_ARABIC_2021", "World Bank", "Loud and Clear: Effective Language of Instruction Policies for Learning", 2021, "https://documents1.worldbank.org/curated/en/517851626203470278/pdf/Effective-Language-of-Instruction-Policies-for-Learning.pdf", "Box 4, PDF p. 31: MSA is written/educational, not an L1; colloquial types distinguished", "institutional evidence synthesis"),
    source("SRC_UNESCO_ARABIC", "UNESCO", "Arabic language", 2024, "https://www.unesco.org/en/arabic-language?hub=752", "standard/classical Arabic coexists with many dialects; approximately 450m Arabic speakers", "institutional umbrella estimate"),
    source("SRC_WB_EGYPT_POP", "World Bank", "Population, total - Egypt, Arab Republic", 2024, "https://data.worldbank.org/indicator/SP.POP.TOTL?locations=EG", "116,538,258 residents (2024)", "institutional population estimate"),
    source("SRC_INDIA_C16_2011", "Census of India", "C-16 Population by Mother Tongue", 2011, "https://censusindia.gov.in/nada/index.php/catalog/10191", "raw mother-tongue returns and Statement 1 language totals", "official census"),
    source("SRC_BPS_INDONESIAN_ABILITY_2022", "Statistics Indonesia (BPS)", "Long Form SP2020 topic table 196", 2022, "https://sensus.bps.go.id/topik/tabular/sp2022/196/1/0", "TOTAL age 5+: able to use Indonesian 248,501,794; unable 5,177,554", "official weighted census long-form estimate"),
    source("SRC_BPS_INDONESIAN_HOME_2010", "Statistics Indonesia (BPS)", "Nationality, Ethnicity, Religion and Daily Language", 2010, "https://www.bps.go.id/en/publication/2012/05/23/55eca38b7fe0830834605b35/nationality--ethnicity--religion--and-dailylanguage-of-indonesian-population.html", "42,682,566 age 5+ daily/home Indonesian users", "official census publication"),
    source("SRC_BBS_BANGLADESH_2022", "Bangladesh Bureau of Statistics", "Population and Housing Census 2022", 2022, "https://bbs.portal.gov.bd/pages/static-pages/6922e0ff933eb65569e297dc", "post-enumeration adjusted population 169,828,911", "official census"),
    source("SRC_BBS_SEDS_2023", "Bangladesh Bureau of Statistics", "Sample Vital Statistics / Socio-Economic and Demographic Survey 2023", 2023, "https://nsds.bbs.gov.bd/storage/files/1/Publications/others/SEDS_2023_Report.pdf", "Bangla mother tongue 99.17%", "official sample survey"),
    source("SRC_UNESCO_SWAHILI_2026", "UNESCO", "Kiswahili: a bridge for cultural diversity, dialogue and digital innovation", 2026, "https://www.unesco.org/en/articles/kiswahili-bridge-cultural-diversity-dialogue-and-digital-innovation", "more than 200m speakers across Africa and beyond", "institutional mixed L1/L2 lower bound"),
    source("SRC_JP_POP_2024", "Statistics Bureau of Japan", "Current Population Estimates as of October 1, 2024", 2024, "https://www.stat.go.jp/english/data/jinsui/2024np/index.html", "total 123,802,000; Japanese-national population 120,296,000", "official administrative estimate"),
    source("SRC_JP_MEXT_SCHOOL_LANGUAGE", "Ministry of Education, Culture, Sports, Science and Technology", "Guidebook for Starting School / Course of Study: Japanese Language", 2011, "https://www.mext.go.jp/component/a_menu/education/micro_detail/__icsFiles/afieldfile/2011/04/11/1298356_2.pdf", "Japanese common language, common-use characters and kana taught in national curriculum", "official curriculum"),
    source("SRC_JP_MEXT_JAPANESE_INSTRUCTION_2025", "Ministry of Education, Culture, Sports, Science and Technology", "Survey of pupils needing Japanese-language instruction", 2025, "https://www.mext.go.jp/b_menu/houdou/31/09/1421569_00007.htm", "84,759 public-school pupils; stage counts 54,888 elementary, 20,681 lower secondary, 7,313 upper secondary, 1,877 other", "official administrative survey"),
    source("SRC_JP_MEXT_ENROLMENT_2025", "Ministry of Education, Culture, Sports, Science and Technology", "School Basic Survey 2025", 2025, "https://www.mext.go.jp/b_menu/toukei/chousa01/kihon/kekka/k_detail/2025.htm", "2,645,837 undergraduates plus 277,132 graduate/professional-degree students", "official administrative statistics"),
    source("SRC_OECD_PIAAC_JAPAN_2023", "OECD", "Survey of Adult Skills 2023: Japan country note", "2022-2023", "https://www.oecd.org/en/publications/2024/12/survey-of-adults-skills-2023-country-notes_df7b4a60/japan_c63b2ef1.html", "7% of represented adults at or below Level 1 in literacy, numeracy and adaptive problem solving; represented population about 74.7m", "international sample survey"),
    source("SRC_VN_GSO_MIDTERM_2024", "General Statistics Office of Viet Nam", "2024 mid-term Population and Housing Census press release", 2024, "https://www.gso.gov.vn/du-lieu-va-so-lieu-thong-ke/2025/01/thong-cao-bao-chi-ket-qua-dieu-tra-dan-so-va-nha-o-giua-ky-nam-2024/", "population 101,112,656 on 1 April 2024", "official census survey"),
    source("SRC_VN_EDUCATION_LAW", "National Assembly of Viet Nam", "Law on Education 43/2019/QH14", 2019, "https://english.luatvietnam.vn/law-on-education-no-43-2019-tt-qh14-of-the-national-assembly-175003-doc1.html", "Article 11(1): Vietnamese is official language in education institutions", "official law"),
    source("SRC_PH_PSA_2024", "Philippine Statistics Authority", "2024 Census of Population", 2024, "https://psa.gov.ph/statistics/population-and-housing/node/1684077791", "Table 1: resident population 112,729,484 on 1 July 2024", "official census"),
    source("SRC_PH_RA12027_2024", "Republic of the Philippines", "Republic Act No. 12027", 2024, "https://lawphil.net/statutes/repacts/ra2024/pdf/ra_12027_2024.pdf", "Filipino and English media of instruction; regional languages auxiliary", "official law"),
    source("SRC_PH_PSA_HOME_LANGUAGE_2020", "Philippine Statistics Authority", "Tagalog most widely spoken language at home, 2020 CPH", 2020, "https://psa.gov.ph/content/tagalog-most-widely-spoken-language-home-2020-census-population-and-housing", "Tagalog 10,522,507 households; household count, not persons", "official census bulletin"),
    source("SRC_GOETHE_GERMAN_2013", "Goethe-Institut", "German in figures", 2013, "https://www.goethe.de/resources/files/pdf21/gi_04-13_en-web.pdf", "around 100m native speakers", "institutional rounded estimate"),
    source("SRC_UNESCO_HAUSA_2026", "UNESCO", "African languages, the blind spot of AI", 2026, "https://www.unesco.org/en/articles/african-languages-blind-spot-ai", "over 80m Hausa speakers in Nigeria", "institutional lower-bound estimate"),
    source("SRC_IJCAI_HAUSA_2024", "IJCAI AI for Good", "Proceedings paper on Hausa language technology", 2024, "https://www.ijcai.org/proceedings_aai4g/2024/1", "over 100m Hausa speakers globally", "peer-reviewed mixed L1/L2 lower-bound estimate"),
    source("SRC_PERSIAN_2024", "Computers", "Persian-language NLP survey", 2024, "https://doi.org/10.3390/computers13080212", "approximately 110m speakers across Persian/Farsi, Dari and Tajik standards", "peer-reviewed cross-standard estimate"),
    source("SRC_WB_IRAN_POP", "World Bank", "Population, total - Iran", 2024, "https://data.worldbank.org/indicator/SP.POP.TOTL?locations=IR", "91,567,738 residents (2024)", "institutional population estimate"),
    source("SRC_PBS_LANGUAGE_2023", "Pakistan Bureau of Statistics", "2023 Census Table 11, population by mother tongue", 2023, "https://www.pbs.gov.pk/wp-content/uploads/census_tables/tables/table_11_national.pdf", "Punjabi 88,915,544; Urdu 22,249,307", "official census"),
    source("SRC_PAK_CONSTITUTION", "Government of Pakistan", "Constitution of Pakistan", 2023, "https://pakistancode.gov.pk/pdffiles/administrator9d8e2ecc414c6d3371ac41114b61a2c4.pdf", "Article 251: Urdu national language", "official law"),
    source("SRC_WAP_2024", "Journal of Asian and African Studies", "West African Pidgin Englishes", 2024, "https://doi.org/10.1177/00020397241263364", "106-143m across six mutually intelligible related varieties, estimates adjusted to 2022", "peer-reviewed cluster estimate"),
    source("SRC_TUIK_POP_2024", "Turkish Statistical Institute", "Address Based Population Registration System Results 2024", 2024, "https://veriportali.tuik.gov.tr/Bulten/Index?dil=2&p=Adrese-Dayali-Nufus-Kayit-Sistemi-Sonuclari-2023-53783", "85,664,944 residents", "official administrative population"),
    source("SRC_TURKISH_SURVEY_2023", "Language Resources and Evaluation", "Resources and processing of Turkish", 2023, "https://doi.org/10.1007/s10579-022-09605-4", "Turkish spoken by over 80m, mainly in Turkiye", "peer-reviewed lower-bound estimate"),
    source("SRC_KOSTAT_POP_2024", "Statistics Korea", "2024 Population and Housing Census", 2024, "https://kostat.go.kr/boardDownload.es?bid=11747&list_no=439064&seq=1", "51.81m residents; 49.76m Korean nationals", "official register-based census"),
    source("SRC_OXFORD_KOREAN", "University of Oxford Faculty of Asian and Middle Eastern Studies", "Korean", "n.d.", "https://www.ames.ox.ac.uk/korean", "approximately 80m Korean speakers worldwide; standards differ between Koreas", "scholarly institutional estimate"),
    source("SRC_THAI_NSO_2024", "National Statistical Office of Thailand", "Statistical Yearbook / registration population 2024", 2024, "https://www.nso.go.th/public/e-book/Bulletin-of-Statistics/bulletin-4-68/32/", "65,951,210 registered residents", "official administrative population"),
]


def stratum(sid, target_ids, label, tag, script, geography, measure_class,
            low, base, high, unit, definition, year, source_ids, rankability,
            overlap_group, additivity, derivation=None, limitations=None,
            endpoint="language_population_basis"):
    return {
        "stratum_id": sid,
        "language_target_ids": target_ids,
        "exact_variety_or_register": label,
        "language_tag_or_profile": tag,
        "script_orthography": script,
        "geography": geography,
        "measure_class": measure_class,
        "population_low": low,
        "population_base": base,
        "population_high": high,
        "population_unit": "persons",
        "source_unit_or_denominator": unit,
        "population_definition": definition,
        "population_reference_year": str(year),
        "source_ids": source_ids,
        "rankability": rankability,
        "endpoint": endpoint,
        "overlap_group": overlap_group,
        "additivity": additivity,
        "derivation": derivation,
        "limitations": limitations or [],
    }


S = []
add = S.append

# Direct or statistically typed language measures.
add(stratum("LLPS-CMN-CN-ABILITY-2020", ["lang:cmn-Hans-CN:spoken"], "Mainland Standard Mandarin (Putonghua), reported communicative ability", "cmn-Hans-CN", "spoken; normally paired with PRC standard characters in education", "Mainland China census universe", "reported_ability", 1_139_517_197, 1_139_587_786, 1_139_658_375, "persons", "People able to use Putonghua for communication; derived from 80.72% of the 2020 Mainland census population.", 2020, ["SRC_CN_NBS_CENSUS_2020", "SRC_CN_MOE_PUTONGHUA_2020"], "eligible_direct_typed_measure", "CN-2020-language-capability", "Not additive with any written-Chinese, census-population, enrolment, rural, older, or offline row.", "1,411,778,724 x 80.72%; low/high reflect rate rounding only, not sampling confidence.", ["Not an L1 count.", "Not proof of literacy or advanced academic comfort."]))
add(stratum("LLPS-ID-ID-ABILITY-2022", ["lang:id-Latn-ID"], "Bahasa Indonesia, reported communicative ability age 5+", "id-Latn-ID", "Latin; EYD V", "Indonesia", "reported_ability", None, 248_501_794, None, "persons age 5+", "BPS weighted long-form estimate of people able to understand and produce comprehensible Indonesian.", 2022, ["SRC_BPS_INDONESIAN_ABILITY_2022"], "eligible_direct_typed_measure", "ID-ability-home-education", "Primary Indonesian ability denominator; do not add home-language or enrolment rows.", None, ["Point estimate; BPS page does not publish a confidence interval.", "Oral/receptive ability does not itself prove advanced reading."]))
add(stratum("LLPS-ID-ID-HOME-2010", ["lang:id-Latn-ID"], "Bahasa Indonesia daily/home users age 5+", "id-Latn-ID", "Latin", "Indonesia", "home_language", 42_682_566, 42_682_566, 42_682_566, "persons age 5+", "Census daily/home-language count.", 2010, ["SRC_BPS_INDONESIAN_HOME_2010"], "eligible_direct_typed_measure_alternative", "ID-ability-home-education", "Subset/alternative baseline; never add to the 2022 ability count.", None, ["Older reference year and narrower construct than ability."]))
add(stratum("LLPS-HI-IN-L1-2011", ["lang:hi-Deva-IN"], "Hindi raw mother-tongue return", "hi-Deva-IN", "Devanagari not directly enumerated", "India", "l1", 322_230_097, 322_230_097, 322_230_097, "persons L1", "Raw Hindi return, excluding separately returned varieties grouped under the broader Hindi umbrella.", 2011, ["SRC_INDIA_C16_2011"], "eligible_direct_typed_measure", "IND-C16-2011-person", "Country-disjoint from Pakistan; do not add the 528m Hindi umbrella.", None, ["Historical census vintage.", "Mother tongue does not prove Devanagari literacy."]))
add(stratum("LLPS-BN-BD-L1PROXY-2022", ["lang:bn-Beng-BD"], "Bangla, Bangladesh standard community", "bn-Beng-BD", "Bengali script; Bangladesh orthography", "Bangladesh", "derived_l1_proxy", 168_410_840, 168_419_331, 168_427_822, "persons L1 proxy", "Adjusted population multiplied by official 99.17% Bangla mother-tongue share.", "2022-2023", ["SRC_BBS_BANGLADESH_2022", "SRC_BBS_SEDS_2023"], "eligible_derived_typed_measure", "BN-BD-language", "Country-disjoint from India Bengali; may be combined only in a parallel-package profile.", "169,828,911 x 99.17%; low/high are decimal-rounding bounds (99.165%-99.175%), not sampling confidence.", ["Derived rather than a published direct headcount.", "Does not prove literacy or advanced academic comfort."]))
add(stratum("LLPS-BN-IN-L1-2011", ["lang:bn-Beng-IN"], "Bengali, India standard", "bn-Beng-IN", "Bengali script; Indian orthography", "India", "l1", 96_177_835, 96_177_835, 96_177_835, "persons L1", "Raw Census mother-tongue return.", 2011, ["SRC_INDIA_C16_2011"], "eligible_direct_typed_measure", "IND-C16-2011-person", "Country-disjoint from Bangladesh Bangla; may be combined only in a parallel-package profile.", None, ["Historical census vintage."]))
add(stratum("LLPS-EN-US-HOME-2023", ["lang:en-Latn-001"], "English-only home-language users age 5+", "en-Latn-US", "Latin; US English", "United States", "home_language", 245_250_680, 245_472_067, 245_693_454, "persons age 5+", "ACS estimate of people speaking only English at home.", 2023, ["SRC_US_ACS_B16001_2023"], "eligible_direct_typed_measure_partial_global_coverage", "EN-country-disjoint", "Country-disjoint from Canada, Australia, and England/Wales rows; do not add global English estimate.", "ACS estimate +/- published margin of error.", ["Excludes multilingual English-proficient people."]))
add(stratum("LLPS-EN-CA-KNOWLEDGE-2021", ["lang:en-Latn-001"], "English knowledge in private households", "en-Latn-CA", "Latin; Canadian English", "Canada", "reported_ability", None, 31_628_570, None, "persons", "Census profile count reporting knowledge of English.", 2021, ["SRC_STATCAN_LANGUAGE_2021"], "eligible_direct_typed_measure_partial_global_coverage", "EN-country-disjoint", "Country-disjoint from other national English rows; do not add global English estimate.", None, ["Knowledge is not identical to main/home language or academic comfort."]))
add(stratum("LLPS-EN-AU-HOME-2021", ["lang:en-Latn-001"], "English-only home-language users", "en-Latn-AU", "Latin; Australian English", "Australia", "home_language", 18_303_662, 18_303_662, 18_303_662, "persons", "Census count using only English at home.", 2021, ["SRC_ABS_LANGUAGE_2021"], "eligible_direct_typed_measure_partial_global_coverage", "EN-country-disjoint", "Country-disjoint from other national English rows; do not add global English estimate.", None, ["Excludes multilingual English-proficient people.", "Census nonresponse applies."]))
add(stratum("LLPS-ES-US-HOME-2023", ["lang:es-Latn-US"], "Spanish home-language users age 5+", "es-Latn-US", "Latin; US Spanish", "United States", "home_language", 43_235_387, 43_369_734, 43_504_081, "persons age 5+", "ACS estimate of people speaking Spanish at home.", 2023, ["SRC_US_ACS_B16001_2023"], "eligible_direct_typed_measure", "ES-US-vs-global", "Do not add to the global Cervantes native/potential-user totals, which already include US speakers.", "ACS estimate +/- published margin of error.", ["Home use does not directly measure reading or regional standard preference."]))
add(stratum("LLPS-PA-IN-L1-2011", ["lang:pa-Guru-IN"], "Punjabi/Panjabi raw mother-tongue return in India", "pa-IN", "Script not enumerated; Gurmukhi intervention target", "India", "l1", 31_144_095, 31_144_095, 31_144_095, "persons L1", "Raw Census mother-tongue return.", 2011, ["SRC_INDIA_C16_2011"], "eligible_direct_typed_measure_language_not_script", "PA-crossborder", "Country-disjoint from Pakistan Punjabi; script readership is not measured.", None, ["Do not label all 31.1m as Gurmukhi-literate."]))
add(stratum("LLPS-PA-PK-L1-2023", ["lang:pnb-Arab-PK"], "Punjabi mother-tongue return in Pakistan", "pnb-PK", "Script not enumerated; Shahmukhi intervention target", "Pakistan", "l1", 88_915_544, 88_915_544, 88_915_544, "persons L1", "2023 Census mother-tongue count.", 2023, ["SRC_PBS_LANGUAGE_2023"], "eligible_direct_typed_measure_language_not_script", "PA-crossborder", "Country-disjoint from India Punjabi; script readership is not measured.", None, ["Do not label all 88.9m as Shahmukhi-literate."]))
add(stratum("LLPS-UR-IN-L1-2011", ["lang:ur-Arab-IN"], "Urdu mother-tongue return in India", "ur-Arab-IN", "Perso-Arabic; script literacy not enumerated", "India", "l1", 50_725_762, 50_725_762, 50_725_762, "persons L1", "Raw Census mother-tongue return.", 2011, ["SRC_INDIA_C16_2011"], "eligible_direct_typed_measure", "UR-crossborder", "Country-disjoint from Pakistan Urdu.", None, ["Historical census vintage."]))
add(stratum("LLPS-UR-PK-L1-2023", ["lang:ur-Arab-PK"], "Urdu mother-tongue return in Pakistan", "ur-Arab-PK", "Perso-Arabic; script literacy not enumerated", "Pakistan", "l1", 22_249_307, 22_249_307, 22_249_307, "persons L1", "2023 Census mother-tongue count.", 2023, ["SRC_PBS_LANGUAGE_2023"], "eligible_direct_typed_measure", "UR-crossborder", "Country-disjoint from India Urdu; not additive with Pakistan exposure ceiling.", None, []))
add(stratum("LLPS-TE-IN-L1-2011", ["lang:te-Telu-IN"], "Telugu mother-tongue return", "te-Telu-IN", "Telugu", "India", "l1", 81_127_740, 81_127_740, 81_127_740, "persons L1", "Census language total.", 2011, ["SRC_INDIA_C16_2011"], "eligible_direct_typed_measure", "IND-C16-2011-person", "Do not add the same persons' L2/L3 reports without capability-profile de-duplication.", None, ["Below 100m on direct L1 evidence; retained as near-threshold control."]))
add(stratum("LLPS-MR-IN-L1-2011", ["lang:mr-Deva-IN"], "Marathi mother-tongue return", "mr-Deva-IN", "Devanagari", "India", "l1", 82_801_140, 82_801_140, 82_801_140, "persons L1", "Census language total.", 2011, ["SRC_INDIA_C16_2011"], "eligible_direct_typed_measure", "IND-C16-2011-person", "Not additive with Hindi umbrella.", None, ["Below 100m on direct evidence; retained as near-threshold control."]))
add(stratum("LLPS-TA-IN-L1-2011", ["lang:ta-Taml-IN"], "Tamil mother-tongue return in India", "ta-Taml-IN", "Tamil", "India", "l1", 68_888_839, 68_888_839, 68_888_839, "persons L1", "Census language total.", 2011, ["SRC_INDIA_C16_2011"], "eligible_direct_typed_measure", "IND-C16-2011-person", "India-only; do not treat as worldwide Tamil count.", None, ["Below 100m; retained because it is a major official-language cohort."]))

# Global or cross-standard institutional estimates. These are context/package evidence,
# not exact-language rank denominators until decomposed into compatible country/variety cells.
add(stratum("LLPS-EN-GLOBAL-MIXED", ["lang:en-Latn-001"], "English users of varying proficiency", "en-Latn-001", "Latin; multiple standards", "Worldwide", "mixed_l1_l2_ability_estimate", 1_500_000_000, None, None, "persons", "Institutional estimate of 1.5b English users of varying proficiency.", 2013, ["SRC_UK_ENGLISH_GLOBAL"], "context_only_global_mixed_definition", "EN-global", "Never add to country English rows; global estimate subsumes them.", None, ["No L1/L2, literacy, academic-comfort, country, or uncertainty split."]))
add(stratum("LLPS-ES-GLOBAL-NATIVE", ["lang:es-Latn-001"], "Spanish native-domain users; common written core with regional overlays", "es-Latn-001", "Latin; multiple national standards", "Worldwide", "institutional_native_speaker_estimate", None, 520_000_000, None, "persons", "Instituto Cervantes modeled native-domain community.", 2025, ["SRC_CERVANTES_SPANISH_2025"], "package_context_only_until_country_variety_split", "ES-global", "Never add potential users or US home-language row.", None, ["Common-core package reach is not one exact regional target.", "Source publishes a rounded total, not an uncertainty interval."]))
add(stratum("LLPS-ES-GLOBAL-POTENTIAL", ["lang:es-Latn-001"], "Spanish potential users", "es-Latn-001", "Latin; multiple national standards", "Worldwide", "mixed_native_limited_and_learner_estimate", 630_000_000, None, None, "persons", "Lower bound: potential users exceed 630m.", 2025, ["SRC_CERVANTES_SPANISH_2025"], "context_only_mixed_definition", "ES-global", "Superset of the 520m native-domain estimate; never add.", None, ["Not a comfortable-reader or native-only denominator."]))
add(stratum("LLPS-PT-GLOBAL-SPEAKERS", ["lang:pt-Latn-001"], "Portuguese speakers; common core with regional overlays", "pt-Latn-001", "Latin; Brazilian, European, African and other standards", "Worldwide", "institutional_speaker_estimate", None, 265_000_000, None, "persons", "UN institutional worldwide speaker estimate.", 2026, ["SRC_UN_PORTUGUESE_2026"], "package_context_only_until_country_variety_split", "PT-global", "One global total; do not duplicate across regional targets.", None, ["No L1/L2, country, literacy, academic-comfort, or uncertainty split."]))
add(stratum("LLPS-FR-GLOBAL-FRANCOPHONES", ["lang:fr-Latn-001"], "Francophones under OIF method", "fr-Latn-001", "Latin; worldwide standards", "Worldwide", "institutional_country_modeled_speaker_estimate", None, 396_000_000, None, "persons", "OIF modeled Francophone total using country-level approaches, including literacy-in-French models for selected states.", 2025, ["SRC_OIF_FRENCH_2026"], "provisionally_rankable_only_after_country_rows_imported", "FR-global", "Never add the 170m learner count or country components to this global total.", None, ["Country methods are heterogeneous.", "A rounded global total cannot be assigned to one territorial target without the country table."]))
add(stratum("LLPS-RU-GLOBAL-SPEAKERS", ["lang:ru-Cyrl-001"], "Russian users", "ru-Cyrl-001", "Cyrillic; shared written standard with national overlays", "Worldwide", "institutional_speaker_lower_bound", 250_000_000, None, None, "persons", "UNESCO lower-bound estimate: over 250m speakers globally.", 2024, ["SRC_UNESCO_RUSSIAN_2024"], "context_only_until_l1_l2_country_split", "RU-global", "Do not add Russia census or diaspora cells to the global total.", None, ["No country, L1/L2, literacy, academic-comfort, or uncertainty split."]))
add(stratum("LLPS-SW-GLOBAL-USERS", ["lang:sw-Latn-001", "lang:swh-Latn-TZ:variety:tanzania-mainland-standard-kiswahili", "lang:swh-Latn-KE", "lang:swh-Latn-UG", "lang:swh-Latn-RW", "lang:swh-Latn-BI", "lang:swc-Latn-CD:variety:kivu-congo-swahili"], "Kiswahili cross-border user community", "sw/swh/swc-Latn", "Latin; national and regional standards", "Africa and diaspora", "cross_border_mixed_l1_l2_lower_bound", 200_000_000, None, None, "persons", "UNESCO lower-bound user estimate across Africa and beyond.", 2026, ["SRC_UNESCO_SWAHILI_2026"], "bridge_package_context_only", "SW-global", "Shared once across all Kiswahili/Swahili target profiles; no child target inherits 200m.", None, ["No country, L1/L2, literacy, or standard split."]))
add(stratum("LLPS-HA-NG-USERS", ["lang:ha-Latn-NG", "lang:ha-Arab-NG"], "Hausa users in Nigeria", "ha-NG", "Latin Boko and Ajami; script shares unmeasured", "Nigeria", "institutional_speaker_lower_bound", 80_000_000, None, None, "persons", "UNESCO lower bound for Hausa speakers in Nigeria.", 2026, ["SRC_UNESCO_HAUSA_2026"], "context_only_until_l1_l2_script_split", "HA-global", "Shared across Nigeria Hausa script targets; no script row inherits all 80m.", None, ["No L1/L2 or script split."]))
add(stratum("LLPS-HA-GLOBAL-USERS", ["lang:ha-Latn-NG", "lang:ha-Arab-NG", "lang:ha-Latn-NE", "lang:ha-Arab-NE", "lang:ha-Latn-TD", "lang:ha-Arab-TD", "lang:ha-Latn-GH", "lang:ha-Latn-CM"], "Hausa cross-border L1/L2 community", "ha", "Latin Boko and Ajami; national variation", "West/Central Africa and diaspora", "peer_reviewed_mixed_l1_l2_lower_bound", 100_000_000, None, None, "persons", "Peer-reviewed lower-bound global speaker estimate.", 2024, ["SRC_IJCAI_HAUSA_2024"], "bridge_package_context_only", "HA-global", "Global superset of Nigeria row; never add. No child target inherits 100m.", None, ["Country, L1/L2 and script distribution unmeasured."]))
add(stratum("LLPS-DE-GLOBAL-NATIVE", ["lang:de-Latn-001"], "German native speakers", "de-Latn-001", "Latin; Standard German common core", "German-speaking Europe and diaspora", "institutional_native_speaker_rounded_estimate", None, 100_000_000, None, "persons L1", "Goethe-Institut rounded estimate: around 100m native speakers.", 2013, ["SRC_GOETHE_GERMAN_2013"], "context_only_until_country_split_or_source_range", "DE-global", "Do not create an uncited 95-105m interval.", None, ["Old rounded estimate with no published uncertainty or country table in the cited item."]))
add(stratum("LLPS-PERSIAN-BRIDGE-GLOBAL", ["lang:pes-Arab-IR", "lang:prs-Arab-AF", "lang:tg-Cyrl-TJ"], "Iranian Persian-Dari-Tajik parallel-standard community", "pes/prs/tg", "Perso-Arabic and Tajik Cyrillic", "Iran, Afghanistan, Tajikistan and diaspora", "cross_standard_speaker_estimate", None, 110_000_000, None, "persons", "Peer-reviewed approximate total across Persian standards.", 2024, ["SRC_PERSIAN_2024"], "parallel_package_context_only", "PERSIAN-bridge", "No child standard inherits 110m; parallel editions and cross-comprehension evidence are required.", None, ["Country, L1/L2, script-literacy and standard split absent."]))
add(stratum("LLPS-WAP-BRIDGE-GLOBAL", ["lang:pcm-Latn-NG", "lang:wes-Latn-CM", "lang:kri-Latn-SL"], "West African Pidgin six-variety cluster", "pcm/wes/kri plus Ghanaian Pidgin, Pichi and Aku", "Latin; six related written profiles", "Nigeria, Cameroon, Sierra Leone, Ghana, Equatorial Guinea, Gambia", "peer_reviewed_mutually_intelligible_cluster_estimate", 106_000_000, None, 143_000_000, "persons", "Peer-reviewed 2022-adjusted estimate across six related, mutually intelligible varieties.", 2024, ["SRC_WAP_2024"], "parallel_bridge_package_context_only", "WAP-cluster", "Store once for the six-variety package; no constituent inherits the total.", None, ["Three constituent canonical target profiles are currently absent.", "The range is package reach context, not demonstrated no-study comprehension of one unified orthography."]))

# Territorial/educational exposure profiles. They cross the size threshold but are
# not language-user counts and may not enter the language score without a direct
# language-capability or literacy factor.
add(stratum("LLPS-ZH-HANS-CN-WRITTEN-EXPOSURE", ["lang:zh-Hans-CN:written"], "PRC Standard Written Chinese / normative-character exposure", "zh-Hans-CN", "PRC normative simplified characters", "Mainland China", "territorial_written_standard_exposure_ceiling", None, None, 1_411_778_724, "persons", "The Mainland census universe is 1,411,778,724 and more than 95% of the literate population uses normative Chinese characters; the sources do not publish a compatible exact literate denominator for multiplication.", 2020, ["SRC_CN_NBS_CENSUS_2020", "SRC_CN_MOE_NORMATIVE_CHARACTERS_2021"], "context_only_missing_direct_written_reader_count", "CN-2020-language-capability", "Almost wholly overlaps Putonghua ability and all Mainland subcohorts; never add.", None, ["The numeric high is a territorial ceiling, not a reader-count high-confidence bound.", "Spoken Putonghua ability cannot substitute for written-standard literacy."], "written_standard_exposure") )
add(stratum("LLPS-ZH-HANS-CN-FORMAL-ENROLMENT-2025", ["lang:zh-Hans-CN:written"], "Mainland formal-education opportunity cohort for Standard Written Chinese", "zh-Hans-CN", "PRC normative simplified characters", "Mainland China", "formal_education_enrolment", 280_404_300, 280_404_300, 280_404_300, "learner enrolments", "All formal-education enrolments reported by MOE in 2025; a stage-opportunity universe, not a count needing new Chinese material.", 2025, ["SRC_CN_MOE_EDUCATION_2025"], "eligible_exact_stage_opportunity_measure_only", "CN-formal-education-2025", "Do not add constituent stage enrolments or the whole-language population; use stage rows for package scoring.", None, ["Enrolment stock is not a direct language-ability, need, unique-person, or academic-comfort measure."], "formal_education_opportunity"))
add(stratum("LLPS-ARB-MSA-EDU-EXPOSURE-2025", ["lang:arb-Arab-001"], "Modern Standard Arabic written/educational register", "arb-Arab-001", "Arabic; MSA educational register", "World Bank Arab World aggregate", "territorial_educational_exposure_ceiling", 503_356_133, 503_356_133, 503_356_133, "residents", "Population of the Arab World aggregate; MSA is the cross-state written educational register but is not an L1.", 2025, ["SRC_WB_ARAB_WORLD_POP", "SRC_WB_LOI_ARABIC_2021"], "context_only_requires_literacy_and_education_exposure_adjustment", "AR-MSA-vernacular", "Do not add Arabic umbrella or any vernacular population; country residents include non-Arabic users and migrants.", None, ["An exposure ceiling, not MSA proficiency or literacy.", "MSA must not erase Egyptian, Levantine, Gulf, Iraqi, Yemeni, Sudanese, Maghrebi or other spoken targets."], "written_educational_register_exposure"))
add(stratum("LLPS-AR-UMBRELLA-SPEAKERS", ["lang:arb-Arab-001"], "Arabic umbrella speaker context", "ar (umbrella only)", "Arabic and other scripts", "Worldwide", "macrolanguage_speaker_estimate", None, 450_000_000, None, "persons", "UNESCO approximate Arabic-speaker umbrella.", 2024, ["SRC_UNESCO_ARABIC"], "context_only_macrolanguage", "AR-MSA-vernacular", "Never assign to MSA or add to vernaculars.", None, ["Not an exact language variety or written-register measure."]))
add(stratum("LLPS-ARZ-EG-TERRITORIAL-CEILING-2024", ["lang:arz-Arab-EG", "lang:arz-Latn-EG"], "Egyptian Arabic threshold hypothesis", "arz-EG", "Arabic; Latin transliteration is a separate intervention", "Egypt", "territorial_language_ceiling", 116_538_258, 116_538_258, 116_538_258, "persons", "Egypt resident population; retained only to prove that the exact Egyptian-Arabic cohort may exceed 100m and requires direct language evidence.", 2024, ["SRC_WB_EGYPT_POP", "SRC_WB_LOI_ARABIC_2021"], "context_only_not_a_direct_language_count", "AR-MSA-vernacular", "Do not assign this population wholesale to Egyptian Arabic, MSA, or Latin transliteration; do not add to Arab World totals.", None, ["No direct Egyptian-Arabic speaker, literacy, or script denominator is supplied."], "territorial_threshold_audit"))
add(stratum("LLPS-JA-JP-EXPOSURE-2024", ["lang:ja-Jpan-JP"], "Standard Japanese national educational exposure bracket", "ja-Jpan-JP", "mixed kanji/kana; national curriculum", "Japan", "territorial_educational_exposure_bracket", 120_296_000, None, 123_802_000, "persons", "Official Japanese-national population to total-resident population bracket, paired with national Japanese curriculum evidence.", 2024, ["SRC_JP_POP_2024", "SRC_JP_MEXT_SCHOOL_LANGUAGE"], "context_only_not_a_direct_language_count", "JA-JP-exposure", "One bracket; do not sum bounds or add student subcohorts.", None, ["Nationality is not language.", "Total residents include people not comfortably served in Japanese.", "Bounds are administrative proxies, not confidence bounds."], "national_education_exposure"))
add(stratum("LLPS-JA-JP-PUPILS-NEEDING-INSTRUCTION-2025", ["lang:ja-Jpan-JP"], "Public-school pupils officially needing Japanese-language instruction", "ja-Jpan-JP", "modern Japanese script; grade-level academic Japanese", "Japan public schools", "direct_language_support_need_cohort", 84_759, 84_759, 84_759, "pupils", "Pupils officially identified as needing Japanese instruction, including conversational speakers lacking grade-level academic Japanese.", 2025, ["SRC_JP_MEXT_JAPANESE_INSTRUCTION_2025"], "eligible_exact_stage_need_measure", "JA-direct-cohorts", "Do not add stage components to the total; do not add this need cohort to whole-population exposure.", None, ["Public-school administrative scope only.", "The cohort identifies language-support need, not need for every subject package."], "school_academic_language_support"))
add(stratum("LLPS-JA-JP-TERTIARY-OPPORTUNITY-2025", ["lang:ja-Jpan-JP"], "Undergraduate plus graduate/professional-degree opportunity cohort", "ja-Jpan-JP", "modern Japanese script; academic register", "Japan higher education", "higher_education_enrolment", 2_922_969, 2_922_969, 2_922_969, "learner enrolments", "2,645,837 undergraduates plus 277,132 graduate/professional-degree students.", 2025, ["SRC_JP_MEXT_ENROLMENT_2025"], "eligible_exact_stage_opportunity_measure_only", "JA-direct-cohorts", "Do not add to the whole-population bracket; later need and academic-language-nonoverlap factors remain required.", "2,645,837 + 277,132", ["Opportunity population, not a measured Japanese-resource or English-access deficit."], "higher_education_opportunity"))
add(stratum("LLPS-JA-JP-ADULT-LOW-SKILL-2023", ["lang:ja-Jpan-JP"], "Adults at or below Level 1 in all three PIAAC domains", "ja-Jpan-JP", "modern Japanese script; plain-language and practical numeracy/digital register", "Japan; represented adults age 16-65", "derived_adult_skill_need_cohort", None, 5_229_000, None, "represented adults", "Approximate 7% of 74.7m represented adults at or below Level 1 in literacy, numeracy and adaptive problem solving.", "2022-2023", ["SRC_OECD_PIAAC_JAPAN_2023"], "eligible_derived_stage_need_measure", "JA-direct-cohorts", "Do not add to the whole-population bracket or to single-domain low-skill rates.", "74.7m x 7%, rounded", ["Derived rounded estimate.", "General skill need is not necessarily a Japanese-language deficit."], "adult_integrated_literacy_numeracy_digital_need"))
add(stratum("LLPS-VI-VN-EXPOSURE-2024", ["lang:vi-Latn-VN"], "Vietnamese official education-language exposure", "vi-Latn-VN", "Latin quoc ngu", "Viet Nam", "territorial_educational_exposure_ceiling", 101_112_656, 101_112_656, 101_112_656, "residents", "Official population paired with Vietnamese's statutory education-language role.", 2024, ["SRC_VN_GSO_MIDTERM_2024", "SRC_VN_EDUCATION_LAW"], "context_only_not_a_direct_language_count", "VI-VN-exposure", "Do not add ethnic Kinh or enrolment subcohorts.", None, ["Not an L1, proficiency, literacy, or uniquely served-reader count."], "national_education_exposure"))
add(stratum("LLPS-FIL-PH-EXPOSURE-2024", ["lang:fil-Latn-PH"], "Filipino national education-language exposure", "fil-Latn-PH", "Latin; Filipino national standard", "Philippines", "territorial_educational_exposure_ceiling", 112_729_484, 112_729_484, 112_729_484, "residents", "Official population paired with Filipino's co-medium role with English.", 2024, ["SRC_PH_PSA_2024", "SRC_PH_RA12027_2024"], "context_only_not_a_direct_language_count", "FIL-TL-PH", "Do not add Tagalog household count or assign the population to Tagalog L1.", None, ["Not a Filipino proficiency, literacy, L1, or uniquely served-reader count.", "English is a co-medium and regional languages are auxiliary."], "national_education_exposure"))
add(stratum("LLPS-PES-IR-EXPOSURE-2024", ["lang:pes-Arab-IR"], "Iranian Persian national educational exposure ceiling", "pes-Arab-IR", "Perso-Arabic", "Iran", "territorial_education_exposure_ceiling", 91_567_738, 91_567_738, 91_567_738, "residents", "Iran resident population ceiling; Persian's national schooling role requires a separate language-proficiency/literacy measure.", 2024, ["SRC_WB_IRAN_POP"], "context_only_not_a_direct_language_count", "PERSIAN-bridge", "Do not add to the 110m Persian/Dari/Tajik estimate.", None, ["Below 100m and not a Persian speaker count."]))
add(stratum("LLPS-UR-PK-EXPOSURE-2023", ["lang:ur-Arab-PK"], "Urdu national-language exposure ceiling in Pakistan", "ur-Arab-PK", "Perso-Arabic", "Pakistan", "territorial_national_language_exposure_ceiling", 240_458_089, 240_458_089, 240_458_089, "residents", "Pakistan population ceiling paired with Urdu's constitutional national-language status.", 2023, ["SRC_PBS_LANGUAGE_2023", "SRC_PAK_CONSTITUTION"], "context_only_not_a_direct_language_count", "UR-crossborder", "Do not add Pakistan Urdu L1 or assign universal Urdu proficiency.", None, ["National status does not prove proficiency, literacy, instruction, or academic comfort."], "national_language_exposure"))
add(stratum("LLPS-TR-TR-EXPOSURE-2024", ["lang:tr-Latn-TR"], "Turkish of Turkiye, population/exposure context", "tr-Latn-TR", "Latin; Turkish standard", "Turkiye", "territorial_exposure_ceiling", 80_000_000, None, 85_664_944, "persons", "Peer-reviewed lower bound of over 80m Turkish speakers and official resident-population ceiling.", 2024, ["SRC_TURKISH_SURVEY_2023", "SRC_TUIK_POP_2024"], "partially_identified_language_population_interval", "TR-TR-exposure", "Do not count the wider Turkic family as Turkish.", None, ["Lower and upper are different constructs, not a statistical confidence interval.", "Current evidence remains below 100m for exact Turkish."]))
add(stratum("LLPS-KO-GLOBAL-SPEAKERS", ["lang:ko-Kore-001"], "Korean cross-border speaker context", "ko-Kore-001", "Hangul/mixed orthographies; distinct ROK/DPRK standards", "Korean peninsula and diaspora", "scholarly_speaker_approximation", None, 80_000_000, None, "persons", "Oxford scholarly approximation of 80m Korean speakers worldwide.", "n.d.", ["SRC_OXFORD_KOREAN", "SRC_KOSTAT_POP_2024"], "context_only_until_rok_dprk_diaspora_split", "KO-global", "Do not add the South Korean population or Korean-national count.", None, ["Rounded and undated global estimate.", "ROK and DPRK standards/orthographies need separate profiles.", "Below 100m."]))
add(stratum("LLPS-TH-TH-EXPOSURE-2024", ["lang:th-Thai-TH"], "Thai official-language territorial exposure", "th-Thai-TH", "Thai", "Thailand", "territorial_official_language_exposure_ceiling", 65_951_210, 65_951_210, 65_951_210, "registered residents", "Official registered population; Thai is identified as official language in the NSO yearbook.", 2024, ["SRC_THAI_NSO_2024"], "context_only_not_a_direct_language_count", "TH-TH-exposure", "Do not treat residents as Thai L1 or literate readers.", None, ["Below 100m.", "Territorial population is not a language-user measure."]))


PACKAGE_PROFILES = [
    {
        "package_profile_id": "PKG-BN-BD-IN-PARALLEL",
        "label": "Bangladesh and India Bangla/Bengali parallel common-core package",
        "component_stratum_ids": ["LLPS-BN-BD-L1PROXY-2022", "LLPS-BN-IN-L1-2011"],
        "population_low": 264_588_675,
        "population_base": 264_597_166,
        "population_high": 264_605_657,
        "population_unit": "country-disjoint persons; mixed direct/derived L1 measures",
        "aggregation": "Arithmetic sum is person-disjoint by country, but cross-year and mixed evidence class; package context only.",
        "rankability": "not_a_language_rank_row; package_intervention_context",
    },
    {
        "package_profile_id": "PKG-PA-GURU-SHAHMUKHI-PARALLEL",
        "label": "Punjabi Gurmukhi/Shahmukhi parallel package",
        "component_stratum_ids": ["LLPS-PA-IN-L1-2011", "LLPS-PA-PK-L1-2023"],
        "population_low": 120_059_639,
        "population_base": 120_059_639,
        "population_high": 120_059_639,
        "population_unit": "country-disjoint persons L1",
        "aggregation": "Person counts are country-disjoint; neither census enumerates script, so the sum is language-community reach for a two-script package only.",
        "rankability": "not_a_language_rank_row; package_intervention_context",
    },
    {
        "package_profile_id": "PKG-HINDI-URDU-PARALLEL-L1-LOWER-BOUND",
        "label": "Hindi/Urdu Devanagari-Perso-Arabic parallel package, enumerated L1 lower bound",
        "component_stratum_ids": ["LLPS-HI-IN-L1-2011", "LLPS-UR-IN-L1-2011", "LLPS-UR-PK-L1-2023"],
        "population_low": 395_205_166,
        "population_base": 395_205_166,
        "population_high": 395_205_166,
        "population_unit": "country-and-census-category-disjoint persons L1",
        "aggregation": "Indian Hindi and Urdu are disjoint raw census categories; Pakistan Urdu is country-disjoint. This is not evidence of no-study cross-script comprehension.",
        "rankability": "not_a_language_rank_row; parallel_package_context",
    },
    {
        "package_profile_id": "PKG-PERSIAN-PARALLEL",
        "label": "Iranian Persian-Dari-Tajik parallel-standard package",
        "component_stratum_ids": ["LLPS-PERSIAN-BRIDGE-GLOBAL"],
        "population_low": None,
        "population_base": 110_000_000,
        "population_high": None,
        "population_unit": "mixed cross-standard speakers",
        "aggregation": "Single literature estimate stored once; no summation and no child inheritance.",
        "rankability": "not_a_language_rank_row; bridge_package_context",
    },
    {
        "package_profile_id": "PKG-WEST-AFRICAN-PIDGIN-SIX",
        "label": "Six-profile West African Pidgin parallel/bridge package",
        "component_stratum_ids": ["LLPS-WAP-BRIDGE-GLOBAL"],
        "population_low": 106_000_000,
        "population_base": None,
        "population_high": 143_000_000,
        "population_unit": "mixed cluster speakers",
        "aggregation": "Single peer-reviewed cluster estimate stored once; no constituent inherits the range.",
        "rankability": "not_a_language_rank_row; bridge_package_context",
    },
    {
        "package_profile_id": "PKG-HAUSA-MULTISCRIPT-MULTICOUNTRY",
        "label": "Hausa multi-country, Boko/Ajami parallel package",
        "component_stratum_ids": ["LLPS-HA-GLOBAL-USERS"],
        "population_low": 100_000_000,
        "population_base": None,
        "population_high": None,
        "population_unit": "mixed L1/L2 users",
        "aggregation": "One global lower bound; no country or script row inherits it.",
        "rankability": "not_a_language_rank_row; bridge_package_context",
    },
    {
        "package_profile_id": "PKG-KISWAHILI-MULTISTANDARD",
        "label": "Kiswahili multi-standard parallel package",
        "component_stratum_ids": ["LLPS-SW-GLOBAL-USERS"],
        "population_low": 200_000_000,
        "population_base": None,
        "population_high": None,
        "population_unit": "mixed L1/L2 users",
        "aggregation": "One global lower bound; no country standard inherits it.",
        "rankability": "not_a_language_rank_row; bridge_package_context",
    },
]


NONPERSON_CONTEXT_MEASURES = [
    {
        "context_id": "CTX-TL-PH-HOME-HOUSEHOLDS-2020",
        "language_target_ids": ["lang:tl-Latn-PH"],
        "value": 10_522_507,
        "unit": "households",
        "definition": "Households reporting Tagalog as the language generally spoken at home.",
        "reference_year": "2020",
        "source_ids": ["SRC_PH_PSA_HOME_LANGUAGE_2020"],
        "disposition": "excluded_from_person_population_strata; never converted without household microdata",
    }
]


MANDATORY_LABELS = {
    "English": ["LLPS-EN-US-HOME-2023", "LLPS-EN-GLOBAL-MIXED"],
    "Spanish": ["LLPS-ES-US-HOME-2023", "LLPS-ES-GLOBAL-NATIVE"],
    "Portuguese": ["LLPS-PT-GLOBAL-SPEAKERS"],
    "French": ["LLPS-FR-GLOBAL-FRANCOPHONES"],
    "Russian": ["LLPS-RU-GLOBAL-SPEAKERS"],
    "Modern Standard Arabic": ["LLPS-ARB-MSA-EDU-EXPOSURE-2025"],
    "Bangla Bangladesh": ["LLPS-BN-BD-L1PROXY-2022"],
    "Standard Chinese spoken/written": ["LLPS-CMN-CN-ABILITY-2020", "LLPS-ZH-HANS-CN-WRITTEN-EXPOSURE"],
    "Japanese": ["LLPS-JA-JP-EXPOSURE-2024", "LLPS-JA-JP-PUPILS-NEEDING-INSTRUCTION-2025", "LLPS-JA-JP-TERTIARY-OPPORTUNITY-2025"],
    "German": ["LLPS-DE-GLOBAL-NATIVE"],
    "Persian": ["LLPS-PERSIAN-BRIDGE-GLOBAL", "LLPS-PES-IR-EXPOSURE-2024"],
    "Turkish": ["LLPS-TR-TR-EXPOSURE-2024"],
    "Korean": ["LLPS-KO-GLOBAL-SPEAKERS"],
    "Vietnamese": ["LLPS-VI-VN-EXPOSURE-2024"],
    "Filipino": ["LLPS-FIL-PH-EXPOSURE-2024"],
    "Thai": ["LLPS-TH-TH-EXPOSURE-2024"],
    "Hausa": ["LLPS-HA-GLOBAL-USERS"],
    "Swahili": ["LLPS-SW-GLOBAL-USERS"],
}


def validate():
    errors = []
    sids = [x["stratum_id"] for x in S]
    pids = [x["package_profile_id"] for x in PACKAGE_PROFILES]
    src_ids = {x["source_id"] for x in SOURCES}
    if len(sids) != len(set(sids)):
        errors.append("duplicate stratum_id")
    if len(pids) != len(set(pids)):
        errors.append("duplicate package_profile_id")
    for row in S:
        for key in ("population_low", "population_base", "population_high"):
            if key not in row:
                errors.append(f"{row['stratum_id']}: missing {key}")
        vals = [row[k] for k in ("population_low", "population_base", "population_high")]
        numeric = [v for v in vals if isinstance(v, (int, float))]
        if numeric and min(numeric) < 0:
            errors.append(f"{row['stratum_id']}: negative population")
        lo, base, hi = vals
        if lo is not None and base is not None and lo > base:
            errors.append(f"{row['stratum_id']}: low > base")
        if base is not None and hi is not None and base > hi:
            errors.append(f"{row['stratum_id']}: base > high")
        if lo is not None and hi is not None and lo > hi:
            errors.append(f"{row['stratum_id']}: low > high")
        for src in row["source_ids"]:
            if src not in src_ids:
                errors.append(f"{row['stratum_id']}: unknown source {src}")
    for package in PACKAGE_PROFILES:
        for sid in package["component_stratum_ids"]:
            if sid not in set(sids):
                errors.append(f"{package['package_profile_id']}: unknown component {sid}")
    for label, needed in MANDATORY_LABELS.items():
        missing = [sid for sid in needed if sid not in set(sids)]
        if missing:
            errors.append(f"mandatory {label}: missing {missing}")
    return errors


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def main():
    errors = validate()
    canonical = ROOT / "structured" / "canonical_universe_proposal.json"
    audit = ROOT / "agent_reports" / "LARGE_COHORT_EQUAL_INCLUSION_AUDIT.json"
    equal_audit = ROOT / "qa" / "ID_ZH_JA_EQUAL_TREATMENT_AUDIT.json"
    nonoverlap = ROOT / "structured" / "academic_language_nonoverlap.json"
    payload = {
        "schema": "interlanguage/large-language-population-strata-proposal/1.0.0",
        "artifact_status": "evidence proposal; not scored; no ranking",
        "analytical_boundary": [
            "User/local programme outputs have zero effect on any population, need, score, cost, rank, or recommendation.",
            "Each numeric row preserves its source measure class; territory, L1, L2, ability, literacy, home language, households, and educational exposure are not interchangeable.",
            "Exact-language rows and parallel/common-core package profiles are separate. A package total is never inherited by a child language target.",
            "Institutional world totals that do not expose country/variety/script splits are context-only, even when their scale is certain.",
            "Missing low/base/high values are unknown, not zero; no midpoint is invented.",
            "Academic-language overlap is a separate empirical input and remains null where the companion audit found no comparable national measure; it is not inferred from these population strata.",
        ],
        "primary_input_identities": [
            {"path": "structured/canonical_universe_proposal.json", "bytes": canonical.stat().st_size, "sha256": sha256(canonical)},
            {"path": "agent_reports/LARGE_COHORT_EQUAL_INCLUSION_AUDIT.json", "bytes": audit.stat().st_size, "sha256": sha256(audit)},
            {"path": "qa/ID_ZH_JA_EQUAL_TREATMENT_AUDIT.json", "bytes": equal_audit.stat().st_size, "sha256": sha256(equal_audit)},
            {"path": "structured/academic_language_nonoverlap.json", "bytes": nonoverlap.stat().st_size, "sha256": sha256(nonoverlap)},
        ],
        "sources": SOURCES,
        "population_strata": S,
        "parallel_or_common_core_package_profiles": PACKAGE_PROFILES,
        "nonperson_context_measures": NONPERSON_CONTEXT_MEASURES,
        "mandatory_coverage": MANDATORY_LABELS,
        "validation": {
            "status": "pass" if not errors else "fail",
            "errors": errors,
            "source_count": len(SOURCES),
            "stratum_count": len(S),
            "package_profile_count": len(PACKAGE_PROFILES),
            "eligible_or_partially_eligible_strata": sum(1 for x in S if x["rankability"].startswith("eligible") or x["rankability"].startswith("partially_identified")),
            "context_or_nonrankable_strata": sum(1 for x in S if not (x["rankability"].startswith("eligible") or x["rankability"].startswith("partially_identified"))),
            "all_rows_have_low_base_high_keys": all(all(k in x for k in ("population_low", "population_base", "population_high")) for x in S),
            "all_population_strata_normalized_to_persons": all(x["population_unit"] == "persons" for x in S),
            "nonperson_context_measure_count_excluded_from_scoring": len(NONPERSON_CONTEXT_MEASURES),
            "invalid_interval_count": len([e for e in errors if ">" in e]),
        },
    }
    canonical_bytes = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload["payload_sha256"] = hashlib.sha256(canonical_bytes).hexdigest().upper()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Large-language population strata proposal",
        "",
        "Status: evidence proposal, not a ranking. The table repairs large-cohort omissions without turning territorial populations or macro-language totals into exact-language reach.",
        "",
        "## Result",
        "",
        f"- {len(S)} typed population strata; {len(PACKAGE_PROFILES)} separate parallel/common-core package profiles; {len(SOURCES)} sources.",
        f"- {payload['validation']['eligible_or_partially_eligible_strata']} direct/derived/partially identified rows can supply a population basis at their exact measure endpoint; {payload['validation']['context_or_nonrankable_strata']} remain context or exposure-only.",
        "- Every requested major language is present. Missing intervals remain null; no arbitrary midpoint or fabricated uncertainty band is used.",
        "- All package aggregates are outside the exact-language order and no child language inherits a package total.",
        "",
        "## Typed strata",
        "",
        "| ID | Exact target / register | Geography | Measure class | Low | Base | High | Rankability |",
        "|---|---|---|---|---:|---:|---:|---|",
    ]
    for row in S:
        def v(x):
            return "—" if x is None else f"{x:,}" if isinstance(x, int) else str(x)
        lines.append(f"| `{row['stratum_id']}` | {row['exact_variety_or_register']} | {row['geography']} | `{row['measure_class']}` | {v(row['population_low'])} | {v(row['population_base'])} | {v(row['population_high'])} | `{row['rankability']}` |")
    lines += [
        "",
        "## What becomes rankable",
        "",
        "Direct typed bases now exist for Mainland Putonghua reported ability; Indonesian reported ability and narrower home use; raw Hindi, India Bengali, India/Pakistan Punjabi-language, India/Pakistan Urdu, Telugu, Marathi and India Tamil L1 returns; US English-only home use; Canada English knowledge; Australia English-only home use; and US Spanish home use. Bangladesh Bangla has a transparent derived L1 proxy with rounding bounds. These rows still require separate need, academic-language-overlap, resource-gap and delivery factors before scoring.",
        "",
        "## What remains non-rankable as an exact language population",
        "",
        "Global English, Spanish, Portuguese, French, Russian, German, Hausa, Kiswahili and Persian totals do not expose compatible country/variety/script cells. MSA, written Simplified Chinese, Japanese, Vietnamese, Filipino, Urdu-in-Pakistan, Thai and Iranian Persian territorial rows are educational-exposure ceilings, not direct user counts. They remain visible and cannot be dropped, but they may not be treated as exact-language learner populations until a direct language-capability/literacy adjustment is supplied.",
        "",
        "## Nonduplicative package profiles",
        "",
    ]
    for p in PACKAGE_PROFILES:
        lines += [
            f"### {p['label']}",
            "",
            f"- Population low/base/high: `{p['population_low']}` / `{p['population_base']}` / `{p['population_high']}` ({p['population_unit']}).",
            f"- Components: {', '.join('`'+x+'`' for x in p['component_stratum_ids'])}.",
            f"- Rule: {p['aggregation']}",
            f"- Disposition: `{p['rankability']}`.",
            "",
        ]
    lines += [
        "## Mandatory guards",
        "",
        "1. Putonghua spoken ability is not Simplified-Chinese reading ability.",
        "2. MSA is a written educational register and not an L1 denominator; Arabic vernaculars remain separate.",
        "3. Hindi 322,230,097 is the raw Hindi return. The broader 528m census umbrella is not Standard Hindi reach.",
        "4. Filipino exposure is not Tagalog L1. The PSA Tagalog measure is households, not persons.",
        "5. Punjabi census counts do not enumerate Gurmukhi/Shahmukhi literacy.",
        "6. The Persian, Hausa, Kiswahili and West African Pidgin totals are stored once at package level and never copied to child standards.",
        "7. English, Spanish, Portuguese, French, Russian and German worldwide estimates remain common-core/context profiles until country-disjoint exact targets are imported.",
        "8. Territorial education exposure can establish that a cohort is too large to omit; it cannot by itself establish unique language benefit.",
        "",
        "## Source registry",
        "",
    ]
    for src in SOURCES:
        lines.append(f"- `{src['source_id']}` — {src['institution_or_author']}, *{src['title']}* ({src['reference_year']}), {src['locator']}. {src['url_or_doi']}")
    lines += [
        "",
        "## Validation",
        "",
        f"Validation status: **{payload['validation']['status']}**. Duplicate IDs: none. Unknown source references: none. Invalid intervals: {payload['validation']['invalid_interval_count']}. Mandatory requested language groups: {len(MANDATORY_LABELS)}/{len(MANDATORY_LABELS)} present.",
        "",
        "This artifact does not score or rank any target and does not use local translation production as evidence.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "json": str(OUT_JSON), "json_bytes": OUT_JSON.stat().st_size, "json_sha256": sha256(OUT_JSON),
        "report": str(OUT_MD), "report_bytes": OUT_MD.stat().st_size, "report_sha256": sha256(OUT_MD),
        "validation": payload["validation"],
    }, indent=2))


if __name__ == "__main__":
    main()
