"""Validate U002 source, reviewed answer fixtures and offline reader packages.

This is structural/regression QA, not native-speaker, educational-efficacy,
assistive-technology-user or PDF/UA certification. Builds must already exist.
"""
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import posixpath
import re
import shutil
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT / "ta-Taml-IN"
C = "http://cnx.rice.edu/cnxml"
M = "http://www.w3.org/1998/Math/MathML"
S = "http://www.w3.org/2000/svg"
H = "http://www.w3.org/1999/xhtml"
OPF = "http://www.idpf.org/2007/opf"


def text(node):
    return "".join(node.itertext())


def normalized(node):
    return " ".join(text(node).split())


def tree_signature(node):
    return node.tag, sorted(node.attrib.items()), (node.text or "").strip(), [(tree_signature(n), (n.tail or "").strip()) for n in node]


def companion_qa(path):
    companion = ET.parse(path).getroot()
    assert companion.tag == f"{{{H}}}div" and companion.get("lang") == "ta-Taml-IN"
    identifiers = [n.get("id") for n in companion.iter() if n.get("id")]
    assert len(identifiers) == len(set(identifiers)) and all(i.startswith("ta2-") for i in identifiers)
    questions = {n.get("id"): n for n in companion.iter() if n.get("data-kind")}
    answers = [n for n in companion.iter() if n.get("data-answer-for")]
    assert len(questions) == len(answers) == 16
    assert Counter(n.get("data-answer-for") for n in answers) == Counter(questions.keys())
    assert Counter(n.get("data-kind") for n in questions.values()) == {"diagnostic": 4, "practice": 4, "mastery": 4, "retry": 4}
    # Pin the actual question numbers as well as reviewed answers: editing a
    # question without its answer must not leave a misleading green receipt.
    question_numbers = {
        "D1": [482], "D2": [64, 6], "D3": [2, 4, 3], "D4": [205, 0, 25, 2],
        "P1": [351, 5, 5], "P2": [2, 1, 6], "P3": [304, 34, 3, 304, 0], "P4": [90, 10, 0, 9],
        "M1": [582, 8], "M2": [406, 0, 4, 406, 46], "M3": [271, 217, 7, 7], "M4": [132, 10, 100, 10, 1],
        "T1": [376, 7], "T2": [508, 0, 5, 508, 58], "T3": [461, 416, 6], "T4": [124, 10, 124],
    }
    # Each fixture has an answer prefix, an explanatory claim, and the specific
    # remedial explanation(s) needed. This guards already-reviewed prose; it
    # does not automatically judge the quality of arbitrary Tamil reasoning.
    fixtures = {
        "D1": ("3 இலக்கங்கள்: 4, 8, 2.", "482 என்ற ஒரு எண்ணைக் குறிக்கிறோம்", {"R1"}),
        "D2": ("பத்துகள் இடம்; மதிப்பு 60.", "6 பத்துகளைக் குறிக்கிறது", {"R1"}),
        "D3": ("243.", "200 + 40 + 3 = 243", {"R2"}),
        "D4": ("ஆம், மதிப்பு மாறும்.", "மற்ற இலக்கங்களின் இடங்களைக் காக்கிறது", {"R3"}),
        "P1": ("பத்துகள் இடம்; மதிப்பு 50.", "5 பத்துகளைக் குறிக்கும்", {"R1"}),
        "P2": ("216.", "200 + 10 + 6 = 216", {"R2"}),
        "P3": ("சமமல்ல.", "304 = 300 + 0 + 4; 34 = 30 + 4", {"R3"}),
        "P4": ("9 பத்துகள் பட்டைகள்; 0 ஒன்றுகள் கட்டங்கள்.", "ஒவ்வொரு பட்டையும் 10-ஐக் குறிக்கிறது", {"R2", "R3"}),
        "M1": ("பத்துகள் இடம்; மதிப்பு 80.", "இலக்கம் 8 என்பதும் அதன் மதிப்பு 80 என்பதும்", {"R1"}),
        "M2": ("0 பத்துகள் இடத்தில் உள்ளது.", "406 = 400 + 0 + 6", {"R3"}),
        "M3": ("271-இல் 7 பத்துகள் இடத்தில் உள்ளது; மதிப்பு 70.", "அதன் இடம் மாறுவதால் அது குறிக்கும் மதிப்பு மாறுகிறது", {"R1"}),
        "M4": ("1 நூறுகள் சதுரம், 3 பத்துகள் பட்டைகள், 2 ஒன்றுகள் கட்டங்கள்.", "132 = 100 + 30 + 2", {"R2"}),
        "T1": ("பத்துகள் இடம்; மதிப்பு 70.", "7 பத்துகளைக் குறிக்கும்", {"R1"}),
        "T2": ("0 பத்துகள் இடத்தில் உள்ளது.", "508 = 500 + 0 + 8", {"R3"}),
        "T3": ("461-இல் 6 பத்துகள் இடத்தில் உள்ளது; மதிப்பு 60.", "அது இருக்கும் இடம் மாறியதால் அதன் மதிப்பு மாறியுள்ளது", {"R1"}),
        "T4": ("1 நூறுகள் சதுரம், 2 பத்துகள் பட்டைகள், 4 ஒன்றுகள் கட்டங்கள்.", "124 = 100 + 20 + 4", {"R2"}),
    }
    assert set(questions) == {"ta2-" + k for k in fixtures}
    for answer in answers:
        key = answer.get("data-answer-for").removeprefix("ta2-")
        prefix, reasoning, routes = fixtures[key]
        answer_text = normalized(answer.find(f"{{{H}}}p"))
        assert answer_text.startswith(prefix) and reasoning in answer_text, f"Changed answer/reasoning: {key}"
        assert len(answer_text) > 100
        actual_routes = {n.get("href") for n in answer.findall(f".//{{{H}}}a")}
        assert {"#ta2-" + route for route in routes} <= actual_routes
        assert all(route[1:] in identifiers for route in actual_routes)
        question_text = " ".join(text(n) for n in questions["ta2-" + key].findall(f"{{{H}}}p"))
        assert [int(n) for n in re.findall(r"\d+", question_text)] == question_numbers[key], key
    sums = companion.findall(f".//{{{M}}}math")
    expected_sums = [(482, [400, 80, 2]), (24, [20, 4]), (205, [200, 0, 5]), (25, [20, 5]), (176, [100, 70, 6]), (237, [200, 30, 7])]
    assert len(sums) == len(expected_sums) == 6
    for node, (total, terms) in zip(sums, expected_sums):
        assert all(n.tag in (f"{{{M}}}math", f"{{{M}}}mrow", f"{{{M}}}mn", f"{{{M}}}mo") for n in node.iter())
        assert [int(n.text) for n in node.findall(f".//{{{M}}}mn")] == [total, *terms]
        assert [n.text for n in node.findall(f".//{{{M}}}mo")] == ["=", *(["+"] * (len(terms) - 1))]
        assert total == sum(terms)
    arithmetic = re.findall(r"(\d+(?:\s*\+\s*\d+)*)\s*=\s*(\d+(?:\s*\+\s*\d+)*)", text(companion))
    for left, right in arithmetic:
        assert sum(map(int, re.split(r"\s*\+\s*", left))) == sum(map(int, re.split(r"\s*\+\s*", right))), (left, right)
    r1 = companion.find(f'.//{{{H}}}section[@id="ta2-R1"]')
    assert "முழு எண்களைத் தசமப்புள்ளியோ பின்னக் குறியீடோ இல்லாமல்" in text(r1), "Rightmost-ones notation qualification regressed"
    return companion, {"items": 16, "one_to_one_answers": "16/16", "answer_reasoning_regression_fixtures": "16/16", "remediation_links": "16/16", "unique_ta2_ids": len(identifiers), "mathml_sums_checked": 6, "all_detected_additive_equalities_checked": len(arithmetic), "notation_scope_qualification": "present"}


