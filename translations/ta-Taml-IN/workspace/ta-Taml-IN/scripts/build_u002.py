"""Build the separate U002 draft reader and deterministic offline EPUB.

U001 is not rebuilt or modified. CNXML structures not explicitly supported here
fail closed; mathematical source tables remain real tables, never screenshots.
"""
import argparse
import copy
import html
import json
from pathlib import Path
import re
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile

sys.dont_write_bytecode = True
from build import credits, math, sha, xhtml

ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT / "ta-Taml-IN"
SOURCE = LANG / "translation/m81243-fs-id2340048.cnxml"
COMPANION = LANG / "translation/recovery-u002.xhtml"
C = "http://cnx.rice.edu/cnxml"
H = "http://www.w3.org/1999/xhtml"
M = "http://www.w3.org/1998/Math/MathML"
S = "http://www.w3.org/2000/svg"
ESC = html.escape
UNIT = "A00-U002"
SOURCE_ID = "fs-id2340048"
TITLE = "முழு எண்களை மாதிரிகளால் காட்டுதல்"
ASSETS = ("book.css", "u002.css", "fonts/NotoSansTamil.ttf", "fonts/OFL.txt")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def local(node):
    return node.tag.rsplit("}", 1)[-1]


def identity(node):
    return f' id="{ESC(node.get("id"))}"' if node.get("id") else ""


def numbered_figures():
    """This subsection is in Chapter 1; filenames do not encode figure numbers."""
    module = ET.parse(LANG / "provenance/m81243.en.cnxml")
    figures = module.findall(f".//{{{C}}}content//{{{C}}}figure")
    numbered = [n for n in figures if "unnumbered" not in n.get("class", "").split()]
    result = {n.get("id"): f"1.{i}" for i, n in enumerate(numbered, 1)}
    expected = {
        "CNX_BMath_Figure_01_01_002": "1.2",
        "CNX_BMath_Figure_01_01_004": "1.3",
        "CNX_BMath_Figure_01_01_005": "1.4",
    }
    require(all(result.get(k) == v for k, v in expected.items()), "Canonical U002 figure numbering changed")
    return result


