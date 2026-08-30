from __future__ import annotations

import collections
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import unicodedata
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import pdfplumber
from PIL import Image, ImageDraw, ImageOps
from pypdf import PdfReader


OUTPUT_DIR = Path(__file__).resolve().parent
TASK_ROOT = OUTPUT_DIR.parents[1]
WORKSPACE_ROOT = TASK_ROOT
PDF_PATH = TASK_ROOT / "PAPER.pdf"
RENDER_DIR = TASK_ROOT / "rendered_pages"
DOCX_PATH = TASK_ROOT / "PAPER.docx"
MARKDOWN_PATH = TASK_ROOT / "PAPER.md"
FACTS_PATH = OUTPUT_DIR / "FINAL_PDF_MECHANICAL_AUDIT_20260830.json"
CONTACT_DIR = OUTPUT_DIR / "contact_sheets"
EXPECTED_PAGES = 109

EXPECTED_IDENTIFIERS = {
    "title": "Allocating AI Translation Compute for Marginal Educational Access",
    "subtitle": "A global language, interlanguage, accessibility, and open-curriculum portfolio model",
    "report_date": "2026-08-30",
    "model_identity": "OpenAI Codex gpt-5.6-sol, Ultra",
    "population_observation_count": "475 population observations",
    "source_record_count": "81 registered source records",
    "authority_count": "58 distinct authority labels",
    "candidate_intervention_count": "143 exact natural-language/profile interventions",
    "eligible_intervention_count": "134 passed the cardinal eligibility gate",
    "base_top100_compute": "407.305 million",
    "high_top100_compute": "1.866 billion gross tokens",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def rel(path: Path) -> str:
    return path.resolve().relative_to(WORKSPACE_ROOT).as_posix()


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value)).strip()


def canonical_identifier_text(value: str) -> str:
    """Comparison form resilient to PDF line-end hyphen extraction behavior."""
    return "".join(character.casefold() for character in unicodedata.normalize("NFKC", value) if character.isalnum())


def safe_string(value: Any) -> str:
    text = str(value)
    profile_name = Path.home().name
    if profile_name:
        text = re.sub(re.escape(profile_name), "[REDACTED_PROFILE_NAME]", text, flags=re.I)
    text = text.replace(str(WORKSPACE_ROOT), "<workspace>")
    text = text.replace(str(Path.home()), "<home>")
    return text


