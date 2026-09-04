"""Check exact full-module exports and optionally rasterize every page for review."""
import argparse
from collections import Counter
import hashlib
import json
import logging
import re
from pathlib import Path
import shutil
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
from PIL import Image, ImageDraw
import pdfplumber
from pypdf import PdfReader
from pypdf.generic import DictionaryObject, NameObject
from pdf_qa import tamil_token_check, visible_print_text
from build_u002 import require

ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT / "ta-Taml-IN"
H = "{http://www.w3.org/1999/xhtml}"
S = "{http://www.w3.org/2000/svg}"


class GeometryWarnings(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING)
        self.counts = Counter()

    def emit(self, record):
        self.counts[record.getMessage()] += 1


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rotation_aware_text(doc, extracted, raw_text):
    """Validate, then undo Poppler's geometric reversal of 45 vertical labels.

    This never changes PDF bytes. Raw content order must independently contain
    each complete 15-label sequence. Only declared -90-degree SVG labels qualify;
    no missing label, arbitrary reversal or whole-document whitespace repair is
    allowed. Their horizontal semantic alternatives remain searchable unchanged.
    """
    expected = Counter()
    sequences = Counter()
    for svg in doc.iter(S + "svg"):
        labels = [unicodedata.normalize("NFC", "".join(n.itertext())) for n in svg.iter(S + "text") if "rotate(-90)" in n.get("transform", "")]
        if labels:
            require(len(labels) == 15, "Unexpected rotated chart label structure")
            expected.update(labels)
            sequences[re.sub(r"\s+", "", "".join(labels))] += 1
    require(sum(expected.values()) == 45, "Expected three original 15-place charts")
    compact_raw = re.sub(r"\s+", "", unicodedata.normalize("NFC", raw_text))
    for sequence, count in sequences.items():
        require(compact_raw.count(sequence) == count, "Raw PDF order does not preserve complete rotated chart labels")
    changes = []
    for label, count in sorted(expected.items(), key=lambda pair: -len(pair[0])):
        clusters = []
        for char in label:
            if unicodedata.category(char).startswith("M"):
                require(clusters, "Invalid leading combining mark")
                clusters[-1] += char
            else:
                clusters.append(char)
        reversed_label = "".join(reversed(clusters))
        pattern = r"(?<![\u0b80-\u0bff])" + re.escape(reversed_label).replace(r"\ ", r"\s+") + r"(?![\u0b80-\u0bff])"
        fixed, observed = re.subn(pattern, label, extracted)
        require(observed == count, f"Unexpected rotated-label extraction count for {label}: {observed} != {count}")
        extracted = fixed
        changes.append({"authored_label": label, "geometric_extraction": reversed_label, "occurrences": observed})
    return extracted, changes


def page_reference_check(doc, pdf, expected):
    actual = {key.removeprefix("/"): pdf.get_destination_page_number(value) + 1 for key, value in pdf.named_destinations.items()}
    require(actual == expected, "PDF destination map differs from export")
    refs = 0
    for link in doc.iter(H + "a"):
        href = link.get("href", "")
        if href.startswith("#") and "skip" not in link.get("class", "").split():
            fields = list(link.iter(H + "bdi"))
            require(len(fields) == 1 and fields[0].get("data-pdf-target") == href[1:], "Missing/mismatched print page field")
            require(fields[0].text == str(actual[href[1:]]), "Printed page reference is stale")
            refs += 1
    require(refs > 92, "Too few paper navigation references")
    page_objects = {(page.indirect_reference.idnum, page.indirect_reference.generation) for page in pdf.pages}
    def destination(value):
        if isinstance(value, str):
            require(value.removeprefix("/") in actual, "PDF link destination does not resolve")
        else:
            require(isinstance(value, list) and value, "Unsupported internal PDF destination")
            ref = value[0]
            require((getattr(ref, "idnum", None), getattr(ref, "generation", None)) in page_objects, "PDF page-array destination does not resolve")
    for page in pdf.pages:
        for annotation in page.get("/Annots", []):
            annotation = annotation.get_object()
            dest = annotation.get("/Dest")
            if dest is not None:
                destination(dest)
            action = annotation.get("/A")
            if action is not None:
                action = action.get_object()
                require(action.get("/S") in {"/URI", "/GoTo"}, "Unexpected PDF action")
                if action.get("/S") == "/GoTo":
                    destination(action.get("/D"))
    return {"named_destinations": len(actual), "printed_internal_link_references": refs, "stable_map": True}


