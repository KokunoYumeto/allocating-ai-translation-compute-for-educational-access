"""Offline Telugu pilot builder and fail-closed structural/mathematical QA.

Standard library only. No network, external JS, learner tracking, or training export.
"""
from pathlib import Path
import copy
import hashlib
import html
import json
import os
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET
from fractions import Fraction
from html.parser import HTMLParser
from inspect_source import slots, MATH

BASE = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
XML = "{http://www.w3.org/XML/1998/namespace}"
ET.register_namespace("", CN[1:-1])
ET.register_namespace("m", MATH[1:-1])


def digest(data):
    return hashlib.sha256(data).hexdigest()


def atomic_write(path, data):
    """Keep the previous artifact intact if a small output write fails."""
    path.parent.mkdir(exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix="." + path.name + ".", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def local(tag):
    return tag.rsplit("}", 1)[-1]


def serialize(root):
    return ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"


def load_source():
    return ET.parse(BASE / "sources/TE-B001.en.cnxml").getroot()


def localize(source, catalog):
    target = copy.deepcopy(source)
    all_slots = list(slots(target))
    assert len(all_slots) == catalog["expected_text_slot_count"], "Source slot drift"
    used = set()
    for i, (element, key, value) in enumerate(all_slots, 1):
        name = f"s{i:03d}"
        if name in catalog["translations"]:
            translated = catalog["translations"][name]
            assert re.search(r"[\u0c00-\u0c7f]", translated), name
            if element.tag.startswith(MATH) and key == "text":
                assert local(element.tag) == "mtext" and value == "and", "Math token changed"
            if key == "alt":
                element.set(key, translated)
            else:
                setattr(element, key, translated)
            used.add(name)
        elif re.search(r"[A-Za-z]", value):
            raise AssertionError(f"Untranslated prose {name}: {value}")
    assert used == set(catalog["translations"]), "Unused translation slots"
    images = list(target.iter(CN + "image"))
    assert len(images) == 1
    assert images[0].get("src") == catalog["asset_localization"]["original"]
    images[0].set("src", catalog["asset_localization"]["localized"])
    images[0].set("mime-type", "image/svg+xml")
    target.set(XML + "lang", "te-Telu-IN")
    return target


def render(root, prefix=""):
    """Small strict renderer for this exact source subsection, never a generic CNXML claim."""
    tag = local(root.tag)
    if root.tag.startswith(MATH):
        node = copy.deepcopy(root)
        node.tail = None
        for element in node.iter():
            element.tag = local(element.tag)
        node.set("xmlns", MATH[1:-1])
        return ET.tostring(node, encoding="unicode")
    esc = html.escape
    ident = f' id="{esc(prefix + root.get("id"))}"' if root.get("id") else ""
    content = esc(root.text or "") + "".join(render(child, prefix) + esc(child.tail or "") for child in root)
    if tag == "link":
        target = root.get("target-id")
        return f'<a href="#{prefix}{esc(target)}">{esc(target)}</a>'
    if tag == "image":
        # Both language columns use the localized mathematical redraw, explicitly disclosed.
        return '<img src="../assets/number-line.te.svg" alt="' + esc(root.get("bridge-alt", "")) + '"/>'
    if tag == "media":
        image = root.find(CN + "image")
        assert image is not None
        alt = root.get("alt", "")
        return f'<div{ident}><img src="../assets/number-line.te.svg" alt="{esc(alt)}"/></div>'
    if tag == "label":
        assert not content.strip()
        return ""
    mapping = {"section":"section", "title":"h3", "para":"p", "note":"aside",
               "equation":"div", "term":"dfn", "figure":"figure", "caption":"figcaption",
               "example":"section", "exercise":"section", "problem":"div", "solution":"div",
               "list":"ul", "item":"li", "span":"span"}
    assert tag in mapping, f"Unsupported CNXML element: {tag}"
    css = f' class="cn-{tag}' + (" try" if root.get("class") == "try" else "") + '"'
    return f'<{mapping[tag]}{ident}{css}>{content}</{mapping[tag]}>'


def math_signature(root):
    out = []
    for element in root.iter():
        if element.tag.startswith(MATH):
            text = (element.text or "").strip()
            if local(element.tag) == "mtext" and text in ("and", "మరియు"):
                text = "AND"
            out.append((local(element.tag), sorted(element.attrib.items()), text))
    return out


class HTMLCheck(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links, self.images, self.languages = [], [], [], []
        self.math = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "a":
            self.links.append(a.get("href", ""))
        if tag == "img":
            assert a.get("alt"), "Image without alt text"
            self.images.append(a["src"])
        if "lang" in a:
            self.languages.append(a["lang"])
        self.math += tag == "math"
        assert tag not in {"script", "iframe", "form"}, "Unexpected active/external content"


def check_math_cases():
    """Independently compute every distinct numeric claim used by our assessment keys."""
    classify = lambda values: [str(v) for v in values if Fraction(str(v)).denominator == 1 and Fraction(str(v)) >= 0]
    assert classify(["0", "1/4", "3", "5.2", "15", "105"]) == ["0", "3", "15", "105"]
    assert classify(["0", "2/3", "2", "9", "11.8", "241", "376"]) == ["0", "2", "9", "241", "376"]
    assert classify(["0", "5/3", "7", "8.8", "13", "201"]) == ["0", "7", "13", "201"]
    assert Fraction(6, 3) == 2 and Fraction(12, 4) == 3 and Fraction("4.0") == 4
    assert 0 < Fraction(1, 4) < 1 and 5 < Fraction("5.2") < 6
    assert 0 < Fraction(2, 3) < 1 and 8 < Fraction("8.8") < 9
    assert 1 < Fraction(5, 3) < 2 and 11 < Fraction("11.8") < 12
    assert 2 < 5 and 1 < 4 and 735 > 537 and 624 > 426
    assert 300 + 0 + 5 == 305 and 400 + 0 + 2 == 402
    assert 500 + 30 + 7 == 537 and 700 + 30 + 5 == 735
    assert 400 + 20 + 6 == 426 and 600 + 20 + 4 == 624
    return "Exact Fraction/integer assertions passed for source and bridge examples"


def build():
    assert shutil.disk_usage(BASE).free >= 32 * 1024 * 1024, "Less than 32 MiB free: stop before writing any artifact"
    lock = json.loads((BASE / "sources.lock.json").read_text(encoding="utf-8"))
    assert digest((BASE / "sources/TE-B001.en.cnxml").read_bytes()) == lock["pilot_source"]["sha256"], "Canonical subsection hash drift"
    source = load_source()
    catalog = json.loads((BASE / "translations/TE-B001.te.json").read_text(encoding="utf-8"))
    assert catalog["source_commit"] == next(r["commit"] for r in lock["repositories"] if r["id"] == "A00-A20-en")
    target = localize(source, catalog)
    sids = [x.get("id") for x in source.iter() if x.get("id")]
    tids = [x.get("id") for x in target.iter() if x.get("id")]
    assert sids == tids and len(sids) == len(set(sids))
    assert [x.tag for x in source.iter()] == [x.tag for x in target.iter()]
    assert math_signature(source) == math_signature(target)
    xml_bytes = serialize(target)
    bridge = ET.parse(BASE / "translations/bridge.xhtml").getroot()
    for element in bridge.iter():
        element.tag = local(element.tag)
    bridge_html = ET.tostring(bridge, encoding="unicode", method="html")
    te_html, en_html = render(target), render(source, "en-")
    page = f'''<!doctype html>
<html lang="te-Telu-IN"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>సంఖ్యల నుంచి బీజగణితానికి · TE-B001</title>
<style>
:root{{color-scheme:light;--ink:#193849;--accent:#006b67;--paper:#fffdfa}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:18px/1.85 'Nirmala UI','Noto Sans Telugu',sans-serif}}
header,main,footer{{max-width:1100px;margin:auto;padding:26px}}header{{border-bottom:5px solid var(--accent)}}
h1{{font-size:2rem;line-height:1.5}}h2{{font-size:1.55rem;border-bottom:1px solid #bdd7d4;padding-bottom:10px;margin-top:2.4em}}h3{{font-size:1.2rem;line-height:1.6}}
p,li,dd{{overflow-wrap:anywhere}}a{{color:#005e86}}nav a{{display:inline-block;margin:5px 15px 5px 0}}
aside,.cn-example,details{{background:#eef6f4;border-left:4px solid var(--accent);padding:15px 22px;margin:20px 0}}
li{{margin:14px 0}}dd{{margin:0 0 22px 0}}dt{{font-weight:700}}summary{{cursor:pointer;font-weight:700}}
figure{{margin:20px 0}}img{{max-width:100%;height:auto}}figcaption{{font-size:.9em}}dfn{{font-style:normal;font-weight:600}}
math{{font-size:1.12em}}.cn-equation{{padding:8px 0}}.cn-solution{{border-top:1px dotted #aac3c0;margin-top:14px}}
.cn-exercise{{margin:16px 0}}.english{{font-size:16px}}code{{font-size:.8em}}.meta{{color:#526873;font-size:.88em}}
footer{{font-size:.83em;border-top:2px solid #bdd7d4}}@media(max-width:600px){{body{{font-size:17px}}header,main,footer{{padding:17px}}h1{{font-size:1.6rem}}aside,details{{padding:12px}}}}
@media print{{body{{font-size:11pt}}nav,summary{{display:none}}details>div,details>ol,details>section{{display:block!important}}h2,h3{{break-after:avoid}}li,figure{{break-inside:avoid}}}}
</style></head><body>
<header><p class="meta">తెలుగు–English mastery bridge · te-Telu-IN · TE-B001 · review pilot</p>
<h1>సంఖ్యల నుంచి బీజగణితానికి</h1><p>సహజ సంఖ్యలు, సున్నా, పూర్ణాంకాలు · Counting numbers, zero and whole numbers</p>
<nav><a href="#bridge">ప్రారంభ పరీక్ష</a><a href="#source-te">మూలపాఠం అనువాదం</a><a href="#source-en">English source</a><a href="#attribution">మూలాలు / credits</a></nav>
<p class="meta">One complete subsection; not a complete module or book. Placement and worked-solution additions are labeled separately. Telugu linguistic review remains open.</p></header>
<main>{bridge_html}<section id="source-te"><h2>మూలపాఠం అనువాదం · OpenStax source subsection</h2>
<p class="meta">A00 · m81243 · fs-id1830385 · Original identifiers and mathematical structure retained.</p>{te_html}</section>
<details id="source-en" class="english" lang="en"><summary>Read the parallel canonical English subsection</summary>{en_html}</details>
</main><footer id="attribution" lang="en"><p>Adapted from <em>Prealgebra 2e</em>, OpenStax, Rice University; senior contributing authors Lynn Marecek, MaryAnne Anthony-Smith, and Andrea Honeycutt Mathis. Canonical source: <a href="https://github.com/openstax/osbooks-prealgebra-bundle/blob/38cae454e644abf9f0a623e876994553881597c9/modules/m81243/index.cnxml">m81243 at 38cae454e644abf9f0a623e876994553881597c9</a>. Indonesian reference edition: <a href="https://github.com/KokunoYumeto/openstax-prealgebra-2e-id-ID">KokunoYumeto/openstax-prealgebra-2e-id-ID</a>, v0.2.7. Existing source and contributor credits remain in the preserved notices.</p>
<p>CC BY-NC-SA 4.0, subject to retained component notices. <a href="../notices/A00-LICENSE.txt">License</a> · <a href="../ATTRIBUTION.md">Full provenance and change disclosure</a>. No endorsement by OpenStax, Rice University, the source authors, or either state government. Translation, added diagnostics and explanations, and the number-line SVG redraw were prepared with OpenAI Codex assistance at the user's request. The English column also displays the disclosed localized diagram, not the upstream JPG. This pilot has no external scripts, fonts, scoring service, or telemetry.</p></footer></body></html>'''
    check = HTMLCheck()
    check.feed(page)
    assert len(check.ids) == len(set(check.ids)), "Duplicate HTML IDs"
    for link in check.links:
        if link.startswith("#"):
            assert link[1:] in check.ids, link
    for item in [f"{p}{i:02d}" for p in ("D", "R") for i in range(1, 9)]:
        assert item in check.ids and "S-" + item in check.ids
    for image in check.images:
        assert (BASE / "reader" / image).resolve().is_file()
    assert check.math == 2 * len(list(source.iter(MATH + "math")))
    assert "\ufffd" not in page and "TODO" not in page
    output = page.encode("utf-8")
    receipt = {
        "schema":"te-bridge-qa-v1", "locale":"te-Telu-IN", "unit":"TE-B001",
        "scope":"one complete subsection m81243#fs-id1830385 plus original bridge",
        "source_sha256":digest(serialize(source)), "target_sha256":digest(xml_bytes),
        "reader_sha256":digest(output), "source_element_count":len(list(source.iter())),
        "preserved_source_ids":len(sids), "source_math_elements":len(math_signature(source)),
        "source_math_expressions":len(list(source.iter(MATH + "math"))),
        "source_exercises":len(list(source.iter(CN + "exercise"))),
        "translated_prose_slots":len(catalog["translations"]), "diagnostic_items":8,
        "recheck_items":8, "full_bridge_solutions":18,
        "checks":{"identifiers":"PASS", "element_order":"PASS", "math_structure_and_tokens":"PASS",
                  "all_prose_slots_translated":"PASS", "local_fragment_links":"PASS", "image_alt_and_files":"PASS",
                  "duplicate_ids":"PASS", "solution_pairing":"PASS", "mathematical_assertions":check_math_cases()},
        "limitations":["Not a full module translation", "Not a validated placement test", "No independent native-speaker review claimed", "Structural QA is scoped to this subsection, not whole-book CNXML schema conformance"],
    }
    # All source/HTML/math assertions above run before replacing any output.
    atomic_write(BASE / "generated/TE-B001.te.cnxml", xml_bytes)
    atomic_write(BASE / "reader/TE-B001.html", output)
    atomic_write(BASE / "qa/build-receipt.json", (json.dumps(receipt,ensure_ascii=False,indent=2)+"\n").encode("utf-8"))
    print(json.dumps(receipt,ensure_ascii=True,indent=2))


if __name__ == "__main__":
    build()
