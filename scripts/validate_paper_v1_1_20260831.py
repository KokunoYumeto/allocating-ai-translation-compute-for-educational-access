#!/usr/bin/env python3
"""Deterministic source, arithmetic, and content validation for PAPER.md."""

from __future__ import annotations

import csv
import hashlib
import json
from decimal import Decimal, ROUND_CEILING, ROUND_HALF_UP
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "PAPER.md"
TOP100 = ROOT / "TOP_100.csv"
TOP10 = ROOT / "TOP_10.csv"
FORWARD = ROOT / "table_c_forward_residual_commissioning.csv"
POLICY_VALIDATION = ROOT / "allocation_policy_v1_1_validation.json"
RECEIPT = ROOT / "PAPER_V1_1_CONTENT_VALIDATION_20260831.json"
COMPUTE = ROOT / "compute_token_audit_33_roots_20260830.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def appendix_rows(text: str, start: str, end: str | None) -> int:
    begin = text.index(start) + len(start)
    finish = text.index(end, begin) if end else len(text)
    lines = [line for line in text[begin:finish].splitlines() if line.startswith("| ")]
    return max(0, len(lines) - 2)


def markdown_row(values: list[str]) -> str:
    """Match the paper builder's escaping without losing literal cell pipes."""
    cells = [value.replace("\r", " ").replace("\n", " ").strip().replace("|", "\\|") for value in values]
    return "| " + " | ".join(cells) + " |"


def table_data_rows(text: str, headers: list[str]) -> list[str]:
    """Find one unambiguous rendered table; return its data lines in order."""
    lines = text.splitlines()
    header = markdown_row(headers)
    matches = [index for index, line in enumerate(lines) if line == header]
    if len(matches) != 1:
        return []
    start = matches[0] + 1
    if start >= len(lines) or lines[start] != markdown_row(["---"] * len(headers)):
        return []
    rows = []
    for line in lines[start + 1:]:
        if not line.startswith("| "):
            break
        rows.append(line)
    return rows


def rendered_rows(rows: list[dict[str, str]], columns: list[str]) -> list[str]:
    return [markdown_row([row[column] for column in columns]) for row in rows]