def references_qa(doc, document_path, read_bytes):
    """Use one contained-path resolver for filesystem and EPUB dependencies."""
    ids = [n.get("id") for n in doc.iter() if n.get("id")]
    assert len(ids) == len(set(ids)), "Duplicate rendered IDs"
    id_set = set(ids)
    dependencies = set()
    fragments = 0

    def resolve(value, base):
        nonlocal fragments
        url = urlsplit(value)
        assert not url.netloc and not url.scheme, f"Nonlocal dependency: {value}"
        assert not url.query, f"Unexpected resource query: {value}"
        if url.path:
            resource = posixpath.normpath(posixpath.join(posixpath.dirname(base), unquote(url.path)))
            assert not resource.startswith(("../", "/")) and "\\" not in resource, value
        else:
            resource = base
        data = read_bytes(resource)
        if url.fragment:
            target_ids = id_set if resource == document_path else {n.get("id") for n in ET.fromstring(data).iter() if n.get("id")}
            assert unquote(url.fragment) in target_ids, value
            fragments += 1
        if resource != base:
            dependencies.add(resource)
        return resource

    for node in doc.iter():
        assert node.tag.rsplit("}", 1)[-1] not in ("script", "iframe", "form", "object", "embed")
        assert not any(key.lower().startswith("on") for key in node.attrib)
        assert "srcset" not in node.attrib, "Review srcset dependencies explicitly"
        for key in ("aria-labelledby", "aria-describedby", "headers"):
            assert all(ref in id_set for ref in node.get(key, "").split()), key
        for key in ("href", "src", "poster", "{http://www.w3.org/1999/xlink}href"):
            value = node.get(key)
            if not value:
                continue
            url = urlsplit(value)
            if url.scheme or url.netloc:
                assert node.tag == f"{{{H}}}a" and key == "href" and url.scheme in ("http", "https") and url.netloc
            else:
                resolve(value, document_path)
        for value in node.attrib.values():
            for target in re.findall(r"url\(['\"]?([^)'\"]+)['\"]?\)", value):
                resolve(target, document_path)
    css_files = {name for name in dependencies if name.endswith(".css")}
    for name in css_files:
        css = read_bytes(name).decode("utf-8")
        assert not re.search(r"@import\b", css), "Uninspected imported CSS"
        for target in re.findall(r"url\(['\"]?([^)'\"]+)['\"]?\)", css):
            resolve(target, name)
    return {"unique_ids": len(ids), "resolved_fragment_references": fragments, "local_dependencies": sorted(dependencies), "remote_runtime_dependencies": 0}


