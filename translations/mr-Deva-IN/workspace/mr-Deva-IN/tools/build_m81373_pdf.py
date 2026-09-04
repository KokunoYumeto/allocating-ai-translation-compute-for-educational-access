"""Standalone m81373 reading-copy PDF directly from the released assembly XML.

The immutable build_pdf.py supplies fonts, shaping, ActualText paragraphs and
layout primitives. This module adds general source tables, nested list items,
metadata, and verified fallback symbols. It never reads HTML/CSS or a browser.
Run with Python -B. Existing bridge PDFs and all source files remain untouched.
"""
from collections import Counter
from copy import deepcopy
from io import BytesIO
import json
from pathlib import Path
import platform
import re
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape, quoteattr

import assemble_m81373 as assembly
import build_pdf as core


BASE = Path(__file__).resolve().parents[1]
UNIT = "A20-m81373"
SOURCE_SHA = "4a47646ee5129394213e7576d23356dbfc603c6a956dcbfaf45d90e3a1fe82fa"
HELPER_SHA = "c54d8571feb262fcce90d37dbe9d02fcdf9b39246fbed739ce9992f1185afc90"
ASSEMBLY_RECEIPT_SHA = "3141b0a206675ee56968f09f19e727f7fad82f2cfa940e28434ed8a0543f3d29"
TABLE_ROWS = (3, 3, 6, 6, 4, 4, 5, 7, 5, 7, 4)
SYMBOLS = frozenset("′″⇒≠≤□")
ORIGINAL_FRAMING = "स्रोताच्या क्रमातील एकत्रित अनुवाद-मसुदा. मूळ शिकवणी, सोडवलेली उदाहरणे, सराव, स्रोत-उत्तरे, स्वमूल्यमापन आणि शब्दसूची येथे एकत्र केली आहेत. नव्याने जोडलेली उत्तरे व स्पष्टीकरणे स्वतंत्रपणे चिन्हांकित आहेत. हा वाचकाच्या मांडणीला मान्यता मिळालेला दस्तऐवज नाही; संपूर्ण पुस्तक किंवा पाच-पुस्तकांचा कार्यप्रवाह पूर्ण झाल्याचा दावा नाही."
PDF_FRAMING = "स्रोताच्या क्रमातील स्वतंत्र PDF वाचन-मसुदा. मूळ शिकवणी, सोडवलेली उदाहरणे, सराव, स्रोत-उत्तरे, स्वमूल्यमापन आणि शब्दसूची येथे एकत्र केली आहेत. नव्याने जोडलेली उत्तरे व स्पष्टीकरणे स्वतंत्रपणे चिन्हांकित आहेत. ही आशय आणि मांडणी तपासण्यासाठीची PDF प्रत आहे; संपूर्ण पुस्तक किंवा पाच-पुस्तकांचा कार्यप्रवाह पूर्ण झाल्याचा दावा नाही."
require = core.pins.require
sha = core.pins.sha


def read_json(path):
    raw = path.read_bytes()
    return json.loads(raw, object_pairs_hook=assembly.object_pairs), raw


def source_table_shapes(root):
    return [{"id": n.get("id"), "rows": len(list(n.iter("tr"))),
             "columns": [len(tr) for tr in n.iter("tr")],
             "header_rows": len(n.findall("thead/tr"))} for n in root.iter("table")]


