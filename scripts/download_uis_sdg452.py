#!/usr/bin/env python3
"""Download the bounded UIS SDG 4.5.2 language-of-instruction series.

The script preserves every returned observation for the three both-sex stage
indicators and separately emits the latest observation(s) per country-stage.
It does not map country aggregates to individual language populations.
"""

from __future__ import annotations

import csv
import hashlib
import json
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_OUT = ROOT / "sources" / "uis_sdg452_language_instruction_202602.csv"
LATEST_OUT = ROOT / "structured" / "uis_sdg452_latest_country_stage.csv"
RECEIPT_OUT = ROOT / "qa" / "UIS_SDG452_DOWNLOAD_RECEIPT.json"

API = "https://data.unesco.org/api/explore/v2.1/catalog/datasets/uis001/records"
DATASET_PAGE = "https://data.unesco.org/explore/dataset/uis001/"
INDICATORS = {
    "FHLANGILP.G2T3": "early_grades",
    "FHLANGILP.PRIMARY": "end_primary",
    "FHLANGILP.LOWERSEC": "lower_secondary",
}
FIELDS = [
    "indicator_id",
    "stage",
    "indicator_label_en",
    "country_id",
    "country_name_en",
    "year",
    "value",
    "magnitude",
    "qualifier",
    "footnotes",
    "api_query_url",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def fetch_indicator(indicator_id: str) -> tuple[list[dict], list[str]]:
    rows: list[dict] = []
    urls: list[str] = []
    offset = 0
    while True:
        params = urllib.parse.urlencode(
            {
                "where": f"indicator_id='{indicator_id}'",
                "order_by": "country_id,year",
                "limit": 100,
                "offset": offset,
            }
        )
        url = f"{API}?{params}"
        urls.append(url)
        request = urllib.request.Request(url, headers={"User-Agent": "Open educational access research/1.0"})
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.load(response)
        batch = payload.get("results", [])
        for item in batch:
            rows.append(
                {
                    "indicator_id": item.get("indicator_id"),
                    "stage": INDICATORS[indicator_id],
                    "indicator_label_en": item.get("indicator_label_en"),
                    "country_id": item.get("country_id"),
                    "country_name_en": item.get("country_name_en"),
                    "year": item.get("year"),
                    "value": item.get("value"),
                    "magnitude": item.get("magnitude"),
                    "qualifier": item.get("qualifier"),
                    "footnotes": item.get("footnotes"),
                    "api_query_url": url,
                }
            )
        offset += len(batch)
        if not batch or offset >= int(payload.get("total_count", 0)):
            break
    return rows, urls


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(
            {
                key: json.dumps(value, ensure_ascii=False, sort_keys=True)
                if isinstance(value, (dict, list))
                else value
                for key, value in row.items()
            }
            for row in rows
        )


def year_number(value: object) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return -1


def comparable(value: object) -> str:
    """Stable comparison text for scalar or nested API values."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def main() -> None:
    fetched: list[dict] = []
    query_urls: list[str] = []
    counts: dict[str, int] = {}
    for indicator_id in INDICATORS:
        rows, urls = fetch_indicator(indicator_id)
        fetched.extend(rows)
        query_urls.extend(urls)
        counts[indicator_id] = len(rows)

    fetched.sort(key=lambda r: (r["indicator_id"] or "", r["country_id"] or "", year_number(r["year"]), str(r["value"])))
    write_csv(RAW_OUT, fetched)

    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in fetched:
        grouped[(row["indicator_id"], row["country_id"])].append(row)
    latest: list[dict] = []
    conflicting_latest_groups: list[str] = []
    for key, rows in sorted(grouped.items()):
        newest = max(year_number(row["year"]) for row in rows)
        selected = [row for row in rows if year_number(row["year"]) == newest]
        signatures = {
            (comparable(row["value"]), comparable(row["qualifier"]), comparable(row["footnotes"]))
            for row in selected
        }
        if len(signatures) > 1:
            conflicting_latest_groups.append("|".join(key))
        seen: set[tuple] = set()
        for row in selected:
            signature = tuple(comparable(row.get(field)) for field in FIELDS[:-1])
            if signature not in seen:
                latest.append(row)
                seen.add(signature)
    write_csv(LATEST_OUT, latest)

    receipt = {
        "schema": "interlanguage/uis-sdg452-download-receipt/1.0.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_page": DATASET_PAGE,
        "dataset_license": "CC BY-SA 4.0 as stated on the UNESCO DataHub dataset page",
        "dataset_release_context": "UIS Data Browser February 2026 education release",
        "indicator_ids": INDICATORS,
        "query_urls": query_urls,
        "rows_by_indicator": counts,
        "raw_rows": len(fetched),
        "latest_country_stage_rows": len(latest),
        "country_stage_groups": len(grouped),
        "conflicting_latest_groups": conflicting_latest_groups,
        "interpretation_boundary": "Country-stage aggregate only. It cannot be assigned to an exact language cohort without compatible language-specific evidence.",
        "outputs": [
            {"path": RAW_OUT.relative_to(ROOT).as_posix(), "bytes": RAW_OUT.stat().st_size, "sha256": sha256(RAW_OUT)},
            {"path": LATEST_OUT.relative_to(ROOT).as_posix(), "bytes": LATEST_OUT.stat().st_size, "sha256": sha256(LATEST_OUT)},
        ],
    }
    RECEIPT_OUT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_OUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
