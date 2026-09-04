#!/usr/bin/env python3
"""Build the JSON-first canonical candidate universe.

This script deliberately uses only the Python standard library.  It does not
score candidates.  Its job is to normalize candidate identity, package rows,
access overlays, population-measure classes, source aliases, and row-level
provenance without inventing values or treating incompatible denominators as
additive.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STRUCTURED = ROOT / "structured"
QA = ROOT / "qa"
OUTPUT = STRUCTURED / "canonical_universe_proposal.json"

CANDIDATE_CSVS = [
    "accessibility_candidates.csv",
    "china_candidates.csv",
    "global_omission_candidates.csv",
    "indonesia_candidates.csv",
    "south_asia_candidates.csv",
]
SOURCE_CSVS = [
    "accessibility_sources.csv",
    "china_sources.csv",
    "global_omission_sources.csv",
    "indonesia_sources.csv",
    "south_asia_sources.csv",
]
PROPOSALS = [
    "africa_mapping_proposal.json",
    "americas_arctic_mapping.json",
    "oceania_indian_ocean_mapping_proposal.json",
    "southeast_asia_mapping_proposal.json",
    "japan_mapping_proposal.json",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def file_identity(path: Path, role: str) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": str(path),
        "role": role,
        "bytes": len(data),
        "sha256": sha256_bytes(data),
    }


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def row_hash(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def proposal_rows(data: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    rows = data[kind]
    if not rows:
        return []
    if isinstance(rows[0], dict):
        return [dict(row) for row in rows]
    if kind == "candidates":
        fields = (
            data.get("candidate_fields")
            or data.get("candidate_header")
            or data.get("requested_candidate_header")
        )
    else:
        fields = (
            data.get("source_fields")
            or data.get("source_header")
            or data.get("requested_source_header")
        )
    if not fields:
        raise ValueError(f"Array-form proposal has no {kind} field list")
    return [dict(zip(fields, row)) for row in rows]


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def slug(value: str, limit: int = 72) -> str:
    text = unicodedata.normalize("NFKD", value)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return (text or "unresolved")[:limit].rstrip("-")


def parse_number(value: Any) -> int | float | None:
    text = clean(value).replace(",", "")
    if text == "":
        return None
    number = float(text)
    if number.is_integer():
        return int(number)
    return number


def truthy(value: Any) -> bool:
    return clean(value).lower() in {"true", "yes", "1", "rankable"}


def normalize_tag(tag: str) -> str:
    aliases = {
        "ind": "id-Latn-ID",
        "pa-Arab-PK": "pnb-Arab-PK",
        "ja-JP": "ja-Jpan-JP",
        "jsl": "jsl-JP",
        "asf": "asf-AU",
        "sgn": "",
        "und": "",
    }
    return aliases.get(clean(tag), clean(tag))


def infer_mode(tag: str, script: str, target_id: str) -> str:
    joined = f"{tag} {script} {target_id}".lower()
    if "visual-manual" in joined or re.search(
        r"(^|[-:])(ase|asf|jsl|csl|ins|pks|inl|bzs|mfs|rsl|tsm|esl|nsi|sfs|bvl|nzs|prl)([-:]|$)",
        joined,
    ):
        return "signed"
    if target_id.endswith(":spoken"):
        return "spoken"
    if target_id.endswith(":written"):
        return "written"
    if target_id.startswith("macro:"):
        return "unresolved_macro"
    return "written_or_multimodal"


def infer_measure_class(row: dict[str, Any], disposition: dict[str, Any] | None) -> str:
    if disposition and disposition.get("measure_class"):
        return clean(disposition["measure_class"]).lower()
    unit = clean(row.get("population_unit")).lower()
    definition = clean(row.get("population_definition")).lower()
    notes = clean(row.get("notes"))
    note_match = re.search(r"measure_class\s*=\s*([^;]+)", notes, re.I)
    note_class = clean(note_match.group(1)).lower() if note_match else ""
    if "percent" in unit:
        return "percentage_only"
    if "person_times" in unit or "person-times" in unit:
        return "person_times"
    if "fte" in unit:
        return "fte_person_years"
    if "households" in unit and not unit.startswith("persons"):
        return "households"
    if "enrol" in unit or "learners" in unit or "students" in unit:
        return "enrolment"
    if "unhcr" in unit or "displac" in unit or "refugee" in definition:
        return "displacement_status_cohort"
    if "ethnicity" in unit or "identity" in unit or "race_category" in unit:
        return "ethnicity_or_identity_proxy"
    if any(token in unit for token in ("territory", "national_population", "island_population")):
        return "territorial_exposure_ceiling"
    if "home_language" in unit or "mother_tongue" in unit or "l1" in unit:
        return "home_or_first_language"
    if any(
        token in unit
        for token in (
            "speaking",
            "speaker",
            "language_users",
            "language_knowledge",
            "speak_or_understand",
            "greatest_use_language",
        )
    ):
        return "speaker_or_reported_ability"
    if "workforce" in unit or "employed" in unit:
        return "workforce_cohort"
    if any(token in unit for token in ("disability", "hearing", "vision", "blind", "deaf")):
        return "disability_proxy"
    if note_class:
        note_map = {
            "h": "home_language",
            "h aggregate": "home_language_aggregate",
            "h aggregate/inverse": "home_language_aggregate",
            "h unquantified": "home_language_unquantified",
            "h/ethnicity aggregate": "home_language_ethnicity_proxy",
            "h/language response": "home_language_response",
            "h retrospective": "home_language_retrospective",
            "h/l1": "home_or_first_language",
            "s": "speaker_or_reported_ability",
            "s aggregate/unquantified": "speaker_aggregate_unquantified",
            "s/c combined": "speaker_combined_cohort",
            "e": "enrolment",
            "p": "proxy",
            "l": "literacy_or_language_percentage",
            "l aggregate": "literacy_aggregate",
            "unknown": "unknown",
            "identity_not_population": "identity_proxy",
            "aggregate_not_population": "aggregate_proxy",
        }
        return note_map.get(note_class, note_class.replace(" ", "_"))
    if any(token in definition for token in ("l1", "first language", "mother tongue")):
        return "home_or_first_language"
    if "home-language" in definition or "home language" in definition:
        return "home_language"
    if any(token in definition for token in ("enrolled", "enrolment", "learners", "students", "pupils")):
        return "enrolment"
    if any(token in definition for token in ("nonattendance", "out-of-school", "not enrolled")):
        return "education_status_cohort"
    if any(token in definition for token in ("opportunity universe", "total population", "residents aged")):
        return "territorial_or_age_exposure_ceiling"
    if any(token in definition for token in ("direct-reach", "direct reach", "speaker estimate")):
        return "direct_reach_synthesis"
    if clean(row.get("population_low")) or clean(row.get("population_base")) or clean(row.get("population_high")):
        return "persons_basis_not_stated"
    return "no_usable_population"


def direct_measure_class(measure_class: str) -> bool:
    disallowed = (
        "enrol",
        "territorial",
        "exposure",
        "workforce",
        "status",
        "displacement",
        "household",
        "percentage",
        "proxy",
        "ethnicity",
        "identity",
        "fte",
        "person_times",
        "unknown",
        "no_usable",
        "aggregate",
        "unclassified",
        "basis_not_stated",
        "synthesis",
        "ceiling",
    )
    return not any(token in measure_class for token in disallowed)


def output_target_id(
    row: dict[str, Any],
    origin: str,
    disposition: dict[str, Any] | None,
    repeated_tags: dict[tuple[str, str], int],
) -> str | None:
    if disposition and clean(disposition.get("canonical_target_id")):
        return clean(disposition["canonical_target_id"])
    tag = normalize_tag(clean(row.get("language_tag")))
    language = clean(row.get("language_variety"))
    territory = clean(row.get("territory_community"))
    if not tag:
        if not language or language.lower() in {"none", "not applicable", "n/a"}:
            return None
        unresolved_markers = ("unresolved", "aggregate", "cluster", "macro", "screening")
        if any(marker in f"{language} {row.get('target_label', '')}".lower() for marker in unresolved_markers):
            return f"macro:{clean(row['candidate_id'])}"
        return f"lang:unresolved-tag:{slug(language)}:{slug(territory, 36)}"

    base = f"lang:{tag}"
    origin_key = origin.lower()
    duplicate_in_file = repeated_tags.get((origin, tag), 0) > 1
    if duplicate_in_file and "africa_mapping" in origin_key:
        return f"{base}:variety:{slug(language or territory, 42)}"
    if duplicate_in_file and "americas_arctic" in origin_key:
        return f"{base}:variety:{slug(language or territory, 42)}"
    if duplicate_in_file and "oceania_indian_ocean" in origin_key:
        return f"{base}:community:{slug(territory.split(';')[0], 42)}"
    return base


def main() -> None:
    input_manifest: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []

    for filename in CANDIDATE_CSVS:
        path = STRUCTURED / filename
        rows = read_csv(path)
        record = file_identity(path, "current_candidate_csv")
        record["candidate_rows"] = len(rows)
        input_manifest.append(record)
        for index, row in enumerate(rows, start=2):
            candidates.append(
                {
                    "origin_file": f"structured/{filename}",
                    "source_row_number": index,
                    "row": row,
                    "original_row_hash": row_hash(row),
                }
            )

    for filename in SOURCE_CSVS:
        path = STRUCTURED / filename
        rows = read_csv(path)
        record = file_identity(path, "current_source_csv")
        record["source_rows"] = len(rows)
        input_manifest.append(record)
        for index, row in enumerate(rows, start=2):
            sources.append(
                {
                    "origin_file": f"structured/{filename}",
                    "source_row_number": index,
                    "row": row,
                    "original_row_hash": row_hash(row),
                }
            )

    for filename in PROPOSALS:
        path = STRUCTURED / filename
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        candidate_rows = proposal_rows(data, "candidates")
        source_rows = proposal_rows(data, "sources")
        record = file_identity(path, "regional_mapping_proposal")
        record.update({"candidate_rows": len(candidate_rows), "source_rows": len(source_rows)})
        input_manifest.append(record)
        for index, row in enumerate(candidate_rows, start=1):
            candidates.append(
                {
                    "origin_file": f"structured/{filename}",
                    "source_row_number": index,
                    "row": row,
                    "original_row_hash": row_hash(row),
                }
            )
        for index, row in enumerate(source_rows, start=1):
            sources.append(
                {
                    "origin_file": f"structured/{filename}",
                    "source_row_number": index,
                    "row": row,
                    "original_row_hash": row_hash(row),
                }
            )

    reference_files = [
        (ROOT / "DURABLE_GOAL.md", "controlling_goal"),
        (ROOT / "SCORING_SPECIFICATION.md", "controlling_scoring_specification"),
        (ROOT / "CANDIDATE_UNIVERSE_RAW.csv", "superseded_audit_snapshot_not_independent_input"),
        (QA / "CANDIDATE_CANONICALIZATION_AUDIT_20260901.md", "canonicalization_audit"),
        (QA / "CANDIDATE_DISPOSITION_20260901.json", "row_disposition_authority"),
        (QA / "RAW_CANDIDATE_EVIDENCE_AUDIT.json", "raw_evidence_audit"),
        (QA / "SOURCE_IDENTITY_AUDIT.json", "source_identity_audit"),
        (STRUCTURED / "accessibility_population_reference_proposal.json", "accessibility_population_disposition"),
    ]
    for path, role in reference_files:
        input_manifest.append(file_identity(path, role))

    disposition = json.loads((QA / "CANDIDATE_DISPOSITION_20260901.json").read_text(encoding="utf-8-sig"))
    raw_audit = json.loads((QA / "RAW_CANDIDATE_EVIDENCE_AUDIT.json").read_text(encoding="utf-8-sig"))
    source_audit = json.loads((QA / "SOURCE_IDENTITY_AUDIT.json").read_text(encoding="utf-8-sig"))
    a11y_disposition = json.loads(
        (STRUCTURED / "accessibility_population_reference_proposal.json").read_text(encoding="utf-8-sig")
    )

    a11y_updates = {
        item["candidate_id"]: item["field_updates"]
        for item in a11y_disposition["candidate_updates"]
    }
    for item in candidates:
        candidate_id = clean(item["row"].get("candidate_id"))
        if candidate_id in a11y_updates:
            item["row"] = {**item["row"], **a11y_updates[candidate_id]}
            item["applied_update"] = "accessibility_population_reference_proposal"
        item["effective_row_hash"] = row_hash(item["row"])

    # The input candidate IDs are globally unique by design.
    candidate_ids = [clean(item["row"].get("candidate_id")) for item in candidates]
    if len(candidate_ids) != len(set(candidate_ids)) or "" in candidate_ids:
        raise ValueError("Candidate IDs are blank or not globally unique")

    # Source aliases share a URL, not necessarily an identical claim.  Preserve
    # every source row but bind URL aliases to one deterministic canonical ID.
    url_groups = {
        group["canonical_url"]: sorted(group["source_ids"])
        for group in source_audit["same_url_multiple_source_ids"]
    }
    source_alias_lookup: dict[str, tuple[str, list[str]]] = {}
    for url, ids in url_groups.items():
        canonical = ids[0]
        for source_id in ids:
            source_alias_lookup[source_id] = (canonical, ids)

    source_registry: list[dict[str, Any]] = []
    source_ids_seen: set[str] = set()
    for item in sources:
        row = item["row"]
        source_id = clean(row.get("source_id"))
        if not source_id or source_id in source_ids_seen:
            raise ValueError(f"Blank or duplicate source_id: {source_id!r}")
        source_ids_seen.add(source_id)
        canonical_source_id, alias_ids = source_alias_lookup.get(source_id, (source_id, [source_id]))
        source_registry.append(
            {
                "source_id": source_id,
                "canonical_source_id": canonical_source_id,
                "same_url_alias_ids": alias_ids,
                "title": clean(row.get("title")),
                "organization": clean(row.get("organization")),
                "year": clean(row.get("year")),
                "url": clean(row.get("url")),
                "access_date": clean(row.get("access_date")),
                "claim_scope": clean(row.get("claim_scope")),
                "origin_file": item["origin_file"],
                "source_row_number": item["source_row_number"],
                "source_row_sha256": item["original_row_hash"],
                "undated": clean(row.get("year")).lower() in {"", "n.d.", "nd", "undated"},
            }
        )
    source_registry.sort(key=lambda row: row["source_id"])

    # Explicit repeated-denominator groups from the independent raw audit.
    repeated_group_by_candidate: dict[str, str] = {}
    repeated_group_data: dict[str, dict[str, Any]] = {}
    for index, group in enumerate(raw_audit["repeated_denominators"], start=1):
        group_id = f"shared-denominator:{index:03d}"
        repeated_group_data[group_id] = group
        for candidate_id in group["candidate_ids"]:
            repeated_group_by_candidate[candidate_id] = group_id

    # Count repeated tags within each origin so true regional varieties can be
    # preserved while stage/cohort rows for Japan and Southeast Asia collapse.
    repeated_tags: dict[tuple[str, str], int] = defaultdict(int)
    for item in candidates:
        tag = normalize_tag(clean(item["row"].get("language_tag")))
        if tag:
            repeated_tags[(item["origin_file"], tag)] += 1

    # First pass: canonical target IDs and one primary output classification.
    row_state: dict[str, dict[str, Any]] = {}
    for item in candidates:
        row = item["row"]
        candidate_id = clean(row["candidate_id"])
        disp = disposition.get(candidate_id)
        target_id = output_target_id(row, item["origin_file"], disp, repeated_tags)
        disp_name = clean(disp.get("disposition")) if disp else "regional_proposal"
        primary_type = "access_overlay" if disp_name == "overlay_only" else "package_intervention"
        row_state[candidate_id] = {
            "item": item,
            "disposition": disp,
            "disposition_name": disp_name,
            "target_id": target_id,
            "primary_type": primary_type,
        }

    # Canonical language targets are dimensions.  They are not extra candidate
    # mappings; each candidate still has exactly one primary package/overlay.
    target_acc: dict[str, dict[str, Any]] = {}
    for candidate_id, state in row_state.items():
        target_id = state["target_id"]
        if not target_id:
            continue
        row = state["item"]["row"]
        tag = normalize_tag(clean(row.get("language_tag")))
        script = clean(row.get("script_orthography"))
        territory = clean(row.get("territory_community"))
        language = clean(row.get("language_variety"))
        exactness = "exact"
        if target_id.startswith("macro:"):
            exactness = "unresolved_macro"
        elif target_id.startswith("lang:unresolved-tag:"):
            exactness = "exact_name_identifier_unresolved"
        acc = target_acc.setdefault(
            target_id,
            {
                "language_target_id": target_id,
                "universe_membership": True,
                "language_tags": [],
                "language_variety_names": [],
                "scripts_orthographies": [],
                "territories_communities": [],
                "language_mode": infer_mode(tag, script, target_id),
                "exactness": exactness,
                "source_candidate_ids": [],
                "source_origin_files": [],
                "population_measure_ids": [],
                "rankable_population_basis": False,
                "unranked_reasons": [],
            },
        )
        for key, value in (
            ("language_tags", tag),
            ("language_variety_names", language),
            ("scripts_orthographies", script),
            ("territories_communities", territory),
            ("source_candidate_ids", candidate_id),
            ("source_origin_files", state["item"]["origin_file"]),
        ):
            if value and value not in acc[key]:
                acc[key].append(value)

    # Population measures.  Shared groups and duplicate preferred rows are
    # explicitly resolved, never summed.  Ka'apor is split because its original
    # triplet mixed community size with deaf signers.
    measure_acc: dict[str, dict[str, Any]] = {}
    row_measure_ids: dict[str, list[str]] = defaultdict(list)
    row_population_disposition: dict[str, str] = {}

    def add_measure(
        *,
        candidate_id: str,
        target_id: str | None,
        measure_class: str,
        low: int | float | None,
        base: int | float | None,
        high: int | float | None,
        unit: str,
        definition: str,
        year: str,
        source_id: str,
        source_url: str,
        confidence: str,
        shared_group_id: str | None,
        rankable_flag: bool,
        special_key: str = "",
        forced_context_reason: str = "",
    ) -> str:
        if shared_group_id:
            key = f"shared:{shared_group_id}:{special_key}"
        else:
            key_payload = [
                target_id,
                measure_class,
                low,
                base,
                high,
                unit,
                definition,
                year,
                source_id,
                special_key,
            ]
            key = row_hash(key_payload)[:24].lower()
        measure_id = f"pop:{key}"
        rank_eligibility = "eligible_direct_typed_measure"
        if forced_context_reason:
            rank_eligibility = f"context_only:{forced_context_reason}"
        elif shared_group_id:
            rank_eligibility = "context_only:shared_denominator"
        elif not rankable_flag:
            rank_eligibility = "context_only:source_row_unranked"
        elif not direct_measure_class(measure_class):
            rank_eligibility = f"context_only:measure_class_{measure_class}"
        acc = measure_acc.setdefault(
            measure_id,
            {
                "population_measure_id": measure_id,
                "language_target_ids": [],
                "source_candidate_ids": [],
                "measure_class": measure_class,
                "population_low": low,
                "population_base": base,
                "population_high": high,
                "population_unit": unit,
                "population_definition": definition,
                "population_reference_year": year,
                "population_source_id": source_id,
                "population_source_url": source_url,
                "evidence_confidence": confidence,
                "shared_denominator_group": shared_group_id,
                "rank_eligibility": rank_eligibility,
                "aggregation_policy": "non_additive; never sum with another measure or measure class without a proved disjoint-person crosswalk",
            },
        )
        if target_id and target_id not in acc["language_target_ids"]:
            acc["language_target_ids"].append(target_id)
        if candidate_id not in acc["source_candidate_ids"]:
            acc["source_candidate_ids"].append(candidate_id)
        row_measure_ids[candidate_id].append(measure_id)
        return measure_id

    for candidate_id, state in row_state.items():
        row = state["item"]["row"]
        disp = state["disposition"]
        target_id = state["target_id"]
        decision = clean(disp.get("preferred_population_row_decision")) if disp else ""
        measure_class = infer_measure_class(row, disp)
        low = parse_number(row.get("population_low"))
        base = parse_number(row.get("population_base"))
        high = parse_number(row.get("population_high"))
        shared_group_id = repeated_group_by_candidate.get(candidate_id)

        if candidate_id == "AMAR_BRA_KAAPOR_SIGN":
            add_measure(
                candidate_id=candidate_id,
                target_id=target_id,
                measure_class="community_population_context",
                low=2000,
                base=None,
                high=2300,
                unit="persons_kaapor_community_context",
                definition="Ka’apor community population range; context only and not the sign-language user count.",
                year="",
                source_id=clean(row.get("population_source_id")),
                source_url=clean(row.get("population_source_url")),
                confidence=clean(row.get("evidence_confidence")),
                shared_group_id=None,
                rankable_flag=False,
                special_key="community",
                forced_context_reason="different_denominator_community_population",
            )
            add_measure(
                candidate_id=candidate_id,
                target_id=target_id,
                measure_class="named_sign_language_users_approximate",
                low=None,
                base=18,
                high=None,
                unit="persons_deaf_kaapor_signers_approximate",
                definition="Approximately 18 deaf Ka’apor signers; kept separate from the 2,000–2,300 community-population range.",
                year="",
                source_id=clean(row.get("population_source_id")),
                source_url=clean(row.get("population_source_url")),
                confidence=clean(row.get("evidence_confidence")),
                shared_group_id=None,
                rankable_flag=False,
                special_key="signers",
                forced_context_reason="undated_approximate_count",
            )
            row_population_disposition[candidate_id] = "split_mixed_denominators_into_two_nonadditive_typed_measures"
            continue

        if low is None and base is None and high is None:
            row_population_disposition[candidate_id] = "no_numeric_population_measure"
            continue
        if decision.startswith("discard_") or decision.startswith("exclude_"):
            row_population_disposition[candidate_id] = f"excluded_by_disposition:{decision}"
            continue
        if decision in {
            "retain_intervention_without_population",
            "merge_notes_no_numeric_population",
            "retain_no_population_until_direct_measure",
        }:
            row_population_disposition[candidate_id] = f"excluded_by_disposition:{decision}"
            continue

        forced_context_reason = ""
        if state["disposition_name"] in {"split_required", "keep_target_unranked"}:
            forced_context_reason = state["disposition_name"]
        if state["primary_type"] == "access_overlay":
            forced_context_reason = "access_overlay_proxy_or_context"
        if not clean(row.get("population_reference_year")):
            forced_context_reason = forced_context_reason or "missing_reference_year_partial_identification"
        if not clean(row.get("population_source_id")):
            forced_context_reason = forced_context_reason or "missing_source_partial_identification"
        measure_id = add_measure(
            candidate_id=candidate_id,
            target_id=target_id,
            measure_class=measure_class,
            low=low,
            base=base,
            high=high,
            unit=clean(row.get("population_unit")),
            definition=clean(row.get("population_definition")),
            year=clean(row.get("population_reference_year")),
            source_id=clean(row.get("population_source_id")),
            source_url=clean(row.get("population_source_url")),
            confidence=clean(row.get("evidence_confidence")),
            shared_group_id=shared_group_id,
            rankable_flag=truthy(row.get("rankable")),
            forced_context_reason=forced_context_reason,
        )
        row_population_disposition[candidate_id] = f"retained_typed_measure:{measure_id}"

    # Attach measures to targets and derive the conservative target evidence state.
    for measure_id, measure in measure_acc.items():
        for target_id in measure["language_target_ids"]:
            if target_id in target_acc and measure_id not in target_acc[target_id]["population_measure_ids"]:
                target_acc[target_id]["population_measure_ids"].append(measure_id)
            if target_id in target_acc and measure["rank_eligibility"] == "eligible_direct_typed_measure":
                target_acc[target_id]["rankable_population_basis"] = True
    for target in target_acc.values():
        if target["exactness"] != "exact":
            target["rankable_population_basis"] = False
            target["unranked_reasons"].append(target["exactness"])
        if not target["rankable_population_basis"]:
            target["unranked_reasons"].append("no_validated_direct_typed_population_basis")
        for key in (
            "language_tags",
            "language_variety_names",
            "scripts_orthographies",
            "territories_communities",
            "source_candidate_ids",
            "source_origin_files",
            "population_measure_ids",
            "unranked_reasons",
        ):
            target[key] = sorted(set(target[key]))

    # Primary entities: every input candidate maps to exactly one package or overlay.
    package_acc: dict[str, dict[str, Any]] = {}
    overlay_acc: dict[str, dict[str, Any]] = {}
    provenance: list[dict[str, Any]] = []
    for candidate_id, state in row_state.items():
        item = state["item"]
        row = item["row"]
        target_id = state["target_id"]
        disp = state["disposition"]
        measure_ids = sorted(set(row_measure_ids.get(candidate_id, [])))
        if state["primary_type"] == "access_overlay":
            output_id = f"overlay:{slug(candidate_id)}"
            acc = overlay_acc.setdefault(
                output_id,
                {
                    "access_overlay_id": output_id,
                    "overlay_label": clean(row.get("target_label")),
                    "language_target_ids": [],
                    "territories_communities": [],
                    "modality": clean(row.get("modality")),
                    "learner_stage_scope": clean(row.get("learner_stage_scope")),
                    "population_measure_ids": [],
                    "source_candidate_ids": [],
                    "source_origin_files": [],
                    "rankable_as_language_target": False,
                    "evidence_status": "access_overlay_only; never substitutes for a named language target",
                    "baseline_access_status": clean(row.get("baseline_access_status")),
                    "evidence_confidence": clean(row.get("evidence_confidence")),
                    "notes": clean(row.get("notes")),
                },
            )
            if target_id and target_id not in acc["language_target_ids"]:
                acc["language_target_ids"].append(target_id)
            for key, values in (
                ("territories_communities", [clean(row.get("territory_community"))]),
                ("population_measure_ids", measure_ids),
                ("source_candidate_ids", [candidate_id]),
                ("source_origin_files", [item["origin_file"]]),
            ):
                for value in values:
                    if value and value not in acc[key]:
                        acc[key].append(value)
        else:
            # Collapse the known global/South-Asia duplicate family into one
            # general package while retaining both row-provenance records.
            collapse_group = clean(disp.get("overlap_collapse_group")) if disp else ""
            if (
                collapse_group.startswith("collapse:")
                and item["origin_file"]
                in {
                    "structured/global_omission_candidates.csv",
                    "structured/south_asia_candidates.csv",
                }
            ):
                output_id = f"package:{slug(target_id or collapse_group)}:general"
            else:
                output_id = f"package:{slug(candidate_id)}"
            acc = package_acc.setdefault(
                output_id,
                {
                    "package_intervention_id": output_id,
                    "language_target_ids": [],
                    "target_labels": [],
                    "territories_communities": [],
                    "learner_stage_scopes": [],
                    "modalities": [],
                    "population_measure_ids": [],
                    "source_candidate_ids": [],
                    "source_origin_files": [],
                    "academic_language_overlap": [],
                    "baseline_access_status": [],
                    "evidence_confidence": [],
                    "source_rankable_flags": [],
                    "canonical_rank_status": "unranked_pending_need_model_and_valid_population_basis",
                    "notes": [],
                },
            )
            for key, values in (
                ("language_target_ids", [target_id] if target_id else []),
                ("target_labels", [clean(row.get("target_label"))]),
                ("territories_communities", [clean(row.get("territory_community"))]),
                ("learner_stage_scopes", [clean(row.get("learner_stage_scope"))]),
                ("modalities", [clean(row.get("modality"))]),
                ("population_measure_ids", measure_ids),
                ("source_candidate_ids", [candidate_id]),
                ("source_origin_files", [item["origin_file"]]),
                ("academic_language_overlap", [clean(row.get("overlap_definition"))]),
                ("baseline_access_status", [clean(row.get("baseline_access_status"))]),
                ("evidence_confidence", [clean(row.get("evidence_confidence"))]),
                ("source_rankable_flags", [clean(row.get("rankable"))]),
                ("notes", [clean(row.get("notes"))]),
            ):
                for value in values:
                    if value and value not in acc[key]:
                        acc[key].append(value)

        provenance.append(
            {
                "provenance_id": f"row:{slug(item['origin_file'], 54)}:{slug(candidate_id, 72)}",
                "input_candidate_id": candidate_id,
                "origin_file": item["origin_file"],
                "source_row_number": item["source_row_number"],
                "original_row_sha256": item["original_row_hash"],
                "effective_row_sha256": item["effective_row_hash"],
                "applied_update": item.get("applied_update", ""),
                "input_disposition": state["disposition_name"],
                "primary_output_type": state["primary_type"],
                "primary_output_id": output_id,
                "language_target_ids": [target_id] if target_id else [],
                "population_measure_ids": measure_ids,
                "population_measure_disposition": row_population_disposition[candidate_id],
                "population_source_id": clean(row.get("population_source_id")),
                "preferred_population_row_decision": clean(disp.get("preferred_population_row_decision")) if disp else "regional_proposal_rules",
                "mapped_exactly_once": True,
            }
        )

    for collection in (package_acc, overlay_acc):
        for entity in collection.values():
            for key, value in entity.items():
                if isinstance(value, list):
                    entity[key] = sorted(set(value))

    language_targets = sorted(target_acc.values(), key=lambda row: row["language_target_id"])
    population_measures = sorted(measure_acc.values(), key=lambda row: row["population_measure_id"])
    package_interventions = sorted(package_acc.values(), key=lambda row: row["package_intervention_id"])
    access_overlays = sorted(overlay_acc.values(), key=lambda row: row["access_overlay_id"])
    provenance.sort(key=lambda row: (row["origin_file"], row["source_row_number"], row["input_candidate_id"]))

    # A compact deterministic assignment map is exposed separately from the
    # richer provenance rows.  This is the machine-checkable 1,062-row
    # partition requested by the canonicalization audit.
    input_assignment = [
        {
            "input_candidate_id": row["input_candidate_id"],
            "origin_file": row["origin_file"],
            "primary_output_type": row["primary_output_type"],
            "primary_output_id": row["primary_output_id"],
            "language_target_ids": row["language_target_ids"],
            "population_measure_ids": row["population_measure_ids"],
        }
        for row in provenance
    ]

    # 100m+ audit is measure-bounded and keeps shared totals as one entry.
    large_profiles: list[dict[str, Any]] = []
    for measure in population_measures:
        unit = measure["population_unit"].lower()
        values = [
            value
            for value in (
                measure["population_low"],
                measure["population_base"],
                measure["population_high"],
            )
            if isinstance(value, (int, float))
        ]
        if not values or max(values) < 100_000_000:
            continue
        if "percent" in unit or "million" in unit:
            continue
        status = "present_exact_target"
        omission_flag = False
        reasons: list[str] = []
        target_ids = measure["language_target_ids"]
        if not target_ids:
            status = "access_overlay_or_unattached_context"
            reasons.append("not_a_language_target")
        if any(target_id.startswith("macro:") for target_id in target_ids):
            status = "unresolved_macro_requires_exact_children"
            omission_flag = True
            reasons.append("macro_not_rankable")
        if measure["rank_eligibility"] != "eligible_direct_typed_measure":
            reasons.append(measure["rank_eligibility"])
        large_profiles.append(
            {
                "population_measure_id": measure["population_measure_id"],
                "language_target_ids": target_ids,
                "source_candidate_ids": measure["source_candidate_ids"],
                "population_low": measure["population_low"],
                "population_base": measure["population_base"],
                "population_high": measure["population_high"],
                "population_unit": measure["population_unit"],
                "measure_class": measure["measure_class"],
                "profile_status": status,
                "omission_flag": omission_flag,
                "omission_or_caveat_reasons": sorted(set(reasons)),
            }
        )
    large_profiles.sort(
        key=lambda row: max(
            value or 0
            for value in (row["population_low"], row["population_base"], row["population_high"])
        ),
        reverse=True,
    )

    # Preserve the disposition of every >=100m *input row* from the independent
    # audit, even when canonicalization blanks an invalid contextual proxy or
    # collapses repeated/duplicate evidence to one retained measure.
    hundred_million_input_row_disposition: list[dict[str, Any]] = []
    for audited_row in raw_audit["large_population_rows"]:
        candidate_id = audited_row["candidate_id"]
        state = row_state[candidate_id]
        hundred_million_input_row_disposition.append(
            {
                "input_candidate_id": candidate_id,
                "origin_file": audited_row["input_file"],
                "primary_output_type": state["primary_type"],
                "primary_output_id": next(
                    row["primary_output_id"]
                    for row in provenance
                    if row["input_candidate_id"] == candidate_id
                ),
                "language_target_ids": [state["target_id"]] if state["target_id"] else [],
                "population_measure_ids": sorted(set(row_measure_ids.get(candidate_id, []))),
                "population_measure_disposition": row_population_disposition[candidate_id],
                "omission_flag": (
                    bool(state["target_id"] and state["target_id"].startswith("macro:"))
                    or not bool(row_measure_ids.get(candidate_id, []))
                ),
                "audit_note": (
                    "No value was imputed. A blank measure list records an explicit duplicate/proxy exclusion or accessibility-population disposition."
                ),
            }
        )
    hundred_million_input_row_disposition.sort(key=lambda row: row["input_candidate_id"])

    primary_ids = [row["primary_output_id"] for row in provenance]
    mapped_input_ids = [row["input_candidate_id"] for row in provenance]
    unmapped = sorted(set(candidate_ids) - set(mapped_input_ids))
    multiply_mapped = sorted(
        candidate_id for candidate_id in set(mapped_input_ids) if mapped_input_ids.count(candidate_id) != 1
    )
    invalid_measures = []
    for measure in population_measures:
        low, base, high = (
            measure["population_low"],
            measure["population_base"],
            measure["population_high"],
        )
        if low is not None and base is not None and low > base:
            invalid_measures.append(measure["population_measure_id"])
        if base is not None and high is not None and base > high:
            invalid_measures.append(measure["population_measure_id"])
        if low is not None and high is not None and low > high:
            invalid_measures.append(measure["population_measure_id"])

    source_fk_missing = sorted(
        {
            row["population_source_id"]
            for row in provenance
            if row["population_source_id"] and row["population_source_id"] not in source_ids_seen
        }
    )

    payload = {
        "language_targets": language_targets,
        "population_measures": population_measures,
        "package_interventions": package_interventions,
        "access_overlays": access_overlays,
        "source_registry": source_registry,
        "source_row_provenance": provenance,
        "input_assignment": input_assignment,
        "hundred_million_profile_audit": large_profiles,
        "hundred_million_input_row_disposition": hundred_million_input_row_disposition,
    }
    payload_hashes = {key: row_hash(value) for key, value in payload.items()}

    output = {
        "schema_version": "interlanguage/global-educational-access-canonical-universe/1.0.0",
        "artifact_status": "validated_json_first_canonicalization_proposal_not_scoring_output",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "controlling_boundary": {
            "purpose": "Normalize exact language targets, typed population evidence, packages, access overlays, sources, and row provenance before any scoring.",
            "one_input_candidate_one_primary_mapping": True,
            "existing_or_local_work_affects_need_or_rank": False,
            "missing_values_are_zero": False,
            "population_measure_classes_interchangeable": False,
            "population_measures_additive_by_default": False,
            "raw_snapshot_role": "audit reference only; its 189 IDs are a subset of the 206 current structured rows and are not remapped as duplicate inputs",
            "large_profile_scope": "All >=100m numeric profiles present in the ten bounded candidate inputs; external global exhaustiveness remains a separate omission audit.",
        },
        "input_manifest": sorted(input_manifest, key=lambda row: row["path"]),
        "normalization_rules": {
            "canonical_dimensions": [
                "language_targets",
                "population_measures",
                "package_interventions",
                "access_overlays",
            ],
            "target_identity_excludes": [
                "learner stage",
                "subject domain",
                "delivery carrier",
                "disability status",
                "enrolment status",
            ],
            "preserved_distinctions": [
                "written versus spoken",
                "named sign languages",
                "script and orthography",
                "territory and genuine community variety",
                "population measure class",
            ],
            "macro_rule": "Retain unresolved macro rows unranked; split only where the inputs already contain exact child rows.",
            "shared_denominator_rule": "Represent each audited repeated denominator once, link all relevant targets, and mark it context-only and non-additive.",
            "kaapor_rule": "Split 2,000–2,300 community population from approximately 18 deaf signers; never treat them as one low/base/high interval.",
            "source_alias_rule": "Preserve every source ID and claim row; bind same-URL IDs to a deterministic canonical_source_id without erasing claim differences.",
            "forbidden_aggregation": "Never add L1, exposure, enrolment, households, displacement, disability, FTE/person-times, percentages, proxies, or repeated regional totals.",
        },
        **payload,
        "validation": {
            "input_candidate_rows": len(candidates),
            "unique_input_candidate_ids": len(set(candidate_ids)),
            "source_input_rows": len(sources),
            "unique_source_ids": len(source_ids_seen),
            "source_row_provenance_rows": len(provenance),
            "input_assignment_rows": len(input_assignment),
            "one_primary_mapping_per_input_candidate": len(provenance) == len(candidates) and not multiply_mapped,
            "zero_unmapped_requirement": len(unmapped) == 0,
            "unmapped_candidate_ids": unmapped,
            "multiply_mapped_candidate_ids": multiply_mapped,
            "language_target_rows": len(language_targets),
            "population_measure_rows": len(population_measures),
            "package_intervention_rows": len(package_interventions),
            "access_overlay_rows": len(access_overlays),
            "unresolved_macro_language_targets": sum(
                target["exactness"] == "unresolved_macro" for target in language_targets
            ),
            "exact_name_identifier_unresolved_targets": sum(
                target["exactness"] == "exact_name_identifier_unresolved" for target in language_targets
            ),
            "targets_with_direct_typed_population_basis": sum(
                target["rankable_population_basis"] for target in language_targets
            ),
            "remaining_unrankable_language_targets": sum(
                not target["rankable_population_basis"] for target in language_targets
            ),
            "shared_denominator_groups_in_audit": len(raw_audit["repeated_denominators"]),
            "shared_denominator_measure_rows": sum(
                bool(measure["shared_denominator_group"]) for measure in population_measures
            ),
            "invalid_population_intervals_after_kaapor_split": sorted(set(invalid_measures)),
            "source_foreign_key_failures": source_fk_missing,
            "same_url_alias_groups": len(source_audit["same_url_multiple_source_ids"]),
            "hundred_million_profiles": len(large_profiles),
            "hundred_million_unresolved_macro_flags": sum(
                row["omission_flag"] for row in large_profiles
            ),
            "hundred_million_input_rows_audited": len(hundred_million_input_row_disposition),
            "hundred_million_input_rows_expected": raw_audit["summary"]["rows_with_any_population_estimate_ge_100m"],
            "hundred_million_input_row_coverage_complete": (
                len(hundred_million_input_row_disposition)
                == raw_audit["summary"]["rows_with_any_population_estimate_ge_100m"]
            ),
            "rankable_flag_rows_missing_population_in_raw_audit": raw_audit["summary"]["rankable_missing_population_count"],
            "rankable_flag_rows_missing_source_in_raw_audit": raw_audit["summary"]["rankable_missing_source_count"],
            "rankable_flag_rows_missing_year_in_raw_audit": raw_audit["summary"]["rankable_missing_year_count"],
            "validation_passed": (
                len(provenance) == len(candidates)
                and not unmapped
                and not multiply_mapped
                and not invalid_measures
                and not source_fk_missing
                and len(source_ids_seen) == len(sources)
            ),
        },
        "payload_sha256": payload_hashes,
    }

    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "bytes": OUTPUT.stat().st_size,
                "sha256": sha256_bytes(OUTPUT.read_bytes()),
                "validation": output["validation"],
                "payload_sha256": payload_hashes,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