class Renderer:
    def __init__(self):
        self.figures = numbered_figures()
        self.media_paths = set()

    def inner(self, node):
        return ESC(node.text or "") + "".join(self.render(n) + ESC(n.tail or "") for n in node)

    def media(self, node):
        images = list(node)
        require(len(images) == 1 and images[0].tag == f"{{{C}}}image", "Expected one local SVG per media")
        image = images[0]
        require(not list(image) and not (image.text or "").strip(), "Unhandled image contents")
        require(image.get("mime-type") == "image/svg+xml", "U002 media must use its translated SVG")
        path = (SOURCE.parent / image.get("src", "")).resolve()
        require(path.is_relative_to(LANG / "assets/u002") and path.is_file(), "Missing or out-of-scope U002 SVG")
        self.media_paths.add(path)
        svg = copy.deepcopy(ET.parse(path).getroot())
        require(svg.tag == f"{{{S}}}svg", "Media root is not SVG")
        title = svg.find(f"{{{S}}}title")
        description = svg.find(f"{{{S}}}desc")
        require(title is not None and description is not None, "SVG needs title and description")
        require(title.get("id") and description.get("id"), "SVG accessible labels need IDs")
        require(node.get("alt"), "Source media needs a Tamil description")
        # The source-faithful strand exposes its exact translated description.
        # Geometry and source asset IDs are retained; this is a rendering copy.
        description.text = node.get("alt")
        svg.set("role", "img")
        svg.set("aria-labelledby", title.get("id") + " " + description.get("id"))
        hint_id = node.get("id") + "-diagram-help"
        return f'<div{identity(node)} class="source-media"><p id="{hint_id}" class="diagram-hint muted">படம் முழுவதும் தெரியாவிட்டால் கிடைமட்டமாக நகர்த்திப் பார்க்கவும். படத்தின் விளக்கம் கீழே உள்ளது.</p><div class="diagram-scroll" role="region" tabindex="0" aria-label="{ESC("".join(title.itertext()))}" aria-describedby="{hint_id}">{xhtml(svg)}</div><p class="media-description muted">{ESC(node.get("alt"))}</p></div>'

    def paragraph(self, node):
        # A CNXML para may contain block media. Splitting it into a paragraph
        # group avoids invalid div-inside-p markup and HTML parser reparenting.
        block = {"media", "table", "figure", "note", "example"}
        if not any(local(n) in block for n in node):
            return f'<p{identity(node)}>{self.inner(node)}</p>'
        parts = []
        pending = ESC(node.text or "")
        for child in node:
            if local(child) in block:
                if pending.strip():
                    parts.append(f"<p>{pending}</p>")
                parts.append(self.render(child))
                pending = ESC(child.tail or "")
            else:
                pending += self.render(child) + ESC(child.tail or "")
        if pending.strip():
            parts.append(f"<p>{pending}</p>")
        return f'<div{identity(node)} class="source-paragraph">{"".join(parts)}</div>'

    def table(self, node):
        table_id = node.get("id")
        require(table_id and node.get("aria-label"), "A source table needs ID and description")
        require(all(local(n) in ("label", "tgroup") for n in node), "Unhandled source table child")
        for label in node.findall(f"{{{C}}}label"):
            require(not list(label) and not (label.text or "").strip(), "Nonempty table labels need explicit rendering")
        groups = node.findall(f"{{{C}}}tgroup")
        require(len(groups) == 1, "Expected one tgroup")
        group = groups[0]
        columns = int(group.get("cols", "0"))
        require(columns == 5, "Review renderer before changing the U002 table shape")
        require(all(local(n) in ("colspec", "thead", "tbody") for n in group), "Unhandled tgroup child")
        colspecs = group.findall(f"{{{C}}}colspec")
        require(len(colspecs) == columns, "Missing table column specifications")
        for i, col in enumerate(colspecs, 1):
            require(col.attrib == {"colnum": str(i), "colname": f"c{i}"} and not list(col), "Unhandled colspec")
        heads = group.findall(f"{{{C}}}thead")
        bodies = group.findall(f"{{{C}}}tbody")
        require(len(heads) == len(bodies) == 1, "Expected one table head and body")
        require(len(heads[0]) == 1, "Multirow column headers need explicit support")
        header_ids = [f"{table_id}-col-{i}" for i in range(1, columns + 1)]

        def row_html(row, index, is_head=False):
            require(row.tag == f"{{{C}}}row", "Unhandled table row element")
            require(set(row.attrib) <= {"valign"} and row.get("valign", "top") == "top", "Unhandled row alignment/span")
            entries = list(row)
            require(len(entries) == columns and all(n.tag == f"{{{C}}}entry" for n in entries), "Table column count mismatch")
            # The place-value name in column 2 identifies each non-total row.
            row_header = f"{table_id}-row-{index}" if not is_head and "".join(entries[1].itertext()).strip() else None
            cells = []
            for i, entry in enumerate(entries):
                require(set(entry.attrib) <= {"align"}, "Unhandled entry attributes/span")
                alignment = entry.get("align", "left")
                require(alignment in ("left", "center", "right"), "Unsupported cell alignment")
                at = f' class="align-{alignment}"'
                if is_head:
                    tag = "th"
                    at += f' id="{header_ids[i]}" scope="col"'
                elif i == 1 and row_header:
                    tag = "th"
                    at += f' id="{row_header}" scope="row" headers="{header_ids[i]}"'
                else:
                    tag = "td"
                    at += f' headers="{header_ids[i]}{" " + row_header if row_header else ""}"'
                cells.append(f"<{tag}{at}>{self.inner(entry)}</{tag}>")
            return "<tr>" + "".join(cells) + "</tr>"

        header = row_html(heads[0][0], 0, True)
        body = "".join(row_html(row, i) for i, row in enumerate(bodies[0], 1))
        hint_id = f"{table_id}-scroll-help"
        return f'''<div class="source-table-group"><p id="{hint_id}" class="table-hint muted">அட்டவணை முழுவதும் தெரியாவிட்டால் கிடைமட்டமாக நகர்த்திப் பார்க்கவும்.</p><div class="table-scroll" role="region" tabindex="0" aria-label="இடமதிப்பு அட்டவணை" aria-describedby="{hint_id}"><table id="{ESC(table_id)}" aria-label="{ESC(node.get('aria-label'))}"><colgroup>{'<col/>' * columns}</colgroup><thead>{header}</thead><tbody>{body}</tbody></table></div></div>'''

    def render(self, node):
        name = local(node)
        if node.tag.startswith("{" + M + "}"):
            return math(node)
        require(node.tag.startswith("{" + C + "}"), f"Unexpected source namespace: {node.tag}")
        if name == "link":
            target = node.get("target-id")
            require(target in self.figures, f"Unresolved source figure link: {target}")
            require(not list(node) and not (node.text or "").strip(), "Unhandled explicit link text")
            return f'<a{identity(node)} href="#{ESC(target)}">படம் {self.figures[target]}</a>'
        if name == "media":
            return self.media(node)
        if name == "table":
            return self.table(node)
        if name == "para":
            return self.paragraph(node)
        if name == "newline":
            require(not list(node) and not (node.text or "").strip(), "Unhandled newline contents")
            return "<br/>"
        if name == "figure":
            require(node.get("id") in self.figures, "Missing numbered figure mapping")
            require(all(local(n) in ("media", "caption") for n in node), "Unhandled figure child")
            captions = node.findall(f"{{{C}}}caption")
            require(len(captions) <= 1, "Multiple figure captions")
            body = "".join(self.render(n) for n in node if local(n) != "caption")
            caption = self.inner(captions[0]) if captions else ""
            return f'<figure{identity(node)}>{body}<figcaption>படம் {self.figures[node.get("id")]}{": " if caption else ""}{caption}</figcaption></figure>'
        if name == "section":
            require(node.get("id") == SOURCE_ID and len(node) and local(node[0]) == "title", "Unexpected source subsection")
            title = f'<h2{identity(node[0])}>{self.inner(node[0])}</h2>'
            body = "".join(self.render(n) + ESC(n.tail or "") for n in list(node)[1:])
            return f'<section{identity(node)} class="page source-faithful"><p class="source-head">மூலநூல் மொழிபெயர்ப்பு · A00 · m81243 · {SOURCE_ID}</p>{title}{body}</section>'
        tags = {"title": "h3", "note": "aside", "equation": "div", "term": "dfn", "example": "div", "exercise": "div", "problem": "div", "solution": "div", "list": "ul", "item": "li", "span": "span"}
        require(name in tags, f"Unsupported/context-invalid CNXML tag: {name}")
        css = {"note": "note", "equation": "equation", "example": "example", "solution": "source-sol", "list": "labeled"}.get(name, "")
        at = identity(node) + (f' class="{css}"' if css else "")
        if name == "solution":
            body = ESC(node.text or "") + "".join((f'<h4{identity(n)}>{self.inner(n)}</h4>' if local(n) == "title" else self.render(n)) + ESC(n.tail or "") for n in node)
        else:
            body = self.inner(node)
        if name == "example":
            body = "<h3>எடுத்துக்காட்டு</h3>" + body
        if name == "note" and node.get("class") == "try":
            body = "<h3>நீங்களே முயலுங்கள்</h3>" + body
        return f"<{tags[name]}{at}>{body}</{tags[name]}>"


