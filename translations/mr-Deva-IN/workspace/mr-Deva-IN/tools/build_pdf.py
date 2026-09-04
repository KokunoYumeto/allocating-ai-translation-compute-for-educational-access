"""Direct structured-XML reading copies; never reads HTML, CSS, or a browser.

Run with bundled Python: python -B mr-Deva-IN/tools/build_pdf.py MR-BRIDGE-007
ReportLab 4.4.9 and uharfbuzz are required. On this workstation the small
shaping dependency is installed only in ignored tmp/pdfs/python-deps.
These PDFs are NOT evidence of HTML visual QA or PDF/UA conformance.
"""
import argparse
from collections import Counter
from io import BytesIO
import json
from pathlib import Path
import platform
import re
import struct
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape, quoteattr

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "tmp/pdfs/python-deps"))
import uharfbuzz as hb
import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (Flowable, Image, PageBreak, Paragraph,
                               SimpleDocTemplate, Spacer, Table, TableStyle)
from PIL import Image as PILImage
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject
import build_unit as pins

SUPPORTED = frozenset({"MR-BRIDGE-006", "MR-BRIDGE-007", "MR-BRIDGE-008"})
FONT_SPECS = {"MR": ("C:/Windows/Fonts/Nirmala.ttc", 0),
              "MRBold": ("C:/Windows/Fonts/Nirmala.ttc", 1),
              "Symbols": ("C:/Windows/Fonts/cambria.ttc", 0)}
WIDTH, HEIGHT = A4
MARGIN = 44
CONTENT_WIDTH = WIDTH - 2 * MARGIN
INLINE = frozenset("span a strong em b i small sup sub code br cite dfn".split())
CONTAINERS = frozenset("article header section div aside figure ul".split())
LEAVES = frozenset("p h1 h2 h3 h4 nav figcaption li caption".split())


class CollectionFont(TTFont):
    """RL's TTC hbFace defaults to index 0; preserve the selected face index."""
    def __init__(self, name, path, index):
        self.collection_index = index
        super().__init__(name, path, subfontIndex=index, shapable=True)

    @property
    def hbFace(self):
        face = super().hbFace  # Initializes RL's private glyph mapping state.
        if not getattr(self, "_indexed_hb_face", False):
            face = self.__hbFace__ = hb.Face(hb.Blob(self.face._ttf_data),
                                           self.collection_index)
            self._indexed_hb_face = True
        return face


def register_fonts():
    records = []
    for name, (filename, index) in FONT_SPECS.items():
        font = CollectionFont(name, filename, index)
        pins.require(font.shapable, "HarfBuzz shaping unavailable")
        fs_type = struct.unpack(">H", font.face.get_table("OS/2")[8:10])[0]
        pins.require(not fs_type & (2 | 0x100 | 0x200), "font embedding/subsetting restricted")
        pdfmetrics.registerFont(font)
        records.append({"name": name, "path": filename, "collection_index": index,
                        "sha256": pins.sha(Path(filename).read_bytes()),
                        "embedding_fsType": fs_type, "shaping": "HarfBuzz"})
    pdfmetrics.registerFontFamily("MR", normal="MR", bold="MRBold",
                                  italic="MR", boldItalic="MRBold")
    return records


def validate_coverage(text):
    body = pdfmetrics.getFont("MR").face.charToGlyph
    bold = pdfmetrics.getFont("MRBold").face.charToGlyph
    symbols = pdfmetrics.getFont("Symbols").face.charToGlyph
    missing = sorted({ord(c) for c in text if not c.isspace()
                      and (not (symbols if c == "□" else body).get(ord(c))
                           or (c != "□" and not bold.get(ord(c))))})
    pins.require(not missing, "missing glyphs: " + str([f"U+{c:04X}" for c in missing]))


def normalized(text):
    return re.sub(r"\s+", " ", text or "")


def logical(node):
    result = normalized(node.text)
    for child in node:
        result += "\n" if child.tag == "br" else logical(child)
        result += normalized(child.tail)
    return result


def text_markup(text):
    return escape(normalized(text)).replace("□", '<font name="Symbols">□</font>')


def inline(node):
    result = text_markup(node.text)
    for child in node:
        pins.require(child.tag in INLINE, "unsupported inline XML: " + child.tag)
        value = inline(child)
        if child.tag == "br":
            value = "<br/>"
        elif child.tag == "a":
            value = "<link href=" + quoteattr(child.get("href")) + ' color="#165c78">' + value + "</link>"
        elif child.tag in {"strong", "b", "dfn"}:
            value = "<b>" + value + "</b>"
        elif child.tag in {"sup", "sub"}:
            value = "<" + child.tag + ">" + value + "</" + child.tag + ">"
        result += value + text_markup(child.tail)
    return result


