#!/usr/bin/env python3
"""Need/access-only ranking with a separately joined from-scratch compute view.

The intrinsic scorer has no compute-table argument.  The efficiency scorer accepts
the already-computed intrinsic rows and a standardized fresh-compute table.  This
one-way API boundary is intentional: compute, implementation, project, asset,
reuse, and user-work metadata cannot influence intrinsic eligibility or order.

Only the Python standard library is used so the synthetic verification fixture can
run in a clean environment.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import urlparse


SCHEMA_VERSION = "interlanguage/needs-access-ranking/1.1.0"
DEFAULT_FACTOR_REGISTRY_PATH = Path(__file__).resolve().with_name("INTRINSIC_FACTOR_REGISTRY.json")
DEFAULT_STANDARD_COMPUTE_REGISTRY_PATH = (
    Path(__file__).resolve().parents[1] / "structured" / "schema" / "standard_compute_factor_registry.csv"
)

CANDIDATE_FIELDS = (
    "candidate_id",
    "target_label",
    "language_target_id",
    "language_target_label",
    "territory_cell_id",
    "population_partition_id",
    "population_cell_definition",
    "population_denominator_id",
    "population_allocation_crosswalk_hash",
    "normative_joint_need_component_id",
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
    "event_id",
    "numerator_definition",
    "denominator_stratum_id",
    "condition_on_event_id",
    "resource_audit_group_hash",
    "resource_finding_status",
    "baseline_policy_version",
    "baseline_observation_date",
    "baseline_functional_route_id",
    "baseline_access_endpoint_id",
    "program_exclusion_registry_hash",
)

COMPUTE_FIELDS = (
    "candidate_id",
    "language_target_id",
    "package_id",
    "learner_stage",
    "subject_domain",
    "delivery_format",
    "compute_scope",
    "compute_measure_class",
    "compute_low",
    "compute_base",
    "compute_high",
    "compute_unit",
    "source_id",
    "source_url",
    "source_class",
    "is_public",
    "formula_version",
    "factor_registry_version",
    "compute_input_set_hash",
    "compute_derivation_set_hash",
    "factor_registry_file_hash",
    "compute_model_role",
    "compute_evidence_status",
    "benchmark_profile_id",
    "tokenization_measurement_set_sha256",
    "measurement_profile_registry_file_sha256",
    "measurement_profile_set_hash",
    "direct_measurement_row_hash",
    "compute_binding_mode",
    "successor_roster_file_sha256",
    "target_binding_row_hash",
    "target_binding_set_hash",
    "order_b_eligible",
)

STANDARD_COMPUTE_PACKAGE_PREFIXES = {
    "PKG-TEXT": ("text.",),
    "PKG-ACCESSIBLE-PUBLICATION": ("text.", "html.", "publication."),
    "PKG-AUDIO": ("text.", "audio."),
    "PKG-CAPTIONS": ("text.", "captions."),
    "PKG-NAMED-SIGN": ("text.", "sign."),
    "PKG-COMPLETE-ACCESS": ("text.", "html.", "publication.", "audio.", "captions.", "sign."),
}

PINNED_STANDARD_COMPUTE_REGISTRY_SHA256 = {
    "standard-compute-closed-registry-2026-09-01-v2": "b0d23b05278e3713a6fc1a6492855ffa76035621bc36b581e357d470a78e62e1",
}
PINNED_STANDARD_COMPUTE_TOKENIZATION_SHA256 = "6ae11eae5bfb61e237feeb8b8664277b7462e5ba08b34e6e35df1c072b22c2ae"
PINNED_SUCCESSOR_TARGET_ROSTER_SHA256 = "983a40756107072ca779c1f3a37684c8e5865fbedd9fc42768e9d1cab754656f"
PINNED_STANDARD_COMPUTE_TARGET_BINDINGS_SHA256 = "d6abddd16d43c201086da1b0566960950ea8e934434c40e2cf0c3312f4c3f8af"

DRAW_FIELDS = (
    "draw_set_id",
    "draw_id",
    "candidate_id",
    "factor_name",
    "value",
)

COUNTRY_ID_FIELDS = ("country_code", "country_name")

# Exact public population/education/access fields produced by build_country_context.py.
# A source row may request only one of these fields.  The synthetic-only field is
# admitted solely behind --allow-synthetic and can never enter a production run.
COUNTRY_CONTEXT_ALLOWED_VALUE_FIELDS = frozenset(
    {
        "adult_literacy_pct",
        "electricity_access_pct",
        "end_lower_secondary_math_minimum_pct",
        "end_lower_secondary_reading_minimum_pct",
        "end_primary_math_minimum_pct",
        "end_primary_reading_minimum_pct",
        "internet_users_pct",
        "learning_deprivation_pct",
        "learning_poverty_pct",
        "learning_poverty_schooling_deprivation_pct",
        "lower_secondary_completion_pct",
        "lower_secondary_out_of_school_pct",
        "mobile_subscriptions_per_100",
        "population_0_14_thousands",
        "population_15_24_thousands",
        "population_25_64_thousands",
        "population_65_plus_thousands",
        "population_age_10",
        "population_primary_age",
        "population_total_thousands",
        "primary_completion_pct",
        "primary_out_of_school_pct",
        "tertiary_gross_enrolment_pct",
        "upper_secondary_completion_pct",
        "upper_secondary_out_of_school_pct",
        "urban_population_pct",
        "wb_adult_literacy_pct",
        "wb_population_total",
        "wb_secondary_gross_enrolment_pct",
        "wb_tertiary_gross_enrolment_pct",
        "youth_literacy_pct",
    }
)
SYNTHETIC_CONTEXT_FIELDS = frozenset({"synthetic_need_pct"})

FORBIDDEN_TOKENS = (
    "asset",
    "completed",
    "completion",
    "current_",
    "current_project",
    "existing_",
    "existing_work",
    "funding",
    "holding",
    "implementation",
    "inventory",
    "local_",
    "local_work",
    "prior_",
    "prior_translation",
    "production_status",
    "project_",
    "project_status",
    "readiness",
    "reuse",
    "staffing",
    "sunk",
    "user_",
    "user_priority",
    "user_work",
    "work_",
    "work_done",
)

RATE_ROLES = {"need", "access_gain"}
FACTOR_ROLES = {"population", *RATE_ROLES}
OVERLAP_RULES = {"none", "max_union"}
SOURCE_CLASSES = {"public_empirical", "public_model", "synthetic_fixture"}
PUBLIC_SOURCE_CLASSES = {"public_empirical", "public_model"}
RANKING_MEASURE_CLASS_REGISTRY_VERSION = "ranking-measure-class-registry-2026-09-01-v1"
RANKING_MEASURE_CLASSES = frozenset(
    {
        "global_language_need_v1",
        "learner_domain_access_12m",
        "research_access_12m",
    }
)
LANGUAGE_NEED_MEASURE_CLASSES = frozenset({"language_target_need_v1"})
RESOURCE_FINDING_STATUSES = frozenset(
    {"RESOURCE_FOUND", "NO_QUALIFYING_RESOURCE_FOUND", "SEARCH_UNRESOLVED"}
)

# A context column is legal only for the named factor, orientation, and stage.
# Direct means larger source values imply larger factor values; complement means
# the registered factor is one minus the scaled public source value.
CONTEXT_FACTOR_BINDINGS: Mapping[str, Mapping[str, tuple[str, frozenset[str]]]] = {
    "population": {
        "population_total_thousands": ("direct", frozenset({"E0", "E1", "E2", "E3", "E4", "E5", "E6"})),
        "population_0_14_thousands": ("direct", frozenset({"E0", "E1", "E2", "E3"})),
        "population_15_24_thousands": ("direct", frozenset({"E3", "E4", "E5", "E6"})),
        "population_25_64_thousands": ("direct", frozenset({"E5", "E6"})),
        "population_65_plus_thousands": ("direct", frozenset({"E6"})),
        "population_age_10": ("direct", frozenset({"E2"})),
        "population_primary_age": ("direct", frozenset({"E1", "E2"})),
        "wb_population_total": ("direct", frozenset({"E0", "E1", "E2", "E3", "E4", "E5", "E6"})),
    },
    "education_need": {
        "learning_poverty_pct": ("direct", frozenset({"E1", "E2"})),
        "learning_deprivation_pct": ("direct", frozenset({"E1", "E2"})),
        "learning_poverty_schooling_deprivation_pct": ("direct", frozenset({"E1", "E2"})),
        "primary_out_of_school_pct": ("direct", frozenset({"E1", "E2"})),
        "lower_secondary_out_of_school_pct": ("direct", frozenset({"E3"})),
        "upper_secondary_out_of_school_pct": ("direct", frozenset({"E4"})),
        "primary_completion_pct": ("complement", frozenset({"E1", "E2"})),
        "lower_secondary_completion_pct": ("complement", frozenset({"E3"})),
        "upper_secondary_completion_pct": ("complement", frozenset({"E4"})),
        "adult_literacy_pct": ("complement", frozenset({"E6"})),
        "wb_adult_literacy_pct": ("complement", frozenset({"E6"})),
        "youth_literacy_pct": ("complement", frozenset({"E4", "E5", "E6"})),
    },
    "accessible_delivery_reach": {
        "internet_users_pct": ("direct", frozenset({"E0", "E1", "E2", "E3", "E4", "E5", "E6"})),
        "electricity_access_pct": ("direct", frozenset({"E0", "E1", "E2", "E3", "E4", "E5", "E6"})),
    },
}


@dataclass(frozen=True)
class FactorRegistry:
    version: str
    sha256: str
    rules: Mapping[str, tuple[str, str]]


class RankingError(ValueError):
    """Raised when an input cannot support the declared ranking semantics."""


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _decimal(value: Any, *, label: str) -> Decimal | None:
    text = _text(value)
    if not text:
        return None
    try:
        result = Decimal(text)
    except InvalidOperation as exc:
        raise RankingError(f"{label} is not a decimal: {text!r}") from exc
    if not result.is_finite():
        raise RankingError(f"{label} must be finite")
    return result


def _integer(value: Any, *, label: str) -> int:
    text = _text(value)
    if not text:
        raise RankingError(f"{label} is required")
    try:
        result = int(text)
    except ValueError as exc:
        raise RankingError(f"{label} is not an integer: {text!r}") from exc
    return result


def _truth(value: Any) -> bool:
    return _text(value).casefold() in {"1", "true", "yes", "y"}


def _is_sha256(value: Any) -> bool:
    return bool(re.fullmatch(r"[0-9a-fA-F]{64}", _text(value)))


def _is_iso_date(value: Any) -> bool:
    return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", _text(value)))


def _fmt(value: Decimal | int | str | None) -> str:
    if value is None:
        return ""
    if isinstance(value, Decimal):
        if value == 0:
            return "0"
        text = format(value, "f")
        return text.rstrip("0").rstrip(".") if "." in text else text
    return str(value)


def _quantile(values: Sequence[Decimal], probability: Decimal) -> Decimal | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = probability * Decimal(len(ordered) - 1)
    lower_index = int(position)
    upper_index = min(lower_index + 1, len(ordered) - 1)
    weight = position - Decimal(lower_index)
    return ordered[lower_index] * (Decimal(1) - weight) + ordered[upper_index] * weight


def _mean(values: Sequence[Decimal]) -> Decimal | None:
    return sum(values, Decimal(0)) / Decimal(len(values)) if values else None


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode("utf-8")


def load_factor_registry(path: Path = DEFAULT_FACTOR_REGISTRY_PATH) -> FactorRegistry:
    """Load the closed, versioned intrinsic-factor allowlist."""
    try:
        raw_bytes = path.read_bytes()
        document = json.loads(raw_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RankingError(f"cannot load intrinsic factor registry {path}: {exc}") from exc
    if document.get("schema") != "interlanguage/intrinsic-factor-registry/1.0.0":
        raise RankingError("intrinsic factor registry has an unsupported schema")
    version = _text(document.get("registry_version"))
    if not version:
        raise RankingError("intrinsic factor registry lacks registry_version")
    rules: dict[str, tuple[str, str]] = {}
    factors = document.get("factors")
    if not isinstance(factors, list) or not factors:
        raise RankingError("intrinsic factor registry must contain a nonempty factors list")
    for index, raw in enumerate(factors, start=1):
        if not isinstance(raw, dict):
            raise RankingError(f"intrinsic factor registry row {index} is not an object")
        name = _text(raw.get("factor_name"))
        role = _text(raw.get("factor_role"))
        unit_class = _text(raw.get("unit_class"))
        if not name or name in rules:
            raise RankingError(f"intrinsic factor registry has blank or duplicate factor_name: {name!r}")
        if role not in FACTOR_ROLES:
            raise RankingError(f"intrinsic factor registry {name!r} has invalid factor_role: {role!r}")
        expected_unit_class = "population_count" if role == "population" else "conditional_proportion"
        if unit_class != expected_unit_class:
            raise RankingError(
                f"intrinsic factor registry {name!r} requires unit_class {expected_unit_class!r}"
            )
        if _has_forbidden_token(name):
            raise RankingError(f"intrinsic factor registry contains forbidden factor_name: {name!r}")
        rules[name] = (role, unit_class)
    return FactorRegistry(version, sha256_bytes(raw_bytes), rules)


def _factor_registry(registry: FactorRegistry | None) -> FactorRegistry:
    return registry if registry is not None else load_factor_registry()


def _intervention_key(row: Mapping[str, Any]) -> str:
    """Return the auditable composite language/package/stage/domain/format key."""
    components = [
        _text(row.get("language_target_id")),
        _text(row.get("territory_cell_id")),
        _text(row.get("package_id")),
        _text(row.get("learner_stage")),
        _text(row.get("subject_domain")),
        _text(row.get("delivery_format")),
    ]
    return "intervention-v1:" + json.dumps(components, ensure_ascii=True, separators=(",", ":"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise RankingError(f"{path} has no header")
        return [dict(row) for row in reader]


def _project_rows(rows: Iterable[Mapping[str, Any]], fields: Sequence[str]) -> list[dict[str, str]]:
    """Project onto an allowlist; extra project/status fields are noninterfering."""
    return [{field: _text(row.get(field, "")) for field in fields} for row in rows]


def ignored_columns(rows: Sequence[Mapping[str, Any]], fields: Sequence[str]) -> list[str]:
    allowed = set(fields)
    return sorted({key for row in rows for key in row if key not in allowed})


def _has_forbidden_token(name: str) -> bool:
    folded = name.casefold()
    return any(token in folded for token in FORBIDDEN_TOKENS)


def _require_public_source(row: Mapping[str, str], *, allow_synthetic: bool, label: str) -> None:
    source_class = row["source_class"]
    if source_class not in SOURCE_CLASSES:
        raise RankingError(f"{label}.source_class must be one of {sorted(SOURCE_CLASSES)}")
    if source_class == "synthetic_fixture":
        if not allow_synthetic:
            raise RankingError(f"{label} is synthetic; rerun only a test with --allow-synthetic")
    elif not _truth(row["is_public"]):
        raise RankingError(f"{label} is not declared public")
    if not row["source_id"] or not row["source_url"]:
        raise RankingError(f"{label} requires source_id and source_url")
    parsed = urlparse(row["source_url"])
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise RankingError(f"{label}.source_url must be a public http(s) network URL")


def load_country_context(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for raw in rows:
        row = {str(key): _text(value) for key, value in raw.items()}
        code = row.get("country_code", "")
        if not code:
            raise RankingError("COUNTRY_CONTEXT row lacks country_code")
        if code in result:
            raise RankingError(f"duplicate COUNTRY_CONTEXT country_code: {code}")
        result[code] = row
    return result


def normalize_candidates(
    rows: Sequence[Mapping[str, Any]], country_context: Mapping[str, Mapping[str, str]]
) -> tuple[list[dict[str, str]], list[str]]:
    ignored = ignored_columns(rows, CANDIDATE_FIELDS)
    projected = _project_rows(rows, CANDIDATE_FIELDS)
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    seen_interventions: dict[str, str] = {}
    signature_by_measure_class: dict[str, tuple[str, str]] = {}
    signature_by_language_target: dict[str, tuple[str, str]] = {}
    overlap_signatures: dict[str, set[tuple[str, ...]]] = defaultdict(set)
    for row in projected:
        candidate_id = row["candidate_id"]
        if not candidate_id:
            raise RankingError("candidate_id is required")
        if candidate_id in seen:
            raise RankingError(f"duplicate candidate_id: {candidate_id}")
        seen.add(candidate_id)
        for field in (
            "target_label",
            "language_target_id",
            "language_target_label",
            "measure_class",
            "language_need_measure_class",
            "endpoint_id",
            "learner_stage",
            "subject_domain",
            "package_id",
            "delivery_format",
            "stratum_compatibility_key",
        ):
            if not row[field]:
                raise RankingError(f"{candidate_id}.{field} is required")
        if not row["territory_cell_id"]:
            row["territory_cell_id"] = row["stratum_compatibility_key"]
        if row["measure_class"] not in RANKING_MEASURE_CLASSES:
            raise RankingError(
                f"{candidate_id}.measure_class is not registered by "
                f"{RANKING_MEASURE_CLASS_REGISTRY_VERSION}: {row['measure_class']!r}"
            )
        if row["language_need_measure_class"] not in LANGUAGE_NEED_MEASURE_CLASSES:
            raise RankingError(
                f"{candidate_id}.language_need_measure_class is not registered: "
                f"{row['language_need_measure_class']!r}"
            )
        if row["eligibility_status"] and row["eligibility_status"] not in {"ELIGIBLE", "STRUCTURAL_ZERO"}:
            raise RankingError(f"{candidate_id}.eligibility_status is invalid")
        if row["rankability_status"] and row["rankability_status"] not in {
            "POINT_DISTRIBUTION",
            "INTERVAL_ONLY",
            "INSUFFICIENT_PUBLIC_EVIDENCE",
            "STRUCTURAL_ZERO",
        }:
            raise RankingError(f"{candidate_id}.rankability_status is invalid")
        for field in (
            "language_target_id",
            "territory_cell_id",
            "measure_class",
            "language_need_measure_class",
            "endpoint_id",
            "learner_stage",
            "subject_domain",
            "package_id",
            "delivery_format",
            "stratum_compatibility_key",
            "overlap_group_id",
        ):
            if row[field] and _has_forbidden_token(row[field]):
                raise RankingError(f"{candidate_id}.{field} contains a forbidden local/project token")
        horizon = _integer(row["horizon_months"], label=f"{candidate_id}.horizon_months")
        if horizon <= 0:
            raise RankingError(f"{candidate_id}.horizon_months must be positive")
        rule = row["overlap_rule"] or "none"
        if rule not in OVERLAP_RULES:
            raise RankingError(f"{candidate_id}.overlap_rule must be one of {sorted(OVERLAP_RULES)}")
        if rule == "max_union" and not row["overlap_group_id"]:
            raise RankingError(f"{candidate_id} uses max_union without overlap_group_id")
        if rule == "none" and row["overlap_group_id"]:
            raise RankingError(f"{candidate_id} has overlap_group_id but overlap_rule=none")
        evidence_fields = (
            "overlap_evidence_source_id",
            "overlap_evidence_source_url",
            "overlap_evidence_source_class",
            "overlap_evidence_is_public",
        )
        if rule == "max_union":
            if not row["country_code"]:
                raise RankingError(f"{candidate_id} uses max_union without a country_code")
            if not all(row[field] for field in evidence_fields):
                raise RankingError(f"{candidate_id} uses max_union without complete public overlap evidence")
            if row["overlap_evidence_source_class"] not in PUBLIC_SOURCE_CLASSES:
                raise RankingError(f"{candidate_id} max_union evidence must be public_empirical or public_model")
            if not _truth(row["overlap_evidence_is_public"]):
                raise RankingError(f"{candidate_id} max_union evidence is not declared public")
            overlap_signatures[row["overlap_group_id"]].add(
                (
                    row["country_code"],
                    row["stratum_compatibility_key"],
                    row["measure_class"],
                    row["endpoint_id"],
                    str(horizon),
                    row["overlap_evidence_source_id"],
                    row["overlap_evidence_source_url"],
                )
            )
        elif any(row[field] for field in evidence_fields):
            raise RankingError(f"{candidate_id} supplies overlap evidence but overlap_rule=none")
        if row["country_code"] and row["country_code"] not in country_context:
            raise RankingError(f"{candidate_id} country_code is absent from COUNTRY_CONTEXT: {row['country_code']}")
        row["horizon_months"] = str(horizon)
        row["overlap_rule"] = rule
        row["intervention_key"] = _intervention_key(row)
        if row["intervention_key"] in seen_interventions:
            raise RankingError(
                "duplicate composite intervention key for "
                f"{seen_interventions[row['intervention_key']]} and {candidate_id}: {row['intervention_key']}"
            )
        seen_interventions[row["intervention_key"]] = candidate_id
        signature = (row["endpoint_id"], row["horizon_months"])
        prior_signature = signature_by_measure_class.setdefault(row["measure_class"], signature)
        if signature != prior_signature:
            raise RankingError(
                f"measure_class {row['measure_class']!r} mixes endpoint/horizon signatures: "
                f"{prior_signature!r} versus {signature!r}"
            )
        language_signature = (
            row["language_target_label"],
            row["language_need_measure_class"],
        )
        prior_language_signature = signature_by_language_target.setdefault(
            row["language_target_id"], language_signature
        )
        if language_signature != prior_language_signature:
            raise RankingError(
                f"language_target_id {row['language_target_id']!r} mixes target identity signatures: "
                f"{prior_language_signature!r} versus {language_signature!r}"
            )
        result.append(row)
    invalid_overlap_groups = {
        group: sorted(signatures)
        for group, signatures in overlap_signatures.items()
        if len(signatures) != 1
    }
    if invalid_overlap_groups:
        raise RankingError(
            "max_union overlap groups mix geography, strata, endpoints, or evidence identity: "
            f"{invalid_overlap_groups}"
        )
    return result, ignored


@dataclass(frozen=True)
class Factor:
    candidate_id: str
    name: str
    role: str
    conditional_order: int
    measure_class: str
    low: Decimal | None
    base: Decimal | None
    high: Decimal | None
    unit: str
    source_id: str
    source_class: str
    event_id: str
    numerator_definition: str
    denominator_stratum_id: str
    condition_on_event_id: str


def _normalize_factor_value(value: Decimal | None, scale: Decimal, *, role: str, label: str) -> Decimal | None:
    if value is None:
        return None
    normalized = value * scale
    if normalized < 0:
        raise RankingError(f"{label} cannot be negative")
    if role in RATE_ROLES and normalized > 1:
        raise RankingError(f"{label} must be within [0,1] after value_scale")
    return normalized


def normalize_factors(
    rows: Sequence[Mapping[str, Any]],
    candidates: Sequence[Mapping[str, str]],
    country_context: Mapping[str, Mapping[str, str]],
    *,
    allow_synthetic: bool = False,
    factor_registry: FactorRegistry | None = None,
    resource_audit_path: Path | None = None,
    program_exclusion_registry_path: Path | None = None,
) -> tuple[dict[str, list[Factor]], list[str]]:
    registry = _factor_registry(factor_registry)
    ignored = ignored_columns(rows, FACTOR_FIELDS)
    projected = _project_rows(rows, FACTOR_FIELDS)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    factors: dict[str, list[Factor]] = defaultdict(list)
    seen: set[tuple[str, str]] = set()
    for index, row in enumerate(projected, start=2):
        candidate_id = row["candidate_id"]
        if candidate_id not in candidate_by_id:
            raise RankingError(f"factor row {index} has unknown candidate_id: {candidate_id}")
        name = row["factor_name"]
        if not name or name not in registry.rules:
            raise RankingError(
                f"{candidate_id} has unregistered factor_name {name!r} under {registry.version}"
            )
        key = (candidate_id, name)
        if key in seen:
            raise RankingError(f"duplicate factor: {candidate_id}/{name}")
        seen.add(key)
        role = row["factor_role"]
        if role not in FACTOR_ROLES:
            raise RankingError(f"{candidate_id}/{name}.factor_role must be one of {sorted(FACTOR_ROLES)}")
        registered_role, registered_unit_class = registry.rules[name]
        if role != registered_role:
            raise RankingError(
                f"{candidate_id}/{name}.factor_role {role!r} conflicts with registry role {registered_role!r}"
            )
        order = _integer(row["conditional_order"], label=f"{candidate_id}/{name}.conditional_order")
        if role == "population" and order != 0:
            raise RankingError(f"{candidate_id}/{name}: population must have conditional_order 0")
        if role != "population" and order <= 0:
            raise RankingError(f"{candidate_id}/{name}: conditional rates require positive conditional_order")
        if not row["factor_measure_class"] or not row["unit"]:
            raise RankingError(f"{candidate_id}/{name} requires factor_measure_class and unit")
        if _has_forbidden_token(row["factor_measure_class"]):
            raise RankingError(f"{candidate_id}/{name}.factor_measure_class contains a forbidden local/project token")
        if role == "population" and row["unit"] not in {"persons", "learner_years"}:
            raise RankingError(f"{candidate_id}/{name}: population unit must be persons or learner_years after scaling")
        if role in RATE_ROLES and row["unit"] != "proportion":
            raise RankingError(f"{candidate_id}/{name}: conditional rate unit must be proportion after scaling")
        actual_unit_class = "population_count" if role == "population" else "conditional_proportion"
        if actual_unit_class != registered_unit_class:
            raise RankingError(f"{candidate_id}/{name} unit class conflicts with the factor registry")
        _require_public_source(row, allow_synthetic=allow_synthetic, label=f"{candidate_id}/{name}")
        if name == "resource_gap":
            if not _is_sha256(row["resource_audit_group_hash"]):
                raise RankingError(f"{candidate_id}/{name} requires resource_audit_group_hash")
            if row["resource_finding_status"] not in RESOURCE_FINDING_STATUSES:
                raise RankingError(f"{candidate_id}/{name} requires a registered resource_finding_status")
            if not row["baseline_policy_version"]:
                raise RankingError(f"{candidate_id}/{name} requires baseline_policy_version")
            if not _is_iso_date(row["baseline_observation_date"]):
                raise RankingError(f"{candidate_id}/{name} requires baseline_observation_date")
            if not row["baseline_functional_route_id"] or not row["baseline_access_endpoint_id"]:
                raise RankingError(
                    f"{candidate_id}/{name} requires an exact baseline functional route and access endpoint"
                )
            if not _is_sha256(row["program_exclusion_registry_hash"]):
                raise RankingError(f"{candidate_id}/{name} requires program_exclusion_registry_hash")
            if resource_audit_path is None or program_exclusion_registry_path is None:
                raise RankingError(f"{candidate_id}/{name} requires canonical resource-audit and exclusion-register bytes")
            if sha256_file(resource_audit_path) != row["resource_audit_group_hash"].casefold():
                raise RankingError(f"{candidate_id}/{name}.resource_audit_group_hash does not match canonical bytes")
            if sha256_file(program_exclusion_registry_path) != row["program_exclusion_registry_hash"].casefold():
                raise RankingError(f"{candidate_id}/{name}.program_exclusion_registry_hash does not match canonical bytes")
            if row["source_class"] != "synthetic_fixture":
                audit_rows = read_csv(resource_audit_path)
                derived_rows = [
                    item for item in audit_rows
                    if _text(item.get("baseline_functional_route_id")) == row["baseline_functional_route_id"]
                    and _text(item.get("baseline_access_endpoint_id")) == row["baseline_access_endpoint_id"]
                ]
                if len(derived_rows) != 1 or not _text(derived_rows[0].get("resource_gap_base")):
                    raise RankingError(f"{candidate_id}/{name} lacks one canonical resource-gap derivation row")
                derived = derived_rows[0]
                for scalar_field, audit_field in (
                    ("low", "resource_gap_low"), ("base", "resource_gap_base"), ("high", "resource_gap_high")
                ):
                    claimed = _text(row[scalar_field])
                    expected = _text(derived.get(audit_field))
                    if claimed != expected:
                        raise RankingError(f"{candidate_id}/{name}.{scalar_field} was not derived from resource-audit bytes")
        scale = _decimal(row["value_scale"] or "1", label=f"{candidate_id}/{name}.value_scale")
        assert scale is not None
        if scale <= 0:
            raise RankingError(f"{candidate_id}/{name}.value_scale must be positive")
        low = _decimal(row["low"], label=f"{candidate_id}/{name}.low")
        base = _decimal(row["base"], label=f"{candidate_id}/{name}.base")
        high = _decimal(row["high"], label=f"{candidate_id}/{name}.high")
        context_field = row["country_context_field"]
        if context_field:
            allowed_context_fields = set(COUNTRY_CONTEXT_ALLOWED_VALUE_FIELDS)
            if allow_synthetic:
                allowed_context_fields.update(SYNTHETIC_CONTEXT_FIELDS)
            if context_field not in allowed_context_fields:
                raise RankingError(f"COUNTRY_CONTEXT field is not on the positive scoring allowlist: {context_field}")
            bindings = dict(CONTEXT_FACTOR_BINDINGS.get(name, {}))
            if allow_synthetic and name == "education_need":
                bindings["synthetic_need_pct"] = ("direct", frozenset({"E0", "E1", "E2", "E3", "E4", "E5", "E6"}))
            binding = bindings.get(context_field)
            if binding is None:
                raise RankingError(
                    f"COUNTRY_CONTEXT field {context_field!r} is not registered for factor {name!r}"
                )
            orientation, allowed_stages = binding
            learner_stage = candidate_by_id[candidate_id]["learner_stage"]
            if learner_stage not in allowed_stages:
                raise RankingError(
                    f"COUNTRY_CONTEXT {context_field!r} is incompatible with learner_stage {learner_stage!r}"
                )
            country_code = candidate_by_id[candidate_id]["country_code"]
            if not country_code:
                raise RankingError(f"{candidate_id}/{name} requests COUNTRY_CONTEXT without country_code")
            context_row = country_context[country_code]
            if context_field not in context_row:
                raise RankingError(f"COUNTRY_CONTEXT lacks requested field: {context_field}")
            context_value = _decimal(context_row[context_field], label=f"COUNTRY_CONTEXT[{country_code}].{context_field}")
            if base is not None and context_value is not None:
                raise RankingError(f"{candidate_id}/{name} supplies both base and country_context_field")
            if context_value is None:
                base = None
            elif orientation == "direct":
                base = context_value
            elif orientation == "complement":
                base = (Decimal(1) / scale) - context_value
            else:
                raise RankingError(f"unsupported context orientation: {orientation}")
        low = _normalize_factor_value(low, scale, role=role, label=f"{candidate_id}/{name}.low")
        base = _normalize_factor_value(base, scale, role=role, label=f"{candidate_id}/{name}.base")
        high = _normalize_factor_value(high, scale, role=role, label=f"{candidate_id}/{name}.high")
        if low is not None and high is not None and low > high:
            raise RankingError(f"{candidate_id}/{name}: low exceeds high")
        if base is not None and low is not None and base < low:
            raise RankingError(f"{candidate_id}/{name}: base is below low")
        if base is not None and high is not None and base > high:
            raise RankingError(f"{candidate_id}/{name}: base exceeds high")
        evidence_fields = (
            row["event_id"], row["numerator_definition"],
            row["denominator_stratum_id"], row["condition_on_event_id"],
        )
        factors[candidate_id].append(
            Factor(candidate_id, name, role, order, row["factor_measure_class"], low, base, high,
                   row["unit"], row["source_id"], row["source_class"], row["event_id"], row["numerator_definition"],
                   row["denominator_stratum_id"], row["condition_on_event_id"])
        )

    factor_signature_by_measure_class: dict[str, tuple[tuple[int, str, str, str, str], ...]] = {}
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    for candidate in candidates:
        candidate_id = candidate["candidate_id"]
        items = sorted(factors.get(candidate_id, []), key=lambda item: (item.conditional_order, item.name))
        if not items:
            raise RankingError(f"{candidate_id} has no factor rows")
        if sum(item.role == "population" for item in items) != 1:
            raise RankingError(f"{candidate_id} requires exactly one population factor")
        if not any(item.role == "need" for item in items):
            raise RankingError(f"{candidate_id} requires at least one need factor")
        if not any(item.role == "access_gain" for item in items):
            raise RankingError(f"{candidate_id} requires at least one access_gain factor")
        orders = [item.conditional_order for item in items]
        if len(orders) != len(set(orders)):
            raise RankingError(f"{candidate_id} conditional_order values must be unique")
        if any(item.event_id or item.numerator_definition or item.denominator_stratum_id or item.condition_on_event_id for item in items):
            prior_event = ""
            denominator = ""
            seen_event_ids: set[str] = set()
            for item in items:
                if not item.event_id or not item.numerator_definition or not item.denominator_stratum_id:
                    raise RankingError(f"{candidate_id}/{item.name} has an incomplete conditional-event identity")
                if denominator and item.denominator_stratum_id != denominator:
                    raise RankingError(f"{candidate_id} conditional chain changes denominator stratum")
                if item.event_id in seen_event_ids:
                    raise RankingError(f"{candidate_id} conditional chain reuses event_id {item.event_id!r}")
                seen_event_ids.add(item.event_id)
                denominator = item.denominator_stratum_id
                if item.role == "population":
                    if item.condition_on_event_id:
                        raise RankingError(f"{candidate_id}/{item.name} population root cannot have a parent event")
                elif item.condition_on_event_id != prior_event:
                    raise RankingError(
                        f"{candidate_id}/{item.name} must condition on immediately preceding event {prior_event!r}"
                    )
                prior_event = item.event_id
        denominator_classes = [
            (item.role, item.measure_class)
            for item in items
            if item.role != "population"
        ]
        if len(denominator_classes) != len(set(denominator_classes)):
            raise RankingError(
                f"{candidate_id} repeats a conditional role/denominator measure class"
            )
        signature = tuple(
            (item.conditional_order, item.name, item.role, item.measure_class, item.unit)
            for item in items
        )
        ranking_measure_class = candidate_by_id[candidate_id]["measure_class"]
        prior_signature = factor_signature_by_measure_class.setdefault(ranking_measure_class, signature)
        if signature != prior_signature:
            raise RankingError(
                f"measure_class {ranking_measure_class!r} mixes factor/denominator signatures: "
                f"{prior_signature!r} versus {signature!r}"
            )
        factors[candidate_id] = items
    return dict(factors), ignored


def normalize_draws(
    rows: Sequence[Mapping[str, Any]],
    *,
    factor_registry: FactorRegistry | None = None,
) -> tuple[dict[tuple[str, str, str], Decimal], list[str]]:
    registry = _factor_registry(factor_registry)
    ignored = ignored_columns(rows, DRAW_FIELDS)
    projected = _project_rows(rows, DRAW_FIELDS)
    result: dict[tuple[str, str, str], Decimal] = {}
    for index, row in enumerate(projected, start=2):
        if not all(row[field] for field in ("draw_set_id", "draw_id", "candidate_id", "factor_name", "value")):
            raise RankingError(f"joint-draw row {index} has a blank required field")
        if row["factor_name"] != "compute_new" and row["factor_name"] not in registry.rules:
            raise RankingError(
                f"joint-draw row {index} has unregistered factor under {registry.version}: "
                f"{row['factor_name']!r}"
            )
        key = (row["candidate_id"], f"{row['draw_set_id']}::{row['draw_id']}", row["factor_name"])
        if key in result:
            raise RankingError(f"duplicate joint draw cell: {key}")
        value = _decimal(row["value"], label=f"joint draw {key}")
        assert value is not None
        if value < 0:
            raise RankingError(f"joint draw {key} cannot be negative")
        result[key] = value
    return result, ignored


def _product(values: Iterable[Decimal | None]) -> Decimal | None:
    result = Decimal(1)
    for value in values:
        if value is None:
            return None
        result *= value
    return result


def _intrinsic_draw_scores(
    candidates: Sequence[Mapping[str, str]],
    factors: Mapping[str, Sequence[Factor]],
    draws: Mapping[tuple[str, str, str], Decimal],
    removed_factors: set[str],
) -> dict[str, dict[str, Decimal]]:
    known_candidate_ids = {candidate["candidate_id"] for candidate in candidates}
    unknown_candidate_ids = {candidate_id for candidate_id, _, _ in draws} - known_candidate_ids
    if unknown_candidate_ids:
        raise RankingError(f"joint draws reference unknown candidates: {sorted(unknown_candidate_ids)}")
    draw_keys_by_candidate: dict[str, set[str]] = defaultdict(set)
    for candidate_id, draw_key, factor_name in draws:
        if factor_name != "compute_new":
            draw_keys_by_candidate[candidate_id].add(draw_key)
    scores: dict[str, dict[str, Decimal]] = defaultdict(dict)
    for candidate in candidates:
        candidate_id = candidate["candidate_id"]
        active = [factor for factor in factors[candidate_id] if factor.name not in removed_factors]
        active_names = {factor.name for factor in active}
        for draw_key in sorted(draw_keys_by_candidate.get(candidate_id, set())):
            values: list[Decimal] = []
            complete = True
            for factor in active:
                value = draws.get((candidate_id, draw_key, factor.name))
                if value is None:
                    complete = False
                    break
                if factor.role in RATE_ROLES and value > 1:
                    raise RankingError(f"joint draw rate exceeds 1: {candidate_id}/{draw_key}/{factor.name}")
                values.append(value)
            unknown_names = {
                factor_name
                for row_candidate, row_draw, factor_name in draws
                if row_candidate == candidate_id and row_draw == draw_key and factor_name != "compute_new"
            } - active_names - removed_factors
            if unknown_names:
                raise RankingError(f"joint draw has undeclared intrinsic factors for {candidate_id}: {sorted(unknown_names)}")
            if complete:
                product = _product(values)
                assert product is not None
                scores[candidate_id][draw_key] = product
    return dict(scores)


def _enforce_common_complete_draws(
    candidates: Sequence[Mapping[str, str]],
    factors: Mapping[str, Sequence[Factor]],
    draws: Mapping[tuple[str, str, str], Decimal],
    raw_scores: Mapping[str, Mapping[str, Decimal]],
    removed_factors: set[str],
) -> tuple[dict[str, dict[str, Decimal]], dict[str, dict[str, Any]]]:
    """Reject favorable draw subsets; retain only full class-wide joint draw grids."""
    diagnostics: dict[str, dict[str, Any]] = {}
    filtered: dict[str, dict[str, Decimal]] = {}
    by_class: dict[str, list[str]] = defaultdict(list)
    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    for candidate in candidates:
        by_class[candidate["measure_class"]].append(candidate["candidate_id"])
    declared_by_candidate: dict[str, set[str]] = defaultdict(set)
    for candidate_id, draw_key, factor_name in draws:
        if factor_name != "compute_new" and factor_name not in removed_factors:
            declared_by_candidate[candidate_id].add(draw_key)
    for measure_class, candidate_ids in by_class.items():
        dynamic_ids = [candidate_id for candidate_id in candidate_ids if declared_by_candidate[candidate_id]]
        class_draw_keys = set().union(*(declared_by_candidate[candidate_id] for candidate_id in dynamic_ids)) if dynamic_ids else set()
        for candidate_id in candidate_ids:
            declared = declared_by_candidate[candidate_id]
            complete = set(raw_scores.get(candidate_id, {}))
            if not declared:
                diagnostics[candidate_id] = {
                    "draw_completeness_status": "deterministic_no_intrinsic_draws",
                    "declared_intrinsic_draw_count": 0,
                    "complete_intrinsic_draw_count": 0,
                    "missing_joint_draw_count": 0,
                }
                continue
            active_names = {
                factor.name
                for factor in factors[candidate_id]
                if factor.name not in removed_factors
            }
            missing_cells = sum(
                (candidate_id, draw_key, factor_name) not in draws
                for draw_key in class_draw_keys
                for factor_name in active_names
            )
            if declared == class_draw_keys and complete == class_draw_keys and missing_cells == 0:
                filtered[candidate_id] = dict(raw_scores[candidate_id])
                status = "complete_common_joint_draw_set"
            else:
                status = "incomplete_or_noncommon_joint_draw_set"
            diagnostics[candidate_id] = {
                "draw_completeness_status": status,
                "declared_intrinsic_draw_count": len(declared),
                "complete_intrinsic_draw_count": len(complete),
                "missing_joint_draw_count": missing_cells,
            }
    unknown = set(raw_scores) - set(candidate_by_id)
    if unknown:
        raise RankingError(f"draw scores reference unknown candidates: {sorted(unknown)}")
    return filtered, diagnostics


def _competition_assign(records: list[dict[str, Any]], score_field: str, rank_prefix: str) -> None:
    rankable = [row for row in records if row.get(score_field) is not None]
    for measure_class, rows in (("global_common_benefit_v1", rankable),):
        distinct = sorted({row[score_field] for row in rows}, reverse=True)
        rank_by_value = {value: 1 + sum(other > value for other in (row[score_field] for row in rows)) for value in distinct}
        tie_by_value = {value: f"{measure_class}::tie::{index:04d}" for index, value in enumerate(distinct, start=1)}
        count_by_value = {value: sum(row[score_field] == value for row in rows) for value in distinct}
        for row in rows:
            value = row[score_field]
            rank = rank_by_value[value]
            row[f"{rank_prefix}_rank"] = rank
            row[f"{rank_prefix}_tie_group"] = tie_by_value[value]
            row[f"{rank_prefix}_rank_low"] = rank
            row[f"{rank_prefix}_rank_high"] = rank + count_by_value[value] - 1


def _partial_rank_bounds(records: list[dict[str, Any]], *, low_field: str, high_field: str, top_k: int) -> None:
    for rows in (records,):
        n = len(rows)
        for row in rows:
            low = row.get(low_field)
            high = row.get(high_field)
            if low is None or high is None:
                row["possible_rank_best"] = None
                row["possible_rank_worst"] = None
                row["top_k_status"] = "interval_unavailable"
                continue
            best = 1 + sum(
                other.get(low_field) is not None and other[low_field] > high
                for other in rows
                if other is not row
            )
            worst = n - sum(
                other.get(high_field) is not None and other[high_field] < low
                for other in rows
                if other is not row
            )
            row["possible_rank_best"] = best
            row["possible_rank_worst"] = worst
            if worst <= top_k:
                row["top_k_status"] = "definite"
            elif best <= top_k < worst:
                row["top_k_status"] = "possible"
            else:
                row["top_k_status"] = "outside"


def _attach_posterior_rank_summaries(
    records: list[dict[str, Any]],
    draw_scores: Mapping[str, Mapping[str, Decimal]],
    *,
    top_k: int,
    id_field: str = "candidate_id",
    point_field: str = "point_score",
) -> None:
    by_id = {row[id_field]: row for row in records}
    by_class: dict[str, list[str]] = defaultdict(list)
    for row in records:
        record_id = row[id_field]
        if row.get(point_field) is not None:
            by_class["global_common_benefit_v1"].append(record_id)
            row["posterior_rank_population_size"] = 0
            row["posterior_rank_status"] = "unavailable_pending_competitor_audit"
        else:
            row["posterior_rank_status"] = "not_rankable"
    rank_samples: dict[str, list[Decimal]] = defaultdict(list)
    top_hits: dict[str, int] = defaultdict(int)
    rank_draw_counts: dict[str, int] = defaultdict(int)
    for measure_class, candidate_ids in by_class.items():
        for candidate_id in candidate_ids:
            by_id[candidate_id]["posterior_rank_population_size"] = len(candidate_ids)
        drawn_ids = [candidate_id for candidate_id in candidate_ids if draw_scores.get(candidate_id)]
        if not drawn_ids:
            for candidate_id in candidate_ids:
                by_id[candidate_id]["posterior_rank_status"] = "unavailable_no_joint_draw_model"
            continue
        unrepresented = [
            candidate_id
            for candidate_id in candidate_ids
            if not draw_scores.get(candidate_id)
            and by_id[candidate_id].get("posterior_draw_count", 0)
        ]
        if unrepresented:
            for candidate_id in candidate_ids:
                by_id[candidate_id]["posterior_rank_status"] = (
                    "unavailable_unrepresented_rankable_competitor"
                )
            continue
        shared_draws = set.intersection(*(set(draw_scores[candidate_id]) for candidate_id in drawn_ids))
        if not shared_draws:
            for candidate_id in candidate_ids:
                by_id[candidate_id]["posterior_rank_status"] = "unavailable_no_common_joint_draws"
            continue
        for draw_key in sorted(shared_draws):
            scores = {
                candidate_id: (
                    draw_scores[candidate_id][draw_key]
                    if candidate_id in drawn_ids
                    else by_id[candidate_id][point_field]
                )
                for candidate_id in candidate_ids
            }
            for candidate_id, score in scores.items():
                rank = 1 + sum(other > score for other in scores.values())
                rank_samples[candidate_id].append(Decimal(rank))
                rank_draw_counts[candidate_id] += 1
                if rank <= top_k:
                    top_hits[candidate_id] += 1
        for candidate_id in candidate_ids:
            row = by_id[candidate_id]
            samples = rank_samples[candidate_id]
            row["posterior_rank_draw_count"] = rank_draw_counts[candidate_id]
            row["posterior_rank_p05"] = _quantile(samples, Decimal("0.05"))
            row["posterior_rank_median"] = _quantile(samples, Decimal("0.50"))
            row["posterior_rank_p95"] = _quantile(samples, Decimal("0.95"))
            row["posterior_top_k_probability"] = (
                Decimal(top_hits[candidate_id]) / Decimal(rank_draw_counts[candidate_id])
                if rank_draw_counts[candidate_id]
                else None
            )
            row["posterior_rank_status"] = "available_full_competitor_set"


def rank_intrinsic(
    candidates: Sequence[Mapping[str, str]],
    factors: Mapping[str, Sequence[Factor]],
    *,
    draws: Mapping[tuple[str, str, str], Decimal] | None = None,
    removed_factors: Iterable[str] = (),
    top_k: int = 100,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Decimal]]]:
    """Rank intrinsic need/access gain.  No compute input is accepted here."""
    if top_k <= 0:
        raise RankingError("top_k must be positive")
    removed = set(removed_factors)
    all_factor_names = {factor.name for items in factors.values() for factor in items}
    unknown_removed = removed - all_factor_names
    if unknown_removed:
        raise RankingError(f"unknown removed factors: {sorted(unknown_removed)}")
    if any(factor.role == "population" and factor.name in removed for items in factors.values() for factor in items):
        raise RankingError("population factors cannot be removed")
    population_units = {
        factor.unit for items in factors.values() for factor in items
        if factor.role == "population"
    }
    if len(population_units) != 1:
        raise RankingError(f"global comparison mixes incompatible benefit units: {sorted(population_units)}")

    raw_draw_scores = _intrinsic_draw_scores(candidates, factors, draws or {}, removed)
    draw_scores, draw_diagnostics = _enforce_common_complete_draws(
        candidates,
        factors,
        draws or {},
        raw_draw_scores,
        removed,
    )
    records: list[dict[str, Any]] = []
    for candidate in candidates:
        candidate_id = candidate["candidate_id"]
        active = [factor for factor in factors[candidate_id] if factor.name not in removed]
        if any(factor.source_class != "synthetic_fixture" and not factor.event_id for factor in active):
            raise RankingError(f"{candidate_id} lacks normative conditional-event evidence")
        if not any(factor.role == "need" for factor in active):
            raise RankingError(f"factor removal leaves {candidate_id} without a need factor")
        if not any(factor.role == "access_gain" for factor in active):
            raise RankingError(f"factor removal leaves {candidate_id} without an access_gain factor")
        low = _product(factor.low for factor in active)
        base = _product(factor.base for factor in active)
        high = _product(factor.high for factor in active)
        candidate_draws = list(draw_scores.get(candidate_id, {}).values())
        posterior_mean = _mean(candidate_draws)
        point_score = posterior_mean if posterior_mean is not None else base
        point_basis = "joint_draw_mean" if posterior_mean is not None else ("low_base_high_base" if base is not None else "missing")
        rankability = candidate["rankability_status"] or "POINT_DISTRIBUTION"
        eligibility = candidate["eligibility_status"] or "ELIGIBLE"
        if eligibility == "STRUCTURAL_ZERO":
            point_score = Decimal(0) if all(value in {None, Decimal(0)} for value in (low, base, high)) else None
            point_basis = "structural_zero_unranked"
        elif rankability in {"INSUFFICIENT_PUBLIC_EVIDENCE", "INTERVAL_ONLY", "STRUCTURAL_ZERO"}:
            point_score = None
            point_basis = rankability.casefold()
        records.append(
            {
                **candidate,
                "factor_names": ";".join(factor.name for factor in active),
                "factor_measure_classes": ";".join(f"{factor.name}={factor.measure_class}" for factor in active),
                "source_ids": ";".join(sorted({factor.source_id for factor in active})),
                "removed_factors": ";".join(sorted(removed)),
                "intrinsic_low": low,
                "intrinsic_base": base,
                "intrinsic_high": high,
                "point_score": point_score,
                "point_basis": point_basis,
                "posterior_mean": posterior_mean,
                "posterior_p05": _quantile(candidate_draws, Decimal("0.05")),
                "posterior_p50": _quantile(candidate_draws, Decimal("0.50")),
                "posterior_p95": _quantile(candidate_draws, Decimal("0.95")),
                "posterior_draw_count": len(candidate_draws),
                **draw_diagnostics[candidate_id],
                "missing_low_factors": ";".join(factor.name for factor in active if factor.low is None),
                "missing_base_factors": ";".join(factor.name for factor in active if factor.base is None),
                "missing_high_factors": ";".join(factor.name for factor in active if factor.high is None),
                "intrinsic_rank": None,
                "intrinsic_tie_group": "",
                "intrinsic_rank_low": None,
                "intrinsic_rank_high": None,
                "possible_rank_best": None,
                "possible_rank_worst": None,
                "top_k_status": "interval_unavailable",
                "posterior_rank_population_size": 0,
                "posterior_rank_draw_count": 0,
                "posterior_rank_p05": None,
                "posterior_rank_median": None,
                "posterior_rank_p95": None,
                "posterior_top_k_probability": None,
            }
        )
    _competition_assign(records, "point_score", "intrinsic")
    _partial_rank_bounds(records, low_field="intrinsic_low", high_field="intrinsic_high", top_k=top_k)
    _attach_posterior_rank_summaries(records, draw_scores, top_k=top_k)
    records.sort(
        key=lambda row: (
            row["measure_class"],
            row["intrinsic_rank"] if row["intrinsic_rank"] is not None else 10**12,
            row["candidate_id"],
        )
    )
    return records, draw_scores


def _sum_identified(values: Sequence[Decimal | None]) -> Decimal | None:
    return sum((value for value in values if value is not None), Decimal(0)) if all(
        value is not None for value in values
    ) else None


def _language_factor_fingerprint(items: Sequence[Factor]) -> tuple[tuple[Any, ...], ...]:
    return tuple(
        (
            item.name,
            item.role,
            item.conditional_order,
            item.measure_class,
            item.low,
            item.base,
            item.high,
            item.unit,
            item.source_id,
        )
        for item in items
        if item.role in {"population", "need"}
    )


def _language_need_candidate_draws(
    candidate_id: str,
    items: Sequence[Factor],
    draws: Mapping[tuple[str, str, str], Decimal],
) -> tuple[dict[str, Decimal], set[str], int]:
    active = [item for item in items if item.role in {"population", "need"}]
    names = {item.name for item in active}
    declared = {
        draw_key
        for row_candidate, draw_key, factor_name in draws
        if row_candidate == candidate_id and factor_name in names
    }
    scores: dict[str, Decimal] = {}
    missing = 0
    for draw_key in declared:
        values: list[Decimal] = []
        complete = True
        for factor in active:
            value = draws.get((candidate_id, draw_key, factor.name))
            if value is None:
                missing += 1
                complete = False
                break
            values.append(value)
        if complete:
            product = _product(values)
            assert product is not None
            scores[draw_key] = product
    return scores, declared, missing


def rank_language_targets(
    candidates: Sequence[Mapping[str, str]],
    factors: Mapping[str, Sequence[Factor]],
    *,
    draws: Mapping[tuple[str, str, str], Decimal] | None = None,
    top_k: int = 100,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Decimal]]]:
    """Order L: one needs-only row per exact language target, summed over territory cells.

    Package, stage-domain access-gain, delivery-format, and compute values are not
    inputs to the score.  Multiple packages for one target/cell must repeat the
    same language-need evidence and therefore cannot multiply or change the target.
    """
    if top_k <= 0:
        raise RankingError("top_k must be positive")
    population_units = {
        factor.unit for items in factors.values() for factor in items
        if factor.role == "population"
    }
    if len(population_units) != 1:
        raise RankingError(f"Order L mixes incompatible benefit units: {sorted(population_units)}")
    draw_values = draws or {}
    cells: dict[tuple[str, str], list[Mapping[str, str]]] = defaultdict(list)
    for candidate in candidates:
        cells[(candidate["language_target_id"], candidate["territory_cell_id"])].append(candidate)

    cell_rows: dict[tuple[str, str], dict[str, Any]] = {}
    cell_draws: dict[tuple[str, str], dict[str, Decimal]] = {}
    for cell_key, members in cells.items():
        members = sorted(members, key=lambda row: row["candidate_id"])
        fingerprints = {
            _language_factor_fingerprint(factors[member["candidate_id"]])
            for member in members
        }
        if len(fingerprints) != 1:
            raise RankingError(
                f"language target/territory cell {cell_key!r} changes population/need evidence across packages"
            )
        active = [
            item
            for item in factors[members[0]["candidate_id"]]
            if item.role in {"population", "need"}
        ]
        if any(item.source_class != "synthetic_fixture" and not item.event_id for item in active):
            raise RankingError(f"language target/territory cell {cell_key!r} lacks normative joint-need evidence")
        if any(item.source_class != "synthetic_fixture" for item in active):
            for member in members:
                for field in (
                    "population_partition_id", "population_cell_definition",
                    "population_denominator_id", "normative_joint_need_component_id",
                ):
                    if not member[field]:
                        raise RankingError(f"{member['candidate_id']}.{field} is required for production Order L")
        low = _product(item.low for item in active)
        base = _product(item.base for item in active)
        high = _product(item.high for item in active)
        member_draw_maps: list[dict[str, Decimal]] = []
        member_declared: list[set[str]] = []
        member_missing: list[int] = []
        for member in members:
            scores, declared, missing = _language_need_candidate_draws(
                member["candidate_id"], factors[member["candidate_id"]], draw_values
            )
            member_draw_maps.append(scores)
            member_declared.append(declared)
            member_missing.append(missing)
        nonempty_declared = [declared for declared in member_declared if declared]
        complete_cell_draws: dict[str, Decimal] = {}
        if nonempty_declared:
            expected_keys = set.union(*nonempty_declared)
            declared_candidates = [
                (declared, score_map, missing)
                for declared, score_map, missing in zip(member_declared, member_draw_maps, member_missing)
                if declared
            ]
            if all(
                declared == expected_keys and set(score_map) == expected_keys and missing == 0
                for declared, score_map, missing in declared_candidates
            ):
                reference = declared_candidates[0][1]
                if any(score_map != reference for _, score_map, _ in declared_candidates[1:]):
                    raise RankingError(
                        f"language target/territory cell {cell_key!r} has package-dependent need draws"
                    )
                complete_cell_draws = dict(reference)
        if complete_cell_draws:
            cell_draws[cell_key] = complete_cell_draws
        population_factor = next(item for item in active if item.role == "population")
        chain_signature = tuple(
            (item.name, item.role, item.conditional_order, item.measure_class, item.unit,
             item.event_id, item.denominator_stratum_id, item.condition_on_event_id)
            for item in active
        )
        population_identity = (
            members[0]["country_code"], population_factor.source_id,
            population_factor.measure_class, population_factor.unit,
            population_factor.denominator_stratum_id,
        )
        cell_rows[cell_key] = {
            "language_target_id": members[0]["language_target_id"],
            "language_target_label": members[0]["language_target_label"],
            "territory_cell_id": members[0]["territory_cell_id"],
            "language_need_measure_class": members[0]["language_need_measure_class"],
            "country_code": members[0]["country_code"],
            "member_candidate_ids": ";".join(member["candidate_id"] for member in members),
            "intervention_count": len(members),
            "source_ids": ";".join(sorted({item.source_id for item in active})),
            "factor_names": ";".join(item.name for item in active),
            "chain_signature": chain_signature,
            "population_identity": population_identity,
            "low": low,
            "base": base,
            "high": high,
            "draw_status": (
                "complete_common_cell_draws"
                if complete_cell_draws
                else ("incomplete_cell_draws" if nonempty_declared else "deterministic_no_draws")
            ),
            "status_point_rankable": all(
                member["eligibility_status"] != "STRUCTURAL_ZERO"
                and member["rankability_status"] not in {
                    "STRUCTURAL_ZERO", "INSUFFICIENT_PUBLIC_EVIDENCE", "INTERVAL_ONLY"
                }
                for member in members
            ),
        }

    by_target: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in cell_rows.values():
        by_target[row["language_target_id"]].append(row)
    records: list[dict[str, Any]] = []
    target_draw_scores: dict[str, dict[str, Decimal]] = {}
    for language_target_id, target_cells in by_target.items():
        target_cells = sorted(target_cells, key=lambda row: row["territory_cell_id"])
        measure_classes = {row["language_need_measure_class"] for row in target_cells}
        labels = {row["language_target_label"] for row in target_cells}
        if len(measure_classes) != 1 or len(labels) != 1:
            raise RankingError(f"language target {language_target_id!r} is not one comparable target")
        chain_signatures = {row["chain_signature"] for row in target_cells}
        if len(chain_signatures) != 1:
            raise RankingError(f"language target {language_target_id!r} mixes incompatible need chains")
        population_identities = [row["population_identity"] for row in target_cells]
        if len(population_identities) != len(set(population_identities)):
            raise RankingError(
                f"language target {language_target_id!r} repeats one population basis under renamed territory cells"
            )
        low = _sum_identified([row["low"] for row in target_cells])
        base = _sum_identified([row["base"] for row in target_cells])
        high = _sum_identified([row["high"] for row in target_cells])
        random_cells = [
            (row, cell_draws[(language_target_id, row["territory_cell_id"])])
            for row in target_cells
            if (language_target_id, row["territory_cell_id"]) in cell_draws
        ]
        incomplete_cells = [row for row in target_cells if row["draw_status"] == "incomplete_cell_draws"]
        combined_draws: dict[str, Decimal] = {}
        if random_cells and not incomplete_cells:
            shared = set.intersection(*(set(score_map) for _, score_map in random_cells))
            if shared and all(set(score_map) == shared for _, score_map in random_cells):
                for draw_key in sorted(shared):
                    values: list[Decimal] = []
                    for row in target_cells:
                        score_map = cell_draws.get((language_target_id, row["territory_cell_id"]))
                        value = score_map[draw_key] if score_map else row["base"]
                        if value is None:
                            values = []
                            break
                        values.append(value)
                    if values:
                        combined_draws[draw_key] = sum(values, Decimal(0))
        if combined_draws:
            target_draw_scores[language_target_id] = combined_draws
        posterior_values = list(combined_draws.values())
        posterior_mean = _mean(posterior_values)
        point_score = posterior_mean if posterior_mean is not None else base
        if not all(row["status_point_rankable"] for row in target_cells):
            point_score = None
            posterior_mean = None
            target_draw_scores.pop(language_target_id, None)
        records.append(
            {
                "language_target_id": language_target_id,
                "language_target_label": target_cells[0]["language_target_label"],
                "measure_class": target_cells[0]["language_need_measure_class"],
                "territory_cell_ids": ";".join(row["territory_cell_id"] for row in target_cells),
                "country_codes": ";".join(sorted({row["country_code"] for row in target_cells})),
                "member_candidate_ids": ";".join(
                    candidate_id
                    for row in target_cells
                    for candidate_id in row["member_candidate_ids"].split(";")
                ),
                "territory_cell_count": len(target_cells),
                "intervention_count": sum(row["intervention_count"] for row in target_cells),
                "source_ids": ";".join(sorted({source_id for row in target_cells for source_id in row["source_ids"].split(";")})),
                "factor_names": target_cells[0]["factor_names"],
                "language_need_low": low,
                "language_need_base": base,
                "language_need_high": high,
                "point_score": point_score,
                "point_basis": "joint_draw_mean" if posterior_mean is not None else ("low_base_high_base" if base is not None else "missing"),
                "posterior_mean": posterior_mean,
                "posterior_p05": _quantile(posterior_values, Decimal("0.05")),
                "posterior_p50": _quantile(posterior_values, Decimal("0.50")),
                "posterior_p95": _quantile(posterior_values, Decimal("0.95")),
                "posterior_draw_count": len(posterior_values),
                "draw_completeness_status": (
                    "complete_transnational_joint_draws"
                    if combined_draws
                    else ("incomplete_territory_draws" if incomplete_cells else "deterministic_no_draws")
                ),
                "language_rank": None,
                "language_tie_group": "",
                "language_rank_low": None,
                "language_rank_high": None,
                "possible_rank_best": None,
                "possible_rank_worst": None,
                "top_k_status": "interval_unavailable",
                "posterior_rank_population_size": 0,
                "posterior_rank_draw_count": 0,
                "posterior_rank_p05": None,
                "posterior_rank_median": None,
                "posterior_rank_p95": None,
                "posterior_top_k_probability": None,
            }
        )
    _competition_assign(records, "point_score", "language")
    _partial_rank_bounds(records, low_field="language_need_low", high_field="language_need_high", top_k=top_k)
    _attach_posterior_rank_summaries(
        records,
        target_draw_scores,
        top_k=top_k,
        id_field="language_target_id",
        point_field="point_score",
    )
    records.sort(
        key=lambda row: (
            row["measure_class"],
            row["language_rank"] if row["language_rank"] is not None else 10**12,
            row["language_target_id"],
        )
    )
    return records, target_draw_scores


def build_overlap_portfolio_units(
    records: Sequence[Mapping[str, Any]],
    *,
    draw_scores: Mapping[str, Mapping[str, Decimal]] | None = None,
    top_k: int = 100,
) -> list[dict[str, Any]]:
    """Collapse explicitly substitutable max-union groups into benefit units."""
    units: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    group_classes: dict[str, set[str]] = defaultdict(set)
    group_compatibility: dict[str, set[tuple[str, ...]]] = defaultdict(set)
    for row in records:
        if row["overlap_rule"] == "max_union":
            unit_id = f"overlap::{row['overlap_group_id']}"
            group_classes[row["overlap_group_id"]].add(row["measure_class"])
            signature = (
                _text(row.get("country_code")),
                _text(row.get("stratum_compatibility_key")),
                _text(row.get("measure_class")),
                _text(row.get("endpoint_id")),
                _text(row.get("horizon_months")),
                _text(row.get("overlap_evidence_source_id")),
                _text(row.get("overlap_evidence_source_url")),
            )
            if not all(signature):
                raise RankingError(
                    f"max_union row lacks compatibility or public evidence identity: {row.get('candidate_id')}"
                )
            group_compatibility[row["overlap_group_id"]].add(signature)
        else:
            unit_id = f"candidate::{row['candidate_id']}"
        units[(row["measure_class"], unit_id)].append(row)
    invalid_groups = {group: classes for group, classes in group_classes.items() if len(classes) > 1}
    if invalid_groups:
        raise RankingError(f"overlap groups cross measure classes: {invalid_groups}")
    incompatible_groups = {
        group: sorted(signatures)
        for group, signatures in group_compatibility.items()
        if len(signatures) != 1
    }
    if incompatible_groups:
        raise RankingError(
            "max_union overlap groups mix geography, strata, endpoints, or evidence identity: "
            f"{incompatible_groups}"
        )
    output: list[dict[str, Any]] = []
    unit_draw_scores: dict[str, dict[str, Decimal]] = defaultdict(dict)
    for (measure_class, unit_id), members in units.items():
        members = sorted(members, key=lambda member: member["candidate_id"])
        member_ids = sorted(member["candidate_id"] for member in members)
        member_points = [member.get("point_score") for member in members]
        member_lows = [member.get("intrinsic_low") for member in members]
        member_highs = [member.get("intrinsic_high") for member in members]

        # max_union is a maximum of substitutable benefit events.  A known member
        # lower bound remains a valid lower bound; the upper bound is identified
        # only when every member upper bound is known.
        known_lows = [value for value in member_lows if value is not None]
        portfolio_low = max(known_lows) if known_lows else None
        portfolio_high = max(member_highs) if all(value is not None for value in member_highs) else None

        complete_points = all(value is not None for value in member_points)
        gain = max(member_points) if complete_points else None
        group_draws: dict[str, Decimal] = {}
        member_draw_maps: list[Mapping[str, Decimal]] = []
        if draw_scores is not None and members:
            member_draw_maps = [draw_scores.get(member_id, {}) for member_id in member_ids]
            random_maps = [item for item in member_draw_maps if item]
            deterministic_points = {
                member_id: member.get("point_score")
                for member_id, member, member_map in zip(member_ids, members, member_draw_maps)
                if not member_map
            }
            if random_maps and all(value is not None for value in deterministic_points.values()):
                shared_draws = set.intersection(*(set(item) for item in random_maps))
                for draw_key in sorted(shared_draws):
                    values = [
                        member_map[draw_key]
                        if member_map
                        else deterministic_points[member_id]
                        for member_id, member_map in zip(member_ids, member_draw_maps)
                    ]
                    group_draws[draw_key] = max(values)
        if group_draws:
            unit_draw_scores[unit_id] = group_draws
            gain = _mean(list(group_draws.values()))

        if len(members) == 1:
            representatives = member_ids
            representative_status = "unique"
        elif group_draws:
            representatives = sorted(
                {
                    member_id
                    for draw_key, draw_maximum in group_draws.items()
                    for member_id, member_draw_map in zip(member_ids, member_draw_maps)
                    if member_draw_map[draw_key] == draw_maximum
                }
            )
            representative_status = "unique" if len(representatives) == 1 else "draw_dependent"
        elif complete_points:
            representatives = sorted(
                member["candidate_id"] for member in members if member.get("point_score") == gain
            )
            representative_status = "tied" if len(representatives) > 1 else "unique"
        else:
            representatives = []
            representative_status = "unresolved"
        posterior_values = list(group_draws.values())
        substitution_diagnostic_gain = gain
        substitution_diagnostic_posterior_draw_count = len(posterior_values)
        portfolio_point_basis = "joint_draw_mean_of_drawwise_max" if group_draws else ("complete_member_point_max" if complete_points else "missing_member_point")
        if unit_id.startswith("overlap::") and len(members) > 1:
            # A qualitative source identity establishes neither unique union
            # benefit nor sequential marginal portfolio gain. Preserve the max
            # only as a substitution diagnostic; do not point-rank it.
            gain = None
            group_draws = {}
            posterior_values = []
            unit_draw_scores.pop(unit_id, None)
            portfolio_point_basis = "qualitative_overlap_unranked_substitution_diagnostic_only"
        output.append(
            {
                "measure_class": measure_class,
                "portfolio_unit_id": unit_id,
                "overlap_rule": "max_union" if unit_id.startswith("overlap::") else "none",
                "overlap_group_id": unit_id.split("::", 1)[1] if unit_id.startswith("overlap::") else "",
                "member_candidate_ids": ";".join(member_ids),
                "representative_candidate_ids": ";".join(representatives),
                "representative_status": representative_status,
                "portfolio_low": portfolio_low,
                "portfolio_gain": gain,
                "substitution_diagnostic_gain": substitution_diagnostic_gain,
                "substitution_diagnostic_posterior_draw_count": substitution_diagnostic_posterior_draw_count,
                "portfolio_high": portfolio_high,
                "point_basis": portfolio_point_basis,
                "posterior_mean": _mean(posterior_values),
                "posterior_p05": _quantile(posterior_values, Decimal("0.05")),
                "posterior_p50": _quantile(posterior_values, Decimal("0.50")),
                "posterior_p95": _quantile(posterior_values, Decimal("0.95")),
                "posterior_draw_count": len(posterior_values),
                "portfolio_rank": None,
                "portfolio_tie_group": "",
                "portfolio_rank_low": None,
                "portfolio_rank_high": None,
                "possible_rank_best": None,
                "possible_rank_worst": None,
                "top_k_status": "interval_unavailable",
                "posterior_rank_population_size": 0,
                "posterior_rank_draw_count": 0,
                "posterior_rank_p05": None,
                "posterior_rank_median": None,
                "posterior_rank_p95": None,
                "posterior_top_k_probability": None,
            }
        )
    _competition_assign(output, "portfolio_gain", "portfolio")
    _partial_rank_bounds(output, low_field="portfolio_low", high_field="portfolio_high", top_k=top_k)
    _attach_posterior_rank_summaries(
        output,
        unit_draw_scores,
        top_k=top_k,
        id_field="portfolio_unit_id",
        point_field="portfolio_gain",
    )
    output.sort(
        key=lambda row: (
            row["measure_class"],
            row["portfolio_rank"] if row["portfolio_rank"] is not None else 10**12,
            row["portfolio_unit_id"],
        )
    )
    return output


@dataclass(frozen=True)
class ComputeEstimate:
    candidate_id: str
    intervention_key: str
    language_target_id: str
    package_id: str
    learner_stage: str
    subject_domain: str
    delivery_format: str
    scope: str
    measure_class: str
    low: Decimal | None
    base: Decimal | None
    high: Decimal | None
    unit: str
    source_id: str
    formula_version: str
    factor_registry_version: str
    compute_input_set_hash: str
    benchmark_profile_id: str
    direct_measurement_row_hash: str
    successor_roster_file_sha256: str
    target_binding_row_hash: str
    target_binding_set_hash: str


def _standard_compute_registry_versions(
    path: Path = DEFAULT_STANDARD_COMPUTE_REGISTRY_PATH,
) -> set[str]:
    if not path.exists():
        return set()
    rows = read_csv(path)
    return {_text(row.get("factor_registry_version")) for row in rows if _text(row.get("factor_registry_version"))}


def _standard_compute_registry_rows(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    rows = read_csv(path)
    result: dict[tuple[str, str], dict[str, str]] = {}
    row_hashes: list[str] = []
    registry_hashes: set[str] = set()
    for index, row in enumerate(rows, start=2):
        version = _text(row.get("factor_registry_version"))
        factor_id = _text(row.get("factor_id"))
        if not version or not factor_id or (version, factor_id) in result:
            raise RankingError(f"standard-compute registry row {index} has a blank or duplicate key")
        clean = {
            key: row[key]
            for key in sorted(row)
            if key not in {"registry_row_hash", "registry_hash"}
        }
        observed_row_hash = sha256_bytes(
            json.dumps(clean, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        )
        if _text(row.get("registry_row_hash")).casefold() != observed_row_hash:
            raise RankingError(f"standard-compute registry row {index} hash mismatch")
        for field in (
            "coefficient_mean",
            "coefficient_p05",
            "coefficient_p50",
            "coefficient_p95",
            "coefficient_lower_bound",
            "coefficient_upper_bound",
        ):
            coefficient = _decimal(row.get(field), label=f"registry/{factor_id}.{field}")
            if coefficient != Decimal(1):
                raise RankingError(f"registry/{factor_id}.{field} must be the pinned identity coefficient 1")
        if _has_forbidden_token(_text(row.get("factor_code"))) or _has_forbidden_token(
            _text(row.get("factor_description"))
        ):
            raise RankingError(f"registry/{factor_id} contains a forbidden local/project factor")
        row_hashes.append(observed_row_hash)
        registry_hashes.add(_text(row.get("registry_hash")).casefold())
        result[(version, factor_id)] = row
    expected_registry_hash = sha256_bytes(("\n".join(row_hashes) + "\n").encode("ascii"))
    if registry_hashes != {expected_registry_hash}:
        raise RankingError("standard-compute registry semantic hash mismatch")
    expected_factor_ids = {f"F{index:03d}" for index in range(1, 49)}
    observed_factor_ids = {factor_id for _, factor_id in result}
    versions = {version for version, _ in result}
    if len(versions) != 1 or observed_factor_ids != expected_factor_ids:
        raise RankingError("standard-compute registry must be the complete closed F001-F048 ledger")
    registry_version = next(iter(versions))
    pinned_file_hash = PINNED_STANDARD_COMPUTE_REGISTRY_SHA256.get(registry_version)
    if pinned_file_hash is None or sha256_file(path) != pinned_file_hash:
        raise RankingError("standard-compute registry bytes are not the pinned registry for this version")
    return result


def _verify_compute_factor_input_row(row: Mapping[str, Any], *, index: int) -> None:
    clean = {key: row[key] for key in sorted(row) if key != "input_row_hash"}
    observed = sha256_bytes(
        json.dumps(clean, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    if _text(row.get("input_row_hash")).casefold() != observed:
        raise RankingError(f"standard-compute factor-input row {index} hash mismatch")


def _load_standard_compute_measurement_profiles(
    tokenization_measurements_path: Path,
    measurement_profiles_path: Path,
) -> tuple[dict[str, dict[str, str]], str, str, str]:
    tokenization_hash = sha256_file(tokenization_measurements_path)
    if tokenization_hash != PINNED_STANDARD_COMPUTE_TOKENIZATION_SHA256:
        raise RankingError("standard-compute tokenization measurements are not the pinned benchmark bytes")
    token_rows = read_csv(tokenization_measurements_path)
    token_by_profile: dict[str, dict[str, str]] = {}
    for index, row in enumerate(token_rows, start=2):
        if _text(row.get("is_reference_source")).casefold() == "true":
            continue
        profile_id = f"flores:{_text(row.get('flores_code'))}"
        if not _text(row.get("flores_code")) or profile_id in token_by_profile:
            raise RankingError(f"tokenization measurement row {index} has a blank or duplicate profile")
        token_by_profile[profile_id] = row

    profile_rows = read_csv(measurement_profiles_path)
    profile_by_id: dict[str, dict[str, str]] = {}
    row_hashes: list[str] = []
    set_hashes: set[str] = set()
    for index, row in enumerate(profile_rows, start=2):
        profile_id = _text(row.get("benchmark_profile_id"))
        if not profile_id or profile_id in profile_by_id or profile_id not in token_by_profile:
            raise RankingError(f"measurement-profile row {index} has an unknown, blank, or duplicate profile")
        clean = {
            key: row[key]
            for key in sorted(row)
            if key not in {"profile_row_hash", "profile_set_hash"}
        }
        row_hash = sha256_bytes(
            json.dumps(clean, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        )
        token_row = token_by_profile[profile_id]
        token_row_hash = sha256_bytes(
            json.dumps(
                {key: token_row[key] for key in sorted(token_row)},
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        )
        if _text(row.get("profile_row_hash")).casefold() != row_hash:
            raise RankingError(f"measurement-profile row {index} hash mismatch")
        if _text(row.get("direct_measurement_row_hash")).casefold() != token_row_hash:
            raise RankingError(f"measurement-profile row {index} does not bind its direct tokenization row")
        if (
            profile_id != f"flores:{_text(token_row.get('flores_code'))}"
            or _text(row.get("flores_code")) != _text(token_row.get("flores_code"))
            or _text(row.get("language_code")) != _text(token_row.get("language_code"))
            or _text(row.get("script_code")) != _text(token_row.get("script_code"))
            or _text(row.get("aligned_sentences")) != "1012"
            or _text(row.get("profile_measurement_kind")) != "DIRECT_ALIGNED_BENCHMARK"
            or _text(row.get("profile_match_scope")) != "ALIGNED_LANGUAGE_SCRIPT_TOKENIZATION_PROXY"
            or _text(row.get("tokenization_measurement_set_sha256")).casefold() != tokenization_hash
        ):
            raise RankingError(f"measurement-profile row {index} is not an exact direct aligned profile")
        row_hashes.append(row_hash)
        set_hashes.add(_text(row.get("profile_set_hash")).casefold())
        profile_by_id[profile_id] = row
    expected_set_hash = sha256_bytes(("\n".join(row_hashes) + "\n").encode("ascii"))
    if set(profile_by_id) != set(token_by_profile) or len(profile_by_id) != 203 or set_hashes != {expected_set_hash}:
        raise RankingError("measurement-profile registry is incomplete or has a semantic set-hash mismatch")
    return profile_by_id, tokenization_hash, sha256_file(measurement_profiles_path), expected_set_hash


def _compute_tag_components(tag: str) -> tuple[str, str, str]:
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


def _compute_canonical_json_bytes(value: Any) -> bytes:
    """Match the UTF-8 canonicalization used by the frozen compute registries."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _compute_target_representation(target: Mapping[str, Any]) -> dict[str, Any]:
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