def unit_credits():
    result = credits()
    old = "எண்ணுக்கோட்டுப் படம் தமிழில் மறுவரையப்பட்டது;"
    require(result.count(old) == 1, "Review shared credit text before reusing it for U002")
    return result.replace('id="ta-attribution"', 'id="ta2-attribution"', 1).replace(old, "இடமதிப்புப் படங்கள் தமிழில் மறுவரையப்பட்டன;", 1)


def validate_document(book, source):
    doc = ET.fromstring(book)
    ids = [n.get("id") for n in doc.iter() if n.get("id")]
    require(len(ids) == len(set(ids)), "Duplicate generated document IDs")
    id_set = set(ids)
    require(all(n.get("id") in id_set for n in source.iter() if n.get("id")), "A source identifier was dropped")
    for n in doc.iter():
        require(local(n) not in ("script", "iframe", "form", "object", "embed"), "Unexpected active content")
        for key in ("aria-labelledby", "aria-describedby", "headers"):
            require(all(ref in id_set for ref in n.get(key, "").split()), f"Unresolved {key}")
        for key in ("href", "src"):
            value = n.get(key, "")
            if value.startswith("#"):
                require(value[1:] in id_set, f"Unresolved fragment: {value}")
            elif value.startswith(("http:", "https:")):
                require(n.tag == f"{{{H}}}a" and key == "href", "Remote runtime dependency")
            elif value:
                require(value in ("assets/book.css", "assets/u002.css"), f"Unpackaged relative dependency: {value}")
        for value in n.attrib.values():
            for ref in re.findall(r"url\(#([^)]+)\)", value):
                require(ref in id_set, f"Unresolved SVG reference: {ref}")
    return doc


