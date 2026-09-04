#!/usr/bin/env python3
"""Audit source identity and candidate-to-source linkage before canonicalization."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[1]

CSV_PAIRS = (
    ("structured/indonesia_candidates.csv", "structured/indonesia_sources.csv"),
    ("structured/china_candidates.csv", "structured/china_sources.csv"),
    ("structured/south_asia_candidates.csv", "structured/south_asia_sources.csv"),
    ("structured/global_omission_candidates.csv", "structured/global_omission_sources.csv"),
    ("structured/accessibility_candidates.csv", "structured/accessibility_sources.csv"),
)

JSON_INPUTS = (
    "structured/africa_mapping_proposal.json",
    "structured/americas_arctic_mapping.json",
    "structured/oceania_indian_ocean_mapping_proposal.json",
    "structured/southeast_asia_mapping_proposal.json",
    "structured/japan_mapping_proposal.json",
)

CANDIDATE_HEADER = (
    "candidate_id", "target_label", "language_variety", "language_tag",
    "script_orthography", "territory_community", "modality", "learner_stage_scope",
    "population_low", "population_base", "population_high", "population_unit",
    "population_definition", "population_reference_year", "population_source_id",
    "population_source_url", "academic_language_overlap_low",
    "academic_language_overlap_base", "academic_language_overlap_high",
    "overlap_definition", "baseline_access_status", "evidence_confidence", "rankable",
    "notes",
)

SOURCE_HEADER = ("source_id", "title", "organization", "year", "url", "access_date", "claim_scope")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [{key: clean(value) for key, value in row.items()} for row in csv.DictReader(handle)]


def header(payload: dict[str, Any], kind: str) -> list[str]:
    keys = (
        ("candidate_header", "requested_candidate_header", "candidate_fields")
        if kind == "candidate"
        else ("source_header", "requested_source_header", "source_fields")
    )
    fallback = CANDIDATE_HEADER if kind == "candidate" else SOURCE_HEADER
    for key in keys:
        value = payload.get(key)
        if isinstance(value, list) and value:
            return [clean(item) for item in value]
        if isinstance(value, str) and value.strip():
            return [part.strip() for part in value.split("|")]
    return list(fallback)


def normalize_rows(payload: dict[str, Any], key: str, kind: str) -> list[dict[str, str]]:
    columns = header(payload, kind)
    result: list[dict[str, str]] = []
    for row in payload.get(key, []):
        if isinstance(row, dict):
            result.append({str(name): clean(value) for name, value in row.items()})
        elif isinstance(row, list):
            if len(row) != len(columns):
                raise ValueError(f"{key} row length {len(row)} does not match header {len(columns)}")
            result.append(dict(zip(columns, (clean(value) for value in row))))
        else:
            raise TypeError(f"unsupported {key} row type: {type(row).__name__}")
    return result


def canonical_url(url: str) -> str:
    text = clean(url)
    if not text:
        return ""
    parts = urlsplit(text)
    return urlunsplit((parts.scheme.casefold(), parts.netloc.casefold(), parts.path.rstrip("/"), parts.query, ""))


def source_signature(row: dict[str, str]) -> tuple[str, ...]:
    return tuple(clean(row.get(field)) for field in SOURCE_HEADER[1:])


def main() -> None:
    candidates: list[dict[str, str]] = []
    sources: list[dict[str, str]] = []
    input_files: list[dict[str, Any]] = []

    for candidate_rel, source_rel in CSV_PAIRS:
        for relative, target, reader in (
            (candidate_rel, candidates, read_csv),
            (source_rel, sources, read_csv),
        ):
            path = ROOT / relative
            rows = reader(path)
            for row in rows:
                row["_input_file"] = relative
            target.extend(rows)
            input_files.append({"relative_path": relative, "bytes": path.stat().st_size, "sha256": sha256(path)})

    for relative in JSON_INPUTS:
        path = ROOT / relative
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        candidate_rows = normalize_rows(payload, "candidates", "candidate")
        source_rows = normalize_rows(payload, "sources", "source")
        for row in candidate_rows:
            row["_input_file"] = relative
        for row in source_rows:
            row["_input_file"] = relative
        candidates.extend(candidate_rows)
        sources.extend(source_rows)
        input_files.append({"relative_path": relative, "bytes": path.stat().st_size, "sha256": sha256(path)})

    by_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_url: dict[str, list[dict[str, str]]] = defaultdict(list)
    for source in sources:
        by_id[source.get("source_id", "")].append(source)
        if canonical_url(source.get("url", "")):
            by_url[canonical_url(source.get("url", ""))].append(source)

    blank_source_ids = [source for source in sources if not source.get("source_id")]
    conflicting_ids = []
    exact_duplicate_ids = []
    for source_id, rows in sorted(by_id.items()):
        if not source_id or len(rows) <= 1:
            continue
        signatures = {source_signature(row) for row in rows}
        item = {
            "source_id": source_id,
            "row_count": len(rows),
            "input_files": sorted({row["_input_file"] for row in rows}),
            "urls": sorted({row.get("url", "") for row in rows}),
        }
        if len(signatures) > 1:
            conflicting_ids.append(item)
        else:
            exact_duplicate_ids.append(item)

    duplicate_urls = []
    for url, rows in sorted(by_url.items()):
        ids = sorted({row.get("source_id", "") for row in rows if row.get("source_id")})
        if len(ids) > 1:
            duplicate_urls.append({"canonical_url": url, "source_ids": ids, "row_count": len(rows)})

    known_ids = {source_id for source_id in by_id if source_id}
    missing_candidate_links = []
    link_url_mismatches = []
    for row in candidates:
        source_id = row.get("population_source_id", "")
        if not source_id:
            continue
        if source_id not in known_ids:
            missing_candidate_links.append(
                {
                    "candidate_id": row.get("candidate_id", ""),
                    "population_source_id": source_id,
                    "candidate_source_url": row.get("population_source_url", ""),
                    "input_file": row["_input_file"],
                }
            )
            continue
        candidate_url = canonical_url(row.get("population_source_url", ""))
        registry_urls = {canonical_url(source.get("url", "")) for source in by_id[source_id]}
        registry_urls.discard("")
        if candidate_url and registry_urls and candidate_url not in registry_urls:
            link_url_mismatches.append(
                {
                    "candidate_id": row.get("candidate_id", ""),
                    "population_source_id": source_id,
                    "candidate_source_url": candidate_url,
                    "registered_urls": sorted(registry_urls),
                    "input_file": row["_input_file"],
                }
            )

    missing_required_source_fields = []
    undated_sources = []
    for source in sources:
        missing = [field for field in SOURCE_HEADER if not source.get(field)]
        if missing:
            missing_required_source_fields.append(
                {"source_id": source.get("source_id", ""), "missing_fields": missing, "input_file": source["_input_file"]}
            )
        year = source.get("year", "").casefold().replace(" ", "")
        if year in {"", "n.d.", "nd", "undated"}:
            undated_sources.append(
                {"source_id": source.get("source_id", ""), "title": source.get("title", ""), "input_file": source["_input_file"]}
            )

    result = {
        "schema": "global-educational-access/source-identity-audit/1.0.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Pre-canonical source identity and foreign-key audit; not a ranking.",
        "input_files": input_files,
        "summary": {
            "candidate_rows": len(candidates),
            "source_rows": len(sources),
            "unique_nonblank_source_ids": len(known_ids),
            "blank_source_id_rows": len(blank_source_ids),
            "conflicting_source_id_count": len(conflicting_ids),
            "exact_duplicate_source_id_count": len(exact_duplicate_ids),
            "same_url_multiple_source_id_count": len(duplicate_urls),
            "candidate_population_source_missing_from_registry_count": len(missing_candidate_links),
            "candidate_source_url_mismatch_count": len(link_url_mismatches),
            "source_rows_missing_required_fields": len(missing_required_source_fields),
            "undated_source_rows": len(undated_sources),
        },
        "conflicting_source_ids": conflicting_ids,
        "exact_duplicate_source_ids": exact_duplicate_ids,
        "same_url_multiple_source_ids": duplicate_urls,
        "candidate_population_source_missing_from_registry": missing_candidate_links,
        "candidate_source_url_mismatches": link_url_mismatches,
        "source_rows_missing_required_fields": missing_required_source_fields,
        "undated_sources": undated_sources,
    }

    out_json = ROOT / "qa" / "SOURCE_IDENTITY_AUDIT.json"
    out_md = ROOT / "qa" / "SOURCE_IDENTITY_AUDIT.md"
    out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = result["summary"]
    lines = [
        "# Source identity audit",
        "",
        "This validates source identity and candidate population-source linkage before canonicalization. It does not validate every substantive claim and is not a ranking.",
        "",
        "## Counts",
        "",
        *[f"- `{key}`: {value}" for key, value in summary.items()],
        "",
        "## Canonicalization gate",
        "",
        "Conflicting source IDs and missing candidate foreign keys must be resolved. Duplicate IDs or URLs may be merged only after title, organization, year, URL, and claim scope are reconciled; an undated source may remain evidence but cannot supply an invented population reference year.",
        "",
        "## Machine-readable details",
        "",
        f"See `{out_json.name}`. SHA-256: `{sha256(out_json)}`.",
        "",
    ]
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({
        "json": str(out_json),
        "json_sha256": sha256(out_json),
        "markdown": str(out_md),
        "markdown_sha256": sha256(out_md),
        "summary": summary,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