def load_inputs(base=BASE):
    base = Path(base).resolve()
    require(sha((base/"tools/build_pdf.py").read_bytes()) == HELPER_SHA, "immutable PDF helper changed")
    receipt, receipt_raw = read_json(base/"qa/A20-m81373-assembly-receipt.json")
    require(sha(receipt_raw) == ASSEMBLY_RECEIPT_SHA, "released assembly receipt changed")
    require(len(receipt["inputs"]) == 339, "expected all 339 assembly input pins")
    for path, record in receipt["inputs"].items():
        raw = assembly.safe_path(base, path).read_bytes()
        require((len(raw), sha(raw)) == (record["bytes"], record["sha256"]), "assembly input drift: "+path)
    raw = assembly.safe_path(base, receipt["output"]["path"]).read_bytes()
    require(sha(raw) == SOURCE_SHA == receipt["output"]["sha256"], "released assembly XML changed")
    require(len(raw) == receipt["output"]["bytes"], "assembly byte count drift")
    # This is the assembler's pure in-memory reconstruction, never its writer.
    rebuilt, rebuilt_receipt = assembly.Assembly(base).build()
    require(rebuilt == raw and rebuilt_receipt == receipt_raw, "assembly cannot be exactly reproduced")
    core.pins.validate_text(raw.decode("utf-8"), "assembly")
    require(b"<!DOCTYPE" not in raw and b"<!ENTITY" not in raw, "XML declarations prohibited")
    source = ET.fromstring(raw)
    require(source.tag == "article" and source.get("id") == UNIT and source.get("lang") == "mr-Deva-IN",
            "wrong PDF source identity")
    ids = assembly.source_ids(source)
    require(len(ids) == len(set(ids)) == 664, "664 unique XML IDs required")
    canonical = set(receipt["canonical_id_order"])
    require(len(canonical) == 625 and [i for i in ids if i in canonical] == receipt["canonical_id_order"],
            "canonical ID order drift")
    checks = [n for n in source.iter() if n.get("data-check")]
    require(len(checks) == 437 and {n.get("data-check"): assembly.text(n) for n in checks} == receipt["expected_math"],
            "437 mathematical strings changed")
    selectors = [n.get("data-source") for n in source.iter() if n.get("data-source")]
    require(selectors == [n["locator"] for n in receipt["selection_order"]] and len(selectors) == 134,
            "134 source selections changed")
    require(receipt["counts"]["source_exercises"] == 84 and receipt["counts"]["source_supplied_answers"] == 55
            and receipt["counts"]["authored_answers_to_source_omissions"] == 29, "answer classification changed")
    shapes = source_table_shapes(source)
    require(tuple(n["rows"] for n in shapes) == TABLE_ROWS, "source table row drift")
    require([n["header_rows"] for n in shapes] == [0, 0]+[1]*9, "source table header drift")
    require(all(n["columns"] == [2]*n["rows"] for n in shapes[:-1])
            and shapes[-1]["columns"] == [4]*4, "table columns changed")
    rating = source.find(".//table[@id='MR-BRIDGE-007--mr-checklist']")
    require([core.logical(n).strip() for n in rating.iter("td")] == ["□"]*9, "ratings must be unfilled")
    metadata = source.find("header/dl")
    require([n.tag for n in metadata] == ["dt", "dd"]*4, "metadata pairs changed")
    allowed = core.INLINE | core.CONTAINERS | core.LEAVES | {"table", "thead", "tbody", "tr", "th", "td", "img", "dl", "dt", "dd"}
    require(all(n.tag in allowed for n in source.iter()), "unsupported module element")
    local_links, urls = [], []
    for n in source.iter("a"):
        href = n.get("href", "")
        if href.startswith("#"):
            require(href[1:] in ids, "unresolved local PDF link")
            local_links.append(href[1:])
        else:
            require(href.startswith("https://"), "unsafe PDF link")
            urls.append(href)
    asset_records = []
    require(len(receipt["assets"]) == 28, "28 pinned canonical assets required")
    for path, record in receipt["assets"].items():
        image = assembly.safe_path(base, path).read_bytes()
        require(record["mime"] == "image/jpeg" and image.startswith(b"\xff\xd8\xff"), "invalid canonical JPEG")
        require((len(image), sha(image)) == (record["bytes"], record["sha256"]), "asset pin mismatch")
        require(path in receipt["inputs"], "asset missing from input pins")
        asset_records.append(dict(record, path=path))
    images = list(source.iter("img"))
    require(len(images) == 28 and {n.get("src") for n in images} == {"../"+p for p in receipt["assets"]},
            "image routes/uses changed")
    require(sum(r["bytes"] for r in asset_records) == 1551848, "canonical asset byte count changed")
    require(all(n.get("alt", "").strip() for n in images), "empty image description")
    root = deepcopy(source)
    paragraph = root.find("header/p[@data-kind='original']")
    require(paragraph is not None and len(paragraph) == 0 and paragraph.text == ORIGINAL_FRAMING,
            "unreviewed header framing")
    paragraph.text = PDF_FRAMING
    transform = {"path": "article/header/p[@data-kind='original'][1]", "kind": "render-clone-only authored framing",
                 "original": ORIGINAL_FRAMING, "rendered": PDF_FRAMING,
                 "all_other_XML_content": "unchanged", "original_XML_attached": True}
    return {"unit": UNIT, "base": base, "root": root, "original_root": source, "xml": raw,
            "assembly_receipt": receipt, "assembly_receipt_raw": receipt_raw, "ids": ids,
            "assets": receipt["assets"], "asset_records": asset_records, "math_count": 437,
            "local_links": local_links, "urls": urls, "source_tables": shapes,
            "header_transformation": transform}


