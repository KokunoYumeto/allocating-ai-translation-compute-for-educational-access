#!/usr/bin/env python3
"""Run bounded structural, text, privacy, and renderer-safety checks on a PDF."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--text", type=Path, required=True)
    args = parser.parse_args()

    reader = PdfReader(str(args.pdf))
    pages = list(reader.pages)
    text = "\n\f\n".join(page.extract_text() or "" for page in pages)
    args.text.parent.mkdir(parents=True, exist_ok=True)
    args.text.write_text(text, encoding="utf-8", newline="\n")

    profile_token = os.environ.get("USERNAME", "").casefold()
    metadata_values = [str(value) for value in (reader.metadata or {}).values() if value is not None]
    metadata_text = "\n".join(metadata_values)
    page_sizes = Counter(
        (
            round(float(page.mediabox.width), 3),
            round(float(page.mediabox.height), 3),
        )
        for page in pages
    )
    annotation_count = sum(len(page.get("/Annots", [])) for page in pages)
    acroform = reader.trailer.get("/Root", {}).get("/AcroForm")
    names = reader.trailer.get("/Root", {}).get("/Names", {})
    javascript = bool(names.get("/JavaScript")) if hasattr(names, "get") else False
    embedded_files = bool(names.get("/EmbeddedFiles")) if hasattr(names, "get") else False
    tagged = bool(reader.trailer.get("/Root", {}).get("/MarkInfo", {}).get("/Marked"))

    pattern_counts = {
        "replacement_character": text.count("\ufffd"),
        "windows_profile_path": len(re.findall(r"(?i)[A-Za-z]:\\Users\\", text + metadata_text)),
        "profile_username": (text + "\n" + metadata_text).casefold().count(profile_token) if profile_token else 0,
        "raw_tex_begin": len(re.findall(r"\\begin\s*\{", text)),
        "raw_tex_frac": text.count("\\frac"),
        "raw_tex_theta": text.count("\\theta"),
        "unicode_em_dash": text.count("\u2014"),
        "unicode_en_dash": text.count("\u2013"),
        "unicode_nonbreaking_hyphen": text.count("\u2011"),
    }
    checks = {
        "nonempty": args.pdf.stat().st_size > 0,
        "page_count_59": len(pages) == 59,
        "unencrypted": not reader.is_encrypted,
        "tagged": tagged,
        "no_acroform": not bool(acroform),
        "no_javascript": not javascript,
        "no_embedded_files": not embedded_files,
        "no_replacement_character": pattern_counts["replacement_character"] == 0,
        "no_profile_path": pattern_counts["windows_profile_path"] == 0,
        "no_profile_username": pattern_counts["profile_username"] == 0,
        "no_raw_tex_commands": sum(pattern_counts[key] for key in ("raw_tex_begin", "raw_tex_frac", "raw_tex_theta")) == 0,
        "ascii_prose_dashes": sum(pattern_counts[key] for key in ("unicode_em_dash", "unicode_en_dash", "unicode_nonbreaking_hyphen")) == 0,
    }
    report = {
        "schema": "interlanguage/final-pdf-audit/1.0.0",
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "pdf": {"path": args.pdf.name, "bytes": args.pdf.stat().st_size, "sha256": sha256(args.pdf)},
        "text_extract": {"path": args.text.as_posix(), "bytes": args.text.stat().st_size, "sha256": sha256(args.text), "characters": len(text)},
        "page_count": len(pages),
        "page_sizes_points": [
            {"width": width, "height": height, "pages": count}
            for (width, height), count in sorted(page_sizes.items())
        ],
        "annotation_count": annotation_count,
        "metadata_keys": sorted((reader.metadata or {}).keys()),
        "pattern_counts": pattern_counts,
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": report["status"], "pdf": report["pdf"], "page_count": len(pages), "checks": checks}, indent=2))
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