def _exact_successor_profile_matches(
    target: Mapping[str, Any],
    measurement_profiles_by_id: Mapping[str, Mapping[str, str]],
) -> list[Mapping[str, str]]:
    by_language_script: dict[tuple[str, str], Mapping[str, str]] = {}
    for profile in measurement_profiles_by_id.values():
        key = (_text(profile.get("language_code")).casefold(), _text(profile.get("script_code")).casefold())
        if key in by_language_script:
            raise RankingError(f"ambiguous pinned measurement profiles for exact language/script {key}")
        by_language_script[key] = profile
    matched: dict[str, Mapping[str, str]] = {}
    for tag in target.get("language_tags", []):
        language, script, _ = _compute_tag_components(str(tag))
        if language and script:
            profile = by_language_script.get((language, script.casefold()))
            if profile is not None:
                matched[_text(profile.get("benchmark_profile_id"))] = profile
    return [matched[key] for key in sorted(matched)]


def _load_standard_compute_target_bindings(
    successor_roster_path: Path,
    target_bindings_path: Path,
    measurement_profiles_by_id: Mapping[str, Mapping[str, str]],
    *,
    tokenization_measurement_set_hash: str,
    measurement_profile_registry_file_hash: str,
    measurement_profile_set_hash: str,
) -> tuple[dict[str, dict[str, str]], str, str]:
    successor_roster_file_hash = sha256_file(successor_roster_path)
    if successor_roster_file_hash != PINNED_SUCCESSOR_TARGET_ROSTER_SHA256:
        raise RankingError("successor target roster bytes do not match the pinned frozen roster")
    roster = json.loads(successor_roster_path.read_text(encoding="utf-8"))
    if roster.get("schema") != "interlanguage/successor-target-roster/2.0.0":
        raise RankingError("successor target roster schema is not pinned v2")
    payload = {
        key: value
        for key, value in roster.items()
        if key not in {"snapshot_id", "snapshot_payload_sha256"}
    }
    payload_hash = sha256_bytes(_compute_canonical_json_bytes(payload))
    roster_snapshot_id = f"successor-target-roster:sha256:{payload_hash}"
    if (
        _text(roster.get("snapshot_payload_sha256")).casefold() != payload_hash
        or _text(roster.get("snapshot_id")) != roster_snapshot_id
    ):
        raise RankingError("successor target roster snapshot hash or ID mismatch")
    targets = roster.get("roster_targets")
    if not isinstance(targets, list) or not targets:
        raise RankingError("frozen successor roster has no roster_targets")
    target_by_id: dict[str, Mapping[str, Any]] = {}
    for target in targets:
        target_id = _text(target.get("roster_target_id"))
        if not target_id or target_id in target_by_id:
            raise RankingError("frozen successor roster has blank or duplicate roster_target_id")
        clean_target = {key: target[key] for key in sorted(target) if key != "roster_row_sha256"}
        target_row_hash = sha256_bytes(_compute_canonical_json_bytes(clean_target))
        expected_requirement = (
            "DIRECT_EXACT_PROFILE_OR_EXPLICIT_MISSING_UNRANKED"
            if target.get("production_applicable") is True
            else "EXPLICIT_CONTEXT_OR_MISSING_UNRANKED_ONLY"
        )
        if (
            _text(target.get("roster_row_sha256")).casefold() != target_row_hash
            or _text(target.get("profile_binding_requirement")) != expected_requirement
        ):
            raise RankingError(f"frozen successor roster row {target_id!r} has invalid row provenance")
        target_by_id[target_id] = target

    if sha256_file(target_bindings_path) != PINNED_STANDARD_COMPUTE_TARGET_BINDINGS_SHA256:
        raise RankingError("target-binding registry bytes do not match the pinned exhaustive registry")
    binding_rows = read_csv(target_bindings_path)
    binding_by_target: dict[str, dict[str, str]] = {}
    row_hashes: list[str] = []
    set_hashes: set[str] = set()
    for index, row in enumerate(binding_rows, start=2):
        target_id = _text(row.get("roster_target_id"))
        if not target_id or target_id in binding_by_target or target_id not in target_by_id:
            raise RankingError(f"target-binding row {index} has a blank, duplicate, or non-roster target")
        clean = {
            key: row[key]
            for key in sorted(row)
            if key not in {"binding_row_hash", "binding_set_hash"}
        }
        row_hash = sha256_bytes(_compute_canonical_json_bytes(clean))
        if _text(row.get("binding_row_hash")).casefold() != row_hash:
            raise RankingError(f"target-binding row {index} hash mismatch")
        target = target_by_id[target_id]
        target_roster_hash = _text(target.get("roster_row_sha256")).casefold()
        representation_id = "repr:" + sha256_bytes(_compute_canonical_json_bytes(_compute_target_representation(target)))[:24]
        if (
            _text(row.get("roster_snapshot_id")) != roster_snapshot_id
            or _text(row.get("successor_roster_file_sha256")).casefold() != successor_roster_file_hash
            or _text(row.get("target_roster_row_hash")).casefold() != target_roster_hash
            or _text(row.get("target_kind")) != _text(target.get("target_kind"))
            or _text(row.get("language_target_id")) != _text(target.get("language_target_id"))
            or _text(row.get("intervention_target_id")) != _text(target.get("intervention_target_id"))
            or _text(row.get("production_applicable")).casefold()
            != ("true" if target.get("production_applicable") is True else "false")
            or _text(row.get("target_representation_id")) != representation_id
            or _text(row.get("tokenization_measurement_set_sha256")).casefold() != tokenization_measurement_set_hash
            or _text(row.get("measurement_profile_registry_file_sha256")).casefold() != measurement_profile_registry_file_hash
            or _text(row.get("measurement_profile_set_hash")).casefold() != measurement_profile_set_hash
            or _text(row.get("sensitivity_control_status")) != "COMMON_ENVELOPE_AVAILABLE_SEPARATELY_NOT_FOR_POINT_ORDER"
        ):
            raise RankingError(f"target-binding row {index} does not bind the frozen roster and measurement bytes")
        exact_matches = (
            _exact_successor_profile_matches(target, measurement_profiles_by_id)
            if target.get("target_kind") == "canonical_language_target"
            else []
        )
        production_applicable = target.get("production_applicable") is True
        if len(exact_matches) == 1:
            measured = exact_matches[0]
            expected_eligible = "true" if production_applicable else "false"
            expected_unavailable = "" if production_applicable else "NOT_PRODUCTION_APPLICABLE"
            if (
                _text(row.get("benchmark_profile_id")) != _text(measured.get("benchmark_profile_id"))
                or _text(row.get("profile_measurement_kind")) != "DIRECT_ALIGNED_BENCHMARK"
                or _text(row.get("profile_match_scope")) != "ALIGNED_LANGUAGE_SCRIPT_TOKENIZATION_PROXY"
                or _text(row.get("binding_method")) != "EXACT_BCP47_LANGUAGE_SUBTAG_AND_EXPLICIT_SCRIPT"
                or _text(row.get("binding_status")) != "DIRECT_PROFILE_BOUND"
                or _text(row.get("order_b_eligible")).casefold() != expected_eligible
                or _text(row.get("unavailable_reason")) != expected_unavailable
                or _text(row.get("direct_measurement_row_hash")).casefold() != _text(measured.get("direct_measurement_row_hash")).casefold()
            ):
                raise RankingError(f"target-binding row {index} misstates an exact direct profile")
        else:
            if not production_applicable:
                expected_unavailable = "NOT_PRODUCTION_APPLICABLE_AND_NO_DIRECT_ALIGNED_PROFILE"
            elif target.get("target_kind") != "canonical_language_target":
                expected_unavailable = "TARGET_HAS_NO_DIRECT_LANGUAGE_SCRIPT_PROFILE"
            elif len(exact_matches) > 1:
                expected_unavailable = "AMBIGUOUS_EXACT_CODE_SCRIPT_PROFILES"
            else:
                expected_unavailable = "NO_DIRECT_ALIGNED_PROFILE"
            if (
                _text(row.get("benchmark_profile_id"))
                or _text(row.get("profile_measurement_kind")) != "NONE"
                or _text(row.get("profile_match_scope")) != "NONE"
                or _text(row.get("binding_method")) != "NO_EXACT_CODE_SCRIPT_MATCH"
                or _text(row.get("binding_status")) != "NO_DIRECT_PROFILE"
                or _text(row.get("order_b_eligible")).casefold() != "false"
                or _text(row.get("unavailable_reason")) != expected_unavailable
                or _text(row.get("direct_measurement_row_hash"))
            ):
                raise RankingError(f"target-binding row {index} must remain explicitly missing and unranked")
        row_hashes.append(row_hash)
        set_hashes.add(_text(row.get("binding_set_hash")).casefold())
        binding_by_target[target_id] = row
    expected_set_hash = sha256_bytes(("\n".join(row_hashes) + "\n").encode("ascii"))
    if set(binding_by_target) != set(target_by_id) or set_hashes != {expected_set_hash}:
        raise RankingError("target-binding registry does not cover the frozen successor roster exactly once")
    return binding_by_target, expected_set_hash, successor_roster_file_hash