def reader_qa(target, companion, reader):
    document = ET.parse(reader / "index.html").getroot()
    assert document.get("lang") == document.get("{http://www.w3.org/XML/1998/namespace}lang") == "ta-Taml-IN"
    assert "\ufffd" not in (reader / "index.html").read_text(encoding="utf-8")

    def read_local(name):
        path = (reader / name).resolve()
        assert path.is_relative_to(reader.resolve()) and path.is_file(), name
        return path.read_bytes()

    closure = references_qa(document, "index.html", read_local)
    by_id = {n.get("id"): n for n in document.iter() if n.get("id")}
    source_section = by_id["fs-id2340048"]
    assert all(n.get("id") in by_id for n in target.iter() if n.get("id"))
    assert [math_signature(n) for n in target.findall(f".//{{{M}}}math")] == [math_signature(n) for n in source_section.findall(f".//{{{M}}}math")]
    for section in companion:
        assert tree_signature(section) == tree_signature(by_id[section.get("id")]), section.get("id")
    order = [n.get("id") for n in document.find(f"{{{H}}}body/{{{H}}}main")]
    assert order[order.index("fs-id2340048") + 1] == "ta2-source-help"
    assert [i for i in order if i.startswith("ta2-") and i != "ta2-attribution"] == [n.get("id") for n in companion]
    figures = ET.parse(LANG / "provenance/m81243.en.cnxml").findall(f".//{{{C}}}content//{{{C}}}figure")
    numbered = [n for n in figures if "unnumbered" not in n.get("class", "").split()]
    mapping = {n.get("id"): f"1.{i}" for i, n in enumerate(numbered, 1)}
    expected_mapping = {"CNX_BMath_Figure_01_01_002": "1.2", "CNX_BMath_Figure_01_01_004": "1.3", "CNX_BMath_Figure_01_01_005": "1.4"}
    for link in source_section.findall(f".//{{{H}}}a"):
        assert text(link) == "படம் " + mapping[link.get("href")[1:]]
    for fid, number in expected_mapping.items():
        assert mapping[fid] == number and text(by_id[fid].find(f"{{{H}}}figcaption")).startswith("படம் " + number)
    parents = {child: parent for parent in document.iter() for child in parent}
    for original in target.findall(f".//{{{C}}}table"):
        table = by_id[original.get("id")]
        assert table.tag == f"{{{H}}}table" and table.get("aria-label") == original.get("aria-label")
        region = parents[table]
        assert region.get("role") == "region" and region.get("tabindex") == "0" and region.get("aria-label")
        assert normalized(by_id[region.get("aria-describedby")]), "Missing visible scrolling instruction"
        original_rows = original.findall(f".//{{{C}}}row")
        rows = table.findall(f"{{{H}}}thead/{{{H}}}tr") + table.findall(f"{{{H}}}tbody/{{{H}}}tr")
        assert len(rows) == len(original_rows) == 5
        assert all(len(row) == 5 for row in rows)
        column_headers = [n.get("id") for n in rows[0]]
        assert all(n.tag == f"{{{H}}}th" and n.get("scope") == "col" and n.get("id") for n in rows[0])
        for index, (source_row, rendered_row) in enumerate(zip(original_rows, rows)):
            assert [normalized(n) for n in source_row] == [normalized(n) for n in rendered_row]
            if index == 0:
                continue
            row_header = rendered_row[1] if normalized(source_row[1]) else None
            if row_header is not None:
                assert row_header.tag == f"{{{H}}}th" and row_header.get("scope") == "row" and row_header.get("id")
            for column, cell in enumerate(rendered_row):
                associations = cell.get("headers", "").split()
                assert column_headers[column] in associations
                if row_header is not None and cell is not row_header:
                    assert row_header.get("id") in associations
        assert not table.findall(f".//{{{H}}}img") and not table.findall(f".//{{{S}}}svg")
    assert "overflow-x: auto" in (reader / "assets/u002.css").read_text(encoding="utf-8")
    for media in target.findall(f".//{{{C}}}media"):
        path = (LANG / "translation" / media.find(f"{{{C}}}image").get("src")).resolve()
        expected = copy.deepcopy(ET.parse(path).getroot())
        expected.find(f"{{{S}}}desc").text = media.get("alt")
        media_container = by_id[media.get("id")]
        rendered = media_container.find(f".//{{{S}}}svg")
        assert tree_signature(rendered) == tree_signature(expected), media.get("id")
        description = next(n for n in media_container.findall(f"{{{H}}}p") if "media-description" in n.get("class", "").split())
        assert media.get("alt") == text(description)
        region = parents[rendered]
        assert region.get("role") == "region" and region.get("tabindex") == "0" and region.get("aria-label")
        assert "diagram-scroll" in region.get("class", "").split()
        assert normalized(by_id[region.get("aria-describedby")]), "Missing visible diagram scrolling instruction"
        assert parents[description] is media_container, "Text alternative must remain outside the scroll region"
    assert len(document.findall(f".//{{{M}}}math")) == 57
    assert len(document.findall(f".//{{{S}}}svg")) == 9
    screen = ET.parse(reader / "screen.html").getroot()
    body = screen.find(f"{{{H}}}body")
    assert body.get("class") == "screen-profile"
    del body.attrib["class"]
    assert tree_signature(screen) == tree_signature(document), "Screen reader body differs from print HTML"
    references_qa(screen, "screen.html", read_local)
    assert "min-width: 34rem" in (reader / "assets/u002.css").read_text(encoding="utf-8")
    closure.update({"source_mathml_preserved": 51, "companion_mathml_preserved": 6, "tables_with_semantic_headers": 2, "column_headers": 10, "row_headers": 6, "svg_geometry_and_source_descriptions_preserved": 9, "keyboard_focusable_diagram_scroll_regions": 9, "figure_numbers": expected_mapping, "screen_profile_same_content": True, "companion_sections_unchanged": len(list(companion))})
    return closure


