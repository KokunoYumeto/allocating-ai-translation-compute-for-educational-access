#!/usr/bin/env python3
"""Build non-additive named-sign and accessibility commissioning lanes.

These lanes are deliberately coequal with, but not merged into, the
person-language ranking.  A census count of users of a named sign language can
describe one exact stratum; it is not interchangeable with hearing loss, a
disability total, or a count of people using another sign language.  Likewise,
an accessibility standard or delivery mode is an overlapping service
obligation rather than a population that can be added to language counts.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


BASE = Path(__file__).resolve().parents[1]
SIGNED_INPUT = BASE / "structured/SIGNED_ACCESSIBILITY_EMPIRICAL_INPUTS.csv"
ACCESS_INPUT = BASE / "structured/accessibility_candidates.csv"
AUTHORITY = BASE / "structured/SUCCESSOR_EDITION_TARGET_AUTHORITY_v3.csv"

SIGN_OUT = BASE / "structured/NAMED_SIGN_LANGUAGE_EVIDENCE_v1.csv"
ACCESS_OUT = BASE / "structured/ACCESSIBILITY_MODE_COMMISSIONING_v1.csv"
CONTEXT_OUT = BASE / "structured/ACCESSIBILITY_EVIDENCE_CONTEXT_v1.csv"
COMBINED_OUT = BASE / "structured/STRUCTURAL_ACCESS_COMMISSIONING_REGISTER_v1.csv"
QA_OUT = BASE / "qa/STRUCTURAL_ACCESS_LANES_V1_QA.json"


SIGN_FIELDS = [
    "record_id", "edition_target_id", "authority_binding_status",
    "language_or_intervention", "language_tag", "jurisdiction",
    "reference_year", "measure_label", "measure_status", "context_value",
    "context_unit", "allocation_denominator_low_persons",
    "allocation_denominator_base_persons",
    "allocation_denominator_high_persons", "allocation_denominator_use",
    "evidence_role", "directness", "language_specificity", "source_tier",
    "source_publisher", "source_title", "publication_date", "source_url",
    "source_locator", "commissioning_lane", "rank_use", "additivity_class",
    "overlap_group", "double_count_rule", "recommended_use", "status",
    "limitations", "row_sha256",
]

ACCESS_FIELDS = [
    "candidate_id", "target_label", "language_variety", "language_tag",
    "script_orthography", "territory_community", "modality",
    "learner_stage_scope", "commissioning_band", "allocation_denominator_use",
    "allocation_denominator_low_persons",
    "allocation_denominator_base_persons",
    "allocation_denominator_high_persons", "context_value_low",
    "context_value_base", "context_value_high", "context_unit",
    "context_definition", "context_reference_year", "context_source_id",
    "context_source_url", "overlap_definition", "baseline_access_status",
    "evidence_confidence", "rank_use", "notes", "row_sha256",
]

CONTEXT_FIELDS = [
    "record_id", "intervention_or_language", "jurisdiction",
    "reference_year", "evidence_role", "measure_label", "context_value",
    "context_qualifier", "context_unit", "population_universe", "age_scope",
    "measure_definition", "directness", "source_tier", "source_publisher",
    "source_title", "publication_date", "source_url", "source_locator",
    "applicable_interventions", "allocation_denominator_use",
    "double_count_rule", "status", "limitations", "row_sha256",
]

COMBINED_FIELDS = [
    "structural_id", "structural_lane", "target_or_intervention",
    "edition_target_id", "language_tag", "territory_or_community",
    "evidence_status", "commissioning_band", "source_record_id",
    "source_url", "allocation_denominator_base_persons", "context_value",
    "context_unit", "rank_use", "nonadditivity_rule", "row_sha256",
]


SIGN_TARGETS = {
    "SL-ASL-US-GAP": ("edition-target:lang:ase-US", "ase-US"),
    "SL-ASL-CA-2021-KNOW": ("edition-target:lang:ase-CA", "ase-CA"),
    "SL-BSL-ENG-2021-MAIN": ("edition-target:lang:bfi-GB", "bfi-GB"),
    "SL-BSL-WLS-2021-MAIN": ("edition-target:lang:bfi-GB", "bfi-GB"),
    "SL-BSL-SCT-2022-CANUSE": ("edition-target:lang:bfi-GB", "bfi-GB"),
    "SL-BSL-NIR-2021-MAIN": ("edition-target:lang:bfi-GB", "bfi-GB"),
    "SL-LIBRAS-BR-2019-KNOW": ("edition-target:lang:bzs-BR", "bzs-BR"),
    "SL-LSF-FR-1998-99-USE": ("edition-target:lang:fsl-FR", "fsl-FR"),
    "SL-DGS-DE-2007-INTERP-PROXY": ("edition-target:lang:gsg-DE", "gsg-DE"),
    "SL-JSL-JP-2006-SIGNMEDIATED": ("edition-target:lang:jsl-JP", "jsl-JP"),
    "SL-CSL-CN-2025-HEARING-PROXY": ("edition-target:lang:csl-CN", "csl-CN"),
    "SL-ISLINDIA-IN-2011-HEARING-PROXY": ("edition-target:lang:ins-IN", "ins-IN"),
    "SL-AUSLAN-AU-2021-HOME": ("edition-target:lang:asf-AU", "asf-AU"),
    "SL-NZSL-NZ-2023-CANUSE": ("edition-target:lang:nzs-NZ", "nzs-NZ"),
    # The current authority does not yet contain an LSQ target.  Keep the
    # exact identity visible without pretending it maps to ASL or LSF.
    "SL-LSQ-CA-2021-KNOW": ("", "fcs-CA"),
    "SL-IRSL-IE-2011-HOME": ("edition-target:lang:isg-IE", "isg-IE"),
    # Spain's source does not distinguish Spanish and Catalan sign languages.
    "SL-SPAIN-SIGN-2020-USE": ("", "und-sign-ES"),
}

BASELINE_ACCESS_IDS = {
    "A11Y_SEMANTIC_RESPONSIVE_HTML",
    "A11Y_REFLOWABLE_EPUB33",
    "A11Y_NATIVE_MATHML",
    "A11Y_TEXT_IMAGE_DESCRIPTIONS",
    "A11Y_OFFLINE_DOWNLOAD_PACKAGE",
    "A11Y_LOW_BITRATE_MEDIA_VARIANT",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(row: dict[str, Any]) -> str:
    payload = {k: "" if v is None else str(v) for k, v in row.items() if k != "row_sha256"}
    data = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    material = []
    for source in rows:
        row = {field: source.get(field, "") for field in fields}
        row["row_sha256"] = canonical_hash(row)
        material.append(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(material)
    tmp.replace(path)


def value_is_person_count(row: dict[str, str]) -> bool:
    try:
        float(row.get("value", ""))
    except (TypeError, ValueError):
        return False
    return row.get("unit", "").strip() == "persons"


def sign_status(row: dict[str, str]) -> str:
    valid = row.get("valid_sign_language_user_count", "").strip().lower()
    if valid == "yes" and value_is_person_count(row):
        return "DIRECT_NAMED_SIGN_LANGUAGE_PERSON_MEASURE"
    if valid == "qualified":
        return "QUALIFIED_OR_UNDIFFERENTIATED_SIGN_MEASURE"
    if row.get("value", "").strip():
        return "PROXY_NOT_A_SIGN_LANGUAGE_USER_COUNT"
    return "MEASUREMENT_GAP_NO_PERSON_DENOMINATOR"


def build_sign_rows(authority_ids: set[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    signed = [row for row in read_csv(SIGNED_INPUT) if row.get("domain") == "signed_language"]
    for source in signed:
        target_id, language_tag = SIGN_TARGETS[source["record_id"]]
        status = sign_status(source)
        admit_denominator = status == "DIRECT_NAMED_SIGN_LANGUAGE_PERSON_MEASURE" and target_id in authority_ids
        rows.append({
            "record_id": source["record_id"],
            "edition_target_id": target_id,
            "authority_binding_status": "EXACT_AUTHORITY_TARGET" if target_id in authority_ids else "EXACT_IDENTITY_MISSING_OR_UNRESOLVED_IN_AUTHORITY",
            "language_or_intervention": source["intervention_or_language"],
            "language_tag": language_tag,
            "jurisdiction": source["jurisdiction"],
            "reference_year": source["reference_year"],
            "measure_label": source["measure_label"],
            "measure_status": status,
            "context_value": source["value"],
            "context_unit": source["unit"],
            "allocation_denominator_low_persons": source["value"] if admit_denominator else "",
            "allocation_denominator_base_persons": source["value"] if admit_denominator else "",
            "allocation_denominator_high_persons": source["value"] if admit_denominator else "",
            "allocation_denominator_use": "EXACT_STRATUM_ONLY_NONADDITIVE" if admit_denominator else "NONE",
            "evidence_role": source["evidence_role"],
            "directness": source["directness"],
            "language_specificity": source["language_specificity"],
            "source_tier": source["source_tier"],
            "source_publisher": source["source_publisher"],
            "source_title": source["source_title"],
            "publication_date": source["publication_date"],
            "source_url": source["source_url"],
            "source_locator": source["source_locator"],
            "commissioning_lane": "NAMED_SIGN_LANGUAGE_MINIMUM_SERVICE",
            "rank_use": "SEPARATE_STRUCTURAL_LANE_NOT_IN_PERSON_LANGUAGE_TOP100",
            "additivity_class": source["additivity_class"],
            "overlap_group": source["overlap_group"],
            "double_count_rule": source["double_count_rule"],
            "recommended_use": source["recommended_use"],
            "status": source["status"],
            "limitations": source["limitations"],
        })

    # Hawai'i Sign Language is not ASL and must not disappear merely because
    # the current census/authority chain lacks a population denominator.
    rows.append({
        "record_id": "SL-HSL-US-HI-GAP",
        "edition_target_id": "",
        "authority_binding_status": "EXACT_IDENTITY_MISSING_IN_AUTHORITY",
        "language_or_intervention": "Hawaiʻi Sign Language",
        "language_tag": "hps-US-HI",
        "jurisdiction": "Hawaiʻi, United States",
        "reference_year": "2013 documentation announcement; current denominator unavailable",
        "measure_label": "Independent Indigenous sign language; no defensible current user denominator",
        "measure_status": "MEASUREMENT_GAP_NO_PERSON_DENOMINATOR",
        "context_value": "",
        "context_unit": "persons",
        "allocation_denominator_low_persons": "",
        "allocation_denominator_base_persons": "",
        "allocation_denominator_high_persons": "",
        "allocation_denominator_use": "NONE",
        "evidence_role": "named_language_identity_and_measurement_gap",
        "directness": "official_university_research_announcement",
        "language_specificity": "named_HSL_not_ASL",
        "source_tier": "primary_research_institution",
        "source_publisher": "University of Hawaiʻi at Mānoa",
        "source_title": "Research team discovers existence of Hawaiʻi Sign Language",
        "publication_date": "2013-03-01",
        "source_url": "https://manoa.hawaii.edu/news/article.php?aId=5600",
        "source_locator": "announcement body: confirmation of uniqueness and independent-language status",
        "commissioning_lane": "ENDANGERED_NAMED_SIGN_LANGUAGE_PRESTIGE_AND_DOCUMENTATION",
        "rank_use": "SEPARATE_STRUCTURAL_LANE_NOT_IN_PERSON_LANGUAGE_TOP100",
        "additivity_class": "not_additive_gap",
        "overlap_group": "HSL_ASL_HAWAII_NONINTERCHANGEABLE",
        "double_count_rule": "Do not substitute ASL, Deaf-population, or hearing-loss counts for Hawaiʻi Sign Language users.",
        "recommended_use": "Retain as an exact named commissioning and evidence-priority target; do not invent a population score.",
        "status": "data_gap",
        "limitations": "Identity evidence does not supply a current user count or educational-material demand estimate.",
    })
    return rows


def build_access_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in read_csv(ACCESS_INPUT):
        cid = source["candidate_id"]
        rows.append({
            "candidate_id": cid,
            "target_label": source["target_label"],
            "language_variety": source["language_variety"],
            "language_tag": source["language_tag"],
            "script_orthography": source["script_orthography"],
            "territory_community": source["territory_community"],
            "modality": source["modality"],
            "learner_stage_scope": source["learner_stage_scope"],
            "commissioning_band": "UNIVERSAL_OPEN_PACKAGE_BASELINE" if cid in BASELINE_ACCESS_IDS else "CONDITIONAL_PARALLEL_ACCESS_ROUTE",
            "allocation_denominator_use": "NONE_NONADDITIVE_ACCESS_OVERLAY",
            "allocation_denominator_low_persons": "",
            "allocation_denominator_base_persons": "",
            "allocation_denominator_high_persons": "",
            "context_value_low": source["population_low"],
            "context_value_base": source["population_base"],
            "context_value_high": source["population_high"],
            "context_unit": source["population_unit"],
            "context_definition": source["population_definition"],
            "context_reference_year": source["population_reference_year"],
            "context_source_id": source["population_source_id"],
            "context_source_url": source["population_source_url"],
            "overlap_definition": source["overlap_definition"],
            "baseline_access_status": source["baseline_access_status"],
            "evidence_confidence": source["evidence_confidence"],
            "rank_use": "SEPARATE_STRUCTURAL_LANE_NOT_IN_PERSON_LANGUAGE_TOP100",
            "notes": source["notes"],
        })
    return rows


def build_context_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in read_csv(SIGNED_INPUT):
        if not source.get("domain", "").startswith("accessibility_"):
            continue
        rows.append({
            "record_id": source["record_id"],
            "intervention_or_language": source["intervention_or_language"],
            "jurisdiction": source["jurisdiction"],
            "reference_year": source["reference_year"],
            "evidence_role": source["evidence_role"],
            "measure_label": source["measure_label"],
            "context_value": source["value"],
            "context_qualifier": source["value_qualifier"],
            "context_unit": source["unit"],
            "population_universe": source["population_universe"],
            "age_scope": source["age_scope"],
            "measure_definition": source["measure_definition"],
            "directness": source["directness"],
            "source_tier": source["source_tier"],
            "source_publisher": source["source_publisher"],
            "source_title": source["source_title"],
            "publication_date": source["publication_date"],
            "source_url": source["source_url"],
            "source_locator": source["source_locator"],
            "applicable_interventions": source["applicable_interventions"],
            "allocation_denominator_use": "NONE_CONTEXT_OR_SUPPLY_EVIDENCE_ONLY",
            "double_count_rule": source["double_count_rule"],
            "status": source["status"],
            "limitations": source["limitations"],
        })
    return rows


def build_combined(sign_rows: list[dict[str, Any]], access_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in sign_rows:
        rows.append({
            "structural_id": source["record_id"],
            "structural_lane": "NAMED_SIGN_LANGUAGE",
            "target_or_intervention": source["language_or_intervention"],
            "edition_target_id": source["edition_target_id"],
            "language_tag": source["language_tag"],
            "territory_or_community": source["jurisdiction"],
            "evidence_status": source["measure_status"],
            "commissioning_band": source["commissioning_lane"],
            "source_record_id": source["record_id"],
            "source_url": source["source_url"],
            "allocation_denominator_base_persons": source["allocation_denominator_base_persons"],
            "context_value": source["context_value"],
            "context_unit": source["context_unit"],
            "rank_use": source["rank_use"],
            "nonadditivity_rule": source["double_count_rule"],
        })
    for source in access_rows:
        rows.append({
            "structural_id": source["candidate_id"],
            "structural_lane": "ACCESSIBILITY_AND_DELIVERY",
            "target_or_intervention": source["target_label"],
            "edition_target_id": "",
            "language_tag": source["language_tag"],
            "territory_or_community": source["territory_community"],
            "evidence_status": source["evidence_confidence"],
            "commissioning_band": source["commissioning_band"],
            "source_record_id": source["context_source_id"],
            "source_url": source["context_source_url"],
            "allocation_denominator_base_persons": "",
            "context_value": source["context_value_base"],
            "context_unit": source["context_unit"],
            "rank_use": source["rank_use"],
            "nonadditivity_rule": source["overlap_definition"],
        })
    return rows


def main() -> None:
    authority_rows = read_csv(AUTHORITY)
    authority_ids = {row["edition_target_id"] for row in authority_rows}
    sign_rows = build_sign_rows(authority_ids)
    access_rows = build_access_rows()
    context_rows = build_context_rows()
    combined_rows = build_combined(sign_rows, access_rows)

    write_csv(SIGN_OUT, SIGN_FIELDS, sign_rows)
    write_csv(ACCESS_OUT, ACCESS_FIELDS, access_rows)
    write_csv(CONTEXT_OUT, CONTEXT_FIELDS, context_rows)
    write_csv(COMBINED_OUT, COMBINED_FIELDS, combined_rows)

    sign_persisted = read_csv(SIGN_OUT)
    access_persisted = read_csv(ACCESS_OUT)
    context_persisted = read_csv(CONTEXT_OUT)
    combined_persisted = read_csv(COMBINED_OUT)
    direct_sign = [row for row in sign_persisted if row["measure_status"] == "DIRECT_NAMED_SIGN_LANGUAGE_PERSON_MEASURE"]
    allocated_direct_sign = [row for row in direct_sign if row["allocation_denominator_base_persons"]]
    invalid_sign = [row for row in sign_persisted if row["measure_status"] != "DIRECT_NAMED_SIGN_LANGUAGE_PERSON_MEASURE"]

    assertions = {
        "sign_rows": len(sign_persisted),
        "accessibility_modes": len(access_persisted),
        "accessibility_context_rows": len(context_persisted),
        "combined_rows": len(combined_persisted),
        "direct_named_sign_person_strata": len(direct_sign),
        "direct_named_sign_strata_with_allocation_denominator": len(allocated_direct_sign),
        "direct_named_sign_strata_missing_authority_binding": len(direct_sign) - len(allocated_direct_sign),
        "all_allocated_direct_sign_strata_exactly_authority_bound": all(row["authority_binding_status"] == "EXACT_AUTHORITY_TARGET" for row in allocated_direct_sign),
        "no_invalid_sign_proxy_used_as_allocation_denominator": all(not row["allocation_denominator_base_persons"] for row in invalid_sign),
        "no_accessibility_proxy_used_as_allocation_denominator": all(not row["allocation_denominator_base_persons"] for row in access_persisted),
        "hsl_identity_gap_retained": any(row["record_id"] == "SL-HSL-US-HI-GAP" for row in sign_persisted),
        "lsq_retained_without_false_asl_or_lsf_binding": any(row["record_id"] == "SL-LSQ-CA-2021-KNOW" and not row["edition_target_id"] for row in sign_persisted),
        "spain_undifferentiated_measure_not_bound_to_one_language": any(row["record_id"] == "SL-SPAIN-SIGN-2020-USE" and not row["edition_target_id"] for row in sign_persisted),
        "row_hashes_valid": all(
            canonical_hash(row) == row["row_sha256"]
            for rows in (sign_persisted, access_persisted, context_persisted, combined_persisted)
            for row in rows
        ),
        "structural_ids_unique": len({row["structural_id"] for row in combined_persisted}) == len(combined_persisted),
    }
    required_checks = (
        assertions["all_allocated_direct_sign_strata_exactly_authority_bound"],
        assertions["no_invalid_sign_proxy_used_as_allocation_denominator"],
        assertions["no_accessibility_proxy_used_as_allocation_denominator"],
        assertions["hsl_identity_gap_retained"],
        assertions["lsq_retained_without_false_asl_or_lsf_binding"],
        assertions["spain_undifferentiated_measure_not_bound_to_one_language"],
        assertions["row_hashes_valid"],
        assertions["structural_ids_unique"],
        assertions["accessibility_context_rows"] == 18,
    )
    qa = {
        "schema": "interlanguage/structural-access-lanes/1.0.0",
        "status": "PASS" if all(required_checks) else "FAIL",
        "method": "Named sign languages and accessibility/delivery modes are coequal structural commissioning lanes. Direct named-language counts remain exact non-additive strata; hearing/disability proxies and accessibility context measures are never converted to beneficiary denominators.",
        "assertions": assertions,
        "measure_status_counts": dict(Counter(row["measure_status"] for row in sign_persisted)),
        "authority_binding_status_counts": dict(Counter(row["authority_binding_status"] for row in sign_persisted)),
        "inputs": {
            str(SIGNED_INPUT.relative_to(BASE)): {"bytes": SIGNED_INPUT.stat().st_size, "sha256": sha256_file(SIGNED_INPUT)},
            str(ACCESS_INPUT.relative_to(BASE)): {"bytes": ACCESS_INPUT.stat().st_size, "sha256": sha256_file(ACCESS_INPUT)},
            str(AUTHORITY.relative_to(BASE)): {"bytes": AUTHORITY.stat().st_size, "sha256": sha256_file(AUTHORITY)},
        },
        "outputs": {
            str(path.relative_to(BASE)): {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
            for path in (SIGN_OUT, ACCESS_OUT, CONTEXT_OUT, COMBINED_OUT)
        },
        "script": {"path": str(Path(__file__).relative_to(BASE)), "bytes": Path(__file__).stat().st_size, "sha256": sha256_file(Path(__file__))},
    }
    QA_OUT.parent.mkdir(parents=True, exist_ok=True)
    QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(qa, ensure_ascii=False, indent=2, sort_keys=True))
    if qa["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
