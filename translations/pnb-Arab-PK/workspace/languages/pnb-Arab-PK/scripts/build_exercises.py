"""Standalone deterministic PNB-009 reader; no shared renderer modifications."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
import argparse
import copy
import csv
import hashlib
import html
import json
import re
import xml.etree.ElementTree as ET

from qa_notation import unique_object


BASE = Path(__file__).resolve().parents[1]
MATH = "http://www.w3.org/1998/Math/MathML"
ET.register_namespace("", MATH)
NUMERIC_PERIODS = {
    ("fs-id1165135195670", 1): "0.",
    ("fs-id1165135639752/item/2", 0): "7.",
    ("fs-id1165132950022/item/2", 0): "1.",
    ("fs-id1165137803284/item/2", 0): "2.",
    ("fs-id1165135320063/item/2", 0): "4.",
    ("fs-id1165137731069/item/2", 0): "4.",
    ("fs-id1165137433547", 0): "18.",
    ("fs-id1165135349856/item/3", 0): "2.",
    ("fs-id1165134054032/item/2", 0): "3.",
    ("fs-id1165137861994/item/2", 0): "−3.",
    ("fs-id1165134325875/item/2", 0): "1.",
    ("fs-id1165137723310", 0): "1.",
    ("fs-id1165135380706/item/2", 0): "2.",
    ("fs-id1165137834372/item/2", 0): "1.",
}
UNIT_CSS = '''
.source-media { max-width:100%; margin-block:1rem; }
.source-media img { display:block; width:var(--source-width); min-width:var(--source-width); max-width:none; height:auto; padding:0; border:0; }
.source-exercise { margin-block:1.5rem; border-block-start:1px solid #cad7d1; padding-block-start:.4rem; }
h4 { font-size:1.1rem; color:var(--accent); margin-block:.7rem; }
h5 { font-size:1rem; margin-block:.5rem; }
.source-metadata { border-inline-start:3px solid #cad7d1; padding-inline-start:1rem; }
.metadata-value { font-size:.8rem; overflow-wrap:anywhere; }
.source-module-title { font-size:1.4rem; }
.source-table th { min-width:3.5rem; }
.source-glossary dt { font-weight:bold; color:var(--accent); }
.source-glossary dd { margin-inline-start:1rem; margin-block-end:1rem; }
.source-para { margin-block:.8rem; }
'''


def tag(node):
    return node.tag.rsplit("}", 1)[-1]


def attributes(values):
    return ''.join(' ' + key + '="' + html.escape(str(value), quote=True) + '"' for key, value in values.items())


def source_attrs(node, omit=()):
    return {"data-source-" + key: value for key, value in node.attrib.items() if key not in ("id", *omit)}


def math_html(original, owner, slot):
    clone = copy.deepcopy(original)
    clone.tail = None
    clone.set("dir", "ltr")
    leaves = []

    def visit(node, path):
        if not len(node):
            leaves.append((node, path))
        for index, child in enumerate(node):
            visit(child, path + [index])

    visit(clone, [])
    edits = []
    for leaf, path in reversed(leaves):
        if tag(leaf) == "mo" and leaf.text in (".", ","):
            edits.append({"path": path, "old": leaf.text, "new": ""})
            leaf.text = ""
            continue
        if (owner, slot) in NUMERIC_PERIODS:
            assert tag(leaf) == "mn" and leaf.text == NUMERIC_PERIODS[(owner, slot)]
            before, after = leaf.text, leaf.text[:-1]
            assert re.fullmatch(r"−?\d+\.", before)
            assert float(before.replace("−", "-")) == float(after.replace("−", "-"))
            edits.append({"path": path, "old": before, "new": after})
            leaf.text = after
        break
    if edits:
        clone.set("data-source-text-edits", json.dumps(edits, ensure_ascii=False, separators=(",", ":")))
    attrs = {"class": "math-isolate", "dir": "ltr", "data-source-owner": owner, "data-source-slot": slot}
    if any(tag(n) == "mtable" for n in original.iter()) or len(list(original.iter())) > 70:
        attrs.update({"tabindex": "0", "role": "region", "aria-label": "ریاضی دا فارمولا؛ لوڑ پئے تے پاسے سرکاؤ"})
    return '<span' + attributes(attrs) + '>' + ET.tostring(clone, encoding="unicode") + '</span>'


class Renderer:
    def __init__(self, source, manifest, translation):
        self.source, self.manifest, self.translation = source, manifest, translation
        self.blocks, self.used = translation["source_blocks"], set()
        self.parent = {c: n for n in source.iter() for c in n}
        self.images = {row["media_id"]: row for row in manifest["images"]}
        self.references = {row["id"]: row for row in manifest["references"]}
        self.exercises = [n.get("id") for n in source.iter() if tag(n) == "exercise"]

    def key(self, node):
        name, owner = tag(node), self.parent[node]
        if name == "title" and owner is self.source:
            return "m49301/title"
        if name == "title" and tag(owner) == "metadata":
            return "m49301/metadata/title"
        if name == "term":
            return owner.get("id") + "/term"
        if node.get("id"):
            return node.get("id")
        if name == "title":
            return owner.get("id") + "/title"
        assert name == "item"
        return owner.get("id") + "/item/" + str(list(owner).index(node) + 1)

    def translated(self, key, node):
        assert key not in self.used, "Duplicate translation use: " + key
        self.used.add(key)
        value = self.blocks[key]
        assert "__DRAFT_REQUIRED__" not in value
        # These blocks translate attributes, not the table/media child content.
        if tag(node) in ("table", "media"):
            assert "{{" not in value
            return value

        def own_math(node):
            for child in node:
                if tag(child) == "math":
                    yield child
                elif tag(child) not in ("list", "table", "media", "para"):
                    yield from own_math(child)

        groups = {"math": list(own_math(node)), "child": [n for n in node if tag(n) == "list"],
                  "link": [n for n in node if tag(n) == "link"]}
        for kind, nodes in groups.items():
            assert re.findall(r"\{\{" + kind + r":(\d+)\}\}", value) == [str(i) for i in range(len(nodes))], key + ":" + kind

        def substitute(match):
            kind, index = match[1], int(match[2])
            original = groups[kind][index]
            if kind == "math":
                return math_html(original, key, index)
            if kind == "child":
                return self.render(original)
            spec = self.references[original.get("target-id")]
            assert spec["kind"] == "table" and not original.get("url")
            return '<a' + attributes({"href": spec["href"], "data-source-link": key + "/link/" + str(index)}) + '>جدول <bdi dir="ltr">' + spec["local_label"] + '</bdi></a>'

        return re.sub(r"\{\{(math|child|link):(\d+)\}\}", substitute, value)

    def table(self, node):
        sid = node.get("id")
        summary = self.translated(sid + "/summary", node)
        attrs = {"id": sid, "class": "source-table", "dir": "ltr", "data-source-summary": summary,
                 "aria-label": self.translation["table_summary_overrides"][sid],
                 "aria-describedby": "exercises-table-summary", "data-description-origin": "original-correction",
                 **source_attrs(node, ("summary",))}
        group = next(n for n in node if tag(n) == "tgroup")
        attrs.update({"data-source-tgroup-" + k: v for k, v in group.attrib.items()})
        if any(tag(n) == "label" for n in node):
            assert all(len(n) == 0 and not (n.text or "").strip() for n in node if tag(n) == "label")
            attrs["data-source-empty-label"] = "true"
        columns = [n for n in group if tag(n) == "colspec"]
        body = '<colgroup>' + ''.join('<col' + attributes({"data-source-" + k: v for k, v in n.attrib.items()}) + ' />' for n in columns) + '</colgroup>' if columns else ''
        row_index = 0
        for subgroup in (n for n in group if tag(n) in ("thead", "tbody")):
            body += '<' + tag(subgroup) + attributes(source_attrs(subgroup)) + '>'
            for row in subgroup:
                row_index += 1
                assert len(row) == int(group.get("cols"))
                body += '<tr' + attributes(source_attrs(row)) + '>'
                for column, entry in enumerate(row, 1):
                    cell_attrs = {"dir": "ltr", **source_attrs(entry)}
                    if entry.get("align") == "center":
                        cell_attrs["style"] = "text-align:center"
                    if column == 1:
                        key = f"{sid}/row/{row_index}/entry/1"
                        cell_attrs.update({"scope": "row", "data-source-key": key})
                        out, value = "th", self.translated(key, entry)
                    else:
                        assert not len(entry)
                        out, value = "td", html.escape((entry.text or "").strip())
                    body += '<' + out + attributes(cell_attrs) + '>' + value + '</' + out + '>'
                body += '</tr>'
            body += '</' + tag(subgroup) + '>'
        advisory = '<p class="scroll-hint source-summary-advisory">ماخذ دے خالی خلاصے بارے <a href="#exercises-table-summary">ساڈی اصل وضاحت ویکھو</a>۔</p>'
        return '<div class="source-table-container" data-source-child="' + sid + '"><div class="table-scroll source-table-scroll" dir="ltr" tabindex="0" role="region" aria-label="جدول؛ لوڑ پئے تے پاسے سرکاؤ"><table' + attributes(attrs) + '>' + body + '</table></div>' + advisory + '</div>'

    def media(self, node):
        sid = node.get("id")
        spec = self.images[sid]
        source_alt = self.translated(sid + "/alt", node)
        asset = BASE / spec["path"]
        assert hashlib.sha256(asset.read_bytes()).hexdigest() == spec["sha256"]
        attrs = {"id": sid, "src": "../" + spec["path"], "alt": self.translation["image_alt_overrides"][sid],
                 "data-source-alt": source_alt, "aria-describedby": self.translation["image_alt_note_ids"][sid],
                 "data-description-origin": "original-accessibility-addition", "width": spec["width"], "height": spec["height"],
                 "style": f'--source-width:{spec["width"]}px', **source_attrs(node, ("alt",))}
        wrapper = '<div class="figure-scroll" dir="ltr" tabindex="0" role="region" aria-label="اصل شکل؛ لوڑ پئے تے پاسے سرکاؤ"><img' + attributes(attrs) + ' /></div>'
        hint = '<p class="scroll-hint">چھوٹی سکرین اُتے پوری شکل ویکھن لئی پاسے سرکاؤ، یا <a href="../' + spec["path"] + '">اصل شکل وکھری کھولو</a>۔</p>'
        advisory = '<p class="scroll-hint source-alt-advisory">متبادل متن بارے <a href="#' + attrs["aria-describedby"] + '">ساڈی وکھری اصل وضاحت ویکھو</a>۔</p>'
        return '<div class="source-media" data-source-child="' + sid + '">' + wrapper + hint + advisory + '</div>'

    def render(self, node):
        name, sid = tag(node), node.get("id")
        attrs = {"id": sid} if sid else {}
        if name == "document":
            return ''.join(self.render(c) for c in node)
        if name in ("metadata", "abstract", "content"):
            return '<div class="source-' + name + '" data-source-tag="' + name + '">' + ''.join(self.render(c) for c in node) + '</div>'
        if name in ("content-id", "uuid"):
            assert len(node) == 0
            return '<p class="metadata-value" dir="ltr" data-source-field="' + name + '"><bdi dir="ltr" lang="en">' + html.escape(node.text) + '</bdi></p>'
        if name == "glossary":
            return '<section class="source-glossary" aria-labelledby="source-glossary-title"><h2 id="source-glossary-title">ماخذ دیاں اصطلاحاں</h2><dl>' + ''.join(self.render(c) for c in node) + '</dl></section>'
        if name == "definition":
            return '<div' + attributes({**attrs, "data-source-tag": "definition"}) + '>' + ''.join(self.render(c) for c in node) + '</div>'
        if name == "section":
            return '<section' + attributes({**attrs, "class": "translated", **source_attrs(node)}) + '>' + ''.join(self.render(c) for c in node) + '</section>'
        if name in ("exercise", "problem", "solution"):
            out = "article" if name == "exercise" else "section" if name == "solution" else "div"
            heading = '<h4>مشق <bdi dir="ltr">' + str(self.exercises.index(sid) + 1) + '</bdi></h4>' if name == "exercise" else '<h5>ماخذ دا حل</h5>' if name == "solution" else ''
            return '<' + out + attributes({**attrs, "class": "source-" + name, **source_attrs(node)}) + '>' + heading + ''.join(self.render(c) for c in node) + '</' + out + '>'
        if name == "list":
            out = "ol" if node.get("list-type") == "enumerated" else "ul"
            attrs.update(source_attrs(node))
            if any(c.get("class") == "token" for item in node for c in item):
                attrs.update({"class": "source-parts", "role": "list"})
            return '<' + out + attributes(attrs) + '>' + ''.join(self.render(c) for c in node) + '</' + out + '>'
        if name == "table":
            return self.table(node)
        if name == "media":
            return self.media(node)
        if name in ("para", "title", "item", "term", "meaning"):
            key = self.key(node)
            attrs["data-source-key"] = key
            if name == "title":
                owner = self.parent[node]
                out = "h2" if owner is self.source or owner.get("id") == "fs-id1165137737761" else "h3"
                if owner is self.source:
                    attrs["class"] = "source-module-title"
            else:
                out = {"para": "p", "item": "li", "term": "dt", "meaning": "dd"}[name]
            if name == "para" and any(tag(c) == "list" for c in node):
                out = "div"
                attrs.update({"class": "source-para", "data-source-tag": "para"})
            return '<' + out + attributes(attrs) + '>' + self.translated(key, node) + '</' + out + '>'
        raise ValueError("Unsupported source element: " + name)


def build():
    manifest = json.loads((BASE / "source-excerpts/manifest-009.json").read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    translation = json.loads((BASE / "translations/unit-009.json").read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    source = ET.parse(BASE / "source-excerpts/unit-009.cnxml").getroot()
    renderer = Renderer(source, manifest, translation)
    body = renderer.render(source)
    assert renderer.used == set(translation["source_blocks"]) and len(renderer.used) == 244
    assert len(renderer.exercises) == 92
    css = (BASE / "styles/reader.css").read_text(encoding="utf-8") + UNIT_CSS
    with (BASE / "terminology.tsv").open(encoding="utf-8", newline="") as stream:
        terms = list(csv.DictReader(stream, delimiter="\t"))
    ledger = '<section id="terminology"><h2>تِن زباناں دی سانجھی اصطلاحی کُنجی</h2><div class="table-scroll"><table><thead><tr><th scope="col">شاہ مکھی پنجابی</th><th scope="col" lang="ur-Arab-PK">اردو</th><th scope="col" lang="en" dir="ltr">English</th></tr></thead><tbody>'
    ledger += ''.join('<tr><td>' + html.escape(row["pnb-Arab-PK"]) + '</td><td lang="ur-Arab-PK">' + html.escape(row["ur-Arab-PK"]) + '</td><td lang="en" dir="ltr">' + html.escape(row["en"]) + '</td></tr>' for row in terms)
    ledger += '</tbody></table></div></section>'
    title = html.escape(translation["title"])
    source_url = manifest["upstream_url"] + '/blob/' + manifest["commit"] + '/' + manifest["path"]
    result = '<!doctype html>\n<html lang="pnb-Arab-PK" dir="rtl"><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" /><title>' + title + ' — PNB-009</title><style>' + css + '</style></head><body>'
    result += '<header><p class="eyebrow"><bdi dir="ltr">PNB-009 · A30 / m49301</bdi></p><h1>' + title + '</h1><p>' + html.escape(translation["subtitle"]) + '</p><p class="status">ابتدائی ترجمہ · پنجابی دے ماہر دی لسانی جانچ ہن تک نہیں ہوئی</p><nav aria-label="سبق دے حصے"><a href="unit-008.html">پچھلا سبق</a> · <a href="#para-00001">ماخذ دے مقصد</a> · <a href="#fs-id1165137737761">مشقاں</a> · <a href="#source-glossary-title">ماخذ دیاں اصطلاحاں</a> · <a href="#exercises-bridge">ساڈیاں اصل وضاحتاں</a></nav></header>'
    result += '<main>' + translation["bridge_before_html"] + '<p class="source-label">ماخذ دا ترجمہ: <bdi dir="ltr" lang="en">OpenStax Precalculus 2e, §1.1</bdi> دے مقصد، حصے دیاں مشقاں تے اصطلاحاں۔</p>' + body + translation["bridge_after_html"] + ledger + '</main>'
    result += '<footer id="credits" lang="en" dir="ltr"><h2>Sources, credits and changes</h2><p>Adapted from <a href="' + source_url + '">OpenStax Precalculus 2e, module m49301</a>, Jay Abramson et al., OpenStax / Rice University; foundational chapters credit David Lippman and Melonie Rasmussen. Figure copyright Rice University, OpenStax, under <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a>. Full contributor notices remain in <a href="../provenance/ATTRIBUTION.md">the provenance record</a>. Exact existing image component rows are retained in <a href="../provenance/unit-009-component-notices.json">unit-009-component-notices.json</a>. OpenStax and Rice University do not endorse this adaptation.</p><p>Changes: Shahmukhi Punjabi translation of the complete 92-exercise selection, its 46 supplied solutions, five module objectives, module title/metadata and eleven glossary definitions. The other 46 exercises have no supplied solutions in the source. All 26 canonical JPEGs remain unchanged, with faithfully translated source alts retained and separately identified original accessible descriptions. Four placeholder table summaries have disclosed accessible replacements; table order and numbers remain. All 164 source MathML trees reconstruct exactly after 40 reversible terminal period/comma edits, including fourteen owner-bound numeric periods. Internal punctuation, numeric signs, colons, semicolons and superscripts remain. Underlined source emphasis stays underlined. Source circled tokens retain corresponding isolated Latin letters; missing tokens are not invented. Original clarification and bilingual support are separate from source translation.</p><p>Indonesian comparison edition: KokunoYumeto/openstax-precalculus-2e-id, alpha.58-reader.1. No native-speaker, educator or assistive-technology certification is claimed. This is not a complete textbook, publication or model-training corpus. Module completion requires a separate cross-unit inventory check; the entire five-work assignment remains active.</p></footer></body></html>'
    parsed = ET.fromstring(result[result.index('<html'):])
    identifiers = [n.get("id") for n in parsed.iter() if n.get("id")]
    assert len(identifiers) == len(set(identifiers))
    source_ids = [n.get("id") for n in source.iter() if n is not source and n.get("id")]
    assert [sid for sid in identifiers if sid in source_ids] == source_ids
    reader = BASE / "reader/unit-009.html"
    for n in parsed.iter():
        for attr in ("href", "src"):
            if not n.get(attr):
                continue
            address = urlsplit(n.get(attr))
            if address.scheme or address.netloc:
                continue
            if address.path:
                path = (reader.parent / unquote(address.path)).resolve()
                assert path.is_relative_to(BASE.resolve()) and path.is_file()
            elif address.fragment:
                assert address.fragment in identifiers
    reader.write_text(result + "\n", encoding="utf-8", newline="\n")
    print("Built PNB-009: 244 source blocks, 92 exercises, 46 supplied solutions, 26 unchanged images")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unit", choices=["009"], default="009")
    parser.parse_args()
    build()
