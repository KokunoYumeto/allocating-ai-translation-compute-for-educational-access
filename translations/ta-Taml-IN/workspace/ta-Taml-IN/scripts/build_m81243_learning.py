"""Build the complete m81243 source + seven separate learning companions.

Local review edition, not a validated course. Standard-library-only build;
never rewrites source, companions, earlier readers, or approved PDFs.
"""
import argparse
from collections import Counter
import copy
import io
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlsplit
import zipfile

sys.dont_write_bytecode = True
import build_m81243_review as review
from build import xhtml
from build_u002 import require

LANG = review.LANG
H, M, S, C = review.H, review.M, review.S, review.C
OUTPUT = LANG / "reader-m81243-learning"
STYLE = LANG / "assets/m81243-learning.css"
EPUB_NAME = "ta-Taml-IN-A00-m81243.epub"
TITLE = "முழு எண்கள்: ஓர் அறிமுகம் — கற்றல் பதிப்பு"
# Key, filename, IDs, sections, new questions, source-answer supports.
COMPANIONS = (
    ("route", "recovery-m81243-route.xhtml", 43, 9, 12, 0),
    ("u001", "recovery.xhtml", 47, 13, 15, 0),
    ("u002", "recovery-u002.xhtml", 45, 13, 16, 0),
    ("large", "recovery-large-numbers.xhtml", 80, 14, 16, 0),
    ("round", "recovery-rounding.xhtml", 50, 14, 16, 0),
    ("missing", "recovery-m81243-missing-answers.xhtml", 38, 9, 0, 29),
    ("reason", "recovery-m81243-supplied-reasoning.xhtml", 38, 9, 0, 29),
)


def signature(node):
    return (node.tag, tuple(sorted(node.attrib.items())), node.text or "",
            tuple((signature(child), child.tail or "") for child in node))


def indexed(node):
    return {n.get("id"): n for n in node.iter() if n.get("id")}


def paragraph(text, href=None, label=None, **attrs):
    node = ET.Element(f"{{{H}}}p", {"class": "editorial-note", **attrs})
    node.text = text
    if href:
        ET.SubElement(node, f"{{{H}}}a", {"href": "#" + href}).text = label
    return node


def render_companion(root):
    """Add focusable inline scroll regions around long MathML, preserving content."""
    rendered = copy.deepcopy(root)
    for parent in list(rendered.iter()):
        for child in list(parent):
            if child.tag != f"{{{M}}}math" or len("".join(child.itertext()).strip()) <= 18:
                continue
            position = list(parent).index(child)
            wrapper = ET.Element(f"{{{H}}}span", {"class": "math-scroll", "role": "region", "tabindex": "0",
                                  "aria-label": "கணிதக் கூற்று — முழுவதும் காண கிடைமட்டமாக நகர்த்தலாம்"})
            wrapper.tail, child.tail = child.tail, None
            parent.remove(child)
            wrapper.append(child)
            parent.insert(position, wrapper)
    # Reverse only this exact renderer-only wrapper and compare the full input tree.
    restored = copy.deepcopy(rendered)
    for parent in list(restored.iter()):
        for child in list(parent):
            if child.tag == f"{{{H}}}span" and child.get("class") == "math-scroll":
                require(len(child) == 1 and child[0].tag == f"{{{M}}}math", "Invalid math scroll wrapper")
                position = list(parent).index(child)
                math = child[0]
                math.tail = child.tail
                parent.remove(child)
                parent.insert(position, math)
    require(signature(restored) == signature(root), "Math scroll adaptation changed companion content")
    return rendered


