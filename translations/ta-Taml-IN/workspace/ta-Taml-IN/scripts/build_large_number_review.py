"""Build/check the isolated U003–U005 HTML source-review draft; no PDF/EPUB.

All input structures are checked before rendering. Accessible chart tables are
derived from identified SVG cells, not from an image filename or an answer total.
"""
import argparse
import copy
import hashlib
import html
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
from build import credits, math, sha, xhtml
from build_u002 import Renderer as BaseRenderer, identity, local, require

ROOT = Path(__file__).resolve().parents[2]
LANG = ROOT / "ta-Taml-IN"
C = "http://cnx.rice.edu/cnxml"
M = "http://www.w3.org/1998/Math/MathML"
H = "http://www.w3.org/1999/xhtml"
S = "http://www.w3.org/2000/svg"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
ESC = html.escape
UNITS = (("U003", "fs-id1883656"), ("U004", "fs-id1321580"), ("U005", "fs-id1339359"))
TITLE = "பெரிய முழு எண்கள்: மூலநூல் மதிப்பாய்வு வரைவு"
OUTPUT = LANG / "reader-large-numbers"
ASSETS = ("large-number-review.css", "fonts/NotoSansTamil.ttf", "fonts/OFL.txt")
TABLE_ID = "fs-id1171100715908"
CHARTS = {
    "fs-id1339846": ("u003-f011", "5278194", 8, 410, 460),
    "fs-id2297687": ("u003-f012", "63407218", 7, 364, 414),
}
PLACES = (
    "நூறு டிரில்லியன்கள்", "பத்து டிரில்லியன்கள்", "டிரில்லியன்கள்",
    "நூறு பில்லியன்கள்", "பத்து பில்லியன்கள்", "பில்லியன்கள்",
    "நூறு மில்லியன்கள்", "பத்து மில்லியன்கள்", "மில்லியன்கள்",
    "நூறாயிரங்கள்", "பத்தாயிரங்கள்", "ஆயிரங்கள்", "நூறுகள்", "பத்துகள்", "ஒன்றுகள்",
)
CNXML_ATTRIBUTES = {
    "section": {"id", XML_LANG}, "title": {"id"}, "para": {"id"},
    "note": {"id", "class"}, "example": {"id"}, "exercise": {"id"},
    "problem": {"id"}, "solution": {"id"}, "figure": {"id", "class"},
    "label": {"id"}, "caption": {"id"}, "media": {"id", "alt"},
    "image": {"src", "mime-type"}, "emphasis": {"id", "effect"},
    "term": {"id", "class"}, "span": {"id", "class"},
    "link": {"id", "target-id"}, "newline": {"id"}, "item": {"id"},
    "list": {"id", "list-type", "class", "number-style", "bullet-style"},
    "table": {"id", "aria-label", "class"}, "tgroup": {"cols"},
    "tbody": set(), "row": set(), "entry": set(),
}
MATH_ATTRIBUTES = {"math": set(), "mrow": set(), "mn": set(), "mo": set(),
                   "mtext": set(), "mstyle": {"fontweight"}}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def ids(node):
    return [n.get("id") for n in node.iter() if n.get("id")]


def math_signature(node):
    return (node.tag, tuple(sorted(node.attrib.items())), node.text or "",
            tuple((math_signature(n), n.tail or "") for n in node))


def source_check(source, english, source_id):
    require(source.tag == f"{{{C}}}section" and source.get("id") == source_id,
            "Wrong source boundary")
    require(source.get(XML_LANG) == "ta-Taml-IN", "Missing Tamil source language")
    require(len(source) and local(source[0]) == "title", "Source heading missing")
    require(ids(source) == ids(english), "English/Tamil source IDs or order differ")
    require([n.tag for n in source.iter()] == [n.tag for n in english.iter()],
            "English/Tamil source structure differs")
    for n in source.iter():
        rules = MATH_ATTRIBUTES if n.tag.startswith("{" + M + "}") else CNXML_ATTRIBUTES
        require(n.tag.startswith(("{" + C + "}", "{" + M + "}")), "Unsupported source namespace")
        require(local(n) in rules, f"Unsupported source element {local(n)}")
        require(set(n.attrib) <= rules[local(n)], f"Unsupported attributes on {local(n)}: {n.attrib}")
        if local(n) == "mstyle":
            require(n.attrib == {"fontweight": "bold"}, "Unsupported MathML style")
        if local(n) == "span":
            require(n.get("class") == "token", "Unsupported source span")
        if local(n) == "note":
            require(n.get("class") in ("try", "howto"), "Unsupported source note")
    for a, b in zip(source.iter(), english.iter()):
        if a.tag in (f"{{{M}}}mn", f"{{{M}}}mo"):
            require((a.text or "") == (b.text or ""), "Source number/operator changed")
        if a.tag == f"{{{M}}}mtext" and "$" in (b.text or ""):
            require(a.text == b.text, "Source currency changed")


