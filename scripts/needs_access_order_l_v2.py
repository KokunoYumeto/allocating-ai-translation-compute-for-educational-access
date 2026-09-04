#!/usr/bin/env python3
"""Versioned Order-L pair: L-ID bounds and L-M model-conditional need.

This module is additive.  It does not alter or relax the strict conditional-chain
implementation in ``needs_access_ranking.py`` (the L-C lane).  L-ID consumes
finite public population ceilings and construct-valid need bounds.  L-M uses one
common hierarchical latent functional-access-need model for every exact target
and emits a complete public joint-draw grid.

Only Python's standard library is used.  The deterministic sampler is defined by
SHA-256-addressed uniforms and a frozen Box-Muller/Laplace approximation; it is a
transparent reference implementation, not a claim that sparse empirical need is
directly point identified.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import urlparse


SCHEMA_VERSION = "interlanguage/order-l-pair/2.1.0"
MODEL_VERSION = "order-l-hierarchical-functional-need/2.1.0"
DRAW_ALGORITHM_VERSION = "sha256-box-muller-laplace/1.0.0"
PRODUCTION_EDITION_REGISTRY_PATH = "structured/SUCCESSOR_EDITION_TARGET_REGISTRY_v3.csv"
PRODUCTION_EVIDENCE_MAP_PATH = "structured/SUCCESSOR_EVIDENCE_IDENTITY_TO_EDITION_v3.csv"
DEFAULT_PRIOR_REGISTRY_PATH = Path(__file__).resolve().with_name("ORDER_L_V2_PRIOR_REGISTRY.json")
DEFAULT_REASON_REGISTRY_PATH = Path(__file__).resolve().with_name("ORDER_L_V2_REASON_CODE_REGISTRY.json")
REFERENCE_PRIOR_FAMILY = "reference_common"
REQUIRED_PRIOR_FAMILIES = frozenset(
    {
        "reference_common",
        "diffuse_common",
        "optimistic_access_common",
        "pessimistic_access_common",
        "assignment_sparse_common",
        "assignment_concentrated_common",
    }
)

CELL_FIELDS = (
    "cell_id",
    "person_profile_id",
    "edition_target_id",
    "edition_target_label",
    "learner_stage_id",
    "functional_access_endpoint_id",
    "benefit_unit",
    "population_denominator_id",
    "population_lower_bound",
    "population_mode",
    "population_upper_bound",
    "population_resolution_status",
    "population_bound_reason_code",
    "assignment_mode",
    "assignment_atom_id",
    "assignment_weight",
    "assignment_within_atom_weight",
    "assignment_reason_code",
    "id_bound_method",
    "id_need_lower_bound",
    "id_need_upper_bound",
    "id_bound_reason_code",
    "evidence_tier",
    "evidence_reason_code",
    "eligibility_status",
    "eligibility_reason_code",
    "rankability_status",
    "rankability_reason_code",
    "universe_version",
    "universe_semantic_hash",
    "population_source_id",
    "population_source_url",
    "population_source_class",
    "population_is_public",
    "population_source_bytes",
    "population_source_sha256",
    "decision_source_id",
    "decision_source_url",
    "decision_source_class",
    "decision_is_public",
    "decision_source_bytes",
    "decision_source_sha256",
    "decision_derivation_id",
    "decision_derivation_json",
    "decision_derivation_bytes",
    "decision_derivation_sha256",
    "decision_binding_sha256",
)

ASSIGNMENT_EVIDENCE_FIELDS = (
    "assignment_evidence_id",
    "person_profile_id",
    "assignment_atom_id",
    "assignment_atom_ids_json",
    "evidence_mode",
    "numerator_count",
    "lower_count",
    "upper_count",
    "denominator_count",
    "compatibility_group_id",
    "compatibility_mode",
    "admission_reason_code",
    "source_id",
    "source_url",
    "source_class",
    "is_public",
    "source_bytes",
    "source_sha256",
    "derivation_id",
    "derivation_json",
    "derivation_bytes",
    "derivation_sha256",
)

OBSERVATION_FIELDS = (
    "observation_id",
    "cell_id",
    "observation_kind",
    "construct_id",
    "likelihood_family",
    "numerator_count",
    "denominator_count",
    "sampling_design",
    "source_scope",
    "source_stage_id",
    "source_endpoint_id",
    "measurement_model_id",
    "transport_model_id",
    "source_correlation_group_id",
    "source_effect_sd",
    "source_id",
    "source_url",
    "source_class",
    "is_public",
    "admission_reason_code",
    "source_bytes",
    "source_sha256",
    "derivation_id",
    "derivation_json",
    "derivation_bytes",
    "derivation_sha256",
)

MEASUREMENT_MODEL_FIELDS = (
    "measurement_model_id",
    "component_id",
    "model_family",
    "sensitivity_mean",
    "specificity_mean",
    "calibration_logit_sd",
    "source_id",
    "source_url",
    "source_class",
    "is_public",
    "admission_reason_code",
    "source_bytes",
    "source_sha256",
    "derivation_id",
    "derivation_json",
    "derivation_bytes",
    "derivation_sha256",
)

TRANSPORT_MODEL_FIELDS = (
    "transport_model_id",
    "model_family",
    "source_scope",
    "source_stage_id",
    "source_endpoint_id",
    "target_stage_id",
    "target_endpoint_id",
    "logit_shift_mean",
    "logit_shift_sd",
    "source_id",
    "source_url",
    "source_class",
    "is_public",
    "admission_reason_code",
    "source_bytes",
    "source_sha256",
    "derivation_id",
    "derivation_json",
    "derivation_bytes",
    "derivation_sha256",
)

EVIDENCE_TIERS = frozenset(
    {
        "DIRECT_ENDPOINT",
        "BOUND_IDENTIFIED",
        "CALIBRATED_MODEL_ASSISTED",
        "TRANSPORTED_MODEL_ASSISTED",
        "PRIOR_DOMINANT",
        "DENOMINATOR_UNIDENTIFIED",
    }
)
ID_BOUND_METHODS = frozenset(
    {"logical_0_1", "supplied_construct_bound", "frechet_bound", "direct_endpoint_census", "structural_zero"}
)
OBSERVATION_KINDS = frozenset({"direct_endpoint_count", "component_proxy_count"})
SOURCE_SCOPES = frozenset({"exact_target", "ecological", "broader_cohort"})
SOURCE_CLASSES = frozenset({"public_empirical", "public_model", "synthetic_fixture"})
LIKELIHOOD_FAMILY = "binomial-logit-laplace/1.0.0"
MEASUREMENT_FAMILY = "misclassified-binomial-logit/1.0.0"
TRANSPORT_FAMILY = "additive-logit-normal/1.0.0"
ASSIGNMENT_MODES = frozenset({"fixed_direct", "latent_symmetric"})
ASSIGNMENT_EVIDENCE_MODES = frozenset({"complete_multinomial", "partial_interval_constraint"})
ASSIGNMENT_COMPATIBILITY_MODES = frozenset(
    {"MUTUALLY_EXCLUSIVE_EXHAUSTIVE", "OVERLAPPING_OR_NONEXHAUSTIVE_BOUNDS"}
)
REASON_CODE_GROUPS = {
    "population_resolution_status": frozenset(
        {"FINITE_BOUND_IDENTIFIED", "FINITE_CEILING_UNRESOLVED"}
    ),
    "population_bound_reason_code": frozenset(
        {
            "DIRECT_MUTUALLY_EXCLUSIVE_COHORT",
            "SOURCE_BOUND_TERRITORIAL_OR_COMMUNITY_CEILING",
            "SOURCE_BOUND_WORLD_CEILING",
        }
    ),
    "assignment_reason_code": frozenset(
        {"EXACT_FIXED_EXCLUSIVE_COHORT", "LATENT_SYMMETRIC_MUTUALLY_EXCLUSIVE_PARTITION"}
    ),
    "id_bound_reason_code": frozenset(
        {
            "LOGICAL_UNIT_INTERVAL",
            "PUBLIC_CONSTRUCT_BOUND",
            "PUBLIC_FRECHET_DERIVATION",
            "EXACT_DIRECT_ENDPOINT_CENSUS",
            "VERIFIED_STRUCTURAL_ZERO",
        }
    ),
    "eligibility_reason_code": frozenset(
        {"COMMON_MODEL_INCLUDED", "VERIFIED_STRUCTURAL_ZERO"}
    ),
    "rankability_status": frozenset(
        {"RANKABLE_COMMON_MODEL", "RANKABLE_STRUCTURAL_ZERO"}
    ),
    "rankability_reason_code": frozenset(
        {"COMPLETE_COMMON_MODEL_CELL", "VERIFIED_STRUCTURAL_ZERO"}
    ),
    "assignment_evidence_admission_reason_code": frozenset(
        {
            "COMPATIBLE_COMPLETE_MULTINOMIAL_CROSSTAB",
            "SOURCE_BOUND_PARTIAL_ASSIGNMENT_INTERVAL",
        }
    ),
    "observation_admission_reason_code": frozenset(
        {
            "EXACT_DIRECT_ENDPOINT_COUNT",
            "EXACT_COMPONENT_PROXY_WITH_MEASUREMENT",
            "TRANSPORTED_COMPONENT_PROXY_WITH_EXPLICIT_MODELS",
            "TRANSPORTED_DIRECT_ENDPOINT_WITH_EXPLICIT_TRANSPORT",
        }
    ),
    "cell_evidence_reason_code": frozenset(
        {
            "DIRECT_ENDPOINT_ROUTE",
            "PARTIAL_IDENTIFICATION_BOUND_ROUTE",
            "COMPONENT_MEASUREMENT_ROUTE",
            "EXPLICIT_TRANSPORT_ROUTE",
            "COMMON_PRIOR_ROUTE",
            "UNRESOLVED_DENOMINATOR_ROUTE",
        }
    ),
    "measurement_admission_reason_code": frozenset(
        {"EXPLICIT_COMPONENT_MEASUREMENT_MODEL"}
    ),
    "transport_admission_reason_code": frozenset(
        {"EXPLICIT_STAGE_ENDPOINT_TRANSPORT_MODEL"}
    ),
}


class OrderLModelError(ValueError):
    """Raised when an input cannot support the declared L-ID/L-M semantics."""


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _decimal(value: Any, *, label: str, required: bool = False) -> Decimal | None:
    raw = _text(value)
    if not raw:
        if required:
            raise OrderLModelError(f"{label} is required")
        return None
    try:
        result = Decimal(raw)
    except InvalidOperation as exc:
        raise OrderLModelError(f"{label} is not a decimal: {raw!r}") from exc
    if not result.is_finite():
        raise OrderLModelError(f"{label} must be finite")
    return result


def _truth(value: Any) -> bool:
    return _text(value).casefold() in {"1", "true", "yes", "y"}


def _fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, Decimal):
        if value == 0:
            return "0"
        result = format(value, "f")
        return result.rstrip("0").rstrip(".") if "." in result else result
    return str(value)


def _d(value: float) -> Decimal:
    return Decimal(format(value, ".15g"))


def _project(rows: Sequence[Mapping[str, Any]], fields: Sequence[str]) -> tuple[list[dict[str, str]], list[str]]:
    allowed = set(fields)
    unknown = sorted({str(key) for row in rows for key in row if key not in allowed})
    if unknown:
        raise OrderLModelError(
            "unknown or prohibited adapter fields fail closed: " + ", ".join(unknown)
        )
    return ([{field: _text(row.get(field)) for field in fields} for row in rows], [])


def read_csv(path: Path, expected_fields: Sequence[str] | None = None) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise OrderLModelError(f"{path} has no CSV header")
        if expected_fields is not None and tuple(reader.fieldnames) != tuple(expected_fields):
            unknown = sorted(set(reader.fieldnames) - set(expected_fields))
            missing = sorted(set(expected_fields) - set(reader.fieldnames))
            raise OrderLModelError(
                f"{path} header is not the exact frozen schema "
                f"(unknown={unknown}, missing={missing}, order_mismatch="
                f"{not unknown and not missing})"
            )
        return [dict(row) for row in reader]


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]], fields: Sequence[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = [{key: _fmt(value) for key, value in row.items()} for row in rows]
    if fields is None:
        fields = list(serialized[0]) if serialized else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="raise", lineterminator="\n")
        writer.writeheader()
        writer.writerows(serialized)


def _require_source(row: Mapping[str, str], *, prefix: str, allow_synthetic: bool) -> None:
    source_class = row[f"{prefix}source_class"]
    source_id = row[f"{prefix}source_id"]
    source_url = row[f"{prefix}source_url"]
    is_public = row[f"{prefix}is_public"]
    if source_class not in SOURCE_CLASSES:
        raise OrderLModelError(f"source_class must be one of {sorted(SOURCE_CLASSES)}")
    if source_class == "synthetic_fixture":
        if not allow_synthetic:
            raise OrderLModelError("synthetic inputs require --allow-synthetic")
    elif not _truth(is_public):
        raise OrderLModelError(f"public source {source_id!r} is not declared public")
    if not source_id or not source_url:
        raise OrderLModelError("every admitted source requires source_id and source_url")
    parsed = urlparse(source_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise OrderLModelError(f"source URL must be public HTTP(S): {source_url!r}")


def _require_content_addressed_source(
    row: Mapping[str, str], *, prefix: str, allow_synthetic: bool
) -> None:
    _require_source(row, prefix=prefix, allow_synthetic=allow_synthetic)
    byte_count = _decimal(
        row[f"{prefix}source_bytes"], label=f"{prefix}source_bytes", required=True
    )
    digest = row[f"{prefix}source_sha256"].casefold()
    if byte_count is None or byte_count != byte_count.to_integral_value() or byte_count <= 0:
        raise OrderLModelError(f"{prefix}source_bytes must be a positive integer")
    if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise OrderLModelError(f"{prefix}source_sha256 must be a SHA-256 hex digest")


def _require_derivation(
    row: Mapping[str, str], *, expected_payload: Mapping[str, Any], prefix: str = ""
) -> str:
    derivation_id = row[f"{prefix}derivation_id"]
    raw_json = row[f"{prefix}derivation_json"]
    if not derivation_id or not raw_json:
        raise OrderLModelError("every admitted declaration requires a derivation_id and derivation_json")
    try:
        document = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise OrderLModelError(f"{derivation_id} derivation_json is invalid") from exc
    canonical = canonical_json_bytes(document)
    if raw_json.encode("utf-8") != canonical:
        raise OrderLModelError(f"{derivation_id} derivation_json must use canonical JSON bytes")
    if document != expected_payload:
        raise OrderLModelError(f"{derivation_id} does not bind the declared decision fields")
    declared_bytes = _decimal(
        row[f"{prefix}derivation_bytes"],
        label=f"{derivation_id}.derivation_bytes",
        required=True,
    )
    if declared_bytes is None or declared_bytes != Decimal(len(canonical)):
        raise OrderLModelError(f"{derivation_id}.derivation_bytes does not match canonical bytes")
    digest = sha256_bytes(canonical)
    if row[f"{prefix}derivation_sha256"].casefold() != digest:
        raise OrderLModelError(f"{derivation_id}.derivation_sha256 does not match canonical bytes")
    return digest


def load_reason_registry(path: Path = DEFAULT_REASON_REGISTRY_PATH) -> tuple[dict[str, frozenset[str]], str]:
    raw = path.read_bytes()
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OrderLModelError(f"reason registry is invalid JSON: {path}") from exc
    allowed = {"schema", "model_version", "reason_code_groups"}
    if set(document) != allowed:
        raise OrderLModelError("reason registry has unknown or missing top-level fields")
    if document["schema"] != "interlanguage/order-l-v2-reason-code-registry/1.0.0":
        raise OrderLModelError("reason registry schema is not the frozen version")
    if document["model_version"] != MODEL_VERSION:
        raise OrderLModelError("reason registry model_version does not match the implementation")
    groups = {
        str(key): frozenset(str(item) for item in value)
        for key, value in document["reason_code_groups"].items()
    }
    if groups != REASON_CODE_GROUPS:
        raise OrderLModelError("reason registry does not exactly match the closed implementation codes")
    return groups, sha256_bytes(raw)


CELL_DECISION_BOUND_FIELDS = (
    "cell_id",
    "person_profile_id",
    "edition_target_id",
    "learner_stage_id",
    "functional_access_endpoint_id",
    "benefit_unit",
    "population_denominator_id",
    "population_lower_bound",
    "population_mode",
    "population_upper_bound",
    "population_resolution_status",
    "population_bound_reason_code",
    "assignment_mode",
    "assignment_atom_id",
    "assignment_weight",
    "assignment_within_atom_weight",
    "assignment_reason_code",
    "id_bound_method",
    "id_need_lower_bound",
    "id_need_upper_bound",
    "id_bound_reason_code",
    "eligibility_status",
    "eligibility_reason_code",
    "rankability_status",
    "rankability_reason_code",
    "universe_version",
    "universe_semantic_hash",
)

EVIDENCE_DERIVATION_FIELDS = {
    "assignment_evidence": tuple(
        field
        for field in ASSIGNMENT_EVIDENCE_FIELDS
        if field
        not in {
            "source_id", "source_url", "source_class", "is_public", "source_bytes",
            "source_sha256", "derivation_id", "derivation_json", "derivation_bytes",
            "derivation_sha256",
        }
    ),
    "observation": tuple(
        field
        for field in OBSERVATION_FIELDS
        if field
        not in {
            "source_id", "source_url", "source_class", "is_public", "source_bytes",
            "source_sha256", "derivation_id", "derivation_json", "derivation_bytes",
            "derivation_sha256",
        }
    ),
    "measurement_model": tuple(
        field
        for field in MEASUREMENT_MODEL_FIELDS
        if field
        not in {
            "source_id", "source_url", "source_class", "is_public", "source_bytes",
            "source_sha256", "derivation_id", "derivation_json", "derivation_bytes",
            "derivation_sha256",
        }
    ),
    "transport_model": tuple(
        field
        for field in TRANSPORT_MODEL_FIELDS
        if field
        not in {
            "source_id", "source_url", "source_class", "is_public", "source_bytes",
            "source_sha256", "derivation_id", "derivation_json", "derivation_bytes",
            "derivation_sha256",
        }
    ),
}


def cell_decision_derivation_payload(row: Mapping[str, Any]) -> dict[str, Any]:
    """Return the exact decision payload that a cell derivation must bind."""
    return {
        "schema": "interlanguage/order-l-cell-decision-derivation/1.0.0",
        "fields": {field: _text(row.get(field)) for field in CELL_DECISION_BOUND_FIELDS},
    }


def evidence_derivation_payload(record_type: str, row: Mapping[str, Any]) -> dict[str, Any]:
    """Return an exact admission payload for one evidence/model registry row."""
    if record_type not in EVIDENCE_DERIVATION_FIELDS:
        raise OrderLModelError(f"unknown evidence derivation record type: {record_type}")
    return {
        "schema": "interlanguage/order-l-evidence-admission-derivation/1.0.0",
        "record_type": record_type,
        "fields": {
            field: _text(row.get(field)) for field in EVIDENCE_DERIVATION_FIELDS[record_type]
        },
    }


def cell_decision_binding_sha256(
    row: Mapping[str, Any], *, derivation_sha256: str | None = None
) -> str:
    """Bind all scientific cell decisions to content-addressed public evidence."""
    if derivation_sha256 is None:
        derivation_sha256 = sha256_bytes(
            canonical_json_bytes(cell_decision_derivation_payload(row))
        )
    payload = {
        "schema": "interlanguage/order-l-cell-decision-binding/1.0.0",
        "decision_derivation_id": _text(row.get("decision_derivation_id")),
        "decision_derivation_sha256": derivation_sha256,
        "decision_source": {
            "id": _text(row.get("decision_source_id")),
            "url": _text(row.get("decision_source_url")),
            "class": _text(row.get("decision_source_class")),
            "is_public": _text(row.get("decision_is_public")).casefold(),
            "bytes": _text(row.get("decision_source_bytes")),
            "sha256": _text(row.get("decision_source_sha256")).casefold(),
        },
        "population_source": {
            "id": _text(row.get("population_source_id")),
            "url": _text(row.get("population_source_url")),
            "class": _text(row.get("population_source_class")),
            "is_public": _text(row.get("population_is_public")).casefold(),
            "bytes": _text(row.get("population_source_bytes")),
            "sha256": _text(row.get("population_source_sha256")).casefold(),
        },
    }
    return sha256_bytes(canonical_json_bytes(payload))


def populate_derivation_fields(
    row: dict[str, str], *, record_type: str, derivation_id: str
) -> None:
    """Test/adapter helper: fill canonical content-addressed derivation fields in-place."""
    payload = evidence_derivation_payload(record_type, row)
    raw = canonical_json_bytes(payload)
    row["derivation_id"] = derivation_id
    row["derivation_json"] = raw.decode("utf-8")
    row["derivation_bytes"] = str(len(raw))
    row["derivation_sha256"] = sha256_bytes(raw)


def populate_cell_decision_fields(row: dict[str, str], *, derivation_id: str) -> None:
    """Test/adapter helper: fill canonical cell decision derivation and binding fields."""
    payload = cell_decision_derivation_payload(row)
    raw = canonical_json_bytes(payload)
    row["decision_derivation_id"] = derivation_id
    row["decision_derivation_json"] = raw.decode("utf-8")
    row["decision_derivation_bytes"] = str(len(raw))
    row["decision_derivation_sha256"] = sha256_bytes(raw)
    row["decision_binding_sha256"] = cell_decision_binding_sha256(
        row, derivation_sha256=row["decision_derivation_sha256"]
    )


@dataclass(frozen=True)
class Cell:
    cell_id: str
    person_profile_id: str
    edition_target_id: str
    edition_target_label: str
    stage_id: str
    endpoint_id: str
    benefit_unit: str
    population_denominator_id: str
    population_low: Decimal
    population_mode: Decimal | None
    population_high: Decimal
    population_resolution_status: str
    population_bound_reason_code: str
    assignment_mode: str
    assignment_atom_id: str
    assignment_weight: Decimal | None
    assignment_within_atom_weight: Decimal
    assignment_reason_code: str
    id_bound_method: str
    id_need_low: Decimal | None
    id_need_high: Decimal | None
    id_bound_reason_code: str
    evidence_tier: str
    evidence_reason_code: str
    eligibility_status: str
    eligibility_reason_code: str
    rankability_status: str
    rankability_reason_code: str
    universe_version: str
    universe_semantic_hash: str
    population_source_id: str
    decision_derivation_sha256: str
    decision_binding_sha256: str


@dataclass(frozen=True)
class Observation:
    observation_id: str
    cell_id: str
    kind: str
    construct_id: str
    likelihood_family: str
    numerator: Decimal
    denominator: Decimal
    sampling_design: str
    source_scope: str
    source_stage_id: str
    source_endpoint_id: str
    measurement_model_id: str
    transport_model_id: str
    correlation_group_id: str
    source_effect_sd: Decimal
    source_id: str


@dataclass(frozen=True)
class AssignmentEvidence:
    evidence_id: str
    person_profile_id: str
    assignment_atom_ids: tuple[str, ...]
    mode: str
    numerator: Decimal | None
    lower_share: Decimal | None
    upper_share: Decimal | None
    denominator: Decimal
    compatibility_group_id: str
    compatibility_mode: str
    source_id: str


@dataclass(frozen=True)
class MeasurementModel:
    model_id: str
    component_id: str
    family: str
    sensitivity: Decimal
    specificity: Decimal
    calibration_logit_sd: Decimal
    source_id: str


@dataclass(frozen=True)
class TransportModel:
    model_id: str
    family: str
    source_scope: str
    source_stage_id: str
    source_endpoint_id: str
    target_stage_id: str
    target_endpoint_id: str
    logit_shift_mean: Decimal
    logit_shift_sd: Decimal
    source_id: str


@dataclass(frozen=True)
class PriorFamily:
    family_id: str
    unmet_need_mean: Decimal
    intercept_sd: Decimal
    cell_sd: Decimal
    assignment_concentration: Decimal


@dataclass(frozen=True)
class PriorRegistry:
    schema: str
    model_version: str
    draw_algorithm_version: str
    likelihood_family: str
    measurement_family: str
    transport_family: str
    sha256: str
    families: Mapping[str, PriorFamily]


def _require_exact_target_set(
    actual: Iterable[str], expected: Iterable[str], *, artifact: str
) -> None:
    actual_set = set(actual)
    expected_set = set(expected)
    if actual_set != expected_set:
        raise OrderLModelError(
            f"{artifact} target set is not the complete authoritative edition universe "
            f"(missing={sorted(expected_set - actual_set)[:5]}, "
            f"foreign={sorted(actual_set - expected_set)[:5]})"
        )


def normalize_cells(
    rows: Sequence[Mapping[str, Any]],
    *,
    allow_synthetic: bool = False,
    expected_edition_target_ids: Iterable[str] | None = None,
    reason_registry: Mapping[str, frozenset[str]] | None = None,
) -> tuple[list[Cell], list[str]]:
    if reason_registry is None:
        reason_registry, _ = load_reason_registry()
    projected, ignored = _project(rows, CELL_FIELDS)
    if not projected:
        raise OrderLModelError("Order-L v2 requires a nonempty exact-target cell roster")
    result: list[Cell] = []
    seen_cells: set[str] = set()
    target_labels: dict[str, str] = {}
    profile_signatures: dict[str, tuple[Any, ...]] = {}
    denominator_profiles: dict[str, str] = {}
    profile_weight: dict[str, Decimal] = defaultdict(Decimal)
    profile_modes: dict[str, str] = {}
    atom_within_weight: dict[tuple[str, str], Decimal] = defaultdict(Decimal)
    benefit_units: set[str] = set()
    universe_versions: set[str] = set()
    universe_hashes: set[str] = set()
    for index, row in enumerate(projected, start=2):
        for field in (
            "cell_id", "person_profile_id", "edition_target_id", "edition_target_label",
            "learner_stage_id", "functional_access_endpoint_id", "benefit_unit",
            "population_denominator_id", "assignment_mode", "assignment_atom_id", "id_bound_method",
            "population_resolution_status", "population_bound_reason_code",
            "assignment_reason_code", "id_bound_reason_code", "evidence_tier",
            "evidence_reason_code",
            "eligibility_status", "eligibility_reason_code", "rankability_status",
            "rankability_reason_code", "universe_version",
            "universe_semantic_hash",
        ):
            if not row[field]:
                raise OrderLModelError(f"cell row {index}.{field} is required")
        if row["cell_id"] in seen_cells:
            raise OrderLModelError(f"duplicate cell_id: {row['cell_id']}")
        seen_cells.add(row["cell_id"])
        if row["benefit_unit"] not in {"persons", "learner_years"}:
            raise OrderLModelError(f"{row['cell_id']}.benefit_unit must be persons or learner_years")
        benefit_units.add(row["benefit_unit"])
        universe_versions.add(row["universe_version"])
        universe_hash = row["universe_semantic_hash"].casefold()
        if re.fullmatch(r"[0-9a-f]{64}", universe_hash) is None:
            raise OrderLModelError(
                f"{row['cell_id']}.universe_semantic_hash must be a 64-character SHA-256 hex digest"
            )
        universe_hashes.add(universe_hash)
        if row["id_bound_method"] not in ID_BOUND_METHODS:
            raise OrderLModelError(f"{row['cell_id']}.id_bound_method is invalid")
        if row["evidence_tier"] not in EVIDENCE_TIERS:
            raise OrderLModelError(f"{row['cell_id']}.evidence_tier is invalid")
        if row["eligibility_status"] not in {"ELIGIBLE", "STRUCTURAL_ZERO"}:
            raise OrderLModelError(f"{row['cell_id']}.eligibility_status is invalid")
        for group in (
            "population_resolution_status", "population_bound_reason_code",
            "assignment_reason_code", "id_bound_reason_code", "eligibility_reason_code",
            "rankability_status", "rankability_reason_code", "evidence_reason_code",
        ):
            if row[group] not in reason_registry[group]:
                raise OrderLModelError(f"{row['cell_id']}.{group} is not a closed reason code")
        low = _decimal(row["population_lower_bound"], label=f"{row['cell_id']}.population_lower_bound", required=True)
        mode = _decimal(row["population_mode"], label=f"{row['cell_id']}.population_mode")
        high = _decimal(row["population_upper_bound"], label=f"{row['cell_id']}.population_upper_bound", required=True)
        if row["assignment_mode"] not in ASSIGNMENT_MODES:
            raise OrderLModelError(f"{row['cell_id']}.assignment_mode is invalid")
        weight = _decimal(row["assignment_weight"], label=f"{row['cell_id']}.assignment_weight")
        within_weight = _decimal(
            row["assignment_within_atom_weight"],
            label=f"{row['cell_id']}.assignment_within_atom_weight",
        )
        assert low is not None and high is not None
        if low < 0 or high < low or high <= 0:
            raise OrderLModelError(
                f"{row['cell_id']} requires 0 <= population lower <= finite positive upper"
            )
        if mode is not None and not low <= mode <= high:
            raise OrderLModelError(f"{row['cell_id']}.population_mode lies outside public bounds")
        if row["population_resolution_status"] == "FINITE_CEILING_UNRESOLVED":
            if low != 0 or mode is not None or row["evidence_tier"] != "DENOMINATOR_UNIDENTIFIED":
                raise OrderLModelError(
                    f"{row['cell_id']} unresolved population requires [0, finite ceiling], blank mode, "
                    "and DENOMINATOR_UNIDENTIFIED diagnostic tier"
                )
            if row["population_bound_reason_code"] not in {
                "SOURCE_BOUND_TERRITORIAL_OR_COMMUNITY_CEILING",
                "SOURCE_BOUND_WORLD_CEILING",
            }:
                raise OrderLModelError(
                    f"{row['cell_id']} unresolved population requires a territorial/community or world ceiling"
                )
        elif row["evidence_tier"] == "DENOMINATOR_UNIDENTIFIED":
            raise OrderLModelError(
                f"{row['cell_id']} denominator-unidentified tier requires explicit unresolved status"
            )
        if row["assignment_mode"] == "fixed_direct":
            if row["assignment_reason_code"] != "EXACT_FIXED_EXCLUSIVE_COHORT":
                raise OrderLModelError(f"{row['cell_id']} fixed assignment has the wrong reason code")
            if weight is None or not Decimal(0) < weight <= Decimal(1):
                raise OrderLModelError(f"{row['cell_id']}.assignment_weight must be in (0,1] for fixed_direct")
            if within_weight is not None:
                raise OrderLModelError(
                    f"{row['cell_id']} fixed_direct assignment cannot also supply assignment_within_atom_weight"
                )
            within_weight = Decimal(1)
        else:
            if row["assignment_reason_code"] != "LATENT_SYMMETRIC_MUTUALLY_EXCLUSIVE_PARTITION":
                raise OrderLModelError(f"{row['cell_id']} latent assignment has the wrong reason code")
            if weight is not None:
                raise OrderLModelError(
                    f"{row['cell_id']} latent_symmetric assignment cannot supply a fixed assignment_weight"
                )
            if within_weight is None or not Decimal(0) < within_weight <= Decimal(1):
                raise OrderLModelError(
                    f"{row['cell_id']}.assignment_within_atom_weight must be in (0,1] for latent_symmetric"
                )
        id_low = _decimal(row["id_need_lower_bound"], label=f"{row['cell_id']}.id_need_lower_bound")
        id_high = _decimal(row["id_need_upper_bound"], label=f"{row['cell_id']}.id_need_upper_bound")
        if row["id_bound_method"] in {"supplied_construct_bound", "frechet_bound"}:
            if id_low is None or id_high is None:
                raise OrderLModelError(f"{row['cell_id']} requires both ID need bounds")
            if not Decimal(0) <= id_low <= id_high <= Decimal(1):
                raise OrderLModelError(f"{row['cell_id']} ID need bounds must lie in [0,1]")
        elif id_low is not None or id_high is not None:
            raise OrderLModelError(
                f"{row['cell_id']} supplies ID need bounds under method {row['id_bound_method']!r}"
            )
        method_reasons = {
            "logical_0_1": "LOGICAL_UNIT_INTERVAL",
            "supplied_construct_bound": "PUBLIC_CONSTRUCT_BOUND",
            "frechet_bound": "PUBLIC_FRECHET_DERIVATION",
            "direct_endpoint_census": "EXACT_DIRECT_ENDPOINT_CENSUS",
            "structural_zero": "VERIFIED_STRUCTURAL_ZERO",
        }
        if row["id_bound_reason_code"] != method_reasons[row["id_bound_method"]]:
            raise OrderLModelError(f"{row['cell_id']} ID-bound reason does not match its method")
        if row["eligibility_status"] == "STRUCTURAL_ZERO":
            if (
                row["id_bound_method"] != "structural_zero"
                or row["eligibility_reason_code"] != "VERIFIED_STRUCTURAL_ZERO"
                or row["rankability_status"] != "RANKABLE_STRUCTURAL_ZERO"
                or row["rankability_reason_code"] != "VERIFIED_STRUCTURAL_ZERO"
            ):
                raise OrderLModelError(
                    f"{row['cell_id']} structural zero requires the complete verified-zero reason tuple"
                )
        elif (
            row["id_bound_method"] == "structural_zero"
            or row["eligibility_reason_code"] != "COMMON_MODEL_INCLUDED"
            or row["rankability_status"] != "RANKABLE_COMMON_MODEL"
            or row["rankability_reason_code"] != "COMPLETE_COMMON_MODEL_CELL"
        ):
            raise OrderLModelError(
                f"{row['cell_id']} eligible cells require the complete common-model reason tuple"
            )
        _require_content_addressed_source(
            row, prefix="population_", allow_synthetic=allow_synthetic
        )
        _require_content_addressed_source(
            row, prefix="decision_", allow_synthetic=allow_synthetic
        )
        decision_digest = _require_derivation(
            row,
            prefix="decision_",
            expected_payload=cell_decision_derivation_payload(row),
        )
        expected_binding = cell_decision_binding_sha256(
            row, derivation_sha256=decision_digest
        )
        if row["decision_binding_sha256"].casefold() != expected_binding:
            raise OrderLModelError(
                f"{row['cell_id']} decision_binding_sha256 does not bind its source and decision fields"
            )
        prior_label = target_labels.setdefault(row["edition_target_id"], row["edition_target_label"])
        if prior_label != row["edition_target_label"]:
            raise OrderLModelError(f"edition target {row['edition_target_id']!r} has inconsistent labels")
        signature = (
            row["learner_stage_id"], row["functional_access_endpoint_id"], row["benefit_unit"],
            row["population_denominator_id"], low, mode, high, row["population_source_id"],
            row["population_source_sha256"], row["population_resolution_status"],
            row["population_bound_reason_code"], row["assignment_mode"],
        )
        prior_signature = profile_signatures.setdefault(row["person_profile_id"], signature)
        if signature != prior_signature:
            raise OrderLModelError(
                f"person profile {row['person_profile_id']!r} changes population, stage, endpoint, or unit"
            )
        prior_profile = denominator_profiles.setdefault(row["population_denominator_id"], row["person_profile_id"])
        if prior_profile != row["person_profile_id"]:
            raise OrderLModelError(
                f"population denominator {row['population_denominator_id']!r} is duplicated across person profiles"
            )
        prior_mode = profile_modes.setdefault(row["person_profile_id"], row["assignment_mode"])
        if prior_mode != row["assignment_mode"]:
            raise OrderLModelError(f"person profile {row['person_profile_id']!r} mixes assignment modes")
        if row["assignment_mode"] == "fixed_direct":
            assert weight is not None
            profile_weight[row["person_profile_id"]] += weight
        else:
            atom_within_weight[(row["person_profile_id"], row["assignment_atom_id"])] += within_weight
        result.append(
            Cell(
                row["cell_id"], row["person_profile_id"], row["edition_target_id"],
                row["edition_target_label"], row["learner_stage_id"],
                row["functional_access_endpoint_id"], row["benefit_unit"],
                row["population_denominator_id"], low, mode, high,
                row["population_resolution_status"], row["population_bound_reason_code"],
                row["assignment_mode"],
                row["assignment_atom_id"], weight, within_weight,
                row["assignment_reason_code"], row["id_bound_method"], id_low, id_high,
                row["id_bound_reason_code"], row["evidence_tier"], row["evidence_reason_code"],
                row["eligibility_status"],
                row["eligibility_reason_code"], row["rankability_status"],
                row["rankability_reason_code"], row["universe_version"], universe_hash,
                row["population_source_id"], decision_digest, expected_binding,
            )
        )
    if len(benefit_units) != 1:
        raise OrderLModelError(f"Order-L v2 mixes incompatible benefit units: {sorted(benefit_units)}")
    if len(universe_versions) != 1 or len(universe_hashes) != 1:
        raise OrderLModelError(
            "every Order-L V2 cell must bind to one canonical universe version and semantic hash"
        )
    invalid_weights = {
        profile: weight for profile, weight in profile_weight.items()
        if profile_modes[profile] == "fixed_direct" and weight != Decimal(1)
    }
    if invalid_weights:
        raise OrderLModelError(
            "one-person assignment requires weights summing exactly to one per person profile: "
            f"{invalid_weights}"
        )
    invalid_atoms = {
        key: weight for key, weight in atom_within_weight.items() if weight != Decimal(1)
    }
    if invalid_atoms:
        raise OrderLModelError(
            "latent target splits require within-atom weights summing exactly to one: "
            f"{invalid_atoms}"
        )
    if expected_edition_target_ids is not None:
        _require_exact_target_set(
            (cell.edition_target_id for cell in result),
            expected_edition_target_ids,
            artifact="Order-L cells",
        )
    return sorted(result, key=lambda cell: cell.cell_id), ignored


def normalize_measurement_models(
    rows: Sequence[Mapping[str, Any]],
    *,
    allow_synthetic: bool = False,
    reason_registry: Mapping[str, frozenset[str]] | None = None,
) -> tuple[dict[str, MeasurementModel], list[str]]:
    if reason_registry is None:
        reason_registry, _ = load_reason_registry()
    projected, ignored = _project(rows, MEASUREMENT_MODEL_FIELDS)
    result: dict[str, MeasurementModel] = {}
    for index, row in enumerate(projected, start=2):
        if not row["measurement_model_id"] or not row["component_id"]:
            raise OrderLModelError(f"measurement model row {index} lacks identity")
        if row["measurement_model_id"] in result:
            raise OrderLModelError(f"duplicate measurement_model_id: {row['measurement_model_id']}")
        if row["model_family"] != MEASUREMENT_FAMILY:
            raise OrderLModelError("all component proxies require the frozen common measurement family")
        sensitivity = _decimal(row["sensitivity_mean"], label=f"measurement row {index}.sensitivity", required=True)
        specificity = _decimal(row["specificity_mean"], label=f"measurement row {index}.specificity", required=True)
        calibration_sd = _decimal(
            row["calibration_logit_sd"], label=f"measurement row {index}.calibration_logit_sd", required=True
        )
        assert sensitivity is not None and specificity is not None and calibration_sd is not None
        if not Decimal(0) < sensitivity <= 1 or not Decimal(0) < specificity <= 1:
            raise OrderLModelError("measurement sensitivity and specificity must lie in (0,1]")
        if sensitivity + specificity <= 1:
            raise OrderLModelError("measurement model is not directionally identified")
        if calibration_sd < 0:
            raise OrderLModelError("calibration_logit_sd cannot be negative")
        if row["admission_reason_code"] not in reason_registry["measurement_admission_reason_code"]:
            raise OrderLModelError("measurement model admission_reason_code is not closed")
        _require_content_addressed_source(row, prefix="", allow_synthetic=allow_synthetic)
        _require_derivation(
            row,
            expected_payload=evidence_derivation_payload("measurement_model", row),
        )
        result[row["measurement_model_id"]] = MeasurementModel(
            row["measurement_model_id"], row["component_id"], row["model_family"],
            sensitivity, specificity, calibration_sd, row["source_id"],
        )
    return result, ignored


def normalize_assignment_evidence(
    rows: Sequence[Mapping[str, Any]],
    cells: Sequence[Cell],
    *,
    allow_synthetic: bool = False,
    reason_registry: Mapping[str, frozenset[str]] | None = None,
) -> tuple[list[AssignmentEvidence], list[str]]:
    """Normalize complete multinomials and non-renormalized partial share constraints."""
    if reason_registry is None:
        reason_registry, _ = load_reason_registry()
    projected, ignored = _project(rows, ASSIGNMENT_EVIDENCE_FIELDS)
    atoms_by_profile: dict[str, set[str]] = defaultdict(set)
    mode_by_profile: dict[str, str] = {}
    for cell in cells:
        atoms_by_profile[cell.person_profile_id].add(cell.assignment_atom_id)
        mode_by_profile[cell.person_profile_id] = cell.assignment_mode
    result: list[AssignmentEvidence] = []
    seen_ids: set[str] = set()
    complete_seen_atoms: set[tuple[str, str, str]] = set()
    complete_signatures: dict[tuple[str, str], tuple[Decimal, str]] = {}
    complete_totals: dict[tuple[str, str], Decimal] = defaultdict(Decimal)
    complete_atoms: dict[tuple[str, str], set[str]] = defaultdict(set)
    for index, row in enumerate(projected, start=2):
        for field in (
            "assignment_evidence_id", "person_profile_id", "evidence_mode",
            "compatibility_group_id", "compatibility_mode", "admission_reason_code",
        ):
            if not row[field]:
                raise OrderLModelError(f"assignment evidence row {index}.{field} is required")
        if row["assignment_evidence_id"] in seen_ids:
            raise OrderLModelError(f"duplicate assignment_evidence_id: {row['assignment_evidence_id']}")
        seen_ids.add(row["assignment_evidence_id"])
        profile = row["person_profile_id"]
        if row["evidence_mode"] not in ASSIGNMENT_EVIDENCE_MODES:
            raise OrderLModelError("assignment evidence_mode is not closed")
        if row["compatibility_mode"] not in ASSIGNMENT_COMPATIBILITY_MODES:
            raise OrderLModelError("assignment compatibility_mode is not closed")
        atom_ids_raw = row["assignment_atom_ids_json"]
        if atom_ids_raw:
            try:
                parsed_atoms = json.loads(atom_ids_raw)
            except json.JSONDecodeError as exc:
                raise OrderLModelError("assignment_atom_ids_json is invalid") from exc
            if (
                not isinstance(parsed_atoms, list)
                or not parsed_atoms
                or not all(isinstance(item, str) and item.strip() for item in parsed_atoms)
            ):
                raise OrderLModelError("assignment_atom_ids_json requires a nonempty string array")
            atoms = tuple(sorted(item.strip() for item in parsed_atoms))
            if len(set(atoms)) != len(atoms) or atom_ids_raw != canonical_json_bytes(list(atoms)).decode("utf-8"):
                raise OrderLModelError("assignment_atom_ids_json must be a unique sorted canonical array")
        elif row["assignment_atom_id"]:
            atoms = (row["assignment_atom_id"],)
        else:
            raise OrderLModelError("assignment evidence requires an atom or canonical atom set")
        if row["assignment_atom_id"] and atoms != (row["assignment_atom_id"],):
            raise OrderLModelError("assignment_atom_id may only mirror a singleton atom set")
        if profile not in atoms_by_profile or not set(atoms) <= atoms_by_profile[profile]:
            raise OrderLModelError("assignment evidence references an unknown profile/atom set")
        if mode_by_profile[profile] != "latent_symmetric":
            raise OrderLModelError("fixed direct cohorts cannot be overwritten by assignment-share evidence")
        numerator = _decimal(row["numerator_count"], label=f"assignment evidence row {index}.numerator")
        lower = _decimal(row["lower_count"], label=f"assignment evidence row {index}.lower")
        upper = _decimal(row["upper_count"], label=f"assignment evidence row {index}.upper")
        denominator = _decimal(row["denominator_count"], label=f"assignment evidence row {index}.denominator", required=True)
        assert denominator is not None
        if denominator <= 0:
            raise OrderLModelError("assignment evidence requires a positive denominator")
        if row["evidence_mode"] == "complete_multinomial":
            if (
                len(atoms) != 1
                or numerator is None
                or lower is not None
                or upper is not None
                or row["compatibility_mode"] != "MUTUALLY_EXCLUSIVE_EXHAUSTIVE"
                or row["admission_reason_code"] != "COMPATIBLE_COMPLETE_MULTINOMIAL_CROSSTAB"
            ):
                raise OrderLModelError(
                    "complete multinomial evidence requires singleton counts and the exact complete-partition codes"
                )
            if numerator < 0 or numerator > denominator:
                raise OrderLModelError("multinomial numerator must lie in [0, denominator]")
            group_key = (profile, row["compatibility_group_id"])
            atom_key = (*group_key, atoms[0])
            if atom_key in complete_seen_atoms:
                raise OrderLModelError("duplicate atom in one complete multinomial group")
            complete_seen_atoms.add(atom_key)
            signature = (denominator, row["source_id"])
            prior_signature = complete_signatures.setdefault(group_key, signature)
            if prior_signature != signature:
                raise OrderLModelError("one complete multinomial group must use one denominator/source")
            complete_totals[group_key] += numerator
            complete_atoms[group_key].add(atoms[0])
            lower_share = None
            upper_share = None
        else:
            if (
                numerator is not None
                and (lower is not None or upper is not None)
            ):
                raise OrderLModelError("partial assignment uses either point count or lower/upper counts")
            if numerator is not None:
                lower = upper = numerator
            if lower is None or upper is None:
                raise OrderLModelError("partial assignment requires point count or both lower/upper counts")
            if not Decimal(0) <= lower <= upper <= denominator:
                raise OrderLModelError("partial assignment counts require 0 <= lower <= upper <= denominator")
            if (
                row["compatibility_mode"] != "OVERLAPPING_OR_NONEXHAUSTIVE_BOUNDS"
                or row["admission_reason_code"] != "SOURCE_BOUND_PARTIAL_ASSIGNMENT_INTERVAL"
            ):
                raise OrderLModelError(
                    "partial assignments require the exact overlap/nonexhaustive compatibility codes"
                )
            lower_share = lower / denominator
            upper_share = upper / denominator
        if row["admission_reason_code"] not in reason_registry["assignment_evidence_admission_reason_code"]:
            raise OrderLModelError("assignment evidence admission_reason_code is not closed")
        _require_content_addressed_source(row, prefix="", allow_synthetic=allow_synthetic)
        _require_derivation(
            row,
            expected_payload=evidence_derivation_payload("assignment_evidence", row),
        )
        result.append(
            AssignmentEvidence(
                row["assignment_evidence_id"], profile, atoms, row["evidence_mode"],
                numerator, lower_share, upper_share, denominator,
                row["compatibility_group_id"], row["compatibility_mode"], row["source_id"],
            )
        )
    complete_group_by_profile: dict[str, int] = defaultdict(int)
    for group_key, atoms in complete_atoms.items():
        profile = group_key[0]
        complete_group_by_profile[profile] += 1
        if complete_group_by_profile[profile] > 1:
            raise OrderLModelError("a profile may have at most one complete multinomial cross-tab")
        if atoms != atoms_by_profile[profile]:
            raise OrderLModelError(
                f"complete multinomial evidence for {profile!r} must cover every stable atom"
            )
        if complete_totals[group_key] != complete_signatures[group_key][0]:
            raise OrderLModelError(
                f"complete multinomial counts for {profile!r} must sum to the denominator"
            )
    _validate_partial_assignment_feasibility(result, atoms_by_profile)
    return sorted(result, key=lambda item: item.evidence_id), ignored


def normalize_transport_models(
    rows: Sequence[Mapping[str, Any]],
    *,
    allow_synthetic: bool = False,
    reason_registry: Mapping[str, frozenset[str]] | None = None,
) -> tuple[dict[str, TransportModel], list[str]]:
    if reason_registry is None:
        reason_registry, _ = load_reason_registry()
    projected, ignored = _project(rows, TRANSPORT_MODEL_FIELDS)
    result: dict[str, TransportModel] = {}
    for index, row in enumerate(projected, start=2):
        for field in (
            "transport_model_id", "source_scope", "source_stage_id", "source_endpoint_id",
            "target_stage_id", "target_endpoint_id",
        ):
            if not row[field]:
                raise OrderLModelError(f"transport row {index}.{field} is required")
        if row["transport_model_id"] in result:
            raise OrderLModelError(f"duplicate transport_model_id: {row['transport_model_id']}")
        if row["model_family"] != TRANSPORT_FAMILY:
            raise OrderLModelError("all transported observations require the frozen common transport family")
        if row["source_scope"] == "exact_target" or row["source_scope"] not in SOURCE_SCOPES:
            raise OrderLModelError("transport models are only for ecological or broader-cohort evidence")
        mean = _decimal(row["logit_shift_mean"], label=f"transport row {index}.mean", required=True)
        sd = _decimal(row["logit_shift_sd"], label=f"transport row {index}.sd", required=True)
        assert mean is not None and sd is not None
        if sd < 0:
            raise OrderLModelError("transport logit_shift_sd cannot be negative")
        if row["admission_reason_code"] not in reason_registry["transport_admission_reason_code"]:
            raise OrderLModelError("transport model admission_reason_code is not closed")
        _require_content_addressed_source(row, prefix="", allow_synthetic=allow_synthetic)
        _require_derivation(
            row,
            expected_payload=evidence_derivation_payload("transport_model", row),
        )
        result[row["transport_model_id"]] = TransportModel(
            row["transport_model_id"], row["model_family"], row["source_scope"],
            row["source_stage_id"], row["source_endpoint_id"], row["target_stage_id"],
            row["target_endpoint_id"], mean, sd, row["source_id"],
        )
    return result, ignored


def normalize_observations(
    rows: Sequence[Mapping[str, Any]],
    cells: Sequence[Cell],
    measurement_models: Mapping[str, MeasurementModel],
    transport_models: Mapping[str, TransportModel],
    *,
    allow_synthetic: bool = False,
    reason_registry: Mapping[str, frozenset[str]] | None = None,
) -> tuple[list[Observation], list[str]]:
    if reason_registry is None:
        reason_registry, _ = load_reason_registry()
    projected, ignored = _project(rows, OBSERVATION_FIELDS)
    cell_by_id = {cell.cell_id: cell for cell in cells}
    result: list[Observation] = []
    seen: set[str] = set()
    correlation_signatures: dict[str, tuple[str, Decimal]] = {}
    for index, row in enumerate(projected, start=2):
        for field in (
            "observation_id", "cell_id", "observation_kind", "construct_id",
            "likelihood_family", "sampling_design", "source_scope", "source_stage_id",
            "source_endpoint_id", "source_correlation_group_id", "admission_reason_code",
        ):
            if not row[field]:
                raise OrderLModelError(f"observation row {index}.{field} is required")
        if row["observation_id"] in seen:
            raise OrderLModelError(f"duplicate observation_id: {row['observation_id']}")
        seen.add(row["observation_id"])
        if row["cell_id"] not in cell_by_id:
            raise OrderLModelError(f"observation {row['observation_id']} references unknown cell")
        cell = cell_by_id[row["cell_id"]]
        if row["observation_kind"] not in OBSERVATION_KINDS:
            raise OrderLModelError(f"observation {row['observation_id']} has invalid kind")
        if row["likelihood_family"] != LIKELIHOOD_FAMILY:
            raise OrderLModelError("every count observation uses the same frozen binomial likelihood family")
        if row["source_scope"] not in SOURCE_SCOPES:
            raise OrderLModelError(f"observation {row['observation_id']} has invalid source_scope")
        numerator = _decimal(row["numerator_count"], label=f"observation {row['observation_id']}.numerator", required=True)
        denominator = _decimal(
            row["denominator_count"], label=f"observation {row['observation_id']}.denominator", required=True
        )
        source_sd = _decimal(
            row["source_effect_sd"], label=f"observation {row['observation_id']}.source_effect_sd", required=True
        )
        assert numerator is not None and denominator is not None and source_sd is not None
        if numerator < 0 or denominator <= 0 or numerator > denominator:
            raise OrderLModelError("observation counts require 0 <= numerator <= positive denominator")
        if source_sd < 0:
            raise OrderLModelError("source_effect_sd cannot be negative")
        if row["observation_kind"] == "direct_endpoint_count":
            if row["construct_id"] != cell.endpoint_id:
                raise OrderLModelError("a direct endpoint count must name the cell's full functional-access endpoint")
            if row["measurement_model_id"]:
                raise OrderLModelError("direct endpoint counts do not use a component measurement model")
        else:
            model = measurement_models.get(row["measurement_model_id"])
            if model is None:
                raise OrderLModelError("component proxy counts require an explicit registered measurement model")
            if model.component_id != row["construct_id"]:
                raise OrderLModelError("component proxy construct does not match its measurement model")
            if row["construct_id"] == cell.endpoint_id:
                raise OrderLModelError("a component proxy cannot masquerade as the full endpoint")
        transport_required = (
            row["source_scope"] != "exact_target"
            or row["source_stage_id"] != cell.stage_id
            or row["source_endpoint_id"] != cell.endpoint_id
        )
        if transport_required:
            transport = transport_models.get(row["transport_model_id"])
            if transport is None:
                raise OrderLModelError("ecological, broader-cohort, or cross-endpoint evidence requires explicit transport")
            observed_signature = (
                row["source_scope"], row["source_stage_id"], row["source_endpoint_id"],
                cell.stage_id, cell.endpoint_id,
            )
            model_signature = (
                transport.source_scope, transport.source_stage_id, transport.source_endpoint_id,
                transport.target_stage_id, transport.target_endpoint_id,
            )
            if observed_signature != model_signature:
                raise OrderLModelError("transport model does not match the declared source and target strata")
        elif row["transport_model_id"]:
            raise OrderLModelError("exact-target same-endpoint evidence cannot acquire an unnecessary transport shift")
        expected_reason = (
            "TRANSPORTED_COMPONENT_PROXY_WITH_EXPLICIT_MODELS"
            if transport_required and row["observation_kind"] == "component_proxy_count"
            else "TRANSPORTED_DIRECT_ENDPOINT_WITH_EXPLICIT_TRANSPORT"
            if transport_required
            else "EXACT_COMPONENT_PROXY_WITH_MEASUREMENT"
            if row["observation_kind"] == "component_proxy_count"
            else "EXACT_DIRECT_ENDPOINT_COUNT"
        )
        if (
            row["admission_reason_code"] != expected_reason
            or row["admission_reason_code"]
            not in reason_registry["observation_admission_reason_code"]
        ):
            raise OrderLModelError("observation admission reason does not match its evidence route")
        _require_content_addressed_source(row, prefix="", allow_synthetic=allow_synthetic)
        _require_derivation(
            row,
            expected_payload=evidence_derivation_payload("observation", row),
        )
        group_signature = (row["source_id"], source_sd)
        prior_group = correlation_signatures.setdefault(row["source_correlation_group_id"], group_signature)
        if prior_group != group_signature:
            raise OrderLModelError("a source correlation group changes source identity or shared-effect scale")
        result.append(
            Observation(
                row["observation_id"], row["cell_id"], row["observation_kind"],
                row["construct_id"], row["likelihood_family"], numerator, denominator,
                row["sampling_design"], row["source_scope"], row["source_stage_id"],
                row["source_endpoint_id"], row["measurement_model_id"],
                row["transport_model_id"], row["source_correlation_group_id"],
                source_sd, row["source_id"],
            )
        )
    return sorted(result, key=lambda item: item.observation_id), ignored


def validate_cell_evidence_routes(
    cells: Sequence[Cell], observations: Sequence[Observation]
) -> None:
    """Validate closed evidence-admission reasons without using diagnostic tiers as predictors."""
    by_cell: dict[str, list[Observation]] = defaultdict(list)
    for observation in observations:
        by_cell[observation.cell_id].append(observation)
    for cell in cells:
        admitted = by_cell.get(cell.cell_id, [])
        if cell.id_bound_method == "direct_endpoint_census" or any(
            item.kind == "direct_endpoint_count" and not item.transport_model_id
            for item in admitted
        ):
            expected = "DIRECT_ENDPOINT_ROUTE"
        elif any(item.transport_model_id for item in admitted):
            expected = "EXPLICIT_TRANSPORT_ROUTE"
        elif any(item.kind == "component_proxy_count" for item in admitted):
            expected = "COMPONENT_MEASUREMENT_ROUTE"
        elif cell.id_bound_method in {
            "supplied_construct_bound", "frechet_bound", "structural_zero"
        }:
            expected = "PARTIAL_IDENTIFICATION_BOUND_ROUTE"
        elif cell.population_resolution_status == "FINITE_CEILING_UNRESOLVED":
            expected = "UNRESOLVED_DENOMINATOR_ROUTE"
        else:
            expected = "COMMON_PRIOR_ROUTE"
        if cell.evidence_reason_code != expected:
            raise OrderLModelError(
                f"{cell.cell_id}.evidence_reason_code does not match admitted evidence ({expected})"
            )


def load_prior_registry(path: Path = DEFAULT_PRIOR_REGISTRY_PATH) -> PriorRegistry:
    try:
        raw = path.read_bytes()
        document = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OrderLModelError(f"cannot load Order-L prior registry {path}: {exc}") from exc
    if document.get("schema") != "interlanguage/order-l-v2-prior-registry/1.0.0":
        raise OrderLModelError("unsupported Order-L prior registry schema")
    if document.get("model_version") != MODEL_VERSION:
        raise OrderLModelError("prior registry model_version does not match the implementation")
    if document.get("draw_algorithm_version") != DRAW_ALGORITHM_VERSION:
        raise OrderLModelError("prior registry draw algorithm does not match the implementation")
    if document.get("likelihood_family") != LIKELIHOOD_FAMILY:
        raise OrderLModelError("prior registry likelihood family does not match the implementation")
    if document.get("measurement_family") != MEASUREMENT_FAMILY:
        raise OrderLModelError("prior registry measurement family does not match the implementation")
    if document.get("transport_family") != TRANSPORT_FAMILY:
        raise OrderLModelError("prior registry transport family does not match the implementation")
    if document.get("target_predictors") != []:
        raise OrderLModelError("exact-target predictors are forbidden in the common model")
    families: dict[str, PriorFamily] = {}
    for item in document.get("families", []):
        family_id = _text(item.get("prior_family_id"))
        if not family_id or family_id in families:
            raise OrderLModelError("prior registry has a blank or duplicate family")
        mean = _decimal(item.get("unmet_need_prior_mean"), label=f"{family_id}.mean", required=True)
        intercept_sd = _decimal(item.get("stage_endpoint_intercept_sd"), label=f"{family_id}.intercept_sd", required=True)
        cell_sd = _decimal(item.get("cell_logit_sd"), label=f"{family_id}.cell_sd", required=True)
        assignment_concentration = _decimal(
            item.get("assignment_symmetric_concentration"),
            label=f"{family_id}.assignment_symmetric_concentration",
            required=True,
        )
        assert mean is not None and intercept_sd is not None and cell_sd is not None
        assert assignment_concentration is not None
        if (
            not Decimal(0) < mean < Decimal(1)
            or intercept_sd <= 0
            or cell_sd <= 0
            or assignment_concentration <= 0
        ):
            raise OrderLModelError("prior means must be internal probabilities and scales must be positive")
        if mean == Decimal("0.5"):
            raise OrderLModelError("the frozen missing-data priors may not use an automatic 0.5 midpoint")
        families[family_id] = PriorFamily(
            family_id, mean, intercept_sd, cell_sd, assignment_concentration
        )
    if set(families) != REQUIRED_PRIOR_FAMILIES:
        raise OrderLModelError(
            "prior registry requires the four need-prior families plus sparse/concentrated "
            f"assignment sensitivities: {sorted(families)}"
        )
    return PriorRegistry(
        document["schema"], document["model_version"], document["draw_algorithm_version"],
        document["likelihood_family"], document["measurement_family"],
        document["transport_family"], sha256_bytes(raw), families,
    )


def _top_status(best: int, worst: int, k: int) -> str:
    if worst <= k:
        return "definite"
    if best <= k < worst:
        return "possible"
    return "outside"


class _LinearProgram:
    """Small deterministic two-phase simplex: maximize c*x subject to Ax<=b, x>=0."""

    EPSILON = 1e-10

    def __init__(self, a: Sequence[Sequence[float]], b: Sequence[float], c: Sequence[float]):
        self.m = len(b)
        self.n = len(c)
        self.basis = [self.n + index for index in range(self.m)]
        self.nonbasis = list(range(self.n)) + [-1]
        self.tableau = [
            [0.0 for _ in range(self.n + 2)] for _ in range(self.m + 2)
        ]
        for row in range(self.m):
            for column in range(self.n):
                self.tableau[row][column] = a[row][column]
            self.tableau[row][self.n] = -1.0
            self.tableau[row][self.n + 1] = b[row]
        for column in range(self.n):
            self.tableau[self.m][column] = -c[column]
        self.tableau[self.m + 1][self.n] = 1.0

    def _pivot(self, row: int, column: int) -> None:
        inverse = 1.0 / self.tableau[row][column]
        for other_row in range(self.m + 2):
            if other_row == row:
                continue
            for other_column in range(self.n + 2):
                if other_column == column:
                    continue
                self.tableau[other_row][other_column] -= (
                    self.tableau[row][other_column]
                    * self.tableau[other_row][column]
                    * inverse
                )
        for other_column in range(self.n + 2):
            if other_column != column:
                self.tableau[row][other_column] *= inverse
        for other_row in range(self.m + 2):
            if other_row != row:
                self.tableau[other_row][column] *= -inverse
        self.tableau[row][column] = inverse
        self.basis[row], self.nonbasis[column] = self.nonbasis[column], self.basis[row]

    def _simplex(self, phase: int) -> bool:
        objective_row = self.m + 1 if phase == 1 else self.m
        while True:
            entering: int | None = None
            for column in range(self.n + 1):
                if phase == 2 and self.nonbasis[column] == -1:
                    continue
                if entering is None or (
                    self.tableau[objective_row][column]
                    < self.tableau[objective_row][entering] - self.EPSILON
                ) or (
                    abs(
                        self.tableau[objective_row][column]
                        - self.tableau[objective_row][entering]
                    )
                    <= self.EPSILON
                    and self.nonbasis[column] < self.nonbasis[entering]
                ):
                    entering = column
            assert entering is not None
            if self.tableau[objective_row][entering] >= -self.EPSILON:
                return True
            leaving: int | None = None
            for row in range(self.m):
                if self.tableau[row][entering] <= self.EPSILON:
                    continue
                if leaving is None:
                    leaving = row
                    continue
                candidate = self.tableau[row][self.n + 1] / self.tableau[row][entering]
                current = self.tableau[leaving][self.n + 1] / self.tableau[leaving][entering]
                if candidate < current - self.EPSILON or (
                    abs(candidate - current) <= self.EPSILON
                    and self.basis[row] < self.basis[leaving]
                ):
                    leaving = row
            if leaving is None:
                return False
            self._pivot(leaving, entering)

    def solve(self) -> tuple[str, float, list[float]]:
        leaving = min(range(self.m), key=lambda row: self.tableau[row][self.n + 1])
        if self.tableau[leaving][self.n + 1] < -self.EPSILON:
            self._pivot(leaving, self.n)
            if (
                not self._simplex(1)
                or self.tableau[self.m + 1][self.n + 1] < -self.EPSILON
                or abs(self.tableau[self.m + 1][self.n + 1]) > self.EPSILON
            ):
                return "infeasible", float("nan"), []
            if -1 in self.basis:
                row = self.basis.index(-1)
                entering = min(
                    range(self.n + 1),
                    key=lambda column: (
                        abs(self.tableau[row][column]) <= self.EPSILON,
                        self.nonbasis[column],
                    ),
                )
                if abs(self.tableau[row][entering]) > self.EPSILON:
                    self._pivot(row, entering)
        if not self._simplex(2):
            return "unbounded", float("inf"), []
        solution = [0.0 for _ in range(self.n)]
        for row in range(self.m):
            if self.basis[row] < self.n:
                solution[self.basis[row]] = self.tableau[row][self.n + 1]
        return "optimal", self.tableau[self.m][self.n + 1], solution


def _partial_assignment_constraints(
    profile: str, assignment_evidence: Sequence[AssignmentEvidence]
) -> list[AssignmentEvidence]:
    return [
        item
        for item in assignment_evidence
        if item.person_profile_id == profile and item.mode == "partial_interval_constraint"
    ]


def _solve_assignment_polytope(
    atoms: Sequence[str],
    constraints: Sequence[AssignmentEvidence],
    coefficients: Mapping[str, Decimal],
    *,
    maximize: bool,
) -> tuple[Decimal, dict[str, Decimal]]:
    if not constraints:
        values = [coefficients.get(atom, Decimal(0)) for atom in atoms]
        optimum = max(values) if maximize else min(values)
        chosen = values.index(optimum)
        return optimum, {
            atom: Decimal(1) if index == chosen else Decimal(0)
            for index, atom in enumerate(atoms)
        }
    index_by_atom = {atom: index for index, atom in enumerate(atoms)}
    matrix: list[list[float]] = []
    bounds: list[float] = []
    matrix.append([1.0] * len(atoms))
    bounds.append(1.0)
    matrix.append([-1.0] * len(atoms))
    bounds.append(-1.0)
    for item in constraints:
        assert item.lower_share is not None and item.upper_share is not None
        indicator = [0.0] * len(atoms)
        for atom in item.assignment_atom_ids:
            indicator[index_by_atom[atom]] = 1.0
        matrix.append(indicator)
        bounds.append(float(item.upper_share))
        matrix.append([-value for value in indicator])
        bounds.append(-float(item.lower_share))
    objective = [float(coefficients.get(atom, Decimal(0))) for atom in atoms]
    if not maximize:
        objective = [-value for value in objective]
    status, optimum, solution = _LinearProgram(matrix, bounds, objective).solve()
    if status != "optimal":
        raise OrderLModelError("partial assignment constraints define an infeasible share polytope")
    if not maximize:
        optimum = -optimum
    optimum_decimal = Decimal(format(max(0.0, min(1.0, optimum)), ".12g"))
    shares = {
        atom: Decimal(format(max(0.0, solution[index]), ".15g"))
        for index, atom in enumerate(atoms)
    }
    total = sum(shares.values(), Decimal(0))
    if total <= 0:
        raise OrderLModelError("assignment polytope solver returned zero total mass")
    shares = {atom: value / total for atom, value in shares.items()}
    return optimum_decimal, shares


def _validate_partial_assignment_feasibility(
    assignment_evidence: Sequence[AssignmentEvidence],
    atoms_by_profile: Mapping[str, set[str]],
) -> None:
    for profile, atoms in atoms_by_profile.items():
        constraints = _partial_assignment_constraints(profile, assignment_evidence)
        if constraints:
            _solve_assignment_polytope(
                sorted(atoms), constraints, {}, maximize=True
            )


def _constrain_assignment_draw(
    atoms: Sequence[str],
    unconstrained: Mapping[str, Decimal],
    constraints: Sequence[AssignmentEvidence],
) -> dict[str, Decimal]:
    """Radially project one common-prior draw onto a feasible constrained-share polytope."""
    if not constraints:
        return dict(unconstrained)
    _, anchor = _solve_assignment_polytope(atoms, constraints, {}, maximize=True)
    maximum_lambda = Decimal(1)
    for item in constraints:
        assert item.lower_share is not None and item.upper_share is not None
        anchor_sum = sum((anchor[atom] for atom in item.assignment_atom_ids), Decimal(0))
        draw_sum = sum((unconstrained[atom] for atom in item.assignment_atom_ids), Decimal(0))
        slope = draw_sum - anchor_sum
        if slope > 0:
            maximum_lambda = min(
                maximum_lambda, max(Decimal(0), (item.upper_share - anchor_sum) / slope)
            )
        elif slope < 0:
            maximum_lambda = min(
                maximum_lambda, max(Decimal(0), (item.lower_share - anchor_sum) / slope)
            )
    projected = {
        atom: anchor[atom] + maximum_lambda * (unconstrained[atom] - anchor[atom])
        for atom in atoms
    }
    running = sum((projected[atom] for atom in atoms[:-1]), Decimal(0))
    projected[atoms[-1]] = Decimal(1) - running
    tolerance = Decimal("1e-9")
    for item in constraints:
        assert item.lower_share is not None and item.upper_share is not None
        value = sum((projected[atom] for atom in item.assignment_atom_ids), Decimal(0))
        if value < item.lower_share - tolerance or value > item.upper_share + tolerance:
            raise OrderLModelError("constrained assignment draw escaped its feasible polytope")
    return projected


def rank_order_l_id(
    cells: Sequence[Cell], observations: Sequence[Observation]
) -> list[dict[str, Any]]:
    """L-ID: aggregate finite burden bounds and conservative rank sets."""
    observations_by_cell: dict[str, list[Observation]] = defaultdict(list)
    for observation in observations:
        observations_by_cell[observation.cell_id].append(observation)
    by_target: dict[str, list[Cell]] = defaultdict(list)
    atoms_by_profile: dict[str, set[str]] = defaultdict(set)
    for cell in cells:
        by_target[cell.language_target_id].append(cell)
        atoms_by_profile[cell.person_profile_id].add(cell.assignment_atom_id)

    def cell_need_bounds(cell: Cell) -> tuple[Decimal, Decimal, str]:
        method = "structural_zero" if cell.eligibility_status == "STRUCTURAL_ZERO" else cell.id_bound_method
        if method == "structural_zero":
            return Decimal(0), Decimal(0), method
        if method == "logical_0_1":
            return Decimal(0), Decimal(1), method
        if method in {"supplied_construct_bound", "frechet_bound"}:
            assert cell.id_need_low is not None and cell.id_need_high is not None
            return cell.id_need_low, cell.id_need_high, method
        if method == "direct_endpoint_census":
            if cell.assignment_mode != "fixed_direct":
                raise OrderLModelError(
                    f"{cell.cell_id} direct endpoint census requires a fixed direct cohort assignment"
                )
            direct = [
                item for item in observations_by_cell.get(cell.cell_id, [])
                if item.kind == "direct_endpoint_count"
                and item.source_scope == "exact_target"
                and item.sampling_design == "census"
            ]
            if len(direct) != 1:
                raise OrderLModelError(
                    f"{cell.cell_id} direct_endpoint_census requires exactly one exact-target census endpoint count"
                )
            observation = direct[0]
            if not (
                cell.population_low == cell.population_high
                and cell.population_mode == cell.population_low
                and observation.denominator == cell.population_low
                and observation.denominator > 0
            ):
                raise OrderLModelError(
                    f"{cell.cell_id} direct endpoint census denominator must equal its exact positive population"
                )
            # A direct full-endpoint numerator is converted to its exact cohort
            # rate only so the common finite-population allocation algebra can
            # be applied.  No component proxy is multiplied into this path.
            rate = observation.numerator / observation.denominator
            return rate, rate, method
        raise OrderLModelError(f"unsupported ID bound method: {method}")  # pragma: no cover

    records: list[dict[str, Any]] = []
    for target_id, target_cells in sorted(by_target.items()):
        low_total = Decimal(0)
        high_total = Decimal(0)
        methods: list[str] = []
        target_by_profile: dict[str, list[Cell]] = defaultdict(list)
        for cell in target_cells:
            target_by_profile[cell.person_profile_id].append(cell)
        for profile, profile_target_cells in sorted(target_by_profile.items()):
            representative = profile_target_cells[0]
            if representative.assignment_mode == "fixed_direct":
                coefficient_low = Decimal(0)
                coefficient_high = Decimal(0)
                for cell in profile_target_cells:
                    need_low, need_high, method = cell_need_bounds(cell)
                    methods.append(method)
                    assert cell.assignment_weight is not None
                    coefficient_low += cell.assignment_weight * need_low
                    coefficient_high += cell.assignment_weight * need_high
            else:
                # The latent atom shares live on one simplex.  Optimizing a
                # linear burden over that simplex selects the minimum/maximum
                # atom coefficient, rather than assigning the full territorial
                # ceiling independently to every listed language row.
                atom_low = {atom: Decimal(0) for atom in atoms_by_profile[profile]}
                atom_high = {atom: Decimal(0) for atom in atoms_by_profile[profile]}
                for cell in profile_target_cells:
                    need_low, need_high, method = cell_need_bounds(cell)
                    methods.append(method)
                    atom_low[cell.assignment_atom_id] += cell.assignment_within_atom_weight * need_low
                    atom_high[cell.assignment_atom_id] += cell.assignment_within_atom_weight * need_high
                coefficient_low = min(atom_low.values())
                coefficient_high = max(atom_high.values())
            if not Decimal(0) <= coefficient_low <= coefficient_high <= Decimal(1):
                raise OrderLModelError(
                    f"L-ID assignment coefficients for {target_id}/{profile} violate one-person bounds"
                )
            low_total += representative.population_low * coefficient_low
            high_total += representative.population_high * coefficient_high
        records.append(
            {
                "order_l_variant": "L-ID",
                "order_id": "LANGUAGE_TARGET_UNMET_NEED_ID_V2",
                "schema_version": SCHEMA_VERSION,
                "language_target_id": target_id,
                "language_target_label": target_cells[0].language_target_label,
                "benefit_unit": target_cells[0].benefit_unit,
                "universe_version": target_cells[0].universe_version,
                "cell_count": len(target_cells),
                "person_profile_count": len({cell.person_profile_id for cell in target_cells}),
                "cell_ids": ";".join(sorted(cell.cell_id for cell in target_cells)),
                "evidence_tiers": ";".join(sorted({cell.evidence_tier for cell in target_cells})),
                "assignment_modes": ";".join(sorted({cell.assignment_mode for cell in target_cells})),
                "bound_methods": ";".join(sorted(set(methods))),
                "burden_lower_bound": low_total,
                "burden_upper_bound": high_total,
                "identification_status": "point_identified" if low_total == high_total else "partial_identification",
                "possible_rank_best": None,
                "possible_rank_worst": None,
                "possible_rank_set": "",
                "top10_status": "",
                "top100_status": "",
            }
        )
    n = len(records)
    for row in records:
        low = row["burden_lower_bound"]
        high = row["burden_upper_bound"]
        best = 1 + sum(other["burden_lower_bound"] > high for other in records if other is not row)
        worst = n - sum(other["burden_upper_bound"] < low for other in records if other is not row)
        row["possible_rank_best"] = best
        row["possible_rank_worst"] = worst
        row["possible_rank_set"] = str(best) if best == worst else f"{best}-{worst}"
        row["top10_status"] = _top_status(best, worst, 10)
        row["top100_status"] = _top_status(best, worst, 100)
    records.sort(key=lambda row: (row["possible_rank_best"], row["possible_rank_worst"], row["language_target_id"]))
    return records


def _uniform(seed: str, *parts: str) -> float:
    payload = "\x1f".join((DRAW_ALGORITHM_VERSION, seed, *parts)).encode("utf-8")
    integer = int.from_bytes(hashlib.sha256(payload).digest(), "big")
    return (integer + 0.5) / float(1 << 256)


def _normal(seed: str, *parts: str) -> float:
    u1 = max(_uniform(seed, *parts, "u1"), 1e-300)
    u2 = _uniform(seed, *parts, "u2")
    return math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)


def _logit(probability: float) -> float:
    probability = min(max(probability, 1e-9), 1.0 - 1e-9)
    return math.log(probability / (1.0 - probability))


def _logistic(value: float) -> float:
    if value >= 0:
        inverse = math.exp(-value)
        return 1.0 / (1.0 + inverse)
    direct = math.exp(value)
    return direct / (1.0 + direct)


def _population_draw(cell: Cell, seed: str, draw_id: str) -> Decimal:
    if cell.population_low == cell.population_high:
        return cell.population_low
    low = float(cell.population_low)
    high = float(cell.population_high)
    u = _uniform(seed, "population", cell.person_profile_id, draw_id)
    if cell.population_mode is None:
        return _d(low + (high - low) * u)
    mode = float(cell.population_mode)
    split = (mode - low) / (high - low)
    if u < split:
        value = low + math.sqrt(u * (high - low) * (mode - low))
    else:
        value = high - math.sqrt((1.0 - u) * (high - low) * (high - mode))
    return _d(value)


def _gamma_draw(shape: float, seed: str, *parts: str) -> float:
    """Deterministic Marsaglia-Tsang gamma draw addressed by public hash keys."""
    if shape <= 0:
        raise OrderLModelError("gamma shape must be positive")
    if shape < 1.0:
        base = _gamma_draw(shape + 1.0, seed, *parts, "boost")
        uniform = max(_uniform(seed, *parts, "shape-lt-one"), 1e-300)
        return base * (uniform ** (1.0 / shape))
    d_value = shape - (1.0 / 3.0)
    c_value = 1.0 / math.sqrt(9.0 * d_value)
    for attempt in range(1000):
        normal = _normal(seed, *parts, "attempt", str(attempt))
        transformed = 1.0 + c_value * normal
        if transformed <= 0:
            continue
        transformed = transformed**3
        uniform = _uniform(seed, *parts, "accept", str(attempt))
        if uniform < 1.0 - 0.0331 * (normal**4):
            return d_value * transformed
        if math.log(max(uniform, 1e-300)) < 0.5 * normal * normal + d_value * (
            1.0 - transformed + math.log(transformed)
        ):
            return d_value * transformed
    raise OrderLModelError("deterministic gamma sampler exceeded its bounded attempt limit")


def _profile_assignment_draws(
    cells: Sequence[Cell],
    assignment_evidence: Sequence[AssignmentEvidence],
    prior: PriorFamily,
    *,
    public_seed: str,
    draw_id: str,
) -> dict[str, Decimal]:
    """Return effective cell shares that sum exactly to one per person profile."""
    by_profile: dict[str, list[Cell]] = defaultdict(list)
    for cell in cells:
        by_profile[cell.person_profile_id].append(cell)
    evidence_count = {
        (item.person_profile_id, item.assignment_atom_id): item.numerator
        for item in assignment_evidence
    }
    result: dict[str, Decimal] = {}
    for profile, profile_cells in sorted(by_profile.items()):
        mode = profile_cells[0].assignment_mode
        if mode == "fixed_direct":
            for cell in profile_cells:
                assert cell.assignment_weight is not None
                result[cell.cell_id] = cell.assignment_weight
            if sum((result[cell.cell_id] for cell in profile_cells), Decimal(0)) != Decimal(1):
                raise OrderLModelError(f"fixed assignment lost mass for profile {profile}")
            continue
        atoms = sorted({cell.assignment_atom_id for cell in profile_cells})
        raw_values: list[Decimal] = []
        for atom in atoms:
            shape = prior.assignment_concentration + evidence_count.get((profile, atom), Decimal(0))
            raw_values.append(
                _d(
                    _gamma_draw(
                        float(shape), public_seed, "assignment-dirichlet", profile, atom,
                        draw_id,
                    )
                )
            )
        total = sum(raw_values, Decimal(0))
        atom_shares: dict[str, Decimal] = {}
        running = Decimal(0)
        for index, (atom, raw_value) in enumerate(zip(atoms, raw_values)):
            share = Decimal(1) - running if index == len(atoms) - 1 else raw_value / total
            atom_shares[atom] = share
            running += share
        for atom in atoms:
            atom_cells = sorted(
                (cell for cell in profile_cells if cell.assignment_atom_id == atom),
                key=lambda cell: cell.cell_id,
            )
            atom_running = Decimal(0)
            for index, cell in enumerate(atom_cells):
                effective = (
                    atom_shares[atom] - atom_running
                    if index == len(atom_cells) - 1
                    else atom_shares[atom] * cell.assignment_within_atom_weight
                )
                result[cell.cell_id] = effective
                atom_running += effective
        if sum((result[cell.cell_id] for cell in profile_cells), Decimal(0)) != Decimal(1):
            raise OrderLModelError(f"latent assignment lost mass for profile {profile}")
    return result


def _observation_linearization(
    observation: Observation,
    measurement_models: Mapping[str, MeasurementModel],
    transport_models: Mapping[str, TransportModel],
    *,
    source_effect: float,
    transport_effect: float,
    calibration_effect: float,
) -> tuple[float, float]:
    n = float(observation.denominator)
    y = float(observation.numerator)
    observed_probability = (y + 0.5) / (n + 1.0)
    if observation.kind == "direct_endpoint_count":
        latent_probability = observed_probability
        attenuation = 1.0
        calibration_variance = 0.0
    else:
        model = measurement_models[observation.measurement_model_id]
        sensitivity = float(model.sensitivity)
        specificity = float(model.specificity)
        attenuation = sensitivity + specificity - 1.0
        latent_probability = (observed_probability - (1.0 - specificity)) / attenuation
        latent_probability = min(max(latent_probability, 1e-6), 1.0 - 1e-6)
        calibration_variance = float(model.calibration_logit_sd) ** 2
    z = _logit(latent_probability) - source_effect - transport_effect - calibration_effect
    information = max(n * observed_probability * (1.0 - observed_probability) * attenuation * attenuation, 1e-6)
    variance = (1.0 / information) + calibration_variance
    return z, variance


def generate_public_joint_draws(
    cells: Sequence[Cell],
    observations: Sequence[Observation],
    measurement_models: Mapping[str, MeasurementModel],
    transport_models: Mapping[str, TransportModel],
    prior_registry: PriorRegistry,
    assignment_evidence: Sequence[AssignmentEvidence] = (),
    *,
    draw_count: int,
    public_seed: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Generate deterministic, complete target and cell draws for every prior family."""
    if draw_count < 16:
        raise OrderLModelError("draw_count must be at least 16")
    if not public_seed:
        raise OrderLModelError("a nonblank public_seed is required")
    cell_by_id = {cell.cell_id: cell for cell in cells}
    observations_by_model_cell: dict[tuple[str, str], list[Observation]] = defaultdict(list)
    for observation in observations:
        cell = cell_by_id[observation.cell_id]
        observations_by_model_cell[(cell.person_profile_id, cell.assignment_atom_id)].append(observation)
    targets = sorted({cell.language_target_id for cell in cells})
    cells_by_target: dict[str, list[Cell]] = defaultdict(list)
    for cell in cells:
        cells_by_target[cell.language_target_id].append(cell)
    source_groups: dict[str, Decimal] = {}
    for observation in observations:
        source_groups.setdefault(observation.correlation_group_id, observation.source_effect_sd)
    target_rows: list[dict[str, Any]] = []
    cell_rows: list[dict[str, Any]] = []
    effect_rows: list[dict[str, Any]] = []
    draw_set_root = sha256_bytes(
        canonical_json_bytes(
            {
                "model_version": MODEL_VERSION,
                "algorithm": DRAW_ALGORITHM_VERSION,
                "prior_registry_sha256": prior_registry.sha256,
                "public_seed": public_seed,
                "draw_count": draw_count,
                "universe_version": cells[0].universe_version,
                "universe_semantic_hash": cells[0].universe_semantic_hash,
                "cell_ids": sorted(cell.cell_id for cell in cells),
                "observation_ids": sorted(observation.observation_id for observation in observations),
                "assignment_evidence_ids": sorted(item.evidence_id for item in assignment_evidence),
            }
        )
    )[:20]
    for draw_index in range(1, draw_count + 1):
        draw_id = f"{draw_index:06d}"
        source_effects = {
            group: float(sd) * _normal(public_seed, "source-effect", group, draw_id)
            for group, sd in sorted(source_groups.items())
        }
        transport_effects = {
            model_id: float(model.logit_shift_mean)
            + float(model.logit_shift_sd) * _normal(public_seed, "transport-effect", model_id, draw_id)
            for model_id, model in sorted(transport_models.items())
        }
        calibration_effects = {
            model_id: float(model.calibration_logit_sd)
            * _normal(public_seed, "measurement-effect", model_id, draw_id)
            for model_id, model in sorted(measurement_models.items())
        }
        for group, value in sorted(source_effects.items()):
            effect_rows.append(
                {
                    "draw_algorithm_version": DRAW_ALGORITHM_VERSION,
                    "draw_id": draw_id,
                    "effect_type": "source_correlation_group",
                    "effect_id": group,
                    "effect_value": _d(value),
                }
            )
        for model_id, value in sorted(transport_effects.items()):
            effect_rows.append(
                {
                    "draw_algorithm_version": DRAW_ALGORITHM_VERSION,
                    "draw_id": draw_id,
                    "effect_type": "transport_model",
                    "effect_id": model_id,
                    "effect_value": _d(value),
                }
            )
        for model_id, value in sorted(calibration_effects.items()):
            effect_rows.append(
                {
                    "draw_algorithm_version": DRAW_ALGORITHM_VERSION,
                    "draw_id": draw_id,
                    "effect_type": "measurement_model",
                    "effect_id": model_id,
                    "effect_value": _d(value),
                }
            )
        profile_population = {
            cell.person_profile_id: _population_draw(cell, public_seed, draw_id)
            for cell in cells
        }
        for family_id, prior in sorted(prior_registry.families.items()):
            draw_set_id = f"order-l-v2::{family_id}::{draw_set_root}"
            target_burdens = {target_id: Decimal(0) for target_id in targets}
            stage_effects: dict[tuple[str, str], float] = {}
            assignment_weights = _profile_assignment_draws(
                cells,
                assignment_evidence,
                prior,
                public_seed=public_seed,
                draw_id=draw_id,
            )
            atom_cells = {
                key: sorted(
                    (
                        member for member in cells
                        if (member.person_profile_id, member.assignment_atom_id) == key
                    ),
                    key=lambda member: member.cell_id,
                )
                for key in {
                    (member.person_profile_id, member.assignment_atom_id) for member in cells
                }
            }
            atom_burden_running: dict[tuple[str, str], Decimal] = defaultdict(Decimal)
            for cell in cells:
                stage_key = (cell.stage_id, cell.endpoint_id)
                if stage_key not in stage_effects:
                    stage_effects[stage_key] = float(prior.intercept_sd) * _normal(
                        public_seed, "stage-endpoint", stage_key[0], stage_key[1], draw_id
                    )
                population = profile_population[cell.person_profile_id]
                model_cell_key = (cell.person_profile_id, cell.assignment_atom_id)
                cell_observations = observations_by_model_cell.get(model_cell_key, [])
                if cell.eligibility_status == "STRUCTURAL_ZERO":
                    theta = Decimal(0)
                    posterior_eta_mean = None
                    posterior_eta_sd = None
                    source_effect_sum = Decimal(0)
                    transport_effect_sum = Decimal(0)
                    calibration_effect_sum = Decimal(0)
                else:
                    prior_eta = _logit(float(prior.unmet_need_mean)) + stage_effects[stage_key]
                    prior_variance = float(prior.cell_sd) ** 2
                    precision = 1.0 / prior_variance
                    weighted_location = prior_eta * precision
                    for observation in cell_observations:
                        source_effect = source_effects[observation.correlation_group_id]
                        transport_effect = transport_effects.get(observation.transport_model_id, 0.0)
                        calibration_effect = calibration_effects.get(observation.measurement_model_id, 0.0)
                        location, variance = _observation_linearization(
                            observation,
                            measurement_models,
                            transport_models,
                            source_effect=source_effect,
                            transport_effect=transport_effect,
                            calibration_effect=calibration_effect,
                        )
                        observation_precision = 1.0 / variance
                        precision += observation_precision
                        weighted_location += location * observation_precision
                    posterior_eta_mean = weighted_location / precision
                    posterior_eta_sd = math.sqrt(1.0 / precision)
                    residual = _normal(
                        public_seed,
                        "cell-posterior",
                        model_cell_key[0],
                        model_cell_key[1],
                        draw_id,
                    )
                    theta = _d(_logistic(posterior_eta_mean + posterior_eta_sd * residual))
                    source_effect_sum = _d(
                        sum(
                            source_effects[group]
                            for group in {item.correlation_group_id for item in cell_observations}
                        )
                    )
                    transport_effect_sum = _d(
                        sum(
                            transport_effects[model_id]
                            for model_id in {item.transport_model_id for item in cell_observations if item.transport_model_id}
                        )
                    )
                    calibration_effect_sum = _d(
                        sum(
                            calibration_effects[model_id]
                            for model_id in {item.measurement_model_id for item in cell_observations if item.measurement_model_id}
                        )
                    )
                assignment_weight_draw = assignment_weights[cell.cell_id]
                atom_assignment_share = sum(
                    (assignment_weights[member.cell_id] for member in atom_cells[model_cell_key]),
                    Decimal(0),
                )
                atom_burden = population * atom_assignment_share * theta
                if cell.cell_id == atom_cells[model_cell_key][-1].cell_id:
                    burden = atom_burden - atom_burden_running[model_cell_key]
                else:
                    burden = atom_burden * assignment_weight_draw / atom_assignment_share
                    atom_burden_running[model_cell_key] += burden
                target_burdens[cell.language_target_id] += burden
                cell_rows.append(
                    {
                        "model_version": MODEL_VERSION,
                        "draw_algorithm_version": DRAW_ALGORITHM_VERSION,
                        "prior_family_id": family_id,
                        "draw_set_id": draw_set_id,
                        "draw_id": draw_id,
                        "cell_id": cell.cell_id,
                        "person_profile_id": cell.person_profile_id,
                        "assignment_mode": cell.assignment_mode,
                        "assignment_atom_id": cell.assignment_atom_id,
                        "language_target_id": cell.language_target_id,
                        "population_draw": population,
                        "assignment_weight_draw": assignment_weight_draw,
                        "need_probability_draw": theta,
                        "burden_draw": burden,
                        "source_shared_effect_sum": source_effect_sum,
                        "transport_effect_sum": transport_effect_sum,
                        "measurement_effect_sum": calibration_effect_sum,
                        "posterior_eta_mean": _d(posterior_eta_mean) if posterior_eta_mean is not None else None,
                        "posterior_eta_sd": _d(posterior_eta_sd) if posterior_eta_sd is not None else None,
                    }
                )
            for target_id in targets:
                target_rows.append(
                    {
                        "order_l_variant": "L-M",
                        "order_id": "LANGUAGE_TARGET_EXPECTED_NEED_MODEL_V2",
                        "model_version": MODEL_VERSION,
                        "prior_family_id": family_id,
                        "draw_set_id": draw_set_id,
                        "draw_id": draw_id,
                        "language_target_id": target_id,
                        "benefit_unit": cells_by_target[target_id][0].benefit_unit,
                        "need_burden_draw": target_burdens[target_id],
                    }
                )
    target_rows.sort(key=lambda row: (row["prior_family_id"], row["draw_id"], row["language_target_id"]))
    cell_rows.sort(key=lambda row: (row["prior_family_id"], row["draw_id"], row["cell_id"]))
    effect_rows.sort(key=lambda row: (row["draw_id"], row["effect_type"], row["effect_id"]))
    return target_rows, cell_rows, effect_rows