def companion_gate(roots, source):
    source_exercises = {n.get("id"): n for n in source.iter(f"{{{C}}}exercise")}
    final_section = source.find(f'.//{{{C}}}section[@id="fs-id2279009"]')
    final_ids = [n.get("id") for n in final_section.iter(f"{{{C}}}exercise")]
    answer_map, new_questions = {}, []
    for key, _, id_count, section_count, q_count, source_count in COMPANIONS:
        root = roots[key]
        ids = review.ids(root)
        require(root.tag == f"{{{H}}}div" and len(ids) == len(set(ids)) == id_count,
                "Companion root/ID inventory changed: " + key)
        require(len(root) == section_count and all(n.tag == f"{{{H}}}section" for n in root),
                "Companion section inventory changed: " + key)
        questions = [n for n in root.iter() if n.get("data-kind")]
        answers = [n for n in root.iter() if n.get("data-answer-for")]
        require(len(questions) == q_count and len(answers) == q_count + source_count,
                "Companion question/answer count changed: " + key)
        if q_count:
            require(Counter(n.get("id") for n in questions) ==
                    Counter(n.get("data-answer-for") for n in answers),
                    "Missing or duplicate new-item answer: " + key)
            for q in questions:
                require(not any(n.get("data-answer-for") for n in q.iter()),
                        "Answer nested in assessed question")
            new_questions.extend(questions)
        else:
            expected_ids = [i for i in final_ids if
                            (source_exercises[i].find(f"{{{C}}}solution") is None) == (key == "missing")]
            require([n.get("data-answer-for") for n in answers] == expected_ids,
                    "Source-answer support order/coverage changed: " + key)
            for answer in answers:
                sid = answer.get("data-answer-for")
                exercise = source_exercises[sid]
                require(answer.get("data-source-problem") == exercise.find(f"{{{C}}}problem").get("id"),
                        "Wrong source problem mapped")
                if key == "reason":
                    require(answer.get("data-source-solution") == exercise.find(f"{{{C}}}solution").get("id"),
                            "Wrong original source solution mapped")
                require(sid not in answer_map, "Duplicate source answer support")
                answer_map[sid] = answer.get("id")
    require(set(answer_map) == set(final_ids) and len(answer_map) == 58,
            "Final source exercise support is incomplete")
    require(len(new_questions) == 75, "New assessment inventory changed")
    return answer_map


def source_for_learning(baseline_nodes, answer_map):
    """Change only identified renderer-added notes; append labelled support links."""
    nodes = copy.deepcopy(baseline_nodes)
    wrapper = ET.Element(f"{{{H}}}div")
    wrapper.extend(nodes)
    lookup = indexed(wrapper)
    old_end = "இந்த வரைவில் தனித்த தேர்ச்சிச் சோதனையோ மீட்புக் கற்றல் வழியோ இணைக்கப்படவில்லை."
    new_end = "தனியாக எழுதப்பட்ட கற்றல் வழியையும் விடைகளுடன் கூடிய சுயசோதனைகளையும் இந்தப் பதிப்பின் துணைப்பகுதியில் பயன்படுத்துங்கள்."
    for key in ("mr-confidence-warning", "mr-confidence-help"):
        note = lookup[key]
        require((note.text or "").count(old_end) == 1 and len(note) == 0,
                "Confidence editorial note changed")
        note.text = note.text.replace(old_end, new_end) + " "
        ET.SubElement(note, f"{{{H}}}a", {"href": "#ta-route-checkpoints"}).text = "கற்றல் வழிக்குச் செல்லுங்கள்."
    activity = lookup["mr-unbundled-activity"]
    require(len(activity) == 0 and "மாற்றுச் செயலும்" in (activity.text or ""),
            "Unbundled-worksheet editorial note changed")
    activity.text = ("பதிப்புக் குறிப்பு: மேலே குறிப்பிடப்பட்ட செயல்தாள் இங்கே இணைக்கப்படவில்லை. "
                     "அதை முடிப்பது இந்தக் கற்றல் வழியின் நிபந்தனை அல்ல. தனியாக எழுதப்பட்ட விளக்கங்களுக்கும் பயிற்சிக்கும் ")
    ET.SubElement(activity, f"{{{H}}}a", {"href": "#ta2-start"}).text = "இடமதிப்புத் துணைப்பகுதியைப் பயன்படுத்துங்கள்."
    missing_count = 0
    for sid, target in answer_map.items():
        exercise = lookup[sid]
        notes = [n for n in exercise if n.get("class") == "editorial-note missing-solution"]
        require(len(notes) <= 1, "Duplicate missing-source-answer label")
        if notes:
            note = notes[0]
            require(len(note) == 0 and note.text == "மூலத்தில் இந்தப் பயிற்சிக்கான விடை சேர்க்கப்படவில்லை. கூடுதல் விடைத்துணை இந்த மதிப்பாய்வு வரைவில் இல்லை.",
                    "Missing-source-answer editorial label changed")
            note.text = "மூலத்தில் இந்தப் பயிற்சிக்கான விடை சேர்க்கப்படவில்லை. புதிதாக எழுதப்பட்ட விடையும் காரணமும் தனித் துணைப்பகுதியில் உள்ளன."
            missing_count += 1
        exercise.append(paragraph("புதிய துணைப்பகுதி — ", target, "விடையும் படிப்படியான காரணமும்",
                                  **{"data-learning-support-for": sid}))
    require(missing_count == 29, "Expected 29 preserved source omissions")
    # Math, source IDs and exact original solution trees are checked separately below.
    require([review.math_signature(n) for n in wrapper.iter(f"{{{M}}}math")] ==
            [review.math_signature(n) for b in baseline_nodes for n in b.iter(f"{{{M}}}math")],
            "Editorial adaptation changed source mathematics")
    baseline_lookup = {i: n for b in baseline_nodes for i, n in indexed(b).items()}
    for sid, node in baseline_lookup.items():
        if node.get("class") == "source-sol":
            require(signature(lookup[sid]) == signature(node), "Original source solution changed")
    return nodes