def markup(text):
    def word(match):
        value = match.group(0)
        if set(value) & SYMBOLS:
            # ReportLab 4.4.9 shapeFragWord shapes a complete space-delimited
            # word with its first font. Per-character fallback therefore emits
            # missing glyphs for 5-prime-4-double-prime after a Nirmala digit.
            # Keep the complete symbol-bearing word in verified Cambria.
            cmap = core.pdfmetrics.getFont("Symbols").face.charToGlyph
            require(all(cmap.get(ord(c)) for c in value), "symbol-word glyph missing: "+value)
            return '<font name="Symbols">'+escape(value)+'</font>'
        return escape(value)
    return re.sub(r"\S+", word, core.normalized(text))


def inline(node):
    value = markup(node.text)
    for child in node:
        require(child.tag in core.INLINE, "unsupported inline XML: "+child.tag)
        rendered = inline(child)
        if child.tag == "br":
            rendered = "<br/>"
        elif child.tag == "a":
            href = child.get("href", "")
            require(href.startswith(("https://", "#")), "unsafe link")
            rendered = "<link href="+quoteattr(href)+' color="#165c78">'+rendered+"</link>"
        elif child.tag in {"b", "strong", "dfn"}:
            rendered = "<b>"+rendered+"</b>"
        elif child.tag in {"sup", "sub"}:
            rendered = "<"+child.tag+">"+rendered+"</"+child.tag+">"
        value += rendered + markup(child.tail)
    return value


