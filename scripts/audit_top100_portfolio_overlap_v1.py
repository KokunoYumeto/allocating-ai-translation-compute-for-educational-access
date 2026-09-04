#!/usr/bin/env python3
"""Bounded non-additivity audit for the current needs-only Top-100.

This does not change the intervention ranking.  It identifies rows whose
source-bound person denominators are likely the same people under alternate
script/orthography or duplicate identity tags, so a later portfolio order can
use union bounds instead of summing standalone scores.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOP100 = ROOT / "structured" / "TOP100_NEEDS_ONLY_v3.csv"
AUTH = ROOT / "structured" / "EVIDENCE_AUTHORIZATION_v1.csv"
OUT = ROOT / "structured" / "PORTFOLIO_OVERLAP_REGISTER_v1.csv"
QA = ROOT / "qa" / "PORTFOLIO_OVERLAP_AUDIT_v1.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (text or "").casefold())


def digest_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    top = read_csv(TOP100)
    auth = read_csv(AUTH)
    auth_by_id = {r.get("authorization_id", ""): r for r in auth}
    # Group only by a deliberately conservative signature.  Matching label,
    # year, territory suffix and exact base is a warning signal, not proof of
    # identity; the output retains both source IDs for later adjudication.
    groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in top:
        tag = row.get("language_tag", "")
        territory = tag.rsplit("-", 1)[-1] if "-" in tag else ""
        key = (
            norm(row.get("label", "")),
            row.get("population_reference_year", ""),
            territory,
        )
        groups[key].append(row)

    out: list[dict[str, str]] = []
    duplicate_groups = 0
    duplicate_rows = 0
    potentially_repeated_base = 0.0
    for key, rows in sorted(groups.items()):
        if len(rows) < 2:
            continue
        # Require equal positive base values before calling the group a likely
        # shared population.  Different bases remain visible but are not
        # mechanically collapsed by this audit.
        bases = {row.get("population_base", "") for row in rows}
        positive_equal = len(bases) == 1 and next(iter(bases), "") not in {"", "0", "0.000000"}
        if not positive_equal:
            continue
        duplicate_groups += 1
        duplicate_rows += len(rows)
        values = [float(row["population_base"]) for row in rows]
        potentially_repeated_base += sum(values) - max(values)
        group_id = "probable-shared-persons:" + hashlib.sha256("|".join(key).encode("utf-8")).hexdigest()[:16]
        for row in rows:
            aid = row.get("authorization_id", "")
            ar = auth_by_id.get(aid, {})
            out.append(
                {
                    "overlap_group": group_id,
                    "decision_rank": row.get("decision_rank", ""),
                    "edition_target_id": row.get("edition_target_id", ""),
                    "label": row.get("label", ""),
                    "language_tag": row.get("language_tag", ""),
                    "script": row.get("script", ""),
                    "population_base": row.get("population_base", ""),
                    "population_reference_year": row.get("population_reference_year", ""),
                    "population_source_id": row.get("population_source_id", ""),
                    "authorization_id": aid,
                    "authorization_additivity_class": ar.get("additivity_class", ""),
                    "source_evidence_row_sha256": row.get("source_evidence_row_sha256", ""),
                    "assessment": "probable_shared_population; retain as separate script/edition interventions; do not sum in a portfolio without a disjoint crosswalk",
                }
            )

    # Source-declared multi-language response universes can overlap even when
    # their language labels and marginal counts differ.  The authorization
    # layer assigns a shared overlap_group only when the source construct
    # explicitly permits or reports overlapping language responses.  Keep the
    # standalone ranks, but expose the portfolio non-additivity.
    explicit_groups: dict[str, list[tuple[dict[str, str], dict[str, str]]]] = defaultdict(list)
    for row in top:
        ar = auth_by_id.get(row.get("authorization_id", ""), {})
        overlap_group = ar.get("overlap_group", "")
        source_record_id = ar.get("source_record_id", "")
        if overlap_group and overlap_group != source_record_id:
            explicit_groups[overlap_group].append((row, ar))

    for overlap_group, members in sorted(explicit_groups.items()):
        if len(members) < 2:
            continue
        duplicate_groups += 1
        duplicate_rows += len(members)
        bases = [float(row["population_base"]) for row, _ in members]
        potentially_repeated_base += max(0.0, sum(bases) - max(bases))
        group_id = "source-declared-overlap:" + hashlib.sha256(
            overlap_group.encode("utf-8")
        ).hexdigest()[:16]
        for row, ar in members:
            out.append(
                {
                    "overlap_group": group_id,
                    "decision_rank": row.get("decision_rank", ""),
                    "edition_target_id": row.get("edition_target_id", ""),
                    "label": row.get("label", ""),
                    "language_tag": row.get("language_tag", ""),
                    "script": row.get("script", ""),
                    "population_base": row.get("population_base", ""),
                    "population_reference_year": row.get("population_reference_year", ""),
                    "population_source_id": row.get("population_source_id", ""),
                    "authorization_id": row.get("authorization_id", ""),
                    "authorization_additivity_class": ar.get("additivity_class", ""),
                    "source_evidence_row_sha256": row.get("source_evidence_row_sha256", ""),
                    "assessment": "source_declared_overlapping_language_response_universe; retain standalone ranks; do not sum marginal language counts as unique people",
                }
            )

    fields = list(out[0]) if out else [
        "overlap_group", "decision_rank", "edition_target_id", "label", "language_tag", "script",
        "population_base", "population_reference_year", "population_source_id", "authorization_id",
        "authorization_additivity_class", "source_evidence_row_sha256", "assessment",
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out)

    payload = {
        "schema": "interlanguage/portfolio-overlap-audit/1.0.0",
        "status": "AUDIT_COMPLETE",
        "scope": "TOP100_NEEDS_ONLY_v3 exact current file; warning-level signature audit only",
        "inputs": {
            "top100_path": str(TOP100.relative_to(ROOT)),
            "top100_sha256": digest_bytes(TOP100),
            "authorization_path": str(AUTH.relative_to(ROOT)),
            "authorization_sha256": digest_bytes(AUTH),
            "top100_rows": len(top),
        },
        "probable_shared_population_groups": duplicate_groups,
        "probable_shared_population_rows": duplicate_rows,
        "potentially_repeated_base_persons_upper_warning": potentially_repeated_base,
        "register_path": str(OUT.relative_to(ROOT)),
        "register_rows": len(out),
        "interpretation": [
            "A matching signature is not proof that every person is identical; it is a conservative non-additivity warning.",
            "Standalone intervention ranks are unchanged.",
            "Portfolio aggregation must use explicit union/intersection bounds or a disjoint crosswalk.",
            "No human review is required to retain this warning or continue deterministic paper work.",
        ],
    }
    QA.parent.mkdir(parents=True, exist_ok=True)
    QA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"register": str(OUT), "qa": str(QA), **payload}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