def validate(book, payload, source_nodes, roots, answer_map, source):
    doc = ET.fromstring(book)
    ids = review.ids(doc)
    require(len(ids) == len(set(ids)), "Duplicate document ID")
    lookup = indexed(doc)
    for expected in source_nodes:
        require(signature(lookup[expected.get("id")]) == signature(expected),
                "Rendered source block changed during integration")
    for key, root in roots.items():
        wrapper = lookup["mrl-" + key]
        require(len(wrapper) == 2 and signature(wrapper[0]) == signature(root),
                "Companion content changed during integration: " + key)
    source_ids = review.ids(source)
    require([i for i in ids if i in set(source_ids)] == source_ids, "Original source IDs/order changed")
    for sid, target in answer_map.items():
        notes = lookup[sid].findall(f'{{{H}}}p[@data-learning-support-for="{sid}"]')
        require(len(notes) == 1 and notes[0].find(f"{{{H}}}a").get("href") == "#" + target,
                "Wrong or missing source-to-support link")
    for n in doc.iter():
        require(review.local(n) not in {"script", "iframe", "form", "input", "button", "object", "embed", "foreignObject", "base"},
                "Unexpected active content")
        require(not any(k.lower().startswith("on") for k in n.attrib), "Event handler")
        for attr in ("aria-labelledby", "aria-describedby", "headers"):
            require(all(i in lookup for i in n.get(attr, "").split()), "Unresolved " + attr)
        for attr in ("data-answer-for", "data-source-problem", "data-source-solution", "data-remediation"):
            require(not n.get(attr) or n.get(attr) in lookup, "Unresolved " + attr)
        for attr in ("href", "src"):
            ref = n.get(attr, "")
            if ref.startswith("#"):
                require(ref[1:] in lookup, "Unresolved local reference " + ref)
            elif ref.startswith(("http:", "https:")):
                require(n.tag == f"{{{H}}}a" and attr == "href", "Remote runtime dependency")
            elif ref:
                require(ref in payload, "Unpackaged dependency " + ref)
        for value in n.attrib.values():
            for ref in re.findall(r"url\(['\"]?([^)'\" ]+)['\"]?\)", value):
                require(ref.startswith("#") and ref[1:] in lookup, "Unresolved SVG paint reference")
        if n.tag == f"{{{H}}}p":
            require(not any(review.local(c) in {"div", "table", "figure", "section", "ul", "ol", "aside"}
                            for c in n.iter() if c is not n), "Block element inside paragraph")
    for name, raw in payload.items():
        if not name.endswith(".css"):
            continue
        css = raw.decode("utf-8")
        require(not re.search(r"@import|https?:", css, re.I), "Remote CSS dependency")
        for ref in re.findall(r"url\(['\"]?([^)'\" ]+)", css):
            require((PurePosixPath(name).parent / ref).as_posix() in payload, "Unpackaged CSS dependency")
    expected_math = 249 + sum(len(list(root.iter(f"{{{M}}}math"))) for root in roots.values())
    require(len(list(doc.iter(f"{{{M}}}math"))) == expected_math, "MathML inventory changed")
    require(len(list(doc.iter(f"{{{S}}}svg"))) == 49, "SVG occurrence inventory changed")
    require(len([n for n in doc.iter() if n.tag.startswith("{" + H + "}") and n.get("data-kind")]) == 75,
            "New question inventory changed")
    require(len([n for n in doc.iter() if n.get("data-answer-for")]) == 133, "Answer inventory changed")
    return doc