def chart_rows(svg, media_id):
    prefix, digits, leading, label_y, digit_y = CHARTS[media_id]
    require(svg.get("viewBox", "").split()[2] == "1082", "Dense chart intrinsic width changed")
    indexed = {n.get("id"): n for n in svg.iter() if n.get("id")}
    rows = []
    actual_digits = []
    for column, power in enumerate(range(14, -1, -1)):
        digit = indexed.get(f"{prefix}-digit-p{power}")
        place = indexed.get(f"{prefix}-place-p{power}")
        require(digit is not None and place is not None, "Missing identified SVG chart cell")
        require(digit.tag == place.tag == f"{{{S}}}text", "Chart cell is not text")
        require(digit.get("x") == str(51 + 70 * column) and digit.get("y") == str(digit_y),
                "SVG digit position differs from verified source geometry")
        require(place.get("transform") == f"translate({58 + 70 * column} {label_y}) rotate(-90)",
                "SVG place label position differs from verified source geometry")
        name = "".join(place.itertext())
        value = "".join(digit.itertext())
        require(name == PLACES[column], "SVG place label no longer matches its power")
        require(value == ("" if column < leading else digits[column - leading]),
                "SVG digit/blank differs from verified source chart")
        actual_digits.append(value)
        rows.append((power, name, value, int(value) * 10 ** power if value else None))
    require(sum(v for _, _, _, v in rows if v is not None) == int("".join(actual_digits)),
            "Derived chart contributions do not reconstruct the source number")
    require(len([n for n in indexed if n.startswith(prefix + "-digit-p")]) == 15,
            "Unexpected extra SVG digit cell")
    return rows


