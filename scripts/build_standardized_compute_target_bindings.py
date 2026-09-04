"""Build an exhaustive, fail-closed successor-target to compute-profile binding registry.

Only an exact language subtag plus an explicit script subtag may bind a target
to a direct FLORES measurement profile. Region, family, name, prestige, and the
common sensitivity envelope never create a direct binding.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


BINDING_SCHEMA_VERSION = "interlanguage/standard-compute-target-binding/1.0.0"
BINDING_PROTOCOL_VERSION = "exact-bcp47-language-script/1.0.0"
SNAPSHOT_UTC = "2026-09-01T00:00:00Z"
PINNED_ROSTER_SHA256 = "983a40756107072ca779c1f3a37684c8e5865fbedd9fc42768e9d1cab754656f"
PINNED_ROSTER_RECEIPT_SHA256 = "2fc00c134b25a682dbe1c2be161b9ba29c717eb04714f3e3b7306dbc2f156328"
PINNED_SUCCESSOR_UNIVERSE_SHA256 = "e078f8e72701d87b23a0f4b25184f89293a1e2931776b61f8e77f599d801a97c"
PINNED_SUCCESSOR_RECEIPT_SHA256 = "a470e834748b28c55bf713635833838ad6cf1adb38129265872818da7c5d5254"
PINNED_ISO6393_TABLE_SHA256 = "7a5ac370703ea0897356a8c383f2147865caf479e41c1c7bd96cc4c5f65e6907"
PINNED_ISO6393_MACROLANGUAGE_SHA256 = "fb01a86376d9c1abfc96d16be1b6dcffb4776a1f52fa22338d4979e9ffe1822f"
PINNED_IANA_LANGUAGE_SUBTAG_REGISTRY_SHA256 = "be21e91b6851f750a7b1a687f11209d46ad5a8471d6b10a1efc8d1dac4c8a926"
ROSTER_TOP_FIELDS = {
    "audit_date", "collision_dispositions", "counts", "expected_evaluation_kind_counts",
    "ontology_version", "roster_authority_identities", "roster_targets", "schema",
    "schema_contract_identity_included", "scorer_identity_included", "snapshot_id",
    "snapshot_payload_sha256", "status", "stratum_to_target_mapping", "target_selector",
    "universe_version", "unmanifested_inputs_imported",
}
ROSTER_TARGET_FIELDS = {
    "effective_universe_membership", "empirical_stratum_id", "exactness", "identity_assertions",
    "intervention_target_id", "language_mode", "language_tags", "language_target_id",
    "language_variety_names", "package_or_overlay_inheritance", "production_applicable",
    "profile_binding_requirement", "profile_binding_status", "roster_row_sha256",
    "roster_target_id", "scripts_orthographies", "target_identity_status", "target_kind",
    "territories_communities",
}
PINNED_ROSTER_COUNTS = {
    "roster_targets": 1266,
    "preserved_legacy_language_targets": 945,
    "audited_appended_language_targets": 24,
    "language_targets": 969,
    "production_applicable_language_targets": 860,
    "context_or_superseded_language_targets": 109,
    "regional_empirical_input_rows": 302,
    "regional_empirical_unique_strata": 297,
    "regional_empirical_intervention_targets": 297,
    "regional_empirical_collision_strata": 5,
    "production_applicable_targets": 1157,
    "expected_successor_evaluation_rows": 3325,
}
PINNED_TARGET_SELECTOR = {
    "all_binding_rows": "every roster_targets row",
    "all_binding_row_count": 1266,
    "effective_production_selector": "production_applicable == true",
    "effective_production_target_count": 1157,
    "effective_language_target_count": 860,
    "effective_empirical_intervention_target_count": 297,
    "binding_outcome_contract": "one row per roster target: direct exact profile or explicit missing/unranked",
}

ALIAS_FIELDS = (
    "source_language_code", "profile_language_code", "script_code", "territory_codes",
    "allowed_modes", "variety_required_terms", "relation_type", "point_binding_allowed",
    "iso6393_source_row_hash", "iso6393_profile_row_hash", "macrolanguage_row_hash",
    "iso6393_table_sha256", "iso6393_macrolanguage_sha256", "iana_registry_sha256",
    "authority_urls", "proxy_limitation", "alias_row_hash", "alias_set_hash",
)

BINDING_FIELDS = (
    "roster_snapshot_id",
    "successor_roster_file_sha256",
    "roster_target_id",
    "target_kind",
    "language_target_id",
    "intervention_target_id",
    "production_applicable",
    "target_representation_id",
    "target_language_or_variety_code",
    "target_script_code",
    "target_territory_code",
    "benchmark_profile_id",
    "profile_measurement_kind",
    "profile_match_scope",
    "binding_method",
    "binding_status",
    "order_b_eligible",
    "unavailable_reason",
    "sensitivity_control_status",
    "tokenization_measurement_set_sha256",
    "measurement_profile_registry_file_sha256",
    "measurement_profile_set_hash",
    "direct_measurement_row_hash",
    "target_roster_row_hash",
    "binding_row_hash",
    "binding_set_hash",
)


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_row_hash(row: Mapping[str, Any], excluded: set[str] | None = None) -> str:
    excluded_fields = excluded or set()
    return sha256_bytes(canonical_json_bytes({key: row[key] for key in sorted(row) if key not in excluded_fields}))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=BINDING_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in BINDING_FIELDS} for row in rows)


def write_alias_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ALIAS_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in ALIAS_FIELDS} for row in rows)


def build_alias_crosswalk(
    iso6393_path: Path,
    macrolanguage_path: Path,
    iana_registry_path: Path,
) -> tuple[list[dict[str, str]], str]:
    """Build the small, closed operational crosswalk from pinned authorities."""
    for path, expected_hash, expected_bytes, label in (
        (iso6393_path, PINNED_ISO6393_TABLE_SHA256, 178280, "ISO 639-3 table"),
        (macrolanguage_path, PINNED_ISO6393_MACROLANGUAGE_SHA256, 4609, "ISO 639-3 macrolanguage table"),
        (iana_registry_path, PINNED_IANA_LANGUAGE_SUBTAG_REGISTRY_SHA256, 731799, "IANA language-subtag registry"),
    ):
        if path.stat().st_size != expected_bytes or sha256_file(path) != expected_hash:
            raise ValueError(f"{label} bytes do not match the pinned authority snapshot")
    with iso6393_path.open("r", encoding="utf-8-sig", newline="") as handle:
        iso_rows = list(csv.DictReader(handle, delimiter="\t"))
    iso_by_id = {row["Id"]: row for row in iso_rows}
    required = {
        "ind": ("id", "I", "Indonesian"),
        "jpn": ("ja", "I", "Japanese"),
        "zho": ("zh", "M", "Chinese"),
        "cmn": ("", "I", "Mandarin Chinese"),
    }
    for code, (part1, scope, name) in required.items():
        row = iso_by_id.get(code)
        if row is None or (row["Part1"], row["Scope"], row["Ref_Name"]) != (part1, scope, name):
            raise ValueError(f"pinned ISO 639-3 authority row mismatch for {code}")
    with macrolanguage_path.open("r", encoding="utf-8-sig", newline="") as handle:
        macro_rows = list(csv.DictReader(handle, delimiter="\t"))
    macro = next((row for row in macro_rows if row.get("M_Id") == "zho" and row.get("I_Id") == "cmn"), None)
    if macro is None or macro.get("I_Status") != "A":
        raise ValueError("pinned ISO 639-3 authority lacks active zho/cmn macrolanguage membership")
    iana_text = iana_registry_path.read_text(encoding="utf-8")
    for evidence in (
        "Subtag: id\nDescription: Indonesian",
        "Subtag: ja\nDescription: Japanese",
        "Subtag: cmn\nDescription: Mandarin Chinese\nAdded: 2009-07-29\nMacrolanguage: zh",
        "Subtag: zh\nDescription: Chinese\nAdded: 2005-10-16\nScope: macrolanguage",
    ):
        if evidence not in iana_text:
            raise ValueError("pinned IANA registry lacks a required alias/macrolanguage record")

    row_hash = lambda row: sha256_bytes(canonical_json_bytes(row))
    source_hashes = {code: row_hash(iso_by_id[code]) for code in required}
    macro_hash = row_hash(macro)
    authority_urls = (
        "https://iso639-3.sil.org/code_tables/download_tables;"
        "https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry"
    )
    specs = (
        ("id", "ind", "Latn", "ID", "Indonesian;Bahasa Indonesia", "ISO639_PART1_PART3_EQUIVALENT", ""),
        ("ja", "jpn", "Jpan", "JP", "Japanese", "ISO639_PART1_PART3_EQUIVALENT", ""),
        ("zh", "zho", "Hans", "CN;SG", "Chinese;Mandarin", "ISO639_PART1_PART3_MACROLANGUAGE_EQUIVALENT", "The zho FLORES row is a written script proxy and does not establish spoken-variety equivalence."),
        ("zh", "zho", "Hant", "HK;MO;TW", "Chinese", "ISO639_PART1_PART3_MACROLANGUAGE_EQUIVALENT", "The zho FLORES row is a written script proxy and does not establish spoken-variety equivalence."),
        ("cmn", "zho", "Hans", "CN", "Mandarin;Putonghua", "ISO639_MACROLANGUAGE_MEMBER_PROFILE_PROXY", "ISO 639 proves membership, not benchmark-variety identity; allow only written Mandarin in CN and retain this proxy limitation."),
        ("cmn", "zho", "Hant", "TW", "Mandarin;Guoyu", "ISO639_MACROLANGUAGE_MEMBER_PROFILE_PROXY", "ISO 639 proves membership, not benchmark-variety identity; allow only written Taiwan Mandarin and retain this proxy limitation."),
        ("zho", "zho", "Hans", "CN;SG", "Chinese;Mandarin", "ISO6393_IDENTITY_WITH_TERRITORY_SCOPE", "Written script proxy only; spoken varieties are excluded."),
        ("zho", "zho", "Hant", "HK;MO;TW", "Chinese", "ISO6393_IDENTITY_WITH_TERRITORY_SCOPE", "Written script proxy only; spoken varieties are excluded."),
    )
    rows: list[dict[str, str]] = []
    for source, profile, script, territories, variety_terms, relation, limitation in specs:
        source_authority_code = {"id": "ind", "ja": "jpn", "zh": "zho"}.get(source, source)
        row = {
            "source_language_code": source,
            "profile_language_code": profile,
            "script_code": script,
            "territory_codes": territories,
            "allowed_modes": "written;written_or_multimodal",
            "variety_required_terms": variety_terms,
            "relation_type": relation,
            "point_binding_allowed": "true",
            "iso6393_source_row_hash": source_hashes[source_authority_code],
            "iso6393_profile_row_hash": source_hashes[profile],
            "macrolanguage_row_hash": macro_hash if source in {"cmn", "zh", "zho"} else "",
            "iso6393_table_sha256": PINNED_ISO6393_TABLE_SHA256,
            "iso6393_macrolanguage_sha256": PINNED_ISO6393_MACROLANGUAGE_SHA256,
            "iana_registry_sha256": PINNED_IANA_LANGUAGE_SUBTAG_REGISTRY_SHA256,
            "authority_urls": authority_urls,
            "proxy_limitation": limitation,
            "alias_row_hash": "",
            "alias_set_hash": "",
        }
        row["alias_row_hash"] = canonical_row_hash(row, {"alias_row_hash", "alias_set_hash"})
        rows.append(row)
    rows.sort(key=lambda row: (row["source_language_code"], row["script_code"], row["territory_codes"]))
    alias_set_hash = sha256_bytes(("\n".join(row["alias_row_hash"] for row in rows) + "\n").encode("ascii"))
    for row in rows:
        row["alias_set_hash"] = alias_set_hash
    return rows, alias_set_hash


def tag_components(tag: str) -> tuple[str, str, str]:
    parts = [part for part in tag.strip().split("-") if part]
    if not parts:
        return "", "", ""
    language = parts[0].casefold()
    script = next((part.title() for part in parts[1:] if len(part) == 4 and part.isalpha()), "")
    territory = next(
        (
            part.upper()
            for part in parts[1:]
            if (len(part) == 2 and part.isalpha()) or (len(part) == 3 and part.isdigit())
        ),
        "",
    )
    return language, script, territory


def target_representation(target: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "roster_target_id": target.get("roster_target_id", ""),
        "target_kind": target.get("target_kind", ""),
        "language_target_id": target.get("language_target_id"),
        "intervention_target_id": target.get("intervention_target_id"),
        "empirical_stratum_id": target.get("empirical_stratum_id"),
        "language_tags": target.get("language_tags", []),
        "language_variety_names": target.get("language_variety_names", []),
        "scripts_orthographies": target.get("scripts_orthographies", []),
        "territories_communities": target.get("territories_communities", []),
        "language_mode": target.get("language_mode", ""),
        "exactness": target.get("exactness", ""),
    }


def exact_profile_matches(
    target: Mapping[str, Any],
    profile_by_language_script: Mapping[tuple[str, str], Mapping[str, str]],
) -> list[Mapping[str, str]]:
    matched: dict[str, Mapping[str, str]] = {}
    for tag in target.get("language_tags", []):
        language, script, _ = tag_components(str(tag))
        if not language or not script:
            continue
        profile = profile_by_language_script.get((language, script.casefold()))
        if profile is not None:
            matched[profile["benchmark_profile_id"]] = profile
    return [matched[key] for key in sorted(matched)]


def validate_frozen_authorities(
    roster_path: Path,
    roster_receipt_path: Path,
    successor_universe_path: Path,
    successor_receipt_path: Path,
) -> dict[str, Any]:
    """Authenticate the complete frozen roster and its two upstream receipts."""
    expected_files = (
        (roster_path, PINNED_ROSTER_SHA256, "successor target roster"),
        (roster_receipt_path, PINNED_ROSTER_RECEIPT_SHA256, "successor target-roster receipt"),
        (successor_universe_path, PINNED_SUCCESSOR_UNIVERSE_SHA256, "successor universe"),
        (successor_receipt_path, PINNED_SUCCESSOR_RECEIPT_SHA256, "successor universe receipt"),
    )
    for path, expected_hash, label in expected_files:
        if sha256_file(path) != expected_hash:
            raise ValueError(f"{label} bytes do not match the pinned authority")
    roster = json.loads(roster_path.read_text(encoding="utf-8"))
    if set(roster) != ROSTER_TOP_FIELDS:
        raise ValueError("successor target roster has unknown or missing top-level fields")
    if roster.get("counts") != PINNED_ROSTER_COUNTS or roster.get("target_selector") != PINNED_TARGET_SELECTOR:
        raise ValueError("successor target roster declared counts or selectors are not the frozen contract")
    targets = roster.get("roster_targets")
    if not isinstance(targets, list) or len(targets) != 1266:
        raise ValueError("successor target roster must contain exactly 1,266 rows")
    if any(set(target) != ROSTER_TARGET_FIELDS for target in targets):
        raise ValueError("successor target roster row has unknown or missing fields")
    for target in targets:
        assertions = target.get("identity_assertions")
        if not isinstance(assertions, list) or any(
            not isinstance(assertion, dict)
            or set(assertion) != {"label", "aliases", "territory", "script_or_mode"}
            for assertion in assertions
        ):
            raise ValueError("successor target identity assertion has unknown or missing fields")
    if roster.get("expected_evaluation_kind_counts") != {
        "language_target_summary": 969,
        "legacy_package_intervention_summary": 1011,
        "typed_endpoint_stage_package_event": 1035,
        "successor_package_profile_summary": 13,
        "regional_empirical_stratum": 297,
    }:
        raise ValueError("successor target roster evaluation-kind counts mismatch")
    if any(
        set(row) != {
            "additivity", "bundle_ids", "chosen_by_bundle_order", "compatibility_status",
            "disposition", "evidence_ids", "intervention_target_identity_evidence_ids", "stratum_id",
        }
        for row in roster.get("collision_dispositions", [])
    ):
        raise ValueError("successor collision disposition has unknown or missing fields")
    computed_counts = {
        "roster_targets": len(targets),
        "language_targets": sum(target.get("target_kind") == "canonical_language_target" for target in targets),
        "regional_empirical_intervention_targets": sum(target.get("target_kind") == "regional_empirical_intervention_target" for target in targets),
        "production_applicable_targets": sum(target.get("production_applicable") is True for target in targets),
        "production_applicable_language_targets": sum(
            target.get("target_kind") == "canonical_language_target" and target.get("production_applicable") is True
            for target in targets
        ),
    }
    for key, value in computed_counts.items():
        if PINNED_ROSTER_COUNTS[key] != value:
            raise ValueError(f"successor target roster computed count mismatch: {key}")
    stratum_map = roster.get("stratum_to_target_mapping")
    if not isinstance(stratum_map, list) or len(stratum_map) != 297:
        raise ValueError("successor target roster must contain exactly 297 stratum mappings")
    if any(set(row) != {"stratum_id", "intervention_target_id", "mapping_cardinality"} for row in stratum_map):
        raise ValueError("successor stratum mapping has unknown or missing fields")
    empirical_pairs = {
        (str(target.get("empirical_stratum_id") or ""), str(target.get("intervention_target_id") or ""))
        for target in targets
        if target.get("target_kind") == "regional_empirical_intervention_target"
    }
    mapped_pairs = {(str(row["stratum_id"]), str(row["intervention_target_id"])) for row in stratum_map}
    if empirical_pairs != mapped_pairs or any(row["mapping_cardinality"] != "ONE_STRATUM_TO_ONE_INTERVENTION_TARGET" for row in stratum_map):
        raise ValueError("successor stratum mapping is not an exact one-to-one empirical-target mapping")

    roster_receipt = json.loads(roster_receipt_path.read_text(encoding="utf-8"))
    if (
        roster_receipt.get("schema") != "interlanguage/successor-target-roster-receipt/2.0.0"
        or roster_receipt.get("validation_passed") is not True
        or roster_receipt.get("snapshot_id") != roster.get("snapshot_id")
        or roster_receipt.get("snapshot_payload_sha256") != roster.get("snapshot_payload_sha256")
        or roster_receipt.get("counts") != PINNED_ROSTER_COUNTS
        or roster_receipt.get("target_selector") != PINNED_TARGET_SELECTOR
        or roster_receipt.get("roster_artifact") != {
            "path": "structured/SUCCESSOR_TARGET_ROSTER_v2.json",
            "bytes": roster_path.stat().st_size,
            "sha256": PINNED_ROSTER_SHA256,
        }
    ):
        raise ValueError("successor target-roster receipt does not authenticate the frozen roster")
    successor_receipt = json.loads(successor_receipt_path.read_text(encoding="utf-8"))
    artifacts = {item.get("path"): item for item in successor_receipt.get("artifacts", [])}
    if (
        successor_receipt.get("schema") != "interlanguage/successor-universe-build-receipt/2.0.0"
        or successor_receipt.get("validation_passed") is not True
        or artifacts.get("structured/canonical_universe_successor_v2.json") != {
            "path": "structured/canonical_universe_successor_v2.json",
            "bytes": successor_universe_path.stat().st_size,
            "sha256": PINNED_SUCCESSOR_UNIVERSE_SHA256,
        }
        or successor_receipt.get("target_roster_binding", {}).get("sha256") != PINNED_ROSTER_SHA256
        or successor_receipt.get("target_roster_binding", {}).get("receipt_sha256") != PINNED_ROSTER_RECEIPT_SHA256
    ):
        raise ValueError("successor universe receipt does not authenticate the frozen universe and roster")
    successor = json.loads(successor_universe_path.read_text(encoding="utf-8"))
    if (
        successor.get("target_roster_binding", {}).get("sha256") != PINNED_ROSTER_SHA256
        or successor.get("target_roster_binding", {}).get("snapshot_id") != roster.get("snapshot_id")
    ):
        raise ValueError("successor universe does not cross-bind the frozen target roster")
    return roster


def build_bindings(
    roster_path: Path,
    profiles_path: Path,
    roster_receipt_path: Path | None = None,
    successor_universe_path: Path | None = None,
    successor_receipt_path: Path | None = None,
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    roster_bytes_hash = sha256_file(roster_path)
    if roster_receipt_path is None or successor_universe_path is None or successor_receipt_path is None:
        raise ValueError("all frozen roster and successor authority receipts are required")
    roster = validate_frozen_authorities(
        roster_path,
        roster_receipt_path,
        successor_universe_path,
        successor_receipt_path,
    )
    if roster.get("schema") != "interlanguage/successor-target-roster/2.0.0":
        raise ValueError("successor target roster schema is not pinned v2")
    payload = {
        key: value
        for key, value in roster.items()
        if key not in {"snapshot_id", "snapshot_payload_sha256"}
    }
    payload_hash = sha256_bytes(canonical_json_bytes(payload))
    if roster.get("snapshot_payload_sha256") != payload_hash:
        raise ValueError("successor target roster payload hash mismatch")
    expected_snapshot_id = f"successor-target-roster:sha256:{payload_hash}"
    if roster.get("snapshot_id") != expected_snapshot_id:
        raise ValueError("successor target roster snapshot ID mismatch")
    targets = roster.get("roster_targets")
    if not isinstance(targets, list) or not targets:
        raise ValueError("successor roster has no roster_targets")
    target_ids = [str(target.get("roster_target_id", "")) for target in targets]
    if any(not target_id for target_id in target_ids) or len(target_ids) != len(set(target_ids)):
        raise ValueError("successor roster target IDs are blank or duplicated")
    for target in targets:
        stated_row_hash = str(target.get("roster_row_sha256", ""))
        actual_row_hash = canonical_row_hash(target, {"roster_row_sha256"})
        if stated_row_hash != actual_row_hash:
            raise ValueError(f"successor roster row hash mismatch: {target.get('roster_target_id')}")
        expected_requirement = (
            "DIRECT_EXACT_PROFILE_OR_EXPLICIT_MISSING_UNRANKED"
            if target.get("production_applicable") is True
            else "EXPLICIT_CONTEXT_OR_MISSING_UNRANKED_ONLY"
        )
        if target.get("profile_binding_requirement") != expected_requirement:
            raise ValueError(f"successor roster profile-binding requirement mismatch: {target.get('roster_target_id')}")
    roster_snapshot_id = expected_snapshot_id

    profiles = read_csv(profiles_path)
    if len(profiles) != 203:
        raise ValueError("direct measurement-profile registry must contain 203 rows")
    profile_set_hashes = {row["profile_set_hash"] for row in profiles}
    tokenization_hashes = {row["tokenization_measurement_set_sha256"] for row in profiles}
    if len(profile_set_hashes) != 1 or len(tokenization_hashes) != 1:
        raise ValueError("measurement-profile registry hashes are inconsistent")
    profile_file_hash = sha256_file(profiles_path)
    profile_set_hash = next(iter(profile_set_hashes))
    tokenization_hash = next(iter(tokenization_hashes))
    profile_by_language_script: dict[tuple[str, str], Mapping[str, str]] = {}
    for profile in profiles:
        key = (profile["language_code"].casefold(), profile["script_code"].casefold())
        if key in profile_by_language_script:
            raise ValueError(f"ambiguous direct profiles for exact code/script {key}")
        profile_by_language_script[key] = profile

    bindings: list[dict[str, str]] = []
    for target in sorted(targets, key=lambda item: item["roster_target_id"]):
        target_id = str(target["roster_target_id"])
        components = [tag_components(str(tag)) for tag in target.get("language_tags", [])]
        languages = sorted({language for language, _, _ in components if language})
        scripts = sorted({script for _, script, _ in components if script})
        territories = sorted({territory for _, _, territory in components if territory})
        matches = (
            exact_profile_matches(target, profile_by_language_script)
            if target.get("target_kind") == "canonical_language_target"
            else []
        )
        direct = len(matches) == 1
        profile = matches[0] if direct else None
        production_applicable = target.get("production_applicable") is True
        point_eligible = direct and production_applicable
        representation_id = "repr:" + sha256_bytes(canonical_json_bytes(target_representation(target)))[:24]
        if point_eligible:
            unavailable_reason = ""
        elif direct:
            unavailable_reason = "NOT_PRODUCTION_APPLICABLE"
        elif not production_applicable:
            unavailable_reason = "NOT_PRODUCTION_APPLICABLE_AND_NO_DIRECT_ALIGNED_PROFILE"
        elif target.get("target_kind") != "canonical_language_target":
            unavailable_reason = "TARGET_HAS_NO_DIRECT_LANGUAGE_SCRIPT_PROFILE"
        elif len(matches) > 1:
            unavailable_reason = "AMBIGUOUS_EXACT_CODE_SCRIPT_PROFILES"
        else:
            unavailable_reason = "NO_DIRECT_ALIGNED_PROFILE"
        row: dict[str, str] = {
            "roster_snapshot_id": roster_snapshot_id,
            "successor_roster_file_sha256": roster_bytes_hash,
            "roster_target_id": target_id,
            "target_kind": str(target.get("target_kind", "")),
            "language_target_id": str(target.get("language_target_id") or ""),
            "intervention_target_id": str(target.get("intervention_target_id") or ""),
            "production_applicable": "true" if production_applicable else "false",
            "target_representation_id": representation_id,
            "target_language_or_variety_code": ";".join(languages),
            "target_script_code": ";".join(scripts),
            "target_territory_code": ";".join(territories),
            "benchmark_profile_id": profile["benchmark_profile_id"] if profile else "",
            "profile_measurement_kind": "DIRECT_ALIGNED_BENCHMARK" if profile else "NONE",
            "profile_match_scope": "ALIGNED_LANGUAGE_SCRIPT_TOKENIZATION_PROXY" if profile else "NONE",
            "binding_method": "EXACT_BCP47_LANGUAGE_SUBTAG_AND_EXPLICIT_SCRIPT" if profile else "NO_EXACT_CODE_SCRIPT_MATCH",
            "binding_status": "DIRECT_PROFILE_BOUND" if profile else "NO_DIRECT_PROFILE",
            "order_b_eligible": "true" if point_eligible else "false",
            "unavailable_reason": unavailable_reason,
            "sensitivity_control_status": "COMMON_ENVELOPE_AVAILABLE_SEPARATELY_NOT_FOR_POINT_ORDER",
            "tokenization_measurement_set_sha256": tokenization_hash,
            "measurement_profile_registry_file_sha256": profile_file_hash,
            "measurement_profile_set_hash": profile_set_hash,
            "direct_measurement_row_hash": profile["direct_measurement_row_hash"] if profile else "",
            "target_roster_row_hash": str(target["roster_row_sha256"]),
            "binding_row_hash": "",
            "binding_set_hash": "",
        }
        row["binding_row_hash"] = canonical_row_hash(row, {"binding_row_hash", "binding_set_hash"})
        bindings.append(row)

    binding_set_hash = sha256_bytes(("\n".join(row["binding_row_hash"] for row in bindings) + "\n").encode("ascii"))
    for row in bindings:
        row["binding_set_hash"] = binding_set_hash
    counts = {
        "targets": len(bindings),
        "direct_profile_bound": sum(row["binding_status"] == "DIRECT_PROFILE_BOUND" for row in bindings),
        "no_direct_profile": sum(row["binding_status"] == "NO_DIRECT_PROFILE" for row in bindings),
        "production_applicable": sum(row["production_applicable"] == "true" for row in bindings),
        "production_direct_profile_eligible": sum(row["order_b_eligible"] == "true" for row in bindings),
        "production_missing_unranked": sum(
            row["production_applicable"] == "true" and row["order_b_eligible"] == "false"
            for row in bindings
        ),
    }
    return bindings, {
        "schema_version": BINDING_SCHEMA_VERSION,
        "binding_protocol_version": BINDING_PROTOCOL_VERSION,
        "snapshot_utc": SNAPSHOT_UTC,
        "roster_snapshot_id": roster_snapshot_id,
        "successor_roster_file_sha256": roster_bytes_hash,
        "measurement_profile_registry_file_sha256": profile_file_hash,
        "measurement_profile_set_hash": profile_set_hash,
        "tokenization_measurement_set_sha256": tokenization_hash,
        "binding_set_hash": binding_set_hash,
        "counts": counts,
        "status": "PASS",
        "notes": [
            "Every frozen successor roster target, including language and empirical intervention targets, has exactly one binding row.",
            "Only an exact language subtag plus explicit script subtag can bind a direct measured profile.",
            "Region, language family, target name, prestige, need, population, and the common envelope do not create a binding.",
            "Targets without one exact direct profile remain missing and ineligible for Order-B point ranking.",
        ],
    }


def main(argv: Sequence[str] | None = None) -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--successor-roster", type=Path, default=root / "structured" / "SUCCESSOR_TARGET_ROSTER_v2.json")
    parser.add_argument("--successor-roster-receipt", type=Path, default=root / "qa" / "SUCCESSOR_TARGET_ROSTER_RECEIPT_20260901_v2.json")
    parser.add_argument("--successor-universe", type=Path, default=root / "structured" / "canonical_universe_successor_v2.json")
    parser.add_argument("--successor-universe-receipt", type=Path, default=root / "qa" / "SUCCESSOR_UNIVERSE_BUILD_RECEIPT_20260901_v2.json")
    parser.add_argument("--measurement-profiles", type=Path, default=root / "structured" / "standardized_compute_measurement_profiles.csv")
    parser.add_argument("--iso6393-table", type=Path, default=root / "qa" / "_standard_compute_tmp" / "iso-639-3.tab")
    parser.add_argument("--iso6393-macrolanguages", type=Path, default=root / "qa" / "_standard_compute_tmp" / "iso-639-3-macrolanguages.tab")
    parser.add_argument("--iana-language-subtag-registry", type=Path, default=root / "qa" / "_standard_compute_tmp" / "iana_language_subtag_registry.txt")
    parser.add_argument("--alias-crosswalk-output", type=Path, default=root / "structured" / "standardized_compute_language_alias_crosswalk.csv")
    parser.add_argument("--output", type=Path, default=root / "structured" / "standardized_compute_successor_target_bindings.csv")
    parser.add_argument("--receipt", type=Path, default=root / "qa" / "STANDARDIZED_COMPUTE_TARGET_BINDING_RECEIPT.json")
    args = parser.parse_args(argv)
    alias_rows, alias_set_hash = build_alias_crosswalk(
        args.iso6393_table.resolve(),
        args.iso6393_macrolanguages.resolve(),
        args.iana_language_subtag_registry.resolve(),
    )
    write_alias_csv(args.alias_crosswalk_output.resolve(), alias_rows)
    bindings, receipt = build_bindings(
        args.successor_roster.resolve(),
        args.measurement_profiles.resolve(),
        args.successor_roster_receipt.resolve(),
        args.successor_universe.resolve(),
        args.successor_universe_receipt.resolve(),
    )
    write_csv(args.output.resolve(), bindings)
    receipt["binding_registry_file_sha256"] = sha256_file(args.output.resolve())
    receipt["binding_registry_path"] = str(args.output.resolve())
    receipt["language_alias_crosswalk_file_sha256"] = sha256_file(args.alias_crosswalk_output.resolve())
    receipt["language_alias_crosswalk_set_hash"] = alias_set_hash
    args.receipt.resolve().write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="",
    )
    print(
        f"PASS bindings={receipt['counts']['targets']} direct={receipt['counts']['direct_profile_bound']} "
        f"missing={receipt['counts']['no_direct_profile']} set={receipt['binding_set_hash']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
