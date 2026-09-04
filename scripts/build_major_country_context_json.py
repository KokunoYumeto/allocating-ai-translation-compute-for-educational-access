from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "COUNTRY_NEED_COMPONENTS.csv"
OUTPUT = ROOT / "structured" / "major_country_context.json"

METRICS = (
    "wb_population_total",
    "learning_poverty_pct",
    "end_primary_reading_below_minimum_pct",
    "end_primary_math_below_minimum_pct",
    "end_lower_secondary_reading_below_minimum_pct",
    "end_lower_secondary_math_below_minimum_pct",
    "primary_noncompletion_pct",
    "lower_secondary_noncompletion_pct",
    "upper_secondary_noncompletion_pct",
    "adult_basic_literacy_gap_pct",
    "youth_basic_literacy_gap_pct",
    "recent_internet_nonuse_pct",
    "electricity_access_gap_pct",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def number(value: str) -> float | None:
    value = value.strip()
    return None if value == "" else float(value)


def main() -> None:
    with INPUT.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    countries = []
    for row in rows:
        population = number(row["wb_population_total"])
        if population is None or population < 50_000_000:
            continue
        record = {
            "country_code": row["country_code"],
            "country_name": row["country_name"],
            "metrics": {},
        }
        for metric in METRICS:
            value = number(row.get(metric, ""))
            source_metric = metric
            if metric.endswith("_below_minimum_pct"):
                source_metric = metric.replace("_below_minimum_pct", "_minimum_pct")
            elif metric.endswith("_noncompletion_pct"):
                source_metric = metric.replace("_noncompletion_pct", "_completion_pct")
            elif metric == "adult_basic_literacy_gap_pct":
                source_metric = "adult_literacy_pct"
            elif metric == "youth_basic_literacy_gap_pct":
                source_metric = "youth_literacy_pct"
            elif metric == "recent_internet_nonuse_pct":
                source_metric = "internet_users_pct"
            elif metric == "electricity_access_gap_pct":
                source_metric = "electricity_access_pct"
            record["metrics"][metric] = {
                "value": value,
                "unit": "persons" if metric == "wb_population_total" else "percent",
                "reference_year": number(row.get(f"{source_metric}__year", "")),
                "missing": value is None,
            }
        countries.append(record)

    countries.sort(
        key=lambda item: item["metrics"]["wb_population_total"]["value"], reverse=True
    )
    payload = {
        "schema": "interlanguage/global-educational-access-major-country-context/1.0.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input": {
            "path": INPUT.name,
            "sha256": sha256(INPUT),
            "country_rows": len(rows),
        },
        "selection": {
            "minimum_population": 50_000_000,
            "selected_country_count": len(countries),
        },
        "countries": countries,
        "interpretation_guardrail": (
            "Country context is a public covariate and omission audit, not a language-population "
            "estimate. It may be joined only through an exact territorial language stratum with "
            "an explicit denominator model; it cannot assign one national rate to a transnational "
            "language or turn national exposure into direct speakers."
        ),
        "score": None,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "selected_country_count": len(countries),
                "input_sha256": sha256(INPUT),
                "output_sha256": sha256(OUTPUT),
            }
        )
    )


if __name__ == "__main__":
    main()
