#!/usr/bin/env python3
"""Build population-stage-endpoint-horizon event proposals without scoring.

Version 2 treats a direct learner cohort as a valid population event even when
no whole-language speaker total exists.  It normalizes defensible counts to
persons, assigns immutable semantic identifiers, records ecological-proxy
transport assumptions, and computes only logical Frechet union/intersection
bounds for overlapping deficits.  Unknown empirical factors remain unknown.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_PATH = ROOT / "structured" / "canonical_universe_proposal.json"
COUNTRY_CONTEXT_PATH = ROOT / "structured" / "major_country_context.json"
OUTPUT_JSON = ROOT / "structured" / "empirical_event_gap_ledger_v2.json"
OUTPUT_CSV = ROOT / "structured" / "empirical_event_gap_ledger_v2.csv"

SCHEMA = "interlanguage/population-stage-endpoint-event-proposal/2.0.0"
PROPOSAL_HORIZON_MONTHS = 12

ISO2_TO_ISO3 = {
    "AF": "AFG", "AR": "ARG", "AU": "AUS", "BD": "BGD", "BR": "BRA",
    "CA": "CAN", "CD": "COD", "CN": "CHN", "CO": "COL", "DE": "DEU",
    "EG": "EGY", "ET": "ETH", "FR": "FRA", "GB": "GBR", "ID": "IDN",
    "IN": "IND", "IR": "IRN", "JP": "JPN", "KE": "KEN", "KR": "KOR",
    "MX": "MEX", "MM": "MMR", "NG": "NGA", "NP": "NPL", "PK": "PAK",
    "PH": "PHL", "RU": "RUS", "SD": "SDN", "TH": "THA", "TR": "TUR",
    "TZ": "TZA", "US": "USA", "VN": "VNM",
}

DIRECT_COHORT_CLASSES = {
    "education_status_cohort",
    "enrolment",
    "enrolment_subcohort",
    "low_literacy_cohort",
    "status_cohort",
    "workforce_cohort",
}

LANGUAGE_REACH_CLASSES = {
    "first_learned", "home_language", "home_language_nonexclusive",
    "home_or_first_language", "l1", "nonexclusive_use", "reported_ability",
    "speaker_estimate", "speaker_or_reported_ability", "usual_spoken",
}

PROXY_CLASSES = {
    "combined_territorial_exposure", "disability_population_ceiling",
    "disability_proxy", "ethnicity_or_identity_proxy", "ethnicity_proxy",
    "offline_population_estimate", "persons_basis_not_stated", "proxy",
    "territorial_exposure", "territorial_exposure_ceiling",
    "territorial_or_age_exposure_ceiling",
}

CSV_FIELDS = (
    "event_id", "language_target_id", "language_target_label",
    "package_intervention_id", "country_region_subtag", "country_iso3",
    "stage_identity_status", "stage_ids_json", "stage_scope_raw_json",
    "endpoint_id", "endpoint_operational_status", "horizon_months",
    "horizon_basis", "population_measure_id", "population_event_role",
    "population_denominator_id", "population_numerator_event_id",
    "source_population_unit", "normalization_status", "normalization_multiplier",
    "population_low_persons", "population_base_persons", "population_high_persons",
    "person_basis_status", "cohort_without_language_total_eligible",
    "education_need_status", "resource_gap_status", "academic_nonoverlap_status",
    "delivery_access_status", "ecological_proxy_transport_status",
    "ecological_proxy_assumption_ids_json", "deficit_union_low",
    "deficit_union_high", "deficit_intersection_low", "deficit_intersection_high",
    "partial_identification_status", "rankable_now", "gap_codes_json",
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode("utf-8")


def semantic_id(prefix: str, value: Any) -> str:
    return f"{prefix}:{hashlib.sha256(canonical_bytes(value)).hexdigest()[:24]}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def decimal_text(value: Any) -> str | None:
    if value is None or value == "":
        return None
    number = Decimal(str(value))
    text = format(number, "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def multiply_text(value: Any, multiplier: Decimal) -> str | None:
    if value is None or value == "":
        return None
    number = Decimal(str(value)) * multiplier
    text = format(number, "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def population_unit_normalization(unit: str, measure_class: str) -> dict[str, str | None]:
    folded = unit.strip().casefold()
    if "person_times" in folded or "person-times" in folded or folded == "fte_person_years":
        return {"status": "NONPERSON_FLOW_OR_FTE_NOT_NORMALIZED", "multiplier": None, "person_basis": "NOT_PERSON_COUNT"}
    if folded.startswith("percent") or "per_1000" in folded or folded == "households" or folded.startswith("households_"):
        return {"status": "RATE_OR_HOUSEHOLD_MEASURE_NOT_NORMALIZED", "multiplier": None, "person_basis": "NOT_PERSON_COUNT"}
    if folded.startswith("million "):
        return {"status": "NORMALIZED_EXACT_DECIMAL_MULTIPLIER", "multiplier": "1000000", "person_basis": "PUBLISHED_PERSON_COUNT_ROUNDED_IN_MILLIONS"}
    if folded.startswith("persons") or folded in {"people", "persons age 5+", "reported people affected or displaced"}:
        return {"status": "NORMALIZED_IDENTITY_MULTIPLIER", "multiplier": "1", "person_basis": "PUBLISHED_PERSON_COUNT"}
    if folded.startswith("learners_"):
        return {"status": "NORMALIZED_LEARNER_COUNT_IDENTITY_MULTIPLIER", "multiplier": "1", "person_basis": "LEARNER_PERSON_STOCK"}
    if "enrolment" in folded or "learner records" in folded or "represented in-school" in folded:
        return {"status": "PROVISIONAL_ENROLMENT_STOCK_TO_PERSONS", "multiplier": "1", "person_basis": "UNIQUENESS_REQUIRES_DUPLICATION_AUDIT"}
    if measure_class in DIRECT_COHORT_CLASSES and folded == "people":
        return {"status": "NORMALIZED_IDENTITY_MULTIPLIER", "multiplier": "1", "person_basis": "PUBLISHED_PERSON_COUNT"}
    return {"status": "UNRESOLVED_UNIT_TO_PERSONS", "multiplier": None, "person_basis": "UNKNOWN"}


def region_subtag(tags: Sequence[str]) -> tuple[str | None, str | None]:
    regions = {
        part
        for tag in tags
        for part in str(tag).split(":", 1)[0].split("-")[1:]
        if re.fullmatch(r"[A-Z]{2}|[0-9]{3}", part)
    }
    if len(regions) != 1:
        return None, None
    region = next(iter(regions))
    return region, ISO2_TO_ISO3.get(region, region if len(region) == 3 else None)


def stage_ids(definition: str, raw_scopes: Sequence[str]) -> list[str]:
    """Return only stage identities explicit in the population definition.

    Package-scope prose is retained separately and never used to manufacture a
    stage-specific denominator.
    """
    text = definition.casefold()
    if text.startswith("derived lower-secondary"):
        return ["ISCED2"]
    found: set[str] = set()
    patterns = (
        ("ISCED0", r"\b(preschool|pre-school|early childhood)\b"),
        ("ISCED1", r"\b(primary|elementary)\b"),
        ("ISCED2", r"\b(lower[- ]secondary|junior[- ]secondary|junior high|compulsory-age)\b"),
        ("ISCED3", r"\b(upper[- ]secondary|senior[- ]secondary|high school|secondary-vocational|smk)\b"),
        ("ISCED5", r"\b(associate|higher-vocational|professional training college)\b"),
        ("ISCED6", r"\b(undergraduate|bachelor)\b"),
        ("ISCED7", r"\b(master|professional-degree)\b"),
        ("ISCED8", r"\bdoctoral\b"),
    )
    for identifier, pattern in patterns:
        if re.search(pattern, text):
            found.add(identifier)
    # "graduate students" without an explicit component is a compound 7/8 stock.
    if "graduate students" in text and not ({"ISCED7", "ISCED8"} & found):
        found.update({"ISCED7", "ISCED8"})
    return sorted(found)


def direct_need_count(definition: str) -> bool:
    text = definition.casefold()
    markers = (
        "needing japanese instruction", "not enrolled", "nonattendance",
        "absent 30 or more days", "not employed, enrolled", "lacking basic literacy",
    )
    return any(marker in text for marker in markers)


def frechet_bounds(intervals: Sequence[tuple[Decimal, Decimal]]) -> dict[str, str | None]:
    """Return sharp logical bounds absent dependence assumptions.

    For no events, all outputs are missing.  For one or more events, union and
    intersection bounds use only marginal intervals and no independence claim.
    """
    if not intervals:
        return {"union_low": None, "union_high": None, "intersection_low": None, "intersection_high": None}
    for low, high in intervals:
        if low < 0 or high > 1 or low > high:
            raise ValueError(f"invalid probability interval: {(low, high)}")
    count = Decimal(len(intervals))
    lows = [low for low, _ in intervals]
    highs = [high for _, high in intervals]
    union_low = max(max(lows), sum(lows, Decimal(0)) - (count - 1))
    union_high = min(Decimal(1), sum(highs, Decimal(0)))
    intersection_low = max(Decimal(0), sum(lows, Decimal(0)) - (count - 1))
    intersection_high = min(highs)
    return {
        "union_low": decimal_text(union_low),
        "union_high": decimal_text(union_high),
        "intersection_low": decimal_text(intersection_low),
        "intersection_high": decimal_text(intersection_high),
    }


def population_role(measure: Mapping[str, Any]) -> str:
    measure_class = str(measure.get("measure_class", ""))
    definition = str(measure.get("population_definition", ""))
    if direct_need_count(definition):
        return "DIRECT_NEED_NUMERATOR_COHORT"
    if measure_class in DIRECT_COHORT_CLASSES:
        return "DIRECT_LEARNER_OR_APPLIED_COHORT"
    if measure_class in LANGUAGE_REACH_CLASSES:
        return "LANGUAGE_REACH_CEILING"
    if measure_class in PROXY_CLASSES or measure.get("shared_denominator_group"):
        return "PROXY_CONTEXT_OR_SHARED_DENOMINATOR"
    return "OTHER_TYPED_POPULATION_MEASURE"


def proxy_metrics_for_stage(stage_values: Sequence[str]) -> list[str]:
    metrics: set[str] = set()
    for stage in stage_values:
        if stage in {"ISCED1", "ISCED2"}:
            metrics.update({"learning_poverty_pct", "learning_deprivation_pct", "primary_out_of_school_pct"})
        elif stage == "ISCED3":
            metrics.update({"lower_secondary_out_of_school_pct", "upper_secondary_out_of_school_pct"})
    return sorted(metrics)


def context_lookup(document: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {str(row["country_code"]): row for row in document.get("countries", [])}


def build(canonical_path: Path, country_context_path: Path) -> dict[str, Any]:
    canonical = load_json(canonical_path)
    context_document = load_json(country_context_path)
    contexts = context_lookup(context_document)
    targets = {row["language_target_id"]: row for row in canonical["language_targets"]}
    measures = {row["population_measure_id"]: row for row in canonical["population_measures"]}

    rows: list[dict[str, Any]] = []
    for package in sorted(canonical["package_interventions"], key=lambda row: row["package_intervention_id"]):
        measure_ids = package.get("population_measure_ids") or [None]
        for language_target_id in sorted(package["language_target_ids"]):
            target = targets[language_target_id]
            region, iso3 = region_subtag(target.get("language_tags", []))
            for measure_id in measure_ids:
                measure = measures.get(measure_id) if measure_id else None
                definition = str(measure.get("population_definition", "")) if measure else ""
                raw_scopes = sorted(str(value) for value in package.get("learner_stage_scopes", []))
                stages = stage_ids(definition, raw_scopes)
                stage_status = (
                    "EXACT_SINGLE_STAGE_FROM_POPULATION_DEFINITION" if len(stages) == 1
                    else "EXPLICIT_COMPOUND_STAGE_FROM_POPULATION_DEFINITION" if len(stages) > 1
                    else "MISSING_STAGE_SPECIFIC_POPULATION_IDENTITY"
                )

                endpoint_identity = {
                    "language_target_id": language_target_id,
                    "package_intervention_id": package["package_intervention_id"],
                    "target_labels": package.get("target_labels", []),
                    "modalities": package.get("modalities", []),
                    "stage_ids": stages,
                    "horizon_months": PROPOSAL_HORIZON_MONTHS,
                    "endpoint_type": "functional_use_of_fixed_package",
                }
                endpoint_id = semantic_id("endpoint", endpoint_identity)
                denominator_identity = None
                normalization = {"status": "MISSING_POPULATION_MEASURE", "multiplier": None, "person_basis": "UNKNOWN"}
                normalized = {"low": None, "base": None, "high": None}
                role = "MISSING_POPULATION_MEASURE"
                denominator_id = None
                numerator_id = None
                if measure:
                    normalization = population_unit_normalization(str(measure["population_unit"]), str(measure["measure_class"]))
                    multiplier = Decimal(normalization["multiplier"]) if normalization["multiplier"] else None
                    if multiplier is not None:
                        normalized = {
                            "low": multiply_text(measure.get("population_low"), multiplier),
                            "base": multiply_text(measure.get("population_base"), multiplier),
                            "high": multiply_text(measure.get("population_high"), multiplier),
                        }
                    denominator_identity = {
                        "population_measure_id": measure_id,
                        "measure_class": measure["measure_class"],
                        "definition": measure["population_definition"],
                        "reference_year": measure["population_reference_year"],
                        "source_id": measure["population_source_id"],
                        "source_url": measure["population_source_url"],
                        "source_unit": measure["population_unit"],
                        "normalization_multiplier": normalization["multiplier"],
                    }
                    denominator_id = semantic_id("denominator", denominator_identity)
                    numerator_id = semantic_id("population-event", {
                        "denominator_id": denominator_id,
                        "values_persons": normalized,
                    })
                    role = population_role(measure)

                event_identity = {
                    "language_target_id": language_target_id,
                    "package_intervention_id": package["package_intervention_id"],
                    "population_denominator_id": denominator_id,
                    "stage_ids": stages,
                    "endpoint_id": endpoint_id,
                    "horizon_months": PROPOSAL_HORIZON_MONTHS,
                }
                event_id = semantic_id("beneficiary-event", event_identity)

                proxy_assumptions: list[dict[str, Any]] = []
                context = contexts.get(iso3 or "")
                for metric_id in proxy_metrics_for_stage(stages):
                    metric = context.get("metrics", {}).get(metric_id) if context else None
                    if not metric or metric.get("missing"):
                        continue
                    assumption = {
                        "transport_assumption_id": semantic_id("transport", {
                            "event_id": event_id,
                            "country_code": iso3,
                            "metric_id": metric_id,
                            "reference_year": metric.get("reference_year"),
                        }),
                        "proxy_country_code": iso3,
                        "proxy_metric_id": metric_id,
                        "proxy_reported_value": decimal_text(metric.get("value")),
                        "proxy_reported_unit": metric.get("unit"),
                        "proxy_reference_year": decimal_text(metric.get("reference_year")),
                        "target_denominator_stratum_id": denominator_id,
                        "transport_assumption": "target-stratum conditional rate equals the national rate",
                        "transport_status": "UNTRANSPORTED_ECOLOGICAL_PROXY_NO_STRATUM_EQUIVALENCE_EVIDENCE",
                        "factor_low": None,
                        "factor_base": None,
                        "factor_high": None,
                        "logical_probability_low": "0",
                        "logical_probability_high": "1",
                    }
                    proxy_assumptions.append(assumption)

                is_direct_need = role == "DIRECT_NEED_NUMERATOR_COHORT"
                deficit_events = []
                factor_definitions = (
                    ("education_need", "learner satisfies the fixed educational-need event"),
                    ("resource_gap", "learner lacks a functionally adequate resource on the fixed route"),
                    ("academic_nonoverlap", "learner cannot independently use an existing academic lingua-franca route"),
                    ("delivery_access_gap", "learner cannot reach or use the candidate delivery route"),
                )
                for factor_name, factor_definition in factor_definitions:
                    constitutive = factor_name == "education_need" and is_direct_need
                    low = high = "1" if constitutive else None
                    deficit_events.append({
                        "factor_name": factor_name,
                        "event_id": semantic_id("deficit-event", {
                            "beneficiary_event_id": event_id,
                            "factor_name": factor_name,
                            "definition": factor_definition,
                        }),
                        "event_definition": factor_definition,
                        "numerator_event_id": numerator_id if constitutive else None,
                        "denominator_stratum_id": denominator_id,
                        "condition_on_event_id": numerator_id,
                        "conditioning_set_id": semantic_id("conditioning-set", {
                            "population_event_id": numerator_id,
                            "prior_events": [],
                        }),
                        "evidence_status": "CONSTITUTIVE_DIRECT_COUNT" if constitutive else "MISSING_PUBLIC_CONDITIONAL_EVENT_EVIDENCE",
                        "low": low,
                        "base": low,
                        "high": high,
                        "logical_probability_low": low or "0",
                        "logical_probability_high": high or "1",
                    })

                logical_intervals = [
                    (Decimal(item["logical_probability_low"]), Decimal(item["logical_probability_high"]))
                    for item in deficit_events
                ]
                bounds = frechet_bounds(logical_intervals)
                normalized_available = any(value is not None for value in normalized.values())
                exact_cohort = role in {"DIRECT_NEED_NUMERATOR_COHORT", "DIRECT_LEARNER_OR_APPLIED_COHORT"}
                cohort_without_total = bool(exact_cohort and normalized_available and stages)
                gaps = []
                if not measure:
                    gaps.append("population_measure")
                if normalization["multiplier"] is None:
                    gaps.append("person_unit_normalization")
                if len(stages) != 1:
                    gaps.append("single_exact_stage_identity")
                gaps.extend([
                    "endpoint_operational_threshold",
                    "resource_gap_conditional_event",
                    "academic_nonoverlap_conditional_event",
                    "delivery_access_conditional_event",
                    "empirical_deficit_dependence",
                ])
                if not is_direct_need:
                    gaps.append("education_need_conditional_event")
                if proxy_assumptions:
                    gaps.append("ecological_proxy_transport_evidence")

                rows.append({
                    "event_id": event_id,
                    "language_target_id": language_target_id,
                    "language_target_label": " / ".join(target.get("language_variety_names", [])),
                    "language_tags": target.get("language_tags", []),
                    "package_intervention_id": package["package_intervention_id"],
                    "package_target_labels": package.get("target_labels", []),
                    "delivery_modalities": package.get("modalities", []),
                    "country_region_subtag": region,
                    "country_iso3": iso3,
                    "stage_identity_status": stage_status,
                    "stage_ids": stages,
                    "stage_scope_raw": raw_scopes,
                    "endpoint_id": endpoint_id,
                    "endpoint_definition": endpoint_identity,
                    "endpoint_operational_status": "PROPOSED_FIXED_PACKAGE_ENDPOINT_THRESHOLD_NOT_YET_EVIDENCE_BOUND",
                    "horizon_months": PROPOSAL_HORIZON_MONTHS,
                    "horizon_basis": "COMMON_ANALYSIS_POLICY_PROPOSAL_NOT_SOURCE_REPORTED",
                    "population_measure_id": measure_id,
                    "population_event_role": role,
                    "population_denominator_id": denominator_id,
                    "population_denominator_identity": denominator_identity,
                    "population_numerator_event_id": numerator_id,
                    "source_population_unit": measure.get("population_unit") if measure else None,
                    "source_population_values": {
                        "low": measure.get("population_low") if measure else None,
                        "base": measure.get("population_base") if measure else None,
                        "high": measure.get("population_high") if measure else None,
                    },
                    "normalization_status": normalization["status"],
                    "normalization_multiplier": normalization["multiplier"],
                    "population_values_persons": normalized,
                    "person_basis_status": normalization["person_basis"],
                    "aggregation_policy": measure.get("aggregation_policy") if measure else "no_population_measure",
                    "shared_denominator_group": measure.get("shared_denominator_group") if measure else None,
                    "cohort_without_language_total_eligible": cohort_without_total,
                    "deficit_events": deficit_events,
                    "ecological_proxy_transport_status": (
                        "UNTRANSPORTED_PROXY_LOCATORS_PRESENT" if proxy_assumptions
                        else "NO_STAGE_COMPATIBLE_COUNTRY_PROXY_LOCATOR"
                    ),
                    "ecological_proxy_assumptions": proxy_assumptions,
                    "deficit_union_bounds": {"low": bounds["union_low"], "high": bounds["union_high"]},
                    "deficit_intersection_bounds": {"low": bounds["intersection_low"], "high": bounds["intersection_high"]},
                    "partial_identification_status": "LOGICAL_FRECHET_BOUNDS_ONLY_NO_DEPENDENCE_ASSUMPTION",
                    "rankable_now": False,
                    "gap_codes": sorted(set(gaps)),
                })

    represented_targets = {row["language_target_id"] for row in rows}
    # A target may currently exist only as an access overlay or an identity
    # hypothesis.  It still receives the identical event schema rather than
    # disappearing because no package row has yet been proposed.
    for language_target_id in sorted(set(targets) - represented_targets):
        target = targets[language_target_id]
        region, iso3 = region_subtag(target.get("language_tags", []))
        endpoint_identity = {
            "language_target_id": language_target_id,
            "package_intervention_id": None,
            "target_labels": [],
            "modalities": [],
            "stage_ids": [],
            "horizon_months": PROPOSAL_HORIZON_MONTHS,
            "endpoint_type": "functional_use_of_fixed_package",
        }
        endpoint_id = semantic_id("endpoint", endpoint_identity)
        event_id = semantic_id("beneficiary-event", {
            "language_target_id": language_target_id,
            "package_intervention_id": None,
            "population_denominator_id": None,
            "stage_ids": [],
            "endpoint_id": endpoint_id,
            "horizon_months": PROPOSAL_HORIZON_MONTHS,
        })
        deficit_events = []
        for factor_name, factor_definition in (
            ("education_need", "learner satisfies the fixed educational-need event"),
            ("resource_gap", "learner lacks a functionally adequate resource on the fixed route"),
            ("academic_nonoverlap", "learner cannot independently use an existing academic lingua-franca route"),
            ("delivery_access_gap", "learner cannot reach or use the candidate delivery route"),
        ):
            deficit_events.append({
                "factor_name": factor_name,
                "event_id": semantic_id("deficit-event", {
                    "beneficiary_event_id": event_id,
                    "factor_name": factor_name,
                    "definition": factor_definition,
                }),
                "event_definition": factor_definition,
                "numerator_event_id": None,
                "denominator_stratum_id": None,
                "condition_on_event_id": None,
                "conditioning_set_id": semantic_id("conditioning-set", {
                    "population_event_id": None,
                    "prior_events": [],
                }),
                "evidence_status": "MISSING_PUBLIC_CONDITIONAL_EVENT_EVIDENCE",
                "low": None,
                "base": None,
                "high": None,
                "logical_probability_low": "0",
                "logical_probability_high": "1",
            })
        bounds = frechet_bounds([(Decimal(0), Decimal(1)) for _ in deficit_events])
        rows.append({
            "event_id": event_id,
            "language_target_id": language_target_id,
            "language_target_label": " / ".join(target.get("language_variety_names", [])),
            "language_tags": target.get("language_tags", []),
            "package_intervention_id": None,
            "package_target_labels": [],
            "delivery_modalities": [],
            "country_region_subtag": region,
            "country_iso3": iso3,
            "stage_identity_status": "MISSING_STAGE_SPECIFIC_POPULATION_IDENTITY",
            "stage_ids": [],
            "stage_scope_raw": [],
            "endpoint_id": endpoint_id,
            "endpoint_definition": endpoint_identity,
            "endpoint_operational_status": "PACKAGE_AND_ENDPOINT_THRESHOLD_NOT_YET_DEFINED",
            "horizon_months": PROPOSAL_HORIZON_MONTHS,
            "horizon_basis": "COMMON_ANALYSIS_POLICY_PROPOSAL_NOT_SOURCE_REPORTED",
            "population_measure_id": None,
            "population_event_role": "MISSING_POPULATION_MEASURE",
            "population_denominator_id": None,
            "population_denominator_identity": None,
            "population_numerator_event_id": None,
            "source_population_unit": None,
            "source_population_values": {"low": None, "base": None, "high": None},
            "normalization_status": "MISSING_POPULATION_MEASURE",
            "normalization_multiplier": None,
            "population_values_persons": {"low": None, "base": None, "high": None},
            "person_basis_status": "UNKNOWN",
            "aggregation_policy": "no_population_measure",
            "shared_denominator_group": None,
            "cohort_without_language_total_eligible": False,
            "deficit_events": deficit_events,
            "ecological_proxy_transport_status": "NO_STAGE_COMPATIBLE_COUNTRY_PROXY_LOCATOR",
            "ecological_proxy_assumptions": [],
            "deficit_union_bounds": {"low": bounds["union_low"], "high": bounds["union_high"]},
            "deficit_intersection_bounds": {"low": bounds["intersection_low"], "high": bounds["intersection_high"]},
            "partial_identification_status": "LOGICAL_FRECHET_BOUNDS_ONLY_NO_DEPENDENCE_ASSUMPTION",
            "rankable_now": False,
            "gap_codes": [
                "academic_nonoverlap_conditional_event", "delivery_access_conditional_event",
                "education_need_conditional_event", "empirical_deficit_dependence",
                "endpoint_operational_threshold", "package_intervention", "person_unit_normalization",
                "population_measure", "resource_gap_conditional_event", "single_exact_stage_identity",
            ],
        })

    rows.sort(key=lambda row: (row["language_target_id"], row["package_intervention_id"] or "", row["population_measure_id"] or ""))
    represented_targets = {row["language_target_id"] for row in rows}
    if represented_targets != set(targets):
        raise ValueError("event proposal did not retain the complete canonical target universe")
    if any(row["rankable_now"] for row in rows):
        raise ValueError("event proposal must not emit ranks")

    counts = {
        "canonical_language_targets": len(targets),
        "represented_language_targets": len(represented_targets),
        "event_proposal_rows": len(rows),
        "rows_with_population_measure": sum(row["population_measure_id"] is not None for row in rows),
        "rows_normalized_to_persons": sum(row["normalization_multiplier"] is not None for row in rows),
        "rows_with_single_exact_stage": sum(len(row["stage_ids"]) == 1 for row in rows),
        "direct_cohort_rows_not_requiring_language_total": sum(row["cohort_without_language_total_eligible"] for row in rows),
        "language_targets_with_direct_cohort_route": len({
            row["language_target_id"] for row in rows if row["cohort_without_language_total_eligible"]
        }),
        "rows_with_untransported_ecological_proxy": sum(bool(row["ecological_proxy_assumptions"]) for row in rows),
        "rankings_produced": 0,
    }
    document = {
        "schema": SCHEMA,
        "artifact_status": "event_and_gap_proposal_not_scores_or_ranks",
        "input_manifest": {
            "canonical_universe": {"file": canonical_path.name, "bytes": canonical_path.stat().st_size, "sha256": sha256_file(canonical_path)},
            "country_context": {"file": country_context_path.name, "bytes": country_context_path.stat().st_size, "sha256": sha256_file(country_context_path)},
        },
        "uniform_contract": {
            "population_unit": "persons only after explicit unit transport; original units and precision retained",
            "beneficiary_unit": "exact learner-stage-package access event, not automatically a unique person across events",
            "whole_language_population_required": False,
            "immutable_ids": ["event_id", "endpoint_id", "population_denominator_id", "population_numerator_event_id", "deficit_events[].event_id", "deficit_events[].conditioning_set_id", "ecological_proxy_assumptions[].transport_assumption_id"],
            "ecological_proxy_rule": "national rates remain null factor values with logical [0,1] bounds until target-stratum transportability is evidenced",
            "overlap_rule": "publish both Frechet union and intersection bounds; never multiply overlapping marginal deficits as conditionals",
            "missingness_rule": "missing empirical evidence remains null and cannot become zero, a midpoint, a penalty, or a negative control",
            "horizon_rule": f"{PROPOSAL_HORIZON_MONTHS} months is a common proposal parameter, not a source-reported empirical value",
        },
        "counts": counts,
        "direct_cohort_language_target_ids": sorted({
            row["language_target_id"] for row in rows if row["cohort_without_language_total_eligible"]
        }),
        "events": rows,
    }
    document["payload_sha256"] = hashlib.sha256(canonical_bytes(rows)).hexdigest().upper()
    return document


def csv_row(row: Mapping[str, Any]) -> dict[str, Any]:
    deficits = {item["factor_name"]: item for item in row["deficit_events"]}
    return {
        "event_id": row["event_id"],
        "language_target_id": row["language_target_id"],
        "language_target_label": row["language_target_label"],
        "package_intervention_id": row["package_intervention_id"],
        "country_region_subtag": row["country_region_subtag"] or "",
        "country_iso3": row["country_iso3"] or "",
        "stage_identity_status": row["stage_identity_status"],
        "stage_ids_json": json.dumps(row["stage_ids"], separators=(",", ":")),
        "stage_scope_raw_json": json.dumps(row["stage_scope_raw"], ensure_ascii=False, separators=(",", ":")),
        "endpoint_id": row["endpoint_id"],
        "endpoint_operational_status": row["endpoint_operational_status"],
        "horizon_months": row["horizon_months"],
        "horizon_basis": row["horizon_basis"],
        "population_measure_id": row["population_measure_id"] or "",
        "population_event_role": row["population_event_role"],
        "population_denominator_id": row["population_denominator_id"] or "",
        "population_numerator_event_id": row["population_numerator_event_id"] or "",
        "source_population_unit": row["source_population_unit"] or "",
        "normalization_status": row["normalization_status"],
        "normalization_multiplier": row["normalization_multiplier"] or "",
        "population_low_persons": row["population_values_persons"]["low"] or "",
        "population_base_persons": row["population_values_persons"]["base"] or "",
        "population_high_persons": row["population_values_persons"]["high"] or "",
        "person_basis_status": row["person_basis_status"],
        "cohort_without_language_total_eligible": str(row["cohort_without_language_total_eligible"]).lower(),
        "education_need_status": deficits["education_need"]["evidence_status"],
        "resource_gap_status": deficits["resource_gap"]["evidence_status"],
        "academic_nonoverlap_status": deficits["academic_nonoverlap"]["evidence_status"],
        "delivery_access_status": deficits["delivery_access_gap"]["evidence_status"],
        "ecological_proxy_transport_status": row["ecological_proxy_transport_status"],
        "ecological_proxy_assumption_ids_json": json.dumps([item["transport_assumption_id"] for item in row["ecological_proxy_assumptions"]], separators=(",", ":")),
        "deficit_union_low": row["deficit_union_bounds"]["low"],
        "deficit_union_high": row["deficit_union_bounds"]["high"],
        "deficit_intersection_low": row["deficit_intersection_bounds"]["low"],
        "deficit_intersection_high": row["deficit_intersection_bounds"]["high"],
        "partial_identification_status": row["partial_identification_status"],
        "rankable_now": "false",
        "gap_codes_json": json.dumps(row["gap_codes"], separators=(",", ":")),
    }


def write_outputs(document: Mapping[str, Any], json_path: Path, csv_path: Path) -> None:
    json_path.write_bytes(json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(CSV_FIELDS), lineterminator="\n")
        writer.writeheader()
        writer.writerows(csv_row(row) for row in document["events"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical", type=Path, default=CANONICAL_PATH)
    parser.add_argument("--country-context", type=Path, default=COUNTRY_CONTEXT_PATH)
    parser.add_argument("--json-output", type=Path, default=OUTPUT_JSON)
    parser.add_argument("--csv-output", type=Path, default=OUTPUT_CSV)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    document = build(args.canonical, args.country_context)
    write_outputs(document, args.json_output, args.csv_output)
    print(json.dumps({"status": "PASS", "counts": document["counts"], "json": str(args.json_output), "csv": str(args.csv_output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