def epub_files(book, navigation, out):
    nav = f'''<html xmlns="{H}" xmlns:epub="http://www.idpf.org/2007/ops" lang="ta-Taml-IN" xml:lang="ta-Taml-IN"><head><title>உள்ளடக்கம்</title></head><body><nav epub:type="toc" id="toc"><h1>உள்ளடக்கம்</h1><ol>{''.join(f'<li><a href="book.xhtml#{ESC(i)}">{ESC(t)}</a></li>' for i,t in navigation)}</ol></nav></body></html>'''
    files = {"OEBPS/book.xhtml": book.encode(), "OEBPS/nav.xhtml": nav.encode(), "OEBPS/LICENSE.txt": (out / "LICENSE.txt").read_bytes()}
    for asset in ASSETS:
        data = (LANG / "assets" / asset).read_bytes()
        if asset == "book.css":
            # EPUBCheck does not support Chromium's nested page-margin boxes.
            parts = data.decode("utf-8").split("\n@page", 1)
            require(len(parts) == 2, "Expected common/print CSS boundary")
            data = (parts[0] + "\n").encode()
        files["OEBPS/assets/" + asset] = data
    files["META-INF/container.xml"] = b'''<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/package.opf" media-type="application/oebps-package+xml"/></rootfiles></container>'''
    files["OEBPS/package.opf"] = f'''<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="uid">urn:language-allocation:ta-Taml-IN:{UNIT}:0.1.0</dc:identifier><dc:title>{TITLE}</dc:title><dc:language>ta-Taml-IN</dc:language><dc:creator>OpenStax contributors; unofficial Tamil adaptation with OpenAI Codex</dc:creator><dc:rights>CC BY-NC-SA 4.0; component notices apply</dc:rights><meta property="dcterms:modified">2026-08-30T00:00:00Z</meta></metadata><manifest><item id="book" href="book.xhtml" media-type="application/xhtml+xml" properties="mathml svg"/><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/><item id="css" href="assets/book.css" media-type="text/css"/><item id="unitcss" href="assets/u002.css" media-type="text/css"/><item id="font" href="assets/fonts/NotoSansTamil.ttf" media-type="font/ttf"/><item id="fontlicense" href="assets/fonts/OFL.txt" media-type="text/plain"/><item id="license" href="LICENSE.txt" media-type="text/plain"/></manifest><spine><itemref idref="book"/></spine></package>'''.encode()
    for name, data in files.items():
        if name.endswith((".xhtml", ".xml", ".opf")):
            ET.fromstring(data)
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=LANG / "reader-u002")
    args = parser.parse_args()
    out = args.out.resolve()
    require(shutil.disk_usage(LANG).free > 100 * 1024 * 1024, "Less than 100 MiB free; no build writes permitted")
    require(COMPANION.is_file(), "U002 companion is not ready; refusing to fabricate or substitute U001 content")
    require(not out.is_relative_to(LANG / "reader") and out not in (ROOT, LANG), "Output would overlap U001 or a workspace root")
    source = ET.parse(SOURCE).getroot()
    companion = ET.parse(COMPANION).getroot()
    require(companion.tag == f"{{{H}}}div", "Unexpected companion root")
    sections = list(companion)
    require(sections and all(n.tag == f"{{{H}}}section" and n.get("id", "").startswith("ta2-") for n in sections), "Companion must contain named ta2- sections")
    insertion = [i for i, n in enumerate(sections) if n.get("id") == "ta2-source-help"]
    require(len(insertion) == 1, "Need the actual U002 source-help section as insertion point")
    renderer = Renderer()
    rendered_source = renderer.render(source)
    navigation = []
    pieces = []
    for index, section in enumerate(sections):
        if index == insertion[0]:
            pieces.append(rendered_source)
            navigation.append((SOURCE_ID, "மூலநூல் மொழிபெயர்ப்பு"))
        heading = section.find(f"{{{H}}}h2")
        require(heading is not None, "Companion section lacks its navigation heading")
        navigation.append((section.get("id"), "".join(heading.itertext())))
        pieces.append(xhtml(section))
    pieces.append(unit_credits())
    navigation.append(("ta2-attribution", "மூலமும் உரிமமும்"))
    nav_items = "".join(f'<li><a href="#{ESC(i)}">{ESC(t)}</a></li>' for i, t in navigation)
    cover = f'''<header class="cover"><p>எண்ணறிவு மீட்பு · இந்தியத் தமிழ் · அலகு 02</p><h1>{TITLE}</h1><p>A00 / OpenStax Prealgebra 2e · மூலநூல் மொழிபெயர்ப்பும் தனிப் பயிற்சித் துணையும்</p><p class="muted">ta-Taml-IN · ஆய்வுக்கான தொடக்கப் பதிப்பு 0.1.0 · 2026-08-30</p><p>இந்தச் சிறு அலகு முழுப் பாடத்திட்டத்தையும் உள்ளடக்காது. தாய்மொழிப் பேச்சாளர் மற்றும் ஆசிரியரின் மதிப்பாய்வு இன்னும் தேவை.</p><nav aria-label="உள்ளடக்கம்"><ul>{nav_items}</ul></nav></header>'''
    book = f'''<!DOCTYPE html><html xmlns="{H}" lang="ta-Taml-IN" xml:lang="ta-Taml-IN"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><title>{TITLE} | ta-Taml-IN · U002</title><link rel="stylesheet" href="assets/book.css"/><link rel="stylesheet" href="assets/u002.css"/></head><body><a class="skip" href="#main">பாடத்திற்குச் செல்லுங்கள்</a>{cover}<main id="main">{''.join(pieces)}</main></body></html>'''
    document = validate_document(book, source)
    screen_book = book.replace("<body>", '<body class="screen-profile">', 1)
    validate_document(screen_book, source)
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(book, encoding="utf-8", newline="\n")
    (out / "screen.html").write_text(screen_book, encoding="utf-8", newline="\n")
    for asset in ASSETS:
        destination = out / "assets" / asset
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(LANG / "assets" / asset, destination)
    shutil.copyfile(LANG / "provenance/A00-LICENSE.txt", out / "LICENSE.txt")
    files = epub_files(book, navigation, out)
    epub_path = out / f"ta-Taml-IN-{UNIT}.epub"
    with zipfile.ZipFile(epub_path, "w") as archive:
        for name, data in [("mimetype", b"application/epub+zip"), *sorted(files.items())]:
            info = zipfile.ZipInfo(name, (2026, 8, 30, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_STORED if name == "mimetype" else zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    outputs = {p.relative_to(out).as_posix(): {"bytes": p.stat().st_size, "sha256": sha(p)} for p in sorted(out.rglob("*")) if p.is_file() and p.name != "build-manifest.json"}
    inputs = [SOURCE, COMPANION, Path(__file__).resolve(), LANG / "scripts/build.py", LANG / "provenance/m81243.en.cnxml", LANG / "provenance/A00-preface-credits.en.cnxml", LANG / "provenance/A00-LICENSE.txt", *(LANG / "assets" / p for p in ASSETS), *sorted(renderer.media_paths)]
    manifest = {"unit": UNIT, "version": "0.1.0", "status": "draft-not-complete-course", "source_scope": "m81243#" + SOURCE_ID, "figure_numbers": {n.get("id"): renderer.figures[n.get("id")] for n in source.findall(f".//{{{C}}}figure")}, "navigation": [{"id": i, "title": t} for i, t in navigation], "inputs": {p.relative_to(LANG).as_posix(): sha(p) for p in inputs}, "outputs": outputs, "structural_counts": {"mathml": len(document.findall(f".//{{{M}}}math")), "tables": len(document.findall(f".//{{{H}}}table")), "inline_svg": len(document.findall(f".//{{{S}}}svg"))}}
    (out / "build-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"output": str(out), "files": len(outputs), "html_sha256": sha(out / "index.html"), "epub_sha256": sha(epub_path), "counts": manifest["structural_counts"]}, indent=2))


if __name__ == "__main__":
    main()
