"""Build/check the isolated m81243 whole-module HTML SOURCE-REVIEW draft.

No companions, PDF, EPUB, network or shared-output changes. Source structures
are explicitly supported and unsupported changes fail closed.
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
import assemble_m81243 as assembly
from build import credits, math, sha, xhtml
from build_u002 import Renderer as SmallRenderer, identity, local, require
from build_large_number_review import Renderer as LargeRenderer, chart_rows, ids, math_signature

LANG = Path(__file__).resolve().parents[1]
ROOT = LANG.parent
SOURCE = LANG / "translation/m81243.cnxml"
OUTPUT = LANG / "reader-m81243-review"
C = "http://cnx.rice.edu/cnxml"
M = "http://www.w3.org/1998/Math/MathML"
H = "http://www.w3.org/1999/xhtml"
S = "http://www.w3.org/2000/svg"
D = "http://cnx.rice.edu/mdml"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
ESC = html.escape
TITLE = "முழு எண்கள்: ஓர் அறிமுகம் — மூலநூல் மதிப்பாய்வு வரைவு"
UNITS = dict(zip(("fs-id1830385", "fs-id2340048", "fs-id1883656", "fs-id1321580",
                  "fs-id1339359", "fs-id2472737", "fs-id2296006", "fs-id2279009"),
                 ("U001", "U002", "U003", "U004", "U005", "U006", "U007", "U008")))
TABLES = {
    "fs-id1714120": (5, 5, 5), "fs-id1785447": (5, 5, 5),
    "fs-id1171100715908": (3, 2, 5), "eip-659": (3, 2, 5),
    "eip-493": (3, 2, 4), "eip-379": (3, 2, 4),
    "eip-695": (3, 2, 4), "eip-596": (3, 2, 4),
}
CHART_KEYS = {"fs-id1339846": "fs-id1339846", "fs-id2297687": "fs-id2297687",
              "eip-id1170196618449": "fs-id1339846"}
SELF_CHECK_MEDIA = "eip-id1165721974707"
CONFIDENCE_WARNING = ("மதிப்பாய்வுக் குறிப்பு: கீழுள்ள நம்பிக்கைச் சரிபார்ப்புப் பட்டியல் "
                      "ஒருவரின் சுய உணர்வைக் குறிக்கிறது; அது கணிதத் திறனையோ தேர்ச்சியையோ "
                      "நிரூபிக்கும் சோதனை அல்ல. மூலத்தின் ஆலோசனைகள் அப்படியே உள்ளன. "
                      "இந்த வரைவில் தனித்த தேர்ச்சிச் சோதனையோ மீட்புக் கற்றல் வழியோ இணைக்கப்படவில்லை.")
CNXML_ATTRS = {
    "document": {XML_LANG}, "title": {"id"}, "metadata": set(), "content": set(),
    "section": {"id", "class", XML_LANG}, "para": {"id"}, "note": {"id", "class"},
    "example": {"id"}, "exercise": {"id"}, "problem": {"id"}, "solution": {"id"},
    "figure": {"id", "class"}, "label": {"id"}, "caption": {"id"},
    "media": {"id", "alt"}, "image": {"src", "mime-type"},
    "emphasis": {"id", "effect"}, "term": {"id", "class"}, "span": {"id", "class"},
    "link": {"id", "target-id", "url"}, "newline": {"id"}, "item": {"id"},
    "list": {"id", "class", "list-type", "number-style", "bullet-style", "display"},
    "table": {"id", "class", "aria-label"}, "tgroup": {"cols"},
    "colspec": {"colnum", "colname"}, "thead": set(), "tbody": set(),
    "row": {"valign"}, "entry": {"align", "valign"}, "equation": {"id", "class"},
    "glossary": {XML_LANG}, "definition": {"id"}, "meaning": {"id"},
}
MATH_ATTRS = {n: set() for n in ("math", "mrow", "mn", "mo", "mtext", "mfrac")}
MATH_ATTRS.update({"mstyle": {"fontweight"}, "mspace": {"width"}})
MDML_ATTRS = {n: set() for n in ("content-id", "title", "abstract", "uuid")}
SVG_TAGS = {"svg", "title", "desc", "g", "defs", "marker", "path",
            "rect", "text", "tspan", "use", "circle"}
COUNTS = {"source_ids": 628, "source_nodes": 2122, "source_mathml": 249,
          "source_exercises": 88, "source_solutions": 59, "source_media": 47}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def content_text(node):
    return "".join(node.itertext())


def check_number_line(svg):
    """Lock the visually checked source directions, before SVG ID namespacing.

    SVG marker-end belongs to the last subpath only. A combined upper path
    therefore silently loses the right arrowhead despite keeping all words.
    """
    paths = {node.get("d"): node for node in svg.iter(f"{{{S}}}path")}
    for direction in ("M340 67 H560", "M285 67 H65"):
        require(direction in paths and paths[direction].get("marker-end") == "url(#arrow)",
                "Number-line upper direction arrow missing")
    require("M340 67 H560 M285 67 H65" not in paths, "Compound upper arrow path")
    baseline = paths.get("M40 105 H605")
    require(baseline is not None and all(baseline.get(key) == "url(#arrow)" for key in ("marker-start", "marker-end")),
            "Number-line baseline direction missing")
    marker = svg.find(f'.//{{{S}}}marker[@id="arrow"]')
    require(marker is not None and marker.get("orient") == "auto-start-reverse" and
            marker.find(f"{{{S}}}path").get("d") == "M0 0 L7 3.5 L0 7", "Number-line arrowhead geometry changed")
    texts = [n.text for n in svg.iter(f"{{{S}}}text")]
    require(texts == ["சிறிதாகும்", "பெரிதாகும்", *map(str, range(7))], "Number-line direction/numeral labels changed")


def count_source(source):
    return {"source_ids": len(ids(source)), "source_nodes": len(list(source.iter())),
            "source_mathml": len(source.findall(f".//{{{M}}}math")),
            "source_exercises": len(source.findall(f".//{{{C}}}exercise")),
            "source_solutions": len(source.findall(f".//{{{C}}}solution")),
            "source_media": len(source.findall(f".//{{{C}}}media"))}


def source_check(source, english):
    require(source.tag == f"{{{C}}}document" and source.get(XML_LANG) == "ta-Taml-IN",
            "Wrong assembled module or language")
    require([local(n) for n in source] == ["title", "metadata", "content", "glossary"],
            "Unexpected module top-level structure")
    require(count_source(source) == COUNTS, "Pinned source counts changed; review before building")
    require(len(ids(source)) == len(set(ids(source))), "Duplicate source IDs")
    require(ids(source) == ids(english), "English/Tamil IDs or source order differ")
    require([n.tag for n in source.iter()] == [n.tag for n in english.iter()],
            "English/Tamil source structure differs")
    require([len(n) for n in source.iter()] == [len(n) for n in english.iter()],
            "English/Tamil source hierarchy differs")
    require([n.get("id") for n in source.find(f"{{{C}}}content")] == list(UNITS),
            "Top-level source boundaries changed")
    for n in source.iter():
        namespace = n.tag[1:].split("}")[0]
        rules = {C: CNXML_ATTRS, M: MATH_ATTRS, D: MDML_ATTRS}.get(namespace)
        require(rules is not None and local(n) in rules, f"Unsupported source tag {n.tag}")
        require(set(n.attrib) <= rules[local(n)], f"Unsupported attributes on {local(n)}")
        if n.get(XML_LANG):
            require(n.get(XML_LANG) == "ta-Taml-IN", "Unexpected source language")
        if namespace == M and local(n) == "mspace":
            require(n.get("width") in ("0.2em", "0.5em", "1em"), "Unreviewed MathML spacing")
        if namespace == M and local(n) == "mstyle":
            require(n.attrib == {"fontweight": "bold"}, "Unreviewed MathML style")
        if local(n) == "note":
            require(n.get("class", "") in ("", "try", "howto", "manipulative-math", "media-2"),
                    "Unsupported source note class")
        if local(n) == "section":
            require(n.get("class", "") in ("", "key-concepts", "section-exercises",
                    "practice-perfect", "everyday", "writing", "self-check"),
                    "Unsupported section class")
    for a, b in zip(source.iter(), english.iter()):
        if a.tag in (f"{{{M}}}mn", f"{{{M}}}mo"):
            require(a.text == b.text, "Source number/operator changed")
        if a.tag == f"{{{M}}}mtext" and "$" in (b.text or ""):
            require(a.text == b.text, "Source currency changed")
    metadata = source.find(f"{{{C}}}metadata")
    require([n.tag for n in metadata] == [f"{{{D}}}{n}" for n in
            ("content-id", "title", "abstract", "uuid")], "Unsupported metadata shape")
    for key in ("content-id", "uuid"):
        require(metadata.find(f"{{{D}}}{key}").text ==
                english.find(f"{{{C}}}metadata/{{{D}}}{key}").text, "Source metadata identity changed")


def namespace_svg(svg, prefix):
    """Rewrite all IDs and IDREFs in a rendering copy, never in a source asset."""
    original_ids = ids(svg)
    require(len(original_ids) == len(set(original_ids)), "Duplicate IDs inside original SVG")
    mapping = {i: prefix + "--" + i for i in original_ids}
    for n in svg.iter():
        require(n.tag.startswith("{" + S + "}") and local(n) in SVG_TAGS, "Unsupported/active SVG tag")
        require(not any(k.lower().startswith("on") for k in n.attrib), "SVG event handler")
        require("style" not in n.attrib, "Unreviewed style attribute in original SVG")
        for key, value in list(n.attrib.items()):
            if key == "id":
                n.set(key, mapping[value])
            elif key in ("aria-labelledby", "aria-describedby"):
                require(all(i in mapping for i in value.split()), "Unresolved SVG ARIA reference")
                n.set(key, " ".join(mapping[i] for i in value.split()))
            elif key == "href" or key.endswith("}href"):
                require(key == "href" and value.startswith("#") and value[1:] in mapping,
                        "Remote/unsupported SVG href")
                n.set(key, "#" + mapping[value[1:]])
            else:
                def replacement(match):
                    ref = match.group(1)
                    require(ref.startswith("#") and ref[1:] in mapping, "External/unresolved SVG URL")
                    return "url(#" + mapping[ref[1:]] + ")"
                n.set(key, re.sub(r"url\(['\"]?([^)'\" ]+)['\"]?\)", replacement, value))
    return mapping


def self_check_data(svg):
    indexed = {n.get("id"): n for n in svg.iter() if n.get("id")}
    prefix = "u008-appb001"
    require(svg.get("viewBox") == "0 0 1392 700", "Self-check chart geometry changed")
    headings = []
    skills = []
    for i in range(4):
        n = indexed.get(f"{prefix}-header-{i}")
        require(n is not None and n.tag == f"{{{S}}}text" and n.get("data-column") == str(i),
                "Missing identified self-check heading")
        headings.append(content_text(n))
    for row in range(6):
        n = indexed.get(f"{prefix}-skill-{row}")
        require(n is not None and n.tag == f"{{{S}}}text" and n.get("data-row") == str(row),
                "Missing self-check skill")
        skills.append(content_text(n))
        for col in range(1, 4):
            cell = indexed.get(f"{prefix}-response-r{row}-c{col}")
            require(cell is not None and cell.tag == f"{{{S}}}rect" and
                    cell.get("data-row") == str(row) and cell.get("data-column") == str(col)
                    and cell.get("data-response-cell") == "blank" and not list(cell)
                    and not (cell.text or "").strip(), "Self-check response is not a blank source cell")
    require(len([n for n in svg.iter() if n.get("data-response-cell")]) == 18,
            "Self-check blank-cell count changed")
    return headings, skills


class Renderer(LargeRenderer):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.occurrences = []
        self.table_data = {}
        self.confidence_data = None
        self.missing_solutions = []

    def paragraph(self, node):
        blocks = {"media", "table", "figure", "note", "example", "list"}
        if not any(local(n) in blocks for n in node):
            return f'<p{identity(node)}>{self.inner(node)}</p>'
        parts, pending = [], ESC(node.text or "")
        for child in node:
            if local(child) in blocks:
                if pending.strip():
                    parts.append(f"<p>{pending}</p>")
                parts.append(self.render(child))
                pending = ESC(child.tail or "")
            else:
                pending += self.render(child) + ESC(child.tail or "")
        if pending.strip():
            parts.append(f"<p>{pending}</p>")
        return f'<div{identity(node)} class="source-paragraph">{"".join(parts)}</div>'

    def chart_table(self, svg, media_id):
        rows = chart_rows(svg, CHART_KEYS[media_id])
        self.chart_data[media_id] = rows
        prefix = "mr-" + media_id
        headings = [f"{prefix}-col-{i}" for i in range(3)]
        body = []
        for power, name, digit, value in rows:
            rid = f"{prefix}-p{power}"
            body.append(f'<tr data-place-power="{power}"><th id="{rid}" scope="row" headers="{headings[0]}">{ESC(name)}</th><td headers="{headings[1]} {rid}">{digit or "காலி"}</td><td headers="{headings[2]} {rid}">{format(value, ",") if value is not None else "—"}</td></tr>')
        total = sum(value for _, _, _, value in rows if value is not None)
        return f'<div class="chart-alternative"><p id="{prefix}-help">படத்தின் அதே 15 இடங்கள் வரிசைகளாக உள்ளன. “காலி” என்பது எழுதப்படாத இடம்; அது எழுதப்பட்ட 0 இலக்கத்திலிருந்து வேறுபட்டது. “—” என்பது காலியிடத்திற்கு மதிப்பு தரப்படவில்லை என்பதைக் குறிக்கிறது.</p><table id="{prefix}-table" class="place-table" aria-describedby="{prefix}-help"><caption>படத்தின் உரை மாற்று: {total:,}</caption><thead><tr><th id="{headings[0]}" scope="col">இடம்</th><th id="{headings[1]}" scope="col">இலக்கம்</th><th id="{headings[2]}" scope="col">அந்த இலக்கத்தின் மதிப்பு</th></tr></thead><tbody>{"".join(body)}</tbody><tfoot><tr><th scope="row" colspan="2">மொத்த மதிப்பு</th><td>{total:,}</td></tr></tfoot></table></div>'

    def confidence_table(self, svg, media_id):
        headings, skills = self_check_data(svg)
        self.confidence_data = {"media_id": media_id, "headings": headings, "skills": skills,
                                "rows": 6, "blank_response_cells": 18, "interactive": False}
        prefix = "mr-confidence"
        header = "".join(f'<th id="{prefix}-col-{i}" scope="col">{ESC(t)}</th>' for i, t in enumerate(headings))
        body = []
        for row, skill in enumerate(skills):
            rid = f"{prefix}-skill-{row}"
            cells = "".join(f'<td headers="{prefix}-col-{col} {rid}" data-response-cell="blank"><span class="sr-only">காலிப் பதில் இடம்</span></td>' for col in range(1, 4))
            body.append(f'<tr><th id="{rid}" headers="{prefix}-col-0" scope="row">{ESC(skill)}</th>{cells}</tr>')
        return f'<div class="chart-alternative"><p class="editorial-note" id="{prefix}-help">{CONFIDENCE_WARNING} கீழுள்ள அட்டவணை படத்தின் நிலையான உரை மாற்று; இது நிரப்பக்கூடிய படிவம் அல்ல. ஆறு திறன்களுக்கும் தலா மூன்று பதில் இடங்கள் காலியாகவே வைக்கப்பட்டுள்ளன.</p><div class="table-scroll" role="region" tabindex="0" aria-label="சுய மதிப்பீட்டு அட்டவணையின் உரை மாற்று"><table id="{prefix}-table" class="confidence-table" aria-describedby="{prefix}-help"><caption>சுய மதிப்பீட்டுப் படத்தின் உரை மாற்று — பதில்கள் நிரப்பப்படவில்லை</caption><thead><tr>{header}</tr></thead><tbody>{"".join(body)}</tbody></table></div></div>'

    def media(self, node):
        require(len(node) == 1 and node[0].tag == f"{{{C}}}image", "Expected one SVG per source media")
        img = node[0]
        require(not list(img) and not (img.text or "").strip() and img.get("mime-type") == "image/svg+xml",
                "Unsupported source media payload")
        path = (SOURCE.parent / img.get("src", "")).resolve()
        require(path.is_relative_to((LANG / "assets").resolve()) and path.suffix == ".svg" and path.is_file(),
                "Missing/out-of-scope source SVG")
        media_id = node.get("id")
        require(media_id and node.get("alt"), "Missing source media identity/alt")
        svg = copy.deepcopy(ET.parse(path).getroot())
        require(svg.tag == f"{{{S}}}svg", "Not an SVG root")
        if path.name == "number-line.ta.svg":
            check_number_line(svg)
        title = svg.find(f"{{{S}}}title")
        desc = svg.find(f"{{{S}}}desc")
        require(title is not None and desc is not None and title.get("id") and desc.get("id"),
                "SVG title/description IDs missing")
        dims = svg.get("viewBox", "").split()
        require(len(dims) == 4 and float(dims[2]) > 0 and float(dims[3]) > 0, "Bad intrinsic SVG geometry")
        width = float(dims[2])
        alternative = ""
        if media_id in CHART_KEYS:
            alternative = self.chart_table(svg, media_id)
        if media_id == SELF_CHECK_MEDIA:
            alternative = self.confidence_table(svg, media_id)
        desc.text = node.get("alt")
        svg.set("role", "img")
        svg.set("aria-labelledby", title.get("id") + " " + desc.get("id"))
        mapping = namespace_svg(svg, "mr-svg-" + media_id)
        svg.set("style", f"width:{width:g}px;min-width:{width:g}px;height:auto")
        self.media_paths.add(path)
        self.occurrences.append({"media_id": media_id, "asset": path.relative_to(LANG).as_posix(),
                                 "width": width, "svg_id_map": mapping})
        hint = "mr-" + media_id + "-diagram-help"
        return f'<div{identity(node)} class="source-media"><p id="{hint}" class="diagram-hint">படம் முழுவதும் தெரியாவிட்டால் கிடைமட்டமாக நகர்த்திப் பார்க்கலாம். முழு உரை விளக்கம் கீழே உள்ளது.</p><div class="diagram-scroll" role="region" tabindex="0" aria-label="{ESC(content_text(title))}" aria-describedby="{hint}">{xhtml(svg)}</div><p class="media-description">{ESC(node.get("alt"))}</p>{alternative}</div>'

    def table(self, node):
        tid = node.get("id")
        require(tid in TABLES and node.get("aria-label"), "Unreviewed source table")
        declared, columns, row_count = TABLES[tid]
        groups = node.findall(f"{{{C}}}tgroup")
        require(len(groups) == 1 and groups[0].get("cols") == str(declared), "Source table declaration changed")
        rows = groups[0].findall(f".//{{{C}}}row")
        require(len(rows) == row_count and all(len(row) == columns for row in rows), "Source table actual shape changed")
        self.table_data[tid] = {"declared_columns": declared, "actual_columns": columns,
                                "rows_including_header": row_count}
        if columns == 5:
            return SmallRenderer.table(self, node)
        require(node.get("class") in ("unnumbered unstyled", "unnumbered unstyled has-images"),
                "Unexpected source table class")
        require(all(local(n) in ("label", "tgroup") for n in node), "Unhandled source table child")
        labels = "".join(self.render(n) for n in node if local(n) == "label")
        group = groups[0]
        require(len(group) == 1 and local(group[0]) == "tbody", "Unhandled two-column table structure")
        heads = [f"mr-{tid}-col-{i}" for i in range(2)]
        body = []
        for row in rows:
            require(local(row) == "row" and not row.attrib, "Unexpected two-column row attributes")
            cells = []
            for i, entry in enumerate(row):
                require(local(entry) == "entry" and set(entry.attrib) <= {"valign"} and
                        entry.get("valign", "top") in ("top", "bottom"), "Unhandled source table cell")
                cells.append(f'<td headers="{heads[i]}" class="valign-{entry.get("valign", "top")}">{self.inner(entry)}</td>')
            body.append("<tr>" + "".join(cells) + "</tr>")
        note = f"mr-{tid}-note"
        second = "எண்ணின் பெயர்" if tid == "fs-id1171100715908" else "எண் அல்லது படம்"
        return f'<div class="source-table-group">{labels}<p class="editorial-note" id="{note}">மதிப்பாய்வுக் குறிப்பு: மூலக் கோப்பு மூன்று நெடுவரிசைகள் எனக் கூறினாலும், ஒவ்வொரு வரிசையிலும் இரண்டு உள்ளீடுகளே உள்ளன. இங்கே அவை இரண்டு தரவு நெடுவரிசைகளாகக் காட்டப்படுகின்றன. நெடுவரிசைத் தலைப்புகள் வாசிப்பிற்காகச் சேர்க்கப்பட்டவை.</p><div class="table-scroll" role="region" tabindex="0" aria-label="மூலச் செய்முறை அட்டவணை"><table{identity(node)} class="source-steps" aria-label="{ESC(node.get("aria-label"))}" aria-describedby="{note}"><thead><tr><th id="{heads[0]}" scope="col">செய்முறை</th><th id="{heads[1]}" scope="col">{second}</th></tr></thead><tbody>{"".join(body)}</tbody></table></div></div>'

    def render(self, node):
        name = local(node)
        if node.tag.startswith("{" + M + "}"):
            return math(node)
        require(node.tag.startswith("{" + C + "}"), f"Unsupported content namespace: {node.tag}")
        if name == "section":
            top = node.get("id") in UNITS
            old_unit = self.unit
            if top:
                self.unit = UNITS[node.get("id")]
            self.depth += 1
            level = min(self.depth + 1, 6)
            title = node.find(f"{{{C}}}title")
            lead = ""
            if top:
                lead = f'<p class="source-head">மூலநூல் மொழிபெயர்ப்பு · {self.unit} · m81243#{node.get("id")}</p>'
            if title is None:
                require(node.get("id") == "fs-id2279009", "Unexpected untitled source section")
                lead += f'<h{level}>பகுதிப் பயிற்சிகள்</h{level}><p class="editorial-note">மேலுள்ள வாசிப்புத் தலைப்பு சேர்க்கப்பட்டது; இந்த வெளிப்புறப் பகுதிக்கு மூலத்தில் தனித் தலைப்பு இல்லை.</p>'
            if node.get("class") == "self-check":
                lead += f'<p class="editorial-note" id="mr-confidence-warning">{CONFIDENCE_WARNING}</p>'
            body = ESC(node.text or "")
            for child in node:
                body += ((f'<h{level}{identity(child)}>{self.inner(child)}</h{level}>' if local(child) == "title"
                          else self.render(child)) + ESC(child.tail or ""))
            self.depth -= 1
            self.unit = old_unit
            back = '<p class="back-link"><a href="#mr-start">உள்ளடக்கத்திற்குத் திரும்புங்கள்</a></p>' if top else ""
            return f'<section{identity(node)} class="{"source-faithful" if top else "source-subsection"}" data-source-unit="{UNITS[node.get("id")] if top else old_unit}">{lead}{body}{back}</section>'
        if name == "link":
            if node.get("url"):
                require(set(node.attrib) <= {"id", "url"} and node.get("url") in
                        ("https://www.openstax.org/l/24detplaceval", "https://www.openstax.org/l/24numdigword"),
                        "Unreviewed source external URL")
                return f'<a{identity(node)} href="{ESC(node.get("url"))}" rel="external">{self.inner(node)}</a><span class="optional-link"> (விருப்ப இணைய இணைப்பு; உள்ளடக்கம் இங்கே இணைக்கப்படவில்லை)</span>'
            return SmallRenderer.render(self, node)
        if name == "list":
            require(all(local(n) == "item" for n in node), "Non-item source list child")
            attrs = {k: v for k, v in node.attrib.items() if k != "id"}
            if attrs in ({}, {"display": "block"}, {"list-type": "bulleted", "bullet-style": "bullet"}):
                tag, attr = "ul", ' class="source-bullets"'
            elif attrs == {"list-type": "enumerated", "number-style": "arabic", "class": "stepwise"}:
                tag, attr = "ol", ' class="source-steps-list" type="1"'
            else:
                allowed = (
                    {"list-type": "labeled-item"}, {"list-type": "labeled-item", "class": "circled"},
                    {"list-type": "enumerated", "class": "circled", "number-style": "lower-alpha"},
                    {"list-type": "enumerated", "class": "circled", "number-style": "arabic"},
                    {"list-type": "enumerated", "class": "circled"},
                )
                require(attrs in allowed, f"Unsupported source list style: {attrs}")
                for i, item in enumerate(node):
                    require(len(item) and local(item[0]) == "span" and item[0].text == chr(0x24D0 + i),
                            "Circled list source token missing or reordered")
                tag, attr = "ol", ' class="source-circled" type="a" role="list"'
            return f'<{tag}{identity(node)}{attr}>{self.inner(node)}</{tag}>'
        if name == "emphasis":
            require(node.get("effect", "bold") in ("bold", "italics"), "Unsupported emphasis")
            tag = "em" if node.get("effect") == "italics" else "strong"
            return f'<{tag}{identity(node)}>{self.inner(node)}</{tag}>'
        if name == "term":
            require(node.get("class", "") in ("", "no-emphasis"), "Unsupported term style")
            return f'<dfn{identity(node)} class="{node.get("class", "")}">{self.inner(node)}</dfn>'
        if name == "label":
            require(not list(node) and not (node.text or "").strip(), "Unhandled nonempty source label")
            return f'<span{identity(node)}></span>' if node.get("id") else ""
        if name == "exercise":
            body = self.inner(node)
            if node.find(f"{{{C}}}solution") is None:
                self.missing_solutions.append(node.get("id"))
                body += '<p class="editorial-note missing-solution">மூலத்தில் இந்தப் பயிற்சிக்கான விடை சேர்க்கப்படவில்லை. கூடுதல் விடைத்துணை இந்த மதிப்பாய்வு வரைவில் இல்லை.</p>'
            return f'<div{identity(node)} class="source-exercise"><p class="review-id">பயிற்சி · {ESC(node.get("id"))}</p>{body}</div>'
        if name == "note":
            result = SmallRenderer.render(self, node)
            if node.get("class") == "manipulative-math":
                result += '<p class="editorial-note" id="mr-unbundled-activity">மதிப்பாய்வுக் குறிப்பு: மேலே குறிப்பிடப்பட்ட செயல்தாள் இங்கே இணைக்கப்படவில்லை. அதை முடிப்பது இந்த வரைவை வாசிப்பதற்கான நிபந்தனை அல்ல. மாற்றுச் செயலும் மீட்புக் கற்றல் துணையும் இந்தப் பதிப்பில் சேர்க்கப்படவில்லை.</p>'
            return result
        if name == "glossary":
            require(all(local(n) == "definition" for n in node), "Unhandled glossary child")
            return f'<section id="mr-glossary" class="source-faithful"><p class="source-head">மூலநூல் மொழிபெயர்ப்பு · m81243 · glossary</p><h2>கலைச்சொற்கள்</h2><dl>{self.inner(node)}</dl></section>'
        if name == "definition":
            require([local(n) for n in node] == ["term", "meaning"], "Unsupported glossary definition shape")
            return f'<div{identity(node)}><dt{identity(node[0])}>{self.inner(node[0])}</dt><dd{identity(node[1])}>{self.inner(node[1])}</dd></div>'
        return super().render(node)

    def metadata(self, node):
        parts = ['<section id="mr-metadata" class="source-faithful"><h2>மூலத் தகவலும் கற்றல் நோக்கங்களும்</h2>']
        labels = {"content-id": "மூலக் கூறு அடையாளம்", "title": "மூலத் தலைப்பு", "uuid": "மூல UUID"}
        for child in node:
            name = local(child)
            if name == "abstract":
                parts.append('<div id="mr-objectives">' + self.inner(child) + '</div>')
            else:
                require(name in labels and not list(child), "Unsupported metadata content")
                parts.append(f'<dl class="source-metadata"><dt>{labels[name]}</dt><dd>{ESC(child.text or "")}</dd></dl>')
        parts.append("</section>")
        return "".join(parts)


def review_credits():
    result = credits()
    edits = {
        'id="ta-attribution"': 'id="mr-attribution"',
        "நூலின் ஒரு துணைப்பகுதியின்": "நூலின் m81243 என்ற முழுக் கூறின்",
        "எண்ணுக்கோட்டுப் படம் தமிழில் மறுவரையப்பட்டது; மீட்புக் கற்றல் துணைப்பகுதி புதிதாக எழுதப்பட்டது.":
        "படங்கள் தமிழில் மறுவரையப்பட்டன. இந்த மூலநூல் மதிப்பாய்வு வரைவில் மீட்புக் கற்றல் துணைகளோ கூடுதல் விடைத்துணைகளோ சேர்க்கப்படவில்லை.",
    }
    for old, new in edits.items():
        require(result.count(old) == 1, "Shared credit wording changed; review adaptation")
        result = result.replace(old, new, 1)
    return result.replace("இணைக்கப்பட்ட LICENSE.txt-இல்", '<a href="LICENSE.txt">இணைக்கப்பட்ட LICENSE.txt</a>-இல்')


def validate_document(book, source, payload):
    doc = ET.fromstring(book)
    all_ids = ids(doc)
    require(len(all_ids) == len(set(all_ids)), "Duplicate document IDs")
    expected = ids(source)
    require([i for i in all_ids if i in set(expected)] == expected, "Source ID order or identity lost")
    indexed = {n.get("id"): n for n in doc.iter() if n.get("id")}
    require({"mr-confidence-table", "mr-confidence-warning", *[f"mr-{i}-table" for i in CHART_KEYS]} <= set(indexed),
            "Required semantic alternative or confidence warning missing")
    for section in source.findall(f".//{{{C}}}section"):
        rendered = indexed[section.get("id")]
        require([i for i in ids(rendered) if i in set(expected)] == ids(section), "Source boundary crossed")
    require([math_signature(n) for n in source.findall(f".//{{{M}}}math")] ==
            [math_signature(n) for n in doc.findall(f".//{{{M}}}math")], "Source MathML content/order changed")
    # Keep every nonempty CNXML text/tail fragment within its closest source-ID
    # boundary. Extra editorial labels and semantic alternatives do not replace it.
    parents = {child: parent for parent in source.iter() for child in parent}
    normalize = lambda value: re.sub(r"\s+", " ", value).strip()
    for n in source.iter():
        if not n.tag.startswith("{" + C + "}"):
            continue
        for fragment, owner in ((n.text, n), (n.tail, parents.get(n))):
            if not fragment or not fragment.strip() or owner is None:
                continue
            while not owner.get("id") and owner in parents:
                owner = parents[owner]
            if owner.get("id"):
                require(normalize(fragment) in normalize(content_text(indexed[owner.get("id")])),
                        f"Source text lost within {owner.get('id')}")
    for key in ("content-id", "title", "uuid"):
        metadata_value = source.find(f"{{{C}}}metadata/{{{D}}}{key}").text
        require(metadata_value in content_text(indexed["mr-metadata"]), "Source metadata text lost")
    medias = source.findall(f".//{{{C}}}media")
    require(len(doc.findall(f".//{{{S}}}svg")) == 47, "Media occurrence lost")
    for media in medias:
        rendered = indexed[media.get("id")]
        svg = rendered.find(f".//{{{S}}}svg")
        require(svg is not None and content_text(svg.find(f"{{{S}}}desc")) == media.get("alt"),
                "Rendered media description differs from exact source alt")
    for n in doc.iter():
        require(local(n) not in ("script", "iframe", "form", "input", "button", "object", "embed", "foreignObject"),
                "Unexpected active content")
        require(not any(k.lower().startswith("on") for k in n.attrib), "Event handler")
        for key in ("aria-labelledby", "aria-describedby", "headers"):
            require(all(i in indexed for i in n.get(key, "").split()), f"Unresolved {key}")
        for key in ("href", "src"):
            value = n.get(key, "")
            if value.startswith("#"):
                require(value[1:] in indexed, f"Unresolved local reference {value}")
            elif value.startswith(("http:", "https:")):
                require(n.tag == f"{{{H}}}a" and key == "href", "Remote runtime dependency")
            elif value:
                require(value in payload, f"Unpackaged dependency {value}")
        for value in n.attrib.values():
            for ref in re.findall(r"url\(['\"]?([^)'\" ]+)['\"]?\)", value):
                require(ref.startswith("#") and ref[1:] in indexed, "Unresolved inline SVG reference")
        if n.tag == f"{{{H}}}p":
            require(not any(local(c) in ("div", "table", "figure", "section", "ul", "ol", "aside")
                            for c in n.iter() if c is not n), "Block element nested in paragraph")
    css = payload["assets/m81243-review.css"].decode("utf-8")
    require("@import" not in css.lower() and "http:" not in css.lower() and "https:" not in css.lower(), "Remote CSS dependency")
    for ref in re.findall(r"url\(['\"]?([^)'\" ]+)", css):
        require((PurePosixPath("assets") / ref).as_posix() in payload, "Unpackaged CSS asset")
    confidence = indexed["mr-confidence-table"]
    blanks = [n for n in confidence.iter(f"{{{H}}}td") if n.get("data-response-cell") == "blank"]
    require(len(blanks) == 18 and len(confidence.findall(f"{{{H}}}tbody/{{{H}}}tr")) == 6,
            "Static confidence table is not six by three blank response cells")
    require("நிரூபிக்கும் சோதனை அல்ல" in content_text(indexed["mr-confidence-warning"]),
            "Confidence checklist incorrectly presented as mastery")
    for media_id in CHART_KEYS:
        table = indexed[f"mr-{media_id}-table"]
        require(len(table.findall(f"{{{H}}}tbody/{{{H}}}tr")) == 15, "Incomplete place chart alternative")
    return doc


def build_payload():
    candidate, gate = assembly.assemble()
    require(SOURCE.read_bytes() == candidate, "Assembled source is stale or differs from validated fragments")
    gate_inputs = {**gate["witnesses"],
                   **{row["path"]: row["sha256"] for row in gate["sections_in_canonical_order"]},
                   **{row["path"]: row["sha256"] for row in gate["media"]}}
    for key in ("front_matter", "glossary", "assembler"):
        gate_inputs[gate[key]["path"]] = gate[key]["sha256"]
    source = ET.parse(SOURCE).getroot()
    english = ET.parse(LANG / "provenance/m81243.en.cnxml").getroot()
    source_check(source, english)
    renderer = Renderer()
    metadata = renderer.metadata(source.find(f"{{{C}}}metadata"))
    sections = source.find(f"{{{C}}}content")
    body = "".join(renderer.render(n) + ESC(n.tail or "") for n in sections)
    glossary = renderer.render(source.find(f"{{{C}}}glossary"))
    require(len(renderer.occurrences) == 47 and len(renderer.media_paths) == 46 and
            len(renderer.chart_data) == 3 and len(renderer.missing_solutions) == 29,
            "Rendered occurrence/alternative/solution count changed")
    navigation = [("mr-metadata", "மூலத் தகவலும் கற்றல் நோக்கங்களும்")]
    for section in sections:
        title = section.find(f"{{{C}}}title")
        navigation.append((section.get("id"), content_text(title) if title is not None else "பகுதிப் பயிற்சிகள் — சேர்த்த வாசிப்புத் தலைப்பு"))
    navigation += [("mr-glossary", "கலைச்சொற்கள்"), ("mr-attribution", "மூலமும் உரிமமும்")]
    nav = "".join(f'<li><a href="#{i}">{ESC(title)}</a></li>' for i, title in navigation)
    title = content_text(source.find(f"{{{C}}}title"))
    cover = f'<header id="mr-start"><p class="eyebrow">A00 · m81243 · U001–U008 · இந்தியத் தமிழ்</p><h1>{ESC(title)}</h1><div class="draft-banner"><h2>மூலநூல் மதிப்பாய்வுக்கான வரைவு</h2><p>முழுக் கூறின் மூல மொழிபெயர்ப்பை மதிப்பாய்வு செய்வதற்கான HTML இது. இது முழுப் பாடத்திட்டமோ முடிக்கப்பட்ட தனிக்கற்றல் வழிமுறையோ அல்ல. மீட்புக் கற்றல் துணைகளும் கூடுதல் விடைத்துணைகளும் இங்கே இணைக்கப்படவில்லை.</p><p>மூலத்தில் உள்ள 88 பயிற்சிகளில் 59 பயிற்சிகளின் விடைகள் இங்கே வெளிப்படையாக உள்ளன; 29 பயிற்சிகளுக்கு மூலத்தில் விடை இல்லை. விடையில்லாத இடங்கள் குறிக்கப்பட்டுள்ளன. சுய நம்பிக்கைப் பட்டியல் தேர்ச்சிச் சோதனை அல்ல. தாய்மொழிப் பேச்சாளர்/ஆசிரியர் மதிப்பாய்வும் வாசிப்புத் திரைச் சரிபார்ப்பும் இன்னும் தேவை.</p></div><p>மூல எண்கள், சர்வதேச காற்புள்ளிகள், டாலர்/மைல்/பவுண்டு அலகுகள் அப்படியே உள்ளன. வெளி இணைய இணைப்புகளும் குறிப்பிடப்பட்ட செயல்தாளும் இங்கே இணைக்கப்படாத விருப்ப வளங்கள். இந்தப் பக்கத்தை வாசிக்க இணையக் கணக்கு தேவையில்லை. மதிப்பாய்வுக்காகச் சேர்த்த குறிப்புகள் தனியாகக் குறிக்கப்பட்டுள்ளன.</p><nav aria-label="உள்ளடக்கம்"><ol>{nav}</ol></nav></header>'
    book = f'<!DOCTYPE html><html xmlns="{H}" lang="ta-Taml-IN" xml:lang="ta-Taml-IN"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><title>{TITLE}</title><link rel="stylesheet" href="assets/m81243-review.css"/></head><body><a class="skip" href="#mr-main">உள்ளடக்கத்திற்குச் செல்லுங்கள்</a>{cover}<main id="mr-main">{metadata}{body}{glossary}{review_credits()}</main></body></html>'
    assets = [LANG / "assets" / a for a in ("m81243-review.css", "fonts/NotoSansTamil.ttf", "fonts/OFL.txt")] + sorted(renderer.media_paths)
    payload = {"assets/" + p.relative_to(LANG / "assets").as_posix(): p.read_bytes() for p in assets}
    payload["LICENSE.txt"] = (LANG / "provenance/A00-LICENSE.txt").read_bytes()
    payload["index.html"] = book.encode("utf-8")
    doc = validate_document(book, source, payload)
    inputs = [SOURCE, Path(__file__).resolve(), LANG / "scripts/build.py", LANG / "scripts/build_u002.py",
              LANG / "scripts/build_large_number_review.py", LANG / "provenance/m81243.en.cnxml",
              LANG / "provenance/A00-preface-credits.en.cnxml", LANG / "provenance/A00-LICENSE.txt", *assets]
    manifest = {
        "version": "0.1.0", "status": "whole-module-source-review-draft-no-companions",
        "formats": ["HTML"], "scope": "m81243", "navigation": [{"id": i, "title": t} for i, t in navigation],
        "counts": {**count_source(source), "document_ids": len(ids(doc)), "unique_svg_assets": len(renderer.media_paths),
                   "svg_occurrences": len(renderer.occurrences), "semantic_place_charts": 3,
                   "source_tables": 8, "blank_confidence_response_cells": 18},
        "figure_numbers": {f.get("id"): renderer.figures.get(f.get("id")) for f in source.findall(f".//{{{C}}}figure")},
        "table_shapes": renderer.table_data, "media_occurrences": renderer.occurrences,
        "chart_alternatives": {i: [{"power": p, "place": name, "digit": digit, "contribution": value}
                                  for p, name, digit, value in rows] for i, rows in renderer.chart_data.items()},
        "confidence_alternative": renderer.confidence_data, "source_exercises_without_solution": renderer.missing_solutions,
        "optional_unbundled_source_links": [n.get("url") for n in source.findall(f".//{{{C}}}link") if n.get("url")],
        "inputs": {p.relative_to(LANG).as_posix(): sha(p) for p in inputs},
        "source_validation_inputs": gate_inputs,
        "outputs": {name: {"bytes": len(data), "sha256": digest(data)} for name, data in sorted(payload.items())},
    }
    require(SOURCE.read_bytes() == candidate and all(sha(LANG / name) == expected for name, expected in gate_inputs.items()),
            "Validated source input changed during rendering")
    payload["build-manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return payload, manifest


def self_test(payload):
    """Mutate only in memory; an accepted mutation is a test failure."""
    tests = []
    def rejected(operation, label):
        try:
            operation()
        except (ValueError, ET.ParseError):
            tests.append(label)
            return
        raise ValueError("Negative test accepted: " + label)
    renderer = Renderer()
    rejected(lambda: renderer.render(ET.fromstring(f'<unknown xmlns="{C}"/>')), "unknown tag")
    number_line = ET.parse(LANG / "assets/number-line.ta.svg").getroot()
    check_number_line(number_line)
    missing_arrow = copy.deepcopy(number_line)
    right = missing_arrow.find(f'.//{{{S}}}path[@d="M340 67 H560"]')
    del right.attrib["marker-end"]
    rejected(lambda: check_number_line(missing_arrow), "number-line right arrowhead")
    compound = copy.deepcopy(number_line)
    compound.find(f'.//{{{S}}}path[@d="M340 67 H560"]').set("d", "M340 67 H560 M285 67 H65")
    rejected(lambda: check_number_line(compound), "compound number-line arrow path")
    rejected(lambda: renderer.render(ET.fromstring(f'<list xmlns="{C}" list-type="enumerated" number-style="upper-roman"/>')), "unknown list")
    source = ET.parse(SOURCE).getroot()
    english = ET.parse(LANG / "provenance/m81243.en.cnxml").getroot()
    changed = copy.deepcopy(source)
    changed.find(f".//{{{C}}}para").set("invented", "x")
    rejected(lambda: source_check(changed, english), "unsupported source attribute")
    reparented = copy.deepcopy(source)
    section = reparented.find(f"{{{C}}}content/{{{C}}}section")
    first, second = section[1], section[2]
    section.remove(second)
    first.append(second)
    require([n.tag for n in reparented.iter()] == [n.tag for n in source.iter()],
            "Hierarchy fixture unexpectedly changed preorder")
    rejected(lambda: source_check(reparented, english), "same-preorder reparenting")
    for tid in ("fs-id1714120", "eip-659"):
        table = copy.deepcopy(source.find(f'.//{{{C}}}table[@id="{tid}"]'))
        table.find(f"{{{C}}}tgroup").set("cols", "4")
        rejected(lambda t=table: renderer.table(t), "table declaration " + tid)
    table = copy.deepcopy(source.find(f'.//{{{C}}}table[@id="eip-659"]'))
    row = table.find(f".//{{{C}}}row")
    row.remove(row[-1])
    rejected(lambda: renderer.table(table), "missing actual table cell")
    svg = ET.parse(LANG / "assets/u003/CNX_BMath_Figure_01_01_012_img.svg").getroot()
    svg.find('.//*[@id="u003-f012-digit-p4"]').text = "9"
    rejected(lambda: chart_rows(svg, "fs-id2297687"), "chart internal zero")
    svg2 = ET.parse(LANG / "assets/u003/CNX_BMath_Figure_01_01_011.svg").getroot()
    svg2.find('.//*[@id="u003-f011-digit-p6"]').set("x", "681")
    rejected(lambda: chart_rows(svg2, "fs-id1339846"), "chart geometry")
    chart = ET.parse(LANG / "assets/u008/CNX_BMath_Figure_AppB_001.svg").getroot()
    chart.find('.//*[@id="u008-appb001-response-r0-c1"]').set("data-response-cell", "checked")
    rejected(lambda: self_check_data(chart), "prefilled confidence cell")
    unsafe = ET.fromstring(f'<svg xmlns="{S}"><use href="https://invalid.example/picture.svg"/></svg>')
    rejected(lambda: namespace_svg(unsafe, "test"), "remote SVG use")
    bad_media = copy.deepcopy(source.find(f".//{{{C}}}media"))
    bad_media[0].set("src", "../../../outside.svg")
    rejected(lambda: renderer.media(bad_media), "media path escape")
    book = payload["index.html"].decode("utf-8")
    mutations = (
        (book.replace('href="#mr-start"', 'href="#missing-target"', 1), payload, "broken link"),
        (book.replace('id="mr-start"', 'id="mr-main"', 1), payload, "duplicate document ID"),
        (book.replace('id="para-00001"', 'id="missing-objective"', 1), payload, "metadata objective ID lost"),
        (book.replace("இந்தப் பகுதியின் முடிவில், உங்களால் பின்வருவனவற்றைச் செய்ய முடியும்:", "சோதனைக்காக மாற்றப்பட்ட உரை", 1), payload, "source objective text lost"),
        (book.replace("mr-svg-eip-id1170196618449--u003-f011-title", "mr-svg-fs-id1339846--u003-f011-title"), payload, "reused SVG ID collision"),
        (book.replace("<mn>5,278,194</mn>", "<mn>5,278,195</mn>", 1), payload, "source MathML"),
        (book, {k: v for k, v in payload.items() if k != "assets/fonts/NotoSansTamil.ttf"}, "missing local font"),
        (book, {**payload, "assets/m81243-review.css": b"@import 'https://invalid.example/x';"}, "remote CSS"),
        (book.replace('id="mr-confidence-warning"', 'id="deleted-confidence-warning"', 1), payload, "confidence warning removed"),
    )
    for changed_book, changed_payload, label in mutations:
        # Missing required semantic elements should fail cleanly too.
        rejected(lambda b=changed_book, p=changed_payload: validate_document(b, source, p), label)
    return tests


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Read-only byte-for-byte verification")
    args = parser.parse_args()
    payload, manifest = build_payload()
    tests = self_test(payload)
    require(payload == build_payload()[0], "Repeated in-memory build differs")
    out = OUTPUT.resolve()
    require(out.parent == LANG.resolve() and out.name == "reader-m81243-review" and not OUTPUT.is_symlink(),
            "Unsafe output directory")
    existing = {p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file()} if out.exists() else set()
    require(existing <= set(payload), "Unexpected output files; refusing deletion or silent packaging")
    for name in payload:
        require((out / name).resolve().is_relative_to(out), "Output path escapes isolated reader")
    if args.check:
        require(existing == set(payload), "Output file set differs")
        require(all((out / name).read_bytes() == data for name, data in payload.items()), "Outputs are stale")
    else:
        require(shutil.disk_usage(LANG).free > 100 * 1024 * 1024 + sum(map(len, payload.values())),
                "Less than 100 MiB free after build; no writes")
        for name, data in payload.items():
            dest = out / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
    print(json.dumps({"mode": "check" if args.check else "build", "output": str(out), "files": len(payload),
                      "html_sha256": digest(payload["index.html"]), "counts": manifest["counts"],
                      "negative_tests": tests}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