def safe_mapping(value: Any) -> Any:
    if isinstance(value, dict):
        return {safe_string(k): safe_mapping(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe_mapping(v) for v in value]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return safe_string(value)


def dereference(value: Any) -> Any:
    try:
        return value.get_object()
    except AttributeError:
        return value


def rect(box: Any) -> list[float]:
    return [round(float(box.left), 4), round(float(box.bottom), 4), round(float(box.right), 4), round(float(box.top), 4)]


def run_tool(arguments: list[str]) -> dict[str, Any]:
    try:
        proc = subprocess.run(arguments, capture_output=True, check=False)
    except FileNotFoundError:
        return {"status": "UNAVAILABLE", "command": arguments[0]}
    stdout = proc.stdout
    stderr = proc.stderr
    return {
        "status": "PASS" if proc.returncode == 0 else "FAIL",
        "command": arguments[0],
        "returncode": proc.returncode,
        "stdout_bytes": len(stdout),
        "stdout_sha256": sha256_bytes(stdout),
        "stderr_bytes": len(stderr),
        "stderr_sha256": sha256_bytes(stderr),
        "stdout": stdout,
        "stderr": stderr,
    }


def extract_docx_text(xml_bytes: bytes) -> str:
    root = ET.fromstring(xml_bytes)
    chunks: list[str] = []
    for node in root.iter():
        local = node.tag.rsplit("}", 1)[-1]
        if local == "t" and node.text:
            chunks.append(node.text)
        elif local == "tab":
            chunks.append("\t")
        elif local in {"br", "cr", "p"}:
            chunks.append("\n")
    return "".join(chunks)


def parse_properties(xml_bytes: bytes) -> dict[str, str]:
    root = ET.fromstring(xml_bytes)
    result: dict[str, str] = {}
    for child in root:
        key = child.tag.rsplit("}", 1)[-1]
        result[key] = safe_string(child.text or "")
    return result


def identifier_results(text: str) -> dict[str, dict[str, Any]]:
    normalized = normalize_text(text)
    canonical = canonical_identifier_text(text)
    return {
        key: {
            "expected": value,
            "present": value in normalized,
            "count": normalized.count(value),
            "canonical_present": canonical_identifier_text(value) in canonical,
        }
        for key, value in EXPECTED_IDENTIFIERS.items()
    }


def inspect_docx() -> tuple[dict[str, Any], str]:
    result: dict[str, Any] = {
        "path": rel(DOCX_PATH),
        "bytes": DOCX_PATH.stat().st_size,
        "sha256": sha256(DOCX_PATH),
    }
    with zipfile.ZipFile(DOCX_PATH) as archive:
        bad_part = archive.testzip()
        names = archive.namelist()
        result["zip_integrity"] = "PASS" if bad_part is None else "FAIL"
        result["bad_zip_part"] = bad_part
        result["package_part_count"] = len(names)
        result["has_main_document"] = "word/document.xml" in names
        result["has_comments_part"] = "word/comments.xml" in names
        result["has_custom_properties"] = "docProps/custom.xml" in names
        core = parse_properties(archive.read("docProps/core.xml")) if "docProps/core.xml" in names else {}
        app = parse_properties(archive.read("docProps/app.xml")) if "docProps/app.xml" in names else {}
        main_text = extract_docx_text(archive.read("word/document.xml"))
        result["core_properties"] = core
        result["application_properties"] = {
            key: app.get(key, "")
            for key in ("Application", "AppVersion", "Pages", "Words", "Characters", "Company")
            if key in app
        }
    result["normalized_text_characters"] = len(normalize_text(main_text))
    result["normalized_text_sha256"] = sha256_bytes(normalize_text(main_text).encode("utf-8"))
    result["identifiers"] = identifier_results(main_text)
    return result, main_text


def inspect_markdown() -> tuple[dict[str, Any], str]:
    text = MARKDOWN_PATH.read_text(encoding="utf-8")
    result = {
        "path": rel(MARKDOWN_PATH),
        "bytes": MARKDOWN_PATH.stat().st_size,
        "sha256": sha256(MARKDOWN_PATH),
        "normalized_text_characters": len(normalize_text(text)),
        "normalized_text_sha256": sha256_bytes(normalize_text(text).encode("utf-8")),
        "identifiers": identifier_results(text),
    }
    return result, text


def inspect_pdf() -> tuple[dict[str, Any], list[str], list[str]]:
    strict_status = "PASS"
    strict_error = ""
    try:
        strict_reader = PdfReader(str(PDF_PATH), strict=True)
        _ = len(strict_reader.pages)
        for strict_page in strict_reader.pages:
            _ = strict_page.mediabox
    except Exception as exc:  # audit capture
        strict_status = "FAIL"
        strict_error = safe_string(f"{type(exc).__name__}: {exc}")

    reader = PdfReader(str(PDF_PATH), strict=False)
    if reader.is_encrypted:
        try:
            decrypt_result = reader.decrypt("")
        except Exception as exc:  # audit capture
            decrypt_result = safe_string(f"ERROR: {type(exc).__name__}: {exc}")
    else:
        decrypt_result = "not_required"

    root = dereference(reader.trailer["/Root"])
    metadata = safe_mapping(dict(reader.metadata or {}))
    xmp_status: dict[str, Any]
    try:
        xmp = reader.xmp_metadata
        if xmp is None:
            xmp_status = {"present": False}
        else:
            xmp_status = {
                "present": True,
                "dc_title": safe_mapping(getattr(xmp, "dc_title", None)),
                "dc_creator": safe_mapping(getattr(xmp, "dc_creator", None)),
                "dc_subject": safe_mapping(getattr(xmp, "dc_subject", None)),
                "pdf_keywords": safe_mapping(getattr(xmp, "pdf_keywords", None)),
                "pdf_producer": safe_mapping(getattr(xmp, "pdf_producer", None)),
                "xmp_create_date": safe_mapping(getattr(xmp, "xmp_create_date", None)),
                "xmp_modify_date": safe_mapping(getattr(xmp, "xmp_modify_date", None)),
            }
    except Exception as exc:  # audit capture
        xmp_status = {"present": "ERROR", "error": safe_string(f"{type(exc).__name__}: {exc}")}

    names = dereference(root.get("/Names")) if root.get("/Names") is not None else None
    name_tree_keys = sorted(str(k) for k in names.keys()) if isinstance(names, dict) else []
    acroform = dereference(root.get("/AcroForm")) if root.get("/AcroForm") is not None else None
    top_level_fields = []
    if isinstance(acroform, dict) and acroform.get("/Fields") is not None:
        top_level_fields = list(dereference(acroform.get("/Fields")))
    try:
        field_map = reader.get_fields() or {}
        field_error = ""
    except Exception as exc:  # audit capture
        field_map = {}
        field_error = safe_string(f"{type(exc).__name__}: {exc}")

    annotation_types: collections.Counter[str] = collections.Counter()
    action_types: collections.Counter[str] = collections.Counter()
    annotation_pages: dict[int, int] = {}
    widget_pages: list[int] = []
    page_additional_actions: list[int] = []
    page_box_presence: dict[str, list[int]] = {key: [] for key in ("/MediaBox", "/CropBox", "/BleedBox", "/TrimBox", "/ArtBox")}
    effective_box_counter: dict[str, collections.Counter[tuple[float, ...]]] = {
        key: collections.Counter() for key in ("media", "crop", "bleed", "trim", "art")
    }
    rotation_counter: collections.Counter[int] = collections.Counter()
    orientation_counter: collections.Counter[str] = collections.Counter()
    user_unit_counter: collections.Counter[float] = collections.Counter()
    pypdf_texts: list[str] = []
    contentless_pages: list[int] = []

    for page_number, page in enumerate(reader.pages, start=1):
        raw_page = page
        for key in page_box_presence:
            if key in raw_page:
                page_box_presence[key].append(page_number)
        boxes = {
            "media": page.mediabox,
            "crop": page.cropbox,
            "bleed": page.bleedbox,
            "trim": page.trimbox,
            "art": page.artbox,
        }
        for key, value in boxes.items():
            effective_box_counter[key][tuple(rect(value))] += 1
        media_width = float(page.mediabox.width)
        media_height = float(page.mediabox.height)
        rotation = int(page.get("/Rotate", 0) or 0) % 360
        rotation_counter[rotation] += 1
        effective_width, effective_height = (media_height, media_width) if rotation in {90, 270} else (media_width, media_height)
        orientation_counter["landscape" if effective_width > effective_height else "portrait"] += 1
        user_unit_counter[float(page.get("/UserUnit", 1) or 1)] += 1
        if page.get("/AA") is not None:
            page_additional_actions.append(page_number)

        contents = page.get_contents()
        if contents is None:
            contentless_pages.append(page_number)

        text = page.extract_text() or ""
        pypdf_texts.append(text)

        annots = page.get("/Annots")
        if annots is None:
            continue
        resolved_annots = dereference(annots)
        annotation_pages[page_number] = len(resolved_annots)
        for annot_ref in resolved_annots:
            annot = dereference(annot_ref)
            subtype = str(annot.get("/Subtype", "UNSPECIFIED"))
            annotation_types[subtype] += 1
            if subtype == "/Widget":
                widget_pages.append(page_number)
            action = dereference(annot.get("/A")) if annot.get("/A") is not None else None
            if isinstance(action, dict):
                action_types[str(action.get("/S", "UNSPECIFIED"))] += 1
            if annot.get("/AA") is not None:
                action_types["ANNOTATION_ADDITIONAL_ACTION"] += 1

    plumber_texts: list[str] = []
    plumber_error = ""
    try:
        with pdfplumber.open(PDF_PATH) as pdf:
            plumber_texts = [(page.extract_text() or "") for page in pdf.pages]
    except Exception as exc:  # audit capture
        plumber_error = safe_string(f"{type(exc).__name__}: {exc}")

    def text_summary(texts: list[str]) -> dict[str, Any]:
        normalized_pages = [normalize_text(text) for text in texts]
        char_counts = [len(text) for text in normalized_pages]
        word_counts = [len(text.split()) for text in normalized_pages]
        empty_pages = [index + 1 for index, text in enumerate(normalized_pages) if not text]
        minimum = min(char_counts) if char_counts else 0
        maximum = max(char_counts) if char_counts else 0
        return {
            "page_count": len(texts),
            "total_normalized_characters": sum(char_counts),
            "total_words_by_whitespace": sum(word_counts),
            "empty_text_pages": empty_pages,
            "minimum_page_characters": minimum,
            "minimum_character_pages": [index + 1 for index, count in enumerate(char_counts) if count == minimum],
            "maximum_page_characters": maximum,
            "maximum_character_pages": [index + 1 for index, count in enumerate(char_counts) if count == maximum],
            "replacement_character_count": sum(text.count("\ufffd") for text in texts),
            "nul_character_count": sum(text.count("\x00") for text in texts),
            "normalized_text_sha256": sha256_bytes("\n\f\n".join(normalized_pages).encode("utf-8")),
        }

    all_pypdf_text = "\n\f\n".join(pypdf_texts)
    suspicious_patterns = {
        "todo": r"\bTODO\b",
        "tbd": r"\bTBD\b",
        "placeholder": r"\bPLACEHOLDER\b",
        "codex_file_citation": r"codex-file-citation",
        "tool_reference_token": r"turn\d+(?:search|fetch|view)\d+",
        "unresolved_double_braces": r"\{\{[^{}]+\}\}",
        "unresolved_double_brackets": r"\[\[[^\[\]]+\]\]",
    }
    suspicious_counts = {
        key: len(re.findall(pattern, all_pypdf_text, flags=re.I))
        for key, pattern in suspicious_patterns.items()
    }

    first_bytes = PDF_PATH.read_bytes()[:4096]
    trailer_id = reader.trailer.get("/ID")
    result = {
        "path": rel(PDF_PATH),
        "bytes": PDF_PATH.stat().st_size,
        "sha256": sha256(PDF_PATH),
        "pdf_header": safe_string(getattr(reader, "pdf_header", "")),
        "linearized": b"/Linearized" in first_bytes,
        "strict_parse_status": strict_status,
        "strict_parse_error": strict_error,
        "page_count": len(reader.pages),
        "expected_page_count": EXPECTED_PAGES,
        "page_count_status": "PASS" if len(reader.pages) == EXPECTED_PAGES else "FAIL",
        "is_encrypted": reader.is_encrypted,
        "decrypt_result": decrypt_result,
        "trailer_id_present": trailer_id is not None,
        "metadata": metadata,
        "xmp_metadata": xmp_status,
        "catalog_security_and_payload_flags": {
            "open_action_present": root.get("/OpenAction") is not None,
            "catalog_additional_actions_present": root.get("/AA") is not None,
            "name_tree_keys": name_tree_keys,
            "javascript_name_tree_present": "/JavaScript" in name_tree_keys,
            "embedded_files_name_tree_present": "/EmbeddedFiles" in name_tree_keys,
            "page_additional_action_pages": page_additional_actions,
        },
        "forms_and_annotations": {
            "acroform_present": acroform is not None,
            "top_level_acroform_field_count": len(top_level_fields),
            "get_fields_count": len(field_map),
            "get_fields_error": field_error,
            "widget_count": annotation_types.get("/Widget", 0),
            "widget_pages": sorted(set(widget_pages)),
            "annotation_count": sum(annotation_types.values()),
            "annotation_types": dict(sorted(annotation_types.items())),
            "annotation_pages": {str(k): v for k, v in sorted(annotation_pages.items())},
            "annotation_action_types": dict(sorted(action_types.items())),
        },
        "page_geometry": {
            "raw_box_presence_counts": {key: len(value) for key, value in page_box_presence.items()},
            "effective_boxes": {
                key: [
                    {"rectangle_points": list(rectangle), "page_count": count}
                    for rectangle, count in counter.items()
                ]
                for key, counter in effective_box_counter.items()
            },
            "rotations": {str(key): value for key, value in sorted(rotation_counter.items())},
            "orientations": dict(sorted(orientation_counter.items())),
            "user_units": {str(key): value for key, value in sorted(user_unit_counter.items())},
            "pages_without_content_streams": contentless_pages,
        },
        "text_extraction": {
            "pypdf": text_summary(pypdf_texts),
            "pdfplumber": text_summary(plumber_texts) if plumber_texts else {"status": "FAIL", "error": plumber_error},
            "identifiers": identifier_results(all_pypdf_text),
            "suspicious_token_counts": suspicious_counts,
        },
    }
    return result, pypdf_texts, plumber_texts


def inspect_external_pdf_tools() -> dict[str, Any]:
    pdfinfo_run = run_tool(["pdfinfo", str(PDF_PATH)])
    pdfinfo_selected: dict[str, str] = {}
    if pdfinfo_run.get("status") == "PASS":
        decoded = pdfinfo_run["stdout"].decode("utf-8", errors="replace")
        for line in decoded.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            if key.strip() in {
                "Title", "Subject", "Keywords", "Author", "Creator", "Producer",
                "CreationDate", "ModDate", "Custom Metadata", "Metadata Stream",
                "Tagged", "UserProperties", "Suspects", "Form", "JavaScript",
                "Pages", "Encrypted", "Page size", "Page rot", "File size",
                "Optimized", "PDF version",
            }:
                pdfinfo_selected[key.strip()] = safe_string(value.strip())
    pdfinfo_clean = {key: value for key, value in pdfinfo_run.items() if key not in {"stdout", "stderr"}}
    pdfinfo_clean["selected_fields"] = pdfinfo_selected

    pdffonts_run = run_tool(["pdffonts", str(PDF_PATH)])
    font_rows: list[dict[str, Any]] = []
    if pdffonts_run.get("status") == "PASS":
        decoded = pdffonts_run["stdout"].decode("utf-8", errors="replace")
        for line in decoded.splitlines()[2:]:
            parts = line.split()
            if len(parts) < 8:
                continue
            font_rows.append({
                "name": safe_string(parts[0]),
                "embedded": parts[-5].lower() == "yes",
                "subset": parts[-4].lower() == "yes",
                "unicode_map": parts[-3].lower() == "yes",
            })
    pdffonts_clean = {key: value for key, value in pdffonts_run.items() if key not in {"stdout", "stderr"}}
    pdffonts_clean.update({
        "font_row_count": len(font_rows),
        "all_fonts_embedded": bool(font_rows) and all(row["embedded"] for row in font_rows),
        "all_fonts_have_unicode_map": bool(font_rows) and all(row["unicode_map"] for row in font_rows),
        "font_rows": font_rows,
    })

    pdftotext_run = run_tool(["pdftotext", "-enc", "UTF-8", str(PDF_PATH), "-"])
    pdftotext_clean = {key: value for key, value in pdftotext_run.items() if key not in {"stdout", "stderr"}}
    if pdftotext_run.get("status") == "PASS":
        decoded = pdftotext_run["stdout"].decode("utf-8", errors="replace")
        pdftotext_clean.update({
            "decoded_characters": len(decoded),
            "normalized_characters": len(normalize_text(decoded)),
            "replacement_character_count": decoded.count("\ufffd"),
            "identifiers": identifier_results(decoded),
        })
    return {"pdfinfo": pdfinfo_clean, "pdffonts": pdffonts_clean, "pdftotext": pdftotext_clean}


def image_ink_ratio(image: Image.Image, threshold: int = 245) -> float:
    gray = ImageOps.grayscale(image)
    histogram = gray.histogram()
    ink = sum(histogram[: threshold + 1])
    return ink / (gray.width * gray.height)


def inspect_rendered_pages() -> dict[str, Any]:
    pattern = re.compile(r"^page-(\d+)\.png$", flags=re.I)
    indexed: list[tuple[int, Path]] = []
    for path in RENDER_DIR.iterdir():
        match = pattern.match(path.name)
        if match:
            indexed.append((int(match.group(1)), path))
    indexed.sort()
    numbers = [number for number, _ in indexed]
    expected_numbers = list(range(1, EXPECTED_PAGES + 1))
    missing = sorted(set(expected_numbers) - set(numbers))
    extra = sorted(set(numbers) - set(expected_numbers))
    duplicates = sorted(number for number, count in collections.Counter(numbers).items() if count > 1)

    dimensions: collections.Counter[tuple[int, int]] = collections.Counter()
    modes: collections.Counter[str] = collections.Counter()
    invalid_pages: list[int] = []
    ink_ratios: list[tuple[int, float]] = []
    for number, path in indexed:
        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                dimensions[image.size] += 1
                modes[image.mode] += 1
                ink_ratios.append((number, image_ink_ratio(image)))
        except Exception:
            invalid_pages.append(number)

    CONTACT_DIR.mkdir(parents=True, exist_ok=True)
    for old in CONTACT_DIR.glob("contact-*.png"):
        old.unlink()
    page_width = 220
    page_height = 311
    label_height = 24
    padding = 10
    columns = 4
    rows = 3
    per_sheet = columns * rows
    contact_paths: list[str] = []
    for sheet_index in range(0, len(indexed), per_sheet):
        subset = indexed[sheet_index : sheet_index + per_sheet]
        canvas_width = padding + columns * (page_width + padding)
        canvas_height = padding + rows * (label_height + page_height + padding)
        canvas = Image.new("RGB", (canvas_width, canvas_height), "#D6D6D6")
        draw = ImageDraw.Draw(canvas)
        for offset, (number, path) in enumerate(subset):
            row = offset // columns
            column = offset % columns
            x = padding + column * (page_width + padding)
            y = padding + row * (label_height + page_height + padding)
            draw.text((x + 4, y + 4), f"Page {number}", fill="black")
            with Image.open(path) as image:
                thumb = image.convert("RGB")
                thumb.thumbnail((page_width, page_height), Image.Resampling.LANCZOS)
                page_canvas = Image.new("RGB", (page_width, page_height), "white")
                px = (page_width - thumb.width) // 2
                py = (page_height - thumb.height) // 2
                page_canvas.paste(thumb, (px, py))
                canvas.paste(page_canvas, (x, y + label_height))
        contact_path = CONTACT_DIR / f"contact-{sheet_index // per_sheet + 1:02d}.png"
        canvas.save(contact_path, optimize=True)
        contact_paths.append(rel(contact_path))

    minimum_ratio = min((ratio for _, ratio in ink_ratios), default=0.0)
    maximum_ratio = max((ratio for _, ratio in ink_ratios), default=0.0)
    return {
        "directory": rel(RENDER_DIR),
        "png_count": len(indexed),
        "expected_png_count": EXPECTED_PAGES,
        "numbers_sequential_expected_range": numbers == expected_numbers,
        "missing_page_numbers": missing,
        "extra_page_numbers": extra,
        "duplicate_page_numbers": duplicates,
        "invalid_or_undecodable_pages": invalid_pages,
        "dimensions": [
            {"width": width, "height": height, "page_count": count}
            for (width, height), count in dimensions.items()
        ],
        "modes": dict(modes),
        "minimum_ink_ratio": round(minimum_ratio, 8),
        "minimum_ink_ratio_pages": [number for number, ratio in ink_ratios if ratio == minimum_ratio],
        "maximum_ink_ratio": round(maximum_ratio, 8),
        "maximum_ink_ratio_pages": [number for number, ratio in ink_ratios if ratio == maximum_ratio],
        "raster_blank_pages_at_0_0001_ink_ratio": [number for number, ratio in ink_ratios if ratio < 0.0001],
        "contact_sheets": contact_paths,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in (PDF_PATH, DOCX_PATH, MARKDOWN_PATH):
        if not path.is_file():
            raise FileNotFoundError(path)

    docx, docx_text = inspect_docx()
    markdown, markdown_text = inspect_markdown()
    pdf, pypdf_texts, plumber_texts = inspect_pdf()
    external_tools = inspect_external_pdf_tools()
    rendered_pages = inspect_rendered_pages()

    identifier_matrix: dict[str, dict[str, Any]] = {}
    pdf_text = "\n\f\n".join(pypdf_texts)
    for key, expected in EXPECTED_IDENTIFIERS.items():
        markdown_exact = expected in normalize_text(markdown_text)
        docx_exact = expected in normalize_text(docx_text)
        pypdf_exact = expected in normalize_text(pdf_text)
        plumber_exact = expected in normalize_text("\n\f\n".join(plumber_texts)) if plumber_texts else False
        markdown_canonical = canonical_identifier_text(expected) in canonical_identifier_text(markdown_text)
        docx_canonical = canonical_identifier_text(expected) in canonical_identifier_text(docx_text)
        pypdf_canonical = canonical_identifier_text(expected) in canonical_identifier_text(pdf_text)
        plumber_canonical = canonical_identifier_text(expected) in canonical_identifier_text("\n\f\n".join(plumber_texts)) if plumber_texts else False
        identifier_matrix[key] = {
            "expected": expected,
            "exact": {
                "markdown": markdown_exact,
                "docx": docx_exact,
                "pdf_pypdf": pypdf_exact,
                "pdf_pdfplumber": plumber_exact,
                "all_four": all((markdown_exact, docx_exact, pypdf_exact, plumber_exact)),
            },
            "canonical_punctuation_insensitive": {
                "markdown": markdown_canonical,
                "docx": docx_canonical,
                "pdf_pypdf": pypdf_canonical,
                "pdf_pdfplumber": plumber_canonical,
                "all_four": all((markdown_canonical, docx_canonical, pypdf_canonical, plumber_canonical)),
            },
        }

    facts = {
        "schema": "independent-final-pdf-mechanical-audit-v1",
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "scope": "Read-only audit of the exact final PDF, its exact rendered-page directory, and mechanically comparable root PAPER.docx/PAPER.md identifiers.",
        "pdf": pdf,
        "external_pdf_tools": external_tools,
        "rendered_pages": rendered_pages,
        "source_docx": docx,
        "source_markdown": markdown,
        "identifier_matrix": identifier_matrix,
    }
    FACTS_PATH.write_text(json.dumps(facts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "facts_path": rel(FACTS_PATH),
        "facts_bytes": FACTS_PATH.stat().st_size,
        "facts_sha256": sha256(FACTS_PATH),
        "pdf_pages": pdf["page_count"],
        "pdf_sha256": pdf["sha256"],
        "contact_sheet_count": len(rendered_pages["contact_sheets"]),
    }, indent=2))


if __name__ == "__main__":
    main()
