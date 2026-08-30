from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "PAPER.md"
JSON_OUT = ROOT / "FINAL_CONTENT_VALIDATION_20260830.json"
MD_OUT = ROOT / "FINAL_CONTENT_VALIDATION_20260830.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def read_csv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def check(name: str, passed: bool, detail: str) -> dict[str, object]:
    return {"name": name, "passed": bool(passed), "detail": detail}


def main() -> None:
    paper = PAPER.read_text(encoding="utf-8")
    observations = read_csv("population_observations_master.csv")
    sources = read_csv("population_source_register_public.csv")
    candidates = read_csv("candidate_interventions_master.csv")
    natural_scores = read_csv("natural_language_scores_v3.csv")
    expansion_scores = read_csv("candidate_expansion_scores.csv")
    eligible = read_csv("portfolio_linguistic_candidates.csv")
    top10 = read_csv("TOP_10.csv")
    top100 = read_csv("TOP_100.csv")
    needs = read_csv("top100_needs_assignment_v2.csv")
    crosswalk = read_csv("top100_interlanguage_overlap_crosswalk.csv")
    compute = json.loads((ROOT / "compute_token_audit_33_roots_20260830.json").read_text(encoding="utf-8"))

    results: list[dict[str, object]] = []
    results += [
        check("population_observation_rows", len(observations) == 475, f"rows={len(observations)}"),
        check("source_record_rows", len(sources) == 81, f"rows={len(sources)}"),
        check("distinct_authority_labels", len({r['authority'] for r in sources}) == 58, f"labels={len({r['authority'] for r in sources})}"),
        check("candidate_rows", len(candidates) == 210, f"rows={len(candidates)}"),
        check("exact_natural_profile_interventions", len(natural_scores) + len(expansion_scores) == 143, f"base_scores={len(natural_scores)} expansion_scores={len(expansion_scores)} total={len(natural_scores) + len(expansion_scores)}"),
        check("eligible_cardinal_rows", len(eligible) == 134, f"rows={len(eligible)}"),
        check("top10_rows", len(top10) == 10, f"rows={len(top10)}"),
        check("top100_rows", len(top100) == 100, f"rows={len(top100)}"),
        check("top100_unique_positions", len({r['portfolio_position'] for r in top100}) == 100, f"unique={len({r['portfolio_position'] for r in top100})}"),
        check("needs_assignments", len(needs) == 100 and all(r.get("needs_first_package", "").strip() for r in needs), f"rows={len(needs)} nonempty={sum(bool(r.get('needs_first_package', '').strip()) for r in needs)}"),
    ]

    top10_order = [r["intervention_name"] for r in sorted(top10, key=lambda r: int(r["portfolio_position"]))]
    expected_top10 = [
        "Bahasa Indonesia", "Bangladesh Bangla", "Telugu", "Indian Bengali",
        "Vietnamese", "Marathi", "Indian Tamil", "Western Punjabi", "Javanese", "Gujarati",
    ]
    results.append(check("top10_order", top10_order == expected_top10, " | ".join(top10_order)))

    relation_counts = Counter(r["overlap_relation_status"] for r in crosswalk)
    results += [
        check("crosswalk_rows", len(crosswalk) == 100, f"rows={len(crosswalk)}"),
        check("crosswalk_exact_profile", relation_counts["exact_profile_match"] == 16, str(dict(relation_counts))),
        check("crosswalk_named_country", relation_counts["exact_language_script_and_target_country_cell"] == 4, str(dict(relation_counts))),
        check("crosswalk_hypothesis", relation_counts["hypothesis_only_language_script_match_territory_unresolved"] == 1, str(dict(relation_counts))),
        check("crosswalk_unmapped", relation_counts["no_exact_relation_in_current_matrix"] == 79, str(dict(relation_counts))),
        check("cross_language_reach_zero", all(float(r["current_cross_language_demographic_reach_credit"]) == 0 for r in crosswalk), "all 100 credits equal zero"),
        check("interlanguage_rankability_false", all(r["rankable_under_current_evidence"].lower() == "false" for r in crosswalk), "all 100 flags false"),
    ]

    roots = compute["root_counters"]
    closure = compute["descendant_inclusive_closure"]
    results += [
        check("compute_root_total", roots["total_tokens"] == 83_638_632_771, str(roots["total_tokens"])),
        check("compute_input_partition", roots["gross_input_tokens"] == roots["cached_input_tokens"] + roots["fresh_uncached_input_tokens"] + roots["cache_write_input_tokens"], "gross = cached + fresh + cache-write"),
        check("compute_total_identity", roots["total_tokens"] == roots["gross_input_tokens"] + roots["output_tokens"], "total = gross input + output"),
        check("reasoning_subset", roots["reasoning_is_subset_of_output"] is True, str(roots["reasoning_is_subset_of_output"])),
        check("closure_contains_roots", closure["contains_all_33_roots"] is True and closure["descendant_exclusive_total_asserted"] is False, closure["comparison_semantics"]),
        check("closure_total", closure["inclusive_total_tokens"] == 10_253_232_856_362, str(closure["inclusive_total_tokens"])),
    ]

    required_paper_strings = [
        "475 population observations and 81 registered source records from 58 distinct authority labels",
        "Bahasa Indonesia, Bangladesh Bangla, Telugu, Indian Bengali, Vietnamese",
        "83,638,632,771",
        "10,253,232,856,362",
        "88,493,496",
        "19,745 measured teaching-package pages",
        "20,763 selected-corpus working pages",
        "27,705-page documented rendered universe",
        "722/722",
        "Top-100 exact-profile crosswalk",
        "16 exact-profile matches",
        "four exact language/script plus named-country matches",
        "79 unmapped rows",
        "OpenAI Codex gpt-5.6-sol, Ultra",
    ]
    normalized_paper = re.sub(r"\s+", " ", paper)
    for value in required_paper_strings:
        results.append(check(f"paper_contains:{value[:36]}", value in normalized_paper, value))

    forbidden_patterns = {
        "absolute_windows_profile": r"[A-Za-z]:\\Users\\[^\\\r\n]+",
        "absolute_unix_profile": r"/" + r"Users/[^/\r\n]+",
        "private_codex_path": r"\.codex",
        "stale_openlogic_321": r"321/722",
        "stale_indonesian_remainder": r"0\.5049501669",
        "old_unaudited_top100": r"90 non-audited|only the audited Top 10 receive|rows remain explicitly unaudited",
        "tool_citation_token": r"turn\d+(?:search|view|fetch)\d+|codex-file-citation",
        "placeholder": r"\b(?:TODO|TBD|PLACEHOLDER)\b",
        "replacement_character": "\ufffd",
    }
    for name, pattern in forbidden_patterns.items():
        hits = re.findall(pattern, paper, flags=re.IGNORECASE)
        results.append(check(f"paper_forbidden:{name}", not hits, f"hits={len(hits)}"))

    public_files = [
        ROOT / "PAPER.md",
        ROOT / "population_source_register_public.csv",
        ROOT / "INDONESIAN_PROGRAM_COMPUTE_AND_PAGE_RECONCILIATION_PUBLIC_20260830.md",
        ROOT / "compute_token_audit_33_roots_20260830.json",
        ROOT / "TOP100_INTERLANGUAGE_CROSSWALK_METHOD_20260830.md",
        ROOT / "TOP100_INTERLANGUAGE_CROSSWALK_VALIDATION_RECEIPT_20260830.md",
    ]
    private_location_pattern = (
        r"[A-Za-z]:\\Users\\[^\\\r\n]+|"
        + r"/"
        + r"Users/[^/\r\n]+|(?:^|[\\/])\.codex(?:[\\/]|$)"
    )
    for path in public_files:
        text = path.read_text(encoding="utf-8-sig")
        private = bool(re.search(
            private_location_pattern,
            text,
            flags=re.IGNORECASE,
        ))
        results.append(check(f"public_privacy:{path.name}", not private, f"bytes={path.stat().st_size} sha256={sha256(path)}"))

    failed = [item for item in results if not item["passed"]]
    receipt = {
        "schema": "standalone-ai-compute-access-final-content-validation/1.0.0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "paper": {"bytes": PAPER.stat().st_size, "sha256": sha256(PAPER)},
        "checks": results,
        "summary": {"total": len(results), "passed": len(results) - len(failed), "failed": len(failed)},
    }
    JSON_OUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Final content validation",
        "",
        f"- Checks: {len(results)}",
        f"- Passed: {len(results) - len(failed)}",
        f"- Failed: {len(failed)}",
        f"- PAPER.md SHA-256: `{receipt['paper']['sha256']}`",
        "",
    ]
    lines.extend(f"- {'PASS' if item['passed'] else 'FAIL'}: {item['name']} - {item['detail']}" for item in results)
    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(receipt["summary"], indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
