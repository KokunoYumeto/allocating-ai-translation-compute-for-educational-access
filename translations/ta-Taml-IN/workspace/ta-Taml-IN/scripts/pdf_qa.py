"""Inspect exported PDF text/tagging/geometry and build raster contact sheets."""
import hashlib
import json
import argparse
import subprocess
import unicodedata
import shutil
import re
from collections import Counter
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image, ImageDraw
from pypdf import PdfReader
import pdfplumber

ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT / "ta-Taml-IN"

def visible_print_text(html_path, extra_hidden_classes=()):
    """Return print-intended text, without confusing SVG alternatives with ink."""
    doc = ET.parse(html_path).getroot()
    body = doc.find("{http://www.w3.org/1999/xhtml}body")
    assert body is not None
    hidden_classes = {"skip", "diagram-hint", "table-hint", *extra_hidden_classes}
    blocks = {"body", "header", "nav", "main", "section", "aside", "div", "p", "h1", "h2", "h3", "h4", "ul", "ol", "li", "dl", "dt", "dd", "figure", "figcaption", "table", "caption", "thead", "tbody", "tr", "td", "th", "text"}
    def visible(node):
        if hidden_classes.intersection(node.get("class", "").split()):
            return ""
        if node.tag in ("{http://www.w3.org/2000/svg}title", "{http://www.w3.org/2000/svg}desc"):
            return ""
        content = (node.text or "") + "".join(visible(child) + (child.tail or "") for child in node)
        return "\n" + content + "\n" if node.tag.rsplit("}", 1)[-1] in blocks else content
    return visible(body)


def tamil_token_check(html_path, extracted, extra_hidden_classes=()):
    """Compare visible print-intended Tamil, without confusing SVG alternatives with ink."""
    body = ET.parse(html_path).getroot().find("{http://www.w3.org/1999/xhtml}body")
    tokens = lambda s: re.findall(r"[\u0b80-\u0bff]+", unicodedata.normalize("NFC", s))
    authored = Counter(tokens(visible_print_text(html_path, extra_hidden_classes)))
    found = Counter(tokens(extracted))
    missing, extra = authored - found, found - authored
    assert not missing, f"Missing authored Tamil tokens: {dict(missing)}"
    headers = Counter(tokens(" ".join(" ".join(n.itertext()) for n in body.findall(".//{http://www.w3.org/1999/xhtml}thead"))))
    assert all(t in headers for t in extra), f"Unexplained extra PDF Tamil tokens: {dict(extra)}"
    dependent = set(chr(n) for n in range(0x0bbe, 0x0bce))
    assert not any(t[0] in dependent for t in found), "Tamil token begins with a dependent vowel sign"
    return {"authored_tokens": sum(authored.values()), "extracted_tokens": sum(found.values()), "missing": dict(missing), "extra_repeated_header_tokens": dict(extra)}