def package_gate(files):
    """Check every content document, including non-spine SVGs and license/nav."""
    docs = {name: ET.fromstring(raw) for name, raw in files.items() if name.endswith((".xhtml", ".svg"))}
    lookups = {name: indexed(doc) for name, doc in docs.items()}
    for name, doc in docs.items():
        require(len(review.ids(doc)) == len(lookups[name]), "Duplicate ID in packaged document")

    def reference(name, ref, remote_allowed=False):
        parsed = urlsplit(ref)
        if parsed.scheme or parsed.netloc:
            require(remote_allowed and parsed.scheme in ("http", "https") and bool(parsed.netloc),
                    "Remote package dependency")
            return
        require(not parsed.query, "Unexpected query in local package reference")
        dest = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(parsed.path))) if parsed.path else name
        require(not dest.startswith(("../", "/")) and dest in files, "Unpackaged resource in package")
        if parsed.fragment:
            require(dest in lookups and unquote(parsed.fragment) in lookups[dest], "Unresolved package fragment")

    for name, doc in docs.items():
        for n in doc.iter():
            require(review.local(n) not in {"script", "iframe", "form", "input", "button", "object", "embed", "foreignObject", "base"},
                    "Active content in packaged document")
            require(not any(k.lower().startswith("on") for k in n.attrib), "Packaged event handler")
            for attr in ("aria-labelledby", "aria-describedby", "headers"):
                require(all(i in lookups[name] for i in n.get(attr, "").split()), "Unresolved packaged IDREF")
            for attr in ("href", "src", "{http://www.w3.org/1999/xlink}href"):
                if n.get(attr):
                    reference(name, n.get(attr), n.tag == f"{{{H}}}a" and attr == "href")
            for value in n.attrib.values():
                for ref in re.findall(r"url\(['\"]?([^)'\" ]+)['\"]?\)", value):
                    reference(name, ref)
    for name, raw in files.items():
        if name.endswith(".css"):
            css = raw.decode("utf-8")
            require(not re.search(r"@import|https?:", css, re.I), "Remote packaged CSS")
            for ref in re.findall(r"url\(['\"]?([^)'\" ]+)", css):
                reference(name, ref)
    opf = ET.fromstring(files["OEBPS/package.opf"])
    ns = "{http://www.idpf.org/2007/opf}"
    items = opf.findall(ns + "manifest/" + ns + "item")
    manifest_ids = [item.get("id") for item in items]
    require(len(manifest_ids) == len(set(manifest_ids)), "Duplicate EPUB manifest ID")
    for item in items:
        reference("OEBPS/package.opf", item.get("href"))
    require(all(n.get("idref") in manifest_ids for n in opf.findall(ns + "spine/" + ns + "itemref")), "Unresolved EPUB spine item")


