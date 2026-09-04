#!/usr/bin/env python3
"""Integrate a bounded set of independently verified creole census rows.

This is a deterministic successor-layer repair.  It neither scans the workspace
nor changes the frozen v2 universe.  It updates only the three named regional
tables and their two named source registries, then records exact hashes.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
AFRICA = BASE / "structured/AFRICA_EMPIRICAL_NEED_INPUTS.csv"
AMERICAS = BASE / "structured/AMERICAS_EUROPE_EMPIRICAL_NEED_INPUTS.csv"
OCEANIA = BASE / "structured/OCEANIA_CENTRAL_ASIA_EMPIRICAL_INPUTS.csv"
AFRICA_SOURCES = BASE / "structured/AFRICA_EMPIRICAL_NEED_SOURCES.csv"
AMERICAS_SOURCES = BASE / "structured/AMERICAS_EUROPE_EMPIRICAL_NEED_SOURCE_REGISTRY.csv"
RECEIPT = BASE / "qa/CREOLE_PRIMARY_EVIDENCE_INTEGRATION_20260903.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"missing header: {path}")
        return list(reader.fieldnames), [dict(row) for row in reader]


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]], *, quote_all: bool) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            lineterminator="\n",
            extrasaction="raise",
            quoting=csv.QUOTE_ALL if quote_all else csv.QUOTE_MINIMAL,
        )
        writer.writeheader()
        writer.writerows(rows)
    os.replace(tmp, path)


def upsert(rows: list[dict[str, str]], key: str, value: str, changes: dict[str, str], fields: list[str]) -> None:
    matches = [row for row in rows if row.get(key) == value]
    if len(matches) > 1:
        raise ValueError(f"duplicate {key}={value}")
    if matches:
        matches[0].update(changes)
        return
    row = {field: "" for field in fields}
    row[key] = value
    row.update(changes)
    rows.append(row)


def assert_unique(rows: list[dict[str, str]], key: str, label: str) -> None:
    values = [row.get(key, "") for row in rows]
    if len(values) != len(set(values)):
        raise ValueError(f"duplicate {key} in {label}")


def main() -> None:
    tracked = [AFRICA, AMERICAS, OCEANIA, AFRICA_SOURCES, AMERICAS_SOURCES]
    before = {str(p.relative_to(BASE)).replace("\\", "/"): {"bytes": p.stat().st_size, "sha256": sha256_file(p)} for p in tracked}

    af_fields, af_rows = read_csv(AFRICA)
    am_fields, am_rows = read_csv(AMERICAS)
    oc_fields, oc_rows = read_csv(OCEANIA)
    afs_fields, afs_rows = read_csv(AFRICA_SOURCES)
    ams_fields, ams_rows = read_csv(AMERICAS_SOURCES)

    upsert(oc_rows, "stratum_id", "mfe-Latn-MU", {
        "population_low_persons": "1002135",
        "population_base_persons": "1002135",
        "population_high_persons": "1002135",
        "population_measure_class": "census_home_language_including_combinations",
        "population_definition": "Official Table D9 aggregate for residents of the Island of Mauritius reporting Creole usually spoken at home, including combinations; Rodrigues is excluded and modeled separately.",
        "population_reference_year": "2022",
        "population_secondary_context": "Table D8 records 926,120 residents of the Island of Mauritius reporting Creole alone. The Republic-wide D9 aggregate 1,045,558 includes Rodrigues and is not added to this island-specific row.",
        "source_locators": "MUS_CENSUS_2022: Tables D8-D9, PDF pp. 158-170; Island of Mauritius D9 aggregate = 1,002,135 and Rodrigues D9 aggregate = 43,423 | MUS_PRESCHOOL_LANG: classroom findings | OER_UNESCO_2019: Definition I.1 and areas of action | WCAG_22: Conformance requirements and Success Criteria",
        "uncertainty_incompatibilities": "D9 includes combination responses and is not L1, literacy or academic ability. The D8 single-language count and D9 any-combination aggregate are non-equivalent and nonadditive.",
    }, oc_fields)

    upsert(oc_rows, "stratum_id", "crs-Latn-SC", {
        "population_low_persons": "87272",
        "population_base_persons": "87323",
        "population_high_persons": "87374",
        "population_measure_class": "derived_census_first_home_language",
        "population_definition": "Kreol Seselwa as the most widely spoken language in homes: published 85.1% applied to the enumerated 2022 census population 102,612. Endpoints preserve one-decimal share rounding.",
        "population_reference_year": "2022",
        "population_secondary_context": "The census enumerated 102,612 people; 119,878 was a separate adjusted population estimate and is not the denominator for this census-language construction.",
        "source_urls": "https://www.nbs.gov.sc/downloads/1555-seychelles-population-and-housing-census-2022;https://seychellesresearchjournal.com/wp-content/uploads/2025/07/a_birds-eye_view_of_the_sociolinguistic_landscape_of_seychelles-mats_deutschmann-seychelles_research_journal-7-2.pdf;https://www.taylorfrancis.com/chapters/oa-edit/10.4324/9781003028383-4/researching-kreol-seselwa-role-education-pursuit-educational-equity-seychelles-mats-deutschmann-justin-zelime;https://www.unesco.org/en/legal-affairs/recommendation-open-educational-resources-oer?hub=422;https://www.w3.org/TR/WCAG22/",
        "source_locators": "SYC_CENSUS_2022: enumerated census population 102,612 | SYC_HOME_LANG_STUDY: Deutschmann (2025), pp. 21-22, 85.1% home-language statement and written/spoken domain split | SYC_TRANSITION_OA: education transition discussion | OER_UNESCO_2019: Definition I.1 and areas of action | WCAG_22: Conformance requirements and Success Criteria",
        "uncertainty_incompatibilities": "Derived rounded-rate interval for most-spoken home language, not all speakers or literacy. The adjusted 119,878 population estimate belongs to a different series and is not used.",
    }, oc_fields)

    upsert(am_rows, "stratum_id", "bzj-Latn-BZ", {
        "population_unit": "persons age 4+; multiple responses permitted",
        "population_low_persons": "180792",
        "population_base_persons": "180792",
        "population_high_persons": "180792",
        "population_measure_class": "census_reported_speakers",
        "population_definition": "Statistical Institute of Belize 2022 census direct count of people age 4+ able to speak Creole; people could report more than one language.",
        "population_reference_year": "2022",
        "population_secondary_context": "The same official infographic reports 49.0% and district shares. Multiple-response ability is not an L1, exclusive identity, literacy or academic-comfort count.",
        "source_ids": "BZ_CENSUS_LANG_INFOGRAPHIC_2022;BZ_EDU_PLAN_2021_25;KREYOL_MT_2024;COMMON_VOICE_26_2026;OER_UNESCO_2019",
        "source_urls": "https://sib.org.bz/wp-content/uploads/Languages_Infographic_2022.pdf;https://edc.gov.bz/wp-content/uploads/2023/04/The-Belize-Education-Sector-Plan-2021-2025_MoECST.pdf;https://www.cs.jhu.edu/~kevinduh/t/naacl24/final_pdf/paper289.pdf;https://raw.githubusercontent.com/common-voice/cv-dataset/main/datasets/scripted-speech/cv-corpus-26.0-2026-06-12.json;https://www.unesco.org/en/legal-affairs/recommendation-open-educational-resources-oer?hub=422",
        "source_locators": "BZ_CENSUS_LANG_INFOGRAPHIC_2022: one-page official census infographic, Creole 180,792 persons and 49.0% | BZ_EDU_PLAN_2021_25: pp. 14 and 53 | KREYOL_MT_2024: pp. 2, 5-6 and Table 3 | COMMON_VOICE_26_2026: locale inventory | OER_UNESCO_2019: Definition I.1 and scope",
        "uncertainty_incompatibilities": "Multiple-response speaking ability is nonexclusive and cannot be added to other Belize language counts; it is not L1, literacy, school-medium exposure or academic comfort.",
        "evidence_confidence": "high for official direct census count and multiple-response definition; medium for policy mismatch; low for outcomes and complete open-resource/access inventory",
    }, am_fields)

    upsert(am_rows, "stratum_id", "pap-Latn-AW", {
        "population_unit": "persons",
        "population_low_persons": "69354",
        "population_base_persons": "69354",
        "population_high_persons": "69354",
        "population_measure_class": "census_language_spoken_at_home",
        "population_definition": "Aruba 2010 census direct count of people reporting Papiamento as the language most often spoken at home.",
        "population_reference_year": "2010",
        "population_secondary_context": "The earlier education source reports 2,190 primary pupils with no or little everyday Dutch in 2000; that separate historic stage cohort is contextual and is not added.",
        "source_ids": "AW_CENSUS_LANGUAGE_2010;AW_EDUCATION_2000_2003;KREYOL_MT_2024;COMMON_VOICE_26_2026;OER_UNESCO_2019;CATALOG_OTL_20260901;CATALOG_DOAB_20260901",
        "source_urls": "https://cbs.aw/wp/wp-content/uploads/2012/07/Fifth-Population-and-Housing-Census-Aruba.pdf;https://cbs.aw/wp/wp-content/uploads/2013/02/05-02-Ad_Onderwijs_op_Aruba_context_en_output.pdf;https://www.cs.jhu.edu/~kevinduh/t/naacl24/final_pdf/paper289.pdf;https://raw.githubusercontent.com/common-voice/cv-dataset/main/datasets/scripted-speech/cv-corpus-26.0-2026-06-12.json;https://www.unesco.org/en/legal-affairs/recommendation-open-educational-resources-oer?hub=422;https://open.umn.edu/opentextbooks/textbooks.json;https://directory.doabooks.org/rest/search",
        "source_locators": "AW_CENSUS_LANGUAGE_2010: Table P-D1, all ages, Papiamento total 69,354 | AW_EDUCATION_2000_2003: pp. 36-38 | KREYOL_MT_2024: Table 3 | COMMON_VOICE_26_2026: locale inventory | OER_UNESCO_2019: Definition I.1 | catalog snapshots as separately described",
        "uncertainty_incompatibilities": "Most-spoken home language is not total ability, literacy or academic comfort. Aruba's official etymological spelling is not interchangeable with Curaçao/Bonaire phonemic spelling.",
        "evidence_confidence": "high for official direct census count; high for historic cohort as separate context; low for current academic-overlap and open-resource completeness",
    }, am_fields)

    upsert(am_rows, "stratum_id", "pap-Latn-CW", {
        "population_unit": "persons responding to the individual home-language census question",
        "population_low_persons": "114975",
        "population_base_persons": "115048",
        "population_high_persons": "115122",
        "population_measure_class": "derived_census_first_home_language",
        "population_definition": "Published 78.0% reporting Papiamentu as the most-spoken home language among 147,498 person responses; interval preserves one-decimal share rounding.",
        "population_reference_year": "2023",
        "population_secondary_context": "The source also reports 10% as second and 2% as third home language. Those rounded, nonexclusive positions are context and are not added to the first-position interval.",
        "source_locators": "CW_CENSUS_LANGUAGE_2023: 147,498 person responses; 78% most-spoken, 10% second, 2% third home language | KREYOL_MT_2024: pp. 2, 5-6 and Table 3 | COMMON_VOICE_26_2026: locale inventory | OER_UNESCO_2019: Definition I.1 | catalog snapshots as separately described",
        "uncertainty_incompatibilities": "Derived rounded-share interval is for first/most home language, not all speakers, literacy or academic comfort. Do not add second/third-position shares. Curaçao/Bonaire phonemic spelling is not Aruba's etymological spelling.",
        "evidence_confidence": "high for official response universe and published rounded share; medium for derived interval; low for academic overlap and open-resource completeness",
    }, am_fields)

    common_stp = {
        "territory": "São Tomé and Príncipe",
        "script_or_mode": "Latin orthography; exact language edition",
        "population_unit": "persons; multiple languages permitted",
        "population_measure_class": "census_reported_speakers",
        "population_reference_year": "2012",
        "population_secondary_context": "The same census table reports 170,223 of 173,015 residents speaking Portuguese. This substantial nonexclusive overlap is not proof of written or academic Portuguese comfort.",
        "education_language_exposure_mismatch_by_stage": "Portuguese dominates formal schooling; the census language counts do not identify school-medium exposure or subject-level comprehension for the creole-language cohorts.",
        "learning_completion_evidence": "No exact language-by-learning endpoint is inferred from the census language table.",
        "functional_resource_access": "Exact open educational coverage by language, stage and subject remains unverified.",
        "open_adaptable_scarcity": "No complete open-license curriculum ladder was verified for this exact language.",
        "academic_lingua_franca_nonoverlap": "Portuguese-speaking overlap is high and nonexclusive, but academic reading comfort is unmeasured.",
        "device_connectivity_electricity": "No exact language-access cross-tab was verified.",
        "accessible_offline_delivery_evidence": "Offline semantic text, print, audio and accessibility layers remain commissioning requirements, not measured reach.",
        "source_ids": "STP_RGPH2012_LANG",
        "source_urls": "https://www.ine.st/phocadownload/userupload/Documentos/Recenseamentos/2012/Dados%20Distritais%20e%20Nacional%20Recenseamento%202012/Resultados%20Nacionais%20do%20IV%20RGPH%202012.pdf",
        "source_locators": "STP_RGPH2012_LANG: Quadro 10, PDF p. 48, resident population by age, sex and language spoken",
        "uncertainty_incompatibilities": "Multiple-response spoken-language counts overlap Portuguese and other languages; they are not L1, literacy, exclusive identity or academic-comfort counts.",
        "evidence_confidence": "high for official direct census count; low for stage outcomes, academic overlap and open-resource/access completeness",
    }
    for sid, label, aliases, count, definition in (
        ("cri-Latn-ST", "Forro / Sãotomense", "Forro; Santome; Sãotomense", "62707", "Official 2012 census direct count of residents reporting that they speak Forro."),
        ("aoa-Latn-ST", "Angolar", "Ngola; Angolar Creole", "11377", "Official 2012 census direct count of residents reporting that they speak Angolar."),
        ("pre-Latn-ST", "Lung'Ie / Principense", "Lung'Ie; Lunguié; Principense", "1753", "Official 2012 census direct count of residents reporting that they speak Lung'Ie."),
    ):
        changes = dict(common_stp)
        changes.update({
            "label": label,
            "aliases": aliases,
            "population_low_persons": count,
            "population_base_persons": count,
            "population_high_persons": count,
            "population_definition": definition,
        })
        upsert(af_rows, "stratum_id", sid, changes, af_fields)

    upsert(af_rows, "stratum_id", "pov-Latn-GW", {
        "label": "Guinea-Bissau Kriol",
        "aliases": "Kriol; Crioulo da Guiné-Bissau",
        "territory": "Guinea-Bissau",
        "script_or_mode": "Latin orthography; national bridge-language edition",
        "population_unit": "Guinea-Bissau nationals; multiple languages permitted",
        "population_low_persons": "1303743",
        "population_base_persons": "1303743",
        "population_high_persons": "1303743",
        "population_measure_class": "census_reported_speakers",
        "population_definition": "Official RGPH 2009 Table 6 direct count of Guinea-Bissau nationals reporting that they speak Kriol; multiple language responses were permitted.",
        "population_reference_year": "2009",
        "population_secondary_context": "1,303,743 of 1,442,227 nationals; published share 90.4%. Portuguese was reported by 390,727 (27.1%).",
        "education_language_exposure_mismatch_by_stage": "Kriol is the national communication bridge, while Portuguese reach is much lower; the census reports rural Portuguese use at 14.7% versus rural Kriol use at 89.8%.",
        "learning_completion_evidence": "The same report states 51.9% of nationals age 6+ were literate and 43.7% had never attended school; these are national/ethnicity-context figures, not Kriol-specific learning effects.",
        "functional_resource_access": "National bridge reach is direct; a complete open curriculum inventory by stage and subject remains unverified.",
        "open_adaptable_scarcity": "No complete open-license school-to-tertiary ladder was verified for Kriol.",
        "academic_lingua_franca_nonoverlap": "Portuguese-speaking overlap is directly counted but conversational ability is not academic proficiency; the measures are nonexclusive.",
        "device_connectivity_electricity": "No exact language-access cross-tab was verified.",
        "accessible_offline_delivery_evidence": "Offline, low-bandwidth semantic text and printable teacher/self-study materials are indicated by the school-access context but reach is not quantified here.",
        "source_ids": "GNB_RGPH2009_LANG",
        "source_urls": "https://stat-guinebissau.com/Menu_principal/IV_RGPH/rgph1/caracteristicas_socio_cultural.pdf",
        "source_locators": "GNB_RGPH2009_LANG: Resumo pp. 9-10; section 3.6 pp. 36-43; Quadro 6 p. 38 (Kriol 1,303,743; Portuguese 390,727); rural comparison pp. 42-43",
        "uncertainty_incompatibilities": "Multiple-response speaking counts overlap and are not L1, literacy or academic-comfort counts. The report notes census undercount/weighting limitations; published direct counts are retained without projecting them to 2026.",
        "evidence_confidence": "high for official direct census count and language overlap; medium for national education context; low for current open-resource and access completeness",
    }, af_fields)

    upsert(afs_rows, "source_id", "GNB_RGPH2009_LANG", {
        "title": "Características socioculturais: Terceiro Recenseamento Geral da População e Habitação 2009",
        "organization": "Instituto Nacional de Estatística, Guinea-Bissau",
        "year": "2009",
        "url": "https://stat-guinebissau.com/Menu_principal/IV_RGPH/rgph1/caracteristicas_socio_cultural.pdf",
        "access_date": "2026-09-03",
        "source_type": "official census report",
        "locator": "Resumo pp. 9-10; section 3.6 pp. 36-43; Quadro 6 p. 38",
        "claim_scope": "Direct multiple-response counts for languages spoken by Guinea-Bissau nationals, including Kriol and Portuguese; national literacy/attendance context.",
        "territory_or_scope": "Guinea-Bissau nationals enumerated in RGPH 2009",
        "notes": "Counts are nonexclusive; report describes post-enumeration undercount and weighting limitations. No projection to a later year is made.",
    }, afs_fields)
    upsert(afs_rows, "source_id", "STP_RGPH2012_LANG", {
        "title": "Resultados Nacionais do IV Recenseamento Geral da População e da Habitação 2012",
        "organization": "Instituto Nacional de Estatística de São Tomé e Príncipe",
        "year": "2013",
        "url": "https://www.ine.st/phocadownload/userupload/Documentos/Recenseamentos/2012/Dados%20Distritais%20e%20Nacional%20Recenseamento%202012/Resultados%20Nacionais%20do%20IV%20RGPH%202012.pdf",
        "access_date": "2026-09-03",
        "source_type": "official census report",
        "locator": "Quadro 10, PDF p. 48",
        "claim_scope": "Direct multiple-response resident counts for Portuguese, Forro, Angolar and Lung'Ie.",
        "territory_or_scope": "São Tomé and Príncipe residents",
        "notes": "Spoken-language responses overlap; not L1, literacy or exclusive identity.",
    }, afs_fields)
    upsert(ams_rows, "source_id", "BZ_CENSUS_LANG_INFOGRAPHIC_2022", {
        "publisher": "Statistical Institute of Belize",
        "title": "Languages Spoken in Belize According to the 2022 Census",
        "reference_year": "2022",
        "source_type": "official census infographic",
        "territory_or_scope": "Belize, people age 4+; multiple-response spoken languages",
        "url": "https://sib.org.bz/wp-content/uploads/Languages_Infographic_2022.pdf",
        "locator": "one-page infographic: Creole 180,792 persons, 49.0%",
        "construct_and_limits": "Direct count of people able to speak Creole; multiple languages permitted; not L1, literacy or academic comfort.",
        "accessed_date": "2026-09-03",
    }, ams_fields)
    upsert(ams_rows, "source_id", "AW_CENSUS_LANGUAGE_2010", {
        "publisher": "Central Bureau of Statistics Aruba",
        "title": "Fifth Population and Housing Census Aruba: Selected Tables",
        "reference_year": "2010",
        "source_type": "official census report",
        "territory_or_scope": "Aruba residents",
        "url": "https://cbs.aw/wp/wp-content/uploads/2012/07/Fifth-Population-and-Housing-Census-Aruba.pdf",
        "locator": "Table P-D1: population by language most spoken in the household, all ages",
        "construct_and_limits": "Direct person count for most-spoken home language; not total speaking ability, literacy or academic comfort.",
        "accessed_date": "2026-09-03",
    }, ams_fields)

    for rows, key, label in ((af_rows, "stratum_id", "Africa inputs"), (am_rows, "stratum_id", "Americas inputs"), (oc_rows, "stratum_id", "Oceania inputs"), (afs_rows, "source_id", "Africa sources"), (ams_rows, "source_id", "Americas sources")):
        assert_unique(rows, key, label)

    af_rows.sort(key=lambda row: row["stratum_id"])
    am_rows.sort(key=lambda row: row["stratum_id"])
    oc_rows.sort(key=lambda row: row["stratum_id"])
    afs_rows.sort(key=lambda row: row["source_id"])
    ams_rows.sort(key=lambda row: row["source_id"])
    write_csv(AFRICA, af_fields, af_rows, quote_all=False)
    write_csv(AMERICAS, am_fields, am_rows, quote_all=True)
    write_csv(OCEANIA, oc_fields, oc_rows, quote_all=True)
    write_csv(AFRICA_SOURCES, afs_fields, afs_rows, quote_all=False)
    write_csv(AMERICAS_SOURCES, ams_fields, ams_rows, quote_all=True)

    expected = {
        (AFRICA, "pov-Latn-GW"): "1303743",
        (AFRICA, "cri-Latn-ST"): "62707",
        (AFRICA, "aoa-Latn-ST"): "11377",
        (AFRICA, "pre-Latn-ST"): "1753",
        (AMERICAS, "bzj-Latn-BZ"): "180792",
        (AMERICAS, "pap-Latn-AW"): "69354",
        (AMERICAS, "pap-Latn-CW"): "115048",
        (OCEANIA, "mfe-Latn-MU"): "1002135",
        (OCEANIA, "crs-Latn-SC"): "87323",
    }
    checks: dict[str, bool] = {}
    for (path, sid), base in expected.items():
        _, rows = read_csv(path)
        row = next(row for row in rows if row["stratum_id"] == sid)
        checks[f"{path.stem}:{sid}:base"] = row["population_base_persons"] == base

    local_sources = [
        BASE / "sources/creole_primary_20260903/Mauritius_HPC_TR_Vol2_Demography_Yr22.pdf",
        BASE / "sources/creole_primary_20260903/Aruba_Fifth_Population_Housing_Census.pdf",
        BASE / "sources/creole_primary_20260903/Guinea_Bissau_RGPH2009_sociocultural.pdf",
        BASE / "sources/creole_primary_20260903/STP_RGPH2012_national.pdf",
    ]
    for path in local_sources:
        checks[f"source_pdf:{path.name}"] = path.exists() and path.read_bytes()[:5] == b"%PDF-"

    after = {str(p.relative_to(BASE)).replace("\\", "/"): {"bytes": p.stat().st_size, "sha256": sha256_file(p)} for p in tracked}
    receipt = {
        "schema": "interlanguage/creole-primary-evidence-integration/1.0.0",
        "generated_date": "2026-09-03",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "scope": "bounded census corrections/additions for Guinea-Bissau, São Tomé and Príncipe, Belize, Aruba, Curaçao, Mauritius and Seychelles",
        "before": before,
        "after": after,
        "source_snapshots": {
            str(path.relative_to(BASE)).replace("\\", "/"): {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
            for path in local_sources
        },
        "checks": checks,
        "nonadditivity": "Every count retains its source universe. Multiple-response, home-language, first-home-language and territorial constructs are never summed without a proved disjoint crosswalk.",
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2))
    if receipt["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