def validate_coverage(value):
    body = core.pdfmetrics.getFont("MR").face.charToGlyph
    bold = core.pdfmetrics.getFont("MRBold").face.charToGlyph
    symbols = core.pdfmetrics.getFont("Symbols").face.charToGlyph
    missing = []
    for character in set(value):
        if character.isspace():
            continue
        if character in SYMBOLS:
            okay = symbols.get(ord(character))
        else:
            okay = body.get(ord(character)) and bold.get(ord(character))
        if not okay:
            missing.append(f"U+{ord(character):04X}")
    require(not missing, "missing glyphs: "+str(sorted(missing)))
    return [{"character": c, "codepoint": f"U+{ord(c):04X}", "font": "Symbols",
             "glyph_id": symbols[ord(c)]} for c in sorted(set(value) & SYMBOLS)]


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
        if node.tag == "li" and any(c.tag not in core.INLINE for c in node):
            for anchor in self.ids_for(node):
                self.story.append(core.Anchor(anchor, self.positions))
            lead = ET.Element("p")
            lead.text = node.text
            reached_block = False
            for child in node:
                if child.tag in core.INLINE:
                    require(not reached_block, "unexpected mixed list tail")
                    lead.append(deepcopy(child))
                else:
                    if not reached_block:
                        self.walk(lead)
                        self.story[-1].keepWithNext = True
                    reached_block = True
                    self.walk(child)
                    require(not (child.tail or "").strip(), "unexpected list tail text")
        elif node.tag in core.LEAVES:
            style = node.tag if node.tag in {"h1", "h2", "h3", "h4"} else "p"
            if self.cell_mode:
                style = "cell"
            elif node.tag in {"figcaption", "nav"}:
                style = "small"
            if node.tag == "p" and len(node) == 1 and node[0].tag == "a" and self.story:
                self.story[-1].keepWithNext = True
            self.story.append(self.paragraph(inline(node), core.logical(node), style, self.ids_for(node, True)))
            # A standalone subpart label introduces the following calculation.
            # Keep it with that content without changing the preserved XML text.
            if node.tag == "p" and re.fullmatch(r"\([a-z]\)", core.logical(node).strip()):
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
                for i, child in enumerate(node):
                    self.walk(child)
                    if i+1 < len(node) and node[i+1].tag == "figcaption":
                        self.story[-1].keepWithNext = True
            elif node.tag in core.CONTAINERS:
                require(not (node.text or "").strip(), "unexpected container text")
                for child in node:
                    self.walk(child)
                    require(not (child.tail or "").strip(), "unexpected block tail")
            else:
                raise ValueError("unsupported PDF block: "+node.tag)
        if node.get("data-source"):
            label = "Source: "+node.get("data-source")
            if self.story:
                self.story[-1].keepWithNext = True
            self.story.append(self.paragraph(markup(label), label, "source"))

    def image(self, node):
        src = node.get("src", "")
        require(src.startswith("../assets/"), "unexpected image route")
        path = src[3:]
        require(path in self.data["assets"], "unlisted source image")
        filename = assembly.safe_path(self.data["base"], path)
        with core.PILImage.open(filename) as source:
            width, height = source.size
            source.verify()
        scale = min(self.available_width/width, (220 if self.cell_mode else 355)/height, .85)
        image = core.Image(str(filename), width=width*scale, height=height*scale)
        image.hAlign = "CENTER"
        image.keepWithNext = True
        before, after = core.Spacer(1, 3 if self.cell_mode else 8), core.Spacer(1, 4 if self.cell_mode else 8)
        before.keepWithNext = after.keepWithNext = True
        alt = "आकृतीचे वर्णन: "+node.get("alt")
        self.story.extend([before, image, after, self.paragraph(markup(alt), alt, "small")])
        self.image_records.append({"path": path, "width_points": width*scale, "height_points": height*scale,
                                   "available_width_points": self.available_width, "inside_table": self.cell_mode})

    def cell(self, cell, width):
        if all(n.tag in core.INLINE for n in cell):
            return self.paragraph(inline(cell), core.logical(cell), "cellhead" if cell.tag == "th" else "cell",
                                  self.ids_for(cell, True))
        require(not (cell.text or "").strip(), "unreviewed mixed cell prefix")
        outer, old_width, old_mode = self.story, self.available_width, self.cell_mode
        self.story, self.available_width, self.cell_mode = [], width, True
        for anchor in self.ids_for(cell):
            self.story.append(core.Anchor(anchor, self.positions))
        for child in cell:
            require(child.tag in {"figure", "div", "p"}, "unsupported table cell block")
            self.walk(child)
            require(not (child.tail or "").strip(), "unreviewed mixed cell tail")
        if self.story:
            self.story[-1].keepWithNext = False
        result = core.pack_groups(self.story)
        self.story, self.available_width, self.cell_mode = outer, old_width, old_mode
        return result

    def table(self, node):
        for caption in node.findall("caption"):
            self.walk(caption)
            self.story[-1].keepWithNext = True
        rows = list(node.iter("tr"))
        columns = len(rows[0])
        require(columns in {2, 4} and all(len(n) == columns for n in rows), "irregular table")
        fractions = (.40, .20, .19, .21) if columns == 4 else (.38, .62)
        if node.get("id", "").endswith("daily-counts"):
            fractions = (.5, .5)
        widths = [self.available_width*f for f in fractions]
        cells = [[self.cell(cell, widths[i]-14) for i, cell in enumerate(row)] for row in rows]
        headers = len(node.findall("thead/tr"))
        table = core.Table(cells, colWidths=widths, repeatRows=headers, hAlign="LEFT", splitByRow=1)
        commands = [("FONTNAME", (0, 0), (-1, -1), "MR"),
                    ("GRID", (0, 0), (-1, -1), .5, core.colors.HexColor("#93a8b4")),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]
        if headers:
            commands.append(("BACKGROUND", (0, 0), (-1, headers-1), core.colors.HexColor("#e7f0f4")))
        table.setStyle(core.TableStyle(commands))
        self.story.extend([table, core.Spacer(1, 10)])
        self.table_records.append({"id": node.get("id"), "rows": len(rows), "columns": columns,
                                   "header_rows": headers, "column_widths_points": widths,
                                   "cell_logical_text": [[core.logical(c).strip() for c in row] for row in rows]})

    def metadata(self, node):
        require([n.tag for n in node] == ["dt", "dd"]*4, "unexpected metadata")
        for index in range(0, len(node), 2):
            term, value = node[index:index+2]
            actual = core.logical(term).strip()+": "+core.logical(value).strip()
            anchors = self.ids_for(term, True)+self.ids_for(value, True)
            self.story.append(self.paragraph("<b>"+inline(term)+"</b>: "+inline(value), actual, "small", anchors))
            self.metadata_records.append({"term": core.logical(term).strip(), "value": core.logical(value).strip()})