def main():
    if not __debug__:
        raise SystemExit("Do not run PDF QA with Python -O; assertions must remain active")
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdftoppm", required=True, help="Poppler pdftoppm executable")
    parser.add_argument("--profiles", nargs="+", choices=["print", "screen"], default=["print", "screen"])
    parser.add_argument("--unit", choices=["U001", "U002"], default="U001")
    parser.add_argument("--pdftotext", help="Poppler text extractor; defaults beside pdftoppm")
    parser.add_argument("--reuse-rasters", action="store_true", help="Reuse existing rasters only for a PDF with an identical prior receipt hash")
    args = parser.parse_args()
    sibling = Path(args.pdftoppm).with_name("pdftotext.exe" if args.pdftoppm.lower().endswith(".exe") else "pdftotext")
    pdftotext = args.pdftotext or (str(sibling) if sibling.is_file() else shutil.which("pdftotext"))
    if not pdftotext:
        parser.error("Poppler pdftotext was not found; pass --pdftotext explicitly")
    receipt = {"status":"automated-pass-visual-review-separate", "profiles":{}}
    prior = LANG / ("qa/pdf-receipt.json" if args.unit == "U001" else "qa/U002-pdf-receipt.json")
    unit_prefix = "" if args.unit == "U001" else "U002-"
    previous_profiles = {}
    if prior.is_file():
        previous_profiles = json.loads(prior.read_text(encoding="utf-8")).get("profiles", {})
        for key, record in previous_profiles.items():
            path = ROOT / record["path"]
            if key not in args.profiles and path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]:
                receipt["profiles"][key] = record
    for profile in args.profiles:
        path = LANG / f"output/pdf/ta-Taml-IN-A00-{args.unit}-{profile}.pdf"
        pdf = PdfReader(path)
        root = pdf.trailer["/Root"]
        assert root.get("/StructTreeRoot")
        assert root.get("/MarkInfo").get("/Marked")
        assert root.get("/Lang", "").startswith("ta")
        # pypdf 6.14.2 ignores ActualText during extraction here, reporting NULs
        # for contextual Tamil glyphs. Poppler honors the logical replacement
        # text. Keep that cross-engine limitation visible instead of stripping
        # corrupt characters or falsely declaring the PDFs' text corrupt.
        pypdf_text = "\n".join(p.extract_text() or "" for p in pdf.pages)
        extraction = subprocess.run([pdftotext, "-enc", "UTF-8", str(path), "-"],
                                    check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    timeout=60, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        extracted = unicodedata.normalize("NFC", extraction.stdout.decode("utf-8"))
        assert "\x00" not in extracted, "Logical PDF text contains NULs"
        actual_text_spans = 0
        marked_content_spans = 0
        for page in pdf.pages:
            stream = page.get_contents()
            # ContentStream may be falsy as a dictionary despite having data.
            data = stream.get_data() if stream is not None else b""
            actual_text_spans += data.count(b"/ActualText")
            marked_content_spans += data.count(b"BDC")
        assert actual_text_spans > 0 and marked_content_spans > 0
        expected = ("இயல்", "முழு", "376") if args.unit == "U001" else ("இடமதிப்பு", "முழு", "176", "237", "$374")
        assert all(word in extracted for word in expected)
        assert "\ufffd" not in extracted
        assert "Lynn Marecek" in extracted and "Becky Wheelock" in extracted
        reader = LANG / ("reader" if args.unit == "U001" else "reader-u002")
        token_check = tamil_token_check(reader / ("index.html" if profile == "print" else "screen.html"), extracted)
        with pdfplumber.open(path) as pp:
            overflow = [(i+1, ch.get("text"), ch["x0"], ch["x1"], ch["top"], ch["bottom"]) for i,p in enumerate(pp.pages) for ch in p.chars if ch["x0"] < -1 or ch["x1"] > p.width+1 or ch["top"] < -1 or ch["bottom"] > p.height+1]
        assert not overflow, overflow[:10]
        folder = ROOT / f"tmp/pdfs/{unit_prefix}{profile}-pages"
        folder.mkdir(parents=True, exist_ok=True)
        # Overwrite our own QA rasters one page at a time; no duplicate corpus.
        # Ignore any old higher-numbered rasters after pagination becomes shorter.
        pages = []
        same_pdf = previous_profiles.get(profile, {}).get("sha256") == hashlib.sha256(path.read_bytes()).hexdigest()
        for number in range(1, len(pdf.pages) + 1):
            page_prefix = folder / f"page-{number:02}"
            page = page_prefix.with_suffix(".png")
            if not (args.reuse_rasters and same_pdf and page.is_file() and page.stat().st_mtime >= path.stat().st_mtime):
                subprocess.run([args.pdftoppm, "-f", str(number), "-l", str(number),
                                "-singlefile", "-scale-to", "1200", "-png",
                                str(path), str(page_prefix)], check=True, timeout=60,
                               creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            assert page.is_file() and page.stat().st_mtime >= path.stat().st_mtime
            pages.append(page)
        contact_paths = []
        for group in range(0, len(pages), 4):
            canvas = Image.new("RGB", (1000, 1470), "#d8e0e3")
            draw = ImageDraw.Draw(canvas)
            for j,p in enumerate(pages[group:group+4]):
                im = Image.open(p).convert("RGB")
                im.thumbnail((480,700))
                x = (j%2)*500+10
                y = (j//2)*735+25
                canvas.paste(im,(x,y))
                draw.text((x,y-18),f"{profile} / {p.stem}",fill="black")
            dest = ROOT / f"tmp/pdfs/{unit_prefix}{profile}-contact-{group//4+1}.png"
            canvas.save(dest)
            contact_paths.append(dest.relative_to(ROOT).as_posix())
        receipt["profiles"][profile] = {"path":path.relative_to(ROOT).as_posix(), "pages":len(pdf.pages), "bytes":path.stat().st_size, "sha256":hashlib.sha256(path.read_bytes()).hexdigest(), "tagged":True,"language":root.get("/Lang"),"unicode_text_check":"pass-Poppler-ActualText-aware", "tamil_token_check": token_check, "actual_text_spans":actual_text_spans, "marked_content_spans":marked_content_spans, "pypdf_extraction_nuls":pypdf_text.count("\x00"), "extraction_limit":"pypdf extract_text does not recover contextual Tamil glyphs here; use an ActualText-aware extractor. This is not PDF/UA certification.", "out_of_page_glyph_boxes":len(overflow),"contact_sheets":contact_paths}
    prior.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False,indent=2))

if __name__ == "__main__":
    main()
