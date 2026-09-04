#!/usr/bin/env python3
"""Make deduplicated language-group views from the exact-edition order.

The primary rank is intentionally edition-level.  This view is a separate
communication layer for readers who ask for "languages": overlapping script,
territory, accessibility, and interlanguage editions are never summed.  A
group representative is the maximum member median and carries the complete
member list so that no macro-language count is presented as additive.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="raise", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(path)


def group_key(row: dict[str, str]) -> str:
    tag = (row.get("language_tag") or "").strip()
    eid = row.get("edition_target_id", "")
    low = f"{tag} {eid}".lower()
    if "unresolved-tag:any-target" in low or "all-languages" in low:
        return ""
    if eid.startswith("edition-target:macro:") or eid.startswith("edition-target:interlanguage:"):
        return "interlanguage:" + eid.split(":", 2)[-1]
    clean = re.sub(r"^lang:", "", tag)
    code = clean.split("-", 1)[0].lower() if clean else ""
    aliases = {"id": "id", "ind": "id", "zh": "zh", "zho": "zh", "cmn": "zh", "ja": "ja", "jpn": "ja"}
    code = aliases.get(code, code)
    if not code or code.startswith("unresolved"):
        return "edition:" + eid
    return "language:" + code


def num(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def aggregate(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = group_key(row)
        if key:
            groups[key].append(row)
    out: list[dict[str, str]] = []
    for key, members in groups.items():
        medians = [num(r.get("intrinsic_need_median", "")) for r in members]
        medians = [v for v in medians if v is not None]
        if not medians:
            continue
        representative = max(medians)
        chosen = next(r for r in members if num(r.get("intrinsic_need_median", "")) == representative)
        p05 = [num(r.get("intrinsic_need_p05", "")) for r in members]
        p95 = [num(r.get("intrinsic_need_p95", "")) for r in members]
        p05 = [v for v in p05 if v is not None]
        p95 = [v for v in p95 if v is not None]
        out.append({
            "group_key": key,
            "representative_label": chosen.get("label", ""),
            "representative_language_tag": chosen.get("language_tag", ""),
            "representative_edition_target_id": chosen.get("edition_target_id", ""),
            "member_count": str(len(members)),
            "member_edition_target_ids": ";".join(sorted(r.get("edition_target_id", "") for r in members)),
            "member_labels": " || ".join(sorted(set(r.get("label", "") for r in members))),
            "population_basis_classes": ";".join(sorted(set(r.get("population_basis_class", "") for r in members))),
            "group_need_p05_min": f"{min(p05):.6f}" if p05 else "",
            "group_need_median_max_nonadditive": f"{representative:.6f}",
            "group_need_p95_max": f"{max(p95):.6f}" if p95 else "",
            "aggregation_rule": "max member median; members overlap and are not summed",
            "model_status": "L-M_LANGUAGE_GROUP_VIEW",
        })
    out.sort(key=lambda r: (-float(r["group_need_median_max_nonadditive"]), r["group_key"]))
    for i, row in enumerate(out, 1):
        row["decision_rank"] = str(i)
    return out


def build(root: Path) -> dict[str, object]:
    source = root / "structured/ORDER_L_M_v3.csv"
    rows = read_csv(source)
    overlays: list[dict[str, str]] = []
    for row in rows:
        key = group_key(row)
        if not key:
            overlays.append(row)
    rank_rows = [row for row in rows if group_key(row) and row.get("model_status", "").startswith("L-M_")]
    out = aggregate(rank_rows)
    fields = ["decision_rank", "group_key", "representative_label", "representative_language_tag", "representative_edition_target_id", "member_count", "member_edition_target_ids", "member_labels", "population_basis_classes", "group_need_p05_min", "group_need_median_max_nonadditive", "group_need_p95_max", "aggregation_rule", "model_status"]
    top10 = root / "structured/TOP10_LANGUAGE_GROUPS_v3.csv"
    top100 = root / "structured/TOP100_LANGUAGE_GROUPS_v3.csv"
    all_groups = root / "structured/LANGUAGE_GROUP_ORDER_L_M_v3.csv"
    write_csv(all_groups, out, fields)
    write_csv(top10, out[:10], fields)
    write_csv(top100, out[:100], fields)
    direct_rows = [row for row in rank_rows if row.get("population_basis_class", "").startswith("DIRECT_")]
    direct_out = aggregate(direct_rows)
    direct_all = root / "structured/DIRECT_PERSON_LANGUAGE_GROUP_ORDER_v3.csv"
    direct_top10 = root / "structured/TOP10_DIRECT_PERSON_LANGUAGE_GROUPS_v3.csv"
    direct_top100 = root / "structured/TOP100_DIRECT_PERSON_LANGUAGE_GROUPS_v3.csv"
    write_csv(direct_all, direct_out, fields)
    write_csv(direct_top10, direct_out[:10], fields)
    write_csv(direct_top100, direct_out[:100], fields)
    overlay_fields = ["edition_target_id", "label", "language_tag", "population_basis_class", "model_status"]
    overlay_rows = [{field: row.get(field, "") for field in overlay_fields} for row in overlays]
    overlay_path = root / "structured/ACCESSIBILITY_OVERLAY_ORDER_v3.csv"
    write_csv(overlay_path, overlay_rows, overlay_fields)
    manifest = {}
    for path in (all_groups, top10, top100, direct_all, direct_top10, direct_top100, overlay_path):
        manifest[str(path.relative_to(root)).replace("\\", "/")] = {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    receipt = {
        "schema": "interlanguage/language-group-order-view/1.0.0",
        "status": "PASS",
        "source": {"path": str(source.relative_to(root)).replace("\\", "/"), "bytes": source.stat().st_size, "sha256": hashlib.sha256(source.read_bytes()).hexdigest()},
        "group_count": len(out), "direct_person_group_count": len(direct_out), "overlay_count": len(overlay_rows),
        "aggregation": "max member median; no overlapping member populations summed",
        "outputs": manifest,
    }
    receipt_path = root / "qa/LANGUAGE_GROUP_ORDER_V3_RECEIPT.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (root / "qa/LANGUAGE_GROUP_ORDER_V3_RECEIPT.sha256").write_text(
        f"{hashlib.sha256(receipt_path.read_bytes()).hexdigest()}  {receipt_path.name}\n", encoding="utf-8"
    )
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(json.dumps(build(args.root.resolve()), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
