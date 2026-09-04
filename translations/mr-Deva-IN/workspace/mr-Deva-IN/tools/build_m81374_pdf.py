"""Standalone m81374 reading-copy PDF from the accepted assembly XML.

The immutable build_pdf.py supplies the approved HarfBuzz/ReportLab layout,
font, ActualText, attachment, and PDF inspection primitives.  This module adds
the complete m81374 source contract, three-column tables, nested source lists,
the h5/footer structures, and a pinned circled-letter fallback.  It never reads
HTML, CSS, or a browser.  Run with Python -B and the recorded bundled runtime.
"""
from collections import Counter
from copy import deepcopy
from io import BytesIO
import json
from pathlib import Path
import platform
import re
import struct
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape, quoteattr

import assemble_m81374 as assembly
import build_pdf as core


BASE = Path(__file__).resolve().parents[1]
UNIT = "A20-m81374"
SOURCE_SHA = "c629adb12dd6381b9d219d783f4af055aa1a8c060a9b36dce3bfcb5a39c1172d"
HELPER_SHA = "c54d8571feb262fcce90d37dbe9d02fcdf9b39246fbed739ce9992f1185afc90"
ASSEMBLY_RECEIPT_SHA = "b9ba76426ed17552d523f6ad192cbb11944efcd85483cfef88289c98f646df16"
ASSEMBLY_BUILDER_SHA = "3220e1a0164c1a6af71066d3250952cc7773a70a1f6095c0a5fbc3548274b54d"
PRIMARY_SOURCE_TEST_SHA = "3f11b59133d137b32e5157dab8baab25f17236b69bd47942a5708b74597fd9e7"
ASSEMBLY_ONLY_IDS = (
    "A20-m81374", "assembly-objectives", "assembly-content",
    "MR-BRIDGE-015--MR-BRIDGE-015-self-rating", "credits",
)
TABLE_ROWS = (6, 6, 3, 8, 6, 5, 8, 3, 4)
TABLE_COLUMNS = (3, 3, 2, 3, 3, 3, 3, 2, 4)
TABLE_HEADERS = (1, 1, 0, 1, 1, 1, 1, 0, 1)
MATH_SYMBOLS = frozenset("π⁴⁵₁₂ℤ→∈√∞≠≤≥")
CIRCLED_SYMBOLS = frozenset("ⓐⓑⓒⓓⓔⓕⓖⓗ")
CIRCLED_FONT = "C:/Windows/Fonts/seguisym.ttf"
LEAVES = core.LEAVES | {"h5"}
CONTAINERS = core.CONTAINERS | {"footer"}
ORIGINAL_FRAMING = (
    "स्रोताच्या क्रमातील संपूर्ण एकत्रित अनुवाद-मसुदा. मूळ शिकवणी, सोडवलेली उदाहरणे, "
    "विभाग-सराव, धड्याची उजळणी, सराव चाचणी, स्रोत-उत्तरे आणि उत्तर नसलेल्या प्रश्नांच्या "
    "स्पष्ट नोंदी येथे एकत्र आहेत. दुरुस्त्या व जोडस्पष्टीकरणे स्वतंत्र लेखक-भूमिकेत राहतात. "
    "हा HTML/PDF वाचक, मानवी मान्यता, संपूर्ण पुस्तक किंवा पाच-पुस्तकांचा पूर्ण कार्यप्रवाह नाही."
)
PDF_FRAMING = (
    "स्रोताच्या क्रमातील स्वतंत्र PDF वाचन-मसुदा. मूळ शिकवणी, सोडवलेली उदाहरणे, विभाग-सराव, "
    "धड्याची उजळणी, सराव चाचणी, स्रोत-उत्तरे आणि उत्तर नसलेल्या प्रश्नांच्या स्पष्ट नोंदी येथे "
    "एकत्र आहेत. दुरुस्त्या व जोडस्पष्टीकरणे स्वतंत्र लेखक-भूमिकेत राहतात. ही आशय आणि मांडणी "
    "तपासण्यासाठीची PDF प्रत आहे; संपूर्ण पुस्तक किंवा पाच-पुस्तकांचा कार्यप्रवाह पूर्ण झाल्याचा दावा नाही."
)
require = core.pins.require
sha = core.pins.sha


def read_json(path):
    raw = path.read_bytes()
    return json.loads(raw, object_pairs_hook=assembly.object_pairs), raw