def load_inputs(unit, base=BASE):
    pins.require(unit in SUPPORTED, "PDF builder is bounded to units 006-008")
    base = Path(base).resolve()
    config, config_raw = pins.read_json(pins.inside(base, f"units/{unit}.json"))
    lock, lock_raw = pins.read_json(pins.inside(base, f"provenance/{unit}.lock.json"))
    raw = pins.inside(base, f"translations/{unit}.xml").read_bytes()
    xml = raw.decode("utf-8")
    pins.validate_text(xml, "translation")
    pins.require("<!DOCTYPE" not in xml and "<!ENTITY" not in xml, "XML entities prohibited")
    root = ET.fromstring(raw)
    pins.require(root.tag == "article" and root.get("id") == unit
                 and root.get("lang") == "mr-Deva-IN", "wrong unit/locale")
    assets = pins.validate_asset_config(config)
    local_links, external_count, images = pins.validate_markup(root, assets)
    ids = [n.get("id") for n in root.iter() if n.get("id")]
    pins.require(len(ids) == len(set(ids)), "duplicate ID")
    pins.require(all(n in ids for n in local_links), "broken local link")
    sources = [n for n in root.iter() if n.get("data-source")]
    selections = lock["source_selections"]
    pins.require([(n.get("data-source"), n.get("id")) for n in sources] ==
                 [(s["locator"], s["target_id"]) for s in selections], "source selection drift")
    pins.require(len(sources) == config["source_count"], "source count drift")
    checks = [n for n in root.iter() if n.get("data-check")]
    pins.require(len(checks) == len({n.get("data-check") for n in checks}), "duplicate math key")
    pins.require({n.get("data-check"): "".join(n.itertext()) for n in checks}
                 == config["expected_math"], "displayed mathematical chain drift")
    pins.require(all(t in "".join(root.itertext()) for t in config["required_terms"]), "term drift")
    for witness in lock["witnesses"]:
        pins.require(pins.sha(pins.inside(base, witness["path"]).read_bytes()) == witness["sha256"],
                     "witness drift: " + witness["path"])
    _, asset_records = pins.load_pinned_assets(assets, lock["witnesses"], base, images)
    allowed = INLINE | CONTAINERS | LEAVES | {"table", "thead", "tbody", "tr", "th", "td", "img"}
    pins.require(all(n.tag in allowed for n in root.iter()), "unsupported PDF XML element")
    return {"unit": unit, "base": base, "root": root, "xml": raw, "config": config,
            "config_raw": config_raw, "lock": lock, "lock_raw": lock_raw, "ids": ids,
            "assets": assets, "asset_records": asset_records, "math_count": len(checks),
            "local_links": local_links, "external_count": external_count}


class ReadingParagraph(Paragraph):
    """No split: preserve logical Unicode ActualText across shaped glyph runs."""
    def __init__(self, markup, style, actual, anchors=(), positions=None):
        super().__init__(markup, style)
        self.actual = actual.strip()
        self.anchors = anchors
        self.positions = positions if positions is not None else {}

    def split(self, availWidth, availHeight):
        return []

    def wrap(self, availWidth, availHeight):
        width, height = super().wrap(availWidth, availHeight)
        pins.require(height <= HEIGHT - 2 * MARGIN - 30, "paragraph cannot fit one page")
        # With splitLongWords disabled, negative extraSpace signals clipped text.
        pins.require(all((getattr(line, "extraSpace", line[0] if isinstance(line, tuple) else 0)
                          >= -0.01) for line in self.blPara.lines),
                     "unbreakable line overflows at width " + str(availWidth) + ": " + self.actual[:140])
        return width, height

    def draw(self):
        for anchor in self.anchors:
            self.canv.bookmarkHorizontalAbsolute(anchor, self.canv._currentMatrix[5] + self.height)
            self.positions[anchor] = self.canv.getPageNumber() - 1
        text = ("\ufeff" + self.actual).encode("utf-16-be").hex().upper()
        self.canv._code.append("/Span << /ActualText <" + text + "> >> BDC")
        super().draw()
        self.canv._code.append("EMC")


class Anchor(Flowable):
    def __init__(self, anchor, positions):
        super().__init__()
        self.anchor, self.positions = anchor, positions
        self.width = self.height = 0
        self.keepWithNext = True

    def draw(self):
        self.canv.bookmarkHorizontalAbsolute(self.anchor, self.canv._currentMatrix[5])
        self.positions[self.anchor] = self.canv.getPageNumber() - 1