def validate_complete_target_draw_grid(
    rows: Sequence[Mapping[str, Any]],
    *,
    target_ids: Iterable[str],
    prior_family_ids: Iterable[str],
    draw_count: int,
) -> None:
    expected_targets = set(target_ids)
    expected_families = set(prior_family_ids)
    expected_draw_ids = {f"{index:06d}" for index in range(1, draw_count + 1)}
    seen: set[tuple[str, str, str]] = set()
    family_draws: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        family = _text(row.get("prior_family_id"))
        draw_id = _text(row.get("draw_id"))
        target_id = _text(row.get("language_target_id"))
        if family not in expected_families or draw_id not in expected_draw_ids or target_id not in expected_targets:
            raise OrderLModelError("joint draws contain an unknown family, draw, or exact target")
        key = (family, draw_id, target_id)
        if key in seen:
            raise OrderLModelError(f"duplicate L-M joint draw cell: {key}")
        seen.add(key)
        family_draws[family].add(draw_id)
        value = _decimal(row.get("need_burden_draw"), label=f"joint draw {key}", required=True)
        if value is None or value < 0:
            raise OrderLModelError(f"joint draw {key} must be finite and nonnegative")
    expected = {
        (family, draw_id, target_id)
        for family in expected_families
        for draw_id in expected_draw_ids
        for target_id in expected_targets
    }
    if seen != expected:
        missing = sorted(expected - seen)[:5]
        extra = sorted(seen - expected)[:5]
        raise OrderLModelError(
            "incomplete L-M target x draw x prior grid; no posterior rank is permitted "
            f"(missing examples={missing}, extra examples={extra})"
        )
    if any(draw_ids != expected_draw_ids for draw_ids in family_draws.values()):
        raise OrderLModelError("all prior families must use the same complete public draw grid")