def numeric_ink_check(html, extracted, page_count, raw_text):
    authored = visible_print_text(html, extra_hidden_classes={"sr-only"})
    chars = set("0123456789+=≈×÷−<>≤≥$€₹%,.")
    expected = Counter(c for c in authored if c in chars)
    doc = ET.parse(html).getroot()
    list_markers = []
    for ordered in doc.iter(H + "ol"):
        if "source-circled" in ordered.get("class", "").split():
            continue  # stylesheet suppresses these markers; circled text is ink
        require(ordered.get("type", "1") == "1" and not {"start", "reversed"}.intersection(ordered.attrib), "Unreviewed ordered-list numbering")
        items = ordered.findall(H + "li")
        require(all("value" not in n.attrib for n in items), "Unreviewed list value override")
        list_markers.extend(str(n) for n in range(1, len(items) + 1))
    expected.update("".join(n + "." for n in list_markers))
    repeated_headers = []
    normalize = lambda text: " ".join(unicodedata.normalize("NFC", text).split())
    normalized_authored, normalized_extracted = normalize(authored), normalize(extracted)
    for header in doc.iter(H + "thead"):
        phrase = normalize(" ".join(header.itertext()))
        if not any(c.isascii() and c.isdigit() for c in phrase):
            continue
        baseline_count = normalized_authored.count(phrase)
        observed_count = normalized_extracted.count(phrase)
        require(baseline_count == 1, "Repeated numeric header needs an unambiguous source identity")
        repeats = max(0, observed_count - baseline_count)
        expected.update({c: count * repeats for c, count in Counter(c for c in phrase if c in chars).items()})
        repeated_headers.append({"header_text": phrase, "authored_occurrences": baseline_count, "extracted_occurrences": observed_count, "additional_full_header_repeats": repeats})
    # Each physical page has exactly one generated numeric footer.
    expected.update("".join(str(n) for n in range(1, page_count + 1)))
    found = Counter(c for c in extracted if c in chars)
    require(expected == found, f"Visible numeric/operator inventory differs: missing {dict(expected-found)}, extra {dict(found-expected)}")
    page_fields = Counter(n.text for n in doc.iter(H + "bdi") if n.get("data-pdf-target"))
    # Raw content order keeps right-aligned page fields with their own link;
    # default geometric extraction sometimes collects their numbers as a column.
    ink_fields = Counter(re.findall(r"\(ப\.\s*([0-9]{1,3})\s*\)", raw_text))
    require(page_fields == ink_fields, "Printed PDF page-reference ink differs from authored labels")
    return {"characters": dict(sorted(expected.items())), "printed_page_reference_fields": sum(ink_fields.values()), "page_number_footers": page_count, "generated_ordered_list_markers": len(list_markers), "numeric_header_repeats": repeated_headers,
            "limit": "Inventory proves character counts, not numeral/operator placement or mathematical reading order; full visual review remains required."}


def negative_tests(doc, pdf, expected, html, logical, raw_text):
    checked = []
    for changed, label in [(re.sub(r"[0-9]", "", logical), "all ASCII digits removed"),
                           (logical.replace("23,658", "23,659", 1), "one rounding digit changed"),
                           (logical.replace("23,658", "23.658", 1), "grouping comma changed to decimal point")]:
        require(changed != logical, "Numeric fixture did not modify text")
        try:
            numeric_ink_check(html, changed, len(pdf.pages), raw_text)
        except ValueError as exc:
            require(str(exc).startswith("Visible numeric/operator inventory differs:"), "Numeric fixture failed for an unrelated reason")
            checked.append(label)
        else:
            raise ValueError("Numeric ink fault accepted")
    annotation = next(a.get_object() for page in pdf.pages for a in page.get("/Annots", []) if a.get_object().get("/Dest") is not None)
    dest, action = annotation.pop("/Dest"), annotation.get("/A")
    annotation[NameObject("/A")] = DictionaryObject({NameObject("/S"): NameObject("/GoTo"), NameObject("/D"): NameObject("/qa-nonexistent-destination")})
    try:
        try:
            page_reference_check(doc, pdf, expected)
        except ValueError as exc:
            require(str(exc) == "PDF link destination does not resolve", "GoTo fixture failed for an unrelated reason")
            checked.append("broken GoTo action destination")
        else:
            raise ValueError("Broken GoTo action accepted")
    finally:
        annotation[NameObject("/Dest")] = dest
        if action is None:
            del annotation["/A"]
        else:
            annotation[NameObject("/A")] = action
    return checked