class Renderer(BaseRenderer):
    def __init__(self):
        super().__init__()
        self.unit = None
        self.chart_data = {}

    def chart_table(self, svg, media_id):
        rows = chart_rows(svg, media_id)
        self.chart_data[media_id] = rows
        prefix = "lr-" + media_id
        headers = [f"{prefix}-col-{i}" for i in range(3)]
        body = []
        for power, name, digit, value in rows:
            row_id = f"{prefix}-p{power}"
            body.append(f'<tr data-place-power="{power}"><th id="{row_id}" scope="row" headers="{headers[0]}">{ESC(name)}</th><td headers="{headers[1]} {row_id}">{digit if digit else "காலி"}</td><td headers="{headers[2]} {row_id}">{format(value, ",") if value is not None else "—"}</td></tr>')
        total = sum(value for _, _, _, value in rows if value is not None)
        return f'''<div class="chart-alternative"><p id="{prefix}-help">படத்தின் அதே 15 இடங்கள் கீழே ஒவ்வொரு வரிசையாகக் கொடுக்கப்பட்டுள்ளன. “காலி” என்பது படத்தில் இலக்கம் எழுதப்படாத இடம்; அது எழுதப்பட்ட 0 இலக்கத்திலிருந்து வேறுபட்டது. “—” என்பது அந்தக் காலியிடத்திற்குக் கணக்கிடப்பட்ட மதிப்பு தரப்படவில்லை என்பதைக் குறிக்கிறது.</p><table id="{prefix}-table" class="place-table" aria-describedby="{prefix}-help"><caption>படத்திலிருந்து உருவாக்கப்பட்ட உரை அட்டவணை: {total:,}</caption><colgroup><col class="place-name"/><col class="place-digit"/><col class="place-value"/></colgroup><thead><tr><th id="{headers[0]}" scope="col">இடம்</th><th id="{headers[1]}" scope="col">இலக்கம்</th><th id="{headers[2]}" scope="col">அந்த இலக்கத்தின் மதிப்பு</th></tr></thead><tbody>{''.join(body)}</tbody><tfoot><tr><th scope="row" colspan="2">மொத்த மதிப்பு</th><td>{total:,}</td></tr></tfoot></table></div>'''

    def media(self, node):
        require(len(node) == 1 and node[0].tag == f"{{{C}}}image", "Expected one image per media")
        image = node[0]
        require(not list(image) and not (image.text or "").strip(), "Unhandled image content")
        require(image.get("mime-type") == "image/svg+xml", "Expected translated SVG")
        path = (LANG / "translation" / image.get("src", "")).resolve()
        require(path.is_relative_to(LANG / "assets" / self.unit.lower()) and path.is_file(),
                f"Missing or out-of-scope SVG: {path}")
        self.media_paths.add(path)
        svg = copy.deepcopy(ET.parse(path).getroot())
        require(svg.tag == f"{{{S}}}svg", "Not an SVG root")
        title = svg.find(f"{{{S}}}title")
        desc = svg.find(f"{{{S}}}desc")
        require(title is not None and desc is not None and title.get("id") and desc.get("id"),
                "SVG lacks accessible title/description IDs")
        require(node.get("id") and node.get("alt"), "Source media lacks ID/description")
        require(len(svg.get("viewBox", "").split()) == 4, "SVG lacks intrinsic geometry")
        width = float(svg.get("viewBox").split()[2])
        require(width >= 600, "Unexpected chart intrinsic width")
        # Only the rendering copy uses the exact translated source alt.
        desc.text = node.get("alt")
        svg.set("role", "img")
        svg.set("aria-labelledby", title.get("id") + " " + desc.get("id"))
        svg.set("style", f"width:{width:g}px;min-width:{width:g}px;height:auto")
        hint = "lr-" + node.get("id") + "-diagram-help"
        alternative = self.chart_table(svg, node.get("id")) if node.get("id") in CHARTS else ""
        return f'''<div{identity(node)} class="source-media"><p id="{hint}" class="diagram-hint">படத்தை கிடைமட்டமாக நகர்த்திப் பார்க்கலாம். முழு உரை விளக்கம் படத்திற்குக் கீழே உள்ளது.</p><div class="diagram-scroll" role="region" tabindex="0" aria-label="{ESC(''.join(title.itertext()))}" aria-describedby="{hint}">{xhtml(svg)}</div><p class="media-description">{ESC(node.get('alt'))}</p>{alternative}</div>'''

    def table(self, node):
        require(node.get("id") == TABLE_ID and node.get("aria-label"), "Unexpected source table")
        require(node.get("class") == "unnumbered unstyled", "Source table class changed")
        require(len(node) == 1 and local(node[0]) == "tgroup" and node[0].get("cols") == "3",
                "Review original declared-three/actual-two-column discrepancy")
        group = node[0]
        require(len(group) == 1 and local(group[0]) == "tbody" and len(group[0]) == 5,
                "Source table structure changed")
        headers = (TABLE_ID + "-step", TABLE_ID + "-words")
        body = []
        for row in group[0]:
            require(local(row) == "row" and len(row) == 2 and all(local(n) == "entry" for n in row),
                    "Source table must contain exactly two actual entries in every row")
            body.append("<tr>" + "".join(f'<td headers="{headers[i]}">{self.inner(n)}</td>' for i, n in enumerate(row)) + "</tr>")
        note_id = TABLE_ID + "-review-note"
        return f'''<div class="source-table-group"><p id="{note_id}" class="editorial-note">மதிப்பாய்வுக் குறிப்பு: மூலக் கோப்பில் மூன்று நெடுவரிசைகள் எனக் குறிக்கப்பட்டுள்ளன; ஆனால் ஒவ்வொரு வரிசையிலும் இரண்டு உள்ளீடுகளே உள்ளன. இங்கே அந்த இரண்டு உள்ளீடுகளும் இரண்டு நெடுவரிசைகளாகக் காட்டப்படுகின்றன. கீழுள்ள நெடுவரிசைத் தலைப்புகள் வாசிப்பிற்காகச் சேர்க்கப்பட்டவை.</p><table id="{TABLE_ID}" class="source-steps" aria-label="{ESC(node.get('aria-label'))}" aria-describedby="{note_id}"><thead><tr><th id="{headers[0]}" scope="col">செய்முறை</th><th id="{headers[1]}" scope="col">எண்ணின் பெயர்</th></tr></thead><tbody>{''.join(body)}</tbody></table></div>'''

    def render(self, node):
        name = local(node)
        if node.tag.startswith("{" + M + "}"):
            return math(node)
        if name == "section":
            self.unit = next((u for u, i in UNITS if i == node.get("id")), None)
            require(self.unit is not None, "Unknown source section")
            body = "".join(self.render(n) + ESC(n.tail or "") for n in list(node)[1:])
            return f'<section{identity(node)} class="source-faithful" data-source-unit="{self.unit}"><p class="source-head">மூலநூல் மொழிபெயர்ப்பு · A00 · {self.unit} · m81243#{node.get("id")}</p><h2{identity(node[0])}>{self.inner(node[0])}</h2>{body}<p class="back-link"><a href="#lr-start">உள்ளடக்கத்திற்குத் திரும்புங்கள்</a></p></section>'
        if name == "emphasis":
            require(node.get("effect") == "italics", "Unsupported source emphasis")
            return f'<em{identity(node)}>{self.inner(node)}</em>'
        if name == "term":
            require(node.get("class") == "no-emphasis", "Unsupported source term style")
            return f'<dfn{identity(node)} class="no-emphasis">{self.inner(node)}</dfn>'
        if name == "span":
            return f'<span{identity(node)} class="token">{self.inner(node)}</span>'
        if name == "newline":
            require(not list(node) and not (node.text or "").strip(), "Unhandled newline content")
            return f'<br{identity(node)}/>'
        if name == "list":
            require(all(local(n) == "item" for n in node), "Non-item source list child")
            attrs = {k: v for k, v in node.attrib.items() if k != "id"}
            if attrs == {"list-type": "bulleted", "bullet-style": "bullet"}:
                tag, at = "ul", ' class="source-bullets"'
            elif attrs == {"list-type": "enumerated", "number-style": "arabic", "class": "stepwise"}:
                tag, at = "ol", ' class="source-steps-list" type="1"'
            else:
                allowed = (
                    {"list-type": "enumerated", "number-style": "lower-alpha", "class": "circled"},
                    {"list-type": "labeled-item", "class": "circled"},
                    {"list-type": "labeled-item"},
                )
                require(attrs in allowed, f"Unsupported list style: {attrs}")
                for i, item in enumerate(node):
                    require(len(item) and local(item[0]) == "span" and item[0].text == chr(0x24D0 + i),
                            "Circled source list labels changed")
                tag, at = "ol", ' class="source-circled" type="a" role="list"'
            return f'<{tag}{identity(node)}{at}>{self.inner(node)}</{tag}>'
        if name == "figure":
            require(all(local(n) in ("media", "caption", "label") for n in node), "Unhandled figure child")
            require(node.get("class", "") in ("", "unnumbered"), "Unhandled figure class")
            captions = node.findall(f"{{{C}}}caption")
            require(len(captions) <= 1, "Multiple source captions")
            pieces = []
            for child in node:
                if local(child) == "label":
                    require(not list(child) and not (child.text or "").strip(), "Nonempty unhandled figure label")
                    if child.get("id"):
                        pieces.append(f'<span{identity(child)}></span>')
                elif local(child) != "caption":
                    pieces.append(self.render(child))
            caption = self.inner(captions[0]) if captions else ""
            if node.get("class") != "unnumbered":
                require(node.get("id") in self.figures, "Missing whole-module figure number")
                caption = "படம் " + self.figures[node.get("id")] + (": " + caption if caption else "")
            if caption or captions:
                pieces.append(f'<figcaption{identity(captions[0]) if captions else ""}>{caption}</figcaption>')
            return f'<figure{identity(node)}>{"".join(pieces)}</figure>'
        return super().render(node)


