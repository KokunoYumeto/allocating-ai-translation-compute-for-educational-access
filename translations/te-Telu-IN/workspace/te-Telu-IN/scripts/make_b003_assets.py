"""Preserve two pinned JPEGs and draw accessible, deterministic TE-B003 charts.

--originals-only writes only two selected JPEGs after SHA-256, ZIP CRC and pinned
Git blob checks. --verify and --self-test are read-only; no network or lazy fetch.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import xml.etree.ElementTree as ET
import zipfile

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parent
OUT = BASE / "assets/B003"
SOURCE = BASE / "sources/TE-B003.en.cnxml"
COMMIT = "38cae454e644abf9f0a623e876994553881597c9"
ARCHIVE_SHA = "effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917"
SOURCE_SHA = "bc72cfa64bed7541270041bcd045957daf40268dbc0286bfe3ee17ab3f86961d"
PREFIX = "osbooks-prealgebra-bundle-" + COMMIT + "/"
CN = "{http://cnx.rice.edu/cnxml}"
SVG = "{http://www.w3.org/2000/svg}"
ET.register_namespace("", SVG[1:-1])
NAMES = {11: "CNX_BMath_Figure_01_01_011.jpg", 12: "CNX_BMath_Figure_01_01_012_img.jpg"}
NUMBERS = {11: 5278194, 12: 63407218}
WIDTH, HEIGHT, LEFT, CELL = 2240, 460, 40, 144
INK, LINE = "#153a4b", "#318b90"
GROUPS = [("ట్రిలియన్లు", "Trillions"), ("బిలియన్లు", "Billions"),
          ("మిలియన్లు", "Millions"), ("వేలు", "Thousands"), ("ఒకట్లు", "Ones")]
PLACE_WORDS = [
    (("వంద", "ట్రిలియన్లు"), ("Hundred", "trillions")),
    (("పది", "ట్రిలియన్లు"), ("Ten", "trillions")),
    (("ట్రిలియన్లు",), ("Trillions",)),
    (("వంద", "బిలియన్లు"), ("Hundred", "billions")),
    (("పది", "బిలియన్లు"), ("Ten", "billions")),
    (("బిలియన్లు",), ("Billions",)),
    (("వంద", "మిలియన్లు"), ("Hundred", "millions")),
    (("పది", "మిలియన్లు"), ("Ten", "millions")),
    (("మిలియన్లు",), ("Millions",)),
    (("వంద", "వేలు"), ("Hundred", "thousands")),
    (("పదివేలు",), ("Ten", "thousands")),
    (("వేలు",), ("Thousands",)),
    (("వందలు",), ("Hundreds",)),
    (("పదులు",), ("Tens",)),
    (("ఒకట్లు",), ("Ones",)),
]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def source_assets(write_originals=False):
    need(file_digest(SOURCE) == SOURCE_SHA, "Frozen subsection hash changed")
    metadata = json.loads((BASE / "sources/TE-B003.source.json").read_text(encoding="utf-8"))
    need(metadata["unit"] == "TE-B003" and metadata["source_sha256"] == SOURCE_SHA
         and metadata["source_commit"] == COMMIT, "Unpinned source metadata")
    source = ET.parse(SOURCE).getroot()
    need(source.get("id") == "fs-id1883656", "Wrong subsection")
    parents = {c: p for p in source.iter() for c in p}
    images = list(source.iter(CN + "image"))
    wanted = {"../../media/" + name for name in NAMES.values()}
    need(len(images) == 2 and {im.get("src") for im in images} == wanted, "Wrong selected image set")
    lock = json.loads((BASE / "sources.lock.json").read_text(encoding="utf-8"))
    archive = next(r for r in lock["canonical_archives"] if r["id"] == "A00-A20-en-complete-archive")
    need(archive["sha256"] == ARCHIVE_SHA and archive["commit"] == COMMIT, "Unpinned archive")
    path = ROOT / archive["path"]
    need(path.stat().st_size == archive["bytes"], "Archive size changed")
    need(file_digest(path) == ARCHIVE_SHA, "Canonical archive SHA-256 mismatch")
    selected = ["media/" + Path(im.get("src")).name for im in images]
    env = os.environ.copy()
    env.update(GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
    tree = subprocess.check_output(["git", "-C", str(ROOT / "downloads/upstream-prealgebra"),
        "ls-tree", "-r", "-z", COMMIT, "--", *selected], env=env)
    blobs = {}
    for row in tree.split(b"\0"):
        if row:
            header, name = row.split(b"\t", 1)
            mode, kind, oid = header.split()
            need(kind == b"blob", "Selected member not a blob")
            blobs[name.decode()] = oid.decode()
    need(set(blobs) == set(selected), "Selected pinned blobs missing")
    records, total = [], 0
    with zipfile.ZipFile(path) as package:
        need(package.comment.decode() == COMMIT, "ZIP comment does not identify pin")
        for image, name in zip(images, selected):
            member = PREFIX + name
            info = package.getinfo(member)
            need(0 < info.file_size < 2_000_000, "Selected member exceeds small-file bound")
            payload = package.read(member)  # Selected-member ZIP CRC validation, not full extraction.
            total += len(payload)
            need(total < 4_000_000, "Selected originals exceed bounded output")
            blob = hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()
            need(blob == blobs[name], "Selected JPEG differs from pinned Git blob")
            target = OUT / "original" / Path(name).name
            if target.exists():
                need(target.read_bytes() == payload, "Preserved original differs; refusing overwrite")
            elif write_originals:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(payload)
            else:
                raise FileNotFoundError("Run --originals-only before verification: " + str(target))
            media = parents[image]
            parent = parents.get(media)
            number = next(k for k, v in NAMES.items() if Path(name).name == v)
            records.append({"number": number, "original_src": image.get("src"),
                "original_path": target.relative_to(BASE).as_posix(), "original_sha256": digest(payload),
                "original_bytes": len(payload), "source_git_blob_sha1": blob,
                "source_zip_member": member, "source_zip_crc32": f"{info.CRC:08x}",
                "media_id": media.get("id"),
                "figure_id": parent.get("id") if parent is not None and parent.tag == CN + "figure" else None,
                "localized_path": f"assets/B003/CNX_BMath_Figure_01_01_{number:03}.te.svg"})
    return records, total


def node(parent, tag, attrs=None, text=None):
    child = ET.SubElement(parent, SVG + tag, {str(k): str(v) for k, v in (attrs or {}).items()})
    child.text = text
    return child


def label(parent, x, y, value, size=24, color=INK, anchor="middle", **attrs):
    return node(parent, "text", {"x": x, "y": y, "font-size": size, "fill": color,
        "text-anchor": anchor, **attrs}, value)


def chart(number):
    value = NUMBERS[number]
    digits = str(value).rjust(15)
    root = ET.Element(SVG + "svg", {"width": str(WIDTH), "height": str(HEIGHT),
        "viewBox": f"0 0 {WIDTH} {HEIGHT}", "role": "img", "aria-labelledby": "title desc",
        "lang": "te", "font-family": "Nirmala UI, Noto Sans Telugu, sans-serif",
        "data-value": str(value), "data-columns": "15", "data-periods": "5"})
    node(root, "title", {"id": "title"}, f"స్థాన విలువల పట్టిక / Place-value chart: {value:,}")
    descriptions = []
    for col, ((te, en), digit) in enumerate(zip(PLACE_WORDS, digits)):
        descriptions.append(f"{' '.join(te)} ({' '.join(en)}): " +
                            (digit if digit.strip() else "ఖాళీ / blank"))
    node(root, "desc", {"id": "desc"},
        "15 స్థానాలు, 5 మూడంకెల సమూహాలు; ఎడమ నుంచి కుడికి / 15 places in five three-digit periods, left to right: " +
        "; ".join(descriptions) + ". Blank leading cells are not additional zeros. Each place unit is ten times the next place unit to its right. " +
        "International scale; million/billion/trillion Telugu spellings are editorial bilingual labels. New code-native redraw, not an altered source JPEG.")
    node(root, "rect", {"width": WIDTH, "height": HEIGHT, "fill": "white"})
    label(root, LEFT, 43, "స్థాన విలువలు / Place values", 28, anchor="start")
    label(root, WIDTH - LEFT, 43, f"{value:,}", 30, anchor="end", **{"data-role": "number-caption"})
    for group_index, (te, en) in enumerate(GROUPS):
        x = LEFT + group_index * CELL * 3
        group = node(root, "g", {"data-role": "period", "data-index": group_index,
            "data-first-column": group_index * 3, "data-column-count": 3})
        node(group, "rect", {"x": x, "y": 78, "width": CELL * 3, "height": 80,
            "fill": "#ccebea", "stroke": LINE, "stroke-width": 2})
        label(group, x + CELL * 1.5, 112, te, 28, **{"data-role": "period-name-te"})
        label(group, x + CELL * 1.5, 142, en, 20, **{"lang": "en", "data-role": "period-name-en"})
    for col, ((te, en), digit) in enumerate(zip(PLACE_WORDS, digits)):
        x = LEFT + col * CELL
        group = node(root, "g", {"data-role": "place-column", "data-column": col,
            "data-exponent": 14 - col, "data-digit": digit.strip(), "data-place-unit": 10 ** (14 - col)})
        node(group, "rect", {"x": x, "y": 158, "width": CELL, "height": 164,
            "fill": "#f7fbfb", "stroke": LINE, "stroke-width": 1.2, "data-role": "place-cell"})
        node(group, "rect", {"x": x, "y": 322, "width": CELL, "height": 68,
            "fill": "#e6f4f2" if digit.strip() else "white", "stroke": LINE,
            "stroke-width": 1.2, "data-role": "digit-cell"})
        for row, line in enumerate(te):
            label(group, x + CELL / 2, 200 + row * 32 if len(te) == 2 else 218,
                  line, 24, **{"data-role": "place-name-te"})
        for row, line in enumerate(en):
            label(group, x + CELL / 2, 267 + row * 25 if len(en) == 2 else 279,
                  line, 16, "#385b68", **{"lang": "en", "data-role": "place-name-en"})
        if digit.strip():
            label(group, x + CELL / 2, 368, digit, 38, **{"data-role": "digit"})
    for boundary in range(6):
        x = LEFT + boundary * 3 * CELL
        node(root, "line", {"x1": x, "x2": x, "y1": 78, "y2": 390,
            "stroke": LINE, "stroke-width": 3, "data-role": "period-boundary"})
    label(root, LEFT, 434, "అంతర్జాతీయ మూడంకెల సమూహాలు / International three-digit periods", 24, anchor="start")
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"


def math_check(number, payload):
    root = ET.fromstring(payload)
    need(root.tag == SVG + "svg" and root.get("viewBox") == f"0 0 {WIDTH} {HEIGHT}", "Wrong SVG canvas")
    need(not list(root.iter(SVG + "image")) and not list(root.iter(SVG + "script")), "SVG must be code-native/static")
    need(root.get("role") == "img" and root.get("aria-labelledby") == "title desc", "Missing SVG accessible name")
    need(root.find(SVG + "title") is not None and root.find(SVG + "desc") is not None, "Missing descriptive text")
    need(root.get("data-value") == str(NUMBERS[number]), "Wrong figure value")
    expected = str(NUMBERS[number]).rjust(15)
    columns = [e for e in root.iter(SVG + "g") if e.get("data-role") == "place-column"]
    need(len(columns) == 15, "Wrong number of place columns")
    value = 0
    for col, (group, digit) in enumerate(zip(columns, expected)):
        need(group.get("data-column") == str(col) and group.get("data-exponent") == str(14 - col), "Place order wrong")
        need(group.get("data-place-unit") == str(10 ** (14 - col)), "Place scale wrong")
        need(group.get("data-digit") == digit.strip(), "Digit occupies wrong place")
        cells = [e for e in group if e.get("data-role") in {"place-cell", "digit-cell"}]
        need(len(cells) == 2 and all(e.get("x") == str(LEFT + col * CELL) and e.get("width") == str(CELL) for e in cells), "Column geometry drift")
        for language, terms in zip(("te", "en"), PLACE_WORDS[col]):
            actual = [e.text for e in group if e.get("data-role") == "place-name-" + language]
            need(actual == list(terms), "Visible place label mismatch")
        printed = [e for e in group if e.get("data-role") == "digit"]
        need([e.text for e in printed] == ([digit] if digit.strip() else []), "Visible digit mismatch or leading blank filled")
        if digit.strip():
            need(printed[0].get("x") == str(LEFT + col * CELL + CELL / 2), "Digit misaligned with column center")
            value += int(digit) * 10 ** (14 - col)
    need(value == NUMBERS[number], "Positional sum differs from source number")
    periods = [e for e in root.iter(SVG + "g") if e.get("data-role") == "period"]
    need(len(periods) == 5, "Missing period")
    for index, (group, names) in enumerate(zip(periods, GROUPS)):
        need(group.get("data-first-column") == str(index * 3) and group.get("data-column-count") == "3", "Period grouping changed")
        need([e.text for e in group if e.get("data-role") == "period-name-te"] == [names[0]], "Telugu period label changed")
        need([e.text for e in group if e.get("data-role") == "period-name-en"] == [names[1]], "English period label changed")
    boundaries = [e for e in root.iter(SVG + "line") if e.get("data-role") == "period-boundary"]
    need([e.get("x1") for e in boundaries] == [str(LEFT + i * 3 * CELL) for i in range(6)], "Period boundary positions changed")
    for rect in root.iter(SVG + "rect"):
        x, y = float(rect.get("x", 0)), float(rect.get("y", 0))
        need(x >= 0 and y >= 0 and x + float(rect.get("width")) <= WIDTH
             and y + float(rect.get("height")) <= HEIGHT, "Rectangle outside canvas")
    return {"columns": 15, "periods": 5, "columns_per_period": 3,
        "exponents_left_to_right": list(range(14, -1, -1)),
        "leading_blank_cells": 15 - len(str(value)), "digits_left_to_right": list(str(value)),
        "value": value, "digits_in_correct_columns": True, "visible_place_labels_match": True}


def self_test():
    """Reject independent in-memory digit, zero, label, scale and grouping defects."""
    rejected = 0
    for number in NUMBERS:
        payload = chart(number)
        math_check(number, payload)
        for case in range(6):
            root = ET.fromstring(payload)
            columns = [e for e in root.iter(SVG + "g") if e.get("data-role") == "place-column"]
            if case == 0:
                columns[-1].set("data-digit", "9")
            elif case == 1:
                victim = next(e for e in columns[-1] if e.get("data-role") == "digit")
                victim.text = "0"
            elif case == 2:
                victim = next(e for e in columns[0] if e.get("data-role") == "place-name-te")
                victim.text = "లక్షలు"
            elif case == 3:
                columns[0].set("data-place-unit", "100000")
            elif case == 4:
                victim = next(e for e in root.iter(SVG + "g") if e.get("data-role") == "period")
                victim.set("data-column-count", "2")
            else:
                label(columns[0], LEFT + CELL / 2, 368, "0", **{"data-role": "digit"})
            try:
                math_check(number, ET.tostring(root))
            except ValueError:
                rejected += 1
            else:
                raise AssertionError(f"Accepted corrupt chart {number}, fixture{case}")
    print(f"PASS: two valid charts; {rejected} corrupted digit/blank/label/scale/period fixtures rejected; no writes")


def build(verify=False, originals_only=False):
    records, size = source_assets(write_originals=not verify)
    if originals_only:
        print(json.dumps({"originals": records, "bytes": size, "archive_sha256_crc_git_blobs": "PASS"}, ensure_ascii=False))
        return
    for record in records:
        number = record.pop("number")
        payload = chart(number)
        record.update(math_checks=math_check(number, payload), localized_sha256=digest(payload),
            localized_bytes=len(payload), recommended_min_width_px=WIDTH,
            disclosure="New code-native mathematical redraw; original JPEG unchanged. Horizontal bilingual labels replace rotated English labels; source positions and values preserved.")
        target = BASE / record["localized_path"]
        if verify:
            need(target.read_bytes() == payload, "SVG differs from deterministic generator")
            math_check(number, target.read_bytes())
        else:
            target.write_bytes(payload)
    manifest = {"schema": "te-b002-assets-v1", "unit": "TE-B003", "source_subsection_id": "fs-id1883656",
        "source_subsection_sha256": SOURCE_SHA, "canonical_commit": COMMIT,
        "canonical_archive_sha256": ARCHIVE_SHA,
        "source_attribution": "OpenStax, Prealgebra 2e; existing project notices and source attribution remain applicable.",
        "generator": "scripts/make_b003_assets.py", "verification_command": "python -B te-Telu-IN/scripts/make_b003_assets.py --verify",
        "scope": "Exactly two selected unchanged JPEGs and two new SVGs; no downloads or bulk extraction.",
        "canon_consulted": ["C10", "C11", "C12", "TS6-PV-005", "TS6-COMMA-008"],
        "choices": ["Preserve15 positions in five international three-digit periods; never substitute lakh/crore labels.",
            "Retain blank leading cells and the internal zero of63,407,218; digits aligned to their source place columns.",
            "Use witnessed small-place terms; million/billion/trillion loanwords are editorial bilingual choices, not claimed official TS/AP witnesses.",
            "Use horizontal multiline labels at native2240px width; reader should pan locally rather than shrink text.",
            "Original011 has four bands including its title; original012 has three bands and no visible globaltitle. See DECISIONS.md for corrected accessibility descriptions.",
            "Code-native layout adds an explicit bilingual chart heading and number caption. The canonical originals remain byte-exact and accessible in parallel English.",
            "Both originals read and visually inspected before drawing; structural tests do not replace main-task rendered-reader inspection.",
            "Manifest uses the existing te-b002-assets-v1 field schema for build_unit compatibility; unit and generator identify B003."],
        "assets": records,
        "qa": {"selected_original_count": 2, "original_bytes": size, "localized_svg_count": 2,
            "localized_bytes": sum(r["localized_bytes"] for r in records),
            "all_unit_counts_values_and_digit_links": "PASS", "selected_original_crc_and_git_blob_hashes": "PASS",
            "visual_svg_review": "Pending main-task final reader inspection; source JPEGs viewed before authoring."}}
    encoded = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    if verify:
        need((OUT / "manifest.json").read_bytes() == encoded, "Manifest differs from source/generator")
    else:
        (OUT / "manifest.json").write_bytes(encoded)
        sections = []
        for record in records:
            sections.append(f'<section><h2>{record["media_id"]}</h2><p>Unchanged original</p><img class="original" src="original/{Path(record["original_path"]).name}" alt="Unchanged canonical chart">'
                f'<p>New Telugu redraw: scroll horizontally to inspect all15 positions.</p><div class="pan" tabindex="0"><img class="chart" src="{Path(record["localized_path"]).name}" alt="Bilingual15-column place-value chart"></div></section>')
        preview = '<!doctype html><html lang="te"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>B003 chart QA</title>' + \
            '<style>body{font-family:"Nirmala UI",sans-serif;background:#eef4f4;color:#153a4b;margin:24px}main{max-width:1100px;margin:auto}section{padding:20px;background:white;margin:24px 0}.original{max-width:100%;height:auto}.pan{overflow-x:auto;max-width:100%;border:1px solid #318b90}.chart{display:block;width:2240px;max-width:none;height:auto}</style><main><h1>B003 source and Telugu charts</h1>' + \
            ''.join(sections) + '</main></html>\n'
        (OUT / "preview.html").write_text(preview, encoding="utf-8")
    print(json.dumps({"status": "PASS", **manifest["qa"]}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--originals-only", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    need(sum((args.originals_only, args.verify, args.self_test)) <= 1, "Choose at most one operation")
    if args.self_test:
        self_test()
    else:
        build(args.verify, args.originals_only)
