#!/usr/bin/env python3
"""Independent, bounded source-trace audit for the current needs Top-100.

The ranker and authorization builder are deliberately not imported here.  The
audit re-reads their persisted CSV/JSON projections and checks joins, hashes,
bound semantics, and source identity independently.  It is a QA artifact, not
another ranking implementation.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TOP100 = ROOT / "structured" / "TOP100_NEEDS_ONLY_v3.csv"
SCORE = ROOT / "structured" / "GLOBAL_TARGET_SCORE_TABLE_v3.csv"
AUTH = ROOT / "structured" / "EVIDENCE_AUTHORIZATION_v1.csv"
AUTHORITY = ROOT / "structured" / "SUCCESSOR_EDITION_TARGET_AUTHORITY_v3.csv"
CANON = ROOT / "structured" / "canonical_universe_successor_v2.json"
OUT = ROOT / "qa" / "TOP100_SOURCE_TRACE_AUDIT_v2.json"
REPORT = ROOT / "agent_reports" / "TOP100_SOURCE_TRACE_AUDIT_v2.md"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def persisted_hash(row: dict[str, str], fields: list[str]) -> str:
    projected = {
        field: "" if row.get(field) is None else str(row.get(field, ""))
        for field in fields
        if field != "evidence_row_sha256"
    }
    return hashlib.sha256(canonical_json(projected).encode("utf-8")).hexdigest()


def present(value: Any) -> bool:
    return value is not None and str(value) != ""


def number(value: Any) -> float | None:
    if not present(value):
        return None
    try:
        n = float(str(value).replace(",", ""))
    except ValueError:
        return None
    return n if n >= 0 else None


def bound_assertion(row: dict[str, str]) -> tuple[bool, str]:
    kind = str(row.get("population_bound_type", "")).upper()
    low, base, high = row.get("population_low_persons", ""), row.get("population_base_persons", ""), row.get("population_high_persons", "")
    nlow, nhigh = row.get("normalized_population_low_persons", ""), row.get("normalized_population_high_persons", "")
    if kind == "POINT":
        ok = present(base) and str(nlow) == str(base) and str(nhigh) == str(base)
    elif kind == "INTERVAL":
        ok = present(low) and present(high) and str(nlow) == str(low) and str(nhigh) == str(high)
    elif kind == "LOWER_BOUND":
        ok = present(low) and not present(high) and str(nlow) == str(low) and not present(nhigh)
    elif kind == "UPPER_BOUND":
        ok = present(high) and not present(low) and not present(nlow) and str(nhigh) == str(high)
    elif kind == "NONE":
        ok = not any(present(x) for x in (low, base, high, nlow, nhigh))
    else:
        ok = False
    return ok, kind


def main() -> None:
    top = read_csv(TOP100)
    score = read_csv(SCORE)
    auth = read_csv(AUTH)
    authority = read_csv(AUTHORITY)
    canon = json.loads(CANON.read_text(encoding="utf-8"))
    auth_fields = list(csv.DictReader(AUTH.open("r", encoding="utf-8-sig", newline="")).fieldnames or [])
    auth_by_id = {row.get("authorization_id", ""): row for row in auth}
    authority_by_id = {row.get("edition_target_id", ""): row for row in authority}
    score_ids = {row.get("edition_target_id", "") for row in score}
    failures: list[str] = []
    warnings: list[str] = []

    ranks = [int(row.get("decision_rank", "0")) for row in top if row.get("decision_rank", "").isdigit()]
    if ranks != list(range(1, 101)):
        failures.append(f"Top100 ranks are not exactly 1..100: first/last={ranks[:3]}/{ranks[-3:]}")
    top_ids = [row.get("edition_target_id", "") for row in top]
    if len(top_ids) != len(set(top_ids)):
        failures.append("Top100 edition_target_id values are duplicated")

    shape_counts: Counter[str] = Counter()
    interval_rows: list[str] = []
    auth_hash_failures: list[str] = []
    target_hash_failures: list[str] = []
    join_failures: list[str] = []
    forbidden_terms = ("user_local", "prior_translation", "sunk_compute", "project_convenience", "personal_work", "local_file_inventory")
    for row in top:
        eid = row.get("edition_target_id", "")
        aid = row.get("authorization_id", "")
        ar = auth_by_id.get(aid)
        tr = authority_by_id.get(eid)
        if eid not in score_ids:
            join_failures.append(f"{eid}: absent from score table")
        if not ar:
            join_failures.append(f"{eid}: authorization_id {aid} absent")
        else:
            if ar.get("authorization_status") != "ADMIT":
                join_failures.append(f"{eid}: authorization status {ar.get('authorization_status')!r}")
            if ar.get("edition_target_id") != eid:
                join_failures.append(f"{eid}: authorization target mismatch")
            if row.get("evidence_row_sha256") != ar.get("evidence_row_sha256"):
                join_failures.append(f"{eid}: persisted evidence row hash differs from authorization")
            if persisted_hash(ar, auth_fields) != ar.get("evidence_row_sha256"):
                auth_hash_failures.append(aid)
            ok, kind = bound_assertion(ar)
            shape_counts[kind] += 1
            if not ok:
                failures.append(f"{aid}: bound normalization assertion failed ({kind})")
            if kind == "INTERVAL":
                interval_rows.append(eid)
                if ar.get("authorization_tier", "").startswith("A_"):
                    failures.append(f"{eid}: non-degenerate interval has A tier")
                if ar.get("population_rankability_status") != "INTERVAL_ONLY":
                    failures.append(f"{eid}: interval is not labelled INTERVAL_ONLY")
            if ar.get("population_rankability_status") == "POINT_DISTRIBUTION" and kind == "INTERVAL":
                failures.append(f"{eid}: source interval still labelled POINT_DISTRIBUTION")
        if not tr:
            join_failures.append(f"{eid}: absent from target authority")
        elif row.get("target_row_sha256") != tr.get("row_sha256"):
            target_hash_failures.append(eid)
        blob = json.dumps(row, ensure_ascii=False).lower()
        for term in forbidden_terms:
            if term in blob:
                failures.append(f"{eid}: forbidden predictor term {term}")

    if join_failures:
        failures.extend(join_failures)
    if auth_hash_failures:
        failures.append(f"{len(auth_hash_failures)} authorization persisted-row hashes failed")
    if target_hash_failures:
        failures.append(f"{len(target_hash_failures)} target authority row hashes failed")
    # A source hash is not independently recomputed here when the raw source
    # object is not uniquely keyed by the authorization row; its presence and
    # the authorization CSV's own round-trip hash are still required.
    missing_source_hash = [row.get("edition_target_id", "") for row in top if not row.get("source_evidence_row_sha256", "")]
    if missing_source_hash:
        failures.append(f"{len(missing_source_hash)} Top100 rows lack source_evidence_row_sha256")

    if len(top) != 100:
        failures.append(f"Top100 row count is {len(top)}, expected 100")
    if len(score_ids) != len(score):
        failures.append("score target IDs are not unique")
    if any(kind in {"LOWER_BOUND", "UPPER_BOUND", "NONE", "MIXED"} for kind in shape_counts):
        warnings.append("Top100 contains no admitted one-sided/none rows by design; any such shape would require exclusion")

    payload = {
        "schema": "interlanguage/top100-source-trace-audit/2.0.0",
        "status": "PASS" if not failures else "FAIL",
        "scope": "current persisted needs-only Top100 after authorization bound/OER repairs; independent read-only join and semantic audit",
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
            for path in (TOP100, SCORE, AUTH, AUTHORITY, CANON)
        },
        "counts": {
            "top100_rows": len(top),
            "top100_unique_targets": len(set(top_ids)),
            "score_rows": len(score),
            "authorization_rows": len(auth),
            "interval_rows_in_top100": len(interval_rows),
            "bound_shapes_in_top100": dict(shape_counts),
        },
        "checks": {
            "ranks_exact_1_to_100": ranks == list(range(1, 101)),
            "target_ids_unique": len(top_ids) == len(set(top_ids)),
            "all_score_joins": not any("absent from score" in x for x in join_failures),
            "all_admitted_authorization_joins": not any("authorization" in x for x in join_failures),
            "authorization_persisted_hashes": not auth_hash_failures,
            "target_authority_hashes": not target_hash_failures,
            "bound_normalization": not any("bound normalization" in x for x in failures),
            "interval_status_and_tier": not any("interval" in x and ("tier" in x or "labelled" in x) for x in failures),
            "source_evidence_hash_presence": not missing_source_hash,
            "forbidden_predictor_scan": not any("forbidden predictor" in x for x in failures),
        },
        "interval_target_ids": interval_rows,
        "warnings": warnings,
        "failures": failures,
        "interpretation": [
            "A source POINT may have blank raw low/high; normalized endpoints are explicit scoring adapters and are not source claims.",
            "A non-degenerate source range is reported as INTERVAL_ONLY/B interval tier; it is not silently collapsed to a point.",
            "The audit validates identity and persisted projections, not the truth of the underlying external source claims.",
            "Standalone ranks remain model-conditional; probable shared populations remain non-additive in portfolio use.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Top-100 source-trace audit v2",
        "",
        f"Status: **{payload['status']}**.",
        "",
        "This is an independent read-only audit of the persisted Top-100, score table, authorization ledger, and target authority. It does not recompute ranks.",
        "",
        f"- Top-100 rows/unique targets: {len(top)}/{len(set(top_ids))}; exact ranks 1–100: {payload['checks']['ranks_exact_1_to_100']}",
        f"- Authorization persisted-row hashes valid: {payload['checks']['authorization_persisted_hashes']}; target row hashes valid: {payload['checks']['target_authority_hashes']}",
        f"- Bound shapes in Top-100: {dict(shape_counts)}; non-degenerate interval rows: {len(interval_rows)}",
        f"- Failures: {len(failures)}",
        "",
        "The JSON artifact records exact input hashes, row-level failure labels, and the distinction between raw source bounds and normalized scoring bounds.",
    ]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