def epub_qa(reader, report_path):
    archive_path = reader / "ta-Taml-IN-A00-U002.epub"
    with zipfile.ZipFile(archive_path) as archive:
        assert archive.infolist()[0].filename == "mimetype" and archive.infolist()[0].compress_type == zipfile.ZIP_STORED
        assert archive.read("mimetype") == b"application/epub+zip" and archive.testzip() is None
        assert len(archive.namelist()) == len(set(archive.namelist()))
        for name in archive.namelist():
            assert not name.startswith("/") and ".." not in name.split("/")
            if name.endswith((".xhtml", ".opf", ".xml")):
                ET.fromstring(archive.read(name))
        assert archive.read("OEBPS/book.xhtml") == (reader / "index.html").read_bytes()
        book = ET.fromstring(archive.read("OEBPS/book.xhtml"))
        nav = ET.fromstring(archive.read("OEBPS/nav.xhtml"))
        book_closure = references_qa(book, "OEBPS/book.xhtml", archive.read)
        references_qa(nav, "OEBPS/nav.xhtml", archive.read)
        opf = ET.fromstring(archive.read("OEBPS/package.opf"))
        assert opf.find(".//{http://purl.org/dc/elements/1.1/}identifier").text == "urn:language-allocation:ta-Taml-IN:A00-U002:0.1.0"
        manifest = {n.get("id"): n for n in opf.findall(f"{{{OPF}}}manifest/{{{OPF}}}item")}
        assert set(manifest["book"].get("properties").split()) == {"mathml", "svg"}
        assert manifest["nav"].get("properties") == "nav"
        resources = {"OEBPS/" + n.get("href") for n in manifest.values()}
        assert all(name in archive.namelist() for name in resources)
        assert set(archive.namelist()) == resources | {"mimetype", "META-INF/container.xml", "OEBPS/package.opf"}
        assert [n.get("idref") for n in opf.findall(f"{{{OPF}}}spine/{{{OPF}}}itemref")] == ["book"]
        for relative in ("assets/u002.css", "assets/fonts/NotoSansTamil.ttf", "assets/fonts/OFL.txt", "LICENSE.txt"):
            assert archive.read("OEBPS/" + relative) == (reader / relative).read_bytes()
        css = (reader / "assets/book.css").read_text(encoding="utf-8").split("\n@page", 1)[0] + "\n"
        assert archive.read("OEBPS/assets/book.css") == css.encode()
        expected_nav = json.loads((reader / "build-manifest.json").read_text(encoding="utf-8"))["navigation"]
        assert [(n.get("href"), text(n)) for n in nav.findall(f".//{{{H}}}a")] == [("book.xhtml#" + n["id"], n["title"]) for n in expected_nav]
        external = {"status": "not-run-or-report-not-provided"}
        if report_path.is_file():
            report = json.loads(report_path.read_text(encoding="utf-8"))
            checker = report["checker"]
            assert checker["filename"] == archive_path.name
            assert all(checker[key] == 0 for key in ("nFatal", "nError", "nWarning", "nUsage"))
            assert not report["messages"]
            assert report["publication"]["identifier"] == "urn:language-allocation:ta-Taml-IN:A00-U002:0.1.0"
            checked = {n["fileName"] for n in report["items"]}
            assert checked == set(archive.namelist()), "EPUBCheck archive inventory mismatch"
            for item in report["items"]:
                digest = hashlib.sha256(archive.read(item["fileName"])).digest()
                # The installed 5.3.0 JSON reporter omits zero-padding on
                # individual hexadecimal bytes. Match its observed encoding
                # as well as conventional hex; our own hashes stay 64 digits.
                encodings = {digest.hex(), "".join(format(byte, "x") for byte in digest)}
                assert item["checkSum"] in encodings, "Stale EPUBCheck report"
            external = {"status": "pass", "version": checker["checkerVersion"], "fatal": 0, "errors": 0, "warnings": 0, "report_sha256": sha(report_path), "archive_entry_checksums_matched_to_current_epub": len(checked), "checksum_note":"Matches standard SHA-256 hex or the installed reporter's unpadded per-byte hex; independent 64-digit artifact hashes are recorded separately."}
    return {"internal_status": "pass", "crc": "pass", "html_content_identity": True, "font_and_license_packaged": True, "closure": book_closure, "epubcheck": external, "sha256": sha(archive_path)}