def review_credits():
    result = credits()
    replacements = {
        'id="ta-attribution"': 'id="lr-attribution"',
        "நூலின் ஒரு துணைப்பகுதியின்": "நூலின் தொடர்ந்து வரும் மூன்று துணைப்பகுதிகளின்",
        "எண்ணுக்கோட்டுப் படம் தமிழில் மறுவரையப்பட்டது; மீட்புக் கற்றல் துணைப்பகுதி புதிதாக எழுதப்பட்டது.":
        "இடமதிப்புப் படங்கள் தமிழில் மறுவரையப்பட்டன. இந்த மதிப்பாய்வு வரைவில் மீட்புக் கற்றல் துணைப்பகுதி இன்னும் இணைக்கப்படவில்லை.",
    }
    for old, new in replacements.items():
        require(result.count(old) == 1, "Shared credits changed; review adaptation before building")
        result = result.replace(old, new, 1)
    return result


def validate_document(book, sources, payload):
    doc = ET.fromstring(book)
    all_ids = ids(doc)
    require(len(all_ids) == len(set(all_ids)), "Duplicate generated IDs")
    id_set = set(all_ids)
    expected = [i for source in sources for i in ids(source)]
    require([i for i in all_ids if i in set(expected)] == expected, "Source ID sequence/boundaries changed")
    for source in sources:
        section = doc.find(f'.//{{{H}}}section[@id="{source.get("id")}"]')
        require(section is not None, "Source section missing")
        require([i for i in ids(section) if i in set(expected)] == ids(source), "Source IDs crossed boundaries")
        original_math = source.findall(f".//{{{M}}}math")
        rendered_math = section.findall(f".//{{{M}}}math")
        require([math_signature(n) for n in original_math] == [math_signature(n) for n in rendered_math],
                "Source MathML content/order changed during rendering")
    for n in doc.iter():
        require(local(n) not in ("script", "iframe", "form", "object", "embed", "foreignObject"), "Active content")
        require(not any(k.lower().startswith("on") for k in n.attrib), "Event handler found")
        for key in ("aria-labelledby", "aria-describedby", "headers"):
            require(all(ref in id_set for ref in n.get(key, "").split()), f"Unresolved {key}")
        for key in ("href", "src"):
            value = n.get(key, "")
            if value.startswith("#"):
                require(value[1:] in id_set, f"Unresolved fragment: {value}")
            elif value.startswith(("http:", "https:")):
                require(n.tag == f"{{{H}}}a" and key == "href", "Remote runtime dependency")
            elif value:
                require(value in payload, f"Unpackaged dependency: {value}")
        for value in n.attrib.values():
            for ref in re.findall(r"url\(['\"]?([^)'\"]+)['\"]?\)", value):
                require(ref.startswith("#") and ref[1:] in id_set,
                        f"External or unresolved inline SVG/CSS reference: {ref}")
        if n.tag == f"{{{H}}}p":
            require(not any(local(c) in ("div", "table", "figure", "section", "ul", "ol") for c in n.iter() if c is not n),
                    "Block element illegally nested in HTML paragraph")
    css = payload["assets/large-number-review.css"].decode("utf-8")
    require("@import" not in css and "http:" not in css and "https:" not in css, "Remote CSS dependency")
    for value in re.findall(r"url\(['\"]?([^)'\"]+)", css):
        require((PurePosixPath("assets") / value).as_posix() in payload, "Unpackaged CSS font")
    return doc