def normalize_compute(
    rows: Sequence[Mapping[str, Any]],
    intrinsic_records: Sequence[Mapping[str, Any]],
    *,
    allow_synthetic: bool = False,
    compute_inputs_path: Path | None = None,
    factor_inputs_path: Path | None = None,
    compute_registry_path: Path = DEFAULT_STANDARD_COMPUTE_REGISTRY_PATH,
    tokenization_measurements_path: Path | None = None,
    measurement_profiles_path: Path | None = None,
    successor_roster_path: Path | None = None,
    target_bindings_path: Path | None = None,
    allow_profile_contract_examples: bool = False,
) -> tuple[dict[str, ComputeEstimate], list[str]]:
    ignored = ignored_columns(rows, COMPUTE_FIELDS)
    projected = _project_rows(rows, COMPUTE_FIELDS)
    candidate_by_id = {row["candidate_id"]: row for row in intrinsic_records}
    valid_ids = set(candidate_by_id)
    result: dict[str, ComputeEstimate] = {}
    registered_compute_versions = _standard_compute_registry_versions(compute_registry_path)
    production_rows = [row for row in projected if row.get("source_class") != "synthetic_fixture"]
    derivations_by_candidate: dict[str, list[dict[str, str]]] = defaultdict(list)
    factor_inputs_by_candidate: dict[str, list[dict[str, str]]] = defaultdict(list)
    registry_rows: dict[tuple[str, str], dict[str, str]] = {}
    derivation_bytes_hash = ""
    factor_input_bytes_hash = ""
    registry_bytes_hash = ""
    measurement_profiles_by_id: dict[str, dict[str, str]] = {}
    tokenization_measurement_set_hash = ""
    measurement_profile_registry_file_hash = ""
    measurement_profile_set_hash = ""
    target_bindings_by_id: dict[str, dict[str, str]] = {}
    target_binding_set_hash = ""
    successor_roster_file_hash = ""
    if production_rows:
        if (
            compute_inputs_path is None
            or factor_inputs_path is None
            or tokenization_measurements_path is None
            or measurement_profiles_path is None
        ):
            raise RankingError(
                "public standardized compute requires canonical derivations, normalized factor inputs, pinned tokenization measurements, and the direct-profile registry"
            )
        derivation_bytes_hash = sha256_file(compute_inputs_path)
        factor_input_bytes_hash = sha256_file(factor_inputs_path)
        registry_bytes_hash = sha256_file(compute_registry_path)
        for item in read_csv(compute_inputs_path):
            derivations_by_candidate[_text(item.get("candidate_id"))].append(item)
        for factor_index, item in enumerate(read_csv(factor_inputs_path), start=2):
            _verify_compute_factor_input_row(item, index=factor_index)
            factor_inputs_by_candidate[_text(item.get("candidate_id"))].append(item)
        registry_rows = _standard_compute_registry_rows(compute_registry_path)
        (
            measurement_profiles_by_id,
            tokenization_measurement_set_hash,
            measurement_profile_registry_file_hash,
            measurement_profile_set_hash,
        ) = _load_standard_compute_measurement_profiles(
            tokenization_measurements_path,
            measurement_profiles_path,
        )
        if (successor_roster_path is None) != (target_bindings_path is None):
            raise RankingError("successor roster and target-binding registry must be supplied together")
        if successor_roster_path is not None and target_bindings_path is not None:
            (
                target_bindings_by_id,
                target_binding_set_hash,
                successor_roster_file_hash,
            ) = _load_standard_compute_target_bindings(
                successor_roster_path,
                target_bindings_path,
                measurement_profiles_by_id,
                tokenization_measurement_set_hash=tokenization_measurement_set_hash,
                measurement_profile_registry_file_hash=measurement_profile_registry_file_hash,
                measurement_profile_set_hash=measurement_profile_set_hash,
            )
    for index, row in enumerate(projected, start=2):
        candidate_id = row["candidate_id"]
        if candidate_id not in valid_ids:
            raise RankingError(f"compute row {index} has unknown candidate_id: {candidate_id}")
        candidate = candidate_by_id[candidate_id]
        for field in (
            "language_target_id",
            "package_id",
            "learner_stage",
            "subject_domain",
            "delivery_format",
            "compute_scope",
            "compute_measure_class",
            "compute_unit",
            "formula_version",
            "factor_registry_version",
            "compute_input_set_hash",
        ):
            if not row[field]:
                raise RankingError(f"{candidate_id}.{field} is required in compute table")
        for field in ("language_target_id", "package_id", "learner_stage", "subject_domain", "delivery_format"):
            if row[field] != candidate[field]:
                raise RankingError(
                    f"compute/{candidate_id}.{field} does not match the composite intervention endpoint"
                )
        intervention_key = candidate["intervention_key"]
        if intervention_key in result:
            raise RankingError(f"duplicate compute intervention row: {intervention_key}")
        if row["compute_scope"] != "standardized_from_scratch":
            raise RankingError(f"{candidate_id}.compute_scope must be standardized_from_scratch")
        for field in ("package_id", "delivery_format", "compute_scope", "compute_measure_class", "compute_unit", "formula_version"):
            if _has_forbidden_token(row[field]):
                raise RankingError(f"{candidate_id}.{field} contains a forbidden local/project token")
        _require_public_source(row, allow_synthetic=allow_synthetic, label=f"compute/{candidate_id}")
        if not _is_sha256(row["compute_input_set_hash"]):
            raise RankingError(f"{candidate_id}.compute_input_set_hash must be SHA-256")
        if row["source_class"] != "synthetic_fixture":
            for field in (
                "compute_derivation_set_hash",
                "factor_registry_file_hash",
                "compute_model_role",
                "compute_evidence_status",
                "benchmark_profile_id",
                "tokenization_measurement_set_sha256",
                "measurement_profile_registry_file_sha256",
                "measurement_profile_set_hash",
                "direct_measurement_row_hash",
                "compute_binding_mode",
            ):
                if not row[field]:
                    raise RankingError(f"{candidate_id}.{field} is required for public standardized compute")
            if row["compute_input_set_hash"].casefold() != factor_input_bytes_hash:
                raise RankingError(f"{candidate_id}.compute_input_set_hash does not match normalized factor-input bytes")
            if not _is_sha256(row["compute_derivation_set_hash"]) or row["compute_derivation_set_hash"].casefold() != derivation_bytes_hash:
                raise RankingError(f"{candidate_id}.compute_derivation_set_hash does not match canonical derivation bytes")
            if not _is_sha256(row["factor_registry_file_hash"]) or row["factor_registry_file_hash"].casefold() != registry_bytes_hash:
                raise RankingError(f"{candidate_id}.factor_registry_file_hash does not match the closed registry bytes")
            if row["compute_model_role"] != "primary_measured_feature" or row["compute_evidence_status"] != "MEASURED_COMMON_BENCHMARK":
                raise RankingError(f"{candidate_id} is not an admissible primary measured-feature compute row")
            binding_mode = row["compute_binding_mode"]
            if binding_mode == "PROFILE_CONTRACT_EXAMPLE":
                if (
                    not allow_profile_contract_examples
                    or row["benchmark_profile_id"] != row["language_target_id"]
                    or not row["language_target_id"].startswith("flores:")
                    or any(row[field] for field in ("successor_roster_file_sha256", "target_binding_row_hash", "target_binding_set_hash", "order_b_eligible"))
                ):
                    raise RankingError(f"{candidate_id} profile-contract examples cannot enter production compute-efficiency order")
            elif binding_mode == "FROZEN_SUCCESSOR_BINDING":
                binding = target_bindings_by_id.get(row["language_target_id"])
                if binding is None:
                    raise RankingError(f"{candidate_id} has no row in the frozen successor target-binding registry")
                if (
                    _text(binding.get("binding_status")) != "DIRECT_PROFILE_BOUND"
                    or _text(binding.get("order_b_eligible")).casefold() != "true"
                    or row["benchmark_profile_id"] != _text(binding.get("benchmark_profile_id"))
                    or row["direct_measurement_row_hash"].casefold() != _text(binding.get("direct_measurement_row_hash")).casefold()
                    or row["successor_roster_file_sha256"].casefold() != successor_roster_file_hash
                    or row["target_binding_row_hash"].casefold() != _text(binding.get("binding_row_hash")).casefold()
                    or row["target_binding_set_hash"].casefold() != target_binding_set_hash
                    or row["order_b_eligible"].casefold() != "true"
                ):
                    raise RankingError(f"{candidate_id} is not exactly bound to a direct measured successor profile")
            else:
                raise RankingError(f"{candidate_id}.compute_binding_mode is not admissible")
            measured_profile = measurement_profiles_by_id.get(row["benchmark_profile_id"])
            if measured_profile is None:
                raise RankingError(f"{candidate_id}.benchmark_profile_id is absent from the pinned direct-profile registry")
            if row["tokenization_measurement_set_sha256"].casefold() != tokenization_measurement_set_hash:
                raise RankingError(f"{candidate_id} tokenization measurement-set hash mismatch")
            if row["measurement_profile_registry_file_sha256"].casefold() != measurement_profile_registry_file_hash:
                raise RankingError(f"{candidate_id} measurement-profile registry byte hash mismatch")
            if row["measurement_profile_set_hash"].casefold() != measurement_profile_set_hash:
                raise RankingError(f"{candidate_id} measurement-profile semantic set hash mismatch")
            if row["direct_measurement_row_hash"].casefold() != _text(measured_profile.get("direct_measurement_row_hash")).casefold():
                raise RankingError(f"{candidate_id} direct measurement-row hash mismatch")
            bound_rows = derivations_by_candidate.get(candidate_id, [])
            if len(bound_rows) != 1:
                raise RankingError(f"{candidate_id} requires exactly one canonical compute-input derivation row")
            bound = bound_rows[0]
            for field in (
                "compute_low",
                "compute_base",
                "compute_high",
                "factor_registry_version",
                "model_role",
                "evidence_status",
                "benchmark_profile_id",
                "tokenization_measurement_set_sha256",
                "measurement_profile_registry_file_sha256",
                "measurement_profile_set_hash",
                "direct_measurement_row_hash",
            ):
                source_field = {
                    "model_role": "compute_model_role",
                    "evidence_status": "compute_evidence_status",
                }.get(field, field)
                if _text(bound.get(field)) != row[source_field]:
                    raise RankingError(f"{candidate_id}.{source_field} does not match the canonical derivation")
            if row["benchmark_profile_id"] != f"flores:{_text(bound.get('flores_code'))}":
                raise RankingError(f"{candidate_id}.benchmark_profile_id does not match the canonical FLORES profile")
            if _text(bound.get("script_code")) != _text(measured_profile.get("script_code")):
                raise RankingError(f"{candidate_id} canonical script does not match the direct measured profile")
            bound_factor_rows = factor_inputs_by_candidate.get(candidate_id, [])
            if not bound_factor_rows:
                raise RankingError(f"{candidate_id} has no normalized factor-input rows")
            recomputed = {"low": Decimal(0), "base": Decimal(0), "high": Decimal(0)}
            seen_factor_ids: set[str] = set()
            for factor_row in bound_factor_rows:
                factor_id = _text(factor_row.get("factor_id"))
                factor_key = (row["factor_registry_version"], factor_id)
                if factor_key not in registry_rows or factor_id in seen_factor_ids:
                    raise RankingError(f"{candidate_id} has an unknown or duplicate normalized factor {factor_id!r}")
                seen_factor_ids.add(factor_id)
                registered = registry_rows[factor_key]
                if _text(factor_row.get("factor_registry_version")) != row["factor_registry_version"]:
                    raise RankingError(f"{candidate_id}/{factor_id} registry version mismatch")
                if _text(factor_row.get("quantity_unit")) != _text(registered.get("quantity_unit")):
                    raise RankingError(f"{candidate_id}/{factor_id} quantity unit mismatch")
                if _text(factor_row.get("estimate_status")) != "MEASURED_REPRESENTATION_WITH_DECLARED_PROCESS_SCENARIOS":
                    raise RankingError(f"{candidate_id}/{factor_id} is not a primary measured-representation scenario input")
                for scenario, quantity_field, coefficient_field in (
                    ("low", "quantity_low", "coefficient_mean"),
                    ("base", "quantity_base", "coefficient_mean"),
                    ("high", "quantity_high", "coefficient_mean"),
                ):
                    quantity = _decimal(factor_row.get(quantity_field), label=f"{candidate_id}/{factor_id}.{quantity_field}")
                    coefficient = _decimal(registered.get(coefficient_field), label=f"registry/{factor_id}.{coefficient_field}")
                    if quantity is None or quantity < 0 or coefficient is None or coefficient <= 0:
                        raise RankingError(f"{candidate_id}/{factor_id} has invalid scenario quantity or coefficient")
                    recomputed[scenario] += quantity * coefficient
            package_prefixes = STANDARD_COMPUTE_PACKAGE_PREFIXES.get(row["package_id"])
            if package_prefixes is None:
                raise RankingError(f"{candidate_id}.package_id is not in the standardized package registry")
            expected_factor_ids = {
                factor_id
                for (version, factor_id), registry_row in registry_rows.items()
                if version == row["factor_registry_version"]
                and any(_text(registry_row.get("factor_code")).startswith(prefix) for prefix in package_prefixes)
            }
            if seen_factor_ids != expected_factor_ids:
                raise RankingError(f"{candidate_id} factor ledger does not exactly match package {row['package_id']}")
            for scenario in ("low", "base", "high"):
                declared = _decimal(row[f"compute_{scenario}"], label=f"{candidate_id}.compute_{scenario}")
                if declared is None or abs(declared - recomputed[scenario]) > Decimal("0.0001"):
                    raise RankingError(f"{candidate_id}.compute_{scenario} was not recomputed from normalized factors")
        if row["source_class"] != "synthetic_fixture" and row["factor_registry_version"] not in registered_compute_versions:
            raise RankingError(
                f"{candidate_id}.factor_registry_version is absent from the closed standard-compute registry"
            )
        low = _decimal(row["compute_low"], label=f"{candidate_id}.compute_low")
        base = _decimal(row["compute_base"], label=f"{candidate_id}.compute_base")
        high = _decimal(row["compute_high"], label=f"{candidate_id}.compute_high")
        for label, value in (("low", low), ("base", base), ("high", high)):
            if value is not None and value <= 0:
                raise RankingError(f"{candidate_id}.compute_{label} must be positive")
        if low is not None and high is not None and low > high:
            raise RankingError(f"{candidate_id}: compute_low exceeds compute_high")
        if base is not None and low is not None and base < low:
            raise RankingError(f"{candidate_id}: compute_base is below compute_low")
        if base is not None and high is not None and base > high:
            raise RankingError(f"{candidate_id}: compute_base exceeds compute_high")
        result[intervention_key] = ComputeEstimate(
            candidate_id,
            intervention_key,
            row["language_target_id"],
            row["package_id"],
            row["learner_stage"],
            row["subject_domain"],
            row["delivery_format"],
            row["compute_scope"],
            row["compute_measure_class"],
            low,
            base,
            high,
            row["compute_unit"],
            row["source_id"],
            row["formula_version"],
            row["factor_registry_version"],
            row["compute_input_set_hash"],
            row["benchmark_profile_id"],
            row["direct_measurement_row_hash"],
            row["successor_roster_file_sha256"],
            row["target_binding_row_hash"],
            row["target_binding_set_hash"],
        )
    return result, ignored


