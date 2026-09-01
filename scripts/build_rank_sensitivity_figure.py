#!/usr/bin/env python3
"""Build the paper's deterministic rank-sensitivity figure and data table."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "TOP_100.csv"
PORTFOLIO_INPUT = ROOT / "portfolio_linguistic_candidates.csv"
DATA_OUTPUT = ROOT / "figure_1_rank_sensitivity_data.csv"
PNG_OUTPUT = ROOT / "figure_1_rank_sensitivity.png"
SVG_OUTPUT = ROOT / "figure_1_rank_sensitivity.svg"

LANE_COLORS = {
    "base": "#176B87",
    "optimistic": "#C94C4C",
    "scarcity": "#6A4C93",
}

EXPECTED_ELIGIBLE_ROWS = 135
EXPECTED_TOP10 = [
    "Standard Simplified Chinese (Mainland China)",
    "Bahasa Indonesia",
    "Telugu",
    "Indian Bengali",
    "Bangladesh Bangla",
    "Marathi",
    "Indian Tamil",
    "Vietnamese",
    "Javanese",
    "Gujarati",
]


def main() -> None:
    with INPUT.open("r", encoding="utf-8-sig", newline="") as handle:
        top100_rows = list(csv.DictReader(handle))
    with PORTFOLIO_INPUT.open("r", encoding="utf-8-sig", newline="") as handle:
        portfolio_rows = list(csv.DictReader(handle))

    portfolio_count = len(portfolio_rows)
    if portfolio_count != EXPECTED_ELIGIBLE_ROWS:
        raise ValueError(f"Expected {EXPECTED_ELIGIBLE_ROWS} eligible rows, found {portfolio_count}")
    if len(top100_rows) != 100:
        raise ValueError(f"Expected 100 ordered headline rows, found {len(top100_rows)}")
    actual_top10 = [row["intervention_name"] for row in top100_rows[:10]]
    if actual_top10 != EXPECTED_TOP10:
        raise ValueError(f"Unexpected Top 10 order: {actual_top10}")
    rows = top100_rows[:20]

    output_fields = [
        "portfolio_position",
        "intervention_id",
        "intervention_name",
        "target_profiles",
        "admission_lane",
        "base_efficiency_rank_low",
        "base_efficiency_rank_high",
        "optimistic_efficiency_rank_low",
        "optimistic_efficiency_rank_high",
        "scarcity_efficiency_rank_low",
        "scarcity_efficiency_rank_high",
        "informative_rank_best",
        "informative_rank_worst",
        "admission_lane_rank_low",
        "admission_lane_rank_high",
        "conservative_efficiency_rank_low",
        "conservative_efficiency_rank_high",
    ]
    with DATA_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row[field] for field in output_fields} for row in rows)

    fig, ax = plt.subplots(figsize=(10.8, 8.0))
    y_positions = list(range(len(rows)))
    for y, row in zip(y_positions, rows):
        best = int(row["informative_rank_best"])
        worst = int(row["informative_rank_worst"])
        admitted_rank = (
            int(row["admission_lane_rank_low"])
            + int(row["admission_lane_rank_high"])
        ) / 2
        color = LANE_COLORS[row["admission_lane"]]
        ax.hlines(y, best, worst, color="#9AA4AE", linewidth=2.2, zorder=1)
        ax.scatter(best, y, marker="|", s=110, linewidths=1.7, color="#3B454E", zorder=2)
        ax.scatter(worst, y, marker="|", s=110, linewidths=1.7, color="#3B454E", zorder=2)
        ax.scatter(admitted_rank, y, s=52, color=color, edgecolor="white", linewidth=0.7, zorder=3)

    labels = [
        f"{row['portfolio_position']}. {row['intervention_name']} ({row['target_profiles']})"
        for row in rows
    ]
    ax.set_yticks(y_positions, labels)
    ax.invert_yaxis()
    ax.set_xlabel("Rank (1 = highest); line spans base, optimistic, and scarcity views")
    ax.set_title("Sensitivity of the headline Top 20 across three informative ranking views")
    ax.grid(axis="x", color="#D9DEE3", linewidth=0.7)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=8.6)
    ax.tick_params(axis="x", labelsize=9)

    legend_handles = [
        plt.Line2D(
            [0], [0], marker="o", linestyle="", markerfacecolor=color,
            markeredgecolor="white", markersize=7, label=f"Admitted through {lane} view"
        )
        for lane, color in LANE_COLORS.items()
    ]
    ax.legend(handles=legend_handles, loc="upper right", frameon=False, fontsize=8.5)
    fig.text(
        0.01,
        0.012,
        f"All {portfolio_count} conservative lower-bound scores are zero and tie at ranks 1–{portfolio_count}; "
        "that degenerate view is reported separately and is not plotted.",
        fontsize=8,
        color="#4F5962",
    )
    fig.tight_layout(rect=(0.0, 0.035, 1.0, 1.0))
    fig.savefig(PNG_OUTPUT, dpi=300, facecolor="white")
    fig.savefig(SVG_OUTPUT, facecolor="white")
    plt.close(fig)

    print(f"rows={len(rows)}")
    print(PNG_OUTPUT)
    print(SVG_OUTPUT)
    print(DATA_OUTPUT)


if __name__ == "__main__":
    main()
