"""Preserve the exact pinned B019 media and build checked code-native redraws.

No network or bulk extraction is performed. Original rasters are never edited or
overwritten. The first development stage supports ``--originals-only`` so every
selected source image can be inspected before its redraw specification is fixed.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import io
import json
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile

from PIL import Image

from build import atomic_write
from inspect_source import slots, CN


BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parent
OUT = BASE / "assets/B019"
COMMIT = "38cae454e644abf9f0a623e876994553881597c9"
SOURCE_SHA = "5c0d3d631bb07b5f2251bb72018f9f6b9b530f63d9bed26857b7c66ffb335275"
MODULE_SHA = "b32058ce714e5fd43b010ccc81b2ae00a11567b229e9f96dda7b85b3cd82ba6b"
ARCHIVE_SHA = "effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917"
NAMES = [
    "CNX_BMath_Figure_01_02_201_img.jpg",
    "CNX_BMath_Figure_01_02_203_img.jpg",
    "CNX_BMath_Figure_01_02_205_img.jpg",
    "CNX_BMath_Figure_01_02_207_img.jpg",
    "CNX_BMath_Figure_01_02_216.jpg",
    "CNX_BMath_Figure_01_02_217.jpg",
    "CNX_BMath_Figure_01_02_218.jpg",
    "CNX_BMath_Figure_01_02_220.jpg",
    "CNX_BMath_Figure_01_02_221.jpg",
    "CNX_BMath_Figure_01_02_222.jpg",
    "CNX_BMath_Figure_01_02_224.jpg",
    "CNX_BMath_Figure_01_02_225.jpg",
    "CNX_BMath_Figure_01_02_226.jpg",
    "CNX_BMath_Figure_01_02_208_img.jpg",
    "CNX_BMath_Figure_01_02_209_img.jpg",
    "CNX_BMath_Figure_01_02_210_img.jpg",
    "CNX_BMath_Figure_01_02_211_img.jpg",
    "CNX_BMath_Figure_01_02_212_img.jpg",
    "CNX_BMath_Figure_01_02_213_img.jpg",
    "CNX_BMath_Figure_01_02_214_img.jpg",
    "CNX_BMath_Figure_01_02_215_img.jpg",
    "CNX_BMath_Figure_AppB_002_A.jpg",
]
SVG = "{http://www.w3.org/2000/svg}"
INK = "#173b4d"
EDGE = "#287a82"
PALE = "#eef8f8"
HEAD = "#acdadd"
BLOCK = "#c5dce5"
BLOCK_EDGE = "#496f7d"
FONT = "Nirmala UI, Noto Sans Telugu, sans-serif"

# These values were transcribed only after all selected originals were viewed
# at their complete supplied pixel dimensions. They are mathematical redraw
# specifications, not attempts to reproduce decorative raster placement.
MODEL_SPECS = {
    "201_img": {"groups": [("ones", 2), ("ones", 4)], "value": 6, "expression": "2 + 4"},
    "203_img": {"groups": [("tens", 1), ("ones", 2)], "value": 12, "expression": "8 + 4"},
    "205_img": {"groups": [("tens", 8), ("ones", 9)], "value": 89, "expression": "14 + 75"},
    "207_img": {"groups": [("tens", 4), ("ones", 1)], "value": 41, "expression": "16 + 25"},
}

BLANK_216 = {
    (2, 0), (7, 0), (3, 1), (7, 1), (4, 2), (8, 2),
    (0, 3), (3, 3), (4, 3), (6, 3), (9, 3),
    (1, 4), (5, 4), (7, 4), (8, 4),
    (1, 5), (2, 5), (5, 5), (6, 5), (8, 5),
    (3, 6), (4, 6), (6, 6), (7, 6), (9, 6),
    (2, 7), (5, 7), (7, 7), (8, 7), (9, 7),
    (0, 8), (2, 8), (3, 8), (6, 8),
    (1, 9), (4, 9), (5, 9), (8, 9), (9, 9),
}
BLANK_218 = {
    (3, 0), (6, 0), (9, 0), (2, 1), (6, 1), (9, 1),
    (3, 2), (5, 2), (7, 2), (1, 3), (2, 3), (8, 3),
    (3, 4), (4, 4), (6, 4), (7, 4),
    (0, 5), (3, 5), (4, 5), (5, 5), (6, 5), (8, 5), (9, 5),
    (1, 6), (2, 6), (7, 6), (9, 6),
    (0, 7), (3, 7), (7, 7), (8, 7),
    (1, 8), (4, 8), (6, 8), (9, 8),
    (2, 9), (3, 9), (5, 9), (9, 9),
}
TABLE_SPECS = {
    "216": {"rows": list(range(10)), "cols": list(range(10)), "blanks": BLANK_216},
    "217": {"rows": list(range(10)), "cols": list(range(10)), "blanks": set()},
    "218": {"rows": list(range(10)), "cols": list(range(10)), "blanks": BLANK_218},
    "220": {"rows": list(range(6, 10)), "cols": list(range(3, 10)), "blanks": "all"},
    "221": {"rows": list(range(6, 10)), "cols": list(range(3, 10)), "blanks": set()},
    "222": {"rows": list(range(3, 10)), "cols": list(range(6, 10)), "blanks": "all"},
    "224": {"rows": list(range(5, 10)), "cols": list(range(5, 10)), "blanks": "all"},
    "225": {"rows": list(range(5, 10)), "cols": list(range(5, 10)), "blanks": set()},
    "226": {"rows": list(range(6, 10)), "cols": list(range(6, 10)), "blanks": "all"},
}

PERIMETER_SPECS = {
    "208_img": {"unit": "in", "unit_te": "అంగుళాలు", "points": [(110, 300), (360, 70), (610, 300)],
        "edges": [14, 12, 18], "labels": [("14 in", 190, 185), ("12 in", 530, 185), ("18 in", 360, 340)], "answer": 44},
    "209_img": {"unit": "cm", "unit_te": "సెంటీమీటర్లు", "points": [(130, 70), (130, 310), (630, 310)],
        "edges": [5, 12, 13], "labels": [("5 cm", 78, 205), ("13 cm", 450, 175), ("12 cm", 380, 350)], "answer": 30},
    "210_img": {"unit": "m", "unit_te": "మీటర్లు", "points": [(120, 90), (600, 90), (600, 300), (120, 300)],
        "edges": [21, 7, 21, 7], "labels": [("21 m", 360, 70), ("7 m", 645, 205), ("21 m", 360, 340), ("7 m", 75, 205)], "answer": 56},
    "211_img": {"unit": "ft", "unit_te": "అడుగులు", "points": [(140, 70), (580, 70), (580, 320), (140, 320)],
        "edges": [19, 14, 19, 14], "labels": [("19 ft", 360, 50), ("14 ft", 630, 205), ("19 ft", 360, 360), ("14 ft", 85, 205)], "answer": 66},
    "212_img": {"unit": "yd", "unit_te": "గజాలు", "points": [(210, 70), (510, 70), (580, 330), (140, 330)],
        "edges": [19, 18, 16, 18], "labels": [("19 yd", 360, 50), ("18 yd", 630, 195), ("16 yd", 360, 370), ("18 yd", 90, 195)], "answer": 71},
    "213_img": {"unit": "m", "unit_te": "మీటర్లు", "points": [(220, 70), (500, 70), (610, 320), (110, 320)],
        "edges": [24, 17, 29, 17], "labels": [("24 m", 360, 50), ("17 m", 650, 190), ("29 m", 360, 360), ("17 m", 75, 190)], "answer": 87},
    "214_img": {"unit": "ft", "unit_te": "అడుగులు", "points": [(80, 80), (650, 80), (650, 290), (210, 290), (210, 200), (80, 200)],
        "edges": [24, 7, 19, 3, 5, 4], "labels": [("24 ft", 365, 60), ("7 ft", 690, 190), ("19 ft", 430, 330), ("3 ft", 250, 255), ("5 ft", 145, 230), ("4 ft", 45, 145)], "answer": 62},
    "215_img": {"unit": "in", "unit_te": "అంగుళాలు", "points": [(80, 80), (650, 80), (650, 320), (330, 320), (330, 150), (80, 150)],
        "edges": [25, 10, 14, 7, 11, None], "labels": [("25 in", 365, 60), ("10 in", 700, 205), ("14 in", 490, 360), ("7 in", 370, 240), ("11 in", 205, 185)], "answer": 70},
}

SELF_HEADERS = [
    (["నేను చేయగలను…"], ["I can…"]),
    (["నమ్మకంగా"], ["Confidently"]),
    (["కొంత సహాయంతో"], ["With some help"]),
    (["లేదు—ఇంకా", "అర్థం కాలేదు!"], ["No—I don’t", "get it!"]),
]
# Translator-coordinated final wording is substituted before the generator is
# declared stable. English strings are exact transcriptions of the source pixels.
SELF_ROWS = [
    (["సంకలనాన్ని చిహ్నాలతో రాయగలను."], "use addition notation."),
    (["పూర్ణాంకాల సంకలనాన్ని నమూనాలతో చూపగలను."], "model addition of whole numbers."),
    (["నమూనాలు లేకుండా పూర్ణాంకాలను కలపగలను."], "add whole numbers without models."),
    (["మాటల్లో ఇచ్చినదాన్ని గణిత సంకేతాలతో రాయగలను."], "translate word phrases to math notation."),
    (["జీవిత సందర్భాల సమస్యల్లో పూర్ణాంకాలను కలపగలను."], "add whole numbers in applications."),
]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write(path, data):
    need(shutil.disk_usage(BASE).free >= 32 * 1024 * 1024 + len(data), "Free-space guard")
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(path, data)


def source():
    raw = (BASE / "sources/TE-B019.en.cnxml").read_bytes()
    need(digest(raw) == SOURCE_SHA, "Frozen source changed")
    meta = json.loads((BASE / "sources/TE-B019.source.json").read_text("utf-8"))
    need(
        meta["source_commit"] == COMMIT
        and meta["source_sha256"] == SOURCE_SHA
        and meta["source_module"]["sha256"] == MODULE_SHA
        and meta["text_slots"] == 494,
        "Source pin/count changed",
    )
    root = ET.fromstring(raw)
    need(
        root.get("id") == "fs-id2263283"
        and len(list(root.iter())) == 1017
        and len(list(slots(root))) == 494,
        "Source scope/count changed",
    )
    need([Path(e.get("src")).name for e in root.iter(CN + "image")] == NAMES, "Selected image order changed")
    module = (ROOT / meta["source_module"]["path"]).read_bytes()
    need(digest(module) == MODULE_SHA, "Canonical module changed")
    selected = next(e for e in ET.fromstring(module).iter() if e.get("id") == "fs-id2263283")
    selected.tail = None
    need(ET.tostring(selected) == ET.tostring(root), "Frozen selection differs from canonical module")
    return root


def originals(write_missing=False):
    root = source()
    parents = {child: parent for parent in root.iter() for child in parent}
    lock = json.loads((BASE / "sources.lock.json").read_text("utf-8"))
    record = next(r for r in lock["canonical_archives"] if r["id"] == "A00-A20-en-complete-archive")
    need(record["sha256"] == ARCHIVE_SHA and record["commit"] == COMMIT, "Archive lock changed")
    archive = ROOT / record["path"]
    need(archive.stat().st_size == 537455794 and file_digest(archive) == ARCHIVE_SHA, "Archive bytes changed")
    env = os.environ.copy()
    env.update(GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
    listing = subprocess.check_output(
        ["git", "-C", str(ROOT / "downloads/upstream-prealgebra"), "ls-tree", "-z", COMMIT, "--"]
        + ["media/" + name for name in NAMES],
        env=env,
    )
    blobs = {}
    for row in listing.split(b"\0"):
        if row:
            header, path = row.split(b"\t")
            _mode, kind, blob = header.split()
            need(kind == b"blob", "Selected object is not a Git blob")
            blobs[path.decode()] = blob.decode()
    need(set(blobs) == {"media/" + name for name in NAMES}, "Pinned media set differs")

    assets = []
    images = list(root.iter(CN + "image"))
    with zipfile.ZipFile(archive) as zipped:
        need(zipped.comment.decode() == COMMIT, "Archive comment changed")
        for image, name in zip(images, NAMES):
            member = "osbooks-prealgebra-bundle-" + COMMIT + "/media/" + name
            info = zipped.getinfo(member)
            need(0 < info.file_size < 2_000_000, "Selected image exceeds size bound")
            data = zipped.read(member)
            blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            need(blob == blobs["media/" + name], "Image differs from pinned Git blob")
            destination = OUT / "original" / name
            if destination.exists():
                need(destination.read_bytes() == data, "Refusing original overwrite: " + name)
            elif write_missing:
                write(destination, data)
            else:
                raise FileNotFoundError(destination)
            with Image.open(io.BytesIO(data)) as opened:
                dimensions = list(opened.size)
                image_format = opened.format
            media = parents[image]
            figure = parents.get(media)
            assets.append(
                {
                    "original_src": image.get("src"),
                    "original_path": destination.relative_to(BASE).as_posix(),
                    "original_sha256": digest(data),
                    "original_bytes": len(data),
                    "original_dimensions_px": dimensions,
                    "original_format": image_format,
                    "source_git_blob_sha1": blob,
                    "source_zip_crc32": f"{info.CRC:08x}",
                    "source_zip_member": member,
                    "media_id": media.get("id"),
                    "figure_id": figure.get("id") if figure is not None and figure.tag == CN + "figure" else None,
                    "localized_path": (OUT / (Path(name).stem + ".te.svg")).relative_to(BASE).as_posix(),
                }
            )
    return assets


def element(parent, tag, attrs=None, value=None):
    node = ET.SubElement(parent, SVG + tag, {key: str(item) for key, item in (attrs or {}).items()})
    if value is not None:
        node.text = str(value)
    return node


def svg_root(width, height, suffix, title, description):
    ET.register_namespace("", SVG[1:-1])
    root = ET.Element(
        SVG + "svg",
        {
            "width": str(width),
            "height": str(height),
            "viewBox": f"0 0 {width} {height}",
            "role": "img",
            "aria-labelledby": "title desc",
            "lang": "te",
            "font-family": FONT,
            "data-source-suffix": suffix,
        },
    )
    element(root, "title", {"id": "title"}, title)
    element(root, "desc", {"id": "desc"}, description)
    element(
        root,
        "metadata",
        value="New code-native mathematical redraw of one pinned OpenStax source image; the original raster is retained unchanged.",
    )
    element(root, "rect", {"x": 0, "y": 0, "width": width, "height": height, "fill": "#ffffff", "data-role": "background"})
    return root


def model_layout(suffix):
    spec = MODEL_SPECS[suffix]
    height = 470 if suffix == "205_img" else 360
    placements = {
        "201_img": [("ones", 2, 170, 145, 2), ("ones", 4, 400, 145, 4)],
        "203_img": [("tens", 1, 120, 145, 10), ("ones", 2, 520, 145, 2)],
        "205_img": [("tens", 8, 90, 75, 10), ("ones", 9, 500, 115, 3)],
        "207_img": [("tens", 4, 120, 90, 10), ("ones", 1, 520, 145, 1)],
    }[suffix]
    return 760, height, placements, spec


def model_svg(suffix):
    width, height, placements, spec = model_layout(suffix)
    groups = "; ".join(f"{count} {kind}" for kind, count, _x, _y, _cols in placements)
    root = svg_root(
        width,
        height,
        suffix,
        "పూర్ణాంకాల సంకలన బ్లాకుల నమూనా / Whole-number addition block model",
        f"{spec['expression']} కోసం బ్లాకుల నమూనా. కనిపించే సమూహాలు: {groups}. "
        f"Block model for {spec['expression']}; visible groups: {groups}. The numerical equation is not printed in this redraw.",
    )
    element(root, "text", {"x": width / 2, "y": 42, "text-anchor": "middle", "font-size": 25, "fill": INK, "data-role": "heading"},
            "సంకలన బ్లాకుల నమూనా · Addition block model")
    for index, (kind, count, start_x, start_y, cols) in enumerate(placements, 1):
        group = element(
            root,
            "g",
            {
                "data-role": "model-group",
                "data-group": index,
                "data-kind": kind,
                "data-count": count,
                "data-value": count * (10 if kind == "tens" else 1),
            },
        )
        for item in range(count):
            if kind == "tens":
                origin_x, origin_y = start_x, start_y + 38 * item
                for cell in range(10):
                    element(
                        group,
                        "rect",
                        {
                            "x": origin_x + 24 * cell,
                            "y": origin_y,
                            "width": 24,
                            "height": 24,
                            "fill": BLOCK,
                            "stroke": BLOCK_EDGE,
                            "stroke-width": 1.2,
                            "data-unit-cell": cell,
                            "data-item": item,
                        },
                    )
            else:
                origin_x = start_x + 38 * (item % cols)
                origin_y = start_y + 38 * (item // cols)
                element(
                    group,
                    "rect",
                    {
                        "x": origin_x,
                        "y": origin_y,
                        "width": 24,
                        "height": 24,
                        "fill": BLOCK,
                        "stroke": BLOCK_EDGE,
                        "stroke-width": 1.2,
                        "data-unit-cell": 0,
                        "data-item": item,
                    },
                )
    element(
        root,
        "text",
        {"x": width / 2, "y": height - 20, "text-anchor": "middle", "font-size": 20, "fill": "#526b78", "data-role": "unit-key"},
        "ఒక చిన్న గడి విలువ 1; పది గడుల కడ్డీ విలువ 10 · one cell = 1; one rod = 10",
    )
    return ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"


def blank_cells(spec):
    if spec["blanks"] == "all":
        return {(row, col) for row in spec["rows"] for col in spec["cols"]}
    return set(spec["blanks"])


def table_svg(suffix):
    spec = TABLE_SPECS[suffix]
    rows, cols, blanks = spec["rows"], spec["cols"], blank_cells(spec)
    cell_w, cell_h, margin = 68, 54, 20
    table_cols, table_rows = len(cols) + 1, len(rows) + 1
    width, height = margin * 2 + table_cols * cell_w, margin * 2 + table_rows * cell_h
    description = (
        f"సంకలన పట్టిక: శీర్షికతో కలిపి {table_cols} నిలువు వరుసలు, {table_rows} అడ్డు వరుసలు; "
        f"ఖాళీ సమాధాన గడులు {len(blanks)}. Addition table: {table_cols} columns and {table_rows} rows including headers; "
        f"{len(blanks)} answer cells are blank. Column headers: {', '.join(map(str, cols))}; row headers: {', '.join(map(str, rows))}."
    )
    root = svg_root(width, height, suffix, "సంకలన పట్టిక / Addition table", description)
    for grid_row in range(table_rows):
        for grid_col in range(table_cols):
            data_row = rows[grid_row - 1] if grid_row else None
            data_col = cols[grid_col - 1] if grid_col else None
            is_header = grid_row == 0 or grid_col == 0
            is_blank = not is_header and (data_row, data_col) in blanks
            semantic_value = "" if is_header or is_blank else data_row + data_col
            cell = element(
                root,
                "g",
                {
                    "data-role": "table-cell",
                    "data-grid-row": grid_row,
                    "data-grid-col": grid_col,
                    "data-row-value": "" if data_row is None else data_row,
                    "data-col-value": "" if data_col is None else data_col,
                    "data-header": str(is_header).lower(),
                    "data-blank": str(is_blank).lower(),
                    "data-value": semantic_value,
                },
            )
            x, y = margin + grid_col * cell_w, margin + grid_row * cell_h
            element(
                cell,
                "rect",
                {"x": x, "y": y, "width": cell_w, "height": cell_h, "fill": HEAD if is_header else PALE,
                 "stroke": EDGE, "stroke-width": 1.5, "data-role": "cell-boundary"},
            )
            if is_header:
                value = "+" if grid_row == grid_col == 0 else data_col if grid_row == 0 else data_row
            elif not is_blank:
                value = data_row + data_col
            else:
                value = None
            if value is not None:
                element(cell, "text", {"x": x + cell_w / 2, "y": y + 36, "text-anchor": "middle", "font-size": 24,
                                       "font-weight": 600 if is_header else 400, "fill": INK, "data-role": "cell-value"}, value)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"


def perimeter_svg(suffix):
    spec = PERIMETER_SPECS[suffix]
    width, height = 740, 420
    shown = ", ".join(value for value, _x, _y in spec["labels"])
    missing = " One boundary edge is intentionally unlabeled and must be derived from the given vertical lengths." if None in spec["edges"] else ""
    root = svg_root(
        width,
        height,
        suffix,
        "చుట్టుకొలత సాధన ఆకారం / Perimeter practice figure",
        f"మూసుకున్న ఆకారపు అంచులపై కనిపించే పొడవులు: {shown}. ప్రతి అంచును ఒకసారి కలపాలి. "
        f"Closed figure with visible boundary labels: {shown}. Add every boundary edge once.{missing} The perimeter answer is not shown.",
    )
    element(
        root,
        "polygon",
        {"points": " ".join(f"{x},{y}" for x, y in spec["points"]), "fill": "#e9f5f2", "stroke": EDGE,
         "stroke-width": 4, "stroke-linejoin": "round", "data-role": "boundary",
         "data-edge-count": len(spec["edges"]),
         "data-visible-lengths": ",".join(str(edge) for edge in spec["edges"] if edge is not None),
         "data-derived-unlabeled-length": "" if None not in spec["edges"] else spec["answer"] - sum(edge for edge in spec["edges"] if edge is not None),
         "data-unit": spec["unit"]},
    )
    for index, (value, x, y) in enumerate(spec["labels"], 1):
        element(root, "text", {"x": x, "y": y, "text-anchor": "middle", "font-size": 25, "fill": INK,
                               "data-role": "side-label", "data-label-index": index}, value)
    element(root, "text", {"x": width / 2, "y": height - 18, "text-anchor": "middle", "font-size": 20,
                           "fill": "#526b78", "data-role": "unit-key"}, f"{spec['unit']} = {spec['unit_te']}")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"


def selfcheck_svg():
    suffix = "AppB_002_A"
    x_edges = [20, 740, 980, 1220, 1460]
    y_edges = [20, 156, 256, 356, 456, 556, 656]
    description = (
        "స్వీయ పరిశీలన పట్టిక. ఐదు లక్ష్యాలు; మూడు స్వీయ అంచనా ఎంపికలు; మొత్తం 15 ఎంపిక గడులు ఖాళీగా ఉన్నాయి. "
        "Self-assessment: five objectives, three confidence options, all 15 response cells blank. Objectives: "
        + "; ".join(" ".join(te) + " / " + en for te, en in SELF_ROWS)
    )
    root = svg_root(1480, 680, suffix, "స్వీయ పరిశీలన / Self-assessment checklist", description)
    for row in range(6):
        for col in range(4):
            response = row > 0 and col > 0
            cell = element(root, "g", {"data-role": "table-cell", "data-row": row, "data-col": col,
                                       "data-response": str(response).lower()})
            x, y = x_edges[col], y_edges[row]
            width, height = x_edges[col + 1] - x, y_edges[row + 1] - y
            element(cell, "rect", {"x": x, "y": y, "width": width, "height": height,
                                   "fill": HEAD if row == 0 else PALE if row % 2 else "#ffffff",
                                   "stroke": EDGE, "stroke-width": 1.5, "data-role": "cell-boundary"})
            if row == 0:
                te, en = SELF_HEADERS[col]
                cx = (x_edges[col] + x_edges[col + 1]) / 2
                for line, value in enumerate(te):
                    element(cell, "text", {"x": cx, "y": (54 if len(te) > 1 else 76) + 32 * line,
                                           "text-anchor": "middle", "font-size": 26, "fill": INK,
                                           "data-role": "header-te", "lang": "te"}, value)
                for line, value in enumerate(en):
                    element(cell, "text", {"x": cx, "y": 118 + 22 * line, "text-anchor": "middle",
                                           "font-size": 20, "fill": "#334e5d", "data-role": "header-en", "lang": "en"}, value)
            elif col == 0:
                te, en = SELF_ROWS[row - 1]
                for line, value in enumerate(te):
                    element(cell, "text", {"x": x + 18, "y": y + (31 if len(te) > 1 else 40) + 32 * line,
                                           "text-anchor": "start", "font-size": 25, "fill": INK,
                                           "data-role": "objective-te", "lang": "te"}, value)
                element(cell, "text", {"x": x + 18, "y": y + 87, "text-anchor": "start", "font-size": 20,
                                       "fill": "#334e5d", "data-role": "objective-en", "lang": "en"}, en)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"


def suffix_for(name):
    stem = Path(name).stem
    if stem.startswith("CNX_BMath_Figure_01_02_"):
        return stem.removeprefix("CNX_BMath_Figure_01_02_")
    need(stem == "CNX_BMath_Figure_AppB_002_A", "Unexpected source image")
    return "AppB_002_A"


def svg_bytes(name):
    suffix = suffix_for(name)
    if suffix in MODEL_SPECS:
        return model_svg(suffix)
    if suffix in TABLE_SPECS:
        return table_svg(suffix)
    if suffix in PERIMETER_SPECS:
        return perimeter_svg(suffix)
    need(suffix == "AppB_002_A", "No redraw specification")
    return selfcheck_svg()


def common_check(root, suffix):
    need(root.tag == SVG + "svg" and root.get("data-source-suffix") == suffix, "SVG identity changed")
    need(root.get("role") == "img" and root.get("aria-labelledby") == "title desc" and root.get("lang") == "te",
         "Accessible root changed")
    need(root.find(SVG + "title") is not None and root.find(SVG + "desc") is not None, "Accessible title/description missing")
    need(not any(e.tag in {SVG + "image", SVG + "script", SVG + "foreignObject", SVG + "use"} for e in root.iter()),
         "SVG is not code-native static content")
    need(not any(key.startswith("on") or key in {"href", "transform", "style", "display", "visibility", "opacity"}
                 for e in root.iter() for key in e.attrib), "Hidden, transformed or interactive SVG content")
    width, height = int(root.get("width")), int(root.get("height"))
    need(root.get("viewBox") == f"0 0 {width} {height}", "Canvas changed")
    background = next((e for e in root if e.get("data-role") == "background"), None)
    need(background is not None and background.tag == SVG + "rect" and background.get("width") == str(width)
         and background.get("height") == str(height), "Background/canvas mismatch")
    return width, height


def check_model(root, suffix):
    width, height = common_check(root, suffix)
    expected_width, expected_height, placements, spec = model_layout(suffix)
    need((width, height) == (expected_width, expected_height), "Model canvas changed")
    groups = [e for e in root if e.get("data-role") == "model-group"]
    need(len(groups) == len(placements), "Model group count changed")
    actual_value = 0
    for group, (kind, count, start_x, start_y, cols), number in zip(groups, placements, range(1, len(groups) + 1)):
        need(group.get("data-group") == str(number) and group.get("data-kind") == kind
             and group.get("data-count") == str(count), "Model group metadata changed")
        cells = list(group)
        expected_cells = count * (10 if kind == "tens" else 1)
        need(len(cells) == expected_cells and all(e.tag == SVG + "rect" for e in cells), "Model unit-cell count changed")
        seen = set()
        for cell in cells:
            item, unit = int(cell.get("data-item")), int(cell.get("data-unit-cell"))
            need(0 <= item < count and 0 <= unit < (10 if kind == "tens" else 1), "Model cell index changed")
            need((item, unit) not in seen, "Duplicate model cell")
            seen.add((item, unit))
            if kind == "tens":
                x, y = start_x + 24 * unit, start_y + 38 * item
            else:
                x, y = start_x + 38 * (item % cols), start_y + 38 * (item // cols)
            need((float(cell.get("x")), float(cell.get("y")), float(cell.get("width")), float(cell.get("height")))
                 == (x, y, 24, 24), "Model cell geometry changed")
            need(cell.get("fill") == BLOCK and cell.get("stroke") == BLOCK_EDGE, "Model cell visibility changed")
            need(0 <= x and 0 <= y and x + 24 <= width and y + 24 <= height, "Model cell outside canvas")
        actual_value += count * (10 if kind == "tens" else 1)
        need(group.get("data-value") == str(count * (10 if kind == "tens" else 1)), "Model group value changed")
    need(actual_value == spec["value"], "Modeled value changed")
    visible = [e.text for e in root.iter(SVG + "text")]
    need(visible == ["సంకలన బ్లాకుల నమూనా · Addition block model",
                     "ఒక చిన్న గడి విలువ 1; పది గడుల కడ్డీ విలువ 10 · one cell = 1; one rod = 10"],
         "Visible model wording or answer changed")
    need(not any(e.get("data-role") == "answer" for e in root.iter()), "Model image reveals a numerical answer")
    return {"kind": "block_model", "expression": spec["expression"], "modeled_value": actual_value,
            "groups": [[kind, count] for kind, count, _x, _y, _cols in placements], "visible_answer": False}


def check_table(root, suffix):
    width, height = common_check(root, suffix)
    spec = TABLE_SPECS[suffix]
    rows, cols, blanks = spec["rows"], spec["cols"], blank_cells(spec)
    cell_w, cell_h, margin = 68, 54, 20
    expected_width, expected_height = margin * 2 + (len(cols) + 1) * cell_w, margin * 2 + (len(rows) + 1) * cell_h
    need((width, height) == (expected_width, expected_height), "Addition-table canvas/orientation changed")
    cells = [e for e in root if e.get("data-role") == "table-cell"]
    need(len(cells) == (len(rows) + 1) * (len(cols) + 1), "Addition-table cell count changed")
    seen, blank_count = set(), 0
    for cell in cells:
        grid_row, grid_col = int(cell.get("data-grid-row")), int(cell.get("data-grid-col"))
        need((grid_row, grid_col) not in seen, "Duplicate addition-table cell")
        seen.add((grid_row, grid_col))
        is_header = grid_row == 0 or grid_col == 0
        data_row = rows[grid_row - 1] if grid_row else None
        data_col = cols[grid_col - 1] if grid_col else None
        is_blank = not is_header and (data_row, data_col) in blanks
        need(cell.get("data-header") == str(is_header).lower() and cell.get("data-blank") == str(is_blank).lower(),
             "Addition-table header/blank metadata changed")
        expected_semantic_value = "" if is_header or is_blank else str(data_row + data_col)
        need(cell.get("data-value") == expected_semantic_value, "Addition-table semantic value changed")
        boundary = cell.find(SVG + "rect")
        labels = cell.findall(SVG + "text")
        need(boundary is not None and len(cell) == 1 + len(labels), "Addition-table cell structure changed")
        x, y = margin + grid_col * cell_w, margin + grid_row * cell_h
        need(tuple(float(boundary.get(key)) for key in ("x", "y", "width", "height")) == (x, y, cell_w, cell_h),
             "Addition-table cell geometry changed")
        if is_header:
            expected = "+" if grid_row == grid_col == 0 else data_col if grid_row == 0 else data_row
            need(len(labels) == 1 and labels[0].text == str(expected), "Addition-table header changed")
        elif is_blank:
            blank_count += 1
            need(not labels, "Blank answer cell was filled")
        else:
            need(len(labels) == 1 and labels[0].text == str(data_row + data_col), "False addition-table value")
    need(blank_count == len(blanks), "Addition-table blank count changed")
    return {"kind": "addition_table", "columns_including_header": len(cols) + 1,
            "rows_including_header": len(rows) + 1, "blank_answer_cells": blank_count,
            "all_visible_sums_true": True}


def check_perimeter(root, suffix):
    width, height = common_check(root, suffix)
    need((width, height) == (740, 420), "Perimeter canvas changed")
    spec = PERIMETER_SPECS[suffix]
    boundary = next((e for e in root if e.get("data-role") == "boundary"), None)
    need(boundary is not None and boundary.tag == SVG + "polygon", "Perimeter boundary missing")
    need(boundary.get("points") == " ".join(f"{x},{y}" for x, y in spec["points"]), "Perimeter topology changed")
    derived = spec["answer"] - sum(edge for edge in spec["edges"] if edge is not None)
    need(boundary.get("data-edge-count") == str(len(spec["edges"]))
         and boundary.get("data-visible-lengths") == ",".join(str(edge) for edge in spec["edges"] if edge is not None)
         and boundary.get("data-derived-unlabeled-length") == (str(derived) if None in spec["edges"] else "")
         and boundary.get("data-unit") == spec["unit"], "Perimeter semantic metadata changed")
    labels = [e for e in root if e.get("data-role") == "side-label"]
    need([(e.text, int(e.get("data-label-index"))) for e in labels]
         == [(value, index) for index, (value, _x, _y) in enumerate(spec["labels"], 1)], "Perimeter labels changed")
    for label, (_value, x, y) in zip(labels, spec["labels"]):
        need((float(label.get("x")), float(label.get("y"))) == (x, y), "Perimeter label position changed")
    unit_key = next((e for e in root if e.get("data-role") == "unit-key"), None)
    need(unit_key is not None and unit_key.text == f"{spec['unit']} = {spec['unit_te']}", "Perimeter unit key changed")
    need(len(labels) == len([edge for edge in spec["edges"] if edge is not None]), "Labeled-edge count changed")
    need((derived == 0 and None not in spec["edges"]) or (derived == 3 and spec["edges"].count(None) == 1),
         "Perimeter invariant changed")
    need(not any(e.get("data-role") == "answer" for e in root.iter()), "Perimeter problem reveals answer")
    need(str(spec["answer"]) not in [e.text for e in root.iter(SVG + "text")], "Perimeter answer printed")
    return {"kind": "perimeter_problem", "visible_edge_lengths": [edge for edge in spec["edges"] if edge is not None],
            "unlabeled_derived_edges": spec["edges"].count(None),
            "derived_unlabeled_lengths": [derived] if None in spec["edges"] else [],
            "verified_perimeter_not_displayed": spec["answer"],
            "unit": spec["unit"], "visible_answer": False}


def check_selfcheck(root):
    suffix = "AppB_002_A"
    width, height = common_check(root, suffix)
    need((width, height) == (1480, 680), "Self-check canvas changed")
    cells = [e for e in root if e.get("data-role") == "table-cell"]
    need(len(cells) == 24, "Self-check must have four columns and six rows including header")
    seen, responses = set(), 0
    for cell in cells:
        row, col = int(cell.get("data-row")), int(cell.get("data-col"))
        need((row, col) not in seen and 0 <= row < 6 and 0 <= col < 4, "Self-check cell coordinates changed")
        seen.add((row, col))
        labels = cell.findall(SVG + "text")
        response = row > 0 and col > 0
        need(cell.get("data-response") == str(response).lower(), "Self-check response metadata changed")
        if response:
            responses += 1
            need(len(cell) == 1 and not labels, "Self-check response cell is not blank")
        elif row == 0:
            te, en = SELF_HEADERS[col]
            need([e.text for e in labels] == te + en, "Self-check header changed")
            need([e.get("lang") for e in labels] == ["te"] * len(te) + ["en"] * len(en), "Self-check header language changed")
        else:
            te, en = SELF_ROWS[row - 1]
            need([e.text for e in labels] == te + [en], "Self-check objective changed")
            need([e.get("lang") for e in labels] == ["te"] * len(te) + ["en"], "Self-check objective language changed")
    need(responses == 15, "Self-check must retain 15 blank response cells")
    need(not list(root.iter(SVG + "path")) and not list(root.iter(SVG + "circle")), "Invented self-check mark")
    return {"kind": "self_assessment", "columns": 4, "rows_including_header": 6, "objectives": 5,
            "confidence_options": 3, "blank_response_cells": 15, "preselected_state": False,
            "exact_english_rows_preserved": True}


def check_svg(name, payload):
    suffix = suffix_for(name)
    root = ET.fromstring(payload)
    if suffix in MODEL_SPECS:
        return check_model(root, suffix)
    if suffix in TABLE_SPECS:
        return check_table(root, suffix)
    if suffix in PERIMETER_SPECS:
        return check_perimeter(root, suffix)
    need(suffix == "AppB_002_A", "Unexpected redraw")
    return check_selfcheck(root)


def build(verify=False, originals_only=False):
    records = originals(write_missing=not verify)
    if originals_only:
        print(json.dumps({"status": "PASS", "originals": len(records),
                          "original_bytes": sum(a["original_bytes"] for a in records),
                          "archive_sha_crc_git_blobs": "PASS"}))
        return
    outputs = {}
    for record, name in zip(records, NAMES):
        payload = svg_bytes(name)
        record["math_checks"] = check_svg(name, payload)
        record["localized_sha256"] = digest(payload)
        record["localized_bytes"] = len(payload)
        record["recommended_min_width_px"] = int(ET.fromstring(payload).get("width"))
        record["disclosure"] = (
            "New code-native bilingual mathematical redraw after complete original-pixel inspection; "
            "the source JPEG is retained unchanged and no raster pixels are embedded or edited."
        )
        if name.endswith("_222.jpg"):
            record["source_alt_correction"] = (
                "Frozen source alt reverses the table dimensions. Inspected pixels show 5 columns and 8 rows including headers, "
                "with column headers 6-9 and row headers 3-9; the redraw follows the pixels."
            )
        target = BASE / record["localized_path"]
        outputs[target] = payload
    manifest = {
        "schema": "te-b002-assets-v1",
        "unit": "TE-B019",
        "source_subsection_id": "fs-id2263283",
        "source_subsection_sha256": SOURCE_SHA,
        "canonical_commit": COMMIT,
        "canonical_archive_sha256": ARCHIVE_SHA,
        "source_attribution": "OpenStax, Prealgebra 2e; existing project notices and source attribution remain applicable.",
        "generator": "scripts/make_b019_assets.py",
        "verification_command": "python -B te-Telu-IN/scripts/make_b019_assets.py --verify",
        "scope": "Exactly 22 selected unchanged source JPEGs and 22 code-native localized SVG redraws; no download or bulk extraction.",
        "choices": [
            "All 22 exact source rasters were read at complete supplied pixel size before redraw specifications were fixed.",
            "Block-model counts are 201:2+4 individual units; 203:one ten rod+2 units; 205:eight rods+9 units; 207:four rods+1 unit.",
            "Addition-chart blank cells, axes and visible sums follow the inspected pixels; full answer charts remain full and problem charts remain incomplete.",
            "Figure222 follows the actual 5-column by8-row orientation; frozen English alt's reversed dimensions remain documented rather than silently changing source.",
            "Perimeter redraws retain every visible source length and unit. Figure215 keeps its sixth edge unlabeled; the derived3 and perimeter70 are verification-only, not printed.",
            "Self-check retains the exact five English objectives, bilingual Telugu rows and all15 response cells blank; no score or correct state is invented.",
            "Fresh B019-stage reads used actual TS6PDF27, TS2PDF44 and TS6PDF141-142 OCR before complete page images. They support సంకలనం, place-aligned values and చుట్టుకొలత, but not official Telugu labels for expression/addend/notation.",
            "Evidence is Telangana-only; no Andhra Pradesh terminology difference or native-speaker approval is claimed.",
        ],
        "assets": records,
        "qa": {
            "source_media_count": 22,
            "localized_asset_count": 22,
            "original_bytes": sum(a["original_bytes"] for a in records),
            "original_crc_git_blob_archive_sha": "PASS",
            "code_native_math_checks": "PASS",
            "independent_visual_approval": False,
            "native_speaker_approval": False,
        },
    }
    outputs[OUT / "manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    sections = []
    for record in records:
        local = Path(record["localized_path"]).name
        original = Path(record["original_path"]).name
        sections.append(
            f'<section><h2>{record["media_id"]}: {local}</h2><p>Unchanged source</p>'
            f'<img class="original" src="original/{original}" alt="Preserved source image">'
            f'<p>Code-native redraw</p><div class="scroll" tabindex="0"><img src="{local}" '
            f'width="{record["recommended_min_width_px"]}" alt="B019 localized asset author preview"></div></section>'
        )
    preview = (
        '<!doctype html><html lang="te"><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
        '<title>B019 asset author preview</title><style>body{font-family:"Nirmala UI",sans-serif;color:#173b4d;background:#edf3f4;margin:24px}'
        'main{max-width:1500px;margin:auto}section{background:#fff;border:1px solid #cad9dd;padding:18px;margin:24px 0}'
        '.scroll{max-width:100%;overflow:auto}.scroll:focus{outline:3px solid #385e8c}.scroll img{max-width:none;display:block}'
        'img.original{max-width:100%;height:auto;display:block}h2{font-size:18px}</style><main><h1>B019 asset author preview</h1>'
        '<p>Author comparison only; independent integrated-reader review remains separate.</p>' + "".join(sections) + '</main></html>\n'
    )
    outputs[OUT / "preview.html"] = preview.encode("utf-8")
    for path, payload in outputs.items():
        if verify:
            need(path.read_bytes() == payload, "Generated asset/manifest differs: " + path.name)
        else:
            write(path, payload)
    print(json.dumps({"status": "PASS", "assets": len(records), "original_bytes": manifest["qa"]["original_bytes"],
                      "svg_bytes": sum(a["localized_bytes"] for a in records), "writes": 0 if verify else len(outputs)}))


def self_test():
    rejected = 0

    def reject(name, change, label):
        nonlocal rejected
        root = ET.fromstring(svg_bytes(name))
        change(root)
        try:
            check_svg(name, ET.tostring(root))
        except (ValueError, TypeError, KeyError, StopIteration, IndexError):
            rejected += 1
        else:
            raise AssertionError("Accepted corrupted asset: " + name + " / " + label)

    for name in NAMES:
        check_svg(name, svg_bytes(name))
        reject(name, lambda root: root.set("viewBox", "0 0 1 1"), "clipped canvas")
        reject(name, lambda root: root.set("opacity", "0"), "invisible root")
        reject(name, lambda root: element(root, "image", {"href": "wrong.jpg"}), "embedded raster")
        suffix = suffix_for(name)
        if suffix in MODEL_SPECS:
            reject(name, lambda root: next(e for e in root if e.get("data-role") == "model-group").remove(
                list(next(e for e in root if e.get("data-role") == "model-group"))[0]), "missing unit cell")
            reject(name, lambda root: next(e for e in root if e.get("data-role") == "model-group").set("data-count", "99"),
                   "false block count")
            reject(name, lambda root: element(root, "text", {"data-role": "answer"}, MODEL_SPECS[suffix]["value"]),
                   "visible answer")
        elif suffix in TABLE_SPECS:
            reject(name, lambda root: root.remove(next(e for e in root if e.get("data-role") == "table-cell")), "missing cell")
            reject(name, lambda root: setattr(next(e for e in root.iter(SVG + "text") if e.get("data-role") == "cell-value"),
                                              "text", "999"), "false value")
            if blank_cells(TABLE_SPECS[suffix]):
                reject(name, lambda root: element(next(e for e in root if e.get("data-blank") == "true"), "text",
                                                   {"data-role": "cell-value"}, "999"), "filled blank")
        elif suffix in PERIMETER_SPECS:
            reject(name, lambda root: next(e for e in root if e.get("data-role") == "boundary").set("points", "0,0"),
                   "false topology")
            reject(name, lambda root: setattr(next(e for e in root if e.get("data-role") == "side-label"), "text", "999 in"),
                   "false length")
            reject(name, lambda root: element(root, "text", {"data-role": "answer"}, PERIMETER_SPECS[suffix]["answer"]),
                   "visible answer")
        else:
            reject(name, lambda root: element(next(e for e in root if e.get("data-response") == "true"), "text", value="✓"),
                   "preselected response")
            reject(name, lambda root: setattr(next(e for e in root.iter(SVG + "text") if e.get("data-role") == "objective-en"),
                                              "text", "wrong objective"), "changed English objective")
            reject(name, lambda root: root.remove(next(e for e in root if e.get("data-response") == "true")),
                   "missing response cell")
    need(rejected >= 100, "Self-test coverage unexpectedly low")
    print(json.dumps({"status": "PASS", "valid_assets": 22, "rejected_corruptions": rejected, "writes": 0}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--originals-only", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    need(sum((args.originals_only, args.verify, args.self_test)) <= 1, "Choose at most one mode")
    if args.self_test:
        self_test()
    else:
        build(verify=args.verify, originals_only=args.originals_only)