class AtomicGroup(Flowable):
    """Small explicit groups cannot be broken by advisory KeepTogether fallback."""
    def __init__(self, children):
        super().__init__()
        self.children = children

    def wrap(self, availWidth, availHeight):
        self.geometry = []
        y = 0
        for child in self.children:
            width, height = child.wrapOn(self.canv, availWidth, availHeight)
            y += child.getSpaceBefore()
            self.geometry.append((child, y, height))
            y += height + child.getSpaceAfter()
        pins.require(y <= HEIGHT - 2 * MARGIN - 30, "atomic group exceeds page height")
        self.width, self.height = availWidth, y
        return availWidth, y

    def draw(self):
        for child, y, height in self.geometry:
            child.drawOn(self.canv, 0, self.height - y - height)


def pack_groups(flowables):
    result, pending = [], []
    for flowable in flowables:
        if pending or flowable.getKeepWithNext():
            pending.append(flowable)
            if not flowable.getKeepWithNext():
                result.append(AtomicGroup(pending))
                pending = []
        else:
            result.append(flowable)
    pins.require(not pending, "unterminated PDF layout group")
    return result


def styles():
    base = dict(fontName="MR", fontSize=10.8, leading=17.7, shaping=1,
                splitLongWords=0, spaceShrinkage=0, spaceAfter=7,
                textColor=colors.HexColor("#172e3b"))
    result = {"p": ParagraphStyle("body", **base)}
    for tag, size, leading in [("h1", 22, 29), ("h2", 15, 22), ("h3", 12.5, 19), ("h4", 11, 18)]:
        opts = dict(base, fontName="MRBold", fontSize=size, leading=leading,
                    spaceBefore=12, spaceAfter=7, keepWithNext=True)
        result[tag] = ParagraphStyle(tag, **opts)
    result["small"] = ParagraphStyle("small", **dict(base, fontSize=8.7, leading=14))
    result["source"] = ParagraphStyle("source", **dict(base, fontSize=7.2, leading=11,
                                                       textColor=colors.HexColor("#536570")))
    result["cell"] = ParagraphStyle("cell", **dict(base, fontSize=9.5, leading=15, spaceAfter=0))
    result["cellhead"] = ParagraphStyle("cellhead", parent=result["cell"], fontName="MRBold")
    return result