def repeat_qa(reader, repeat):
    manifests = [json.loads((folder / "build-manifest.json").read_text(encoding="utf-8")) for folder in (reader, repeat)]
    assert manifests[0] == manifests[1], "Repeat input/output manifest mismatch"
    expected_files = {"index.html", "screen.html", "ta-Taml-IN-A00-U002.epub", "LICENSE.txt", "assets/book.css", "assets/u002.css", "assets/fonts/NotoSansTamil.ttf", "assets/fonts/OFL.txt"}
    assert set(manifests[0]["outputs"]) == expected_files
    for relative, digest in manifests[0]["inputs"].items():
        assert sha(LANG / relative) == digest, f"Build input changed: {relative}"
    for folder, manifest in zip((reader, repeat), manifests):
        assert {p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file()} == expected_files | {"build-manifest.json"}
        for relative, identity in manifest["outputs"].items():
            assert sha(folder / relative) == identity["sha256"]
            assert (folder / relative).stat().st_size == identity["bytes"]
    assert sha(reader / "build-manifest.json") == sha(repeat / "build-manifest.json")
    return {"status": "pass", "identical_files_including_manifest": len(expected_files) + 1, "current_inputs_verified": len(manifests[0]["inputs"]), "outputs": manifests[0]["outputs"]}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def math_signature(node):
    value = (node.text or "").strip()
    if node.tag == f"{{{M}}}mtext":
        # Language changes are allowed; currencies, signs and numeric punctuation
        # are not discarded with the letters (unlike a digits-only comparison).
        value = re.sub(r"[^0-9$€₹.,…+\-=/×÷%]", "", value)
    return node.tag, sorted(node.attrib.items()), value, [math_signature(n) for n in node]


