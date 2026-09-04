"""Preserve three pinned JPEGs and draw TE-B004 number-naming diagrams.
Only selected ZIP members are read/extracted. --verify and --self-test are read-only.
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
OUT = BASE / "assets/B004"
SOURCE = BASE / "sources/TE-B004.en.cnxml"
COMMIT = "38cae454e644abf9f0a623e876994553881597c9"
ARCHIVE_SHA = "effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917"
SOURCE_SHA = "b4f0a1d73243b8f923cb2ee15842b21235c24608c732b00929435ce8c9e55545"
PREFIX = "osbooks-prealgebra-bundle-" + COMMIT + "/"
CN = "{http://cnx.rice.edu/cnxml}"
SVG = "{http://www.w3.org/2000/svg}"
ET.register_namespace("", SVG[1:-1])
NAMES = {n: f"CNX_BMath_Figure_01_01_{n:03}_img.jpg" for n in (13,14,15)}
INK, ACCENT, MUTED = "#153a4b", "#006b67", "#426271"
LEFT, CELL = 40, 400
SPECS = {
    13: {"number": "37,519,248", "groups": ["37", "519", "248"], "powers": [6,3,0],
        "periods": [("మిలియన్లు", "millions"), ("వేలు", "thousands"), ("ఒకట్లు", "ones")],
        "english": [("Thirty-seven million",), ("Five hundred nineteen", "thousand"), ("Two hundred forty-eight",)],
        "telugu": [("ముప్పై ఏడు మిలియన్లు",), ("ఐదు వందల", "పందొమ్మిది వేలు"), ("రెండు వందల", "నలభై ఎనిమిది")]},
    14: {"number": "8,165,432,098,710", "groups": ["8", "165", "432", "098", "710"], "powers": [12,9,6,3,0],
        "periods": [("ట్రిలియన్లు", "trillions"), ("బిలియన్లు", "billions"), ("మిలియన్లు", "millions"), ("వేలు", "thousands"), ("ఒకట్లు", "ones")],
        "english": [("Eight trillion,",), ("One hundred sixty-five", "billion,"), ("Four hundred thirty-two", "million,"), ("Ninety-eight thousand,",), ("Seven hundred ten",)],
        "telugu": [("ఎనిమిది ట్రిలియన్లు",), ("నూట అరవై ఐదు", "బిలియన్లు"), ("నాలుగు వందల", "ముప్పై రెండు మిలియన్లు"), ("తొంభై ఎనిమిది వేలు",), ("ఏడు వందల పది",)]},
    15: {"number": "327,577,529", "groups": ["327", "577", "529"], "powers": [6,3,0],
        "periods": [("మిలియన్లు", "millions"), ("వేలు", "thousands"), ("ఒకట్లు", "ones")]},
}

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
    metadata = json.loads((BASE / "sources/TE-B004.source.json").read_text(encoding="utf-8"))
    need(metadata["unit"] == "TE-B004" and metadata["source_sha256"] == SOURCE_SHA
         and metadata["source_commit"] == COMMIT, "Unpinned source metadata")
    source = ET.parse(SOURCE).getroot()
    need(source.get("id") == "fs-id1321580", "Wrong subsection")
    parents = {c: p for p in source.iter() for c in p}
    images = list(source.iter(CN + "image"))
    wanted = {"../../media/" + name for name in NAMES.values()}
    need(len(images) == 3 and {im.get("src") for im in images} == wanted, "Wrong selected image set")
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
            need(total < 6_000_000, "Selected originals exceed bounded output")
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
                "localized_path": f"assets/B004/CNX_BMath_Figure_01_01_{number:03}.te.svg"})
    return records, total


def node(parent, tag, attrs=None, text=None):
    child = ET.SubElement(parent, SVG + tag, {str(k): str(v) for k, v in (attrs or {}).items()})
    child.text = text
    return child


def label(parent, x, y, value, size=24, color=INK, anchor="middle", **attrs):
    return node(parent, "text", {"x": x, "y": y, "font-size": size, "fill": color,
        "text-anchor": anchor, **attrs}, value)


def dimensions(number):
    return LEFT * 2 + len(SPECS[number]["groups"]) * CELL, 660 if number != 15 else 300


def diagram(number):
    spec = SPECS[number]
    width, height = dimensions(number)
    names = number != 15
    root = ET.Element(SVG + "svg", {"width": str(width), "height": str(height),
        "viewBox": f"0 0 {width} {height}", "role": "img", "aria-labelledby": "title desc",
        "lang": "te", "font-family": "Nirmala UI, Noto Sans Telugu, sans-serif",
        "data-number": spec["number"], "data-period-count": len(spec["groups"]).__str__()})
    node(root, "title", {"id": "title"}, "మూడంకెల సమూహాలు / Three-digit periods: " + spec["number"])
    description = []
    for i, (digits, (te, en)) in enumerate(zip(spec["groups"], spec["periods"])):
        text = f"{digits}: {te} ({en})"
        if names:
            text += "; English: " + " ".join(spec["english"][i]) + "; తెలుగు అర్థం: " + " ".join(spec["telugu"][i])
        description.append(text)
    node(root, "desc", {"id": "desc"}, "; ".join(description) +
        ". International grouping preserved. " +
        ("One arrow connects each digit group with its English number-name chunk and separate Telugu gloss. English named scales use singular words; this is not a Telugu suffix-removal rule. " if names else "Only the period labels are shown, as in the source; no number-name answer is added. ") +
        "Million/billion/trillion Telugu loanwords are editorial. New code-native redraw; original JPEG unchanged.")
    node(root, "rect", {"width": width, "height": height, "fill": "white"})
    label(root, LEFT, 42, "మూడంకెల సమూహాలు / periods", 28, anchor="start")
    label(root, width - LEFT, 42, spec["number"], 28, anchor="end", **{"data-role": "number-caption"})
    if names:
        defs = node(root, "defs")
        marker = node(defs, "marker", {"id": "arrowhead", "viewBox": "0 0 10 10", "refX": 8,
            "refY": 5, "markerWidth": 7, "markerHeight": 7, "orient": "auto-start-reverse"})
        node(marker, "path", {"d": "M0 0L10 5L0 10Z", "fill": ACCENT})
    for i, (digits, (te, en), power) in enumerate(zip(spec["groups"], spec["periods"], spec["powers"])):
        x, center = LEFT + CELL * i, LEFT + CELL * (i + 0.5)
        group = node(root, "g", {"id": f"period-{i}", "data-role": "period",
            "data-index": i, "data-digits": digits, "data-power": power})
        node(group, "rect", {"x": x + 8, "y": 65, "width": CELL - 16, "height": 170,
            "rx": 10, "fill": "#eef8f5", "stroke": "#b5d8d2"})
        label(group, center, 112, digits, 40, **{"data-role": "period-digits"})
        node(group, "path", {"d": f"M{center-62} 122V133Q{center-62} 141 {center-54} 141H{center-8}L{center} 148L{center+8} 141H{center+54}Q{center+62} 141 {center+62} 133V122",
            "fill": "none", "stroke": ACCENT, "stroke-width": 2, "data-role": "period-bracket"})
        label(group, center, 182, te, 26, ACCENT, **{"data-role": "period-name-te"})
        label(group, center, 216, en, 22, ACCENT, **{"lang": "en", "data-role": "period-name-en"})
        if i < len(spec["groups"]) - 1:
            label(root, x + CELL, 112, ",", 38, **{"data-role": "number-comma", "data-after": i})
        if names:
            output = node(root, "g", {"id": f"name-{i}", "data-role": "name-chunk", "data-index": i})
            node(output, "rect", {"x": x + 8, "y": 300, "width": CELL - 16, "height": 286,
                "rx": 10, "fill": "#fffaf0", "stroke": "#dbcaa4"})
            label(output, center, 330, "English", 18, MUTED, **{"lang": "en", "data-role": "english-caption"})
            for row, line in enumerate(spec["english"][i]):
                label(output, center, 365 + row * 32, line, 23, **{"lang": "en", "data-role": "english-name"})
            label(output, center, 442, "తెలుగు అర్థం / gloss", 19, MUTED, **{"data-role": "gloss-caption"})
            for row, line in enumerate(spec["telugu"][i]):
                label(output, center, 482 + row * 37, line, 26, **{"data-role": "telugu-gloss"})
            node(root, "path", {"d": f"M{center} 247V282", "fill": "none", "stroke": ACCENT,
                "stroke-width": 3, "marker-end": "url(#arrowhead)", "data-role": "name-arrow",
                "data-from": f"period-{i}", "data-to": f"name-{i}"})
    footer = "English పేర్లు; వేరుగా తెలుగు అర్థాలు / English names with separate Telugu glosses" if names else "మిలియన్లు - వేలు - ఒకట్లు / millions - thousands - ones"
    label(root, LEFT, height - 25, footer, 23, MUTED, anchor="start")
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"


def english_value(phrase):
    """Independent arithmetic check of the actual visible English name chunk."""
    small = dict(zip("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split(), range(20)))
    tens = dict(zip("twenty thirty forty fifty sixty seventy eighty ninety".split(), range(20, 100, 10)))
    scales = {"thousand": 1000, "million": 10**6, "billion": 10**9, "trillion": 10**12}
    words = phrase.lower().strip().rstrip(",").replace("-", " ").split()
    scale = scales.pop(words[-1], 1) if words[-1] in scales else 1
    if scale != 1:
        words = words[:-1]
    value = 0
    for word in words:
        if word in small:
            value += small[word]
        elif word in tens:
            value += tens[word]
        elif word == "hundred":
            need(0 < value < 10, "Invalid hundred coefficient")
            value *= 100
        else:
            raise ValueError("Unexpected English number token: " + word)
    need(0 <= value < 1000, "Named period exceeds three digits")
    return value * scale


def math_check(number, payload):
    spec = SPECS[number]
    width, height = dimensions(number)
    root = ET.fromstring(payload)
    need(root.tag == SVG + "svg" and root.get("viewBox") == f"0 0 {width} {height}", "Wrong SVG canvas")
    need(not list(root.iter(SVG + "image")) and not list(root.iter(SVG + "script")), "Must be code-native/static")
    need(root.get("role") == "img" and root.get("aria-labelledby") == "title desc", "Missing accessible name")
    need(root.find(SVG + "title") is not None and root.find(SVG + "desc") is not None, "Missing SVG description")
    need(root.get("data-number") == spec["number"], "Incorrect number")
    groups = [e for e in root.iter(SVG + "g") if e.get("data-role") == "period"]
    need(len(groups) == len(spec["groups"]), "Wrong period count")
    value = 0
    for i, (group, digits, power, names) in enumerate(zip(groups, spec["groups"], spec["powers"], spec["periods"])):
        need(group.get("id") == f"period-{i}" and group.get("data-index") == str(i), "Wrong period order")
        need(group.get("data-digits") == digits and group.get("data-power") == str(power), "Digit group or power changed")
        need([e.text for e in group if e.get("data-role") == "period-digits"] == [digits], "Visible digit group changed")
        need([e.text for e in group if e.get("data-role") == "period-name-te"] == [names[0]], "Telugu period label changed")
        need([e.text for e in group if e.get("data-role") == "period-name-en"] == [names[1]], "English period label changed")
        value += int(digits) * 10**power
    need(",".join(spec["groups"]) == spec["number"], "Source comma groups differ")
    need(value == int(spec["number"].replace(",", "")), "Positional sum wrong")
    commas = [e for e in root.iter(SVG + "text") if e.get("data-role") == "number-comma"]
    need([e.get("data-after") for e in commas] == [str(i) for i in range(len(groups)-1)] and all(e.text == "," for e in commas), "Visible number comma missing")
    chunks = [e for e in root.iter(SVG + "g") if e.get("data-role") == "name-chunk"]
    arrows = [e for e in root.iter(SVG + "path") if e.get("data-role") == "name-arrow"]
    if number == 15:
        need(not chunks and not arrows, "Source period-only figure gained name answers")
    else:
        need(len(chunks) == len(arrows) == len(groups), "Missing name or arrow")
        named = 0
        for i, (chunk, arrow) in enumerate(zip(chunks, arrows)):
            need(chunk.get("id") == f"name-{i}" and chunk.get("data-index") == str(i), "Name order changed")
            english = [e.text for e in chunk if e.get("data-role") == "english-name"]
            telugu = [e.text for e in chunk if e.get("data-role") == "telugu-gloss"]
            need(english == list(spec["english"][i]) and telugu == list(spec["telugu"][i]), "Visible name/gloss changed")
            actual = english_value(" ".join(english))
            need(actual == int(spec["groups"][i]) * 10**spec["powers"][i], "English name value mismatches period")
            named += actual
            need(arrow.get("data-from") == f"period-{i}" and arrow.get("data-to") == f"name-{i}", "Arrow links wrong name")
            center = LEFT + CELL * (i + .5)
            need(arrow.get("d") == f"M{center} 247V282" and arrow.get("marker-end") == "url(#arrowhead)", "Arrow geometry changed")
        need(named == value, "Named chunks do not sum to source number")
    for rect in root.iter(SVG + "rect"):
        x, y = float(rect.get("x", 0)), float(rect.get("y", 0))
        need(x >= 0 and y >= 0 and x + float(rect.get("width")) <= width
             and y + float(rect.get("height")) <= height, "Rectangle outside canvas")
    return {"source_digit_groups": spec["groups"], "period_powers": spec["powers"],
        "value": value, "source_commas_preserved": True, "name_arrows": len(arrows),
        "english_name_arithmetic": "PASS" if number != 15 else "not_applicable_source_has_periods_only",
        "telugu_glosses_separate_from_english_rules": True}


def self_test():
    rejected = 0
    for number in SPECS:
        payload = diagram(number)
        math_check(number, payload)
        for case in range(5):
            root = ET.fromstring(payload)
            groups = [e for e in root.iter(SVG + "g") if e.get("data-role") == "period"]
            if case == 0:
                next(e for e in groups[-1] if e.get("data-role") == "period-digits").text = "000"
            elif case == 1:
                groups[0].set("data-power", "3")
            elif case == 2:
                next(e for e in groups[0] if e.get("data-role") == "period-name-en").text = "lakhs"
            elif case == 3:
                victim = next(e for e in root if e.get("data-role") == "number-comma")
                root.remove(victim)
            elif number == 15:
                node(root, "g", {"data-role": "name-chunk"})
            else:
                next(e for e in root.iter(SVG + "path") if e.get("data-role") == "name-arrow").set("data-to", "name-1")
            try:
                math_check(number, ET.tostring(root))
            except ValueError:
                rejected += 1
            else:
                raise AssertionError(f"Accepted corrupt fixture{case} for{number}")
    # Naming-specific negatives, including a source-internal leading zero.
    for number, role, wrong in [(14, "period-digits", "98"), (13, "english-name", "Thirty-six million")]:
        root = ET.fromstring(diagram(number))
        target = next(e for e in root.iter(SVG + "text") if e.get("data-role") == role and (number != 14 or e.text == "098"))
        target.text = wrong
        try:
            math_check(number, ET.tostring(root))
        except ValueError:
            rejected += 1
        else:
            raise AssertionError("Accepted naming-specific corruption")
    need(english_value("Ninety-eight thousand,") == 98000, "Independent English name arithmetic failed")
    need(english_value("One hundred sixty-five billion,") == 165000000000, "Independent scale arithmetic failed")
    print(f"PASS: three diagrams, source grouping and named-value arithmetic; {rejected} corruption fixtures rejected; no writes")


def build(verify=False, originals_only=False):
    records, size = source_assets(write_originals=not verify)
    if originals_only:
        print(json.dumps({"originals": records, "bytes": size, "archive_sha256_crc_git_blobs": "PASS"}, ensure_ascii=False))
        return
    for record in records:
        number = record.pop("number")
        payload = diagram(number)
        record.update(math_checks=math_check(number, payload), localized_sha256=digest(payload),
            localized_bytes=len(payload), recommended_min_width_px=dimensions(number)[0],
            disclosure="New code-native redraw; source JPEG unchanged. English number-name chunks retained with explicitly separate editorial Telugu glosses where the source names numbers.")
        target = BASE / record["localized_path"]
        if verify:
            need(target.read_bytes() == payload, "SVG differs from deterministic generator")
            math_check(number, target.read_bytes())
        else:
            target.write_bytes(payload)
    manifest = {"schema": "te-b002-assets-v1", "unit": "TE-B004", "source_subsection_id": "fs-id1321580",
        "source_subsection_sha256": SOURCE_SHA, "canonical_commit": COMMIT,
        "canonical_archive_sha256": ARCHIVE_SHA,
        "source_attribution": "OpenStax, Prealgebra 2e; existing project notices and source attribution remain applicable.",
        "generator": "scripts/make_b004_assets.py", "verification_command": "python -B te-Telu-IN/scripts/make_b004_assets.py --verify",
        "scope": "Exactly three selected unchanged JPEGs and three new SVGs; no downloads or bulk extraction.",
        "canon_consulted": ["C18", "C20"],
        "choices": ["Preserve three-digit international groups, including literal098; no lakh/crore substitution.",
            "Keep exact visible English source name words and punctuation; final-s and omitted-and conventions are English-only.",
            "Telugu standalone glosses coordinated with B004 translator; running prose may use connective scale forms, not a suffix-removal rule.",
            "Preserve3 and5 digit-to-name arrows in013/014;015 remains period-label-only without new number-name answers.",
            "Use own bilingual headings, vertical arrow layout and separately labeled Telugu glosses; original JPEGs remain byte-exact.",
            "Original014 sourcealt has bilions, but inspected JPEG correctly reads billions; no typo propagated to new bilingual labels.",
            "Million/billion/trillion Telugu labels are editorial; AP and official regional loanword attestations remain unverified.",
            "Reader should use recommended_min_width_px and a focusable local-panning wrapper; main-task final reader inspection pending."],
        "assets": records,
        "qa": {"selected_original_count": 3, "original_bytes": size, "localized_svg_count": 3,
            "localized_bytes": sum(r["localized_bytes"] for r in records),
            "all_unit_counts_values_and_digit_links": "PASS", "selected_original_crc_and_git_blob_hashes": "PASS",
            "visual_svg_review": "Pending main-task rendered-reader inspection; three source JPEGs viewed before authoring."}}
    encoded = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    if verify:
        need((OUT / "manifest.json").read_bytes() == encoded, "Manifest differs from source/generator")
    else:
        (OUT / "manifest.json").write_bytes(encoded)
        sections = []
        for record in records:
            sections.append(f'<section><h2>{record["media_id"]}</h2><p>Unchanged source</p><img class="original" src="original/{Path(record["original_path"]).name}" alt="Canonical original number-naming figure"><p>New bilingual redraw; scroll to inspect every group.</p>'
                f'<div class="pan" tabindex="0"><img style="width:{record["recommended_min_width_px"]}px" src="{Path(record["localized_path"]).name}" alt="Bilingual grouping and naming diagram"></div></section>')
        preview = '<!doctype html><html lang="te"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>B004 diagram QA</title><style>body{font-family:"Nirmala UI",sans-serif;color:#153a4b;background:#edf4f3;margin:24px}main{max-width:1100px;margin:auto}section{background:white;padding:20px;margin:24px 0}.original{max-width:100%;height:auto}.pan{max-width:100%;overflow-x:auto;border:1px solid #9bc9c0}.pan img{display:block;max-width:none;height:auto}</style><main><h1>B004 source and localized diagrams</h1>' + ''.join(sections) + '</main></html>\n'
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
