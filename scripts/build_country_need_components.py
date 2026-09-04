from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "COUNTRY_CONTEXT.csv"
OUTPUT = ROOT / "COUNTRY_NEED_COMPONENTS.csv"


DIRECT_FIELDS = [
    "country_code",
    "country_name",
    "wb_population_total",
    "population_0_14_thousands",
    "population_15_24_thousands",
    "population_25_64_thousands",
    "population_65_plus_thousands",
    "learning_poverty_pct",
    "learning_deprivation_pct",
    "end_primary_reading_minimum_pct",
    "end_primary_math_minimum_pct",
    "end_lower_secondary_reading_minimum_pct",
    "end_lower_secondary_math_minimum_pct",
    "primary_completion_pct",
    "lower_secondary_completion_pct",
    "upper_secondary_completion_pct",
    "tertiary_gross_enrolment_pct",
    "adult_literacy_pct",
    "youth_literacy_pct",
    "internet_users_pct",
    "electricity_access_pct",
    "mobile_subscriptions_per_100",
    "urban_population_pct",
]

COMPLEMENTS = {
    "end_primary_reading_below_minimum_pct": "end_primary_reading_minimum_pct",
    "end_primary_math_below_minimum_pct": "end_primary_math_minimum_pct",
    "end_lower_secondary_reading_below_minimum_pct": "end_lower_secondary_reading_minimum_pct",
    "end_lower_secondary_math_below_minimum_pct": "end_lower_secondary_math_minimum_pct",
    "primary_noncompletion_pct": "primary_completion_pct",
    "lower_secondary_noncompletion_pct": "lower_secondary_completion_pct",
    "upper_secondary_noncompletion_pct": "upper_secondary_completion_pct",
    "adult_basic_literacy_gap_pct": "adult_literacy_pct",
    "youth_basic_literacy_gap_pct": "youth_literacy_pct",
    "recent_internet_nonuse_pct": "internet_users_pct",
    "electricity_access_gap_pct": "electricity_access_pct",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def complement(value: str) -> str:
    if value == "":
        return ""
    number = float(value)
    return f"{100.0 - number:.12g}"


def main() -> None:
    with INPUT.open("r", newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))

    output_fields = DIRECT_FIELDS + list(COMPLEMENTS) + [
        f"{field}__year" for field in DIRECT_FIELDS if field not in {"country_code", "country_name"}
    ]
    output_rows = []
    for row in rows:
        out = {field: row.get(field, "") for field in DIRECT_FIELDS}
        for derived, source in COMPLEMENTS.items():
            out[derived] = complement(row.get(source, ""))
        for field in DIRECT_FIELDS:
            if field in {"country_code", "country_name"}:
                continue
            out[f"{field}__year"] = row.get(f"{field}__year", "")
        output_rows.append(out)

    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(output_rows)

    nonblank = {
        field: sum(1 for row in output_rows if row.get(field, "") != "")
        for field in list(COMPLEMENTS) + ["learning_poverty_pct"]
    }
    print(
        json.dumps(
            {
                "rows": len(output_rows),
                "nonblank_counts": nonblank,
                "sha256": sha256(OUTPUT),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
