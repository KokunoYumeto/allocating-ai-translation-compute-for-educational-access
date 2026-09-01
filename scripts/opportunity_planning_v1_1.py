"""Scope-aware assembly of explicitly provisional opportunity judgments.

No population is converted into readership here. Recovered OpenLogic judgments
can inform the FR-2 formal-reasoning scope only; new package-specific research
overrides them. Scenario endpoints are supplied judgments, not confidence
intervals, observed benefits, or automatically selected midpoints.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path


DIMENSIONS = "RSANVPFD"


def file_identity(path: Path) -> dict:
    return {"filename": path.name, "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper()}


def parse_band(value: str, dimension: str) -> tuple[int, int] | None:
    match = re.fullmatch(re.escape(dimension) + r"([0-5])(?:-([0-5]))?", value.strip())
    if not match:
        return None
    low, high = int(match[1]), int(match[2] or match[1])
    if low > high or (dimension != "R" and high > 4):
        raise ValueError(f"Invalid {dimension} band: {value}")
    return low, high


def exact_prior_for_row(row: dict, recovered: list[dict], source_identity: dict) -> dict:
    """Retain only scope-compatible prior judgments, never a prior rank."""
    tags = {part.strip() for field in ("target_profiles", "named_output_profile_ids")
            for part in row.get(field, "").split(";") if part.strip()}
    matches = [item for item in recovered if item.get("tag") in tags]
    if len(matches) != 1:
        return {}
    prior = matches[0]
    first_package = row.get("first_bounded_package", "")
    same_domain = "registered FR-2 Formal-reasoning core" in first_package
    resolved = "resolution" not in row.get("education_stages", "").lower()
    # Demographic/supply/overlap priors for an advanced reading cohort must
    # never become claimed audiences for a new ECE, TVET, or small residual.
    allowed = DIMENSIONS if same_domain and resolved else "VPFD"
    supplied = {}
    evidence_ids = [x for x in prior.get("evidence_ids", "").split(";") if x]
    if not evidence_ids:
        return {}
    for dimension in allowed:
        interval = parse_band(prior.get(dimension, ""), dimension)
        if interval is None:
            continue
        low, high = interval
        supplied[dimension] = {
            "low": low, "high": high,
            "basis": (
                f"Retained provisional {dimension} judgment for exact profile {prior['tag']} "
                f"from {prior['profile_id']}. "
                + ("The current FR-2 package is in the same formal-reasoning/advanced-reading domain. "
                   "The prior concerns plausible access, not observed uptake or completed learning. "
                   if same_domain and resolved else
                   "Only a profile-level modifier is carried across the changed package scope; "
                   "no reader, scarcity, accessibility or overlap band is transferred. ")
                + prior.get("decision_caveat", "")
            ),
            "evidence_ids": evidence_ids,
            "assumption_status": "prior_research_judgment",
            "source_register": "marginal_intelligibility_reach_20260816/GLOBAL_GAP_REGISTER.csv",
            "source_register_identity": source_identity,
            "source_profile_id": prior["profile_id"],
            "planning_scope": "FR-2 formal-reasoning curriculum opportunity" if same_domain and resolved else "exact-profile modifier only",
            "reader_cohort": prior.get("likely_reader_cohort", ""),
            "source_confidence": prior.get("confidence", ""),
            "package_scope_caveat": (
                "Prior judgment retained for the same educational domain, not a newly calibrated "
                "estimate of FR-2 downloads, beneficiaries, or learning gains. Narrower package "
                "evaluation can revise it. No full-language population is assigned as readers."
            ),
            "calibration_status": "retained_domain_prior_not_measurement",
            "sensitivity_endpoint_interpretation": "conditional ordinal judgments, not observed bounds or confidence intervals",
        }
        if dimension == "R":
            supplied[dimension]["measure_kind"] = "newly_comfortable_reader_opportunity"
    result = {"dimensions": supplied}
    if same_domain and resolved:
        result["delivery_mode"] = "semantic_text_offline"
    return result


def load_calibrations(paths: list[Path]) -> tuple[dict, list[dict]]:
    """Load researcher-authored judgments; duplicate entry ownership fails."""
    by_id, inputs = {}, []
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(f"Required planning calibration is missing: {path.name}")
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        records = payload.get("entries", payload.get("evidence", []))
        if isinstance(records, dict):
            records = [{"entry_id": key, **value} for key, value in records.items()]
        if not isinstance(records, list) or not records:
            raise ValueError(f"Planning calibration has no entries: {path.name}")
        identity = file_identity(path)
        inputs.append(identity)
        for record in records:
            entry_id = record.get("entry_id", "")
            if not entry_id or entry_id in by_id:
                raise ValueError(f"Missing/duplicate planning entry: {entry_id}")
            evidence = copy.deepcopy(record.get("evidence", record))
            evidence.pop("entry_id", None)
            if not isinstance(evidence.get("dimensions"), dict):
                raise ValueError(f"Missing dimensions for planning entry: {entry_id}")
            for dim, value in evidence["dimensions"].items():
                if dim not in DIMENSIONS or not isinstance(value, dict):
                    raise ValueError(f"Invalid planning dimension: {entry_id}/{dim}")
                value["calibration_file_identity"] = identity
                if value.get("base") is not None:
                    base = value["base"]
                    if not isinstance(base, int) or not value["low"] <= base <= value["high"] or not value.get("base_basis"):
                        raise ValueError(f"Unjustified baseline band: {entry_id}/{dim}")
            by_id[entry_id] = evidence
    return by_id, inputs


def assemble_context(rows: list[dict], recovered: list[dict], recovered_identity: dict,
                     lane_context: dict, calibrations: dict) -> tuple[dict, list[dict]]:
    context = copy.deepcopy(lane_context)
    context.update({"opportunity_view": "planning", "scenario_label": "base"})
    context.setdefault("evidence", {})
    crosswalk = []
    row_ids = {row["entry_id"] for row in rows}
    missing = set(calibrations) - row_ids
    if missing:
        raise ValueError("Calibration has no current candidate: " + ", ".join(sorted(missing)))
    for row in rows:
        entry_id = row["entry_id"]
        retained = exact_prior_for_row(row, recovered, recovered_identity)
        current = context["evidence"].setdefault(entry_id, {})
        current.update(retained)
        calibrated = calibrations.get(entry_id)
        if calibrated:
            old_dims = current.get("dimensions", {})
            current.update(copy.deepcopy(calibrated))
            current["dimensions"] = {**old_dims, **copy.deepcopy(calibrated["dimensions"])}
            if not current.get("delivery_mode"):
                combined_route = " ".join((row.get("first_bounded_package", ""), row.get("education_stages", ""))).lower()
                oral_entry = any(term in combined_route for term in ("literacy", "foundational", "ece", "spoken narration", "oral"))
                current["delivery_mode"] = "text_with_oral_entry_offline" if oral_entry else "semantic_text_offline"
                current["delivery_mode_basis"] = "Named current package route; separates oral/literacy entry from an already-reading semantic-text cohort for A comparability. Not a value ranking between modes."
        dimensions = current.get("dimensions", {})
        if dimensions:
            crosswalk.append({"entry_id": entry_id, "current_package": row.get("first_bounded_package", ""),
                              "current_stage": row.get("education_stages", ""),
                              "calibration_origin": "package_specific_research" if calibrated else "recovered_scope_compatible_prior",
                              "dimensions": copy.deepcopy(dimensions)})
    return context, crosswalk


def scenario_context(context: dict, label: str) -> dict:
    """Use supplied baseline/endpoints explicitly; never invent a midpoint."""
    if label not in {"base", "cautious", "favorable", "envelope", "measured_only"}:
        raise ValueError("Unknown planning scenario: " + label)
    result = copy.deepcopy(context)
    result["scenario_label"] = label
    result["opportunity_view"] = "measured_only" if label == "measured_only" else "planning"
    if label in {"envelope", "measured_only"}:
        return result
    for evidence in result.get("evidence", {}).values():
        for dimension, value in evidence.get("dimensions", {}).items():
            if value.get("status") == "unknown" or "low" not in value or "high" not in value:
                continue
            # Dialect risk is a separate adverse modifier: lower risk is the
            # favorable scenario. It is never multiplied into reader counts.
            field = ("base" if label == "base" else
                     "high" if (label == "favorable") != (dimension == "D") else "low")
            chosen = value.get(field)
            if chosen is None:
                continue
            value["supplied_planning_envelope"] = {"low": value["low"], "high": value["high"]}
            value["selected_scenario_band"] = {"scenario": label, "field": field, "value": chosen}
            value["low"] = value["high"] = chosen
            value["scenario_interpretation"] = "conditional ordinal planning judgment; not confidence bound or observed benefit"
    return result
