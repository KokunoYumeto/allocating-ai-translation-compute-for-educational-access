#!/usr/bin/env python3
"""Build conservative portfolio non-additivity bounds for the audited Top-100.

The overlap register identifies alternate script/identity rows that may refer to
the same people.  This artifact is a population-set diagnostic only: it keeps
the standalone decision ranks and source identities unchanged, and reports
sharp marginal count bounds when no disjoint-person crosswalk or common-universe
ceiling is evidenced.

For a group with marginal person-count intervals ``[L_i, H_i]`` the primary
bounds are the assumption-light set-cardinality bounds::

    union lower       = max_i(L_i)
    union upper       = sum_i(H_i)
    intersection lower = 0
    intersection upper = min_i(H_i)

If a common universe ceiling ``N`` were independently supplied, the usual
Frechet count refinements would be possible.  The script records
``max_i(H_i)`` as a *diagnostic* candidate ceiling, but never uses it to narrow
the primary bounds.  Thus an inferred same-universe assumption cannot silently
turn a warning into a unique-person estimate.

No need score, standalone rank, compute value, local production field, or
publication state is read or used.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TOP100 = ROOT / "structured" / "TOP100_NEEDS_ONLY_v3.csv"
DEFAULT_REGISTER = ROOT / "structured" / "PORTFOLIO_OVERLAP_REGISTER_v1.csv"
DEFAULT_AUDIT = ROOT / "qa" / "PORTFOLIO_OVERLAP_AUDIT_v1.json"
DEFAULT_CSV_OUTPUT = ROOT / "structured" / "PORTFOLIO_NONADDITIVITY_BOUNDS_v1.csv"
DEFAULT_JSON_OUTPUT = ROOT / "qa" / "PORTFOLIO_NONADDITIVITY_BOUNDS_v1.json"

SCHEMA = "interlanguage/portfolio-nonadditivity-bounds/1.0.0"
ZERO = Decimal("0")

CSV_FIELDS = [
    "record_type",
    "overlap_group",
    "overlap_type",
    "scenario",
    "crosswalk_status",
    "rankability_status",
    "formula_version",
    "bound_unit",
    "member_index",
    "member_count",
    "decision_rank",
    "edition_target_id",
    "label",
    "language_tag",
    "script",
    "population_reference_year",
    "population_low",
    "population_base",
    "population_high",
    "population_source_id",
    "authorization_id",
    "authorization_additivity_class",
    "evidence_identity_id",
    "source_record_id",
    "source_evidence_row_sha256",
    "target_row_sha256",
    "evidence_row_sha256",
    "source_registry_row_hashes",
    "register_population_base",
    "register_population_source_id",
    "register_authorization_id",
    "register_source_evidence_row_sha256",
    "register_assessment",
    "group_population_low_sum",
    "group_population_base_sum",
    "group_population_high_sum",
    "group_union_lower",
    "group_union_upper",
    "group_intersection_lower",
    "group_intersection_upper",
    "group_same_universe_ceiling_diagnostic_only",
    "group_union_lower_same_universe_diagnostic_only",
    "group_union_upper_same_universe_diagnostic_only",
    "group_intersection_lower_same_universe_diagnostic_only",
    "group_intersection_upper_same_universe_diagnostic_only",
    "group_naive_overcount_lower",
    "group_naive_overcount_upper",
    "portfolio_group_count",
    "portfolio_member_count",
    "portfolio_groupwise_naive_base_sum",
    "portfolio_groupwise_union_lower_sum",
    "portfolio_groupwise_union_upper_sum",
    "portfolio_groupwise_intersection_lower_sum",
    "portfolio_groupwise_intersection_upper_sum",
    "portfolio_groupwise_overcount_lower",
    "portfolio_groupwise_overcount_upper",
    "portfolio_all_rows_union_lower",
    "portfolio_all_rows_union_upper",
    "portfolio_all_rows_intersection_lower",
    "portfolio_all_rows_intersection_upper",
    "bound_method",
    "standalone_rank_snapshot_sha256",
    "standalone_rank_unchanged",
]


class BoundsError(RuntimeError):
    """Raised when an input contract or deterministic invariant fails."""


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise BoundsError(f"CSV has no header: {path}")
        return [dict(row) for row in reader]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_manifest(path: Path, root: Path) -> dict[str, Any]:
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        rel = str(path)
    return {"path": rel, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def display_path(path: Path, root: Path) -> str:
    """Return a stable slash-separated path for artifact metadata."""
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def decimal_value(value: str, *, field: str, row_id: str, required: bool = True) -> Decimal | None:
    text = (value or "").strip()
    if not text:
        if required:
            raise BoundsError(f"{row_id}.{field} is empty")
        return None
    try:
        number = Decimal(text)
    except (InvalidOperation, ValueError) as exc:
        raise BoundsError(f"{row_id}.{field} is not a decimal: {value!r}") from exc
    if not number.is_finite():
        raise BoundsError(f"{row_id}.{field} is not finite: {value!r}")
    return number


def number_text(value: Decimal | None) -> str:
    """Canonical decimal text used in both CSV and JSON payloads."""
    if value is None:
        return ""
    # ``format(..., 'f')`` avoids exponent notation.  Keep meaningful source
    # precision out of the calculation while making derived values stable.
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    if text in {"", "-0"}:
        return "0"
    return text


def rank_key(value: str) -> tuple[int, str]:
    text = (value or "").strip()
    try:
        return (int(text), text)
    except ValueError:
        return (sys.maxsize, text)


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def require_columns(rows: Iterable[Mapping[str, str]], required: Iterable[str], label: str) -> None:
    rows = list(rows)
    if not rows:
        raise BoundsError(f"{label} is empty")
    # DictReader rows all share the same key set; inspect the first row and
    # retain an explicit check so a future malformed CSV fails closed.
    present = set(rows[0])
    missing = sorted(set(required) - present)
    if missing:
        raise BoundsError(f"{label} missing required columns: {missing}")


def same_universe_diagnostics(
    lows: list[Decimal], highs: list[Decimal], candidate_ceiling: Decimal
) -> dict[str, Decimal]:
    """Return Frechet count refinements under an *unasserted* ceiling.

    These values are deliberately emitted with a diagnostic-only suffix.  The
    primary result never substitutes them for the marginal-only bounds.
    """
    count_minus_one = Decimal(len(lows) - 1)
    union_lower = max(max(lows), sum(lows, ZERO) - count_minus_one * candidate_ceiling)
    union_upper = min(candidate_ceiling, sum(highs, ZERO))
    intersection_lower = max(ZERO, sum(lows, ZERO) - count_minus_one * candidate_ceiling)
    intersection_upper = min(highs)
    return {
        "union_lower": union_lower,
        "union_upper": union_upper,
        "intersection_lower": intersection_lower,
        "intersection_upper": intersection_upper,
    }


def build_group(group_id: str, register_rows: list[dict[str, str]], top_by_id: Mapping[str, dict[str, str]]) -> dict[str, Any]:
    members: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for register_row in sorted(
        register_rows,
        key=lambda row: (rank_key(row.get("decision_rank", "")), row.get("edition_target_id", "")),
    ):
        edition_id = register_row.get("edition_target_id", "")
        if edition_id in seen_ids:
            raise BoundsError(f"duplicate edition_target_id in overlap group {group_id}: {edition_id}")
        seen_ids.add(edition_id)
        top_row = top_by_id.get(edition_id)
        if top_row is None:
            raise BoundsError(f"register row not found in Top-100: {edition_id}")

        # The register is a warning ledger derived from the exact Top-100.  A
        # mismatch means the source lineage changed and the artifact must not
        # silently mix rows.
        for field in (
            "decision_rank",
            "label",
            "language_tag",
            "population_reference_year",
            "population_base",
            "population_source_id",
            "authorization_id",
            "source_evidence_row_sha256",
        ):
            if register_row.get(field, "") != top_row.get(field, ""):
                raise BoundsError(
                    f"register/Top-100 mismatch for {edition_id}.{field}: "
                    f"{register_row.get(field)!r} != {top_row.get(field)!r}"
                )

        low = decimal_value(top_row.get("population_low", ""), field="population_low", row_id=edition_id)
        base = decimal_value(top_row.get("population_base", ""), field="population_base", row_id=edition_id)
        high = decimal_value(top_row.get("population_high", ""), field="population_high", row_id=edition_id)
        assert low is not None and base is not None and high is not None
        if low < ZERO or low > base or base > high:
            raise BoundsError(f"invalid population interval for {edition_id}: {low}, {base}, {high}")

        members.append(
            {
                "top": top_row,
                "register": register_row,
                "low": low,
                "base": base,
                "high": high,
            }
        )

    if len(members) < 2:
        raise BoundsError(f"overlap group has fewer than two members: {group_id}")

    lows = [member["low"] for member in members]
    bases = [member["base"] for member in members]
    highs = [member["high"] for member in members]
    candidate_ceiling = max(highs)
    # Primary bounds use no common-universe assumption.
    union_lower = max(lows)
    union_upper = sum(highs, ZERO)
    intersection_lower = ZERO
    intersection_upper = min(highs)
    diagnostics = same_universe_diagnostics(lows, highs, candidate_ceiling)
    naive_base_sum = sum(bases, ZERO)
    overcount_lower = max(ZERO, naive_base_sum - union_upper)
    overcount_upper = max(ZERO, naive_base_sum - union_lower)

    return {
        "overlap_group": group_id,
        "member_count": len(members),
        "members": members,
        "population_low_sum": sum(lows, ZERO),
        "population_base_sum": naive_base_sum,
        "population_high_sum": sum(highs, ZERO),
        "union_lower": union_lower,
        "union_upper": union_upper,
        "intersection_lower": intersection_lower,
        "intersection_upper": intersection_upper,
        "same_universe_ceiling_diagnostic_only": candidate_ceiling,
        "union_lower_same_universe_diagnostic_only": diagnostics["union_lower"],
        "union_upper_same_universe_diagnostic_only": diagnostics["union_upper"],
        "intersection_lower_same_universe_diagnostic_only": diagnostics["intersection_lower"],
        "intersection_upper_same_universe_diagnostic_only": diagnostics["intersection_upper"],
        "naive_overcount_lower": overcount_lower,
        "naive_overcount_upper": overcount_upper,
    }


def build_portfolio(groups: list[dict[str, Any]]) -> dict[str, Any]:
    all_members = [member for group in groups for member in group["members"]]
    lows = [member["low"] for member in all_members]
    highs = [member["high"] for member in all_members]
    bases = [member["base"] for member in all_members]
    # This all-row result makes no claim that distinct warning groups are
    # disjoint.  It is intentionally broad and is retained as a diagnostic.
    all_rows_union_lower = max(lows) if lows else ZERO
    all_rows_union_upper = sum(highs, ZERO)
    all_rows_intersection_lower = ZERO
    all_rows_intersection_upper = min(highs) if highs else ZERO

    groupwise_naive_base_sum = sum((group["population_base_sum"] for group in groups), ZERO)
    groupwise_union_lower_sum = sum((group["union_lower"] for group in groups), ZERO)
    groupwise_union_upper_sum = sum((group["union_upper"] for group in groups), ZERO)
    groupwise_intersection_lower_sum = sum((group["intersection_lower"] for group in groups), ZERO)
    groupwise_intersection_upper_sum = sum((group["intersection_upper"] for group in groups), ZERO)
    return {
        "group_count": len(groups),
        "member_count": len(all_members),
        "groupwise_naive_base_sum": groupwise_naive_base_sum,
        "groupwise_union_lower_sum": groupwise_union_lower_sum,
        "groupwise_union_upper_sum": groupwise_union_upper_sum,
        "groupwise_intersection_lower_sum": groupwise_intersection_lower_sum,
        "groupwise_intersection_upper_sum": groupwise_intersection_upper_sum,
        "groupwise_overcount_lower": max(ZERO, groupwise_naive_base_sum - groupwise_union_upper_sum),
        "groupwise_overcount_upper": max(ZERO, groupwise_naive_base_sum - groupwise_union_lower_sum),
        "all_rows_union_lower": all_rows_union_lower,
        "all_rows_union_upper": all_rows_union_upper,
        "all_rows_intersection_lower": all_rows_intersection_lower,
        "all_rows_intersection_upper": all_rows_intersection_upper,
    }


def member_json(member: Mapping[str, Any]) -> dict[str, Any]:
    top = member["top"]
    register = member["register"]
    return {
        "decision_rank": top.get("decision_rank", ""),
        "edition_target_id": top.get("edition_target_id", ""),
        "label": top.get("label", ""),
        "language_tag": top.get("language_tag", ""),
        "script": register.get("script", ""),
        "population_reference_year": top.get("population_reference_year", ""),
        "population_low": top.get("population_low", ""),
        "population_base": top.get("population_base", ""),
        "population_high": top.get("population_high", ""),
        "population_source_id": top.get("population_source_id", ""),
        "authorization_id": top.get("authorization_id", ""),
        "authorization_additivity_class": register.get("authorization_additivity_class", ""),
        "evidence_identity_id": top.get("evidence_identity_id", ""),
        "source_record_id": top.get("source_record_id", ""),
        "source_evidence_row_sha256": top.get("source_evidence_row_sha256", ""),
        "target_row_sha256": top.get("target_row_sha256", ""),
        "evidence_row_sha256": top.get("evidence_row_sha256", ""),
        "source_registry_row_hashes": top.get("source_registry_row_hashes", ""),
        "register_population_base": register.get("population_base", ""),
        "register_population_source_id": register.get("population_source_id", ""),
        "register_authorization_id": register.get("authorization_id", ""),
        "register_source_evidence_row_sha256": register.get("source_evidence_row_sha256", ""),
        "register_assessment": register.get("assessment", ""),
    }


def csv_member_row(
    group: Mapping[str, Any],
    member: Mapping[str, Any],
    member_index: int,
    portfolio: Mapping[str, Any],
) -> dict[str, str]:
    top = member["top"]
    register = member["register"]
    values: dict[str, Any] = {
        "record_type": "GROUP_MEMBER",
        "overlap_group": group["overlap_group"],
        "overlap_type": "probable_shared_persons",
        "scenario": "generic_no_common_universe",
        "crosswalk_status": "NONE_PROVEN",
        "rankability_status": "UNRANKED_WARNING_ONLY",
        "formula_version": "marginal-count-set-bounds-v1",
        "bound_unit": "persons",
        "member_index": str(member_index),
        "member_count": str(group["member_count"]),
        "decision_rank": top.get("decision_rank", ""),
        "edition_target_id": top.get("edition_target_id", ""),
        "label": top.get("label", ""),
        "language_tag": top.get("language_tag", ""),
        "script": register.get("script", ""),
        "population_reference_year": top.get("population_reference_year", ""),
        "population_low": top.get("population_low", ""),
        "population_base": top.get("population_base", ""),
        "population_high": top.get("population_high", ""),
        "population_source_id": top.get("population_source_id", ""),
        "authorization_id": top.get("authorization_id", ""),
        "authorization_additivity_class": register.get("authorization_additivity_class", ""),
        "evidence_identity_id": top.get("evidence_identity_id", ""),
        "source_record_id": top.get("source_record_id", ""),
        "source_evidence_row_sha256": top.get("source_evidence_row_sha256", ""),
        "target_row_sha256": top.get("target_row_sha256", ""),
        "evidence_row_sha256": top.get("evidence_row_sha256", ""),
        "source_registry_row_hashes": top.get("source_registry_row_hashes", ""),
        "register_population_base": register.get("population_base", ""),
        "register_population_source_id": register.get("population_source_id", ""),
        "register_authorization_id": register.get("authorization_id", ""),
        "register_source_evidence_row_sha256": register.get("source_evidence_row_sha256", ""),
        "register_assessment": register.get("assessment", ""),
        "group_population_low_sum": number_text(group["population_low_sum"]),
        "group_population_base_sum": number_text(group["population_base_sum"]),
        "group_population_high_sum": number_text(group["population_high_sum"]),
        "group_union_lower": number_text(group["union_lower"]),
        "group_union_upper": number_text(group["union_upper"]),
        "group_intersection_lower": number_text(group["intersection_lower"]),
        "group_intersection_upper": number_text(group["intersection_upper"]),
        "group_same_universe_ceiling_diagnostic_only": number_text(group["same_universe_ceiling_diagnostic_only"]),
        "group_union_lower_same_universe_diagnostic_only": number_text(group["union_lower_same_universe_diagnostic_only"]),
        "group_union_upper_same_universe_diagnostic_only": number_text(group["union_upper_same_universe_diagnostic_only"]),
        "group_intersection_lower_same_universe_diagnostic_only": number_text(group["intersection_lower_same_universe_diagnostic_only"]),
        "group_intersection_upper_same_universe_diagnostic_only": number_text(group["intersection_upper_same_universe_diagnostic_only"]),
        "group_naive_overcount_lower": number_text(group["naive_overcount_lower"]),
        "group_naive_overcount_upper": number_text(group["naive_overcount_upper"]),
        "portfolio_group_count": str(portfolio["group_count"]),
        "portfolio_member_count": str(portfolio["member_count"]),
        "portfolio_groupwise_naive_base_sum": number_text(portfolio["groupwise_naive_base_sum"]),
        "portfolio_groupwise_union_lower_sum": number_text(portfolio["groupwise_union_lower_sum"]),
        "portfolio_groupwise_union_upper_sum": number_text(portfolio["groupwise_union_upper_sum"]),
        "portfolio_groupwise_intersection_lower_sum": number_text(portfolio["groupwise_intersection_lower_sum"]),
        "portfolio_groupwise_intersection_upper_sum": number_text(portfolio["groupwise_intersection_upper_sum"]),
        "portfolio_groupwise_overcount_lower": number_text(portfolio["groupwise_overcount_lower"]),
        "portfolio_groupwise_overcount_upper": number_text(portfolio["groupwise_overcount_upper"]),
        "portfolio_all_rows_union_lower": number_text(portfolio["all_rows_union_lower"]),
        "portfolio_all_rows_union_upper": number_text(portfolio["all_rows_union_upper"]),
        "portfolio_all_rows_intersection_lower": number_text(portfolio["all_rows_intersection_lower"]),
        "portfolio_all_rows_intersection_upper": number_text(portfolio["all_rows_intersection_upper"]),
        "bound_method": "marginal_count_only_set_bounds; no_common_universe_ceiling_used",
        "standalone_rank_snapshot_sha256": portfolio["standalone_rank_snapshot_sha256"],
        "standalone_rank_unchanged": "true",
    }
    return {field: str(values.get(field, "")) for field in CSV_FIELDS}


def csv_summary_row(portfolio: Mapping[str, Any]) -> dict[str, str]:
    values: dict[str, Any] = {
        "record_type": "PORTFOLIO_SUMMARY",
        "overlap_group": "__PORTFOLIO__",
        "overlap_type": "portfolio_component_summary",
        "scenario": "generic_no_common_universe",
        "crosswalk_status": "NONE_PROVEN",
        "rankability_status": "UNRANKED_WARNING_ONLY",
        "formula_version": "marginal-count-set-bounds-v1",
        "bound_unit": "persons",
        "member_count": str(portfolio["member_count"]),
        "portfolio_group_count": str(portfolio["group_count"]),
        "portfolio_member_count": str(portfolio["member_count"]),
        "portfolio_groupwise_naive_base_sum": number_text(portfolio["groupwise_naive_base_sum"]),
        "portfolio_groupwise_union_lower_sum": number_text(portfolio["groupwise_union_lower_sum"]),
        "portfolio_groupwise_union_upper_sum": number_text(portfolio["groupwise_union_upper_sum"]),
        "portfolio_groupwise_intersection_lower_sum": number_text(portfolio["groupwise_intersection_lower_sum"]),
        "portfolio_groupwise_intersection_upper_sum": number_text(portfolio["groupwise_intersection_upper_sum"]),
        "portfolio_groupwise_overcount_lower": number_text(portfolio["groupwise_overcount_lower"]),
        "portfolio_groupwise_overcount_upper": number_text(portfolio["groupwise_overcount_upper"]),
        "portfolio_all_rows_union_lower": number_text(portfolio["all_rows_union_lower"]),
        "portfolio_all_rows_union_upper": number_text(portfolio["all_rows_union_upper"]),
        "portfolio_all_rows_intersection_lower": number_text(portfolio["all_rows_intersection_lower"]),
        "portfolio_all_rows_intersection_upper": number_text(portfolio["all_rows_intersection_upper"]),
        "bound_method": "marginal_count_only_set_bounds; groupwise_sums_are_not_unique_person_estimates",
        "standalone_rank_snapshot_sha256": portfolio["standalone_rank_snapshot_sha256"],
        "standalone_rank_unchanged": "true",
    }
    return {field: str(values.get(field, "")) for field in CSV_FIELDS}


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--top100", type=Path, default=DEFAULT_TOP100)
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--csv-output", type=Path, default=DEFAULT_CSV_OUTPUT)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    return parser.parse_args()


def build(args: argparse.Namespace) -> tuple[dict[str, Any], list[dict[str, str]]]:
    top = read_csv(args.top100)
    register = read_csv(args.register)
    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    if not isinstance(audit, dict):
        raise BoundsError("overlap audit JSON must be an object")

    require_columns(
        top,
        (
            "decision_rank",
            "edition_target_id",
            "label",
            "language_tag",
            "population_low",
            "population_base",
            "population_high",
            "population_reference_year",
            "population_source_id",
            "authorization_id",
            "evidence_identity_id",
            "source_record_id",
            "source_evidence_row_sha256",
            "target_row_sha256",
            "evidence_row_sha256",
            "source_registry_row_hashes",
        ),
        "Top-100",
    )
    require_columns(
        register,
        (
            "overlap_group",
            "decision_rank",
            "edition_target_id",
            "label",
            "language_tag",
            "script",
            "population_base",
            "population_reference_year",
            "population_source_id",
            "authorization_id",
            "authorization_additivity_class",
            "source_evidence_row_sha256",
            "assessment",
        ),
        "overlap register",
    )

    top_by_id: dict[str, dict[str, str]] = {}
    for row in top:
        edition_id = row.get("edition_target_id", "")
        if not edition_id:
            raise BoundsError("Top-100 row has empty edition_target_id")
        if edition_id in top_by_id:
            raise BoundsError(f"duplicate Top-100 edition_target_id: {edition_id}")
        top_by_id[edition_id] = row

    groups_by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in register:
        group_id = row.get("overlap_group", "")
        if not group_id:
            raise BoundsError("overlap register row has empty overlap_group")
        groups_by_id[group_id].append(row)
    groups = [build_group(group_id, groups_by_id[group_id], top_by_id) for group_id in sorted(groups_by_id)]
    all_member_ids = [
        member["top"]["edition_target_id"] for group in groups for member in group["members"]
    ]
    if len(all_member_ids) != len(set(all_member_ids)):
        raise BoundsError("an edition_target_id appears in more than one overlap group")
    portfolio = build_portfolio(groups)

    top_hash = sha256_file(args.top100)
    register_hash = sha256_file(args.register)
    audit_hash = sha256_file(args.audit)
    audit_inputs = audit.get("inputs", {}) if isinstance(audit.get("inputs", {}), dict) else {}
    audit_top_hash = str(audit_inputs.get("top100_sha256", "")).lower()
    if audit_top_hash and audit_top_hash != top_hash.lower():
        raise BoundsError(f"audit Top-100 hash mismatch: {audit_top_hash} != {top_hash}")

    expected_rows = audit.get("probable_shared_population_rows")
    expected_groups = audit.get("probable_shared_population_groups")
    if expected_rows is not None and int(expected_rows) != len(register):
        raise BoundsError(f"audit/register row count mismatch: {expected_rows} != {len(register)}")
    if expected_groups is not None and int(expected_groups) != len(groups):
        raise BoundsError(f"audit/register group count mismatch: {expected_groups} != {len(groups)}")

    # Reproduce the legacy warning quantity as a cross-check, without using it
    # as a bound or rank input.
    repeated_warning = sum(
        (group["population_base_sum"] - max(member["base"] for member in group["members"])
         for group in groups),
        ZERO,
    )
    expected_warning = audit.get("potentially_repeated_base_persons_upper_warning")
    if expected_warning is not None and Decimal(str(expected_warning)) != repeated_warning:
        raise BoundsError(f"audit repeated-base warning mismatch: {expected_warning} != {number_text(repeated_warning)}")

    # Standalone ranks are copied, never recomputed.  Keep an exact source
    # snapshot in JSON and verify every emitted member row against it.
    rank_snapshot = {row["edition_target_id"]: row.get("decision_rank", "") for row in top}
    overlap_ids = {
        member["top"]["edition_target_id"] for group in groups for member in group["members"]
    }
    rank_snapshot_hash = hashlib.sha256(canonical_json_bytes(rank_snapshot)).hexdigest()
    portfolio["standalone_rank_snapshot_sha256"] = rank_snapshot_hash
    csv_rows: list[dict[str, str]] = []
    for group in groups:
        for index, member in enumerate(group["members"], start=1):
            row = csv_member_row(group, member, index, portfolio)
            if row["decision_rank"] != rank_snapshot[row["edition_target_id"]]:
                raise BoundsError(f"standalone rank changed for {row['edition_target_id']}")
            csv_rows.append(row)
    csv_rows.append(csv_summary_row(portfolio))

    try:
        root = ROOT
        top_manifest = file_manifest(args.top100, root)
        register_manifest = file_manifest(args.register, root)
        audit_manifest = file_manifest(args.audit, root)
    except OSError as exc:
        raise BoundsError(f"cannot hash input manifest: {exc}") from exc

    document: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "BOUNDS_COMPLETE",
        "scope": "Exact current TOP100_NEEDS_ONLY_v3 rows named by PORTFOLIO_OVERLAP_REGISTER_v1; warning-level overlap groups only",
        "estimand": "Source-bound person-set cardinality diagnostics; not a unique-person or intervention-gain estimate",
        "inputs": {
            "top100": top_manifest,
            "overlap_register": register_manifest,
            "overlap_audit": audit_manifest,
        },
        "method": {
            "primary_bound_method": "marginal_count_only_set_bounds_no_ceiling",
            "frechet_count_refinement_requires": "an evidenced finite common-universe ceiling N",
            "union_lower": "max_i(population_low_i)",
            "union_upper": "sum_i(population_high_i)",
            "intersection_lower": "0",
            "intersection_upper": "min_i(population_high_i)",
            "same_universe_refinement": "max(max_i(L_i), sum_i(L_i)-(n-1)N) <= union <= min(N,sum_i(H_i)); N is not evidenced and is diagnostic-only",
            "same_universe_ceiling_policy": "record max_i(population_high_i) as candidate diagnostic ceiling; never use it to constrain primary bounds",
            "independence_assumption": False,
            "disjoint_crosswalk_used": False,
            "event_level_joint_model_used": False,
            "need_weighted_bounds_computed": False,
            "population_only_reason": "register contains source-bound population warnings; no compatible joint beneficiary event/crosswalk is supplied",
            "local_production_factor_used": False,
            "standalone_rank_recomputation": False,
        },
        "groups": [
            {
                "overlap_group": group["overlap_group"],
                "member_count": group["member_count"],
                "members": [member_json(member) for member in group["members"]],
                "population_low_sum": number_text(group["population_low_sum"]),
                "population_base_sum": number_text(group["population_base_sum"]),
                "population_high_sum": number_text(group["population_high_sum"]),
                "union_bounds": {"lower": number_text(group["union_lower"]), "upper": number_text(group["union_upper"])},
                "intersection_bounds": {"lower": number_text(group["intersection_lower"]), "upper": number_text(group["intersection_upper"])},
                "same_universe_ceiling_diagnostic_only": number_text(group["same_universe_ceiling_diagnostic_only"]),
                "same_universe_union_bounds_diagnostic_only": {
                    "lower": number_text(group["union_lower_same_universe_diagnostic_only"]),
                    "upper": number_text(group["union_upper_same_universe_diagnostic_only"]),
                },
                "same_universe_intersection_bounds_diagnostic_only": {
                    "lower": number_text(group["intersection_lower_same_universe_diagnostic_only"]),
                    "upper": number_text(group["intersection_upper_same_universe_diagnostic_only"]),
                },
                "naive_base_overcount_bounds": {
                    "lower": number_text(group["naive_overcount_lower"]),
                    "upper": number_text(group["naive_overcount_upper"]),
                },
                "bound_status": "CONSERVATIVE_MARGINAL_ONLY",
            }
            for group in groups
        ],
        "portfolio_summary": {
            "group_count": portfolio["group_count"],
            "member_count": portfolio["member_count"],
            "groupwise_naive_base_sum": number_text(portfolio["groupwise_naive_base_sum"]),
            "groupwise_union_lower_sum": number_text(portfolio["groupwise_union_lower_sum"]),
            "groupwise_union_upper_sum": number_text(portfolio["groupwise_union_upper_sum"]),
            "groupwise_intersection_lower_sum": number_text(portfolio["groupwise_intersection_lower_sum"]),
            "groupwise_intersection_upper_sum": number_text(portfolio["groupwise_intersection_upper_sum"]),
            "groupwise_overcount_bounds": {
                "lower": number_text(portfolio["groupwise_overcount_lower"]),
                "upper": number_text(portfolio["groupwise_overcount_upper"]),
            },
            "all_register_rows_union_bounds_diagnostic_only": {
                "lower": number_text(portfolio["all_rows_union_lower"]),
                "upper": number_text(portfolio["all_rows_union_upper"]),
            },
            "all_register_rows_intersection_bounds_diagnostic_only": {
                "lower": number_text(portfolio["all_rows_intersection_lower"]),
                "upper": number_text(portfolio["all_rows_intersection_upper"]),
            },
            "aggregation_note": "Groupwise sums are component diagnostics; warning groups are not asserted mutually disjoint and no value is a unique-person portfolio total.",
        },
        "standalone_rank_snapshot": rank_snapshot,
        "overlap_rank_snapshot": {key: rank_snapshot[key] for key in sorted(overlap_ids)},
        "standalone_rank_snapshot_sha256": rank_snapshot_hash,
        "checks": {
            "top100_rows": len(top),
            "register_rows": len(register),
            "register_groups": len(groups),
            "audit_counts_match": (
                (expected_rows is None or int(expected_rows) == len(register))
                and (expected_groups is None or int(expected_groups) == len(groups))
            ),
            "register_rows_join_top100": True,
            "register_source_ids_and_hashes_match_top100": True,
            "member_ids_unique_across_groups": True,
            "population_intervals_valid": True,
            "standalone_ranks_unchanged": True,
            "standalone_rank_snapshot_rows": len(rank_snapshot),
            "standalone_rank_snapshot_sha256": rank_snapshot_hash,
            "local_production_factor_used": False,
            "independence_assumed": False,
            "primary_bounds_use_inferred_ceiling": False,
            "deterministic_order": True,
        },
        "outputs": {
            "csv": {"path": display_path(args.csv_output, ROOT)},
            "json": {"path": display_path(args.json_output, ROOT)},
            "implementation": file_manifest(Path(__file__).resolve(), root),
        },
        "payload_sha256": hashlib.sha256(
            canonical_json_bytes(
                {"groups": document_groups_for_hash(groups), "portfolio": portfolio_for_hash(portfolio)}
            )
        ).hexdigest(),
    }
    return document, csv_rows


def document_groups_for_hash(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert Decimal-rich groups into a stable hash payload."""
    result: list[dict[str, Any]] = []
    for group in groups:
        result.append(
            {
                "overlap_group": group["overlap_group"],
                "member_ids": [member["top"]["edition_target_id"] for member in group["members"]],
                "population_low_sum": number_text(group["population_low_sum"]),
                "population_base_sum": number_text(group["population_base_sum"]),
                "population_high_sum": number_text(group["population_high_sum"]),
                "union_lower": number_text(group["union_lower"]),
                "union_upper": number_text(group["union_upper"]),
                "intersection_lower": number_text(group["intersection_lower"]),
                "intersection_upper": number_text(group["intersection_upper"]),
            }
        )
    return result


def portfolio_for_hash(portfolio: Mapping[str, Any]) -> dict[str, Any]:
    """Convert Decimal-rich portfolio totals into a stable hash payload."""
    return {
        key: (number_text(value) if isinstance(value, Decimal) else value)
        for key, value in sorted(portfolio.items())
    }


def main() -> int:
    args = parse_args()
    try:
        document, csv_rows = build(args)
        write_csv(args.csv_output, csv_rows)
        csv_manifest = file_manifest(args.csv_output, ROOT)
        document["outputs"]["csv"] = csv_manifest
        # Keep JSON key order stable and avoid timestamps or host-dependent
        # values.  Its own hash is intentionally reported externally because a
        # self-hash would be circular.
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_bytes(json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8") + b"\n")
        result = {
            "csv": file_manifest(args.csv_output, ROOT),
            "json": file_manifest(args.json_output, ROOT),
            "groups": document["portfolio_summary"]["group_count"],
            "members": document["portfolio_summary"]["member_count"],
            "payload_sha256": document["payload_sha256"],
        }
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (BoundsError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
