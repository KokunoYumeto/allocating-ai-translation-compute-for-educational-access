#!/usr/bin/env python3
"""Summarize rank stability without changing the preregistered estimator."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "structured"
Q = ROOT / "qa"
SCORE = S / "GLOBAL_TARGET_SCORE_TABLE_v3.csv"
PRIOR = S / "ORDER_L_SENSITIVITY_v3.csv"
REMOVAL = S / "ORDER_L_FACTOR_REMOVAL_SENSITIVITY_v3.csv"
OUT = S / "RANK_SENSITIVITY_SUMMARY_v1.csv"
QA = Q / "RANK_SENSITIVITY_SUMMARY_QA_v1.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def file_id(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest().upper(),
    }


def average_ranks(values: list[float], reverse: bool = False) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i], reverse=reverse)
    ranks = [0.0] * len(values)
    position = 0
    while position < len(order):
        end = position + 1
        while end < len(order) and values[order[end]] == values[order[position]]:
            end += 1
        rank = (position + 1 + end) / 2.0
        for idx in order[position:end]:
            ranks[idx] = rank
        position = end
    return ranks


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or not xs:
        return float("nan")
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    numerator = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return numerator / (dx * dy) if dx and dy else float("nan")


def spearman_from_rank_maps(reference: dict[str, int], scenario: dict[str, int]) -> float:
    keys = sorted(set(reference) & set(scenario))
    return pearson([float(reference[key]) for key in keys], [float(scenario[key]) for key in keys])


score_rows = [row for row in read_csv(SCORE) if row.get("l_m_need_rank")]
reference = {row["edition_target_id"]: int(row["l_m_need_rank"]) for row in score_rows}
score_by_id = {row["edition_target_id"]: row for row in score_rows}

prior_rows = read_csv(PRIOR)
removal_rows = read_csv(REMOVAL)
prior_maps: dict[str, dict[str, int]] = defaultdict(dict)
removal_maps: dict[str, dict[str, int]] = defaultdict(dict)
for row in prior_rows:
    prior_maps[row["prior_family"]][row["edition_target_id"]] = int(row["rank"])
for row in removal_rows:
    removal_maps[row["removed_factor"]][row["edition_target_id"]] = int(row["rank"])

population_ids = sorted(reference)
population_values = [float(score_by_id[target]["population_point_for_model"]) for target in population_ids]
population_ranks = average_ranks(population_values, reverse=True)
model_ranks = [float(reference[target]) for target in population_ids]
population_rank_spearman = pearson(population_ranks, model_ranks)

fields = [
    "edition_target_id",
    "label",
    "language_tag",
    "reference_rank",
    "population_point_for_model_persons",
    "top10_probability",
    "top100_probability",
    "prior_family_rank_min",
    "prior_family_rank_max",
    "prior_family_rank_span",
    "prior_families_top10_count",
    "factor_removal_rank_min",
    "factor_removal_rank_max",
    "factor_removal_rank_span",
    "factor_removal_scenarios_top10_count",
    "robust_top10_all_prior_families",
    "robust_top10_all_factor_removals",
    "robust_top100_all_scenarios",
    "row_sha256",
]
out_rows: list[dict[str, str]] = []
for target in sorted(reference, key=lambda key: reference[key]):
    score = score_by_id[target]
    prior_ranks = [mapping[target] for mapping in prior_maps.values()]
    removal_ranks = [mapping[target] for mapping in removal_maps.values()]
    row = {
        "edition_target_id": target,
        "label": score["label"],
        "language_tag": score["language_tag"],
        "reference_rank": str(reference[target]),
        "population_point_for_model_persons": score["population_point_for_model"],
        "top10_probability": score["l_m_need_top10_probability"],
        "top100_probability": score["l_m_need_top100_probability"],
        "prior_family_rank_min": str(min(prior_ranks)),
        "prior_family_rank_max": str(max(prior_ranks)),
        "prior_family_rank_span": str(max(prior_ranks) - min(prior_ranks)),
        "prior_families_top10_count": str(sum(rank <= 10 for rank in prior_ranks)),
        "factor_removal_rank_min": str(min(removal_ranks)),
        "factor_removal_rank_max": str(max(removal_ranks)),
        "factor_removal_rank_span": str(max(removal_ranks) - min(removal_ranks)),
        "factor_removal_scenarios_top10_count": str(sum(rank <= 10 for rank in removal_ranks)),
        "robust_top10_all_prior_families": str(all(rank <= 10 for rank in prior_ranks)).lower(),
        "robust_top10_all_factor_removals": str(all(rank <= 10 for rank in removal_ranks)).lower(),
        "robust_top100_all_scenarios": str(all(rank <= 100 for rank in [*prior_ranks, *removal_ranks])).lower(),
    }
    encoded = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    row["row_sha256"] = hashlib.sha256(encoded).hexdigest().upper()
    out_rows.append(row)

with OUT.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(out_rows)

scenario_spearman = {
    **{f"prior:{name}": spearman_from_rank_maps(reference, mapping) for name, mapping in sorted(prior_maps.items())},
    **{f"remove:{name}": spearman_from_rank_maps(reference, mapping) for name, mapping in sorted(removal_maps.items())},
}
scenario_top10 = {
    **{f"prior:{name}": [target for target, rank in sorted(mapping.items(), key=lambda pair: pair[1]) if rank <= 10] for name, mapping in sorted(prior_maps.items())},
    **{f"remove:{name}": [target for target, rank in sorted(mapping.items(), key=lambda pair: pair[1]) if rank <= 10] for name, mapping in sorted(removal_maps.items())},
}
all_maps = [*prior_maps.values(), *removal_maps.values()]
robust_top10 = [target for target in reference if all(mapping[target] <= 10 for mapping in all_maps)]
union_top10 = [target for target in reference if any(mapping[target] <= 10 for mapping in all_maps)]
checks = {
    "reference_target_count": len(reference) == 204,
    "every_prior_scenario_has_reference_set": all(set(mapping) == set(reference) for mapping in prior_maps.values()),
    "every_factor_removal_has_reference_set": all(set(mapping) == set(reference) for mapping in removal_maps.values()),
    "summary_rows_match_reference": len(out_rows) == len(reference),
    "row_hashes_valid": all(
        hashlib.sha256(json.dumps({k: row[k] for k in fields if k != "row_sha256"}, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest().upper()
        == row["row_sha256"]
        for row in out_rows
    ),
    "ranks_are_permutations": all(sorted(mapping.values()) == list(range(1, len(reference) + 1)) for mapping in all_maps),
}
payload = {
    "schema": "interlanguage/rank-sensitivity-summary/1.0.0",
    "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "status": "PASS" if all(checks.values()) else "FAIL",
    "inputs": [file_id(path) for path in (SCORE, PRIOR, REMOVAL)],
    "output": file_id(OUT),
    "checks": checks,
    "reference_person_targets": len(reference),
    "prior_families": sorted(prior_maps),
    "factor_removal_scenarios": sorted(removal_maps),
    "population_rank_spearman": population_rank_spearman,
    "scenario_rank_spearman": scenario_spearman,
    "robust_top10_all_prior_and_factor_removal_scenarios": sorted(robust_top10, key=lambda target: reference[target]),
    "union_top10_across_prior_and_factor_removal_scenarios": sorted(union_top10, key=lambda target: reference[target]),
    "scenario_top10": scenario_top10,
    "interpretation": [
        "High correlation with population rank means the present common-prior order is population-dominant, not a measured language-specific scarcity order.",
        "Prior-family and factor-removal scenarios test model sensitivity; they do not resolve missing target-specific evidence.",
        "A stable rank under common priors is conditional on the source-authorized candidate subset and must not be read as global completeness.",
    ],
}
Q.mkdir(parents=True, exist_ok=True)
QA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(payload, ensure_ascii=False, indent=2))