def table_shapes(root):
    return [{
        "id": node.get("id"),
        "rows": len(list(node.iter("tr"))),
        "columns": [len(row) for row in node.iter("tr")],
        "header_rows": len(node.findall("thead/tr")),
    } for node in root.iter("table")]


def load_inputs(base=BASE):
    base = Path(base).resolve()
    helper_raw = (base / "tools/build_pdf.py").read_bytes()
    require(sha(helper_raw) == HELPER_SHA, "immutable PDF helper changed")
    require(sha((base / "tools/assemble_m81374.py").read_bytes()) == ASSEMBLY_BUILDER_SHA,
            "accepted assembly builder changed")
    require(sha((base / "tools/test_m81374_primary_source.py").read_bytes()) == PRIMARY_SOURCE_TEST_SHA,
            "accepted independent source oracle changed")

    receipt, receipt_raw = read_json(base / "qa/A20-m81374-assembly-receipt.json")
    require(sha(receipt_raw) == ASSEMBLY_RECEIPT_SHA, "accepted assembly receipt changed")
    require(len(receipt["inputs"]) == 954, "expected all 954 assembly input pins")
    require(sum(record["bytes"] for record in receipt["inputs"].values()) == 13527010,
            "assembly input byte census changed")
    for path, record in receipt["inputs"].items():
        raw = assembly.safe_path(base, path).read_bytes()
        require((len(raw), sha(raw)) == (record["bytes"], record["sha256"]),
                "assembly input drift: " + path)

    raw = assembly.safe_path(base, receipt["output"]["path"]).read_bytes()
    require((len(raw), sha(raw)) == (588465, SOURCE_SHA), "accepted assembly XML changed")
    require(receipt["output"] == {"path": "translations/A20-m81374.xml",
                                   "sha256": SOURCE_SHA, "bytes": 588465},
            "assembly output record changed")
    rebuilt, rebuilt_receipt = assembly.Assembly(base).build()
    require(rebuilt == raw and rebuilt_receipt == receipt_raw,
            "assembly cannot be exactly reproduced")
    core.pins.validate_text(raw.decode("utf-8"), "assembly")
    require(b"<!DOCTYPE" not in raw and b"<!ENTITY" not in raw, "XML declarations prohibited")

    source = ET.fromstring(raw)
    require(source.tag == "article" and source.get("id") == UNIT
            and source.get("lang") == "mr-Deva-IN", "wrong PDF source identity")
    require(len(source.findall("header")) == len(source.findall("footer")) == 1,
            "one module header/footer required")
    ids = assembly.source_ids(source)
    require(len(ids) == len(set(ids)) == 1371, "1371 unique XML IDs required")
    canonical = set(receipt["canonical_id_order"])
    require(len(canonical) == 1366, "1366 canonical IDs required")
    require([ident for ident in ids if ident in canonical] == receipt["canonical_id_order"],
            "canonical ID order drift")
    require(tuple(ident for ident in ids if ident not in canonical) == ASSEMBLY_ONLY_IDS,
            "five assembly-only IDs changed")

    selectors = [node.get("data-source") for node in source.iter() if node.get("data-source")]
    require(selectors == [item["locator"] for item in receipt["selection_order"]]
            and len(selectors) == 380, "380 source selections changed")
    checks = [node for node in source.iter() if node.get("data-check")]
    require(len(checks) == 685, "685 target checks required")
    require({node.get("data-check"): assembly.text(node) for node in checks}
            == receipt["expected_math"], "reviewed mathematical strings changed")
    counts = receipt["counts"]
    required_counts = {
        "source_elements_per_locale": 7223, "canonical_ids": 1366,
        "unique_ordered_nonnested_selectors": 380, "rebuilt_source_wrappers": 14,
        "outer_authored_nodes_retained": 26, "source_exercises": 255,
        "source_supplied_answers": 141, "explicit_source_answer_omissions": 114,
        "source_mathml": 481, "namespaced_target_checks": 685,
        "canonical_assets": 149, "canonical_asset_bytes": 9908130,
        "blank_self_rating_cells": 9, "adapted_linear_source_tables": 2,
        "adapted_linear_source_rows": 7, "adapted_linear_source_entries": 14,
        "localized_same_module_source_links": 6,
        "external_outside_module_source_links": 8, "optional_external_resources": 1,
    }
    require(counts == required_counts, "accepted assembly count contract changed")
    roles = Counter(node.get("data-kind") for node in source.iter() if node.get("data-kind"))
    require(roles == Counter(translation=380, original=340, **{"source-context": 16}, adaptation=1),
            "translation/source role census changed")
    problems = [node for node in source.iter() if node.get("class") == "problem"]
    solutions = [node for node in source.iter() if node.get("class") == "solution"]
    require((len(problems), len(solutions), len(problems) - len(solutions)) == (255, 141, 114),
            "exercise/answer role census changed")

    shapes = table_shapes(source)
    require(tuple(item["rows"] for item in shapes) == TABLE_ROWS, "table row census changed")
    require(tuple(item["columns"][0] for item in shapes) == TABLE_COLUMNS
            and all(item["columns"] == [item["columns"][0]] * item["rows"] for item in shapes),
            "table column census changed")
    require(tuple(item["header_rows"] for item in shapes) == TABLE_HEADERS,
            "table header census changed")
    rating = source.find(".//table[@id='MR-BRIDGE-015--MR-BRIDGE-015-self-rating']")
    require(rating is not None, "self-rating table missing")
    rating_cells = list(rating.iter("td"))
    require(len(rating_cells) == 9 and all(not core.logical(node).strip()
            and not node.attrib and len(node) == 0 for node in rating_cells),
            "nine rating cells must remain blank")
    require(len(receipt["table_adaptations"]) == 2
            and sum(item["source_rows"] for item in receipt["table_adaptations"]) == 7
            and sum(item["source_entries"] for item in receipt["table_adaptations"]) == 14,
            "linear source-table adaptation disclosure changed")

    metadata = source.find("header/dl")
    require(metadata is not None and [node.tag for node in metadata] == ["dt", "dd"] * 4,
            "metadata pairs changed")
    allowed = (core.INLINE | CONTAINERS | LEAVES
               | {"table", "thead", "tbody", "tr", "th", "td", "img", "dl", "dt", "dd"})
    require(all(node.tag in allowed for node in source.iter()), "unsupported module element")

    local_links, urls = [], []
    for node in source.iter("a"):
        href = node.get("href", "")
        if href.startswith("#"):
            require(href[1:] in ids, "unresolved local PDF link")
            local_links.append(href[1:])
        else:
            require(href.startswith("https://"), "unsafe PDF link")
            urls.append(href)
    require((len(local_links), len(urls)) == (288, 10), "target link census changed")
    require(len(receipt["link_policy"]["localized_links"]) == 6,
            "same-module localization census changed")
    require(all(item["new_href"].startswith("#") for item in receipt["link_policy"]["localized_links"]),
            "same-module link policy changed")

    require(len(receipt["assets"]) == 149, "149 canonical assets required")
    asset_records = []
    for path, record in receipt["assets"].items():
        image = assembly.safe_path(base, path).read_bytes()
        require(record["mime"] == "image/jpeg" and image.startswith(b"\xff\xd8\xff"),
                "invalid canonical JPEG")
        require((len(image), sha(image)) == (record["bytes"], record["sha256"]),
                "canonical asset pin mismatch: " + path)
        require(path in receipt["inputs"], "asset missing from input pins")
        asset_records.append(dict(record, path=path))
    images = list(source.iter("img"))
    routes = [node.get("src") for node in images]
    require(len(images) == 149 and routes == ["../" + path for path in receipt["assets"]],
            "canonical image order/routes changed")
    require(sum(record["bytes"] for record in asset_records) == 9908130,
            "canonical asset byte count changed")
    require(all(node.get("alt", "").strip() for node in images), "empty image description")

    root = deepcopy(source)
    framing = root.find("header/p[@data-kind='original']")
    require(framing is not None and len(framing) == 0 and framing.text == ORIGINAL_FRAMING,
            "unreviewed header framing")
    framing.text = PDF_FRAMING
    transform = {
        "path": "article/header/p[@data-kind='original'][1]",
        "kind": "render-clone-only authored framing", "original": ORIGINAL_FRAMING,
        "rendered": PDF_FRAMING, "all_other_XML_content": "unchanged",
        "original_XML_attached": True,
    }
    return {
        "unit": UNIT, "base": base, "root": root, "original_root": source, "xml": raw,
        "assembly_receipt": receipt, "assembly_receipt_raw": receipt_raw, "ids": ids,
        "assets": receipt["assets"], "asset_records": asset_records, "math_count": 685,
        "local_links": local_links, "urls": urls, "tables": shapes,
        "header_transformation": transform, "roles": roles,
    }