def main():
    if not __debug__:
        raise RuntimeError("Run QA without Python -O; assertions must remain enabled")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reader", type=Path, default=LANG / "reader-u002")
    parser.add_argument("--repeat", type=Path, default=ROOT / "build/ta-u002-repeat")
    parser.add_argument("--epubcheck-report", type=Path, default=LANG / "qa/U002-epubcheck.json")
    args = parser.parse_args()
    assert shutil.disk_usage(LANG).free > 100 * 1024 * 1024, "Less than 100 MiB free; receipt write paused"
    sid = "fs-id2340048"
    source = ET.parse(LANG / "provenance/m81243.en.cnxml").find(f'.//{{{C}}}section[@id="{sid}"]')
    target_path = LANG / f"translation/m81243-{sid}.cnxml"
    target = ET.parse(target_path).getroot()
    assert [(n.tag, n.get("id")) for n in source.iter()] == [(n.tag, n.get("id")) for n in target.iter()]
    assert target.get("{http://www.w3.org/XML/1998/namespace}lang") == "ta-Taml-IN"
    original_math = source.findall(f'.//{{{M}}}math')
    assert [math_signature(n) for n in original_math] == [math_signature(n) for n in target.findall(f'.//{{{M}}}math')]
    assert len(original_math) == 51
    assert [n.get("target-id") for n in source.findall(f'.//{{{C}}}link')] == [n.get("target-id") for n in target.findall(f'.//{{{C}}}link')]
    target_ids = {n.get("id") for n in target.iter() if n.get("id")}
    assert all(n.get("target-id") in target_ids for n in target.findall(f'.//{{{C}}}link'))
    svg_ids = set()
    media_files = []
    original_images = source.findall(f'.//{{{C}}}image')
    translated_images = target.findall(f'.//{{{C}}}image')
    assert len(original_images) == len(translated_images) == 9
    for original, image in zip(original_images, translated_images):
        expected = Path(original.get("src")).stem + ".svg"
        assert image.get("mime-type") == "image/svg+xml"
        assert image.get("src") == "../assets/u002/" + expected
        path = (target_path.parent / image.get("src")).resolve()
        assert path.is_relative_to(LANG / "assets/u002") and path.is_file()
        svg = ET.parse(path).getroot()
        assert svg.tag == f"{{{S}}}svg"
        ids = [n.get("id") for n in svg.iter() if n.get("id")]
        assert len(ids) == len(set(ids)) and not svg_ids.intersection(ids)
        svg_ids.update(ids)
        assert svg.get("role") == "img"
        assert svg.find(f"{{{S}}}title") is not None and svg.find(f"{{{S}}}desc") is not None
        for label in svg.get("aria-labelledby", "").split():
            assert label in ids
        assert "TamilBook" in path.read_text(encoding="utf-8")
        media_files.append({"path":path.relative_to(LANG).as_posix(), "sha256":sha(path)})
    for table in target.findall(f'.//{{{C}}}table'):
        group = table.find(f"{{{C}}}tgroup")
        assert group.get("cols") == "5"
        assert len(group.find(f"{{{C}}}thead/{{{C}}}row")) == 5
        assert table.get("aria-label") and table.get("aria-label") != source.find(f'.//{{{C}}}table[@id="{table.get("id")}"]').get("aria-label")
    expected_answers = {"fs-id2609767":"176", "fs-id2136425":"237"}
    for solution, answer in expected_answers.items():
        actual = target.find(f'.//{{{C}}}solution[@id="{solution}"]/{{{C}}}para')
        assert "".join(actual.itertext()).strip() == answer
    assert 1*100 + 7*10 + 6 == 176
    assert 2*100 + 3*10 + 7 == 237
    assert 3*100 + 7*10 + 4 == 374
    assert 1*100 + 3*10 + 8 == 138
    assert 2*100 + 1*10 + 5 == 215
    companion_path = LANG / "translation/recovery-u002.xhtml"
    companion, companion_checks = companion_qa(companion_path)
    reader_checks = reader_qa(target, companion, args.reader.resolve())
    repeat_checks = repeat_qa(args.reader.resolve(), args.repeat.resolve())
    epub_checks = epub_qa(args.reader.resolve(), args.epubcheck_report.resolve())
    pending = ["native-speaker/educator review", "assistive-technology user testing", "screen/print PDF rendering and PDF/UA checks are outside this verifier", "browser visual/interaction evidence must be recorded separately"]
    if epub_checks["epubcheck"]["status"] != "pass":
        pending.append("external EPUBCheck report bound to the current EPUB")
    result = {"status":"draft-structural-and-offline-checks-pass-not-complete-course", "scope":"m81243#fs-id2340048", "elements":len(list(source.iter())), "source_ids":len(target_ids), "math_expressions":51, "currency_and_operator_tokens":"preserved", "source_exercises_with_solutions":3, "tables":2, "svg_media":media_files, "source_sha256":sha(target_path), "companion_sha256":sha(companion_path), "verifier_sha256":sha(Path(__file__)), "companion":companion_checks, "reader":reader_checks, "epub":epub_checks, "repeat_build":repeat_checks, "pending":pending, "limitations":["Answer fixtures protect reviewed content; matching text is not independent proof of pedagogical efficacy or native Tamil quality.", "Semantic markup and local-resource closure do not certify screen-reader usability or PDF accessibility."]}
    (LANG / "qa/U002-structural-receipt.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
