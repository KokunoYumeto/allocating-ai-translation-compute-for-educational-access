from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STRUCTURED = ROOT / "structured"

CANDIDATE_FIELDS = [
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
]

SOURCE_FIELDS = [
    "source_id",
    "title",
    "organization",
    "year",
    "url",
    "access_date",
    "claim_scope",
]

NUMERIC_TRIPLES = [
    ("population_low", "population_base", "population_high"),
    (
        "academic_language_overlap_low",
        "academic_language_overlap_base",
        "academic_language_overlap_high",
    ),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def read_csv(path: Path, expected: list[str]) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != expected:
            raise ValueError(
                f"{path.name}: schema mismatch\nexpected={expected}\nactual={reader.fieldnames}"
            )
        return [{key: (value or "").strip() for key, value in row.items()} for row in reader]


def parse_number(value: str, field: str, candidate_id: str) -> float | None:
    if value == "":
        return None
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"{candidate_id}: {field} is not numeric: {value!r}") from exc


def normalized(value: str) -> str:
    return " ".join(value.casefold().split())


def semantic_key(row: dict[str, str]) -> str:
    parts = [
        row["language_tag"],
        row["script_orthography"],
        row["territory_community"],
        row["modality"],
        row["learner_stage_scope"],
    ]
    return "|".join(normalized(part) for part in parts)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    candidate_files = sorted(STRUCTURED.glob("*_candidates.csv"))
    if not candidate_files:
        raise SystemExit("No structured/*_candidates.csv files are ready")

    # Only ingest the source table paired with each candidate table.  The
    # structured directory also contains other evidence tables whose names end
    # in ``_sources.csv`` (for example standardized-compute sources) but whose
    # schemas and dependency graphs are intentionally different.
    source_files: list[Path] = []
    missing_source_pairs: list[str] = []
    for candidate_path in candidate_files:
        prefix = candidate_path.name[: -len("_candidates.csv")]
        source_path = STRUCTURED / f"{prefix}_sources.csv"
        if not source_path.exists():
            missing_source_pairs.append(source_path.name)
        else:
            source_files.append(source_path)
    if missing_source_pairs:
        raise SystemExit(
            "Missing paired candidate source tables: " + ", ".join(missing_source_pairs)
        )

    candidates: list[dict[str, str]] = []
    sources: list[dict[str, str]] = []
    input_files = []

    for path in candidate_files:
        rows = read_csv(path, CANDIDATE_FIELDS)
        for row in rows:
            row["origin_file"] = path.name
            row["semantic_key"] = semantic_key(row)
        candidates.extend(rows)
        input_files.append(
            {"path": path.name, "kind": "candidate", "rows": len(rows), "sha256": sha256(path)}
        )

    for path in source_files:
        rows = read_csv(path, SOURCE_FIELDS)
        for row in rows:
            row["origin_file"] = path.name
        sources.extend(rows)
        input_files.append(
            {"path": path.name, "kind": "source", "rows": len(rows), "sha256": sha256(path)}
        )

    errors: list[str] = []
    warnings: list[str] = []
    missing_counts: Counter[str] = Counter()
    candidate_ids: defaultdict[str, list[str]] = defaultdict(list)
    semantic_groups: defaultdict[str, list[str]] = defaultdict(list)

    for row in candidates:
        cid = row["candidate_id"]
        if not cid:
            errors.append(f"{row['origin_file']}: blank candidate_id")
            continue
        candidate_ids[cid].append(row["origin_file"])
        semantic_groups[row["semantic_key"]].append(cid)

        for field in (
            "target_label",
            "language_variety",
            "language_tag",
            "script_orthography",
            "territory_community",
            "modality",
            "learner_stage_scope",
            "population_unit",
            "population_definition",
            "evidence_confidence",
        ):
            if not row[field]:
                missing_counts[field] += 1

        for low_field, base_field, high_field in NUMERIC_TRIPLES:
            low = parse_number(row[low_field], low_field, cid)
            base = parse_number(row[base_field], base_field, cid)
            high = parse_number(row[high_field], high_field, cid)
            present = [value for value in (low, base, high) if value is not None]
            if present and any(value < 0 for value in present):
                errors.append(f"{cid}: negative value in {low_field}/{base_field}/{high_field}")
            if low is not None and base is not None and low > base:
                errors.append(f"{cid}: {low_field} exceeds {base_field}")
            if base is not None and high is not None and base > high:
                errors.append(f"{cid}: {base_field} exceeds {high_field}")
            if low is not None and high is not None and low > high:
                errors.append(f"{cid}: {low_field} exceeds {high_field}")

        if any(row[field] for field in ("population_low", "population_base", "population_high")):
            for required in (
                "population_unit",
                "population_definition",
                "population_reference_year",
                "population_source_id",
                "population_source_url",
            ):
                if not row[required]:
                    errors.append(f"{cid}: population supplied but {required} is blank")

        if row["rankable"].casefold() not in {"true", "false", "yes", "no", "1", "0"}:
            warnings.append(f"{cid}: rankable value is not a recognized boolean: {row['rankable']!r}")

    duplicate_ids = {key: value for key, value in candidate_ids.items() if len(value) > 1}
    for cid, origins in duplicate_ids.items():
        errors.append(f"duplicate candidate_id {cid}: {origins}")

    duplicate_rows: list[dict[str, object]] = []
    for key, ids in semantic_groups.items():
        unique_ids = sorted(set(ids))
        if len(unique_ids) > 1:
            duplicate_rows.append(
                {
                    "semantic_key": key,
                    "candidate_count": len(unique_ids),
                    "candidate_ids": ";".join(unique_ids),
                    "resolution_status": "requires_source_reconciliation",
                }
            )

    source_id_groups: defaultdict[str, list[str]] = defaultdict(list)
    for row in sources:
        source_id_groups[row["source_id"]].append(row["origin_file"])
        if not row["source_id"] or not row["url"]:
            errors.append(f"{row['origin_file']}: source row missing source_id or url")
    duplicate_source_ids = {
        key: value for key, value in source_id_groups.items() if key and len(value) > 1
    }
    for sid, origins in duplicate_source_ids.items():
        warnings.append(f"duplicate source_id {sid}: {origins}; reconcile before canonical merge")

    source_urls_by_id: defaultdict[str, set[str]] = defaultdict(set)
    for row in sources:
        if row["source_id"]:
            source_urls_by_id[row["source_id"]].add(row["url"])
    for row in candidates:
        source_id = row["population_source_id"]
        source_url = row["population_source_url"]
        if not source_id:
            continue
        if source_id not in source_urls_by_id:
            errors.append(
                f"{row['candidate_id']}: population_source_id {source_id!r} has no paired source row"
            )
        elif source_url and source_url not in source_urls_by_id[source_id]:
            errors.append(
                f"{row['candidate_id']}: population_source_url does not match source row for {source_id!r}"
            )

    candidate_output_fields = CANDIDATE_FIELDS + ["origin_file", "semantic_key"]
    source_output_fields = SOURCE_FIELDS + ["origin_file"]
    write_csv(ROOT / "CANDIDATE_UNIVERSE_RAW.csv", candidate_output_fields, candidates)
    write_csv(ROOT / "PUBLIC_SOURCES_RAW.csv", source_output_fields, sources)
    write_csv(
        ROOT / "CANDIDATE_DUPLICATE_AUDIT.csv",
        ["semantic_key", "candidate_count", "candidate_ids", "resolution_status"],
        duplicate_rows,
    )

    validation = {
        "schema": "interlanguage/global-educational-access-candidate-validation/1.0.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "candidate_rows": len(candidates),
        "source_rows": len(sources),
        "candidate_files": len(candidate_files),
        "source_files": len(source_files),
        "unique_candidate_ids": len(candidate_ids),
        "semantic_duplicate_groups": len(duplicate_rows),
        "duplicate_source_ids": duplicate_source_ids,
        "missing_field_counts": dict(sorted(missing_counts.items())),
        "errors": errors,
        "warnings": warnings,
        "inputs": input_files,
        "outputs": {},
    }
    for filename in (
        "CANDIDATE_UNIVERSE_RAW.csv",
        "PUBLIC_SOURCES_RAW.csv",
        "CANDIDATE_DUPLICATE_AUDIT.csv",
    ):
        path = ROOT / filename
        validation["outputs"][filename] = {
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }

    validation_path = ROOT / "CANDIDATE_VALIDATION.json"
    validation_path.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "candidate_rows": len(candidates),
                "source_rows": len(sources),
                "semantic_duplicate_groups": len(duplicate_rows),
                "errors": len(errors),
                "warnings": len(warnings),
            }
        )
    )
    if errors:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
