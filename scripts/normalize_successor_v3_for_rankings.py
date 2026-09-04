#!/usr/bin/env python3
"""Normalize the bounded successor-edition authority for the v3 ranker.

The successor builder intentionally emits a compact authority schema.  The
ranker consumes a small, explicitly projected feature view.  This adapter is
the only bridge: it copies no scores, ranks, project status, or local-work
metadata and preserves the source row hashes in the projected rows.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


SCRIPT_CODES = {
    "Adlm", "Arab", "Armn", "Bali", "Bass", "Beng", "Berf", "Brai",
    "Bugi", "Cans", "Cher", "Cyrl", "Deva", "Ethi", "Geor", "Grek",
    "Gujr", "Guru", "Hang", "Hans", "Hant", "Hebr", "Jpan", "Khmr",
    "Knda", "Kore", "Latn", "Laoo", "Mlym", "Mend", "Mong", "Mymr",
    "Nkoo", "Olck", "Orya", "Osma", "Rohg", "Sinh", "Syrc", "Taml",
    "Telu", "Tfng", "Thaa", "Thai", "Tibt", "Vaii", "Yiii", "Zyyy",
}


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


def split_values(value: str) -> list[str]:
    return [part.strip() for part in str(value or "").split(";") if part.strip()]


def json_list(value: str) -> str:
    return json.dumps(split_values(value), ensure_ascii=False, separators=(",", ":"))


def first_script(tag_text: str, orthography_text: str) -> str:
    for tag in split_values(tag_text):
        parts = re.split(r"[-_]", tag)
        for part in parts[1:]:
            if part in SCRIPT_CODES:
                return part
    text = f"{tag_text} {orthography_text}".lower()
    terms = {
        "Hans": ("simplified",), "Hant": ("traditional",), "Jpan": ("japanese", "kanji"),
        "Hang": ("hangul",), "Kore": ("korean",), "Arab": ("arabic", "ajami", "perso-arabic"),
        "Cyrl": ("cyrillic",), "Deva": ("devanagari",), "Beng": ("bengali", "bangla"),
        "Guru": ("gurmukhi",), "Thai": ("thai",), "Mymr": ("myanmar", "burmese"),
        "Ethi": ("ethiopic", "ge'ez", "geez"), "Taml": ("tamil",), "Telu": ("telugu",),
        "Mong": ("mongolian",), "Tibt": ("tibetan",), "Cans": ("canadian syllabics",),
        "Brai": ("braille",), "Latn": ("latin", "roman"), "Zyyy": ("oral", "signed", "audio"),
    }
    for code, needles in terms.items():
        if any(needle in text for needle in needles):
            return code
    return "Zyyy"


def id_aliases(identifier: str) -> set[str]:
    """Return only structural aliases, never name-derived aliases."""
    value = str(identifier or "")
    aliases = {value}
    if value.startswith("edition-target:"):
        value = value[len("edition-target:"):]
        aliases.add(value)
    for prefix in ("edition:regional:", "edition:supplement:", "edition:"):
        if value.startswith(prefix):
            aliases.add(value[len(prefix):])
    return {x for x in aliases if x}


def row_hash(row: dict[str, str]) -> str:
    payload = {k: v for k, v in row.items() if k not in {"registry_row_hash", "mapping_row_hash"}}
    data = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def normalize(a_path: Path, b_path: Path, out_a: Path, out_b: Path) -> dict[str, object]:
    a_rows = read_csv(a_path)
    b_rows = read_csv(b_path)
    out_a_fields = [
        "edition_target_id", "edition_key", "edition_role", "edition_derivation_class",
        "normalized_language_codes_json", "language_code_status", "language_names_json",
        "normalized_script_codes_json", "script_code_status", "script_orthography_json",
        "mode_json", "mode_status", "territory_community_json", "production_intervention_scope",
        "effective_order_l_target", "target_kind", "regional_stratum_id", "disposition",
        "registry_row_hash",
    ]
    out_a_rows: list[dict[str, str]] = []
    for source in a_rows:
        target_id = source.get("edition_target_id", "")
        if not target_id:
            raise ValueError("empty edition_target_id")
        row = {
            "edition_target_id": target_id,
            "edition_key": source.get("edition_key", ""),
            "edition_role": source.get("target_kind", ""),
            "edition_derivation_class": source.get("disposition", ""),
            "normalized_language_codes_json": json_list(source.get("language_tags", "")),
            "language_code_status": "SUCCESSOR_V3_EXPLICIT_TAG",
            "language_names_json": json_list(source.get("language_variety_names", "")),
            "normalized_script_codes_json": json.dumps([first_script(source.get("language_tags", ""), source.get("scripts_orthographies", ""))], separators=(",", ":")),
            "script_code_status": "SUCCESSOR_V3_DERIVED_FROM_EXPLICIT_TAG_OR_ORTHOGRAPHY",
            "script_orthography_json": json_list(source.get("scripts_orthographies", "")),
            "mode_json": json_list(source.get("language_mode", "")),
            "mode_status": "SUCCESSOR_V3_EXPLICIT_MODE",
            "territory_community_json": json_list(source.get("territories_communities", "")),
            "production_intervention_scope": source.get("target_kind", ""),
            "effective_order_l_target": source.get("effective_order_l_target", "false"),
            "target_kind": source.get("target_kind", ""),
            "regional_stratum_id": source.get("regional_stratum_id", ""),
            "disposition": source.get("disposition", ""),
            "registry_row_hash": source.get("row_sha256", ""),
        }
        out_a_rows.append(row)
    if len({r["edition_target_id"] for r in out_a_rows}) != len(out_a_rows):
        raise ValueError("duplicate edition IDs")

    out_b_fields = list(dict.fromkeys(list(b_rows[0].keys()) if b_rows else [] + [
        "normalized_edition_target_id", "supplement_stratum_id", "empirical_stratum_id",
        "intervention_target_id", "roster_target_id",
    ]))
    # Ensure the added fields are present even when the source table is empty.
    for field in ("normalized_edition_target_id", "supplement_stratum_id", "empirical_stratum_id", "intervention_target_id", "roster_target_id"):
        if field not in out_b_fields:
            out_b_fields.append(field)
    out_b_rows: list[dict[str, str]] = []
    for source in b_rows:
        target_id = source.get("edition_target_id", "")
        suffix = ""
        if target_id.startswith("edition-target:regional:"):
            suffix = target_id[len("edition-target:regional:"):]
        elif target_id.startswith("edition-target:supplement:"):
            suffix = target_id[len("edition-target:supplement:"):]
        row = dict(source)
        row["normalized_edition_target_id"] = target_id
        row["supplement_stratum_id"] = suffix if source.get("source_lane", "") == "large_population_supplement_v1" else ""
        row["empirical_stratum_id"] = suffix if target_id.startswith("edition-target:regional:") else ""
        row["intervention_target_id"] = target_id
        row["roster_target_id"] = target_id
        out_b_rows.append(row)

    write_csv(out_a, out_a_rows, out_a_fields)
    write_csv(out_b, out_b_rows, out_b_fields)
    return {
        "a_rows": len(out_a_rows), "b_rows": len(out_b_rows),
        "a_sha256": hashlib.sha256(out_a.read_bytes()).hexdigest(),
        "b_sha256": hashlib.sha256(out_b.read_bytes()).hexdigest(),
        "a_path": str(out_a), "b_path": str(out_b),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    result = normalize(
        root / "structured/SUCCESSOR_EDITION_TARGET_AUTHORITY_v3.csv",
        root / "structured/SUCCESSOR_EDITION_EVIDENCE_MAPPING_v3.csv",
        root / "structured/SUCCESSOR_EDITION_TARGET_REGISTRY_v3.csv",
        root / "structured/SUCCESSOR_EDITION_EVIDENCE_IDENTITY_TO_EDITION_v3.csv",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
