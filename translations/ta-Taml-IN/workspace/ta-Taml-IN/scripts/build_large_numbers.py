"""Build the U003-U005 recovery-review HTML/EPUB without changing source preview.

This is a reviewed local learning segment, not a complete module or course.
All deterministic files are constructed and checked before any output write.
"""
import argparse
from collections import Counter
import io
import json
from pathlib import Path
import re
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile

sys.dont_write_bytecode = True
import assemble_m81243 as assembly
import build_large_number_review as review
from build import xhtml
from build_u002 import require

LANG = review.LANG
H, M, S = review.H, review.M, review.S
COMPANION = LANG / "translation/recovery-large-numbers.xhtml"
STYLE = LANG / "assets/large-number-recovery.css"
OUTPUT = LANG / "reader-large-recovery"
TITLE = "பெரிய முழு எண்கள்: இடமதிப்பும் எண்ணின் பெயரும்"
EPUB_NAME = "ta-Taml-IN-A00-U003-U005.epub"


def signature(node):
    return (node.tag, tuple(sorted(node.attrib.items())), node.text or "",
            tuple((signature(c), c.tail or "") for c in node))


def validate_companion(companion):
    require(companion.tag == f"{{{H}}}div", "Unexpected companion root")
    all_ids = review.ids(companion)
    require(len(all_ids) == len(set(all_ids)) == 80, "Companion ID inventory changed")
    require(all(i.startswith("ta-large-") for i in all_ids), "Unexpected companion ID prefix")
    require(len(companion) == 14 and all(c.tag == f"{{{H}}}section" for c in companion),
            "Expected fourteen companion sections")
    questions = [n for n in companion.iter() if n.get("data-kind")]
    require(Counter(n.get("data-kind") for n in questions) ==
            Counter(diagnostic=4, practice=4, mastery=4, retry=4), "Question coverage changed")
    answers = [n for n in companion.iter() if n.get("data-answer-for")]
    require(Counter(n.get("data-answer-for") for n in answers) ==
            Counter(n.get("id") for n in questions), "Missing/duplicate companion answer")
    for q in questions:
        require(not q.findall(".//*[@data-answer-for]"), "Answer mixed into a question")
    for answer in answers:
        refs = [a.get("href") for a in answer.iter(f"{{{H}}}a")]
        require("#" + answer.get("data-answer-for") in refs, "Answer lacks exact retry link")
        require(any(ref in {f"#ta-large-R{i}" for i in range(1, 5)} for ref in refs),
                "Answer lacks an executable remedy")
    return questions, answers


def validate(book, sources, payload, companion, rendered_sources):
    doc = review.validate_document(book, sources, payload)
    validate_companion(companion)
    for baseline in rendered_sources:
        rendered = doc.find(f'.//{{{H}}}section[@id="{baseline.get("id")}"]')
        require(rendered is not None and signature(rendered) == signature(baseline),
                "Source-preview content changed during integration")
    for section in companion:
        rendered = doc.find(f'.//{{{H}}}section[@id="{section.get("id")}"]')
        require(rendered is not None and signature(rendered) == signature(section),
                "Companion content changed in rendering")
    css = payload["assets/large-number-recovery.css"].decode("utf-8")
    require(not re.search(r"@import|url\s*\(|https?:", css, re.I), "Unexpected recovery CSS dependency")
    require(len(doc.findall(f".//{{{S}}}svg")) == 8, "Figure loss/duplication")
    require(len(doc.findall(f".//{{{M}}}math")) == 56, "MathML loss/duplication")
    require(len(doc.findall(f".//{{{H}}}table")) == 6, "Semantic table loss/duplication")
    return doc


