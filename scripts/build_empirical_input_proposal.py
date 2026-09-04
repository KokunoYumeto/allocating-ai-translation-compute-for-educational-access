#!/usr/bin/env python3
"""Build an evidence-readiness proposal from the canonical language universe.

This script is deliberately fail-closed.  It does not impute educational need,
resource scarcity, academic-language non-overlap, delivery reach, functional
use, stage cohorts, or endpoints.  It emits scorer-ready CSV rows only when an
exact target has all required identities and every factor is bound to public
low/base/high evidence.  The current canonical universe does not meet that
threshold, so its principal output is an exact, machine-readable gap ledger.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANONICAL = ROOT / "structured" / "canonical_universe_proposal.json"
DEFAULT_FACTOR_REGISTRY = ROOT / "scripts" / "INTRINSIC_FACTOR_REGISTRY.json"
DEFAULT_OER = ROOT / "structured" / "oer_scarcity_evidence.json"
DEFAULT_BASELINE_POLICY = ROOT / "structured" / "baseline_resource_policy.json"
DEFAULT_EXCLUSION_REGISTRY = ROOT / "structured" / "program_output_exclusion_register.json"
DEFAULT_JSON_OUTPUT = ROOT / "structured" / "empirical_input_gap_ledger.json"
DEFAULT_CSV_OUTPUT = ROOT / "structured" / "empirical_input_gap_ledger.csv"
DEFAULT_READY_CANDIDATES = ROOT / "structured" / "empirical_candidates_ready.csv"
DEFAULT_READY_FACTORS = ROOT / "structured" / "empirical_factor_sources_ready.csv"

CANONICAL_SCHEMA = "interlanguage/global-educational-access-canonical-universe/1.0.0"
LEDGER_SCHEMA = "interlanguage/empirical-input-gap-ledger/1.0.0"

# The executable scorer accepts these columns.  Importing the scorer would make
# this evidence census depend on executable ranking code, so the public contract
# is reproduced here and checked against the script before output is written.
CANDIDATE_FIELDS = (
    "candidate_id",
    "target_label",
    "language_target_id",
    "language_target_label",
    "territory_cell_id",
    "country_code",
    "measure_class",
    "language_need_measure_class",
    "endpoint_id",
    "horizon_months",
    "learner_stage",
    "subject_domain",
    "package_id",
    "delivery_format",
    "stratum_compatibility_key",
    "eligibility_status",
    "rankability_status",
    "universe_version",
    "overlap_group_id",
    "overlap_rule",
    "overlap_evidence_source_id",
    "overlap_evidence_source_url",
    "overlap_evidence_source_class",
    "overlap_evidence_is_public",
)

FACTOR_FIELDS = (
    "candidate_id",
    "factor_name",
    "factor_role",
    "conditional_order",
    "factor_measure_class",
    "low",
    "base",
    "high",
    "unit",
    "value_scale",
    "source_id",
    "source_url",
    "source_class",
    "is_public",
    "country_context_field",
    "resource_audit_group_hash",
    "resource_finding_status",
    "baseline_policy_version",
    "baseline_observation_date",
    "baseline_functional_route_id",
    "baseline_access_endpoint_id",
    "program_exclusion_registry_hash",
)

GAP_FACTORS = (
    "education_need",
    "resource_gap",
    "academic_nonoverlap",
    "standardized_access_gain",
    "accessible_delivery_reach",
    "conditional_functional_use",
)

LEDGER_CSV_FIELDS = (
    "language_target_id",
    "language_target_label",
    "language_tag",
    "country_identity_status",
    "country_region_subtag",
    "stage_identity_status",
    "stage_scope_values_json",
    "endpoint_identity_status",
    "candidate_identity_ready",
    "eligible_population_measure_count",
    "eligible_population_measure_ids_json",
    "population_factor_status",
    "conditional_chain_status",
    "education_need_status",
    "resource_gap_status",
    "resource_evidence_locator_target_id",
    "academic_nonoverlap_status",
    "standardized_access_gain_status",
    "accessible_delivery_reach_status",
    "conditional_functional_use_status",
    "scorer_candidate_row_ready",
    "scorer_factor_chain_ready",
    "rankable_now",
    "package_intervention_ids_json",
    "source_candidate_ids_json",
    "missing_requirements_json",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8") + b"\n")


def write_csv(path: Path, fields: Iterable[str], rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in writer.fieldnames})


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def exact_region_subtags(language_tags: Iterable[str]) -> list[str]:
    regions: set[str] = set()
    for tag in language_tags:
        core = str(tag).split(":", 1)[0]
        for subtag in core.split("-")[1:]:
            if re.fullmatch(r"[A-Z]{2}|[0-9]{3}", subtag):
                regions.add(subtag)
    return sorted(regions)


def normalized_target_key(language_target_id: str) -> str:
    value = language_target_id.removeprefix("lang:")
    return value.split(":", 1)[0]


def exact_scorer_stage_values(package_rows: Iterable[Mapping[str, Any]]) -> list[str]:
    # Only literal closed-registry values count.  Free-text ranges are locators,
    # not an authority to split people across stages or invent an ISCED mapping.
    return sorted(
        {
            str(stage)
            for package in package_rows
            for stage in package.get("learner_stage_scopes", [])
            if re.fullmatch(r"E[0-6]", str(stage))
        }
    )


def all_stage_scope_values(package_rows: Iterable[Mapping[str, Any]]) -> list[str]:
    return sorted(
        {
            str(stage)
            for package in package_rows
            for stage in package.get("learner_stage_scopes", [])
            if str(stage).strip()
        }
    )


def verify_scorer_contract(scorer_path: Path) -> None:
    source = scorer_path.read_text(encoding="utf-8")
    for field in (*CANDIDATE_FIELDS, *FACTOR_FIELDS):
        if f'"{field}"' not in source:
            raise ValueError(f"scorer contract no longer exposes expected field {field!r}")


def build(
    canonical_path: Path,
    factor_registry_path: Path,
    oer_path: Path,
    baseline_policy_path: Path,
    exclusion_registry_path: Path,
) -> dict[str, Any]:
    canonical = load_json(canonical_path)
    if canonical.get("schema_version") != CANONICAL_SCHEMA:
        raise ValueError(f"unsupported canonical schema: {canonical.get('schema_version')!r}")
    if not canonical.get("validation", {}).get("validation_passed"):
        raise ValueError("canonical universe validation_passed is not true")

    registry = load_json(factor_registry_path)
    registered_factors = {row["factor_name"] for row in registry.get("factors", [])}
    missing_registry = sorted(set(("population", *GAP_FACTORS)) - registered_factors)
    if missing_registry:
        raise ValueError(f"closed factor registry lacks required factors: {missing_registry}")

    policy = load_json(baseline_policy_path)
    exclusion = load_json(exclusion_registry_path)
    if policy.get("baseline_policy_version") != exclusion.get("baseline_policy_version"):
        raise ValueError("baseline policy and programme-exclusion registry do not agree")

    oer = load_json(oer_path) if oer_path.exists() else {"targets": []}
    oer_by_target = {str(row.get("target_id")): row for row in oer.get("targets", [])}
    measures = {row["population_measure_id"]: row for row in canonical["population_measures"]}
    sources = {row["source_id"]: row for row in canonical["source_registry"]}
    packages_by_language: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for package in canonical["package_interventions"]:
        for language_target_id in package["language_target_ids"]:
            packages_by_language[language_target_id].append(package)

    targets = [row for row in canonical["language_targets"] if row.get("rankable_population_basis") is True]
    expected = canonical.get("validation", {}).get("targets_with_direct_typed_population_basis")
    if len(targets) != expected:
        raise ValueError(f"typed-population target count {len(targets)} differs from canonical validation {expected}")

    rows: list[dict[str, Any]] = []
    ready_candidates: list[dict[str, str]] = []
    ready_factors: list[dict[str, str]] = []

    for target in sorted(targets, key=lambda row: row["language_target_id"]):
        language_target_id = target["language_target_id"]
        package_rows = sorted(
            packages_by_language.get(language_target_id, []), key=lambda row: row["package_intervention_id"]
        )
        regions = exact_region_subtags(target.get("language_tags", []))
        stage_values = all_stage_scope_values(package_rows)
        exact_stages = exact_scorer_stage_values(package_rows)

        # canonical package_interventions intentionally have no endpoint_id or
        # horizon_months.  A prose access aspiration is not an executable endpoint.
        endpoint_values: list[str] = []
        country_status = "EXACT_BCP47_REGION_IDENTITY" if len(regions) == 1 else "MISSING_OR_AMBIGUOUS_COUNTRY_IDENTITY"
        stage_status = "EXACT_CLOSED_STAGE_IDENTITY" if len(exact_stages) == 1 else "MISSING_EXACT_CLOSED_STAGE_IDENTITY"
        endpoint_status = "MISSING_EXACT_ENDPOINT_AND_HORIZON_IDENTITY"
        identity_ready = country_status == "EXACT_BCP47_REGION_IDENTITY" and stage_status == "EXACT_CLOSED_STAGE_IDENTITY" and bool(endpoint_values)

        eligible_measures = [
            measures[measure_id]
            for measure_id in target.get("population_measure_ids", [])
            if measures[measure_id].get("rank_eligibility") == "eligible_direct_typed_measure"
        ]
        if not eligible_measures:
            raise ValueError(f"{language_target_id} was marked rankable_population_basis without an eligible measure")
        if len(eligible_measures) > 1:
            population_status = "MULTIPLE_NONADDITIVE_LANGUAGE_MEASURES_REQUIRE_STRATUM_PARTITION"
        else:
            population_status = "LANGUAGE_POPULATION_LOCATOR_ONLY_STAGE_ENDPOINT_DENOMINATOR_MISSING"

        oer_key = normalized_target_key(language_target_id)
        oer_locator = oer_by_target.get(oer_key)
        if oer_locator is None:
            resource_status = "MISSING_EXACT_STAGE_SUBJECT_ROUTE_RESOURCE_AUDIT"
            oer_locator_id = ""
        else:
            resource_status = "CATEGORICAL_TARGET_LOCATOR_ONLY_NOT_A_QUANTITATIVE_STAGE_ROUTE_FACTOR"
            oer_locator_id = oer_key

        factor_status = {
            "education_need": "MISSING_PUBLIC_CONDITIONAL_RATE_FOR_EXACT_COUNTRY_STAGE_ENDPOINT_DENOMINATOR",
            "resource_gap": resource_status,
            "academic_nonoverlap": "MISSING_PUBLIC_LOW_BASE_HIGH_NONOVERLAP_FOR_EXACT_CAPABILITY_STRATUM",
            "standardized_access_gain": "MISSING_PUBLIC_LOW_BASE_HIGH_GAIN_FOR_FIXED_PACKAGE_ENDPOINT_HORIZON",
            "accessible_delivery_reach": "MISSING_ROUTE_SPECIFIC_LOW_BASE_HIGH_REACH_FOR_EXACT_STRATUM",
            "conditional_functional_use": "MISSING_ENDPOINT_SPECIFIC_LOW_BASE_HIGH_FUNCTIONAL_USE_RATE",
        }
        missing_requirements = [
            "exact_closed_learner_stage",
            "exact_functional_access_endpoint",
            "fixed_horizon_months",
            "fixed_subject_or_canon_package",
            "stage_endpoint_compatible_population_denominator",
            "documented_conditional_denominator_chain",
            *[f"public_factor:{name}" for name in GAP_FACTORS],
        ]
        if len(regions) != 1:
            missing_requirements.append("exact_country_or_territory_cell")
        if len(eligible_measures) > 1:
            missing_requirements.append("nonoverlapping_population_measure_selection_or_partition")

        row = {
            "language_target_id": language_target_id,
            "language_target_label": " / ".join(target.get("language_variety_names", [])),
            "language_tag": "|".join(target.get("language_tags", [])),
            "country_identity_status": country_status,
            "country_region_subtag": regions[0] if len(regions) == 1 else "",
            "stage_identity_status": stage_status,
            "stage_scope_values": stage_values,
            "exact_scorer_stage_values": exact_stages,
            "endpoint_identity_status": endpoint_status,
            "endpoint_values": endpoint_values,
            "candidate_identity_ready": identity_ready,
            "eligible_population_measure_count": len(eligible_measures),
            "eligible_population_measure_ids": [m["population_measure_id"] for m in eligible_measures],
            "eligible_population_measures": eligible_measures,
            "population_factor_status": population_status,
            "conditional_chain_status": "MISSING_EXPLICIT_CONDITIONAL_DENOMINATOR_CHAIN",
            "factor_evidence_status": factor_status,
            "resource_evidence_locator_target_id": oer_locator_id,
            "resource_evidence_locator": oer_locator,
            "scorer_candidate_row_ready": False,
            "scorer_factor_chain_ready": False,
            "rankable_now": False,
            "package_intervention_ids": [p["package_intervention_id"] for p in package_rows],
            "source_candidate_ids": sorted(set(target.get("source_candidate_ids", []))),
            "missing_requirements": sorted(set(missing_requirements)),
        }
        rows.append(row)

    # No row may pass merely because it has a language population.  Any future
    # ready row must also have an exact identity and a complete evidence chain.
    for row in rows:
        if row["scorer_candidate_row_ready"] or row["scorer_factor_chain_ready"] or row["rankable_now"]:
            raise ValueError("builder attempted to emit an empirical rank before all evidence gates passed")

    counts = {
        "typed_population_targets": len(rows),
        "exact_country_identities": sum(row["country_identity_status"] == "EXACT_BCP47_REGION_IDENTITY" for row in rows),
        "exact_closed_stage_identities": sum(row["stage_identity_status"] == "EXACT_CLOSED_STAGE_IDENTITY" for row in rows),
        "exact_endpoint_horizon_identities": sum(bool(row["endpoint_values"]) for row in rows),
        "complete_country_stage_endpoint_identities": sum(bool(row["candidate_identity_ready"]) for row in rows),
        "single_direct_population_measure": sum(row["eligible_population_measure_count"] == 1 for row in rows),
        "multiple_nonadditive_direct_population_measures": sum(row["eligible_population_measure_count"] > 1 for row in rows),
        "resource_target_locators_only": sum(bool(row["resource_evidence_locator_target_id"]) for row in rows),
        "complete_empirical_factor_chains": 0,
        "scorer_ready_candidate_rows": len(ready_candidates),
        "scorer_ready_factor_rows": len(ready_factors),
        "rankings_produced": 0,
    }

    document = {
        "schema": LEDGER_SCHEMA,
        "artifact_status": "evidence_gap_ledger_not_a_ranking",
        "purpose": "map the canonical typed-population universe to the executable scorer contract without imputing missing identities or factors",
        "input_manifest": {
            "canonical_universe": {"path": canonical_path.name, "bytes": canonical_path.stat().st_size, "sha256": sha256_file(canonical_path)},
            "factor_registry": {"path": factor_registry_path.name, "bytes": factor_registry_path.stat().st_size, "sha256": sha256_file(factor_registry_path)},
            "oer_locator_audit": {"path": oer_path.name, "bytes": oer_path.stat().st_size, "sha256": sha256_file(oer_path)},
            "baseline_policy": {"path": baseline_policy_path.name, "bytes": baseline_policy_path.stat().st_size, "sha256": sha256_file(baseline_policy_path)},
            "program_exclusion_registry": {"path": exclusion_registry_path.name, "bytes": exclusion_registry_path.stat().st_size, "sha256": sha256_file(exclusion_registry_path)},
        },
        "factor_registry_version": registry.get("registry_version"),
        "baseline_policy_version": policy.get("baseline_policy_version"),
        "rules": {
            "country_identity": "one exact BCP47 region subtag; no country inferred from prose",
            "stage_identity": "one literal E0-E6 closed-registry value; free-text ranges are retained as locators only",
            "endpoint_identity": "an explicit endpoint_id and horizon are required; neither is present in canonical package_interventions",
            "population": "language populations remain locators until aligned to an exact stage/endpoint denominator; nonadditive measures are never summed",
            "factors": "every factor requires public low/base/high evidence and a documented conditional denominator chain",
            "resource_locator": "categorical OER evidence is a search locator, not a quantitative resource_gap factor",
            "missingness": "missing is never zero, one-half, a midpoint, a score penalty, or an implicit negative control",
            "program_outputs": "programme/local outputs are excluded from all need, benefit, cost, score and rank inputs",
        },
        "required_factor_chain": ["population", *GAP_FACTORS],
        "counts": counts,
        "complete_identity_language_target_ids": [row["language_target_id"] for row in rows if row["candidate_identity_ready"]],
        "scorer_ready_candidate_rows": ready_candidates,
        "scorer_ready_factor_rows": ready_factors,
        "rows": rows,
    }
    document["payload_sha256"] = hashlib.sha256(canonical_json_bytes(document["rows"])).hexdigest().upper()
    return document


def csv_projection(row: Mapping[str, Any]) -> dict[str, Any]:
    factors = row["factor_evidence_status"]
    return {
        "language_target_id": row["language_target_id"],
        "language_target_label": row["language_target_label"],
        "language_tag": row["language_tag"],
        "country_identity_status": row["country_identity_status"],
        "country_region_subtag": row["country_region_subtag"],
        "stage_identity_status": row["stage_identity_status"],
        "stage_scope_values_json": json.dumps(row["stage_scope_values"], ensure_ascii=False, separators=(",", ":")),
        "endpoint_identity_status": row["endpoint_identity_status"],
        "candidate_identity_ready": str(row["candidate_identity_ready"]).lower(),
        "eligible_population_measure_count": row["eligible_population_measure_count"],
        "eligible_population_measure_ids_json": json.dumps(row["eligible_population_measure_ids"], separators=(",", ":")),
        "population_factor_status": row["population_factor_status"],
        "conditional_chain_status": row["conditional_chain_status"],
        "education_need_status": factors["education_need"],
        "resource_gap_status": factors["resource_gap"],
        "resource_evidence_locator_target_id": row["resource_evidence_locator_target_id"],
        "academic_nonoverlap_status": factors["academic_nonoverlap"],
        "standardized_access_gain_status": factors["standardized_access_gain"],
        "accessible_delivery_reach_status": factors["accessible_delivery_reach"],
        "conditional_functional_use_status": factors["conditional_functional_use"],
        "scorer_candidate_row_ready": "false",
        "scorer_factor_chain_ready": "false",
        "rankable_now": "false",
        "package_intervention_ids_json": json.dumps(row["package_intervention_ids"], separators=(",", ":")),
        "source_candidate_ids_json": json.dumps(row["source_candidate_ids"], separators=(",", ":")),
        "missing_requirements_json": json.dumps(row["missing_requirements"], separators=(",", ":")),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical", type=Path, default=DEFAULT_CANONICAL)
    parser.add_argument("--factor-registry", type=Path, default=DEFAULT_FACTOR_REGISTRY)
    parser.add_argument("--oer", type=Path, default=DEFAULT_OER)
    parser.add_argument("--baseline-policy", type=Path, default=DEFAULT_BASELINE_POLICY)
    parser.add_argument("--exclusion-registry", type=Path, default=DEFAULT_EXCLUSION_REGISTRY)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--csv-output", type=Path, default=DEFAULT_CSV_OUTPUT)
    parser.add_argument("--ready-candidates-output", type=Path, default=DEFAULT_READY_CANDIDATES)
    parser.add_argument("--ready-factors-output", type=Path, default=DEFAULT_READY_FACTORS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    verify_scorer_contract(ROOT / "scripts" / "needs_access_ranking.py")
    document = build(
        args.canonical,
        args.factor_registry,
        args.oer,
        args.baseline_policy,
        args.exclusion_registry,
    )
    write_json(args.json_output, document)
    write_csv(args.csv_output, LEDGER_CSV_FIELDS, (csv_projection(row) for row in document["rows"]))
    write_csv(args.ready_candidates_output, CANDIDATE_FIELDS, document["scorer_ready_candidate_rows"])
    write_csv(args.ready_factors_output, FACTOR_FIELDS, document["scorer_ready_factor_rows"])
    print(json.dumps({
        "status": "PASS",
        "ledger_json": str(args.json_output),
        "ledger_csv": str(args.csv_output),
        "ready_candidate_rows": document["counts"]["scorer_ready_candidate_rows"],
        "ready_factor_rows": document["counts"]["scorer_ready_factor_rows"],
        "rankings_produced": 0,
        "counts": document["counts"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