def _quantile(values: Sequence[Decimal], probability: Decimal) -> Decimal:
    if not values:
        raise OrderLModelError("cannot summarize an empty posterior")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = probability * Decimal(len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - Decimal(lower)
    return ordered[lower] * (Decimal(1) - weight) + ordered[upper] * weight


def _mean(values: Sequence[Decimal]) -> Decimal:
    if not values:
        raise OrderLModelError("cannot summarize an empty posterior")
    return sum(values, Decimal(0)) / Decimal(len(values))


def _prior_diagnostics(
    cells: Sequence[Cell],
    observations: Sequence[Observation],
    measurement_models: Mapping[str, MeasurementModel],
    prior: PriorFamily,
    assignment_evidence: Sequence[AssignmentEvidence] = (),
) -> dict[str, dict[str, Any]]:
    cell_by_id = {cell.cell_id: cell for cell in cells}
    observations_by_model_cell: dict[tuple[str, str], list[Observation]] = defaultdict(list)
    for observation in observations:
        cell = cell_by_id[observation.cell_id]
        observations_by_model_cell[(cell.person_profile_id, cell.assignment_atom_id)].append(observation)
    atoms_by_profile: dict[str, set[str]] = defaultdict(set)
    for cell in cells:
        atoms_by_profile[cell.person_profile_id].add(cell.assignment_atom_id)
    evidence_count = {
        (item.person_profile_id, item.assignment_atom_id): item.numerator
        for item in assignment_evidence
    }
    evidence_total: dict[str, Decimal] = defaultdict(Decimal)
    for item in assignment_evidence:
        evidence_total[item.person_profile_id] += item.numerator
    weighted_total: dict[str, Decimal] = defaultdict(Decimal)
    weighted_prior_only: dict[str, Decimal] = defaultdict(Decimal)
    weighted_prior_fraction: dict[str, Decimal] = defaultdict(Decimal)
    prior_only_count: dict[str, int] = defaultdict(int)
    cell_count: dict[str, int] = defaultdict(int)
    prior_precision = Decimal(1) / (prior.cell_sd * prior.cell_sd)
    for cell in cells:
        target_id = cell.language_target_id
        population_expectation = (
            cell.population_low + cell.population_high
        ) / Decimal(2) if cell.population_mode is None else (
            cell.population_low + cell.population_mode + cell.population_high
        ) / Decimal(3)
        if cell.assignment_mode == "fixed_direct":
            assert cell.assignment_weight is not None
            assignment_expectation = cell.assignment_weight
        else:
            atom_count = Decimal(len(atoms_by_profile[cell.person_profile_id]))
            atom_expectation = (
                prior.assignment_concentration
                + evidence_count.get((cell.person_profile_id, cell.assignment_atom_id), Decimal(0))
            ) / (
                prior.assignment_concentration * atom_count
                + evidence_total[cell.person_profile_id]
            )
            assignment_expectation = atom_expectation * cell.assignment_within_atom_weight
        weight = population_expectation * assignment_expectation
        cell_observations = observations_by_model_cell.get(
            (cell.person_profile_id, cell.assignment_atom_id), []
        )
        likelihood_precision = Decimal(0)
        for observation in cell_observations:
            _, variance = _observation_linearization(
                observation,
                measurement_models,
                {},
                source_effect=0.0,
                transport_effect=0.0,
                calibration_effect=0.0,
            )
            likelihood_precision += _d(1.0 / variance)
        fraction = prior_precision / (prior_precision + likelihood_precision)
        weighted_total[target_id] += weight
        weighted_prior_fraction[target_id] += weight * fraction
        cell_count[target_id] += 1
        if not cell_observations:
            weighted_prior_only[target_id] += weight
            prior_only_count[target_id] += 1
    output: dict[str, dict[str, Any]] = {}
    for target_id in weighted_total:
        denominator = weighted_total[target_id]
        output[target_id] = {
            "model_cell_count": cell_count[target_id],
            "prior_only_cell_count": prior_only_count[target_id],
            "prior_only_population_fraction": (
                weighted_prior_only[target_id] / denominator if denominator else Decimal(0)
            ),
            "prior_dominance_fraction": (
                weighted_prior_fraction[target_id] / denominator if denominator else Decimal(1)
            ),
        }
    return output


def summarize_order_l_m(
    target_draw_rows: Sequence[Mapping[str, Any]],
    cells: Sequence[Cell],
    observations: Sequence[Observation],
    measurement_models: Mapping[str, MeasurementModel],
    prior_registry: PriorRegistry,
    l_id_rows: Sequence[Mapping[str, Any]],
    assignment_evidence: Sequence[AssignmentEvidence] = (),
    *,
    prior_family_id: str = REFERENCE_PRIOR_FAMILY,
    draw_count: int,
) -> list[dict[str, Any]]:
    target_ids = sorted({cell.language_target_id for cell in cells})
    validate_complete_target_draw_grid(
        target_draw_rows,
        target_ids=target_ids,
        prior_family_ids=prior_registry.families,
        draw_count=draw_count,
    )
    if prior_family_id not in prior_registry.families:
        raise OrderLModelError(f"unknown prior family: {prior_family_id}")
    by_target: dict[str, dict[str, Decimal]] = defaultdict(dict)
    draw_set_ids: set[str] = set()
    for row in target_draw_rows:
        if row["prior_family_id"] != prior_family_id:
            continue
        target_id = _text(row["language_target_id"])
        draw_id = _text(row["draw_id"])
        value = _decimal(row["need_burden_draw"], label="need_burden_draw", required=True)
        assert value is not None
        by_target[target_id][draw_id] = value
        draw_set_ids.add(_text(row["draw_set_id"]))
    if len(draw_set_ids) != 1:
        raise OrderLModelError("one prior family must have exactly one draw_set_id")
    label_by_target = {cell.language_target_id: cell.language_target_label for cell in cells}
    cells_by_target: dict[str, list[Cell]] = defaultdict(list)
    for cell in cells:
        cells_by_target[cell.language_target_id].append(cell)
    id_by_target = {str(row["language_target_id"]): row for row in l_id_rows}
    diagnostics = _prior_diagnostics(
        cells,
        observations,
        measurement_models,
        prior_registry.families[prior_family_id],
        assignment_evidence,
    )
    records: list[dict[str, Any]] = []
    for target_id in target_ids:
        values = list(by_target[target_id].values())
        records.append(
            {
                "order_l_variant": "L-M",
                "order_id": "LANGUAGE_TARGET_EXPECTED_NEED_MODEL_V2",
                "schema_version": SCHEMA_VERSION,
                "model_version": MODEL_VERSION,
                "prior_family_id": prior_family_id,
                "draw_set_id": next(iter(draw_set_ids)),
                "language_target_id": target_id,
                "language_target_label": label_by_target[target_id],
                "benefit_unit": cells_by_target[target_id][0].benefit_unit,
                "decision_scope": "conditional_on_supplied_finite_roster",
                "posterior_mean_need": _mean(values),
                "posterior_median_need": _quantile(values, Decimal("0.50")),
                "posterior_p05_need": _quantile(values, Decimal("0.05")),
                "posterior_p95_need": _quantile(values, Decimal("0.95")),
                "posterior_draw_count": len(values),
                "decision_rank": None,
                "decision_tie_group_id": "",
                "decision_rank_low": None,
                "decision_rank_high": None,
                "posterior_rank_p05": None,
                "posterior_rank_p50": None,
                "posterior_rank_p95": None,
                "posterior_top10_probability": None,
                "posterior_top100_probability": None,
                "top10_boundary_tie": False,
                "top100_boundary_tie": False,
                "l_id_burden_lower_bound": id_by_target[target_id]["burden_lower_bound"],
                "l_id_burden_upper_bound": id_by_target[target_id]["burden_upper_bound"],
                "l_id_possible_rank_best": id_by_target[target_id]["possible_rank_best"],
                "l_id_possible_rank_worst": id_by_target[target_id]["possible_rank_worst"],
                "evidence_tiers": ";".join(sorted({cell.evidence_tier for cell in cells_by_target[target_id]})),
                **diagnostics[target_id],
            }
        )
    means = sorted({row["posterior_mean_need"] for row in records}, reverse=True)
    for index, value in enumerate(means, start=1):
        members = [row for row in records if row["posterior_mean_need"] == value]
        rank = 1 + sum(row["posterior_mean_need"] > value for row in records)
        tie_group = f"L-M::{prior_family_id}::tie::{index:04d}"
        for row in members:
            row["decision_rank"] = rank
            row["decision_tie_group_id"] = tie_group
            row["decision_rank_low"] = rank
            row["decision_rank_high"] = rank + len(members) - 1
            row["top10_boundary_tie"] = rank <= 10 <= rank + len(members) - 1 and len(members) > 1
            row["top100_boundary_tie"] = rank <= 100 <= rank + len(members) - 1 and len(members) > 1
    rank_samples: dict[str, list[Decimal]] = defaultdict(list)
    top10_hits: dict[str, int] = defaultdict(int)
    top100_hits: dict[str, int] = defaultdict(int)
    for draw_id in sorted(next(iter(by_target.values()))):
        scores = {target_id: by_target[target_id][draw_id] for target_id in target_ids}
        for target_id, score in scores.items():
            rank = 1 + sum(other > score for other in scores.values())
            rank_samples[target_id].append(Decimal(rank))
            top10_hits[target_id] += rank <= 10
            top100_hits[target_id] += rank <= 100
    for row in records:
        target_id = row["language_target_id"]
        samples = rank_samples[target_id]
        row["posterior_rank_p05"] = _quantile(samples, Decimal("0.05"))
        row["posterior_rank_p50"] = _quantile(samples, Decimal("0.50"))
        row["posterior_rank_p95"] = _quantile(samples, Decimal("0.95"))
        row["posterior_top10_probability"] = Decimal(top10_hits[target_id]) / Decimal(draw_count)
        row["posterior_top100_probability"] = Decimal(top100_hits[target_id]) / Decimal(draw_count)
    records.sort(key=lambda row: (row["decision_rank"], row["language_target_id"]))
    return records


def summarize_prior_sensitivity(
    target_draw_rows: Sequence[Mapping[str, Any]],
    cells: Sequence[Cell],
    observations: Sequence[Observation],
    measurement_models: Mapping[str, MeasurementModel],
    prior_registry: PriorRegistry,
    l_id_rows: Sequence[Mapping[str, Any]],
    assignment_evidence: Sequence[AssignmentEvidence] = (),
    *,
    draw_count: int,
) -> list[dict[str, Any]]:
    summaries = {
        family_id: summarize_order_l_m(
            target_draw_rows, cells, observations, measurement_models, prior_registry,
            l_id_rows, assignment_evidence, prior_family_id=family_id, draw_count=draw_count,
        )
        for family_id in sorted(prior_registry.families)
    }
    reference = {row["language_target_id"]: row for row in summaries[REFERENCE_PRIOR_FAMILY]}
    output: list[dict[str, Any]] = []
    for family_id, rows in summaries.items():
        for row in rows:
            baseline = reference[row["language_target_id"]]
            output.append(
                {
                    "model_version": MODEL_VERSION,
                    "prior_family_id": family_id,
                    "language_target_id": row["language_target_id"],
                    "posterior_mean_need": row["posterior_mean_need"],
                    "posterior_median_need": row["posterior_median_need"],
                    "posterior_p05_need": row["posterior_p05_need"],
                    "posterior_p95_need": row["posterior_p95_need"],
                    "decision_rank": row["decision_rank"],
                    "posterior_rank_p05": row["posterior_rank_p05"],
                    "posterior_rank_p50": row["posterior_rank_p50"],
                    "posterior_rank_p95": row["posterior_rank_p95"],
                    "posterior_top10_probability": row["posterior_top10_probability"],
                    "posterior_top100_probability": row["posterior_top100_probability"],
                    "prior_dominance_fraction": row["prior_dominance_fraction"],
                    "mean_change_from_reference": row["posterior_mean_need"] - baseline["posterior_mean_need"],
                    "rank_change_from_reference": row["decision_rank"] - baseline["decision_rank"],
                    "reference_top10_membership_stable": (row["decision_rank"] <= 10) == (baseline["decision_rank"] <= 10),
                    "reference_top100_membership_stable": (row["decision_rank"] <= 100) == (baseline["decision_rank"] <= 100),
                }
            )
    output.sort(key=lambda row: (row["prior_family_id"], row["decision_rank"], row["language_target_id"]))
    return output


def build_boundary_pairwise_probabilities(
    l_m_rows: Sequence[Mapping[str, Any]], target_draw_rows: Sequence[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    target_ids = [str(row["language_target_id"]) for row in l_m_rows]
    ranks = {str(row["language_target_id"]): int(row["decision_rank"]) for row in l_m_rows}
    reference_draws: dict[str, dict[str, Decimal]] = defaultdict(dict)
    for row in target_draw_rows:
        if row["prior_family_id"] == REFERENCE_PRIOR_FAMILY:
            value = _decimal(row["need_burden_draw"], label="need_burden_draw", required=True)
            assert value is not None
            reference_draws[str(row["language_target_id"])][str(row["draw_id"])] = value
    output: list[dict[str, Any]] = []
    for requested_k in (10, 100):
        effective_k = min(requested_k, len(target_ids))
        near = sorted(
            target_id for target_id in target_ids
            if max(1, effective_k - 1) <= ranks[target_id] <= effective_k + 1
        )
        for left_index, left in enumerate(near):
            for right in near[left_index + 1 :]:
                shared = sorted(set(reference_draws[left]) & set(reference_draws[right]))
                left_hits = sum(reference_draws[left][draw] > reference_draws[right][draw] for draw in shared)
                right_hits = sum(reference_draws[right][draw] > reference_draws[left][draw] for draw in shared)
                ties = len(shared) - left_hits - right_hits
                output.append(
                    {
                        "model_version": MODEL_VERSION,
                        "requested_boundary_k": requested_k,
                        "effective_boundary_rank": effective_k,
                        "language_target_id_a": left,
                        "language_target_id_b": right,
                        "draw_count": len(shared),
                        "probability_a_outranks_b": Decimal(left_hits) / Decimal(len(shared)),
                        "probability_b_outranks_a": Decimal(right_hits) / Decimal(len(shared)),
                        "probability_tie": Decimal(ties) / Decimal(len(shared)),
                    }
                )
    return output


def build_value_of_information_skeleton(
    cells: Sequence[Cell], observations: Sequence[Observation], l_id_rows: Sequence[Mapping[str, Any]],
    l_m_rows: Sequence[Mapping[str, Any]],
    assignment_evidence: Sequence[AssignmentEvidence] = (),
) -> list[dict[str, Any]]:
    observations_by_cell: dict[str, list[Observation]] = defaultdict(list)
    for observation in observations:
        observations_by_cell[observation.cell_id].append(observation)
    id_by_target = {str(row["language_target_id"]): row for row in l_id_rows}
    model_by_target = {str(row["language_target_id"]): row for row in l_m_rows}
    output: list[dict[str, Any]] = []
    assignment_evidence_profiles = {item.person_profile_id for item in assignment_evidence}
    for cell in cells:
        direct = [
            observation for observation in observations_by_cell.get(cell.cell_id, [])
            if observation.kind == "direct_endpoint_count"
            and observation.source_scope == "exact_target"
        ]
        if cell.eligibility_status == "STRUCTURAL_ZERO":
            continue
        identified = id_by_target[cell.language_target_id]
        modeled = model_by_target[cell.language_target_id]
        if not direct:
            output.append(
                {
                    "voi_table_role": "separate_evidence_acquisition_order_not_need_score",
                    "language_target_id": cell.language_target_id,
                    "stratum_id": cell.person_profile_id,
                    "cell_id": cell.cell_id,
                    "missing_construct": "direct_functional_access_endpoint",
                    "current_public_bounds": json.dumps(
                        {
                            "lower": _fmt(identified["burden_lower_bound"]),
                            "upper": _fmt(identified["burden_upper_bound"]),
                        }, sort_keys=True, separators=(",", ":")
                    ),
                    "current_top100_probability": modeled["posterior_top100_probability"],
                    "current_rank_interval": f"{_fmt(modeled['posterior_rank_p05'])}-{_fmt(modeled['posterior_rank_p95'])}",
                    "proposed_observation_endpoint": cell.endpoint_id,
                    "required_denominator_definition": cell.population_denominator_id,
                    "expected_rank_width_reduction": "",
                    "expected_regret_reduction": "",
                    "source_class_required": "public_empirical",
                    "voi_status": "SKELETON_NOT_COMPUTED_REQUIRES_PROSPECTIVE_DESIGN",
                }
            )
        if (
            cell.assignment_mode == "latent_symmetric"
            and cell.person_profile_id not in assignment_evidence_profiles
        ):
            output.append(
                {
                    "voi_table_role": "separate_evidence_acquisition_order_not_need_score",
                    "language_target_id": cell.language_target_id,
                    "stratum_id": cell.person_profile_id,
                    "cell_id": cell.cell_id,
                    "missing_construct": "multilingual_assignment_share",
                    "current_public_bounds": json.dumps(
                        {"lower": "0", "upper": "1"}, sort_keys=True, separators=(",", ":")
                    ),
                    "current_top100_probability": modeled["posterior_top100_probability"],
                    "current_rank_interval": f"{_fmt(modeled['posterior_rank_p05'])}-{_fmt(modeled['posterior_rank_p95'])}",
                    "proposed_observation_endpoint": "complete_language_capability_profile_cross_tab",
                    "required_denominator_definition": cell.population_denominator_id,
                    "expected_rank_width_reduction": "",
                    "expected_regret_reduction": "",
                    "source_class_required": "public_empirical",
                    "voi_status": "SKELETON_NOT_COMPUTED_REQUIRES_PROSPECTIVE_DESIGN",
                }
            )
    output.sort(key=lambda row: (row["language_target_id"], row["cell_id"]))
    return output


def order_l_semantic_hash(rows: Sequence[Mapping[str, Any]], *, variant: str) -> str:
    if variant == "L-ID":
        fields = (
            "language_target_id", "benefit_unit", "burden_lower_bound", "burden_upper_bound",
            "possible_rank_best", "possible_rank_worst", "top10_status", "top100_status",
        )
    elif variant == "L-M":
        fields = (
            "language_target_id", "benefit_unit", "posterior_mean_need", "decision_rank",
            "decision_tie_group_id", "posterior_top10_probability", "posterior_top100_probability",
        )
    else:
        raise OrderLModelError(f"unknown Order-L variant for hash: {variant}")
    payload = [{field: _fmt(row.get(field)) for field in fields} for row in rows]
    return sha256_bytes(canonical_json_bytes(payload))


def _path(value: str) -> Path:
    return Path(value).resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cells", required=True, type=_path)
    parser.add_argument("--assignment-evidence", required=True, type=_path)
    parser.add_argument("--observations", required=True, type=_path)
    parser.add_argument("--measurement-models", required=True, type=_path)
    parser.add_argument("--transport-models", required=True, type=_path)
    parser.add_argument("--prior-registry", type=_path, default=DEFAULT_PRIOR_REGISTRY_PATH)
    parser.add_argument("--l-id-output", required=True, type=_path)
    parser.add_argument("--l-m-output", required=True, type=_path)
    parser.add_argument("--joint-draw-output", required=True, type=_path)
    parser.add_argument("--cell-draw-output", required=True, type=_path)
    parser.add_argument("--shared-effect-output", required=True, type=_path)
    parser.add_argument("--sensitivity-output", required=True, type=_path)
    parser.add_argument("--pairwise-output", required=True, type=_path)
    parser.add_argument("--voi-output", required=True, type=_path)
    parser.add_argument("--validation-output", required=True, type=_path)
    parser.add_argument("--draw-count", type=int, default=512)
    parser.add_argument("--public-seed", default="order-l-v2-public-seed-2026-09-01")
    parser.add_argument("--allow-synthetic", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    raw_cells = read_csv(args.cells)
    raw_assignment_evidence = read_csv(args.assignment_evidence)
    raw_observations = read_csv(args.observations)
    raw_measurements = read_csv(args.measurement_models)
    raw_transports = read_csv(args.transport_models)
    cells, ignored_cells = normalize_cells(raw_cells, allow_synthetic=args.allow_synthetic)
    assignment_evidence, ignored_assignment_evidence = normalize_assignment_evidence(
        raw_assignment_evidence, cells, allow_synthetic=args.allow_synthetic
    )
    measurements, ignored_measurements = normalize_measurement_models(
        raw_measurements, allow_synthetic=args.allow_synthetic
    )
    transports, ignored_transports = normalize_transport_models(
        raw_transports, allow_synthetic=args.allow_synthetic
    )
    observations, ignored_observations = normalize_observations(
        raw_observations, cells, measurements, transports, allow_synthetic=args.allow_synthetic
    )
    priors = load_prior_registry(args.prior_registry)
    l_id = rank_order_l_id(cells, observations)
    target_draws, cell_draws, effects = generate_public_joint_draws(
        cells, observations, measurements, transports, priors,
        assignment_evidence,
        draw_count=args.draw_count, public_seed=args.public_seed,
    )
    l_m = summarize_order_l_m(
        target_draws, cells, observations, measurements, priors, l_id,
        assignment_evidence,
        draw_count=args.draw_count,
    )
    sensitivity = summarize_prior_sensitivity(
        target_draws, cells, observations, measurements, priors, l_id,
        assignment_evidence,
        draw_count=args.draw_count,
    )
    pairwise = build_boundary_pairwise_probabilities(l_m, target_draws)
    voi = build_value_of_information_skeleton(
        cells, observations, l_id, l_m, assignment_evidence
    )
    for path, rows in (
        (args.l_id_output, l_id),
        (args.l_m_output, l_m),
        (args.joint_draw_output, target_draws),
        (args.cell_draw_output, cell_draws),
        (args.shared_effect_output, effects),
        (args.sensitivity_output, sensitivity),
        (args.pairwise_output, pairwise),
        (args.voi_output, voi),
    ):
        write_csv(path, rows)
    outputs = {
        name: {"path": str(path), "sha256": sha256_file(path), "bytes": path.stat().st_size}
        for name, path in (
            ("l_id", args.l_id_output), ("l_m", args.l_m_output),
            ("joint_draws", args.joint_draw_output), ("cell_draws", args.cell_draw_output),
            ("shared_effects", args.shared_effect_output), ("prior_sensitivity", args.sensitivity_output),
            ("boundary_pairwise", args.pairwise_output), ("value_of_information", args.voi_output),
        )
    }
    validation = {
        "schema": SCHEMA_VERSION,
        "model_version": MODEL_VERSION,
        "draw_algorithm_version": DRAW_ALGORITHM_VERSION,
        "implementation_sha256": sha256_file(Path(__file__).resolve()),
        "prior_registry_sha256": priors.sha256,
        "public_seed": args.public_seed,
        "draw_count": args.draw_count,
        "universe_version": cells[0].universe_version,
        "universe_semantic_hash": cells[0].universe_semantic_hash,
        "production_universe_hash_authority": PRODUCTION_UNIVERSE_HASH_AUTHORITY,
        "frozen_production_universe_semantic_hash": FROZEN_PRODUCTION_UNIVERSE_SEMANTIC_HASH,
        "input_universe_matches_frozen_production": (
            cells[0].universe_semantic_hash == FROZEN_PRODUCTION_UNIVERSE_SEMANTIC_HASH
        ),
        "target_count": len({cell.language_target_id for cell in cells}),
        "person_profile_count": len({cell.person_profile_id for cell in cells}),
        "assignment_atom_count": len({(cell.person_profile_id, cell.assignment_atom_id) for cell in cells}),
        "assignment_evidence_count": len(assignment_evidence),
        "cell_count": len(cells),
        "observation_count": len(observations),
        "l_id_semantic_hash": order_l_semantic_hash(l_id, variant="L-ID"),
        "l_m_semantic_hash": order_l_semantic_hash(l_m, variant="L-M"),
        "input_sha256": {
            "cells": sha256_file(args.cells),
            "assignment_evidence": sha256_file(args.assignment_evidence),
            "observations": sha256_file(args.observations),
            "measurement_models": sha256_file(args.measurement_models),
            "transport_models": sha256_file(args.transport_models),
            "prior_registry": sha256_file(args.prior_registry),
        },
        "ignored_input_columns": {
            "cells": ignored_cells,
            "assignment_evidence": ignored_assignment_evidence,
            "observations": ignored_observations,
            "measurement_models": ignored_measurements,
            "transport_models": ignored_transports,
        },
        "contracts": {
            "strict_l_c_implementation_unchanged": True,
            "language_keyed_not_candidate_or_package_keyed": True,
            "canonical_universe_version_and_semantic_hash_required": True,
            "finite_population_ceiling_required": True,
            "one_person_assignment_per_profile": True,
            "latent_assignment_is_symmetric_over_stable_atoms": True,
            "assignment_share_evidence_is_multinomial_and_profile_compatible": True,
            "assignment_prior_sensitivity_reported": True,
            "target_split_merge_conserves_assignment_atom_mass": True,
            "direct_endpoint_bypasses_component_multiplication": True,
            "component_proxy_requires_measurement_model": True,
            "ecological_or_cross_endpoint_requires_transport_model": True,
            "shared_source_effect_drawn_once_per_group": True,
            "complete_target_draw_grid_required_for_rank": True,
            "missing_endpoint_is_latent_not_zero_or_half": True,
            "evidence_tier_is_diagnostic_only": True,
            "forbidden_predictors_absent": True,
            "reference_diffuse_optimistic_pessimistic_priors": True,
            "global_top100_release_authorized": False,
            "decision_scope": "conditional_on_supplied_finite_roster",
        },
        "outputs": outputs,
    }
    args.validation_output.parent.mkdir(parents=True, exist_ok=True)
    args.validation_output.write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
