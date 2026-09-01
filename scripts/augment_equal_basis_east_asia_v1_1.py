#!/usr/bin/env python3
"""Idempotently register corrected equal-basis profiles.

This runs after the legacy master builders.  It preserves the distinction between a
territory population ceiling used for ex-ante sensitivity analysis and a measured
comfortable-reader or underserved-person count, which neither row supplies.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_csv(name: str) -> tuple[list[str], list[dict[str, str]]]:
    with (ROOT / name).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def upsert(name: str, key: str, replacements: list[dict[str, str]]) -> None:
    path = ROOT / name
    if path.exists():
        fields, rows = read_csv(name)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        fields, rows = list(replacements[0]), []
    wanted = {row[key]: row for row in replacements}
    output: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        value = row[key]
        if value in wanted:
            output.append({field: wanted[value].get(field, "") for field in fields})
            seen.add(value)
        else:
            output.append(row)
    for value, row in wanted.items():
        if value not in seen:
            output.append({field: row.get(field, "") for field in fields})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)


INDONESIAN_CANDIDATE = {
    "intervention_id": "NAT-121", "target_type": "natural_language",
    "target_name": "Bahasa Indonesia", "variety_or_register": "id-Latn-ID",
    "script": "Latn", "territory_scope": "Indonesia", "curriculum_source": "Open Logic Project",
    "curriculum_work": "Formal-reasoning core", "curriculum_unit": "FR-2",
    "adaptation_depth": "D3", "formats": "AX-HTML;AX-PDF;AX-OFFLINE",
    "existing_local_status": "established Indonesian program; Open Logic complete 722 of 722; public catalog verifies 27 of 40 roles published and 13 in production; page ledgers document multiple noninterchangeable rendered/corpus universes and no final translated-page total; ex-ante equal-basis row",
    "source_ids": "PM-S021;ACE-E021;ACE-E023;CURRENT_INDONESIAN_PROGRAM_STATUS_20260830;INDONESIAN_PUBLIC_PROGRAM_AUDIT_20260830;INDONESIAN_PROGRAM_COMPUTE_AND_PAGE_RECONCILIATION_20260830",
    "evidence_status": "official functional-language population ceiling; exact current public program inventory; written access and academic-language non-overlap remain sensitivities",
    "overlap_rule": "Credit only the exact Bahasa Indonesia cell. Keep D=1 solely for the ex-ante equal-treatment opportunity comparison; use D=0 for any ex-post Open Logic completion analysis.",
    "notes": "Equal-treatment counterfactual for whether Bahasa Indonesia belonged in the original language opportunity set. The completed-baseline row answers the ex-post question; future work targets only the exact 13 production roles or demonstrated format/access gaps.",
    "rankability_status": "requires_exact_population_join",
    "profile_tag_status": "single_valid_bcp47", "profile_resolution_status": "resolved_single_profile",
    "profile_ranking_treatment": "ex_ante_equal_basis_rank_forward_residual_separate",
    "profile_negative_control_status": "", "profile_source_ids": "ACE-E021;TP-S001-IANA;TP-S002-CLDR",
    "resolved_edition_name": "Bahasa Indonesia",
}

CHINESE_CANDIDATE = {
    "intervention_id": "NAT-122", "target_type": "natural_language",
    "target_name": "Mainland Simplified Chinese", "variety_or_register": "zh-Hans-CN",
    "script": "Hans", "territory_scope": "China", "curriculum_source": "Open Logic Project",
    "curriculum_work": "Formal-reasoning core", "curriculum_unit": "FR-2",
    "adaptation_depth": "D3", "formats": "AX-HTML;AX-PDF;AX-OFFLINE",
    "existing_local_status": "complete Open Logic 722 of 722 and Algebra and Trigonometry 2e 94 of 94; Calculus Volume 1 30 of 55; six additional fixed STEM books pending; ex-ante equal-basis row",
    "source_ids": "PM-S022;ACE-E060;ACE-E061;ACE-E062;ACE-E063",
    "evidence_status": "official mainland census denominator and standardized-character prevalence; exact written academic comfort remains a sensitivity; local completion and accessibility residual are hash-pinned",
    "overlap_rule": "Credit only the zh-Hans-CN mainland written-standard cell. Keep D=1 solely for the ex-ante equal-treatment opportunity comparison; use D=0 for each exact completed corpus and measured source-token residual for partial works.",
    "notes": "Equal-treatment counterfactual for the original language-opportunity set. Forward work must not duplicate completed Open Logic or Algebra and Trigonometry; prioritize exact STEM residual, semantic accessibility, and demonstrated advanced gaps.",
    "rankability_status": "requires_exact_population_join",
    "profile_tag_status": "single_valid_bcp47", "profile_resolution_status": "resolved_single_profile",
    "profile_ranking_treatment": "ex_ante_equal_basis_rank_forward_residual_separate",
    "profile_negative_control_status": "", "profile_source_ids": "ACE-E061;TP-S001-IANA;TP-S002-CLDR",
    "resolved_edition_name": "Standard Simplified Chinese (Mainland China)",
}

JAPANESE_CANDIDATE = {
    "intervention_id": "NAT-123", "target_type": "natural_language",
    "target_name": "Japanese", "variety_or_register": "ja-Jpan-JP", "script": "Jpan",
    "territory_scope": "Japan", "curriculum_source": "Open Logic Project",
    "curriculum_work": "Formal-reasoning core", "curriculum_unit": "FR-2",
    "adaptation_depth": "D3", "formats": "AX-HTML;AX-PDF;AX-OFFLINE",
    "existing_local_status": "strong national compulsory-school and advanced mathematics supply; no complete exact local FR-2 edition registered; stage-specific open, accessible, postgraduate, and frontier gaps researched; ex-ante equal-basis row",
    "source_ids": "PM-S023;ACE-E064;ACE-E065;ACE-E068",
    "evidence_status": "official Japan census territory denominator plus bounded school and advanced-supply audit; Japanese comfortable-reader count and exact open-access deficit remain sensitivities",
    "overlap_rule": "Credit only a ja-Jpan-JP gross territory ceiling in the ex-ante sensitivity comparison. Do not treat the census total as a Japanese-language or underserved-reader count. Forward work is stage-specific and must not duplicate strong compulsory-school provision.",
    "notes": "Equal-basis correction. Forward commissioning starts with a proof-to-algebra prerequisite bridge, semantic accessibility, or an exact postgraduate/research-frontier absence rather than another generic compulsory-school algebra book.",
    "rankability_status": "requires_exact_population_join",
    "profile_tag_status": "single_valid_bcp47", "profile_resolution_status": "resolved_single_profile",
    "profile_ranking_treatment": "ex_ante_equal_basis_rank_forward_stage_specific",
    "profile_negative_control_status": "", "profile_source_ids": "ACE-E064;ACE-E065;TP-S001-IANA;TP-S002-CLDR",
    "resolved_edition_name": "Japanese (Japan)",
}

HINDI_CANDIDATE = {
    "intervention_id": "NAT-124", "target_type": "natural_language",
    "target_name": "Standard Hindi", "variety_or_register": "hi-Deva-IN",
    "script": "Deva", "territory_scope": "India", "curriculum_source": "Open Logic Project",
    "curriculum_work": "Formal-reasoning core", "curriculum_unit": "FR-2",
    "adaptation_depth": "D3", "formats": "AX-HTML;AX-PDF;AX-OFFLINE",
    "existing_local_status": "complete local Hindi formal-reasoning edition recorded in the Hindi-Urdu lane; ex-ante equal-basis row; forward work limited to uncovered subject, stage, and accessibility residuals",
    "source_ids": "PM-S001;ACE-E011;ACE-E019;ACE-A007",
    "evidence_status": "official same-name Hindi mother-tongue component; the larger census Hindi category and C-17 first/second/third-language totals remain separate umbrella or conversational sensitivities",
    "overlap_rule": "Credit only the C-16 same-name Hindi mother-tongue component for the exact hi-Deva-IN ex-ante row. Never substitute the 528,347,193 Hindi census umbrella or the 691,347,193 reported first/second/third-language union for Standard Hindi academic readership.",
    "notes": "Equal-treatment correction for a completed language program. Keep D=1 only for ex-ante comparison; use D=0 for the exact completed formal-reasoning corpus and commission only demonstrated subject, stage, format, or accessibility residuals.",
    "rankability_status": "requires_exact_population_join",
    "profile_tag_status": "single_valid_bcp47", "profile_resolution_status": "resolved_single_profile",
    "profile_ranking_treatment": "ex_ante_equal_basis_rank_forward_residual_separate",
    "profile_negative_control_status": "completed_exact_corpus_not_language_wide_zero",
    "profile_source_ids": "ACE-E011;ACE-E019;TP-S001-IANA;TP-S002-CLDR",
    "resolved_edition_name": "Standard Hindi (India)",
}

BHOJPURI_INDIA_CANDIDATE = {
    "intervention_id": "NAT-125", "target_type": "natural_language",
    "target_name": "Bhojpuri", "variety_or_register": "bho-Deva-IN",
    "script": "Deva", "territory_scope": "India", "curriculum_source": "OpenStax",
    "curriculum_work": "Algebra and Trigonometry 2e", "curriculum_unit": "MV-1",
    "adaptation_depth": "D2", "formats": "AX-HTML;AX-PDF;AX-OFFLINE",
    "existing_local_status": "missing; Indian Bhojpuri was previously hidden inside the Hindi census umbrella while only the much smaller Nepal profile was ranked",
    "source_ids": "PM-S001;ACE-E011",
    "evidence_status": "official exact C-16 Bhojpuri mother-tongue row; educational standard and cross-border technical-register fit remain separate research variables",
    "overlap_rule": "Credit the 50,579,447 Indian Bhojpuri row only once. It is nested inside the printed Hindi census umbrella, so never add both. Keep the Nepal Bhojpuri population and regional package separately tagged.",
    "notes": "Largest exact missing South Asian natural-language profile found by the universe-completeness audit. A shared India-Nepal semantic source may reduce compute, but each regional edition retains its own population cell.",
    "rankability_status": "requires_exact_population_join",
    "profile_tag_status": "single_valid_bcp47", "profile_resolution_status": "resolved_single_profile",
    "profile_ranking_treatment": "rank_exact_india_profile_cross_border_reuse_separate",
    "profile_negative_control_status": "", "profile_source_ids": "ACE-E011;TP-S001-IANA",
    "resolved_edition_name": "Bhojpuri (India)",
}

CHINESE_OBSERVATION = {
    "observation_id": "POP-CN-001", "region": "Asia", "subregion": "Eastern Asia",
    "language_label": "Mainland China population",
    "edition_profile": "zh-Hans-CN standardized written Chinese gross territory ceiling",
    "iso_639_3_or_other_id": "zh-Hans-CN", "territory": "China",
    "modality": "written_text_candidate", "script_or_profile": "Hans",
    "orthography_evidence_status": "official standardized-character prevalence independently established",
    "learner_stratum": "national written-standard potential population",
    "measure_type": "official_census_mainland_population_gross_territory_ceiling", "count_unit": "persons",
    "population_low": "1411778724", "population_base": "1411778724", "population_high": "1411778724",
    "reference_date_or_year": "2020-11-01", "source_id": "PM-S022",
    "source_locator": "Section I Total Population; mainland row 1,411,778,724; note 6",
    "source_observation_transcribed_exactly": "true", "negative_control": "false",
    "source_candidate_flag_superseded": "false",
    "target_mapping_status": "territory_ceiling_with_independent_zh_Hans_CN_written_standard_mapping",
    "observation_use": "gross_upper_bound_pending_intervention_edges", "gross_population_only": "true",
    "rank_ready_marginal_access": "false", "overlap_group_id": "CN-MAINLAND-2020-TOTAL",
    "alternative_measure_role": "standalone_territory_ceiling_not_exact_language_count",
    "academic_lingua_franca_overlap_status": "unmeasured",
    "existing_edition_overlap_status": "partial_exact_corpora_completed_forward_residual_required",
    "portfolio_overlap_status": "single_total_population_ceiling_do_not_sum_with_subpopulations",
    "common_year_status": "source_year_observation_no_projection",
    "caveats": "Total mainland population is not an exact zh-Hans-CN comfort count. MOE reports Putonghua prevalence 80.72% and standardized-character use above 95% among literate people, with substantial regional disparity. Downstream practical-access and academic-nonoverlap sensitivities remain mandatory.",
    "provenance_table": "ACE-E060;ACE-E061",
}

INDONESIAN_OBSERVATION = {
    "observation_id": "POP-ID-018", "region": "Asia", "subregion": "Southeast Asia",
    "language_label": "Bahasa Indonesia",
    "edition_profile": "BPS functional-language category Dapat Berbahasa Indonesia",
    "iso_639_3_or_other_id": "id-Latn-ID", "territory": "Indonesia",
    "modality": "written_text_candidate", "script_or_profile": "Latin",
    "orthography_evidence_status": "exact named functional-language population; written academic comfort unmeasured",
    "learner_stratum": "population_age_5_plus",
    "measure_type": "official_long_form_census_able_to_speak_indonesian_persons_age5plus",
    "count_unit": "persons", "population_low": "", "population_base": "248501794",
    "population_high": "", "reference_date_or_year": "2022", "source_id": "PM-S021",
    "source_locator": "TOTAL row; 248,501,794 able to speak Indonesian of 253,679,348 persons aged 5+",
    "source_observation_transcribed_exactly": "true", "negative_control": "false",
    "source_candidate_flag_superseded": "false",
    "target_mapping_status": "exact_named_functional_language_population_ceiling_for_id_Latn_ID",
    "observation_use": "gross_upper_bound_pending_intervention_edges", "gross_population_only": "true",
    "rank_ready_marginal_access": "false", "overlap_group_id": "",
    "alternative_measure_role": "standalone_functional_language_observation_preferred_over_home_language_for_reach_ceiling",
    "academic_lingua_franca_overlap_status": "unmeasured",
    "existing_edition_overlap_status": "partial_local_editions_subtracted_by_curriculum_not_population",
    "portfolio_overlap_status": "territory_adult_literacy_proxy_sensitivity;unmeasured_low0_neutral0.5_high1_sensitivity",
    "common_year_status": "source_year_observation_no_projection",
    "caveats": "The BPS definition establishes oral functional Indonesian only. It does not establish literacy, academic reading comfort, educational deprivation, or unique readership. Low and high source bounds are unreported, so the model uses the published point as base/high and zero as the evidence-bounded low sensitivity.",
    "provenance_table": "SP-D008",
}

JAPANESE_OBSERVATION = {
    "observation_id": "POP-JP-001", "region": "Asia", "subregion": "Eastern Asia",
    "language_label": "Japan population",
    "edition_profile": "ja-Jpan-JP Japanese gross territory ceiling",
    "iso_639_3_or_other_id": "ja-Jpan-JP", "territory": "Japan",
    "modality": "written_text_candidate", "script_or_profile": "Jpan",
    "orthography_evidence_status": "production profile resolved; census does not measure Japanese-language comfort",
    "learner_stratum": "national written-standard potential population",
    "measure_type": "official_census_territory_population_gross_ceiling", "count_unit": "persons",
    "population_low": "126146099", "population_base": "126146099", "population_high": "126146099",
    "reference_date_or_year": "2020-10-01", "source_id": "PM-S023",
    "source_locator": "Basic Complete Tabulation, Table 1, 2020 exact population 126,146,099",
    "source_observation_transcribed_exactly": "true", "negative_control": "false",
    "source_candidate_flag_superseded": "false",
    "target_mapping_status": "territory_ceiling_with_ja_Jpan_JP_profile_mapping",
    "observation_use": "gross_upper_bound_pending_intervention_edges", "gross_population_only": "true",
    "rank_ready_marginal_access": "false", "overlap_group_id": "JP-2020-TOTAL",
    "alternative_measure_role": "standalone_territory_ceiling_not_exact_language_count",
    "academic_lingua_franca_overlap_status": "unmeasured",
    "existing_edition_overlap_status": "strong_national_supply_stage_specific_open_and_advanced_gap_unmeasured",
    "portfolio_overlap_status": "single_total_population_ceiling_do_not_sum_with_subpopulations",
    "common_year_status": "source_year_observation_no_projection",
    "caveats": "Japan's census total includes residents regardless of language and is not a Japanese comfortable-reader or underserved-person count. Strong compulsory-school and advanced supply reduces forward duplication but does not establish open-license, accessibility, postgraduate, or research-frontier completeness.",
    "provenance_table": "ACE-E064;ACE-E065;ACE-E068",
}

HINDI_OBSERVATION = {
    "observation_id": "POP-IN-COMP-006", "region": "Asia", "subregion": "South Asia",
    "language_label": "Hindi",
    "edition_profile": "C-16 same-name mother-tongue component: Hindi; hi-Deva-IN edition profile independently resolved",
    "iso_639_3_or_other_id": "hin", "territory": "India",
    "modality": "written_text_candidate", "script_or_profile": "Devanagari",
    "orthography_evidence_status": "edition profile resolved independently from the population table",
    "learner_stratum": "same_name_mother_tongue_component_population",
    "measure_type": "census_same_name_mother_tongue_component_persons", "count_unit": "persons",
    "population_low": "322230097", "population_base": "322230097", "population_high": "322230097",
    "reference_date_or_year": "2011", "source_id": "PM-S001",
    "source_locator": "Statement 1, printed pp. 5-6; same-name mother-tongue component Hindi = 322,230,097",
    "source_observation_transcribed_exactly": "true", "negative_control": "false",
    "source_candidate_flag_superseded": "false",
    "target_mapping_status": "same_name_mother_tongue_component_preferred_for_standard_edition",
    "observation_use": "gross_upper_bound_pending_intervention_edges", "gross_population_only": "true",
    "rank_ready_marginal_access": "false", "overlap_group_id": "ALT-POP-IN-006-CATEGORY-COMPONENT",
    "alternative_measure_role": "same_name_component_preferred_over_parent_aggregate",
    "academic_lingua_franca_overlap_status": "c17_category_proxy_available_not_component_measure",
    "existing_edition_overlap_status": "complete_exact_formal_reasoning_corpus_forward_residual_by_unit",
    "portfolio_overlap_status": "nested_in_parent_category_never_sum",
    "common_year_status": "source_year_observation_no_projection",
    "caveats": "The same-name component is 60.988324% of the printed 528,347,193 Hindi census-language umbrella. The umbrella contains Bhojpuri, Chhattisgarhi, Magahi, Rajasthani, and other returns and is not Standard Hindi reach. C-17's 691,347,193 reported first/second/third-language total inherits that umbrella and measures reported language knowledge, not comfortable academic reading. The 322,230,097 component is a gross ex-ante ceiling, not a measured underserved population.",
    "audit_notes": "Exact same-name C-16 component admitted for equal-basis comparison; existing corpus coverage is subtracted at the curriculum-unit level rather than erasing the language population.",
    "provenance_table": "ACE-A099",
}

CHINESE_SOURCE = {
    "source_id": "PM-S022", "title": "Communique of the Seventh National Population Census (No. 2)",
    "authority": "National Bureau of Statistics of China", "reference_date_or_year": "2020-11-01",
    "source_type": "official census communique", "territory": "China",
    "measure_definition": "Persons enumerated in the 31 mainland provinces autonomous regions and municipalities plus servicemen",
    "url": "https://www.stats.gov.cn/english/PressRelease/202105/t20210510_1817187.html",
    "source_locator": "Section I Total Population; mainland row 1,411,778,724; note 6 defines exclusions",
    "accessed_date": "2026-08-30", "source_tier": "1", "confidence": "high",
    "limitations": "Territory population denominator only. It is not an exact count of zh-Hans-CN readers or comfortable academic-language users; Hong Kong, Macao, Taiwan, and foreigners in the 31 jurisdictions are excluded by the source definition.",
    "provenance_table": "ACE-E060",
}

INDONESIAN_SOURCE = {
    "source_id": "PM-S021",
    "title": "Jumlah Penduduk Berumur 5 Tahun ke Atas Menurut Wilayah, Jenis Kelamin, dan Kemampuan Berbahasa Indonesia, di INDONESIA",
    "authority": "BPS-Statistics Indonesia", "reference_date_or_year": "2022",
    "source_type": "official Long Form Population Census 2020 table released for 2022",
    "territory": "Indonesia",
    "measure_definition": "Population aged 5 and over reported able to understand spoken Indonesian and produce Indonesian words intelligible to another person",
    "url": "https://sensus.bps.go.id/topik/tabular/sp2022/196",
    "source_locator": "TOTAL row; Total / Dapat Berbahasa Indonesia = 248,501,794; table metadata and classification definition",
    "accessed_date": "2026-08-30", "source_tier": "1", "confidence": "high",
    "limitations": "This is an official long-form census point estimate of oral functional ability, not written literacy, home language, mother tongue, academic reading comfort, or proof of demand for a particular curriculum. The model therefore treats it as a gross Bahasa Indonesia reach ceiling and applies written-access and academic-language non-overlap factors separately.",
    "provenance_table": "SP-D008",
}

JAPANESE_SOURCE = {
    "source_id": "PM-S023", "title": "Population and Households of Japan 2020: Summary of the Results",
    "authority": "Statistics Bureau of Japan", "reference_date_or_year": "2020-10-01",
    "source_type": "official national census summary", "territory": "Japan",
    "measure_definition": "Total resident population of Japan as of October 1, 2020",
    "url": "https://www.stat.go.jp/english/data/kokusei/2020/summary/pdf/01.pdf",
    "source_locator": "Basic Complete Tabulation, Table 1, 2020 row; 126,146,099 persons",
    "accessed_date": "2026-08-30", "source_tier": "1", "confidence": "high",
    "limitations": "Territory population denominator only. It includes residents regardless of language and is not an exact Japanese-language, comfortable academic-reader, or underserved-person count.",
    "provenance_table": "ACE-E068",
}


def normalized_candidate(row: dict[str, str]) -> dict[str, str]:
    return {key: row.get(key, "") for key in (
        "intervention_id", "target_type", "target_name", "variety_or_register",
        "script", "territory_scope", "curriculum_source", "curriculum_work",
        "curriculum_unit", "adaptation_depth", "formats", "existing_local_status",
        "source_ids", "evidence_status", "overlap_rule", "notes", "rankability_status",
    )}


def normalized_observation(master: dict[str, str], orthography: str) -> dict[str, str]:
    return {
        "population_cell_id": master["observation_id"], "region": master["region"],
        "subregion": master["subregion"], "language_name": master["language_label"],
        "variety_name": master["edition_profile"],
        "iso_639_3_or_other_id": master["iso_639_3_or_other_id"],
        "territory": master["territory"], "source_reported_script": master["script_or_profile"],
        "source_reported_orthography": orthography, "modality": master["modality"],
        "learner_stratum": master["learner_stratum"], "measure_type": master["measure_type"],
        "count_unit": master["count_unit"], "population_low": master["population_low"],
        "population_base": master["population_base"], "population_high": master["population_high"],
        "reference_year": master["reference_date_or_year"], "source_id": master["source_id"],
        "source_locator": master["source_locator"], "confidence": "high",
        "source_observation_transcribed_exactly": "true", "negative_control": "false",
        "producer_strict_reach_flag_superseded": "false",
        "target_mapping_status": master["target_mapping_status"],
        "observation_use": master["observation_use"], "gross_population_only": "true",
        "rank_ready_marginal_access": "false", "requires_intervention_edge": "true",
        "orthography_evidence_status": master["orthography_evidence_status"],
        "academic_lingua_franca_overlap_status": master["academic_lingua_franca_overlap_status"],
        "existing_edition_overlap_status": master["existing_edition_overlap_status"],
        "portfolio_overlap_status": master["portfolio_overlap_status"],
        "overlap_group_id": master["overlap_group_id"],
        "alternative_measure_role": master["alternative_measure_role"],
        "hierarchy_parent_cell_id": "", "overlap_source_id": "", "c17_nonoverlap_low": "",
        "c17_nonoverlap_base": "", "c17_nonoverlap_high": "",
        "corrected_written_population_low": "", "corrected_written_population_base": "",
        "corrected_written_population_high": "", "common_year_status": master["common_year_status"],
        "overlap_notes": "No exact academic-language or underserved-reader deduction is measured; retain explicit sensitivities.",
        "caveats": master["caveats"],
        "audit_notes": master.get(
            "audit_notes",
            "Official population observation admitted only as a gross equal-basis ceiling; never as a measured language-access deficit.",
        ),
    }


def main() -> None:
    upsert(
        "staging/interlanguage_matrix/candidate_interventions_normalized.csv",
        "intervention_id",
        [normalized_candidate(INDONESIAN_CANDIDATE), normalized_candidate(CHINESE_CANDIDATE), normalized_candidate(JAPANESE_CANDIDATE), normalized_candidate(HINDI_CANDIDATE), normalized_candidate(BHOJPURI_INDIA_CANDIDATE)],
    )
    upsert(
        "population_observations_normalized.csv",
        "population_cell_id",
        [
            normalized_observation(INDONESIAN_OBSERVATION, "standard Indonesian Latin orthography"),
            normalized_observation(CHINESE_OBSERVATION, "standard simplified Chinese character profile"),
            normalized_observation(JAPANESE_OBSERVATION, "Japanese mixed kanji-kana writing profile"),
        ],
    )
    upsert(
        "staging/equal_basis_east_asia_v1_1/source_register.csv",
        "source_id",
        [INDONESIAN_SOURCE, CHINESE_SOURCE, JAPANESE_SOURCE],
    )
    upsert("candidate_interventions_master.csv", "intervention_id", [INDONESIAN_CANDIDATE, CHINESE_CANDIDATE, JAPANESE_CANDIDATE, HINDI_CANDIDATE, BHOJPURI_INDIA_CANDIDATE])
    upsert("population_observations_master.csv", "observation_id", [INDONESIAN_OBSERVATION, CHINESE_OBSERVATION, JAPANESE_OBSERVATION, HINDI_OBSERVATION])
    upsert("population_source_register_master.csv", "source_id", [INDONESIAN_SOURCE, CHINESE_SOURCE, JAPANESE_SOURCE])
    print("registered=NAT-121,NAT-122,NAT-123,NAT-124,NAT-125 observations=POP-ID-018,POP-CN-001,POP-JP-001,POP-IN-COMP-006,POP-IN-023 sources=PM-S021,PM-S022,PM-S023,PM-S001")


if __name__ == "__main__":
    main()
