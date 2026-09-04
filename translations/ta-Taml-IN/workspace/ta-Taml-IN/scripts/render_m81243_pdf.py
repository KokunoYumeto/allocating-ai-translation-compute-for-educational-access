"""Print isolated full-module PDF variants without changing HTML/EPUB or old PDFs."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pypdf import PdfReader

sys.dont_write_bytecode = True
import build_m81243_learning as learning
from build import xhtml
from build_u002 import require

LANG, ROOT = learning.LANG, learning.LANG.parent
H, S = learning.H, learning.S
STYLE = LANG / "assets/m81243-pdf.css"

LAYOUT_RULES = (
    ".answer > .source-reference { break-inside: avoid; break-after: avoid; }",
    ".answer > .source-reference + * { break-before: avoid; }",
    "#fs-id1684233 { break-inside: avoid; }",
    "#ta-m1-reason-15 > .feedback { break-inside: avoid; }",
)
LAYOUT_TARGETS = {
    "fs-id1684233", "ta-m1-missing-02", "ta-m1-missing-04", "ta-m1-missing-29",
    "ta-m1-reason-06", "ta-m1-reason-08", "ta-m1-reason-14", "ta-m1-reason-15",
}


def layout_contract(baseline, css):
    doc = ET.fromstring(baseline)
    ids = {node.get("id") for node in doc.iter() if node.get("id")}
    require(LAYOUT_TARGETS.issubset(ids), "PDF pagination target is absent from the learning reader")
    normalized = " ".join(css.split())
    require(all(rule in normalized for rule in LAYOUT_RULES), "Required PDF pagination rule is absent")
    return {"targets": sorted(LAYOUT_TARGETS), "rules": list(LAYOUT_RULES)}


def layout_negative_tests(baseline, css):
    rejected = []
    for rule in LAYOUT_RULES:
        require(rule in css, "Pagination rule formatting no longer matches its regression fixture")
        changed = css.replace(rule, rule.replace("avoid", "auto", 1), 1)
        try:
            layout_contract(baseline, changed)
        except ValueError as exc:
            require(str(exc) == "Required PDF pagination rule is absent", "Pagination fixture failed for an unrelated reason")
            rejected.append(rule.split(" {", 1)[0])
        else:
            raise ValueError("Broken PDF pagination rule accepted")
    return rejected


def prepare(profile, baseline, destinations=None):
    source = ET.fromstring(baseline)
    doc = copy.deepcopy(source)
    parents = {c: p for p in doc.iter() for c in p}
    wide, original_classes = [], {}
    for svg in doc.iter(f"{{{S}}}svg"):
        width = float(svg.get("viewBox").split()[2])
        if width < 960:
            continue
        path, ancestor = [], parents.get(svg)
        while ancestor is not None and ancestor.tag != f"{{{H}}}section":
            path.append(ancestor)
            ancestor = parents.get(ancestor)
        group = next((n for n in path if n.tag == f"{{{H}}}figure"), None)
        if group is None:
            group = next((n for n in path if "source-table-group" in n.get("class", "").split()), None)
        if group is None:
            group = next((n for n in path if "source-media" in n.get("class", "").split()), None)
        require(group is not None, "Wide source graphic has no identified containing block")
        if "pdf-wide" not in group.get("class", "").split():
            wide.append(group.get("id") or next((n.get("id") for n in group.iter() if n.get("id")), None))
            original_classes[id(group)] = group.get("class")
            group.set("class", group.get("class", "") + " pdf-wide")
    # Reverse the sole content-tree adaptation before changing head/body profile.
    restored = copy.deepcopy(doc)
    for original, n in zip(doc.iter(), restored.iter()):
        if id(original) in original_classes:
            old = original_classes[id(original)]
            if old is None:
                del n.attrib["class"]
            else:
                n.set("class", old)
    require(learning.signature(restored) == learning.signature(source), "PDF layout adaptation changed reading content")
    head = doc.find(f"{{{H}}}head")
    for link in head.findall(f"{{{H}}}link"):
        asset = (learning.OUTPUT / link.get("href")).resolve()
        require(asset.is_relative_to(learning.OUTPUT.resolve()) and asset.is_file(), "Missing/out-of-reader stylesheet")
        link.set("href", asset.as_uri())
    ET.SubElement(head, f"{{{H}}}link", {"rel": "stylesheet", "href": STYLE.as_uri()})
    # Temporary print adaptation: visible page references, never source edits.
    for link in doc.iter(f"{{{H}}}a"):
        href = link.get("href", "")
        if href.startswith("#") and "skip" not in link.get("class", "").split():
            target = href[1:]
            require(destinations is None or target in destinations, f"Missing PDF destination: {target}")
            reference = ET.SubElement(link, f"{{{H}}}span", {"class": "pdf-page-reference"})
            reference.text = " (ப. "
            number = ET.SubElement(reference, f"{{{H}}}bdi", {"class": "pdf-page-number", "data-pdf-target": target})
            number.text = "000" if destinations is None else str(destinations[target])
            number.tail = ")"
        if href and not href.startswith(("#", "http:", "https:")):
            asset = (learning.OUTPUT / href).resolve()
            require(asset.is_relative_to(learning.OUTPUT.resolve()) and asset.is_file(), "Unpackaged print link")
            link.set("href", asset.as_uri())
    body = doc.find(f"{{{H}}}body")
    body.set("class", profile + "-profile")
    cover = body.find(f"{{{H}}}header")
    note = ET.Element(f"{{{H}}}p", {"class": "editorial-note", "id": "pdf-paper-note"})
    note.text = "அச்சுப் பதிப்புக் குறிப்பு: அகலமான படங்களும் அவற்றுடன் இணைந்த அட்டவணைகளும் A3 கிடைமட்டத் தாள்களில் உள்ளன. மற்ற பக்கங்கள் A4 அளவில் உள்ளன. படங்களின் எண்களும் சொற்களும் மாற்றப்படவில்லை. இணைப்புகளின் அருகிலுள்ள ‘ப.’ குறிப்பு, இந்தப் பதிப்பில் செல்ல வேண்டிய பக்க எண்ணைக் காட்டுகிறது."
    cover.insert(2, note)
    return ("<!DOCTYPE html>" + xhtml(doc, parent_namespace="")).encode("utf-8"), wide


def page_destinations(path):
    pdf = PdfReader(path)
    mapping = {key.removeprefix("/"): pdf.get_destination_page_number(value) + 1 for key, value in pdf.named_destinations.items()}
    require(mapping and all(0 < n <= len(pdf.pages) < 1000 for n in mapping.values()), "Invalid PDF destination pages")
    return mapping


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chromium", default="C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")
    parser.add_argument("--profiles", nargs="+", choices=["print", "screen"], default=["print", "screen"])
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    payload, manifest = learning.build_payload()
    require(all((learning.OUTPUT / name).read_bytes() == data for name, data in payload.items()), "Learning reader bytes are stale")
    style_text = STYLE.read_text(encoding="utf-8")
    layout = layout_contract(payload["index.html"], style_text)
    layout["negative_fixtures_rejected"] = layout_negative_tests(payload["index.html"], style_text)
    snapshot = {**manifest["inputs"], "assets/m81243-pdf.css": learning.review.sha(STYLE),
                "scripts/render_m81243_pdf.py": learning.review.sha(Path(__file__))}
    tmp = ROOT / "tmp/pdfs/ta-m81243"
    out = LANG / "output/pdf"
    require(shutil.disk_usage(ROOT).free > 512 * 1024 * 1024, "Insufficient space for full-module export")
    tmp.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    receipt_path = LANG / "qa/M81243-pdf-export.json"
    old = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.is_file() else {}
    records = {}
    if not args.prepare_only and old.get("inputs") == snapshot:
        for profile, record in old.get("profiles", {}).items():
            pdf, html = ROOT / record["pdf"], ROOT / record["html"]
            if profile not in args.profiles and pdf.is_file() and html.is_file() and learning.review.sha(pdf) == record["pdf_sha256"] and learning.review.sha(html) == record["html_sha256"]:
                records[profile] = record
    for profile in args.profiles:
        raw, wide = prepare(profile, payload["index.html"])
        html = tmp / f"m81243-{profile}.html"
        html.write_bytes(raw)
        target = out / f"ta-Taml-IN-A00-m81243-{profile}.pdf"
        if not args.prepare_only:
            require(shutil.disk_usage(ROOT).free > 512 * 1024 * 1024, "Insufficient free space; no export attempted")
            cache = tmp / f"document-print-{profile}"
            cache.mkdir(exist_ok=True)
            destinations, stable = None, False
            for pass_number in range(1, 5):
                raw, wide = prepare(profile, payload["index.html"], destinations)
                html.write_bytes(raw)
                candidate = tmp / f"m81243-{profile}-pass-{pass_number}.pdf"
                command = [args.chromium, "--headless", "--disable-gpu", "--disable-background-networking", "--disable-sync", "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--no-pdf-header-footer", "--export-tagged-pdf", "--virtual-time-budget=3000", f"--user-data-dir={cache}", f"--print-to-pdf={candidate}", html.as_uri()]
                subprocess.run(command, check=True, timeout=180, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                require(candidate.is_file() and candidate.stat().st_size > 10000, "PDF not produced")
                actual = page_destinations(candidate)
                print(f"{profile}: export pass {pass_number}; {len(actual)} named destinations", flush=True)
                if actual == destinations:
                    shutil.copyfile(candidate, target)
                    stable = True
                    break
                destinations = actual
            require(stable, "Printed page references did not reach stable pagination")
        records[profile] = {"html": html.relative_to(ROOT).as_posix(), "html_sha256": hashlib.sha256(raw).hexdigest(),
                            "wide_blocks": wide, "pdf": target.relative_to(ROOT).as_posix(),
                            "pdf_sha256": None if args.prepare_only else learning.review.sha(target),
                            "stable_page_reference_pass": None if args.prepare_only else pass_number,
                            "page_destinations": {} if args.prepare_only else destinations}
        print(json.dumps({"profile": profile, **records[profile]}, ensure_ascii=False), flush=True)
    require(all(learning.review.sha(LANG / path) == digest for path, digest in snapshot.items()), "Input changed during PDF export")
    receipt = {"status": "prepared-only" if args.prepare_only else "exported-unverified-PDF", "source_html_sha256": learning.review.digest(payload["index.html"]), "inputs": snapshot, "layout_contract": layout, "profiles": records,
               "limits": ["Text extraction, page geometry and full raster review are required before delivery.", "PDFs have mixed A4 and A3-landscape pages; native/AT/PDFUA review remains separate."]}
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