def register_fonts():
    records = core.register_fonts()
    font = core.TTFont("Circled", CIRCLED_FONT, shapable=True)
    fs_type = struct.unpack(">H", font.face.get_table("OS/2")[8:10])[0]
    require(not fs_type & (2 | 0x100 | 0x200), "circled fallback font embedding restricted")
    require(all(font.face.charToGlyph.get(ord(character)) for character in CIRCLED_SYMBOLS),
            "circled fallback coverage changed")
    core.pdfmetrics.registerFont(font)
    records.append({
        "name": "Circled", "path": CIRCLED_FONT, "collection_index": 0,
        "sha256": sha(Path(CIRCLED_FONT).read_bytes()), "embedding_fsType": fs_type,
        "shaping": "HarfBuzz",
    })
    return records


def markup(text):
    def word(match):
        value = match.group(0)
        if set(value) & CIRCLED_SYMBOLS:
            name = "Circled"
        elif set(value) & MATH_SYMBOLS:
            name = "Symbols"
        else:
            return escape(value)
        cmap = core.pdfmetrics.getFont(name).face.charToGlyph
        require(all(cmap.get(ord(character)) for character in value),
                f"{name} word glyph missing: " + value)
        return '<font name="' + name + '">' + escape(value) + "</font>"
    return re.sub(r"\S+", word, core.normalized(text))


