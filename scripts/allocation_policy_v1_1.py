"""Evidence partial order and explicitly normative educational-access dispatch.

This module reads no files.  It does not use existing positions, ranks, ORDER,
or TOP_100.  Gross source populations never become newly comfortable readers.

Public interface::

    ranked_rows, diagnostics = rank_portfolio(rows, evidence_context=None)

``rows`` are builder dictionaries with unique ``entry_id`` values. Optional
private helpers (removed from returned rows) are ``_population_observations``
(unaltered population-join/master dictionaries), ``_needs_edges`` (exact
needs/output edges), and ``_lane_mapping`` (lane plus source/basis).

Context accepts ``policy`` overrides, ``evidence`` keyed by entry_id,
``opportunity_view`` ('planning', the default, or 'measured_only'), and
``completed_package_keys``. Optional ``scenario_label`` records a caller-supplied
evidence scenario (e.g. cautious/base/favorable); it never generates values or
selects interval endpoints. Run separate calls with explicit evidence maps.
Per-entry evidence can supply population_observations,
needs_edges, lane/lane_basis, delivery_mode, and ``dimensions``. A dimension is
{low, high, basis, evidence_ids, assumption_status}; R additionally requires
measure_kind='newly_comfortable_reader_opportunity'. Ordinal intervals without
provenance are unknown, not zero. Literature-backed plausible reader ranges are
valid provisional planning inferences, not observed reader counts. Planning
admits sourced qualitative intervals; measured_only keeps those as unknown while
preserving their prior intervals and provenance. Explicit measurement-supported
intervals use assumption_status='measured_evidence'. Extra source-register and
scope metadata is preserved verbatim in dimension provenance. A is comparable
only in the same named mode.

Package identity is (needs_profile_id, named_output_profile_id, package_id,
stage_id, modality). Different explicit residuals/stages/modes are NOT collapsed.
Compute-reuse-only edges do not confer package ownership or reader benefits.
An explicit ``_work_components`` / evidence.work_components contract supersedes
that legacy HRN key: identity is (locale, package_id, stage_id, modality), with
all four fields required. ``owner_entry_id`` or context.component_owners declares
canonical ownership. Exact aliases are removed before ranking. Mixed ownership
must be residualized by the builder before ranking; the module never retains
stale whole-bundle scope or R. ``_reuse_components`` / evidence.reuse_components
requires exact existing owner claims and cannot be active work. Residual evidence
with reuse declares opportunity_component_keys equal to its active keys.

The default 6/3/1 lane allocation and scheduling of dynamically eligible actions
are declared policy, not estimated optimal weights. Static evidence fronts are
diagnostics, not barriers: an action becomes eligible as soon as none of its
dominators remain. Policy dispatch supplies a concrete next action without
claiming welfare rank or requiring exhaustion of an unrelated antichain.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable, Mapping


HIGH = "high_reach_underserved"
REGIONAL = "regional_depth"
ENDANGERED = "endangered_prestige"
LANES = (HIGH, REGIONAL, ENDANGERED)
DIMENSION_MAX = {"R": 5, "S": 4, "A": 4, "N": 4, "V": 4, "P": 4, "F": 4, "D": 4}
OPPORTUNITY_VIEWS = {"planning", "measured_only"}
PLANNING_ASSUMPTION_STATUSES = {
    "source_supported_ordinal_judgment", "prior_qualitative_judgment",
    "prior_research_judgment", "provisional_inference", "provisional_qualitative_inference",
    "literature_backed_planning_range",
}
MEASURED_ASSUMPTION_STATUSES = {"measured_evidence", "measured", "observed_measurement"}
LANE_DIMENSIONS = {
    HIGH: ("R", "S", "N", "A"),
    REGIONAL: ("S", "N", "A"),
    ENDANGERED: ("V", "P", "S", "N", "A"),
}
DEFAULT_POLICY = {
    "policy_id": "educational-access-dispatch-1.1.0",
    "lane_cycle": [HIGH, HIGH, REGIONAL, HIGH, HIGH, REGIONAL, HIGH, ENDANGERED, HIGH, REGIONAL],
    "gross_scope_thresholds_persons": [1_000_000, 10_000_000, 50_000_000],
    "potential_high_reach_threshold_persons": 10_000_000,
    "denominator_priority": [
        "mother_tongue_or_first_language", "home_or_usual_language_use",
        "functional_language_ability_or_estimate", "institutional_speaker_estimate",
        "territory_all_residents_ceiling", "other_source_defined_person_count", "unknown",
    ],
    "need_evidence_priority": {
        "stage_specific": 3, "registered_provisional": 2,
        "profile_or_residual_resolution": 1, "unresolved": 0,
    },
    "interpretation": (
        "Normative 6/3/1 exposure allocation, not an empirical optimum. Among dynamically eligible actions whose dominators no longer remain, "
        "prioritize source-backed stage-specific actions, rotate compatible typed-population views, "
        "then prefer gross scope strata and operational specificity. Unknown benefit is not zero."
    ),
}


def _strings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [part.strip() for part in value.split(";") if part.strip()]
    return [str(part).strip() for part in value if str(part).strip()]


def _number(value: Any) -> Decimal | None:
    if value is None or str(value).strip() == "":
        return None
    try:
        result = Decimal(str(value).replace(",", ""))
    except InvalidOperation:
        return None
    return result if result.is_finite() and result >= 0 else None


def _truth(value: Any) -> bool:
    return value is True or str(value).lower() in {"true", "yes", "1"}


def _policy(context: Mapping[str, Any]) -> dict[str, Any]:
    policy = copy.deepcopy(DEFAULT_POLICY)
    overrides = context.get("policy", {})
    unknown = set(overrides) - set(policy)
    if unknown:
        raise ValueError("Unknown allocation policy fields: " + ", ".join(sorted(unknown)))
    policy.update(copy.deepcopy(dict(overrides)))
    cycle = policy["lane_cycle"]
    if not isinstance(cycle, list) or not cycle or set(cycle) != set(LANES):
        raise ValueError("lane_cycle must use and retain all three declared lanes")
    thresholds = policy["gross_scope_thresholds_persons"]
    if not thresholds or any(_number(n) is None or _number(n) <= 0 for n in thresholds):
        raise ValueError("Gross scope thresholds must be positive finite numbers")
    if thresholds != sorted(set(thresholds)):
        raise ValueError("Gross scope thresholds must be strictly increasing")
    if _number(policy["potential_high_reach_threshold_persons"]) in {None, Decimal(0)}:
        raise ValueError("Potential high-reach threshold must be positive")
    if set(policy["denominator_priority"]) != set(DEFAULT_POLICY["denominator_priority"]):
        raise ValueError("denominator_priority must retain each declared class exactly once")
    if len(policy["denominator_priority"]) != len(set(policy["denominator_priority"])):
        raise ValueError("denominator_priority contains duplicate classes")
    priorities = policy["need_evidence_priority"]
    if set(priorities) != set(DEFAULT_POLICY["need_evidence_priority"]) or any(
        not isinstance(v, int) or isinstance(v, bool) for v in priorities.values()
    ):
        raise ValueError("need_evidence_priority requires the four declared integer priorities")
    return policy


def _denominator(observation: Mapping[str, Any]) -> tuple[str, str]:
    explicit = str(observation.get("denominator_class", "")).strip()
    if explicit in DEFAULT_POLICY["denominator_priority"]:
        return explicit, "verbatim source-table denominator_class"
    measure = str(observation.get("measure_type") or observation.get("source_measure_type") or
                  observation.get("population_measure") or explicit).lower()
    if any(word in measure for word in ("mother_tongue", "first_language", "same_name_mother")):
        return "mother_tongue_or_first_language", "lexical normalization of source measure: " + measure
    if any(word in measure for word in ("at_home", "home_language", "daily_language", "usual_language")):
        return "home_or_usual_language_use", "lexical normalization of source measure: " + measure
    if any(word in measure for word in ("territory", "mainland_population", "all_residents")):
        return "territory_all_residents_ceiling", "lexical normalization of source measure: " + measure
    if any(word in measure for word in ("functional", "able_to_speak", "language_ability", "language_knowledge")):
        return "functional_language_ability_or_estimate", "lexical normalization of source measure: " + measure
    if any(word in measure for word in ("speaker", "language_users")):
        return "institutional_speaker_estimate", "source speaker/user estimate; not academic comfort: " + measure
    return "other_source_defined_person_count", "unmapped source measure retained: " + measure


def _gross_observations(raw: Iterable[Mapping[str, Any]], policy: Mapping[str, Any]) -> list[dict[str, Any]]:
    results = []
    for source in raw:
        source = dict(source)
        source_id = str(source.get("source_id") or source.get("population_source_id") or "")
        observation_id = str(source.get("observation_id") or "")
        unit = str(source.get("count_unit") or source.get("population_unit") or "").lower().strip()
        denominator, denominator_rule = _denominator(source)
        values = {key: _number(source.get("population_" + key)) for key in ("low", "base", "high")}
        # A reported point remains a point; neither missing endpoint is invented.
        used_field = next((key for key in ("base", "low", "high") if values[key] is not None), "")
        value = values[used_field] if used_field else None
        superseded = _truth(source.get("source_candidate_flag_superseded"))
        eligible = bool(source_id and value is not None and unit in {"persons", "person", "people"} and not superseded)
        reason = (
            "source-backed person observation; gross scheduling context only" if eligible else
            "superseded observation" if superseded else
            "missing source provenance" if not source_id else
            "non-person or unspecified count unit" if unit not in {"persons", "person", "people"} else
            "missing nonnegative finite population observation"
        )
        learner_stratum = str(source.get("learner_stratum") or "unspecified_source_stratum")
        # Different source strata and denominator types are never count-compared.
        comparison_key = "|".join((denominator, learner_stratum, unit or "unspecified_unit"))
        band = sum(value >= Decimal(str(t)) for t in policy["gross_scope_thresholds_persons"]) if eligible else None
        results.append({
            "observation_id": observation_id, "source_id": source_id,
            "universe_profile_id": source.get("universe_profile_id", ""),
            "denominator_class": denominator, "denominator_rule": denominator_rule,
            "learner_stratum": learner_stratum, "count_unit": unit,
            "comparison_key": comparison_key,
            "reference_date_or_year": source.get("reference_date_or_year", source.get("population_reference_year", "")),
            "source_value_status": source.get("source_value_status", source.get("population_interval_status", "unspecified")),
            "source_low": str(values["low"]) if values["low"] is not None else None,
            "source_base": str(values["base"]) if values["base"] is not None else None,
            "source_high": str(values["high"]) if values["high"] is not None else None,
            "scheduling_value": str(value) if eligible else None,
            "scheduling_value_rule": "reported base, else reported lower bound, else reported upper bound; no imputation",
            "scheduling_value_field": "population_" + used_field if used_field else None,
            "scope_is_upper_bound_only": bool(used_field == "high" and values["low"] is None and values["base"] is None),
            "gross_scope_band_index": band,
            "gross_scope_band_rule": "count of policy thresholds reached by selected source value; not R or benefit",
            "eligible_for_scope_policy": eligible, "eligibility_basis": reason,
            "aggregation_rule": "never sum observations; alternatives and possible overlap retained",
        })
    return sorted(results, key=lambda r: (r["comparison_key"], r["source_id"], r["observation_id"], json.dumps(r, sort_keys=True)))


def _dimension(name: str, value: Any, opportunity_view: str) -> dict[str, Any]:
    unknown = {
        "low": 0, "high": DIMENSION_MAX[name], "status": "unknown",
        "band": name + "U", "basis": "No sourced compatible ordinal opportunity interval supplied.",
        "evidence_ids": [], "opportunity_view": opportunity_view,
        "interval_interpretation": "full possibility set; neither endpoint is an estimated benefit",
    }
    if not isinstance(value, Mapping):
        return unknown
    if value.get("status") == "unknown":
        unknown["basis"] = str(value.get("basis") or unknown["basis"])
        return unknown
    low, high = _number(value.get("low")), _number(value.get("high"))
    evidence_ids = sorted(set(_strings(value.get("evidence_ids"))))
    if low is None or high is None or not evidence_ids or not value.get("basis"):
        unknown["basis"] = "Supplied dimension lacked bounds or source provenance; retained as unknown."
        return unknown
    if low != low.to_integral_value() or high != high.to_integral_value() or low > high or high > DIMENSION_MAX[name]:
        raise ValueError("Invalid ordinal interval for " + name)
    assumption_status = str(value.get("assumption_status", "source_supported_ordinal_judgment"))
    provenance = {
        key: copy.deepcopy(item) for key, item in value.items()
        if key not in {"low", "high", "basis", "evidence_ids", "assumption_status", "measure_kind", "status"}
    }
    interval = {
        "low": int(low), "high": int(high), "basis": str(value["basis"]),
        "evidence_ids": evidence_ids, "assumption_status": assumption_status,
        "measure_kind": value.get("measure_kind"), "provenance": provenance,
    }
    if name == "R" and value.get("measure_kind") != "newly_comfortable_reader_opportunity":
        unknown["basis"] = "R requires a newly comfortable-reader planning or measurement basis; gross or unspecified measures do not qualify."
        unknown["rejected_interval"] = interval
        return unknown
    measured = assumption_status in MEASURED_ASSUMPTION_STATUSES
    provisional = assumption_status in PLANNING_ASSUMPTION_STATUSES
    if not measured:
        interval["interpretation"] = "provisional qualitative research judgment or scenario; not an observed reader count"
        unknown["prior_interval"] = interval
        unknown["assumption_status"] = assumption_status
        unknown["provenance"] = provenance
        if not provisional:
            unknown["basis"] = "Scenario, policy assumption, or unrecognized evidence status is preserved but not admitted as an opportunity inference."
            return unknown
        if opportunity_view == "measured_only":
            unknown["basis"] = "Conservative measured-only view: sourced qualitative planning interval retained as a prior, not measurement evidence."
            return unknown
    result = {
        **interval,
        "status": "measurement_supported_ordinal_interval" if measured else "provisional_planning_inference",
        "band": f"{name}{int(low)}" if low == high else f"{name}{int(low)}..{name}{int(high)}",
        "opportunity_view": opportunity_view,
        "interval_interpretation": (
            "measurement-supported ordinal classification; not a cardinal welfare score or a new exact reader count"
            if measured else "provisional literature-backed ordinal planning inference within the supplied scope; not measured readership or current package benefit"
        ),
    }
    if not measured:
        result["prior_interval"] = copy.deepcopy(interval)
    return result


def _need_evidence(row: Mapping[str, Any], policy: Mapping[str, Any]) -> dict[str, Any]:
    status = str(row.get("package_evidence_status", ""))
    package = bool(str(row.get("first_bounded_package", "")).strip())
    if package and status == "literature_backed_high_reach_need" and row.get("needs_profile_ids"):
        tier = "stage_specific"
        basis = "literature_backed_high_reach_need + registered needs_profile_ids + bounded package"
    elif package and status.startswith(("registered_curriculum_package", "source_informed_provisional_")):
        tier = "registered_provisional"
        basis = (
            "source-informed provisional package need; local supply/cohort uncertainty remains explicit; not a measured cohort"
            if status.startswith("source_informed_provisional_") else
            "registered curriculum package; exact local fit remains provisional"
        )
    elif package and ("profile_resolution" in status or "residual" in status):
        tier = "profile_or_residual_resolution"
        basis = "explicit profile/residual action; not proof of a learner deficit"
    else:
        tier = "unresolved"
        basis = "No recognized source-backed package category; value remains unknown, not zero."
    profile = str(row.get("target_profiles", "")).strip()
    unresolved = any(word in profile.lower() for word in ("unresolved", "exact profiles", "locale outputs required"))
    precision = int(bool(profile) and not unresolved)
    formats = bool(str(row.get("delivery_formats", "")).strip())
    teacher = bool(str(row.get("teacher_independent_requirements", "")).strip())
    accessible = bool(str(row.get("accessibility_requirements", "")).strip())
    delivery = int(formats) + int(teacher and accessible)
    return {
        "tier": tier, "need_evidence_priority": policy["need_evidence_priority"][tier],
        "need_evidence_rule": "declared evidence/readiness policy tier, not benefit weight", "basis": basis,
        "target_precision_priority": precision,
        "target_precision_rule": "1 for a stated surface without explicit unresolved-profile markers; operational only",
        "target_precision_basis": profile or "no target profile supplied",
        "delivery_route_priority": delivery,
        "delivery_route_rule": "one point for stated formats; one for stated independent-use AND accessibility requirements; not QA proof or benefit",
        "delivery_route_basis": {
            "delivery_formats_present": formats, "teacher_independent_requirements_present": teacher,
            "accessibility_requirements_present": accessible,
        },
        "non_overlap_rule_present": bool(str(row.get("non_overlap_rule", "")).strip()),
        "action_kind": "bounded_package_or_exact_residual" if package and precision else "bounded_profile_or_package_resolution",
    }


def _package_keys(edges: Iterable[Mapping[str, Any]]) -> list[str]:
    keys = set()
    for edge in edges:
        if edge.get("edge_role") == "cross_locale_compute_reuse_only":
            continue
        if edge.get("edge_status", "resolved") != "resolved":
            continue
        need = str(edge.get("needs_profile_id", "")).strip()
        if not need:
            continue
        for output in _strings(edge.get("named_output_profile_id")):
            key = (need, output, str(edge.get("package_id", "")), str(edge.get("stage_id", "")), str(edge.get("modality", "")))
            keys.add(json.dumps(key, ensure_ascii=False, separators=(",", ":")))
    return sorted(keys)


def work_component_key(component: Mapping[str, Any]) -> str:
    """Return a canonical exact-work key; never infer a stage from an HRN ID."""
    fields = ("locale", "package_id", "stage_id", "modality")
    values = []
    for field in fields:
        value = component.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Explicit work components require nonempty string field: " + field)
        values.append(value.strip())
    return json.dumps(("work-component-v1", *values), ensure_ascii=False, separators=(",", ":"))


def _canonical_work_contracts(rows: Mapping[str, Mapping[str, Any]], context: Mapping[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, str], list[dict[str, Any]]]:
    """Validate canonical work ownership before any opportunity comparison.

    A partial alias is a concrete scope inconsistency, not a reason to keep
    whole-bundle opportunity or to invent a reduced ordinal R. The caller must
    supply the active residual, its new visible scope and its source calibration.
    """
    contracts: dict[str, dict[str, Any]] = {}
    claims: dict[str, set[str]] = defaultdict(set)
    declared_owners: dict[str, set[str]] = defaultdict(set)
    for key, owner in context.get("component_owners", {}).items():
        if not isinstance(key, str) or not isinstance(owner, str) or not owner.strip():
            raise ValueError("component_owners requires canonical string keys and nonempty owner entry IDs")
        declared_owners[key].add(owner.strip())
    for entry_id, row in rows.items():
        evidence = context.get("evidence", {}).get(entry_id, {})
        explicit = "work_components" in evidence or "_work_components" in row
        raw_work = evidence.get("work_components", row.get("_work_components", []))
        raw_reuse = evidence.get("reuse_components", row.get("_reuse_components", []))
        if raw_reuse and not explicit:
            raise ValueError("Reuse components require an explicit active-work contract: " + entry_id)
        if not explicit:
            continue
        if not isinstance(raw_work, list) or not isinstance(raw_reuse, list):
            raise ValueError("work_components and reuse_components must be lists: " + entry_id)
        active, reuse = {}, {}
        for raw, destination, is_active in ((raw_work, active, True), (raw_reuse, reuse, False)):
            for component in raw:
                if not isinstance(component, Mapping):
                    raise ValueError("Work/reuse component must be an object: " + entry_id)
                key = work_component_key(component)
                if key in destination:
                    raise ValueError("Duplicate component key inside one row: " + entry_id + " / " + key)
                destination[key] = copy.deepcopy(dict(component))
                owner = component.get("owner_entry_id")
                if owner is not None:
                    if not isinstance(owner, str) or not owner.strip():
                        raise ValueError("owner_entry_id must be a nonempty string: " + entry_id)
                    declared_owners[key].add(owner.strip())
                if is_active:
                    claims[key].add(entry_id)
        if set(active) & set(reuse):
            raise ValueError("A reused component cannot also be active work: " + entry_id)
        contracts[entry_id] = {
            "active_components": active, "reuse_components": reuse,
            "active_component_keys": sorted(active), "reuse_component_keys": sorted(reuse),
            "identity_rule": "exact locale + package_id + stage_id + modality; no stage inferred from HRN or language alone",
            "ownership_semantics": "canonical planned commissioning ownership; not proof of already completed production",
        }
    owners = {}
    for key in sorted(set(claims) | {key for contract in contracts.values() for key in contract["reuse_components"]}):
        declarations = declared_owners[key]
        if len(declarations) > 1:
            raise ValueError("Conflicting canonical component owners: " + key)
        if declarations:
            owner = next(iter(declarations))
            basis = "explicit canonical owner declaration"
        elif len(claims[key]) == 1:
            owner = next(iter(claims[key]))
            basis = "sole active claimant; no arbitrary cross-row owner choice"
        else:
            raise ValueError("Duplicate or reused component requires an explicit canonical owner: " + key)
        if owner not in rows:
            raise ValueError("Unknown canonical component owner: " + owner + " / " + key)
        if owner not in claims[key]:
            raise ValueError("Canonical owner does not actively claim the exact component: " + owner + " / " + key)
        owners[key] = owner
        for entry_id in claims[key]:
            contracts[entry_id].setdefault("owner_selection_basis", {})[key] = basis
    suppressed = []
    for entry_id, contract in sorted(contracts.items()):
        active_keys = contract["active_component_keys"]
        unowned = [key for key in active_keys if owners[key] == entry_id]
        covered = {key: owners[key] for key in active_keys if owners[key] != entry_id}
        contract["canonical_owners"] = {key: owners[key] for key in sorted(set(active_keys) | set(contract["reuse_component_keys"]))}
        if covered and unowned:
            raise ValueError("Mixed component ownership: residualize visible scope and opportunity before ranking: " + entry_id)
        if covered or not active_keys:
            suppressed.append({
                "entry_id": entry_id,
                "reason": "all_exact_work_components_canonically_owned_elsewhere" if covered else "explicit_contract_has_no_active_work_components",
                "package_owners": covered,
            })
        for key, component in contract["reuse_components"].items():
            # A reuse reference cannot silently acquire even a sole owner: the
            # reference or explicit registry must actually name its owner.
            if not component.get("owner_entry_id") and key not in context.get("component_owners", {}):
                raise ValueError("Reuse component must explicitly name its canonical owner: " + entry_id + " / " + key)
        evidence = context.get("evidence", {}).get(entry_id, {})
        opportunity_dimensions = {
            dimension for dimension, value in evidence.get("dimensions", {}).items()
            if dimension in "RSAN" and isinstance(value, Mapping) and value.get("status") != "unknown"
            and value.get("low") is not None and value.get("high") is not None
        }
        if contract["reuse_component_keys"] and unowned and opportunity_dimensions:
            scoped = evidence.get("opportunity_component_keys")
            if not isinstance(scoped, list) or any(not isinstance(key, str) for key in scoped) or set(scoped) != set(unowned) or len(scoped) != len(set(scoped)):
                raise ValueError("Active opportunity scope not declared: opportunity_component_keys must exactly match active residual work: " + entry_id)
            contract["opportunity_scope_validation"] = "explicit active-component set matches the supplied residual opportunity calibration; reuse keys excluded"
        else:
            contract["opportunity_scope_validation"] = "no reuse-bearing quantified opportunity supplied, or no active residual"
    return contracts, dict(sorted(owners.items())), suppressed


def _package_coverage(row: Mapping[str, Any], supplied: Mapping[str, Any], keys: list[str]) -> dict[str, Any]:
    """Do not erase unkeyed bundle outputs merely because known edges repeat."""
    explicit = supplied.get("package_ownership_complete", row.get("_package_ownership_complete"))
    declared = supplied.get("actionable_output_profile_ids", row.get("_actionable_output_profile_ids"))
    basis = "explicit actionable-output registry"
    if declared is None:
        targets = _strings(row.get("target_profiles"))
        exact = targets and all(re.fullmatch(r"[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*", tag) for tag in targets)
        declared = targets if exact else None
        basis = "all target_profiles are exact tag-list entries" if exact else "target description is not an exhaustive machine-readable action/output registry"
    outputs = set(_strings(declared)) if declared is not None else None
    keyed_outputs = {json.loads(key)[1] for key in keys}
    unkeyed = sorted(outputs - keyed_outputs) if outputs is not None else None
    if explicit is False:
        complete = False
        basis = "caller explicitly marks action-key coverage incomplete"
    elif unkeyed:
        complete = False
        basis += "; some actionable outputs lack exact package keys"
    elif explicit is True:
        complete = True
        basis = "caller explicitly asserts exhaustive exact action-key registry; no known unkeyed output contradicts it"
    else:
        complete = bool(keys and outputs) if outputs is not None else None
    return {"complete": complete, "basis": basis, "unkeyed_output_profile_ids": unkeyed}


def _lane(row: Mapping[str, Any], supplied: Mapping[str, Any], observations: list[dict[str, Any]], policy: Mapping[str, Any]) -> tuple[str, str]:
    mapping = row.get("_lane_mapping", {})
    requested = supplied.get("lane") or mapping.get("lane")
    basis = supplied.get("lane_basis") or mapping.get("basis") or mapping.get("source")
    if requested:
        if requested not in LANES or not basis:
            raise ValueError("Explicit lane mappings require a declared lane and provenance: " + str(row["entry_id"]))
        return requested, "source/register mapping (not inherited rank): " + str(basis)
    if "signed_language" in str(row.get("entry_type", "")).lower() or "signed video" in str(row.get("delivery_formats", "")).lower():
        return ENDANGERED, "policy: signed-language access belongs to the independent prestige/modality lane; not an endangerment claim"
    large = any(o["eligible_for_scope_policy"] and Decimal(o["scheduling_value"]) >= Decimal(str(policy["potential_high_reach_threshold_persons"])) for o in observations)
    if large:
        return HIGH, "policy: at least one typed gross person universe meets potential-high-reach threshold; R remains separate"
    if row.get("package_evidence_status") == "literature_backed_high_reach_need" and row.get("needs_profile_ids"):
        return HIGH, "policy: registered high-reach stage-specific need; unknown demographic increment is not imputed"
    return REGIONAL, "policy: regional-depth default when no sourced lane or potential-large-universe trigger is present"


def _dominates(a: Mapping[str, Any], b: Mapping[str, Any]) -> bool:
    strict = False
    for dimension in LANE_DIMENSIONS[a["lane"]]:
        left, right = a["dimensions"][dimension], b["dimensions"][dimension]
        if dimension == "A" and (not a["delivery_mode"] or a["delivery_mode"] != b["delivery_mode"]):
            return False
        if left["low"] < right["high"]:
            return False
        strict = strict or left["low"] > right["high"]
    return strict


def _fronts(metadata: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    edges = []
    for lane in LANES:
        ids = sorted(entry_id for entry_id, m in metadata.items() if m["lane"] == lane)
        incoming = {entry_id: 0 for entry_id in ids}
        successors: dict[str, list[str]] = defaultdict(list)
        for a in ids:
            for b in ids:
                if a != b and _dominates(metadata[a], metadata[b]):
                    successors[a].append(b)
                    incoming[b] += 1
                    edges.append({"before": a, "after": b, "lane": lane, "dimensions": list(LANE_DIMENSIONS[lane]), "basis": "lower(a)>=upper(b) on all compatible dimensions, strict on at least one"})
        remaining = set(ids)
        front = 1
        while remaining:
            layer = sorted(entry_id for entry_id in remaining if incoming[entry_id] == 0)
            if not layer:
                raise ValueError("Unexpected cycle in robust evidence dominance")
            for entry_id in layer:
                metadata[entry_id]["evidence_front"] = front
                metadata[entry_id]["evidence_tie_group"] = f"{lane}:front-{front}"
                metadata[entry_id]["evidence_front_size"] = len(layer)
                remaining.remove(entry_id)
                for successor in successors[entry_id]:
                    incoming[successor] -= 1
            front += 1
    return edges


def rank_portfolio(
    rows: Iterable[Mapping[str, Any]], evidence_context: Mapping[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return a deterministic nonduplicative dispatch queue and full provenance.

    All supplied candidate rows are considered. The caller chooses the final
    publication/exposure cutoff (for example 100); this function never imports
    a previous portfolio, drops an unknown merely for being unknown, or reads
    an old position/rank/lane. Only exact package ownership suppresses entries.
    """
    context = evidence_context or {}
    opportunity_view = context.get("opportunity_view", "planning")
    if opportunity_view not in OPPORTUNITY_VIEWS:
        raise ValueError("opportunity_view must be 'planning' or 'measured_only'")
    scenario_label = context.get("scenario_label", "as_supplied")
    if not isinstance(scenario_label, str) or not scenario_label.strip():
        raise ValueError("scenario_label must be a nonempty descriptive string")
    policy = _policy(context)
    row_by_id: dict[str, dict[str, Any]] = {}
    metadata: dict[str, dict[str, Any]] = {}
    denominator_priority = {value: index for index, value in enumerate(policy["denominator_priority"])}
    for original in rows:
        row = copy.deepcopy(dict(original))
        entry_id = str(row.get("entry_id", "")).strip()
        if not entry_id or entry_id in row_by_id:
            raise ValueError("Every candidate requires a unique nonempty entry_id: " + entry_id)
        row_by_id[entry_id] = row
    work_contracts, canonical_component_owners, component_suppressions = _canonical_work_contracts(row_by_id, context)
    component_suppression_by_id = {item["entry_id"]: item for item in component_suppressions}
    for entry_id, row in sorted(row_by_id.items()):
        supplied = context.get("evidence", {}).get(entry_id, {})
        observations = _gross_observations(supplied.get("population_observations", row.get("_population_observations", [])), policy)
        eligible = [o for o in observations if o["eligible_for_scope_policy"]]
        # Prefer a declared source type; then a source stratum. Never choose
        # between incompatible types by which has the largest number.
        typed_groups = sorted({o["comparison_key"] for o in eligible}, key=lambda key: (denominator_priority[key.split("|", 1)[0]], key))
        primary_group = typed_groups[0] if typed_groups else "unknown|unknown|unknown"
        same_group = [o for o in eligible if o["comparison_key"] == primary_group]
        representative = min(same_group, key=lambda o: (-o["gross_scope_band_index"], o["source_id"], o["observation_id"], json.dumps(o, sort_keys=True))) if same_group else None
        lane, lane_basis = _lane(row, supplied, observations, policy)
        dimensions = {name: _dimension(name, supplied.get("dimensions", {}).get(name), opportunity_view) for name in DIMENSION_MAX}
        edges = supplied.get("needs_edges", row.get("_needs_edges", []))
        work_contract = work_contracts.get(entry_id)
        package_keys = work_contract["active_component_keys"] if work_contract is not None else _package_keys(edges)
        metadata[entry_id] = {
            "entry_id": entry_id, "lane": lane, "lane_basis": lane_basis,
            "opportunity_view": opportunity_view, "scenario_label": scenario_label,
            "dimensions": dimensions, "delivery_mode": str(supplied.get("delivery_mode", "")),
            "unknown_dimensions": [name for name, dim in dimensions.items() if dim["status"] == "unknown"],
            "provisional_inference_dimensions": [name for name, dim in dimensions.items() if dim["status"] == "provisional_planning_inference"],
            "operational_evidence": _need_evidence(row, policy),
            "population_observations": observations, "primary_typed_view": primary_group,
            "typed_view_selection_rule": "policy denominator order then exact source-stratum label; never cross-type numeric comparison",
            "representative_gross_observation": representative,
            "gross_scope_band_index": representative["gross_scope_band_index"] if representative else None,
            "gross_scope_selection_rule": "largest magnitude band within ONE compatible source type/stratum only; no summation; no R inference",
            "package_keys": package_keys,
            "package_key_coverage": (
                {"complete": True, "basis": "explicit validated canonical work-component contract", "unkeyed_output_profile_ids": []}
                if work_contract is not None else _package_coverage(row, supplied, package_keys)
            ),
            "package_key_rule": (
                "explicit locale + package + stage + modality work identity; coarse HRN ownership bypassed"
                if work_contract is not None else "exact need + named output + explicit package/stage/modality; compute-only edges excluded"
            ),
            "work_component_contract": work_contract,
            "benefit_estimate_status": "cardinal benefit not estimated; ordinal planning inferences are not observed counts; unknown is not zero",
        }
        if entry_id in component_suppression_by_id:
            metadata[entry_id].update({
                "disposition": component_suppression_by_id[entry_id],
                "evidence_front": None, "evidence_tie_group": None, "evidence_front_size": None,
            })
    dominance_edges = _fronts({entry_id: m for entry_id, m in metadata.items() if entry_id not in component_suppression_by_id})
    predecessors: dict[str, set[str]] = {entry_id: set() for entry_id in row_by_id}
    for edge in dominance_edges:
        predecessors[edge["after"]].add(edge["before"])
    for entry_id, m in metadata.items():
        m["dominance_predecessor_ids"] = sorted(predecessors[entry_id])
        m["evidence_front_role"] = "static DAG-layer diagnostic only; not an exhaustion or dispatch gate"
    remaining = set(row_by_id) - set(component_suppression_by_id)
    package_owners = {str(key): "already_completed" for key in context.get("completed_package_keys", [])}
    typed_dispatch_counts: dict[tuple[str, str], int] = defaultdict(int)
    ranked, trace, suppressed = [], [], copy.deepcopy(component_suppressions)
    cycle = policy["lane_cycle"]
    cursor = 0
    while remaining:
        # Suppress only rows whose EVERY exact actionable package is already
        # owned. Partial bundles survive with their uncovered actions explicit.
        for entry_id in sorted(remaining):
            keys = metadata[entry_id]["package_keys"]
            if keys and metadata[entry_id]["package_key_coverage"]["complete"] is True and all(key in package_owners for key in keys):
                owners = {key: package_owners[key] for key in keys}
                disposition = {"entry_id": entry_id, "reason": "all_exact_actionable_package_keys_already_owned", "package_owners": owners}
                suppressed.append(disposition)
                metadata[entry_id]["disposition"] = disposition
                remaining.remove(entry_id)
        if not remaining:
            break
        # The partial order constrains only actual predecessors, not unrelated
        # incomparable rows in an earlier static layer. A successor can compete
        # under policy immediately after its last remaining dominator clears.
        eligible = {entry_id for entry_id in remaining if not (predecessors[entry_id] & remaining)}
        if not eligible:
            raise ValueError("No topologically eligible action remains in the dominance DAG")
        lane = None
        for _ in range(len(cycle)):
            proposed = cycle[cursor % len(cycle)]
            cursor += 1
            if any(metadata[entry_id]["lane"] == proposed for entry_id in eligible):
                lane = proposed
                break
        if lane is None:
            raise ValueError("No dispatch lane available for remaining candidates")
        candidates = [entry_id for entry_id in eligible if metadata[entry_id]["lane"] == lane]
        eligible_in_lane = sorted(candidates)
        need_priority = max(metadata[entry_id]["operational_evidence"]["need_evidence_priority"] for entry_id in candidates)
        candidates = [entry_id for entry_id in candidates if metadata[entry_id]["operational_evidence"]["need_evidence_priority"] == need_priority]
        groups = {metadata[entry_id]["primary_typed_view"] for entry_id in candidates}
        group = min(groups, key=lambda key: (typed_dispatch_counts[(lane, key)], denominator_priority[key.split("|", 1)[0]], key))
        candidates = [entry_id for entry_id in candidates if metadata[entry_id]["primary_typed_view"] == group]

        def operational_key(entry_id: str) -> tuple[Any, ...]:
            m = metadata[entry_id]
            op = m["operational_evidence"]
            # None occurs only in the independently rotated unknown view.
            scope_key = -m["gross_scope_band_index"] if m["gross_scope_band_index"] is not None else 0
            return scope_key, -op["target_precision_priority"], -op["delivery_route_priority"], entry_id

        chosen = min(candidates, key=operational_key)
        m = metadata[chosen]
        front = m["evidence_front"]
        all_keys = m["package_keys"]
        covered = {key: package_owners[key] for key in all_keys if key in package_owners}
        unowned = [key for key in all_keys if key not in package_owners]
        ownership = (
            "registered_actions_covered_unkeyed_actions_retained" if covered and not unowned else
            "partially_covered_schedule_only_unowned_actions" if covered else
            "new_exact_package_owner" if unowned else "no_exact_package_keys_no_suppression_inferred"
        )
        reason = (
            f"Declared lane cycle {lane}; no remaining dominance predecessors in the {opportunity_view} view; "
            f"static opportunity layer {front} is diagnostic only (planning inference is not measurement); "
            f"package-evidence policy tier {m['operational_evidence']['tier']}; "
            f"least-dispatched compatible typed view {group}; within-view gross stratum, "
            "target/route specificity, then stable ID. Gross scope is not newly comfortable reach."
        )
        output = {key: copy.deepcopy(value) for key, value in row_by_id[chosen].items() if not key.startswith("_")}
        output.update({
            "exposure_position": str(len(ranked) + 1), "allocation_lane": lane,
            "ordering_basis": reason, "evidence_front": str(front),
            "evidence_tie_group": m["evidence_tie_group"], "allocation_policy_id": policy["policy_id"],
            "allocation_decision_basis": reason,
            "unknown_opportunity_dimensions": ";".join(m["unknown_dimensions"]),
            "benefit_estimate_status": m["benefit_estimate_status"],
            "package_ownership_status": ownership,
            "owned_package_keys": json.dumps(unowned, ensure_ascii=False, separators=(",", ":")),
            "covered_package_keys": json.dumps(covered, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
        })
        # Wave is a downstream presentation/cutoff decision, never an old input.
        output.pop("wave", None)
        ranked.append(output)
        selection = {
            "entry_id": chosen, "exposure_position": len(ranked), "lane": lane,
            "opportunity_view": opportunity_view, "scenario_label": scenario_label,
            "evidence_front": front, "evidence_tie_group": m["evidence_tie_group"],
            "eligible_entry_ids_in_lane_before_policy": eligible_in_lane,
            "remaining_dominance_predecessors": sorted(predecessors[chosen] & remaining),
            "cleared_dominance_predecessors": {
                predecessor: copy.deepcopy(metadata[predecessor]["disposition"])
                for predecessor in sorted(predecessors[chosen])
            },
            "need_evidence_priority": need_priority, "typed_view": group,
            "typed_view_dispatch_count_before_selection": typed_dispatch_counts[(lane, group)],
            "gross_scope_band_index": m["gross_scope_band_index"],
            "operational_key_without_final_id": list(operational_key(chosen)[:-1]),
            "final_tie_break": "canonical entry_id, only after all declared preceding criteria",
            "ordering_reason": reason, "newly_owned_package_keys": unowned,
            "previously_covered_package_keys": covered,
        }
        trace.append(selection)
        m["disposition"] = {"status": "dispatched", "position": len(ranked), "package_ownership_status": ownership}
        for key in unowned:
            package_owners[key] = chosen
        typed_dispatch_counts[(lane, group)] += 1
        remaining.remove(chosen)
    policy_json = json.dumps(policy, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    run_configuration_json = json.dumps({"policy": policy, "opportunity_view": opportunity_view, "scenario_label": scenario_label}, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    diagnostics = {
        "schema": "interlanguage/evidence-allocation-policy/1.1.0", "policy": policy,
        "opportunity_view": opportunity_view,
        "scenario_label": scenario_label,
        "scenario_generation_rule": "All intervals are caller-supplied; the label never selects endpoints, imputes a midpoint, or generates cautious/base/favorable values.",
        "opportunity_view_interpretation": (
            "Planning: provenance-backed qualitative intervals may guide provisional ordinal opportunity comparisons; they are not observed reader counts."
            if opportunity_view == "planning" else
            "Measured-only: qualitative planning intervals remain explicit priors and unknown in active comparisons; only measurement-supported intervals are active."
        ),
        "policy_sha256": hashlib.sha256(policy_json.encode("utf-8")).hexdigest(),
        "run_configuration_sha256": hashlib.sha256(run_configuration_json.encode("utf-8")).hexdigest(),
        "input_rows": len(row_by_id), "dispatched_rows": len(ranked),
        "canonical_component_owners": canonical_component_owners,
        "work_component_ownership_rule": "Canonical exact-work ownership is resolved before opportunity ranking. Entire aliases are suppressed; mixed ownership must be explicitly residualized with active-scope calibration. Reuse never adds a component or reader estimate.",
        "suppressed_entries": suppressed, "dominance_edges": dominance_edges,
        "evidence_partial_order_rule": "robust ordinal interval dominance within a lane under the declared opportunity view; planning priors are provisional inference, not measurements; unknown dimensions and incompatible modes preserve incomparability",
        "topological_eligibility_rule": "An action is eligible exactly when none of its dominance predecessors remain; selected or fully covered predecessors clear immediately. Static fronts are diagnostic only and are never exhausted as allocation barriers.",
        "static_front_is_not_dispatch_priority": True,
        "opportunity_status_counts": {
            status: sum(dim["status"] == status for m in metadata.values() for dim in m["dimensions"].values())
            for status in ("unknown", "provisional_planning_inference", "measurement_supported_ordinal_interval")
        },
        "evidence_fronts_are_not_gross_population_ranks": True,
        "gross_population_is_not_R": True, "unknown_benefit_is_not_zero": True,
        "lane_counts": {lane: sum(row["allocation_lane"] == lane for row in ranked) for lane in LANES},
        "dispatch_trace": trace, "package_owners": dict(sorted(package_owners.items())),
        "entries": {entry_id: metadata[entry_id] for entry_id in sorted(metadata)},
    }
    return ranked, diagnostics