def rank_efficiency(
    intrinsic_records: Sequence[Mapping[str, Any]],
    compute: Mapping[str, ComputeEstimate],
    *,
    intrinsic_draw_scores: Mapping[str, Mapping[str, Decimal]] | None = None,
    draws: Mapping[tuple[str, str, str], Decimal] | None = None,
    top_k: int = 100,
) -> list[dict[str, Any]]:
    """Rank standardized fresh gain per compute after intrinsic ranks are fixed."""
    draw_values = draws or {}
    output: list[dict[str, Any]] = []
    efficiency_draw_scores: dict[str, dict[str, Decimal]] = defaultdict(dict)
    for intrinsic in intrinsic_records:
        candidate_id = intrinsic["candidate_id"]
        intervention_key = intrinsic["intervention_key"]
        estimate = compute.get(intervention_key)
        if estimate is None:
            output.append(
                {
                    "candidate_id": candidate_id,
                    "intervention_key": intervention_key,
                    "language_target_id": intrinsic["language_target_id"],
                    "target_label": intrinsic["target_label"],
                    "measure_class": f"{intrinsic['measure_class']}::per::missing_standardized_compute",
                    "intrinsic_measure_class": intrinsic["measure_class"],
                    "intrinsic_point_score": intrinsic["point_score"],
                    "intrinsic_rank": intrinsic["intrinsic_rank"],
                    "package_id": "",
                    "learner_stage": intrinsic["learner_stage"],
                    "subject_domain": intrinsic["subject_domain"],
                    "delivery_format": "",
                    "compute_scope": "",
                    "compute_measure_class": "",
                    "compute_unit": "",
                    "compute_low": None,
                    "compute_base": None,
                    "compute_high": None,
                    "compute_source_id": "",
                    "compute_formula_version": "",
                    "factor_registry_version": "",
                    "compute_input_set_hash": "",
                    "benchmark_profile_id": "",
                    "direct_measurement_row_hash": "",
                    "successor_roster_file_sha256": "",
                    "target_binding_row_hash": "",
                    "target_binding_set_hash": "",
                    "efficiency_low": None,
                    "efficiency_base": None,
                    "efficiency_high": None,
                    "point_score": None,
                    "point_basis": "missing_standardized_compute",
                    "efficiency_status": "missing_standardized_compute",
                    "posterior_mean": None,
                    "posterior_p05": None,
                    "posterior_p50": None,
                    "posterior_p95": None,
                    "posterior_draw_count": 0,
                    "missing_compute_draw_count": 0,
                    "efficiency_rank": None,
                    "efficiency_tie_group": "",
                    "efficiency_rank_low": None,
                    "efficiency_rank_high": None,
                    "possible_rank_best": None,
                    "possible_rank_worst": None,
                    "top_k_status": "interval_unavailable",
                    "posterior_rank_population_size": 0,
                    "posterior_rank_draw_count": 0,
                    "posterior_rank_p05": None,
                    "posterior_rank_median": None,
                    "posterior_rank_p95": None,
                    "posterior_top_k_probability": None,
                }
            )
            continue
        measure_class = f"{intrinsic['measure_class']}::per::{estimate.measure_class}::{estimate.unit}"
        low = (
            intrinsic["intrinsic_low"] / estimate.high
            if intrinsic.get("intrinsic_low") is not None and estimate.high is not None
            else None
        )
        base = (
            intrinsic["point_score"] / estimate.base
            if intrinsic.get("point_score") is not None and estimate.base is not None
            else None
        )
        high = (
            intrinsic["intrinsic_high"] / estimate.low
            if intrinsic.get("intrinsic_high") is not None and estimate.low is not None
            else None
        )
        efficiency_draws: list[Decimal] = []
        efficiency_basis = "low_base_high"
        candidate_gain_draws = (intrinsic_draw_scores or {}).get(candidate_id, {})
        candidate_has_compute_draws = any(
            key[0] == candidate_id and key[2] == "compute_new" for key in draw_values
        )
        missing_compute_draw_count = 0
        for draw_key, gain in candidate_gain_draws.items():
            compute_draw = draw_values.get((candidate_id, draw_key, "compute_new"))
            if candidate_has_compute_draws and compute_draw is None:
                missing_compute_draw_count += 1
                continue
            denominator = compute_draw if candidate_has_compute_draws else estimate.base
            if denominator is not None:
                if denominator <= 0:
                    raise RankingError(f"compute_new draw must be positive: {candidate_id}/{draw_key}")
                ratio = gain / denominator
                efficiency_draws.append(ratio)
                efficiency_draw_scores[candidate_id][draw_key] = ratio
        posterior_mean = _mean(efficiency_draws)
        if candidate_has_compute_draws and missing_compute_draw_count:
            # A posterior ranking requires the complete common gain/compute grid.
            # Partial pairs remain a diagnostic only and are never a ranking key.
            base = None
            posterior_mean = None
            efficiency_draw_scores.pop(candidate_id, None)
            efficiency_basis = "incomplete_joint_gain_and_compute_draw_grid"
        elif efficiency_draws:
            base = posterior_mean
            efficiency_basis = "joint_gain_and_compute_draws" if candidate_has_compute_draws else "joint_gain_draws_over_compute_base"
        elif candidate_gain_draws and candidate_has_compute_draws:
            # A declared compute-draw model must never silently fall back to the
            # deterministic compute base when no same-draw pair is complete.
            base = None
            efficiency_basis = "joint_gain_and_compute_draws_no_complete_pairs"
        elif candidate_gain_draws and estimate.base is None:
            base = None
            efficiency_basis = "joint_gain_draws_missing_compute_base"
        output.append(
            {
                "candidate_id": candidate_id,
                "intervention_key": intervention_key,
                "language_target_id": intrinsic["language_target_id"],
                "target_label": intrinsic["target_label"],
                "measure_class": measure_class,
                "intrinsic_measure_class": intrinsic["measure_class"],
                "intrinsic_point_score": intrinsic["point_score"],
                "intrinsic_rank": intrinsic["intrinsic_rank"],
                "package_id": estimate.package_id,
                "learner_stage": estimate.learner_stage,
                "subject_domain": estimate.subject_domain,
                "delivery_format": estimate.delivery_format,
                "compute_scope": estimate.scope,
                "compute_measure_class": estimate.measure_class,
                "compute_unit": estimate.unit,
                "compute_low": estimate.low,
                "compute_base": estimate.base,
                "compute_high": estimate.high,
                "compute_source_id": estimate.source_id,
                "compute_formula_version": estimate.formula_version,
                "factor_registry_version": estimate.factor_registry_version,
                "compute_input_set_hash": estimate.compute_input_set_hash,
                "benchmark_profile_id": estimate.benchmark_profile_id,
                "direct_measurement_row_hash": estimate.direct_measurement_row_hash,
                "successor_roster_file_sha256": estimate.successor_roster_file_sha256,
                "target_binding_row_hash": estimate.target_binding_row_hash,
                "target_binding_set_hash": estimate.target_binding_set_hash,
                "efficiency_low": low,
                "efficiency_base": base,
                "efficiency_high": high,
                "point_score": base,
                "point_basis": efficiency_basis,
                "efficiency_status": "point_ranked" if base is not None else ("interval_only" if low is not None and high is not None else "missing"),
                "posterior_mean": posterior_mean,
                "posterior_p05": _quantile(efficiency_draws, Decimal("0.05")),
                "posterior_p50": _quantile(efficiency_draws, Decimal("0.50")),
                "posterior_p95": _quantile(efficiency_draws, Decimal("0.95")),
                "posterior_draw_count": len(efficiency_draws),
                "missing_compute_draw_count": missing_compute_draw_count,
                "efficiency_rank": None,
                "efficiency_tie_group": "",
                "efficiency_rank_low": None,
                "efficiency_rank_high": None,
                "possible_rank_best": None,
                "possible_rank_worst": None,
                "top_k_status": "interval_unavailable",
                "posterior_rank_population_size": 0,
                "posterior_rank_draw_count": 0,
                "posterior_rank_p05": None,
                "posterior_rank_median": None,
                "posterior_rank_p95": None,
                "posterior_top_k_probability": None,
            }
        )
    _competition_assign(output, "point_score", "efficiency")
    _partial_rank_bounds(output, low_field="efficiency_low", high_field="efficiency_high", top_k=top_k)
    _attach_posterior_rank_summaries(output, efficiency_draw_scores, top_k=top_k)
    output.sort(
        key=lambda row: (
            row["measure_class"],
            row["efficiency_rank"] if row["efficiency_rank"] is not None else 10**12,
            row["candidate_id"],
        )
    )
    return output