def main():
    require(__debug__, "Do not disable assertions for PDF QA")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profiles", nargs="+", choices=["print", "screen"], default=["print", "screen"])
    parser.add_argument("--pdftotext", default=shutil.which("pdftotext"))
    parser.add_argument("--pdftoppm")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--reuse-rasters", action="store_true")
    parser.add_argument("--raster-run", default="", help="Optional safe suffix retaining a prior candidate's raster evidence")
    args = parser.parse_args()
    require(not args.raster_run or re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.raster_run), "Unsafe raster-run label")
    require(args.pdftotext, "An ActualText-aware Poppler extractor is required")
    require(not args.render or args.pdftoppm, "Raster creation needs --pdftoppm")
    export_path = LANG / "qa/M81243-pdf-export.json"
    export_hash = sha(export_path)
    export = json.loads(export_path.read_text(encoding="utf-8"))
    require(export["status"] == "exported-unverified-PDF", "PDF export receipt is not ready")
    require(all(sha(LANG / name) == digest for name, digest in export["inputs"].items()), "PDF export inputs are stale")
    require(sha(LANG / "reader-m81243-learning/index.html") == export["source_html_sha256"], "Source reader changed")
    qa_inputs = {p.relative_to(LANG).as_posix(): sha(p) for p in [Path(__file__), LANG / "scripts/pdf_qa.py", LANG / "scripts/build_u002.py"]}
    receipt_path = LANG / "qa/M81243-pdf-receipt.json"
    prior = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.is_file() else {}
    records = {}
    for profile in args.profiles:
        expected = export["profiles"][profile]
        path, html = ROOT / expected["pdf"], ROOT / expected["html"]
        identity = sha(path)
        require(identity == expected["pdf_sha256"] and sha(html) == expected["html_sha256"], "PDF/input HTML differs from export receipt")
        print(f"{profile}: checking logical Tamil in {path.name}", flush=True)
        extraction = subprocess.run([args.pdftotext, "-enc", "UTF-8", str(path), "-"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        extracted = unicodedata.normalize("NFC", extraction.stdout.decode("utf-8"))
        require("\x00" not in extracted and "\ufffd" not in extracted, "Logical PDF text contains corrupt characters")
        require(all(t in extracted for t in ["இடமதிப்பு", "முழு", "Lynn Marecek", "Becky Wheelock"]), "Missing expected source content or attribution")
        raw_extraction = subprocess.run([args.pdftotext, "-raw", "-enc", "UTF-8", str(path), "-"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        doc = ET.parse(html).getroot()
        raw_text = raw_extraction.stdout.decode("utf-8")
        logical, rotations = rotation_aware_text(doc, extracted, raw_text)
        token_check = tamil_token_check(html, logical, extra_hidden_classes={"sr-only"})
        pdf = PdfReader(path)
        page_references = page_reference_check(doc, pdf, expected["page_destinations"])
        numeric_ink = numeric_ink_check(html, logical, len(pdf.pages), raw_text)
        faults = negative_tests(doc, pdf, expected["page_destinations"], html, logical, raw_text)
        catalog = pdf.trailer["/Root"]
        require(catalog.get("/StructTreeRoot") and catalog.get("/MarkInfo").get("/Marked"), "Missing PDF tags")
        require(catalog.get("/Lang") == "ta-Taml-IN", "Wrong PDF language")
        sizes = Counter(tuple(round(float(n)) for n in (p.mediabox.width, p.mediabox.height)) for p in pdf.pages)
        require(set(sizes).issubset({(595, 842), (1191, 842)}) and len(sizes) == 2, "Unexpected paper dimensions")
        actual_text, marked, nuls = 0, 0, 0
        for i, page in enumerate(pdf.pages, 1):
            stream = page.get_contents()
            data = stream.get_data() if stream is not None else b""
            actual_text += data.count(b"/ActualText")
            marked += data.count(b"BDC")
            nuls += (page.extract_text() or "").count("\x00")
            if i % 20 == 0:
                print(f"{profile}: tag/text diagnostic {i}/{len(pdf.pages)}", flush=True)
        require(actual_text > 0 and marked > 0, "Missing expected contextual text replacements")
        overflow = []
        warnings = GeometryWarnings()
        font_logger = logging.getLogger("pdfminer.pdffont")
        old_propagate = font_logger.propagate
        font_logger.addHandler(warnings)
        font_logger.propagate = False
        with pdfplumber.open(path) as pp:
            for i, page in enumerate(pp.pages, 1):
                overflow.extend((i, c.get("text"), c["x0"], c["x1"], c["top"], c["bottom"]) for c in page.chars if c["x0"] < -1 or c["x1"] > page.width + 1 or c["top"] < -1 or c["bottom"] > page.height + 1)
                page.close()
                if i % 20 == 0:
                    print(f"{profile}: glyph geometry {i}/{len(pp.pages)}", flush=True)
        font_logger.removeHandler(warnings)
        font_logger.propagate = old_propagate
        require(not overflow, f"Out-of-page glyphs: {overflow[:10]}")
        record = {"path": expected["pdf"], "sha256": identity, "bytes": path.stat().st_size, "html_sha256": expected["html_sha256"], "pages": len(pdf.pages), "paper_sizes_points": {f"{w}x{h}": count for (w, h), count in sizes.items()}, "tagged": True, "language": catalog.get("/Lang"), "unicode_text_check": "pass-Poppler-ActualText-aware-with-declared-rotation-normalization", "tamil_token_check": token_check, "rotated_label_extraction_checks": rotations, "paper_navigation": page_references, "actual_text_spans": actual_text, "marked_content_spans": marked, "pypdf_extraction_nuls": nuls, "out_of_page_glyph_boxes": len(overflow), "rasters": {}, "contact_sheets": {}}
        records[profile] = record
        record["numeric_and_operator_ink_check"] = numeric_ink
        record["negative_tests"] = faults
        record["geometry_parser_warnings"] = dict(warnings.counts)
        if warnings.counts:
            print(f"{profile}: geometry parser warnings recorded: {dict(warnings.counts)}", flush=True)
        if args.render:
            suffix = "-" + args.raster_run if args.raster_run else ""
            folder = ROOT / f"tmp/pdfs/ta-m81243/{profile}-pages{suffix}"
            folder.mkdir(parents=True, exist_ok=True)
            old = prior.get("profiles", {}).get(profile, {})
            pages = []
            for number in range(1, len(pdf.pages) + 1):
                require(shutil.disk_usage(ROOT).free > 512 * 1024 * 1024, "Insufficient space for raster review")
                prefix = folder / f"page-{number:03}"
                page = prefix.with_suffix(".png")
                rel = page.relative_to(ROOT).as_posix()
                reusable = args.reuse_rasters and old.get("sha256") == identity and page.is_file() and old.get("rasters", {}).get(rel) == sha(page)
                if not reusable:
                    subprocess.run([args.pdftoppm, "-f", str(number), "-l", str(number), "-singlefile", "-scale-to", "1200", "-png", str(path), str(prefix)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                require(page.is_file(), "Raster missing")
                record["rasters"][rel] = sha(page)
                pages.append(page)
                if number % 10 == 0:
                    print(f"{profile}: raster {number}/{len(pdf.pages)}", flush=True)
            for group in range(0, len(pages), 4):
                canvas = Image.new("RGB", (1000, 1470), "#d8e0e3")
                draw = ImageDraw.Draw(canvas)
                for j, page in enumerate(pages[group:group+4]):
                    with Image.open(page) as im:
                        im = im.convert("RGB")
                        im.thumbnail((480, 700))
                        x, y = (j % 2) * 500 + 10, (j // 2) * 735 + 25
                        canvas.paste(im, (x, y))
                        draw.text((x, y - 18), f"{profile} / {page.stem}", fill="black")
                contact = folder / f"contact-{group//4+1:02}.png"
                canvas.save(contact)
                record["contact_sheets"][contact.relative_to(ROOT).as_posix()] = sha(contact)
        require(sha(path) == identity and sha(html) == expected["html_sha256"], "PDF/HTML changed during QA")
        print(f"{profile}: automated checks passed; visual review remains separate", flush=True)
    require(sha(export_path) == export_hash and all(sha(LANG / name) == digest for name, digest in export["inputs"].items()), "Export inputs changed during QA")
    require(all(sha(LANG / name) == digest for name, digest in qa_inputs.items()), "QA script changed during execution")
    # Carry forward another profile only when this exact export and QA inputs match.
    if prior.get("export_receipt_sha256") == export_hash and prior.get("qa_inputs") == qa_inputs:
        for profile, record in prior.get("profiles", {}).items():
            if profile not in records and sha(ROOT / record["path"]) == record["sha256"]:
                records[profile] = record
    receipt = {"status": "automated-pass-visual-review-separate", "export_receipt_sha256": export_hash, "qa_inputs": qa_inputs, "profiles": records, "limits": ["A raster is evidence to inspect, not an automatic visual approval.", "Per-glyph page bounds do not prove unclipped nested containers, reading order or usable links.", "pypdf contextual-Tamil NULs are an extractor limitation; logical text is checked with Poppler ActualText support.", "No PDF/UA, native-language, screen-reader or learning-efficacy certification."]}
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"receipt": receipt_path.relative_to(ROOT).as_posix(), "profiles": {p: {"pages": r["pages"], "sha256": r["sha256"]} for p, r in records.items()}}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
