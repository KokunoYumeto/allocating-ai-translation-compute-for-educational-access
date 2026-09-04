#!/usr/bin/env python3
"""Build a conservative, source-bound population authorization ledger.

The successor-universe files intentionally preserve many context and
quarantined observations.  This script does not score or impute them.  It
creates an auditable admission/exclusion table for the *population* input to a
later model: only exact edition targets with a typed person measure, explicit
source identity, and a defensible person denominator are admitted.  Stage,
territorial, percentage, proxy, and synthetic/context observations remain
visible but cannot silently become beneficiary counts.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

BASE = Path(__file__).resolve().parents[1]
CANON = BASE / "structured/canonical_universe_successor_v2.json"
AUTHORITY = BASE / "structured/SUCCESSOR_EDITION_TARGET_AUTHORITY_v3.csv"
MAPPING = BASE / "structured/SUCCESSOR_EDITION_EVIDENCE_MAPPING_v3.csv"
REGIONAL_FILES = [
    BASE / "structured/ASIA_EMPIRICAL_NEED_INPUTS.csv",
    BASE / "structured/AFRICA_EMPIRICAL_NEED_INPUTS.csv",
    BASE / "structured/AMERICAS_EUROPE_EMPIRICAL_NEED_INPUTS.csv",
    BASE / "structured/OCEANIA_CENTRAL_ASIA_EMPIRICAL_INPUTS.csv",
]
REGIONAL_SOURCE_FILES = [
    BASE / "structured/ASIA_EMPIRICAL_NEED_SOURCES.csv",
    BASE / "structured/AFRICA_EMPIRICAL_NEED_SOURCES.csv",
    BASE / "structured/AMERICAS_EUROPE_EMPIRICAL_NEED_SOURCE_REGISTRY.csv",
    BASE / "structured/OCEANIA_CENTRAL_ASIA_SOURCE_REGISTRY.csv",
]
OUT = BASE / "structured/EVIDENCE_AUTHORIZATION_v1.csv"
RECEIPT = BASE / "qa/EVIDENCE_AUTHORIZATION_V1_RECEIPT.json"
RECEIPT_SHA = BASE / "qa/EVIDENCE_AUTHORIZATION_V1_RECEIPT.sha256"

FIELDS = [
    "authorization_id", "authorization_status", "authorization_tier", "reason",
    "edition_target_id", "canonical_language_target_id", "regional_stratum_id",
    "evidence_identity_id", "source_lane", "source_record_id", "evidence_role",
    "measure_class", "population_unit", "population_low_persons",
    "population_base_persons", "population_high_persons", "population_bound_type",
    "normalized_population_low_persons", "normalized_population_high_persons",
    "population_definition",
    "reference_year", "territory", "script_or_mode", "source_ids", "source_urls",
    "source_locators", "source_registry_row_hashes", "target_binding",
    "population_rankability_status", "rank_eligibility_source_label",
    "additivity_class", "overlap_group", "target_exactness", "target_row_sha256",
    "evidence_row_sha256", "source_evidence_row_sha256", "local_work_exclusion",
    "synthetic_or_model_prior",
]

PERSON_MEASURE_CLASSES = {
    "l1", "home_language", "home_or_first_language", "home_language_response",
    "home_language_nonexclusive", "speaker_or_reported_ability", "reported_ability",
    "speaker_estimate", "speaker_estimate_lower_bound", "usual_spoken", "daily_use",
    "language_knowledge", "nonexclusive_use", "first_learned",
}
REGIONAL_ALLOW_RE = re.compile(
    r"(?:^|_)(?:census_mother_tongue(?:_count)?|census_language_used_at_home|"
    r"census_language_spoken_at_home|census_language_spoken_at_home_any_response|"
    r"census_household_language_count|census_home_language_including_combinations|"
    r"census_current_language_use_primary_or_secondary|"
    r"census_first_language_learned|census_conversational_knowledge_published_rounded_count|"
    r"census_reported_speakers|census_everyday_conversation_ability|"
    r"census_speak_or_understand|census_native_language|"
    r"census_exact_language_speaking_or_home_use|census_exact_childhood_acquired_language|"
    r"census_childhood_acquired_language|census_self_reported_speaking_ability|"
    r"census_self_report_fluent_speaking_age5plus|census_rounded_language_ability_interval|"
    r"census_rounded_language_literacy_interval|census_written_tifinagh_literacy_count|"
    r"derived_census_first_home_language|derived_census_home_language_any_response|"
    r"derived_census_reported_speaking_age5plus|exact_census_reported_language_ability_count|"
    r"exact_census_reported_daily_language_use_count|preliminary_census_native_language_rounded|"
    r"official_2000_exact_variant_estimate|official_sociolinguistic_survey_estimate|"
    r"official_plan_citing_2018_census_speaker_count|official_sample_survey_speaking_ability_estimate|"
    r"official_approximate_source_stated_speaker_range|official_source_stated_lower_bound_speakers|"
    r"source_stated_2009_fluent_speaker_estimate_range|survey_estimate_language_spoken_at_home_age5plus|"
    r"peer_reviewed_(?:rounded_speaker_estimate|secondary_estimate_range|transnational_estimate_range|"
    r"rounded_minimum_speakers|rounded_l1_l2_estimate)|"
    r"research_estimate_transboundary_speakers|published_transboundary_estimate_range)"
)
DENY_RE = re.compile(
    r"(?:percentage|percent|proxy|ethnic|ethnicity|identity|territorial|exposure|ceiling|"
    r"enrol|enroll|student|learner|workforce|resident|refugee|disability|support_need|"
    r"not_estimated|unrankable|no_compatible|no_denominator|sample_counts_no_population|"
    r"household_counts_no_person|shares_without|share_no_|no_exact_|not_script_readership|"
    r"script_literacy_overlap|mixed_year_derived|model_based|nationality|offline_population|"
    r"stage|opportunity|context_only|macro_|l1_proxy|direct_reach_synthesis)"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def row_hash(row: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json({k: v for k, v in row.items() if k not in {"row_sha256", "evidence_row_sha256"}}))


def persisted_row_hash(row: Mapping[str, Any]) -> str:
    """Hash the exact string-valued CSV projection, excluding its hash field.

    Dicts assembled from JSON contain numbers, booleans and nulls, whereas a
    CSV round trip exposes strings (and writes null as an empty cell). Hashing
    this normalized projection makes the receipt reproducible from persisted
    bytes while source_evidence_row_sha256 retains the raw source-object
    identity.
    """
    projected = {}
    for field in FIELDS:
        if field == "evidence_row_sha256":
            continue
        value = row.get(field, "")
        projected[field] = "" if value is None else str(value)
    return sha256_bytes(canonical_json(projected))


def _present(value: Any) -> bool:
    """Whether a source bound cell is present (empty CSV cell means null)."""
    return value is not None and str(value) != ""


def bound_type(low: Any, base: Any, high: Any) -> str:
    """Classify the source bound encoding without filling missing cells.

    The upstream successor contract uses the same five meaningful states:
    POINT (a base point, optionally repeated at both endpoints), INTERVAL
    (both endpoints), LOWER_BOUND, UPPER_BOUND, and NONE.  MIXED is retained
    as an explicit diagnostic for malformed combinations such as a base plus
    only one endpoint; it is never silently coerced to a point.
    """
    has_low, has_base, has_high = _present(low), _present(base), _present(high)
    if has_base:
        if has_low and has_high:
            nlow, nbase, nhigh = num(low), num(base), num(high)
            if nlow is not None and nbase is not None and nhigh is not None:
                return "POINT" if nlow == nbase == nhigh else "INTERVAL"
            return "MIXED"
        # A lower/upper-bound source may repeat its one supplied endpoint in
        # ``base`` (for example, a published "more than one million" floor).
        # Keep that as one-sided evidence rather than mistaking it for a
        # complete point estimate.  A non-equal combination is malformed.
        if has_low and not has_high:
            nlow, nbase = num(low), num(base)
            return "LOWER_BOUND" if nlow is not None and nbase is not None and nlow == nbase else "MIXED"
        if has_high and not has_low:
            nbase, nhigh = num(base), num(high)
            return "UPPER_BOUND" if nhigh is not None and nbase is not None and nhigh == nbase else "MIXED"
        if not has_low and not has_high:
            return "POINT"
        return "MIXED"
    if has_low and has_high:
        return "INTERVAL"
    if has_low:
        return "LOWER_BOUND"
    if has_high:
        return "UPPER_BOUND"
    return "NONE"


def normalized_bounds(low: Any, base: Any, high: Any, semantics: str | None = None) -> tuple[Any, Any]:
    """Return deterministic model bounds while retaining raw source cells.

    Only a point base is repeated into two arithmetic endpoints.  Intervals
    retain both source endpoints.  One-sided and absent evidence remains
    one-sided/absent; no upper or lower ceiling is invented in this ledger.
    """
    semantics = semantics or bound_type(low, base, high)
    if semantics == "POINT":
        return (base, base) if _present(base) else ("", "")
    if semantics == "INTERVAL":
        return low, high
    if semantics == "LOWER_BOUND":
        return low, ""
    if semantics == "UPPER_BOUND":
        return "", high
    return "", ""


def effective_rankability_status(source_status: Any, semantics: str) -> str:
    """Align the rankability label with the source bound shape.

    Some legacy canonical records called a three-point low/base/high screening
    band ``POINT_DISTRIBUTION``.  That label is not faithful to the actual
    evidence: a non-degenerate band must be scored and reported as an
    interval.  This adapter changes only the derived authorization label; the
    raw source object and its original status remain preserved by
    ``source_evidence_row_sha256``.
    """
    status = str(source_status or "").strip().upper()
    if semantics == "INTERVAL" and status == "POINT_DISTRIBUTION":
        return "INTERVAL_ONLY"
    return status


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="raise", lineterminator="\n")
        writer.writeheader()
        writer.writerows({k: row.get(k, "") for k in FIELDS} for row in rows)
    tmp.replace(path)


def num(value: Any) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    try:
        value = float(str(value).replace(",", ""))
    except ValueError:
        return None
    return value if value >= 0 else None


def source_tokens(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    return [x.strip() for x in re.split(r"[;|]", str(value or "")) if x.strip()]


def target_eid(language_target_id: str, authority_ids: set[str]) -> str:
    raw = str(language_target_id or "")
    candidates = [raw, "edition-target:" + raw]
    for candidate in candidates:
        if candidate in authority_ids:
            return candidate
    return ""


def source_lookup(source_registry: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for source in source_registry:
        ids = [source.get("source_id"), source.get("canonical_source_id"), source.get("upstream_source_id")]
        ids.extend(source.get("same_url_alias_ids", []) or [])
        for sid in ids:
            if sid:
                key = str(sid)
                if key in lookup:
                    # The frozen canonical registry remains primary when an
                    # inherited regional registry uses the same identifier
                    # with a landing-page URL rather than the direct file.
                    # New successor-only source IDs still enter below.
                    continue
                lookup[key] = source
    return lookup


def source_fields(ids: Iterable[str], urls: Iterable[str], lookup: dict[str, dict[str, Any]]) -> tuple[str, str, str]:
    id_list = list(dict.fromkeys(str(x) for x in ids if str(x).strip()))
    url_list = list(dict.fromkeys(str(x) for x in urls if str(x).strip()))
    hashes: list[str] = []
    for sid in id_list:
        source = lookup.get(sid)
        if not source:
            continue
        if source.get("url"):
            url_list.append(str(source["url"]))
        if source.get("source_row_sha256"):
            hashes.append(str(source["source_row_sha256"]))
    return ";".join(id_list), ";".join(dict.fromkeys(url_list)), ";".join(dict.fromkeys(hashes))


def base_row(**kwargs: Any) -> dict[str, Any]:
    row = {field: "" for field in FIELDS}
    row.update(kwargs)
    row["local_work_exclusion"] = "true"
    row["synthetic_or_model_prior"] = "false"
    return row


def classify_canonical(evidence: dict[str, Any], target: dict[str, Any], lookup: dict[str, dict[str, Any]]) -> tuple[str, str, str]:
    label = str(evidence.get("rank_eligibility_source_label", ""))
    binding = str(evidence.get("target_binding", ""))
    status = str(evidence.get("population_rankability_status", ""))
    cls = str(evidence.get("measure_class", ""))
    definition = str(evidence.get("population_definition", ""))
    vals = evidence.get("person_normalization", {}).get("values_persons", {}) or {}
    base = num(vals.get("base")); low = num(vals.get("low")); high = num(vals.get("high"))
    semantics = bound_type(vals.get("low", ""), vals.get("base", ""), vals.get("high", ""))
    status = effective_rankability_status(status, semantics)
    ids = source_tokens(evidence.get("source_ids")); urls = source_tokens(evidence.get("source_url"))
    _, resolved_urls, _ = source_fields(ids, urls, lookup)
    exact = str(target.get("exactness", "")) == "exact"
    if not exact:
        return "EXCLUDE", "target identity is unresolved/macro/context", "none"
    # Preserve exact, source-bound enrolment/support cohorts in a separate
    # opportunity lane.  They are useful for planning but are never admitted
    # as a whole-language person denominator.
    if label.startswith("eligible_exact_stage") or cls in {"formal_education_enrolment", "higher_education_enrolment", "direct_language_support_need_cohort"}:
        if (base is None and low is None and high is None) or not ids or not resolved_urls:
            return "EXCLUDE", "stage/opportunity row lacks a numeric bound or source resolution", "none"
        return "STAGE_OPPORTUNITY", "exact source-bound stage/enrolment opportunity; excluded from person-need order", "STAGE_EXACT_OPPORTUNITY"
    if not binding == "DIRECT_TARGET_ONLY":
        return "EXCLUDE", f"target binding is {binding or 'missing'}", "none"
    if not label.startswith(("eligible_direct_", "ADMIT_DIRECT")):
        return "EXCLUDE", f"eligibility label is {label or 'missing'}", "none"
    if status not in {"POINT_DISTRIBUTION", "INTERVAL_ONLY"}:
        return "EXCLUDE", f"population rankability status is {status or 'missing'}", "none"
    if cls.lower() not in PERSON_MEASURE_CLASSES:
        return "EXCLUDE", f"measure class {cls or 'missing'} is not a direct person-language class", "none"
    # As in the regional lane, the controlled measure-class token carries the
    # positive/negative semantic contract.  Definitions often use words such
    # as "households", "resident", or "not ethnic identity" to delimit an
    # otherwise direct census person count.  Searching that prose with the
    # deny regex reverses the meaning of those cautions (for example, it had
    # excluded the American Samoa census count merely because the valid
    # home-language universe was described as people in households).
    if DENY_RE.search(cls.lower()):
        return "EXCLUDE", "definition/class contains proxy, context, script-mismatch, or non-person denominator marker", "none"
    if base is None and low is None and high is None:
        return "EXCLUDE", "no numeric person bound", "none"
    # A lower-bound-only statement is useful descriptive evidence but cannot
    # support a comparable interval or model denominator without inventing an
    # upper bound.  Retain it as an explicit exclusion until a source supplies
    # a bounded estimate.
    if base is None and not (low is not None and high is not None):
        return "EXCLUDE", "numeric evidence lacks a complete explicit interval (lower/upper bound or point)", "none"
    if status == "POINT_DISTRIBUTION" and base is None:
        return "EXCLUDE", "point distribution lacks a base person count", "none"
    if status == "INTERVAL_ONLY" and (low is None or high is None):
        return "EXCLUDE", "interval evidence lacks both explicit bounds", "none"
    if bound_type(vals.get("low", ""), vals.get("base", ""), vals.get("high", "")) in {"LOWER_BOUND", "UPPER_BOUND", "MIXED"}:
        return "EXCLUDE", "numeric evidence is one-sided or has a mixed bound encoding", "none"
    if not ids:
        return "EXCLUDE", "missing source identity", "none"
    if not resolved_urls:
        return "EXCLUDE", "source identity has no resolvable URL", "none"
    tier = "A_DIRECT_TYPED_PERSON" if status == "POINT_DISTRIBUTION" else "B_INTERVAL_TYPED_PERSON"
    return "ADMIT", "exact target + direct typed person measure + source-resolved evidence", tier


def classify_regional(row: dict[str, str], authority_row: dict[str, str], lookup: dict[str, dict[str, Any]]) -> tuple[str, str, str]:
    cls = str(row.get("population_measure_class", ""))
    # Exclusion markers are evaluated on the measure class and affirmative
    # population definition only.  The uncertainty field deliberately says
    # what a valid measure does *not* establish (for example, "not literacy"
    # or "no learner denominator"); searching those cautions as if they were
    # the measurement claim inverted their meaning and excluded valid census
    # person counts.
    # The controlled measure-class token is the positive/negative semantic
    # contract.  Definitions routinely contain negated cautions such as
    # "not ethnic belonging" or "usual residents"; substring-matching those
    # prose cautions inverted them.  Apply deny markers to the class token
    # only, after the explicit allowlist match.
    blob = cls.lower()
    base = num(row.get("population_base_persons")); low = num(row.get("population_low_persons")); high = num(row.get("population_high_persons"))
    if str(authority_row.get("effective_order_l_target", "false")).lower() != "true":
        return "EXCLUDE", "authority target is not effective", "none"
    if not REGIONAL_ALLOW_RE.search(cls.lower()):
        return "EXCLUDE", f"regional class {cls or 'missing'} is not an explicitly typed person count", "none"
    if DENY_RE.search(blob):
        return "EXCLUDE", "regional definition/class contains incompatible proxy, ceiling, or script-mismatch marker", "none"
    if base is None and low is None and high is None:
        return "EXCLUDE", "no numeric person bound", "none"
    if base is None and not (low is not None and high is not None):
        return "EXCLUDE", "numeric evidence lacks a complete explicit interval (lower/upper bound or point)", "none"
    if bound_type(row.get("population_low_persons", ""), row.get("population_base_persons", ""), row.get("population_high_persons", "")) in {"LOWER_BOUND", "UPPER_BOUND", "MIXED"}:
        return "EXCLUDE", "numeric evidence is one-sided or has a mixed bound encoding", "none"
    ids = source_tokens(row.get("source_ids")); urls = source_tokens(row.get("source_urls"))
    _, resolved_urls, _ = source_fields(ids, urls, lookup)
    if not ids:
        return "EXCLUDE", "missing source identity", "none"
    if not resolved_urls:
        return "EXCLUDE", "source identity has no resolvable URL", "none"
    if not row.get("population_reference_year", "").strip():
        return "EXCLUDE", "missing reference year", "none"
    semantics = bound_type(row.get("population_low_persons", ""), row.get("population_base_persons", ""), row.get("population_high_persons", ""))
    if semantics == "INTERVAL":
        tier = "B_REGIONAL_INTERVAL_TYPED_PERSON"
    else:
        tier = "A_REGIONAL_EXACT_TYPED_PERSON" if "exact" in cls.lower() or "census_" in cls.lower() else "B_REGIONAL_ESTIMATE"
    return "ADMIT", "exact regional authority target + typed person measure + source-resolved evidence", tier


def main() -> None:
    canon = json.loads(CANON.read_text(encoding="utf-8"))
    authority_rows = read_csv(AUTHORITY)
    mapping_rows = read_csv(MAPPING)
    authority_by_eid = {str(row["edition_target_id"]): row for row in authority_rows}
    authority_ids = set(authority_by_eid)
    target_by_lang = {str(row["canonical_target_id"]): row for row in authority_rows if row.get("canonical_target_id")}
    target_by_eid = authority_by_eid
    source_registry = list(canon.get("source_registry", []))
    for path in REGIONAL_SOURCE_FILES:
        for raw_source in read_csv(path):
            source = dict(raw_source)
            source["source_row_sha256"] = sha256_bytes(canonical_json(raw_source))
            source_registry.append(source)
    lookup = source_lookup(source_registry)
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    counts = Counter()

    # The normalized successor mapping is the authority for attaching a
    # regional evidence identity to an edition target.  Earlier builds tried
    # to reconstruct this attachment from the regional stratum ID alone.  That
    # failed whenever an exact regional row had already been normalized onto a
    # canonical language edition, silently excluding otherwise comparable
    # rows.  Keep all mapped identities, require agreement if duplicate source
    # rows exist, and fail closed on ambiguity.
    mapped_targets: dict[tuple[str, str], set[str]] = defaultdict(set)
    for mapped in mapping_rows:
        lane = str(mapped.get("source_lane", ""))
        record = str(mapped.get("source_record_id", ""))
        edition = str(mapped.get("edition_target_id", ""))
        if lane and record and edition:
            mapped_targets[(lane, record)].add(edition)

    # Canonical population evidence is authoritative for canonical target IDs.
    for evidence in canon.get("population_evidence", []):
        language_ids = [str(x) for x in evidence.get("language_target_ids", [])]
        lang_id = language_ids[0] if language_ids else ""
        eid = target_eid(lang_id, authority_ids)
        target = target_by_eid.get(eid, {})
        status, reason, tier = classify_canonical(evidence, target, lookup) if eid else ("EXCLUDE", "no exact authority target binding", "none")
        ids = source_tokens(evidence.get("source_ids")); urls = source_tokens(evidence.get("source_url"))
        source_id_text, source_url_text, source_hash_text = source_fields(ids, urls, lookup)
        vals = evidence.get("person_normalization", {}).get("values_persons", {}) or {}
        # Preserve the source's bound semantics.  A point estimate is carried
        # in ``base`` with null low/high; downstream model adapters may use a
        # degenerate point for arithmetic, but the authorization ledger must
        # never rewrite a missing endpoint as if the source supplied it.
        vlow = vals.get("low", "")
        vbase = vals.get("base", "")
        vhigh = vals.get("high", "")
        vtype = bound_type(vlow, vbase, vhigh)
        vnorm_low, vnorm_high = normalized_bounds(vlow, vbase, vhigh, vtype)
        effective_status = effective_rankability_status(evidence.get("population_rankability_status", ""), vtype)
        effective_tier = tier
        if status == "ADMIT" and vtype == "INTERVAL" and tier == "A_DIRECT_TYPED_PERSON":
            effective_tier = "B_INTERVAL_TYPED_PERSON"
        out = base_row(
            authorization_id="auth:canonical:" + str(evidence.get("population_evidence_id", "")),
            authorization_status=status, authorization_tier=effective_tier, reason=reason,
            edition_target_id=eid, canonical_language_target_id=lang_id,
            evidence_identity_id=str(evidence.get("population_evidence_id", "")),
            source_lane=str(evidence.get("origin_lane", "")), source_record_id=str(evidence.get("origin_record_id", "")),
            evidence_role=str(evidence.get("measure_role", "")), measure_class=str(evidence.get("measure_class", "")),
            population_unit=str(evidence.get("source_values", {}).get("unit", "")),
            population_low_persons=vlow, population_base_persons=vbase, population_high_persons=vhigh,
            population_bound_type=vtype,
            normalized_population_low_persons=vnorm_low,
            normalized_population_high_persons=vnorm_high,
            population_definition=str(evidence.get("population_definition", "")), reference_year=str(evidence.get("reference_year", "")),
            source_ids=source_id_text, source_urls=source_url_text, source_locators="",
            source_registry_row_hashes=source_hash_text, target_binding=str(evidence.get("target_binding", "")),
            population_rankability_status=effective_status,
            rank_eligibility_source_label=str(evidence.get("rank_eligibility_source_label", "")),
            additivity_class=str(evidence.get("additivity_class", "")), overlap_group=str(evidence.get("overlap_group", "") or ""),
            target_exactness=str(target.get("exactness", "")), target_row_sha256=str(target.get("row_sha256", "")),
            source_evidence_row_sha256=sha256_bytes(canonical_json(evidence)),
        )
        rows.append(out); counts["canonical_" + status.lower()] += 1

    # Regional bundles are exact when their stratum has an effective authority row.
    for path in REGIONAL_FILES:
        for regional in read_csv(path):
            sid = str(regional.get("stratum_id", ""))
            mapped = mapped_targets.get((path.stem, sid), set())
            if len(mapped) == 1:
                eid = next(iter(mapped))
            elif len(mapped) > 1:
                eid = ""
            else:
                eid = target_eid(sid, authority_ids) or ("edition-target:regional:" + sid if "edition-target:regional:" + sid in authority_ids else "")
            target = authority_by_eid.get(eid, {})
            if len(mapped) > 1:
                status, reason, tier = "EXCLUDE", "ambiguous normalized authority target binding", "none"
            else:
                status, reason, tier = classify_regional(regional, target, lookup) if eid else ("EXCLUDE", "no exact authority target binding", "none")
            ids = source_tokens(regional.get("source_ids")); urls = source_tokens(regional.get("source_urls"))
            source_id_text, source_url_text, source_hash_text = source_fields(ids, urls, lookup)
            aid = "auth:regional:" + path.stem + ":" + sid
            if aid in seen:
                continue
            seen.add(aid)
            # Keep blank source endpoints blank for POINT semantics.  The
            # ranker can normalize a source-supplied base internally, while
            # this persisted authority remains faithful to the bundle
            # contract (missing numeric evidence stays null).
            rlow = regional.get("population_low_persons", "")
            rbase = regional.get("population_base_persons", "")
            rhigh = regional.get("population_high_persons", "")
            rtype = bound_type(rlow, rbase, rhigh)
            rnorm_low, rnorm_high = normalized_bounds(rlow, rbase, rhigh, rtype)
            rstatus = "INTERVAL_ONLY" if rtype == "INTERVAL" and status == "ADMIT" else ("POINT_DISTRIBUTION" if status == "ADMIT" else "INSUFFICIENT_PUBLIC_EVIDENCE")
            overlap_group = sid
            overlap_text = " ".join(
                [
                    str(regional.get("population_definition", "")),
                    str(regional.get("uncertainty_incompatibilities", "")),
                ]
            ).casefold()
            multiresponse_markers = (
                "multiple language",
                "more than one language",
                "overlap across languages",
                "including combinations",
                "primary and secondary language categories overlap",
            )
            if source_id_text and any(marker in overlap_text for marker in multiresponse_markers):
                overlap_key = "|".join(
                    [
                        source_id_text,
                        str(regional.get("territory", "")),
                        str(regional.get("population_measure_class", "")),
                    ]
                )
                overlap_group = "nonadditive-multilanguage:" + sha256_bytes(
                    overlap_key.encode("utf-8")
                )[:16]
            out = base_row(
                authorization_id=aid, authorization_status=status, authorization_tier=tier, reason=reason,
                edition_target_id=eid, regional_stratum_id=sid,
                evidence_identity_id="regional:" + path.stem + ":" + sid,
                source_lane=path.stem, source_record_id=sid, evidence_role="REGIONAL_EMPIRICAL_STRATUM",
                measure_class=str(regional.get("population_measure_class", "")), population_unit=str(regional.get("population_unit", "")),
                population_low_persons=rlow, population_base_persons=rbase, population_high_persons=rhigh,
                population_bound_type=rtype,
                normalized_population_low_persons=rnorm_low,
                normalized_population_high_persons=rnorm_high,
                population_definition=str(regional.get("population_definition", "")), reference_year=str(regional.get("population_reference_year", "")),
                territory=str(regional.get("territory", "")), script_or_mode=str(regional.get("script_or_mode", "")),
                source_ids=source_id_text, source_urls=source_url_text, source_locators=str(regional.get("source_locators", "")),
                source_registry_row_hashes=source_hash_text, target_binding="DIRECT_TARGET_ONLY" if status == "ADMIT" else "",
                population_rankability_status=rstatus,
                rank_eligibility_source_label="eligible_regional_typed_measure" if status == "ADMIT" else "context_only:regional_excluded",
                additivity_class="non_additive; never sum with another measure or measure class without a proved disjoint-person crosswalk",
                overlap_group=overlap_group, target_exactness=str(target.get("exactness", "")), target_row_sha256=str(target.get("row_sha256", "")),
                source_evidence_row_sha256=sha256_bytes(canonical_json(regional)),
            )
            rows.append(out); counts["regional_" + status.lower()] += 1

    # Stable order and row hashes are computed after all semantic fields exist.
    # The hash is deliberately computed from the exact string projection that
    # DictWriter emits, then checked again after a CSV round trip below.  This
    # catches the old numeric/null mismatch where an in-memory JSON row hashed
    # differently from its persisted CSV representation.
    rows.sort(key=lambda x: x["authorization_id"])
    for row in rows:
        row["evidence_row_sha256"] = persisted_row_hash(row)
    admitted = [row for row in rows if row["authorization_status"] == "ADMIT"]
    admitted_ids = {row["edition_target_id"] for row in admitted}
    valid_bound_types = {"POINT", "INTERVAL", "LOWER_BOUND", "UPPER_BOUND", "NONE", "MIXED"}

    def normalized_bound_assertion(row: Mapping[str, Any]) -> bool:
        semantics = str(row.get("population_bound_type", ""))
        low = row.get("population_low_persons", "")
        base = row.get("population_base_persons", "")
        high = row.get("population_high_persons", "")
        nlow = row.get("normalized_population_low_persons", "")
        nhigh = row.get("normalized_population_high_persons", "")
        if semantics == "POINT":
            return _present(base) and str(nlow) == str(base) and str(nhigh) == str(base)
        if semantics == "INTERVAL":
            return _present(low) and _present(high) and str(nlow) == str(low) and str(nhigh) == str(high)
        if semantics == "LOWER_BOUND":
            return (
                _present(low) and not _present(high)
                and (not _present(base) or (num(base) is not None and num(base) == num(low)))
                and str(nlow) == str(low) and not _present(nhigh)
            )
        if semantics == "UPPER_BOUND":
            return (
                _present(high) and not _present(low)
                and (not _present(base) or (num(base) is not None and num(base) == num(high)))
                and not _present(nlow) and str(nhigh) == str(high)
            )
        if semantics == "NONE":
            return not _present(low) and not _present(base) and not _present(high) and not _present(nlow) and not _present(nhigh)
        # MIXED is an explicit diagnostic, never a normalized scoring input.
        return not _present(nlow) and not _present(nhigh)

    assertions = {
        "rows_total": len(rows),
        "admitted_rows": len(admitted),
        "excluded_rows": len(rows) - len(admitted),
        "admitted_target_count": len(admitted_ids),
        "admitted_no_context_or_stage_binding": all(row["target_binding"] == "DIRECT_TARGET_ONLY" for row in admitted),
        "admitted_no_synthetic_prior": all(row["synthetic_or_model_prior"] == "false" for row in admitted),
        "admitted_have_source_identity": all(bool(row["source_ids"]) for row in admitted),
        "admitted_have_source_url": all(bool(row["source_urls"]) for row in admitted),
        "admitted_have_exact_authority": all(row["target_exactness"] in {"exact", "exact_regional_stratum", "exact_sentinel_target"} for row in admitted),
        "authorization_ids_unique": len({row["authorization_id"] for row in rows}) == len(rows),
        "bound_types_valid": all(row["population_bound_type"] in valid_bound_types for row in rows),
        "normalized_bounds_are_deterministic": all(normalized_bound_assertion(row) for row in rows),
        "mixed_bound_rows_excluded": all(row["authorization_status"] == "EXCLUDE" for row in rows if row["population_bound_type"] == "MIXED"),
    }
    if not all(assertions.values()):
        raise RuntimeError(json.dumps(assertions, sort_keys=True))
    write_csv(OUT, rows)
    # Re-read the bytes just written.  This is the authoritative hash check;
    # it proves the target/evidence row hashes survive CSV serialization.
    persisted_rows = read_csv(OUT)
    assertions["serialized_row_count_matches"] = len(persisted_rows) == len(rows)
    assertions["serialized_row_hashes_valid"] = (
        assertions["serialized_row_count_matches"]
        and all(row.get("evidence_row_sha256", "") == persisted_row_hash(row) for row in persisted_rows)
    )
    assertions["persisted_row_hashes_valid"] = assertions["serialized_row_hashes_valid"]
    if not all(assertions.values()):
        raise RuntimeError(json.dumps(assertions, sort_keys=True))
    receipt = {
        "schema": "interlanguage/evidence-authorization/1.1.0",
        "status": "PASS",
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "script": {
            "path": "scripts/build_evidence_authorization_v1.py",
            "bytes": Path(__file__).stat().st_size,
            "sha256": sha256_file(Path(__file__)),
        },
        "rule": "Only exact authority targets with explicit typed person-language evidence and source-resolved identity/URL are admitted; all context, stage, proxy, ceiling, script-mismatch, and synthetic rows remain excluded.",
        "bound_rule": "population_low_persons, population_base_persons, and population_high_persons preserve the source-normalized person cells exactly, including null endpoints as empty cells. population_bound_type is derived without imputation (POINT, INTERVAL, LOWER_BOUND, UPPER_BOUND, NONE, or explicit MIXED diagnostic). normalized_population_low_persons/high_persons are deterministic scoring adapters: a POINT base is repeated to both endpoints, an INTERVAL retains both endpoints, and one-sided/NONE evidence remains one-sided/empty. Lower/upper-bound rows remain EXCLUDE until a bounded source is available.",
        "hash_semantics": "source_evidence_row_sha256 is the canonical JSON hash of the raw source object; evidence_row_sha256 is computed over the normalized string-valued persisted CSV row (all FIELDS except evidence_row_sha256, null serialized as empty) and recomputed after writing/readback to prove serialization stability.",
        "inputs": {str(path.relative_to(BASE)).replace("\\", "/"): {"bytes": path.stat().st_size, "sha256": sha256_file(path)} for path in [CANON, AUTHORITY, MAPPING] + REGIONAL_FILES + REGIONAL_SOURCE_FILES},
        "output": {str(OUT.relative_to(BASE)).replace("\\", "/"): {"bytes": OUT.stat().st_size, "sha256": sha256_file(OUT), "rows": len(rows)}},
        "counts": {
            **dict(counts),
            "population_bound_type": dict(Counter(row["population_bound_type"] for row in rows)),
            "source_null_low_rows": sum(not _present(row["population_low_persons"]) for row in rows),
            "source_null_base_rows": sum(not _present(row["population_base_persons"]) for row in rows),
            "source_null_high_rows": sum(not _present(row["population_high_persons"]) for row in rows),
            "point_rows_with_source_null_low": sum(row["population_bound_type"] == "POINT" and not _present(row["population_low_persons"]) for row in rows),
            "point_rows_with_source_null_high": sum(row["population_bound_type"] == "POINT" and not _present(row["population_high_persons"]) for row in rows),
        },
        "assertions": assertions,
        "source_registry_records": len(source_registry),
        "mapping_rank_eligible_true_rows": sum(str(x.get("rank_eligible", "")).lower() == "true" for x in read_csv(MAPPING)),
        "mapping_rank_eligible_false_rows": sum(str(x.get("rank_eligible", "")).lower() == "false" for x in read_csv(MAPPING)),
        "local_work_exclusion": "true; no user/project production, prior translation, sunk compute, or local inventory is read by this layer",
    }
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    RECEIPT_SHA.write_text(f"{sha256_file(RECEIPT)}  {RECEIPT.name}\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