def factor_removal_sensitivity(
    candidates: Sequence[Mapping[str, str]],
    factors: Mapping[str, Sequence[Factor]],
    *,
    draws: Mapping[tuple[str, str, str], Decimal] | None = None,
    top_k: int = 100,
) -> list[dict[str, Any]]:
    baseline, _ = rank_intrinsic(candidates, factors, draws=draws, top_k=top_k)
    baseline_by_id = {row["candidate_id"]: row for row in baseline}
    removable = sorted({factor.name for items in factors.values() for factor in items if factor.role != "population"})
    output: list[dict[str, Any]] = []
    for factor_name in removable:
        try:
            sensitivity, _ = rank_intrinsic(
                candidates,
                factors,
                draws=draws,
                removed_factors={factor_name},
                top_k=top_k,
            )
        except RankingError:
            # Removing the only factor in a required role is not a valid model.
            continue
        for row in sensitivity:
            baseline_row = baseline_by_id[row["candidate_id"]]
            rank_change = (
                row["intrinsic_rank"] - baseline_row["intrinsic_rank"]
                if row["intrinsic_rank"] is not None and baseline_row["intrinsic_rank"] is not None
                else None
            )
            output.append(
                {
                    "removed_factor": factor_name,
                    "candidate_id": row["candidate_id"],
                    "measure_class": row["measure_class"],
                    "baseline_score": baseline_row["point_score"],
                    "sensitivity_score": row["point_score"],
                    "baseline_rank": baseline_row["intrinsic_rank"],
                    "sensitivity_rank": row["intrinsic_rank"],
                    "rank_change": rank_change,
                }
            )
    return output


