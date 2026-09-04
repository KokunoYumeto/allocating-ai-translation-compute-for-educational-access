"""Preserve selected TE-B005 source JPEGs and generate code-native SVGs.

No downloads or bulk extraction. Verification and corruption tests are read-only.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parent
OUT = BASE / "assets/B005"
SOURCE = BASE / "sources/TE-B005.en.cnxml"
SOURCE_SHA = "49c4b683bd9ed3d0bb8b797a302760b512a286d78f7eaa7855c420077a136f31"
COMMIT = "38cae454e644abf9f0a623e876994553881597c9"
ARCHIVE_SHA = "effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917"
PREFIX = "osbooks-prealgebra-bundle-" + COMMIT + "/"
CN = "{http://cnx.rice.edu/cnxml}"
SVG = "{http://www.w3.org/2000/svg}"
NAMES = {n: f"CNX_BMath_Figure_01_01_{n:03}_img.jpg" for n in (16, 17, 18)}
ET.register_namespace("", SVG[1:-1])
INK, ACCENT, MUTED = "#153a4b", "#006b67", "#426271"
LEFT, CELL, HEIGHT = 40, 400, 660
SPECS = {
    16: {"number": "53,401,742", "groups": ["53", "401", "742"], "powers": [6, 3, 0],
        "periods": [("మిలియన్లు", "millions"), ("వేలు", "thousands"), ("ఒకట్లు", "ones")],
        "english": [("fifty-three million",), ("four hundred one", "thousand"), ("seven hundred forty-two",)],
        "telugu": [("యాభై మూడు మిలియన్లు",), ("నాలుగు వందల ఒక వేలు",), ("ఏడు వందల", "నలభై రెండు")]},
    17: {"number": "9,246,073,189", "groups": ["9", "246", "073", "189"], "powers": [9, 6, 3, 0],
        "periods": [("బిలియన్లు", "billions"), ("మిలియన్లు", "millions"), ("వేలు", "thousands"), ("ఒకట్లు", "ones")],
        "english": [("nine billion",), ("two hundred forty-six", "million"), ("seventy-three thousand",), ("one hundred eighty-nine",)],
        "telugu": [("తొమ్మిది బిలియన్లు",), ("రెండు వందల", "నలభై ఆరు మిలియన్లు"), ("డెబ్బై మూడు వేలు",), ("నూట ఎనభై తొమ్మిది",)]},
    18: {"number": "77,000,000,000", "groups": ["77", "000", "000", "000"], "powers": [9, 6, 3, 0],
        "periods": [("బిలియన్లు", "billions"), ("మిలియన్లు", "millions"), ("వేలు", "thousands"), ("ఒకట్లు", "ones")],
        "english": [("77 billion",), (), (), ()],
        "telugu": [("డెబ్బై ఏడు బిలియన్లు",), (), (), ()]},
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
    need(file_digest(SOURCE) == SOURCE_SHA, "Frozen B005 subsection changed")
    metadata = json.loads((BASE / "sources/TE-B005.source.json").read_text("utf-8"))
    need(metadata["unit"] == "TE-B005" and metadata["source_sha256"] == SOURCE_SHA
         and metadata["source_commit"] == COMMIT, "Unpinned source metadata")
    source = ET.parse(SOURCE).getroot()
    need(source.get("id") == "fs-id1339359", "Wrong subsection")
    source_text = " ".join(source.itertext())
    for spec in SPECS.values():
        need(spec["number"] in source_text, "Expected example number absent from source")
    parents = {child: parent for parent in source.iter() for child in parent}
    images = list(source.iter(CN + "image"))
    need(len(images) == 3 and {im.get("src") for im in images} ==
         {"../../media/" + name for name in NAMES.values()}, "Wrong selected image set")
    lock = json.loads((BASE / "sources.lock.json").read_text("utf-8"))
    archive = next(r for r in lock["canonical_archives"] if r["id"] == "A00-A20-en-complete-archive")
    need(archive["sha256"] == ARCHIVE_SHA and archive["commit"] == COMMIT, "Unpinned archive")
    path = ROOT / archive["path"]
    need(path.stat().st_size == archive["bytes"] and file_digest(path) == ARCHIVE_SHA,
         "Canonical archive size/SHA mismatch")
    selected = ["media/" + Path(im.get("src")).name for im in images]
    env = os.environ.copy()
    env.update(GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
    tree = subprocess.check_output(["git", "-C", str(ROOT / "downloads/upstream-prealgebra"),
        "ls-tree", "-r", "-z", COMMIT, "--", *selected], env=env)
    blobs = {}
    for row in tree.split(b"\0"):
        if row:
            header, name = row.split(b"\t", 1)
            _, kind, oid = header.split()
            need(kind == b"blob", "Selected member is not a Git blob")
            blobs[name.decode()] = oid.decode()
    need(set(blobs) == set(selected), "Pinned selected blobs missing")
    if write_originals:
        need(shutil.disk_usage(BASE).free >= 32 * 1024 * 1024, "Insufficient free space")
    records, total = [], 0
    with zipfile.ZipFile(path) as package:
        need(package.comment.decode() == COMMIT, "ZIP comment is not the pinned commit")
        for image, name in zip(images, selected):
            member = PREFIX + name
            info = package.getinfo(member)
            need(0 < info.file_size < 2_000_000, "Selected image exceeds small-file bound")
            payload = package.read(member)  # CRC checked for this member only.
            total += len(payload)
            need(total < 6_000_000, "Selected originals exceed bounded output")
            blob = hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()
            need(blob == blobs[name], "Original differs from pinned Git blob")
            target = OUT / "original" / Path(name).name
            if target.exists():
                need(target.read_bytes() == payload, "Preserved original changed; refusing overwrite")
            elif write_originals:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(payload)
            else:
                raise FileNotFoundError("Missing preserved original: " + str(target))
            media = parents[image]
            parent = parents.get(media)
            number = next(k for k, value in NAMES.items() if value == Path(name).name)
            records.append({"number": number, "original_src": image.get("src"),
                "original_path": target.relative_to(BASE).as_posix(),
                "original_sha256": digest(payload), "original_bytes": len(payload),
                "source_git_blob_sha1": blob, "source_zip_member": member,
                "source_zip_crc32": f"{info.CRC:08x}", "media_id": media.get("id"),
                "figure_id": parent.get("id") if parent is not None and parent.tag == CN + "figure" else None,
                "localized_path": f"assets/B005/CNX_BMath_Figure_01_01_{number:03}.te.svg"})
    return records, total


def node(parent, tag, attrs=None, text=None):
    child = ET.SubElement(parent, SVG + tag, {str(k): str(v) for k, v in (attrs or {}).items()})
    child.text = text
    return child


def label(parent, x, y, value, size=24, color=INK, anchor="middle", **attrs):
    return node(parent, "text", {"x": x, "y": y, "font-size": size, "fill": color,
        "text-anchor": anchor, **attrs}, value)


def dimensions(number):
    return LEFT * 2 + len(SPECS[number]["groups"]) * CELL, HEIGHT


def diagram(number):
    spec = SPECS[number]
    width, height = dimensions(number)
    root = ET.Element(SVG + "svg", {"width": str(width), "height": str(height),
        "viewBox": f"0 0 {width} {height}", "role": "img", "aria-labelledby": "title desc",
        "lang": "te", "font-family": "Nirmala UI, Noto Sans Telugu, sans-serif",
        "data-number": spec["number"], "data-period-count": str(len(spec["groups"]))})
    node(root, "title", {"id": "title"}, "పేర్ల నుంచి అంకెలకు / Words to digits: " + spec["number"])
    parts = []
    for i, (digits, (te, en)) in enumerate(zip(spec["groups"], spec["periods"])):
        english = " ".join(spec["english"][i])
        gloss = " ".join(spec["telugu"][i])
        parts.append(f"{te} ({en}): " +
            (f"English {english}; తెలుగు అర్థం {gloss}; " if english else "No source name is given; ") +
            f"downward arrow to {digits} in three digit positions")
    node(root, "desc", {"id": "desc"}, "; ".join(parts) +
        ". Empty leading positions in the first period stay blank, not zero. Later periods keep all three digits, including zeros. " +
        "English source phrases are preserved; Telugu glosses are separate editorial wording, not an English suffix rule. " +
        ("Source017 alt text erroneously says742; inspected original JPEG and source answer show073. " if number == 17 else "") +
        "New code-native redraw; original JPEG unchanged. International comma grouping retained.")
    node(root, "rect", {"width": width, "height": height, "fill": "white"})
    label(root, LEFT, 42, "పేర్ల నుంచి అంకెలకు / words → digits", 26, anchor="start")
    label(root, width - LEFT, 42, spec["number"], 27, anchor="end", **{"data-role": "number-caption"})
    defs = node(root, "defs")
    marker = node(defs, "marker", {"id": "arrowhead", "viewBox": "0 0 10 10", "refX": 8,
        "refY": 5, "markerWidth": 7, "markerHeight": 7, "orient": "auto-start-reverse"})
    node(marker, "path", {"d": "M0 0L10 5L0 10Z", "fill": ACCENT})
    for i, (digits, power, (te, en)) in enumerate(zip(spec["groups"], spec["powers"], spec["periods"])):
        x, center = LEFT + CELL * i, LEFT + CELL * i + CELL // 2
        group = node(root, "g", {"id": f"period-{i}", "data-role": "period", "data-index": i,
            "data-digits": digits, "data-power": power})
        node(group, "rect", {"x": x + 8, "y": 65, "width": CELL - 16, "height": 300,
            "rx": 10, "fill": "#eef8f5", "stroke": "#b5d8d2"})
        label(group, center, 102, te, 26, ACCENT, **{"data-role": "period-name-te"})
        label(group, center, 134, en, 22, ACCENT, **{"lang": "en", "data-role": "period-name-en"})
        if spec["english"][i]:
            label(group, center, 176, "English", 18, MUTED, **{"lang": "en", "data-role": "english-caption"})
            for row, line in enumerate(spec["english"][i]):
                label(group, center, 212 + row * 31, line, 23, **{"lang": "en", "data-role": "english-name"})
            label(group, center, 280, "తెలుగు అర్థం / gloss", 18, MUTED, **{"data-role": "gloss-caption"})
            for row, line in enumerate(spec["telugu"][i]):
                label(group, center, 316 + row * 34, line, 25, **{"data-role": "telugu-gloss"})
        output = node(root, "g", {"id": f"digits-{i}", "data-role": "digit-output", "data-index": i})
        node(output, "rect", {"x": x + 8, "y": 440, "width": CELL - 16, "height": 135,
            "rx": 10, "fill": "#fffaf0", "stroke": "#dbcaa4"})
        padded = digits.rjust(3)
        for pos, digit in enumerate(padded):
            at = center + (pos - 1) * 50
            label(output, at, 501, digit.strip(), 38,
                **{"data-role": "digit", "data-slot": pos})
            node(output, "line", {"x1": at - 18, "x2": at + 18, "y1": 516, "y2": 516,
                "stroke": INK, "stroke-width": 2, "data-role": "digit-slot", "data-slot": pos})
        label(output, center, 552, "అంకెలకు స్థానాలు / digit places", 20, MUTED)
        node(root, "path", {"d": f"M{center} 382V422", "fill": "none", "stroke": ACCENT,
            "stroke-width": 3, "marker-end": "url(#arrowhead)", "data-role": "name-to-digits-arrow",
            "data-from": f"period-{i}", "data-to": f"digits-{i}"})
        if i < len(spec["groups"]) - 1:
            label(root, x + CELL, 501, ",", 34, **{"data-role": "number-comma", "data-after": i})
            if number != 18:
                label(root, x + CELL, 212, ",", 30, **{"data-role": "phrase-comma", "data-after": i})
    footer = ("పేరు ఇవ్వని సమూహాల్లో 000 / unnamed periods → 000" if number == 18 else
              "English పేర్లు; వేరుగా తెలుగు అర్థాలు / English names with separate Telugu glosses")
    label(root, LEFT, height - 25, footer, 22, MUTED, anchor="start")
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"


def english_value(phrase):
    """Interpret actual displayed source name chunks, independently of digit specs."""
    small = dict(zip("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split(), range(20)))
    tens = dict(zip("twenty thirty forty fifty sixty seventy eighty ninety".split(), range(20, 100, 10)))
    scales = {"thousand": 1000, "million": 10**6, "billion": 10**9, "trillion": 10**12}
    words = phrase.lower().replace("-", " ").split()
    if not words:
        return 0
    scale = scales.get(words[-1], 1)
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
        elif word.isascii() and word.isdigit():
            need(len(words) == 1, "Mixed numeral/word coefficient")
            value = int(word)
        else:
            raise ValueError("Unexpected English number token: " + word)
    need(0 <= value < 1000, "Named period coefficient exceeds three digits")
    return value * scale


def math_check(number, payload):
    spec = SPECS[number]
    width, height = dimensions(number)
    root = ET.fromstring(payload)
    need(root.tag == SVG + "svg" and root.get("viewBox") == f"0 0 {width} {height}", "Wrong SVG canvas")
    need(not list(root.iter(SVG + "image")) and not list(root.iter(SVG + "script")), "Must be code-native/static")
    need(root.get("role") == "img" and root.get("aria-labelledby") == "title desc", "Missing accessible SVG name")
    need(root.find(SVG + "title") is not None and root.find(SVG + "desc") is not None, "Missing SVG description")
    need(root.get("data-number") == spec["number"], "Wrong number metadata")
    need([e.text for e in root if e.get("data-role") == "number-caption"] == [spec["number"]], "Wrong visible number caption")
    groups = [e for e in root if e.get("data-role") == "period"]
    outputs = [e for e in root if e.get("data-role") == "digit-output"]
    arrows = [e for e in root if e.get("data-role") == "name-to-digits-arrow"]
    count = len(spec["groups"])
    need(len(groups) == len(outputs) == len(arrows) == count, "Missing period/output/arrow")
    positional, named = 0, 0
    for i, (group, output, arrow, digits, power, names) in enumerate(zip(groups, outputs, arrows,
            spec["groups"], spec["powers"], spec["periods"])):
        need(group.get("id") == f"period-{i}" and group.get("data-index") == str(i), "Period order changed")
        need(group.get("data-digits") == digits and group.get("data-power") == str(power), "Digit group/power changed")
        need([e.text for e in group if e.get("data-role") == "period-name-te"] == [names[0]], "Telugu period changed")
        need([e.text for e in group if e.get("data-role") == "period-name-en"] == [names[1]], "English period changed")
        english = [e.text for e in group if e.get("data-role") == "english-name"]
        telugu = [e.text for e in group if e.get("data-role") == "telugu-gloss"]
        need(english == list(spec["english"][i]) and telugu == list(spec["telugu"][i]), "Visible English name/Telugu gloss changed")
        actual = english_value(" ".join(english))
        need(actual == int(digits) * 10**power, "Visible name does not match positional value")
        named += actual
        positional += int(digits) * 10**power
        need(output.get("id") == f"digits-{i}" and output.get("data-index") == str(i), "Output order changed")
        digit_nodes = [e for e in output if e.get("data-role") == "digit"]
        need([e.get("data-slot") for e in digit_nodes] == ["0", "1", "2"], "Missing/reordered digit position")
        need([(e.text or "") for e in digit_nodes] == [d.strip() for d in digits.rjust(3)], "Visible digits or leading blank changed")
        slots = [e for e in output if e.get("data-role") == "digit-slot"]
        need([e.get("data-slot") for e in slots] == ["0", "1", "2"], "Missing digit underline")
        center = LEFT + CELL * i + CELL // 2
        for pos, (digit_node, slot) in enumerate(zip(digit_nodes, slots)):
            at = center + (pos - 1) * 50
            need(digit_node.get("x") == str(at) and digit_node.get("y") == "501", "Digit geometry changed")
            need(slot.get("x1") == str(at-18) and slot.get("x2") == str(at+18)
                 and slot.get("y1") == slot.get("y2") == "516", "Digit underline geometry changed")
        need(arrow.get("data-from") == f"period-{i}" and arrow.get("data-to") == f"digits-{i}", "Wrong word-to-digit arrow link")
        need(arrow.get("d") == f"M{center} 382V422" and arrow.get("marker-end") == "url(#arrowhead)", "Arrow direction/geometry changed")
    need(named == positional == int(spec["number"].replace(",", "")), "Named/positional totals differ")
    need(",".join(spec["groups"]) == spec["number"], "Source comma grouping differs")
    for role, expected in [("number-comma", count-1), ("phrase-comma", count-1 if number != 18 else 0)]:
        commas = [e for e in root if e.get("data-role") == role]
        need(len(commas) == expected and [e.get("data-after") for e in commas] == [str(i) for i in range(expected)]
             and all(e.text == "," for e in commas), "Comma display changed")
    for rect in root.iter(SVG + "rect"):
        x, y = float(rect.get("x", 0)), float(rect.get("y", 0))
        need(x >= 0 and y >= 0 and x + float(rect.get("width")) <= width
             and y + float(rect.get("height")) <= height, "Rectangle outside canvas")
    return {"source_digit_groups": spec["groups"], "period_powers": spec["powers"],
        "value": positional, "three_digit_slots_per_period": True,
        "initial_unused_slots_remain_blank": True, "source_commas_preserved": True,
        "word_to_digit_arrows": count, "english_name_arithmetic": "PASS",
        "unnamed_periods_stay_unnamed": number == 18,
        "telugu_glosses_separate_from_english_rules": True}


def self_test():
    rejected = 0
    for number in SPECS:
        payload = diagram(number)
        math_check(number, payload)
        for case in range(7):
            root = ET.fromstring(payload)
            if case == 0:
                target = [e for e in root.iter(SVG + "text") if e.get("data-role") == "digit"][-1]
                target.text = "8" if target.text != "8" else "9"
            elif case == 1:
                next(e for e in root if e.get("data-role") == "period").set("data-power", "3")
            elif case == 2:
                next(e for e in root.iter(SVG + "text") if e.get("data-role") == "period-name-en").text = "lakhs"
            elif case == 3:
                root.remove(next(e for e in root if e.get("data-role") == "number-comma"))
            elif case == 4:
                next(e for e in root if e.get("data-role") == "name-to-digits-arrow").set("data-to", "digits-1")
            elif case == 5:
                next(e for e in root if e.get("data-role") == "name-to-digits-arrow").set("d", "M240 422V382")
            elif case == 6:
                next(e for e in root.iter(SVG + "text") if e.get("data-role") == "english-name").text = "one million"
            try:
                math_check(number, ET.tostring(root))
            except ValueError:
                rejected += 1
            else:
                raise AssertionError(f"Accepted corruption{case} for{number}")
    for number, fixture in [(17, "drop-leading-zero"), (18, "invent-unnamed-name"), (16, "leading-blank-to-zero")]:
        root = ET.fromstring(diagram(number))
        if fixture == "drop-leading-zero":
            out = next(e for e in root if e.get("id") == "digits-2")
            next(e for e in out if e.get("data-role") == "digit").text = ""
        elif fixture == "invent-unnamed-name":
            group = next(e for e in root if e.get("id") == "period-1")
            label(group, 0, 0, "zero million", **{"data-role": "english-name"})
        else:
            out = next(e for e in root if e.get("id") == "digits-0")
            next(e for e in out if e.get("data-role") == "digit").text = "0"
        try:
            math_check(number, ET.tostring(root))
        except ValueError:
            rejected += 1
        else:
            raise AssertionError("Accepted " + fixture)
    need(english_value("seventy-three thousand") == 73000, "English73 check failed")
    need(english_value("77 billion") == 77000000000, "Numeric77 check failed")
    print(f"PASS: three diagrams and named/positional values; {rejected} corruption fixtures rejected; no writes")


def build(verify=False, originals_only=False):
    records, size = source_assets(write_originals=not verify)
    if originals_only:
        print(json.dumps({"originals": records, "bytes": size, "archive_sha256_crc_git_blobs": "PASS"}))
        return
    for record in records:
        number = record.pop("number")
        payload = diagram(number)
        record.update(math_checks=math_check(number, payload), localized_sha256=digest(payload),
            localized_bytes=len(payload), recommended_min_width_px=dimensions(number)[0],
            disclosure="New code-native redraw; original JPEG unchanged. Source English words map down to digit positions, with separate editorial Telugu glosses. Leading blank slots and required zero digits remain distinct.")
        target = BASE / record["localized_path"]
        if verify:
            need(target.read_bytes() == payload, "SVG differs from deterministic generator")
            math_check(number, target.read_bytes())
        else:
            target.write_bytes(payload)
    manifest = {"schema": "te-b002-assets-v1", "unit": "TE-B005", "source_subsection_id": "fs-id1339359",
        "source_subsection_sha256": SOURCE_SHA, "canonical_commit": COMMIT,
        "canonical_archive_sha256": ARCHIVE_SHA,
        "source_attribution": "OpenStax, Prealgebra 2e; existing project notices and source attribution remain applicable.",
        "generator": "scripts/make_b005_assets.py",
        "verification_command": "python -B te-Telu-IN/scripts/make_b005_assets.py --verify",
        "scope": "Exactly three selected unchanged JPEGs and three new SVGs; no downloads or bulk extraction.",
        "canon_consulted": ["C11", "C18", "TS6 PDF13/printed3 naming instruction"],
        "choices": [
            "Read complete frozen B005 source, then read only selected016/017/018 JPEGs from the SHA-verified archive; inspected all three originals before drawing.",
            "Retain English source word-to-digit direction, exact phrases and international numeric groups. Telugu standalone glosses coordinated with B005 translator.",
            "Each period has three digit slots. First-period unused positions remain blank;073 and the three000 groups remain exact.",
            "017 original JPEG and canonical numeric answer agree on073; frozen alt text incorrectly says742. New SVG uses073 and records the discrepancy, not a source-image edit.",
            "018 preserves literal77 billion and three unnamed periods; no invented English number-name phrases in those blank groups. Budget currency symbols remain in surrounding source, not invented inside the diagram.",
            "New bilingual cards and annotations separate English names from editorial Telugu glosses. No Telugu suffix-removal or universal omitted-and rule is asserted.",
            "Reread TS6 naming OCR13/16 and TS2 zero-place OCR42; inspected TS2 page42 again. These support words/digits distinction, coefficient-scale syntax and zero position, not official million/billion loanword status.",
            "No lakh/crore replacement; million/billion Telugu labels remain editorial and AP/native-speaker approval remains open.",
            "Reader should honor recommended_min_width_px using a focusable local scroll region; rendered visual QA is separate."
        ],
        "assets": records,
        "qa": {"selected_original_count": 3, "original_bytes": size, "localized_svg_count": 3,
            "localized_bytes": sum(r["localized_bytes"] for r in records),
            "all_unit_counts_values_and_digit_links": "PASS",
            "selected_original_crc_and_git_blob_hashes": "PASS",
            "visual_svg_review": "Pending rendered-reader inspection; all three original JPEGs viewed before authoring."}}
    encoded = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    if verify:
        need((OUT / "manifest.json").read_bytes() == encoded, "Manifest differs from source/generator")
    else:
        (OUT / "manifest.json").write_bytes(encoded)
        sections = []
        for record in records:
            sections.append(f'<section><h2>{record["media_id"]}</h2><p>Unchanged source</p><img class="original" src="original/{Path(record["original_path"]).name}" alt="Canonical original word-to-digit diagram"><p>New bilingual redraw; scroll to inspect every period.</p>'
                f'<div class="pan" tabindex="0" role="region" aria-label="Bilingual diagram; horizontal scrolling"><img style="width:{record["recommended_min_width_px"]}px" src="{Path(record["localized_path"]).name}" alt="Bilingual English-name to digit-position diagram"></div></section>')
        preview = '<!doctype html><html lang="te"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>B005 diagram QA</title><style>body{font-family:"Nirmala UI",sans-serif;color:#153a4b;background:#edf4f3;margin:24px}main{max-width:1100px;margin:auto}section{background:white;padding:20px;margin:24px 0}.original{max-width:100%;height:auto}.pan{max-width:100%;overflow-x:auto;border:1px solid #9bc9c0}.pan img{display:block;max-width:none;height:auto}</style><main><h1>B005 source and localized diagrams</h1>' + ''.join(sections) + '</main></html>\n'
        (OUT / "preview.html").write_text(preview, encoding="utf-8")
    print(json.dumps({"status": "PASS", **manifest["qa"]}))


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
