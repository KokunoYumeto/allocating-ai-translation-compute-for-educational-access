#!/usr/bin/env python3
"""Audit final DOCX structure, privacy, and renderer-safe text without unpacking it."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
DC = "http://purl.org/dc/elements/1.1/"
CP = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"


def sha256(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest().upper()
    return digest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    profile_token = os.environ.get("USERNAME", "").casefold()

    with zipfile.ZipFile(args.docx) as package:
        corrupt_member = package.testzip()
        names = set(package.namelist())
        xml_parts = {
            name: package.read(name)
            for name in names
            if name.endswith((".xml", ".rels"))
        }

    decoded = "\n".join(data.decode("utf-8", errors="replace") for data in xml_parts.values())
    document = ET.fromstring(xml_parts["word/document.xml"])
    core = ET.fromstring(xml_parts["docProps/core.xml"])
    creator = core.findtext(f"{{{DC}}}creator") or ""
    last_modified_by = core.findtext(f"{{{CP}}}lastModifiedBy") or ""
    paragraphs = document.findall(f".//{{{W}}}p")
    tables = document.findall(f".//{{{W}}}tbl")
    sections = document.findall(f".//{{{W}}}sectPr")
    omml = document.findall(f".//{{{M}}}oMath") + document.findall(f".//{{{M}}}oMathPara")
    rsid_count = len(re.findall(r"\bw:rsid[A-Za-z]*=", decoded))
    tracked_insertions = len(document.findall(f".//{{{W}}}ins"))
    tracked_deletions = len(document.findall(f".//{{{W}}}del"))
    profile_count = decoded.casefold().count(profile_token) if profile_token else 0
    pattern_counts = {
        "replacement_character": decoded.count("\ufffd"),
        "windows_profile_path": len(re.findall(r"(?i)[A-Za-z]:\\Users\\", decoded)),
        "profile_username": profile_count,
        "unicode_em_dash": decoded.count("\u2014"),
        "unicode_en_dash": decoded.count("\u2013"),
        "unicode_nonbreaking_hyphen": decoded.count("\u2011"),
        "rsid_attributes": rsid_count,
        "tracked_insertions": tracked_insertions,
        "tracked_deletions": tracked_deletions,
    }
    checks = {
        "valid_zip": corrupt_member is None,
        "document_xml_present": "word/document.xml" in names,
        "seventeen_tables": len(tables) == 17,
        "eight_sections": len(sections) == 8,
        "native_math_present": len(omml) > 0,
        "creator_scrubbed": creator == "",
        "last_modified_by_scrubbed": last_modified_by == "",
        "custom_properties_absent": "docProps/custom.xml" not in names,
        "comments_absent": not any(name.startswith("word/comments") for name in names),
        "no_rsid_attributes": rsid_count == 0,
        "no_tracked_changes": tracked_insertions == 0 and tracked_deletions == 0,
        "no_replacement_character": pattern_counts["replacement_character"] == 0,
        "no_profile_path": pattern_counts["windows_profile_path"] == 0,
        "no_profile_username": profile_count == 0,
        "ascii_prose_dashes": sum(pattern_counts[key] for key in ("unicode_em_dash", "unicode_en_dash", "unicode_nonbreaking_hyphen")) == 0,
    }
    report = {
        "schema": "interlanguage/final-docx-audit/1.0.0",
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "docx": {"path": args.docx.name, "bytes": args.docx.stat().st_size, "sha256": sha256(args.docx)},
        "package_entry_count": len(names),
        "paragraph_count": len(paragraphs),
        "table_count": len(tables),
        "section_count": len(sections),
        "native_math_object_count": len(omml),
        "metadata": {"creator_present": bool(creator), "last_modified_by_present": bool(last_modified_by)},
        "pattern_counts": pattern_counts,
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": report["status"], "docx": report["docx"], "checks": checks}, indent=2))
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
