#!/usr/bin/env python3
"""Audit the heterogeneous pre-canonical candidate evidence without ranking it.

This script deliberately treats every source row as evidence, not as a distinct
language target.  Its main purpose is to expose repeated denominators, missing
provenance, incompatible estimate triplets, and very-large population rows before
the canonical universe is frozen.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]

CSV_INPUTS = (
    "structured/indonesia_candidates.csv",
    "structured/china_candidates.csv",
    "structured/south_asia_candidates.csv",
    "structured/global_omission_candidates.csv",
    "structured/accessibility_candidates.csv",
)

JSON_INPUTS = (
    "structured/africa_mapping_proposal.json",
    "structured/americas_arctic_mapping.json",
    "structured/oceania_indian_ocean_mapping_proposal.json",
    "structured/southeast_asia_mapping_proposal.json",
    "structured/japan_mapping_proposal.json",
)

EXPECTED_COLUMNS = (
    "candidate_id",
    "target_label",
    "language_variety",
    "language_tag",
    "script_orthography",
    "territory_community",
    "modality",
    "learner_stage_scope",
    "population_low",
    "population_base",
    "population_high",
    "population_unit",
    "population_definition",
    "population_reference_year",
    "population_source_id",
    "population_source_url",
    "academic_language_overlap_low",
    "academic_language_overlap_base",
    "academic_language_overlap_high",
    "overlap_definition",
    "baseline_access_status",
    "evidence_confidence",
    "rankable",
    "notes",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def as_number(value: Any) -> float | None:
    text = clean(value).replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def is_rankable(value: Any) -> bool:
    return clean(value).casefold() in {"1", "true", "yes", "y", "rankable"}


def header_from_json(payload: dict[str, Any]) -> list[str]:
    for key in ("candidate_header", "requested_candidate_header", "candidate_fields"):
        value = payload.get(key)
        if isinstance(value, list) and value:
            return [clean(item) for item in value]
        if isinstance(value, str) and value.strip():
            return [part.strip() for part in value.split("|")]
    return list(EXPECTED_COLUMNS)


def read_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def read_json_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    candidates = payload.get("candidates", [])
    header = header_from_json(payload)
    result: list[dict[str, Any]] = []
    for row in candidates:
        if isinstance(row, dict):
            result.append(row)
        elif isinstance(row, list):
            if len(row) != len(header):
                raise ValueError(
                    f"{path}: candidate has {len(row)} cells but header has {len(header)}"
                )
            result.append(dict(zip(header, row)))
        else:
            raise TypeError(f"{path}: unsupported candidate row type {type(row).__name__}")
    return result


def population_triplet(row: dict[str, Any]) -> tuple[float | None, float | None, float | None]:
    return (
        as_number(row.get("population_low")),
        as_number(row.get("population_base")),
        as_number(row.get("population_high")),
    )


def iter_loaded() -> Iterable[tuple[str, Path, list[dict[str, Any]]]]:
    for relative in CSV_INPUTS:
        path = ROOT / relative
        yield relative, path, read_csv_rows(path)
    for relative in JSON_INPUTS:
        path = ROOT / relative
        yield relative, path, read_json_rows(path)


def main() -> None:
    loaded = list(iter_loaded())
    all_rows: list[dict[str, Any]] = []
    input_files: list[dict[str, Any]] = []
    for relative, path, rows in loaded:
        input_files.append(
            {
                "path": str(path),
                "relative_path": relative,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "candidate_rows": len(rows),
            }
        )
        for source_row_number, original in enumerate(rows, start=2):
            row = {key: clean(value) for key, value in original.items()}
            row["_input_file"] = relative
            row["_source_row_number"] = source_row_number
            all_rows.append(row)

    ids = [row.get("candidate_id", "") for row in all_rows]
    duplicate_ids = {
        candidate_id: count
        for candidate_id, count in sorted(Counter(ids).items())
        if candidate_id and count > 1
    }

    rankable_rows = [row for row in all_rows if is_rankable(row.get("rankable"))]
    rankable_missing_population = []
    rankable_missing_source = []
    rankable_missing_year = []
    invalid_triplets = []
    large_population_rows = []
    denominator_groups: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)

    for row in all_rows:
        low, base, high = population_triplet(row)
        numeric = [value for value in (low, base, high) if value is not None]
        ref = {
            "candidate_id": row.get("candidate_id", ""),
            "target_label": row.get("target_label", ""),
            "language_tag": row.get("language_tag", ""),
            "territory_community": row.get("territory_community", ""),
            "population_low": low,
            "population_base": base,
            "population_high": high,
            "population_unit": row.get("population_unit", ""),
            "population_definition": row.get("population_definition", ""),
            "population_reference_year": row.get("population_reference_year", ""),
            "population_source_id": row.get("population_source_id", ""),
            "population_source_url": row.get("population_source_url", ""),
            "input_file": row["_input_file"],
            "source_row_number": row["_source_row_number"],
        }
        if is_rankable(row.get("rankable")):
            if not numeric:
                rankable_missing_population.append(ref)
            if not row.get("population_source_id") or not row.get("population_source_url"):
                rankable_missing_source.append(ref)
            if not row.get("population_reference_year"):
                rankable_missing_year.append(ref)

        if low is not None and base is not None and low > base:
            invalid_triplets.append({**ref, "reason": "population_low_gt_population_base"})
        if base is not None and high is not None and base > high:
            invalid_triplets.append({**ref, "reason": "population_base_gt_population_high"})
        if low is not None and high is not None and low > high:
            invalid_triplets.append({**ref, "reason": "population_low_gt_population_high"})

        if numeric and max(numeric) >= 100_000_000:
            large_population_rows.append(ref)

        if numeric:
            key = (
                row.get("population_source_id", ""),
                row.get("population_reference_year", ""),
                row.get("population_unit", ""),
                row.get("population_definition", ""),
                clean(low),
                clean(base),
                clean(high),
            )
            denominator_groups[key].append(ref)

    repeated_denominators = []
    for key, members in denominator_groups.items():
        if len(members) <= 1:
            continue
        repeated_denominators.append(
            {
                "population_source_id": key[0],
                "population_reference_year": key[1],
                "population_unit": key[2],
                "population_definition": key[3],
                "population_low": key[4],
                "population_base": key[5],
                "population_high": key[6],
                "row_count": len(members),
                "candidate_ids": sorted(member["candidate_id"] for member in members),
                "rule": "Shared denominator evidence; these rows are not additive and do not imply distinct beneficiaries.",
            }
        )
    repeated_denominators.sort(key=lambda item: (-item["row_count"], item["population_source_id"]))

    result = {
        "schema": "global-educational-access/raw-candidate-evidence-audit/1.0.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Pre-canonical evidence audit only; this artifact is not a ranking or a count of distinct language targets.",
        "guardrails": [
            "Every input row is evidence, not necessarily a unique language or beneficiary population.",
            "Repeated denominators must be assigned once to a mutually exclusive canonical stratum before scoring.",
            "Population measure classes remain separate and are not silently converted.",
            "No local project, prior translation, completion, reuse, readiness, or sunk-compute field is read.",
        ],
        "input_files": input_files,
        "summary": {
            "input_file_count": len(input_files),
            "raw_candidate_row_count": len(all_rows),
            "rankable_flag_row_count": len(rankable_rows),
            "unique_nonblank_candidate_id_count": len(set(item for item in ids if item)),
            "duplicate_candidate_id_count": len(duplicate_ids),
            "rankable_missing_population_count": len(rankable_missing_population),
            "rankable_missing_source_count": len(rankable_missing_source),
            "rankable_missing_year_count": len(rankable_missing_year),
            "invalid_population_triplet_count": len(invalid_triplets),
            "repeated_denominator_group_count": len(repeated_denominators),
            "rows_with_any_population_estimate_ge_100m": len(large_population_rows),
        },
        "duplicate_candidate_ids": duplicate_ids,
        "rankable_missing_population": rankable_missing_population,
        "rankable_missing_source": rankable_missing_source,
        "rankable_missing_year": rankable_missing_year,
        "invalid_population_triplets": invalid_triplets,
        "repeated_denominators": repeated_denominators,
        "large_population_rows": sorted(
            large_population_rows,
            key=lambda item: -max(
                value
                for value in (
                    item["population_low"],
                    item["population_base"],
                    item["population_high"],
                )
                if value is not None
            ),
        ),
    }

    output_json = ROOT / "qa" / "RAW_CANDIDATE_EVIDENCE_AUDIT.json"
    output_md = ROOT / "qa" / "RAW_CANDIDATE_EVIDENCE_AUDIT.md"
    output_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary = result["summary"]
    lines = [
        "# Raw candidate evidence audit",
        "",
        "This is a pre-canonical evidence audit, not a ranking and not a count of distinct languages or beneficiaries.",
        "",
        "## Counts",
        "",
    ]
    for key, value in summary.items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(
        [
            "",
            "## Release gate",
            "",
            "The canonical universe may not be ranked until every repeated denominator is assigned once to a compatible, mutually exclusive stratum and every rankable row has an evidenced population status, source, and reference year (or an explicit partial-identification status).",
            "",
            "## Machine-readable details",
            "",
            f"See `{output_json.name}`. SHA-256: `{sha256(output_json)}`.",
            "",
        ]
    )
    output_md.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({
        "json": str(output_json),
        "json_sha256": sha256(output_json),
        "markdown": str(output_md),
        "markdown_sha256": sha256(output_md),
        "summary": summary,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
