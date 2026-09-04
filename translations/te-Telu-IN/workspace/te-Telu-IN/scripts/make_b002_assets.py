"""Build nine small code-native TE-B002 SVGs from checked mathematical specs.

Reads only the nine selected JPEG ZIP members, verifies their pinned Git blobs,
and preserves their bytes under assets/B002/original/. No downloads or bulk
extraction. --originals-only permits visual inspection before authoring; --verify
is read-only and checks source bytes, deterministic SVGs, counts and the manifest.
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
OUT = BASE / "assets/B002"
SOURCE = BASE / "sources/TE-B002.en.cnxml"
COMMIT = "38cae454e644abf9f0a623e876994553881597c9"
ARCHIVE_SHA = "effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917"
PREFIX = "osbooks-prealgebra-bundle-" + COMMIT + "/"
CN = "{http://cnx.rice.edu/cnxml}"
NS = "http://www.w3.org/2000/svg"
SVG = "{" + NS + "}"
ET.register_namespace("", NS)
INK, RED = "#153a4b", "#b12835"
COLORS = {"hundred": ("#d9f0f0", "#23676b"), "ten": ("#fff0c8", "#8b6109"),
          "one": ("#fbe0e5", "#8e3b4d")}
WORDS = {"hundred": ("వందలు", "hundreds"), "ten": ("పదులు", "tens"), "one": ("ఒకట్లు", "ones")}
VALUES = {"hundred": 100, "ten": 10, "one": 1}
SUFFIXES = {2: "002.jpg", 3: "003_img.jpg", 4: "004.jpg", 5: "005.jpg",
            6: "006_img.jpg", 7: "007_img.jpg", 8: "008_img.jpg", 9: "009_img.jpg", 10: "010_img.jpg"}
MODELS = {4: (1, 1, 1), 5: (1, 3, 8), 7: (2, 1, 5), 9: (1, 7, 6), 10: (2, 3, 7)}
NUMERALS = {5: 138, 7: 215, 9: 176, 10: 237}
ARROWS = {3: (3, 7, 4), 6: (1, 3, 8), 8: (2, 1, 5)}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def need(condition, message):
    if not condition:
        raise ValueError(message)


def child(parent, tag, attrs=None, text=None, **kwargs):
    element = ET.SubElement(parent, SVG + tag, {str(k): str(v) for k, v in (attrs or {}).items()} | kwargs)
    element.text = text
    return element


def text(parent, x, y, content, size=24, color=INK, anchor="middle", **attrs):
    return child(parent, "text", {"x": x, "y": y, "font-size": size, "fill": color,
                                  "text-anchor": anchor, **attrs}, content)


def frame(width, height, title, description):
    root = ET.Element(SVG + "svg", {"width": str(width), "height": str(height),
        "viewBox": f"0 0 {width} {height}", "role": "img", "aria-labelledby": "title desc",
        "lang": "te", "font-family": "Nirmala UI, Noto Sans Telugu, sans-serif"})
    child(root, "title", {"id": "title"}, title)
    child(root, "desc", {"id": "desc"}, description)
    child(root, "rect", {"width": width, "height": height, "fill": "white"})
    return root


def place_heading(parent, x, y, kind):
    te, en = WORDS[kind]
    text(parent, x, y, te, 27)
    text(parent, x, y + 25, en, 17, "#526573")


def block(parent, kind, x, y, cell=12):
    """Actual unit rectangles, not a decorative pattern: 100, 10 or 1 per group."""
    rows, cols = ((10, 10) if kind == "hundred" else (1, 10) if kind == "ten" else (1, 1))
    group = child(parent, "g", {"data-kind": kind, "data-value": VALUES[kind]})
    fill, stroke = COLORS[kind]
    for row in range(rows):
        for col in range(cols):
            child(group, "rect", {"x": x + cell * col, "y": y + cell * row,
                "width": cell, "height": cell, "fill": fill, "stroke": stroke,
                "stroke-width": 0.8, "data-cell": "1", "data-row": row, "data-col": col})
    return group


def base_ten(number):
    counts = dict(zip(("hundred", "ten", "one"), MODELS[number]))
    if number == 4:
        root = frame(900, 300, "ఒకట్లు, పదులు, వందలు / Base-ten units",
                     "ఒకట్లు: 1; పదులు: 1 (10 ఒకట్లు); వందలు: 1 (10 పదులు = 100 ఒకట్లు). Separate models, not a combined-number question.")
        for x, kind in zip((150, 450, 750), ("one", "ten", "hundred")):
            place_heading(root, x, 38, kind)
            block(root, kind, x - (6 if kind == "one" else 60), 120)
            text(root, x, 278, {"one": "1", "ten": "10 × 1 = 10", "hundred": "10 × 10 = 100"}[kind], 22)
        return root
    expected = NUMERALS[number]
    root = frame(960, 370, "వందలు, పదులు, ఒకట్లు / Base-ten block model",
                 f"వందలు: {counts['hundred']}; పదులు: {counts['ten']}; ఒకట్లు: {counts['one']}. {counts['hundred']} hundreds squares of 100 unit cells each; {counts['ten']} tens rods of 10 cells each; {counts['one']} single units. The visible diagram does not print the answer.")
    for lane, kind in enumerate(("hundred", "ten", "one")):
        center = 160 + 320 * lane
        place_heading(root, center, 40, kind)
        count = counts[kind]
        if kind == "hundred":
            start = center - (count * 120 + (count - 1) * 18) / 2
            for i in range(count):
                block(root, kind, start + i * 138, 128)
        elif kind == "ten":
            for i in range(count):
                block(root, kind, center - 60, 110 + i * 26)
        else:
            for i in range(count):
                block(root, kind, center - 42 + (i % 4) * 24, 146 + (i // 4) * 30)
        if number == 5:
            # The source figure labels these counts; the example/try figures do not.
            text(root, center, 335, f"{count} × {VALUES[kind]} = {count * VALUES[kind]}", 23)
    need(sum(counts[k] * VALUES[k] for k in counts) == expected, "Model specification error")
    return root


def bills():
    root = frame(960, 400, "అమెరికా డాలర్లు / U.S. dollar bill groups",
                 "3 × $100, 7 × $10, 4 × $1; అమెరికా డాలర్లు (USD). Schematic counting cards, not currency artwork: three $100 bills, seven $10 bills and four $1 bills. No currency conversion.")
    text(root, 480, 35, "అమెరికా డాలర్లు (U.S. dollars)", 26)
    text(root, 480, 66, "లెక్కింపు నమూనా / schematic counting cards", 18, "#526573")
    for lane, (count, amount) in enumerate(((3, 100), (7, 10), (4, 1))):
        center = 160 + lane * 320
        for i in range(count):
            x, y = center - 110 + (i % 2) * 118, 105 + (i // 2) * 53
            group = child(root, "g", {"data-kind": "bill", "data-denomination": amount})
            child(group, "rect", {"x": x, "y": y, "width": 102, "height": 40, "rx": 5,
                "fill": "#edf4f7", "stroke": "#416477", "stroke-width": 1.8})
            text(group, x + 51, y + 28, f"${amount}", 23)
        text(root, center, 350, f"{count} × ${amount} = ${count * amount}", 24)
    return root


def arrows(number):
    digits = ARROWS[number]
    currency = number == 3
    values = [digits[i] * (100, 10, 1)[i] for i in range(3)]
    total = sum(values)
    root = frame(860, 355, "స్థాన విలువలు / Place-value digit correspondence",
                 f"{'అమెరికా డాలర్లు (USD): ' if currency else ''}విస్తరణ రూపం: {values[0]} + {values[1]} + {values[2]}; సంక్షిప్త రూపం: {total}. Red leading digits connect by arrows to their matching positions in the compact numeral.")
    text(root, 430, 30, "అమెరికా డాలర్లు (U.S. dollars)" if currency else "విస్తరణ రూపం / expanded form", 23)
    defs = child(root, "defs")
    marker = child(defs, "marker", {"id": "arrowhead", "viewBox": "0 0 10 10", "refX": 8,
        "refY": 5, "markerWidth": 6, "markerHeight": 6, "orient": "auto-start-reverse"})
    child(marker, "path", {"d": "M0 0L10 5L0 10Z", "fill": RED})
    for i, (sx, ex, kind) in enumerate(zip((160, 420, 680), (386, 430, 474), ("hundred", "ten", "one"))):
        place_heading(root, sx + 15, 73, kind)
        if currency:
            text(root, sx - 27, 145, "$", 32)
        for j, digit in enumerate(str(values[i])):
            attrs = {"id": f"expanded-{i}-{j}", "data-digit": digit,
                     "data-role": "expanded-digit", "data-place-index": i}
            text(root, sx + 27 * j, 145, digit, 32, RED if j == 0 else INK, **attrs)
        text(root, ex, 288, str(digits[i]), 37, RED, id=f"compact-{i}", **{"data-role": "compact-digit", "data-digit": str(digits[i])})
        child(root, "path", {"d": f"M{sx} 161C{sx} 211 {ex} 211 {ex} 248",
            "fill": "none", "stroke": RED, "stroke-width": 2.5, "marker-end": "url(#arrowhead)",
            "data-role": "digit-arrow", "data-from": f"expanded-{i}-0", "data-to": f"compact-{i}",
            "data-place-value": (100, 10, 1)[i]})
    for x in (313, 573):
        text(root, x, 145, "+", 30)
    if currency:
        text(root, 342, 288, "$", 37)
    text(root, 430, 334, "సంక్షిప్త రూపం / compact form", 23)
    return root


def svg_bytes(number):
    root = bills() if number == 2 else arrows(number) if number in ARROWS else base_ten(number)
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"


def math_check(number, payload):
    root = ET.fromstring(payload)
    need(root.tag == SVG + "svg", "Not SVG")
    need(not list(root.iter(SVG + "image")) and not list(root.iter(SVG + "script")), "SVG must be code-native/static")
    if number == 2:
        groups = [e for e in root.iter(SVG + "g") if e.get("data-kind") == "bill"]
        actual = {value: sum(g.get("data-denomination") == str(value) for g in groups) for value in (100, 10, 1)}
        need(actual == {100: 3, 10: 7, 1: 4}, "Incorrect dollar group counts")
        need(sum(k * v for k, v in actual.items()) == 374, "Dollar total error")
        return {"bill_counts": actual, "currency": "USD", "value": 374}
    if number in MODELS:
        groups = [e for e in root.iter(SVG + "g") if e.get("data-kind") in VALUES]
        actual = tuple(sum(g.get("data-kind") == k for g in groups) for k in ("hundred", "ten", "one"))
        need(actual == MODELS[number], "Incorrect block group counts")
        for group in groups:
            kind = group.get("data-kind")
            cells = [e for e in group if e.get("data-cell") == "1"]
            rows, cols = (10, 10) if kind == "hundred" else (1, 10) if kind == "ten" else (1, 1)
            need(len(cells) == VALUES[kind], "Wrong unit-cell count")
            need({(int(c.get('data-row')), int(c.get('data-col'))) for c in cells} == {(r,c) for r in range(rows) for c in range(cols)}, "Wrong grid dimensions")
            need(all(c.get("width") == "12" and c.get("height") == "12" for c in cells), "Inconsistent unit scale")
        result = {"groups_hundreds_tens_ones": list(actual), "unit_cells_per_group": [100, 10, 1]}
        if number != 4:
            result["value"] = actual[0] * 100 + actual[1] * 10 + actual[2]
            need(result["value"] == NUMERALS[number], "Incorrect modeled value")
        else:
            result["separate_unit_legend_not_combined_number"] = True
        return result
    ids = {e.get("id"): e for e in root.iter() if e.get("id")}
    links = [e for e in root.iter(SVG + "path") if e.get("data-role") == "digit-arrow"]
    need(len(links) == 3, "Missing digit arrow")
    actual_digits = []
    for i, arrow in enumerate(links):
        start, end = ids[arrow.get("data-from")], ids[arrow.get("data-to")]
        need(start.text == end.text == str(ARROWS[number][i]), "Incorrect digit correspondence")
        sx, ex = start.get("x"), end.get("x")
        need(arrow.get("d") == f"M{sx} 161C{sx} 211 {ex} 211 {ex} 248", "Arrow geometry misses digit centers")
        need(start.get("fill") == end.get("fill") == RED, "Source digit emphasis lost")
        actual_digits.append(int(end.text))
    need(int("".join(map(str, actual_digits))) == sum(d * p for d, p in zip(actual_digits, (100, 10, 1))), "Place expansion mismatch")
    return {"digits": actual_digits, "place_values": [100, 10, 1], "value": int("".join(map(str, actual_digits))), "digit_arrows": 3, "red_emphasis": True}


def self_test():
    """Independent in-memory negative fixtures; never write test files."""
    for number in SUFFIXES:
        payload = svg_bytes(number)
        math_check(number, payload)
        root = ET.fromstring(payload)
        width, height = map(float, root.get("viewBox").split()[2:])
        for rectangle in root.iter(SVG + "rect"):
            x, y = float(rectangle.get("x", 0)), float(rectangle.get("y", 0))
            need(x >= 0 and y >= 0 and x + float(rectangle.get("width")) <= width
                 and y + float(rectangle.get("height")) <= height, "Rectangle outside canvas")
        if number == 2:
            victim = next(e for e in root if e.get("data-kind") == "bill")
            root.remove(victim)
        elif number in MODELS:
            victim = next(e for e in root.iter(SVG + "g") if e.get("data-kind") in VALUES)
            victim.remove(victim[0])
        else:
            victim = next(e for e in root.iter(SVG + "path") if e.get("data-role") == "digit-arrow")
            victim.set("data-to", "compact-1")
        try:
            math_check(number, ET.tostring(root))
        except ValueError:
            pass
        else:
            raise AssertionError(f"Incorrect fixture was accepted: {number}")
    print("PASS: nine valid diagrams, nine count/arrow corruption fixtures rejected, all rectangles inside SVG canvases; no writes")


def source_assets(write_originals=False):
    source = ET.parse(SOURCE).getroot()
    need(source.get("id") == "fs-id2340048", "Wrong source subsection")
    parents = {c: p for p in source.iter() for c in p}
    images = list(source.iter(CN + "image"))
    wanted = {"../../media/CNX_BMath_Figure_01_01_" + tail for tail in SUFFIXES.values()}
    need(len(images) == 9 and {im.get("src") for im in images} == wanted, "Unexpected source image set")
    lock = json.loads((BASE / "sources.lock.json").read_text(encoding="utf-8"))
    archive = next(r for r in lock["canonical_archives"] if r["id"] == "A00-A20-en-complete-archive")
    need(archive["sha256"] == ARCHIVE_SHA and archive["commit"] == COMMIT, "Unpinned archive")
    path = ROOT / archive["path"]
    need(path.stat().st_size == archive["bytes"], "Archive size changed")
    names = ["media/" + Path(im.get("src")).name for im in images]
    env = os.environ.copy()
    env.update(GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
    output = subprocess.check_output(["git", "-C", str(ROOT / "downloads/upstream-prealgebra"),
        "ls-tree", "-r", "-z", COMMIT, "--", *names], env=env)
    blobs = {}
    for row in output.split(b"\0"):
        if row:
            header, member = row.split(b"\t", 1)
            mode, kind, oid = header.split()
            need(kind == b"blob", "Unexpected Git object type")
            blobs[member.decode()] = oid.decode()
    need(set(blobs) == set(names), "Missing pinned selected blobs")
    records, total = [], 0
    with zipfile.ZipFile(path) as package:
        need(package.comment.decode() == COMMIT, "Wrong ZIP commit comment")
        for image, relative in zip(images, names):
            member = PREFIX + relative
            info = package.getinfo(member)
            need(0 < info.file_size < 2_000_000, "Selected image exceeds small-file bound")
            payload = package.read(member)  # This selected member only; CRC checked by ZipFile.
            total += len(payload)
            need(total < 8_000_000, "Selected originals exceed small-output bound")
            blob = hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()
            need(blob == blobs[relative], "Selected JPEG differs from pinned Git blob")
            filename = Path(relative).name
            target = OUT / "original" / filename
            if target.exists():
                need(target.read_bytes() == payload, "Preserved original differs; refusing overwrite: " + filename)
            elif write_originals:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(payload)
            else:
                raise FileNotFoundError("Run --originals-only before verification: " + str(target))
            media = parents[image]
            parent = parents.get(media)
            figure_id = parent.get("id") if parent is not None and parent.tag == CN + "figure" else None
            number = next(k for k,v in SUFFIXES.items() if filename.endswith(v))
            records.append({"number": number, "original_src": image.get("src"),
                "original_path": target.relative_to(BASE).as_posix(), "original_sha256": digest(payload),
                "original_bytes": len(payload), "source_git_blob_sha1": blob,
                "source_zip_member": member, "media_id": media.get("id"), "figure_id": figure_id,
                "localized_path": f"assets/B002/CNX_BMath_Figure_01_01_{number:03}.te.svg"})
    return records, total


def build(verify=False, originals_only=False):
    records, original_bytes = source_assets(write_originals=not verify)
    if originals_only:
        print(json.dumps({"originals": len(records), "bytes": original_bytes, "selected_member_blob_hashes_and_crc": "PASS"}))
        return
    for record in records:
        number = record.pop("number")
        payload = svg_bytes(number)
        record["math_checks"] = math_check(number, payload)
        record["localized_sha256"] = digest(payload)
        record["localized_bytes"] = len(payload)
        record["disclosure"] = "New code-native mathematical redraw; no source JPEG pixels edited or embedded."
        target = BASE / record["localized_path"]
        if verify:
            need(target.read_bytes() == payload, "SVG differs from deterministic generator: " + target.name)
            math_check(number, target.read_bytes())
        else:
            target.write_bytes(payload)
    manifest = {"schema": "te-b002-assets-v1", "unit": "TE-B002", "source_subsection_id": "fs-id2340048",
        "source_subsection_sha256": digest(SOURCE.read_bytes()), "canonical_commit": COMMIT,
        "canonical_archive_sha256": ARCHIVE_SHA, "source_attribution": "OpenStax, Prealgebra 2e; existing project notices and source attribution remain applicable.",
        "generator": "scripts/make_b002_assets.py", "verification_command": "python -B te-Telu-IN/scripts/make_b002_assets.py --verify",
        "scope": "Exactly nine selected unchanged JPEGs and nine new SVGs; no downloads or bulk extraction.",
        "canon_consulted": ["C03", "C04", "C05", "C10", "C11", "C12"],
        "choices": ["Keep U.S. dollars without rupee conversion; draw plain counting cards, not currency artwork.",
                    "Use witnessed వందలు, పదులు, ఒకట్లు and explicit equal-size unit cells.",
                    "Retain red significant digits and their three correspondence arrows.",
                    "Preserve source order of the unit/rod/square legend; preserve all modeled counts.",
                    "Do not print answers or counted quantities in the 215/176/237 question diagrams.",
                    "AP differences are unverified; no native-speaker approval claimed.",
                    "Original JPEGs individually read and visually inspected; see DECISIONS.md in this asset directory.",
                    "Browser discovery returned no available browser; mathematical and structural tests do not replace final rendered-reader inspection."],
        "assets": records,
        "qa": {"selected_original_count": 9, "original_bytes": original_bytes,
               "localized_svg_count": 9, "localized_bytes": sum(r["localized_bytes"] for r in records),
               "all_unit_counts_values_and_digit_links": "PASS", "selected_original_crc_and_git_blob_hashes": "PASS",
               "visual_svg_review": "Main task to inspect preview/final reader; browser connection unavailable in asset subtask."}}
    encoded = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    target = OUT / "manifest.json"
    if verify:
        need(target.read_bytes() == encoded, "Asset manifest differs from current source/generator")
    else:
        target.write_bytes(encoded)
        sections = []
        for record in records:
            original = "original/" + Path(record["original_path"]).name
            localized = Path(record["localized_path"]).name
            sections.append(f'<section><h2>{record["media_id"]}</h2><p>Unchanged English original</p>'
                            f'<img class="original" src="{original}" alt="Canonical English source diagram">'
                            f'<p>New Telugu code-native redraw</p><img src="{localized}" alt="Telugu redraw for visual QA"></section>')
        preview = ('<!doctype html><html lang="te"><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
                   '<title>TE-B002 diagram QA</title><style>body{font-family:"Nirmala UI",sans-serif;color:#153a4b;background:#edf2f4;margin:0;padding:24px}'
                   'main{max-width:1040px;margin:auto}section{background:white;padding:20px;margin:24px 0;border:1px solid #cbd9de;break-inside:avoid}'
                   'img{display:block;max-width:100%;height:auto}img.original{max-width:min(100%,600px)}h1{font-size:26px}h2{font-size:18px}</style>'
                   '<main><h1>TE-B002: original and localized diagrams</h1><p>Local QA preview; originals unchanged. Not a native-speaker approval.</p>'
                   + ''.join(sections) + '</main></html>\n')
        (OUT / "preview.html").write_text(preview, encoding="utf-8")
    print(json.dumps({"status": "PASS", **manifest["qa"]}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--originals-only", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    need(sum((args.verify, args.originals_only, args.self_test)) <= 1, "Choose at most one operation")
    if args.self_test:
        self_test()
    else:
        build(args.verify, args.originals_only)
