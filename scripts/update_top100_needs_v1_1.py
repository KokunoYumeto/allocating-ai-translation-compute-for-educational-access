from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOP = ROOT / "TOP_100.csv"
NEEDS = ROOT / "top100_needs_assignment_v2.csv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    top_rows = read(TOP)
    old_rows = read(NEEDS)
    fields = list(old_rows[0])
    by_id = {row["intervention_id"]: row for row in old_rows}

    chinese = {
        "portfolio_position": "",
        "intervention_id": "NAT-122",
        "intervention_name": "Standard Simplified Chinese (Mainland China)",
        "target_profiles": "zh-Hans-CN",
        "territory_or_scope": "China",
        "needs_evidence_stage": "direct_official_and_exact_local_residual_audit",
        "needs_first_package": (
            "Do not duplicate complete Open Logic or Algebra and Trigonometry 2e. "
            "Complete the exact 26-module Calculus Volume 1 residual, continue the six "
            "remaining fixed-STEM books where absent, and build semantic accessibility derivatives."
        ),
        "needs_assignment_status": "directly_audited_stage_specific_residual",
        "needs_observed_evidence": (
            "Open Logic 722/722; Algebra and Trigonometry 94/94; Calculus I 29/55; "
            "six further fixed-STEM books pending; Open Logic PDF untagged with seven "
            "font rows lacking ToUnicode."
        ),
        "needs_source": "ACE-E060;ACE-E061;ACE-E062;ACE-E063",
        "needs_caveat": (
            "The 1,411,778,724 census value is a gross mainland territory ceiling, not an "
            "exact comfortable-reader count. Platform abundance does not prove open, offline, "
            "teacher-independent, or semantically accessible sequence closure."
        ),
        "learner_stage": "secondary_to_research_frontier_and_accessibility",
        "need_class": "exact_residual_stem_accessibility_and_advanced_gap_audit",
        "first_open_package_or_sequence": (
            "CALC1-0030 through CALC1-0055; semantic HTML/MathML, navigable EPUB and tagged PDF "
            "for the complete Open Logic corpus; then exact remaining fixed-STEM residual."
        ),
        "evidence_scope": "official national denominator and supply context plus hash-pinned program state",
        "classification_basis": (
            "Equal-basis opportunity and forward allocation are separate: D=1 only for the "
            "ex-ante comparator; D=0 for complete exact corpora; measured residual for partial works."
        ),
        "existing_supply_summary": (
            "Large national Chinese digital-education supply; complete local Open Logic and Algebra "
            "and Trigonometry; partial Calculus I; exact accessibility defect recorded."
        ),
        "confidence": "high_on_exact_residual_medium_on_incremental_population_access",
        "caveat_v2": (
            "zh-Hans-CN is not blanket coverage for every Sinitic language or minority community; "
            "advanced and frontier gaps require content-specific inventory."
        ),
        "source_ids_urls": (
            "PM-S022=https://www.stats.gov.cn/english/PressRelease/202105/t20210510_1817187.html ; "
            "ACE-E061=https://www.moe.gov.cn/jyb_sjzl/wenzi/202108/t20210827_554992.html ; "
            "ACE-E062=https://higher.smartedu.cn/help ; ACE-E063=local pinned state"
        ),
    }

    rebuilt: list[dict[str, str]] = []
    missing: list[str] = []
    for top in sorted(top_rows, key=lambda row: int(row["portfolio_position"])):
        intervention_id = top["intervention_id"]
        if intervention_id == "NAT-122":
            row = dict(chinese)
        elif intervention_id in by_id:
            row = dict(by_id[intervention_id])
        else:
            missing.append(intervention_id)
            continue
        row["portfolio_position"] = top["portfolio_position"]
        row["intervention_name"] = top["intervention_name"]
        row["target_profiles"] = top["target_profiles"]
        row["territory_or_scope"] = top["territory_or_scope"]
        rebuilt.append({field: row.get(field, "") for field in fields})

    if missing:
        raise RuntimeError(f"Missing needs rows for current Top 100: {missing}")
    if len(rebuilt) != 100 or len({row['intervention_id'] for row in rebuilt}) != 100:
        raise RuntimeError("Top-100 needs rebuild is not a 100-row unique intervention set")

    with NEEDS.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rebuilt)

    print({
        "rows": len(rebuilt),
        "first": rebuilt[0]["intervention_id"],
        "last": rebuilt[-1]["intervention_id"],
        "directly_audited": sum(
            row["needs_assignment_status"].startswith("directly_audited") for row in rebuilt
        ),
    })


if __name__ == "__main__":
    main()