def make_epub(book, navigation, payload):
    nav_items = "".join(f'<li><a href="book.xhtml#{review.ESC(i)}">{review.ESC(t)}</a></li>' for i, t in navigation)
    nav = f'<html xmlns="{H}" xmlns:epub="http://www.idpf.org/2007/ops" lang="ta-Taml-IN" xml:lang="ta-Taml-IN"><head><title>உள்ளடக்கம்</title></head><body><nav epub:type="toc" id="toc"><h1>உள்ளடக்கம்</h1><ol>{nav_items}</ol></nav></body></html>'
    files = {"OEBPS/book.xhtml": book.encode("utf-8"), "OEBPS/nav.xhtml": nav.encode("utf-8")}
    media_types = {".css": "text/css", ".ttf": "font/ttf", ".txt": "text/plain", ".svg": "image/svg+xml", ".xhtml": "application/xhtml+xml"}
    items = ['<item id="book" href="book.xhtml" media-type="application/xhtml+xml" properties="mathml svg"/>', '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>']
    license_id = None
    for index, (name, raw) in enumerate(sorted(payload.items())):
        if name == "index.html":
            continue
        require(Path(name).suffix in media_types, "Unknown EPUB asset type")
        files["OEBPS/" + name] = raw
        items.append(f'<item id="asset{index}" href="{review.ESC(name)}" media-type="{media_types[Path(name).suffix]}"/>')
        if name == "LICENSE.xhtml":
            license_id = "asset" + str(index)
    require(license_id is not None, "Readable license document is missing")
    files["META-INF/container.xml"] = b'<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/package.opf" media-type="application/oebps-package+xml"/></rootfiles></container>'
    files["OEBPS/package.opf"] = f'<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid"><metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="uid">urn:language-allocation:ta-Taml-IN:A00-m81243:0.1.0</dc:identifier><dc:title>{TITLE}</dc:title><dc:language>ta-Taml-IN</dc:language><dc:creator>OpenStax contributors; unofficial Tamil adaptation with OpenAI Codex</dc:creator><dc:rights>CC BY-NC-SA 4.0; component notices apply</dc:rights><meta property="dcterms:modified">2026-08-31T00:00:00Z</meta></metadata><manifest>{"".join(items)}</manifest><spine><itemref idref="book"/><itemref idref="{license_id}" linear="no"/></spine></package>'.encode("utf-8")
    for name, raw in files.items():
        if name.endswith((".xhtml", ".xml", ".opf", ".svg")):
            ET.fromstring(raw)
    package_gate(files)
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as archive:
        for name, raw in [("mimetype", b"application/epub+zip"), *sorted(files.items())]:
            entry = zipfile.ZipInfo(name, (2026, 8, 31, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o644 << 16
            entry.compress_type = zipfile.ZIP_STORED if name == "mimetype" else zipfile.ZIP_DEFLATED
            archive.writestr(entry, raw)
    with zipfile.ZipFile(io.BytesIO(out.getvalue())) as archive:
        require(archive.namelist()[0] == "mimetype" and len(archive.namelist()) == len(files) + 1, "EPUB file closure changed")
        require(all(archive.read(n) == raw for n, raw in files.items()), "EPUB payload changed")
    return out.getvalue()


def build_payload():
    baseline, source_manifest = review.build_payload()
    source_negative_tests = review.self_test(baseline)
    paths = [LANG / "translation" / row[1] for row in COMPANIONS] + [STYLE, Path(__file__).resolve()]
    inputs = {**source_manifest["inputs"], **source_manifest["source_validation_inputs"],
              **{p.relative_to(LANG).as_posix(): review.sha(p) for p in paths}}
    source = ET.parse(review.SOURCE).getroot()
    roots = {key: ET.parse(LANG / "translation" / name).getroot() for key, name, *_ in COMPANIONS}
    answer_map = companion_gate(roots, source)
    roots = {key: render_companion(root) for key, root in roots.items()}
    source_doc = ET.fromstring(baseline["index.html"])
    original_nodes = list(source_doc.find(f"{{{H}}}body/{{{H}}}main"))
    require([n.get("id") for n in original_nodes] == ["mr-metadata", *review.UNITS, "mr-glossary", "mr-attribution"], "Unexpected source-preview boundaries")
    source_nodes = source_for_learning(original_nodes[:-1], answer_map)
    navigation, pieces = [], []

    def add_companion(key):
        root = roots[key]
        for section in root:
            heading = section.find(f"{{{H}}}h2")
            require(heading is not None, "Companion heading missing")
            navigation.append((section.get("id"), review.content_text(heading)))
        back = '<p class="module-return"><a href="#ta-route-checkpoints">நான்கு கற்றல் படிகளின் பதிவுக்குத் திரும்புங்கள்</a> · <a href="#mr-start">உள்ளடக்கம்</a></p>'
        pieces.append(f'<div id="mrl-{key}" class="learning-companion">{xhtml(root)}{back}</div>')

    for key in ("route", "u001", "u002", "large", "round"):
        add_companion(key)
    pieces.append('<div id="mrl-source"><p class="editorial-note">பின்வருவது மூலநூல் மொழிபெயர்ப்பு. மூல விடைகள் வெளிப்படையாக உள்ளன. சேர்த்த குறிப்புகளும் புதிய விடைத்துணை இணைப்புகளும் தனியாகக் குறிக்கப்பட்டுள்ளன.</p>')
    for node, nav in zip(source_nodes, source_manifest["navigation"][:-1]):
        pieces.append(xhtml(node))
        navigation.append((node.get("id"), nav["title"]))
    pieces.append('</div>')
    for key in ("missing", "reason"):
        add_companion(key)
    credits = review.review_credits()
    old = "இந்த மூலநூல் மதிப்பாய்வு வரைவில் மீட்புக் கற்றல் துணைகளோ கூடுதல் விடைத்துணைகளோ சேர்க்கப்படவில்லை."
    require(credits.count(old) == 1, "Editorial credit wording changed")
    credits = credits.replace(old, "நான்கு மீட்புக் கற்றல் துணைகள், 58 பகுதிப் பயிற்சிகளுக்கான விடை விளக்கங்கள், இறுதிச் சுயசோதனையுடன் கற்றல் வழி ஆகியவை புதிதாக எழுதப்பட்டவை; அவை மூலநூல் மொழிபெயர்ப்பு அல்ல.")
    credits = credits.replace('href="LICENSE.txt"', 'href="LICENSE.xhtml"')
    pieces.append(credits)
    navigation.append(("mr-attribution", "மூலமும் உரிமமும்"))
    nav = "".join(f'<li><a href="#{review.ESC(i)}">{review.ESC(title)}</a></li>' for i, title in navigation)
    cover = f'<header id="mr-start"><p class="eyebrow">A00 · m81243 · U001–U008 · இந்தியத் தமிழ் · 0.1.0</p><h1>{TITLE}</h1><div class="draft-banner"><h2>மதிப்பாய்வுக்கான கற்றல் பதிப்பு</h2><p>முழு எண்களின் இந்த ஒரு கூறுக்கான மூலநூல் மொழிபெயர்ப்பும் தனியாக எழுதப்பட்ட கற்றல் துணைகளும் இணைக்கப்பட்டுள்ளன. இது முழுப் பாடத்திட்டமோ வகுப்பு நிலை நிர்ணயச் சோதனையோ அல்ல. தாய்மொழிப் பேச்சாளர், ஆசிரியர், கற்போர் மற்றும் உதவித் தொழில்நுட்பப் பயனர் மதிப்பாய்வு இன்னும் தேவை.</p><p>மூலத்தின் 88 பயிற்சிகளுள் 59-க்கு மூல விடைகள் உள்ளன; மீதமுள்ள 29-க்கு புதிய விடைகள் தனித் துணைப்பகுதியில் உள்ளன. புதிய 75 சோதனை/பயிற்சி வினாக்களுக்கும் விடைகள் உள்ளன. நம்பிக்கைப் பட்டியல் தேர்ச்சிச் சோதனை அல்ல.</p></div><p><a href="#ta-route-start">இணைந்த கற்றல் வழியில் தொடங்குங்கள்.</a> தாளில் உங்கள் முன்னேற்றத்தைப் பதிவு செய்யுங்கள். பழைய தனிப் பகுதியின் வெளியீட்டு நிலைக் குறிப்பைவிட இந்த இணைந்த வழியின் நான்கு படிகளைப் பின்பற்றுங்கள்.</p><p>எண்கள், சர்வதேசக் காற்புள்ளிகள், அசல் அலகுகள் மற்றும் வரலாற்றுத் தரவுகள் மூலத்தில் உள்ளபடி வைக்கப்பட்டுள்ளன. இணைக்கப்படாத வெளி வளங்கள் விருப்பமானவை; இந்தப் பதிப்பின் கற்றல் வழிக்கு இணையக் கணக்கோ ஆசிரியரின் ஒப்புதலோ தேவையில்லை.</p><nav aria-label="உள்ளடக்கம்"><ol>{nav}</ol></nav></header>'
    book = f'<!DOCTYPE html><html xmlns="{H}" lang="ta-Taml-IN" xml:lang="ta-Taml-IN"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><title>{TITLE}</title><link rel="stylesheet" href="assets/m81243-review.css"/><link rel="stylesheet" href="assets/large-number-recovery.css"/><link rel="stylesheet" href="assets/m81243-learning.css"/></head><body><a class="skip" href="#mr-main">உள்ளடக்கத்திற்குச் செல்லுங்கள்</a>{cover}<main id="mr-main">{"".join(pieces)}</main></body></html>'
    payload = {name: data for name, data in baseline.items() if name not in ("index.html", "build-manifest.json")}
    license_text = payload["LICENSE.txt"].decode("utf-8")
    license_escaped = review.ESC(license_text).replace("\r", "&#13;")
    payload["LICENSE.xhtml"] = (f'<html xmlns="{H}" lang="en" xml:lang="en"><head><title>License notice</title><link rel="stylesheet" href="assets/m81243-review.css"/><link rel="stylesheet" href="assets/m81243-learning.css"/></head><body><h1>License notice</h1><pre class="license-text">{license_escaped}</pre></body></html>').encode("utf-8")
    require(ET.fromstring(payload["LICENSE.xhtml"]).find(f"{{{H}}}body/{{{H}}}pre").text == license_text,
            "License text changed in readable XHTML alternative")
    for style in (STYLE, LANG / "assets/large-number-recovery.css"):
        inputs[style.relative_to(LANG).as_posix()] = review.sha(style)
        payload["assets/" + style.name] = style.read_bytes()
    payload["index.html"] = book.encode("utf-8")
    doc = validate(book, payload, source_nodes, roots, answer_map, source)
    tests = []
    def rejected(mutated, changed_payload, reason):
        require(mutated != book or changed_payload != payload, "Negative fixture did not change")
        try:
            validate(mutated, changed_payload, source_nodes, roots, answer_map, source)
        except ValueError as exc:
            require(reason in str(exc), "Negative fixture failed for unrelated reason: " + str(exc))
            tests.append(reason)
            return
        raise ValueError("Negative fixture accepted: " + reason)
    for target, expected in (("fs-id1830385", "Rendered source block changed"), ("ta-round-R4", "Companion content changed")):
        changed = ET.fromstring(book)
        indexed(changed)[target].find(f"{{{H}}}p").text += " மாற்றம்"
        rejected(ET.tostring(changed, encoding="unicode"), payload, expected)
    rejected(book.replace('href="#mr-main"', 'href="#absent"', 1), payload, "Unresolved local reference")
    rejected(book.replace('id="mr-main"', 'id="mr-start"', 1), payload, "Duplicate document ID")
    rejected(book, {k: v for k, v in payload.items() if k != "assets/fonts/NotoSansTamil.ttf"}, "Unpackaged CSS dependency")
    rejected(book, {**payload, "assets/m81243-learning.css": b'@import "https://invalid.example/a.css";'}, "Remote CSS dependency")
    license_raw = payload["LICENSE.xhtml"]
    package_cases = [
        ({**payload, "LICENSE.xhtml": license_raw.replace(b'assets/m81243-review.css', b'assets/no-such-style.css', 1)}, navigation, "Unpackaged resource in package"),
        ({**payload, "LICENSE.xhtml": license_raw.replace(b'assets/m81243-review.css', b'https://invalid.example/license.css', 1)}, navigation, "Remote package dependency"),
        ({**payload, "LICENSE.xhtml": license_raw.replace(b'</body>', b'<script>bad()</script></body>', 1)}, navigation, "Active content in packaged document"),
        (payload, [("missing-nav-target", "invalid")], "Unresolved package fragment"),
    ]
    for changed_payload, changed_nav, expected in package_cases:
        try:
            make_epub(book, changed_nav, changed_payload)
        except ValueError as exc:
            require(expected in str(exc), "Package fixture failed for unrelated reason: " + str(exc))
            tests.append(expected)
        else:
            raise ValueError("Invalid EPUB package accepted: " + expected)
    payload[EPUB_NAME] = make_epub(book, navigation, payload)
    require(all(review.sha(LANG / p) == digest for p, digest in inputs.items()), "Validated input changed during build")
    manifest = {"version": "0.1.0", "locale": "ta-Taml-IN", "scope": "A00 m81243 only",
                "status": "integrated-learning-review-edition-not-validated-course", "formats": ["HTML", "EPUB"],
                "inputs": inputs, "source_counts": source_manifest["counts"],
                "counts": {"companions": 7, "new_questions": 75, "new_question_answers": 75,
                           "source_answer_supports": 58, "original_source_solutions": 59,
                           "source_omissions_preserved": 29, "document_ids": len(review.ids(doc)),
                           "mathml": len(list(doc.iter(f"{{{M}}}math"))), "svg_occurrences": 49},
                "source_answer_map": answer_map, "source_renderer_negative_tests": source_negative_tests,
                "integration_negative_tests": tests,
                "navigation": [{"id": i, "title": title} for i, title in navigation],
                "limits": ["EPUBCheck and browser QA are separate hash-matched records.",
                           "No new PDF, native-speaker, learner, AT or PDF/UA certification.",
                           "A10/A20 and the rest of A00 remain outside this reader."],
                "outputs": {n: {"bytes": len(b), "sha256": review.digest(b)} for n, b in sorted(payload.items())}}
    payload["build-manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return payload, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify existing output set and bytes without writing")
    args = parser.parse_args()
    payload, manifest = build_payload()
    require(payload == build_payload()[0], "Repeated in-memory build differs")
    out = OUTPUT.resolve()
    require(out.parent == LANG.resolve() and out.name == "reader-m81243-learning" and not OUTPUT.is_symlink(), "Unsafe output directory")
    existing = {p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file()} if out.exists() else set()
    require(existing <= set(payload), "Unexpected output files; no automatic deletion")
    require(all((out / name).resolve().is_relative_to(out) for name in payload), "Output path escapes reader")
    if args.check:
        require(existing == set(payload) and all((out / n).read_bytes() == b for n, b in payload.items()), "Output file set or bytes are stale")
    else:
        require(shutil.disk_usage(LANG).free > 100 * 1024 * 1024 + sum(map(len, payload.values())), "Insufficient disk space")
        for name, raw in payload.items():
            path = out / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
    print(json.dumps({"mode": "check" if args.check else "build", "files": len(payload), "counts": manifest["counts"],
                      "html_sha256": review.digest(payload["index.html"]), "epub_sha256": review.digest(payload[EPUB_NAME]),
                      "integration_negative_tests": manifest["integration_negative_tests"]}, indent=2))


if __name__ == "__main__":
    main()
