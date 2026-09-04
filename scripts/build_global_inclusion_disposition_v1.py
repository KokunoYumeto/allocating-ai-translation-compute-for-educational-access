#!/usr/bin/env python3
"""Build the publication-facing global inclusion, disposition, and safety tables.

This builder does not score new populations.  It makes the full target universe,
large/context strata, structural-access lanes, displacement portfolios, bridge
experiments, aliases, and explicit sentinel gaps visible in one deterministic
register.  Missing population evidence remains null.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
STRUCTURED = ROOT / "structured"
REPORTS = ROOT / "agent_reports"
QA = ROOT / "qa"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def file_identity(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest().upper(),
    }


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def truthy(value: Any) -> bool:
    return clean(value).lower() in {"1", "true", "yes", "y"}


def join_nonempty(values: Iterable[str], sep: str = ";") -> str:
    seen: set[str] = set()
    result: list[str] = []
    for raw in values:
        for value in clean(raw).split(sep):
            item = value.strip()
            if item and item not in seen:
                seen.add(item)
                result.append(item)
    return sep.join(result)


def row_digest(row: dict[str, Any], hash_field: str = "row_sha256") -> str:
    body = {k: clean(v) for k, v in row.items() if k != hash_field}
    encoded = json.dumps(
        body, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: clean(row.get(field, "")) for field in fields})


def split_tags(value: str) -> set[str]:
    tags: set[str] = set()
    for part in clean(value).replace("|", ";").split(";"):
        part = part.strip()
        if part:
            tags.add(part)
    return tags


AUTHORITY_PATH = STRUCTURED / "SUCCESSOR_EDITION_TARGET_AUTHORITY_v3.csv"
ALIAS_PATH = STRUCTURED / "SUCCESSOR_EDITION_ALIAS_LEDGER_v3.csv"
SCORE_PATH = STRUCTURED / "GLOBAL_TARGET_SCORE_TABLE_v3.csv"
TOP100_PATH = STRUCTURED / "TOP100_NEEDS_ONLY_v3.csv"
AUTHZ_PATH = STRUCTURED / "EVIDENCE_AUTHORIZATION_v1.csv"
SUPPLEMENT_PATH = STRUCTURED / "LARGE_POPULATION_OMISSION_SUPPLEMENT_v1.csv"
STRUCTURAL_PATH = STRUCTURED / "STRUCTURAL_ACCESS_COMMISSIONING_REGISTER_v1.csv"
OMISSION_PATH = STRUCTURED / "global_omission_candidates.csv"
AMERICAS_INPUT_PATH = STRUCTURED / "AMERICAS_EUROPE_EMPIRICAL_NEED_INPUTS.csv"
INTERLANGUAGE_PATH = REPORTS / "INTERLANGUAGE_STRUCTURED_EVIDENCE_MATRIX.csv"
SENTINEL_PATH = STRUCTURED / "GLOBAL_INCLUSION_SENTINEL_SPEC_v1.csv"

INCLUSION_OUT = STRUCTURED / "GLOBAL_INCLUSION_DISPOSITION_REGISTER_v1.csv"
SENTINEL_OUT = STRUCTURED / "GLOBAL_INCLUSION_SENTINEL_STATUS_v1.csv"
CROSSWALK_OUT = STRUCTURED / "SOURCE_TO_SCORE_CROSSWALK_v1.csv"
PUBLIC_SCORE_OUT = STRUCTURED / "GLOBAL_TARGET_SCORE_TABLE_PUBLIC_v3.csv"
DISPLACEMENT_OUT = STRUCTURED / "DISPLACEMENT_EDUCATION_PORTFOLIO_v1.csv"
QA_OUT = QA / "GLOBAL_INCLUSION_DISPOSITION_QA_v1.json"


authority = read_csv(AUTHORITY_PATH)
aliases = read_csv(ALIAS_PATH)
scores = read_csv(SCORE_PATH)
top100 = read_csv(TOP100_PATH)
authorizations = read_csv(AUTHZ_PATH)
supplements = read_csv(SUPPLEMENT_PATH)
structural = read_csv(STRUCTURAL_PATH)
omissions = read_csv(OMISSION_PATH)
americas_inputs = read_csv(AMERICAS_INPUT_PATH)
interlanguages = read_csv(INTERLANGUAGE_PATH)
sentinels = read_csv(SENTINEL_PATH)

authority_by_id = {row["edition_target_id"]: row for row in authority}
score_by_id = {row["edition_target_id"]: row for row in scores}
top100_by_id = {row["edition_target_id"]: row for row in top100}
tags_to_authority: dict[str, list[dict[str, str]]] = defaultdict(list)
for row in authority:
    for tag in split_tags(row.get("language_tags", "")):
        tags_to_authority[tag].append(row)

alias_to_primary: dict[str, str] = {}
for row in aliases:
    alias_id = row["alias_id"]
    alias_to_primary[alias_id] = row["primary_edition_target_id"]
    if not alias_id.startswith("edition-target:"):
        alias_to_primary[f"edition-target:{alias_id}"] = row["primary_edition_target_id"]


INCLUSION_FIELDS = [
    "inclusion_id",
    "record_kind",
    "target_id",
    "canonical_target_id",
    "target_label",
    "language_or_intervention_tag",
    "script_or_mode",
    "territory_or_community",
    "decision_lane",
    "evidence_status",
    "population_low_persons",
    "population_base_persons",
    "population_high_persons",
    "population_definition",
    "population_reference_year",
    "source_ids",
    "source_urls",
    "rank_status",
    "current_direct_person_rank",
    "disposition_reason",
    "priority_action",
    "overlap_nonadditivity",
    "source_record_ids",
    "row_sha256",
]

inclusion_rows: list[dict[str, Any]] = []


def add_inclusion(row: dict[str, Any]) -> None:
    row = {field: clean(row.get(field, "")) for field in INCLUSION_FIELDS}
    row["row_sha256"] = row_digest(row)
    inclusion_rows.append(row)


# 1. Every edition authority target.  Synthetic population ceilings are never copied.
for target in authority:
    target_id = target["edition_target_id"]
    score = score_by_id.get(target_id, {})
    order_lane = clean(score.get("order_lane"))
    direct_rank = clean(score.get("l_m_need_rank"))
    direct = (
        order_lane == "person_need"
        and bool(direct_rank)
        and truthy(score.get("primary_order_eligible"))
        and not truthy(score.get("synthetic_or_model_prior"))
    )
    source_bound = bool(clean(score.get("population_source_url"))) and not truthy(
        score.get("synthetic_or_model_prior")
    )
    stage = order_lane == "stage_opportunity" and source_bound
    unresolved = "unresolved" in clean(target.get("exactness")).lower() or "UNRESOLVED" in clean(
        target.get("disposition")
    )
    is_sign = "sign" in clean(target.get("language_mode")).lower() or any(
        word in clean(target.get("language_variety_names")).lower()
        for word in ("sign language", "signed language")
    )
    if direct:
        lane = "DIRECT_PERSON_LANGUAGE"
        evidence_status = "DIRECT_PERSON_SOURCE_BOUND_RANKED"
        rank_status = "DIRECT_PERSON_RANKED"
        action = "RETAIN_AND_REFINE_STAGE_SUBJECT_AND_ACCESS_EVIDENCE"
    elif stage:
        lane = "STAGE_OPPORTUNITY"
        evidence_status = "DIRECT_STAGE_OPPORTUNITY_NOT_WHOLE_LANGUAGE_DENOMINATOR"
        rank_status = "SEPARATE_STAGE_OPPORTUNITY_RANKED"
        action = "RETAIN_AND_REFINE_STAGE_SUBJECT_AND_ACCESS_EVIDENCE"
    elif is_sign:
        lane = "NAMED_SIGN_LANGUAGE"
        evidence_status = (
            "SOURCE_BOUND_CONTEXT_NOT_RANKED" if source_bound else "NO_SOURCE_BOUND_PERSON_DENOMINATOR"
        )
        rank_status = "SEPARATE_STRUCTURAL_LANE"
        action = "MEASURE_NAMED_SIGN_LANGUAGE_USERS_AND_ACCESS_ENDPOINTS"
    else:
        lane = "LANGUAGE_CONTEXT_OR_EVIDENCE_ACQUISITION"
        evidence_status = (
            "IDENTITY_OR_SCOPE_UNRESOLVED"
            if unresolved
            else "SOURCE_BOUND_CONTEXT_NOT_RANKED"
            if source_bound
            else "NO_SOURCE_BOUND_PERSON_DENOMINATOR"
        )
        rank_status = "UNRANKED_EXPLICIT"
        action = (
            "RESOLVE_IDENTITY_BEFORE_POPULATION_BINDING"
            if unresolved
            else "ACQUIRE_SOURCE_BOUND_PERSON_DENOMINATOR_OR_DOCUMENT_NEGATIVE_CONTROL"
        )
    atom = clean(score.get("population_atom_id"))
    overlap = (
        f"Population atom {atom} may be shared by multiple edition, territory, or script arms; do not sum."
        if atom and source_bound
        else "No population may be inferred from the language name, territory, script, or model prior."
    )
    add_inclusion(
        {
            "inclusion_id": f"authority:{target_id}",
            "record_kind": "EDITION_AUTHORITY_TARGET",
            "target_id": target_id,
            "canonical_target_id": target.get("canonical_target_id"),
            "target_label": target.get("language_variety_names"),
            "language_or_intervention_tag": target.get("language_tags"),
            "script_or_mode": join_nonempty(
                [target.get("scripts_orthographies", ""), target.get("language_mode", "")]
            ),
            "territory_or_community": target.get("territories_communities"),
            "decision_lane": lane,
            "evidence_status": evidence_status,
            "population_low_persons": score.get("population_low") if source_bound else "",
            "population_base_persons": score.get("population_base") if source_bound else "",
            "population_high_persons": score.get("population_high") if source_bound else "",
            "population_definition": score.get("population_definition") if source_bound else "",
            "population_reference_year": score.get("population_reference_year") if source_bound else "",
            "source_ids": score.get("population_source_id") if source_bound else "",
            "source_urls": score.get("population_source_url") if source_bound else "",
            "rank_status": rank_status,
            "current_direct_person_rank": direct_rank if direct else "",
            "disposition_reason": clean(
                score.get("primary_order_exclusion_reason")
                or target.get("disposition")
                or evidence_status
            ),
            "priority_action": action,
            "overlap_nonadditivity": overlap,
            "source_record_ids": join_nonempty(
                [score.get("source_record_id", ""), score.get("authorization_ids", "")]
            ),
        }
    )


# 2. Every explicit alias: visibility without duplicate beneficiary credit.
for alias in aliases:
    add_inclusion(
        {
            "inclusion_id": f"alias:{alias['alias_scope']}:{alias['alias_id']}",
            "record_kind": "ALIAS_NO_SEPARATE_POPULATION_CREDIT",
            "target_id": alias["alias_id"],
            "canonical_target_id": alias["primary_canonical_target_id"],
            "target_label": alias["alias_id"],
            "language_or_intervention_tag": alias["alias_id"],
            "decision_lane": "IDENTITY_AND_DEDUPLICATION",
            "evidence_status": "ALIAS_TO_PRIMARY_TARGET",
            "rank_status": "NEVER_SEPARATELY_RANKED",
            "disposition_reason": alias["reason"],
            "priority_action": "USE_PRIMARY_TARGET_AND_PRESERVE_ALIAS_FOR_DISCOVERY",
            "overlap_nonadditivity": f"Exact alias of {alias['primary_edition_target_id']}; zero separate population credit.",
            "source_record_ids": alias.get("row_sha256", ""),
        }
    )


# 3. Large/context-only population measurements.  They are mandatory visibility
# records and never silently promoted to comfortable-reader language counts.
for item in supplements:
    add_inclusion(
        {
            "inclusion_id": f"large-context:{item['stratum_id']}",
            "record_kind": "LARGE_OR_CONTEXT_POPULATION_STRATUM",
            "target_id": item["stratum_id"],
            "target_label": item["label"],
            "language_or_intervention_tag": item["stratum_id"].split("-reported", 1)[0].split("-education", 1)[0].split("-home", 1)[0],
            "script_or_mode": item["script_or_mode"],
            "territory_or_community": item["territory"],
            "decision_lane": "MANDATORY_LARGE_CONTEXT_AND_VALUE_OF_INFORMATION",
            "evidence_status": "DIRECT_SOURCE_BOUND_CONTEXT_NOT_COMFORTABLE_READER_COUNT",
            "population_low_persons": item["population_low_persons"],
            "population_base_persons": item["population_base_persons"],
            "population_high_persons": item["population_high_persons"],
            "population_definition": item["population_definition"],
            "population_reference_year": item["population_reference_year"],
            "source_ids": item["source_ids"],
            "source_urls": item["source_urls"],
            "rank_status": "SEPARATE_CONTEXT_LANE_NOT_DIRECT_PERSON_ORDER",
            "disposition_reason": item["uncertainty_incompatibilities"],
            "priority_action": "MEASURE_STAGE_SUBJECT_COMFORT_SCARCITY_AND_NONOVERLAP",
            "overlap_nonadditivity": "This exposure, home-language, or reported-language construct must not be added to direct language populations without a proved disjoint-person crosswalk.",
            "source_record_ids": item["stratum_id"],
        }
    )


# 4. Named signed-language and accessibility/offline commissions.
for item in structural:
    has_denom = bool(clean(item.get("allocation_denominator_base_persons")))
    add_inclusion(
        {
            "inclusion_id": f"structural:{item['structural_id']}",
            "record_kind": "STRUCTURAL_ACCESS_INTERVENTION",
            "target_id": item.get("edition_target_id") or item["structural_id"],
            "target_label": item["target_or_intervention"],
            "language_or_intervention_tag": item["language_tag"],
            "script_or_mode": item["structural_lane"],
            "territory_or_community": item["territory_or_community"],
            "decision_lane": item["structural_lane"],
            "evidence_status": item["evidence_status"],
            "population_base_persons": item["allocation_denominator_base_persons"] if has_denom else "",
            "population_definition": item["context_unit"] if has_denom else "",
            "source_ids": item["source_record_id"],
            "source_urls": item["source_url"],
            "rank_status": item["rank_use"],
            "disposition_reason": item["commissioning_band"],
            "priority_action": "COMMISSION_SEPARATE_STRUCTURAL_LANE_OR_ACQUIRE_MISSING_DENOMINATOR",
            "overlap_nonadditivity": item["nonadditivity_rule"],
            "source_record_ids": item["source_record_id"],
        }
    )


# 5. Bridge/interlanguage experiments.  Production reuse and reader reach stay separate.
for item in interlanguages:
    add_inclusion(
        {
            "inclusion_id": f"bridge:{item['bridge_id']}",
            "record_kind": "BRIDGE_OR_INTERLANGUAGE_PROFILE",
            "target_id": item["bridge_id"],
            "target_label": item["bridge_name"],
            "script_or_mode": item["scripts_or_modalities"],
            "territory_or_community": item["communities_potentially_served"],
            "decision_lane": "BRIDGE_AND_INTERLANGUAGE_EXPERIMENT",
            "evidence_status": f"EVIDENCE_GRADE_{item['evidence_grade']}",
            "source_ids": item["source_ids"],
            "source_urls": item["source_urls_or_dois"],
            "rank_status": "NO_PERSON_CREDIT_WITHOUT_COMMUNITY_SCRIPT_ENDPOINT_BOUND",
            "disposition_reason": item["current_evidence_disposition"],
            "priority_action": "TEST_FUNCTIONAL_MATHEMATICS_COMPREHENSION_AND_PRODUCTION_REUSE_SEPARATELY",
            "overlap_nonadditivity": f"{item['unique_gain_rule']} {item['double_count_rule']}",
            "source_record_ids": item["bridge_id"],
        }
    )


# 6. Displacement portfolios: status populations are not language populations.
displacement_candidate_ids = {
    "glob_apc_sy_refugee",
    "glob_rhg_stateless",
    "glob_afghan_displaced",
    "glob_sudan_displaced",
    "glob_ajp_palestinian_refugee",
}
displacement_rows: list[dict[str, Any]] = []


def add_displacement(row: dict[str, Any]) -> None:
    displacement_rows.append(row)


language_arms = {
    "glob_apc_sy_refugee": "Syrian/North Levantine Arabic; Modern Standard Arabic; each host-country language",
    "glob_rhg_stateless": "Rohingya Hanifi; Rohingya Latin; Rohingya Arabic; Bangla and Myanmar host/transition interfaces",
    "glob_afghan_displaced": "Dari; Pashto; Hazaragi; Uzbek and other explicitly measured Afghan languages; each host-country language",
    "glob_sudan_displaced": "Sudanese Arabic; Dinka; Nuer; named Darfur and Nuba languages; each host-country language",
    "glob_ajp_palestinian_refugee": "Palestinian Arabic; Modern Standard Arabic; each host-country language",
}

for item in omissions:
    if item["candidate_id"] not in displacement_candidate_ids:
        continue
    add_displacement(
        {
            "portfolio_id": f"displacement:{item['candidate_id']}",
            "portfolio_label": item["target_label"],
            "origin_or_status_scope": item["territory_community"],
            "host_scope": "Multiple or unspecified hosts; must be split before country-context factors are used.",
            "population_low_persons": item["population_low"],
            "population_base_persons": item["population_base"],
            "population_high_persons": item["population_high"],
            "population_definition": item["population_definition"],
            "population_reference_year": item["population_reference_year"],
            "language_script_arms": language_arms[item["candidate_id"]],
            "education_stage_needs": "school continuity; host-language acquisition; bilingual subject bridges; credential continuity; adult and higher-education continuation",
            "delivery_needs": "offline-first resumable packages; mobile layouts; accessible formats; low-data synchronization; print fallback",
            "source_ids": item["population_source_id"],
            "source_urls": item["population_source_url"],
            "rank_use": "SEPARATE_DISPLACEMENT_PORTFOLIO_NOT_LANGUAGE_PERSON_RANK",
            "nonadditivity_rule": item["notes"],
            "evidence_status": "DIRECT_STATUS_COHORT_DENOMINATOR_LANGUAGE_DISTRIBUTION_UNRESOLVED",
        }
    )

ukraine = next(
    (
        row
        for row in americas_inputs
        if row.get("stratum_id") == "uk-Cyrl-EU-TEMP"
    ),
    None,
)
if ukraine:
    add_displacement(
        {
            "portfolio_id": "displacement:ukraine-eu-school-continuity",
            "portfolio_label": ukraine["label"],
            "origin_or_status_scope": "Displaced children from Ukraine in European Union host systems",
            "host_scope": "European Union host systems; country and modality must remain stratified.",
            "population_low_persons": ukraine["population_low_persons"],
            "population_base_persons": ukraine["population_base_persons"],
            "population_high_persons": ukraine["population_high_persons"],
            "population_definition": ukraine["population_definition"],
            "population_reference_year": ukraine["population_reference_year"],
            "language_script_arms": "Ukrainian Cyrillic continuity; Russian where directly measured; each host-country language",
            "education_stage_needs": "school continuity; host-language acquisition; dual-enrolment burden reduction; credential continuity",
            "delivery_needs": "resumable low-data and offline packages; accessible mobile formats; print fallback",
            "source_ids": ukraine["source_ids"],
            "source_urls": ukraine["source_urls"],
            "rank_use": "SEPARATE_DISPLACEMENT_PORTFOLIO_NOT_LANGUAGE_PERSON_RANK",
            "nonadditivity_rule": ukraine["uncertainty_incompatibilities"],
            "evidence_status": "DIRECT_ENROLLED_LEARNER_COHORT_LANGUAGE_DISTRIBUTION_UNRESOLVED",
        }
    )

for portfolio_id, label, arms in [
    (
        "displacement:venezuela-regional",
        "Venezuelan refugees and migrants — host-specific education portfolio",
        "Venezuelan Spanish; Brazilian Portuguese and each other host-country language; Indigenous-language arms where directly evidenced",
    ),
    (
        "displacement:south-sudan-regional",
        "South Sudanese refugees — host-specific education portfolio",
        "Juba Arabic; Dinka; Nuer; Bari and other named languages; each host-country language",
    ),
    (
        "displacement:somalia-regional",
        "Somali refugees — host-specific education portfolio",
        "Somali Latin; Arabic where directly measured; each host-country language",
    ),
    (
        "displacement:drc-regional",
        "DRC refugees and internal displacement — host-specific education portfolio",
        "French; Lingala; Kiswahili; Tshiluba; Kikongo varieties and other named languages; each host-country language",
    ),
]:
    add_displacement(
        {
            "portfolio_id": portfolio_id,
            "portfolio_label": label,
            "origin_or_status_scope": "Explicit global-inclusion sentinel; current bounded source register lacks a publication-ready cohort denominator.",
            "host_scope": "Origin, host country, school stage, and language distribution must be measured separately.",
            "population_low_persons": "",
            "population_base_persons": "",
            "population_high_persons": "",
            "population_definition": "",
            "population_reference_year": "",
            "language_script_arms": arms,
            "education_stage_needs": "school continuity; host-language acquisition; bilingual subject bridges; credential continuity; adult and higher-education continuation",
            "delivery_needs": "offline-first resumable packages; mobile layouts; accessible formats; low-data synchronization; print fallback",
            "source_ids": "",
            "source_urls": "",
            "rank_use": "SEPARATE_DISPLACEMENT_PORTFOLIO_NOT_LANGUAGE_PERSON_RANK",
            "nonadditivity_rule": "No population is assigned until a direct status-cohort source and nonoverlapping host/origin construction are registered.",
            "evidence_status": "SOURCE_DISCOVERY_REQUIRED_NO_POPULATION_ASSIGNED",
        }
    )

DISPLACEMENT_FIELDS = [
    "portfolio_id",
    "portfolio_label",
    "origin_or_status_scope",
    "host_scope",
    "population_low_persons",
    "population_base_persons",
    "population_high_persons",
    "population_definition",
    "population_reference_year",
    "language_script_arms",
    "education_stage_needs",
    "delivery_needs",
    "source_ids",
    "source_urls",
    "rank_use",
    "nonadditivity_rule",
    "evidence_status",
    "row_sha256",
]
for row in displacement_rows:
    row["row_sha256"] = row_digest(row)

for item in displacement_rows:
    add_inclusion(
        {
            "inclusion_id": item["portfolio_id"],
            "record_kind": "DISPLACEMENT_EDUCATION_PORTFOLIO",
            "target_id": item["portfolio_id"],
            "target_label": item["portfolio_label"],
            "language_or_intervention_tag": item["language_script_arms"],
            "script_or_mode": "MULTILINGUAL_HOST_SPECIFIC_PORTFOLIO",
            "territory_or_community": join_nonempty(
                [item["origin_or_status_scope"], item["host_scope"]]
            ),
            "decision_lane": "DISPLACEMENT_EDUCATION_PORTFOLIO",
            "evidence_status": item["evidence_status"],
            "population_low_persons": item["population_low_persons"],
            "population_base_persons": item["population_base_persons"],
            "population_high_persons": item["population_high_persons"],
            "population_definition": item["population_definition"],
            "population_reference_year": item["population_reference_year"],
            "source_ids": item["source_ids"],
            "source_urls": item["source_urls"],
            "rank_status": item["rank_use"],
            "disposition_reason": item["evidence_status"],
            "priority_action": "SPLIT_ORIGIN_HOST_STAGE_LANGUAGE_AND_DELIVERY_ARMS_BEFORE_ALLOCATION",
            "overlap_nonadditivity": item["nonadditivity_rule"],
            "source_record_ids": item["portfolio_id"],
        }
    )


# 7. Sentinel status: every known high-consequence population is either linked
# to an existing target/context stratum or explicitly shown as missing.
SENTINEL_FIELDS = [
    "sentinel_id",
    "target_label",
    "expected_edition_target_id",
    "expected_language_tag",
    "script_or_mode",
    "territory_or_community",
    "sentinel_class",
    "minimum_lane",
    "presence_status",
    "matched_target_ids",
    "matched_context_strata",
    "current_rank_status",
    "current_direct_person_ranks",
    "why_required",
    "preferred_evidence_action",
    "publication_disposition",
    "row_sha256",
]
sentinel_rows: list[dict[str, Any]] = []
for item in sentinels:
    expected_id = item["expected_edition_target_id"]
    expected_tag = item["expected_language_tag"]
    matched: list[dict[str, str]] = []
    presence = "MISSING_EXACT_TARGET"
    context_matches = [
        row
        for row in supplements
        if expected_tag
        and (
            row["stratum_id"].startswith(expected_tag)
            or expected_tag.lower() in row["label"].lower()
        )
    ]
    if expected_id in authority_by_id:
        matched = [authority_by_id[expected_id]]
        presence = "PRESENT_EXACT_TARGET"
    elif expected_id in alias_to_primary and alias_to_primary[expected_id] in authority_by_id:
        matched = [authority_by_id[alias_to_primary[expected_id]]]
        presence = "PRESENT_AS_ALIAS_TO_PRIMARY"
    elif expected_tag and expected_tag in tags_to_authority:
        matched = tags_to_authority[expected_tag]
        presence = "PRESENT_TAG_MATCH_DIFFERENT_TARGET_ID"
    elif context_matches:
        presence = "PRESENT_CONTEXT_STRATUM_NO_EXACT_EDITION_TARGET"
    elif expected_tag:
        expected_base = expected_tag.split("-", 1)[0]
        base_matches = [
            row
            for row in authority
            if any(tag.split("-", 1)[0] == expected_base for tag in split_tags(row.get("language_tags", "")))
        ]
        if base_matches:
            matched = base_matches
            presence = "PRESENT_BASE_LANGUAGE_ONLY_EXACT_TERRITORY_SCRIPT_OR_STANDARD_PROFILE_MISSING"
    matched_ids = [row["edition_target_id"] for row in matched]
    rank_rows = [score_by_id.get(target_id, {}) for target_id in matched_ids]
    ranks = [
        clean(top100_by_id.get(target_id, {}).get("decision_rank", row.get("l_m_need_rank", "")))
        for target_id, row in zip(matched_ids, rank_rows)
    ]
    ranks = [rank for rank in ranks if rank]
    any_ranked = any(
        clean(row.get("order_lane")) == "person_need"
        and bool(clean(row.get("l_m_need_rank")))
        and truthy(row.get("primary_order_eligible"))
        for row in rank_rows
    )
    any_stage = any(
        clean(row.get("order_lane")) == "stage_opportunity"
        and truthy(row.get("primary_order_eligible"))
        for row in rank_rows
    )
    if any_ranked:
        current_rank_status = "DIRECT_PERSON_RANKED"
        publication_disposition = "VISIBLE_DIRECT_PERSON_LANE_PLUS_STAGE_SUBJECT_PROFILE"
    elif any_stage:
        current_rank_status = "STAGE_OPPORTUNITY_RANKED"
        publication_disposition = "VISIBLE_STAGE_OPPORTUNITY_LANE_PLUS_STAGE_SUBJECT_PROFILE"
    elif matched:
        current_rank_status = "EXACT_TARGET_UNRANKED"
        publication_disposition = "VISIBLE_UNRANKED_EVIDENCE_PRIORITY_OR_NEGATIVE_CONTROL"
    elif context_matches:
        current_rank_status = "CONTEXT_ONLY"
        publication_disposition = "VISIBLE_MANDATORY_CONTEXT_AND_VALUE_OF_INFORMATION_LANE"
    else:
        current_rank_status = "NO_TARGET_OR_CONTEXT_RECORD"
        publication_disposition = "UNRANKED_EVIDENCE_NEEDED_ADD_EXACT_TARGET"
    row = {
        **item,
        "presence_status": presence,
        "matched_target_ids": ";".join(matched_ids),
        "matched_context_strata": ";".join(row["stratum_id"] for row in context_matches),
        "current_rank_status": current_rank_status,
        "current_direct_person_ranks": ";".join(ranks),
        "publication_disposition": publication_disposition,
    }
    row["row_sha256"] = row_digest(row)
    sentinel_rows.append(row)
    add_inclusion(
        {
            "inclusion_id": f"sentinel:{item['sentinel_id']}",
            "record_kind": "GLOBAL_INCLUSION_SENTINEL_CHECK",
            "target_id": expected_id,
            "canonical_target_id": ";".join(matched_ids),
            "target_label": item["target_label"],
            "language_or_intervention_tag": expected_tag,
            "script_or_mode": item["script_or_mode"],
            "territory_or_community": item["territory_or_community"],
            "decision_lane": item["minimum_lane"],
            "evidence_status": presence,
            "rank_status": current_rank_status,
            "current_direct_person_rank": ";".join(ranks),
            "disposition_reason": item["why_required"],
            "priority_action": item["preferred_evidence_action"],
            "overlap_nonadditivity": "Sentinel rows are coverage checks and receive zero additional population credit.",
            "source_record_ids": ";".join(
                [*matched_ids, *(row["stratum_id"] for row in context_matches)]
            ),
        }
    )


# 8. Complete source-to-score crosswalk.
CROSSWALK_FIELDS = [
    "authorization_id",
    "source_lane",
    "source_record_id",
    "evidence_identity_id",
    "edition_target_id",
    "canonical_language_target_id",
    "regional_stratum_id",
    "authorization_status",
    "authorization_tier",
    "authorization_reason",
    "population_low_persons",
    "population_base_persons",
    "population_high_persons",
    "population_definition",
    "source_ids",
    "source_urls",
    "score_row_present",
    "score_order_lane",
    "score_primary_order_eligible",
    "score_population_atom_id",
    "score_selected_source_record_id",
    "score_authorization_ids",
    "binding_outcome",
    "row_sha256",
]
crosswalk_rows: list[dict[str, Any]] = []
for auth in authorizations:
    score = score_by_id.get(auth["edition_target_id"], {})
    selected_ids = set(filter(None, clean(score.get("authorization_ids")).split(";")))
    if auth["authorization_status"] == "ADMIT":
        outcome = (
            "ADMITTED_AND_SELECTED_FOR_SCORE"
            if auth["authorization_id"] in selected_ids
            else "ADMITTED_NOT_SELECTED_COMPETING_OR_NONPRIMARY_EVIDENCE"
        )
    elif auth["authorization_status"] == "STAGE_OPPORTUNITY":
        outcome = "STAGE_OPPORTUNITY_SEPARATE_ORDER"
    else:
        outcome = "EXCLUDED_WITH_EXPLICIT_REASON"
    row = {
        "authorization_id": auth["authorization_id"],
        "source_lane": auth["source_lane"],
        "source_record_id": auth["source_record_id"],
        "evidence_identity_id": auth["evidence_identity_id"],
        "edition_target_id": auth["edition_target_id"],
        "canonical_language_target_id": auth["canonical_language_target_id"],
        "regional_stratum_id": auth["regional_stratum_id"],
        "authorization_status": auth["authorization_status"],
        "authorization_tier": auth["authorization_tier"],
        "authorization_reason": auth["reason"],
        "population_low_persons": auth["population_low_persons"],
        "population_base_persons": auth["population_base_persons"],
        "population_high_persons": auth["population_high_persons"],
        "population_definition": auth["population_definition"],
        "source_ids": auth["source_ids"],
        "source_urls": auth["source_urls"],
        "score_row_present": "true" if score else "false",
        "score_order_lane": score.get("order_lane", ""),
        "score_primary_order_eligible": score.get("primary_order_eligible", ""),
        "score_population_atom_id": score.get("population_atom_id", ""),
        "score_selected_source_record_id": score.get("source_record_id", ""),
        "score_authorization_ids": score.get("authorization_ids", ""),
        "binding_outcome": outcome,
    }
    row["row_sha256"] = row_digest(row)
    crosswalk_rows.append(row)


# 9. Public-safe score table.  Synthetic territorial/world ceilings are blank,
# while the identity and explicit acquisition reason remain visible.
public_score_rows: list[dict[str, Any]] = []
public_extra_fields = ["public_population_status", "public_use_caveat", "public_row_sha256"]
score_fields = list(scores[0].keys())
for original in scores:
    row = dict(original)
    synthetic = truthy(row.get("synthetic_or_model_prior")) or (
        not truthy(row.get("primary_order_eligible"))
        and clean(row.get("population_source_id")).startswith("MODEL_PRIOR_")
    )
    if synthetic:
        for field in [
            "population_low",
            "population_base",
            "population_high",
            "population_point_for_model",
            "population_source_url",
            "population_reference_year",
            "population_confidence",
            "population_atom_id",
            "source_population_low_persons",
            "source_population_base_persons",
            "source_population_high_persons",
            "normalized_population_low_persons",
            "normalized_population_high_persons",
            "intrinsic_need_low",
            "intrinsic_need_model",
            "intrinsic_need_high",
            "l_m_need_p05",
            "l_m_need_median",
            "l_m_need_mean",
            "l_m_need_p95",
            "l_m_efficiency_p05",
            "l_m_efficiency_median",
            "l_m_efficiency_mean",
            "l_m_efficiency_p95",
        ]:
            row[field] = ""
        row["population_basis_class"] = "NO_PUBLIC_SOURCE_BOUND_PERSON_DENOMINATOR"
        row["population_source_id"] = ""
        row["population_definition"] = "No source-bound person denominator is published for this target."
        row["public_population_status"] = "UNRANKED_NO_SOURCE_BOUND_PERSON_DENOMINATOR"
        row["public_use_caveat"] = "Identity and evidence-acquisition record only; no population, benefit total, or rank may be inferred from country/world model priors."
    else:
        row["public_population_status"] = (
            "SOURCE_BOUND_DIRECT_PERSON_ORDER"
            if truthy(row.get("primary_order_eligible"))
            else "SOURCE_BOUND_CONTEXT_NOT_DIRECT_PERSON_ORDER"
        )
        row["public_use_caveat"] = "Use only with the published definition, reference year, uncertainty, and nonadditivity rule."
    row["public_row_sha256"] = row_digest(row, hash_field="public_row_sha256")
    public_score_rows.append(row)


# Deterministic order and writes.
inclusion_rows.sort(key=lambda row: (row["record_kind"], row["inclusion_id"]))
sentinel_rows.sort(key=lambda row: row["sentinel_id"])
crosswalk_rows.sort(key=lambda row: row["authorization_id"])
displacement_rows.sort(key=lambda row: row["portfolio_id"])
public_score_rows.sort(key=lambda row: row["edition_target_id"])

write_csv(INCLUSION_OUT, inclusion_rows, INCLUSION_FIELDS)
write_csv(SENTINEL_OUT, sentinel_rows, SENTINEL_FIELDS)
write_csv(CROSSWALK_OUT, crosswalk_rows, CROSSWALK_FIELDS)
write_csv(PUBLIC_SCORE_OUT, public_score_rows, score_fields + public_extra_fields)
write_csv(DISPLACEMENT_OUT, displacement_rows, DISPLACEMENT_FIELDS)


# Data-product QA.
inclusion_ids = [row["inclusion_id"] for row in inclusion_rows]
missing_sentinels = [
    row["sentinel_id"]
    for row in sentinel_rows
    if row["presence_status"] == "MISSING_EXACT_TARGET"
]
partial_profile_sentinels = [
    row["sentinel_id"]
    for row in sentinel_rows
    if row["presence_status"]
    == "PRESENT_BASE_LANGUAGE_ONLY_EXACT_TERRITORY_SCRIPT_OR_STANDARD_PROFILE_MISSING"
]
context_only_sentinels = [
    row["sentinel_id"]
    for row in sentinel_rows
    if row["presence_status"] == "PRESENT_CONTEXT_STRATUM_NO_EXACT_EDITION_TARGET"
]
top100_atom_groups: dict[str, list[str]] = defaultdict(list)
for row in top100:
    atom = clean(row.get("population_atom_id"))
    if atom:
        top100_atom_groups[atom].append(row["edition_target_id"])
duplicate_top100_atoms = {
    atom: ids for atom, ids in top100_atom_groups.items() if len(ids) > 1
}
synthetic_public_population_leaks = []
for row in public_score_rows:
    if row["public_population_status"] == "UNRANKED_NO_SOURCE_BOUND_PERSON_DENOMINATOR":
        leaked = [
            field
            for field in (
                "population_low",
                "population_base",
                "population_high",
                "population_point_for_model",
                "source_population_low_persons",
                "source_population_base_persons",
                "source_population_high_persons",
                "normalized_population_low_persons",
                "normalized_population_high_persons",
                "intrinsic_need_low",
                "intrinsic_need_model",
                "intrinsic_need_high",
            )
            if clean(row.get(field))
        ]
        if leaked:
            synthetic_public_population_leaks.append(
                {"edition_target_id": row["edition_target_id"], "fields": leaked}
            )

input_paths = [
    AUTHORITY_PATH,
    ALIAS_PATH,
    SCORE_PATH,
    TOP100_PATH,
    AUTHZ_PATH,
    SUPPLEMENT_PATH,
    STRUCTURAL_PATH,
    OMISSION_PATH,
    AMERICAS_INPUT_PATH,
    INTERLANGUAGE_PATH,
    SENTINEL_PATH,
]
output_paths = [
    INCLUSION_OUT,
    SENTINEL_OUT,
    CROSSWALK_OUT,
    PUBLIC_SCORE_OUT,
    DISPLACEMENT_OUT,
]

hard_failures: list[str] = []
if len(set(inclusion_ids)) != len(inclusion_ids):
    hard_failures.append("duplicate inclusion_id")
if len(authority_by_id) != len(authority):
    hard_failures.append("duplicate edition_target_id in authority")
if len(score_by_id) != len(scores):
    hard_failures.append("duplicate edition_target_id in score table")
if set(authority_by_id) != set(score_by_id):
    hard_failures.append("authority and score target sets differ")
if len(crosswalk_rows) != len(authorizations):
    hard_failures.append("authorization crosswalk row count mismatch")
if synthetic_public_population_leaks:
    hard_failures.append("synthetic/model prior values leaked into public population fields")
if any(row["row_sha256"] != row_digest(row) for row in inclusion_rows):
    hard_failures.append("inclusion row hash verification failed")
if any(row["row_sha256"] != row_digest(row) for row in sentinel_rows):
    hard_failures.append("sentinel row hash verification failed")
if any(row["row_sha256"] != row_digest(row) for row in displacement_rows):
    hard_failures.append("displacement row hash verification failed")

qa = {
    "schema": "interlanguage/global-inclusion-disposition-qa/1.0.0",
    "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "status": "FAIL" if hard_failures else "PASS_WITH_EXPLICIT_EVIDENCE_GAPS",
    "purpose": "Make all target, context, structural, displacement, bridge, alias, and high-consequence sentinel dispositions visible without inventing population counts.",
    "inputs": [file_identity(path) for path in input_paths],
    "outputs": [file_identity(path) for path in output_paths],
    "counts": {
        "authority_targets": len(authority),
        "alias_rows": len(aliases),
        "large_context_rows": len(supplements),
        "structural_access_rows": len(structural),
        "interlanguage_profiles": len(interlanguages),
        "displacement_portfolios": len(displacement_rows),
        "sentinel_checks": len(sentinel_rows),
        "sentinels_missing_exact_target": len(missing_sentinels),
        "sentinels_partial_base_language_only": len(partial_profile_sentinels),
        "sentinels_context_only_without_exact_target": len(context_only_sentinels),
        "inclusion_register_rows": len(inclusion_rows),
        "source_to_score_crosswalk_rows": len(crosswalk_rows),
        "public_score_rows": len(public_score_rows),
        "direct_person_score_rows": sum(
            1 for row in scores if truthy(row.get("primary_order_eligible"))
        ),
        "public_unranked_rows_with_population_values_removed": sum(
            1
            for row in public_score_rows
            if row["public_population_status"]
            == "UNRANKED_NO_SOURCE_BOUND_PERSON_DENOMINATOR"
        ),
    },
    "record_kind_counts": dict(sorted(Counter(row["record_kind"] for row in inclusion_rows).items())),
    "sentinel_presence_counts": dict(sorted(Counter(row["presence_status"] for row in sentinel_rows).items())),
    "missing_sentinel_ids": missing_sentinels,
    "partial_profile_sentinel_ids": partial_profile_sentinels,
    "context_only_sentinel_ids": context_only_sentinels,
    "top100_duplicate_population_atoms": duplicate_top100_atoms,
    "synthetic_public_population_leaks": synthetic_public_population_leaks,
    "hard_failures": hard_failures,
    "release_notes": [
        "PASS_WITH_EXPLICIT_EVIDENCE_GAPS is a data-integrity result, not permission to call the global evidence census complete.",
        "Every missing sentinel must remain visibly unranked/evidence-needed or acquire source-bound evidence before publication prose claims global completeness.",
        "Top-100 rows sharing a population atom require a duplicate-aware portfolio view before funder-facing presentation.",
        "Displacement cohorts are separate host-specific education portfolios and never direct language-person ranks.",
        "Bridge/interlanguage production reuse and reader comprehension are separate quantities; no family-wide reach is credited.",
    ],
}
QA_OUT.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(json.dumps(qa, ensure_ascii=False, indent=2))