def inline(node):
    value = markup(node.text)
    for child in node:
        require(child.tag in core.INLINE, "unsupported inline XML: " + child.tag)
        rendered = inline(child)
        if child.tag == "br":
            rendered = "<br/>"
        elif child.tag == "a":
            href = child.get("href", "")
            require(href.startswith(("https://", "#")), "unsafe link")
            rendered = "<link href=" + quoteattr(href) + ' color="#165c78">' + rendered + "</link>"
        elif child.tag in {"b", "strong", "dfn"}:
            rendered = "<b>" + rendered + "</b>"
        elif child.tag in {"i", "em", "cite"}:
            rendered = "<i>" + rendered + "</i>"
        elif child.tag in {"sup", "sub"}:
            rendered = "<" + child.tag + ">" + rendered + "</" + child.tag + ">"
        value += rendered + markup(child.tail)
    return value


def validate_coverage(value):
    body = core.pdfmetrics.getFont("MR").face.charToGlyph
    bold = core.pdfmetrics.getFont("MRBold").face.charToGlyph
    symbols = core.pdfmetrics.getFont("Symbols").face.charToGlyph
    circled = core.pdfmetrics.getFont("Circled").face.charToGlyph
    missing = []
    fallback = []
    for character in sorted(set(value), key=ord):
        if character.isspace():
            continue
        if character in CIRCLED_SYMBOLS:
            okay, font = circled.get(ord(character)), "Circled"
        elif character in MATH_SYMBOLS:
            okay, font = symbols.get(ord(character)), "Symbols"
        else:
            okay, font = body.get(ord(character)) and bold.get(ord(character)), None
        if not okay:
            missing.append(f"U+{ord(character):04X}")
        elif font:
            cmap = circled if font == "Circled" else symbols
            fallback.append({"character": character, "codepoint": f"U+{ord(character):04X}",
                             "font": font, "glyph_id": cmap[ord(character)]})
    require(not missing, "missing glyphs: " + str(missing))
    return fallback


def validate_render_clone(data):
    require(sha(data["xml"]) == SOURCE_SHA, "source bytes changed after load")
    restored = deepcopy(data["root"])
    framing = restored.find("header/p[@data-kind='original']")
    require(framing is not None and framing.text == PDF_FRAMING and len(framing) == 0,
            "render framing changed after load")
    framing.text = ORIGINAL_FRAMING
    require(ET.tostring(restored) == ET.tostring(ET.fromstring(data["xml"])),
            "render clone changed content beyond the authorized header")