def render_pdf(data):
    validate_render_clone(data)
    font_records = core.register_fonts()
    all_text = "".join(data["root"].itertext())+"".join(n.get("alt", "") for n in data["root"].iter())
    fallback = validate_coverage(all_text)
    story = ModuleStory(data)
    flowables = story.compose()
    stream = BytesIO()
    doc = core.SimpleDocTemplate(stream, pagesize=core.A4, leftMargin=core.MARGIN, rightMargin=core.MARGIN,
                                 topMargin=core.MARGIN+7, bottomMargin=core.MARGIN+6,
                                 title="संबंध आणि फलने | A20-m81373 | PDF reading draft",
                                 author="Marathi STEM bridge workflow", pageCompression=1)
    def footer(canvas, document):
        canvas.saveState()
        canvas.setFont("MR", 8)
        canvas.setFillColor(core.colors.HexColor("#536570"))
        canvas.drawString(core.MARGIN, 24, UNIT+" | XML reading copy")
        canvas.drawRightString(core.WIDTH-core.MARGIN, 24, str(document.page))
        canvas.restoreState()
    def canvas(*args, **kwargs):
        return core.Canvas(*args, **dict(kwargs, invariant=True, pdfVersion=(1, 7), initialFontName="MR", initialFontSize=10))
    doc.build(flowables, onFirstPage=footer, onLaterPages=footer, canvasmaker=canvas)
    require(set(story.positions) == set(data["ids"]), "not every XML identity was drawn")
    writer = core.PdfWriter(clone_from=BytesIO(stream.getvalue()))
    writer.pdf_header = "%PDF-1.7"
    writer.root_object[core.NameObject("/Lang")] = core.TextStringObject("mr-Deva-IN")
    for anchor, page in story.positions.items():
        writer.add_named_destination(anchor, page)
    writer.add_attachment(UNIT+".xml", data["xml"])
    final = BytesIO()
    writer.write(final)
    raw = final.getvalue()
    structure = core.inspect_pdf(raw, data["ids"])
    require(structure["image_placements"] == len(story.image_records) == 28, "image placement drift")
    receipt = {"schema": 1, "unit": UNIT, "locale": "mr-Deva-IN", "result": "PASS",
               "status": "PASS structural checks; visual review separate",
               "method": "Direct released assembly XML to ReportLab PDF; no HTML/CSS/browser input",
               "source_sha256": sha(data["xml"]), "assembly_receipt_sha256": sha(data["assembly_receipt_raw"]),
               "assembly_builder_sha256": sha((data["base"]/"tools/assemble_m81373.py").read_bytes()),
               "builder_sha256": sha(Path(__file__).read_bytes()), "immutable_pdf_helper_sha256": HELPER_SHA,
               "pin_validator_sha256": sha(Path(core.pins.__file__).read_bytes()),
               "pdf_sha256": sha(raw), "pdf_bytes": len(raw), "attached_xml_sha256": sha(data["xml"]),
               "input_pins": data["assembly_receipt"]["inputs"], "pinned_inputs_checked": 339,
               "python": platform.python_version(), "reportlab": core.reportlab.Version,
               "uharfbuzz": core.hb.__version__, "fonts": font_records, "fallback_glyphs": fallback,
               "shaping_binaries": [{"path": str(p), "sha256": sha(p.read_bytes())}
                                    for p in sorted(Path(core.hb.__file__).parent.glob("*.pyd"))],
               "source_blocks": 134, "canonical_ids": 625, "source_exercises": 84,
               "source_supplied_answers": 55, "authored_answers_to_source_omissions": 29,
               "math_checks": 437, "xml_ids": data["ids"], "anchor_pages_zero_based": story.positions,
               "assets": data["asset_records"], "image_geometry": story.image_records,
               "source_links": {"internal": len(data["local_links"]), "https": len(data["urls"])},
               "tables": story.table_records, "metadata": story.metadata_records,
               "empty_rating_cells": 9, "logical_paragraphs": len(story.text_records),
               "logical_text_sha256": sha("\n".join(story.text_records).encode("utf-8")),
               "header_transformation": data["header_transformation"], "structure": structure,
               "not_claimed": ["HTML visual QA; browser policy block remains unresolved", "PDF/UA or tagged-PDF conformance",
                               "PDF/A conformance", "universal text extraction", "native-teacher approval",
                               "independent whole-module source/math acceptance", "five-book completion"],
               "visual_review": "Not asserted by builder; see qa/A20-m81373-pdf-builder-review.md"}
    return raw, receipt


def build(base=BASE):
    data = load_inputs(base)
    raw, receipt = render_pdf(data)
    core.pins.write_outputs([(assembly.safe_path(data["base"], f"output/pdf/{UNIT}.pdf"), raw),
                             (assembly.safe_path(data["base"], f"qa/{UNIT}-pdf-build-receipt.json"),
                              assembly.json_bytes(receipt))])
    return receipt


if __name__ == "__main__":
    result = build()
    print(json.dumps({k: result[k] for k in ("unit", "pdf_sha256", "pdf_bytes", "structure")}, ensure_ascii=False, indent=2))