class XMLStory:
    def __init__(self, data):
        self.data, self.styles = data, styles()
        self.story, self.positions, self.seen = [], {}, set()
        self.text_records, self.image_records = [], []

    def ids_for(self, node, descendants=False):
        ids = []
        for n in node.iter() if descendants else [node]:
            anchor = n.get("id")
            if anchor and anchor not in self.seen:
                ids.append(anchor)
                self.seen.add(anchor)
        return ids

    def paragraph(self, markup, text, style="p", anchors=()):
        self.text_records.append(text.strip())
        return ReadingParagraph(markup, self.styles[style], text, anchors, self.positions)

    def walk(self, node):
        if node.tag in LEAVES:
            sty = node.tag if node.tag in {"h1", "h2", "h3", "h4"} else "p"
            if node.tag in {"figcaption", "nav"}:
                sty = "small"
            if node.tag == "p" and len(node) == 1 and node[0].tag == "a" and self.story:
                self.story[-1].keepWithNext = True
            self.story.append(self.paragraph(inline(node), logical(node), sty,
                                             self.ids_for(node, True)))
        else:
            for anchor in self.ids_for(node):
                self.story.append(Anchor(anchor, self.positions))
            if node.tag == "img":
                asset_id = node.get("src")[6:]
                path = pins.inside(self.data["base"], self.data["assets"][asset_id]["path"])
                with PILImage.open(path) as source:
                    width, height = source.size
                scale = min(CONTENT_WIDTH / width, 355 / height, 0.85)
                drawing = Image(str(path), width=width * scale, height=height * scale)
                drawing.hAlign = "CENTER"
                drawing.keepWithNext = True
                after_image = Spacer(1, 8)
                after_image.keepWithNext = True
                self.story.extend([Spacer(1, 8), drawing, after_image])
                alt = node.get("alt")
                self.story.append(self.paragraph(text_markup("आकृतीचे वर्णन: " + alt),
                                                 "आकृतीचे वर्णन: " + alt, "small"))
                self.story[-1].keepWithNext = True
                self.image_records.append({"id": asset_id, "width_points": width * scale,
                                           "height_points": height * scale})
            elif node.tag == "table":
                self.table(node)
            elif node.tag in CONTAINERS:
                pins.require(not (node.text or "").strip(), "unexpected container text")
                for child in node:
                    self.walk(child)
                    pins.require(not (child.tail or "").strip(), "unexpected block tail text")
            else:
                raise ValueError("unsupported PDF block: " + node.tag)
        if node.get("data-source"):
            label = "Source: " + node.get("data-source")
            if self.story:
                self.story[-1].keepWithNext = True
            self.story.append(self.paragraph(escape(label), label, "source"))

    def table(self, node):
        for caption in node.findall("caption"):
            self.walk(caption)
        rows = []
        for tr in node.iter("tr"):
            row = []
            for cell in tr:
                row.append(self.paragraph(inline(cell), logical(cell),
                                          "cellhead" if cell.tag == "th" else "cell",
                                          self.ids_for(cell, True)))
            rows.append(row)
        pins.require(len(rows) == 4 and all(len(r) == 4 for r in rows), "unexpected self-check shape")
        pins.require([logical(c).strip() for c in node.iter("td")] == ["□"] * 9,
                     "self-check ratings must remain empty")
        table = Table(rows, colWidths=[CONTENT_WIDTH * f for f in (.40, .20, .19, .21)],
                      repeatRows=1, hAlign="LEFT")
        table.setStyle(TableStyle([("FONTNAME", (0, 0), (-1, -1), "MR"),
                                   ("GRID", (0, 0), (-1, -1), .5, colors.HexColor("#93a8b4")),
                                   ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e7f0f4")),
                                   ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                   ("LEFTPADDING", (0, 0), (-1, -1), 7),
                                   ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                                   ("TOPPADDING", (0, 0), (-1, -1), 8),
                                   ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
        self.story.extend([table, Spacer(1, 10)])

    def compose(self):
        self.walk(self.data["root"])
        pins.require(self.seen == set(self.data["ids"]), "unrendered XML IDs")
        self.story.append(PageBreak())
        self.story.append(self.paragraph("XML identity index", "XML identity index", "h2"))
        note = ("Every source and local XML ID is retained below and as a named PDF destination. "
                "The exact UTF-8 XML is attached. This separate XML reading copy does not certify "
                "HTML rendering, PDF/UA accessibility, or native-teacher review.")
        self.story.append(self.paragraph(escape(note), note, "small"))
        ids = self.data["ids"]
        rows = []
        for start in range(0, len(ids), 2):
            row = [self.paragraph(escape(i), i, "source") for i in ids[start:start + 2]]
            rows.append(row + [""] * (2 - len(row)))
        index = Table(rows, colWidths=[CONTENT_WIDTH / 2] * 2, hAlign="LEFT")
        index.setStyle(TableStyle([("FONTNAME", (0, 0), (-1, -1), "MR"),
                                   ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                   ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                   ("TOPPADDING", (0, 0), (-1, -1), 1),
                                   ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
        self.story.append(index)
        return pack_groups(self.story)


def inspect_pdf(raw, expected_ids=()):
    reader = PdfReader(BytesIO(raw))
    pins.require(set(reader.named_destinations) == set(expected_ids), "PDF named destination drift")
    fonts, links, widgets, image_count = {}, 0, 0, 0
    for page in reader.pages:
        for ref in page.get("/Resources", {}).get("/Font", {}).values():
            font = ref.get_object()
            name = str(font.get("/BaseFont"))
            descriptor = font.get("/FontDescriptor")
            pins.require(descriptor is not None, "nonembedded font: " + name)
            descriptor = descriptor.get_object()
            stream = descriptor.get("/FontFile2")
            pins.require(stream and stream.get_object().get_data(), "font bytes missing")
            pins.require(font.get("/ToUnicode"), "font Unicode map missing")
            fonts[name] = {"embedded": True, "to_unicode": True}
        for ref in page.get("/Annots", []):
            annotation = ref.get_object()
            widgets += annotation.get("/Subtype") == "/Widget"
            pins.require(annotation.get("/Subtype") == "/Link", "non-link annotation")
            action = annotation.get("/A")
            if action:
                action = action.get_object()
                pins.require(action.get("/S") == "/URI" and str(action.get("/URI")).startswith("https://"),
                             "unsafe PDF action")
            links += 1
        image_count += sum(ref.get_object().get("/Subtype") == "/Image"
                           for ref in page.get("/Resources", {}).get("/XObject", {}).values())
    pins.require(not widgets and not reader.trailer["/Root"].get("/AcroForm"), "unexpected form/rating state")
    return {"pages": len(reader.pages), "named_destinations": len(reader.named_destinations),
            "embedded_fonts": fonts, "link_annotations": links, "image_placements": image_count,
            "widgets": widgets, "actual_text_spans": sum(p.get_contents().get_data().count(b"/ActualText")
                                                           for p in reader.pages)}


def render_pdf(data):
    font_records = register_fonts()
    all_text = "".join(data["root"].itertext()) + "".join(n.get("alt", "") for n in data["root"].iter())
    validate_coverage(all_text)
    story = XMLStory(data)
    flowables = story.compose()
    stream = BytesIO()
    doc = SimpleDocTemplate(stream, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                            topMargin=MARGIN + 7, bottomMargin=MARGIN + 6,
                            title=data["config"]["title"], author="Marathi STEM bridge workflow",
                            pageCompression=1)

    def page_footer(canvas, document):
        canvas.saveState()
        canvas.setFont("MR", 8)
        canvas.setFillColor(colors.HexColor("#536570"))
        canvas.drawString(MARGIN, 24, data["unit"] + " | XML reading copy")
        canvas.drawRightString(WIDTH - MARGIN, 24, str(document.page))
        canvas.restoreState()

    def canvas_factory(*args, **kwargs):
        return Canvas(*args, **dict(kwargs, invariant=True, pdfVersion=(1, 7),
                                   initialFontName="MR", initialFontSize=10))

    doc.build(flowables, onFirstPage=page_footer, onLaterPages=page_footer, canvasmaker=canvas_factory)
    pins.require(set(story.positions) == set(data["ids"]), "missing drawn anchor")
    writer = PdfWriter(clone_from=BytesIO(stream.getvalue()))
    writer.pdf_header = "%PDF-1.7"
    writer.root_object[NameObject("/Lang")] = TextStringObject("mr-Deva-IN")
    for anchor, page in story.positions.items():
        writer.add_named_destination(anchor, page)
    writer.add_attachment(data["unit"] + ".xml", data["xml"])
    final = BytesIO()
    writer.write(final)
    raw = final.getvalue()
    structure = inspect_pdf(raw, data["ids"])
    pins.require(structure["image_placements"] == len(story.image_records), "image placement drift")
    receipt = {"schema": 1, "unit": data["unit"], "result": "PASS",
               "status": "PASS structural checks; visual review separate",
               "method": "Direct XML to ReportLab PDF with HarfBuzz; no HTML or browser input",
               "source_sha256": pins.sha(data["xml"]), "config_sha256": pins.sha(data["config_raw"]),
               "lock_sha256": pins.sha(data["lock_raw"]), "pdf_sha256": pins.sha(raw),
               "pdf_bytes": len(raw), "builder_sha256": pins.sha(Path(__file__).read_bytes()),
               "pin_validator_sha256": pins.sha(Path(pins.__file__).read_bytes()),
               "python": platform.python_version(), "reportlab": reportlab.Version,
               "uharfbuzz": hb.__version__, "fonts": font_records,
               "shaping_binaries": [{"path": str(p), "sha256": pins.sha(p.read_bytes())}
                                    for p in sorted(Path(hb.__file__).parent.glob("*.pyd"))],
               "source_blocks": data["config"]["source_count"], "math_checks": data["math_count"],
               "xml_ids": data["ids"], "anchor_pages_zero_based": story.positions,
               "assets": data["asset_records"], "image_geometry": story.image_records,
               "pinned_witnesses_checked": len(data["lock"]["witnesses"]),
               "source_links": {"internal": len(data["local_links"]), "https": data["external_count"]},
               "logical_paragraphs": len(story.text_records),
               "logical_text_sha256": pins.sha("\n".join(story.text_records).encode("utf-8")),
               "attached_xml_sha256": pins.sha(data["xml"]), "structure": structure,
               "empty_rating_cells": sum(logical(n).strip() == "□" for n in data["root"].iter("td")),
               "not_claimed": ["HTML visual QA (policy block remains unresolved)", "PDF/UA or tagged-PDF conformance",
                               "PDF/A conformance", "native-teacher review", "interactive self-check storage"],
               "visual_review": "Not asserted by builder; see qa/PDF-builder-review.md"}
    return raw, receipt


def build(unit, base=BASE):
    data = load_inputs(unit, base)
    raw, receipt = render_pdf(data)
    pins.write_outputs([(pins.inside(data["base"], f"output/pdf/{unit}.pdf"), raw),
                        (pins.inside(data["base"], f"qa/{unit}-pdf-build-receipt.json"),
                         (json.dumps(receipt, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))])
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("unit", choices=sorted(SUPPORTED))
    args = parser.parse_args()
    result = build(args.unit)
    print(json.dumps({k: result[k] for k in ("unit", "pdf_sha256", "pdf_bytes", "structure")},
                     ensure_ascii=False, indent=2))