class ModuleStory(core.XMLStory):
    def __init__(self, data):
        super().__init__(data)
        self.available_width = core.CONTENT_WIDTH
        self.cell_mode = False
        self.table_records, self.metadata_records = [], []

    def walk(self, node):
        if node.tag == "li" and any(child.tag not in core.INLINE for child in node):
            self.mixed_list_item(node)
        elif node.tag in LEAVES:
            style = node.tag if node.tag in {"h1", "h2", "h3", "h4", "h5"} else "p"
            if node.tag == "li":
                style = "li"
            elif self.cell_mode:
                style = "cell"
            elif node.tag in {"figcaption", "nav"}:
                style = "small"
            if node.tag == "p" and len(node) == 1 and node[0].tag == "a" and self.story:
                self.story[-1].keepWithNext = True
            rendered = inline(node)
            if node.tag == "li":
                rendered = "• " + rendered
            self.story.append(self.paragraph(rendered, core.logical(node), style,
                                             self.ids_for(node, True)))
            if node.tag == "p" and re.fullmatch(r"[ⓐ-ⓗ]", core.logical(node).strip()):
                self.story[-1].keepWithNext = True
        else:
            for anchor in self.ids_for(node):
                self.story.append(core.Anchor(anchor, self.positions))
            if node.tag == "img":
                self.image(node)
            elif node.tag == "table":
                self.table(node)
            elif node.tag == "dl":
                self.metadata(node)
            elif node.tag == "figure":
                require(not (node.text or "").strip(), "unexpected figure text")
                for index, child in enumerate(node):
                    self.walk(child)
                    if index + 1 < len(node) and node[index + 1].tag == "figcaption":
                        self.story[-1].keepWithNext = True
            elif node.tag in CONTAINERS and ((node.text or "").strip()
                                              or any(child.tag in core.INLINE for child in node)):
                self.mixed_container(node)
            elif node.tag in CONTAINERS:
                require(not (node.text or "").strip(), "unexpected container text")
                for child in node:
                    self.walk(child)
                    require(not (child.tail or "").strip(), "unexpected block tail")
            else:
                raise ValueError("unsupported PDF block: " + node.tag)
        if node.get("data-source"):
            label = "Source: " + node.get("data-source")
            if self.story:
                self.story[-1].keepWithNext = True
            self.story.append(self.paragraph(markup(label), label, "source"))

    def mixed_container(self, node):
        """Preserve an inline run on either side of a real block child."""
        run = ET.Element("p")
        run.text = node.text

        def flush(keep=False):
            nonlocal run
            if core.logical(run).strip():
                paragraph = self.paragraph(inline(run), core.logical(run), "p",
                                           self.ids_for(run, True))
                paragraph.keepWithNext = keep
                self.story.append(paragraph)
            run = ET.Element("p")

        for child in node:
            if child.tag in core.INLINE:
                run.append(deepcopy(child))
            else:
                flush(keep=True)
                self.walk(child)
                run.text = child.tail
        flush()

    def mixed_list_item(self, node):
        for anchor in self.ids_for(node):
            self.story.append(core.Anchor(anchor, self.positions))
        lead = ET.Element("p")
        lead.text = node.text
        reached_block = False
        for child in node:
            if child.tag in core.INLINE:
                require(not reached_block, "unexpected mixed list inline after block")
                lead.append(deepcopy(child))
            else:
                if not reached_block and core.logical(lead).strip():
                    paragraph = self.paragraph("• " + inline(lead), core.logical(lead), "li")
                    paragraph.keepWithNext = True
                    self.story.append(paragraph)
                reached_block = True
                self.walk(child)
                require(not (child.tail or "").strip(), "unexpected mixed list tail")

    def image(self, node):
        src = node.get("src", "")
        require(src.startswith("../assets/"), "unexpected image route")
        path = src[3:]
        require(path in self.data["assets"], "unlisted source image")
        filename = assembly.safe_path(self.data["base"], path)
        with core.PILImage.open(filename) as source:
            width, height = source.size
            source.verify()
        scale = min(self.available_width / width, 355 / height, .85)
        image = core.Image(str(filename), width=width * scale, height=height * scale)
        image.hAlign = "CENTER"
        image.keepWithNext = True
        before, after = core.Spacer(1, 8), core.Spacer(1, 8)
        before.keepWithNext = after.keepWithNext = True
        alt = "आकृतीचे वर्णन: " + node.get("alt")
        self.story.extend([before, image, after, self.paragraph(markup(alt), alt, "small")])
        self.image_records.append({
            "path": path, "width_points": width * scale, "height_points": height * scale,
            "available_width_points": self.available_width, "inside_table": self.cell_mode,
        })

    def cell(self, cell, width):
        require(all(child.tag in core.INLINE for child in cell), "unsupported table cell block")
        actual = core.logical(cell).strip()
        anchors = self.ids_for(cell, True)
        if not actual:
            require(not anchors, "empty table cell may not hide IDs")
            return ""
        return self.paragraph(inline(cell), actual,
                              "cellhead" if cell.tag == "th" else "cell", anchors)

    def table(self, node):
        for caption in node.findall("caption"):
            self.walk(caption)
            self.story[-1].keepWithNext = True
        rows = list(node.iter("tr"))
        columns = len(rows[0])
        require(columns in {2, 3, 4} and all(len(row) == columns for row in rows),
                "irregular table")
        fractions = {2: (.25, .75), 3: (.18, .34, .48),
                     4: (.40, .20, .19, .21)}[columns]
        widths = [self.available_width * fraction for fraction in fractions]
        cells = [[self.cell(cell, widths[index] - 14) for index, cell in enumerate(row)]
                 for row in rows]
        headers = len(node.findall("thead/tr"))
        table = core.Table(cells, colWidths=widths, repeatRows=headers,
                           hAlign="LEFT", splitByRow=1)
        commands = [
            ("FONTNAME", (0, 0), (-1, -1), "MR"),
            ("GRID", (0, 0), (-1, -1), .5, core.colors.HexColor("#93a8b4")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]
        for row_index, row in enumerate(rows):
            for column_index, cell in enumerate(row):
                if cell.tag == "th":
                    commands.extend([
                        ("BACKGROUND", (column_index, row_index), (column_index, row_index),
                         core.colors.HexColor("#e7f0f4")),
                        ("FONTNAME", (column_index, row_index), (column_index, row_index), "MRBold"),
                    ])
        table.setStyle(core.TableStyle(commands))
        self.story.extend([table, core.Spacer(1, 10)])
        self.table_records.append({
            "id": node.get("id"), "rows": len(rows), "columns": columns,
            "header_rows": headers, "column_widths_points": widths,
            "cell_logical_text": [[core.logical(cell).strip() for cell in row] for row in rows],
        })

    def metadata(self, node):
        require([item.tag for item in node] == ["dt", "dd"] * 4, "unexpected metadata")
        for index in range(0, len(node), 2):
            term, value = node[index:index + 2]
            actual = core.logical(term).strip() + ": " + core.logical(value).strip()
            anchors = self.ids_for(term, True) + self.ids_for(value, True)
            self.story.append(self.paragraph("<b>" + inline(term) + "</b>: " + inline(value),
                                             actual, "small", anchors))
            self.metadata_records.append({"term": core.logical(term).strip(),
                                          "value": core.logical(value).strip()})


def module_styles():
    styles = core.styles()
    styles["h5"] = core.ParagraphStyle("h5", parent=styles["h4"], fontSize=10.2,
                                       leading=16, leftIndent=10, spaceBefore=8)
    styles["li"] = core.ParagraphStyle("li", parent=styles["p"], leftIndent=14,
                                       firstLineIndent=-10, spaceAfter=5)
    return styles


def render_pdf(data):
    validate_render_clone(data)
    font_records = register_fonts()
    all_text = "".join(data["root"].itertext()) + "".join(
        node.get("alt", "") for node in data["root"].iter())
    fallback = validate_coverage(all_text)
    story = ModuleStory(data)
    story.styles = module_styles()
    flowables = story.compose()
    stream = BytesIO()
    document = core.SimpleDocTemplate(
        stream, pagesize=core.A4, leftMargin=core.MARGIN, rightMargin=core.MARGIN,
        topMargin=core.MARGIN + 7, bottomMargin=core.MARGIN + 6,
        title="फलनांचे आलेख | A20-m81374 | PDF reading draft",
        author="Marathi STEM bridge workflow", pageCompression=1,
    )

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("MR", 8)
        canvas.setFillColor(core.colors.HexColor("#536570"))
        canvas.drawString(core.MARGIN, 24, UNIT + " | XML reading copy")
        canvas.drawRightString(core.WIDTH - core.MARGIN, 24, str(doc.page))
        canvas.restoreState()

    def canvas(*args, **kwargs):
        return core.Canvas(*args, **dict(kwargs, invariant=True, pdfVersion=(1, 7),
                                         initialFontName="MR", initialFontSize=10))

    document.build(flowables, onFirstPage=footer, onLaterPages=footer, canvasmaker=canvas)
    require(set(story.positions) == set(data["ids"]), "not every XML identity was drawn")
    writer = core.PdfWriter(clone_from=BytesIO(stream.getvalue()))
    writer.pdf_header = "%PDF-1.7"
    writer.root_object[core.NameObject("/Lang")] = core.TextStringObject("mr-Deva-IN")
    for anchor, page in story.positions.items():
        writer.add_named_destination(anchor, page)
    writer.add_attachment(UNIT + ".xml", data["xml"])
    final = BytesIO()
    writer.write(final)
    raw = final.getvalue()
    structure = core.inspect_pdf(raw, data["ids"])
    require(structure["image_placements"] == len(story.image_records) == 149,
            "image placement drift")
    receipt = {
        "schema": 1, "unit": UNIT, "locale": "mr-Deva-IN", "result": "PASS",
        "status": "PASS structural checks; visual review separate",
        "method": "Direct accepted assembly XML to ReportLab PDF; no HTML/CSS/browser input",
        "source_sha256": sha(data["xml"]),
        "assembly_receipt_sha256": sha(data["assembly_receipt_raw"]),
        "assembly_builder_sha256": ASSEMBLY_BUILDER_SHA,
        "independent_source_oracle_sha256": PRIMARY_SOURCE_TEST_SHA,
        "builder_sha256": sha(Path(__file__).read_bytes()),
        "immutable_pdf_helper_sha256": HELPER_SHA,
        "pin_validator_sha256": sha(Path(core.pins.__file__).read_bytes()),
        "pdf_sha256": sha(raw), "pdf_bytes": len(raw),
        "attached_xml_sha256": sha(data["xml"]),
        "input_pins": data["assembly_receipt"]["inputs"],
        "pinned_inputs_checked": 954, "pinned_input_bytes": 13527010,
        "python": platform.python_version(), "reportlab": core.reportlab.Version,
        "uharfbuzz": core.hb.__version__, "fonts": font_records,
        "fallback_glyphs": fallback,
        "shaping_binaries": [{"path": str(path), "sha256": sha(path.read_bytes())}
                             for path in sorted(Path(core.hb.__file__).parent.glob("*.pyd"))],
        "source_elements_per_locale": 7223, "source_mathml": 481,
        "source_blocks": 380, "canonical_ids": 1366,
        "assembly_only_ids": list(ASSEMBLY_ONLY_IDS), "xml_ids": data["ids"],
        "source_exercises": 255, "source_supplied_answers": 141,
        "explicit_source_answer_omissions": 114, "math_checks": 685,
        "role_census": dict(sorted(data["roles"].items())),
        "anchor_pages_zero_based": story.positions,
        "assets": data["asset_records"], "image_geometry": story.image_records,
        "source_link_policy": {"localized_same_module": 6, "external_outside_module": 8,
                               "optional_external_resource": 1},
        "rendered_links": {"internal": len(data["local_links"]), "https": len(data["urls"])},
        "tables": story.table_records,
        "linear_source_table_adaptations": data["assembly_receipt"]["table_adaptations"],
        "metadata": story.metadata_records, "empty_rating_cells": 9,
        "logical_paragraphs": len(story.text_records),
        "logical_text_sha256": sha("\n".join(story.text_records).encode("utf-8")),
        "header_transformation": data["header_transformation"], "structure": structure,
        "not_claimed": [
            "HTML visual QA; browser policy block remains unresolved",
            "PDF/UA or tagged-PDF conformance", "PDF/A conformance",
            "universal text extraction", "native-speaker or mathematics-teacher approval",
            "complete A20 book", "five-book completion",
        ],
        "visual_review": "Not asserted by builder; see qa/A20-m81374-pdf-builder-review.md",
    }
    return raw, receipt


def build(base=BASE):
    data = load_inputs(base)
    raw, receipt = render_pdf(data)
    core.pins.write_outputs([
        (assembly.safe_path(data["base"], f"output/pdf/{UNIT}.pdf"), raw),
        (assembly.safe_path(data["base"], f"qa/{UNIT}-pdf-build-receipt.json"),
         assembly.json_bytes(receipt)),
    ])
    return receipt


if __name__ == "__main__":
    result = build()
    print(json.dumps({key: result[key] for key in ("unit", "pdf_sha256", "pdf_bytes", "structure")},
                     ensure_ascii=False, indent=2))