def build_payload():
    module = ET.parse(LANG / "provenance/m81243.en.cnxml").getroot()
    sources = []
    paths = []
    source_positions = []
    module_nodes = list(module.iter())
    for unit, source_id in UNITS:
        path = LANG / "translation" / f"m81243-{source_id}.cnxml"
        require(path.is_file(), f"{unit} translation is not ready")
        source = ET.parse(path).getroot()
        english = module.find(f'.//{{{C}}}section[@id="{source_id}"]')
        require(english is not None, "English source boundary missing")
        source_check(source, english, source_id)
        source_positions.append(module_nodes.index(english))
        sources.append(source)
        paths.append(path)
    require(source_positions == sorted(source_positions), "Unit order differs from English source")
    renderer = Renderer()
    pieces = [renderer.render(source) for source in sources]
    require(len(renderer.media_paths) == 8 and len(renderer.chart_data) == 2, "Unexpected figure/chart count")
    navigation = [(source.get("id"), "".join(source[0].itertext())) for source in sources]
    navigation.append(("lr-attribution", "மூலமும் உரிமமும்"))
    nav = "".join(f'<li><a href="#{i}">{ESC(title)}</a></li>' for i, title in navigation)
    cover = f'''<header id="lr-start"><p class="eyebrow">A00 · U003–U005 · இந்தியத் தமிழ்</p><h1>{TITLE}</h1><div class="draft-banner"><p>மூலநூல் மதிப்பாய்வுக்கான வரைவு. மீட்புக் கற்றல் துணைப்பகுதி இன்னும் இணைக்கப்படவில்லை.</p><p>இது முழுப் பாடத்திட்டமோ, தனியாகக் கற்கத் தேவையான அனைத்தும் சோதிக்கப்பட்ட கற்றல் பதிப்போ அல்ல. தாய்மொழிப் பேச்சாளர் மற்றும் ஆசிரியரின் மதிப்பாய்வு இன்னும் தேவை. மூலப் பயிற்சிகளின் விடைகள் மதிப்பாய்விற்காக இங்கே வெளிப்படையாகக் காட்டப்படுகின்றன.</p></div><p>மூன்று மூன்றான சர்வதேச இடமதிப்புத் தொகுதிகளும் மூல எண்களும் காற்புள்ளிகளும் அப்படியே வைக்கப்பட்டுள்ளன. படங்கள் பெரிதாக இருந்தால் அவற்றை கிடைமட்டமாக நகர்த்திப் பார்க்கலாம்.</p><nav aria-label="உள்ளடக்கம்"><ol>{nav}</ol></nav></header>'''
    book = f'''<!DOCTYPE html><html xmlns="{H}" lang="ta-Taml-IN" xml:lang="ta-Taml-IN"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><title>{TITLE}</title><link rel="stylesheet" href="assets/large-number-review.css"/></head><body><a class="skip" href="#lr-main">உள்ளடக்கத்திற்குச் செல்லுங்கள்</a>{cover}<main id="lr-main">{''.join(pieces)}{review_credits()}</main></body></html>'''
    asset_paths = [LANG / "assets" / p for p in ASSETS] + sorted(renderer.media_paths)
    payload = {"assets/" + p.relative_to(LANG / "assets").as_posix(): p.read_bytes() for p in asset_paths}
    payload["LICENSE.txt"] = (LANG / "provenance/A00-LICENSE.txt").read_bytes()
    payload["index.html"] = book.encode("utf-8")
    doc = validate_document(book, sources, payload)
    inputs = [*paths, Path(__file__).resolve(), LANG / "scripts/build.py", LANG / "scripts/build_u002.py",
              LANG / "provenance/m81243.en.cnxml", LANG / "provenance/A00-preface-credits.en.cnxml",
              LANG / "provenance/A00-LICENSE.txt", *asset_paths]
    manifest = {
        "version": "0.1.0", "status": "source-review-draft-recovery-companion-pending",
        "formats": ["HTML"], "scope": [f"m81243#{i}" for _, i in UNITS],
        "navigation": [{"id": i, "title": t} for i, t in navigation],
        "figure_numbers": {n.get("id"): renderer.figures.get(n.get("id")) for source in sources for n in source.findall(f".//{{{C}}}figure")},
        "source_table_discrepancy": {"id": TABLE_ID, "declared_columns": 3, "actual_entries_per_row": 2, "rendered_data_columns": 2},
        "chart_alternatives": {i: [{"power": p, "place": name, "digit": digit, "contribution": value} for p, name, digit, value in rows] for i, rows in renderer.chart_data.items()},
        "structural_counts": {"source_ids": sum(len(ids(source)) for source in sources), "document_ids": len(ids(doc)),
                              "source_mathml": len(doc.findall(f".//{{{M}}}math")), "inline_svg": len(doc.findall(f".//{{{S}}}svg")),
                              "source_tables": 1, "accessible_chart_tables": 2,
                              "source_exercises": sum(len(source.findall(f".//{{{C}}}exercise")) for source in sources)},
        "inputs": {p.relative_to(LANG).as_posix(): sha(p) for p in inputs},
        "outputs": {name: {"bytes": len(data), "sha256": digest(data)} for name, data in sorted(payload.items())},
    }
    payload["build-manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return payload, manifest


def self_test():
    """Mutation checks run entirely in memory; none change sources or outputs."""
    def rejected(operation, label):
        try:
            operation()
        except ValueError:
            return
        raise ValueError("Negative test failed: " + label)

    renderer = Renderer()
    rejected(lambda: renderer.render(ET.fromstring(f'<unknown xmlns="{C}"/>')), "unknown element")
    rejected(lambda: renderer.render(ET.fromstring(f'<list xmlns="{C}" list-type="enumerated" number-style="upper-roman"/>')), "list style")
    source = ET.parse(LANG / "translation/m81243-fs-id1321580.cnxml").getroot()
    table = copy.deepcopy(source.find(f'.//{{{C}}}table'))
    table[0].set("cols", "2")
    rejected(lambda: renderer.table(table), "unreviewed table declaration")
    svg = ET.parse(LANG / "assets/u003/CNX_BMath_Figure_01_01_012_img.svg").getroot()
    svg.find(f'.//*[@id="u003-f012-digit-p4"]').text = "9"
    rejected(lambda: chart_rows(svg, "fs-id2297687"), "interior zero changed")
    svg = ET.parse(LANG / "assets/u003/CNX_BMath_Figure_01_01_011.svg").getroot()
    svg.find(f'.//*[@id="u003-f011-digit-p6"]').set("x", "681")
    rejected(lambda: chart_rows(svg, "fs-id1339846"), "digit shifted one column")
    return 5


def document_self_test(payload):
    sources = [ET.parse(LANG / "translation" / f"m81243-{i}.cnxml").getroot() for _, i in UNITS]
    book = payload["index.html"].decode("utf-8")
    mutations = (
        (book.replace('href="#lr-start"', 'href="#missing-review-target"', 1), payload, "unresolved link"),
        (book.replace('id="lr-start"', 'id="lr-main"', 1), payload, "duplicate document ID"),
        (book.replace("<mn>5,278,194</mn>", "<mn>5,278,195</mn>", 1), payload, "source MathML change"),
        (book, {**payload, "assets/large-number-review.css": b"@import 'https://invalid.example/style.css';"}, "remote CSS"),
    )
    for changed_book, changed_payload, label in mutations:
        try:
            validate_document(changed_book, sources, changed_payload)
        except ValueError:
            continue
        raise ValueError("Negative document test failed: " + label)
    return len(mutations)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Compare expected deterministic files without writing")
    args = parser.parse_args()
    tests = self_test()
    payload, manifest = build_payload()
    tests += document_self_test(payload)
    require(payload == build_payload()[0], "Two in-memory builds were not byte-identical")
    out = OUTPUT.resolve()
    require(out == (LANG / "reader-large-numbers").resolve() and out not in (ROOT, LANG), "Unsafe output directory")
    existing = {p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file()} if out.exists() else set()
    require(existing <= set(payload), "Unexpected output files; refusing to delete or silently package them")
    if args.check:
        require(existing == set(payload), "Generated output file set differs")
        require(all((out / name).read_bytes() == data for name, data in payload.items()), "Generated files are stale")
    else:
        require(shutil.disk_usage(LANG).free > 100 * 1024 * 1024 + sum(map(len, payload.values())),
                "Less than 100 MiB free after build; no writes permitted")
        for name, data in payload.items():
            destination = out / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
    print(json.dumps({"mode": "check" if args.check else "build", "output": str(out), "files": len(payload),
                      "html_sha256": digest(payload["index.html"]), "negative_tests": tests,
                      "counts": manifest["structural_counts"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