def main() -> None:
    text = PAPER.read_text(encoding="utf-8")
    compact_text = " ".join(text.split())
    top = read_csv(TOP100)
    top10 = read_csv(TOP10)
    forward = read_csv(FORWARD)
    compute = json.loads(COMPUTE.read_text(encoding="utf-8"))
    top_ids = [row["entry_id"] for row in top]
    policy_present = POLICY_VALIDATION.exists()
    policy = json.loads(POLICY_VALIDATION.read_text(encoding="utf-8")) if policy_present else None
    banned = [
        "Working-draft validity notice", "Calculus Volume 1 29/55",
        "Calculus Volume 1 29 of 55", "26-module calculus residual",
        "165,323,060",
        "Western Punjabi | pnb-Arab-PK | 88,915,544",
    ]
    required = [
        "83,638,632,771", "81,480,422,656", "1,906,326,611",
        "251,883,504", "10,253,232,856,362", "1,139,587,786",
        "1,139,517,198–1,139,658,374", "50,579,447", "168,419,331",
        "Calculus Volume 1: complete=30/55; residual=25", "CALC1-0031 through CALC1-0055",
        "Bahasa Indonesia Evidence-to-Practice and Research Core",
        "Japanese Open Mathematics Access and Research Bridge",
        "OpenAI Codex gpt-5.6-sol, Ultra",
    ]

    root = compute["root_counters"]
    gross_partition = (
        root["cached_input_tokens"] + root["fresh_uncached_input_tokens"]
        + root["cache_write_input_tokens"]
    )
    putonghua_denominator = Decimal(1_411_778_724)
    putonghua_base = int((putonghua_denominator * Decimal("0.8072")).to_integral_value(rounding=ROUND_HALF_UP))
    putonghua_low = int((putonghua_denominator * Decimal("0.80715")).to_integral_value(rounding=ROUND_CEILING))
    putonghua_high = int((putonghua_denominator * Decimal("0.80725")).to_integral_value(rounding=ROUND_CEILING) - 1)
    bd_denominator = Decimal(169_828_911)
    bd_base = int((bd_denominator * Decimal("0.9917")).to_integral_value(rounding=ROUND_HALF_UP))
    cn_calc = next(row for row in forward if row["forward_row_id"] == "FWD-CN-CALC1")

    paper_top10_summary = table_data_rows(text, [
        "Position", "ID", "Intervention", "Profiles", "Planning R/S/A/N", "Population basis", "First bounded package",
    ])
    paper_top10_needs = table_data_rows(text, [
        "Position", "ID", "Why now", "Follow-on", "Prerequisite route", "Access design",
    ])
    paper_appendix_a = table_data_rows(text, [
        "Pos.", "ID", "Intervention", "Profiles", "Scope", "Population context", "Stages",
        "First package", "Evidence", "Operational ordering basis",
    ])
    paper_appendix_b = table_data_rows(text, [
        "Pos.", "Intervention", "Follow-on", "Prerequisite route", "Delivery",
        "Teacher-independent requirements", "Accessibility", "Non-overlap",
    ])
    paper_appendix_c = table_data_rows(text, [
        "Pos.", "ID", "Matrix rows", "Mechanisms", "Credited cross-language reach (not estimated utility)", "Compute reuse",
        "Current completion", "Forward deficit", "Next action",
    ])
    appendix_counts = {
        "appendix_a_top100": appendix_rows(text, "# Appendix A. Full ordered Top 100: population, stage, and product", "# Appendix B."),
        "appendix_b_top100": appendix_rows(text, "# Appendix B. Full ordered Top 100: continuation, prerequisites, and access", "# Appendix C."),
        "appendix_c_crosswalk": appendix_rows(text, "# Appendix C. Interlanguage/shared-core crosswalk and exact forward work", "# Appendix D."),
        "appendix_d_universe": appendix_rows(text, "# Appendix D. Expected global profiles and dispositions", "# Appendix E."),
        "appendix_e_architectures": appendix_rows(text, "# Appendix E. Bridge and shared-production architectures", "# Appendix F."),
        "appendix_f_artifacts": appendix_rows(text, "# Appendix F. Reproducibility identities", "# Appendix G."),
        "appendix_g_calibrations": appendix_rows(text, "# Appendix G. Scope-calibrated planning judgments", None),
    }
    calibration_paths = [ROOT / "staging" / "opportunity_planning_v1_1" / name for name in ("asia_core.json", "large_profiles.json")]
    calibrations = []
    for path in calibration_paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        calibrations.extend(payload.get("entries", payload.get("evidence", [])))
    paper_calibration_rows = table_data_rows(text, ["Action", "Position", "R", "S", "A", "N", "Exact planning scope", "Reader-band reasoning"])
    calibration_ids = [entry["entry_id"] for entry in calibrations]
    checks = {
        "paper_nonempty": PAPER.stat().st_size > 100_000,
        "canonical_top100": len(top) == 100 and len(set(top_ids)) == 100 and all(top_ids),
        "canonical_top100_positions": [row["exposure_position"] for row in top] == [str(position) for position in range(1, len(top) + 1)],
        "canonical_top10_exact_prefix": len(top10) == 10 and top10 == top[:10],
        "paper_top10_summary_matches_canonical_prefix": paper_top10_summary == [markdown_row([
            row["exposure_position"], row["entry_id"], row["entry_name"], row["target_profiles"],
            "/".join(row.get("opportunity_" + dim, dim + "U") for dim in "RSAN"), row["population_context"], row["first_bounded_package"],
        ]) for row in top[:10]],
        "paper_top10_needs_matches_canonical_prefix": paper_top10_needs == rendered_rows(top[:10], [
            "exposure_position", "entry_id", "why_now", "follow_on_package", "prerequisite_route", "delivery_formats",
        ]),
        "paper_appendix_a_matches_canonical_order_and_content": paper_appendix_a == rendered_rows(top, [
            "exposure_position", "entry_id", "entry_name", "target_profiles", "territory_or_scope",
            "population_context", "education_stages", "first_bounded_package", "package_evidence_status", "ordering_basis",
        ]),
        "paper_appendix_b_matches_canonical_order_and_content": paper_appendix_b == rendered_rows(top, [
            "exposure_position", "entry_name", "follow_on_package", "prerequisite_route", "delivery_formats",
            "teacher_independent_requirements", "accessibility_requirements", "non_overlap_rule",
        ]),
        "paper_appendix_c_matches_canonical_ids_and_order": [
            [cell.strip() for cell in line.split("|", 3)[1:3]] for line in paper_appendix_c
        ] == [[row["exposure_position"], row["entry_id"]] for row in top],
        "all_required_claims_present": all(value in text for value in required),
        "all_stale_claims_absent": not any(value in text for value in banned),
        "user_first_name_absent_case_insensitive": "floris" not in text.casefold(),
        "root_input_partition": gross_partition == root["gross_input_tokens"],
        "root_total_invariant": root["gross_input_tokens"] + root["output_tokens"] == root["total_tokens"],
        "putonghua_arithmetic": (putonghua_low, putonghua_base, putonghua_high) == (1_139_517_198, 1_139_587_786, 1_139_658_374),
        "bangladesh_arithmetic": bd_base == 168_419_331,
        "chinese_forward_state": cn_calc["verified_complete_units"] == "30" and cn_calc["total_units"] == "55" and cn_calc["residual_units"] == "25",
        "appendix_a_has_100_rows": appendix_counts["appendix_a_top100"] == 100,
        "appendix_b_has_100_rows": appendix_counts["appendix_b_top100"] == 100,
        "appendix_c_has_100_rows": appendix_counts["appendix_c_crosswalk"] == 100,
        "appendix_d_has_54_rows": appendix_counts["appendix_d_universe"] == 54,
        "appendix_e_has_16_rows": appendix_counts["appendix_e_architectures"] == 16,
        "appendix_f_has_expected_artifact_rows": appendix_counts["appendix_f_artifacts"] == 16 + int(policy_present),
        "appendix_g_has_every_calibration": appendix_counts["appendix_g_calibrations"] == len(calibrations)
            and [line.split("|", 2)[1].strip() for line in paper_calibration_rows] == calibration_ids,
        "calibration_provenance_hashes_present": all(path.name in text and sha256(path) in text for path in calibration_paths),
        "planning_measurement_distinction_present": all(phrase in compact_text for phrase in (
            "not experimentally", "not measured beneficiary counts", "measured-only", "never an automatically invented midpoint")),
        "observation_rows_not_fake_commissions": not any(row["entry_id"].startswith("OBS-") for row in top),
        "key_references_present": all(value in text for value in [
            "Walter, S. L., & Benson, C. (2012)",
            "Bangladesh Bureau of Statistics. (2024)",
            "Department of Statistics Malaysia. (2022)",
            "Ministry of Education of Japan. (2026a)",
            "Ministry of Education of the People's Republic of China. (2026)",
            "Sawaki, Y. (2017)", "W3C. (2025)",
        ]),
    }
    if policy_present:
        policy_is_dict = isinstance(policy, dict)
        policy_checks = policy.get("checks") if policy_is_dict else None
        checks.update({
            "allocation_policy_receipt_schema": policy_is_dict and policy.get("schema") == "interlanguage/allocation-policy-validation/1.1.0",
            "allocation_policy_receipt_status": policy_is_dict and policy.get("status") == "PASS",
            "allocation_policy_receipt_checks": isinstance(policy_checks, dict) and bool(policy_checks) and all(value is True for value in policy_checks.values()),
            "allocation_policy_receipt_inputs": policy_is_dict and isinstance(policy.get("inputs"), dict),
            "allocation_policy_receipt_policy": policy_is_dict and isinstance(policy.get("policy"), dict),
            "allocation_policy_receipt_diagnostics": policy_is_dict and isinstance(policy.get("diagnostics"), dict),
            "paper_allocation_policy_receipt_provenance": POLICY_VALIDATION.name in text and sha256(POLICY_VALIDATION) in text,
        })
    status = "PASS" if all(checks.values()) else "FAIL"
    output = {
        "schema": "interlanguage/paper-v1-1-content-validation/1.0.0",
        "status": status,
        "checks": checks,
        "appendix_counts": appendix_counts,
        "arithmetic": {
            "putonghua": {"low": putonghua_low, "base": putonghua_base, "high": putonghua_high},
            "bangladesh_bangla_point": bd_base,
            "root_input_partition": gross_partition,
        },
        "paper": {"bytes": PAPER.stat().st_size, "sha256": sha256(PAPER)},
        "top100": {"bytes": TOP100.stat().st_size, "sha256": sha256(TOP100)},
        "top10": {"bytes": TOP10.stat().st_size, "sha256": sha256(TOP10)},
        "forward": {"bytes": FORWARD.stat().st_size, "sha256": sha256(FORWARD)},
        "compute_receipt": {"bytes": COMPUTE.stat().st_size, "sha256": sha256(COMPUTE)},
        "allocation_policy_receipt": {"bytes": POLICY_VALIDATION.stat().st_size, "sha256": sha256(POLICY_VALIDATION)} if policy_present else None,
        "limitations": "This validates source state, selected arithmetic, exact canonical Top-10 prefix, emitted paper table order and content, optional allocation-policy receipt schema/status, stale-claim absence, and appendix closure. It does not replace PDF rendering or visual QA.",
    }
    RECEIPT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "failed": [key for key, value in checks.items() if not value], "paper_sha256": sha256(PAPER), "receipt_sha256": sha256(RECEIPT)}, indent=2))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