def _serialize_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    return [{key: _fmt(value) for key, value in row.items()} for row in rows]


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]], fields: Sequence[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = _serialize_rows(rows)
    if fields is None:
        fields = list(serialized[0]) if serialized else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="raise", lineterminator="\n")
        writer.writeheader()
        writer.writerows(serialized)


def ranking_hash(rows: Sequence[Mapping[str, Any]], *, kind: str) -> str:
    if kind == "intrinsic":
        fields = ("candidate_id", "measure_class", "point_score", "intrinsic_rank", "intrinsic_tie_group")
    elif kind == "efficiency":
        fields = ("intervention_key", "measure_class", "point_score", "efficiency_rank", "efficiency_tie_group")
    elif kind == "language":
        fields = (
            "language_target_id",
            "measure_class",
            "point_score",
            "language_rank",
            "language_tie_group",
        )
    else:
        raise RankingError(f"unknown ranking hash kind: {kind}")
    payload = [{field: _fmt(row.get(field)) for field in fields} for row in rows]
    return sha256_bytes(canonical_json_bytes(payload))


def _path(value: str) -> Path:
    return Path(value).resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", required=True, type=_path)
    parser.add_argument("--factor-sources", required=True, type=_path)
    parser.add_argument("--country-context", required=True, type=_path)
    parser.add_argument("--compute-sources", type=_path)
    parser.add_argument("--compute-derivations", type=_path)
    parser.add_argument("--compute-inputs", type=_path)
    parser.add_argument("--compute-tokenization-measurements", type=_path)
    parser.add_argument("--compute-measurement-profiles", type=_path)
    parser.add_argument("--compute-successor-roster", type=_path)
    parser.add_argument("--compute-target-bindings", type=_path)
    parser.add_argument(
        "--compute-factor-registry",
        type=_path,
        default=DEFAULT_STANDARD_COMPUTE_REGISTRY_PATH,
    )
    parser.add_argument("--joint-draws", type=_path)
    parser.add_argument("--factor-registry", type=_path, default=DEFAULT_FACTOR_REGISTRY_PATH)
    parser.add_argument("--language-output", type=_path)
    parser.add_argument("--intrinsic-output", required=True, type=_path)
    parser.add_argument("--efficiency-output", type=_path)
    parser.add_argument("--portfolio-output", type=_path)
    parser.add_argument("--factor-removal-output", type=_path)
    parser.add_argument("--validation-output", required=True, type=_path)
    parser.add_argument("--remove-factor", action="append", default=[])
    parser.add_argument("--top-k", type=int, default=100)
    parser.add_argument("--allow-synthetic", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    raw_candidates = read_csv(args.candidates)
    raw_factors = read_csv(args.factor_sources)
    raw_context = read_csv(args.country_context)
    raw_draws = read_csv(args.joint_draws) if args.joint_draws else []
    factor_registry = load_factor_registry(args.factor_registry)
    context = load_country_context(raw_context)
    candidates, ignored_candidate = normalize_candidates(raw_candidates, context)
    factors, ignored_factor = normalize_factors(
        raw_factors,
        candidates,
        context,
        allow_synthetic=args.allow_synthetic,
        factor_registry=factor_registry,
    )
    draws, ignored_draw = normalize_draws(raw_draws, factor_registry=factor_registry)

    language_targets, language_draw_scores = rank_language_targets(
        candidates,
        factors,
        draws=draws,
        top_k=args.top_k,
    )
    if args.language_output:
        write_csv(args.language_output, language_targets)
    language_hash = ranking_hash(language_targets, kind="language")

    # Intrinsic ranking is completed before the compute table is read or joined.
    intrinsic, intrinsic_draw_scores = rank_intrinsic(
        candidates,
        factors,
        draws=draws,
        removed_factors=args.remove_factor,
        top_k=args.top_k,
    )
    write_csv(args.intrinsic_output, intrinsic)
    intrinsic_hash = ranking_hash(intrinsic, kind="intrinsic")

    portfolio: list[dict[str, Any]] = []
    if args.portfolio_output:
        portfolio = build_overlap_portfolio_units(
            intrinsic,
            draw_scores=intrinsic_draw_scores,
            top_k=args.top_k,
        )
        write_csv(args.portfolio_output, portfolio)

    factor_removal: list[dict[str, Any]] = []
    if args.factor_removal_output:
        factor_removal = factor_removal_sensitivity(candidates, factors, draws=draws, top_k=args.top_k)
        write_csv(args.factor_removal_output, factor_removal)

    efficiency: list[dict[str, Any]] = []
    ignored_compute: list[str] = []
    if args.compute_sources:
        if not args.efficiency_output:
            raise RankingError("--compute-sources requires --efficiency-output")
        if not args.allow_synthetic and (
            not args.compute_derivations
            or not args.compute_inputs
            or not args.compute_tokenization_measurements
            or not args.compute_measurement_profiles
            or not args.compute_successor_roster
            or not args.compute_target_bindings
        ):
            raise RankingError(
                "public --compute-sources requires derivations, factor inputs, pinned measurements, direct profiles, the frozen successor roster, and exhaustive target bindings"
            )
        raw_compute = read_csv(args.compute_sources)
        compute, ignored_compute = normalize_compute(
            raw_compute,
            intrinsic,
            allow_synthetic=args.allow_synthetic,
            compute_inputs_path=args.compute_derivations,
            factor_inputs_path=args.compute_inputs,
            compute_registry_path=args.compute_factor_registry,
            tokenization_measurements_path=args.compute_tokenization_measurements,
            measurement_profiles_path=args.compute_measurement_profiles,
            successor_roster_path=args.compute_successor_roster,
            target_bindings_path=args.compute_target_bindings,
        )
        efficiency = rank_efficiency(
            intrinsic,
            compute,
            intrinsic_draw_scores=intrinsic_draw_scores,
            draws=draws,
            top_k=args.top_k,
        )
        write_csv(args.efficiency_output, efficiency)
    elif args.efficiency_output:
        raise RankingError("--efficiency-output requires --compute-sources")

    outputs = {"intrinsic": {"path": str(args.intrinsic_output), "sha256": sha256_file(args.intrinsic_output)}}
    for name, path in (
        ("language_targets", args.language_output),
        ("efficiency", args.efficiency_output),
        ("portfolio", args.portfolio_output),
        ("factor_removal", args.factor_removal_output),
    ):
        if path and path.exists():
            outputs[name] = {"path": str(path), "sha256": sha256_file(path)}

    validation = {
        "schema": SCHEMA_VERSION,
        "implementation_sha256": sha256_file(Path(__file__).resolve()),
        "intrinsic_formula": "population * ordered conditional need rates * ordered conditional access-gain rates",
        "efficiency_formula": "frozen intrinsic gain / standardized from-scratch fresh-equivalent compute",
        "top_k": args.top_k,
        "intrinsic_ranking_hash": intrinsic_hash,
        "language_target_ranking_hash": language_hash,
        "efficiency_ranking_hash": ranking_hash(efficiency, kind="efficiency") if efficiency else None,
        "input_sha256": {
            "candidates": sha256_file(args.candidates),
            "factor_sources": sha256_file(args.factor_sources),
            "country_context": sha256_file(args.country_context),
            "compute_sources": sha256_file(args.compute_sources) if args.compute_sources else None,
            "compute_derivations": sha256_file(args.compute_derivations) if args.compute_derivations else None,
            "compute_inputs": sha256_file(args.compute_inputs) if args.compute_inputs else None,
            "compute_factor_registry": sha256_file(args.compute_factor_registry) if args.compute_sources else None,
            "compute_tokenization_measurements": sha256_file(args.compute_tokenization_measurements) if args.compute_tokenization_measurements else None,
            "compute_measurement_profiles": sha256_file(args.compute_measurement_profiles) if args.compute_measurement_profiles else None,
            "compute_successor_roster": sha256_file(args.compute_successor_roster) if args.compute_successor_roster else None,
            "compute_target_bindings": sha256_file(args.compute_target_bindings) if args.compute_target_bindings else None,
            "joint_draws": sha256_file(args.joint_draws) if args.joint_draws else None,
            "factor_registry": sha256_file(args.factor_registry),
        },
        "ignored_input_columns": {
            "candidates": ignored_candidate,
            "factor_sources": ignored_factor,
            "compute_sources": ignored_compute,
            "joint_draws": ignored_draw,
        },
        "removed_factors": sorted(args.remove_factor),
        "missing_base_candidates": [row["candidate_id"] for row in intrinsic if row["point_score"] is None],
        "measure_classes": sorted({row["measure_class"] for row in intrinsic}),
        "language_target_count": len(language_targets),
        "overlap_portfolio_units": len(portfolio),
        "outputs": outputs,
        "contracts": {
            "intrinsic_before_compute_join": True,
            "language_target_order_before_compute_join": True,
            "language_package_proliferation_noninterference": True,
            "factor_registry_version": factor_registry.version,
            "factor_registry_sha256": factor_registry.sha256,
            "max_union_requires_compatible_stratum_and_public_evidence": True,
            "posterior_ranks_include_deterministic_competitors": True,
            "missing_is_not_zero": True,
            "competition_ranks": True,
            "partial_identification_bounds": True,
            "forbidden_fields_projected_out_by_allowlist": True,
            "synthetic_inputs_allowed": bool(args.allow_synthetic),
        },
    }
    args.validation_output.parent.mkdir(parents=True, exist_ok=True)
    args.validation_output.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
