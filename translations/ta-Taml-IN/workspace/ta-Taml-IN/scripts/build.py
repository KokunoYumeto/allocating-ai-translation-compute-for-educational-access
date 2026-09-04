"""Deterministic local book/EPUB build. Standard library only. No remote runtime.
The source excerpt and recovery companion remain separate editorial strands.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT / "ta-Taml-IN"
C = "http://cnx.rice.edu/cnxml"
M = "http://www.w3.org/1998/Math/MathML"
H = "http://www.w3.org/1999/xhtml"
E = html.escape

def xhtml(node, parent_namespace=H):
    """Serialize unprefixed SVG/MathML so both text/html and XHTML readers work.

    ElementTree's ns1:svg is legal XML but not an SVG element in a text/html
    browser. A namespace boundary must be an explicit default xmlns instead.
    """
    namespace, name = node.tag[1:].split("}", 1) if node.tag.startswith("{") else (parent_namespace, node.tag)
    attributes = f' xmlns="{E(namespace)}"' if namespace != parent_namespace else ""
    for key, value in node.attrib.items():
        if key.startswith("{http://www.w3.org/XML/1998/namespace}"):
            key = "xml:" + key.rsplit("}", 1)[-1]
        attributes += f' {E(key)}="{E(value)}"'
    body = E(node.text or "") + "".join(xhtml(child, namespace) + E(child.tail or "") for child in node)
    return f"<{name}{attributes}>{body}</{name}>"

def local(node):
    return node.tag.rsplit("}", 1)[-1]

def attrs(node):
    return f' id="{E(node.get("id"))}"' if node.get("id") else ""

def inner(node):
    return E(node.text or "") + "".join(render(child) + E(child.tail or "") for child in node)

def math(node):
    name = local(node)
    at = "".join(f' {E(k)}="{E(v)}"' for k, v in node.attrib.items())
    if name == "math":
        at += f' xmlns="{M}"'
    body = E(node.text or "") + "".join(math(child) + E(child.tail or "") for child in node)
    return f"<{name}{at}>{body}</{name}>"

def render(node):
    name = local(node)
    if node.tag.startswith("{" + M):
        return math(node)
    if name == "link":
        return f'<a href="#{E(node.get("target-id"))}">படம் 1.1</a>'
    if name == "media":
        # Inline SVG inherits the bundled Tamil font; the source media identity is retained.
        svg = (LANG / "assets/number-line.ta.svg").read_text(encoding="utf-8")
        return f'<div{attrs(node)}>{svg}<p class="muted">{E(node.get("alt", ""))}</p></div>'
    if name == "label":
        return ""
    tags = {"section":"section", "title":"h3", "para":"p", "note":"aside", "equation":"div", "figure":"figure", "caption":"figcaption", "term":"dfn", "example":"div", "exercise":"div", "problem":"div", "solution":"div", "list":"ul", "item":"li", "span":"span"}
    assert name in tags, f"Unsupported CNXML tag: {name}"
    tag = tags[name]
    css = {"note":"note", "equation":"equation", "example":"example", "solution":"source-sol", "list":"labeled"}.get(name, "")
    if name == "section":
        css = "page source-faithful"
    at = attrs(node) + (f' class="{css}"' if css else "")
    body = inner(node)
    if name == "section":
        body = body.replace("<h3>", "<h2>", 1).replace("</h3>", "</h2>", 1)
        body = '<p class="source-head">மூலநூல் மொழிபெயர்ப்பு · A00 · m81243 · fs-id1830385</p>' + body
    if name == "example":
        body = '<h3>எடுத்துக்காட்டு</h3>' + body
    if name == "note" and node.get("class") == "try":
        body = '<h3>நீங்களே முயலுங்கள்</h3>' + body
    return f"<{tag}{at}>{body}</{tag}>"

def credits():
    source = ET.parse(LANG / "provenance/A00-preface-credits.en.cnxml")
    authors = source.find(f'.//{{{C}}}section[@id="eip-214"]')
    assert authors is not None
    author_text = []
    for n in authors.iter():
        if local(n) == "para":
            # itertext retains author names/affiliations; newline elements become separators.
            content = E(n.text or "")
            for child in n:
                content += ("<br/>" if local(child) == "newline" else E("".join(child.itertext()))) + E(child.tail or "")
            author_text.append("<p>" + content + "</p>")
    return f'''<section id="ta-attribution" class="page credits"><h2>மூலமும் உரிமமும்</h2>
<p>OpenStax, Rice University வெளியிட்ட <span lang="en">Prealgebra 2e</span> நூலின் ஒரு துணைப்பகுதியின் அதிகாரப்பூர்வமற்ற இந்தியத் தமிழ் மொழிபெயர்ப்பு இது. OpenStax, Rice University அல்லது மூலப் பங்களிப்பாளர்கள் இதை ஆதரித்ததாகவோ அங்கீகரித்ததாகவோ பொருள் இல்லை.</p>
<p>மூல ஆசிரியர்கள்: <span lang="en">Lynn Marecek; MaryAnne Anthony-Smith; Andrea Honeycutt Mathis</span>. ஆங்கில மூலமும் இந்தோனேசிய வழிநூலும் ஒப்பிடப்பட்டன. எண்ணுக்கோட்டுப் படம் தமிழில் மறுவரையப்பட்டது; மீட்புக் கற்றல் துணைப்பகுதி புதிதாக எழுதப்பட்டது.</p>
<p>உரை மற்றும் தமிழ் தழுவல்: <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0</a>. மூலத்தின் தனிப்பட்ட கூறுகளுக்கான உரிமைகள் தனியே பொருந்தும். மூல அட்டைப்படம், சின்னங்கள், வணிக முத்திரைகள் இங்கே இல்லை. இணைக்கப்பட்ட LICENSE.txt-இல் முழு உரிம உரை உள்ளது.</p>
<p>உருவாக்க உதவி: OpenAI Codex gpt-5.6-sol, Ultra, பயனர் அறிவுறுத்தலின்படி. மனித ஆசிரியர்/பங்களிப்பாளர் உரிமைகளை இது மாற்றாது. தாய்மொழிப் பேச்சாளர் அல்லது ஆசிரியரின் ஒப்புதல் இன்னும் பெறப்படவில்லை. இது தொடக்கச் சரிபார்ப்புப் பதிப்பு.</p>
<p>Font: Noto Sans Tamil, SIL Open Font License 1.1. No online service or account is needed to read this book. Mathematical screen-reader behavior and PDF/UA conformance are not certified; semantic HTML is the primary accessible format.</p>
<p lang="en">Source pins: <a href="https://github.com/openstax/osbooks-prealgebra-bundle/tree/38cae454e644abf9f0a623e876994553881597c9">OpenStax canonical commit 38cae454e644abf9f0a623e876994553881597c9</a>; <a href="https://github.com/KokunoYumeto/openstax-prealgebra-2e-id-ID/tree/3de9207f56f8b5c57c017abf973fb04e00d740f1">Indonesian v0.2.7 source</a>. Original contributor credits follow, unchanged in substance and language.</p>
<div lang="en">{''.join(author_text)}</div></section>'''

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=LANG / "reader")
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    source = ET.parse(LANG / "translation/m81243-fs-id1830385.cnxml").getroot()
    companion = ET.parse(LANG / "translation/recovery.xhtml").getroot()
    ET.register_namespace("", H)
    sections = list(companion)
    # Route: start, diagnostic, answers, three explanations, source, source help, practice, mastery/retry.
    content = "".join(xhtml(n) for n in sections[:6]) + render(source) + "".join(xhtml(n) for n in sections[6:]) + credits()
    cover = '''<header class="cover"><p>எண்ணறிவு மீட்பு · இந்தியத் தமிழ் · தொடக்க அலகு 01</p><h1>எண்ணும் எண்களும் முழு எண்களும்</h1><p>A00 / OpenStax Prealgebra 2e · தமிழ் மூலம் மற்றும் தனிப் பயிற்சித் துணை</p><p class="muted">ta-Taml-IN · ஆய்வுக்கான தொடக்கப் பதிப்பு 0.1.0 · 2026-08-30</p>
<nav aria-label="உள்ளடக்கம்"><ul><li><a href="#ta-start">பயன்படுத்தும் முறை</a></li><li><a href="#ta-placement">தொடக்கச் சோதனை</a></li><li><a href="#ta-R1">எளிய விளக்கங்கள்</a></li><li><a href="#fs-id1830385">மூலநூல் மொழிபெயர்ப்பு</a></li><li><a href="#ta-practice">பயிற்சி</a></li><li><a href="#ta-mastery">தேர்ச்சிச் சோதனை</a></li><li><a href="#ta-retry">மீள்சோதனை</a></li><li><a href="#ta-attribution">மூலமும் உரிமமும்</a></li></ul></nav></header>'''
    template = f'''<!DOCTYPE html><html xmlns="{H}" lang="ta-Taml-IN" xml:lang="ta-Taml-IN"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><title>எண்ணும் எண்களும் முழு எண்களும் | ta-Taml-IN</title><link rel="stylesheet" href="assets/book.css"/></head><body BODYCLASS><a class="skip" href="#main">பாடத்திற்குச் செல்லுங்கள்</a>{cover}<main id="main">{content}</main></body></html>'''
    book = template.replace(" BODYCLASS", "")
    ET.fromstring(book)
    (out / "index.html").write_text(book, encoding="utf-8", newline="\n")
    (out / "screen.html").write_text(template.replace("BODYCLASS", 'class="screen-profile"'), encoding="utf-8", newline="\n")
    # This pilot includes only its own assets; later-unit drafts stay separate.
    for relative in ["book.css", "number-line.ta.svg", "fonts/NotoSansTamil.ttf", "fonts/OFL.txt"]:
        destination = out / "assets" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(LANG / "assets" / relative, destination)
    shutil.copyfile(LANG / "provenance/A00-LICENSE.txt", out / "LICENSE.txt")
    # EPUB is an offline book, not a learning-record/training-data export.
    nav = f'''<html xmlns="{H}" xmlns:epub="http://www.idpf.org/2007/ops" lang="ta-Taml-IN"><head><title>உள்ளடக்கம்</title></head><body><nav epub:type="toc" id="toc"><h1>உள்ளடக்கம்</h1><ol><li><a href="book.xhtml#ta-start">பயன்படுத்தும் முறை</a></li><li><a href="book.xhtml#fs-id1830385">மூலநூல் பகுதி</a></li><li><a href="book.xhtml#ta-mastery">தேர்ச்சி</a></li><li><a href="book.xhtml#ta-attribution">உரிமம்</a></li></ol></nav></body></html>'''
    files = {"OEBPS/book.xhtml": book.encode(), "OEBPS/nav.xhtml": nav.encode(), "OEBPS/assets/book.css": (LANG / "assets/book.css").read_bytes(), "OEBPS/assets/fonts/NotoSansTamil.ttf": (LANG / "assets/fonts/NotoSansTamil.ttf").read_bytes(), "OEBPS/assets/fonts/OFL.txt": (LANG / "assets/fonts/OFL.txt").read_bytes(), "OEBPS/LICENSE.txt": (out / "LICENSE.txt").read_bytes()}
    # Reflowable EPUB does not use PDF page furniture. EPUBCheck's CSS grammar
    # rejects Chromium's nested page-margin boxes; keep the common screen CSS.
    css_parts = (LANG / "assets/book.css").read_text(encoding="utf-8").split("\n@page", 1)
    assert len(css_parts) == 2, "Expected print-only CSS boundary"
    files["OEBPS/assets/book.css"] = (css_parts[0] + "\n").encode()
    files["META-INF/container.xml"] = b'''<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/package.opf" media-type="application/oebps-package+xml"/></rootfiles></container>'''
    files["OEBPS/package.opf"] = '''<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="uid">urn:language-allocation:ta-Taml-IN:A00-U001:0.1.0</dc:identifier><dc:title>எண்ணும் எண்களும் முழு எண்களும்</dc:title><dc:language>ta-Taml-IN</dc:language><dc:creator>OpenStax contributors; unofficial Tamil adaptation with OpenAI Codex</dc:creator><dc:rights>CC BY-NC-SA 4.0; component notices apply</dc:rights><meta property="dcterms:modified">2026-08-30T00:00:00Z</meta></metadata><manifest><item id="book" href="book.xhtml" media-type="application/xhtml+xml" properties="mathml svg"/><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/><item id="css" href="assets/book.css" media-type="text/css"/><item id="font" href="assets/fonts/NotoSansTamil.ttf" media-type="font/ttf"/><item id="fontlicense" href="assets/fonts/OFL.txt" media-type="text/plain"/><item id="license" href="LICENSE.txt" media-type="text/plain"/></manifest><spine><itemref idref="book"/></spine></package>'''.encode()
    with zipfile.ZipFile(out / "ta-Taml-IN-A00-U001.epub", "w") as z:
        for name, data in [("mimetype", b"application/epub+zip"), *sorted(files.items())]:
            info = zipfile.ZipInfo(name, (2026, 8, 30, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED if name == "mimetype" else zipfile.ZIP_DEFLATED
            z.writestr(info, data)
    manifest = {p.relative_to(out).as_posix(): {"bytes": p.stat().st_size, "sha256": sha(p)} for p in sorted(out.rglob("*")) if p.is_file() and p.name != "build-manifest.json"}
    (out / "build-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out), "files": len(manifest), "html_sha256": sha(out / "index.html"), "epub_sha256": sha(out / "ta-Taml-IN-A00-U001.epub")}, indent=2))

if __name__ == "__main__":
    main()
