#!/usr/bin/env python3
"""Structural and accessibility audit for the staged research-report DOCX."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

from lxml import etree
from PIL import Image

from build_report_docx import (
    RECORD_FIELD_PREFIX,
    RECORD_ROW_TAG,
    RECORD_TABLE_TAG,
    _record_heading_columns,
    parse_markdown,
)


NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

INLINE_RE = re.compile(
    r"(\\\(.+?\\\)|\*\*.+?\*\*|`.+?`|(?<!\*)\*[^*]+?\*(?!\*)|\[[^\]]+\]\([^\)]+\))"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def attr(node, name: str, namespace: str = "w") -> str | None:
    if node is None:
        return None
    return node.get(f"{{{NS[namespace]}}}{name}")


def parse_part(archive: zipfile.ZipFile, name: str):
    return etree.fromstring(archive.read(name))


def rendered_inline_text(text: str) -> str:
    """Return the exact visible text produced by build_report_docx.add_inline."""
    parts: list[str] = []
    cursor = 0
    for match in INLINE_RE.finditer(text):
        parts.append(text[cursor : match.start()])
        token = match.group(0)
        if token.startswith(r"\("):
            parts.append(token[2:-2])
        elif token.startswith("**"):
            parts.append(token[2:-2])
        elif token.startswith("`"):
            parts.append(token[1:-1])
        elif token.startswith("["):
            link = re.fullmatch(r"\[([^\]]+)\]\(([^\)]+)\)", token)
            if link:
                parts.append(f"{link.group(1)} ({link.group(2)})")
            else:
                parts.append(token)
        else:
            parts.append(token[1:-1])
        cursor = match.end()
    parts.append(text[cursor:])
    return "".join(parts)


def rendered_equation_text(source: str) -> str:
    """Mirror visible equation text; subscript formatting does not alter text."""
    text = source.replace(r"\,", " ")
    text = re.sub(r"_\{([^}]*)\}", r"\1", text)
    return re.sub(r"_(.)", r"\1", text)


def source_units(source_path: Path) -> tuple[list[tuple[str, object]], list[str], int]:
    """Create a semantic visible-text ledger from the source Markdown."""
    source_text = source_path.read_text(encoding="utf-8-sig")
    _, tokens = parse_markdown(source_text)
    units: list[tuple[str, object]] = []
    image_alts: list[str] = []
    for token in tokens:
        if token.kind in {"heading", "paragraph"}:
            units.append(("paragraph", rendered_inline_text(str(token.value))))
        elif token.kind == "equation":
            units.append(("paragraph", rendered_equation_text(str(token.value))))
        elif token.kind == "list":
            for item in token.value["items"]:
                units.append(("paragraph", rendered_inline_text(str(item))))
        elif token.kind == "table":
            rows = [
                [rendered_inline_text(str(cell)) for cell in row]
                for row in token.value
            ]
            units.append(("table", rows))
        elif token.kind == "image":
            image_alts.append(str(token.value.get("alt") or ""))
    return units, image_alts, source_text.count(r"\|\|")


def record_table_units(group) -> tuple[list[list[str]], list[str]]:
    """Reconstruct a source table from its visible semantic record fields.

    Values are read from the displayed Word fields, not an embedded source
    copy. Labels, order, field counts and paragraph text are checked too.
    """
    errors: list[str] = []
    headers: list[str] | None = None
    rows: list[list[str]] = []
    records = group.xpath("w:sdtContent/w:sdt", namespaces=NS)
    if not records:
        errors.append("Labelled-record group contains no records")
    for row_index, record in enumerate(records, start=1):
        if attr(record.find("w:sdtPr/w:tag", namespaces=NS), "val") != RECORD_ROW_TAG:
            errors.append(f"Labelled-record row {row_index}: unexpected record tag")
        fields = record.xpath("w:sdtContent/w:p/w:sdt", namespaces=NS)
        row: list[str] = []
        row_headers: list[str] = []
        for column_index, field in enumerate(fields):
            tag = attr(field.find("w:sdtPr/w:tag", namespaces=NS), "val")
            if tag != RECORD_FIELD_PREFIX + str(column_index):
                errors.append(f"Labelled-record row {row_index} column {column_index}: missing/reordered field tag {tag!r}")
            alias = attr(field.find("w:sdtPr/w:alias", namespaces=NS), "val")
            if alias is None:
                errors.append(f"Labelled-record row {row_index} column {column_index}: missing header identity")
            row_headers.append(rendered_inline_text(alias or ""))
            row.append("".join(field.xpath("w:sdtContent//w:t/text()", namespaces=NS)))
        if headers is None:
            headers = row_headers
        elif row_headers != headers:
            errors.append(f"Labelled-record row {row_index}: header sequence changed")
        if not fields:
            errors.append(f"Labelled-record row {row_index}: no displayed value fields")
        if headers:
            heading_columns = _record_heading_columns(headers)
            labelled = [f"{header}: {value}" for header, value in zip(row_headers, row)]
            expected_paragraphs = ["  ·  ".join(labelled[:heading_columns])] + labelled[heading_columns:]
            paragraphs = record.xpath("w:sdtContent/w:p", namespaces=NS)
            actual_paragraphs = ["".join(p.xpath(".//w:t/text()", namespaces=NS)) for p in paragraphs]
            if actual_paragraphs != expected_paragraphs:
                errors.append(f"Labelled-record row {row_index}: visible labels/separators/paragraphs changed")
            expected_styles = ["RecordHeading"] + ["RecordField"] * (len(expected_paragraphs) - 1)
            actual_styles = [attr(p.find("w:pPr/w:pStyle", namespaces=NS), "val") for p in paragraphs]
            if actual_styles != expected_styles:
                errors.append(f"Labelled-record row {row_index}: semantic paragraph styles changed")
        rows.append(row)
    return [headers or []] + rows, errors


def docx_units(document) -> tuple[list[tuple[str, object]], list[str], int, int, dict[str, object]]:
    """Extract main-story text/tables after the editorial cover."""
    units: list[tuple[str, object]] = []
    body = document.find("w:body", namespaces=NS)
    started = False
    record_errors: list[str] = []
    record_groups: list[dict[str, int]] = []
    for child in body:
        if child.tag == f"{{{NS['w']}}}p":
            text = "".join(child.xpath(".//w:t/text()", namespaces=NS))
            if not started:
                if text == "Abstract":
                    started = True
                else:
                    continue
            if text:
                units.append(("paragraph", text))
        elif child.tag == f"{{{NS['w']}}}tbl" and started:
            rows = []
            for row in child.xpath("w:tr", namespaces=NS):
                cells = [
                    "".join(cell.xpath(".//w:t/text()", namespaces=NS))
                    for cell in row.xpath("w:tc", namespaces=NS)
                ]
                rows.append(cells)
            units.append(("table", rows))
        elif child.tag == f"{{{NS['w']}}}sdt" and started:
            tag = attr(child.find("w:sdtPr/w:tag", namespaces=NS), "val")
            if tag != RECORD_TABLE_TAG:
                record_errors.append(f"Unexpected main-story structured group: {tag!r}")
                continue
            rows, errors = record_table_units(child)
            record_errors.extend(errors)
            record_groups.append({"rows": len(rows) - 1, "columns": len(rows[0]), "cells": sum(map(len, rows[1:]))})
            units.append(("table", rows))
    image_alts = [
        node.get("descr") or ""
        for node in document.xpath("//wp:docPr", namespaces=NS)
    ]
    table_text = [
        str(cell)
        for kind, value in units
        if kind == "table"
        for row in value
        for cell in row
    ]
    literal_double_pipes = sum(text.count("||") for text in table_text)
    residual_escaped_pipes = sum(text.count(r"\|") for text in table_text)
    return units, image_alts, literal_double_pipes, residual_escaped_pipes, {"groups": record_groups, "errors": record_errors}


def abbreviated(value: object, limit: int = 240) -> str:
    rendered = repr(value)
    return rendered if len(rendered) <= limit else rendered[: limit - 3] + "..."


def audit(
    docx_path: Path,
    render_dir: Path | None = None,
    source_path: Path | None = None,
    expected_source_sha256: str | None = None,
    model_spec_path: Path | None = None,
    expected_model_spec_sha256: str | None = None,
) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[dict[str, object]] = []

    with zipfile.ZipFile(docx_path) as archive:
        bad = archive.testzip()
        if bad:
            errors.append(f"ZIP CRC failure: {bad}")
        required = {"word/document.xml", "word/styles.xml", "word/numbering.xml"}
        missing = sorted(required.difference(archive.namelist()))
        if missing:
            errors.append("Missing OOXML parts: " + ", ".join(missing))
        document = parse_part(archive, "word/document.xml")
        styles = parse_part(archive, "word/styles.xml")
        numbering = parse_part(archive, "word/numbering.xml")

    sections = document.xpath("//w:sectPr", namespaces=NS)
    orientation_counts = {"portrait": 0, "landscape": 0}
    for index, section in enumerate(sections, start=1):
        pgsz = section.find("w:pgSz", namespaces=NS)
        width = int(attr(pgsz, "w") or 0)
        height = int(attr(pgsz, "h") or 0)
        orientation = attr(pgsz, "orient") or "portrait"
        if orientation == "landscape" or width > height:
            orientation_counts["landscape"] += 1
            expected = (15840, 12240)
        else:
            orientation_counts["portrait"] += 1
            expected = (12240, 15840)
        if (width, height) != expected:
            errors.append(f"Section {index}: page size {(width, height)} != {expected}")
        pgmar = section.find("w:pgMar", namespaces=NS)
        for side in ("top", "right", "bottom", "left"):
            if int(attr(pgmar, side) or 0) != 1440:
                errors.append(f"Section {index}: {side} margin is not 1440 DXA")
        for side in ("header", "footer"):
            value = int(attr(pgmar, side) or 0)
            if abs(value - 708) > 1:
                errors.append(f"Section {index}: {side} distance {value} is not 708 DXA")

    expected_styles = {
        "Normal": {"size": "22", "after": "160", "line": "320"},
        "Heading1": {"size": "32", "before": "360", "after": "200", "color": "2E74B5"},
        "Heading2": {"size": "26", "before": "240", "after": "120", "color": "2E74B5"},
        "Heading3": {"size": "24", "before": "160", "after": "80", "color": "1F4D78"},
        "RecordHeading": {"size": "22", "before": "200", "after": "80", "line": "274", "color": "1F4D78", "alignment": "left"},
        "RecordField": {"size": "20", "before": "0", "after": "80", "line": "274", "alignment": "left"},
    }
    for style_id, expected in expected_styles.items():
        nodes = styles.xpath(f"//w:style[@w:styleId='{style_id}']", namespaces=NS)
        if not nodes:
            errors.append(f"Missing required style {style_id}")
            continue
        style = nodes[0]
        size = attr(style.find("w:rPr/w:sz", namespaces=NS), "val")
        spacing = style.find("w:pPr/w:spacing", namespaces=NS)
        color = attr(style.find("w:rPr/w:color", namespaces=NS), "val")
        if size != expected["size"]:
            errors.append(f"{style_id}: size {size} != {expected['size']}")
        for key in ("before", "after", "line"):
            if key in expected and attr(spacing, key) != expected[key]:
                errors.append(f"{style_id}: {key} {attr(spacing, key)} != {expected[key]}")
        if "color" in expected and color != expected["color"]:
            errors.append(f"{style_id}: color {color} != {expected['color']}")
        if "alignment" in expected and attr(style.find("w:pPr/w:jc", namespaces=NS), "val") != expected["alignment"]:
            errors.append(f"{style_id}: alignment is not {expected['alignment']}")

    tables = document.xpath("//w:tbl", namespaces=NS)
    table_widths: list[int] = []
    for table_index, table in enumerate(tables, start=1):
        tblw = table.find("w:tblPr/w:tblW", namespaces=NS)
        tblind = table.find("w:tblPr/w:tblInd", namespaces=NS)
        layout = table.find("w:tblPr/w:tblLayout", namespaces=NS)
        width = int(attr(tblw, "w") or 0)
        table_widths.append(width)
        if attr(tblw, "type") != "dxa" or width not in {9360, 12960}:
            errors.append(f"Table {table_index}: invalid explicit width {width}")
        if int(attr(tblind, "w") or -1) != 120 or attr(tblind, "type") != "dxa":
            errors.append(f"Table {table_index}: tblInd is not 120 DXA")
        if attr(layout, "type") != "fixed":
            errors.append(f"Table {table_index}: layout is not fixed")
        grid = [int(attr(col, "w") or 0) for col in table.xpath("w:tblGrid/w:gridCol", namespaces=NS)]
        if sum(grid) != width:
            errors.append(f"Table {table_index}: grid sum {sum(grid)} != tblW {width}")
        rows = table.xpath("w:tr", namespaces=NS)
        if not rows or rows[0].find("w:trPr/w:tblHeader", namespaces=NS) is None:
            errors.append(f"Table {table_index}: first row lacks repeating header flag")
        for row_index, row in enumerate(rows, start=1):
            if row.find("w:trPr/w:cantSplit", namespaces=NS) is None:
                errors.append(f"Table {table_index} row {row_index}: row can split across pages")
            cells = row.xpath("w:tc", namespaces=NS)
            widths = [int(attr(cell.find("w:tcPr/w:tcW", namespaces=NS), "w") or 0) for cell in cells]
            if len(widths) == len(grid) and widths != grid:
                errors.append(f"Table {table_index} row {row_index}: tcW does not match tblGrid")

    image_nodes = document.xpath("//wp:docPr", namespaces=NS)
    missing_alt = [int(node.get("id", "0")) for node in image_nodes if not (node.get("descr") or "").strip()]
    if missing_alt:
        errors.append(f"Images missing meaningful descr alt text: {missing_alt}")

    list_paragraphs = document.xpath("//w:p[w:pPr/w:numPr]", namespaces=NS)
    abstract_nums = numbering.xpath("//w:abstractNum", namespaces=NS)
    nums = numbering.xpath("//w:num", namespaces=NS)
    if not list_paragraphs:
        errors.append("No real numbered/bulleted paragraphs found")
    if not abstract_nums or not nums:
        errors.append("Numbering definitions are missing")

    heading_levels: list[int] = []
    for pstyle in document.xpath("//w:p/w:pPr/w:pStyle", namespaces=NS):
        value = attr(pstyle, "val") or ""
        match = re.fullmatch(r"Heading([123])", value)
        if match:
            heading_levels.append(int(match.group(1)))
        elif value == "RecordHeading":
            heading_levels.append(2)
    for previous, current in zip(heading_levels, heading_levels[1:]):
        if current > previous + 1:
            errors.append(f"Heading hierarchy skips from {previous} to {current}")

    visible_text = " ".join(document.xpath("//w:t/text()", namespaces=NS))
    for pattern, label in (
        (r"codex-file-citation", "Codex file citation token"),
        (r"turn\d+(?:search|view|fetch)\d+", "tool citation token"),
        (r"\[PLACEHOLDER\]|\bTBD\b", "placeholder text"),
    ):
        if re.search(pattern, visible_text, re.I):
            errors.append(f"Visible {label} remains")

    source_roundtrip = None
    source_roundtrip_passed = source_path is None
    actual_units, actual_alts, literal_pipes, residual_pipes, record_audit = docx_units(document)
    errors.extend(record_audit["errors"])
    if expected_source_sha256 and source_path is None:
        errors.append("An expected source SHA-256 was supplied without --source")
    if source_path is not None:
        source_hash = sha256(source_path)
        if expected_source_sha256 and source_hash != expected_source_sha256.upper():
            errors.append(
                f"Source SHA-256 {source_hash} != expected {expected_source_sha256.upper()}"
            )
        expected_units, expected_alts, escaped_pipes = source_units(source_path)
        mismatch = None
        for index, (expected, actual) in enumerate(
            zip(expected_units, actual_units, strict=False), start=1
        ):
            if expected != actual:
                mismatch = {
                    "unit": index,
                    "expected": abbreviated(expected),
                    "actual": abbreviated(actual),
                }
                errors.append(
                    f"Source round-trip mismatch at semantic unit {index}: "
                    f"expected {abbreviated(expected)}, actual {abbreviated(actual)}"
                )
                break
        if len(expected_units) != len(actual_units):
            errors.append(
                f"Source round-trip unit count {len(actual_units)} != expected {len(expected_units)}"
            )
        if expected_alts != actual_alts:
            errors.append(
                f"Source image alt-text sequence {actual_alts!r} != expected {expected_alts!r}"
            )
        if escaped_pipes != literal_pipes or residual_pipes:
            errors.append(
                "Escaped-pipe round-trip failed: "
                f"source={escaped_pipes}, docx_literal={literal_pipes}, residual={residual_pipes}"
            )
        source_roundtrip_passed = (
            mismatch is None
            and len(expected_units) == len(actual_units)
            and expected_alts == actual_alts
            and escaped_pipes == literal_pipes
            and residual_pipes == 0
        )
        source_roundtrip = {
            "source": str(source_path.resolve()),
            "bytes": source_path.stat().st_size,
            "sha256": source_hash,
            "expected_sha256": expected_source_sha256.upper() if expected_source_sha256 else None,
            "expected_units": len(expected_units),
            "actual_units": len(actual_units),
            "image_alt_texts": len(actual_alts),
            "source_escaped_double_pipes": escaped_pipes,
            "docx_literal_double_pipes": literal_pipes,
            "docx_residual_escaped_pipes": residual_pipes,
            "first_mismatch": mismatch,
        }

    model_spec_identity = None
    if expected_model_spec_sha256 and model_spec_path is None:
        errors.append("An expected MODEL_SPEC SHA-256 was supplied without --model-spec")
    if model_spec_path is not None:
        model_spec_hash = sha256(model_spec_path)
        if expected_model_spec_sha256 and model_spec_hash != expected_model_spec_sha256.upper():
            errors.append(
                f"MODEL_SPEC SHA-256 {model_spec_hash} != expected "
                f"{expected_model_spec_sha256.upper()}"
            )
        model_spec_identity = {
            "file": str(model_spec_path.resolve()),
            "bytes": model_spec_path.stat().st_size,
            "sha256": model_spec_hash,
            "expected_sha256": (
                expected_model_spec_sha256.upper() if expected_model_spec_sha256 else None
            ),
        }

    render_report = None
    if render_dir is not None:
        pages = sorted(render_dir.glob("page-*.png"), key=lambda p: int(re.search(r"(\d+)", p.stem).group(1)))
        ink_ratios: dict[str, float] = {}
        for page in pages:
            with Image.open(page) as image:
                grayscale = image.convert("L").resize((200, 260))
                pixels = list(grayscale.get_flattened_data()) if hasattr(grayscale, "get_flattened_data") else list(grayscale.getdata())
            ink_ratios[page.name] = sum(value < 242 for value in pixels) / len(pixels)
        blank_pages = [name for name, ratio in ink_ratios.items() if ratio < 0.006]
        sparse_pages = [name for name, ratio in ink_ratios.items() if 0.006 <= ratio < 0.015]
        render_report = {
            "page_count": len(pages),
            "pages": [p.name for p in pages],
            "blank_page_candidates": blank_pages,
            "sparse_page_candidates": sparse_pages,
            "minimum_ink_ratio": min(ink_ratios.values(), default=None),
        }
        if not pages:
            errors.append("Render directory contains no page PNGs")
        zero_byte = [p.name for p in pages if p.stat().st_size == 0]
        if zero_byte:
            errors.append("Zero-byte rendered pages: " + ", ".join(zero_byte))
        if blank_pages:
            errors.append("Rendered blank-page candidates: " + ", ".join(blank_pages))
        if sparse_pages:
            warnings.append("Visually sparse pages to inspect: " + ", ".join(sparse_pages))

    checks.extend(
        [
            {"name": "zip_crc", "passed": not any("ZIP CRC" in e for e in errors)},
            {"name": "section_geometry", "passed": not any(e.startswith("Section ") for e in errors)},
            {"name": "preset_styles", "passed": not any(e.startswith(tuple(expected_styles)) for e in errors)},
            {"name": "table_geometry_and_headers", "passed": not any(e.startswith("Table ") for e in errors)},
            {"name": "labelled_record_structure", "passed": not record_audit["errors"]},
            {"name": "image_alt_text", "passed": not missing_alt},
            {"name": "real_numbering", "passed": bool(list_paragraphs and abstract_nums and nums)},
            {"name": "heading_hierarchy", "passed": not any("Heading hierarchy" in e for e in errors)},
            {"name": "token_hygiene", "passed": not any("token" in e.lower() or "placeholder" in e.lower() for e in errors)},
            {
                "name": "source_text_roundtrip",
                "passed": source_roundtrip_passed,
            },
            {
                "name": "input_hash_guards",
                "passed": not any("sha-256" in e.lower() for e in errors),
            },
        ]
    )

    return {
        "status": "PASS" if not errors else "FAIL",
        "file": str(docx_path.resolve()),
        "bytes": docx_path.stat().st_size,
        "sha256": sha256(docx_path),
        "sections": len(sections),
        "orientations": orientation_counts,
        "tables": len(tables),
        "table_widths_dxa": table_widths,
        "labelled_records": record_audit,
        "images": len(image_nodes),
        "real_list_paragraphs": len(list_paragraphs),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "render": render_report,
        "source_roundtrip": source_roundtrip,
        "model_spec_identity": model_spec_identity,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    parser.add_argument("--render-dir", type=Path)
    parser.add_argument("--source", type=Path, help="Optional PAPER.md for semantic text round-trip QA")
    parser.add_argument("--expected-source-sha256")
    parser.add_argument("--model-spec", type=Path, help="Optional controlling model specification identity")
    parser.add_argument("--expected-model-spec-sha256")
    parser.add_argument("--out-json", type=Path)
    args = parser.parse_args()
    report = audit(
        args.docx.resolve(),
        args.render_dir.resolve() if args.render_dir else None,
        args.source.resolve() if args.source else None,
        args.expected_source_sha256,
        args.model_spec.resolve() if args.model_spec else None,
        args.expected_model_spec_sha256,
    )
    encoded = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
