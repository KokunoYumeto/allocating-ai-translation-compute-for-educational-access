#!/usr/bin/env python3
"""Integrate verified Thai and Taiwan official language-use evidence.

The source constructs remain literal: Thailand usual languages spoken at home;
Taiwan current primary-or-secondary communication language among resident
nationals aged six or older.  None is relabelled as mother tongue, literacy,
academic comfort, or the number needing a particular resource.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "structured/ASIA_EMPIRICAL_NEED_INPUTS.csv"
SOURCES = ROOT / "structured/ASIA_EMPIRICAL_NEED_SOURCES.csv"
THAI_PDF = ROOT / "sources/asia_primary_20260904/Thailand_2010_Census_Final_National.pdf"
TAIWAN_XLSX = ROOT / "sources/asia_primary_20260904/Taiwan_2020_Census_Language_Use_Table6.xlsx"
QA = ROOT / "qa/ASIA_PRIMARY_LANGUAGE_EVIDENCE_INTEGRATION_20260904.json"


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="raise", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def identity(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def merged_tokens(existing: str, additions: list[str]) -> str:
    values: list[str] = []
    for value in [*(existing or "").split(";"), *additions]:
        value = value.strip()
        if value and value not in values:
            values.append(value)
    return ";".join(values)


input_fields, input_rows = read_csv(INPUTS)
source_fields, source_rows = read_csv(SOURCES)
by_stratum = {row["stratum_id"]: row for row in input_rows}
by_source = {row["source_id"]: row for row in source_rows}

thai_source_id = "ASIA_THA_NSO_CENSUS_2010_LANG"
taiwan_source_id = "ASIA_TWN_DGBAS_CENSUS_2020_LANG"

source_upserts = [
    {
        "source_id": thai_source_id,
        "title": "The 2010 Population and Housing Census: Whole Kingdom",
        "organization": "National Statistical Office of Thailand",
        "year": "2012 (2010 census reference date)",
        "url": "https://catalogapi.nso.go.th/api/doc/department/D10/SD10_04/SD10_04_165_2.pdf",
        "access_date": "2026-09-04",
        "source_type": "primary official census final report",
        "locator": "Table 7, PDF page 97: Population by usual languages spoken at home, sex and area",
        "claim_scope": "Whole-Kingdom population classified as Thai only, Thai and other languages, or only other languages spoken at home",
        "territory_or_scope": "Thailand",
        "notes": f"Local source witness {THAI_PDF.name}; SHA-256 {sha256(THAI_PDF)}. Table values are population counts under a household usual-language construct, not individual mother tongue, literacy, or academic proficiency.",
    },
    {
        "source_id": taiwan_source_id,
        "title": "2020 Population and Housing Census, Table 6: Language Usage for the Resident Nationals Aged 6 Years and Over",
        "organization": "Directorate-General of Budget, Accounting and Statistics, Taiwan",
        "year": "2020",
        "url": "https://ws.dgbas.gov.tw/001/Upload/463/relfile/11065/230300/t006.xlsx",
        "access_date": "2026-09-04",
        "source_type": "primary official census statistical table",
        "locator": "Table 6, Grand Total row: denominator 21,784,369; primary and secondary use columns",
        "claim_scope": "Current primary and secondary communication-language estimates for resident nationals aged 6+",
        "territory_or_scope": "Taiwan including Penghu, Kinmen and Lienchiang under the census scope",
        "notes": f"Local source witness {TAIWAN_XLSX.name}; SHA-256 {sha256(TAIWAN_XLSX)}. Detailed characteristics are census estimates; the table excludes resident non-nationals and children under six and does not measure proficiency, literacy, or need.",
    },
]
for row in source_upserts:
    by_source[row["source_id"]] = {field: str(row.get(field, "")) for field in source_fields}

# Replace the registration-context Thai denominator with the direct census
# population construct; all previously gathered education/access context stays.
thai = by_stratum["th-Thai-TH"]
thai.update(
    {
        "population_unit": "persons classified by usual languages spoken at home",
        "population_low_persons": "64080191",
        "population_base_persons": "64080191",
        "population_high_persons": "64080191",
        "population_measure_class": "census_language_used_at_home",
        "population_definition": "2010 census population classified as using only Thai at home (59,866,190) or Thai and another language at home (4,214,001); the two published categories sum to 64,080,191.",
        "population_reference_year": "2010-09-01",
        "population_secondary_context": "The complete census population was 65,981,659. The Thai-included categories are mutually exclusive within Table 7; only-other-language was 1,901,468.",
        "source_ids": merged_tokens(thai.get("source_ids", ""), [thai_source_id]),
        "source_urls": merged_tokens(thai.get("source_urls", ""), [source_upserts[0]["url"]]),
        "source_locators": "THA_NSO_2010 Table 7, PDF page 97: only Thai 59,866,190; Thai and other languages 4,214,001; only other languages 1,901,468. " + thai.get("source_locators", ""),
        "uncertainty_incompatibilities": "The census construct classifies population by usual languages spoken at home. It is not individual mother tongue, Thai literacy, tested proficiency, academic comfort, or a count needing every educational resource. " + thai.get("uncertainty_incompatibilities", ""),
        "evidence_confidence": "high for the official whole-population Table 7 counts; low for Thai literacy, academic comfort, and stage-subject resource need",
    }
)

taiwan_common = {
    "territory": "Taiwan; resident nationals aged 6+ census universe",
    "population_unit": "persons reporting the language as current primary or secondary communication language",
    "population_reference_year": "2020-11-08",
    "population_measure_class": "census_current_language_use_primary_or_secondary",
    "population_secondary_context": "Table 6 universe 21,784,369 resident nationals aged 6+. The language table excludes 919,419 non-national residents and 1,126,109 resident-national children under six.",
    "learning_completion_evidence": "No learning or completion outcome is multiplied into this language-use measure.",
    "functional_resource_access": "Current language use is not evidence of complete open, accessible, offline, or stage-complete educational supply.",
    "open_adaptable_scarcity": "Unknown at exact stage, subject, licence, accessibility and offline endpoints; written Standard Chinese supply is not automatically credited to every spoken-language function.",
    "academic_lingua_franca_nonoverlap": "Unmeasured. Current use does not establish academic literacy in this language, Standard Written Chinese, or English.",
    "device_connectivity_electricity": "No territory-wide device or connectivity rate is transformed into a language-person measure.",
    "accessible_offline_delivery_evidence": "Accessible text, captioned/audio, sign-language and offline modes remain separate interventions.",
    "source_ids": taiwan_source_id,
    "source_urls": source_upserts[1]["url"],
    "source_locators": "DGBAS Table 6 Grand Total row; primary-use and secondary-use columns; primary-or-secondary values are transparent sums within each named language.",
    "uncertainty_incompatibilities": "Primary and secondary language categories overlap across languages and must not be summed. The estimates are current communication use, not mother tongue, proficiency, literacy, ethnicity, or educational need.",
    "evidence_confidence": "high for the official census-estimate construct; low for academic comfort and specific unmet resource need",
}

new_rows = [
    {
        **taiwan_common,
        "stratum_id": "cmn-Hant-TW",
        "label": "Taiwan Mandarin (Guoyu) — current primary or secondary use",
        "aliases": "Guoyu; Mandarin in Taiwan",
        "script_or_mode": "spoken Mandarin communication; written Traditional Chinese is a separate access construct",
        "population_low_persons": "21090192",
        "population_base_persons": "21090192",
        "population_high_persons": "21090192",
        "population_definition": "DGBAS 2020 estimate: 14,463,896 current primary-use plus 6,626,296 current secondary-use Mandarin among resident nationals aged 6+.",
        "education_language_exposure_mismatch_by_stage": "Mandarin primary-or-secondary use was 96.8% in this restricted universe; this does not establish literacy in Traditional Chinese or access for excluded migrants and under-six children.",
    },
    {
        **taiwan_common,
        "stratum_id": "nan-Hant-TW",
        "label": "Taiwanese Taigi / Southern Min — current primary or secondary use",
        "aliases": "Taiwanese; Taigi; Southern Min in Taiwan; DGBAS 閩南語 category",
        "script_or_mode": "spoken Taigi; Traditional Han and standardized romanization delivery arms must be separately audited",
        "population_low_persons": "18728839",
        "population_base_persons": "18728839",
        "population_high_persons": "18728839",
        "population_definition": "DGBAS 2020 estimate: 6,897,535 current primary-use plus 11,831,304 current secondary-use Taiwanese among resident nationals aged 6+.",
        "education_language_exposure_mismatch_by_stage": "Current primary-or-secondary use was 86.0%, but workplace/school dominance and intergenerational transmission require separate evidence; written Standard Chinese is not a spoken-Taigi substitute.",
    },
    {
        **taiwan_common,
        "stratum_id": "hak-Hant-TW",
        "label": "Taiwan Hakka — current primary or secondary use",
        "aliases": "Hakka in Taiwan; DGBAS 客語 category",
        "script_or_mode": "spoken Hakka; Traditional Han and Hakka romanization delivery arms; internal varieties remain explicit",
        "population_low_persons": "1193332",
        "population_base_persons": "1193332",
        "population_high_persons": "1193332",
        "population_definition": "DGBAS 2020 estimate: 329,462 current primary-use plus 863,870 current secondary-use Hakka among resident nationals aged 6+.",
        "education_language_exposure_mismatch_by_stage": "Current primary-or-secondary use was 5.5%; this is distinct from Hakka identity, self-rated ability, childhood acquisition and school-language use.",
    },
]
for row in new_rows:
    normalized = {field: str(row.get(field, "")) for field in input_fields}
    by_stratum[row["stratum_id"]] = normalized

final_inputs = [by_stratum[key] for key in sorted(by_stratum)]
final_sources = [by_source[key] for key in sorted(by_source)]
write_csv(INPUTS, input_fields, final_inputs)
write_csv(SOURCES, source_fields, final_sources)

# Re-read to prove shape and exact values.
_, check_inputs = read_csv(INPUTS)
_, check_sources = read_csv(SOURCES)
check_by_stratum = {row["stratum_id"]: row for row in check_inputs}
required_values = {
    "th-Thai-TH": "64080191",
    "cmn-Hant-TW": "21090192",
    "nan-Hant-TW": "18728839",
    "hak-Hant-TW": "1193332",
}
checks = {
    "input_ids_unique": len(check_by_stratum) == len(check_inputs),
    "source_ids_unique": len({row["source_id"] for row in check_sources}) == len(check_sources),
    "required_source_ids_present": {sid: sid in {row["source_id"] for row in check_sources} for sid in (thai_source_id, taiwan_source_id)},
    "required_population_points_exact": {
        sid: check_by_stratum.get(sid, {}).get("population_base_persons") == value
        for sid, value in required_values.items()
    },
    "thai_component_sum": 59866190 + 4214001 == 64080191,
    "taiwan_component_sums": {
        "Mandarin": 14463896 + 6626296 == 21090192,
        "Taiwanese": 6897535 + 11831304 == 18728839,
        "Hakka": 329462 + 863870 == 1193332,
    },
}
status = "PASS" if all(
    [checks["input_ids_unique"], checks["source_ids_unique"], checks["thai_component_sum"], *checks["required_source_ids_present"].values(), *checks["required_population_points_exact"].values(), *checks["taiwan_component_sums"].values()]
) else "FAIL"
receipt = {
    "schema": "interlanguage/asia-primary-language-evidence-integration/1.0.0",
    "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "status": status,
    "authority_note": "Exact official language-use constructs only; no row is relabelled as literacy, proficiency, academic comfort, or unmet need.",
    "source_witnesses": [identity(THAI_PDF), identity(TAIWAN_XLSX)],
    "outputs": [identity(INPUTS), identity(SOURCES)],
    "checks": checks,
}
QA.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(receipt, ensure_ascii=False, indent=2))