def make_epub(book, navigation, payload):
    nav_items = "".join(f'<li><a href="book.xhtml#{review.ESC(i)}">{review.ESC(t)}</a></li>'
                        for i, t in navigation)
    nav = f'''<html xmlns="{H}" xmlns:epub="http://www.idpf.org/2007/ops" lang="ta-Taml-IN" xml:lang="ta-Taml-IN"><head><title>உள்ளடக்கம்</title></head><body><nav epub:type="toc" id="toc"><h1>உள்ளடக்கம்</h1><ol>{nav_items}</ol></nav></body></html>'''
    files = {"OEBPS/book.xhtml": book.encode("utf-8"), "OEBPS/nav.xhtml": nav.encode("utf-8")}
    media_types = {".css": "text/css", ".ttf": "font/ttf", ".txt": "text/plain", ".svg": "image/svg+xml"}
    items = ['<item id="book" href="book.xhtml" media-type="application/xhtml+xml" properties="mathml svg"/>',
             '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>']
    for index, (name, data) in enumerate(sorted(payload.items())):
        if name == "index.html":
            continue
        require(Path(name).suffix in media_types, f"Unhandled EPUB payload: {name}")
        files["OEBPS/" + name] = data
        items.append(f'<item id="asset{index}" href="{review.ESC(name)}" media-type="{media_types[Path(name).suffix]}"/>')
    files["META-INF/container.xml"] = b'''<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/package.opf" media-type="application/oebps-package+xml"/></rootfiles></container>'''
    files["OEBPS/package.opf"] = f'''<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="uid">urn:language-allocation:ta-Taml-IN:A00-U003-U005:0.1.0</dc:identifier><dc:title>{TITLE}</dc:title><dc:language>ta-Taml-IN</dc:language><dc:creator>OpenStax contributors; unofficial Tamil adaptation with OpenAI Codex</dc:creator><dc:rights>CC BY-NC-SA 4.0; component notices apply</dc:rights><meta property="dcterms:modified">2026-08-31T00:00:00Z</meta></metadata><manifest>{''.join(items)}</manifest><spine><itemref idref="book"/></spine></package>'''.encode("utf-8")
    for name, data in files.items():
        if name.endswith((".xml", ".xhtml", ".opf", ".svg")):
            ET.fromstring(data)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, data in [("mimetype", b"application/epub+zip"), *sorted(files.items())]:
            info = zipfile.ZipInfo(name, (2026, 8, 31, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_STORED if name == "mimetype" else zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    return buffer.getvalue()


def build_payload():
    # This checks both witnesses, hierarchy, mathematics and closed source SVGs;
    # it constructs candidates only and never rewrites the assembled source.
    _, gate = assembly.assemble()
    gate_inputs = {**gate["witnesses"],
                   **{row["path"]: row["sha256"] for row in gate["sections_in_canonical_order"]},
                   **{row["path"]: row["sha256"] for row in gate["media"]}}
    for key in ("front_matter", "glossary", "assembler"):
        gate_inputs[gate[key]["path"]] = gate[key]["sha256"]
    companion_digest, style_digest = review.sha(COMPANION), review.sha(STYLE)
    baseline, base_manifest = review.build_payload()
    source_doc = ET.fromstring(baseline["index.html"])
    source_sections = list(source_doc.find(f"{{{H}}}body/{{{H}}}main"))[:3]
    sources = [ET.parse(LANG / f"translation/m81243-{sid}.cnxml").getroot() for _, sid in review.UNITS]
    require([n.get("id") for n in source_sections] == [sid for _, sid in review.UNITS],
            "Unexpected source-preview boundaries")
    companion = ET.parse(COMPANION).getroot()
    questions, answers = validate_companion(companion)
    pieces, navigation = [], []
    inserted = False
    for section in companion:
        if section.get("id") == "ta-large-source-help":
            for source in source_sections:
                pieces.append(xhtml(source))
                navigation.append((source.get("id"), "".join(source.find(f"{{{H}}}h2").itertext())))
            inserted = True
        heading = section.find(f"{{{H}}}h2")
        require(heading is not None, "Companion section has no navigation heading")
        navigation.append((section.get("id"), "".join(heading.itertext())))
        pieces.append(xhtml(section))
    require(inserted, "Source insertion marker missing")
    credits = review.review_credits()
    old = "இந்த மதிப்பாய்வு வரைவில் மீட்புக் கற்றல் துணைப்பகுதி இன்னும் இணைக்கப்படவில்லை."
    require(credits.count(old) == 1, "Review credits changed")
    credits = credits.replace(old, "மீட்புக் கற்றல் விளக்கங்களும் 16 கேள்விகளும் அவற்றின் விடைகளும் புதிதாக எழுதப்பட்டவை; அவை மூலநூலிலிருந்து மொழிபெயர்க்கப்பட்டவை அல்ல.")
    pieces.append(credits)
    navigation.append(("lr-attribution", "மூலமும் உரிமமும்"))
    nav = "".join(f'<li><a href="#{review.ESC(i)}">{review.ESC(t)}</a></li>' for i, t in navigation)
    cover = f'''<header id="lr-start"><p class="eyebrow">A00 · U003–U005 · இந்தியத் தமிழ் · 0.1.0</p><h1>{TITLE}</h1><div class="draft-banner"><p>மதிப்பாய்வுக்கான கற்றல் பதிப்பு: மூலநூல் மொழிபெயர்ப்பும் தனியாகக் குறிக்கப்பட்ட புதிய மீட்புக் கற்றல் துணையும்.</p><p>இது முழுப் பாடத்திட்டமோ வகுப்பு ஒதுக்கீட்டுச் சோதனையோ அல்ல. தாய்மொழிப் பேச்சாளர், ஆசிரியர், கற்போர் மற்றும் உதவித் தொழில்நுட்பப் பயனர் மதிப்பாய்வு இன்னும் தேவை.</p></div><p><a href="#ta-large-start">கற்கத் தொடங்குங்கள்</a>. மூல எடுத்துக்காட்டுகளின் விடைகள் வெளிப்படையாக உள்ளன; புதிய கேள்விகளின் விடைகள் தனிப் பகுதிகளில் உள்ளன.</p><nav aria-label="உள்ளடக்கம்"><ol>{nav}</ol></nav></header>'''
    book = f'''<!DOCTYPE html><html xmlns="{H}" lang="ta-Taml-IN" xml:lang="ta-Taml-IN"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><title>{TITLE}</title><link rel="stylesheet" href="assets/large-number-review.css"/><link rel="stylesheet" href="assets/large-number-recovery.css"/></head><body><a class="skip" href="#lr-main">உள்ளடக்கத்திற்குச் செல்லுங்கள்</a>{cover}<main id="lr-main">{''.join(pieces)}</main></body></html>'''
    payload = {name: data for name, data in baseline.items() if name not in ("index.html", "build-manifest.json")}
    payload["assets/large-number-recovery.css"] = STYLE.read_bytes()
    payload["index.html"] = book.encode("utf-8")
    doc = validate(book, sources, payload, companion, source_sections)
    # Mutation checks prevent relaxed route/content validation from passing silently.
    mutations = [book.replace('href="#ta-large-R1"', 'href="#missing-remedy"', 1),
                 book.replace('id="ta-large-D1"', 'id="ta-large-D2"', 1),
                 book.replace('data-answer-for="ta-large-D1"', 'data-answer-for="ta-large-D2"', 1)]
    prose_mutation = ET.fromstring(book)
    source_para = next(n for n in sources[0].iter(f"{{{review.C}}}para") if n.get("id"))
    rendered_para = prose_mutation.find(f'.//*[@id="{source_para.get("id")}"]')
    require(rendered_para is not None, "Source prose negative-test target is missing")
    rendered_para.text = (rendered_para.text or "") + " மாற்றப்பட்டது"
    mutations.append(ET.tostring(prose_mutation, encoding="unicode"))
    for index, mutated in enumerate(mutations):
        require(mutated != book, "Negative fixture did not mutate document")
        try:
            validate(mutated, sources, payload, companion, source_sections)
        except ValueError as exc:
            require(index != 3 or "Source-preview content changed" in str(exc),
                    "Prose mutation failed for an unrelated reason")
            continue
        raise ValueError("Invalid generated companion passed validation")
    payload[EPUB_NAME] = make_epub(book, navigation, payload)
    inputs = dict(base_manifest["inputs"])
    for path in (COMPANION, STYLE, Path(__file__).resolve(), Path(assembly.__file__),
                 LANG / "provenance/m81243.id-ID.cnxml"):
        inputs[path.relative_to(LANG).as_posix()] = review.sha(path)
    require(review.sha(COMPANION) == companion_digest and review.sha(STYLE) == style_digest,
            "Companion/style changed during build")
    require(all(review.sha(LANG / name) == expected for name, expected in gate_inputs.items()),
            "Source validation input changed during build")
    manifest = {
        "version": "0.1.0", "status": "learning-segment-review-not-complete-module-or-course",
        "formats": ["HTML", "EPUB"], "locale": "ta-Taml-IN",
        "source_scope": base_manifest["scope"], "source_inputs": inputs,
        "source_validation_inputs": gate_inputs,
        "source_assembly_gate": "Both full witnesses and all source fragments validated as candidates, without writing",
        "navigation": [{"id": i, "title": title} for i, title in navigation],
        "counts": {"source_ids": 141, "source_mathml": 55, "source_exercises": 15,
                   "companion_questions": len(questions), "companion_answers": len(answers),
                   "mathml": 56, "inline_svg": 8, "tables": 6, "document_ids": len(review.ids(doc))},
        "negative_tests": len(mutations),
        "limits": ["Rendered QA and EPUBCheck are separate hash-matched receipts.",
                   "No new PDF or native-speaker/learner/assistive-technology certification is produced.",
                   "Four-of-four gates apply only within this learning segment."],
        "outputs": {name: {"bytes": len(data), "sha256": review.digest(data)} for name, data in sorted(payload.items())},
    }
    payload["build-manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return payload, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Compare all existing output bytes without writing")
    args = parser.parse_args()
    payload, manifest = build_payload()
    require(payload == build_payload()[0], "Repeat builds differ")
    out = OUTPUT.resolve()
    require(out == (LANG / "reader-large-recovery").resolve(), "Unexpected output target")
    existing = {p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file()} if out.exists() else set()
    require(existing <= set(payload), "Unexpected output files; no automatic deletion allowed")
    if args.check:
        require(existing == set(payload), "Output file set differs")
        require(all((out / name).read_bytes() == data for name, data in payload.items()), "Output bytes are stale")
    else:
        require(shutil.disk_usage(LANG).free > 100 * 1024 * 1024 + sum(map(len, payload.values())), "Insufficient space")
        for name, data in payload.items():
            path = out / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(json.dumps({"mode": "check" if args.check else "build", "files": len(payload),
                      "output": str(out), "html_sha256": review.digest(payload["index.html"]),
                      "epub_sha256": review.digest(payload[EPUB_NAME]), "counts": manifest["counts"]}, indent=2))


if __name__ == "__main__":
    main()
